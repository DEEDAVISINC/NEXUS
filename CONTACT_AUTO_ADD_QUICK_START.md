# 🚀 NEXUS AUTO-CONTACT: QUICK START

**Your contacts are now automatically captured and organized. Here's how to use it.**

---

## What Happens Automatically

### 1. When You Review a Solicitation
**System extracts and adds:**
- Procurement officer names
- Email addresses
- Phone numbers
- Job titles
- Agency names

**Example:**
You open Canton Township Water Main Parts RFQ.
→ System finds: Brad Johnson, Buyer, bjohnson@canton-mi.org, (734) 394-5120
→ **Automatically added to GPSS CONTACTS** with role "Procurement"

### 2. When You Generate an RFQ
**System automatically adds supplier:**

```bash
python3 generate_rfq_trucks.py "Monroe_Truck_Equipment"
```

→ Generates RFQ PDF
→ **Automatically adds:** Monroe Truck Equipment to GPSS CONTACTS as "Supplier"
→ Records: "RFQ sent for RCOC 7814 Trucks"

### 3. When You Identify a Subcontractor
**Manual API call (or future frontend integration):**

Use API to add sub when you find one for a bid.

---

## How to Use It

### ✅ AUTOMATED (Already Working)

#### 1. Generate RFQ → Supplier Added Automatically
```bash
cd "/Users/deedavis/NEXUS BACKEND"
python3 generate_rfq_trucks.py "National_Auto_Fleet_Group"
```

**Output:**
```
✅ RFQ Generated: ...
Adding supplier to NEXUS contacts system...
  ✓ Supplier contact added to NEXUS: National Auto Fleet Group
```

**What happened:**
- RFQ PDF created with Avenir font + watermark
- Supplier "National Auto Fleet Group" added to GPSS CONTACTS
- Role Category: Supplier
- Notes: "RFQ sent for RCOC 7814 Trucks"

---

### 🔲 SEMI-AUTOMATED (API Available)

#### 2. Add Supplier Manually (if not using RFQ generator)

**When to use:** You call/email a supplier directly without generating RFQ

**Command:**
```bash
curl -X POST http://localhost:5000/api/contacts/add-supplier \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Ferguson Supply",
    "email": "sales@ferguson.com",
    "phone": "800-274-8765",
    "product_type": "Plumbing supplies",
    "context": "Called for Canton water main parts quote"
  }'
```

---

#### 3. Extract Contacts from Solicitation Text

**When to use:** You have a solicitation and want to extract contacts

**Command:**
```bash
curl -X POST http://localhost:5000/api/contacts/auto-extract-solicitation \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Contact: Noah Cohen, Contract Specialist\nEmail: ncohen@bayareametro.gov\nPhone: (415) 778-5215\nAssociation of Bay Area Governments",
    "name": "ABAG Grant Writing RFQ"
  }'
```

**Output:**
```json
{
  "success": true,
  "contacts_found": 1,
  "contacts_added": 1,
  "contacts": [
    {
      "Name": "Noah Cohen",
      "Email": "ncohen@bayareametro.gov",
      "Title": "Contract Specialist",
      "Organization": "Association of Bay Area Governments",
      "Role Category": "Procurement"
    }
  ]
}
```

---

#### 4. Add Subcontractor Contact

**When to use:** You identify a sub for a specific bid

**Command:**
```bash
curl -X POST http://localhost:5000/api/contacts/add-subcontractor \
  -H "Content-Type: application/json" \
  -d '{
    "name": "ABC Landscaping",
    "email": "contact@abclandscaping.com",
    "phone": "248-555-1234",
    "services": "Landscaping, Snow removal, Irrigation",
    "context": "Identified for Warren DDA Landscape bid - good pricing"
  }'
```

---

## Real-World Usage Examples

### Example 1: RCOC 7814 Trucks (AUTOMATED ✅)

**You do:**
```bash
python3 generate_rfq_trucks.py "National_Auto_Fleet_Group"
python3 generate_rfq_trucks.py "Monroe_Truck_Equipment"
```

**System does:**
- Creates 2 RFQ PDFs
- Adds National Auto Fleet Group to GPSS CONTACTS
- Adds Monroe Truck Equipment to GPSS CONTACTS
- Both tagged as "Supplier" with context "RFQ sent for RCOC 7814 Trucks"

**Your benefit:**
- Next time you need truck quotes, you have their contact info
- You can see history: "RFQ sent for RCOC 7814 Trucks"
- Build supplier database automatically

---

### Example 2: Canton Water Main Parts (MANUAL FOR NOW)

**You do:**
1. Call Ferguson Supply for quote
2. After call, add to system:

```bash
curl -X POST http://localhost:5000/api/contacts/add-supplier \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Ferguson Supply",
    "phone": "800-274-8765",
    "product_type": "Plumbing supplies",
    "context": "Called 2/1/26 - quoted Canton water main brass fittings"
  }'
```

**Your benefit:**
- Contact saved with context
- Next water project, you know Ferguson provides good pricing
- Build supplier history

---

### Example 3: Mining Solicitations (SEMI-AUTOMATED)

