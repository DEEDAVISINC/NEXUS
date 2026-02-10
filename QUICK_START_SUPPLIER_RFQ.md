# Quick Start: Generate Supplier RFQ

## When to Use This

**You received a solicitation from a buyer (RCOC, Canton, etc.) and need to get quotes from suppliers.**

---

## 3-Step Process

### 1️⃣ Extract Items (Supplier-Safe)

Create `items.json`:
```json
[
  {
    "item": 1,
    "description": "Item description",
    "spec": "Specification",
    "quantity": 100
  }
]
```

**❌ NO client names, NO solicitation numbers, NO specific addresses!**

---

### 2️⃣ Create Config JSON

**Minimum required:**

```json
{
    "request_type": "SUPPLIER",
    "company": {
        "name": "DEE DAVIS INC",
        "address": "755 W Big Beaver Rd, Suite 2020, Troy, MI 48084",
        "phone": "248-376-4550",
        "email": "info@deedavis.biz",
        "website": "www.deedavis.biz",
        "contact_person": "Dee Davis, President & CEO"
    },
    "rfq_details": {
        "rfq_number": "DDI-2026-XXX",
        "title": "PROJECT NAME",
        "issue_date": "March 1, 2026",
        "due_date": "March 10, 2026",
        "due_time": "12:00 PM EST",
        "project_name": "Michigan Client"
    },
    "colors": {
        "primary": "#D97706",
        "accent": "#0F172A",
        "text": "#374151"
    },
    "items_file": "items.json",
    "excel": {
        "output_file": "DEE_DAVIS_INC_PROJECT_RFQ.xlsx",
        "certification": "EDWOSB CERTIFIED",
        "delivery_location": "Metro Detroit, MI"
    }
}
```

**Save as:** `rfq_supplier_name_config.json`

---

### 3️⃣ Generate

```bash
python3 generate_supplier_rfq.py rfq_config.json
```

**Done!** → PDF + Excel ready to email

---

## What You Get

✅ **Professional PDF RFQ** - Branded quote request  
✅ **Professional Excel File** - With instructions, your branding, supplier fill-in columns  
✅ **Buyer-Protected** - No client-identifying information  

---

## Email to Supplier

**Subject:** Quote Request - DDI-2026-XXX - [Project Name]

**Attachments:**
- PDF RFQ
- Excel file
- Specifications PDF (if applicable)

---

## Change Colors

In config JSON:
```json
"colors": {
    "primary": "#1E40AF",    // Blue
    "accent": "#1F2937",     // Charcoal
    "text": "#374151"
}
```

Common colors:
- Orange: `#D97706`
- Blue: `#1E40AF`
- Green: `#059669`
- Purple: `#7C3AED`

---

## Full Documentation

See: `NEXUS_SUPPLIER_RFQ_SYSTEM.md`
