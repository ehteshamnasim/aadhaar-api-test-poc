"""
Enhanced Error Analysis System
Provides detailed error messages with request/response logging and fix suggestions
"""

import json
import re
import traceback
from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass, asdict


@dataclass
class APIRequest:
    """Represents an API request"""
    method: str
    url: str
    headers: Dict[str, str]
    body: Optional[Dict] = None
    timestamp: str = None
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()
    
    def to_curl(self) -> str:
        """Convert request to curl command for easy reproduction"""
        curl = f"curl -X {self.method} '{self.url}'"
        
        for key, value in self.headers.items():
            curl += f" -H '{key}: {value}'"
        
        if self.body:
            curl += f" -d '{json.dumps(self.body)}'"
        
        return curl


@dataclass
class APIResponse:
    """Represents an API response"""
    status_code: int
    headers: Dict[str, str]
    body: Optional[Dict] = None
    response_time_ms: float = 0
    timestamp: str = None
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


@dataclass
class ErrorDetail:
    """Detailed error information"""
    test_name: str
    error_type: str
    error_message: str
    stack_trace: str
    line_number: Optional[int] = None
    file_path: Optional[str] = None
    request: Optional[APIRequest] = None
    response: Optional[APIResponse] = None
    expected_value: Optional[str] = None
    actual_value: Optional[str] = None
    suggested_fixes: List[str] = None
    root_cause: Optional[str] = None
    timestamp: str = None
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()
        if self.suggested_fixes is None:
            self.suggested_fixes = []


