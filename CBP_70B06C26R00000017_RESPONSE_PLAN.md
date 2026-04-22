# CBP Medical Support Services — Response preparation (70B06C26R00000017)

**Status:** IN PREPARATION — NEXUS kickoff  
**Operating due (Dee):** **2026-04-28, 5:00 PM Eastern** — **confirm in SAM.gov** (authority)  
**Facts / POCs / ceiling:** `CBP_70B06C26R00000017_SOLICITATION_FACTS.md`  
**Working folder (local, not in git):** `BIDS:RESOURCES/DHS CBP MEDICAL SUPPORT SERVICES/`  
**Source package (mirrored — use this for all prep):** `BIDS:RESOURCES/DHS CBP MEDICAL SUPPORT SERVICES/00_SOURCE_PACKAGE/` — full copy of your `~/Downloads/...Medical+Support+Services+for+CBP+.../` folder (SF 1449, SOW, Attachments 1–7, draft Q&A).  
**Downloads original (backup):** same tree under the space-named folder in `~/Downloads/` if you need it.

---

## NEXUS response system + ProposalBio (mandatory)

**No buyer-facing response leaves NEXUS without this pipeline** (see `.cursor/rules/nexus-outbound-workflow.mdc` — NEXUS-SYSTEM-ONLY):

1. **CLASSIFY** — Document type and recipient (here: **Proposal** to CO/CS; government templates in `00_SOURCE_PACKAGE/`).  
2. **BUILD** — Technical/cost/attachment content in the bid folder; any **narrative** the evaluator reads must be NEXUS-generated and solicitation-tuned.  
3. **APPLY ProposalBio** — For proposals: **all 10 biohacks**; per pipeline: **composite ≥ 75**, **no critical failures**, **ProposalBio Gate = UNLOCKED** before “ready to send” (see outbound workflow table).  
4. **VERIFY** — Buyer/supplier protection, company info (`COMPANY_INFO_MASTER.md` / `.cursorrules`), and **Proposal Readiness Gate** (`.cursor/rules/proposal-readiness-gate.mdc`): Strategy Fit, Evaluator Risk, Differentiation, Read Pattern — each **PASS**; **ProposalBio applied = documented**.  
5. **PLACE** — Only **final** PDFs/attachments the CO will receive go in **`SEND_TO_BUYER/`** after the gates above.  
6. **PRESENT** — Package is shown as complete in session (Dee) before email send.

**Government-mandated forms** (e.g. Attachment 4 xlsx, Attachment 2 docx) are **filled** from NEXUS-approved text and numbers; the **controlling** drafts still live in the NEXUS workflow — not a one-off Word session that bypasses ProposalBio for narrative volume.

**Reference:** `PROPOSALBIO_QUICK_START.md`, `NEXUS_COMMAND_REFERENCE.md` (e.g. `POST /gpss/proposalbio/analyze` if using the API). Airtable/GPSS tracking: `PROPOSALBIO_AIRTABLE_SETUP_GUIDE.md` when you log scores to **GPSS ProposalBio Scores**.

---

## How to use this file

- Check off **Phase** items in order.  
- **NEXUS + ProposalBio + readiness gate** (above) govern **every** final artifact to the buyer.  
- **Submission docs** (final, buyer-safe) go only in `SEND_TO_BUYER/`.  
- **Supplier** RFQs, LoC requests, no-buyer-id drafts → `SEND_TO_SUPPLIER/`.  
- **Sub** packages → `SEND_TO_SUBCONTRACTOR/`.  
- Internal analysis, SOW markups, compliance matrix **working** copies → folder root (never email root-only files without review).

---

## Phase 0 — Authority & package (block everything else on this)

