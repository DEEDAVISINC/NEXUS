# SHIELD Pilot Proposal — Wayne County Lead-Safe Navigation

**From:** Dee Davis Inc. (DDI) + Community Wellness Connections (CWC)
**To:** Angela Medina, Section Manager, Care Coordination, EHB | Aimee Surma, EHB
**Date:** April 27, 2026
**Re:** Pilot structure for DDI/CWC as Third-Party Administrator for childhood blood lead testing and follow-up navigation in Wayne County

---

## The Problem

Michigan's universal blood lead testing law (MCL 333.5474d, effective April 30, 2025) requires every child to be tested at 12 and 24 months. In 2024, only **20.3%** of Michigan children under 6 were tested. In Wayne County alone, approximately **39,460 mandatory tests per year** are needed based on birth data — the vast majority are not happening.

When a child does test elevated (4.1% of tested children statewide), the follow-up system is fragmented. Families are left to navigate abatement contractors, emergency housing, benefits enrollment, transportation, and clinical follow-up on their own — or rely on overstretched local health departments to coordinate it all.

There is no unified system that schedules the test, tracks the result, activates follow-up services, verifies completion, and bills the payer. SHIELD is that system.

---

## The Proposal

DDI proposes a **90-day pilot** in Wayne County in which DDI operates as the **Third-Party Administrator (TPA)** for all mandatory childhood blood lead testing and follow-up services.

### What DDI Does

- **Schedules every mandatory BLL test** for children at 12 and 24 months in the pilot area
- **Manages the testing workflow** — routes families to Quest Diagnostics or LHD labs, arranges NEMT when needed, tracks results in SHIELD
- **Activates the full service cascade** when a child tests elevated: navigator assigned, home visit conducted, CLPPP referral submitted, remediation coordinated, emergency housing placed, benefits enrolled, retesting scheduled
- **Verifies every service delivery** through automated two-way confirmation (contractor confirms, family confirms, both sides verified before payment)
- **Bills the payers directly** — MCOs, Medicaid FFS, and private insurers. Not MDHHS.
- **Reports real-time outcomes** to MDHHS through a dedicated partner portal with live data on SLA compliance, service completion rates, and county-level metrics

### What CWC Does

- **Staffs the navigator workforce** — trained Community Health Workers embedded in Wayne County communities
- **Delivers direct services** — CHW home visits, MIBridges benefits enrollment, housing navigation, lead-safe education, family support
- **Serves as the community-facing brand** — families interact with Cause We Care, not a government agency

### What MDHHS Does

- **Routes referrals** through existing CLPPP/LHD channels into SHIELD
- **Provides vendor introductions** for certified lead abatement contractors, nurse home visit agencies, and emergency housing partners in Wayne County
- **Monitors outcomes** through the `/mdhhs` partner portal — no manual reporting required
- **Pays nothing** — DDI bears all operational costs and bills payers directly

---

## Pilot Structure

### Geography

**Wayne County** — Michigan's largest county by population (1.77M), highest birth volume (~19,730/year), and high prevalence of pre-1978 housing stock and elevated blood lead levels. CWC already has community presence here.

### Duration

| Phase | Duration | What Happens |
|-------|----------|-------------|
| **Ramp-Up** | Weeks 1-2 | DDI onboards navigator team, seeds SHIELD with LHD referral sources, configures vendor network, trains CWC navigators on system |
| **Active Intake** | Weeks 3-14 (90 days) | Open enrollment — every referral served. DDI schedules tests, activates services, verifies delivery, bills payers |
| **Evaluation Gate** | Day 90 | MDHHS reviews pilot data: SLA compliance, service completion rates, family satisfaction, billing accuracy, volume handled |
| **Decision** | Day 90-100 | Go/no-go on Phase 2 expansion based on real data |

### Volume

**Open enrollment** — every CLPPP/LHD referral and every test DDI schedules during the 90-day window is served. No artificial cap.

Projected volume at 25% capture in first 90 days:
- ~2,466 tests scheduled
- ~101 elevated cases entering full service cascade
- ~740 NEMT trips arranged

This is not a 10-family demonstration. This is a real operational pilot at real volume.

### Staffing

| Role | Count | Entity | Responsibility |
|------|-------|--------|----------------|
| Navigator (CHW) | 3-5 | CWC | Caseload of 15-25 active families each. Home visits, scheduling, benefits enrollment, family support |
| Navigator Supervisor | 1 | DDI/CWC | Quality oversight, SLA monitoring, service approval, billing verification |
| Program Director | 1 | DDI (Dee Davis) | MDHHS relationship, vendor management, system operations, reporting |

### Technology

**SHIELD** — Screening, Housing, Intake, Education, Lead Defense

| Component | Function | Access |
|-----------|----------|--------|
| Caseworker Intake (`/refer`) | External referral submission | LHD caseworkers, CLPPP staff |
| Navigator Workspace (`/navigator`) | Daily case management, service activation, call/SMS, time tracking | CWC navigators |
| MDHHS Partner Portal (`/mdhhs`) | Real-time outcomes, SLA compliance, county metrics | Angela, Aimee, LHD directors |
| Family Status Tracker (`/status`) | Case progress visibility | Families (case number + last name) |
| VERTEX Billing | Automated claim generation, supervisor approval, payer routing | DDI back office |
| Verification Engine | Two-way SMS confirmation with contractors and families | Automated |

All data is HIPAA-compliant. Every entry point displays a mandatory compliance acknowledgment.

---

## Service Lines — 9 Total

