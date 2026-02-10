# 🤖 AIRTABLE AUTOMATIONS - COMPLETE NEXUS INTEGRATION
**Goal:** Fully automated workflows - no manual steps  
**Time:** 60-90 minutes to set up all automations  
**Result:** NEXUS runs itself

---

## 📋 TABLE OF CONTENTS

1. **Won Bid → Create Contract** (Critical)
2. **Deadline Alerts** (Critical)
3. **Document Package Complete → Ready to Submit** (Important)
4. **New RFP Created → Notification** (Important)
5. **AI Recommendation Approved → Update Opportunity** (Important)
6. **High Priority Opportunity → Slack/Email Alert** (Helpful)
7. **Opportunity Deadline Passed → Archive** (Helpful)
8. **Contract Won → Create Invoice in VERTEX** (Financial)
9. **Supplier Quote Received → Update Opportunity** (Workflow)
10. **Officer Outreach Sent → Update Status** (Tracking)

---

## 🎯 AUTOMATION #1: WON BID → CREATE CONTRACT
**Priority:** 🔴 CRITICAL  
**Impact:** Automatic contract tracking when you win bids

### **SETUP:**

1. **Go to Airtable → Your NEXUS base → Click "Automations" (top right)**

2. **Click "+ Create automation"**

3. **Name it:** `Won Bid Creates Contract`

4. **TRIGGER:**
   - Type: **"When record matches conditions"**
   - Table: **GPSS OPPORTUNITIES**
   - Conditions:
     - When **STATUS** contains **"Won"** (or however you mark won bids)
     - Or **Pipeline Stage** = **"Won"**

5. **ACTION #1: Create Record**
   - In table: **CONTRACTS**
   - Map fields:
     - Contract Name → {Name} (from OPPORTUNITIES)
     - Opportunity → {Record ID} (link back)
     - Client/Agency → {AGENCY NAME}
     - Contract Value → {VALUE}
     - Start Date → {Today} (use formula)
     - Status → "Active"
     - RFP Number → {RFP NUMBER}
     - Contracting Officer → {CONTRACTING OFFICER}

6. **ACTION #2: Update Original Opportunity** (Optional)
   - Update record in **GPSS OPPORTUNITIES**
   - Set field: **Notes** → Append "✅ Contract created in CONTRACTS table"

7. **Click "Turn on automation"**

---

## 🎯 AUTOMATION #2: DEADLINE ALERTS (3-DAY WARNING)
**Priority:** 🔴 CRITICAL  
**Impact:** Never miss a deadline

### **SETUP:**

1. **Create automation:** `Deadline Alert - 3 Days`

2. **TRIGGER:**
   - Type: **"When record matches conditions"**
   - Table: **GPSS OPPORTUNITIES**
   - Conditions:
     - **Days Until Due** is less than or equal to **3**
     - AND **STATUS** does not contain **"Won"**
     - AND **STATUS** does not contain **"Submitted"**
     - AND **STATUS** does not contain **"Passed"**

3. **ACTION: Send email**
   - To: `bids.deedavisinc@gmail.com`
   - Subject: `🚨 URGENT: {Name} Due in {Days Until Due} Days!`
   - Body:
     ```
     DEADLINE ALERT
     
     Opportunity: {Name}
     Due Date: {Deadline}
     Days Left: {Days Until Due}
     Value: {VALUE}
     Agency: {AGENCY NAME}
     
     Status: {STATUS}
     Priority: {Priority}
     
     Action Required: Complete and submit bid!
     
     Link: {Record URL}
     ```

4. **Turn on automation**

### **BONUS: Create 3 versions:**
- 7-day warning (advance planning)
- 3-day warning (urgent)
- 1-day warning (CRITICAL)

---

## 🎯 AUTOMATION #3: DEADLINE ALERT (1-DAY WARNING)
**Priority:** 🔴 CRITICAL  
**Impact:** Last chance alert

### **SETUP:**

Same as #2 but:
- **Conditions:** Days Until Due = **1**
- **Subject:** `🚨🚨🚨 CRITICAL: {Name} Due TOMORROW!`
- **Add to body:** "THIS IS YOUR LAST DAY TO SUBMIT!"

---

## 🎯 AUTOMATION #4: DOCUMENT PACKAGE READY → UPDATE STATUS
**Priority:** 🟡 IMPORTANT  
**Impact:** Visual confirmation package is ready

