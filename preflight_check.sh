#!/bin/bash

# NEXUS Netlify Pre-Flight Check
# Run this before deploying to Netlify

echo "🚀 NEXUS NETLIFY PRE-FLIGHT CHECK"
echo "=================================="
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -d "nexus-frontend" ]; then
    echo -e "${RED}❌ Error: nexus-frontend directory not found${NC}"
    echo "Please run this script from the NEXUS BACKEND root directory"
    exit 1
fi

echo "📁 Checking directory structure..."
if [ -d "nexus-frontend" ]; then
    echo -e "${GREEN}✓${NC} nexus-frontend directory exists"
else
    echo -e "${RED}✗${NC} nexus-frontend directory missing"
    exit 1
fi

if [ -f "nexus-frontend/package.json" ]; then
    echo -e "${GREEN}✓${NC} package.json exists"
else
    echo -e "${RED}✗${NC} package.json missing"
    exit 1
fi

if [ -f "nexus-frontend/netlify.toml" ]; then
    echo -e "${GREEN}✓${NC} netlify.toml exists"
else
    echo -e "${RED}✗${NC} netlify.toml missing"
    exit 1
fi

echo ""
echo "🔍 Checking netlify.toml configuration..."

# Check if backend URL is configured
if grep -q "your-backend-url-here" nexus-frontend/netlify.toml; then
    echo -e "${RED}✗${NC} Backend URL not configured!"
    echo "   Edit nexus-frontend/netlify.toml and set REACT_APP_API_BASE"
    echo "   to your Render backend URL"
    ERRORS=1
else
    BACKEND_URL=$(grep "REACT_APP_API_BASE" nexus-frontend/netlify.toml | head -1 | cut -d'"' -f2)
    echo -e "${GREEN}✓${NC} Backend URL configured: ${BACKEND_URL}"
fi

echo ""
echo "📦 Checking frontend dependencies..."
cd nexus-frontend

if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}⚠${NC}  node_modules not found"
    echo "   Run: cd nexus-frontend && npm install"
    echo ""
    read -p "Install dependencies now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        npm install
    fi
else
    echo -e "${GREEN}✓${NC} node_modules exists"
fi

echo ""
echo "🔨 Testing local build..."
echo "   (This may take a minute...)"

if npm run build > /tmp/nexus-build.log 2>&1; then
    echo -e "${GREEN}✓${NC} Build successful!"
    echo "   Build output: nexus-frontend/build/"
else
    echo -e "${RED}✗${NC} Build failed!"
    echo "   Check log: /tmp/nexus-build.log"
    echo ""
    echo "Last 10 lines of build log:"
    tail -10 /tmp/nexus-build.log
    ERRORS=1
fi

cd ..

echo ""
echo "🔐 Checking git status..."

# Check if there are uncommitted changes
if [ -n "$(git status --porcelain)" ]; then
    echo -e "${YELLOW}⚠${NC}  Uncommitted changes detected:"
    git status --short
    echo ""
    echo "   You should commit these before deploying"
else
    echo -e "${GREEN}✓${NC} All changes committed"
fi

# Check if we're on main branch
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "main" ] && [ "$CURRENT_BRANCH" != "master" ]; then
    echo -e "${YELLOW}⚠${NC}  Current branch: $CURRENT_BRANCH"
    echo "   Netlify typically deploys from main/master"
else
    echo -e "${GREEN}✓${NC} On main branch"
fi

# Check if there are unpushed commits
if git status | grep -q "Your branch is ahead"; then
    echo -e "${YELLOW}⚠${NC}  Unpushed commits detected"
    echo "   Run: git push origin main"
else
    echo -e "${GREEN}✓${NC} All commits pushed"
fi

echo ""
echo "🌐 Checking backend..."

if [ -n "$BACKEND_URL" ] && [ "$BACKEND_URL" != "your-backend-url-here.com" ]; then
    echo "   Testing: ${BACKEND_URL}/health"
    
    if curl -s -f -m 10 "${BACKEND_URL}/health" > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} Backend is responding"
        
        # Check if it's PythonAnywhere
        if echo "$BACKEND_URL" | grep -q "pythonanywhere.com"; then
            echo -e "${GREEN}✓${NC} Using PythonAnywhere backend"
        fi
    else
        echo -e "${RED}✗${NC} Backend not responding"
        echo "   Make sure your backend is deployed and running"
        if echo "$BACKEND_URL" | grep -q "pythonanywhere.com"; then
            echo "   PythonAnywhere: Check Web tab and click 'Reload'"
        fi
        echo "   Test manually: curl ${BACKEND_URL}/health"
        ERRORS=1
    fi
else
    echo -e "${YELLOW}⚠${NC}  Backend URL not configured - skipping test"
fi

echo ""
echo "📋 Backend requirements..."

if [ -f "requirements.txt" ]; then
    echo -e "${GREEN}✓${NC} requirements.txt exists"
else
    echo -e "${RED}✗${NC} requirements.txt missing"
    ERRORS=1
fi

if [ -f "api_server.py" ]; then
    echo -e "${GREEN}✓${NC} api_server.py exists"
else
    echo -e "${RED}✗${NC} api_server.py missing"
    ERRORS=1
fi

echo ""
echo "=================================="
if [ -n "$ERRORS" ]; then
    echo -e "${RED}❌ Pre-flight check FAILED${NC}"
    echo ""
    echo "Please fix the errors above before deploying to Netlify."
    exit 1
else
    echo -e "${GREEN}✅ PRE-FLIGHT CHECK PASSED!${NC}"
    echo ""
    echo "Your NEXUS system is ready for Netlify deployment!"
    echo ""
    echo "Next steps:"
    echo "1. Deploy backend to PythonAnywhere (if not done)"
    echo "   See: NETLIFY_PYTHONANYWHERE_DEPLOY.md"
    echo "2. Update netlify.toml with backend URL (if not done)"
    echo "3. Commit and push: git add . && git commit -m 'Ready for deployment' && git push"
    echo "4. Deploy to Netlify via dashboard"
    echo "5. Set up nexus.deedavis.biz custom domain"
    echo ""
    echo "See NETLIFY_PYTHONANYWHERE_DEPLOY.md for detailed instructions."
fi
