# SETUP REMAINING 8 AUTOMATIONS - QUICK GUIDE
**Follow this step-by-step to complete your automation setup**

**Time Required:** 30 minutes  
**Status:** 5 done ✅ | 8 remaining 🆕

---

## 📋 SETUP ORDER

Complete in this order for best results:

1. ✅ Automation 7: High-Value Opportunity ($100K+) - **GPSS**
2. ✅ Automation 8: Delivery Overdue Alert - **FULFILLMENT**
3. ✅ Automation 9: Delivery Due TODAY - **FULFILLMENT**
4. ✅ Automation 10: Invoice Overdue Alert - **VERTEX**
5. ✅ Automation 11: Payment Received - **VERTEX**
6. ✅ Automation 12: Critical Inventory Shortage - **FULFILLMENT**
7. ✅ Automation 13: Project Deadline 24 Hours - **ATLAS**
8. ✅ Automation 14: Expense Payment Due TODAY - **VERTEX**

---

## 🎯 AUTOMATION 7: HIGH-VALUE OPPORTUNITY ($100K+)

**Table:** GPSS OPPORTUNITIES  
**Time:** 3 minutes

### Quick Steps:
1. Open Airtable → GPSS OPPORTUNITIES → Automations
2. Create automation: `💎 High-Value Opportunity Alert`
3. Trigger: When record created
4. Condition: Estimated Value > 100000
5. Action: Send email to info@deedavis.biz
6. Subject: `💎 HIGH VALUE: {Estimated Value} - {Name}`
7. Body: Copy from `ALL_115_AUTOMATIONS_EXCEL_GRID.md` line ~95
8. Turn ON

**Test:** Create opportunity with value $150,000 → Check email

---

## 🎯 AUTOMATION 8: DELIVERY OVERDUE ALERT

**Table:** FULFILLMENT DELIVERIES  
**Time:** 3 minutes

### Quick Steps:
1. Open Airtable → FULFILLMENT DELIVERIES → Automations
2. Create automation: `🚨 Delivery OVERDUE Alert`
3. Trigger: When record matches conditions
4. Condition 1: STATUS is "Pending"
5. Condition 2: SCHEDULED_DATE is before today
6. Action: Send email to info@deedavis.biz
7. Subject: `🚨 OVERDUE: Delivery for {CLIENT_NAME}`
8. Body: Copy from `ALL_115_AUTOMATIONS_EXCEL_GRID.md` line ~130
9. Turn ON

**Test:** Create delivery with yesterday's date, status "Pending" → Check email

---

## 🎯 AUTOMATION 9: DELIVERY DUE TODAY

**Table:** FULFILLMENT DELIVERIES  
**Time:** 3 minutes

### Quick Steps:
1. Open Airtable → FULFILLMENT DELIVERIES → Automations
2. Create automation: `📦 Delivery Due TODAY`
3. Trigger: When record matches conditions
4. Condition 1: STATUS is "Pending"
5. Condition 2: SCHEDULED_DATE is today
6. Action: Send email to info@deedavis.biz
7. Subject: `📦 SHIP TODAY: {PRODUCT_NAME} to {CLIENT_NAME}`
8. Body: Copy from `ALL_115_AUTOMATIONS_EXCEL_GRID.md` line ~165
9. Turn ON

**Test:** Create delivery with today's date, status "Pending" → Check email

---

## 🎯 AUTOMATION 10: INVOICE OVERDUE ALERT

**Table:** VERTEX INVOICES  
**Time:** 3 minutes

### Quick Steps:
1. Open Airtable → VERTEX INVOICES → Automations
2. Create automation: `💰 Invoice OVERDUE Alert`
3. Trigger: When record matches conditions
4. Condition 1: PAYMENT_STATUS is "Unpaid"
5. Condition 2: DUE_DATE is before today
6. Action: Send email to info@deedavis.biz
7. Subject: `💰 OVERDUE: Invoice #{INVOICE_NUMBER} - {CLIENT_NAME}`
8. Body: Copy from `ALL_115_AUTOMATIONS_EXCEL_GRID.md` line ~200
9. Turn ON

**Test:** Create invoice with yesterday's due date, status "Unpaid" → Check email

---

## 🎯 AUTOMATION 11: PAYMENT RECEIVED

**Table:** VERTEX INVOICES  
**Time:** 3 minutes

### Quick Steps:
1. Open Airtable → VERTEX INVOICES → Automations
2. Create automation: `🎉 Payment Received!`
3. Trigger: When record matches conditions
4. Condition: PAYMENT_STATUS is "Paid"
5. Action: Send email to info@deedavis.biz
6. Subject: `🎉 PAID: {TOTAL_AMOUNT} from {CLIENT_NAME}`
7. Body: Copy from `ALL_115_AUTOMATIONS_EXCEL_GRID.md` line ~235
8. Turn ON

