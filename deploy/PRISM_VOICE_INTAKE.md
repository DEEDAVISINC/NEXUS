# PRISM Voice Intake — NEMT AI Call Center

**Purpose:** HAP CareSource members call DDI → automated voice agent collects trip details → creates PRISM order + NEMT trip in the ops queue.

---

## LIVE STATUS (Jun 2026)

| Component | Status |
|-----------|--------|
| Twilio account (paid, voice + SMS) | ✅ **LIVE** — tested |
| **855-773-0035** inbound webhook → PA | ✅ **LIVE** |
| PRISM voice agent (slot collection → order) | ✅ **LIVE** |
| Member SMS (confirmations, trip grades) from 855 | ✅ **LIVE** |
| QC spine + MCO audit exports on PA | ✅ **LIVE** |
| Mark Complete → VERTEX + billing gate | ✅ **LIVE** |
| Portal member care (`855` on portal.deedavis.biz) | ✅ **LIVE** |
| **Caller ID / CNAM** (“DDI” on outbound 855) | ⬜ **ONLY REMAINING** |

**Do not re-list Twilio upgrade or test-call prep** — those are complete. Next ops item: **toll-free CNAM branding** so members see **DDI** (not a random number) when we text or call them.

### Caller ID (CNAM) — last step

**Reality check on 855:** Standard **CNAM** in Twilio is built for **US local numbers** and shows best on **landlines**. Toll-free (**855**) often displays as **“Toll Free Caller”** on mobile even after CNAM registration — that is a carrier limitation, not a Twilio misconfiguration. For **mobile** recipients (most HAP members), use **Branded Calling** (Step 4 below) in addition to CNAM.

| What members see | Channel | Fix |
|------------------|---------|-----|
| Number only on **texts** | SMS from 855 | Normal — SMS has no CNAM. Save **855-773-0035** as **DDI Member Care** in materials so they recognize it. |
| **“Toll Free”** on outbound **voice** | Mobile | Branded Calling enrollment (AT&T / T-Mobile / Verizon paths) |
| Business name on outbound **voice** | Landline | CNAM registration (Step 3) |

**Target display string (max 15 characters):** `DDI` or `DEE DAVIS INC`

---

#### Step 1 — Business profile (one time)

