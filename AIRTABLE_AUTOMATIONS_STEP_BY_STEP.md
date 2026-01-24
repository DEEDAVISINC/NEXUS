# AIRTABLE AUTOMATIONS - STEP BY STEP SETUP
**Start Here: Critical Bid Tracking Automations**

---

## 🎯 PRIORITY ORDER

We'll set these up **one by one, in this order:**

### **🔴 PHASE 1: CRITICAL BID TRACKING (Do First - 6 automations)**
1. ✅ Bid Deadline Alert (48 hours before)
2. ✅ Quote Due Reminder (24 hours before)
3. ✅ Quote Received Notification
4. ✅ New Opportunity Alert
5. ✅ Supplier Non-Response Alert
6. ✅ Winning Bid Workflow

### **🟡 PHASE 2: IMPORTANT EFFICIENCY (Do Next - 5 automations)**
7. ⏳ AI Recommendation Alert
8. ⏳ Officer Outreach Follow-up
9. ⏳ Invoice Generation on Win
10. ⏳ Capability Statement Auto-attach
11. ⏳ Competitive Intel Tracking

### **🟢 PHASE 3: NICE TO HAVE (Do Later - 4 automations)**
12. ⏳ Supplier Performance Scoring
13. ⏳ Monthly Win Rate Report
14. ⏳ Quarterly Revenue Forecast
15. ⏳ Contract Renewal Reminders

---

# 🔴 AUTOMATION 1: BID DEADLINE ALERT (48 HOURS)

**Why:** Never miss a bid deadline  
**When:** 48 hours before deadline  
**Table:** GPSS OPPORTUNITIES

## Step-by-Step Setup:

### **1. Open Airtable Automations**
- Go to your NEXUS Airtable base
- Click **Automations** (lightning bolt icon in top right)
- Click **Create automation**

### **2. Name the Automation**
- Name: `🚨 Bid Deadline Alert - 48 Hours`

### **3. Configure Trigger**
- Trigger Type: **When record matches conditions**
- Table: `GPSS OPPORTUNITIES`
- Conditions:
  - When `Deadline` is within `the next 2 days`
  - AND `Status` is one of: `Awaiting Quotes`, `Ready to Bid`, `In Progress`
  - AND `Priority` is not `cancelled`

### **4. Add Action: Send Email**
- Action Type: **Send email**
- To: `info@deedavis.biz` (or your email)
- Subject: `🚨 BID DUE IN 48 HOURS: {Name}`
- Body:
```
⚠️ URGENT: BID DEADLINE APPROACHING

RFP: {Name}
RFP Number: {RFP NUMBER}
Agency: {AGENCY}
━━━━━━━━━━━━━━━━━━━━━━━━
⏰ DEADLINE: {Deadline}
   (48 hours from now)

Current Status: {Status}
Priority: {Priority}

Estimated Value: ${Estimated Value}
Est Profit: ${Est Profit}
━━━━━━━━━━━━━━━━━━━━━━━━

📋 CHECKLIST:
□ All quotes received?
□ Pricing calculated?
□ Bid forms completed?
□ Submission method confirmed?

Contracting Officer:
{CONTRACTING OFFICER}

Contacts:
{Contacts Extracted}

Suppliers Contacted:
{Suppliers Contacted}

Quotes Status:
{Quotes Status}
━━━━━━━━━━━━━━━━━━━━━━━━

🔗 View in Airtable:
[Link to record]

⚠️ ACTION REQUIRED WITHIN 48 HOURS
```

### **5. Test the Automation**
- Click **Test automation**
- Check if email arrives correctly

### **6. Turn ON**
- Toggle automation to **ON**
- Click **Done**

---

## ✅ VERIFICATION

After setup, verify:
- [ ] Automation appears in list as **ON**
- [ ] Test email received
- [ ] Email formatting looks good
- [ ] All fields populate correctly

**Status:** [ ] COMPLETE

---

# 🔴 AUTOMATION 2: QUOTE DUE REMINDER (24 HOURS)

