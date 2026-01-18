# NEXUS Video Demo & Media Guide

## Overview

The NEXUS backend now includes video serving capabilities for demonstrations, client presentations, and documentation enhancement.

## Available Videos

### Primary Demo Video
- **File:** `nexus-2.mp4`
- **Location:** `/photos_and_videos/nexus-2.mp4`
- **Purpose:** Platform demonstration, client presentations, stakeholder showcases

### Legacy Demo Video
- **File:** `nexus.mp4`
- **Location:** `/photos_and_videos/nexus.mp4`

---

## API Endpoints

### Serve Video File
```http
GET /media/videos/{filename}
```

**Example:**
```bash
curl http://127.0.0.1:8000/media/videos/nexus-2.mp4 --output demo.mp4
```

**Direct Browser Access:**
```
http://127.0.0.1:8000/media/videos/nexus-2.mp4
```

**Supported Formats:**
- `.mp4` (recommended)
- `.mov`
- `.avi`
- `.webm`

### List Available Videos
```http
GET /media/videos
```

**Response:**
```json
{
  "videos": [
    "nexus-2.mp4",
    "nexus.mp4"
  ],
  "base_url": "http://127.0.0.1:8000/media/videos/"
}
```

**Example:**
```bash
curl http://127.0.0.1:8000/media/videos
```

---

## Client Presentation

### HTML Showcase Page
Open the professional demo page in any browser:

```bash
open NEXUS_DEMO_SHOWCASE.html
```

**Features:**
- Embedded video player with controls
- Professional branding and design
- Core capabilities overview
- Responsive layout for all devices
- Call-to-action section

**Use Cases:**
- Client presentations
- Stakeholder meetings
- Investor pitches
- Partner demonstrations
- Sales presentations

---

## Documentation Integration

### Markdown Embed Syntax

Add video references to any markdown file:

```markdown
## Platform Demo

Watch the full demonstration:
[NEXUS Platform Demo](http://127.0.0.1:8000/media/videos/nexus-2.mp4)

Or view directly: `http://127.0.0.1:8000/media/videos/nexus-2.mp4`
```

### HTML Embed Code

For HTML documentation or pages:

```html
<video width="100%" controls>
  <source src="/media/videos/nexus-2.mp4" type="video/mp4">
  Your browser does not support the video tag.
</video>
```

### Enhanced Documentation Files

The following documentation files now include video references:
- `QUICK_REFERENCE.md` - Quick access to demo video
- This file (`NEXUS_VIDEO_DEMO.md`) - Comprehensive guide

---

## Production Deployment

### Environment Variables
No additional environment variables needed. The video endpoint uses existing Flask configuration.

### Security Notes
- Only video file extensions are allowed (`.mp4`, `.mov`, `.avi`, `.webm`)
- Files are served from the secure `photos_and_videos` folder
- No directory traversal vulnerabilities
- Standard Flask security applies

### CDN/Cloud Hosting (Optional)

For production deployments with high traffic, consider uploading videos to:

**AWS S3 + CloudFront:**
```bash
aws s3 cp photos_and_videos/nexus-2.mp4 s3://your-bucket/media/
```

**Google Cloud Storage:**
```bash
gsutil cp photos_and_videos/nexus-2.mp4 gs://your-bucket/media/
```

**Azure Blob Storage:**
```bash
az storage blob upload --account-name youraccountname \
  --container-name media \
  --name nexus-2.mp4 \
  --file photos_and_videos/nexus-2.mp4
```

Then update the showcase HTML or API to point to the CDN URL.

---

## Testing

### Test Video Endpoint
```bash
# Check if video is accessible
curl -I http://127.0.0.1:8000/media/videos/nexus-2.mp4

# Expected response:
# HTTP/1.1 200 OK
# Content-Type: video/mp4
# Content-Length: [file size]
```

### Test Video List
```bash
curl http://127.0.0.1:8000/media/videos | python3 -m json.tool
```

### Test in Browser
Navigate to:
```
http://127.0.0.1:8000/media/videos/nexus-2.mp4
```

Should auto-play or prompt download depending on browser settings.

---

## Troubleshooting

### Video Not Found (404)
**Problem:** `curl http://127.0.0.1:8000/media/videos/nexus-2.mp4` returns 404

**Solutions:**
1. Verify file exists:
   ```bash
   ls -lh "photos_and_videos/nexus-2.mp4"
   ```

2. Check file permissions:
   ```bash
   chmod 644 "photos_and_videos/nexus-2.mp4"
   ```

3. Restart the server:
   ```bash
   PORT=8000 python3 api_server.py
   ```

### Video Won't Play in Browser
**Problem:** Video downloads instead of playing

**Solutions:**
- Ensure proper MIME type (server handles this automatically)
- Try different browser (Chrome, Firefox, Safari)
- Check video codec compatibility
- Use VLC or other player to verify video file integrity

### Invalid File Type Error
**Problem:** Get "Invalid file type" error

**Solution:**
- Only `.mp4`, `.mov`, `.avi`, `.webm` extensions are allowed
- Rename file if needed:
  ```bash
  mv photos_and_videos/demo.MP4 photos_and_videos/demo.mp4
  ```

---

## Usage Examples

### 1. Client Email
```
Hi [Client Name],

Thank you for your interest in NEXUS. I've prepared a demonstration 
video showcasing our platform's capabilities:

http://your-domain.com/media/videos/nexus-2.mp4

Or view the interactive showcase:
http://your-domain.com/NEXUS_DEMO_SHOWCASE.html

Best regards,
[Your Name]
```

### 2. ProposalBio™ Integration
Embed video in generated proposals:

```python
proposal_html = f"""
<div class="demo-section">
  <h2>Platform Demonstration</h2>
  <video width="100%" controls>
    <source src="{video_url}/nexus-2.mp4" type="video/mp4">
  </video>
</div>
"""
```

### 3. Stakeholder Reports
Include in automated reports:

```markdown
## Q1 Platform Updates

Review our latest capabilities demonstration:
[View Demo Video](http://nexus-api.com/media/videos/nexus-2.mp4)
```

---

## Advanced Features

### Streaming Support
The Flask `send_from_directory` function automatically handles:
- Range requests (for video seeking)
- Proper MIME types
- Efficient file streaming
- Browser caching headers

### Mobile Optimization
Videos are served with responsive attributes:
- Playback on iOS/Android devices
- Adaptive quality based on connection
- Touch-friendly controls

### Analytics (Optional Enhancement)
Track video views by adding logging:

```python
@app.route('/media/videos/<filename>', methods=['GET'])
def serve_video(filename):
    # Log analytics
    print(f"Video view: {filename} from {request.remote_addr}")
    
    # Serve video
    return send_from_directory(video_folder, filename)
```

---

## Best Practices

1. **Keep Videos Updated:** Regularly update `nexus-2.mp4` with latest features
2. **File Size:** Optimize videos for web (target < 50MB for good loading)
3. **Backup:** Keep video backups in cloud storage
4. **Version Control:** Don't commit large videos to git (use `.gitignore`)
5. **Security:** Use authentication for sensitive demo content if needed

---

## Future Enhancements

Potential additions:
- Video thumbnails generation
- Multiple quality versions (720p, 1080p)
- Subtitle/caption support
- Chapter markers
- Video analytics dashboard
- Automated video transcoding
- Live streaming support

---

## Support

For issues or questions:
- Check troubleshooting section above
- Review Flask logs: `tail -f api_server.log`
- Test with curl commands
- Verify file permissions and paths

**Status:** ✅ Fully operational and tested
**Last Updated:** January 18, 2026
