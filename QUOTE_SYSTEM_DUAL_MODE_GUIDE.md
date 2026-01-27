# Quote System - Dual Mode Guide

**Two distinct quote request types built into the system:**

---

## 🎯 When to Use Each Type

### 📦 Supplier/Product Quotes
**Use for:** Materials, equipment, products, supplies

**Examples:**
- Aggregate materials (sand, gravel, crushed stone)
- Industrial supplies (bolts, tools, equipment)
- Chemical products (chlorine, cleaners)
- Office supplies
- Water infrastructure parts
- Steel containers
- Anything you BUY and RESELL

**Focus:** Product specs, pricing, delivery

---

### 👷 Subcontractor Service Quotes
**Use for:** Professional services, labor, construction

**Examples:**
- Landscaping services
- Lawn maintenance
- Construction work
- Installation services
- Repair/maintenance services
- Snow removal
- Painting, electrical, plumbing
- Anything requiring LABOR and COMPLIANCE

**Focus:** Insurance, bonding, licenses, W-9, references

---

## 📋 What's Different Between Them?

### Supplier Quotes Include:
- ✅ Product specifications
- ✅ Quantity and unit pricing
- ✅ Delivery terms
- ✅ Payment terms
- ✅ Lead times

### Subcontractor Quotes ALSO Include:
- ✅ **General Liability Insurance** (minimum $1M)
- ✅ **Certificate of Insurance** required with quote
- ✅ **W-9 Form** required
- ✅ **Business License** verification
- ✅ **Worker's Compensation** proof
- ✅ **Auto Insurance** (if applicable)
- ✅ **Three references** from similar projects
- ✅ **Safety records** and protocols
- ✅ **Bonding capability** (may be required)

---

## 🖥️ How to Use the System

### Step 1: Select Request Type

When you open the Quote Generator, you'll see two buttons at the top:

```
📦 Supplier/Product Quote          👷 Subcontractor Services
Materials, equipment, supplies     Landscaping, construction, services
```

**Click the one that matches your need.**

---

### Step 2: Load Template

Click **"📋 Load Template"** to get the appropriate template.

**It automatically loads the right template based on your selection!**

---

### Step 3: Fill in Details

#### For Supplier Quotes:
```
RFQ_NUMBER: DDI-2026-001
TITLE: Aggregate Materials Quote Request
ISSUE_DATE: January 27, 2026
DUE_DATE: February 3, 2026
DUE_TIME: 2:00 PM EST
CONTRACT_PERIOD: 12 months

INTRODUCTION:
DEE DAVIS INC is seeking competitive quotes for a Michigan municipal client.

SCOPE:
Vendor will provide aggregate materials as specified below.

KEY_REQUIREMENTS:
- Delivery within 2 business days
- MDOT specifications required
- Net 30 payment terms

ITEMS:
1 | Fill Sand | Clear of debris and rocks | 300 | tons
2 | 6A Stone | Standard grade | 500 | tons
```

#### For Subcontractor Quotes:
```
REQUEST_TYPE: SUBCONTRACTOR
RFQ_NUMBER: DDI-2026-005
TITLE: Commercial Landscaping Services
ISSUE_DATE: January 27, 2026
DUE_DATE: February 5, 2026
DUE_TIME: 3:00 PM EST
CONTRACT_PERIOD: 12 months

INTRODUCTION:
DEE DAVIS INC is seeking qualified landscaping subcontractors for a Michigan municipal contract.

SCOPE:
Subcontractor will provide professional landscaping services including mowing, trimming, fertilization, and seasonal maintenance.

KEY_REQUIREMENTS:
- Must carry minimum $1M General Liability Insurance
- Certificate of Insurance required with quote
- W-9 form required
- Valid business license
- Worker's Compensation insurance proof
- Provide 3 recent references
- Background checks may be required

SERVICES:
1 | Weekly Lawn Mowing | 40 acres municipal property | 30 weeks | per season
2 | Fertilization | Spring and fall applications | 2 applications | per year
3 | Snow Removal | As needed during winter | On-call | per event

COMPLIANCE_REQUIREMENTS:
- General Liability Insurance: Minimum $1,000,000
- Auto Insurance: Minimum $1,000,000
- Workers Compensation: As required by Michigan law
- Business License: Current and valid
- Bonding Capability: May be required for award
```

