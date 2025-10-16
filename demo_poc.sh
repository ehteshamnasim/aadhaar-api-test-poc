#!/bin/bash

clear

cat << "EOF"
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║     🤖 AI-Powered API Test Automation POC Demo 🤖        ║
║                                                           ║
║              Fully Autonomous Test Generation            ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
EOF

echo ""
echo "Demo Flow:"
echo "=========="
echo "1. Developer commits API spec"
echo "2. AI auto-generates tests (40-60s)"
echo "3. Tests run locally"
echo "4. Auto-commit + auto-push"
echo "5. CI/CD triggers on GitHub"
echo "6. Real-time dashboard updates"
echo ""

read -p "Press Enter to start demo..." 

echo ""
echo "🔍 Checking prerequisites..."
echo ""

# Check services
check_service() {
    if curl -s $1 > /dev/null 2>&1; then
        echo "✅ $2"
        return 0
    else
        echo "❌ $2 not running"
        echo "   Start with: $3"
        return 1
    fi
}

ALL_GOOD=true

check_service "http://localhost:11434/api/tags" "Ollama" "ollama serve" || ALL_GOOD=false
check_service "http://localhost:5000/health" "Dummy API" "python3 api/dummy_aadhaar_api.py" || ALL_GOOD=false
check_service "http://localhost:8080/api/health" "Dashboard" "python3 start_dashboard.py" || ALL_GOOD=false

if [ "$ALL_GOOD" = false ]; then
    echo ""
    echo "❌ Please start all services first!"
    exit 1
fi

echo ""
echo "✅ All services running!"
echo ""

# Show current state
echo "📊 Current State:"
echo "════════════════"
git log -1 --oneline
echo ""

if [ -f tests/test_aadhaar_api.py ]; then
    LINES=$(wc -l < tests/test_aadhaar_api.py)
    TESTS=$(grep -c "def test_" tests/test_aadhaar_api.py)
    echo "Current tests: $TESTS test cases ($LINES lines)"
else
    echo "No tests exist yet"
fi

echo ""
read -p "Press Enter to trigger AI test generation..." 

echo ""
echo "🚀 Triggering POC..."
echo ""

# Update spec
echo "# Demo update: $(date)" >> specs/aadhaar-api.yaml

# Commit (triggers POC)
git add specs/aadhaar-api.yaml
git commit -m "Demo: API spec updated"

echo ""
echo "✅ POC triggered!"
echo ""
echo "📊 Watch progress:"
echo "   Dashboard: http://localhost:8080"
echo "   Logs: tail -f poc_output.log"
echo ""
echo "⏱️  Expected time: 40-60 seconds"
echo ""
echo "Wait for completion message..."

# Wait for POC to complete (check for completion in log)
timeout=120
elapsed=0
while [ $elapsed -lt $timeout ]; do
    if tail -1 poc_output.log 2>/dev/null | grep -q "POC COMPLETED"; then
        echo ""
        echo "✅ POC Completed!"
        break
    fi
    sleep 2
    elapsed=$((elapsed + 2))
    echo -ne "\rElapsed: ${elapsed}s"
done

echo ""
echo ""
echo "📋 Results:"
echo "═══════════"

# Show new commits
echo ""
echo "Git commits:"
git log -2 --oneline

echo ""
if [ -f tests/test_aadhaar_api.py ]; then
    LINES=$(wc -l < tests/test_aadhaar_api.py)
    TESTS=$(grep -c "def test_" tests/test_aadhaar_api.py)
    echo "Generated: $TESTS test cases ($LINES lines)"
fi

echo ""
echo "🌐 View results:"
echo "   Dashboard: http://localhost:8080"
echo "   Coverage: http://localhost:8080/coverage-report"
echo "   Tests: http://localhost:8080/generated-tests"

echo ""
echo "📊 Check GitHub Actions:"
git remote get-url origin 2>/dev/null && echo "   $(git remote get-url origin | sed 's/.git$//')/actions"

echo ""
echo "✅ Demo complete!"
echo ""