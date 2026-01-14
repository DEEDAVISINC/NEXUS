# GPSS VENDOR MANAGEMENT & OPPORTUNITY MINING SYSTEM

## 📋 **TABLE 1: VENDOR PORTALS**

### **Purpose:** Track ALL vendor portals/sites where you're registered for opportunity mining

### **Fields to Add:**

| Field Name | Field Type | Options/Configuration |
|------------|-----------|----------------------|
| **Portal ID** | Auto-number | PRIMARY FIELD - Auto-generated unique ID |
| **Portal Name** | Single line text | e.g., "SAM.gov", "Michigan SIGMA", "BuyBoard" |
| **Portal Type** | Single select | Options: `Federal`, `State`, `Local`, `Cooperative`, `Enterprise`, `Industry-Specific` |
| **Portal URL** | URL | Direct link to portal |
| **Login URL** | URL | Direct link to login page |
| **Registration Status** | Single select | Options: `Active`, `Pending`, `Expired`, `Renewal Needed`, `Not Registered` (colors: green, yellow, red, orange, gray) |
| **Username** | Single line text | Login username |
| **Password Note** | Long text | **NEVER store actual password** - note location (e.g., "See 1Password") |
| **Registration Date** | Date | When you registered |
| **Expiration Date** | Date | When registration expires |
| **Renewal Frequency** | Single select | Options: `Annual`, `Biannual`, `Monthly`, `No Expiration`, `Unknown` |
| **Auto-Mining Enabled** | Checkbox | Can NEXUS auto-check this portal? |
| **Mining Frequency** | Single select | Options: `Daily`, `Twice Daily`, `Weekly`, `Manual Only` |
| **Last Checked** | Date & time | Last time NEXUS checked for opportunities |
| **Opportunities Found (Total)** | Number | Lifetime opportunity count from this portal |
| **Opportunities This Month** | Number | Current month opportunity count |
| **API Available** | Checkbox | Does portal have an API? |
| **API Key** | Long text | If API exists (encrypted storage recommended) |
| **Scraping Method** | Single select | Options: `API`, `Web Scraping`, `Manual`, `RSS Feed`, `Email Alerts` |
| **Geographic Focus** | Single select | Options: `National`, `MI`, `OH`, `IL`, `IN`, `WI`, `Multi-State`, `Regional` |
| **Primary Industry** | Single select | Options: `All Industries`, `Healthcare`, `Transportation`, `IT/Tech`, `Professional Services`, `Facilities`, `Education` |
| **Set-Aside Filter** | Multiple select | Options: `EDWOSB`, `WOSB`, `8(a)`, `HUBZone`, `SDVOSB`, `Small Business`, `All` |
| **Min Contract Value** | Currency | Don't mine opportunities below this value |
| **Max Contract Value** | Currency | Don't mine opportunities above this value |
| **Success Rate** | Percent | Win rate from opportunities found here |
| **Total Awarded Value** | Currency | Total $ value of contracts won from this portal |
| **Priority Level** | Single select | Options: `Critical`, `High`, `Medium`, `Low` (based on success rate) |
| **Notes** | Long text | Special instructions, contacts, tips |
| **Contact Name** | Single line text | Portal support contact |
| **Contact Email** | Email | Portal support email |
| **Contact Phone** | Phone number | Portal support phone |
| **Last Login** | Date & time | Track when you last logged in manually |
| **Auto-Login Working** | Checkbox | Can NEXUS auto-login successfully? |
| **Scraping Issues** | Long text | Track any technical issues |
| **Opportunities Link** | Link to another record | Link to "Opportunities" table |
| **Tags** | Multiple select | Options: `High-Value`, `Easy-Win`, `EDWOSB-Friendly`, `Quick-Turnaround`, `Relationship-Based` |
| **Created Date** | Created time | Auto-generated |

---

## 📋 **TABLE 2: OPPORTUNITY FORECASTS**

### **Purpose:** Predicted/forecasted opportunities based on historical data and patterns

### **Fields to Add:**

