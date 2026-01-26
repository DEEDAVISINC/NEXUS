# SUBSCRIBE TO BID SOURCES
**Get opportunities flowing to your automation**

**Your Email:** `bids.deedavisinc@gmail.com`

---

## 🎯 SUBSCRIBE TO THESE (15 Minutes Total)

### **1. SAM.gov (Federal Contracts)** ⭐ Most Important
**URL:** https://sam.gov

**Steps:**
1. Create account (or log in)
2. Go to "Contract Opportunities" 
3. Click "Advanced Search"
4. Enter your NAICS codes or keywords:
   - Office supplies
   - Landscaping
   - Janitorial
   - Industrial supplies
5. Click "Follow This Search"
6. Set email to: `bids.deedavisinc@gmail.com`
7. Choose "Daily Digest" or "Immediate"

**Done! You'll get federal opportunities daily.**

---

### **2. BidNet Direct (State & Local)**
**URL:** https://bidnetdirect.com

**Steps:**
1. Create account with: `bids.deedavisinc@gmail.com`
2. Select your state: Michigan
3. Add nearby states: Ohio, Indiana, Illinois
4. Select categories:
   - Office supplies
   - Landscaping/grounds maintenance
   - Janitorial services
   - Medical supplies
5. Set email notifications: Daily

**Done! You'll get state/local opportunities.**

---

### **3. PlanetBids (Municipal)**
**URL:** https://planetbids.com

**Steps:**
1. Create vendor account
2. Email: `bids.deedavisinc@gmail.com`
3. Select Michigan
4. Choose product categories
5. Enable daily notifications

---

### **4. Michigan SIGMA VSS (State of Michigan)**
**URL:** https://www.michigan.gov/sigmavss

**Steps:**
1. Register as vendor
2. Email: `bids.deedavisinc@gmail.com`
3. Select your commodity codes
4. Enable email alerts

---

### **5. Local Governments (Quick Adds)**

**Detroit:**
- https://detroitmi.gov/government/departments/procurement
- Sign up for bid notifications

**Oakland County:**
- https://oakgov.com/purchasing
- Subscribe to bidding opportunities

**Wayne County:**
- https://waynecounty.com/departments/procurement
- Email alerts

---

## ✅ WHAT HAPPENS NEXT

After you subscribe:
1. Bid notifications start arriving at `bids.deedavisinc@gmail.com`
2. NEXUS automation checks every 30 minutes (or hourly)
3. AI extracts opportunity details
4. Creates Airtable records automatically
5. Sends diversity inquiries (if high-value)
6. You review opportunities in Airtable

---

## 🔄 SCHEDULE THE AUTOMATION

### **Option 1: Mac Cron (Run Every Hour)**

```bash
# Edit crontab
crontab -e

# Add this line:
0 * * * * cd "/Users/deedavis/NEXUS BACKEND" && /usr/local/bin/python3 nexus_email_automation.py >> /Users/deedavis/NEXUS\ BACKEND/nexus_email.log 2>&1
```

**This runs every hour at :00 (9:00, 10:00, 11:00, etc.)**

---

### **Option 2: Manual Check (For Now)**

Just run when you want to check:
```bash
cd "/Users/deedavis/NEXUS BACKEND"
python3 nexus_email_automation.py
```

---

## 📊 MONITORING

**Check the log:**
```bash
tail -f /Users/deedavis/NEXUS\ BACKEND/nexus_email.log
```

**Check Airtable:**
- Open your GPSS OPPORTUNITIES table
- Look for new records with "Source Status" = "NEW"
- HIGH VALUE FLAG = true for contracts ≥$50K

---

## 🎉 YOU'RE LIVE!

Email automation is working! Subscribe to 2-3 sources today and you'll start seeing opportunities automatically populated in Airtable.

**Test it:** 
1. Subscribe to SAM.gov (5 min)
2. Wait 24 hours
3. Run: `python3 nexus_email_automation.py`
4. Check GPSS OPPORTUNITIES table for new records!

---

*Created: January 25, 2026*
*Your automation is LIVE and ready!* ✅
