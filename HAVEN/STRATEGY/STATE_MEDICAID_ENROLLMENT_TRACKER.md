# STATE MEDICAID PROVIDER ENROLLMENT TRACKER

**Purpose:** Track DDI's Medicaid provider enrollment status in each target state for NEMT/Personal Care TPA expansion.

**Universal Credential:** NPI: 1538939111 (works in all states)

---

## ENROLLMENT STATUS BY STATE

| State | System | Portal URL | Status | Provider ID | Enrolled Date | Notes |
|-------|--------|------------|--------|-------------|---------------|-------|
| **Michigan** | CHAMPS | milogintp.michigan.gov | ✅ **ENROLLED** | 6309049 | 03/23/2026 | Active through 12/31/2999. HAP CareSource contract live. |
| **Texas** | TMHP | tmhp.com | 🔲 **PRIORITY** | — | — | ⚠️ **HHSC NEMT OE (HHS0016482) closes Sept 15, 2026** — DDI can be TPA prime. Requires: TX SOS ($750) + TMHP + insurance. See `STATE_NEMT_STRUCTURE_INTELLIGENCE.md` |
| **Ohio** | MITS | medicaid.ohio.gov | 🔲 **PRIORITY — WEEKEND** | — | — | ⚠️ **ALERT:** Both Molina + Humana require OH Medicaid enrollment. Once approved: (1) Submit Molina via portal, (2) Re-send Humana to ohionetworkspecialist@humana.com with Medicaid ID. |
| **Georgia** | GAMMIS | gammis.georgia.gov | 🔲 Not Started | — | — | — |
| **Florida** | FMMIS | mymedicaid-florida.com | 🔲 **PRIORITY — WEEKEND** | — | — | ⚠️ **ALERT:** Once approved, reply to Humana FL LTC (LTCnetworkrequests@humana.com) with Medicaid ID. They requested: Legal name, TIN, NPI, Medicaid ID, effective date, service address, service county. |
| **Tennessee** | TennCare Connect | tn.gov/tenncare | 🔲 Not Started | — | — | — |
| **Louisiana** | Medicaid Web Portal | lamedicaid.com | 🔲 Not Started | — | — | — |
| **Alabama** | Alabama Medicaid | medicaid.alabama.gov | 🔲 Not Started | — | — | — |
| **Mississippi** | Envision | medicaid.ms.gov | 🔲 Not Started | — | — | — |
| **South Carolina** | SC DHHS | scdhhs.gov | 🔲 Not Started | — | — | — |

---

## STATUS KEY

| Symbol | Meaning |
|--------|---------|
| ✅ **ENROLLED** | Active Medicaid provider, can bill |
| 🟡 **PENDING** | Application submitted, awaiting approval |
| 🔲 Not Started | No application submitted yet |
| ❌ Denied | Application denied (with reason) |

---

## ENROLLMENT PRIORITY

**Tier 1 — Immediate (Active MCO Conversations):**
1. Michigan ✅ DONE
2. Texas — 5 MCOs in outreach pipeline
3. Ohio — 5 MCOs in outreach pipeline
4. Georgia — 4 MCOs in outreach pipeline

**Tier 2 — Near-Term (Outreach Sent):**
5. Tennessee — 3 MCOs contacted
6. Florida — 5 MCOs contacted
7. Louisiana — MCOs contacted
8. South Carolina — MCOs contacted

**Tier 3 — Pipeline:**
9. Alabama — Hot reply received (Stephanie Logan, Andrew Hill)
10. Mississippi — Magnolia credentialing in progress

---

## ENROLLMENT PROCESS NOTES

### What You Need for Most State Medicaid Enrollments:
- [ ] NPI (1538939111) ✅
- [ ] FEIN / Tax ID
- [ ] Business license (state where enrolling)
- [ ] Proof of liability insurance
- [ ] W-9
- [ ] Banking info for EFT
- [ ] Provider type selection (usually "Atypical Agency" or "Transportation Provider" for NEMT TPA)

### Michigan CHAMPS Lessons Learned:
- Enrolled as **Atypical Agency / NEMT** — this was the correct provider type
- Initial application had wrong category — MDHHS Provider Enrollment Unit (AJT) clarified
- Contact: Provider Support 800-979-4662, option 1
- Email: MSA-HomeHelpProviders@michigan.gov
- Approval was fast once correct category selected (submitted 03/22, approved 03/23)

---

## ACTION ITEMS

### 🔥 WEEKEND PRIORITY (May 17-18)
- [ ] **Florida:** Initiate FMMIS enrollment at mymedicaid-florida.com — **BLOCKED:** Humana FL LTC waiting for Medicaid ID to process DDI's request. Once approved, reply to LTCnetworkrequests@humana.com with full credentialing info.
- [ ] **Ohio — MITS:** Initiate Ohio Medicaid enrollment at medicaid.ohio.gov — **BLOCKED:** Both Molina Ohio AND Humana Ohio require Ohio Medicaid enrollment to credential. Once approved:
  - Submit to Molina via Ohio Provider Contracting Guide portal
  - Re-send to Humana at ohionetworkspecialist@humana.com with Ohio Medicaid ID
- [ ] **Texas:** Initiate TMHP enrollment — high priority given 5 MCOs in pipeline

### Standard Queue
- [ ] **Georgia:** Research GAMMIS enrollment process

---

## WHEN TO ENROLL

**Strategy:** Enroll in a state when:
1. You have an active MCO conversation advancing toward contract, OR
2. You win a contract that requires state Medicaid billing

**Don't pre-enroll everywhere** — it creates maintenance overhead (annual renewals, etc.) for states where you have no contracts.

**Exception:** If a state has a long enrollment timeline (60-90 days), start early when you see serious MCO interest.

---

*Last Updated: May 14, 2026 @ 6:20 PM*
*Next Review: May 19 (Monday) — Check FL Medicaid enrollment status, reply to Humana FL LTC if approved*

---

## KEY REFERENCE

**See `STATE_NEMT_STRUCTURE_INTELLIGENCE.md`** for how NEMT is structured in each state (FFS vs MCO-only vs Broker). This determines DDI's path — TPA prime opportunity vs MCO contracts only.
