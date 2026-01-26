# 📇 NEXUS CONTACTS - COMPREHENSIVE SCHEMA

**Universal Contact Management for All Business Relationships**  
**DEE DAVIS INC - Government Contracting**

**Created:** January 23, 2026  
**Status:** Ready to implement

---

## 🎯 PURPOSE

**Centralized contact database for:**
- 🏛️ **Procurement Officers** - Government buyers and contracting officers
- 🏭 **Suppliers** - Product manufacturers and wholesalers
- 👷 **Subcontractors** - Service providers and subs
- 🤝 **Partners** - Strategic partners and consultants
- 📊 **Prospects** - Potential clients
- 📋 **Everyone** - All business contacts in one place

---

## 📊 AIRTABLE TABLE SETUP

### **Table Name:** `NEXUS CONTACTS`

**Why Universal?**
- One contact database for all systems (GPSS, ATLAS, DDCSS, LBPC)
- Eliminates duplicate contacts across tables
- Links to opportunities, projects, quotes, orders
- Complete relationship history in one place

---

## 📝 FIELD STRUCTURE (30 FIELDS)

### **BASIC INFORMATION (Required)**

| # | Field Name | Field Type | Description | Required? |
|---|-----------|------------|-------------|-----------|
| 1 | **CONTACT NAME** | Single line text | Full name (First Last) | ✅ YES |
| 2 | **EMAIL** | Email | Primary email address | ✅ YES |
| 3 | **PHONE** | Phone number | Primary phone number | No |
| 4 | **CONTACT TYPE** | Single select | Procurement Officer, Supplier, Subcontractor, Partner, Prospect, Other | ✅ YES |

**Contact Type Options:**
- `Procurement Officer` - Government buyers
- `Supplier` - Product vendors
- `Subcontractor` - Service providers
- `Partner` - Strategic partners
- `Prospect` - Potential clients
- `Other` - Misc contacts

---

### **ORGANIZATION (8 fields)**

| # | Field Name | Field Type | Description |
|---|-----------|------------|-------------|
| 5 | **ORGANIZATION** | Single line text | Company/agency name |
| 6 | **TITLE** | Single line text | Job title/position |
| 7 | **DEPARTMENT** | Single line text | Department or division |
| 8 | **ORG TYPE** | Single select | Government, Private Company, Non-Profit, Academic, Other |
| 9 | **AGENCY LEVEL** | Single select | Federal, State, County, City, Private (for gov contacts) |
| 10 | **LOCATION** | Single line text | City, State |
| 11 | **ADDRESS** | Long text | Full street address |
| 12 | **WEBSITE** | URL | Organization website |

**Org Type Options:**
- `Government` - Federal/state/local agencies
- `Private Company` - For-profit businesses
- `Non-Profit` - Non-profit organizations
- `Academic` - Universities/schools
- `Other` - Other types

**Agency Level Options:**
- `Federal` - VA, DoD, DOE, etc.
- `State` - State agencies
- `County` - County governments
- `City` - Municipal governments
- `Private` - Not government

---

### **CONTACT DETAILS (5 fields)**

| # | Field Name | Field Type | Description |
|---|-----------|------------|-------------|
| 13 | **ALT EMAIL** | Email | Secondary email |
| 14 | **ALT PHONE** | Phone number | Secondary phone |
| 15 | **FAX** | Phone number | Fax number (for old-school agencies) |
| 16 | **MOBILE** | Phone number | Mobile phone |
| 17 | **DIRECT LINE** | Phone number | Direct office line |

---

### **RELATIONSHIP TRACKING (8 fields)**

