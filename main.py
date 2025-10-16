#!/usr/bin/env python3
"""
AI-Powered API Test Automation
FIXED: Coverage calculation + Real-time UI updates
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
        if response.status_code == 200:
            print(f"  ✓ Event sent: {event_type}")
            return True
    except Exception as e:
        print(f"  ⚠️ Event failed: {e}")
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
        
        # Ensure API directory exists
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
        """Execute complete workflow"""
        print("\n" + "="*70)
        print("🚀 AI API Test Automation")
        print(f"   Version: v{self.version}")
        print("="*70 + "\n")
        
        # Send initial clear event
        send_event('clear', {'message': 'Starting new POC run'})
        time.sleep(0.5)
        
        try:
            # Parse
            self._update_status("📄 Parsing OpenAPI specification...")
            parsed_spec = self.parse_spec()
            time.sleep(0.5)
            
            # Generate
            self._update_status("🤖 Generating tests with AI...")
            test_code = self.generate_tests(parsed_spec)
            time.sleep(0.5)
            
            # Validate
            self._update_status("✓ Validating generated code...")
            self.validate_code(test_code)
            time.sleep(0.5)
            
            # Save
            self._update_status("💾 Saving test file...")
            self.save_test_file(test_code, parsed_spec)
            time.sleep(0.5)
            
            # Execute Tests
            self._update_status("🧪 Executing tests...")
            self.run_tests()
            time.sleep(0.5)
            
            # Contract tests
            self._update_status("🔍 Running contract tests...")
            self.run_contract_tests(parsed_spec)
            time.sleep(0.5)
            
            # Coverage - CRITICAL FIX
            self._update_status("📊 Calculating code coverage...")
            self.calculate_coverage()
            time.sleep(0.5)
            
            # Comparison
            self._update_status("📊 Generating comparison...")
            self.show_comparison()
            time.sleep(0.5)
            
            # Git
            self._update_status("📝 Git operations...")
            self.git_commit_and_push()
            time.sleep(0.5)
            
            # Complete
            self._update_status("✅ POC completed successfully!")
            self.print_summary()
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            send_event('error', {'message': str(e)})
    
    def _update_status(self, message: str):
        """Update status in UI"""
        print(f"\n{message}")
        send_event('status', {'message': message})
    
    def parse_spec(self):
        parser = OpenAPIParser(self.spec_path)
        parsed = parser.to_dict()
        self.endpoint_count = len(parsed['endpoints'])
        
        print(f"   Found {self.endpoint_count} endpoints")
        
        send_event('parse', {
            'file': os.path.basename(self.spec_path),
            'endpoints': self.endpoint_count
        })
        
        return parsed
    
    def generate_tests(self, parsed_spec):
        generator = TestGenerator()
        
        if not generator.check_ollama_status():
            raise Exception("Ollama not running")
        
        send_event('generate', {
            'progress': 30,
            'count': 0,
            'status': 'in_progress',
            'message': 'AI generating tests...'
        })
        
        test_code = generator.generate_tests(parsed_spec)
        
        # Count tests
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
            'message': f'Generated {self.unique_test_count} tests successfully!'
        })
        
        return test_code
    
    def validate_code(self, test_code):
        result = CodeValidator.validate_all(test_code)
        
        send_event('validate', {
            'syntax': result['results']['syntax'][0],
            'imports': result['results']['imports'][0],
            'overall': result['passed'],
            'message': 'Validation passed' if result['passed'] else 'Validation failed'
        })
        
        if not result['passed']:
            raise Exception("Validation failed")
        
        print("   ✅ Passed")
    
    def save_test_file(self, test_code, parsed_spec):
        """Save test file with forced template"""
        filename = 'test_aadhaar_api.py' if self.version == 1 else f'test_aadhaar_api_v{self.version}.py'
        self.test_file_path = os.path.join(self.output_dir, filename)
        
        # Deduplicate tests
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
        
        # FORCED TEMPLATE
        final_code = f'''"""
