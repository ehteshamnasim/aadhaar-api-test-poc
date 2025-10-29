import requests
import json
from typing import Dict, List

class TestGenerator:
    """Generate pytest tests using Ollama Llama3:70b"""
    
    def __init__(self, ollama_url: str = "http://localhost:11434"):
        self.ollama_url = ollama_url
        self.model = "qwen2.5-coder:14b"
    
    def generate_tests(self, parsed_spec: Dict) -> str:
        """Generate complete test file from parsed spec"""
        prompt = self._build_prompt(parsed_spec)
        
        print(f"   Using Ollama model: {self.model}")
        print(f"   Ollama URL: {self.ollama_url}")
        
        # Call Ollama API
        response = requests.post(
            f"{self.ollama_url}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "num_predict": 2000
                }
            },
            timeout=300  # 5 minutes timeout for large model
        )
        
        if response.status_code != 200:
            raise Exception(f"Ollama API error: {response.status_code} - {response.text}")
        
        result = response.json()
        test_code = result.get('response', '')
        
        # Extract code from markdown if present
        if '```python' in test_code:
            test_code = test_code.split('```python')[1].split('```')[0].strip()
        elif '```' in test_code:
            test_code = test_code.split('```')[1].split('```')[0].strip()
        
        return test_code
    
    def _build_prompt(self, parsed_spec: Dict) -> str:
        """
        Build prompt for LLM code generation.
        
        Extracts base path from base_url and combines with endpoint paths
        to generate correct test requests.
        
        Parameters:
            parsed_spec: Dictionary containing API specification
            
        Returns:
            Formatted prompt string for LLM
        """
        endpoints = parsed_spec['endpoints']
        base_url = parsed_spec.get('base_url', 'http://localhost:5001/api/v1')
        
        # Extract base path from base_url
        # Example: 'http://localhost:5001/api/v1' -> '/api/v1'
        from urllib.parse import urlparse
        parsed_url = urlparse(base_url)
        base_path = parsed_url.path or ''
        
        prompt = f"""You are an expert Python test engineer. Generate pytest test code for the following REST API.

Requirements:
- Use pytest framework
- Import Flask app directly: from api.dummy_aadhaar_api import app
- Use Flask test client: client = app.test_client()
- Make requests using full paths including base path: response = client.post('{base_path}/path', json={{...}})
- Include tests for success cases (2xx responses)
- Include tests for error cases (4xx responses) - understand the difference:
  * 400 Bad Request: Invalid format, wrong data type, pattern mismatch
  * 403 Forbidden: Missing consent field or consent=False
  * 401 Unauthorized: Missing authentication or invalid credentials
- Test with valid and invalid payloads
- For success tests, provide ALL required fields including 'consent: true' if needed
- Add clear test names and docstrings
- Use pytest fixtures for test client
- Follow PEP 8 style guide
- Validate response structure, not just status codes

CRITICAL RULES FOR STATUS CODES:
1. If endpoint requires 'consent' field: missing consent or consent=False → expect 403
2. If endpoint requires 'consent' field and testing success: ALWAYS include "consent": true
3. Missing required fields (non-consent) → expect 400
4. Invalid field format/pattern → expect 400
5. Success cases → expect 200 or 201 based on spec

IMPORTANT: All request paths must start with '{base_path}' (base path from API spec)

API Endpoints to test:

"""
        
        for ep in endpoints:
            full_path = base_path + ep['path']
            prompt += f"\n{ep['method']} {full_path}\n"
            prompt += f"Summary: {ep['summary']}\n"
            
            if ep['request_body'].get('properties'):
                prompt += f"Request body fields: {list(ep['request_body']['properties'].keys())}\n"
                required_fields = ep['request_body'].get('required_fields', [])
                prompt += f"Required fields: {required_fields}\n"
                
                # Highlight consent field if present
                if 'consent' in ep['request_body'].get('properties', {}):
                    prompt += f"⚠️  CONSENT FIELD: This endpoint has 'consent' field - missing/false consent returns 403, not 400!\n"
            
            prompt += f"Expected responses: {list(ep['responses'].keys())}\n"
            
            # Add response details for better test generation
            for status_code, response_info in ep['responses'].items():
                prompt += f"  - {status_code}: {response_info.get('description', 'N/A')}\n"
            
            prompt += "\n"
        
        prompt += f"""
Generate ONLY the Python code for pytest tests. Include:
1. Import statements (pytest, from api.dummy_aadhaar_api import app)
2. Pytest fixture for test client
3. Test functions using client.post(), client.get(), etc.
4. Assert statements for status codes AND response structure
5. For each endpoint, create at least:
   - 1 success test with ALL required fields (including consent: true if needed)
   - 1 test for missing required field (expect 400)
   - 1 test for invalid field format/pattern (expect 400)
   - 1 test for consent validation if endpoint has consent field (expect 403)
6. For GET endpoints with query parameters, test both valid and missing params
7. Validate response JSON structure, not just status codes

IMPORTANT: ALL test requests MUST include the base path '{base_path}'

Example structure for POST endpoint with consent:
```python
import pytest
from api.dummy_aadhaar_api import app

@pytest.fixture
def client():
    return app.test_client()

def test_demographics_success(client):
    # Success case - include ALL required fields
    response = client.post('{base_path}/aadhaar/demographics', json={{
        "aadhaar_number": "123456789012",
        "consent": true  # MUST include consent for success
    }})
    assert response.status_code == 200
    data = response.get_json()
    assert 'name' in data
    assert 'dob' in data

def test_demographics_missing_aadhaar(client):
    # Missing non-consent field → 400
    response = client.post('{base_path}/aadhaar/demographics', json={{
        "consent": true
    }})
    assert response.status_code == 400

def test_demographics_invalid_aadhaar_format(client):
    # Invalid format → 400
    response = client.post('{base_path}/aadhaar/demographics', json={{
        "aadhaar_number": "123",  # Invalid - not 12 digits
        "consent": true
    }})
    assert response.status_code == 400

def test_demographics_no_consent(client):
    # Missing consent field → 403
    response = client.post('{base_path}/aadhaar/demographics', json={{
        "aadhaar_number": "123456789012"
    }})
    assert response.status_code == 403
```

Example for GET endpoint with query params:
```python
def test_masked_aadhaar_success(client):
    response = client.get('{base_path}/aadhaar/masked-aadhaar?aadhaar_number=123456789012')
    assert response.status_code == 200
    data = response.get_json()
    assert 'masked_aadhaar' in data
    assert data['masked_aadhaar'] == 'XXXXXXXX9012'

def test_masked_aadhaar_missing_param(client):
    response = client.get('{base_path}/aadhaar/masked-aadhaar')
    assert response.status_code == 400

def test_masked_aadhaar_invalid_format(client):
    response = client.get('{base_path}/aadhaar/masked-aadhaar?aadhaar_number=123')
    assert response.status_code == 400
```

Do not include explanations, just the code. Start directly with imports.
"""
        
        return prompt
    
    def check_ollama_status(self) -> bool:
        """Check if Ollama is running"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def check_model_exists(self) -> bool:
        """Check if llama3:70b model exists"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                for model in models:
                    if 'llama3:70b' in model.get('name', ''):
                        return True
            return False
        except:
            return False

if __name__ == '__main__':
    # Test the generator
    from parser import OpenAPIParser
    
    generator = TestGenerator()
    
    # Check Ollama status
    print("Checking Ollama status...")
    if not generator.check_ollama_status():
        print("❌ Ollama is not running!")
        print("   Start it with: ollama serve")
        exit(1)
    
    print("✅ Ollama is running")
    
    # Check model
    if not generator.check_model_exists():
        print("⚠️  llama3:70b model not found!")
        print("   Pull it with: ollama pull llama3:70b")
        exit(1)
    
    print("✅ llama3:70b model found")
    
    # Generate tests
    parser = OpenAPIParser('specs/aadhaar-api.yaml')
    parsed_spec = parser.to_dict()
    
    print("\nGenerating tests...")
    test_code = generator.generate_tests(parsed_spec)
    
    print("\nGenerated Test Code:")
    print("=" * 80)
    print(test_code)