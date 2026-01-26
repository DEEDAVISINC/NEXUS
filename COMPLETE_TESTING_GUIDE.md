# NEXUS COMPLETE TESTING GUIDE
## All Systems Testing Checklist

**Date:** January 21, 2026  
**Purpose:** Test all NEXUS systems before deployment  
**Time Required:** 30-45 minutes for complete testing

---

## 🎯 TESTING PRIORITY

### **Priority 1: Critical Systems (Test First - 15 min)**
1. AI Recommendation System
2. Subcontractor System
3. Fulfillment System
4. Officer Outreach System

### **Priority 2: Core Systems (10 min)**
5. GPSS Opportunities
6. Financial Tracking
7. Supplier System

### **Priority 3: Supporting Systems (10 min)**
8. ATLAS Project Management
9. DDCSS Corporate Sales
10. LBPC Surplus Recovery

---

## 🚀 QUICK START

### **One-Command Full Test:**
```bash
# Run comprehensive test suite
python test_system_comprehensive.py
```

### **Individual System Tests:**
```bash
# AI Recommendations
python test_ai_recommendations.py

# Fulfillment System
python test_fulfillment_system.py

# Officer Outreach
python contracting_officer_outreach.py

# Start API Server (for endpoint testing)
python api_server.py
```

---

## 📋 SYSTEM-BY-SYSTEM TESTING

---

## 1. AI RECOMMENDATION SYSTEM ⭐ NEW

### **What to Test:**
- [ ] Capability gap analysis
- [ ] Subcontractor recommendations
- [ ] Supplier recommendations
- [ ] Approve/deny workflow
- [ ] Compliance calculator

### **How to Test:**

**Option A: Automated Test Script**
```bash
python test_ai_recommendations.py
```

**Option B: Manual API Testing**
```bash
# Terminal 1: Start server
python api_server.py

# Terminal 2: Test endpoints
# 1. Capability Gap Analysis
curl -X POST http://localhost:5000/ai/recommendations/capability-gap \
  -H "Content-Type: application/json" \
  -d '{"opportunity_id": "recYOUR_OPP_ID"}'

# 2. Get Pending Recommendations
curl http://localhost:5000/ai/recommendations/pending

# 3. Compliance Calculator
curl -X POST http://localhost:5000/ai/compliance/calculate \
  -H "Content-Type: application/json" \
  -d '{"contract_value": 500000, "your_work_value": 280000, "subcontractor_work_value": 180000}'
```

### **Expected Results:**
- ✅ AI analyzes opportunity and creates recommendation
- ✅ Recommendation saved to Airtable (AI RECOMMENDATIONS table)
- ✅ Confidence score (0-100) displayed
- ✅ Reasoning provided
- ✅ Compliance check returns compliant/non-compliant status

### **Verify in Airtable:**
- Open AI RECOMMENDATIONS table
- See new record with STATUS = "Pending Approval"
- Check CONFIDENCE and REASONING fields populated

---

## 2. SUBCONTRACTOR SYSTEM ⭐ NEW

### **What to Test:**
- [ ] Find subcontractors by service type
- [ ] Search existing subcontractors
- [ ] Generate RFQ emails
- [ ] Send bulk RFQs
- [ ] AI score quotes
- [ ] Calculate markup
- [ ] Generate bid summaries

### **How to Test:**

```bash
# Start server
python api_server.py

# Test in another terminal:

# 1. Find Subcontractors
curl -X POST http://localhost:5000/gpss/subcontractors/find \
  -H "Content-Type: application/json" \
  -d '{"service_type": "janitorial", "location": "Virginia Beach VA", "max_results": 10}'

# 2. Search Existing
curl -X POST http://localhost:5000/gpss/subcontractors/search \
  -H "Content-Type: application/json" \
  -d '{"service_type": "janitorial", "location": "Virginia", "min_rating": 3.5}'

# 3. Generate RFQ
curl -X POST http://localhost:5000/gpss/subcontractors/rfq/generate \
  -H "Content-Type: application/json" \
  -d '{
    "subcontractor": {"company_name": "Test Co", "email": "test@test.com"},
    "opportunity": {"service_type": "cleaning", "value": 100000},
    "scope": "Clean offices weekly"
  }'
```

### **Expected Results:**
- ✅ Returns list of subcontractors
- ✅ Subcontractors have contact info and capabilities
- ✅ RFQ email generated with professional content
- ✅ Quotes tracked in GPSS SUBCONTRACTOR QUOTES table

