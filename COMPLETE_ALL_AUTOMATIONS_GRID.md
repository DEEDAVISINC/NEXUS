# ALL 45 NEXUS AUTOMATIONS - COMPLETE GRID
**Set up ALL automations across EVERY system**

---

## 📊 SYSTEMS COVERED:

| System | Automations | Priority |
|--------|-------------|----------|
| 1. GPSS Bid Tracking | 5 | ✅ **DONE (5/5)** |
| 2. Fulfillment System | 8 | 🔴 CRITICAL |
| 3. VERTEX Financial | 4 | 🔴 CRITICAL |
| 4. ATLAS Projects | 3 | 🟡 IMPORTANT |
| 5. AI Recommendations | 4 | 🟡 IMPORTANT |
| 6. Officer Outreach | 4 | 🔴 CRITICAL |
| 7. Subcontractor Mgmt | 4 | 🟡 IMPORTANT |
| 8. Supplier Management | 2 | 🟢 NICE TO HAVE |
| 9. Proposal Quality | 3 | 🔴 CRITICAL |
| 10. LBPC Surplus | 3 | 🟡 IMPORTANT |
| 11. DDCSS Marketing | 2 | 🟢 NICE TO HAVE |
| 12. Cross-System | 3 | 🟢 NICE TO HAVE |
| **TOTAL** | **45** | **5 done, 40 to go** |

---

## 🎯 RECOMMENDED ORDER:

1. **CRITICAL** (15 automations) - Do these next
2. **IMPORTANT** (18 automations) - Do after critical
3. **NICE TO HAVE** (7 automations) - Do when ready
4. **DONE** (5 automations) - Already complete ✅

---

# 🔴 CRITICAL AUTOMATIONS (DO NEXT - 15 automations)

---

## 🔴 AUTOMATION 7: LOW INVENTORY ALERT

**System:** Fulfillment  
**Table:** FULFILLMENT INVENTORY

| Step | What to Click | What to Select/Type |
|------|---------------|---------------------|
| 1 | Create automation | - |
| 2 | Name | `🟡 Low Inventory Alert` |
| 3 | Trigger | When record matches conditions |
| 4 | Table | `FULFILLMENT INVENTORY` |
| 5 | Condition 1 | `QUANTITY_ON_HAND` < `REORDER_POINT` |
| 6 | Condition 2 | AND `STATUS` is not `Out of Stock` |
| 7 | Close trigger | - |
| 8 | Add action | Update record |
| 9 | Field to update | `STATUS` → `Low Stock` |
| 10 | Close update | - |
| 11 | Add action | Send email |
| 12 | To | `info@deedavis.biz` |
| 13 | From name | `NEXUS Inventory` |
| 14 | Subject | `🟡 LOW INVENTORY: ` + [PRODUCT_NAME] |
| 15 | Message | See template ⬇️ |
| 16 | Close email | - |
| 17 | Turn ON | - |

**Template:**
```
REORDER RECOMMENDED

Product: [PRODUCT_NAME]
SKU: [PRODUCT_SKU]
━━━━━━━━━━━━━━━━━━━━━━━━
Current Stock: [QUANTITY_ON_HAND] units
Reorder Point: [REORDER_POINT] units
Recommended Order: [REORDER_QUANTITY] units

Committed: [QUANTITY_COMMITTED] units
Available: [QUANTITY_AVAILABLE] units

Supplier: [SUPPLIER]
Unit Cost: [UNIT_COST]
━━━━━━━━━━━━━━━━━━━━━━━━
ACTION: Create purchase order
```

**Status:** [ ] COMPLETE [ ] ON

---

## 🔴 AUTOMATION 8: CRITICAL INVENTORY SHORTAGE

**System:** Fulfillment  
**Table:** FULFILLMENT INVENTORY