| # | Field Name | Field Type | Description |
|---|-----------|------------|-------------|
| 18 | **RELATIONSHIP STAGE** | Single select | New, Contacted, Engaged, Active, Inactive |
| 19 | **SOURCE** | Single select | RFP/RFQ, Networking, Referral, Web Search, Cold Outreach, Other |
| 20 | **FIRST CONTACT DATE** | Date | When we first made contact |
| 21 | **LAST CONTACT DATE** | Date | Most recent interaction |
| 22 | **NEXT FOLLOW-UP** | Date | When to follow up next |
| 23 | **TAGS** | Multiple select | Custom tags (VA, DoD, Local, Emergency, etc.) |
| 24 | **NOTES** | Long text | General notes and history |
| 25 | **PRIORITY** | Single select | High, Medium, Low |

**Relationship Stage Options:**
- `New` - Just discovered
- `Contacted` - Initial outreach sent
- `Engaged` - Active conversation
- `Active` - Ongoing relationship
- `Inactive` - Past contact

**Source Options:**
- `RFP/RFQ` - Found in solicitation
- `Networking` - Met at event
- `Referral` - Referred by someone
- `Web Search` - Found online
- `Cold Outreach` - Proactive search
- `Other` - Other sources

**Priority Options:**
- `High` - Top priority contact
- `Medium` - Standard priority
- `Low` - Low priority

**Tags (Multiple Select):**
- `VA` - Veterans Affairs
- `DoD` - Department of Defense
- `DOE` - Department of Energy
- `State Gov` - State government
- `County Gov` - County government
- `City Gov` - Municipal government
- `Local` - Local to Michigan
- `Out of State` - Outside Michigan
- `Medical Supplies` - Medical/healthcare
- `Construction` - Construction services
- `Office Supplies` - Office products
- `IT Services` - Technology
- `Professional Services` - Consulting
- `Emergency Equipment` - Emergency/safety
- `Facilities` - Facilities management
- `Janitorial` - Cleaning services
- `Landscape` - Landscaping
- `Transportation` - Vehicles/logistics
- `Food Services` - Food/catering
- `Diversity Certified` - MBE/WBE/etc.
- `GSA Schedule` - Has GSA contract
- `Small Business` - Small business
- `Large Enterprise` - Large company
- Add more as needed

---

### **LINKED RECORDS (5 fields)**

| # | Field Name | Field Type | Description |
|---|-----------|------------|-------------|
| 26 | **RELATED OPPORTUNITIES** | Link to another record | Link to: Opportunities |
| 27 | **RELATED ORDERS** | Link to another record | Link to: GPSS Supplier Orders |
| 28 | **RELATED QUOTES** | Link to another record | Link to: GPSS Supplier Quotes |
| 29 | **RELATED PROJECTS** | Link to another record | Link to: ATLAS Projects |
| 30 | **OFFICER OUTREACH** | Link to another record | Link to: Officer Outreach Tracking |

---

### **METADATA (4 fields - Auto)**

| # | Field Name | Field Type | Description |
|---|-----------|------------|-------------|
| 31 | **RECORD ID** | Autonumber | Unique record ID |
| 32 | **CREATED DATE** | Created time | When record was created |
| 33 | **LAST MODIFIED** | Last modified time | When record was updated |
| 34 | **ADDED BY** | Single line text | Who added (default: "NEXUS AI") |

---

## 🎨 VIEWS TO CREATE

### **View 1: 🏛️ Procurement Officers**
**Filter:** Contact Type = "Procurement Officer"  
**Sort:** Last Contact Date (newest first)  
**Purpose:** All government buyers and contracting officers

**Fields to Show:**
- Contact Name
- Email
- Organization
- Title
- Agency Level
- Last Contact Date
- Next Follow-up
- Priority
- Tags

---

### **View 2: 🏭 Suppliers**
**Filter:** Contact Type = "Supplier"  
**Sort:** Organization  
**Purpose:** All product vendors and manufacturers

**Fields to Show:**
- Contact Name
- Organization
- Email
- Phone
- Tags (product categories)
- Relationship Stage
- Last Contact Date
- Notes

---

### **View 3: 👷 Subcontractors**
**Filter:** Contact Type = "Subcontractor"  
**Sort:** Organization  
**Purpose:** All service providers and subs

