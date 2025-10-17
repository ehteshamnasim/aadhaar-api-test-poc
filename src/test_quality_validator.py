"""
Test Quality Validator - Ensures generated tests meet quality standards
"""

import ast
import re
from typing import Dict, List, Tuple

class TestQualityValidator:
    """
    Validates quality of generated test code
    Checks for comprehensive error coverage, assertion quality, and test patterns
    """
    
    def __init__(self):
        self.quality_score = 0
        self.issues = []
        self.recommendations = []
    
    def validate_test_suite(self, test_code: str) -> Dict:
        """
        Validate overall test suite quality
        
        Parameters:
            test_code: Generated test code as string
        
        Returns:
            Dictionary with quality score, issues, and recommendations
        """
        self.quality_score = 100
        self.issues = []
        self.recommendations = []
        
        # Check test count
        test_count = self._count_tests(test_code)
        if test_count < 5:
            self.issues.append(f"Only {test_count} tests found - recommend at least 5 per endpoint")
            self.quality_score -= 20
        
        # Check error path coverage
        error_coverage = self._check_error_path_coverage(test_code)
        if error_coverage < 0.4:  # Less than 40% error tests
            self.issues.append(f"Low error path coverage ({error_coverage:.0%}) - recommend 40%+ error tests")
            self.quality_score -= 15
            self.recommendations.append("Add more tests for: missing parameters, invalid formats, not found errors")
        
        # Check assertion quality
        assertion_quality = self._check_assertion_quality(test_code)
        if assertion_quality < 0.5:
            self.issues.append("Weak assertions detected - many tests only check status codes")
            self.quality_score -= 15
            self.recommendations.append("Add assertions for response body structure, error messages, data types")
        
        # Check docstring coverage
        docstring_coverage = self._check_docstring_coverage(test_code)
        if docstring_coverage < 0.7:
            self.issues.append(f"Low docstring coverage ({docstring_coverage:.0%}) - recommend 70%+")
            self.quality_score -= 10
            self.recommendations.append("Add docstrings to all test functions explaining what they validate")
        
        # Check for edge cases
        has_edge_cases = self._check_edge_cases(test_code)
        if not has_edge_cases:
            self.issues.append("No edge case tests found")
            self.quality_score -= 10
            self.recommendations.append("Add edge case tests: empty strings, spaces, boundary values")
        
        # Check for proper test client usage
        proper_client = self._check_test_client_usage(test_code)
        if not proper_client:
            self.issues.append("Not using Flask test client properly")
            self.quality_score -= 20
            self.recommendations.append("Use Flask test client: client.post('/path', json={...})")
        
        # Check for test categories
        categories = self._identify_test_categories(test_code)
        missing_categories = []
        required = ['success', 'missing_parameter', 'invalid_format', 'not_found']
        for cat in required:
            if cat not in categories:
                missing_categories.append(cat)
        
        if missing_categories:
            self.issues.append(f"Missing test categories: {', '.join(missing_categories)}")
            self.quality_score -= len(missing_categories) * 5
            self.recommendations.append(f"Add tests for: {', '.join(missing_categories)}")
        
        return {
            'score': max(0, self.quality_score),
            'passed': self.quality_score >= 70,
            'test_count': test_count,
            'error_coverage': error_coverage,
            'assertion_quality': assertion_quality,
            'docstring_coverage': docstring_coverage,
            'has_edge_cases': has_edge_cases,
            'categories': categories,
            'issues': self.issues,
            'recommendations': self.recommendations
        }
    
    def _count_tests(self, test_code: str) -> int:
        """Count number of test functions"""
        return len(re.findall(r'def test_\w+', test_code))
    
    def _check_error_path_coverage(self, test_code: str) -> float:
        """
        Check percentage of tests that test error paths
        
        Returns:
            Ratio of error tests to total tests (0.0 to 1.0)
        """
        total_tests = self._count_tests(test_code)
        if total_tests == 0:
            return 0.0
        
        error_keywords = ['missing', 'invalid', 'not_found', 'error', 'failed', 'consent', 'expired', 'wrong']
        error_tests = 0
        
        for match in re.finditer(r'def (test_\w+)', test_code):
            test_name = match.group(1).lower()
            if any(keyword in test_name for keyword in error_keywords):
                error_tests += 1
        
        return error_tests / total_tests
    
    def _check_assertion_quality(self, test_code: str) -> float:
        """
        Check quality of assertions (not just status code checks)
        
        Returns:
            Ratio of comprehensive assertions to total assertions (0.0 to 1.0)
        """
        # Count all assertions
        all_assertions = len(re.findall(r'assert ', test_code))
        if all_assertions == 0:
            return 0.0
        
        # Count only status code assertions
        status_only = len(re.findall(r'assert .*status_code.*[=!<>]', test_code))
        
        # Good assertions check response body, data structure, error messages
        good_assertions = all_assertions - status_only
        
        return good_assertions / all_assertions if all_assertions > 0 else 0.0
    
    def _check_docstring_coverage(self, test_code: str) -> float:
        """
        Check percentage of test functions with docstrings
        
        Returns:
            Ratio of tests with docstrings to total tests (0.0 to 1.0)
        """
        total_tests = self._count_tests(test_code)
        if total_tests == 0:
            return 0.0
        
        # Count docstrings (triple quotes after def test_)
        docstrings = len(re.findall(r'def test_\w+[^:]*:\s*[\'\"]{3}', test_code))
        
        return docstrings / total_tests
    
    def _check_edge_cases(self, test_code: str) -> bool:
        """
        Check if edge cases are tested
        
        Returns:
            True if edge case tests found
        """
        edge_keywords = ['empty', 'spaces', 'boundary', 'edge', 'zero', 'null', 'none']
        test_code_lower = test_code.lower()
        
        return any(keyword in test_code_lower for keyword in edge_keywords)
    
    def _check_test_client_usage(self, test_code: str) -> bool:
        """
        Check if Flask test client is used properly
        
        Returns:
            True if proper client usage detected
        """
        # Check for Flask test client pattern
        has_client_fixture = '@pytest.fixture' in test_code and 'def client' in test_code
        has_client_usage = 'client.post(' in test_code or 'client.get(' in test_code
        
        return has_client_fixture and has_client_usage
    
    def _identify_test_categories(self, test_code: str) -> List[str]:
        """
        Identify which test categories are present
        
        Returns:
            List of category names found in tests
        """
        categories = []
        test_code_lower = test_code.lower()
        
        category_patterns = {
            'success': ['success', 'valid', 'happy'],
            'missing_parameter': ['missing', 'required', 'without'],
            'invalid_format': ['invalid', 'format', 'short', 'long', 'letters', 'special'],
            'not_found': ['not_found', 'notfound', '404', 'nonexistent'],
            'consent': ['consent', 'authorization', 'permission'],
            'expired': ['expired', 'timeout'],
            'edge_case': ['empty', 'spaces', 'boundary', 'edge']
        }
        
        for category, keywords in category_patterns.items():
            if any(keyword in test_code_lower for keyword in keywords):
                categories.append(category)
        
        return categories
    
    def generate_improvement_prompt(self, validation_result: Dict, original_prompt: str) -> str:
        """
        Generate improved prompt based on validation issues
        
        Parameters:
            validation_result: Result from validate_test_suite()
            original_prompt: Original prompt used
        
        Returns:
            Enhanced prompt addressing quality issues
        """
        if validation_result['passed']:
            return ""
        
        improvements = "\n\nADDITIONAL REQUIREMENTS TO ADDRESS QUALITY ISSUES:\n"
        
        if validation_result['test_count'] < 5:
            improvements += "- Generate AT LEAST 8-10 test cases per endpoint\n"
        
        if validation_result['error_coverage'] < 0.4:
            improvements += "- CRITICAL: 50%+ of tests MUST test error paths (4xx responses)\n"
            improvements += "- Include tests for: missing params, invalid formats, not found, consent errors\n"
        
        if validation_result['assertion_quality'] < 0.5:
            improvements += "- Add comprehensive assertions beyond status codes\n"
            improvements += "- Assert response body structure: assert 'error' in data\n"
            improvements += "- Assert error messages: assert data['message'] contains expected text\n"
        
        if validation_result['docstring_coverage'] < 0.7:
            improvements += "- Add docstrings to ALL test functions\n"
            improvements += "- Example: \"\"\"Test verify endpoint with missing aadhaar parameter\"\"\"\n"
        
        if not validation_result['has_edge_cases']:
            improvements += "- Add edge case tests: empty strings, spaces, boundary values\n"
        
        if validation_result['recommendations']:
            improvements += "\nRECOMMENDATIONS:\n"
            for rec in validation_result['recommendations']:
                improvements += f"- {rec}\n"
        
        return original_prompt + improvements


if __name__ == '__main__':
    # Test the validator
    sample_test = '''
import pytest
from api.dummy_aadhaar_api import app

@pytest.fixture
def client():
    return app.test_client()

def test_verify_success(client):
    """Test successful verification"""
    response = client.post('/api/v1/aadhaar/verify', json={"aadhaar_number": "123456789012"})
    assert response.status_code == 200

def test_verify_missing_param(client):
    response = client.post('/api/v1/aadhaar/verify', json={})
    assert response.status_code == 400
'''
    
    validator = TestQualityValidator()
    result = validator.validate_test_suite(sample_test)
    
    print(f"Quality Score: {result['score']}/100")
    print(f"Passed: {result['passed']}")
    print(f"Test Count: {result['test_count']}")
    print(f"Error Coverage: {result['error_coverage']:.0%}")
    print(f"Assertion Quality: {result['assertion_quality']:.0%}")
    print(f"\nIssues:")
    for issue in result['issues']:
        print(f"  - {issue}")
    print(f"\nRecommendations:")
    for rec in result['recommendations']:
        print(f"  - {rec}")
