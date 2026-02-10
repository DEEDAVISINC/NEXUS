# DEE DAVIS INC FRAMEWORKS - QUICK REFERENCE CARD
**Print this and keep it visible while working**

---

## 🎯 THE 6 FRAMEWORKS (At a Glance)

| # | Framework | When to Use | Output | Quality Standard |
|---|-----------|-------------|--------|------------------|
| **1** | **Officer Outreach** | After opportunities close | Vendor list adds | 30-40% response rate |
| **2** | **Auto CapStat** | Sources sought, outreach | Custom PDF | <5 min generation time |
| **3A** | **Grainger Script** | Before SUPPLY bids | Better pricing | 5-10% discount target |
| **3B** | **Service Sub** ⭐ | Before SERVICE bids | Qualified subs + proof | 3+ subs vetted, LOI signed |
| **4** | **Transformation** | Writing proposals | Outcome-focused proposals | 40/50 minimum score |
| **5** | **ProposalBio** | Before submission | Quality check | 75/100 minimum score |

---

## 📋 THE COMPLETE WORKFLOW (One Page)

```
┌─────────────────────────────────────────────────────────┐
│ STAGE 1: OPPORTUNITY DISCOVERY                          │
├─────────────────────────────────────────────────────────┤
│ ✓ Find opportunity on SAM.gov                           │
│ ✓ Add to Officer Outreach table                         │
│ ✓ Generate CapStat: python3 auto_generate...py <id>    │
│ ✓ Send introduction letter                              │
│                                                          │
│ Frameworks: Officer Outreach + Auto CapStat             │
│ Time: 20-30 minutes                                     │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ STAGE 2: QUALIFICATION & NEGOTIATION                    │
├─────────────────────────────────────────────────────────┤
│ ✓ Complete Transformation Worksheet                     │
│   Score ≥40/50? YES → Proceed | NO → Pass              │
│                                                          │
│ IF SUPPLY BID:                                          │
│ ✓ Request supplier quotes                               │
│ ✓ Use Grainger Call Script to negotiate                │
│ ✓ Calculate margins                                     │
│ ✓ Make GO/NO-GO decision                               │
│                                                          │
│ IF SERVICE BID: ⭐ NEW                                  │
│ ✓ Find 5-10 potential subs (Google, Yelp, etc.)        │
│ ✓ Vet 3-5 qualified subs (licenses, insurance)         │
│ ✓ Request quotes, negotiate terms                       │
│ ✓ Gather sub's metrics (response time, quality)        │
│ ✓ Get Letter of Intent signed                          │
│ ✓ Calculate margins (15-25% target)                    │
│                                                          │
│ Frameworks: Transformation + Grainger/Service Sub       │
│ Time: 2-4 hours (service), 1-2 hours (supply)          │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ STAGE 3: PROPOSAL WRITING                               │
├─────────────────────────────────────────────────────────┤
│ ✓ Keep Proposal Quick Reference open                    │
│ ✓ Follow Transformation Framework structure:            │
│   1. Problem Mastery (educate them)                     │
│   2. Transformation (what they get)                     │
│   3. Proof (case studies with numbers)                  │
│   4. Credentials (brief, supporting only)               │
│ ✓ Include Auto CapStat PDF                             │
│ ✓ AI blocks resume-style content                        │
│                                                          │
│ Frameworks: Transformation + Auto CapStat               │
│ Time: 4-8 hours                                         │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ STAGE 4: QUALITY ASSURANCE                              │
├─────────────────────────────────────────────────────────┤
│ ✓ Run Transformation Checklist                          │
│   Minimum: 40/50 (8/10 per section)                    │
│                                                          │
│ ✓ Run ProposalBio in NEXUS                             │
│   Minimum: 75/100                                       │
│   All biohacks: ≥6/10                                   │
│   Quality Gate: UNLOCKED                                │
│                                                          │
│ ✓ Fix critical issues                                   │
│ ✓ Re-run until both gates pass                         │
│                                                          │
│ Frameworks: Transformation + ProposalBio                │
│ Time: 30 minutes - 2 hours                              │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ STAGE 5: SUBMISSION & FOLLOW-UP                         │
├─────────────────────────────────────────────────────────┤
│ ✓ Submit proposal                                        │
│ ✓ Send thank you email (human touch!)                  │
│ ✓ Track in Airtable                                     │
│ ✓ Follow up Day 7 (if appropriate)                     │
│ ✓ Log win/loss in ProposalBio Learning                 │
│                                                          │
│ Frameworks: Officer Outreach + ProposalBio              │
│ Time: Ongoing                                           │
└─────────────────────────────────────────────────────────┘
```

---

## ⚡ EMERGENCY QUICK REFERENCE

### **"I need to respond to sources sought NOW"**
```bash
python3 auto_generate_opportunity_capstat.py --manual
# Answer prompts → Get PDF in 2 minutes
# Attach to email → Send
```

### **"I need to write a proposal NOW"**
```
1. Complete Transformation Worksheet (30 min)
2. Score ≥40/50? YES → Write | NO → Pass
3. Keep Quick Reference open while writing
4. Follow structure: Problem → Transformation → Proof → Credentials
5. Run ProposalBio before submitting
```

