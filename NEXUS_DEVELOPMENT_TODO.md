# NEXUS DEVELOPMENT TODO

**Last updated: February 20, 2026**

---

## SYSTEM BUILD — HIGH PRIORITY

### 1. Auto Bid Folder Creation
**Status:** Design complete, not implemented
**Time:** 30 min (basic) | 2-3 hours (full)
**Files:** `NEXUS_AUTO_BID_FOLDERS.md`

- Auto-creates folder when opportunity added
- Downloads solicitation PDF
- Generates strategy docs
- Updates Airtable with folder path

**Implementation:**
1. Add `create_bid_folder()` to `nexus_backend.py`
2. Add API endpoint `/opportunities/create-folder`
3. Create Airtable automation (trigger on new record)
4. Test with sample opportunity

### 2. NEXUS Pricing Automation
**Status:** Design complete, not implemented
**Time:** 2-3 hours
**Files:** `NEXUS_PRICING_AUTOMATION_SIMPLE.md`

- Calculate pricing with markup (one click)
- Auto-fill bid forms
- Generate submission emails

### 3. Auto Email Parsing for Solicitations
**Status:** Not started
- Extract solicitation details from emails automatically

### 4. AI Bid Analysis (Go/No-Go)
**Status:** Not started
- Auto-analyze if solicitation is worth pursuing

---

## AIRTABLE — OUTSTANDING TASKS

### 5. Add Fields to Existing Tables (~20 min)
**Status:** Documented in `AIRTABLE_FINAL_TODO_JAN_27.md`, not yet completed
- [ ] VENDOR PORTAL: Add 8 fields (Portal URL, Type, Status, etc.)
- [ ] Mining Targets: Add 9 fields (Target URL, Type, Frequency, etc.)
- [ ] Opportunities: Add 5 document package fields
- [ ] Opportunities: Add 3 capability statement fields
- [ ] SUBCONTRACTORS: Add 4 compliance fields

### 6. Create Quote Requests Table (~15-20 min)
**Status:** Not created yet
- New table with 17 fields for tracking supplier quote requests and follow-ups

---

## GSA MULTIPLE AWARD SCHEDULE — ALL SECTORS

### 7. GSA MAS Application (Multi-SIN)
**Status:** Research complete, not started
**Priority:** STRATEGIC — one application opens permanent federal sales channel across ALL DDI lanes
**Timeline:** 6-12 months from start to award | 20-year contract term
**Decision:** Evaluate hiring GSA consultant ($5K-15K, cuts timeline in half) vs. self-submit

**Phase 1 SINs (Initial Application — strongest past performance):**

| SIN | Service Lane | Why Phase 1 |
|---|---|---|
| 561730 | Grounds Maintenance | Already bidding, strongest lane |
| 492110 | Courier / Package Delivery | DOT + MC numbers in hand |
| 561210FAC | Facilities Maintenance & Repair | Subcontractor model ready |
| 531 | Employee Relocation Solutions | Mortgage broker license + agent pool |

**Phase 2 SINs (Modification after award):**

| SIN | Service Lane | Notes |
|---|---|---|
| 621 II | Drug Testing / Lab Services | Building past performance now (Georgia DOAS, etc.) |
| 485 | Ground Transportation / NEMT | Sub-based, need past performance |
| 561720 | Janitorial Services | Natural extension of facilities |
| 492210SB | Local Courier Delivery | Extension of courier lane |
| 531210 | Real Estate Agents/Brokers | Lease coordination |
| Product SINs | Industrial/Medical Supply Reselling | TBD based on wins |

**Steps to complete:**
- [ ] Complete "Pathways to Success" training (free, 3-4 hours, required before applying)
- [ ] Complete readiness assessment (required within past year)
- [ ] Gather 2 years of financial statements (or use Startup Springboard if under 2 years)
- [ ] Develop commercial price list for Phase 1 services
- [ ] Collect 2-3 past performance references per SIN (government or commercial)
- [ ] Prepare GSA MAS proposal — 3 volumes: administrative, technical, pricing
- [ ] Register on eOffer system
- [ ] Submit application
- [ ] Negotiate pricing with GSA contracting officer
- [ ] After award: submit modifications to add Phase 2 SINs as past performance builds

### 8. Add All Service Lane NAICS Codes to NEXUS Scanner
**Status:** Not started
**Time:** 30 min

Add these codes so NEXUS catches opportunities across all lanes while GSA application is in progress:

**Real Estate / Relocation:**
- 531120 — Lessors of Nonresidential Buildings
- 531210 — Offices of Real Estate Agents and Brokers
- 531311 — Residential Property Managers
- 531312 — Nonresidential Property Managers

**Facilities:**
- 561210 — Facilities Support Services
- 561720 — Janitorial Services
- 561730 — Grounds Maintenance / Landscaping