### **SETUP:**

1. **Create automation:** `Document Package Ready`

2. **TRIGGER:**
   - Type: **"When record matches conditions"**
   - Table: **GPSS OPPORTUNITIES**
   - Conditions:
     - **PACKAGE STATUS** = **"Attached"**

3. **ACTION: Update record**
   - In same table (GPSS OPPORTUNITIES)
   - Update fields:
     - **STATUS** → Add value **"Documents Ready"**
     - **Notes** → Append "✅ Bid package assembled and attached"

4. **Turn on automation**

---

## 🎯 AUTOMATION #5: NEW SUPPLIER RFP CREATED → NOTIFICATION
**Priority:** 🟡 IMPORTANT  
**Impact:** Track when RFPs sent to suppliers

### **SETUP:**

1. **Create automation:** `New Supplier RFP Notification`

2. **TRIGGER:**
   - Type: **"When record created"**
   - Table: **SUPPLIER RFPS**

3. **ACTION: Send email**
   - To: `bids.deedavisinc@gmail.com`
   - Subject: `📧 Supplier RFP Sent: {PROJECT NAME}`
   - Body:
     ```
     New Supplier RFP Created
     
     RFP Number: {DDI RFP NUMBER}
     Project: {PROJECT NAME}
     Category: {CATEGORY}
     Location: {SANITIZED LOCATION}
     
     Quote Due: {QUOTE DUE DATE}
     Contract Value: ${CONTRACT VALUE MIN} - ${CONTRACT VALUE MAX}
     
     Status: {STATUS}
     
     PDF Path: {PDF GENERATED PATH}
     ```

4. **Turn on automation**

---

## 🎯 AUTOMATION #6: AI RECOMMENDATION APPROVED → UPDATE OPPORTUNITY
**Priority:** 🟡 IMPORTANT  
**Impact:** Close the loop on AI recommendations

### **SETUP:**

1. **Create automation:** `AI Recommendation Approved`

2. **TRIGGER:**
   - Type: **"When record matches conditions"**
   - Table: **AI RECOMMENDATIONS**
   - Conditions:
     - **STATUS** = **"APPROVED"**

3. **ACTION #1: Find linked opportunity record**
   - Use **OPPORTUNITY** field (linked record)

4. **ACTION #2: Update opportunity**
   - In table: **GPSS OPPORTUNITIES**
   - Update fields:
     - **AI RECOMMENDATION** → Copy from {RECOMMENDATION} field
     - **Notes** → Append "✅ AI recommendation approved"
     - **STATUS** → Add "AI Approved"

5. **Turn on automation**

---

## 🎯 AUTOMATION #7: HIGH PRIORITY OPPORTUNITY → INSTANT ALERT
**Priority:** 🟢 HELPFUL  
**Impact:** Immediate notification for hot opportunities

### **SETUP:**

1. **Create automation:** `High Priority Alert`

2. **TRIGGER:**
   - Type: **"When record matches conditions"**
   - Table: **GPSS OPPORTUNITIES**
   - Conditions:
     - **PRIORITY SCORE** is greater than **80**
     - OR **Priority** = **"High"**
     - OR **HIGH VALUE FLAG** is checked

3. **ACTION: Send email**
   - To: `bids.deedavisinc@gmail.com`
   - Subject: `🔥 HIGH PRIORITY: {Name} - ${VALUE}`
   - Body:
     ```
     HIGH PRIORITY OPPORTUNITY DETECTED
     
     Name: {Name}
     Value: {VALUE}
     Priority Score: {PRIORITY SCORE}
     
     Agency: {AGENCY NAME}
     Deadline: {Deadline}
     Days Left: {Days Until Due}
     
     Set-Aside: {Set-Aside Type}
     Location: {Performance Location}
     
     WHY IT'S HOT:
     - High value: ${VALUE}
     - Priority Score: {PRIORITY SCORE}
     - Strategic fit for EDWOSB
     
     REVIEW IMMEDIATELY!
     Link: {Record URL}
     ```

4. **Turn on automation**

---

## 🎯 AUTOMATION #8: DEADLINE PASSED → AUTO-ARCHIVE
**Priority:** 🟢 HELPFUL  
**Impact:** Clean up expired opportunities

### **SETUP:**

