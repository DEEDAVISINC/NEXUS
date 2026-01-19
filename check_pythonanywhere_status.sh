#!/bin/bash
# 🔍 PythonAnywhere Status Checker
# Run this on PythonAnywhere to diagnose issues

echo "=================================================="
echo "🔍 NEXUS BACKEND STATUS CHECK"
echo "=================================================="
echo ""

# Check 1: Directory exists
echo "1️⃣ Checking if nexus-backend directory exists..."
if [ -d ~/nexus-backend ]; then
    echo "   ✅ Directory found: ~/nexus-backend"
    cd ~/nexus-backend
else
    echo "   ❌ Directory NOT found!"
    echo "   Solution: Run: git clone https://github.com/DEEDAVISINC/NEXUS.git nexus-backend"
    exit 1
fi

# Check 2: Git status
echo ""
echo "2️⃣ Checking Git status..."
git status &>/dev/null
if [ $? -eq 0 ]; then
    echo "   ✅ Git repository is valid"
    BRANCH=$(git branch --show-current)
    echo "   📍 Current branch: $BRANCH"
    git fetch origin main &>/dev/null
    LOCAL=$(git rev-parse @)
    REMOTE=$(git rev-parse @{u})
    if [ "$LOCAL" = "$REMOTE" ]; then
        echo "   ✅ Code is up to date with GitHub"
    else
        echo "   ⚠️  Code is BEHIND GitHub - need to pull!"
    fi
else
    echo "   ❌ Not a valid Git repository"
fi

# Check 3: Virtual environment
echo ""
echo "3️⃣ Checking virtual environment..."
if [ -d venv ]; then
    echo "   ✅ Virtual environment exists"
    source venv/bin/activate
    echo "   ✅ Virtual environment activated"
else
    echo "   ❌ Virtual environment NOT found"
    echo "   Solution: Run: python3 -m venv venv"
    exit 1
fi

# Check 4: Python version
echo ""
echo "4️⃣ Checking Python version..."
PYTHON_VERSION=$(python --version 2>&1)
echo "   📍 $PYTHON_VERSION"

# Check 5: Required packages
echo ""
echo "5️⃣ Checking required packages..."
REQUIRED_PACKAGES=("flask" "pyairtable" "anthropic" "feedparser" "requests")
for package in "${REQUIRED_PACKAGES[@]}"; do
    if python -c "import $package" 2>/dev/null; then
        echo "   ✅ $package installed"
    else
        echo "   ❌ $package NOT installed"
        echo "   Solution: Run: pip install $package"
    fi
done

# Check 6: Environment variables
echo ""
echo "6️⃣ Checking environment variables (.env file)..."
if [ -f .env ]; then
    echo "   ✅ .env file exists"
    # Check for required keys without exposing values
    if grep -q "AIRTABLE_API_KEY=" .env; then
        echo "   ✅ AIRTABLE_API_KEY is set"
    else
        echo "   ❌ AIRTABLE_API_KEY is MISSING"
    fi
    if grep -q "AIRTABLE_BASE_ID=" .env; then
        echo "   ✅ AIRTABLE_BASE_ID is set"
    else
        echo "   ❌ AIRTABLE_BASE_ID is MISSING"
    fi
    if grep -q "ANTHROPIC_API_KEY=" .env; then
        echo "   ✅ ANTHROPIC_API_KEY is set"
    else
        echo "   ❌ ANTHROPIC_API_KEY is MISSING"
    fi
else
    echo "   ❌ .env file NOT found!"
    echo "   Solution: Create .env file with your API keys"
fi

# Check 7: Main backend file
echo ""
echo "7️⃣ Checking main backend files..."
FILES=("nexus_backend.py" "api_server.py" "requirements.txt")
for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "   ✅ $file exists"
    else
        echo "   ❌ $file NOT found"
    fi
done

# Check 8: Test backend import
echo ""
echo "8️⃣ Testing backend imports..."
python -c "from nexus_backend import AirtableClient, ClaudeAI" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "   ✅ Backend imports successfully"
else
    echo "   ❌ Backend import FAILED"
    echo "   Running detailed error check..."
    python -c "from nexus_backend import AirtableClient, ClaudeAI"
fi

# Check 9: API server
echo ""
echo "9️⃣ Checking API server..."
if [ -f api_server.py ]; then
    python -c "from api_server import app" 2>/dev/null
    if [ $? -eq 0 ]; then
        echo "   ✅ API server imports successfully"
    else
        echo "   ❌ API server import FAILED"
        echo "   Running detailed error check..."
        python -c "from api_server import app"
    fi
fi

# Summary
echo ""
echo "=================================================="
echo "📊 STATUS SUMMARY"
echo "=================================================="
echo ""
echo "If all checks show ✅, your backend is ready!"
echo "Next step: Go to Web tab and click 'Reload' button"
echo ""
echo "If any checks show ❌, fix those issues first."
echo ""
echo "=================================================="
