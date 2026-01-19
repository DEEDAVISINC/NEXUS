#!/bin/bash
# Comprehensive test for NEXUS media and legal endpoints

echo "=========================================================="
echo "NEXUS Media & Legal Endpoints - Comprehensive Test"
echo "=========================================================="
echo ""

GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

BASE_URL="http://127.0.0.1:8000"
PASS=0
FAIL=0

# Helper function to test endpoint
test_endpoint() {
    local name="$1"
    local url="$2"
    local expected_code="${3:-200}"
    
    echo -e "${BLUE}Testing: $name${NC}"
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$url")
    
    if [ "$HTTP_CODE" = "$expected_code" ]; then
        echo -e "${GREEN}✓ PASS${NC} - HTTP $HTTP_CODE"
        ((PASS++))
    else
        echo -e "${RED}✗ FAIL${NC} - Expected $expected_code, got $HTTP_CODE"
        ((FAIL++))
    fi
    echo ""
}

# Test JSON endpoint
test_json_endpoint() {
    local name="$1"
    local url="$2"
    
    echo -e "${BLUE}Testing: $name${NC}"
    RESPONSE=$(curl -s "$url")
    
    if echo "$RESPONSE" | python3 -m json.tool > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PASS${NC} - Valid JSON response"
        echo "$RESPONSE" | python3 -m json.tool | head -n 15
        ((PASS++))
    else
        echo -e "${RED}✗ FAIL${NC} - Invalid JSON"
        ((FAIL++))
    fi
    echo ""
}

echo "=========================================="
echo "1. VIDEO ENDPOINTS"
echo "=========================================="
echo ""

test_json_endpoint "List Videos API" "$BASE_URL/media/videos"
test_endpoint "Video: nexus-2.mp4" "$BASE_URL/media/videos/nexus-2.mp4"
test_endpoint "Video: nexus.mp4" "$BASE_URL/media/videos/nexus.mp4"
test_endpoint "Security: Invalid file type" "$BASE_URL/media/videos/test.txt" "400"

echo "=========================================="
echo "2. LEGAL DOCUMENT ENDPOINTS"
echo "=========================================="
echo ""

test_json_endpoint "List Legal Docs API" "$BASE_URL/legal"
test_endpoint "Terms of Use" "$BASE_URL/legal/terms"
test_endpoint "Privacy Policy" "$BASE_URL/legal/privacy"

echo "=========================================="
echo "3. CORE API ENDPOINTS"
echo "=========================================="
echo ""

test_endpoint "Health Check" "$BASE_URL/health"
test_endpoint "Dashboard Stats" "$BASE_URL/dashboard/stats"

echo "=========================================="
echo "4. FILE ACCESSIBILITY"
echo "=========================================="
echo ""

# Check if showcase HTML exists
if [ -f "NEXUS_DEMO_SHOWCASE.html" ]; then
    echo -e "${GREEN}✓ PASS${NC} - NEXUS_DEMO_SHOWCASE.html exists"
    ((PASS++))
else
    echo -e "${RED}✗ FAIL${NC} - NEXUS_DEMO_SHOWCASE.html not found"
    ((FAIL++))
fi
echo ""

# Check if legal docs exist
if [ -f "ALEXIS_NEXUS_TERMS_OF_USE.html" ]; then
    echo -e "${GREEN}✓ PASS${NC} - ALEXIS_NEXUS_TERMS_OF_USE.html exists"
    ((PASS++))
else
    echo -e "${RED}✗ FAIL${NC} - ALEXIS_NEXUS_TERMS_OF_USE.html not found"
    ((FAIL++))
fi
echo ""

if [ -f "ALEXIS_NEXUS_PRIVACY_POLICY.html" ]; then
    echo -e "${GREEN}✓ PASS${NC} - ALEXIS_NEXUS_PRIVACY_POLICY.html exists"
    ((PASS++))
else
    echo -e "${RED}✗ FAIL${NC} - ALEXIS_NEXUS_PRIVACY_POLICY.html not found"
    ((FAIL++))
fi
echo ""

# Check if videos exist
if [ -f "photos_and_videos/nexus-2.mp4" ]; then
    SIZE=$(ls -lh "photos_and_videos/nexus-2.mp4" | awk '{print $5}')
    echo -e "${GREEN}✓ PASS${NC} - nexus-2.mp4 exists ($SIZE)"
    ((PASS++))
else
    echo -e "${RED}✗ FAIL${NC} - nexus-2.mp4 not found"
    ((FAIL++))
fi
echo ""

echo "=========================================="
echo "5. CONTENT TYPE VERIFICATION"
echo "=========================================="
echo ""

# Check video content type
echo -e "${BLUE}Checking: Video Content-Type${NC}"
CONTENT_TYPE=$(curl -sI "$BASE_URL/media/videos/nexus-2.mp4" | grep -i "content-type" | awk '{print $2}' | tr -d '\r')
if [[ "$CONTENT_TYPE" == "video/mp4"* ]]; then
    echo -e "${GREEN}✓ PASS${NC} - Content-Type: $CONTENT_TYPE"
    ((PASS++))
else
    echo -e "${RED}✗ FAIL${NC} - Expected video/mp4, got $CONTENT_TYPE"
    ((FAIL++))
fi
echo ""

# Check HTML content type
echo -e "${BLUE}Checking: Legal Doc Content-Type${NC}"
CONTENT_TYPE=$(curl -sI "$BASE_URL/legal/terms" | grep -i "content-type" | awk '{print $2}' | tr -d '\r')
if [[ "$CONTENT_TYPE" == "text/html"* ]]; then
    echo -e "${GREEN}✓ PASS${NC} - Content-Type: $CONTENT_TYPE"
    ((PASS++))
else
    echo -e "${RED}✗ FAIL${NC} - Expected text/html, got $CONTENT_TYPE"
    ((FAIL++))
fi
echo ""

echo "=========================================="
echo "TEST SUMMARY"
echo "=========================================="
echo ""

TOTAL=$((PASS + FAIL))
PERCENT=$((PASS * 100 / TOTAL))

echo -e "${GREEN}Passed:${NC} $PASS / $TOTAL"
echo -e "${RED}Failed:${NC} $FAIL / $TOTAL"
echo -e "${YELLOW}Success Rate:${NC} $PERCENT%"
echo ""

if [ $FAIL -eq 0 ]; then
    echo -e "${GREEN}=========================================="
    echo "   ALL TESTS PASSED! ✓"
    echo "==========================================${NC}"
else
    echo -e "${YELLOW}=========================================="
    echo "   SOME TESTS FAILED"
    echo "==========================================${NC}"
fi

echo ""
echo "Quick Access URLs:"
echo "  Video Demo:     $BASE_URL/media/videos/nexus-2.mp4"
echo "  Terms of Use:   $BASE_URL/legal/terms"
echo "  Privacy Policy: $BASE_URL/legal/privacy"
echo "  Showcase Page:  file://$(pwd)/NEXUS_DEMO_SHOWCASE.html"
echo ""
