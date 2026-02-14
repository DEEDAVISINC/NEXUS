# 🎯 NEXUS SYSTEM ACRONYMS

**Complete list of all NEXUS subsystem names and acronyms**

---

## **Core Systems:**

### **1. GPSS** - Government Procurement Strategic System
- **Function:** Government contracting intelligence and proposal management
- **Features:** Opportunity tracking, AI proposal generation, pricing intelligence, compliance checking

### **2. ATLAS** - Advanced Task & Logistics Automation System
- **Function:** Project management and execution
- **Features:** Project tracking, WBS generation, change order management, task automation

### **3. DDCSS** - Diversity Division Corporate Success System
- **Function:** Corporate sales and business development
- **Features:** Client avatar builder, success path mapping, pitch generation, email analysis

### **4. LBPC** - Lead & Proposal Builder for Claims
- **Function:** Surplus recovery and legal claims management
- **Features:** Lead mining, document generation, workflow automation, e-signature integration

### **5. VERTEX** - Financial Excellence & Revenue Tracking Executive System
- **Function:** Financial management and intelligence
- **Features:** Invoicing, expense tracking, revenue analysis, cash flow forecasting

### **6. GBIS** - Grant Business Intelligence System
- **Function:** Grant discovery and application management
- **Features:** Grant mining, eligibility analysis, application tracking, compliance management

### **7. COMPASS™** - Compliant Optimization & Messaging Performance Assessment System
- **Function:** Proposal quality assurance and validation
- **Tagline:** "Precision Validated. Competition Ready."
- **Features:** 10-point quality scoring, compliance validation, win-readiness assessment
- **Marketing Name:** COMPASS™ (external-facing)
- **Internal Code:** ProposalBio™ (technical module)

### **8. PRISM** - Professional Resource Inspection & Service Management
- **Function:** Field service dispatch, order management, and document verification
- **Tagline:** "See every detail. Miss nothing."
- **Features:** Order lifecycle management, field agent dispatch, vendor portal, scanback upload, AI-powered document inspection, adaptive learning error detection, correction workflow, shipping/lab tracking
- **Service Types:** Notary signing, drug testing (DOT/non-DOT), DNA collection, fingerprinting, courier/runner, apostille, background checks, process serving
- **Key Innovation:** Real-time document inspection catches missing signatures, initials, seals, and fields BEFORE documents ship — eliminating rejections and return trips
- **Vendor Type:** Field Agents (distinct from Suppliers and Subcontractors)

---

## **System Relationships:**

```
NEXUS Business Operating System
│
├── GPSS (Find & Win Government Contracts)
│   └── Uses COMPASS™ for proposal validation
│   └── Won service contracts flow to PRISM for execution
│
├── DDCSS (Win Corporate Clients)
│   └── Blueprint contracts create PRISM client profiles
│   └── Creates invoices via VERTEX
│
├── PRISM (Dispatch, Execute & Verify Field Services)  ← NEW
│   └── Receives clients from DDCSS and GPSS
│   └── Manages field agents (notaries, collectors, techs)
│   └── AI document inspection with adaptive learning
│   └── Completed services trigger VERTEX invoicing
│   └── Complex engagements create ATLAS projects
│
├── ATLAS (Execute Projects)
│   └── Creates invoices via VERTEX
│   └── Receives complex service engagements from PRISM
│
├── VERTEX (Financial Command Center)
│   └── Consolidates all revenue/expenses
│   └── PRISM services auto-generate invoice line items
│   └── Tracks field agent payments as expenses
│
├── LBPC (Surplus Recovery)
│   └── Creates invoices via VERTEX
│
├── GBIS (Win Grants)
│   └── Tracks funding via VERTEX
│
└── COMPASS™ (Quality Assurance)
    └── Validates all proposals across GPSS/GBIS/DDCSS
```

---

## **Quick Reference:**

| Acronym | Full Name | Primary Function |
|---------|-----------|------------------|
| **NEXUS** | Network for Execution & Unified Systems | Complete business operating system |
| **GPSS** | Government Procurement Strategic System | Government contracting |
| **ATLAS** | Advanced Task & Logistics Automation System | Project management |
| **DDCSS** | Diversity Division Corporate Success System | Corporate sales |
| **PRISM** | Professional Resource Inspection & Service Management | Field service dispatch & document verification |
| **LBPC** | Lead & Proposal Builder for Claims | Surplus recovery |
| **VERTEX** | Financial Excellence & Revenue Tracking Executive System | Financial management |
| **GBIS** | Grant Business Intelligence System | Grant intelligence |
| **COMPASS™** | Compliant Optimization & Messaging Performance Assessment System | Proposal quality assurance |

---

## **Three Vendor Types in NEXUS:**

| Role | System | What They Do | Examples |
|------|--------|-------------|----------|
| **Suppliers** | GPSS | Sell products, provide quotes | Grainger, Fastenal, Master Lock |
| **Subcontractors** | Sub Portal | Do project work under DDI as prime | Pressure washers, landscapers, janitorial |
| **Field Agents** | PRISM | Accept orders, execute field services, upload scanbacks | Notaries, drug test collectors, DNA techs, fingerprint techs, couriers |

**These are three distinct roles with three distinct portal experiences. Never mix terminology.**

---

## **Marketing Usage:**

**External Communications:**
- Use COMPASS™ (with trademark symbol)
- Never reference ProposalBio™ publicly
- Tagline: "Precision Validated. Competition Ready."
- PRISM: "See every detail. Miss nothing."

**Internal Documentation:**
- Backend code: `proposalbio_module.py`
- Internal reference: ProposalBio™
- Technical discussions: ProposalBio system
- PRISM backend: `prism_module.py` (planned)
- PRISM frontend: `PRISMSystem.tsx` (planned)

---

**Last Updated:** February 13, 2026  
**Total Systems:** 8  
**Status:** 7 systems operational, PRISM in architecture phase
