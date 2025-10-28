# 🔄 Self-Healing Workflow - Complete Explanation

## Your Questions Answered

### Q1: "After self healing, that flow should be correct right?"
**Answer**: Currently **partially correct**. Here's what happens:

### Q2: "After self healing test will rerun? or before?"
**Answer**: Currently **NO** - tests do NOT re-run after healing. They should!

### Q3: "In generated test cases, if self healing happen how can we know that is self healed?"
**Answer**: Currently **NOT TRACKED** in generated files. We need to add markers!

---

## Current Workflow (What Happens Now) ❌

```
1. Git commit detected
   ↓
2. Tests generated (test_aadhaar_api_v41.py)
   ↓
3. Tests executed
   ↓
4. Test fails: assert 200 == 400
   ↓
5. Self-healing triggered
   ↓
6. Healed code generated
   ↓
7. Healing event sent to dashboard
   ↓
8. ❌ STOPS HERE - Test file NOT updated
   ↓
9. ❌ Tests NOT re-run
   ↓
10. ❌ Next commit uses SAME broken test
```

**Problem**: Healing happens but changes are NOT applied to actual test files!

---

## Improved Workflow (What SHOULD Happen) ✅

```
1. Git commit detected
   ↓
2. Tests generated (test_aadhaar_api_v41.py)
   ↓
3. Tests executed (FIRST RUN)
   ↓
4. Test fails: assert 200 == 400
   ↓
5. Self-healing triggered
   ↓
6. ✅ Healed code written to test file with marker
   ↓
7. ✅ Healing event sent to dashboard
   ↓
8. ✅ Tests RE-RUN automatically (SECOND RUN)
   ↓
9. ✅ Healed test now passes
   ↓
10. ✅ Git commit created with healed tests
   ↓
11. ✅ Next commit uses FIXED test
```

**Benefits**:
- Tests are actually fixed
- Re-run confirms healing worked
- Test files show healing history
- Dashboard shows before/after results

---

## Proposed Implementation

### 1. Add Healing Markers to Test Files

#### Before Healing
```python
def test_verify_otp_success(client):
    response = client.post('/api/v1/aadhaar/otp/verify', 
                          json={'transaction_id': '123', 'otp': '456'})
    assert response.status_code == 400  # Expected 400 but API returned 200
```

#### After Healing (with markers) ✅
```python
def test_verify_otp_success(client):
    # 🔧 AUTO-HEALED on 2025-10-28 02:50:15
    # Original: assert response.status_code == 400
    # Reason: API behavior changed - now returns 200 instead of 400
    # Confidence: 85%
    response = client.post('/api/v1/aadhaar/otp/verify', 
                          json={'transaction_id': '123', 'otp': '456'})
    assert response.status_code == 200  # ✅ HEALED: Changed from 400
```

**Benefits**:
- ✅ Clear visual indicator
- ✅ Timestamp shows when healed
- ✅ Original assertion preserved in comment
- ✅ Explanation of why it changed
- ✅ Confidence score tracked

---

### 2. Test Re-run Logic

```python
def run_tests_fixed(self, test_file):
    """
    Run tests with automatic healing and re-run
    """
    # First run
    print("[PROGRESS] Executing automated test suite (FIRST RUN)")
    result1 = self._execute_tests(test_file)
    failures1 = self._extract_failures(result1)
    
    # Apply healing if needed
    healed_tests = []
    if failures1:
        print(f"\n   ⚠️  {len(failures1)} tests failed - attempting healing...")
        
        for failure in failures1:
            if self._can_auto_heal(failure['reason']):
                healed = self._apply_healing_to_file(
                    test_file, 
                    failure['test_name'], 
                    failure['reason']
                )
                if healed:
                    healed_tests.append(failure['test_name'])
                    print(f"   🔧 Healed: {failure['test_name']}")
    
    # Second run (only if healing happened)
    if healed_tests:
        print(f"\n[PROGRESS] Re-running tests after healing ({len(healed_tests)} healed)")
        result2 = self._execute_tests(test_file)
        
        # Compare results
        failures2 = self._extract_failures(result2)
        healing_success = len(failures1) - len(failures2)
        
        print(f"\n   📊 Healing Results:")
        print(f"   • Before: {len(failures1)} failures")
        print(f"   • After: {len(failures2)} failures")
        print(f"   • Fixed: {healing_success} tests ✅")
        
        return result2  # Return re-run results
    
    return result1  # Return original results
```

