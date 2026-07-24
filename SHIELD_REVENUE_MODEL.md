# SHIELD Revenue Model — DDI as TPA for All Mandatory Childhood BLL Testing

**Prepared by:** DDI / NEXUS
**Date:** April 26, 2026
**Updated:** June 10, 2026 — pilot dispatch-volume model added
**For:** Internal — Dee Davis
**Purpose:** Full revenue projection for DDI operating as TPA for universal childhood blood lead level testing in Michigan, per universal testing law (MCL 333.5474d, effective April 30, 2025).

**Complete program framework:** `SHIELD_PROGRAM_COMPLETE_FRAMEWORK.md`

---

## Business Model

DDI is the **Third-Party Administrator (TPA)**. CWC is the **navigation nonprofit**. MDHHS pays **nothing**.

- DDI schedules and manages **all** mandatory BLL tests for children at 12 and 24 months
- CWC navigators deliver all wraparound services
- DDI bills **MCOs** (Molina, UHC, Meridian, HAP, Priority Health, McLaren, Aetna Better Health), **Medicaid FFS**, and **private insurers** — not MDHHS
- DDI earns revenue from: CHW billing codes (navigation), NEMT, and 22.5% admin fees on all subcontracted services
- MDHHS gets a fully managed testing + follow-up pipeline at zero cost

---

## Source Data

### Michigan Medicaid Rates (Verified)

| Code | Description | Rate | Source |
|------|-------------|------|--------|
| **CPT 83655** | Blood Lead Assay (lab test) | $10.03 | MI Medicaid Clinical Lab Fee Schedule (2022, +2.5% 2026) |
| **CPT 98960** | CHW Individual, 15-min unit | ~$25.00 | Coded in SHIELD — **VERIFY IN CHAMPS Monday** |
| **CPT 98961** | CHW Group (2-4), 15-min unit | ~$25.00 | Same code family |
| **CPT 98962** | CHW Group (5-8), 15-min unit | ~$25.00 | Same code family |
| **T2002** | NEMT Ambulatory Base Trip (one-way) | $17.34 | MI MDHHS NEMT FFS Schedule |
| **T2003** | NEMT Mileage/Mile (loaded) | $0.71 | MI MDHHS NEMT FFS Schedule |
| **A0130** | NEMT Wheelchair Van (one-way) | $46.52 | MI MDHHS NEMT FFS Schedule |
| **T2007** | NEMT Waiting Time (per 15 min) | $6.25 | MI MDHHS NEMT FFS Schedule |

### CHW Service Limits (Michigan Medicaid)

- Max 128 units/month per beneficiary (32 hours)
- Max 2 hours/day
- Max 16 visits/month
- Face-to-face or telehealth (no audio-only)
- Requires licensed healthcare provider recommendation

### DDI Admin Fee

- **22.5%** on all subcontracted services (remediation, nurse visits, housing, filters)

---

## Payer Mix — Universal Testing = ALL Payers

The universal testing law covers **every child**, not just Medicaid. DDI bills the child's payer.

| Payer | % of Children | CHW Rate/Unit (est.) | Notes |
|-------|--------------|---------------------|-------|
| Medicaid / MCO | ~42% statewide | ~$25 | Wayne/Genesee higher (~55%) |
| Private Insurance | ~50% statewide | ~$40+ | Oakland higher (~65%). Private pays more. |
| CHIP (MIChild) | included in Medicaid | ~$25 | Medicaid-adjacent |
| Uninsured / Other | ~7-8% | State/grant-funded | Title V, CLPPP, MDHHS block grant |
| **Blended average** | | **~$33/unit** | Weighted by county mix |

---

## Population Data — 4 Pilot Counties

Source: Michigan Vital Statistics, 2024 Provisional Birth Data

| County | Population | Annual Births (2024) | Mandatory Tests/Year (12mo + 24mo) |
|--------|-----------|---------------------|-----------------------------------|
| Wayne | 1,771,063 | 19,730 | ~39,460 |
| Oakland | 1,274,395 | 12,233 | ~24,466 |
| Macomb | 881,217 | 8,522 | ~17,044 |
| Genesee | 401,759 | 4,098 | ~8,196 |
| **Total** | **4,328,434** | **44,583** | **~89,166** |

