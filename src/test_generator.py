import requests
import json
from typing import Dict, List

class TestGenerator:
    """Generate pytest tests using Ollama with coverage-driven iteration"""
    
    def __init__(self, ollama_url: str = "http://localhost:11434"):
        self.ollama_url = ollama_url
        self.model = "qwen2.5-coder:14b"
        self.max_iterations = 2  # Maximum number of refinement iterations
    
    def generate_tests(self, parsed_spec: Dict) -> str:
        """
        Generate complete test file from parsed spec
        
        Parameters:
            parsed_spec: Parsed OpenAPI specification
        
        Returns:
            Generated test code as string
        """
        prompt = self._build_prompt(parsed_spec)
        
        print(f"   Using Ollama model: {self.model}")
        print(f"   Ollama URL: {self.ollama_url}")
        
        test_code = self._call_ollama(prompt)
        return test_code
    
    def generate_additional_tests(self, targeted_prompt: str) -> str:
        """
        Generate additional tests to fill coverage gaps
        
        Parameters:
            targeted_prompt: Prompt specifically targeting missing coverage
        
        Returns:
            Additional test code as string
        """
        print(f"   Generating targeted tests for missing coverage...")
        
        additional_code = self._call_ollama(targeted_prompt, num_predict=3000)
        return additional_code
    
    def _call_ollama(self, prompt: str, num_predict: int = 5000) -> str:
        """
        Call Ollama API with given prompt
        
        Parameters:
            prompt: Prompt to send to LLM
            num_predict: Maximum tokens to generate
        
        Returns:
            Generated code as string
        """
        # Call Ollama API with optimized parameters for comprehensive test generation
        response = requests.post(
            f"{self.ollama_url}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.2,  # Lower temperature for more deterministic, structured output
                    "num_predict": num_predict,
                    "top_p": 0.9,
                    "top_k": 40
                }
            },
            timeout=600  # 10 minutes timeout for comprehensive test generation
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
        """Build comprehensive prompt for LLM with coverage requirements"""
        endpoints = parsed_spec['endpoints']
        
        prompt = f"""You are an expert Python test engineer specializing in comprehensive test coverage. Generate pytest test code for the following REST API with the goal of achieving 95%+ code coverage.

CRITICAL REQUIREMENTS FOR HIGH COVERAGE:
- Use pytest framework with Flask test client
- Import Flask app: from api.dummy_aadhaar_api import app
- Use test client: client = app.test_client()
- Make requests: response = client.post('/api/v1/path', json={{...}})
- **MUST test ALL error paths and edge cases**
- Follow PEP 8 and include clear docstrings

TEST CATEGORIES REQUIRED (for EACH endpoint):

1. SUCCESS CASES (Happy Path):
   - Valid data with all required fields
   - Valid data with optional fields
   - Multiple valid scenarios with different test data

2. MISSING PARAMETER ERRORS (400):
   - Missing each required field individually
   - Missing multiple required fields
   - Empty JSON body (expect 415 Unsupported Media Type)
   - Missing specific consent fields where applicable

3. INVALID FORMAT ERRORS (400):
   - Too short values (e.g., Aadhaar with 11 digits)
   - Too long values (e.g., Aadhaar with 13 digits)
   - Invalid characters (letters in numeric fields)
   - Special characters where not allowed
   - Empty strings ""
   - Strings with only spaces "   "

4. NOT FOUND ERRORS (404):
   - Valid format but non-existent resources
   - Aadhaar numbers not in system

5. CONSENT/AUTHORIZATION ERRORS (400/403):
   - Missing consent field
   - Consent set to false
   - Invalid transaction IDs

6. EDGE CASES:
   - Expired transactions
   - Reused OTPs
   - Invalid OTP values
   - Boundary values

API Endpoints to test:

"""
        
        for ep in endpoints:
            prompt += f"\n{ep['method']} {ep['path']}\n"
            prompt += f"Summary: {ep['summary']}\n"
            
            if ep['request_body'].get('properties'):
                prompt += f"Request body fields: {list(ep['request_body']['properties'].keys())}\n"
                prompt += f"Required fields: {ep['request_body'].get('required_fields', [])}\n"
            
            prompt += f"Expected responses: {list(ep['responses'].keys())}\n"
            prompt += "\n"
        
        prompt += """
EXAMPLE STRUCTURE (follow this pattern for ALL endpoints):

```python
import pytest
from api.dummy_aadhaar_api import app

@pytest.fixture
def client():
    \"\"\"Create Flask test client fixture\"\"\"
    return app.test_client()

# SUCCESS CASES
def test_endpoint_valid_success(client):
    \"\"\"Test endpoint with valid data - success case\"\"\"
    response = client.post('/api/v1/path', json={{
        "required_field": "valid_value",
        "other_field": "valid_value"
    }})
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'success'

# MISSING PARAMETER ERRORS
def test_endpoint_missing_required_field(client):
    \"\"\"Test endpoint with missing required field\"\"\"
    response = client.post('/api/v1/path', json={{
        "other_field": "value"
    }})
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data

def test_endpoint_no_json_body(client):
    \"\"\"Test endpoint without JSON body\"\"\"
    response = client.post('/api/v1/path')
    assert response.status_code == 415  # Unsupported Media Type

# INVALID FORMAT ERRORS
def test_endpoint_invalid_format_short(client):
    \"\"\"Test endpoint with too short value\"\"\"
    response = client.post('/api/v1/path', json={{
        "aadhaar_number": "12345"  # Too short
    }})
    assert response.status_code == 400

def test_endpoint_invalid_format_letters(client):
    \"\"\"Test endpoint with letters in numeric field\"\"\"
    response = client.post('/api/v1/path', json={{
        "aadhaar_number": "12345678ABCD"
    }})
    assert response.status_code == 400

# NOT FOUND ERRORS
def test_endpoint_not_found(client):
    \"\"\"Test endpoint with non-existent resource\"\"\"
    response = client.post('/api/v1/path', json={{
        "aadhaar_number": "999999999999"
    }})
    assert response.status_code == 404

# CONSENT/AUTHORIZATION ERRORS (if applicable)
def test_endpoint_missing_consent(client):
    \"\"\"Test endpoint without consent field\"\"\"
    response = client.post('/api/v1/path', json={{
        "aadhaar_number": "123456789012"
    }})
    assert response.status_code == 400

def test_endpoint_consent_false(client):
    \"\"\"Test endpoint with consent set to false\"\"\"
    response = client.post('/api/v1/path', json={{
        "aadhaar_number": "123456789012",
        "consent": false
    }})
    assert response.status_code == 400

# EDGE CASES
def test_endpoint_empty_string(client):
    \"\"\"Test endpoint with empty string\"\"\"
    response = client.post('/api/v1/path', json={{
        "aadhaar_number": ""
    }})
    assert response.status_code == 400
```

IMPORTANT:
- Generate AT LEAST 6-10 test cases per endpoint
- Cover ALL error paths (missing params, invalid formats, not found, consent errors)
- Use descriptive test names: test_<endpoint>_<scenario>_<expected_result>
- Include docstrings for each test explaining what it validates
- Use proper assertions for status codes AND response structure
- Test with realistic data (valid Aadhaar: "123456789012", "987654321098")
- Generate ONLY Python code, no explanations
- Start directly with imports

Begin code generation now:
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