# PENDING ACTIONS — CHECK EVERY SESSION

**Last Updated:** June 12, 2026 (Twilio voice/SMS live · CNAM only remaining)

---

## 🔴 ACTION REQUIRED — PRIORITY

| Task | Details | Status |
|---|---|---|
| **Molina Healthcare of MI — HIDE SNP LTSS contract is EXECUTED** | Vendor ID 214337479, credentialed thru Jul 31, 2029. Fully executed agreement received Jul 22 (Non-Medical Transportation + Community Transition Services). Orientation (Jul 23 @ 10 AM ET) **attended**. | ✅ **DONE** |
| **Molina — Availity Portal registration SUBMITTED (not yet active)** | Registered Jul 23 @ 9:12 AM. **App ID 63821858.** Availity confirmed: "registration is in process" — someone will contact via email in **3-5 business days** with activation status. **Cannot submit claims/check eligibility until activated.** Once active: confirm **NPI 1538939111 is entered** — LTSS orientation deck (Slide 8) warns claims deny for missing NPI on atypical providers. | 🟡 **PENDING — check back ~Jul 28-30** |
| **Molina — LTSS Orientation Training Attestation — HARD GATE** | Per orientation deck (Sarah Fenton, Jul 23): **"You will not receive members until this form has been completed and submitted."** Attestation will be emailed after orientation — sign and return to `MHMLTSSContracting@MolinaHealthCare.Com` **immediately**. Nothing else matters (scope, rates, Availity) until this is done. | 🔴 **URGENT — check inbox tonight** |
| **Molina — corrected contact routing (do NOT email Arielle for referrals)** | Per orientation: referrals are 100% member/Care-Coordinator-initiated — DDI cannot solicit or ask to be "added to a list." Contact for auth questions going forward = **LTSS Specialist** (MHM-LTSS-Specialist@MolinaHealthCare.Com), NOT Care Coordinators directly, NOT Arielle (contracting is closed out). Never request PA via Availity — fax only. Check member eligibility before every service (Availity or 855-322-4077). | ✅ **NOTED — routing corrected** |
| **Molina — first payment defaults to virtual credit card (ECHO)** | Watch for ECHO "Quick Remit" email. If direct deposit preferred, need the **Draft Number** off first Explanation of Provider Payments (EPP) to register — instructions were attached to orientation invite. | ⬜ **TODO once first claim pays** |
| **Molina — PRISM/VERTEX is code-ready** | `nemt_billing.py` now has full Molina LTSS payer config: contract rates (T2003 $27, A0130 $35, mileage S0215 $0.67/mi, S0209 $3.00/mi, T2038 Community Transition manual + T1028 $150 assessment), payer auto-detection, and a **hard-gate eligibility check** that blocks dispatch until both gates below clear. QC profile + ops doc: `BIDS:RESOURCES/MOLINA HIDE SNP LTSS NETWORK/QC_CONTRACT_PROFILE.md`, `MOLINA_HIDE_SNP_OPERATIONS.md`. | ✅ **DONE — code ready, gated on 2 flags below** |
| **Molina — flip the 2 hard-gate flags once cleared** | In `nemt_billing.py`: `MOLINA_LTSS_ATTESTATION_ON_FILE = False` and `MOLINA_LTSS_AVAILITY_ACTIVE = False`. Flip each to `True` only when (1) attestation is signed & returned and (2) Availity is active with NPI 1538939111 confirmed. PRISM will not let a Molina trip pass eligibility check until both are `True` — this is intentional, not a bug. | ⬜ **WAITING on attestation + Availity above** |
| ~~**Molina — verify Non-Medical Transportation is in final scope**~~ | ✅ **CONFIRMED Jul 23** — Attachment B (Statement of Work), page 15 of 25, Service Types checklist: both **☒ Non-Medical Transportation** and **☒ Community Transition Services** are checked. The Jul 8 portal glitch did not carry through to the executed agreement. | ✅ **DONE** |
| **Molina — build revenue model from fee schedule** | Fee schedule for Non-Medical Transportation + Community Transition Services was sent Jul 8 as an attachment. Needs to be pulled and run through DDI's margin model (boutique/select cohort framing, not volume) so PIPELINE_TALLY.md numbers are real, not placeholders. | ⬜ **TODO** |
| **Molina — confirm added to in-network provider directory** | Arielle confirmed (Jul 17) referrals are member-choice driven through Care Coordinators, and DDI is added to the internal provider list "once fully contracted." Contract is now executed — confirm DDI is live in that directory so Care Coordinators can actually route members. | ⬜ **TODO — follow up with Arielle** |
|---|---|---|
| **HAP CareSource — Brian Grcevich call** | **Wed Jun 10 @ 1:00 PM ET** — Non-medical waiver trips via CM service plan → DDI (Vendor 100000469269). Medical stays **MTM**. Prep: `HAP CARESOURCE NEMT NETWORK/BRIAN_ROUTING_CALL_PREP_2026-06-08.md` · Brian **317-296-0519** | 🟢 **CONFIRMED** |
| **MICH HIDE SNP — 8 MCO emails** | ✅ **Gmail scheduled Fri Jun 12 @ 7:04 PM ET** → delivers **Mon Jun 15, 8:00–9:45 AM ET**. Logged `OUTBOUND_EMAIL_LOG.md`. **Mon AM:** confirm Sent folder + flip log to SENT. **Follow-up Wed Jun 24 @ 12 PM ET** — non-responders only. **Do NOT send HAP.** | ✅ **QUEUED** |
| **FMCSA Clearinghouse — identity verification** | **Deadline Jul 6, 2026.** DDI = **C/TPA** — must complete or **lose Clearinghouse access.** Steps: (1) https://clearinghouse.fmcsa.dot.gov → Log in (2) **My Dashboard → My Profile** (3) Click **Begin Identity Verification** (4) Follow prompts · Ref: `COMPLIANCE_KNOWLEDGE/CLEARINGHOUSE_IDENTITY_VERIFICATION.md` · Phone 844-955-0207 · **Not on calendar until Dee approves** | ⬜ **URGENT — do this week** |
| **MDHHS SHIELD follow-up (Angela Medina + Aimee Surma)** | **May 30 follow-up SENT**. **Trigger Jun 16:** if silent → direct LHD wave. **Emails READY:** `CLIENT OUTREACH/LHD_DIRECT_OUTREACH_JUN_2026/SEND_TO_LHD/` · **Attach:** `DDI_CWC_PHC_Program_Narrative.pdf` · Call Angela **517-897-5203** optional before send | 🟡 **AWAITING — LHD PACKAGE READY** |
| **Jun 4 — LHD director verification** | LinkedIn verify: Guzmán, Willette, Corsi, London, Moore. Call Macomb/Genesee/Kent to confirm emails. | ⬜ **TODAY** |
| **Blue Cross Complete — Alina Pabin intro call** | **May 30 follow-up SENT** — no reply. **Final touch Thu Jun 11 @ 2:30 PM** — HAP **replied Jun 7** (two-lane routing); Alina touch can proceed on schedule. Prep: `BCBSM NEMT PARTNERSHIP/ALINA_MEETING_TALK_TRACK.md` | 🟡 **THU 6/11** |
| **MHEF Capacity Building concept paper** | Inquiry done · Sayre replied Mar 27 — **submit in Fluxx** | ⬜ **$300K track** — see `MICHIGAN_FUNDER_MAP.md` |
| **BCBSM Foundation concept paper** | **Winter cycle — return end Sept 2026.** Begin build **Sep 30** · Submit **Oct 29, 2026**. Summer cycle skipped. Outline: `GRANT_APPLICATION_PACKAGE/CWC_GRANTS/BCBSM_FOUNDATION_CONCEPT_PAPER_OUTLINE.md` · Form: forms.office.com/r/wZdDebmJf9 | 🟡 **SCHEDULED — SEP/OCT** |
| **RENEW SCAC CODE (DFCL)** | **EXPIRED Feb 3, 2026.** Go to https://scaccode.com — renew for $97. If can't renew lapsed code, call NMFTA (866) 411-6632. Update company name from DEPOINTE → DEE DAVIS INC and address to Troy. **This is the single blocker for USPS HCR routes.** | ⬜ URGENT |
| **Register on USPS Logistics Gateway** | After SCAC renewal → https://logistics.usps.com/ — register with DFCL code. This is the portal for Highway Contract Routes (DDI's current eSourcing registration is for small deliveries only). | ⬜ BLOCKED (needs SCAC) |
| **Add freight NAICS to SAM.gov** | DDI needs ALL freight lanes visible: **484110** (local), **484121** (long-distance TL), **484122** (LTL), **484220** (specialized long-distance — heavy haul, tanker), **484230** (specialized — auto transport). DDI already has 484210 + 488510. Without these 5, DDI is invisible to reefer, flatbed, heavy haul, auto transport, and tanker contract searches. Log into SAM.gov → Edit Registration → NAICS Codes → Add all five. | ⬜ TODO |
| ~~**University Health — Isabelle bid table email**~~ | ✅ **SENT May 29, 2026** — per-mile rates to Isabelle.Vallejo@uhtx.com | ✅ DONE |
| **3D INK WAVE 1 + 1B — SEND OUTREACH** | **41 emails READY. Fri May 29 @ 5:00 PM ET — Session 1 (10 sends).** | 🟡 **5 PM ET** |
| **Electron — Uber Health login in PRISM webview** | Fix pushed Jun 5: Chrome UA + OAuth popup modal + `persist:partner` session. **Test:** quit Electron fully → `npm run electron-dev` → PRISM → NEMT → Live Portals → Uber Health → sign in. Use **Browser ↗** if popup still fails. | ⬜ **TEST after restart**
| **Email SouthStar (Jon/Luis)** | Ask about service contract financing (not just PO) for HAP contract | ⬜ TODO |
| **CareSource Ohio (Kristen Halsey)** | 7-day follow-up due TODAY | ⬜ TODO |
| ~~**Jun 7 Sun @ 12 PM ET**~~ | ~~PRISM Finish-Up~~ | ✅ Voice + QC live on PA |
| **HAP CareSource — walkthrough prep** | **DEFERRED** until input→invoice wired — see `HAP_NEMT_PIPELINE_COMPLETION_GATE.md` · If they ask early, send one-pager only | ⏸ **AFTER PIPELINE** |
| **HAP NEMT — Mark Complete → VERTEX + QC gate** | `TPADivisionWorkspace.tsx` → `POST /prism/nemt/orders/<id>/complete` + `nexus_qc_engine` | ✅ Wired — `auto_generate_claim: true`, QC record returned |
| **HAP Voice Intake (855-773-0035)** | Twilio inbound → PRISM order + NEMT queue · member SMS · PA live | ✅ **LIVE** — tested |
| **HAP 855 — Caller ID (CNAM)** | Register **DDI** display on outbound from **855-773-0035** (Twilio Trust Hub / toll-free CNAM) | ⬜ **ONLY REMAINING** telephony item · `deploy/PRISM_VOICE_INTAKE.md` |
| **FEMA STOS (freight TSP)** | **MOB-C / Freight 1st Direct** — FTL, LTL, maritime, air, rail, TTHU. **Onboarding currently CLOSED** (per FEMA site). Monitor next open period · file rates in Rate Filing Cycle when eligible. **Not passenger or NEMT.** Contact: FEMA-Transportation-Programs@fema.dhs.gov | ⏸ **Monitor** — not HAVEN blocker |

