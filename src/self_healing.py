"""
Self-Healing Test System
Automatically repairs broken tests when APIs change
"""

import ast
import json
import difflib
import requests
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from pathlib import Path


class SelfHealingEngine:
    """
    AI-powered test repair engine that automatically fixes broken tests
    """
    
    def __init__(self, ollama_url: str = "http://localhost:11434"):
        """
        Initialize self-healing engine
        
        Args:
            ollama_url: Ollama server URL for AI-powered repairs
        """
        self.ollama_url = ollama_url
        self.model = "qwen2.5-coder:14b"
        self.healing_history = []
        self.confidence_threshold = 0.75
        
    def analyze_test_failure(self, test_name: str, error_message: str, 
                           test_code: str, api_response: Dict = None) -> Dict:
        """
        Analyze why a test failed and determine if it can be auto-healed
        
        Args:
            test_name: Name of the failed test
            error_message: Pytest error message
            test_code: The actual test code
            api_response: Actual API response if available
            
        Returns:
            Analysis results with healable status and suggested fixes
        """
        analysis = {
            'test_name': test_name,
            'failure_type': self._classify_failure(error_message),
            'healable': False,
            'confidence': 0.0,
            'suggested_fix': None,
            'reason': '',
            'api_change_detected': False
        }
        
        # Detect common healable failures
        if 'AssertionError' in error_message:
            if 'status_code' in error_message or 'status code' in error_message.lower():
                analysis['healable'] = True
                analysis['api_change_detected'] = True
                analysis['reason'] = 'API status code changed'
                analysis['confidence'] = 0.85
                
            elif 'KeyError' in error_message or 'key' in error_message.lower():
                analysis['healable'] = True
                analysis['api_change_detected'] = True
                analysis['reason'] = 'API response schema changed'
                analysis['confidence'] = 0.80
                
            elif api_response and 'expected' in error_message.lower():
                analysis['healable'] = True
                analysis['api_change_detected'] = True
                analysis['reason'] = 'API response value changed'
                analysis['confidence'] = 0.75
        
        return analysis
    
    def heal_test(self, test_code: str, test_name: str, failure_info: Dict,
                  actual_response: Dict = None) -> Tuple[str, Dict]:
        """
        Automatically heal a broken test using AI
        
        Args:
            test_code: Original test code
            test_name: Name of test to heal
            failure_info: Information about the failure
            actual_response: Actual API response from the failure
            
        Returns:
            Tuple of (healed_code, healing_metadata)
        """
        healing_metadata = {
            'test_name': test_name,
            'timestamp': datetime.now().isoformat(),
            'before_code': test_code,
            'after_code': None,
            'changes': [],
            'confidence': 0.0,
            'auto_applied': False,
            'method': 'ai_powered'
        }
        
        # Try rule-based healing first (faster and more reliable)
        healed_code, confidence = self._rule_based_healing(
            test_code, test_name, failure_info, actual_response
        )
        
        if healed_code and confidence >= self.confidence_threshold:
            healing_metadata['after_code'] = healed_code
            healing_metadata['confidence'] = confidence
            healing_metadata['method'] = 'rule_based'
            healing_metadata['auto_applied'] = True
            healing_metadata['changes'] = self._generate_diff(test_code, healed_code)
            self.healing_history.append(healing_metadata)
            return healed_code, healing_metadata
        
        # Fall back to AI-powered healing for complex cases
        healed_code, confidence = self._ai_powered_healing(
            test_code, test_name, failure_info, actual_response
        )
        
        healing_metadata['after_code'] = healed_code
        healing_metadata['confidence'] = confidence
        healing_metadata['auto_applied'] = confidence >= self.confidence_threshold
        healing_metadata['changes'] = self._generate_diff(test_code, healed_code)
        
        self.healing_history.append(healing_metadata)
        return healed_code, healing_metadata
    
    def _rule_based_healing(self, test_code: str, test_name: str,
                           failure_info: Dict, actual_response: Dict) -> Tuple[str, float]:
        """
        Apply rule-based healing for common patterns
        
        Returns:
            Tuple of (healed_code, confidence_score)
        """
        healed = test_code
        confidence = 0.0
        
        # Extract the specific test function
        test_function = self._extract_test_function(test_code, test_name)
        if not test_function:
            return healed, 0.0
        
        failure_type = failure_info.get('failure_type', '')
        error_msg = failure_info.get('error_message', '')
        
        # Rule 1: Status code mismatch
        if 'status_code' in error_msg.lower():
            expected, actual = self._extract_status_codes(error_msg)
            if expected and actual:
                # Replace expected status code with actual
                pattern = f"assert response.status_code == {expected}"
                replacement = f"assert response.status_code == {actual}"
                healed = test_code.replace(pattern, replacement)
                
                # Also try other patterns
                pattern2 = f"response.status_code, {expected}"
                replacement2 = f"response.status_code, {actual}"
                healed = healed.replace(pattern2, replacement2)
                
                if healed != test_code:
                    confidence = 0.90
                    return healed, confidence
        
        # Rule 2: Response field missing/renamed
        if 'KeyError' in error_msg or 'key' in error_msg.lower():
            missing_key = self._extract_missing_key(error_msg)
            if missing_key and actual_response:
                # Suggest field that might have replaced it
                available_keys = list(actual_response.keys()) if isinstance(actual_response, dict) else []
                similar_key = self._find_similar_key(missing_key, available_keys)
                
                if similar_key:
                    healed = test_code.replace(f"['{missing_key}']", f"['{similar_key}']")
                    healed = healed.replace(f'["{missing_key}"]', f'["{similar_key}"]')
                    confidence = 0.80
                    return healed, confidence
        
        # Rule 3: Response value changed
        if 'assert' in error_msg.lower() and '==' in error_msg:
            # Extract expected vs actual from assertion error
            expected_val, actual_val = self._extract_assertion_values(error_msg)
            if expected_val and actual_val:
                # Replace expected value with actual value
                healed = test_code.replace(f'== {expected_val}', f'== {actual_val}')
                healed = healed.replace(f'== "{expected_val}"', f'== "{actual_val}"')
                healed = healed.replace(f"== '{expected_val}'", f"== '{actual_val}'")
                
                if healed != test_code:
                    confidence = 0.75
                    return healed, confidence
        
        return healed, confidence
    
    def _ai_powered_healing(self, test_code: str, test_name: str,
                          failure_info: Dict, actual_response: Dict) -> Tuple[str, float]:
        """
        Use AI to heal complex test failures
        
        Returns:
            Tuple of (healed_code, confidence_score)
        """
        prompt = self._build_healing_prompt(test_code, test_name, failure_info, actual_response)
        
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.2,  # Lower temperature for more deterministic fixes
                        "num_predict": 1000
                    }
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                healed_code = result.get('response', '')
                
                # Extract code from markdown
                if '```python' in healed_code:
                    healed_code = healed_code.split('```python')[1].split('```')[0].strip()
                elif '```' in healed_code:
                    healed_code = healed_code.split('```')[1].split('```')[0].strip()
                
                # Validate healed code
                if self._validate_healed_code(healed_code, test_name):
                    confidence = 0.70  # AI healing gets moderate confidence
                    return healed_code, confidence
        
        except Exception as e:
            print(f"AI healing failed: {e}")
        
        return test_code, 0.0
    
    def _build_healing_prompt(self, test_code: str, test_name: str,
                            failure_info: Dict, actual_response: Dict) -> str:
        """Build prompt for AI-powered healing"""
        prompt = f"""You are an expert at fixing broken API tests. A test has failed and needs to be repaired.

Test Function:
```python
{self._extract_test_function(test_code, test_name)}
```

Failure Information:
- Test Name: {test_name}
- Error Type: {failure_info.get('failure_type', 'Unknown')}
- Error Message: {failure_info.get('error_message', 'Not provided')}
- Reason: {failure_info.get('reason', 'Not provided')}

Actual API Response:
{json.dumps(actual_response, indent=2) if actual_response else 'Not available'}

Task: Fix the test to match the actual API behavior. Only modify the assertions that are failing.

Requirements:
1. Keep the test structure intact
2. Only update assertions to match actual API behavior
3. Add comments explaining what changed
4. Return ONLY the fixed test function code

Fixed test function:
"""
        return prompt
    
    def _classify_failure(self, error_message: str) -> str:
        """Classify the type of test failure"""
        error_lower = error_message.lower()
        
        if 'assertionerror' in error_lower:
            if 'status' in error_lower:
                return 'status_code_mismatch'
            elif 'keyerror' in error_lower or 'key' in error_lower:
                return 'schema_change'
            else:
                return 'value_mismatch'
        elif 'connectionerror' in error_lower or 'timeout' in error_lower:
            return 'connection_issue'
        elif 'typeerror' in error_lower:
            return 'type_mismatch'
        else:
            return 'unknown'
    
    def _extract_test_function(self, test_code: str, test_name: str) -> str:
        """Extract specific test function from test file"""
        lines = test_code.split('\n')
        function_lines = []
        capturing = False
        
        for i, line in enumerate(lines):
            if f'def {test_name}' in line:
                capturing = True
            
            if capturing:
                function_lines.append(line)
                
                # Stop at next function or class definition
                if i > 0 and line and not line.startswith((' ', '\t', '@')) and 'def ' in line and f'def {test_name}' not in line:
                    break
        
        return '\n'.join(function_lines[:-1]) if len(function_lines) > 1 else '\n'.join(function_lines)
    
    def _extract_status_codes(self, error_msg: str) -> Tuple[Optional[int], Optional[int]]:
        """Extract expected and actual status codes from error message"""
        import re
        
        # Pattern: "assert 200 == 201" or "assert status_code == 200"
        pattern = r'assert.*?(\d{3}).*?==.*?(\d{3})'
        match = re.search(pattern, error_msg)
        
        if match:
            return int(match.group(2)), int(match.group(1))  # expected, actual
        
        # Alternative pattern: "AssertionError: 201 != 200"
        pattern2 = r'(\d{3})\s*!=\s*(\d{3})'
        match2 = re.search(pattern2, error_msg)
        
        if match2:
            return int(match2.group(2)), int(match2.group(1))  # expected, actual
        
        return None, None
    
    def _extract_missing_key(self, error_msg: str) -> Optional[str]:
        """Extract the missing key from KeyError message"""
        import re
        
        # Pattern: KeyError: 'field_name'
        pattern = r"KeyError:\s*['\"](\w+)['\"]"
        match = re.search(pattern, error_msg)
        
        if match:
            return match.group(1)
        
        return None
    
    def _find_similar_key(self, missing_key: str, available_keys: List[str]) -> Optional[str]:
        """Find similar key name in available keys"""
        missing_lower = missing_key.lower()
        
        # Exact match (case-insensitive)
        for key in available_keys:
            if key.lower() == missing_lower:
                return key
        
        # Fuzzy match using difflib
        matches = difflib.get_close_matches(missing_key, available_keys, n=1, cutoff=0.6)
        if matches:
            return matches[0]
        
        return None
    
    def _extract_assertion_values(self, error_msg: str) -> Tuple[Optional[str], Optional[str]]:
        """Extract expected and actual values from assertion error"""
        import re
        
        # Pattern: "assert 'value1' == 'value2'"
        pattern = r"assert\s+(.+?)\s*==\s*(.+?)(?:\s|$)"
        match = re.search(pattern, error_msg)
        
        if match:
            return match.group(2).strip(), match.group(1).strip()
        
        return None, None
    
    def _validate_healed_code(self, code: str, test_name: str) -> bool:
        """Validate that healed code is syntactically correct"""
        try:
            # Check syntax
            ast.parse(code)
            
            # Check that test function exists
            if f'def {test_name}' not in code:
                return False
            
            return True
        except:
            return False
    
    def _generate_diff(self, before: str, after: str) -> List[Dict]:
        """Generate human-readable diff between before and after code"""
        changes = []
        
        if before == after:
            return changes
        
        before_lines = before.split('\n')
        after_lines = after.split('\n')
        
        diff = difflib.unified_diff(before_lines, after_lines, lineterm='')
        
        for line in diff:
            if line.startswith('---') or line.startswith('+++'):
                continue
            elif line.startswith('-'):
                changes.append({
                    'type': 'removed',
                    'line': line[1:].strip()
                })
            elif line.startswith('+'):
                changes.append({
                    'type': 'added',
                    'line': line[1:].strip()
                })
        
        return changes
    
    def get_healing_summary(self) -> Dict:
        """Get summary of all healing operations"""
        total = len(self.healing_history)
        auto_applied = sum(1 for h in self.healing_history if h['auto_applied'])
        
        avg_confidence = sum(h['confidence'] for h in self.healing_history) / total if total > 0 else 0
        
        return {
            'total_healings': total,
            'auto_applied': auto_applied,
            'manual_review': total - auto_applied,
            'average_confidence': round(avg_confidence, 2),
            'success_rate': round(auto_applied / total * 100, 1) if total > 0 else 0,
            'history': self.healing_history
        }
    
    def export_healing_report(self, output_file: str):
        """Export healing report to JSON file"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': self.get_healing_summary(),
            'detailed_history': self.healing_history
        }
        
        Path(output_file).write_text(json.dumps(report, indent=2))
