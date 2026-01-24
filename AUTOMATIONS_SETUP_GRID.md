# AIRTABLE AUTOMATIONS SETUP - GRID FORMAT

---

## 🔴 AUTOMATION 1: BID DEADLINE ALERT (48 HOURS)

| Step | Action | Value |
|------|--------|-------|
| **1** | Open Automations | Click lightning bolt icon → Create automation |
| **2** | Name | `🚨 Bid Deadline Alert - 48 Hours` |
| **3** | Trigger Type | When record matches conditions |
| **4** | Table | `GPSS OPPORTUNITIES` |
| **5** | Condition 1 | When `Deadline` is within `the next 2 days` |
| **6** | Condition 2 | AND `Status` is one of: `Awaiting Quotes`, `Ready to Bid`, `In Progress` |
| **7** | Action Type | Send email |
| **8** | To | `info@deedavis.biz` |
| **9** | Subject | `🚨 BID DUE IN 48 HOURS: {Name}` |
| **10** | Body | See template below ⬇️ |
| **11** | Test | Click "Test automation" |
| **12** | Turn ON | Toggle to ON |

### Email Body Template:
```
⚠️ URGENT: BID DEADLINE APPROACHING

RFP: {Name}
RFP Number: {RFP NUMBER}
Agency: {AGENCY}
━━━━━━━━━━━━━━━━━━━━━━━━
⏰ DEADLINE: {Deadline}
   (48 hours from now)

Status: {Status}
Priority: {Priority}

Value: ${Estimated Value}
Profit: ${Est Profit}
━━━━━━━━━━━━━━━━━━━━━━━━
📋 CHECKLIST:
□ All quotes received?
□ Pricing calculated?
□ Bid forms completed?
□ Submission confirmed?

Officer: {CONTRACTING OFFICER}
Contacts: {Contacts Extracted}

🔗 View: [Link to record]
⚠️ ACTION REQUIRED WITHIN 48 HOURS
```

**Status:** [ ] COMPLETE

---

## 🔴 AUTOMATION 2: QUOTE DUE REMINDER (24 HOURS)

| Step | Action | Value |
|------|--------|-------|
| **1** | Create Automation | Click Create automation |
| **2** | Name | `⏰ Quote Due Reminder - 24 Hours` |
| **3** | Trigger Type | When record matches conditions |
| **4** | Table | `GPSS SUBCONTRACTOR QUOTES` |
| **5** | Condition 1 | When `Quote Due Date` is within `the next 1 day` |
| **6** | Condition 2 | AND `Status` is `Pending` |
| **7** | Action Type | Send email |
| **8** | To | `info@deedavis.biz` |
| **9** | Subject | `⏰ QUOTE DUE TOMORROW: {Subcontractor} for {Opportunity}` |
| **10** | Body | See template below ⬇️ |
| **11** | Test | Click "Test automation" |
| **12** | Turn ON | Toggle to ON |

### Email Body Template:
```
⏰ QUOTE REMINDER: DUE IN 24 HOURS

Supplier: {Subcontractor → COMPANY NAME}
Opportunity: {Opportunity → Name}
RFP: {Opportunity → RFP NUMBER}
━━━━━━━━━━━━━━━━━━━━━━━━
⏰ QUOTE DUE: {Quote Due Date} (Tomorrow!)

CONTACT:
Email: {Subcontractor → EMAIL}
Phone: {Subcontractor → PHONE}
Service: {Subcontractor → SERVICE TYPE}
━━━━━━━━━━━━━━━━━━━━━━━━
📋 ACTION:
□ Call supplier to follow up
□ Send reminder email
□ Check if quote received
□ Update status

🔗 View: [Link to record]
⚠️ FOLLOW UP TODAY
```

**Status:** [ ] COMPLETE

---

## 🔴 AUTOMATION 3: QUOTE RECEIVED NOTIFICATION

| Step | Action | Value |
|------|--------|-------|
| **1** | Create Automation | Click Create automation |
| **2** | Name | `✅ Quote Received Notification` |
| **3** | Trigger Type | When record matches conditions |
| **4** | Table | `GPSS SUBCONTRACTOR QUOTES` |
| **5** | Condition 1 | When `Status` becomes `Received` |
| **6** | Action Type | Send email |
| **7** | To | `info@deedavis.biz` |
| **8** | Subject | `✅ QUOTE RECEIVED: {Subcontractor} for {Opportunity}` |
| **9** | Body | See template below ⬇️ |
| **10** | Test | Click "Test automation" |
| **11** | Turn ON | Toggle to ON |

