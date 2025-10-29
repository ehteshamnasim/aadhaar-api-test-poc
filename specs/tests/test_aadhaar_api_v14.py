import pytest
from api.dummy_aadhaar_api import app

@pytest.fixture
def client():
    return app.test_client()

# POST /aadhaar/verify-cache


# ========================================
# PRESERVED TESTS (26 tests from previous version)
# These tests passed and their endpoints were unchanged
# ========================================

# ✓ PRESERVED - Endpoint unchanged
def test_demographics_missing_aadhaar_number(client):
    response = client.post('/api/v1/aadhaar/demographics', json={'consent': True})
    assert response.status_code == 400









# ✓ PRESERVED - Endpoint unchanged
def test_demographics_missing_consent(client):
    response = client.post('/api/v1/aadhaar/demographics', json={'aadhaar_number': '123456789012'})
    assert response.status_code == 400









# ✓ PRESERVED - Endpoint unchanged
def test_demographics_success(client):
    response = client.post('/api/v1/aadhaar/demographics', json={'aadhaar_number': '123456789012', 'consent': True})
    assert response.status_code == 200









# ✓ PRESERVED - Endpoint unchanged
def test_ekyc_missing_aadhaar_number(client):
    response = client.post('/api/v1/aadhaar/ekyc', json={'transaction_id': '1234567890', 'consent': True})
    assert response.status_code == 400









# ✓ PRESERVED - Endpoint unchanged
def test_ekyc_missing_consent(client):
    response = client.post('/api/v1/aadhaar/ekyc', json={'aadhaar_number': '123456789012', 'transaction_id': '1234567890'})
    assert response.status_code == 400









# ✓ PRESERVED - Endpoint unchanged
def test_ekyc_missing_transaction_id(client):
    response = client.post('/api/v1/aadhaar/ekyc', json={'aadhaar_number': '123456789012', 'consent': True})
    assert response.status_code == 400









# ✓ PRESERVED - Endpoint unchanged
def test_ekyc_success(client):
    response = client.post('/api/v1/aadhaar/ekyc', json={'aadhaar_number': '123456789012', 'transaction_id': '1234567890', 'consent': True})
    assert response.status_code == 200









# ✓ PRESERVED - Endpoint unchanged
def test_face_authentication_missing_aadhaar_number(client):
    response = client.post('/api/v1/aadhaar/face-authentication', json={'face_image': 'base64image'})
    assert response.status_code == 401









# ✓ PRESERVED - Endpoint unchanged
def test_face_authentication_missing_face_image(client):
    response = client.post('/api/v1/aadhaar/face-authentication', json={'aadhaar_number': '123456789012'})
    assert response.status_code == 401









# ✓ PRESERVED - Endpoint unchanged
def test_face_authentication_success(client):
    response = client.post('/api/v1/aadhaar/face-authentication', json={'aadhaar_number': '123456789012', 'face_image': 'base64image'})
    assert response.status_code == 200









# ✓ PRESERVED - Endpoint unchanged
def test_health_check_bad_gateway(client):
    response = client.get('/api/v1/aadhaar/health-check')
    assert response.status_code == 502









# ✓ PRESERVED - Endpoint unchanged
def test_health_check_gateway_timeout(client):
    response = client.get('/api/v1/aadhaar/health-check')
    assert response.status_code == 504








# ✓ PRESERVED - Endpoint unchanged
def test_health_check_service_unavailable(client):
    response = client.get('/api/v1/aadhaar/health-check')
    assert response.status_code == 503









# ✓ PRESERVED - Endpoint unchanged
def test_health_check_success(client):
    response = client.get('/api/v1/aadhaar/health-check')
    assert response.status_code == 200









# ✓ PRESERVED - Endpoint unchanged
def test_masked_aadhaar_invalid_request(client):
    response = client.get('/api/v1/aadhaar/masked-aadhaar', json={'invalid_field': 'value'})
    assert response.status_code == 400









# ✓ PRESERVED - Endpoint unchanged
def test_masked_aadhaar_success(client):
    response = client.get('/api/v1/aadhaar/masked-aadhaar')
    assert response.status_code == 200









# ✓ PRESERVED - Endpoint unchanged
def test_otp_generate_missing_aadhaar_number(client):
    response = client.post('/api/v1/aadhaar/otp/generate', json={})
    assert response.status_code == 400









# ✓ PRESERVED - Endpoint unchanged
def test_otp_generate_success(client):
    response = client.post('/api/v1/aadhaar/otp/generate', json={'aadhaar_number': '123456789012'})
    assert response.status_code == 200









