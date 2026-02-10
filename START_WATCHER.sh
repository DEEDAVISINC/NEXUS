#!/bin/bash
# Start NEXUS Solicitation Watcher in background

cd "/Users/deedavis/NEXUS BACKEND"

echo "🚀 Starting NEXUS Solicitation Watcher..."
echo ""
echo "This will run in the background and automatically process new PDFs."
echo "When you drop a PDF in photos_and_videos/, it will:"
echo "  1. Create folder"
echo "  2. Move PDF"
echo "  3. Parse data"
echo "  4. Add to Airtable"
echo "  5. Generate analysis"
echo ""
echo "Press Ctrl+C to stop."
echo ""

python3 solicitation_watcher.py
