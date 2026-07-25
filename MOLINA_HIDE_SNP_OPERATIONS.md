# MOLINA HIDE SNP LTSS OPERATIONS — DEE DAVIS INC.

**Contracting party:** Molina Healthcare of Michigan, Inc.
**Plan / program:** HIDE SNP LTSS (Non-Medical Transportation + Community Transition Services)
**Contract type:** Molina Michigan HCBS Provider Services Agreement (PSA — FFS)
**Vendor ID:** 214337479 (credentialed thru Jul 31, 2029)
**Fully executed:** Jul 21, 2026 (Effective Date) — Provider signed Jul 17, 2026; Molina countersigned Jul 21, 2026
**Executed PDF (source of truth):** `BIDS:RESOURCES/MOLINA HIDE SNP LTSS NETWORK/CONTRACTS/Molina_HIDE_SNP_LTSS_PSA_Fully_Executed_2026-07-21.pdf`
**Contract index:** `BIDS:RESOURCES/MOLINA HIDE SNP LTSS NETWORK/CONTRACTS/README.md`
**Orientation completed:** Jul 23, 2026 (Sarah Fenton, Provider Services / LTSS Orientation)
**Orientation deck (archived):** `BIDS:RESOURCES/MOLINA HIDE SNP LTSS NETWORK/ORIENTATION/Molina_LTSS_Provider_Orientation_2026-07-23.pptx`

---

## 🔴 GO-LIVE STATUS — TWO HARD GATES OPEN

DDI **cannot receive members** until both of these clear:

1. **Orientation Training Attestation** — must be signed and returned to `MHMLTSSContracting@MolinaHealthCare.Com`. Watch inbox — Sarah Fenton said this would be emailed after the Jul 23 orientation.
2. **Availity portal activation** — registered Jul 23 (App ID 63821858), Availity confirmed 3-5 business days to activate (~Jul 28-30). Once active, confirm NPI **1538939111** is entered in the provider profile — atypical providers (NEMT has no professional licensure) deny claims without it.

Both gates are enforced in code — see `nemt_billing.py`: `MOLINA_LTSS_ATTESTATION_ON_FILE` and `MOLINA_LTSS_AVAILITY_ACTIVE`. PRISM's `check_member_eligibility_checklist()` will fail dispatch automatically until Dee confirms both are done and flips these flags to `True`.

---

## SCOPE (Attachment B — visually confirmed)

**Source of truth:** `BIDS:RESOURCES/MOLINA HIDE SNP LTSS NETWORK/CONTRACTS/Molina_HIDE_SNP_LTSS_PSA_Fully_Executed_2026-07-21.pdf`, Attachment B (page 15)

| Service | Status |
|---------|--------|
| **Non-Medical Transportation (NMT)** | ✅ Checked in executed Attachment B |
| **Community Transition Services (CTS)** | ✅ Checked in executed Attachment B |

