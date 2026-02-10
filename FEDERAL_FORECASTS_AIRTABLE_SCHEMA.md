# FEDERAL FORECASTS - AIRTABLE SCHEMA

**Table Name:** `Federal Forecasts`

**Purpose:** Store REAL federal procurement forecasts from official government sources (NASA, GSA, DHS, USAID, Commerce, Treasury, SAM.gov pre-solicitations)

---

## FIELDS TO CREATE IN AIRTABLE

### **Basic Information**

| Field Name | Type | Description |
|------------|------|-------------|
| **Title** | Single line text | Forecast title (e.g., "NASA - IT Equipment Modernization") |
| **Agency** | Single select | Primary agency (NASA, GSA, DHS, USAID, Commerce, Treasury, etc.) |
| **Sub-Agency** | Single line text | Sub-agency or office (e.g., "Johnson Space Center") |
| **Description** | Long text | What they plan to buy |
| **NAICS Code** | Single line text | Industry classification code |
| **PSC Code** | Single line text | Product/Service Code (optional) |

### **Financial & Timeline**

| Field Name | Type | Description |
|------------|------|-------------|
| **Estimated Value** | Currency | Estimated contract value |
| **Estimated Solicitation Date** | Date | When RFP/RFQ will be posted |
| **Expected Award Date** | Date | When contract will be awarded |
| **Contract Duration** | Single line text | "1 year", "3 years", etc. |
| **Fiscal Year** | Single select | FY2026, FY2027, etc. |

### **Procurement Details**

| Field Name | Type | Description |
|------------|------|-------------|
| **Set-Aside Type** | Single select | WOSB, EDWOSB, 8(a), SDVOSB, HUBZone, Unrestricted |
| **Contract Type** | Single select | FFP, T&M, Cost Plus, IDIQ, etc. |
| **Place of Performance** | Single line text | City, State where work will be done |
| **State** | Single line text | State abbreviation |
| **Solicitation Number** | Single line text | If pre-solicitation, the solicitation number |

### **Source & Tracking**

| Field Name | Type | Description |
|------------|------|-------------|
| **Source** | Single select | SAM.gov Pre-Solicitation, NASA Official Forecast, GSA Forecast, DHS Forecast, USAID Forecast, Commerce Forecast, Treasury Forecast |
| **Source URL** | URL | Link to original forecast |
| **Forecast Type** | Single select | Near-Term (0-3 months), Short-Term (3-6 months), Long-Term (6-12 months), FY2026 Forecast, FY2027 Forecast |
| **Confidence** | Single select | High, Medium, Low (how confident is the forecast) |
| **Posted Date** | Date | When forecast was published |
| **Response Deadline** | Date | For pre-solicitations only |
| **Mined Date** | Date | When NEXUS discovered this forecast |

### **AI Analysis**

| Field Name | Type | Description |
|------------|------|-------------|
| **Fit Score** | Number | 0-100 score (how well matches DEE DAVIS INC capabilities) |
| **Fit Analysis** | Long text | AI explanation of fit |
| **Priority** | Single select | HIGH, MEDIUM, LOW |
| **Recommended Action** | Long text | What to do next |
| **Preparation Tips** | Long text | How to prepare for this opportunity |

### **Workflow & Status**

| Field Name | Type | Description |
|------------|------|-------------|
| **Status** | Single select | New, Analyzed, Tracking, Watching, Preparing, Solicitation Posted, Bid Submitted, Won, Lost, Cancelled |
| **Assigned To** | Single select | Who's tracking this forecast |
| **Notes** | Long text | Internal notes |
| **Competitors** | Long text | Known competitors interested in this |
| **Last Updated** | Last modified time | Auto-updated timestamp |

### **Linked Records**

| Field Name | Type | Description |
|------------|------|-------------|
| **Related Opportunities** | Link to GPSS OPPORTUNITIES | Links when solicitation is posted |
| **Related Proposals** | Link to GPSS PROPOSALS | Links if you decide to bid |

---

