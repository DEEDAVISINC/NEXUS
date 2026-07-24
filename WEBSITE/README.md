# deedavis.biz — Website Pages (workspace source)

**Master tracker (read when Dee says "DDI website update"):** `DEEDAVIS_BIZ_WEBSITE_UPDATE_TRACKER.md`

Static HTML pages for **deedavis.biz**, version-controlled in this workspace until deployed to Netlify.

**Last live check:** June 2026 — homepage + old `/solutions/professional-services` are live; everything in `WEBSITE/` below is **not** deployed except where noted.

---

## Deploy backlog (priority order)

| Priority | What | Why |
|----------|------|-----|
| **P0 — now** | `cwc-proof/index.html` | Funder QR on pitch Page 6 — **404 today** → `CWC_PROOF_NETLIFY_HOSTING.md` |
| **P1 — batch** | VITAL, HAVEN, ARENA pages + 3D Ink hub + rate sheet | Built in NEXUS, **404 on live site**; Wave 1 outreach links to rate sheet URL |
| **P1 — homepage** | Contract Sectors cards + global nav links | Required in README deploy steps — cards for VITAL, HAVEN, ARENA, 3D Ink (`DEEDAVIS_WEBSITE_NATIONAL_TPA_COPY.md`) |
| **P1 — compliance** | Remove **SWFT** claims on live homepage/case studies | `NEXUS_SYSTEM_CORRECTIONS.md` + `DEEDAVIS_WEBSITE_NATIONAL_TPA_COPY.md` — DCSA denied SWFT Mar 2026 |
| **P1 — national TPA copy** | Homepage hero + sector blurbs + footer | Paste from `ESSENTIALS/DEEDAVIS_WEBSITE_NATIONAL_TPA_COPY.md` implementation checklist |
| **P2 — NCS partner** | Link **deedavis.biz** → `deedavisinc.nationalcrimesearch.com` | NCS Exhibit B — footer or Federal Security / Background section (`PARTNERSHIPS/NATIONAL_CRIME_SEARCH_PARTNERSHIP_SUMMARY.md`) |
| **P3 — future** | `/vendors` public RFQ board | Designed, not built — `VENDOR_PORTAL_SYSTEM_DESIGN.md`, `SUPPLIER_SUB_SYSTEM_STATUS_FEB_8.md` |
| **Not deedavis.biz** | `cwecare.org/program-narrative` | Lives on **CWC Netlify site** (`nexus-frontend/public/program-narrative.html`) — separate deploy |

**Recommended Netlify move:** Deploy the **entire `WEBSITE/` folder** in one push (all staged HTML + `cwc-proof`). Then edit the **live homepage** in Netlify for cards, nav, SWFT removal, and NCS link — homepage is not yet in this `WEBSITE/` repo folder.

---

## Pages (NEXUS source → live status)

| URL | Source file | Live status (Jun 2026) |
|-----|-------------|------------------------|
| `https://deedavis.biz/cwc-proof` | `cwc-proof/index.html` | ❌ **404 — deploy P0** |
| `https://deedavis.biz/solutions/vital` | `solutions/vital/index.html` | ❌ 404 — staged in NEXUS |
| `https://deedavis.biz/solutions/haven` | `solutions/haven/index.html` | ❌ 404 — staged in NEXUS |
| `https://deedavis.biz/solutions/event-mobility` | `solutions/event-mobility/index.html` | ❌ 404 — staged (ARENA program) |
| `https://deedavis.biz/solutions/professional-services` | `solutions/professional-services/index.html` | ⚠️ **Old page live** — NEXUS hub **not** deployed (replace on deploy) |
| `https://deedavis.biz/solutions/professional-services/3d-ink-signatures` | `solutions/professional-services/3d-ink-signatures/index.html` | ❌ 404 — staged |
| `https://deedavis.biz/resources/3d-ink-signatures-agency-rate-sheet-2026` | `resources/3d-ink-signatures-agency-rate-sheet-2026.html` | ❌ 404 — staged |
| `https://deedavis.biz/` (homepage) | *not in `WEBSITE/` — edited on live host* | ✅ Live — needs national TPA + SWFT cleanup |
| `https://deedavis.biz/vendors` | *not built* | ❌ Future — supplier portal design only |

**Note:** `/cwc-proof` deploys immediately (funder blocker). Other `WEBSITE/` pages can ship in the **same Netlify deploy** — you do not have to wait for homepage cleanup, but add homepage cards/nav when you can so new URLs are discoverable.

**Outreach sync:** `CLIENT OUTREACH/3D INK SIGNATURES/SEND_TO_BUYER/3D_Ink_Signatures_AGENCY_Rate_Sheet.html` mirrors the staged website file (print → PDF for Wave 1 attachments).

## Deploy to deedavis.biz

1. Open your **deedavis.biz** site in Netlify (or current host).
2. Upload or sync staged pages to matching publish paths (e.g. `/solutions/vital/index.html`, `/solutions/haven/index.html`).
3. Verify live URLs after deploy.
4. **Homepage:** Add Contract Sectors cards → VITAL, HAVEN, **ARENA**, **Professional Services (3D Ink)**.
5. **Global nav:** Add program links matching other solution pages.
6. **Professional Services:** Sector page links to agency rate sheet; rate sheet nav links back to sector page.

## Local preview

```bash
open "/Users/deedavis/NEXUS BACKEND/WEBSITE/solutions/vital/index.html"
```

Or serve locally:

```bash
cd "/Users/deedavis/NEXUS BACKEND/WEBSITE"
python3 -m http.server 8080
# Visit http://localhost:8080/solutions/vital/
```

## Related NEXUS files

- `VITAL/VITAL_Master_Proposal.html` — print/PDF proposal version
- `VITAL_SYSTEM_SPECIFICATION.md` — PRISM module specs
- `VITAL_MARKET_RESEARCH.md` — market intel
- `HAVEN/ONE_PAGERS/HAVEN_Master_Proposal.html` — HAVEN proposal version
- `ESSENTIALS/SECTOR_CAP_STATEMENTS/DDI_HAVEN_Disaster_Response_Capability_Statement.html`
- `ESSENTIALS/DEEDAVIS_WEBSITE_NATIONAL_TPA_COPY.md` — site-wide copy rules

## Company info (verified)

Phone: 855-773-0035 | Email: info@deedavis.biz | Troy, MI 48084 | CAGE 8UMX3 | UEI HJB4KNYJVGZ1 | Medicaid Provider | E-Verify Program Administrator