**Coverage area:** Statewide (HIDE SNP LTSS program is not region-limited like HAP CareSource's Region 10).

---

## RATES

**Source:** `CONTRACTS/Molina_LTSS_Fee_Schedule_2026-04-01.pdf` — **100% of published fee schedule, no discount.**

| Component | HCPCS | DDI Rate |
|-----------|-------|----------|
| NMT ambulatory base trip | T2003 | **$27.00** |
| NMT wheelchair van base trip | A0130 | **$35.00** |
| NMT ambulatory mileage (loaded) | S0215 | **$0.67/mi** |
| NMT wheelchair van mileage (loaded) | S0209 | **$3.00/mi** |
| Community Transition Services | T2038 | **"Manual"** — negotiated per case with LTSS Specialist before invoicing |
| Community Transition assessment | T1028 | **$150.00 flat** |

**Invoice formula (NMT):** `Base + (loaded miles × per-mile rate)`

| Example | Calculation | Molina pays DDI |
|---------|-------------|------------------|
| Ambulatory, 5 mi | $27 + (5 × $0.67) | **$30.35** |
| Ambulatory, 15 mi | $27 + (15 × $0.67) | **$37.05** |
| Wheelchair, 5 mi | $35 + (5 × $3.00) | **$50.00** |
| Wheelchair, 15 mi | $35 + (15 × $3.00) | **$80.00** |

**Note:** Molina's mileage rates are notably richer than HAP CareSource's flat $1.85/mi for all trip types — especially wheelchair ($3.00/mi vs $1.85/mi). Wheelchair/WAV trips are the stronger margin lane here.

**VERTEX / NEXUS billing:** `nemt_billing.compute_trip_claim()` — auto-detects Molina payer, applies base HCPCS (T2003/A0130) + mileage line (S0215/S0209). Ops must enter **actual loaded mileage** on Mark Complete, same as HAP.

**CTS invoice formula:** `$150 assessment (T1028, billed once IF a home assessment was required and completed) + Amount Authorized (T2038)` — computed by `nemt_billing.compute_cts_claim()`. DDI never invents the T2038 dollar figure; it is set by DDI's own Authorization Sign-Off, driven by the real invoice(s) collected in Step 3 — Michigan State Plan Medicaid funds the release, DDI does not cut the check.

---

## COMMUNITY TRANSITION SERVICES (CTS) — SECONDARY SERVICE, FULL PRISM WORKFLOW

**CTS is not a ride.** It's a case-management "Authorization Case" for a member moving from a nursing facility into their own residence — no mileage, no driver, no pickup/dropoff. PRISM tracks it as its own case type (`community_transition`), separate from NMT trips, with its own 7-stage lifecycle.

**What the service actually covers (per Provider Manual, MLTSS section p.141):** *"Non-reoccurring expenses for Members transitioning from a nursing facility to another residence where the Member is responsible for his or her own living arrangement."* One-time only — never rent or recurring utilities.

**STARTING SCOPE (Operative Constraint):** Only **Security Deposit** and **Utility Set-up** expense categories are accepted right now. **Furnishings** and **Moving Costs** require subcontractor disclosure under **Article 2.9** of the executed Molina HCBS PSA — not yet completed as of the Jul 23, 2026 orientation. PRISM hard-blocks those two categories at intake (`nemt_billing.MOLINA_LTSS_SUBCONTRACTOR_DISCLOSURE_FILED = False`) until Dee confirms the disclosure is filed.

### The CTS Authorization Case — 7 stages (in order)

```
1. Referral Received          — discharge planner or Care Coordinator contacts DDI
2. Eligibility/PCSP Verification — member active + CTS approved on the PCSP (Y/N)
3. Documentation Collected     — real invoice/quote per expense item, no verbal estimates
4. Home Assessment (if required) — physical suitability review -> T1028 ($150) becomes billable
5. Authorization Sign-Off      — DDI authorizes release of funds -> T2038 becomes billable
                                  at DDI's Amount Authorized (rate still unconfirmed w/ Molina)
6. Funds Released / Case Closed — Molina pays direct, or DDI pass-through (mechanism TBD)
7. Documented for Audit         — full record retained
```

PRISM auto-computes the current stage (1-7) from case field state every time the case is saved — ops doesn't manually set the stage number, they just fill in the fields for whatever step they're on (`nemt_billing.compute_cts_stage()`).

### Intake fields (the "CTS Authorization Case")

Member ID/Name/DOB, Referral Source + Date, PCSP Confirmation (Y/N), Transition Destination Address, Requested Expense Category (dropdown, Security Deposit/Utility Set-up open — Furnishings/Moving Costs blocked), Requested Amount (per line item), Supporting Document Upload (required before authorization), Home Assessment Required? (Y/N) + Result, Authorization Status (Pending/Verified/Authorized/Denied), Authorization Date, Amount Authorized, Payee, Case Notes.

### Intake source — dedicated address

CTS referrals come from **nursing facility discharge planners or Molina Care Coordinators** — not member call-ins like NEMT rides. To keep financial/authorization documents (invoices, assessments, sign-off records) out of the ride-booking inbox and preserve a clean audit trail per Molina's contract requirements, CTS intake routes to its **own dedicated address: `cts@deedavis.biz`** (set up mail routing/forwarding to the LTSS ops team) rather than `nemt@deedavis.biz`. See `prism_orders_api.SERVICE_ROUTING_EMAILS['community_transition']`.

### Where this lives in PRISM

| Component | Function / config |
|---|---|
| Order creation (manual entry) | `prism_nemt.create_community_transition_order()` |
| Order creation (from generic PRISM intake, `service_key=community_transition` or `cts`) | `prism_nemt.create_cts_from_prism_intake()` — auto-fires alongside the NEMT auto-link on every intake submission; does NOT require pickup/dropoff |
| Current stage (1-7) auto-computed | `nemt_billing.compute_cts_stage()` |
| Expense category gate (Article 2.9) | `nemt_billing.check_cts_expense_category_allowed()` — blocks Furnishings/Moving Costs until `MOLINA_LTSS_SUBCONTRACTOR_DISCLOSURE_FILED = True` |
| Readiness / pre-invoice checklist | `nemt_billing.check_cts_readiness_checklist()` — checks both Molina hard gates, referral recorded, PCSP confirmation, documented expenses w/ supporting docs, home assessment (if required), authorization sign-off w/ amount + payee |
| Claim calculation | `nemt_billing.compute_cts_claim()` |
| QC checklist (CTS-1 → CTS-9) | `prism_orders_api.SERVICE_QC_CHECKLISTS['community_transition']` |
| Workflow gate overlay (generic PRISM order UI) | `prism_orders_api.SERVICE_STAGE_OVERRIDES['community_transition']` |
| Required scanback docs | `prism_orders_api.SERVICE_EXPECTED_DOCS['community_transition']` — Referral Documentation, PCSP Confirmation, Supporting Invoice/Quote per Expense Item, Home Assessment Report (if required), Authorization Sign-Off Record |
| Routing/margin reference | `prism_service_router.SERVICE_CATALOG['community_transition_assessment']`, `['community_transition_services']` |

### API routes (live once PRISM is running)

| Route | Purpose |
|---|---|
| `GET /prism/nemt/cts` | List all CTS cases (filter by `?status=` or `?stage=`) |
| `POST /prism/nemt/cts` | Log a new CTS case (Step 1 — Referral Received) |
| `GET /prism/nemt/cts/<cts_id>` | Get one CTS case |
| `PATCH /prism/nemt/cts/<cts_id>` | Update PCSP confirmation, home assessment, authorization sign-off, disbursement, case closure — refreshes stage + readiness on every save |
| `POST /prism/nemt/cts/<cts_id>/expenses` | Add one documented expense item — rejects Furnishings/Moving Costs (400) and missing supporting docs (400) |
| `GET /prism/nemt/cts/<cts_id>/claim` | Preview the T1028+T2038 claim + readiness checklist before invoicing (Step 8) |
| `GET /prism/nemt/cts/by-prism/<prism_id>` | Look up the CTS case linked to a PRISM order |

**Same two hard gates apply.** `MOLINA_LTSS_ATTESTATION_ON_FILE` and `MOLINA_LTSS_AVAILITY_ACTIVE` block CTS readiness exactly like they block NMT dispatch — flipping them to `True` clears both service lines at once (same vendor/NPI).

---

## REFERRAL MODEL — DIFFERENT FROM HAP (CRITICAL)

Per the Provider Manual (MLTSS section) and Jul 23 orientation:

- Referrals are **100% member / Care Coordinator-initiated** through the **Person-Centered Service Plan (PCSP)**. DDI **cannot** solicit placement on a vendor list or ask Care Coordinators to send trips.
- DDI's role: be available, credentialed, and responsive when a Care Coordinator authorizes a trip on a member's PCSP.
- **Eligibility must be verified before every service** (Availity or 855-322-4077) — this is **not** auto-verified the way HAP's credentialed parallel-vendor status (100000469269) allows. See `nemt_billing.apply_molina_ltss_intake_defaults()` — it deliberately does NOT set `eligibility_verified = True`.
- **Prior authorization is fax only** — never request PA through Availity.
- **Atypical Provider note:** NEMT is billed under DDI's NPI (1538939111), not a separate Medicaid-only ID — confirmed at orientation. Just make sure Availity has the NPI entered once active.

---

## CORRECT CONTACT ROUTING

| Need | Contact | NOT |
|------|---------|-----|
| Day-to-day authorization / operational questions | LTSS Specialist — `MHM-LTSS-Specialist@MolinaHealthCare.Com` | ❌ Arielle Goodson (contracting closed out) |
| Attestation return | `MHMLTSSContracting@MolinaHealthCare.Com` | — |
| Member eligibility check | Availity (once active) or 855-322-4077 | ❌ Guessing / skipping the check |
| Referral / directory questions | N/A — member/Care Coordinator initiated only | ❌ Do not solicit Care Coordinators directly |
| Prior authorization | Fax only | ❌ Availity |

---

## FIRST PAYMENT

Molina defaults new providers to **ECHO virtual credit card (Quick Remit)**. Watch for the ECHO email after the first claim pays. If direct deposit is preferred, the **Draft Number** off the first Explanation of Provider Payments (EPP) is required to register — instructions were attached to the orientation invite.

---

## PRISM / VERTEX CODE MAP

| Function | Location |
|----------|----------|
| Payer directory entry | `nemt_billing.MICHIGAN_MCO_PAYERS["Molina Healthcare Michigan"]` |
| Contract rates | `nemt_billing.MOLINA_LTSS_CONTRACT_RATES`, `MOLINA_LTSS_*_MILEAGE_PER_MILE` |
| Hard-gate flags | `nemt_billing.MOLINA_LTSS_ATTESTATION_ON_FILE`, `MOLINA_LTSS_AVAILITY_ACTIVE` |
| Intake defaults + gate enforcement | `nemt_billing.apply_molina_ltss_intake_defaults()` |
| Eligibility checklist (gate-aware) | `nemt_billing.check_member_eligibility_checklist()` |
| Trip pricing | `nemt_billing.compute_trip_claim()` |
| PRISM payer auto-detection | `prism_nemt._intake_payer()` (matches "molina", "hide snp", "ltss") |
| CTS order model + intake auto-link | `prism_nemt.create_community_transition_order()`, `create_cts_from_prism_intake()` |
| CTS stage engine + expense category gate | `nemt_billing.compute_cts_stage()`, `check_cts_expense_category_allowed()` |
| CTS readiness checklist + claim | `nemt_billing.check_cts_readiness_checklist()`, `compute_cts_claim()` |
| CTS Article 2.9 subcontractor disclosure flag | `nemt_billing.MOLINA_LTSS_SUBCONTRACTOR_DISCLOSURE_FILED` (False until filed) |
| QC contract profile | `BIDS:RESOURCES/MOLINA HIDE SNP LTSS NETWORK/QC_CONTRACT_PROFILE.md` |

**To go live:** once Dee confirms (1) attestation signed & returned and (2) Availity active with NPI confirmed, flip both flags in `nemt_billing.py` to `True`. No other code changes needed — PRISM will immediately start allowing Molina trips through the eligibility gate.

---

## RELATED DOCS

- `BIDS:RESOURCES/MOLINA HIDE SNP LTSS NETWORK/QC_CONTRACT_PROFILE.md` — QC/audit reference
- `CLIENT OUTREACH/ACTIVE_RELATIONSHIP_STATUS.md` — relationship history & contacts
- `PENDING_ACTIONS.md` — attestation + Availity tracking (check nightly)
- `PIPELINE_TALLY.md` — revenue pipeline entry
- `NEXUS_QUALITY_CONTROL_FRAMEWORK.md` — system-wide QC master