---

### Step 4: Generate PDF

Click **"✨ Generate Quote Request"**

The system will:
1. Parse your template
2. Generate a professional PDF with:
   - Company logo watermark (top and bottom)
   - Avenir font styling
   - Properly formatted tables
   - **All compliance requirements (for subcontractors)**
3. Create download link

---

### Step 5: Download & Send

Click **"📥 Download PDF"** and send to your suppliers or subcontractors.

---

## 🚨 Critical Business Rules (Both Types)

**NEVER reveal in quotes:**
- ❌ Client/agency names
- ❌ Government solicitation numbers
- ❌ Procurement officer names
- ❌ Specific addresses

**ALWAYS use:**
- ✅ Generic DDI numbers (DDI-2026-001, DDI-2026-002)
- ✅ "Michigan municipal client"
- ✅ "Southeast Michigan" for location
- ✅ Quote deadline EARLIER than government deadline

---

## 📄 Sample Output Differences

### Supplier Quote PDF Includes:
1. Request for Quote (header)
2. RFQ Details
3. Introduction
4. Items Table (Description, Specs, Qty, Unit, Pricing)
5. Quote Submission Requirements
6. Contact Information

### Subcontractor Quote PDF Includes:
1. Request for Quote - **Subcontractor Services** (header)
2. RFQ Details
3. Introduction
4. **Services Table** (Service, Scope, Volume, Unit, Pricing)
5. **Compliance & Insurance Requirements** ← NEW SECTION
6. **Quote Submission Requirements - Subcontractor** ← Enhanced
7. **Required Documents List:**
   - Certificate of Insurance
   - W-9 Form
   - Business License
   - Worker's Comp proof
   - Auto Insurance proof
   - Three references
   - Pricing breakdown
   - Safety records
8. Contact Information

---

## ✅ Quick Decision Guide

**Ask yourself: "Am I buying a PRODUCT or hiring LABOR?"**

| Scenario | Request Type |
|----------|--------------|
| Buying sand, gravel, stone | 📦 Supplier |
| Buying industrial supplies | 📦 Supplier |
| Buying equipment | 📦 Supplier |
| Buying chemicals | 📦 Supplier |
| Hiring landscaping company | 👷 Subcontractor |
| Hiring construction crew | 👷 Subcontractor |
| Hiring snow removal service | 👷 Subcontractor |
| Hiring maintenance service | 👷 Subcontractor |

---

## 🎨 Color Schemes (Both Types)

Both types support color schemes:

```
COLOR_SCHEME: 1  (Navy & Orange - Default)
COLOR_SCHEME: 2  (Brown & Orange)
COLOR_SCHEME: 3  (Purple & Purple)
COLOR_SCHEME: 4  (Dark Blue & Cyan)
COLOR_SCHEME: 5  (Brown & Orange Alt)
```

---

## 💡 Pro Tips

### For Supplier Quotes:
- Keep it simple and product-focused
- Emphasize specs and quantity
- Delivery terms are key
- Net 30 payment preferred

### For Subcontractor Quotes:
- Emphasize compliance upfront
- Request all documents WITH the quote
- Include safety requirements
- Reference checks are critical
- Insurance minimums are NON-NEGOTIABLE

---

## 🚀 System Benefits

**Automatic:**
- ✅ Professional formatting
- ✅ Logo watermarking
- ✅ Compliance sections (subcontractor)
- ✅ Supplier protection rules enforced
- ✅ Timestamped and tracked

**No manual work:**
- You just fill in the template
- System handles all formatting
- PDF generated instantly
- Ready to send

---

## 📞 Support

If unsure which type to use, ask yourself:

**"Would I need their insurance certificate and W-9 before starting work?"**

- **YES** → Use Subcontractor
- **NO** → Use Supplier

---

**Remember:** The system protects your business by keeping client information confidential in BOTH types!
