# MOLINA HIDE SNP LTSS OPERATIONS — DEE DAVIS INC.

**Contracting party:** Molina Healthcare of Michigan, Inc.
**Plan / program:** HIDE SNP LTSS (Non-Medical Transportation + Community Transition Services)
**Contract type:** Molina Michigan HCBS Provider Services Agreement (PSA — FFS)
**Vendor ID:** 214337479 (credentialed thru Jul 31, 2029)
**Fully executed:** Jul 22, 2026
**Executed PDF:** `BIDS:RESOURCES/MOLINA HIDE SNP LTSS NETWORK/CONTRACTS/Molina_HIDE_SNP_LTSS_PSA_Fully_Executed_2026-07-22.pdf`
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

**Source of truth:** `BIDS:RESOURCES/MOLINA HIDE SNP LTSS NETWORK/CONTRACTS/Molina_HIDE_SNP_LTSS_PSA_Fully_Executed_2026-07-22.pdf`, page 15

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

**CTS invoice formula:** `$150 assessment (T1028, billed once) + PCSP-authorized amount (T2038)` — computed by `nemt_billing.compute_cts_claim()`. DDI never guesses the T2038 dollar figure; it comes from the LTSS Specialist team and is entered against the CTS record before invoicing.

---

## COMMUNITY TRANSITION SERVICES (CTS) — SECONDARY SERVICE, FULL PRISM WORKFLOW

**CTS is not a ride.** It's a one-time case-management service for a member moving from a nursing facility into their own residence — no mileage, no driver, no pickup/dropoff. PRISM tracks it as its own order type, separate from NMT trips.

**What the service actually covers (per Provider Manual, MLTSS section p.141):** *"Non-reoccurring expenses for Members transitioning from a nursing facility to another residence where the Member is responsible for his or her own living arrangement."* Think: security deposit, essential furnishings (bed, table, chairs), moving costs, utility setup — **one-time only, never rent or recurring utilities.**

### The CTS workflow (in order)

```
1. Care Coordinator authorizes CTS on the member's PCSP
2. DDI gets the PCSP-authorized dollar amount from the LTSS Specialist team
   (T2038 is "Manual" pricing — there is NO fixed rate to bill against until
   this number is obtained)
3. DDI completes the home & environment assessment (T1028, $150 flat)
4. DDI coordinates/purchases the authorized non-recurring setup items,
   keeping itemized receipts for every purchase
5. Itemized total is checked against the authorized amount — PRISM flags
   (does not silently allow) any overage
6. Claim submitted: T1028 ($150) + T2038 (authorized amount)
```

### Where this lives in PRISM

| Component | Function / config |
|---|---|
| Order creation (manual entry) | `prism_nemt.create_community_transition_order()` |
| Order creation (from generic PRISM intake, `service_key=community_transition` or `cts`) | `prism_nemt.create_cts_from_prism_intake()` — auto-fires alongside the NEMT auto-link on every intake submission |
| Readiness / pre-invoice checklist | `nemt_billing.check_cts_readiness_checklist()` — checks both Molina hard gates, PCSP authorization on file, transitioning-from/to documented, assessment completed, receipts within budget, no recurring charges |
| Claim calculation | `nemt_billing.compute_cts_claim()` |
| QC checklist (CTS-1 → CTS-9) | `prism_orders_api.SERVICE_QC_CHECKLISTS['community_transition']` |
| Workflow stages | `prism_orders_api.SERVICE_STAGE_OVERRIDES['community_transition']` |
| Required scanback docs | `prism_orders_api.SERVICE_EXPECTED_DOCS['community_transition']` — PCSP/CTS Authorization, Home & Environment Assessment (T1028), Itemized Expense Receipts, Proof of New Residence |
| Routing/margin reference | `prism_service_router.SERVICE_CATALOG['community_transition_assessment']`, `['community_transition_services']` |

### API routes (live once PRISM is running)

| Route | Purpose |
|---|---|
| `GET /prism/nemt/cts` | List all CTS records |
| `POST /prism/nemt/cts` | Manually log a new CTS record |
| `GET /prism/nemt/cts/<cts_id>` | Get one CTS record |
| `PATCH /prism/nemt/cts/<cts_id>` | Set `pcsp_authorized_amount`, mark `assessment_completed`, add/replace `itemized_expenses` |
| `GET /prism/nemt/cts/<cts_id>/claim` | Preview the T1028+T2038 claim + readiness checklist before invoicing |
| `GET /prism/nemt/cts/by-prism/<prism_id>` | Look up the CTS record linked to a PRISM order |

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
| CTS readiness checklist + claim | `nemt_billing.check_cts_readiness_checklist()`, `compute_cts_claim()` |
| QC contract profile | `BIDS:RESOURCES/MOLINA HIDE SNP LTSS NETWORK/QC_CONTRACT_PROFILE.md` |

**To go live:** once Dee confirms (1) attestation signed & returned and (2) Availity active with NPI confirmed, flip both flags in `nemt_billing.py` to `True`. No other code changes needed — PRISM will immediately start allowing Molina trips through the eligibility gate.

---

## RELATED DOCS

- `BIDS:RESOURCES/MOLINA HIDE SNP LTSS NETWORK/QC_CONTRACT_PROFILE.md` — QC/audit reference
- `CLIENT OUTREACH/ACTIVE_RELATIONSHIP_STATUS.md` — relationship history & contacts
- `PENDING_ACTIONS.md` — attestation + Availity tracking (check nightly)
- `PIPELINE_TALLY.md` — revenue pipeline entry
- `NEXUS_QUALITY_CONTROL_FRAMEWORK.md` — system-wide QC master
