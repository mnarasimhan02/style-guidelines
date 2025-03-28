from typing import List, Dict, Tuple
import re
from langchain.text_splitter import RecursiveCharacterTextSplitter

def extract_sections(text: str) -> List[Tuple[str, str]]:
    """Extract sections and their content from text."""
    # Simple section extraction based on common heading patterns
    section_pattern = r'(?m)^#{1,6}\s+(.+)$'
    sections = []
    current_section = ""
    current_content = []

    for line in text.split('\n'):
        heading_match = re.match(section_pattern, line)
        if heading_match:
            if current_section:
                sections.append((current_section, '\n'.join(current_content)))
            current_section = heading_match.group(1)
            current_content = []
        else:
            current_content.append(line)

    if current_section:
        sections.append((current_section, '\n'.join(current_content)))
    return sections

def create_chunks(text: str, chunk_size: int = 500, chunk_overlap: int = 50) -> List[str]:
    """Split text into overlapping chunks."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", " ", ""]
    )
    return text_splitter.split_text(text)

def extract_examples(text: str) -> List[str]:
    """Extract examples from text content."""
    # Look for common example indicators
    example_patterns = [
        r'Example:\s*(.*?)(?=\n\n|$)',
        r'e\.g\.\s*(.*?)(?=\n\n|$)',
        r'For example:\s*(.*?)(?=\n\n|$)'
    ]
    
    examples = []
    for pattern in example_patterns:
        matches = re.finditer(pattern, text, re.DOTALL)
        examples.extend(match.group(1).strip() for match in matches)
    
    return examples

def identify_rule_type(text: str) -> str:
    """Identify the type of style rule from text content."""
    # Define keywords associated with different rule types
    rule_types = {
        'formatting': ['format', 'style', 'font', 'spacing', 'margin', 'indent'],
        'grammar': ['grammar', 'tense', 'verb', 'noun', 'adjective', 'adverb'],
        'punctuation': ['punctuation', 'comma', 'period', 'colon', 'semicolon'],
        'terminology': ['term', 'word choice', 'vocabulary', 'glossary'],
        'structure': ['structure', 'organization', 'layout', 'section', 'heading']
    }
    
    text_lower = text.lower()
    for rule_type, keywords in rule_types.items():
        if any(keyword in text_lower for keyword in keywords):
            return rule_type
    
    return 'general'
