# NEXUS - AUTOMATIC BID FOLDER CREATION

**When new opportunity is created in Airtable → NEXUS automatically creates organized folder structure.**

---

## 🎯 THE AUTOMATION

### **Trigger: New Opportunity Created**

**When:**
- User adds new opportunity to GPSS Opportunities table
- OR opportunity imported from RSS feed
- OR opportunity added via email/API

**NEXUS automatically:**
1. Creates folder: `photos_and_videos/[CLIENT] [BID TYPE]/`
2. Downloads solicitation PDF to folder
3. Creates strategy document in folder
4. Creates submission checklist in folder
5. Updates Airtable with folder path

**Done in < 2 seconds. Zero manual work.**

---

## 📁 FOLDER STRUCTURE AUTO-CREATED

```
photos_and_videos/
└── [CLIENT] [BID TYPE]/
    ├── [ORIGINAL_SOLICITATION].pdf (auto-downloaded)
    ├── [CLIENT]_BID_STRATEGY.md (auto-generated)
    ├── [CLIENT]_SUBMISSION_CHECKLIST.md (auto-generated)
    ├── [CLIENT]_SUPPLIER_LIST.md (auto-generated)
    └── README.md (overview)
```

**All auto-created. No user action needed.**

---

## 🔧 IMPLEMENTATION

### **Backend Function: `create_bid_folder()`**

```python
def create_bid_folder(opportunity_id):
    """
    Auto-create organized folder for new opportunity.
    
    Args:
        opportunity_id: Airtable record ID
    
    Returns:
        folder_path: Path to created folder
    """
    # Get opportunity details from Airtable
    opp = get_opportunity(opportunity_id)
    
    # Generate folder name
    folder_name = f"{opp['Client'].upper()} {opp['Bid_Type'].upper()}"
    folder_path = f"photos_and_videos/{folder_name}"
    
    # Create folder
    os.makedirs(folder_path, exist_ok=True)
    
    # Download solicitation PDF
    if opp['Solicitation_URL']:
        download_pdf(opp['Solicitation_URL'], f"{folder_path}/{opp['RFQ_Number']}.pdf")
    
    # Generate strategy document
    create_strategy_doc(opp, folder_path)
    
    # Generate submission checklist
    create_checklist(opp, folder_path)
    
    # Generate supplier list
    create_supplier_list(opp, folder_path)
    
    # Update Airtable with folder path
    update_opportunity(opportunity_id, {'Folder_Path': folder_path})
    
    return folder_path
```

---

## 📄 AUTO-GENERATED DOCUMENTS

### **1. Strategy Document**

**File:** `[CLIENT]_BID_STRATEGY.md`

**Auto-generated content:**
```markdown
# [CLIENT] [BID TYPE] - BID STRATEGY

**RFQ Number:** [Auto-filled]
**Due Date:** [Auto-filled]
**Est. Value:** [Auto-filled]

## Quick Facts
- Client: [Auto-filled]
- Location: [Auto-filled]
- NAICS: [Auto-filled]
- Our Advantage: [Auto-filled from certifications]

## Next Steps
1. Review solicitation
2. Get supplier quotes
3. Calculate pricing
4. Complete bid forms
5. Submit by [deadline]
```

### **2. Submission Checklist**

**File:** `[CLIENT]_SUBMISSION_CHECKLIST.md`

**Auto-generated with specific requirements:**
```markdown
# SUBMISSION CHECKLIST

Due: [Auto-filled deadline]
Submit to: [Auto-filled from solicitation]

## Documents Required
- [ ] Completed bid form
- [ ] W-9
- [ ] [Auto-populated from solicitation requirements]

## Submission
- Email: [Auto-filled]
- Portal: [Auto-filled if available]
```

### **3. Supplier List**

**File:** `[CLIENT]_SUPPLIER_LIST.md`

**Auto-populated from NEXUS suppliers database:**
```markdown
# RECOMMENDED SUPPLIERS

Based on NAICS [code] and location [state]:

1. [Supplier name] - [Contact] - [Phone]
2. [Supplier name] - [Contact] - [Phone]
```

