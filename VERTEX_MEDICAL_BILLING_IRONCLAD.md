# VERTEX Medical Billing — Ironclad Checklist

**Last Updated:** July 28, 2026  
**Owner:** Dieasha D. Davis / NEXUS  
**Code:** `nemt_billing.py` · `vertex_medical_billing_scrub.py` · `nexus_qc_engine.py` · `/vertex/nemt/*`

---

## What “ironclad” means here

VERTEX must not create a billable medical claim that will **deny**, **miss timely filing**, **use the wrong payer ID**, or **skip QC**.  
Invoice generation ≠ payer submission — scrub/gates first; Availity/837 next.

---

## Implemented (Jul 28, 2026 hardening)

| Control | Status |
|---|---|
| Claim scrub before invoice (fields, mileage, duplicate DOS, HCPCS hints) | ✅ `vertex_medical_billing_scrub.py` |
| Timely filing clock (default 365 days; Molina per orientation) | ✅ |
| Molina clearinghouse payer ID **38334** (was wrong 38217) | ✅ |
| Priority Health payer ID **38217** (no longer collides with Molina) | ✅ |
| HAP eligibility audit stamps + portal confirm flag | ✅ |
| QC gate: no QC record = **block** (legacy opt-out `VERTEX_QC_ALLOW_LEGACY=1`) | ✅ |
| Opt-in API token for NEMT write endpoints (`VERTEX_NEMT_API_TOKEN`) | ✅ |
| Regression tests | ✅ `test_vertex_medical_billing_ironclad.py` |

**Run tests:**
```bash
python3 test_vertex_medical_billing_ironclad.py
```

---

## Ops hard gates (you must clear — code correctly blocks)

| Gate | Status | Action |
|---|---|---|
| Molina LTSS attestation on file | ⬜ False | Sign/return → then flip `MOLINA_LTSS_ATTESTATION_ON_FILE` |
| Molina Availity active + NPI 1538939111 | ⬜ False | Activate App 63821858 → flip `MOLINA_LTSS_AVAILITY_ACTIVE` |
| Priority Health prism password | ⬜ | Set password for `info@deedavis.biz.prism` before ~Aug 7 |
| Set `VERTEX_NEMT_API_TOKEN` in production `.env` | ⬜ | Match `REACT_APP_NEXUS_INTERNAL_TOKEN` in frontend build |

---

## Still open (next ironclad tranche)

| Gap | Risk | Priority |
|---|---|---|
| No 837P / Availity auto-submit | Claims never leave DDI automatically | P1 |
| No 835 ERA parse / denial queue | Manual remits only | P1 |
| No appeal / dispute clocks (90/120) | Money left on table | P1 |
| Priority / Aetna / McLaren / BCC rate engines | Stub directory only | P2 |
| Encrypt local `nemt_billing_data.json` PHI | Disk plaintext | P2 |

---

## Env flags

| Variable | Default | Meaning |
|---|---|---|
| `VERTEX_QC_ALLOW_LEGACY` | `0` | `1` = allow invoice with no QC record (audit exception only) |
| `VERTEX_HAP_REQUIRE_PORTAL_CONFIRM` | `1` | Scrub requires HAP portal audit path |
| `VERTEX_NEMT_API_TOKEN` / `NEXUS_INTERNAL_API_TOKEN` | unset | When set, write APIs require `X-NEXUS-Token` |
| `REACT_APP_NEXUS_INTERNAL_TOKEN` | unset | Frontend sends matching header |

---

## Do not flip without Dee

- `MOLINA_LTSS_ATTESTATION_ON_FILE`
- `MOLINA_LTSS_AVAILITY_ACTIVE`
- `MOLINA_LTSS_SUBCONTRACTOR_DISCLOSURE_FILED`
