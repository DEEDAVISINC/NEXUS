# 📋 CREATE THESE 3 TABLES IN AIRTABLE

---

## **TABLE 1: GPSS Suppliers**

| Field Name | Type | Settings |
|------------|------|----------|
| Supplier ID | Autonumber | PRIMARY FIELD |
| Company Name | Single line text | |
| Website | URL | |
| Primary Contact Email | Email | |
| Primary Contact Phone | Phone number | |
| Product Keywords | Long text | |
| Net 30 Available | Checkbox | |
| Net 45 Available | Checkbox | |
| Business Status | Single select | Options: Active, Prospective, Inactive, Blacklisted |
| Typical Margin (%) | Number | Precision: 0, Format: Decimal |
| Overall Rating | Rating | Max: 5, Icon: Star, Color: Yellow |
| Discovery Method | Single select | Options: AI Mining, Google Search, Manual Entry, Referral, GSA Mining, Cold Outreach |
| Discovery Date | Date | Include time: No |
| Discovered By | Single select | Options: AI Mining, Manual Entry, Dee Davis |

---

## **TABLE 2: GPSS Supplier Quotes**

| Field Name | Type | Settings |
|------------|------|----------|
| Quote Request ID | Autonumber | PRIMARY FIELD |
| Opportunity | Link to another record | Table: Opportunities |
| Supplier | Link to another record | Table: GPSS Suppliers |
| Product/Service Requested | Long text | |
| Quantity | Single line text | |
| Supplier Quote Amount | Currency | Precision: 2, Symbol: $ |
| Request Sent Date | Date | Include time: Yes |
| Quote Received Date | Date | Include time: Yes |
| Request Status | Single select | Options: Draft, Sent, Received, Declined, No Response, Expired |
| Our Markup (%) | Number | Precision: 0, Format: Decimal |
| Quoted Lead Time (Days) | Number | Precision: 0, Format: Integer |
| Selected for Quote | Checkbox | |
| Contract Awarded | Checkbox | |
| AI Recommendation | Long text | |

---

## **TABLE 3: GPSS Supplier Orders**

| Field Name | Type | Settings |
|------------|------|----------|
| Order ID | Autonumber | PRIMARY FIELD |
| PO Number | Single line text | |
| Opportunity | Link to another record | Table: Opportunities |
| Supplier | Link to another record | Table: GPSS Suppliers |
| Product Details | Long text | |
| Order Date | Date | Include time: No |
| Order Amount | Currency | Precision: 2, Symbol: $ |
| Customer Invoice Amount | Currency | Precision: 2, Symbol: $ |
| Order Status | Single select | Options: Ordered, Confirmed, Shipped, Delivered, Completed, Cancelled |
| Expected Delivery Date | Date | Include time: No |
| Actual Delivery Date | Date | Include time: No |
| Payment Method | Single select | Options: Net 30, Net 45, Net 60, Factor Direct Payment, Check, ACH, Credit Card |
| Factoring Used | Checkbox | |
| Quality Rating | Rating | Max: 5, Icon: Star, Color: Yellow |

---

## ✅ **THAT'S IT!**

**3 tables × 14 fields each = 42 fields total**

**Time: 45-60 minutes**

**Then message: "Tables created"**