### Email Body Template:
```
✅ NEW QUOTE RECEIVED

From: {Subcontractor → COMPANY NAME}
For: {Opportunity → Name}
━━━━━━━━━━━━━━━━━━━━━━━━
💰 AMOUNT: ${Quote Amount}

Contact: {Subcontractor → EMAIL}
Phone: {Subcontractor → PHONE}
━━━━━━━━━━━━━━━━━━━━━━━━
OPPORTUNITY:
RFP: {Opportunity → RFP NUMBER}
Agency: {Opportunity → AGENCY}
Deadline: {Opportunity → Deadline}
Est Value: ${Opportunity → Estimated Value}
━━━━━━━━━━━━━━━━━━━━━━━━
TIMELINE:
RFQ Sent: {RFQ Sent Date}
Due: {Quote Due Date}
Received: {CREATED DATE}
━━━━━━━━━━━━━━━━━━━━━━━━
📋 NEXT STEPS:
□ Review quote
□ Calculate markup
□ Compare quotes
□ Update opportunity
□ Prepare bid

Notes: {Notes}

🔗 View: [Link to record]
✅ QUOTE IN HAND - READY TO BID
```

**Status:** [ ] COMPLETE

---

## 🔴 AUTOMATION 4: NEW OPPORTUNITY ALERT

| Step | Action | Value |
|------|--------|-------|
| **1** | Create Automation | Click Create automation |
| **2** | Name | `🆕 New Opportunity Alert` |
| **3** | Trigger Type | When record created |
| **4** | Table | `GPSS OPPORTUNITIES` |
| **5** | Action Type | Send email |
| **6** | To | `info@deedavis.biz` |
| **7** | Subject | `🆕 NEW OPPORTUNITY: {Name}` |
| **8** | Body | See template below ⬇️ |
| **9** | Test | Click "Test automation" |
| **10** | Turn ON | Toggle to ON |

### Email Body Template:
```
🆕 NEW RFP ADDED TO NEXUS

RFP: {Name}
Number: {RFP NUMBER}
Agency: {AGENCY}
━━━━━━━━━━━━━━━━━━━━━━━━
⏰ DEADLINE: {Deadline}

Status: {Status}
Priority: {Priority}
━━━━━━━━━━━━━━━━━━━━━━━━
💰 VALUE:
Estimated: ${Estimated Value}
Profit: ${Est Profit}
━━━━━━━━━━━━━━━━━━━━━━━━
📞 OFFICER:
{CONTRACTING OFFICER}

CONTACTS:
{Contacts Extracted}
━━━━━━━━━━━━━━━━━━━━━━━━
📋 NEXT STEPS:
□ Review RFP requirements
□ Identify suppliers
□ Send quote requests
□ Calculate pricing
□ Prepare bid

🔗 View: [Link to record]
🚀 START WORKING ON THIS BID
```

**Status:** [ ] COMPLETE

---

## 🔴 AUTOMATION 5: SUPPLIER NON-RESPONSE ALERT

| Step | Action | Value |
|------|--------|-------|
| **1** | Create Automation | Click Create automation |
| **2** | Name | `⚠️ Supplier Non-Response Alert` |
| **3** | Trigger Type | When record matches conditions |
| **4** | Table | `GPSS SUBCONTRACTOR QUOTES` |
| **5** | Condition 1 | When `Quote Due Date` is `in the past` |
| **6** | Condition 2 | AND `Status` is `Pending` |
| **7** | Action 1 Type | Update record |
| **8** | Update Field | `Status` → `Overdue` |
| **9** | Action 2 Type | Send email |
| **10** | To | `info@deedavis.biz` |
| **11** | Subject | `⚠️ QUOTE OVERDUE: {Subcontractor} for {Opportunity}` |
| **12** | Body | See template below ⬇️ |
| **13** | Test | Click "Test automation" |
| **14** | Turn ON | Toggle to ON |

