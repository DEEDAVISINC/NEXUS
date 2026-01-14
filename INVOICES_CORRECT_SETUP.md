# NEXUS INVOICES TABLE - CORRECT COMPLETE SETUP
## (For NEXUS Command Center - Single Base)

---

## 🚨 **WHAT WAS MISSING/WRONG IN PREVIOUS VERSION:**

### ❌ **REMOVED (but shouldn't have been):**
- **Contact** - Should be "Link to Contacts table" (I changed it to Contact Name + Contact Email text fields)
- **Created By** - Missing entirely (should be Single line text)

### ⚠️ **ADDED (but wasn't in original spec):**
- **Contact Name** - I added this as text (should be removed)
- **Contact Email** - I added this as text (should be removed)  
- **Source Record ID** - I added this (not needed in single base)
- **Source Reference** - I added this (not needed in single base)
- **Amount Paid** - I added this (not in original spec)

### ✅ **CORRECT NOW:**
Since you're in **NEXUS Command Center** (ONE base with all tables), the links will work properly!

---

## **CORRECT FIELD COUNT: 45 FIELDS**

---

## **PART 1: CREATE THE TABLE**

1. Open **NEXUS Command Center** base in Airtable
2. Click the **"+"** button next to your last table tab
3. Select **"Create empty table"**
4. Name it: **Invoices**
5. Click **Create**

---

## **PART 2: SET UP ALL FIELDS**

---

### **FIELD 1: Invoice ID**

1. Click on the **"Name"** column header
2. Click **"Customize field type"**
3. Change name to: **Invoice ID**
4. Click **"Autonumber"** field type
5. Click **Save**

✅ **Field 1 complete!**

---

### **FIELD 2: Invoice Number**

1. Click the **"+"** button
2. Field name: **Invoice Number**
3. Click **"Formula"** field type
4. Formula:
   ```
   "INV-" & YEAR({Invoice Date}) & "-" & TEXT({Invoice ID}, "0000")
   ```
5. Click **Create field**

✅ **Field 2 complete!**

---

### **FIELD 3: Invoice Date**

1. Click the **"+"** button
2. Field name: **Invoice Date**
3. Click **"Date"** field type
4. Date format: **Local** (M/D/YYYY)
5. Include a time field: **No**
6. Click **Create field**

✅ **Field 3 complete!**

---

### **FIELD 4: Due Date**

1. Click the **"+"** button
2. Field name: **Due Date**
3. Click **"Date"** field type
4. Date format: **Local** (M/D/YYYY)
5. Include a time field: **No**
6. Click **Create field**

✅ **Field 4 complete!**

---

### **FIELD 5: Invoice Status**

1. Click the **"+"** button
2. Field name: **Invoice Status**
3. Click **"Single select"** field type
4. Add these 6 options:
   - **Draft** (Gray)
   - **Sent** (Blue)
   - **Pending** (Yellow)
   - **Paid** (Green)
   - **Overdue** (Red)
   - **Cancelled** (Gray)
5. Click **Create field**

✅ **Field 5 complete!**

---

### **FIELD 6: Client Name**

1. Click the **"+"** button
2. Field name: **Client Name**
3. Click **"Single line text"** field type
4. Click **Create field**

✅ **Field 6 complete!**

---

### **FIELD 7: Client Type**

1. Click the **"+"** button
2. Field name: **Client Type**
3. Click **"Single select"** field type
4. Add these 5 options:
   - **Government - Federal**
   - **Government - State**
   - **Government - Local**
   - **Enterprise - Private**
   - **Small Business**
5. Click **Create field**

✅ **Field 7 complete!**

---

### **FIELD 8: Contact** 🆕 **CORRECTED - WAS MISSING!**

1. Click the **"+"** button
2. Field name: **Contact**
3. Click **"Link to another record"** field type
4. In the popup:
   - Select **"Choose an existing table"**
   - Find and select: **Contacts** (from DDCSS)
   - Allow linking to multiple records: **No** (one contact per invoice)
5. Click **Create field**

✅ **Field 8 complete!** (This was wrong in previous version - I had Contact Name + Contact Email as text)

---

### **FIELD 9: Bill To Address**

1. Click the **"+"** button
2. Field name: **Bill To Address**
3. Click **"Long text"** field type
4. Toggle **"Enable rich text formatting"** to **OFF**
5. Click **Create field**

✅ **Field 9 complete!**

---

### **FIELD 10: Source System**

1. Click the **"+"** button
2. Field name: **Source System**
3. Click **"Single select"** field type
4. Add these 4 options:
   - **GPSS**
   - **ATLAS**
   - **DDCSS**
   - **Manual**
