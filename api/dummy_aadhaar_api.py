from flask import Flask, request, jsonify
import re

app = Flask(__name__)

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
    data = request.get_json()
    
    if not data or 'aadhaar_number' not in data:
        return jsonify({"status": "invalid", "error": "aadhaar_number is required"}), 400
    
    aadhaar = data['aadhaar_number']
    
    if not is_valid_aadhaar(aadhaar):
        return jsonify({"status": "invalid", "error": "Aadhaar must be 12 digits"}), 400
    
    if aadhaar in VALID_AADHAARS:
        return jsonify({"status": "valid", "message": "Aadhaar number is valid"}), 200
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
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy"}), 200

if __name__ == '__main__':
    print("Starting Dummy Aadhaar API on http://localhost:5001")
    app.run(host='0.0.0.0', port=5001, debug=True)