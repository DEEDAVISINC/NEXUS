#!/bin/bash
# Quick update script for PythonAnywhere

echo "🚀 Updating NEXUS Backend on PythonAnywhere..."
echo ""

cd ~/nexus-backend || exit

echo "📥 Pulling latest code..."
git pull origin main

echo ""
echo "📦 Installing dependencies..."
pip install python-dateutil --quiet

echo ""
echo "✅ Update complete!"
echo ""
echo "👉 NOW: Go to Web tab → Click RELOAD button"
echo ""
