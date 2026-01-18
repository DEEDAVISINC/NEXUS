# 💎 VERTEX - Airtable Schema (Complete Setup Guide)

**All 7 tables for the VERTEX Financial System**

---

## 📊 **TABLE OVERVIEW**

| # | Table Name | Fields | Setup Time | Priority |
|---|------------|--------|------------|----------|
| 1 | VERTEX Invoices | 50 | 60 min | HIGH |
| 2 | VERTEX Expenses | 20 | 30 min | HIGH |
| 3 | VERTEX Revenue | 15 | 20 min | MEDIUM |
| 4 | VERTEX Bank Transactions | 18 | 25 min | MEDIUM |
| 5 | VERTEX Payroll | 22 | 30 min | LOW |
| 6 | VERTEX Clients | 16 | 20 min | MEDIUM |
| 7 | VERTEX Reports | 10 | 15 min | LOW |

**Total Setup Time:** ~3.5 hours  
**Recommended Order:** 1 → 6 → 2 → 3 → 4 → 5 → 7

---

## 💰 **TABLE 1: VERTEX Invoices**

### **Purpose:** Universal invoicing across all NEXUS systems with government compliance and factoring support

### **Fields:**

| Field Name | Field Type | Options/Configuration |
|------------|-----------|----------------------|
| **Invoice Number** | Single line text | PRIMARY FIELD - Auto-generated format: INV-YYYY-#### |
| **Invoice Date** | Date | Date invoice was created |
| **Due Date** | Date | Payment due date |
| **Client Name** | Single line text | Client/customer name |
| **Client ID** | Link to another record | Link to VERTEX Clients table |
| **Source System** | Single select | Options: `GPSS`, `ATLAS`, `DDCSS`, `LBPC`, `GBIS`, `Other` |
| **Source Record ID** | Single line text | ID from source system (opportunity, project, etc.) |
| **GPSS Opportunity** | Link to another record | Link to GPSS Opportunities (if applicable) |
| **ATLAS Project** | Link to another record | Link to ATLAS Projects (if applicable) |
| **DDCSS Prospect** | Link to another record | Link to DDCSS Prospects (if applicable) |
| **LBPC Lead** | Link to another record | Link to LBPC Leads (if applicable) |
| **Invoice Type** | Single select | Options: `Standard`, `Government Contract`, `Recurring`, `Milestone`, `Final`, `Progress` |
| **Line Items** | Long text | JSON format: `[{"description":"","quantity":1,"rate":0,"amount":0}]` |
| **Subtotal** | Currency | Sum of all line items |
| **Tax Rate (%)** | Number | Percentage (0-100) |
| **Tax Amount** | Currency | Formula: `{Subtotal} * {Tax Rate (%)} / 100` |
| **Discount (%)** | Number | Percentage discount (0-100) |
| **Discount Amount** | Currency | Formula: `{Subtotal} * {Discount (%)} / 100` |
| **Total Amount** | Currency | Formula: `{Subtotal} + {Tax Amount} - {Discount Amount}` |
| **Amount Paid** | Currency | Total amount received |
| **Balance Due** | Currency | Formula: `{Total Amount} - {Amount Paid}` |
| **Payment Status** | Single select | Options: `Unpaid`, `Partial`, `Paid`, `Overdue`, `Cancelled`, `Factored` |
| **Payment Method** | Single select | Options: `Check`, `ACH`, `Wire`, `Credit Card`, `Factoring`, `Other` |
| **Payment Date** | Date | Date payment was received |
| **Payment Terms** | Single select | Options: `Net 15`, `Net 30`, `Net 45`, `Net 60`, `Due on Receipt`, `Custom` |
| **Days Outstanding** | Formula | Formula: `IF({Payment Status}="Paid",0,DATETIME_DIFF(TODAY(),{Invoice Date},'days'))` |
| **Aging Category** | Formula | Formula: `IF({Days Outstanding}<=30,"Current",IF({Days Outstanding}<=60,"31-60 Days",IF({Days Outstanding}<=90,"61-90 Days","90+ Days")))` |
| **Notes** | Long text | Internal notes |
| **Client Notes** | Long text | Notes visible to client |
| **PO Number** | Single line text | Client purchase order number |
| **Contract Number** | Single line text | Government contract number (if applicable) |
| **CAGE Code** | Single line text | Government contractor code |
| **DUNS Number** | Single line text | Data Universal Numbering System |
| **SAM.gov UEI** | Single line text | Unique Entity Identifier |
| **Government Agency** | Single line text | Federal/state/local agency name |
| **Contract Type** | Single select | Options: `FFP`, `T&M`, `CPFF`, `IDIQ`, `BPA`, `N/A` |
| **Invoice PDF** | Attachment | Generated invoice PDF |
| **Supporting Documents** | Attachment | Receipts, timesheets, etc. |
| **Sent Date** | Date | Date invoice was sent to client |
| **Sent By** | Single line text | Who sent the invoice |
| **Follow-up Date** | Date | Next follow-up date for unpaid invoices |
| **Created Date** | Created time | Auto-generated |
| **Last Modified** | Last modified time | Auto-generated |
| **Created By** | Created by | Auto-generated |
| **FACTORING FIELDS:** | | |
| **Factoring Status** | Single select | Options: `Not Factored`, `Submitted`, `Approved`, `Funded`, `Paid Off`, `Rejected` |
| **Factoring Company** | Link to another record | Link to VERTEX Clients (factoring company) |
| **Factoring Fee (%)** | Number | Percentage charged (typically 2-5%) |
| **Factoring Fee ($)** | Currency | Formula: `{Total Amount} * {Factoring Fee (%)} / 100` |
| **Advance Rate (%)** | Number | Percentage received upfront (typically 80-90%) |
| **Advance Amount ($)** | Currency | Formula: `{Total Amount} * {Advance Rate (%)} / 100` |
| **Reserve Amount ($)** | Currency | Formula: `{Total Amount} - {Advance Amount ($)} - {Factoring Fee ($)}` |
| **Factoring Submitted Date** | Date | When submitted to factoring company |
| **Factoring Funded Date** | Date | When you received funds |
| **Client Payment to Factor Date** | Date | When client paid factoring company |
| **Reserve Released Date** | Date | When reserve was released to you |

