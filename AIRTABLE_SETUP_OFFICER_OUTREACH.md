# 📊 AIRTABLE SETUP - OFFICER OUTREACH SYSTEM

## Quick Setup Guide (10 Minutes)

**Status:** Required for officer outreach system to work

---

## 🎯 WHAT YOU NEED TO CREATE

You need **2 things** in Airtable:

1. ✅ **Officer Outreach Tracking** table (new)
2. ✅ **Add 2 fields** to existing Opportunities table

---

## 📋 STEP 1: CREATE NEW TABLE

### Table Name: **Officer Outreach Tracking**

In your NEXUS Airtable base, create a new table with this exact name.

---

## 📝 STEP 2: ADD FIELDS TO NEW TABLE

Add these fields to the **Officer Outreach Tracking** table:

| Field Name | Field Type | Description |
|-----------|-----------|-------------|
| **Officer Name** | Single line text | Name of contracting officer |
| **Officer Email** | Email | Officer's email address |
| **Officer Phone** | Phone number | Optional phone |
| **Opportunity Title** | Single line text | Title of closed opportunity |
| **Solicitation Number** | Single line text | Original solicitation # |
| **Agency** | Single line text | Agency/organization name |
| **Related Opportunity** | Link to another record | Links to: Opportunities |
| **Letter Generated Date** | Date | When letter was created |
| **Status** | Single select | Draft, Sent, Follow-up Needed, Responded, Added to Vendor List, No Response |
| **Letter Content** | Long text | Full letter text |
| **Subject Line** | Single line text | Email subject line |
| **Date Sent** | Date | When you sent the email |
| **Follow-up Date** | Date | 10 days after sent |
| **Response Received** | Checkbox | Did they respond? |
| **Response Date** | Date | When they responded |
| **Response Notes** | Long text | What they said |
| **Added to Vendor List** | Checkbox | Success! |
| **Tags** | Multiple select | VA, DoD, State, Local, Healthcare, IT, etc. |
| **Priority** | Single select | High, Medium, Low |
| **Next Action** | Single line text | What to do next |
| **Next Action Date** | Date | When to do it |
| **ProposalBio Score** | Number | Quality score 0-100 |
| **Quality Badge** | Single line text | 🟢/🟡/🔴 indicator |
| **Quality Status** | Single select | Ready to Send, Good - Minor Edits, Needs Improvement |
| **Improvement Notes** | Long text | ProposalBio™ recommendations |
| **Created By** | Single line text | Default: "NEXUS AI" |

### Single Select Options:

**Status:**
- Draft
- Sent
- Follow-up Needed
- Responded
- Added to Vendor List
- No Response

**Priority:**
- High
- Medium
- Low

**Quality Status:**
- Ready to Send
- Good - Minor Edits
- Needs Improvement

**Tags:** (Add as needed)
- VA
- DoD
- DOE
- State
- Local
- Healthcare
- IT
- Construction
- Supplies

---

## 📋 STEP 3: UPDATE OPPORTUNITIES TABLE

Add these **3 fields** to your existing **Opportunities** table:

| Field Name | Field Type | Description |
|-----------|-----------|-------------|
| **Officer Outreach Sent** | Checkbox | Has letter been generated? |
| **Officer Outreach Date** | Date | When letter was generated |
| **Officer Outreach Link** | Link to another record | Links to: Officer Outreach Tracking |

This creates a two-way link between opportunities and outreach letters.

---

## 👁️ STEP 4: CREATE USEFUL VIEWS

In the **Officer Outreach Tracking** table, create these views:

### View 1: **✉️ Ready to Send**
- **Filter:** Status = "Draft"
- **Sort:** Letter Generated Date (newest first)
- **Purpose:** Letters ready to review and send

### View 2: **⏰ Follow-up Needed**
- **Filter:** 
  - Status = "Sent"
  - Follow-up Date ≤ Today
  - Response Received = unchecked