| Step | What to Click | What to Select/Type |
|------|---------------|---------------------|
| 1 | Create automation | - |
| 2 | Name | `🚨 Critical Inventory Shortage` |
| 3 | Trigger | When record matches conditions |
| 4 | Table | `FULFILLMENT INVENTORY` |
| 5 | Condition 1 | `QUANTITY_AVAILABLE` < `0` |
| 6 | Condition 2 | OR `STATUS` is `Critical` |
| 7 | Close trigger | - |
| 8 | Add action | Update record |
| 9 | Field to update | `STATUS` → `Critical` |
| 10 | Close update | - |
| 11 | Add action | Send email |
| 12 | To | `info@deedavis.biz` |
| 13 | From name | `NEXUS URGENT` |
| 14 | Subject | `🚨 CRITICAL SHORTAGE: ` + [PRODUCT_NAME] |
| 15 | Message | See template ⬇️ |
| 16 | Close email | - |
| 17 | Turn ON | - |

**Template:**
```
⚠️ CRITICAL INVENTORY ALERT ⚠️

Product: [PRODUCT_NAME]
SKU: [PRODUCT_SKU]
━━━━━━━━━━━━━━━━━━━━━━━━
SHORTAGE:
On Hand: [QUANTITY_ON_HAND]
Committed: [QUANTITY_COMMITTED]
Available: [QUANTITY_AVAILABLE] (NEGATIVE!)

Active Contracts: [ACTIVE_CONTRACTS]
━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ URGENT:
1. Emergency purchase order
2. Contact supplier - expedite
3. Review deliveries - may delay

Supplier: [SUPPLIER]
Order: [REORDER_QUANTITY] minimum
```

**Status:** [ ] COMPLETE [ ] ON

---

## 🔴 AUTOMATION 9: DELIVERY DUE IN 7 DAYS

**System:** Fulfillment  
**Table:** FULFILLMENT DELIVERIES

| Step | What to Click | What to Select/Type |
|------|---------------|---------------------|
| 1 | Create automation | - |
| 2 | Name | `📦 Delivery Due in 7 Days` |
| 3 | Trigger | When record matches conditions |
| 4 | Table | `FULFILLMENT DELIVERIES` |
| 5 | Condition 1 | `DUE_DATE` is within `the next 7 days` |
| 6 | Condition 2 | AND `STATUS` is `Scheduled` |
| 7 | Close trigger | - |
| 8 | Add action | Send email |
| 9 | To | `info@deedavis.biz` |
| 10 | From name | `NEXUS Deliveries` |
| 11 | Subject | `📦 Delivery Due in 7 Days: ` + [DELIVERY_ID] |
| 12 | Message | See template ⬇️ |
| 13 | Close email | - |
| 14 | Turn ON | - |

**Template:**
```
UPCOMING DELIVERY REMINDER

Delivery ID: [DELIVERY_ID]
━━━━━━━━━━━━━━━━━━━━━━━━
Due: [DUE_DATE]
Quantity: [QUANTITY] units
Status: [STATUS]

Contract: [Link to CONTRACT]
━━━━━━━━━━━━━━━━━━━━━━━━
ACTION:
1. Verify inventory available
2. Prepare shipment
3. Confirm carrier
4. Schedule pickup
```

**Status:** [ ] COMPLETE [ ] ON

---

## 🔴 AUTOMATION 10: INVOICE OVERDUE ALERT

**System:** VERTEX Financial  
**Table:** VERTEX INVOICES

| Step | What to Click | What to Select/Type |
|------|---------------|---------------------|
| 1 | Create automation | - |
| 2 | Name | `💰 Invoice Overdue Alert` |
| 3 | Trigger | When record matches conditions |
| 4 | Table | `VERTEX INVOICES` |
| 5 | Condition 1 | `DUE_DATE` is `in the past` |
| 6 | Condition 2 | AND `STATUS` is not `Paid` |
| 7 | Condition 3 | AND `STATUS` is not `Cancelled` |
| 8 | Close trigger | - |
| 9 | Add action | Update record |
| 10 | Field to update | `STATUS` → `Overdue` |
| 11 | Close update | - |
| 12 | Add action | Send email |
| 13 | To | `info@deedavis.biz` |
| 14 | From name | `NEXUS Financial` |
| 15 | Subject | `💰 OVERDUE: ` + [CLIENT_NAME] + ` - $` + [INVOICE_AMOUNT] |
| 16 | Message | See template ⬇️ |
| 17 | Close email | - |
| 18 | Turn ON | - |

