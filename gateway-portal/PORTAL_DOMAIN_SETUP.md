# GATEWAY Onboarding Portal — gateway.deedavis.biz

New hire / independent contractor self-service portal. Magic-link + 6-digit
code sign-in (no password, no NEXUS login). Same pattern as
`prism-intake/` (portal.deedavis.biz) — separate Netlify site, separate
subdomain, talks to the same Flask backend that already runs the GATEWAY
(HR Onboarding) API (`hr_onboarding_api.py`, registered in `api_server.py`).

---

## Step 1 — Netlify (new site)

1. https://app.netlify.com → **Add new site** → **Import an existing project**
2. Connect the repo, set:
   - **Base directory:** `gateway-portal`
   - **Publish directory:** `.` (already set in `netlify.toml`)
   - **Functions directory:** `netlify/functions` (already set in `netlify.toml`)
3. Site name suggestion: `ddi-gateway-portal` → gives you `https://ddi-gateway-portal.netlify.app`

---

## Step 2 — Domain

1. Site → **Domain management** → **Add domain alias / custom domain**
2. Enter: `gateway.deedavis.biz`
3. Netlify shows the DNS record (CNAME) — add it wherever `deedavis.biz` DNS is hosted:

| Type | Name / Host | Value |
|------|-------------|-------|
| **CNAME** | `gateway` | `ddi-gateway-portal.netlify.app` |

Propagation: 5–30 min, up to 24 hrs. Verify:
```bash
dig +short gateway.deedavis.biz CNAME
curl -I https://gateway.deedavis.biz
```

SSL (Let's Encrypt) auto-provisions once DNS resolves.

---

## Step 3 — Environment variables

**Netlify → Site `ddi-gateway-portal` → Project configuration → Environment variables → Production:**

| Variable | Value |
|----------|-------|
| `NEXUS_EMAIL` | `bids.deedavisinc@gmail.com` — the real Gmail account that **authenticates** to Gmail's SMTP relay (unchanged, shared with the rest of NEXUS) |
| `NEXUS_EMAIL_PASSWORD` | Gmail **App Password** for that account (can reuse the same one PRISM portal uses) |
| `GATEWAY_FROM_EMAIL` | `hr@deedavis.biz` — what recipients **see** in the From: header. Requires `hr@deedavis.biz` to be added + verified as a **"Send mail as" alias** on the `bids.deedavisinc@gmail.com` Gmail account (Gmail Settings → Accounts and Import → Send mail as → Add another email address). Until verified, Gmail silently sends as `NEXUS_EMAIL` instead — harmless, just not branded yet. `hr@deedavis.biz` forwards to `bids.deedavisinc@gmail.com` via ImprovMX, so the verification link lands right there. |
| `GATEWAY_API_BASE` | `https://deedavis.pythonanywhere.com` (same Flask app that serves PRISM + GATEWAY) |
| `PORTAL_PUBLIC_URL` | `https://gateway.deedavis.biz` (magic links in email) |
| `GATEWAY_AUTH_SECRET` | Long random string (32+ chars). **Recommended separate from `PORTAL_AUTH_SECRET`** so a PRISM client session can never double as a GATEWAY employee session. If omitted, falls back to `PORTAL_AUTH_SECRET`, then `NEXUS_EMAIL_PASSWORD`. |

After saving: **Deploys → Trigger deploy → Deploy site** (functions must rebuild to pick up new env vars).

---

## Step 4 — Confirm the backend is reachable

The portal calls these Flask endpoints (already live in `hr_onboarding_api.py`):

```
GET  /nexus/hr/onboarding/self?email=...
POST /nexus/hr/onboarding/self/documents
POST /nexus/hr/onboarding/self/acknowledge
```

Test directly against the backend first:
```bash
curl "https://deedavis.pythonanywhere.com/nexus/hr/onboarding/self?email=test@deedavis.biz"
```
A `404` with `"No active GATEWAY record found..."` means the backend is reachable and working correctly (there's just no record for that email yet — expected until HR adds one).

---

## Step 5 — Smoke test

1. In NEXUS → GATEWAY (the internal HR admin view), add a test hire/contractor **with an email address**.
2. Open https://gateway.deedavis.biz
3. Enter that email → check inbox for the sign-in code/link (arrives from `bids.deedavisinc@gmail.com`)
4. Sign in → confirm the dashboard shows: checklist, training, screening status, document upload widgets, acknowledgment signing
5. Upload a test document → confirm it shows "✓ Uploaded" and appears as an attachment on the record back in NEXUS
6. Sign an acknowledgment (type a name) → confirm it shows "✓ Signed" with timestamp

---

## How a new hire/contractor actually gets here

There's no separate "invite" step. As soon as HR adds their record in NEXUS **with an email address**, that email can sign in at `gateway.deedavis.biz` immediately. Tell them the URL (put it in the welcome/offer email) — that's the entire onboarding step.

---

## Sign-in security

Same mechanism as the PRISM client portal — stateless HMAC JWT, no database:
- Enter email → **Email me a sign-in link**
- Inbox receives a link **and** a 6-digit code (15-minute window)
- Click the link **or** enter the code → dashboard
- Session lasts **30 days** on the same browser (auto-restores, no re-login unless signed out or expired)

**Troubleshooting sign-in:**
- Check spam/junk for sender `bids.deedavisinc@gmail.com`
- Code expires in 15 min — tap **Resend code**
- Still stuck: **855-773-0035**

---

## What this portal does NOT do (by design)

- No password, no account creation — identity is proven by the email matching an active GATEWAY record HR already created
- Never shows another person's record — lookup is always by the session-verified email, server-side
- Never exposes the internal audit log, worker-classification notes, or exclusion screening internal detail beyond what the person is entitled to see about themselves
- Does not replace the HR admin view in NEXUS — HR still runs compliance verification, training sign-off, and screening logging there. This portal only handles the pieces the new hire/contractor does themselves: document upload + acknowledgment signing, and a read-only view of their own progress.

---

## Notes

- `nexus.deedavis.biz` = NEXUS Command Center (separate Netlify site)
- `portal.deedavis.biz` = PRISM client intake only
- `gateway.deedavis.biz` = GATEWAY onboarding portal only (this site)
- All three are separate Netlify sites hitting the **same** Flask backend on PythonAnywhere