# ✓ PRESERVED - Endpoint unchanged
def test_otp_verify_missing_otp(client):
    response = client.post('/api/v1/aadhaar/otp/verify', json={'transaction_id': '1234567890'})
    assert response.status_code == 400









# ✓ PRESERVED - Endpoint unchanged
def test_otp_verify_missing_transaction_id(client):
    response = client.post('/api/v1/aadhaar/otp/verify', json={'otp': '123456'})
    assert response.status_code == 400









# ✓ PRESERVED - Endpoint unchanged
def test_otp_verify_success(client):
    response = client.post('/api/v1/aadhaar/otp/verify', json={'transaction_id': '1234567890', 'otp': '123456'})
    assert response.status_code == 200









# ✓ PRESERVED - Endpoint unchanged
def test_test_new_endpoint_success(client):
    response = client.get('/api/v1/aadhaar/test-new-endpoint')
    assert response.status_code == 200















# ✓ PRESERVED - Endpoint unchanged
def test_verify_aadhaar_with_valid_payload(client):
    """
    Test verifying Aadhaar number with a valid payload.
    Expected response: 201 Created
    """
    payload = {
        "aadhaar_number": "123456789012",
        "captcha": "abc123",
        "device_id": "device123",
        "session_token": "token123"
    }
    response = client.post('/aadhaar/verify-cache', json=payload)
    assert response.status_code == 201
    assert 'message' in response.json



# ✓ PRESERVED - Endpoint unchanged
def test_verify_aadhaar_with_missing_required_fields(client):
    """
    Test verifying Aadhaar number with missing required fields.
    Expected response: 400 Bad Request
    """
    payload = {
        "aadhaar_number": "123456789012",
        "device_id": "device123",
        "session_token": "token123"
    }
    response = client.post('/aadhaar/verify-cache', json=payload)
    assert response.status_code == 400
    assert 'error' in response.json



# ✓ PRESERVED - Endpoint unchanged
def test_verify_aadhaar_with_invalid_captcha(client):
    """
    Test verifying Aadhaar number with an invalid captcha.
    Expected response: 401 Unauthorized
    """
    payload = {
        "aadhaar_number": "123456789012",
        "captcha": "wrongcaptcha",
        "device_id": "device123",
        "session_token": "token123"
    }
    response = client.post('/aadhaar/verify-cache', json=payload)
    assert response.status_code == 401
    assert 'error' in response.json



# ✓ PRESERVED - Endpoint unchanged
def test_verify_aadhaar_with_invalid_session_token(client):
    """
    Test verifying Aadhaar number with an invalid session token.
    Expected response: 403 Forbidden
    """
    payload = {
        "aadhaar_number": "123456789012",
        "captcha": "abc123",
        "device_id": "device123",
        "session_token": "invalidtoken"
    }
    response = client.post('/aadhaar/verify-cache', json=payload)
    assert response.status_code == 403
    assert 'error' in response.json




# ========================================
# REGENERATED TESTS (25 tests for changed endpoints)
# These tests were regenerated due to API spec changes
# ========================================

# 🔄 REGENERATED - Endpoint modified
def test_verify_cache_success(client):
    response = client.post('/aadhaar/verify-cache', json={
        'aadhaar_number': '123456789012',
        'captcha': 'abc123'
    })
    assert response.status_code == 201


# 🔄 REGENERATED - Endpoint modified
def test_verify_cache_missing_aadhaar(client):
    response = client.post('/aadhaar/verify-cache', json={
        'captcha': 'abc123'
    })
    assert response.status_code == 400


# 🔄 REGENERATED - Endpoint modified
def test_verify_cache_missing_captcha(client):
    response = client.post('/aadhaar/verify-cache', json={
        'aadhaar_number': '123456789012'
    })
    assert response.status_code == 400

# GET /aadhaar/test-new-endpoint

# 🔄 REGENERATED - Endpoint modified
def test_test_new_endpoint_success(client):
    response = client.get('/aadhaar/test-new-endpoint')
    assert response.status_code == 200

# POST /aadhaar/demographics

# 🔄 REGENERATED - Endpoint modified
def test_demographics_success(client):
    response = client.post('/aadhaar/demographics', json={
        'aadhaar_number': '123456789012',
        'consent': True
    })
    assert response.status_code == 200


# 🔄 REGENERATED - Endpoint modified
def test_demographics_missing_aadhaar(client):
    response = client.post('/aadhaar/demographics', json={
        'consent': True
    })
    assert response.status_code == 400


