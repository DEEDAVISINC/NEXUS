# 📊 NEXUS SYSTEM DIAGRAMS

**Visual representations of all NEXUS workflows and integrations**

---

## 🗺️ TABLE OF CONTENTS

1. [High-Level System Architecture](#1-high-level-system-architecture)
2. [Opportunity Discovery Flow](#2-opportunity-discovery-flow)
3. [Federal Forecasting Flow](#3-federal-forecasting-flow)
4. [Forecast Outreach Flow](#4-forecast-outreach-flow)
5. [Bid Preparation Flow](#5-bid-preparation-flow)
6. [ProposalBio™ Integration Points](#6-proposalbio-integration-points)
7. [Fulfillment & Delivery Flow](#7-fulfillment--delivery-flow)
8. [Financial Tracking Flow](#8-financial-tracking-flow)
9. [Data Flow Diagram](#9-data-flow-diagram)
10. [Airtable Table Relationships](#10-airtable-table-relationships)

---

## 1. HIGH-LEVEL SYSTEM ARCHITECTURE

```mermaid
graph TB
    subgraph "EXTERNAL SOURCES"
        SAM[SAM.gov API]
        STATE[State Portals]
        BIDNET[BidNet/DemandStar]
        NASA[NASA Forecasts]
        GSA[GSA Schedules]
    end
    
    subgraph "MINING LAYER"
        MINE[Mining Agents<br/>Daily Cron Jobs]
        FORECAST[Forecast Mining]
    end
    
    subgraph "AI ANALYSIS LAYER"
        GPT4[GPT-4 Analysis<br/>Fit Scoring]
        PROPOSALBIO[ProposalBio™<br/>Quality Analysis]
        STRATEGIC[Strategic Analysis]
    end
    
    subgraph "NEXUS CORE - Airtable"
        OPP[(GPSS OPPORTUNITIES)]
        FORECASTS[(Federal Forecasts)]
        PRODUCTS[(GPSS PRODUCTS)]
        SUPPLIERS[(GPSS SUPPLIERS)]
        PROPOSALS[(GPSS Proposals)]
        OUTREACH[(Officer Outreach)]
        CONTRACTS[(CONTRACTS)]
        INVOICES[(VERTEX INVOICES)]
    end
    
    subgraph "API SERVER - Flask"
        API[api_server.py<br/>REST Endpoints]
    end
    
    subgraph "AUTOMATION MODULES"
        CAPSTAT[Capability Statement<br/>Generator]
        RFP_GEN[RFP/RFQ<br/>Generator]
        DOC_ASSEMBLY[Document<br/>Assembly]
        CALENDAR[Calendar<br/>Automation]
        EMAIL[Email<br/>System]
    end
    
    subgraph "FRONTEND - React"
        UI[nexus-frontend<br/>User Interface]
    end
    
    subgraph "OUTPUT"
        PDF[PDF Documents]
        ICS[Calendar Files]
        EMAILS[Email Messages]
    end
    
    %% Connections
    SAM --> MINE
    STATE --> MINE
    BIDNET --> MINE
    NASA --> FORECAST
    GSA --> FORECAST
    
    MINE --> GPT4
    FORECAST --> GPT4
    
    GPT4 --> OPP
    GPT4 --> FORECASTS
    
    OPP --> STRATEGIC
    FORECASTS --> CAPSTAT
    
    STRATEGIC --> PROPOSALS
    PROPOSALS --> PROPOSALBIO
    
    UI --> API
    API --> OPP
    API --> FORECASTS
    API --> PROPOSALS
    API --> CAPSTAT
    API --> RFP_GEN
    
    CAPSTAT --> PDF
    CAPSTAT --> OUTREACH
    OUTREACH --> PROPOSALBIO
    
    PROPOSALS --> DOC_ASSEMBLY
    DOC_ASSEMBLY --> PDF
    
    OPP --> CALENDAR
    CALENDAR --> ICS
    
    OUTREACH --> EMAIL
    EMAIL --> EMAILS
    
    CONTRACTS --> INVOICES
    
    style PROPOSALBIO fill:#90EE90
    style API fill:#87CEEB
    style OPP fill:#FFD700
    style FORECASTS fill:#FFA500
```

---

## 2. OPPORTUNITY DISCOVERY FLOW

```mermaid
flowchart TD
    START([Daily Cron Job<br/>6:00 AM]) --> INIT[Initialize Mining Agent]
    INIT --> SAM_API[Call SAM.gov API<br/>Last 7 Days]
    
    SAM_API --> PARSE[Parse Response JSON<br/>Extract Opportunities]
    
    PARSE --> LOOP{More Opps?}
    LOOP -->|Yes| DEDUP[Check for Duplicate<br/>in Airtable]
    
    DEDUP -->|Exists| SKIP[Skip Duplicate]
    SKIP --> LOOP
    
    DEDUP -->|New| AI_ANALYZE[AI Analysis<br/>GPT-4 Fit Scoring]
    
    AI_ANALYZE --> CALC_SCORE[Calculate Fit Score<br/>0-100]
    
    CALC_SCORE --> CHECK_SCORE{Score >= 50?}
    CHECK_SCORE -->|No| REJECT[Log as Low Priority]
    REJECT --> LOOP
    
    CHECK_SCORE -->|Yes| SAVE[Save to Airtable<br/>GPSS OPPORTUNITIES]
    
    SAVE --> CHECK_DEADLINE{Deadline<br/>< 14 days?}
    
    CHECK_DEADLINE -->|Yes| CREATE_CAL[Create Calendar Event<br/>.ics File]
    CREATE_CAL --> SEND_ALERT
    
    CHECK_DEADLINE -->|No| CHECK_PRIORITY
    
    CHECK_PRIORITY{Priority<br/>= High?}
    CHECK_PRIORITY -->|Yes| SEND_ALERT[Send Email Alert]
    CHECK_PRIORITY -->|No| LOG
    
    SEND_ALERT --> LOG[Log Success]
    LOG --> LOOP
    
    LOOP -->|No More| SUMMARY[Generate Daily<br/>Summary Report]
    
    SUMMARY --> END([Mining Complete])
    
    style AI_ANALYZE fill:#90EE90
    style SAVE fill:#FFD700
    style SEND_ALERT fill:#FF6B6B
```

---

## 3. FEDERAL FORECASTING FLOW

```mermaid
sequenceDiagram
    participant CRON as Cron Job
    participant MINER as Forecast Miner
    participant SAM as SAM.gov API
    participant NASA as NASA Website
    participant AI as GPT-4 Analysis
    participant AIRTABLE as Airtable<br/>Federal Forecasts
    participant USER as User Email
    
    CRON->>MINER: Trigger at 6:00 AM
    activate MINER
    
    MINER->>SAM: Get Pre-Solicitations<br/>(ptype='p', next 90 days)
    SAM-->>MINER: Return Forecasts JSON
    
    MINER->>NASA: Scrape Procurement Forecasts
    NASA-->>MINER: Return HTML Tables
    
    loop For Each Forecast
        MINER->>MINER: Parse Forecast Data
        MINER->>MINER: Extract Officer Contact
        
        MINER->>AI: Analyze Fit Score<br/>+ Preparation Tips
        AI-->>MINER: Return Analysis<br/>(Score, Priority, Actions)
        
        alt Fit Score >= 50
            MINER->>AIRTABLE: Create Forecast Record
            AIRTABLE-->>MINER: Return Record ID
            
            alt Fit Score >= 80 AND Has Officer Email
                MINER->>USER: Send HIGH PRIORITY Alert
                USER-->>MINER: Email Delivered
            end
        else Low Score
            MINER->>MINER: Skip (Log Only)
        end
    end
    
    MINER->>MINER: Generate Summary Report
    deactivate MINER
```

---

## 4. FORECAST OUTREACH FLOW

```mermaid
flowchart TD
    START([User Opens Airtable<br/>Federal Forecasts]) --> VIEW[View High Priority<br/>Forecasts]
    
    VIEW --> SELECT[Select Forecast<br/>Fit Score: 85]
    
    SELECT --> REVIEW[Review Details<br/>Officer: John Smith<br/>Email: john.smith@nasa.gov]
    
    REVIEW --> DECISION{Reach Out?}
    DECISION -->|No| END1([End])
    
    DECISION -->|Yes| CLICK[Click Button:<br/>'📧 Reach Out to Officer']
    
    CLICK --> API_CALL[Airtable Button Triggers<br/>API Call to NEXUS]
    
    API_CALL --> GET_FORECAST[API: Get Forecast<br/>Details from Airtable]
    
    GET_FORECAST --> VALIDATE{Has Officer<br/>Email?}
    VALIDATE -->|No| ERROR[Return Error:<br/>Missing Officer Contact]
    ERROR --> END1
    
    VALIDATE -->|Yes| GEN_CAPSTAT[Generate<br/>Capability Statement]
    
    GEN_CAPSTAT --> HTML[Create HTML<br/>Tailored to Agency]
    HTML --> PDF[Convert to PDF<br/>WeasyPrint]
    
    PDF --> GEN_LETTER[Generate<br/>Introduction Letter]
    
    GEN_LETTER --> BUILD_LETTER[Build Letter Text<br/>Personalized Content]
    
    BUILD_LETTER --> PROPOSALBIO[ProposalBio™<br/>Automatic Analysis]
    
    PROPOSALBIO --> ANALYZE_10[Analyze 10 Biohacks<br/>Calculate Score]
    
    ANALYZE_10 --> SCORE{Score >= 75?}
    
    SCORE -->|Yes| BADGE_GREEN[Quality Badge:<br/>🟢 HIGH QUALITY]
    SCORE -->|60-74| BADGE_YELLOW[Quality Badge:<br/>🟡 GOOD QUALITY]
    SCORE -->|< 60| BADGE_RED[Quality Badge:<br/>🔴 NEEDS IMPROVEMENT]
    
    BADGE_GREEN --> CREATE_OUTREACH
    BADGE_YELLOW --> CREATE_OUTREACH
    BADGE_RED --> CREATE_OUTREACH
    
    CREATE_OUTREACH[Create Record in<br/>Officer Outreach Tracking]
    
    CREATE_OUTREACH --> LINK[Link to Forecast<br/>Save Letter Content<br/>Save ProposalBio Score]
    
    LINK --> UPDATE_FORECAST[Update Forecast:<br/>Outreach Status =<br/>'Cap Statement Generated']
    
    UPDATE_FORECAST --> RETURN[Return Success<br/>to User]
    
    RETURN --> SHOW_SUCCESS[Show Success Message<br/>in Airtable]
    
    SHOW_SUCCESS --> USER_REVIEW[User Reviews Letter<br/>in Officer Outreach]
    
    USER_REVIEW --> CUSTOMIZE{Customize?}
    CUSTOMIZE -->|Yes| EDIT[Edit Letter Text]
    EDIT --> DOWNLOAD
    CUSTOMIZE -->|No| DOWNLOAD[Download<br/>Capability Statement PDF]
    
    DOWNLOAD --> COMPOSE[Compose Email<br/>to Officer]
    
    COMPOSE --> ATTACH[Attach Cap Statement]
    
    ATTACH --> SEND[Send Email]
    
    SEND --> UPDATE_STATUS[Update Airtable:<br/>Status = 'Sent'<br/>Date Sent = Today]
    
    UPDATE_STATUS --> AUTO_FOLLOWUP[System Auto-Schedules<br/>Follow-up in 10 Days]
    
    AUTO_FOLLOWUP --> END2([End - Tracking Active])
    
    style PROPOSALBIO fill:#90EE90
    style BADGE_GREEN fill:#90EE90
    style BADGE_YELLOW fill:#FFFF99
    style BADGE_RED fill:#FF6B6B
```

---

## 5. BID PREPARATION FLOW

```mermaid
flowchart TD
    START([User Opens<br/>GPSS OPPORTUNITIES]) --> SELECT[Select Opportunity<br/>Status: New]
    
    SELECT --> REVIEW[Review RFP Details<br/>Fit Score: 82]
    
    REVIEW --> DECISION{Pursue Bid?}
    DECISION -->|No| DECLINE[Update Status:<br/>'Declined']
    DECLINE --> END1([End])
    
    DECISION -->|Yes| CREATE_FOLDER[Create Bid Folder<br/>photos_and_videos/<br/>NASA IT EQUIPMENT/]
    
    CREATE_FOLDER --> UPDATE_STATUS[Update Status:<br/>'In Progress']
    
    UPDATE_STATUS --> AI_REC[Run AI Recommendations<br/>Identify Capability Gaps]
    
    AI_REC --> CHECK_GAPS{Gaps Found?}
    
    CHECK_GAPS -->|Yes| SEARCH_SUB[Search for Subcontractors<br/>GPSS SUBCONTRACTORS]
    SEARCH_SUB --> SELECT_SUB[Select Partners]
    SELECT_SUB --> CHECK_PRODUCTS
    
    CHECK_GAPS -->|No| CHECK_PRODUCTS{Products<br/>Required?}
    
    CHECK_PRODUCTS -->|Yes| SEARCH_PROD[Search GPSS PRODUCTS<br/>Match Line Items]
    
    SEARCH_PROD --> FOUND_PROD{Products<br/>Found?}
    
    FOUND_PROD -->|No| ADD_PROD[Add New Products<br/>to Catalog]
    ADD_PROD --> SEARCH_SUPP
    
    FOUND_PROD -->|Yes| SEARCH_SUPP[Search GPSS SUPPLIERS<br/>for Products]
    
    SEARCH_SUPP --> SELECT_SUPP[Select 3-5 Suppliers]
    
    SELECT_SUPP --> GEN_RFQ[Generate Supplier RFQs<br/>⚠️ NEVER Reveal Buyer!]
    
    GEN_RFQ --> SEND_RFQ[Send RFQs to Suppliers]
    
    SEND_RFQ --> WAIT[Wait for Quotes]
    
    WAIT --> RECEIVE[Receive Quotes]
    
    RECEIVE --> COMPARE[Compare Pricing<br/>in GPSS SUPPLIER QUOTES]
    
    COMPARE --> SELECT_WINNER[Select Best<br/>Price + Terms]
    
    SELECT_WINNER --> STRATEGIC[Run Strategic Analysis<br/>RFP Success®]
    
    STRATEGIC --> CALC_PRICE[Calculate Final Pricing<br/>Cost + Margin]
    
    CALC_PRICE --> CREATE_PROP[Create Proposal<br/>GPSS Proposals]
    
    CREATE_PROP --> FILL_FIELDS[Fill All Fields:<br/>- Executive Summary<br/>- Technical Approach<br/>- Past Performance<br/>- Pricing<br/>- Certifications]
    
    FILL_FIELDS --> AUTO_PROPOSALBIO[🟢 AUTOMATIC<br/>ProposalBio™ Analysis]
    
    AUTO_PROPOSALBIO --> ANALYZE[Analyze All 10 Biohacks<br/>Calculate Composite Score]
    
    ANALYZE --> SCORE{Score?}
    
    SCORE -->|>= 75| PASS[Status: UNLOCKED<br/>🟢 Ready to Submit]
    SCORE -->|60-74| GOOD[Status: UNLOCKED<br/>🟡 Good - Minor Edits]
    SCORE -->|< 60| NEEDS_WORK[Status: LOCKED<br/>🔴 Needs Improvement]
    
    PASS --> ASSEMBLE
    GOOD --> ASSEMBLE
    NEEDS_WORK --> SHOW_IMPROVE[Show Improvement Tips]
    
    SHOW_IMPROVE --> USER_EDIT[User Edits Proposal]
    USER_EDIT --> AUTO_PROPOSALBIO
    
    ASSEMBLE[Assemble Bid Package<br/>Document Assembly API]
    
    ASSEMBLE --> GATHER[Gather All Documents:<br/>- Proposal PDF<br/>- Pricing Sheets<br/>- Certifications<br/>- Past Performance<br/>- Forms]
    
    GATHER --> COMBINE[Combine into<br/>Single Package]
    
    COMBINE --> REVIEW_FINAL[User Final Review]
    
    REVIEW_FINAL --> SIGN[Sign Documents]
    
    SIGN --> SUBMIT[Submit Bid<br/>Portal/Email]
    
    SUBMIT --> UPDATE_DONE[Update Status:<br/>'Submitted']
    
    UPDATE_DONE --> TRACK[Track in Airtable<br/>Wait for Award]
    
    TRACK --> END2([End - Awaiting Award])
    
    CHECK_PRODUCTS -->|No| STRATEGIC
    
    style AUTO_PROPOSALBIO fill:#90EE90
    style PASS fill:#90EE90
    style GOOD fill:#FFFF99
    style NEEDS_WORK fill:#FF6B6B
    style GEN_RFQ fill:#FF6B6B
```

---

## 6. PROPOSALBIO™ INTEGRATION POINTS

```mermaid
graph TB
    subgraph "AUTOMATIC ANALYSIS POINTS"
        A1[Proposal Creation<br/>GPSS Proposals]
        A2[Forecast Outreach Letter<br/>Officer Outreach Tracking]
        A3[Closed Opp Outreach<br/>Officer Outreach Tracking]
    end
    
    subgraph "PROPOSALBIO™ ENGINE"
        PB[ProposalBio™ Analyzer]
        
        B1[Biohack #1:<br/>Mirror Neuron]
        B2[Biohack #2:<br/>Cognitive Ease]
        B3[Biohack #3:<br/>Reciprocity Anchor]
        B4[Biohack #4:<br/>Loss Aversion]
        B5[Biohack #5:<br/>Social Proof]
        B6[Biohack #6:<br/>Authority Signal]
        B7[Biohack #7:<br/>Name Recognition]
        B8[Biohack #8:<br/>Specificity Bias]
        B9[Biohack #9:<br/>Commitment Device]
        B10[Biohack #10:<br/>Peak-End Rule]
        
        CALC[Calculate Composite Score<br/>0-100]
        STATUS[Determine Status:<br/>PASSING / GOOD / NEEDS WORK]
        BADGE[Assign Quality Badge:<br/>🟢🟡🔴]
        IMPROVE[Generate Improvement Tips]
    end
    
    subgraph "AIRTABLE STORAGE"
        T1[(GPSS Proposals<br/>ProposalBio Score)]
        T2[(Officer Outreach Tracking<br/>ProposalBio Score)]
        T3[(GPSS ProposalBio Scores<br/>Historical Data)]
        T4[(GPSS ProposalBio Learning<br/>Win/Loss Correlation)]
    end
    
    subgraph "OUTCOMES & LEARNING"
        W1[Track Win/Loss]
        W2[Correlate Score to Success]
        W3[Adaptive Learning]
        W4[Improve Future Analysis]
    end
    
    %% Connections
    A1 --> PB
    A2 --> PB
    A3 --> PB
    
    PB --> B1
    PB --> B2
    PB --> B3
    PB --> B4
    PB --> B5
    PB --> B6
    PB --> B7
    PB --> B8
    PB --> B9
    PB --> B10
    
    B1 --> CALC
    B2 --> CALC
    B3 --> CALC
    B4 --> CALC
    B5 --> CALC
    B6 --> CALC
    B7 --> CALC
    B8 --> CALC
    B9 --> CALC
    B10 --> CALC
    
    CALC --> STATUS
    STATUS --> BADGE
    STATUS --> IMPROVE
    
    BADGE --> T1
    BADGE --> T2
    CALC --> T3
    
    T1 --> W1
    T2 --> W1
    W1 --> W2
    W2 --> W3
    W3 --> W4
    W4 --> PB
    
    style PB fill:#90EE90
    style A1 fill:#87CEEB
    style A2 fill:#87CEEB
    style A3 fill:#87CEEB
```

---

## 7. FULFILLMENT & DELIVERY FLOW

```mermaid
sequenceDiagram
    participant USER as User
    participant OPP as GPSS OPPORTUNITIES
    participant CONTRACT as CONTRACTS
    participant FULFILL as FULFILLMENT CONTRACTS
    participant INV as FULFILLMENT INVENTORY
    participant PO as FULFILLMENT PURCHASE ORDERS
    participant SUPP as Supplier
    participant DEL as FULFILLMENT DELIVERIES
    
    USER->>OPP: Update Status: 'Awarded'
    OPP->>CONTRACT: Auto-Create Contract Record
    
    alt Product-Based Contract
        CONTRACT->>FULFILL: Create Fulfillment Contract
        
        loop For Each Delivery Schedule
            FULFILL->>INV: Check Inventory<br/>Do we have stock?
            
            alt Stock Available
                INV-->>FULFILL: Yes - Use existing stock
            else Need to Order
                FULFILL->>PO: Create Purchase Order
                PO->>SUPP: Send PO to Supplier
                SUPP-->>PO: Confirm Order
                SUPP->>SUPP: Ship to DDI
                SUPP-->>INV: Update: Stock Received
            end
            
            FULFILL->>DEL: Create Delivery Record
            DEL->>DEL: Schedule Delivery Date
            DEL->>USER: Send Notification:<br/>"Delivery Scheduled"
            
            USER->>DEL: Mark: 'Delivered'
            DEL->>DEL: Capture Signature/POD
            DEL-->>FULFILL: Update Delivery Status
        end
    else Service-Based Contract
        CONTRACT->>CONTRACT: Track Milestones
        Note over CONTRACT: No fulfillment needed<br/>for services
    end
```

---

## 8. FINANCIAL TRACKING FLOW

```mermaid
flowchart LR
    subgraph "DELIVERY"
        DEL[FULFILLMENT DELIVERIES<br/>Status: Delivered]
    end
    
    subgraph "INVOICING"
        AUTO_INV[Auto-Generate Invoice<br/>VERTEX INVOICES]
        PDF[Create Invoice PDF]
        SEND[Send to Client]
        TRACK[Track Payment Status]
    end
    
    subgraph "REVENUE"
        REV[VERTEX REVENUE<br/>Record Income]
    end
    
    subgraph "EXPENSES"
        PO[FULFILLMENT PURCHASE ORDERS]
        EXP[VERTEX EXPENSES<br/>Record Costs]
    end
    
    subgraph "PROFIT ANALYSIS"
        CALC[Calculate Profit Margin]
        REPORT[Financial Reports]
        DASHBOARD[Profitability Dashboard]
    end
    
    DEL --> AUTO_INV
    AUTO_INV --> PDF
    PDF --> SEND
    SEND --> TRACK
    
    TRACK -->|Paid| REV
    
    PO --> EXP
    
    REV --> CALC
    EXP --> CALC
    
    CALC --> REPORT
    REPORT --> DASHBOARD
    
    style REV fill:#90EE90
    style CALC fill:#FFD700
```

---

## 9. DATA FLOW DIAGRAM

```
┌──────────────────────────────────────────────────────────────────────────┐
│                           EXTERNAL SOURCES                                │
│   SAM.gov │ State Portals │ BidNet │ NASA │ GSA │ Email │ Web Forms     │
└─────────────────────────┬────────────────────────────────────────────────┘
                          │
                          ▼
         ┌────────────────────────────────────────┐
         │       MINING & INGESTION LAYER         │
         │  • Python Mining Scripts (Cron)        │
         │  • API Integrations                    │
         │  • Web Scraping                        │
         └────────────┬───────────────────────────┘
                      │
                      ▼
         ┌────────────────────────────────────────┐
         │         AI ANALYSIS LAYER              │
         │  • GPT-4 Fit Scoring                   │
         │  • ProposalBio™ Quality Analysis       │
         │  • Strategic Analysis (RFP Success®)   │
         └────────────┬───────────────────────────┘
                      │
                      ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                          AIRTABLE (Database)                              │
│                                                                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │
│  │GPSS OPPS    │  │Federal      │  │GPSS         │  │GPSS         │   │
│  │             │  │Forecasts    │  │Proposals    │  │Products     │   │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘   │
│         │                 │                 │                 │          │
│  ┌──────┴──────┐  ┌──────┴──────┐  ┌──────┴──────┐  ┌──────┴──────┐   │
│  │Officer      │  │CONTRACTS    │  │GPSS         │  │FULFILLMENT  │   │
│  │Outreach     │  │             │  │Suppliers    │  │Contracts    │   │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘   │
│         │                 │                 │                 │          │
│  ┌──────┴──────┐  ┌──────┴──────┐  ┌──────┴──────┐  ┌──────┴──────┐   │
│  │AI           │  │VERTEX       │  │VERTEX       │  │ProposalBio  │   │
│  │Recommendations│ │Invoices     │  │Revenue      │  │Scores       │   │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘   │
└───────────────────────────┬──────────────────────────────────────────────┘
                            │
                            ▼
         ┌────────────────────────────────────────┐
         │       API SERVER (Flask)               │
         │  • REST Endpoints                      │
         │  • Business Logic                      │
         │  • Automation Orchestration            │
         └────────────┬───────────────────────────┘
                      │
        ┌─────────────┼─────────────┐
        │             │             │
        ▼             ▼             ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│   FRONTEND   │ │  AUTOMATION  │ │   OUTPUT     │
│              │ │              │ │              │
│ • React UI   │ │ • Calendar   │ │ • PDFs       │
│ • Dashboards │ │ • Email      │ │ • ICS Files  │
│ • Forms      │ │ • RFP Gen    │ │ • Emails     │
│ • Reports    │ │ • Doc Assy   │ │ • Docs       │
└──────────────┘ └──────────────┘ └──────────────┘
```

---

## 10. AIRTABLE TABLE RELATIONSHIPS

```mermaid
erDiagram
    GPSS_OPPORTUNITIES ||--o{ GPSS_PROPOSALS : "has proposals"
    GPSS_OPPORTUNITIES ||--o{ AI_RECOMMENDATIONS : "gets recommendations"
    GPSS_OPPORTUNITIES ||--|| CONTRACTS : "becomes contract"
    
    FEDERAL_FORECASTS ||--o{ OFFICER_OUTREACH : "triggers outreach"
    FEDERAL_FORECASTS ||--o{ CAPABILITY_STATEMENTS : "generates capstat"
    
    GPSS_OPPORTUNITIES ||--o{ OFFICER_OUTREACH : "triggers outreach"
    OFFICER_OUTREACH ||--|| CAPABILITY_STATEMENTS : "includes capstat"
    
    GPSS_PROPOSALS ||--|| PROPOSALBIO_SCORES : "analyzed by"
    OFFICER_OUTREACH ||--|| PROPOSALBIO_SCORES : "analyzed by"
    PROPOSALBIO_SCORES ||--o{ PROPOSALBIO_LEARNING : "learns from"
    
    GPSS_PROPOSALS }o--o{ GPSS_PRODUCTS : "includes products"
    GPSS_PROPOSALS }o--o{ GPSS_SUBCONTRACTORS : "includes subcontractors"
    
    GPSS_PRODUCTS }o--o{ GPSS_SUPPLIERS : "supplied by"
    GPSS_SUPPLIERS ||--o{ GPSS_SUPPLIER_QUOTES : "provides quotes"
    
    CONTRACTS ||--o{ FULFILLMENT_CONTRACTS : "creates fulfillment"
    FULFILLMENT_CONTRACTS ||--o{ FULFILLMENT_DELIVERIES : "schedules deliveries"
    FULFILLMENT_CONTRACTS }o--|| FULFILLMENT_INVENTORY : "uses inventory"
    
    FULFILLMENT_CONTRACTS ||--o{ FULFILLMENT_PURCHASE_ORDERS : "generates POs"
    FULFILLMENT_PURCHASE_ORDERS }o--|| GPSS_SUPPLIERS : "sent to supplier"
    
    FULFILLMENT_DELIVERIES ||--o{ VERTEX_INVOICES : "generates invoice"
    VERTEX_INVOICES ||--|| VERTEX_REVENUE : "creates revenue"
    
    FULFILLMENT_PURCHASE_ORDERS ||--|| VERTEX_EXPENSES : "creates expense"
    
    CONTRACTS ||--o{ ATLAS_PROJECTS : "becomes project"
    ATLAS_PROJECTS ||--o{ ATLAS_TASKS : "has tasks"
    
    GPSS_OPPORTUNITIES {
        string Solicitation_Number PK
        string Title
        string Agency
        date Response_Deadline
        int Fit_Score
        string Status
    }
    
    FEDERAL_FORECASTS {
        string Record_ID PK
        string Title
        string Agency
        date Estimated_Solicitation_Date
        string Officer_Email
        int Fit_Score
        boolean Outreach_Status
    }
    
    OFFICER_OUTREACH {
        string Record_ID PK
        string Outreach_Type
        string Officer_Email
        string Letter_Content
        float ProposalBio_Score
        string Status
    }
    
    GPSS_PROPOSALS {
        string Proposal_ID PK
        string Opportunity FK
        text Executive_Summary
        text Technical_Approach
        float Pricing
        float ProposalBio_Score
        string Lock_Status
    }
    
    PROPOSALBIO_SCORES {
        string Score_ID PK
        string Document_ID FK
        float Composite_Score
        json Biohack_Scores
        string Status
    }
    
    CONTRACTS {
        string Contract_ID PK
        string Opportunity FK
        date Award_Date
        float Contract_Value
        string Type
    }
    
    FULFILLMENT_DELIVERIES {
        string Delivery_ID PK
        string Contract FK
        date Scheduled_Date
        date Actual_Date
        string Status
    }
    
    VERTEX_INVOICES {
        string Invoice_ID PK
        string Delivery FK
        float Amount
        date Due_Date
        string Payment_Status
    }
```

---

## 📌 DIAGRAM LEGEND

**Colors:**
- 🟢 Green = ProposalBio™ / Quality Analysis / Success
- 🟡 Yellow = Warning / Medium Priority / Good Quality
- 🔴 Red = Critical / High Priority / Needs Attention / Never Reveal Buyer
- 🔵 Blue = API / System Integration
- 🟠 Orange = Data Storage / Airtable

**Symbols:**
- `[ ]` = Process/Function
- `{ }` = Decision Point
- `( )` = Start/End Point
- `[( )]` = Rounded Process
- `[/ /]` = Data Storage

---

**These diagrams show the complete NEXUS system architecture and all integration points!**

Let me know if you want:
1. More detailed sequence diagrams for specific workflows
2. Entity-relationship diagrams for specific table groups
3. Component interaction diagrams
4. Deployment architecture diagrams
5. Network/security architecture diagrams
