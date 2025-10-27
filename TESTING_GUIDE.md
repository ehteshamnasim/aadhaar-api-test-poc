# Complete Testing Guide - All Features Explained

## 🎯 What Each Feature Does

### 1. **Overview Tab** (Original Features)
**What it does:** Shows your existing API testing pipeline metrics
- API specification parsing
- Test generation progress
- Test execution results
- Code coverage
- Activity logs

**When you see it:** This runs automatically when you use `main.py`

---

### 2. **Self-Healing Tab** ⭐ NEW
**What it does:** Automatically fixes broken tests when APIs change

**Example Scenario:**
```python
# Your API changed from:
GET /users  -> returns status 201

# To:
GET /users  -> returns status 200

# Your test breaks:
assert response.status_code == 201  # ❌ FAILS

# Self-Healing AI fixes it:
assert response.status_code == 200  # ✅ FIXED
```

**When you see it:** 
- When tests fail due to API changes
- AI analyzes the failure
- Suggests and applies fixes automatically
- Shows before/after code diff

---

### 3. **Error Analysis Tab** ⭐ NEW
**What it does:** Deep analysis of why tests failed with actionable fix suggestions

**Example Scenario:**
```python
# Test fails with: 401 Unauthorized

# Error Analysis shows:
- Error Type: HTTPError
- Root Cause: "Missing authentication header"
- Fix Suggestions:
  💡 Add Authorization header with Bearer token
  💡 Check if API key is valid
  💡 Verify authentication endpoint is working
```

**When you see it:**
- Any time a test fails
- Provides detailed request/response info
- Gives specific steps to fix the problem

---

### 4. **API Diff Tab** ⭐ NEW
**What it does:** Shows differences between two versions of your API specification

**Example Scenario:**
```yaml
# Old API spec (v1.0):
/api/orders:
  response:
    total: string  # "100.50"

# New API spec (v1.1):
/api/orders:
  response:
    total: number  # 100.50

# API Diff shows:
🔴 BREAKING CHANGE
Path: /api/v1/orders
Description: Field "total" changed from string to number
Recommendation: Update tests to expect number instead of string
```

**When you see it:**
- When comparing old vs new API specs
- Before deploying API changes
- Identifies breaking vs non-breaking changes

---

### 5. **Anomaly Detection Tab** ⭐ NEW
**What it does:** Uses Machine Learning to detect unusual API behavior

**What is an Anomaly?**
An anomaly is something unexpected or unusual that deviates from normal behavior.

**Example Anomalies:**

**Response Time Anomaly:**
```
Normal: GET /users responds in 100ms
Anomaly: GET /users now takes 500ms (5x slower!)
Severity: CRITICAL
```

**Error Rate Anomaly:**
```
Normal: API has 1% error rate
Anomaly: API now has 15% error rate
Severity: HIGH
```

**Status Code Anomaly:**
```
Normal: GET /products returns 200
Anomaly: GET /products returns 500 Internal Server Error
Severity: CRITICAL
```

**When you see it:**
- During test execution
- When API performance degrades
- When error rates increase
- When unexpected status codes appear

---

### 6. **Traffic Replay Tab** ⭐ NEW
**What it does:** Records real API requests and converts them into tests

**What is Traffic Replay?**
Traffic Replay captures actual API calls from production/staging and saves them. Later, you can "replay" these calls to generate tests automatically.

**Example Workflow:**
```
1. RECORD Phase:
   - User makes request: POST /orders {"item": "laptop", "qty": 1}
   - Traffic Recorder captures: method, URL, headers, body, response
   
2. REPLAY Phase:
   - Converts captured traffic into pytest test:
   
   def test_create_order_from_traffic():
       response = requests.post(
           "https://api.example.com/orders",
           json={"item": "laptop", "qty": 1}
       )
       assert response.status_code == 201
       assert "order_id" in response.json()
```

**When you see it:**
- When recording production traffic
- When generating tests from real usage patterns
- When debugging issues that happened in production

---

## 🧪 How to Test Each Feature

### Method 1: Quick Test with Test Script (Easiest!)

```bash
# Terminal 1: Start dashboard
cd /Users/ehtesham/Developer/aadhaar-api-test-poc
python dashboard/server.py

# Terminal 2: Run test script
python test_dashboard.py

# Browser: Open http://localhost:5050
# Click through all 6 tabs to see data!
```

This sends sample events to ALL tabs automatically! ✅

---

### Method 2: Manual Testing with curl (Step by Step)

#### **Test Self-Healing Tab**

```bash
# Send a healing event
curl -X POST http://localhost:5050/api/event \
  -H "Content-Type: application/json" \
  -d '{
    "type": "healing",
    "test_name": "test_authentication",
    "confidence": 0.95,
    "old_code": "assert response.status_code == 201",
    "new_code": "assert response.status_code == 200",
    "diff": {
      "before": "assert response.status_code == 201",
      "after": "assert response.status_code == 200"
    }
  }'

# Now check dashboard:
# 1. Switch to "Self-Healing" tab
# 2. See the healing with 95% confidence
# 3. Click it to view code diff
```