1. **Create automation:** `Archive Expired Opportunities`

2. **TRIGGER:**
   - Type: **"When record matches conditions"**
   - Table: **GPSS OPPORTUNITIES**
   - Conditions:
     - **Days Until Due** is less than **0**
     - AND **STATUS** does not contain **"Won"**
     - AND **STATUS** does not contain **"Submitted"**

3. **ACTION: Update record**
   - Update fields:
     - **STATUS** → Add **"Expired"**
     - **Pipeline Stage** → **"Lost/Expired"**
     - **Notes** → Append "❌ Deadline passed - archived automatically"

4. **Turn on automation**

---

## 🎯 AUTOMATION #9: CONTRACT WON → CREATE VERTEX INVOICE
**Priority:** 💰 FINANCIAL  
**Impact:** Automatic invoice creation for accounting

### **SETUP:**

1. **Create automation:** `Won Contract Creates Invoice`

2. **TRIGGER:**
   - Type: **"When record created"**
   - Table: **CONTRACTS**
   - OR **"When record matches conditions"**
     - **Status** = **"Active"**

3. **ACTION: Create record**
   - In table: **VERTEX INVOICES**
   - Map fields:
     - Invoice Number → Formula: `INV-{Record ID}`
     - Client → {Client/Agency}
     - Amount → {Contract Value}
     - Date → {Start Date}
     - Status → "Pending"
     - Contract → {Record ID} (link back)
     - Description → "Contract: {Contract Name}"

4. **Turn on automation**

---

## 🎯 AUTOMATION #10: SUPPLIER QUOTE RECEIVED → UPDATE OPPORTUNITY
**Priority:** 🔵 WORKFLOW  
**Impact:** Track quote progress

### **SETUP:**

1. **Create automation:** `Supplier Quote Updates Opportunity`

2. **TRIGGER:**
   - Type: **"When record created"**
   - Table: **GPSS SUPPLIER QUOTES**

3. **ACTION: Find linked opportunity**
   - Use linked field to GPSS OPPORTUNITIES

4. **ACTION: Update opportunity**
   - Update fields:
     - **Notes** → Append "📝 Supplier quote received from {Supplier Name}"
     - **STATUS** → Add "Quotes In Progress"

5. **Turn on automation**

---

## 🎯 AUTOMATION #11: OFFICER OUTREACH SENT → UPDATE TRACKING
**Priority:** 🔵 TRACKING  
**Impact:** Track procurement officer relationships

### **SETUP:**

1. **Create automation:** `Officer Outreach Tracking`

2. **TRIGGER:**
   - Type: **"When record matches conditions"**
   - Table: **OFFICER OUTREACH TRACKING**
   - Conditions:
     - **Status** = **"Sent"**

3. **ACTION: Update linked opportunity**
   - Find linked GPSS OPPORTUNITIES record
   - Update fields:
     - **OFFICER OUTREACH SENT** → Check ✅
     - **OFFICER OUTREACH DATE** → {Date Sent}
     - **Notes** → Append "📧 Officer outreach sent"

4. **Turn on automation**

---

## 🎯 AUTOMATION #12: 7-DAY ADVANCE DEADLINE WARNING
**Priority:** 🔴 CRITICAL  
**Impact:** Plan ahead for upcoming deadlines

### **SETUP:**

Same as Automation #2 but:
- **Conditions:** Days Until Due = **7**
- **Subject:** `📅 Planning Alert: {Name} Due in 1 Week`
- **Body emphasis:** "Start gathering quotes and preparing bid"

---

## 📊 AUTOMATION PRIORITY SUMMARY

### **CRITICAL (Set up first - 30 min):**
1. ✅ Deadline Alert - 3 Days
2. ✅ Deadline Alert - 1 Day
3. ✅ Won Bid → Create Contract

### **IMPORTANT (Set up next - 20 min):**
4. ✅ Document Package Ready
5. ✅ New Supplier RFP Notification
6. ✅ AI Recommendation Approved
7. ✅ Deadline Alert - 7 Days (advance planning)

### **HELPFUL (Set up when time - 20 min):**
8. ✅ High Priority Alert
9. ✅ Deadline Passed → Archive

### **ADVANCED (Set up later - 20 min):**
10. ✅ Contract → Invoice (VERTEX integration)
11. ✅ Supplier Quote → Update Opportunity
12. ✅ Officer Outreach Tracking