---

### 3. File Writing Implementation

```python
def _apply_healing_to_file(self, test_file, test_name, reason):
    """
    Actually write healed code to test file
    
    Returns:
        bool: True if healing was applied successfully
    """
    import re
    from datetime import datetime
    
    # Read current test file
    with open(test_file, 'r') as f:
        content = f.read()
    
    # Generate healed code
    healed_code = self._attempt_healing(test_name, reason)
    if not healed_code:
        return False
    
    # Extract just the assertion from healed code
    healed_assertion = self._extract_assertion(healed_code)
    
    # Find the test function
    test_pattern = rf'def {test_name}\([^)]+\):(.*?)(?=\ndef |\Z)'
    match = re.search(test_pattern, content, re.DOTALL)
    
    if not match:
        print(f"   ⚠️  Could not find test function: {test_name}")
        return False
    
    original_function = match.group(0)
    
    # Extract original assertion
    original_assertion = self._extract_original_assertion(original_function, reason)
    
    # Calculate confidence
    confidence = self._calculate_confidence(reason)
    
    # Build healing comment block
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    healing_comment = f'''
    # 🔧 AUTO-HEALED on {timestamp}
    # Original: {original_assertion}
    # Reason: {self._get_healing_reason(reason)}
    # Confidence: {confidence:.0%}'''
    
    # Replace assertion with healed version
    healed_function = original_function.replace(
        original_assertion,
        healing_comment + '\n    ' + healed_assertion
    )
    
    # Replace in content
    new_content = content.replace(original_function, healed_function)
    
    # Write back to file
    with open(test_file, 'w') as f:
        f.write(new_content)
    
    # Send healing event to dashboard
    send_healing_event(
        test_name=test_name,
        confidence=confidence,
        old_code=original_assertion,
        new_code=healed_assertion
    )
    
    print(f"   ✅ File updated: {test_file}")
    return True
```

---

### 4. Healing Tracking in Test Files

#### Option A: Inline Comments (Recommended) ✅
```python
def test_example(client):
    # 🔧 AUTO-HEALED on 2025-10-28 02:50:15
    # Original: assert response.status_code == 400
    # Reason: API now returns 200
    # Confidence: 85%
    assert response.status_code == 200  # ✅ HEALED
```

**Pros**:
- Easy to see in code
- Git diff shows changes clearly
- Developers understand what happened

#### Option B: Metadata at Top
```python
"""AI-Generated Tests v41 - 2025-10-28 02:45:30
HEALING HISTORY:
- test_verify_otp_success: Healed on 2025-10-28 02:50:15 (85% confidence)
  Original: assert response.status_code == 400
  New: assert response.status_code == 200
  Reason: API behavior changed
"""
```

#### Option C: Separate Healing Log File
```
tests/
  test_aadhaar_api_v41.py
  test_aadhaar_api_v41_healing.json  ← Healing metadata
```

**Recommendation**: Use **Option A (Inline)** + **Option C (Log File)** for best tracking.

---

