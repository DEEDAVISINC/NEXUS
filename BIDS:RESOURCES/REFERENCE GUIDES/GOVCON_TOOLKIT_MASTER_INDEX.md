# GovCon Toolkit — Master Index

**Everything You Need to Win Federal Contracts. Automated. No Excuses.**

**Created:** February 8, 2026  
**Owner:** Dee Davis Inc.

**IDIQ & Task Order Knowledge:** See `IDIQ_GOVCON_KNOWLEDGE.md` in project root for Sources Sought strategy, IDIQ vehicles, task order proposal anatomy, and Recompete Tracker concepts.

---

## THE 7 TOOLS — ALL AUTOMATED IN NEXUS

Every tool auto-generates from Airtable data. No manual copy-paste. Each one is triggered by the workflow step before it.

---

### 1. EMAIL TEMPLATES — AUTO-GENERATED
**What:** Context-aware emails that pull real data from Airtable (opportunity, contact, subcontractor)  
**API Endpoint:** `POST /gpss/generate-email`  
**12 Email Types:** `sb_office_intro`, `co_sources_sought`, `co_presolicitation`, `co_question`, `capstat_intro`, `capstat_to_prime`, `debrief_formal`, `debrief_informal`, `debrief_thanks`, `sub_outreach`, `prime_outreach`, `teaming_followup`  
**Triggered By:** Workflow stage changes, CO outreach system, subcontractor relationship updates  
**Backend:** `GPSSSubcontractorMiner.generate_govcon_email()` in `nexus_backend.py`  
**Reference Guide:** `BIDS:RESOURCES/REFERENCE GUIDES/GOVCON_EMAIL_TEMPLATES.md` (for manual use)

---

### 2. NDA — AUTO-GENERATED
**What:** Pre-filled mutual NDA pulled from subcontractor + opportunity Airtable records  
**API Endpoint:** `POST /gpss/subcontractors/{id}/generate-nda`  
**Auto-Triggered:** When workflow advances and subcontractors are linked (checks compliance, generates if missing)  
**Backend:** `GPSSSubcontractorMiner.generate_nda()` in `nexus_backend.py`  
**Compliance:** Auto-creates tracking record in `GPSS SUBCONTRACTOR COMPLIANCE` table  
**Reference Guide:** `BIDS:RESOURCES/REFERENCE GUIDES/GOVCON_NDA_TEMPLATE.md` (for manual use)

---

### 3. CAPABILITY STATEMENT — AUTO-GENERATED
**What:** HTML + PDF capability statements tailored per opportunity  
**API Endpoint:** `POST /capability-statements/generate`  
**Auto-Triggered:** Pre-solicitation auto-respond pipeline  
**Backend:** `CapabilityStatementSystem` + `forecast_capstat_outreach.py`  
**Templates:** `templates/` folder (VA medical, industrial, construction configs)

---

### 4. PROPOSAL MATRIX — AUTO-GENERATED
**What:** Compliance matrix built from AI analysis of uploaded RFP  
**API Endpoint:** `POST /gpss/opportunities/{id}/proposal-matrix`  
**Auto-Triggered:** When RFP uploaded with GO recommendation, AND when workflow advances to Generate Proposal  
**Backend:** `GPSSSubcontractorMiner.generate_proposal_matrix()` in `nexus_backend.py`  
**Output:** Structured JSON with all requirements, evaluation factors, required docs, critical items flagged  
**Reference Guide:** `BIDS:RESOURCES/REFERENCE GUIDES/PROPOSAL_MATRIX.md` (for understanding the process)

---

### 5. TEAMING AGREEMENT — AUTO-GENERATED
**What:** Pre-filled 12-article teaming agreement from subcontractor + opportunity Airtable data  
**API Endpoint:** `POST /gpss/subcontractors/{id}/generate-teaming-agreement`  
**Input:** Opportunity ID, workshare percentages, task assignments  
**Backend:** `GPSSSubcontractorMiner.generate_teaming_agreement()` in `nexus_backend.py`  
**Compliance:** Auto-creates tracking record in `GPSS SUBCONTRACTOR COMPLIANCE`  
**Reference Guide:** `BIDS:RESOURCES/REFERENCE GUIDES/GOVCON_TEAMING_AGREEMENT_TEMPLATE.md` (for manual use)

---

### 6. GOVCON ROADMAP
**What:** Strategy guides for SAM.gov, set-asides, agency buying behavior  
**Locations:** `EDWOSB_BIG_CONTRACT_HUNTING_GUIDE.md`, `SUBCONTRACTING_MASTER_GUIDE.md`, `SERVICE_CONTRACT_SUB_FRAMEWORK.md`, `CO_OUTREACH_SYSTEM_GUIDE.md`

