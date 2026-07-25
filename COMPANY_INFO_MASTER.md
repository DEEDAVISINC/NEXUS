# 📞 DEE DAVIS INC - MASTER COMPANY INFORMATION
## Always Use These Details for Future Documents

**Last Updated:** June 14, 2026

---

## 🏢 COMPANY INFORMATION

**Legal Name:** Dee Davis Inc.  
**DBA:** The Professionals' Professionals

**Address:**
755 W. Big Beaver Rd., Suite 2020  
Troy, Michigan 48084

### PHONE NUMBERS — WHERE EACH NUMBER GOES (Jun 2026)

| Use | Number | Notes |
|-----|--------|--------|
| **President & CEO personal cell** | **248.376.4550** | Email signatures, bids, caps, CO outreach — **Dee’s personal line**; **not** on web; **do not** forward to Twilio |
| **Websites & public web** | **855.773.0035** | Portal, deedavis.biz, all HTML — **never** 248.376.4550 on web |
| **Google Voice (Troy)** | **248.270.8490** | **Forward all calls to +1 855-773-0035** (Twilio → PRISM voice) |
| **Twilio member care** | **855.773.0035** | Voice inbound, SMS, member materials — webhook target for GV forward |

**Email:** info@deedavis.biz — pair with **248.376.4550** on signatures (CEO personal — not changed).

**Routing setup:** `deploy/PHONE_ROUTING_TWILIO.md`  
**Website:** deedavis.biz  
**Website copy (national TPA — all sectors):** `ESSENTIALS/DEEDAVIS_WEBSITE_NATIONAL_TPA_COPY.md`  
**Website deploy backlog ("DDI website update"):** `WEBSITE/DEEDAVIS_BIZ_WEBSITE_UPDATE_TRACKER.md`  
**Scope on all pages:** Nationwide contract management TPA — 50 states + DC. Troy, MI = headquarters only.

### MICHIGAN MILOGIN ACCOUNTS (Dieasha D. Davis — 3 profiles)

Use the **correct MiLogin** per system — do not mix them up.

| # | Label (how to remember) | User ID | Purpose |
|---|-------------------------|---------|---------|
| **1** | **MDHHS COMMUNITY PARTNER MILOGIN** | `davisd1221` | **MDHHS Community Partners** — MIBridges / Navigator / LPOC for Dee Davis Inc. & Cause We Care. Portal after MiLogin: Community Partners. Reactivated Mar 2026. |
| **2** | *(fill in)* | *(fill in)* | *(e.g. personal, other state program — you name it)* |
| **3** | *(fill in)* | *(fill in)* | *(e.g. CHAMPS, employer, other — you name it)* |

**Passwords are not stored in this file.** Keep them in your password manager with the **same labels** as column 2 (e.g. “MDHHS Community Partner MiLogin”). Optional local file (not in git): `MILOGIN_ACCOUNTS.local.md` in the project root.

---

### EMAIL ROUTING

- **Standard:** info@deedavis.biz (ImprovMX forwarding)
- **Federal / DOD / .mil:** bids.deedavisinc@gmail.com  
  **Note:** ImprovMX has .mil delivery limitation — always use the Gmail address for military and DOD contacts.
