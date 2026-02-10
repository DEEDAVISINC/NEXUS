# NEXUS RFP GENERATOR - USER GUIDE

**Automated Supplier RFP Creation with Buyer Protection**

---

## 🎯 WHAT IT DOES

The RFP Generator automatically creates professional, DDI-branded supplier RFPs with:
- ✅ Professional PDF format
- ✅ DEE DAVIS INC watermark on every page
- ✅ Automatic buyer identity protection (no client names in supplier RFP)
- ✅ Complete RFP template with all sections
- ✅ Tracking in Airtable database

---

## 🚀 QUICK START

### **Step 1: Start the API**

```bash
chmod +x START_RFP_GENERATOR.sh
./START_RFP_GENERATOR.sh
```

The API will start on http://localhost:5002

### **Step 2: Test It**

Open a new terminal and run:

```bash
chmod +x test_rfp_generator.sh
./test_rfp_generator.sh
```

This will generate a test RFP for Auburn Hills Pressure Washing.

### **Step 3: Check Output**

Look in the `generated_rfps/` folder for your PDF:
```
generated_rfps/RFP_DDI-2026-PW-001.pdf
```

Open it and verify:
- ✅ Professional formatting
- ✅ DEE DAVIS INC watermark
- ✅ No mention of "City of Auburn Hills" (buyer protected!)
- ✅ Only says "Oakland County, Michigan"

---

## 📝 HOW TO USE

### **METHOD 1: Test Endpoint (Quickest)**

Generate Auburn Hills RFP:

```bash
curl -X POST http://localhost:5002/api/rfp/test
```

### **METHOD 2: Custom RFP (Most Common)**

Send your own data:

```bash
curl -X POST http://localhost:5002/api/rfp/generate \
  -H "Content-Type: application/json" \
  -d '{
    "project_name": "Industrial Padlocks - Texas Utility",
    "category": "Supplies",
    "sanitized_location": "San Antonio, Texas area",
    "scope_of_work": "Supply of various industrial padlocks...",
    "contract_value_min": 350000,
    "contract_value_max": 490000,
    "quote_due_date": "2026-02-06T17:00:00",
    "contract_period": "3 years (2026-2029)",
    "service_locations_count": 0,
    "insurance_requirements": "GL $1M, Workers Comp",
    "buyer_name": "CPS Energy",
    "buyer_rfp_number": "7000205019"
  }'
```

### **METHOD 3: From Frontend (Future)**

Once the frontend is built:
1. Go to NEXUS dashboard
2. Click "Create RFP"
3. Fill out form
4. Click "Generate PDF"
5. Download and send to suppliers

---

## 📊 API ENDPOINTS

### **POST `/api/rfp/generate`**

Generate a new RFP from JSON data.

**Request Body:**
```json
{
  "project_name": "Municipal Parks Pressure Washing Services",
  "category": "Pressure Washing",
  "sanitized_location": "Oakland County, Michigan",
  "scope_of_work": "Hot water pressure washing...",
  "contract_value_min": 8000,
  "contract_value_max": 15000,
  "quote_due_date": "2026-02-10T17:00:00",
  "contract_period": "March 2026 - December 2026",
  "service_locations_count": 20,
  "insurance_requirements": "GL $1M...",
  "buyer_name": "City of Auburn Hills",
  "buyer_rfp_number": "RFQ-01-30-2026-001"
}
```

**Response:**
```json
{
  "success": true,
  "rfp_number": "DDI-2026-PW-001",
  "pdf_path": "generated_rfps/RFP_DDI-2026-PW-001.pdf",
  "record_id": "recXXXXXXXX",
  "message": "RFP DDI-2026-PW-001 generated successfully"
}
```

---

### **GET `/api/rfp/download/<rfp_number>`**

Download a generated RFP PDF.

**Example:**
```bash
curl -O http://localhost:5002/api/rfp/download/DDI-2026-PW-001
```

---

### **GET `/api/rfp/list`**

Get all generated RFPs from database.

**Response:**
```json
{
  "success": true,
  "rfps": [
    {
      "id": "recXXXX",
      "ddi_rfp_number": "DDI-2026-PW-001",
      "project_name": "Municipal Parks Pressure Washing",
      "status": "draft",
      ...
    }
  ],
  "count": 3
}
```

