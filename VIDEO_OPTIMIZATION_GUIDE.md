# Video Optimization Guide for NEXUS

**Status:** Ready to optimize once ffmpeg is installed  
**Target:** Create 720p (1280x720) and other quality versions

---

## Current Situation

Your `nexus-2.mp4` needs multiple size versions for optimal performance across different devices and connection speeds.

### Installation Issue

The automatic ffmpeg installation encountered a CPU architecture compatibility issue. Here are your options:

---

## ✅ RECOMMENDED SOLUTION: Use HandBrake (GUI - No Terminal Required)

###Step 1: Download HandBrake
- Visit: https://handbrake.fr/downloads.php
- Download for macOS
- Install the application

### Step 2: Create 720p Version
1. Open HandBrake
2. **Source:** Select `photos_and_videos/nexus-2.mp4`
3. **Destination:** Set to `photos_and_videos/nexus-2-720p.mp4`
4. **Preset:** Choose "Web > Gmail Large 3 Minutes 720p30"
5. **Dimensions Tab:**
   - Width: 1280
   - Height: 720
   - Keep Aspect Ratio: ON
6. **Video Tab:**
   - Encoder: H.264 (x264)
   - Framerate: Same as source
   - Quality: Constant Quality RF 23
7. **Audio Tab:**
   - Codec: AAC
   - Bitrate: 128
8. **Click "Start Encode"**

### Step 3: Create 480p Version (Optional - for mobile)
Repeat above with:
- Destination: `nexus-2-480p.mp4`
- Width: 854
- Height: 480
- Quality: RF 25
- Audio Bitrate: 96

### Step 4: Verify Files
After encoding, you should have:
```
photos_and_videos/
├── nexus-2.mp4         (original)
├── nexus-2-720p.mp4    (web optimized)
└── nexus-2-480p.mp4    (mobile optimized)
```

---

## Alternative: Online Conversion (Quick & Easy)

### CloudConvert (Recommended)
1. Visit: https://cloudconvert.com/mp4-to-mp4
2. Upload `nexus-2.mp4`
3. Click "Options" and set:
   - **Resolution:** 1280x720
   - **Video Codec:** H.264
   - **Quality:** High
   - **Audio Codec:** AAC
   - **Audio Bitrate:** 128 kbps
4. Click "Convert"
5. Download as `nexus-2-720p.mp4`
6. Move to `photos_and_videos/` folder

### Online-Convert
1. Visit: https://www.online-convert.com/
2. Upload video
3. Set resolution to 1280x720
4. Download result

---

## ffmpeg Command Line (For Technical Users)

If you get ffmpeg working, run these commands:

```bash
cd "/Users/deedavis/NEXUS BACKEND"

# 720p version (1280x720) - Web optimized
ffmpeg -i photos_and_videos/nexus-2.mp4 \
  -vf "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2" \
  -c:v libx264 \
  -preset medium \
  -crf 23 \
  -c:a aac \
  -b:a 128k \
  -movflags +faststart \
  photos_and_videos/nexus-2-720p.mp4

# 480p version (854x480) - Mobile optimized  
ffmpeg -i photos_and_videos/nexus-2.mp4 \
  -vf "scale=854:480:force_original_aspect_ratio=decrease,pad=854:480:(ow-iw)/2:(oh-ih)/2" \
  -c:v libx264 \
  -preset medium \
  -crf 25 \
  -c:a aac \
  -b:a 96k \
  -movflags +faststart \
  photos_and_videos/nexus-2-480p.mp4

# Create thumbnail
ffmpeg -i photos_and_videos/nexus-2.mp4 \
  -ss 00:00:02 \
  -vframes 1 \
  -vf "scale=1280:720:force_original_aspect_ratio=decrease" \
  photos_and_videos/nexus-2-thumbnail.jpg
```

Or use the automated script:
```bash
./optimize_videos.sh
```

---

## What Happens After Optimization

Once you have the optimized versions, they'll automatically be available through the API:

### API Usage

**Original quality (auto-select best):**
```
http://127.0.0.1:8000/media/videos/nexus-2.mp4
```

