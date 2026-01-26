#!/bin/bash
# Setup NEXUS Email Automation to run every hour

echo "Setting up NEXUS Email Automation..."
echo ""

# Add cron job (if it doesn't already exist)
CRON_CMD="0 * * * * cd '/Users/deedavis/NEXUS BACKEND' && /usr/local/bin/python3 nexus_email_automation.py >> '/Users/deedavis/NEXUS BACKEND/nexus_email.log' 2>&1"

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -q "nexus_email_automation"; then
    echo "✓ Cron job already exists"
else
    # Add the cron job
    (crontab -l 2>/dev/null; echo "$CRON_CMD") | crontab -
    echo "✓ Cron job added - automation will run every hour"
fi

echo ""
echo "NEXUS Email Automation Schedule:"
echo "  Runs: Every hour at :00 (9:00, 10:00, 11:00, etc.)"
echo "  Log: /Users/deedavis/NEXUS BACKEND/nexus_email.log"
echo ""
echo "To check the log:"
echo "  tail -f '/Users/deedavis/NEXUS BACKEND/nexus_email.log'"
echo ""
echo "To remove the cron job:"
echo "  crontab -e"
echo "  (delete the line with nexus_email_automation)"
echo ""
echo "Done! ✅"