### SHIELD pilot launch gaps (`SHIELD_PROGRAM_COMPLETE_FRAMEWORK.md`)

| Gap | Action | Status |
|-----|--------|--------|
| Quest/CRL BLL wholesale rate | Confirm before volume agreements | ⬜ |
| Michigan mobile phlebotomist subs | 2–3 Detroit-area quotes for pediatric lead events | ⬜ |
| CHAMPS 98960 under 6309049 | Verify active for MCO CHW billing | ⬜ |
| Venous premium on rate card | +$125–$175 confirmatory upcharge | ⬜ |
| FEMA TSP registration | Before hurricane season (HAVEN logistics) | ⬜ |
| LHD referral channel | ≥1 county health dept active pre-launch | 🟡 LHD package ready Jun 16 |
| MCIR portal access | Verify DDI can log BLL results directly | ⬜ |

## ⏳ AWAITING RESPONSE

| Contact | Company | Notes |
|---|---|---|
| Daniel Rivera | Anthem Ohio | Awaiting response — will reply when he does |
| ~~Uber Health~~ | ~~Uber Health (AE assignment)~~ | **✅ RESOLVED May 15** — Jeff Metz (AE) + Chris McNally assigned. Dashboard LIVE. Bexar + MI = A Tier. |
| **FL Medicaid** | Gainwell Technologies | Tracking #218601133 — TPA/broker enrollment question (no auto insurance). Expect response by **May 22** |
| **Labcorp Employer Services** | Labcorp | TPA account inquiry submitted May 19 via web form — awaiting rep assignment. Need: wholesale pricing, collection site network, eCCF access |
| **Humana Ohio D-SNP** | Humana (Denise — Provider Relations) | May 19 — Misrouted to provider relations. Redirected to Vendor Management/Procurement for TPA partnership (NEMT, Personal Care, DME, HAVEN). Awaiting correct contact routing. |
| **Louisiana OGB** | Liam Thomas (State Procurement Analyst, liam.thomas@la.gov) | May 19 — Emailed re: TPA services DDI can offer for MA HMO supplemental benefit admin (NEMT, Personal Care, DME, HAVEN). Doc2052093019. Awaiting response. |

