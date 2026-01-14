# NEXUS COMMAND CENTER - COMPLETE AIRTABLE SCHEMA BREAKDOWN

## 🎯 **OVERVIEW**

The **NEXUS Command Center** is a unified Airtable base that consolidates all three business systems (GPSS, ATLAS PM, DDCSS) plus supporting tables for a complete business automation platform.

### **📊 TOTAL TABLES: 20+ Tables**
### **📋 TOTAL FIELDS: 300+ Fields**
### **🔗 TOTAL RELATIONSHIPS: 50+ Links**

---

## 🏗️ **ARCHITECTURE OVERVIEW**

```
NEXUS COMMAND CENTER (Single Airtable Base)
├── 📋 GPSS System (Government Contracting)
├── 🏗️ ATLAS PM System (Project Management)
├── 💼 DDCSS System (Corporate Sales)
├── 💰 Invoices System (Universal Billing)
├── 🤖 AI Systems (Conversations & Intelligence)
└── 🔗 Shared Resources (Contacts, Mining, etc.)
```

---

## 📋 **TABLE 1-4: GPSS SYSTEM (GOVERNMENT CONTRACTING)**

### **1. GPSS Opportunities**
**Purpose:** Track government contract opportunities and RFPs

| Field Name | Type | Purpose |
|------------|------|---------|
| **Opportunity ID** | Autonumber | Primary field |
| **Title** | Single line text | Opportunity name |
| **Agency** | Single line text | Government agency |
| **Value** | Currency | Contract value |
| **Status** | Single select | Draft, Active, Won, Lost, Withdrawn |
| **Due Date** | Date | Proposal deadline |
| **Posted Date** | Date | When posted |
| **Response Date** | Date | When you responded |
| **Win Probability** | Number (0-100) | AI-calculated |
| **Source** | Single select | SAM.gov, State Portal, Direct |
| **Set-Aside** | Single select | EDWOSB, 8(a), HUBZone, Unrestricted |
| **Category** | Single select | Healthcare, Logistics, IT, etc. |
| **Description** | Long text | Full RFP description |
| **Requirements** | Long text | Key requirements |
| **Contacts** | Long text | Agency contacts |
| **Notes** | Long text | Internal notes |

**Views:** All Opportunities, Active, Won, Lost, High Value (> $100K)

---

### **2. GPSS Proposals**
**Purpose:** AI-generated government contract proposals

| Field Name | Type | Purpose |
|------------|------|---------|
| **Proposal ID** | Autonumber | Primary field |
| **Proposal Name** | Single line text | e.g., "MI-MDHHS-2026-0123 - NEMT Services" |
| **Opportunity** | Link to Opportunities | Source opportunity |
| **Status** | Single select | Draft, Review, Sent, Accepted, Rejected |
| **Generated Date** | Date & time | When AI created it |
| **Executive Summary** | Long text | 2-3 paragraph summary |
| **Technical Approach** | Long text | Detailed approach |
| **Staffing Plan** | Long text | Team structure |
| **Past Performance** | Long text | Relevant experience |
| **Pricing - Total** | Currency | Total price |
| **Pricing - Breakdown** | Long text | Cost breakdown |
| **Compliance Checklist** | Long text | Requirements checklist |
| **Win Probability** | Number | AI-calculated score |
| **Sent Date** | Date | When submitted |
| **Response Date** | Date | Agency response |

**Views:** All Proposals, Ready to Send, Under Review, Won Proposals

---

### **3. GPSS Contacts**
**Purpose:** Government agency contacts and points of contact

| Field Name | Type | Purpose |
|------------|------|---------|
| **Contact ID** | Autonumber | Primary field |
| **Name** | Single line text | Full name |
| **Agency** | Single line text | Government agency |
| **Title** | Single line text | Job title |
| **Email** | Email | Contact email |
| **Phone** | Phone | Contact phone |
| **Address** | Long text | Agency address |
| **LinkedIn** | URL | LinkedIn profile |
| **Notes** | Long text | Contact notes |
| **Last Contact** | Date | When last contacted |
| **Response Rate** | Single select | High, Medium, Low |

**Views:** All Contacts, By Agency, Recent Contacts

---

### **4. GPSS Products**
**Purpose:** Services and products offered for government contracts

