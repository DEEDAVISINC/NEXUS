# ASSISTANT TASK: FedEx/UPS Corporate Partnership Setup (via DDCSS)

**Assigned To:** [Assistant Name]  
**Deadline:** Complete setup within 7 days  
**Goal:** Add FedEx and UPS to DDCSS as corporate partnership prospects, complete analysis, generate documents, register in portals, and send outreach

**System Used:** DDCSS (Dee Davis Client Sourcing System)

---

## ✅ WHAT YOU'RE DOING

Adding FedEx and UPS as corporate partnership prospects in **DDCSS** (Dee Davis Client Sourcing System), analyzing their supplier diversity programs, generating proposals, registering in their portals, and sending outreach emails.

**This is CLIENT SOURCING** for the notary business - treated like any other corporate prospect in DDCSS.

**Target Revenue:** $5K-10K/month passive income  
**Your Role:** Set up prospects in DDCSS, run analyses, generate documents, register, and track outreach

---

## 📋 STEP-BY-STEP CHECKLIST

### PHASE 1: SET UP IN DDCSS (Day 1)

**Open DDCSS and create prospects:**

1. [ ] Open NEXUS → DDCSS → Corporate Partnerships
2. [ ] Create "DDCSS Corporate Partnerships" table in Airtable (if doesn't exist - see `DDCSS_CORPORATE_PARTNERSHIPS_INTEGRATION.md` for schema)
3. [ ] Add FedEx as prospect:
   - Company Name: FedEx
   - Prospect Type: Supplier Diversity Partner
   - Services Offered: Mobile Notary, Courier Services
   - Partnership Status: Research
   - Supplier Diversity Program: ✓
   - Portal URL: https://suppliers.sourcing.fedex.com/
   - Estimated Revenue: $8,000
   - Next Action: "Run ProposalBio analysis"

4. [ ] Add UPS as prospect:
   - Company Name: UPS
   - Prospect Type: Supplier Diversity Partner
   - Services Offered: Mobile Notary, Courier Services
   - Partnership Status: Research
   - Supplier Diversity Program: ✓
   - Portal URL: https://ups.supplierone.co/
   - Estimated Revenue: $8,000
   - Next Action: "Run ProposalBio analysis"

**Gather documents (you'll need these later):**

- [ ] Federal Tax ID (EIN)
- [ ] EDWOSB Certification documents
- [ ] D-U-N-S Number (if we don't have, get free at dnb.com)
- [ ] Business License
- [ ] Certificate of Insurance (General Liability)
- [ ] Certificate of Insurance (E&O - Errors & Omissions)
- [ ] 2-3 business references

---

### PHASE 2: RUN PROPOSALBIO ANALYSIS (Day 1)

**Analyze FedEx and UPS supplier diversity programs:**

**For FedEx:**

1. [ ] Click on FedEx prospect in DDCSS
2. [ ] Run ProposalBio analysis (copy template from `DDCSS_CORPORATE_PARTNERSHIPS_INTEGRATION.md`)
3. [ ] Key points to include:
   - Program Status: Active, WBENC-recognized
   - Service Gap: Most locations DON'T have notary services
   - Decision-Makers: Supplier Diversity Program Manager + FedEx Office Operations
   - Strategy: Portal registration + direct outreach
   - Estimated Value: $8,000-40,000/month
4. [ ] Save analysis to "ProposalBio Analysis" field in DDCSS
5. [ ] Update Next Action: "Generate partnership proposal"

**For UPS:**

1. [ ] Click on UPS prospect in DDCSS
2. [ ] Run ProposalBio analysis
3. [ ] Key points:
   - Program Status: Active, 5,500+ UPS Store locations
   - Service Gap: Overflow capacity + mobile service
   - Decision-Makers: Supplier Diversity Manager + UPS Store Operations
   - Strategy: Portal registration + SupplierOne platform
4. [ ] Save analysis to "ProposalBio Analysis" field
5. [ ] Update Next Action: "Generate partnership proposal"

---

### PHASE 3: GENERATE DOCUMENTS VIA NEXUS (Day 2)

**Use NEXUS Document Generator for all documents:**

**Step 1: Start NEXUS**
```bash
cd "/Users/deedavis/NEXUS BACKEND/nexus-frontend"
npm start
```

**Step 2: Start Partnership Proposal API** (separate terminal)
```bash
cd "/Users/deedavis/NEXUS BACKEND"
./START_PARTNERSHIP_API.sh
```

**Step 3: Generate Capability Statement**
1. Open browser: http://localhost:3000
2. Click "DOCUMENTS" card
3. Click "Capability Statements" tab
4. Fill in form:
   - **Company Name:** Dee Davis Inc.
   - **NAICS Codes:** 561440 (Document Preparation Services), 492110 (Couriers and Express Delivery Services)
   - **Core Competencies:** 
     ```
     Mobile Notary Services - Nationwide coverage through automated dispatch platform (Snapdocs). Professional notarization including loan signings, real estate transactions, corporate documents, and general notarizations. Same-day service available in 200+ metro areas.
     
     Courier Services - Time-sensitive document and package delivery with secure chain-of-custody handling. Same-day delivery, rush services, legal document filing, medical records transport (HIPAA compliant), and proof of delivery documentation.
     
     Technology-Enabled Operations - Real-time tracking, digital scheduling, electronic invoicing, quality assurance monitoring, and 99.5%+ platform uptime.
     
     EDWOSB Certified - Woman-owned small business supporting supplier diversity initiatives.
     ```
   - **Past Performance:**
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

5. Click "Generate PDF"
6. Save as: `Dee_Davis_Inc_Capability_Statement.pdf`
7. [ ] Upload to both FedEx and UPS prospects in DDCSS (Documents field)

**Step 4: Generate FedEx Partnership Proposal**
1. Click "Partnership Proposals" tab
2. Click "FedEx Template" button (auto-fills form!)
3. Add contact info:
   - Contact Email: [Dee's email]
   - Contact Phone: [Dee's phone]
4. Click "Generate Proposal PDF"
5. Save as: `Partnership_Proposal_FedEx.pdf`
6. [ ] Upload to FedEx prospect in DDCSS (Documents field)
7. [ ] Update FedEx in DDCSS:
   - Proposal Sent: ✓
   - Proposal Date: Today
   - Next Action: "Register in supplier portal"

**Step 5: Generate UPS Partnership Proposal**
1. Stay on "Partnership Proposals" tab
2. Click "UPS Template" button
3. Add contact info
4. Click "Generate Proposal PDF"
5. Save as: `Partnership_Proposal_UPS.pdf`
6. [ ] Upload to UPS prospect in DDCSS (Documents field)
7. [ ] Update UPS in DDCSS:
   - Proposal Sent: ✓
   - Proposal Date: Today
   - Next Action: "Register in supplier portal"

---

### PHASE 4: REGISTER WITH FEDEX (Day 3)

**FedEx Portal: https://suppliers.sourcing.fedex.com/**

**Step 1: Create Account**
- [ ] Go to https://suppliers.sourcing.fedex.com/
- [ ] Click "Register" or "New Supplier"
- [ ] Create login credentials
- [ ] Verify email

**Step 2: Complete Company Profile**
- [ ] Company Name: Dee Davis Inc.
- [ ] Business Type: Small Business, Woman-Owned
- [ ] Certifications: EDWOSB (upload certification)
- [ ] DUNS Number: [Enter from documents]
- [ ] Tax ID: [Enter from documents]
- [ ] Primary Contact: Dee Davis
- [ ] Email: [Company email]
- [ ] Phone: [Company phone]
- [ ] Business Address: [Company address]

**Step 3: Upload Documents**
- [ ] EDWOSB Certification
- [ ] Certificate of Insurance (General Liability)
- [ ] Certificate of Insurance (E&O)
- [ ] Capability Statement PDF (from NEXUS)
- [ ] Business License

**Step 4: Complete Service Offering**
- [ ] Primary Category: Business Services
- [ ] Sub-Category: Notary Services, Courier Services
- [ ] Service Description:
  ```
  Mobile notary and courier services with nationwide coverage. 
  Automated dispatch platform providing same-day service in 200+ 
  metro areas. Supports business center operations, corporate 
  clients, and time-sensitive document needs. EDWOSB certified 
  woman-owned business.
  ```
- [ ] Geographic Coverage: All 50 United States
- [ ] Annual Revenue: [Enter actual or estimated]
- [ ] Years in Business: [Enter accurate number]

**Step 5: Submit Application**
- [ ] Review all information for accuracy
- [ ] Submit for review
- [ ] Save confirmation number: _______________
- [ ] Screenshot confirmation page

**Step 6: Update DDCSS**
- [ ] Open FedEx prospect in DDCSS
- [ ] Update fields:
  - Portal Registered: ✓
  - Registration Date: Today
  - Partnership Status: `Outreach`
  - Next Action: "Send outreach email to supplier diversity contact"
  - Next Action Date: Tomorrow

---

### PHASE 5: REGISTER WITH UPS (Day 4)

**UPS Portal: https://ups.supplierone.co/**

**Step 1: Create Account**
- [ ] Go to https://ups.supplierone.co/
- [ ] Click "Register Your Business"
- [ ] Create login credentials
- [ ] Verify email

**Step 2: Complete Company Profile**
- [ ] Company Name: Dee Davis Inc.
- [ ] Business Type: Small Business, Woman-Owned
- [ ] Certifications: EDWOSB (upload certification)
- [ ] DUNS Number: [Enter from documents]
- [ ] Tax ID: [Enter from documents]
- [ ] Primary Contact: Dee Davis
- [ ] Email: [Company email]
- [ ] Phone: [Company phone]
- [ ] Business Address: [Company address]

**Step 3: Upload Documents**
- [ ] EDWOSB Certification
- [ ] Certificate of Insurance (General Liability)
- [ ] Certificate of Insurance (E&O)
- [ ] Capability Statement PDF (from NEXUS)
- [ ] Business License

**Step 4: Complete Service Offering**
- [ ] Primary Category: Professional Services
- [ ] Sub-Category: Notary Services, Courier/Delivery Services
- [ ] Service Description:
  ```
  Nationwide mobile notary and courier services supporting 
  business center operations and corporate clients. Automated 
  dispatch platform (Snapdocs) with 1,000+ vetted notaries 
  across all 50 states. Average response time under 2 hours 
  in metro areas. EDWOSB certified woman-owned business.
  ```
- [ ] Geographic Coverage: National (All States)
- [ ] Diversity Certification: WBENC-Eligible, EDWOSB Certified

**Step 5: Join Women Exporters Program (Bonus)**
- [ ] While in UPS portal, look for "Women Exporters Program"
- [ ] Apply to join (increases visibility)
- [ ] Fill out additional profile if required

**Step 6: Submit Application**
- [ ] Review all information for accuracy
- [ ] Submit for review
- [ ] Save confirmation number: _______________
- [ ] Screenshot confirmation page

**Step 7: Update DDCSS**
- [ ] Open UPS prospect in DDCSS
- [ ] Update fields:
  - Portal Registered: ✓
  - Registration Date: Today
  - Partnership Status: `Outreach`
  - Next Action: "Send outreach email"
  - Next Action Date: Tomorrow

---

### PHASE 6: SEND OUTREACH EMAILS (Day 5)

**Use SalesScripts from DDCSS for personalized outreach:**

**For FedEx:**

**Find Contact (if not already in DDCSS):**
- [ ] Call 1-800-463-3339
- [ ] Ask for "Supplier Diversity Department"
- [ ] Get name and email of Supplier Diversity Program Manager
- [ ] Get name and email of FedEx Office Operations contact
- [ ] Update DDCSS with contact info:
  - Primary Contact Name: [Name]
  - Primary Contact Title: [Title]
  - Primary Contact Email: [Email]
  - Primary Contact Phone: [Phone]

**Send Email (use SalesScript from DDCSS):**

See `DDCSS_CORPORATE_PARTNERSHIPS_INTEGRATION.md` for full email template.

**Key template:**

**Subject:** EDWOSB Supplier - Mobile Notary & Courier Services

```
Hi [Name],

I'm reaching out from Dee Davis Inc., a certified EDWOSB that recently 
registered in your supplier diversity portal (Confirmation #: [NUMBER]).

We provide mobile notary and courier services nationwide and see a 
significant opportunity to support FedEx Office locations that currently 
don't offer notary services.

Key Highlights:
• EDWOSB certified woman-owned business
• Nationwide coverage through automated dispatch platform
• Mobile notary services (addresses current FedEx service gap)
• Courier services for time-sensitive documents
• Scalable partnership with no infrastructure investment
• Revenue-sharing model (zero upfront cost to FedEx)

I'd love to schedule a brief 15-minute call to discuss how we can support 
your supplier diversity goals while adding value to FedEx Office operations.

Are you available next week for a quick call?

Best regards,
[Your name]
On behalf of Dee Davis
Dee Davis Inc.
[Phone]
[Email]
```

- [ ] Send email to Supplier Diversity contact
- [ ] Send email to FedEx Office Operations contact (if different)
- [ ] Update DDCSS:
  - Outreach Email Sent: ✓
  - Outreach Date: Today
  - Next Action: "Follow up in 48 hours if no response"
  - Next Action Date: [Today + 2 days]

**For UPS:**

**Use Portal Messaging:**
- [ ] Log into UPS SupplierOne portal
- [ ] Look for "Contact" or "Message" feature
- [ ] Send similar message through portal system

**Also find direct contact:**
- [ ] Search LinkedIn for "UPS Supplier Diversity Manager"
- [ ] Search LinkedIn for "UPS Store Operations Manager"
- [ ] Connect with 2-3 relevant contacts
- [ ] Send InMail or email with same message as above

- [ ] Log all outreach in tracking spreadsheet

---

### PHASE 6: FOLLOW-UP (Days 6-7)

**Day 6:**
- [ ] Check both portals for approval status
- [ ] Check email for any responses
- [ ] If no response from FedEx, call main number again
- [ ] If no response from UPS, send follow-up message via portal

**Day 7:**
- [ ] Create follow-up email for non-responders:

**Subject:** Following Up - EDWOSB Mobile Notary & Courier Partnership

```
Hi [Name],

I wanted to follow up on my email from [DATE] regarding Dee Davis Inc.'s 
mobile notary and courier services.

We're a certified EDWOSB already registered in your supplier diversity 
portal and excited about the opportunity to support [FedEx/UPS] business 
center operations.

Quick recap:
• Mobile notary services (fills service gap at many locations)
• Nationwide courier services
• Revenue-sharing model (no upfront investment)
• Supports your supplier diversity initiatives

Would you be open to a brief 10-minute call this week or next?

I'm happy to work around your schedule.

Best regards,
[Your name]
Dee Davis Inc.
[Phone]
```

- [ ] Send follow-up to anyone who hasn't responded
- [ ] Update DDCSS for each company:
  - If response received:
    - Response Received: ✓
    - Response Date: [Date]
    - Partnership Status: `Meeting Scheduled` (if applicable)
    - Next Action: "Prepare for meeting" or "Continue follow-up"
  - If no response:
    - Next Action: "Final follow-up in 1 week"
    - Next Action Date: [Today + 7 days]

---

## 📊 TRACKING IN DDCSS

**All tracking happens in DDCSS - no separate spreadsheet needed!**

**DDCSS tracks:**
- ✅ Company information
- ✅ Contact details
- ✅ ProposalBio analysis
- ✅ Documents (proposals, capability statements)
- ✅ Portal registration status
- ✅ Outreach email status
- ✅ Response tracking
- ✅ Meeting scheduling
- ✅ Partnership status
- ✅ Next actions and dates
- ✅ Revenue estimates and actuals

**Daily workflow:**
1. Open DDCSS
2. Check "Next Action Date" for overdue tasks
3. Take action (follow-up, send email, etc.)
4. Update status
5. Set next action and date

**Airtable will send reminders when "Next Action Date" arrives.**

---

## 📞 PHONE SCRIPTS (If You Need to Call)

### Calling FedEx Main Line:

**You:** "Hi, I'm calling on behalf of Dee Davis Inc. We're a certified EDWOSB 
that recently registered in your supplier diversity portal. I need to speak 
with someone in the Supplier Diversity Department regarding mobile notary 
and courier services."

**Wait for transfer...**

**You:** "Hi [Name], I'm [Your Name] calling on behalf of Dee Davis Inc. 
We're a certified woman-owned business offering mobile notary and courier 
services nationwide. We registered in your supplier diversity portal 
and would like to discuss partnership opportunities to support FedEx Office 
locations. Would you be the right person to speak with, or can you direct 
me to who handles business service vendor partnerships?"

**Get their email and follow up in writing.**

### Calling UPS (if needed):

**You:** "Hi, I'm calling on behalf of Dee Davis Inc. We registered in the 
UPS SupplierOne portal as a woman-owned business offering mobile notary 
and courier services. I'm trying to connect with the right person to discuss 
partnership opportunities. Can you direct me to the Supplier Diversity team 
or UPS Store Operations?"

---

## 🚨 COMMON QUESTIONS & ANSWERS

**Q: "What's your annual revenue?"**  
A: [Use actual number from company records - don't make this up]

**Q: "How many employees do you have?"**  
A: "We have [X] full-time staff plus a network of 1,000+ independent contractors 
through our Snapdocs dispatch platform."

**Q: "What's your service area?"**  
A: "Nationwide - all 50 states. We can provide same-day service in over 200 
metro areas with 2-hour average response time."

**Q: "What makes you different from other notary services?"**  
A: "Three key differentiators: First, we're EDWOSB certified which supports 
your diversity goals. Second, our automated dispatch platform provides 
nationwide scalability that individual notaries can't match. Third, we 
offer both notary AND courier services, so you have one vendor for multiple 
document-related needs."

**Q: "What's the pricing?"**  
A: "We typically charge $75-100 per mobile notary service. For a partnership 
model, we're proposing a revenue-sharing structure where your locations 
would receive 30% of each transaction with zero upfront investment. We're 
flexible and happy to discuss what works best for your business model."

**Q: "Do you have references?"**  
A: "Yes, absolutely. We can provide references upon request." 
[Have the 2-3 business references ready from the documents you gathered]

---

## ✅ COMPLETION CHECKLIST

**Phase 1: Documents**
- [ ] All documents gathered and in folder
- [ ] Documents scanned/PDF'd if needed

**Phase 2: Capability Statement**
- [ ] NEXUS running
- [ ] Capability statement generated
- [ ] PDF saved and filed

**Phase 3: FedEx Registration**
- [ ] Account created
- [ ] Profile completed
- [ ] Documents uploaded
- [ ] Application submitted
- [ ] Confirmation number saved

**Phase 4: UPS Registration**
- [ ] Account created
- [ ] Profile completed
- [ ] Documents uploaded
- [ ] Women Exporters Program joined
- [ ] Application submitted
- [ ] Confirmation number saved

**Phase 5: Initial Outreach**
- [ ] FedEx contacts identified
- [ ] FedEx emails sent
- [ ] UPS contacts identified
- [ ] UPS messages/emails sent
- [ ] Tracking spreadsheet created and updated

**Phase 6: Follow-up**
- [ ] Portal status checked
- [ ] Follow-up emails sent (if needed)
- [ ] All activity logged

---

## 📧 REPORT BACK TO DEE

**After completing Day 7, send Dee an update email:**

**Subject:** FedEx/UPS Registration Complete - Status Update

```
Hi Dee,

Completed the FedEx/UPS supplier diversity registration. Here's the status:

FEDEX:
• Portal Registration: ✅ Complete (Confirmation #: [NUMBER])
• Documents Uploaded: ✅ [List what was uploaded]
• Outreach Emails Sent: ✅ [Number] contacts
• Responses Received: [Number and who]
• Status: [Pending/In Discussion/etc.]

UPS:
• Portal Registration: ✅ Complete (Confirmation #: [NUMBER])
• Documents Uploaded: ✅ [List what was uploaded]
• Outreach Emails Sent: ✅ [Number] contacts
• Responses Received: [Number and who]
• Status: [Pending/In Discussion/etc.]

NEXT STEPS:
[List what happens next based on responses received]

All tracking information is in: FedEx_UPS_Outreach_Tracker.xlsx

Let me know if you need anything else!

[Your name]
```

---

## 📁 FILES YOU'LL USE

**Reference Documents (READ THESE FIRST):**
1. `FEDEX_UPS_SUPPLIER_DIVERSITY_PROPOSAL.md` - Full partnership proposal
2. `FEDEX_UPS_ACTION_CHECKLIST.md` - Detailed checklist with talking points
3. `DEE_DAVIS_INC_CAPABILITY_STATEMENT_NOTARY_COURIER.md` - Company overview

**Generated Documents:**
1. `Dee_Davis_Inc_Capability_Statement.pdf` - Create this via NEXUS

**Your Created Files:**
1. `FedEx_UPS_Registration_Docs/` folder with all documents
2. `FedEx_UPS_Outreach_Tracker.xlsx` spreadsheet

---

## ⏰ TIMELINE

**Day 1:** Gather documents + Generate capability statement  
**Days 2-3:** Complete both portal registrations  
**Days 4-5:** Initial outreach emails  
**Days 6-7:** Follow-up and status check  

**Total Time:** 7 days to complete everything

---

## 🆘 IF YOU GET STUCK

**Issue: Can't find a document**
- Check company files, Dropbox, Google Drive
- Ask Dee directly: "I need [document name] for the FedEx/UPS registration"

**Issue: NEXUS won't start**
- Make sure you're in the right directory
- Try: `npm install` first, then `npm start`
- If still broken, ask Dee or generate capability statement manually using the markdown file

**Issue: Portal won't accept upload**
- Check file size (must be under 10MB usually)
- Check file format (must be PDF)
- Try renaming file to remove special characters

**Issue: No response after 7 days**
- Be patient - large companies move slowly
- Send second follow-up after 10 days
- Try calling main number again
- Update Dee on status

**Issue: They ask a question you don't know**
- Say: "That's a great question. Let me confirm with Dee Davis and get back to you today."
- Ask Dee immediately
- Respond same day with answer

---

## 💰 REMEMBER THE GOAL

**This partnership could generate $5K-10K/month in passive income for the company.**

Your job is to get Dee Davis Inc. in front of the right decision-makers at FedEx 
and UPS. Do it professionally, promptly, and thoroughly.

**Good luck! You've got this.** 🚀

---

*Questions? Ask Dee before starting.*
