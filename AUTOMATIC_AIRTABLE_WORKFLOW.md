# AUTOMATIC AIRTABLE WORKFLOW
**MANDATORY: ALL RFPs and supplier contacts MUST be added to Airtable automatically**

---

## 🎯 RULE: NO MANUAL TRACKING

**From now on, EVERY TIME:**
- An RFP is reviewed → Automatically add to GPSS OPPORTUNITIES
- **Buyer contacts in RFP → Automatically extract and store CONTRACTING OFFICER info**
- A supplier is identified → Automatically add to GPSS SUBCONTRACTORS  
- A quote request is sent → Automatically link in GPSS SUBCONTRACTOR QUOTES

**NO EXCEPTIONS. NO ASKING. AUTOMATIC.**

---

## 📋 WORKFLOW FOR EVERY RFP

### **Step 1: RFP Comes In**
```python
from auto_rfp_to_airtable import AirtableAutoSync

sync = AirtableAutoSync()

# Extract RFP info
rfp_data = {
    "Name": "ITB 123 - Widget Supply",
    "RFP NUMBER": "ITB 123",
    "Deadline": "2026-02-01",
    "Status": "Awaiting Quotes",
    "Agency": "City of Example",
    "Estimated Value": 100000,
    "Est Profit": 15000
}

# Get full RFP text for buyer contact extraction
rfp_full_text = """
[Full RFP document text here]
This should include contracting officer name, email, phone, submission instructions, etc.
"""

# Add to Airtable IMMEDIATELY (with buyer contact extraction)
opp_id = sync.add_opportunity(rfp_data, rfp_full_text)
# This automatically extracts and stores:
# - Contracting Officer name, email, phone
# - Submission contact
# - Questions contact
# - All other contacts found
```

### **Step 1.5: Buyer Contact Extraction (AUTOMATIC)**

**What gets extracted from the RFP:**
```
CONTRACTING OFFICER field gets:
John Smith
john.smith@example.gov
(555) 123-4567

Contacts Extracted field gets:
Submission: bids@example.gov
Questions: john.smith@example.gov
Contact: procurement@example.gov
```

**Patterns recognized:**
- "Contracting Officer: Name"
- "Contract Specialist: Name"
- "Buyer: Name"
- "POC: Name"
- "Point of Contact: Name"
- "Submit to: email"
- "Bid to: email"
- "Questions to: email"
- All email addresses found
- All phone numbers found

**Stored in Airtable:**
- `CONTRACTING OFFICER` = Primary contact name, email, phone
- `Contacts Extracted` = All submission, questions, and other contacts

**Used for:**
- ✅ Submitting bids
- ✅ Asking questions
- ✅ Following up
- ✅ Future outreach
- ✅ Officer relationship tracking

### **Step 2: Find Suppliers**
```python
# As soon as suppliers are identified
for supplier in identified_suppliers:
    supplier_data = {
        "COMPANY NAME": supplier['name'],
        "SERVICE TYPE": supplier['service'],
        "EMAIL": supplier['email'],
        "PHONE": supplier['phone'],
        "CITY": supplier['city'],
        "STATE": supplier['state'],
        "DISCOVERY METHOD": "Web search / Previous bid / etc",
        "DISCOVERY DATE": "2026-01-24",
        "NOTES": f"Identified for {rfp_data['Name']}"
    }
    
    # Add to Airtable IMMEDIATELY
    sub_id = sync.add_supplier(supplier_data)
```

### **Step 3: Send Quote Requests**
```python
# IMMEDIATELY after sending email/fax
quote_data = {
    "Status": "Pending",
    "RFQ Sent Date": "2026-01-24",
    "Quote Due Date": "2026-01-31",
    "Notes": "Emailed quote request on 1/24"
}

# Link in Airtable IMMEDIATELY
sync.link_quote(rfp_number, company_name, quote_data)
```

### **Step 4: Quote Received**
```python
# When quote comes in
quote_update = {
    "Status": "Received",
    "Quote Amount": 25000,
    "Notes": "Quote received: $25,000 for full scope"
}

# Update Airtable IMMEDIATELY
sync.link_quote(rfp_number, company_name, quote_update)
```

---

## 🔄 ONE-COMMAND PROCESSING

For complete RFP processing (all in one shot):

```python
from auto_rfp_to_airtable import AirtableAutoSync

sync = AirtableAutoSync()

# Prepare RFP data
rfp_data = {
    "Name": "ITB 4618 - Road Repair Materials",
    "RFP NUMBER": "ITB 4618",
    "Deadline": "2026-02-15",
    "Status": "Awaiting Quotes",
    "Agency": "City of Detroit"
}

# Prepare suppliers list
suppliers_list = [
    {
        "supplier": {
            "COMPANY NAME": "ABC Materials",
            "SERVICE TYPE": "Asphalt & Concrete",
            "EMAIL": "quotes@abcmaterials.com",
            "CITY": "Detroit",
            "STATE": "MI"
        },
        "quote_data": {
            "Status": "Pending",
            "RFQ Sent Date": "2026-01-24",
            "Quote Due Date": "2026-02-10",
            "Notes": "Emailed 1/24"
        }
    },
    {
        "supplier": {
            "COMPANY NAME": "XYZ Supply",
            "SERVICE TYPE": "Construction Materials",
            "EMAIL": "sales@xyzsupply.com"
        },
        "quote_data": {
            "Status": "Pending",
            "RFQ Sent Date": "2026-01-24"
        }
    }
]

# Process EVERYTHING automatically
sync.process_rfp_complete(rfp_data, suppliers_list)
```

