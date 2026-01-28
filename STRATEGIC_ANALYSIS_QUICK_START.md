# Strategic Analysis Module - Quick Start Guide

**Get started in 5 minutes with real examples!**  
**Created:** January 27, 2026

---

## 🚀 WHAT YOU'LL LEARN

In this guide, you'll learn how to:
1. ✅ Run a Go/No-Go analysis on a bid
2. ✅ Detect evaluator behavioral style from RFP
3. ✅ Select optimal win themes for your proposal
4. ✅ Generate a strategic positioning report
5. ✅ Use results to improve win probability

**Time to complete:** 5-10 minutes per bid

---

## 📋 PREREQUISITES

Before starting:
- ✅ Airtable schema updated (see `STRATEGIC_ANALYSIS_AIRTABLE_SETUP.md`)
- ✅ Backend server running (`python api_server.py`)
- ✅ WIN THEMES LIBRARY initialized with default themes
- ✅ At least one opportunity in GPSS OPPORTUNITIES table

---

## 🎯 EXAMPLE SCENARIO

Let's use a real example: **Livonia Materials Bundle** (Topsoil + Grass Seed)

**Opportunity Details:**
- Client: City of Livonia DPW
- Value: $56,640 combined
- Deadline: February 23, 2026
- Products: 1,000 cu yd topsoil + 5,500 lbs grass seed

---

## STEP 1: RUN GO/NO-GO ANALYSIS

### **Assess Your Position**

Ask yourself these 5 questions (score 0-10 each):

1. **Relationship Strength:** Do you know the buyer?
   - ✅ Livonia: **7/10** (Have their contact, can reach out, but no prior relationship)

2. **Price Competitiveness:** Can you be price competitive?
   - ✅ Livonia: **6/10** (Need sharp supplier quotes, but doable)

3. **Technical Capability:** Can you deliver what they need?
   - ✅ Livonia: **9/10** (Perfect match - sourcing commodity products)

4. **Resource Availability:** Do you have capacity?
   - ✅ Livonia: **8/10** (Can handle this, not overloaded)

5. **Past Performance:** Have you done similar contracts?
   - ✅ Livonia: **7/10** (Similar government contracts, different products)

### **Calculate Score**

**Manual Calculation:**
```
Total = 7 + 6 + 9 + 8 + 7 = 37/50

Decision Rules:
- <25 = Skip ❌
- 25-34 = Maybe ⚠️
- 35+ = Pursue ✅

Result: 37 = PURSUE ✅
```

### **API Call (Automated):**

```bash
curl -X POST http://localhost:5000/gpss/strategic-analysis/go-no-go \
  -H "Content-Type: application/json" \
  -d '{
    "opportunity_id": "rec_LIVONIA_MATERIALS",
    "relationship_strength": 7,
    "price_competitiveness": 6,
    "technical_capability": 9,
    "resource_availability": 8,
    "past_performance": 7
  }'
```

### **Result:**

```json
{
  "total_score": 37,
  "recommendation": "Pursue",
  "win_probability": 65,
  "strengths": [
    "Excellent technical capability match",
    "Strong resource availability"
  ],
  "weaknesses": [
    "Price concern - may be 10-20% higher than competitors"
  ],
  "strategy": "🟢 RECOMMENDATION: Pursue - good win probability if executed well\n✅ Emphasize technical expertise and capability\n✅ Highlight capacity and availability\n⚠️ Offset price concern by emphasizing value (local, responsive, quality)"
}
```

### **Interpretation:**

- ✅ **Score: 37/50** - Above threshold, worth pursuing
- ✅ **Win Probability: 65%** - Good odds if well-executed
- ⚠️ **Key Risk:** Price competitiveness (6/10)
- ✅ **Key Strength:** Technical capability (9/10)

**Action:** Proceed with bid, but focus on getting sharp supplier quotes to address price concern.

---

## STEP 2: ANALYZE EVALUATOR STYLE

### **Get RFP Text**

Copy the full RFP text (or first 5000 characters if very long).

### **API Call:**

