# ALL NEXUS AUTOMATIONS - COMPLETE GUIDE
**Balanced notification strategy: Email alerts + Dashboard displays**

---

## 📊 REVISED AUTOMATION STRATEGY

After analyzing your NEXUS dashboard, here's the optimal approach:

### **🔴 CRITICAL EMAIL ALERTS (14 total)**
These require immediate action → Send email alerts:
- Already done: 5 (✅ 1, 2, 3, 4, 6)
- Skipped: 1 (⏸️ 5 - needs field)
- To setup: 8 (🆕 7-14)

### **🟢 DASHBOARD-ONLY NOTIFICATIONS (100+ actions)**
These are tracked automatically → Your dashboard already shows them:
- New opportunities → Shows in Activity Stream
- Quote updates → Shows in Activity Stream
- Task updates → Shows in Deadlines section
- Project updates → Shows in Activity Stream
- AI recommendations → Shows in Alerts section

**Why?** Your dashboard auto-refreshes every 30 seconds and pulls from Airtable. No automation needed!

---

## 📋 HOW TO USE THIS FILE

1. **Start at Automation #1**
2. **Follow the grid row by row**
3. **Copy the email template exactly**
4. **Check the box when done**
5. **Move to next automation**

**Email Automations: 14 total**  
**Already done: 5** (Automations 1, 2, 3, 4, 6)  
**Skipped: 1** (Automation 5 - needs field added)  
**To setup: 8** (Automations 7-14)

---

# 🔴 CRITICAL EMAIL AUTOMATIONS (14 total)

**Purpose:** These send immediate email alerts for actions requiring urgent response

---

## ✅ AUTOMATION 1: BID DEADLINE ALERT (48 HOURS)

**System:** GPSS  
**Table:** GPSS OPPORTUNITIES  
**Status:** ✅ DONE

---

## ✅ AUTOMATION 2: QUOTE DUE REMINDER (24 HOURS)

**System:** GPSS  
**Table:** GPSS SUBCONTRACTOR QUOTES  
**Status:** ✅ DONE

---

## ✅ AUTOMATION 3: QUOTE RECEIVED NOTIFICATION

**System:** GPSS  
**Table:** GPSS SUBCONTRACTOR QUOTES  
**Status:** ✅ DONE

---

## ✅ AUTOMATION 4: NEW OPPORTUNITY ALERT

**System:** GPSS  
**Table:** GPSS OPPORTUNITIES  
**Status:** ✅ DONE

---

## ⏸️ AUTOMATION 5: SUPPLIER NON-RESPONSE ALERT

**System:** GPSS  
**Table:** GPSS SUBCONTRACTOR QUOTES  
**Status:** ⏸️ SKIPPED (needs Quote Due Date field)

---

## ✅ AUTOMATION 6: WINNING BID WORKFLOW

**System:** GPSS  
**Table:** GPSS OPPORTUNITIES  
**Status:** ✅ DONE

---

## 🆕 AUTOMATION 7: HIGH-VALUE OPPORTUNITY ALERT ($100K+)

**System:** GPSS  
**Table:** GPSS OPPORTUNITIES  
**Purpose:** 🔴 EMAIL - Immediate alert for high-value opportunities

| Step | Action | Value |
|------|--------|-------|
| 1 | Create automation | Click "+ Create automation" in GPSS OPPORTUNITIES |
| 2 | Name | `💎 High-Value Opportunity Alert` |
| 3 | Trigger | When record created |
| 4 | Table | GPSS OPPORTUNITIES |
| 5 | Add condition | When ANY conditions are met |
| 6 | Condition | Estimated Value is greater than 100000 |
| 7 | Add action | Send email |
| 8 | To | info@deedavis.biz |
| 9 | From name | NEXUS Priority Alert |
| 10 | Subject | `💎 HIGH VALUE: {Estimated Value} - {Name}` |
| 11 | Message | Copy template below ⬇️ |
| 12 | Turn ON | Toggle automation ON |

**Email Template:**
```
💎 HIGH-VALUE OPPORTUNITY DETECTED

RFP: {Name}
Value: {Estimated Value}
Agency: {AGENCY}

⏰ Deadline: {DUE_DATE}
Source: {Source}
Status: {STATUS}

🎯 WHY THIS MATTERS:
High-value contracts require extra attention to proposal quality and team capacity.

🚀 NEXT STEPS:
1. Review full RFP in GPSS → Opportunities
2. Assess capability gaps
3. Consider teaming partners
4. Allocate senior resources

📊 View in NEXUS: http://localhost:3000/gpss

--
NEXUS Priority Alert System
```

**Status:** ⬜ NOT DONE

---

## 🆕 AUTOMATION 8: DELIVERY OVERDUE ALERT

**System:** FULFILLMENT  
**Table:** FULFILLMENT DELIVERIES  
**Purpose:** 🔴 EMAIL - Critical alert for late deliveries

| Step | Action | Value |
|------|--------|-------|
| 1 | Create automation | Click "+ Create automation" in FULFILLMENT DELIVERIES |
| 2 | Name | `🚨 Delivery OVERDUE Alert` |
| 3 | Trigger | When record matches conditions |
| 4 | Table | FULFILLMENT DELIVERIES |
| 5 | Add conditions | When ALL conditions are met |
| 6 | Condition 1 | STATUS is "Pending" |
| 7 | Condition 2 | SCHEDULED_DATE is before today |
| 8 | Add action | Send email |
| 9 | To | info@deedavis.biz |
| 10 | From name | NEXUS URGENT |
| 11 | Subject | `🚨 OVERDUE: Delivery for {CLIENT_NAME}` |
| 12 | Message | Copy template below ⬇️ |
| 13 | Turn ON | Toggle automation ON |