AI-Generated API Tests - v{self.version}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Endpoints: {self.endpoint_count} | Tests: {self.unique_test_count}
"""

import pytest
import requests


BASE_URL = "{parsed_spec['base_url']}"


@pytest.fixture(scope="session")
def session():
    """Provides requests Session"""
    with requests.Session() as s:
        s.headers.update({{'Content-Type': 'application/json'}})
        yield s


@pytest.fixture(scope="session", autouse=True)
def check_api():
    """Verify API is running"""
    try:
        r = requests.get(BASE_URL.replace('/api/v1', '/health'), timeout=3)
        assert r.status_code == 200
        print("\\n✅ API accessible")
    except Exception as e:
        pytest.fail(f"❌ API not running: {{e}}")


'''
        
        # Add test functions
        for test_name in sorted(test_functions.keys()):
            final_code += '\n' + test_functions[test_name] + '\n'
        
        # Save
        with open(self.test_file_path, 'w') as f:
            f.write(final_code)
        
        print(f"   Saved: {filename} ({self.unique_test_count} tests)")
    
    def run_tests(self):
        """Execute tests"""
        print(f"   Running: pytest {self.test_file_path}")
        
        if not os.path.exists(self.test_file_path):
            print(f"   ❌ File not found")
            send_event('execute', {'passed': 0, 'failed': 0, 'total': self.unique_test_count, 'details': []})
            return
        
        # Check API
        try:
            r = requests.get('http://localhost:5001/health', timeout=3)
            if r.status_code != 200:
                print("   ❌ API not responding")
                send_event('execute', {'passed': 0, 'failed': self.unique_test_count, 'total': self.unique_test_count, 'details': []})
                return
            print("   ✅ API accessible")
        except:
            print("   ❌ API not running")
            send_event('execute', {'passed': 0, 'failed': self.unique_test_count, 'total': self.unique_test_count, 'details': []})
            return
        
        # Run pytest
        try:
            result = subprocess.run(
                ['pytest', self.test_file_path, '-v', '--tb=short'],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            output = result.stdout + result.stderr
            
            # Parse results
            self.passed_tests = 0
            self.failed_tests = 0
            details = []
            
            lines = output.split('\n')
            
            for i, line in enumerate(lines):
                if '::test_' in line and (' PASSED' in line or ' FAILED' in line):
                    try:
                        test_name = line.split('::')[1].split()[0]
                        passed = 'PASSED' in line
                        
                        if passed:
                            self.passed_tests += 1
                            reason = "✅ Test passed"
                        else:
                            self.failed_tests += 1
                            reason = self._extract_failure_reason(lines, i)
                        
                        details.append({
                            'name': test_name,
                            'passed': passed,
                            'reason': reason
                        })
                        
                        icon = "✅" if passed else "❌"
                        print(f"   {icon} {test_name}")
                    
                    except:
                        pass
            
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
    
    def _extract_failure_reason(self, lines, start_index):
        """Extract failure reason"""
        for i in range(start_index + 1, min(start_index + 20, len(lines))):
            line = lines[i]
            
            if 'ConnectionError' in line:
                return "❌ Cannot connect to API"
            if 'TimeoutError' in line:
                return "❌ API timeout"
            if 'AssertionError' in line:
                for j in range(i, min(i + 5, len(lines))):
                    if 'assert' in lines[j].lower():
                        return f"❌ {lines[j].strip()[:100]}"
                return "❌ Assertion failed"
            if 'Error:' in line:
                return f"❌ {line.strip()[:100]}"
        
        return "❌ Test failed"
    
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
    
    def calculate_coverage(self):
        """Calculate coverage - COMPLETE FIX"""
        print("   Analyzing code coverage...")
        
        try:
            # Get project root directory
            project_root = os.path.dirname(os.path.abspath(__file__))
            api_path = os.path.join(project_root, 'api')
            
            print(f"   Project root: {project_root}")
            print(f"   API path: {api_path}")
            print(f"   Test file: {self.test_file_path}")
            
            # Check if API directory exists
            if not os.path.exists(api_path):
                print(f"   ⚠️ API directory not found at: {api_path}")
                print(f"   Creating API directory...")
                os.makedirs(api_path, exist_ok=True)
            
            # List API files
            if os.path.exists(api_path):
                api_files = [f for f in os.listdir(api_path) if f.endswith('.py')]
                print(f"   API files found: {api_files}")
            
            # Step 1: Clean old coverage data
            coverage_file = os.path.join(project_root, '.coverage')
            if os.path.exists(coverage_file):
                os.remove(coverage_file)
                print("   Cleaned old coverage data")
            
            # Step 2: Run coverage
            print("   Running coverage analysis...")
            
            cmd = [
                'coverage', 'run',
                '--source=api',
                '--omit=*/tests/*,*/venv/*',
                '-m', 'pytest',
                self.test_file_path,
                '-v'
            ]
            
            print(f"   Command: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60,
                cwd=project_root
            )
            
            if result.returncode != 0:
                print(f"   ⚠️ Coverage run warnings:")
                if result.stderr:
                    print(f"   {result.stderr[:200]}")
            else:
                print("   ✅ Coverage data collected")
            
            # Step 3: Generate report
            print("   Generating coverage report...")
            
            report_result = subprocess.run(
                ['coverage', 'report', '-m'],
                capture_output=True,
                text=True,
                cwd=project_root
            )
            
            print("\n   Coverage Report:")
            print("   " + "="*60)
            for line in report_result.stdout.split('\n'):
                if line.strip():
                    print(f"   {line}")
            print("   " + "="*60)
            
            # Step 4: Parse percentage
            coverage = 0
            for line in report_result.stdout.split('\n'):
                if 'TOTAL' in line:
                    parts = line.split()
                    try:
                        coverage_str = parts[-1].rstrip('%')
                        coverage = int(float(coverage_str))
                        print(f"\n   ✅ Parsed coverage: {coverage}%")
                    except Exception as e:
                        print(f"   ⚠️ Parse error: {e}")
            
            # Step 5: Generate HTML
            print("   Generating HTML report...")
            
            html_result = subprocess.run(
                ['coverage', 'html', '-d', 'htmlcov'],
                capture_output=True,
                text=True,
                cwd=project_root
            )
            
            htmlcov_index = os.path.join(project_root, 'htmlcov', 'index.html')
            
            if os.path.exists(htmlcov_index):
                print(f"   ✅ HTML report: {htmlcov_index}")
            else:
                print(f"   ⚠️ HTML report not generated")
            
            self.actual_coverage = coverage
            
            print(f"\n   Final Coverage: {coverage}%")
            
            # Send to dashboard
            send_event('coverage', {'percentage': coverage})
            
            # Wait to ensure event is processed
            time.sleep(0.5)
            
        except FileNotFoundError:
            print("   ❌ Coverage not installed")
            print("   💡 Install: pip install coverage")
            self.actual_coverage = 0
            send_event('coverage', {'percentage': 0})
        
        except Exception as e:
            print(f"   ❌ Coverage error: {e}")
            import traceback
            traceback.print_exc()
            self.actual_coverage = 0
            send_event('coverage', {'percentage': 0})
    
    def show_comparison(self):
        """Generate comparison"""
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
        """Git operations"""
        try:
            result = subprocess.run(['git', 'status', '--porcelain', self.test_file_path], 
                                  capture_output=True, text=True)
            
            if not result.stdout.strip():
                print("   No changes")
                send_event('git', {'committed': False, 'pushed': False, 'message': 'No changes'})
                return
            
            subprocess.run(['git', 'add', self.test_file_path], check=True)
            print("   ✅ Staged")
            
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            subprocess.run(['git', 'commit', '-m', f'🤖 v{self.version} - {timestamp}', '--no-verify'],
                         capture_output=True, check=True)
            
            result = subprocess.run(['git', 'rev-parse', '--short', 'HEAD'],
                                  capture_output=True, text=True)
            commit_hash = result.stdout.strip()
            
            print(f"   ✅ Committed: {commit_hash}")
            
            send_event('git', {'committed': True, 'pushed': False, 'message': f'Committed ({commit_hash})'})
            
            # Push
            result = subprocess.run(['git', 'branch', '--show-current'], capture_output=True, text=True)
            branch = result.stdout.strip() or 'main'
            
            result = subprocess.run(['git', 'remote'], capture_output=True, text=True)
            
            if 'origin' in result.stdout:
                print(f"   🚀 Pushing...")
                
                push_result = subprocess.run(['git', 'push', 'origin', branch],
                                           capture_output=True, text=True, timeout=30)
                
                if push_result.returncode == 0:
                    print(f"   ✅ Pushed")
                    send_event('git', {'committed': True, 'pushed': True, 'message': f'Pushed to {branch}'})
                    send_event('cicd', {'status': 'triggered', 'message': 'CI/CD triggered', 'build': 'GitHub'})
                else:
                    print(f"   ⚠️ Push failed")
                    send_event('git', {'committed': True, 'pushed': False, 'message': 'Push failed'})
        
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    def print_summary(self):
        duration = (datetime.now() - self.start_time).total_seconds()
        
        print("\n" + "="*70)
        print("✅ COMPLETED")
        print(f"   Duration: {duration:.1f}s")
        print(f"   Tests: {self.unique_test_count}")
        print(f"   Passed: {self.passed_tests}")
        print(f"   Failed: {self.failed_tests}")
        print(f"   Coverage: {self.actual_coverage}%")
        print("="*70)
        print(f"\n🌐 Dashboard: http://localhost:8080\n")


def main():
    orchestrator = POCOrchestrator(spec_path='specs/aadhaar-api.yaml')
    orchestrator.run()


if __name__ == '__main__':
    main()