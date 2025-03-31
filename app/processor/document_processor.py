from typing import List, Dict, Any
import PyPDF2
from docx import Document
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
import re
import io
from app.models.rule_schema import StyleRule

class DocumentProcessor:
    def __init__(self):
        self.model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
        self.index = None
        self.style_rules = []
        self.chunk_size = 500
        self.corrections_map = {
            # Company name
            r'(?i)daiichi\s+sankyo(?!\s+inc)': 'Daiichi Sankyo',
            
            # Clinical terms
            r'\b(?i)phase\s+(one|1)\b': 'PHASE ONE',
            r'\b(?i)phase\s+(two|2)\b': 'PHASE TWO',
            r'\b(?i)clinical\s+trial(?!s)': 'Clinical Trial',
            r'\b(?i)subject(?!s\b|\w)': 'Subject',
            r'\b(?i)patient(?!s\b|\w)': 'Patient',
            
            # Document sections
            r'\b(?i)version(?!s\b|\w)': 'Version',
            r'\b(?i)appendix(?!es\b|\w)': 'Appendix',
            r'\b(?i)table(?!s\b|\w)': 'Table',
            r'\b(?i)figure(?!s\b|\w)': 'Figure',
            r'\b(?i)section(?!s\b|\w)': 'Section',
            
            # Status terms
            r'\b(?i)approved(?!s\b|\w)': 'APPROVED',
            r'\b(?i)confidential(?!s\b|\w)': 'CONFIDENTIAL',
            r'\b(?i)draft(?!s\b|\w)': 'DRAFT',
            
            # Titles and roles
            r'\b(?i)dr\.?\s': 'Dr. ',
            r'\b(?i)prof\.?\s': 'Prof. ',
            r'\b(?i)principal\s+investigator': 'Principal Investigator',
            
            # Common abbreviations
            r'\b(?i)e\.?g\.?\s': 'e.g., ',
            r'\b(?i)i\.?e\.?\s': 'i.e., ',
            r'\b(?i)vs\.?\s': 'vs. ',
            r'\b(?i)etc\.?\s': 'etc. ',
            
            # Technical terms
            r'\b(?i)ds-8201a?\b': 'DS-8201a',
            r'\b(?i)t-dxd\b': 'T-DXd',
            r'\b(?i)nsclc\b': 'NSCLC',
            r'\b(?i)her2\b': 'HER2',
            r'\b(?i)ild\b': 'ILD',
            
            # Document types
            r'\b(?i)csr\b': 'CSR',
            r'\b(?i)sap\b': 'SAP',
            r'\b(?i)icf\b': 'ICF',
        }

    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from a PDF file"""
        text = ""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            print(f"Error extracting text from PDF: {str(e)}")
        return text

    def extract_text_from_docx(self, file_path: str) -> str:
        """Extract text from a DOCX file"""
        text = ""
        try:
            doc = Document(file_path)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        except Exception as e:
            print(f"Error extracting text from DOCX: {str(e)}")
        return text

    def chunk_text(self, text: str) -> List[str]:
        """Split text into chunks by sentences"""
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        chunks = []
        current_chunk = []
        current_length = 0
        
        for sentence in sentences:
            sentence_length = len(sentence)
            if current_length + sentence_length > self.chunk_size:
                if current_chunk:
                    chunks.append('. '.join(current_chunk) + '.')
                current_chunk = [sentence]
                current_length = sentence_length
            else:
                current_chunk.append(sentence)
                current_length += sentence_length
        
        if current_chunk:
            chunks.append('. '.join(current_chunk) + '.')
        
        return chunks

    def apply_style_corrections(self, text: str) -> str:
        """Apply style corrections to the text"""
        corrected = text
        changes_made = []
        
        for pattern, replacement in self.corrections_map.items():
            matches = list(re.finditer(pattern, corrected))
            if matches:
                for m in matches:
                    if m.group(0) != replacement:  # Only record if there's an actual change
                        changes_made.append(f"Changed '{m.group(0)}' to '{replacement}'")
                corrected = re.sub(pattern, replacement, corrected)
        
        return corrected, changes_made

    def process_style_guide(self, content: bytes, rules: Dict[str, List[StyleRule]]):
        """Process the style guide content and store the rules"""
        self.style_rules = rules
        
    def process_document(self, file_path: str) -> List[Dict]:
        """Process a document against stored style rules"""
        results = []
        
        if not self.style_rules:
            return results
            
        # Read document content
        if file_path.endswith('.pdf'):
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()
        else:
            # Handle docx files here
            text = "Document text extraction not implemented for this format"
            
        # Apply style rules
        for category, rules in self.style_rules.items():
            for rule in rules:
                # Simple text matching for now
                if rule.pattern in text:
                    results.append({
                        "category": category,
                        "rule": rule.description,
                        "type": rule.type,
                        "original": rule.pattern,
                        "suggestion": rule.replacement
                    })
                    
        return results

    def process_csr(self, file_path: str) -> List[Dict[str, Any]]:
        """Process CSR document and find style matches"""
        try:
            # Extract text based on file type
            if file_path.endswith('.pdf'):
                text = self.extract_text_from_pdf(file_path)
            else:
                text = self.extract_text_from_docx(file_path)
            
            # Split into chunks
            chunks = self.chunk_text(text)
            results = []
            
            # Process each chunk
            for chunk in chunks:
                # Apply style corrections
                corrected_text, changes = self.apply_style_corrections(chunk)
                
                # Only include chunks where corrections were made
                if changes:
                    # Create embedding for the chunk
                    chunk_embedding = self.model.encode([chunk])[0]
                    
                    # Find similar style rules
                    D, I = self.index.search(
                        chunk_embedding.reshape(1, -1).astype('float32'),
                        min(3, len(self.style_rules))
                    )
                    
                    matches = [
                        {
                            "rule": self.style_rules[idx],
                            "distance": float(dist),
                            "changes": changes
                        }
                        for dist, idx in zip(D[0], I[0])
                        if dist < 100  # Filter out very distant matches
                    ]
                    
                    if matches:  # Only include chunks that have matches
                        results.append({
                            "text": chunk,
                            "corrected_text": corrected_text,
                            "matches": matches
                        })
            
            print(f"Processed {len(chunks)} chunks, found corrections for {len(results)} chunks")
            return results
            
        except Exception as e:
            print(f"Error processing CSR: {str(e)}")
            raise