### **Views to Create:**

1. **All Invoices** (Grid view - default)
2. **Unpaid Invoices** (Filter: Payment Status = Unpaid or Partial)
3. **Overdue** (Filter: Days Outstanding > 30 AND Payment Status ≠ Paid)
4. **Aging Report** (Group by: Aging Category)
5. **Factored Invoices** (Filter: Factoring Status ≠ Not Factored)
6. **By System** (Group by: Source System)
7. **Government Contracts** (Filter: Invoice Type = Government Contract)
8. **This Month** (Filter: Invoice Date is within this month)

---

## 💳 **TABLE 2: VERTEX Expenses**

### **Purpose:** Track all business expenses, tax deductions, and billable expenses

### **Fields:**

| Field Name | Field Type | Options/Configuration |
|------------|-----------|----------------------|
| **Expense ID** | Auto number | PRIMARY FIELD - Format: EXP-#### |
| **Expense Date** | Date | Date expense was incurred |
| **Vendor/Payee** | Single line text | Who was paid |
| **Vendor ID** | Link to another record | Link to VERTEX Clients (vendor profile) |
| **Description** | Long text | What was purchased/paid for |
| **Category** | Single select | Options: `Payroll`, `Software/Tools`, `Marketing`, `Office Supplies`, `Travel`, `Meals`, `Equipment`, `Rent/Utilities`, `Professional Services`, `Insurance`, `Taxes`, `Other` |
| **Subcategory** | Single line text | More specific categorization |
| **Amount** | Currency | Total expense amount |
| **Payment Method** | Single select | Options: `Check`, `Credit Card`, `ACH`, `Wire`, `Cash`, `Debit Card` |
| **Payment Date** | Date | Date payment was made |
| **Payment Status** | Single select | Options: `Unpaid`, `Paid`, `Pending`, `Reimbursed` |
| **Receipt** | Attachment | Receipt image/PDF |
| **Tax Deductible** | Checkbox | Is this expense tax deductible? |
| **Tax Category** | Single select | Options: `100% Deductible`, `50% Deductible` (meals), `Not Deductible` |
| **Billable** | Checkbox | Is this expense billable to a client? |
| **Billable To** | Link to another record | Link to VERTEX Clients |
| **Project** | Link to another record | Link to ATLAS Projects (if billable) |
| **Invoice** | Link to another record | Link to VERTEX Invoices (if billed) |
| **Reimbursable** | Checkbox | Should employee be reimbursed? |
| **Notes** | Long text | Additional notes |
| **Created Date** | Created time | Auto-generated |
| **Last Modified** | Last modified time | Auto-generated |

