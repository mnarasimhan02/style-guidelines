# Style Guide Document Processor

A tool for processing and applying style guide rules to CSR documents using vector similarity search.

## Features
- Preprocesses style guide PDFs into semantic chunks
- Stores style rules in FAISS vector database
- Processes CSR documents (Word/Text)
- Applies relevant style transformations
- Web interface for document processing

## Setup
1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
streamlit run app.py
```

## Project Structure
- `document_processor.py`: Main processing logic
- `utils.py`: Helper functions
- `app.py`: Streamlit web interface
- `requirements.txt`: Project dependencies
