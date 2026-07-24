# MICH / HIDE SNP — How Capitation Dollars Are Built & Spent (CY 2026)

**Source:** MDHHS public actuarial files (downloaded Jun 9, 2026)  
**Local copies:** `NEXUS_LEARNING/MICH_CAPITATION_CY2026/`  
**Use:** Call prep (CareSource Brian routing), MCO outreach, NEMT market-size modeling  

**Official page:** https://www.michigan.gov/mdhhs/doing-business/providers/mi-coordinated-health

| File | Purpose |
|------|---------|
| `CY2026_MICH_Certification_Report.pdf` | Milliman actuarial certification narrative |
| `Appendix_2_CY2026_Cost_Models.xlsx` | **Benefit PMPM by service category** (the spend breakdown) |
| `Appendix_3_CY2026_Capitation_Rate_Development.xlsx` | **Total monthly capitation rate** by member tier + admin loads |
| `Appendix_4_MI_Coordinated_Health_Medicaid_Trends.xlsx` | Trend factors (not parsed here) |

---

## HOW MONEY FLOWS (30-SECOND VERSION)

1. **CMS** pays the **Medicare Advantage (HIDE SNP)** portion.  
2. **MDHHS** pays the **Medicaid** portion (Appendix 3 rates — **monthly PMPM**).  
3. Each of the **9 MCOs** receives capitation **per enrolled dual-eligible member** by **rate cell** (how sick / where they live).  
4. The MCO must **pay providers** to deliver the **benefit package** (Appendix M in state contract) — hospitals, pharmacies, **NEMT vendors**, **HCBS/waiver providers**, nursing homes, etc.  
5. What is left after claims + mandated admin = plan margin (not publicly line-itemed per MCO).

**The $6.88B (7-year) award table** = actuarial **projection** if enrollment matches bid assumptions — **not** a guaranteed lump sum.

---

## MEMBER TIERS (RATE CELLS) — WHO GETS WHICH PMPM

MDHHS certifies **8 Medicaid rate cells** (Appendix 2 & 3). Every dual-eligible member falls into one:

| Rate cell | Who (plain English) | CY2026 Medicaid **effective rate** (Appendix 3) |
|-----------|---------------------|--------------------------------------------------|
| **Community Well — 65+** | Dual-eligible, **community**, generally healthier senior | **$487.72 / month** |
| **Community Well — Under 65** | Dual-eligible, community, under 65 | **$364.80 / month** |
| **NF Level of Care — 65+** | **Nursing-facility level of need** but living in **community** (HCBS waiver) | **$2,790.78 / month** |
| **NF Level of Care — Under 65** | Same, under 65 | **$2,986.78 / month** |
| **Nursing Subtier A — 65+ / U65** | In **nursing home** (subtier A) | **$7,749 / $7,542 / month** |
| **Nursing Subtier B — 65+ / U65** | In nursing home (subtier B — higher acuity) | **$11,936 / $11,566 / month** |

**Statewide blended average (all cells, Appendix 3):** **~$886.11 / member / month** Medicaid capitation.

**Wayne + Macomb HAP orientation (~4,500 members):** Mix will skew **Community Well** + **NF Level of Care** (LTSS-heavy duals) — not nursing-home subtier unless institutionalized.

---

## WHERE DOLLARS GO — BENEFIT PMPM BY CATEGORY (APPENDIX 2)

Below = **Medicaid benefit cost PMPM** embedded in capitation (actuarial **expected spend**, not a budget memo to MCOs).

### Community Well — 65+ (largest pool statewide: ~501K member-months exposure CY2026)

| Category | PMPM | Annualized | Notes |
|----------|------|------------|-------|
| Inpatient hospital | $14.79 | $177 | |
| Outpatient hospital | $8.97 | $108 | |
| Pharmacy | $5.26 | $63 | |
| **Emergency transportation** | **$1.65** | **$20** | Ancillary |
| **Non-emergency transportation (NEMT)** | **$6.30** | **$76** | **Ancillary — actuarial “medical NEMT” bucket** |
| Other ancillary (DME, dental, etc.) | $25.04 | $300 | |
| Professional (PCP, specialist, labs, etc.) | $24.72 | $297 | |
| **LTSS — Hospice** | $3.32 | $40 | |
| **LTSS — Nursing home** | $24.76 | $297 | Some NF spend in community tier |
| **LTSS — HCBS (waiver / home & community)** | **$302.43** | **$3,629** | **Waiver services bucket — personal care, waiver supports, etc.** |
| **Subtotal LTSS** | **$330.51** | **$3,966** | |
| **Total medical + LTSS benefit PMPM** | **$418.23** | **$5,019** | Before admin / DCW add-ons |

**Plus (Appendix 3, same cell):** Admin **$33.92** + DCW add-on **$63.78** → **$487.72** total Medicaid capitation PMPM.

### Community Well — Under 65

| Category | PMPM |
|----------|------|
| **Non-emergency transportation** | **$10.88** |
| **HCBS** | **$205.18** |
| **Total benefit PMPM** | **~$311** (sum of categories) |
| **Total capitation (Appendix 3)** | **$364.80 / month** |

### NF Level of Care — 65+ (HCBS waiver in community — high LTSS)

