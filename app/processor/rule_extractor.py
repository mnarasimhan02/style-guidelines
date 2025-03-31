import re
from typing import List, Dict
import spacy
from app.models.rule_schema import StyleRule, RuleCategory, RuleType
import uuid

class RuleExtractor:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
        self.category_keywords = {
            RuleCategory.STRUCTURE: ["section", "heading", "table", "format", "layout"],
            RuleCategory.NUMBERS: ["number", "measurement", "range", "value", "unit"],
            RuleCategory.DOMAIN: ["medical", "drug", "company", "clinical", "disease"],
            RuleCategory.FORMATTING: ["capital", "space", "hyphen", "indent", "font"],
            RuleCategory.PUNCTUATION: ["comma", "period", "colon", "semicolon"],
            RuleCategory.GRAMMAR: ["tense", "verb", "sentence", "plural", "singular"],
            RuleCategory.ABBREVIATIONS: ["abbreviation", "acronym", "short form"],
            RuleCategory.REFERENCES: ["reference", "citation", "source", "bibliography"]
        }
        
        # Common rule patterns
        self.rule_patterns = [
            r'(?P<pattern>.*?)\s*(?:should be|must be|is|are)\s*(?P<replacement>.*)',
            r'(?P<pattern>.*?)\s*(?:→|=>|->)\s*(?P<replacement>.*)',
            r'Use\s*"(?P<replacement>.*?)"\s*(?:instead of|not)\s*"(?P<pattern>.*?)"',
            r'(?P<pattern>.*?)\s*(?:changes to|becomes)\s*(?P<replacement>.*)'
        ]

    def _determine_rule_type(self, rule_text: str, pattern: str, replacement: str) -> RuleType:
        if any(word in rule_text.lower() for word in ["case", "upper", "lower", "capitalize"]):
            return RuleType.CASE
        if len(pattern.split()) > 3 or len(replacement.split()) > 3:
            return RuleType.MULTI
        if any(char in pattern for char in ["*", "?", "+", "[", "]", "("]):
            return RuleType.PATTERN
        if any(word in rule_text.lower() for word in ["when", "if", "unless", "except", "context"]):
            return RuleType.CONTEXT
        return RuleType.DIRECT

    def _determine_category(self, rule_text: str) -> RuleCategory:
        doc = self.nlp(rule_text.lower())
        category_scores = {category: 0 for category in RuleCategory}
        
        for token in doc:
            for category, keywords in self.category_keywords.items():
                if any(keyword in token.text for keyword in keywords):
                    category_scores[category] += 1
                    
        # Default to FORMATTING if no clear category is found
        max_score = max(category_scores.values())
        if max_score == 0:
            return RuleCategory.FORMATTING
            
        return max(category_scores.items(), key=lambda x: x[1])[0]

    def extract_rules(self, text: str) -> List[StyleRule]:
        rules = []
        
        # Split text into potential rule segments
        segments = re.split(r'\n(?=\d+\.|\-|\•|\*|\w+\))', text)
        
        for segment in segments:
            segment = segment.strip()
            if not segment:
                continue
                
            # Try each rule pattern
            for pattern in self.rule_patterns:
                match = re.search(pattern, segment, re.IGNORECASE)
                if match:
                    pattern_text = match.group('pattern').strip()
                    replacement_text = match.group('replacement').strip()
                    
                    # Create rule
                    rule = StyleRule(
                        id=str(uuid.uuid4()),
                        category=self._determine_category(segment),
                        type=self._determine_rule_type(segment, pattern_text, replacement_text),
                        description=segment,
                        pattern=pattern_text,
                        replacement=replacement_text,
                        examples=[]
                    )
                    rules.append(rule)
                    break
                    
            # Look for examples in the following lines
            # TODO: Implement example extraction
        
        return rules

    def categorize_rules(self, rules: List[StyleRule]) -> Dict[str, List[dict]]:
        categorized = {category.value: [] for category in RuleCategory}
        for rule in rules:
            rule_dict = rule.dict()
            categorized[rule.category].append(rule_dict)
        return categorized
