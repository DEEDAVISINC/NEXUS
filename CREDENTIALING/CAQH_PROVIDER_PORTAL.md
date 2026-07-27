# CAQH Provider Data Portal — Dee Davis Inc.

**Last Updated:** July 27, 2026  
**Source of truth also:** `COMPANY_INFO_MASTER.md` · `company_info.py` (`CAQH_PROVIDER_ID`)

---

## Credential Record

| Field | Value |
|---|---|
| **CAQH Provider ID** | **16876320** |
| **Named individual** | Dieasha Davis |
| **Company** | Dee Davis Inc. |
| **Address on invite** | 755 W. Big Beaver Rd., Suite 2020, Troy, MI 48084 |
| **NPI (link on profile)** | 1538939111 |
| **CHAMPS Provider ID** | 6309049 |
| **Invite received** | July 27, 2026 @ ~6:06 PM ET |
| **From** | CAQH System Administrator `<ProviewSystemAdministrator@proview.caqh.org>` |
| **Portal** | https://proview.caqh.org/pr |
| **Support** | 888-599-1771 (have CAQH ID ready) |
| **Status** | 🟡 **INVITED** — registration / profile / authorization / attestation **NOT complete** |

---

## What This Means

- A participating healthcare organization requested DDI/Dieasha in CAQH.
- Completing CAQH speeds MCO credentialing (Humana in progress + other plans).
- **CAQH does NOT grant plan participation.** Contact each organization separately for contracts.

---

## Required Steps (Do in Order)

1. [ ] **Register** — click invite link, or go to proview.caqh.org/pr → “Check for CAQH ID” → use ID **16876320**
2. [ ] **Complete profile** — standardized data elements (practice, NPI, licenses, work history, etc.)
3. [ ] **Set authorization** — allow participating organizations to access the profile
4. [ ] **Attest + upload supporting documentation**
5. [ ] **Update this file + `company_info.py` `CAQH_STATUS`** → `REGISTERED` then `ATTESTED`
6. [ ] **Flip PENDING_ACTIONS row** to DONE when attested

---

## Free Training

After login: Help (upper right) → **Get Trained** (on-demand).  
Chat support available inside the portal.

---

## Related System Files

- `COMPANY_INFO_MASTER.md` — Healthcare licenses + CHAMPS/NEMT + MCO table
- `PENDING_ACTIONS.md` — Priority action row
- `company_info.py` — `CAQH_PROVIDER_ID`, `CAQH_PORTAL_URL`, `CAQH_STATUS`
- Humana / MCO credentialing status — `COMPANY_INFO_MASTER.md` → MCO CREDENTIALING STATUS