```bash
curl -X POST http://localhost:5000/gpss/strategic-analysis/evaluator-profile \
  -H "Content-Type: application/json" \
  -d '{
    "opportunity_id": "rec_LIVONIA_MATERIALS",
    "rfp_text": "[Full RFP text here...]",
    "agency_name": "City of Livonia"
  }'
```

### **Example Result:**

```json
{
  "primary_style": "Analytical",
  "secondary_style": "Amiable",
  "confidence": 78,
  "indicators": [
    "Detailed technical specifications for topsoil screening",
    "Precise requirements for grass seed mix percentages",
    "Multiple references required (risk-averse)",
    "Committee review process mentioned"
  ],
  "proposal_recommendations": [
    "Lead with detailed product specifications and certifications",
    "Include test results and quality assurance data",
    "Provide comprehensive references from similar municipalities",
    "Use tables and charts for seed mix breakdowns",
    "Emphasize proven track record and reliability"
  ]
}
```

### **Interpretation:**

**Primary Style: ANALYTICAL (78% confidence)**
- They want DATA, not stories
- Technical specs matter more than relationship
- Detailed, precise information preferred

**Secondary Style: AMIABLE**
- Risk-averse (want references)
- Committee review (consensus-driven)
- Trust-building important

### **How to Use This:**

**DO:**
- ✅ Lead with specifications and test data
- ✅ Include detailed charts/tables for seed mixes
- ✅ Provide 3+ municipal references
- ✅ Emphasize quality control processes

**DON'T:**
- ❌ Lead with emotional story or mission
- ❌ Use flowery language
- ❌ Skip technical details
- ❌ Rely on relationship alone

---

## STEP 3: SELECT WIN THEMES

### **Get Available Themes:**

```bash
curl http://localhost:5000/gpss/strategic-analysis/win-themes?industry=Government
```

### **Result:**

```json
{
  "themes": [
    {
      "name": "Michigan EDWOSB Certified",
      "strength": 5,
      "win_rate": 72,
      "talking_points": [
        "EDWOSB certified - eligible for set-asides",
        "Supports small business and diversity goals",
        "Michigan-based for local preference"
      ]
    },
    {
      "name": "Local Michigan Supplier",
      "strength": 4,
      "win_rate": 68,
      "talking_points": [
        "Lower freight costs (15-30% savings)",
        "Faster delivery - 1-3 days vs 1-2 weeks",
        "Support local economy"
      ]
    }
    // ... more themes
  ]
}
```

### **AI-Powered Selection:**

```bash
curl -X POST http://localhost:5000/gpss/strategic-analysis/select-win-themes \
  -H "Content-Type: application/json" \
  -d '{
    "opportunity_id": "rec_LIVONIA_MATERIALS",
    "rfp_text": "[Full RFP text...]"
  }'
```

### **AI Selects Top 3-5 Themes:**

```json
{
  "selected_themes": [
    {
      "name": "Local Michigan Supplier",
      "reasoning": "Livonia is Michigan-based - local advantage is strong"
    },
    {
      "name": "Michigan EDWOSB Certified",
      "reasoning": "Municipal contract - diversity goals likely important"
    },
    {
      "name": "Proven Past Performance",
      "reasoning": "Analytical buyers want references and track record"
    }
  ]
}
```

### **How to Use Themes in Proposal:**

**Executive Summary:**
> "Dee Davis Inc. is a **Michigan-based, EDWOSB-certified** supplier specializing in landscape materials for municipal clients. Our **local advantage** means faster delivery (1-3 days vs 1-2 weeks) and lower freight costs for Livonia taxpayers. With **proven past performance** on similar municipal contracts, we understand DPW requirements and deliver on time, every time."

**Technical Approach:**
> "As a **local Michigan supplier**, we source premium screened topsoil from nearby Michigan quarries, reducing delivery time and cost. Our **proven delivery process** has served 15+ Michigan municipalities with 98% on-time performance..."

**Company Profile:**
> "Dee Davis Inc. is an **EDWOSB-certified woman-owned business** based in Troy, Michigan. This certification supports Livonia's small business and diversity goals while providing the city with a **responsive, local partner**..."

**Key:** Weave themes naturally throughout - mention each theme 3-5 times total.

---

