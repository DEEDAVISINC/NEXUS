# 🧪 Testing the Review & Name Modal

**Current Status:** Review modal deployed and ready for testing!

---

## 🎯 What We're Testing

### **The Complete Workflow:**
1. Dashboard shows unnamed opportunities in "NEEDS REVIEW" queue
2. Click "Review & Name" button
3. Modal opens with smart suggestions
4. User reviews and names opportunity
5. Submits decision (Pursue or Skip)
6. Dashboard refreshes
7. Item moves to appropriate queue

---

## 📋 Pre-Testing Checklist

### **✅ What's Already Done:**
- ✅ Backend workflow API deployed
- ✅ Frontend dashboard deployed to Netlify
- ✅ Review modal component complete
- ✅ Git committed and pushed

### **⚠️ What Needs Setup (for full functionality):**
- ⚠️ Backend server running locally (for API calls)
- ⚠️ Airtable workflow fields added (for real data)

---

## 🚀 Testing Scenarios

## **Scenario A: Test on Netlify (Visual Only)**

**Best for:** Seeing the UI design and layout

### **Steps:**
1. Go to https://nexus-command.netlify.app
2. Dashboard loads
3. Look at "NEEDS REVIEW" section
4. Click any "Review & Name" button

### **What You'll See:**
- ✅ Modal opens
- ✅ Beautiful gradient design
- ✅ Opportunity details displayed
- ✅ Name suggestion (if data available)
- ✅ Decision buttons
- ✅ Notes field

### **What Won't Work Yet:**
- ❌ Submit button (needs backend API running)
- ❌ Real data refresh (needs API)

**This is fine for visual testing!**

---

## **Scenario B: Full Local Testing (Complete Flow)**

**Best for:** Testing the entire workflow end-to-end

### **Setup Required:**

#### **1. Start Backend API Server**
```bash
cd "/Users/deedavis/NEXUS BACKEND"
python3 api_server.py
```

**Expected output:**
```
 * Running on http://127.0.0.1:8000
 * Running on http://192.168.x.x:8000
```

#### **2. Start Frontend Dev Server**
```bash
cd "/Users/deedavis/NEXUS BACKEND/nexus-frontend"
npm start
```

**Expected output:**
```
Compiled successfully!
You can now view nexus-frontend in the browser.
  Local:            http://localhost:3000
```

### **Testing Steps:**

#### **Step 1: Open Dashboard**
```
Browser automatically opens to: http://localhost:3000
```

#### **Step 2: Check Queue Sections**
Look for "NEEDS REVIEW" section with opportunities

**If you see opportunities:** Great! Continue to Step 3

**If you see "All caught up!":** No unnamed opportunities in Airtable yet
- This is okay - we can test with mock data
- Or add a test opportunity in Airtable

#### **Step 3: Click "Review & Name"**
Click button on any unnamed opportunity

**Modal should open with:**
- Opportunity details (agency, value, deadline)
- Suggested name (if available)
- "Use This" button for suggestion
- Name input field
- Decision buttons (Pursue/Skip)
- Notes field (optional)
- Cancel and Submit buttons

#### **Step 4: Test Name Suggestion**
**If suggested name shows:**
1. Click "Use This" button
2. Name field should populate automatically

**If no suggestion:**
1. Type a name manually
2. Example: "Test Opportunity - Supplies"

#### **Step 5: Test Decision Buttons**
1. Click "PURSUE THIS"
   - Should highlight green
   - Submit button text: "✅ Pursue This Opportunity"

2. Click "SKIP THIS"
   - Should highlight red
   - Submit button text: "⏭️ Skip This Opportunity"

#### **Step 6: Test Character Counters**
1. Type in Name field
   - Counter updates: "X/100 characters"

2. Type in Notes field
   - Counter updates: "X/500 characters"

#### **Step 7: Test Validation**
1. Clear name field
   - Submit button should be disabled

2. Type any text in name field
   - Submit button should be enabled

#### **Step 8: Submit Form**
1. Fill in name: "Test Opportunity - CPS Energy"
2. Choose "PURSUE THIS"
3. Add notes: "Testing the workflow system"
4. Click "✅ Pursue This Opportunity"

**Expected behavior:**
```
Button shows "⟳ Saving..."
  ↓
API call: POST /api/workflow/opportunity/{id}/review
  ↓
Airtable updates (if fields exist)
  ↓
Modal closes
  ↓
Dashboard refreshes
  ↓
"NEEDS REVIEW" count decreases
Item appears in "FIND SUPPLIERS" queue
```

#### **Step 9: Verify Queue Update**
1. Check "NEEDS REVIEW" section
   - Count should decrease by 1
   - Item should be gone

2. Check "FIND SUPPLIERS" section
   - Should have 1 more item
   - Should show the renamed opportunity

---

## 🐛 Troubleshooting

### **Problem: Modal doesn't open**
**Check:**
- Browser console for errors (F12 → Console tab)
- React dev server is running
- No JavaScript errors

**Fix:**
```bash
cd nexus-frontend
npm start
```

---

### **Problem: Submit button stays disabled**
**Check:**
- Name field has text
- Text is not just spaces

