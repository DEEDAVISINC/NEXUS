#!/bin/bash
# One-command PDF generator for VA Courier Capability Statement

echo "============================================================"
echo "  GENERATING PDF - DEE DAVIS INC VA COURIER CAP STATEMENT"
echo "============================================================"
echo ""

cd "/Users/deedavis/NEXUS BACKEND"

# Run the Python generator
python3 generate_va_courier_capstat.py

echo ""
echo "✅ HTML Generated!"
echo ""
echo "📄 Now converting to PDF..."
echo ""

# Open in browser for quick Command+P → Save as PDF
open "photos_and_videos/SOURCES SOUGHT NOTICEGENERAL BID/VA_Courier_Capability_Statement_FORMATTED.html"

echo "============================================================"
echo "  IN YOUR BROWSER:"
echo "  1. Press Command+P"
echo "  2. Select 'Save as PDF'"
echo "  3. Click Save"
echo "  4. Done! Attach to email!"
echo "============================================================"
echo ""
echo "📧 Email to: eileen.meyer@va.gov"
echo "📅 Deadline: February 12, 2026 at 10:00 AM Central"
echo ""
