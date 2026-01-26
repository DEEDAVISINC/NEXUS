# 🚀 NEXUS CONTACTS - QUICK START GUIDE

**Universal Contact Management for All Business Relationships**  
**Setup Time:** 30 minutes  
**Created:** January 23, 2026

---

## 🎯 WHAT THIS DOES

**Automatically capture and track ALL contacts:**
- 🏛️ **Procurement Officers** from every RFP/RFQ
- 🏭 **Suppliers** for products
- 👷 **Subcontractors** for services
- 🤝 **Partners** and prospects
- 📋 **Everyone** in one place

**Benefits:**
- ✅ Never lose contact information
- ✅ Complete relationship history
- ✅ Auto-link to opportunities and orders
- ✅ Follow-up reminders
- ✅ One source of truth

---

## ⏱️ QUICK SETUP (30 MINUTES)

### **STEP 1: Create Airtable Table (10 minutes)**

1. Open your NEXUS Airtable base
2. Create new table: `NEXUS CONTACTS`
3. Follow field guide: `NEXUS_CONTACTS_COMPREHENSIVE_SCHEMA.md`

**Quick Field List (34 fields):**

**Required (4):**
- CONTACT NAME (Single line text)
- EMAIL (Email)
- PHONE (Phone)
- CONTACT TYPE (Single select: Procurement Officer, Supplier, Subcontractor, Partner, Prospect, Other)

**Organization (8):**
- ORGANIZATION
- TITLE
- DEPARTMENT
- ORG TYPE
- AGENCY LEVEL
- LOCATION
- ADDRESS
- WEBSITE

**Contact Details (5):**
- ALT EMAIL
- ALT PHONE
- FAX
- MOBILE
- DIRECT LINE

**Relationship (8):**
- RELATIONSHIP STAGE
- SOURCE
- FIRST CONTACT DATE
- LAST CONTACT DATE
- NEXT FOLLOW-UP
- TAGS (Multiple select)
- NOTES
- PRIORITY

**Links (5):**
- RELATED OPPORTUNITIES
- RELATED ORDERS
- RELATED QUOTES
- RELATED PROJECTS
- OFFICER OUTREACH

**Metadata (4):**
- RECORD ID (Autonumber)
- CREATED DATE (Created time)
- LAST MODIFIED (Last modified time)
- ADDED BY (Single line text)

---

### **STEP 2: Create Views (5 minutes)**

**Create these 9 views:**

1. **🏛️ Procurement Officers**
   - Filter: Contact Type = "Procurement Officer"
   - Sort: Last Contact Date (newest first)

2. **🏭 Suppliers**
   - Filter: Contact Type = "Supplier"
   - Sort: Organization

3. **👷 Subcontractors**
   - Filter: Contact Type = "Subcontractor"
   - Sort: Organization

4. **⏰ Follow-up Needed**
   - Filter: Next Follow-up ≤ Today
   - Sort: Next Follow-up (oldest first)

5. **🔥 High Priority**
   - Filter: Priority = "High"

6. **📍 Local Contacts (Michigan)**
   - Filter: Tags contains "Local"

7. **🆕 New This Month**
   - Filter: Created Date ≥ first day of month

8. **📊 By Organization**
   - Group by: Organization

9. **🏷️ By Contact Type**
   - Group by: Contact Type

---

### **STEP 3: Import Existing Contacts (10 minutes)**

Run the import script:

```bash
python3 add_contacts_to_nexus.py
```

**What it imports:**
- ✅ 6 procurement officers from `PROCUREMENT_OFFICERS_LIST.md`
- ✅ 7 suppliers and subcontractors from `VENDOR_CLIENT_CONTACTS.md`
- ✅ 13 total contacts to start

**Expected output:**
```
🚀 NEXUS CONTACTS IMPORTER

📋 IMPORTING PROCUREMENT OFFICERS
✅ ADDED: Mark Rozinsky (City of Dearborn) - Procurement Officer
✅ ADDED: Tina Marie Kern (CPS Energy) - Procurement Officer
✅ ADDED: Joan E. Daniels (Oakland County) - Procurement Officer
... (6 total)

🏭 IMPORTING SUPPLIERS & SUBCONTRACTORS
✅ ADDED: GSA Sales Team (Generac Power Systems) - Supplier
✅ ADDED: Government Sales (Grainger) - Supplier
✅ ADDED: Owner (Cut King Lawn Care) - Subcontractor
... (7 total)

📊 IMPORT SUMMARY
✅ Added:   13 new contacts
🔄 Updated: 0 existing contacts
⏩ Skipped: 0 contacts
📋 Total:   13 contacts in NEXUS
```

---

### **STEP 4: Verify (5 minutes)**

1. Open NEXUS CONTACTS table in Airtable
2. Check "🏛️ Procurement Officers" view → See 6 officers
3. Check "🏭 Suppliers" view → See suppliers
4. Check "👷 Subcontractors" view → See subs
5. Open a contact → Verify all fields populated

