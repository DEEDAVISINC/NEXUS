# NEXUS AIRTABLE QUICK SETUP GUIDE
**Get your bid tracking into Airtable in 15 minutes**

---

## 🎯 WHAT WE'RE DOING

You have 12 active bids with 21+ suppliers tracked in markdown files. This guide will get ALL that data into Airtable so you never have to manually track bids again.

---

## ⚡ QUICK START (3 Steps)

### STEP 1: Add Fields to Your Tables (10 min)

Open your Airtable base and add these fields to each table:

#### **GPSS OPPORTUNITIES Table**

You already have:
- Name ✅
- RFP NUMBER ✅
- Deadline ✅
- Status ✅

**Add these fields:**

| Field Name | Type | Options |
|-----------|------|---------|
| Agency | Single line text | - |
| Estimated Value | Currency | USD, No decimals |
| Est Profit | Currency | USD, No decimals |
| Priority | Single select | Options: CRITICAL, HIGH, READY, URGENT, CONDITIONAL, Future |
| Suppliers Contacted | Long text | - |
| Quotes Status | Single line text | - |
| Description | Long text | - |
| Submission Method | Single line text | - |

---

#### **GPSS SUBCONTRACTORS Table**

You have:
- (some auto fields) ✅

**Add ALL these fields:**

| Field Name | Type | Options |
|-----------|------|---------|
| Company Name | Single line text | (Make this PRIMARY field) |
| Service Type | Single line text | - |
| Location | Single line text | - |
| Email | Email | - |
| Phone | Phone | - |
| Website | URL | - |
| Status | Single select | Options: Active, Not Yet Contacted, Declined, Active - Quote Received |
| Rating | Number | 0-5, 1 decimal place |
| Notes | Long text | - |
| Contact Date | Date | Include time |

---

#### **GPSS SUBCONTRACTOR QUOTES Table**

You have:
- QUOTE ID ✅
- CREATED DATE ✅

**Add these fields:**

| Field Name | Type | Options |
|-----------|------|---------|
| Opportunity | Link to another record | Link to: GPSS OPPORTUNITIES |
| Subcontractor | Link to another record | Link to: GPSS SUBCONTRACTORS |
| Status | Single select | Options: Pending, Received, Declined, Selected |
| RFQ Sent Date | Date | - |
| Quote Due Date | Date | - |
| Quote Amount | Currency | USD |
| Notes | Long text | - |

---

### STEP 2: Import Your Data (3 min)

I've created 3 CSV files with ALL your bid data ready to import:

1. **`NEXUS_Opportunities_Import.csv`** → Import to GPSS OPPORTUNITIES
2. **`NEXUS_Suppliers_Import.csv`** → Import to GPSS SUBCONTRACTORS  
3. **`NEXUS_Quotes_Import.csv`** → Import to GPSS SUBCONTRACTOR QUOTES

**How to import:**
1. Open each table in Airtable
2. Click the dropdown arrow next to table name
3. Choose "Import data" → "CSV file"
4. Select the corresponding CSV file
5. Map the columns (Airtable usually auto-maps correctly)
6. Click "Import"

---

### STEP 3: Done! (2 min)

Once imported, you'll have:

✅ **12 active bids** in GPSS OPPORTUNITIES  
✅ **21 suppliers** in GPSS SUBCONTRACTORS  
✅ **30+ quote tracking records** in GPSS SUBCONTRACTOR QUOTES  

All linked together automatically!

---

## 📊 WHAT YOU GET

### In GPSS OPPORTUNITIES:
- All 12 active bids with deadlines
- Estimated values and profits
- Current status and priority
- Which suppliers were contacted
- Quote status for each

### In GPSS SUBCONTRACTORS:
- All 21 suppliers/subcontractors
- Contact information
- Service types and locations
- Current status (active, awaiting, etc.)
- Notes on when contacted

### In GPSS SUBCONTRACTOR QUOTES:
- Every RFQ sent linked to the opportunity
- Which supplier got the RFQ
- When sent, when due
- Current status
- Quote amounts (when received)

---

## 🔗 HOW THE LINKING WORKS

Once imported, Airtable will automatically link:

**Opportunity** ↔ **Quotes** ↔ **Subcontractors**

Example:
```
"ITB 4614 Midland Asphalt"
  ↓
  Linked to Quote #1
    ↓
    Linked to "Bit Mat Products Company"
      ↓
      Shows contact info, status, notes
```

Click any opportunity to see all quotes. Click any quote to see the supplier details.

---

## 💡 AFTER IMPORT

### Update as you go:

**When a quote comes in:**
1. Find the quote record in GPSS SUBCONTRACTOR QUOTES
2. Change Status to "Received"
3. Add Quote Amount
4. The opportunity will auto-update

**When you win a bid:**
1. Update Status in GPSS OPPORTUNITIES to "Won"
2. All linked quotes show in one place

**When you contact a new supplier:**
1. Add them to GPSS SUBCONTRACTORS
2. Create a quote record linking to the opportunity
3. Done!

---

## 🚀 NEXT STEPS AFTER SETUP

### NEXUS backend will automatically:

1. ✅ Read opportunities from Airtable
2. ✅ Display in frontend dashboard
3. ✅ Show quotes and suppliers
4. ✅ Track deadlines
5. ✅ Calculate profits

### You can:

1. ✅ View all bids in one place (Airtable or NEXUS frontend)
2. ✅ Filter by deadline, status, priority
3. ✅ See which suppliers haven't responded
4. ✅ Track quote amounts and profits
5. ✅ Never lose track of bids or suppliers again!

---

## 📁 FILES CREATED

1. **`NEXUS_Opportunities_Import.csv`** - 12 active bids
2. **`NEXUS_Suppliers_Import.csv`** - 21 suppliers/subcontractors
3. **`NEXUS_Quotes_Import.csv`** - 30+ quote tracking records
4. **`AIRTABLE_QUICK_SETUP_GUIDE.md`** - This guide

---

## ⏱️ TIME REQUIRED

- **Add fields to tables:** 10 minutes
- **Import 3 CSV files:** 3 minutes
- **Verify data:** 2 minutes
- **TOTAL:** 15 minutes

---

## ✅ CHECKLIST

- [ ] Add fields to GPSS OPPORTUNITIES table
- [ ] Add fields to GPSS SUBCONTRACTORS table
- [ ] Add fields to GPSS SUBCONTRACTOR QUOTES table
- [ ] Import `NEXUS_Opportunities_Import.csv`
- [ ] Import `NEXUS_Suppliers_Import.csv`
- [ ] Import `NEXUS_Quotes_Import.csv`
- [ ] Verify data looks correct
- [ ] Test NEXUS backend/frontend connection
- [ ] Delete all markdown tracking files (optional - you won't need them!)

---

## 🎉 DONE!

After this 15-minute setup, you'll have a professional bid tracking system that:

- ✅ Automatically syncs with NEXUS
- ✅ Never loses track of suppliers or quotes
- ✅ Shows you what needs attention
- ✅ Calculates profits automatically
- ✅ Works from any device (Airtable mobile app too!)

**You'll never have to ask "did we contact this supplier?" again.**

---

**Ready? Start with STEP 1 above!** 🚀
