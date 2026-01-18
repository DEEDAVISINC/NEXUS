#!/bin/bash

# NEXUS Startup Script
# Run this to start your system cleanly

echo "🚀 Starting NEXUS System..."
echo ""

# Kill existing processes
echo "1. Cleaning up old processes..."
lsof -ti:3000 | xargs kill -9 2>/dev/null
lsof -ti:8000 | xargs kill -9 2>/dev/null
sleep 2

# Start backend
echo "2. Starting Backend..."
cd "/Users/deedavis/NEXUS BACKEND"
python3 api_server.py > backend.log 2>&1 &
BACKEND_PID=$!
echo "   Backend PID: $BACKEND_PID"
sleep 5

# Check if backend started
if curl -s http://localhost:8000/health > /dev/null; then
    echo "   ✅ Backend is running!"
else
    echo "   ❌ Backend failed to start. Check backend.log"
    exit 1
fi

# Start frontend
echo "3. Starting Frontend..."
cd "/Users/deedavis/NEXUS BACKEND/nexus-frontend"
npm start > ../frontend.log 2>&1 &
FRONTEND_PID=$!
echo "   Frontend PID: $FRONTEND_PID"

echo ""
echo "✅ NEXUS is starting up!"
echo ""
echo "📊 Monitor logs:"
echo "   Backend:  tail -f backend.log"
echo "   Frontend: tail -f frontend.log"
echo ""
echo "🌐 Access: http://localhost:3000"
echo ""
echo "🛑 Stop NEXUS:"
echo "   kill $BACKEND_PID $FRONTEND_PID"
echo ""
