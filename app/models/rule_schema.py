from enum import Enum
from typing import List, Dict
from pydantic import BaseModel, Field
import uuid

class RuleCategory(str, Enum):
    """Category of style rule."""
    STRUCTURE = "structure"  # Document structure (sections, headings)
    NUMBERS = "numbers"  # Numbers and measurements
    DOMAIN = "domain"  # Domain-specific terms
    FORMATTING = "formatting"  # General formatting
    PUNCTUATION = "punctuation"  # Punctuation rules
    GRAMMAR = "grammar"  # Grammar rules
    ABBREVIATION = "abbreviation"  # Abbreviations and acronyms
    REFERENCE = "reference"  # Citations and references

class RuleType(str, Enum):
    """Type of style rule."""
    DIRECT = "direct"  # Simple word/phrase replacement
    PATTERN = "pattern"  # Regex or pattern-based replacement
    MULTI = "multi"  # Multi-word phrase substitutions
    CASE = "case"  # Case-sensitive handling
    CONTEXT = "context"  # Context-aware substitution

class StyleRule(BaseModel):
    """Style rule model."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    category: RuleCategory
    type: RuleType
    description: str = ""
    pattern: str
    replacement: str
    examples: List[str] = Field(default_factory=list)
    context: Dict = {}

    class Config:
        use_enum_values = True