### **Verify in Airtable:**
- Check GPSS SUBCONTRACTORS table has records
- Check GPSS SUBCONTRACTOR QUOTES table for RFQs

---

## 3. FULFILLMENT SYSTEM ⭐ NEW

### **What to Test:**
- [ ] Create fulfillment contract
- [ ] Get active contracts
- [ ] Track deliveries
- [ ] Update delivery status
- [ ] Inventory health check
- [ ] Create purchase orders
- [ ] Receive POs
- [ ] Dashboard view

### **How to Test:**

**Automated Test:**
```bash
python test_fulfillment_system.py
```

**Manual API Test:**
```bash
# Start server
python api_server.py

# Test endpoints:

# 1. Create Contract
curl -X POST http://localhost:5000/fulfillment/contracts \
  -H "Content-Type: application/json" \
  -d '{
    "product_name": "Test Product",
    "total_quantity": 1000,
    "unit_price": 10.00,
    "delivery_frequency": "Monthly",
    "supplier_id": "recSUPPLIER_ID"
  }'

# 2. Check Inventory Health
curl http://localhost:5000/fulfillment/inventory/health-check

# 3. Get Active Contracts
curl http://localhost:5000/fulfillment/contracts

# 4. Dashboard
curl http://localhost:5000/fulfillment/dashboard
```

### **Expected Results:**
- ✅ Contract created with auto-generated delivery schedule
- ✅ Inventory tracking initialized
- ✅ Health check identifies low stock
- ✅ Dashboard shows all data

### **Verify in Airtable:**
- FULFILLMENT CONTRACTS table has new contract
- FULFILLMENT DELIVERIES table has scheduled deliveries
- FULFILLMENT INVENTORY table tracking stock
- FULFILLMENT PURCHASE ORDERS table (if PO created)

---

## 4. OFFICER OUTREACH SYSTEM ⭐ NEW

### **What to Test:**
- [ ] Finds closed opportunities
- [ ] Generates introduction letters
- [ ] ProposalBio™ scores letters
- [ ] Saves to Airtable
- [ ] Links to opportunities

### **How to Test:**

```bash
# Run officer outreach system
python contracting_officer_outreach.py
```

### **Expected Results:**
```
Found X closed opportunities to reach out on

[1/X] Processing: Female Condoms...
    🟢 HIGH QUALITY ProposalBio™ Score: 78.3/100
    ✅ Letter saved to Airtable

✅ Generated: X letters
📊 Average ProposalBio™ Score: 76.8/100
```

### **Verify in Airtable:**
- Open **Officer Outreach Tracking** table
- See new records with STATUS = "Draft"
- Check LETTER_CONTENT field has full letter
- Check PROPOSALBIO_SCORE field (should be 60-90)
- Verify links to GPSS OPPORTUNITIES

### **Check Opportunities Table:**
- Open GPSS OPPORTUNITIES
- Closed opportunities should have:
  - Officer Outreach Sent = ✓
  - Officer Outreach Date = today
  - Officer Outreach Link = link to letter

---

## 5. FINANCIAL TRACKING (VERTEX)

### **What to Test:**
- [ ] Invoice generation
- [ ] Expense tracking
- [ ] Profit calculation
- [ ] Invoice/expense linking

### **How to Test:**

```bash
# Start server
python api_server.py

# Test invoice generation
curl -X POST http://localhost:5000/invoices/generate/opportunity \
  -H "Content-Type: application/json" \
  -d '{"opportunity_id": "recOPP_ID"}'

# Get invoices
curl http://localhost:5000/invoices

# Check expenses
# (Created automatically by fulfillment deliveries)
```

### **Expected Results:**
- ✅ Invoice created with line items
- ✅ Expense created for COGS
- ✅ Profit = Revenue - Expenses
- ✅ Links to opportunity/contract

### **Verify in Airtable:**
- Check **Invoices** or **VERTEX INVOICES** table
- Check **VERTEX EXPENSES** table
- Verify amounts are correct
- Check links between records

---

## 6. GPSS OPPORTUNITIES

### **What to Test:**
- [ ] Opportunity qualification
- [ ] Proposal generation
- [ ] Opportunity tracking
- [ ] Mining/import

### **How to Test:**

```bash
# Start server
python api_server.py

# Qualify opportunity
curl -X POST http://localhost:5000/qualify-opportunity \
  -H "Content-Type: application/json" \
  -d '{"opportunity_id": "recOPP_ID"}'
```

### **Expected Results:**
- ✅ Opportunity analyzed
- ✅ Qualification score calculated
- ✅ Recommendation provided

