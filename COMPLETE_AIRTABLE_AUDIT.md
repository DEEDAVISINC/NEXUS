# COMPLETE AIRTABLE TABLES AUDIT
## Which Tables Exist, Which Are Missing, Which Are Incomplete

**Date:** January 21, 2026  
**Purpose:** Identify all tables needed by NEXUS backend and their status

---

## 🟢 TABLES THAT SHOULD EXIST (Verify These)

### **GPSS SYSTEM - Government Contracting**

| Table Name | Status | Priority | Notes |
|-----------|--------|----------|-------|
| `GPSS OPPORTUNITIES` | ✅ Should exist | CRITICAL | Core opportunities table |
| `GPSS CONTACTS` | ✅ Should exist | HIGH | Contact management |
| `GPSS PRODUCTS` | ✅ Should exist | MEDIUM | Product catalog |
| `GPSS SUPPLIERS` | ✅ Should exist | HIGH | Product suppliers (for laptops, etc.) |
| `GPSS Supplier Quotes` | ✅ Should exist | HIGH | Quotes from product suppliers |
| `GPSS Supplier Orders` | ✅ Should exist | MEDIUM | Purchase orders for products |

---

### **ATLAS SYSTEM - Project Management**

| Table Name | Status | Priority | Notes |
|-----------|--------|----------|-------|
| `ATLAS Projects` | ✅ Should exist | HIGH | Project tracking |
| `ATLAS RFP Analysis` | ⚠️ May be missing | MEDIUM | RFP analysis storage |
| `ATLAS WBS` | ⚠️ May be missing | MEDIUM | Work breakdown structure |
| `ATLAS Change Orders` | ⚠️ May be missing | LOW | Change order tracking |

---

### **DDCSS SYSTEM - Corporate Sales**

| Table Name | Status | Priority | Notes |
|-----------|--------|----------|-------|
| `DDCSS Prospects` | ✅ Should exist | HIGH | Corporate prospects |
| `DDCSS Blueprints` | ⚠️ May be missing | MEDIUM | Blueprint frameworks |
| `DDCSS AI Responses` | ⚠️ May be missing | LOW | AI response analysis |

---

### **LBPC SYSTEM - Legal Services**

| Table Name | Status | Priority | Notes |
|-----------|--------|----------|-------|
| `LBPC Leads` | ✅ Should exist | HIGH | Legal leads/cases |
| `LBPC Documents` | ⚠️ May be missing | MEDIUM | Document tracking |
| `LBPC Tasks` | ⚠️ May be missing | MEDIUM | Task management |

---

### **VERTEX SYSTEM - Financial Tracking**

| Table Name | Status | Priority | Notes |
|-----------|--------|----------|-------|
| `Invoices` | ✅ Should exist | CRITICAL | Invoice management |
| `VERTEX INVOICES` | ⚠️ Check if duplicate | HIGH | May be same as "Invoices" |
| `VERTEX EXPENSES` | ⚠️ May be missing | HIGH | Expense tracking |

---

### **VENDOR PORTAL MINING**

| Table Name | Status | Priority | Notes |
|-----------|--------|----------|-------|
| `Vendor Portals` | ✅ Should exist | MEDIUM | Portal tracking |
| `Mining Targets` | ✅ Should exist | MEDIUM | Mining targets |

---

## 🔴 TABLES THAT ARE DEFINITELY MISSING

### **1. SUBCONTRACTOR SYSTEM** ⚠️ **CRITICAL - NEEDED NOW**

| Table Name | Status | Priority | What It's For |
|-----------|--------|----------|---------------|
| `GPSS SUBCONTRACTORS` | ❌ **MISSING** | **CRITICAL** | Service subcontractors database |
| `GPSS SUBCONTRACTOR QUOTES` | ❌ **MISSING** | **CRITICAL** | Quotes from subcontractors |
| `GPSS Teaming Arrangements` | ❌ **MISSING** | HIGH | Teaming agreement tracking |

**Why critical:** You just added subcontractor endpoints but tables don't exist!

---

