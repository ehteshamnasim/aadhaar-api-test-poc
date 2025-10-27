# Simple Test Scenarios - Minimal Changes Guide

This guide shows you **exactly what to change** in your existing files to trigger each dashboard feature.

---

## 🎯 Files You'll Modify

1. **`api/dummy_aadhaar_api.py`** - Your Flask API server
2. **`specs/aadhaar-api.yaml`** - Your OpenAPI specification

---

## Scenario 1: Test Self-Healing (Auto-fix broken tests)

### What to do: Change API response, tests will break, then self-heal

**Step 1:** Change status code in `api/dummy_aadhaar_api.py`

```python
# Line 34: Change from 200 to 201
# OLD:
return jsonify({"status": "valid", "message": "Aadhaar number is valid"}), 200

# NEW:
return jsonify({"status": "valid", "message": "Aadhaar number is valid"}), 201
```

**Step 2:** Update spec to match in `specs/aadhaar-api.yaml`

```yaml
# Line 28: Change from '200' to '201'
# OLD:
        '200':
          description: Valid Aadhaar

# NEW:
        '201':
          description: Valid Aadhaar
```

**Step 3:** Run your tests (they will fail first)

```bash
python main.py --spec specs/aadhaar-api.yaml --heal
```

**What happens:**
- Tests expect status 200 (old behavior)
- API returns 201 (new behavior)
- Tests fail ❌
- Self-healing AI detects the issue
- Automatically fixes tests to expect 201 ✅
- Dashboard shows the healing in "Self-Healing" tab

---

## Scenario 2: Test Error Analysis (Deep error investigation)

### What to do: Make API return authentication errors

**Step 1:** Add auth check in `api/dummy_aadhaar_api.py`

```python
# Add after line 19 in verify_aadhaar() function
@app.route('/api/v1/aadhaar/verify', methods=['POST'])
def verify_aadhaar():
    """Verify Aadhaar number"""
    data = request.get_json()
    
    # ADD THIS NEW CODE:
    auth_token = request.headers.get('Authorization')
    if not auth_token or auth_token != 'Bearer valid-token-123':
        return jsonify({
            "status": "unauthorized", 
            "error": "Missing or invalid authentication token"
        }), 401
    
    # ... rest of existing code ...
```

**Step 2:** Run tests (they will fail with 401 errors)

```bash
python main.py --spec specs/aadhaar-api.yaml
```

**What happens:**
- Tests don't send Authorization header
- API returns 401 Unauthorized ❌
- Error Analysis examines the failure
- Shows root cause: "Missing authentication header"
- Suggests fixes in dashboard "Error Analysis" tab

---

## Scenario 3: Test API Diff (Compare API versions)

### What to do: Create two versions of your spec file

**Step 1:** Copy current spec

```bash
cp specs/aadhaar-api.yaml specs/aadhaar-api-v1.yaml
```

**Step 2:** Modify `specs/aadhaar-api.yaml` - Add breaking change

```yaml
# Around line 20: Change response field type
# OLD (in aadhaar-api-v1.yaml):
properties:
  aadhaar_number:
    type: string
    pattern: '^[0-9]{12}$'

# NEW (in aadhaar-api.yaml):
properties:
  aadhaar_number:
    type: integer  # BREAKING: Changed from string to integer!
    minimum: 100000000000
```

**Step 3:** Add a new endpoint in `specs/aadhaar-api.yaml`

```yaml
# Add at the end, before /aadhaar/demographics:
  /aadhaar/validate-new:
    post:
      summary: New validation endpoint (v2)
      description: Enhanced validation with additional checks
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                aadhaar_number:
                  type: string
      responses:
        '200':
          description: Validation result
```

**Step 4:** Compare the two specs