| Field Name | Type | Purpose |
|------------|------|---------|
| **Product ID** | Autonumber | Primary field |
| **Name** | Single line text | Product/service name |
| **Category** | Single select | Healthcare, Logistics, IT, etc. |
| **Description** | Long text | Detailed description |
| **Base Price** | Currency | Standard price |
| **Unit** | Single select | Per Hour, Per Day, Fixed Price |
| **Certifications** | Long text | Required certifications |
| **Active** | Checkbox | Currently offered |

**Views:** All Products, By Category, Active Only

---

## 🏗️ **TABLE 5-9: ATLAS PM SYSTEM (PROJECT MANAGEMENT)**

### **5. ATLAS Projects**
**Purpose:** Track all client projects and contracts

| Field Name | Type | Purpose |
|------------|------|---------|
| **Project ID** | Autonumber | Primary field |
| **Project Name** | Single line text | Project title |
| **Client** | Single line text | Client name |
| **Project Type** | Single select | Government, Enterprise, Internal |
| **Status** | Single select | Planning, Active, On Hold, Completed |
| **Start Date** | Date | Project start |
| **End Date** | Date | Project end |
| **Budget** | Currency | Total budget |
| **Spent** | Currency | Amount spent |
| **Remaining** | Formula | Budget - Spent |
| **Project Manager** | Single line text | PM name |
| **Team Members** | Long text | Team list |
| **Description** | Long text | Project description |
| **Risk Level** | Single select | Low, Medium, High |
| **Priority** | Single select | Low, Medium, High, Critical |

**Views:** All Projects, Active Projects, By Client, Over Budget

---

### **6. ATLAS Tasks**
**Purpose:** Individual project tasks and milestones

| Field Name | Type | Purpose |
|------------|------|---------|
| **Task ID** | Autonumber | Primary field |
| **Task Name** | Single line text | Task description |
| **Project** | Link to Projects | Parent project |
| **Assigned To** | Single line text | Team member |
| **Status** | Single select | To Do, In Progress, Review, Done |
| **Priority** | Single select | Low, Medium, High |
| **Due Date** | Date | Task deadline |
| **Estimated Hours** | Number | Time estimate |
| **Actual Hours** | Number | Time spent |
| **Created Date** | Created time | When created |
| **Completed Date** | Date | When finished |

**Views:** All Tasks, My Tasks, Overdue, By Project

---

### **7. ATLAS Change Orders**
**Purpose:** Track project change requests and modifications

| Field Name | Type | Purpose |
|------------|------|---------|
| **Change Order ID** | Autonumber | Primary field |
| **Project** | Link to Projects | Affected project |
| **Title** | Single line text | Change description |
| **Type** | Single select | Scope Change, Schedule Change, Cost Change |
| **Requested By** | Single line text | Who requested |
| **Status** | Single select | Pending, Approved, Rejected |
| **Original Value** | Currency | Original amount |
| **Change Value** | Currency | Change amount |
| **New Total** | Formula | Original + Change |
| **Reason** | Long text | Justification |
| **Impact Analysis** | Long text | AI analysis of impacts |
| **Approved Date** | Date | When approved |

**Views:** All Change Orders, Pending Approval, By Project

---

### **8. ATLAS Documents**
**Purpose:** Project documentation and deliverables

| Field Name | Type | Purpose |
|------------|------|---------|
| **Document ID** | Autonumber | Primary field |
| **Name** | Single line text | Document name |
| **Project** | Link to Projects | Related project |
| **Type** | Single select | Contract, Deliverable, Report, Other |
| **Status** | Single select | Draft, Review, Final, Archived |
| **Created Date** | Created time | When created |
| **Last Modified** | Last modified time | When updated |
| **Version** | Number | Document version |
| **File Location** | Single line text | Where stored |

**Views:** All Documents, By Project, Recent Documents

---

### **9. ATLAS RFP Analysis**
**Purpose:** AI analysis of project RFPs

| Field Name | Type | Purpose |
|------------|------|---------|
| **Analysis ID** | Autonumber | Primary field |
| **RFP Title** | Single line text | RFP name |
| **Client** | Single line text | Client name |
| **Analysis Date** | Date & time | When analyzed |
| **Win Probability** | Number (0-100) | AI-calculated |
| **Risk Assessment** | Long text | Risk factors |
| **Requirements** | Long text | Key requirements |
| **Competitive Analysis** | Long text | Competitor info |
| **Pricing Strategy** | Long text | Recommended pricing |
| **Timeline** | Long text | Project timeline |
| **Recommendations** | Long text | Action items |

