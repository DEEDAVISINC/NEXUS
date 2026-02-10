#!/bin/bash

echo "=========================================="
echo "  PARTNERSHIP PROPOSAL GENERATOR API"
echo "=========================================="
echo ""
echo "Starting Partnership Proposal Generator..."
echo "Port: 5004"
echo "Output: generated_partnerships/"
echo ""

# Navigate to the backend directory
cd "/Users/deedavis/NEXUS BACKEND"

# Make sure the script is executable
chmod +x partnership_proposal_api.py

# Run the API
python3 partnership_proposal_api.py
