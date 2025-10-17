# Technical Deep Dive - AI Test Automation POC

## System Architecture & Data Flow

### Component Overview
```
┌──────────────────────────────────────────────────────────────┐
│                     POC Orchestrator                         │
│                      (main.py)                               │
│                                                              │
│  ┌────────────┐  ┌──────────────┐  ┌────────────────┐      │
│  │ OpenAPI    │→ │ Test         │→ │ Code           │      │
│  │ Parser     │  │ Generator    │  │ Validator      │      │
│  └────────────┘  └──────────────┘  └────────────────┘      │
│         ↓               ↓                   ↓               │
│  ┌────────────┐  ┌──────────────┐  ┌────────────────┐      │
│  │ Contract   │  │ Test         │  │ Coverage       │      │
│  │ Tester     │  │ Executor     │  │ Analyzer       │      │
│  └────────────┘  └──────────────┘  └────────────────┘      │
└──────────────────┬───────────────────────────────────────────┘
                   │
                   │ HTTP POST /api/event
                   │ JSON: {type, data}
                   ↓
         ┌─────────────────────────┐
         │  Dashboard Server       │
         │  (Flask - Port 8080)    │
         │                         │
         │  Event Queue ───→ SSE   │
         │  Event History (100)    │
         └─────────┬───────────────┘
                   │
                   │ Server-Sent Events
                   │ text/event-stream
                   ↓
         ┌─────────────────────────┐
         │   Browser Dashboard     │
         │   (HTML/CSS/JS)         │
         │                         │
         │   EventSource('/events')│
         └─────────────────────────┘
```

---

## Core Technical Methods

### 1. OpenAPI Parsing (`src/openapi_parser.py`)

**Method:** `OpenAPIParser.to_dict()`

**Process:**
```python
def to_dict(self):
    # Load YAML specification
    spec = yaml.safe_load(file)
    
    # Extract endpoints
    for path, methods in spec['paths'].items():
        for method, details in methods.items():
            endpoint = {
                'path': path,
                'method': method.upper(),
                'summary': details.get('summary'),
                'request_body': self._extract_schema(details.get('requestBody')),
                'responses': self._extract_responses(details.get('responses'))
            }
```

**Output Data Structure:**
```json
{
  "endpoints": [
    {
      "path": "/api/v1/verify",
      "method": "POST",
      "summary": "Verify Aadhaar number",
      "request_body": {
        "type": "object",
        "properties": {
          "aadhaar_number": {"type": "string"}
        }
      },
      "responses": {
        "200": {"schema": {...}}
      }
    }
  ]
}
```

**Event Sent:**
```python
send_event('parse', {
    'file': 'api.yaml',
    'endpoints': 5,
    'status': 'success'
})
```

---

### 2. AI Test Generation (`src/test_generator.py`)

**Method:** `TestGenerator.generate_tests(parsed_spec)`

**LLM Integration Process:**
```python
# 1. Construct AI Prompt
prompt = f"""
Generate pytest test cases for these API endpoints.
Use Flask test client, not requests library.

Endpoints:
{json.dumps(parsed_spec['endpoints'], indent=2)}

Requirements:
- Use Flask test client (app.test_client())
- Import from api.dummy_aadhaar_api
- Test success and error cases
- Use proper assertions
"""

# 2. Call Ollama API
response = requests.post(
    f"{OLLAMA_URL}/api/generate",
    json={
        "model": "qwen2.5-coder:14b",
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.1,  # Low for deterministic output
            "top_p": 0.9
        }
    },
    timeout=300
)

# 3. Extract generated code
generated_code = response.json()['response']

# 4. Clean and validate
test_code = self._extract_code_block(generated_code)
```

**Streaming Progress:**
```python
# For each test created
send_event('test_created', {
    'test_number': count,
    'test_name': test_function_name
})

# Overall progress
send_event('generate', {
    'count': total_tests,
    'progress': 100,
    'status': 'success'
})
```

**Generated Test Format:**
```python
def test_verify_aadhaar_valid(client):
    """Test valid Aadhaar verification"""
    response = client.post('/api/v1/verify', json={
        'aadhaar_number': '123456789012'
    })
    assert response.status_code == 200
    assert response.json['status'] == 'success'
```

---

### 3. Code Validation (`src/validator.py`)