## Complete Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    GIT COMMIT DETECTED                          │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 1: Generate Tests                                         │
│  • Parse OpenAPI spec                                           │
│  • AI generates test_aadhaar_api_v41.py                        │
│  • 15 tests created                                             │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 2: Execute Tests (FIRST RUN)                             │
│  • Run pytest on new test file                                  │
│  • Result: 8 passed, 7 failed                                   │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 3: Analyze Failures                                       │
│  • test_verify_otp_success: assert 200 == 400                  │
│  • test_demographics: assert 200 == 400                        │
│  • test_auth: assert 200 == 401                                │
│  • ... 4 more failures                                          │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 4: Self-Healing (for each failure)                       │
│  • Check if healable (regex match status codes)                │
│  • Generate healed code                                         │
│  • Calculate confidence (65-95%)                                │
│  • ✅ Write to test file with healing markers                  │
│  • ✅ Log to healing history file                              │
│  • Send event to dashboard                                     │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 5: Re-run Tests (SECOND RUN) ✅                          │
│  • Run pytest again on HEALED test file                        │
│  • Result: 14 passed, 1 failed                                  │
│  • 6 tests fixed by healing!                                    │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 6: Report & Commit                                        │
│  • Dashboard shows healing success                              │
│  • Git commit: "Auto-healed 6 tests"                           │
│  • Test file now has healing markers                            │
└─────────────────────────────────────────────────────────────────┘
```

---

## Code Implementation

### Enhanced `main.py` additions:

```python
class POCOrchestrator:
    def __init__(self, spec_path):
        # ... existing code ...
        self.healing_history = []  # Track all healings
        self.healing_log_file = "tests/healing_history.json"
    
    def run_tests_with_healing(self, test_file):
        """
        Enhanced test execution with automatic healing and re-run
        """
        print("[PROGRESS] Executing automated test suite")
        
        # FIRST RUN
        print("\n🔍 FIRST RUN: Initial test execution...")
        result_first = self._execute_pytest(test_file)
        failures_first = self._parse_failures(result_first)
        
        # Display first run results
        passed_first = self.passed_tests
        failed_first = self.failed_tests
        print(f"\n   📊 First Run Results:")
        print(f"   • Passed: {passed_first}")
        print(f"   • Failed: {failed_first}")
        
        # HEALING PHASE
        if failures_first and failed_first > 0:
            print(f"\n🔧 HEALING PHASE: Attempting to fix {failed_first} failures...")
            healed_count = 0
            
            for failure in failures_first:
                test_name = failure['test_name']
                reason = failure['reason']
                
                if self._can_auto_heal(reason):
                    success = self._apply_healing_to_file(
                        test_file, 
                        test_name, 
                        reason
                    )
                    if success:
                        healed_count += 1
                        print(f"   ✅ Healed: {test_name}")
                    else:
                        print(f"   ⚠️  Could not heal: {test_name}")
            
            # SECOND RUN (if any healing happened)
            if healed_count > 0:
                print(f"\n🔁 SECOND RUN: Re-executing after healing {healed_count} tests...")
                result_second = self._execute_pytest(test_file)
                failures_second = self._parse_failures(result_second)
                
                passed_second = self.passed_tests
                failed_second = self.failed_tests
                
                # Calculate healing effectiveness
                tests_fixed = failed_first - failed_second
                healing_rate = (tests_fixed / failed_first * 100) if failed_first > 0 else 0
                
                print(f"\n   📊 Second Run Results:")
                print(f"   • Passed: {passed_second} (↑{passed_second - passed_first})")
                print(f"   • Failed: {failed_second} (↓{failed_first - failed_second})")
                print(f"\n   🎯 Healing Effectiveness:")
                print(f"   • Tests Fixed: {tests_fixed}/{failed_first}")
                print(f"   • Success Rate: {healing_rate:.1f}%")
                
                # Save healing history
                self._save_healing_history({
                    'timestamp': datetime.now().isoformat(),
                    'test_file': test_file,
                    'healed_count': healed_count,
                    'tests_fixed': tests_fixed,
                    'success_rate': healing_rate,
                    'before': {'passed': passed_first, 'failed': failed_first},
                    'after': {'passed': passed_second, 'failed': failed_second}
                })
                
                return result_second
            else:
                print("\n   ⚠️  No tests were healable")
        else:
            print("\n   ✅ All tests passed - no healing needed")
        
        return result_first
    
    def _save_healing_history(self, healing_data):
        """Save healing history to JSON file"""
        import json
        history = []
        
        # Load existing history
        if os.path.exists(self.healing_log_file):
            with open(self.healing_log_file, 'r') as f:
                history = json.load(f)
        
        # Append new healing
        history.append(healing_data)
        
        # Save
        with open(self.healing_log_file, 'w') as f:
            json.dump(history, f, indent=2)
        
        print(f"\n   📝 Healing history saved to: {self.healing_log_file}")
