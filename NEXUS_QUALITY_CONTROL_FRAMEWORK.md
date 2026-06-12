# NEXUS Quality Control Framework — System-Wide

**Owner:** Dee Davis Inc. — Contract Management TPA  
**Scope:** Every service line, every contract, every buyer type — nationwide  
**Last updated:** May 31, 2026  
**Rule file:** `.cursor/rules/nexus-quality-control-systemwide.mdc`

---

## Core principle

**DDI is prime on every contract. Quality control is not optional, not HAP-only, and not “member surveys only.”**

If a subcontractor fails, **DDI’s CPARS, plan scorecard, and audit trail take the hit.** NEXUS must prove — for any contract, any lane — that DDI:

1. Vetted who executes  
2. Controlled what was delivered  
3. Documented proof  
4. Caught failures before the buyer did  
5. Can produce an audit packet in **≤ 2 business days**

---

## Module roles (where QC lives)

| Module | QC responsibility | Proof artifacts |
|--------|-----------------|-----------------|
| **GPSS** | Pre-award: compliance matrix, sub plan, margin floor, win theme | Bid folder `WORKFLOW_CHECKLIST.md`, requirement matrix |
| **PRISM** | **Field delivery QC** — dispatch gates, compliance modules, inspections, member/client feedback | Orders, scanbacks, inspections, trip snapshots, grade archives |
| **VERTEX** | **Financial QC** — rates, CLINs, timely filing, denial scrub | Invoices, claims, payment reconciliation |
| **COMPASS** | **Contract QC** — deliverables, CO reporting, modifications, performance periods | Deliverables log, monthly reports, comms with CO |
| **ATLAS** | Project milestones, staffing, change control | Milestone sign-off, RAID log |
| **SHIELD** | Verification / eligibility where applicable | Verification steps, audit trail |
| **Subcontractor framework** | 6 pillars before any sub touches work | NDA, non-compete, COI, staffing plan, comms plan |

**Do not collapse lanes:** Member trip grades = PRISM. Billing audits = VERTEX. CO monthly reports = COMPASS.

---

## Universal QC gate — every contract, every delivery

No work starts. No invoice goes out. No period closes until the gate passes.

```
CONTRACT REGISTERED (COMPASS)
    → SUBS CLEARED (6 pillars) if subs used
    → INTAKE COMPLETE (PRISM / GPSS)
    → COMPLIANCE CHECK (lane-specific module)
    → EXECUTE + DOCUMENT
    → QC INSPECTION / VALIDATION
    → CLIENT / MEMBER FEEDBACK (where applicable)
    → VERTEX BILLING MATCH
    → COMPASS DELIVERABLE / PERIOD CLOSE
    → AUDIT ARCHIVE IMMUTABLE
```

| Gate | Pass = | Fail = |
|------|--------|--------|
| Contract registered | COMPASS contract ID, POP, CLINs, CO contact | STOP — no billing narrative |
| Sub cleared | All 6 pillars green | Sub does not start |
| Intake complete | Required fields per service line | STOP — no dispatch |
| Compliance | Lane module returns COMPLIANT | STOP — no release to client/plan |
| Execution | Timestamps, IDs, fulfillment proof | Incident + grievance log |
| QC inspection | Pass or corrected | Rework before bill |
| Feedback | Grade/survey/CO acceptance as required | Escalation per SLA |
| Billing match | VERTEX = contract rate + scope | Hold invoice |
| Period close | COMPASS deliverable submitted | Escalate to Dee |

---

## Nine universal pillars (all contracts)

| # | Pillar | Applies to |
|---|--------|------------|
| 1 | **Authorization & scope** | Eligibility, PO, trip auth, SOW, set-aside rules |
| 2 | **Credentialing** | Agents, subs, collectors, drivers — active + compliant only |
| 3 | **Execution standards** | Lane SOPs, timeliness, chain of custody, fatal-flaw rules |
| 4 | **Documentation** | Immutable record per unit of service (trip, test, scanback, filing) |
| 5 | **Inspection / validation** | AI + human QC where required (scanbacks, DOT fatal flaws, etc.) |
| 6 | **Client / member experience** | Surveys, grades, grievances, CO feedback |
| 7 | **Billing integrity** | Correct rate, units, payer ID, timely filing |
| 8 | **Regulatory & contract compliance** | Training attestations, FAR/DFAR, plan manuals, OSHA/DOT/etc. |
| 9 | **Audit readiness** | Pull any record + crosswalk to invoice in minutes |

---

## Service-line QC overlays (TPA 1–9 + lanes)

Each lane adds **non-negotiable QC checks** on top of the universal gate.

### TPA 1 — Drug Testing & Compliance
| Check | Standard | Module |
|-------|----------|--------|
| Chain of custody | No fatal flaws (49 CFR Part 40) | `prism_dot_compliance.py` |
| MRO | Required on positives | Partner AMRO |
| Clearinghouse | Pre-employment / annual queries when FMCSA | `prism_clearinghouse.py` |
| Random pool | Selection documented | `prism_random_pool.py` |
| Lab | SAMHSA-certified for DOT | Quest / CRL / Labcorp |
| **Audit pull** | Donor ID, collector, lab, MRO, result | PRISM order + VERTEX |

