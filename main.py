#!/usr/bin/env python3
"""
AI-Powered API Test Automation
Production-ready with proper error handling and professional logging
"""

import os
import sys
import time
import subprocess
import hashlib
import threading
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from parser import OpenAPIParser
from test_generator import TestGenerator
from contract_tester import ContractTester
from validator import CodeValidator

import requests
import re

DASHBOARD_URL = "http://localhost:5050"

# Dashboard integration functions
def send_healing_event(test_name, confidence, old_code, new_code):
    """Send self-healing event to dashboard"""
    healing_data = {
        'type': 'healing',
        'test_name': test_name,
        'confidence': confidence,
        'old_code': old_code,
        'new_code': new_code,
        'diff': {'before': old_code, 'after': new_code}
    }
    try:
        requests.post(f"{DASHBOARD_URL}/api/event", json=healing_data, timeout=2)
    except:
        pass

def send_error_analysis_event(test_name, error_type, message, root_cause, suggestions):
    """Send error analysis event to dashboard"""
    error_data = {
        'type': 'error_analysis',
        'test_name': test_name,
        'error_type': error_type,
        'message': message,
        'root_cause': root_cause,
        'suggestions': suggestions
    }
    try:
        requests.post(f"{DASHBOARD_URL}/api/event", json=error_data, timeout=2)
    except:
        pass

def send_api_diff_event(changes):
    """Send API diff event to dashboard"""
    diff_data = {'type': 'api_diff', 'changes': changes}
    try:
        requests.post(f"{DASHBOARD_URL}/api/event", json=diff_data, timeout=2)
    except:
        pass

def send_anomaly_event(endpoint, severity, anomaly_type, description, expected, actual):
    """Send anomaly event to dashboard"""
    anomaly_data = {
        'type': 'anomaly',
        'endpoint': endpoint,
        'severity': severity,
        'anomaly_type': anomaly_type,
        'description': description,
        'expected': expected,
        'actual': actual
    }
    try:
        requests.post(f"{DASHBOARD_URL}/api/event", json=anomaly_data, timeout=2)
    except:
        pass


def send_event(event_type: str, data: dict):
    """Send event to dashboard"""
    for _ in range(2):
        try:
            response = requests.post(
                f"{DASHBOARD_URL}/api/event",
                json={'type': event_type, **data},
                timeout=2
            )
            if response.status_code == 200:
                return True
        except:
            time.sleep(0.2)
    return False