**Transportation:**
- 485 — Ground Transportation (NEMT)
- 492110 — Courier and Express Delivery
- 488490 — Other Support Activities for Transportation

**Medical:**
- 621511 — Medical Laboratories (Drug Testing)

**Disaster Relief / Emergency Housing:**
- 624230 — Emergency and Other Relief Services
- 562910 — Remediation Services
- 236220 — Commercial/Institutional Building Construction (reconstruction coordination)

### 9. Formalize Subcontractor Pools by Lane
**Status:** Not started

**Real Estate Agents:**
- Identify agents from existing pool willing to work under DDI prime contracts
- Run through 6-pillar subcontractor framework (NDA, non-compete, COI, etc.)
- Focus on high-PCS-volume regions (military bases, major federal hubs)

**All Other Lanes:**
- Continue building sub pools for drug testing, grounds, courier, janitorial
- Same 6-pillar framework for each
- Track in Airtable GPSS SUBCONTRACTORS

---

## DISASTER RELIEF / EMERGENCY HOUSING LANE

### 10. Register on SAM.gov Disaster Response Registry
**Status:** Not started
**Time:** 15 minutes — DO THIS NOW
**Priority:** Immediate — free registration, puts DDI in front of COs during emergencies

- Register DDI's capabilities: housing coordination, property management, logistics, relocation services
- No application process — voluntary self-registration
- COs use this registry to find vendors FAST during declared disasters

### 11. FEMA Direct Lease Program — Get On The List
**Status:** Research complete, not started
**Priority:** High — this is where mortgage broker license + agent pool = direct revenue

**What it is:** FEMA leases existing residential properties for disaster survivors. They need property management companies and real estate agents to find/manage properties.

**DDI's role:**
- Agents identify available properties in disaster-affected areas
- DDI manages the FEMA contract (compliance, HUD inspections, reporting)
- Properties leased 12-24 months each — recurring revenue
- FEMA pays lease costs, utilities, security deposits

