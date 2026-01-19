#!/bin/bash
# Video Optimization Script for NEXUS
# Creates multiple quality versions of nexus-2.mp4

set -e

SOURCE_VIDEO="photos_and_videos/nexus-2.mp4"
OUTPUT_DIR="photos_and_videos/optimized"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo "=========================================="
echo "NEXUS Video Optimization"
echo "=========================================="
echo ""

# Check if ffmpeg is installed
if ! command -v ffmpeg &> /dev/null; then
    echo -e "${RED}ERROR: ffmpeg is not installed${NC}"
    echo ""
    echo "To install ffmpeg on macOS:"
    echo "  1. Install via Homebrew: brew install ffmpeg"
    echo "  2. Or download from: https://ffmpeg.org/download.html"
    echo ""
    echo "For quick installation, run:"
    echo "  /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
    echo "  brew install ffmpeg"
    echo ""
    exit 1
fi

# Check if source video exists
if [ ! -f "$SOURCE_VIDEO" ]; then
    echo -e "${RED}ERROR: Source video not found: $SOURCE_VIDEO${NC}"
    exit 1
fi

# Create output directory
mkdir -p "$OUTPUT_DIR"

echo -e "${BLUE}Source Video Information:${NC}"
ffprobe -v error -show_entries format=duration,size,bit_rate -show_entries stream=width,height,codec_name -of default=noprint_wrappers=1 "$SOURCE_VIDEO"
echo ""

# Get original dimensions
ORIGINAL_WIDTH=$(ffprobe -v error -select_streams v:0 -show_entries stream=width -of default=noprint_wrappers=1:nokey=1 "$SOURCE_VIDEO")
ORIGINAL_HEIGHT=$(ffprobe -v error -select_streams v:0 -show_entries stream=height -of default=noprint_wrappers=1:nokey=1 "$SOURCE_VIDEO")

echo -e "${GREEN}Original Resolution: ${ORIGINAL_WIDTH}x${ORIGINAL_HEIGHT}${NC}"
echo ""

echo "=========================================="
echo "Creating Optimized Versions..."
echo "=========================================="
echo ""

# 1. 720p HD (1280x720) - Good balance for web
echo -e "${BLUE}1. Creating 720p HD version (1280x720)...${NC}"
ffmpeg -i "$SOURCE_VIDEO" \
    -vf "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2" \
    -c:v libx264 \
    -preset medium \
    -crf 23 \
    -c:a aac \
    -b:a 128k \
    -movflags +faststart \
    -y \
    "$OUTPUT_DIR/nexus-2-720p.mp4" 2>&1 | tail -n 5

if [ -f "$OUTPUT_DIR/nexus-2-720p.mp4" ]; then
    SIZE=$(ls -lh "$OUTPUT_DIR/nexus-2-720p.mp4" | awk '{print $5}')
    echo -e "${GREEN}✓ Created: nexus-2-720p.mp4 ($SIZE)${NC}"
else
    echo -e "${RED}✗ Failed to create 720p version${NC}"
fi
echo ""

# 2. 480p SD (854x480) - Mobile/slow connections
echo -e "${BLUE}2. Creating 480p SD version (854x480)...${NC}"
ffmpeg -i "$SOURCE_VIDEO" \
    -vf "scale=854:480:force_original_aspect_ratio=decrease,pad=854:480:(ow-iw)/2:(oh-ih)/2" \
    -c:v libx264 \
    -preset medium \
    -crf 25 \
    -c:a aac \
    -b:a 96k \
    -movflags +faststart \
    -y \
    "$OUTPUT_DIR/nexus-2-480p.mp4" 2>&1 | tail -n 5

if [ -f "$OUTPUT_DIR/nexus-2-480p.mp4" ]; then
    SIZE=$(ls -lh "$OUTPUT_DIR/nexus-2-480p.mp4" | awk '{print $5}')
    echo -e "${GREEN}✓ Created: nexus-2-480p.mp4 ($SIZE)${NC}"
else
    echo -e "${RED}✗ Failed to create 480p version${NC}"
fi
echo ""

# 3. 1080p Full HD (1920x1080) - High quality (only if original is larger)
if [ "$ORIGINAL_WIDTH" -ge 1920 ] || [ "$ORIGINAL_HEIGHT" -ge 1080 ]; then
    echo -e "${BLUE}3. Creating 1080p Full HD version (1920x1080)...${NC}"
    ffmpeg -i "$SOURCE_VIDEO" \
        -vf "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2" \
        -c:v libx264 \
        -preset medium \
        -crf 22 \
        -c:a aac \
        -b:a 192k \
        -movflags +faststart \
        -y \
        "$OUTPUT_DIR/nexus-2-1080p.mp4" 2>&1 | tail -n 5
    
    if [ -f "$OUTPUT_DIR/nexus-2-1080p.mp4" ]; then
        SIZE=$(ls -lh "$OUTPUT_DIR/nexus-2-1080p.mp4" | awk '{print $5}')
        echo -e "${GREEN}✓ Created: nexus-2-1080p.mp4 ($SIZE)${NC}"
    else
        echo -e "${RED}✗ Failed to create 1080p version${NC}"
    fi
    echo ""
else
    echo -e "${YELLOW}⊘ Skipping 1080p - original resolution too small${NC}"
    echo ""
fi

# 4. Create thumbnail image (poster)
echo -e "${BLUE}4. Creating video thumbnail...${NC}"
ffmpeg -i "$SOURCE_VIDEO" \
    -ss 00:00:02 \
    -vframes 1 \
    -vf "scale=1280:720:force_original_aspect_ratio=decrease" \
    -y \
    "$OUTPUT_DIR/nexus-2-thumbnail.jpg" 2>&1 | tail -n 5

if [ -f "$OUTPUT_DIR/nexus-2-thumbnail.jpg" ]; then
    SIZE=$(ls -lh "$OUTPUT_DIR/nexus-2-thumbnail.jpg" | awk '{print $5}')
    echo -e "${GREEN}✓ Created: nexus-2-thumbnail.jpg ($SIZE)${NC}"
else
    echo -e "${RED}✗ Failed to create thumbnail${NC}"
fi
echo ""

echo "=========================================="
echo "Optimization Complete!"
echo "=========================================="
echo ""

# Show summary
echo -e "${GREEN}Created Files:${NC}"
ls -lh "$OUTPUT_DIR" | tail -n +2
echo ""

echo -e "${BLUE}File Sizes Comparison:${NC}"
echo "Original:"
ls -lh "$SOURCE_VIDEO" | awk '{print "  " $9 ": " $5}'
echo ""
echo "Optimized:"
for file in "$OUTPUT_DIR"/*.mp4; do
    if [ -f "$file" ]; then
        ls -lh "$file" | awk '{print "  " $9 ": " $5}'
    fi
done
echo ""

echo -e "${YELLOW}Next Steps:${NC}"
echo "1. Test videos in browser to ensure quality"
echo "2. Copy files to main photos_and_videos folder if satisfied"
echo "3. Update API to serve multiple quality options"
echo ""
echo "Commands to deploy:"
echo "  cp $OUTPUT_DIR/*.mp4 photos_and_videos/"
echo "  cp $OUTPUT_DIR/*.jpg photos_and_videos/"
echo ""
