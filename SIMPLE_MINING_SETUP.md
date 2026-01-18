# 🎯 SIMPLE MINING TABLES SETUP

**Time: 15 minutes**  
**What you need: 1 new table in Airtable**

---

## TABLE 1: VENDOR PORTALS (Create This)

### Step 1: Create Table
1. Go to Airtable → Your NEXUS base
2. Click "Add table" → Name it: **VENDOR PORTALS**

### Step 2: Add These 10 Fields (Minimum Required)

| Field Name | Type | Options |
|------------|------|---------|
| **Portal Name** | Single line text | (primary field) |
| **Portal URL** | URL | |
| **Portal Type** | Single select | Federal, State, Local, Cooperative |
| **Auto-Mining Enabled** | Checkbox | |
| **Search Enabled** | Checkbox | |
| **Description** | Long text | |
| **Keywords** | Long text | |
| **Category** | Single select | Government, Commercial, Cooperative |
| **Icon** | Single line text | |
| **Last Checked** | Date & time | |

**That's it!** Just 10 fields.

---

## TABLE 2: MINING TARGETS (Already Exists - Verify)

### Check if it has these 8 fields:

| Field Name | Type |
|------------|------|
| **Target Name** | Single line text |
| **Target URL** | URL |
| **Source Type** | Single select |
| **Active** | Checkbox |
| **Description** | Long text |
| **Keywords** | Long text |
| **Scraping Method** | Single select |
| **Last Scraped** | Date & time |

If missing any, add them. Otherwise you're done!

---

## ✅ AFTER SETUP

Run this to auto-populate portals:

```bash
cd "/Users/deedavis/NEXUS BACKEND"
python3 initialize_portals.py
```

This adds:
- SAM.gov
- GSA eBuy  
- DIBBS
- Unison
- SubNet
- NECO

**Done!** 🚀

---

## 📋 CHECKLIST

- [ ] Create VENDOR PORTALS table (10 fields)
- [ ] Verify Mining Targets has 8 fields
- [ ] Run initialize script
- [ ] Check tables have data

**Time: ~15 minutes total**
