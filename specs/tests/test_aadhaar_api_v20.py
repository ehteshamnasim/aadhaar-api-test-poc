import pytest
from api.dummy_aadhaar_api import app

@pytest.fixture
def client():
    return app.test_client()



# ========================================
# PRESERVED TESTS (14 tests from previous version)
# These tests passed and their endpoints were unchanged
# ========================================

# ✓ PRESERVED - Endpoint unchanged
def test_ekyc_missing_field(client):
    """Test eKYC with missing field"""
    response = client.post('/api/v1/aadhaar/ekyc', json={"aadhaar_number": "123456789012", "transaction_id": "123456"})
    assert response.status_code == 400






# ✓ PRESERVED - Endpoint unchanged
def test_ekyc_no_consent(client):
    """Test eKYC without consent"""
    response = client.post('/api/v1/aadhaar/ekyc', json={"aadhaar_number": "123456789012", "transaction_id": "123456", "consent": False})
    assert response.status_code == 403






# ✓ PRESERVED - Endpoint unchanged
def test_ekyc_success(client):
    """Test successful eKYC"""
    response = client.post('/api/v1/aadhaar/ekyc', json={"aadhaar_number": "123456789012", "transaction_id": "123456", "consent": True})
    assert response.status_code == 200






# ✓ PRESERVED - Endpoint unchanged
def test_face_authentication_missing_field(client):
    """Test face-based authentication with missing field"""
    response = client.post('/api/v1/aadhaar/face-authentication', json={"aadhaar_number": "123456789012"})
    assert response.status_code == 401






# ✓ PRESERVED - Endpoint unchanged
def test_face_authentication_success(client):
    """Test successful face-based authentication"""
    response = client.post('/api/v1/aadhaar/face-authentication', json={"aadhaar_number": "123456789012", "face_image": "base64image"})
    assert response.status_code == 200






# ✓ PRESERVED - Endpoint unchanged
def test_generate_otp_missing_field(client):
    """Test OTP generation with missing field"""
    response = client.post('/api/v1/aadhaar/otp/generate', json={})
    assert response.status_code == 400






# ✓ PRESERVED - Endpoint unchanged
def test_generate_otp_success(client):
    """Test successful OTP generation"""
    response = client.post('/api/v1/aadhaar/otp/generate', json={"aadhaar_number": "123456789012"})
    assert response.status_code == 200






# ✓ PRESERVED - Endpoint unchanged
def test_get_masked_aadhaar_missing_field(client):
    """Test retrieval of masked Aadhaar number with missing field"""
    response = client.get('/api/v1/aadhaar/masked-aadhaar', json={})
    assert response.status_code == 400






# ✓ PRESERVED - Endpoint unchanged
def test_get_masked_aadhaar_success(client):
    """Test successful retrieval of masked Aadhaar number"""
    response = client.get('/api/v1/aadhaar/masked-aadhaar')
    assert response.status_code == 200






# ✓ PRESERVED - Endpoint unchanged
def test_health_check_success(client):
    """Test successful health check endpoint"""
    response = client.get('/api/v1/health')
    assert response.status_code == 200





# ✓ PRESERVED - Endpoint unchanged
def test_verify_aadhaar_missing_field(client):
    """Test Aadhaar verification with missing field"""
    response = client.post('/api/v1/aadhaar/verify', json={})
    assert response.status_code == 400






# ✓ PRESERVED - Endpoint unchanged
def test_verify_aadhaar_success(client):
    """Test successful Aadhaar verification"""
    response = client.post('/api/v1/aadhaar/verify', json={"aadhaar_number": "123456789012"})
    assert response.status_code == 201






# ✓ PRESERVED - Endpoint unchanged
def test_verify_otp_missing_field(client):
    """Test OTP verification with missing field"""
    response = client.post('/api/v1/aadhaar/otp/verify', json={})
    assert response.status_code == 400






# ✓ PRESERVED - Endpoint unchanged
def test_verify_otp_success(client):
    """Test successful OTP verification"""
    response = client.post('/api/v1/aadhaar/otp/verify', json={"transaction_id": "123456", "otp": "123456"})
    assert response.status_code == 200










# ========================================
# REGENERATED TESTS (5 tests for changed endpoints)
# These tests were regenerated due to API spec changes
# ========================================

# 🔄 REGENERATED - Endpoint modified
def test_get_demographics_success(client):
    """
    Test successful retrieval of demographic details with valid payload.
    """
    response = client.post('/api/v1/aadhaar/demographics', json={"aadhaar_number": "123456789012", "consent": True})
    assert response.status_code == 200
    assert 'demographic_details' in response.json


# 🔄 REGENERATED - Endpoint modified
def test_get_demographics_missing_aadhaar_number(client):
    """
    Test retrieval of demographic details with missing aadhaar_number.
    """
    response = client.post('/api/v1/aadhaar/demographics', json={"consent": True})
    assert response.status_code == 400
    assert 'error' in response.json


# 🔄 REGENERATED - Endpoint modified
def test_get_demographics_missing_consent(client):
    """
    Test retrieval of demographic details with missing consent.
    """
    response = client.post('/api/v1/aadhaar/demographics', json={"aadhaar_number": "123456789012"})
    assert response.status_code == 400
    assert 'error' in response.json


# 🔄 REGENERATED - Endpoint modified
def test_get_demographics_invalid_aadhaar_number(client):
    """
    Test retrieval of demographic details with invalid aadhaar_number.
    """
    response = client.post('/api/v1/aadhaar/demographics', json={"aadhaar_number": "invalid", "consent": True})
    assert response.status_code == 403
    assert 'error' in response.json


# 🔄 REGENERATED - Endpoint modified
def test_get_demographics_invalid_consent(client):
    """
    Test retrieval of demographic details with invalid consent.
    """
    response = client.post('/api/v1/aadhaar/demographics', json={"aadhaar_number": "123456789012", "consent": "invalid"})
    assert response.status_code == 400
    assert 'error' in response.json

