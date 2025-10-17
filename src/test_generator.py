import requests
import json
from typing import Dict, List

class TestGenerator:
    """Generate pytest tests using Ollama with optimized settings"""
    
    def __init__(self, ollama_url: str = "http://localhost:11434"):
        self.ollama_url = ollama_url
        self.model = "qwen2.5-coder:14b"
        print(f"   🤖 Using model: {self.model}")
    
    def generate_tests(self, parsed_spec: Dict) -> str:
        """Generate complete test file from parsed spec with optimized settings"""
        prompt = self._build_prompt(parsed_spec)
        
        print(f"   Using Ollama model: {self.model}")
        print(f"   Ollama URL: {self.ollama_url}")
        
        # Call Ollama API with optimized parameters for speed
        response = requests.post(
            f"{self.ollama_url}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,      # Lower = faster + more focused
                    "num_predict": 1500,     # Reduced tokens = faster generation
                    "top_p": 0.9,
                    "top_k": 40,
                    "repeat_penalty": 1.1,
                    "num_ctx": 2048,         # Smaller context = faster
                    "num_thread": 8,         # Parallel processing
                    "num_gpu": 1             # Use GPU if available
                }
            },
            timeout=180  # 3 minutes - much faster timeout
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
        """Build concise prompt for fast LLM generation"""
        endpoints = parsed_spec['endpoints']
        
        # Simplified prompt for speed
        prompt = f"""Generate pytest tests for REST API. Use @pytest.mark.parametrize to reduce code.

SETUP:
```python
import pytest
from api.dummy_aadhaar_api import app

@pytest.fixture
def client():
    return app.test_client()
```

ENDPOINTS:
"""
        
        for ep in endpoints:
            prompt += f"{ep['method']} {ep['path']}"
            if ep['request_body'].get('required_fields'):
                prompt += f" (Required: {ep['request_body']['required_fields']})"
            prompt += "\n"
        
        prompt += """
Generate 3-4 tests per endpoint:
1. Valid success case
2. Missing required field (use parametrize for multiple fields)
3. Invalid format (use parametrize)
4. Not found/Error case

Use parametrize to combine similar tests. Keep it concise. Output only Python code, no explanations.
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
        """Check if qwen2.5-coder:14b model exists"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                for model in models:
                    model_name = model.get('name', '')
                    if 'qwen2.5-coder' in model_name:
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
        print(f"⚠️  {generator.model} not found!")
        print(f"   Pull it with: ollama pull {generator.model}")
        exit(1)
    
    print(f"✅ {generator.model} model found")
    
    # Generate tests
    parser = OpenAPIParser('specs/aadhaar-api.yaml')
    parsed_spec = parser.to_dict()
    
    print("\nGenerating tests...")
    test_code = generator.generate_tests(parsed_spec)
    
    print("\nGenerated Test Code:")
    print("=" * 80)
    print(test_code)