### Email Body Template:
```
⚠️ SUPPLIER NOT RESPONDING

Supplier: {Subcontractor → COMPANY NAME}
For: {Opportunity → Name}
━━━━━━━━━━━━━━━━━━━━━━━━
❌ QUOTE OVERDUE
Due: {Quote Due Date}

RFQ Sent: {RFQ Sent Date}
━━━━━━━━━━━━━━━━━━━━━━━━
CONTACT:
Email: {Subcontractor → EMAIL}
Phone: {Subcontractor → PHONE}
Service: {Subcontractor → SERVICE TYPE}
━━━━━━━━━━━━━━━━━━━━━━━━
OPPORTUNITY:
RFP: {Opportunity → RFP NUMBER}
Agency: {Opportunity → AGENCY}
Deadline: {Opportunity → Deadline}
━━━━━━━━━━━━━━━━━━━━━━━━
📋 OPTIONS:
□ Call supplier NOW
□ Send follow-up email
□ Find backup supplier
□ Update opportunity
□ Decide: Wait or move on?

Notes: {Notes}

🔗 View: [Link to record]
⚠️ DECISION NEEDED
```

**Status:** [ ] COMPLETE

---

## 🔴 AUTOMATION 6: WINNING BID WORKFLOW

| Step | Action | Value |
|------|--------|-------|
| **1** | Create Automation | Click Create automation |
| **2** | Name | `🎉 Winning Bid Workflow` |
| **3** | Trigger Type | When record matches conditions |
| **4** | Table | `GPSS OPPORTUNITIES` |
| **5** | Condition 1 | When `Status` becomes `Won` |
| **6** | Action Type | Send email |
| **7** | To | `info@deedavis.biz` |
| **8** | Subject | `🎉 CONTRACT WON: {Name}` |
| **9** | Body | See template below ⬇️ |
| **10** | Test | Click "Test automation" |
| **11** | Turn ON | Toggle to ON |

### Email Body Template:
```
🎉 CONGRATULATIONS - CONTRACT AWARDED!

RFP: {Name}
Number: {RFP NUMBER}
Agency: {AGENCY}
━━━━━━━━━━━━━━━━━━━━━━━━
💰 CONTRACT:
Award: ${Estimated Value}
Profit: ${Est Profit}
━━━━━━━━━━━━━━━━━━━━━━━━
📞 OFFICER:
{CONTRACTING OFFICER}

Contacts: {Contacts Extracted}
━━━━━━━━━━━━━━━━━━━━━━━━
📋 IMMEDIATE ACTIONS:
□ Create project in ATLAS
□ Generate invoice in VERTEX
□ Set up fulfillment tracking
□ Contact suppliers/subs
□ Confirm delivery schedule
□ Review contract terms
□ Set up payment tracking
□ Send thank you to officer
□ Update CRM relationships
□ Add to portfolio

Suppliers: {Suppliers Contacted}
━━━━━━━━━━━━━━━━━━━━━━━━
🔗 View: [Link to record]
🚀 START CONTRACT EXECUTION
```

**Status:** [ ] COMPLETE

---

## ✅ COMPLETION CHECKLIST

| # | Automation | Status | Email Works |
|---|------------|--------|-------------|
| 1 | 🚨 Bid Deadline Alert (48h) | [ ] ON | [ ] Tested |
| 2 | ⏰ Quote Due Reminder (24h) | [ ] ON | [ ] Tested |
| 3 | ✅ Quote Received Notification | [ ] ON | [ ] Tested |
| 4 | 🆕 New Opportunity Alert | [ ] ON | [ ] Tested |
| 5 | ⚠️ Supplier Non-Response Alert | [ ] ON | [ ] Tested |
| 6 | 🎉 Winning Bid Workflow | [ ] ON | [ ] Tested |

---

## 🎯 WHAT YOU GET

✅ Never miss a deadline - 48-hour alerts  
✅ Never lose a quote - Follow-up reminders  
✅ Instant quote notifications - Know immediately  
✅ Track all new opportunities - No RFPs slip through  
✅ Supplier accountability - Non-response alerts  
✅ Win celebration & next steps - Automatic workflow  

**Result:** Professional bid tracking with zero manual monitoring

---

## 📝 NOTES

- All emails go to: `info@deedavis.biz` (change if needed)
- Test each automation before turning ON
- You can edit email templates after setup
- Turn OFF any automation if you need to pause it
- Check your spam folder for test emails

---

**🚀 START WITH #1 NOW - Takes 2 minutes!**
