#!/usr/bin/env python3
"""
AI-Powered API Test Automation - PRODUCTION READY
Fixed: Real-time updates, correct flow, accurate counts, coverage calculation
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
    """Send event to dashboard with retry"""
    for attempt in range(3):
        try:
            response = requests.post(
                f"{DASHBOARD_URL}/api/event",
                json={'type': event_type, **data},
                timeout=2
            )
            if response.status_code == 200:
                print(f"  ✓ Event: {event_type}")
                return True
            time.sleep(0.2)
        except:
            if attempt < 2:
                time.sleep(0.3)
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
        """Execute complete workflow with proper event sequencing"""
        print("\n" + "="*70)
        print("🚀 AI API Test Automation - v" + str(self.version))
        print("="*70 + "\n")
        
        # STEP 0: Clear dashboard
        print("🔄 Initializing...")
        send_event('clear', {'message': 'Starting new POC run'})
        time.sleep(1)  # Wait for clear to complete
        
        try:
            # STEP 1: Parse spec
            print("\n📄 STEP 1: Parsing OpenAPI specification...")
            send_event('status', {'message': '📄 Parsing OpenAPI specification...'})
            time.sleep(0.5)
            
            parsed_spec = self.parse_spec()
            time.sleep(1)  # Wait for UI update
            
            # STEP 2: Generate tests
            print("\n🤖 STEP 2: Generating tests with AI...")
            send_event('status', {'message': '🤖 Generating tests with AI...'})
            time.sleep(0.5)
            
            test_code = self.generate_tests(parsed_spec)
            time.sleep(1)  # Wait for UI update
            
            # STEP 3: Validate code
            print("\n✓ STEP 3: Validating generated code...")
            send_event('status', {'message': '✓ Validating generated code...'})
            time.sleep(0.5)
            
            self.validate_code(test_code)
            time.sleep(1)  # Wait for UI update
            
            # STEP 4: Save test file
            print("\n💾 STEP 4: Saving test file...")
            send_event('status', {'message': '💾 Saving test file...'})
            time.sleep(0.5)
            
            self.save_test_file(test_code, parsed_spec)
            time.sleep(1)  # Wait for UI update
            
            # STEP 5: Execute tests
            print("\n🧪 STEP 5: Executing tests...")
            send_event('status', {'message': '🧪 Executing tests...'})
            time.sleep(0.5)
            
            self.run_tests_with_details()
            time.sleep(1)  # Wait for UI update
            
            # STEP 6: Contract testing
            print("\n🔍 STEP 6: Running contract tests...")
            send_event('status', {'message': '🔍 Running contract tests...'})
            time.sleep(0.5)
            
            self.run_contract_tests(parsed_spec)
            time.sleep(1)  # Wait for UI update
            
            # STEP 7: Calculate coverage
            print("\n📊 STEP 7: Calculating code coverage...")
            send_event('status', {'message': '📊 Calculating code coverage...'})
            time.sleep(0.5)
            
            self.calculate_coverage_correctly()
            time.sleep(1)  # Wait for UI update
            
            # STEP 8: Generate comparison
            print("\n📊 STEP 8: Generating comparison...")
            send_event('status', {'message': '📊 Generating comparison...'})
            time.sleep(0.5)
            
            self.show_comparison()
            time.sleep(1)  # Wait for UI update
            
            # STEP 9: Git operations
            print("\n📝 STEP 9: Git operations...")
            send_event('status', {'message': '📝 Git operations...'})
            time.sleep(0.5)
            
            self.git_commit_and_push()
            time.sleep(1)  # Wait for UI update
            
            # COMPLETE
            print("\n✅ POC COMPLETED!")
            send_event('status', {'message': '✅ POC completed successfully!'})
            
            self.print_summary()
            
        except Exception as e:
            print(f"\n❌ FATAL ERROR: {e}")
            import traceback
            traceback.print_exc()
            send_event('error', {'message': str(e)})
            raise
    
    def parse_spec(self):
        """Parse OpenAPI specification"""
        try:
            parser = OpenAPIParser(self.spec_path)
            parsed = parser.to_dict()
            self.endpoint_count = len(parsed['endpoints'])
            
            print(f"   ✅ Found {self.endpoint_count} endpoints")
            for i, ep in enumerate(parsed['endpoints'], 1):
                print(f"      {i}. {ep['method']:6} {ep['path']}")
            
            # Send parse event with status
            send_event('parse', {
                'file': os.path.basename(self.spec_path),
                'endpoints': self.endpoint_count,
                'status': 'success'
            })
            
            return parsed
            
        except Exception as e:
            print(f"   ❌ Parse failed: {e}")
            send_event('parse', {
                'file': os.path.basename(self.spec_path),
                'endpoints': 0,
                'status': 'failed'
            })
            raise
    
    def generate_tests(self, parsed_spec):
        """Generate tests with progress updates"""
        generator = TestGenerator()
        
        if not generator.check_ollama_status():
            raise Exception("Ollama not running - Start with: ollama serve")
        
        # Initial progress
        send_event('generate', {
            'progress': 10,
            'count': 0,
            'status': 'in_progress',
            'message': 'Initializing AI model...'
        })
        time.sleep(0.5)
        
        # Start progress thread
        stop_progress = threading.Event()
        
        def send_progress_updates():
            progress = 20
            messages = [
                'Sending specification to LLM...',
                'LLM analyzing API structure...',
                'LLM generating test scenarios...',
                'LLM writing test code...',
                'Finalizing tests...'
            ]
            idx = 0
            
            while not stop_progress.is_set() and progress < 90:
                time.sleep(7)
                if not stop_progress.is_set():
                    send_event('generate', {
                        'progress': min(progress, 90),
                        'count': 0,
                        'status': 'in_progress',
                        'message': messages[idx % len(messages)]
                    })
                    progress += 15
                    idx += 1
        
        progress_thread = threading.Thread(target=send_progress_updates, daemon=True)
        progress_thread.start()
        
        try:
            # Generate tests
            print("   ⏳ Waiting for LLM response (30-60s)...")
            test_code = generator.generate_tests(parsed_spec)
            
            # Stop progress thread
            stop_progress.set()
            progress_thread.join(timeout=2)
            
            # Count unique tests
            test_names = set()
            for line in test_code.split('\n'):
                if line.strip().startswith('def test_'):
                    name = line.split('(')[0].replace('def ', '').strip()
                    test_names.add(name)
            
            self.unique_test_count = len(test_names)
            
            print(f"   ✅ Generated {self.unique_test_count} unique tests")
            
            # Send completion with count
            send_event('generate', {
                'progress': 100,
                'count': self.unique_test_count,
                'status': 'success',
                'message': f'✅ Generated {self.unique_test_count} tests successfully!'
            })
            
            return test_code
            
        except Exception as e:
            stop_progress.set()
            print(f"   ❌ Generation failed: {e}")
            send_event('generate', {
                'progress': 0,
                'count': 0,
                'status': 'failed',
                'message': f'Generation failed: {str(e)[:50]}'
            })
            raise
    
    def validate_code(self, test_code):
        """Validate generated code"""
        print("   🔍 Running validation checks...")
        
        result = CodeValidator.validate_all(test_code)
        
        # Extract individual results
        syntax_passed = result['results']['syntax'][0]
        imports_passed = result['results']['imports'][0]
        overall_passed = result['passed']
        
        print(f"      Syntax: {'✓' if syntax_passed else '✗'}")
        print(f"      Imports: {'✓' if imports_passed else '✗'}")
        print(f"      Overall: {'✓' if overall_passed else '✗'}")
        
        # Send validation event
        send_event('validate', {
            'syntax': syntax_passed,
            'imports': imports_passed,
            'overall': overall_passed,
            'message': 'Validation passed' if overall_passed else 'Validation failed'
        })
        
        if not overall_passed:
            raise Exception("Code validation failed")
        
        print("   ✅ Validation passed")
    
    def save_test_file(self, test_code, parsed_spec):
        """Save test file with deduplication"""
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
        
        # Update count
        self.unique_test_count = len(test_functions)
        
        print(f"   Deduplicated to {self.unique_test_count} unique tests")
        
        # Create file with template
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
    with requests.Session() as s:
        s.headers.update({{'Content-Type': 'application/json'}})
        yield s


@pytest.fixture(scope="session", autouse=True)
def check_api():
    try:
        r = requests.get(BASE_URL.replace('/api/v1', '/health'), timeout=3)
        assert r.status_code == 200
        print("\\n✅ API is accessible")
    except Exception as e:
        pytest.fail(f"❌ API not running: {{e}}")


'''
        
        # Add test functions
        for test_name in sorted(test_functions.keys()):
            final_code += '\n' + test_functions[test_name] + '\n'
        
        # Save file
        with open(self.test_file_path, 'w') as f:
            f.write(final_code)
        
        print(f"   ✅ Saved: {filename}")
    
    def run_tests_with_details(self):
        """Execute tests and capture detailed results"""
        print(f"   Running pytest: {self.test_file_path}")
        
        if not os.path.exists(self.test_file_path):
            print("   ❌ Test file not found")
            send_event('execute', {
                'passed': 0,
                'failed': 0,
                'total': self.unique_test_count,
                'details': []
            })
            return
        
        # Check API health
        try:
            r = requests.get('http://localhost:5001/health', timeout=3)
            if r.status_code != 200:
                raise Exception("API not healthy")
            print("   ✅ API is accessible")
        except Exception as e:
            print(f"   ❌ API not accessible: {e}")
            
            # Create failure details
            details = []
            for i in range(self.unique_test_count):
                details.append({
                    'name': f'test_{i+1}',
                    'passed': False,
                    'reason': f'❌ API not running: {str(e)}'
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
                ['pytest', self.test_file_path, '-v', '--tb=short'],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            output = result.stdout + '\n' + result.stderr
            
            # Parse results
            self.passed_tests = 0
            self.failed_tests = 0
            details = []
            
            lines = output.split('\n')
            
            for i, line in enumerate(lines):
                if '::test_' in line and (' PASSED' in line or ' FAILED' in line):
                    try:
                        parts = line.split('::')
                        if len(parts) >= 2:
                            test_name = parts[1].split()[0]
                            passed = 'PASSED' in line
                            
                            if passed:
                                self.passed_tests += 1
                                reason = '✅ Test passed'
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
                    
                    except Exception as e:
                        print(f"   ⚠️ Parse error: {e}")
            
            print(f"\n   Results: {self.passed_tests} passed, {self.failed_tests} failed / {self.unique_test_count} total")
            
            # Send results
            send_event('execute', {
                'passed': self.passed_tests,
                'failed': self.failed_tests,
                'total': self.unique_test_count,
                'details': details
            })
            
        except Exception as e:
            print(f"   ❌ Execution error: {e}")
            send_event('execute', {
                'passed': 0,
                'failed': self.unique_test_count,
                'total': self.unique_test_count,
                'details': []
            })
    
    def _extract_failure_reason(self, lines, start_idx):
        """Extract detailed failure reason from pytest output"""
        for i in range(start_idx + 1, min(start_idx + 20, len(lines))):
            line = lines[i].strip()
            
            if 'ConnectionError' in line or 'Connection refused' in line:
                return "❌ Cannot connect to API"
            if 'Timeout' in line:
                return "❌ API timeout"
            if 'assert' in line.lower() and ('==' in line or '!=' in line):
                clean = line.replace('E       ', '').replace('assert ', '')
                return f"❌ {clean[:100]}"
            if 'AssertionError' in line:
                return f"❌ Assertion failed: {line[:100]}"
            if 'KeyError' in line:
                return f"❌ Missing field: {line[:100]}"
        
        return "❌ Test failed"
    
    def run_contract_tests(self, parsed_spec):
        """Run contract tests"""
        print(f"   Testing {self.endpoint_count} endpoints...")
        
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
            
            print(f"   ✅ Results: {summary['passed']}/{summary['total']} passed")
            
            send_event('contract', {
                'total': summary['total'],
                'passed': summary['passed'],
                'failed': summary['failed'],
                'status': 'completed'
            })
        except Exception as e:
            print(f"   ❌ Contract testing error: {e}")
            send_event('contract', {
                'total': self.endpoint_count,
                'passed': 0,
                'failed': self.endpoint_count,
                'status': 'error'
            })
    
    def calculate_coverage_correctly(self):
        """Calculate coverage - PROPER METHOD"""
        print("   Analyzing code coverage...")
        
        try:
            project_root = os.path.dirname(os.path.abspath(__file__))
            api_path = os.path.join(project_root, 'api')
            
            # Verify API directory exists
            if not os.path.exists(api_path):
                print(f"   ⚠️ API directory not found: {api_path}")
                self.actual_coverage = 0
                send_event('coverage', {'percentage': 0})
                return
            
            # List API files
            api_files = [f for f in os.listdir(api_path) if f.endswith('.py') and f != '__init__.py']
            
            if not api_files:
                print(f"   ⚠️ No API files to measure coverage")
                self.actual_coverage = 0
                send_event('coverage', {'percentage': 0})
                return
            
            print(f"   API files: {api_files}")
            
            # Clean old coverage data
            coverage_file = os.path.join(project_root, '.coverage')
            if os.path.exists(coverage_file):
                os.remove(coverage_file)
            
            # Step 1: Run coverage
            print("   Running coverage analysis...")
            
            subprocess.run(
                ['coverage', 'run', '--source=api', '-m', 'pytest', self.test_file_path, '-q'],
                capture_output=True,
                timeout=60,
                cwd=project_root
            )
            
            # Step 2: Generate report
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
            print("   " + "="*60)
            
            # Step 3: Parse percentage
            coverage = 0
            for line in report_result.stdout.split('\n'):
                if 'TOTAL' in line:
                    parts = line.split()
                    try:
                        coverage_str = parts[-1].rstrip('%')
                        coverage = int(float(coverage_str))
                    except:
                        pass
                    break
            
            # Step 4: Generate HTML
            subprocess.run(
                ['coverage', 'html', '-d', 'htmlcov'],
                capture_output=True,
                cwd=project_root
            )
            
            htmlcov_path = os.path.join(project_root, 'htmlcov', 'index.html')
            if os.path.exists(htmlcov_path):
                print(f"   ✅ HTML report: {htmlcov_path}")
            
            self.actual_coverage = coverage
            print(f"\n   ✅ Final Coverage: {coverage}%")
            
            # Send coverage event
            send_event('coverage', {'percentage': coverage})
            
        except FileNotFoundError:
            print("   ❌ Coverage tool not installed")
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
        """Generate before/after comparison"""
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
        
        print("   ✅ Comparison generated")
        
        send_event('comparison', comparison)
    
    def git_commit_and_push(self):
        """Git operations"""
        try:
            result = subprocess.run(
                ['git', 'status', '--porcelain', self.test_file_path],
                capture_output=True,
                text=True
            )
            
            if not result.stdout.strip():
                print("   ℹ️ No changes to commit")
                send_event('git', {
                    'committed': False,
                    'pushed': False,
                    'message': 'No changes'
                })
                return
            
            # Stage and commit
            subprocess.run(['git', 'add', self.test_file_path], check=True)
            
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            subprocess.run(
                ['git', 'commit', '-m', f'🤖 AI tests v{self.version} - {timestamp}', '--no-verify'],
                capture_output=True,
                check=True
            )
            
            result = subprocess.run(
                ['git', 'rev-parse', '--short', 'HEAD'],
                capture_output=True,
                text=True
            )
            commit_hash = result.stdout.strip()
            
            print(f"   ✅ Committed: {commit_hash}")
            
            send_event('git', {
                'committed': True,
                'pushed': False,
                'message': f'Committed ({commit_hash})'
            })
            
            # Push
            result = subprocess.run(
                ['git', 'branch', '--show-current'],
                capture_output=True,
                text=True
            )
            branch = result.stdout.strip() or 'main'
            
            result = subprocess.run(['git', 'remote'], capture_output=True, text=True)
            
            if 'origin' in result.stdout:
                print(f"   🚀 Pushing to origin/{branch}...")
                
                push_result = subprocess.run(
                    ['git', 'push', 'origin', branch],
                    capture_output=True,
                    timeout=30
                )
                
                if push_result.returncode == 0:
                    print(f"   ✅ Pushed successfully")
                    
                    send_event('git', {
                        'committed': True,
                        'pushed': True,
                        'message': f'Pushed to {branch}'
                    })
                    
                    send_event('cicd', {
                        'status': 'triggered',
                        'message': 'CI/CD pipeline triggered',
                        'build': 'View on GitHub Actions'
                    })
                else:
                    print(f"   ⚠️ Push failed")
                    send_event('git', {
                        'committed': True,
                        'pushed': False,
                        'message': 'Push failed'
                    })
            else:
                print("   ℹ️ No remote configured")
                send_event('git', {
                    'committed': True,
                    'pushed': False,
                    'message': 'No remote'
                })
        
        except Exception as e:
            print(f"   ❌ Git error: {e}")
            send_event('git', {
                'committed': False,
                'pushed': False,
                'message': f'Error: {str(e)[:50]}'
            })
    
    def print_summary(self):
        """Print final summary"""
        duration = (datetime.now() - self.start_time).total_seconds()
        
        print("\n" + "="*70)
        print("✅ POC COMPLETED SUCCESSFULLY")
        print("="*70)
        print(f"   Duration:    {duration:.1f}s")
        print(f"   Endpoints:   {self.endpoint_count}")
        print(f"   Tests:       {self.unique_test_count}")
        print(f"   Passed:      {self.passed_tests}")
        print(f"   Failed:      {self.failed_tests}")
        print(f"   Coverage:    {self.actual_coverage}%")
        print("="*70)
        print(f"\n🌐 Dashboard: http://localhost:8080")
        print(f"📄 Coverage:  http://localhost:8080/coverage-report")
        print(f"🔬 Tests:     http://localhost:8080/generated-tests\n")


def main():
    """Main entry point"""
    try:
        orchestrator = POCOrchestrator(spec_path='specs/aadhaar-api.yaml')
        orchestrator.run()
        sys.exit(0)
    except KeyboardInterrupt:
        print("\n\n⚠️ Interrupted by user\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}\n")
        sys.exit(1)


if __name__ == '__main__':
    main()