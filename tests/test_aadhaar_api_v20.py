"""AI-Generated Tests v20 - 2025-10-17 13:06:51"""
import pytest
from api.dummy_aadhaar_api import app

@pytest.fixture
def client():
    """Flask test client fixture"""
    return app.test_client()


def test_generate_otp_missing_field(client):
    """Test missing aadhaar_number field in OTP generation"""
    response = client.post('/api/v1/aadhaar/otp/generate', json={})
    assert response.status_code == 400


def test_generate_otp_success(client):
    """Test successful OTP generation"""
    response = client.post('/api/v1/aadhaar/otp/generate', json={'aadhaar_number': '123456789012'})
    assert response.status_code == 200


def test_get_demographics_missing_aadhaar(client):
    """Test missing aadhaar_number field in demographic details retrieval"""
    response = client.post('/api/v1/aadhaar/demographics', json={'consent': True})
    assert response.status_code == 400


def test_get_demographics_missing_consent(client):
    """Test missing consent field in demographic details retrieval"""
    response = client.post('/api/v1/aadhaar/demographics', json={'aadhaar_number': '123456789012'})
    assert response.status_code == 400


def test_get_demographics_success(client):
    """Test successful retrieval of demographic details"""
    response = client.post('/api/v1/aadhaar/demographics', json={'aadhaar_number': '123456789012', 'consent': True})
    assert response.status_code == 200


def test_perform_ekyc_missing_aadhaar(client):
    """Test missing aadhaar_number field in eKYC"""
    response = client.post('/api/v1/aadhaar/ekyc', json={'transaction_id': '1234567890', 'consent': True})
    assert response.status_code == 400


def test_perform_ekyc_missing_consent(client):
    """Test missing consent field in eKYC"""
    response = client.post('/api/v1/aadhaar/ekyc', json={'aadhaar_number': '123456789012', 'transaction_id': '1234567890'})
    assert response.status_code == 400

def test_perform_ekyc_missing_transaction_id(client):
    """Test missing transaction_id field in eKYC"""
    response = client.post('/api/v1/aadhaar/ekyc', json={'aadhaar_number': '123456789012', 'consent': True})
    assert response.status_code == 400


def test_perform_ekyc_success(client):
    """Test successful eKYC"""
    response = client.post('/api/v1/aadhaar/ekyc', json={'aadhaar_number': '123456789012', 'transaction_id': '1234567890', 'consent': True})
    assert response.status_code == 200


def test_verify_aadhaar_missing_field(client):
    """Test missing aadhaar_number field in Aadhaar verification"""
    response = client.post('/api/v1/aadhaar/verify', json={})
    assert response.status_code == 400


def test_verify_aadhaar_success(client):
    """Test successful Aadhaar verification"""
    response = client.post('/api/v1/aadhaar/verify', json={'aadhaar_number': '123456789012'})
    assert response.status_code == 200


def test_verify_otp_missing_otp(client):
    """Test missing otp field in OTP verification"""
    response = client.post('/api/v1/aadhaar/otp/verify', json={'transaction_id': '1234567890'})
    assert response.status_code == 400


def test_verify_otp_missing_transaction_id(client):
    """Test missing transaction_id field in OTP verification"""
    response = client.post('/api/v1/aadhaar/otp/verify', json={'otp': '123456'})
    assert response.status_code == 400


def test_verify_otp_success(client):
    """Test successful OTP verification"""
    response = client.post('/api/v1/aadhaar/otp/verify', json={'transaction_id': '1234567890', 'otp': '123456'})
    assert response.status_code == 200