**Email Template:**
```
🚨 DELIVERY OVERDUE - IMMEDIATE ACTION REQUIRED

Client: {CLIENT_NAME}
Product: {PRODUCT_NAME}
Quantity: {QUANTITY_TO_SHIP}
Due Date: {SCHEDULED_DATE}
Days Late: [Calculate manually]

⚠️ CLIENT IMPACT:
This delivery is past due. Client may be impacted.

🚀 IMMEDIATE ACTIONS:
1. Check inventory availability
2. Contact supplier if stock is low
3. Ship today if possible
4. Call client to update them
5. Update delivery status in NEXUS

📊 View in NEXUS: http://localhost:3000/fulfillment

--
NEXUS Urgent Alert System
```

**Status:** ⬜ NOT DONE

---

## 🆕 AUTOMATION 9: DELIVERY DUE TODAY

**System:** FULFILLMENT  
**Table:** FULFILLMENT DELIVERIES  
**Purpose:** 🔴 EMAIL - Ship today reminder

| Step | Action | Value |
|------|--------|-------|
| 1 | Create automation | Click "+ Create automation" in FULFILLMENT DELIVERIES |
| 2 | Name | `📦 Delivery Due TODAY` |
| 3 | Trigger | When record matches conditions |
| 4 | Table | FULFILLMENT DELIVERIES |
| 5 | Add conditions | When ALL conditions are met |
| 6 | Condition 1 | STATUS is "Pending" |
| 7 | Condition 2 | SCHEDULED_DATE is today |
| 8 | Add action | Send email |
| 9 | To | info@deedavis.biz |
| 10 | From name | NEXUS Daily Alert |
| 11 | Subject | `📦 SHIP TODAY: {PRODUCT_NAME} to {CLIENT_NAME}` |
| 12 | Message | Copy template below ⬇️ |
| 13 | Turn ON | Toggle automation ON |

**Email Template:**
```
📦 DELIVERY DUE TODAY

Client: {CLIENT_NAME}
Product: {PRODUCT_NAME}
Quantity: {QUANTITY_TO_SHIP}
Due Date: {SCHEDULED_DATE} (TODAY)

📋 SHIPPING CHECKLIST:
☐ Verify inventory available
☐ Pack and label shipment
☐ Print shipping label
☐ Get tracking number
☐ Ship via carrier
☐ Update status to "In Transit"
☐ Add tracking number to NEXUS

📊 View in NEXUS: http://localhost:3000/fulfillment

--
NEXUS Daily Alert System
```

**Status:** ⬜ NOT DONE

---

## 🆕 AUTOMATION 10: INVOICE OVERDUE ALERT

**System:** VERTEX  
**Table:** VERTEX INVOICES  
**Purpose:** 🔴 EMAIL - Cash flow protection

| Step | Action | Value |
|------|--------|-------|
| 1 | Create automation | Click "+ Create automation" in VERTEX INVOICES |
| 2 | Name | `💰 Invoice OVERDUE Alert` |
| 3 | Trigger | When record matches conditions |
| 4 | Table | VERTEX INVOICES |
| 5 | Add conditions | When ALL conditions are met |
| 6 | Condition 1 | PAYMENT_STATUS is "Unpaid" |
| 7 | Condition 2 | DUE_DATE is before today |
| 8 | Add action | Send email |
| 9 | To | info@deedavis.biz |
| 10 | From name | NEXUS Cash Flow Alert |
| 11 | Subject | `💰 OVERDUE: Invoice #{INVOICE_NUMBER} - {CLIENT_NAME}` |
| 12 | Message | Copy template below ⬇️ |
| 13 | Turn ON | Toggle automation ON |

**Email Template:**
```
💰 INVOICE OVERDUE - FOLLOW UP NEEDED

Invoice: #{INVOICE_NUMBER}
Client: {CLIENT_NAME}
Amount: {TOTAL_AMOUNT}
Due Date: {DUE_DATE}
Days Late: [Calculate manually]

⚠️ CASH FLOW IMPACT:
This overdue invoice affects your cash flow.

🚀 FOLLOW-UP ACTIONS:
1. Check if payment was received (update status if so)
2. Send payment reminder to client
3. Call client if >30 days overdue
4. Review payment terms for future contracts
5. Consider late fees if applicable

📊 View in NEXUS: http://localhost:3000/vertex

--
NEXUS Cash Flow Alert System
```

**Status:** ⬜ NOT DONE

---

## 🆕 AUTOMATION 11: PAYMENT RECEIVED CELEBRATION

**System:** VERTEX  
**Table:** VERTEX INVOICES  
**Purpose:** 🔴 EMAIL - Celebrate wins & track cash flow

| Step | Action | Value |
|------|--------|-------|
| 1 | Create automation | Click "+ Create automation" in VERTEX INVOICES |
| 2 | Name | `🎉 Payment Received!` |
| 3 | Trigger | When record matches conditions |
| 4 | Table | VERTEX INVOICES |
| 5 | Add condition | When ANY conditions are met |
| 6 | Condition | PAYMENT_STATUS is "Paid" |
| 7 | Add action | Send email |
| 8 | To | info@deedavis.biz |
| 9 | From name | NEXUS Wins |
| 10 | Subject | `🎉 PAID: {TOTAL_AMOUNT} from {CLIENT_NAME}` |
| 11 | Message | Copy template below ⬇️ |
| 12 | Turn ON | Toggle automation ON |

**Email Template:**
```
🎉 PAYMENT RECEIVED!

Invoice: #{INVOICE_NUMBER}
Client: {CLIENT_NAME}
Amount: {TOTAL_AMOUNT}
Paid Date: {PAYMENT_DATE}

💰 CASH FLOW UPDATE:
This payment has been received and deposited.

🎯 QUICK STATS:
- System: {SYSTEM}
- Original Due: {DUE_DATE}
- Payment Terms: Net 30
- Status: PAID ✅

📊 View in NEXUS: http://localhost:3000/vertex

--
NEXUS Wins Tracking
```

