#!/bin/bash
# Script to add supplier mining credentials to .env

ENV_FILE="/Users/deedavis/NEXUS BACKEND/.env"

# Add credentials to .env
cat >> "$ENV_FILE" << 'EOF'

# ThomasNet Credentials
THOMASNET_EMAIL=info@deedavis.biz
THOMASNET_PASSWORD=siphoq-towSe8-qyjmyb

# Google Custom Search API
GOOGLE_CSE_API_KEY=AIzaSyCXZf-DqDrpKYQHObSqD3WonOQNgDtC76o
GOOGLE_CSE_ID=94a560f2e338647f2
EOF

echo "✅ Credentials added to .env file!"
