# YOUR AGENDA — Friday, April 24, 2026

**Today (authoritative date):** **Friday, April 24, 2026.**

**This week:** **CBP** path to **Apr 28 5 PM ET** (4 days); **KY** questions **submitted**, proposals **5/7**; SouthStar broker package **sent 4/22**; **MDHHS EHB partnership meeting held yesterday 4/23 — brief + one-pager delivered 7:04 PM to both Angela Medina and Aimee Surma** (see milestone below, follow-up owed within 2 weeks).

---

```
TOMORROW'S PRIORITIES — Friday, April 24, 2026

1. 🛠  **FIRST THING: SHIELD Airtable build** — Create `nexus_lead_screening`
     base in Airtable with all 10 tables (Referrals, Families, Children,
     Navigators, Service_Activations, Case_Milestones, Contractors, Billing,
     Outcomes_Reporting, Referral_Source_Accounts). Set `LEAD_SCREENING_BASE_ID`
     in `.env`. Run `python3 seed_shield_referral_source_accounts.py --apply`
     to seed Angela Medina + Aimee Surma + 6 LHD placeholders. Verify seed
     results in Airtable UI before moving on.

2. 📝  **CBP Medical Support 70B06C26R00000017** — 4 DAYS OUT. Close remaining
     gaps in `BIDS:RESOURCES/DHS CBP MEDICAL SUPPORT SERVICES/WORKFLOW_CHECKLIST.md`:
     PFT partner, LRP, psych/vision consultants, Quest/Concentra LoCs,
     Attachment 4 pricing, Attachments 5–6, SB plan. Due **Apr 28 5 PM ET**.

3. 🚗  **Laguna Beach Senior Transportation T&CS 26-002** — 3 days out.
     Due **Apr 27 3:00 PM PT** (6 PM ET). PlanetBids lump sum + cost + response
     files. `BIDS:RESOURCES/LAGUNA BEACH SENIOR TRANSPORTATION/`.

4. 📄  **MDHHS pilot structure prep (10-member demo)** — Start the outline —
     selection criteria, 90-day outcomes framework, roles matrix,
     SHIELD outcomes-report export format. Owed at the 5/4-week follow-up.

5. 📬  **Top 5 ready-to-send emails** — DHC Landscaping, Pittsburgh URA Title
     Services, Ohio DOH Medical Courier, USACE Palatka Custodial, OCTA Bicycle
     Count. All have cap statements staged in SEND_TO_BUYER folders.

MEETINGS: None scheduled tomorrow. MDHHS follow-up to be requested for
          week of 5/4 (5/4–5/8).
FOLLOW-UPS DUE:
  - KY DMS addendum watch ~4/30 (6 days)
  - ICE DHS (Tracy Riley) — 30-day follow-up window from Mar 22 reply → hit
  - CBP (Jared Tritle) — no reply since Mar 22 cold intro (33 days silent)
PREP NEEDED:
  - CBP proposal package — confirm HUBZone status in SAM before final pricing
  - MDHHS pilot doc outline — primary source is
    `BIDS:RESOURCES/PARTNERSHIP DOCUMENTATIONS/CWC_DDI_MDHHS_Meeting_Brief.pdf`
```

---

## 🏛️ BUSINESS MILESTONE — MDHHS Environmental Health Bureau Partnership Meeting (held 4/23/2026)

**Meeting:** Microsoft Teams · **Thursday 4/23, 3:00–3:30 PM ET** · CWC+DDI-requested pitch
**Attendees:** Angela Medina (Section Manager, Care Coordination, EHB — `MedinaA@michigan.gov`, 517-897-5203) · Aimee Surma (EHB — `SurmaA@michigan.gov`) · Dieasha D. Davis (CWC+DDI)
**Outcome:** Favorable reception of the **community navigation + program administration partnership model**. MDHHS-committed next steps confirmed. **Positioning: "Partner in Michigan's lead-safe ecosystem."**

**CWC+DDI 24-hour commitment:**
- [x] Send meeting brief + one-pager to Angela and Aimee — **✅ DONE 4/23 7:04 PM ET to both**

**MDHHS committed to (3):**
1. Schedule formal follow-up within 2 weeks (target week of **May 4, 2026**)
2. Share CWC+DDI brief + one-pager with LHD directors in **Wayne, Oakland, Macomb, Genesee, Kent (Grand Rapids), Muskegon**
3. Facilitate introductions to those LHD directors once documentation is reviewed

**CWC+DDI owed at follow-up:**
- [ ] Pilot structure documentation — **10-member demo** for lead screening navigation + housing stability, **90-day outcomes framework**, selection criteria, roles matrix
- [ ] Request introduction to MDHHS Medicaid MCO contract leads (payer-side path)

**Where this lives in NEXUS:**
- Master reference: `COMPANY_INFO_MASTER.md` → "🏛️ MDHHS PARTNERSHIP — LEAD SAFE ECOSYSTEM"
- Primary source PDFs: `BIDS:RESOURCES/PARTNERSHIP DOCUMENTATIONS/CWC_DDI_MDHHS_Meeting_Brief.pdf` + `CWC_DDI_Overview_OnePager.pdf`
- SHIELD `Referral_Source_Accounts` seed: `seed_shield_referral_source_accounts.py` (dry-run shows 2 MDHHS + 6 LHD placeholders; run with `--apply` after `LEAD_SCREENING_BASE_ID` is set in `.env`)

---

# YOUR AGENDA — Wednesday, April 22, 2026 (archived)

**Authoritative date at time of write:** **Wednesday, April 22, 2026.**

