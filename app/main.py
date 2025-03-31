from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Dict
import uvicorn
import os
import logging
import tempfile
import io
import PyPDF2
from app.processor.document_processor import DocumentProcessor
from app.processor.rule_extractor import RuleExtractor
from app.models.rule_schema import StyleRule, RuleCategory, RuleType

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Style Guide Checker")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize processors
doc_processor = DocumentProcessor()
rule_extractor = RuleExtractor()

# Add default rules for testing
default_rules_text = """
1. Capitalization Rules:
   - "subject" → "Subject" when used as a noun
   - "DAIICHI SANKYO" → "Daiichi Sankyo"
   - "section" → "Section" when referring to document sections

2. Status Terms:
   - "approved" → "APPROVED"
   - "completed" → "COMPLETED"
   - "ongoing" → "ONGOING"

3. Document Types:
   - "informed consent form" → "ICF"
   - "clinical study report" → "CSR"
   - "statistical analysis plan" → "SAP"

4. Section References:
   - "see section" → "see Section"
   - "in appendix" → "in Appendix"
   - "table 1" → "Table 1"

5. Medical Terms:
   - Use "adverse event" instead of "side effect"
   - "patient" → "subject" when referring to study participants
   - "medicine" → "study drug"
"""

style_guide_processed = False

@app.post("/upload/style-guide")
async def upload_style_guide(file: UploadFile = File(...)):
    global style_guide_processed
    try:
        logger.info(f"Received style guide file: {file.filename}")
        
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Style guide must be a PDF file")
        
        # Read the uploaded file content
        content = await file.read()
        
        # Create a PDF reader object using BytesIO
        pdf_file = io.BytesIO(content)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        # Extract text from all pages
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
            
        # For testing, add default rules if the extracted text is too short
        if len(text.strip()) < 100:
            text = default_rules_text
        
        # Extract and categorize rules
        rules = rule_extractor.extract_rules(text)
        categorized_rules = rule_extractor.categorize_rules(rules)
        doc_processor.process_style_guide(content, categorized_rules)
        style_guide_processed = True
        
        return {"filename": file.filename, "status": "success", "message": "Style guide processed successfully", "rules": categorized_rules}
    except Exception as e:
        logger.error(f"Error processing style guide: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing file: {str(e)}"
        )

@app.post("/upload/csr")
async def upload_csr(file: UploadFile = File(...)):
    global style_guide_processed
    
    try:
        logger.info(f"Received CSR file: {file.filename}")
        
        if not style_guide_processed:
            raise HTTPException(status_code=400, detail="Please upload style guide first")
            
        if not (file.filename.lower().endswith('.pdf') or file.filename.lower().endswith('.docx')):
            raise HTTPException(status_code=400, detail="CSR must be a PDF or DOCX file")
        
        # Save uploaded file temporarily
        suffix = '.pdf' if file.filename.endswith('.pdf') else '.docx'
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            logger.info(f"Saving to temporary file: {temp_file.name}")
            content = await file.read()
            temp_file.write(content)
            temp_file.flush()
            
            # Process the CSR document
            logger.info("Processing CSR document...")
            results = doc_processor.process_csr(temp_file.name)
            
            # Clean up
            logger.info("Cleaning up temporary file...")
            os.unlink(temp_file.name)
            
            # Format results for frontend
            corrections = [
                {
                    "section": "Section " + str(i + 1),
                    "original_text": result["text"],
                    "corrected_text": result["corrected_text"],
                    "rules_applied": [
                        f"{change} (Rule: {match['rule']})"
                        for match in result["matches"]
                        for change in match["changes"]
                    ]
                }
                for i, result in enumerate(results)
            ]
            
            logger.info(f"Found {len(corrections)} corrections")
            return {
                "filename": file.filename,
                "status": "success",
                "corrections": corrections
            }
    except Exception as e:
        logger.error(f"Error processing CSR: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing file: {str(e)}"
        )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