### **2. AI RECOMMENDATION SYSTEM** ⚠️ **CRITICAL - NEEDED NOW**

| Table Name | Status | Priority | What It's For |
|-----------|--------|----------|---------------|
| `AI RECOMMENDATIONS` | ❌ **MISSING** | **CRITICAL** | AI suggestion tracking |
| `COMPANY CAPABILITIES` | ❌ **MISSING** | **HIGH** | Your skills inventory |
| `AI LEARNING` | ❌ **MISSING** | MEDIUM | Learning/improvement tracking |

**Why critical:** New AI recommendation system won't work without these!

---

### **3. FULFILLMENT SYSTEM** ⚠️ **HIGH PRIORITY**

| Table Name | Status | Priority | What It's For |
|-----------|--------|----------|---------------|
| `FULFILLMENT CONTRACTS` | ❌ **MISSING** | HIGH | Multi-delivery contracts |
| `FULFILLMENT DELIVERIES` | ❌ **MISSING** | HIGH | Individual delivery tracking |
| `FULFILLMENT INVENTORY` | ❌ **MISSING** | HIGH | Inventory management |
| `FULFILLMENT PURCHASE ORDERS` | ❌ **MISSING** | HIGH | PO tracking |

**Why high priority:** Backend code references these extensively!

---

### **4. RSS FEED SYSTEM**

| Table Name | Status | Priority | What It's For |
|-----------|--------|----------|---------------|
| `RSS Feeds` | ⚠️ Unknown | MEDIUM | RSS feed tracking |

---

## 📊 PRIORITY SUMMARY

### **🔴 CREATE IMMEDIATELY (Critical):**

1. **GPSS SUBCONTRACTORS** (20 fields) - Subcontractor database
2. **GPSS SUBCONTRACTOR QUOTES** (21 fields) - Service quotes
3. **AI RECOMMENDATIONS** (11 fields) - AI suggestion tracking
4. **COMPANY CAPABILITIES** (7 fields) - Your skills inventory

**Total: 4 tables, ~15 minutes setup**

---

### **🟡 CREATE SOON (High Priority):**

5. **FULFILLMENT CONTRACTS** - Multi-delivery tracking
6. **FULFILLMENT DELIVERIES** - Delivery records
7. **FULFILLMENT INVENTORY** - Stock management
8. **FULFILLMENT PURCHASE ORDERS** - Supplier POs
9. **GPSS Teaming Arrangements** - Subcontractor agreements
10. **VERTEX EXPENSES** - Expense tracking

**Total: 6 tables, ~30 minutes setup**

---

### **⚪ CREATE Eventually (Medium/Low Priority):**

11. **AI LEARNING** - Learning system tracking
12. **ATLAS RFP Analysis** - RFP storage
13. **ATLAS WBS** - Work breakdown
14. **ATLAS Change Orders** - Change tracking
15. **DDCSS Blueprints** - Blueprint storage
16. **DDCSS AI Responses** - Response tracking
17. **LBPC Documents** - Document tracking
18. **LBPC Tasks** - Task management

**Total: 8 tables**

---

## 🎯 ACTION PLAN

### **STEP 1: Critical Tables (Do This First - 15 min)**

Create these 4 tables to unblock your AI recommendation and subcontractor systems:

**A. Subcontractor Tables (See SUBCONTRACTOR_TABLES_NEEDED.md)**
- `GPSS SUBCONTRACTORS` (20 fields)
- `GPSS SUBCONTRACTOR QUOTES` (21 fields)

**B. AI Recommendation Tables (See Below)**
- `AI RECOMMENDATIONS` (11 fields)
- `COMPANY CAPABILITIES` (7 fields)

---

### **STEP 2: High Priority Tables (Do This Week - 30 min)**

Create fulfillment and financial tables:

**C. Fulfillment System (See FULFILLMENT_AIRTABLE_SETUP.md)**
- `FULFILLMENT CONTRACTS`
- `FULFILLMENT DELIVERIES`
- `FULFILLMENT INVENTORY`
- `FULFILLMENT PURCHASE ORDERS`