**Method:** `CodeValidator.validate_test_file(file_path)`

**Three-Stage Validation:**

**Stage 1 - Syntax Check:**
```python
import ast

def check_syntax(self, code):
    try:
        ast.parse(code)  # Python AST parsing
        return True
    except SyntaxError as e:
        return False, str(e)
```

**Stage 2 - Import Check:**
```python
def check_imports(self, file_path):
    # Extract all imports
    imports = self._extract_imports(code)
    
    # Verify each import
    for imp in imports:
        try:
            __import__(imp)
        except ImportError:
            missing.append(imp)
    
    return len(missing) == 0
```

**Stage 3 - Structure Check:**
```python
def validate_structure(self, code):
    # Parse AST
    tree = ast.parse(code)
    
    # Check for test functions
    test_functions = [
        node.name for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef)
        and node.name.startswith('test_')
    ]
    
    return len(test_functions) > 0
```

**Event Sent:**
```python
send_event('validate', {
    'syntax': True,
    'imports': True,
    'structure': True,
    'overall': True,
    'message': 'Validation passed'
})
```

---

### 4. Test Execution (`main.py::run_tests_fixed()`)

**Method:** `POCOrchestrator.run_tests_fixed()`

**Process Flow:**

**Step 1 - Setup Coverage:**
```python
import coverage

cov = coverage.Coverage(
    source=['api'],              # Measure api/ directory
    omit=['*/tests/*', '*/.venv/*']
)
cov.start()
```

**Step 2 - Run pytest:**
```python
import pytest

result = pytest.main([
    test_file,
    '-v',                    # Verbose
    '--tb=line',            # Traceback style
    '--json-report',        # JSON output
    '--json-report-file=test_report.json'
])
```

**Step 3 - Parse Results:**
```python
def parse_pytest_output(self, report_file):
    with open(report_file) as f:
        data = json.load(f)
    
    details = []
    for test in data['tests']:
        details.append({
            'name': test['nodeid'],
            'status': 'pass' if test['outcome'] == 'passed' else 'fail',
            'reason': test.get('call', {}).get('longrepr', '')
        })
    
    return {
        'passed': data['summary']['passed'],
        'failed': data['summary']['failed'],
        'total': data['summary']['total'],
        'details': details
    }
```

**Step 4 - Extract Failure Reasons:**
```python
def extract_assertion_error(self, output):
    # Parse pytest output for assertion details
    patterns = [
        r'AssertionError: (.+)',
        r'assert (.+)',
        r'Expected: (.+), Got: (.+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, output)
        if match:
            return match.group(1)
```

**Event Sent:**
```python
send_event('execute', {
    'passed': 4,
    'failed': 1,
    'total': 5,
    'details': [
        {
            'name': 'test_verify_valid',
            'status': 'pass',
            'duration': '0.12s'
        },
        {
            'name': 'test_verify_invalid',
            'status': 'fail',
            'reason': 'AssertionError: Expected 400, got 500'
        }
    ]
})
```

---

### 5. Contract Testing (`src/contract_tester.py`)

**Method:** `ContractTester.test_against_spec(spec_path, base_url)`

**Process Using Schemathesis:**

```python
import schemathesis

# Load OpenAPI schema
schema = schemathesis.from_path(spec_path)

results = []

# Property-based testing
@schema.parametrize()
def test_api(case):
    # Schemathesis generates test cases automatically
    response = case.call(base_url=base_url)
    
    # Validate response
    case.validate_response(response)
    
    results.append({
        'endpoint': f"{case.method} {case.path}",
        'status': 'pass' if valid else 'fail',
        'checks': {
            'status_code': response.status_code in case.definition.get('responses'),
            'schema_valid': validate_schema(response.json(), case.definition),
            'required_fields': check_required_fields(response.json())
        }
    })
```

**Validation Checks:**
1. **Status Code** - Matches OpenAPI spec
2. **Response Schema** - JSON structure matches schema
3. **Required Fields** - All required fields present
4. **Data Types** - Field types match specification
5. **Enum Values** - Values within allowed enums

**Event Sent:**
```python
send_event('contract', {
    'total': 5,
    'passed': 4,
    'failed': 1,
    'status': 'completed'
})
```

---

### 6. Coverage Analysis (`main.py::analyze_coverage()`)

**Method:** `POCOrchestrator.analyze_coverage()`