**Status:** ⬜ NOT DONE

---

## 🆕 AUTOMATION 12: CRITICAL INVENTORY SHORTAGE

**System:** FULFILLMENT  
**Table:** FULFILLMENT INVENTORY  
**Purpose:** 🔴 EMAIL - Prevent stockouts

| Step | Action | Value |
|------|--------|-------|
| 1 | Create automation | Click "+ Create automation" in FULFILLMENT INVENTORY |
| 2 | Name | `⚠️ CRITICAL Inventory Shortage` |
| 3 | Trigger | When record matches conditions |
| 4 | Table | FULFILLMENT INVENTORY |
| 5 | Add conditions | When ALL conditions are met |
| 6 | Condition 1 | ON_HAND is less than REORDER_POINT |
| 7 | Condition 2 | STATUS is not "Reordering" |
| 8 | Add action | Send email |
| 9 | To | info@deedavis.biz |
| 10 | From name | NEXUS CRITICAL |
| 11 | Subject | `⚠️ CRITICAL: Low stock on {PRODUCT_NAME}` |
| 12 | Message | Copy template below ⬇️ |
| 13 | Turn ON | Toggle automation ON |

**Email Template:**
```
⚠️ CRITICAL INVENTORY SHORTAGE

Product: {PRODUCT_NAME}
On Hand: {ON_HAND}
Committed: {COMMITTED}
Available: {AVAILABLE}
Reorder Point: {REORDER_POINT}

🚨 RISK:
Cannot fulfill upcoming deliveries without immediate reorder.

🚀 IMMEDIATE ACTIONS:
1. Place PO with {SUPPLIER_NAME} NOW
2. Request expedited shipping
3. Update inventory status to "Reordering"
4. Calculate days until stockout
5. Alert clients if delays expected

📋 SUGGESTED ORDER:
Quantity: {REORDER_QUANTITY}
Cost: {UNIT_COST} × {REORDER_QUANTITY}

📊 View in NEXUS: http://localhost:3000/fulfillment

--
NEXUS Critical Alert System
```

**Status:** ⬜ NOT DONE

---

## 🆕 AUTOMATION 13: PROJECT DEADLINE 24 HOURS

**System:** ATLAS PM  
**Table:** ATLAS TASKS  
**Purpose:** 🔴 EMAIL - Prevent late deliverables

| Step | Action | Value |
|------|--------|-------|
| 1 | Create automation | Click "+ Create automation" in ATLAS TASKS |
| 2 | Name | `⏰ Project Task Due in 24 Hours` |
| 3 | Trigger | When record matches conditions |
| 4 | Table | ATLAS TASKS |
| 5 | Add conditions | When ALL conditions are met |
| 6 | Condition 1 | STATUS is not "Complete" |
| 7 | Condition 2 | DUE_DATE is within next 1 day |
| 8 | Add action | Send email |
| 9 | To | info@deedavis.biz |
| 10 | From name | NEXUS Project Alert |
| 11 | Subject | `⏰ DUE TOMORROW: {TASK_NAME}` |
| 12 | Message | Copy template below ⬇️ |
| 13 | Turn ON | Toggle automation ON |

**Email Template:**
```
⏰ PROJECT TASK DUE IN 24 HOURS

Task: {TASK_NAME}
Project: {PROJECT_NAME}
Due Date: {DUE_DATE}
Priority: {PRIORITY}
Assigned: {ASSIGNED_TO}

⚠️ PROJECT IMPACT:
This task is critical path. Delay will impact project timeline.

🚀 COMPLETE TODAY:
1. Review task requirements
2. Complete all work
3. Update status to "Complete"
4. Update progress percentage
5. Document any blockers

📊 View in NEXUS: http://localhost:3000/atlas

--
NEXUS Project Management Alert
```

**Status:** ⬜ NOT DONE

---

## 🆕 AUTOMATION 14: EXPENSE PAYMENT DUE TODAY

**System:** VERTEX  
**Table:** VERTEX EXPENSES  
**Purpose:** 🔴 EMAIL - Avoid late fees

| Step | Action | Value |
|------|--------|-------|
| 1 | Create automation | Click "+ Create automation" in VERTEX EXPENSES |
| 2 | Name | `💳 Expense Payment DUE TODAY` |
| 3 | Trigger | When record matches conditions |
| 4 | Table | VERTEX EXPENSES |
| 5 | Add conditions | When ALL conditions are met |
| 6 | Condition 1 | PAYMENT_STATUS is "Unpaid" |
| 7 | Condition 2 | DUE_DATE is today |
| 8 | Add action | Send email |
| 9 | To | info@deedavis.biz |
| 10 | From name | NEXUS Payment Alert |
| 11 | Subject | `💳 PAY TODAY: {AMOUNT} to {SUPPLIER_NAME}` |
| 12 | Message | Copy template below ⬇️ |
| 13 | Turn ON | Toggle automation ON |

**Email Template:**
```
💳 EXPENSE PAYMENT DUE TODAY

Supplier: {SUPPLIER_NAME}
Amount: {AMOUNT}
Due Date: {DUE_DATE} (TODAY)
Category: {CATEGORY}
Reference: {REFERENCE_NUMBER}

⚠️ AVOID LATE FEES:
Pay today to maintain good supplier relationships.

🚀 PAYMENT CHECKLIST:
☐ Verify amount matches invoice
☐ Process payment via ACH/check/card
☐ Get payment confirmation
☐ Update status to "Paid"
☐ Add payment date to NEXUS
☐ File receipt

📊 View in NEXUS: http://localhost:3000/vertex

--
NEXUS Payment Alert System
```