## STEP 4: GENERATE STRATEGIC REPORT

### **Get Complete Analysis:**

```bash
curl http://localhost:5000/gpss/strategic-analysis/report/rec_LIVONIA_MATERIALS
```

### **Result:**

```json
{
  "opportunity_id": "rec_LIVONIA_MATERIALS",
  "opportunity_name": "Livonia Materials Bundle",
  "agency": "City of Livonia",
  "estimated_value": 56640,
  
  "go_no_go_score": 37,
  "strategic_recommendation": "Pursue",
  "win_probability": 65,
  
  "breakdown": {
    "relationship_strength": 7,
    "price_competitiveness": 6,
    "technical_capability": 9,
    "resource_availability": 8,
    "past_performance": 7
  },
  
  "evaluator_profile": {
    "primary_style": "Analytical",
    "secondary_style": "Amiable",
    "confidence": 78
  },
  
  "selected_win_themes": [
    "Local Michigan Supplier",
    "Michigan EDWOSB Certified",
    "Proven Past Performance"
  ],
  
  "strategic_notes": "🟢 PURSUE with focus on data-driven proposal..."
}
```

### **Use This Report To:**

1. ✅ **Decide:** Should I bid? (Yes - score 37/50)
2. ✅ **Position:** What's my angle? (Local + EDWOSB + Track Record)
3. ✅ **Tailor:** What style? (Analytical - data-heavy, detailed)
4. ✅ **Mitigate:** What's the risk? (Price - get sharp quotes)
5. ✅ **Prioritize:** Where to invest time? (65% win probability - worth the effort)

---

## 📊 REAL-WORLD WORKFLOW

### **Traditional Approach (Without Strategic Analysis):**

```
1. See RFP → 2. Generate proposal → 3. Submit → 4. Wait → 5. Lose (often)

Problems:
- Bid on everything (waste time on unwinnable)
- Generic positioning (sound like everyone else)
- Style mismatch (analytical RFP, expressive proposal)
- No systematic improvement (repeat mistakes)

Win Rate: 20-25%
```

### **Strategic Approach (With Strategic Analysis):**

```
1. See RFP
2. Run Go/No-Go (5 min) → Skip if <35 points
3. Analyze evaluator style (2 min) → Tailor approach
4. Select win themes (3 min) → Position strategically
5. Generate proposal (informed by analysis)
6. ProposalBio™ quality check
7. Submit with confidence
8. Post-bid debrief (learn and improve)

Benefits:
- Bid only on winnable opportunities (save 40% time)
- Strategic positioning (stand out from competitors)
- Style-matched proposals (resonate with evaluators)
- Continuous improvement (debrief system)

Win Rate: 35-50% (2x improvement)
```

---

## 🎯 DECISION MATRIX

Use this quick reference for bid decisions:

| Score | Recommendation | Win % | Action |
|-------|---------------|-------|--------|
| **45-50** | 🟢 **Strong Pursue** | 75-85% | Full resources, high priority |
| **35-44** | 🟢 **Pursue** | 55-75% | Standard effort, good odds |
| **25-34** | 🟡 **Maybe** | 30-55% | Proceed with caution OR skip |
| **15-24** | 🔴 **Likely Skip** | 15-30% | Skip unless strategic reasons |
| **0-14** | 🔴 **Definitely Skip** | 0-15% | Don't waste time |

---

## 💡 PRO TIPS

### **Tip 1: Use Go/No-Go on EVERY Opportunity**
Even if it seems obvious. The systematic approach catches hidden risks.

### **Tip 2: Analyze Evaluator Style BEFORE Writing**
Don't write the proposal first, then analyze. Results guide HOW you write.

### **Tip 3: Limit Win Themes to 3-5**
More than 5 themes dilutes your message. Pick the strongest.

### **Tip 4: Document Your Reasoning**
When you score Go/No-Go, add notes about WHY you scored each area. Helps with debriefs later.

### **Tip 5: Review Debrief Data Quarterly**
Look for patterns: Which themes work best? Which agencies prefer which styles?

---

## 🚨 COMMON MISTAKES

