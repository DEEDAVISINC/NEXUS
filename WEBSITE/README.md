# deedavis.biz — Website Pages (NEXUS Source)

Static HTML pages for **deedavis.biz**, version-controlled in NEXUS until deployed to the live site host (Netlify or other).

## Pages

| URL | Source file | Status |
|-----|-------------|--------|
| `https://deedavis.biz/solutions/vital` | `solutions/vital/index.html` | Staged — deploy after site cleanup |
| `https://deedavis.biz/solutions/haven` | `solutions/haven/index.html` | Staged — deploy after site cleanup |
| `https://deedavis.biz/solutions/event-mobility` | `solutions/event-mobility/index.html` | Staged — deploy after site cleanup |
| `https://deedavis.biz/solutions/professional-services` | `solutions/professional-services/index.html` | Sector hub — multiple professional service divisions |
| `https://deedavis.biz/solutions/professional-services/3d-ink-signatures` | `solutions/professional-services/3d-ink-signatures/index.html` | 3D Ink division detail + inline rates |
| `https://deedavis.biz/resources/3d-ink-signatures-agency-rate-sheet-2026` | `resources/3d-ink-signatures-agency-rate-sheet-2026.html` | Print-ready agency rate sheet (linked from hub + 3D Ink page) |

**Note:** Do not publish until the broader deedavis.biz cleanup pass is done (nav, homepage cards, cross-links).

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

Phone: 248.376.4550 | Email: info@deedavis.biz | Troy, MI 48084 | CAGE 8UMX3 | UEI HJB4KNYJVGZ1 | Medicaid Provider | E-Verify Program Administrator