**Status:** ⬜ NOT DONE

This is a MAJOR opportunity!
Give immediate attention.
```

[ ] COMPLETE [ ] ON

---

## AUTOMATION 8: LOST BID FOLLOW-UP

**System:** GPSS  
**Table:** GPSS OPPORTUNITIES

| Step | Action | Value |
|------|--------|-------|
| 1 | Create automation | |
| 2 | Name | `📊 Lost Bid - Debrief Needed` |
| 3 | Trigger | When record matches conditions |
| 4 | Table | GPSS OPPORTUNITIES |
| 5 | Condition | Status becomes Lost |
| 6 | Add action | Send email |
| 7 | To | info@deedavis.biz |
| 8 | From name | NEXUS Learning |
| 9 | Subject | 📊 Lost Bid Debrief: [Name] |
| 10 | Message | See template ⬇️ |
| 11 | Turn ON | |

**Email Template:**
```
📊 BID LOST - LEARNING OPPORTUNITY

RFP: [Name]
Agency: [AGENCY]
Our Bid: $[Est Profit]

ACTION:
1. Request debrief
2. Ask winning bid amount
3. Document lessons
4. Update pricing

Contact: [CONTRACTING OFFICER]
```

[ ] COMPLETE [ ] ON

---

## AUTOMATION 9: LOW INVENTORY ALERT

**System:** Fulfillment  
**Table:** FULFILLMENT INVENTORY

| Step | Action | Value |
|------|--------|-------|
| 1 | Create automation | |
| 2 | Name | `🟡 Low Inventory Alert` |
| 3 | Trigger | When record matches conditions |
| 4 | Table | FULFILLMENT INVENTORY |
| 5 | Condition 1 | QUANTITY_ON_HAND < REORDER_POINT |
| 6 | Condition 2 | AND STATUS is not Out of Stock |
| 7 | Add action | Update record |
| 8 | Field to update | STATUS → Low Stock |
| 9 | Add action | Send email |
| 10 | To | info@deedavis.biz |
| 11 | From name | NEXUS Inventory |
| 12 | Subject | 🟡 LOW INVENTORY: [PRODUCT_NAME] |
| 13 | Message | See template ⬇️ |
| 14 | Turn ON | |

**Email Template:**
```
REORDER RECOMMENDED

Product: [PRODUCT_NAME]
SKU: [PRODUCT_SKU]

Current: [QUANTITY_ON_HAND]
Reorder Point: [REORDER_POINT]
Order: [REORDER_QUANTITY]

Supplier: [SUPPLIER]
Cost: [UNIT_COST]

ACTION: Create purchase order
```

[ ] COMPLETE [ ] ON

---

## AUTOMATION 10: CRITICAL INVENTORY SHORTAGE

**System:** Fulfillment  
**Table:** FULFILLMENT INVENTORY

| Step | Action | Value |
|------|--------|-------|
| 1 | Create automation | |
| 2 | Name | `🚨 Critical Inventory Shortage` |
| 3 | Trigger | When record matches conditions |
| 4 | Table | FULFILLMENT INVENTORY |
| 5 | Condition 1 | QUANTITY_AVAILABLE < 0 |
| 6 | Condition 2 | OR STATUS is Critical |
| 7 | Add action | Update record |
| 8 | Field to update | STATUS → Critical |
| 9 | Add action | Send email |
| 10 | To | info@deedavis.biz |
| 11 | From name | NEXUS URGENT |
| 12 | Subject | 🚨 CRITICAL SHORTAGE: [PRODUCT_NAME] |
| 13 | Message | See template ⬇️ |
| 14 | Turn ON | |

**Email Template:**
```
⚠️ CRITICAL INVENTORY ALERT

Product: [PRODUCT_NAME]

On Hand: [QUANTITY_ON_HAND]
Committed: [QUANTITY_COMMITTED]
Available: [QUANTITY_AVAILABLE] (NEGATIVE!)

⚠️ URGENT:
1. Emergency PO
2. Contact supplier
3. Review deliveries

Supplier: [SUPPLIER]
```

[ ] COMPLETE [ ] ON

---

## AUTOMATION 11: DELIVERY DUE IN 7 DAYS

**System:** Fulfillment  
**Table:** FULFILLMENT DELIVERIES

| Step | Action | Value |
|------|--------|-------|
| 1 | Create automation | |
| 2 | Name | `📦 Delivery Due in 7 Days` |
| 3 | Trigger | When record matches conditions |
| 4 | Table | FULFILLMENT DELIVERIES |
| 5 | Condition 1 | DUE_DATE within next 7 days |
| 6 | Condition 2 | AND STATUS is Scheduled |
| 7 | Add action | Send email |
| 8 | To | info@deedavis.biz |
| 9 | From name | NEXUS Deliveries |
| 10 | Subject | 📦 Delivery Due 7 Days: [DELIVERY_ID] |
| 11 | Message | See template ⬇️ |
| 12 | Turn ON | |

**Email Template:**
```
UPCOMING DELIVERY

Delivery: [DELIVERY_ID]
Due: [DUE_DATE]
Quantity: [QUANTITY] units

