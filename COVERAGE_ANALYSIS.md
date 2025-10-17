# Code Coverage Analysis & Improvement Strategy

## Current Coverage Status

**Overall Coverage: 81% (77 statements, 15 missed)**

### Coverage Report:
```
Name                       Stmts   Miss  Cover   Missing Lines
------------------------------------------------------------
api/dummy_aadhaar_api.py      77     15    81%   30, 35, 43, 51, 56, 69, 81, 95-97, 120, 125, 137, 140-141
```

---

## What is Code Coverage?

### Definition
**Code Coverage** measures which lines of code are executed during test runs.

### Types of Coverage:

1. **Statement Coverage** (What we measure)
   - Percentage of code statements executed
   - Current: 81% (62 out of 77 lines executed)

2. **Branch Coverage** (More advanced)
   - Percentage of decision branches executed
   - Example: Both `if` and `else` paths tested

3. **Function Coverage**
   - Percentage of functions called
   - Current: ~86% (6 out of 7 endpoints + 1 helper)

4. **Line Coverage**
   - Similar to statement coverage
   - Counts executable lines

### Formula:
```
Coverage % = (Executed Lines / Total Executable Lines) × 100
Coverage % = (62 / 77) × 100 = 81%
```

---

## Missing Lines Analysis

### Line-by-Line Breakdown:

```python
# Line 30: Invalid Aadhaar error in verify_aadhaar()
return jsonify({"status": "invalid", "error": "Aadhaar must be 12 digits"}), 400

# Line 35: Aadhaar not found error in verify_aadhaar()
return jsonify({"status": "invalid", "error": "Aadhaar not found in database"}), 400

# Line 43: Missing aadhaar_number in get_demographics()
return jsonify({"error": "aadhaar_number is required"}), 400

# Line 51: Invalid Aadhaar format in get_demographics()
return jsonify({"error": "Invalid Aadhaar format"}), 400

# Line 56: Aadhaar not found in get_demographics()
return jsonify({"error": "Aadhaar not found"}), 400

# Line 69: Invalid Aadhaar format in generate_otp()
return jsonify({"error": "Invalid Aadhaar format"}), 400

# Line 81: Aadhaar not found in generate_otp()
return jsonify({"error": "Aadhaar not found"}), 400

# Line 95-97: Invalid/expired OTP in verify_otp()
return jsonify({"error": "Invalid or expired OTP"}), 400

# Line 120: Missing consent in ekyc_auth()
return jsonify({"error": "Consent is required"}), 403

# Line 125: Invalid Aadhaar format in ekyc_auth()
return jsonify({"error": "Invalid Aadhaar format"}), 400

# Line 137: Authentication failed in ekyc_auth()
return jsonify({"error": "Authentication failed or Aadhaar not found"}), 400

# Line 140-141: Main block (if __name__ == '__main__')
print("Starting Dummy Aadhaar API on http://localhost:5001")
app.run(host='0.0.0.0', port=5001, debug=True)
```

---

## Why These Lines Are Missed

### 1. **Error Paths Not Tested** (Lines 30, 35, 43, 51, 56, 69, 81, 95-97, 120, 125, 137)
**Reason:** Current tests only cover "happy path" (successful scenarios)

**Example - Current Test:**
```python
def test_verify_aadhaar_valid(client):
    # Only tests success case
    response = client.post('/api/v1/aadhaar/verify', 
                          json={'aadhaar_number': '123456789012'})
    assert response.status_code == 200
```

**Missing Tests:**
- Invalid format: `'12345'` (less than 12 digits)
- Not found: `'999999999999'` (not in database)
- Missing parameter: `{}` (no aadhaar_number)
- Invalid characters: `'12345678901a'` (non-numeric)

### 2. **Main Block Not Executed** (Lines 140-141)
**Reason:** Tests use `app.test_client()`, not `app.run()`

**Explanation:**
```python
if __name__ == '__main__':  # False when imported in tests
    app.run()  # Never executed during testing
```

---

## Improvement Strategy

### Goal: 81% → 95%+ Coverage

### Phase 1: Add Error Case Tests (Target: 90%)

#### 1. **verify_aadhaar() Error Cases**

