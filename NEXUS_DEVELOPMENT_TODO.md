# NEXUS DEVELOPMENT TODO

## 🚀 HIGH PRIORITY

### **1. Auto Bid Folder Creation**
**Status:** Design complete, not implemented  
**Time:** 30 min (basic) | 2-3 hours (full)  
**Files:** `NEXUS_AUTO_BID_FOLDERS.md`  

**What it does:**
- Auto-creates folder when opportunity added
- Downloads solicitation PDF
- Generates strategy docs
- Updates Airtable with folder path

**Implementation:**
1. Add `create_bid_folder()` to `nexus_backend.py`
2. Add API endpoint `/opportunities/create-folder`
3. Create Airtable automation (trigger on new record)
4. Test with sample opportunity

---

## 📊 MEDIUM PRIORITY

### **2. NEXUS Pricing Automation**
**Status:** Design complete, not implemented  
**Time:** 2-3 hours  
**Files:** `NEXUS_PRICING_AUTOMATION_SIMPLE.md`  

**What it does:**
- Calculate pricing with markup (one click)
- Auto-fill bid forms
- Generate submission emails

---

## 📝 BACKLOG

### **3. Auto Email Parsing for Solicitations**
Extract solicitation details from emails automatically.

### **4. AI Bid Analysis**
Auto-analyze if solicitation is worth pursuing.

### **5. Voice Commands**
"NEXUS, create folder for Detroit Water bid"

---

## ✅ COMPLETED

- ✅ Bid folder organization system (manual)
- ✅ Direct answers rule (no fluff)
- ✅ CPS Energy bid completed

---

*Last updated: January 26, 2026*