**Result:** 
- ✅ Opportunity added to Airtable
- ✅ All suppliers added to Airtable  
- ✅ All quote links created
- ✅ Everything tracked
- ✅ No manual work

---

## 🚨 CRITICAL RULES

### **ALWAYS:**
1. ✅ Add RFP to Airtable IMMEDIATELY when you see it
2. ✅ Add supplier to Airtable IMMEDIATELY when identified
3. ✅ Create quote link IMMEDIATELY when contact is made
4. ✅ Update status IMMEDIATELY when quote received

### **NEVER:**
1. ❌ Wait to be asked to add to Airtable
2. ❌ Track in markdown files only
3. ❌ Assume user will remember to update
4. ❌ Forget to link suppliers to opportunities

---

## 📊 WHAT GETS TRACKED AUTOMATICALLY

### **Every RFP:**
- Name
- RFP NUMBER (unique identifier)
- Deadline (with time)
- Status (Awaiting Quotes, Ready to Bid, etc.)
- Agency name
- **CONTRACTING OFFICER (name, email, phone) - AUTOMATICALLY EXTRACTED**
- **Contacts Extracted (submission email, questions contact, all contacts) - AUTOMATICALLY EXTRACTED**
- Estimated value
- Est profit
- Priority level
- Suppliers contacted
- Quotes status

### **Every Supplier:**
- COMPANY NAME (unique identifier)
- SERVICE TYPE
- Location (City, State)
- Contact info (Email, Phone, Website)
- How we found them (Discovery Method)
- When we found them (Discovery Date)
- Current relationship status
- Complete notes on interactions

### **Every Quote Request:**
- Which opportunity
- Which supplier
- Current status (Pending, Received, Declined)
- When RFQ sent
- When quote is due
- Quote amount (when received)
- Complete notes

---

## 🔧 INTEGRATION WITH EXISTING SYSTEMS

### **When using nexus_backend.py:**
```python
# At the top of any RFP processing function
from auto_rfp_to_airtable import AirtableAutoSync
sync = AirtableAutoSync()

# After extracting RFP details
sync.add_opportunity(rfp_data)

# After identifying suppliers
for supplier in suppliers:
    sync.add_supplier(supplier_data)
    sync.link_quote(rfp_number, supplier_name, quote_data)
```

### **When processing manually:**
```bash
# Run the auto-sync script
python3 auto_rfp_to_airtable.py
```

---

## ✅ BENEFITS

### **For You:**
- ✅ Never lose track of an RFP
- ✅ Never forget which suppliers you contacted
- ✅ Never miss a quote deadline
- ✅ Always know current status
- ✅ Everything in one place (Airtable)
- ✅ Accessible from anywhere (phone, tablet, computer)

### **For NEXUS:**
- ✅ Backend automatically syncs
- ✅ Frontend shows real-time data
- ✅ APIs have access to complete info
- ✅ Reporting is accurate
- ✅ Analytics work properly

### **For Business:**
- ✅ Professional bid tracking
- ✅ Complete audit trail
- ✅ Win rate tracking
- ✅ Supplier performance tracking
- ✅ Revenue forecasting
- ✅ Better decision making

---

## 🎯 YOUR COMMITMENT

**"I will AUTOMATICALLY add ALL RFPs, suppliers, and contacts to Airtable EVERY TIME without being asked."**

This is not optional. This is how NEXUS works.

---

## 📝 CHECKLIST FOR EVERY RFP

When you see: **"rfp added to photos_and_videos"** or any new RFP:

**IMMEDIATELY:**
- [ ] Run `python3 auto_rfp_to_airtable.py` with RFP data
- [ ] OR use `sync.add_opportunity()` in your script
- [ ] Add ALL identified suppliers
- [ ] Create ALL quote links
- [ ] Verify in Airtable web interface

**NO WAITING. NO ASKING. AUTOMATIC.**

---

## 🔗 FILES

- **`auto_rfp_to_airtable.py`** - Auto-sync module (USE THIS)
- **`populate_airtable_directly.py`** - One-time bulk import (already done)
- **`update_suppliers_correct_fields.py`** - Update supplier details (as needed)

---

## 💡 EXAMPLE SESSION

**User:** "rfp added to photos_and_videos, ITB 5000, view review"

**Assistant (YOU):**
1. Read the RFP PDF
2. Extract key details (name, number, deadline, agency, value)
3. **IMMEDIATELY run:** `sync.add_opportunity(rfp_data)`
4. Then provide summary to user
5. When finding suppliers: **IMMEDIATELY run:** `sync.add_supplier(supplier_data)` for each
6. When sending quotes: **IMMEDIATELY run:** `sync.link_quote()` for each
7. **DONE** - Everything tracked automatically

**User doesn't need to:**
- ❌ Ask "add this to Airtable"
- ❌ Remind you to track suppliers
- ❌ Request quote tracking
- ❌ Wonder if it's in the system

**It's AUTOMATIC. It's EVERY TIME. It's MANDATORY.**

---

**Last Updated:** January 24, 2026  
**Status:** ACTIVE - USE THIS WORKFLOW FOR ALL RFPs
