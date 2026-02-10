#!/bin/bash
# NEXUS System Status Check
# Created: February 5, 2026

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔍 NEXUS SYSTEM STATUS CHECK"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check backend
echo "1️⃣ Backend API (Port 8000):"
if lsof -i :8000 > /dev/null 2>&1; then
    echo "   ✅ RUNNING"
    BACKEND_PID=$(lsof -t -i:8000)
    echo "   PID: $BACKEND_PID"
else
    echo "   ❌ OFFLINE"
    echo "   To start: python3 api_server.py &"
fi
echo ""

# Check cron jobs
echo "2️⃣ Automation (Cron Jobs):"
CRON_COUNT=$(crontab -l 2>/dev/null | grep -c "send_bid_notifications.py")
if [ $CRON_COUNT -gt 0 ]; then
    echo "   ✅ INSTALLED ($CRON_COUNT notification jobs)"
    echo "   Schedule:"
    crontab -l | grep "send_bid_notifications" | head -3
else
    echo "   ❌ NOT INSTALLED"
    echo "   To install: ./setup_automatic_notifications.sh"
fi
echo ""

# Check for urgent bids
echo "3️⃣ Urgent Bids (≤ 3 days):"
python3 -c "
from datetime import datetime
bids = [
    {'id': 'RCOC 7732', 'deadline': datetime(2026, 2, 10, 14, 30)},
    {'id': 'RCOC 7842', 'deadline': datetime(2026, 2, 17, 14, 30)},
    {'id': 'RCOC 7814', 'deadline': datetime(2026, 2, 17, 14, 30)},
    {'id': 'RCOC 7790', 'deadline': datetime(2026, 2, 17, 14, 30)},
]
now = datetime.now()
urgent = [b for b in bids if (b['deadline'] - now).days <= 3]
if urgent:
    print('   🔴 URGENT:', len(urgent), 'bid(s)')
    for b in urgent:
        days = (b['deadline'] - now).days
        print(f'      • {b[\"id\"]}: {days} days')
else:
    print('   ✅ No urgent bids (all > 3 days away)')
" 2>/dev/null || echo "   ⚠️  Could not check (Python error)"
echo ""

# Check last notification
echo "4️⃣ Last Notification Check:"
if [ -f /tmp/nexus_notifications.log ]; then
    echo "   Last run:"
    tail -5 /tmp/nexus_notifications.log
else
    echo "   ❌ No log file found"
    echo "   System hasn't run yet"
fi
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 QUICK ACTIONS:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Start backend:    python3 api_server.py &"
echo "Test notification: python3 send_bid_notifications.py"
echo "View status page: open SYSTEM_STATUS.html"
echo "View logs:        tail -f /tmp/nexus_notifications.log"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