**Fields to Show:**
- Contact Name
- Organization
- Email
- Phone
- Tags (service types)
- Location
- Relationship Stage
- Last Contact Date

---

### **View 4: ⏰ Follow-up Needed**
**Filter:** 
- Next Follow-up ≤ Today
- Relationship Stage ≠ "Inactive"

**Sort:** Next Follow-up (oldest first)  
**Purpose:** Contacts that need follow-up

---

### **View 5: 🔥 High Priority**
**Filter:** Priority = "High"  
**Sort:** Next Follow-up  
**Purpose:** VIP contacts

---

### **View 6: 📍 Local Contacts (Michigan)**
**Filter:** Tags contains "Local"  
**Sort:** Organization  
**Purpose:** Michigan-based contacts

---

### **View 7: 🆕 New Contacts (This Month)**
**Filter:** Created Date ≥ First day of this month  
**Sort:** Created Date (newest first)  
**Purpose:** Recently added contacts

---

### **View 8: 📊 By Organization**
**Group By:** Organization  
**Sort:** Contact Name  
**Purpose:** See all contacts at each organization

---

### **View 9: 🏷️ By Contact Type**
**Group By:** Contact Type  
**Sort:** Organization  
**Purpose:** Organized by role

---

## 🔗 INTEGRATION WITH EXISTING SYSTEMS

### **Replaces/Consolidates:**

**Current separate contact tables:**
- `GPSS CONTACTS` → Migrate to `NEXUS CONTACTS`
- Officer Outreach contacts → Auto-link to `NEXUS CONTACTS`
- Supplier contacts (in supplier tables) → Link to `NEXUS CONTACTS`

**Benefits:**
- ✅ One source of truth
- ✅ No duplicate contacts
- ✅ Complete relationship history
- ✅ Cross-system visibility

---

## 🚀 MIGRATION PLAN

### **Phase 1: Create New Table**
1. Create `NEXUS CONTACTS` table with all 34 fields
2. Set up 9 views
3. Don't delete old tables yet

### **Phase 2: Import Existing Contacts**
1. Export contacts from `GPSS CONTACTS`
2. Import to `NEXUS CONTACTS` (set Type = "Procurement Officer")
3. Import supplier contacts (set Type = "Supplier")
4. Import subcontractor contacts (set Type = "Subcontractor")

### **Phase 3: Link to Existing Records**
1. Update `Opportunities` table to link to `NEXUS CONTACTS`
2. Update `GPSS Supplier Orders` to link to `NEXUS CONTACTS`
3. Update `Officer Outreach Tracking` to link to `NEXUS CONTACTS`

### **Phase 4: Update Backend Code**
1. Update `nexus_backend.py` to use `NEXUS CONTACTS`
2. Update `contracting_officer_outreach.py` to use `NEXUS CONTACTS`
3. Update supplier scripts to use `NEXUS CONTACTS`

### **Phase 5: Retire Old Tables (Later)**
1. Once everything works, can delete `GPSS CONTACTS`
2. Keep one universal contact table

---

## 📝 PYTHON INTEGRATION

### **Add Contact Function:**