## VIEWS TO CREATE

### **1. High Priority Forecasts**
- **Filter:** `Priority = "HIGH"` AND `Status != "Cancelled"`
- **Sort:** Estimated Solicitation Date (earliest first)
- **Purpose:** Focus on best opportunities

### **2. WOSB Set-Asides**
- **Filter:** `Set-Aside Type` contains "WOSB" OR "EDWOSB"
- **Sort:** Fit Score (highest first)
- **Purpose:** Your competitive advantage forecasts

### **3. Coming Soon (Next 90 Days)**
- **Filter:** `Estimated Solicitation Date` is within next 90 days
- **Sort:** Estimated Solicitation Date (earliest first)
- **Purpose:** Immediate preparation needed

### **4. By Agency**
- **Group:** Agency
- **Sort:** Estimated Value (highest first)
- **Purpose:** Track opportunities by agency

### **5. New & Unanalyzed**
- **Filter:** `Status = "New"` AND `Fit Score` is empty
- **Sort:** Mined Date (newest first)
- **Purpose:** Forecasts waiting for AI analysis

### **6. Tracking & Preparing**
- **Filter:** `Status` is one of "Tracking", "Watching", "Preparing"
- **Sort:** Estimated Solicitation Date (earliest first)
- **Purpose:** Active forecast tracking

---

## AUTOMATIONS TO CREATE

### **1. New High-Priority Forecast Alert**
**Trigger:** When record created OR updated  
**Condition:** `Fit Score >= 80` AND `Priority = "HIGH"`  
**Action:** Send email notification

**Email Template:**
```
Subject: 🔮 HIGH PRIORITY Federal Forecast: {Title}

New federal procurement forecast matches your capabilities!

FORECAST: {Title}
AGENCY: {Agency}
ESTIMATED VALUE: ${Estimated Value}
SOLICITATION DATE: {Estimated Solicitation Date}
SET-ASIDE: {Set-Aside Type}

FIT SCORE: {Fit Score}/100
PRIORITY: HIGH

WHY IT'S A GOOD FIT:
{Fit Analysis}

RECOMMENDED ACTION:
{Recommended Action}

PREPARATION TIPS:
{Preparation Tips}

View in NEXUS: [Link to Airtable record]

---
This forecast was automatically discovered by NEXUS Federal Forecasts System
```

### **2. Solicitation Date Approaching (30 Days)**
**Trigger:** Scheduled (daily at 8 AM)  
**Condition:** `Estimated Solicitation Date` is within next 30 days AND `Status != "Cancelled"`  
**Action:** Send reminder email

**Email Template:**
```
Subject: ⏰ Federal Forecast - Solicitation Expected in 30 Days

FORECAST: {Title}
AGENCY: {Agency}
ESTIMATED SOLICITATION DATE: {Estimated Solicitation Date} (30 days away!)

TIME TO PREPARE:
1. Research agency's procurement history
2. Identify suppliers for your quotes
3. Draft capability statement section
4. Pre-qualify any teaming partners
5. Monitor SAM.gov for solicitation posting

View forecast: [Link]
```

### **3. Solicitation Date Approaching (7 Days)**
**Trigger:** Scheduled (daily at 8 AM)  
**Condition:** `Estimated Solicitation Date` is within next 7 days AND `Status != "Cancelled"`  
**Action:** Send urgent reminder

**Email Template:**
```
Subject: 🚨 URGENT - Federal Forecast Solicitation Expected THIS WEEK

FORECAST: {Title}
AGENCY: {Agency}
ESTIMATED SOLICITATION DATE: {Estimated Solicitation Date} (WITHIN 7 DAYS!)

URGENT ACTIONS:
1. Monitor SAM.gov DAILY for posting
2. Have supplier quotes ready
3. Prepare bid forms in advance
4. Clear calendar for immediate response

Status: {Status}
Fit Score: {Fit Score}/100

View forecast: [Link]
```

### **4. Weekly Forecast Digest**
**Trigger:** Scheduled (Monday 8 AM)  
**Action:** Send summary of all active forecasts

