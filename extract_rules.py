from app.processor.rule_extractor import RuleExtractor
from PyPDF2 import PdfReader

def main():
    # Read PDF
    pdf = PdfReader('styleexample/GP-RA005_Suppl.1_Global English-Language House Style Guide.pdf')
    text = ''
    for page in pdf.pages:
        text += page.extract_text()
    
    # Extract rules
    extractor = RuleExtractor()
    rules = extractor.extract_rules(text)
    
    print(f'Found {len(rules)} rules:')
    print('-' * 80)
    for rule in rules:
        print(f'Category: {rule["category"]}')
        print(f'Type: {rule["type"]}')
        print(f'Pattern: {rule["pattern"]}')
        print(f'Replacement: {rule["replacement"]}')
        print('-' * 80)

if __name__ == '__main__':
    main()
