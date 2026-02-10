# QUICK UPLOAD GUIDE - COMPANY DOCUMENTS

**Goal:** Get all your standard bid documents uploaded so NEXUS can auto-assemble bid packages.

---

## 🎯 PRIORITY 1: UPLOAD THESE FIRST (Most Used)

### **1. W-9 Form** 
**Save as:** `TAX_LEGAL/W-9_Form_2026.pdf`  
**Used in:** 95% of bids  
**Status:** [ ] Not uploaded

### **2. EDWOSB Certificate**
**Save as:** `CERTIFICATIONS/EDWOSB_Certificate.pdf`  
**Used in:** Set-aside bids (your competitive advantage!)  
**Status:** [ ] Not uploaded

### **3. WOSB Certificate**
**Save as:** `CERTIFICATIONS/WOSB_Certificate.pdf`  
**Used in:** Set-aside bids  
**Status:** [ ] Not uploaded

### **4. General Liability Insurance**
**Save as:** `INSURANCE/General_Liability_Certificate.pdf`  
**Used in:** 50% of bids  
**Status:** [ ] Not uploaded

---

## 🎯 PRIORITY 2: UPLOAD THESE SOON (Frequently Requested)

### **5. SAM.gov Registration Status**
**Save as:** `TAX_LEGAL/SAM_Registration.pdf`  
**Get it from:** sam.gov → Your profile → Print to PDF  
**Status:** [ ] Not uploaded

### **6. CAGE Code Documentation**
**Save as:** `TAX_LEGAL/CAGE_Code_Documentation.pdf`  
**Your CAGE:** 8UMX3  
**Status:** [ ] Not uploaded

### **7. General Capability Statement**
**Save as:** `CAPABILITY_STATEMENTS/General_CapStatement.pdf`  
**Need to create?** Use `capability_statement_generator.py`  
**Status:** [ ] Not uploaded

---

## 🎯 PRIORITY 3: UPLOAD AS NEEDED (Occasionally Requested)

### **8. MBE Certificate** (if you have it)
**Save as:** `CERTIFICATIONS/MBE_Certificate.pdf`  
**Status:** [ ] Not uploaded / [ ] Not applicable

### **9. Workers Comp Insurance** (if you have employees)
**Save as:** `INSURANCE/Workers_Comp_Certificate.pdf`  
**Status:** [ ] Not uploaded / [ ] Not applicable

### **10. Banking/ACH Form** (for payment setup)
**Save as:** `COMPANY_INFO/Banking_ACH_Form.pdf`  
**Status:** [ ] Not uploaded

### **11. Company References** (3-5 clients/suppliers)
**Save as:** `COMPANY_INFO/References.pdf`  
**Status:** [ ] Not uploaded

---

## 📤 HOW TO UPLOAD (3 Easy Ways)

### **Option 1: Drag and Drop (Easiest)**
1. Open Finder
2. Navigate to `/Users/deedavis/NEXUS BACKEND/COMPANY_DOCUMENTS/`
3. Drag your PDFs into the appropriate subfolder

### **Option 2: Copy from Desktop**
```bash
# Example: Copy W-9 from Desktop
cp ~/Desktop/W-9.pdf "/Users/deedavis/NEXUS BACKEND/COMPANY_DOCUMENTS/TAX_LEGAL/W-9_Form_2026.pdf"
```

### **Option 3: Scan Directly**
If scanning:
1. Scan at 300 DPI (clear quality)
2. Save as PDF
3. Name clearly (e.g., `EDWOSB_Certificate.pdf`)
4. Move to appropriate folder

---

## ✅ VERIFICATION CHECKLIST

Before uploading each document, verify:

