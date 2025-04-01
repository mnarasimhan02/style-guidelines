import pytest
import requests
import os
import time
import json
from typing import Dict, List

# Configuration
API_URL = "http://127.0.0.1:8001"
UI_URL = "http://127.0.0.1:3000"
STYLE_GUIDE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                               "styleexample/GP-RA005_Suppl.1_Global English-Language House Style Guide.pdf")
CSR_DOC_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                           "csrexample/CSR Phase 1_StyleGuide_POC.docx")

class TestE2E:
    @pytest.fixture(scope="class")
    def api_session(self):
        session = requests.Session()
        yield session
        session.close()

    def test_api_style_guide_upload(self, api_session):
        """Test style guide upload through API"""
        assert os.path.exists(STYLE_GUIDE_PATH), f"Style guide not found at {STYLE_GUIDE_PATH}"
        
        with open(STYLE_GUIDE_PATH, "rb") as f:
            files = {"file": (os.path.basename(STYLE_GUIDE_PATH), f, "application/pdf")}
            response = api_session.post(f"{API_URL}/upload/style-guide", files=files)
        
        assert response.status_code == 200, f"Upload failed with status {response.status_code}: {response.text}"
        data = response.json()
        assert "rules" in data
        assert len(data["rules"]) > 0
        print(f"API: Successfully extracted {len(data['rules'])} rules from style guide")

    def test_api_csr_upload(self, api_session):
        """Test CSR document upload through API"""
        assert os.path.exists(CSR_DOC_PATH), f"CSR document not found at {CSR_DOC_PATH}"
        
        # First upload style guide as it's required
        self.test_api_style_guide_upload(api_session)
        
        with open(CSR_DOC_PATH, "rb") as f:
            files = {"file": (os.path.basename(CSR_DOC_PATH), f, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
            response = api_session.post(f"{API_URL}/upload/csr", files=files)
        
        assert response.status_code == 200, f"Upload failed with status {response.status_code}: {response.text}"
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        
        # Verify all sections are present
        sections_with_changes = sum(1 for section in data if section.get("changes"))
        total_sections = len(data)
        assert total_sections > sections_with_changes, "Only sections with changes are present"
        
        # Verify section content
        for section in data:
            assert "text" in section, "Section missing original text"
            assert "corrected_text" in section, "Section missing corrected text"
            if section.get("changes"):
                assert len(section["changes"]) > 0, "Changes list is empty for section with changes"
        
        print(f"API: Processed {total_sections} total sections, {sections_with_changes} with changes")
        return data

    def test_cors_headers(self, api_session):
        """Test CORS headers"""
        headers = {
            "Origin": "http://127.0.0.1:3000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        }
        
        # Options request to check CORS
        response = api_session.options(f"{API_URL}/upload/style-guide", headers=headers)
        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers.keys()
        
        # Verify actual request with CORS
        with open(STYLE_GUIDE_PATH, "rb") as f:
            files = {"file": (os.path.basename(STYLE_GUIDE_PATH), f, "application/pdf")}
            response = api_session.post(
                f"{API_URL}/upload/style-guide",
                files=files,
                headers={"Origin": "http://127.0.0.1:3000"}
            )
        assert response.status_code == 200
        print("API: CORS headers verified")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
