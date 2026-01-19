#!/bin/bash
# Test script for NEXUS video endpoints

echo "=================================================="
echo "NEXUS Video Endpoints Test"
echo "=================================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

BASE_URL="http://127.0.0.1:8000"

# Test 1: List available videos
echo -e "${BLUE}Test 1: List available videos${NC}"
echo "GET $BASE_URL/media/videos"
echo ""
curl -s "$BASE_URL/media/videos" | python3 -m json.tool
echo ""
echo ""

# Test 2: Check if nexus-2.mp4 is accessible (HEAD request)
echo -e "${BLUE}Test 2: Check nexus-2.mp4 accessibility${NC}"
echo "HEAD $BASE_URL/media/videos/nexus-2.mp4"
echo ""
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -I "$BASE_URL/media/videos/nexus-2.mp4")
if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✓ Video is accessible (HTTP $HTTP_CODE)${NC}"
    
    # Get file size
    SIZE=$(curl -sI "$BASE_URL/media/videos/nexus-2.mp4" | grep -i content-length | awk '{print $2}' | tr -d '\r')
    if [ ! -z "$SIZE" ]; then
        SIZE_MB=$(echo "scale=2; $SIZE / 1048576" | bc)
        echo -e "${GREEN}  File size: ${SIZE_MB}MB${NC}"
    fi
else
    echo -e "${RED}✗ Video not accessible (HTTP $HTTP_CODE)${NC}"
fi
echo ""
echo ""

# Test 3: Check if nexus.mp4 is accessible
echo -e "${BLUE}Test 3: Check nexus.mp4 accessibility${NC}"
echo "HEAD $BASE_URL/media/videos/nexus.mp4"
echo ""
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -I "$BASE_URL/media/videos/nexus.mp4")
if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✓ Video is accessible (HTTP $HTTP_CODE)${NC}"
else
    echo -e "${RED}✗ Video not accessible (HTTP $HTTP_CODE)${NC}"
fi
echo ""
echo ""

# Test 4: Try to access invalid file type
echo -e "${BLUE}Test 4: Security test - try invalid file type${NC}"
echo "GET $BASE_URL/media/videos/test.txt"
echo ""
RESPONSE=$(curl -s "$BASE_URL/media/videos/test.txt")
echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"
echo ""
echo ""

echo "=================================================="
echo "Test Complete"
echo "=================================================="
echo ""
echo "To view video in browser:"
echo "  $BASE_URL/media/videos/nexus-2.mp4"
echo ""
echo "To open showcase page:"
echo "  open NEXUS_DEMO_SHOWCASE.html"
echo ""