ACTION:
1. Verify inventory
2. Prepare shipment
3. Confirm carrier
4. Schedule pickup
```

[ ] COMPLETE [ ] ON

---

## AUTOMATION 12: DELIVERY DUE TODAY

**System:** Fulfillment  
**Table:** FULFILLMENT DELIVERIES

| Step | Action | Value |
|------|--------|-------|
| 1 | Create automation | |
| 2 | Name | `🚚 Delivery Due TODAY` |
| 3 | Trigger | When record matches conditions |
| 4 | Table | FULFILLMENT DELIVERIES |
| 5 | Condition 1 | DUE_DATE is today |
| 6 | Condition 2 | AND STATUS not Delivered |
| 7 | Condition 3 | AND STATUS not Cancelled |
| 8 | Add action | Send email |
| 9 | To | info@deedavis.biz |
| 10 | From name | NEXUS URGENT |
| 11 | Subject | 🚚 DELIVERY DUE TODAY: [DELIVERY_ID] |
| 12 | Message | See template ⬇️ |
| 13 | Turn ON | |

**Email Template:**
```
⏰ DELIVERY DUE TODAY

Delivery: [DELIVERY_ID]
Quantity: [QUANTITY]

URGENT:
1. Ship immediately
2. Update to "In Transit"
3. Add tracking
4. Notify client if delay
```

[ ] COMPLETE [ ] ON

---

## AUTOMATION 13: OVERDUE DELIVERY ALERT

**System:** Fulfillment  
**Table:** FULFILLMENT DELIVERIES

| Step | Action | Value |
|------|--------|-------|
| 1 | Create automation | |
| 2 | Name | `⚠️ Overdue Delivery Alert` |
| 3 | Trigger | When record matches conditions |
| 4 | Table | FULFILLMENT DELIVERIES |
| 5 | Condition 1 | DUE_DATE in the past |
| 6 | Condition 2 | AND STATUS not Delivered |
| 7 | Condition 3 | AND STATUS not Cancelled |
| 8 | Add action | Update record |
| 9 | Field to update | STATUS → Late |
| 10 | Add action | Send email |
| 11 | To | info@deedavis.biz |
| 12 | From name | NEXUS CRITICAL |
| 13 | Subject | ⚠️ LATE DELIVERY: [DELIVERY_ID] |
| 14 | Message | See template ⬇️ |
| 15 | Turn ON | |

**Email Template:**
```
⚠️ LATE DELIVERY

Delivery: [DELIVERY_ID]
Was Due: [DUE_DATE]
Status: OVERDUE

URGENT:
1. Ship immediately
2. Contact client - apologize
3. Provide tracking
4. Document delay reason
```

[ ] COMPLETE [ ] ON

---

## AUTOMATION 14: INVOICE OVERDUE ALERT

**System:** VERTEX  
**Table:** VERTEX INVOICES

| Step | Action | Value |
|------|--------|-------|
| 1 | Create automation | |
| 2 | Name | `💰 Invoice Overdue Alert` |
| 3 | Trigger | When record matches conditions |
| 4 | Table | VERTEX INVOICES |
| 5 | Condition 1 | DUE_DATE in the past |
| 6 | Condition 2 | AND STATUS not Paid |
| 7 | Condition 3 | AND STATUS not Cancelled |
| 8 | Add action | Update record |
| 9 | Field to update | STATUS → Overdue |
| 10 | Add action | Send email |
| 11 | To | info@deedavis.biz |
| 12 | From name | NEXUS Financial |
| 13 | Subject | 💰 OVERDUE: [CLIENT_NAME] - $[INVOICE_AMOUNT] |
| 14 | Message | See template ⬇️ |
| 15 | Turn ON | |

**Email Template:**
```
⚠️ INVOICE OVERDUE

Client: [CLIENT_NAME]
Amount: $[INVOICE_AMOUNT]

Invoice Date: [INVOICE_DATE]
Due Date: [DUE_DATE]

ACTION:
1. Send payment reminder
2. Follow up via phone
3. Escalate if > 30 days
```

[ ] COMPLETE [ ] ON

---

## AUTOMATION 15: INVOICE DUE SOON

**System:** VERTEX  
**Table:** VERTEX INVOICES

| Step | Action | Value |
|------|--------|-------|
| 1 | Create automation | |
| 2 | Name | `⏰ Invoice Due in 5 Days` |
| 3 | Trigger | When record matches conditions |
| 4 | Table | VERTEX INVOICES |
| 5 | Condition 1 | DUE_DATE within next 5 days |
| 6 | Condition 2 | AND STATUS is Sent |
| 7 | Add action | Send email |
| 8 | To | info@deedavis.biz |
| 9 | From name | NEXUS Financial |
| 10 | Subject | ⏰ Invoice Due Soon: [CLIENT_NAME] - $[INVOICE_AMOUNT] |
| 11 | Message | See template ⬇️ |
| 12 | Turn ON | |

**Email Template:**
```
INVOICE DUE IN 5 DAYS

Client: [CLIENT_NAME]
Amount: $[INVOICE_AMOUNT]
Due: [DUE_DATE]

Send friendly reminder:
"Invoice #[ID] for $[INVOICE_AMOUNT] 
due on [DUE_DATE]. Questions?"
```

[ ] COMPLETE [ ] ON

---

## AUTOMATION 16: PAYMENT RECEIVED

**System:** VERTEX  
**Table:** VERTEX INVOICES

| Step | Action | Value |
|------|--------|-------|
| 1 | Create automation | |
| 2 | Name | `💰 Payment Received` |
| 3 | Trigger | When record matches conditions |
| 4 | Table | VERTEX INVOICES |
| 5 | Condition | STATUS becomes Paid |
| 6 | Add action | Send email |
| 7 | To | info@deedavis.biz |
| 8 | From name | NEXUS Financial |
| 9 | Subject | 💰 PAYMENT: [CLIENT_NAME] - $[INVOICE_AMOUNT] |
| 10 | Message | See template ⬇️ |
| 11 | Turn ON | |

**Email Template:**
```
💰 PAYMENT RECEIVED!

Client: [CLIENT_NAME]
Amount: $[INVOICE_AMOUNT] ✅

Invoice Date: [INVOICE_DATE]
Due Date: [DUE_DATE]
Paid: TODAY