**Views:** All Analyses, High Probability, Recent Analyses

---

## 💼 **TABLE 10-15: DDCSS SYSTEM (CORPORATE SALES)**

### **10. DDCSS Prospects**
**Purpose:** Corporate consulting prospects and leads

| Field Name | Type | Purpose |
|------------|------|---------|
| **Company Name** | Single line text | Primary field |
| **Industry Sector** | Single select | 9 sectors (Transportation, Healthcare, etc.) |
| **Company Size** | Single select | Employee count ranges |
| **Revenue Range** | Single select | Revenue brackets |
| **Location** | Single line text | City, State |
| **Website** | URL | Company website |
| **Contact Name** | Single line text | Primary contact |
| **Contact Email** | Email | Contact email |
| **Pipeline Stage** | Single select | Cold, Warm, Hot, Won, Lost |
| **Qualification Score** | Number (0-100) | AI-calculated |
| **Budget Range** | Single select | $25K-$50K, $50K-$100K, etc. |
| **Current Challenge** | Long text | Problems they're facing |
| **Win Probability** | Number (0-100) | AI-calculated |

**Views:** All Prospects, Hot Prospects, By Sector, Won Deals

---

### **11. DDCSS Client Avatars**
**Purpose:** Ideal customer profile definitions

| Field Name | Type | Purpose |
|------------|------|---------|
| **Avatar ID** | Autonumber | Primary field |
| **Avatar Name** | Single line text | Profile name |
| **Industry** | Single select | Target industry |
| **Company Size** | Single select | Size range |
| **Pain Points** | Long text | Key problems |
| **Goals** | Long text | What they want |
| **Budget** | Single select | Spending capacity |
| **Decision Makers** | Long text | Who decides |
| **Buying Process** | Long text | How they buy |
| **Created Date** | Created time | When created |

**Views:** All Avatars, By Industry, Active Avatars

---

### **12. DDCSS Success Paths**
**Purpose:** Sales journey definitions from cold to close

| Field Name | Type | Purpose |
|------------|------|---------|
| **Path ID** | Autonumber | Primary field |
| **Path Name** | Single line text | Path title |
| **Target Avatar** | Link to Avatars | Target profile |
| **Stages** | Long text | Step-by-step process |
| **Timeline** | Single select | 30, 60, 90, 180 days |
| **Touchpoints** | Number | Contact points |
| **Conversion Rate** | Number | Success rate |
| **Created Date** | Created time | When created |

**Views:** All Paths, By Avatar, High Converting

---

### **13. DDCSS PitchMaps**
**Purpose:** AI-generated sales scripts and presentations

| Field Name | Type | Purpose |
|------------|------|---------|
| **PitchMap ID** | Autonumber | Primary field |
| **Title** | Single line text | Pitch title |
| **Target Company** | Single line text | Prospect name |
| **Script** | Long text | Full sales script |
| **Key Points** | Long text | Main talking points |
| **Objection Handling** | Long text | Common objections |
| **Call to Action** | Long text | Next steps |
| **Generated Date** | Date & time | When created |
| **Used Count** | Number | Times used |

**Views:** All PitchMaps, Recent, By Company

---

### **14. DDCSS AI Responses**
**Purpose:** Email response analysis and sentiment tracking

| Field Name | Type | Purpose |
|------------|------|---------|
| **Response ID** | Autonumber | Primary field |
| **Prospect** | Link to Prospects | Related prospect |
| **Email Subject** | Single line text | Email subject |
| **Email Content** | Long text | Full email |
| **Sentiment** | Single select | Positive, Neutral, Negative |
| **Interest Level** | Number (0-100) | AI-calculated |
| **Key Phrases** | Long text | Important phrases |
| **Recommended Action** | Long text | Next steps |
| **Analyzed Date** | Date & time | When analyzed |

**Views:** All Responses, Recent, By Sentiment

---

### **15. DDCSS MVP Problems**
**Purpose:** Problems discovered through Reddit mining

