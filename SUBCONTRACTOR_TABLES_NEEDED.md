# 📋 SUBCONTRACTOR SYSTEM - TABLES TO CREATE

**Create these 2 new tables in Airtable:**

---

## **TABLE 1: `GPSS SUBCONTRACTORS`**

### **All Fields:**

1. **COMPANY NAME** (Single line text) - Primary field
2. **SERVICE TYPE** (Single line text)
3. **CITY** (Single line text)
4. **STATE** (Single line text)
5. **PHONE** (Phone number)
6. **EMAIL** (Email)
7. **WEBSITE** (URL)
8. **DESCRIPTION** (Long text)
9. **DISCOVERY METHOD** (Single line text)
10. **DISCOVERY DATE** (Date)
11. **DISCOVERED BY** (Single line text)
12. **RELATIONSHIP STATUS** (Single line text)
13. **RELIABILITY RATING** (Rating 0-5)
14. **RESPONSE RATE (%)** (Number)
15. **CONTRACTS WON TOGETHER** (Number)
16. **LAST CONTACTED** (Date)
17. **SOURCE NOTES** (Long text)
18. **NOTES** (Long text)
19. **CREATED DATE** (Created time)
20. **LAST MODIFIED** (Last modified time)

---

## **TABLE 2: `GPSS SUBCONTRACTOR QUOTES`**

### **All Fields:**

1. **QUOTE ID** (Auto number) - Primary field
2. **OPPORTUNITY** (Link to another record) → Link to "Opportunities"
3. **SUBCONTRACTOR** (Link to another record) → Link to "GPSS SUBCONTRACTORS"
4. **STATUS** (Single line text)
5. **RFQ SENT DATE** (Date)
6. **QUOTE DUE DATE** (Date)
7. **EMAIL SUBJECT** (Single line text)
8. **EMAIL BODY** (Long text)
9. **RESPONSE TEXT** (Long text)
10. **QUOTE AMOUNT** (Currency)
11. **RESPONSE TIME (DAYS)** (Number)
12. **AI SCORE** (Number)
13. **SCORE REASONING** (Long text)
14. **RECOMMENDATION** (Single line text)
15. **SELECTED** (Checkbox)
16. **MARKUP PERCENTAGE** (Number)
17. **MARKUP AMOUNT** (Currency)
18. **FINAL BID AMOUNT** (Currency)
19. **ESTIMATED PROFIT** (Currency)
20. **NOTES** (Long text)
21. **CREATED DATE** (Created time)

---

## ✅ **QUICK CHECKLIST:**

- [ ] Create `GPSS SUBCONTRACTORS` table (20 fields)
- [ ] Create `GPSS SUBCONTRACTOR QUOTES` table (21 fields)
- [ ] Link SUBCONTRACTOR field to GPSS SUBCONTRACTORS
- [ ] Link OPPORTUNITY field to Opportunities
- [ ] Add 1 test subcontractor to verify

**Setup time: 10 minutes**

---

## 📝 **NOTE:**

These are **separate** from your existing supplier tables:
- ✅ `GPSS Suppliers` = Product suppliers
- ✅ `GPSS Supplier Quotes` = Product quotes
- 🆕 `GPSS SUBCONTRACTORS` = Service subcontractors
- 🆕 `GPSS SUBCONTRACTOR QUOTES` = Service quotes

Different purposes, different tables!