- **Sort:** Follow-up Date (oldest first)
- **Purpose:** Officers who need follow-up

### View 3: **✅ Responded**
- **Filter:** Response Received = checked
- **Sort:** Response Date (newest first)
- **Purpose:** Track successful outreach

### View 4: **🟢 High Quality (75+)**
- **Filter:** ProposalBio Score ≥ 75
- **Sort:** ProposalBio Score (highest first)
- **Purpose:** Best letters to send first

### View 5: **📊 By Agency**
- **Type:** Grouped by Agency
- **Sort:** Officer Name
- **Purpose:** Organize by contracting agency

---

## ✅ VERIFICATION CHECKLIST

After setup, verify:

- [ ] **Officer Outreach Tracking** table exists
- [ ] All 24+ fields created in outreach table
- [ ] **Opportunities** table has 3 new fields
- [ ] Link field connects both tables
- [ ] At least 2-3 views created
- [ ] Status field has all 6 options
- [ ] Priority field has 3 options
- [ ] Tags field has common tags

---

## 🧪 TEST THE SYSTEM

Once Airtable is set up:

```bash
python3 contracting_officer_outreach.py
```

**What should happen:**

1. System scans **Opportunities** table
2. Finds closed opportunities with officer contact
3. Generates letters with your company info
4. Creates records in **Officer Outreach Tracking**
5. Links to original opportunity
6. Includes ProposalBio™ quality scores

**Expected output:**
```
Found 3 closed opportunities to reach out on

[1/3] Processing: Female Condoms...
    🟢 HIGH QUALITY ProposalBio™ Score: 78.3/100
    ✅ Letter saved to Airtable

✅ Generated: 3 letters
📊 Average ProposalBio™ Score: 76.8/100
```

**Then check Airtable:**
- Go to **Officer Outreach Tracking** table
- See new records
- Open "✉️ Ready to Send" view
- Review letters

---

## 📊 OPTIONAL: ENHANCED SETUP

### Add Formulas (Optional but useful):

**Follow-up Date Field:**
- Change to Formula type
- Formula: `DATEADD({Date Sent}, 10, 'days')`
- Auto-calculates follow-up date

**Days Since Sent:**
- Field Type: Formula
- Formula: `DATETIME_DIFF(TODAY(), {Date Sent}, 'days')`
- Shows how long since sent

**Response Time:**
- Field Type: Formula  
- Formula: `DATETIME_DIFF({Response Date}, {Date Sent}, 'days')`
- Shows how fast they responded

---

## 🎯 WHAT IF I DON'T HAVE OPPORTUNITIES TABLE?

If you don't have an **Opportunities** table yet:

### Quick Create:

1. Create **Opportunities** table
2. Add minimum fields:
   - Title (Single line text)
   - Status (Single select: Active, Closed, Inactive)
   - Solicitation Number (Single line text)
   - Agency (Single line text)
   - Point of Contact (Single line text)
   - Contact Email (Email)
   - Response Deadline (Date)
   - Description (Long text)

3. Add one test record:
   - Title: "Female Condoms"
   - Status: "Closed"
   - Solicitation Number: "766-26-1-400-0182"
   - Agency: "VA Medical Center - 766 Ladson"
   - Point of Contact: "Jennifer Coleman"
   - Contact Email: "jennifer.coleman4@va.gov"

4. Run the system to test!

---

## 💡 PRO TIPS

### For Best Results:

**1. Always include officer contact info in Opportunities:**
- Point of Contact (name)
- Contact Email (required!)
- Without email, system skips the opportunity

**2. Mark opportunities as "Closed" when appropriate:**
- System only processes closed opportunities
- Prevents duplicate outreach

**3. Use Tags for organization:**
- Tag by agency type (VA, DoD, etc.)
- Tag by product/service type
- Makes filtering easier

**4. Review before sending:**
- Check "✉️ Ready to Send" view daily
- Quality check letters
- Customize if needed
- Then send!

