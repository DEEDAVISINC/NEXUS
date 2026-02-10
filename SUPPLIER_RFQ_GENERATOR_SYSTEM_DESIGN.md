# NEXUS SUPPLIER RFQ GENERATOR - SYSTEM DESIGN
**Auto-Generate Supplier-Facing RFQs from Buyer RFQs**

**Created:** January 30, 2026  
**Purpose:** Protect buyer identity while creating professional supplier quotes  
**Critical Rule:** NEVER reveal end buyer to suppliers

---

## 🎯 PROBLEM STATEMENT

**Current Issue:**
When DEE DAVIS INC receives an RFQ from a buyer (e.g., City of Auburn Hills), we need to get quotes from suppliers. BUT we cannot reveal the buyer's identity to suppliers (they could bypass us and bid direct).

**Solution:**
Auto-generate a DEE DAVIS INC branded RFQ that:
- ✅ Contains all technical specifications
- ✅ Uses generic location (e.g., "Oakland County" not "Auburn Hills")
- ✅ Branded as DEE DAVIS INC RFQ
- ✅ Positions us as the prime contractor
- ❌ NEVER includes buyer name, agency, or solicitation number

---

## 🏗️ SYSTEM ARCHITECTURE

### **INPUT:** Buyer's RFQ/RFP
- PDF, Word doc, or text
- Contains buyer name, agency, location, specs
- May include buyer solicitation number

### **PROCESS:** Transform & Protect
1. Extract technical specifications
2. Remove buyer identifying information
3. Generalize location (city → county/region)
4. Add DEE DAVIS INC branding
5. Generate unique DDI RFQ number
6. Format as professional RFQ document

### **OUTPUT:** Supplier-Facing RFQ
- PDF and/or HTML format
- DEE DAVIS INC branded
- Generic client description
- Complete technical specs
- Ready to send to suppliers

---

## 📋 DATA TRANSFORMATION RULES

### **BUYER INFO → SUPPLIER INFO:**

| Buyer RFQ Says | Supplier RFQ Says |
|----------------|-------------------|
| "City of Auburn Hills" | "Michigan municipal client" |
| "Auburn Hills, MI" | "Oakland County, Michigan" |
| "RFQ #01-30-2026-001" | "DDI-2026-PW-001" (our number) |
| "Stan Torres, Parks Supervisor" | "DEE DAVIS INC Project Manager" |
| "storres@auburnhills.org" | "info@deedavis.biz" |
| "1500 Brown Road, Auburn Hills" | "Multiple locations in Oakland County" |
| "City of Auburn Hills website" | NO LINK (removed) |

### **LOCATION GENERALIZATION:**

| Specific Location | Generalized Location |
|-------------------|---------------------|
| Auburn Hills, MI | Oakland County, MI |
| Canton Township, MI | Wayne County, MI |
| Rock Island, IL | Illinois municipal client |
| San Antonio, TX | Texas utility client |
| Jackson County, MI | Michigan county government |

### **AGENCY TYPE MAPPING:**

| Buyer Type | Generic Description |
|------------|---------------------|
| City of [Name] | "Municipal client in [County]" |
| [Name] Township | "Michigan township" |
| [Name] County | "[State] county government" |
| [Name] Utility | "[State] utility client" |
| Federal Agency | "Federal government client" |

---

## 🔧 SYSTEM COMPONENTS

### **COMPONENT 1: RFQ PARSER**

**Function:** Extract key information from buyer's RFQ

**Extracts:**
- Buyer name/agency
- Location (city, county, state)
- Solicitation number
- Due date
- Scope of work
- Technical specifications
- Quantities
- Insurance requirements
- Special requirements

**Technology:** Python + PDF parsing + NLP

---

### **COMPONENT 2: INFORMATION SANITIZER**

**Function:** Remove/replace buyer identifying information

**Rules:**
1. **Remove:**
   - Buyer name
   - Buyer contact names
   - Buyer email addresses
   - Buyer phone numbers
   - Buyer websites
   - Buyer solicitation numbers
   - Specific addresses (replace with county)

