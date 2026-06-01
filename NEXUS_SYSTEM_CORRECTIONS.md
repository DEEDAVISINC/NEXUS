# NEXUS SYSTEM CORRECTIONS & CLARIFICATIONS

**Fixing system boundaries and manual usability.**

---

## CORRECTION 0: SWFT / DCSA — DDI vs LAKOTA (AUTHORITATIVE)

**Source of truth:** `COMPANY_INFO_MASTER.md` (Federal/Compliance section) · `PARTNERSHIPS/LAKOTA_SOFTWARE_PARTNERSHIP_SUMMARY.md`

### DDI — DO NOT CLAIM SWFT

- **~~SWFT Authorized~~** is **incorrect for Dee Davis Inc.** on marketing, signatures, capability statements, emails, and code defaults.
- **DDI's SWFT access was denied by DCSA (March 2026).** DCSA indicated requirements including **minimum interim Secret clearance** and **Facility Clearance Level (FCL)** for that path.
- **Do not** list “SWFT Authorized,” “SWFT-approved,” or “DCSA SWFT-authorized” **on DDI outbound documents**.

### Lakota — SWFT ACTIVE (partner)

- **Lakota Software IS SWFT-authorized** — Lakota can submit to DCSA SWFT.
- **Internal / ops docs:** “Lakota/SWFT (active)” is correct.
- **DDI primes; Lakota provides SWFT technology and submission** under the platform model.

### Buyer-facing fingerprinting positioning (DDI)

- FD-258 / LiveScan **capture** by DDI
- Electronic submission via **SWFT-authorized technology partner (Lakota)** where contract requires — do not say “DDI is SWFT authorized”
- **Path to future DDI-direct SWFT (if pursued):** win applicable contract → **DD Form 254** → FCL triggers per security process — see master file.

**NEXUS / agents must read `COMPANY_INFO_MASTER.md` before asserting who holds SWFT authority — Lakota yes, DDI no.**

---

## CORRECTION 1: VERTEX Scope

### ❌ WRONG: Forecasting in VERTEX

**VERTEX** = Financial Excellence & Revenue Tracking Executive System

**What VERTEX Actually Does:**
- ✅ Invoice generation from all systems
- ✅ Payment tracking
- ✅ Expense management (subs, suppliers, field agents)
- ✅ Cash flow tracking (actuals, not forecasts)
- ✅ Revenue reconciliation
- ✅ Profitability analysis by business line

