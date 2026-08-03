# Availity Essentials — Dee Davis Inc. Organization Account

**Last Updated:** July 29, 2026  
**Source email:** Availity Notification `<gateway-prd@availity.com>` → `info@deedavis.biz`  
**Received:** July 29, 2026 @ ~9:36 AM ET  
**Subject:** Updates regarding your recently submitted Availity registration

> **PASTE NOTE:** Trailing `brian.Grcevich@caresource.com` / “Press tab to insert” in the Gmail paste was **autocomplete UI noise only** — disregard. Not related to this Availity approval.

---

## Account Record

| Field | Value |
|---|---|
| **Status** | ✅ **APPLICATION APPROVED** — organization account live |
| **Organization** | DEE DAVIS INC. |
| **Application ID** | **63821858** (from Jul 23 registration) |
| **Customer ID** | **3878016** |
| **Admin** | Dieasha D. Davis / Dee D Davis |
| **User ID** | **DEEDAVISINC** (from RegistrationInfo.html) |
| **Admin email** | info@deedavis.biz |
| **NPI on registration** | **1538939111** — **VERIFY on org profile after login** (Molina atypical: missing NPI = claim denials) |
| **CHAMPS** | 6309049 |
| **EIN** | 84-4114181 |
| **Portal** | Availity Essentials |

---

## What This Means

| Is | Isn’t |
|---|---|
| Org account approved — admin can manage users / access | Automatic payer enrollment for every plan |
| Unlocks Availity path for Molina LTSS (NPI must be on profile) | Auto 837 submit from VERTEX (still manual / future build) |
| Clears NEXUS hard gate `MOLINA_LTSS_AVAILITY_ACTIVE` | Molina member referrals by themselves |

---

## Required Steps (today / this week)

1. [ ] Log in to Availity Essentials with existing User ID / password
2. [ ] **Account → My Account → Manage My Organization** — confirm Customer ID **3878016**
3. [ ] Confirm **NPI 1538939111** is present and correct on the organization profile
4. [ ] Review admin onboarding / quick reference guide (link in approval email)
5. [ ] Add users only as needed — **do not share User IDs** (Availity policy)
6. [ ] Update this file when NPI verified on profile
7. [ ] Molina PA remains **fax only** — never request PA via Availity

---

## NEXUS Flags

| Flag | Value | As of |
|---|---|---|
| `MOLINA_LTSS_ATTESTATION_ON_FILE` | `True` | Jul 29, 2026 |
| `MOLINA_LTSS_AVAILITY_ACTIVE` | `True` | Jul 29, 2026 (approval email) |

Both Molina NMT + CTS hard gates are now clear in code. First live trips still need eligibility check every service + QC before VERTEX invoice.

---

## Related

- Registration receipt: iCloud `AGREEMENTS /AVAILITY/RegistrationInfo.html`
- Calendar follow-up Jul 30: can mark done / skip — approved early Jul 29
- Ops: `MOLINA_HIDE_SNP_OPERATIONS.md`
- Billing: `nemt_billing.py`, `VERTEX_PAYER_PROFILES.json` (payer ID **38334**)
