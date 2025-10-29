"""AI-Generated Tests v23 - 2025-10-30 02:17:46"""
import pytest
from api.dummy_aadhaar_api import app

@pytest.fixture
def client():
    """Flask test client fixture"""
    return app.test_client()


def test_demographics_invalid_aadhaar_format(client):
    response = client.post('/api/v1/aadhaar/demographics', json={
        "aadhaar_number": "123",
        "consent": True
    })
    assert response.status_code == 400


def test_demographics_missing_aadhaar(client):
    response = client.post('/api/v1/aadhaar/demographics', json={
        "consent": True
    })
    assert response.status_code == 400


def test_demographics_no_consent(client):
    response = client.post('/api/v1/aadhaar/demographics', json={
        "aadhaar_number": "123456789012"
    })
    assert response.status_code == 403


def test_demographics_success(client):
    response = client.post('/api/v1/aadhaar/demographics', json={
        "aadhaar_number": "123456789012",
        "consent": True
    })
    assert response.status_code == 200
    data = response.get_json()
    assert 'name' in data
    assert 'dob' in data


def test_ekyc_invalid_aadhaar_format(client):
    response = client.post('/api/v1/aadhaar/ekyc', json={
        "aadhaar_number": "123",
        "transaction_id": "123456",
        "consent": True
    })
    assert response.status_code == 400


def test_ekyc_missing_aadhaar(client):
    response = client.post('/api/v1/aadhaar/ekyc', json={
        "transaction_id": "123456",
        "consent": True
    })
    assert response.status_code == 400


def test_ekyc_no_consent(client):
    response = client.post('/api/v1/aadhaar/ekyc', json={
        "aadhaar_number": "123456789012",
        "transaction_id": "123456"
    })
    assert response.status_code == 403


def test_ekyc_success(client):
    response = client.post('/api/v1/aadhaar/ekyc', json={
        "aadhaar_number": "123456789012",
        "transaction_id": "123456",
        "consent": True
    })
    assert response.status_code == 200


def test_face_authentication_invalid_aadhaar_format(client):
    response = client.post('/api/v1/aadhaar/face-authentication', json={
        "aadhaar_number": "123",
        "face_image": "base64_encoded_image"
    })
    assert response.status_code == 401


def test_face_authentication_missing_aadhaar(client):
    response = client.post('/api/v1/aadhaar/face-authentication', json={
        "face_image": "base64_encoded_image"
    })
    assert response.status_code == 401


def test_face_authentication_success(client):
    response = client.post('/api/v1/aadhaar/face-authentication', json={
        "aadhaar_number": "123456789012",
        "face_image": "base64_encoded_image"
    })
    assert response.status_code == 200


def test_health_success(client):
    response = client.get('/api/v1/health')
    assert response.status_code == 200

def test_masked_aadhaar_invalid_format(client):
    response = client.get('/api/v1/aadhaar/masked-aadhaar?aadhaar_number=123')
    assert response.status_code == 400


def test_masked_aadhaar_missing_param(client):
    response = client.get('/api/v1/aadhaar/masked-aadhaar')
    assert response.status_code == 400


def test_masked_aadhaar_success(client):
    response = client.get('/api/v1/aadhaar/masked-aadhaar?aadhaar_number=123456789012')
    assert response.status_code == 200
    data = response.get_json()
    assert 'masked_aadhaar' in data
    assert data['masked_aadhaar'] == 'XXXXXXXX9012'


def test_otp_generate_invalid_aadhaar_format(client):
    response = client.post('/api/v1/aadhaar/otp/generate', json={
        "aadhaar_number": "123"
    })
    assert response.status_code == 400


def test_otp_generate_missing_aadhaar(client):
    response = client.post('/api/v1/aadhaar/otp/generate', json={})
    assert response.status_code == 400


def test_otp_generate_success(client):
    response = client.post('/api/v1/aadhaar/otp/generate', json={
        "aadhaar_number": "123456789012"
    })
    assert response.status_code == 200
    data = response.get_json()
    assert 'transaction_id' in data


def test_otp_verify_invalid_transaction_id_format(client):
    response = client.post('/api/v1/aadhaar/otp/verify', json={
        "transaction_id": "abc",
        "otp": "123456"
    })
    assert response.status_code == 400


def test_otp_verify_missing_transaction_id(client):
    response = client.post('/api/v1/aadhaar/otp/verify', json={
        "otp": "123456"
    })
    assert response.status_code == 400


def test_otp_verify_success(client):
    response = client.post('/api/v1/aadhaar/otp/verify', json={
        "transaction_id": "123456",
        "otp": "123456"
    })
    assert response.status_code == 200


def test_verify_invalid_aadhaar_format(client):
    response = client.post('/api/v1/aadhaar/verify', json={
        "aadhaar_number": "123"
    })
    assert response.status_code == 400


def test_verify_missing_aadhaar(client):
    response = client.post('/api/v1/aadhaar/verify', json={})
    assert response.status_code == 400


def test_verify_success(client):
    response = client.post('/api/v1/aadhaar/verify', json={
        "aadhaar_number": "123456789012"
    })
    assert response.status_code == 201