**Why:** Follow up with suppliers before quotes are due  
**When:** 24 hours before quote deadline  
**Table:** GPSS SUBCONTRACTOR QUOTES

## Step-by-Step Setup:

### **1. Create New Automation**
- Click **Create automation**
- Name: `⏰ Quote Due Reminder - 24 Hours`

### **2. Configure Trigger**
- Trigger Type: **When record matches conditions**
- Table: `GPSS SUBCONTRACTOR QUOTES`
- Conditions:
  - When `Quote Due Date` is within `the next 1 day`
  - AND `Status` is `Pending`

### **3. Add Action: Send Email**
- Action Type: **Send email**
- To: `info@deedavis.biz`
- Subject: `⏰ QUOTE DUE TOMORROW: {Subcontractor} for {Opportunity}`
- Body:
```
⏰ QUOTE REMINDER: DUE IN 24 HOURS

Supplier: {Subcontractor → COMPANY NAME}
Opportunity: {Opportunity → Name}
RFP Number: {Opportunity → RFP NUMBER}
━━━━━━━━━━━━━━━━━━━━━━━━
⏰ QUOTE DUE: {Quote Due Date}
   (Tomorrow!)

RFQ Sent: {RFQ Sent Date}
━━━━━━━━━━━━━━━━━━━━━━━━

SUPPLIER CONTACT:
Company: {Subcontractor → COMPANY NAME}
Email: {Subcontractor → EMAIL}
Phone: {Subcontractor → PHONE}
Service: {Subcontractor → SERVICE TYPE}
━━━━━━━━━━━━━━━━━━━━━━━━

OPPORTUNITY DETAILS:
Agency: {Opportunity → AGENCY}
Deadline: {Opportunity → Deadline}
Est Value: ${Opportunity → Estimated Value}
━━━━━━━━━━━━━━━━━━━━━━━━

📋 ACTION ITEMS:
□ Call supplier to follow up
□ Send reminder email if needed
□ Check if quote received yet
□ Update status when received

🔗 View Quote in Airtable:
[Link to record]

⚠️ FOLLOW UP TODAY
```

### **4. Test & Turn ON**
- Test automation
- Verify email
- Turn ON

**Status:** [ ] COMPLETE

---

# 🔴 AUTOMATION 3: QUOTE RECEIVED NOTIFICATION

**Why:** Immediately know when a quote comes in  
**When:** Quote status changes to "Received"  
**Table:** GPSS SUBCONTRACTOR QUOTES

## Step-by-Step Setup:

### **1. Create New Automation**
- Name: `✅ Quote Received Notification`

### **2. Configure Trigger**
- Trigger Type: **When record matches conditions**
- Table: `GPSS SUBCONTRACTOR QUOTES`
- Conditions:
  - When `Status` becomes `Received`

### **3. Add Action: Send Email**
- To: `info@deedavis.biz`
- Subject: `✅ QUOTE RECEIVED: {Subcontractor} for {Opportunity}`
- Body:
```
✅ NEW QUOTE RECEIVED

From: {Subcontractor → COMPANY NAME}
For: {Opportunity → Name}
━━━━━━━━━━━━━━━━━━━━━━━━

💰 QUOTE AMOUNT: ${Quote Amount}

Service: {Subcontractor → SERVICE TYPE}
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
Quote Due: {Quote Due Date}
Quote Received: {CREATED DATE}

Response Time: [Calculate days]
━━━━━━━━━━━━━━━━━━━━━━━━

📋 NEXT STEPS:
□ Review quote details
□ Calculate markup
□ Compare with other quotes
□ Update opportunity status
□ Prepare bid submission

Notes:
{Notes}

🔗 View in Airtable:
[Link to record]

✅ QUOTE IN HAND - READY TO BID
```

### **4. Test & Turn ON**

**Status:** [ ] COMPLETE

---

# 🔴 AUTOMATION 4: NEW OPPORTUNITY ALERT

**Why:** Know immediately when a new RFP is added  
**When:** New record created in GPSS OPPORTUNITIES  
**Table:** GPSS OPPORTUNITIES

