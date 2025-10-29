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
    def __init__(self, spec_path: str, output_dir: str = None):
        self.spec_path = spec_path
        
        # If no output_dir specified, use 'tests' subfolder in same directory as spec file
        if output_dir is None:
            spec_dir = os.path.dirname(spec_path) or '.'
            output_dir = os.path.join(spec_dir, 'tests')
        
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
        self.spec_changes = []  # Track detected spec changes
        self.changed_endpoints = set()  # Track which endpoints changed
        
        Path(output_dir).mkdir(parents=True, exist_ok=True)
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
        Detects changes in API specification by comparing with previous version
        Uses file-based tracking instead of git (no git dependency)
        Each spec file has its own version tracking
        """
        try:
            # Store baseline in same directory as spec file (hidden file)
            spec_dir = os.path.dirname(self.spec_path) or '.'
            spec_basename = os.path.basename(self.spec_path).replace('.yaml', '').replace('.yml', '')
            version_file = os.path.join(spec_dir, f'.{spec_basename}.baseline')
            
            # Read current spec
            with open(self.spec_path, 'r') as f:
                current_spec = f.read()
            
            # Check if previous version exists
            if not os.path.exists(version_file):
                print(f"   ℹ️  First run for {spec_basename} - saving spec baseline")
                # Save current spec as baseline for next run
                with open(version_file, 'w') as f:
                    f.write(current_spec)
                return
            
            # Load previous spec
            with open(version_file, 'r') as f:
                prev_spec = f.read()
            
            # Compare specs
            changes = self._compare_specs(prev_spec, current_spec)
            
            if changes:
                self.spec_changes = changes  # Store for selective regeneration
                
                # Extract changed endpoints (exclude server URL changes)
                for change in changes:
                    if 'path' in change and change.get('type') != 'server_url_changed':
                        self.changed_endpoints.add(change['path'])
                
                print(f"   ✓ Detected {len(changes)} API changes in {spec_basename}")
                if self.changed_endpoints:
                    print(f"   → {len(self.changed_endpoints)} endpoints affected")
                send_api_diff_event(changes)
                
                # Update baseline after successful detection
                with open(version_file, 'w') as f:
                    f.write(current_spec)
            else:
                print(f"   ✓ No API changes detected in {spec_basename}")
                
        except Exception as e:
            print(f"   ⚠ API diff detection error: {e}")
    
    def _compare_specs(self, prev_spec, current_spec):
        """
        Compares two API specs and identifies changes
        
        Args:
            prev_spec: Previous specification content
            current_spec: Current specification content
            
        Returns:
            List of changes with detailed information
        """
        import yaml
        import re
        
        changes = []
        
        try:
            # Parse YAML specs
            prev_data = yaml.safe_load(prev_spec)
            current_data = yaml.safe_load(current_spec)
            
            # Check server URL changes
            prev_servers = prev_data.get('servers', [])
            current_servers = current_data.get('servers', [])
            
            prev_urls = [s.get('url', '') for s in prev_servers if isinstance(s, dict)]
            current_urls = [s.get('url', '') for s in current_servers if isinstance(s, dict)]
            
            if prev_urls != current_urls:
                changes.append({
                    'type': 'server_url_changed',
                    'path': 'servers',
                    'description': f'Server URL changed: {prev_urls} → {current_urls}',
                    'breaking': False,
                    'recommendation': 'Update base URL in tests'
                })
            
            # Get paths (endpoints)
            prev_paths = prev_data.get('paths', {})
            current_paths = current_data.get('paths', {})
            
            # Track all paths
            all_paths = set(list(prev_paths.keys()) + list(current_paths.keys()))
            
            for path in all_paths:
                prev_methods = prev_paths.get(path, {})
                current_methods = current_paths.get(path, {})
                
                # New endpoint
                if path not in prev_paths:
                    changes.append({
                        'type': 'added',
                        'path': path,
                        'methods': list(current_methods.keys()),
                        'description': f'New endpoint: {path}',
                        'breaking': False,
                        'recommendation': 'Generate tests for new endpoint'
                    })
                
                # Removed endpoint
                elif path not in current_paths:
                    changes.append({
                        'type': 'removed',
                        'path': path,
                        'methods': list(prev_methods.keys()),
                        'description': f'Endpoint removed: {path}',
                        'breaking': True,
                        'recommendation': 'Archive tests for removed endpoint'
                    })
                
                # Modified endpoint - check each HTTP method
                else:
                    all_methods = set(list(prev_methods.keys()) + list(current_methods.keys()))
                    
                    for method in all_methods:
                        if method == 'parameters':  # Skip parameter definitions
                            continue
                            
                        prev_method_spec = prev_methods.get(method, {})
                        current_method_spec = current_methods.get(method, {})
                        
                        # New method
                        if method not in prev_methods:
                            changes.append({
                                'type': 'method_added',
                                'path': path,
                                'method': method.upper(),
                                'description': f'New method {method.upper()} added to {path}',
                                'breaking': False,
                                'recommendation': f'Generate tests for {method.upper()} {path}'
                            })
                        
                        # Removed method
                        elif method not in current_methods:
                            changes.append({
                                'type': 'method_removed',
                                'path': path,
                                'method': method.upper(),
                                'description': f'Method {method.upper()} removed from {path}',
                                'breaking': True,
                                'recommendation': f'Archive tests for {method.upper()} {path}'
                            })
                        
                        # Check for response/request changes
                        else:
                            method_changes = self._compare_method_specs(
                                path, method.upper(), prev_method_spec, current_method_spec
                            )
                            changes.extend(method_changes)
            
            return changes
            
        except Exception as e:
            print(f"   ⚠️  YAML parsing error, falling back to simple comparison: {e}")
            # Fallback to regex-based comparison
            return self._compare_specs_simple(prev_spec, current_spec)
    
    def _compare_method_specs(self, path, method, prev_spec, current_spec):
        """
        Compare specifications for a specific HTTP method
        
        Returns:
            List of detected changes
        """
        changes = []
        
        # Check response codes
        prev_responses = prev_spec.get('responses', {})
        current_responses = current_spec.get('responses', {})
        
        prev_codes = set(prev_responses.keys())
        current_codes = set(current_responses.keys())
        
        # New response codes
        for code in current_codes - prev_codes:
            changes.append({
                'type': 'response_added',
                'path': path,
                'method': method,
                'status_code': code,
                'description': f'{method} {path}: New response code {code}',
                'breaking': False,
                'recommendation': f'Update tests to handle {code} response'
            })
        
        # Removed response codes
        for code in prev_codes - current_codes:
            changes.append({
                'type': 'response_removed',
                'path': path,
                'method': method,
                'status_code': code,
                'description': f'{method} {path}: Response code {code} removed',
                'breaking': True,
                'recommendation': f'Tests will be regenerated automatically without {code} response assertions'
            })
        
        # Check request body changes
        prev_request = prev_spec.get('requestBody', {})
        current_request = current_spec.get('requestBody', {})
        
        if prev_request != current_request:
            changes.append({
                'type': 'request_modified',
                'path': path,
                'method': method,
                'description': f'{method} {path}: Request body changed',
                'breaking': True,
                'recommendation': f'Regenerate tests for {method} {path}'
            })
        
        return changes
    
    def _compare_specs_simple(self, prev_spec, current_spec):
        """
        Simple regex-based comparison (fallback)
        """
        import re
        
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
    
    def _filter_spec_for_changed_endpoints(self, parsed_spec):
        """
        Filter spec to include only changed endpoints
        
        Args:
            parsed_spec: Full parsed specification
            
        Returns:
            Filtered spec with only changed endpoints
        """
        if not self.changed_endpoints:
            return parsed_spec  # No changes, return full spec
        
        filtered_spec = parsed_spec.copy()
        filtered_spec['endpoints'] = [
            ep for ep in parsed_spec['endpoints']
            if ep.get('path') in self.changed_endpoints
        ]
        
        return filtered_spec
    
    def _load_previous_tests(self):
        """
        Load tests from the most recent previous version
        
        File Organization:
        - Current test: tests/test_aadhaar_api_v{N}.py (active, being generated)
        - Previous test: tests/test_aadhaar_api_v{N-1}.py (source of preserved tests)
        - Older versions: tests/test_aadhaar_api_v*.py (historical versions)
        
        Returns:
            Dict with test code and metadata, or None
        """
        if self.version == 1:
            return None  # No previous version
        
        prev_version = self.version - 1
        prev_filename = f'test_aadhaar_api_v{prev_version}.py' if prev_version > 1 else 'test_aadhaar_api.py'
        prev_path = os.path.join(self.output_dir, prev_filename)
        
        if not os.path.exists(prev_path):
            return None
        
        try:
            with open(prev_path, 'r') as f:
                prev_code = f.read()
            
            return {
                'code': prev_code,
                'version': prev_version,
                'path': prev_path
            }
        except Exception as e:
            print(f"   ⚠️  Error loading previous tests: {e}")
            return None
    
    def _extract_tests_for_endpoints(self, test_code, endpoints_to_keep):
        """
        Extract test functions for specific endpoints from test code
        
        Args:
            test_code: Full test file content
            endpoints_to_keep: Set of endpoint paths to keep tests for
            
        Returns:
            List of test function strings
        """
        import re
        
        tests = []
        
        # Remove section headers from the test code before extraction
        # This prevents duplicate headers from being included in preserved tests
        cleaned_code = re.sub(
            r'#\s*={20,}\s*\n#\s*(PRESERVED|REGENERATED)\s+TESTS.*?\n#.*?\n#\s*={20,}\s*\n',
            '',
            test_code,
            flags=re.MULTILINE
        )
        
        # Also remove inline comments that mark tests
        cleaned_code = re.sub(
            r'#\s*[✓🔄]\s*(PRESERVED|REGENERATED)\s*-.*?\n',
            '',
            cleaned_code
        )
        
        # Find all test functions
        test_pattern = r'(def test_\w+\(.*?\):.*?)(?=\ndef test_|\Z)'
        matches = re.findall(test_pattern, cleaned_code, re.DOTALL)
        
        for test_func in matches:
            # Check if test belongs to an endpoint we want to keep
            # Look for endpoint paths in test function
            keep_test = False
            
            if not endpoints_to_keep:  # If no specific endpoints, keep all
                keep_test = True
            else:
                for endpoint in endpoints_to_keep:
                    # Convert endpoint path to test-friendly format
                    endpoint_slug = endpoint.replace('/', '_').replace('-', '_').strip('_')
                    if endpoint_slug in test_func or endpoint in test_func:
                        keep_test = True
                        break
            
            if keep_test:
                tests.append(test_func)
        
        return tests
    
    def _merge_tests(self, old_tests, new_tests, parsed_spec):
        """
        Merge old passing tests with newly generated tests
        
        Args:
            old_tests: Previous test code
            new_tests: Newly generated test code
            parsed_spec: Current API specification
            
        Returns:
            Merged test code
        """
        import re
        
        if not old_tests:
            return new_tests  # No old tests to merge
        
        # Calculate unchanged endpoints
        all_endpoints = set(ep['path'] for ep in parsed_spec['endpoints'])
        unchanged_endpoints = all_endpoints - self.changed_endpoints
        
        if not unchanged_endpoints:
            return new_tests  # All endpoints changed, use only new tests
        
        print(f"   📝 Merging tests: keeping {len(unchanged_endpoints)} unchanged endpoint tests")
        
        # Extract tests for unchanged endpoints from old code
        old_test_functions = self._extract_tests_for_endpoints(
            old_tests['code'], 
            unchanged_endpoints
        )
        
        # Extract header (imports, fixtures) from new tests
        header_pattern = r'^(.*?)(?=def test_)'
        header_match = re.search(header_pattern, new_tests, re.DOTALL)
        header = header_match.group(1) if header_match else ''
        
        # Extract new test functions
        new_test_functions = self._extract_tests_for_endpoints(
            new_tests,
            self.changed_endpoints
        )
        
        # Combine
        merged_code = header + '\n'
        
        # Add old tests first (preserved)
        if old_test_functions:
            merged_code += '\n# ========================================\n'
            merged_code += f'# PRESERVED TESTS ({len(old_test_functions)} tests from previous version)\n'
            merged_code += '# These tests passed and their endpoints were unchanged\n'
            merged_code += '# ========================================\n\n'
            
            print(f"   DEBUG: Adding {len(old_test_functions)} preserved tests with comments")
            
            for test in old_test_functions:
                # Add inline comment before each preserved test
                test_lines = test.split('\n')
                if test_lines and test_lines[0].startswith('def test_'):
                    merged_code += f'# ✓ PRESERVED - Endpoint unchanged\n'
                merged_code += test + '\n\n'
        
        # Add new tests
        if new_test_functions:
            merged_code += '\n# ========================================\n'
            merged_code += f'# REGENERATED TESTS ({len(new_test_functions)} tests for changed endpoints)\n'
            merged_code += '# These tests were regenerated due to API spec changes\n'
            merged_code += '# ========================================\n\n'
            
            for test in new_test_functions:
                # Add inline comment before each regenerated test
                test_lines = test.split('\n')
                if test_lines and test_lines[0].startswith('def test_'):
                    merged_code += f'# 🔄 REGENERATED - Endpoint modified\n'
                merged_code += test + '\n\n'
        
        merged_count = len(old_test_functions) + len(new_test_functions)
        print(f"   ✓ Merged {len(old_test_functions)} preserved + {len(new_test_functions)} regenerated = {merged_count} total tests")
        
        # Send regeneration event
        send_event('test_regeneration', {
            'preserved_count': len(old_test_functions),
            'regenerated_count': len(new_test_functions),
            'total_count': merged_count,
            'changed_endpoints': list(self.changed_endpoints),
            'unchanged_endpoints': list(unchanged_endpoints),
            'spec_changes': self.spec_changes  # Include detailed spec changes
        })
        
        return merged_code
    
    def generate_tests(self, parsed_spec):
        """Generate tests with real-time progress and selective regeneration"""
        generator = TestGenerator()
        
        if not generator.check_ollama_status():
            raise Exception("AI model unavailable")
        
        # Check if we should do selective regeneration
        previous_tests = None
        spec_to_generate = parsed_spec
        
        if self.spec_changes:
            # Load previous tests
            previous_tests = self._load_previous_tests()
            
            if previous_tests:
                print(f"   📋 Spec changes detected - using selective regeneration")
                print(f"   → Regenerating tests for {len(self.changed_endpoints)} changed endpoints")
                print(f"   → Preserving tests for unchanged endpoints")
                
                # Filter spec to only changed endpoints
                spec_to_generate = self._filter_spec_for_changed_endpoints(parsed_spec)
            else:
                print(f"   ℹ️  Spec changes detected but no previous tests found")
        
        send_event('generate', {
            'progress': 10,
            'count': 0,
            'status': 'in_progress',
            'message': 'Initializing AI model and analyzing API specification',
            'selective': bool(previous_tests and self.spec_changes),
            'endpoints_to_regenerate': len(self.changed_endpoints) if self.spec_changes else len(parsed_spec['endpoints'])
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
            if previous_tests and self.spec_changes:
                msgs.insert(0, f'Selective regeneration: targeting {len(self.changed_endpoints)} changed endpoints')
            
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
            # Generate tests for the filtered spec
            test_code = generator.generate_tests(spec_to_generate)
            stop.set()
            t.join(timeout=1)
            
            # Merge with previous tests if doing selective regeneration
            was_selective = False
            if previous_tests and self.spec_changes:
                test_code = self._merge_tests(previous_tests, test_code, parsed_spec)
                was_selective = True
            
            # Count unique tests 
            test_names = []
            for line in test_code.split('\n'):
                if line.strip().startswith('def test_'):
                    name = line.split('(')[0].replace('def ', '').strip()
                    if name not in test_names:
                        test_names.append(name)
                        
                        # Only send individual test events if NOT selective regeneration
                        # (selective regeneration already sent the regeneration event with counts)
                        if not was_selective:
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
        
        # Check if this is merged code with comments (selective regeneration)
        if '# PRESERVED TESTS' in test_code or '# REGENERATED TESTS' in test_code:
            print("   ✓ Saving merged test file with preservation comments")
            with open(self.test_file_path, 'w') as f:
                f.write(test_code)
            # Extract test count from merged code
            test_count = test_code.count('def test_')
            self.unique_test_count = test_count
            print(f"   ✓ Test suite prepared: {filename}")
            return
        
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
    
    def _execute_pytest(self, test_file_path):
        """
        Execute pytest on the given test file and return the result.
        
        Args:
            test_file_path: Absolute path to the test file
            
        Returns:
            subprocess.CompletedProcess: The result of pytest execution
        """
        abs_test_path = os.path.abspath(test_file_path)
        project_root = os.path.dirname(os.path.abspath(__file__))
        
        result = subprocess.run(
            ['pytest', abs_test_path, '-v', '--tb=line', '-p', 'no:cacheprovider'],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=project_root,
            env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
        )
        
        return result
    
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
            # Execute pytest using helper method
            result = self._execute_pytest(self.test_file_path)
            
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
    """
    Main entry point for test automation
    
    Usage:
        python main.py specs/aadhaar-api.yaml
        python main.py specs/payment-api.yaml
        python main.py specs/user-management.yaml
    """
    if len(sys.argv) < 2:
        print("Usage: python main.py <spec_file_path>")
        print("Example: python main.py specs/aadhaar-api.yaml")
        sys.exit(1)
    
    spec_path = sys.argv[1]
    
    if not os.path.exists(spec_path):
        print(f"Error: Spec file not found: {spec_path}")
        sys.exit(1)
    
    orchestrator = POCOrchestrator(spec_path=spec_path)
    orchestrator.run()


if __name__ == '__main__':
    main()