```python
# Test invalid format
def test_verify_aadhaar_invalid_format(client):
    """Test Aadhaar with invalid format"""
    response = client.post('/api/v1/aadhaar/verify', 
                          json={'aadhaar_number': '12345'})  # Only 5 digits
    assert response.status_code == 400
    assert response.json['error'] == "Aadhaar must be 12 digits"

# Test not found
def test_verify_aadhaar_not_found(client):
    """Test Aadhaar not in database"""
    response = client.post('/api/v1/aadhaar/verify', 
                          json={'aadhaar_number': '999999999999'})
    assert response.status_code == 400
    assert response.json['error'] == "Aadhaar not found in database"

# Test missing parameter
def test_verify_aadhaar_missing_param(client):
    """Test missing aadhaar_number"""
    response = client.post('/api/v1/aadhaar/verify', json={})
    assert response.status_code == 400
    assert response.json['error'] == "aadhaar_number is required"

# Test non-numeric
def test_verify_aadhaar_non_numeric(client):
    """Test Aadhaar with letters"""
    response = client.post('/api/v1/aadhaar/verify', 
                          json={'aadhaar_number': '12345678901a'})
    assert response.status_code == 400
    assert response.json['error'] == "Aadhaar must be 12 digits"
```

#### 2. **get_demographics() Error Cases**

```python
def test_demographics_missing_aadhaar(client):
    """Test missing aadhaar_number"""
    response = client.post('/api/v1/aadhaar/demographics', 
                          json={'consent': True})
    assert response.status_code == 400

def test_demographics_missing_consent(client):
    """Test missing consent"""
    response = client.post('/api/v1/aadhaar/demographics', 
                          json={'aadhaar_number': '123456789012'})
    assert response.status_code == 403

def test_demographics_invalid_format(client):
    """Test invalid Aadhaar format"""
    response = client.post('/api/v1/aadhaar/demographics', 
                          json={'aadhaar_number': 'invalid', 'consent': True})
    assert response.status_code == 400

def test_demographics_not_found(client):
    """Test Aadhaar not found"""
    response = client.post('/api/v1/aadhaar/demographics', 
                          json={'aadhaar_number': '999999999999', 'consent': True})
    assert response.status_code == 400
```

#### 3. **generate_otp() Error Cases**

```python
def test_generate_otp_invalid_format(client):
    """Test OTP generation with invalid Aadhaar"""
    response = client.post('/api/v1/aadhaar/otp/generate', 
                          json={'aadhaar_number': '12345'})
    assert response.status_code == 400

def test_generate_otp_not_found(client):
    """Test OTP generation for non-existent Aadhaar"""
    response = client.post('/api/v1/aadhaar/otp/generate', 
                          json={'aadhaar_number': '999999999999'})
    assert response.status_code == 400
```

#### 4. **verify_otp() Error Cases**

```python
def test_verify_otp_invalid(client):
    """Test OTP verification with wrong OTP"""
    # First generate OTP
    gen_response = client.post('/api/v1/aadhaar/otp/generate', 
                               json={'aadhaar_number': '123456789012'})
    txn_id = gen_response.json['transaction_id']
    
    # Try wrong OTP
    response = client.post('/api/v1/aadhaar/otp/verify', 
                          json={'transaction_id': txn_id, 'otp': '999999'})
    assert response.status_code == 400
    assert 'Invalid or expired OTP' in response.json['error']

def test_verify_otp_expired(client):
    """Test OTP verification with expired transaction"""
    response = client.post('/api/v1/aadhaar/otp/verify', 
                          json={'transaction_id': 'INVALID', 'otp': '123456'})
    assert response.status_code == 400
```

#### 5. **ekyc_auth() Error Cases**