#### **Test Error Analysis Tab**

```bash
# Send an error analysis event
curl -X POST http://localhost:5050/api/event \
  -H "Content-Type: application/json" \
  -d '{
    "type": "error_analysis",
    "test_name": "test_payment_api",
    "error_type": "AssertionError",
    "message": "Expected status code 200, but got 401",
    "root_cause": "Missing authentication token",
    "suggestions": [
      "Add Authorization header with valid token",
      "Check if token has expired",
      "Verify API key is configured correctly"
    ],
    "request": {
      "method": "POST",
      "url": "https://api.example.com/payments",
      "headers": {"Content-Type": "application/json"}
    },
    "response": {
      "status_code": 401,
      "body": {"error": "Unauthorized"}
    }
  }'

# Now check dashboard:
# 1. Switch to "Error Analysis" tab
# 2. See the error in the list
# 3. Click it to see full details and fix suggestions
```

#### **Test API Diff Tab**

```bash
# Send an API diff event
curl -X POST http://localhost:5050/api/event \
  -H "Content-Type: application/json" \
  -d '{
    "type": "api_diff",
    "changes": [
      {
        "type": "removed",
        "path": "/api/v1/legacy-endpoint",
        "description": "Deprecated endpoint removed",
        "breaking": true,
        "recommendation": "Migrate to /api/v2/new-endpoint"
      },
      {
        "type": "added",
        "path": "/api/v2/new-feature",
        "description": "New feature endpoint added",
        "breaking": false,
        "recommendation": "Add tests for new endpoint"
      },
      {
        "type": "modified",
        "path": "/api/v1/users",
        "description": "Response field type changed from string to number",
        "breaking": true,
        "recommendation": "Update tests to expect number type"
      }
    ]
  }'

# Now check dashboard:
# 1. Switch to "API Diff" tab
# 2. See breaking vs non-breaking changes
# 3. Review recommendations
```

#### **Test Anomaly Detection Tab**

```bash
# Send an anomaly event (Response Time)
curl -X POST http://localhost:5050/api/event \
  -H "Content-Type: application/json" \
  -d '{
    "type": "anomaly",
    "endpoint": "/api/users",
    "severity": "critical",
    "type": "response_time",
    "description": "Response time is 5x higher than baseline",
    "expected": "100ms",
    "actual": "550ms"
  }'

# Send another anomaly (Error Rate)
curl -X POST http://localhost:5050/api/event \
  -H "Content-Type: application/json" \
  -d '{
    "type": "anomaly",
    "endpoint": "/api/orders",
    "severity": "high",
    "type": "error_rate",
    "description": "Error rate increased from 2% to 18%",
    "expected": "< 2%",
    "actual": "18%"
  }'

# Now check dashboard:
# 1. Switch to "Anomalies" tab
# 2. See critical (red) and high (orange) severity anomalies
# 3. View expected vs actual values
```

#### **Test Traffic Replay Tab**

```bash
# Send traffic events
curl -X POST http://localhost:5050/api/event \
  -H "Content-Type: application/json" \
  -d '{
    "type": "traffic",
    "method": "GET",
    "url": "https://api.example.com/users/123",
    "status_code": 200
  }'

curl -X POST http://localhost:5050/api/event \
  -H "Content-Type: application/json" \
  -d '{
    "type": "traffic",
    "method": "POST",
    "url": "https://api.example.com/orders",
    "status_code": 201
  }'

curl -X POST http://localhost:5050/api/event \
  -H "Content-Type: application/json" \
  -d '{
    "type": "traffic",
    "method": "DELETE",
    "url": "https://api.example.com/sessions/abc",
    "status_code": 204
  }'

# Now check dashboard:
# 1. Switch to "Traffic Replay" tab
# 2. See recorded requests with color-coded methods
# 3. Green (POST), Blue (GET), Red (DELETE)
```

---

### Method 3: Test with Backend Integration (Real Usage)

This is how it works in production - you call the functions from your backend code.

#### **Where to Add Code: `main.py`**

```python
# 1. Import the helper functions at the top of main.py
from dashboard_integration import (
    emit_healing_event,
    emit_error_analysis_event,
    emit_api_diff_event,
    emit_anomaly_event,
    emit_traffic_event
)

# 2. In POCOrchestrator.__init__, initialize the new modules
from src.self_healing import SelfHealingEngine
from src.error_analyzer import ErrorAnalyzer
from src.api_diff import APIDiffDetector
from src.anomaly_detector import AnomalyDetector
from src.traffic_replay import TrafficRecorder

class POCOrchestrator:
    def __init__(self):
        # ... existing code ...
        
        # Add these new modules
        self.healer = SelfHealingEngine()
        self.error_analyzer = ErrorAnalyzer()
        self.diff_detector = APIDiffDetector()
        self.anomaly_detector = AnomalyDetector()
        self.traffic_recorder = TrafficRecorder()
```

