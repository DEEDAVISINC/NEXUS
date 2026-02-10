# NEXUS PRODUCT CATALOG - SETUP GUIDE
**HOW TO ADD ALL RCOC PRODUCTS TO AIRTABLE**

**Date:** January 29, 2026  
**Products to Add:** 9 items from 3 RCOC bids  
**Total Value:** $126,895

---

## 📁 FILES CREATED FOR YOU

### **1. RCOC_MASTER_PRODUCT_LIST_FOR_NEXUS.md** ⭐ MAIN FILE
- **What it is:** Complete details for every product
- **Use for:** Full product specifications and notes
- **Contains:** 
  - Full product descriptions
  - All manufacturer info
  - All supplier SKUs (Zoro + Grainger)
  - Detailed pricing comparison
  - Complete specs for each item
  - Categories and tags
  - Usage history

### **2. RCOC_PRODUCTS_AIRTABLE_IMPORT.csv** 📊 IMPORT FILE
- **What it is:** CSV file ready for direct import to Airtable
- **Use for:** Bulk import to NEXUS (fastest method!)
- **Contains:** All 9 products in CSV format with all fields

### **3. RCOC_QUICK_REFERENCE_SKU_LIST.md** 🔍 QUICK LOOKUP
- **What it is:** Fast SKU lookup table
- **Use for:** Quick reference when ordering or quoting
- **Contains:** Simple tables with just SKUs and prices

---

## 🎯 HOW TO ADD TO NEXUS (3 OPTIONS)

### **OPTION 1: CSV IMPORT (FASTEST!)** ⭐ RECOMMENDED

**Step 1:** Open your NEXUS Airtable base
**Step 2:** Go to "Product Catalog" table (or create it)
**Step 3:** Click "+" button → "Import data" → "CSV file"
**Step 4:** Upload: `RCOC_PRODUCTS_AIRTABLE_IMPORT.csv`
**Step 5:** Map fields (Airtable will auto-match most)
**Step 6:** Click "Import"

**Done!** All 9 products imported in seconds! ✅

---

### **OPTION 2: Manual Entry (Most Control)**

**Step 1:** Open `RCOC_MASTER_PRODUCT_LIST_FOR_NEXUS.md`
**Step 2:** For each product, create a new record in Airtable
**Step 3:** Copy/paste fields from the document
**Step 4:** Add any custom fields you need

**Time:** 15-20 minutes for all 9 products

---

### **OPTION 3: Copy/Paste from Quick Reference**

**Step 1:** Open `RCOC_QUICK_REFERENCE_SKU_LIST.md`
**Step 2:** Copy the quick lookup table
**Step 3:** Paste into Airtable (basic fields only)
**Step 4:** Enhance with details from master list as needed

**Time:** 5-10 minutes (minimal detail)

---

## 📋 AIRTABLE TABLE STRUCTURE

### **Table Name:** Product Catalog

### **Recommended Fields:**

| Field Name | Type | Description |
|------------|------|-------------|
| Product Description | Long text | Full product name and specs |
| Manufacturer | Single line text | Company name |
| Manufacturer Part # | Single line text | Mfr part number |
| Product Series | Single line text | Optional (Scott, WYPALL, etc.) |
| Category | Single select | Janitorial, Industrial, Automotive |
| Subcategory | Single select | Paper Products, Wipers, etc. |
| UOM | Single line text | Pack, Each, Carton, etc. |
| Preferred Supplier | Single select | Zoro or Grainger |
| Preferred Supplier SKU | Single line text | Item # from preferred supplier |
| Preferred Unit Cost | Currency | Price from preferred supplier |
| Alternative Supplier | Single select | Backup supplier |
| Alternative Supplier SKU | Single line text | Item # from alternative |
| Alternative Unit Cost | Currency | Price from alternative |
| Savings % | Percent | How much cheaper preferred is |
| Last Quote Date | Date | When you got this pricing |
| Contract Used In | Long text | Which bids used this product |
| Qty Last Ordered | Number | How many in last order |
| Total Last Cost | Currency | Total of last order |
| Notes | Long text | Special notes, savings info |
| Status | Single select | Active, Discontinued, etc. |
| Zoro Link | URL | Link to Zoro product page |
| Grainger Link | URL | Link to Grainger product page |

---

## 🎯 QUICK START (10 MINUTES)

**If you want to get started NOW:**

1. **Open Airtable** (your NEXUS base)
2. **Create table:** "Product Catalog"
3. **Add these 5 essential fields:**
   - Product Description (text)
   - Manufacturer Part # (text)
   - Supplier (select: Zoro, Grainger)
   - Supplier SKU (text)
   - Unit Price (currency)
4. **Import CSV:** `RCOC_PRODUCTS_AIRTABLE_IMPORT.csv`
5. **Done!** Enhance fields later as needed

**That's it! You can now search products in NEXUS!** ✅

---

## 🔍 HOW TO USE PRODUCT CATALOG

### **Scenario 1: New Similar RFQ**
**Example:** Detroit DPW wants toilet paper

1. Open NEXUS Product Catalog
2. Search: "toilet paper"
3. Find: KC 04460 at $96.29 from Zoro (Item G4519551)
4. Submit quote immediately!

**Time saved:** 1-2 hours of supplier research!

---

### **Scenario 2: RCOC Reorders (Next Year)**
**Example:** RCOC releases IFB 7732 again in 2027

