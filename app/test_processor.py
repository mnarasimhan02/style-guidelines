from processor.document_processor import DocumentProcessor

def test_processing():
    processor = DocumentProcessor()
    
    # Process style guide
    style_guide_path = "styleexample/GP-RA005_Suppl.1_Global English-Language House Style Guide.pdf"
    print(f"\nProcessing style guide: {style_guide_path}")
    processor.process_style_guide(style_guide_path)
    
    # Process CSR
    csr_path = "csrexample/CSR Phase 1_StyleGuide_POC.docx"
    print(f"\nProcessing CSR: {csr_path}")
    results = processor.process_csr(csr_path)
    
    # Print first few results
    print("\nFirst few matches:")
    for i, result in enumerate(results[:3]):
        print(f"\nChunk {i+1}:")
        print(f"Text: {result['text'][:200]}...")
        print("\nTop matches:")
        for j, match in enumerate(result['matches'][:2]):
            print(f"{j+1}. Rule: {match['rule'][:100]}...")
            print(f"   Distance: {match['distance']}")

if __name__ == "__main__":
    test_processing()
