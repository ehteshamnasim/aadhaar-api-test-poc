#!/bin/bash

echo "🚀 Setting up API Test Automation Environment"
echo "=============================================="

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Install pytest-json-report for better test parsing
echo "📊 Installing pytest-json-report for accurate test results..."
pip install pytest-json-report

# Install coverage tools
echo "📈 Installing coverage tools..."
pip install coverage pytest-cov

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p tests
mkdir -p htmlcov
mkdir -p specs

# Set up Git hooks (optional)
echo "🔧 Setting up Git hooks..."
if [ -d ".git" ]; then
    # Create pre-commit hook to validate tests
    cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
echo "🧪 Running pre-commit validation..."

# Check if tests exist and are valid
if ls tests/test_*.py 1> /dev/null 2>&1; then
    echo "✅ Test files found"
    python -m py_compile tests/test_*.py
    if [ $? -eq 0 ]; then
        echo "✅ Test files are valid Python syntax"
    else
        echo "❌ Syntax errors in test files"
        exit 1
    fi
else
    echo "⚠️  No test files found"
fi

echo "✅ Pre-commit validation passed"
EOF
    chmod +x .git/hooks/pre-commit
fi

echo ""
echo "✅ Setup completed!"
echo ""
echo "🔧 Next steps:"
echo "1. Start the dummy API: python api/dummy_aadhaar_api.py"
echo "2. Start the dashboard: python dashboard/server.py"
echo "3. Run the automation: python main.py"
echo ""
echo "📋 Health checks:"
echo "• API health: curl http://localhost:5001/health"
echo "• Dashboard: http://localhost:8080"
echo "• Ollama: curl http://localhost:11434/api/tags"
echo ""