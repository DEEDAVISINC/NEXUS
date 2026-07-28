# VERTEX Payer Profiles — HAP CareSource + Molina
**Status:** Spec for implementation (Option 2 — Jul 28, 2026)  
**Owner:** VERTEX Medical Billing  
**Rule:** Contract-first — every field cites a signed agreement, orientation deck, or ops source of truth. Do not invent rates or filing windows.

**Machine target (later):** load into `nemt_billing.MICHIGAN_MCO_PAYERS` / `VERTEX_PAYER_PROFILES.json`  
**Related:** `NEXUS_BILLING_MODULE_PLAN_VS_VERTEX.md` · `VERTEX_MEDICAL_BILLING_IRONCLAD.md`

---

## Shared profile schema (every medical payer)

| Field | Required | Purpose |
|---|---|---|
| `payer_key` | Yes | Stable ID in NEXUS (`hap_caresource`, `molina_mi_ltss`) |
| `legal_name` / `plan_brand` | Yes | Claim + invoice display |
| `contract_refs[]` | Yes | Paths to executed PDFs + effective dates |
| `vendor_id` / `npi` / `champs_id` | Yes | Claim header |
| `geography` | Yes | Counties / statewide |
| `services_in_scope[]` | Yes | Attachment B / checklist only |
| `hcpcs_rates[]` | Yes | Code, unit, amount, mileage rules, source doc |
| `clearinghouse` | Yes | Name + electronic payer ID(s) |
| `timely_filing_days` | Yes | From DOS |
| `dispute_days` / `appeal_days` | Yes if known | From remittance / denial |
| `eligibility` | Yes | Method, phone, portal, auto-rules |
| `prior_auth` | Yes | Channel (fax/portal), banned channels |
| `remittance` | Yes | ECHO / EFT / ERA path |
| `volume_monitor` | Yes | Phase 6: expected activity signal |
| `nexus_gates[]` | Yes | Code flags that must be True |
| `open_gaps[]` | Yes | Not yet in NEXUS |

---

# PROFILE A — HAP CareSource (MI Coordinated Health / HIDE SNP NEMT)

## Identity

| Field | Value | Source |
|---|---|---|
| `payer_key` | `hap_caresource` | NEXUS |
| Legal name | Health Alliance Plan / CareSource Michigan (CareSource Provider Agreement) | `CARESOURCE_CONTRACT_SCOPE.md` |
| Plan brand | HAP CareSource — MI Coordinated Health (HIDE SNP) | Same |
| Vendor ID | **100000469269** | Issued Apr 28, 2026 |
| NPI | **1538939111** | COMPANY_INFO_MASTER |
| CHAMPS | **6309049** | Same |
| Taxonomy | 347E00000X (Transportation Broker) / ops also cites NEMT taxonomy as needed | CHAMPS / ops |
| Contract effective | Executed Mar 31, 2026; credentialing/Vendor ID Apr 28, 2026 | Scope doc |
| Contract docs | `BIDS:RESOURCES/HAP CARESOURCE NEMT NETWORK/CONTRACTS/CareSource_Michigan_LTSS_MA_SNP_Fully_Executed_2026-03-31.pdf` | Scope doc |
| DTMB / state note | **Not** MA190000000912 (ModivCare broker) — separate opportunity | Scope doc |

## Geography & scope

| Field | Value |
|---|---|
| Live counties | **Wayne, Macomb** |
| Pending | Oakland (do not claim live until CareSource confirms) |
| In-scope services | LTSS / HIDE SNP **non-medical** NEMT under CM service plan |
| Out of scope | Medical NEMT routed to **MTM**; pharmacy/Rx home delivery (PBM) |

## Rates (claim compute)

| HCPCS | Description | Rate | Notes |
|---|---|---|---|
| T2002 | Ambulatory base | **$28.00** | `HAP_CARESOURCE_CONTRACT_RATES` |
| A0130 | Wheelchair / WAV base | **$35.00** | Same |
| T2003 | Ambulatory loaded mileage | **$1.85 / mi** | Mileage line |
| A0425 | Wheelchair loaded mileage | **$1.85 / mi** | Mileage line |