## Step-by-Step Setup:

### **1. Create New Automation**
- Name: `🆕 New Opportunity Alert`

### **2. Configure Trigger**
- Trigger Type: **When record created**
- Table: `GPSS OPPORTUNITIES`

### **3. Add Action: Send Email**
- To: `info@deedavis.biz`
- Subject: `🆕 NEW OPPORTUNITY: {Name}`
- Body:
```
🆕 NEW RFP ADDED TO NEXUS

RFP: {Name}
RFP Number: {RFP NUMBER}
Agency: {AGENCY}
━━━━━━━━━━━━━━━━━━━━━━━━

⏰ DEADLINE: {Deadline}
Days Until Due: {Days Until Due}

Status: {Status}
Priority: {Priority}
━━━━━━━━━━━━━━━━━━━━━━━━

💰 OPPORTUNITY VALUE:
Estimated Value: ${Estimated Value}
Est Profit: ${Est Profit}
━━━━━━━━━━━━━━━━━━━━━━━━

📞 CONTRACTING OFFICER:
{CONTRACTING OFFICER}

CONTACTS:
{Contacts Extracted}
━━━━━━━━━━━━━━━━━━━━━━━━

📋 NEXT STEPS:
□ Review RFP requirements
□ Identify suppliers/subcontractors
□ Send quote requests
□ Calculate pricing
□ Prepare bid submission

🔗 View in Airtable:
[Link to record]

🚀 START WORKING ON THIS BID
```

### **4. Test & Turn ON**

**Status:** [ ] COMPLETE

---

# 🔴 AUTOMATION 5: SUPPLIER NON-RESPONSE ALERT

**Why:** Follow up on suppliers who haven't responded  
**When:** Quote is overdue (3 days past due date)  
**Table:** GPSS SUBCONTRACTOR QUOTES

## Step-by-Step Setup:

### **1. Create New Automation**
- Name: `⚠️ Supplier Non-Response Alert`

### **2. Configure Trigger**
- Trigger Type: **When record matches conditions**
- Table: `GPSS SUBCONTRACTOR QUOTES`
- Conditions:
  - When `Quote Due Date` is `in the past`
  - AND `Status` is still `Pending`

### **3. Add Action: Update Record**
- Table: `GPSS SUBCONTRACTOR QUOTES`
- Record: Trigger record
- Fields:
  - `Status` → `Overdue`

### **4. Add Action 2: Send Email**
- To: `info@deedavis.biz`
- Subject: `⚠️ QUOTE OVERDUE: {Subcontractor} for {Opportunity}`
- Body:
```
⚠️ SUPPLIER NOT RESPONDING

Supplier: {Subcontractor → COMPANY NAME}
For: {Opportunity → Name}
━━━━━━━━━━━━━━━━━━━━━━━━

❌ QUOTE OVERDUE
Due Date: {Quote Due Date}
Days Overdue: [Calculate]

RFQ Sent: {RFQ Sent Date}
━━━━━━━━━━━━━━━━━━━━━━━━

SUPPLIER CONTACT:
Email: {Subcontractor → EMAIL}
Phone: {Subcontractor → PHONE}
Service: {Subcontractor → SERVICE TYPE}
━━━━━━━━━━━━━━━━━━━━━━━━

OPPORTUNITY:
RFP: {Opportunity → RFP NUMBER}
Agency: {Opportunity → AGENCY}
Deadline: {Opportunity → Deadline}
━━━━━━━━━━━━━━━━━━━━━━━━

📋 ACTION OPTIONS:
□ Call supplier immediately
□ Send follow-up email
□ Find backup supplier
□ Update opportunity status
□ Decide: Wait or move on?

Notes:
{Notes}

🔗 View in Airtable:
[Link to record]

⚠️ DECISION NEEDED
```

### **5. Test & Turn ON**

**Status:** [ ] COMPLETE

---

# 🔴 AUTOMATION 6: WINNING BID WORKFLOW

**Why:** Automate next steps when you win a contract  
**When:** Opportunity status changes to "Won"  
**Table:** GPSS OPPORTUNITIES

