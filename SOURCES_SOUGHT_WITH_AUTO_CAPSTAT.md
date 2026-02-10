# 🎯 SOURCES SOUGHT RESPONSE SYSTEM
## **With Automated Opportunity-Specific Capability Statements**

**Date:** February 3, 2026  
**Status:** ACTIVE - Integrated with NEXUS

---

## 🚀 THE COMPLETE WORKFLOW (30 Minutes Total)

### **STEP 1: Find Sources Sought Opportunity (5 min)**
1. Go to SAM.gov
2. Search for WOSB/EDWOSB sources sought
3. Find active opportunity
4. Save to NEXUS OFFICER OUTREACH TRACKING table

### **STEP 2: Auto-Generate Opportunity-Specific Capability Statement (2 min)**
```bash
cd "/Users/deedavis/NEXUS BACKEND"
python3 auto_generate_opportunity_capstat.py <outreach_record_id>
```

**What it does:**
- ✅ Pulls opportunity details from Airtable
- ✅ Determines product/service category
- ✅ Selects appropriate NAICS codes
- ✅ Customizes competencies for this specific opportunity
- ✅ Chooses colors based on agency/set-aside
- ✅ Generates HTML + PDF capability statement
- ✅ Updates NEXUS record (CAPSTATGENERATED = True)

### **STEP 3: Customize Response Email (10 min)**
Use the template below, attach the auto-generated PDF

### **STEP 4: Submit Response (3 min)**
Send email with capability statement attachment

### **STEP 5: Track in NEXUS (2 min)**
Mark as SENT, set follow-up date

---

## 📧 SOURCES SOUGHT RESPONSE EMAIL TEMPLATE

**Subject:** Sources Sought Response - [Solicitation Number] - EDWOSB Vendor

**To:** [Contracting Officer Email from SAM.gov]

**Body:**

```
[Contracting Officer Name]
[Agency Name]
[Address from SAM.gov]

RE: Sources Sought Notice - [Solicitation Number]
     [Product/Service Name]

Dear [Contracting Officer Name]:

Dee Davis Inc. respectfully submits this capability statement in response to your sources sought notice for [Product/Service Name] (Solicitation Number: [NUMBER]).

COMPANY OVERVIEW:
Dee Davis Inc. is a certified EDWOSB (Economically Disadvantaged Woman-Owned Small Business) specializing in [product category] procurement and distribution. We are registered in SAM.gov and ready to support federal agencies.

CERTIFICATIONS & CREDENTIALS:
• CAGE Code: 8UMX3
• UEI: HJB4KNYJVGZ1
• DUNS: 002636755
• SAM.gov Registered (Active Status)
• SBA EDWOSB Certified
• Michigan-based, Nationwide Capability

CAPABILITY TO PERFORM:
Dee Davis Inc. has established relationships with [manufacturers/suppliers] and can provide:
• Competitive pricing
• Prompt delivery timelines
• Quality products meeting federal specifications
• Excellent past performance record
• Full compliance with FAR regulations

INTEREST CONFIRMATION:
Dee Davis Inc. confirms strong interest in bidding on the forthcoming solicitation. We request to be added to your vendor notification list for this procurement.

Please find attached our capability statement tailored to this opportunity.

Thank you for considering Dee Davis Inc. as a potential contractor for this requirement.

Respectfully submitted,

Dee Davis
President
Dee Davis Inc.
755 W Big Beaver Rd, Suite 2020
Troy, MI 48084-4925
Phone: 248-376-4550
Email: info@deedavis.biz

CAGE Code: 8UMX3 | EDWOSB Certified | SAM.gov Registered
```

**Attachments:**
- [X] Opportunity-specific capability statement PDF (auto-generated)
- [X] W-9 Form (from COMPANY FORMS folder)

---

## 🤖 HOW THE AUTO-GENERATION WORKS:

### **Smart Category Detection:**

The system automatically detects what type of opportunity it is and customizes everything:

**Cable/Wire Products:**
- NAICS: 5995 - Cable and Wire Products
- Competencies: Cable assembly sourcing, electronic components
- Highlights: Major cable manufacturers partnerships

**Industrial Supplies:**
- NAICS: 423840 - Industrial Supplies
- Competencies: Industrial supply procurement, multi-category fulfillment
- Highlights: Grainger, Fastenal, MSC partnerships

**Medical Supplies:**
- NAICS: 423450 - Medical Equipment
- Competencies: Medical equipment, healthcare compliance
- Highlights: FDA/CDC standards compliance