**D. Financial/Teaming**
- `VERTEX EXPENSES`
- `GPSS Teaming Arrangements`

---

### **STEP 3: Optional Tables (Do As Needed)**

Create project management and tracking tables:
- ATLAS tables (RFP Analysis, WBS, Change Orders)
- DDCSS tables (Blueprints, AI Responses)
- LBPC tables (Documents, Tasks)
- AI LEARNING

---

## 📋 DETAILED SETUP GUIDES

### **🔴 CRITICAL TABLE 1: GPSS SUBCONTRACTORS**

**Purpose:** Store service subcontractors (different from product suppliers)

Create table with these **20 fields:**

| # | Field Name | Type | Settings |
|---|-----------|------|----------|
| 1 | `COMPANY_NAME` | Single line text | Primary field |
| 2 | `SERVICE_TYPE` | Single line text | e.g., "Aircraft Maintenance" |
| 3 | `CAPABILITIES` | Long text | What services they provide |
| 4 | `CITY` | Single line text | - |
| 5 | `STATE` | Single line text | - |
| 6 | `LOCATION` | Single line text | Full location string |
| 7 | `PHONE` | Phone | - |
| 8 | `EMAIL` | Email | Contact email |
| 9 | `CONTACT_EMAIL` | Email | Same as EMAIL |
| 10 | `WEBSITE` | URL | - |
| 11 | `DESCRIPTION` | Long text | Company description |
| 12 | `PAST_PERFORMANCE` | Long text | Previous work history |
| 13 | `RATING` | Number | 0-5, Precision: 1 decimal |
| 14 | `STATUS` | Single select | Options: `Active`, `Available`, `Inactive` |
| 15 | `CERTIFICATIONS` | Long text | GSA, 8(a), WOSB, etc. |
| 16 | `DISCOVERY_METHOD` | Single line text | How you found them |
| 17 | `DISCOVERY_DATE` | Date | When added |
| 18 | `RELATIONSHIP_STATUS` | Single line text | New, Established, etc. |
| 19 | `CONTRACTS_WON_TOGETHER` | Number | Count |
| 20 | `NOTES` | Long text | Additional info |

---

### **🔴 CRITICAL TABLE 2: GPSS SUBCONTRACTOR QUOTES**

**Purpose:** Track RFQ/RFP sent to subcontractors and their responses

Create table with these **21 fields:**

| # | Field Name | Type | Settings |
|---|-----------|------|----------|
| 1 | `QUOTE_ID` | Auto number | Primary field |
| 2 | `OPPORTUNITY` | Link to record | Link to: `GPSS OPPORTUNITIES` |
| 3 | `SUBCONTRACTOR` | Link to record | Link to: `GPSS SUBCONTRACTORS` |
| 4 | `STATUS` | Single select | Options: `Pending`, `Received`, `Declined`, `Selected` |
| 5 | `RFQ_SENT_DATE` | Date | When RFQ was sent |
| 6 | `QUOTE_DUE_DATE` | Date | Response deadline |
| 7 | `EMAIL_SUBJECT` | Single line text | RFQ email subject |
| 8 | `EMAIL_BODY` | Long text | RFQ email content |
| 9 | `RESPONSE_TEXT` | Long text | Their quote response |
| 10 | `QUOTE_AMOUNT` | Currency | Their quoted price |
| 11 | `RESPONSE_TIME_DAYS` | Number | How fast they responded |
| 12 | `AI_SCORE` | Number | 0-100 AI score |
| 13 | `SCORE_REASONING` | Long text | Why AI scored it this way |
| 14 | `RECOMMENDATION` | Single line text | AI recommendation |
| 15 | `SELECTED` | Checkbox | User selected this quote |
| 16 | `MARKUP_PERCENTAGE` | Number | Your markup % |
| 17 | `MARKUP_AMOUNT` | Currency | Dollar markup |
| 18 | `FINAL_BID_AMOUNT` | Currency | What you bid to govt |
| 19 | `ESTIMATED_PROFIT` | Currency | Your profit |
| 20 | `NOTES` | Long text | Additional notes |
| 21 | `CREATED` | Created time | Auto-tracked |