### **"Supplier won't give me a discount"**
```
Use Grainger Script leverage points:
- Size of contract ($X million)
- Guaranteed payment (government)
- EDWOSB certification (diversity)
- Ready to award today
- Ask for government pricing specifically
```

### **"I can't find qualified subs for service bid"** ⭐ NEW
```
Use Service Sub Framework sourcing methods:
- Google: "[Service] [Location]"
- Yelp/Angi/Thumbtack/HomeAdvisor
- SAM.gov (who won past contracts?)
- Facebook business groups
- Industry associations
Target: 5-10 potential, vet down to 3-5 qualified
```

### **"My proposal scores low"**
```
Transformation score low (<40)?
→ Add case studies with metrics
→ Quantify outcomes
→ Show transformation clearly

ProposalBio score low (<75)?
→ Fix biohacks scored <6
→ Add stories (challenge-solution-result)
→ Improve readability
→ Increase agency name mentions
```

---

## 🚫 NEVER SUBMIT IF...

- [ ] Transformation score < 40/50
- [ ] ProposalBio score < 75/100
- [ ] Any biohack < 6/10
- [ ] Quality gate: LOCKED
- [ ] No quantified outcomes (need 5+)
- [ ] No case studies with metrics (need 2+)
- [ ] Resume-style content present
- [ ] No transformation clearly stated

**Below standards = DO NOT SUBMIT**

---

## ✅ READY TO SUBMIT WHEN...

- [x] Transformation score ≥ 40/50
- [x] ProposalBio score ≥ 75/100
- [x] All biohacks ≥ 6/10
- [x] Quality gate: UNLOCKED
- [x] 5+ quantified metrics included
- [x] 2+ case studies with outcomes
- [x] Transformation clearly stated (FROM → TO)
- [x] No resume-style content
- [x] Auto CapStat PDF attached
- [x] All forms complete and accurate

**All checked = SUBMIT WITH CONFIDENCE! 🚀**

---

## 📞 QUICK COMMANDS

```bash
# Generate capability statement from Airtable
python3 auto_generate_opportunity_capstat.py <record_id>

# Generate capability statement manually
python3 auto_generate_opportunity_capstat.py --manual

# Run officer outreach system
python contracting_officer_outreach.py

# Start NEXUS backend (for ProposalBio)
cd "/Users/deedavis/NEXUS BACKEND"
python api_server.py

# Start NEXUS frontend
cd "/Users/deedavis/NEXUS BACKEND/nexus-frontend"
npm start
```

---

## 📁 KEY FILES (Keep Bookmarked)

**Planning:**
- `PROPOSAL_TRANSFORMATION_WORKSHEET.md` (complete FIRST!)

**Writing:**
- `PROPOSAL_QUICK_REFERENCE.md` (keep OPEN)

**Reference:**
- `TRANSFORMATION_PROPOSAL_FRAMEWORK.md` (complete guide)
- `GRAINGER_CALL_SCRIPT_FINAL.md` (negotiation)
- `MASTER_FRAMEWORKS_INTEGRATION.md` (this connects everything)

**Quick Starts:**
- `OFFICER_OUTREACH_QUICK_START.md` (15 min)
- `AUTO_CAPSTAT_QUICK_START.md` (2 min)
- `PROPOSALBIO_QUICK_START.md` (10 min)

---

## 💡 REMEMBER

### **Officer Outreach:**
> "Every closed opportunity is a future relationship"

### **Auto CapStat:**
> "Generic = 5% response. Customized = 30-50%"

### **Grainger Script:**
> "You have leverage. Size matters. Be confident."

### **Service Sub Framework:** ⭐ NEW
> "Subs deliver the work. YOU deliver the transformation."

### **Transformation Framework:**
> "Nobody cares what you've DONE. They care about OUTCOMES."

### **ProposalBio:**
> "Objective quality gates prevent bad proposals"

---

## 🎯 SUCCESS METRICS (Weekly Tracking)

| Metric | Target | Actual |
|--------|--------|--------|
| Officer letters sent | 5-10 | ____ |
| CapStats generated | 5-10 | ____ |
| Supplier negotiations | 1-3 | ____ |
| Proposals written | 1-3 | ____ |
| Quality gates passed | 90%+ | ____ |
| Average Transformation score | 43/50 | ____ |
| Average ProposalBio score | 80/100 | ____ |
| Proposals submitted | 1-3 | ____ |

**Track weekly. Review monthly. Improve quarterly.**

---

## 🔥 ONE-SENTENCE RULES

1. **Officer Outreach:** Send within 7-30 days of opportunity closing
2. **Auto CapStat:** Generate in <5 minutes, customize for each opportunity
3. **Grainger Script:** Aim for 5-10% discount + tax removal
4. **Transformation Worksheet:** Complete BEFORE writing (40/50 minimum)
5. **Transformation Writing:** Outcomes not credentials, educate not pitch
6. **ProposalBio:** Run before submitting (75/100 minimum)
7. **Quality Gates:** BOTH must pass (Transformation + ProposalBio)
8. **Follow-Up:** Thank you email within 24 hours (human touch!)

---

**PRINT THIS CARD. KEEP IT VISIBLE. REFERENCE IT CONSTANTLY.**

---

**Last Updated:** February 4, 2026  
**Owner:** Dee Davis