**You should see:**
- Mark Rozinsky (Dearborn)
- Tina Kern (CPS Energy)
- Joan Daniels (Oakland County)
- Madison Heights City Clerk
- Warren DDA Purchasing
- Jackson County Purchasing
- Generac, Kohler, IMP Corp
- Grainger, Detroit Salt, Mopec
- Cut King Lawn Care

---

## 🔄 DAILY WORKFLOW: EVERY RFP REVIEW

**When you review ANY RFP/solicitation, automatically capture contact:**

### **Example: Reviewing CPS Energy RFQ**

**1. Extract procurement officer info:**
```python
# This will be automatic in future versions
add_contact_to_nexus(
    name="Tina Marie Kern",
    email="tkern@cpsenergy.com",
    contact_type="Procurement Officer",
    organization="CPS Energy",
    title="Buyer",
    phone="210-935-5988",
    location="San Antonio, TX",
    source="RFP/RFQ",
    tags=["City Gov", "Out of State", "Office Supplies"],
    priority="High",
    notes="RFQ 7000205103 - Industrial Wipers. Bid due Jan 31, 2026."
)
```

**2. Automatically added to NEXUS CONTACTS**
- ✅ Saved with all details
- ✅ Tagged appropriately
- ✅ Priority set
- ✅ Ready for follow-up

**3. Link to opportunity**
- Create opportunity in Opportunities table
- Link to Tina's contact record
- Complete relationship history

**4. After bid closes**
- Automatically generate officer outreach letter
- Track in Officer Outreach Tracking
- Link back to contact

---

## 📋 CONTACT TYPES & WHEN TO USE

### **🏛️ Procurement Officer**
**Use for:** Government buyers, contracting officers, purchasing managers

**Examples:**
- Mark Rozinsky (City of Dearborn)
- Tina Kern (CPS Energy)
- Joan Daniels (Oakland County)

**Tag with:** Agency type (VA, DoD, City Gov, County Gov, etc.)

---

### **🏭 Supplier**
**Use for:** Product vendors, manufacturers, wholesalers

**Examples:**
- Generac (Generators)
- Grainger (Industrial supplies)
- Detroit Salt (Road salt)
- Mopec (Medical supplies)

**Tag with:** Product category (Emergency Equipment, Office Supplies, Construction, Medical Supplies)

---

### **👷 Subcontractor**
**Use for:** Service providers, subs, contractors

**Examples:**
- Cut King Lawn Care (Landscaping)
- Excel Landscaping (Municipal landscaping)
- Ley's Lawn Care (Lawn services)

**Tag with:** Service type (Landscape, Construction, IT Services, Professional Services)

---

### **🤝 Partner**
**Use for:** Strategic partners, consultants, advisors

**Examples:**
- Business development partners
- Technical consultants
- Legal/compliance advisors

---

### **📊 Prospect**
**Use for:** Potential clients (for DDCSS corporate sales)

**Examples:**
- Corporate prospects
- Consulting leads
- Training opportunities

---

## 🎯 BEST PRACTICES

### **Always Capture:**
1. ✅ **Name** - Full name (First Last)
2. ✅ **Email** - REQUIRED for follow-up
3. ✅ **Organization** - Company/agency
4. ✅ **Contact Type** - Procurement Officer, Supplier, Subcontractor, etc.
5. ✅ **Tags** - For filtering and organization
6. ✅ **Notes** - Project details, opportunities, quotes

### **For Procurement Officers:**
- ✅ Always include project/RFP details in notes
- ✅ Tag by agency type (VA, DoD, City, County, etc.)
- ✅ Set priority (High for big opportunities)
- ✅ Note bid deadlines and outcomes
- ✅ Set follow-up dates

### **For Suppliers:**
- ✅ Tag by product category
- ✅ Note if GSA schedule holder
- ✅ Track pricing and lead times
- ✅ Link to quotes and orders
- ✅ Note account numbers

### **For Subcontractors:**
- ✅ Tag by service type
- ✅ Note if local (Michigan)
- ✅ Track certifications (MBE/WBE)
- ✅ Note insurance and bonding
- ✅ Link to bids and projects

---

## 🔗 INTEGRATION WITH OTHER SYSTEMS

### **Opportunities Table**
```
Opportunity: CPS Energy Industrial Wipers
  ↓ Links to
Contact: Tina Kern (Procurement Officer)
  ↓ Shows
- All opportunities with Tina
- Email history
- Officer outreach status
```

### **GPSS Supplier Orders**
```
Order: Generac Generator Purchase
  ↓ Links to
Contact: GSA Sales Team (Generac)
  ↓ Shows
- All orders from Generac
- Pricing history
- Lead times
```

### **Officer Outreach Tracking**
```
Officer Outreach: Female Condoms Follow-up
  ↓ Links to
Contact: Jennifer Coleman (VA)
  ↓ Shows
- Outreach history
- Response tracking
- Relationship status
```

