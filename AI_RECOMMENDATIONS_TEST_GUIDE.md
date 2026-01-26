# AI RECOMMENDATIONS TABLE - TEST SETUP GUIDE
**🧪 Super Simple Testing Instructions**

---

## ✅ STEP 1: VERIFY TABLE EXISTS

1. Open Airtable in your browser
2. Go to your NEXUS base
3. Look for a table named: **`AI RECOMMENDATIONS`**
4. Click on it

**Can you see the table?**
- ✅ YES → Go to Step 2
- ❌ NO → You need to create the table first (use `AI_RECOMMENDATIONS_TABLE_SETUP.md`)

---

## ✅ STEP 2: CHECK FIELDS

Look at the column headers. You should see these 11 fields:

```
1. OPPORTUNITY
2. TYPE
3. RECOMMENDATION
4. CONFIDENCE
5. REASONING
6. STATUS
7. USER_DECISION
8. USER_NOTES
9. SELECTED_OPTION
10. CREATED
11. DECIDED_AT
```

**Do you see all 11 fields?**
- ✅ YES → Go to Step 3
- ❌ NO → Missing fields need to be added

### Missing Fields? Add Them:

**Missing OPPORTUNITY field?**
- Click "+" to add field
- Name: `OPPORTUNITY`
- Type: "Link to another record"
- Select table: "GPSS OPPORTUNITIES" (or "Opportunities")
- Save

**Missing TYPE field?**
- Click "+" to add field
- Name: `TYPE`
- Type: "Single select"
- Add options: `Capability Gap Analysis`, `Subcontractor Recommendation`, `Supplier Recommendation`, `Compliance Check`
- Save

**Missing CONFIDENCE field?**
- Click "+" to add field
- Name: `CONFIDENCE`
- Type: "Number"
- Format: Integer (0 decimal places)
- Save

(Repeat for any other missing fields using the guide)

---

## ✅ STEP 3: CREATE TEST RECORD

### Method A: Using Airtable Interface (EASIEST)

1. **Click the blue "+" button** at the bottom of the table
   - This adds a new empty row