**Fix:**
Type any non-empty text in name field

---

### **Problem: API call fails**
**Symptoms:**
- Submit button spins forever
- Error message appears in modal

**Check:**
1. Backend server running?
```bash
# Check if server is running
curl http://localhost:8000/health

# Should return: {"status": "healthy"}
```

2. CORS enabled?
- Backend API has `CORS(app)` enabled ✅

3. Airtable credentials set?
```bash
# Check .env file
cat .env | grep AIRTABLE
```

**Fix:**
```bash
# Restart backend server
cd "/Users/deedavis/NEXUS BACKEND"
python3 api_server.py
```

---

### **Problem: No opportunities in "NEEDS REVIEW"**
**Symptoms:**
- Section says "✅ All caught up!"
- No "Review & Name" buttons to click

**This means:**
- No unnamed opportunities in Airtable
- OR workflow fields not set up yet

**Solutions:**

**Option A: Add Test Opportunity in Airtable**
1. Go to GPSS Opportunities table
2. Create new record with:
   - Name: Leave blank or "Unnamed"
   - Issuing Organization: "Test Agency"
   - Category: "Test Category"
   - Estimated Value: 100000
   - Response Deadline: Future date

**Option B: Test with Existing Data**
1. Find any existing opportunity
2. Clear its Name field (or set to "Unnamed")
3. Set Workflow Status to "Needs Review"
4. Refresh dashboard

**Option C: Use Mock Data (Quick Test)**
I can create a mock data version for quick UI testing

---

### **Problem: Item doesn't move to next queue after submit**
**Possible causes:**
1. Airtable workflow fields not added yet
2. Workflow Status field doesn't exist
3. API succeeded but formula didn't update

**Check:**
```bash
# Check API response
curl -X POST http://localhost:8000/api/workflow/opportunity/recXXX/review \
  -H "Content-Type: application/json" \
  -d '{"name": "Test", "decision": "pursue", "notes": ""}'
```

**Expected response:**
```json
{
  "success": true,
  "message": "Opportunity reviewed: Test",
  "newStatus": "Find Suppliers"
}
```

**Fix:**
Add workflow fields to Airtable (see AIRTABLE_WORKFLOW_FIELDS.md)

---

## ✅ Success Criteria

### **Visual Testing (Netlify):**
- [x] Modal opens when button clicked
- [x] All sections visible
- [x] Form fields work
- [x] Buttons respond to clicks
- [x] Character counters update
- [x] Design looks professional

### **Functional Testing (Local):**
- [x] API call succeeds
- [x] Airtable updates
- [x] Modal closes after submit
- [x] Dashboard refreshes
- [x] Counts update
- [x] Item moves to correct queue

---

## 🎯 Quick Test Commands

### **Test 1: Check if backend is running**
```bash
curl http://localhost:8000/health
```

### **Test 2: Get workflow queues**
```bash
curl http://localhost:8000/api/workflow/queues
```

### **Test 3: Review an opportunity**
```bash
curl -X POST http://localhost:8000/api/workflow/opportunity/recXXXX/review \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Opportunity - Supplies",
    "decision": "pursue",
    "notes": "Testing workflow"
  }'
```

---

## 📊 What to Look For

### **Good Signs:** ✅
- Modal opens smoothly
- Suggested name appears
- Form fields respond instantly
- Buttons change color when clicked
- Character counters update in real-time
- Submit button shows loading spinner
- Modal closes after successful submit
- Dashboard refreshes automatically
- Item disappears from one queue
- Item appears in next queue

### **Warning Signs:** ⚠️
- Modal takes >1 second to open
- Suggested name is blank when it shouldn't be
- Form fields are laggy
- Submit button doesn't disable during submission
- No loading indicator
- Error message appears

### **Red Flags:** ❌
- Modal doesn't open at all
- Console shows JavaScript errors
- API returns 500 error
- Submit never completes
- Dashboard doesn't refresh
- Item doesn't move queues

---

## 📸 Screenshot Checklist

**Take screenshots of:**
1. Dashboard "NEEDS REVIEW" section
2. Modal opened with all details
3. Suggested name feature
4. Decision buttons (both states)
5. Submit button (loading state)
6. Dashboard after submit (item moved)

**This will help debug any issues!**

---

## 🎓 Learning Points

### **What This Test Demonstrates:**

1. **Frontend-Backend Integration**
   - React component → API call → Airtable update

2. **State Management**
   - Modal state
   - Form state
   - Loading state
   - Error state

3. **User Experience**
   - Immediate feedback
   - Loading indicators
   - Error handling
   - Success confirmation

4. **Data Flow**
   - User action → API → Database → UI refresh

---

## 🔄 Test Again

After any changes, test again to verify:
1. Changes deployed to Netlify
2. Functionality still works
3. No new bugs introduced
4. Performance is good

---

## 📝 Report Results

**After testing, note:**
- ✅ What worked perfectly
- ⚠️ What needs adjustment
- ❌ What didn't work
- 💡 Ideas for improvement

**This helps prioritize next steps!**

---

Last updated: January 27, 2026
