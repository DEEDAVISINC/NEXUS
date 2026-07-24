# deedavis.biz — DDI Website Update Tracker

**When Dee says "DDI website update," "update the website," or "deedavis.biz deploy" — this file is what she means.**

**Not:** `nexus.deedavis.biz` (Command Center app) · **Not:** `cwecare.org` (nonprofit site)

**Last updated:** June 2026

---

## What this project is

The **public marketing site** at **https://deedavis.biz** — homepage, program/solution pages, funder QR proof page, future vendor portal.

- **Source files (on Mac):** `WEBSITE/` folder in this workspace
- **Host:** Netlify — site whose **primary domain is deedavis.biz**
- **Copy rules:** `ESSENTIALS/DEEDAVIS_WEBSITE_NATIONAL_TPA_COPY.md`
- **Deploy how-to (cwc-proof):** `GRANT_APPLICATION_PACKAGE/CWC_GRANTS/CWC_PROOF_NETLIFY_HOSTING.md`

---

## Three sites — do not mix up

| Site | URL | Purpose |
|------|-----|---------|
| **DDI marketing** | **deedavis.biz** | ← **THIS TRACKER** |
| NEXUS Command Center | nexus.deedavis.biz | Bids, PRISM, internal ops — separate Netlify site |
| Cause We Care | cwecare.org | Nonprofit — program narrative at `/program-narrative` |

---

## Live vs staged (last checked June 2026)

| URL | Workspace source | Live? |
|-----|------------------|-------|
| `/` homepage | *edited on Netlify — not in `WEBSITE/` yet* | ✅ Live — **needs cleanup** (see below) |
| `/cwc-proof` | `WEBSITE/cwc-proof/index.html` | ❌ 404 — **blocker for funder pitch QR** |
| `/solutions/vital` | `WEBSITE/solutions/vital/index.html` | ❌ 404 |
| `/solutions/haven` | `WEBSITE/solutions/haven/index.html` | ❌ 404 |
| `/solutions/event-mobility` (ARENA) | `WEBSITE/solutions/event-mobility/index.html` | ❌ 404 |
| `/solutions/professional-services` | `WEBSITE/solutions/professional-services/index.html` | ⚠️ **Old page live** — replace with NEXUS-staged hub |
| `/solutions/professional-services/3d-ink-signatures` | `WEBSITE/solutions/professional-services/3d-ink-signatures/index.html` | ❌ 404 |
| `/resources/3d-ink-signatures-agency-rate-sheet-2026` | `WEBSITE/resources/3d-ink-signatures-agency-rate-sheet-2026.html` | ❌ 404 — 3D Ink Wave 1 links here |
| `/vendors` | *not built* | ❌ Future (`VENDOR_PORTAL_SYSTEM_DESIGN.md`) |

**Verify after any deploy:**

```bash
curl -I https://deedavis.biz/cwc-proof
curl -I https://deedavis.biz/solutions/vital
curl -I https://deedavis.biz/solutions/haven
```

---

## Backlog (priority order)

### P0 — Funder blocker (do first)

- [ ] Deploy `WEBSITE/cwc-proof/index.html` → `https://deedavis.biz/cwc-proof`
- [ ] Scan QR on pitch package Page 6 from phone — must not 404
- [ ] Check off in `GRANT_APPLICATION_PACKAGE/CWC_GRANTS/THREE_PROGRAM_PITCH_PACKAGE.md` §13b

### P1 — Staged HTML batch (one Netlify deploy)

Deploy **entire `WEBSITE/` folder** to deedavis.biz publish root:

- [ ] VITAL — `/solutions/vital`
- [ ] HAVEN — `/solutions/haven`
- [ ] ARENA — `/solutions/event-mobility`
- [ ] Professional Services hub — replaces old `/solutions/professional-services`
- [ ] 3D Ink division page
- [ ] 3D Ink agency rate sheet — `/resources/3d-ink-signatures-agency-rate-sheet-2026`