### **Views to Create:**

1. **All Expenses** (Grid view - default)
2. **Unpaid** (Filter: Payment Status = Unpaid)
3. **By Category** (Group by: Category)
4. **Tax Deductible** (Filter: Tax Deductible = checked)
5. **Billable Expenses** (Filter: Billable = checked AND Invoice is empty)
6. **This Month** (Filter: Expense Date is within this month)

---

## 💵 **TABLE 3: VERTEX Revenue**

### **Purpose:** Track all income sources (invoices, grants, investments, other)

### **Fields:**

| Field Name | Field Type | Options/Configuration |
|------------|-----------|----------------------|
| **Revenue ID** | Auto number | PRIMARY FIELD - Format: REV-#### |
| **Revenue Date** | Date | Date income was received |
| **Source** | Single line text | Where did this money come from? |
| **Revenue Type** | Single select | Options: `Invoice Payment`, `Grant`, `Investment`, `Loan`, `Refund`, `Interest`, `Other Income` |
| **Source System** | Single select | Options: `GPSS`, `ATLAS`, `DDCSS`, `LBPC`, `GBIS`, `Other` |
| **Amount** | Currency | Total amount received |
| **Payment Method** | Single select | Options: `Check`, `ACH`, `Wire`, `Credit Card`, `Cash`, `Other` |
| **Invoice** | Link to another record | Link to VERTEX Invoices (if payment for invoice) |
| **Grant** | Link to another record | Link to GBIS Grant Applications (if grant income) |
| **Opportunity** | Link to another record | Link to GPSS Opportunities (if contract payment) |
| **Project** | Link to another record | Link to ATLAS Projects (if project payment) |
| **Category** | Single select | Options: `Operating Revenue`, `Non-Operating Revenue`, `Capital` |
| **Taxable** | Checkbox | Is this taxable income? |
| **Recurring** | Checkbox | Is this recurring income? |
| **Notes** | Long text | Additional details |
| **Created Date** | Created time | Auto-generated |
| **Last Modified** | Last modified time | Auto-generated |

### **Views to Create:**

1. **All Revenue** (Grid view - default)
2. **By Type** (Group by: Revenue Type)
3. **By System** (Group by: Source System)
4. **This Month** (Filter: Revenue Date is within this month)
5. **Recurring Revenue** (Filter: Recurring = checked)

---

## 🏦 **TABLE 4: VERTEX Bank Transactions**

### **Purpose:** Import and manage bank/credit card transactions, reconciliation

### **Fields:**