Next:
1. Update accounting
2. Send thank you
3. Archive invoice
```

[ ] COMPLETE [ ] ON

---

## AUTOMATION 17: EXPENSE PAYMENT DUE

**System:** VERTEX  
**Table:** VERTEX EXPENSES

| Step | Action | Value |
|------|--------|-------|
| 1 | Create automation | |
| 2 | Name | `💳 Expense Payment Due` |
| 3 | Trigger | When record matches conditions |
| 4 | Table | VERTEX EXPENSES |
| 5 | Condition 1 | Payment due within next 3 days |
| 6 | Condition 2 | AND STATUS not Paid |
| 7 | Add action | Send email |
| 8 | To | info@deedavis.biz |
| 9 | From name | NEXUS Financial |
| 10 | Subject | 💳 Payment Due: [EXPENSE_NAME] - $[AMOUNT] |
| 11 | Message | See template ⬇️ |
| 12 | Turn ON | |

**Email Template:**
```
EXPENSE PAYMENT DUE

Expense: [EXPENSE_NAME]
Amount: $[AMOUNT]

Category: [CATEGORY]

ACTION: Process payment
```

[ ] COMPLETE [ ] ON

---

## AUTOMATION 18: PROJECT DEADLINE - 7 DAYS

**System:** ATLAS  
**Table:** ATLAS PROJECTS

| Step | Action | Value |
|------|--------|-------|
| 1 | Create automation | |
| 2 | Name | `⏰ Project Deadline - 7 Days` |
| 3 | Trigger | When record matches conditions |
| 4 | Table | ATLAS PROJECTS |
| 5 | Condition 1 | DUE_DATE within next 7 days |
| 6 | Condition 2 | AND STATUS not Completed |
| 7 | Condition 3 | AND STATUS not Cancelled |
| 8 | Add action | Send email |
| 9 | To | info@deedavis.biz |
| 10 | From name | NEXUS Projects |
| 11 | Subject | ⏰ Project Due 7 Days: [PROJECT_NAME] |
| 12 | Message | See template ⬇️ |
| 13 | Turn ON | |

**Email Template:**
```
PROJECT DEADLINE APPROACHING

Project: [PROJECT_NAME]
Client: [CLIENT_NAME]
Due: [DUE_DATE] (7 days)

Status: [STATUS]
Progress: [PROGRESS_PERCENTAGE]%

Budget: [BUDGET]
Used: [BUDGET_USED]

ACTIONS:
1. Review status
2. Check deliverables
3. Coordinate team
4. Final review
```

[ ] COMPLETE [ ] ON

---

## AUTOMATION 19: TASK OVERDUE ALERT

**System:** ATLAS  
**Table:** ATLAS TASKS

| Step | Action | Value |
|------|--------|-------|
| 1 | Create automation | |
| 2 | Name | `⚠️ Task Overdue Alert` |
| 3 | Trigger | When record matches conditions |
| 4 | Table | ATLAS TASKS |
| 5 | Condition 1 | DUE_DATE in the past |
| 6 | Condition 2 | AND STATUS not Done |
| 7 | Condition 3 | AND STATUS not Cancelled |
| 8 | Add action | Send email |
| 9 | To | info@deedavis.biz |
| 10 | From name | NEXUS Tasks |
| 11 | Subject | ⚠️ Overdue Task: [TASK_NAME] |
| 12 | Message | See template ⬇️ |
| 13 | Turn ON | |

**Email Template:**
```
TASK OVERDUE

Task: [TASK_NAME]
Project: [Link to PROJECT]

Was Due: [DUE_DATE]
Priority: [PRIORITY]
Assigned: [ASSIGNED_TO]

ACTION: Complete and update
```

[ ] COMPLETE [ ] ON

---

## AUTOMATION 20: PROJECT KICKOFF REMINDER

**System:** ATLAS  
**Table:** ATLAS PROJECTS

| Step | Action | Value |
|------|--------|-------|
| 1 | Create automation | |
| 2 | Name | `🚀 Project Kickoff Reminder` |
| 3 | Trigger | When record created |
| 4 | Table | ATLAS PROJECTS |
| 5 | Condition | START_DATE within next 3 days |
| 6 | Add action | Send email |
| 7 | To | info@deedavis.biz |
| 8 | From name | NEXUS Projects |
| 9 | Subject | 🚀 Kickoff Soon: [PROJECT_NAME] |
| 10 | Message | See template ⬇️ |
| 11 | Turn ON | |

**Email Template:**
```
PROJECT KICKOFF APPROACHING

Project: [PROJECT_NAME]
Client: [CLIENT_NAME]
Start: [START_DATE]

PREPARE:
1. Review scope
2. Prepare agenda
3. Confirm team
4. Set up comms
5. Review expectations

Budget: [BUDGET]
```

[ ] COMPLETE [ ] ON

---

## AUTOMATION 21: NEW AI RECOMMENDATION

**System:** AI  
**Table:** AI RECOMMENDATIONS

| Step | Action | Value |
|------|--------|-------|
| 1 | Create automation | |
| 2 | Name | `🤖 New AI Recommendation` |
| 3 | Trigger | When record created |
| 4 | Table | AI RECOMMENDATIONS |
| 5 | Condition | STATUS is Pending Approval |
| 6 | Add action | Send email |
| 7 | To | info@deedavis.biz |
| 8 | From name | NEXUS AI |
| 9 | Subject | 🤖 AI RECOMMENDATION: [TYPE] |
| 10 | Message | See template ⬇️ |
| 11 | Turn ON | |

**Email Template:**
```
NEW AI RECOMMENDATION

Type: [TYPE]
Opportunity: [OPPORTUNITY]

RECOMMENDATION:
[RECOMMENDATION]

CONFIDENCE: [CONFIDENCE]%

