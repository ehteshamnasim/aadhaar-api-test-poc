#!/bin/bash

echo "🚀 Setting up AI-Powered API Test Automation POC"
echo "================================================"

# Create directories
mkdir -p tests htmlcov .git/hooks

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Check for Ollama
echo ""
echo "🔍 Checking Ollama installation..."
if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama not found!"
    echo ""
    echo "Please install Ollama:"
    echo "  macOS/Linux: curl https://ollama.ai/install.sh | sh"
    echo "  Windows: Download from https://ollama.ai"
    echo ""
    exit 1
fi

echo "✅ Ollama is installed"

# Check if Ollama is running
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo ""
    echo "⚠️  Ollama is not running!"
    echo "   Start it with: ollama serve"
    echo ""
else
    echo "✅ Ollama is running"
fi

# Check for llama3:70b model
echo ""
echo "🔍 Checking for llama3:70b model..."
if ollama list | grep -q "llama3:70b"; then
    echo "✅ llama3:70b model found"
else
    echo "❌ llama3:70b model not found!"
    echo ""
    echo "Pulling llama3:70b model (this may take a while)..."
    echo "   Note: This model is ~40GB in size"
    echo ""
    read -p "Do you want to pull it now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        ollama pull llama3:70b
    else
        echo "⚠️  You'll need to pull it manually: ollama pull llama3:70b"
    fi
fi

# Initialize git if not exists
if [ ! -d .git ]; then
    echo ""
    echo "📝 Initializing Git repository..."
    git init
    git config user.name "AI Test Bot"
    git config user.email "ai-bot@example.com"
    
    # Initial commit
    git add .
    git commit -m "Initial commit: POC setup" --no-verify
fi

# Setup Git hooks
echo ""
echo "🔧 Setting up Git hooks..."
./setup_hooks.sh

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Ensure Ollama is running: ollama serve"
echo "2. Start API (Terminal 1): python api/dummy_aadhaar_api.py"
echo "3. Test auto-trigger:"
echo "   - Edit specs/aadhaar-api.yaml"
echo "   - git add specs/aadhaar-api.yaml"
echo "   - git commit -m 'Updated spec'"
echo "   - Watch POC auto-run! 🎉"
echo ""
echo "Or run manually: python main.py"
echo "Dashboard: http://localhost:8080"