| Category | PMPM |
|----------|------|
| **Non-emergency transportation** | **$55.11** |
| **HCBS** | **$2,027.06** |
| **Total benefit PMPM** | **~$2,209** |
| **Total capitation (Appendix 3)** | **$2,790.78 / month** |

### NF Level of Care — Under 65

| Category | PMPM |
|----------|------|
| **Non-emergency transportation** | **$89.52** |
| **HCBS** | **$2,138.98** |
| **Total capitation (Appendix 3)** | **$2,986.78 / month** |

---

## CRITICAL LINK TO BRIAN’S TWO-LANE MODEL (Jun 7, 2026)

| Brian’s lane | Actuarial home (Appendix 2) | Who gets paid |
|--------------|----------------------------|---------------|
| **Medical transport → MTM** | **Ancillary → Non-Emergency Transportation** (+ emergency transport) | **MTM** (plan’s medical NEMT broker/vendor) |
| **Non-medical → DDI via CM service plan** | **LTSS → HCBS** (waiver services authorized on individualized service plan) | **Credentialed waiver providers (DDI)** |

**Important:** Public actuarial files **do not sub-split HCBS** into “non-medical transport vs personal care vs respite.” The **$302 PMPM HCBS** (Community Well 65+) is a **combined waiver-services bucket**. On the Brian call, ask: **what HCBS service codes / waiver line items** map to non-medical transport, and **what rate** ($28/$35 base + $1.85/mi loaded mileage vs fee schedule).

**NEMT PMPM is NOT DDI’s lane** under Brian’s clarification — that’s the **medical** bucket MTM serves, even though DDI’s contract says “NEMT” in LTSS checklist language.

---

## UTILIZATION HINT — MEDICAL NEMT (COMMUNITY WELL 65+)

Appendix 2 actuarial inputs for **Non-Emergency Transportation** (Community Well 65+):

- **Utilization:** ~2,029 services per 1,000 members per month (~**2 trips/member/month** statewide average in model)  
- **Cost per service:** ~**$37.27** (actuarial allowed — not necessarily HAP’s $28/$35 base + $1.85/mi)  
- **PMPM:** **$6.30**

That medical NEMT volume sits with **MTM**, not DDI, per Brian.

---

## WHAT MCOs MUST COVER (CONTRACT — NOT IN EXCEL)

State HIDE SNP contract **Appendix M** requires coverage including:

- **Item 28:** Non-emergency medical transportation (medical)  
- **Item 18:** Home and community-based services  
- **Item 34:** Personal care services  
- Plus hospital, pharmacy, NF, dental, therapies, etc.

**Appendix N** (contract) spells **NEMT network, 24/7 access, dedicated phone on ID card** — plan-level obligation; Brian says **medical** fulfillment is **MTM**.

---

## HAP CARESOURCE CONTEXT

| Metric | Value |
|--------|-------|
| HAP 7-yr state award (est.) | **~$559.6M** (DTMB synopsis — enrollment-driven) |
| HAP Wayne + Macomb live members (orientation) | **~4,500** |
| DDI contract | **Non-medical waiver transport** (per Brian) — **not** full medical NEMT book |
| DDI trip rates (confirmed Jun 2026) | **$28** ambulatory / **$35** wheelchair base + **$1.85/mi** loaded mileage |

**Rough HCBS pool (if all 4,500 were Community Well 65+ — illustrative only):**  
$302.43 PMPM × 4,500 = **~$1.36M/month** in actuarial **HCBS** capitation through HAP for that hypothetical mix — **entire waiver bucket**, not transport alone. Transport is a **slice** Brian must define.

---

## QUESTIONS FOR BRIAN CALL (GROUNDED IN THIS DATA)

1. Confirm: **Medical NEMT PMPM / MTM** vs **non-medical drawn from HCBS waiver** — matches state actuarial split?  
2. Which **HCBS waiver service type / procedure codes** bill for non-medical transport to Vendor 100000469269?  
3. Confirm **$28 / $35 base + $1.85/mi** maps to non-medical HCBS billing codes (vs medical NEMT fee schedule)?  
4. For **NF Level of Care** members ($2,027+ HCBS PMPM), is non-medical transport volume higher priority for DDI?  
5. Will CMs see DDI under **Provider Sourcing** for waiver transport distinct from MTM in directory?

---

## FILES & LINKS

- MDHHS MICH page: https://www.michigan.gov/mdhhs/doing-business/providers/mi-coordinated-health  
- Award synopsis (9 plans, $6.88B): DTMB RFP 240000002334  
- Intel index: `NEXUS_LEARNING/MICH_HIDE_SNP_STATE_MCO_AWARDS.md`  
- **Contract excerpts (Appendix M/N, broker rebuttal):** `NEXUS_LEARNING/MICH_HIDE_SNP_NEMT_CONTRACT_EXCERPTS.md`  
- Call prep: `BIDS:RESOURCES/HAP CARESOURCE NEMT NETWORK/BRIAN_ROUTING_CALL_PREP_2026-06-08.md`

---

*Actuarial PMPM ≠ check to DDI. Shows how state expects MCO capitation to cover benefit categories. DDI revenue = authorized non-medical trips × contracted rate × volume.*
