# NEXUS Supplier RFQ Generation System

## What This Does

**AUTOMATICALLY generates professional supplier RFQ packages when you receive a solicitation that requires supplier quotes.**

When you get a bid from a buyer (like RCOC, Canton Township, etc.) that requires you to source products, this system creates:

1. ✅ **Professional PDF RFQ** - Branded quote request document
2. ✅ **Professional Excel File** - With clear instructions, company branding, and supplier fill-in columns
3. ✅ **Supplier-Safe** - No client-identifying information (protects your business)

---

## The Workflow

### When You Receive a Solicitation

```
BUYER SOLICITATION
        ↓
Extract items/specs
        ↓
Create JSON config
        ↓
Run: python3 generate_supplier_rfq.py config.json
        ↓
BOOM! → PDF + Excel ready to send
```

### Example: RCOC 7790 Traffic Signs

**You received:** RCOC solicitation for 109 traffic signs

**What NEXUS does:**
1. You create config JSON with RFQ details
2. Extract items to clean JSON (no RCOC branding)
3. Run one command
4. Get professional PDF + Excel to send to Road Traffic Signs & Grainger

---

## How to Use It

### Step 1: Create Clean Items JSON

Extract items from buyer solicitation into supplier-safe format:

```json
[
  {
    "item": 1,
    "description": "STOP Sign, 30x30 Octagon, R1-1",
    "spec": "ASTM TYPE IV",
    "quantity": 600
  },
  {
    "item": 2,
    "description": "Chevron Alignment (Reversible), 24x30, W1-8RL",
    "spec": "ASTM TYPE XI",
    "quantity": 350
  }
]
```

**Save as:** `clean_items_for_suppliers.json` (or similar)

**CRITICAL:** No client names, no solicitation numbers, no specific addresses!

---

### Step 2: Create RFQ Config JSON

Create a config file with all RFQ details:

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
        "rfq_number": "DDI-2026-008",
        "title": "Medical Supplies",
        "issue_date": "March 1, 2026",
        "due_date": "March 10, 2026",
        "due_time": "12:00 PM EST",
        "project_name": "Michigan Healthcare Client",
        "contract_period": "Annual supply contract"
    },
    "colors": {
        "primary": "#D97706",
        "accent": "#0F172A",
        "text": "#374151"
    },
    "introduction": "DEE DAVIS INC, an EDWOSB-certified woman-owned small business, is seeking competitive bulk pricing...",
    
    "items_file": "clean_items_for_suppliers.json",
    
    "excel": {
        "output_file": "DEE_DAVIS_INC_MEDICAL_SUPPLIES_RFQ_87_ITEMS.xlsx",
        "certification": "EDWOSB CERTIFIED",
        "delivery_location": "Metro Detroit, MI",
        "column_headers": [
            "Item #",
            "Description",
            "Specification",
            "Quantity",
            "Unit",
            "YOUR PART NUMBER",
            "YOUR UNIT PRICE",
            "EXTENDED TOTAL",
            "LEAD TIME",
            "NOTES"
        ]
    }
}
```

**Save as:** `rfq_[supplier_name]_config.json`

---

### Step 3: Generate RFQ Package

**One command generates everything:**

```bash
python3 generate_supplier_rfq.py "photos_and_videos/YOUR BID FOLDER/rfq_config.json"
```

**Output:**
```
📋 Generating Supplier RFQ Package...

1️⃣ Generating PDF RFQ...
   ✓ Generated: rfq_supplier.pdf

2️⃣ Generating Excel file...
   ✓ Generated: DEE_DAVIS_INC_PROJECT_RFQ_87_ITEMS.xlsx