### Current Compliance Gap

- **Only 20.3%** of Michigan children under 6 were tested in 2024 (135,727 out of ~670,000)
- **4.1%** of tested children had elevated BLL >= 3.5 mcg/dL (5,583 statewide)
- Universal testing law just took effect — MDHHS needs partners to close the gap
- DDI solves this problem

---

## Revenue Stream 1: CHW Navigation on EVERY Test

DDI doesn't bill for the lab test — Quest/LHD does that. DDI bills for scheduling, coordination, and follow-up.

| Activity | Units (15 min) | Revenue (@$33 blended) |
|----------|---------------|----------------------|
| Scheduling call + family coordination | 1 | $33 |
| Day-of confirmation / support | 1 | $33 |
| Results follow-up + documentation | 1 | $33 |
| **Per-test average** | **3 units** | **$99** |

---

## Revenue Stream 2: NEMT for Routine Testing

Families who need transportation to the lab.

| Item | Rate |
|------|------|
| Base trip (one-way) T2002 | $17.34 |
| Avg 10-mile loaded mileage | $7.10 |
| Round trip total | ~$49 |
| % of families needing NEMT | ~30% |
| **Per-test NEMT (when used)** | **$49** |

---

## Revenue Stream 3: Full Elevated Case Service Cascade

When a child tests elevated (BLL >= 3.5 mcg/dL), the full SHIELD cascade activates. This is the complete lifecycle for a family requiring lead abatement — typically 60-90 days.

### Week 1: Discovery + Initial Response

| Service | Who | CHW Units | CHW Revenue | Other Revenue |
|---------|-----|-----------|-------------|---------------|
| BLL result received, family contacted | CWC Navigator | 2 | $66 | — |
| Initial home visit + environmental assessment | CWC Navigator | 4 | $132 | — |
| CLPPP referral + enrollment coordination | CWC Navigator | 2 | $66 | — |
| NEMT to pediatrician for confirmatory draw | DDI/Uber Health | — | — | $49 |
| Confirmatory test scheduled + tracked | CWC Navigator | 2 | $66 | — |
| Lead inspection scheduled with contractor | CWC Navigator | 2 | $66 | — |
| **Week 1** | | **12** | **$396** | **$49** |

### Week 2: Emergency Displacement + Benefits

| Service | Who | CHW Units | CHW Revenue | Other Revenue |
|---------|-----|-----------|-------------|---------------|
| Emergency housing placement coordinated | CWC Navigator | 4 | $132 | — |
| Emergency housing (hotel/temp, 14-30 nights) | Subcontractor | — | — | $1,400-$3,000 |
| DDI 22.5% admin on housing | DDI | — | — | $315-$675 |
| MIBridges — SNAP enrollment | CWC Navigator | 2 | $66 | — |
| MIBridges — Emergency relief (cash) | CWC Navigator | 2 | $66 | — |
| MIBridges — Child care assistance | CWC Navigator | 1 | $33 | — |
| NEMT to MDHHS office | DDI/Uber Health | — | — | $49 |
| Filter Safety Net enrollment + install | CWC Navigator | 2 | $66 | — |
| Water filters (if outside state program) | DDI | — | — | $40-$80 |
| DDI 22.5% on filters | DDI | — | — | $9-$18 |
| Family check-in visits (2x/week) | CWC Navigator | 4 | $132 | — |
| **Week 2** | | **15** | **$495** | **$1,813-$3,822** |

### Weeks 3-6: Remediation + Ongoing Support

| Service | Who | CHW Units | CHW Revenue | Other Revenue |
|---------|-----|-----------|-------------|---------------|
| Lead abatement work | Subcontractor | — | — | $3,000-$10,000 |
| DDI 22.5% admin on abatement | DDI | — | — | $675-$2,250 |
| Remediation coordination (inspections, clearance) | CWC Navigator | 8 | $264 | — |
| Nurse home visit (developmental + clinical) | Subcontractor | — | — | $150-$300 |
| DDI 22.5% admin on nurse | DDI | — | — | $34-$68 |
| NEMT to follow-up pediatric (2 visits) | DDI/Uber Health | — | — | $98 |
| NEMT to WIC office | DDI/Uber Health | — | — | $49 |
| NEMT to housing office / MSHDA | DDI/Uber Health | — | — | $49 |
| CHW home visits during remediation (2x/wk, 4 wks) | CWC Navigator | 16 | $528 | — |
| Lead-safe education, nutrition counseling | CWC Navigator | 4 | $132 | — |
| **Weeks 3-6** | | **28** | **$924** | **$4,055-$12,814** |