---

### **🔴 CRITICAL TABLE 3: AI RECOMMENDATIONS**

**Purpose:** Track all AI suggestions and your approve/deny decisions

Create table with these **11 fields:**

| # | Field Name | Type | Settings |
|---|-----------|------|----------|
| 1 | `OPPORTUNITY` | Link to record | Link to: `GPSS OPPORTUNITIES` |
| 2 | `TYPE` | Single select | Options: `Capability Gap Analysis`, `Subcontractor Recommendation`, `Supplier Recommendation`, `Compliance Check` |
| 3 | `RECOMMENDATION` | Long text | AI's recommendation |
| 4 | `CONFIDENCE` | Number | 0-100, Integer |
| 5 | `REASONING` | Long text | Why AI suggests this |
| 6 | `STATUS` | Single select | Options: `Pending Approval`, `Approved`, `Denied`, `Modified` |
| 7 | `USER_DECISION` | Single select | Options: `APPROVED`, `DENIED`, `MODIFIED` |
| 8 | `USER_NOTES` | Long text | Your reasoning |
| 9 | `SELECTED_OPTION` | Single line text | What you picked (if different) |
| 10 | `CREATED` | Date | Include time |
| 11 | `DECIDED_AT` | Date | Include time |

---

### **🔴 CRITICAL TABLE 4: COMPANY CAPABILITIES**

**Purpose:** Your skills inventory for AI gap analysis

Create table with these **7 fields:**

| # | Field Name | Type | Settings |
|---|-----------|------|----------|
| 1 | `CAPABILITY_NAME` | Single line text | e.g., "Project Management" |
| 2 | `SKILL_LEVEL` | Single select | Options: `Expert`, `Intermediate`, `Beginner`, `None` |
| 3 | `CAPACITY` | Single select | Options: `High`, `Medium`, `Low` |
| 4 | `HOURLY_RATE` | Currency | USD |
| 5 | `TEAM_SIZE` | Number | Integer |
| 6 | `CERTIFICATIONS` | Long text | - |
| 7 | `NOTES` | Long text | - |

**Populate with:**
- Project Management: Expert, High, $150
- Government Contracting: Expert, High, $150
- Proposal Writing: Expert, High, $125
- Product Sourcing: Expert, High, $100
- Cybersecurity: None, Low, $0 ← Include gaps!
- Software Development: None, Low, $0
- Engineering: None, Low, $0

---

## 🟡 HIGH PRIORITY TABLE 5: GPSS Teaming Arrangements

**Purpose:** Track teaming agreements with subcontractors

Create table with these **15 fields:**

| # | Field Name | Type | Settings |
|---|-----------|------|----------|
| 1 | `ARRANGEMENT_NAME` | Single line text | Primary |
| 2 | `OPPORTUNITY` | Link to record | Link to: `GPSS OPPORTUNITIES` |
| 3 | `SUBCONTRACTOR` | Link to record | Link to: `GPSS SUBCONTRACTORS` |
| 4 | `ROLE` | Single select | Options: `Prime`, `Sub`, `Joint Venture`, `Teaming` |
| 5 | `YOUR_WORKSHARE_PERCENT` | Number | Your % of work |
| 6 | `YOUR_WORKSHARE_VALUE` | Currency | Your $ amount |
| 7 | `SUB_WORKSHARE_PERCENT` | Number | Their % of work |
| 8 | `SUB_WORKSHARE_VALUE` | Currency | Their $ amount |
| 9 | `COMPLIANT` | Checkbox | Meets 50% rule? |
| 10 | `AGREEMENT_STATUS` | Single select | Options: `Proposed`, `Signed`, `Active`, `Completed`, `Cancelled` |
| 11 | `SIGNED_DATE` | Date | When signed |
| 12 | `SCOPE_OF_WORK` | Long text | What each party does |
| 13 | `AGREEMENT_DOCUMENT` | Attachment | Signed agreement |
| 14 | `NOTES` | Long text | - |
| 15 | `CREATED` | Created time | Auto |

---

