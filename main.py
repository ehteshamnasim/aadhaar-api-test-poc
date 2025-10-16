#!/usr/bin/env python3
"""
AI-Powered API Test Automation
FIXED: Coverage 0%, Parse status, Failure reasons
"""

import os
import sys
import time
import subprocess
import hashlib
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from parser import OpenAPIParser
from test_generator import TestGenerator
from contract_tester import ContractTester
from validator import CodeValidator

import requests

DASHBOARD_URL = "http://localhost:8080"


def send_event(event_type: str, data: dict):
    """Send event to dashboard"""
    try:
        response = requests.post(
            f"{DASHBOARD_URL}/api/event",
            json={'type': event_type, **data},
            timeout=2
        )
        return response.status_code == 200
    except:
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
    
    def run(self):
        """Execute workflow"""
        print("\n" + "="*70)
        print("🚀 AI API Test Automation")
        print(f"   Version: v{self.version}")
        print("="*70 + "\n")
        
        send_event('clear', {'message': 'Starting'})
        time.sleep(0.3)
        
        try:
            # Parse - FIX STATUS
            self._update_status("📄 Parsing spec...")
            parsed_spec = self.parse_spec()
            time.sleep(0.3)
            
            # Generate
            self._update_status("🤖 Generating tests...")
            test_code = self.generate_tests(parsed_spec)
            time.sleep(0.3)
            
            # Validate
            self._update_status("✓ Validating...")
            self.validate_code(test_code)
            time.sleep(0.3)
            
            # Save
            self._update_status("💾 Saving...")
            self.save_test_file(test_code, parsed_spec)
            time.sleep(0.3)
            
            # Execute - FIX FAILURE REASONS
            self._update_status("🧪 Executing tests...")
            self.run_tests_with_reasons()
            time.sleep(0.3)
            
            # Contract
            self._update_status("🔍 Contract testing...")
            self.run_contract_tests(parsed_spec)
            time.sleep(0.3)
            
            # Coverage - FIX 0% ISSUE
            self._update_status("📊 Calculating coverage...")
            self.calculate_coverage_fixed()
            time.sleep(0.3)
            
            # Comparison
            self.show_comparison()
            time.sleep(0.3)
            
            # Git
            self._update_status("📝 Git...")
            self.git_commit_and_push()
            time.sleep(0.3)
            
            self._update_status("✅ Completed!")
            self.print_summary()
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            send_event('error', {'message': str(e)})
    
    def _update_status(self, message: str):
        """Update status"""
        print(f"\n{message}")
        send_event('status', {'message': message})
    
    def parse_spec(self):
        """Parse spec - FIX PENDING STATUS"""
        try:
            parser = OpenAPIParser(self.spec_path)
            parsed = parser.to_dict()
            self.endpoint_count = len(parsed['endpoints'])
            
            print(f"   Found {self.endpoint_count} endpoints")
            for i, ep in enumerate(parsed['endpoints'], 1):
                print(f"      {i}. {ep['method']} {ep['path']}")
            
            # CRITICAL FIX: Send complete parse event
            send_event('parse', {
                'file': os.path.basename(self.spec_path),
                'endpoints': self.endpoint_count,
                'status': 'success'
            })
            
            return parsed
            
        except Exception as e:
            print(f"   ❌ Parse error: {e}")
            send_event('parse', {
                'file': os.path.basename(self.spec_path),
                'endpoints': 0,
                'status': 'failed'
            })
            raise
    
    def generate_tests(self, parsed_spec):
        """Generate tests"""
        generator = TestGenerator()
        
        if not generator.check_ollama_status():
            raise Exception("Ollama not running")
        
        send_event('generate', {
            'progress': 30,
            'count': 0,
            'status': 'in_progress',
            'message': 'AI generating...'
        })
        
        test_code = generator.generate_tests(parsed_spec)
        
        test_names = set()
        for line in test_code.split('\n'):
            if line.strip().startswith('def test_'):
                name = line.split('(')[0].replace('def ', '').strip()
                test_names.add(name)
        
        self.unique_test_count = len(test_names)
        
        print(f"   Generated {self.unique_test_count} tests")
        
        send_event('generate', {
            'progress': 100,
            'count': self.unique_test_count,
            'status': 'success',
            'message': f'{self.unique_test_count} tests generated'
        })
        
        return test_code
    
    def validate_code(self, test_code):
        """Validate"""
        result = CodeValidator.validate_all(test_code)
        
        send_event('validate', {
            'syntax': result['results']['syntax'][0],
            'imports': result['results']['imports'][0],
            'overall': result['passed'],
            'message': 'Passed' if result['passed'] else 'Failed'
        })
        
        if not result['passed']:
            raise Exception("Validation failed")
        
        print("   ✅ Passed")
    
    def save_test_file(self, test_code, parsed_spec):
        """Save test file"""
        filename = 'test_aadhaar_api.py' if self.version == 1 else f'test_aadhaar_api_v{self.version}.py'
        self.test_file_path = os.path.join(self.output_dir, filename)
        
        # Deduplicate
        test_functions = {}
        lines = test_code.split('\n')
        
        i = 0
        while i < len(lines):
            line = lines[i]
            if line.strip().startswith('def test_'):
                test_name = line.split('(')[0].replace('def ', '').strip()
                func_lines = [line]
                i += 1
                while i < len(lines):
                    if lines[i].strip() and not lines[i].startswith((' ', '\t')):
                        break
                    func_lines.append(lines[i])
                    i += 1
                
                if test_name not in test_functions:
                    test_functions[test_name] = '\n'.join(func_lines)
            else:
                i += 1
        
        self.unique_test_count = len(test_functions)
        
        # Template
        final_code = f'''"""
AI-Generated API Tests - v{self.version}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

import pytest
import requests


BASE_URL = "{parsed_spec['base_url']}"


@pytest.fixture(scope="session")
def session():
    with requests.Session() as s:
        s.headers.update({{'Content-Type': 'application/json'}})
        yield s


@pytest.fixture(scope="session", autouse=True)
def check_api():
    try:
        r = requests.get(BASE_URL.replace('/api/v1', '/health'), timeout=3)
        assert r.status_code == 200
    except Exception as e:
        pytest.fail(f"❌ API not running: {{e}}")


'''
        
        for test_name in sorted(test_functions.keys()):
            final_code += '\n' + test_functions[test_name] + '\n'
        
        with open(self.test_file_path, 'w') as f:
            f.write(final_code)
        
        print(f"   Saved: {filename}")
    
    def run_tests_with_reasons(self):
        """Execute tests - FIX FAILURE REASONS"""
        print(f"   Running: pytest {self.test_file_path}")
        
        if not os.path.exists(self.test_file_path):
            print("   ❌ File not found")
            send_event('execute', {'passed': 0, 'failed': 0, 'total': self.unique_test_count, 'details': []})
            return
        
        # Check API
        try:
            r = requests.get('http://localhost:5001/health', timeout=3)
            if r.status_code != 200:
                print("   ❌ API not responding")
                
                # Create failure details
                details = []
                for i in range(self.unique_test_count):
                    details.append({
                        'name': f'test_{i+1}',
                        'passed': False,
                        'reason': '❌ API not accessible - cannot execute test'
                    })
                
                send_event('execute', {
                    'passed': 0,
                    'failed': self.unique_test_count,
                    'total': self.unique_test_count,
                    'details': details
                })
                return
            print("   ✅ API accessible")
        except Exception as e:
            print(f"   ❌ API error: {e}")
            
            # Create failure details
            details = []
            for i in range(self.unique_test_count):
                details.append({
                    'name': f'test_{i+1}',
                    'passed': False,
                    'reason': f'❌ Cannot connect to API: {str(e)[:80]}'
                })
            
            send_event('execute', {
                'passed': 0,
                'failed': self.unique_test_count,
                'total': self.unique_test_count,
                'details': details
            })
            return
        
        # Run pytest
        try:
            result = subprocess.run(
                ['pytest', self.test_file_path, '-v', '--tb=short', '--capture=no'],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            output = result.stdout + '\n' + result.stderr
            
            # Parse with DETAILED REASONS
            self.passed_tests = 0
            self.failed_tests = 0
            details = []
            
            lines = output.split('\n')
            
            for i, line in enumerate(lines):
                if '::test_' in line and (' PASSED' in line or ' FAILED' in line):
                    try:
                        # Extract test name
                        parts = line.split('::')
                        if len(parts) >= 2:
                            test_name = parts[1].split()[0]
                            passed = 'PASSED' in line
                            
                            if passed:
                                self.passed_tests += 1
                                reason = '✅ Test passed'
                            else:
                                self.failed_tests += 1
                                # EXTRACT DETAILED REASON
                                reason = self._get_detailed_failure_reason(lines, i, output)
                            
                            details.append({
                                'name': test_name,
                                'passed': passed,
                                'reason': reason
                            })
                            
                            icon = "✅" if passed else "❌"
                            print(f"   {icon} {test_name}")
                            if not passed:
                                print(f"      → {reason}")
                    
                    except Exception as e:
                        print(f"   ⚠️ Parse error: {e}")
            
            print(f"\n   Results: {self.passed_tests} passed, {self.failed_tests} failed")
            
            send_event('execute', {
                'passed': self.passed_tests,
                'failed': self.failed_tests,
                'total': self.unique_test_count,
                'details': details
            })
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            send_event('execute', {'passed': 0, 'failed': self.unique_test_count, 'total': self.unique_test_count, 'details': []})
    
    def _get_detailed_failure_reason(self, lines, start_idx, full_output):
        """Extract detailed failure reason"""
        reason = "❌ Test failed"
        
        # Look for specific error patterns
        for i in range(start_idx + 1, min(start_idx + 25, len(lines))):
            line = lines[i].strip()
            
            # Connection errors
            if 'ConnectionError' in line or 'Connection refused' in line:
                return "❌ Cannot connect to API - verify API is running on port 5001"
            
            # Timeout
            if 'Timeout' in line or 'timeout' in line:
                return "❌ API request timeout - API not responding or too slow"
            
            # Assertion with comparison
            if 'assert' in line.lower():
                if '==' in line:
                    # Extract assertion
                    clean_line = line.replace('E       ', '').replace('assert ', '')
                    return f"❌ Assertion failed: {clean_line[:100]}"
                elif '!=' in line:
                    clean_line = line.replace('E       ', '').replace('assert ', '')
                    return f"❌ Assertion failed: {clean_line[:100]}"
            
            # Status code mismatch
            if 'status_code' in line and ('200' in line or '400' in line or '403' in line):
                return f"❌ Status code mismatch: {line[:100]}"
            
            # AssertionError with details
            if 'AssertionError:' in line:
                msg = line.split('AssertionError:')[1].strip()
                if msg:
                    return f"❌ {msg[:100]}"
            
            # KeyError
            if 'KeyError' in line:
                return f"❌ Missing field in response: {line[:100]}"
            
            # JSON errors
            if 'JSONDecodeError' in line or 'json' in line.lower():
                return "❌ Invalid JSON response from API"
        
        # Fallback: look for "E " lines (pytest error lines)
        error_lines = []
        for line in lines[start_idx:start_idx+20]:
            if line.strip().startswith('E '):
                error_lines.append(line.strip()[2:])
        
        if error_lines:
            return f"❌ {' | '.join(error_lines[:2])[:120]}"
        
        return reason
    
    def run_contract_tests(self, parsed_spec):
        """Contract testing"""
        send_event('contract', {
            'total': self.endpoint_count,
            'passed': 0,
            'failed': 0,
            'status': 'running'
        })
        
        try:
            tester = ContractTester(parsed_spec['base_url'])
            results = tester.test_contracts(parsed_spec['endpoints'])
            summary = tester.get_summary()
            
            print(f"   {summary['passed']}/{summary['total']} passed")
            
            send_event('contract', {
                'total': summary['total'],
                'passed': summary['passed'],
                'failed': summary['failed'],
                'status': 'completed'
            })
        except Exception as e:
            print(f"   Error: {e}")
    
    def calculate_coverage_fixed(self):
        """Calculate coverage - COMPLETE FIX"""
        print("   Running coverage...")
        
        try:
            project_root = os.path.dirname(os.path.abspath(__file__))
            api_path = os.path.join(project_root, 'api')
            
            print(f"   API path: {api_path}")
            
            # Verify API directory
            if not os.path.exists(api_path):
                print(f"   ⚠️ API directory not found")
                self.actual_coverage = 0
                send_event('coverage', {'percentage': 0})
                return
            
            api_files = [f for f in os.listdir(api_path) if f.endswith('.py') and f != '__init__.py']
            print(f"   API files: {api_files}")
            
            if not api_files:
                print(f"   ⚠️ No API files to measure")
                self.actual_coverage = 0
                send_event('coverage', {'percentage': 0})
                return
            
            # Clean old coverage
            coverage_file = os.path.join(project_root, '.coverage')
            if os.path.exists(coverage_file):
                os.remove(coverage_file)
            
            # Run coverage
            print("   Executing coverage run...")
            
            result = subprocess.run(
                ['coverage', 'run', '--source=api', '-m', 'pytest', self.test_file_path, '-q'],
                capture_output=True,
                text=True,
                timeout=60,
                cwd=project_root
            )
            
            # Generate report
            print("   Generating report...")
            
            report_result = subprocess.run(
                ['coverage', 'report'],
                capture_output=True,
                text=True,
                cwd=project_root
            )
            
            print("\n   Coverage Report:")
            print("   " + "="*60)
            for line in report_result.stdout.split('\n'):
                if line.strip():
                    print(f"   {line}")
            print("   " + "="*60 + "\n")
            
            # Parse percentage
            coverage = 0
            for line in report_result.stdout.split('\n'):
                if 'TOTAL' in line:
                    parts = line.split()
                    try:
                        coverage_str = parts[-1].rstrip('%')
                        coverage = int(float(coverage_str))
                        print(f"   ✅ Coverage: {coverage}%")
                    except:
                        pass
                    break
            
            # Generate HTML
            subprocess.run(
                ['coverage', 'html', '-d', 'htmlcov'],
                capture_output=True,
                cwd=project_root
            )
            
            htmlcov_index = os.path.join(project_root, 'htmlcov', 'index.html')
            if os.path.exists(htmlcov_index):
                print(f"   ✅ HTML: {htmlcov_index}")
            
            self.actual_coverage = coverage
            
            send_event('coverage', {'percentage': coverage})
            
        except FileNotFoundError:
            print("   ❌ Coverage not installed")
            self.actual_coverage = 0
            send_event('coverage', {'percentage': 0})
        
        except Exception as e:
            print(f"   ❌ Error: {e}")
            import traceback
            traceback.print_exc()
            self.actual_coverage = 0
            send_event('coverage', {'percentage': 0})
    
    def show_comparison(self):
        """Comparison"""
        duration = (datetime.now() - self.start_time).total_seconds()
        
        if self.test_file_path and os.path.exists(self.test_file_path):
            with open(self.test_file_path, 'r') as f:
                lines = len(f.read().split('\n'))
        else:
            lines = 0
        
        comparison = {
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
        }
        
        send_event('comparison', comparison)
    
    def git_commit_and_push(self):
        """Git"""
        try:
            result = subprocess.run(['git', 'status', '--porcelain', self.test_file_path], 
                                  capture_output=True, text=True)
            
            if not result.stdout.strip():
                print("   No changes")
                send_event('git', {'committed': False, 'pushed': False, 'message': 'No changes'})
                return
            
            subprocess.run(['git', 'add', self.test_file_path], check=True)
            
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            subprocess.run(['git', 'commit', '-m', f'🤖 v{self.version} - {timestamp}', '--no-verify'],
                         capture_output=True, check=True)
            
            result = subprocess.run(['git', 'rev-parse', '--short', 'HEAD'],
                                  capture_output=True, text=True)
            commit_hash = result.stdout.strip()
            
            print(f"   ✅ Committed: {commit_hash}")
            
            send_event('git', {'committed': True, 'pushed': False, 'message': f'({commit_hash})'})
            
            result = subprocess.run(['git', 'branch', '--show-current'], capture_output=True, text=True)
            branch = result.stdout.strip() or 'main'
            
            result = subprocess.run(['git', 'remote'], capture_output=True, text=True)
            
            if 'origin' in result.stdout:
                push_result = subprocess.run(['git', 'push', 'origin', branch],
                                           capture_output=True, timeout=30)
                
                if push_result.returncode == 0:
                    print(f"   ✅ Pushed")
                    send_event('git', {'committed': True, 'pushed': True, 'message': 'Pushed'})
                    send_event('cicd', {'status': 'triggered', 'message': 'CI/CD triggered', 'build': 'GitHub'})
        
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    def print_summary(self):
        duration = (datetime.now() - self.start_time).total_seconds()
        
        print("\n" + "="*70)
        print("✅ COMPLETED")
        print(f"   Duration: {duration:.1f}s")
        print(f"   Endpoints: {self.endpoint_count}")
        print(f"   Tests: {self.unique_test_count}")
        print(f"   Passed: {self.passed_tests}")
        print(f"   Failed: {self.failed_tests}")
        print(f"   Coverage: {self.actual_coverage}%")
        print("="*70 + "\n")


def main():
    orchestrator = POCOrchestrator(spec_path='specs/aadhaar-api.yaml')
    orchestrator.run()


if __name__ == '__main__':
    main()