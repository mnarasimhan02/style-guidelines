from app.processor.document_processor import DocumentProcessor

def main():
    # Initialize processor
    processor = DocumentProcessor()
    
    # Process CSR document
    csr_path = "csrexample/CSR Phase 1_StyleGuide_POC.docx"
    processor.process_and_show_changes(csr_path)

if __name__ == "__main__":
    main()