- [ ] **SAM.gov** — Open active notice `70B06C26R00000017`. Record: **exact** due date, time, **time zone**, set-aside, NAICS, PSC, and **all amendment numbers** (download PDFs).
- [ ] **Save** new SAM PDFs to `BIDS:RESOURCES/DHS CBP MEDICAL SUPPORT SERVICES/01_SOLICITATION_AMENDMENTS/` and name with amendment IDs. (Baseline RFP **already** mirrored in `00_SOURCE_PACKAGE/`.)
- [ ] If Block 8 in your local `SF 1449` still disagrees with SAM, **replace** local file from SAM — the operating schedule is **SAM + Dee**, not a stale download.
- [ ] **Acknowledgment** — RFP may require **listing addenda in the offer**; add a one-page **Amendment / Addenda Acknowledgment** to the transmittal (template line in Phase 8).

---

## Phase 1 — Eligibility, SAM, and reps

- [ ] **SAM** active, correct UEI, **reps & certs** current for offer date.
- [ ] **HUBZone** — Per downloaded SF 1449; **re-confirm in SAM** (if full-and-open, adjust strategy; do not assume).
- [ ] **WOSB/EDWOSB** — Form shows WOSB program checkboxes; align **actual** certification with offer (no overclaiming).
- [ ] **FAR/DFARS** — Note RFO FAR Part 12 + class deviations referenced on SF 1449; pull required clauses from Section II in the PDF volume and mark **in matrix** (Phase 2).

---

## Phase 2 — SOW / RFP → compliance matrix (core technical work)

**Input:** `00_SOURCE_PACKAGE/2.1.1- ATTACHMENT 1- FINAL SOW_Medical_Services - March 2026.docx` (and any SOW in amended PDFs).

**Deliverable (internal, root folder):** `SOW_COMPLIANCE_MATRIX.xlsx` or `.md` table with at least:

| SOW ref (section) | Requirement (short) | DDI / partner / method | Status | Offer section |
|-------------------|---------------------|--------------------------|--------|---------------|
| (fill) | | | P / G / N | Vol. 1, p. x |

- [ ] **Section A / national coverage** — Map to DDI + **Quest + Concentra** (or approved subs) site coverage; flag gaps and **cure** (partner letter, add site, or explicit exception request if allowed).
- [ ] **Hiring Center / NPD / fitness / drug** — Per SOW, separate threads; who performs each (TPA, collection network, MRO, lab, oral fluid, etc.).
- [ ] **IT / web services / reporting** — SOW is heavy on **data exchange, QA, security**; assign internal owner + **cyber/PII** bullet list for proposal narrative.
- [ ] **Labor / place of performance** — Align with **Attachment 3** (locations) and **Attachment 7** (wage determinations).
- [ ] **Key personnel** — RFP may require **named KPs + alternates**; start a `KEY_PERSONNEL_ROSTER.md` (resumes in `SEND_TO_BUYER/` only when final).

---

## Phase 3 — Subcontracts, LoCs, and proof (no buyer leakage to suppliers per `.cursorrules`)

- [ ] **Quest** — Panel, account, pricing, **Letter of Commitment** or LoC as required by RFP for **federal TPA** use (align with `PARTNER_ACCOUNT_UPDATES` / Abbott-eScreen where relevant).
- [ ] **Concentra** — Occupational health / collections as scoped in SOW; LoC or agreement path.
- [ ] **eScreen** / lab chain — If solicitation names specific platforms, ensure narrative + exhibits match; **do not** paste buyer’s name in supplier drafts (use DDI RFQ id).
- [ ] **MRO / C/TPA** path — If SOW requires MRO, name credential and oversight model.
- [ ] For each partner: internal **SEND_TO_SUBCONTRACTOR** or `SEND_TO_SUPPLIER` package as appropriate; track dates in this checklist.

---

## Phase 4 — Past performance (Attachment 5) and prior experience (Attachment 6)

- [ ] Complete **questionnaires** in government templates; no substitute PDFs unless allowed.
- [ ] **Pick references** that mirror **federal/occupational health/drug/fitness** scale (redact PII; use **CPAR or contact** only as permitted).
- [ ] If weak on **direct** CBP-scale work, use **relevant** agency work and explain **teaming/perf** in narrative (honest, evaluator-defensible).