## 🟡 HIGH PRIORITY: FULFILLMENT TABLES

See full details in: `FULFILLMENT_AIRTABLE_SETUP.md`

**Quick summary - Create these 4 tables:**
1. `FULFILLMENT CONTRACTS` - Master contract records
2. `FULFILLMENT DELIVERIES` - Individual delivery tracking
3. `FULFILLMENT INVENTORY` - Stock levels
4. `FULFILLMENT PURCHASE ORDERS` - Supplier POs

---

## 🟡 HIGH PRIORITY TABLE: VERTEX EXPENSES

**Purpose:** Track all expenses (COGS, labor, overhead)

Create table with these **12 fields:**

| # | Field Name | Type | Settings |
|---|-----------|------|----------|
| 1 | `EXPENSE_NUMBER` | Auto number | Primary |
| 2 | `OPPORTUNITY` | Link to record | Link to: `GPSS OPPORTUNITIES` (optional) |
| 3 | `PROJECT` | Link to record | Link to: `ATLAS Projects` (optional) |
| 4 | `EXPENSE_TYPE` | Single select | Options: `COGS`, `Labor`, `Overhead`, `Materials`, `Subcontractor`, `Other` |
| 5 | `DESCRIPTION` | Long text | What the expense is for |
| 6 | `AMOUNT` | Currency | Expense amount |
| 7 | `EXPENSE_DATE` | Date | When incurred |
| 8 | `VENDOR` | Single line text | Who you paid |
| 9 | `PAYMENT_STATUS` | Single select | Options: `Pending`, `Paid`, `Overdue` |
| 10 | `PAYMENT_DATE` | Date | When paid |
| 11 | `CATEGORY` | Single select | Options: `Direct Cost`, `Indirect Cost`, `Fixed`, `Variable` |
| 12 | `NOTES` | Long text | - |

---

## ✅ VERIFICATION CHECKLIST

### **Check These Existing Tables:**

**For GPSS OPPORTUNITIES, verify it has:**
- [ ] `TITLE` field
- [ ] `DESCRIPTION` field
- [ ] `AGENCY NAME` field
- [ ] `SOLICITATION NUMBER` field
- [ ] `Type` field (Product vs Service)
- [ ] `SET_ASIDE` field

**For GPSS SUPPLIERS, verify it has:**
- [ ] `COMPANY_NAME` field
- [ ] `PRODUCTS` field
- [ ] `RATING` field
- [ ] `PAYMENT_TERMS` field
- [ ] `GSA_SCHEDULE` field
- [ ] `CONTACT_EMAIL` field

**For Invoices, verify it has:**
- [ ] `Source System` field
- [ ] `Client Name` field
- [ ] `Contract Number` field
- [ ] `Invoice Status` field
- [ ] `Invoice Date` field

---

## 🎯 IMMEDIATE ACTION ITEMS

**RIGHT NOW (15 minutes):**
1. Create `GPSS SUBCONTRACTORS` table (20 fields)
2. Create `GPSS SUBCONTRACTOR QUOTES` table (21 fields)
3. Create `AI RECOMMENDATIONS` table (11 fields)
4. Create `COMPANY CAPABILITIES` table (7 fields)
5. Add 5-10 capabilities to COMPANY CAPABILITIES

**THIS WEEK (30 minutes):**
6. Create fulfillment tables (4 tables)
7. Create `GPSS Teaming Arrangements` table
8. Create `VERTEX EXPENSES` table

**OPTIONAL (As Needed):**
9. Create ATLAS project management tables
10. Create DDCSS corporate sales tables
11. Create LBPC document/task tables

---

## 📞 QUICK REFERENCE

**Subcontractor Setup:** See `SUBCONTRACTOR_TABLES_NEEDED.md`  
**AI Recommendations Setup:** See `AIRTABLE_SETUP_AI_RECOMMENDATIONS.md`  
**Fulfillment Setup:** See `FULFILLMENT_AIRTABLE_SETUP.md` (if exists)

---

**This is your complete Airtable audit. Start with the 4 critical tables and you'll unblock both major systems!** 🚀
