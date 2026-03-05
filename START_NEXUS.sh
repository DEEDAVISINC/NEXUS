#!/bin/bash

# NEXUS Unified Launcher
# ======================
# Start both the Flask API backend and React frontend with one command
# Usage: ./START_NEXUS.sh

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                                                            ║${NC}"
echo -e "${BLUE}║              🌐 NEXUS COMMAND CENTER v1.0                  ║${NC}"
echo -e "${BLUE}║                                                            ║${NC}"
echo -e "${BLUE}║     Enterprise Contract Management & AI Automation        ║${NC}"
echo -e "${BLUE}║                                                            ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Get the directory where this script is located
NEXUS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$NEXUS_DIR"

# Check if virtual environment exists
if [ ! -d "$NEXUS_DIR/venv" ]; then
    echo -e "${YELLOW}⚠️  Virtual environment not found. Creating one...${NC}"
    python3 -m venv "$NEXUS_DIR/venv"
    source "$NEXUS_DIR/venv/bin/activate"
    pip install -r requirements.txt --quiet
else
    source "$NEXUS_DIR/venv/bin/activate"
fi

# Function to cleanup processes on exit
cleanup() {
    echo ""
    echo -e "${YELLOW}🛑 Shutting down NEXUS...${NC}"
    if [ -n "$API_PID" ]; then
        kill $API_PID 2>/dev/null || true
        echo -e "${GREEN}   ✓ API Server stopped${NC}"
    fi
    if [ -n "$REACT_PID" ]; then
        kill $REACT_PID 2>/dev/null || true
        echo -e "${GREEN}   ✓ Frontend stopped${NC}"
    fi
    if [ -n "$INGESTION_PID" ]; then
        kill $INGESTION_PID 2>/dev/null || true
        echo -e "${GREEN}   ✓ Continuous Ingestion stopped${NC}"
    fi
    echo -e "${GREEN}👋 NEXUS is offline. See you next time!${NC}"
    exit 0
}

# Set up cleanup on script exit
trap cleanup INT TERM EXIT

# Check if API is already running
if lsof -ti:8000 > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Port 8000 is already in use. Killing existing process...${NC}"
    kill $(lsof -ti:8000) 2>/dev/null || true
    sleep 2
fi

# Check if React is already running
if lsof -ti:3000 > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Port 3000 is already in use. Killing existing process...${NC}"
    kill $(lsof -ti:3000) 2>/dev/null || true
    sleep 2
fi

echo ""
echo -e "${BLUE}🔧 Starting NEXUS Backend Services...${NC}"
echo ""

# Start the Flask API Server
echo -e "${BLUE}   → Starting Flask API Server on port 8000...${NC}"
python api_server.py > /tmp/nexus_api.log 2>&1 &
API_PID=$!

# Wait for API to be ready
echo -e "${BLUE}   → Waiting for API to initialize...${NC}"
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}   ✓ API Server running at http://localhost:8000${NC}"
        break
    fi
    sleep 1
    if [ $i -eq 30 ]; then
        echo -e "${RED}   ✗ API Server failed to start. Check /tmp/nexus_api.log${NC}"
        exit 1
    fi
done

echo ""

# Start Continuous Ingestion in background (optional)
if [ -f "$NEXUS_DIR/nexus_continuous_ingestion.py" ]; then
    echo -e "${BLUE}   → Starting Continuous Data Ingestion...${NC}"
    python "$NEXUS_DIR/nexus_continuous_ingestion.py" --daemon > /tmp/nexus_ingestion.log 2>&1 &
    INGESTION_PID=$!
    echo -e "${GREEN}   ✓ Continuous Ingestion running (PID: $INGESTION_PID)${NC}"
    echo ""
fi

# Start the React Frontend
echo -e "${BLUE}🔧 Starting NEXUS Frontend...${NC}"
cd "$NEXUS_DIR/nexus-frontend"
echo -e "${BLUE}   → Starting React development server on port 3000...${NC}"
npm start > /tmp/nexus_react.log 2>&1 &
REACT_PID=$!

# Wait for React to be ready
echo -e "${BLUE}   → Waiting for React to compile...${NC}"
for i in {1..60}; do
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        echo -e "${GREEN}   ✓ Frontend running at http://localhost:3000${NC}"
        break
    fi
    sleep 2
    if [ $i -eq 60 ]; then
        echo -e "${RED}   ✗ Frontend failed to start. Check /tmp/nexus_react.log${NC}"
        exit 1
    fi
done

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  ✅ NEXUS IS FULLY OPERATIONAL                            ║${NC}"
echo -e "${GREEN}╠════════════════════════════════════════════════════════════╣${NC}"
echo -e "${GREEN}║                                                            ║${NC}"
echo -e "${GREEN}║  🌐 NEXUS Dashboard:    http://localhost:3000               ║${NC}"
echo -e "${GREEN}║  🔌 API Server:       http://localhost:8000               ║${NC}"
echo -e "${GREEN}║                                                            ║${NC}"
echo -e "${GREEN}║  📋 Available Systems:                                    ║${NC}"
echo -e "${GREEN}║     • NOVA - Federal Opportunity Discovery                  ║${NC}"
echo -e "${GREEN}║     • GPSS - Government Pipeline Management                 ║${NC}"
echo -e "${GREEN}║     • ATLAS - Project Management                          ║${NC}"
echo -e "${GREEN}║     • PRISM - Field Service Operations                      ║${NC}"
echo -e "${GREEN}║     • COMPASS - Post-Award Fulfillment                    ║${NC}"
echo -e "${GREEN}║     • VERTEX - Financial Command Center                   ║${NC}"
echo -e "${GREEN}║                                                            ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Open browser
echo -e "${BLUE}🌐 Opening NEXUS in your browser...${NC}"
sleep 2
open "http://localhost:3000" || xdg-open "http://localhost:3000" || echo -e "${YELLOW}   Please manually open: http://localhost:3000${NC}"

echo ""
echo -e "${YELLOW}💡 Press Ctrl+C to stop NEXUS${NC}"
echo ""

# Keep script running
echo -e "${BLUE}📊 Monitoring NEXUS services...${NC}"
while true; do
    # Check if processes are still running
    if ! kill -0 $API_PID 2>/dev/null; then
        echo -e "${RED}⚠️  API Server has stopped unexpectedly!${NC}"
        echo -e "${BLUE}🔄 Attempting to restart...${NC}"
        python api_server.py > /tmp/nexus_api.log 2>&1 &
        API_PID=$!
        sleep 5
    fi
    
    if ! kill -0 $REACT_PID 2>/dev/null; then
        echo -e "${RED}⚠️  Frontend has stopped unexpectedly!${NC}"
        echo -e "${BLUE}🔄 Attempting to restart...${NC}"
        cd "$NEXUS_DIR/nexus-frontend"
        npm start > /tmp/nexus_react.log 2>&1 &
        REACT_PID=$!
        sleep 10
    fi
    
    sleep 5
done
