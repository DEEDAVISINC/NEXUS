# PIPELINE REVENUE TALLY
**Last Updated:** June 12, 2026 ET

---

## SESSION NOTE (June 12)

- **Twilio + 855 voice/SMS** — ✅ **LIVE** and tested (inbound PRISM voice intake + outbound member SMS)
- **Only telephony gap:** **CNAM** — register **DDI** caller ID on **855-773-0035** outbound
- **QC spine + MCO audit HTML** — Live on PA (`nexus_qc`, mco-packet, breakdown)

## SESSION NOTE (June 8)

- **PRISM HAP pipeline — PRODUCTION GATE PASS** — PA `nemt_linked: True` after surgical deploy; portal + NEXUS UI on Netlify live
- **Guest ride tracking** — Ops pastes Uber/Lyft URL in Transport → **📤 Save link** → member sees **🚗 Track live ride** on portal (NOT automatic; NOT Twilio)
- **Portal UX** — Emoji status labels (no more "Agent Assigned"); order ID merge fix; 20s dashboard refresh
- **PA deploy** — Full git clone failed (~370MB); curl hotfix works; consider PA upgrade or shallow clone before HAP volume

## SESSION NOTE (June 7)

- **HAP billing ops** — Pay **once weekly** (not twice); **Wednesday = internal drain day** until portal manual confirms cutoff; each contract (HAP vs BCBSM vs others) gets its own billing profile — no shared Net 30 default
- **ModivCare** — **Inbound only**; no proactive enrollment unless they reach out
- **Mark Complete → VERTEX** — Approved in principle; wiring deferred
- **Netlify portal** — 4 env vars confirmed on `ddi-prism-portal` (`PRISM_API_BASE` → PA)

## SESSION NOTE (June 6)

- **PRISM Hub** — Division notification bells wired to live `/prism/orders` (needs-attention counts)
- **PRISM division workspace** — Real API orders in NEMT workspace; **Agent Network** directory (search/pagination) replaces mock agent cards
- **Electron partner webview** — Uber Health login fix (Chrome UA + OAuth popup modal) — **test after full Electron restart**
- **Tomorrow:** CareSource provider manual lookup · PRISM→VERTEX invoicing ($28/$35 trips) · Square sandbox · Electron Uber login test

## SESSION NOTE (June 2)

- **Texas LRGVDC DPS #2026-02** — Transport-only submission package drafted in `SEND_TO_BUYER/DPS_2026-02_TRANSPORT/` (parked for Dee review — Jun 18 mandatory Weslaco conference + TX SOS)
- LRGVDC questions draft updated (Q6 authorized rep, Q7 Attachment 6 N/A) — send by **Jun 26**
- Texas tracks on free portals only (no BidNet)

## TOTAL PIPELINE: $28M+ LIFETIME (Conservative)

---

## ACTIVE MCO CONTRACTS

| Program | Status | Annual Revenue | DDI Margin | Lifetime Value |
|---------|--------|----------------|------------|----------------|
| **HAP CareSource MI HIDE SNP** | ✅ LIVE | $540K | $216K (40%) | $2.7M (5yr) |
| **Molina Healthcare of Michigan — HIDE SNP LTSS** (Non-Medical Transportation + Community Transition Services — both confirmed in Attachment B scope) | ✅ **CONTRACT EXECUTED Jul 22** — orientation attended Jul 23, Availity pending activation | Rates confirmed: NMT $27/trip (T2003) or $35/trip wheelchair van (A0130) + $0.67-$3.00/mi. Community Transition mostly "Manual" negotiated + $150 assessment. **100% of published fee schedule — no discount.** Annual $ **pending member-choice referral volume** (member-driven, not guaranteed minimum) | TBD once volume known | TBD |

---

## ✅ SUBMITTED — AWAITING AWARD (UNIVERSITY HEALTH, SAN ANTONIO)

| Opportunity | Solicitation | Submitted | Annual Revenue | DDI Margin | Win Prob | Lifetime |
|-------------|--------------|-----------|----------------|------------|----------|----------|
| **Pharmacy Courier** | RFP-226-03-068-SVC | May 17 | **$4.26M** | **$2.0M (47%)** | 55% | $21.3M / $10M margin |
| **Lab Courier** | RFP-226-04-073-SVC | May 17 | $480K | $144K (30%) | 45% | $2.4M / $720K margin |
| **Combined UH** | — | — | **$4.74M** | **$2.15M** | — | **$23.7M revenue / $10.7M margin** |

---

## ACTIVE BIDS — HARD DEADLINES

