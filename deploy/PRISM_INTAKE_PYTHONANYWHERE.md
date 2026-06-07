# PRISM Intake ↔ NEXUS Dashboard — PythonAnywhere Deploy

**Goal:** `POST /prism/intake` and `GET /prism/orders` live at `https://deedavis.pythonanywhere.com` so:

- Netlify portal → `/.netlify/functions/prism-intake` → forwards to `/prism/intake`
- NEXUS PRISM tab (`nexus.deedavis.biz`) → `GET /prism/orders`

If you see **"Coming Soon: PythonAnywhere"** in the browser, the web app is not configured or not reloaded.

---

## 1. Bash console — pull latest code

```bash
cd ~/nexus-backend
git pull origin main
source venv/bin/activate   # or: workon nexus
pip install -r requirements.txt
mkdir -p uploads/prism
```

Ensure `.env` exists in `~/nexus-backend/.env` with at least:

```
AIRTABLE_API_KEY=...
AIRTABLE_BASE_ID=...
NEXUS_EMAIL=...
NEXUS_EMAIL_PASSWORD=...

# Rider/member SMS + confirmation engine (copy from local .env)
TWILIO_ACCOUNT_SID=...
TWILIO_AUTH_TOKEN=...
TWILIO_FROM_NUMBER=+1...

# Optional — SendGrid confirmations + confirm/cancel links
SENDGRID_API_KEY=...
SENDGRID_FROM_EMAIL=info@deedavis.biz
NEXUS_CONFIRM_BASE_URL=https://nexus.deedavis.biz
```

---

## 2. Web tab — source code paths

| Setting | Value |
|---------|--------|
| **Source code** | `/home/deedavis/nexus-backend` |
| **Working directory** | `/home/deedavis/nexus-backend` |
| **Virtualenv** | `/home/deedavis/nexus-backend/venv` **or** `/home/deedavis/.virtualenvs/nexus` |

---

## 3. WSGI file — paste exact config

1. Web tab → **WSGI configuration file** link  
   (`/var/www/deedavis_pythonanywhere_com_wsgi.py`)
2. **Delete everything** in that file.
3. Copy contents from repo: **`deploy/deedavis_pythonanywhere_com_wsgi.py`**
4. If your venv uses **mkvirtualenv `nexus`**, comment Option A and uncomment Option B in that file.
5. Save.

---

## 4. Reload

Web tab → green **Reload** `deedavis.pythonanywhere.com` → wait 10 seconds.

---

## 5. Smoke tests (must all pass)

```bash
# Health + notification channel check
curl -s https://deedavis.pythonanywhere.com/health | python3 -m json.tool
# Expect: status healthy, notifications.twilio_configured true/false,
#         notifications.missing_for_full_notifications lists any unset env vars

# Create test order (intake)
curl -s -X POST https://deedavis.pythonanywhere.com/prism/intake \
  -H "Content-Type: application/json" \
  -d '{
    "confirmation": "SMOKE-PRISM-001",
    "service_key": "nemt",
    "service_label": "NEMT Smoke Test",
    "client_email": "smoke@test.example.com",
    "client_company": "Smoke Test Co",
    "urgency": "routine",
    "tier": 1
  }'
# Expect: {"success":true,"order":{...}}

# Dashboard queue
curl -s https://deedavis.pythonanywhere.com/prism/orders | head -c 500
# Expect: JSON with orders array containing SMOKE-PRISM-001

# NEMT module (dispatch / complete / invoice)
curl -s https://deedavis.pythonanywhere.com/prism/nemt/orders | python3 -m json.tool
# Expect: {"orders": [...], "count": N}

curl -s https://deedavis.pythonanywhere.com/prism/nemt/orders/by-prism/SMOKE-PRISM-001
# Expect: 404 until NEMT order linked, or order JSON when linked

# After deploy — health should still show mode pa-minimal; NEMT must NOT 404:
curl -s -o /dev/null -w "NEMT HTTP %{http_code}\n" https://deedavis.pythonanywhere.com/prism/nemt/orders
# Expect: HTTP 200 and JSON {"orders":[...],"count":N}
```

**NEMT on PA (production Transport buttons):** Netlify PRISM uses `REACT_APP_API_BASE=https://deedavis.pythonanywhere.com`. Until NEMT routes are deployed, Transport **Verify / Dispatch / Complete** return 404 on production.

Deploy checklist:
1. `git pull origin main` on PA (includes `prism_pa_app.py` NEMT blueprint + `prism_nemt.py` + `nemt_billing.py`)
2. Web tab → **Reload** `deedavis.pythonanywhere.com`
3. Confirm: `curl -s https://deedavis.pythonanywhere.com/prism/nemt/orders` → JSON, not HTML 404
4. Voice intake on PA already creates linked NEMT orders via `prism_voice_intake.py`

Local UI button test (before or after PA deploy):
```bash
# Terminal 1 — API (full stack with NEMT)
cd ~/nexus-backend && source venv/bin/activate && python3 api_server.py

# Terminal 2 — Frontend pointed at local API
cd nexus-frontend && REACT_APP_API_BASE=http://127.0.0.1:8000 npm start

# Seed a scheduled test order
python3 scripts/seed_nemt_ui_test.py
# Note prism_order_id from output → PRISM → Transport → Orders → open row
# Click: Verify Eligibility → Dispatch Trip → Mark Complete → Invoice
```

---

## 6. End-to-end with live portal

1. Netlify redeployed (after git push to `prism-intake/`).
2. Submit one order on `https://ddi-prism-portal.netlify.app`.
3. Open NEXUS → **PRISM** → Orders — new row should appear within seconds.

Portal success copy when synced: **"ORDER QUEUED IN NEXUS PRISM — [confirmation #]"**

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| "Coming Soon" page | Web app not created or WSGI broken — check error log on Web tab |
| 404 on `/prism/*` | Old code — `git pull` + Reload |
| 500 on import | Error log — usually missing `pip install -r requirements.txt` |
| Order in API but not Airtable | Airtable field mismatch — order still in `uploads/prism/orders.json` (dashboard OK) |
| Portal says "sync pending" | PA down or Netlify `PRISM_API_BASE` wrong — should be `https://deedavis.pythonanywhere.com` |

**Error log:**

```bash
tail -50 /var/log/deedavis.pythonanywhere.com.error.log
```
