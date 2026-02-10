#!/bin/bash
# Setup NEXUS Calendar Automation System
# Run this once to install dependencies and set up cron jobs

echo "🚀 Setting up NEXUS Calendar Automation System..."
echo ""

# Install required Python packages
echo "📦 Installing dependencies..."
pip3 install icalendar pyairtable

# Make scripts executable
chmod +x calendar_automation.py

# Create cron jobs
echo ""
echo "⏰ Setting up automated cron jobs..."

# Backup existing crontab
crontab -l > /tmp/crontab_backup_$(date +%Y%m%d_%H%M%S).txt 2>/dev/null

# Create new cron entries
NEXUS_DIR="/Users/deedavis/NEXUS BACKEND"

cat > /tmp/nexus_calendar_cron.txt << EOF
# NEXUS Calendar Automation System
# Auto-generate calendar files and send deadline reports

# Daily deadline report (Every morning at 7:00 AM)
0 7 * * * cd "$NEXUS_DIR" && /usr/bin/python3 -c "from calendar_automation import handle_daily_deadline_report; handle_daily_deadline_report()" >> calendar_automation.log 2>&1

# Process new opportunities (Every hour)
0 * * * * cd "$NEXUS_DIR" && /usr/bin/python3 -c "from calendar_automation import handle_process_new_opportunities; handle_process_new_opportunities()" >> calendar_automation.log 2>&1

# Urgent deadline alerts (Every 6 hours: 8am, 2pm, 8pm, 2am)
0 8,14,20,2 * * * cd "$NEXUS_DIR" && /usr/bin/python3 -c "from calendar_automation import CalendarAutomation; ca = CalendarAutomation(); urgent = [o for o in ca.get_upcoming_deadlines(3) if o['days_until'] <= 1]; print(f'🚨 URGENT: {len(urgent)} deadlines within 24 hours!') if urgent else None" >> calendar_automation.log 2>&1
EOF

# Add to crontab
(crontab -l 2>/dev/null; cat /tmp/nexus_calendar_cron.txt) | crontab -

echo ""
echo "✅ Cron jobs installed:"
echo "   - Daily deadline report: 7:00 AM"
echo "   - Process new opportunities: Every hour"
echo "   - Urgent alerts: Every 6 hours"
echo ""

# Test the system
echo "🧪 Testing calendar automation..."
cd "$NEXUS_DIR"
python3 calendar_automation.py

echo ""
echo "✅ NEXUS Calendar Automation System is LIVE!"
echo ""
echo "📋 What happens now:"
echo "   1. Every morning at 7 AM: Email with upcoming deadlines"
echo "   2. Every hour: Check for new opportunities and generate calendars"
echo "   3. Every 6 hours: Alert for urgent deadlines (< 24 hours)"
echo ""
echo "📁 Calendar files saved to: $NEXUS_DIR/calendars/"
echo "📧 Daily reports emailed to: info@deedavis.biz"
echo ""
echo "🎯 NEVER MISS A DEADLINE AGAIN!"
echo ""
