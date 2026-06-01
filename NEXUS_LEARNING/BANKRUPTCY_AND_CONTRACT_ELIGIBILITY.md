# Bankruptcy & Government Contract Eligibility — Reference

**Added:** May 29, 2026  
**Purpose:** Correct the common assumption that bankruptcy automatically bars bidding. Document how buyers actually treat distressed incumbents — and how DDI uses financial stability in strategy (without naming competitors in proposals).

**Related:** `MODIVCARE_COMPETITIVE_INTEL.md` · `INCUMBENT_VULNERABILITY_SIGNALS.md` · `FEDERAL_CERTIFICATION_VEHICLE_ROADMAP.md`

---

## The Common Misconception

> "You can't be in bankruptcy and go after contracts."

**Reality:** There is **no universal federal or state law** that says "Chapter 11 = cannot bid." What exists is a **responsibility / financial-capacity gate** — and sometimes **explicit solicitation certifications** — that make winning **much harder** while in bankruptcy, and still awkward **after** emergence.

---

## Chapter 11 vs Chapter 7 (Quick)

| Type | What it means | Can they usually keep operating? | Can they usually keep bidding? |
|------|---------------|----------------------------------|--------------------------------|
| **Chapter 11** | Reorganization — debtor restructures debt, continues business | **Yes** — that's the design | **Often yes legally** — subject to responsibility review, bonding, solicitation language |
| **Chapter 7** | Liquidation — wind down | **No** (wind-down) | **Generally no** for new work |

**ModivCare:** Filed **Chapter 11** August 2025 (S.D. Texas). **Emerged** December 29, 2025. Still operating; credibility damaged nationally (Maine, Michigan recompetes).

---

## How Buyers Actually Gate Distressed Vendors

### 1. Responsibility determination (Federal — FAR)

For **federal** awards, the contracting officer must find the offeror **responsible** per **FAR Subpart 9.1** (generally):

- Adequate financial resources / financing to perform
- Satisfactory performance record
- Integrity and business ethics
- Organization and experience
- Necessary equipment, facilities, personnel
- Licensed and authorized to do business

**Bankruptcy is not an automatic disqualifier** on the FAR face — but **financial resources** and **integrity** reviews are where Ch 11 filings hurt. COs and attorneys can make a **non-responsibility** determination if performance risk is too high.

**SAM.gov:** Exclusion/debarment is separate from bankruptcy. Bankruptcy alone does not auto-exclude — unless related conduct triggers exclusion.

### 2. Solicitation-specific certifications

Many RFPs, RFQs, and vendor packets ask bidders to certify:

- Not currently in bankruptcy or insolvency proceedings
- No bankruptcy filing within the past **X years** (3, 5, 7 — varies)
- Not subject to reorganization under bankruptcy laws
- Ability to obtain required bonds and insurance

**If the form requires it → read the exact wording.** Some ask about **active** proceedings only; others ask about **history**. That determines whether an **emerged** debtor can certify "no."

**NEXUS action on every bid:** Compliance matrix row for **financial responsibility / bankruptcy certifications** — pull exact language from Section L / vendor attestation.

### 3. Performance bonds, payment bonds, letters of credit

Large **state Medicaid NEMT broker** contracts often require financial assurances. During active Ch 11:

- Bonding companies frequently **refuse or price prohibitively**
- Practical effect: **cannot perform** even if technically allowed to submit

This is often the **real** barrier — not a statute.

### 4. State & local / Medicaid agency practice

State DHHS, DTMB, and MCO procurement teams apply similar **financial stability** and **continuity of service** logic:

- Will this vendor survive a multi-year broker contract?
- Will members lose rides mid-contract?
- Political risk if incumbent melted down publicly (Maine)

**Maine example:** Bipartisan pressure to void ModivCare award and re-bid — driven by **flawed procurement + financial distress + service risk**, not a single "bankruptcy = banned" statute.

### 5. MCO vendor contracting

MCOs often require:

