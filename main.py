#!/usr/bin/env python3
"""
AI-Powered API Test Automation POC
Main orchestrator script - Auto-triggered by Git hooks
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

# Import dashboard server
sys.path.insert(0, str(Path(__file__).parent / 'dashboard'))
from server import start_dashboard_server, send_event

class POCOrchestrator:
    """Main orchestrator for POC"""
    
    def __init__(self, spec_path: str, output_dir: str = 'tests'):
        self.spec_path = spec_path
        self.output_dir = output_dir
        self.test_file_path = None
        self.start_time = datetime.now()
        
        # Create output directory
        Path(output_dir).mkdir(exist_ok=True)
    
    def run(self):
        """Run complete POC pipeline"""
        print("\n" + "="*70)
        print("🚀 AI-Powered API Test Automation POC")
        print(f"   Triggered at: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70 + "\n")
        
        try:
            # Step 0: Check what triggered this
            self.check_trigger_reason()
            
            # Step 1: Parse OpenAPI spec
            send_event('status', {'message': 'Parsing OpenAPI specification...'})
            parsed_spec = self.parse_spec()
            
            # Step 2: Run contract tests
            send_event('status', {'message': 'Running contract tests...'})
            self.run_contract_tests(parsed_spec)
            
            # Step 3: Generate tests
            send_event('status', {'message': 'Generating tests with AI...'})
            test_code = self.generate_tests(parsed_spec)
            
            # Step 4: Validate generated code
            send_event('status', {'message': 'Validating generated code...'})
            self.validate_code(test_code)
            
            # Step 5: Save test file
            send_event('status', {'message': 'Saving test file...'})
            self.save_test_file(test_code)
            
            # Step 6: Run tests
            send_event('status', {'message': 'Executing tests...'})
            self.run_tests()
            
            # Step 7: Calculate coverage
            send_event('status', {'message': 'Calculating coverage...'})
            self.calculate_coverage()
            
            # Step 8: Git commit (only if tests changed)
            send_event('status', {'message': 'Committing to Git...'})
            self.git_commit()
            
            # Step 9: Final status
            duration = (datetime.now() - self.start_time).total_seconds()
            send_event('status', {'message': f'✅ POC completed in {duration:.1f}s!'})
            
            print("\n" + "="*70)
            print("✅ POC COMPLETED SUCCESSFULLY!")
            print(f"   Duration: {duration:.1f} seconds")
            print("="*70)
            print(f"\n📊 Dashboard: http://localhost:8080")
            print(f"📝 Generated tests: {self.test_file_path}")
            print(f"📈 Coverage report: htmlcov/index.html")
            print(f"📋 Full log: poc_output.log\n")
            
        except Exception as e:
            send_event('error', {'message': str(e)})
            print(f"\n❌ Error: {str(e)}\n")
            import traceback
            traceback.print_exc()
            raise
    
    def check_trigger_reason(self):
        """Check what triggered this run"""
        try:
            # Get last commit message
            result = subprocess.run(
                ['git', 'log', '-1', '--pretty=%B'],
                capture_output=True,
                text=True
            )
            last_commit_msg = result.stdout.strip()
            
            # Get changed files in last commit
            result = subprocess.run(
                ['git', 'diff-tree', '--no-commit-id', '--name-only', '-r', 'HEAD'],
                capture_output=True,
                text=True
            )
            changed_files = result.stdout.strip().split('\n')
            
            print("📌 Trigger Information:")
            print(f"   Last commit: {last_commit_msg}")
            print(f"   Changed files: {', '.join(changed_files)}")
            print()
            
            # Check if spec was changed
            spec_changed = any('specs/' in f for f in changed_files)
            if spec_changed:
                print("✅ API specification changed - generating new tests")
            else:
                print("ℹ️  Manual run - regenerating tests anyway")
            print()
            
        except Exception as e:
            print(f"⚠️  Could not determine trigger reason: {e}")
            print()
    
    def parse_spec(self) -> dict:
        """Parse OpenAPI specification"""
        print("📄 Parsing OpenAPI specification...")
        parser = OpenAPIParser(self.spec_path)
        parsed = parser.to_dict()
        
        endpoint_count = len(parsed['endpoints'])
        print(f"   Found {endpoint_count} endpoints")
        
        send_event('parse', {
            'file': self.spec_path,
            'endpoints': endpoint_count
        })
        
        return parsed
    
    def run_contract_tests(self, parsed_spec: dict):
        """Run contract tests"""
        print("\n🔍 Running contract tests...")
        tester = ContractTester(parsed_spec['base_url'])
        results = tester.test_contracts(parsed_spec['endpoints'])
        summary = tester.get_summary()
        
        print(f"   Contract tests: {summary['passed']}/{summary['total']} passed")
        
        send_event('contract', {
            'total': summary['total'],
            'passed': summary['passed'],
            'failed': summary['failed']
        })
    
    def generate_tests(self, parsed_spec: dict) -> str:
        """Generate tests using Ollama LLM"""
        print("\n🤖 Generating tests with Ollama Llama3:70b...")
        
        # Check Ollama first
        generator = TestGenerator()
        
        if not generator.check_ollama_status():
            raise Exception("Ollama is not running. Start it with: ollama serve")
        
        if not generator.check_model_exists():
            raise Exception("llama3:70b model not found. Pull it with: ollama pull llama3:70b")
        
        send_event('generate', {
            'progress': 30,
            'count': 0,
            'status': 'in_progress',
            'message': 'Sending request to Ollama LLM...'
        })
        
        test_code = generator.generate_tests(parsed_spec)
        
        # Count test functions
        test_count = test_code.count('def test_')
        print(f"   Generated {test_count} test functions")
        
        send_event('generate', {
            'progress': 100,
            'count': test_count,
            'status': 'success',
            'message': f'Generated {test_count} tests'
        })
        
        return test_code
    
    def validate_code(self, test_code: str):
        """Validate generated code"""
        print("\n✓ Validating generated code...")
        result = CodeValidator.validate_all(test_code)
        
        if result['passed']:
            print("   ✅ All validations passed")
        else:
            print("   ❌ Validation failed:")
            for check, (passed, msg) in result['results'].items():
                if not passed:
                    print(f"      {check}: {msg}")
        
        send_event('validate', {
            'syntax': result['results']['syntax'][0],
            'imports': result['results']['imports'][0],
            'overall': result['passed'],
            'message': 'Validation passed' if result['passed'] else 'Validation failed'
        })
        
        if not result['passed']:
            raise Exception("Code validation failed")
    
    def save_test_file(self, test_code: str):
        """Save test file"""
        self.test_file_path = os.path.join(self.output_dir, 'test_aadhaar_api.py')
        
        with open(self.test_file_path, 'w') as f:
            f.write(test_code)
        
        print(f"\n💾 Test file saved: {self.test_file_path}")
    
    def run_tests(self):
        """Execute pytest tests"""
        print("\n🧪 Running tests...")
        
        try:
            result = subprocess.run(
                ['pytest', self.test_file_path, '-v', '--tb=short'],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            # Parse pytest output
            output = result.stdout
            passed = output.count(' PASSED')
            failed = output.count(' FAILED')
            total = passed + failed
            
            print(f"   Tests: {passed}/{total} passed")
            if failed > 0:
                print(f"   ⚠️  {failed} test(s) failed - check output for details")
            
            send_event('execute', {
                'passed': passed,
                'failed': failed,
                'total': total
            })
            
        except Exception as e:
            print(f"   ⚠️ Test execution error: {str(e)}")
            send_event('execute', {
                'passed': 0,
                'failed': 0,
                'total': 0
            })
    
    def calculate_coverage(self):
        """Calculate code coverage"""
        print("\n📊 Calculating coverage...")
        
        try:
            # Run coverage
            subprocess.run(
                ['coverage', 'run', '-m', 'pytest', self.test_file_path],
                capture_output=True,
                timeout=60
            )
            
            # Generate report
            result = subprocess.run(
                ['coverage', 'report'],
                capture_output=True,
                text=True
            )
            
            # Parse coverage percentage
            output = result.stdout
            if 'TOTAL' in output:
                lines = output.split('\n')
                for line in lines:
                    if 'TOTAL' in line:
                        parts = line.split()
                        coverage_str = parts[-1].rstrip('%')
                        coverage = int(coverage_str) if coverage_str.isdigit() else 0
                        print(f"   Coverage: {coverage}%")
                        
                        send_event('coverage', {'percentage': coverage})
                        break
            
            # Generate HTML report
            subprocess.run(['coverage', 'html'], capture_output=True)
            print("   HTML report: htmlcov/index.html")
            
        except Exception as e:
            print(f"   ⚠️ Coverage calculation error: {str(e)}")
            send_event('coverage', {'percentage': 0})
    
    def git_commit(self):
        """Commit to Git"""
        print("\n📝 Committing to Git...")
        
        # Check if test file actually changed
        try:
            result = subprocess.run(
                ['git', 'diff', '--quiet', self.test_file_path],
                capture_output=True
            )
            
            if result.returncode == 0:
                print("   ℹ️  No changes to commit (tests unchanged)")
                send_event('git', {
                    'committed': False,
                    'message': 'No changes to commit'
                })
                return
        except:
            pass
        
        results = GitCommitter.auto_commit_tests(self.test_file_path)
        
        committed = 'commit' in results and results['commit'][0]
        
        send_event('git', {
            'committed': committed,
            'message': 'Tests committed to Git' if committed else 'Git commit skipped'
        })

def main():
    """Main entry point"""
    
    # Check if running from Git hook or manually
    is_hook_triggered = os.getenv('GIT_DIR') is not None or len(sys.argv) > 1 and sys.argv[1] == '--hook'
    
    if is_hook_triggered:
        print("🔔 Triggered by Git commit hook")
    else:
        print("🖱️  Manually triggered")
    
    # Start dashboard server in background
    dashboard_thread = threading.Thread(target=start_dashboard_server, daemon=True)
    dashboard_thread.start()
    
    # Wait for server to start
    time.sleep(2)
    
    if not is_hook_triggered:
        print("\n📊 Dashboard started at: http://localhost:8080")
        print("    (Open in your browser to see real-time updates)\n")
        time.sleep(2)
    
    # Run POC
    orchestrator = POCOrchestrator(spec_path='specs/aadhaar-api.yaml')
    orchestrator.run()
    
    # If triggered by hook, exit immediately
    if is_hook_triggered:
        print("\n✅ Background processing complete")
        sys.exit(0)
    
    # If manual run, keep dashboard running
    print("\n⏳ Dashboard server running. Press Ctrl+C to stop.\n")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down...\n")

if __name__ == '__main__':
    main()