**Template:**
```
⚠️ INVOICE OVERDUE

Client: [CLIENT_NAME]
Amount: [INVOICE_AMOUNT]
━━━━━━━━━━━━━━━━━━━━━━━━
Invoice Date: [INVOICE_DATE]
Due Date: [DUE_DATE]
Days Overdue: [Calculate]

Description: [DESCRIPTION]
━━━━━━━━━━━━━━━━━━━━━━━━
ACTION:
1. Send payment reminder
2. Follow up via phone
3. Escalate if > 30 days
4. Update when paid
```

**Status:** [ ] COMPLETE [ ] ON

---

## 🔴 AUTOMATION 11: INVOICE DUE SOON

**System:** VERTEX Financial  
**Table:** VERTEX INVOICES

| Step | What to Click | What to Select/Type |
|------|---------------|---------------------|
| 1 | Create automation | - |
| 2 | Name | `⏰ Invoice Due in 5 Days` |
| 3 | Trigger | When record matches conditions |
| 4 | Table | `VERTEX INVOICES` |
| 5 | Condition 1 | `DUE_DATE` is within `the next 5 days` |
| 6 | Condition 2 | AND `STATUS` is `Sent` |
| 7 | Close trigger | - |
| 8 | Add action | Send email |
| 9 | To | `info@deedavis.biz` |
| 10 | From name | `NEXUS Financial` |
| 11 | Subject | `⏰ Invoice Due Soon: ` + [CLIENT_NAME] + ` - $` + [INVOICE_AMOUNT] |
| 12 | Message | See template ⬇️ |
| 13 | Close email | - |
| 14 | Turn ON | - |

**Template:**
```
INVOICE DUE IN 5 DAYS

Client: [CLIENT_NAME]
Amount: [INVOICE_AMOUNT]
Due: [DUE_DATE]
━━━━━━━━━━━━━━━━━━━━━━━━
RECOMMENDED:
Send friendly reminder:

"Just a reminder that invoice #[ID] for 
$[INVOICE_AMOUNT] is due on [DUE_DATE]. 
Please let me know if you have questions."
```

**Status:** [ ] COMPLETE [ ] ON

---

## 🔴 AUTOMATION 12: OFFICER OUTREACH FOLLOW-UP

**System:** Officer Outreach  
**Table:** Officer Outreach Tracking

| Step | What to Click | What to Select/Type |
|------|---------------|---------------------|
| 1 | Create automation | - |
| 2 | Name | `📬 Officer Follow-Up Reminder` |
| 3 | Trigger | When record matches conditions |
| 4 | Table | `Officer Outreach Tracking` |
| 5 | Condition 1 | `Follow-up Date` is `today` or `in the past` |
| 6 | Condition 2 | AND `Status` is `Sent` |
| 7 | Condition 3 | AND `Response Received` is not checked |
| 8 | Close trigger | - |
| 9 | Add action | Update record |
| 10 | Field to update | `Status` → `Follow-up Needed` |
| 11 | Close update | - |
| 12 | Add action | Send email |
| 13 | To | `info@deedavis.biz` |
| 14 | From name | `NEXUS Outreach` |
| 15 | Subject | `📬 Follow-Up: ` + [Officer Name] + ` - ` + [Agency] |
| 16 | Message | See template ⬇️ |
| 17 | Close email | - |
| 18 | Turn ON | - |

**Template:**
```
⏰ FOLLOW-UP REMINDER

Officer: [Officer Name]
Email: [Officer Email]
Agency: [Agency]
━━━━━━━━━━━━━━━━━━━━━━━━
Original Opportunity: [Opportunity Title]
Solicitation #: [Solicitation Number]
Letter Sent: [Date Sent]
Days Since: [Calculate]
Follow-up Due: [Follow-up Date]
━━━━━━━━━━━━━━━━━━━━━━━━
RECOMMENDED FOLLOW-UP:

"Hi [Officer Name],

Following up on my email from [Date Sent] 
regarding [Opportunity Title].

Would appreciate being added to your vendor 
list for future opportunities.

Would you have 10 minutes for a brief call?"
━━━━━━━━━━━━━━━━━━━━━━━━
ACTION: Send follow-up email
```

**Status:** [ ] COMPLETE [ ] ON

---

