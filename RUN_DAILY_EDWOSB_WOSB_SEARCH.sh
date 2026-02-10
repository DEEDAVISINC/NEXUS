#!/bin/bash
# DAILY EDWOSB/WOSB OPPORTUNITY SEARCH
# Runs automatically every day to find NEW opportunities
# Only finds EDWOSB and WOSB - filters out SDVOSB, HUBZone, 8(a)

cd "/Users/deedavis/NEXUS BACKEND"

# Load environment variables
export $(cat .env | xargs)

# Run the miner
python3 auto_mine_edwosb_wosb_only.py

# Log the results
echo "$(date): EDWOSB/WOSB search completed" >> /tmp/nexus_daily_search.log