```python
def test_ekyc_missing_consent(client):
    """Test eKYC without consent"""
    response = client.post('/api/v1/aadhaar/ekyc', 
                          json={
                              'aadhaar_number': '123456789012',
                              'transaction_id': 'TXN123456'
                          })
    assert response.status_code == 403

def test_ekyc_invalid_format(client):
    """Test eKYC with invalid Aadhaar format"""
    response = client.post('/api/v1/aadhaar/ekyc', 
                          json={
                              'aadhaar_number': 'invalid',
                              'transaction_id': 'TXN123456',
                              'consent': True
                          })
    assert response.status_code == 400

def test_ekyc_auth_failed(client):
    """Test eKYC with mismatched transaction"""
    response = client.post('/api/v1/aadhaar/ekyc', 
                          json={
                              'aadhaar_number': '123456789012',
                              'transaction_id': 'WRONG',
                              'consent': True
                          })
    assert response.status_code == 400
```

---

### Phase 2: Ignore Main Block (Target: 93%)

**Option 1: Add coverage pragma**
```python
if __name__ == '__main__':  # pragma: no cover
    print("Starting Dummy Aadhaar API on http://localhost:5001")
    app.run(host='0.0.0.0', port=5001, debug=True)
```

**Option 2: Update .coveragerc**
```ini
[run]
omit = 
    */tests/*
    */__main__.py

[report]
exclude_lines =
    pragma: no cover
    if __name__ == .__main__.:
```

---

### Phase 3: Branch Coverage (Target: 95%+)

Add tests for all conditional branches:

```python
# Test both valid and invalid for each validation
# Test both success and error for each endpoint
# Test both present and missing for each required field
```

---

## Complete Test File with All Error Cases

### Create: `tests/test_aadhaar_api_complete.py`