```python
def add_contact_to_nexus(
    name: str,
    email: str,
    contact_type: str,
    organization: str = None,
    title: str = None,
    phone: str = None,
    location: str = None,
    source: str = "RFP/RFQ",
    tags: List[str] = None,
    notes: str = None,
    priority: str = "Medium"
):
    """Add contact to NEXUS CONTACTS table"""
    
    # Check for duplicates
    formula = f"{{EMAIL}} = '{email}'"
    existing = airtable.search_records('NEXUS CONTACTS', formula)
    
    if existing:
        print(f"⚠️ Contact already exists: {name} ({email})")
        return existing[0]['id']
    
    # Prepare fields
    fields = {
        'CONTACT NAME': name,
        'EMAIL': email,
        'CONTACT TYPE': contact_type,
        'FIRST CONTACT DATE': datetime.now().strftime('%Y-%m-%d'),
        'ADDED BY': 'NEXUS AI',
        'RELATIONSHIP STAGE': 'New',
        'SOURCE': source,
        'PRIORITY': priority
    }
    
    # Add optional fields
    if organization:
        fields['ORGANIZATION'] = organization
    if title:
        fields['TITLE'] = title
    if phone:
        fields['PHONE'] = phone
    if location:
        fields['LOCATION'] = location
    if tags:
        fields['TAGS'] = tags
    if notes:
        fields['NOTES'] = notes
    
    # Create record
    record = airtable.create_record('NEXUS CONTACTS', fields)
    print(f"✅ Added contact: {name} ({contact_type})")
    
    return record['id']
```

---

## 🔄 AUTO-EXTRACT CONTACTS FROM RFPs

**When reviewing RFPs, automatically extract:**

1. **Procurement Officer**
   - Name
   - Email
   - Phone
   - Agency
   - Title
   - Location

2. **Add to NEXUS CONTACTS**
   - Type = "Procurement Officer"
   - Source = "RFP/RFQ"
   - Tags = agency type
   - Link to Opportunity

3. **Available for Officer Outreach**
   - Automatically linkable
   - Track relationship
   - Follow-up reminders

---

## 📋 EXAMPLE RECORDS

### **Example 1: Procurement Officer**

```
CONTACT NAME: Mark Rozinsky
EMAIL: mrozinsky@dearborn.gov
PHONE: (313) 943-2375
CONTACT TYPE: Procurement Officer
ORGANIZATION: City of Dearborn
TITLE: Purchasing Manager
DEPARTMENT: Purchasing Division
ORG TYPE: Government
AGENCY LEVEL: City
LOCATION: Dearborn, Michigan
RELATIONSHIP STAGE: New
SOURCE: RFP/RFQ
FIRST CONTACT DATE: 2026-01-23
TAGS: City Gov, Local, Emergency Equipment
PRIORITY: High
NOTES: Contact for emergency generator vendor list. Phase 2 opportunity estimated $120K-$180K.
```

---

### **Example 2: Supplier**

```
CONTACT NAME: Sales Team
EMAIL: sales@generac.com
PHONE: (888) 436-3722
CONTACT TYPE: Supplier
ORGANIZATION: Generac Power Systems
ORG TYPE: Private Company
LOCATION: Waukesha, Wisconsin
WEBSITE: https://www.generac.com
RELATIONSHIP STAGE: New
SOURCE: Web Search
FIRST CONTACT DATE: 2026-01-23
TAGS: Emergency Equipment, GSA Schedule, Large Enterprise
PRIORITY: High
NOTES: GSA contract holder for emergency generators. Need to establish account for government pricing.
```

---

### **Example 3: Subcontractor**

```
CONTACT NAME: Owner
EMAIL: cutkinglawncare@gmail.com
PHONE: (586) 555-1234
CONTACT TYPE: Subcontractor
ORGANIZATION: Cut King Lawn Care
ORG TYPE: Private Company
LOCATION: Madison Heights, Michigan
RELATIONSHIP STAGE: Contacted
SOURCE: Web Search
FIRST CONTACT DATE: 2026-01-22
TAGS: Landscape, Local, Small Business
PRIORITY: Medium
NOTES: Subcontractor for Madison Heights Senior Lawn Services bid. Requested quote for $40-45/cut.
```

---

## ✅ SETUP CHECKLIST

**To implement NEXUS CONTACTS:**