**Specific quality:**
```
http://127.0.0.1:8000/media/videos/nexus-2.mp4?quality=720p
http://127.0.0.1:8000/media/videos/nexus-2.mp4?quality=480p
```

**List all versions:**
```bash
curl http://127.0.0.1:8000/media/videos | python3 -m json.tool
```

---

## Expected File Sizes

Based on typical compression:

| Version | Resolution | Estimated Size | Best For |
|---------|------------|----------------|----------|
| Original | Varies | 3.9MB | High quality display |
| 720p | 1280x720 | ~1-2MB | Most web users |
| 480p | 854x480 | ~500KB-1MB | Mobile, slow connections |

---

## Benefits of Multiple Qualities

### 720p (1280x720) - Recommended Default
✅ Perfect balance of quality and file size  
✅ Loads quickly on most connections  
✅ Looks great on laptops and desktops  
✅ Suitable for presentations  
✅ Ideal for embedded website videos

### 480p (854x480) - Mobile Optimized
✅ Smallest file size  
✅ Fast loading on mobile networks  
✅ Less data usage for clients  
✅ Works well on slower connections

### Original - Maximum Quality
✅ Best possible quality  
✅ For download/offline viewing  
✅ When quality is critical

---

## Testing Your Videos

After creating optimized versions, test them:

### In Browser
```bash
# Test 720p
open "http://127.0.0.1:8000/media/videos/nexus-2.mp4?quality=720p"

# Test 480p  
open "http://127.0.0.1:8000/media/videos/nexus-2.mp4?quality=480p"
```

### Check File Info
```bash
ls -lh photos_and_videos/nexus-2*.mp4
```

### Verify Quality
- Does video play smoothly?
- Is text readable?
- Is audio clear?
- Does it load quickly?

---

## Showcase Page Integration

Your `NEXUS_DEMO_SHOWCASE.html` is already configured to use the video. Once optimized versions exist, it will automatically use the best quality for the user's connection.

To manually specify quality in HTML:
```html
<video controls>
  <source src="/media/videos/nexus-2.mp4?quality=720p" type="video/mp4">
</video>
```

---

## Production Deployment Checklist

Before deploying to production:

- [ ] Create 720p version
- [ ] Create 480p version (optional)
- [ ] Create thumbnail image (optional)
- [ ] Test all quality versions
- [ ] Verify file sizes are reasonable
- [ ] Update showcase page if needed
- [ ] Deploy files with API server
- [ ] Test on production URLs

---

## Quick Start (HandBrake Method)

1. **Download HandBrake:** https://handbrake.fr/
2. **Open** `nexus-2.mp4` in HandBrake
3. **Select preset:** "Web > Gmail Large 3 Minutes 720p30"
4. **Save as:** `nexus-2-720p.mp4` in `photos_and_videos/` folder
5. **Click "Start Encode"**
6. **Restart API server** (optional - it will work automatically)
7. **Test:** http://127.0.0.1:8000/media/videos/nexus-2.mp4?quality=720p

---

## Troubleshooting

### "Video quality looks poor"
- Increase quality setting (lower RF number)
- Use preset: "Web > High Quality" instead
- Ensure source video is high quality

### "File size too large"
- Lower quality setting (higher RF number)
- Reduce audio bitrate to 96kbps
- Try 480p instead of 720p

### "Video won't play in browser"
- Ensure codec is H.264 (not H.265)
- Enable "Web Optimized" / "Fast Start" option
- Check audio codec is AAC

---

## Summary

**Easiest Method:** HandBrake GUI application  
**Fastest Method:** CloudConvert online  
**Most Control:** ffmpeg command line

**Recommended for you:** HandBrake (download, drag & drop, click encode)

Once complete, your API will automatically serve optimized videos!

**Files to create:**
- `nexus-2-720p.mp4` ← **Primary goal (1280x720)**
- `nexus-2-480p.mp4` ← Optional (854x480)

---

**Next Steps:**
1. Download HandBrake: https://handbrake.fr/
2. Encode `nexus-2-720p.mp4` at 1280x720
3. Save to `photos_and_videos/` folder
4. Test at: http://127.0.0.1:8000/media/videos/nexus-2.mp4?quality=720p

**Status:** API ready, waiting for optimized video files ✅
