# NEXUS Voice Assistant Options

**Three ways to get voice access to NEXUS — pick what works for you.**

---

## Option 1: Quick Local Assistant (Mac Only)
**Setup time: 0 minutes | Works offline | Text + voice output**

This runs directly on your Mac. No setup required. Just run it.

### Start It
```bash
cd "/Users/deedavis/NEXUS BACKEND"
python3 nexus_voice_assistant.py
```

### What It Does
- Reads your `DAILY_BRIEFING.md` and speaks it to you
- Type commands, hear responses via Mac's built-in voice
- No internet, no AWS, no Alexa device needed

### Commands
| Say/Type | What It Does |
|----------|--------------|
| `briefing` | Full morning briefing — emails, deadlines, priorities |
| `emails` | How many emails ready to send |
| `deadlines` | Upcoming bid due dates |
| `stale` | How many bids have gone dormant |
| `help` | List all commands |
| `quit` | Exit |

### Make It Even Easier
Add an alias to your shell:
```bash
echo 'alias nexus="python3 /Users/deedavis/NEXUS\ BACKEND/nexus_voice_assistant.py"' >> ~/.zshrc
source ~/.zshrc
```
Now just type `nexus` in any terminal to start.

---

## Option 2: Full Alexa Integration (Echo Devices)
**Setup time: 15-30 minutes | Works with Echo devices | Full voice control**

If you have an Echo device, this gives you hands-free NEXUS access.

### Prerequisites
- Amazon Echo device (Echo, Echo Dot, Echo Show)
- Amazon Developer account (free)
- AWS account for Lambda (free tier works)

### Quick Setup
1. **Start local server:**
   ```bash
   cd "/Users/deedavis/NEXUS BACKEND"
   python3 nexus_alexa_skill.py
   ```

2. **Expose to internet (for testing):**
   ```bash
   # Install ngrok if needed
   brew install ngrok
   
   # Start tunnel
   ngrok http 5001
   ```
   Copy the https URL.

3. **Create Alexa Skill:**
   - Go to https://developer.amazon.com/alexa/console/ask
   - Create new skill → "NEXUS Command Center" → Custom → Alexa-hosted
   - JSON Editor → paste contents of `alexa_skill_config/interaction_model.json`
   - Build model
   - Endpoint → HTTPS → paste ngrok URL + `/alexa`
   - Test tab → "open alexis nexus"

### Voice Commands (with Echo)
| Say | What It Does |
|-----|--------------|
| "Alexa, open Alexis NEXUS" | Start the skill |
| "Give me my daily briefing" | Morning status with emails, deadlines |
| "How many emails do I need to send" | Email backlog count |
| "What deadlines are coming up" | Bid due dates |
| "Find federal opportunities" | Search SAM.gov |
| "What's my daily target" | NOVA progress |
| "Show me my pipeline" | GPSS overview |

### Production Deployment
For 24/7 operation without ngrok, deploy to AWS Lambda:
1. Package `alexa-skill/lambda_function.py` with dependencies
2. Deploy to AWS Lambda
3. Update Alexa skill endpoint to Lambda ARN
4. Set `NEXUS_API_URL` environment variable

---

## Option 3: Siri Shortcuts (iPhone/Mac)
**Setup time: 5 minutes | Works on iPhone, iPad, Mac | Limited but convenient**

Create Siri shortcuts that trigger NEXUS scripts.

### Setup on Mac
1. Open Shortcuts app
2. Create new shortcut
3. Add action: "Run Shell Script"
4. Script: `python3 "/Users/deedavis/NEXUS BACKEND/nexus_daily_briefing.py" && open "/Users/deedavis/NEXUS BACKEND/DAILY_BRIEFING.md"`
5. Name it "NEXUS Briefing"
6. Say "Hey Siri, NEXUS Briefing" to run it

### Useful Shortcuts to Create
| Shortcut Name | Shell Command |
|---------------|---------------|
| "NEXUS Briefing" | `python3 nexus_daily_briefing.py && open DAILY_BRIEFING.md` |
| "NEXUS Emails" | `python3 nexus_voice_assistant.py <<< "emails"` |
| "Open NEXUS" | `open "/Users/deedavis/NEXUS BACKEND"` |

---

## Comparison

| Feature | Local Assistant | Alexa | Siri Shortcuts |
|---------|-----------------|-------|----------------|
| Setup time | None | 15-30 min | 5 min |
| Voice input | No (text only) | Yes | Yes |
| Voice output | Yes | Yes | No |
| Works offline | Yes | No | Depends |
| Hands-free | No | Yes | Yes |
| Full NEXUS access | Basic | Full (70+ intents) | Limited |

---

## Recommendation

**Start with Option 1** (Local Assistant) — it works immediately and gives you the core daily briefing functionality.

**Add Option 2** (Alexa) when you want hands-free access from anywhere in your office. The skill is already built; you just need to deploy it.

**Use Option 3** (Siri) for quick triggers from your phone when you're away from your computer.

---

## Daily Workflow with Voice

**Morning routine:**
1. "Alexa, open Alexis NEXUS" → "Give me my daily briefing"
2. Hear: "93 emails ready to send. 4 deadlines this week. Your top priority is Kentucky drug testing due April 1st."
3. "How many emails do I need to send?" → Get the specific backlog
4. "Find federal opportunities" → Start opportunity hunting

**Throughout the day:**
- "What deadlines are coming up?" — Quick check before lunch
- "Add to pipeline" — When reviewing opportunities
- "Show me stale bids" — Weekly cleanup

---

*Voice + NEXUS = Less screen time, more action.*