**Steps:**
- [ ] Register on Disaster Response Registry (item #10)
- [ ] Review FEMA Direct Lease program requirements in detail
- [ ] Contact FEMA procurement to express interest as property management company
- [ ] Identify agents in disaster-prone regions (FL, TX, LA, NC, CA)
- [ ] Build FEMA-specific capability statement

### 12. FEMA Advance Contracts — Long-Term Goal
**Status:** Future
**What:** Pre-competed contracts for disaster response services. 104 contracts across 46 mission areas. When disaster hits, you're already approved. Target categories:
- Temporary housing coordination
- Disaster logistics / supply chain support
- Shelter support services

---

## B2B PRIVATE SECTOR OUTREACH — 3D INK AND LIVESCAN CO

### 13. FD-258 Fingerprinting + Drug Testing Outreach Campaign
**Status:** IN PROGRESS — First batch sent Feb 20, 2026
**Tracker:** `FD258_PRIVATE_SECTOR_OUTREACH.md` (master strategy + pricing + all email templates)
**Emails:** `OUTREACH_EMAILS_READY_TO_SEND.md` (immigration) + `OUTREACH_EMAILS_TRUCKING_STAFFING.md` (trucking + staffing) + `OUTREACH_EMAILS_MORTGAGE_INSURANCE.md` (mortgage + insurance + title) + `OUTREACH_EMAILS_HEALTHCARE_TELEHEALTH.md` (healthcare + telehealth + multi-state licensing)

#### BATCH 1 — Immigration Law Firms (SENT Feb 20, 2026)

| # | Target | Email | Contact | Status |
|---|--------|-------|---------|--------|
| 1 | Garmo & Kiste, PLC | info@garmokiste.com | Brian Garmo | ✅ SENT 2/20 |
| 2 | Dobkin Law Group | info@dobkinlawgroup.com | Donald Dobkin | ✅ SENT 2/20 |
| 3 | Jeelani Law Firm | info@jeelani-law.com | General | ✅ SENT 2/20 |
| 4 | McAllister Law Firm | usa@myimmigration.lawyer | Bethany McAllister | ✅ SENT 2/20 |
| 5 | Fragomen | troyinfo@fragomen.com | Alexandra LaCombe | ✅ SENT 2/20 |

#### BATCH 2 — Trucking Companies (SENT Feb 20, 2026)

| # | Target | Email | Location | Status |
|---|--------|-------|----------|--------|
| 6 | TL Transport LLC (91 trucks) | info@tltransportllc.com | Warren | ✅ SENT 2/20 |
| 7 | Ryan Transportation (40+ yrs) | safety@ryantransportation.com | Livonia | ✅ SENT 2/20 |
| 8 | A.D. Transport | info@adtransport.com | Canton | ✅ SENT 2/20 |
| 9 | ADICA Trucking | safety@adicatrucking.com | Detroit | ✅ SENT 2/20 |
| 10 | Midwest Freight Systems | safety@midwestfreightsystems.com | Warren | ⚠️ MAY BE DUPLICATE |

#### BATCH 3 — Staffing Agencies (SENT Feb 20, 2026)

| # | Target | Email | Location | Status |
|---|--------|-------|----------|--------|
| 11 | Qualified Staffing | info@q-staffing.com | Sterling Heights | ✅ SENT 2/20 |
| 12 | Michigan Prime Staff | info@michiganprimestaffing.com | Livonia | ✅ SENT 2/20 |
| 13 | Elwood Staffing | farmingtonhills.mi@elwoodstaffing.com | Farmington Hills | ✅ SENT 2/20 |
| 14 | Statewide Staffing | hr@statewide-staffing.com | Southfield | ✅ SENT 2/20 |
| 15 | Diversified Employment | info@ddiversified.com | Michigan | ✅ SENT 2/20 |

#### BATCH 4 — Insurance & Title (SENT Feb 20, 2026) + Mortgage (PENDING)

| # | Target | Email | Location | Status |
|---|--------|-------|----------|--------|
| 16 | United Wholesale Mortgage | EXISTING CLIENT | Pontiac | ✅ ALREADY CLIENT (Danielle Doebel) |
| 17 | Lending Force LLC | info@lendingfrc.com | Troy (Big Beaver) | ✅ SENT 2/20 |
| 18 | Stateside Lending | info@statesidelending.com | Troy (Big Beaver) | ✅ SENT 2/20 |
| 19 | Swift Home Loans | info@swifthomeloans.com | Birmingham | ✅ SENT 2/20 |
| 20 | FDI Group | info@fdigroup.com | Novi | ✅ SENT 2/20 |
| 21 | Lockton Companies | locktonmichigan@lockton.com | Detroit | ✅ SENT 2/20 |
| 22 | Capital Title (Troy) | troy@capitaltitle.net | Troy | ✅ SENT 2/20 |
| 23 | Capital Title (Southfield) | southfield@capitaltitle.net | Southfield | ✅ SENT 2/20 |
| 24 | Marsh McLennan Agency (BUILDING) | Alexandra.OConnell@marshmma.com | 755 Big Beaver Ste 2300 | ✅ SENT 2/20 |

#### BATCH 5 — Healthcare, Telehealth & Multi-State Licensing (SENT Feb 20, 2026)

**Also sent (added during session):**

| # | Target | Email | Location | Status |
|---|--------|-------|----------|--------|
| — | Kelly Services (Big Beaver HQ) | info@kellyservicesinc.com | Troy | ✅ SENT 2/20 |
| — | Robert Half | troy@accountemps.com | Troy | ✅ SENT 2/20 |
| — | Manpower SE Michigan | staff@manpowermi.com | SE Michigan | ✅ SENT 2/20 |
| — | DMC Credentialing | credentialing@dmc.org | Detroit | ✅ SENT 2/20 |
| — | Henry Ford Provider Affairs | ProviderAffairs@hfhs.org | Detroit | ✅ SENT 2/20 |
| — | Henry Ford West Bloomfield | PV@hfhs.org | West Bloomfield | ✅ SENT 2/20 |
| — | Henry Ford Macomb | MacombMedicalAffairs@hfhs.org | Macomb | ✅ SENT 2/20 |
| — | Trinity Health Oakland | PO-MedStaffServices@trinity-health.org | Oakland | ✅ SENT 2/20 |

| # | Target | Email | Location | Status |
|---|--------|-------|----------|--------|
| 25 | Entech Medical Staffing (WBENC) | medical@teamentech.com | Troy (Crooks Rd) | ✅ SENT 2/20 |
| 26 | Favorite Healthcare Staffing | michigan@favoritestaffing.com | Michigan | ✅ SENT 2/20 |
| 27 | Detroit Harmony Health (telehealth) | Info@DetroitHarmonyHealth.com | Detroit | ✅ SENT 2/20 |
| 28 | Ortele Health (telehealth) | schedule@ortele.com | Detroit | ✅ SENT 2/20 |
| 29 | Telesure (PARTNER - licensing co.) | info@telesure.co | National | ✅ SENT 2/20 |
| 30 | MyMichigan Health CVO | CVO@mymichigan.org | Midland | ✅ SENT 2/20 |
| 31 | Assist 1 Medical Staffing | assist1staffing@gmail.com | Auburn Hills | ✅ SENT 2/20 |

#### BATCH 6 — Defense Contractors, Adoption (NEXT WEEK)

| # | Target | Phone | Contact | Status |
|---|--------|-------|---------|--------|
| 32 | Raytheon/RTX (Troy) | Main switchboard | Facility Security Officer | [ ] PENDING |
| 33 | General Dynamics Land Systems | 586-825-4000 | Facility Security Officer | [ ] PENDING |
| 34 | BAE Systems (Sterling Heights) | Main switchboard | Facility Security Officer | [ ] PENDING |
| 35 | Bethany Christian Services | bethany.org | Adoption Program Director | [ ] PENDING |

#### BATCH 7 — Remaining Immigration Firms

| # | Target | Email / Phone | Contact | Status |
|---|--------|--------------|---------|--------|
| 36 | Shihab Burke, LLC (Troy) | 248-524-0700 | Sam Shihab | [ ] PENDING |
| 37 | Hobballah Legal Group (Dearborn) | myprolawyer.com / 313-443-8999 | Attorney | [ ] PENDING |
| 38 | Dhade & Associates (W. Bloomfield) | detroitimmigration.com / 248-254-3441 | Herman Dhade | [ ] PENDING |
| 39 | Akhtar & Associates (Troy) | sherakhtar.com / 248-828-7900 | Sher Akhtar | [ ] PENDING |
| 40 | Elsharnoby & Associates (Dearborn) | Via website / 313-581-9666 | Attorney | [ ] PENDING |

#### MONDAY FEB 23, 2026 — ACTION LIST

**Lab Accounts & MRO (Open these — all free):**
- [ ] Call LabCorp — 800-833-3984 opt 2 — Ask about BOTH: (1) Open drug testing lab account + order free supplies AND (2) Register 3D Ink as a collection site in their network (get inbound clients)
- [ ] Call CRL (Clinical Reference Lab) — 800-445-6917 — Open account, FormFox e-CCF registration
- [ ] Order supplies from Quest (already have account) — 800-877-7484

**Walk-In Collection Site Networks (Partner accounts — free):**
- [ ] Call Accredited Drug Testing — 800-221-4291 — Free employer account, 37 Detroit locations, same-day walk-in
- [ ] Sign up US Health Testing partner program — ushealthtesting.com/partner-program — Revenue-sharing, 25,000+ sites

**MRO Services (Low/no cost):**
- [ ] Sign up ASAP Programs — asap-programs.com — $0 setup, no contracts, no monthly fees
- [ ] Call National Drug Screening — 866-843-4545 — Ask about BOTH: (1) Reseller Program (TPA backend) AND (2) Join Collection Site Network (get inbound clients routed to 3D Ink)

**Phone Targets (no email — call these):**
- [ ] Bartech (Livonia) — 800-828-4410
- [ ] Aerotek (Royal Oak) — (248) 728-9300
- [ ] Randstad (Troy, Big Beaver!) — (248) 786-5201

**In-Person:**
- [ ] Walk to Fragomen Suite 2050 — in-person intro
- [ ] Walk to Marsh McLennan Suite 2300 — in-person intro

**Procurement / Government Outreach — Land Bank Notary Signing (see LAND_BANK_OUTREACH_MONDAY.md):**
- [ ] Detroit Land Bank — Email mrios@detroitlandbank.org (already drafted in SEND_TO_BUYER)
- [ ] Michigan State Land Bank — Email landbank@michigan.gov
- [ ] Wayne County Land Bank — Email wclbinquiries@waynecounty.com
- [ ] Genesee County Land Bank — Call (810) 257-3088 or contact form
- [ ] Oakland County Land Bank — Email robinsonj@oakgov.com (Jill Robinson)
- [ ] Cuyahoga Land Bank (Cleveland) — Contact form at cuyahogalandbank.org
- [ ] Pittsburgh URA — Email icoleman@ura.org (Ivy Coleman) — Title & Settlement RFQ

#### FOLLOW-UP SCHEDULE
- [ ] Follow up ALL outreach emails — Feb 25, 2026 (5 days after send)
- [ ] Call Danielle Doebel — ask about referrals to UWM broker partners
- [ ] Post Mat Ishbia photo on LinkedIn/website
- [ ] Create 3D Ink services one-pager for follow-up emails
- [ ] Send Batch 3 (defense/adoption) — Feb 25-28, 2026
- [ ] Send Batch 4 (remaining immigration) — Feb 24-26, 2026

#### REVENUE TARGET
- 14 active clients = $31,325/month potential
- Break-even target: 5 clients = ~$11,000/month

---

## BACKLOG

### 14. Voice Commands
"NEXUS, create folder for Detroit Water bid"

---

## COMPLETED

- ✅ Bid folder organization system (manual)
- ✅ Direct answers rule (no fluff)
- ✅ CPS Energy bid completed
- ✅ Subcontractor management framework documented
- ✅ ProposalBio module built
- ✅ Capability statement generator built
- ✅ Quote generator with supplier protection built
- ✅ Real estate / relocation lane research completed (Feb 2026)
- ✅ Disaster relief / emergency housing lane research completed (Feb 2026)

---

*This is the single master TODO. If it's not on this list, it's not being tracked.*
