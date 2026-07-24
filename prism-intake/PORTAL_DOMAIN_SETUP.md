# PRISM Client Portal — portal.deedavis.biz

**Netlify site:** `ddi-prism-portal` → https://ddi-prism-portal.netlify.app  
**Target URL:** https://portal.deedavis.biz

---

## Step 1 — Netlify (Domain settings)

1. Open https://app.netlify.com/projects/ddi-prism-portal
2. **Domain management** → **Add domain alias** or **Set custom domain**
3. Enter: `portal.deedavis.biz`
4. Remove `prism.deedavis.biz` if it was added by mistake
5. Netlify will show the DNS record you need (usually CNAME)

---

## Step 2 — DNS (wherever deedavis.biz is hosted)

Add **one** record:

| Type | Name / Host | Value / Points to |
|------|-------------|-------------------|
| **CNAME** | `portal` | `ddi-prism-portal.netlify.app` |

**Not** an A record unless Netlify explicitly instructs you to use their load balancer IPs.

Propagation: usually 5–30 minutes; up to 24 hours.

Verify:
```bash
dig +short portal.deedavis.biz CNAME
curl -I https://portal.deedavis.biz
```

---

## Step 3 — SSL

Netlify provisions **Let's Encrypt** automatically after DNS resolves.  
Web tab / Domain management should show **HTTPS** green check when ready.

---

## Step 4 — Smoke test

1. Open https://portal.deedavis.biz
2. Submit a test NEMT order
3. Confirm in NEXUS → PRISM → Orders

---

## Step 5 — Email (confirmations + ops copies)

Portal email is sent **from** `bids.deedavisinc@gmail.com` via Netlify — **not** from PythonAnywhere.

**Netlify → Site `ddi-prism-portal` → Project configuration → Environment variables → Production:**

| Variable | Value |
|----------|--------|
| `NEXUS_EMAIL` | `bids.deedavisinc@gmail.com` |
| `NEXUS_EMAIL_PASSWORD` | Gmail **App Password** (16 chars, from Google Account → Security → App passwords) |
| `USER_EMAIL` | `bids.deedavisinc@gmail.com` (ops copy inbox) |
| `PRISM_API_BASE` | `https://deedavis.pythonanywhere.com` |
| `PORTAL_PUBLIC_URL` | `https://portal.deedavis.biz` (magic links in email) |
| `PORTAL_AUTH_SECRET` | Long random string (32+ chars). **Required for sign-in.** If omitted, falls back to `NEXUS_EMAIL_PASSWORD`. |

After saving variables: **Deploys → Trigger deploy → Deploy site** (functions must rebuild).

---

## Step 6 — Sign-in security (magic link + code)

Members sign in with **email → link or 6-digit code** (not password). Session lasts **30 days** on the same browser.

**Flow:**
1. Enter email → **Email me a sign-in link**
2. Inbox receives link **and** 6-digit code (15-minute window)
3. Click link **or** enter code → dashboard
4. **Schedule a service** — contact email locked to verified address; unverified emails cannot submit
5. Return visits: auto-restore session (no re-login unless signed out or expired)

**Troubleshooting login:**
- Check spam/junk for sender `bids.deedavisinc@gmail.com`
- Code expires in 15 min — tap **Resend code**
- Link and code both work — use whichever is easier
- Still stuck: **855-773-0035**

**Who gets what:**

| Email | Recipient |
|-------|-----------|
| Ops dispatch | `nemt@deedavis.biz` + `bids.deedavisinc@gmail.com` |
| Requester confirmation | Email on Step 1 of the form (e.g. client contact) |
| Rider confirmation | Member email on Step 3 (if provided) |

**Check Sent** in `bids.deedavisinc@gmail.com` — messages are sent *from* that account; they do not appear in Inbox unless you are the requester.

---

## Notes

- `nexus.deedavis.biz` = NEXUS Command Center (separate Netlify site)
- `portal.deedavis.biz` = PRISM client intake only
- Code routes Netlify functions when hostname is `portal.deedavis.biz` or `*.netlify.app`
