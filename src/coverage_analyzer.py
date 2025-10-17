"""
Coverage Analyzer - Identifies missing coverage and generates targeted test suggestions
"""

import json
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple

class CoverageAnalyzer:
    """
    Analyzes code coverage and generates targeted prompts for missing coverage
    """
    
    def __init__(self, source_file: str = "api/dummy_aadhaar_api.py"):
        self.source_file = source_file
        self.coverage_data = None
        self.missing_lines = []
        self.source_code = self._read_source()
    
    def _read_source(self) -> List[str]:
        """
        Read source code file line by line
        
        Returns:
            List of source code lines
        """
        try:
            with open(self.source_file, 'r') as f:
                return f.readlines()
        except FileNotFoundError:
            return []
    
    def run_coverage_analysis(self, test_file: str) -> Tuple[float, List[int]]:
        """
        Run coverage analysis on test file
        
        Parameters:
            test_file: Path to test file to analyze
        
        Returns:
            Tuple of (coverage_percentage, list_of_missing_line_numbers)
        """
        try:
            # Run pytest with coverage
            result = subprocess.run(
                [
                    'pytest', test_file,
                    '--cov=api',
                    '--cov-report=json',
                    '--cov-report=term-missing',
                    '-q'
                ],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            # Read coverage JSON
            coverage_json_path = Path('coverage.json')
            if coverage_json_path.exists():
                with open(coverage_json_path, 'r') as f:
                    self.coverage_data = json.load(f)
                
                # Extract missing lines
                files_data = self.coverage_data.get('files', {})
                for file_path, file_data in files_data.items():
                    if self.source_file in file_path:
                        self.missing_lines = file_data.get('missing_lines', [])
                        total_lines = len(file_data.get('executed_lines', [])) + len(self.missing_lines)
                        executed_lines = len(file_data.get('executed_lines', []))
                        coverage_pct = (executed_lines / total_lines * 100) if total_lines > 0 else 0
                        
                        return coverage_pct, self.missing_lines
            
            return 0.0, []
            
        except Exception as e:
            print(f"Coverage analysis error: {e}")
            return 0.0, []
    
    def get_missing_code_context(self, line_num: int, context_lines: int = 3) -> Dict:
        """
        Get code context around a missing line
        
        Parameters:
            line_num: Line number to get context for
            context_lines: Number of lines before/after to include
        
        Returns:
            Dictionary with line context information
        """
        if not self.source_code or line_num < 1 or line_num > len(self.source_code):
            return {}
        
        start = max(0, line_num - context_lines - 1)
        end = min(len(self.source_code), line_num + context_lines)
        
        context = {
            'line_number': line_num,
            'line_content': self.source_code[line_num - 1].strip(),
            'context_before': [
                {'num': i + 1, 'code': self.source_code[i].strip()}
                for i in range(start, line_num - 1)
            ],
            'context_after': [
                {'num': i + 1, 'code': self.source_code[i].strip()}
                for i in range(line_num, end)
            ]
        }
        
        return context
    
    def identify_error_paths(self) -> List[Dict]:
        """
        Identify error handling paths that are not covered
        
        Returns:
            List of dictionaries describing uncovered error paths
        """
        error_paths = []
        
        for line_num in self.missing_lines:
            context = self.get_missing_code_context(line_num)
            if not context:
                continue
            
            line_content = context['line_content'].lower()
            
            # Categorize error type
            error_type = "unknown"
            test_suggestion = ""
            
            if 'missing' in line_content or 'required' in line_content:
                error_type = "missing_parameter"
                test_suggestion = "Test with missing required parameters"
            
            elif 'invalid' in line_content or 'format' in line_content:
                error_type = "invalid_format"
                test_suggestion = "Test with invalid data formats (too short, too long, invalid characters)"
            
            elif 'not found' in line_content or '404' in line_content:
                error_type = "not_found"
                test_suggestion = "Test with non-existent resources"
            
            elif 'consent' in line_content:
                error_type = "consent_error"
                test_suggestion = "Test with missing consent or consent=false"
            
            elif 'expired' in line_content:
                error_type = "expired_resource"
                test_suggestion = "Test with expired transactions or tokens"
            
            elif 'return' in line_content and ('error' in line_content or '400' in line_content or '404' in line_content):
                error_type = "error_response"
                test_suggestion = "Test to trigger this specific error response"
            
            error_paths.append({
                'line_number': line_num,
                'line_content': context['line_content'],
                'error_type': error_type,
                'test_suggestion': test_suggestion,
                'context': context
            })
        
        return error_paths
    
    def generate_targeted_prompt(self, error_paths: List[Dict], existing_tests: str) -> str:
        """
        Generate targeted prompt for LLM to cover missing lines
        
        Parameters:
            error_paths: List of uncovered error paths from identify_error_paths()
            existing_tests: Existing test code to avoid duplication
        
        Returns:
            Targeted prompt string for LLM
        """
        if not error_paths:
            return ""
        
        prompt = f"""You are an expert test engineer. The current test suite has {len(error_paths)} uncovered code paths. Generate ADDITIONAL pytest test cases to cover these specific missing lines.

CURRENT COVERAGE GAPS:

"""
        
        for i, path in enumerate(error_paths, 1):
            prompt += f"\n{i}. Line {path['line_number']}: {path['line_content']}\n"
            prompt += f"   Type: {path['error_type']}\n"
            prompt += f"   Required: {path['test_suggestion']}\n"
        
        prompt += f"""

REQUIREMENTS:
- Generate NEW test functions that specifically target the above missing lines
- Use Flask test client: client = app.test_client()
- Import: from api.dummy_aadhaar_api import app
- Use pytest fixtures
- Do NOT duplicate existing tests
- Focus on error cases and edge cases shown above
- Include clear docstrings explaining what line/path is being covered

EXISTING TESTS (do not duplicate):
```python
{existing_tests[:500]}  # Showing first 500 chars for reference
...
```

Generate ONLY the NEW test functions needed to cover the missing lines. Start with:

```python
# Additional tests to improve coverage

def test_...
```
"""
        
        return prompt
    
    def get_coverage_summary(self, coverage_pct: float, missing_count: int) -> str:
        """
        Generate human-readable coverage summary
        
        Parameters:
            coverage_pct: Coverage percentage
            missing_count: Number of missing lines
        
        Returns:
            Formatted summary string
        """
        status = "Excellent" if coverage_pct >= 95 else "Good" if coverage_pct >= 80 else "Needs Improvement"
        
        summary = f"""
Coverage Analysis Summary:
--------------------------
Coverage: {coverage_pct:.1f}%
Status: {status}
Missing Lines: {missing_count}

"""
        
        if missing_count > 0:
            summary += "Missing line numbers: " + ", ".join(str(line) for line in self.missing_lines[:10])
            if missing_count > 10:
                summary += f" ... and {missing_count - 10} more"
        
        return summary


if __name__ == '__main__':
    # Test the analyzer
    analyzer = CoverageAnalyzer()
    
    print("Running coverage analysis...")
    coverage_pct, missing_lines = analyzer.run_coverage_analysis('tests/test_aadhaar_api.py')
    
    print(analyzer.get_coverage_summary(coverage_pct, len(missing_lines)))
    
    if missing_lines:
        print("\nIdentifying error paths...")
        error_paths = analyzer.identify_error_paths()
        
        for path in error_paths:
            print(f"\nLine {path['line_number']}: {path['line_content']}")
            print(f"  Type: {path['error_type']}")
            print(f"  Suggestion: {path['test_suggestion']}")
