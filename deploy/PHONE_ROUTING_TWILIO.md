# DDI Phone Routing — Business GV → Twilio 855 (Member Path)

**Goal:** Member and public **business** calls hit **Twilio 855-773-0035** → PRISM voice agent + SMS.  
**248.376.4550 is Dieasha D. Davis’s personal cell** — stays on email signatures; **never** on websites; **do not** forward it to Twilio.

---

## Number roles

| Number | Role | On websites? | Routes to |
|--------|------|--------------|-----------|
| **855-773-0035** | Member care, public call/SMS, Twilio | **YES** — all public web | PRISM voice webhooks on PA |
| **248.270.8490** | Google Voice business (Troy) | List **855** on web; GV forwards | **Forward to +1 855-773-0035** |
| **248.376.4550** | **President & CEO personal cell** | **NO** | **Dee’s phone only** — **not** Twilio, **not** optional forward |

**What forwards to 855:** Google Voice **248.270.8490** (and any future Twilio-purchased local 248 you assign the same webhook).  
**What does NOT forward to 855:** **248.376.4550** — personal line for direct CEO contact on email/CO correspondence.

---

## Step 1 — Google Voice (248-270-8490) → Twilio 855

Do this in **Google Admin → Voice**:

1. **Users** → assign **248.270.8490** to your user if not already.
2. Open **Google Voice** app or [voice.google.com](https://voice.google.com) → **Settings**.
3. **Calls** → **Call forwarding** → add **+1 855-773-0035**.
4. Enable **ring linked numbers** / forward all calls to that number.
5. **Test:** Call **248-270-8490** from another phone → should hit Twilio → PRISM voice greeting on **855**.

**Optional:** In GV, set voicemail to off or short timeout so calls pass to 855 quickly.

---

## Step 2 — Twilio console (855 already live)

Confirm **+1 855-773-0035** voice webhook (both numbers must use **identical** config if you add a second Twilio number):

| Setting | Value |
|---------|--------|
| A call comes in | Webhook **POST** |
| URL | `https://deedavis.pythonanywhere.com/prism/voice/inbound` |
| Status callback (optional) | `https://deedavis.pythonanywhere.com/prism/voice/call-status` |

**Phone Numbers** → **855-773-0035** → Friendly name: `DDI Member Care`

---

## Step 3 — (Optional) Add 248 local in Twilio

If you **port** or **buy** a Troy **248** number in Twilio (business line, not personal 248.376):

1. Twilio → **Phone Numbers** → Buy **+1 248…** (local Troy).
2. **Voice & Fax** → same webhook as 855:
   - `POST https://deedavis.pythonanywhere.com/prism/voice/inbound`
3. Publish **855** on websites; use extra Twilio 248 only if you want a local caller ID on outbound.

GV **248.270.8490** can stay forwarded to 855 until/unless you port it into Twilio.

---

## Customer care coordinator handoff (why GV → 855 works)

**Public numbers stay fixed.** **Who answers live calls** can change without reprinting materials or updating websites.

```
Caller → GV 248.270.8490 (or direct 855) → Twilio 855 → PRISM voice agent
         → self-serve booking / status
         → OR "representative" → PRISM_VOICE_TRANSFER_NUMBER (coordinator ring target)
```

| Layer | What you control | How |
|-------|------------------|-----|
| **Business entry** | GV **248.270.8490** | Forward to **855** (one setting in Google Voice) |
| **Member / web line** | **855-773-0035** | Twilio webhook → PRISM (unchanged on flyers, portal, HAP) |
| **Live coordinator** | Any DDI customer care coordinator | Set `PRISM_VOICE_TRANSFER_NUMBER` on PythonAnywhere to that person’s **E.164** mobile or a **Google Voice / ring group** number |

**Swap coordinators:** Update `PRISM_VOICE_TRANSFER_NUMBER` (or Twilio Studio / ring group) — **no** change to 855, portal, or CEO personal **248.376.4550**.

**CEO personal 248.376.4550** stays off the member path — coordinators get overflow, not your personal cell by default.

Details: `deploy/PRISM_VOICE_INTAKE.md` (transfer env + Twilio console).

---

## Step 4 — President & CEO personal (248.376.4550)

- **Personal cell** for Dieasha D. Davis — direct contact on **email signatures**, bids, caps, CO outreach.
- **Do not** put on deedavis.biz, portal, proof pages, or member materials.
- **Do not** set call forwarding from this number to **855** — members and Twilio traffic use **855** and **GV 248.270**; this line stays personal.

Email signature example: `248.376.4550 | info@deedavis.biz`

---

## Step 5 — Websites (NEXUS rule)

All **HTML / public web** contact lines:

```
855-773-0035 | info@deedavis.biz
```

**Never** `248.376.4550` on web. Portal already uses 855.

---

## Verify

- [ ] Call **855-773-0035** → PRISM voice agent
- [ ] Call **248-270-8490** → same agent (after GV forward)
- [ ] SMS test from Twilio → arrives from **855**
- [ ] Website footer shows **855** only
- [ ] Email signature still **248.376.4550** (CEO personal — not forwarded)

---

## Env (PythonAnywhere)

```bash
TWILIO_FROM_NUMBER=+18557730035
PRISM_VOICE_BASE_URL=https://deedavis.pythonanywhere.com
# PRISM_MEMBER_CARE_PHONE=85577300335
```

Full voice stack: `deploy/PRISM_VOICE_INTAKE.md`
