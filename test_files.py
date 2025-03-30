from app.processor.document_processor import DocumentProcessor

def main():
    processor = DocumentProcessor()
    
    # Process style guide
    style_guide_path = "styleexample/GP-RA005_Suppl.1_Global English-Language House Style Guide.pdf"
    print(f"\nProcessing style guide: {style_guide_path}")
    processor.process_style_guide(style_guide_path)
    
    # Process CSR document
    csr_path = "csrexample/CSR Phase 1_StyleGuide_POC.docx"
    print(f"\nProcessing CSR document: {csr_path}")
    results = processor.process_csr(csr_path)
    
    # Print results
    print("\nResults:")
    print("-" * 80)
    for i, result in enumerate(results, 1):
        print(f"\nSection {i}:")
        print("\nOriginal Text:")
        print(result["text"])
        print("\nCorrected Text:")
        print(result["corrected_text"])
        print("\nChanges Made:")
        for match in result["matches"]:
            for change in match["changes"]:
                print(f"- {change}")
        print("-" * 80)

if __name__ == "__main__":
    main()
