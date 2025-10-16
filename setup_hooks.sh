#!/bin/bash

echo "🔧 Setting up Git hooks for auto-trigger..."

# Create hooks directory if it doesn't exist
mkdir -p .git/hooks

# Create post-commit hook
cat > .git/hooks/post-commit << 'EOF'
#!/bin/bash

# Get list of changed files in the last commit
CHANGED_FILES=$(git diff-tree --no-commit-id --name-only -r HEAD)

# Check if any spec files were modified
if echo "$CHANGED_FILES" | grep -q "specs/"; then
    echo "🔔 API specification changed! Triggering AI test generation..."
    echo "Changed files: $CHANGED_FILES"
    
    # Run POC in background to avoid blocking the commit
    nohup python main.py > poc_output.log 2>&1 &
    
    echo "✅ AI test generation started in background"
    echo "📊 View progress at: http://localhost:8080"
    echo "📝 Check logs: tail -f poc_output.log"
else
    echo "ℹ️  No spec files changed, skipping test generation"
fi
EOF

# Make hook executable
chmod +x .git/hooks/post-commit

echo "✅ Git hook installed successfully!"
echo ""
echo "Test it:"
echo "1. Edit specs/aadhaar-api.yaml"
echo "2. git add specs/aadhaar-api.yaml"
echo "3. git commit -m 'Updated API spec'"
echo "4. Watch POC auto-run! 🎉"