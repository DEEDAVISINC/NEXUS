# NEXUS AIRTABLE AUTOMATIONS - COMPLETE GUIDE

**Created:** January 21, 2026  
**Purpose:** Step-by-step guide for all Airtable automations across the entire NEXUS system

---

## 📋 TABLE OF CONTENTS

1. [Fulfillment System Automations](#fulfillment-system-automations) (8 automations)
2. [GPSS Opportunity Automations](#gpss-opportunity-automations) (5 automations)
3. [VERTEX Financial Automations](#vertex-financial-automations) (4 automations)
4. [ATLAS Project Automations](#atlas-project-automations) (3 automations)
5. [Supplier Management Automations](#supplier-management-automations) (2 automations)
6. [Subcontractor Management Automations](#subcontractor-management-automations) (4 automations)
7. [AI Recommendation Automations](#ai-recommendation-automations) (4 automations) ⭐ NEW
8. [Officer Outreach Automations](#officer-outreach-automations) (4 automations)
9. [Proposal Quality Automations](#proposal-quality-automations) (3 automations)
10. [LBPC Surplus Recovery Automations](#lbpc-surplus-recovery-automations) (3 automations)
11. [DDCSS Marketing Automations](#ddcss-marketing-automations) (2 automations)
12. [Cross-System Automations](#cross-system-automations) (3 automations)

**Total Automations:** 46 ⭐ UPDATED (includes AI Recommendation System)

---

## 🎯 AUTOMATION PRIORITY LEVELS

**🔴 CRITICAL (Set up first):**
- Must have for system to function properly
- Prevent revenue loss or client issues
- Set up within first week

**🟡 IMPORTANT (Set up within 2 weeks):**
- Significantly improve efficiency
- Prevent minor issues
- High ROI on time investment

**🟢 NICE TO HAVE (Set up when ready):**
- Quality of life improvements
- Advanced features
- Can wait until system is running smoothly

---

# FULFILLMENT SYSTEM AUTOMATIONS

## 1. 🔴 CRITICAL: Low Inventory Alert

**Priority:** CRITICAL  
**Table:** FULFILLMENT INVENTORY  
**Purpose:** Alert when inventory drops below reorder point

### Setup Instructions:

1. Go to **Automations** → **Create automation**
2. **Name:** "Low Inventory Alert"
3. **Trigger:** When record matches conditions
   - Table: `FULFILLMENT INVENTORY`
   - Conditions:
     - When `QUANTITY_ON_HAND` < `REORDER_POINT`
     - AND `STATUS` is not "Out of Stock"
4. **Action 1:** Update record
   - Table: `FULFILLMENT INVENTORY`
   - Record: Trigger record
   - Fields:
     - `STATUS` → "Low Stock"
5. **Action 2:** Send email
   - To: `your-email@deedavisinc.com`
   - Subject: `🟡 LOW INVENTORY: {PRODUCT_NAME}`
   - Body:
```
REORDER RECOMMENDED

Product: {PRODUCT_NAME}
SKU: {PRODUCT_SKU}
━━━━━━━━━━━━━━━━━━━━━━━━
Current Stock: {QUANTITY_ON_HAND} units
Reorder Point: {REORDER_POINT} units
Recommended Order: {REORDER_QUANTITY} units

Committed to Contracts: {QUANTITY_COMMITTED} units
Available: {QUANTITY_AVAILABLE} units
Active Contracts: {ACTIVE_CONTRACTS}

Supplier: {SUPPLIER}
Unit Cost: {UNIT_COST}
━━━━━━━━━━━━━━━━━━━━━━━━
ACTION NEEDED:
Create purchase order to restock inventory

View in Airtable:
[Link to record]
```
6. **Turn ON** the automation

---

## 2. 🔴 CRITICAL: Inventory Shortage Alert

**Priority:** CRITICAL  
**Table:** FULFILLMENT INVENTORY  
**Purpose:** Emergency alert when can't fulfill commitments

### Setup Instructions:

1. **Name:** "Critical Inventory Shortage"
2. **Trigger:** When record matches conditions
   - Table: `FULFILLMENT INVENTORY`
   - Conditions:
     - When `QUANTITY_AVAILABLE` < 0
     - OR `STATUS` is "Critical"
3. **Action 1:** Update record
   - Table: `FULFILLMENT INVENTORY`
   - Record: Trigger record
   - Fields:
     - `STATUS` → "Critical"
4. **Action 2:** Send email
   - To: `your-email@deedavisinc.com`
   - Subject: `🚨 CRITICAL: INVENTORY SHORTAGE - {PRODUCT_NAME}`
   - Body:
```
⚠️ CRITICAL INVENTORY ALERT ⚠️

Product: {PRODUCT_NAME}
SKU: {PRODUCT_SKU}
━━━━━━━━━━━━━━━━━━━━━━━━
SHORTAGE DETAILS:
On Hand: {QUANTITY_ON_HAND} units
Committed: {QUANTITY_COMMITTED} units
Available: {QUANTITY_AVAILABLE} units (NEGATIVE!)

Active Contracts: {ACTIVE_CONTRACTS}
━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ URGENT ACTION REQUIRED:
1. Create emergency purchase order
2. Contact supplier for expedited delivery
3. Review upcoming deliveries - may need to delay

Supplier: {SUPPLIER}
Recommended Order: {REORDER_QUANTITY} units minimum

View in Airtable:
[Link to record]
```
5. **Turn ON** the automation

---

## 3. 🔴 CRITICAL: Delivery Due in 7 Days

**Priority:** CRITICAL  
**Table:** FULFILLMENT DELIVERIES  
**Purpose:** Prepare for upcoming delivery

### Setup Instructions:

1. **Name:** "Delivery Reminder - 7 Days"
2. **Trigger:** When record matches conditions
   - Table: `FULFILLMENT DELIVERIES`
   - Conditions:
     - When `DUE_DATE` is within the next 7 days
     - AND `STATUS` is "Scheduled"
3. **Action:** Send email
   - To: `your-email@deedavisinc.com`
   - Subject: `📦 Delivery Due in 7 Days: {DELIVERY_ID}`
   - Body:
```
UPCOMING DELIVERY REMINDER

Delivery ID: {DELIVERY_ID}
Delivery #{DELIVERY_NUMBER}
━━━━━━━━━━━━━━━━━━━━━━━━
DELIVERY DETAILS:
Due Date: {DUE_DATE}
Quantity: {QUANTITY} units
Status: {STATUS}

Contract: [Link to CONTRACT]
━━━━━━━━━━━━━━━━━━━━━━━━
ACTION NEEDED:
1. Verify inventory is available
2. Prepare shipment
3. Confirm shipping carrier
4. Schedule pickup/drop-off

View in Airtable:
[Link to record]
```
4. **Turn ON** the automation

---

## 4. 🟡 IMPORTANT: Delivery Due Today

**Priority:** IMPORTANT  
**Table:** FULFILLMENT DELIVERIES  
**Purpose:** Same-day delivery alert

### Setup Instructions:

1. **Name:** "Delivery Due Today"
2. **Trigger:** When record matches conditions
   - Table: `FULFILLMENT DELIVERIES`
   - Conditions:
     - When `DUE_DATE` is today
     - AND `STATUS` is not "Delivered"
     - AND `STATUS` is not "Cancelled"
3. **Action:** Send email
   - To: `your-email@deedavisinc.com`
   - Subject: `🚚 DELIVERY DUE TODAY: {DELIVERY_ID}`
   - Body:
```
⏰ DELIVERY DUE TODAY

Delivery ID: {DELIVERY_ID}
━━━━━━━━━━━━━━━━━━━━━━━━
Due: TODAY ({DUE_DATE})
Quantity: {QUANTITY} units
Status: {STATUS}

Contract: [Link to CONTRACT]
━━━━━━━━━━━━━━━━━━━━━━━━
URGENT ACTION:
1. Ship immediately if not already sent
2. Update status to "In Transit"
3. Add tracking number
4. Notify client if delay expected

View in Airtable:
[Link to record]
```
4. **Turn ON** the automation

---

## 5. 🟡 IMPORTANT: Overdue Delivery Alert

**Priority:** IMPORTANT  
**Table:** FULFILLMENT DELIVERIES  
**Purpose:** Alert for late deliveries

### Setup Instructions:

1. **Name:** "Overdue Delivery Alert"
2. **Trigger:** When record matches conditions
   - Table: `FULFILLMENT DELIVERIES`
   - Conditions:
     - When `DUE_DATE` is in the past
     - AND `STATUS` is not "Delivered"
     - AND `STATUS` is not "Cancelled"
3. **Action 1:** Update record
   - Table: `FULFILLMENT DELIVERIES`
   - Record: Trigger record
   - Fields:
     - `STATUS` → "Late"
4. **Action 2:** Send email
   - To: `your-email@deedavisinc.com`
   - Subject: `⚠️ OVERDUE DELIVERY: {DELIVERY_ID}`
   - Body:
```
⚠️ LATE DELIVERY ALERT

Delivery ID: {DELIVERY_ID}
━━━━━━━━━━━━━━━━━━━━━━━━
Was Due: {DUE_DATE}
Current Status: {STATUS}
Days Overdue: [Calculate]

Contract: [Link to CONTRACT]
━━━━━━━━━━━━━━━━━━━━━━━━
URGENT ACTION REQUIRED:
1. Ship immediately
2. Contact client to apologize
3. Provide tracking info
4. Update delivery status
5. Document reason for delay

View in Airtable:
[Link to record]
```
5. **Turn ON** the automation

---

## 6. 🟢 Purchase Order Arriving Soon

**Priority:** NICE TO HAVE  
**Table:** FULFILLMENT PURCHASE ORDERS  
**Purpose:** Prepare to receive inventory

### Setup Instructions:

1. **Name:** "PO Arriving Soon"
2. **Trigger:** When record matches conditions
   - Table: `FULFILLMENT PURCHASE ORDERS`
   - Conditions:
     - When `EXPECTED_DELIVERY_DATE` is within the next 2 days
     - AND `STATUS` is "Ordered"
3. **Action:** Send email
   - To: `your-email@deedavisinc.com`
   - Subject: `📦 PO Arriving in 2 Days: {PO_NUMBER}`
   - Body:
```
PURCHASE ORDER ARRIVING SOON

PO Number: {PO_NUMBER}
━━━━━━━━━━━━━━━━━━━━━━━━
Expected: {EXPECTED_DELIVERY_DATE}
Supplier: {SUPPLIER}
Products: {PRODUCTS}
Quantity: {QUANTITY_ORDERED} units
Total Cost: {TOTAL_COST}
━━━━━━━━━━━━━━━━━━━━━━━━
ACTION NEEDED:
1. Prepare receiving area
2. Have inspection checklist ready
3. Clear space for storage
4. Be ready to update inventory

View in Airtable:
[Link to record]
```
4. **Turn ON** the automation

---

## 7. 🟢 Contract Completion Celebration

**Priority:** NICE TO HAVE  
**Table:** FULFILLMENT CONTRACTS  
**Purpose:** Celebrate and follow up on completed contracts

### Setup Instructions:

1. **Name:** "Contract Completed"
2. **Trigger:** When record matches conditions
   - Table: `FULFILLMENT CONTRACTS`
   - Conditions:
     - When `DELIVERIES_REMAINING` = 0
     - OR `STATUS` is "Completed"
3. **Action 1:** Update record
   - Table: `FULFILLMENT CONTRACTS`
   - Record: Trigger record
   - Fields:
     - `STATUS` → "Completed"
4. **Action 2:** Send email
   - To: `your-email@deedavisinc.com`
   - Subject: `🎉 CONTRACT COMPLETED: {CONTRACT_NAME}`
   - Body:
```
🎉 CONGRATULATIONS! CONTRACT COMPLETED 🎉

Contract: {CONTRACT_NAME}
Client: {CLIENT_NAME}
━━━━━━━━━━━━━━━━━━━━━━━━
CONTRACT SUMMARY:
Total Deliveries: {TOTAL_DELIVERIES} ✅
Product: {PRODUCT}
Total Quantity: {TOTAL_QUANTITY} units

FINANCIAL SUMMARY:
Total Value: {TOTAL_VALUE}
Unit Price: {UNIT_PRICE}
Unit Cost: {SUPPLIER_UNIT_COST}
Margin per Unit: {MARGIN_PER_UNIT}
Total Profit: ${MARGIN_PER_UNIT} × {TOTAL_QUANTITY}

Duration: {START_DATE} to {END_DATE}
━━━━━━━━━━━━━━━━━━━━━━━━
NEXT STEPS:
1. ✅ Follow up with client for testimonial
2. ✅ Request renewal or additional opportunities
3. ✅ Review performance metrics
4. ✅ Document lessons learned
5. ✅ Archive contract records

View in Airtable:
[Link to record]
```
5. **Turn ON** the automation

---

## 8. 🟢 Auto-Calculate Contract Progress

**Priority:** NICE TO HAVE  
**Table:** FULFILLMENT DELIVERIES  
**Purpose:** Update contract when delivery is marked delivered

### Setup Instructions:

1. **Name:** "Update Contract Progress"
2. **Trigger:** When record matches conditions
   - Table: `FULFILLMENT DELIVERIES`
   - Conditions:
     - When `STATUS` changes to "Delivered"
3. **Action 1:** Find records (get linked contract)
   - Table: `FULFILLMENT CONTRACTS`
   - Conditions:
     - Where record ID is in `CONTRACT` field of trigger
4. **Action 2:** Update record
   - Table: `FULFILLMENT CONTRACTS`
   - Record: Result from previous step
   - Fields:
     - `DELIVERIES_COMPLETED` → Add 1
     - `DELIVERIES_REMAINING` → Subtract 1
5. **Turn ON** the automation

---

# GPSS OPPORTUNITY AUTOMATIONS

## 9. 🔴 CRITICAL: High Priority Opportunity Alert

**Priority:** CRITICAL  
**Table:** GPSS OPPORTUNITIES  
**Purpose:** Alert for high-value opportunities with approaching deadlines

### Setup Instructions:

1. **Name:** "High Priority Opportunity Alert"
2. **Trigger:** When record created or matches conditions
   - Table: `GPSS OPPORTUNITIES`
   - Conditions:
     - When `PRIORITY` is "High"
     - OR `ESTIMATED_VALUE` > 100000
     - AND `RESPONSE_DEADLINE` is within the next 14 days
3. **Action:** Send email
   - To: `your-email@deedavisinc.com`
   - Subject: `🎯 HIGH PRIORITY: {TITLE}`
   - Body:
```
🎯 HIGH PRIORITY OPPORTUNITY

Title: {TITLE}
Solicitation #: {SOLICITATION_NUMBER}
━━━━━━━━━━━━━━━━━━━━━━━━
OPPORTUNITY DETAILS:
Agency: {AGENCY}
Estimated Value: {ESTIMATED_VALUE}
Priority: {PRIORITY}
Win Probability: {WIN_PROBABILITY}

Set-Aside: {SET_ASIDE}
NAICS: {NAICS_CODE}
━━━━━━━━━━━━━━━━━━━━━━━━
⏰ DEADLINE:
Response Due: {RESPONSE_DEADLINE}
Days Remaining: [Calculate]
━━━━━━━━━━━━━━━━━━━━━━━━
IMMEDIATE ACTIONS:
1. Review RFP document
2. Assess capabilities & qualifications
3. Find suppliers (if product-based)
4. Begin proposal development
5. Mark decision: Bid or Pass

View in Airtable:
[Link to record]
```
4. **Turn ON** the automation

---

## 10. 🔴 CRITICAL: Proposal Deadline Approaching

**Priority:** CRITICAL  
**Table:** GPSS OPPORTUNITIES  
**Purpose:** Final reminder before deadline

### Setup Instructions:

1. **Name:** "Proposal Deadline - 48 Hours"
2. **Trigger:** When record matches conditions
   - Table: `GPSS OPPORTUNITIES`
   - Conditions:
     - When `RESPONSE_DEADLINE` is within the next 2 days
     - AND `STATUS` is not "Submitted"
     - AND `STATUS` is not "Not Pursuing"
     - AND `BID_DECISION` is "Yes - Bid"
3. **Action:** Send email
   - To: `your-email@deedavisinc.com`
   - Subject: `🚨 DEADLINE IN 48 HRS: {TITLE}`
   - Body:
```
⚠️ URGENT: PROPOSAL DEADLINE IN 48 HOURS

Title: {TITLE}
Solicitation #: {SOLICITATION_NUMBER}
━━━━━━━━━━━━━━━━━━━━━━━━
⏰ DUE: {RESPONSE_DEADLINE}
Status: {STATUS}
━━━━━━━━━━━━━━━━━━━━━━━━
🚨 CRITICAL ACTIONS:
1. Finalize proposal (ProposalBio™ quality check)
2. Get all pricing locked in
3. Review compliance checklist
4. Prepare submission package
5. Submit BEFORE deadline

Estimated Value: {ESTIMATED_VALUE}
This is a high-value opportunity!

View in Airtable:
[Link to record]
```
4. **Turn ON** the automation

---

## 11. 🟡 IMPORTANT: Opportunity Status Change

**Priority:** IMPORTANT  
**Table:** GPSS OPPORTUNITIES  
**Purpose:** Track when status changes to "Won"

### Setup Instructions:

1. **Name:** "Opportunity Won - Celebration"
2. **Trigger:** When record matches conditions
   - Table: `GPSS OPPORTUNITIES`
   - Conditions:
     - When `STATUS` changes to "Won"
3. **Action 1:** Send email
   - To: `your-email@deedavisinc.com`
   - Subject: `🎉 CONTRACT WON: {TITLE}`
   - Body:
```
🎉🎉🎉 CONGRATULATIONS! 🎉🎉🎉

You won the contract!

Title: {TITLE}
Solicitation #: {SOLICITATION_NUMBER}
Client: {AGENCY}
Value: {ESTIMATED_VALUE}
━━━━━━━━━━━━━━━━━━━━━━━━
NEXT STEPS:
1. ✅ Review contract terms carefully
2. ✅ Set up fulfillment contract (if product-based)
3. ✅ Create ATLAS project (if service-based)
4. ✅ Order initial inventory (if needed)
5. ✅ Schedule kickoff meeting with client
6. ✅ Update vendor portal if applicable

View in Airtable:
[Link to record]
```
4. **Action 2:** Create linked record (if product-based)
   - Table: `FULFILLMENT CONTRACTS`
   - Fields to map from opportunity:
     - `CONTRACT_NAME` → {TITLE}
     - `CLIENT_NAME` → {AGENCY}
     - `TOTAL_VALUE` → {ESTIMATED_VALUE}
5. **Turn ON** the automation

---

## 12. 🟢 Weekly Opportunity Digest

**Priority:** NICE TO HAVE  
**Table:** GPSS OPPORTUNITIES  
**Purpose:** Weekly summary of all active opportunities

### Setup Instructions:

1. **Name:** "Weekly Opportunity Digest"
2. **Trigger:** At a scheduled time
   - Frequency: Weekly
   - Day: Monday
   - Time: 8:00 AM
3. **Action 1:** Find records
   - Table: `GPSS OPPORTUNITIES`
   - Conditions:
     - Where `STATUS` is "New" OR "Under Review" OR "Proposal In Progress"
     - AND `RESPONSE_DEADLINE` is in the future
4. **Action 2:** Send email
   - To: `your-email@deedavisinc.com`
   - Subject: `📊 Weekly Opportunity Digest - [Date]`
   - Body:
```
📊 WEEKLY OPPORTUNITY DIGEST
Week of [Date]
━━━━━━━━━━━━━━━━━━━━━━━━
ACTIVE OPPORTUNITIES: [Count]

[For each opportunity found:]
━━━━━━━━━━━━━━━━━━━━━━━━
{TITLE}
Value: {ESTIMATED_VALUE}
Due: {RESPONSE_DEADLINE}
Priority: {PRIORITY}
Status: {STATUS}

[End loop]
━━━━━━━━━━━━━━━━━━━━━━━━
SUMMARY:
Total Est. Value: [Sum of all]
High Priority: [Count]
Due This Week: [Count]
Due Next Week: [Count]

View all opportunities in Airtable
```
5. **Turn ON** the automation

---

## 13. 🟢 Auto-Tag Opportunities by Value

**Priority:** NICE TO HAVE  
**Table:** GPSS OPPORTUNITIES  
**Purpose:** Automatically categorize by contract size

### Setup Instructions:

1. **Name:** "Auto-Tag by Value"
2. **Trigger:** When record created or updated
   - Table: `GPSS OPPORTUNITIES`
   - Conditions:
     - When `ESTIMATED_VALUE` changes
3. **Action:** Update record
   - Table: `GPSS OPPORTUNITIES`
   - Record: Trigger record
   - Fields (use conditional logic):
     - If `ESTIMATED_VALUE` > 1000000: Add tag "Large Contract"
     - If `ESTIMATED_VALUE` 250000-999999: Add tag "Medium Contract"
     - If `ESTIMATED_VALUE` < 250000: Add tag "Small Contract"
4. **Turn ON** the automation

---

# VERTEX FINANCIAL AUTOMATIONS

## 14. 🔴 CRITICAL: Invoice Overdue Alert

**Priority:** CRITICAL  
**Table:** VERTEX INVOICES  
**Purpose:** Alert when payment is late

### Setup Instructions:

1. **Name:** "Invoice Overdue Alert"
2. **Trigger:** When record matches conditions
   - Table: `VERTEX INVOICES`
   - Conditions:
     - When `DUE_DATE` is in the past
     - AND `STATUS` is not "Paid"
     - AND `STATUS` is not "Cancelled"
3. **Action 1:** Update record
   - Table: `VERTEX INVOICES`
   - Record: Trigger record
   - Fields:
     - `STATUS` → "Overdue"
4. **Action 2:** Send email
   - To: `your-email@deedavisinc.com`
   - Subject: `💰 OVERDUE INVOICE: {CLIENT_NAME} - ${INVOICE_AMOUNT}`
   - Body:
```
⚠️ INVOICE OVERDUE

Client: {CLIENT_NAME}
Invoice Amount: {INVOICE_AMOUNT}
━━━━━━━━━━━━━━━━━━━━━━━━
PAYMENT DETAILS:
Invoice Date: {INVOICE_DATE}
Due Date: {DUE_DATE}
Days Overdue: [Calculate]
Status: Overdue

Description: {DESCRIPTION}
━━━━━━━━━━━━━━━━━━━━━━━━
ACTION REQUIRED:
1. Send payment reminder to client
2. Follow up via phone
3. Escalate if > 30 days overdue
4. Update status when paid

View in Airtable:
[Link to record]
```
5. **Turn ON** the automation

---

## 15. 🟡 IMPORTANT: Invoice Due Soon

**Priority:** IMPORTANT  
**Table:** VERTEX INVOICES  
**Purpose:** Remind to follow up before due date

### Setup Instructions:

1. **Name:** "Invoice Due in 5 Days"
2. **Trigger:** When record matches conditions
   - Table: `VERTEX INVOICES`
   - Conditions:
     - When `DUE_DATE` is within the next 5 days
     - AND `STATUS` is "Sent"
3. **Action:** Send email
   - To: `your-email@deedavisinc.com`
   - Subject: `⏰ Invoice Due Soon: {CLIENT_NAME} - ${INVOICE_AMOUNT}`
   - Body:
```
INVOICE DUE IN 5 DAYS

Client: {CLIENT_NAME}
Amount: {INVOICE_AMOUNT}
Due Date: {DUE_DATE}
━━━━━━━━━━━━━━━━━━━━━━━━
RECOMMENDED ACTION:
Send friendly payment reminder to client

"Just a reminder that invoice #{ID} for ${INVOICE_AMOUNT} 
is due on {DUE_DATE}. Please let me know if you have 
any questions."

View in Airtable:
[Link to record]
```
4. **Turn ON** the automation

---

## 16. 🟡 IMPORTANT: Expense Payment Due

**Priority:** IMPORTANT  
**Table:** VERTEX EXPENSES  
**Purpose:** Remind to pay suppliers/vendors

### Setup Instructions:

1. **Name:** "Expense Payment Due"
2. **Trigger:** When record matches conditions
   - Table: `VERTEX EXPENSES`
   - Conditions:
     - When record has a payment due date
     - AND due date is within the next 3 days
     - AND `STATUS` is not "Paid"
3. **Action:** Send email
   - To: `your-email@deedavisinc.com`
   - Subject: `💳 Payment Due: {EXPENSE_NAME} - ${AMOUNT}`
   - Body:
```
EXPENSE PAYMENT DUE SOON

Expense: {EXPENSE_NAME}
Amount: {AMOUNT}
Due: [Payment due date]
━━━━━━━━━━━━━━━━━━━━━━━━
DETAILS:
Category: {CATEGORY}
Description: {DESCRIPTION}
Vendor: [If applicable]
━━━━━━━━━━━━━━━━━━━━━━━━
ACTION:
Process payment before due date

View in Airtable:
[Link to record]
```
4. **Turn ON** the automation

---

## 17. 🟢 Monthly Financial Summary

**Priority:** NICE TO HAVE  
**Table:** Multiple (VERTEX INVOICES, VERTEX EXPENSES)  
**Purpose:** Monthly revenue and expense report

### Setup Instructions:

1. **Name:** "Monthly Financial Summary"
2. **Trigger:** At a scheduled time
   - Frequency: Monthly
   - Day: 1st of month
   - Time: 9:00 AM
3. **Action 1:** Find records (invoices)
   - Table: `VERTEX INVOICES`
   - Conditions:
     - Where `INVOICE_DATE` is last month
4. **Action 2:** Find records (expenses)
   - Table: `VERTEX EXPENSES`
   - Conditions:
     - Where `DATE` is last month
5. **Action 3:** Send email
   - To: `your-email@deedavisinc.com`
   - Subject: `📊 Monthly Financial Summary - [Month Year]`
   - Body:
```
📊 FINANCIAL SUMMARY
[Month Year]
━━━━━━━━━━━━━━━━━━━━━━━━
REVENUE:
Total Invoiced: [Sum of invoices]
Paid: [Sum where STATUS = Paid]
Outstanding: [Sum where STATUS != Paid]

EXPENSES:
Total Expenses: [Sum of expenses]
By Category:
  - COGS: [Sum]
  - Operations: [Sum]
  - Marketing: [Sum]
  - Other: [Sum]

NET PROFIT: [Revenue - Expenses]
Profit Margin: [Calculate %]
━━━━━━━━━━━━━━━━━━━━━━━━
OUTSTANDING INVOICES: [Count]
OVERDUE INVOICES: [Count]

View VERTEX Dashboard in Airtable
```
6. **Turn ON** the automation

---

# ATLAS PROJECT AUTOMATIONS

## 18. 🟡 IMPORTANT: Project Deadline Approaching

**Priority:** IMPORTANT  
**Table:** ATLAS PROJECTS  
**Purpose:** Alert when project due date approaching

### Setup Instructions:

1. **Name:** "Project Deadline - 7 Days"
2. **Trigger:** When record matches conditions
   - Table: `ATLAS PROJECTS`
   - Conditions:
     - When `DUE_DATE` is within the next 7 days
     - AND `STATUS` is not "Completed"
     - AND `STATUS` is not "Cancelled"
3. **Action:** Send email
   - To: `your-email@deedavisinc.com`
   - Subject: `⏰ Project Due in 7 Days: {PROJECT_NAME}`
   - Body:
```
PROJECT DEADLINE APPROACHING

Project: {PROJECT_NAME}
Client: {CLIENT_NAME}
Due: {DUE_DATE} (7 days)
━━━━━━━━━━━━━━━━━━━━━━━━
STATUS:
Current Status: {STATUS}
Progress: {PROGRESS_PERCENTAGE}%
Priority: {PRIORITY}

Budget: {BUDGET}
Budget Used: {BUDGET_USED}
Remaining: {BUDGET} - {BUDGET_USED}
━━━━━━━━━━━━━━━━━━━━━━━━
ACTIONS NEEDED:
1. Review project status
2. Check all deliverables
3. Coordinate with team/subs
4. Schedule final review
5. Prepare for delivery

View in Airtable:
[Link to record]
```
4. **Turn ON** the automation

---

## 19. 🟢 Task Overdue Alert

**Priority:** NICE TO HAVE  
**Table:** ATLAS TASKS  
**Purpose:** Alert for overdue tasks

### Setup Instructions:

1. **Name:** "Task Overdue Alert"
2. **Trigger:** When record matches conditions
   - Table: `ATLAS TASKS`
   - Conditions:
     - When `DUE_DATE` is in the past
     - AND `STATUS` is not "Done"
     - AND `STATUS` is not "Cancelled"
3. **Action:** Send email
   - To: `your-email@deedavisinc.com`
   - Subject: `⚠️ Overdue Task: {TASK_NAME}`
   - Body:
```
TASK OVERDUE

Task: {TASK_NAME}
Project: [Link to PROJECT]
━━━━━━━━━━━━━━━━━━━━━━━━
Was Due: {DUE_DATE}
Status: {STATUS}
Priority: {PRIORITY}
Assigned To: {ASSIGNED_TO}
━━━━━━━━━━━━━━━━━━━━━━━━
ACTION:
Complete task and update status

View in Airtable:
[Link to record]
```
4. **Turn ON** the automation

---

## 20. 🟢 Project Status Report

**Priority:** NICE TO HAVE  
**Table:** ATLAS PROJECTS  
**Purpose:** Weekly project status update

### Setup Instructions:

1. **Name:** "Weekly Project Status"
2. **Trigger:** At a scheduled time
   - Frequency: Weekly
   - Day: Friday
   - Time: 4:00 PM
3. **Action 1:** Find records
   - Table: `ATLAS PROJECTS`
   - Conditions:
     - Where `STATUS` is "In Progress" OR "At Risk"
4. **Action 2:** Send email
   - To: `your-email@deedavisinc.com`
   - Subject: `📋 Weekly Project Status - [Date]`
   - Body:
```
📋 WEEKLY PROJECT STATUS
Week ending [Date]
━━━━━━━━━━━━━━━━━━━━━━━━
ACTIVE PROJECTS: [Count]

[For each project:]
━━━━━━━━━━━━━━━━━━━━━━━━
{PROJECT_NAME}
Client: {CLIENT_NAME}
Status: {STATUS}
Progress: {PROGRESS_PERCENTAGE}%
Due: {DUE_DATE}
At Risk: [Yes/No based on status]

[End loop]
━━━━━━━━━━━━━━━━━━━━━━━━
SUMMARY:
On Track: [Count]
At Risk: [Count]
Due Next Week: [Count]

View all projects in Airtable
```
5. **Turn ON** the automation

---

# SUPPLIER MANAGEMENT AUTOMATIONS

## 21. 🟡 IMPORTANT: New Supplier Added

**Priority:** IMPORTANT  
**Table:** GPSS SUPPLIERS  
**Purpose:** Track and verify new suppliers

### Setup Instructions:

1. **Name:** "New Supplier Added"
2. **Trigger:** When record created
   - Table: `GPSS SUPPLIERS`
3. **Action:** Send email
   - To: `your-email@deedavisinc.com`
   - Subject: `🏢 New Supplier Added: {COMPANY_NAME}`
   - Body:
```
NEW SUPPLIER ADDED TO DATABASE

Company: {COMPANY_NAME}
━━━━━━━━━━━━━━━━━━━━━━━━
CONTACT INFO:
Contact: {CONTACT_NAME}
Email: {EMAIL}
Phone: {PHONE}
Website: {WEBSITE}

BUSINESS INFO:
Category: {CATEGORY}
GSA Contract: {HAS_GSA_CONTRACT}
Payment Terms: {PAYMENT_TERMS}
━━━━━━━━━━━━━━━━━━━━━━━━
NEXT STEPS:
1. ✅ Verify company legitimacy
2. ✅ Request W-9 and insurance
3. ✅ Negotiate pricing/terms
4. ✅ Add to approved vendor list
5. ✅ Test with small order

View in Airtable:
[Link to record]
```
4. **Turn ON** the automation

---

## 22. 🟢 Supplier Performance Alert

**Priority:** NICE TO HAVE  
**Table:** GPSS SUPPLIERS  
**Purpose:** Alert when supplier rating drops

### Setup Instructions:

1. **Name:** "Supplier Performance Issue"
2. **Trigger:** When record matches conditions
   - Table: `GPSS SUPPLIERS`
   - Conditions:
     - When `RATING` changes
     - AND `RATING` < 3
3. **Action:** Send email
   - To: `your-email@deedavisinc.com`
   - Subject: `⚠️ Supplier Performance Issue: {COMPANY_NAME}`
   - Body:
```
SUPPLIER PERFORMANCE ALERT

Supplier: {COMPANY_NAME}
Rating: {RATING} ⭐ (Below Standard)
━━━━━━━━━━━━━━━━━━━━━━━━
PERFORMANCE METRICS:
Current Rating: {RATING}/5
[Other metrics if tracked]

RECOMMENDED ACTIONS:
1. Review recent orders for issues
2. Contact supplier about concerns
3. Consider finding alternative supplier
4. Document performance issues
5. Re-evaluate vendor status

View in Airtable:
[Link to record]
```
4. **Turn ON** the automation

---

# SUBCONTRACTOR MANAGEMENT AUTOMATIONS

## 23. 🟡 IMPORTANT: Quote Response Received

**Priority:** IMPORTANT  
**Table:** GPSS SUBCONTRACTOR QUOTES  
**Purpose:** Alert when subcontractor responds with quote

### Setup Instructions:

1. **Name:** "Subcontractor Quote Received"
2. **Trigger:** When record matches conditions
   - Table: `GPSS SUBCONTRACTOR QUOTES`
   - Conditions:
     - When `RESPONSE TEXT` is not empty
     - AND `QUOTE AMOUNT` is not empty
     - AND `STATUS` changes to "Quote Received"
3. **Action:** Send email
   - To: `your-email@deedavisinc.com`
   - Subject: `📬 Quote Received: {SUBCONTRACTOR} - {OPPORTUNITY}`
   - Body:
```
SUBCONTRACTOR QUOTE RECEIVED

Opportunity: {OPPORTUNITY}
Subcontractor: {SUBCONTRACTOR}
━━━━━━━━━━━━━━━━━━━━━━━━
QUOTE DETAILS:
Quote Amount: {QUOTE AMOUNT}
Response Time: {RESPONSE TIME (DAYS)} days

NEXT STEPS:
1. ✅ Review quote details in RESPONSE TEXT field
2. ✅ Run AI scoring (click "Score All Quotes")
3. ✅ Compare with other quotes
4. ✅ Select best quote and calculate markup
5. ✅ Submit final bid

View Quote in Airtable:
[Link to record]
```
4. **Turn ON** the automation

---

## 24. 🔴 CRITICAL: High-Score Quote Alert

**Priority:** CRITICAL  
**Table:** GPSS SUBCONTRACTOR QUOTES  
**Purpose:** Alert when AI scores a quote highly (top candidate)

### Setup Instructions:

1. **Name:** "High-Score Subcontractor Quote"
2. **Trigger:** When record matches conditions
   - Table: `GPSS SUBCONTRACTOR QUOTES`
   - Conditions:
     - When `AI SCORE` >= 85
     - AND `RECOMMENDATION` = "Recommend"
3. **Action:** Send email
   - To: `your-email@deedavisinc.com`
   - Subject: `⭐ TOP QUOTE: {SUBCONTRACTOR} - Score: {AI SCORE}/100`
   - Body:
```
⭐ HIGH-QUALITY QUOTE RECEIVED

Opportunity: {OPPORTUNITY}
Subcontractor: {SUBCONTRACTOR}
━━━━━━━━━━━━━━━━━━━━━━━━
AI ANALYSIS:
Score: {AI SCORE}/100
Recommendation: {RECOMMENDATION}

Quote Amount: {QUOTE AMOUNT}
Response Time: {RESPONSE TIME (DAYS)} days

AI Reasoning:
{SCORE REASONING}
━━━━━━━━━━━━━━━━━━━━━━━━
SUGGESTED ACTION:
This is a top-rated quote. Consider selecting and 
calculating your markup to prepare final bid.

View in Airtable:
[Link to record]
```
4. **Turn ON** the automation

---

## 25. 🟡 IMPORTANT: RFQ Overdue Alert

**Priority:** IMPORTANT  
**Table:** GPSS SUBCONTRACTOR QUOTES  
**Purpose:** Alert when subcontractor hasn't responded by due date

### Setup Instructions:

1. **Name:** "Subcontractor Quote Overdue"
2. **Trigger:** When record matches conditions
   - Table: `GPSS SUBCONTRACTOR QUOTES`
   - Conditions:
     - When `QUOTE DUE DATE` is in the past
     - AND `STATUS` = "RFQ Sent"
     - AND `RESPONSE TEXT` is empty
3. **Action 1:** Update record
   - Table: `GPSS SUBCONTRACTOR QUOTES`
   - Record: Trigger record
   - Fields:
     - `STATUS` → "Overdue"
4. **Action 2:** Send email
   - To: `your-email@deedavisinc.com`
   - Subject: `⏰ Quote Overdue: {SUBCONTRACTOR} - {OPPORTUNITY}`
   - Body:
```
⏰ SUBCONTRACTOR QUOTE OVERDUE

Opportunity: {OPPORTUNITY}
Subcontractor: {SUBCONTRACTOR}
Contact: {SUBCONTRACTOR EMAIL}
━━━━━━━━━━━━━━━━━━━━━━━━
RFQ DETAILS:
RFQ Sent: {RFQ SENT DATE}
Due Date: {QUOTE DUE DATE}
Days Overdue: [Calculate]

RECOMMENDED ACTION:
1. Follow up via phone/email
2. Ask for status update
3. Offer extension if needed
4. OR move to backup subcontractor

Other quotes for this opportunity:
[View all quotes for this opportunity]

View in Airtable:
[Link to record]
```
5. **Turn ON** the automation

---

## 26. 🟢 New Subcontractor Added

**Priority:** NICE TO HAVE  
**Table:** GPSS SUBCONTRACTORS  
**Purpose:** Track new subcontractors found

### Setup Instructions:

1. **Name:** "New Subcontractor Added"
2. **Trigger:** When record created
   - Table: `GPSS SUBCONTRACTORS`
   - Conditions:
     - When `DISCOVERED BY` = "NEXUS Auto-Mining"
3. **Action:** Send email
   - To: `your-email@deedavisinc.com`
   - Subject: `🏢 New Subcontractor Found: {COMPANY NAME} - {CITY}, {STATE}`
   - Body:
```
NEW SUBCONTRACTOR DISCOVERED

Company: {COMPANY NAME}
Service: {SERVICE TYPE}
Location: {CITY}, {STATE}
━━━━━━━━━━━━━━━━━━━━━━━━
CONTACT INFO:
Email: {EMAIL}
Phone: {PHONE}
Website: {WEBSITE}

Discovery:
Method: {DISCOVERY METHOD}
Date: {DISCOVERY DATE}
Source: {SOURCE NOTES}
━━━━━━━━━━━━━━━━━━━━━━━━
NEXT STEPS (when you need them):
1. Review their website/capabilities
2. Send RFQ when opportunity arises
3. Build relationship for future work
4. Track response quality and pricing

View in Airtable:
[Link to record]
```
4. **Turn ON** the automation

---

# AI RECOMMENDATION AUTOMATIONS

## 27. 🟡 IMPORTANT: New AI Recommendation Alert

**Priority:** IMPORTANT  
**Table:** AI RECOMMENDATIONS  
**Purpose:** Notify you when AI creates a new recommendation for your review

### Setup Instructions:

1. **Name:** "New AI Recommendation Alert"
2. **Trigger:** When record created
   - Table: `AI RECOMMENDATIONS`
3. **Condition:** Only run when
   - `STATUS` = "Pending Approval"
4. **Action:** Send email
   - To: `your-email@deedavisinc.com`
   - Subject: `🤖 AI RECOMMENDATION: {TYPE}`
   - Body:
```
NEW AI RECOMMENDATION READY FOR YOUR REVIEW

Type: {TYPE}
Opportunity: {OPPORTUNITY}
━━━━━━━━━━━━━━━━━━━━━━━━
AI RECOMMENDATION:
{RECOMMENDATION}

CONFIDENCE: {CONFIDENCE}%

REASONING:
{REASONING}
━━━━━━━━━━━━━━━━━━━━━━━━
ACTION NEEDED:
Review and approve/deny this recommendation

View in Airtable:
[Link to record]
```
5. **Turn ON** the automation

---

## 28. 🟡 IMPORTANT: High Confidence Recommendation Alert

**Priority:** IMPORTANT  
**Table:** AI RECOMMENDATIONS  
**Purpose:** Fast-track high-confidence recommendations (90%+)

### Setup Instructions:

1. **Name:** "High Confidence AI Recommendation"
2. **Trigger:** When record created
   - Table: `AI RECOMMENDATIONS`
3. **Condition:** Only run when
   - `CONFIDENCE` ≥ 90
   - AND `STATUS` = "Pending Approval"
4. **Action:** Send email
   - To: `your-email@deedavisinc.com`
   - Subject: `⚡ HIGH CONFIDENCE ({CONFIDENCE}%): {TYPE}`
   - Body:
```
HIGH CONFIDENCE AI RECOMMENDATION

Type: {TYPE}
Confidence: {CONFIDENCE}% ⭐ (Very High)
━━━━━━━━━━━━━━━━━━━━━━━━
AI RECOMMENDATION:
{RECOMMENDATION}

REASONING:
{REASONING}
━━━━━━━━━━━━━━━━━━━━━━━━
WHY HIGH CONFIDENCE:
AI is very confident in this recommendation.
Quick review recommended - this is likely the right choice.

QUICK ACTIONS:
✅ Approve if reasoning looks good
❌ Deny if you see issues
📝 Modify if adjustment needed

View in Airtable:
[Link to record]
```
5. **Turn ON** the automation

---

## 29. 🟢 NICE TO HAVE: Low Confidence Recommendation Alert

**Priority:** NICE TO HAVE  
**Table:** AI RECOMMENDATIONS  
**Purpose:** Flag low-confidence recommendations for careful review

### Setup Instructions:

1. **Name:** "Low Confidence AI Recommendation"
2. **Trigger:** When record created
   - Table: `AI RECOMMENDATIONS`
3. **Condition:** Only run when
   - `CONFIDENCE` < 70
   - AND `STATUS` = "Pending Approval"
4. **Action:** Send email
   - To: `your-email@deedavisinc.com`
   - Subject: `⚠️ LOW CONFIDENCE ({CONFIDENCE}%): {TYPE}`
   - Body:
```
LOW CONFIDENCE AI RECOMMENDATION

Type: {TYPE}
Confidence: {CONFIDENCE}% ⚠️ (Uncertain)
━━━━━━━━━━━━━━━━━━━━━━━━
AI RECOMMENDATION:
{RECOMMENDATION}

REASONING:
{REASONING}
━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ CAUTION:
AI is uncertain about this recommendation.
Deep review recommended before deciding.

SUGGESTED ACTIONS:
📊 Review all available options
🔍 Verify AI's reasoning carefully
💭 Use your expertise to decide
❓ Request more information if needed

View in Airtable:
[Link to record]
```
5. **Turn ON** the automation

---

## 30. 🟢 NICE TO HAVE: Pending Decision Reminder

**Priority:** NICE TO HAVE  
**Table:** AI RECOMMENDATIONS  
**Purpose:** Remind you of pending decisions after 24 hours

### Setup Instructions:

1. **Name:** "Pending AI Decision Reminder"
2. **Trigger:** When record matches conditions
   - Table: `AI RECOMMENDATIONS`
   - Conditions:
     - When `STATUS` = "Pending Approval"
     - AND `CREATED` was "24 hours ago"
3. **Action:** Send email
   - To: `your-email@deedavisinc.com`
   - Subject: `⏰ REMINDER: Pending AI Recommendation`
   - Body:
```
PENDING AI RECOMMENDATION (24 HOURS)

Type: {TYPE}
Opportunity: {OPPORTUNITY}
Created: {CREATED}
━━━━━━━━━━━━━━━━━━━━━━━━
AI RECOMMENDATION:
{RECOMMENDATION}

Confidence: {CONFIDENCE}%
━━━━━━━━━━━━━━━━━━━━━━━━
REMINDER:
This recommendation has been pending for 24 hours.
Please review and make a decision.

The system is waiting for your approval/denial
to proceed with this opportunity.

View in Airtable:
[Link to record]
```
4. **Turn ON** the automation

---

# OFFICER OUTREACH AUTOMATIONS

## 31. 🔴 CRITICAL: Follow-Up Reminder

**Priority:** CRITICAL  
**Table:** Officer Outreach Tracking  
**Purpose:** Remind to follow up with officers who haven't responded

### Setup Instructions:

1. **Name:** "Officer Outreach Follow-Up Reminder"
2. **Trigger:** When record matches conditions
   - Table: `Officer Outreach Tracking`
   - Conditions:
     - When `Follow-up Date` is today or in the past
     - AND `Status` is "Sent"
     - AND `Response Received` is not checked
3. **Action 1:** Update record
   - Table: `Officer Outreach Tracking`
   - Record: Trigger record
   - Fields:
     - `Status` → "Follow-up Needed"
4. **Action 2:** Send email
   - To: `your-email@deedavisinc.com`
   - Subject: `📬 Follow-Up Needed: {Officer Name} - {Agency}`
   - Body:
```
⏰ FOLLOW-UP REMINDER

Officer: {Officer Name}
Email: {Officer Email}
Agency: {Agency}
━━━━━━━━━━━━━━━━━━━━━━━━
OUTREACH DETAILS:
Original Opportunity: {Opportunity Title}
Solicitation #: {Solicitation Number}
Letter Sent: {Date Sent}
Days Since Sent: [Calculate from Date Sent]
Follow-up Due: {Follow-up Date}
━━━━━━━━━━━━━━━━━━━━━━━━
RECOMMENDED FOLLOW-UP:

Subject: "Following up - Dee Davis, Inc. capabilities"

"Hi {Officer Name},

I wanted to follow up on my email from {Date Sent} regarding 
{Opportunity Title} (Solicitation #{Solicitation Number}).

While I understand you've already awarded that contract, I'd 
appreciate the opportunity to:

1. Be added to your vendor list for future opportunities
2. Share our capability statement
3. Learn about upcoming requirements

Would you have 10 minutes for a brief call?

Best regards,
Dee Davis"

━━━━━━━━━━━━━━━━━━━━━━━━
ACTION:
Send follow-up email and update status

View in Airtable:
[Link to record]
```
5. **Turn ON** the automation

---

## 28. 🟡 IMPORTANT: Response Received - Next Steps

**Priority:** IMPORTANT  
**Table:** Officer Outreach Tracking  
**Purpose:** Celebrate responses and guide next actions

### Setup Instructions:

1. **Name:** "Officer Response Received"
2. **Trigger:** When record matches conditions
   - Table: `Officer Outreach Tracking`
   - Conditions:
     - When `Response Received` checkbox is checked
3. **Action 1:** Update record
   - Table: `Officer Outreach Tracking`
   - Record: Trigger record
   - Fields:
     - `Status` → "Responded"
     - `Response Date` → TODAY()
4. **Action 2:** Send email
   - To: `your-email@deedavisinc.com`
   - Subject: `🎉 Officer Responded: {Officer Name} - {Agency}`
   - Body:
```
🎉 SUCCESS! OFFICER RESPONDED

Officer: {Officer Name}
Email: {Officer Email}
Agency: {Agency}
━━━━━━━━━━━━━━━━━━━━━━━━
Response Date: {Response Date}
Days to Response: [Calculate]
Response Notes: {Response Notes}
━━━━━━━━━━━━━━━━━━━━━━━━
NEXT STEPS:
1. ✅ Review their response in detail
2. ✅ Ask to be added to vendor list
3. ✅ Send capability statement if requested
4. ✅ Request information on upcoming opportunities
5. ✅ Schedule follow-up call if appropriate
6. ✅ Add to CRM for ongoing relationship

Priority: {Priority}

View in Airtable:
[Link to record]
```
5. **Turn ON** the automation

---

## 28. 🟢 Added to Vendor List - Celebration

**Priority:** NICE TO HAVE  
**Table:** Officer Outreach Tracking  
**Purpose:** Track and celebrate vendor list additions

### Setup Instructions:

1. **Name:** "Added to Vendor List Success"
2. **Trigger:** When record matches conditions
   - Table: `Officer Outreach Tracking`
   - Conditions:
     - When `Added to Vendor List` checkbox is checked
3. **Action 1:** Update record
   - Table: `Officer Outreach Tracking`
   - Record: Trigger record
   - Fields:
     - `Status` → "Added to Vendor List"
4. **Action 2:** Send email
   - To: `your-email@deedavisinc.com`
   - Subject: `🎯 VENDOR LIST SUCCESS: {Agency}`
   - Body:
```
🎯🎯🎯 ADDED TO VENDOR LIST! 🎯🎯🎯

Officer: {Officer Name}
Agency: {Agency}
━━━━━━━━━━━━━━━━━━━━━━━━
This relationship started from:
Opportunity: {Opportunity Title}
Solicitation: {Solicitation Number}

Timeline:
Letter Sent: {Date Sent}
Response Received: {Response Date}
Added to List: TODAY

Days to Success: [Calculate]
━━━━━━━━━━━━━━━━━━━━━━━━
NEXT STEPS:
1. ✅ Thank them for adding you
2. ✅ Request notification of future opportunities
3. ✅ Send quarterly capability updates
4. ✅ Monitor {Agency} opportunities closely
5. ✅ Build ongoing relationship

This could lead to multiple future awards!

View in Airtable:
[Link to record]
```
5. **Turn ON** the automation

---

## 29. 🟢 Weekly Officer Outreach Report

**Priority:** NICE TO HAVE  
**Table:** Officer Outreach Tracking  
**Purpose:** Weekly summary of outreach activities

### Setup Instructions:

1. **Name:** "Weekly Officer Outreach Report"
2. **Trigger:** At a scheduled time
   - Frequency: Weekly
   - Day: Monday
   - Time: 8:30 AM
3. **Action 1:** Find records (sent this week)
   - Table: `Officer Outreach Tracking`
   - Conditions:
     - Where `Date Sent` is in the last 7 days
4. **Action 2:** Find records (need follow-up)
   - Table: `Officer Outreach Tracking`
   - Conditions:
     - Where `Status` is "Follow-up Needed"
5. **Action 3:** Find records (responded this week)
   - Table: `Officer Outreach Tracking`
   - Conditions:
     - Where `Response Date` is in the last 7 days
6. **Action 4:** Send email
   - To: `your-email@deedavisinc.com`
   - Subject: `📬 Weekly Officer Outreach Report - [Date]`
   - Body:
```
📬 OFFICER OUTREACH WEEKLY REPORT
Week of [Date]
━━━━━━━━━━━━━━━━━━━━━━━━
ACTIVITY THIS WEEK:
Letters Sent: [Count from action 1]
Responses Received: [Count from action 3]
Response Rate: [Calculate %]

PENDING FOLLOW-UPS: [Count from action 2]
━━━━━━━━━━━━━━━━━━━━━━━━
CUMULATIVE STATS:
Total Letters Sent: [Count all where Date Sent exists]
Total Responses: [Count where Response Received = true]
Overall Response Rate: [Calculate %]
Added to Vendor Lists: [Count where Added to Vendor List = true]
Vendor List Conversion: [Calculate %]
━━━━━━━━━━━━━━━━━━━━━━━━
TOP AGENCIES BY RESPONSE:
[List agencies with highest response rates]
━━━━━━━━━━━━━━━━━━━━━━━━
ACTION ITEMS:
- Follow up with {count} officers
- Review {count} draft letters ready to send
- Track future opportunities from relationships

View all outreach in Airtable
```
7. **Turn ON** the automation

---

# PROPOSAL QUALITY AUTOMATIONS

## 30. 🔴 CRITICAL: Low ProposalBio Score Alert

**Priority:** CRITICAL  
**Table:** GPSS Proposals  
**Purpose:** Alert when proposal quality is too low

### Setup Instructions:

1. **Name:** "Low Proposal Quality Alert"
2. **Trigger:** When record matches conditions
   - Table: `GPSS Proposals`
   - Conditions:
     - When `ProposalBio Score` < 70
     - AND `Status` is "Draft" OR "Review"
3. **Action:** Send email
   - To: `your-email@deedavisinc.com`
   - Subject: `⚠️ LOW QUALITY PROPOSAL: {Proposal Name}`
   - Body:
```
⚠️ PROPOSAL QUALITY ALERT

Proposal: {Proposal Name}
Opportunity: {RFP Number}
━━━━━━━━━━━━━━━━━━━━━━━━
QUALITY SCORE: {ProposalBio Score}/100 ⚠️
Status: {Quality Status}
Badge: {Quality Badge}

Opportunity Value: {Opportunity Value}
Due Date: {Due Date}
━━━━━━━━━━━━━━━━━━━━━━━━
ISSUES FOUND:
{Improvement Notes}
━━━━━━━━━━━━━━━━━━━━━━━━
CRITICAL ACTION REQUIRED:
1. Review ProposalBio™ recommendations
2. Revise proposal to address issues
3. Re-run quality check
4. Target score: 80+ before submission

This is a ${Opportunity Value} opportunity!
Do not submit with quality score below 70.

View in Airtable:
[Link to record]
```
4. **Turn ON** the automation

---

## 31. 🟡 IMPORTANT: Proposal Ready to Send

**Priority:** IMPORTANT  
**Table:** GPSS Proposals  
**Purpose:** Confirm proposal passes quality check

### Setup Instructions:

1. **Name:** "Proposal Quality Check Passed"
2. **Trigger:** When record matches conditions
   - Table: `GPSS Proposals`
   - Conditions:
     - When `ProposalBio Score` >= 80
     - OR `Quality Status` is "Ready to Send"
3. **Action 1:** Update record
   - Table: `GPSS Proposals`
   - Record: Trigger record
   - Fields:
     - `Status` → "Ready to Send"
4. **Action 2:** Send email
   - To: `your-email@deedavisinc.com`
   - Subject: `✅ PROPOSAL READY: {Proposal Name}`
   - Body:
```
✅ PROPOSAL QUALITY CHECK PASSED

Proposal: {Proposal Name}
RFP: {RFP Number}
Agency: {Agency Name}
━━━━━━━━━━━━━━━━━━━━━━━━
QUALITY SCORE: {ProposalBio Score}/100 ✅
Status: Ready to Send
Badge: {Quality Badge}

Opportunity Value: {Opportunity Value}
Due Date: {Due Date}
Days Until Due: [Calculate]
━━━━━━━━━━━━━━━━━━━━━━━━
NEXT STEPS:
1. ✅ Final executive review
2. ✅ Prepare submission package
3. ✅ Verify all attachments included
4. ✅ Submit before {Due Date}
5. ✅ Update status to "Sent"

This proposal meets all quality standards!

View in Airtable:
[Link to record]
```
5. **Turn ON** the automation

---

## 32. 🟡 IMPORTANT: Proposal Deadline Warning

**Priority:** IMPORTANT  
**Table:** GPSS Proposals  
**Purpose:** Final warning before proposal due date

### Setup Instructions:

1. **Name:** "Proposal Deadline - 48 Hours"
2. **Trigger:** When record matches conditions
   - Table: `GPSS Proposals`
   - Conditions:
     - When `Due Date` is within the next 2 days
     - AND `Status` is not "Sent"
     - AND `Status` is not "Withdrawn"
3. **Action:** Send email
   - To: `your-email@deedavisinc.com`
   - Subject: `🚨 PROPOSAL DUE IN 48 HRS: {Proposal Name}`
   - Body:
```
🚨 URGENT: PROPOSAL DEADLINE IN 48 HOURS

Proposal: {Proposal Name}
RFP: {RFP Number}
Agency: {Agency Name}
━━━━━━━━━━━━━━━━━━━━━━━━
⏰ DUE: {Due Date} (48 hours!)
Status: {Status}
Quality Score: {ProposalBio Score}/100
Opportunity Value: {Opportunity Value}
━━━━━━━━━━━━━━━━━━━━━━━━
CRITICAL ACTIONS:
1. Complete any remaining sections
2. Run final ProposalBio™ quality check
3. Get executive approval
4. Prepare submission package
5. SUBMIT BEFORE DEADLINE

Do not let this ${Opportunity Value} opportunity slip away!

View in Airtable:
[Link to record]
```
4. **Turn ON** the automation

---

# LBPC SURPLUS RECOVERY AUTOMATIONS

## 33. 🟡 IMPORTANT: New Lead Follow-Up Sequence

**Priority:** IMPORTANT  
**Table:** LBPC Leads  
**Purpose:** Automated follow-up for new surplus recovery leads

### Setup Instructions:

1. **Name:** "LBPC New Lead - Day 3 Follow-Up"
2. **Trigger:** When record matches conditions
   - Table: `LBPC Leads`
   - Conditions:
     - When record created 3 days ago
     - AND `Status` is "New" OR "Contacted - No Response"
3. **Action:** Send email
   - To: `your-email@deedavisinc.com`
   - Subject: `📞 Follow-Up Needed: {Client Name} - ${Surplus Amount}`
   - Body:
```
LBPC FOLLOW-UP REMINDER

Client: {Client Name}
Surplus Amount: {Surplus Amount}
━━━━━━━━━━━━━━━━━━━━━━━━
LEAD DETAILS:
Property: {Property Address}, {City}, {State}
County: {County}
Case #: {Case Number}

First Contact: [3 days ago]
Status: {Status}
Priority: {Priority}
━━━━━━━━━━━━━━━━━━━━━━━━
RECOMMENDED ACTION:
Send follow-up letter/email:

"Dear {Client Name},

I'm following up on the surplus funds from your property 
at {Property Address}. This is ${Surplus Amount} that 
belongs to you.

Our services are 100% contingency-based - you pay nothing 
upfront. We handle all paperwork and only charge 30% when 
funds are successfully recovered.

You get 70% (${Client Payout}) with zero risk.

Can we schedule a brief call to discuss?

Best regards,
Lancaster Banques P.C."

━━━━━━━━━━━━━━━━━━━━━━━━
Your 30% Fee: {Fee Amount}

View in Airtable:
[Link to record]
```
4. **Turn ON** the automation

---

## 34. 🟢 Contract Signed - Congratulations

**Priority:** NICE TO HAVE  
**Table:** LBPC Leads  
**Purpose:** Celebrate signed contracts and guide next steps

### Setup Instructions:

1. **Name:** "LBPC Contract Signed"
2. **Trigger:** When record matches conditions
   - Table: `LBPC Leads`
   - Conditions:
     - When `Status` changes to "Contract Signed"
3. **Action:** Send email
   - To: `your-email@deedavisinc.com`
   - Subject: `🎉 CONTRACT SIGNED: {Client Name} - ${Surplus Amount}`
   - Body:
```
🎉 LBPC CONTRACT SIGNED!

Client: {Client Name}
Surplus Amount: {Surplus Amount}
Your Fee (30%): {Fee Amount}
Client Gets (70%): {Client Payout}
━━━━━━━━━━━━━━━━━━━━━━━━
CASE DETAILS:
Property: {Property Address}
County: {County}, {State}
Case #: {Case Number}

Contract Signed: TODAY
━━━━━━━━━━━━━━━━━━━━━━━━
NEXT STEPS:
1. ✅ File claim with county/court
2. ✅ Submit all required documentation
3. ✅ Track claim status
4. ✅ Follow up every 2 weeks
5. ✅ Process payment when received

Estimated Timeline: 60-90 days

View in Airtable:
[Link to record]
```
4. **Turn ON** the automation

---

## 35. 🟢 Payment Received - Success

**Priority:** NICE TO HAVE  
**Table:** LBPC Leads  
**Purpose:** Track and celebrate successful recoveries

### Setup Instructions:

1. **Name:** "LBPC Payment Received"
2. **Trigger:** When record matches conditions
   - Table: `LBPC Leads`
   - Conditions:
     - When `Status` changes to "Payment Received"
3. **Action:** Send email
   - To: `your-email@deedavisinc.com`
   - Subject: `💰 PAYMENT RECEIVED: {Client Name} - ${Fee Amount}`
   - Body:
```
💰💰💰 PAYMENT RECEIVED! 💰💰💰

Client: {Client Name}
Total Surplus: {Surplus Amount}
Your Fee (30%): {Fee Amount} ✅
Client Payout (70%): {Client Payout}
━━━━━━━━━━━━━━━━━━━━━━━━
CASE DETAILS:
Property: {Property Address}
County: {County}, {State}
Case #: {Case Number}

Contract Signed: {Contract Signed Date}
Payment Received: TODAY
Days to Recovery: [Calculate]
━━━━━━━━━━━━━━━━━━━━━━━━
NEXT STEPS:
1. ✅ Process client payment (70%)
2. ✅ Send thank you note
3. ✅ Request testimonial/referral
4. ✅ Update financial records in VERTEX
5. ✅ Mark case as closed

Congratulations on another successful recovery!

View in Airtable:
[Link to record]
```
4. **Turn ON** the automation

---

# DDCSS MARKETING AUTOMATIONS

## 36. 🟡 IMPORTANT: Hot Prospect Alert

**Priority:** IMPORTANT  
**Table:** DDCSS Prospects  
**Purpose:** Alert for high-priority marketing prospects

### Setup Instructions:

1. **Name:** "DDCSS Hot Prospect Alert"
2. **Trigger:** When record matches conditions
   - Table: `DDCSS Prospects`
   - Conditions:
     - When `Lead Score` >= 80
     - OR `Priority` is "High"
     - AND `Status` is "New" OR "Contacted"
3. **Action:** Send email
   - To: `your-email@deedavisinc.com`
   - Subject: `🔥 HOT PROSPECT: {Company Name}`
   - Body:
```
🔥 HIGH PRIORITY PROSPECT

Company: {Company Name}
Contact: {Contact Name}
━━━━━━━━━━━━━━━━━━━━━━━━
QUALIFICATION:
Lead Score: {Lead Score}/100
Industry: {Industry}
Company Size: {Company Size}
Estimated Value: {Estimated Value}
Priority: {Priority}
━━━━━━━━━━━━━━━━━━━━━━━━
CONTACT INFO:
Email: {Email}
Phone: {Phone}
Website: {Website}
━━━━━━━━━━━━━━━━━━━━━━━━
RECOMMENDED ACTIONS:
1. Review AI qualification notes
2. Research company website
3. Prepare personalized outreach
4. Call within 24 hours
5. Send DDCSS Blueprint

This is a hot lead - act fast!

View in Airtable:
[Link to record]
```
4. **Turn ON** the automation

---

## 37. 🟢 Follow-Up Campaign Sequence

**Priority:** NICE TO HAVE  
**Table:** DDCSS Prospects  
**Purpose:** Automated follow-up sequence for prospects

### Setup Instructions:

1. **Name:** "DDCSS Follow-Up - Day 7"
2. **Trigger:** When record matches conditions
   - Table: `DDCSS Prospects`
   - Conditions:
     - When record created 7 days ago
     - AND `Status` is "Contacted"
     - AND no recent activity
3. **Action:** Send email
   - To: `your-email@deedavisinc.com`
   - Subject: `📧 DDCSS Follow-Up: {Company Name}`
   - Body:
```
DDCSS FOLLOW-UP REMINDER

Company: {Company Name}
Contact: {Contact Name}
━━━━━━━━━━━━━━━━━━━━━━━━
PROSPECT INFO:
First Contact: [7 days ago]
Last Activity: [Date]
Lead Score: {Lead Score}
Status: {Status}
━━━━━━━━━━━━━━━━━━━━━━━━
RECOMMENDED FOLLOW-UP:

Subject: "Following up - Digital Marketing Blueprint"

"Hi {Contact Name},

I wanted to follow up on the digital marketing blueprint 
I sent last week. Did you have a chance to review it?

I'd love to hop on a quick 15-minute call to:
- Answer any questions
- Customize the strategy for {Company Name}
- Show you specific results we can achieve

Are you available for a brief call this week?

Best regards,
Dee Davis"

━━━━━━━━━━━━━━━━━━━━━━━━
ACTION: Send follow-up and update status

View in Airtable:
[Link to record]
```
4. **Turn ON** the automation

---

# CROSS-SYSTEM AUTOMATIONS

## 38. 🟡 IMPORTANT: Won Opportunity → Create Fulfillment Contract

**Priority:** IMPORTANT  
**Tables:** GPSS OPPORTUNITIES → FULFILLMENT CONTRACTS  
**Purpose:** Automatically create fulfillment contract when opportunity won

### Setup Instructions:

1. **Name:** "Auto-Create Fulfillment Contract"
2. **Trigger:** When record matches conditions
   - Table: `GPSS OPPORTUNITIES`
   - Conditions:
     - When `STATUS` changes to "Won"
     - AND opportunity is product-based (you may need to add a field to indicate this)
3. **Action:** Create record
   - Table: `FULFILLMENT CONTRACTS`
   - Map fields:
     - `CONTRACT_NAME` → {TITLE}
     - `CLIENT_NAME` → {AGENCY}
     - `TOTAL_VALUE` → {ESTIMATED_VALUE}
     - `STATUS` → "Active"
     - `NOTES` → "Auto-created from opportunity {SOLICITATION_NUMBER}"
4. **Turn ON** the automation

**Note:** You'll need to manually add delivery details, but this creates the shell

---

## 39. 🟢 Delivery Completed → Create Invoice

**Priority:** NICE TO HAVE  
**Tables:** FULFILLMENT DELIVERIES → VERTEX INVOICES  
**Purpose:** Auto-create invoice when delivery confirmed

### Setup Instructions:

1. **Name:** "Auto-Create Invoice on Delivery"
2. **Trigger:** When record matches conditions
   - Table: `FULFILLMENT DELIVERIES`
   - Conditions:
     - When `STATUS` changes to "Delivered"
3. **Action 1:** Find records (get contract info)
   - Table: `FULFILLMENT CONTRACTS`
   - Conditions:
     - Where record ID is in `CONTRACT` field
4. **Action 2:** Create record
   - Table: `VERTEX INVOICES`
   - Fields:
     - `CLIENT_NAME` → From contract: {CLIENT_NAME}
     - `INVOICE_AMOUNT` → Calculate: {QUANTITY} × {UNIT_PRICE}
     - `INVOICE_DATE` → {ACTUAL_DELIVERY_DATE}
     - `DUE_DATE` → Add 30 days to invoice date
     - `STATUS` → "Sent"
     - `DESCRIPTION` → "Delivery #{DELIVERY_NUMBER} - {DELIVERY_ID}"
     - `CATEGORY` → "Product Sales"
5. **Turn ON** the automation

---

## 40. 🟢 Weekly System Health Check

**Priority:** NICE TO HAVE  
**Purpose:** Overall system status report

### Setup Instructions:

1. **Name:** "Weekly System Health Check"
2. **Trigger:** At a scheduled time
   - Frequency: Weekly
   - Day: Monday
   - Time: 7:00 AM
3. **Action:** Send email
   - To: `your-email@deedavisinc.com`
   - Subject: `📊 NEXUS Weekly System Report - [Date]`
   - Body:
```
📊 NEXUS SYSTEM WEEKLY REPORT
Week of [Date]
━━━━━━━━━━━━━━━━━━━━━━━━
🎯 OPPORTUNITIES (GPSS)
Active: [Count from GPSS OPPORTUNITIES where STATUS = active]
High Priority: [Count where PRIORITY = High]
Due This Week: [Count]
Won This Week: [Count where STATUS = Won]

📦 FULFILLMENT
Active Contracts: [Count from FULFILLMENT CONTRACTS]
Deliveries This Week: [Count]
Low Inventory Items: [Count where STATUS = Low Stock]
Critical Items: [Count where STATUS = Critical]

💰 FINANCIALS (VERTEX)
Revenue This Month: [Sum invoices]
Expenses This Month: [Sum expenses]
Overdue Invoices: [Count]
Profit Margin: [Calculate]

🔨 PROJECTS (ATLAS)
Active Projects: [Count where STATUS = In Progress]
Due This Week: [Count]
At Risk: [Count where STATUS = At Risk]

━━━━━━━━━━━━━━━━━━━━━━━━
🚨 ATTENTION NEEDED:
- Critical inventory: [Count]
- Overdue deliveries: [Count]
- Overdue invoices: [Count]
- At-risk projects: [Count]

View Dashboard in Airtable
```
4. **Turn ON** the automation

---

# 🔧 AUTOMATION SETUP CHECKLIST

## Phase 1: Critical (Week 1)
Set up these immediately - 9 automations:

```
FULFILLMENT:
□ 1. Low Inventory Alert
□ 2. Inventory Shortage Alert
□ 3. Delivery Due in 7 Days

OPPORTUNITIES:
□ 9. High Priority Opportunity Alert
□ 10. Proposal Deadline Approaching

FINANCIAL:
□ 14. Invoice Overdue Alert

OUTREACH:
□ 26. Officer Outreach Follow-Up Reminder

PROPOSALS:
□ 30. Low ProposalBio Score Alert

LBPC:
□ 33. New Lead Follow-Up Sequence
```

## Phase 2: Important (Week 2)
Set up these next - 12 automations:

```
FULFILLMENT:
□ 4. Delivery Due Today
□ 5. Overdue Delivery Alert

OPPORTUNITIES:
□ 11. Opportunity Status Change

FINANCIAL:
□ 15. Invoice Due Soon
□ 16. Expense Payment Due

PROJECTS:
□ 18. Project Deadline Approaching

SUPPLIERS:
□ 21. New Supplier Added

OUTREACH:
□ 27. Response Received - Next Steps

PROPOSALS:
□ 31. Proposal Ready to Send
□ 32. Proposal Deadline Warning

MARKETING:
□ 36. Hot Prospect Alert

CROSS-SYSTEM:
□ 38. Won Opportunity → Fulfillment Contract
```

## Phase 3: Nice to Have (Month 1)
Set up when ready - 17 automations:

```
FULFILLMENT:
□ 6. Purchase Order Arriving Soon
□ 7. Contract Completion Celebration
□ 8. Auto-Calculate Contract Progress

OPPORTUNITIES:
□ 12. Weekly Opportunity Digest
□ 13. Auto-Tag Opportunities by Value

FINANCIAL:
□ 17. Monthly Financial Summary

PROJECTS:
□ 19. Task Overdue Alert
□ 20. Project Status Report

SUPPLIERS:
□ 22. Supplier Performance Alert

OUTREACH:
□ 28. Added to Vendor List - Celebration
□ 29. Weekly Officer Outreach Report

LBPC:
□ 34. Contract Signed - Congratulations
□ 35. Payment Received - Success

MARKETING:
□ 37. Follow-Up Campaign Sequence

CROSS-SYSTEM:
□ 39. Delivery Completed → Invoice
□ 40. Weekly System Health Check
```

---

# 📱 NOTIFICATION SETTINGS

## Email Notifications

**Recommended:**
- Use your primary business email: `your-email@deedavisinc.com`
- Set up email filters/labels for automation emails
- Create folder: "NEXUS Alerts"
- Set up rules for high-priority alerts (flag/star critical ones)

## SMS/Text Notifications (Optional)

**For critical alerts only:**
- Use Airtable's SMS action (requires Twilio integration)
- Recommended for:
  - Inventory shortages
  - Overdue deliveries
  - High-value opportunities

---

# 🔍 TESTING YOUR AUTOMATIONS

## How to Test:

1. **Create test records** with trigger conditions
2. **Wait** for automation to run (usually instant)
3. **Check your email** for notification
4. **Verify** automation ran correctly in Automation History

## Test Scenarios:

```
✅ Create test delivery with DUE_DATE = 7 days from now
   → Should receive "Delivery Due in 7 Days" email

✅ Create test inventory with QUANTITY_ON_HAND = 50, REORDER_POINT = 100
   → Should receive "Low Inventory Alert" email

✅ Create test opportunity with ESTIMATED_VALUE = 500000, PRIORITY = High
   → Should receive "High Priority Opportunity" email
```

---

# 💡 AUTOMATION BEST PRACTICES

## Do:
✅ Test each automation with dummy data first
✅ Use clear, descriptive names
✅ Include all relevant info in email body
✅ Add links back to Airtable records
✅ Review automation history weekly
✅ Turn off unused automations

## Don't:
❌ Create duplicate automations
❌ Use vague email subjects
❌ Send too many notifications (alert fatigue)
❌ Forget to test before going live
❌ Ignore automation errors

---

# 🚨 TROUBLESHOOTING

## "Automation didn't run"
→ Check trigger conditions are met
→ Verify automation is turned ON
→ Check automation run history for errors

## "Email not received"
→ Check spam/junk folder
→ Verify email address is correct
→ Check automation history shows email sent

## "Wrong data in email"
→ Check field mappings
→ Verify linked records exist
→ Test with different record

## "Automation running too often"
→ Review trigger conditions
→ Add additional conditions to limit
→ Consider using scheduled trigger instead

---

# 📊 MONITORING AUTOMATION HEALTH

**Weekly Review:**
- Check Automation History for errors
- Review email notifications received
- Verify critical automations are running
- Test 1-2 automations with dummy data

**Monthly Review:**
- Review all 25 automations
- Turn off unused automations
- Update email templates if needed
- Add new automations as needed

---

# ✅ SETUP COMPLETE CHECKLIST

```
□ Phase 1 automations (6) - CRITICAL
□ Phase 2 automations (8) - IMPORTANT
□ Phase 3 automations (11) - NICE TO HAVE
□ Email notifications configured
□ Test scenarios completed
□ Automation history reviewed
□ Troubleshooting guide bookmarked
□ Weekly review scheduled
```

---

**All 38 automations configured = Full NEXUS automation!** 🚀

**Questions?** Review troubleshooting section or test with dummy data first.

**Built:** January 21, 2026  
**Total Automations:** 38 (covers ENTIRE NEXUS system)  
**Setup Time:** ~5-6 hours (all automations)  
**ROI:** Save 15-20 hours/week in manual tracking

**COMPLETE COVERAGE:**
✅ Fulfillment System (8 automations)
✅ GPSS Opportunities (5 automations)
✅ VERTEX Financial (4 automations)
✅ ATLAS Projects (3 automations)
✅ Supplier Management (2 automations)
✅ Officer Outreach (4 automations) ⭐ NEW
✅ Proposal Quality (3 automations) ⭐ NEW
✅ LBPC Surplus Recovery (3 automations) ⭐ NEW
✅ DDCSS Marketing (2 automations) ⭐ NEW
✅ Cross-System Integration (3 automations)