2. **Fill in the OPPORTUNITY field:**
   - Click in the OPPORTUNITY cell
   - A dropdown appears showing your opportunities
   - Select ANY opportunity from the list (doesn't matter which)
   - If you don't have any opportunities, type: `Test Opportunity`

3. **Fill in the TYPE field:**
   - Click in the TYPE cell
   - Select: **`Capability Gap Analysis`**

4. **Fill in the RECOMMENDATION field:**
   - Click in the RECOMMENDATION cell
   - Type (or copy/paste):
   ```
   You lack cybersecurity certification for this RFP. Consider partnering with SecureIT Solutions who has CMMC Level 2 certification and DOD past performance.
   ```

5. **Fill in the CONFIDENCE field:**
   - Click in the CONFIDENCE cell
   - Type: **`85`**

6. **Fill in the REASONING field:**
   - Click in the REASONING cell
   - Type (or copy/paste):
   ```
   RFP requires CMMC Level 2 certification which your company doesn't currently have. SecureIT Solutions has this certification and has completed 15+ DOD contracts in the past 3 years.
   ```

7. **Fill in the STATUS field:**
   - Click in the STATUS cell
   - Select: **`Pending Approval`**

8. **Leave these fields BLANK for now:**
   - USER_DECISION (leave blank)
   - USER_NOTES (leave blank)
   - SELECTED_OPTION (leave blank)
   - DECIDED_AT (leave blank)
   - CREATED (auto-fills when you save)

9. **Hit Enter or click outside the row to SAVE**

---

### Method B: Copy/Paste Quick Values (FASTER)

If your cursor is in the first empty row, just copy and paste these values:

**For RECOMMENDATION field:**
```
You lack cybersecurity certification for this RFP. Consider partnering with SecureIT Solutions who has CMMC Level 2 certification and DOD past performance.
```

**For REASONING field:**
```
RFP requires CMMC Level 2 certification which your company doesn't currently have. SecureIT Solutions has this certification and has completed 15+ DOD contracts in the past 3 years.
```

**For CONFIDENCE field:**
```
85
```

---

## ✅ STEP 4: VERIFY TEST RECORD

After saving, your test record should look like this:

| Field | Value |
|-------|-------|
| OPPORTUNITY | (One of your opportunities selected) |
| TYPE | `Capability Gap Analysis` |
| RECOMMENDATION | "You lack cybersecurity certification..." |
| CONFIDENCE | `85` |
| REASONING | "RFP requires CMMC Level 2..." |
| STATUS | `Pending Approval` |
| USER_DECISION | (blank) |
| USER_NOTES | (blank) |
| SELECTED_OPTION | (blank) |
| CREATED | (Today's date with time) ✅ |
| DECIDED_AT | (blank) |

**Can you see all these values?**
- ✅ YES → **TEST PASSED!** 🎉
- ❌ NO → See troubleshooting below

---

## ✅ STEP 5: TEST APPROVAL WORKFLOW

Now let's test approving a recommendation:

1. **Click on your test record** (the row you just created)

2. **Change USER_DECISION field:**
   - Click in the USER_DECISION cell
   - Select: **`APPROVED`**

3. **Change STATUS field:**
   - Click in the STATUS cell
   - Change from "Pending Approval" to: **`Approved`**

4. **Add USER_NOTES:**
   - Click in the USER_NOTES cell
   - Type: `Good recommendation. Will reach out to SecureIT.`

5. **Set DECIDED_AT:**
   - Click in the DECIDED_AT cell
   - Click "Today" or select today's date
   - Make sure time is included

6. **Save** (hit Enter or click outside)

**Now your record shows the complete workflow!** ✅

---

## ✅ STEP 6: CREATE SECOND TEST RECORD (OPTIONAL)

Create another test to see variety:

1. Click "+" to add new record
2. Fill in:
   - **OPPORTUNITY:** (Select any)
   - **TYPE:** `Subcontractor Recommendation`
   - **RECOMMENDATION:** `Use ABC Janitorial Services for this contract. They're local to Detroit and have 10+ VA facility contracts.`
   - **CONFIDENCE:** `92`
   - **REASONING:** `Local provider with strong VA past performance. Average pricing 15% below competitors. 8(a) certified provides socioeconomic advantage.`
   - **STATUS:** `Pending Approval`
3. Save

**Now you have 2 test records - one approved, one pending!** ✅

---

## 🎯 WHAT SUCCESS LOOKS LIKE

After testing, you should see:

**Record 1 (Approved):**
- TYPE: Capability Gap Analysis
- CONFIDENCE: 85
- STATUS: Approved
- USER_DECISION: APPROVED
- USER_NOTES: "Good recommendation..."
- DECIDED_AT: Today's date

**Record 2 (Pending):**
- TYPE: Subcontractor Recommendation
- CONFIDENCE: 92
- STATUS: Pending Approval
- USER_DECISION: (blank)
- DECIDED_AT: (blank)

**This proves the table is working correctly!** 🎉

---

## ❌ TROUBLESHOOTING

### Problem: "Can't find GPSS OPPORTUNITIES table"

**Solution:**
1. Check what your Opportunities table is actually named
2. It might be called just "Opportunities" (without GPSS)
3. When setting up OPPORTUNITY field:
   - Link to whatever your opportunities table is named
   - Common names: "Opportunities", "GPSS OPPORTUNITIES", "GPSS Opportunities"

### Problem: "CONFIDENCE field won't accept numbers"

**Solution:**
1. Click the CONFIDENCE field header (column name)
2. Click "Customize field type"
3. Change to: "Number"
4. Format: Integer
5. Precision: 0 decimal places
6. Save

### Problem: "CREATED field is blank"

**Solution:**
- This is normal! CREATED only fills when you first save the record
- If it's still blank after saving:
  1. Click the CREATED field header
  2. Click "Customize field type"
  3. Change to: "Created time"
  4. Check "Include a time field"
  5. Save
  6. Delete test record and create new one (CREATED should now auto-fill)

### Problem: "Can't select TYPE options"

**Solution:**
1. Click the TYPE field header
2. Click "Customize field type"
3. Make sure it's "Single select"
4. Add these 4 options:
   - `Capability Gap Analysis`
   - `Subcontractor Recommendation`
   - `Supplier Recommendation`
   - `Compliance Check`
5. Save

### Problem: "STATUS options are wrong"

**Solution:**
1. Click the STATUS field header
2. Click "Customize field type"
3. Make sure these 4 options exist:
   - `Pending Approval`
   - `Approved`
   - `Denied`
   - `Modified`
4. Save

---

## 🧪 ADVANCED TEST: API Integration (Optional)

Once the table works manually, test if the API can access it:

### Test 1: Check if API can read the table

```bash
curl -X GET "https://deedavis.pythonanywhere.com/ai/recommendations" \
  -H "Content-Type: application/json"
```

**Expected:** List of your test records (as JSON)

### Test 2: Check if API can create a record

```bash
curl -X POST "https://deedavis.pythonanywhere.com/ai/recommendations" \
  -H "Content-Type: application/json" \
  -d '{
    "opportunity_id": "recXXXXXX",
    "type": "Compliance Check",
    "recommendation": "Test from API",
    "confidence": 75,
    "reasoning": "API integration test"
  }'
```

**Expected:** Success message + new record appears in Airtable

*(Replace `recXXXXXX` with an actual opportunity record ID from your table)*

---

## ✅ FINAL CHECKLIST

- [ ] Table exists: `AI RECOMMENDATIONS`
- [ ] All 11 fields are present
- [ ] Test record created successfully
- [ ] Test record approved successfully
- [ ] CREATED field auto-fills with timestamp
- [ ] All dropdown options work (TYPE, STATUS, USER_DECISION)
- [ ] Second test record created (optional)
- [ ] API can read records (optional)
- [ ] API can create records (optional)

---

## 🎉 YOU'RE DONE!

**If you can:**
1. ✅ See the table
2. ✅ Create test records
3. ✅ Approve/deny records
4. ✅ All fields save properly

**Then your AI RECOMMENDATIONS table is ready!** 🤖✨

---

## 📞 NEED MORE HELP?

**Still stuck?** Tell me:
1. Which step are you on?
2. What error do you see?
3. What happens when you try?

I'll give you specific fix instructions!

---

**Test setup complete!** Your AI system can now track and approve recommendations! 🚀