---

## 🔄 AIRTABLE INTEGRATION

### **New Fields in Opportunities Table:**

| Field Name | Type | Auto-populated |
|------------|------|----------------|
| `Folder_Path` | Text | Yes - folder location |
| `Folder_Created` | Checkbox | Yes - auto-checked |
| `Documents_Count` | Number | Yes - count of files |
| `Last_Updated` | Date | Yes - auto-updates |

### **Button: "Open Bid Folder"**

**In Opportunities table:**
- Click button → Opens folder in Finder/Explorer
- All docs right there
- One click access

---

## 📧 EMAIL INTEGRATION

### **When solicitation arrives via email:**

**NEXUS automatically:**
1. Extracts PDF attachment
2. Creates opportunity in Airtable
3. Creates folder structure
4. Saves PDF to folder
5. Generates strategy docs
6. Sends notification: "New bid folder created: [CLIENT]"

**User sees:**
- Email arrives: 10:00 AM
- NEXUS processes: 10:00:05 AM
- Folder ready: 10:00:07 AM
- Notification sent: 10:00:08 AM

**Total time: 8 seconds. Zero manual work.**

---

## 🎨 MAKE.COM SCENARIO

### **"New Opportunity → Create Folder"**

**Trigger:** New record in Opportunities table

**Actions:**
1. Get opportunity details
2. Call NEXUS API: `/opportunities/create-folder`
3. Wait for folder creation
4. Update Airtable with folder path
5. Send Slack notification
6. Done

**Run time: 3-5 seconds**

---

## 📱 NEXUS FRONTEND

### **Opportunities View:**

```
┌─────────────────────────────────────────┐
│ CPS Energy - Industrial Wipers         │
│ Due: Jan 27, 2026                       │
│                                         │
│ 📁 Folder: photos_and_videos/CPS ENERGY│
│    [Open Folder] [View Documents: 5]   │
│                                         │
│ Documents:                              │
│ ✅ RFQ_7000205103.pdf                  │
│ ✅ Bid_Submission_Supplement_signed.pdf│
│ ✅ Terms_Conditions_signed.pdf         │
│ ⬜ Strategy guide                      │
│ ⬜ Submission checklist                │
│                                         │
│    [Upload Document] [Auto-Organize]   │
└─────────────────────────────────────────┘
```

---

## 🚀 AUTO-ORGANIZATION FEATURES

### **1. Smart File Detection**

**When user uploads file to any folder:**
- NEXUS detects file type (quote, bid form, email, etc.)
- Auto-moves to correct bid folder
- Auto-renames with consistent naming
- Updates Airtable document count

### **2. Duplicate Detection**

**If file already exists:**
- NEXUS asks: "File exists. Replace or keep both?"
- User clicks one button
- Done

### **3. Auto-Archiving**

**When bid status = "Won" or "Lost":**
- NEXUS auto-renames folder: `[CLIENT] - WON` or `[CLIENT] - LOST`
- Moves to archive after 90 days
- Keeps recent bids accessible

---

## ⚡ SPEED BENCHMARKS

| Action | Max Time |
|--------|----------|
| Create folder structure | < 500ms |
| Download solicitation PDF | < 2 seconds |
| Generate strategy doc | < 200ms |
| Generate checklist | < 100ms |
| Update Airtable | < 300ms |
| **Total** | **< 3 seconds** |

---

## 🎯 USER EXPERIENCE

### **Old Way (Manual):**
1. User downloads PDF
2. User creates folder manually
3. User moves PDF to folder
4. User creates strategy doc
5. User creates checklist
6. User updates tracking
**Time: 10-15 minutes**

### **New Way (NEXUS):**
1. User adds opportunity to Airtable
2. NEXUS does everything else
**Time: 3 seconds**

**Time saved: 14 minutes 57 seconds per bid**

---

