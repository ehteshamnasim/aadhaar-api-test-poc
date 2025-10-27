# 🎯 YOUR COMPLETE WORKFLOW - EXPLAINED

Based on your code, here's what you have and what needs to be fixed:

---

## 📊 **Current Setup - What You Have**

### Your Workflow:
```
Terminal 1: python api/dummy_aadhaar_api.py (API server on port 5001)
Terminal 2: python3 start_dashboard.py       (Dashboard on port 8080) ← WRONG PORT!
Terminal 3: git commit → triggers main.py    (Test automation)
```

### What Happens When You Commit:
```bash
1. You change specs/aadhaar-api.yaml
2. Git commit triggers (probably post-commit hook)
3. main.py runs automatically
4. Sends events to http://localhost:8080 ← WRONG!
5. Dashboard runs on port 8080 ← SHOULD BE 5050!
```

---

## 🐛 **THE PROBLEM - Port Mismatch!**

### In `main.py` (line 24):
```python
DASHBOARD_URL = "http://localhost:8080"  # ← Points to port 8080
```

### In `start_dashboard.py` (line 18):
```python
app.run(host='0.0.0.0', port=8080, ...)  # ← Runs on port 8080
```

### In `dashboard/server.py` (fixed by me):
```python
app.run(host='0.0.0.0', port=5050, ...)  # ← NOW runs on port 5050!
```

### In `test_dashboard.py`:
```python
DASHBOARD_URL = "http://localhost:5050"  # ← Points to port 5050
```

**MISMATCH!**
- `main.py` sends to port **8080**
- `start_dashboard.py` tries to run on port **8080**
- But I changed `dashboard/server.py` to port **5050**
- And `test_dashboard.py` expects port **5050**

---

## ✅ **THE FIX - Align All Ports**

### Option A: Everything on Port 5050 (RECOMMENDED)

**Why 5050?**
- Less common port (less conflicts)
- Already configured in test scripts
- Already set in dashboard/server.py

**Changes Needed:**

1. **Fix `main.py` line 24:**
```python
# OLD:
DASHBOARD_URL = "http://localhost:8080"

# NEW:
DASHBOARD_URL = "http://localhost:5050"
```

2. **Fix `start_dashboard.py` line 18:**
```python
# OLD:
app.run(host='0.0.0.0', port=8080, ...)

# NEW:
app.run(host='0.0.0.0', port=5050, ...)
```

3. **Fix `start_dashboard.py` line 12 (display message):**
```python
# OLD:
print("\n🌐 Dashboard running at: http://localhost:8080")

# NEW:
print("\n🌐 Dashboard running at: http://localhost:5050")
```

### Option B: Everything on Port 8080

**Changes Needed:**

1. **Fix `dashboard/server.py` line 785:**
```python
# OLD:
app.run(host='0.0.0.0', port=5050, ...)

# NEW:
app.run(host='0.0.0.0', port=8080, ...)
```

2. **Fix `test_dashboard.py` line 13:**
```python
# OLD:
DASHBOARD_URL = "http://localhost:5050/api/event"

# NEW:
DASHBOARD_URL = "http://localhost:8080/api/event"
```

---

## 📋 **Why Only Overview Tab Works**

### Your `main.py` Already Sends These Events:
```python
✅ send_event('clear', ...)         # Line 95
✅ send_event('parse', ...)         # Line 147
✅ send_event('generate', ...)      # Line 167, 193, 237
✅ send_event('test_created', ...) # Line 227
✅ send_event('validate', ...)     # Line 257
✅ send_event('execute', ...)      # Line 456, 509
✅ send_event('coverage', ...)     # Line 535
✅ send_event('summary', ...)      # Line 557
```

### Your `main.py` DOES NOT Send These Events:
```python
❌ emit_healing_event()         # Self-Healing tab
❌ emit_error_analysis_event()  # Error Analysis tab
❌ emit_api_diff_event()        # API Diff tab
❌ emit_anomaly_event()         # Anomalies tab
❌ emit_traffic_event()         # Traffic Replay tab (handled by API)
```

**That's why only Overview tab shows data!**

---

## 🎯 **API Diff - How It SHOULD Work for You**

### Current Situation:
- You only have `specs/aadhaar-api.yaml`
- No comparison possible

### Solution: Git-Based Comparison

When you commit changes to `specs/aadhaar-api.yaml`, compare:
- **Current version** (after commit)
- **Previous version** (before commit)

### Implementation:

```python
# In main.py, add this function:

def detect_spec_changes(self):
    """Compare current spec with previous git version"""
    try:
        # Get previous version from git
        result = subprocess.run(
            ['git', 'show', 'HEAD~1:specs/aadhaar-api.yaml'],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            old_spec_content = result.stdout
            
            # Save to temp file
            with open('/tmp/old_spec.yaml', 'w') as f:
                f.write(old_spec_content)
            
            # Compare specs
            from src.api_diff import APIDiffDetector
            from dashboard_integration import emit_api_diff_event
            
            detector = APIDiffDetector()
            changes = detector.compare_specs(
                '/tmp/old_spec.yaml',
                self.spec_path
            )
            
            if changes:
                emit_api_diff_event(changes=[{
                    'type': c.change_type,
                    'path': c.path,
                    'description': c.description,
                    'breaking': c.breaking,
                    'recommendation': c.recommendation
                } for c in changes])
                
                return changes
    except:
        pass
    
    return None

# Then call it in run() method after parsing:
def run(self):
    # ... existing code ...
    
    parsed_spec = self.parse_spec()
    
    # ADD THIS:
    spec_changes = self.detect_spec_changes()
    if spec_changes:
        self._log(f"Detected {len(spec_changes)} API changes")
    
    # ... rest of code ...
```