```

---

## What You'll See After Implementation

### 1. In Test Files (with healing markers)
```python
def test_verify_otp_success(client):
    # 🔧 AUTO-HEALED on 2025-10-28 02:50:15
    # Original: assert response.status_code == 400
    # Reason: API behavior changed - returns 200 instead of 400
    # Confidence: 85%
    response = client.post('/api/v1/aadhaar/otp/verify', json={...})
    assert response.status_code == 200  # ✅ HEALED: Changed from 400
```

### 2. In Terminal Output
```
🔍 FIRST RUN: Initial test execution...
   ✗ test_verify_otp_success: Line 13: assert 200 == 400
   ✗ test_demographics: Line 20: assert 200 == 400
   
   📊 First Run Results:
   • Passed: 8
   • Failed: 7

🔧 HEALING PHASE: Attempting to fix 7 failures...
   ✅ Healed: test_verify_otp_success (85% confidence)
   ✅ Healed: test_demographics (85% confidence)
   ✅ Healed: test_auth (88% confidence)
   ... (4 more)

🔁 SECOND RUN: Re-executing after healing 6 tests...
   ✓ test_verify_otp_success
   ✓ test_demographics
   ✓ test_auth
   
   📊 Second Run Results:
   • Passed: 14 (↑6)
   • Failed: 1 (↓6)
   
   🎯 Healing Effectiveness:
   • Tests Fixed: 6/7
   • Success Rate: 85.7%
```

### 3. In Dashboard
```
Self-Healing Tab:
┌────────────────────────────────────────────────────┐
│ Total Healings: 14                                 │
│ Success Rate: 92%                                  │
│ Avg Confidence: 87%                                │
│                                                    │
│ Recent Healing Operations:                        │
│ ✅ test_verify_otp_success (85%) - Fixed          │
│ ✅ test_demographics (85%) - Fixed                 │
│ ✅ test_auth (88%) - Fixed                         │
│ ✅ test_verify_aadhaar (95%) - Fixed              │
│ ⚠️ test_server_error (65%) - Needs Review         │
└────────────────────────────────────────────────────┘
```

### 4. In Healing History File (`tests/healing_history.json`)
```json
[
  {
    "timestamp": "2025-10-28T02:50:15.123456",
    "test_file": "tests/test_aadhaar_api_v41.py",
    "healed_count": 6,
    "tests_fixed": 6,
    "success_rate": 85.7,
    "before": {"passed": 8, "failed": 7},
    "after": {"passed": 14, "failed": 1},
    "healings": [
      {
        "test_name": "test_verify_otp_success",
        "original": "assert response.status_code == 400",
        "healed": "assert response.status_code == 200",
        "confidence": 0.85,
        "reason": "API behavior changed"
      }
    ]
  }
]
```

---

## Benefits of This Approach

### ✅ For Developers
- Test files show healing history
- Clear visual markers (🔧, ✅)
- Understand why assertions changed
- Git history tracks all healing

### ✅ For Testing
- Tests automatically fixed and re-run
- Confirmation that healing worked
- High healing success rate (85-95%)
- Reduced manual fixing effort

### ✅ For Debugging
- Complete healing history
- Confidence scores tracked
- Before/After comparison
- Easy to roll back if needed

### ✅ For Dashboard
- Real-time healing updates
- Success metrics visible
- Healing effectiveness tracked
- Before/After test counts

---

## Summary

### Current Situation ❌
- Healing generates code but doesn't apply it
- Tests don't re-run after healing
- No tracking in test files
- No way to know what was healed

### Improved Workflow ✅
- Healing writes to test files with markers
- Tests automatically re-run after healing
- Healing markers show what changed and why
- History file tracks all healings
- Dashboard shows healing effectiveness

---

## Next Steps to Implement

1. **Add file writing logic** to `_apply_healing_to_file()`
2. **Add re-run logic** to `run_tests_with_healing()`
3. **Add healing markers** to test files
4. **Create healing history** JSON file
5. **Update dashboard** to show before/after counts

**Would you like me to implement these improvements now?** 🚀
