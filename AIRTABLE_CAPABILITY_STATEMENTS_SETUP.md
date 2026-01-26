# AIRTABLE CAPABILITY STATEMENTS TABLE SETUP

## Table Name: `CapabilityStatements`

## 📊 Fields Configuration

### 1. RecordID (Formula)
- **Type:** Formula
- **Formula:** `RECORD_ID()`
- **Description:** Auto-generated unique record ID

### 2. OpportunityID (Link to Opportunities)
- **Type:** Link to another record
- **Linked Table:** Opportunities
- **Allow linking to multiple records:** No
- **Description:** Links to the opportunity this capability statement was generated for

### 3. ClientName (Single line text)
- **Type:** Single line text
- **Description:** Name of the client/agency (e.g., "CPS Energy", "VA Medical")

### 4. RFQNumber (Single line text)
- **Type:** Single line text
- **Description:** RFQ/Solicitation number (e.g., "7000205103", "VA-26-1234")

### 5. GeneratedDate (Date)
- **Type:** Date
- **Include time:** Yes
- **Format:** Local (friendly)
- **Description:** When the capability statement was generated

### 6. HTMLPath (Long text)
- **Type:** Long text
- **Description:** File path to the generated HTML file

### 7. PDFPath (Long text)
- **Type:** Long text
- **Description:** File path to the generated PDF file

### 8. ConfigJSON (Long text)
- **Type:** Long text
- **Description:** The full JSON configuration used to generate this statement

### 9. Status (Single select)
- **Type:** Single select
- **Options:**
  - Generated (Green)
  - Submitted (Blue)
  - Accepted (Purple)
  - Rejected (Red)
  - Archived (Gray)
- **Description:** Status of the capability statement

### 10. Template (Single select)
- **Type:** Single select
- **Options:**
  - default
  - va_medical
  - construction
  - custom
- **Description:** Template type used

### 11. SubmittedDate (Date)
- **Type:** Date
- **Include time:** Yes
- **Description:** When the capability statement was submitted to client

### 12. SubmittedBy (Single line text)
- **Type:** Single line text
- **Description:** Who submitted it (e.g., "Dee Davis", "System Auto")

### 13. Notes (Long text)
- **Type:** Long text
- **Description:** Any notes about this capability statement

### 14. OpportunityName (Lookup)
- **Type:** Lookup
- **Lookup from:** OpportunityID → Title
- **Description:** Name of the opportunity (pulled from Opportunities table)

### 15. OpportunityStatus (Lookup)
- **Type:** Lookup
- **Lookup from:** OpportunityID → Status
- **Description:** Status of the opportunity (pulled from Opportunities table)

---

## 🎨 View Configurations

### 1. All Statements (Grid View - Primary)
**Visible Fields:**
- RecordID
- ClientName
- RFQNumber
- GeneratedDate
- Status
- Template

**Group by:** Status  
**Sort by:** GeneratedDate (descending)

### 2. Recent (Grid View)
**Filters:** 
- GeneratedDate is within the last 30 days

**Sort by:** GeneratedDate (descending)

### 3. By Client (Grid View)
**Group by:** ClientName  
**Sort by:** GeneratedDate (descending)

### 4. Submitted (Grid View)
**Filters:**
- Status is "Submitted" OR "Accepted"

**Sort by:** SubmittedDate (descending)

---

## 🤖 Automations

### 1. Auto-Generate from Opportunity
**Trigger:** When opportunity status changes to "Ready to Bid"

**Actions:**
1. Call webhook: `POST /capability-statements/generate`
2. Body: 
   ```json
   {
       "opportunity_id": "{{OpportunityID}}",
       "template": "default"
   }
   ```
3. Update opportunity with generated file paths

### 2. Email Notification on Generation
**Trigger:** When capability statement is created

**Actions:**
1. Send email to Dee Davis
2. Subject: "Capability Statement Generated - {{ClientName}}"
3. Body: "New capability statement for {{ClientName}} ({{RFQNumber}}) is ready for review."

### 3. Archive Old Statements
**Trigger:** Scheduled - Run daily at midnight

**Actions:**
1. Find records where:
   - Status is "Generated"
   - GeneratedDate is more than 90 days ago
2. Update Status to "Archived"

---

## 🔗 Integration with Other Tables

