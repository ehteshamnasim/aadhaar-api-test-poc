#!/usr/bin/env python3
"""
AI-Powered API Test Automation POC
Main orchestrator - Auto-triggered by Git hooks
"""

import os
import sys
import time
import threading
import subprocess
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from parser import OpenAPIParser
from test_generator import TestGenerator
from contract_tester import ContractTester
from validator import CodeValidator
from git_committer import GitCommitter

# Event sending configuration
import requests
import json as json_module

DASHBOARD_URL = "http://localhost:8080"
MAX_EVENT_RETRIES = 5
EVENT_RETRY_DELAY = 1

def send_event(event_type: str, data: dict):
    """Send event to dashboard with aggressive retry"""
    payload = {'type': event_type, **data}
    
    for attempt in range(MAX_EVENT_RETRIES):
        try:
            response = requests.post(
                f"{DASHBOARD_URL}/api/event",
                json=payload,
                timeout=3,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                print(f"  ✓ Event: {event_type}")
                return True
            else:
                print(f"  ⚠️ Event failed (HTTP {response.status_code}): {event_type}")
                
        except requests.exceptions.ConnectionError:
            if attempt == 0:
                print(f"  ⏳ Dashboard connecting... (attempt {attempt + 1}/{MAX_EVENT_RETRIES})")
            time.sleep(EVENT_RETRY_DELAY)
            continue
            
        except Exception as e:
            print(f"  ❌ Event error: {e}")
            break
    
    print(f"  ❌ Event failed after {MAX_EVENT_RETRIES} attempts: {event_type}")
    return False

def wait_for_dashboard(max_wait=30):
    """Wait for dashboard to be ready"""
    print("\n⏳ Waiting for dashboard...")
    
    for i in range(max_wait):
        try:
            response = requests.get(f"{DASHBOARD_URL}/api/health", timeout=2)
            if response.status_code == 200:
                print("✅ Dashboard ready\n")
                # Send initial event to confirm connection
                send_event('status', {'message': 'POC initializing...'})
                return True
        except:
            pass
        
        if i % 5 == 0 and i > 0:
            print(f"  Still waiting... ({i}s)")
        
        time.sleep(1)
    
    print("⚠️  Dashboard timeout (continuing anyway)\n")
    return False


class POCOrchestrator:
    """Main POC orchestrator"""
    
    def __init__(self, spec_path: str, output_dir: str = 'tests'):
        self.spec_path = spec_path
        self.output_dir = output_dir
        self.test_file_path = None
        self.start_time = datetime.now()
        
        Path(output_dir).mkdir(exist_ok=True)
    
    def run(self):
        """Run complete POC pipeline"""
        print("\n" + "="*70)
        print("🚀 AI-Powered API Test Automation POC")
        print(f"   Started: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70 + "\n")
        
        # CRITICAL: Wait for dashboard
        dashboard_ready = wait_for_dashboard(max_wait=15)
        
        if not dashboard_ready:
            print("⚠️  WARNING: Dashboard may not show updates\n")
        
        try:
            # Initial status
            send_event('status', {'message': '🚀 POC Started'})
            time.sleep(0.5)  # Give time for event to process
            
            # Step 1: Parse spec
            send_event('status', {'message': 'Parsing OpenAPI specification...'})
            parsed_spec = self.parse_spec()
            time.sleep(0.3)
            
            # Step 2: Contract tests
            send_event('status', {'message': 'Running contract tests...'})
            self.run_contract_tests(parsed_spec)
            time.sleep(0.3)
            
            # Step 3: Generate tests
            send_event('status', {'message': 'Generating tests with AI...'})
            test_code = self.generate_tests(parsed_spec)
            time.sleep(0.3)
            
            # Step 4: Validate
            send_event('status', {'message': 'Validating generated code...'})
            self.validate_code(test_code)
            time.sleep(0.3)
            
            # Step 5: Save
            send_event('status', {'message': 'Saving test file...'})
            self.save_test_file(test_code)
            time.sleep(0.3)
            
            # Step 6: Run tests
            send_event('status', {'message': 'Executing tests...'})
            self.run_tests()
            time.sleep(0.3)
            
            # Step 7: Coverage
            send_event('status', {'message': 'Calculating coverage...'})
            self.calculate_coverage()
            time.sleep(0.3)

            self.show_comparison()
            time.sleep(0.1)

            
            # Step 8: Git commit
            send_event('status', {'message': 'Committing to Git...'})
            self.git_commit()
            time.sleep(0.3)
            
            # Final status
            duration = (datetime.now() - self.start_time).total_seconds()
            send_event('status', {'message': f'✅ POC completed in {duration:.1f}s'})
            
            print("\n" + "="*70)
            print("✅ POC COMPLETED")
            print(f"   Duration: {duration:.1f}s")
            print("="*70)
            print(f"\n📊 Dashboard: http://localhost:8080")
            print(f"📝 Tests: {self.test_file_path}")
            print(f"📈 Coverage: htmlcov/index.html\n")
            
        except Exception as e:
            send_event('error', {'message': str(e)})
            print(f"\n❌ Error: {str(e)}\n")
            import traceback
            traceback.print_exc()
            raise
    
    def parse_spec(self) -> dict:
        """Parse OpenAPI specification"""
        print("📄 Parsing spec...")
        parser = OpenAPIParser(self.spec_path)
        parsed = parser.to_dict()
        
        endpoint_count = len(parsed['endpoints'])
        print(f"   Found {endpoint_count} endpoints")
        
        send_event('parse', {
            'file': 'specs/aadhaar-api.yaml',
            'endpoints': endpoint_count
        })
        
        return parsed
    
    def run_contract_tests(self, parsed_spec: dict):
        """Run contract tests"""
        print("\n🔍 Contract testing...")
        
        total = len(parsed_spec['endpoints'])
        send_event('contract', {
            'total': total,
            'passed': 0,
            'failed': 0
        })
        
        tester = ContractTester(parsed_spec['base_url'])
        results = tester.test_contracts(parsed_spec['endpoints'])
        summary = tester.get_summary()
        
        print(f"   Results: {summary['passed']}/{summary['total']} passed")
        
        send_event('contract', {
            'total': summary['total'],
            'passed': summary['passed'],
            'failed': summary['failed']
        })
    
    def generate_tests(self, parsed_spec: dict) -> str:
        """Generate tests"""
        print("\n🤖 Generating tests...")
        
        generator = TestGenerator()
        
        if not generator.check_ollama_status():
            raise Exception("Ollama not running")
        
        if not generator.check_model_exists():
            raise Exception("llama3:70b not found")
        
        send_event('generate', {
            'progress': 30,
            'count': 0,
            'status': 'in_progress',
            'message': 'Sending to LLM...'
        })
        
        # Progress thread
        stop_progress = threading.Event()
        
        def send_progress():
            progress = 40
            while not stop_progress.is_set() and progress < 90:
                time.sleep(10)
                if not stop_progress.is_set():
                    send_event('generate', {
                        'progress': progress,
                        'count': 0,
                        'status': 'in_progress',
                        'message': f'LLM processing... ({progress}%)'
                    })
                    progress += 10
        
        progress_thread = threading.Thread(target=send_progress, daemon=True)
        progress_thread.start()
        
        try:
            test_code = generator.generate_tests(parsed_spec)
            stop_progress.set()
            progress_thread.join(timeout=1)
            
            test_count = test_code.count('def test_')
            print(f"   Generated {test_count} tests")
            
            send_event('generate', {
                'progress': 100,
                'count': test_count,
                'status': 'success',
                'message': f'Generated {test_count} tests'
            })
            
            return test_code
            
        except Exception as e:
            stop_progress.set()
            raise
    
    def validate_code(self, test_code: str):
        """Validate code"""
        print("\n✓ Validating...")
        result = CodeValidator.validate_all(test_code)
        
        send_event('validate', {
            'syntax': result['results']['syntax'][0],
            'imports': result['results']['imports'][0],
            'overall': result['passed'],
            'message': 'Validation passed' if result['passed'] else 'Validation failed'
        })
        
        if not result['passed']:
            raise Exception("Validation failed")
        
        print("   ✅ Validation passed")
    
    def save_test_file(self, test_code: str):
        """Save test file"""
        self.test_file_path = os.path.join(self.output_dir, 'test_aadhaar_api.py')
        
        with open(self.test_file_path, 'w') as f:
            f.write(test_code)
        
        print(f"\n💾 Saved: {self.test_file_path}")
    
    def run_tests(self):
        """Run tests"""
        print("\n🧪 Running tests...")
        
        try:
            result = subprocess.run(
                ['pytest', self.test_file_path, '-v'],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            output = result.stdout
            passed = output.count(' PASSED')
            failed = output.count(' FAILED')
            total = passed + failed
            
            print(f"   {passed}/{total} passed")
            
            send_event('execute', {
                'passed': passed,
                'failed': failed,
                'total': total
            })
            
        except Exception as e:
            print(f"   ⚠️ Error: {e}")
            send_event('execute', {'passed': 0, 'failed': 0, 'total': 0})
    
    def calculate_coverage(self):
        """Calculate coverage"""
        print("\n📊 Coverage...")
        
        try:
            subprocess.run(
                ['coverage', 'run', '-m', 'pytest', self.test_file_path],
                capture_output=True,
                timeout=60
            )
            
            result = subprocess.run(
                ['coverage', 'report'],
                capture_output=True,
                text=True
            )
            
            output = result.stdout
            if 'TOTAL' in output:
                for line in output.split('\n'):
                    if 'TOTAL' in line:
                        parts = line.split()
                        coverage_str = parts[-1].rstrip('%')
                        coverage = int(coverage_str) if coverage_str.isdigit() else 0
                        print(f"   {coverage}%")
                        
                        send_event('coverage', {'percentage': coverage})
                        break
            
            subprocess.run(['coverage', 'html'], capture_output=True)
            
        except Exception as e:
            print(f"   ⚠️ Error: {e}")
            send_event('coverage', {'percentage': 0})
    
    

    def git_commit(self):
        """Git commit and push"""
        print("\n📝 Committing to Git...")
        
        try:
            # Check if file changed
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
            
            print(f"   Changes detected in {self.test_file_path}")
            
            # Add file
            subprocess.run(['git', 'add', self.test_file_path], check=True)
            print("   ✓ Staged for commit")
            
            # Commit
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            commit_msg = f"🤖 AI-generated tests - {timestamp}"
            
            subprocess.run(
                ['git', 'commit', '-m', commit_msg, '--no-verify'],
                capture_output=True,
                text=True,
                check=True
            )
            
            # Get commit hash
            result = subprocess.run(
                ['git', 'rev-parse', '--short', 'HEAD'],
                capture_output=True,
                text=True
            )
            commit_hash = result.stdout.strip()
            print(f"   ✓ Committed: {commit_hash}")
            
            send_event('git', {
                'committed': True,
                'pushed': False,
                'message': f'Committed ({commit_hash})'
            })
            
            # Auto-push
            print("   🚀 Pushing to remote...")
            send_event('status', {'message': 'Pushing to remote...'})
            
            # Get current branch
            result = subprocess.run(
                ['git', 'branch', '--show-current'],
                capture_output=True,
                text=True
            )
            branch = result.stdout.strip() or 'main'
            
            # Check if remote exists
            result = subprocess.run(
                ['git', 'remote'],
                capture_output=True,
                text=True
            )
            
            if 'origin' in result.stdout:
                # Push to remote
                push_result = subprocess.run(
                    ['git', 'push', 'origin', branch],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if push_result.returncode == 0:
                    print(f"   ✓ Pushed to origin/{branch}")
                    send_event('git', {
                        'committed': True,
                        'pushed': True,
                        'message': f'Pushed to origin/{branch}'
                    })
                    
                    send_event('cicd', {
                        'status': 'triggered',
                        'message': 'CI/CD pipeline triggered',
                        'build': 'Starting...'
                    })
                else:
                    error_msg = push_result.stderr.strip()
                    print(f"   ⚠️ Push failed: {error_msg}")
                    send_event('git', {
                        'committed': True,
                        'pushed': False,
                        'message': f'Push failed: {error_msg[:50]}'
                    })
            else:
                print("   ℹ️ No remote configured, skipping push")
                send_event('git', {
                    'committed': True,
                    'pushed': False,
                    'message': 'No remote configured'
                })
            
        except subprocess.TimeoutExpired:
            print("   ⚠️ Push timeout (30s)")
            send_event('git', {
                'committed': True,
                'pushed': False,
                'message': 'Push timeout'
            })
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Git error: {e.stderr if e.stderr else str(e)}")
            send_event('git', {
                'committed': False,
                'pushed': False,
                'message': 'Commit/push failed'
            })
        except Exception as e:
            print(f"   ❌ Error: {e}")
            send_event('git', {
                'committed': False,
                'pushed': False,
                'message': str(e)
            })

    def show_comparison(self):
        """Show before/after comparison"""
        print("\n📊 Test Generation Summary")
        print("=" * 50)
        
        # Count endpoints
        parser = OpenAPIParser(self.spec_path)
        endpoints = len(parser.get_endpoints())
        
        # Count generated tests
        if self.test_file_path and os.path.exists(self.test_file_path):
            with open(self.test_file_path, 'r') as f:
                content = f.read()
                test_count = content.count('def test_')
                lines = len(content.split('\n'))
        else:
            test_count = 0
            lines = 0
        
        comparison = {
            'before': {
                'manual_effort': f'{endpoints * 30} minutes',
                'test_files': 0,
                'test_cases': 0,
                'coverage': '0%'
            },
            'after': {
                'ai_time': f'{(datetime.now() - self.start_time).seconds} seconds',
                'test_files': 1,
                'test_cases': test_count,
                'lines_of_code': lines,
                'coverage': 'Calculated'
            }
        }
        
        print("\n📉 Before AI:")
        print(f"   Manual effort: {comparison['before']['manual_effort']}")
        print(f"   Test coverage: {comparison['before']['coverage']}")
        
        print("\n📈 After AI:")
        print(f"   Generation time: {comparison['after']['ai_time']}")
        print(f"   Test cases: {comparison['after']['test_cases']}")
        print(f"   Lines of code: {comparison['after']['lines_of_code']}")
        
        # Send to dashboard
        send_event('comparison', comparison)

    def run_with_retry(self, max_retries=2):
        """Run POC with retry on failure"""
        for attempt in range(max_retries + 1):
            try:
                if attempt > 0:
                    print(f"\n🔄 Retry attempt {attempt}/{max_retries}")
                    send_event('status', {'message': f'Retrying... (attempt {attempt})'})
                    time.sleep(5)  # Wait before retry
                
                self.run()
                return True  # Success
                
            except Exception as e:
                if attempt < max_retries:
                    print(f"   ⚠️ Attempt {attempt + 1} failed: {e}")
                    send_event('status', {'message': f'Attempt {attempt + 1} failed, retrying...'})
                else:
                    print(f"   ❌ All attempts failed")
                    send_event('error', {'message': f'Failed after {max_retries + 1} attempts'})
                    raise
        
        return False



def main():
    """Main entry point"""
    orchestrator = POCOrchestrator(spec_path='specs/aadhaar-api.yaml')
    
    success = orchestrator.run_with_retry(max_retries=2)
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()