#!/bin/bash

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Starting Dashboard System${NC}"
echo "======================================"

# Check if venv exists
if [ ! -d "venv" ]; then
    echo -e "${RED}✗ Virtual environment not found!${NC}"
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    echo -e "${GREEN}✓ Virtual environment found${NC}"
    source venv/bin/activate
fi

# Check if dashboard is already running
if lsof -Pi :5050 -sTCP:LISTEN -t >/dev/null ; then
    echo -e "${YELLOW}⚠ Dashboard already running on port 5050${NC}"
    read -p "Kill existing process and restart? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        lsof -ti:5050 | xargs kill -9 2>/dev/null
        echo -e "${GREEN}✓ Killed existing process${NC}"
    else
        echo "Using existing dashboard"
        open http://localhost:5050
        exit 0
    fi
fi

# Start dashboard in background
echo -e "${GREEN}Starting dashboard server...${NC}"
python start_dashboard.py > dashboard.log 2>&1 &
DASH_PID=$!

# Wait for dashboard to start
sleep 2

# Check if dashboard is running
if lsof -Pi :5050 -sTCP:LISTEN -t >/dev/null ; then
    echo -e "${GREEN}✓ Dashboard started successfully (PID: $DASH_PID)${NC}"
    echo -e "${GREEN}✓ Dashboard available at: http://localhost:5050${NC}"
    
    # Run diagnostic
    echo ""
    echo "Running diagnostic tests..."
    python diagnose_dashboard.py
    
    echo ""
    echo -e "${GREEN}======================================"
    echo "Dashboard is ready!"
    echo "======================================"
    echo ""
    echo "Next steps:"
    echo "1. Open browser: http://localhost:5050"
    echo "2. Run tests: python main.py"
    echo "3. Watch dashboard update in real-time"
    echo ""
    echo "To stop dashboard: kill $DASH_PID"
    echo -e "Or run: lsof -ti:5050 | xargs kill${NC}"
    echo ""
    
    # Open browser
    sleep 1
    open http://localhost:5050
    
else
    echo -e "${RED}✗ Failed to start dashboard${NC}"
    echo "Check dashboard.log for errors"
    exit 1
fi