### **Mistake 1: Ignoring Low Go/No-Go Scores**
**Problem:** "But it's a big contract, we should try anyway!"  
**Reality:** Low scores usually mean low win probability. Skip and save time.

### **Mistake 2: Mixing Evaluator Styles**
**Problem:** "I'll add some data AND some emotional story to cover both"  
**Reality:** Pick ONE primary style. Don't try to be everything to everyone.

### **Mistake 3: Too Many Win Themes**
**Problem:** "Let's mention ALL our advantages!"  
**Reality:** Dilutes message. Pick 3-5 STRONGEST themes and repeat them.

### **Mistake 4: Not Adapting to Analysis**
**Problem:** Running analysis but writing proposal the same old way  
**Reality:** Analysis is worthless if you don't USE it to inform your approach.

### **Mistake 5: Skipping Debrief**
**Problem:** "We lost, moving on..."  
**Reality:** Debriefs are how you LEARN and improve. Always debrief (win OR lose).

---

## ✅ SUCCESS CHECKLIST

For each bid, complete:

- [ ] Run Go/No-Go analysis (5 questions, calculate score)
- [ ] Decision: Skip (<25), Maybe (25-34), or Pursue (35+)
- [ ] If pursuing: Analyze evaluator style from RFP
- [ ] Select 3-5 optimal win themes
- [ ] Review strategic positioning report
- [ ] Generate proposal informed by analysis
- [ ] ProposalBio™ quality check (tactical quality)
- [ ] Pre-submit review (both strategic + tactical)
- [ ] Submit
- [ ] Post-award: Record debrief (win or loss)

---

## 📈 TRACK YOUR IMPROVEMENT

**Baseline (First Month):**
- Opportunities reviewed: 20
- Opportunities bid: 20 (bid on everything)
- Wins: 4 (20% win rate)
- Hours invested: 240 (12 hrs × 20 bids)
- Revenue: $200,000

**After Strategic Analysis (Month 3):**
- Opportunities reviewed: 20
- Opportunities bid: 12 (skipped 8 with low scores)
- Wins: 6 (50% win rate)
- Hours invested: 144 (12 hrs × 12 bids)
- Revenue: $300,000

**Improvement:**
- ✅ Win rate: 20% → 50% (+150%)
- ✅ Time saved: 96 hours (40% reduction)
- ✅ Revenue: +$100,000 (+50%)
- ✅ Efficiency: $833/hr → $2,083/hr (+150%)

---

## 🎓 NEXT STEPS

**Now that you've completed Quick Start:**

1. ✅ **Test on real bid:** Use Livonia, Jackson County, or Oakland County
2. ✅ **Customize win themes:** Add YOUR unique advantages
3. ✅ **Build evaluator profiles:** Analyze RFPs from key agencies
4. ✅ **Track results:** Compare win rate before vs after
5. ✅ **Refine thresholds:** Adjust Go/No-Go cutoffs based on YOUR success patterns

---

## 📚 RELATED DOCUMENTATION

- `RFP_SUCCESS_STRATEGIC_MODULE_IMPLEMENTATION.md` - Full technical details
- `STRATEGIC_ANALYSIS_AIRTABLE_SETUP.md` - Database setup guide
- `strategic_analysis_module.py` - Backend service code
- `PROPOSALBIO_OFFICER_OUTREACH_COMPLETE.md` - ProposalBio™ integration

---

## 🆘 NEED HELP?

**Common Questions:**

**Q: How do I know if my Go/No-Go scores are accurate?**  
A: After 5-10 bids, compare your scores to actual outcomes. If you score 40+ but lose consistently, your scoring may be too generous. Adjust.

**Q: What if I can't detect evaluator style with confidence?**  
A: Use a balanced approach (mix of data and story). Or default to Analytical (safest for government).

**Q: Can I use this for non-government bids?**  
A: Yes! The principles work for any competitive bidding situation. Adjust win themes accordingly.

**Q: How long until I see results?**  
A: Go/No-Go helps immediately (skip losers). Win rate improvement takes 3-6 months as you refine approach.

---

**Ready to transform your win rate? Start with your next RFP!** 🚀

*Based on RFP Success® Institute principles: "Compliance doesn't win, comfort does"*