- [ ] **Correct company name:** DEE DAVIS INC (exactly as registered)
- [ ] **Current/not expired** (check dates!)
- [ ] **All pages included** (don't forget page 2!)
- [ ] **Clear and legible** (no blurry scans)
- [ ] **Official signatures/stamps** (if required)
- [ ] **PDF format** (not Word, not images)
- [ ] **File name matches guide** (makes automation easier)

---

## 🚀 WHAT HAPPENS AFTER UPLOAD?

Once your documents are uploaded:

### **Immediate Benefits:**
1. ✅ **Faster bid prep** - No hunting for files
2. ✅ **Auto-assembly** - System pulls docs automatically
3. ✅ **Expiration tracking** - Alerts before docs expire
4. ✅ **Compliance check** - Verify all requirements met

### **Example: RCOC Paper Bid**
**Before upload:**
- "Send me your W-9"
- "Do you have EDWOSB cert?"
- "What's your insurance?"
- Manual hunting for files (10-15 minutes)

**After upload:**
```
System: Preparing RCOC bid package...
  ✅ W-9 attached
  ✅ EDWOSB cert attached
  ✅ WOSB cert attached
  ✅ Insurance attached
  
📦 Package ready in 30 seconds!
```

---

## 📅 EXPIRATION TRACKING

After uploading, create these tracking files:

### **CERTIFICATIONS/EXPIRATION_DATES.md:**
```markdown
# Certification Expiration Dates

| Certificate | Expiration Date | Renewal Start Date |
|-------------|----------------|-------------------|
| EDWOSB | [Your date] | [90 days before] |
| WOSB | [Your date] | [90 days before] |
| MBE | [Your date] | [90 days before] |
```

### **INSURANCE/EXPIRATION_DATES.md:**
```markdown
# Insurance Expiration Dates

| Policy | Expiration Date | Renewal Start Date |
|--------|----------------|-------------------|
| General Liability | [Your date] | [30 days before] |
| Workers Comp | [Your date] | [30 days before] |
```

---

## 🎯 TODAY'S ACTION PLAN

**Right now (10 minutes):**
1. [ ] Locate your W-9 on your computer
2. [ ] Copy it to `COMPANY_DOCUMENTS/TAX_LEGAL/W-9_Form_2026.pdf`
3. [ ] Locate EDWOSB/WOSB certificates
4. [ ] Copy them to `COMPANY_DOCUMENTS/CERTIFICATIONS/`

**This afternoon (30 minutes):**
5. [ ] Find insurance certificates
6. [ ] Copy to `COMPANY_DOCUMENTS/INSURANCE/`
7. [ ] Log into SAM.gov, print registration to PDF
8. [ ] Save to `COMPANY_DOCUMENTS/TAX_LEGAL/`

**This week (1 hour):**
9. [ ] Create/update capability statement
10. [ ] Create references document
11. [ ] Create expiration tracking files
12. [ ] Test bid package assembly

---

## 📊 PROGRESS TRACKER

**Essential Documents (Must Have):**
- [ ] W-9 Form
- [ ] EDWOSB Certificate
- [ ] WOSB Certificate
- [ ] General Liability Insurance

**Status:** 0/4 uploaded

**Important Documents (Should Have):**
- [ ] SAM.gov Registration
- [ ] CAGE Code Documentation
- [ ] Capability Statement
- [ ] References

**Status:** 0/4 uploaded

**Optional Documents (Nice to Have):**
- [ ] MBE Certificate
- [ ] Workers Comp Insurance
- [ ] Banking/ACH Form
- [ ] Industry-specific capability statements

**Status:** 0/4 uploaded

---

## 🔍 HOW TO CHECK WHAT'S UPLOADED

Run this command:
```bash
ls -R "/Users/deedavis/NEXUS BACKEND/COMPANY_DOCUMENTS"
```

Should see:
```
CERTIFICATIONS/
  EDWOSB_Certificate.pdf
  WOSB_Certificate.pdf

TAX_LEGAL/
  W-9_Form_2026.pdf
  SAM_Registration.pdf
  CAGE_Code_Documentation.pdf

INSURANCE/
  General_Liability_Certificate.pdf

... etc
```

---

## 💡 PRO TIPS

1. **Use consistent naming** - Makes automation work better
2. **Keep backups** - Cloud storage + physical copies
3. **Update annually** - W-9 should match current year
4. **Track expirations** - Set calendar reminders
5. **Scan at 300 DPI** - Clear, professional quality
6. **PDF only** - Standardize on PDF format

---

## 🚨 WHAT NOT TO UPLOAD

**Do NOT put these in this folder:**
- ❌ Personal documents (not business-related)
- ❌ Login passwords or credentials
- ❌ Private banking information (beyond official forms)
- ❌ Credit card numbers
- ❌ Unencrypted sensitive data

---

## ✅ COMPLETION CHECKLIST

**When you're done, you should have:**
- [ ] All essential docs uploaded (W-9, EDWOSB, WOSB, Insurance)
- [ ] Files named according to guide
- [ ] Expiration dates tracked
- [ ] Verified all documents are current and valid
- [ ] Tested that system can find documents

**Status:** Ready to upload

---

**Start with W-9 and certificates - those are used in almost every bid!**

**Takes 10 minutes now, saves hours later.** ⚡
