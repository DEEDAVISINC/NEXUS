# FULFILLMENT SYSTEM - AIRTABLE TABLE SETUP GUIDE

**Purpose:** Step-by-step instructions to create the 4 required Airtable tables for the Fulfillment System

---

## 📋 TABLES TO CREATE

1. **FULFILLMENT CONTRACTS** - Master contract records
2. **FULFILLMENT DELIVERIES** - Individual shipment tracking
3. **FULFILLMENT INVENTORY** - Real-time inventory tracking
4. **FULFILLMENT PURCHASE ORDERS** - Supplier order management

---

## TABLE 1: FULFILLMENT CONTRACTS

### Create Table
1. In Airtable, click **"Add a table"**
2. Name it: **FULFILLMENT CONTRACTS**
3. Add the following fields:

### Fields Configuration

| Field Name | Field Type | Configuration |
|------------|------------|---------------|
| CONTRACT_ID | Single line text | - |
| CONTRACT_NAME | Single line text | - |
| CLIENT_NAME | Single line text | - |
| PRODUCT | Single line text | - |
| TOTAL_QUANTITY | Number | Integer, no decimals |
| UNIT_PRICE | Currency | USD, 2 decimals |
| TOTAL_VALUE | Currency | USD, 2 decimals |
| START_DATE | Date | - |
| END_DATE | Date | - |
| DELIVERY_FREQUENCY | Single select | Options: Weekly, Biweekly, Monthly, Quarterly, Semi-Annual, Annual |
| QUANTITY_PER_DELIVERY | Number | Integer, no decimals |
| TOTAL_DELIVERIES | Number | Integer, no decimals |
| DELIVERIES_COMPLETED | Number | Integer, no decimals, default: 0 |
| DELIVERIES_REMAINING | Number | Integer, no decimals |
| STATUS | Single select | Options: Active, Paused, Completed, Cancelled |
| SUPPLIER_ID | Link to another record | Link to: GPSS SUPPLIERS |
| SUPPLIER_UNIT_COST | Currency | USD, 2 decimals |
| MARGIN_PER_UNIT | Currency | USD, 2 decimals |
| NEXT_DELIVERY_DATE | Date | - |
| ALERT_THRESHOLD | Number | Integer, no decimals |
| NOTES | Long text | - |

### Views to Create
1. **Active Contracts** - Filter: Status = Active
2. **By Client** - Group by: CLIENT_NAME
3. **Due Soon** - Filter: NEXT_DELIVERY_DATE within 7 days

---

## TABLE 2: FULFILLMENT DELIVERIES

### Create Table
1. Click **"Add a table"**
2. Name it: **FULFILLMENT DELIVERIES**
3. Add the following fields:

### Fields Configuration

| Field Name | Field Type | Configuration |
|------------|------------|---------------|
| DELIVERY_ID | Single line text | - |
| CONTRACT | Link to another record | Link to: FULFILLMENT CONTRACTS, Allow multiple |
| DELIVERY_NUMBER | Number | Integer, no decimals |
| DUE_DATE | Date | - |
| SCHEDULED_DATE | Date | - |
| ACTUAL_DELIVERY_DATE | Date | - |
| QUANTITY | Number | Integer, no decimals |
| STATUS | Single select | Options: Scheduled, In Transit, Delivered, Late, Cancelled |
| TRACKING_NUMBER | Single line text | - |
| CARRIER | Single select | Options: UPS, FedEx, USPS, DHL, Other |
| SHIPPING_COST | Currency | USD, 2 decimals |
| DELIVERED_TO | Single line text | - |
| DELIVERY_CONFIRMATION | Attachment | - |
| NOTES | Long text | - |
| DAYS_EARLY_LATE | Number | Integer (positive = early, negative = late) |

### Views to Create
1. **Due This Week** - Filter: DUE_DATE within 7 days, STATUS ≠ Delivered
2. **In Transit** - Filter: STATUS = In Transit
3. **Completed** - Filter: STATUS = Delivered, Sort: ACTUAL_DELIVERY_DATE descending
4. **Overdue** - Filter: DUE_DATE < TODAY(), STATUS ≠ Delivered

---

## TABLE 3: FULFILLMENT INVENTORY

### Create Table
1. Click **"Add a table"**
2. Name it: **FULFILLMENT INVENTORY**
3. Add the following fields:

### Fields Configuration

| Field Name | Field Type | Configuration |
|------------|------------|---------------|
| PRODUCT_SKU | Single line text | - |
| PRODUCT_NAME | Single line text | - |
| QUANTITY_ON_HAND | Number | Integer, no decimals |
| QUANTITY_COMMITTED | Number | Integer, no decimals (allocated to deliveries) |
| QUANTITY_AVAILABLE | Number | Integer, no decimals (on hand - committed) |
| REORDER_POINT | Number | Integer, no decimals |
| REORDER_QUANTITY | Number | Integer, no decimals |
| SUPPLIER | Link to another record | Link to: GPSS SUPPLIERS, Allow multiple |
| UNIT_COST | Currency | USD, 2 decimals |
| LAST_RESTOCK_DATE | Date | - |
| NEXT_RESTOCK_DATE | Date | - |
| LOCATION | Single line text | - |
| STATUS | Single select | Options: Healthy, Low Stock, Critical, Out of Stock |
| ACTIVE_CONTRACTS | Number | Integer, no decimals |
| MONTHLY_BURN_RATE | Number | Integer, no decimals (units per month) |
| ESTIMATED_RUNOUT_DATE | Date | - |

