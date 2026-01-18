# GPSS SUPPLIER MINING SYSTEM - AIRTABLE SCHEMA

## 🎯 **PURPOSE:**
Automate supplier discovery, quote management, and order tracking for government product contracts.

---

## 📋 **TABLE 1: GPSS SUPPLIERS**

### **Purpose:** Your supplier database (companies you BUY from to fulfill contracts)

### **Fields to Add:**

| Field Name | Field Type | Options/Configuration |
|------------|-----------|----------------------|
| **Supplier ID** | Autonumber | PRIMARY FIELD - Auto-generated unique ID |
| **Company Name** | Single line text | e.g., "SP Richards", "Ingram Micro" |
| **Website** | URL | Company website |
| **Company Type** | Single select | Options: `Manufacturer`, `Distributor`, `Wholesaler`, `Reseller` |
| **Business Status** | Single select | Options: `Active`, `Prospective`, `Inactive`, `Blacklisted` (colors: green, yellow, gray, red) |
| **Primary Contact Name** | Single line text | Main contact person |
| **Primary Contact Email** | Email | Main contact email |
| **Primary Contact Phone** | Phone number | Main contact phone |
| **Account Manager Name** | Single line text | Your dedicated account rep |
| **Account Manager Email** | Email | Account rep email |
| **Account Manager Phone** | Phone number | Account rep phone |

### **Product Information:**

| Field Name | Field Type | Options/Configuration |
|------------|-----------|----------------------|
| **Product Categories** | Multiple select | Options: `Office Supplies`, `Technology`, `Furniture`, `Janitorial`, `Safety/PPE`, `Medical`, `Educational`, `Vehicles`, `Food Service`, `Maintenance`, `Construction`, `Textiles`, `Industrial`, `Telecommunications`, `Laboratory`, `Printing`, `Other` |
| **Product Keywords** | Long text | Comma-separated keywords for search matching |
| **NAICS Codes Served** | Long text | NAICS codes this supplier serves |
| **PSC Codes Served** | Long text | PSC codes (federal product categories) |
| **Brands Carried** | Long text | Brands/manufacturers they distribute |
| **Product Catalog** | Attachment | Upload their product catalog (PDF/Excel) |

### **Terms & Capabilities:**

| Field Name | Field Type | Options/Configuration |
|------------|-----------|----------------------|
| **Net 30 Available** | Checkbox | Can you get Net 30 terms? |
| **Net 45 Available** | Checkbox | Can you get Net 45 terms? |
| **Net 60 Available** | Checkbox | Can you get Net 60 terms? |
| **Net Terms Notes** | Long text | Special notes about payment terms |
| **Credit Status** | Single select | Options: `Not Applied`, `Applied`, `Approved`, `Denied` |
| **Credit Limit** | Currency | Your approved credit limit |
| **Credit Approved Date** | Date | When credit was approved |
| **Minimum Order** | Currency | Minimum order amount required |
| **Drop Ship Available** | Checkbox | Can they ship direct to customer? |
| **Direct Ship Available** | Checkbox | Can they ship to customer from warehouse? |
| **Typical Lead Time (Days)** | Number | Normal delivery timeframe |
| **Expedited Available** | Checkbox | Can they rush orders? |
| **Expedited Lead Time (Days)** | Number | Rush delivery timeframe |

### **Pricing & Margins:**

| Field Name | Field Type | Options/Configuration |
|------------|-----------|----------------------|
| **Typical Margin (%)** | Number | Your average markup with this supplier |
| **Volume Discounts Available** | Checkbox | Do they offer volume pricing? |
| **Government Discount (%)** | Number | Special discount for gov't contracts |
| **EDWOSB Discount (%)** | Number | Special discount for EDWOSB certification |
| **Pricing Sheet** | Attachment | Upload their pricing sheet |
| **Last Price Update** | Date | When you last updated pricing |

### **Qualifications:**

| Field Name | Field Type | Options/Configuration |
|------------|-----------|----------------------|
| **GSA Contract Holder** | Checkbox | Do they have GSA schedule? |
| **GSA Schedule Number** | Single line text | Their GSA contract number |
| **Government Supplier** | Checkbox | Do they sell to government? |
| **Years in Business** | Number | How long they've been operating |
| **BBB Rating** | Single select | Options: `A+`, `A`, `A-`, `B+`, `B`, `B-`, `C+`, `C`, `Not Rated` |
| **Certifications** | Multiple select | Options: `ISO 9001`, `Women-Owned`, `Minority-Owned`, `8(a)`, `HUBZone`, `SDVOSB`, `Other` |
| **Insurance Coverage** | Currency | Their liability coverage amount |
| **Bonding Capacity** | Currency | Their bonding capacity |

