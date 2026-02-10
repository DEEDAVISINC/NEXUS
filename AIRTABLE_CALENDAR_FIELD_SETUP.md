# AIRTABLE SETUP - Calendar Automation Field

**Required for:** Calendar automation to track which opportunities have been processed  
**Table:** GPSS OPPORTUNITIES  
**Status:** ⚠️ FIELD MISSING - Needs to be added

---

## ⚠️ REQUIRED FIELD:

### **"Calendar Generated"**
**Field Type:** Checkbox  
**Purpose:** Tracks which opportunities have had calendar files generated  
**Default:** Unchecked

---

## 🛠️ HOW TO ADD IT:

### **Step 1: Open Airtable**
1. Go to your NEXUS Airtable base
2. Open the **GPSS OPPORTUNITIES** table

### **Step 2: Add New Field**
1. Click the **"+"** button at the right of the column headers
2. Field name: **Calendar Generated**
3. Field type: **Checkbox**
4. Click **Create field**

### **Step 3: Leave All Unchecked**
- Don't check any boxes yet
- System will automatically check them as it generates calendar files

**That's it! Field is ready.**

---

## 📊 CURRENT GPSS OPPORTUNITIES FIELDS:

**Fields that exist:**
- ✅ Deadline
- ✅ HIGH VALUE FLAG
- ✅ Name
- ✅ RFP NUMBER
- ✅ Source Status

**Fields needed:**
- ❌ **Calendar Generated** ← ADD THIS

---

## 🔄 HOW IT WORKS:

### **Before Adding Field:**
- System generates calendar files every hour
- But doesn't track which ones it's already done
- Could generate duplicate files for same opportunity

### **After Adding Field:**
1. ✅ New opportunity added to Airtable
2. ✅ Calendar Generated = Unchecked
3. ✅ Hourly job runs, finds unchecked opportunity
4. ✅ Generates .ics calendar file
5. ✅ Emails file to you
6. ✅ Checks the "Calendar Generated" box
7. ✅ Won't process that opportunity again

---

## ⚙️ SYSTEM BEHAVIOR:

**With field added:**
- ✅ No duplicate calendar files
- ✅ Only new opportunities processed
- ✅ Efficient and clean

**Without field:**
- ⚠️ System still works
- ⚠️ But might generate duplicates
- ⚠️ Less efficient

---

## 🎯 WHEN TO ADD IT:

**Recommended:** Add it now (takes 30 seconds)

**System will work without it, but:**
- May generate duplicate calendar files
- Less efficient
- Better to add it now

---

## ✅ VERIFICATION:

**After adding the field, verify it's working:**

1. **Add a test opportunity** with a deadline
2. **Wait for next hourly run** (or run manually)
3. **Check if "Calendar Generated" gets checked**
4. **Check email** for calendar file

---

## 🚀 QUICK SETUP GUIDE:

**Total Time:** 30 seconds

1. Open Airtable → NEXUS base
2. Go to **GPSS OPPORTUNITIES** table
3. Click **"+"** to add field
4. Name: **Calendar Generated**
5. Type: **Checkbox**
6. Click **Create**
7. Done!

---

## 📋 OPTIONAL: Other Useful Fields

**These fields would enhance the system but are NOT required:**

- **Calendar File Sent** (Date field) - When calendar was emailed
- **Quote Deadline** (Date field) - Auto-calculated supplier quote deadline
- **Days Until Deadline** (Formula field) - Days remaining
- **Urgency** (Formula field) - "Urgent", "This Week", "Next Week"

**For now, just add "Calendar Generated" and the system will work!**

---

## ❓ TROUBLESHOOTING:

**Q: Do I need to check any existing opportunities?**  
A: No, leave them all unchecked. System will process them on next hourly run.

**Q: What if I accidentally check some boxes?**  
A: No problem. System will skip those and only process unchecked ones.

**Q: Can I rename the field?**  
A: No, must be exactly "Calendar Generated" (with that capitalization and space).

**Q: What if I don't add it?**  
A: System still works, but may generate duplicate files for same opportunities.

---

## 🎯 BOTTOM LINE:

**Required:** ✅ Add "Calendar Generated" checkbox field to GPSS OPPORTUNITIES  
**Time:** 30 seconds  
**Impact:** Prevents duplicate calendar files  
**When:** Do it now before first hourly run

---

*Created: January 28, 2026*  
*Priority: MEDIUM (system works without it, but better with it)*  
*Setup Time: 30 seconds*
