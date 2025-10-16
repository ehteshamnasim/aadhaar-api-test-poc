#!/usr/bin/env python3
"""
AI-Powered API Test Automation
Fixed: Coverage order, auto-refresh, loading states
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
        requests.post(f"{DASHBOARD_URL}/api/event", json={'type': event_type, **data}, timeout=2)
    except:
        pass


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
        """Execute complete workflow - CORRECTED ORDER"""
        print("\n" + "="*70)
        print("🚀 AI API Test Automation")
        print(f"   Version: v{self.version}")
        print("="*70 + "\n")
        
        try:
            # Parse
            print("📄 Parsing spec...")
            parsed_spec = self.parse_spec()
            
            # Generate
            print("\n🤖 Generating tests...")
            test_code = self.generate_tests(parsed_spec)
            
            # Validate
            print("\n✓ Validating...")
            self.validate_code(test_code)
            
            # Save
            print("\n💾 Saving...")
            self.save_test_file(test_code, parsed_spec)
            
            # Execute Tests FIRST
            print("\n🧪 Executing tests...")
            self.run_tests()
            
            # Contract tests SECOND (validates spec conformance)
            print("\n🔍 Contract testing...")
            self.run_contract_tests(parsed_spec)
            
            # Coverage LAST (measures overall test quality)
            print("\n📊 Calculating coverage...")
            self.calculate_coverage()
            
            # Show why coverage is low if applicable
            self.analyze_coverage()
            
            # Comparison
            print("\n📊 Generating comparison...")
            self.show_comparison()
            
            # Git
            print("\n📝 Git operations...")
            self.git_commit_and_push()
            
            # Send completion event for auto-refresh
            self.send_completion()
            
            self.print_summary()
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            send_event('error', {'message': str(e)})
    
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
            'message': 'Generating...'
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
            'message': f'{self.unique_test_count} tests generated'
        })
        
        return test_code
    
    def validate_code(self, test_code):
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
        """Execute tests with detailed failure reasons"""
        print(f"   Running: pytest {self.test_file_path}")
        
        # Signal start to hide sections
        send_event('tests_started', {'message': 'Tests executing...'})
        
        # Verify file exists
        if not os.path.exists(self.test_file_path):
            print(f"   ❌ File not found: {self.test_file_path}")
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
            print("   ❌ API not running on port 5001")
            print("   💡 Start: python3 api/dummy_aadhaar_api.py")
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
                            reason = "✅ All assertions passed, response matched expectations"
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
                        if not passed:
                            print(f"      Reason: {reason}")
                    
                    except Exception as e:
                        pass
            
            print(f"\n   Results: {self.passed_tests} passed, {self.failed_tests} failed")
            
            # Send to dashboard
            send_event('execute', {
                'passed': self.passed_tests,
                'failed': self.failed_tests,
                'total': self.unique_test_count,
                'details': details
            })
            
        except subprocess.TimeoutExpired:
            print("   ❌ Timeout")
            send_event('execute', {'passed': 0, 'failed': self.unique_test_count, 'total': self.unique_test_count, 'details': []})
        except Exception as e:
            print(f"   ❌ Error: {e}")
            send_event('execute', {'passed': 0, 'failed': self.unique_test_count, 'total': self.unique_test_count, 'details': []})
    
    def _extract_failure_reason(self, lines, start_index):
        """Extract detailed failure reason"""
        for i in range(start_index + 1, min(start_index + 20, len(lines))):
            line = lines[i]
            
            if 'ConnectionError' in line or 'ConnectionRefusedError' in line:
                return "❌ Cannot connect to API - verify API is running"
            
            if 'TimeoutError' in line or 'timeout' in line.lower():
                return "❌ API request timeout - API not responding"
            
            if 'AssertionError' in line:
                for j in range(i, min(i + 5, len(lines))):
                    if 'assert' in lines[j].lower():
                        return f"❌ {lines[j].strip()[:120]}"
                return "❌ Assertion failed"
            
            if 'status_code' in line.lower() and ('==' in line or '!=' in line):
                return f"❌ Status code mismatch: {line.strip()[:120]}"
            
            if 'KeyError' in line:
                return f"❌ Missing field in response: {line.strip()[:120]}"
            
            if 'Error:' in line:
                return f"❌ {line.strip()[:120]}"
        
        return "❌ Test failed - see logs"
    
    def run_contract_tests(self, parsed_spec):
        """Contract testing"""
        send_event('contract', {'total': self.endpoint_count, 'passed': 0, 'failed': 0, 'status': 'running'})
        
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
        """Calculate coverage with detailed analysis"""
        try:
            # Run coverage
            subprocess.run(
                ['coverage', 'run', '--source=api', '-m', 'pytest', self.test_file_path], 
                capture_output=True,
                timeout=60
            )
            
            # Get report
            result = subprocess.run(['coverage', 'report'], capture_output=True, text=True)
            
            coverage = 0
            for line in result.stdout.split('\n'):
                if 'TOTAL' in line:
                    try:
                        coverage = int(line.split()[-1].rstrip('%'))
                    except:
                        pass
            
            # Generate detailed report
            subprocess.run(['coverage', 'html', '-d', 'htmlcov'], capture_output=True)
            
            # Get missed lines info
            result_detailed = subprocess.run(
                ['coverage', 'report', '--show-missing'],
                capture_output=True,
                text=True
            )
            
            self.actual_coverage = coverage
            print(f"   Coverage: {coverage}%")
            
            # Store detailed info for analysis
            self.coverage_details = result_detailed.stdout
            
            send_event('coverage', {
                'percentage': coverage,
                'details': result_detailed.stdout if coverage < 85 else None
            })
            
        except Exception as e:
            print(f"   Error: {e}")
            self.actual_coverage = 0
            send_event('coverage', {'percentage': 0})
    
    def analyze_coverage(self):
        """Analyze why coverage might be low"""
        if self.actual_coverage >= 85:
            print(f"   ✅ Coverage target met!")
            return
        
        print(f"\n   ⚠️  Coverage is {self.actual_coverage}% (target: ≥85%)")
        print(f"   📋 Possible reasons:")
        
        # Analyze coverage details
        if hasattr(self, 'coverage_details'):
            lines = self.coverage_details.split('\n')
            
            for line in lines:
                if 'dummy_aadhaar_api' in line and '%' in line:
                    parts = line.split()
                    if len(parts) >= 4:
                        file = parts[0]
                        coverage_pct = parts[3].rstrip('%')
                        missing = parts[-1] if 'Missing' in self.coverage_details else ''
                        
                        print(f"      • {file}: {coverage_pct}% covered")
                        if missing and missing != file:
                            print(f"        Missing lines: {missing[:50]}")
        
        print(f"\n   💡 To improve coverage:")
        print(f"      1. Add tests for error cases (400, 403, 500)")
        print(f"      2. Test edge cases (empty fields, invalid formats)")
        print(f"      3. Test all conditional branches (if/else)")
        print(f"      4. Add boundary value tests")
    
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
        """Git commit and push"""
        try:
            result = subprocess.run(['git', 'status', '--porcelain', self.test_file_path], 
                                  capture_output=True, text=True)
            
            if not result.stdout.strip():
                print("   ℹ️  No changes")
                send_event('git', {'committed': False, 'pushed': False, 'message': 'No changes'})
                return
            
            subprocess.run(['git', 'add', self.test_file_path], check=True)
            print("   ✅ Staged")
            
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            commit_msg = f'🤖 AI tests v{self.version} - {timestamp}'
            
            subprocess.run(['git', 'commit', '-m', commit_msg, '--no-verify'],
                         capture_output=True, check=True)
            
            result = subprocess.run(['git', 'rev-parse', '--short', 'HEAD'],
                                  capture_output=True, text=True)
            commit_hash = result.stdout.strip()
            
            print(f"   ✅ Committed: {commit_hash}")
            
            send_event('git', {'committed': True, 'pushed': False, 'message': f'Committed ({commit_hash})'})
            
            # Push
            result = subprocess.run(['git', 'branch', '--show-current'],
                                  capture_output=True, text=True)
            branch = result.stdout.strip() or 'main'
            
            result = subprocess.run(['git', 'remote'], capture_output=True, text=True)
            
            if 'origin' not in result.stdout:
                print("   ℹ️  No remote")
                send_event('git', {'committed': True, 'pushed': False, 'message': 'No remote'})
                return
            
            print(f"   🚀 Pushing to origin/{branch}...")
            
            push_result = subprocess.run(['git', 'push', 'origin', branch],
                                        capture_output=True, text=True, timeout=30)
            
            if push_result.returncode == 0:
                print(f"   ✅ Pushed")
                send_event('git', {'committed': True, 'pushed': True, 'message': f'Pushed to {branch}'})
                send_event('cicd', {'status': 'triggered', 'message': 'CI/CD triggered', 'build': 'GitHub'})
            else:
                print(f"   ⚠️  Push failed")
                send_event('git', {'committed': True, 'pushed': False, 'message': 'Push failed'})
        
        except Exception as e:
            print(f"   ❌ Error: {e}")
            send_event('git', {'committed': False, 'pushed': False, 'message': str(e)[:50]})
    
    def send_completion(self):
        """Send completion event to trigger auto-refresh"""
        duration = (datetime.now() - self.start_time).total_seconds()
        
        send_event('poc_complete', {
            'duration': duration,
            'version': self.version,
            'tests': self.unique_test_count,
            'passed': self.passed_tests,
            'failed': self.failed_tests,
            'coverage': self.actual_coverage,
            'timestamp': datetime.now().isoformat()
        })
    
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