# DAY 1: START HERE

**Date:** February 1, 2026  
**Goal:** Audit NEXUS and identify critical bugs  
**Time:** 8 hours

---

## 🎯 YOUR MISSION TODAY

**Find and list everything that's broken.**

Don't fix anything yet - just TEST and DOCUMENT what needs fixing.

---

## ⏰ SCHEDULE

### **9:00 AM - Start Backend**

```bash
cd "/Users/deedavis/NEXUS BACKEND"
python3 api_server.py
```

**Check:** Does it start without errors?

If NO → Write down error in bug tracker

---

### **9:05 AM - Start Frontend**

Open new terminal:

```bash
cd "/Users/deedavis/NEXUS BACKEND/nexus-frontend"
npm start
```

**Check:** Does browser open at http://localhost:3000?

If NO → Write down error in bug tracker

---

### **9:10 AM - Start Document APIs**

Open new terminals for each:

```bash
# Terminal 3: Partnership Proposals
cd "/Users/deedavis/NEXUS BACKEND"
./START_PARTNERSHIP_API.sh

# Terminal 4: Quote Generator (if exists)
python3 quote_generator_api.py

# Terminal 5: CapStat Generator (if exists)
python3 capability_statement_generator.py

# Terminal 6: RFP Generator
./START_RFP_GENERATOR.sh
```

**Check:** Do they all start on ports 5001-5004?

---

### **9:30 AM-12:00 PM - TEST GPSS (2.5 hours)**

**Open browser:** http://localhost:3000

**Click:** GPSS system card

**Test these features:**

1. **Dashboard**
   - [ ] Does it load?
   - [ ] Do stats display?
   - [ ] Any console errors? (F12)

2. **Upload RFP**
   - [ ] Can you click "Upload RFP" button?
   - [ ] Can you select a PDF?
   - [ ] Does it extract contacts?
   - [ ] Does it save to Airtable?

3. **Opportunities Table**
   - [ ] Do opportunities display?
   - [ ] Can you filter?
   - [ ] Can you sort?
   - [ ] Can you click an opportunity?

4. **AI Qualification**
   - [ ] Does it score opportunities (0-100)?
   - [ ] Does ProposalBio analysis work?
   - [ ] Any errors?

**For EVERY bug you find:**
- Write it down in bug tracker
- Note: WHERE it happens
- Note: WHAT the error says
- Note: HOW to reproduce it

---

### **12:00 PM-1:00 PM - LUNCH BREAK**

---

### **1:00 PM-3:30 PM - TEST ATLAS (2.5 hours)**

**Open:** http://localhost:3000 → ATLAS

**Test these features:**

1. **Projects Dashboard**
   - [ ] Does it load?
   - [ ] Can you see projects?
   - [ ] Can you create new project?

2. **RFP Analysis**
   - [ ] Can you upload RFP?
   - [ ] Does AI analysis work?
   - [ ] Does it show risks/requirements?

3. **WBS Generator**
   - [ ] Can you generate WBS?
   - [ ] Does it create work breakdown structure?
   - [ ] Can you edit it?

4. **Task Board**
   - [ ] Does Kanban view load?
   - [ ] Can you create tasks?
   - [ ] Can you drag/drop?
   - [ ] Do other views work (Timeline, List)?

5. **Calendar Export**
   - [ ] Can you export tasks?
   - [ ] Does .ics file download?
   - [ ] Does it open in Calendar.app?

**Write down ALL bugs.**

---

### **3:30 PM-5:00 PM - TEST DDCSS (1.5 hours)**

**Open:** http://localhost:3000 → DDCSS

**Test these features:**

1. **Prospects**
   - [ ] Can you see prospects?
   - [ ] Can you add new prospect?
   - [ ] Can you click a prospect?

2. **Corporate Partnerships**
   - [ ] Can you add FedEx/UPS?
   - [ ] Can you fill in fields?
   - [ ] Does it save to Airtable?

3. **ProposalBio Analysis**
   - [ ] Can you run analysis?
   - [ ] Does it work?

4. **Pipeline Tracking**
   - [ ] Can you change status?
   - [ ] Can you set next actions?

**Write down ALL bugs.**

---

### **5:00 PM-6:00 PM - TEST DOCUMENTS (1 hour)**

**Open:** http://localhost:3000 → DOCUMENTS

