# 📋 Optional Airtable Fields to Add for New Features

**Fields to enhance Quote, CapStat, and Contract Command Center integration**

---

## 🎯 Opportunities Table (GPSS)

### For Capability Statements:
```
Field Name: Cap Statement Generated
Type: Checkbox
Purpose: Track if cap statement was generated for this opp

Field Name: Cap Statement Date
Type: Date
Purpose: When was it generated

Field Name: Cap Statement Link
Type: Link to Records (CapabilityStatements table)
Purpose: Link to generated cap statement record
```

### For Quote Tracking:
```
Field Name: Quotes Sent
Type: Number (or Rollup from Quote Requests)
Purpose: How many supplier quotes sent

Field Name: Quotes Received
Type: Number (or Rollup from Quote Requests)
Purpose: How many suppliers responded

Field Name: Best Quote Amount
Type: Currency (or Rollup from Quote Requests)
Purpose: Lowest quote received

Field Name: Quote Response Rate
Type: Formula
Purpose: {Quotes Received} / {Quotes Sent}
```

### For Contract Management:
```
Field Name: Contract
Type: Link to Records (Contracts table)
Purpose: Link to contract if won

Field Name: Contract Status
Type: Single Select
Options: Not Applicable, Setup, Active, Completed
Purpose: Post-award status
```

---

## 🏭 Suppliers Table (GPSS)

### For Quote Performance:
```
Field Name: Quotes Sent Count
Type: Rollup (from Quote Requests)
Purpose: Total quotes requested from this supplier

Field Name: Quotes Received Count
Type: Rollup (from Quote Requests)
Purpose: How many times they responded

Field Name: Response Rate
Type: Formula
Purpose: {Quotes Received} / {Quotes Sent}

Field Name: Average Response Time
Type: Rollup (Average of Response Time from Quote Requests)
Purpose: Days to respond on average

Field Name: Supplier Rating
Type: Rating (1-5 stars)
Purpose: Overall performance rating
```

### For Contract Performance:
```
Field Name: Active Contracts
Type: Count (from Contracts table)
Purpose: How many active contracts with this supplier

Field Name: On-Time Delivery Rate
Type: Percent
Purpose: Performance metric

Field Name: Last Used Date
Type: Date
Purpose: When did we last buy from them
```

---

## 💰 Invoices Table

### For Contract Tracking:
```
Field Name: Contract
Type: Link to Records (Contracts table)
Purpose: Link to related contract (if from contract)

Field Name: Delivery
Type: Link to Records (Contract Deliveries table)
Purpose: Link to specific delivery being invoiced
```

---

## 👥 Contacts Table

### For Relationship Tracking:
```
Field Name: Last Interaction
Type: Date
Purpose: Last contact date

Field Name: Interaction Count
Type: Count (from Contract Interactions table)
Purpose: How many times contacted

Field Name: Relationship Quality
Type: Single Select
Options: Excellent, Good, Fair, Poor, New
Purpose: Relationship status
```

---

## 🆕 NEW TABLES NEEDED

### These tables probably DON'T exist yet:

### 1. Quote Requests (NEW)
```
Purpose: Track supplier quote requests
Links to: Opportunities, Suppliers
Fields: 16 (see QUOTE_REQUESTS_AIRTABLE_SCHEMA.md)
Time: 15 minutes
```

### 2. Contracts (NEW)
```
Purpose: Post-award contract management
Links to: Opportunities, Suppliers, Invoices
Fields: 25+
Time: 30 minutes
```

### 3. Purchase Orders (NEW)
```
Purpose: Supplier PO tracking
Links to: Contracts, Suppliers, Quote Requests
Fields: 20+
Time: 20 minutes
```

### 4. Contract Deliveries (NEW)
```
Purpose: Delivery schedule & tracking
Links to: Contracts, Purchase Orders
Fields: 15+
Time: 15 minutes
```

### 5. Contract Interactions (NEW)
```
Purpose: Log all client/supplier communications
Links to: Contracts, Contacts
Fields: 12+
Time: 10 minutes
```

### 6. Contract Issues (NEW)
```
Purpose: Problem tracking & resolution
Links to: Contracts, Deliveries, Purchase Orders
Fields: 12+
Time: 10 minutes
```

---

## 📊 Priority Guide

### MUST HAVE (for basic functionality):
- ✅ Your existing 70+ tables work fine!
- Nothing breaks if you don't add these fields

### NICE TO HAVE (enhances workflow):
**Opportunities table:**
- Cap Statement Generated (checkbox)
- Quotes Sent/Received (numbers)

**Suppliers table:**
- Response Rate (formula)
- Supplier Rating (rating)

### CRITICAL FOR "NOTHING FALLS THROUGH":
**NEW TABLES (6 tables):**
- Quote Requests
- Contracts
- Purchase Orders
- Contract Deliveries
- Contract Interactions
- Contract Issues

**Time to add: ~2 hours for all 6 tables**

---

## 🎯 Recommendation

### Option 1: Start Using NOW (No Changes)
Your existing tables work! The features will function with what you have.

### Option 2: Add Enhancement Fields (30 min)
Add the fields above to Opportunities and Suppliers tables for better tracking.

### Option 3: Full Integration (2 hours)
Create the 6 new tables for complete post-award management.

---

## ✅ What Works RIGHT NOW With NO Changes:

1. **Find Opportunities** ✅ (uses existing Opportunities table)
2. **Generate Cap Statements** ✅ (creates PDFs, can link to Opportunities)
3. **Price Bids** ✅ (uses existing Pricing tables)
4. **Generate Proposals** ✅ (uses existing Proposals table)
5. **Create Invoices** ✅ (uses existing Invoices table)

## 🆕 What Needs New Tables:

1. **Track Quote Requests** 🆕 (needs Quote Requests table)
2. **Manage Contracts** 🆕 (needs 5 CCC tables)
3. **Track Deliveries** 🆕 (needs Contract Deliveries table)
4. **Log Interactions** 🆕 (needs Contract Interactions table)

---

## 🚀 Quick Win

**Add just these 3 fields to Opportunities table:**
1. Cap Statement Generated (checkbox)
2. Quotes Sent (number)
3. Contract (link to Contracts table)

**Time: 5 minutes**
**Benefit: See status at-a-glance in opportunity table**

---

**Bottom line: Your 70+ tables are READY TO USE! Only add fields if you want enhanced tracking!**
