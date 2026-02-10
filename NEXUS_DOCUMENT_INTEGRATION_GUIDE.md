# NEXUS DOCUMENT INTEGRATION - Implementation Guide

**Created:** January 27, 2026  
**Purpose:** Integrate company documents repository with NEXUS GPSS system  
**Goal:** One-click bid package assembly from NEXUS dashboard

---

## 🎯 WHAT WE'RE BUILDING

### **Before Integration:**
```
User workflow:
1. Find opportunity in NEXUS
2. Switch to terminal
3. Run Python script manually
4. Copy files manually
5. Upload to Airtable manually
Time: 5-10 minutes
```

### **After Integration:**
```
User workflow:
1. Find opportunity in NEXUS
2. Click "Assemble Package" button
3. Documents automatically assembled and attached
Time: 30 seconds ⚡
```

---

## 📋 IMPLEMENTATION STEPS

### **Step 1: Update Airtable Schema ✅**

**Add these fields to "Opportunities" table:**

| Field Name | Field Type | Options | Purpose |
|------------|------------|---------|---------|
| `Documents Package` | Attachment | - | Store assembled bid documents |
| `Documents Checklist` | Multiple Select | W-9, EDWOSB, WOSB, Insurance, SAM, CAGE, CapStatement, References | Track which docs are included |
| `Package Status` | Single Select | Not Needed, Incomplete, Ready, Attached | Track assembly status |
| `Package Assembled Date` | Date | - | When package was last assembled |
| `Package Assembled By` | Single Line Text | - | Who/what assembled it (API/Manual) |

**How to add in Airtable:**
1. Open your NEXUS Airtable base
2. Go to "Opportunities" table
3. Click "+" to add new field
4. Create each field above with exact settings
5. Save

---

### **Step 2: Create API Endpoint 🔧**

**File:** `/Users/deedavis/NEXUS BACKEND/api_server.py`

**Add this endpoint:**

```python
@app.post("/api/gpss/opportunities/{opportunity_id}/assemble-package")
def assemble_bid_package_for_opportunity(opportunity_id: str):
    """
    Assemble bid package for a specific opportunity
    1. Get opportunity details from Airtable
    2. Gather documents from COMPANY_DOCUMENTS/
    3. Create package folder
    4. Upload documents to Airtable as attachments
    5. Update opportunity record
    """
    try:
        # Import the assembly function
        from assemble_bid_package import assemble_bid_package as assemble_package_local
        import shutil
        from pathlib import Path
        
        # 1. Get opportunity from Airtable
        airtable = AirtableClient()
        opportunity = airtable.get_record('Opportunities', opportunity_id)
        
        if not opportunity:
            return jsonify({"error": "Opportunity not found"}), 404
        
        # 2. Get opportunity title for folder name
        opp_title = opportunity.get('Title', f'Opportunity_{opportunity_id}')
        
        # 3. Assemble package locally
        result = assemble_package_local(opp_title)
        
        if not result["success"]:
            return jsonify({
                "error": "Package assembly incomplete",
                "missing": result["missing"]
            }), 400
        
        # 4. Upload documents to Airtable
        docs_folder = Path(result["output_dir"])
        attachments = []
        
        for doc_file in docs_folder.glob("*.pdf"):
            with open(doc_file, 'rb') as f:
                # Upload to Airtable (simplified - actual implementation needs file upload handling)
                attachments.append({
                    "filename": doc_file.name,
                    "url": f"file://{doc_file}"  # Airtable needs actual URL or base64
                })
        
        # 5. Update Airtable record
        update_data = {
            "Package Status": "Attached",
            "Documents Checklist": result["copied"],
            "Package Assembled Date": datetime.now().isoformat(),
            "Package Assembled By": "NEXUS API"
        }
        
        airtable.update_record('Opportunities', opportunity_id, update_data)
        
        return jsonify({
            "success": True,
            "documents": result["copied"],
            "missing": result["missing"],
            "package_path": result["output_dir"]
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
```

---

### **Step 3: Update Frontend Component 🎨**