| Field Name | Field Type | Options/Configuration |
|------------|-----------|----------------------|
| **Forecast ID** | Auto-number | PRIMARY FIELD |
| **Forecast Title** | Single line text | e.g., "MI DOT Annual Road Maintenance Contract" |
| **Agency/Organization** | Single line text | Who will post it |
| **Portal** | Link to another record | Link to "Vendor Portals" table |
| **Forecast Type** | Single select | Options: `Historical Pattern`, `Agency Budget Cycle`, `Renewal Forecast`, `New Opportunity`, `AI Prediction` |
| **Predicted Post Date** | Date | When we think it'll be posted |
| **Confidence Level** | Single select | Options: `Very High (90%+)`, `High (70-89%)`, `Medium (50-69%)`, `Low (<50%)` |
| **Estimated Value** | Currency | Predicted contract value |
| **Contract Duration** | Number | Expected duration in months |
| **Source of Forecast** | Single select | Options: `Historical Data`, `Agency Announcement`, `Budget Documents`, `Industry Intel`, `AI Analysis` |
| **Historical Data** | Long text | Past contract information |
| **Last Awarded Date** | Date | When similar contract was last awarded |
| **Last Awarded Value** | Currency | Previous contract value |
| **Frequency** | Single select | Options: `Annual`, `Biannual`, `Every 2 Years`, `Every 3 Years`, `One-Time` |
| **Set-Aside Type** | Single select | Options: `EDWOSB`, `8(a)`, `HUBZone`, `SDVOSB`, `Small Business`, `Unrestricted`, `Unknown` |
| **NAICS Code** | Single line text | Expected NAICS |
| **Service Category** | Single select | Same 9 categories as pricing system |
| **Geographic Region** | Single select | `Federal`, `MI`, `OH`, `IL`, `IN`, `WI`, `Other` |
| **Target Deadline** | Date | Expected submission deadline |
| **Prep Time Needed** | Number | Days needed to prepare proposal |
| **Alert Date** | Formula | `{Predicted Post Date} - {Prep Time Needed} days` |
| **Status** | Single select | Options: `Watching`, `Posted`, `Expired`, `Awarded`, `Cancelled`, `False Alarm` |
| **Actual Post Date** | Date | When it actually posted (for accuracy tracking) |
| **Actual Value** | Currency | Actual contract value (for accuracy tracking) |
| **Forecast Accuracy** | Formula | Compare predicted vs actual |
| **Action Items** | Long text | What to prepare now |
| **Key Contacts** | Long text | Who to reach out to |
| **Win Probability** | Number | Our estimated win chance (0-100) |
| **Pursuit Decision** | Single select | Options: `Pursue`, `Watch`, `No-Bid`, `Undecided` |
| **Assigned To** | Single line text | Team member assigned |
| **Notes** | Long text | Additional intelligence |
| **Tags** | Multiple select | Options: `High-Value`, `Strategic`, `Must-Win`, `Quick-Win`, `Partnership-Needed` |
| **Created Date** | Created time | Auto-generated |

---

## 📋 **RECOMMENDED VIEWS:**

### **For Vendor Portals:**
1. **All Portals** - Default view
2. **Active Portals** - Filter: Registration Status = Active
3. **Auto-Mining Enabled** - Filter: Auto-Mining Enabled = TRUE
4. **Needs Renewal** - Filter: Expiration Date < 30 days from today
5. **By Type** - Group by: Portal Type
6. **High Priority** - Filter: Priority Level = Critical or High
7. **Daily Check** - Filter: Mining Frequency = Daily

### **For Opportunity Forecasts:**
1. **All Forecasts** - Default view
2. **Watching** - Filter: Status = Watching
3. **High Confidence** - Filter: Confidence Level = Very High or High
4. **Coming Soon (30 days)** - Filter: Predicted Post Date < 30 days
5. **Pursuit Decisions** - Filter: Pursuit Decision = Pursue
6. **By Agency** - Group by: Agency/Organization
7. **EDWOSB Opportunities** - Filter: Set-Aside Type = EDWOSB

---

## 🔗 **RELATIONSHIPS BETWEEN TABLES:**

```
Vendor Portals
    ↓
    ├─→ Opportunities (discovered opportunities)
    ├─→ Opportunity Forecasts (predicted opportunities)
    └─→ Pricing History (opportunities we bid on)
```

---

## 📋 **TABLE 3: MINING TARGETS**

### **Purpose:** Track ANY site to scrape for opportunities (registered OR not registered)

### **Fields to Add:**