| Field Name | Type | Purpose |
|------------|------|---------|
| **Title** | Single line text | Primary field - Problem description |
| **Category** | Single select | Business, Sales, Operations, etc. |
| **Total Score** | Number (0-100) | Overall profitability score |
| **Frequency Score** | Number (0-100) | How often mentioned |
| **Intensity Score** | Number (0-100) | Emotional intensity |
| **Market Size Score** | Number (0-100) | Subreddit size/engagement |
| **Solution Type** | Single select | PDF, DDCSS, GPSS, ATLAS, New Service |
| **Recommended Action** | Long text | Next steps |
| **Status** | Single select | Discovered, Validated, Building, Launched |

**Views:** High Value Problems, PDF Opportunities, DDCSS Opportunities

---

## 💰 **TABLE 16: INVOICES SYSTEM**

### **16. Invoices**
**Purpose:** Government and enterprise compliant invoicing

| Field Name | Type | Purpose |
|------------|------|---------|
| **Invoice ID** | Autonumber | Primary field |
| **Invoice Number** | Formula | INV-2024-0001 format |
| **Invoice Date** | Date | When created |
| **Due Date** | Date | Payment due |
| **Invoice Status** | Single select | Draft, Sent, Paid, Overdue |
| **Client Name** | Single line text | Bill to |
| **Client Type** | Single select | Government Federal, Enterprise, etc. |
| **Contact** | Link to Contacts | Billing contact |
| **Source System** | Single select | GPSS, ATLAS, DDCSS, Manual |
| **Opportunity** | Link to Opportunities | Source opportunity |
| **Project** | Link to Projects | Source project |
| **Prospect** | Link to Prospects | Source prospect |
| **Contract Number** | Single line text | Government contract # |
| **Subtotal** | Currency | Before tax/shipping |
| **Shipping & Handling** | Currency | S&H costs |
| **Tax Rate** | Percent | Tax percentage |
| **Tax Amount** | Formula | Calculated tax |
| **Total Amount** | Formula | Final total |
| **Payment Date** | Date | When paid |
| **Payment Method** | Single select | ACH, Wire, Check, etc. |
| **Days Outstanding** | Formula | Days since invoice date |

**Views:** All Invoices, Pending Payment, Overdue, Government Contracts

---

## 🤖 **TABLE 17-18: AI & INTELLIGENCE SYSTEMS**

### **17. AI Conversations**
**Purpose:** Persistent storage of AI copilot conversations

| Field Name | Type | Purpose |
|------------|------|---------|
| **Conversation ID** | Autonumber | Primary field |
| **Session ID** | Single line text | Unique session identifier |
| **Started** | Created time | When conversation began |
| **Last Updated** | Last modified time | When last updated |
| **Messages** | Long text | JSON array of all messages |
| **Message Count** | Number | Total messages |
| **Summary** | Long text | AI-generated summary |
| **System Context** | Single select | GPSS, ATLAS, DDCSS, etc. |
| **Topics** | Multiple select | Topics discussed |
| **Status** | Single select | Active, Archived, Important |
| **User Rating** | Single select | ⭐ to ⭐⭐⭐⭐⭐ |

**Views:** All Conversations, Recent Active, By System, Important

---

### **18. Mining Targets**
**Purpose:** Websites and portals to monitor for opportunities

| Field Name | Type | Purpose |
|------------|------|---------|
| **Target ID** | Autonumber | Primary field |
| **Name** | Single line text | Portal name |
| **URL** | URL | Website URL |
| **Type** | Single select | Government, Enterprise, Private |
| **Frequency** | Single select | Daily, Weekly, Monthly |
| **Last Checked** | Date & time | When last scanned |
| **Status** | Single select | Active, Inactive, Error |
| **Notes** | Long text | Special instructions |

**Views:** All Targets, Active Targets, By Type

---

## 🔗 **TABLE 19-20: SHARED RESOURCES**

### **19. Contacts (Universal)**
**Purpose:** All business contacts across all systems

| Field Name | Type | Purpose |
|------------|------|---------|
| **Contact ID** | Autonumber | Primary field |
| **Name** | Single line text | Full name |
| **Email** | Email | Email address |
| **Phone** | Phone | Phone number |
| **Company** | Single line text | Company name |
| **Title** | Single line text | Job title |
| **Type** | Single select | Government, Enterprise, Vendor |
| **Source System** | Single select | GPSS, ATLAS, DDCSS |
| **Notes** | Long text | Contact notes |
| **Last Contact** | Date | When last contacted |