5. Click **Create field**

✅ **Field 10 complete!**

---

### **FIELD 11: Opportunity** 🆕 **NOW WORKS WITH SINGLE BASE!**

1. Click the **"+"** button
2. Field name: **Opportunity**
3. Click **"Link to another record"** field type
4. In the popup:
   - Select **"Choose an existing table"**
   - Find and select: **Opportunities** (from GPSS)
   - Allow linking to multiple records: **No**
5. Click **Create field**

✅ **Field 11 complete!**

---

### **FIELD 12: Project** 🆕 **NOW WORKS WITH SINGLE BASE!**

1. Click the **"+"** button
2. Field name: **Project**
3. Click **"Link to another record"** field type
4. In the popup:
   - Select **"Choose an existing table"**
   - Find and select: **ATLAS Projects**
   - Allow linking to multiple records: **No**
5. Click **Create field**

✅ **Field 12 complete!**

---

### **FIELD 13: Prospect** 🆕 **NOW WORKS WITH SINGLE BASE!**

1. Click the **"+"** button
2. Field name: **Prospect**
3. Click **"Link to another record"** field type
4. In the popup:
   - Select **"Choose an existing table"**
   - Find and select: **DDCSS Prospects**
   - Allow linking to multiple records: **No**
5. Click **Create field**

✅ **Field 13 complete!**

---

### **FIELD 14: Contract Number**

1. Click the **"+"** button
2. Field name: **Contract Number**
3. Click **"Single line text"** field type
4. Click **Create field**

✅ **Field 14 complete!**

---

### **FIELD 15: Contract Type**

1. Click the **"+"** button
2. Field name: **Contract Type**
3. Click **"Single select"** field type
4. Add these 6 options:
   - **FFP (Fixed Price)**
   - **T&M (Time & Materials)**
   - **Cost Plus**
   - **IDIQ**
   - **Task Order**
   - **BPA Call**
5. Click **Create field**

✅ **Field 15 complete!**

---

### **FIELD 16: CAGE Code**

1. Click the **"+"** button
2. Field name: **CAGE Code**
3. Click **"Single line text"** field type
4. Default value: **8UMX3**
5. Click **Create field**

✅ **Field 16 complete!**

---

### **FIELD 17: UEI Number**

1. Click the **"+"** button
2. Field name: **UEI Number**
3. Click **"Single line text"** field type
4. Click **Create field**

✅ **Field 17 complete!**

---

### **FIELD 18: CLIN Items**

1. Click the **"+"** button
2. Field name: **CLIN Items**
3. Click **"Long text"** field type
4. Toggle **"Enable rich text formatting"** to **OFF**
5. Click **Create field**

✅ **Field 18 complete!**

---

### **FIELD 19: Period of Performance**

1. Click the **"+"** button
2. Field name: **Period of Performance**
3. Click **"Single line text"** field type
4. Click **Create field**

✅ **Field 19 complete!**

---

### **FIELD 20: POP Start Date**

1. Click the **"+"** button
2. Field name: **POP Start Date**
3. Click **"Date"** field type
4. Date format: **Local** (M/D/YYYY)
5. Include a time field: **No**
6. Click **Create field**

✅ **Field 20 complete!**

---

### **FIELD 21: POP End Date**

1. Click the **"+"** button
2. Field name: **POP End Date**
3. Click **"Date"** field type
4. Date format: **Local** (M/D/YYYY)
5. Include a time field: **No**
6. Click **Create field**

✅ **Field 21 complete!**

---

### **FIELD 22: Contracting Officer**

1. Click the **"+"** button
2. Field name: **Contracting Officer**
3. Click **"Single line text"** field type
4. Click **Create field**

✅ **Field 22 complete!**

---

### **FIELD 23: Contracting Officer Email**

1. Click the **"+"** button
2. Field name: **Contracting Officer Email**
3. Click **"Email"** field type
4. Click **Create field**

✅ **Field 23 complete!**

---

### **FIELD 24: Payment Office**

1. Click the **"+"** button
2. Field name: **Payment Office**
3. Click **"Single line text"** field type
4. Click **Create field**

✅ **Field 24 complete!**

---

### **FIELD 25: WAWF Required**

1. Click the **"+"** button
2. Field name: **WAWF Required**
3. Click **"Checkbox"** field type
4. Click **Create field**

✅ **Field 25 complete!**

---

### **FIELD 26: Purchase Order Number**

1. Click the **"+"** button
2. Field name: **Purchase Order Number**
3. Click **"Single line text"** field type
4. Click **Create field**

✅ **Field 26 complete!**

---

### **FIELD 27: Payment Terms**