---

## 📞 PARTNER ONBOARDING — SCHEDULE

| Partner | Task | Questions to Ask | Status |
|---|---|---|---|
| **Lyft Healthcare** | Schedule AE sales call | 1) When is Lyft Assisted coming to MI? 2) Medicaid approval timeline for MI? 3) Healthcare broker program available? | ⬜ TODO |

## ⚠️ CRITICAL FIX NEEDED

**70+ emails sent with incomplete service list.** Future emails MUST include:
- NEMT TPA
- Personal Care TPA  
- DME (Durable Medical Equipment)
- HAVEN (disaster transport, emergency pharmacy delivery, temporary housing)

All pending MCO emails need audit before sending.

---

## 📧 MCO OUTREACH — READY TO SEND

| State | Emails Ready | File Location |
|---|---|---|
| Louisiana | 4 emails | `CLIENT OUTREACH/LOUISIANA MCO NEMT HAVEN/` |
| Ohio | 3 emails (CareSource, Molina, Humana) | `CLIENT OUTREACH/OHIO MCO NEMT HAVEN/` |
| Texas | 5 emails (Superior, UHC, Aetna, Amerigroup, BCBS) | `CLIENT OUTREACH/TEXAS MCO NEMT HAVEN/` |
| Mississippi | 3 emails | `CLIENT OUTREACH/MISSISSIPPI MCO NEMT HAVEN/` |
| South Carolina | 2 emails | `CLIENT OUTREACH/SOUTH CAROLINA MCO NEMT HAVEN/` |

