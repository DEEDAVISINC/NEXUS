# NEXUS INVOICES TABLE - GOVERNMENT & ENTERPRISE COMPLIANT

## **Fields to Add (46 fields):**

---

### **INVOICE BASICS**

1. **Invoice ID** - Autonumber (rename "Name" field)
2. **Invoice Number** - Formula: `"INV-" & YEAR({Invoice Date}) & "-" & TEXT({Invoice ID}, "0000")`
3. **Invoice Date** - Date
4. **Due Date** - Date
5. **Invoice Status** - Single select: Draft, Sent, Pending, Paid, Overdue, Cancelled

---

### **CLIENT INFORMATION**

6. **Client Name** - Single line text
7. **Client Type** - Single select: Government - Federal, Government - State, Government - Local, Enterprise - Private, Small Business
8. **Contact** - Link to "Contacts" table
9. **Bill To Address** - Long text

---

### **SOURCE LINKING** (What generated this invoice)

10. **Source System** - Single select: GPSS, ATLAS, DDCSS, Manual
11. **Opportunity** - Link to "Opportunities" table (GPSS)
12. **Project** - Link to "ATLAS Projects" table
13. **Prospect** - Link to "DDCSS Prospects" table

---

### **GOVERNMENT CONTRACT FIELDS**

14. **Contract Number** - Single line text
15. **Contract Type** - Single select: FFP (Fixed Price), T&M (Time & Materials), Cost Plus, IDIQ, Task Order, BPA Call
16. **CAGE Code** - Single line text (default: 8UMX3)
17. **UEI Number** - Single line text
18. **CLIN Items** - Long text (Contract Line Item Numbers)
19. **Period of Performance** - Single line text (e.g., "01/01/2024 - 12/31/2024")
20. **POP Start Date** - Date
21. **POP End Date** - Date
22. **Contracting Officer** - Single line text
23. **Contracting Officer Email** - Email
24. **Payment Office** - Single line text
25. **WAWF Required** - Checkbox

---

### **ENTERPRISE/COMMERCIAL FIELDS**

26. **Purchase Order Number** - Single line text
27. **Payment Terms** - Single select: Net 15, Net 30, Net 45, Net 60, Due on Receipt, Custom
28. **Project Name** - Single line text

---

### **INVOICE AMOUNTS**

29. **Subtotal** - Currency (USD, 2 decimals)
30. **Shipping & Handling** - Currency (USD, 2 decimals)
31. **Tax Rate** - Percent (2 decimals)
32. **Tax Amount** - Formula: `{Subtotal} * {Tax Rate}` (format as Currency)
33. **Total Amount** - Formula: `{Subtotal} + {Shipping & Handling} + {Tax Amount}` (format as Currency)

---

### **LINE ITEMS** (Structured Text)

34. **Line Items** - Long text (Format: Description | Quantity | Rate | Amount)

---

### **PAYMENT TRACKING**

35. **Payment Date** - Date
36. **Payment Method** - Single select: ACH, Wire Transfer, Check, Credit Card, Government Portal (WAWF), Other
37. **Payment Reference** - Single line text
38. **Days Outstanding** - Formula: `IF({Invoice Status} = "Paid", 0, DATETIME_DIFF(TODAY(), {Invoice Date}, 'days'))` (format as Integer)

---

### **NOTES & COMPLIANCE**

39. **Invoice Notes** - Long text
40. **Terms & Conditions** - Long text
41. **Special Instructions** - Long text
42. **Sent To Email** - Email
43. **Sent Date** - Date (with time)

---

### **SYSTEM TRACKING**

44. **Created By** - Single line text (system/user)
45. **Last Modified** - Last modified time
46. **Created Date** - Created time

---

## **OPTIONAL:**

47. **Shipments** - Link to "Shipments" table (for tracking physical deliveries)

---

## 📋 **VIEWS TO CREATE:**

1. **All Invoices** - Default view
2. **Pending Payment** - Filter: Status = Sent or Pending
3. **Overdue** - Filter: Status = Overdue
4. **Paid** - Filter: Status = Paid
5. **Government Contracts** - Filter: Client Type contains "Government"
6. **Enterprise Clients** - Filter: Client Type = Enterprise - Private
7. **By Source System** - Group by: Source System
8. **This Month** - Filter: Invoice Date is within this month

---

## 🏛️ **GOVERNMENT COMPLIANCE FEATURES:**

✅ **Contract Number** - Required for all government invoices  
✅ **CLIN Items** - Track Contract Line Item Numbers  
✅ **Period of Performance** - Required by FAR  
✅ **CAGE Code** - Your contractor identification (8UMX3)  
✅ **UEI** - Universal Entity Identifier  
✅ **WAWF Ready** - Flag for Wide Area Workflow invoices  
✅ **Contracting Officer Info** - Who to send to  
✅ **Payment Office** - Where payment comes from  
✅ **Prompt Payment Act** - Auto-calculates days outstanding  

---

## 💼 **ENTERPRISE COMPLIANCE FEATURES:**

✅ **Purchase Order Number** - Required by most enterprises  
✅ **Flexible Payment Terms** - Net 15/30/45/60  
✅ **Professional Formatting** - Clean, professional layout  
✅ **Tax Calculation** - Automatic tax computation  
✅ **Multiple Payment Methods** - ACH, Wire, Check, Card  
✅ **Proper Invoice Numbering** - INV-2024-0001 format  

---

## 🚨 **KEY DIFFERENCES FROM YOUR ORIGINAL SPEC:**

Your original had **35 fields**, but the correct version has **46 fields**.

### **What's Different:**

**ADDED (now included):**
- Field 8: **Contact** - Link to Contacts table ✅
- Field 11: **Opportunity** - Link to Opportunities table ✅
- Field 12: **Project** - Link to ATLAS Projects table ✅
- Field 13: **Prospect** - Link to DDCSS Prospects table ✅
- Field 30: **Shipping & Handling** - Currency (for calculated shipping fees) ✅
- Field 44: **Created By** - Single line text ✅

**These 6 fields bring the total from 35 to 46 fields.**

---

**Use this list as your reference while creating the table in NEXUS Command Center!** 📋✨

For detailed step-by-step instructions on HOW to create each field, refer to: `INVOICES_CORRECT_SETUP.md`