- **NEXUS outbound bids:** bids.deedavisinc@gmail.com
- **Legal / compliance intake:** gc@deedavis.biz — subcontractor NDAs & non-competes, COI/insurance submissions, grievance & incident reports, buyer audit requests, HIPAA/BAA correspondence, regulatory correspondence (FMCSA Clearinghouse, SAMHSA, state licensing), disputes. Reads as "General Counsel" shorthand — do **not** use "legal@" (invites demand-letter fishing; implies in-house counsel that doesn't exist).
- **Quality control intake:** qc@deedavis.biz — PRISM/VERTEX/COMPASS/GPSS inspection results, sub performance issues, deliverable QA, QC_CONTRACT_PROFILE-related correspondence.
- **Accounts Payable/Receivable intake:** apar@deedavis.biz — invoices, remittance, payment status, VERTEX billing correspondence.
- **Setup:** gc@, qc@, and apar@ are ImprovMX aliases on the deedavis.biz domain (same mechanism as info@). **Confirmed live via ImprovMX API (Jul 2026):** all three forward to **ops.ddinc@gmail.com** ("OPERATIONS DDI"). `IMPROVMX_API_KEY` is stored in `.env` — use it for any future alias changes (`PUT https://api.improvmx.com/v3/domains/deedavis.biz/aliases/{id}` with JSON body `{"forward": "..."}`, Basic Auth `api:{key}`; form-encoded bodies return 400, must be JSON).
- **Note:** a pre-existing `compliance@deedavis.biz` alias exists on the domain (created before gc/qc/apar). **Dee confirmed (Jul 2026): leave it as-is** — forwards to bids.deedavisinc@gmail.com, not touched, not reconciled with gc/qc/apar. Do not "fix" this in a future session.
- **ops.ddinc@gmail.com confirmed live** (Jul 2026) — inbox exists, forwarding chain verified working end to end.
- **Employee/contractor aliases (GATEWAY, Jul 2026):** eligible hires get `firstname.lastname@deedavis.biz` auto-provisioned via ImprovMX (collision-safe, forwards to their personal email on file — GATEWAY sign-in always stays on the personal email). Eligibility is role-based, NOT everyone — controlled by the **'NEXUS HR ROLE EMAIL POLICY' Airtable table** (edit directly in Airtable or via `GET/POST /nexus/hr/role-email-policy` — no code change needed). Timing: NOT at hire — deferred until credentialing clears (`/can-work` gate passes). On offboarding (archive), the alias redirects to **gc@deedavis.biz** instead of being deleted. See `hr_onboarding_api.py` docstring for full mechanics.
- **Employee/Vendor Numbers (GATEWAY, Jul 2026, finalized after 4 rounds of Dee feedback):** every hire gets a personnel number the moment onboarding starts, format **`[SEQ]-[YYMM]-[EMP|VEN]-[LEVEL]-[DIVISION][ACCOUNT EMOJI]`** — e.g. `0001-2607-EMP-AGT-DPTE🩵` = 1st hire that month/type, July 2026, W-2 employee, Agent level, DEPOINTE division, Molina account (🩵). No `DDI-` prefix (redundant — everything here is DDI, per Dee).
  - **Split into two parts, on purpose:** the **core** (`0001-2607-EMP` — sequence + hire month + worker type) is generated ONCE and **never changes again for that person's entire tenure**, no matter how many times they transfer or get promoted. The **suffix** (`AGT-DPTE🩵` — current level/division text + account color emoji) is **mutable** and rebuilds via `PUT /nexus/hr/onboarding/<id>/assignment` any time someone changes accounts, divisions, or gets promoted — every rebuild is logged in the append-only audit trail (old number -> new number), so nothing about assignment history is ever lost even though the visible number changes.
  - **Account is a color emoji, not a text code** — per Dee: *"remove the segement hap molina etc and replace at the end of the number by 🟠, 🟢, 🩵, 🔵, etc, i couldnt find a teal circle, thats why i used the heart."* Current palette (**'NEXUS HR ACCOUNT CODES'** Airtable table, `EMOJI` column): CareSource (= HAP CareSource, Michigan — one account, per Dee: *"caresource is hap, its orange"*) = 🟠, Molina Healthcare of Michigan = 🩵 (heart, standing in for teal), Humana = 🟢, Blue Cross Complete (Dee's shorthand "BCBSM") = 🔵. Meridian and General have no emoji assigned yet — flag colors for those if wanted. **No emoji appended at all** if the account is blank or has none assigned — never invents a color. Text `ACCOUNT_CODE` values (CSRC, MOLN, HUMN, etc.) still exist in that table for internal search/filtering — they just no longer appear in the personnel number itself.
  - **Humana, Blue Cross Complete (BCBSM), and Meridian are active relationships (confirmed by Dee, Jul 2026):** Humana = credentialing in progress; Blue Cross Complete = awaiting Alina Pabin's follow-up (she's the tracked entity Dee's "BCBSM" shorthand maps to); Meridian = DDI is waiting on Meridian to offer the contract opportunity. All three reflected in the `NEXUS HR ACCOUNT CODES` Airtable table `STATUS` field with these real statuses — not "not yet engaged."
  - Segment order was flipped per Dee, after being asked "what happens if they move to a different department or add responsibilities": *"the order of the segments are wrong, they should be the total opposite, therefore the ending can change or be added to."* Original order was `[DIVISION]-[ACCOUNT]-[LEVEL]-[EMP|VEN]-[YYMM]-[SEQ]` — flipped so the permanent part comes first and the part that changes over time is the tail end.
  - `EMP` = W-2 employee, `VEN` = 1099 contractor ("vendor number," Dee's terminology). `LEVEL` (seniority tier — **'NEXUS HR LEVEL CODES'** Airtable table, e.g. Agent=AGT, Supervisor=SUP, Manager=MGR, Director=DIR) edits live via `GET/POST /nexus/hr/level-codes`; account emoji edits live via `GET/POST /nexus/hr/account-codes` — no code change needed for either. Blank/unmatched level falls back to `STF` — never fabricated.
  - Answers all of Dee's questions in sequence: "how do i know that a customer care agent is working in the HAP account, or the MOLINA account... or if they are a manager, supervisor etc" (level is text, account is the color emoji) -> "what happens when they move to a different department" (only the suffix rebuilds — the permanent core, and every invoice/timesheet/CPARS doc that ever referenced it, still traces to the same person) -> "the ending can change or be added to" (mutable assignment moved to the very end) -> "replace ... by [emoji]" (account is now a color glyph, not a text code).
- **Pending decision:** pm@deedavis.biz (contract/program management — COMPASS deliverables, CO reporting) and hipaa@deedavis.biz (HIPAA Privacy Officer contact — BAA requests, PHI incidents) were proposed but not yet confirmed. Add here + to company_info.py if approved.
- **hr@deedavis.biz — INTENTIONALLY routes to bids.deedavisinc@gmail.com, NOT ops.ddinc@gmail.com.** Do not "fix" this to match the gc/qc/apar pattern. It's a verified "Send mail as" alias on the bids.deedavisinc@gmail.com Gmail account, used as `GATEWAY_FROM_EMAIL` for Gateway Portal onboarding emails (see `gateway-portal/PORTAL_DOMAIN_SETUP.md`). Moving it breaks the Gmail "Send mail as" verification and requires re-verification wherever it lands. Dee confirmed (Jul 2026): leave as-is unless there's a real reason to migrate.

### GOOGLE ACCOUNT — NEXUS BIDS (bids.deedavisinc@gmail.com)

| Field | Value |
|---|---|
| **Email** | bids.deedavisinc@gmail.com |
| **Google Payment Identification Number** | **6409-3404-3699** |
| **Use** | NEXUS outbound email, federal/DOD/.mil, Google Pay / payments profile on this account |
| **Env var (NEXUS)** | `GOOGLE_PAYMENT_IDENTIFICATION_NUMBER` in `.env` |

**Confidentiality footers (optional on outbound):** Full copy-paste blocks for **Dee Davis Inc.** and **Cause We Care** — `ESSENTIALS/EMAIL_FOOTER_TEMPLATES.md` — also defined in `company_info.py` as `EMAIL_FOOTER_CONFIDENTIAL_DDI` / `EMAIL_FOOTER_CONFIDENTIAL_CWC`.

---

## 🎯 FEDERAL CREDENTIALS

**EIN:** 84-4114181 ⭐ **CORRECT EIN — USE THIS FOR ALL DOCUMENTS**  
**CAGE Code:** 8UMX3  
**UEI:** HJB4KNYJVGZ1  
**DUNS:** 002636755  
**SAM.gov Status:** Active

> ⚠️ **WARNING:** Some older files contain an incorrect EIN (47-3015027). That is WRONG. The correct EIN is **84-4114181**. Always use this master file as the source of truth.

---

## COMMONWEALTH OF PENNSYLVANIA — PROCUREMENT VENDOR (DGS / eMarketplace)

**Status:** Registered — **Procurement Vendor** (PA **Supplier Relationship Management / SRM**)
**Vendor number:** **0000569615**
**Admin user ID (portal login):** **DEEDAVISINC**

**Confirmation:** SRM registration confirmed via email from **SRMRFC@pa.gov** (April 2026).

**PA Supplier Portal (login):** https://www.pasupplierportal.state.pa.us/irj/portal

**What you can do in the portal (per Commonwealth):**
- View and respond to Commonwealth contract solicitations
- Set up additional users for the organization (including bidders)
- Maintain company data — **bank information (ACH)**, addresses

**Systems:**
- **PA Supplier Portal** — vendor profile, **ACH required** for Commonwealth payment (per standard PA contract terms).
- **JAGGAER** — ITQs, RFQs, RFPs (electronic qualification and submissions; access per portal / SRM workflow).

**Support:** PA Supplier Portal — **1-877-435-7363**, option **1** | **ra-pscsrmportal@pa.gov** | **SRM / registration:** **SRMRFC@pa.gov**  
**JAGGAER:** **1-800-233-1121**, option **2**

**eAlerts (recommended):** Register for solicitation email alerts by category — http://www.dgs.internet.state.pa.us/EAlerts_V2/Login.aspx

**DGS Small Business (PA-specific):** Some solicitations are **Small Business Reserved** (DGS **self-certified** Small Business only). Criteria (Commonwealth): independently owned; not dominant in field; **≤100** FTE employees; **under $38.5 million** gross annual revenue. **Self-certify:** https://pro.prismcompliance.com/CustomCertApp/ApplicationStart.aspx?t=101&j=9qoWxXGezrY%3D *(re-verify link in DGS email if it expires).*

**DGS Small Diverse Business:** First self-certify as Small Business, then verify as **≥51%** minority, woman, veteran, service-disabled veteran, disability, or LGBT-owned for **DGS-verified** Small Diverse opportunities. **Program:** https://www.dgs.pa.gov/Small%20Diverse%20Business%20Program/Pages/default.aspx

**Operational notes:**
- ITQ instructions note **Microsoft Edge or a non-Apple device** if Mac/browser issues during registration or JAGGAER.

**Example active ITQ (courier lane):** Solicitation **4400028185** — Courier Services (statewide; qualification period per eMarketplace — confirm due dates in portal).

---

## 🏆 CERTIFICATIONS

**Small Business:**
- EDWOSB (Economically Disadvantaged Women-Owned Small Business)
- WOSB (Women-Owned Small Business)
- WBE (Woman Business Enterprise)
- MBE (Minority Business Enterprise - NMSDC)
- WBENC Certified (Women's Business Enterprise National Council — nationally recognized WBE)
- SBE (Small Business Enterprise)

**WBENC / Great Lakes WBC — WOSB (DePointe dba) — RENEWAL IN PROGRESS:**
- **Profile:** WOSB — Women-Owned Small Business (WBENC / Great Lakes Women's Business Council)
- **Business:** DEE DAVIS INC. dba **DEPOINTE** | Owner: Dieasha D. Davis
- **Certification date:** 7/31/2025 | **Expiration:** **5/28/2026**
- **Third courtesy notice:** March 29, 2026 (60-day window — **submit renewal before expiration**)
- **Contact:** greatlakeswbc@wbenclink.org | **734-677-1400** | [Great Lakes WBC](https://greatlakeswbc.wbenclink.org)
- **If renewal already submitted:** disregard notice per WBENC email

**Diversity Verification (Third-Party):**
- SupplierGateway — Certificate of Diverse Ownership (Cert #SG07252258991752)
  - Certified Categories: Disadvantaged Business Enterprise, Minority Owned, Small Business, Small Disadvantaged Business, Woman Owned
  - Primary NAICS: 488510
  - Valid: July 10, 2025 — July 9, 2028
  - Applicability: United States
  - Verify: www.suppliergateway.com/verifycert
- Coupa Verified Supplier (Cert ID: 7002160) — ⚠️ EXPIRED 11/19/2025 — NEEDS RENEWAL
  - Verified via voided check, address confirmed: 755 W. Big Beaver Rd Ste 2020, Troy, MI 48084
  - Coupa is used by Fortune 500 companies for procurement — renewal recommended

**Federal/Compliance:**
- E-Verify Certified (Employment Eligibility Verification) — **Company ID: DDAVB62C** | Status: ACTIVE | Role: Program Administrator | Company: DEE DAVIS INC.
- ~~SWFT Authorized~~ — ❌ INCORRECT. SWFT access was denied by DCSA March 2026. Requires minimum interim Secret clearance + Facility Clearance Level. Do NOT claim SWFT on any documents. Path: win a fingerprinting contract → DD Form 254 → FCL triggers automatically.

**PENDING CERTIFICATIONS (In Progress):**
- **8(a) Business Development Program** — SBA certification, APPLICATION PENDING
  - Unlocks: sole-source contracts up to $4.5M (services) / $7M (manufacturing), 8(a) set-asides, mentor-protege program
  - Once certified: NEXUS miners will add 8(a) set-aside filter to all opportunity searches
- **DBE (Disadvantaged Business Enterprise)** — DOT/FTA certification, APPLICATION PENDING
  - Unlocks: DOT/FTA-funded transit contracts with DBE goals, preferred vendor status at transit agencies nationwide
  - Certifying agency: State UCP (Unified Certification Program) — Florida: Hillsborough County Aviation Authority; Michigan: MDOT
  - Directly relevant to: PSTA, DDOT, SMART, and all FTA-funded transit procurement

**⚠️ FINGERPRINTING SCOPE — CURRENT STATUS (Updated April 2026):**

DDI provides biometric fingerprinting services through a partnership with **Lakota Software Solutions** (maker of WHORL biometric platform — built FBI NGI, eDO system, DoD ABIS, DHS HART).

**Current DDI Fingerprinting Capability:**
- **Hardware:** Kojak 10-Print scanner (Integrated Biometrics) — FBI Appendix F certified, portable, USB-powered
- **Software:** WHORL by Lakota — ⚠️ NOT YET ACTIVATED. Lakota relationship exists; WHORL license not yet purchased. Confirm before deploying.
- **Submission:** DDI direct SWFT — ❌ DENIED (March 2026). **Lakota Software — ✅ SWFT-authorized** (partner handles DCSA SWFT submission). DDI primes; Lakota provides SWFT technology. Do NOT claim DDI holds SWFT on outbound docs.
- **ATF EFT Creation** — EFT file creation for FFL dealers, NFA applications (ATF Form 4) — available via Lakota relationship
- **FD-258 Ink Cards** — Traditional rolled prints for paper submissions — available now
- **Federal EDOs** — ⚠️ PENDING CONFIRMATION. Lakota built the FBI's eDO system. Confirm WHORL's EDO submission capability with Sam Cilento before marketing.

**Three Revenue Lanes (strategy in FINGERPRINTING_THREE_LANES.md):**
1. Interstate professional licensure (real estate, nursing, law, insurance agents)
2. ATF/NFA firearms (FFL dealers, suppressors, NFA Form 4)
3. Federal agency fingerprinting (pending WHORL activation + channel confirmation)

**What DDI Does NOT Do (yet):** Michigan state-level fingerprinting via IdentoGO/IDEMIA network. That requires separate state certification. Not competing with IdentoGO in Michigan.

**State Partnerships:**
- MDHHS Community Partner (Michigan Department of Health and Human Services) — **Dee Davis Inc.:** MI Bridges Community Partner **since May 15, 2020**. **Cause We Care:** MI Bridges Community Partner **since 2024**. Do not merge these dates in funder-facing copy. Digital benefits navigation — helping residents create accounts, apply for assistance (SNAP, Medicaid, cash, child care), navigate the online portal, and access referral services. **Past performance: DDI — 200+ benefits applications facilitated; CWC — 50+ benefits applications facilitated.**
- **MDHHS Environmental Health Bureau — Lead Safe Ecosystem Partner (April 23, 2026)** — CWC+DDI pitched and had favorably received a community navigation + program administration partnership model. **Positioning: "Partner in Michigan's lead-safe ecosystem."** See `🏛️ MDHHS PARTNERSHIP — LEAD SAFE ECOSYSTEM` section below for contacts, commitments, and deliverables.

**Technical:**
- CMMC-AB (Cybersecurity Maturity Model Certification)

**Notary & Document Services:**
- CNTDA (Certified Notary & Trained Document Agent — estate planning, trust signings, legal document delivery)
- NPR (Notary Permit Runner — building permit expediting for contractors)
  - Issued by: CYNA / Cynanotary
  - Certified: June 25, 2021
  - Certificate No: cert_pgd973mp
  - Certificate file: `DEE DAVIS INC 2/certificate-of-completion-for-notary-permit-runner-npr.pdf`
- Michigan Commissioned Notary Public — Active Since April 2005 (20+ years)

**State Licenses:**
- Michigan Personnel License #6016004743 (Personnel Agency / Staffing — State of Michigan)
- **Mortgage Loan Originator (MLO) — Michigan** | NMLS# 2099291 | Dieasha D. Davis (active)
- **Mortgage Loan Originator / Mortgage Broker — Georgia** | NMLS# 2099291 | Dieasha D. Davis (active)

**Training Platform Partnerships:**
- **North American Learning Institute (NALI)** — https://nalearning.org/partner — DDI is a registered **Referral Partner** (username: deedav1sinc). Workplace compliance portal: https://courseforwork.com. Used to credential DDI agents, drivers, and subcontractors. DDI can assign courses, track completion, and pull certification proof through the partner portal. 100% online, self-paced, nationally recognized, guaranteed acceptance. Courses start at $15-$25 each.

  **Full NALI Workplace Compliance Course Catalog (29 courses):**

  | Course | Price | DDI Use Case |
  |---|---|---|
  | **HIPAA** | $15 | ALL medical service agents — Rx delivery, NEMT, medical courier, DNA, drug testing |
  | **Bloodborne Pathogens** | $15 | Medical courier, specimen transport, phlebotomy, drug testing collectors |
  | **First Aid** | $25 | NEMT drivers, field agents, all mobile service agents |
  | **CPR** | $25 | NEMT drivers, field agents, all mobile service agents |
  | **Drug & Alcohol Awareness** | $25 | All agents — especially drug testing collectors and supervisors |
  | **HIV/AIDS Awareness** | $15 | Medical service agents, specimen handlers |
  | **HazCom** | $25 | Medical courier, specimen transport, chemical handling |
  | **Fire Safety** | $25 | Field ops, property preservation, facility services |
  | **Confined Space** | $25 | Field ops, property preservation, grounds maintenance |
  | **Ergonomics** | $25 | All field agents — injury prevention |
  | **Sexual Harassment** | $25 | ALL agents — workplace compliance requirement |
  | **Diversity Awareness** | $25 | ALL agents — workplace compliance |
  | **Workplace Violence** | $25 | ALL agents — workplace safety |
  | **Ethics** | $25 | ALL agents — professional conduct |
  | **Conflict Resolution** | $15 | ALL agents — client-facing de-escalation |
  | **Fraud, Waste, and Abuse** | $25 | Billing staff, compliance officers — Medicaid/Medicare FWA requirement |
  | **Human Trafficking** | $25 | NEMT drivers — federally recommended awareness |
  | **Theft Awareness & Prevention** | $25 | Rx delivery (controlled substances), courier, field ops |
  | **Bullying** | $25 | Supervisors, team leads |
  | **Anger Management** | $25 | Court-referral, employee development |
  | **Behavior Modification** | $25 | Court-referral, employee development |
  | **Marijuana Education** | $25 | Drug testing staff — policy awareness |
  | **Tobacco Awareness** | $25 | Occupational health, wellness programs |
  | **Vaping** | $25 | Occupational health, student/athlete testing |
  | **Virus Awareness (COVID-19)** | $25 | All field agents — infection control |
  | **Food Safety** | $25 | Facility services, janitorial |
  | **Food Allergens** | $25 | Facility services |
  | **Concussions** | $25 | Athletics testing programs (K-12/collegiate) |
  | **PIPEDA Training** | $25 | Canadian privacy compliance (if cross-border work) |

  **IMPORTANT: DDI offers access to training through the NALI partner portal — DDI does NOT pay for agent/sub training. All subcontractors and independent agents are responsible for their own training costs. DDI provides the platform and referral access; the sub pays for and completes the courses themselves.**

  **Credentialing fees (sub pays DDI):** DDI charges a **credentialing fee** above partner list price for assignment, completion tracking, audit-ready records, MCO/contract gate checks, and PRISM activation. Published fee table and bundles: `DEE_DAVIS_INC_COMPLETE_SERVICE_CATALOG.md` (section *Agent Credentialing Program*). Machine-readable fees: `prism_service_router.py` — `CREDENTIAL_TRAINING_SOURCES`, `CREDENTIALING_BUNDLES`, `CREDENTIALING_FULL_PACKAGES`.

  **Key DDI-required courses by service line (agent/sub pays):**
  - Rx Delivery drivers: HIPAA + Drug & Alcohol Awareness + Theft Awareness
  - NEMT drivers: HIPAA + First Aid + CPR + Human Trafficking + Drug & Alcohol Awareness
  - Medical Courier: HIPAA + Bloodborne Pathogens + HazCom
  - Drug Testing Collectors: HIPAA + Bloodborne Pathogens + Drug & Alcohol Awareness
  - ALL agents (baseline): Sexual Harassment + Diversity Awareness + Ethics + Conflict Resolution + Workplace Violence

  **Additional Training Platform:**
  - **Quest Employer Solutions Online Training Center** — DOT-specific training (DOT Supervisor Reasonable Suspicion, DOT Drug & Alcohol Awareness, FMCSA compliance). Used for drug testing collector and C/TPA supervisor training requirements.

**Professional Training & Certifications:**
- **Legal Support Specialist Certification** — certificate on file (`COMPANY_DOCUMENTS/CERTIFICATIONS/LEGAL_SUPPORT_SPECIALIST_CERTIFICATION.pdf`; synced from iCloud CERTIFICATES)
- **Virtual Transaction Coordination Certification** — certificate on file (`COMPANY_DOCUMENTS/CERTIFICATIONS/VIRTUAL_TRANSACTION_COORDINATION_CERTIFICATE.pdf`; synced from iCloud `CERTIFICATES/VIRTUAL TRANSACTION COORIDNATION CERTIFICATE.pdf`)
- **Property Data Collection Training Certificate #I-03** (Walitt Solutions, September 25, 2022) — HUD/Fannie Mae PDC report format, residential property condition assessment, data collection protocols
- **Property & Casualty Insurance Prelicense Certificate** (A.D. Banker & Company, Course #0432, September 22, 2022) — property risk assessment, casualty evaluation, insurance compliance
- **Real Estate Prelicense Certificate** — Michigan real estate principles, property law, transaction documentation
- Project Management for Government Projects (certificate on file — image-based PDF)
- Property Preservation industry contacts and relationships (Safeguard Properties network)
- CSH Supportive Housing Onboarding — Homelessness Systems & Coordinated Entry (Dec 2023)
- CSH Building Community in Supportive Housing (Cert ID: yxqpbk330i, Dec 2023)

**Security:**
- TWIC-Certified Personnel (Transportation Worker Identification Credential — secure facility access)
- **ALL DDI drivers and couriers MUST be TWIC-certified** — non-negotiable requirement for DDI operations
- TWIC Escort Services — DDI provides escorts for non-cleared personnel in restricted/secure areas (ports, maritime terminals, government installations)
- DDI ownership (Dieasha D. Davis + spouse) — both TWIC-certified
- Subcontractor fleet (God Is Good Hauling) — all main drivers TWIC-certified

**TWIC Credentials (CONFIDENTIAL):**
- **Dieasha D. Davis — TWIC PIN:** 68527963

**Business Model:**
- Value-Added Reseller (VAR) — DDI sources products from manufacturer-authorized distributors, adds procurement management, compliance documentation, quality assurance, and logistics coordination, then delivers to the end client. This is DDI's core product supply model for government contracts. Used across medical supplies, industrial equipment, IT hardware, office products, and all commodity categories.

**Entity Type:** C Corporation

---

## 📋 DBA / SUBSIDIARY NAMES

- **DBA:** The Professionals' Professionals
- **Freight 1st Direct** — DDI's independent freight brokerage (MC-1647572, DOT-4250594)
- **FleetFlow TMS LLC** — Logistics technology subsidiary (pre-launch mid-2026)
- **3D Ink and Livescan Co** — Fingerprinting and compliance services division
- **Depointe DNA** — DNA testing services division (DDC/DNA Diagnostics Center collection partner)

---

## 🤲 AFFILIATED NONPROFIT: CAUSE WE CARE

**Legal Name:** Cause We Care  
**Doing Business As (DBA):** *(none — blank on SAM.gov)*  
**Type:** 501(c)(3) Nonprofit Organization  
**EIN:** 92-3602670  
**Physical Address (SAM.gov):** 755 W. Big Beaver Rd., Suite 2020, Troy, Michigan 48084-4925, USA  
**Mailing (legacy on some grant drafts — verify before reuse):** 1221 Bowers St, Unit 2141, Birmingham, Michigan 48012  
**EMAIL ROUTING (FYI — use the right inbox):**
| Inbox | Address | Use for |
|-------|---------|---------|
| **Executive Director / primary** | **ddavis@cwecare.org** | Dieasha D. Davis (ED); leadership, grantor/partner-facing where the ED is the contact, strategic nonprofit correspondence |
| **General organization** | **info@cwecare.org** | General inquiries, public routing, org-wide notices (board/team can triage) |

**Phone:** 248.376.4550  
**Website:** cwecare.org — **LIVE** (dedicated Netlify site; deploy via `nexus-frontend/CWC_DEPLOY.md`)  
**Founder/Executive Director:** Dieasha D. Davis  
**Board Director (Veteran):** Gary C. Felton Jr. — U.S. Army Veteran  
**Focus Areas:** Community health, social services, veteran support, underserved populations  

**Mission & Vision (canonical — cwecare.org):**
- **Public purpose:** We connect families to the resources they need — food security, safe housing, education essentials, health navigation, and community support — because every family deserves someone in their corner.
- **Formal mission:** To connect Michigan families with the resources, support, and navigation they need to overcome hardship — without barriers, without judgment, and without delay.
- **Tagline:** Cause We Care, You Should Too. · **Theme:** Care. Navigate. Transform.
- **Vision:** A Michigan where no family faces crisis alone — community care as the standard, not the exception.

**CWC + DDI structural alignment (grants / funders):**  
`GRANT_APPLICATION_PACKAGE/CWC_GRANTS/CWC_DDI_MISSION_ALIGNMENT.html` (PDF via Chrome print) · companion `CWC_DDI_MISSION_ALIGNMENT.md`

**MDHHS MI Bridges Community Partner:** Since **2024** *(DDI: since May 15, 2020 — separate entity, separate enrollment date)*

**Active Programs:**
- MIBridges benefits navigation (MDHHS Community Partner since 2024)
- Community health outreach and lead-based paint awareness (Wayne Metro liaison)
- Hair Cuts for Vets (Gary C. Felton Jr. program — veteran community engagement)
- Veteran employment and hiring initiative
- Homelessness systems and coordinated entry services

**Dee Davis — CSH (Corporation for Supportive Housing) Training:**
- CSH Supportive Housing Onboarding Series — Homelessness Systems & Coordinated Entry (completed Dec 17, 2023)
- CSH Building Community in Supportive Housing (Cert ID: yxqpbk330i, issued Dec 17, 2023)

**Strategic Role in DDI Ecosystem:**
- Cause We Care serves as DDI's community-based organization (CBO) teaming partner
  for government research contracts and community health proposals
- Eligible to apply for foundation grants, federal grants (via Grants.gov), and MDHHS subgrants
- Gary Felton's veteran leadership opens veteran-focused grant funding and HIRE Vets recognition

**Federal Credentials:**
- **UEI:** **VEJMFMVV6PQ1** — entity registration **submitted** (await Active in SAM)
- **EIN:** 92-3602670
- **CAGE:** *(none until full SAM registration completes)*

**SAM.gov Status:**
- **UEI:** VEJMFMVV6PQ1
- **Physical address on record:** 755 W. Big Beaver Rd., Ste 2020, Troy, MI 48084-4925, USA
- **Entity registration submitted** — confirmation email to **nsa@deedavis.ink** — **no action required at this time** (await GSA validation / active status)
- Prior renewal ref (if applicable): INC-GSAFSD8651858 — March 22, 2026

**Registration Status:**
- [x] **SAM.gov — ENTITY REGISTRATION SUBMITTED** — await confirmation email processing + **Active** status in SAM before federal bids / CAGE
- [ ] SAM.gov shows **Active** registration — verify in portal when available
- [ ] Grants.gov applicant account — PENDING (**after** SAM shows Active)
- [ ] Community Foundation for SE Michigan portal — PENDING
- [ ] Michigan Health Endowment Fund portal — PENDING
- [x] GiveButter "Haircuts for Heroes" — ACTIVE — givebutter.com/haircutsforheroes/causewecare — Goal: $20K — needs promotion push
- [x] GiveButter "Kids in Comfort" — ACTIVE — givebutter.com/kidsincomfort — Goal: $40K — community underwear drive
- [x] Website cwecare.org — **LIVE** (Jun 2026) — mission on About page; homepage hero copy per live site

**Source of Truth:** This section is the master reference for all Cause We Care grant
applications, teaming agreements, and NEXUS GBIS pipeline records.

---

## 📋 VENDOR PORTAL REGISTRATIONS

- **SAM.gov** — Active
- **Michigan SIGMA VSS** — Registered (sigmavss.michigan.gov) — Vendor # VS0245604
- **Maryland eMMA** — Registration in progress (emma.maryland.gov)
- **BidNet Direct / MITN** — Registered (100+ Michigan municipal agencies)
- **Oakland County Supplier Diversity Program** — Registered
- **Sourcewell** — Active (cooperative purchasing — vehicle and equipment contracts)
- **Kentucky VSS** — Registered (vss.ky.gov) — Vendor # KS0026951 — Since 02/15/2025 — **⚠️ Must submit Form SAS-63 with every Kentucky bid**
- **Maine VSS** — **Active** (Advantage Self Service) — Vendor # **VS0000032746** — Activated **06/15/2026** — See **Maine VSS section below** — **⚠️ Mail/fax Substitute W-9 per portal instructions if not yet done**

---

## STATE OF MAINE — ADVANTAGE VSS (PROCUREMENT VENDOR)

**Status:** **Certified user — active** (welcome email **June 15, 2026** from `ADVANTAGEME.SYSADM@maine.gov`)

**System:** **Advantage Self Service (VSS)** — State of Maine Division of Purchases vendor/procurement portal ( **not** MaineCare Medicaid provider enrollment — that is a separate DHHS process).

| Field | Value |
|-------|-------|
| **Portal URL** | https://mevss.hostams.com/PRDVSS1X1/AltSelfService |
| **Vendor / Customer code** | **VS0000032746** |
| **Headquarters Account Code** | **VS0000032746** |
| **User ID (case sensitive)** | **DEEDAVISINC** |
| **Headquarters legal name** | DEE DAVIS INC |
| **Location name** | DEE DAVIS INC |
| **Activation confirmed** | **June 15, 2026** |

**What this is:** Maine **state procurement** vendor registration — view/respond to state RFPs, contracts, and grants posted on Maine VSS (e.g. DHHS solicitations such as MaineCare NET opp **0520260310**).

**What this is NOT:** Approved **MaineCare Medicaid provider** status. DDI is **not** enrolled as a Maine Medicaid provider in this master file (active Medicaid: Michigan, Maryland only).

**Remaining setup:**
- [ ] **Substitute W-9** — mail/fax per portal instructions if not already submitted

**Support:**
- **VSS / procurement questions:** Maine Division of Purchases — **(207) 624-7340**
- **Login / password:** Maine IT Help Desk — **(207) 624-7700**
- Notification email is no-reply — do not reply to `ADVANTAGEME.SYSADM@maine.gov`

---

## 📋 INDUSTRY MEMBERSHIPS

- **NMSDC** (National Minority Supplier Development Council) — MBE certification

---

## 📋 INDUSTRY LICENSES

**Healthcare:**
- NPI: 1538939111 (Healthcare Provider)
- Active Medicaid Provider (**Michigan**, **Maryland**). **Texas:** TMHP portal login / **Provider Administrator** on enrollment transaction **D19273048** only — **Texas Medicaid provider enrollment not yet applied / not submitted** per Dee; TMHP access can exist before a complete application.

**Transportation/Logistics:**
- MC Number: 1647572 (Freight Broker)
- US DOT: 4250594
- **SCAC Code: DFCL** (Standard Carrier Alpha Code — NMFTA) — ⚠️ **EXPIRED Feb 3, 2026 — RENEWAL REQUIRED** — Originally assigned to DEPOINTE, needs update to DEE DAVIS INC + Troy address. Certificate: `BIDS:RESOURCES/CERTIFICATES FOR NEXUS REFERENCES/certificate.pdf`. Renew at https://scaccode.com ($97/year). Required for USPS Logistics Gateway (HCR routes) and federal freight contracts.

### Terminology — Healthcare logistics & medical courier (both in NEXUS)

- **Healthcare logistics** — Preferred **umbrella** for buyer-facing positioning: coordination of medical-related transport, specimens, supplies, chain of custody, and compliance (cap statements, general outreach when not mirroring a specific RFx).
- **Medical courier** — **Keep** for solicitations, NAICS-aligned bids, SAM/keyword discovery, and whenever the buyer’s document says **medical courier** — mirror their language.
- **Code:** `company_info.py` — `HEALTHCARE_LOGISTICS_PRIMARY_LABEL`, `MEDICAL_COURIER_RFP_KEYWORD`, `HEALTHCARE_LOGISTICS_SEARCH_KEYWORDS`.

### Terminology — NEMT, patient transport & RFx language (both in NEXUS)

- **Non-emergency medical transportation (NEMT)** — Preferred **umbrella**; **NEMT** is the usual government/Medicaid shorthand.
- **Patient transport / medical transport / paratransit / wheelchair or stretcher** — Use when the **solicitation, MCO, or state portal** uses those words — **mirror the buyer**.
- **Code:** `company_info.py` — `NEMT_PRIMARY_LABEL`, `NEMT_SHORT`, `NEMT_SEARCH_KEYWORDS`.

### Terminology — Biometrics & fingerprinting (both in NEXUS)

- **Biometrics** — Preferred **umbrella** for positioning (identity capture, fingerprint-based services).
- **Fingerprinting / livescan / electronic fingerprinting / FD-258 / criminal history / applicant prints** — Use when the **solicitation** uses those words — **mirror the buyer**. Channeling/submission is **per contract**; do not claim DCSA SWFT unless `COMPANY_INFO_MASTER.md` / NEXUS corrections say so.
- **Code:** `company_info.py` — `BIOMETRICS_PRIMARY_LABEL`, `FINGERPRINTING_RFX_KEYWORD`, `BIOMETRICS_FINGERPRINTING_SEARCH_KEYWORDS`.

### Terminology — Drug & alcohol testing (both in NEXUS)

- **Drug and alcohol testing** — Preferred **umbrella** (occupational / workplace programs; DOT vs non-DOT per contract).
- **Drug testing** alone — Fine when RFx uses that shorthand; **mirror** terms like **DOT**, **SAMHSA**, **C/TPA / consortium**, **random**, **pre-employment**, **post-accident**, **Part 40** when the buyer does.
- **Code:** `company_info.py` — `DRUG_ALCOHOL_TESTING_PRIMARY_LABEL`, `DRUG_TESTING_RFX_KEYWORD`, `DRUG_ALCOHOL_TESTING_SEARCH_KEYWORDS`.

### Terminology — Notary, authentication, witnessing & credentialing (both in NEXUS)

- **Notarial services** — Preferred **umbrella** for notary-facing positioning.
- **Notary / mobile notary / RON / signing agent / loan signing** — Mirror **RFx** language; state law governs acts (acknowledgment, jurat, copy certification, etc.).
- **Document authentication** — Often paired with notary/apostille in solicitations — **mirror the buyer’s terms** (authentication vs apostille vs legalization).
- **Witnessing** — Use when the solicitation says **witness** / **subscribing witness**; do not conflate with notarial acts unless the RFx does.
- **Credentialing** — Umbrella for **workforce / healthcare / provider** credentialing; mirror **primary source verification (PSV)**, **enrollment**, **privileging**, **licensure verification** when those appear.
- **Code:** `company_info.py` — `NOTARY_PRIMARY_LABEL`, `NOTARY_RFX_KEYWORD`, `NOTARY_AUTHENTICATION_WITNESSING_SEARCH_KEYWORDS`, `CREDENTIALING_PRIMARY_LABEL`, `CREDENTIALING_SEARCH_KEYWORDS`.

---

## 🤝 STRATEGIC PARTNERSHIPS

**Healthcare & Testing:**
- Quest Diagnostics (Certified DOT drug testing provider)
- Concentra — Occupational health and clinical services network partner (nationwide occ health locations; DOT physicals, titers, and clinical bundles as scoped per contract; complements Quest/eScreen for integrated TPA fulfillment)
- DDC (DNA Diagnostics Center) - Court-admissible DNA testing (DDI is a collection partner via Depointe DNA DBA)
- Uber Health (NEMT transportation platform)
- **USDTL (United States Drug Testing Laboratories)** — OUTREACH SENT 03/20/2026 — Hair, nail, umbilical cord, oral fluid testing. SAMHSA-certified, CAP/CLIA accredited. Des Plaines, IL. Contact: Jenny Rodriguez, forensictesting@usdtl.com. Expands DDI's testing menu beyond urine/oral fluid into alternative specimen testing (90-day detection window). Collection partner agreement pending.

**Professional Services:**
- ZigSig (Remote Online Notarization platform)
- NALI (Professional training & compliance)

**Financial Services:**
- Bankers Factoring (DDI is an authorized BROKER — DDI refers businesses to Bankers Factoring and earns broker commissions. Also available for DDI's own government contract invoices. Non-recourse factoring, up to 90% advance, same-day funding, PO financing. Contact: Chris Curtin, President, chris@bankersfactoring.com, 866-598-4295, cell 561-758-6285)
- SuretyCloud (Federal contract bond solutions)

**Logistics:**
- Freight 1st Direct (DDI's independent freight brokerage — MC-1647572, DOT-4250594)

---

## 💻 PROPRIETARY TECHNOLOGY (FOUNDER-BUILT — DDI'S COMPETITIVE MOAT)

**DDI's technology infrastructure was designed and built by founder Dee Davis. These are not off-the-shelf tools — they are proprietary AI systems that represent years of development, a significant intellectual property asset, and a 5-10 year competitive advantage over other government contractors.**

**NEXUS — AI-Assisted Contract Acquisition Operating System**
- Master platform integrating all 8 DDI systems
- Automates 90% of the contract lifecycle (discovery → award → execution)
- Fortune 500-level capability at small business scale
- Status: Operational (continuous enhancement)

**GPSS — Government Procurement Strategic System**
- AI-powered opportunity mining (SAM.gov, 22+ vendor portals)
- Automated proposal generation (4 hours vs. industry 2-3 days)
- Supplier/subcontractor automated sourcing with USASpending verification
- ProposalBio™ scientific persuasion framework (10-point scoring)
- Status: Operational

**ATLAS PM — Enterprise Intelligence & Project Management**
- AI-enabled project orchestration and real-time compliance monitoring
- Automated WBS generation, change order impact analysis
- Predictive analytics and strategic decision support
- Status: Operational

**FleetFlow™ — Logistics Intelligence Platform**
- Advanced AI & predictive modeling for freight/logistics
- Real-time operational intelligence, route optimization
- Company: FleetFlow TMS LLC (a DEE DAVIS INC company)
- Status: Pre-launch (Mid-2026)

**COMPASS™ — Proposal Quality Assurance System**
- ProposalBio 10-point biohack validation on every buyer-facing document
- Compliance checking, win-readiness assessment
- Status: Integrated across all systems

**PRISM — Field Service Dispatch & Management**
- Professional resource inspection, dispatch, document verification
- AI-powered document inspection (signatures, seals, compliance)
- Status: Architecture phase

**DDCSS — Corporate Sales System**
- Client avatar building, success path mapping, PitchMap generation
- AI email response analysis, multi-sector pipeline management
- Status: Operational

**VERTEX — Financial Management System**
- Automated invoicing (government & enterprise compliant)
- Real-time profit tracking, cash flow forecasting
- Status: Operational

**GBIS — Grant Business Intelligence System**
- Grant discovery, eligibility screening, application pipeline
- Status: Operational

**Technology Grant Eligibility:**
These platforms qualify DDI for SBIR/STTR grants ($50K-$2M+), SBA Growth Accelerator grants, EDA tech development grants, Michigan MEDC innovation funding, and NSF SBIR programs. The technology is also a future SaaS licensing opportunity (30,000+ small government contractors as addressable market).

---

## 🎯 CORE POSITIONING

**Business Identity:** FEDERALLY CERTIFIED EDWOSB CONTRACT MANAGEMENT FIRM & BUSINESS OPERATING SYSTEM — FOCUSED ON ALL FORMS OF BUSINESS CONTINUITY

**Tagline:** "The Professionals' Professionals"

**What DDI Is:**
Dee Davis Inc. is a federally certified EDWOSB contract management firm and business operating system focused on all forms of business continuity. DDI wins contracts, sources qualified subcontractors and suppliers to fulfill the work, and manages every aspect of project delivery — compliance, invoicing, quality assurance, reporting, and coordination. DDI is the single accountable point of contact between the client and a network of vetted fulfillment partners. Nothing stops because one person, one vendor, or one system is unavailable.

**Why Business Continuity:**
Every service DDI delivers — drug testing, fingerprinting, courier, grounds maintenance, NEMT, staffing, emergency logistics — exists to keep operations running without interruption. DDI's proprietary AI technology platforms (NEXUS, ATLAS PM, FleetFlow™, COMPASS™, PRISM, GPSS, DDCSS, VERTEX, GBIS) replicate decision-making across hundreds of operations simultaneously. If a subcontractor falls through, the system reroutes. If a compliance deadline shifts, the system adapts. If a client needs emergency logistics at 2 AM, the system responds. That is business continuity — and it is DDI's core identity, not a service line.

**Why DDI Can Compete in Any Category:**
DDI is not limited by trade or commodity. Contract management, administration, and coordination — powered by proprietary AI technology — is the core competency. If there's a contract, DDI can win it, source the right people or products, and manage the delivery. This is why DDI operates across healthcare, facilities, logistics, construction, transportation, professional services, emergency management, and every other sector.

**Proprietary Technology Platforms (Built In-House by Founder):**
DDI's competitive moat is its technology. Dee Davis personally built 8+ integrated AI systems that automate 90% of the contract acquisition and delivery lifecycle — enabling Fortune 500-level operations at small business scale:
- **NEXUS** — Cohesive AI-Assisted Contract Acquisition Operating System (the master platform)
- **GPSS** — Government Procurement Strategic System (opportunity discovery through award)
- **ATLAS PM** — AI-Powered Enterprise Intelligence & Project Management Platform
- **FleetFlow™** — Advanced Logistics Intelligence Platform (pre-launch mid-2026, FleetFlow TMS LLC)
- **COMPASS™** — Proposal Quality Assurance & Validation System (ProposalBio 10-point scoring)
- **PRISM** — Professional Resource Inspection & Service Management (field service dispatch)
- **DDCSS** — Diversity Division Corporate Success System (corporate sales pipeline)
- **VERTEX** — Financial Excellence & Revenue Tracking Executive System
- **GBIS** — Grant Business Intelligence System (grant discovery and application)

This technology infrastructure is not just operational tooling — it is an asset class with SBIR/STTR eligibility, tech grant potential, and future SaaS licensing value.

**Elevator Pitch (Updated Feb 2026):**
"As someone who's not a people person at all, I built DEE DAVIS INC to prove that exceptional service doesn't require constant hand-holding—it requires exceptional systems. Basically, I figured out how to clone myself through technology instead of hiring people I'd have to manage.

We're a certified EDWOSB contract management firm under CAGE Code 8UMX3. We win government and commercial contracts across every sector, source qualified partners to execute the work, and manage the entire delivery—compliance, invoicing, quality assurance, everything. We don't do the work. We make sure the work gets done right.

That model powers everything we touch—emergency logistics through DEPOINTE, drug testing and mobile compliance through 3D Ink & Livescan, freight brokerage through Freight 1st Direct, and certified notary services through CNTDA. Same philosophy, different battlefield.

But here's what actually matters: every operation runs on proprietary AI platforms like ATLAS PM, FleetFlow™, and NEXUS Command Center that replicate my decision-making across hundreds of operations simultaneously. That's not just automation—that's business continuity. If a subcontractor falls through, the system reroutes. If a compliance deadline shifts, the system adapts. If I'm asleep at 2 AM and a client needs emergency logistics, the system responds. Nothing stops because one person is unavailable.

So while other contractors are drowning in manual processes and hoping their teams 'get it,' my clones are handling 24/7 emergency response, regulatory compliance tracking, crisis management, and white-glove client services—without me ever being on a call.

The result? No waiting for callbacks. No wondering if someone dropped the ball. No 'managing the manager.' Just flawless execution delivered through technology-first operations that scale without the chaos.

We're 'The Professionals' Professionals' because we engineer solutions while others are still managing problems. Zero drama—and honestly? My clones work harder than I ever could."

**Short Version (for emails/intros):**
"Dee Davis Inc. is a federally certified EDWOSB contract management firm and business operating system based in Troy, Michigan, focused on all forms of business continuity. Powered by proprietary AI technology platforms built in-house, we win contracts, source qualified partners, and manage project delivery across every sector — ensuring nothing stops because one person or one system is unavailable."

**Business Description (~1,000 characters — for SAM.gov, vendor registrations, portals):**
Dee Davis Inc. — "The Professionals' Professionals" is a federally certified EDWOSB contract management firm and business operating system headquartered in Troy, Michigan, focused on all forms of business continuity. We win government and commercial contracts across every sector, source qualified partners to execute the work, and manage every aspect of project delivery — compliance, invoicing, quality assurance, coordination — ensuring operations never stop. Our proprietary AI technology platforms (NEXUS, ATLAS PM, FleetFlow™, COMPASS™, PRISM) automate 90% of the contract lifecycle, enabling Fortune 500-level operations at small business scale. Certified EDWOSB, WOSB, WBE, MBE, SBE, WBENC with full federal credentials (CAGE: 8UMX3, UEI: HJB4KNYJVGZ1), E-Verify enrolled, CMMC-AB certified. We hold DOT and MC authority for transportation, NPI for healthcare, and active Medicaid provider status in multiple states. Dee Davis Inc. doesn't do the work — we make sure the work never stops.

---

## 🔢 NAICS CODES — COMPLETE MASTER LIST (SAM.gov Source of Truth)

**Last Updated:** March 2, 2026 — Full sweep of all NEXUS files
**Instructions:** Log into sam.gov → Dee Davis Inc. → Edit Registration → NAICS Codes
**Codes marked ✅ VERIFY** = should already be there, confirm they are
**Codes marked ⚠️ ADD** = not yet in SAM, must be added now

---

### GROUP 1 — HEALTHCARE, TESTING & COMPLIANCE

| NAICS | Description | DDI Service | Action |
|-------|-------------|-------------|--------|
| 621511 | Medical Laboratories | Drug testing, DNA, lead testing | ✅ VERIFY |
| 621999 | All Other Ambulatory Health Care Services | Mobile testing, lead testing, NEMT | ✅ VERIFY |
| 621910 | Ambulance Services | NEMT program development | ✅ VERIFY |
| 541620 | Environmental Consulting Services | Lead testing, environmental programs | ✅ VERIFY |
| 541380 | Testing Laboratories and Services | Drug/lab testing coordination | ✅ VERIFY |

---

### GROUP 2 — FINGERPRINTING, BACKGROUND CHECKS & SECURITY

| NAICS | Description | DDI Service | Action |
|-------|-------------|-------------|--------|
| 561611 | Investigation, Guard & Armored Car Services | Fingerprinting, background checks, SWFT | ✅ VERIFY |
| 561612 | Security Guards and Patrol Services | Security services, background checks | ✅ VERIFY |

---

### GROUP 3 — PROFESSIONAL & LEGAL SERVICES

| NAICS | Description | DDI Service | Action |
|-------|-------------|-------------|--------|
| 541199 | All Other Legal Services | Notary, RON, document prep | ✅ VERIFY |
| 541990 | All Other Professional, Scientific & Technical | Drug testing, fingerprinting, notary overflow | ✅ VERIFY |
| 561110 | Office Administrative Services | Document preparation, permit running | ✅ VERIFY |
| 561492 | Court Reporting and Stenotype Services | Court-related document services | ✅ VERIFY |
| 541930 | Translation and Interpretation Services | Translation services lane | ✅ VERIFY |

---

### GROUP 4 — MANAGEMENT CONSULTING & ADVISORY

| NAICS | Description | DDI Service | Action |
|-------|-------------|-------------|--------|
| 541611 | Administrative Management Consulting | Contract management, NEMT, project executive | ✅ VERIFY |
| 541614 | Process, Physical Distribution & Logistics Consulting | Transportation optimization, freight | ✅ VERIFY |
| 541618 | Other Management Consulting Services | Business continuity, crisis coordination | ✅ VERIFY |
| 541690 | Other Scientific & Technical Consulting | Federal advisory, HHS consulting, program support | ✅ VERIFY |
| 541612 | Human Resources Consulting Services | Staffing advisory, workforce consulting | ✅ VERIFY |

---

### GROUP 5 — STAFFING & WORKFORCE

| NAICS | Description | DDI Service | Action |
|-------|-------------|-------------|--------|
| 561320 | Temporary Help Services | Staffing solutions (Employment Crew) | ✅ VERIFY |
| 561311 | Employment Placement Agencies | Staffing solutions, direct placement | ✅ VERIFY |

---

### GROUP 6 — IT & TECHNOLOGY SERVICES

| NAICS | Description | DDI Service | Action |
|-------|-------------|-------------|--------|
| 541512 | Computer Systems Design Services | IT services contracts | ✅ VERIFY |
| 541519 | Other Computer Related Services | IT support, tech services | ✅ VERIFY |
| 541511 | Custom Computer Programming Services | Software/systems development | ✅ ADDED |
| 518210 | Computing Infrastructure Providers, Data Processing | Records management, data services | ✅ ADDED |

---

### GROUP 7 — TRANSPORTATION, COURIER & LOGISTICS

| NAICS | Description | DDI Service | Action |
|-------|-------------|-------------|--------|
| 485991 | Special Needs Transportation | NEMT (wheelchair van, paratransit) | ✅ VERIFY |
| 485999 | All Other Transit & Ground Passenger Transportation | NEMT overflow | ✅ VERIFY |
| 492110 | Couriers and Express Delivery Services | Medical courier, specimen transport | ✅ VERIFY |
| 492210 | Local Messengers and Delivery | Local courier, permit running | ✅ VERIFY |
| 488510 | Freight Transportation Arrangement | Freight 1st Direct brokerage | ✅ VERIFY |
| 488190 | Other Support Activities for Air Transportation | Freight 1st Direct AOG ground courier + TWIC escort | ⚠️ ADD |
| 484210 | Used Household and Office Goods Moving | Moving & relocation contracts | ✅ VERIFY |

---

### GROUP 8 — FACILITIES, CONSTRUCTION & GROUNDS

| NAICS | Description | DDI Service | Action |
|-------|-------------|-------------|--------|
| 561720 | Janitorial Services | Janitorial & custodial contracts | ✅ VERIFY |
| 561730 | Landscaping Services | Grounds maintenance contracts | ✅ VERIFY |
| 561210 | Facilities Support Services | Facility maintenance & repair | ✅ VERIFY |
| 561790 | Other Services to Buildings & Dwellings | Pressure washing, exterior services | ✅ VERIFY |
| 561990 | All Other Support Services | General facility support overflow | ✅ ADDED |
| 236220 | Commercial & Institutional Building Construction | Construction contracts | ✅ VERIFY |
| 238990 | All Other Specialty Trade Contractors | Construction renovation | ✅ VERIFY |
| 238160 | Roofing Contractors | Roofing contracts | ✅ ADDED |
| 238330 | Flooring Contractors | Flooring contracts | ✅ ADDED |

---

### GROUP 9 — EVENTS & SECURITY

| NAICS | Description | DDI Service | Action |
|-------|-------------|-------------|--------|
| 561920 | Convention and Trade Show Organizers | Event services contracts | ✅ VERIFY |
| 561621 | Security Systems Services | Security systems installation | ✅ ADDED |

---

### GROUP 10 — FINANCIAL & INSURANCE SERVICES

| NAICS | Description | DDI Service | Action |
|-------|-------------|-------------|--------|
| 524126 | Direct Property & Casualty Insurance Carriers | Surety bonds | ✅ VERIFY |
| 524210 | Insurance Agencies and Brokerages | Surety bonds, bond placement | ✅ VERIFY |

---

### GROUP 11 — MEDICAL & INDUSTRIAL PRODUCTS (RESALE/VAR)

| NAICS | Description | DDI Service | Action |
|-------|-------------|-------------|--------|
| 423450 | Medical & Hospital Equipment Merchant Wholesalers | Medical supplies resale | ✅ VERIFY |
| 339113 | Surgical Appliance & Supplies Manufacturing | Surgical supplies (DLA, VA) | ✅ VERIFY |
| 339112 | Surgical & Medical Instrument Manufacturing | Medical instruments resale | ✅ VERIFY |
| 424210 | Drugs & Druggists' Sundries Merchant Wholesalers | Pharmaceutical supplies | ✅ ADDED |
| 423850 | Industrial Supplies Merchant Wholesalers | Industrial supplies (CPS Energy, RCOC) | ✅ VERIFY |
| 423840 | Industrial Machinery & Equipment Merchant Wholesalers | Industrial equipment resale | ✅ VERIFY |
| 424120 | Stationery & Office Supplies Merchant Wholesalers | Office supplies contracts | ✅ VERIFY |
| 424490 | Other Grocery & Related Products | Food/beverage supplies | ✅ VERIFY |

---

### GROUP 12 — EMERGENCY, DISASTER & ENVIRONMENTAL

| NAICS | Description | DDI Service | Action |
|-------|-------------|-------------|--------|
| 562910 | Remediation Services | Environmental remediation contracts | ✅ VERIFY |
| 562119 | Other Waste Collection | Waste/debris contracts | ✅ VERIFY |
| 562112 | Hazardous Waste Collection | Medical/hazardous waste | ✅ VERIFY |
| **721110** | Hotels (except Casino Hotels) and Motels | HAVEN disaster housing coordination | ⚠️ ADD |
| **621610** | Home Health Care Services | HAVEN medical continuity post-disaster | ⚠️ ADD |
| **488999** | All Other Support Activities for Transportation | HAVEN evacuation logistics | ⚠️ ADD |

---

### GROUP 13 — DOCUMENT & RECORDS MANAGEMENT

| NAICS | Description | DDI Service | Action |
|-------|-------------|-------------|--------|
| 561410 | Document Preparation Services | Document prep, records | ✅ VERIFY |

---

### ⚠️ GROUP 14 — MARKET RESEARCH & COMMUNITY HEALTH (NEW LANE)

**ADD ALL OF THESE before submitting OASIS+ application.**

| NAICS | Description | DDI Service / Lane | Action |
|-------|-------------|-------------------|--------|
| **541910** | Market Research and Public Opinion Polling | Market research, survey admin, SB/diversity research | ✅ ADDED |
| **541720** | R&D in the Social Sciences and Humanities | Community health needs assessment, program evaluation, SDOH | ✅ ADDED |
| **624190** | Other Individual and Family Services | MIBridges benefits navigation, social services coordination | ✅ ADDED |
| **624230** | Emergency and Other Relief Services | Crisis social services, emergency community support | ✅ ADDED |
| **624221** | Temporary Shelters | Homeless services, housing support programs | ✅ ADDED |

---

### OASIS+ WOSB — PRIMARY NAICS PER DOMAIN

| Domain | Primary NAICS | Description |
|--------|--------------|-------------|
| **Social Services** | 624190 | Other Individual and Family Services |
| **Management and Advisory** | 541611 | Administrative Management Consulting |
| **Research and Development** | 541720 | R&D in the Social Sciences |

---

### HOW TO UPDATE SAM.GOV RIGHT NOW

```
1. Go to sam.gov → Sign In
2. Entity Registrations → Dee Davis Inc. → Edit Registration
3. Navigate to "NAICS Codes" section
4. VERIFY all codes marked ✅ VERIFY are present
5. ADD every code marked ⚠️ ADD (especially Group 14)
6. Save and submit
7. Wait 24–48 hours for propagation
8. Then go to oasis.app.cloud.gov and begin OASIS+ submission
```

**Total codes in this master list: 57**
**All 57 codes confirmed in SAM.gov as of March 2026.**

---

## 📋 UNSPSC CODES (For eMMA, Vendor Registrations, Portals)

**Services:**
- 72000000 — Building & Facility Construction and Maintenance
- 72100000 — Building & Facility Maintenance and Repair
- 72150000 — Specialized Trade Construction & Maintenance
- 76000000 — Industrial Cleaning Services
- 76110000 — Decontamination Services
- 77000000 — Environmental Services (Landscaping, Grounds, Pest Control)
- 77100000 — Environmental Management
- 78000000 — Transportation, Storage & Mail Services
- 78100000 — Mail & Cargo Transport
- 78110000 — Passenger Transport
- 80000000 — Management & Business Professionals & Admin Services
- 80100000 — Management Advisory Services
- 80110000 — Human Resources Services (Staffing)
- 80120000 — Legal Services (Notary)
- 80140000 — Marketing & Distribution
- 81000000 — Engineering & Research Services
- 81100000 — Professional Engineering Services
- 81110000 — Project Management
- 84000000 — Financial & Insurance Services
- 85000000 — Healthcare Services
- 85120000 — Noncore Healthcare Services

**Products:**
- 24000000 — Material Handling & Storage Equipment
- 26000000 — Power Generation & Distribution Equipment
- 31000000 — Manufacturing Components & Supplies
- 39000000 — Lighting & Electrical Equipment
- 40000000 — Distribution & Conditioning Systems (HVAC, Plumbing)
- 41000000 — Laboratory & Measuring Equipment
- 42000000 — Medical Equipment & Supplies
- 46000000 — Defense & Law Enforcement & Security
- 47000000 — Cleaning Equipment & Supplies
- 53000000 — Apparel, Luggage & Personal Care (Uniforms, PPE)

---

## 📝 STANDARD EMAIL SIGNATURE

```
Dee Davis
Owner
Dee Davis Inc.
755 W. Big Beaver Rd., Suite 2020
Troy, Michigan 48084
Phone: 248.376.4550
Email: info@deedavis.biz

EDWOSB | WOSB | WBENC | MBE | WBE | SBE | E-Verify Program Administrator
CAGE Code: 8UMX3 | UEI: HJB4KNYJVGZ1
MI SIGMA VSS: VS0245604
```

---

## 📄 STANDARD FOOTER FOR DOCUMENTS

```
DEE DAVIS INC
755 W. Big Beaver Rd., Suite 2020 | Troy, MI 48084
Phone: 248.376.4550 | Email: info@deedavis.biz
EDWOSB | WOSB | WBENC | MBE | WBE | SBE | E-Verify Program Administrator | CAGE: 8UMX3 | UEI: HJB4KNYJVGZ1
MI SIGMA VSS: VS0245604
```

---

## 🎨 BRANDING ASSETS

**Logo:** `dee davis inc logo.png` (987KB)  
**Location:** `/Users/deedavis/NEXUS BACKEND/BIDS:RESOURCES/dee davis inc logo.png`

**Colors:**
- Primary: Blue gradient (#1e40af to #3b82f6)
- Accent: Professional blue/white scheme

---

## 📋 INSURANCE COVERAGE

**Carrier:** The Hartford — Property and Casualty Insurance Company of Hartford (NAIC# 34690)
**Policy Number:** 76 SBU BS3SZP
**Producer:** AP Intego Insurance Group LLC
**Policy Period:** 04/28/2025 – 04/28/2026
**⚠️ RENEWAL DATE: April 28, 2026 — set reminder 60 days prior (February 27, 2026)**
**Policy Service:** 1-877-287-1316 (Mon–Fri 7am–7pm CT)
**Claims Hotline:** 1-800-327-3636 (24 hours)
**Online Portal:** https://business.thehartford.com
**Mailing Address on Policy:** 1221 Bowers St Unit 2141, Birmingham MI 48012-7084

| Coverage | Limit | Status |
|---|---|---|
| **Commercial General Liability** | $1M per occurrence / $2M aggregate | ACTIVE |
| **Damage to Rented Premises** | $1M per occurrence | ACTIVE |
| **Medical Expense** | $10K per person | ACTIVE |
| **Personal & Advertising Injury** | $1M | ACTIVE |
| **Products-Comp/Op Aggregate** | $2M | ACTIVE |
| **Employment Practices Liability (EPLI)** | $25K each claim / $25K aggregate | ACTIVE |
| **Blanket Additional Insured** | By contract endorsement (Form SL 30 32) | INCLUDED |
| **Hartford Cyber Center** | Incident response + risk management tools (access code: 952689) | INCLUDED |

**COI Requests:** Can be generated instantly via https://business.thehartford.com
**Additional Insured:** Blanket endorsement included — no need to call Hartford for each sub/client COI.

**⚠️ NOT CURRENTLY COVERED (Consider Adding):**
- Professional Liability / Errors & Omissions (E&O) — recommended for DDI's service model
- Commercial Auto — needed if DDI vehicles used for NEMT, courier, mobile testing
- Workers Compensation — required when DDI has W-2 employees
- Cargo / Inland Marine — for freight brokerage and supply delivery contracts

---

## 🎯 USE THIS FOR:

- ✅ All capability statements
- ✅ All email templates
- ✅ All correspondence
- ✅ All proposals
- ✅ All federal submissions
- ✅ All NEXUS-generated documents

**ALWAYS reference this file when creating new documents to ensure consistency!**

---

## PAST PERFORMANCE & CONTRACT HISTORY

**State of Michigan — Immigration Clerical Assistant (ICA)**
- DDI held a State of Michigan contract as Immigration Clerical Assistants
- Program has since been phased out by the state
- Relevance: Demonstrates direct state government contract experience in immigration services, document processing, and clerical administration
- Supports credibility for: apostille services, immigration document authentication, biometric fingerprinting for immigration, USCIS-related contracts, document preparation services

**Notary Public — State of Michigan**
- Michigan Commissioned Notary Public since April 2005 (20+ years continuous)
- CNTDA — Certified Notary & Trained Document Agent
- NPR — Notary Permit Runner (Certified)

*Note: As DDI wins contracts and builds CPARS history, add each completed contract here with agency, contract number, period of performance, value, and CPARS rating.*

---

---

## 🏥 MICHIGAN CHAMPS — MEDICAID PROVIDER ENROLLMENT

**System:** CHAMPS (Community Health Automated Medicaid Processing System)
**MILogin Access:** milogintp.michigan.gov

### NEMT Provider Enrollment

| Field | Value |
|---|---|
| **Application Number** | **20260323058125** |
| **Provider ID** | **6309049** |
| **Application Type** | Atypical Agency |
| **Business Status** | **ACTIVE — APPROVED** |
| **Eligibility Date Range** | **03/23/2026 — 12/31/2999** |
| **Specialty** | Non-Emergency Transportation Agency / No Subspecialty |
| **Specialty** | NEMT (Non-Emergency Medical Transportation) |
| **NPI** | 1538939111 |
| **Taxonomy Code** | 347E00000X (Transportation Broker) |
| **Ownership Type** | Corporate - Non Charitable |
| **Managing Employee** | Dieasha D. Davis |
| **Date Submitted** | March 22, 2026 |
| **Status** | Submitted for State Review |
| **Previous Application (Rejected)** | 20251210748456 — rejected because wrong provider type ("Group" instead of "Atypical Agency") |

### MCO CREDENTIALING STATUS

| MCO | Status | Vendor ID / Details |
|---|---|---|
| **CareSource** | ✅ **CONTRACT EXECUTED — Apr 28, 2026** | Vendor ID **100000469269** — **NEMT TPA, Wayne + Macomb counties** (Oakland pending). **This is the HAP CareSource Michigan plan** — per Dee: *"caresource is hap, its orange"* — one account, not two. Provider portal active. Dana Drew — Dana.Drew@CareSource.com — 937.926.5848. Brian Grcevich — Brian.Grcevich@CareSource.com — orientation ✅ May 6, 2026. **Scope doc:** `BIDS:RESOURCES/HAP CARESOURCE NEMT NETWORK/CARESOURCE_CONTRACT_SCOPE.md` |
| Molina Healthcare of Michigan | Pending | Troy HQ — same city as DDI |
| **Humana** | 🔄 **CREDENTIALING** | Active credentialing in progress as of Jul 2026 (per Dee). |
| Meridian Health Plan | ⏳ **AWAITING CONTRACT OFFER** | Detroit HQ — largest MI Medicaid MCO. Waiting on Meridian to offer DDI the contract. |
| UnitedHealthcare Community Plan | Pending | |
| Aetna Better Health | Pending | |
| Blue Cross Complete | ⏳ **AWAITING FOLLOW-UP** | Alina Pabin (VP, Provider Network Management) — apabin@mibluecrosscomplete.com — responded 05/06/2026 (30-min intro). **Post–Memorial Day follow-up SENT** early June 2026 — availability weeks of **June 2 & June 9, afternoons ET**; awaiting her follow-up (per Dee, Jul 2026). |
| McLaren Health Plan | Pending | Flint HQ |
| Priority Health Choice | Pending | Grand Rapids |

### ACTIONS NEEDED:

- [x] Submit corrected CHAMPS application as Atypical Agency / NEMT — **SUBMITTED 03/22/2026**
- [x] **APPROVED 03/23/2026** — Provider ID 6309049, Active through 12/31/2999
- [x] **CareSource NEMT contract executed Apr 28, 2026** — Vendor ID 100000469269
- [x] **Orientation with Brian Grcevich (CareSource)** — ✅ SCHEDULED May 6, 2026 1:00 PM ET — Teams meeting
- [ ] **Humana** — credentialing in progress (Jul 2026)
- [ ] **Blue Cross Complete** — awaiting Alina Pabin follow-up
- [ ] **Meridian** — awaiting contract offer
- [ ] **Continue MCO credentialing** — Molina, UHC, Aetna, McLaren, Priority Health
- [ ] **Confirm with CareSource on orientation** — does this contract cover HAP CareSource (Michigan) as well?

### IMPORTANT NOTES:

- DDI initially submitted as "Group" provider type — **WRONG**. Must be "Atypical Agency" with NEMT specialty.
- Email from MDHHS Provider Enrollment Unit (AJT) on 03/22/2026 clarified the correct enrollment path.
- Contact for enrollment questions: **Provider Support 800-979-4662, option 1**
- CHAMPS Provider Enrollment Unit email: MSA-HomeHelpProviders@michigan.gov

### WHAT THIS UNLOCKS:

- Medicaid NEMT provider status in Michigan
- Ability to contract with MCOs for non-emergency medical transportation
- Access to Michigan's $200M+ annual NEMT spend
- Foundation for NEMT brokerage services statewide

---

## 🏥 TEXAS TMHP — PORTAL ACCESS vs. ENROLLMENT (RECORDED)

**System:** TMHP ([tmhp.com](https://www.tmhp.com)) — Texas Medicaid & Healthcare Partnership (administrative services for Texas Medicaid, per HHSC/TMHP scope).

### What we know (Texas HHS notification + Dee confirmation)

| Field | Value |
|-------|-------|
| **Enrollment transaction** | **D19273048** |
| **Portal access** | **Provider Administrator** — automated email from `DONOTREPLY@hhs.texas.gov` (TMHP notices) |
| **Name on notice** | Dieasha Davis |
| **Texas Medicaid enrollment application** | **Not yet submitted** — per Dee (NEXUS update: user confirmed has not applied yet) |
| **Recorded in NEXUS** | May 10, 2026 |

**Plain English:** The TMHP email means you have **portal permissions** on that enrollment transaction (typically to manage **users** linked to a provider identifier workflow). It does **not** mean Texas Medicaid has **approved** Dee Davis Inc. as a provider yet. **Applying** = completing and submitting the Medicaid provider enrollment through TMHP (or as TMHP directs).

**What Provider Administrator typically means:** Administer **users** for the enrollment transaction / provider identifier path in TMHP (“Unlinking a user will restrict all access…”). Still log in and confirm what **D19273048** is (draft, initiated file, etc.).

### Next steps for Dee

1. Log in to **TMHP.com** → locate **D19273048** → note whether it is **empty/draft**, **in progress**, or **submitted** — align with “haven’t applied yet.”
2. When ready: start or continue **Texas Medicaid provider enrollment** in TMHP per the path for your **entity type** (NEMT broker / TPA as Texas classifies it — follow TMHP prompts and any HHSC provider manual).
3. After **submit**: track notices, **effective date**, and **Texas Medicaid Provider Identifier** — then update this section.
4. PDF/screenshot milestones (submitted, pending, approved).

### WHAT THIS SUPPORTS (once enrollment is approved)

- Credentialing with Texas MCOs for **NEMT / HAVEN** TPA work
- Controlled portal access for billing/credentialing staff when you add them

---

*Master Company Information — Michigan CHAMPS section updated March 22, 2026; Texas TMHP portal noted May 10, 2026*  
*Certifications Updated: E-Verify & SWFT Certified (established 2022) documented in master file*  
*CEO personal (email only): 248.376.4550 · Websites & member calls: 855-773-0035 · GV 248.270.8490 forwards to 855*  
*DDI_PROFILE in federal_forecasts_system.py synced with this file — Feb 10, 2026*
*CHAMPS NEMT enrollment submitted 03/22/2026 — Application #20260323058125*

---

## 🏛️ MDHHS PARTNERSHIP — LEAD SAFE ECOSYSTEM

**Status (as of April 23, 2026):** Active partnership development. CWC+DDI pitched a community navigation + program administration model to the MDHHS Environmental Health Bureau. Model was **received positively** by both attendees. Formal follow-up committed within 2 weeks. Local health department introductions committed for 6 target counties.

**Positioning statement (approved):** *"Partner in Michigan's lead-safe ecosystem."* Use this phrasing in all CWC/DDI public materials, the SHIELD `/refer` public intake page, and outbound correspondence with MDHHS and local health departments. Do **not** claim to be an MDHHS contractor, grantee, or subgrantee — the relationship is a **referral partnership**, not a funded contract (yet).

**Operating model (three words, memorable):** **MDHHS refers. CWC navigates. DDI administers.**
- CWC (501c3) — community trust + navigation layer (MIBridges-certified, MDHHS Community Partner)
- DDI (EDWOSB) — program administration + compliance + billing layer
- Cost to MDHHS: **Zero** — every service line funded through existing Medicaid MCO billing, court contracts, federal grant channels, or HRSN/HCBS waiver pathways

**Reference documents (confidential, internal-use only):**
- `GRANT_APPLICATION_PACKAGE/CWC_GRANTS/CWC_DDI_MISSION_ALIGNMENT.html` — grant-ready structural + mission alignment (SHIELD · HAVEN · VITAL)
- `BIDS:RESOURCES/PARTNERSHIP DOCUMENTATIONS/CWC_DDI_MDHHS_Meeting_Brief.pdf` — full 3-page meeting brief (attendees, 8 outcomes, 6 next-steps, contact info)
- `BIDS:RESOURCES/PARTNERSHIP DOCUMENTATIONS/CWC_DDI_Overview_OnePager.pdf` — 3-page one-pager (6 service lines, EHB-specific program fit, 3-point ask)

---

### MDHHS PARTNER CONTACTS

| Contact | Role | Email | Phone | Notes |
|---------|------|-------|-------|-------|
| **Angela Medina** | Care Coordination Section Manager, Division of Environmental Community Services, **Environmental Health Bureau** | MedinaA@michigan.gov | **517-897-5203** | **Primary decision-maker.** Confirmed Apr 23: timing is "perfect" given PA 146 of 2023. Owns referral-pathway decisions and LHD-director intros. |
| **Aimee Surma** | Environmental Health Bureau | SurmaA@michigan.gov | — | Program contact. Surfaced housing + food navigation need (Apr 23). **OOO auto-reply** received early June 2026 (same day as SHIELD follow-up) — back TBD; non-urgent CLPPP: **517-335-8885** / MDHHS-CLPPP@michigan.gov. |

### LOCAL HEALTH DEPARTMENT DIRECTORS (MDHHS-FACILITATED INTROS — INBOUND EXPECTED)

MDHHS committed on Apr 23 to share the CWC+DDI brief + one-pager with LHD directors in the following counties. When introductions arrive, log each director as a separate `Referral_Source_Accounts` record in SHIELD and link the intro email to this partnership record.

| County | Director | Email | Phone | Status |
|--------|----------|-------|-------|--------|
| Wayne | *(pending — MDHHS intro)* | — | — | Awaiting intro from Angela/Aimee |
| Oakland | *(pending — MDHHS intro)* | — | — | Awaiting intro from Angela/Aimee |
| Macomb | *(pending — MDHHS intro)* | — | — | Awaiting intro from Angela/Aimee |
| Genesee | *(pending — MDHHS intro)* | — | — | Awaiting intro from Angela/Aimee |
| Kent (Grand Rapids) | *(pending — MDHHS intro)* | — | — | Awaiting intro from Angela/Aimee |
| Muskegon | *(pending — MDHHS intro)* | — | — | Awaiting intro from Angela/Aimee |

---

### APRIL 23, 2026 MEETING — SUMMARY

**Meeting:** MDHHS Environmental Health Bureau · Microsoft Teams · **3:00–3:30 PM ET**
**Attendees:** Angela Medina + Aimee Surma (MDHHS) · Dieasha D. Davis (CWC+DDI)
**Nature:** CWC+DDI-requested pitch to introduce the community navigation and program administration partnership model. **Not a grant request.**

**What CWC+DDI asked for (5 items):**
1. Formal recognition as a community navigation + program administration partner within MDHHS program referral infrastructure
2. Referral pathway — MDHHS case workers refer enrolled members to CWC by service-line need
3. Introduction to MDHHS Medicaid managed care liaison or MCO contract leads (payer-side)
4. Environmental Health pilot — one EHB program area for a 2026 DDI TPA program
5. Program authorization — **Full multi-year program** starting Wayne County for lead screening navigation + housing stability, with **continuous real-time outcomes reporting**

**What MDHHS committed to (3 items):**
1. Schedule a formal follow-up meeting with CWC+DDI (within 2 weeks)
2. Share the CWC+DDI one-pager and meeting brief with local health department directors in Wayne, Oakland, Macomb, Genesee, Grand Rapids, and Muskegon
3. Facilitate introductions to those LHD directors once they have reviewed the documentation

**Commitment CWC+DDI delivered:**
- Submit meeting brief + one-pager to Angela and Aimee within 24 hours — **✅ DONE: sent 4/23/2026 at 7:04 PM ET to both MedinaA@michigan.gov and SurmaA@michigan.gov**

**Prior credibility anchor (raised during the meeting):** CWC previously participated in Wayne Metro's Lead Screening Outreach Program serving the Pontiac, Michigan area, partnering with Grandparents on the Go and local public schools. Angela acknowledged this history.

---

### MDHHS-SIDE TOOLING TO ALIGN WITH

CWC+DDI's public `/refer` page and navigator AI should reference these state programs as **complements**, never as substitutes:

| Program | URL | How CWC+DDI fits |
|---------|-----|------------------|
| MI Lead Safe — Get Ahead of Lead | https://www.michigan.gov/mileadsafe/get-ahead-of-lead | State-facing info hub on drinking water programs |
| Apply for Home Lead Services | https://www.michigan.gov/mileadsafe/lead-services/apply-for-home-lead-services | State intake that routes families to the correct lead services program. CWC+DDI are the **navigation + admin layer** families receive after they qualify. |

---

### ACTION ITEMS (OWED BY CWC+DDI)

- [x] Submit meeting brief + one-pager to Angela and Aimee within 24 hours — **DONE 4/23 7:04 PM ET**
- [x] **Prepare program proposal documentation** for follow-up meeting — **✅ SENT early May 2026** (full package + Guidde demos)
- [ ] **Schedule formal follow-up meeting** — **June 2026 follow-up email SENT** to Angela/Aimee (meeting + LHD intros). ⏳ Await reply · call Angela **517-897-5203** if no response by ~June 9
- [ ] When LHD-director intros arrive, log each contact as a `Referral_Source_Accounts` record in SHIELD (one per director)
- [ ] Request introduction to MDHHS Medicaid MCO contract leads (payer-side path to sustained reimbursement)

---

*MDHHS Partnership section added April 23, 2026 — post-meeting. Seed script: `seed_shield_referral_source_accounts.py`.*