---

## 📋 PORTAL/ENROLLMENT TASKS

| Task | Portal | Status |
|---|---|---|
| Add commodity code **9S301** (NEMT) | Michigan SIGMA VSS | ⬜ **TODO — blocks auto-alert on recompete** |
| **Maine VSS — Substitute W-9** | mevss.hostams.com | ⬜ Mail/fax per portal · Account active **Jun 15** — VS0000032746 / DEEDAVISINC |
| **Texas TMHP — IAMOnline activate** | tmhp.com | ⬜ Activate link within **7 days** (email Jun 15) · User **DEEDAVISINC** · enrollment txn **D19273048** |
| Florida Medicaid enrollment | FMMIS | ⏳ Question submitted #218601133 — awaiting guidance on TPA/broker enrollment |
| Ohio Medicaid enrollment | ODM PNM/MITS | ⬜ Weekend |
| Texas Medicaid enrollment | TMHP | ⬜ Weekend |
| Molina Ohio portal submission | Provider Contracting Guide | ⬜ Weekend |
| **Maryland eMMA registration** | emma.maryland.gov | ⬜ TODO — missed NEMT RFP (BPM056475) May 14. Complete to catch future MD opportunities. |

---

## 🚐 NEMT STATE ENROLLMENT — TPA MODEL