**Invoice formula:** `Base + (loaded miles × $1.85)`  
**Code:** `nemt_billing.compute_trip_claim()` when payer is HAP/CareSource.

## Clearinghouse / claims

| Field | Value | Source |
|---|---|---|
| Clearinghouse | **Availity** | `HAP_CARESOURCE_OPERATIONS.md` |
| Electronic payer ID (Medicaid) | **MIMCDCS1** | Ops / walkthrough |
| Electronic payer ID (MI Coordinated Health) | **MIMCRCS1** | Same |
| Legacy directory ID | `68069` in `MICHIGAN_MCO_PAYERS` — **confirm before 837**; Availity IDs above are operational | Ironclad note |
| Claim format | 837P (target) / CMS-1500 payload today in VERTEX invoice notes | Ironclad |
| Timely filing | **365 days from DOS** | Ops + walkthrough |
| Dispute / appeal windows | ⚠️ **Confirm from executed agreement / portal** — not hardcoded here until cited | Open |
| Remittance | Portal + **ECHO**; enroll EFT after first payment (888-834-3511) | Ops |

## Eligibility & auth

| Field | Value |
|---|---|
| Eligibility | Portal / Availity — **portal confirm required before claim** (`eligibility_portal_confirmed`) |
| Intake default | Parallel vendor stamp OK for dispatch; **not** a substitute for portal confirm at claim |
| Prior auth | CM service plan / parallel vendor path — `HAP-PARALLEL-VENDOR-100000469269` when no specific auth # |
| Medical vs non-medical | Medical → MTM; DDI = non-medical CM-authorized |

## NEXUS gates

| Gate | Status |
|---|---|
| QC record before invoice | ✅ Required (`VERTEX_QC_ALLOW_LEGACY=0`) |
| Claim scrub + timely filing | ✅ |
| HAP portal confirm for claim | ✅ Scrub warns/blocks per env |
| Live 837 submit | ❌ Gap |
| Denial / appeal clocks | ❌ Gap |

## Volume monitor (Phase 6 inputs)

| Signal | Why |
|---|---|
| Claims/trips per week in Wayne + Macomb | Detect “contract live, zero referrals” (MTM routing conflict pattern) |
| Days since last completed billable trip | Alert if >14 days while contract active |
| County mix | Flag if Oakland trips appear before activation |
| Claim denial rate | Target ≤2% per QC plan |

---

# PROFILE B — Molina Healthcare of Michigan (HIDE SNP LTSS)

## Identity

| Field | Value | Source |
|---|---|---|
| `payer_key` | `molina_mi_ltss` | NEXUS |
| Legal name | Molina Healthcare of Michigan, Inc. | Executed PSA |
| Program | HIDE SNP LTSS | Ops |
| Vendor ID | **214337479** (credentialed thru **2029-07-31**) | Ops / CONTRACTS |
| NPI | **1538939111** (must be on Availity profile — atypical) | Orientation |
| CHAMPS | **6309049** | COMPANY_INFO |
| Effective date | **2026-07-21** | Executed PSA |
| Contract docs | `.../CONTRACTS/Molina_HIDE_SNP_LTSS_PSA_Fully_Executed_2026-07-21.pdf` | Ops |
| Fee schedule source | HCBS fee schedule (NMT/CTS rates match Attachment B coding) | Ops |

## Geography & scope

| Field | Value |
|---|---|
| Geography | **Statewide** (HIDE SNP LTSS) |
| Attachment B in scope | **NMT** + **CTS** only |
| CTS starting categories | Security Deposit + Utility Set-up |
| CTS blocked until Article 2.9 | Furnishings + Moving Costs (`MOLINA_LTSS_SUBCONTRACTOR_DISCLOSURE_FILED`) |
| Referral model | 100% member / Care Coordinator (PCSP) — **DDI cannot solicit list placement** |
| PA channel | **Fax only** — never request PA via Availity |
| Ops contacts | LTSS Specialist `MHM-LTSS-Specialist@MolinaHealthCare.Com`; contracting `MHMLTSSContracting@...` (not Arielle for referrals) |