---

### 7. OPPORTUNITY TRACKER — FULLY AUTOMATED
**What:** Multi-source opportunity tracking with AI scoring  
**Airtable:** `GPSS OPPORTUNITIES` (150+ opportunities, auto-mined)  
**API:** `/gpss/opportunities` with filtering, EDWOSB analytics  
**AI:** Go/No-Go calculator, win probability, evaluator profiling

---

## BONUS TOOLS (Already In NEXUS)

| Tool | Location | What It Does |
|------|----------|-------------|
| Go/No-Go Calculator | API: `/gpss/go-no-go` | Scores opportunity fit before you invest time |
| Evaluator Profiler | API: `/gpss/evaluator-profile` | Profiles the CO's communication style |
| ProposalBio Scorer | API endpoint | Scores your proposal quality (target 75+/100) |
| Subcontractor Mining | `nexus_backend.py` | Auto-searches SAM.gov for qualified subs |
| Compliance Tracker | `GPSS SUBCONTRACTOR COMPLIANCE` table | Tracks W-9s, insurance, NDAs, agreements |
| Quote Comparison | API: `/gpss/quote-comparison` | Side-by-side supplier pricing with AI recommendation |
| RFP Upload & Analysis | API: `/gpss/upload-rfp` | Upload PDF → AI extracts everything → creates opportunity |
| Cap Statement Generator | API: `/capability-statements/generate` | One-click tailored capability statements |
| CO Contact Extraction | `extract_buyer_contacts.py` | Auto-extracts CO info from solicitations |
| Workshare Calculator | `SUBCONTRACTING_MASTER_GUIDE.md` | Verifies 50% self-performance compliance |

---

## THE AUTOMATION CHAIN (How Actions Trigger Actions)

```
RFP UPLOADED → /gpss/upload-rfp
    ├── AUTO: AI analyzes full document
    ├── AUTO: Creates opportunity in Airtable
    ├── AUTO: Extracts & stores CO contacts
    ├── AUTO: Go/No-Go score calculated
    └── AUTO: If GO → Proposal Matrix generated
                  |
                  v
WORKFLOW: "Find Suppliers" → /api/workflow/advance
    ├── AUTO: Searches Database + ThomasNet + Google + GSA
    ├── AUTO: Links suppliers to opportunity
    └── AUTO: If subcontractors linked → NDAs generated
                  |
                  v
WORKFLOW: "Request Quotes" → /api/workflow/advance
    ├── AUTO: Generates RFQ emails for each supplier
    └── AUTO: Sends quote requests
                  |
                  v
WORKFLOW: "Generate Proposal" → /api/workflow/advance
    ├── AUTO: Proposal matrix re-generated with latest data
    ├── AUTO: Intelligent pricing calculated
    └── AUTO: ProposalBio quality score
                  |
                  v
MANUAL TRIGGERS (available anytime):
    /gpss/generate-email                    → Context-aware email (12 types)
    /gpss/subcontractors/{id}/generate-nda  → Pre-filled NDA from Airtable
    /gpss/subcontractors/{id}/generate-teaming-agreement → Full teaming agreement
    /gpss/opportunities/{id}/proposal-matrix → Compliance matrix
    /capability-statements/generate         → Tailored cap statement
```

---

## ALL API ENDPOINTS — QUICK REFERENCE

### Document Generators (NEW):
| Endpoint | Method | What It Does |
|----------|--------|-------------|
| `/gpss/generate-email` | POST | Context-aware GovCon email (12 types) |
| `/gpss/subcontractors/{id}/generate-nda` | POST | Pre-filled NDA from Airtable data |
| `/gpss/subcontractors/{id}/generate-teaming-agreement` | POST | Full teaming agreement |
| `/gpss/opportunities/{id}/proposal-matrix` | POST | Compliance matrix from RFP analysis |

### Existing Automation:
| Endpoint | Method | What It Does |
|----------|--------|-------------|
| `/gpss/upload-rfp` | POST | Upload PDF → Full analysis → Create opportunity → Matrix |
| `/capability-statements/generate` | POST | Tailored cap statements (HTML + PDF) |
| `/api/workflow/opportunity/{id}/advance` | POST | Advance workflow with auto-triggers |
| `/gpss/go-no-go` | POST | Score opportunity fit |
| `/gpss/evaluator-profile` | POST | Profile CO communication style |
| `/gpss/quote-comparison/{id}` | GET | Side-by-side supplier pricing |
| `/gpss/subcontractors/{id}/compliance/check` | POST | Check all compliance docs |

---

*Every tool is automated. Upload → Analyze → Generate → Execute. No manual work unless you choose to.*

---

**Last Updated:** February 8, 2026