### Links to Opportunities
- **Field:** OpportunityID (Link)
- **Purpose:** Track which opportunity the statement is for
- **Benefits:** 
  - Auto-populate client name
  - Track opportunity status
  - Link to opportunity details

### CompanyInfo Integration
The Python module automatically pulls company data from CompanyInfo table:
- CompanyName
- CAGECode
- UEI (if available)
- DUNSNumber
- TaxID
- SAMStatus
- Address, City, State, ZipCode
- Phone, Email, Website
- President name

---

## 📱 Make.com Webhook Setup

### Scenario 1: Generate from Airtable Button
1. **Trigger:** Webhook (Instant)
2. **Parse JSON**
3. **HTTP Request:**
   - Method: POST
   - URL: `https://your-domain.com/capability-statements/generate`
   - Body: Raw JSON from webhook
4. **Parse Response**
5. **Airtable Update:**
   - Update CapabilityStatements record with file paths

### Scenario 2: Auto-Generate on Opportunity Update
1. **Trigger:** Airtable (Watch Records)
   - Table: Opportunities
   - Trigger Field: Status
   - Trigger Value: "Ready to Bid"
2. **HTTP Request:**
   - Generate capability statement
3. **Airtable Create:**
   - Create new CapabilityStatements record
4. **Airtable Update:**
   - Link back to Opportunities

---

## 🧪 Testing

### Test Generation
```bash
# Test with default
python3 generate_html_with_highlights.py default_config.json

# Verify output
ls default.html
open default.html

# Test PDF
python3 generate_enhanced_pdf.py default_config.json
open default_enhanced.pdf
```

### Test API
```bash
# Test generation endpoint
curl -X POST http://localhost:5000/capability-statements/generate \
  -H "Content-Type: application/json" \
  -d '{
    "client_name": "Test Client",
    "rfq_number": "TEST-123",
    "template": "default"
  }'

# Test templates endpoint
curl http://localhost:5000/capability-statements/templates

# Test list endpoint
curl http://localhost:5000/capability-statements/list
```

---

## 📈 Usage Metrics to Track

Add these fields to track usage:
- **TimesViewed** (Number) - How many times HTML was accessed
- **TimesDownloaded** (Number) - How many times PDF was downloaded
- **LastAccessed** (Date) - Last time file was viewed
- **ResultStatus** (Single select) - Won, Lost, Pending

---

## 🎯 Best Practices

1. **Generate early** - Create capability statements when opportunity is qualified
2. **Customize per client** - Tailor highlights and competencies to match RFQ
3. **Keep updated** - Regenerate if company info changes
4. **Archive old versions** - Don't delete, just archive
5. **Track results** - Note which statements led to wins

---

## 🚀 Quick Start

### First Time Setup
```bash
# 1. Ensure scripts are executable
chmod +x generate_html_with_highlights.py
chmod +x generate_enhanced_pdf.py

# 2. Create output directory
mkdir -p generated_capability_statements

# 3. Test generation
python3 generate_html_with_highlights.py default_config.json

# 4. Verify output
open default.html

# 5. Ready to automate!
```

### Create Your First Statement
```bash
# 1. Copy default config
cp default_config.json my_first_capstat.json

# 2. Edit for your opportunity
nano my_first_capstat.json
# Update: client_name, rfq_number, date

# 3. Generate
python3 generate_html_with_highlights.py my_first_capstat.json
python3 generate_enhanced_pdf.py my_first_capstat.json

# 4. Review
open my_first_capstat.html
open my_first_capstat_enhanced.pdf

# 5. Submit to client!
```

---

## 📊 Sample Data

### Sample Record 1
```json
{
    "ClientName": "CPS Energy",
    "RFQNumber": "7000205103",
    "GeneratedDate": "2026-01-23T10:30:00.000Z",
    "Status": "Submitted",
    "Template": "default",
    "SubmittedDate": "2026-01-23T14:00:00.000Z",
    "SubmittedBy": "Dee Davis"
}
```

### Sample Record 2
```json
{
    "ClientName": "Department of Veterans Affairs",
    "RFQNumber": "VA-26-1234",
    "GeneratedDate": "2026-01-22T09:15:00.000Z",
    "Status": "Generated",
    "Template": "va_medical"
}
```

---

## 🎉 You're All Set!

The capability statement generator is now fully integrated with NEXUS. Generate professional statements in seconds!