**Email Template:**
```
Subject: 📊 Weekly Federal Forecasts Summary

ACTIVE FORECASTS: {Count of Status = "Tracking" or "Watching" or "Preparing"}

HIGH PRIORITY (This Quarter):
{List of Priority = "HIGH" and Est. Solicitation Date within 90 days}

COMING SOON (Next 30 Days):
{List of Est. Solicitation Date within 30 days}

NEW THIS WEEK:
{List of Mined Date within last 7 days}

View all forecasts in NEXUS: [Link to Airtable view]
```

---

## INITIAL SETUP

### **Step 1: Create Table**
1. In your NEXUS Airtable base, create new table: "Federal Forecasts"
2. Add all fields listed above

### **Step 2: Create Views**
1. Create the 6 views listed above
2. Customize sort/filter as needed

### **Step 3: Set Up Automations**
1. Create the 4 automations listed above
2. Update email addresses
3. Test each automation

### **Step 4: Run Initial Mine**
```bash
cd "/Users/deedavis/NEXUS BACKEND"
python3 federal_forecasts_system.py
```

### **Step 5: Schedule Automated Mining**
Add to cron (runs daily at 6 AM):
```bash
0 6 * * * cd "/Users/deedavis/NEXUS BACKEND" && /usr/bin/python3 -c "from federal_forecasts_system import handle_mine_federal_forecasts; handle_mine_federal_forecasts()" >> federal_forecasts.log 2>&1
```

---

## USAGE WORKFLOW

### **Daily (Automated)**
1. 6:00 AM - System mines new forecasts from all sources
2. 6:30 AM - AI analyzes and scores each forecast
3. 7:00 AM - High-priority alerts sent to your email
4. 8:00 AM - Approaching solicitation reminders sent

### **Weekly (Manual Review)**
1. Monday morning - Review weekly digest
2. Check "High Priority Forecasts" view
3. Update Status on forecasts you're tracking
4. Add notes on preparation progress

### **When Solicitation Posts**
1. Link forecast to actual opportunity in GPSS OPPORTUNITIES
2. Update forecast Status to "Solicitation Posted"
3. Begin bid preparation workflow

---

## EXPECTED RESULTS

### **After First Mine:**
- 50-150 federal forecasts discovered
- 10-30 high-fit matches (score ≥ 70)
- 3-10 high-priority forecasts (score ≥ 80)

### **Ongoing (Weekly):**
- 5-15 new forecasts added
- 2-5 new high-fit matches
- 1-3 solicitations posted from forecasts

### **Value:**
- **3-6 months advance notice** of upcoming procurements
- **Competitive advantage** - prepare before others know
- **Higher win rate** - enter bids fully prepared
- **Time to build relationships** with agencies before RFP drops

---

## DATA SOURCES

**Real Government Data:**
1. ✅ SAM.gov Pre-Solicitations (daily updates)
2. ✅ NASA Procurement Forecasts (quarterly updates)
3. ✅ GSA Forecast of Contracting Opportunities (quarterly)
4. ✅ DHS Acquisition Planning Forecast System (quarterly)
5. ✅ USAID Business Forecast (quarterly)
6. ✅ Commerce Procurement Forecasts (quarterly)
7. ✅ Treasury Small Business Forecast (quarterly)

**NOT predictions** - These are OFFICIAL agency announcements!

---

## NEXT STEPS

1. [ ] Create "Federal Forecasts" table in Airtable with all fields
2. [ ] Create the 6 views
3. [ ] Set up the 4 automations
4. [ ] Run initial mine: `python3 federal_forecasts_system.py`
5. [ ] Schedule daily automated mining (cron job)
6. [ ] Review first batch of forecasts
7. [ ] Start tracking high-priority forecasts

---

**You now have REAL federal forecast data - not predictions, actual government announcements!** 🔮✅

*Created: January 28, 2026*  
*System: Federal Forecasts Mining*  
*Status: Ready to Deploy*
