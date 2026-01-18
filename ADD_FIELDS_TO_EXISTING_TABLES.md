# 🎯 ADD FIELDS TO EXISTING TABLES

**Both tables already exist! You just need to add fields.**

**Time: 10-15 minutes**

---

## TABLE 1: VENDOR PORTAL (Already Exists - Add Fields)

**Current status:** Has 3 records, only has "Added Date" field

### Add These 9 Fields:

| # | Field Name | Field Type | Options |
|---|------------|-----------|---------|
| 1 | **Portal Name** | Single line text | |
| 2 | **Portal URL** | URL | |
| 3 | **Portal Type** | Single select | `Federal`, `State`, `Local`, `Cooperative` |
| 4 | **Auto-Mining Enabled** | Checkbox | |
| 5 | **Search Enabled** | Checkbox | |
| 6 | **Description** | Long text | |
| 7 | **Keywords** | Long text | |
| 8 | **Category** | Single select | `Government`, `Commercial`, `Cooperative` |
| 9 | **Icon** | Single line text | |

**How to add:**
1. Open your VENDOR PORTAL table in Airtable
2. Click the "+" button to add each field
3. Name it exactly as shown above
4. Select the correct field type
5. Add options for Single select fields

---

## TABLE 2: Mining Targets (Already Exists - Verify/Add Missing Fields)

**Current status:** Exists, 0 records

### Make Sure It Has These 8 Fields (Add Any Missing):

| # | Field Name | Field Type | Options |
|---|------------|-----------|---------|
| 1 | **Target Name** | Single line text | |
| 2 | **Target URL** | URL | |
| 3 | **Source Type** | Single select | `Intelligence`, `Marketplace`, `Archive`, `News`, `Portal` |
| 4 | **Active** | Checkbox | |
| 5 | **Description** | Long text | |
| 6 | **Keywords** | Long text | |
| 7 | **Scraping Method** | Single select | `API`, `Web Scraping`, `RSS Feed`, `Manual` |
| 8 | **Last Scraped** | Date & time | |

**How to verify:**
1. Open your Mining Targets table
2. Check if each field above exists
3. Add any that are missing

---

## ✅ AFTER ADDING FIELDS

Run this to populate both tables with government portals:

```bash
cd "/Users/deedavis/NEXUS BACKEND"
python3 initialize_portals.py
```

**This will add:**
- ✅ SAM.gov
- ✅ GSA eBuy
- ✅ DIBBS (Defense)
- ✅ Unison Marketplace
- ✅ SBA SubNet
- ✅ NECO Cooperative

Plus 5 intelligence sources (FPDS, USASpending, etc.)

---

## 📋 QUICK CHECKLIST

- [ ] Add 9 fields to VENDOR PORTAL table (5 min)
- [ ] Verify/add fields to Mining Targets table (3 min)
- [ ] Run `python3 initialize_portals.py` (2 min)
- [ ] Verify data populated in both tables

**Total Time: ~10 minutes**

---

## 🎯 SUMMARY

**You DON'T need to create any new tables!**

Both tables exist. You just need to:
1. Add fields to VENDOR PORTAL
2. Verify fields in Mining Targets  
3. Run the populate script

That's it! 🚀