**Test ALL 4 tabs:**

1. **Quotes**
   - [ ] Can you add line items?
   - [ ] Does it calculate total?
   - [ ] Does "Generate PDF" work?
   - [ ] Does PDF look professional?

2. **Capability Statements**
   - [ ] Can you fill form?
   - [ ] Does "Generate PDF" work?
   - [ ] Does PDF look good?

3. **RFP Generator**
   - [ ] Can you create supplier RFP?
   - [ ] Does buyer protection work?
   - [ ] Does PDF generate?

4. **Partnership Proposals**
   - [ ] Can you click FedEx Template?
   - [ ] Does it auto-fill form?
   - [ ] Does "Generate Proposal PDF" work?
   - [ ] Does PDF look professional?

**Write down ALL bugs.**

---

### **6:00 PM-6:30 PM - CREATE BUG TRACKER**

**Open Airtable (or use spreadsheet)**

**Create table: "NEXUS Launch Bugs"**

**Columns:**
- Bug ID (number)
- System (GPSS/ATLAS/DDCSS/Documents/Dashboard)
- Description (what's broken)
- Severity (MUST FIX / SHOULD FIX / NICE TO FIX)
- Status (Open / Fixed / Wontfix)
- How to Reproduce
- Error Message (if any)
- Assigned To
- Fixed Date

**Enter ALL bugs you found today.**

---

### **6:30 PM-7:00 PM - PRIORITIZE**

**Review your bug list.**

**Mark each as:**
- **MUST FIX** - Blocks launch, prevents core workflow
- **SHOULD FIX** - Annoying but not blocking
- **NICE TO FIX** - Polish, cut if needed

**Count:**
- MUST FIX bugs: _____
- SHOULD FIX bugs: _____
- NICE TO FIX bugs: _____

**If you have more than 20 MUST FIX bugs, we're in trouble.**

---

## 📋 END OF DAY CHECKLIST

- [ ] Tested GPSS completely
- [ ] Tested ATLAS completely
- [ ] Tested DDCSS completely
- [ ] Tested Documents completely
- [ ] Created bug tracker with ALL bugs
- [ ] Prioritized each bug (MUST/SHOULD/NICE)
- [ ] Know exactly what needs fixing tomorrow
- [ ] Updated LAUNCH_DAILY_TRACKER.md

---

## 🎯 DELIVERABLE

**By end of Day 1, you should have:**

1. ✅ Complete list of bugs
2. ✅ Bugs prioritized by severity
3. ✅ Rough estimate of how many days to fix
4. ✅ Confidence whether 14 days is realistic

---

## 💡 TESTING TIPS

**1. Use Fresh Eyes**
- Pretend you've never seen NEXUS before
- Click everything
- Try to break it

**2. Check Console**
- F12 → Console tab
- Red errors = bugs
- Screenshot errors

**3. Test Real Workflows**
- Don't just click buttons
- Actually upload a real RFP
- Actually create a real project
- Actually generate a real document

**4. Test with Bad Data**
- What if you upload a non-PDF?
- What if you leave fields empty?
- What if you enter 999999999?

**5. Write Down EVERYTHING**
- Don't trust your memory
- Document as you go
- Be specific

---

## 🚨 IF YOU GET STUCK

**Backend won't start?**
- Check if something is already running on port 8000
- Try: `lsof -ti:8000 | xargs kill`
- Then restart

**Frontend won't start?**
- Try: `rm -rf node_modules && npm install`
- Then: `npm start`

**Document APIs won't start?**
- Check if ports 5001-5004 are free
- Try starting one at a time
- Skip any that don't exist yet

**Don't know how to test something?**
- Ask Dee
- Or skip it and mark as "Unable to test"

---

## 📊 EXPECTED OUTCOME

**Best Case:** 5-10 MUST FIX bugs  
→ We're on track for 14 days

**Realistic Case:** 15-20 MUST FIX bugs  
→ Tight but doable

**Worst Case:** 30+ MUST FIX bugs  
→ Need to cut scope or extend timeline

---

## ✅ TOMORROW (DAY 2)

You'll fix all ATLAS bugs.

But today, just TEST and DOCUMENT.

---

**START TESTING. WRITE DOWN EVERYTHING. SEE YOU AT END OF DAY 1.** 🚀