## Rates (claim compute)

| HCPCS | Description | Rate |
|---|---|---|
| T2003 | NMT ambulatory base | **$27.00** |
| A0130 | NMT wheelchair van base | **$35.00** |
| S0215 | Ambulatory loaded mileage | **$0.67 / mi** |
| S0209 | Wheelchair loaded mileage | **$3.00 / mi** |
| T1028 | CTS assessment | **$150.00** flat |
| T2038 | CTS authorized amount | **Manual** — Authorization Sign-Off amount only |

**NMT formula:** `Base + (loaded miles × mileage rate)`  
**CTS formula:** `T1028 (if assessment) + T2038 (authorized)` — never invent T2038.

## Clearinghouse / claims

| Field | Value | Source |
|---|---|---|
| Clearinghouse | Availity → Molina / ECHO path | Orientation |
| Electronic payer ID | **38334** | Orientation + EFT PDF (B5) — **fixed in code Jul 28** |
| Do not use | `38217` (Priority Health collision — legacy incorrect) | Ironclad |
| Availity App ID | **63821858** (activation pending as of Jul 23 register) | Ops |
| Timely filing | **365 days from DOS** | Orientation B6 |
| Claim dispute | **120 days** from remittance; use **CDRF** | Orientation B7 |
| Post-service appeal | **90 days** from denial | Orientation B8 |
| First payment | ECHO virtual card (Quick Remit) default; Draft # → EFT | Ops |
| ERA | ECHO / providerpayments.com | Orientation |

## Eligibility & auth

| Field | Value |
|---|---|
| Eligibility | Every service — Availity or **855-322-4077** — **not** auto-verified |
| Prior auth | Fax; LTSS Specialist coordinates start |
| Continuity of Care | 90-day CoC on new enrollments — **not modeled in NEXUS yet** |

## NEXUS gates (hard)

| Flag | Must be True to dispatch/bill |
|---|---|
| `MOLINA_LTSS_ATTESTATION_ON_FILE` | Orientation attestation returned |
| `MOLINA_LTSS_AVAILITY_ACTIVE` | Portal live + NPI on profile |
| `MOLINA_LTSS_SUBCONTRACTOR_DISCLOSURE_FILED` | Only for Furnishings/Moving CTS |

Claim scrub also re-checks attestation + Availity at invoice time.

## Volume monitor (Phase 6 inputs)

| Signal | Why |
|---|---|
| NMT trips/week after both hard gates True | Detect silent network / no PCSP flow |
| CTS cases opened vs closed | Case pipeline health |
| Days since last Molina claim | Alert if gates True and volume = 0 for >14 days |
| T2038 without Authorization Sign-Off | Fatal — should already block |
| Dispute/appeal deadlines approaching | Money recovery |

---

## Implementation checklist (code — after Dee approves specs)

1. [ ] Persist profiles as `VERTEX_PAYER_PROFILES.json` (or Airtable VERTEX PAYERS)
2. [ ] Drive `timely_filing_days`, `dispute_days`, `appeal_days` from profile (not only scrub defaults)
3. [ ] Claim status machine: `draft → scrubbed → submitted → paid/denied/partial → appealed`
4. [ ] Denial queue fields: CARC/RARC, remittance date, dispute_due, appeal_due
5. [ ] 837P export using profile clearinghouse IDs (HAP: MIMCDCS1/MIMCRCS1; Molina: 38334)
6. [ ] Phase 6 monitor job: weekly volume vs profile thresholds → PENDING_ACTIONS / Alexa brief

---

## Open confirmations (do not invent)

| Item | Owner |
|---|---|
| HAP dispute/appeal day counts from executed agreement text | Dee / contract read |
| HAP `68069` vs Availity MIMCDCS1/MIMCRCS1 — which goes on 837 | First live claim test |
| Molina fee schedule PDF citation (02.01 vs 04.01 archive) | Ops archive |
| Whether T2004 multi-pass enters Molina scope | Dee — only if DDI will bill it |

---

*Spec only. Not legal advice. Advisor review before live 837/835.*
