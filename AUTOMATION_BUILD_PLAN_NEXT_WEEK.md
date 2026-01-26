# NEXUS AUTOMATION BUILD PLAN
**Scheduled: Next Week**

---

## 🎯 **GOAL:**

**Stop doing manual RFP work. Let NEXUS automate:**
- Supplier discovery
- Quote request email generation
- Quote tracking
- Bid calculation

---

## 📅 **TIMELINE: Next Week**

### **Day 1-2: Backend Integration**
- Fix syntax error in `nexus_backend.py` (line 5784)
- Test existing automation functions:
  - `find_suppliers_for_product()`
  - `generate_quote_request_email()`
  - `process_opportunity()`
- Create wrapper script for easy calling

### **Day 3-4: Command Line Tool**
- Build simple CLI:
  ```bash
  $ nexus rfp automate --product "Chlorine" --qty "13K gal"
  ```
- Output ready-to-send emails
- Save to Airtable automatically

### **Day 5: Testing**
- Test on 2-3 real RFPs
- Refine email templates
- Fix any bugs

---

## 🔧 **WHAT'S ALREADY BUILT:**

**In `nexus_backend.py` (80% complete):**
- ✅ Supplier search (database + Google + GSA)
- ✅ Email generation
- ✅ Quote scoring
- ✅ Bid calculation
- ✅ Airtable integration

**What needs to be added (20%):**
- ❌ PDF upload/parsing
- ❌ Simple UI or CLI
- ❌ Email sending integration
- ❌ Quote response tracking

---

## 📋 **BUILD CHECKLIST:**

### **Phase 1: Core Automation (Priority 1)**
- [ ] Fix `nexus_backend.py` syntax error
- [ ] Test `find_suppliers_for_product()` function
- [ ] Test `generate_quote_request_email()` function
- [ ] Create `automate_rfp.py` wrapper script
- [ ] Test end-to-end with HCMA Chlorine example

### **Phase 2: Command Line Interface (Priority 2)**
- [ ] Build CLI tool with argparse
- [ ] Add command: `nexus rfp analyze <pdf>`
- [ ] Add command: `nexus rfp find-suppliers <product>`
- [ ] Add command: `nexus rfp generate-emails <opportunity_id>`
- [ ] Add command: `nexus rfp automate <pdf>` (all-in-one)

### **Phase 3: Email Integration (Priority 3)**
- [ ] Integrate with Gmail API or SMTP
- [ ] Add "Send All" functionality
- [ ] Track sent emails in Airtable
- [ ] Add follow-up reminders

### **Phase 4: Web UI (Future)**
- [ ] Upload page
- [ ] Automation dashboard
- [ ] Email review/edit page
- [ ] Quote comparison page

---

## 🚀 **SUCCESS METRICS:**

**Before Automation:**
- Time per RFP: 3 hours
- Manual supplier research
- Manual email writing
- Manual tracking

**After Automation:**
- Time per RFP: 30 seconds
- Automated supplier discovery (8+ suppliers)
- Automated email generation
- Automated tracking in Airtable

**Goal: 10x faster RFP processing** ⚡

---

## 💡 **USE CASES TO TEST:**

1. **HCMA Liquid Chlorine** (already know requirements)
2. **CPS Energy RFQ** (current bid)
3. **Madison Heights Lawn Service** (service-based)
4. **Any new commodity RFP** (paper, salt, etc.)

---

## 📝 **NOTES:**

- Keep buyer information anonymous in supplier emails (strategic!)
- Auto-check for diversity/local preference requirements
- Generate compliance checklists automatically
- Calculate bid pricing with recommended margins

---

## ✅ **WHEN COMPLETE:**

**You'll be able to:**
```bash
# Upload RFP
$ nexus rfp automate photos_and_videos/new_rfp.pdf

🤖 Processing RFP...
✅ Product: Road Salt
✅ Quantity: 500 tons
✅ Location: Detroit, MI
✅ Deadline: Feb 15, 2026

✅ Found 8 suppliers
✅ Generated 8 quote request emails
✅ Added to Airtable
✅ Emails saved to: /quotes/road_salt_quotes.txt

📧 Ready to send:
   1. Morton Salt - sales@mortonsalt.com
   2. Cargill - quotes@cargill.com
   3. Detroit Salt - info@detroitsalt.com
   ... 5 more

Copy/paste and send, or use:
$ nexus rfp send-emails road_salt_quotes.txt

Done in 30 seconds! ⚡
```

---

**Status: Documented and ready to build next week** ✅

**For now: Continue manual process (but faster with generated emails/checklists)**