| Field Name | Field Type | Options/Configuration |
|------------|-----------|----------------------|
| **Transaction ID** | Auto number | PRIMARY FIELD - Format: TXN-#### |
| **Transaction Date** | Date | Date transaction occurred |
| **Post Date** | Date | Date transaction posted to account |
| **Description** | Long text | Bank's transaction description |
| **Amount** | Currency | Transaction amount |
| **Type** | Single select | Options: `Debit`, `Credit` |
| **Account** | Single select | Options: `Checking`, `Savings`, `Credit Card`, `PayPal`, `Other` |
| **Account Number (Last 4)** | Single line text | Last 4 digits of account |
| **Category** | Single select | Same as Expenses category list + `Revenue`, `Transfer`, `Unclassified` |
| **Matched** | Checkbox | Has this been matched to invoice/expense? |
| **Matched To Type** | Single select | Options: `Invoice`, `Expense`, `Revenue`, `Transfer`, `None` |
| **Invoice Match** | Link to another record | Link to VERTEX Invoices |
| **Expense Match** | Link to another record | Link to VERTEX Expenses |
| **Revenue Match** | Link to another record | Link to VERTEX Revenue |
| **Reconciled** | Checkbox | Has this been reconciled? |
| **Notes** | Long text | Additional notes |
| **Import Batch** | Single line text | Batch ID from CSV import |
| **Created Date** | Created time | Auto-generated |
| **Last Modified** | Last modified time | Auto-generated |

### **Views to Create:**

1. **All Transactions** (Grid view - default, sorted by Transaction Date DESC)
2. **Unmatched** (Filter: Matched = unchecked)
3. **Unreconciled** (Filter: Reconciled = unchecked)
4. **By Account** (Group by: Account)
5. **This Month** (Filter: Transaction Date is within this month)

---

## 👥 **TABLE 5: VERTEX Payroll**

### **Purpose:** Track employee and contractor payments, taxes, deductions

### **Fields:**

| Field Name | Field Type | Options/Configuration |
|------------|-----------|----------------------|
| **Payroll ID** | Auto number | PRIMARY FIELD - Format: PAY-#### |
| **Pay Period Start** | Date | Start of pay period |
| **Pay Period End** | Date | End of pay period |
| **Employee Name** | Single line text | Full name |
| **Employee Type** | Single select | Options: `W-2 Employee`, `1099 Contractor`, `Owner Draw` |
| **Employee ID** | Single line text | Internal employee ID |
| **SSN/EIN (Last 4)** | Single line text | Last 4 digits only (security) |
| **Gross Pay** | Currency | Total pay before deductions |
| **Hourly Rate** | Currency | $ per hour (if applicable) |
| **Hours Worked** | Number | Hours (if applicable) |
| **Salary** | Currency | Annual salary (if salaried) |
| **Federal Tax** | Currency | Federal income tax withheld |
| **State Tax** | Currency | State income tax withheld |
| **FICA (Social Security)** | Currency | Formula: `{Gross Pay} * 0.062` (6.2% up to wage base) |
| **Medicare** | Currency | Formula: `{Gross Pay} * 0.0145` (1.45%) |
| **Other Deductions** | Currency | Health insurance, 401k, etc. |
| **Deduction Notes** | Long text | Details on deductions |
| **Net Pay** | Currency | Formula: `{Gross Pay} - {Federal Tax} - {State Tax} - {FICA (Social Security)} - {Medicare} - {Other Deductions}` |
| **Payment Date** | Date | Date payment was made |
| **Payment Method** | Single select | Options: `Direct Deposit`, `Check`, `Wire`, `Cash` |
| **Payment Status** | Single select | Options: `Pending`, `Paid`, `Cancelled` |
| **YTD Gross** | Currency | Year-to-date total (rollup or manual) |
| **Notes** | Long text | Additional notes |
| **Created Date** | Created time | Auto-generated |

### **Views to Create:**

1. **All Payroll** (Grid view - default)
2. **By Employee** (Group by: Employee Name)
3. **W-2 Employees** (Filter: Employee Type = W-2 Employee)
4. **1099 Contractors** (Filter: Employee Type = 1099 Contractor)
5. **This Year** (Filter: Pay Period End is within this year)

---

## 🤝 **TABLE 6: VERTEX Clients**

### **Purpose:** Financial profiles for all clients, vendors, and factoring companies

### **Fields:**

