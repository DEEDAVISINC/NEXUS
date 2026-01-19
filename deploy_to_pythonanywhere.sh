#!/bin/bash
# 🚀 NEXUS Backend Deployment Script for PythonAnywhere
# Copy and paste this entire script into PythonAnywhere Bash console

echo "=================================================="
echo "🚀 DEPLOYING NEXUS BACKEND TO PYTHONANYWHERE"
echo "=================================================="
echo ""

# Navigate to backend directory
echo "📁 Navigating to nexus-backend directory..."
cd ~/nexus-backend || {
    echo "❌ ERROR: nexus-backend directory not found!"
    echo "   Please run: git clone https://github.com/DEEDAVISINC/NEXUS.git nexus-backend"
    exit 1
}

# Pull latest code
echo "📥 Pulling latest code from GitHub..."
git pull origin main || {
    echo "❌ ERROR: Git pull failed!"
    echo "   Check your internet connection and GitHub access"
    exit 1
}

# Check if virtualenv exists
echo "🔍 Checking virtual environment..."
if [ ! -d "venv" ]; then
    echo "⚠️  Virtual environment not found. Creating one..."
    python3 -m venv venv
fi

# Activate virtualenv
echo "⚡ Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Check for .env file
echo "🔐 Checking environment variables..."
if [ ! -f ".env" ]; then
    echo "⚠️  WARNING: .env file not found!"
    echo "   You need to create .env with your API keys"
    echo "   Example:"
    echo "   AIRTABLE_API_KEY=your_key_here"
    echo "   AIRTABLE_BASE_ID=your_base_id_here"
    echo "   ANTHROPIC_API_KEY=your_key_here"
else
    echo "✅ .env file found"
fi

# Test backend
echo "🧪 Testing backend..."
python -c "from nexus_backend import AirtableClient; print('✅ Backend imports successfully')" || {
    echo "❌ ERROR: Backend has import errors!"
    exit 1
}

echo ""
echo "=================================================="
echo "✅ DEPLOYMENT COMPLETE!"
echo "=================================================="
echo ""
echo "📋 NEXT STEPS:"
echo "1. Go to Web tab in PythonAnywhere"
echo "2. Click the green 'Reload' button"
echo "3. Wait 10 seconds"
echo "4. Test: curl https://deedavis.pythonanywhere.com/health"
echo ""
echo "=================================================="