**Vehicles:**
- NAICS: 441110 - Automobile Dealers
- Competencies: Vehicle procurement, fleet services
- Highlights: Wholesale dealer partnerships

**Cleaning Services:**
- NAICS: 561720 - Janitorial Services
- Competencies: Prime contracting, subcontractor management
- Highlights: EDWOSB prime contractor capability

**And more...**

### **Smart Color Selection:**

**WOSB/EDWOSB Set-Asides:**
- Amber accent (#d97706) - highlights your EDWOSB certification

**VA/Veterans Affairs:**
- Blue accent (#0066cc) - professional healthcare theme

**Other Federal:**
- Orange accent (#f97316) - professional federal theme

---

## 📋 COMPLETE EXAMPLE WORKFLOW:

### **Scenario: You found a WOSB sources sought for cable assemblies**

**1. Add to NEXUS (via Airtable or API):**
```python
outreach_table.create({
    'OPPORTUNITY TITLE': 'Cable Assembly',
    'SOLICITATION NUMBER': 'SPRRA2-26-R-0008_0002',
    'AGENCY': 'Defense Logistics Agency',
    'STATUS': 'DRAFT',
    'PRIORITY': 'HIGH',
    'TAGS': ['WOSB', 'Federal'],
    'DEADLINE': '2026-02-16'
})
```

**2. Auto-generate capability statement:**
```bash
python3 auto_generate_opportunity_capstat.py recKeusVGeCAeLor8
```

**Output:**
```
✅ Config saved: capstat_config_Cable_Assembly_20260203_143022.json
✅ HTML generated: capstat_Cable_Assembly_20260203_143022.html
✅ PDF generated: capstat_Cable_Assembly_20260203_143022_enhanced.pdf
✅ Updated outreach record: CAPSTATGENERATED = True

📄 Files Generated:
   HTML: capstat_Cable_Assembly_20260203_143022.html
   PDF: capstat_Cable_Assembly_20260203_143022_enhanced.pdf

Customizations Applied:
   ✓ NAICS: 5995 - Cable and Wire Products
   ✓ Competencies: Cable assembly sourcing
   ✓ Colors: WOSB amber accent
   ✓ Highlights: Major cable manufacturer partnerships
```

**3. Customize email (5 min)**

**4. Attach PDF and send**

**5. Update status to SENT**

**TOTAL TIME: 15-20 minutes**

---

## 🎯 MANUAL MODE (No Airtable Record Yet):

```bash
python3 auto_generate_opportunity_capstat.py --manual
```

**Prompts:**
```
Opportunity Title: Cable Assembly
Solicitation Number (optional): SPRRA2-26-R-0008_0002
Agency Name (optional): Defense Logistics Agency
Set-Aside Type (WOSB/EDWOSB/etc, optional): WOSB
```

**Generates the same customized capability statement!**

---

## 📊 TRACKING IN NEXUS:

**OFFICER OUTREACH TRACKING Table:**

| Field | Value | Auto-Updated? |
|-------|-------|---------------|
| OPPORTUNITY TITLE | Cable Assembly | ✓ |
| SOLICITATION NUMBER | SPRRA2-26-R-0008_0002 | ✓ |
| AGENCY | Defense Logistics Agency | ✓ |
| STATUS | DRAFT → SENT | Manual |
| CAPSTATGENERATED | True | ✓ Auto |
| CAPSTAT GENERATED DATE | 2026-02-03T14:30:22 | ✓ Auto |
| DATE SENT | 2026-02-03 | Manual |
| FOLLOW-UP DATE | 2026-02-10 | Manual |

---

## 💰 WHY THIS IS BRILLIANT:

### **Before (Generic Capability Statement):**
- ❌ Same statement for everyone
- ❌ No customization to opportunity
- ❌ Generic NAICS codes
- ❌ Doesn't highlight relevant experience
- ❌ Looks mass-produced
- **Result:** Gets ignored

### **After (Auto-Generated Opportunity-Specific):**
- ✅ Customized to exact opportunity
- ✅ Relevant NAICS codes for THIS opportunity
- ✅ Competencies match requirement
- ✅ Colors match agency/set-aside
- ✅ Highlights relevant partnerships
- ✅ Looks professionally tailored
- **Result:** Stands out, gets attention!

---

## 🔄 INTEGRATION WITH NEXUS FRONTEND:

**Coming soon in DocumentGenerator:**

```typescript
// Click "Generate Capability Statement" button
// Select opportunity from dropdown
// System auto-generates customized PDF
// One-click attach to outreach email
```

**For now, use command line (works perfectly!):**
```bash
python3 auto_generate_opportunity_capstat.py <record_id>
```

---

## 📁 FILE ORGANIZATION:

**Generated files go to current directory:**
```
/Users/deedavis/NEXUS BACKEND/
├── capstat_Cable_Assembly_20260203_143022.html
├── capstat_Cable_Assembly_20260203_143022_enhanced.pdf
├── capstat_config_Cable_Assembly_20260203_143022.json
├── capstat_Shipping_Storage_20260203_150000.html
├── capstat_Shipping_Storage_20260203_150000_enhanced.pdf
└── capstat_config_Shipping_Storage_20260203_150000.json
```

**Move to organized folder when done:**
```bash
mkdir -p "generated_capability_statements"
mv capstat_*.html generated_capability_statements/
mv capstat_*.pdf generated_capability_statements/
mv capstat_config_*.json generated_capability_statements/
```

---

## ✅ COMPLETE ACTION CHECKLIST:

**For Each Sources Sought Response:**

- [ ] Find sources sought opportunity on SAM.gov
- [ ] Add to OFFICER OUTREACH TRACKING in Airtable
- [ ] Get record ID from Airtable
- [ ] Run: `python3 auto_generate_opportunity_capstat.py <record_id>`
- [ ] Review generated PDF
- [ ] Customize email template
- [ ] Attach PDF + W-9
- [ ] Send to contracting officer
- [ ] Update status to SENT in Airtable
- [ ] Set follow-up date (7-14 days)
- [ ] Move files to generated_capability_statements folder

**Time: 20-30 minutes per response**

---

## 🚀 SCALE THIS:

**Respond to 5 sources sought per week = 20 vendor lists per month!**

**Month 1:**
- 20 vendor lists
- 20 customized capability statements
- 20 contracting officer relationships

**Month 3:**
- 60 vendor lists
- First RFP invitations
- 2-3 federal contract bids

**Month 6:**
- 120 vendor lists
- Regular RFP notifications
- First federal contract WIN! 🎉

---

## 🎯 EXPECTED RESULTS:

**Short-term (30 days):**
- 10-20 sources sought responses
- 10-20 vendor list additions
- 10-20 customized capability statements
- Relationships with 10-20 contracting officers

**Mid-term (90 days):**
- 30-60 vendor list additions
- 5-10 RFP invitations
- 3-5 federal bids submitted
- First federal contract award ($50K-150K)

**Long-term (180 days):**
- 60-120 vendor list additions
- Regular RFP pipeline
- Multiple federal contracts
- Strong federal track record
- Past performance for larger contracts

---

## 💡 PRO TIPS:

**1. Respond FAST:**
- Same day or within 24 hours of posting
- Shows urgency and capability

**2. Customize the email:**
- Don't just attach PDF - explain WHY you're a good fit
- Reference specific requirements

**3. Follow up:**
- If no RFP released in 2 weeks, send follow-up
- "Checking in on status of solicitation..."

**4. Track everything:**
- NEXUS keeps all your outreach organized
- Easy to see what's pending vs sent vs responded

**5. Build relationships:**
- Contracting officers remember proactive vendors
- You're getting on their radar BEFORE competition starts

---

## 🔧 TROUBLESHOOTING:

**Q: Script says "command not found"?**
```bash
# Make executable
chmod +x auto_generate_opportunity_capstat.py
# Run with python3
python3 auto_generate_opportunity_capstat.py <record_id>
```

**Q: Can't find record ID?**
- Open Airtable
- Click on the record
- URL will show: ...rec123ABC...
- That's your record ID

**Q: PDF not generating?**
```bash
# Install dependencies
pip install weasyprint
# OR
brew install wkhtmltopdf
```

**Q: Want to regenerate with different customizations?**
```bash
# Edit the generated config JSON file
nano capstat_config_*.json
# Then regenerate HTML + PDF
python3 generate_html_with_highlights.py capstat_config_*.json
python3 generate_enhanced_pdf.py capstat_config_*.json
```

---

## 📞 QUICK REFERENCE:

**Generate from Airtable record:**
```bash
python3 auto_generate_opportunity_capstat.py recABC123
```

**Generate manually:**
```bash
python3 auto_generate_opportunity_capstat.py --manual
```

**Files generated:**
- Config: `capstat_config_[Title]_[Timestamp].json`
- HTML: `capstat_[Title]_[Timestamp].html`
- PDF: `capstat_[Title]_[Timestamp]_enhanced.pdf`

---

**THIS IS THE SMART WAY TO WIN FEDERAL CONTRACTS!** 🎯

You're not just responding to sources sought - you're building a customized, professional brand that shows you understand THEIR specific needs! 💰
