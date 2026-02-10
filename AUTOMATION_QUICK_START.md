# ⚡ AUTOMATION QUICK START - 30 MINUTES TO FULLY AUTOMATED
**Start Here:** Set up critical automations first  
**Time:** 30 minutes  
**Result:** Never miss deadlines + auto-contract tracking

---

## 🎯 CRITICAL AUTOMATIONS (DO THESE FIRST)

### **1. DEADLINE ALERT - 1 DAY (10 min)**

**Go to:** Airtable → NEXUS base → Click "Automations" → "+ Create automation"

**Name:** `Deadline Alert - 1 Day`

**Trigger:**
- When record matches conditions
- Table: GPSS OPPORTUNITIES
- Conditions:
  - Days Until Due ≤ 1
  - STATUS does not contain "Won"
  - STATUS does not contain "Submitted"

**Action:**
- Send email
- To: `bids.deedavisinc@gmail.com`
- Subject: `🚨🚨🚨 CRITICAL: {Name} Due TOMORROW!`
- Body:
```
DEADLINE ALERT - LAST CHANCE

Opportunity: {Name}
Due Date: {Deadline}
Days Left: {Days Until Due}
Value: {VALUE}
Agency: {AGENCY NAME}

THIS IS YOUR LAST DAY TO SUBMIT!

Link: {Record URL}
```

**Turn on** ✅

---

### **2. DEADLINE ALERT - 3 DAYS (10 min)**

**Name:** `Deadline Alert - 3 Days`

**Same setup as #1 but:**
- Conditions: Days Until Due ≤ 3
- Subject: `🚨 URGENT: {Name} Due in {Days Until Due} Days!`
- Body: Remove "LAST CHANCE" text

**Turn on** ✅

---

### **3. WON BID → CREATE CONTRACT (10 min)**

**Name:** `Won Bid Creates Contract`

**Trigger:**
- When record matches conditions
- Table: GPSS OPPORTUNITIES
- Conditions:
  - STATUS contains "Won"

**Action #1 - Create record:**
- Table: CONTRACTS
- Map fields:
  - Contract Name → {Name}
  - Opportunity → {Record ID}
  - Client/Agency → {AGENCY NAME}
  - Contract Value → {VALUE}
  - Status → "Active"
  - RFP Number → {RFP NUMBER}

**Action #2 - Update opportunity:**
- Update record in GPSS OPPORTUNITIES
- Notes → Append "✅ Contract created"

**Turn on** ✅

---

## ✅ DONE! (30 minutes)

**You now have:**
- ✅ 1-day deadline warnings
- ✅ 3-day deadline warnings
- ✅ Automatic contract creation when you win

**Result:** You'll never miss a deadline and won bids automatically become contracts!

---

## 🚀 WANT MORE? (Add these next - 60 min total)

Open full guide: `AIRTABLE_AUTOMATIONS_COMPLETE_SETUP.md`

**Important (20 min):**
4. Deadline Alert - 7 Days (advance planning)
5. Document Package Ready notification
6. New Supplier RFP notification
7. AI Recommendation approved workflow

**Helpful (20 min):**
8. High Priority opportunity alerts
9. Auto-archive expired opportunities

**Advanced (20 min):**
10. Contract → Invoice (VERTEX)
11. Supplier Quote → Opportunity update
12. Officer Outreach tracking

---

## 💡 TESTING YOUR AUTOMATIONS

### **Test Deadline Alerts:**
1. Create test opportunity
2. Set deadline to tomorrow
3. Set Days Until Due = 1
4. Check your email in 1-2 minutes
5. Delete test record

### **Test Won Bid → Contract:**
1. Create test opportunity
2. Set STATUS to contain "Won"
3. Check CONTRACTS table for new record
4. Delete test records

---

## 🎯 QUICK REFERENCE

**To access automations:**
Airtable → NEXUS base → "Automations" button (top right)

**To test automation:**
Open automation → Click "Test" button → Use sample record

**To check if working:**
Automations → Click automation name → View "Runs" tab

**To turn off:**
Open automation → Toggle switch to OFF

---

## ✅ CHECKLIST

**Critical (30 min):**
- [ ] Deadline Alert - 1 Day
- [ ] Deadline Alert - 3 Days
- [ ] Won Bid → Create Contract
- [ ] Test all three

**Important (20 min):**
- [ ] Deadline Alert - 7 Days
- [ ] Document Package Ready
- [ ] New Supplier RFP
- [ ] AI Recommendation Approved

**Helpful (20 min):**
- [ ] High Priority Alert
- [ ] Auto-Archive Expired

**Advanced (20 min):**
- [ ] Contract → Invoice
- [ ] Quote → Opportunity
- [ ] Officer Outreach

---

**START NOW: Open Airtable → Automations → Create first automation** ⚡

*30 minutes = Never miss another deadline!*
