# PRODUCT CATALOG AUTOMATION RULE
**MANDATORY: Save ALL Product Information Immediately**

---

## 🚨 THE RULE

**EVERY TIME you receive a supplier quote, catalog, or product information:**

### **IMMEDIATELY CREATE A PYTHON SCRIPT TO ADD TO NEXUS**

No exceptions. No delays. No "we'll do it later."

---

## ✅ WHAT TO CAPTURE (ALWAYS)

For **EVERY PRODUCT:**

1. **Supplier SKU/Item Number** (TreeStuff 24791, Zoro G4519551, Grainger 846N89, etc.)
2. **Manufacturer Name** (Master Lock, Kimberly-Clark, DMM, etc.)
3. **Manufacturer Part Number** (M1KALFSTSLZ12KS, 04460, etc.)
4. **Model Number** (X-Arbor, Banshee, etc.)
5. **Product Description** (full name and specs)
6. **Unit Price** (from quote)
7. **UPC/EAN Code** (if available)
8. **Unit of Measure** (EA, PK, CTN, etc.)
9. **Supplier Name** (TreeStuff, Grainger, Zoro, etc.)
10. **Quote Number/Reference**
11. **Date of Quote**
12. **Contract/RFQ Used In**
13. **Any alternative SKUs** (if product available from multiple suppliers)

---

## 📋 WORKFLOW (MANDATORY)

### **STEP 1: Receive Quote**
Supplier sends quote (email, PDF, verbal, etc.)

### **STEP 2: Create Add Script IMMEDIATELY**
```bash
# Create Python script to add products
python3 create_add_products_script.py
```

### **STEP 3: Run Script**
```bash
python3 add_[source]_products.py
```

### **STEP 4: Verify in Airtable**
Check that all products with SKUs are now searchable

---

## 📝 SCRIPT TEMPLATE

Save this as your starting point:

```python
#!/usr/bin/env python3
"""
Add [SOURCE] Products to NEXUS
Adds all products from [QUOTE/CATALOG] to GPSS PRODUCTS table
"""

import os
from pyairtable import Api

# Load .env
env_file = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(env_file):
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()

api_key = os.environ.get('AIRTABLE_API_KEY')
base_id = os.environ.get('AIRTABLE_BASE_ID')

if not api_key or not base_id:
    print('❌ ERROR: Missing Airtable credentials')
    exit(1)

api = Api(api_key)
table = api.table(base_id, 'GPSS PRODUCTS')

products = [
    {
        'NAME': 'Product Name Here',
        'PRODUCT CATEGORY': 'Category - Subcategory',
        'SUPPLIER': 'Supplier Name',
        'UNIT PRICE': '00.00/unit',
        'Description': '''Supplier SKU: XXXXX
Manufacturer: Company Name
Manufacturer Part #: PARTNUM
Model: ModelName
UPC: 123456789
Quote: Q-12345 (Date)
Contract: CLIENT RFQ#
Cost: $XX.XX/unit

Additional notes, specs, alternatives here.'''
    }
]

print(f'🚀 ADDING {len(products)} PRODUCTS TO NEXUS...\n')

added = 0
for p in products:
    try:
        table.create(p)
        sku = p['Description'].split('SKU: ')[1].split('\\n')[0] if 'SKU:' in p['Description'] else 'N/A'
        print(f"✅ {p['NAME']}")
        print(f"   SKU: {sku} - ${p['UNIT PRICE']}\n")
        added += 1
    except Exception as e:
        print(f"❌ ERROR: {p['NAME']}: {e}\n")

print(f"✅ Added {added} of {len(products)} products!")
```

---

## 🎯 EXAMPLES

### **Example 1: TreeStuff Forestry Quote**
**Received:** TreeStuff Quote Q-52998 with 11 items

**Action:**
1. Created `add_forestry_products.py` immediately
2. Captured all 11 SKUs (33166, 99863, 24791, etc.)
3. Ran script → All in NEXUS ✅
4. Now searchable anytime

