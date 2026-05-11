# HAVEN — Housing, Assistance, Vital Emergency Network

**Disaster Response TPA for Managed Care Organizations**

---

## Folder Structure

```
HAVEN/
├── AGREEMENTS/           ← Partner legal agreements (templates + generated)
│   ├── HAVEN_Partner_NDA.html
│   ├── HAVEN_Partner_Agreement_Comprehensive.html
│   ├── HAVEN_Business_Associate_Agreement.html
│   └── HAVEN_COI_Request.html
│
├── ONE_PAGERS/           ← Marketing materials for partners & MCOs
│   ├── HAVEN_Master_Proposal.html
│   ├── HAVEN_Partnership_OnePager.html
│   └── [Partner-type specific one-pagers]
│
├── OUTREACH/             ← Email templates for partner & MCO outreach
│   ├── HAVEN_MCO_OUTREACH_TEMPLATES.md
│   └── HAVEN_PARTNER_OUTREACH_[TYPE].md
│
├── STRATEGY/             ← Planning docs, registries, action plans
│   ├── HAVEN_ACTION_PLAN.md
│   └── [Strategy and planning docs]
│
├── GENERATED/            ← Auto-created: personalized docs per partner
│   └── [PARTNER-ID]/
│
└── SENT/                 ← Auto-created: copies of sent documents
    └── [PARTNER-ID]/
```

---

## Document Delivery System

HAVEN uses the **NEXUS Document Delivery System** (`nexus_document_delivery.py`) with a HAVEN-specific onboarding module (`haven_partner_onboarding.py`).

### Partner Onboarding Workflow

```
1. REGISTER      →  Partner added to registry
2. NDA SENT      →  NDA emailed to partner
3. NDA SIGNED    →  Partner signs and returns
4. AGREEMENT     →  Service Agreement sent
5. AGREEMENT     →  Partner signs and returns
   SIGNED
6. BAA SENT      →  HIPAA BAA sent
7. BAA SIGNED    →  Partner signs and returns
8. COI REQUEST   →  Insurance request sent
9. COI RECEIVED  →  Partner provides COI
10. CREDENTIALING →  Background checks, licenses verified
11. ACTIVE       →  Partner activated in HAVEN network
```

### Using the CLI

```bash
cd "/Users/deedavis/NEXUS BACKEND"

# Register a new partner
python3 haven_partner_onboarding.py register \
  --company "Acme Transport" \
  --contact "John Smith" \
  --email "john@acmetransport.com" \
  --phone "555-123-4567" \
  --type transport \
  --areas MI OH IN

# Start onboarding (sends NDA)
python3 haven_partner_onboarding.py send -p HAVEN-TP-2605101234 --doc nda

# After partner signs NDA, advance to next step
python3 haven_partner_onboarding.py advance -p HAVEN-TP-2605101234 --doc nda

# Check dashboard
python3 haven_partner_onboarding.py dashboard

# Check for partners needing follow-up
python3 haven_partner_onboarding.py reminders --days 3
```

### Using the API

```
POST /api/haven/partners                     # Register partner
GET  /api/haven/partners/<id>                # Get status
POST /api/haven/partners/<id>/generate       # Generate all docs
POST /api/haven/partners/<id>/send/<doc>     # Send specific doc
POST /api/haven/partners/<id>/start-onboarding  # Send NDA
POST /api/haven/partners/<id>/advance        # Mark signed, send next
POST /api/haven/partners/<id>/activate       # Activate partner
GET  /api/haven/dashboard                    # Onboarding dashboard
GET  /api/haven/reminders?days=3             # Pending follow-ups
```

---

## Agreement Templates

All agreements include **personalization placeholders**:

| Placeholder | Replaced With |
|-------------|---------------|
| `{{PARTNER_NAME}}` | Company legal name |
| `{{CONTACT_NAME}}` | Primary contact person |
| `{{PARTNER_ADDRESS}}` | Company address |
| `{{EFFECTIVE_DATE}}` | Agreement date |
| `{{PARTNER_TYPE}}` | housing / transport / medical |
| `{{SERVICE_AREAS}}` | States/regions covered |
| `{{PARTNER_ID}}` | HAVEN partner ID |

### Document Sequence by Partner Type

| Partner Type | Required Documents |
|--------------|-------------------|
| **Housing** | NDA → Service Agreement → BAA → COI |
| **Transport** | NDA → Service Agreement → BAA → COI |
| **Medical** | NDA → Service Agreement → BAA → COI |

---

## Integration with NEXUS

HAVEN connects to the central document delivery system:

```python
from nexus_document_delivery import NEXUSDocumentDelivery

delivery = NEXUSDocumentDelivery()

# Send a document
result = delivery.send(
    document_type="haven_nda",
    recipient_email="partner@example.com",
    recipient_name="Partner Company",
    subject="HAVEN Partner NDA",
    html_body="<html>...</html>",
    attachments=[{"path": "/path/to/nda.pdf", "filename": "NDA.pdf"}],
    source_module="haven",
    source_record_id="HAVEN-TP-2605101234"
)

# Track delivery status
delivery.update_status(result["delivery_id"], "signed")
```

---

## Partner Types

### Housing Partners
Hotels, vacation rentals, temporary housing providers.
- Provides shelter during evacuations
- Must have General Liability, Property, Workers Comp

### Transport Partners
NEMT, rideshare, medical transport providers.
- Provides member evacuation and medical transport
- Must have GL, Commercial Auto, Workers Comp, Professional Liability

### Medical Partners  
DME, pharmacy, home health, medical equipment providers.
- Ensures medical continuity during disasters
- Must have GL, Professional Liability, Product Liability, Workers Comp

---

## SendGrid Configuration

Document delivery requires SendGrid environment variables:

```bash
export SENDGRID_API_KEY="SG.xxxx"
export SENDGRID_FROM_EMAIL="info@deedavis.biz"
```

Without these, documents will be **staged** in the `SEND_TO_SUBCONTRACTOR/` folder for manual send.

---

## Files

| File | Purpose |
|------|---------|
| `haven_partner_onboarding.py` | Partner onboarding system |
| `nexus_document_delivery.py` | Central delivery infrastructure |
| `haven_module.py` | HAVEN core module |
| `haven_outreach_engine.py` | Partner/MCO outreach automation |
| `haven_disaster_watch.py` | Disaster monitoring |

---

*HAVEN — Housing, Assistance, Vital Emergency Network*
*Dee Davis Inc. — Disaster Response TPA*
