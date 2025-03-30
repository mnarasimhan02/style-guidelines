from pydantic import BaseModel
from typing import List, Optional

class StyleRule(BaseModel):
    """Represents a style rule extracted from the style guide"""
    section: str
    rule_text: str
    embedding: Optional[List[float]] = None

class CorrectionResult(BaseModel):
    """Represents a correction result for a section of text"""
    section: str
    original_text: str
    corrected_text: str
    rules_applied: List[str]

class ProcessingResponse(BaseModel):
    """Response model for document processing endpoints"""
    status: str
    message: str
    corrections: Optional[List[CorrectionResult]] = None