### **Performance Tracking:**

| Field Name | Field Type | Options/Configuration |
|------------|-----------|----------------------|
| **Total Orders Placed** | Rollup | Count from "Supplier Orders" table |
| **Total Value Purchased** | Rollup | Sum of order amounts from "Supplier Orders" |
| **Average Order Value** | Formula | `{Total Value Purchased} / {Total Orders Placed}` |
| **On-Time Delivery (%)** | Number | Percentage of on-time deliveries |
| **Quality Rating** | Rating | 1-5 stars for product quality |
| **Responsiveness Rating** | Rating | 1-5 stars for communication |
| **Price Competitiveness** | Rating | 1-5 stars for pricing |
| **Overall Rating** | Formula | Average of above ratings |
| **Last Order Date** | Rollup | Most recent order from "Supplier Orders" |
| **Orders This Year** | Rollup | Count of orders this year |
| **Defect Rate (%)** | Number | Percentage of defective products |

### **Financial:**

| Field Name | Field Type | Options/Configuration |
|------------|-----------|----------------------|
| **Payment Method** | Single select | Options: `Check`, `ACH`, `Wire`, `Credit Card` |
| **Bank Account Info** | Long text | Bank details for factoring directed payments |
| **W-9 on File** | Checkbox | Do you have their W-9? |
| **W-9 Upload** | Attachment | Upload their W-9 form |
| **Tax ID** | Single line text | Their EIN/Tax ID |
| **Factoring Approved** | Checkbox | Can Bankers/Porter pay them directly? |
| **Factoring Notes** | Long text | Notes for factor payments |

### **Discovery & Source:**

| Field Name | Field Type | Options/Configuration |
|------------|-----------|----------------------|
| **Discovery Method** | Single select | Options: `GSA Mining`, `Google Search`, `ThomasNet`, `Referral`, `Cold Outreach`, `Trade Show`, `Manual Research` |
| **Discovery Date** | Date | When you found this supplier |
| **Discovered By** | Single select | Options: `AI Mining`, `Manual Entry`, `Dee Davis`, `Team Member` |
| **Source URL** | URL | Where you found them (if online) |
| **Mining Confidence Score** | Number | AI confidence this is good supplier (0-100) |

### **Relationship Management:**

| Field Name | Field Type | Options/Configuration |
|------------|-----------|----------------------|
| **Relationship Stage** | Single select | Options: `Discovered`, `Contacted`, `In Discussions`, `Applied for Credit`, `Approved`, `Active`, `Preferred`, `Inactive` (colors: gray, yellow, orange, blue, green, purple, red) |
| **First Contact Date** | Date | When you first reached out |
| **Application Submitted Date** | Date | When you applied for account |
| **First Order Date** | Date | Your first order with them |
| **Last Contact Date** | Date | Most recent communication |
| **Next Follow-up Date** | Date | When to follow up next |
| **Follow-up Notes** | Long text | Notes for next contact |

### **AI & Automation:**

| Field Name | Field Type | Options/Configuration |
|------------|-----------|----------------------|
| **AI Match Score** | Number | How well AI thinks they match needs (0-100) |
| **Auto-Quote Enabled** | Checkbox | Can AI automatically request quotes? |
| **Quote Request Email Template** | Long text | Custom email template for this supplier |
| **Typical Response Time (Hours)** | Number | How fast they usually respond |
| **Preferred Contact Method** | Single select | Options: `Email`, `Phone`, `Portal`, `Fax` |

### **Links:**

| Field Name | Field Type | Options/Configuration |
|------------|-----------|----------------------|
| **Opportunities Quoted** | Link to another record | Link to "Opportunities" table |
| **Supplier Quotes** | Link to another record | Link to "Supplier Quotes" table |
| **Orders Placed** | Link to another record | Link to "Supplier Orders" table |

### **Notes & Tags:**