#### **Where to Add Self-Healing**

```python
# In main.py, in the test execution section
# Add after test failures are detected

def run_tests(self):
    # ... existing test execution code ...
    
    # When tests fail
    if test_failures:
        for failure in test_failures:
            # TRY TO HEAL THE TEST
            healing_result = self.healer.heal_test(
                test_file=failure['test_file'],
                test_name=failure['test_name'],
                error_message=failure['error_message']
            )
            
            # SEND TO DASHBOARD
            if healing_result and healing_result.get('success'):
                emit_healing_event(
                    test_name=failure['test_name'],
                    confidence=healing_result['confidence'],
                    old_code=healing_result['original_code'],
                    new_code=healing_result['healed_code']
                )
```

#### **Where to Add Error Analysis**

```python
# In main.py, after test failures
# Add alongside healing code

def run_tests(self):
    # ... existing code ...
    
    if test_failures:
        for failure in test_failures:
            # ANALYZE THE ERROR
            error_detail = self.error_analyzer.analyze_failure({
                'test_name': failure['test_name'],
                'error_type': failure['error_type'],
                'error_message': failure['error_message'],
                'traceback': failure['traceback']
            })
            
            # SEND TO DASHBOARD
            emit_error_analysis_event(
                test_name=error_detail.test_name,
                error_type=error_detail.error_type,
                message=error_detail.message,
                root_cause=error_detail.root_cause,
                suggestions=error_detail.suggestions,
                request_data=error_detail.request,
                response_data=error_detail.response
            )
```

#### **Where to Add API Diff**

```python
# In main.py, add a new method to compare specs

def compare_api_specs(self, old_spec_path, new_spec_path):
    """Compare two API specifications"""
    
    # DETECT DIFFERENCES
    changes = self.diff_detector.compare_specs(
        old_spec_path=old_spec_path,
        new_spec_path=new_spec_path
    )
    
    # SEND TO DASHBOARD
    if changes:
        emit_api_diff_event(changes=[
            {
                'type': change.change_type,
                'path': change.path,
                'description': change.description,
                'breaking': change.breaking,
                'recommendation': change.recommendation
            }
            for change in changes
        ])
    
    return changes

# Usage:
# python main.py --old-spec specs/api-v1.yaml --new-spec specs/api-v2.yaml --compare
```

#### **Where to Add Anomaly Detection**

```python
# In main.py, during test execution
# Add metrics tracking

def run_tests(self):
    # ... existing code ...
    
    for test in test_results:
        # CHECK RESPONSE TIME
        if test['response_time']:
            anomaly = self.anomaly_detector.detect_response_time_anomaly(
                endpoint=test['endpoint'],
                response_time=test['response_time']
            )
            
            if anomaly:
                emit_anomaly_event(
                    endpoint=anomaly.endpoint,
                    severity=anomaly.severity,
                    anomaly_type=anomaly.anomaly_type,
                    description=anomaly.description,
                    expected=anomaly.expected_value,
                    actual=anomaly.actual_value
                )
        
        # CHECK ERROR RATE
        if test['status_code'] >= 400:
            anomaly = self.anomaly_detector.detect_error_rate_anomaly(
                endpoint=test['endpoint']
            )
            
            if anomaly:
                emit_anomaly_event(
                    endpoint=anomaly.endpoint,
                    severity=anomaly.severity,
                    anomaly_type='error_rate',
                    description=anomaly.description,
                    expected=anomaly.expected_value,
                    actual=anomaly.actual_value
                )
```

#### **Where to Add Traffic Replay**

```python
# In main.py, when making API calls

def execute_api_request(self, method, url, **kwargs):
    """Execute API request and record traffic"""
    
    # MAKE THE REQUEST
    response = requests.request(method, url, **kwargs)
    
    # RECORD THE TRAFFIC
    self.traffic_recorder.record_request(
        method=method,
        url=url,
        headers=kwargs.get('headers', {}),
        body=kwargs.get('json', {}),
        status_code=response.status_code,
        response_body=response.json() if response.headers.get('content-type') == 'application/json' else response.text
    )
    
    # SEND TO DASHBOARD
    emit_traffic_event(
        method=method,
        url=url,
        status_code=response.status_code
    )
    
    return response
```

---

## 📂 File Locations - Where Everything Is

