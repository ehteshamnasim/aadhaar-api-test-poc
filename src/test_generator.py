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
        """Build prompt for LLM"""
        endpoints = parsed_spec['endpoints']
        
        prompt = f"""You are an expert Python test engineer. Generate pytest test code for the following REST API.

Requirements:
- Use pytest framework
- Import Flask app directly: from api.dummy_aadhaar_api import app
- Use Flask test client: client = app.test_client()
- Make requests using: response = client.post('/api/v1/path', json={{...}})
- Include tests for success cases (2xx responses)
- Include tests for error cases (4xx responses)
- Test with valid and invalid payloads
- Add clear test names and docstrings
- Use pytest fixtures for test client
- Follow PEP 8 style guide

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
Generate ONLY the Python code for pytest tests. Include:
1. Import statements (pytest, pytest.mark.parametrize, from api.dummy_aadhaar_api import app)
2. Pytest fixture for test client
3. Use pytest.mark.parametrize for test data variations where multiple scenarios exist
4. Test functions using client.post(), client.get(), etc.
5. Assert statements for status codes and response structure

Example structure with parameterization:
```python
import pytest
from api.dummy_aadhaar_api import app

@pytest.fixture
def client():
    return app.test_client()

@pytest.mark.parametrize("input_data,expected_status,test_description", [
    ({{"field": "valid_value"}}, 200, "valid input"),
    ({{"field": ""}}, 400, "empty field"),
    ({{"field": None}}, 400, "null field"),
    (None, 400, "missing body"),
])
def test_endpoint_variations(client, input_data, expected_status, test_description):
    \"\"\"Test endpoint with various input scenarios\"\"\"
    response = client.post('/api/v1/path', json=input_data)
    assert response.status_code == expected_status, f"Failed for: {{test_description}}"
```

Benefits of parameterization:
- Reduces code duplication
- Makes it easy to add new test cases
- Better test organization
- Each parameter set runs as a separate test

Use parameterization when testing:
- Multiple valid/invalid input combinations
- Different error cases (missing fields, wrong types, invalid values)
- Various edge cases (empty strings, null values, boundary values)

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