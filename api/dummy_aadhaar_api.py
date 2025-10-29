from flask import Flask, request, jsonify
import re
import time
import random

app = Flask(__name__)

# Configuration flags for testing different scenarios
TEST_MODE = {
    'self_healing': True,       # Set True to test self-healing (changes status codes)
    'error_analysis': False,    # Set True to test error analysis (requires auth)
    'anomaly_detection': False, # Set True to test anomaly detection (adds delays/errors)
    'traffic_replay': True      # Set True to record traffic
}

# Dummy valid Aadhaar numbers for testing
VALID_AADHAARS = {
    "123456789012": {"name": "Eht****** Kum**", "dob": "1990-01-01", "gender": "M", "address": "Delhi, ****10"},
    "987654321098": {"name": "Pri****** Sha**", "dob": "1995-05-15", "gender": "F", "address": "Mumbai, ****20"}
}

# Dummy OTP storage (in-memory for demo)
OTPS = {}

def is_valid_aadhaar(aadhaar):
    """Validate Aadhaar: must be 12 digits"""
    return bool(re.match(r'^\d{12}$', aadhaar))

@app.route('/api/v1/aadhaar/verify', methods=['POST'])
def verify_aadhaar():
    """Verify Aadhaar number"""
    
    # TEST SCENARIO: Error Analysis - Require authentication
    if TEST_MODE['error_analysis']:
        auth_token = request.headers.get('Authorization')
        if not auth_token or auth_token != 'Bearer valid-token-123':
            return jsonify({
                "status": "unauthorized", 
                "error": "Missing or invalid authentication token"
            }), 401
    
    # TEST SCENARIO: Anomaly Detection - Add random delays
    if TEST_MODE['anomaly_detection']:
        if random.random() > 0.7:  # 30% of requests are slow
            time.sleep(2)  # 2 second delay simulates performance issue
        
        # Randomly return errors to simulate high error rate
        if random.random() > 0.85:  # 15% error rate
            return jsonify({"error": "Database connection timeout"}), 500
    
    data = request.get_json()
    
    if not data or 'aadhaar_number' not in data:
        return jsonify({"status": "invalid", "error": "aadhaar_number is required"}), 400
    
    aadhaar = data['aadhaar_number']
    
    if not is_valid_aadhaar(aadhaar):
        return jsonify({"status": "invalid", "error": "Aadhaar must be 12 digits"}), 400
    
    if aadhaar in VALID_AADHAARS:
        # TEST SCENARIO: Self-Healing - Change status code to trigger test failures
        status_code = 201 if TEST_MODE['self_healing'] else 200
        return jsonify({"status": "valid", "message": "Aadhaar number is valid"}), status_code
    else:
        return jsonify({"status": "invalid", "error": "Aadhaar not found in database"}), 400

@app.route('/api/v1/aadhaar/demographics', methods=['POST'])
def get_demographics():
    """Get demographic details"""
    data = request.get_json()
    
    if not data or 'aadhaar_number' not in data:
        return jsonify({"error": "aadhaar_number is required"}), 400
    
    if 'consent' not in data or not data['consent']:
        return jsonify({"error": "Consent is required"}), 403
    
    aadhaar = data['aadhaar_number']
    
    if not is_valid_aadhaar(aadhaar):
        return jsonify({"error": "Invalid Aadhaar format"}), 400
    
    if aadhaar in VALID_AADHAARS:
        return jsonify(VALID_AADHAARS[aadhaar]), 200
    else:
        return jsonify({"error": "Aadhaar not found"}), 400

@app.route('/api/v1/aadhaar/otp/generate', methods=['POST'])
def generate_otp():
    """Generate OTP for Aadhaar"""
    data = request.get_json()
    
    if not data or 'aadhaar_number' not in data:
        return jsonify({"error": "aadhaar_number is required"}), 400
    
    aadhaar = data['aadhaar_number']
    
    if not is_valid_aadhaar(aadhaar):
        return jsonify({"error": "Invalid Aadhaar format"}), 400
    
    if aadhaar in VALID_AADHAARS:
        # Dummy OTP generation
        otp = "123456"  # In real scenario, generate random and send via SMS/email
        txn_id = f"TXN{aadhaar[:6]}"
        OTPS[txn_id] = {"aadhaar": aadhaar, "otp": otp}
        return jsonify({
            "transaction_id": txn_id,
            "message": "OTP sent to registered mobile"
        }), 200
    else:
        return jsonify({"error": "Aadhaar not found"}), 400

@app.route('/api/v1/aadhaar/otp/verify', methods=['POST'])
def verify_otp():
    """Verify OTP for Aadhaar authentication"""
    data = request.get_json()
    
    if not data or 'transaction_id' not in data or 'otp' not in data:
        return jsonify({"error": "transaction_id and otp are required"}), 400
    
    txn_id = data['transaction_id']
    otp = data['otp']
    
    if txn_id in OTPS and OTPS[txn_id]['otp'] == otp:
        aadhaar = OTPS[txn_id]['aadhaar']
        del OTPS[txn_id]  # OTP is one-time use
        return jsonify({
            "status": "success",
            "message": "OTP verified successfully",
            "aadhaar_number": aadhaar
        }), 200
    else:
        return jsonify({"error": "Invalid or expired OTP"}), 400

