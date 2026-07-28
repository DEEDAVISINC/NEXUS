# NEXUS Billing Module — Plan vs VERTEX Reality
**Date:** July 28, 2026  
**Source plan:** Draft architecture (internal review) — “NEXUS Billing Module Integration Plan”  
**Compared against:** Live VERTEX NEMT/CTS stack + ironclad tranche 1 (`VERTEX_MEDICAL_BILLING_IRONCLAD.md`)

---

## Verdict

The draft plan is **directionally right** and names the real end-state (837 → 835 → denials → AR → contract volume monitor).  
It is **not** a greenfield build. Calling it a new “Billing Module” as if VERTEX doesn’t exist will duplicate work and confuse ownership.

**Map the plan onto VERTEX** (medical claims) + keep standard invoicing on existing VERTEX invoices. Do **not** invent a parallel billing system.

---

## Division split — agree / adjust

| Plan says | NEXUS reality | Call |
|---|---|---|
| Medical claims: DEPOINTE NEMT, Molina CTS, SHIELD | NEMT + CTS already in `nemt_billing.py` / PRISM | ✅ Agree |
| Standard invoicing: HAVEN, VITAL, ARENA, 3D Ink, Freight | Already VERTEX invoices / not HCPCS | ✅ Agree |
| DNA = separate review | Correct — lab rules ≠ NEMT | ✅ Agree |
| “Billing is ad hoc per contract” | Partially outdated — HAP/Molina have rate engines + scrub; submit/ERA still ad hoc | ⚠️ Soften language |

---

## Phase map — plan vs built

| Plan phase | Status in NEXUS today | Gap |
|---|---|---|
| **1 Encounter capture** | ✅ Mostly — PRISM trip/CTS intake + Mark Complete → VERTEX; HCPCS/rate at claim compute | Extend SHIELD codes; force code+rate at intake UI for all medical lanes |
| **2 Eligibility 270/271** | 🟡 Soft — HAP stamps + portal confirm flag; Molina hard gates; **no real 270/271** | Real Availity eligibility API / logged portal check |
| **3 Claims engine 837P/CMS-1500** | 🟡 Partial — CMS-1500 **payload in invoice notes** + factoring HTML; **not** true 837P | Build 837P exporter per payer profile |
| **4 Clearinghouse submit** | ❌ Manual | Availity submit path (HAP first; Molina 38334) |
| **5 Remittance 835 + AR aging** | 🟡 Manual `post_payment` only | 835 parse, denial queue, 30/60/90 AR |
| **6 Contract compliance monitor** | ❌ Not built (closest: QC profiles + pipeline tallies) | Volume-vs-contract flags (HAP zero-referral pattern) |
| **7 GBIS / revenue spread** | 🟡 VERTEX REVENUE exists; GBIS separate | Wire reconciled claim $ into GBIS |

**Ironclad tranche 1 already shipped (Jul 28):** scrub, timely filing clock, Molina payer ID 38334, QC no-record block, opt-in API token, tests. That sits **between** plan Phase 1–3 — pre-submit defense.

---

## Data model — plan vs code

| Plan entity | Closest existing | Action |
|---|---|---|
| Payer | `MICHIGAN_MCO_PAYERS` in `nemt_billing.py` | Expand into formal payer profiles (filing, appeal, clearinghouse) |
| Contract | QC_CONTRACT_PROFILE + Airtable + PDF paths | Tag clauses (timely filing, appeal, referral mins) |
| Member/Rider | Trip/order fields (Medicaid ID, etc.) | Keep in PRISM; don’t fork |
| Encounter | PRISM NEMT order / CTS case / trip log | Rename conceptually → “encounter”; same store |
| Claim | VERTEX INVOICES (NEMT source) | Add claim status machine (draft/scrubbed/submitted/paid/denied) |
| Remittance | `post_payment` → VERTEX REVENUE | Add 835 import + denial reasons |
| Denial/Appeal | ❌ | New queue + 90/120 clocks (Molina orientation B7–B8) |
| AR aging | ❌ | Snapshot from claim status + DOS/submit dates |

---

## Immediate next-step options — recommendation

| Option | What it is | Recommendation |
|---|---|---|
| **1** Build Phase 1 encounter prototype | Partially done for NEMT/CTS | **Do not restart** — only extend SHIELD + intake UI gaps |
| **2** Draft HAP + Molina payer profile specs | Specs from signed contracts | **Do this week** — unlocks Phase 3–4 without wrong IDs/windows |
| **3** Draft Phase 6 contract compliance monitor first | Volume vs contract terms | **High defensive value** for HAP pattern — **build after payer profiles**, or as a thin parallel dashboard using existing trip/claim counts |

### Recommended sequence (grounded)

1. **Option 2 now** — formal HAP + Molina payer profiles (timely filing, appeal, clearinghouse IDs, Availity payer IDs, rate source = signed fee schedule).  
2. **Then Phase 4/5 thin slice** — 837 export + denial/AR queue (the money path).  
3. **Phase 6** as a **monitor on top of claim volume** (not a separate billing system) — flag zero claims / zero referrals over N days vs contract expectations.

**Do not** pick Option 1 as a greenfield “Billing Module.” That would rebuild VERTEX under a new name.

---

## Naming / ownership rule

| Lane | Owns it |
|---|---|
| Medical claims (NEMT, CTS, future SHIELD claim codes) | **VERTEX Medical Billing** (`nemt_billing` + scrub + future 837/835) |
| Standard commercial invoices | **VERTEX** invoices (existing) |
| Field delivery / encounter truth | **PRISM** |
| Contract deliverables / POP | **COMPASS** |
| Pre-award / compliance matrix | **GPSS** |
| Volume-vs-contract alerts | New **monitor** under VERTEX/COMPASS — not a 4th billing stack |

---

## Compliance note (keep from plan)

Before live 837/835: billing/compliance advisor review — timely filing, HIPAA transaction standards, payer-specific rules. Plan disclaimer stays.

---

## Bottom line

The plan describes the **right end-state**.  
VERTEX already owns **Phases 1–3 partial**.  
Next money move is **payer profiles → submit/ERA**, not a new module brand.  
Phase 6 is the **strategic defense** against dead contracts — build it as a monitor, not a rewrite.