**File:** `/Users/deedavis/NEXUS BACKEND/nexus-frontend/src/components/systems/GPSSSystem.tsx`

**Add "Assemble Package" function:**

```typescript
const assemblePackageForOpportunity = async (opportunityId: string) => {
  try {
    setNotification({ message: 'Assembling bid package...', type: 'success' });
    
    const response = await api.post(`/api/gpss/opportunities/${opportunityId}/assemble-package`);
    
    if (response.data.success) {
      setNotification({ 
        message: `Package assembled! ${response.data.documents.length} documents attached`, 
        type: 'success' 
      });
      
      // Refresh opportunities to show updated status
      fetchOpportunities();
    } else {
      setNotification({ 
        message: `Package incomplete. Missing: ${response.data.missing.join(', ')}`, 
        type: 'error' 
      });
    }
  } catch (error: any) {
    console.error('Error assembling package:', error);
    setNotification({ 
      message: error.response?.data?.error || 'Failed to assemble package', 
      type: 'error' 
    });
  }
};
```

**Add button to Opportunities table:**

```typescript
// In the opportunities table rendering (around line 800-900)
<button 
  onClick={() => assemblePackageForOpportunity(opp.id)}
  className="bg-blue-600 text-white px-3 py-1 rounded hover:bg-blue-700"
  title="Assemble bid documents package"
>
  📦 Assemble Package
</button>
```

---

### **Step 4: Update assemble_bid_package.py 🔧**

**Add function to work with Airtable:**

```python
def assemble_for_airtable(opportunity_id, opportunity_title):
    """
    Assemble package and return data for Airtable upload
    """
    result = assemble_bid_package(opportunity_title)
    
    # Prepare files for Airtable attachment
    attachments = []
    output_dir = Path(result["output_dir"])
    
    for doc_file in output_dir.glob("*.pdf"):
        with open(doc_file, 'rb') as f:
            attachments.append({
                "filename": doc_file.name,
                "content": f.read(),
                "type": "application/pdf"
            })
    
    return {
        "success": result["success"],
        "documents": result["copied"],
        "missing": result["missing"],
        "attachments": attachments
    }
```

---

## 🎯 USAGE WORKFLOW

### **User Experience:**

1. **Open NEXUS Dashboard**
   - Navigate to GPSS → Opportunities

2. **Find Your Opportunity**
   - Example: "RCOC Paper Products"

3. **Click "Assemble Package" Button**
   - System checks for required documents
   - Copies them from COMPANY_DOCUMENTS/
   - Uploads to Airtable
   - Updates opportunity record

4. **See Results**
   - "Package Status" changes to "Attached"
   - Documents appear in "Documents Package" field
   - "Documents Checklist" shows what's included

5. **Download When Needed**
   - Click on attachment in Airtable
   - Download all documents as zip
   - Ready to submit!

---

## 📊 AIRTABLE FIELD DETAILS

### **Package Status Options:**

| Status | Meaning | When to Use |
|--------|---------|-------------|
| Not Needed | No bid package required | Quote-only opportunities |
| Incomplete | Missing required documents | Need to upload more docs |
| Ready | All docs available locally | Ready to assemble |
| Attached | Package assembled and uploaded | Ready to submit bid |

### **Documents Checklist Options:**

- W-9
- EDWOSB
- WOSB  
- MBE
- Insurance
- SAM
- CAGE
- CapStatement
- References
- Banking
- WorkersComp

---

## 🔄 INTEGRATION FLOW

```
User clicks "Assemble Package"
         ↓
Frontend calls API: POST /api/gpss/opportunities/:id/assemble-package
         ↓
API gets opportunity details from Airtable
         ↓
API calls assemble_bid_package.py
         ↓
Python script gathers documents from COMPANY_DOCUMENTS/
         ↓
Documents copied to temporary package folder
         ↓
API uploads documents to Airtable as attachments
         ↓
API updates opportunity record (status, checklist, date)
         ↓
Frontend refreshes and shows success message
         ↓
User sees "Package Status: Attached" ✅
```