### TPA 2 — Fingerprinting / Biometrics
| Check | Standard | Module |
|-------|----------|--------|
| Print quality | NFIQ / FBI reject rules | `prism_fingerprinting_compliance.py` |
| Channel | Per contract — no unauthorized SWFT claims | `COMPANY_INFO_MASTER.md` |
| Submission | ORI / channel correct | PRISM order |
| **Audit pull** | Capture file, submission receipt, result | PRISM + archive |

### TPA 3 — DNA (DePointe)
| Check | Standard | Module |
|-------|----------|--------|
| Chain of custody | AABB legal collection | `prism_dna_compliance.py` |
| Lab | AABB-accredited for legal/immigration | DDC |
| **Audit pull** | COC, lab accession, result report | PRISM |

### TPA 4 — Notary & Documents
| Check | Standard | Module |
|-------|----------|--------|
| Scanback inspection | Errors found → correction loop | `prism_inspection_engine.py` |
| Agent gate | Onboarding Active + compliance ready | `NEXUS_ONBOARDING_SYSTEM.md` |
| Journal / RON | State rules per act | `prism_notary_compliance.py` |
| **Audit pull** | Scanback, inspection result, agent cert | PRISM |

### TPA 5 — Healthcare Transportation (NEMT / MOB-A)
| Check | Standard | Module |
|-------|----------|--------|
| Eligibility | Plan enrollment / CM authorization | PRISM + payer portal |
| Timeliness | OTP targets per contract | PRISM timestamps |
| Mileage | Loaded miles before complete | `prism_nemt.py` |
| Member grade | SMS + portal gate | `member_satisfaction_survey.py` |
| Grievances | Logged ≤ 48h | **System-wide grievance log (build)** |
| **Audit pull** | Member Trip Grade Report + trip JSON/HTML + VERTEX claim | PRISM + VERTEX |

### TPA 6 — Logistics / Freight / Courier (MOB-C)
| Check | Standard | Module |
|-------|----------|--------|
| POD / chain | Proof of delivery, temperature if cold chain | VITAL SLA modules where Rx |
| Driver DQ | FMCSA file current if CDL | Fleet compliance TPA |
| **Audit pull** | Trip/POD, invoice, compliance file | PRISM/VITAL + VERTEX |

### TPA 7 — Background Screening
| Check | Standard | Module |
|-------|----------|--------|
| FCRA / permissible purpose | Documented | Order intake |
| Turnaround & accuracy | Dispute process | NCS / partner |
| **Module gap** | Need `prism_background_checks.py` | Planned |

### TPA 8 — Medical Credentialing
| Check | Standard | Module |
|-------|----------|--------|
| Primary source verification | Per hospital/VA rules | **Module gap — building** |

### TPA 9 — Workforce Compliance
| Check | Standard | Module |
|-------|----------|--------|
| Bundled screening + physical + drug | Single employer file | Scattered — unify |

### Product / supply lanes (GPSS reseller)
| Check | Standard | Module |
|-------|----------|--------|
| Spec match | RFQ ↔ delivery ↔ bid line item | Bid folder + supplier COA |
| Buyer protection | No supplier bypass | `never-reveal-buyer-to-supplier.mdc` |
| **Audit pull** | PO, delivery proof, invoice | VERTEX + bid folder |

### Facilities (janitorial, grounds, etc.)
| Check | Standard | Module |
|-------|----------|--------|
| Sub 6 pillars | Before site work | Subcontractor framework |
| QA walkthrough | Photos, checklist, CO standards | COMPASS deliverable + sub reports |
| **Audit pull** | Inspection log, photos, invoice | COMPASS + VERTEX |

---

## Buyer-type audit patterns

| Buyer | What they usually sample | What DDI prepares |
|-------|-------------------------|-------------------|
| **MCO / Medicaid plan** | Trips, grievances, OTP, member experience, creds | Member Trip Grade Report, trip register, grievance log, auth proof |
| **Federal CO** | Deliverables, CPARS, billing, sub flow-down | COMPASS deliverables, VERTEX invoices, compliance matrix |
| **State / municipal** | Local preference docs, insurance, performance | COMPASS + cert copies + lane QC logs |
| **Commercial / hospital** | SLA, incident rate, turnaround | PRISM orders + inspection + SLA dashboard |
| **Grant funder** | Population served, outcomes, financials | CWC/DDI grant files — no fabricated metrics |

**Random vs targeted:** Both happen. Build for **100% documentation**; audits sample from your archive.

---

## Per-contract QC registry (required when contract is won)

When GPSS/COMPASS registers a win, create in contract folder:

```
BIDS:RESOURCES/[CLIENT] [BID TYPE] - WON/
├── QC_CONTRACT_PROFILE.md      ← rates, SLAs, reporting cadence, CO/plan QC contact
├── WORKFLOW_CHECKLIST.md       ← gated steps (existing)
├── COMPLIANCE/                 ← COIs, training, attestations
├── QC_LOG/                     ← monthly QC notes, incidents, corrective actions
└── AUDIT_EXPORTS/              ← PDFs pulled for buyer requests
```

**`QC_CONTRACT_PROFILE.md` minimum fields:**
- Contract ID, buyer, POP, service lane(s)  
- Sub(s) if any + pillar status  
- Rate sheet / CLIN map → VERTEX  
- SLAs (OTP, response time, grade targets)  
- Reporting cadence (weekly/monthly/quarterly)  
- Audit contact + last audit date  

---

## Reporting cadence — system-wide

| Cadence | All contracts | Owner |
|---------|---------------|-------|
| **Daily** | Open orders/trips, compliance expirations, failed inspections | Ops |
| **Weekly** | Grievances, F/D grades, claim denials, sub performance | Dee |
| **Monthly** | COMPASS deliverable where required; VERTEX denial rate; OTP/volume | Ops + Billing |
| **Quarterly** | MCO quality packets (where plan); internal QC review | Dee |
| **Annual** | Training re-attestation, insurance renewal, sub re-vet | Compliance |

---

## NEXUS system status — QC capabilities

| Capability | Status | Location |
|------------|--------|----------|
| DOT fatal flaw / drug QC | ✅ | `prism_dot_compliance.py`, `COMPLIANCE_KNOWLEDGE/` |
| Fingerprinting QC | ✅ | `prism_fingerprinting_compliance.py` |
| DNA COC QC | ✅ | `prism_dna_compliance.py` |
| Notary scanback inspection | ✅ | `prism_inspection_engine.py` |
| NEMT member trip grades + MCO packet | ✅ | `member_satisfaction_survey.py`, `member_trip_grade_audit_report.py` |
| Subcontractor 6-pillar framework | ✅ | `.cursor/rules/subcontractor-management.mdc` |
| COMPASS deliverables | ✅ Partial | `compass_api.py` — needs every won contract registered |
| VERTEX billing QC | ✅ Partial | Rate validation manual until auto-scrub complete |
| **System-wide QC registry + VERTEX billing gate** | ✅ | `nexus_qc_engine.py`, `nexus_qc_api.py` |
| **MCO QC Master Breakdown (9 pillars + request index)** | ✅ | `/nexus/qc/mco/breakdown.html` |
| **Grievance log (all lanes)** | ✅ Partial | `nexus_qc_grievances.json` — API live |
| **Background check QC module** | ⬜ | Gap per TPA audit |
| **Freight QC module** | ⬜ | Gap per TPA audit |
| **Facilities QA walkthrough template** | ⬜ | COMPASS template needed |

---

## Implementation priority (engineering + ops)

| Priority | Item | Why |
|----------|------|-----|
| **P0** | Every **won contract** gets `QC_CONTRACT_PROFILE.md` + COMPASS registration | No contract without QC profile |
| **P0** | NEMT: Mark Complete → VERTEX + dispatch UI | Billing QC |
| **P1** | **Grievance / incident log** — all lanes, linked to PRISM order ID | MCO + federal §2.10 pattern |
| **P1** | Extend member-grade pattern to **client satisfaction** for notary/courier/drug (where buyer wants it) | Reusable survey engine |
| **P2** | COMPASS monthly QC report template per contract type | CO reporting |
| **P2** | `prism_background_checks.py` + freight QC module | Close TPA gaps |
| **P3** | Unified QC dashboard in NEXUS UI | Single pane for Dee |

---

## Weekly QC standup (15 min — Dee)

- [ ] Any contract with open gate failure?  
- [ ] Any sub pillar expired (insurance, COI)?  
- [ ] Grievances / F grades / fatal flaws / inspection failures?  
- [ ] Claim denials this week?  
- [ ] Deliverable due to CO/plan in next 14 days?  
- [ ] Audit request pending?  

---

## One-line standard (internal)

> **Every unit of service — trip, test, scanback, delivery, filing — has a compliance check, a proof record, a billing match, and an audit export. No exceptions.**

---

## Related documents

| Doc | Purpose |
|-----|---------|
| `BIDS:RESOURCES/HAP CARESOURCE NEMT NETWORK/HAP_QUALITY_CONTROL_PLAN.md` | HAP instance of this framework |
| `SUBCONTRACTOR_MANAGEMENT` rule | Sub 6 pillars |
| `NEXUS_PRISM_TPA_AUDIT.md` | Module inventory + gaps |
| `DDI_BUSINESS_MODEL.md` | Prime/TPA model |
| `COMPLIANCE_KNOWLEDGE/` | Lane regulatory reference |
| `PRISM_MASTER.md` | Inspection + agent gate detail |

---

*HAP was the first live MCO proof point. This framework is the standard for every contract DDI holds or wins.*
