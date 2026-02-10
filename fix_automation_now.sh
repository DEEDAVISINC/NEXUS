#!/bin/bash
# Fix NEXUS Automation - Keep ONLY urgent notifications
# Created: February 5, 2026

echo "🔧 Fixing NEXUS Automation..."
echo ""

# Backup current crontab
crontab -l > /tmp/cron_backup_$(date +%Y%m%d_%H%M%S).txt
echo "✅ Backed up current crontab"

# Create new crontab with ONLY what we want
cat > /tmp/nexus_cron_clean.txt << 'EOF'
# =====================================================================
# NEXUS AUTOMATION - CLEAN & FOCUSED
# =====================================================================

# Email automation: Check inbox for new solicitations (hourly)
0 * * * * cd '/Users/deedavis/NEXUS BACKEND' && /usr/local/bin/python3 nexus_email_automation.py >> '/Users/deedavis/NEXUS BACKEND/nexus_email.log' 2>&1

# Mine federal forecasts (daily at 6 AM)
0 6 * * * cd "/Users/deedavis/NEXUS BACKEND" && /usr/local/bin/python3 mine_real_federal_forecasts.py >> federal_forecasts.log 2>&1

# =====================================================================
# NEXUS URGENT BID NOTIFICATIONS (ONLY bids ≤ 3 days)
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

# Install clean crontab
crontab /tmp/nexus_cron_clean.txt

echo "✅ Installed clean automation"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ NEXUS AUTOMATION - NOW RUNNING CLEAN"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🔴 REMOVED (too noisy):"
echo "  ❌ Calendar automation (867 opportunity emails)"
echo "  ❌ Daily deadline reports (all opportunities)"
echo "  ❌ Hourly opportunity processing"
echo ""
echo "✅ KEPT (essential):"
echo "  ✅ Email inbox monitoring (new solicitations)"
echo "  ✅ Federal forecast mining (daily at 6 AM)"
echo "  ✅ URGENT bid notifications (≤ 3 days ONLY)"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📧 YOU WILL NOW GET EMAILS FOR:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  🔴 Bids due TODAY"
echo "  🔴 Bids due TOMORROW"
echo "  🟡 Bids due in 2 days"
echo "  🟡 Bids due in 3 days"
echo "  📧 New solicitations in inbox"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "❌ YOU WILL NOT GET EMAILS FOR:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  ❌ Bids > 3 days away (check NEXUS banner)"
echo "  ❌ Daily opportunity summaries (removed)"
echo "  ❌ 867 opportunity emails (removed)"
echo "  ❌ Calendar generation spam (removed)"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 AUTOMATION SCHEDULE:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Daily: 6 AM - Mine federal forecasts"
echo "Daily: 7 AM, 12 PM, 6 PM - Check urgent bids"
echo "Hourly: Check inbox for new solicitations"
echo "Every 2 hours (6 AM-8 PM): Critical deadline checks"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "✅ AUTOMATION IS NOW CLEAN & FOCUSED!"
echo ""
echo "View active cron jobs:"
echo "  crontab -l"
echo ""
echo "View notification log:"
echo "  tail -f /tmp/nexus_notifications.log"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