| State | Task | Portal/Path | Deadline | Status |
|---|---|---|---|---|
| **Texas** | HHSC NEMT Open Enrollment (HHS0016482) | TMHP + TX SOS | **Sept 15, 2026** | ⬜ TODO — TPA prime, sub to Uber Health |
| **North Carolina** | NC SOS Registration | ncsos.gov | Target: June 2026 | ⬜ TODO — **RADAR explore:** `RADAR HEALTHCARE MCO/NC_MEDICAID_EXPLORATION.md` |
| **North Carolina** | NCTracks Enrollment (Transportation Broker 347E00000X) | nctracks.nc.gov | Target: June 2026 | ⬜ TODO — after SOS |
| **North Carolina** | MCO Outreach (AmeriHealth, Carolina Complete, Healthy Blue, UHC, Alliance, Partners, Trillium, Vaya) | Direct contact | Ongoing | ⬜ TODO — after NCTracks |
| **Arizona** | MCO Outreach (Mercy Care, UHC AZ, Banner-University, Arizona Complete Health) | Direct contact | Ongoing | ⬜ TODO — **RADAR explore:** `RADAR HEALTHCARE MCO/AZ_AHCCCS_EXPLORATION.md` |
| **Maine** | MaineCare NET recompete follow-up (Penquis + Waldo CAP) | mevss.hostams.com | **Jun 17, 2026** | ⬜ Follow-up — `CLIENT OUTREACH/MAINE NEMT TEAMING/` · Opp 0520260310 · **VSS active Jun 15** — VS0000032746 / DEEDAVISINC |

---

## 📞 CALLS SCHEDULED

| Date | Time | Who | Prep File |
|---|---|---|---|
| Wed May 13 | 1:30 PM ET | Uber Health — Ariana Cirkelis | `HAVEN/OUTREACH/UBER_HEALTH_CALL_PREP_MAY13.md` |
| Wed May 14 | TBD | Metro One SC — Michelle Ebert | `HAVEN/OUTREACH/METRO_ONE_SC_CALL_PREP_MAY14.md` |

---

## 📬 RESPONSES RECEIVED — LOGGED

| Date | From | Company | Result |
|---|---|---|---|
| May 12 | Sarah Oumedian | Michigan DHHS | No timeline yet — add 9S3 to SIGMA |
| May 12 | Rick Johnson | Buckeye Ohio | ❌ Declined — referred to Natalie Lukaszewicz |
| May 12 | Sandra Salas | Molina Texas | ❌ Declined — services in-house |
| May 12 | Natalie Lukaszewicz | Centene Corporate | ✅ SENT (VP referral from Rick) |
| May 11 | Stephanie Logan | Alabama Medicaid NEMT | **First email sent 7:53 PM ET** |
| Jun 1 | Jason Giombetti | Elder Services of Worcester Area | **Next cycle ~2029** — LOI May 22 was hard deadline (not a no); next transport RFP in ~3 years; Dee thanked — **re-outreach when next RFP opens** |
| Jun 1 | Beth Rubin (win) | Greene County CDJFS OH | **ON RFP NOTIFICATION LIST** — will notify for next NEMT RFP; Dee thanked — thread closed |

---

## ⏳ FOLLOW-UP CADENCE

| Contact | Company | Last Contact | Next Follow-Up |
|---|---|---|---|
| Bennett Emfinger | Alabama Medicaid NET | May 12 | ~~Jun 9~~ **CANCELLED** — Bennett replied 6/4 (internal review); **HOLD until ~Jun 18–25** · `ALABAMA_MEDICAID_NET_THREAD.md` |
| Natasha Crusoe | Alabama Medicaid NET | — | **Net-new** — per Stephanie OOO routing May 31 |
| Stephanie Logan | Alabama Medicaid NEMT Director | **May 11 @ 7:53 PM ET** | **Jun 3** — after OOO return Jun 2 · **no re-send from queue** |
| Kristen Halsey | CareSource Ohio | May 13 | May 20 (7 days) — SENT full service pitch |
| Natalie Lukaszewicz | Buckeye Health Plan / Centene | May 13 | Mid-July 2026 (Q3) — "network closed, reach out later this year" |

