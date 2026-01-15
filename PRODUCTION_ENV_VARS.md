# NEXUS Production Environment Variables

## Render Backend Environment Variables

Add these in your Render dashboard under **Environment** tab:

### Required Variables

```
AIRTABLE_API_KEY
```
**Value:** Your Airtable API key  
**Where to find:** [airtable.com/account](https://airtable.com/account)  
**Example:** `keyABCDEF1234567890`

---

```
AIRTABLE_BASE_ID
```
**Value:** Your Airtable base ID  
**Where to find:** Open your base, look in URL: `airtable.com/appXXXXXXXXXXXXXX`  
**Example:** `appABCDEF1234567890`

---

```
ANTHROPIC_API_KEY
```
**Value:** Your Anthropic (Claude) API key  
**Where to find:** [console.anthropic.com](https://console.anthropic.com)  
**Example:** `sk-ant-api03-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX`

---

```
JWT_SECRET
```
**Value:** A random secret string (generate one)  
**How to generate:** Use a password generator or run: `openssl rand -hex 32`  
**Example:** `a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6`

---

```
PORT
```
**Value:** `8000`  
**Note:** Render may override this automatically

---

### Optional Variables

```
GOOGLE_API_KEY
```
**Value:** Your Google API key (for opportunity mining)  
**Where to find:** [console.cloud.google.com](https://console.cloud.google.com)  
**Required for:** GPSS opportunity mining features

---

```
GOOGLE_CSE_ID
```
**Value:** Your Google Custom Search Engine ID  
**Where to find:** [programmablesearchengine.google.com](https://programmablesearchengine.google.com)  
**Required for:** GPSS opportunity mining features

---

```
ALEXA_SKILL_ID
```
**Value:** Your Alexa Skill ID (if using Alexa integration)  
**Where to find:** Alexa Developer Console  
**Required for:** Alexa voice commands

---

## Netlify Frontend Environment Variables

Add these in your `nexus-frontend/netlify.toml` file:

### Production Environment

```toml
[context.production.environment]
  REACT_APP_API_BASE = "https://your-actual-backend-url.onrender.com"
```

**Replace with:** Your actual Render backend URL

**Example:**
```toml
[context.production.environment]
  REACT_APP_API_BASE = "https://nexus-backend-abc123.onrender.com"
```

---

## How to Add Environment Variables

### In Render:

1. Go to your Render dashboard
2. Select your **nexus-backend** service
3. Click **"Environment"** in the left sidebar
4. Click **"Add Environment Variable"**
5. Enter **Key** and **Value**
6. Click **"Save Changes"**
7. Service will automatically redeploy

### In Netlify:

1. Environment variables are set in `netlify.toml` file
2. Edit the file locally
3. Commit and push to GitHub
4. Netlify will automatically redeploy

---

## Security Best Practices

### DO:
✅ Use strong, random values for JWT_SECRET  
✅ Keep API keys secret - never commit to git  
✅ Rotate keys periodically (every 90 days)  
✅ Use different keys for development and production  
✅ Store keys securely (password manager)

### DON'T:
❌ Never commit `.env` files to git  
❌ Never share API keys in Slack/email  
❌ Never use simple/guessable secrets  
❌ Never reuse the same keys across projects  
❌ Never hardcode keys in source code

---

## Verifying Your Configuration

### Test Backend:
```bash
curl https://your-backend-url.onrender.com/health
```

Should return:
```json
{
  "service": "NEXUS Backend",
  "status": "healthy",
  "version": "1.0.0"
}
```

### Test Frontend:
1. Visit your Netlify URL
2. Open browser console (F12)
3. Check for API connection
4. Should see successful API calls

---

## Troubleshooting

### "Invalid API Key" Errors
- Double-check key values in Render dashboard
- Ensure no extra spaces before/after keys
- Verify keys are active in Airtable/Anthropic console

### "Connection Refused" Errors
- Verify `REACT_APP_API_BASE` in netlify.toml
- Check that backend URL is correct
- Test backend directly: `/health` endpoint

### "CORS" Errors
- Update CORS configuration in `api_server.py`
- Add your Netlify domain to allowed origins
- Restart backend service after changes

---

## Quick Copy-Paste Template

For Render dashboard (update values):

```
AIRTABLE_API_KEY=your_key_here
AIRTABLE_BASE_ID=your_base_id_here
ANTHROPIC_API_KEY=your_anthropic_key_here
JWT_SECRET=your_random_secret_here
PORT=8000
GOOGLE_API_KEY=your_google_key_here
GOOGLE_CSE_ID=your_cse_id_here
ALEXA_SKILL_ID=your_skill_id_here
```

---

## Need Help?

- **Airtable API:** [support.airtable.com](https://support.airtable.com)
- **Anthropic API:** [docs.anthropic.com](https://docs.anthropic.com)
- **Render Support:** [community.render.com](https://community.render.com)
- **Netlify Support:** [community.netlify.com](https://community.netlify.com)
