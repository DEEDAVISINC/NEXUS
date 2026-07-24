# CWC Digital Proof Sheet — Netlify Hosting (deedavis.biz/cwc-proof)

**Goal:** QR on Page 6 of `THREE_PROGRAM_PITCH_PACKAGE.html` must resolve to a live page — not 404.

**Target URL:** `https://deedavis.biz/cwc-proof`

**Source of truth (NEXUS):** `GRANT_APPLICATION_PACKAGE/CWC_GRANTS/DIGITAL_PROOF_SHEET.html`

**Deploy copy (deedavis.biz site):** `WEBSITE/cwc-proof/index.html`

---

## Yes — Netlify is the right place

`deedavis.biz` is already on Netlify. This is a **single static HTML page** — no build step, no React, no Python. You add one folder and redeploy the deedavis.biz site.

**Do not** put this on the NEXUS (`nexus.deedavis.biz`) or CWC (`cwecare.org`) Netlify sites. The QR points to **deedavis.biz** specifically.

---

## Option A — Netlify UI (fastest, ~5 minutes)

Use this if you manage deedavis.biz through the Netlify dashboard and don’t have the CLI linked locally.

### Step 1 — Find the correct site

1. Log in to [app.netlify.com](https://app.netlify.com).
2. Open the site whose **primary domain** is `deedavis.biz` (not `nexus.deedavis.biz`, not `cwecare.org`).
3. **Site configuration → Domain management** — confirm `deedavis.biz` is listed.

### Step 2 — Upload the page

**If the site deploys from drag-and-drop or manual upload:**

1. On your Mac, open: `WEBSITE/cwc-proof/` (contains `index.html`).
2. In Netlify → **Deploys** → drag the **`cwc-proof` folder** onto the deploy zone  
   — or use **Deploy manually** and upload the folder.

**If the site deploys from Git or a local publish folder:**

1. Copy `WEBSITE/cwc-proof/index.html` into your live deedavis.biz publish root under `cwc-proof/index.html`.
2. Trigger a deploy (push to connected repo, or **Trigger deploy → Deploy site**).

### Step 3 — Verify (required before funder mail)

```bash
curl -I https://deedavis.biz/cwc-proof
```

Expect: `HTTP/2 200` (or `301` → `200` with trailing slash — both OK).

Also test on your phone: scan the QR on Page 6 of the pitch PDF.

### Step 4 — Mark done in NEXUS

In `THREE_PROGRAM_PITCH_PACKAGE.md` §13b, check:

`| DIGITAL_PROOF_SHEET hosted at deedavis.biz/cwc-proof | ✅ |`

Remove or hide the red **MUST-FIX** banner on Page 6 of the HTML after verify (optional — or leave until first funder send).

---

## Option B — Netlify CLI (repeatable deploys)

Use this if deedavis.biz is linked to the Netlify CLI on your machine.

### One-time: link the deedavis.biz site

```bash
cd "/Users/deedavis/NEXUS BACKEND/WEBSITE"
netlify link
```

Select the site where **deedavis.biz** is the primary domain. Note the site name/ID for future deploys.

### Deploy only the proof page (if deedavis.biz publish root = entire WEBSITE folder)

```bash
cd "/Users/deedavis/NEXUS BACKEND/WEBSITE"
netlify deploy --prod --dir=.
```

This publishes everything under `WEBSITE/` including `cwc-proof/index.html`.

### Deploy if deedavis.biz uses a different publish root

If your live site publish folder is elsewhere (e.g. a separate repo), copy only:

```
cwc-proof/index.html  →  [publish-root]/cwc-proof/index.html
```

Then deploy that site’s normal way.

---

## Option C — Git-connected site (best long-term)

If deedavis.biz Netlify site is connected to a Git repo:

1. Add `WEBSITE/cwc-proof/index.html` to that repo (or symlink/copy from NEXUS).
2. Commit and push — Netlify auto-deploys.
3. Verify `https://deedavis.biz/cwc-proof`.

**NEXUS workflow:** When you update `DIGITAL_PROOF_SHEET.html`, re-copy to deploy path:

```bash
cp "/Users/deedavis/NEXUS BACKEND/GRANT_APPLICATION_PACKAGE/CWC_GRANTS/DIGITAL_PROOF_SHEET.html" \
   "/Users/deedavis/NEXUS BACKEND/WEBSITE/cwc-proof/index.html"
```

Then redeploy deedavis.biz.

---

## URL mapping (how Netlify serves it)

| File on disk | Live URL |
|--------------|----------|
| `cwc-proof/index.html` | `https://deedavis.biz/cwc-proof` |
| same | `https://deedavis.biz/cwc-proof/` |

No `_redirects` rule required for a standard static folder.

---

## Optional: pretty URL without folder name

Only if you prefer `deedavis.biz/cwc-proof.html` instead — **not recommended** because the QR already encodes `/cwc-proof`. If you change the URL, regenerate the QR on Page 6.

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| 404 on `/cwc-proof` | File not in publish root, or wrong Netlify site deployed |
| 404 but homepage works | Deploy went to wrong site — check domain on Netlify site card |
| SSL warning | Wait 1–2 min after deploy; Netlify provisions HTTPS automatically |
| Old content after update | Hard refresh or incognito; check latest deploy timestamp in Netlify |
| QR works on desktop, not phone | Confirm phone is on cellular/Wi‑Fi without corporate DNS blocking |

---

## Pre-distribution checklist

- [ ] `https://deedavis.biz/cwc-proof` returns **200**
- [ ] Page title: **Digital Operating Proof — Cause We Care + Dee Davis Inc.**
- [ ] HAP Vendor **100000469269** and CHAMPS **6309049** visible on page
- [ ] Phone **855-773-0035** and email **info@deedavis.biz** on page
- [ ] QR on pitch Page 6 opens this URL on a phone
- [ ] §13b checklist updated in `THREE_PROGRAM_PITCH_PACKAGE.md`

---

## Related files

| File | Purpose |
|------|---------|
| `DIGITAL_PROOF_SHEET.html` | NEXUS master — edit here first |
| `WEBSITE/cwc-proof/index.html` | Deploy copy for deedavis.biz |
| `THREE_PROGRAM_PITCH_PACKAGE.html` | QR on Page 6 |
| `WEBSITE/README.md` | Other deedavis.biz staged pages |

---

*Last updated: June 2026 — deploy before MHEF/CFSEM distribution.*