```bash
python -c "
from src.api_diff import APIDiffDetector
from dashboard_integration import emit_api_diff_event

detector = APIDiffDetector()
changes = detector.compare_specs(
    'specs/aadhaar-api-v1.yaml',
    'specs/aadhaar-api.yaml'
)
emit_api_diff_event(changes=[{
    'type': c.change_type,
    'path': c.path,
    'description': c.description,
    'breaking': c.breaking,
    'recommendation': c.recommendation
} for c in changes])
"
```

**What happens:**
- Compares old vs new spec
- Detects BREAKING change: string → integer
- Detects new endpoint added
- Dashboard "API Diff" tab shows:
  - 🔴 Breaking changes (red)
  - 🟢 New endpoints (green)
  - Recommendations for updating tests

---

## Scenario 4: Test Anomaly Detection (Unusual behavior)

### What to do: Make API slow or return errors

### Option A: Simulate Slow Responses

**Step 1:** Add delay in `api/dummy_aadhaar_api.py`

```python
# Add at the top after imports
import time
import random

# Add in verify_aadhaar() function after line 21
@app.route('/api/v1/aadhaar/verify', methods=['POST'])
def verify_aadhaar():
    """Verify Aadhaar number"""
    
    # ADD THIS: Randomly make API slow
    if random.random() > 0.7:  # 30% of requests are slow
        time.sleep(2)  # 2 second delay!
    
    data = request.get_json()
    # ... rest of code ...
```

### Option B: Simulate High Error Rate

**Step 2:** Make API fail randomly in `api/dummy_aadhaar_api.py`

```python
# Add in verify_aadhaar() after getting data
@app.route('/api/v1/aadhaar/verify', methods=['POST'])
def verify_aadhaar():
    """Verify Aadhaar number"""
    data = request.get_json()
    
    # ADD THIS: Randomly return 500 errors
    if random.random() > 0.8:  # 20% error rate!
        return jsonify({"error": "Database connection failed"}), 500
    
    # ... rest of code ...
```

**Step 3:** Run tests with monitoring

```bash
python main.py --spec specs/aadhaar-api.yaml --detect-anomalies
```

**What happens:**
- Some requests take 2+ seconds (normal: <100ms)
- Anomaly detector flags slow responses
- Dashboard "Anomalies" tab shows:
  - 🔴 CRITICAL: Response time anomaly
  - 🟠 HIGH: Error rate anomaly
  - Expected vs Actual values

---

## Scenario 5: Test Traffic Replay (Record and replay requests)

### What to do: Make real API calls and record them

**Step 1:** Start recording traffic in `api/dummy_aadhaar_api.py`

```python
# Add at the top after imports
from src.traffic_replay import TrafficRecorder

# Add after app = Flask(__name__)
traffic_recorder = TrafficRecorder()

# Add middleware to record all requests
@app.before_request
def record_request():
    request.start_time = time.time()

@app.after_request
def record_response(response):
    if hasattr(request, 'start_time'):
        duration = (time.time() - request.start_time) * 1000
        traffic_recorder.record_request(
            method=request.method,
            url=request.url,
            headers=dict(request.headers),
            body=request.get_json() if request.is_json else None,
            status_code=response.status_code,
            response_body=response.get_json() if response.is_json else None,
            duration_ms=duration
        )
    return response
```

**Step 2:** Make some API calls

```bash
# Call 1: Verify Aadhaar
curl -X POST http://localhost:5001/api/v1/aadhaar/verify \
  -H "Content-Type: application/json" \
  -d '{"aadhaar_number": "123456789012"}'

# Call 2: Get demographics
curl -X POST http://localhost:5001/api/v1/aadhaar/demographics \
  -H "Content-Type: application/json" \
  -d '{"aadhaar_number": "123456789012", "consent": true}'

# Call 3: Generate OTP
curl -X POST http://localhost:5001/api/v1/aadhaar/otp/generate \
  -H "Content-Type: application/json" \
  -d '{"aadhaar_number": "987654321098"}'
```

**Step 3:** View recorded traffic

