# NEXUS Alexa Skill Setup Guide

## Quick Start (5 minutes)

### Step 1: Start Local Alexa Skill Server
```bash
cd "/Users/deedavis/NEXUS BACKEND"
python3 nexus_alexa_skill.py
```
This starts the Alexa skill endpoint on `http://localhost:5001`

### Step 2: Expose to Internet (for Alexa to reach your local NEXUS)
```bash
# Install ngrok if you don't have it
brew install ngrok  # macOS

# Start ngrok tunnel
ngrok http 5001
```
Copy the https URL (e.g., `https://abc123.ngrok.io`)

### Step 3: Configure Alexa Skill (Alexa Developer Console)
1. Go to https://developer.amazon.com/alexa/console/ask
2. Click "Create Skill"
3. Name: "NEXUS Command Center"
4. Default Language: English (US)
5. Choose "Custom" model
6. Choose "Alexa-hosted (Node.js)" or "Provision your own"
7. Click "Create Skill"

### Step 4: Upload Interaction Model
In the Alexa Developer Console:
1. Go to "Interaction Model" → "JSON Editor"
2. Copy/paste contents of `alexa_skill_config/interaction_model.json`
3. Click "Save Model" then "Build Model"

### Step 5: Connect to Your NEXUS
1. Go to "Endpoint" in the left menu
2. Select "HTTPS"
3. Paste your ngrok URL + `/alexa` (e.g., `https://abc123.ngrok.io/alexa`)
4. Select SSL Certificate type: "My development endpoint is a sub-domain..."
5. Click "Save Endpoints"

### Step 6: Test It
1. Go to "Test" tab
2. Type: "open nexus" or speak it
3. Try these commands:
   - "what's my priority today?"
   - "find federal opportunities"
   - "what's my daily target?"
   - "add to pipeline"
   - "help"

## Available Voice Commands

### Core NEXUS Commands
| Voice Command | NEXUS Action |
|--------------|--------------|
| "Alexa, open NEXUS" | Welcome, shows you what you can do |
| "Alexa, ask NEXUS what's my priority today" | Reads autonomous actions from NEXUS |
| "Alexa, tell NEXUS to find federal opportunities" | Triggers NOVA search |
| "Alexa, ask NEXUS what's my daily target" | Reports NOVA progress (X of 3) |
| "Alexa, ask NEXUS to add to pipeline" | Adds discovered opportunity to GPSS |
| "Alexa, tell NEXUS to generate capability statement" | Opens document generator |
| "Alexa, ask NEXUS to open GPSS" | Confirms navigation to pipeline |
| "Alexa, ask NEXUS how many opportunities I have" | Pipeline stats |

### Conversation Flow
**Example 1: Daily Priorities**
```
You: "Alexa, ask NEXUS what's my priority today"
Alexa: "You have 5 actions today. 2 are high priority. 
        First, review the opportunity from Veterans Affairs for drug testing services, 
        valued at $125,000. Second, generate a capability statement for the Army Corps.
        Would you like me to take you to the first one?"
```

**Example 2: Find Opportunities**
```
You: "Alexa, tell NEXUS to find federal opportunities"
Alexa: "I found 3 opportunities. The top match is from the VA: 
        Medical Courier Services, valued at $450,000. 
        Say 'add to pipeline' if you'd like to pursue this one."

You: "Add to pipeline"
Alexa: "Adding opportunity to your GPSS pipeline. Done. 
        I've created a new opportunity record with status 'Pipeline - Needs Review'."
```

**Example 3: Check Progress**
```
You: "Alexa, ask NEXUS what's my daily target"
Alexa: "Your daily target progress: 1 out of 3 opportunities found today. 
        You need 2 more to hit your goal. Would you like me to search for some?"
```

## Visual Responses (Alexa Show/Echo Devices)

If you have an Echo Show or device with a screen, NEXUS will display:

- **Dashboard view** with action counts and daily target
- **Opportunity cards** showing agency, value, deadline
- **Pipeline stats** with visual progress indicators

## Production Deployment

For 24/7 operation without ngrok:

### Option A: AWS Lambda (Recommended)
1. Deploy `nexus_alexa_skill.py` as an AWS Lambda function
2. Update skill.json with your Lambda ARN
3. Set environment variable `NEXUS_API_URL` to your hosted NEXUS

### Option B: Self-Hosted with Public URL
1. Deploy NEXUS to a server with public IP/domain
2. Update `NEXUS_API_BASE` in `nexus_alexa_skill.py`
3. Run the Flask server with HTTPS

### Option C: Keep Local (Development)
Use ngrok whenever you want to test. The free tier works fine for testing.

## Troubleshooting

### "I can't connect to NEXUS"
- Make sure `nexus_alexa_skill.py` is running
- Check ngrok is running and URL is updated in Alexa console
- Verify NEXUS API is accessible at `http://localhost:8000`

### "Alexa says she can't find opportunities"
- Check that NOVA API endpoints are working: `curl http://localhost:8000/api/hunter/profile`
- Verify Airtable is connected
- Check `nexus_api.log` for errors

### "Visual responses not showing"
- Make sure your device has a screen (Echo Show, Fire TV, etc.)
- Check "Alexa Presentation Language" is enabled in skill config
- Verify APL documents are valid JSON

## Advanced: Push Notifications

To have NEXUS proactively notify you via Alexa (e.g., "NEXUS found a high-priority opportunity"):

1. Enable Proactive Events in Alexa Console
2. Add notification code to `nexus_continuous_ingestion.py`
3. Set up AWS SNS or similar for delivery

See `nexus_alexa_notifications.py` for implementation template.

## Next Steps

1. Test all voice commands in the Test tab
2. Submit for certification when ready
3. Install on your devices
4. Start using voice to control NEXUS!

**Pro tip**: Create a routine! Say "Alexa, good morning" and have it automatically trigger "what's my priority today" and "find federal opportunities".