- [ ] Create `NEXUS CONTACTS` table in Airtable
- [ ] Add all 34 fields (Basic, Organization, Contact Details, Relationship, Links, Metadata)
- [ ] Set up Single Select options (Contact Type, Org Type, Agency Level, etc.)
- [ ] Add Multiple Select tags (20+ options)
- [ ] Create 9 views (Procurement Officers, Suppliers, Subcontractors, etc.)
- [ ] Test with 3-5 sample contacts
- [ ] Import existing procurement officers from `PROCUREMENT_OFFICERS_LIST.md`
- [ ] Import existing suppliers from `VENDOR_CLIENT_CONTACTS.md`
- [ ] Create Python script to add contacts from markdown files
- [ ] Update backend to use `NEXUS CONTACTS` for new RFP reviews
- [ ] Link to existing Opportunities, Orders, Outreach records

---

## 🎯 WORKFLOW: EVERY RFP REVIEW

**When reviewing any RFP/solicitation:**

1. **Extract procurement officer info**
   ```python
   add_contact_to_nexus(
       name="Mark Rozinsky",
       email="mrozinsky@dearborn.gov",
       contact_type="Procurement Officer",
       organization="City of Dearborn",
       title="Purchasing Manager",
       phone="(313) 943-2375",
       location="Dearborn, Michigan",
       source="RFP/RFQ",
       tags=["City Gov", "Local", "Emergency Equipment"],
       priority="High",
       notes="Contact for generator vendor list. Phase 2 opportunity."
   )
   ```

2. **Link to opportunity**
   - Create opportunity in Opportunities table
   - Link contact to opportunity

3. **Available for outreach**
   - When opportunity closes
   - Auto-generate officer outreach letter
   - Link to NEXUS CONTACTS

---

## 💡 PRO TIPS

### **For Procurement Officers:**
- ✅ Always capture email (required for outreach)
- ✅ Tag by agency type (VA, DoD, City, etc.)
- ✅ Set priority (High for big opportunities)
- ✅ Add notes about projects and opportunities
- ✅ Set follow-up dates

### **For Suppliers:**
- ✅ Tag by product category
- ✅ Note if they have GSA schedule
- ✅ Track pricing and lead times in notes
- ✅ Link to quotes and orders

### **For Subcontractors:**
- ✅ Tag by service type (Landscape, Construction, etc.)
- ✅ Note if they're local (Michigan)
- ✅ Track certifications (MBE/WBE)
- ✅ Link to opportunities they bid on

### **Universal:**
- ✅ One contact = one record (no duplicates)
- ✅ Complete relationship history
- ✅ Regular follow-ups
- ✅ Keep notes updated

---

## 📊 METRICS TO TRACK

**Contact Database Health:**
- Total contacts by type
- New contacts this month
- Follow-ups completed
- Response rate (for outreach)
- Active relationships
- Contacts by location
- Contacts by priority

**Procurement Officers:**
- Total government buyers
- By agency level (Federal, State, County, City)
- Outreach sent vs responded
- Opportunities per officer
- Win rate by officer relationship

**Suppliers:**
- Total suppliers by category
- Quotes requested
- Orders placed
- Supplier performance
- Pricing competitiveness

**Subcontractors:**
- Total subs by service type
- Local vs out-of-state
- Quotes requested
- Work performed
- Quality ratings

---

## 🚀 READY TO IMPLEMENT?

**Next Steps:**

1. **Create table** (20 minutes)
2. **Import existing contacts** (30 minutes)
3. **Create Python script** (30 minutes)
4. **Update backend** (1 hour)
5. **Test with new RFP** (10 minutes)

**Total Setup Time:** ~2.5 hours

**Ongoing:** Every RFP review auto-captures contacts

---

## 📞 SUPPORT

**Questions?**
- See: `NEXUS_ALL_AIRTABLE_TABLES_MASTER_LIST.md`
- Contact management best practices: This document
- Python integration: See script in `/Users/deedavis/NEXUS BACKEND/add_contacts_to_nexus.py` (to be created)

---

**Status:** Ready to implement  
**Priority:** High (needed for every RFP review)  
**Impact:** Complete contact management and relationship tracking

**Let's build your universal contact database!** 🎯