| Field Name | Field Type | Options/Configuration |
|------------|-----------|----------------------|
| **Target ID** | Auto-number | PRIMARY FIELD |
| **Target Name** | Single line text | e.g., "GSA eBuy Public Search", "Michigan RFP Page" |
| **Target Type** | Single select | Options: `Public Portal`, `Agency Website`, `Industry Board`, `Competitor Site`, `News/Alert Site`, `Social Media`, `Other` |
| **Target URL** | URL | Page to scrape |
| **Registered Vendor?** | Checkbox | Are we registered here? Links to Vendor Portals if yes |
| **Scraping Method** | Single select | Options: `Public Web Scraping`, `RSS Feed`, `Email Parsing`, `API (Public)`, `Manual Watch` |
| **Scraping Frequency** | Single select | Options: `Hourly`, `Daily`, `Twice Daily`, `Weekly`, `Manual Only` |
| **Last Scraped** | Date & time | Last check time |
| **Opportunities Found** | Number | Total opportunities discovered |
| **Data Quality** | Single select | Options: `Excellent`, `Good`, `Fair`, `Poor` (how reliable is this source) |
| **Scraping Status** | Single select | Options: `Active`, `Paused`, `Failed`, `Testing` |
| **Scraping Selectors** | Long text | CSS selectors or xpath for scraping |
| **Search Keywords** | Long text | Keywords to search for (comma-separated) |
| **NAICS Filter** | Single line text | Only find opportunities with these NAICS codes |
| **Min Value Filter** | Currency | Ignore opportunities below this value |
| **Geographic Filter** | Multiple select | `Federal`, `MI`, `OH`, `IL`, `IN`, `WI`, `All States` |
| **Purpose** | Single select | Options: `Direct Opportunities`, `Competitor Intel`, `Market Research`, `Agency Tracking`, `Industry Trends` |
| **Access Level** | Single select | Options: `Public (No Login)`, `Requires Registration`, `Requires Payment`, `Restricted` |
| **Reliability Score** | Number | 1-10 (how often does this source have real opportunities) |
| **False Positive Rate** | Percent | How often finds non-opportunities |
| **Priority** | Single select | Options: `Critical`, `High`, `Medium`, `Low`, `Research Only` |
| **Notes** | Long text | Scraping tips, gotchas, special instructions |
| **Opportunities Link** | Link to another record | Link to "Opportunities" table |
| **Tags** | Multiple select | Options: `High-Value`, `EDWOSB-Rich`, `Quick-Turnaround`, `Competitive-Intel`, `Research` |
| **Created Date** | Created time | Auto-generated |

---

## ⚡ **QUICK START CHECKLIST:**

- [ ] Create Table: Vendor Portals (registered sites)
- [ ] Create Table: Opportunity Forecasts (predictions)
- [ ] Create Table: Mining Targets (ANY site to scrape)
- [ ] Add your registered portals (SAM.gov, state portals, etc.)
- [ ] Add public research targets (competitor sites, news, etc.)
- [ ] Link to existing Opportunities table
- [ ] Create recommended views
- [ ] Set up mining frequency for each target

---

## 🎯 **PORTAL EXAMPLES TO ADD:**

### **Vendor Portals (Registered):**

**Federal:**
- SAM.gov
- GSA eBuy
- DIBBS (Defense)
- NASA SEWP
- VA VAAR

**State (Your Focus):**
- Michigan SIGMA
- Ohio ODJFS
- Illinois Procurement Gateway
- Indiana PO Portal
- Wisconsin VendorNet

**Cooperative:**
- NASPO ValuePoint
- Sourcewell
- BuyBoard
- TIPS
- E&I Cooperative

**Local:**
- County procurement sites
- City bid portals
- School district RFPs

**Enterprise:**
- Private company portals
- Healthcare systems
- University systems

---

### **Mining Targets (Public Scraping - Not Registered):**

**Public Federal Searches:**
- SAM.gov public search (no login)
- FedBizOpps archive
- USA Spending (contract awards)
- Federal Procurement Data System

**State Public Pages:**
- Michigan Open Data
- Ohio transparency sites
- State budget documents

**Industry Intelligence:**
- GovWin (public portions)
- Bloomberg Government (free tier)
- Government Executive
- Defense News contract awards

**Competitive Intel:**
- Company press releases (contract wins)
- LinkedIn company updates
- Industry association news
- Trade publication awards

**Agency Websites:**
- Individual agency procurement pages
- "Doing Business With Us" pages
- Pre-solicitation notices
- Industry day announcements

**News & Alerts:**
- Google Alerts for RFP keywords
- Twitter/X government accounts
- Government RSS feeds
- Agency newsletters

**Market Research:**
- GovTribe public data
- FPDS public search
- Agency strategic plans
- Congressional budget docs

---

## 📊 **EXPECTED RESULT:**

Once complete, NEXUS will:
- ✅ Track ALL vendor portals in one place
- ✅ Auto-mine opportunities daily
- ✅ Forecast upcoming contracts
- ✅ Alert you BEFORE RFPs post
- ✅ Track success rates by portal
- ✅ Prioritize best opportunities
- ✅ Never miss a deadline

**Estimated setup time: 30-40 minutes**
**Estimated ROI: $10M+ in discovered opportunities per year**

---

**Let me know when tables are ready and I'll build the mining engine!** 🚀

