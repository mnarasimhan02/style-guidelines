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
from docx import Document
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
    allow_origins=["*"],
    allow_credentials=False,  # Must be False when allow_origins=["*"]
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize processors
doc_processor = DocumentProcessor()
rule_extractor = RuleExtractor()

def validate_pdf(filename: str, content_type: str) -> bool:
    """Validate PDF file."""
    if not filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=400,
            detail="File must be a PDF"
        )
    if content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. File must be a valid PDF."
        )
    return True

def validate_docx(filename: str, content_type: str) -> bool:
    """Validate DOCX file."""
    if not filename.lower().endswith('.docx'):
        raise HTTPException(
            status_code=400,
            detail="File must be a DOCX"
        )
    if content_type != "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. File must be a valid DOCX."
        )
    return True

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
        logger.info(f"Received style guide file: {file.filename} (type: {file.content_type})")
        
        # Validate PDF file
        validate_pdf(file.filename, file.content_type)
        
        # Read the uploaded file content
        content = await file.read()
        
        # Create a PDF reader object using BytesIO
        pdf_file = io.BytesIO(content)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        # Extract text from page 6 onwards
        text = ""
        for page_num in range(5, len(pdf_reader.pages)):  # Start from index 5 (6th page)
            text += pdf_reader.pages[page_num].extract_text()
            
        # For testing, add default rules if the extracted text is too short
        if len(text.strip()) < 100:
            text = default_rules_text
        
        # Extract and categorize rules
        rules = rule_extractor.extract_rules(text)
        categorized_rules = rule_extractor.categorize_rules(rules)
        doc_processor.process_style_guide(content, categorized_rules)
        style_guide_processed = True
        
        # Convert rules to dictionary format for frontend
        formatted_rules = {}
        for category, rule_list in categorized_rules.items():
            formatted_rules[category] = [
                {
                    'id': str(rule.id),
                    'pattern': rule.pattern,
                    'replacement': rule.replacement,
                    'type': rule.type,
                    'category': rule.category,
                    'description': rule.description or '',
                    'examples': rule.examples or []
                }
                for rule in rule_list
            ]
        
        return {
            "filename": file.filename,
            "status": "success",
            "message": "Style guide processed successfully",
            "rules": formatted_rules
        }
    except HTTPException as e:
        raise e
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
        logger.info(f"Received CSR file: {file.filename} (type: {file.content_type})")
        
        # Validate DOCX file
        validate_docx(file.filename, file.content_type)
        
        if not style_guide_processed:
            raise HTTPException(
                status_code=400,
                detail="Please upload a style guide first"
            )
        
        # Create a temporary file to store the uploaded content
        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file.flush()
            
            # Process the CSR document
            results = doc_processor.process_csr(temp_file.name)
            
            # Clean up
            os.unlink(temp_file.name)
            
            return results
            
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error processing CSR: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing file: {str(e)}"
        )

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
