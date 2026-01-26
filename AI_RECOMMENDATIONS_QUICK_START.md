# AI RECOMMENDATIONS - QUICK START CARD
## Get Up & Running in 15 Minutes

---

## ⚡ FASTEST PATH TO FIRST USE

### **Step 1: Create Tables (10 min)**

Go to Airtable → Create these tables:

**AI RECOMMENDATIONS** (11 fields):
```
OPPORTUNITY (link to GPSS OPPORTUNITIES)
TYPE (select: Capability Gap Analysis, Subcontractor Recommendation, Supplier Recommendation)
RECOMMENDATION (long text)
CONFIDENCE (number 0-100)
REASONING (long text)
STATUS (select: Pending Approval, Approved, Denied, Modified)
USER_DECISION (select: APPROVED, DENIED, MODIFIED)
USER_NOTES (long text)
SELECTED_OPTION (single line)
CREATED (date with time)
DECIDED_AT (date with time)
```

**COMPANY CAPABILITIES** (7 fields):
```
CAPABILITY_NAME (single line: "Project Management", etc.)
SKILL_LEVEL (select: Expert, Intermediate, Beginner, None)
CAPACITY (select: High, Medium, Low)
HOURLY_RATE (currency)
TEAM_SIZE (number)
CERTIFICATIONS (long text)
NOTES (long text)
```

Add your capabilities:
- Project Management: Expert, High, $150
- Government Contracting: Expert, High, $150
- Cybersecurity: None, Low, $0 ← Include gaps!

---

### **Step 2: Test It (5 min)**

```bash
# Terminal 1: Start server
python api_server.py

# Terminal 2: Run tests
python test_ai_recommendations.py
```

---

### **Step 3: Use It (30 seconds per decision)**

```bash
# Get capability analysis
curl -X POST http://localhost:5000/ai/recommendations/capability-gap \
  -H "Content-Type: application/json" \
  -d '{"opportunity_id": "recYOUR_OPP_ID"}'

# AI responds with recommendation + reasoning

# Approve it
curl -X POST http://localhost:5000/ai/recommendations/recREC_ID/approve \
  -H "Content-Type: application/json" \
  -d '{"decision": "approved", "notes": "Looks good!"}'
```

---

## 🎯 THE PATTERN

```
AI analyzes (10 sec) → AI suggests (instant) → YOU decide (30 sec) → System learns
```

---

## 📞 QUICK COMMANDS

**Get pending decisions:**
```bash
curl http://localhost:5000/ai/recommendations/pending
```

**Capability gap analysis:**
```bash
curl -X POST http://localhost:5000/ai/recommendations/capability-gap \
  -d '{"opportunity_id": "recXYZ"}'
```

**Find subcontractors:**
```bash
curl -X POST http://localhost:5000/ai/recommendations/subcontractors \
  -d '{"opportunity_id": "recXYZ", "needed_skills": ["Cybersecurity"]}'
```

**Find suppliers:**
```bash
curl -X POST http://localhost:5000/ai/recommendations/suppliers \
  -d '{"opportunity_id": "recXYZ", "product_description": "laptops"}'
```

**Check compliance:**
```bash
curl -X POST http://localhost:5000/ai/compliance/calculate \
  -d '{"contract_value": 500000, "your_work_value": 280000, "subcontractor_work_value": 180000}'
```

**Approve:**
```bash
curl -X POST http://localhost:5000/ai/recommendations/recID/approve \
  -d '{"decision": "approved", "notes": "Good!"}'
```

**Deny:**
```bash
curl -X POST http://localhost:5000/ai/recommendations/recID/approve \
  -d '{"decision": "denied", "notes": "Not this one"}'
```

---

## 🚀 SPEED GAINS

- **Before:** 8-12 hours per opportunity
- **After:** 5 minutes per opportunity
- **Speedup:** 96-144x faster!

---

## 🎯 WHAT YOU CONTROL

- ✅ Which opportunities to pursue
- ✅ Self-perform vs partner
- ✅ Which subcontractor/supplier
- ✅ Pricing & margins
- ✅ All strategic decisions

**AI just does the grunt work!**

---

## 📚 FULL DOCS

- **Setup:** `AIRTABLE_SETUP_AI_RECOMMENDATIONS.md`
- **Usage:** `AI_RECOMMENDATION_SYSTEM.md`
- **Flows:** `COMPLETE_SYSTEM_FLOWS.md`
- **Summary:** `AI_RECOMMENDATION_IMPLEMENTATION_COMPLETE.md`

---

## ✅ READY CHECKLIST

- [ ] AI RECOMMENDATIONS table created
- [ ] COMPANY CAPABILITIES table created
- [ ] Added 5-10 capabilities (include gaps!)
- [ ] Server running: `python api_server.py`
- [ ] Tested: `python test_ai_recommendations.py`
- [ ] First real opportunity tested
- [ ] 🚀 Ready to scale!

---

**AI suggests. You decide. System learns. You win.** 🎯