## 🔴 AUTOMATION 13: OFFICER RESPONSE RECEIVED

**System:** Officer Outreach  
**Table:** Officer Outreach Tracking

| Step | What to Click | What to Select/Type |
|------|---------------|---------------------|
| 1 | Create automation | - |
| 2 | Name | `🎉 Officer Responded` |
| 3 | Trigger | When record matches conditions |
| 4 | Table | `Officer Outreach Tracking` |
| 5 | Condition 1 | `Response Received` checkbox is `checked` |
| 6 | Close trigger | - |
| 7 | Add action | Update record |
| 8 | Field to update (1) | `Status` → `Responded` |
| 9 | Field to update (2) | `Response Date` → `TODAY()` |
| 10 | Close update | - |
| 11 | Add action | Send email |
| 12 | To | `info@deedavis.biz` |
| 13 | From name | `NEXUS Outreach` |
| 14 | Subject | `🎉 Officer Responded: ` + [Officer Name] + ` - ` + [Agency] |
| 15 | Message | See template ⬇️ |
| 16 | Close email | - |
| 17 | Turn ON | - |

**Template:**
```
🎉 SUCCESS! OFFICER RESPONDED

Officer: [Officer Name]
Agency: [Agency]
━━━━━━━━━━━━━━━━━━━━━━━━
Response Date: [Response Date]
Days to Response: [Calculate]

Response Notes: [Response Notes]
━━━━━━━━━━━━━━━━━━━━━━━━
NEXT STEPS:
1. Review response in detail
2. Ask to join vendor list
3. Send capability statement
4. Request upcoming opportunities
5. Schedule follow-up call
6. Add to CRM
```

**Status:** [ ] COMPLETE [ ] ON

---

## 🔴 AUTOMATION 14: LOW PROPOSAL QUALITY ALERT

**System:** Proposal Quality  
**Table:** GPSS Proposals

| Step | What to Click | What to Select/Type |
|------|---------------|---------------------|
| 1 | Create automation | - |
| 2 | Name | `⚠️ Low Proposal Quality Alert` |
| 3 | Trigger | When record matches conditions |
| 4 | Table | `GPSS Proposals` |
| 5 | Condition 1 | `ProposalBio Score` < `70` |
| 6 | Condition 2 | AND `Status` is `Draft` OR `Review` |
| 7 | Close trigger | - |
| 8 | Add action | Send email |
| 9 | To | `info@deedavis.biz` |
| 10 | From name | `NEXUS Quality` |
| 11 | Subject | `⚠️ LOW QUALITY: ` + [Proposal Name] |
| 12 | Message | See template ⬇️ |
| 13 | Close email | - |
| 14 | Turn ON | - |

**Template:**
```
⚠️ PROPOSAL QUALITY ALERT

Proposal: [Proposal Name]
RFP: [RFP Number]
━━━━━━━━━━━━━━━━━━━━━━━━
QUALITY: [ProposalBio Score]/100 ⚠️
Status: [Quality Status]
Badge: [Quality Badge]

Value: [Opportunity Value]
Due: [Due Date]
━━━━━━━━━━━━━━━━━━━━━━━━
ISSUES:
[Improvement Notes]
━━━━━━━━━━━━━━━━━━━━━━━━
CRITICAL ACTION:
1. Review ProposalBio™ recommendations
2. Revise proposal
3. Re-run quality check
4. Target 80+ before submission

Do NOT submit below 70!
```

**Status:** [ ] COMPLETE [ ] ON

---

## 🔴 AUTOMATION 15: PROPOSAL READY TO SEND

**System:** Proposal Quality  
**Table:** GPSS Proposals

| Step | What to Click | What to Select/Type |
|------|---------------|---------------------|
| 1 | Create automation | - |
| 2 | Name | `✅ Proposal Quality Check Passed` |
| 3 | Trigger | When record matches conditions |
| 4 | Table | `GPSS Proposals` |
| 5 | Condition 1 | `ProposalBio Score` >= `80` |
| 6 | Condition 2 | OR `Quality Status` is `Ready to Send` |
| 7 | Close trigger | - |
| 8 | Add action | Update record |
| 9 | Field to update | `Status` → `Ready to Send` |
| 10 | Close update | - |
| 11 | Add action | Send email |
| 12 | To | `info@deedavis.biz` |
| 13 | From name | `NEXUS Quality` |
| 14 | Subject | `✅ PROPOSAL READY: ` + [Proposal Name] |
| 15 | Message | See template ⬇️ |
| 16 | Close email | - |
| 17 | Turn ON | - |