---

## 7. SUPPLIER SYSTEM

### **What to Test:**
- [ ] Supplier search
- [ ] Supplier mining
- [ ] Quote tracking

### **How to Test:**

```bash
# Start server
python api_server.py

# Search suppliers
curl -X POST http://localhost:5000/gpss/suppliers/search \
  -H "Content-Type: application/json" \
  -d '{"product": "laptops", "category": "IT Equipment"}'
```

### **Expected Results:**
- ✅ Returns list of suppliers
- ✅ Suppliers have ratings and contact info

---

## 8. ATLAS PROJECT MANAGEMENT

### **What to Test:**
- [ ] Project creation
- [ ] Task management
- [ ] RFP analysis

### **How to Test:**

```bash
# Start server
python api_server.py

# Test RFP analysis
curl -X POST http://localhost:5000/atlas/analyze-rfp \
  -H "Content-Type: application/json" \
  -d '{"rfp_content": "Sample RFP text..."}'
```

---

## 9. DDCSS CORPORATE SALES

### **What to Test:**
- [ ] Prospect qualification
- [ ] Blueprint generation
- [ ] Response analysis

### **How to Test:**

```bash
# Start server
python api_server.py

# Qualify prospect
curl -X POST http://localhost:5000/ddcss/qualify-prospect \
  -H "Content-Type: application/json" \
  -d '{"prospect_id": "recPROSPECT_ID"}'
```

---

## 10. LBPC SURPLUS RECOVERY

### **What to Test:**
- [ ] Lead creation
- [ ] AI qualification
- [ ] Document generation

### **How to Test:**

```bash
# Start server
python api_server.py

# Test lead qualification
curl -X POST http://localhost:5000/lbpc/leads/recLEAD_ID/qualify \
  -H "Content-Type: application/json"
```

---

## ✅ COMPLETE TESTING CHECKLIST

### **Before Testing:**
- [ ] All Airtable tables created
- [ ] Environment variables set (.env file)
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Sample data in key tables

### **During Testing:**
- [ ] Backend starts without errors
- [ ] All API endpoints respond
- [ ] Data saves to Airtable correctly
- [ ] No Python errors in console
- [ ] Response times acceptable (<5 seconds)

### **After Testing:**
- [ ] Review Airtable for test data
- [ ] Clean up test records if needed
- [ ] Document any issues found
- [ ] Verify all critical systems work

---

## 🐛 TROUBLESHOOTING

### **"Table not found" errors:**
- Check table name spelling (exact match required)
- Verify AIRTABLE_BASE_ID in .env
- Confirm API key has access

### **"Connection refused" errors:**
- Ensure `python api_server.py` is running
- Check port 5000 is not in use
- Verify firewall settings

### **No data in Airtable:**
- Check Airtable API key is valid
- Verify Base ID is correct
- Check field names match exactly (case-sensitive)

### **AI errors:**
- Verify ANTHROPIC_API_KEY in .env
- Check API key has credits
- Ensure Claude API is accessible

---

## 📊 SUCCESS CRITERIA

**System is ready for deployment when:**

✅ All Priority 1 systems test successfully  
✅ No Python errors during testing  
✅ Data saves correctly to Airtable  
✅ API responses are fast (<5 seconds)  
✅ AI recommendations work  
✅ Financial tracking accurate  
✅ All test scripts complete without errors  

---

## 🎯 DEPLOYMENT READINESS

After all tests pass:

1. ✅ Review test results
2. ✅ Clean up test data (optional)
3. ✅ Commit code: `git add . && git commit -m "All systems tested"`
4. ✅ Ready for deployment!

**Next step:** Follow `PRE_DEPLOYMENT_CHECKLIST.md` for deployment

---

## 📝 TEST RESULTS TEMPLATE

Record your test results:

```
Date Tested: ___________
Tested By: ___________

✅ AI Recommendation System: PASS / FAIL
✅ Subcontractor System: PASS / FAIL
✅ Fulfillment System: PASS / FAIL
✅ Officer Outreach: PASS / FAIL
✅ Financial Tracking: PASS / FAIL
✅ GPSS Opportunities: PASS / FAIL
✅ Supplier System: PASS / FAIL
✅ ATLAS Projects: PASS / FAIL
✅ DDCSS Sales: PASS / FAIL
✅ LBPC Recovery: PASS / FAIL

Issues Found:
_________________________________
_________________________________

Overall Status: READY / NOT READY
```

---

**Complete testing = confident deployment! 🚀**
