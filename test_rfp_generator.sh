#!/bin/bash
# Test NEXUS RFP Generator API

echo "Testing RFP Generator API..."
echo ""
echo "Generating Auburn Hills Pressure Washing RFP..."
echo ""

curl -X POST http://localhost:5002/api/rfp/test \
  -H "Content-Type: application/json" \
  | python3 -m json.tool

echo ""
echo ""
echo "Check generated_rfps/ folder for the PDF!"
echo ""
echo "To download via API:"
echo "  curl -O http://localhost:5002/api/rfp/download/DDI-2026-PW-001"