**This week:** **CBP** path to **Apr 28 5 PM ET**; **KY** questions **submitted**; **KY** proposals **5/7**; SouthStar broker package **sent 4/22** (`SOUTHSTAR_BROKER_AGREEMENT_COMPLETION.md`).

---

```
TODAY'S PRIORITIES — Wednesday, April 22, 2026

1. **SouthStar** — Broker application + supporting docs **emailed to Jon Shane** **2026-04-22** ✓ — await registration / approval email.
2. **Kentucky DMS (Mine Safety) RFP 128 2600000415** — Written questions **e‑mailed 2026-04-22** ✓ (Robin.Uphoff@ky.gov); await addendum ~**4/30** per RFP — `WRITTEN_QUESTIONS_DUE_2026-04-23.md` in bid folder.
3. **CBP Medical 70B06C26R00000017** — Phase 0 (SAM) + start **SOW compliance matrix** (`00_SOURCE_PACKAGE/`); `CBP_70B06C26R00000017_RESPONSE_PLAN.md` · due **Apr 28, 5:00 PM ET** (verify SAM).
4. **One outbound or follow-up** — If bandwidth after 1–3.

DEADLINES: **4/28** CBP; **4/27** Laguna 3 PM PT; **5/7** KY proposals; KY addendum watch **~4/30**.
```

---

# YOUR AGENDA — Tuesday, April 7, 2026 (archived)

**Session close:** Good night save — BCBSM STARS supplier profile logged complete in `PARTNER_ACCOUNT_UPDATES.md`.

**This week:** Fulton Tuesday, CBP + Harris Thursday — protect margin time on bids, not just email volume.

---

## Priority 1 — Fulton County drug testing (DUE TUESDAY APR 8)

- Folder: `BIDS:RESOURCES/FULTON COUNTY DRUG TESTING/`
- GPSS unlocked — blocked on Concentra pricing per dashboard
- Action: Finalize pricing, package, submit before deadline

---

## Priority 2 — CBP Medical Support 70B06C26R00000017 (DUE APR 28, 2026 — 5:00 PM **ET** — `CBP_70B06C26R00000017_SOLICITATION_FACTS.md`)

- Folder: `BIDS:RESOURCES/DHS CBP MEDICAL SUPPORT SERVICES/`
- GPSS record `recuIBuYAPagC27qt` — technical narrative in progress; **close gaps** in `WORKFLOW_CHECKLIST.md` (PFT partner, LRP, psych/vision consultants, Quest/Concentra LoCs, Attachment 4 pricing, Attachments 5–6, SB plan)
- Action: Package **full** proposal + required attachments for SAM/electronic submission

---

## Priority 3 — Harris Health AB02182026 (DUE THU APR 10)

- Folder: `BIDS:RESOURCES/HARRIS HEALTH RFO AB02182026/`
- Quest panel + Concentra titers confirmations per tracker
- Action: Align NCS scope if still in play for background elements

---

## Same-day if not done


| Task                                | Notes                                                                                                                       |
| ----------------------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| USDA APHIS + Port of Detroit emails | `USDA APHIS EMERGENCY TRANSPORT/SEND_TO_BUYER/` and Detroit Port outreach                                                   |
| DIBBS verification email            | [dibbs_validation@dla.mil](mailto:dibbs_validation@dla.mil)                                                                 |
| Lakota / Sam Cilento call           | **Mon Apr 13, 2026 — 1:30–2:00 PM ET** — Meet `php-xxbr-ewa` — WHORL/DeCA — update `FINGERPRINTING_CURRENT_STATUS.md` after |
| MiLogin MDHHS                       | **davisd1221** — sign in so account stays active                                                                            |
| NAICS 488190 on SAM.gov             | Freight 1st Direct / AOG lane                                                                                               |


---

## Aging follow-ups

- Larry Smith, ModivCare NEMT (Mar 26)
- **Molina — REPLIED:** portal contract request + Jennifer Casbar (MTM / Access2Care) — see `PARTNER_ACCOUNT_UPDATES.md` Michigan CHAMPS section

---

## Hard deadlines (next 14 days)


| Date   | What                                         |
| ------ | -------------------------------------------- |
| Apr 8  | Fulton County drug testing                   |
| Apr 10 | Harris Health RFO (if still current)         |
| Apr 28 | **CBP Medical Support — proposals due 5:00 PM ET (SAM = authority)**      |
| Apr 16 | MDHHS Navigator training (if enrolling)      |
| Apr 13 | **Lakota / Sam Cilento** — 1:30 PM ET (Meet) |
| May 28 | WBENC renewal expires                        |


---

## Vendor queue (one touch per day)

HAP CareSource packet, UHC credentialing, Access2Care/MTM app, WBENC renewal, Abbott/eScreen follow-up, NDS Jean Saporita, Quest/Erika Goad.

---

*Updated: April 7, 2026 — CBP due date: Dee confirmed **Apr 28, 5:00 PM** (amendment/CO; not Apr 21 SF1449 scan).*

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---

---
## COLLECTION ACTIONS DUE — 2026-04-17

_No collection actions due today. AR is current._


---
## FINANCIAL SNAPSHOT — 2026-04-17 06:14

| Metric | Value |
|---|---|
| Net Cash Position | $0.00 |
| Total AR Outstanding | $0.00 |
| Total AP Outstanding | $0.00 |
| Bank Balance | $0.00 |
| Overall Margin | 0.0% |
| 30-Day Cash Forecast | $0.00 |
| 60-Day Cash Forecast | $0.00 |
| High Alerts | 0 |

