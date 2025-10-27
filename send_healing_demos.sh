#!/bin/bash

echo "Sending healing events for your 9 failed test cases..."
echo

# Case 1: assert 200 == 400
curl -s -X POST http://localhost:5050/api/event -H "Content-Type: application/json" -d '{
  "type": "healing",
  "test_name": "test_verify_otp_success",
  "confidence": 0.85,
  "old_code": "assert response.status_code == 400",
  "new_code": "assert response.status_code == 200  # Auto-healed: API behavior changed",
  "diff": {
    "before": "assert response.status_code == 400",
    "after": "assert response.status_code == 200  # Auto-healed"
  }
}' && echo "✅ Sent: test_verify_otp_success (200 vs 400)"

# Case 2: assert 200 == 400
curl -s -X POST http://localhost:5050/api/event -H "Content-Type: application/json" -d '{
  "type": "healing",
  "test_name": "test_demographics_invalid_consent",
  "confidence": 0.85,
  "old_code": "assert response.status_code == 400",
  "new_code": "assert response.status_code == 200  # Auto-healed: Expected error but got success",
  "diff": {
    "before": "assert response.status_code == 400",
    "after": "assert response.status_code == 200"
  }
}' && echo "✅ Sent: test_demographics_invalid_consent (200 vs 400)"

# Case 3: assert 201 == 200
curl -s -X POST http://localhost:5050/api/event -H "Content-Type: application/json" -d '{
  "type": "healing",
  "test_name": "test_verify_aadhaar_success",
  "confidence": 0.95,
  "old_code": "assert response.status_code == 200",
  "new_code": "assert response.status_code == 201  # Auto-healed: API returns 201 Created",
  "diff": {
    "before": "assert response.status_code == 200",
    "after": "assert response.status_code == 201  # Created"
  }
}' && echo "✅ Sent: test_verify_aadhaar_success (201 vs 200)"

# Case 4: assert 200 == 401
curl -s -X POST http://localhost:5050/api/event -H "Content-Type: application/json" -d '{
  "type": "healing",
  "test_name": "test_protected_endpoint",
  "confidence": 0.88,
  "old_code": "assert response.status_code == 401",
  "new_code": "assert response.status_code == 200  # Auto-healed: Auth no longer required",
  "diff": {
    "before": "assert response.status_code == 401",
    "after": "assert response.status_code == 200"
  }
}' && echo "✅ Sent: test_protected_endpoint (200 vs 401)"

# Case 5: assert 200 == 403
curl -s -X POST http://localhost:5050/api/event -H "Content-Type: application/json" -d '{
  "type": "healing",
  "test_name": "test_forbidden_resource",
  "confidence": 0.88,
  "old_code": "assert response.status_code == 403",
  "new_code": "assert response.status_code == 200  # Auto-healed: Access now allowed",
  "diff": {
    "before": "assert response.status_code == 403",
    "after": "assert response.status_code == 200"
  }
}' && echo "✅ Sent: test_forbidden_resource (200 vs 403)"

echo
echo "========================================================================"
echo "✅ All 5 healing events sent successfully!"
echo "🎯 Open http://localhost:5050 → Self-Healing tab to see them"
echo "========================================================================"
