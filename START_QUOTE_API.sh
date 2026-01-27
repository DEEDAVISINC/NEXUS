#!/bin/bash
# Start NEXUS Quote Generator API

cd "$(dirname "$0")"

echo "============================================================"
echo "🚀 NEXUS Quote Generator API - Starting..."
echo "============================================================"

# Check if Flask is installed
if ! python3 -c "import flask" 2>/dev/null; then
    echo "❌ Flask not installed!"
    echo ""
    echo "Install with:"
    echo "  pip3 install --user flask flask-cors"
    echo "  OR"
    echo "  pip3 install flask flask-cors --break-system-packages"
    echo ""
    exit 1
fi

echo "✓ Flask installed"
echo "✓ Starting API server on port 5001..."
echo ""

python3 quote_generator_api.py