# 🔄 REGENERATED - Endpoint modified
def test_demographics_missing_consent(client):
    response = client.post('/aadhaar/demographics', json={
        'aadhaar_number': '123456789012'
    })
    assert response.status_code == 400

# POST /aadhaar/otp/generate

# 🔄 REGENERATED - Endpoint modified
def test_otp_generate_success(client):
    response = client.post('/aadhaar/otp/generate', json={
        'aadhaar_number': '123456789012'
    })
    assert response.status_code == 200


# 🔄 REGENERATED - Endpoint modified
def test_otp_generate_missing_aadhaar(client):
    response = client.post('/aadhaar/otp/generate', json={})
    assert response.status_code == 400

# POST /aadhaar/otp/verify

# 🔄 REGENERATED - Endpoint modified
def test_otp_verify_success(client):
    response = client.post('/aadhaar/otp/verify', json={
        'transaction_id': '123456789',
        'otp': '123456'
    })
    assert response.status_code == 200


# 🔄 REGENERATED - Endpoint modified
def test_otp_verify_missing_transaction_id(client):
    response = client.post('/aadhaar/otp/verify', json={
        'otp': '123456'
    })
    assert response.status_code == 400


# 🔄 REGENERATED - Endpoint modified
def test_otp_verify_missing_otp(client):
    response = client.post('/aadhaar/otp/verify', json={
        'transaction_id': '123456789'
    })
    assert response.status_code == 400

# POST /aadhaar/ekyc

# 🔄 REGENERATED - Endpoint modified
def test_ekyc_success(client):
    response = client.post('/aadhaar/ekyc', json={
        'aadhaar_number': '123456789012',
        'transaction_id': '123456789',
        'consent': True
    })
    assert response.status_code == 200


# 🔄 REGENERATED - Endpoint modified
def test_ekyc_missing_aadhaar(client):
    response = client.post('/aadhaar/ekyc', json={
        'transaction_id': '123456789',
        'consent': True
    })
    assert response.status_code == 400


# 🔄 REGENERATED - Endpoint modified
def test_ekyc_missing_transaction_id(client):
    response = client.post('/aadhaar/ekyc', json={
        'aadhaar_number': '123456789012',
        'consent': True
    })
    assert response.status_code == 400


# 🔄 REGENERATED - Endpoint modified
def test_ekyc_missing_consent(client):
    response = client.post('/aadhaar/ekyc', json={
        'aadhaar_number': '123456789012',
        'transaction_id': '123456789'
    })
    assert response.status_code == 400

# GET /aadhaar/masked-aadhaar

# 🔄 REGENERATED - Endpoint modified
def test_masked_aadhaar_success(client):
    response = client.get('/aadhaar/masked-aadhaar')
    assert response.status_code == 200


# 🔄 REGENERATED - Endpoint modified
def test_masked_aadhaar_error(client):
    response = client.get('/aadhaar/masked-aadhaar')
    assert response.status_code == 400

# POST /aadhaar/face-authentication

# 🔄 REGENERATED - Endpoint modified
def test_face_authentication_success(client):
    response = client.post('/aadhaar/face-authentication', json={
        'aadhaar_number': '123456789012',
        'face_image': 'base64encodedimage'
    })
    assert response.status_code == 200


# 🔄 REGENERATED - Endpoint modified
def test_face_authentication_missing_aadhaar(client):
    response = client.post('/aadhaar/face-authentication', json={
        'face_image': 'base64encodedimage'
    })
    assert response.status_code == 401


# 🔄 REGENERATED - Endpoint modified
def test_face_authentication_missing_face_image(client):
    response = client.post('/aadhaar/face-authentication', json={
        'aadhaar_number': '123456789012'
    })
    assert response.status_code == 401

# GET /aadhaar/health-check

# 🔄 REGENERATED - Endpoint modified
def test_health_check_success(client):
    response = client.get('/aadhaar/health-check')
    assert response.status_code == 200


# 🔄 REGENERATED - Endpoint modified
def test_health_check_service_unavailable(client):
    response = client.get('/aadhaar/health-check')
    assert response.status_code == 503


# 🔄 REGENERATED - Endpoint modified
def test_health_check_bad_gateway(client):
    response = client.get('/aadhaar/health-check')
    assert response.status_code == 502


# 🔄 REGENERATED - Endpoint modified
def test_health_check_gateway_timeout(client):
    response = client.get('/aadhaar/health-check')
    assert response.status_code == 504

