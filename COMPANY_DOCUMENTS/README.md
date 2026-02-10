# DEE DAVIS INC - COMPANY DOCUMENTS REPOSITORY

**Purpose:** Central storage for all standard company documents used in bid submissions.

**Created:** January 27, 2026  
**Location:** `/Users/deedavis/NEXUS BACKEND/COMPANY_DOCUMENTS/`

---

## 📁 FOLDER STRUCTURE

```
COMPANY_DOCUMENTS/
├── README.md (this file)
├── CERTIFICATIONS/
│   ├── EDWOSB_Certificate.pdf
│   ├── WOSB_Certificate.pdf
│   ├── MBE_Certificate.pdf
│   ├── WBE_Certificate.pdf
│   └── CERTIFICATION_EXPIRATION_DATES.md
├── TAX_LEGAL/
│   ├── W-9_Form.pdf
│   ├── CAGE_Code_Documentation.pdf
│   └── SAM_Registration.pdf
├── INSURANCE/
│   ├── General_Liability_Certificate.pdf
│   ├── Workers_Comp_Certificate.pdf
│   └── INSURANCE_EXPIRATION_DATES.md
├── COMPANY_INFO/
│   ├── Company_Profile.pdf
│   ├── NAICS_Codes.md
│   ├── Banking_ACH_Form.pdf
│   └── References.pdf
└── CAPABILITY_STATEMENTS/
    ├── General_CapStatement.pdf
    ├── Industrial_Supplies_CapStatement.pdf
    ├── Construction_Materials_CapStatement.pdf
    └── Medical_Supplies_CapStatement.pdf
```

---

## 📋 REQUIRED DOCUMENTS CHECKLIST

### **CERTIFICATIONS** (Most Important!)
- [ ] **EDWOSB Certificate** - Economically Disadvantaged Woman-Owned Small Business
- [ ] **WOSB Certificate** - Woman-Owned Small Business
- [ ] **MBE Certificate** - Minority Business Enterprise (if applicable)
- [ ] **WBE Certificate** - Woman Business Enterprise (if applicable)
- [ ] **DBE Certificate** - Disadvantaged Business Enterprise (if applicable)
- [ ] **SBE Certificate** - Small Business Enterprise (if applicable)

### **TAX & LEGAL** (Required for Most Bids)
- [ ] **W-9 Form** - IRS Tax Form (must be current year)
- [ ] **CAGE Code Documentation** - 8UMX3
- [ ] **SAM.gov Registration** - Active status confirmation
- [ ] **UEI Number** - Unique Entity Identifier
- [ ] **DUNS Number** (if still used)

### **INSURANCE** (Sometimes Required)
- [ ] **General Liability Certificate** - $1M-$2M coverage typical
- [ ] **Workers Compensation** - If you have employees
- [ ] **Auto Insurance** - For delivery vehicles
- [ ] **Product Liability** - For certain products

### **COMPANY INFORMATION** (Standard)
- [ ] **Company Profile** - 1-2 page overview
- [ ] **NAICS Codes List** - All codes you qualify under
- [ ] **Banking/ACH Form** - For payment setup
- [ ] **References** - 3-5 previous clients/suppliers
- [ ] **Financial Statements** - Sometimes required for large contracts

### **CAPABILITY STATEMENTS** (Competitive Advantage)
- [ ] **General Capability Statement** - All-purpose
- [ ] **Industry-Specific Versions** - Customized by sector

---

## 🎯 HOW THE SYSTEM USES THESE DOCUMENTS

### **Automated Bid Package Assembly:**

When you're ready to submit a bid, the system will:

1. **Check bid requirements** - What documents are needed?
2. **Pull from this folder** - Automatically locate required docs
3. **Assemble package** - Create complete submission package
4. **Alert for missing docs** - If something is not found
5. **Track expirations** - Warn when certificates expire

### **Example Workflow:**

```
User: "Prepare bid package for RCOC Paper"
System: 
  ✅ Found W-9
  ✅ Found EDWOSB Certificate
  ✅ Found WOSB Certificate
  ✅ Found General Liability Insurance
  ⚠️  Missing: Workers Comp (not required for this bid)
  
  📦 Bid Package Ready:
     - Bid Form (completed)
     - W-9
     - EDWOSB Certificate
     - WOSB Certificate
     - General Liability Certificate
     
  Ready to submit!
```

---