1. Log in: [console.twilio.com](https://console.twilio.com)
2. **Account** → **Trust Hub** → **Customer profiles** (or **Overview** → complete open tasks)
3. Create or open **Primary Customer Profile** → type **Business**
4. Fill from `COMPANY_INFO_MASTER.md`:

| Field | Value |
|-------|--------|
| Legal business name | **Dee Davis Inc.** |
| EIN | **84-4114181** |
| Address | 755 W. Big Beaver Rd., Suite 2020, Troy, MI 48084 |
| Website | deedavis.biz |
| Contact | Dieasha D. Davis · info@deedavis.biz · member care 855-773-0035 |

5. Submit for verification if prompted (KYC). Wait for **Approved** before Step 3.

---

#### Step 2 — Toll-free messaging verification (if not already done)

SMS from 855 requires **Toll-Free Verification** (separate from CNAM):

1. **Trust Hub** → **Registrations** → tab **Toll-free**
2. Register **+18557730035** with use case: *Member ride notifications, appointment confirmations, trip grade surveys — HAP CareSource non-medical NEMT*
3. Include EIN **84-4114181** (required for business submissions as of Feb 2026)
4. Sample messages: confirmation text + grade link + HELP/STOP replies (match `deploy/TWILIO_OPTOUT_DDI.md`)

---

#### Step 3 — CNAM (landline caller ID)

1. **Trust Hub** → **Registrations** → tab **CNAM**
2. **Create registration** → link your **Primary Customer Profile**
3. **CNAM display name:** `DDI` (or `DEE DAVIS INC` — 15 char max)
4. Assign number **+1 855-773-0035** to the CNAM profile when prompted
5. Submit → status **In review** → **Approved** (often **3–5 business days**)
6. **Test:** Outbound call from 855 to a **landline** if you have one; mobile may still show “Toll Free”

Console path shortcut: **Phone Numbers** → **855-773-0035** → **Configure** → look for **Trust Hub / CNAM / Branded Calling** links in the sidebar.

---

#### Step 4 — Branded Calling (mobile caller ID — recommended for HAP)

1. **Trust Hub** → **Registrations** → tab **Branded Calling**
2. Create registration → business profile + **855-773-0035**
3. **Display name:** DDI (or Dee Davis Inc.)
4. **Call reason** (example): *Non-medical ride confirmation*
5. Upload logo if requested (DDI logo from cap statement assets)
6. Carrier approval varies by MNO; allow **1–2 weeks**
7. **Test:** Outbound from 855 to **your cell** on AT&T, T-Mobile, and Verizon if possible

If Branded Calling is not offered for your toll-free on your account tier, open a Twilio support ticket: *“Request Branded Calling or outbound CNAM display for toll-free +18557730035 — healthcare member notifications.”*

---

#### Step 5 — Friendly name (internal Twilio label)

1. **Phone Numbers** → **855-773-0035** → set friendly name: `HAP Member Care`
2. Does not change what members see — helps your Twilio console only

---

#### Step 6 — Verify before printing CM materials

- [ ] Inbound: call **855-773-0035** → PRISM voice agent answers
- [ ] Outbound SMS: trip confirmation or grade text arrives from **855-773-0035**
- [ ] Outbound voice (if used): cell shows **DDI** or acceptable branded label — not “Scam Likely”
- [ ] HELP / STOP on 855 returns DDI copy per `deploy/TWILIO_OPTOUT_DDI.md`

Optional (not blocking): set `PRISM_VOICE_TRANSFER_NUMBER` to Google Voice / ops mobile when human queue is ready.

---

## Phone number architecture (3 lines — do not mix)

| Line | Number | Use |
|------|--------|-----|
| **President & CEO personal** | 248.376.4550 | Email signatures only — **not** Twilio, **not** on web |
| **Public web + Twilio** | **855-773-0035** | All websites, portal, voice inbound, member SMS |
| **Google Voice (Troy)** | **248-270-8490** | **Forward to +1 855-773-0035** — same PRISM voice path |

**Full routing:** `deploy/PHONE_ROUTING_TWILIO.md`

| **Human handoff** | Google Voice or ops mobile | `PRISM_VOICE_TRANSFER_NUMBER` when caller asks for agent — **never CEO personal 248.376** |

If `PRISM_VOICE_TRANSFER_NUMBER` is unset, the agent tells the caller to use the portal and does **not** ring the CEO personal line.

Internal no-show alerts → `OPS_ALERT_PHONE` (default **734.413.8310** mobile), not CEO personal.

---

## Architecture

```
Member calls Twilio number (855-773-0035)
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
TWILIO_FROM_NUMBER=+18557730035

# Public HTTPS base — Twilio must reach this
PRISM_VOICE_BASE_URL=https://deedavis.pythonanywhere.com

# Human handoff when caller asks for a person (Google Voice 248.270.8490 — not listed on member websites)
PRISM_VOICE_TRANSFER_NUMBER=

# Member care line on SMS (defaults to 855-773-0035 from company_info if unset)
# PRISM_MEMBER_CARE_PHONE=8557730035

# Internal no-show / ops alerts (mobile — NOT desk)
OPS_ALERT_PHONE=+17344138310

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

1. Use **855-773-0035** (or your voice-capable toll-free) for NEMT member intake.
2. **Voice & Fax → Configure:**
   - **A call comes in:** Webhook `POST`
   - URL: `https://deedavis.pythonanywhere.com/prism/voice/inbound`
3. **Optional status callback:** `https://deedavis.pythonanywhere.com/prism/voice/call-status`
4. Enable **Speech recognition** on the number (US English).

4. **Coordinator handoff:** Set `PRISM_VOICE_TRANSFER_NUMBER` to the active **customer care coordinator** (E.164 mobile or GV ring group). Change this when staffing shifts — public **855** stays the same.

Give HAP / member-facing materials **855-773-0035** — not the CEO personal line.

---

## Google Voice (248-270-8490) → Twilio 855

**Required:** Forward Google Voice business line to Twilio so all business calls hit PRISM.

1. Google Voice → **Settings** → **Call forwarding** → **+1 855-773-0035**
2. Twilio **855-773-0035** webhook: `POST https://deedavis.pythonanywhere.com/prism/voice/inbound`
3. Test: call **248-270-8490** → same voice agent as calling **855** directly

See **`deploy/PHONE_ROUTING_TWILIO.md`** for full checklist.

Optional human queue when GV is only used for transfer (not primary inbound):

1. Set `PRISM_VOICE_TRANSFER_NUMBER` to a ring group or mobile (E.164).
2. Reload PythonAnywhere.
3. Test: call 855, say "representative" — should ring transfer target, not CEO personal 248.376.

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

Caller can say **"representative"** or **"agent"** anytime → transfer to `PRISM_VOICE_TRANSFER_NUMBER` (if set).

---

## Files

| File | Role |
|------|------|
| `prism_voice_intake.py` | Twilio webhooks, session state, order creation |
| `company_info.py` | `PHONE_MEMBER_CARE_*`, `member_care_phone_display()`, `ops_alert_phone_e164()` |
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

*Channel #1 for HAP per `HAP_CARESOURCE_OPERATIONS.md` — members call **855-773-0035**, not CEO personal.*
