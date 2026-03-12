# Alexis NEXUS — Your Voice Assistant Setup

**Invocation:** "Alexa, open Alexis NEXUS"

---

## Step 1: Start the Local Server (Terminal 1)

```bash
cd "/Users/deedavis/NEXUS BACKEND"
python3 nexus_alexa_skill.py
```

You should see:
```
NEXUS Alexa Skill — Full Integration
Connecting to NEXUS API at: http://localhost:8000
Handling 85 intents
Starting on port 5001...
```

**Leave this running.**

---

## Step 2: Expose to Internet (Terminal 2)

```bash
# Install ngrok if you don't have it
brew install ngrok

# Start the tunnel
ngrok http 5001
```

You'll see something like:
```
Forwarding    https://abc123.ngrok-free.app -> http://localhost:5001
```

**Copy that https URL.** You'll need it in Step 4.

---

## Step 3: Create the Skill in Alexa Console

1. Go to: https://developer.amazon.com/alexa/console/ask
2. Sign in with your Amazon account (same one your Echos use)
3. Click **"Create Skill"**
4. Fill in:
   - Skill name: `Alexis NEXUS`
   - Default language: `English (US)`
   - Choose model: `Custom`
   - Hosting: `Provision your own`
5. Click **"Create Skill"**
6. Choose template: `Start from Scratch`

---

## Step 4: Upload the Interaction Model

1. In the left menu, click **"Interaction Model"** → **"JSON Editor"**
2. Delete everything in the editor
3. Copy the entire contents of this file:
   ```
   /Users/deedavis/NEXUS BACKEND/alexa_skill_config/interaction_model.json
   ```
4. Paste into the JSON Editor
5. Click **"Save Model"**
6. Click **"Build Model"** (takes 30-60 seconds)

---

## Step 5: Set the Endpoint

1. In the left menu, click **"Endpoint"**
2. Select **"HTTPS"**
3. In the **Default Region** field, paste your ngrok URL + `/alexa`:
   ```
   https://abc123.ngrok-free.app/alexa
   ```
4. For SSL certificate type, select:
   **"My development endpoint is a sub-domain of a domain that has a wildcard certificate..."**
5. Click **"Save Endpoints"**

---

## Step 6: Test It

1. Click the **"Test"** tab at the top
2. Enable testing: Set dropdown to **"Development"**
3. Type or say: `open alexis nexus`
4. You should hear the welcome message

### Test Commands:
- `give me my daily briefing`
- `how many emails do I need to send`
- `what deadlines are coming up`
- `find federal opportunities`

---

## Step 7: Use on Your Echo Devices

Once testing works, Alexis NEXUS is automatically available on all Echo devices linked to your Amazon account.

Just say:
> **"Alexa, open Alexis NEXUS"**

Then:
> **"Give me my daily briefing"**

---

## Daily Usage

| What You Say | What Happens |
|--------------|--------------|
| "Alexa, open Alexis NEXUS" | Starts the skill |
| "Give me my daily briefing" | Reads emails ready, deadlines, top priorities |
| "How many emails do I need to send" | Reports your outreach backlog |
| "What deadlines are coming up" | Lists upcoming bid due dates |
| "How many stale bids" | Reports dormant opportunities |
| "Find federal opportunities" | Searches for EDWOSB set-asides |
| "What's my daily target" | NOVA progress tracking |
| "Show me my pipeline" | GPSS overview |
| "Generate capability statement" | Starts cap statement workflow |

---

## Important Notes

1. **ngrok URL changes** every time you restart it. Update the endpoint in Alexa Console when it changes.

2. **Keep the local server running** — Alexis NEXUS talks to `nexus_alexa_skill.py` on your Mac.

3. **Daily briefing data** comes from `DAILY_BRIEFING.md` — make sure the briefing generator runs each morning.

---

## Make It Permanent (Optional)

To avoid ngrok URL changes, deploy to AWS Lambda:

1. Package `alexa-skill/lambda_function.py`
2. Deploy to AWS Lambda
3. Update skill endpoint to Lambda ARN
4. Set environment variable `NEXUS_API_URL`

This gives you 24/7 access without keeping your Mac running.

---

## Troubleshooting

**"I can't connect to NEXUS"**
- Check `nexus_alexa_skill.py` is running
- Check ngrok is running
- Verify the endpoint URL in Alexa Console

**"Skill not responding"**
- Rebuild the model in Alexa Console
- Check Terminal 1 for error messages

**"I don't hear the daily briefing data"**
- Run `python3 nexus_daily_briefing.py` to generate fresh data
- Check that `DAILY_BRIEFING.md` exists

---

*"Alexa, open Alexis NEXUS... give me my daily briefing"*