**5. Track everything:**
- Mark "Date Sent" when you send
- Note "Response Received" immediately  
- Add to "Response Notes"
- Check "Added to Vendor List" when confirmed

---

## 🔄 WORKFLOW AFTER SETUP

### Daily Routine (5 minutes):

1. **Morning:** Run officer outreach system
   ```bash
   python3 contracting_officer_outreach.py
   ```

2. **Review:** Check "✉️ Ready to Send" view
   - See new letters generated
   - Review quality scores
   - Customize if needed

3. **Send:** Send 2-5 letters per day
   - Copy letter to email
   - Send to officer
   - Mark "Date Sent" in Airtable
   - Change Status to "Sent"

4. **Follow-up:** Check "⏰ Follow-up Needed" view
   - Send follow-ups after 10 days
   - Track responses

5. **Celebrate:** When they respond!
   - Check "Response Received"
   - Add notes
   - Check "Added to Vendor List" if confirmed

---

## 📸 VISUAL REFERENCE

### What Your Airtable Should Look Like:

**Officer Outreach Tracking Table:**
```
┌──────────────┬─────────────────┬──────────────┬──────────┬─────────┐
│ Officer Name │ Officer Email   │ Opportunity  │ Status   │ Score   │
├──────────────┼─────────────────┼──────────────┼──────────┼─────────┤
│ Jennifer     │ jennifer.col... │ Female Con...│ Draft    │ 78.3    │
│ Coleman      │                 │              │          │         │
├──────────────┼─────────────────┼──────────────┼──────────┼─────────┤
│ John Smith   │ john.smith@...  │ Road Salt    │ Sent     │ 82.1    │
├──────────────┼─────────────────┼──────────────┼──────────┼─────────┤
│ Mary Jones   │ mary.jones@...  │ Wipers       │ Responded│ 85.5    │
└──────────────┴─────────────────┴──────────────┴──────────┴─────────┘
```

**Opportunities Table (with new fields):**
```
┌──────────────┬──────────┬────────────────────┬──────────────────┐
│ Title        │ Status   │ Officer Outreach   │ Outreach Link    │
│              │          │ Sent?              │                  │
├──────────────┼──────────┼────────────────────┼──────────────────┤
│ Female       │ Closed   │ ✓                  │ → Jennifer Col...│
│ Condoms      │          │                    │                  │
├──────────────┼──────────┼────────────────────┼──────────────────┤
│ Road Salt    │ Closed   │ ✓                  │ → John Smith     │
├──────────────┼──────────┼────────────────────┼──────────────────┤
│ Wipers       │ Active   │                    │                  │
└──────────────┴──────────┴────────────────────┴──────────────────┘
```

---

## ⏱️ SETUP TIME

**Realistically:**
- Create table: 2 minutes
- Add fields: 5 minutes
- Create views: 2 minutes
- Test: 1 minute
**Total: 10 minutes**

---

## 🆘 TROUBLESHOOTING

### "System can't find Officer Outreach Tracking table"

**Fix:** Make sure table name is EXACTLY:
```
Officer Outreach Tracking
```
(Capital letters, spaces, no typos)

### "No opportunities found"

**Check:**
1. Do you have opportunities with Status = "Closed"?
2. Do they have officer contact email?
3. Is "Officer Outreach Sent" field unchecked?

### "Records not creating"

**Check:**
1. Airtable API key in .env file
2. Airtable Base ID correct
3. Field names match exactly

---

## ✅ YOU'RE READY!

Once Airtable is set up:

1. ✅ Run: `python3 contracting_officer_outreach.py`
2. ✅ Check Airtable for new letters
3. ✅ Review in "Ready to Send" view
4. ✅ Send to officers
5. ✅ Build relationships
6. ✅ Win more contracts!

---

**Setup Time:** 10 minutes  
**Maintenance:** 5 minutes daily  
**ROI:** 2-3x more contract opportunities  
**Status:** Ready when you are! 🚀
