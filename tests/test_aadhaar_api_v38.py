"""AI-Generated Tests v38 - 2025-10-28 02:29:46"""
import pytest
from api.dummy_aadhaar_api import app

@pytest.fixture
def client():
    """Flask test client fixture"""
    return app.test_client()


def test_demographics_missing_aadhaar_field(client):
    response = client.post('/api/v1/aadhaar/demographics', json={'consent': True})
    assert response.status_code == 400


def test_demographics_missing_consent_field(client):
    response = client.post('/api/v1/aadhaar/demographics', json={'aadhaar_number': '123456789012'})
    assert response.status_code == 400


def test_demographics_success(client):
    response = client.post('/api/v1/aadhaar/demographics', json={'aadhaar_number': '123456789012', 'consent': True})
    assert response.status_code == 200


def test_ekyc_missing_aadhaar_field(client):
    response = client.post('/api/v1/aadhaar/ekyc', json={'transaction_id': '1234567890', 'consent': True})
    assert response.status_code == 400


def test_ekyc_missing_consent_field(client):
    response = client.post('/api/v1/aadhaar/ekyc', json={'aadhaar_number': '123456789012', 'transaction_id': '1234567890'})
    assert response.status_code == 400


def test_ekyc_missing_transaction_id_field(client):
    response = client.post('/api/v1/aadhaar/ekyc', json={'aadhaar_number': '123456789012', 'consent': True})
    assert response.status_code == 400


def test_ekyc_success(client):
    response = client.post('/api/v1/aadhaar/ekyc', json={'aadhaar_number': '123456789012', 'transaction_id': '1234567890', 'consent': True})
    assert response.status_code == 200


def test_face_authentication_missing_aadhaar_field(client):
    response = client.post('/api/v1/aadhaar/face-authentication', json={'face_image': 'base64image'})
    assert response.status_code == 401


def test_face_authentication_missing_face_image_field(client):
    response = client.post('/api/v1/aadhaar/face-authentication', json={'aadhaar_number': '123456789012'})
    assert response.status_code == 401

def test_face_authentication_success(client):
    response = client.post('/api/v1/aadhaar/face-authentication', json={'aadhaar_number': '123456789012', 'face_image': 'base64image'})
    assert response.status_code == 200


def test_generate_otp_missing_field(client):
    response = client.post('/api/v1/aadhaar/otp/generate', json={})
    assert response.status_code == 400


def test_generate_otp_success(client):
    response = client.post('/api/v1/aadhaar/otp/generate', json={'aadhaar_number': '123456789012'})
    assert response.status_code == 200


def test_get_masked_aadhaar_success(client):
    response = client.get('/api/v1/aadhaar/masked-aadhaar')
    assert response.status_code == 200


def test_verify_aadhaar_missing_field(client):
    response = client.post('/api/v1/aadhaar/verify', json={})
    assert response.status_code == 400


def test_verify_aadhaar_success(client):
    response = client.post('/api/v1/aadhaar/verify', json={'aadhaar_number': '123456789012'})
    assert response.status_code == 200


def test_verify_otp_missing_otp_field(client):
    response = client.post('/api/v1/aadhaar/otp/verify', json={'transaction_id': '1234567890'})
    assert response.status_code == 400


def test_verify_otp_missing_transaction_id_field(client):
    response = client.post('/api/v1/aadhaar/otp/verify', json={'otp': '123456'})
    assert response.status_code == 400


def test_verify_otp_success(client):
    response = client.post('/api/v1/aadhaar/otp/verify', json={'transaction_id': '1234567890', 'otp': '123456'})
    assert response.status_code == 200