1. Click the **"+"** button
2. Field name: **Payment Terms**
3. Click **"Single select"** field type
4. Add these 6 options:
   - **Net 15**
   - **Net 30**
   - **Net 45**
   - **Net 60**
   - **Due on Receipt**
   - **Custom**
5. Click **Create field**

✅ **Field 27 complete!**

---

### **FIELD 28: Project Name**

1. Click the **"+"** button
2. Field name: **Project Name**
3. Click **"Single line text"** field type
4. Click **Create field**

✅ **Field 28 complete!**

---

### **FIELD 29: Subtotal**

1. Click the **"+"** button
2. Field name: **Subtotal**
3. Click **"Currency"** field type
4. Currency: **USD ($)**
5. Precision: **2 decimals** (0.00)
6. Click **Create field**

✅ **Field 29 complete!**

---

### **FIELD 30: Tax Rate**

1. Click the **"+"** button
2. Field name: **Tax Rate**
3. Click **"Percent"** field type
4. Precision: **2 decimals** (0.00%)
5. Click **Create field**

✅ **Field 30 complete!**

---

### **FIELD 31: Tax Amount**

1. Click the **"+"** button
2. Field name: **Tax Amount**
3. Click **"Formula"** field type
4. Formula:
   ```
   {Subtotal} * {Tax Rate}
   ```
5. Click **"Customize field type"** at bottom
6. Select **Currency**
7. Currency: **USD ($)**
8. Precision: **2 decimals**
9. Click **Save**
10. Click **Create field**

✅ **Field 31 complete!**

---

### **FIELD 32: Total Amount**

1. Click the **"+"** button
2. Field name: **Total Amount**
3. Click **"Formula"** field type
4. Formula:
   ```
   {Subtotal} + {Tax Amount}
   ```
5. Click **"Customize field type"** at bottom
6. Select **Currency**
7. Currency: **USD ($)**
8. Precision: **2 decimals**
9. Click **Save**
10. Click **Create field**

✅ **Field 32 complete!**

---

### **FIELD 33: Line Items**

1. Click the **"+"** button
2. Field name: **Line Items**
3. Click **"Long text"** field type
4. Toggle **"Enable rich text formatting"** to **OFF**
5. Click **Create field**

✅ **Field 33 complete!**

---

### **FIELD 34: Payment Date**

1. Click the **"+"** button
2. Field name: **Payment Date**
3. Click **"Date"** field type
4. Date format: **Local** (M/D/YYYY)
5. Include a time field: **No**
6. Click **Create field**

✅ **Field 34 complete!**

---

### **FIELD 35: Payment Method**

1. Click the **"+"** button
2. Field name: **Payment Method**
3. Click **"Single select"** field type
4. Add these 6 options:
   - **ACH**
   - **Wire Transfer**
   - **Check**
   - **Credit Card**
   - **Government Portal (WAWF)**
   - **Other**
5. Click **Create field**

✅ **Field 35 complete!**

---

### **FIELD 36: Payment Reference**

1. Click the **"+"** button
2. Field name: **Payment Reference**
3. Click **"Single line text"** field type
4. Click **Create field**

✅ **Field 36 complete!**

---

### **FIELD 37: Days Outstanding**

1. Click the **"+"** button
2. Field name: **Days Outstanding**
3. Click **"Formula"** field type
4. Formula:
   ```
   IF({Invoice Status} = "Paid", 0, DATETIME_DIFF(TODAY(), {Invoice Date}, 'days'))
   ```
5. Click **"Customize field type"** at bottom
6. Select **Integer**
7. Click **Save**
8. Click **Create field**

✅ **Field 37 complete!**

---

### **FIELD 38: Invoice Notes**

1. Click the **"+"** button
2. Field name: **Invoice Notes**
3. Click **"Long text"** field type
4. Toggle **"Enable rich text formatting"** to **OFF**
5. Click **Create field**

✅ **Field 38 complete!**

---

### **FIELD 39: Terms & Conditions**

1. Click the **"+"** button
2. Field name: **Terms & Conditions**
3. Click **"Long text"** field type
4. Toggle **"Enable rich text formatting"** to **OFF**
5. Click **Create field**

✅ **Field 39 complete!**

---

### **FIELD 40: Special Instructions**

1. Click the **"+"** button
2. Field name: **Special Instructions**
3. Click **"Long text"** field type
4. Toggle **"Enable rich text formatting"** to **OFF**
5. Click **Create field**

✅ **Field 40 complete!**

---

### **FIELD 41: Sent To Email**

1. Click the **"+"** button
2. Field name: **Sent To Email**
3. Click **"Email"** field type
4. Click **Create field**