```python
import pytest
from api.dummy_aadhaar_api import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

# ============= VERIFY AADHAAR =============

def test_verify_aadhaar_valid(client):
    """Test valid Aadhaar verification"""
    response = client.post('/api/v1/aadhaar/verify', 
                          json={'aadhaar_number': '123456789012'})
    assert response.status_code == 200
    assert response.json['status'] == 'valid'

def test_verify_aadhaar_missing_param(client):
    """Test missing aadhaar_number parameter"""
    response = client.post('/api/v1/aadhaar/verify', json={})
    assert response.status_code == 400
    assert 'aadhaar_number is required' in response.json['error']

def test_verify_aadhaar_invalid_format_short(client):
    """Test Aadhaar with less than 12 digits"""
    response = client.post('/api/v1/aadhaar/verify', 
                          json={'aadhaar_number': '12345'})
    assert response.status_code == 400
    assert 'must be 12 digits' in response.json['error']

def test_verify_aadhaar_invalid_format_long(client):
    """Test Aadhaar with more than 12 digits"""
    response = client.post('/api/v1/aadhaar/verify', 
                          json={'aadhaar_number': '1234567890123'})
    assert response.status_code == 400

def test_verify_aadhaar_invalid_format_letters(client):
    """Test Aadhaar with non-numeric characters"""
    response = client.post('/api/v1/aadhaar/verify', 
                          json={'aadhaar_number': '12345678901a'})
    assert response.status_code == 400

def test_verify_aadhaar_not_found(client):
    """Test Aadhaar not in database"""
    response = client.post('/api/v1/aadhaar/verify', 
                          json={'aadhaar_number': '999999999999'})
    assert response.status_code == 400
    assert 'not found in database' in response.json['error']

# ============= DEMOGRAPHICS =============

def test_demographics_valid(client):
    """Test getting demographics with valid data"""
    response = client.post('/api/v1/aadhaar/demographics', 
                          json={
                              'aadhaar_number': '123456789012',
                              'consent': True
                          })
    assert response.status_code == 200
    assert 'name' in response.json

def test_demographics_missing_aadhaar(client):
    """Test demographics without aadhaar_number"""
    response = client.post('/api/v1/aadhaar/demographics', 
                          json={'consent': True})
    assert response.status_code == 400
    assert 'aadhaar_number is required' in response.json['error']

def test_demographics_missing_consent(client):
    """Test demographics without consent"""
    response = client.post('/api/v1/aadhaar/demographics', 
                          json={'aadhaar_number': '123456789012'})
    assert response.status_code == 403
    assert 'Consent is required' in response.json['error']

def test_demographics_consent_false(client):
    """Test demographics with consent=false"""
    response = client.post('/api/v1/aadhaar/demographics', 
                          json={
                              'aadhaar_number': '123456789012',
                              'consent': False
                          })
    assert response.status_code == 403

def test_demographics_invalid_format(client):
    """Test demographics with invalid Aadhaar format"""
    response = client.post('/api/v1/aadhaar/demographics', 
                          json={
                              'aadhaar_number': 'invalid',
                              'consent': True
                          })
    assert response.status_code == 400
    assert 'Invalid Aadhaar format' in response.json['error']

def test_demographics_not_found(client):
    """Test demographics for non-existent Aadhaar"""
    response = client.post('/api/v1/aadhaar/demographics', 
                          json={
                              'aadhaar_number': '999999999999',
                              'consent': True
                          })
    assert response.status_code == 400
    assert 'Aadhaar not found' in response.json['error']

# ============= GENERATE OTP =============

def test_generate_otp_valid(client):
    """Test OTP generation with valid Aadhaar"""
    response = client.post('/api/v1/aadhaar/otp/generate', 
                          json={'aadhaar_number': '123456789012'})
    assert response.status_code == 200
    assert 'transaction_id' in response.json

def test_generate_otp_missing_param(client):
    """Test OTP generation without aadhaar_number"""
    response = client.post('/api/v1/aadhaar/otp/generate', json={})
    assert response.status_code == 400

def test_generate_otp_invalid_format(client):
    """Test OTP generation with invalid format"""
    response = client.post('/api/v1/aadhaar/otp/generate', 
                          json={'aadhaar_number': '12345'})
    assert response.status_code == 400
    assert 'Invalid Aadhaar format' in response.json['error']

def test_generate_otp_not_found(client):
    """Test OTP generation for non-existent Aadhaar"""
    response = client.post('/api/v1/aadhaar/otp/generate', 
                          json={'aadhaar_number': '999999999999'})
    assert response.status_code == 400
    assert 'Aadhaar not found' in response.json['error']

# ============= VERIFY OTP =============

def test_verify_otp_valid(client):
    """Test OTP verification with correct OTP"""
    # Generate OTP first
    gen_response = client.post('/api/v1/aadhaar/otp/generate', 
                               json={'aadhaar_number': '123456789012'})
    txn_id = gen_response.json['transaction_id']
    
    # Verify with correct OTP
    response = client.post('/api/v1/aadhaar/otp/verify', 
                          json={
                              'transaction_id': txn_id,
                              'otp': '123456'
                          })
    assert response.status_code == 200
    assert response.json['status'] == 'success'

def test_verify_otp_missing_params(client):
    """Test OTP verification without required params"""
    response = client.post('/api/v1/aadhaar/otp/verify', json={})
    assert response.status_code == 400
    assert 'transaction_id and otp are required' in response.json['error']

def test_verify_otp_invalid(client):
    """Test OTP verification with wrong OTP"""
    gen_response = client.post('/api/v1/aadhaar/otp/generate', 
                               json={'aadhaar_number': '123456789012'})
    txn_id = gen_response.json['transaction_id']
    
    response = client.post('/api/v1/aadhaar/otp/verify', 
                          json={
                              'transaction_id': txn_id,
                              'otp': '999999'
                          })
    assert response.status_code == 400
    assert 'Invalid or expired OTP' in response.json['error']

def test_verify_otp_expired_transaction(client):
    """Test OTP verification with non-existent transaction"""
    response = client.post('/api/v1/aadhaar/otp/verify', 
                          json={
                              'transaction_id': 'INVALID',
                              'otp': '123456'
                          })
    assert response.status_code == 400

# ============= EKYC =============

def test_ekyc_valid(client):
    """Test eKYC with valid data"""
    response = client.post('/api/v1/aadhaar/ekyc', 
                          json={
                              'aadhaar_number': '123456789012',
                              'transaction_id': 'TXN123456',
                              'consent': True
                          })
    assert response.status_code == 200
    assert response.json['status'] == 'success'

def test_ekyc_missing_params(client):
    """Test eKYC without required parameters"""
    response = client.post('/api/v1/aadhaar/ekyc', json={})
    assert response.status_code == 400

def test_ekyc_missing_consent(client):
    """Test eKYC without consent"""
    response = client.post('/api/v1/aadhaar/ekyc', 
                          json={
                              'aadhaar_number': '123456789012',
                              'transaction_id': 'TXN123456'
                          })
    assert response.status_code == 403
    assert 'Consent is required' in response.json['error']

def test_ekyc_consent_false(client):
    """Test eKYC with consent=false"""
    response = client.post('/api/v1/aadhaar/ekyc', 
                          json={
                              'aadhaar_number': '123456789012',
                              'transaction_id': 'TXN123456',
                              'consent': False
                          })
    assert response.status_code == 403

def test_ekyc_invalid_format(client):
    """Test eKYC with invalid Aadhaar format"""
    response = client.post('/api/v1/aadhaar/ekyc', 
                          json={
                              'aadhaar_number': 'invalid',
                              'transaction_id': 'TXN123456',
                              'consent': True
                          })
    assert response.status_code == 400
    assert 'Invalid Aadhaar format' in response.json['error']

def test_ekyc_auth_failed(client):
    """Test eKYC with wrong transaction"""
    response = client.post('/api/v1/aadhaar/ekyc', 
                          json={
                              'aadhaar_number': '123456789012',
                              'transaction_id': 'WRONG',
                              'consent': True
                          })
    assert response.status_code == 400
    assert 'Authentication failed' in response.json['error']

def test_ekyc_not_found(client):
    """Test eKYC with non-existent Aadhaar"""
    response = client.post('/api/v1/aadhaar/ekyc', 
                          json={
                              'aadhaar_number': '999999999999',
                              'transaction_id': 'TXN999999',
                              'consent': True
                          })
    assert response.status_code == 400

# ============= HEALTH CHECK =============

def test_health_check(client):
    """Test health check endpoint"""
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json['status'] == 'healthy'
```

