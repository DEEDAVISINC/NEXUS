# Scheduled agenda (NEXUS calendar mirror)

**Purpose:** Every time NEXUS creates a `calendars/*.ics` file, the same commitment is recorded here under **the calendar date of the event** (America/Detroit). Good morning / session reads use this so meetings and deadlines appear on the **scheduled day**, not only in Apple Calendar.

**Rules for NEXUS:** See `.cursor/rules/auto-calendar-events.mdc`.

---

## 2026-04-17 — Thursday

- **12:00 PM ET** — 📋 Portal — **Choice Partners (Ionwave)** — Confirm whether **Modular Buildings and Related Items JOC** RFP posted (est. advertise Apr 17 per Upcoming Contracts). `CHOICE_PARTNERS_PIPELINE.md` · https://hcdeebid.ionwave.net

---

## 2026-04-20 — Monday

- **7:00–8:30 PM ET** — 📞 GovCon Masterclass With Chris (Chris Connections) — Zoom: https://us06web.zoom.us/j/5880131794 — `.ics`: `calendars/GOVCON_MASTERCLASS_CHRIS_CONNECTIONS_2026-04-20.ics`

---

## 2026-04-22 — Wednesday

- **(Today)** — ✓ **KY DMS — written questions e‑mailed** — RFP 128 2600000415 — to Robin.Uphoff@ky.gov; agency deadline **4/23 3:30 PM ET**; draft `BIDS:RESOURCES/KENTUCKY DMS MINE DRUG TESTING/WRITTEN_QUESTIONS_DUE_2026-04-23.md` — `.ics` (reminder, submitted early): `calendars/KENTUCKY_DMS_DRUG_TESTING_QUESTIONS_2026-04-23.ics`

---

## 2026-04-23 — Thursday

- *(No KY questions action — **submitted 4/22**; deadline was 4/23.)*
- **3:00–3:30 PM ET** — ✓ 🏛️ **MDHHS Environmental Health Bureau — Partnership meeting (HELD)** — CWC+DDI pitched community navigation + program admin model to Angela Medina (Section Manager, Care Coordination, EHB) + Aimee Surma (EHB). Favorable reception; LHD director intros committed for 6 counties. Brief + one-pager delivered **4/23 7:04 PM ET** to both. Follow-up owed within 2 weeks. See `COMPANY_INFO_MASTER.md` → 🏛️ MDHHS PARTNERSHIP section.

---

## 2026-04-24 — Friday

- **Morning** — 🛠 **SHIELD Airtable — create `nexus_lead_screening` base + 10 tables** (Referrals, Families, Children, Navigators, Service_Activations, Case_Milestones, Contractors, Billing, Outcomes_Reporting, Referral_Source_Accounts). Then set `LEAD_SCREENING_BASE_ID` in `.env` and run `python3 seed_shield_referral_source_accounts.py --apply` to seed 2 MDHHS contacts + 6 LHD placeholders.

---

## 2026-04-30 — Wednesday

- **4:00 PM ET** — 📝 **Notary Signing — Rochester Hills, MI** — Bring notary stamp, journal, ID verification checklist. `.ics`: `calendars/NOTARY_SIGNING_ROCHESTER_HILLS_2026-04-30.ics`

---

## 2026-05-01 — Thursday

- **Due by 5:00 PM ET** — 🔥 **City of Yonkers — Drug & Alcohol Testing RFP-546** — Submit 4 files via BidNet (empirestatebidsystem.com); folder `BIDS:RESOURCES/YONKERS DRUG ALCOHOL TESTING/` — St. John's Riverside confirmed — Corey.Amundson@YonkersNY.gov

---

## 2026-04-28 — Tuesday

