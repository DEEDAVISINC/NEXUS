# 📊 GPSS SUPPLIER MINING - SIMPLE TABLE SETUP

## 🎯 **DYNAMIC MINING APPROACH:**

**You DON'T pre-define products to mine for.**
**Each RFQ tells the system what to find.**
**System adapts to any product category automatically.**

---

## **TABLE 1: GPSS Suppliers** (Your supplier database)

### **Fields to Create:**

| Field Name | Field Type | Options/Notes |
|------------|-----------|---------------|
| **Supplier ID** | Autonumber | PRIMARY FIELD |
| **Company Name** | Single line text | Required |
| **Website** | URL | |
| **Primary Contact Email** | Email | |
| **Primary Contact Phone** | Phone number | |
| **Product Keywords** | Long text | Open-ended (AI auto-fills from RFQs) |
| **Net 30 Available** | Checkbox | |
| **Net 45 Available** | Checkbox | |
| **Business Status** | Single select | Options: `Active`, `Prospective`, `Inactive`, `Blacklisted` |
| **Typical Margin (%)** | Number | Your avg markup with them |
| **Overall Rating** | Rating | 1-5 stars |
| **Discovery Method** | Single select | Options: `AI Mining`, `Google Search`, `Manual Entry`, `Referral`, `GSA Mining`, `Cold Outreach` |
| **Discovery Date** | Date | When added |
| **Discovered By** | Single select | Options: `AI Mining`, `Manual Entry`, `Dee Davis` |
| **Last Order Date** | Date | Most recent order |

**Total: 14 fields**

---

## **TABLE 2: GPSS Supplier Quotes** (Quote tracking)

### **Fields to Create:**

| Field Name | Field Type | Options/Notes |
|------------|-----------|---------------|
| **Quote Request ID** | Autonumber | PRIMARY FIELD |
| **Opportunity** | Link to another record | Link to "Opportunities" table |
| **Supplier** | Link to another record | Link to "GPSS Suppliers" table |
| **Product/Service Requested** | Long text | What you asked them to quote (AI fills) |
| **Quantity** | Single line text | How many |
| **Supplier Quote Amount** | Currency | Their price |
| **Request Sent Date** | Date & time | When requested |
| **Quote Received Date** | Date & time | When they responded |
| **Request Status** | Single select | Options: `Draft`, `Sent`, `Received`, `Declined`, `No Response`, `Expired` |
| **Our Markup (%)** | Number | Your markup % |
| **Quoted Lead Time (Days)** | Number | Their delivery time |
| **Selected for Quote** | Checkbox | Used this quote? |
| **Contract Awarded** | Checkbox | Won contract? |
| **AI Recommendation** | Long text | AI analysis |

**Total: 14 fields**

---

## **TABLE 3: GPSS Supplier Orders** (Order management)

### **Fields to Create:**

| Field Name | Field Type | Options/Notes |
|------------|-----------|---------------|
| **Order ID** | Autonumber | PRIMARY FIELD |
| **PO Number** | Single line text | Your PO # |
| **Opportunity** | Link to another record | Link to "Opportunities" table |
| **Supplier** | Link to another record | Link to "GPSS Suppliers" table |
| **Product Details** | Long text | What you ordered |
| **Order Date** | Date | When ordered |
| **Order Amount** | Currency | What you paid |
| **Customer Invoice Amount** | Currency | What customer pays |
| **Order Status** | Single select | Options: `Ordered`, `Confirmed`, `Shipped`, `Delivered`, `Completed`, `Cancelled` |
| **Expected Delivery Date** | Date | Expected |
| **Actual Delivery Date** | Date | Actual |
| **Payment Method** | Single select | Options: `Net 30`, `Net 45`, `Net 60`, `Factor Direct Payment`, `Check`, `ACH`, `Credit Card` |
| **Factoring Used** | Checkbox | Used factoring? |
| **Quality Rating** | Rating | 1-5 stars for this order |

**Total: 14 fields**

---

## 🔗 **TABLE RELATIONSHIPS:**

### **Link Fields Setup:**

**In "GPSS Supplier Quotes" table:**
- Field "Opportunity" → Link to "Opportunities" table
- Field "Supplier" → Link to "GPSS Suppliers" table

