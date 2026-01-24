# ALL 6 AUTOMATIONS - GRID FORMAT
**Create all 6, then test at the end**

---

## 🔴 AUTOMATION 1: BID DEADLINE ALERT (48 HOURS)

| Step | What to Click | What to Select/Type |
|------|---------------|---------------------|
| 1 | Click Automations (lightning bolt) | - |
| 2 | Click + Create automation | - |
| 3 | Click "Untitled automation" | Type: `🚨 Bid Deadline Alert - 48 Hours` |
| 4 | Click + Add trigger | Select: **When record matches conditions** |
| 5 | Table dropdown | Select: `GPSS OPPORTUNITIES` |
| 6 | Click + Add field | Select: `Deadline` |
| 7 | Operator dropdown | Select: `is within` |
| 8 | Timeframe | Type: `2` then select `days` |
| 9 | Click + Add condition | - |
| 10 | Field dropdown | Select: `Status` |
| 11 | Operator dropdown | Select: `is` |
| 12 | Value box | Type: `Awaiting Quotes` |
| 13 | Click + Add condition | - |
| 14 | Field dropdown | Select: `Status` |
| 15 | Operator dropdown | Select: `is` |
| 16 | Value box | Type: `Ready to Bid` |
| 17 | Click + Add condition | - |
| 18 | Field dropdown | Select: `Status` |
| 19 | Operator dropdown | Select: `is` |
| 20 | Value box | Type: `In Progress` |
| 21 | Close trigger (X or click outside) | - |
| 22 | Click + Add advanced logic or action | Select: **Send email** |
| 23 | To field | Type: `info@deedavis.biz` |
| 24 | From name | Type: `NEXUS Bid Alert` |
| 25 | Subject | Type: `🚨 BID DUE IN 48 HOURS: ` then + Insert field: `Name` |
| 26 | Message | Copy template below ⬇️ (use + Insert field for each field) |
| 27 | Close email (X) | - |
| 28 | Toggle switch to ON | - |

### Message Template:
```
⚠️ URGENT: BID DEADLINE APPROACHING

RFP: [Name]
RFP Number: [RFP NUMBER]
Agency: [AGENCY]
━━━━━━━━━━━━━━━━━━━━━━━━
⏰ DEADLINE: [Deadline]
   (48 hours from now)

Status: [Status]
Priority: [Priority]

Value: $[Estimated Value]
Profit: $[Est Profit]
━━━━━━━━━━━━━━━━━━━━━━━━
📋 CHECKLIST:
□ All quotes received?
□ Pricing calculated?
□ Bid forms completed?
□ Submission confirmed?

Officer: [CONTRACTING OFFICER]
Contacts: [Contacts Extracted]

⚠️ ACTION REQUIRED WITHIN 48 HOURS
```

**Status:** [ ] COMPLETE [ ] TURNED ON

---

## 🔴 AUTOMATION 2: QUOTE DUE REMINDER (24 HOURS)

| Step | What to Click | What to Select/Type |
|------|---------------|---------------------|
| 1 | Click + Create new... | - |
| 2 | Click "Untitled automation" | Type: `⏰ Quote Due Reminder - 24 Hours` |
| 3 | Click + Add trigger | Select: **When record matches conditions** |
| 4 | Table dropdown | Select: `GPSS SUBCONTRACTOR QUOTES` |
| 5 | Click + Add field | Select: `Quote Due Date` |
| 6 | Operator dropdown | Select: `is within` |
| 7 | Timeframe | Type: `1` then select `day` |
| 8 | Click + Add condition | - |
| 9 | Field dropdown | Select: `Status` |
| 10 | Operator dropdown | Select: `is` |
| 11 | Value box | Type: `Pending` |
| 12 | Close trigger (X) | - |
| 13 | Click + Add advanced logic or action | Select: **Send email** |
| 14 | To field | Type: `info@deedavis.biz` |
| 15 | From name | Type: `NEXUS Quote Alert` |
| 16 | Subject | Type: `⏰ QUOTE DUE TOMORROW: ` then + Insert: `Subcontractor` then type ` for ` then + Insert: `Opportunity` |
| 17 | Message | Copy template below ⬇️ |
| 18 | Close email (X) | - |
| 19 | Toggle switch to ON | - |

### Message Template:
```
⏰ QUOTE REMINDER: DUE IN 24 HOURS

Supplier: [Subcontractor → COMPANY NAME]
Opportunity: [Opportunity → Name]
RFP: [Opportunity → RFP NUMBER]
━━━━━━━━━━━━━━━━━━━━━━━━
⏰ QUOTE DUE: [Quote Due Date] (Tomorrow!)

CONTACT:
Email: [Subcontractor → EMAIL]
Phone: [Subcontractor → PHONE]
Service: [Subcontractor → SERVICE TYPE]
━━━━━━━━━━━━━━━━━━━━━━━━
📋 ACTION:
□ Call supplier to follow up
□ Send reminder email
□ Check if quote received
□ Update status

⚠️ FOLLOW UP TODAY
```

**Status:** [ ] COMPLETE [ ] TURNED ON