## 📋 CONFIGURATION

### **Settings in NEXUS:**

```json
{
  "bid_folders": {
    "base_path": "photos_and_videos",
    "auto_create": true,
    "auto_download_solicitation": true,
    "auto_generate_docs": true,
    "naming_format": "[CLIENT] [BID_TYPE]",
    "archive_after_days": 90
  }
}
```

**User can customize:**
- Base folder path
- Naming format
- Auto-download on/off
- Auto-archive timing

---

## 🔐 PERMISSIONS

**NEXUS needs:**
- ✅ Create folders in `photos_and_videos/`
- ✅ Download files from URLs
- ✅ Write files to folders
- ✅ Read/write Airtable
- ✅ Send notifications

**Security:**
- Only creates folders in designated bid folder
- Cannot delete folders without confirmation
- All actions logged
- User can disable automation anytime

---

## 📊 TRACKING & ANALYTICS

### **NEXUS Dashboard:**

```
Bid Folders Created This Month: 12
Documents Organized: 47
Time Saved: 3.2 hours
Storage Used: 245 MB

Recent Folders:
✅ CPS ENERGY (5 docs)
✅ MADISON HEIGHTS LAWN (3 docs)
✅ OAKLAND COUNTY BODY BAGS (8 docs)
```

---

## 🚦 STATUS INDICATORS

**In Airtable Opportunities table:**

| Status | Indicator |
|--------|-----------|
| Folder created | 📁 Green checkmark |
| Docs missing | ⚠️ Yellow warning |
| Ready to submit | ✅ Green badge |
| Submitted | 🚀 Blue badge |

---

## 🔄 SYNC & BACKUP

**NEXUS automatically:**
- Syncs folder structure to cloud
- Backs up all bid documents
- Versions important files
- Never loses data

**If file is deleted:**
- NEXUS asks: "Restore from backup?"
- One click restore
- Done

---

## 📱 MOBILE ACCESS

**NEXUS mobile app:**
- View all bid folders
- Upload documents from phone
- Auto-organizes to correct folder
- Access anywhere

---

## 🎓 TEACHING OTHERS

**Training new team member:**

**You:** "When you add an opportunity to Airtable, NEXUS creates the folder automatically."

**Them:** "That's it?"

**You:** "That's it. All documents go in that folder. NEXUS handles the organization."

**Training time: 30 seconds**

---

## ✅ IMPLEMENTATION CHECKLIST

**Backend:**
- [ ] `create_bid_folder()` function
- [ ] PDF download function
- [ ] Strategy doc generator
- [ ] Checklist generator
- [ ] Airtable integration
- [ ] Error handling

**Frontend:**
- [ ] "Open Folder" button
- [ ] Document counter
- [ ] Upload interface
- [ ] Status indicators

**Automation:**
- [ ] Make.com scenario
- [ ] Email trigger
- [ ] Airtable trigger
- [ ] Notifications

**Testing:**
- [ ] Create test opportunity
- [ ] Verify folder created
- [ ] Verify docs generated
- [ ] Verify Airtable updated

---

## 🎯 SUCCESS METRICS

**How to know it's working:**

| Metric | Target |
|--------|--------|
| Folder creation time | < 3 seconds |
| Manual folder creation | 0% (all auto) |
| Documents organized | 100% |
| User satisfaction | "I don't even think about it" |

---

## 💡 FUTURE ENHANCEMENTS

**Phase 2:**
- AI auto-fills strategy based on solicitation
- AI recommends suppliers based on requirements
- AI estimates pricing based on historical data
- AI drafts supplier email templates

**Phase 3:**
- Voice command: "NEXUS, create folder for Detroit Water diesel bid"
- Auto-submit when all docs complete
- Auto-follow-up emails after submission

---

## 🚀 BOTTOM LINE

**User adds opportunity → NEXUS creates organized folder → All docs go there → No manual organization needed.**

**Simple. Automatic. Always.**

---

*NEXUS: Because you have better things to do than create folders.*
