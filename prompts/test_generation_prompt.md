# TEST GENERATION PROMPT TEMPLATE

Generate pytest test code for the following REST API endpoints.

## API SPECIFICATION:
Base URL: {base_url}
Endpoints: {endpoint_count}

{endpoints_details}

## REQUIREMENTS:
1. Use pytest framework
2. Use requests library for HTTP calls  
3. Define BASE_URL constant at the top
4. NO pytest fixtures - use direct requests calls
5. Include tests for success (2xx) and error (4xx) cases
6. Test with valid and invalid payloads
7. Add clear docstrings for each test
8. Follow PEP 8 naming conventions

## OUTPUT FORMAT:
Generate ONLY Python code. Start with imports and BASE_URL definition.

## EXAMPLE:
```python
import pytest  
import requests

BASE_URL = "http://localhost:5001/api/v1"

def test_verify_aadhaar_success():
    """Test successful Aadhaar verification."""
    response = requests.post(f"{BASE_URL}/aadhaar/verify", json={"aadhaar_number": "123456789012"})
    assert response.status_code == 200

def test_verify_aadhaar_missing_field():
    """Test Aadhaar verification with missing field."""  
    response = requests.post(f"{BASE_URL}/aadhaar/verify", json={})
    assert response.status_code == 400
```

Generate tests for ALL endpoints listed above.