### Views to Create
1. **Critical Items** - Filter: STATUS = Critical, Sort: QUANTITY_AVAILABLE ascending
2. **Low Stock** - Filter: STATUS = Low Stock
3. **Healthy** - Filter: STATUS = Healthy
4. **All Products** - Sort: PRODUCT_NAME

### Color Coding (Conditional Formatting)
- **Red background**: STATUS = Critical or Out of Stock
- **Yellow background**: STATUS = Low Stock
- **Green background**: STATUS = Healthy

---

## TABLE 4: FULFILLMENT PURCHASE ORDERS

### Create Table
1. Click **"Add a table"**
2. Name it: **FULFILLMENT PURCHASE ORDERS**
3. Add the following fields:

### Fields Configuration

| Field Name | Field Type | Configuration |
|------------|------------|---------------|
| PO_NUMBER | Single line text | - |
| SUPPLIER | Link to another record | Link to: GPSS SUPPLIERS, Allow multiple |
| ORDER_DATE | Date | - |
| EXPECTED_DELIVERY_DATE | Date | - |
| ACTUAL_DELIVERY_DATE | Date | - |
| PRODUCTS | Long text | - |
| QUANTITY_ORDERED | Number | Integer, no decimals |
| QUANTITY_RECEIVED | Number | Integer, no decimals |
| UNIT_COST | Currency | USD, 2 decimals |
| TOTAL_COST | Currency | USD, 2 decimals |
| PAYMENT_TERMS | Single select | Options: Net 30, Net 60, Net 90, COD, Prepay |
| PAYMENT_DUE_DATE | Date | - |
| PAYMENT_STATUS | Single select | Options: Pending, Paid, Overdue |
| STATUS | Single select | Options: Ordered, In Transit, Received, Cancelled |
| NOTES | Long text | - |

### Views to Create
1. **Pending Orders** - Filter: STATUS = Ordered
2. **In Transit** - Filter: STATUS = In Transit
3. **Received** - Filter: STATUS = Received, Sort: ACTUAL_DELIVERY_DATE descending
4. **Payment Due** - Filter: PAYMENT_STATUS = Pending, Sort: PAYMENT_DUE_DATE ascending

---

## 🔗 TABLE RELATIONSHIPS

### Set Up Links Between Tables

1. **FULFILLMENT CONTRACTS → FULFILLMENT DELIVERIES**
   - In DELIVERIES table: CONTRACT field links to CONTRACTS table
   - This allows one contract to have many deliveries

2. **FULFILLMENT CONTRACTS → GPSS SUPPLIERS**
   - In CONTRACTS table: SUPPLIER_ID field links to GPSS SUPPLIERS
   - This shows which supplier provides the product

3. **FULFILLMENT INVENTORY → GPSS SUPPLIERS**
   - In INVENTORY table: SUPPLIER field links to GPSS SUPPLIERS
   - This shows which suppliers can provide each product

4. **FULFILLMENT PURCHASE ORDERS → GPSS SUPPLIERS**
   - In PURCHASE ORDERS table: SUPPLIER field links to GPSS SUPPLIERS
   - This shows which supplier each PO is placed with

---

## ✅ VERIFICATION CHECKLIST

After creating all tables, verify:

- [ ] All 4 tables created with correct names (ALL CAPS)
- [ ] All fields created with exact field names (ALL CAPS)
- [ ] Field types match specification
- [ ] Single select options configured
- [ ] Currency fields set to USD with 2 decimals
- [ ] Links to GPSS SUPPLIERS table work
- [ ] Links between CONTRACTS and DELIVERIES work
- [ ] Views created for each table
- [ ] Color coding applied to INVENTORY table

---

## 🧪 TEST DATA

To test the system, create a sample contract:

### Sample Contract Data
```
CONTRACT_NAME: TEST - Office Supplies Monthly
CLIENT_NAME: City of Austin
PRODUCT: Paper Reams - White 8.5x11
TOTAL_QUANTITY: 600
UNIT_PRICE: 25.00
SUPPLIER_UNIT_COST: 18.00
DELIVERY_FREQUENCY: Monthly
QUANTITY_PER_DELIVERY: 50
START_DATE: [30 days from now]
STATUS: Active
```

This will generate 12 monthly deliveries (600 ÷ 50).

---

## 📞 NEED HELP?

If you encounter issues:

1. **Check field names** - Must be ALL CAPS exactly as shown
2. **Check field types** - Currency vs Number matters
3. **Check links** - Make sure GPSS SUPPLIERS table exists first
4. **Test with sample data** - Use the test contract above

---

## 🚀 NEXT STEPS

Once tables are set up:

1. Run `python test_fulfillment_system.py` to verify backend integration
2. Set up daily monitoring: `python fulfillment_monitor.py`
3. Start using the system via API endpoints
4. Create your first real contract!

---

**Tables ready? Let's track those contracts!** 📦
