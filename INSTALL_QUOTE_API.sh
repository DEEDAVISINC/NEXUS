#!/bin/bash
# Install dependencies for NEXUS Quote Generator API

echo "📦 Installing Flask and dependencies..."
echo ""

pip3 install --user flask flask-cors

echo ""
echo "✅ Installation complete!"
echo ""
echo "Now start the API with:"
echo "  ./START_QUOTE_API.sh"