---

### **Example 2: Grainger Padlocks Quote**
**Received:** Grainger Quote for CPS Energy padlocks

**Action:**
1. Create `add_cps_padlocks_products.py` immediately
2. Capture all SKUs, manufacturer part numbers
3. Run script → All in NEXUS ✅
4. Never lose this info again

---

### **Example 3: Supplier Catalog**
**Received:** New supplier sends 50-item catalog

**Action:**
1. Create `add_[supplier]_catalog_products.py`
2. Add all 50 items with SKUs/part numbers
3. Run script → Entire catalog in NEXUS ✅
4. Instant access for future quotes

---

## 💰 WHY THIS MATTERS

### **Without Product Catalog:**
- ❌ "What was that TreeStuff SKU for the helmet?"
- ❌ Re-search suppliers every time
- ❌ Waste 30-60 minutes finding info
- ❌ Risk wrong part numbers
- ❌ Can't quote quickly

### **With Product Catalog:**
- ✅ Search "X-Arbor helmet" → Instant SKU 24791
- ✅ See all suppliers who carry it
- ✅ Compare pricing instantly
- ✅ Quote in 5 minutes
- ✅ Never lose product data

---

## 🚀 PRODUCTIVITY GAINS

| Task | Without Catalog | With Catalog | Time Saved |
|------|----------------|--------------|------------|
| Find SKU | 15-30 min | 10 seconds | **29 min** |
| Compare suppliers | 1 hour | 2 minutes | **58 min** |
| Similar quote | 2-3 hours | 15 minutes | **2.5 hrs** |
| Reorder/renewal | 3-4 hours | 30 minutes | **3 hrs** |

**Per bid:** Save 4-8 hours  
**Per month:** Save 50+ hours  
**Per year:** Save 600+ hours!

---

## 📊 CURRENT CATALOG STATUS

**As of January 30, 2026:**

| Source | Products | Status |
|--------|----------|--------|
| RCOC Paper (7732) | 5 items | ✅ IN NEXUS |
| RCOC Wipers (7731) | 1 item | ✅ IN NEXUS |
| RCOC Wiper Blades (7798) | 3 items | ✅ IN NEXUS |
| RCOC Forestry (7734) | 11 items | ✅ IN NEXUS |
| **TOTAL** | **20 products** | **✅ SEARCHABLE** |

**Next to add:**
- CPS Energy padlocks (when Grainger quotes - 6 items)
- RCOC Welding supplies (when quoted - 17 items)
- RCOC Building tools (when quoted - ~15 items)
- Any other quotes received

---

## 🎯 MAKE IT A HABIT

**Every supplier interaction:**

1. **Quote received** → Create add script
2. **Catalog received** → Create add script
3. **Product discussed** → Create add script
4. **New supplier found** → Create add script

**No exceptions. This is productivity gold.**

---

## 📁 FILE NAMING CONVENTION

```
add_[source]_products.py
```

**Examples:**
- `add_forestry_products.py` ✅
- `add_cps_padlocks_products.py` ✅
- `add_grainger_catalog_products.py` ✅
- `add_supplier_xyz_products.py` ✅

Keep them all in root directory for easy access.

---

## ✅ CURRENT SCRIPTS CREATED

1. ✅ `add_rcoc_products.py` (9 products)
2. ✅ `add_forestry_products.py` (11 products)
3. ✅ `add_rcoc_welding_products.py` (exists, ready to run)

---

## 🚨 THE COMMITMENT

**From now on:**

**NO supplier quote leaves your inbox without:**
1. ✅ SKUs captured
2. ✅ Script created
3. ✅ Products added to NEXUS
4. ✅ Verified in Airtable

**This is non-negotiable. Your future self will thank you.**

---

*Productivity Rule #1: Capture ALL product data IMMEDIATELY. Never search for the same SKU twice.* 🎯