---

## 🚀 QUICK START GUIDE

### **STEP 1: Access Automations**
1. Open Airtable → NEXUS base
2. Click **"Automations"** button (top toolbar)
3. Click **"+ Create automation"**

### **STEP 2: Set Up Critical Automations First**
Start with deadline alerts:
1. Create 1-day warning
2. Create 3-day warning
3. Create 7-day warning
4. Create Won Bid → Contract

**Time:** 30 minutes  
**Impact:** Never miss deadlines + auto-contract tracking

### **STEP 3: Test Each Automation**
- Use "Test" button in automation editor
- Create test records to verify triggers work
- Check emails arrive correctly

### **STEP 4: Monitor & Refine**
- Check automation run history
- Adjust conditions if too many/few triggers
- Fine-tune email formatting

---

## 💡 TIPS & BEST PRACTICES

### **Email Overload Prevention:**
- Don't create multiple alerts for same deadline
- Use clear subject prefixes (🚨, 📅, ✅)
- Consider digest emails (daily summary)

### **Testing:**
- Always test before turning on
- Use test records, not real opportunities
- Check automation history after enabling

### **Performance:**
- Avoid complex nested automations
- Keep conditions simple
- Use direct field references

### **Maintenance:**
- Review automation runs weekly
- Disable broken automations
- Update conditions as workflow changes

---

## 🎯 AUTOMATION CHECKLIST

**Critical Automations:**
- [ ] Deadline Alert - 1 Day
- [ ] Deadline Alert - 3 Days
- [ ] Deadline Alert - 7 Days
- [ ] Won Bid → Create Contract

**Important Automations:**
- [ ] Document Package Ready
- [ ] New Supplier RFP Notification
- [ ] AI Recommendation Approved

**Helpful Automations:**
- [ ] High Priority Alert
- [ ] Deadline Passed → Archive

**Advanced Automations:**
- [ ] Contract → Invoice (VERTEX)
- [ ] Supplier Quote → Opportunity
- [ ] Officer Outreach Tracking

---

## 🆘 TROUBLESHOOTING

### **Automation not triggering:**
- Check conditions are correct
- Verify field names match exactly
- Test with simple example first

### **Email not received:**
- Check spam folder
- Verify email address correct
- Test email action with simple message

### **Wrong data in automation:**
- Check field mapping
- Use "Record" vs "Field" correctly
- Preview before turning on

---

## 📧 EMAIL TEMPLATE BEST PRACTICES

**Good Subject Lines:**
```
✅ GOOD: 🚨 URGENT: Canton Water Bid Due in 1 Day!
❌ BAD: Notification

✅ GOOD: 📅 Planning: 7 Bids Due Next Week
❌ BAD: Weekly Update
```

**Good Email Bodies:**
- Lead with action required
- Include key details (deadline, value, agency)
- Provide direct link to record
- Use clear formatting

---

## 🎉 WHAT YOU'LL ACHIEVE

**After setting up all automations:**

✅ **Never miss a deadline** (triple alerts: 7-day, 3-day, 1-day)  
✅ **Automatic contract tracking** (won bids → contracts)  
✅ **Financial integration** (contracts → invoices)  
✅ **Document workflow** (package ready → status update)  
✅ **Supplier RFP tracking** (sent → notification)  
✅ **AI recommendation loop** (approved → opportunity update)  
✅ **High priority alerts** (hot opportunities → instant email)  
✅ **Auto-archiving** (expired → cleaned up)  
✅ **Officer relationship tracking** (outreach → logged)  
✅ **Quote progress tracking** (supplier quotes → opportunity update)

**Result:** NEXUS runs itself, you just respond to alerts! 🚀

---

## ⚡ READY TO START?

**Quick Setup (30 min) - Do Critical automations:**
1. Deadline alerts (1-day, 3-day, 7-day)
2. Won Bid → Create Contract
3. Test everything

**Full Setup (90 min) - Do all 12 automations:**
1. Critical (30 min)
2. Important (20 min)
3. Helpful (20 min)
4. Advanced (20 min)

**Choose your path and let's start building!** 🎯

---

*Automation guide created: February 1, 2026*  
*Total automations: 12*  
*Setup time: 30-90 minutes*  
*Impact: Fully automated NEXUS*
