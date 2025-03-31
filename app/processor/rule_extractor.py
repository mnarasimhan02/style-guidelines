import re
from typing import List, Dict
import spacy
from app.models.rule_schema import StyleRule, RuleCategory, RuleType
import uuid

class RuleExtractor:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
        self.category_keywords = {
            RuleCategory.STRUCTURE: {
                'keywords': ["section", "heading", "table", "format", "layout"],
                'tags': ['sections', 'headings', 'tables']
            },
            RuleCategory.NUMBERS: {
                'keywords': ["number", "measurement", "range", "value", "unit"],
                'tags': ['measurements', 'ranges', 'formatting']
            },
            RuleCategory.DOMAIN: {
                'keywords': ["medical", "drug", "company", "clinical", "disease"],
                'tags': ['medical terms', 'company names']
            },
            RuleCategory.FORMATTING: {
                'keywords': ["capital", "space", "hyphen", "indent", "font"],
                'tags': ['capitalization', 'spacing']
            },
            RuleCategory.PUNCTUATION: {
                'keywords': ["comma", "period", "colon", "semicolon"],
                'tags': ['commas', 'periods', 'colons']
            },
            RuleCategory.GRAMMAR: {
                'keywords': ["tense", "verb", "sentence", "plural", "singular"],
                'tags': ['sentence structure', 'tense']
            },
            RuleCategory.ABBREVIATIONS: {
                'keywords': ["abbreviation", "acronym", "short form"],
                'tags': ['acronyms', 'short forms']
            },
            RuleCategory.REFERENCES: {
                'keywords': ["reference", "citation", "source", "bibliography"],
                'tags': ['citations', 'sources']
            }
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
            for category, data in self.category_keywords.items():
                if any(keyword in token.text for keyword in data['keywords']):
                    category_scores[category] += 1
                    
        # Default to FORMATTING if no clear category is found
        max_score = max(category_scores.values())
        if max_score == 0:
            return RuleCategory.FORMATTING
            
        # Return the category with the highest score
        return max(category_scores.items(), key=lambda x: x[1])[0]

    def extract_rules(self, text: str) -> List[Dict]:
        rules = []
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            for pattern in self.rule_patterns:
                match = re.search(pattern, line)
                if match:
                    pattern_text = match.group('pattern').strip()
                    replacement = match.group('replacement').strip()
                    
                    if pattern_text and replacement:
                        rule_type = self._determine_rule_type(line, pattern_text, replacement)
                        category = self._determine_category(line)
                        
                        rule = {
                            'id': str(uuid.uuid4()),
                            'description': line,
                            'pattern': pattern_text,
                            'replacement': replacement,
                            'type': rule_type,
                            'category': category,
                            'examples': []
                        }
                        rules.append(rule)
                        break
                        
        return rules

    def categorize_rules(self, rules: List[Dict]) -> Dict[str, List[StyleRule]]:
        """Convert raw rules to StyleRule objects and categorize them"""
        categorized = {}
        for rule in rules:
            category = rule['category']
            if category not in categorized:
                categorized[category] = []
                
            # Convert dict to StyleRule
            style_rule = StyleRule(
                id=rule['id'],
                category=rule['category'],
                type=rule['type'],
                description=rule['description'],
                pattern=rule['pattern'],
                replacement=rule['replacement'],
                examples=rule['examples']
            )
            categorized[category].append(style_rule)
            
        return {k: v for k, v in sorted(categorized.items(), key=lambda x: len(x[1]), reverse=True)}
