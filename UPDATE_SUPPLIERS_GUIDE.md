# UPDATE SUPPLIERS WITH COMPLETE INFORMATION

## 🎯 ISSUE

Your GPSS SUBCONTRACTORS table currently has:
- ✅ 21 supplier company names
- ❌ Missing: Service Type, City, State, Phone, Email, Website, Status, Notes, Contact Date, Location, Rating

## ✅ SOLUTION (2 minutes)

I've created **`COMPLETE_Suppliers_Import.csv`** with ALL the information for all 21 suppliers.

### **Option 1: Re-import CSV (EASIEST - 2 minutes)**

1. **Open your Airtable base**
2. **Go to GPSS SUBCONTRACTORS table**
3. **Click the dropdown arrow** next to table name
4. **Choose "Import data" → "CSV file"**
5. **Select:** `COMPLETE_Suppliers_Import.csv`
6. **Choose:** "Update existing records"
7. **Match on:** "COMPANY NAME"
8. **Import**

**Result:** All 21 suppliers will be updated with complete info + new fields will be auto-created!

---

### **Option 2: Add Fields Manually Then Re-run Script (10 minutes)**

If you prefer to add fields manually:

**Add these 10 fields to GPSS SUBCONTRACTORS:**

| Field Name | Type |
|-----------|------|
| Service Type | Single line text |
| Location | Single line text |
| City | Single line text |
| State | Single line text |
| Phone | Phone |
| Email | Email |
| Website | URL |
| Status | Single select (Active, Not Yet Contacted, Declined, Active - Quote Received) |
| Rating | Number (0-5, 1 decimal) |
| Notes | Long text |
| Contact Date | Date |

Then re-run: `python3 update_suppliers_complete.py`

---

## 📊 WHAT YOU'LL GET

After updating, each supplier will have:

**Example - Mopec:**
- Company Name: Mopec
- Service Type: Medical/Morgue Supplies
- Location: National
- Email: (blank)
- Status: Active - Quote Received
- Rating: 5
- Notes: Quote received by 1/22: $762.92 + shipping for Oak-0000001089. Quote expires 3/22/2026.
- Contact Date: 2026-01-22

**Example - Fisher Sand & Gravel:**
- Company Name: Fisher Sand & Gravel
- Service Type: Aggregate Materials
- Location: Michigan (serves Midland, Livonia)
- State: MI
- Status: Active
- Notes: Faxed quote request on 1/24 for ITB 4617, 4616, 4615. Open till 12:30 PM Saturdays.
- Contact Date: 2026-01-24

---

## 💡 RECOMMENDATION

**Use Option 1 (CSV Re-import)** - It's faster and will automatically:
- ✅ Update all 21 existing records
- ✅ Add all missing fields
- ✅ Populate all data

Takes 2 minutes vs 10 minutes for manual field creation.

---

**File ready:** `COMPLETE_Suppliers_Import.csv`