class ErrorAnalyzer:
    """
    Analyzes test failures and provides actionable insights
    """
    
    def __init__(self):
        """Initialize error analyzer"""
        self.error_history = []
        self.patterns = {}
    
    def analyze_failure(self, test_name: str, pytest_output: str,
                       test_code: str = None) -> ErrorDetail:
        """
        Analyze a test failure and provide detailed insights
        
        Args:
            test_name: Name of failed test
            pytest_output: Raw pytest output
            test_code: Source code of the test
            
        Returns:
            ErrorDetail object with comprehensive failure analysis
        """
        error_detail = ErrorDetail(
            test_name=test_name,
            error_type='Unknown',
            error_message='',
            stack_trace=pytest_output
        )
        
        # Parse pytest output
        self._parse_pytest_output(error_detail, pytest_output)
        
        # Determine root cause
        error_detail.root_cause = self._determine_root_cause(error_detail)
        
        # Generate fix suggestions
        error_detail.suggested_fixes = self._generate_fix_suggestions(error_detail, test_code)
        
        # Store in history
        self.error_history.append(error_detail)
        
        # Learn patterns
        self._learn_pattern(error_detail)
        
        return error_detail
    
    def _parse_pytest_output(self, error_detail: ErrorDetail, output: str):
        """Parse pytest output to extract detailed error information"""
        lines = output.split('\n')
        
        for i, line in enumerate(lines):
            # Extract error type
            if 'Error:' in line or 'Exception:' in line:
                error_detail.error_type = line.split(':')[0].strip().split()[-1]
            
            # Extract file and line number
            file_line_match = re.search(r'([^\s]+\.py):(\d+):', line)
            if file_line_match:
                error_detail.file_path = file_line_match.group(1)
                error_detail.line_number = int(file_line_match.group(2))
            
            # Extract assertion details
            if 'AssertionError' in line or 'assert' in line.lower():
                error_detail.error_message = line.strip()
                
                # Try to extract expected vs actual
                expected, actual = self._extract_expected_actual(line, lines, i)
                if expected:
                    error_detail.expected_value = expected
                if actual:
                    error_detail.actual_value = actual
            
            # Extract connection errors
            if 'ConnectionError' in line or 'Timeout' in line:
                error_detail.error_message = line.strip()
                error_detail.error_type = 'ConnectionError' if 'ConnectionError' in line else 'Timeout'
    
    def _extract_expected_actual(self, line: str, all_lines: List[str], 
                                current_idx: int) -> tuple:
        """Extract expected and actual values from assertion"""
        expected = None
        actual = None
        
        # Pattern 1: "assert 200 == 201"
        match = re.search(r'assert\s+(.+?)\s*==\s*(.+?)(?:\s|$)', line)
        if match:
            actual = match.group(1).strip()
            expected = match.group(2).strip()
            return expected, actual
        
        # Pattern 2: "AssertionError: 200 != 201"
        match = re.search(r'AssertionError:\s*(.+?)\s*!=\s*(.+?)(?:\s|$)', line)
        if match:
            actual = match.group(1).strip()
            expected = match.group(2).strip()
            return expected, actual
        
        # Pattern 3: Multi-line output
        for i in range(current_idx, min(current_idx + 10, len(all_lines))):
            if 'Expected:' in all_lines[i]:
                expected = all_lines[i].split('Expected:')[1].strip()
            elif 'Actual:' in all_lines[i]:
                actual = all_lines[i].split('Actual:')[1].strip()
        
        return expected, actual
    
    def _determine_root_cause(self, error_detail: ErrorDetail) -> str:
        """
        Determine the root cause of the error
        
        Returns:
            Human-readable root cause explanation
        """
        error_type = error_detail.error_type
        error_msg = error_detail.error_message.lower()
        
        # API Response Errors
        if 'status' in error_msg and 'code' in error_msg:
            if error_detail.expected_value and error_detail.actual_value:
                return (f"API returned status code {error_detail.actual_value} "
                       f"but test expected {error_detail.expected_value}. "
                       f"The API behavior has likely changed.")
        
        # Schema/Field Errors
        if 'keyerror' in error_type.lower() or 'key' in error_msg:
            return ("API response is missing expected field. "
                   "The response schema may have changed.")
        
        # Value Mismatch
        if 'assertionerror' in error_type.lower() and error_detail.expected_value:
            return (f"Expected value '{error_detail.expected_value}' "
                   f"but got '{error_detail.actual_value}'. "
                   f"The API response value has changed.")
        
        # Connection Issues
        if 'connectionerror' in error_type.lower():
            return ("Unable to connect to the API. "
                   "Check if the API server is running and accessible.")
        
        # Timeout
        if 'timeout' in error_type.lower():
            return ("API request timed out. "
                   "The API may be slow or unresponsive.")
        
        # Type Errors
        if 'typeerror' in error_type.lower():
            return ("Data type mismatch in response. "
                   "The API response structure may have changed.")
        
        return "Unable to determine specific root cause. Review error details below."
    
    def _generate_fix_suggestions(self, error_detail: ErrorDetail, 
                                 test_code: str = None) -> List[str]:
        """
        Generate actionable fix suggestions
        
        Returns:
            List of suggested fixes
        """
        suggestions = []
        error_type = error_detail.error_type.lower()
        error_msg = error_detail.error_message.lower()
        
        # Status code mismatch
        if 'status' in error_msg and error_detail.expected_value and error_detail.actual_value:
            suggestions.append(
                f"Update assertion: Change 'assert response.status_code == {error_detail.expected_value}' "
                f"to 'assert response.status_code == {error_detail.actual_value}'"
            )
            suggestions.append(
                "Verify if this status code change is intentional in the API"
            )
            suggestions.append(
                "Check API documentation for recent changes"
            )
        
        # Missing field
        if 'keyerror' in error_type:
            suggestions.append(
                "Check the actual API response to see available fields"
            )
            suggestions.append(
                "Use response.get('field', default_value) instead of response['field'] for optional fields"
            )
            suggestions.append(
                "Verify the field name spelling and case sensitivity"
            )
        
        # Connection errors
        if 'connectionerror' in error_type or 'connection' in error_msg:
            suggestions.append(
                "Ensure the API server is running: python api/dummy_aadhaar_api.py"
            )
            suggestions.append(
                "Check if the API URL is correct"
            )
            suggestions.append(
                "Verify network connectivity and firewall settings"
            )
        
        # Timeout
        if 'timeout' in error_type:
            suggestions.append(
                "Increase the request timeout value"
            )
            suggestions.append(
                "Check API performance and response times"
            )
            suggestions.append(
                "Investigate if the API endpoint is experiencing issues"
            )
        
        # Value mismatch
        if 'assertionerror' in error_type and 'value' not in error_msg and error_detail.expected_value:
            suggestions.append(
                f"Update expected value from '{error_detail.expected_value}' "
                f"to '{error_detail.actual_value}'"
            )
            suggestions.append(
                "Confirm if this change in API response is expected"
            )
        
        # General suggestions if no specific ones
        if not suggestions:
            suggestions.append(
                "Review the complete error stack trace for more context"
            )
            suggestions.append(
                "Check recent API changes or updates"
            )
            suggestions.append(
                "Run the test in isolation to rule out test interdependencies"
            )
        
        return suggestions
    
    def _learn_pattern(self, error_detail: ErrorDetail):
        """Learn from error patterns for future predictions"""
        pattern_key = f"{error_detail.error_type}:{error_detail.test_name}"
        
        if pattern_key not in self.patterns:
            self.patterns[pattern_key] = {
                'count': 0,
                'first_seen': error_detail.timestamp,
                'last_seen': error_detail.timestamp,
                'common_fixes': []
            }
        
        self.patterns[pattern_key]['count'] += 1
        self.patterns[pattern_key]['last_seen'] = error_detail.timestamp
    
    def format_error_report(self, error_detail: ErrorDetail, 
                          include_curl: bool = True) -> str:
        """
        Format error detail into human-readable report
        
        Args:
            error_detail: Error details to format
            include_curl: Include curl command for reproduction
            
        Returns:
            Formatted error report
        """
        report = []
        report.append("=" * 70)
        report.append(f"TEST FAILURE ANALYSIS: {error_detail.test_name}")
        report.append("=" * 70)
        report.append("")
        
        # Error Summary
        report.append("ERROR SUMMARY:")
        report.append(f"  Type: {error_detail.error_type}")
        report.append(f"  Message: {error_detail.error_message}")
        if error_detail.line_number:
            report.append(f"  Location: {error_detail.file_path}:Line {error_detail.line_number}")
        report.append(f"  Time: {error_detail.timestamp}")
        report.append("")
        
        # Root Cause
        report.append("ROOT CAUSE:")
        report.append(f"  {error_detail.root_cause}")
        report.append("")
        
        # Expected vs Actual
        if error_detail.expected_value or error_detail.actual_value:
            report.append("COMPARISON:")
            if error_detail.expected_value:
                report.append(f"  Expected: {error_detail.expected_value}")
            if error_detail.actual_value:
                report.append(f"  Actual:   {error_detail.actual_value}")
            report.append("")
        
        # Request Details
        if error_detail.request:
            report.append("REQUEST:")
            report.append(f"  Method: {error_detail.request.method}")
            report.append(f"  URL: {error_detail.request.url}")
            if error_detail.request.body:
                report.append(f"  Body: {json.dumps(error_detail.request.body, indent=4)}")
            
            if include_curl:
                report.append("")
                report.append("  Reproduce with curl:")
                report.append(f"  {error_detail.request.to_curl()}")
            report.append("")
        
        # Response Details
        if error_detail.response:
            report.append("RESPONSE:")
            report.append(f"  Status Code: {error_detail.response.status_code}")
            report.append(f"  Response Time: {error_detail.response.response_time_ms}ms")
            if error_detail.response.body:
                report.append(f"  Body: {json.dumps(error_detail.response.body, indent=4)}")
            report.append("")
        
        # Fix Suggestions
        if error_detail.suggested_fixes:
            report.append("SUGGESTED FIXES:")
            for i, fix in enumerate(error_detail.suggested_fixes, 1):
                report.append(f"  {i}. {fix}")
            report.append("")
        
        report.append("=" * 70)
        
        return '\n'.join(report)
    
    def get_error_statistics(self) -> Dict:
        """Get statistics about errors"""
        if not self.error_history:
            return {
                'total_errors': 0,
                'error_types': {},
                'most_common_errors': []
            }
        
        error_types = {}
        for error in self.error_history:
            error_type = error.error_type
            error_types[error_type] = error_types.get(error_type, 0) + 1
        
        most_common = sorted(error_types.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            'total_errors': len(self.error_history),
            'error_types': error_types,
            'most_common_errors': [{'type': t, 'count': c} for t, c in most_common],
            'patterns_learned': len(self.patterns)
        }
    
    def export_error_report(self, output_file: str):
        """Export all errors to JSON file"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'statistics': self.get_error_statistics(),
            'errors': [asdict(error) for error in self.error_history],
            'patterns': self.patterns
        }
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
