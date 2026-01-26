# AI RECOMMENDATION SYSTEM - AIRTABLE AUTOMATIONS
## Add These to Your Automation Setup

**Date:** January 21, 2026  
**System:** AI Recommendation & Approval  
**Tables:** AI RECOMMENDATIONS, COMPANY CAPABILITIES

---

## 📋 AUTOMATIONS TO ADD

### **Total:** 4 new automations for AI Recommendation System

**Add to Table of Contents:**
```
12. [AI Recommendation Automations](#ai-recommendation-automations) (4 automations) ⭐ NEW
```

**Update Total:** 42 → **46 automations**

---

# AI RECOMMENDATION AUTOMATIONS

## 1. 🟡 IMPORTANT: New AI Recommendation Alert

**Priority:** IMPORTANT  
**Table:** AI RECOMMENDATIONS  
**Purpose:** Notify you when AI creates a new recommendation for your review

### Setup Instructions:

1. Go to **Automations** → **Create automation**
2. **Name:** "New AI Recommendation Alert"
3. **Trigger:** When record created
   - Table: `AI RECOMMENDATIONS`
4. **Condition:** Only run when
   - `STATUS` = "Pending Approval"
5. **Action:** Send email
   - To: `your-email@deedavisinc.com`
   - Subject: `🤖 AI RECOMMENDATION: {TYPE}`
   - Body:
```
NEW AI RECOMMENDATION READY FOR YOUR REVIEW

Type: {TYPE}
Opportunity: {OPPORTUNITY}
━━━━━━━━━━━━━━━━━━━━━━━━
AI RECOMMENDATION:
{RECOMMENDATION}

CONFIDENCE: {CONFIDENCE}%

REASONING:
{REASONING}
━━━━━━━━━━━━━━━━━━━━━━━━
ACTION NEEDED:
Review and approve/deny this recommendation

View in Airtable:
[Link to record]
```
6. **Turn ON** the automation

---

## 2. 🟡 IMPORTANT: High Confidence Recommendation Alert

**Priority:** IMPORTANT  
**Table:** AI RECOMMENDATIONS  
**Purpose:** Fast-track high-confidence recommendations (90%+)

### Setup Instructions:

1. Go to **Automations** → **Create automation**
2. **Name:** "High Confidence AI Recommendation"
3. **Trigger:** When record created
   - Table: `AI RECOMMENDATIONS`
4. **Condition:** Only run when
   - `CONFIDENCE` ≥ 90
   - AND `STATUS` = "Pending Approval"
5. **Action:** Send email
   - To: `your-email@deedavisinc.com`
   - Subject: `⚡ HIGH CONFIDENCE ({CONFIDENCE}%): {TYPE}`
   - Body:
```
HIGH CONFIDENCE AI RECOMMENDATION

Type: {TYPE}
Confidence: {CONFIDENCE}% ⭐ (Very High)
━━━━━━━━━━━━━━━━━━━━━━━━
AI RECOMMENDATION:
{RECOMMENDATION}

REASONING:
{REASONING}
━━━━━━━━━━━━━━━━━━━━━━━━
WHY HIGH CONFIDENCE:
AI is very confident in this recommendation.
Quick review recommended - this is likely the right choice.

QUICK ACTIONS:
✅ Approve if reasoning looks good
❌ Deny if you see issues
📝 Modify if adjustment needed

View in Airtable:
[Link to record]
```
6. **Turn ON** the automation

---

## 3. 🟢 NICE TO HAVE: Low Confidence Recommendation Alert

**Priority:** NICE TO HAVE  
**Table:** AI RECOMMENDATIONS  
**Purpose:** Flag low-confidence recommendations for careful review

### Setup Instructions:

1. Go to **Automations** → **Create automation**
2. **Name:** "Low Confidence AI Recommendation"
3. **Trigger:** When record created
   - Table: `AI RECOMMENDATIONS`
4. **Condition:** Only run when
   - `CONFIDENCE` < 70
   - AND `STATUS` = "Pending Approval"
5. **Action:** Send email
   - To: `your-email@deedavisinc.com`
   - Subject: `⚠️ LOW CONFIDENCE ({CONFIDENCE}%): {TYPE}`
   - Body:
```
LOW CONFIDENCE AI RECOMMENDATION

Type: {TYPE}
Confidence: {CONFIDENCE}% ⚠️ (Uncertain)
━━━━━━━━━━━━━━━━━━━━━━━━
AI RECOMMENDATION:
{RECOMMENDATION}

REASONING:
{REASONING}
━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ CAUTION:
AI is uncertain about this recommendation.
Deep review recommended before deciding.

SUGGESTED ACTIONS:
📊 Review all available options
🔍 Verify AI's reasoning carefully
💭 Use your expertise to decide
❓ Request more information if needed

View in Airtable:
[Link to record]
```
6. **Turn ON** the automation

---

## 4. 🟢 NICE TO HAVE: Pending Decision Reminder

**Priority:** NICE TO HAVE  
**Table:** AI RECOMMENDATIONS  
**Purpose:** Remind you of pending decisions after 24 hours

### Setup Instructions:

1. Go to **Automations** → **Create automation**
2. **Name:** "Pending AI Decision Reminder"
3. **Trigger:** When record matches conditions
   - Table: `AI RECOMMENDATIONS`
   - Conditions:
     - When `STATUS` = "Pending Approval"
     - AND `CREATED` was "24 hours ago"
4. **Action:** Send email
   - To: `your-email@deedavisinc.com`
   - Subject: `⏰ REMINDER: Pending AI Recommendation`
   - Body:
