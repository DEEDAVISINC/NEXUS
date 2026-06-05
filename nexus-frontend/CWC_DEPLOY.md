# Cause We Care — cwecare.org Production Deploy

**Cause We Care is a separate organization with its own domain.** It does **not** live on the NEXUS Netlify site.

| Site | Netlify project | Domains | Purpose |
|------|-----------------|---------|---------|
| **CWC** | `cwecare` | `cwecare.org`, `www.cwecare.org` | Public nonprofit website |
| **NEXUS** | `nexus-command` | `nexus.deedavis.biz` | DDI ops / command center |

**Site code:** `src/components/cwc/CWCSite.tsx`  
**CWC Netlify site ID:** `fca93390-2675-4550-a30a-54a0748ef250`  
**NEXUS Netlify site ID:** `288ca3f0-61b8-4732-8519-19f6d5411b7c` (do not attach cwecare.org here)

---

## Why cwecare.org Was Redirecting to nexus.deedavis.biz

When `cwecare.org` / `www.cwecare.org` was added as a **domain alias** on `nexus-command`, Netlify’s default behavior is to **301 redirect every alias to the site’s primary domain** (`nexus.deedavis.biz`).

That redirect happens **before** the React app loads, so:

1. Browser hits `cwecare.org`
2. Netlify sends you to `nexus.deedavis.biz`
3. URL bar shows NEXUS — not CWC

**Fix:** Dedicated Netlify site `cwecare` with `cwecare.org` as **primary**. The `www.cwecare.org` alias was removed from `nexus-command`.

---

## One-Time: Domain on the CWC Site

1. [app.netlify.com](https://app.netlify.com) → site **`cwecare`** (not nexus-command)
2. **Domain management** → **Add a domain** → `cwecare.org`
3. Add **`www.cwecare.org`** (Netlify redirects www ↔ apex within this site only)
4. If using **Netlify DNS** for cwecare.org, nameservers should point at Netlify and the zone must be linked to **`cwecare`**, not `nexus-command`
5. Wait for HTTPS (automatic once DNS is correct)

**Verify:** Open `https://cwecare.org` — URL bar must stay on `cwecare.org` and show the yellow/blue CWC site.

---

## Deploy CWC (Every Update)

From repo:

```bash
cd "nexus-frontend"
npm run build
netlify deploy --prod --dir=build --site=fca93390-2675-4550-a30a-54a0748ef250
```

Build uses `REACT_APP_PUBLIC_SITE=cwc` (set in `netlify.cwc.toml` and baked in at build time for manual deploys):

```bash
cd "nexus-frontend"
REACT_APP_PUBLIC_SITE=cwc npm run build
netlify deploy --prod --dir=build --site=fca93390-2675-4550-a30a-54a0748ef250
```

**NEXUS deploy** (unchanged — separate site):

```bash
cd "nexus-frontend"
npm run build
netlify deploy --prod --dir=build --site=288ca3f0-61b8-4732-8519-19f6d5411b7c
```

For NEXUS builds, do **not** set `REACT_APP_PUBLIC_SITE=cwc`.

---

## Verify After Deploy

| URL | Expected |
|-----|----------|
| `https://cwecare.org` | CWC home — **URL stays cwecare.org** |
| `https://www.cwecare.org` | Same (may redirect apex ↔ www within CWC site only) |
| `https://cwecare.org/refer` | SHIELD family referral intake |
| `https://cwecare.org/status` | Family case status lookup |
| `https://cwecare.org/program-narrative` | DDI+CWC public health program narrative (funders/partners) |
| `https://nexus.deedavis.biz` | NEXUS landing — **never** CWC |
| `http://localhost:3000/cwc` | Local CWC preview |

---

## Config Reference

- **CWC build config:** `nexus-frontend/netlify.cwc.toml`
- **NEXUS build config:** `nexus-frontend/netlify.toml`
- **Host routing:** `App.tsx` — `REACT_APP_PUBLIC_SITE=cwc` or `cwecare.org` hostname → `CWCSite`
- **SPA redirects:** `public/_redirects` → `/index.html`

---

## Post-Go-Live Checklist

- [ ] `cwecare.org` primary on **`cwecare`** Netlify site (not on nexus-command)
- [ ] `www.cwecare.org` removed from nexus-command aliases
- [ ] HTTPS green on cwecare.org
- [ ] Add `public/cwc-logo.png` (header/footer logo)
- [ ] Update `COMPANY_INFO_MASTER.md` when live
- [ ] Test `/refer` and `/status` on production hostname

*Last updated: May 31, 2026*