---

## 🔴 AUTOMATION 3: QUOTE RECEIVED NOTIFICATION

| Step | What to Click | What to Select/Type |
|------|---------------|---------------------|
| 1 | Click + Create new... | - |
| 2 | Click "Untitled automation" | Type: `✅ Quote Received Notification` |
| 3 | Click + Add trigger | Select: **When record matches conditions** |
| 4 | Table dropdown | Select: `GPSS SUBCONTRACTOR QUOTES` |
| 5 | Click + Add field | Select: `Status` |
| 6 | Operator dropdown | Select: `is` |
| 7 | Value box | Type: `Received` |
| 8 | Close trigger (X) | - |
| 9 | Click + Add advanced logic or action | Select: **Send email** |
| 10 | To field | Type: `info@deedavis.biz` |
| 11 | From name | Type: `NEXUS Quote Alert` |
| 12 | Subject | Type: `✅ QUOTE RECEIVED: ` then + Insert: `Subcontractor` then type ` for ` then + Insert: `Opportunity` |
| 13 | Message | Copy template below ⬇️ |
| 14 | Close email (X) | - |
| 15 | Toggle switch to ON | - |

### Message Template:
```
✅ NEW QUOTE RECEIVED

From: [Subcontractor → COMPANY NAME]
For: [Opportunity → Name]
━━━━━━━━━━━━━━━━━━━━━━━━
💰 AMOUNT: $[Quote Amount]

Contact: [Subcontractor → EMAIL]
Phone: [Subcontractor → PHONE]
━━━━━━━━━━━━━━━━━━━━━━━━
OPPORTUNITY:
RFP: [Opportunity → RFP NUMBER]
Agency: [Opportunity → AGENCY]
Deadline: [Opportunity → Deadline]
Est Value: $[Opportunity → Estimated Value]
━━━━━━━━━━━━━━━━━━━━━━━━
TIMELINE:
RFQ Sent: [RFQ Sent Date]
Due: [Quote Due Date]
Received: [CREATED DATE]
━━━━━━━━━━━━━━━━━━━━━━━━
📋 NEXT STEPS:
□ Review quote
□ Calculate markup
□ Compare quotes
□ Update opportunity
□ Prepare bid

Notes: [Notes]

✅ QUOTE IN HAND - READY TO BID
```

**Status:** [ ] COMPLETE [ ] TURNED ON

---

## 🔴 AUTOMATION 4: NEW OPPORTUNITY ALERT

| Step | What to Click | What to Select/Type |
|------|---------------|---------------------|
| 1 | Click + Create new... | - |
| 2 | Click "Untitled automation" | Type: `🆕 New Opportunity Alert` |
| 3 | Click + Add trigger | Select: **When record created** |
| 4 | Table dropdown | Select: `GPSS OPPORTUNITIES` |
| 5 | Close trigger (X) | - |
| 6 | Click + Add advanced logic or action | Select: **Send email** |
| 7 | To field | Type: `info@deedavis.biz` |
| 8 | From name | Type: `NEXUS Opportunities` |
| 9 | Subject | Type: `🆕 NEW OPPORTUNITY: ` then + Insert: `Name` |
| 10 | Message | Copy template below ⬇️ |
| 11 | Close email (X) | - |
| 12 | Toggle switch to ON | - |

### Message Template:
```
🆕 NEW RFP ADDED TO NEXUS

RFP: [Name]
Number: [RFP NUMBER]
Agency: [AGENCY]
━━━━━━━━━━━━━━━━━━━━━━━━
⏰ DEADLINE: [Deadline]

Status: [Status]
Priority: [Priority]
━━━━━━━━━━━━━━━━━━━━━━━━
💰 VALUE:
Estimated: $[Estimated Value]
Profit: $[Est Profit]
━━━━━━━━━━━━━━━━━━━━━━━━
📞 OFFICER:
[CONTRACTING OFFICER]

CONTACTS:
[Contacts Extracted]
━━━━━━━━━━━━━━━━━━━━━━━━
📋 NEXT STEPS:
□ Review RFP requirements
□ Identify suppliers
□ Send quote requests
□ Calculate pricing
□ Prepare bid

🚀 START WORKING ON THIS BID
```

**Status:** [ ] COMPLETE [ ] TURNED ON

---

## 🔴 AUTOMATION 5: SUPPLIER NON-RESPONSE ALERT

