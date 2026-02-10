# Assistant Quick Start: Generate FedEx/UPS Documents in NEXUS

**Time Required:** 5 minutes total  
**System:** NEXUS Document Generator  
**Output:** 3 professional PDFs ready for supplier diversity portals

---

## 📋 WHAT YOU'RE GENERATING

1. ✅ **Capability Statement** - Company overview for supplier portals
2. ✅ **FedEx Partnership Proposal** - Professional proposal for FedEx supplier diversity
3. ✅ **UPS Partnership Proposal** - Professional proposal for UPS supplier diversity

---

## 🚀 STEP-BY-STEP (5 Minutes)

### **STEP 1: Open NEXUS** (30 seconds)

1. Open Terminal
2. Run these commands:

```bash
cd "/Users/deedavis/NEXUS BACKEND/nexus-frontend"
npm start
```

3. **WAIT** for browser to open automatically (http://localhost:3000)

4. In **ANOTHER terminal window**, start the document APIs:

```bash
cd "/Users/deedavis/NEXUS BACKEND"
./START_PARTNERSHIP_API.sh
```

**Keep both terminals open!**

---

### **STEP 2: Generate Capability Statement** (1 minute)

1. On NEXUS landing page, click **"DOCUMENTS"** card

2. Click **"Capability Statements"** tab

3. Fill in the form:

   **Company Name:**
   ```
   Dee Davis Inc.
   ```

   **NAICS Codes:**
   ```
   561440, 492110
   ```

   **Core Competencies:**
   ```
   Mobile Notary Services - Nationwide coverage through automated dispatch platform (Snapdocs). Professional notarization including loan signings, real estate transactions, corporate documents, and general notarizations. Same-day service available in 200+ metro areas.
   
   Courier Services - Time-sensitive document and package delivery with secure chain-of-custody handling. Same-day delivery, rush services, legal document filing, medical records transport (HIPAA compliant), and proof of delivery documentation.
   
   Technology-Enabled Operations - Real-time tracking, digital scheduling, electronic invoicing, quality assurance monitoring, and 99.5%+ platform uptime.
   
   EDWOSB Certified - Woman-owned small business supporting supplier diversity initiatives.
   ```

   **Past Performance:**
   ```
   Dee Davis Inc. provides mobile notary and courier services to corporate clients, business centers, and government agencies nationwide. Our automated dispatch platform connects 1,000+ vetted notaries across all 50 states, providing consistent quality service with under 2-hour average response time in metro areas.
   
   Key Capabilities:
   - Nationwide coverage (all 50 states)
   - Average response time: Under 2 hours
   - 99%+ successful completion rate
   - Customer satisfaction: 4.5+ out of 5
   - All contractors background-checked
   - $1M+ E&O insurance coverage
   - HIPAA compliant handling
   - Real-time tracking and reporting
   
   Services Include: General notarizations, loan signings, real estate transactions, corporate documents, apostille coordination, same-day courier delivery, rush services, legal filing, and secure document transport.
   ```

4. Click **"Generate PDF"**

5. PDF opens in new tab - review it

6. Save to desktop: **"Dee_Davis_Inc_Capability_Statement.pdf"**

✅ **Capability Statement: DONE**

---

### **STEP 3: Generate FedEx Partnership Proposal** (1 minute)

1. Click **"Partnership Proposals"** tab

2. Click **"FedEx Template"** button (this pre-fills the form!)

3. Add contact information:

   **Contact Email:**
   ```
   [Insert Dee's email]
   ```

   **Contact Phone:**
   ```
   [Insert Dee's phone]
   ```

4. Click **"Generate Proposal PDF"**

5. PDF opens in new tab - review it (it's beautiful!)

6. Save to desktop: **"Partnership_Proposal_FedEx.pdf"**

✅ **FedEx Proposal: DONE**

---

### **STEP 4: Generate UPS Partnership Proposal** (1 minute)

1. Stay on **"Partnership Proposals"** tab

2. Click **"UPS Template"** button (pre-fills for UPS!)

3. Add contact information again:

   **Contact Email:**
   ```
   [Insert Dee's email]
   ```

   **Contact Phone:**
   ```
   [Insert Dee's phone]
   ```

4. Click **"Generate Proposal PDF"**

5. PDF opens in new tab - review it

6. Save to desktop: **"Partnership_Proposal_UPS.pdf"**

✅ **UPS Proposal: DONE**

---

## ✅ YOU'RE DONE!

**You now have 3 professional PDFs:**

1. ✅ `Dee_Davis_Inc_Capability_Statement.pdf`
2. ✅ `Partnership_Proposal_FedEx.pdf`
3. ✅ `Partnership_Proposal_UPS.pdf`

**Time taken:** 5 minutes  
**Quality:** Professional, DDI-branded, ready to submit

---

## 📧 NEXT STEPS

**Now you can:**

1. Register at FedEx supplier portal (https://suppliers.sourcing.fedex.com/)
   - Upload all 3 PDFs

2. Register at UPS supplier portal (https://ups.supplierone.co/)
   - Upload all 3 PDFs

3. Send outreach emails with PDFs attached

---

## 🆘 IF SOMETHING GOES WRONG

### **Problem: Browser doesn't open**
**Solution:** Manually open http://localhost:3000

---

### **Problem: "Generate PDF" button says API error**
**Solution:**
1. Check that you ran `./START_PARTNERSHIP_API.sh` in second terminal
2. Look for "Server starting on http://localhost:5004" message
3. If not running, run the command again

---

### **Problem: Can't find the templates**
**Solution:** 
- Make sure you're on **"Partnership Proposals"** tab (4th tab)
- Look for purple "FedEx Template" and yellow "UPS Template" buttons at top

---

### **Problem: PDF looks wrong or incomplete**
**Solution:**
- This shouldn't happen, but if it does, try generating again
- Make sure all form fields were filled in
- Check that contact email and phone were added

---

## 💡 PRO TIPS

**Tip 1:** Keep both terminal windows open the whole time  
**Tip 2:** If you need to generate more proposals for other companies, just change the "Partner Company Name" field  
**Tip 3:** Save all PDFs to a folder called "FedEx_UPS_Registration_Docs" on desktop  

---

## 📋 CHECKLIST

Before you move on to portal registration, verify:

- [ ] Capability Statement PDF generated and saved
- [ ] FedEx Partnership Proposal PDF generated and saved
- [ ] UPS Partnership Proposal PDF generated and saved
- [ ] All PDFs are on desktop and easy to find
- [ ] All PDFs open correctly and look professional
- [ ] Contact information (email/phone) is correct in proposals

**If all checked, you're ready to proceed with portal registration!**

---

## 🎯 WHAT MAKES THIS BETTER

### **OLD WAY (Manual):**
- ❌ Read 10-page markdown files
- ❌ Copy content into Word
- ❌ Format manually for 2 hours
- ❌ Hope it looks professional
- ❌ Convert to PDF
- ❌ Total time: 3-4 hours

### **NEW WAY (NEXUS):**
- ✅ Click template button
- ✅ Add email and phone
- ✅ Click generate
- ✅ Professional PDF in 30 seconds
- ✅ **Total time: 5 minutes**

---

**YOU'VE GOT THIS!** 🚀

If you have ANY questions, ask Dee. But this should be super straightforward.

---

*The system does all the hard work. You just click buttons and save files.*