class POCOrchestrator:
    def __init__(self, spec_path: str, output_dir: str = 'tests'):
        self.spec_path = spec_path
        self.output_dir = output_dir
        self.test_file_path = None
        self.start_time = datetime.now()
        self.spec_hash = self._calculate_spec_hash()
        self.version = self._get_next_version()
        self.endpoint_count = 0
        self.unique_test_count = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.actual_coverage = 0
        
        Path(output_dir).mkdir(exist_ok=True)
        Path('api').mkdir(exist_ok=True)
    
    def _calculate_spec_hash(self):
        try:
            with open(self.spec_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()[:8]
        except:
            return "unknown"
    
    def _get_next_version(self):
        version = 1
        while True:
            filename = 'test_aadhaar_api.py' if version == 1 else f'test_aadhaar_api_v{version}.py'
            if not os.path.exists(os.path.join(self.output_dir, filename)):
                return version
            version += 1
    
    def detect_spec_changes(self):
        """
        Detects changes in API specification by comparing with previous commit
        """
        try:
            # Check if we're in a git repository
            result = subprocess.run(['git', 'rev-parse', '--git-dir'], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                print("   ⚠ Not a git repository, skipping API diff")
                return
            
            # Get previous version of spec file
            result = subprocess.run(
                ['git', 'show', f'HEAD:{self.spec_path}'],
                capture_output=True, text=True
            )
            
            if result.returncode != 0:
                print("   ⚠ No previous spec version found")
                return
            
            prev_spec = result.stdout
            
            # Read current spec
            with open(self.spec_path, 'r') as f:
                current_spec = f.read()
            
            # Simple comparison of endpoints
            changes = self._compare_specs(prev_spec, current_spec)
            
            if changes:
                print(f"   ✓ Detected {len(changes)} API changes")
                send_api_diff_event(changes)
            else:
                print("   ✓ No API changes detected")
                
        except Exception as e:
            print(f"   ⚠ API diff detection error: {e}")
    
    def _compare_specs(self, prev_spec, current_spec):
        """
        Compares two API specs and identifies changes
        
        Args:
            prev_spec: Previous specification content
            current_spec: Current specification content
            
        Returns:
            List of change dictionaries
        """
        changes = []
        
        # Extract endpoint paths using regex
        prev_paths = set(re.findall(r'^\s+(/[^:]+):', prev_spec, re.MULTILINE))
        current_paths = set(re.findall(r'^\s+(/[^:]+):', current_spec, re.MULTILINE))
        
        # New endpoints
        for path in current_paths - prev_paths:
            changes.append({
                'type': 'added',
                'path': path,
                'description': f'New endpoint added: {path}',
                'breaking': False,
                'recommendation': 'Add test coverage for new endpoint'
            })
        
        # Removed endpoints
        for path in prev_paths - current_paths:
            changes.append({
                'type': 'removed',
                'path': path,
                'description': f'Endpoint removed: {path}',
                'breaking': True,
                'recommendation': 'Remove or update tests for removed endpoint'
            })
        
        # Check for schema changes in common paths
        for path in prev_paths & current_paths:
            # Simple check: if path content differs significantly
            prev_section = self._extract_path_section(prev_spec, path)
            current_section = self._extract_path_section(current_spec, path)
            
            if prev_section != current_section:
                changes.append({
                    'type': 'modified',
                    'path': path,
                    'description': f'Endpoint modified: {path}',
                    'breaking': False,
                    'recommendation': 'Review and update test assertions'
                })
        
        return changes
    
    def _extract_path_section(self, spec, path):
        """
        Extracts specification section for a given path
        
        Args:
            spec: Specification content
            path: API path
            
        Returns:
            Section content or empty string
        """
        lines = spec.split('\n')
        in_section = False
        section = []
        indent_level = 0
        
        for line in lines:
            if path in line and line.strip().startswith(path):
                in_section = True
                indent_level = len(line) - len(line.lstrip())
                section.append(line)
            elif in_section:
                current_indent = len(line) - len(line.lstrip())
                if line.strip() and current_indent <= indent_level:
                    break
                section.append(line)
        
        return '\n'.join(section)
    
    def run(self):
        """Execute workflow"""
        print("\n" + "="*70)
        print(f"AI Test Automation Pipeline - Version {self.version}")
        print("="*70 + "\n")
        
        # Clear dashboard
        send_event('clear', {'message': 'Initializing automation pipeline'})
        time.sleep(1)
        
        try:
            # Parse
            self._log("Analyzing OpenAPI specification")
            parsed_spec = self.parse_spec()
            time.sleep(1.5)
            
            # API Diff Detection
            self._log("Checking for API specification changes")
            self.detect_spec_changes()
            time.sleep(1)
            
            # Generate
            self._log("AI test generation in progress")
            test_code = self.generate_tests(parsed_spec)
            time.sleep(1.5)
            
            # Validate
            self._log("Validating generated test suite")
            self.validate_code(test_code)
            time.sleep(1.5)
            
            # Save
            self._log("Preparing test environment")
            self.save_test_file(test_code, parsed_spec)
            time.sleep(1.5)
            
            # Execute - CRITICAL FIX
            self._log("Executing automated test suite")
            self.run_tests_fixed()
            time.sleep(1.5)
            
            # Contract
            self._log("Validating API contracts")
            self.run_contract_tests(parsed_spec)
            time.sleep(1.5)
            
            # Coverage - CRITICAL FIX
            self._log("Analyzing code coverage metrics")
            self.calculate_coverage_final_fix()
            time.sleep(1.5)
            
            # Comparison
            self.show_comparison()
            time.sleep(1)
            
            # Git
            self._log("Committing changes to repository")
            self.git_commit_and_push()
            time.sleep(1)
            
            # Complete
            self._log("Automation completed successfully")
            self.print_summary()
            
        except Exception as e:
            print(f"\n{e}")
            import traceback
            traceback.print_exc()
            send_event('error', {'message': str(e)})
    
    def _log(self, message: str):
        """Enhanced logging with contextual messages"""
        print(f"[PROGRESS] {message}")
        send_event('status', {'message': message})
    
    def parse_spec(self):
        """Parse spec"""
        parser = OpenAPIParser(self.spec_path)
        parsed = parser.to_dict()
        self.endpoint_count = len(parsed['endpoints'])
        
        print(f"   ✓ {self.endpoint_count} endpoints discovered")
        
        send_event('parse', {
            'file': os.path.basename(self.spec_path),
            'endpoints': self.endpoint_count,
            'status': 'success'
        })
        
        return parsed
    
    def generate_tests(self, parsed_spec):
        """Generate tests with real-time progress"""
        generator = TestGenerator()
        
        if not generator.check_ollama_status():
            raise Exception("AI model unavailable")
        
        send_event('generate', {
            'progress': 10,
            'count': 0,
            'status': 'in_progress',
            'message': 'Initializing AI model and analyzing API specification'
        })
        
        # Progress thread with engaging messages
        stop = threading.Event()
        
        def progress():
            p = 20
            msgs = [
                'Analyzing endpoint patterns and data structures',
                'Crafting test scenarios for each API endpoint',
                'Generating assertion logic and validation checks',
                'Building comprehensive test coverage matrix',
                'Optimizing test cases for maximum code coverage',
                'Finalizing test suite structure and fixtures'
            ]
            idx = 0
            while not stop.is_set() and p < 85:
                time.sleep(8)
                if not stop.is_set():
                    send_event('generate', {
                        'progress': p,
                        'count': 0,
                        'status': 'in_progress',
                        'message': msgs[idx % len(msgs)]
                    })
                    p += 12
                    idx += 1
        
        t = threading.Thread(target=progress, daemon=True)
        t.start()
        
        try:
            test_code = generator.generate_tests(parsed_spec)
            stop.set()
            t.join(timeout=1)
            
            # Count unique tests and send individual test events
            test_names = []
            for line in test_code.split('\n'):
                if line.strip().startswith('def test_'):
                    name = line.split('(')[0].replace('def ', '').strip()
                    if name not in test_names:
                        test_names.append(name)
                        # Send individual test creation event
                        send_event('test_created', {
                            'test_number': len(test_names),
                            'test_name': name,
                            'total_expected': self.endpoint_count * 2  # Rough estimate
                        })
                        time.sleep(0.1)  # Small delay for visual effect
            
            self.unique_test_count = len(test_names)
            
            print(f"   {self.unique_test_count} test cases generated")
            
            send_event('generate', {
                'progress': 100,
                'count': self.unique_test_count,
                'status': 'success',
                'message': f'Test suite generation complete - {self.unique_test_count} test cases ready for execution'
            })
            
            return test_code
        except:
            stop.set()
            raise
    
    def validate_code(self, test_code):
        """Validate"""
        result = CodeValidator.validate_all(test_code)
        
        send_event('validate', {
            'syntax': result['results']['syntax'][0],
            'imports': result['results']['imports'][0],
            'overall': result['passed'],
            'message': 'Code quality verified' if result['passed'] else 'Validation failed'
        })
        
        if not result['passed']:
            raise Exception("Code validation failed")
        
        print("   ✓ Code quality verified")
    
    def save_test_file(self, test_code, parsed_spec):
        """Save file"""
        filename = 'test_aadhaar_api.py' if self.version == 1 else f'test_aadhaar_api_v{self.version}.py'
        self.test_file_path = os.path.join(self.output_dir, filename)
        
        # Deduplicate and convert to Flask test client format
        test_functions = {}
        lines = test_code.split('\n')
        i = 0
        while i < len(lines):
            if lines[i].strip().startswith('def test_'):
                name = lines[i].split('(')[0].replace('def ', '').strip()
                func = [lines[i]]
                i += 1
                while i < len(lines) and (not lines[i].strip() or lines[i].startswith((' ', '\t'))):
                    func.append(lines[i])
                    i += 1
                if name not in test_functions:
                    # Convert requests calls to Flask test client calls
                    func_code = '\n'.join(func)
                    # Convert: session.post(BASE_URL + '/path' -> client.post('/api/v1/path'
                    # Convert: requests.post(BASE_URL + '/path' -> client.post('/api/v1/path'
                    func_code = func_code.replace("session.post(BASE_URL + '", "client.post('/api/v1")
                    func_code = func_code.replace("session.get(BASE_URL + '", "client.get('/api/v1")
                    func_code = func_code.replace("requests.post(BASE_URL + '", "client.post('/api/v1")
                    func_code = func_code.replace("requests.get(BASE_URL + '", "client.get('/api/v1")
                    func_code = func_code.replace('session.post(BASE_URL + "', 'client.post("/api/v1')
                    func_code = func_code.replace('session.get(BASE_URL + "', 'client.get("/api/v1')
                    func_code = func_code.replace('requests.post(BASE_URL + "', 'client.post("/api/v1')
                    func_code = func_code.replace('requests.get(BASE_URL + "', 'client.get("/api/v1')
                    # Fix paths that already have /api/v1 from LLM
                    func_code = func_code.replace("client.post('/aadhaar", "client.post('/api/v1/aadhaar")
                    func_code = func_code.replace("client.get('/aadhaar", "client.get('/api/v1/aadhaar")
                    func_code = func_code.replace('client.post("/aadhaar', 'client.post("/api/v1/aadhaar')
                    func_code = func_code.replace('client.get("/aadhaar', 'client.get("/api/v1/aadhaar')
                    # Convert response.json() to response.get_json()
                    func_code = func_code.replace('.json()', '.get_json()')
                    func_code = func_code.replace('.json', '.get_json()')
                    test_functions[name] = func_code
            else:
                i += 1
        
        self.unique_test_count = len(test_functions)
        
        # Create file with Flask test client setup
        code = f'''"""AI-Generated Tests v{self.version} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
import pytest
from api.dummy_aadhaar_api import app

@pytest.fixture
def client():
    """Flask test client fixture"""
    return app.test_client()

'''
        for name in sorted(test_functions.keys()):
            code += '\n' + test_functions[name] + '\n'
        
        with open(self.test_file_path, 'w') as f:
            f.write(code)
        
        print(f"   ✓ Test suite prepared: {filename}")
    
    def _analyze_error_root_cause(self, reason, test_name):
        """
        Analyzes error message to identify root cause
        
        Args:
            reason: Error message/reason
            test_name: Name of failing test
            
        Returns:
            Human-readable root cause description
        """
        reason_lower = reason.lower()
        
        if '200 ==' in reason or '201 ==' in reason:
            return "Expected successful response but received error status code"
        elif 'assert 400' in reason or 'assert 401' in reason:
            return "Expected error response but received success status"
        elif 'connection' in reason_lower or 'refused' in reason_lower:
            return "Network connection issue - API server may not be running"
        elif 'timeout' in reason_lower:
            return "Request timeout - API response too slow"
        elif 'keyerror' in reason_lower or 'missing' in reason_lower:
            return "Missing expected field in API response"
        elif 'json' in reason_lower:
            return "Invalid JSON response format"
        else:
            return f"Test assertion failed: {reason[:100]}"
    
    def _generate_fix_suggestions(self, reason, error_type):
        """
        Generates actionable fix suggestions based on error
        
        Args:
            reason: Error message
            error_type: Type of error
            
        Returns:
            List of fix suggestion strings
        """
        suggestions = []
        reason_lower = reason.lower()
        
        if '200 ==' in reason or '201 ==' in reason:
            suggestions.append("Check if API endpoint is returning expected status code")
            suggestions.append("Verify request payload matches API requirements")
            suggestions.append("Check API server logs for error details")
        elif 'assert 400' in reason or 'assert 401' in reason:
            suggestions.append("Update test assertion to match actual API behavior")
            suggestions.append("Verify API specification for correct status codes")
        elif 'connection' in reason_lower:
            suggestions.append("Ensure API server is running (python api/dummy_aadhaar_api.py)")
            suggestions.append("Check if port is already in use")
        elif 'keyerror' in reason_lower:
            suggestions.append("Update test to match actual API response structure")
            suggestions.append("Check if API specification is outdated")
        else:
            suggestions.append("Review test logic and API specification")
            suggestions.append("Run test individually for more details: pytest -v -k test_name")
        
        return suggestions
    
    def _can_auto_heal(self, reason):
        """
        Determines if error is auto-healable
        
        Args:
            reason: Error message
            
        Returns:
            Boolean indicating if healing can be attempted
        """
        # Can heal simple assertion errors and missing fields
        healable_patterns = [
            'assert',  # Any assertion error
            'keyerror',
            'missing'
        ]
        reason_lower = reason.lower()
        return any(pattern in reason_lower for pattern in healable_patterns)
    
    def _attempt_healing(self, test_name, reason):
        """
        Attempts to generate healed test code
        
        Args:
            test_name: Name of failing test
            reason: Failure reason
            
        Returns:
            Healed code snippet or None
        """
        import re
        
        # Extract status code assertion failures
        # Matches patterns like: "assert 200 == 400", "assert 201 == 200", etc.
        status_code_pattern = r'assert (\d{3}) == (\d{3})'
        match = re.search(status_code_pattern, reason)
        
        if match:
            actual_code = match.group(1)  # The value that was received
            expected_code = match.group(2)  # The value that was expected
            
            # Determine the reason for the change
            if actual_code == '401':
                change_reason = f"API now requires authentication (401), was expecting {expected_code}"
            elif actual_code == '403':
                change_reason = f"Access forbidden (403), was expecting {expected_code}"
            elif actual_code == '400':
                change_reason = f"Bad request (400), was expecting {expected_code}"
            elif actual_code == '201':
                change_reason = f"Resource created (201), was expecting {expected_code}"
            elif actual_code == '404':
                change_reason = f"Resource not found (404), was expecting {expected_code}"
            elif actual_code == '500':
                change_reason = f"Server error (500), was expecting {expected_code}"
            else:
                change_reason = f"Status code changed from {expected_code} to {actual_code}"
            
            return f"""# HEALED: {change_reason}
# Original assertion: assert response.status_code == {expected_code}
# New assertion: assert response.status_code == {actual_code}

def {test_name}(client):
    # Test logic here...
    response = client.post('/api/v1/endpoint', json={{}})
    assert response.status_code == {actual_code}  # Auto-healed: changed from {expected_code}"""
        
        # Handle KeyError (missing JSON fields)
        if 'keyerror' in reason.lower():
            field_match = re.search(r"KeyError: '(\w+)'", reason, re.IGNORECASE)
            if field_match:
                missing_field = field_match.group(1)
                return f"""# HEALED: Field '{missing_field}' no longer exists in response
# Suggested fix: Check if field exists before accessing

def {test_name}(client):
    response = client.post('/api/v1/endpoint', json={{}})
    data = response.json()
    # Old: data['{missing_field}']
    # New: Check first
    assert '{missing_field}' in data or 'error' not in data  # Auto-healed"""
        
        # Generic assertion healing
        if 'assert' in reason.lower():
            return f"""# HEALED: Assertion failure detected
# Original error: {reason[:100]}
# Manual review recommended

def {test_name}(client):
    # Test needs manual inspection
    # Error: {reason[:80]}
    pass  # TODO: Fix assertion"""
        
        return None
    
    def _calculate_confidence(self, reason):
        """
        Calculates confidence score for healing
        
        Args:
            reason: Error message
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        import re
        
        # Extract status codes from assertion error
        status_code_pattern = r'assert (\d{3}) == (\d{3})'
        match = re.search(status_code_pattern, reason)
        
        if match:
            actual = int(match.group(1))
            expected = int(match.group(2))
            
            # Very high confidence: Simple status code changes
            if actual in [200, 201, 204]:  # Success codes
                if expected in [200, 201, 204]:
                    return 0.95  # Success to success (e.g., 200→201)
                else:
                    return 0.85  # Error to success
            
            # High confidence: Error code changes
            elif actual in [400, 401, 403, 404]:  # Client errors
                if expected in [400, 401, 403, 404]:
                    return 0.90  # Client error to client error
                elif expected in [200, 201]:
                    return 0.88  # Success to client error (API behavior change)
                else:
                    return 0.80
            
            # Medium confidence: Server errors
            elif actual in [500, 502, 503]:
                return 0.65  # Server errors are less predictable
            
            # Default for status code assertions
            return 0.75
        
        # KeyError fixes have medium-high confidence
        elif 'keyerror' in reason.lower():
            return 0.70
        
        # Generic assertion failures
        elif 'assert' in reason.lower():
            return 0.60  # Lower confidence for unknown assertions
        
        # Very low confidence for other errors
        else:
            return 0.50
    
    def _detect_anomalies(self, test_details, pytest_result):
        """
        Detects anomalies in test execution
        
        Args:
            test_details: List of test result dictionaries
            pytest_result: subprocess.CompletedProcess from pytest run
        """
        anomalies_found = False
        
        # Anomaly 1: High failure rate
        if self.unique_test_count > 0:
            failure_rate = (self.failed_tests / self.unique_test_count) * 100
            
            if failure_rate >= 50:
                send_anomaly_event(
                    endpoint='Overall Test Suite',
                    severity='critical',
                    anomaly_type='error_rate',
                    description=f'High test failure rate detected: {failure_rate:.1f}%',
                    expected='<20% failure rate',
                    actual=f'{failure_rate:.1f}% ({self.failed_tests}/{self.unique_test_count} tests failed)'
                )
                print(f"   ⚠ Anomaly: High failure rate ({failure_rate:.1f}%)")
                anomalies_found = True
            elif failure_rate >= 30:
                send_anomaly_event(
                    endpoint='Overall Test Suite',
                    severity='high',
                    anomaly_type='error_rate',
                    description=f'Elevated test failure rate: {failure_rate:.1f}%',
                    expected='<20% failure rate',
                    actual=f'{failure_rate:.1f}% ({self.failed_tests}/{self.unique_test_count} tests failed)'
                )
                print(f"   ⚠ Anomaly: Elevated failure rate ({failure_rate:.1f}%)")
                anomalies_found = True
        
        # Anomaly 2: Slow test execution (parse from pytest output)
        try:
            output = pytest_result.stdout + pytest_result.stderr
            
            # Look for timing information in pytest output
            # Format: "test_name PASSED [100%] in 5.23s"
            for line in output.split('\n'):
                if 'in ' in line and 's' in line:
                    match = re.search(r'in ([\d.]+)s', line)
                    if match:
                        duration = float(match.group(1))
                        
                        if duration > 5.0:  # Tests taking longer than 5 seconds
                            test_name = 'Unknown'
                            if '::test_' in line:
                                test_name = line.split('::')[1].split()[0]
                            
                            send_anomaly_event(
                                endpoint=test_name,
                                severity='medium',
                                anomaly_type='response_time',
                                description=f'Slow test execution detected: {duration:.2f}s',
                                expected='<2s per test',
                                actual=f'{duration:.2f}s'
                            )
                            print(f"   ⚠ Anomaly: Slow test {test_name} ({duration:.2f}s)")
                            anomalies_found = True
        except Exception as e:
            pass  # Timing analysis is best-effort
        
        # Anomaly 3: All tests failing (potential system issue)
        if self.unique_test_count > 0 and self.passed_tests == 0:
            send_anomaly_event(
                endpoint='Test Environment',
                severity='critical',
                anomaly_type='system_failure',
                description='All tests failing - possible environment or API issue',
                expected='Some tests passing',
                actual='0 tests passed'
            )
            print(f"   ⚠ Anomaly: Complete test failure - check environment")
            anomalies_found = True
        
        if not anomalies_found:
            print("   ✓ No anomalies detected")
    
    def run_tests_fixed(self):
        """Execute tests - Using Flask test client (no API server needed)"""
        
        # Verify file
        if not os.path.exists(self.test_file_path):
            print("   ✗ Test file missing")
            send_event('execute', {'passed': 0, 'failed': 0, 'total': self.unique_test_count, 'details': []})
            return
        
        print("   ✓ Tests will run using Flask test client")
        
        # Run pytest with explicit path
        try:
            # CRITICAL: Use absolute path and proper working directory
            abs_test_path = os.path.abspath(self.test_file_path)
            project_root = os.path.dirname(os.path.abspath(__file__))
            
            print(f"   Running: pytest {abs_test_path}")
            
            result = subprocess.run(
                ['pytest', abs_test_path, '-v', '--tb=line', '-p', 'no:cacheprovider'],
                capture_output=True,
                text=True,
                timeout=60,
                cwd=project_root,
                env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
            )
            
            output = result.stdout + '\n' + result.stderr
            
            # Debug output
            print("\n   Pytest Output (first 30 lines):")
            for line in output.split('\n')[:30]:
                if line.strip():
                    print(f"   | {line}")
            
            # Parse results with detailed failure reasons
            self.passed_tests = 0
            self.failed_tests = 0
            details = []
            failure_map = {}
            
            # Extract failure details from FAILURES section
            lines = output.split('\n')
            in_failures = False
            current_test = None
            
            for line in lines:
                # Detect FAILURES section
                if '=== FAILURES ===' in line or '=== ERRORS ===' in line:
                    in_failures = True
                    continue
                if in_failures and '=== short test summary' in line:
                    in_failures = False
                
                # Extract test failures
                if in_failures:
                    # Match lines like: test_aadhaar_api_v3.py:33: assert 200 == 400
                    if '.py:' in line and 'assert' in line:
                        parts = line.split(':')
                        if len(parts) >= 2:
                            # Try to extract line number and assertion
                            try:
                                line_num = parts[1].strip()
                                assertion = ':'.join(parts[2:]).strip() if len(parts) > 2 else line.split('assert')[1].strip()
                                # Store with line number as key for now
                                failure_map[line_num] = f"Line {line_num}: {assertion}"[:120]
                            except:
                                pass
            
            # Build test results
            test_line_map = {}
            for i, line in enumerate(lines):
                # Match test execution lines with status
                if '::test_' in line and (' PASSED' in line or ' FAILED' in line):
                    name = line.split('::')[1].split()[0]
                    
                    if ' PASSED' in line:
                        self.passed_tests += 1
                        details.append({'name': name, 'passed': True, 'reason': 'All assertions passed'})
                        print(f"   ✓ {name}")
                    
                    elif ' FAILED' in line:
                        self.failed_tests += 1
                        # Try to find corresponding failure reason
                        reason = "Assertion failed"
                        
                        # Look for failure line in output
                        for j in range(i+1, min(len(lines), i+50)):
                            if '.py:' in lines[j] and 'assert' in lines[j]:
                                line_num = lines[j].split(':')[1].strip() if ':' in lines[j] else ''
                                if line_num in failure_map:
                                    reason = failure_map[line_num]
                                    break
                                # Or extract directly
                                elif 'assert' in lines[j]:
                                    try:
                                        reason = lines[j].split('assert')[1].strip()[:120]
                                    except:
                                        pass
                                    break
                        
                        details.append({'name': name, 'passed': False, 'reason': reason})
                        print(f"   ✗ {name}: {reason}")
                        
                        # Send error analysis for failed test
                        error_type = "AssertionError" if "assert" in reason.lower() else "TestFailure"
                        
                        # Analyze root cause
                        root_cause = self._analyze_error_root_cause(reason, name)
                        suggestions = self._generate_fix_suggestions(reason, error_type)
                        
                        send_error_analysis_event(
                            test_name=name,
                            error_type=error_type,
                            message=reason,
                            root_cause=root_cause,
                            suggestions=suggestions
                        )
                        
                        # Attempt self-healing for certain error types
                        if self._can_auto_heal(reason):
                            healed_code = self._attempt_healing(name, reason)
                            if healed_code:
                                confidence = self._calculate_confidence(reason)
                                send_healing_event(
                                    test_name=name,
                                    confidence=confidence,
                                    old_code=f"# Original test failed: {reason}",
                                    new_code=healed_code
                                )
                                print(f"   🔧 Auto-heal attempted for {name} (confidence: {confidence:.0%})")
            
            print(f"\n   Results: {self.passed_tests}/{self.unique_test_count} passed")
            
            # Detect anomalies in test execution
            self._detect_anomalies(details, result)
            
            send_event('execute', {
                'passed': self.passed_tests,
                'failed': self.failed_tests,
                'total': self.unique_test_count,
                'details': details
            })
            
        except Exception as e:
            print(f"   ✗ Execution error: {e}")
            import traceback
            traceback.print_exc()
            send_event('execute', {'passed': 0, 'failed': self.unique_test_count, 'total': self.unique_test_count, 'details': []})
    
    def run_contract_tests(self, parsed_spec):
        """Contract tests"""
        send_event('contract', {'total': self.endpoint_count, 'passed': 0, 'failed': 0, 'status': 'running'})
        
        try:
            tester = ContractTester(parsed_spec['base_url'])
            results = tester.test_contracts(parsed_spec['endpoints'])
            summary = tester.get_summary()
            
            print(f"   ✓ {summary['passed']}/{summary['total']} contracts verified")
            
            send_event('contract', {
                'total': summary['total'],
                'passed': summary['passed'],
                'failed': summary['failed'],
                'status': 'completed'
            })
        except Exception as e:
            print(f"   ✗ Contract error: {e}")
    
    def calculate_coverage_final_fix(self):
        """Coverage - FINAL FIX"""
        
        # Only calculate if tests actually ran
        if self.passed_tests == 0 and self.failed_tests == 0:
            print("   ⚠ Skipping coverage (no tests executed)")
            self.actual_coverage = 0
            send_event('coverage', {'percentage': 0})
            return
        
        try:
            project_root = os.path.dirname(os.path.abspath(__file__))
            api_path = os.path.join(project_root, 'api')
            
            if not os.path.exists(api_path) or not os.listdir(api_path):
                print("   ⚠ No API code to measure")
                self.actual_coverage = 0
                send_event('coverage', {'percentage': 0})
                return
            
            # Clean old data
            cov_file = os.path.join(project_root, '.coverage')
            if os.path.exists(cov_file):
                os.remove(cov_file)
            
            # Run coverage
            abs_test_path = os.path.abspath(self.test_file_path)
            
            subprocess.run(
                ['coverage', 'run', '--source=api', '-m', 'pytest', abs_test_path, '-q'],
                capture_output=True,
                timeout=60,
                cwd=project_root
            )
            
            # Generate report
            result = subprocess.run(
                ['coverage', 'report'],
                capture_output=True,
                text=True,
                cwd=project_root
            )
            
            # Parse
            coverage = 0
            for line in result.stdout.split('\n'):
                if 'TOTAL' in line:
                    parts = line.split()
                    try:
                        coverage = int(float(parts[-1].rstrip('%')))
                    except:
                        pass
            
            # Generate HTML
            subprocess.run(['coverage', 'html', '-d', 'htmlcov'], capture_output=True, cwd=project_root)
            
            self.actual_coverage = coverage
            print(f"   ✓ Coverage: {coverage}%")
            
            send_event('coverage', {'percentage': coverage})
            
        except Exception as e:
            print(f"   ✗ Coverage error: {e}")
            self.actual_coverage = 0
            send_event('coverage', {'percentage': 0})
    
    def show_comparison(self):
        """Comparison"""
        duration = (datetime.now() - self.start_time).total_seconds()
        
        lines = 0
        if self.test_file_path and os.path.exists(self.test_file_path):
            with open(self.test_file_path) as f:
                lines = len(f.read().split('\n'))
        
        send_event('comparison', {
            'before': {
                'manual_effort': f'{self.endpoint_count * 30} minutes',
                'test_files': 0,
                'test_cases': 0,
                'coverage': '0%'
            },
            'after': {
                'ai_time': f'{int(duration)} seconds',
                'test_files': self.version,
                'test_cases': self.unique_test_count,
                'lines_of_code': lines,
                'coverage': f'{self.actual_coverage}%'
            }
        })
    
    def git_commit_and_push(self):
        """Git ops"""
        try:
            result = subprocess.run(['git', 'status', '--porcelain', self.test_file_path], capture_output=True, text=True)
            
            if not result.stdout.strip():
                send_event('git', {'committed': False, 'pushed': False, 'message': 'No changes'})
                return
            
            subprocess.run(['git', 'add', self.test_file_path], check=True)
            subprocess.run(['git', 'commit', '-m', f'🤖 v{self.version} - {datetime.now().strftime("%Y-%m-%d %H:%M")}', '--no-verify'], capture_output=True, check=True)
            
            result = subprocess.run(['git', 'rev-parse', '--short', 'HEAD'], capture_output=True, text=True)
            commit_hash = result.stdout.strip()
            
            print(f"   ✓ Committed: {commit_hash}")
            
            send_event('git', {'committed': True, 'pushed': False, 'message': f'({commit_hash})'})
            
            result = subprocess.run(['git', 'branch', '--show-current'], capture_output=True, text=True)
            branch = result.stdout.strip() or 'main'
            
            if 'origin' in subprocess.run(['git', 'remote'], capture_output=True, text=True).stdout:
                if subprocess.run(['git', 'push', 'origin', branch], capture_output=True, timeout=30).returncode == 0:
                    print(f"   ✓ Pushed to {branch}")
                    send_event('git', {'committed': True, 'pushed': True, 'message': f'Deployed to {branch}'})
                    send_event('cicd', {'status': 'triggered', 'message': 'Pipeline initiated', 'build': 'GitHub'})
        except Exception as e:
            print(f"   ✗ Git error: {e}")
    
    def print_summary(self):
        """Summary"""
        duration = (datetime.now() - self.start_time).total_seconds()
        
        print("\n" + "="*70)
        print("AUTOMATION COMPLETE")
        print("="*70)
        print(f"   Duration:    {duration:.1f}s")
        print(f"   Endpoints:   {self.endpoint_count}")
        print(f"   Tests:       {self.unique_test_count}")
        print(f"   Passed:      {self.passed_tests}")
        print(f"   Failed:      {self.failed_tests}")
        print(f"   Coverage:    {self.actual_coverage}%")
        print("="*70 + "\n")


def main():
    orchestrator = POCOrchestrator(spec_path='specs/aadhaar-api.yaml')
    orchestrator.run()


if __name__ == '__main__':
    main()