**In "GPSS Supplier Orders" table:**
- Field "Opportunity" → Link to "Opportunities" table
- Field "Supplier" → Link to "GPSS Suppliers" table

---

## 🤖 **HOW DYNAMIC MINING WORKS:**

### **Example: Paper Pallets RFQ**

```
1. RFQ: "Need 10 pallets of copy paper..."
   ↓
2. AI extracts: "copy paper, pallets, office supplies"
   ↓
3. System searches suppliers with keywords: "paper", "office"
   ↓
4. If not enough found → AI mines web for "copy paper wholesale Net 30"
   ↓
5. AI finds new suppliers, adds them with keywords "paper, copy paper, office supplies"
   ↓
6. Next time paper RFQ comes in → Already have suppliers!
```

### **Example: Random Contract (Traffic Cones)**

```
1. RFQ: "Need 100 traffic cones..."
   ↓
2. AI extracts: "traffic cones, safety equipment"
   ↓
3. System searches: No suppliers with "traffic" or "safety" keywords
   ↓
4. AI mines web: "traffic cones wholesale bulk"
   ↓
5. Finds: 5 safety equipment suppliers
   ↓
6. Adds them with keywords: "traffic cones, safety, PPE, equipment"
   ↓
7. Now you have suppliers for safety equipment category!
```

---

## 💡 **KEY INSIGHT:**

**Product Keywords field = Magic**

- AI auto-fills from each RFQ
- Keywords accumulate over time
- System learns what each supplier carries
- No need to pre-define categories
- Works for ANY product

**Example Supplier Record:**

```
Company: ABC Wholesale Supply
Product Keywords: "paper, copy paper, printer paper, toner, office supplies, 
                   staplers, pens, folders, binders, desk accessories, 
                   mouse pads, keyboards, USB drives, monitors"

This supplier can now match RFQs for ANY of those keywords!
```

---

## ✅ **SETUP CHECKLIST:**

### **Step 1: Create Tables**
- [ ] Create "GPSS Suppliers" table
- [ ] Create "GPSS Supplier Quotes" table  
- [ ] Create "GPSS Supplier Orders" table

### **Step 2: Add Fields (14 fields per table)**
- [ ] Add all 14 fields to Suppliers table
- [ ] Add all 14 fields to Supplier Quotes table
- [ ] Add all 14 fields to Supplier Orders table

### **Step 3: Set Up Relationships**
- [ ] Link "Supplier Quotes" → "Opportunities"
- [ ] Link "Supplier Quotes" → "Suppliers"
- [ ] Link "Supplier Orders" → "Opportunities"
- [ ] Link "Supplier Orders" → "Suppliers"

### **Step 4: Test**
- [ ] Add 1 test supplier manually
- [ ] Verify links work
- [ ] Ready for automation!

---

## 🚀 **WHAT HAPPENS NEXT:**

### **When you process your first RFQ:**

1. AI reads the RFQ
2. Extracts product info (dynamic)
3. Searches your suppliers by keywords
4. Mines web if needed (dynamic)
5. Finds 5-10 suppliers
6. Generates quote requests
7. Tracks responses
8. You pick best quote
9. Win contract

### **Your database grows organically:**

- RFQ #1: Office supplies → 5 new suppliers
- RFQ #2: IT equipment → 3 new suppliers
- RFQ #3: Safety gear → 4 new suppliers
- RFQ #4: Paper again → Already have 5 suppliers!
- RFQ #5: Furniture → 6 new suppliers

**After 10 RFQs: 20-30 suppliers across multiple categories**
**After 50 RFQs: 100+ suppliers, can quote anything instantly**

---

## 🎯 **COMPETITIVE ADVANTAGE:**

**Old way:**
- Specialize in 1-2 product categories
- Limit yourself to what you know
- Pass on "random" opportunities
- Manual supplier research

**New way with dynamic mining:**
- Quote ANY product under $500k
- System finds suppliers automatically
- Grab ALL low-hanging fruit
- Database grows with every RFQ
- Eventually can quote 90% of contracts instantly

---

## 📝 **REMINDER:**

**Total fields to create: 42 fields (14 per table × 3 tables)**

**Time needed: 45-60 minutes**

**Then you're ready to test with real RFQs!**

---

**Ready to create these tables?** 🎯
