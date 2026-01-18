# Installing ffmpeg for Video Optimization

## Quick Installation (macOS)

### Option 1: Using Homebrew (Recommended)

If you don't have Homebrew installed:
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Then install ffmpeg:
```bash
brew install ffmpeg
```

### Option 2: Download Pre-compiled Binary

1. Visit: https://evermeet.cx/ffmpeg/
2. Download the latest `ffmpeg` and `ffprobe` static builds
3. Extract and move to `/usr/local/bin`:
   ```bash
   sudo mv ffmpeg /usr/local/bin/
   sudo mv ffprobe /usr/local/bin/
   sudo chmod +x /usr/local/bin/ffmpeg
   sudo chmod +x /usr/local/bin/ffprobe
   ```

### Option 3: Using MacPorts

```bash
sudo port install ffmpeg
```

## Verify Installation

```bash
ffmpeg -version
ffprobe -version
```

## Run Video Optimization

Once ffmpeg is installed:

```bash
cd "/Users/deedavis/NEXUS BACKEND"
./optimize_videos.sh
```

This will create:
- **720p (1280x720)** - Web optimized
- **480p (854x480)** - Mobile/slow connections  
- **1080p (1920x1080)** - High quality (if original is large enough)
- **Thumbnail image** - For video poster

## Alternative: Online Conversion

If installation is problematic, you can use online tools:

1. **CloudConvert** - https://cloudconvert.com/mp4-converter
2. **Online-Convert** - https://www.online-convert.com/
3. **HandBrake** - https://handbrake.fr/ (Desktop app, no command line needed)

### HandBrake Settings for Web:
- Format: MP4
- Resolution: 1280x720
- Encoder: H.264
- Quality: RF 23
- Audio: AAC 128kbps
- Web Optimized: ON (fast start)
