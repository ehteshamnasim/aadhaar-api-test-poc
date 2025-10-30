import pytest
from api.dummy_aadhaar_api import app

@pytest.fixture
def client():
    return app.test_client()



# ========================================
# PRESERVED TESTS (20 tests from previous version)
# These tests passed and their endpoints were unchanged
# ========================================

# ✓ PRESERVED - Endpoint unchanged
def test_ekyc_invalid_aadhaar_format(client):
    response = client.post('/api/v1/aadhaar/ekyc', json={
        "aadhaar_number": "123",
        "transaction_id": "123456",
        "consent": True
    })
    assert response.status_code == 400




# ✓ PRESERVED - Endpoint unchanged
def test_ekyc_missing_aadhaar(client):
    response = client.post('/api/v1/aadhaar/ekyc', json={
        "transaction_id": "123456",
        "consent": True
    })
    assert response.status_code == 400




# ✓ PRESERVED - Endpoint unchanged
def test_ekyc_no_consent(client):
    response = client.post('/api/v1/aadhaar/ekyc', json={
        "aadhaar_number": "123456789012",
        "transaction_id": "123456"
    })
    assert response.status_code == 403




# ✓ PRESERVED - Endpoint unchanged
def test_ekyc_success(client):
    response = client.post('/api/v1/aadhaar/ekyc', json={
        "aadhaar_number": "123456789012",
        "transaction_id": "123456",
        "consent": True
    })
    assert response.status_code == 200




# ✓ PRESERVED - Endpoint unchanged
def test_face_authentication_invalid_aadhaar_format(client):
    response = client.post('/api/v1/aadhaar/face-authentication', json={
        "aadhaar_number": "123",
        "face_image": "base64_encoded_image"
    })
    assert response.status_code == 401




# ✓ PRESERVED - Endpoint unchanged
def test_face_authentication_missing_aadhaar(client):
    response = client.post('/api/v1/aadhaar/face-authentication', json={
        "face_image": "base64_encoded_image"
    })
    assert response.status_code == 401




# ✓ PRESERVED - Endpoint unchanged
def test_face_authentication_success(client):
    response = client.post('/api/v1/aadhaar/face-authentication', json={
        "aadhaar_number": "123456789012",
        "face_image": "base64_encoded_image"
    })
    assert response.status_code == 200




# ✓ PRESERVED - Endpoint unchanged
def test_health_success(client):
    response = client.get('/api/v1/health')
    assert response.status_code == 200



# ✓ PRESERVED - Endpoint unchanged
def test_masked_aadhaar_invalid_format(client):
    response = client.get('/api/v1/aadhaar/masked-aadhaar?aadhaar_number=123')
    assert response.status_code == 400




# ✓ PRESERVED - Endpoint unchanged
def test_masked_aadhaar_missing_param(client):
    response = client.get('/api/v1/aadhaar/masked-aadhaar')
    assert response.status_code == 400




# ✓ PRESERVED - Endpoint unchanged
def test_masked_aadhaar_success(client):
    response = client.get('/api/v1/aadhaar/masked-aadhaar?aadhaar_number=123456789012')
    assert response.status_code == 200
    data = response.get_json()
    assert 'masked_aadhaar' in data
    assert data['masked_aadhaar'] == 'XXXXXXXX9012'




# ✓ PRESERVED - Endpoint unchanged
def test_otp_generate_invalid_aadhaar_format(client):
    response = client.post('/api/v1/aadhaar/otp/generate', json={
        "aadhaar_number": "123"
    })
    assert response.status_code == 400




# ✓ PRESERVED - Endpoint unchanged
def test_otp_generate_missing_aadhaar(client):
    response = client.post('/api/v1/aadhaar/otp/generate', json={})
    assert response.status_code == 400




# ✓ PRESERVED - Endpoint unchanged
def test_otp_generate_success(client):
    response = client.post('/api/v1/aadhaar/otp/generate', json={
        "aadhaar_number": "123456789012"
    })
    assert response.status_code == 200
    data = response.get_json()
    assert 'transaction_id' in data




# ✓ PRESERVED - Endpoint unchanged
def test_otp_verify_invalid_transaction_id_format(client):
    response = client.post('/api/v1/aadhaar/otp/verify', json={
        "transaction_id": "abc",
        "otp": "123456"
    })
    assert response.status_code == 400




# ✓ PRESERVED - Endpoint unchanged
def test_otp_verify_missing_transaction_id(client):
    response = client.post('/api/v1/aadhaar/otp/verify', json={
        "otp": "123456"
    })
    assert response.status_code == 400




# ✓ PRESERVED - Endpoint unchanged
def test_otp_verify_success(client):
    response = client.post('/api/v1/aadhaar/otp/verify', json={
        "transaction_id": "123456",
        "otp": "123456"
    })
    assert response.status_code == 200




# ✓ PRESERVED - Endpoint unchanged
def test_verify_invalid_aadhaar_format(client):
    response = client.post('/api/v1/aadhaar/verify', json={
        "aadhaar_number": "123"
    })
    assert response.status_code == 400




# ✓ PRESERVED - Endpoint unchanged
def test_verify_missing_aadhaar(client):
    response = client.post('/api/v1/aadhaar/verify', json={})
    assert response.status_code == 400




# ✓ PRESERVED - Endpoint unchanged
def test_verify_success(client):
    response = client.post('/api/v1/aadhaar/verify', json={
        "aadhaar_number": "123456789012"
    })
    assert response.status_code == 201






# ========================================
# REGENERATED TESTS (5 tests for changed endpoints)
# These tests were regenerated due to API spec changes
# ========================================

# 🔄 REGENERATED - Endpoint modified
def test_demographics_success(client):
    # Success case - include ALL required fields
    response = client.post('/api/v1/aadhaar/demographics', json={
        "aadhaar_number": "123456789012",
        "consent": True  # MUST include consent for success
    })
    assert response.status_code == 200
    data = response.get_json()
    assert 'name' in data
    assert 'dob' in data


# 🔄 REGENERATED - Endpoint modified
def test_demographics_missing_aadhaar(client):
    # Missing non-consent field → 400
    response = client.post('/api/v1/aadhaar/demographics', json={
        "consent": True
    })
    assert response.status_code == 400


# 🔄 REGENERATED - Endpoint modified
def test_demographics_invalid_aadhaar_format(client):
    # Invalid format → 400
    response = client.post('/api/v1/aadhaar/demographics', json={
        "aadhaar_number": "123",  # Invalid - not 12 digits
        "consent": True
    })
    assert response.status_code == 400


# 🔄 REGENERATED - Endpoint modified
def test_demographics_no_consent(client):
    # Missing consent field → 403
    response = client.post('/api/v1/aadhaar/demographics', json={
        "aadhaar_number": "123456789012"
    })
    assert response.status_code == 403


# 🔄 REGENERATED - Endpoint modified
def test_demographics_consent_false(client):
    # Consent field set to False → 403
    response = client.post('/api/v1/aadhaar/demographics', json={
        "aadhaar_number": "123456789012",
        "consent": False
    })
    assert response.status_code == 403