✅ **Field 41 complete!**

---

### **FIELD 42: Sent Date**

1. Click the **"+"** button
2. Field name: **Sent Date**
3. Click **"Date"** field type
4. Date format: **Local** (M/D/YYYY)
5. Include a time field: **Yes**
6. Time format: **12 hour**
7. Click **Create field**

✅ **Field 42 complete!**

---

### **FIELD 43: Created By** 🆕 **WAS COMPLETELY MISSING!**

1. Click the **"+"** button
2. Field name: **Created By**
3. Click **"Single line text"** field type
4. Click **Create field**

✅ **Field 43 complete!** (This field was MISSING entirely in my previous version)

---

### **FIELD 44: Last Modified**

1. Click the **"+"** button
2. Field name: **Last Modified**
3. Click **"Last modified time"** field type
4. Date format: **Local** (M/D/YYYY)
5. Time format: **12 hour**
6. Click **Create field**

✅ **Field 44 complete!**

---

### **FIELD 45: Created Date**

1. Click the **"+"** button
2. Field name: **Created Date**
3. Click **"Created time"** field type
4. Date format: **Local** (M/D/YYYY)
5. Time format: **12 hour**
6. Click **Create field**

✅ **Field 45 complete!** 🎉

---

## **OPTIONAL FIELD 46: Shipments** 📦

If you want to link to a Shipments table for tracking deliveries:

1. Click the **"+"** button
2. Field name: **Shipments**
3. Click **"Link to another record"** field type
4. Create new table: **Shipments** (or link to existing)
5. Allow linking to multiple records: **Yes**
6. Click **Create field**

✅ **Optional Field 46 complete!**

---

## **PART 3: CREATE VIEWS**

---

### **VIEW 1: All Invoices**
- Default "Grid view" - leave as is

✅ **View 1 complete!**

---

### **VIEW 2: Pending Payment**

1. Click **"Grid view"** dropdown
2. Select **"Duplicate view"**
3. Name: **Pending Payment**
4. Click **Filter**
5. Add condition: **Invoice Status** is **Sent**
6. Add condition: **Invoice Status** is **Pending**
7. Change to "Where record meets **ANY** of these conditions"
8. Done

✅ **View 2 complete!**

---

### **VIEW 3: Overdue**

1. Duplicate Grid view
2. Name: **Overdue**
3. Filter: **Invoice Status** is **Overdue**
4. Done

✅ **View 3 complete!**

---

### **VIEW 4: Paid**

1. Duplicate Grid view
2. Name: **Paid**
3. Filter: **Invoice Status** is **Paid**
4. Done

✅ **View 4 complete!**

---

### **VIEW 5: Government Contracts**

1. Duplicate Grid view
2. Name: **Government Contracts**
3. Filter: **Client Type** contains **"Government"**
4. Done

✅ **View 5 complete!**

---

### **VIEW 6: Enterprise Clients**

1. Duplicate Grid view
2. Name: **Enterprise Clients**
3. Filter: **Client Type** is **Enterprise - Private**
4. Done

✅ **View 6 complete!**

---

### **VIEW 7: By Source System**

1. Duplicate Grid view
2. Name: **By Source System**
3. Click **Group**
4. Group by: **Source System**
5. Done

✅ **View 7 complete!**

---

### **VIEW 8: This Month**

1. Duplicate Grid view
2. Name: **This Month**
3. Filter: **Invoice Date** is within **this month**
4. Done

✅ **View 8 complete!** 🎉

---

## ✅ **NEXUS COMMAND CENTER - INVOICES TABLE COMPLETE!**

**Total: 45 fields + 8 views**

---

## 🚨 **SUMMARY OF CORRECTIONS:**

### **WHAT WAS WRONG:**
1. ❌ Field 8: I had "Contact Name" (text) instead of "Contact" (link)
2. ❌ I added "Contact Email" (text) - should not exist
3. ❌ I added "Source Record ID" - not needed in single base
4. ❌ I added "Source Reference" - not needed in single base
5. ❌ I added "Amount Paid" - not in original spec
6. ❌ Field 43: "Created By" was COMPLETELY MISSING

### **NOW CORRECT:**
1. ✅ Contact - Link to Contacts table
2. ✅ Opportunity - Link to Opportunities table
3. ✅ Project - Link to ATLAS Projects table
4. ✅ Prospect - Link to DDCSS Prospects table
5. ✅ Created By - Single line text (ADDED BACK)
6. ✅ All 45 fields match original spec
7. ✅ All 8 views included

---

**Now follow this guide step-by-step in your NEXUS Command Center!** 🚀💰

**Let me know when you're done!**