**What VERTEX Does NOT Do:**
- ❌ Opportunity forecasting (that's GPSS pipeline)
- ❌ Win probability scoring (that's GPSS AI)
- ❌ Revenue projections (that's GPSS pipeline value)

### ✅ CORRECT: Forecasting Lives in GPSS (Pipeline)

**GPSS** already has:
- Win Probability field (0-100%)
- Pipeline Stage tracking
- Estimated contract values
- AI scoring for likelihood

**Forecasting Report (GPSS generates):**
```
Pipeline Forecast (Next 90 Days)
├── Stage 5 (Submitted): $X (high probability)
├── Stage 4 (Development): $Y (medium probability)
└── Stage 3 (Resourcing): $Z (low probability)

Weighted Forecast: $[X + (Y×0.6) + (Z×0.3)]
```

**VERTEX receives actuals:**
- Won contracts → VERTEX invoices
- Paid invoices → VERTEX tracks cash

---

## CORRECTION 2: DOCUMENTS System Scope

### ❌ WRONG: Documents = Just Storage

**OLD THINKING:**
- DOCUMENTS = File repository
- Generation happens "somewhere else"

### ✅ CORRECT: DOCUMENTS = Generation Engine + Repository

**DOCUMENTS System Actually Does:**

#### 1. **DOCUMENT GENERATION** (Primary Function)
```
INPUT: RFP/Solicitation + Parameters
OUTPUT: Generated documents

Capabilities:
├── Generate Capability Statement
│   ├── Auto-extract logo (base64)
│   ├── Auto-select sector colors
│   ├── Apply ProposalBio (all 10 biohacks)
│   └── Output: HTML → PDF
├── Generate Quote Response/Proposal
│   ├── Compliance matrix auto-built
│   ├── Pricing tables from data
│   ├── Technical approach (AI-written)
│   └── Output: Full proposal package
├── Generate RFQ (Supplier-facing)
│   ├── Buyer protection applied
│   ├── DDI-2026-### numbering
│   └── Output: Safe-to-send RFQ
├── Generate Subcontractor Outreach
│   ├── 6-pillar vetting framework
│   ├── NDA/Agreement templates
│   └── Output: Sub package
└── Generate All Templates
    ├── Workflows use DOCUMENTS API
    └── Unified generation engine
```

#### 2. **DOCUMENT STORAGE** (Secondary Function)
```
All generated docs stored:
├── BIDS:RESOURCES/[BID]/SEND_TO_BUYER/
├── BIDS:RESOURCES/[BID]/SEND_TO_SUPPLIER/
├── CLIENTS/[CLIENT]/CONTRACTS/
└── Archive/retrieval via API
```

#### 3. **DOCUMENT RETRIEVAL**
```
Query: "Get cap statement for VA Dry Ice bid"
├── Searches file system
├── Returns path + content
└── Can regenerate if needed
```

---

## CRITICAL ISSUE: Manual NEXUS Usage (Outside Cursor)

### The Problem

**Current State:**
- NEXUS workflows require Cursor conversation
- "I found a solicitation" → Cursor interprets → executes
- No direct interface to trigger DOCUMENTS generation
- No self-service for manual RFP processing

**User Experience:**
```
❌ Current: Upload RFP → "Can you generate a cap statement?" 
             → Wait for AI → Get document
             
❌ Problem: Requires conversation, not tool-like
```

### The Solution: NEXUS Manual Interface

#### Option 1: **Command-Line Interface (CLI)**

```bash
# Trigger full workflow from terminal
cd "/Users/deedavis/NEXUS BACKEND"
python3 nexus_cli.py --command intake --file "RFP_36C25626R0057.pdf"

# Output:
# ✅ Opportunity scored: 85/100 🔴 BID NOW
# ✅ Folder created: BIDS:RESOURCES/VA DRY ICE/
# ✅ Cap statement generated: SEND_TO_BUYER/...
# ✅ Next: Review and submit

# Generate specific document only
python3 nexus_cli.py --command generate --type capability_statement \
  --agency "VA" --service "Dry Ice Delivery" --sol "36C25626R0057"

# Check status
python3 nexus_cli.py --command status --bid "VA Dry Ice"

# Get today's priorities
python3 nexus_cli.py --command dashboard
```

#### Option 2: **Web Interface (Simple HTML Form)**

```html
<!-- Local web UI - nexus_local.html -->
<form id="generateForm">
  <h2>NEXUS Document Generator</h2>
  
  <select name="document_type">
    <option value="capability_statement">Capability Statement</option>
    <option value="quote_response">Quote Response</option>
    <option value="rfq">Supplier RFQ</option>
    <option value="sub_outreach">Subcontractor Outreach</option>
  </select>
  
  <input type="text" name="agency" placeholder="VA, USACE, DLA, etc.">
  <input type="text" name="service" placeholder="Drug Testing, Courier, etc.">
  <input type="text" name="sol_number" placeholder="36C25626R0057">
  
  <input type="file" name="rfp_file" accept=".pdf,.doc,.txt">
  
  <button type="submit">Generate</button>
</form>

<!-- On submit: Calls nexus_backend.py API, returns generated file path -->
```

#### Option 3: **Keyboard Shortcuts / Quick Actions in Cursor**

```
# .cursor/rules/nexus-quick-commands.mdc

## Magic Commands (Type in chat, no conversation needed)

/intake [file]
→ Triggers full opportunity intake
→ No "Do you want me to...?"
→ Just executes

/cap [agency] [service] [sol#]
→ Generates capability statement only
→ Immediate output

/quote [bid_name]
→ Generates quote response
→ Uses existing bid folder data

/status [bid_name]
→ Returns stage/status instantly
→ No conversational fluff

/dashboard
→ Returns morning brief instantly
→ Lists priorities
```

---

## PROPOSED: NEXUS API ENDPOINTS

### Backend API Structure

```python
# nexus_api.py - Flask/FastAPI endpoints

@app.route('/api/intake', methods=['POST'])
def opportunity_intake():
    """Full workflow: score → folder → docs → airtable"""
    file = request.files['rfp']
    result = execute_full_workflow(file)
    return jsonify({
        'score': result.score,
        'tier': result.tier,
        'folder': result.folder_path,
        'documents': result.generated_files,
        'airtable_id': result.record_id
    })

@app.route('/api/generate/capability', methods=['POST'])
def generate_capability():
    """Generate cap statement only"""
    params = request.json
    doc = documents.generate_capability_statement(
        agency=params['agency'],
        service=params['service'],
        sector=params.get('sector'),  # Auto-detect if not provided
        logo=params.get('logo_base64')  # Auto-extract if not provided
    )
    return jsonify({
        'html_path': doc.html_path,
        'pdf_path': doc.pdf_path,
        'preview_url': doc.preview_url
    })

@app.route('/api/generate/quote', methods=['POST'])
def generate_quote():
    """Generate quote response"""
    params = request.json
    doc = documents.generate_quote_response(
        solicitation=params['sol_data'],
        pricing=params['pricing_data'],
        past_performance=params['pp_data']
    )
    return jsonify({
        'document_path': doc.path,
        'page_count': doc.page_count,
        'compliance_matrix': doc.compliance_matrix
    })

@app.route('/api/status/<bid_id>', methods=['GET'])
def get_status(bid_id):
    """Get current stage and status"""
    status = airtable.get_bid_status(bid_id)
    return jsonify({
        'stage': status.stage,
        'step': status.current_step,
        'deadline': status.deadline,
        'days_remaining': status.days_left,
        'next_action': status.next_action
    })

@app.route('/api/dashboard', methods=['GET'])
def get_dashboard():
    """Morning brief data"""
    return jsonify({
        'active_bids_by_stage': get_stage_counts(),
        'this_week_deadlines': get_week_deadlines(),
        'attention_needed': get_attention_items(),
        'recommendations': get_recommendations()
    })
```

---

## REVISED SYSTEM ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────┐
│                    NEXUS PLATFORM                            │
│                                                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   REVENUE   │  │   REVENUE   │  │   REVENUE   │        │
│  │   GPSS      │  │   DDCSS     │  │   GBIS      │        │
│  │  (Govt)     │  │ (Corporate) │  │  (Grants)   │        │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘        │
│         │                │                │               │
│         └────────────────┼────────────────┘               │
│                          │                                 │
│              ┌───────────┴───────────┐                    │
│              │      COMPASS™         │                    │
│              │  (Quality Assurance)  │                    │
│              │   ProposalBio Scoring │                    │
│              └───────────┬───────────┘                    │
│                          │                                 │
│  ┌───────────────────────┼───────────────────────┐          │
│  │                       │                       │          │
│  ▼                       ▼                       ▼          │
│ ┌────────────┐    ┌────────────┐    ┌────────────┐        │
│ │  ATLAS   │    │   PRISM    │    │   LBPC     │        │
│ │(Projects)│    │(Field Svcs)│    │ (Surplus)  │        │
│ └────┬─────┘    └────┬─────┘    └────┬─────┘        │
│      │               │               │                   │
│      └───────────────┼───────────────┘                   │
│                      │                                     │
│  ┌───────────────────┴───────────────────┐                │
│  │            VERTEX                     │                │
│  │      (Financial Center)               │                │
│  │  • Invoicing (actuals, not forecasts) │                │
│  │  • Payment tracking                   │                │
│  │  • Expense management                 │                │
│  │  • Cash flow (actuals)                │                │
│  └───────────────────┬───────────────────┘                │
│                      │                                     │
│  ┌───────────────────┴───────────────────┐                │
│  │          DOCUMENTS                  │                │
│  │    (Generation + Storage)           │                │
│  │                                     │                │
│  │  ┌───────────────────────────────┐  │                │
│  │  │     GENERATION ENGINE         │  │                │
│  │  │  • Capability Statements      │  │                │
│  │  │  • Quote Responses            │  │                │
│  │  │  • Proposals                  │  │                │
│  │  │  • RFQs                       │  │                │
│  │  │  • Sub Agreements             │  │                │
│  │  └───────────────────────────────┘  │                │
│  │                                     │                │
│  │  ┌───────────────────────────────┐  │                │
│  │  │     REPOSITORY                │  │                │
│  │  │  • All generated files          │  │                │
│  │  │  • Version history              │  │                │
│  │  │  • Archive/retrieval            │  │                │
│  │  └───────────────────────────────┘  │                │
│  └─────────────────────────────────────┘                │
│                                                          │
│  ┌─────────────────────────────────────┐                │
│  │     AIRTABLE (Data Backbone)        │                │
│  │  • 69 tables across all systems     │                │
│  │  • Status tracking                  │                │
│  │  • Forecasting (GPSS pipeline)      │                │
│  │  • Not in VERTEX                    │                │
│  └─────────────────────────────────────┘                │
└───────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│              INTERFACES (How You Use NEXUS)               │
│                                                              │
│  1. Cursor AI Chat (Conversational)                        │
│     └── Natural language: "I found a solicitation"          │
│                                                              │
│  2. CLI (Command Line)                                      │
│     └── python3 nexus_cli.py --intake RFP.pdf             │
│                                                              │
│  3. Web Form (Self-Service)                                │
│     └── Upload RFP → Select doc type → Generate           │
│                                                              │
│  4. API (Programmatic)                                     │
│     └── POST /api/generate/capability                     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## KEY CHANGES SUMMARY

| Element | Old | New |
|---------|-----|-----|
| **VERTEX** | Had forecasting | ❌ Removed forecasting |
| **GPSS** | Just opportunities | ✅ Now includes pipeline forecasting |
| **DOCUMENTS** | Just storage | ✅ Generation engine + storage |
| **NEXUS Usage** | Cursor chat only | ✅ CLI + Web + API + Chat |

---

## NEXT STEPS

1. **Confirm system boundaries** (this correction)
2. **Build CLI interface** for manual NEXUS usage
3. **Build simple web form** for document generation
4. **Update all system documentation** with corrected scopes

**Does this correction align with your vision?**

---

## CORRECTION: CHAMPS PROVIDER ID — 6309049 (NOT 6309069)

**Date:** May 9, 2026
**Source of truth:** `COMPANY_INFO_MASTER.md` — Michigan CHAMPS section

- **Correct CHAMPS Provider ID:** **6309049**
- **Wrong ID that was in multiple files:** ~~6309069~~
- **Approved:** 03/23/2026, Active through 12/31/2999
- **Application #:** 20260323058125

**Files corrected May 9, 2026:**
- `NEMT_TPA_EXPANSION_STRATEGY.md`
- `HAVEN/STRATEGY/HAVEN_MEDICAID_ENROLLMENT_BY_STATE.md` (3 occurrences) — canonical path; ~~`NEXUS_LEARNING/HAVEN_MEDICAID_ENROLLMENT_BY_STATE.md`~~ superseded May 2026
- `NEXUS_TRAINING_DOCUMENT.md` (2 occurrences)
- `DDI_TPA_DIVISIONS.md` (1 occurrence)

**Files already correct:** `COMPANY_INFO_MASTER.md`, `PARTNER_ACCOUNT_UPDATES.md`, `HAP_CARESOURCE_OPERATIONS.md`, `SHIELD_SERVICE_FULFILLMENT_MAP.md`, `MDHHS_SHIELD_PILOT_PROPOSAL.md`, `ESSENTIALS/DDI_CONTRACT_MANAGEMENT_TPA_POSITIONING.md`, `CLIENT OUTREACH/MCO_MEDICAL_LAB_PHARMACY_COURIER_TARGETS.md`

**Rule:** Always pull CHAMPS ID from `COMPANY_INFO_MASTER.md`. It is **6309049**.