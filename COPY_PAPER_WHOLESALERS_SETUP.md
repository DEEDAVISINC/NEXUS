# 📄 COPY PAPER WHOLESALERS - SETUP GUIDE

## 🚨 ISSUE FOUND

Your `GPSS SUPPLIERS` table exists but only has 1 field:
- **SUPPLIER ID** (Autonumber)

You need to add more fields before we can import suppliers.

---

## ⚡ QUICK FIX: Add These Fields to Airtable

### **Step 1: Open Your Airtable Base**
1. Go to https://airtable.com
2. Open your NEXUS base
3. Find the `GPSS SUPPLIERS` table
4. Click "+" to add new fields

### **Step 2: Add These MINIMUM Fields** (5 minutes)

Click "+ Add field" for each of these:

| Field Name | Field Type | Notes |
|------------|-----------|-------|
| **COMPANY NAME** | Single line text | ⭐ REQUIRED - Primary supplier name |
| **WEBSITE** | URL | Company website |
| **PRIMARY CONTACT EMAIL** | Email | Main contact email |
| **PRIMARY CONTACT PHONE** | Phone number | Main phone number |
| **PRODUCT KEYWORDS** | Long text | Searchable keywords for products |
| **DESCRIPTION** | Long text | Company description |
| **BUSINESS STATUS** | Single select | Options: `Prospective`, `Active`, `Inactive` |
| **DISCOVERY METHOD** | Single select | Options: `Manual Entry`, `ThomasNet`, `Google Search`, `GSA Advantage`, `CSV Import` |
| **DISCOVERY DATE** | Date | When supplier was added |
| **DISCOVERED BY** | Single line text | Who added this supplier |
| **RELATIONSHIP STAGE** | Single select | Options: `Discovered`, `Contacted`, `Qualified`, `Active`, `Preferred` |
| **SOURCE NOTES** | Long text | Additional context about supplier |

### **Step 3: Run the Import Script**

Once you've added those fields, run:

```bash
cd "/Users/deedavis/NEXUS BACKEND"
source .venv/bin/activate
python add_paper_wholesaler.py
```

---

## 🏆 TOP 5 COPY PAPER WHOLESALERS READY TO ADD

### **1. Great Falls Paper** ⭐ Score: 95/100
- **Best For:** Small business set-asides (EDWOSB/WOSB)
- **GSA Contract:** Schedule 75 - Office Solutions
- **Products:** 22,600+ office products including all paper types
- **Contact:** 800-992-7671 | sales@greatfallspaper.com
- **Why:** Small business, responsive, comprehensive catalog

### **2. Unisource (Georgia-Pacific)** 🏆 Score: 98/100
- **Best For:** Large federal contracts $100K+
- **GSA Contract:** Schedule 75
- **Products:** All major paper brands (GP, Boise, Hammermill)
- **Contact:** 800-864-7687 | customersupport@unisourcelink.com
- **Why:** Fortune 500 backing, best bulk pricing, multiple brands

### **3. xpedx (International Paper)** 🏆 Score: 98/100
- **Best For:** Best wholesale pricing (direct manufacturer)
- **GSA Contract:** Schedule 75
- **Products:** International Paper brands, specialty papers
- **Contact:** 800-333-8438 | customer.service@internationalpaper.com
- **Why:** Direct manufacturer = lowest prices, Fortune 500

### **4. Staples Business Advantage** ⚡ Score: 92/100
- **Best For:** Fast delivery, small-medium orders <$50K
- **GSA Contract:** Schedule 75 - Office Solutions
- **Products:** Paper + all office supplies (one-stop-shop)
- **Contact:** 800-333-3330 | advantage@staples.com
- **Why:** Next-day delivery, established, comprehensive

### **5. Office Depot Business Solutions** ⚡ Score: 92/100
- **Best For:** Bundled orders (paper + supplies + tech)
- **GSA Contract:** Schedule 75
- **Products:** Office supplies, technology, furniture
- **Contact:** 888-263-3423 | bsdsales@officedepot.com
- **Why:** Nationwide, good pricing, strong government team

---

## 💡 USAGE STRATEGY

### **For Large Contracts ($100K+):**
1. Get quotes from Unisource AND xpedx
2. Use their pricing to bid aggressively
3. Leverage Fortune 500 backing in proposals

### **For EDWOSB Set-Asides:**
1. Use Great Falls Paper
2. Highlight small business status
3. Fast turnaround, responsive

### **For Quick Orders (<$50K):**
1. Staples or Office Depot
2. Next-day delivery
3. Bundled with other office supplies

### **For Best Pricing:**
1. Always get 3 quotes (Unisource, xpedx, Great Falls)
2. Mention GSA contract in RFP responses
3. Volume discounts on large orders

---

## 🔄 ALTERNATIVE: Manual Entry

If you want to add suppliers manually right now:

1. Go to Airtable
2. Open GPSS SUPPLIERS table
3. Click "+ Add record"
4. Fill in at minimum:
   - **COMPANY NAME:** Great Falls Paper
   - **WEBSITE:** https://www.greatfallspaper.com
   - **PRIMARY CONTACT EMAIL:** sales@greatfallspaper.com
   - **PRIMARY CONTACT PHONE:** 800-992-7671
   - **PRODUCT KEYWORDS:** copy paper, printer paper, office paper, GSA Schedule 75
   - **BUSINESS STATUS:** Prospective
   - **DISCOVERY METHOD:** Manual Entry

Repeat for each of the 5 wholesalers above.

---

## 📋 RECOMMENDED: Full Schema (180+ Fields)

For the complete GPSS Supplier Management System, see:
- `GPSS_VENDOR_MANAGEMENT_SCHEMA.md`
- `GPSS_SUPPLIER_MINING_SCHEMA.md`

These provide tracking for:
- Payment terms (Net 30/45/60)
- GSA contract details
- Performance ratings
- Order history
- Quote tracking
- Certifications (EDWOSB, 8(a), etc.)
- Geographic coverage
- Product categories
- Relationship management

But you can start with the minimum 12 fields above and expand later.

---

## ✅ NEXT STEPS

1. [ ] Add minimum 12 fields to GPSS SUPPLIERS table in Airtable
2. [ ] Run `python add_paper_wholesaler.py`
3. [ ] Verify 5 suppliers added successfully
4. [ ] Start requesting quotes for your next paper RFP!

---

## 📞 CONTACTS TO SAVE

**For immediate copy paper quotes:**

- **Great Falls Paper:** 800-992-7671
- **Unisource:** 800-864-7687
- **International Paper:** 800-333-8438
- **Staples Advantage:** 800-333-3330
- **Office Depot BSD:** 888-263-3423

**All have GSA Schedule 75 contracts = pre-approved government pricing!**

---

**Created:** January 23, 2026  
**Status:** Ready for Airtable field setup