1. Open NEXUS Product Catalog
2. Filter: "Contract = RCOC IFB 7732"
3. See all 5 items with current pricing
4. Check if pricing still valid
5. Submit updated quote

**Time saved:** 3-4 hours of pricing and setup!

---

### **Scenario 3: Supplier Comparison**
**Example:** Should I check Zoro or Grainger first?

1. Open NEXUS Product Catalog
2. Filter by product category
3. View "Savings %" column
4. See that Zoro wins 83% of the time
5. Check Zoro first on all future bids!

**Insight:** Data-driven supplier decisions!

---

### **Scenario 4: Quick Quote for Client**
**Example:** New client needs industrial wipers

1. Search NEXUS: "wipers"
2. Find KC 35431 at $166.99 (Zoro G2856357)
3. Know it's 29% cheaper than Grainger
4. Quote confidently with good margin

**Time saved:** 30-60 minutes per quote!

---

## 📊 PRODUCTS BY CATEGORY

### **Janitorial Supplies (5 products):**
- Dinner Napkins (Grainger)
- Hot Cups 8oz (Zoro)
- Toilet Paper (Zoro)
- Facial Tissue (Zoro)
- Cloth Rags (Zoro)

### **Industrial Supplies (1 product):**
- Industrial Wipers Blue (Zoro)

### **Automotive (3 products):**
- Wiper Blade 18" (Zoro)
- Wiper Blade 22" (Zoro)
- Wiper Blade 20" (Zoro)

---

## 💡 PRO TIPS

### **1. Add Tags for Easy Search**
Create a "Tags" field with multiple select:
- `Oakland County`, `RCOC`, `Government`
- `Paper Products`, `Cleaning`, `Maintenance`
- `Zoro Winner`, `Grainger Winner`
- `High Savings` (20%+), `Medium Savings` (10-20%), `Low Savings` (<10%)

### **2. Link to Contracts Table**
If you have a "Contracts" table in NEXUS:
- Link each product to the contract(s) it was used in
- Track product usage across multiple clients
- See total revenue per product

### **3. Set Up Views**
Create filtered views:
- "Zoro Products" (8 items)
- "Grainger Products" (1 item)
- "High Savings Items" (>20% savings)
- "Janitorial Supplies"
- "Active Products"

### **4. Add Reorder Triggers**
Create a "Reorder Date" field:
- Set reminders for contract renewals
- Check pricing updates annually
- Track when to re-quote

### **5. Track Price Changes**
Add "Price History" field:
- Log when prices change
- Track inflation/deflation
- Adjust future bids accordingly

---

## 📈 FUTURE EXPANSION

**As you win more bids, keep adding products:**

### **From Each New Contract:**
1. Add all products to catalog
2. Include all supplier options
3. Note which supplier was cheapest
4. Link to the contract
5. Update categories/tags

### **Benefits Over Time:**
- ✅ Hundreds of products cataloged
- ✅ Instant pricing for repeat items
- ✅ Data on best suppliers per category
- ✅ Fast quote generation
- ✅ Competitive advantage

**Goal:** 100+ products in catalog within 6 months!

---

## 🎯 IMMEDIATE NEXT STEPS

**To get RCOC products into NEXUS today:**

1. ✅ **Open Airtable** (NEXUS base)
2. ✅ **Create "Product Catalog" table**
3. ✅ **Import CSV:** `RCOC_PRODUCTS_AIRTABLE_IMPORT.csv`
4. ✅ **Add custom fields** (optional - enhance later)
5. ✅ **Test search** - Try finding "toilet paper"
6. ✅ **Bookmark for future use**

**Time:** 10 minutes  
**Value:** Instant access to $127K of product data!

---

## 📞 WHAT YOU HAVE NOW

**3 Complete Files:**
1. ⭐ Master Product List (full details)
2. 📊 CSV Import File (ready to upload)
3. 🔍 Quick Reference (fast lookup)

**All Ready For:**
- ✅ NEXUS Airtable import
- ✅ Future quote generation
- ✅ Supplier comparison
- ✅ Contract renewals
- ✅ Similar RFQs from other clients

---

## 💰 VALUE OF PRODUCT CATALOG

**What This Saves You:**

| Task | Without Catalog | With Catalog | Time Saved |
|------|-----------------|--------------|------------|
| Similar quote | 2-3 hours | 15 minutes | **2.5 hrs** |
| Supplier research | 1-2 hours | 5 minutes | **1.5 hrs** |
| SKU lookup | 30 min | 1 minute | **29 min** |
| Price comparison | 1 hour | 2 minutes | **58 min** |
| Contract renewal | 3-4 hours | 30 minutes | **3 hrs** |

**Per similar bid:** Save 4-8 hours!  
**Value per year:** Hundreds of hours saved!

---

## 🚀 READY TO GO!

**You now have everything to:**
- ✅ Add all RCOC products to NEXUS
- ✅ Search products instantly
- ✅ Quote future bids faster
- ✅ Compare suppliers easily
- ✅ Track pricing over time

**Start with the CSV import - 10 minutes and you're done!** 💪

---

**STATUS:** PRODUCT CATALOG DATA READY ✅  
**PRODUCTS:** 9 items from 3 RCOC contracts  
**VALUE:** $126,895  
**TIME TO IMPORT:** 10 minutes  
**FILES LOCATION:** `photos_and_videos/` folder

---

*NEXUS Product Catalog Setup Guide - January 29, 2026*  
*Everything ready for easy Airtable import!* 🎯