---

## 🚨 ERROR HANDLING

### **Missing Documents:**
```
User clicks "Assemble Package"
→ System finds W-9, EDWOSB, but missing WOSB
→ Shows warning: "Package incomplete. Missing: WOSB"
→ Status set to "Incomplete"
→ User uploads missing docs
→ Tries again
```

### **No Documents Folder:**
```
→ System checks COMPANY_DOCUMENTS/ folder
→ If not found, shows error
→ Provides link to UPLOAD_GUIDE.md
→ User uploads documents first
```

### **Network Errors:**
```
→ Frontend shows "Connection error"
→ Retry button appears
→ Documents stay local (not lost)
```

---

## ✅ TESTING CHECKLIST

### **Backend Testing:**
```bash
# Test API endpoint
curl -X POST http://localhost:8000/api/gpss/opportunities/rec123456/assemble-package

# Expected response:
{
  "success": true,
  "documents": ["W-9_Form_2026.pdf", "EDWOSB_Certificate.pdf", ...],
  "missing": [],
  "package_path": "/Users/deedavis/NEXUS BACKEND/photos_and_videos/RCOC Paper Products/BID_PACKAGE"
}
```

### **Frontend Testing:**
1. Open NEXUS dashboard
2. Go to GPSS → Opportunities
3. Find test opportunity
4. Click "Assemble Package"
5. Verify success message
6. Check Airtable record updated
7. Download attachment and verify files

### **Error Testing:**
1. Remove a required document
2. Try to assemble package
3. Verify "Incomplete" status shown
4. Verify missing docs listed
5. Upload missing doc
6. Try again, verify success

---

## 📈 BENEFITS

### **Time Savings:**
- **Before:** 5-10 minutes per bid
- **After:** 30 seconds per bid
- **Savings:** 4.5-9.5 minutes per bid

**At 30 bids/month:**
- **Time saved:** 2.25-4.75 hours/month
- **Value:** More time for finding opportunities!

### **Error Reduction:**
- ❌ Before: Sometimes forgot documents
- ✅ After: System ensures all docs included
- ❌ Before: Had to manually track what was sent
- ✅ After: Airtable checklist shows exactly what's included

### **Professional Appearance:**
- ✅ Consistent package every time
- ✅ All docs properly named
- ✅ Nothing missing
- ✅ Ready to submit immediately

---

## 🎯 NEXT PHASE ENHANCEMENTS

### **Phase 2: Smart Requirements Detection**
- AI reads RFP to determine required documents
- Auto-sets "Documents Checklist" based on requirements
- Warns if missing specialty documents

### **Phase 3: Auto-Submit Integration**
- Connect to bid portals (BidNet, MITN, etc.)
- One-click submission with documents
- Auto-confirmation tracking

### **Phase 4: Document Expiration Alerts**
- Track certificate expiration dates
- Alert 30-90 days before expiration
- Auto-flag opportunities that need renewed docs

---

## 📞 QUICK REFERENCE

**API Endpoint:**
```
POST /api/gpss/opportunities/:id/assemble-package
```

**Response:**
```json
{
  "success": true,
  "documents": ["W-9.pdf", "EDWOSB.pdf", "WOSB.pdf"],
  "missing": [],
  "package_path": "/path/to/package"
}
```

**Airtable Fields Added:**
- Documents Package (Attachment)
- Documents Checklist (Multiple Select)
- Package Status (Single Select)
- Package Assembled Date (Date)
- Package Assembled By (Text)

---

## ✅ IMPLEMENTATION STATUS

- [ ] Step 1: Update Airtable Schema
- [ ] Step 2: Create API Endpoint
- [ ] Step 3: Update Frontend Component  
- [ ] Step 4: Update Python Script
- [ ] Step 5: Test End-to-End
- [ ] Step 6: Deploy to Production

**Estimated Time:** 1-2 hours  
**Status:** Ready to implement  
**Priority:** High (saves significant time on every bid)

---

**Once complete, you'll have one-click bid package assembly from your NEXUS dashboard!** 🚀