```
PENDING AI RECOMMENDATION (24 HOURS)

Type: {TYPE}
Opportunity: {OPPORTUNITY}
Created: {CREATED}
━━━━━━━━━━━━━━━━━━━━━━━━
AI RECOMMENDATION:
{RECOMMENDATION}

Confidence: {CONFIDENCE}%
━━━━━━━━━━━━━━━━━━━━━━━━
REMINDER:
This recommendation has been pending for 24 hours.
Please review and make a decision.

The system is waiting for your approval/denial
to proceed with this opportunity.

View in Airtable:
[Link to record]
```
5. **Turn ON** the automation

---

## 📊 AUTOMATION SUMMARY

| # | Automation Name | Priority | Purpose | When to Set Up |
|---|----------------|----------|---------|----------------|
| 1 | New AI Recommendation Alert | 🟡 Important | Notify of new recommendations | Week 1 |
| 2 | High Confidence Alert | 🟡 Important | Fast-track 90%+ confidence | Week 1 |
| 3 | Low Confidence Alert | 🟢 Nice to Have | Flag uncertain recommendations | Week 2 |
| 4 | Pending Decision Reminder | 🟢 Nice to Have | 24-hour follow-up | Week 2 |

---

## ✅ SETUP CHECKLIST

**Phase 1: Essential (Week 1) - 2 automations:**
- [ ] New AI Recommendation Alert
- [ ] High Confidence Alert

**Phase 2: Optional (Week 2) - 2 automations:**
- [ ] Low Confidence Alert
- [ ] Pending Decision Reminder

**Total setup time:** ~15 minutes

---

## 🎯 WHY THESE AUTOMATIONS MATTER

### **Without Automations:**
- You have to manually check Airtable for new recommendations
- Might miss high-confidence suggestions
- No alerts for urgent decisions
- Recommendations sit unreviewed

### **With Automations:**
- Instant notification when AI suggests something
- Priority alerts for high-confidence (fast decisions)
- Warnings for low-confidence (careful review)
- Reminders for pending decisions
- Never miss an AI recommendation

---

## 🔄 WORKFLOW WITH AUTOMATIONS

```
1. AI analyzes opportunity
   ↓
2. AI creates recommendation in Airtable
   ↓
3. 📧 Email sent immediately:
   "New AI Recommendation: Capability Gap Analysis"
   ↓
4. IF confidence ≥ 90%:
   📧 Second email: "HIGH CONFIDENCE - Quick review!"
   ↓
5. You review email (30 seconds)
   ↓
6. You decide in Airtable (Approve/Deny)
   ↓
7. IF no decision after 24 hours:
   📧 Reminder email: "Pending decision"
   ↓
8. System proceeds based on your decision
```

---

## 📧 EMAIL FREQUENCY

**Expected volume:**
- **New Recommendations:** 1-5 per day (depending on opportunity flow)
- **High Confidence:** 0-2 per day (subset of new recs)
- **Low Confidence:** 0-1 per day (rare, when AI is uncertain)
- **Reminders:** 0-2 per day (only if decisions pending)

**Total:** 2-10 emails per day related to AI recommendations

**Not overwhelming because:**
- High-quality, actionable alerts only
- Grouped by opportunity
- Clear action items
- Quick to review (30 sec per email)

---

## 🎨 CUSTOMIZATION OPTIONS

### **Adjust Email Frequency:**
Change trigger from "When record created" to "At scheduled time":
- Daily digest at 9 AM: All pending recommendations
- Reduces email volume for busy days

### **Adjust Confidence Thresholds:**
- High confidence: Change from 90% to 85% or 95%
- Low confidence: Change from 70% to 60% or 65%

### **Add Slack/SMS:**
Instead of email, send to:
- Slack channel for team visibility
- SMS for urgent high-confidence recommendations
- Both email AND Slack for critical items

### **Add Auto-Approval (Advanced):**
For 95%+ confidence + specific types:
- Auto-approve capability gap analysis at 95%+
- Auto-approve compliance calculations at 98%+
- Still get notification, just auto-executed

---

## 🔗 INTEGRATION WITH OTHER AUTOMATIONS

**Works together with:**
- **GPSS Opportunity Automations:** New opportunity → AI analyzes → Recommendation created → Alert sent
- **Subcontractor Automations:** High-score quote → AI recommends → Alert sent → You approve
- **Proposal Quality Automations:** Ready to send → AI capability check → Recommendation → Alert

**Creates seamless flow:**
```
Opportunity found
  ↓ (auto)
AI analyzes
  ↓ (auto)
Recommendation created
  ↓ (auto)
Email alert sent
  ↓ (manual)
You approve/deny (30 sec)
  ↓ (auto)
System proceeds
```

---

## 📝 NOTES

**Important:**
- These automations only work AFTER you've created the AI RECOMMENDATIONS table
- Make sure table name is exactly "AI RECOMMENDATIONS" (all caps)
- Test each automation after creating it
- Adjust email addresses to your actual email

**Dependencies:**
- Requires AI RECOMMENDATIONS table ✅
- Requires COMPANY CAPABILITIES table ✅ (for recommendations to work)
- Works with existing opportunity automations

**Performance:**
- Automations run instantly (<5 seconds)
- No delay in notifications
- No impact on Airtable performance

---

## 🚀 NEXT STEPS

1. **Create the 2 Important automations** (Week 1)
   - New AI Recommendation Alert
   - High Confidence Alert

2. **Test with one recommendation**
   - Trigger AI analysis
   - Verify emails arrive
   - Check email content

3. **Add optional automations** (Week 2)
   - Low Confidence Alert
   - Pending Decision Reminder

4. **Monitor and adjust**
   - Track email volume
   - Adjust thresholds if needed
   - Customize as you learn patterns

---

**Add these 4 automations to complete your AI Recommendation System!** 🎉