---

### **POST `/api/rfp/test`**

Generate test RFP (Auburn Hills Pressure Washing).

**Example:**
```bash
curl -X POST http://localhost:5002/api/rfp/test
```

---

### **GET `/api/health`**

Health check endpoint.

**Response:**
```json
{
  "status": "ok",
  "service": "RFP Generator API",
  "version": "1.0.0",
  "airtable_connected": true
}
```

---

## 🔒 BUYER PROTECTION

**The system automatically protects buyer identity:**

### **Confidential (NOT in supplier RFP):**
- ❌ Buyer name (City of Auburn Hills)
- ❌ Buyer RFP number (RFQ-01-30-2026-001)
- ❌ Specific city names
- ❌ Exact addresses
- ❌ Procurement officer names

### **Public (IN supplier RFP):**
- ✅ DDI RFP number (DDI-2026-PW-001)
- ✅ Generic location (Oakland County, Michigan)
- ✅ General project description
- ✅ Specifications
- ✅ Insurance requirements
- ✅ Quote due date (to DEE DAVIS INC)

### **Strong Confidentiality Clause:**

Every RFP includes:
> "The subcontractor agrees to maintain strict confidentiality regarding end client identity and information. The subcontractor shall NOT contact the end client directly under any circumstances."

**Violation = immediate termination + legal action!**

---

## 📋 RFP NUMBERING SYSTEM

**Format:** `DDI-YYYY-CC-###`

- **DDI** = DEE DAVIS INC
- **YYYY** = Year (2026)
- **CC** = Category code
- **###** = Sequential number (001, 002, 003...)

**Category Codes:**
- **PW** = Pressure Washing
- **LS** = Landscaping
- **JAN** = Janitorial
- **CON** = Construction
- **SUP** = Supplies
- **HVAC** = HVAC
- **PLU** = Plumbing
- **ELE** = Electrical
- **MAINT** = Maintenance
- **GEN** = General Services

**Examples:**
- DDI-2026-PW-001 (First pressure washing RFP of 2026)
- DDI-2026-SUP-005 (Fifth supplies RFP of 2026)
- DDI-2026-LS-002 (Second landscaping RFP of 2026)

---

## 📄 PDF OUTPUT

**Each RFP includes:**

### **Cover Page:**
- DEE DAVIS INC branding
- RFP number
- Project name
- Key dates
- Contact information
- CAGE code, DUNS number
- Confidentiality notice

### **Section 1: Introduction**
- About DEE DAVIS INC
- Certifications (EDWOSB/WOSB)
- Purpose of RFP
- Project overview

### **Section 2: Scope of Work**
- General requirements
- Detailed specifications
- Service locations (count only, not addresses)
- Performance standards

### **Section 3: Submission Requirements**
- Proposal format
- Required documents
- Submission instructions
- Email: proposals@deedavis.biz
- Due date

### **Section 4: Terms & Conditions**
- Payment terms (Net 30)
- Insurance requirements
- Confidentiality clause (CRITICAL!)
- Contract terms
- Indemnification

### **Watermark:**
- "DEE DAVIS INC"
- "CERTIFIED EDWOSB"
- "PRIME CONTRACTOR"
- Diagonal, light gray, on every page

### **Footer:**
- Contact information
- CAGE code, DUNS number
- "PROPRIETARY & CONFIDENTIAL"

---

## 🗄️ DATABASE TRACKING

**Airtable Table:** `SUPPLIER_RFPS`

**Fields saved:**
- `ddi_rfp_number` (DDI-2026-PW-001)
- `project_name` (Municipal Parks Pressure Washing)
- `category` (Pressure Washing)
- `sanitized_location` (Oakland County, MI)
- `scope_of_work` (full text)
- `contract_value_min` ($8,000)
- `contract_value_max` ($15,000)
- `quote_due_date` (2026-02-10)
- `contract_period` (March-December 2026)
- `status` (draft, sent, quotes_received, closed)
- `pdf_generated_path` (file location)
- `num_vendors_contacted` (how many sent to)
- `num_quotes_received` (how many quotes)