## 📅 DOCUMENT EXPIRATION TRACKING

### **Certifications:**
| Document | Expiration Date | Renewal Lead Time |
|----------|----------------|-------------------|
| EDWOSB | [Date] | 90 days before |
| WOSB | [Date] | 90 days before |
| MBE | [Date] | 90 days before |

### **Insurance:**
| Document | Expiration Date | Renewal Lead Time |
|----------|----------------|-------------------|
| General Liability | [Date] | 30 days before |
| Workers Comp | [Date] | 30 days before |

### **Tax/Legal:**
| Document | Renewal Frequency | Notes |
|----------|-------------------|-------|
| W-9 | Annual (or when info changes) | Use current year |
| SAM.gov | Annual | Must maintain active status |
| CAGE Code | No expiration | Keep documentation |

---

## 🔒 SECURITY & STORAGE

### **Where to Store Originals:**
- Physical copies in secure file cabinet
- Cloud backup (Google Drive, Dropbox, etc.)
- This folder for NEXUS system access

### **What NOT to Store Here:**
- ❌ Passwords or login credentials
- ❌ Bank account numbers (except on official forms)
- ❌ Social Security Numbers (except on W-9)
- ❌ Credit card information

### **Access Control:**
- Only you and authorized personnel
- Not included in public GitHub repo
- Keep backup copies separately

---

## 📤 HOW TO UPLOAD DOCUMENTS

### **Step 1: Organize Your Files**
Gather all documents and name them clearly:
- `EDWOSB_Certificate.pdf`
- `W-9_Form_2026.pdf`
- `General_Liability_Certificate.pdf`

### **Step 2: Create Subfolders**
```bash
cd "/Users/deedavis/NEXUS BACKEND/COMPANY_DOCUMENTS"
mkdir CERTIFICATIONS
mkdir TAX_LEGAL
mkdir INSURANCE
mkdir COMPANY_INFO
mkdir CAPABILITY_STATEMENTS
```

### **Step 3: Upload Files**
Copy your PDFs into the appropriate folders.

### **Step 4: Update Expiration Dates**
Edit the tracking files with your actual dates.

---

## 🎯 INTEGRATION WITH NEXUS

### **Airtable Integration:**
Once uploaded, these documents will be:
- Referenced in NEXUS Opportunities table
- Auto-attached to bid submissions
- Tracked for expiration dates
- Linked to specific bids

### **Automated Workflows:**
- **Bid submission prep** → Pulls required docs automatically
- **Expiration alerts** → Notifies 30-90 days before expiration
- **Compliance check** → Verifies all required docs present
- **Quick access** → Download bundle for manual submissions

---

## ✅ IMMEDIATE NEXT STEPS

**Today:**
1. Create subfolders (use command below)
2. Upload your W-9
3. Upload EDWOSB/WOSB certificates
4. Upload insurance certificates

**This Week:**
5. Create/update capability statements
6. Gather reference documents
7. Update expiration dates in tracking files
8. Test bid package assembly

---

## 📞 DOCUMENT VERIFICATION CHECKLIST

Before uploading, verify each document has:
- [ ] Clear, legible scan (300 DPI minimum)
- [ ] All pages included
- [ ] Current/not expired
- [ ] Correct company name: **DEE DAVIS INC**
- [ ] Correct address
- [ ] Official signatures/stamps (if required)

---

## 🚀 QUICK COMMANDS

### **Create All Folders:**
```bash
cd "/Users/deedavis/NEXUS BACKEND/COMPANY_DOCUMENTS"
mkdir -p CERTIFICATIONS TAX_LEGAL INSURANCE COMPANY_INFO CAPABILITY_STATEMENTS
```

### **Check What's Uploaded:**
```bash
ls -R "/Users/deedavis/NEXUS BACKEND/COMPANY_DOCUMENTS"
```

### **Verify File Sizes:**
```bash
find "/Users/deedavis/NEXUS BACKEND/COMPANY_DOCUMENTS" -type f -name "*.pdf" -exec ls -lh {} \;
```

---

## 📊 STATUS TRACKING

**Documents Uploaded:** 0/20  
**Expiration Alerts:** None set  
**Integration Status:** Ready for upload  
**Last Updated:** January 27, 2026

---

**Once you upload your documents, NEXUS will be able to auto-assemble bid packages in seconds instead of minutes!**

**Ready to start uploading? Create the folders first, then add your PDFs.** ✅
