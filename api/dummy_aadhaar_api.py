from flask import Flask, request, jsonify
import re

app = Flask(__name__)

# Dummy valid Aadhaar numbers for testing
VALID_AADHAARS = {
    "123456789012": {"name": "Eht****** Kum**", "dob": "1990-01-01", "gender": "M", "address": "Delhi, ****10"},
    "987654321098": {"name": "Pri****** Sha**", "dob": "1995-05-15", "gender": "F", "address": "Mumbai, ****20"}
}

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
        return jsonify({
            "transaction_id": f"TXN{aadhaar[:6]}",
            "message": "OTP sent to registered mobile"
        }), 200
    else:
        return jsonify({"error": "Aadhaar not found"}), 400

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy"}), 200

if __name__ == '__main__':
    print("Starting Dummy Aadhaar API on http://localhost:5001")
    app.run(host='0.0.0.0', port=5001, debug=True)