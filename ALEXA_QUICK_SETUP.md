# ALEXA QUICK SETUP — Do These 6 Steps

**Your endpoint is LIVE at:** `https://hotel-wendy-are-bikini.trycloudflare.com/alexa`

---

## Step 1: Open Alexa Developer Console
Go to: https://developer.amazon.com/alexa/console/ask

Log in with the **SAME Amazon account** your Alexa device is linked to.

---

## Step 2: Create Skill
1. Click **"Create Skill"** (blue button, top right)
2. Name: `NEXUS Command Center`
3. Locale: `English (US)`
4. Type: **Custom**
5. Backend: **Provision your own**
6. Click **"Create Skill"** → then pick **"Start from Scratch"**

---

## Step 3: Set Up the Interaction Model
1. In the left sidebar, click **"JSON Editor"** (under Interaction Model)
2. **Delete everything** in the text box
3. Open this file and copy ALL of it: `/Users/deedavis/NEXUS BACKEND/alexa_skill_config/interaction_model.json`
4. Paste it into the JSON Editor
5. Click **"Save"** at the top
6. Click **"Build Skill"** at the top (wait for it to complete — ~30 seconds)

---

## Step 4: Set the Endpoint
1. In the left sidebar, click **"Endpoint"**
2. Select **"HTTPS"**
3. In the **Default Region** box, paste this URL:

```
https://hotel-wendy-are-bikini.trycloudflare.com/alexa
```

4. For the SSL certificate dropdown, select: **"My development endpoint is a sub-domain of a domain that has a wildcard certificate from a certificate authority"**
5. Click **"Save Endpoints"**

---

## Step 5: Enable APL (for Alexa Show display)
1. In the left sidebar, click **"Interfaces"**
2. Toggle ON: **Alexa Presentation Language**
3. Click **"Save Interfaces"**
4. Click **"Build Skill"** again

---

## Step 6: Test It
1. Click the **"Test"** tab at the top
2. Change the dropdown from "Off" to **"Development"**
3. Type or say: **"open nexus"**
4. You should hear: "Welcome to NEXUS Command Center..."

---

## Voice Commands You Can Use

Once it's working, say to your Alexa device:

| Say This | What Happens |
|---|---|
| "Alexa, open NEXUS" | Opens the command center |
| "What's my priority today?" | Gets today's top actions |
| "Find federal opportunities" | Searches for new contracts |
| "What's my daily target?" | Shows progress toward 3/day goal |
| "How many opportunities do I have?" | Pipeline stats |
| "Show me my pipeline" | Opens GPSS overview |
| "Generate a capability statement for the VA" | Triggers cap statement |

---

## If Something Breaks

The tunnel URL changes every time you restart your computer. To get a new one:

```bash
cd "/Users/deedavis/NEXUS BACKEND"
source .venv/bin/activate
python nexus_alexa_skill.py &
cloudflared tunnel --url http://localhost:5001
```

Then update the endpoint URL in the Alexa Developer Console (Step 4).
