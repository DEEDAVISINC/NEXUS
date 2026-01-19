# 🚨 ADD THESE FIELDS TO AIRTABLE RIGHT NOW

## THE PROBLEM:

Your opportunities are importing, but you can't see the RFP details because **the fields don't exist in Airtable yet!**

---

## ✅ SOLUTION: Add These Fields to Your Airtable

Go to your Airtable: https://airtable.com/appaJZqKVUn3yJ7ma/tblWO4yncFrkI5WpW

### **Step 1: Click the "+" button to add new fields**

### **Step 2: Add these fields EXACTLY as shown:**

| Field Name | Type | Description |
|------------|------|-------------|
| **Agency** | Single line text | Agency name (e.g., "Department of Defense") |
| **Description** | Long text | Full RFP description |
| **Set Aside** | Single line text | Set-aside type (EDWOSB, WOSB, 8(a), etc.) |
| **NAICS** | Single line text | NAICS codes |
| **State** | Single line text | Performance state |
| **Notice Type** | Single line text | Type of notice (Solicitation, Award, etc.) |
| **Source URL** | URL | Link to original RFP |
| **Response Deadline** | Date | When response is due |
| **Posted Date** | Date | When opportunity was posted |
| **Contract Value** | Number | Estimated contract value |
| **Location** | Single line text | Performance location |

---

## 📋 QUICK COPY-PASTE LIST:

Just add these field names (copy-paste each one):

```
Agency
Description
Set Aside
NAICS
State
Notice Type
Source URL
Response Deadline
Posted Date
Contract Value
Location
```

---

## ⚡ AFTER YOU ADD THE FIELDS:

Run this command to re-import opportunities with FULL data:

```bash
cd "/Users/deedavis/NEXUS BACKEND" && python3 reimport_opportunities_full_data.py && python3 -c "
import requests
r = requests.post('http://localhost:8000/gpss/mining/search-govcon-api', json={}, timeout=60)
print(f'Imported {r.json()[\"imported\"]} opportunities with FULL data')
"
```

---

## 🎯 WHAT YOU'LL SEE AFTER:

Instead of:
```
Name: Unknown
Agency: N/A
RFP#: N/A
```

You'll see:
```
Name: "IT Services for Department of Defense"
Agency: "Department of Defense"  
RFP#: "W52P1J-26-T-0123"
Deadline: "2026-02-15"
Description: "The Department of Defense requires..."
Set Aside: "EDWOSB"
State: "Virginia"
Value: "$500,000"
```

---

## 🚨 THIS IS CRITICAL!

**Without these fields, you can't see:**
- What agency posted the RFP
- What the opportunity is about
- Where it's located
- When it's due
- If it's a set-aside for women-owned businesses
- The link to apply

**You NEED these fields to actually use the system!**

---

## ⏰ DO THIS NOW:

1. **Open Airtable** → https://airtable.com/appaJZqKVUn3yJ7ma/tblWO4yncFrkI5WpW
2. **Click "+"** to add each field
3. **Add all 11 fields** from the list above
4. **Re-run the import** (command above)
5. **Refresh your frontend**

**Estimated time: 5 minutes**

---

## 💡 WHY THIS HAPPENED:

When we set up the system, we created the table with only basic fields. The mining code expects these detailed fields to exist, but they need to be manually added in Airtable first.

This is a ONE-TIME setup. Once you add these fields, every future import will automatically populate them with full RFP data.

---

**Status**: 🔴 CRITICAL - Cannot see RFP details without these fields  
**Action**: Add fields to Airtable NOW  
**Time**: 5 minutes  
**Priority**: HIGHEST

**DO THIS NOW before anything else!** 🚨