- W-9, COI, financial statements or parent guarantees
- Vendor diligence on ownership changes post-bankruptcy
- Access2Care / ModivCare brands may remain on MCO networks **after** emergence — relationship continuity ≠ public trust

---

## Timeline: What Changes When

| Phase | Typical bidder status |
|-------|------------------------|
| **Pre-filing distress** (delisting, lawsuits, cash crunch) | Incumbent may still hold contract; challengers build "stability" narrative |
| **Active Chapter 11** | May **continue incumbent work** under court approval; **new awards** face responsibility, bonding, and political headwinds |
| **Post-emergence (plan confirmed)** | **Can bid again** more cleanly — but past Ch 11 appears in diligence, references, and evaluator memory |
| **Recompete window** | Agency often **wants** a new vendor — bankruptcy is one signal among many (CPARS, complaints, scope failure) |

---

## ModivCare — Documented Case (DDI Intel)

| Date | Event |
|------|-------|
| Aug 2025 | Chapter 11 filed (S.D. Texas) |
| Dec 29, 2025 | Emerged from Chapter 11 |
| Jul 31, 2026 | Michigan NEMT broker (MA190000000912) expires — recompete FY2026 |
| May 2026 | Maine MaineCare NET recompete posted (0520260310) |

**Takeaway for DDI:** ModivCare was **not automatically removed** from operating or from the market. Maine and Michigan are **recompete opportunities** because buyers and legislators **lost confidence** — bankruptcy + litigation + procurement scandal — not because a single rule barred them forever.

Full competitor timeline: `MODIVCARE_COMPETITIVE_INTEL.md`

---

## DDI Strategy — How to Use This (Buyer-Facing)

### DO (in proposals and CO conversations)

- Lead with **financial stability**: zero debt, no bankruptcy history, zero-fleet = no fleet capital at risk
- Emphasize **program continuity**: distributed partner model, no single-point-of-failure vendor
- Cite **active Michigan Medicaid operations** (CHAMPS, CareSource HIDE SNP) as proof of performance capacity
- On recompetes, frame **member protection** and **evaluator risk reduction** — language evaluators can defend to leadership

### DO NOT (buyer-facing)

- Name ModivCare or any competitor's bankruptcy in a proposal
- Claim competitors are "legally barred" unless solicitation language explicitly says so and you verified
- Overstate — say "DDI maintains no bankruptcy history" (true per company record), not "bankrupt vendors cannot bid"

### Internal GO/NO-GO

When incumbent shows **3+ vulnerability signals** (`INCUMBENT_VULNERABILITY_SIGNALS.md`) **including** Ch 11 or post-emergence instability → **aggressive pursuit** on recompete.

Add to opportunity scoring (optional fields):

- `incumbent_active_bankruptcy` — boolean
- `incumbent_emerged_bankruptcy_12mo` — boolean
- `solicitation_bankruptcy_cert_required` — boolean (from compliance matrix)

---

## NEXUS Workflow Checklist — Every Solicitation

- [ ] Search RFP for: *bankrupt*, *insolv*, *financial responsibility*, *bond*, *letter of credit*, *debar*, *exclusion*
- [ ] Add compliance matrix rows for each financial attestation
- [ ] If recompete: check `MODIVCARE_COMPETITIVE_INTEL.md` and incumbent USASpending / news
- [ ] If DDI ever faces financial questions: escalate to counsel — do not guess on certifications

---

## Quick Answers for Dee

| Question | Answer |
|----------|--------|
| Can a company in Chapter 11 bid? | **Often yes** — Ch 11 is designed to keep them operating. Winning is another story. |
| Can they hold the incumbent contract? | **Often yes** — especially with court approval; extensions happen. |
| Why does Maine re-bid if they can still bid? | **Political + procurement failure + distrust** — not a permanent legal ban. |
| Is ModivCare still in bankruptcy? | **No** — emerged **Dec 29, 2025**. History still matters. |
| DDI advantage? | **No Ch 11 history**, local accountability, zero-fleet, EDWOSB — defensible stability story. |

---

*When in doubt on a specific certification, read the solicitation language — do not rely on this summary alone for a signed attestation.*
