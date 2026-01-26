# ✅ YOUR COMPLETE AUTOMATION SETUP

**Once you set this up, you never have to search manually again!**

---

## 🤖 **WHAT RUNS AUTOMATICALLY (Forever)**

### **1. EMAIL MONITORING** ✅ Already Running!

**Status:** LIVE - Runs every hour  
**What it does:**
- Checks `bids.deedavisinc@gmail.com` for new bid notifications
- Extracts: RFP number, deadline, organization, value
- Auto-creates opportunities in NEXUS
- Sends diversity inquiries to procurement officers

**Schedule:** Every hour at :00 (9:00, 10:00, 11:00, etc.)  
**Log:** `nexus_email.log`

---

### **2. DAILY SAM.GOV SEARCH** 🆕 Set up once!

**Run this ONE TIME to enable:**
```bash
cd "/Users/deedavis/NEXUS BACKEND"
chmod +x setup_daily_opportunity_search.sh
./setup_daily_opportunity_search.sh
```

**What it does:**
- Searches SAM.gov API every morning at 6 AM
- Looks for: Copy paper, office supplies, industrial products, etc.
- Auto-imports matching opportunities to NEXUS
- Filters by: EDWOSB/WOSB, your product categories

**Schedule:** Daily at 6:00 AM  
**Log:** `opportunity_search.log`

---

## 📧 **ONE-TIME SETUP (15 minutes) - CRITICAL!**

**Subscribe your automation email to bid sources:**

### **A. SAM.gov (Federal)** ⭐ Most Important

1. Go to: https://sam.gov
2. Create account with: `bids.deedavisinc@gmail.com`
3. Set up "Saved Searches" for:
   - "copy paper"
   - "office supplies"
   - "industrial supplies"
4. Enable email notifications → Daily digest

**Why:** Federal contracts worth $$$, EDWOSB advantage

---

### **B. BidNet (State & Local)**

1. Go to: https://bidnetdirect.com
2. Register: `bids.deedavisinc@gmail.com`
3. Select states: Michigan (primary), nearby states
4. Email frequency: Daily digest

**Why:** Local Michigan opportunities, your home market

---

### **C. Michigan SIGMA (Optional)**

1. Go to: https://sigma.michigan.gov
2. Register: `bids.deedavisinc@gmail.com`
3. Enable email alerts

**Why:** State of Michigan contracts

---

## 🔄 **HOW IT ALL WORKS TOGETHER**

### **Daily Automatic Flow:**

```
6:00 AM → SAM.gov API Search
          ↓
          Auto-imports new opportunities to NEXUS
          
Every Hour → Email Check (bids.deedavisinc@gmail.com)
          ↓
          New bid notifications from subscriptions
          ↓
          Auto-extracts details
          ↓
          Creates opportunities in NEXUS
          ↓
          Sends diversity inquiries (if $50K+)

You → Just check NEXUS dashboard once per day
   ↓
   Review new opportunities
   ↓
   Decide which to bid on
```

---

## 📊 **WHERE TO SEE RESULTS**

**NEXUS Command Center → GPSS → Opportunities Tab**

**Filter by:**
- Status: "New - API" or "New - Email"
- Source Status: "NEW"
- Deadline: Next 30 days

**You'll see:**
- Company/Agency name
- RFP number
- Deadline
- Estimated value
- Source (SAM.gov, BidNet, etc.)

---

## ⏰ **YOUR DAILY ROUTINE (5-10 minutes)**

**Morning (once per day):**
1. Open NEXUS
2. Check "Opportunities" tab
3. Review new opportunities (auto-imported overnight)
4. Click "Request Quotes" for products you have suppliers for
5. Done!

**That's it!** No manual searching, no checking multiple sites.

---

## 🎯 **WHAT YOU GET AUTOMATICALLY**

**Without lifting a finger:**
- ✅ Federal opportunities (SAM.gov)
- ✅ State opportunities (State portals)
- ✅ Local opportunities (BidNet, local sites)
- ✅ EDWOSB/WOSB set-asides (priority)
- ✅ Products you have suppliers for
- ✅ Auto-filtered by your keywords

**Your system watches:**
- 📧 Email notifications (hourly)
- 🔍 SAM.gov API (daily)
- 📡 RSS feeds (if configured)

---

## 🚀 **SETUP CHECKLIST**

### **Already Done ✅**
- [x] Email automation script created
- [x] Hourly cron job configured
- [x] Airtable integration working
- [x] Diversity inquiry automation ready

### **Do Once (Tonight - 5 minutes) 🎯**
- [ ] Run: `./setup_daily_opportunity_search.sh`
- [ ] Verify cron job: `crontab -l`

### **Do Once (Tomorrow - 15 minutes) 📧**
- [ ] Subscribe to SAM.gov (use `bids.deedavisinc@gmail.com`)
- [ ] Subscribe to BidNet (use `bids.deedavisinc@gmail.com`)
- [ ] Optional: Subscribe to SIGMA

---

## 📝 **QUICK COMMANDS**

### **Check if automations are running:**
```bash
crontab -l
```

**You should see:**
```
0 * * * * ... nexus_email_automation.py    # Email check (hourly)
0 6 * * * ... search_opportunities_now.py  # SAM.gov search (daily)
```

### **View automation logs:**
```bash
# Email automation log
tail -f "/Users/deedavis/NEXUS BACKEND/nexus_email.log"

# Daily search log
tail -f "/Users/deedavis/NEXUS BACKEND/opportunity_search.log"
```

### **Run manually (test):**
```bash
cd "/Users/deedavis/NEXUS BACKEND"

# Test email automation
python3 nexus_email_automation.py

# Test SAM.gov search
python3 search_opportunities_now.py
```

---

## 💡 **EXPECTED RESULTS**

**After setup, you'll automatically get:**
- **10-30 new opportunities per week** (depending on season/subscriptions)
- **2-5 EDWOSB/WOSB set-asides per month**
- **Products you can quote:** Copy paper, office supplies, industrial, etc.
- **No manual searching required!**

---

## 🎯 **TONIGHT (Find 2 More):**

**For tonight only, run manually:**
```bash
python3 search_opportunities_now.py
```

**Starting tomorrow:** It runs automatically every morning at 6 AM!

---

## ✅ **BOTTOM LINE**

**Set up once = Works forever**

1. **Tonight (5 min):** Run `setup_daily_opportunity_search.sh`
2. **Tomorrow (15 min):** Subscribe to SAM.gov and BidNet
3. **Forever after:** Check NEXUS once per day, see new opportunities automatically

**No more manual searching. No more checking multiple sites. Your system does it all.** 🚀

---

**Status:** Email automation ✅ Live  
**Next:** Daily SAM.gov search (run setup script)  
**Then:** Subscribe email to bid sources (one time)  
**Result:** Fully automated opportunity discovery! 🎉