---

## 📊 REPORTS & METRICS

### **Contact Database Health**
- Total contacts by type
- New contacts this week/month
- Follow-ups due today
- High priority contacts
- Active relationships

### **Procurement Officers**
- Total by agency level (Federal, State, County, City)
- Outreach sent vs responded
- Opportunities per officer
- Win rate by relationship

### **Suppliers**
- Total by category
- Quotes requested
- Orders placed
- Average response time
- Pricing trends

### **Subcontractors**
- Total by service type
- Local vs out-of-state
- Certified vs non-certified
- Work performed
- Quality ratings

---

## 🚨 COMMON ISSUES

### **"Contact already exists"**
✅ **Good!** System prevents duplicates  
→ Existing contact will be updated with new info

### **"No email provided"**
⚠️ **Required:** Email is required for all contacts  
→ Add email or contact will be skipped

### **"Field not found"**
❌ **Check:** Field names in Airtable must match exactly  
→ See: `NEXUS_CONTACTS_COMPREHENSIVE_SCHEMA.md` for correct names

### **"Table not found"**
❌ **Check:** Table must be named exactly `NEXUS CONTACTS`  
→ Case-sensitive, check spelling

---

## 🎉 YOU'RE READY!

**Your NEXUS CONTACTS system is set up!**

### **What You Can Do Now:**

1. ✅ **View all contacts** in Airtable by type
2. ✅ **Add new contacts** from RFPs automatically
3. ✅ **Track relationships** with notes and follow-ups
4. ✅ **Link to opportunities** and orders
5. ✅ **Generate officer outreach** for closed bids
6. ✅ **Manage suppliers** and subcontractors
7. ✅ **Never lose contact info** again

---

## 📚 REFERENCE DOCUMENTS

**Full Documentation:**
- `NEXUS_CONTACTS_COMPREHENSIVE_SCHEMA.md` - Complete field guide
- `PROCUREMENT_OFFICERS_LIST.md` - Government buyers
- `VENDOR_CLIENT_CONTACTS.md` - Suppliers and subs
- `add_contacts_to_nexus.py` - Import script

**Related Systems:**
- `AIRTABLE_SETUP_OFFICER_OUTREACH.md` - Officer outreach integration
- `NEXUS_ALL_AIRTABLE_TABLES_MASTER_LIST.md` - All NEXUS tables

---

## 🔮 FUTURE ENHANCEMENTS

**Planned features:**
- 🤖 Auto-extract contacts from PDF RFPs
- 📧 Email integration for automatic logging
- 📞 Call tracking
- 📅 Calendar integration for follow-ups
- 📊 Advanced analytics and reporting
- 🔗 Integration with LinkedIn
- 💌 Bulk email campaigns
- 🎯 Lead scoring

---

## 💡 PRO TIPS

### **1. Use Tags Liberally**
Tag contacts with multiple categories for easy filtering:
- Agency type (VA, DoD, City, County)
- Product/service type
- Location (Local, Out of State)
- Business size (Small Business, Large Enterprise)
- Special status (GSA Schedule, Diversity Certified)

### **2. Set Follow-up Dates**
Always set "Next Follow-up" date when:
- Requesting quotes
- Sending outreach letters
- After initial contact
- For inactive relationships

### **3. Update Last Contact Date**
Manually update "Last Contact Date" after:
- Phone calls
- Email exchanges
- Meetings
- Any interaction

### **4. Detailed Notes**
Include in notes:
- Project/opportunity details
- Quote amounts and deadlines
- Conversation highlights
- Next steps
- Account numbers
- Special requirements

### **5. Regular Reviews**
Weekly tasks:
- Check "⏰ Follow-up Needed" view
- Update relationship stages
- Add notes for recent interactions
- Set new follow-up dates

---

## ✅ SUCCESS CHECKLIST

**After setup, you should have:**

- [ ] NEXUS CONTACTS table created with 34 fields
- [ ] 9 views created and working
- [ ] 13+ contacts imported successfully
- [ ] Procurement officers visible in their view
- [ ] Suppliers visible in their view
- [ ] Subcontractors visible in their view
- [ ] Follow-up dates set for high-priority contacts
- [ ] Tags configured for your business
- [ ] Links to opportunities working (if applicable)
- [ ] Officer outreach integration (if using)

---

## 🚀 NEXT STEPS

**Start using NEXUS CONTACTS today:**

1. **Add new contacts** as you review RFPs
2. **Set follow-up dates** for active relationships
3. **Track interactions** in notes
4. **Link to opportunities** for complete history
5. **Use views** to organize and prioritize
6. **Review weekly** for follow-ups

**You now have a professional contact management system!** 🎯

---

**Questions? Check the comprehensive schema or modify the system to fit your needs!**

**Setup Time:** 30 minutes  
**Maintenance:** 5 minutes daily  
**ROI:** Never lose a contact again  
**Status:** Ready to use! 🚀