REASONING:
[REASONING]

ACTION: Review and approve/deny
```

[ ] COMPLETE [ ] ON

---

## AUTOMATION 22: HIGH CONFIDENCE AI

**System:** AI  
**Table:** AI RECOMMENDATIONS

| Step | Action | Value |
|------|--------|-------|
| 1 | Create automation | |
| 2 | Name | `⚡ High Confidence AI` |
| 3 | Trigger | When record created |
| 4 | Table | AI RECOMMENDATIONS |
| 5 | Condition | CONFIDENCE >= 90 |
| 6 | Add action | Send email |
| 7 | To | info@deedavis.biz |
| 8 | From name | NEXUS AI Priority |
| 9 | Subject | ⚡ HIGH CONFIDENCE ([CONFIDENCE]%): [TYPE] |
| 10 | Message | See template ⬇️ |
| 11 | Turn ON | |

**Email Template:**
```
⚡ HIGH CONFIDENCE AI

Type: [TYPE]
Confidence: [CONFIDENCE]% ⭐

RECOMMENDATION:
[RECOMMENDATION]

REASONING:
[REASONING]

AI very confident.
Quick review recommended.

✅ Approve if looks good
❌ Deny if issues
```

[ ] COMPLETE [ ] ON

---

## AUTOMATION 23: LOW CONFIDENCE AI WARNING

**System:** AI  
**Table:** AI RECOMMENDATIONS

| Step | Action | Value |
|------|--------|-------|
| 1 | Create automation | |
| 2 | Name | `⚠️ Low Confidence AI` |
| 3 | Trigger | When record created |
| 4 | Table | AI RECOMMENDATIONS |
| 5 | Condition | CONFIDENCE < 70 |
| 6 | Add action | Send email |
| 7 | To | info@deedavis.biz |
| 8 | From name | NEXUS AI |
| 9 | Subject | ⚠️ LOW CONFIDENCE ([CONFIDENCE]%): [TYPE] |
| 10 | Message | See template ⬇️ |
| 11 | Turn ON | |

**Email Template:**
```
⚠️ LOW CONFIDENCE AI

Type: [TYPE]
Confidence: [CONFIDENCE]% ⚠️

RECOMMENDATION:
[RECOMMENDATION]

⚠️ CAUTION:
AI is uncertain.
Deep review recommended.

📊 Review all options
🔍 Verify carefully
💭 Use your expertise
```

[ ] COMPLETE [ ] ON

---

## AUTOMATION 24: OFFICER FOLLOW-UP REMINDER

**System:** Officer Outreach  
**Table:** Officer Outreach Tracking

| Step | Action | Value |
|------|--------|-------|
| 1 | Create automation | |
| 2 | Name | `📬 Officer Follow-Up Reminder` |
| 3 | Trigger | When record matches conditions |
| 4 | Table | Officer Outreach Tracking |
| 5 | Condition 1 | Follow-up Date is today or past |
| 6 | Condition 2 | AND Status is Sent |
| 7 | Condition 3 | AND Response Received not checked |
| 8 | Add action | Update record |
| 9 | Field to update | Status → Follow-up Needed |
| 10 | Add action | Send email |
| 11 | To | info@deedavis.biz |
| 12 | From name | NEXUS Outreach |
| 13 | Subject | 📬 Follow-Up: [Officer Name] - [Agency] |
| 14 | Message | See template ⬇️ |
| 15 | Turn ON | |

**Email Template:**
```
⏰ FOLLOW-UP REMINDER

Officer: [Officer Name]
Email: [Officer Email]
Agency: [Agency]

Original: [Opportunity Title]
Letter Sent: [Date Sent]
Days Since: [Calculate]

FOLLOW-UP:
"Hi [Officer Name],

Following up on email from [Date Sent] 
regarding [Opportunity Title].

Appreciate being added to vendor list 
for future opportunities.

10 minute call?"
```

[ ] COMPLETE [ ] ON

---

## AUTOMATION 25: OFFICER RESPONSE RECEIVED

**System:** Officer Outreach  
**Table:** Officer Outreach Tracking

| Step | Action | Value |
|------|--------|-------|
| 1 | Create automation | |
| 2 | Name | `🎉 Officer Responded` |
| 3 | Trigger | When record matches conditions |
| 4 | Table | Officer Outreach Tracking |
| 5 | Condition | Response Received checked |
| 6 | Add action | Update record |
| 7 | Field to update (1) | Status → Responded |
| 8 | Field to update (2) | Response Date → TODAY() |
| 9 | Add action | Send email |
| 10 | To | info@deedavis.biz |
| 11 | From name | NEXUS Outreach |
| 12 | Subject | 🎉 Officer Responded: [Officer Name] - [Agency] |
| 13 | Message | See template ⬇️ |
| 14 | Turn ON | |

**Email Template:**
```
🎉 SUCCESS! OFFICER RESPONDED

Officer: [Officer Name]
Agency: [Agency]

Response Date: [Response Date]
Days to Response: [Calculate]

Notes: [Response Notes]

NEXT STEPS:
1. Review response
2. Ask for vendor list
3. Send capability statement
4. Request opportunities
5. Schedule call
6. Add to CRM
```

[ ] COMPLETE [ ] ON

---

## AUTOMATION 26: ADDED TO VENDOR LIST

**System:** Officer Outreach  
**Table:** Officer Outreach Tracking

| Step | Action | Value |
|------|--------|-------|
| 1 | Create automation | |
| 2 | Name | `🎯 Added to Vendor List` |
| 3 | Trigger | When record matches conditions |
| 4 | Table | Officer Outreach Tracking |
| 5 | Condition | Added to Vendor List checked |
| 6 | Add action | Update record |
| 7 | Field to update | Status → Added to Vendor List |
| 8 | Add action | Send email |
| 9 | To | info@deedavis.biz |
| 10 | From name | NEXUS Success |
| 11 | Subject | 🎯 VENDOR LIST: [Agency] |
| 12 | Message | See template ⬇️ |
| 13 | Turn ON | |

**Email Template:**
```
🎯 ADDED TO VENDOR LIST!

