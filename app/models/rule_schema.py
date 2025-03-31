from enum import Enum
from typing import List, Dict
from pydantic import BaseModel

class RuleCategory(str, Enum):
    STRUCTURE = "Structure"
    NUMBERS = "Numbers"
    DOMAIN = "Domain"
    FORMATTING = "Formatting"
    PUNCTUATION = "Punctuation"
    GRAMMAR = "Grammar"
    ABBREVIATIONS = "Abbreviations"
    REFERENCES = "References"

class RuleType(str, Enum):
    DIRECT = "DIRECT"
    PATTERN = "PATTERN"
    CONTEXT = "CONTEXT"
    MULTI = "MULTI"
    CASE = "CASE"

class StyleRule(BaseModel):
    id: str
    category: RuleCategory
    type: RuleType
    description: str
    pattern: str
    replacement: str
    examples: List[str] = []
    context: Dict = {}

    class Config:
        use_enum_values = True