@app.route('/api/v1/aadhaar/ekyc', methods=['POST'])
def ekyc_auth():
    """Perform eKYC after OTP verification (dummy)"""
    data = request.get_json()
    
    if not data or 'aadhaar_number' not in data or 'transaction_id' not in data:
        return jsonify({"error": "aadhaar_number and transaction_id are required"}), 400
    
    if 'consent' not in data or not data['consent']:
        return jsonify({"error": "Consent is required"}), 403
    
    aadhaar = data['aadhaar_number']
    txn_id = data['transaction_id']
    
    if not is_valid_aadhaar(aadhaar):
        return jsonify({"error": "Invalid Aadhaar format"}), 400
    
    # Check if recent OTP was verified (in real, use session or token)
    # For dummy, assume if aadhaar exists and txn matches pattern
    if aadhaar in VALID_AADHAARS and txn_id.startswith(f"TXN{aadhaar[:6]}"):
        return jsonify({
            "status": "success",
            "message": "eKYC completed",
            "details": VALID_AADHAARS[aadhaar],
            "xml_signature": "<dummy_signed_xml>signed_data</dummy_signed_xml>"  # Dummy PID block or signature
        }), 200
    else:
        return jsonify({"error": "Authentication failed or Aadhaar not found"}), 400

@app.route('/health', methods=['GET'])
@app.route('/api/v1/health', methods=['GET'])
def health():
    """
    Health check endpoint.
    
    Available at both /health and /api/v1/health for compatibility.
    
    Returns:
        JSON response with health status
    """
    return jsonify({"status": "healthy"}), 200

# TEST SCENARIO: Traffic Replay - Record all requests
if TEST_MODE['traffic_replay']:
    @app.before_request
    def record_request_start():
        """Record request start time"""
        request.start_time = time.time()
    
    @app.after_request
    def record_request_complete(response):
        """Record completed request for traffic replay"""
        if hasattr(request, 'start_time'):
            duration_ms = (time.time() - request.start_time) * 1000
            
            # Send to dashboard for traffic replay visualization
            try:
                import requests as req
                req.post('http://localhost:5050/api/event', json={
                    'type': 'traffic',
                    'method': request.method,
                    'url': request.url,
                    'status_code': response.status_code,
                    'duration_ms': round(duration_ms, 2)
                }, timeout=0.5)
            except:
                pass  # Dashboard might not be running, that's okay
        
        return response

@app.route('/api/v1/aadhaar/masked-aadhaar', methods=['GET'])
def get_masked_aadhaar():
    """Return masked Aadhaar number"""
    aadhaar = request.args.get('aadhaar_number')
    
    if not aadhaar:
        return jsonify({"error": "aadhaar_number parameter is required"}), 400
    
    if not is_valid_aadhaar(aadhaar):
        return jsonify({"error": "Invalid Aadhaar format"}), 400
    
    # Mask first 8 digits
    masked = "XXXXXXXX" + aadhaar[-4:]
    
    return jsonify({
        "masked_aadhaar": masked,
        "status": "success"
    }), 200

@app.route('/api/v1/aadhaar/face-authentication', methods=['POST'])
def face_authentication():
    """Face-based authentication (new feature)"""
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "Request body is required"}), 400
    
    aadhaar = data.get('aadhaar_number')
    face_image = data.get('face_image')
    
    if not aadhaar or not face_image:
        return jsonify({"error": "aadhaar_number and face_image are required"}), 400
    
    if not is_valid_aadhaar(aadhaar):
        return jsonify({"error": "Invalid Aadhaar format"}), 400
    
    # Simulate face matching
    # For demo: valid Aadhaars with face_image containing "valid" will match
    if aadhaar in VALID_AADHAARS and "valid" in face_image.lower():
        return jsonify({
            "status": "authenticated",
            "confidence_score": 0.95,
            "match": True
        }), 200
    else:
        return jsonify({
            "status": "authentication_failed",
            "match": False
        }), 401

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 Starting Dummy Aadhaar API on http://localhost:5001")
    print("="*60)
    print("\n📊 TEST MODES (Edit TEST_MODE dict to enable):")
    print(f"   ✅ Self-Healing: {'ENABLED' if TEST_MODE['self_healing'] else 'DISABLED'} - Changes status codes to trigger test failures")
    print(f"   ✅ Error Analysis: {'ENABLED' if TEST_MODE['error_analysis'] else 'DISABLED'} - Requires auth header")
    print(f"   ✅ Anomaly Detection: {'ENABLED' if TEST_MODE['anomaly_detection'] else 'DISABLED'} - Adds delays and errors")
    print(f"   ✅ Traffic Replay: {'ENABLED' if TEST_MODE['traffic_replay'] else 'DISABLED'} - Records all requests")
    print("\n💡 To test each scenario:")
    print("   1. Set the TEST_MODE flag to True")
    print("   2. Restart this API server")
    print("   3. Run: python main.py --spec specs/aadhaar-api.yaml")
    print("   4. Check dashboard at http://localhost:5050")
    print("\n" + "="*60 + "\n")
    
    app.run(host='0.0.0.0', port=5001, debug=True)