| Field Name | Field Type | Options/Configuration |
|------------|-----------|----------------------|
| **Internal Notes** | Long text | Private notes about this supplier |
| **Strengths** | Long text | What they're good at |
| **Weaknesses** | Long text | What to watch out for |
| **Special Instructions** | Long text | Special handling requirements |
| **Tags** | Multiple select | Options: `Preferred`, `Fast Response`, `Best Pricing`, `Reliable`, `Problematic`, `Drop Ship Expert`, `Government Specialist`, `EDWOSB Friendly`, `Volume Discounter`, `Emergency Contact` |

### **Metadata:**

| Field Name | Field Type | Options/Configuration |
|------------|-----------|----------------------|
| **Created Date** | Created time | Auto-generated |
| **Last Modified** | Last modified time | Auto-generated |
| **Created By** | Single line text | Who added this supplier |

---

## 📋 **TABLE 2: GPSS SUPPLIER QUOTES**

### **Purpose:** Track quote requests TO suppliers and responses FROM suppliers

### **Fields to Add:**

| Field Name | Field Type | Options/Configuration |
|------------|-----------|----------------------|
| **Quote Request ID** | Autonumber | PRIMARY FIELD |
| **Opportunity** | Link to another record | Link to "Opportunities" table |
| **Supplier** | Link to another record | Link to "Suppliers" table |
| **Product/Service Requested** | Long text | What you're asking for |
| **Quantity** | Number | How many units |
| **Specifications** | Long text | Technical specs/requirements |
| **Delivery Location** | Single line text | Where to ship |
| **Required Delivery Date** | Date | Deadline for delivery |

### **Request Tracking:**

| Field Name | Field Type | Options/Configuration |
|------------|-----------|----------------------|
| **Request Sent Date** | Date & time | When quote request was sent |
| **Request Method** | Single select | Options: `Email`, `Phone`, `Portal`, `Auto-Generated` |
| **Request Email** | Long text | Copy of email sent |
| **Request Status** | Single select | Options: `Draft`, `Sent`, `Received`, `Declined`, `No Response`, `Expired` (colors: gray, blue, green, red, orange, yellow) |

### **Supplier Response:**

| Field Name | Field Type | Options/Configuration |
|------------|-----------|----------------------|
| **Quote Received Date** | Date & time | When supplier responded |
| **Response Time (Hours)** | Formula | `DATETIME_DIFF({Quote Received Date}, {Request Sent Date}, 'hours')` |
| **Supplier Quote Amount** | Currency | Their quoted price |
| **Supplier Quote Details** | Long text | Additional details from supplier |
| **Supplier Quote Attachment** | Attachment | Upload their quote PDF |
| **Quoted Lead Time (Days)** | Number | Delivery time they quoted |
| **Quote Valid Until** | Date | Expiration date of quote |

### **Our Pricing Calculations:**

| Field Name | Field Type | Options/Configuration |
|------------|-----------|----------------------|
| **Our Markup (%)** | Number | Your target markup percentage |
| **Our Proposed Price** | Formula | `{Supplier Quote Amount} * (1 + {Our Markup (%)} / 100)` |
| **Gross Margin ($)** | Formula | `{Our Proposed Price} - {Supplier Quote Amount}` |
| **Gross Margin (%)** | Formula | `({Gross Margin ($)} / {Our Proposed Price}) * 100` |
| **Factoring Fee (%)** | Number | Default 3% for government invoices |
| **Factoring Fee ($)** | Formula | `{Our Proposed Price} * ({Factoring Fee (%)} / 100)` |
| **Net Profit After Factoring ($)** | Formula | `{Gross Margin ($)} - {Factoring Fee ($)}` |
| **Net Profit Margin (%)** | Formula | `({Net Profit After Factoring ($)} / {Our Proposed Price}) * 100` |

### **Selection & Outcome:**

| Field Name | Field Type | Options/Configuration |
|------------|-----------|----------------------|
| **Selected for Quote** | Checkbox | Did we use this for customer quote? |
| **Customer Quote Submitted** | Checkbox | Did we submit quote to customer? |
| **Contract Awarded** | Checkbox | Did we win the contract? |
| **Order Placed** | Checkbox | Did we place order with supplier? |
| **Won/Lost Reason** | Long text | Why we won or lost |

### **AI Analysis:**

