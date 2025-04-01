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
                'keywords': ["section", "heading", "table", "format", "layout", "indent", "margin", "page", "paragraph", "list"],
                'tags': ['sections', 'headings', 'tables', 'layout']
            },
            RuleCategory.NUMBERS: {
                'keywords': ["number", "measurement", "range", "value", "unit", "percent", "mg", "ml", "kg", "decimal", "digit"],
                'tags': ['measurements', 'ranges', 'units']
            },
            RuleCategory.DOMAIN: {
                'keywords': ["medical", "drug", "company", "clinical", "disease", "patient", "subject", "treatment", "dose", "study"],
                'tags': ['medical terms', 'company names', 'clinical terms']
            },
            RuleCategory.FORMATTING: {
                'keywords': ["capital", "space", "hyphen", "indent", "font", "bold", "italic", "underline", "case", "format"],
                'tags': ['capitalization', 'spacing', 'formatting']
            },
            RuleCategory.PUNCTUATION: {
                'keywords': ["comma", "period", "colon", "semicolon", "dash", "hyphen", "parentheses", "bracket", "quote"],
                'tags': ['punctuation', 'symbols']
            },
            RuleCategory.GRAMMAR: {
                'keywords': ["tense", "verb", "sentence", "plural", "singular", "active", "passive", "voice", "agreement"],
                'tags': ['sentence structure', 'tense', 'voice']
            },
            RuleCategory.ABBREVIATION: {
                'keywords': ["abbreviation", "acronym", "short form", "initialism", "expansion", "define", "spell out"],
                'tags': ['acronyms', 'abbreviations']
            },
            RuleCategory.REFERENCE: {
                'keywords': ["reference", "citation", "source", "bibliography", "appendix", "table", "figure", "cite"],
                'tags': ['citations', 'references']
            }
        }
        
        # Enhanced rule patterns
        self.rule_patterns = [
            # Direct replacements with arrows
            r'(?P<pattern>[^→]+)→\s*(?P<replacement>.+)',  # Unicode arrow
            r'(?P<pattern>[^=]+)=>\s*(?P<replacement>.+)',  # ASCII arrow
            r'(?P<pattern>[^-]+)->\s*(?P<replacement>.+)',  # ASCII arrow
            
            # Should/must be patterns
            r'(?P<pattern>.*?)\s*(?:should|must)\s+be\s+(?P<replacement>.*)',
            r'(?P<pattern>.*?)\s+(?:is|are)\s+(?P<replacement>.*)',
            
            # Use/write/spell patterns
            r'Use\s*["\'](?P<replacement>.*?)["\'](?:\s+instead\s+of|\s+not\s+)["\'](?P<pattern>.*?)["\']',
            r'Write\s*["\'](?P<replacement>.*?)["\'](?:\s+instead\s+of|\s+not\s+)["\'](?P<pattern>.*?)["\']',
            r'Spell\s+out\s*["\'](?P<pattern>.*?)["\'](?:\s+as\s+)["\'](?P<replacement>.*?)["\']',
            
            # Change/becomes patterns
            r'(?P<pattern>.*?)\s*(?:changes\s+to|becomes)\s*(?P<replacement>.*)',
            r'Change\s*["\'](?P<pattern>.*?)["\'](?:\s+to\s+)["\'](?P<replacement>.*?)["\']',
            
            # Case rules
            r'(?i)(?P<pattern>\b\w+\b)\s*should\s+be\s*(?:in\s+)?(?P<case>upper\s*case|lower\s*case|title\s*case|capitalized)',
            r'(?i)Capitalize\s+(?P<pattern>.*?)(?:\s+when|$)',
            
            # Context-sensitive rules
            r'(?i)When\s+(?P<context>.*?),\s*(?P<pattern>.*?)\s*should\s+be\s*(?P<replacement>.*)',
            r'(?i)If\s+(?P<context>.*?),\s*use\s*(?P<replacement>.*?)\s*(?:instead\s+of|not)\s*(?P<pattern>.*)',
            
            # Multi-word phrases
            r'(?i)Replace\s*["\'](?P<pattern>.*?)["\'](?:\s+with\s+)["\'](?P<replacement>.*?)["\']',
            r'(?i)The\s+phrase\s*["\'](?P<pattern>.*?)["\'](?:\s+should\s+be\s+)["\'](?P<replacement>.*?)["\']',
            
            # Pattern-based rules
            r'(?i)Numbers\s+(?P<pattern>\d+(?:[,-]\d+)*)\s*should\s+be\s*(?P<replacement>.*)',
            r'(?i)Units\s+(?P<pattern>[a-zA-Z]+)\s*should\s+be\s*(?P<replacement>.*)',
            
            # Abbreviation rules
            r'(?i)Abbreviate\s*["\'](?P<pattern>.*?)["\'](?:\s+as\s+)["\'](?P<replacement>.*?)["\']',
            r'(?i)The\s+abbreviation\s*["\'](?P<pattern>.*?)["\'](?:\s+stands\s+for\s+)["\'](?P<replacement>.*?)["\']',
        ]

    def extract_rules(self, text: str) -> List[Dict]:
        """Extract rules from text using regex patterns."""
        rules = []
        doc = self.nlp(text)
        
        # Extract rules using patterns
        for sent in doc.sents:
            sent_text = sent.text.strip()
            
            # Skip empty sentences
            if not sent_text:
                continue
            
            # Try different rule patterns
            for pattern in self.rule_patterns:
                matches = re.finditer(pattern, sent_text)
                for match in matches:
                    try:
                        rule = {
                            'id': str(uuid.uuid4()),
                            'pattern': match.group('pattern').strip(),
                            'replacement': match.group('replacement').strip(),
                            'description': sent_text,
                            'examples': [],
                            'type': self._determine_rule_type(match.group('pattern'), match.group('replacement')),
                            'category': self._determine_rule_category(sent_text)
                        }
                        rules.append(rule)
                    except (IndexError, AttributeError):
                        continue
        
        return rules

    def _determine_rule_type(self, pattern: str, replacement: str) -> RuleType:
        """Determine the type of rule based on pattern and replacement."""
        if callable(replacement):
            return RuleType.PATTERN
        elif '(' in pattern or '[' in pattern:
            return RuleType.PATTERN
        elif len(pattern.split()) > 2:
            return RuleType.MULTI
        elif pattern.lower() != replacement.lower():
            return RuleType.CASE
        else:
            return RuleType.DIRECT

    def _determine_rule_category(self, text: str) -> RuleCategory:
        """Determine the category of a rule based on its text."""
        text = text.lower()
        max_score = 0
        best_category = RuleCategory.FORMATTING  # Default category
        
        for category, info in self.category_keywords.items():
            score = sum(1 for keyword in info['keywords'] if keyword.lower() in text)
            if score > max_score:
                max_score = score
                best_category = category
        
        return best_category

    def categorize_rules(self, rules: List[Dict]) -> Dict[RuleCategory, List[StyleRule]]:
        """Categorize rules based on keywords and content."""
        categorized = {category: [] for category in RuleCategory}
        
        for rule in rules:
            # Create StyleRule object
            style_rule = StyleRule(
                id=rule.get('id', str(uuid.uuid4())),
                pattern=rule['pattern'],
                replacement=rule['replacement'],
                type=RuleType[rule['type'].upper()] if isinstance(rule['type'], str) else rule['type'],
                category=RuleCategory[rule['category'].upper()] if isinstance(rule['category'], str) else rule['category'],
                description=rule.get('description', ''),
                examples=rule.get('examples', [])
            )
            
            categorized[style_rule.category].append(style_rule)
        
        return categorized