```bash
python -c "
from src.traffic_replay import TrafficRecorder
from dashboard_integration import emit_traffic_event

recorder = TrafficRecorder()
for req in recorder.get_recorded_requests():
    emit_traffic_event(
        method=req['method'],
        url=req['url'],
        status_code=req['status_code']
    )
"
```

**What happens:**
- All API calls are recorded
- Dashboard "Traffic Replay" tab shows:
  - 🟢 POST requests (green)
  - 🔵 GET requests (blue)
  - Status codes (200, 201, etc.)
  - Can generate tests from recorded traffic

---

## 🚀 Quick Test All Scenarios

Want to test everything quickly without modifying files?

```bash
# Terminal 1: Start your API
cd /Users/ehtesham/Developer/aadhaar-api-test-poc
python api/dummy_aadhaar_api.py

# Terminal 2: Start dashboard
python dashboard/server.py

# Terminal 3: Send test events (simulates all scenarios)
python test_dashboard.py

# Browser: Open http://localhost:5050
# Click through all 6 tabs!
```

---

## 📋 Checklist: What Triggers What

| Dashboard Tab | What to Change | Where to Change | Expected Result |
|--------------|----------------|-----------------|-----------------|
| **Overview** | Nothing - always shows data | N/A | Shows test metrics automatically |
| **Self-Healing** | Change status code in API | `api/dummy_aadhaar_api.py` line 34 | Tests fail → auto-fix → shows healing |
| **Error Analysis** | Add auth requirement | `api/dummy_aadhaar_api.py` line 21 | Tests fail with 401 → shows analysis |
| **API Diff** | Create two spec versions | `specs/aadhaar-api.yaml` | Shows breaking/non-breaking changes |
| **Anomaly Detection** | Add `time.sleep(2)` or random errors | `api/dummy_aadhaar_api.py` line 23 | Shows slow response or error rate anomalies |
| **Traffic Replay** | Add recording middleware | `api/dummy_aadhaar_api.py` top | Records all requests → shows in dashboard |

---

## 💡 Minimal Changes Summary

### To test Self-Healing:
```python
# api/dummy_aadhaar_api.py, line 34
# Change: 200 → 201
return jsonify({...}), 201  # was 200
```

### To test Error Analysis:
```python
# api/dummy_aadhaar_api.py, line 21 (add new lines)
auth_token = request.headers.get('Authorization')
if not auth_token or auth_token != 'Bearer valid-token-123':
    return jsonify({"error": "Unauthorized"}), 401
```

### To test API Diff:
```bash
# Terminal
cp specs/aadhaar-api.yaml specs/aadhaar-api-v1.yaml
# Then edit specs/aadhaar-api.yaml: change a field type or add endpoint
```

### To test Anomaly Detection:
```python
# api/dummy_aadhaar_api.py, line 23 (add new lines)
import time
if random.random() > 0.7:
    time.sleep(2)  # Make it slow!
```

### To test Traffic Replay:
```python
# api/dummy_aadhaar_api.py, after line 4 (add new lines)
from src.traffic_replay import TrafficRecorder
traffic_recorder = TrafficRecorder()

# Add @app.after_request decorator (see full example above)
```

---

## 🎯 Recommended Testing Order

1. **Start Simple** - Run `python test_dashboard.py` first (no file changes needed!)
2. **Test Self-Healing** - Change status code, see auto-fix
3. **Test Error Analysis** - Add auth requirement, see error breakdown
4. **Test API Diff** - Create two spec versions, see differences
5. **Test Anomalies** - Add delays, see performance issues
6. **Test Traffic** - Add recording, see captured requests

---

## ⚠️ Remember to Revert!

After testing, revert your changes:

```bash
# Revert dummy API changes
git checkout api/dummy_aadhaar_api.py

# Revert spec changes
git checkout specs/aadhaar-api.yaml

# Or manually remove the test code you added
```

---

**That's it!** These are the **minimal changes** needed to test all dashboard features. 

**Easiest way:** Just run `python test_dashboard.py` - it simulates everything without any file changes! ✨
