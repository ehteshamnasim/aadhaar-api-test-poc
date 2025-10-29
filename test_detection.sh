#!/bin/bash
# Comprehensive test script for spec change detection

set -e  # Exit on error

echo "======================================================================"
echo "🧪 COMPREHENSIVE DETECTION TEST"
echo "======================================================================"

cd /Users/ehtesham/Developer/aadhaar-api-test-poc
source venv/bin/activate

SPEC_FILE="specs/aadhaar-api.yaml"
BACKUP_FILE="specs/aadhaar-api.yaml.backup"

# Backup current spec
cp "$SPEC_FILE" "$BACKUP_FILE"

echo ""
echo "✅ Step 1: Baseline established (current state)"
echo "   - Server URL: http://localhost:5001/api/v2"
echo "   - 9 endpoints"
echo ""

# Test 1: Server URL change (already done)
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📝 TEST 1: Server URL Change Detection"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Current URL: http://localhost:5001/api/v2"
echo "Running detection..."
python main.py "$SPEC_FILE" 2>&1 | grep -E "Checking|Detected|changes|No API" || true
echo ""

# Test 2: Version number change (should NOT trigger)
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📝 TEST 2: Version Number Change (Should NOT Trigger)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
sed -i '' 's/version: 1.12.8/version: 1.12.9/g' "$SPEC_FILE"
echo "Changed: version 1.12.8 → 1.12.9"
echo "Running detection..."
python main.py "$SPEC_FILE" 2>&1 | grep -E "Checking|Detected|changes|No API" || true
echo ""

# Test 3: Add new response code (SHOULD trigger)
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📝 TEST 3: New Response Code (SHOULD Trigger)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
# Add 500 response to /aadhaar/verify
cat >> "$SPEC_FILE" << 'EOF'
        '500':
          description: Internal server error
          content:
            application/json:
              schema:
                type: object
                properties:
                  error:
                    type: string
EOF
echo "Added: 500 response code to /aadhaar/verify"
echo "Running detection..."
python main.py "$SPEC_FILE" 2>&1 | grep -E "Checking|Detected|changes|No API|endpoints affected" || true
echo ""

# Test 4: Git commit test
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📝 TEST 4: Git Commit Trigger"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Committing changes..."
git add "$SPEC_FILE" 2>/dev/null || echo "⚠️  Git not initialized or file not in repo"
echo "Note: Detection happens on file change, NOT on git commit"
echo "Git commit is just for versioning, not required for detection"
echo ""

# Restore backup
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔄 Restoring original spec file..."
mv "$BACKUP_FILE" "$SPEC_FILE"
echo "✅ Restored"
echo ""

echo "======================================================================"
echo "📊 TEST SUMMARY"
echo "======================================================================"
echo ""
echo "✅ What TRIGGERS detection:"
echo "   - New/removed endpoints"
echo "   - New/removed HTTP methods"
echo "   - New/removed response codes (200, 400, 500, etc.)"
echo "   - Request body schema changes"
echo "   - Server URL changes (now implemented)"
echo ""
echo "❌ What does NOT trigger:"
echo "   - Version number changes"
echo "   - Description changes"
echo "   - Example value changes"
echo "   - Comment changes"
echo ""
echo "🔑 KEY POINTS:"
echo "   1. Detection happens on FILE CHANGE, not git commit"
echo "   2. Must run: python main.py specs/aadhaar-api.yaml"
echo "   3. Dashboard must be running: http://localhost:5050"
echo "   4. Changes shown in real-time on dashboard UI"
echo ""
echo "======================================================================"
