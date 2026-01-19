# Which Table Needs These Fields?

## 🎯 TABLE: `GPSS OPPORTUNITIES`

---

## Direct Link:
**https://airtable.com/appaJZqKVUn3yJ7ma/tblWO4yncFrkI5WpW**

---

## How to Find It:

1. **Open your Airtable Base** (the link above)
2. **Look for the table** named `GPSS OPPORTUNITIES` in the left sidebar
3. **This is the table** where all government contract opportunities are stored

---

## What This Table Does:

This table stores all the government opportunities (RFPs, RFQs, solicitations) that your system finds through:
- GovCon API
- SAM.gov API
- RSS Feeds
- Web Scraping
- State/Local mining

**This is the MAIN table for your opportunity pipeline.**

---

## Current Fields in the Table:

Right now it only has:
- ✅ Name
- ✅ Status
- ✅ Deadline
- ✅ RFP NUMBER

---

## Fields You Need to ADD:

Add these **11 fields** to the `GPSS OPPORTUNITIES` table:

| Field Name | Field Type |
|------------|------------|
| Agency | Single line text |
| Description | Long text |
| Set Aside | Single line text |
| NAICS | Single line text |
| State | Single line text |
| Notice Type | Single line text |
| Source URL | URL |
| Response Deadline | Date |
| Posted Date | Date |
| Contract Value | Number |
| Location | Single line text |

---

## How to Add Fields:

### Step 1: Open the Table
Click this link: https://airtable.com/appaJZqKVUn3yJ7ma/tblWO4yncFrkI5WpW

### Step 2: Add Each Field
1. Click the **"+"** button at the top right of the table (next to the last column)
2. Select the **field type** (see table above)
3. Name it **exactly as shown** (e.g., "Agency", "Description", etc.)
4. Click **"Create field"**
5. Repeat for all 11 fields

---

## Why This Table?

The **GPSS OPPORTUNITIES** table is:
- Where GovCon API saves opportunities
- Where SAM.gov API saves opportunities  
- Where your frontend reads opportunities from
- Where you filter/search opportunities
- What feeds into ATLAS PM (project management)
- What generates invoices when you win

**This is the heart of your opportunity tracking system.**

---

## After You Add the Fields:

Once you add these 11 fields, you need to:

1. **Re-import opportunities** to populate the new fields:
```bash
cd "/Users/deedavis/NEXUS BACKEND"
python3 reimport_opportunities_full_data.py
```

2. **Refresh your frontend** to see the full RFP details

---

## ✅ Quick Checklist:

- [ ] Open GPSS OPPORTUNITIES table
- [ ] Add "Agency" field (Single line text)
- [ ] Add "Description" field (Long text)
- [ ] Add "Set Aside" field (Single line text)
- [ ] Add "NAICS" field (Single line text)
- [ ] Add "State" field (Single line text)
- [ ] Add "Notice Type" field (Single line text)
- [ ] Add "Source URL" field (URL)
- [ ] Add "Response Deadline" field (Date)
- [ ] Add "Posted Date" field (Date)
- [ ] Add "Contract Value" field (Number)
- [ ] Add "Location" field (Single line text)
- [ ] Run reimport script
- [ ] Refresh frontend

---

**Table**: GPSS OPPORTUNITIES  
**Location**: https://airtable.com/appaJZqKVUn3yJ7ma/tblWO4yncFrkI5WpW  
**Action**: Add 11 fields  
**Time**: 5 minutes
