# NEXUS INVOICES - CREATE 8 VIEWS

## 📍 **WHERE YOU ARE:**

1. You're in **Airtable** (on the web or app)
2. Open your **NEXUS Command Center** base
3. Click on the **Invoices** table tab (at the top with all your other tables)
4. You'll see your 46 fields as columns
5. At the VERY TOP LEFT, you'll see **"Grid view"** with a small dropdown arrow ▼

**THIS is where you'll create all your views!**

---

## **VIEW 1: All Invoices** ✅

**This already exists!**

The "Grid view" you're looking at right now IS your "All Invoices" view.

✅ **Nothing to do for View 1!**

---

## **VIEW 2: Pending Payment**

**Shows invoices that have been sent but not yet paid**

### **WHERE TO CLICK:**
Look at the TOP LEFT of your screen. You'll see **"Grid view"** with a small down arrow ▼ next to it.

### **STEPS:**

1. Click **"Grid view"** (the dropdown arrow)
2. Select **"Duplicate view"**
3. A popup appears - type the new name: **Pending Payment**
4. Click **Create**
5. You're now in the new "Pending Payment" view
6. At the top toolbar, click **"Filter"**
7. Click **"Add condition"**
8. First dropdown: Select **Invoice Status**
9. Second dropdown: Select **is**
10. Third dropdown: Select **Sent**
11. Click **"Add condition"** again (to add another condition)
12. First dropdown: Select **Invoice Status**
13. Second dropdown: Select **is**
14. Third dropdown: Select **Pending**
15. At the very top of the filter box, you'll see "Where record meets **all/any** of these conditions"
16. Click it and change to **any** (because we want Sent OR Pending)
17. Close the filter panel (click X or click outside)

✅ **View 2 complete!**

---

## **VIEW 3: Overdue**

**Shows invoices that are past due**

1. Click the **"Grid view"** dropdown again
2. Select **"Duplicate view"**
3. Name it: **Overdue**
4. Click **Create**
5. Click **"Filter"** at the top
6. Click **"Add condition"**
7. First dropdown: **Invoice Status**
8. Second dropdown: **is**
9. Third dropdown: **Overdue**
10. Close the filter panel

✅ **View 3 complete!**

---

## **VIEW 4: Paid**

**Shows invoices that have been paid**

1. Click the **"Grid view"** dropdown
2. Select **"Duplicate view"**
3. Name it: **Paid**
4. Click **Create**
5. Click **"Filter"**
6. Click **"Add condition"**
7. First dropdown: **Invoice Status**
8. Second dropdown: **is**
9. Third dropdown: **Paid**
10. Close the filter panel

✅ **View 4 complete!**

---

## **VIEW 5: Government Contracts**

**Shows all government invoices (Federal, State, Local)**

1. Click the **"Grid view"** dropdown
2. Select **"Duplicate view"**
3. Name it: **Government Contracts**
4. Click **Create**
5. Click **"Filter"**
6. Click **"Add condition"**
7. First dropdown: **Client Type**
8. Second dropdown: **contains**
9. In the text box, type: **Government**
10. Close the filter panel

✅ **View 5 complete!**

(This will show all records where Client Type contains "Government" - so Federal, State, and Local)

---

## **VIEW 6: Enterprise Clients**

**Shows all private enterprise/business invoices**

1. Click the **"Grid view"** dropdown
2. Select **"Duplicate view"**
3. Name it: **Enterprise Clients**
4. Click **Create**
5. Click **"Filter"**
6. Click **"Add condition"**
7. First dropdown: **Client Type**
8. Second dropdown: **is**
9. Third dropdown: **Enterprise - Private**
10. Close the filter panel

✅ **View 6 complete!**

---

## **VIEW 7: By Source System**

**Groups invoices by which system generated them (GPSS, ATLAS, DDCSS, Manual)**

1. Click the **"Grid view"** dropdown
2. Select **"Duplicate view"**
3. Name it: **By Source System**
4. Click **Create**
5. At the top toolbar, click **"Group"**
6. A dropdown appears - select: **Source System**
7. Your invoices are now grouped!

✅ **View 7 complete!**

(You'll see sections like "GPSS", "ATLAS", "DDCSS", "Manual" with invoices grouped under each)

---

## **VIEW 8: This Month**

**Shows only invoices created this month**

1. Click the **"Grid view"** dropdown
2. Select **"Duplicate view"**
3. Name it: **This Month**
4. Click **Create**
5. Click **"Filter"**
6. Click **"Add condition"**
7. First dropdown: **Invoice Date**
8. Second dropdown: **is within**
9. Third dropdown: **this month**
10. Close the filter panel

✅ **View 8 complete!** 🎉

---

## ✅ **ALL 8 VIEWS COMPLETE!**

You should now see all 8 view tabs at the top of your Invoices table:

1. Grid view (All Invoices)
2. Pending Payment
3. Overdue
4. Paid
5. Government Contracts
6. Enterprise Clients
7. By Source System
8. This Month

---

## **ESTIMATED TIME: 10-15 minutes**

---

**Let me know when you're done and I'll start building the Invoice Generator system!** 🚀💰