**Test:** Create invoice, mark status "Paid" → Check email

---

## 🎯 AUTOMATION 12: CRITICAL INVENTORY SHORTAGE

**Table:** FULFILLMENT INVENTORY  
**Time:** 3 minutes

### Quick Steps:
1. Open Airtable → FULFILLMENT INVENTORY → Automations
2. Create automation: `⚠️ CRITICAL Inventory Shortage`
3. Trigger: When record matches conditions
4. Condition 1: ON_HAND < REORDER_POINT
5. Condition 2: STATUS is not "Reordering"
6. Action: Send email to info@deedavis.biz
7. Subject: `⚠️ CRITICAL: Low stock on {PRODUCT_NAME}`
8. Body: Copy from `ALL_115_AUTOMATIONS_EXCEL_GRID.md` line ~265
9. Turn ON

**Test:** Create inventory item with ON_HAND=5, REORDER_POINT=10 → Check email

---

## 🎯 AUTOMATION 13: PROJECT DEADLINE 24 HOURS

**Table:** ATLAS TASKS  
**Time:** 3 minutes

### Quick Steps:
1. Open Airtable → ATLAS TASKS → Automations
2. Create automation: `⏰ Project Task Due in 24 Hours`
3. Trigger: When record matches conditions
4. Condition 1: STATUS is not "Complete"
5. Condition 2: DUE_DATE is within next 1 day
6. Action: Send email to info@deedavis.biz
7. Subject: `⏰ DUE TOMORROW: {TASK_NAME}`
8. Body: Copy from `ALL_115_AUTOMATIONS_EXCEL_GRID.md` line ~305
9. Turn ON

**Test:** Create task with tomorrow's date, status "In Progress" → Check email

---

## 🎯 AUTOMATION 14: EXPENSE PAYMENT DUE TODAY

**Table:** VERTEX EXPENSES  
**Time:** 3 minutes

### Quick Steps:
1. Open Airtable → VERTEX EXPENSES → Automations
2. Create automation: `💳 Expense Payment DUE TODAY`
3. Trigger: When record matches conditions
4. Condition 1: PAYMENT_STATUS is "Unpaid"
5. Condition 2: DUE_DATE is today
6. Action: Send email to info@deedavis.biz
7. Subject: `💳 PAY TODAY: {AMOUNT} to {SUPPLIER_NAME}`
8. Body: Copy from `ALL_115_AUTOMATIONS_EXCEL_GRID.md` line ~340
9. Turn ON

**Test:** Create expense with today's date, status "Unpaid" → Check email

---

## ✅ COMPLETION CHECKLIST

After setting up all 8 automations:

- [ ] All 8 automations turned ON in Airtable
- [ ] Test each automation with sample data
- [ ] Verify emails received at info@deedavis.biz
- [ ] Delete test records after verification
- [ ] Check dashboard at http://localhost:3000
- [ ] Verify Activity Stream shows updates
- [ ] Verify Alerts section shows urgent items
- [ ] Verify auto-refresh works (wait 30 seconds)

---

## 🚨 TROUBLESHOOTING

**No email received?**
- Check automation is turned ON
- Verify email address is correct
- Check spam/junk folder
- Test with "Use suggested record"

**Field not found?**
- Verify table has required fields
- Check field name spelling (ALL CAPS)
- See `FULFILLMENT_AIRTABLE_SETUP.md` for missing tables

**Automation triggers too often?**
- Add more conditions to narrow scope
- Check date formulas are correct
- Review trigger logic (AND vs OR)

**Email template broken?**
- Copy exact template from grid file
- Use Airtable field picker for variables
- Test with real record, not suggested

---

## 🎉 WHEN YOU'RE DONE

**You'll have:**
- ✅ 14 critical email automations working
- ✅ 100+ dashboard notifications automatic
- ✅ Complete visibility into your business
- ✅ Only 1-5 critical emails per day
- ✅ Everything else in your dashboard

**Total setup time:** 30 minutes  
**Daily time saved:** 45 minutes  
**ROI:** 90x time savings

---

## 📚 FULL DOCUMENTATION

See these files for complete details:
- **Step-by-step grids:** `ALL_115_AUTOMATIONS_EXCEL_GRID.md`
- **Strategy explanation:** `NEXUS_AUTOMATIONS_FINAL_STRATEGY.md`
- **System flows:** `COMPLETE_SYSTEM_FLOWS.md`
- **Master guide:** `NEXUS_AIRTABLE_AUTOMATIONS_COMPLETE_GUIDE.md`

---

**Ready? Start with Automation #7 and work your way down! 🚀**

**You got this! Only 30 minutes to complete automation nirvana!**
