# COMPLETE VENDOR & SUBCONTRACTOR DATABASE SYSTEM
**Two Separate Systems, One Platform**

**Created:** February 8, 2026  
**Purpose:** Differentiate product suppliers (vendors) from service providers (subs)  
**Integration:** Works with Grainger Script (products) + Service Sub Framework (services)

---

## 🎯 THE CRITICAL DISTINCTION

### **VENDORS (Product Suppliers)**
- **What they provide:** PRODUCTS/MATERIALS/SUPPLIES
- **Examples:** Grainger, MOPEC, Morton Salt, Zoro, Fastenal
- **Your role:** Value-Added Reseller (VAR) - Mark up and resell
- **Framework:** Grainger Call Script (negotiate pricing)
- **Database:** VENDOR DATABASE

### **SUBCONTRACTORS (Service Providers)**
- **What they provide:** LABOR/SERVICES/WORK
- **Examples:** ABC Lawn Care, XYZ HVAC, Clean Pro Janitorial
- **Your role:** Prime Contractor (they do work, you manage contract)
- **Framework:** Service Contract Sub Framework
- **Database:** SUBCONTRACTOR DATABASE

---

## 🗄️ TWO SEPARATE AIRTABLE TABLES

### **TABLE 1: VENDORS** (Product Suppliers)

```
PRIMARY INFO:
1. Vendor ID (Autonumber) - PRIMARY
2. Company Name (Single line text)
3. Contact Name (Single line text)
4. Email (Email)
5. Phone (Phone)
6. Website (URL)
7. Account Number (Single line text) - Your account # with them

VENDOR TYPE:
8. Vendor Category (Single select)
   Options: National Distributor, Manufacturer Direct, 
            Regional Distributor, Local Supplier, Online-Only

9. Product Categories (Multiple select)
   Options: Industrial Supplies, Medical Supplies, Safety Equipment,
            Office Supplies, Janitorial Supplies, Hardware, 
            Electrical, Plumbing, HVAC Parts, Chemicals, 
            Building Materials, Salt/Deicing, Landscaping Materials,
            IT Equipment, Lab Supplies, Automotive, Other

GEOGRAPHIC COVERAGE:
10. Ships To (Multiple select)
    Options: Michigan, Ohio, Illinois, Indiana, Wisconsin,
             All 50 States, International

PRICING & TERMS:
11. Has Government Pricing (Checkbox)
12. Typical Discount (Percent) - What discount they usually give you
13. Payment Terms (Single select)
    Options: Net 15, Net 30, Net 45, Net 60, Due on Delivery, COD
14. Minimum Order (Currency)
15. Shipping Costs (Single select)
    Options: Free Shipping, Flat Rate, Calculated, Expensive, Unknown

QUALITY INDICATORS:
16. Pricing Tier (Single select)
    Options: Very Competitive, Competitive, Average, High, Premium
17. Product Availability (Single select)
    Options: Excellent (90%+ in stock), Good (70-89%), 
             Fair (50-69%), Poor (<50%), Unknown
18. Shipping Speed (Single select)
    Options: Same Day, Next Day, 2-3 Days, 1 Week, 2+ Weeks, Slow

RELATIONSHIP:
19. Status (Single select)
    Options: Active, Preferred, Backup, Do Not Use, Testing
    Colors: Green, Blue, Yellow, Red, Gray
20. First Order Date (Date)
21. Last Order Date (Date)
22. Total Orders (Number)
23. Times Used (Number)
24. Average Order Value (Currency)

PERFORMANCE:
25. Order Accuracy (Single select)
    Options: Excellent (99%+), Good (95-98%), Fair (90-94%), Poor (<90%)
26. Customer Service Quality (Rating 1-5)
27. Quote Response Time (Single select)
    Options: <1 hour, 1-4 hours, Same day, Next day, 2-3 days, Slow
28. Willingness to Negotiate (Single select)
    Options: Very Flexible, Somewhat Flexible, Rigid, Unknown

CERTIFICATIONS & SPECIAL PROGRAMS:
29. GSA Contract (Checkbox)
30. GSA Contract Number (Single line text)
31. WOSB/EDWOSB Partner (Checkbox)
32. Diversity Programs (Multiple select)
    Options: WOSB, MBE, VBE, SDB, HUBZone

NOTES:
33. Negotiation Notes (Long text) - Tips for getting best pricing
34. Strengths (Long text)
35. Weaknesses (Long text)
36. General Notes (Long text)
37. Tags (Multiple select)
    Options: Reliable, Fast, Affordable, Government Pricing, 
             Negotiable, Slow, Expensive, Difficult, Preferred,
             GSA Schedule, Drop Ship Capable

TRACKING:
38. Source (Single select)
    Options: Referral, Google Search, Industry Directory, 
             Cold Call, Trade Show, Existing Relationship
39. Created Date (Created time - auto)
```