---

## 🔬 FORENSIC KIT DISTRIBUTOR RELATIONSHIP — NEW CONTRACT LANE

**Target: Mid-June 2026**

DDI should become an authorized distributor for forensic evidence collection kits (sexual assault kits, DNA collection kits, gunshot residue kits, toxicology kits). Every state police agency and crime lab in the country buys these on recurring 3-5 year contracts. EDWOSB set-asides apply.

| Company | Location | Phone | Contact | Priority |
|---|---|---|---|---|
| **Tri-Tech Forensics** | Leland, NC | 800-438-7884 | TBD | **#1 — largest, 40+ years, custom kit mfg, supplies GA/VA/TX** |
| **Sirchie Acquisition Co.** | Youngsville, NC | 800-356-7311 | Dan O'Neil (danoneil@sirchie.com) | #2 — IL State Police 5-yr blanket, TX DPS |
| **Lynn Peavey Company** | Omaha, NE | TBD | TBD | #3 — forensic supplies, TX approved vendor |
| **Arrowhead Forensics** | Lenexa, KS | TBD | TBD | #4 — blood/DNA kits, state contracts |

**The play:** Distributor/reseller agreement → DDI buys at wholesale, wins state contracts using EDWOSB, handles distribution and contract management. Pairs with existing forensic division (Lakota fingerprinting, DDC DNA, Quest drug testing).

**Source:** Indiana State Police NB 26-87598 (DNA Collection Kits) — DDI passed on this bid but identified the supply chain.