| Field Name | Field Type | Options/Configuration |
|------------|-----------|----------------------|
| **Client Name** | Single line text | PRIMARY FIELD - Full name or company name |
| **Client Type** | Single select | Options: `Client`, `Vendor`, `Both`, `Factoring Company`, `Employee`, `Contractor` |
| **Contact Name** | Single line text | Primary contact person |
| **Email** | Email | Primary email |
| **Phone** | Phone number | Primary phone |
| **Address** | Long text | Full address |
| **Tax ID (EIN/SSN)** | Single line text | Encrypted or last 4 only |
| **Payment Terms** | Single select | Options: `Net 15`, `Net 30`, `Net 45`, `Net 60`, `Due on Receipt`, `COD`, `Custom` |
| **Credit Limit** | Currency | Maximum outstanding balance allowed |
| **Current Balance** | Rollup | Sum of unpaid invoices (rollup from VERTEX Invoices) |
| **Total Invoiced** | Rollup | Sum of all invoices (rollup from VERTEX Invoices) |
| **Total Paid** | Rollup | Sum of all payments (rollup from VERTEX Invoices) |
| **Average Payment Time (Days)** | Number | Average days to payment |
| **Payment Rating** | Single select | Options: `Excellent`, `Good`, `Fair`, `Poor`, `New` |
| **Active** | Checkbox | Is this client/vendor active? |
| **Notes** | Long text | Additional notes |
| **Created Date** | Created time | Auto-generated |

### **Views to Create:**

1. **All Clients** (Grid view - default)
2. **Active Clients** (Filter: Active = checked)
3. **Clients Only** (Filter: Client Type = Client or Both)
4. **Vendors Only** (Filter: Client Type = Vendor or Both)
5. **Factoring Companies** (Filter: Client Type = Factoring Company)
6. **High Balance** (Filter: Current Balance > $10,000)

---

## 📊 **TABLE 7: VERTEX Reports**

### **Purpose:** Save financial reports and AI-generated insights

### **Fields:**

| Field Name | Field Type | Options/Configuration |
|------------|-----------|----------------------|
| **Report ID** | Auto number | PRIMARY FIELD - Format: RPT-#### |
| **Report Name** | Single line text | Descriptive name |
| **Report Type** | Single select | Options: `P&L`, `Balance Sheet`, `Cash Flow`, `A/R Aging`, `Expense Summary`, `Revenue Summary`, `Custom`, `AI Insight` |
| **Period Start** | Date | Start date of report period |
| **Period End** | Date | End date of report period |
| **Report Data** | Long text | JSON format with all data |
| **Summary** | Long text | Executive summary (AI-generated) |
| **Key Insights** | Long text | AI-generated insights |
| **Recommendations** | Long text | AI-generated recommendations |
| **Generated Date** | Created time | Auto-generated |
| **Generated By** | Created by | Auto-generated |
| **Export Format** | Multiple select | Options: `PDF`, `CSV`, `Excel`, `QuickBooks`, `JSON` |

### **Views to Create:**

1. **All Reports** (Grid view - default, sorted by Generated Date DESC)
2. **By Type** (Group by: Report Type)
3. **This Month** (Filter: Generated Date is within this month)

---

## 🔗 **RELATIONSHIPS BETWEEN TABLES**

### **VERTEX Invoices links to:**
- VERTEX Clients (Client ID, Factoring Company)
- GPSS Opportunities (Source)
- ATLAS Projects (Source)
- DDCSS Prospects (Source)
- LBPC Leads (Source)
- VERTEX Expenses (billable expenses)
- VERTEX Revenue (payment tracking)

### **VERTEX Expenses links to:**
- VERTEX Clients (Vendor ID, Billable To)
- ATLAS Projects (Project)
- VERTEX Invoices (Invoice - if billed)

### **VERTEX Revenue links to:**
- VERTEX Invoices (Invoice)
- VERTEX Clients (implicit through invoice)
- GPSS Opportunities (Opportunity)
- ATLAS Projects (Project)
- GBIS Grant Applications (Grant)