---

### **TABLE 2: SUBCONTRACTORS** (Service Providers)

```
PRIMARY INFO:
1. Subcontractor ID (Autonumber) - PRIMARY
2. Company Name (Single line text)
3. Contact Name (Single line text)
4. Email (Email)
5. Phone (Phone)
6. Website (URL)

SERVICE TYPES:
7. Service Categories (Multiple select)
   Options: Landscaping, Lawn Care, Snow Removal, HVAC, 
            Plumbing, Electrical, Janitorial, Security,
            Pressure Washing, IT Services, Construction,
            Painting, Roofing, Concrete, Fencing,
            Pest Control, Moving, Courier, Transportation,
            Maintenance, Repairs, Installation, Other

8. Service Specialties (Long text)
   Example: "Commercial HVAC, Government facilities, 24/7 emergency"

GEOGRAPHIC COVERAGE:
9. Service Area (Multiple select)
   Options: Wayne County, Oakland County, Macomb County,
            Metro Detroit, All Michigan, Illinois, Ohio,
            Indiana, Wisconsin, Multi-State, National

QUALITY INDICATORS:
10. Google Rating (Number - 0.0 to 5.0)
11. Yelp Rating (Number - 0.0 to 5.0)
12. Total Reviews (Number)
13. Years in Business (Number)

CERTIFICATIONS & INSURANCE:
14. Liability Insurance (Single select)
    Options: $2M+, $1M-$2M, $500K-$1M, Under $500K, Unknown
15. Liability Expiration (Date)
16. Workers Comp Insurance (Checkbox)
17. Workers Comp Expiration (Date)
18. License Number (Single line text)
19. License State (Single line text)
20. Business Certifications (Multiple select)
    Options: Woman-Owned, Minority-Owned, Veteran-Owned,
             Small Business, SAM.gov Registered, Bonded

CAPABILITIES:
21. Government Experience (Checkbox)
22. Commercial Experience (Checkbox)
23. Residential Only (Checkbox)
24. Emergency Services Available (Checkbox)
25. 24/7 Availability (Checkbox)
26. Bilingual (Checkbox)
27. Crew Size (Single select)
    Options: 1-5 employees, 6-20, 21-50, 51-100, 100+

PRICING & TERMS:
28. Pricing Model (Single select)
    Options: Hourly, Per Project, Per Unit, Monthly Contract, Annual Contract
29. Typical Rate Range (Long text)
    Example: "$45-$65/hour" or "$500-$800 per lawn"
30. Pricing Tier (Single select)
    Options: Very Competitive, Competitive, Average, High, Premium
31. Payment Terms (Single select)
    Options: Net 15, Net 30, 50% Upfront, Due on Completion, Monthly

RELATIONSHIP STATUS:
32. Status (Single select)
    Options: Active, Preferred, Backup, Testing, Do Not Use
    Colors: Green, Blue, Yellow, Gray, Red
33. Source (Single select)
    Options: Vendor Portal, Google Search, Yelp, Referral,
             Past Bid, LinkedIn, Industry Directory, SAM.gov

PERFORMANCE TRACKING:
34. Times Used (Number - default: 0)
35. Projects Completed (Number)
36. Overall Performance Rating (Rating 1-5 stars)
37. Would Use Again (Checkbox)
38. Average Response Time (Number - in hours)
39. Quote Turnaround Time (Number - in hours)

QUALITY METRICS:
40. On-Time Performance (Percent)
41. Completion Rate (Percent)
42. Quality Rating (Rating 1-5 stars)
43. Communication Rating (Rating 1-5 stars)
44. Safety Record (Single select)
    Options: Excellent, Good, Fair, Issues, Unknown

DATES:
45. First Contact Date (Date)
46. Last Contact Date (Date)
47. Last Project Date (Date)
48. Created Date (Created time - auto)

NOTES & REFERENCES:
49. Strengths (Long text)
50. Weaknesses (Long text)
51. Client References (Long text)
52. General Notes (Long text)
53. Tags (Multiple select)
    Options: Responsive, Reliable, Affordable, Quality Work,
             Fast, Professional, Slow, Expensive, Difficult,
             Preferred, Government Qualified, Bonded, Insured

TRANSFORMATION METRICS (For Proposals):
54. Average Project Rating (Number - from customer reviews)
55. Completion Percentage (Percent)
56. Response Time Average (Number - hours)
57. Years Without Incident (Number)
58. Certifications Count (Number)
```

