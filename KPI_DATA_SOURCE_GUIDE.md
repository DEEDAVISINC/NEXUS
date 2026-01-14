# 📊 NEXUS KPI DATA SOURCE GUIDE

## Where Your Dashboard Numbers Come From

This guide shows exactly where each KPI (Key Performance Indicator) on your NEXUS Command Center gets its data.

---

## 🎯 **DASHBOARD KPI CARDS**

### **1. Active Opportunities** 🎯
**Shows:** Number of current RFPs/opportunities
**Data Source:** 
- **Airtable:** GPSS → "Opportunities" table
- **Calculation:** Count of all records where Status ≠ "Closed" or "Lost"
- **Updates:** Every 30 seconds (auto-refresh)
- **Click Action:** Opens GPSS system to view opportunities

**How to see the data:**
1. Click the "Active Opportunities" card
2. You'll go to GPSS → Dashboard
3. Click "Opportunities" tab to see all records

---

### **2. Total Contacts** 👥
**Shows:** Total number of contacts across all opportunities
**Data Source:**
- **Airtable:** GPSS → "Contacts" table  
- **Calculation:** Count of all contact records
- **Updates:** Every 30 seconds (auto-refresh)
- **Click Action:** Opens GPSS system to manage contacts

**How to see the data:**
1. Click the "Total Contacts" card
2. You'll go to GPSS → Dashboard
3. Click "Contacts" tab to see all 4 contacts

**Your current data:**
- You have **4 contacts** in your Contacts table
- These are the people associated with your opportunities
- Could be contracting officers, project managers, etc.

---

### **3. Active Projects** 📋
**Shows:** Number of ongoing projects in ATLAS PM
**Data Source:**
- **Airtable:** ATLAS → "ATLAS Projects" table
- **Calculation:** Count of all records where Status ≠ "Completed" or "Cancelled"
- **Updates:** Every 30 seconds (auto-refresh)
- **Click Action:** Opens ATLAS PM system to view projects

**How to see the data:**
1. Click the "Active Projects" card
2. You'll go to ATLAS PM → Dashboard
3. Click "Projects" tab to see all active projects

---

### **4. Revenue Pipeline** 💰
**Shows:** Total value of all opportunities in your pipeline
**Data Source:**
- **Airtable:** GPSS → "Opportunities" table → "Contract Value" field
- **Calculation:** Sum of all opportunity values where Status = "Pursuing" or "Submitted"
- **Updates:** Every 30 seconds (auto-refresh)
- **Click Action:** Opens GPSS system to view pipeline

**How to see the data:**
1. Click the "Revenue Pipeline" card
2. You'll go to GPSS → Dashboard
3. Click "Opportunities" tab
4. See the "Contract Value" column for each opportunity

**Example:**
- Opportunity 1: $250,000
- Opportunity 2: $500,000
- Opportunity 3: $1,200,000
- **Total Pipeline: $1,950,000** (shows as "$1.9M")

---

## 🔄 **HOW THE DATA FLOWS**

```
┌─────────────────────────────────────┐
│        AIRTABLE DATABASE            │
│  (Your NEXUS Command Center Base)  │
├─────────────────────────────────────┤
│  • Opportunities Table              │
│  • Contacts Table                   │
│  • ATLAS Projects Table             │
│  • Products Table                   │
│  • Invoices Table                   │
│  • AI Conversations Table           │
└──────────────┬──────────────────────┘
               │
               │ API Call Every 30 Seconds
               ↓
┌─────────────────────────────────────┐
│       PYTHON BACKEND (Port 8000)    │
│  Endpoint: /dashboard/stats         │
├─────────────────────────────────────┤
│  1. Queries Airtable                │
│  2. Counts records                  │
│  3. Calculates totals               │
│  4. Returns JSON data               │
└──────────────┬──────────────────────┘
               │
               │ Returns Stats Object
               ↓
┌─────────────────────────────────────┐
│    REACT FRONTEND (Port 3000)       │
│  Component: LandingPage.tsx         │
├─────────────────────────────────────┤
│  1. Receives stats data             │
│  2. Displays in KPI cards           │
│  3. Makes cards clickable           │
│  4. Shows hover tooltips            │
└─────────────────────────────────────┘
```

---

## 📊 **SYSTEM-SPECIFIC STATS**

### **GPSS System Card:**
- **Opportunities:** Count from Opportunities table
- **Pipeline:** Sum of Contract Values
- **Contacts:** Count from Contacts table