### Weeks 7-12: Return + Retest + Closure

| Service | Who | CHW Units | CHW Revenue | Other Revenue |
|---------|-----|-----------|-------------|---------------|
| Clearance inspection coordination | CWC Navigator | 2 | $66 | — |
| Family return-to-home coordination | CWC Navigator | 2 | $66 | — |
| Retest BLL scheduling + follow-up | CWC Navigator | 3 | $99 | — |
| NEMT to retest appointment | DDI/Uber Health | — | — | $49 |
| Post-return home visits (2x/mo, 2 months) | CWC Navigator | 8 | $264 | — |
| Case closure + outcomes reporting | CWC Navigator | 2 | $66 | — |
| **Weeks 7-12** | | **17** | **$561** | **$49** |

### Total Per Elevated Case (Requiring Abatement)

| Revenue Category | Conservative | Target |
|-----------------|-------------|--------|
| CHW Navigation (72 units @ $33) | $2,376 | $2,376 |
| NEMT (8 round trips @ $49) | $392 | $392 |
| DDI Admin — Housing (22.5%) | $315 | $675 |
| DDI Admin — Abatement (22.5%) | $675 | $2,250 |
| DDI Admin — Nurse Visit (22.5%) | $34 | $68 |
| DDI Admin — Filters (22.5%) | $9 | $18 |
| **TOTAL PER ELEVATED CASE** | **$3,801** | **$5,779** |
| **Average** | | **$4,790** |

---

## Year 1 Pilot — Wayne County (Dispatch Volume Model)

**Use this for pilot planning and funder pitch Year 1.** Sized on **1,500–2,000 screening referrals dispatched** (50% capture of mandatory test population), not full-population billing at day one.

| Revenue Stream | Volume | Rate | Estimated Revenue |
|---|---|---|---|
| Screening dispatch coordination | 1,500–2,000 tests | $99/test | $148,500–$198,000 |
| Mobile event fees | 20–30 events | $1,500/event avg | $30,000–$45,000 |
| Per-person mobile screening (events) | 500–750 children | $175–$225/person | $87,500–$168,750 |
| CHW case management (elevated) | 62–82 cases | $3,800–$5,800/case | $235,600–$475,600 |
| Abatement coordination | 40–60 cases | $500/case avg | $20,000–$30,000 |
| HAVEN displacement | 15–25 families | $5,000–$9,000/family | $75,000–$225,000 |
| Sibling screening dispatch | 80–120 siblings | $99/child | $7,920–$11,880 |
| Post-abatement clearance | 55–75 cases | $150/case | $8,250–$11,250 |
| **PILOT YEAR 1 TOTAL** | | | **$612,770–$1,165,480** |

**Retired:** "25 families" pilot sizing. Pilot = dispatch volume + elevated cascade, not family count.

---

## Year 1 — Wayne County (Full Capture Model — Scale Target)

DDI ramps through Year 1: conservative = 25% capture growing to 50%, target = 50% capture.

### Conservative (25% average capture)

| Revenue Stream | Annual |
|----------------|--------|
| Tests scheduled: ~9,865 | |
| CHW on all tests ($99/test) | $976,635 |
| NEMT routine (30% × $49) | $145,019 |
| Elevated cases: ~404 | |
| Elevated case revenue ($4,790 avg) | $1,935,160 |
| **WAYNE COUNTY YEAR 1 (CONSERVATIVE)** | **$3,056,814** |

### Target (50% capture)

| Revenue Stream | Annual |
|----------------|--------|
| Tests scheduled: ~19,730 | |
| CHW on all tests ($99/test) | $1,953,270 |
| NEMT routine (30% × $49) | $290,037 |
| Elevated cases: ~809 | |
| Elevated case revenue ($4,790 avg) | $3,875,110 |
| **WAYNE COUNTY YEAR 1 (TARGET)** | **$6,118,417** |

