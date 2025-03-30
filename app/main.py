from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List
import uvicorn
import os
import logging
from tempfile import NamedTemporaryFile
from app.processor.document_processor import DocumentProcessor

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

# Initialize document processor
doc_processor = DocumentProcessor()
style_guide_processed = False

@app.post("/upload/style-guide")
async def upload_style_guide(file: UploadFile = File(...)):
    """Upload and process a style guide PDF"""
    global style_guide_processed
    try:
        logger.info(f"Received style guide file: {file.filename}")
        
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Style guide must be a PDF file")
        
        # Save uploaded file temporarily
        with NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            logger.info(f"Saving to temporary file: {temp_file.name}")
            content = await file.read()
            temp_file.write(content)
            temp_file.flush()
            
            # Process the style guide
            logger.info("Processing style guide...")
            doc_processor.process_style_guide(temp_file.name)
            style_guide_processed = True
            
            # Clean up
            logger.info("Cleaning up temporary file...")
            os.unlink(temp_file.name)
            
        return {"filename": file.filename, "status": "success", "message": "Style guide processed successfully"}
    except Exception as e:
        logger.error(f"Error processing style guide: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"message": f"Error processing file: {str(e)}"}
        )

@app.post("/upload/csr")
async def upload_csr(file: UploadFile = File(...)):
    """Upload and process a CSR document"""
    global style_guide_processed
    
    try:
        logger.info(f"Received CSR file: {file.filename}")
        
        if not style_guide_processed:
            raise HTTPException(status_code=400, detail="Please upload style guide first")
            
        if not (file.filename.lower().endswith('.pdf') or file.filename.lower().endswith('.docx')):
            raise HTTPException(status_code=400, detail="CSR must be a PDF or DOCX file")
        
        # Save uploaded file temporarily
        suffix = '.pdf' if file.filename.endswith('.pdf') else '.docx'
        with NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
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
        return JSONResponse(
            status_code=500,
            content={"message": f"Error processing file: {str(e)}"}
        )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
