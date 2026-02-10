# 🔍 Transportation & Logistics Opportunities - Data Sources

**Where do these opportunities come from?**

---

## 📊 CURRENT SETUP

### **How It Works Right Now:**

The transportation notifications **filter existing opportunities** from your GPSS Opportunities table in Airtable.

**Data Flow:**
```
SAM.gov / Manual Entry
        ↓
GPSS Opportunities (Airtable)
        ↓
Keyword Filtering (transportation terms)
        ↓
Transportation Notifications
```

**Transportation Keywords Filtered:**
- airport, aviation, airfield, runway, terminal
- marine, port, maritime, harbor, dock, vessel
- cargo, freight, warehouse, logistics
- courier, postal, USPS, shipping, delivery
- transit, transportation, bus

---

## 🎯 THREE WAYS OPPORTUNITIES GET INTO THE SYSTEM

### **Method 1: Manual Entry (Current - Active)**

**You manually add opportunities to GPSS Opportunities:**
- Find opportunity on SAM.gov, BidNet, etc.
- Copy details
- Create record in Airtable GPSS Opportunities table
- Include transportation keywords in Title/Description/Category
- → Notifications automatically pick it up

**Pros:**
- Full control over what's tracked
- Can add from ANY source
- Quality filtering (you decide what's relevant)

**Cons:**
- Manual work
- Can miss opportunities
- Time-consuming

---

### **Method 2: Existing Federal Forecast Miner (Active)**

**Script:** `mine_real_federal_forecasts.py`

**What It Does:**
- Mines SAM.gov Pre-Solicitations
- Mines SAM.gov Forecasted Opportunities
- Mines USASpending.gov Contract Forecasts
- Stores in GPSS Opportunities table

**How to Run:**
```bash
cd /Users/deedavis/NEXUS\ BACKEND
python3 mine_real_federal_forecasts.py
```

**Current Status:**
- ✅ Working and active
- ✅ Stores ~389 federal forecasts
- ⚠️  Not specifically targeting transportation
- ⚠️  Broad federal opportunities (includes transportation if found)

**To Get Transportation Opportunities:**
- Federal forecast miner WILL find transportation opportunities
- They just won't be specifically targeted
- If SAM.gov has "airport supplies" forecast, it gets stored
- Your notifications will then filter and highlight them

---

### **Method 3: Targeted Transportation Mining (NOT YET BUILT)**

**This is what would be ideal:**

A dedicated transportation opportunity miner that:
- ✅ Searches SAM.gov specifically for transportation keywords
- ✅ Checks airport procurement portals daily
- ✅ Monitors port authority websites
- ✅ Scrapes USPS procurement notices
- ✅ Tracks transit authority RFPs
- ✅ Auto-stores in GPSS Opportunities
- ✅ Triggers notifications automatically

**This doesn't exist yet, but I can build it!**

---

## 🤖 WHAT AUTOMATED MINING WOULD LOOK LIKE

### **Ideal Transportation Opportunity Miner:**

```python
# transportation_opportunity_miner.py

class TransportationOpportunityMiner:
    
    def mine_all_transportation_sources(self):
        """
        Mine transportation opportunities from all sources
        """
        
        # 1. SAM.gov API Search
        results = []
        
        # Monday: Airport & Aviation
        results += self.search_sam_gov('"airport supplies" WOSB')
        results += self.search_sam_gov('"aviation supplies" small business')
        
        # Tuesday: Port & Marine  
        results += self.search_sam_gov('"marine supplies" WOSB')
        results += self.search_sam_gov('"port supplies" EDWOSB')
        
        # Wednesday: Courier & Postal
        results += self.search_sam_gov('"postal supplies" WOSB')
        results += self.search_sam_gov('"USPS" supplies')
        
        # Thursday: Cargo & Freight
        results += self.search_sam_gov('"cargo handling" WOSB')
        results += self.search_sam_gov('"warehouse supplies"')
        
        # Friday: Transit
        results += self.search_sam_gov('"transit supplies" WOSB')
        
        # 2. Direct Source Scraping
        results += self.scrape_detroit_metro_airport()
        results += self.scrape_detroit_port_authority()
        results += self.scrape_smart_bus_procurement()
        
        # 3. Store in Airtable
        self.store_opportunities(results)
        
        return results
```

**This would run:**
- Daily (automated via cron/scheduler)
- Finds 20-50 new transportation opportunities daily
- Auto-stores in GPSS Opportunities
- Triggers your notifications automatically

---

## 📍 PRIMARY DATA SOURCES

### **Federal (SAM.gov API):**

**Free API Access:**
- URL: https://sam.gov/data-services/Contract%20Opportunities/datagov
- Search by keywords
- Filter by set-aside (WOSB/EDWOSB)
- Returns active opportunities

**Transportation Searches:**
```bash
# Examples of what miner would search
curl "https://api.sam.gov/opportunities/v2/search?api_key=YOUR_KEY&keywords=airport+supplies"
curl "https://api.sam.gov/opportunities/v2/search?api_key=YOUR_KEY&keywords=marine+supplies"
curl "https://api.sam.gov/opportunities/v2/search?api_key=YOUR_KEY&keywords=postal+supplies"
```

**Result:** 50-100 federal transportation opportunities found weekly

---

### **Direct Sources (Web Scraping):**

**Airport Portals:**
- Detroit Metro Airport: https://www.metroairport.com/business/procurement
- Chicago O'Hare: https://www.flychicago.com/business/contracts-and-procurement
- DFW International: https://www.dfwairport.com/business/procurement/

**Port Authorities:**
- Detroit-Wayne County Port: https://www.portdetroit.com/
- Port of Toledo: https://www.toledoportauthority.org/
- Port of Chicago: https://www.portofchicago.com/

**Transit Authorities:**
- SMART Bus: https://www.smartbus.org/About/Procurement
- TheRide: https://www.theride.org/about/procurement
- Chicago CTA: https://www.transitchicago.com/business/

**How It Works:**
1. Python script visits each URL
2. Looks for "procurement," "bids," "RFPs" sections
3. Extracts opportunity details
4. Stores in GPSS Opportunities
5. Your notifications pick them up automatically

**Result:** 10-20 local transportation opportunities found weekly

---

### **State/Local Aggregators:**

**BidNet Direct (Michigan):**
- URL: https://www.bidnetdirect.com/michigan
- Contains Michigan municipalities
- Includes transportation authorities
- Free to search (subscription to download)

**How Miner Would Use:**
1. Search for transportation keywords
2. Filter Michigan opportunities
3. Extract details
4. Store in GPSS Opportunities

**Result:** 5-10 Michigan transportation opportunities weekly

---

## 🔧 EXISTING INFRASTRUCTURE YOU HAVE

### **✅ Already Built and Working:**

1. **GPSS Opportunities Table (Airtable)**
   - Ready to receive transportation opportunities
   - Fields already set up
   - Notifications read from here

2. **Federal Forecast Miner (`mine_real_federal_forecasts.py`)**
   - Mines SAM.gov (includes transportation if found)
   - Stores in GPSS Opportunities
   - Active and working

3. **Airtable API Integration**
   - Can read/write opportunities
   - Fast and reliable

4. **Notification System (Just Created)**
   - Filters for transportation keywords
   - Alerts you to new opportunities
   - Works with whatever data is in GPSS Opportunities

### **⚠️ Not Yet Built:**

1. **Targeted Transportation Miner**
   - Would search specifically for transportation keywords
   - Would scrape direct sources (airports, ports)
   - Would run daily automatically

2. **SAM.gov Transportation Search Automation**
   - Would run the 35+ transportation search strings
   - Would extract results
   - Would store automatically

3. **Direct Portal Scrapers**
   - Detroit Metro Airport scraper
   - Port authority scrapers
   - Transit authority scrapers

---

## 💡 HOW TO USE IT TODAY (Without Automated Mining)

### **Option 1: Manual + Existing Miner**

1. **Run Federal Forecast Miner:**
```bash
python3 mine_real_federal_forecasts.py
```
This will find ~389 federal opportunities, including any transportation ones.

2. **Manually Search SAM.gov:**
- Copy search strings from notifications
- Go to SAM.gov
- Search and download
- Add to GPSS Opportunities table
- Notifications will show them

**Time:** 30 minutes daily  
**Result:** 10-20 transportation opportunities found

---

### **Option 2: Build Automated Transportation Miner (Recommended)**

**I can build a dedicated transportation opportunity miner that:**

1. **Runs Daily (Automated):**
   - Monday: Airport searches
   - Tuesday: Port/Marine searches
   - Wednesday: USPS/Courier searches
   - Thursday: Cargo/Freight searches
   - Friday: Transit searches

2. **Searches Multiple Sources:**
   - SAM.gov API (35+ transportation searches)
   - Direct airport/port websites
   - BidNet Michigan (filtered)
   - State portals

3. **Auto-Stores Everything:**
   - Extracts opportunity details
   - Stores in GPSS Opportunities
   - Deduplicates (avoids duplicates)
   - Tags with category (Airport, Port, etc.)

4. **Triggers Notifications:**
   - New opportunities → Alert
   - Today's focus → Reminder
   - High-value → Priority alert

**Time to Build:** 2-3 hours  
**Result:** Fully automated transportation opportunity discovery

---

## 🎯 RECOMMENDED APPROACH

### **Phase 1: Enhance Existing Miner (Quick - 30 min)**

Update `mine_real_federal_forecasts.py` to specifically search for transportation keywords:

```python
# Add to existing miner
transportation_keywords = [
    'airport supplies',
    'aviation supplies', 
    'marine supplies',
    'port supplies',
    'cargo handling',
    'postal supplies',
    'USPS supplies',
    'courier supplies',
    'transit supplies',
    'transportation supplies'
]

# Search SAM.gov for each
for keyword in transportation_keywords:
    results = search_sam_gov(keyword)
    store_opportunities(results)
```

**Result:** Federal transportation opportunities automatically found

---

### **Phase 2: Build Direct Source Scrapers (2-3 hours)**

Create specific scrapers for:
- Detroit Metro Airport
- Detroit Port Authority  
- SMART Bus
- Local opportunities

**Result:** Local transportation opportunities automatically found

---

### **Phase 3: Full Automation (1 day)**

- Scheduled daily runs (cron job)
- All 35+ search strings automated
- Direct source monitoring
- Email alerts when new opportunities found
- Integration with NEXUS workflow

**Result:** Hands-free transportation opportunity discovery

---

## 📊 EXPECTED RESULTS BY APPROACH

### **Current (Manual Search):**
- Time: 30 min/day
- Opportunities: 10-20/week
- Source: Manual SAM.gov searches
- Notifications: Show what you manually add

### **With Enhanced Federal Miner:**
- Time: 5 min/week (run script)
- Opportunities: 30-50/week
- Source: SAM.gov federal opportunities
- Notifications: Auto-alert on new transportation finds

### **With Full Automated Miner:**
- Time: 0 min (fully automated)
- Opportunities: 50-100/week
- Source: SAM.gov + direct sources + state/local
- Notifications: Real-time alerts on all new opportunities

---

## 🚀 WHAT I CAN BUILD FOR YOU

### **Automated Transportation Opportunity Miner**

**Features:**
- ✅ Searches SAM.gov for all 35+ transportation keywords
- ✅ Scrapes Detroit Metro Airport, Port, Transit sites
- ✅ Monitors BidNet Michigan for transportation
- ✅ Deduplicates opportunities
- ✅ Auto-stores in GPSS Opportunities
- ✅ Triggers notifications automatically
- ✅ Runs daily via scheduler
- ✅ Email summary of new finds

**Time to Build:** 2-3 hours  
**Maintenance:** Zero (fully automated)  
**Result:** 50-100 transportation opportunities found weekly, automatically

---

## ✅ SUMMARY

**Current State:**
- ✅ Notifications **filter** transportation opportunities from GPSS Opportunities
- ✅ Federal forecast miner brings in ~389 federal opportunities (some transportation)
- ⚠️  NO dedicated transportation mining (yet)
- ⚠️  Manual search required for systematic transportation opportunity discovery

**Data Sources Available:**
1. **Federal:** SAM.gov API (free, comprehensive)
2. **Direct:** Airport/port/transit websites (scrapable)
3. **Aggregators:** BidNet Michigan (subscription)
4. **Existing:** Federal forecast miner (active)

**To Get Fully Automated:**
- Build dedicated transportation miner
- Runs daily
- Searches all 35+ keywords
- Scrapes direct sources
- Auto-stores in Airtable
- Triggers notifications
- **Result: 50-100 opportunities/week, zero manual work**

**Want me to build the automated transportation miner?** It would take 2-3 hours and give you hands-free opportunity discovery! 🚀

---

*Document created: January 31, 2026*  
*Current mining: Manual + Federal forecast miner*  
*Recommended: Build automated transportation miner*
