# Style Guide Checker

A web-based tool for checking clinical study reports (CSR) against style guidelines using semantic matching.

## Features

- Upload CSR documents (.docx or .pdf) and style guide PDFs
- Extract and chunk text from documents
- Use vector embeddings and FAISS for semantic matching
- Apply style corrections based on matched rules
- Interactive results table with export options

## Setup

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Start the backend server:
```bash
uvicorn app.main:app --reload
```

3. Start the frontend development server:
```bash
cd frontend
npm install
npm start
```

## Project Structure

```
.
├── app/                    # Backend FastAPI application
│   ├── main.py            # Main FastAPI application
│   ├── models.py          # Pydantic models
│   ├── processor/         # Document processing modules
│   └── utils/            # Utility functions
├── frontend/             # React frontend application
├── requirements.txt      # Python dependencies
└── README.md            # Project documentation
```