---

## 🔄 SEPARATE WORKFLOWS

### **PRODUCT BID WORKFLOW (Uses VENDOR Database)**

```
PRODUCT OPPORTUNITY FOUND
(Industrial supplies, medical equipment, materials, etc.)
↓
Click "Find Vendors" in NEXUS
↓
SYSTEM SEARCHES VENDOR TABLE:
  • Filter by product category
  • Filter by ships to location
  • Filter by status = Active or Preferred
  • Sort by: Preferred > Pricing Tier > Past performance
↓
DISPLAY RESULTS:
  • Grainger (Preferred, Account #12345, Gov Pricing ✓)
  • Zoro (Active, Competitive pricing)
  • Fastenal (Backup, Fast delivery)
↓
USER SELECTS VENDORS
↓
AUTOMATED QUOTE REQUEST:
  • Generate RFQ with specs
  • Send to selected vendors
  • Track responses
↓
USE GRAINGER CALL SCRIPT:
  • Negotiate government pricing
  • Request tax removal
  • Negotiate shipping
  • Target: 5-10% discount
↓
COMPARE QUOTES:
  • Best price
  • Best terms
  • Best delivery
↓
SELECT WINNER & BUILD BID
```

---

### **SERVICE BID WORKFLOW (Uses SUBCONTRACTOR Database)**

```
SERVICE OPPORTUNITY FOUND
(Landscaping, HVAC, janitorial, pressure washing, etc.)
↓
Click "Find Subs" in NEXUS
↓
SYSTEM SEARCHES (3-Layer):
  Layer 1: SUBCONTRACTORS Table
    • Filter by service category
    • Filter by service area
    • Filter by certifications required
    • Filter by status = Active or Preferred
    • Sort by: Performance rating > Times used
    
  Layer 2: Google Maps + Yelp APIs (if Layer 1 insufficient)
    • Search for contractors
    • Filter by rating ≥4.0
    • Filter by reviews ≥10
    • Auto-save to SUBCONTRACTORS table
    
  Layer 3: Manual fallback (if APIs fail)
    • Show search links
    • Quick-add form
↓
DISPLAY RESULTS:
  • ABC Lawn Care (Preferred, 4.8★, Used 2x, Response: 4hrs)
  • XYZ Landscaping (Active, 4.6★, New, 147 reviews)
  • Green Gardens (Active, 4.7★, Used 1x, Response: 24hrs)
↓
USER SELECTS 5-10 SUBS
↓
AUTOMATED OUTREACH:
  • Generate personalized emails
  • Request: Quote, availability, insurance cert, LOI
  • Send via SendGrid
  • Track in SUB_OUTREACH_TRACKING
  • Auto follow-ups after 3 days
↓
TRACK RESPONSES:
  • Who responded
  • Response times
  • Quote amounts
  • Availability
  • Insurance status
↓
USE SERVICE SUB FRAMEWORK:
  • Vet top 3 candidates
  • Check licenses/insurance
  • Verify capabilities
  • Request references
  • Get Letter of Intent signed
↓
SELECT WINNING SUB:
  • Best price/value
  • Best qualifications
  • Best availability
↓
BUILD TRANSFORMATION PROPOSAL:
  • Use sub's ratings as proof (4.8/5 from 340 reviews)
  • Use sub's response time as metric (4-hour avg)
  • Use sub's track record as case study (98.7% completion rate)
↓
SUBMIT BID
```

---

## 📊 THIRD TABLE: UNIVERSAL OUTREACH TRACKING

### **TABLE 3: OUTREACH_TRACKING** (For both vendors and subs)

