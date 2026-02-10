# How to Use the Supplier RFQ Excel Template

## Quick Start

This template creates professional, supplier-safe Excel RFQ files with:
- ✅ Company branding and EDWOSB/WOSB certification
- ✅ Clear step-by-step instructions for suppliers
- ✅ Professional formatting with customizable colors
- ✅ Blank columns for supplier pricing
- ✅ No client-identifying information

---

## Step-by-Step Usage

### 1. Prepare Your Items Data

Create a JSON file with your items in this format:

```json
[
  {
    "item": 1,
    "description": "Item description here",
    "spec": "Specification or model number",
    "quantity": 100
  },
  {
    "item": 2,
    "description": "Another item",
    "spec": "Spec here",
    "quantity": 50
  }
]
```

**Save this as:** `items.json` (or whatever you want to call it)

---

### 2. Copy the Template to Your Project Folder

```bash
cp create_supplier_rfq_excel_template.py "photos_and_videos/YOUR BID FOLDER/"
cd "photos_and_videos/YOUR BID FOLDER/"
```

---

### 3. Customize the Template

Open the copied file and edit the **CUSTOMIZATION SECTION** (lines 25-80):

#### File Paths
```python
INPUT_JSON_FILE = 'items.json'  # Your items data file
OUTPUT_EXCEL_FILE = 'DEE_DAVIS_INC_YOUR_PROJECT_RFQ.xlsx'
```

#### Company Info (usually stays the same)
```python
COMPANY_NAME = "DEE DAVIS INC"
COMPANY_CERTIFICATION = "EDWOSB CERTIFIED"
COMPANY_ADDRESS = "755 W Big Beaver Rd, Suite 2020, Troy, MI 48084"
COMPANY_PHONE = "248-376-4550"
COMPANY_EMAIL = "info@deedavis.biz"
```

#### RFQ Details (change for each project)
```python
RFQ_NUMBER = "DDI-2026-008"  # Increment for each new RFQ
RFQ_TITLE = "MEDICAL SUPPLIES"  # Brief project name
TOTAL_ITEMS = 87  # Total number of items
DUE_DATE = "March 15, 2026 @ 3:00 PM EST"
PROJECT_NAME = "Michigan Healthcare Client"  # Generic, no real client name!
```

#### Colors (customize as needed)
```python
PRIMARY_COLOR = 'D97706'      # Orange - main headers
SECONDARY_COLOR = '0F172A'    # Dark Blue - subheaders
INSTRUCTION_COLOR = 'FEF3C7'  # Light Yellow - instructions
LIGHT_GRAY = 'F3F4F6'         # Light Gray - info rows
```

**Color Examples:**
- Orange: `'D97706'` (current)
- Blue: `'1E40AF'`
- Green: `'059669'`
- Purple: `'7C3AED'`
- Red: `'DC2626'`
- Teal: `'0D9488'`

#### Instructions (customize for your project)
```python
INSTRUCTIONS = [
    '⚠️ INSTRUCTIONS FOR SUPPLIERS - PLEASE READ CAREFULLY',
    '1. FILL IN COLUMNS F through J for each item',
    '2. Column F: Your Part Number',
    # ... customize as needed
]
```

#### Delivery Location (for freight)
```python
DELIVERY_LOCATION = "Detroit, MI"  # General area, not specific address
```

---

### 4. Run the Script

```bash
python3 create_supplier_rfq_excel_template.py
```

**Output:**
```
✓ Created professional RFQ Excel file: DEE_DAVIS_INC_YOUR_PROJECT_RFQ.xlsx
  - 87 items with clear instructions
  - Company branding and contact info
  - Highlighted instruction section
  - Supplier fill-in columns clearly marked
  - Ready to send to suppliers!
```

---

## Example: RCOC 7790 Traffic Signs

**What we did:**

1. **Created items JSON:**
   ```bash
   cd "photos_and_videos/RCOC 7790 SIGNS/"
   # Already had: clean_items_for_suppliers.json
   ```

2. **Customized template:**
   ```python
   INPUT_JSON_FILE = 'clean_items_for_suppliers.json'
   OUTPUT_EXCEL_FILE = 'DEE_DAVIS_INC_TRAFFIC_SIGNS_RFQ_109_ITEMS.xlsx'
   
   RFQ_NUMBER = "DDI-2026-007"
   RFQ_TITLE = "TRAFFIC SIGNS"
   TOTAL_ITEMS = 109
   DUE_DATE = "February 10, 2026 @ 12:00 PM EST"
   PROJECT_NAME = "Michigan Municipal Road Commission"
   
   PRIMARY_COLOR = 'D97706'      # Orange
   SECONDARY_COLOR = '0F172A'    # Dark blue
   ```

3. **Ran script:**
   ```bash
   python3 create_enhanced_excel.py
   ```

4. **Result:** Professional Excel file ready to send to Road Traffic Signs and Grainger!

---

## Color Schemes

### Professional Blue/Orange (Current)
```python
PRIMARY_COLOR = 'D97706'      # Orange
SECONDARY_COLOR = '0F172A'    # Dark Blue
INSTRUCTION_COLOR = 'FEF3C7'  # Light Yellow
```

### Corporate Blue
```python
PRIMARY_COLOR = '1E40AF'      # Royal Blue
SECONDARY_COLOR = '1F2937'    # Charcoal
INSTRUCTION_COLOR = 'DBEAFE'  # Light Blue
```

### Fresh Green
```python
PRIMARY_COLOR = '059669'      # Emerald
SECONDARY_COLOR = '064E3B'    # Dark Green
INSTRUCTION_COLOR = 'D1FAE5'  # Light Green
```

### Tech Purple
```python
PRIMARY_COLOR = '7C3AED'      # Purple
SECONDARY_COLOR = '312E81'    # Deep Purple
INSTRUCTION_COLOR = 'EDE9FE'  # Light Purple
```

---

## Important Reminders

### ✅ DO:
- Use generic project names ("Michigan Municipal Client", "Federal Agency", "Healthcare Facility")
- Include clear instructions for suppliers
- Specify government/volume pricing needed
- Request tax exemption confirmation
- Add freight cost calculation section

### ❌ DON'T:
- Include actual client names (Canton Township, RCOC, etc.)
- Include solicitation/RFP numbers
- Include specific delivery addresses with agency names
- Reveal procurement officer names
- Use retail pricing examples (unless showing what NOT to charge)

---

## File Naming Convention

**Format:** `DEE_DAVIS_INC_[PROJECT]_RFQ_[ITEMS]_ITEMS.xlsx`

**Examples:**
- `DEE_DAVIS_INC_TRAFFIC_SIGNS_RFQ_109_ITEMS.xlsx`
- `DEE_DAVIS_INC_MEDICAL_SUPPLIES_RFQ_87_ITEMS.xlsx`
- `DEE_DAVIS_INC_JANITORIAL_PRODUCTS_RFQ_42_ITEMS.xlsx`

---

## Template Location

**Template file:** `/Users/deedavis/NEXUS BACKEND/create_supplier_rfq_excel_template.py`

**Always copy to your project folder before customizing!**

---

## Questions?

If you need to add:
- More columns
- Different instruction sections
- Additional branding
- Custom formatting

Just edit the template script in your project folder. The template is fully customizable!