*Outreach mirror:* `CLIENT OUTREACH/3D INK SIGNATURES/SEND_TO_BUYER/3D_Ink_Signatures_AGENCY_Rate_Sheet.html`

### P1 — Homepage + site-wide cleanup (edit live homepage on Netlify)

From `ESSENTIALS/DEEDAVIS_WEBSITE_NATIONAL_TPA_COPY.md` implementation checklist:

- [ ] Homepage hero — **nationwide TPA** + **50 states + DC** (not Michigan-only framing)
- [ ] Contract Sectors cards — add **VITAL**, **HAVEN**, **ARENA**, **Professional Services (3D Ink)**
- [ ] Global nav — links to new solution pages
- [ ] Sector card blurbs — paste from national TPA copy doc
- [ ] **Remove all SWFT authorized claims** — Federal Security section + case study (`NEXUS_SYSTEM_CORRECTIONS.md` — DCSA denied SWFT Mar 2026)
- [ ] Retitle fingerprinting case study — mobile LiveScan, client-approved channels (no SWFT)
- [ ] Footer — nationwide TPA line + verified company info
- [ ] Medicaid NEMT case study — multi-state TPA framing (not MI-only)

**Parked for same pass:** `ESSENTIALS/SURETYCLOUD_WEBSITE_EMBED.md` — SuretyCloud embed when editing site

### P2 — Partner / compliance

- [ ] Add link **deedavis.biz → deedavisinc.nationalcrimesearch.com** (footer or background-screening section) — `PARTNERSHIPS/NATIONAL_CRIME_SEARCH_PARTNERSHIP_SUMMARY.md`
- [ ] NCS logo on co-branded portal — ✅ sent May 16
- [ ] NCS training — deferred until first screening contract (policy Jun 2026)

### P3 — Future (not started)

- [ ] `/vendors` public RFQ board — `VENDOR_PORTAL_SYSTEM_DESIGN.md`
- [ ] SHIELD program page on deedavis.biz — **not built** in `WEBSITE/` yet (grant/MDHHS materials only)
- [ ] Pull homepage into `WEBSITE/index.html` for version control (optional — avoids split-brain edits)

---

## Recommended deploy sequence

1. **Netlify** → open site with primary domain **deedavis.biz**
2. Deploy full `WEBSITE/` directory (P0 + P1 pages in one shot)
3. Verify URLs with `curl` or browser
4. **Second pass:** edit homepage on Netlify for cards, nav, SWFT removal, national TPA copy
5. Add NCS partner link when convenient

**CLI (if linked):**

```bash
cd "/Users/deedavis/NEXUS BACKEND/WEBSITE"
netlify link   # once — pick deedavis.biz site
netlify deploy --prod --dir=.
```

---

## Session continuity — what to read

| Dee says | Read first |
|----------|------------|
| "DDI website update" / "update deedavis.biz" | **This file** |
| Copy / wording for site | `ESSENTIALS/DEEDAVIS_WEBSITE_NATIONAL_TPA_COPY.md` |
| Which HTML to deploy | `WEBSITE/README.md` |
| CWC proof QR only | `GRANT_APPLICATION_PACKAGE/CWC_GRANTS/CWC_PROOF_NETLIFY_HOSTING.md` |
| Company facts on site | `COMPANY_INFO_MASTER.md` |

---

## Status log

| Date | Note |
|------|------|
| May 2026 | VITAL, HAVEN, ARENA, 3D Ink pages built in `WEBSITE/` — held for "site cleanup" before deploy |
| Jun 2026 | `cwc-proof` added for funder pitch QR — P0 deploy |
| Jun 2026 | Live audit: most `WEBSITE/` paths 404; homepage live with outdated SWFT language |
| Jun 2026 | Tracker created — "DDI website update" = this backlog, not NEXUS app |

---

*Michigan is where we manage from. America is where we contract.*
