# 🔧 NEXUS TECHNICAL ARCHITECTURE DIAGRAMS

**Detailed technical views of system components and integrations**

---

## 📋 TABLE OF CONTENTS

1. [API Server Architecture](#1-api-server-architecture)
2. [ProposalBio™ Analysis Engine](#2-proposalbio-analysis-engine)
3. [Airtable Integration Layer](#3-airtable-integration-layer)
4. [Cron Job Schedule](#4-cron-job-schedule)
5. [Document Generation Pipeline](#5-document-generation-pipeline)
6. [Email & Notification System](#6-email--notification-system)
7. [Security & Business Rules](#7-security--business-rules)
8. [Deployment Architecture](#8-deployment-architecture)

---

## 1. API SERVER ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         api_server.py (Flask)                            │
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────┐   │
│  │                     ROUTE GROUPS                                │   │
│  │                                                                  │   │
│  │  ┌──────────────────────────────────────────────────────────┐ │   │
│  │  │  OPPORTUNITIES ENDPOINTS                                  │ │   │
│  │  │  GET    /gpss/opportunities                               │ │   │
│  │  │  GET    /gpss/opportunities/<id>                          │ │   │
│  │  │  POST   /gpss/opportunities                               │ │   │
│  │  │  PUT    /gpss/opportunities/<id>                          │ │   │
│  │  │  DELETE /gpss/opportunities/<id>                          │ │   │
│  │  └──────────────────────────────────────────────────────────┘ │   │
│  │                                                                  │   │
│  │  ┌──────────────────────────────────────────────────────────┐ │   │
│  │  │  PROPOSALS ENDPOINTS                                      │ │   │
│  │  │  GET    /gpss/proposals                                   │ │   │
│  │  │  POST   /gpss/proposals  ➜ 🟢 AUTO PROPOSALBIO™          │ │   │
│  │  │  PUT    /gpss/proposals/<id>                              │ │   │
│  │  │  POST   /gpss/proposals/<id>/analyze  (Manual trigger)    │ │   │
│  │  └──────────────────────────────────────────────────────────┘ │   │
│  │                                                                  │   │
│  │  ┌──────────────────────────────────────────────────────────┐ │   │
│  │  │  FORECAST OUTREACH ENDPOINTS (NEW)                        │ │   │
│  │  │  POST /api/forecasts/<id>/generate-capstat-outreach       │ │   │
│  │  │       ➜ Capability Statement + Proactive Letter           │ │   │
│  │  │  POST /api/forecasts/batch-outreach                       │ │   │
│  │  │       ➜ Process High Priority Forecasts                   │ │   │
│  │  └──────────────────────────────────────────────────────────┘ │   │
│  │                                                                  │   │
│  │  ┌──────────────────────────────────────────────────────────┐ │   │
│  │  │  CONTRACTING OFFICER OUTREACH ENDPOINTS                   │ │   │
│  │  │  POST /api/officer-outreach/generate                      │ │   │
│  │  │       ➜ Generate for Closed Opportunity (Reactive)        │ │   │
│  │  │  POST /api/officer-outreach/batch                         │ │   │
│  │  └──────────────────────────────────────────────────────────┘ │   │
│  │                                                                  │   │
│  │  ┌──────────────────────────────────────────────────────────┐ │   │
│  │  │  DOCUMENT ASSEMBLY ENDPOINTS                              │ │   │
│  │  │  POST /api/assemble-bid-package                           │ │   │
│  │  │  POST /api/generate-rfp                                   │ │   │
│  │  └──────────────────────────────────────────────────────────┘ │   │
│  │                                                                  │   │
│  │  ┌──────────────────────────────────────────────────────────┐ │   │
│  │  │  SUPPLIER RFQ ENDPOINTS                                   │ │   │
│  │  │  POST /api/generate-supplier-rfq                          │ │   │
│  │  │       ⚠️ NEVER REVEAL BUYER TO SUPPLIER!                  │ │   │
│  │  └──────────────────────────────────────────────────────────┘ │   │
│  │                                                                  │   │
│  │  ... (20+ more endpoint groups)                                 │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────┐   │
│  │                     MIDDLEWARE                                  │   │
│  │  • CORS (Cross-Origin Resource Sharing)                        │   │
│  │  • Authentication (if enabled)                                 │   │
│  │  • Request Logging                                             │   │
│  │  • Error Handling                                              │   │
│  └────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────┐   │
│  │                   SERVICE INTEGRATIONS                          │   │
│  │                                                                  │   │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌──────────┐│   │
│  │  │ Airtable   │  │ProposalBio │  │ Document   │  │  Email   ││   │
│  │  │   Client   │  │  Service   │  │  Assembly  │  │  Service ││   │
│  │  └────────────┘  └────────────┘  └────────────┘  └──────────┘│   │
│  │                                                                  │   │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌──────────┐│   │
│  │  │   RFP      │  │ Capability │  │  Calendar  │  │   PDF    ││   │
│  │  │ Generator  │  │ Statement  │  │  Service   │  │Generator ││   │
│  │  └────────────┘  └────────────┘  └────────────┘  └──────────┘│   │
│  └────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────┐   │
│  │                    ENVIRONMENT CONFIG                           │   │
│  │  • AIRTABLE_API_KEY                                             │   │
│  │  • AIRTABLE_BASE_ID                                             │   │
│  │  • OPENAI_API_KEY                                               │   │
│  │  • SAM_GOV_API_KEY                                              │   │
│  │  • USER_EMAIL                                                   │   │
│  │  • SMTP settings                                                │   │
│  └────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 2. PROPOSALBIO™ ANALYSIS ENGINE

```
┌────────────────────────────────────────────────────────────────────────┐
│                    ProposalBio™ Analysis Engine                         │
│                    proposalbio_module.py                                │
└────────────────────────────────────────────────────────────────────────┘

INPUT: Document Text + Metadata
  ↓
┌────────────────────────────────────────────────────────────────────────┐
│                         ProposalBioAnalyzer                             │
└────────────────────────────────────────────────────────────────────────┘
  ↓
  ├─→ [Biohack #1: Mirror Neuron]
  │   ├─ Analyze: Regional tone matching
  │   ├─ Detect: Agency type (federal/state/local)
  │   ├─ Check: Formal language count
  │   ├─ Score: 0-10
  │   └─ Output: {"score": 8.5, "details": "...", "recommendation": "..."}
  │
  ├─→ [Biohack #2: Cognitive Ease]
  │   ├─ Analyze: Readability & white space
  │   ├─ Calculate: Avg words per sentence
  │   ├─ Calculate: Flesch-Kincaid reading level
  │   ├─ Check: White space ratio
  │   ├─ Score: 0-10
  │   └─ Output: {"score": 7.2, "details": "...", "recommendation": "..."}
  │
  ├─→ [Biohack #3: Reciprocity Anchor]
  │   ├─ Analyze: Offering value before asking
  │   ├─ Detect: Phrases like "enclosed", "attached", "provide"
  │   ├─ Score: 0-10
  │   └─ Output: {"score": 9.0, "details": "...", "recommendation": "..."}
  │
  ├─→ [Biohack #4: Loss Aversion]
  │   ├─ Analyze: Risk mitigation language
  │   ├─ Detect: "guarantee", "protect", "ensure", "prevent"
  │   ├─ Score: 0-10
  │   └─ Output: {"score": 6.5, "details": "...", "recommendation": "..."}
  │
  ├─→ [Biohack #5: Social Proof]
  │   ├─ Analyze: Past performance evidence
  │   ├─ Detect: Client names, statistics, success stories
  │   ├─ Count: Quantified achievements
  │   ├─ Score: 0-10
  │   └─ Output: {"score": 8.0, "details": "...", "recommendation": "..."}
  │
  ├─→ [Biohack #6: Authority Signal]
  │   ├─ Analyze: Credibility indicators
  │   ├─ Detect: Certifications (EDWOSB, WOSB, MBE, WBE)
  │   ├─ Check: CAGE code, UEI, DUNS mentions
  │   ├─ Score: 0-10
  │   └─ Output: {"score": 9.5, "details": "...", "recommendation": "..."}
  │
  ├─→ [Biohack #7: Name Recognition]
  │   ├─ Analyze: Client name repetition
  │   ├─ Count: Agency name mentions (target: 3-5)
  │   ├─ Check: Officer name usage
  │   ├─ Score: 0-10
  │   └─ Output: {"score": 7.0, "details": "...", "recommendation": "..."}
  │
  ├─→ [Biohack #8: Specificity Bias]
  │   ├─ Analyze: Concrete details vs. vague language
  │   ├─ Count: Specific numbers, dates, quantities
  │   ├─ Detect: Vague words ("many", "several", "some")
  │   ├─ Score: 0-10
  │   └─ Output: {"score": 8.8, "details": "...", "recommendation": "..."}
  │
  ├─→ [Biohack #9: Commitment Device]
  │   ├─ Analyze: Clear next steps
  │   ├─ Detect: Action items, timelines, deliverables
  │   ├─ Check: Call-to-action clarity
  │   ├─ Score: 0-10
  │   └─ Output: {"score": 7.5, "details": "...", "recommendation": "..."}
  │
  └─→ [Biohack #10: Peak-End Rule]
      ├─ Analyze: Opening & closing strength
      ├─ Check: Strong opening hook
      ├─ Check: Memorable closing
      ├─ Detect: Key phrases in first/last paragraphs
      ├─ Score: 0-10
      └─ Output: {"score": 8.2, "details": "...", "recommendation": "..."}
  
  ↓
┌────────────────────────────────────────────────────────────────────────┐
│                      COMPOSITE SCORE CALCULATION                        │
│                                                                         │
│  Sum all biohack scores: 8.5 + 7.2 + 9.0 + 6.5 + 8.0 + 9.5 + 7.0      │
│                          + 8.8 + 7.5 + 8.2 = 80.2                      │
│                                                                         │
│  Composite Score = (80.2 / 10) * 10 = 80.2                            │
│  (Converts 0-10 avg to 0-100 scale)                                   │
└────────────────────────────────────────────────────────────────────────┘
  ↓
┌────────────────────────────────────────────────────────────────────────┐
│                         STATUS DETERMINATION                            │
│                                                                         │
│  IF Composite Score >= 75 AND All Biohacks >= 6:                      │
│      Status = "PASSING"                                                │
│      Badge = "🟢 HIGH QUALITY"                                         │
│      Lock = "UNLOCKED" (for proposals)                                │
│                                                                         │
│  ELIF Composite Score >= 60:                                           │
│      Status = "GOOD"                                                   │
│      Badge = "🟡 GOOD QUALITY"                                         │
│      Lock = "UNLOCKED" (for proposals)                                │
│                                                                         │
│  ELSE:                                                                  │
│      Status = "NEEDS_IMPROVEMENT"                                      │
│      Badge = "🔴 NEEDS IMPROVEMENT"                                    │
│      Lock = "LOCKED" (for proposals)                                  │
└────────────────────────────────────────────────────────────────────────┘
  ↓
┌────────────────────────────────────────────────────────────────────────┐
│                      IMPROVEMENT RECOMMENDATIONS                        │
│                                                                         │
│  IF Status != "PASSING":                                               │
│      For each biohack with score < 6:                                  │
│          Add recommendation to improvement list                        │
│      Sort by lowest score first                                        │
│      Return top 3 most critical improvements                          │
└────────────────────────────────────────────────────────────────────────┘
  ↓
OUTPUT:
{
  "composite_score": 80.2,
  "overall_status": "PASSING",
  "quality_badge": "🟢 HIGH QUALITY",
  "lock_status": "UNLOCKED",
  "biohack_scores": {
    "mirror_neuron": {"score": 8.5, "details": "...", "recommendation": "..."},
    "cognitive_ease": {"score": 7.2, "details": "...", "recommendation": "..."},
    ... (all 10 biohacks)
  },
  "improvements": [
    "Add more risk mitigation language (Loss Aversion: 6.5/10)",
    "Mention agency name 2 more times (Name Recognition: 7.0/10)"
  ],
  "analyzed_at": "2026-01-31T14:23:45Z",
  "document_type": "proposal",
  "metadata": {...}
}
```

---

## 3. AIRTABLE INTEGRATION LAYER

```
┌────────────────────────────────────────────────────────────────────────┐
│                         AirtableClient Class                            │
│                         (airtable_client.py)                            │
└────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐
│  Configuration  │
├─────────────────┤
│ API_KEY: env    │
│ BASE_ID: env    │
│ Timeout: 30s    │
│ Retry: 3 times  │
└─────────────────┘
        ↓
┌────────────────────────────────────────────────────────────────────────┐
│                           CORE METHODS                                  │
│                                                                         │
│  get_record(table_name, record_id)                                     │
│    ├─ Build URL: https://api.airtable.com/v0/{BASE}/{TABLE}/{ID}     │
│    ├─ Add headers: Authorization: Bearer {API_KEY}                    │
│    ├─ Send GET request                                                │
│    ├─ Parse JSON response                                             │
│    └─ Return: {"id": "...", "fields": {...}, "createdTime": "..."}   │
│                                                                         │
│  create_record(table_name, fields)                                     │
│    ├─ Build URL: https://api.airtable.com/v0/{BASE}/{TABLE}          │
│    ├─ Prepare body: {"fields": {...}}                                │
│    ├─ Send POST request                                               │
│    ├─ Parse JSON response                                             │
│    └─ Return: {"id": "rec...", "fields": {...}}                      │
│                                                                         │
│  update_record(table_name, record_id, fields)                          │
│    ├─ Build URL: https://api.airtable.com/v0/{BASE}/{TABLE}/{ID}     │
│    ├─ Prepare body: {"fields": {...}}                                │
│    ├─ Send PATCH request                                              │
│    └─ Return: Updated record                                          │
│                                                                         │
│  search_records(table_name, formula=None, view=None)                   │
│    ├─ Build URL with query params                                     │
│    ├─ Add filterByFormula if provided                                 │
│    ├─ Add view if provided                                            │
│    ├─ Handle pagination (pageSize=100)                                │
│    ├─ Loop through all pages                                          │
│    └─ Return: List of all records                                     │
│                                                                         │
│  delete_record(table_name, record_id)                                  │
│    ├─ Build URL                                                        │
│    ├─ Send DELETE request                                             │
│    └─ Return: {"deleted": true, "id": "..."}                         │
└────────────────────────────────────────────────────────────────────────┘
        ↓
┌────────────────────────────────────────────────────────────────────────┐
│                        ERROR HANDLING                                   │
│                                                                         │
│  Rate Limiting (429):                                                  │
│    ├─ Wait 30 seconds                                                 │
│    └─ Retry request                                                   │
│                                                                         │
│  Network Errors (500, 503):                                            │
│    ├─ Exponential backoff (1s, 2s, 4s)                               │
│    └─ Max 3 retries                                                   │
│                                                                         │
│  Invalid Data (400, 422):                                              │
│    ├─ Log error details                                               │
│    └─ Raise exception with message                                    │
└────────────────────────────────────────────────────────────────────────┘
        ↓
┌────────────────────────────────────────────────────────────────────────┐
│                    TABLE-SPECIFIC HELPERS                               │
│                                                                         │
│  get_opportunity(opp_id)                                               │
│    └─ Wrapper for get_record('GPSS OPPORTUNITIES', opp_id)           │
│                                                                         │
│  create_proposal(opportunity_id, proposal_data)                        │
│    ├─ Validate required fields                                        │
│    ├─ Link to opportunity: [opportunity_id]                          │
│    └─ Create record in GPSS Proposals                                │
│                                                                         │
│  get_high_priority_opportunities()                                     │
│    └─ search_records('GPSS OPPORTUNITIES',                           │
│                       formula="AND({Status}='New',                    │
│                                    {Fit Score}>=80)")                  │
│                                                                         │
│  get_forecasts_needing_outreach()                                      │
│    └─ search_records('Federal Forecasts',                            │
│                       formula="AND({Fit Score}>=80,                   │
│                                    {Outreach Status}='Not Contacted',│
│                                    {Officer Email}!='')")             │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 4. CRON JOB SCHEDULE

```
TIME      JOB                          FREQUENCY    SCRIPT
─────────────────────────────────────────────────────────────────────────
06:00 AM  Opportunity Mining           Daily        nexus_backend.py
          ├─ SAM.gov
          ├─ State Portals
          ├─ BidNet
          └─ DemandStar

06:15 AM  Federal Forecast Mining      Daily        federal_forecasts_system.py
          ├─ SAM.gov Pre-Solicitations
          ├─ NASA Forecasts
          └─ GSA Schedules

06:30 AM  Calendar Automation          Daily        calendar_automation.py
          ├─ Check upcoming deadlines
          ├─ Generate .ics files
          └─ Send reminders (7, 3, 1 day)

07:00 AM  Closed Opp Outreach          Daily        contracting_officer_outreach.py
          ├─ Find newly closed opps
          ├─ Generate intro letters
          ├─ ProposalBio™ analysis
          └─ Save to Officer Outreach

08:00 AM  Invoice Auto-Generation      Daily        vertex_invoice_system.py
          ├─ Find completed deliveries
          ├─ Generate invoices
          ├─ Send to clients
          └─ Track payment status

09:00 AM  Follow-Up Reminders          Daily        follow_up_system.py
          ├─ Check Officer Outreach dates
          ├─ Identify 10-day follow-ups
          └─ Send reminder emails

12:00 PM  Inventory Check              Daily        fulfillment_inventory.py
          ├─ Check stock levels
          ├─ Alert for low inventory
          └─ Suggest reorders

04:00 PM  Daily Summary Report         Daily        daily_summary.py
          ├─ Compile all activity
          ├─ Generate report
          └─ Email to user

11:00 PM  Database Backup              Daily        backup_system.py
          └─ Backup critical data

SUNDAY    Weekly Analytics Report      Weekly       analytics_report.py
08:00 AM  ├─ Win/loss analysis
          ├─ ProposalBio™ correlation
          ├─ Financial summary
          └─ Forecast accuracy

1st       Monthly Financial Close      Monthly      financial_close.py
09:00 AM  ├─ Revenue summary
          ├─ Expense summary
          ├─ Profitability analysis
          └─ Tax prep data
```

---

## 5. DOCUMENT GENERATION PIPELINE

```
                    DOCUMENT GENERATION PIPELINE
                    ============================

INPUT: Request (Capability Statement, RFP, RFQ, Invoice, Proposal)
  ↓
┌────────────────────────────────────────────────────────────────────────┐
│ Step 1: DATA COLLECTION                                                │
│   ├─ Get record from Airtable (opportunity, forecast, contract, etc.) │
│   ├─ Get company info (from COMPANY_DOCUMENTS/ or env vars)           │
│   ├─ Get certifications (EDWOSB, WOSB, MBE, WBE)                     │
│   ├─ Get past performance (from CONTRACTS table)                      │
│   └─ Get products/suppliers if applicable                             │
└────────────────────────────────────────────────────────────────────────┘
  ↓
┌────────────────────────────────────────────────────────────────────────┐
│ Step 2: TEMPLATE SELECTION                                             │
│   ├─ Determine document type (capstat, rfp, rfq, invoice, etc.)      │
│   ├─ Determine client type (federal, state, local, commercial)       │
│   ├─ Select appropriate template:                                     │
│   │   • capability_statement_template.html                            │
│   │   • rfp_template.html                                             │
│   │   • rfq_template.html                                             │
│   │   • invoice_template.html                                         │
│   └─ Load template file                                               │
└────────────────────────────────────────────────────────────────────────┘
  ↓
┌────────────────────────────────────────────────────────────────────────┐
│ Step 3: VARIABLE REPLACEMENT                                           │
│   ├─ Replace {{COMPANY_NAME}} → "DEE DAVIS INC"                      │
│   ├─ Replace {{CLIENT_NAME}} → agency/client name                    │
│   ├─ Replace {{DATE}} → current date formatted                       │
│   ├─ Replace {{CAGE_CODE}} → "8UMX3"                                 │
│   ├─ Replace {{UEI}} → "HJB4KNYJVGZ1"                                │
│   ├─ Replace {{DUNS}} → "002636755"                                  │
│   ├─ Replace {{TAX_ID}} → "84-4114181"                               │
│   ├─ Replace {{RFQ_NUMBER}} → solicitation number                    │
│   ├─ Replace {{DESCRIPTION}} → project description                   │
│   └─ ... (50+ variables depending on template)                        │
└────────────────────────────────────────────────────────────────────────┘
  ↓
┌────────────────────────────────────────────────────────────────────────┐
│ Step 4: DYNAMIC CONTENT GENERATION                                     │
│   ├─ Past Performance Section:                                        │
│   │   • Query CONTRACTS table                                         │
│   │   • Filter by award status = 'Won'                               │
│   │   • Select relevant contracts (similar to current opportunity)   │
│   │   • Format as bullet points with agency, value, date            │
│   │                                                                    │
│   ├─ Certification Section:                                           │
│   │   • Add EDWOSB certification details                             │
│   │   • Add WOSB certification details                               │
│   │   • Add MBE/WBE if applicable                                    │
│   │   • Include certification numbers and dates                      │
│   │                                                                    │
│   ├─ Product/Service Section (if applicable):                         │
│   │   • List products from GPSS PRODUCTS                             │
│   │   • Categorize by type                                           │
│   │   • Include specifications                                       │
│   │                                                                    │
│   └─ Pricing Section (if RFQ/Proposal):                              │
│       • Line item breakdown                                           │
│       • Quantities                                                    │
│       • Unit prices                                                   │
│       • Extended prices                                               │
│       • Total                                                         │
└────────────────────────────────────────────────────────────────────────┘
  ↓
┌────────────────────────────────────────────────────────────────────────┐
│ Step 5: HTML GENERATION                                                │
│   ├─ Combine template + replaced variables + dynamic content          │
│   ├─ Add CSS styling (inline for PDF compatibility)                  │
│   ├─ Add images (logo, certifications)                               │
│   ├─ Format tables, lists, sections                                  │
│   ├─ Validate HTML (no broken tags)                                  │
│   └─ Save HTML file                                                   │
└────────────────────────────────────────────────────────────────────────┘
  ↓
┌────────────────────────────────────────────────────────────────────────┐
│ Step 6: PDF CONVERSION (WeasyPrint)                                   │
│   ├─ Load HTML file                                                   │
│   ├─ Render to PDF                                                    │
│   │   • Page size: Letter (8.5" x 11")                              │
│   │   • Margins: 0.75" all sides                                    │
│   │   • Headers: Company name + document type                        │
│   │   • Footers: Page numbers + date                                │
│   ├─ Apply fonts (Avenir or fallback to Arial)                      │
│   ├─ Optimize for file size                                          │
│   └─ Save PDF file                                                    │
└────────────────────────────────────────────────────────────────────────┘
  ↓
┌────────────────────────────────────────────────────────────────────────┐
│ Step 7: METADATA & STORAGE                                            │
│   ├─ Generate filename:                                               │
│   │   capstat_NASA_FORECAST_20260131.pdf                             │
│   │   rfq_RCOC_7732_20260131.pdf                                     │
│   │                                                                    │
│   ├─ Save to appropriate folder:                                      │
│   │   • Capability Statements → generated_capability_statements/    │
│   │   • RFPs/RFQs → generated_rfps/                                 │
│   │   • Invoices → generated_invoices/                               │
│   │   • Proposals → GENERATED_QUOTES/                                │
│   │                                                                    │
│   ├─ Update Airtable:                                                 │
│   │   • Add file path to record                                      │
│   │   • Update "Document Generated" field = True                     │
│   │   • Update "Generated Date" = now                                │
│   │                                                                    │
│   └─ Return result:                                                   │
│       {                                                                │
│         "success": true,                                              │
│         "pdf_file": "/path/to/file.pdf",                             │
│         "html_file": "/path/to/file.html",                           │
│         "generated_at": "2026-01-31T14:23:45Z"                       │
│       }                                                                │
└────────────────────────────────────────────────────────────────────────┘

OUTPUT: Generated PDF + HTML files, Airtable updated
```

---

## 6. EMAIL & NOTIFICATION SYSTEM

```
┌────────────────────────────────────────────────────────────────────────┐
│                    EMAIL & NOTIFICATION ARCHITECTURE                    │
└────────────────────────────────────────────────────────────────────────┘

CONFIGURATION (from .env):
  • SMTP_SERVER: smtp.gmail.com
  • SMTP_PORT: 587
  • SMTP_USERNAME: info@deedavis.biz
  • SMTP_PASSWORD: [app password]
  • USER_EMAIL: dee@deedavis.biz

┌────────────────────────────────────────────────────────────────────────┐
│                         EMAIL TYPES                                     │
│                                                                         │
│  1. HIGH PRIORITY ALERTS                                               │
│     Trigger: New high-fit opportunity discovered (score >= 80)        │
│     Subject: 🎯 HIGH PRIORITY Opportunity: [Title]                    │
│     Content: Opportunity details, fit score, why it's good, deadline  │
│     Attachments: None                                                  │
│     Frequency: Immediate (as discovered)                              │
│                                                                         │
│  2. FORECAST ALERTS                                                    │
│     Trigger: High-fit forecast with officer contact (score >= 80)     │
│     Subject: 🔮 HIGH PRIORITY Forecast: [Title]                       │
│     Content: Forecast details, officer info, preparation tips         │
│     Attachments: None                                                  │
│     Frequency: Immediate (as discovered)                              │
│                                                                         │
│  3. DEADLINE REMINDERS                                                 │
│     Trigger: Opportunity deadline approaching                          │
│     Subject: ⏰ Bid Deadline Reminder - [Title]                       │
│     Content: Deadline date, current status, action needed             │
│     Attachments: Calendar .ics file                                   │
│     Frequency: 7 days, 3 days, 1 day before deadline                 │
│                                                                         │
│  4. FOLLOW-UP REMINDERS                                                │
│     Trigger: Officer outreach sent 10 days ago, no response           │
│     Subject: ⏰ Follow-up Reminder - [Agency] Officer Outreach        │
│     Content: Original outreach date, suggested follow-up text         │
│     Attachments: None                                                  │
│     Frequency: 10 days after initial outreach                         │
│                                                                         │
│  5. DAILY SUMMARY                                                      │
│     Trigger: Daily at 4:00 PM                                          │
│     Subject: 📊 Daily NEXUS Summary - [Date]                          │
│     Content: New opps, forecasts, quotes, deliveries, invoices        │
│     Attachments: None                                                  │
│     Frequency: Daily                                                   │
│                                                                         │
│  6. INVOICE NOTIFICATIONS                                              │
│     Trigger: New invoice generated or payment overdue                 │
│     Subject: 💰 Invoice Ready - [Client] - $[Amount]                 │
│     Content: Invoice details, payment terms, client contact           │
│     Attachments: Invoice PDF                                          │
│     Frequency: On invoice creation, then reminders at 7/14/21 days   │
│                                                                         │
│  7. SYSTEM ERRORS                                                      │
│     Trigger: Critical system failure (cron job, API error, etc.)      │
│     Subject: 🚨 NEXUS System Error - [Error Type]                     │
│     Content: Error details, stack trace, affected systems             │
│     Attachments: Error log file                                       │
│     Frequency: Immediate (on error)                                   │
└────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────┐
│                      EMAIL SENDING FLOW                                 │
│                                                                         │
│  1. Trigger Event (opportunity discovered, deadline approaching, etc.) │
│     ↓                                                                   │
│  2. Gather Data (from Airtable, system state, etc.)                   │
│     ↓                                                                   │
│  3. Build Email Content                                                │
│     ├─ Subject line (with emoji for visual scanning)                  │
│     ├─ Formatted body (HTML or plain text)                            │
│     ├─ Call-to-action (link to Airtable, download, etc.)             │
│     └─ Attachments if needed                                          │
│     ↓                                                                   │
│  4. Send via SMTP                                                      │
│     ├─ Connect to SMTP server                                         │
│     ├─ Authenticate                                                    │
│     ├─ Compose MIME message                                           │
│     ├─ Send                                                            │
│     └─ Handle errors (retry 3 times, then log failure)               │
│     ↓                                                                   │
│  5. Log Result                                                         │
│     ├─ Success: Log to email_log.txt                                  │
│     └─ Failure: Log to error_log.txt + alert admin                   │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 7. SECURITY & BUSINESS RULES

```
┌────────────────────────────────────────────────────────────────────────┐
│                        CRITICAL BUSINESS RULE                           │
│                   ⚠️ NEVER REVEAL BUYER TO SUPPLIER ⚠️                 │
└────────────────────────────────────────────────────────────────────────┘

IMPLEMENTATION:

  ┌─────────────────────────────────────────────────────────────────────┐
  │  Supplier RFQ Generation (rfp_generator_api.py)                     │
  │                                                                      │
  │  BEFORE sending to supplier:                                        │
  │    ├─ REMOVE: Client/agency name                                   │
  │    ├─ REMOVE: Solicitation number                                  │
  │    ├─ REMOVE: Procurement officer name                             │
  │    ├─ REMOVE: Specific delivery address with client name          │
  │    ├─ REPLACE: With generic terms:                                 │
  │    │   • "Michigan municipal client"                               │
  │    │   • "Federal client"                                          │
  │    │   • "Government client in Illinois"                           │
  │    │   • "Metro Detroit area" (not specific address)              │
  │    └─ VALIDATION: Scan for client identifiers before sending       │
  │                                                                      │
  │  def sanitize_for_supplier(text, opportunity):                      │
  │      # Remove any mention of client                                │
  │      text = text.replace(opportunity['agency'], 'government client')│
  │      text = text.replace(opportunity['solicitation_number'], '')   │
  │      # ... more sanitization ...                                    │
  │      return text                                                    │
  └─────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────┐
│                        SECURITY MEASURES                                │
│                                                                         │
│  API KEY PROTECTION:                                                   │
│    • All API keys in .env (never hardcoded)                           │
│    • .env in .gitignore (never committed)                             │
│    • Rotate keys every 90 days                                        │
│                                                                         │
│  AIRTABLE SECURITY:                                                    │
│    • Personal access tokens (not API keys)                            │
│    • Scoped permissions (read/write only needed tables)               │
│    • IP whitelist if possible                                         │
│                                                                         │
│  API SERVER SECURITY:                                                  │
│    • CORS configured (only allow frontend domain)                     │
│    • Rate limiting (prevent abuse)                                    │
│    • Input validation (prevent injection attacks)                     │
│    • HTTPS only in production                                         │
│                                                                         │
│  DATA PROTECTION:                                                      │
│    • Client data never shared with suppliers                          │
│    • PII (personally identifiable info) handled carefully             │
│    • Regular backups                                                   │
│    • Secure file storage (proper permissions)                         │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 8. DEPLOYMENT ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      CURRENT DEPLOYMENT (Local)                          │
└─────────────────────────────────────────────────────────────────────────┘

  LOCAL MACHINE (Mac)
  ├─ Python 3.13
  ├─ Virtual Environment
  ├─ Cron Jobs (launchd on macOS)
  ├─ Flask API Server (development mode)
  ├─ React Frontend (development mode)
  └─ File Storage (local directories)

  EXTERNAL SERVICES:
  ├─ Airtable (cloud database)
  ├─ OpenAI API (GPT-4)
  ├─ SAM.gov API
  └─ Email (SMTP via Gmail)

┌─────────────────────────────────────────────────────────────────────────┐
│                     PRODUCTION DEPLOYMENT (Future)                       │
└─────────────────────────────────────────────────────────────────────────┘

  ┌──────────────────────────────────────────────────────────────────────┐
  │                          WEB SERVER                                   │
  │  (PythonAnywhere, Heroku, AWS, DigitalOcean, etc.)                  │
  │                                                                       │
  │  ┌────────────────────────────────────────────────────────────────┐ │
  │  │  BACKEND (Python Flask)                                         │ │
  │  │  • Gunicorn WSGI server                                         │ │
  │  │  • Multiple workers                                             │ │
  │  │  • Auto-restart on crash                                        │ │
  │  │  • HTTPS (SSL certificate)                                      │ │
  │  └────────────────────────────────────────────────────────────────┘ │
  │                                                                       │
  │  ┌────────────────────────────────────────────────────────────────┐ │
  │  │  FRONTEND (React)                                               │ │
  │  │  • Built static files (npm run build)                           │ │
  │  │  • Served by Nginx                                              │ │
  │  │  • CDN for assets (CloudFlare)                                  │ │
  │  └────────────────────────────────────────────────────────────────┘ │
  │                                                                       │
  │  ┌────────────────────────────────────────────────────────────────┐ │
  │  │  SCHEDULED JOBS                                                 │ │
  │  │  • Cron jobs or Celery workers                                  │ │
  │  │  • Redis for job queue                                          │ │
  │  │  • Monitoring (Sentry, LogDNA)                                  │ │
  │  └────────────────────────────────────────────────────────────────┘ │
  │                                                                       │
  │  ┌────────────────────────────────────────────────────────────────┐ │
  │  │  FILE STORAGE                                                   │ │
  │  │  • AWS S3 or similar                                            │ │
  │  │  • Generated PDFs, HTMLs                                        │ │
  │  │  • Backups                                                      │ │
  │  └────────────────────────────────────────────────────────────────┘ │
  └──────────────────────────────────────────────────────────────────────┘

  EXTERNAL SERVICES (same as local):
  ├─ Airtable (cloud database)
  ├─ OpenAI API (GPT-4)
  ├─ SAM.gov API
  └─ Email (SMTP via Gmail or SendGrid)

  MONITORING & LOGGING:
  ├─ Application monitoring (Sentry)
  ├─ Server monitoring (New Relic, DataDog)
  ├─ Log aggregation (LogDNA, Papertrail)
  └─ Uptime monitoring (Pingdom, UptimeRobot)
```

---

## 📌 TECHNICAL NOTES

### Performance Optimizations
- Airtable requests cached for 5 minutes
- Batch API calls where possible
- Async operations for long-running tasks
- ProposalBio™ analysis runs non-blocking

### Scalability Considerations
- Airtable API rate limits: 5 requests/second
- OpenAI API rate limits: Monitor usage
- Queue system for batch operations
- Horizontal scaling for API server

### Monitoring & Alerts
- Error tracking with detailed logs
- Performance metrics collection
- Automated alerts for failures
- Daily health check reports

---

**These technical diagrams show the complete internal architecture of NEXUS!**