```
/Users/ehtesham/Developer/aadhaar-api-test-poc/

├── main.py                       👈 ADD INTEGRATION CODE HERE
│
├── dashboard/
│   ├── server.py                 ✅ Already works (no changes)
│   ├── index.html                ✅ Updated with tabs
│   ├── style.css                 ✅ Updated with styles
│   └── app.js                    ✅ Updated with handlers
│
├── src/
│   ├── self_healing.py          ✅ Backend ready
│   ├── error_analyzer.py        ✅ Backend ready
│   ├── api_diff.py              ✅ Backend ready
│   ├── anomaly_detector.py      ✅ Backend ready
│   └── traffic_replay.py        ✅ Backend ready
│
├── dashboard_integration.py      👈 IMPORT THESE FUNCTIONS
├── test_dashboard.py            👈 RUN THIS TO TEST
└── demo_features.py             👈 TEST BACKEND MODULES
```

---

## 🎬 Complete Test Scenarios

### Scenario 1: Test Everything Quickly

```bash
# Terminal 1
python dashboard/server.py

# Terminal 2
python test_dashboard.py

# Browser: http://localhost:5050
# Click each tab, see all features populated!
```

### Scenario 2: Test Self-Healing in Real Use

```bash
# 1. Create a failing test
cat > tests/test_example.py << 'EOF'
def test_api_endpoint():
    response = requests.get("https://httpbin.org/status/200")
    assert response.status_code == 201  # Wrong! Should be 200
EOF

# 2. Run main.py with healing enabled
python main.py --spec specs/api.yaml --heal

# 3. Watch dashboard: Self-Healing tab shows the fix
```

### Scenario 3: Test API Diff

```bash
# 1. Create two spec versions
cp specs/aadhaar-api.yaml specs/aadhaar-api-v1.yaml
# Edit specs/aadhaar-api.yaml to add/remove endpoints

# 2. Compare them
python -c "
from src.api_diff import APIDiffDetector
from dashboard_integration import emit_api_diff_event

detector = APIDiffDetector()
changes = detector.compare_specs(
    'specs/aadhaar-api-v1.yaml',
    'specs/aadhaar-api.yaml'
)
emit_api_diff_event(changes=[c.__dict__ for c in changes])
"

# 3. Check dashboard: API Diff tab shows changes
```

### Scenario 4: Test Anomaly Detection

```bash
# Run demo that simulates slow responses
python demo_features.py

# Or manually:
python -c "
from dashboard_integration import emit_anomaly_event

emit_anomaly_event(
    endpoint='/api/test',
    severity='critical',
    anomaly_type='response_time',
    description='API is 10x slower than normal',
    expected='50ms',
    actual='500ms'
)
"

# Check dashboard: Anomalies tab shows the issue
```

---

## 🎯 What You Should See

### After Running test_dashboard.py:

**Self-Healing Tab:**
- 3 healing operations
- Confidence scores: 95%, 88%, 72%
- Click any item to see code diff

**Error Analysis Tab:**
- 3 errors listed
- Click to see fix suggestions
- Request/response details visible

**API Diff Tab:**
- 5 changes total
- 2 breaking (red)
- 3 non-breaking (green)

**Anomalies Tab:**
- 4 anomalies
- 2 critical (red)
- 1 high (orange)
- 1 medium (blue)

**Traffic Replay Tab:**
- 10 recorded requests
- Different HTTP methods color-coded
- Status codes shown

**Overview Tab:**
- Your original metrics
- Activity log shows all events

---

## 🔍 How to Debug

If events don't appear:

```bash
# 1. Check dashboard is running
curl http://localhost:5050/api/health

# 2. Check event was received
curl -X POST http://localhost:5050/api/event \
  -H "Content-Type: application/json" \
  -d '{"type":"healing","test_name":"debug"}'

# 3. Check browser console (F12)
# Should see SSE connection and events

# 4. Check dashboard logs
# Terminal running server.py shows event broadcasts
```

---

## 📚 Summary

| Feature | What It Does | When You Use It | How to Test |
|---------|-------------|----------------|-------------|
| **Overview** | Shows existing pipeline metrics | Always running | Use main.py normally |
| **Self-Healing** | Auto-fixes broken tests | When tests fail due to API changes | Run test_dashboard.py or integrate in main.py |
| **Error Analysis** | Deep error breakdown | When any test fails | Run test_dashboard.py or analyze failures |
| **API Diff** | Compares API versions | Before deploying changes | Compare two spec files |
| **Anomaly Detection** | Finds unusual behavior | During execution monitoring | Track metrics, check thresholds |
| **Traffic Replay** | Records real requests | Generating tests from production | Record traffic, generate tests |

**Quick Test:** `python test_dashboard.py` - Tests ALL features in 10 seconds! ✨

**Production Use:** Add integration code to `main.py` as shown above.

**Need Help?** Check the comprehensive guides:
- `DASHBOARD_README.md` - Full integration guide
- `COMPLETE_SUMMARY.md` - Quick start
- `demo_features.py` - Backend module examples