### **DDCSS System Card:**
- **Pipeline:** Count from Prospects table
- **Responses:** Count from AI Conversations where System = DDCSS
- **Sectors:** Always 6 (pre-loaded sectors)

### **ATLAS PM System Card:**
- **Projects:** Count from ATLAS Projects table
- **RFPs Analyzed:** Count of RFP Analysis records
- **Value:** Sum of all project budgets

### **Invoices System Card:**
- **Total Invoices:** Count from Invoices table
- **Revenue:** Sum of paid invoices
- **Pending:** Count where Status = "Pending" or "Sent"

---

## 🎯 **NEW FEATURES (Just Added!)**

### **✅ Clickable KPI Cards**
- Click any KPI card to jump to the relevant system
- Example: Click "Total Contacts" → Opens GPSS → Contacts tab

### **✅ Hover Tooltips**
- Hover over any card to see data source
- Shows which Airtable table the data comes from
- Explains what you'll see when you click

### **✅ Visual Feedback**
- Cards scale up on hover
- Show data source text on hover
- Smooth animations

---

## 🔍 **HOW TO VERIFY YOUR DATA**

### **To Check "Total Contacts: 4":**

**Method 1: Through NEXUS UI**
1. Go to NEXUS Command Center
2. Click "Total Contacts" card
3. Navigate to GPSS → Contacts tab
4. Count the contacts in the table

**Method 2: Through Airtable**
1. Open Airtable in browser
2. Go to "NEXUS Command Center" base
3. Open "Contacts" table
4. See the 4 records directly

**Method 3: Through API (Developer)**
```bash
curl http://localhost:8000/gpss/contacts
```

---

## ⚡ **REAL-TIME UPDATES**

All KPI data updates automatically:
- **Frequency:** Every 30 seconds
- **Manual Refresh:** Click the "REFRESH" button
- **Visual Indicator:** Shows "SYNCING..." during refresh
- **Last Updated:** Timestamp shown in header

---

## 🛠️ **TROUBLESHOOTING**

### **KPI Shows 0 but I have data:**
- Click the card to navigate to the system
- Check if records exist in that table
- Verify Status field isn't filtering them out
- Click REFRESH button manually

### **Data Not Updating:**
- Check backend server is running (port 8000)
- Look for errors in browser console (F12)
- Verify Airtable API key is valid
- Check internet connection

### **Card Not Clickable:**
- Refresh browser page (Cmd+Shift+R)
- Clear browser cache
- Make sure frontend compiled successfully

---

## 📈 **WHAT THE NUMBERS MEAN**

### **Active Opportunities = Potential Contracts**
- Every opportunity is a government RFP you're tracking
- More opportunities = more chances to win work
- Track these from discovery to award

### **Total Contacts = Your Network**
- Key decision makers and stakeholders
- Contracting officers, program managers
- Build relationships with these people

### **Active Projects = Current Work**
- Contracts you've won and are executing
- Projects in progress
- Revenue being delivered

### **Revenue Pipeline = Potential Income**
- Total value of all opportunities
- NOT guaranteed money (yet!)
- Shows business potential

---

## 🎯 **USING KPIs TO RUN YOUR BUSINESS**

### **Daily Check:**
- Glance at dashboard each morning
- Look for changes in numbers
- Click cards to see details

### **Weekly Review:**
- Compare numbers week-over-week
- Identify trends (going up or down?)
- Adjust strategy accordingly

### **Monthly Planning:**
- Set KPI targets for next month
- Track progress toward goals
- Celebrate wins!

---

## 📊 **EXAMPLE SCENARIO**

**You see: "Total Contacts: 4"**

**What this means:**
- You have 4 people in your contact database
- These might be from different agencies
- Each contact is linked to opportunities

**How to grow this number:**
- Attend industry days
- Network at government events
- Add contracting officers from SAM.gov
- Import contacts from business cards
- Add key decision makers

**Goal:** 
- 10 contacts by end of month
- 50 contacts by end of quarter
- Build your government network!

---

## ✅ **SUMMARY**

Your dashboard KPIs are:
- ✅ **Live data** from Airtable
- ✅ **Clickable** to view details
- ✅ **Auto-updating** every 30 seconds
- ✅ **Accurate** real-time counts
- ✅ **Actionable** information

**Use them to:**
- Track business health
- Make decisions
- Monitor progress
- Grow your company

**Click any card to dive deeper into the data!** 🚀