| Task | Status |
|---|---|
| Research Tri-Tech distributor/reseller program | ⬜ Mid-June |
| Draft outreach email to Tri-Tech | ⬜ Mid-June |
| Contact Sirchie (Dan O'Neil) re: distributor terms | ⬜ Mid-June |
| Search USASpending for EDWOSB forensic kit awards | ⬜ Mid-June |
| Identify which state contracts are recompeting 2026-2027 | ⬜ Mid-June |

---

## 🧪 DRUG TESTING C/TPA — BUILD COLLECTION NETWORK

**Strategy doc:** `NEXUS_LEARNING/DDI_DRUG_TESTING_CTPA_STRATEGY.md`

| Task | Priority | Status |
|---|---|---|
| Contact eScreen for C/TPA partner pricing | Medium | ⬜ TODO — National network for overflow |
| Contact On-Time Screening for fleet event pricing | Medium | ⬜ TODO — Trucking collective events |
| Contact 24/7 Onsite for mobile dispatch pricing | Medium | ⬜ TODO — Urgent/post-accident |
| Draft 1099 Collector Agreement | High | ⬜ TODO — For local collectors |
| Draft Collection Company Subcontract Agreement | High | ⬜ TODO — For sub collection companies |
| Post collector job listing (MI, TX) | Medium | ⬜ TODO — Recruit local 1099 |
| Identify small collection companies in metro Detroit | Medium | ⬜ TODO — Sub for mobile |
| Build prospect list from FMCSA SAFER | Medium | ⬜ TODO — Target 50-200 driver fleets |
| **Complete NCS training** | **⚠️ June 3** | ⬜ TODO — Background + drug portal |

---

---

## 📅 KEY DATES — PROGRAM / FUNDER (May 30, 2026 session)

**Full outreach calendar:** `calendars/CWC_DDI_OUTREACH_FOLLOWUP_CALENDAR.md` · **Import all:** `calendars/CWC_DDI_OUTREACH_FOLLOWUP_JUN_JUL_2026.ics`

| Date | Item | Source |
|------|------|--------|
| **Jun 2** | Check BCC + MDHHS inbox (no follow-ups) | `.ics` inbox check |
| **Jun 11** | BCC final follow-up if no response (postponed from 6/9 — after HAP reply) | `cwc_outreach_bcc_final_followup_2026-06-11.ics` |
| **Mid-June / Jun 16** | MDHHS trigger → direct LHD outreach | `LHD_BACKUP_CONTACTS_SIX_COUNTIES.md` |
| **Sep 30, 2026** | Begin BCBSM Foundation concept paper (Winter cycle) | `SESSION_SUMMARY_JUNE_4_2026.md` §12 |
| **Oct 29, 2026** | Submit BCBSM Foundation concept paper | Winter cycle deadline |
| **Sept 2026** | CDC CLPPP cooperative agreement cycle end | `MULTI_STATE_LANDSCAPE_RESEARCH.md` |
| **Nov 18, 2026** | BCBSM Foundation board review #2 | `MICHIGAN_FUNDER_MAP.md` |
| **1st Mon monthly** | EGrAMS + county opioid + CFSEM + MHEF monitor | Jul 6, Aug 3, Sep 7… |
| **Sep 14, 2026 @ 12 PM ET** | **CCAM-TAC quarterly scan (Tier C)** — `python3 nexus_scheduler.py --ccam-tac` + skim Partner/External in `CCAM_FTA_COORDINATION_INTEL.md` · `.ics`: `CCAM_TAC_QUARTERLY_CHECK.ics` | Quarterly (Dec 14, Mar 14, Jun 14, Sep 14…) |

### Monitoring tiers (CCAM / grants — Jun 14, 2026)

| Tier | Cadence | What |
|------|---------|------|
| **A — weekly** | RADAR / bid tracker / MCO Medicaid / SIGMA 9S3 (ModivCare) | Automated + manual deadline pass |
| **B — monthly** | CWC grant pipeline | 1st Mon monthly row above |
| **C — quarterly** | CCAM-TAC Partner + External + Community Rides + ICAM watch | Miner + 15-min human skim · **no CCAM email outreach** |

**Full session:** `SESSION_SUMMARY_MAY_30_2026.md`

---

## 🌐 DDI WEBSITE UPDATE — deedavis.biz (not NEXUS app)

**Tracker:** `WEBSITE/DEEDAVIS_BIZ_WEBSITE_UPDATE_TRACKER.md` — when Dee says **"DDI website update"** or **"update the website,"** read that file.

| Priority | Task | Status |
|----------|------|--------|
| **P0** | Deploy `WEBSITE/cwc-proof/` → **deedavis.biz/cwc-proof** (funder pitch QR) | ⬜ 404 today · `CWC_PROOF_NETLIFY_HOSTING.md` |
| **P1** | Netlify batch deploy — VITAL, HAVEN, ARENA, 3D Ink hub + rate sheet (full `WEBSITE/` folder) | ⬜ Staged, not live |
| **P1** | Homepage cleanup on Netlify — national TPA copy, sector cards, nav, **remove SWFT** | ⬜ `DEEDAVIS_WEBSITE_NATIONAL_TPA_COPY.md` |
| **P2** | Add NCS partner link on deedavis.biz → deedavisinc.nationalcrimesearch.com | ⬜ `NATIONAL_CRIME_SEARCH_PARTNERSHIP_SUMMARY.md` |
| **P3** | `/vendors` public RFQ board | ⬜ Design only — not built |

---

## 🔮 FUTURE TODO — NOT ACTIVE YET

| Item | Details | Trigger / When |
|---|---|---|
| **MICH HIDE SNP — NEMT market size by plan** | Back into **NEMT-only** revenue by MCO after Jun 15 sends land. Source: `MICH_HIDE_SNP_STATE_MCO_AWARDS.md` | When Dee says go |
| **NY lead screening — Onondaga County CLPPP+ wedge** | NYS DOH runs CLPPP+ (20 counties incl. **Onondaga/Syracuse**). No MI-style MDHHS referral path — entry is **county LHD + CBO partner**, optionally **NYHER SCN** (HRSN, children under 6). Position **CWC navigates + DDI administers** same SHIELD model — complement county programs, not state cold pitch. Research: Onondaga County lead program contact → complement outreach. **Separate from SUNY courier bid.** Ref: conversation May 31, 2026; NYS DOH [lead programs](https://www.health.ny.gov/environmental/lead/programs_plans/index.htm) | After MDHHS SHIELD path clearer **or** if Syracuse/Onondaga relationship develops via SUNY/other NY work. Target: **Q3 2026** research pass |

---

**RULE:** At the start of every session, read this file and present any overdue or pending items FIRST before asking "what do you want to work on?"
