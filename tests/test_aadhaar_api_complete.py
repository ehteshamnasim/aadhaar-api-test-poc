"""
Comprehensive test suite for Aadhaar API
Achieves 95%+ code coverage by testing all error paths
"""
import pytest
from api.dummy_aadhaar_api import app

@pytest.fixture
def client():
    """Flask test client fixture"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


# ============================================================================
# VERIFY AADHAAR ENDPOINT - /api/v1/aadhaar/verify
# ============================================================================

def test_verify_aadhaar_valid_success(client):
    """Test valid Aadhaar verification - Happy path"""
    response = client.post('/api/v1/aadhaar/verify', 
                          json={'aadhaar_number': '123456789012'})
    assert response.status_code == 200
    assert response.json['status'] == 'valid'
    assert 'message' in response.json


def test_verify_aadhaar_missing_parameter(client):
    """Test verify endpoint with missing aadhaar_number"""
    response = client.post('/api/v1/aadhaar/verify', json={})
    assert response.status_code == 400
    assert 'aadhaar_number is required' in response.json['error']


def test_verify_aadhaar_no_json_body(client):
    """Test verify endpoint without JSON body"""
    response = client.post('/api/v1/aadhaar/verify')
    assert response.status_code == 415  # Flask returns 415 for missing Content-Type: application/json


def test_verify_aadhaar_invalid_format_short(client):
    """Test Aadhaar with less than 12 digits"""
    response = client.post('/api/v1/aadhaar/verify', 
                          json={'aadhaar_number': '12345'})
    assert response.status_code == 400
    assert 'must be 12 digits' in response.json['error']


def test_verify_aadhaar_invalid_format_long(client):
    """Test Aadhaar with more than 12 digits"""
    response = client.post('/api/v1/aadhaar/verify', 
                          json={'aadhaar_number': '1234567890123456'})
    assert response.status_code == 400
    assert 'must be 12 digits' in response.json['error']


def test_verify_aadhaar_invalid_format_letters(client):
    """Test Aadhaar with non-numeric characters"""
    response = client.post('/api/v1/aadhaar/verify', 
                          json={'aadhaar_number': '12345678901a'})
    assert response.status_code == 400
    assert 'must be 12 digits' in response.json['error']


def test_verify_aadhaar_invalid_format_special_chars(client):
    """Test Aadhaar with special characters"""
    response = client.post('/api/v1/aadhaar/verify', 
                          json={'aadhaar_number': '1234-5678-90'})
    assert response.status_code == 400


def test_verify_aadhaar_not_found(client):
    """Test Aadhaar not in database"""
    response = client.post('/api/v1/aadhaar/verify', 
                          json={'aadhaar_number': '999999999999'})
    assert response.status_code == 400
    assert 'not found in database' in response.json['error']


def test_verify_aadhaar_second_valid(client):
    """Test verification with second valid Aadhaar"""
    response = client.post('/api/v1/aadhaar/verify', 
                          json={'aadhaar_number': '987654321098'})
    assert response.status_code == 200
    assert response.json['status'] == 'valid'


# ============================================================================
# DEMOGRAPHICS ENDPOINT - /api/v1/aadhaar/demographics
# ============================================================================

def test_demographics_valid_success(client):
    """Test getting demographics with valid data"""
    response = client.post('/api/v1/aadhaar/demographics', 
                          json={
                              'aadhaar_number': '123456789012',
                              'consent': True
                          })
    assert response.status_code == 200
    assert 'name' in response.json
    assert 'dob' in response.json
    assert 'gender' in response.json


def test_demographics_missing_aadhaar(client):
    """Test demographics without aadhaar_number"""
    response = client.post('/api/v1/aadhaar/demographics', 
                          json={'consent': True})
    assert response.status_code == 400
    assert 'aadhaar_number is required' in response.json['error']


def test_demographics_no_json_body(client):
    """Test demographics without JSON body"""
    response = client.post('/api/v1/aadhaar/demographics')
    assert response.status_code == 415  # Flask returns 415 for missing Content-Type: application/json


def test_demographics_missing_consent(client):
    """Test demographics without consent field"""
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
    assert 'Consent is required' in response.json['error']


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


def test_demographics_second_valid_aadhaar(client):
    """Test demographics with second valid Aadhaar"""
    response = client.post('/api/v1/aadhaar/demographics', 
                          json={
                              'aadhaar_number': '987654321098',
                              'consent': True
                          })
    assert response.status_code == 200
    assert response.json['gender'] == 'F'


# ============================================================================
# GENERATE OTP ENDPOINT - /api/v1/aadhaar/otp/generate
# ============================================================================

def test_generate_otp_valid_success(client):
    """Test OTP generation with valid Aadhaar"""
    response = client.post('/api/v1/aadhaar/otp/generate', 
                          json={'aadhaar_number': '123456789012'})
    assert response.status_code == 200
    assert 'transaction_id' in response.json
    assert 'message' in response.json
    assert response.json['transaction_id'].startswith('TXN')


def test_generate_otp_missing_parameter(client):
    """Test OTP generation without aadhaar_number"""
    response = client.post('/api/v1/aadhaar/otp/generate', json={})
    assert response.status_code == 400
    assert 'aadhaar_number is required' in response.json['error']


def test_generate_otp_no_json_body(client):
    """Test OTP generation without JSON body"""
    response = client.post('/api/v1/aadhaar/otp/generate')
    assert response.status_code == 415  # Flask returns 415 for missing Content-Type: application/json


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


def test_generate_otp_second_valid_aadhaar(client):
    """Test OTP generation with second valid Aadhaar"""
    response = client.post('/api/v1/aadhaar/otp/generate', 
                          json={'aadhaar_number': '987654321098'})
    assert response.status_code == 200
    assert 'transaction_id' in response.json


# ============================================================================
# VERIFY OTP ENDPOINT - /api/v1/aadhaar/otp/verify
# ============================================================================

def test_verify_otp_valid_success(client):
    """Test OTP verification with correct OTP"""
    # First generate OTP
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
    assert response.json['aadhaar_number'] == '123456789012'


def test_verify_otp_missing_parameters(client):
    """Test OTP verification without required params"""
    response = client.post('/api/v1/aadhaar/otp/verify', json={})
    assert response.status_code == 400
    assert 'transaction_id and otp are required' in response.json['error']


def test_verify_otp_missing_transaction_id(client):
    """Test OTP verification without transaction_id"""
    response = client.post('/api/v1/aadhaar/otp/verify', 
                          json={'otp': '123456'})
    assert response.status_code == 400


def test_verify_otp_missing_otp(client):
    """Test OTP verification without otp"""
    response = client.post('/api/v1/aadhaar/otp/verify', 
                          json={'transaction_id': 'TXN123456'})
    assert response.status_code == 400


def test_verify_otp_no_json_body(client):
    """Test OTP verification without JSON body"""
    response = client.post('/api/v1/aadhaar/otp/verify')
    assert response.status_code == 415  # Flask returns 415 for missing Content-Type: application/json


def test_verify_otp_invalid_otp(client):
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
                              'transaction_id': 'INVALID_TXN',
                              'otp': '123456'
                          })
    assert response.status_code == 400
    assert 'Invalid or expired OTP' in response.json['error']


def test_verify_otp_reuse_attempt(client):
    """Test that OTP cannot be reused after successful verification"""
    # Generate and verify OTP
    gen_response = client.post('/api/v1/aadhaar/otp/generate', 
                               json={'aadhaar_number': '123456789012'})
    txn_id = gen_response.json['transaction_id']
    
    # First verification (should succeed)
    client.post('/api/v1/aadhaar/otp/verify', 
               json={'transaction_id': txn_id, 'otp': '123456'})
    
    # Second verification attempt (should fail - OTP deleted)
    response = client.post('/api/v1/aadhaar/otp/verify', 
                          json={'transaction_id': txn_id, 'otp': '123456'})
    assert response.status_code == 400


# ============================================================================
# EKYC ENDPOINT - /api/v1/aadhaar/ekyc
# ============================================================================

def test_ekyc_valid_success(client):
    """Test eKYC with valid data"""
    response = client.post('/api/v1/aadhaar/ekyc', 
                          json={
                              'aadhaar_number': '123456789012',
                              'transaction_id': 'TXN123456',
                              'consent': True
                          })
    assert response.status_code == 200
    assert response.json['status'] == 'success'
    assert 'details' in response.json
    assert 'xml_signature' in response.json


def test_ekyc_missing_parameters(client):
    """Test eKYC without required parameters"""
    response = client.post('/api/v1/aadhaar/ekyc', json={})
    assert response.status_code == 400
    assert 'aadhaar_number and transaction_id are required' in response.json['error']


def test_ekyc_missing_aadhaar(client):
    """Test eKYC without aadhaar_number"""
    response = client.post('/api/v1/aadhaar/ekyc', 
                          json={
                              'transaction_id': 'TXN123456',
                              'consent': True
                          })
    assert response.status_code == 400


def test_ekyc_missing_transaction_id(client):
    """Test eKYC without transaction_id"""
    response = client.post('/api/v1/aadhaar/ekyc', 
                          json={
                              'aadhaar_number': '123456789012',
                              'consent': True
                          })
    assert response.status_code == 400


def test_ekyc_no_json_body(client):
    """Test eKYC without JSON body"""
    response = client.post('/api/v1/aadhaar/ekyc')
    assert response.status_code == 415  # Flask returns 415 for missing Content-Type: application/json


def test_ekyc_missing_consent(client):
    """Test eKYC without consent field"""
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
    assert 'Consent is required' in response.json['error']


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


def test_ekyc_auth_failed_wrong_transaction(client):
    """Test eKYC with wrong transaction ID"""
    response = client.post('/api/v1/aadhaar/ekyc', 
                          json={
                              'aadhaar_number': '123456789012',
                              'transaction_id': 'WRONG_TXN',
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
    assert 'Authentication failed' in response.json['error']


def test_ekyc_second_valid_aadhaar(client):
    """Test eKYC with second valid Aadhaar"""
    response = client.post('/api/v1/aadhaar/ekyc', 
                          json={
                              'aadhaar_number': '987654321098',
                              'transaction_id': 'TXN987654',
                              'consent': True
                          })
    assert response.status_code == 200
    assert response.json['details']['gender'] == 'F'


# ============================================================================
# HEALTH CHECK ENDPOINT - /health
# ============================================================================

def test_health_check(client):
    """Test health check endpoint"""
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json['status'] == 'healthy'


# ============================================================================
# EDGE CASES AND ADDITIONAL TESTS
# ============================================================================

def test_verify_aadhaar_empty_string(client):
    """Test verify with empty string"""
    response = client.post('/api/v1/aadhaar/verify', 
                          json={'aadhaar_number': ''})
    assert response.status_code == 400


def test_demographics_empty_aadhaar(client):
    """Test demographics with empty Aadhaar"""
    response = client.post('/api/v1/aadhaar/demographics', 
                          json={'aadhaar_number': '', 'consent': True})
    assert response.status_code == 400


def test_generate_otp_spaces_in_aadhaar(client):
    """Test OTP generation with spaces in Aadhaar"""
    response = client.post('/api/v1/aadhaar/otp/generate', 
                          json={'aadhaar_number': '1234 5678 9012'})
    assert response.status_code == 400