Officer: [Officer Name]
Agency: [Agency]

Started from: [Opportunity Title]

Timeline:
Letter Sent: [Date Sent]
Response: [Response Date]
Added: TODAY

Days to Success: [Calculate]

NEXT:
1. Thank them
2. Request notifications
3. Quarterly updates
4. Monitor opportunities
5. Build relationship

Future awards possible!
```

[ ] COMPLETE [ ] ON

---

---

# ✅ CRITICAL EMAIL AUTOMATIONS STATUS

| # | Automation | System | Table | Status |
|---|------------|--------|-------|--------|
| 1 | Bid Deadline Alert (48h) | GPSS | GPSS OPPORTUNITIES | ✅ DONE |
| 2 | Quote Due Reminder (24h) | GPSS | GPSS SUBCONTRACTOR QUOTES | ✅ DONE |
| 3 | Quote Received | GPSS | GPSS SUBCONTRACTOR QUOTES | ✅ DONE |
| 4 | New Opportunity Alert | GPSS | GPSS OPPORTUNITIES | ✅ DONE |
| 5 | Supplier Non-Response | GPSS | GPSS SUBCONTRACTOR QUOTES | ⏸️ SKIPPED |
| 6 | Winning Bid Workflow | GPSS | GPSS OPPORTUNITIES | ✅ DONE |
| 7 | High-Value Opportunity ($100K+) | GPSS | GPSS OPPORTUNITIES | 🆕 TO SETUP |
| 8 | Delivery Overdue Alert | FULFILLMENT | FULFILLMENT DELIVERIES | 🆕 TO SETUP |
| 9 | Delivery Due TODAY | FULFILLMENT | FULFILLMENT DELIVERIES | 🆕 TO SETUP |
| 10 | Invoice Overdue Alert | VERTEX | VERTEX INVOICES | 🆕 TO SETUP |
| 11 | Payment Received | VERTEX | VERTEX INVOICES | 🆕 TO SETUP |
| 12 | Critical Inventory Shortage | FULFILLMENT | FULFILLMENT INVENTORY | 🆕 TO SETUP |
| 13 | Project Deadline 24 Hours | ATLAS | ATLAS TASKS | 🆕 TO SETUP |
| 14 | Expense Payment Due TODAY | VERTEX | VERTEX EXPENSES | 🆕 TO SETUP |

**Email Automations: 14 total**  
**Already Setup: 5** ✅  
**Skipped: 1** ⏸️  
**To Setup: 8** 🆕

---

# 🟢 DASHBOARD-ONLY NOTIFICATIONS (NO AIRTABLE AUTOMATION NEEDED)

**These notifications appear automatically in your NEXUS dashboard because:**
1. Dashboard reads Airtable every 30 seconds
2. Dashboard has "Activity Stream", "Alerts", and "Deadlines" sections
3. Backend API endpoints pull data automatically

### **Examples of Dashboard-Only:**

**Activity Stream** (shows automatically):
- ✅ New opportunity created → Shows in activity
- ✅ Quote received → Shows in activity
- ✅ Contact added → Shows in activity
- ✅ Project updated → Shows in activity
- ✅ Task completed → Shows in activity
- ✅ Invoice generated → Shows in activity

**Alerts Section** (shows automatically):
- ✅ Upcoming deadlines (within 7 days) → Shows in alerts
- ✅ Overdue tasks → Shows in alerts
- ✅ Low inventory → Shows in alerts
- ✅ AI recommendations → Shows in alerts

**Deadlines Section** (shows automatically):
- ✅ All GPSS opportunities with due dates
- ✅ All ATLAS tasks with due dates
- ✅ All deliveries with scheduled dates

### **Why No Automation Needed:**

Your `api_server.py` already has these endpoints working:
- `/dashboard/activity` → Pulls last 10 activities
- `/dashboard/alerts` → Checks for urgent items
- `getDashboardStats()` → Calculates all metrics

Your `LandingPage.tsx` already refreshes every 30 seconds automatically!

**Result:** You only need email automations for CRITICAL items that need immediate action outside of NEXUS.

---

# 🎯 NEXT STEPS

## **Step 1: Complete Critical Email Automations (30 minutes)**
Set up the remaining 8 email automations (#7-14) using the grids above.

## **Step 2: Verify Dashboard is Working**
1. Open NEXUS at `http://localhost:3000`
2. Check "Activity Stream" shows recent changes
3. Check "Alerts" shows urgent items
4. Check "Deadlines" shows upcoming due dates
5. Wait 30 seconds and see it auto-refresh

## **Step 3: Test Full System**
1. Create test opportunity with deadline in 2 days
2. Verify email alert received (Automation #1)
3. Check dashboard shows it in "Alerts" section
4. Mark status as "Won"
5. Verify email alert received (Automation #6)
6. Check dashboard shows it in "Activity Stream"

## **Step 4: Add Nice-to-Have Automations (Optional)**
After critical ones work, you can add:
- Weekly digest email (summary of all activity)
- Monthly reports
- Performance tracking
- Custom alerts for specific scenarios

---

# 🚀 YOU'RE ALMOST READY!

**5 critical automations** ✅ Already working  
**8 critical automations** 🆕 Setup in ~30 minutes  
**100+ notifications** 🟢 Already working via dashboard  

**Total setup time remaining: 30 minutes**

---

**Ready to setup Automations #7-14? Start with #7 at the top of this file!**