---

## Year 2+ — All 4 Counties (50% Capture)

| County | Tests/Yr (50%) | All-Test Revenue | Elevated Cases | Elevated Revenue | **County Total** |
|--------|---------------|-----------------|---------------|-----------------|-----------------|
| Wayne | 19,730 | $2,243,307 | 809 | $3,875,110 | **$6,118,417** |
| Oakland | 12,233 | $1,391,073 | 502 | $2,404,580 | **$3,795,653** |
| Macomb | 8,522 | $969,402 | 349 | $1,671,710 | **$2,641,112** |
| Genesee | 4,098 | $466,338 | 168 | $804,720 | **$1,271,058** |
| **TOTAL** | **44,583** | **$5,070,120** | **1,828** | **$8,756,120** | **$13,826,240** |

---

## Full Scale — 100% Capture (Universal Law Compliance)

This is the target. The law says every child gets tested. DDI schedules every test.

| Metric | 50% Capture | 75% Capture | 100% Capture |
|--------|-------------|-------------|--------------|
| Annual tests (4 counties) | 44,583 | 66,875 | 89,166 |
| Elevated cases | 1,828 | 2,742 | 3,656 |
| **Annual Revenue** | **$13.8M** | **$20.7M** | **$27.7M** |
| **DDI Margin (35-40%)** | $4.8M-$5.5M | $7.2M-$8.3M | $9.7M-$11.1M |
| **3-Year Contract Value** | $41.5M | $62.1M | $83.1M |

---

## Revenue Summary — Pipeline Tally Update

| Scenario | Annual Revenue | DDI Annual Margin | 3-Year Value | Use for |
|----------|---------------|-------------------|--------------|---------|
| **Year 1 Pilot (Wayne, dispatch volume)** | **$613K–$1.17M** | TBD at execution | — | **Funder pitch, MHEF/CFSEM, pilot ops** |
| **Year 1 (Wayne, 25% avg capture)** | $3.1M | $1.1M-$1.2M | $9.2M | Full-scale ramp model |
| **Year 1 (Wayne, 50% capture)** | $6.1M | $2.1M-$2.4M | $18.4M | Full mandatory-test capture at scale |
| **Year 2+ (4 Counties, 50%)** | $13.8M | $4.8M-$5.5M | $41.5M | Multi-county expansion |
| **Full Scale (4 Counties, 100%)** | $27.7M | $9.7M-$11.1M | $83.1M | Universal law compliance target |

---

## Items to Verify Monday

1. **CPT 98960 exact rate** — Log into CHAMPS (MiLogin `davisd1221`), pull Medicaid fee screen
2. **MCO rates vs FFS** — MCO-negotiated CHW rates may differ from FFS $25
3. **Private insurance CHW rates** — Confirm $35-60 range through MCO credentialing contacts
4. **Average abatement cost in SE Michigan** — $3K-$10K range needs refinement
5. **Emergency housing cost** — Hotel/temp housing per-night rates in Wayne/Oakland
6. **MiLeadSafe program coverage** — Does state-funded remediation reduce DDI admin fee opportunity?
7. **TPA admin billing code** — Is there a separate code for test scheduling/management beyond CHW?

---

## Why This Is a No-Brainer for MDHHS

1. **MDHHS pays nothing** — All revenue comes from MCOs, Medicaid FFS, and private insurers
2. **Closes their compliance gap** — Only 20.3% of children are being tested; DDI closes that to 100%
3. **The law requires it** — Universal testing is the law. MDHHS needs a partner to execute.
4. **Zero infrastructure cost to the state** — SHIELD already exists, navigators are already trained, DDI already has lab relationships (Quest), NEMT (Uber Health), and MCO credentialing in progress
5. **Proven TPA model** — DDI already operates as TPA for drug testing. Same model, different test.
6. **Real-time accountability** — SHIELD tracks every test, every SLA, every outcome. MDHHS gets `/mdhhs` portal with live data. No manual reporting.

---

*SHIELD — Screening, Housing, Intake, Education, Lead Defense*
*Every Family Deserves a SHIELD*