```
LINKS:
1. Outreach ID (Autonumber) - PRIMARY
2. Opportunity (Link to Opportunities table)
3. Type (Single select)
   Options: Vendor Quote Request, Subcontractor RFQ, Follow-Up, Other
4. Vendor (Link to VENDORS table) - if product bid
5. Subcontractor (Link to SUBCONTRACTORS table) - if service bid

OUTREACH:
6. Outreach Date (Date with time)
7. Outreach Method (Single select)
   Options: Email, Phone, Portal, Fax, In-Person
8. Subject/Purpose (Single line text)
9. Message Sent (Long text)
10. Email Sent (Checkbox)
11. Email Opened (Checkbox)
12. Email Clicked (Checkbox)

RESPONSE:
13. Response Status (Single select)
    Options: Pending, Responded, Declined, No Response, Unavailable
    Colors: Yellow, Green, Red, Gray, Orange
14. Response Date (Date with time)
15. Response Time Hours (Formula)
    Formula: DATETIME_DIFF({Response Date}, {Outreach Date}, 'hours')
16. Response Method (Single select)
    Options: Email, Phone, Portal, Fax, In-Person

VENDOR RESPONSES (If product):
17. Quote Amount (Currency)
18. Unit Pricing (Long text)
19. Discount Offered (Percent)
20. Tax Included (Checkbox)
21. Shipping Cost (Currency)
22. Lead Time (Single line text)
23. Payment Terms Offered (Single line text)

SUBCONTRACTOR RESPONSES (If service):
24. Quote Amount (Currency)
25. Quote Details (Long text)
26. Available (Checkbox)
27. Availability Start Date (Date)
28. Crew Size Proposed (Number)
29. Insurance Current (Checkbox)
30. License Current (Checkbox)
31. References Provided (Checkbox)

FOLLOW-UP:
32. Follow-Up Needed (Checkbox)
33. Follow-Up Date (Date)
34. Follow-Up Sent (Checkbox)
35. Follow-Up Count (Number)

SELECTION:
36. Selected (Checkbox)
37. Selection Reason (Long text)
38. Not Selected Reason (Long text)
39. Contract Value (Currency) - If selected

POST-AWARD (If selected):
40. LOI Sent (Checkbox)
41. LOI Received (Checkbox)
42. Insurance Cert Received (Checkbox)
43. W-9 Received (Checkbox)
44. Contract Signed (Checkbox)

NOTES:
45. Notes (Long text)
46. Created Date (Created time - auto)
```

---

## 🎯 INTEGRATION WITH EXISTING FRAMEWORKS

### **FOR PRODUCT BIDS (Vendors):**

```
Grainger Call Script Framework
↓
Uses: VENDOR database
↓
Finds: Grainger, Zoro, Fastenal, etc.
↓
Negotiates: Government pricing, discounts, tax removal
↓
Tracks: In VENDOR table performance
↓
Result: 5-10% better margins
```

---

### **FOR SERVICE BIDS (Subcontractors):**

```
Service Contract Sub Framework
↓
Uses: SUBCONTRACTOR database
↓
Finds: Local contractors with ratings/reviews
↓
Vets: Insurance, licenses, capabilities
↓
Collects: Quotes, LOIs, references
↓
Tracks: Performance in SUBCONTRACTOR table
↓
Result: Transformation proof for proposals
```

---

## 🔍 SEARCH LOGIC DIFFERENCES

### **Finding VENDORS (Products):**

**Search by:**
- Product category (Industrial Supplies, Medical, etc.)
- Ships to location (Michigan, National, etc.)
- Has government pricing (Yes/No)
- Pricing tier (Competitive, etc.)
- Past relationship (Preferred > Active > Testing)