---

## Expected Coverage After Implementation

### Before:
```
Coverage: 81% (62/77 lines)
Missing: 15 lines
```

### After Adding Error Tests:
```
Coverage: 95% (73/77 lines)
Missing: 4 lines (main block only)
```

### After Adding Pragma:
```
Coverage: 97% (73/75 lines)
Missing: 2 lines (excluded from coverage)
```

---

## How to Run and Verify

### Step 1: Run Tests with Coverage
```bash
cd /Users/ehtesham/Developer/aadhaar-api-test-poc
source .venv/bin/activate
pytest tests/test_aadhaar_api_complete.py -v --cov=api --cov-report=html --cov-report=term-missing
```

### Step 2: View HTML Report
```bash
open htmlcov/index.html
```

### Step 3: Check Specific File
```bash
coverage report --show-missing
```

---

## Coverage Improvement Checklist

- [ ] Add all error case tests (30+ new tests)
- [ ] Test invalid input formats
- [ ] Test missing required parameters
- [ ] Test not-found scenarios
- [ ] Test unauthorized access (403 errors)
- [ ] Add pragma to main block
- [ ] Run coverage report
- [ ] Verify 95%+ coverage
- [ ] Generate HTML report
- [ ] Update CI/CD pipeline

---

## Key Metrics After Improvement

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| **Coverage** | 81% | 95%+ | +14% |
| **Tested Lines** | 62 | 73 | +11 |
| **Missing Lines** | 15 | 2-4 | -11 to -13 |
| **Test Count** | ~7 | ~35 | +28 |
| **Error Paths** | 20% | 95% | +75% |

---

## Benefits of Higher Coverage

✅ **Confidence** - Know error handling works  
✅ **Bug Prevention** - Catch edge cases early  
✅ **Regression Safety** - Tests catch breaking changes  
✅ **Documentation** - Tests show all API behaviors  
✅ **Maintainability** - Easier to refactor with confidence  

---

## Next Steps

1. **Create complete test file** with all error cases
2. **Run coverage** and verify 95%+
3. **Update POC** to generate error case tests with AI
4. **Add to CI/CD** - Fail builds if coverage drops below 90%
5. **Dashboard** - Show coverage breakdown by endpoint

---

## Conclusion

**Current 81% coverage is GOOD, but can be improved to 95%+ by:**
1. Adding error case tests (all 15 missing lines)
2. Excluding main block with pragma
3. Testing all branches (if/else paths)

**The missing 19% represents untested error handling - critical for production APIs!**