| Opportunity | Agency | Annual Revenue | DDI Margin | Lifetime | Win Prob | Due Date |
|-------------|--------|----------------|------------|----------|----------|----------|
| **DRPA Occ Medical/Drug** | Delaware River Port Auth | $250K-1.2M | $100K+ | $1.5M+ (5yr) | 20% | **June 5** |
| **Minneapolis MPD Background** | City of Minneapolis | $80-140K | $50K+ | $700K (5yr) | 35% | **June 15** |
| **VIA Transit Drug Testing** | VIA Metropolitan Transit | **$146K** | **$102K (70%)** | **$732K (5yr)** | 40% | **June 16** |
| **SUNY Upstate Home Medical Courier** | SUNY Upstate | $1.5M NTE | TBD | 5yr | 15% | **June 17** ⚠️ county invoice blocker |
| **Oakland County DTC Drug** | 52nd District Court | $65K | $45K (70%) | $325K (5yr) | 50% | **June 23** |
| **LRGVDC AAA Transport (DPS)** | LRGVDC Weslaco TX | $100K–500K* | $25K–175K (30%)* | $300K–1.5M* | 35% | **Jul 10** |
| **LRGVDC Title III RFP** | LRGVDC Weslaco TX | Transport slice only | — | — | 25% | **Jul 10** |
| **HHSC Medicaid DRTS** | Texas HHSC | $500K–3M+* | $100K–900K (25%)* | Multi-yr | 15% | **Sep 15** |
| **VA Madison NEMT IDIQ** | VA Middleton WI | TBD | TBD | 5yr | 20% | **Jun 22** |
| **Nevada NET Broker** | NV Health Authority | Capitation | High risk | — | 10% | **Jul 6** |

*ESTIMATED — see bid folder WORKFLOW_CHECKLIST.md

---

## SUBMITTED — AWAITING AWARD (OTHER)

| Opportunity | Agency | Annual Revenue | DDI Margin | Lifetime | Win Prob | Submitted |
|-------------|--------|----------------|------------|----------|----------|-----------|
| **City of Yonkers Drug Testing** | City of Yonkers | $162.5K | $97.5K (60%) | $650K (4yr) | 40% | Apr 30 |
| **Oakland County HHS Medical** | Oakland County | $50K | $20K (40%) | $150K (3yr) | 30% | Apr 20 |
| **Dutchess County Drug Kits** | County of Dutchess | $5K | $2.5K (50%) | $15K (3yr) | 35% | Apr 17 |

---

## 🧪 DRUG TESTING C/TPA — PIPELINE (Building)

| Target Segment | Est. Contracts | Annual Revenue/Contract | Total Annual | DDI Margin |
|---|---|---|---|---|
| **Trucking (50-200 drivers)** | 10 fleets | $35K | $350K | $250K (71%) |
| **Trucking (200-500 drivers)** | 5 fleets | $75K | $375K | $270K (72%) |
| **Trucking (500+ drivers)** | 2 fleets | $150K | $300K | $200K (67%) |
| **Transit/Municipal** | 3 contracts | $50K | $150K | $100K (67%) |
| **TOTAL DRUG TESTING** | 20 contracts | — | **$1.175M** | **$820K (70%)** |

---

## MCO OUTREACH IN PROGRESS (NEMT + HAVEN TPA)

| State | MCOs | Est. Annual Total | Win Prob | Risk-Adj |
|-------|------|-------------------|----------|----------|
| **Louisiana** | 5 | $4.38M | 25% avg | $1.1M |
| **South Carolina** | 3 | $1.25M | 27% avg | $338K |
| **Mississippi** | 3 | $1.45M | 32% avg | $483K |
| **Georgia** | 4 | $2.0M | 20% | $400K |
| **Tennessee** | 3 | $1.2M | 20% | $240K |
| **Ohio** | 6 | $3.0M | 25% | $750K |
| **Texas** | 7 | $4.5M | 20% | $900K |
| **Florida** | 8 | $5.0M | 20% | $1.0M |
| **Alabama** | 1 | $300K | 10% | $30K |
| **MCO TOTAL** | 40 | **$23.1M** | — | **$5.2M** |

---

## 3D INK SIGNATURES — DIRECT CLIENT PIPELINE

| Category | Targets | Avg Contract | Total Pipeline | Status |
|----------|---------|--------------|----------------|--------|
| **Hospitals + Title + Legal + Elder + Immigration + Settlement** | 100+ | — | **$570K** | Outreach ready |

---

## NOTARY SIGNING INCOME (Active)

| Metric | Jun 2026 |
|--------|----------|
| **Outstanding (all companies)** | $2,230 |
| **Next big deposit** | June 22 — $785 |

---

## SUMMARY TOTALS

| Metric | Conservative | Target |
|--------|--------------|--------|
| **Active Annual Revenue (HAP)** | $540K | $540K |
| **Active Bids (UH if won)** | $4.74M | $4.74M |
| **Active Bids (Other if won)** | $1.5M | $3.5M |
| **Pipeline Annual (if all won)** | $28M+ | $34M+ |
| **Risk-Adjusted Annual** | $7.5M | $9.5M |
| **Active DDI Margin (HAP)** | $216K | $216K |
| **Bid DDI Margin (UH if won)** | $2.15M | $2.15M |
| **Risk-Adjusted Margin** | $3.4M | $4.2M |
| **5-Year Lifetime Value** | $28M+ | $48M+ |

---

## STRONGEST LEADS

1. **University Health (San Antonio)** — $4.74M/year SUBMITTED. Awaiting award.
2. **Oakland County DTC Drug Testing** — LOCAL. 50% win prob. Due Jun 23.
3. **VIA Transit Drug Testing** — $146K/yr, 70% margin. Due Jun 16.
4. **Texas LRGVDC DPS Transport** — EDWOSB wedge into Rio Grande Valley AAA pool. Draft ready; Jun 18 conference gate.
5. **HAP CareSource** — Live contract. Proof point for all NEMT/transport bids.

---

**Texas is on the board — LRGVDC draft parked until you're ready to decide on Weslaco travel. University Health is still the whale. One award changes the whole scoreboard.**