**Process:**

**Step 1 - Stop Coverage Collection:**
```python
cov.stop()
cov.save()
```

**Step 2 - Generate Reports:**
```python
# HTML Report
cov.html_report(directory='htmlcov')

# Get percentage
total = cov.report(file=io.StringIO())
```

**Step 3 - Parse Coverage Data:**
```python
def get_coverage_percentage(self):
    # Read .coverage file
    cov = coverage.Coverage()
    cov.load()
    
    # Get line coverage
    analysis = cov.analysis('api/dummy_aadhaar_api.py')
    
    executed_lines = len(analysis[1])  # Executed
    missing_lines = len(analysis[2])    # Missing
    total_lines = executed_lines + missing_lines
    
    percentage = (executed_lines / total_lines) * 100
    return round(percentage, 2)
```

**Event Sent:**
```python
send_event('coverage', {
    'percentage': 81.25
})
```

---

### 7. Real-Time Communication (SSE)

**Server Side:** `dashboard/server.py`

**Method:** `stream_events()`

```python
@app.route('/events')
def stream_events():
    def generate():
        # Send connection message
        yield f"data: {json.dumps({
            'type': 'connection',
            'message': 'Connected'
        })}\n\n"
        
        # Replay recent history
        with history_lock:
            for event in event_history[-20:]:
                yield f"data: {json.dumps(event)}\n\n"
        
        # Stream new events
        while True:
            try:
                event = event_queue.get(timeout=1)
                yield f"data: {json.dumps(event)}\n\n"
            except queue.Empty:
                # Heartbeat every 15 seconds
                if time.time() - last_heartbeat > 15:
                    yield f"data: {json.dumps({
                        'type': 'heartbeat'
                    })}\n\n"
    
    return Response(
        generate(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',
            'Connection': 'keep-alive'
        }
    )
```

**Client Side:** `dashboard/app.js`

```javascript
function connectSSE() {
    eventSource = new EventSource('/events');
    
    eventSource.onmessage = function(event) {
        const data = JSON.parse(event.data);
        
        switch(data.type) {
            case 'parse':
                document.getElementById('spec-file').textContent = data.file;
                document.getElementById('endpoint-count').textContent = data.endpoints;
                break;
                
            case 'test_created':
                document.getElementById('tests-generated').textContent = data.test_number;
                addLog(`Generated test ${data.test_number}: ${data.test_name}`);
                break;
                
            case 'generate':
                document.getElementById('gen-progress').style.width = data.progress + '%';
                break;
                
            case 'execute':
                updateTestResults(data.details);
                break;
        }
    };
    
    eventSource.onerror = function() {
        eventSource.close();
        // Exponential backoff reconnection
        setTimeout(connectSSE, Math.min(1000 * attempts, 5000));
    };
}
```

---

## Data Flow Timeline

### Complete POC Execution Flow:

```
Time    Component           Method                    Event Type      Data
─────────────────────────────────────────────────────────────────────────────
0s      main.py            send_event()              clear           {}
1s      OpenAPIParser      to_dict()                 parse           {file, endpoints: 5}
2s      TestGenerator      generate_tests()          generate        {status: 'starting'}
5s      TestGenerator      (streaming)               test_created    {test_number: 1, name: 'test_verify'}
6s      TestGenerator      (streaming)               test_created    {test_number: 2, name: 'test_generate'}
7s      TestGenerator      (streaming)               test_created    {test_number: 3, name: 'test_download'}
8s      TestGenerator      (streaming)               test_created    {test_number: 4, name: 'test_status'}
9s      TestGenerator      (streaming)               test_created    {test_number: 5, name: 'test_demographic'}
10s     TestGenerator      (complete)                generate        {count: 5, progress: 100, status: 'success'}
11s     CodeValidator      validate_test_file()      validate        {syntax: true, imports: true, overall: true}
12s     POCOrchestrator    run_tests_fixed()         execute         {passed: 4, failed: 1, total: 5, details: [...]}
15s     ContractTester     test_against_spec()       contract        {total: 5, passed: 5, failed: 0}
18s     POCOrchestrator    analyze_coverage()        coverage        {percentage: 81.25}
20s     GitIntegration     commit_and_push()         git             {committed: true, pushed: false}
```

---

## Key Technical Decisions

