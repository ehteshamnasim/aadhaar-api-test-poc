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
        """Build prompt for LLM using template files"""
        try:
            # Load system prompt
            with open('prompts/system_prompt.md', 'r') as f:
                system_prompt = f.read()
            
            # Load test generation prompt template  
            with open('prompts/test_generation_prompt.md', 'r') as f:
                prompt_template = f.read()
            
            # Build endpoints details
            endpoints_details = ""
            for i, ep in enumerate(parsed_spec['endpoints'], 1):
                endpoints_details += f"\n{i}. {ep['method']} {ep['path']}\n"
                endpoints_details += f"   Summary: {ep['summary']}\n"
                
                if ep['request_body'].get('properties'):
                    endpoints_details += f"   Request fields: {list(ep['request_body']['properties'].keys())}\n"
                    endpoints_details += f"   Required: {ep['request_body'].get('required_fields', [])}\n"
                
                endpoints_details += f"   Expected responses: {list(ep['responses'].keys())}\n"
            
            # Format the prompt template
            formatted_prompt = prompt_template.format(
                base_url=parsed_spec['base_url'],
                endpoint_count=len(parsed_spec['endpoints']),
                endpoints_details=endpoints_details
            )
            
            # Combine system prompt + formatted prompt
            final_prompt = f"{system_prompt}\n\n{formatted_prompt}"
            
            return final_prompt
            
        except Exception as e:
            print(f"   ⚠️  Error loading prompt templates: {e}")
            # Fallback to hardcoded prompt
            return self._build_fallback_prompt(parsed_spec)
    
    def _build_fallback_prompt(self, parsed_spec: Dict) -> str:
        """Fallback prompt if template files are missing"""
        base_url = parsed_spec['base_url']
        endpoints = parsed_spec['endpoints']
        
        prompt = f"""CRITICAL: Generate pytest code WITHOUT any fixtures!

You are an expert Python test engineer. Generate pytest test code for REST API.

REQUIREMENTS:
1. NO pytest fixtures - do NOT use (headers), (session), (client) etc.
2. Define BASE_URL constant at the top
3. Use direct requests.post(), requests.get() calls
4. Include success and error test cases

Base URL: {base_url}
Endpoints: {len(endpoints)}

"""
        
        for ep in endpoints:
            prompt += f"\n{ep['method']} {ep['path']}\n"
            prompt += f"Summary: {ep['summary']}\n"
            prompt += f"Expected responses: {list(ep['responses'].keys())}\n\n"
        
        prompt += """
TEMPLATE:
```python
import pytest
import requests

BASE_URL = "http://localhost:5001/api/v1"

def test_endpoint_success():
    response = requests.post(f"{BASE_URL}/endpoint", json={"field": "value"})
    assert response.status_code == 200

def test_endpoint_error():
    response = requests.post(f"{BASE_URL}/endpoint", json={})
    assert response.status_code == 400
```

Generate ONLY Python code. NO explanations. Start with imports.
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