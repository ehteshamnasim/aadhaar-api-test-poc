#!/bin/bash

echo "🧪 Testing Git Hook Auto-Trigger"
echo "================================"

# Backup original spec
cp specs/aadhaar-api.yaml specs/aadhaar-api.yaml.backup

# Make a small change to spec
echo ""
echo "1. Making a change to API spec..."
sed -i.bak 's/version: 1.0.0/version: 1.0.1/' specs/aadhaar-api.yaml

# Show the change
echo "2. Change made:"
git diff specs/aadhaar-api.yaml | head -10

# Commit the change
echo ""
echo "3. Committing change (this should trigger POC)..."
git add specs/aadhaar-api.yaml
git commit -m "Test: Updated API version to trigger auto-generation"

echo ""
echo "4. Check if POC started:"
sleep 3
if ps aux | grep -q "[p]ython main.py"; then
    echo "✅ POC is running in background!"
    echo "📊 View dashboard: http://localhost:8080"
    echo "📝 View logs: tail -f poc_output.log"
else
    echo "❌ POC did not start. Check the hook setup."
fi

# Restore backup
mv specs/aadhaar-api.yaml.backup specs/aadhaar-api.yaml