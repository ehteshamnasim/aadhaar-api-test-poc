import ast
import subprocess
import sys
from typing import Dict, Tuple

class CodeValidator:
    """Validate generated test code"""
    
    @staticmethod
    def validate_syntax(code: str) -> Tuple[bool, str]:
        """Check if code has valid Python syntax"""
        try:
            ast.parse(code)
            return True, "Syntax valid"
        except SyntaxError as e:
            return False, f"Syntax error: {str(e)}"
    
    @staticmethod
    def validate_imports(code: str) -> Tuple[bool, str]:
        """Check if required imports are present"""
        # Check for pytest (required)
        if 'pytest' not in code:
            return False, "Missing import: pytest"
        
        # Check for either requests OR Flask app import
        has_requests = 'requests' in code
        has_flask_import = 'from api.dummy_aadhaar_api import app' in code or 'import app' in code
        
        if not (has_requests or has_flask_import):
            return False, "Missing import: pytest test approach (requests or Flask app)"
        
        return True, "All required imports present"
    
    @staticmethod
    def can_execute(file_path: str) -> Tuple[bool, str]:
        """Check if test file can be executed"""
        try:
            # Try to import the test file
            result = subprocess.run(
                [sys.executable, '-m', 'py_compile', file_path],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                return True, "File can be executed"
            else:
                return False, f"Compilation error: {result.stderr}"
        
        except subprocess.TimeoutExpired:
            return False, "Validation timeout"
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    @classmethod
    def validate_all(cls, code: str, file_path: str = None) -> Dict:
        """Run all validations"""
        results = {
            'syntax': cls.validate_syntax(code),
            'imports': cls.validate_imports(code),
            'executable': (True, "Skipped") if not file_path else cls.can_execute(file_path)
        }
        
        all_passed = all(r[0] for r in results.values())
        
        return {
            'passed': all_passed,
            'results': results
        }

if __name__ == '__main__':
    # Test validation
    sample_code = """
import pytest
import requests

def test_example():
    response = requests.get('http://localhost:5001')
    assert response.status_code == 200
"""
    
    result = CodeValidator.validate_all(sample_code)
    print("Validation results:")
    for check, (passed, msg) in result['results'].items():
        status = "✅" if passed else "❌"
        print(f"{status} {check}: {msg}")