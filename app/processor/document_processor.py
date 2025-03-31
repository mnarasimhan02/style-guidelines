from typing import List, Dict, Any
import PyPDF2
from docx import Document
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
import re
import io
from app.models.rule_schema import StyleRule
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        
    def extract_text_from_docx(self, file_path: str) -> str:
        """Extract text from a DOCX file"""
        text = []
        try:
            doc = Document(file_path)
            # Extract text from paragraphs
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text.append(paragraph.text)
                    
            # Extract text from tables
            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        if cell.text.strip():
                            text.append(cell.text)
                            
            return "\n".join(text)
        except Exception as e:
            logger.error(f"Error extracting text from DOCX: {str(e)}")
            raise

    def chunk_text(self, text: str) -> List[str]:
        """Split text into chunks by sentences"""
        # Split by sentence endings (.!?) but preserve the delimiter
        sentences = [s.strip() for s in re.split(r'([.!?])', text) if s.strip()]
        chunks = []
        current_chunk = []
        current_length = 0
        
        for i in range(0, len(sentences), 2):
            # Get the sentence and its delimiter if available
            sentence = sentences[i]
            delimiter = sentences[i + 1] if i + 1 < len(sentences) else ""
            full_sentence = sentence + delimiter
            
            sentence_length = len(full_sentence)
            if current_length + sentence_length > self.chunk_size:
                if current_chunk:
                    chunks.append("".join(current_chunk))
                current_chunk = [full_sentence]
                current_length = sentence_length
            else:
                current_chunk.append(full_sentence)
                current_length += sentence_length
        
        if current_chunk:
            chunks.append("".join(current_chunk))
        
        return chunks

    def apply_style_corrections(self, text: str) -> tuple[str, List[str]]:
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
        # Flatten the rules list
        flat_rules = []
        for category, rule_list in rules.items():
            flat_rules.extend(rule_list)
        
        self.style_rules = flat_rules
        
        # Create embeddings for semantic search
        rule_texts = []
        for rule in flat_rules:
            rule_texts.append(f"{rule.pattern} {rule.replacement}")
                
        if rule_texts:
            # Create embeddings
            embeddings = self.model.encode(rule_texts)
            
            # Initialize FAISS index
            dimension = embeddings.shape[1]
            self.index = faiss.IndexFlatL2(dimension)
            
            # Add embeddings to index
            self.index.add(embeddings.astype('float32'))
            
            logger.info(f"Initialized FAISS index with {len(rule_texts)} rules")

    def process_csr(self, file_path: str) -> List[Dict[str, Any]]:
        """Process CSR document and find style matches"""
        try:
            # Extract text from DOCX
            text = self.extract_text_from_docx(file_path)
            logger.info(f"Extracted {len(text)} characters from DOCX")
            
            # Split into chunks
            chunks = self.chunk_text(text)
            logger.info(f"Split text into {len(chunks)} chunks")
            
            results = []
            
            # Process each chunk
            for chunk in chunks:
                # Apply style corrections
                corrected_text, changes = self.apply_style_corrections(chunk)
                
                # Create embedding for the chunk
                chunk_embedding = self.model.encode([chunk])[0]
                
                # Find similar style rules
                matches = []
                if self.index is not None:
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
                
                # Include all chunks, even if no corrections were made
                results.append({
                    "text": chunk,
                    "corrected_text": corrected_text,
                    "matches": matches if matches else [],
                    "changes": changes
                })
            
            logger.info(f"Processed {len(chunks)} chunks, found corrections for {len([r for r in results if r['changes']])} chunks")
            return results
            
        except Exception as e:
            logger.error(f"Error processing CSR: {str(e)}")
            raise