---

## Phase 5 — Small business (Attachment 2)

- [ ] **SB utilization plan** — Use **their** template; map subs (HUBZone, WOSB, etc.) to **real** firms and workshare; get **signed** sub LOIs where the plan requires.
- [ ] If **no** meaningful sub work, document **good faith** and compliance with plan instructions (per template — do not improvise format).

---

## Phase 6 — Price (Attachment 4)

- [ ] **Use only** `00_SOURCE_PACKAGE/2.1.1- ATTACHMENT 4_CBP Medical Services Price Proposal Template_70B06C26R00000017.xlsx` (or current amendment version).
- [ ] **Trace** every priced line to SOW/schedule; double-check **units**, **FAR 52.212** commercial pricing, and **60-day** validity (per RFP text).
- [ ] **Internal** price build workbook (for margin review) — root folder, not the submitted file, unless you merge deliberately.

---

## Phase 7 — Other attachments and labor

- [ ] **Attachment 3** — Historical / duty locations: confirm **complete** and consistent with narrative.
- [ ] **Attachment 7** — Wage determinations: match **SCLS** / place of performance; narrative where **CBA/union** applies.

---

## Phase 8 — Transmittal and email submission (buyer) — NEXUS only

- [ ] **ProposalBio + Readiness gate** already **PASS** for every narrative/technical volume; composite **≥ 75** and gate **UNLOCKED** (or document explicit waiver in internal notes — default is no send without pass).  
- [ ] **Email** to: **CO + CS** (see fact sheet) — `shaun.g.saad@cbp.dhs.gov` + `peter.j.giambone@cbp.dhs.gov` (verify in SAM).  
- [ ] **Subject line:** `70B06C26R00000017` — (short title) — [DDI / team name]  
- [ ] **Body:** NEXUS-generated transmittal (who, what volumes, # of files, **addenda acknowledged**), request **read-receipt** or **acknowledgment** if acceptable.  
- [ ] **Attach** (per RFP + matrix): final PDFs of **volumes** (tech + business + price + reps) and completed templates — only files copied into **`SEND_TO_BUYER/`** after Phase 9.  
- [ ] **After send:** Get **written confirmation of receipt** from CO/CS; file in `BIDS:RESOURCES/.../PROOF_OF_SUBMISSION/`.

---

## Phase 9 — Final QA (before send)

- [ ] **Readiness gate checklist** (document in folder or GPSS): Strategy Fit, Evaluator Risk, Differentiation, Read Pattern — all **PASS**; **ProposalBio Applied: PASS** (`proposal-readiness-gate.mdc`).  
- [ ] **HUBZone / set-aside** language matches **SAM** notice.  
- [ ] **Solicitation number** and **amendment** list on transmittal.  
- [ ] **Page limits / format** (if any) from Section L/M equivalent in PDFs.  
- [ ] **Two-person read** of executive summary + price cross-check to matrix.  
- [ ] Only then: move **final** attachments into `SEND_TO_BUYER/` and send.

---

## NEXUS / repo pointers

- **Outbound + ProposalBio:** `.cursor/rules/nexus-outbound-workflow.mdc`  
- **Readiness gate + ProposalBio documentation:** `.cursor/rules/proposal-readiness-gate.mdc`  
- `PROPOSALBIO_QUICK_START.md` · `NEXUS_COMMAND_REFERENCE.md`  
- Calendar: `calendars/CBP_MEDICAL_SUPPORT_PROPOSAL.ics`  
- Trackers: `BID_TRACKER_DASHBOARD.md`, `TODAY_AGENDA.md`  
- Contacts: `VENDOR_CLIENT_CONTACTS.md` (CBP block)

---

*Created by NEXUS — response prep kickoff. Update Phase 0 first every time the solicitation is amended.*