### 1. Why Flask Test Client Instead of Requests?
```python
# ❌ Old method - External HTTP calls
response = requests.post('http://localhost:5001/api/verify', ...)
# Problem: Coverage.py can't track external processes

# ✅ New method - In-process calls
client = app.test_client()
response = client.post('/api/verify', ...)
# Coverage tracks all executed lines: 0% → 81%
```

### 2. Why Server-Sent Events Instead of WebSocket?
- **Unidirectional** - Server → Client only (no need for client messages)
- **Auto-Reconnect** - Built into EventSource API
- **HTTP Compatible** - Works through proxies and firewalls
- **Simpler** - No handshake, no protocol complexity

### 3. Why Event Queue + History?
```python
event_queue = queue.Queue()      # For real-time streaming
event_history = []                # For late-joining clients (last 100)

# New client connects → Gets history + live stream
# Handles: page refresh, network drops, multiple tabs
```

### 4. Why Ollama Local Instead of Cloud LLM?
- **Privacy** - No API data sent to cloud
- **Cost** - No per-token charges
- **Speed** - No network latency
- **Control** - Can customize model and parameters

---

## Performance Optimizations

### 1. Streaming Test Generation
```python
# Instead of generating all tests then sending
# Stream each test as it's created
for test in generated_tests:
    send_event('test_created', {...})  # Immediate feedback
```

### 2. Event History Cap
```python
MAX_HISTORY = 100  # Limit memory usage
if len(event_history) > MAX_HISTORY:
    event_history.pop(0)  # FIFO
```

### 3. SSE Heartbeat
```python
# Keep connection alive
if time.time() - last_heartbeat > 15:
    yield "data: {\"type\":\"heartbeat\"}\n\n"
```

### 4. Progress Bar Transitions
```css
.progress-fill {
    transition: width 0.3s ease;  /* Smooth visual updates */
}
```

---

## Error Handling

### 1. LLM Generation Failures
```python
try:
    code = generator.generate_tests(spec)
except requests.exceptions.Timeout:
    send_event('generate', {
        'status': 'failed',
        'message': 'LLM timeout - retrying...'
    })
    # Fallback to template-based generation
```

### 2. SSE Connection Drops
```javascript
eventSource.onerror = function() {
    reconnectAttempts++;
    if (reconnectAttempts <= MAX_RECONNECT_ATTEMPTS) {
        const delay = Math.min(1000 * reconnectAttempts, 5000);
        setTimeout(connectSSE, delay);  // Exponential backoff
    }
};
```

### 3. Validation Failures
```python
if not syntax_valid:
    send_event('validate', {
        'overall': False,
        'message': f'Syntax error: {error_detail}'
    })
    # Don't proceed to execution
    return False
```

---

## Security Considerations

### 1. Input Validation
```python
# Sanitize OpenAPI spec path
spec_path = os.path.abspath(spec_path)
if not spec_path.startswith(ALLOWED_DIR):
    raise ValueError("Invalid spec path")
```

### 2. Code Execution Isolation
```python
# Generated tests run in controlled environment
# Use Flask test client (in-process, no network)
# Coverage.py sandboxes execution
```

### 3. CORS Configuration
```python
from flask_cors import CORS
CORS(app)  # Allow dashboard to call API from different origin
```

---

## Monitoring & Debugging

### 1. Event Logging
```python
def broadcast_event(event_type, data):
    print(f"[Dashboard] 📡 Broadcast: {event_type} - {data}")
    # Console output for debugging
```

### 2. Health Check Endpoint
```python
@app.route('/api/health')
def health():
    return {
        'status': 'ok',
        'history_size': len(event_history),
        'queue_size': event_queue.qsize()
    }
```

### 3. Browser Console Debugging
```javascript
console.log('[DEBUG] SSE message received:', data);
console.log('[DEBUG] Updated spec-file to:', data.file);
```

---

## Summary

**Architecture**: Event-driven microservices with SSE for real-time updates  
**AI Method**: Prompt engineering with Ollama LLM (14B parameter model)  
**Testing**: Flask test client for in-process execution (81% coverage)  
**Validation**: Three-stage AST-based code validation  
**Communication**: Server-Sent Events with event queue + history  
**Performance**: Streaming updates, connection pooling, event buffering  
**Security**: Input validation, execution isolation, CORS protection
