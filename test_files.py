import requests
import os
import mimetypes

def upload_file(url: str, file_path: str) -> dict:
    """Upload a file to the specified endpoint"""
    content_type = mimetypes.guess_type(file_path)[0]
    with open(file_path, 'rb') as f:
        files = {'file': (os.path.basename(file_path), f, content_type)}
        response = requests.post(url, files=files)
        response.raise_for_status()
        return response.json()

def main():
    base_url = "http://localhost:8001"
    
    # Upload style guide
    style_guide_path = "styleexample/GP-RA005_Suppl.1_Global English-Language House Style Guide.pdf"
    print(f"\nUploading style guide: {style_guide_path}")
    style_guide_result = upload_file(f"{base_url}/upload/style-guide", style_guide_path)
    print("Style guide processed successfully!")
    print(f"Found {sum(len(rules) for rules in style_guide_result['rules'].values())} rules")
    
    # Upload CSR document
    csr_path = "csrexample/CSR Phase 1_StyleGuide_POC.docx"
    print(f"\nUploading CSR document: {csr_path}")
    csr_result = upload_file(f"{base_url}/upload/csr", csr_path)
    
    # Print results
    print("\nResults:")
    print("-" * 80)
    for i, result in enumerate(csr_result, 1):
        print(f"\nSection {i}:")
        print("\nOriginal Text:")
        print(result["text"])
        print("\nCorrected Text:")
        print(result["corrected_text"])
        print("\nChanges Made:")
        if "matches" in result:
            for match in result["matches"]:
                print(f"Rule: {match['rule']['description']}")
                for change in match["changes"]:
                    print(f"- {change}")
        else:
            for change in result["changes"]:
                print(f"- {change}")
        print("-" * 80)

if __name__ == "__main__":
    main()