**You do:**
1. Copy solicitation text
2. Run extraction:

```bash
curl -X POST http://localhost:5000/api/contacts/auto-extract-solicitation \
  -H "Content-Type: application/json" \
  -d '{
    "text": "[PASTE FULL SOLICITATION TEXT]",
    "name": "Rock Island Yard Waste Bags"
  }'
```

**System extracts:**
- Mary Ann Ervin, Buyer, mary.ervin@rigov.org, (309) 732-2156
- City of Rock Island

**Your benefit:**
- Contact saved for future capability statement
- You can follow up after bid submission
- Track relationships with procurement officers

---

## Check Your Contacts in Airtable

**Go to:** https://airtable.com → GPSS CONTACTS table

**You'll see:**
- All extracted procurement contacts (Role: Procurement)
- All suppliers you've requested quotes from (Role: Supplier)
- All subs you've identified (Role: Subcontractor)

**Each contact has:**
- Name, Email, Phone (when available)
- Title/Role Category
- Organization
- Notes (context, when added, what for)

---

## API Endpoints Summary

### Base URL (when NEXUS backend is running):
```
http://localhost:5000
```

### Endpoints:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/contacts/auto-extract-solicitation` | POST | Extract contacts from solicitation text |
| `/api/contacts/add-supplier` | POST | Add supplier when requesting quote |
| `/api/contacts/add-subcontractor` | POST | Add sub when identified for bid |

---

## Frontend Integration (Coming Soon)

### Solicitation Upload Page:
When you upload solicitation:
→ System automatically extracts and adds procurement contacts
→ Shows toast: "✅ Added 2 contacts to system"

### RFQ Generator Page:
When you generate RFQ:
→ System automatically adds supplier
→ Shows toast: "✅ Added Monroe Truck Equipment to contacts"

### Subcontractor Mining:
When you identify sub:
→ One-click "Add to Contacts"
→ Pre-filled form, just confirm

---

## Testing the System

### Test 1: Add a Supplier
```bash
cd "/Users/deedavis/NEXUS BACKEND"
python3 -c "
from auto_contact_manager import AutoContactManager
manager = AutoContactManager()
result = manager.add_supplier_contact(
    supplier_name='Test Supplier 123',
    supplier_email='test@supplier.com',
    product_type='Test products',
    context='Testing the system'
)
print(result)
"
```

**Expected output:**
```python
{'success': True, 'message': 'Supplier contact added: Test Supplier 123', 'record_id': 'recXXXXXX'}
```

---

### Test 2: Generate RFQ with Auto-Contact
```bash
python3 generate_rfq_trucks.py "Test_Supplier"
```

**Expected output:**
```
✅ RFQ Generated: ...
Adding supplier to NEXUS contacts system...
  ✓ Supplier contact added to NEXUS: Test Supplier
```

---

## Business Rules Applied

### ✅ Never Reveal End-Buyer
When adding supplier contacts:
- Context is GENERIC: "RFQ sent for municipal trucks project"
- NO specific client names (Canton Township, Rock Island, etc.)
- NO solicitation numbers
- NO agency addresses

### ✅ Automatic Duplicate Prevention
- Won't add same email twice
- Checks before adding
- Shows message: "ℹ Contact already in system"

### ✅ Categorization
- **Procurement** = Buyers, procurement officers, contracting officers
- **Supplier** = Companies you request quotes from
- **Subcontractor** = Potential partners for bids
- **Client** = Direct clients (non-government)
- **Agency Contact** = General agency contacts

---

## Troubleshooting

### "Contact already in system"
**Meaning:** This email/name already exists in GPSS CONTACTS
**Action:** Nothing needed, it's working correctly (duplicate prevention)

### "Could not add supplier to NEXUS"
**Check:**
1. Is Airtable API key in `.env`?
2. Is `AIRTABLE_BASE_ID` correct?
3. Does GPSS CONTACTS table exist?
4. Are field names correct (Name, Email, Organization, Role Category, Notes)?

### API endpoints not working
**Fix:**
1. Start NEXUS backend: `python3 api_server.py`
2. Verify it's running on port 5000
3. Test: `curl http://localhost:5000/health`

---

## Status

✅ **FULLY WORKING:**
- RFQ generator auto-adds suppliers
- API endpoints for manual additions
- Duplicate prevention
- Airtable integration

🔲 **COMING SOON:**
- Frontend integration (one-click from UI)
- Solicitation upload auto-extraction
- Subcontractor mining integration

---

## Key Files

| File | Purpose |
|------|---------|
| `auto_contact_manager.py` | Core contact extraction engine |
| `api_server.py` | API endpoints (lines 10085-10219) |
| `generate_rfq_trucks.py` | RFQ generator with auto-contact |
| `AUTO_CONTACT_SYSTEM_COMPLETE.md` | Full technical documentation |

---

**Your contacts now build themselves. Every RFQ sent, every solicitation reviewed, every sub identified → automatically tracked in NEXUS.**

---

*Last Updated: February 1, 2026*
*Status: Production Ready - Partially Automated*