| Field Name | Field Type | Options/Configuration |
|------------|-----------|----------------------|
| **AI Recommendation** | Long text | AI analysis of this quote |
| **Competitive Ranking** | Single select | Options: `Best Price`, `Competitive`, `Average`, `High`, `Too Expensive` |
| **Risk Assessment** | Single select | Options: `Low`, `Medium`, `High` |

### **Metadata:**

| Field Name | Field Type | Options/Configuration |
|------------|-----------|----------------------|
| **Created Date** | Created time | Auto-generated |
| **Notes** | Long text | Additional notes |

---

## 📋 **TABLE 3: GPSS SUPPLIER ORDERS**

### **Purpose:** Track actual orders placed with suppliers

### **Fields to Add:**

| Field Name | Field Type | Options/Configuration |
|------------|-----------|----------------------|
| **Order ID** | Autonumber | PRIMARY FIELD |
| **PO Number** | Single line text | Your purchase order number |
| **Opportunity** | Link to another record | Link to "Opportunities" |
| **Supplier** | Link to another record | Link to "Suppliers" |
| **Supplier Quote** | Link to another record | Link to "Supplier Quotes" |
| **Order Date** | Date | When order was placed |
| **Order Amount** | Currency | Total order value |
| **Order Status** | Single select | Options: `Ordered`, `Confirmed`, `In Production`, `Shipped`, `Delivered`, `Invoiced`, `Paid`, `Completed`, `Cancelled` (colors) |

### **Product Details:**

| Field Name | Field Type | Options/Configuration |
|------------|-----------|----------------------|
| **Product Details** | Long text | What was ordered |
| **Quantity** | Number | Number of units |
| **Unit Price** | Currency | Price per unit |
| **Total Price** | Formula | `{Quantity} * {Unit Price}` (or just use Order Amount) |

### **Delivery Tracking:**

| Field Name | Field Type | Options/Configuration |
|------------|-----------|----------------------|
| **Expected Ship Date** | Date | When supplier will ship |
| **Expected Delivery Date** | Date | When we expect delivery |
| **Actual Ship Date** | Date | When actually shipped |
| **Actual Delivery Date** | Date | When actually delivered |
| **Delivery On Time** | Formula | `IF({Actual Delivery Date}, IF({Actual Delivery Date} <= {Expected Delivery Date}, "✓ On Time", "⚠️ Late"), "")` |
| **Tracking Number** | Single line text | Shipment tracking number |
| **Carrier** | Single select | Options: `UPS`, `FedEx`, `USPS`, `Freight`, `Direct Delivery`, `Other` |

### **Invoicing:**

| Field Name | Field Type | Options/Configuration |
|------------|-----------|----------------------|
| **Supplier Invoice Number** | Single line text | Their invoice number |
| **Supplier Invoice Amount** | Currency | Amount on their invoice |
| **Supplier Invoice Date** | Date | Date of their invoice |
| **Supplier Invoice Due Date** | Date | When payment is due |
| **Supplier Invoice** | Attachment | Upload their invoice PDF |

### **Payment Tracking:**

| Field Name | Field Type | Options/Configuration |
|------------|-----------|----------------------|
| **Payment Method** | Single select | Options: `Net 30`, `Net 45`, `Factor Direct Payment`, `Check`, `ACH`, `Wire`, `Credit Card` |
| **Factoring Used** | Checkbox | Did you use factoring? |
| **Factor Paid Supplier** | Checkbox | Did factor pay supplier directly? |
| **Factor Paid Supplier Date** | Date | When factor paid them |
| **We Paid Supplier** | Checkbox | Did we pay supplier directly? |
| **We Paid Supplier Date** | Date | When we paid them |
| **Customer Invoice Submitted** | Checkbox | Did we invoice customer? |
| **Customer Paid Us** | Checkbox | Did customer pay us? |
| **Customer Payment Date** | Date | When customer paid |

### **Quality & Issues:**

| Field Name | Field Type | Options/Configuration |
|------------|-----------|----------------------|
| **Quality Rating** | Rating | 1-5 stars for this order |
| **Issues/Defects** | Long text | Any problems with order |
| **Returns/Replacements** | Long text | Any returns or replacements needed |

### **Profitability:**

