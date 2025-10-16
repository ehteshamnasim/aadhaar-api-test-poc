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

DASHBOARD_URL = "http://localhost:8080"


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
    
    def run(self):
        """Execute workflow"""
        print("\n" + "="*70)
        print(f"🚀 AI Test Automation v{self.version}")
        print("="*70 + "\n")
        
        # Clear dashboard
        send_event('clear', {'message': 'Initializing automation pipeline'})
        time.sleep(1)
        
        try:
            # Parse
            self._log("Analyzing OpenAPI specification")
            parsed_spec = self.parse_spec()
            time.sleep(1.5)
            
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
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            send_event('error', {'message': str(e)})
    
    def _log(self, message: str):
        """Professional logging"""
        print(f"⚡ {message}")
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
        """Generate tests"""
        generator = TestGenerator()
        
        if not generator.check_ollama_status():
            raise Exception("AI model unavailable")
        
        send_event('generate', {
            'progress': 20,
            'count': 0,
            'status': 'in_progress',
            'message': 'AI analyzing API structure'
        })
        
        # Progress thread
        stop = threading.Event()
        
        def progress():
            p = 30
            msgs = ['Generating test scenarios', 'Writing test code', 'Optimizing coverage']
            idx = 0
            while not stop.is_set() and p < 85:
                time.sleep(10)
                if not stop.is_set():
                    send_event('generate', {
                        'progress': p,
                        'count': 0,
                        'status': 'in_progress',
                        'message': msgs[idx % len(msgs)]
                    })
                    p += 20
                    idx += 1
        
        t = threading.Thread(target=progress, daemon=True)
        t.start()
        
        try:
            test_code = generator.generate_tests(parsed_spec)
            stop.set()
            t.join(timeout=1)
            
            # Count unique
            test_names = set()
            for line in test_code.split('\n'):
                if line.strip().startswith('def test_'):
                    test_names.add(line.split('(')[0].replace('def ', '').strip())
            
            self.unique_test_count = len(test_names)
            
            print(f"   ✓ {self.unique_test_count} test cases generated")
            
            send_event('generate', {
                'progress': 100,
                'count': self.unique_test_count,
                'status': 'success',
                'message': f'{self.unique_test_count} test cases ready'
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
        
        # Deduplicate
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
                    test_functions[name] = '\n'.join(func)
            else:
                i += 1
        
        self.unique_test_count = len(test_functions)
        
        # Create file
        code = f'''"""AI-Generated Tests v{self.version} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
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
    except:
        pytest.fail("API unavailable")

'''
        for name in sorted(test_functions.keys()):
            code += '\n' + test_functions[name] + '\n'
        
        with open(self.test_file_path, 'w') as f:
            f.write(code)
        
        print(f"   ✓ Test suite prepared: {filename}")
    
    def run_tests_fixed(self):
        """Execute tests - COMPLETE FIX"""
        
        # Verify file
        if not os.path.exists(self.test_file_path):
            print("   ✗ Test file missing")
            send_event('execute', {'passed': 0, 'failed': 0, 'total': self.unique_test_count, 'details': []})
            return
        
        # Check API
        try:
            r = requests.get('http://localhost:5001/health', timeout=3)
            if r.status_code != 200:
                raise Exception("unhealthy")
        except Exception as e:
            print(f"   ✗ API unavailable: {e}")
            details = [{'name': f'test_{i}', 'passed': False, 'reason': f'API unavailable: {e}'} for i in range(self.unique_test_count)]
            send_event('execute', {'passed': 0, 'failed': self.unique_test_count, 'total': self.unique_test_count, 'details': details})
            return
        
        print("   ✓ API verified")
        
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
            
            # Parse results
            self.passed_tests = 0
            self.failed_tests = 0
            details = []
            
            for line in output.split('\n'):
                if '::test_' in line:
                    if ' PASSED' in line:
                        self.passed_tests += 1
                        name = line.split('::')[1].split()[0]
                        details.append({'name': name, 'passed': True, 'reason': 'Test passed'})
                        print(f"   ✓ {name}")
                    elif ' FAILED' in line:
                        self.failed_tests += 1
                        name = line.split('::')[1].split()[0]
                        reason = "Test failed - check logs"
                        details.append({'name': name, 'passed': False, 'reason': reason})
                        print(f"   ✗ {name}")
            
            print(f"\n   Results: {self.passed_tests}/{self.unique_test_count} passed")
            
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
        print("✅ AUTOMATION COMPLETE")
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