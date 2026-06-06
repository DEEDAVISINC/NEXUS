# PRISM Voice Intake — NEMT AI Call Center

**Purpose:** HAP CareSource members call DDI → automated voice agent collects trip details → creates PRISM order + NEMT trip in the ops queue.

---

## Architecture

```
Member calls Twilio number
  → POST /prism/voice/inbound   (greeting + first question)
  → POST /prism/voice/gather    (speech → slot fill loop)
  → POST /prism/intake          (PRISM order, channel=voice)
  → prism_nemt.create_nemt_order (NEMT dispatch queue)
  → nexus_confirmation_engine   (SMS + email confirmation)
```

**Ops UI:** PRISM → NEMT & Medical Transport division → **Voice Intake** tab

---

## Environment variables

Add to `.env` (local + PythonAnywhere):

```bash
# Required for live phone calls
TWILIO_ACCOUNT_SID=AC...
TWILIO_AUTH_TOKEN=...
TWILIO_FROM_NUMBER=+1XXXXXXXXXX

# Public HTTPS base — Twilio must reach this
PRISM_VOICE_BASE_URL=https://deedavis.pythonanywhere.com

# Human handoff when caller asks for a person (DDI main office)
PRISM_VOICE_TRANSFER_NUMBER=2483764550

# Optional — better speech parsing
OPENAI_API_KEY=sk-...
PRISM_VOICE_OPENAI_MODEL=gpt-4o-mini

# Natural voice (pick one tier)
# Tier 1 — Twilio Generative (no extra cost beyond Twilio TTS rates)
PRISM_VOICE_TTS=Polly.Ruth-Generative
# Alternatives: Polly.Joanna-Generative, Google.en-US-Chirp3-HD-Leda

# Tier 2 — ElevenLabs (most human; ~$0.10–0.20/min)
ELEVENLABS_API_KEY=...
ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM
# Browse voices: https://elevenlabs.io/voice-library

# Existing — confirmations after order created
SENDGRID_API_KEY=...
SENDGRID_FROM_EMAIL=info@deedavis.biz
NEXUS_CONFIRM_BASE_URL=https://nexus.deedavis.biz
```

---

## Twilio console setup

1. Buy or assign a **voice-capable** US number for NEMT member intake.
2. **Voice & Fax → Configure:**
   - **A call comes in:** Webhook `POST`
   - URL: `https://deedavis.pythonanywhere.com/prism/voice/inbound`
3. **Optional status callback:** `https://deedavis.pythonanywhere.com/prism/voice/call-status`
4. Enable **Speech recognition** on the number (US English).

Give HAP / member-facing materials the **Twilio number** — not your personal cell.

---

## Deploy (PythonAnywhere)

```bash
cd ~/nexus-backend && git pull
# Reload web app (Web tab → Reload)
curl -s https://deedavis.pythonanywhere.com/prism/voice/status | python3 -m json.tool
```

Expected: `twilio_configured: true`, `inbound_webhook` URL shown.

---

## Sound human (not robotic)

**Default:** Twilio **Generative** voice (`Polly.Ruth-Generative`) — much warmer than standard Polly.

**Best quality:** Add **ElevenLabs** to `.env`. When `ELEVENLABS_API_KEY` is set, NEXUS auto-generates natural audio and Twilio plays it — callers hear a real conversational tone, not phone-tree energy.

Copy is also conversational: acknowledgments by first name, soft retries, no “Please say…” script language.

---

## Test without a phone

### API simulator

```bash
curl -s -X POST https://deedavis.pythonanywhere.com/prism/voice/simulate \
  -H 'Content-Type: application/json' \
  -d '{"speech":"Maria Johnson"}'
```

Repeat with each answer; reuse `call_sid` from the response for multi-turn.

### PRISM UI

PRISM → NEMT division → **Voice Intake** → **Test without a phone call**

Walk through: name → DOB → Medicaid ID → pickup → dropoff → when → standard/wheelchair → yes.

---

## Voice flow (slots collected)

| Step | Field |
|------|--------|
| 1 | Member full name |
| 2 | Date of birth |
| 3 | Medicaid / member ID |
| 4 | Pickup address |
| 5 | Drop-off address |
| 6 | Pickup date & time |
| 7 | Standard vs wheelchair |
| 8 | Verbal confirmation |

Caller can say **"representative"** or **"agent"** anytime → transfer to `PRISM_VOICE_TRANSFER_NUMBER`.

---

## Files

| File | Role |
|------|------|
| `prism_voice_intake.py` | Twilio webhooks, session state, order creation |
| `prism_pa_app.py` | Registers voice blueprint on PA deploy |
| `nexus-frontend/.../PrismVoiceCallCenter.tsx` | Ops dashboard + simulator |
| `uploads/prism/voice_sessions.json` | In-progress call state |
| `uploads/prism/voice_call_log.json` | Call history for dashboard |

---

## Next upgrades (not in v1)

- Real-time OpenAI voice (Media Streams) for natural conversation
- Eligibility pre-check against CareSource portal before dispatch
- After-hours voicemail → callback queue
- Multi-language (Spanish) for Wayne/Macomb members

---

*Channel #1 for HAP per `HAP_CARESOURCE_OPERATIONS.md` — members call DDI directly.*
