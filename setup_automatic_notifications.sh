#!/bin/bash
# Setup Automatic NEXUS Notifications
# Created: February 5, 2026

echo "🚀 Setting up AUTOMATIC NEXUS Notifications..."
echo ""

# Get current crontab
crontab -l > /tmp/current_cron 2>/dev/null || touch /tmp/current_cron

# Remove old NEXUS notification entries if they exist
grep -v "send_bid_notifications.py" /tmp/current_cron > /tmp/new_cron
grep -v "NEXUS URGENT NOTIFICATIONS" /tmp/new_cron > /tmp/current_cron
mv /tmp/current_cron /tmp/new_cron

# Add new NEXUS notification cron jobs
cat >> /tmp/new_cron << 'EOF'

# =====================================================================
# NEXUS URGENT NOTIFICATIONS (Auto-check for deadlines ≤ 3 days)
# =====================================================================

# Morning check (7 AM) - Primary notification time
0 7 * * * cd /Users/deedavis/NEXUS\ BACKEND && /usr/local/bin/python3 send_bid_notifications.py >> /tmp/nexus_notifications.log 2>&1

# Midday check (12 PM) - Catch any urgent bids
0 12 * * * cd /Users/deedavis/NEXUS\ BACKEND && /usr/local/bin/python3 send_bid_notifications.py >> /tmp/nexus_notifications.log 2>&1

# Evening check (6 PM) - Final daily check
0 18 * * * cd /Users/deedavis/NEXUS\ BACKEND && /usr/local/bin/python3 send_bid_notifications.py >> /tmp/nexus_notifications.log 2>&1

# CRITICAL: Day-of deadline check every 2 hours (6 AM - 8 PM)
0 6,8,10,12,14,16,18,20 * * * cd /Users/deedavis/NEXUS\ BACKEND && /usr/local/bin/python3 send_bid_notifications.py >> /tmp/nexus_notifications.log 2>&1

EOF

# Install new crontab
crontab /tmp/new_cron

# Cleanup
rm /tmp/new_cron

echo "✅ Automatic notifications installed!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📧 EMAIL SCHEDULE (AUTOMATIC):"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Daily checks: 7 AM, 12 PM, 6 PM"
echo "Critical check: Every 2 hours (6 AM - 8 PM)"
echo ""
echo "YOU WILL ONLY GET EMAILS FOR:"
echo "  🔴 Bids due TODAY"
echo "  🔴 Bids due TOMORROW"
echo "  🟡 Bids due in 2 days"
echo "  🟡 Bids due in 3 days"
echo ""
echo "YOU WILL NOT GET EMAILS FOR:"
echo "  ❌ Bids > 3 days away (check NEXUS banner)"
echo "  ❌ Daily summaries (removed)"
echo "  ❌ Status updates (removed)"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 LOGS:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "View notification log:"
echo "  tail -f /tmp/nexus_notifications.log"
echo ""
echo "View current cron jobs:"
echo "  crontab -l"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🎯 SYSTEM IS NOW RUNNING AUTOMATICALLY!"
echo ""
echo "Next automatic check: Tomorrow at 7:00 AM"
echo "Emails sent to: bids.deedavisinc@gmail.com"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