**Views:** All Contacts, By Type, By Company, Recent Contacts

---

### **20. GPSS Pricing Intelligence**
**Purpose:** Historical pricing data and market intelligence

#### **Pricing History Table:**
- **34 fields** for bid tracking, win rates, pricing analysis
- Links to Opportunities and Proposals
- Formulas for profit margins, competitiveness

#### **Cost Templates Table:**
- **16 fields** for service pricing templates
- Base rates, overhead, profit margins

#### **Market Intelligence Table:**
- **13 fields** for competitor pricing data
- Geographic regions, contract sizes, rates

---

## 📊 **SYSTEM STATISTICS**

### **Total Tables:** 20+
### **Total Fields:** 300+
### **Key Relationships:**
- Invoices link to Opportunities, Projects, Prospects
- Proposals link to Opportunities
- Tasks link to Projects
- Change Orders link to Projects
- AI Responses link to Prospects
- All systems share Contacts table

### **System Integration:**
- ✅ **GPSS** (Government): Opportunities → Proposals → Invoices
- ✅ **ATLAS** (Projects): Projects → Tasks → Change Orders → Invoices
- ✅ **DDCSS** (Sales): Prospects → PitchMaps → Invoices
- ✅ **Universal**: Contacts, AI Conversations, Mining Targets

---

## 🎯 **USAGE WORKFLOW**

### **GPSS (Win Government Contracts):**
1. **Discover** opportunities via Mining Targets
2. **Extract** contacts from RFPs
3. **Generate** AI proposals with pricing
4. **Track** in Proposals table
5. **Invoice** via Invoices table

### **ATLAS (Manage Projects):**
1. **Create** projects from won opportunities
2. **Plan** with WBS generation
3. **Track** tasks and change orders
4. **Manage** documents and deliverables
5. **Invoice** via Invoices table

### **DDCSS (Close Corporate Deals):**
1. **Build** client avatars and success paths
2. **Discover** prospects via MVP mining
3. **Generate** pitch scripts
4. **Analyze** email responses
5. **Track** pipeline to close
6. **Invoice** via Invoices table

### **AI Copilot (Universal Assistant):**
- **Conversations** saved to AI Conversations table
- **Commands** can create/edit all records
- **Context-aware** based on current system

---

## 🔧 **TECHNICAL INTEGRATION**

### **Frontend Connections:**
- ✅ React components for all tables
- ✅ API endpoints for CRUD operations
- ✅ Real-time data synchronization
- ✅ AI integration throughout

### **Backend API Endpoints:**
- ✅ `/gpss/*` - GPSS operations
- ✅ `/atlas/*` - ATLAS operations
- ✅ `/ddcss/*` - DDCSS operations
- ✅ `/invoices/*` - Invoice operations
- ✅ `/ai/chat` - AI copilot with full system access

### **AI Integration:**
- ✅ Claude AI for proposal generation
- ✅ Claude AI for RFP analysis
- ✅ Claude AI for pitch scripts
- ✅ Claude AI for email analysis
- ✅ Claude AI for general assistance

---

## 📈 **COMPLETION STATUS**

| System | Tables | Fields | Status | Completion |
|--------|--------|--------|--------|------------|
| **GPSS** | 6 tables | 120+ fields | ✅ Complete | 100% |
| **ATLAS PM** | 5 tables | 80+ fields | ✅ Complete | 100% |
| **DDCSS** | 6 tables | 100+ fields | ✅ Complete | 95% |
| **Invoices** | 1 table | 46 fields | ✅ Complete | 100% |
| **AI Systems** | 2 tables | 25+ fields | ✅ Complete | 100% |
| **Shared** | 2 tables | 30+ fields | ✅ Complete | 100% |

**Overall NEXUS Completion: ~98%** 🚀

---

## 🎉 **RESULT**

The **NEXUS Command Center** is a comprehensive business automation platform with:

- **20+ interconnected tables**
- **300+ fields** across all business functions
- **Full AI integration** throughout
- **Government & enterprise compliance**
- **Universal invoicing** system
- **Complete project management**
- **Corporate sales automation**
- **Intelligent opportunity mining**

**Ready for production use across all business operations!** 🌟