### **VERTEX Bank Transactions links to:**
- VERTEX Invoices (Invoice Match)
- VERTEX Expenses (Expense Match)
- VERTEX Revenue (Revenue Match)

### **VERTEX Payroll links to:**
- (No direct links, but could link to VERTEX Clients if tracking as vendors)

### **VERTEX Clients links to:**
- VERTEX Invoices (rollup for balances)
- VERTEX Expenses (vendor relationships)

### **VERTEX Reports:**
- (No direct links, stores JSON data)

---

## ⏱️ **SETUP ORDER & TIME ESTIMATES**

### **Recommended Setup Order:**

1. **VERTEX Clients** (20 min) - Create this first, other tables link to it
2. **VERTEX Invoices** (60 min) - Core table, most complex
3. **VERTEX Expenses** (30 min) - Links to Clients and Invoices
4. **VERTEX Revenue** (20 min) - Links to Invoices
5. **VERTEX Bank Transactions** (25 min) - Links to Invoices, Expenses, Revenue
6. **VERTEX Payroll** (30 min) - Standalone, can be done later
7. **VERTEX Reports** (15 min) - Standalone, can be done last

**Total Time: ~3.5 hours**

---

## 🎯 **QUICK START GUIDE**

### **Step 1: Create Airtable Base**
1. Go to Airtable.com
2. Click "Add a base"
3. Choose "Start from scratch"
4. Name it: **"NEXUS Command Center"** (or add to existing base)

### **Step 2: Create Tables**
For each table above:
1. Click "Add or import" → "Create empty table"
2. Name the table (e.g., "VERTEX Invoices")
3. Add all fields from the list
4. Configure field types and options exactly as specified
5. Create the recommended views

### **Step 3: Set Up Relationships**
1. In VERTEX Invoices, link to VERTEX Clients
2. In VERTEX Expenses, link to VERTEX Clients and VERTEX Invoices
3. In VERTEX Revenue, link to VERTEX Invoices
4. In VERTEX Bank Transactions, link to VERTEX Invoices, Expenses, Revenue
5. Create rollup fields in VERTEX Clients for balances

### **Step 4: Test with Sample Data**
1. Create a test client in VERTEX Clients
2. Create a test invoice in VERTEX Invoices
3. Create a test expense in VERTEX Expenses
4. Verify formulas are calculating correctly
5. Test views and filters

### **Step 5: Connect to NEXUS Backend**
1. Update `.env` file with `AIRTABLE_BASE_ID`
2. Test API connections
3. Verify data syncing

---

## 💡 **PRO TIPS**

### **Formula Tips:**
- Copy formulas exactly (spacing matters!)
- Test formulas with sample data
- If formula errors, check field names match exactly

### **View Tips:**
- Create views AFTER all fields are added
- Use color coding for status fields
- Set default sort orders

### **Performance Tips:**
- Don't create too many rollup fields (slows down base)
- Use formulas instead of rollups when possible
- Archive old data periodically

### **Security Tips:**
- Never store full SSN or Tax ID
- Use "Last 4 digits only" for sensitive data
- Set proper sharing permissions

---

## ✅ **COMPLETION CHECKLIST**

- [ ] VERTEX Clients table created (20 min)
- [ ] VERTEX Invoices table created (60 min)
- [ ] VERTEX Expenses table created (30 min)
- [ ] VERTEX Revenue table created (20 min)
- [ ] VERTEX Bank Transactions table created (25 min)
- [ ] VERTEX Payroll table created (30 min)
- [ ] VERTEX Reports table created (15 min)
- [ ] All relationships configured
- [ ] All views created
- [ ] Sample data tested
- [ ] Connected to NEXUS backend

---

**Once complete, you'll have a complete financial management system integrated with all NEXUS systems!**

**Next Steps:** Configure automations, build frontend dashboard, set up exports.

---

**Documentation:** `VERTEX_AIRTABLE_SCHEMA.md`  
**Version:** 1.0  
**Last Updated:** January 17, 2026