| Field Name | Field Type | Options/Configuration |
|------------|-----------|----------------------|
| **Customer Invoice Amount** | Currency | What you invoiced customer |
| **Gross Profit** | Formula | `{Customer Invoice Amount} - {Order Amount}` |
| **Gross Margin (%)** | Formula | `({Gross Profit} / {Customer Invoice Amount}) * 100` |
| **Factoring Fee** | Currency | Fee paid to factor |
| **Net Profit After Factoring** | Formula | `{Gross Profit} - {Factoring Fee}` |
| **Net Margin (%)** | Formula | `({Net Profit After Factoring} / {Customer Invoice Amount}) * 100` |

### **Metadata:**

| Field Name | Field Type | Options/Configuration |
|------------|-----------|----------------------|
| **Notes** | Long text | Order notes |
| **Created Date** | Created time | Auto-generated |
| **Last Modified** | Last modified time | Auto-generated |

---

## 🔗 **TABLE RELATIONSHIPS:**

```
GPSS Opportunities (existing)
    ↓
    ├─→ Supplier Quotes (NEW) - Multiple quotes per opportunity
    │      ↓
    │      └─→ Suppliers (NEW) - Each quote from one supplier
    │
    └─→ Supplier Orders (NEW) - Orders placed for won opportunities
           ↓
           └─→ Suppliers (NEW) - Each order to one supplier

Suppliers (NEW)
    ↓
    ├─→ Supplier Quotes - All quotes from this supplier
    └─→ Supplier Orders - All orders to this supplier
```

---

## 🎯 **RECOMMENDED VIEWS:**

### **For GPSS Suppliers:**

1. **All Suppliers** - Default grid view
2. **Active Suppliers** - Filter: Business Status = Active
3. **Preferred Suppliers** - Filter: Tags contains "Preferred"
4. **Net 30 Available** - Filter: Net 30 Available = TRUE
5. **By Category** - Group by: Product Categories
6. **Top Performers** - Sort by: Overall Rating (descending)
7. **Needs Follow-up** - Filter: Next Follow-up Date ≤ Today
8. **Pending Approval** - Filter: Credit Status = Applied
9. **GSA Suppliers** - Filter: GSA Contract Holder = TRUE

### **For Supplier Quotes:**

1. **All Quotes** - Default view
2. **Pending Response** - Filter: Request Status = Sent
3. **Received** - Filter: Request Status = Received
4. **By Opportunity** - Group by: Opportunity
5. **By Supplier** - Group by: Supplier
6. **Selected Quotes** - Filter: Selected for Quote = TRUE
7. **Won Contracts** - Filter: Contract Awarded = TRUE
8. **This Week** - Filter: Request Sent Date = This Week

### **For Supplier Orders:**

1. **All Orders** - Default view
2. **Active Orders** - Filter: Order Status IN (Ordered, Confirmed, In Production, Shipped)
3. **In Transit** - Filter: Order Status = Shipped
4. **Awaiting Payment** - Filter: Supplier Invoice Due Date ≤ 7 days from now, We Paid Supplier = FALSE
5. **By Supplier** - Group by: Supplier
6. **This Month** - Filter: Order Date = This Month
7. **Late Deliveries** - Filter: Delivery On Time = "⚠️ Late"
8. **Using Factoring** - Filter: Factoring Used = TRUE

---

## ⚡ **QUICK START CHECKLIST:**

- [ ] Create table: **GPSS Suppliers**
- [ ] Add all Supplier fields (90+ fields total)
- [ ] Create table: **GPSS Supplier Quotes**
- [ ] Add all Quote fields (40+ fields)
- [ ] Create table: **GPSS Supplier Orders**
- [ ] Add all Order fields (50+ fields)
- [ ] Set up relationships (link fields)
- [ ] Create recommended views
- [ ] Test with 1-2 sample suppliers

**Estimated setup time: 45-60 minutes**

---

## 📊 **EXPECTED RESULT:**

Once complete, you'll have:
- ✅ Complete supplier database (track 100+ suppliers)
- ✅ Automated quote tracking (compare 5-10 quotes per opportunity)
- ✅ Order management (track all purchases)
- ✅ Profitability tracking (know your margins)
- ✅ Supplier performance scoring (rate suppliers)
- ✅ AI-ready data structure (for automation)

---

## 🚀 **NEXT STEPS:**

1. **Create these 3 tables in Airtable** (use this doc as guide)
2. **Add sample suppliers** (3-5 suppliers you know)
3. **Test relationships** (link a quote to opportunity and supplier)
4. **Let me know when done** - I'll build the backend automation!

**Questions? Need help with any field? Just ask!** 🎯