---

## 🔧 **Smart Test Execution - Run Only Changed Tests**

### What You Want:
If only `/api/aadhaar/verify` changed, run only tests for that endpoint.

### How to Implement:

```python
# In main.py, add this method:

def find_affected_tests(self, changed_endpoints):
    """Find tests that use changed endpoints"""
    affected_tests = []
    
    # Read test file
    with open(self.test_file_path, 'r') as f:
        test_code = f.read()
    
    # For each changed endpoint
    for endpoint in changed_endpoints:
        # Extract path like /api/aadhaar/verify
        path = endpoint.get('path', '')
        
        # Find test functions that use this path
        for line_num, line in enumerate(test_code.split('\n'), 1):
            if 'def test_' in line:
                # Get test name
                test_name = line.split('(')[0].replace('def ', '').strip()
                
                # Check if endpoint path appears in next 20 lines
                test_lines = test_code.split('\n')[line_num:line_num+20]
                test_block = '\n'.join(test_lines)
                
                if path in test_block:
                    affected_tests.append(test_name)
    
    return list(set(affected_tests))  # Remove duplicates

# Then modify run_tests_fixed to accept test filter:

def run_tests_fixed(self, test_filter=None):
    """Execute tests - optionally only specific tests"""
    
    # Build pytest command
    cmd = ['pytest', abs_test_path, '-v', '--tb=line']
    
    # Add test filter if provided
    if test_filter:
        # Run only specific tests
        for test_name in test_filter:
            cmd.extend(['-k', test_name])
        
        print(f"   Running {len(test_filter)} affected tests only")
    else:
        print(f"   Running all {self.unique_test_count} tests")
    
    # ... rest of code ...

# Usage in run() method:

def run(self):
    # ... existing code ...
    
    # Check for API changes
    spec_changes = self.detect_spec_changes()
    
    if spec_changes:
        # Find affected tests
        affected_tests = self.find_affected_tests(spec_changes)
        
        if affected_tests:
            print(f"   Smart execution: Running {len(affected_tests)} affected tests")
            self.run_tests_fixed(test_filter=affected_tests)
        else:
            print("   Running all tests (couldn't determine affected tests)")
            self.run_tests_fixed()
    else:
        # No API changes, run all tests
        self.run_tests_fixed()
```

---

## 📱 **Dashboard UI Control (Future Enhancement)**

### Add Checkboxes to API Diff Tab:

In `dashboard/index.html` (inside API Diff tab):
```html
<div id="diff-tab" class="tab-pane">
    <div id="change-list" class="change-list">
        <!-- Each change item gets checkbox -->
        <div class="change-item">
            <input type="checkbox" id="change-1" checked>
            <label>
                <span class="change-path">/api/aadhaar/verify</span>
                <span class="change-type breaking">BREAKING</span>
            </label>
            <button onclick="runTestsFor('/api/aadhaar/verify')">
                Run Tests
            </button>
        </div>
    </div>
    
    <div class="change-actions">
        <button onclick="runSelectedTests()">Run Selected Tests</button>
        <button onclick="runAllTests()">Run All Tests</button>
    </div>
</div>
```

In `dashboard/app.js`:
```javascript
function runTestsFor(endpoint) {
    // Send command to backend
    fetch('http://localhost:5050/api/run-tests', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            endpoints: [endpoint],
            mode: 'selective'
        })
    });
}

function runSelectedTests() {
    // Get checked items
    const selected = [];
    document.querySelectorAll('.change-item input:checked').forEach(cb => {
        const path = cb.closest('.change-item').querySelector('.change-path').textContent;
        selected.push(path);
    });
    
    // Send to backend
    fetch('http://localhost:5050/api/run-tests', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            endpoints: selected,
            mode: 'selective'
        })
    });
}
```

Add endpoint in `dashboard/server.py`:
```python
@app.route('/api/run-tests', methods=['POST'])
def trigger_test_run():
    data = request.get_json()
    endpoints = data.get('endpoints', [])
    mode = data.get('mode', 'all')
    
    # Trigger main.py with selective test flag
    subprocess.Popen([
        'python3', 'main.py',
        '--spec', 'specs/aadhaar-api.yaml',
        '--endpoints', ','.join(endpoints)
    ])
    
    return jsonify({'status': 'started'})
```

---

## 🎯 **SUMMARY - What Needs to be Done**

### Priority 1: Fix Port Mismatch (CRITICAL)
1. ✅ Change `main.py` line 24: `DASHBOARD_URL = "http://localhost:5050"`
2. ✅ Change `start_dashboard.py` line 18: `port=5050`
3. ✅ Change `start_dashboard.py` line 12: Display message to 5050

### Priority 2: Integrate New Features into main.py
1. ✅ Add `emit_error_analysis_event()` when tests fail
2. ✅ Add `emit_healing_event()` when self-healing fixes tests
3. ✅ Add `detect_spec_changes()` for git-based API diff
4. ✅ Add `emit_api_diff_event()` when spec changes detected
5. ✅ Add `emit_anomaly_event()` when slow responses detected

### Priority 3: Smart Test Execution
1. ✅ Add `find_affected_tests()` method
2. ✅ Modify `run_tests_fixed()` to accept test filter
3. ✅ Add command-line flag `--run-changed-only`

### Priority 4: Dashboard UI Controls (Optional)
1. Add checkboxes to API Diff tab
2. Add "Run Selected Tests" button
3. Add `/api/run-tests` endpoint to dashboard

---

**Want me to implement these fixes for you?** Tell me which priority to start with! 🚀
