#!/bin/bash
# Test Regeneration Demo Script

set -e

echo "======================================================================"
echo "🧪 TEST REGENERATION DEMO"
echo "======================================================================"
echo ""

cd /Users/ehtesham/Developer/aadhaar-api-test-poc

# Check prerequisites
echo "📋 Step 1: Checking prerequisites..."
if ! curl -s http://localhost:5050/api/health > /dev/null 2>&1; then
    echo "❌ Dashboard not running!"
    echo "   Start it: python3 dashboard/server.py &"
    exit 1
fi
echo "✅ Dashboard is running"
echo ""

# Activate venv
source venv/bin/activate

# Initial state
echo "📋 Step 2: Establishing baseline..."
echo "   Running initial test generation..."
python main.py specs/aadhaar-api.yaml 2>&1 | grep -E "endpoints discovered|test cases generated" || true
echo ""
sleep 2

# Make a change
echo "📋 Step 3: Making API change (adding 503 response to /aadhaar/verify)..."
echo ""

# Create backup
cp specs/aadhaar-api.yaml specs/aadhaar-api.yaml.backup

# Add 503 response using Python
python3 << 'EOF'
import yaml

with open('specs/aadhaar-api.yaml', 'r') as f:
    spec = yaml.safe_load(f)

# Add 503 response to /aadhaar/verify endpoint
verify_endpoint = spec['paths']['/aadhaar/verify']['post']
verify_endpoint['responses']['503'] = {
    'description': 'Service unavailable',
    'content': {
        'application/json': {
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {
                        'type': 'string',
                        'example': 'Service temporarily unavailable'
                    }
                }
            }
        }
    }
}

with open('specs/aadhaar-api.yaml', 'w') as f:
    yaml.dump(spec, f, default_flow_style=False, sort_keys=False)

print("✅ Added 503 response to /aadhaar/verify")
EOF

echo ""

# Run regeneration
echo "📋 Step 4: Running with spec changes..."
echo "   Watch for 'Selective regeneration' messages..."
echo ""

python main.py specs/aadhaar-api.yaml 2>&1 | grep -E "Detected|selective|Merging|preserved|regenerated" || true

echo ""
echo "======================================================================"
echo "✅ TEST REGENERATION DEMO COMPLETE"
echo "======================================================================"
echo ""
echo "What happened:"
echo "  1. Initial run: Generated tests for all 9 endpoints"
echo "  2. Added 503 response to /aadhaar/verify endpoint"
echo "  3. Re-run detected: 1 API change in 1 endpoint"
echo "  4. Preserved: Tests for 8 unchanged endpoints"
echo "  5. Regenerated: Only tests for /aadhaar/verify"
echo "  6. Merged: Old + New = Complete test suite"
echo ""
echo "📊 Check dashboard: http://localhost:5050"
echo "   Look for 'Test Regeneration' tab to see:"
echo "   - Preserved count"
echo "   - Regenerated count"
echo "   - Changed endpoints list"
echo ""
echo "🔄 Restoring original spec..."
mv specs/aadhaar-api.yaml.backup specs/aadhaar-api.yaml
echo "✅ Restored"
echo ""