**Template:**
```
✅ PROPOSAL QUALITY CHECK PASSED

Proposal: [Proposal Name]
RFP: [RFP Number]
Agency: [Agency Name]
━━━━━━━━━━━━━━━━━━━━━━━━
QUALITY: [ProposalBio Score]/100 ✅
Status: Ready to Send
Badge: [Quality Badge]

Value: [Opportunity Value]
Due: [Due Date]
Days Until Due: [Calculate]
━━━━━━━━━━━━━━━━━━━━━━━━
NEXT STEPS:
1. Final executive review
2. Prepare submission package
3. Verify attachments
4. Submit before [Due Date]
5. Update status to "Sent"

Proposal meets all quality standards!
```

**Status:** [ ] COMPLETE [ ] ON

---

## 🔴 AUTOMATION 16: PROPOSAL DEADLINE WARNING

**System:** Proposal Quality  
**Table:** GPSS Proposals

| Step | What to Click | What to Select/Type |
|------|---------------|---------------------|
| 1 | Create automation | - |
| 2 | Name | `🚨 Proposal Deadline - 48 Hours` |
| 3 | Trigger | When record matches conditions |
| 4 | Table | `GPSS Proposals` |
| 5 | Condition 1 | `Due Date` is within `the next 2 days` |
| 6 | Condition 2 | AND `Status` is not `Sent` |
| 7 | Condition 3 | AND `Status` is not `Withdrawn` |
| 8 | Close trigger | - |
| 9 | Add action | Send email |
| 10 | To | `info@deedavis.biz` |
| 11 | From name | `NEXUS Deadlines` |
| 12 | Subject | `🚨 PROPOSAL DUE 48 HRS: ` + [Proposal Name] |
| 13 | Message | See template ⬇️ |
| 14 | Close email | - |
| 15 | Turn ON | - |

**Template:**
```
🚨 URGENT: PROPOSAL DUE IN 48 HOURS

Proposal: [Proposal Name]
RFP: [RFP Number]
Agency: [Agency Name]
━━━━━━━━━━━━━━━━━━━━━━━━
⏰ DUE: [Due Date] (48 hours!)
Status: [Status]
Quality: [ProposalBio Score]/100
Value: [Opportunity Value]
━━━━━━━━━━━━━━━━━━━━━━━━
CRITICAL ACTIONS:
1. Complete sections
2. Run final quality check
3. Get executive approval
4. Prepare submission
5. SUBMIT BEFORE DEADLINE

Don't lose this $[Opportunity Value] opportunity!
```

**Status:** [ ] COMPLETE [ ] ON

---

# ✅ CRITICAL AUTOMATIONS CHECKLIST (15 total)

| # | Automation | System | Status |
|---|------------|--------|--------|
| 1-6 | GPSS Bid Tracking | GPSS | ✅ **DONE** |
| 7 | Low Inventory Alert | Fulfillment | [ ] |
| 8 | Critical Inventory Shortage | Fulfillment | [ ] |
| 9 | Delivery Due in 7 Days | Fulfillment | [ ] |
| 10 | Invoice Overdue Alert | VERTEX | [ ] |
| 11 | Invoice Due Soon | VERTEX | [ ] |
| 12 | Officer Follow-Up Reminder | Outreach | [ ] |
| 13 | Officer Response Received | Outreach | [ ] |
| 14 | Low Proposal Quality Alert | Proposals | [ ] |
| 15 | Proposal Ready to Send | Proposals | [ ] |
| 16 | Proposal Deadline Warning | Proposals | [ ] |

---

**Want to continue? Tell me:**
- **"done with critical"** when you finish all 15
- **"show me important automations"** for the next 18
- **"show me one at a time"** if you want step-by-step

---

**PROGRESS: 5/45 complete (11%)**  
**NEXT: 10 more critical automations to set up**
