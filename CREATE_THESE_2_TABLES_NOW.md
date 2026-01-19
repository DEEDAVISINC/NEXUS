# Create These 2 Airtable Tables Now

## Quick 10-Minute Fix

You need to create 2 missing tables in Airtable. Here's exactly how:

---

## **Step 1: Go to Your Airtable Base**

**URL:** https://airtable.com/appaJZqKVUn3yJ7ma/

---

## **Step 2: Create Table #1 - DDCSS CERTIFICATIONS**

### **2.1 Create the Table**
1. Click the **"+" button** at the top (next to your other tables)
2. Select **"Start from scratch"**
3. Name it: **DDCSS CERTIFICATIONS**
4. Click **"Create table"**

### **2.2 Add These Fields**

| Field Name | Type | Options |
|------------|------|---------|
| **Certification Name** | Single line text | - |
| **Type** | Single select | Options: `8(a)`, `HUBZone`, `WOSB`, `EDWOSB`, `SDVOSB`, `DBE` |
| **Status** | Single select | Options: `Active`, `Pending`, `Expired`, `Applied` |
| **Expiration Date** | Date | - |
| **Certifying Agency** | Single line text | - |
| **Notes** | Long text | - |

### **How to add fields:**
1. Click the **"+"** in the column header
2. Select field type
3. Name the field
4. For "Single select" - add the options listed above
5. Click **"Create field"**

---

## **Step 3: Create Table #2 - LBPC CONTRACTS**

### **3.1 Create the Table**
1. Click the **"+" button** again
2. Select **"Start from scratch"**
3. Name it: **LBPC CONTRACTS**
4. Click **"Create table"**

### **3.2 Add These Fields**

| Field Name | Type | Options |
|------------|------|---------|
| **Contract Name** | Single line text | - |
| **Client Name** | Single line text | - |
| **Contract Value** | Currency | Format: USD |
| **Start Date** | Date | - |
| **End Date** | Date | - |
| **Status** | Single select | Options: `Active`, `Completed`, `Terminated` |
| **Payment Terms** | Single line text | - |
| **Notes** | Long text | - |

---

## **Step 4: Verify**

After creating both tables, you should see them in your base:

```
✓ DDCSS CERTIFICATIONS (new)
✓ LBPC CONTRACTS (new)
```

---

## **That's It!**

Once you create these 2 tables, your system will be **95% operational**.

The DDCSS and LBPC systems will be able to store all their data.

---

## **After You're Done:**

Refresh your NEXUS frontend dashboard (http://localhost:3000)

The DDCSS and LBPC stats should load without errors.

---

**Time to complete: 10 minutes**

**Then tomorrow: Import 100 opportunities when GovCon resets!**
