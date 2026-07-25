# NEXUS OPS Portal — ops.deedavis.biz

Employee work portal (sector desks). Magic-link + 6-digit code sign-in.
**Separate Netlify site** from GATEWAY. Hits the same Flask backend on PythonAnywhere.

Architecture: `NEXUS_OPS_MASTER.md`  
All DDI domains: `DDI_PORTAL_DOMAINS.md`

---

## Step 1 — Netlify (new site)

1. https://app.netlify.com → **Add new site** → **Import an existing project**
2. Connect the repo, set:
   - **Base directory:** `ops-portal`
   - **Publish directory:** `.` (see `netlify.toml`)
   - **Functions directory:** `netlify/functions`
3. Site name suggestion: `ddi-ops-portal` → `https://ddi-ops-portal.netlify.app`

---

## Step 2 — Domain

1. Site → **Domain management** → **Add custom domain**
2. Enter: `ops.deedavis.biz`
3. Add DNS wherever `deedavis.biz` is hosted:

| Type | Name / Host | Value |
|------|-------------|-------|
| **CNAME** | `ops` | `ddi-ops-portal.netlify.app` |

```bash
dig +short ops.deedavis.biz CNAME
curl -I https://ops.deedavis.biz
```

---

## Step 3 — Environment variables

**Netlify → Site `ddi-ops-portal` → Environment variables → Production:**

| Variable | Value |
|----------|-------|
| `NEXUS_EMAIL` | `bids.deedavisinc@gmail.com` — SMTP auth (same as GATEWAY) |
| `NEXUS_EMAIL_PASSWORD` | Gmail App Password |
| `OPS_FROM_EMAIL` | `hr@deedavis.biz` (or ops-branded alias later) |
| `OPS_API_BASE` | `https://deedavis.pythonanywhere.com` |
| `PORTAL_PUBLIC_URL` | `https://ops.deedavis.biz` |
| **`OPS_AUTH_SECRET`** | Long random string (32+ chars). **MUST differ from `GATEWAY_AUTH_SECRET`.** |

Generate secret:
```bash
openssl rand -hex 32
```

After saving: **Trigger deploy** so functions pick up env vars.

---

## Step 4 — Session policy (OPS only)

| Rule | Value |
|------|-------|
| Idle timeout | 15 minutes |
| Warning | ~13 minutes |
| Absolute max | 12 hours |
| Remember me | Forbidden |

See `NEXUS_OPS_MASTER.md` § Security. Client idle watchdog ships with the shell; server idle enforcement ships with auth functions (Phase A).

---

## Step 5 — Smoke test (Phase A)

1. Open https://ddi-ops-portal.netlify.app (or https://ops.deedavis.biz after DNS)
2. Enter an email that has an **Active** GATEWAY onboarding record
3. Receive OPS sign-in email → code or magic link
4. Confirm desk board loads with can-work banner + accounts
5. Leave idle ~13 min → warning; ~15 min → signed out

**Backend:** PythonAnywhere WSGI loads `prism_pa_app.py` (not `api_server.py`). OPS routes must be registered there. Smoke test: `curl https://deedavis.pythonanywhere.com/ops/health` → `{"ok":true,...}`.

---

## What this portal does NOT do

- Not GATEWAY — no handbook e-sign / hire checklist here
- Not NEXUS Command Center — no bid board / full admin chrome
- Does not replace PRISM/VERTEX backends — desks write back to those systems

---

## Sister portals

- `gateway.deedavis.biz` — onboarding (`gateway-portal/`)
- `nexus.deedavis.biz` — Command Center
- `portal.deedavis.biz` — PRISM client intake