| Step | What to Click | What to Select/Type |
|------|---------------|---------------------|
| 1 | Click + Create new... | - |
| 2 | Click "Untitled automation" | Type: `⚠️ Supplier Non-Response Alert` |
| 3 | Click + Add trigger | Select: **When record matches conditions** |
| 4 | Table dropdown | Select: `GPSS SUBCONTRACTOR QUOTES` |
| 5 | Click + Add field | Select: `Quote Due Date` |
| 6 | Operator dropdown | Select: `is in the past` or `is before` |
| 7 | Click + Add condition | - |
| 8 | Field dropdown | Select: `Status` |
| 9 | Operator dropdown | Select: `is` |
| 10 | Value box | Type: `Pending` |
| 11 | Close trigger (X) | - |
| 12 | Click + Add advanced logic or action | Select: **Update record** |
| 13 | Table | Select: `GPSS SUBCONTRACTOR QUOTES` |
| 14 | Record ID | Select: **Record ID from step 1** |
| 15 | Field to update | Select: `Status` |
| 16 | New value | Type: `Overdue` |
| 17 | Close update action (X) | - |
| 18 | Click + Add advanced logic or action | Select: **Send email** |
| 19 | To field | Type: `info@deedavis.biz` |
| 20 | From name | Type: `NEXUS Alert` |
| 21 | Subject | Type: `⚠️ QUOTE OVERDUE: ` then + Insert: `Subcontractor` then type ` for ` then + Insert: `Opportunity` |
| 22 | Message | Copy template below ⬇️ |
| 23 | Close email (X) | - |
| 24 | Toggle switch to ON | - |

### Message Template:
```
⚠️ SUPPLIER NOT RESPONDING

Supplier: [Subcontractor → COMPANY NAME]
For: [Opportunity → Name]
━━━━━━━━━━━━━━━━━━━━━━━━
❌ QUOTE OVERDUE
Due: [Quote Due Date]

RFQ Sent: [RFQ Sent Date]
━━━━━━━━━━━━━━━━━━━━━━━━
CONTACT:
Email: [Subcontractor → EMAIL]
Phone: [Subcontractor → PHONE]
Service: [Subcontractor → SERVICE TYPE]
━━━━━━━━━━━━━━━━━━━━━━━━
OPPORTUNITY:
RFP: [Opportunity → RFP NUMBER]
Agency: [Opportunity → AGENCY]
Deadline: [Opportunity → Deadline]
━━━━━━━━━━━━━━━━━━━━━━━━
📋 OPTIONS:
□ Call supplier NOW
□ Send follow-up email
□ Find backup supplier
□ Update opportunity
□ Decide: Wait or move on?

Notes: [Notes]

⚠️ DECISION NEEDED
```

**Status:** [ ] COMPLETE [ ] TURNED ON

---

## 🔴 AUTOMATION 6: WINNING BID WORKFLOW

| Step | What to Click | What to Select/Type |
|------|---------------|---------------------|
| 1 | Click + Create new... | - |
| 2 | Click "Untitled automation" | Type: `🎉 Winning Bid Workflow` |
| 3 | Click + Add trigger | Select: **When record matches conditions** |
| 4 | Table dropdown | Select: `GPSS OPPORTUNITIES` |
| 5 | Click + Add field | Select: `Status` |
| 6 | Operator dropdown | Select: `is` |
| 7 | Value box | Type: `Won` |
| 8 | Close trigger (X) | - |
| 9 | Click + Add advanced logic or action | Select: **Send email** |
| 10 | To field | Type: `info@deedavis.biz` |
| 11 | From name | Type: `NEXUS Celebrations` |
| 12 | Subject | Type: `🎉 CONTRACT WON: ` then + Insert: `Name` |
| 13 | Message | Copy template below ⬇️ |
| 14 | Close email (X) | - |
| 15 | Toggle switch to ON | - |

### Message Template:
```
🎉 CONGRATULATIONS - CONTRACT AWARDED!

RFP: [Name]
Number: [RFP NUMBER]
Agency: [AGENCY]
━━━━━━━━━━━━━━━━━━━━━━━━
💰 CONTRACT:
Award: $[Estimated Value]
Profit: $[Est Profit]
━━━━━━━━━━━━━━━━━━━━━━━━
📞 OFFICER:
[CONTRACTING OFFICER]

Contacts: [Contacts Extracted]
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

Suppliers: [Suppliers Contacted]
━━━━━━━━━━━━━━━━━━━━━━━━
🚀 START CONTRACT EXECUTION
```

**Status:** [ ] COMPLETE [ ] TURNED ON

---

## ✅ FINAL CHECKLIST

| # | Automation Name | Created | Turned ON |
|---|-----------------|---------|-----------|
| 1 | 🚨 Bid Deadline Alert (48h) | [ ] | [ ] |
| 2 | ⏰ Quote Due Reminder (24h) | [ ] | [ ] |
| 3 | ✅ Quote Received Notification | [ ] | [ ] |
| 4 | 🆕 New Opportunity Alert | [ ] | [ ] |
| 5 | ⚠️ Supplier Non-Response Alert | [ ] | [ ] |
| 6 | 🎉 Winning Bid Workflow | [ ] | [ ] |

---

## 📝 NOTES

**For all [Field] references in message templates:**
- Use the **+ Insert field** button
- Select the field from the dropdown
- Don't type the field names manually

**For linked fields (with →):**
- Click + Insert field
- Select the linked table name (like "Subcontractor")
- Then select the field from that table (like "COMPANY NAME")

**After creating all 6:**
- Test each one
- Check emails arrive
- Verify formatting
- Confirm all fields populate

---

**🚀 START CREATING - ONE AFTER ANOTHER!**

Tell me when you've finished all 6 and we'll test them!
