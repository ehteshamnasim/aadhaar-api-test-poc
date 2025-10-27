#!/bin/bash

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Complete Dashboard Integration Test  ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
echo ""

# Activate venv
if [ ! -d "venv" ]; then
    echo -e "${RED}✗ No virtual environment found${NC}"
    echo "Run: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

source venv/bin/activate
echo -e "${GREEN}✓ Virtual environment activated${NC}"

# Check dependencies
echo ""
echo "Checking dependencies..."
python -c "import requests, flask, yaml" 2>/dev/null
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ All dependencies installed${NC}"
else
    echo -e "${RED}✗ Missing dependencies${NC}"
    echo "Installing..."
    pip install -r requirements.txt
fi

# Check if dashboard is running
echo ""
echo "Checking dashboard status..."
if ! lsof -Pi :5050 -sTCP:LISTEN -t >/dev/null ; then
    echo -e "${YELLOW}⚠ Dashboard not running${NC}"
    echo "Starting dashboard..."
    python start_dashboard.py > dashboard.log 2>&1 &
    DASH_PID=$!
    sleep 3
    
    if lsof -Pi :5050 -sTCP:LISTEN -t >/dev/null ; then
        echo -e "${GREEN}✓ Dashboard started (PID: $DASH_PID)${NC}"
    else
        echo -e "${RED}✗ Failed to start dashboard${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✓ Dashboard is running${NC}"
fi

# Run diagnostic
echo ""
echo -e "${BLUE}Running diagnostic tests...${NC}"
echo "─────────────────────────────────"
python diagnose_dashboard.py

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║        ✓ ALL TESTS PASSED!            ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${BLUE}Dashboard Status:${NC}"
    echo "  URL: http://localhost:5050"
    echo "  Status: Running"
    echo "  Events: Working"
    echo ""
    echo -e "${BLUE}Next Steps:${NC}"
    echo "  1. Open browser: http://localhost:5050"
    echo "  2. Run main.py: python main.py"
    echo "  3. Watch all 5 tabs populate with data"
    echo ""
    echo -e "${YELLOW}Tabs that will show data:${NC}"
    echo "  • Overview - Always has data"
    echo "  • Self-Healing - When tests fail and are healed"
    echo "  • Error Analysis - When tests fail"
    echo "  • API Diff - When spec changes detected"
    echo "  • Anomalies - When issues detected"
    echo ""
    
    # Open browser
    echo "Opening dashboard in browser..."
    sleep 1
    open http://localhost:5050 2>/dev/null || xdg-open http://localhost:5050 2>/dev/null || echo "Please open: http://localhost:5050"
    
else
    echo ""
    echo -e "${RED}╔════════════════════════════════════════╗${NC}"
    echo -e "${RED}║        ✗ TESTS FAILED!                ║${NC}"
    echo -e "${RED}╚════════════════════════════════════════╝${NC}"
    echo ""
    echo "Check the output above for errors"
    exit 1
fi