✅ RFQ Package Complete!
📤 Ready to send to suppliers
```

---

### Step 4: Send to Suppliers

**Email package includes:**
- ✅ PDF RFQ (professional quote request)
- ✅ Excel file (for supplier pricing)
- ✅ Specifications PDF (technical docs)

---

## JSON Config Reference

### Required Fields

```json
{
    "company": { ... },           // Your company info
    "rfq_details": { ... },       // RFQ number, dates, project name
    "items_file": "items.json",   // OR "items_data": [...]
    "excel": {
        "output_file": "filename.xlsx",
        "certification": "EDWOSB CERTIFIED",
        "delivery_location": "Metro Detroit, MI"
    }
}
```

### Optional Excel Customization

```json
"excel": {
    "output_file": "your_filename.xlsx",
    "certification": "EDWOSB CERTIFIED",  // Or "WOSB", "SBA", etc.
    "instruction_color": "FEF3C7",        // Hex color (no #)
    "light_gray": "F3F4F6",               // Hex color (no #)
    "delivery_location": "General Area",   // NOT specific address
    "column_headers": [
        "Item #",
        "Description",
        "Your custom header...",
        ...
    ],
    "instructions": [
        "⚠️ INSTRUCTIONS FOR SUPPLIERS",
        "1. Custom instruction...",
        "2. Another instruction...",
        ...
    ]
}
```

---

## Color Schemes

Change the `colors` section in your config:

### Professional Orange/Blue (Default)
```json
"colors": {
    "primary": "#D97706",
    "accent": "#0F172A",
    "text": "#374151"
}
```

### Corporate Blue
```json
"colors": {
    "primary": "#1E40AF",
    "accent": "#1F2937",
    "text": "#374151"
}
```

### Fresh Green
```json
"colors": {
    "primary": "#059669",
    "accent": "#064E3B",
    "text": "#374151"
}
```

---

## File Organization

**Recommended folder structure:**

```
photos_and_videos/
└── [CLIENT] [BID TYPE]/
    ├── [Original RFQ PDF]
    ├── clean_items_for_suppliers.json
    ├── rfq_supplier_a_config.json
    ├── rfq_supplier_b_config.json
    ├── DEE_DAVIS_INC_PROJECT_RFQ_ITEMS.xlsx  ← Auto-generated
    ├── rfq_supplier_a.pdf                      ← Auto-generated
    └── rfq_supplier_b.pdf                      ← Auto-generated
```

---

## Example: Real-World Usage

### RCOC 7790 Traffic Signs

**Scenario:** RCOC solicitation for 109 traffic signs, need quotes from Road Traffic Signs & Grainger

**What I did:**

1. **Extracted items:**
   ```bash
   # Created clean_items_for_suppliers.json (109 items, no RCOC branding)
   ```

2. **Created configs:**
   - `rfq_road_traffic_signs_config.json`
   - `rfq_grainger_config.json`

3. **Generated RFQs:**
   ```bash
   python3 generate_supplier_rfq.py rfq_road_traffic_signs_config.json
   python3 generate_supplier_rfq.py rfq_grainger_config.json
   ```

4. **Got:**
   - ✅ 2 professional PDF RFQs
   - ✅ 1 Excel file (same one for both suppliers)
   - ✅ Both branded with DDI, clear instructions, no RCOC info

5. **Sent to suppliers:**
   - Road Traffic Signs: PDF + Excel + Specs
   - Grainger: PDF + Excel + Specs (mentioned account #)

**Result:** Professional RFQ packages ready in 2 minutes!

---

## Integration with NEXUS Frontend

**Future enhancement:** Add this to the NEXUS Quote System UI

When user selects "Generate Supplier RFQ":
1. UI collects: supplier name, items, specs
2. Generates JSON config automatically
3. Calls `generate_supplier_rfq.py` via API
4. Returns download links for PDF + Excel
5. User emails to supplier

---

## Tips & Best Practices

### ✅ DO:
- Use generic project names ("Michigan Municipal Client")
- Include clear, step-by-step instructions in Excel
- Specify government/volume pricing needed
- Request tax exemption confirmation
- Add freight cost calculation
- Mention EDWOSB certification (relationship builder)

### ❌ DON'T:
- Include actual client names (Canton Township, RCOC, etc.)
- Include solicitation/RFP numbers
- Include specific delivery addresses with agency names
- Reveal procurement officer names
- Use retail pricing as targets (unless showing what's too high)

---

## Troubleshooting

### "No items data found"
- Make sure `items_file` points to valid JSON file
- OR include `items_data` array directly in config

### "Excel generation failed"
- Check that `openpyxl` is installed: `pip3 install openpyxl`
- Verify items JSON format is correct

### "PDF generation failed"
- Check that `reportlab` is installed: `pip3 install reportlab`
- Or install `wkhtmltopdf`: `brew install wkhtmltopdf`

---

## Script Locations

**Main script:** `/Users/deedavis/NEXUS BACKEND/generate_supplier_rfq.py`

**PDF generator:** `/Users/deedavis/NEXUS BACKEND/generate_rfq_pdf.py`

**Template (standalone):** `/Users/deedavis/NEXUS BACKEND/create_supplier_rfq_excel_template.py`

---

## Quick Command Reference

```bash
# Generate complete RFQ package (PDF + Excel)
python3 generate_supplier_rfq.py config.json

# Generate PDF only (old way)
python3 generate_rfq_pdf.py config.json

# Generate Excel only (standalone template)
python3 create_supplier_rfq_excel_template.py
```

---

**This system is now part of your automated NEXUS workflow!** 🚀

Every time you need to get quotes from suppliers, use this system to create professional, branded, buyer-protected RFQ packages in minutes.