**NOT searching:**
- Google Maps (vendors aren't local businesses)
- Yelp (product suppliers don't have reviews there)

**Finding method:**
- Your existing relationships
- National distributors (Grainger, Fastenal, etc.)
- Manufacturer direct
- GSA Schedule holders
- Industry directories

---

### **Finding SUBCONTRACTORS (Services):**

**Search by:**
- Service category (Landscaping, HVAC, etc.)
- Service area (Oakland County, Metro Detroit, etc.)
- Ratings (≥4.0 stars)
- Insurance/licenses (Required)
- Past performance (Preferred > Active)

**DOES search:**
- Google Maps API (local contractors)
- Yelp API (local service providers)
- SAM.gov (past contract winners)

**Finding method:**
- Automated API search (Google/Yelp)
- Vendor portal registrations
- Manual research
- Referrals

---

## 📋 AIRTABLE VIEWS (Recommended)

### **VENDORS Table Views:**

1. **All Vendors** - Default
2. **Active Vendors** - Status = Active or Preferred
3. **By Product Category** - Group by: Product Categories
4. **Preferred Vendors** - Status = Preferred
5. **Government Pricing** - Filter: Has Government Pricing = TRUE
6. **GSA Contract Holders** - Filter: GSA Contract = TRUE
7. **Needs Attention** - Last Order Date > 6 months ago
8. **By Pricing Tier** - Group by: Pricing Tier

---

### **SUBCONTRACTORS Table Views:**

1. **All Subcontractors** - Default
2. **Active Subs** - Status = Active or Preferred
3. **By Service Category** - Group by: Service Categories
4. **Preferred Subs** - Status = Preferred
5. **High Rated** - Filter: Overall Performance Rating ≥ 4
6. **Government Qualified** - Government Experience = TRUE
7. **By Service Area** - Group by: Service Area
8. **Needs Insurance Update** - Insurance expiring soon
9. **Response Time Leaders** - Sort by: Average Response Time (ascending)

---

## 📊 DASHBOARD METRICS

### **VENDOR METRICS:**
- Total active vendors: [X]
- Vendors with government pricing: [X]
- Average discount achieved: [X]%
- Orders placed this month: [X]
- Total order value YTD: $[X]

### **SUBCONTRACTOR METRICS:**
- Total active subcontractors: [X]
- Average rating: [X.X] stars
- Average response time: [X] hours
- Projects completed: [X]
- On-time performance: [X]%

---

## 🚀 IMPLEMENTATION PRIORITY

### **TODAY (2 hours):**

**Create 2 tables:**
1. VENDORS table (for products) - 30 min
2. SUBCONTRACTORS table (for services) - 30 min

**Seed databases:**
3. Add 10 known vendors (Grainger, MOPEC, etc.) - 20 min
4. Add 10 known subs (any contractors you've worked with) - 20 min

**Rapid build:**
5. Google search salt vendors (for Oakland County salt bid) - 20 min
6. Add 10 salt product vendors to VENDORS table

**Result:** Ready for tomorrow's calls with organized data

---

### **WEEK 1: Build Product Vendor Database**
- Add national distributors (Grainger, Zoro, Fastenal, etc.)
- Add category-specific vendors (MOPEC for medical, etc.)
- Target: 50+ product vendors

### **WEEK 2: Build Subcontractor Database + Add Automation**
- Manual search: 5 service categories × 10 subs = 50 subs
- Set up Google Maps + Yelp APIs
- Build automated sub search
- Target: 50+ subcontractors + working automation

### **WEEK 3: Automated Outreach**
- Email automation for both vendors and subs
- Different templates for each
- Tracking for both

### **WEEK 4: Vendor Portal (Both Types)**
- deedavis.biz/vendors (for product vendors)
- deedavis.biz/subcontractors (for service providers)
- Separate registration forms for each

---

## 💡 KEY INSIGHTS

**VENDORS (Products):**
- ✅ Relationships matter (negotiate better pricing)
- ✅ National scope (not location-dependent)
- ✅ Focus: Pricing, terms, delivery
- ✅ Framework: Grainger Call Script
- ✅ Database grows slowly (finite list of distributors)

**SUBCONTRACTORS (Services):**
- ✅ Local focus (must service geographic area)
- ✅ Ratings/reviews critical (quality proof)
- ✅ Focus: Capabilities, insurance, performance
- ✅ Framework: Service Sub Framework
- ✅ Database grows rapidly (unlimited local businesses)

---

## ✅ IMMEDIATE ACTIONS (RIGHT NOW)

**Create both Airtable tables using schemas above:**

1. VENDORS table - for product suppliers
2. SUBCONTRACTORS table - for service providers
3. OUTREACH_TRACKING table - for both

**Add what you know:**
- Vendors: Grainger, MOPEC, etc.
- Subs: Any contractors you've worked with

**Priority for tomorrow:**
- VENDORS: Salt suppliers (for Oakland County salt bid)
- SUBS: Pressure washing (if pursuing Auburn Hills)

---

**TWO DATABASES, ONE POWERFUL SYSTEM!** 🎯

---

*Created: February 8, 2026*  
*Distinction: Vendors = Products | Subcontractors = Services*  
*Integration: Grainger Script + Service Sub Framework*
