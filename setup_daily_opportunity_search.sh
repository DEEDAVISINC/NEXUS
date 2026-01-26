#!/bin/bash
# Setup daily automatic SAM.gov opportunity search

echo "🔧 Setting up Daily Opportunity Search..."
echo ""

# Add cron job to run search daily at 6 AM
CRON_CMD="0 6 * * * cd '/Users/deedavis/NEXUS BACKEND' && /usr/local/bin/python3 search_opportunities_now.py >> '/Users/deedavis/NEXUS BACKEND/opportunity_search.log' 2>&1"

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -q "search_opportunities_now"; then
    echo "✓ Daily search already scheduled"
else
    # Add the cron job
    (crontab -l 2>/dev/null; echo "$CRON_CMD") | crontab -
    echo "✓ Daily search scheduled - will run every morning at 6:00 AM"
fi

echo ""
echo "📅 AUTOMATED OPPORTUNITY SEARCH:"
echo "  Frequency: Daily at 6:00 AM"
echo "  Searches: SAM.gov for your product keywords"
echo "  Auto-imports: Matching opportunities to NEXUS"
echo "  Log: /Users/deedavis/NEXUS BACKEND/opportunity_search.log"
echo ""
echo "To view the log:"
echo "  tail -f '/Users/deedavis/NEXUS BACKEND/opportunity_search.log'"
echo ""
echo "To remove this cron job:"
echo "  crontab -e"
echo "  (delete the line with search_opportunities_now)"
echo ""
echo "✅ Done! Your system will automatically find new opportunities every day."