2. **Replace with:**
   - "DEE DAVIS INC municipal client"
   - "Client in [County], [State]"
   - Generic descriptions
   - DEE DAVIS INC contact info

3. **Keep:**
   - Technical specifications
   - Quantities
   - Quality standards
   - Insurance requirements
   - Timeline (adjusted)

---

### **COMPONENT 3: DDI RFQ GENERATOR**

**Function:** Create professional DEE DAVIS INC branded RFQ

**Generates:**
1. **Header:**
   - DEE DAVIS INC logo
   - Unique DDI RFQ number (DDI-YEAR-XXX-###)
   - Issue date
   - Due date (before buyer's deadline)

2. **Project Overview:**
   - Generic client description
   - Project type
   - Contract term
   - Service area (county/region level)

3. **Scope of Work:**
   - Technical specifications (from buyer RFQ)
   - Quantities
   - Quality requirements
   - Performance standards

4. **Submission Requirements:**
   - Pricing format
   - Insurance requirements
   - References
   - Qualifications

5. **Terms & Conditions:**
   - Subcontractor relationship
   - Payment terms (Net 30 after we get paid)
   - Confidentiality (don't contact end client)
   - Hold harmless

6. **Contact Information:**
   - DEE DAVIS INC only
   - info@deedavis.biz
   - 248-376-4550

---

### **COMPONENT 4: DOCUMENT GENERATOR**

**Function:** Output professional RFQ documents

**Output Formats:**
- PDF (primary - for email)
- HTML (for web viewing)
- Word (for editing if needed)
- JSON (for system integration)

**Branding:**
- DEE DAVIS INC header/logo
- Professional formatting
- Consistent styling
- Page numbers
- Watermark (optional)

---

## 💻 TECHNICAL IMPLEMENTATION

### **TECH STACK:**

**Backend:**
- Python 3.x
- Flask/FastAPI for API
- PyPDF2 or pdfplumber for PDF parsing
- python-docx for Word docs
- ReportLab or WeasyPrint for PDF generation

**Frontend:**
- React component in NEXUS dashboard
- Upload RFQ → Preview → Generate → Download

**Database:**
- Store generated RFQs
- Track RFQ numbers (auto-increment)
- Link supplier RFQ to buyer RFQ

**AI/NLP (Optional Enhancement):**
- GPT-4 for intelligent parsing
- Auto-extract specifications
- Auto-detect buyer information to remove

---

## 📱 USER INTERFACE (NEXUS DASHBOARD)

### **SCREEN 1: UPLOAD BUYER RFQ**

```
┌─────────────────────────────────────────┐
│ 🆕 Generate Supplier RFQ                │
├─────────────────────────────────────────┤
│                                         │
│ Upload Buyer RFQ:                       │
│ [📄 Choose File] or [Drag & Drop]      │
│                                         │
│ Buyer Information (Auto-detected):      │
│ Buyer: City of Auburn Hills            │
│ Location: Auburn Hills, MI              │
│ Solicitation #: RFQ-01-30-2026-001      │
│                                         │
│ [Next: Review Specifications] →         │
└─────────────────────────────────────────┘
```

---

### **SCREEN 2: REVIEW & EDIT SPECIFICATIONS**

```
┌─────────────────────────────────────────┐
│ 📝 Review Specifications                │
├─────────────────────────────────────────┤
│                                         │
│ Extracted Specifications:               │
│ ┌─────────────────────────────────────┐ │
│ │ ✅ Scope: Pressure washing services │ │
│ │ ✅ Equipment: Hot water required    │ │
│ │ ✅ Locations: 20 park sites         │ │
│ │ ✅ Response: 1 week turnaround      │ │
│ │ ✅ Insurance: $1M liability + more  │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ Generic Client Description:             │
│ [Municipal client in Oakland County, MI]│
│                                         │
│ ← [Back]  [Next: Generate RFQ] →       │
└─────────────────────────────────────────┘
```

---

### **SCREEN 3: PREVIEW SUPPLIER RFQ**

```
┌─────────────────────────────────────────┐
│ 👁️ Preview Supplier RFQ                 │
├─────────────────────────────────────────┤
│                                         │
│ DDI RFQ Number: DDI-2026-PW-001         │
│ Client: Municipal client (Oakland Cty)  │
│ Due Date: Feb 10, 2026                  │
│                                         │
│ ⚠️  Buyer Protection Check:             │
│ ✅ No buyer name mentioned              │
│ ✅ No specific city mentioned           │
│ ✅ No buyer solicitation #              │
│ ✅ Generic location used                │
│                                         │
│ [📄 Preview PDF] [📧 Preview Email]     │
│                                         │
│ ← [Back]  [Generate & Download] →      │
└─────────────────────────────────────────┘
```

---

### **SCREEN 4: DOWNLOAD & SEND**

```
┌─────────────────────────────────────────┐
│ ✅ Supplier RFQ Generated!               │
├─────────────────────────────────────────┤
│                                         │
│ RFQ Number: DDI-2026-PW-001             │
│ Status: Ready to send                   │
│                                         │
│ [📥 Download PDF]                       │
│ [📥 Download Word]                      │
│ [📧 Email to Suppliers]                 │
│                                         │
│ Quick Send:                             │
│ [Add Supplier Emails]                   │
│ [                                    ]  │
│ [                                    ]  │
│                                         │
│ [Send RFQ to All] →                    │
└─────────────────────────────────────────┘
```

---

## 🔐 BUYER PROTECTION CHECKLIST

**Before generating supplier RFQ, system MUST verify:**

- [ ] ❌ Buyer name removed
- [ ] ❌ Buyer agency name removed
- [ ] ❌ Buyer contact names removed
- [ ] ❌ Buyer email addresses removed
- [ ] ❌ Buyer phone numbers removed
- [ ] ❌ Buyer solicitation number removed
- [ ] ❌ Specific city name removed (use county)
- [ ] ❌ Specific addresses removed
- [ ] ❌ Buyer website/links removed
- [ ] ✅ Generic client description added
- [ ] ✅ DEE DAVIS INC contact info only
- [ ] ✅ Technical specs intact
- [ ] ✅ DDI RFQ number assigned

**IF ANY BUYER INFO DETECTED → SYSTEM ALERT! 🚨**

---

## 📊 DATABASE SCHEMA

### **Table: buyer_rfqs**
```sql
CREATE TABLE buyer_rfqs (
    id INT PRIMARY KEY AUTO_INCREMENT,
    buyer_name VARCHAR(255),
    buyer_agency VARCHAR(255),
    solicitation_number VARCHAR(100),
    location_city VARCHAR(100),
    location_county VARCHAR(100),
    location_state VARCHAR(50),
    due_date DATE,
    upload_date TIMESTAMP,
    original_file_path VARCHAR(500),
    status ENUM('uploaded', 'processing', 'completed')
);
```

### **Table: supplier_rfqs**
```sql
CREATE TABLE supplier_rfqs (
    id INT PRIMARY KEY AUTO_INCREMENT,
    ddi_rfq_number VARCHAR(50) UNIQUE,
    buyer_rfq_id INT,
    generic_client_description TEXT,
    scope_of_work TEXT,
    technical_specs JSON,
    issue_date DATE,
    supplier_due_date DATE,
    generated_pdf_path VARCHAR(500),
    generated_date TIMESTAMP,
    sent_to_suppliers BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (buyer_rfq_id) REFERENCES buyer_rfqs(id)
);
```

### **Table: supplier_quotes_received**
```sql
CREATE TABLE supplier_quotes_received (
    id INT PRIMARY KEY AUTO_INCREMENT,
    supplier_rfq_id INT,
    supplier_name VARCHAR(255),
    supplier_email VARCHAR(255),
    quote_amount DECIMAL(10,2),
    quote_date DATE,
    selected BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (supplier_rfq_id) REFERENCES supplier_rfqs(id)
);
```

---

## 🚀 IMPLEMENTATION PHASES

### **PHASE 1: MVP (2-3 weeks)**
- Manual upload of buyer RFQ (PDF)
- Manual entry of buyer info to remove
- Manual entry of specifications
- Auto-generate PDF with DEE DAVIS INC branding
- Download for email

### **PHASE 2: AI-Enhanced (4-6 weeks)**
- Auto-parse PDF to extract buyer info
- AI detection of buyer identifying information
- Auto-generate generic client descriptions
- One-click generation
- Email integration (send directly from NEXUS)

### **PHASE 3: Advanced (8-12 weeks)**
- Template library for different RFQ types
- Smart recommendations for markup %
- Supplier database integration
- Auto-send to qualified suppliers
- Quote comparison dashboard
- Win/loss tracking

---

## 📧 EMAIL INTEGRATION

### **Email Template for Suppliers:**

```
Subject: RFQ - [Project Type] for Michigan Municipal Client (DDI-2026-XXX-###)

Hi [Supplier Name],

DEE DAVIS INC is seeking quotes for a [project type] project for a 
municipal client in [County], Michigan.

Attached is our formal Request for Quotation (DDI-2026-XXX-###) with 
complete specifications and requirements.

Key Details:
- Project Type: [Type]
- Location: [County], [State]
- Service Start: [Date]
- Quote Due: [Date] at 5:00 PM EST

Please review the attached RFQ and submit your quote to info@deedavis.biz 
by the deadline.

If you have any questions, please email us or call 248-376-4550.

Thank you!

Dee Davis
DEE DAVIS INC
248-376-4550
info@deedavis.biz
```

---

## ✅ SUCCESS CRITERIA

**System is successful if:**

1. ✅ **100% buyer protection** - No buyer info leaked to suppliers
2. ✅ **Professional output** - Supplier RFQs look polished and complete
3. ✅ **Time savings** - Generate in 5-10 min vs. 1-2 hours manually
4. ✅ **Easy to use** - Non-technical user can operate
5. ✅ **Consistent branding** - All supplier RFQs follow DEE DAVIS INC template
6. ✅ **Audit trail** - Track what was removed/changed
7. ✅ **No errors** - Specifications remain accurate

---

## 🎯 BUSINESS IMPACT

**Benefits:**

💰 **Protect Margins:**
- Suppliers can't bypass you if they don't know the buyer
- Preserve your role as prime contractor
- Maintain markup on subcontractor work

⏱️ **Save Time:**
- Auto-generate in minutes instead of hours
- Reuse for similar projects
- Consistent process every time

📈 **Scale Business:**
- Handle more RFQs efficiently
- Professional presentation to suppliers
- Systematic approach to subcontracting

🛡️ **Risk Management:**
- Reduce human error in removing buyer info
- Built-in compliance checks
- Documented audit trail

---

## 📋 NEXT STEPS TO BUILD

**IMMEDIATE (This Week):**
1. Create RFQ template (DONE! ✅ - see Auburn Hills example)
2. Define data extraction rules
3. Design NEXUS UI screens

**SHORT TERM (Next 2-4 Weeks):**
1. Build PDF upload functionality
2. Build form for manual data entry
3. Build PDF generator with DEE DAVIS INC template
4. Test with Auburn Hills RFQ

**LONG TERM (Next 2-3 Months):**
1. Add AI/NLP for auto-parsing
2. Add email integration
3. Add supplier database
4. Add quote tracking dashboard

---

**START WITH AUBURN HILLS - USE THE RFQ I JUST CREATED AS THE TEMPLATE!** 🚀

---

*System Design: January 30, 2026*  
*Critical Rule: NEVER reveal buyer to suppliers*  
*Purpose: Protect business, save time, scale operations*