## Step-by-Step Setup:

### **1. Create New Automation**
- Name: `🎉 Winning Bid Workflow`

### **2. Configure Trigger**
- Trigger Type: **When record matches conditions**
- Table: `GPSS OPPORTUNITIES`
- Conditions:
  - When `Status` becomes `Won`

### **3. Add Action: Send Email**
- To: `info@deedavis.biz`
- Subject: `🎉 CONTRACT WON: {Name}`
- Body:
```
🎉 CONGRATULATIONS - CONTRACT AWARDED!

RFP: {Name}
RFP Number: {RFP NUMBER}
Agency: {AGENCY}
━━━━━━━━━━━━━━━━━━━━━━━━

💰 CONTRACT VALUE:
Award Amount: ${Estimated Value}
Estimated Profit: ${Est Profit}
━━━━━━━━━━━━━━━━━━━━━━━━

📞 CONTRACTING OFFICER:
{CONTRACTING OFFICER}

Contacts:
{Contacts Extracted}
━━━━━━━━━━━━━━━━━━━━━━━━

📋 IMMEDIATE NEXT STEPS:
□ Create project in ATLAS
□ Generate invoice in VERTEX
□ Set up fulfillment tracking
□ Contact suppliers/subcontractors
□ Confirm delivery schedule
□ Review contract terms
□ Set up payment tracking

□ Send thank you to contracting officer
□ Update relationships in CRM
□ Add to portfolio/case studies
━━━━━━━━━━━━━━━━━━━━━━━━

SUPPLIERS/SUBCONTRACTORS USED:
{Suppliers Contacted}

Winning Quotes:
[Link to GPSS SUBCONTRACTOR QUOTES]
━━━━━━━━━━━━━━━━━━━━━━━━

🔗 View in Airtable:
[Link to record]

🚀 START CONTRACT EXECUTION
```

### **4. Add Action 2: Create Project (Optional)**
If you have ATLAS Projects table:
- Action Type: **Create record**
- Table: `ATLAS Projects`
- Fields:
  - `Project Name` → {Name}
  - `Client` → {AGENCY}
  - `Contract Value` → {Estimated Value}
  - `Status` → `Active`
  - Link to opportunity

### **5. Test & Turn ON**

**Status:** [ ] COMPLETE

---

## ✅ PHASE 1 COMPLETION CHECKLIST

After setting up all 6 critical automations, verify:

- [ ] **Automation 1:** Bid Deadline Alert (48 hours) - ON
- [ ] **Automation 2:** Quote Due Reminder (24 hours) - ON
- [ ] **Automation 3:** Quote Received Notification - ON
- [ ] **Automation 4:** New Opportunity Alert - ON
- [ ] **Automation 5:** Supplier Non-Response Alert - ON
- [ ] **Automation 6:** Winning Bid Workflow - ON

### **Test Each One:**
- [ ] Received test emails from all 6
- [ ] Email formatting looks good
- [ ] All fields populate correctly
- [ ] Links work

### **Go Live:**
- [ ] All automations toggled to ON
- [ ] Email notifications working
- [ ] Ready for real RFPs

---

## 📊 WHAT YOU GET FROM PHASE 1

✅ **Never miss a deadline** - 48-hour alerts  
✅ **Never lose a quote** - Follow-up reminders  
✅ **Instant quote notifications** - Know immediately  
✅ **Track all new opportunities** - No RFPs slip through  
✅ **Supplier accountability** - Non-response alerts  
✅ **Win celebration & next steps** - Automatic workflow  

**Result:** Professional bid tracking with zero manual monitoring

---

## 🎯 READY TO START?

**Let's do Automation #1 together right now:**

1. Open your Airtable base
2. Click Automations (lightning bolt)
3. Click Create automation
4. Follow the steps above for "Bid Deadline Alert"

**Tell me when you're ready and I'll walk you through each one!**

---

**After Phase 1 is complete, we'll move to Phase 2 (AI Recommendations, Officer Outreach, etc.)**