| # | Service Line | Delivered By |
|---|-------------|-------------|
| 1 | Blood Lead Level (BLL) Testing | Quest Diagnostics / LHD Labs |
| 2 | CLPPP Case Management | MDHHS CLPPP (DDI navigates families into program) |
| 3 | NEMT | DDI / Uber Health |
| 4 | Lead Remediation Coordination | Subcontracted abatement vendors |
| 5 | Housing Navigation | CWC Navigators + MSHDA |
| 6 | MIBridges Benefits Navigation | CWC Navigators |
| 7 | Filter Safety Net / Drinking Water | Get Ahead of Lead program |
| 8 | Community Health Worker Home Visit | CWC Navigators (CHW certified) |
| 9 | Nurse Home Visit | Subcontracted nurse agency |

Full service delivery map with vendor details, contract status, and MDHHS asks: see attached **SHIELD Service Fulfillment Map**.

---

## How DDI Gets Paid (Zero Cost to MDHHS)

DDI does not request funding from MDHHS. DDI bills existing payers — Medicaid MCOs, Medicaid FFS, and private insurers — for services already covered under their benefit structures.

| What DDI Bills For | Who Pays |
|--------------------|----------|
| Community Health Worker navigation time | MCOs / Medicaid / Private insurers |
| Non-Emergency Medical Transportation | Michigan Medicaid / MCOs |
| Coordination of subcontracted services (remediation, nurse visits) | Pass-through from payer reimbursement |

**Why this works:** The universal testing law creates a mandate. Medicaid and MCOs are already obligated to cover BLL testing, CHW services, and NEMT for enrolled children. Private insurers cover the same for their members. DDI organizes and manages what the payers are already required to fund — MDHHS just provides the referral pipeline.

---

## 90-Day Success Metrics

| Metric | Target | How Measured |
|--------|--------|-------------|
| **Referral-to-first-contact** | < 48 hours | SHIELD SLA tracker (automated) |
| **Test scheduling rate** | 90%+ of referred families tested within 14 days | SHIELD activation records |
| **Service completion rate** | 85%+ of activated services reach "Verified Complete" | Two-way verification engine |
| **Family satisfaction** | 4.0+ / 5.0 | Survey at case closure |
| **Billing accuracy** | 95%+ clean claims (first-pass) | VERTEX claim submission records |
| **Navigator utilization** | 80%+ of available hours logged | Auto time tracking in SHIELD |
| **Elevated case resolution** | Average < 90 days from referral to retest | SHIELD case lifecycle timestamps |

All metrics are available in real time on the MDHHS partner portal. No manual reporting. No quarterly spreadsheets.

---

## Phase 2 Expansion Plan

If the 90-day Wayne County pilot meets success metrics:

| Phase | Timeline | Scope |
|-------|----------|-------|
| **Phase 1** (this proposal) | Months 1-3 | Wayne County — 3-5 navigators |
| **Phase 2** | Months 4-6 | Add Oakland County — 2-3 navigators |
| **Phase 3** | Months 7-9 | Add Macomb + Genesee — 2-3 navigators each |
| **Steady State** | Month 10+ | 4 counties, 10-15 navigators, full compliance pipeline |

Each phase uses the same SHIELD platform, same verification engine, same billing pipeline. Adding a county means adding navigators and vendor relationships — the system scales without rebuilding anything.

---

## What We Need from MDHHS

### At the 5/4 Meeting

1. **Agreement on Wayne County as pilot geography** and referral routing through CLPPP/LHD into SHIELD

2. **Vendor introductions** in Wayne County:
   - Certified lead abatement contractors
   - Emergency/temporary housing partners
   - Nurse home visit agencies
   - MSHDA regional representative
   - Get Ahead of Lead filter supplier pipeline

3. **Confirmation on CHW billing structure:**
   - Can DDI (Type 2 NPI) bill as the org with CHW-certified CWC navigators as rendering providers?
   - Does the referring physician's NPI travel with the CLPPP/LHD referral, or does DDI need to establish an attending provider relationship?

4. **Introduction to MCO contract leads** — DDI is credentialing with Molina, UHC, Meridian, HAP, Priority Health, McLaren, Aetna Better Health. MDHHS introductions accelerate the process.

### Not Requested

- Funding
- Grants
- New legislation
- IT infrastructure
- Staffing

DDI provides everything. MDHHS provides the referral pipeline and vendor network. Families get served.

---

## About the Partners

### Dee Davis Inc. (DDI)

Federally certified EDWOSB contract management firm headquartered in Troy, Michigan. DDI operates as a TPA across healthcare, logistics, and compliance services. Proprietary AI technology platforms (NEXUS, SHIELD, VERTEX, FleetFlow) power operations. Michigan Medicaid NEMT provider (CHAMPS ID 6309049). Existing partnerships with Quest Diagnostics, Uber Health, and Concentra.

**CAGE:** 8UMX3 | **UEI:** HJB4KNYJVGZ1 | **EIN:** 84-4114181

### Community Wellness Connections (CWC)

501(c)(3) nonprofit serving Wayne County and Southeast Michigan. Community Health Worker training and deployment. MIBridges Community Partner. Direct community presence in the neighborhoods most affected by lead exposure.

**Domain:** cwecare.org

---

## Attached Documents

1. **SHIELD Service Fulfillment Map** — Vendor details for all 9 service lines
2. **CWC + DDI Overview One-Pager** — Sent to Angela + Aimee 4/23/2026
3. **CWC + DDI Meeting Brief** — From 4/23 partnership meeting
4. **SHIELD Demo Video** — Pre-recorded system walkthrough *(in production)*

---

*SHIELD — Screening, Housing, Intake, Education, Lead Defense*
*Every Family Deserves a SHIELD*
