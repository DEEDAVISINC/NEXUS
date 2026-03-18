#!/bin/bash
# NEXUS CONTINUOUS INGESTION RUNNER
# ================================
# Run this to start the 24/7 data ingestion engine

# Set environment variables if not already set
export AIRTABLE_API_KEY="${AIRTABLE_API_KEY:-your_airtable_key}"
export AIRTABLE_BASE_ID="${AIRTABLE_BASE_ID:-your_base_id}"
export SAM_GOV_API_KEY="${SAM_GOV_API_KEY:-your_sam_key}"

# Change to NEXUS directory
cd "$(dirname "$0")"

# Check if already running
if pgrep -f "nexus_continuous_ingestion.py" > /dev/null; then
    echo "❌ NEXUS ingestion engine is already running!"
    echo "   Run: pkill -f nexus_continuous_ingestion.py"
    exit 1
fi

# Create log directory
mkdir -p logs

# Run the daemon
echo "🚀 Starting NEXUS Continuous Ingestion Engine..."
echo "   - SAM.gov polling every 15 minutes"
echo "   - Presolicitation hunting every hour"
echo "   - USASpending sync daily at 6 AM"
echo ""
echo "   Logs: nexus_ingestion.log"
echo "   PID: $$"
echo ""

# Run in background
nohup python3 nexus_continuous_ingestion.py --daemon > logs/ingestion.out 2>&1 &

echo "✅ Ingestion engine started!"
echo ""
echo "Commands:"
echo "   tail -f nexus_ingestion.log     # Watch logs"
echo "   pkill -f nexus_continuous_ingestion.py  # Stop engine"