- *(CBP Medical Support moved — see May 5 below. Amendment posted 4/22/2026 extended deadline.)*
- 📋 **CMS-855B + Hardship Waiver submission** — Submit CMS-855B initial Medicare enrollment via PECOS with hardship exception letter (saved: `ESSENTIALS/DDI_Medicare_Hardship_Waiver_Letter.docx`). Also: log into CHAMPS (MiLogin: **davisd1221**) and check/add CHW taxonomy (171400000X) to DDI's existing provider enrollment. Pull CHW fee schedule (98960-98962 rates).

---

## 2026-05-05 — Tuesday

- **5:00 PM EDT** — 🔥 **CBP / DHS — Medical Support Services — Phase I due** — **70B06C26R00000017** — Full & Open / NAICS 621399 / $175M ceiling — Two-phase: Phase I = written tech approach + past performance. Phase II = oral + SB plan + price (date TBD after Phase I evaluation). CO: shaungalen.saad@cbp.dhs.gov · CS: peter.a.giambone@cbp.dhs.gov. DDI path = **sub under Acuity-CHS (incumbent)** — drug testing TPA (Tasks 6–7 / Section A, Tasks 4–5 / Section B). Teaming outreach: `BIDS:RESOURCES/DHS CBP MEDICAL SUPPORT SERVICES/TEAMING_OUTREACH/`. Update `.ics` file to reflect new date.

---

## 2026-05-04 — Monday *(MDHHS follow-up target window opens)*

- **Watch item** — 📅 **MDHHS follow-up meeting — CWC+DDI** — Angela Medina + Aimee Surma committed to a formal follow-up within 2 weeks of 4/23. Target schedule: **week of 5/4 (5/4–5/8)**. Deliverable owed: **pilot structure documentation** (10-member demo — lead screening navigation + housing stability, 90-day outcomes framework, selection criteria, roles matrix).
- **ASK at meeting** — 🛡️ **SHIELD vendor sourcing** — Request from Aimee/Angela: "Who are your current contracted vendors for lead abatement, emergency/temp housing, CHW home visits, and nurse home visits in Wayne, Oakland, Macomb, and Genesee counties — and can CWC/DDI be credentialed to coordinate through them?" Also ask about Get Ahead of Lead filter supplier pipeline and any existing MSHDA regional contacts for housing navigation.
- **ASK at meeting** — 💰 **CHW Medicaid reimbursement rates** — Confirm Michigan Medicaid per-unit rate for CPT 98960/98961/98962 (CHW services). DDI needs the exact number to model navigator staffing costs vs. reimbursement. Also ask: what billing provider structure does MDHHS expect for CHW claims — can DDI bill as the Type 2 NPI org with CWC navigators as rendering providers?
- **ASK at meeting** — 🏥 **Provider enrollment for CHW billing** — DDI's current Medicaid taxonomy is Transportation Broker (347E00000X). Ask Aimee/Angela: does DDI need to add a CHW taxonomy (171400000X) to bill 98960-98962? What's the fastest path to get DDI set up as a CHW billing provider in CHAMPS? Also: does MDHHS have guidance on CMS-855B Medicare enrollment for organizations billing CHI codes (G0019/G0022)?
- **ASK at meeting** — 🩺 **Attending physician NPI for CHW claims** — Michigan Medicaid requires an attending provider NPI on every CHW claim (98960-98962 + modifier CG). When a family is referred through MDHHS/LHD for lead follow-up, does the referring physician's NPI travel with the referral? Or does DDI need to establish its own attending provider relationship (e.g., contract with an FQHC or physician)? This is the "MRO equivalent" for care coordination billing.

---

## 2026-05-07 — Thursday

- **Due by 3:30 PM ET** — 🔥 **KY DMS — proposals** — RFP 128 2600000415 — Kentucky VSS (Technical + Cost + Proprietary); folder `BIDS:RESOURCES/KENTUCKY DMS MINE DRUG TESTING/` — `.ics`: `calendars/KENTUCKY_DMS_DRUG_TESTING_PROPOSAL_2026-05-07.ics`