---

## 🎯 TYPICAL WORKFLOW

### **For Auburn Hills Pressure Washing:**

**Step 1: You receive buyer RFP**
```
From: City of Auburn Hills
RFP: RFQ-01-30-2026-001
Due: February 13, 2026
```

**Step 2: Generate supplier RFP**
```bash
curl -X POST http://localhost:5002/api/rfp/test
```

**Step 3: System creates:**
```
DDI-2026-PW-001 (your RFP number)
generated_rfps/RFP_DDI-2026-PW-001.pdf
```

**Step 4: Email to 5 pressure washing subs:**
```
Subject: RFP - Pressure Washing Services (Oakland County)

Attached: RFP_DDI-2026-PW-001.pdf
Quotes due to: proposals@deedavis.biz
Due: February 10, 2026 (3 days before your deadline!)
```

**Step 5: Track quotes received:**
- Clean Slate Power Washing: $7,500
- Detroit Mobile Wash: $8,200
- ProClean Services: $9,000

**Step 6: Select best sub:**
- Clean Slate: $7,500
- Your markup (18%): $1,350
- Your bid to Auburn Hills: $8,850

**Step 7: Submit to Auburn Hills by Feb 13**

---

## 🛠️ TROUBLESHOOTING

### **API won't start**

**Error:** `ModuleNotFoundError: No module named 'reportlab'`

**Fix:**
```bash
pip install reportlab PyPDF2 flask flask-cors pyairtable
```

---

### **Watermark not appearing**

**Issue:** PyPDF2 version conflict

**Fix:**
```bash
pip install --upgrade PyPDF2
```

If still issues, the system will generate PDF without watermark (still works).

---

### **Airtable errors**

**Error:** `Missing AIRTABLE_API_KEY`

**Fix:** Check your `.env` file has:
```
AIRTABLE_API_KEY=patXXXXXXXXXXXX
AIRTABLE_BASE_ID=appXXXXXXXXXXXX
```

**Note:** RFP generation works WITHOUT Airtable (just won't save to database).

---

### **PDF not generated**

**Check:**
1. `generated_rfps/` folder exists?
2. Do you have write permissions?
3. Check API logs for errors

**Create folder:**
```bash
mkdir -p generated_rfps
chmod 755 generated_rfps
```

---

## 📈 NEXT STEPS

### **This Week: Manual Process**
1. ✅ Use test endpoint to generate Auburn Hills RFP
2. ✅ Email PDF to 3-5 pressure washing subs
3. ✅ Track quotes in spreadsheet
4. ✅ Select winner and submit bid

### **Next Week: Basic Frontend**
1. Create simple form in NEXUS
2. Form calls `/api/rfp/generate` endpoint
3. Download generated PDF
4. Send to suppliers

### **2 Weeks: Full Integration**
1. Upload buyer RFP (PDF or text)
2. AI extracts key information
3. You review and sanitize
4. Generate professional PDF
5. Track in dashboard

### **1 Month: Vendor Portal**
1. Publish RFPs to deedavis.biz/vendors
2. Vendors can download
3. Vendors submit quotes online
4. Auto-notify matching vendors

---

## 🎉 SUCCESS CRITERIA

**You'll know it's working when:**

1. ✅ You run the test command
2. ✅ PDF appears in `generated_rfps/` folder
3. ✅ PDF has DDI watermark on every page
4. ✅ PDF says "Oakland County" NOT "City of Auburn Hills"
5. ✅ PDF has strong confidentiality clause
6. ✅ You can email it to suppliers immediately

**The goal:**
- Generate professional supplier RFPs in **30 seconds**
- Protect buyer identity **automatically**
- Track all RFPs and quotes
- Build vendor network

---

## 📞 QUESTIONS?

If the API isn't working:
1. Check logs in terminal where API is running
2. Test health endpoint: `curl http://localhost:5002/api/health`
3. Verify Python packages installed
4. Check `.env` file for API keys

**The RFP Generator is your secret weapon for becoming a professional prime contractor!** 🏆

---

*Created: January 30, 2026*  
*Version: 1.0.0*  
*System: NEXUS RFP Generator API*
