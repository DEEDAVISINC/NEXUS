#!/bin/bash
# Start NEXUS with Notification System
# Created: February 5, 2026

echo "🚀 Starting NEXUS with Notification System..."
echo ""

# Start backend
echo "📡 Starting NEXUS Backend (Port 8000)..."
cd "/Users/deedavis/NEXUS BACKEND"
python3 api_server.py &
BACKEND_PID=$!
echo "   Backend PID: $BACKEND_PID"
sleep 3

# Start frontend
echo "🌐 Starting NEXUS Frontend (Port 3000)..."
cd "/Users/deedavis/NEXUS BACKEND/nexus-frontend"
npm start &
FRONTEND_PID=$!
echo "   Frontend PID: $FRONTEND_PID"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ NEXUS IS RUNNING WITH NOTIFICATIONS!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🌐 Frontend: http://localhost:3000"
echo "📡 Backend API: http://localhost:8000"
echo "📧 Email Notifications: bids.deedavisinc@gmail.com"
echo ""
echo "🎯 YOU WILL NOW SEE:"
echo "  ✅ Deadline banner at top of NEXUS"
echo "  ✅ All 4 active RCOC bids displayed"
echo "  ✅ Real-time countdown timers"
echo "  ✅ Color-coded urgency (🔴 Urgent, 🟡 This Week, 🟢 Upcoming)"
echo ""
echo "📧 TO SEND EMAIL NOTIFICATION:"
echo "  python3 send_bid_notifications.py"
echo ""
echo "⏹️  TO STOP NEXUS:"
echo "  kill $BACKEND_PID $FRONTEND_PID"
echo ""
echo "Press Ctrl+C to stop both services"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Wait for Ctrl+C
wait
