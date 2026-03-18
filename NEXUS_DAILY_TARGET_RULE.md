# NEXUS Critical Business Rule: 3 Opportunities Per Day

## The Rule

**NEXUS MUST find 3 NEW opportunities every single day.**

This is non-negotiable. This is how DDI wins contracts.

---

## Why This Matters

### The Math
- **3 opportunities/day × 30 days = 90 opportunities/month**
- **Realistic bid rate: ~15% of opportunities = ~13 bids/month**
- **Win rate: ~25% = ~3 wins/month**
- **Revenue target: HIT**

### Without This Rule
- Find 1 opportunity/day = 4 bids/month = 1 win/month = **FAILURE**
- Inconsistent searching = missed deadlines = **LOST REVENUE**
- No system = reactive bidding = **LOW WIN RATE**

---

## How NEXUS Enforces This

### 1. Continuous Monitoring
- Checks every 15 minutes: "Did we find 3 opportunities today?"
- Logs progress: `2/3 opportunities found today (1 more needed)`
- Tracks in `daily_stats.json`

### 2. Automatic Escalation
**Before 8 PM:** Normal searching
- SAM.gov every 15 minutes
- Presolicitations every hour

**After 8 PM (if behind):** URGENT MODE
- Expands search to 72 hours back
- Searches additional NAICS codes
- Logs: `🚨 URGENT: Only 1/3 opportunities found and it's 20:00!`

### 3. End-of-Day Alert (11:45 PM)
**If target met:**
```
✅ SUCCESS! Found 3/3 opportunities today
   On track for 12+ bids this month
```

**If target missed:**
```
🚨 DAILY TARGET MISSED! Only found 1/3 opportunities
   Shortfall: 2 opportunities
   This puts monthly bid target (12+) at RISK
   CRITICAL ALERT SAVED to critical_alerts.jsonl
```

### 4. Monthly Tracking
- Tracks days target met vs. missed
- Projects monthly opportunity total
- Alerts if monthly target at risk

---

## What Counts Toward the 3?

### ✅ COUNTS:
- **New solicitations** from SAM.gov (any value, any type)
- **Presolicitations/Sources Sought** (relationship building)
- **Modifications/amendments** (new opportunities)
- **State/local opportunities** (if enabled)

### ❌ DOES NOT COUNT:
- Duplicates (already in system)
- Closed/cancelled opportunities
- Already-bid opportunities
- Auto-matches from internal database (must be NEW)

---

## Daily Stats File

```json
{
  "date": "2026-03-05",
  "new_opportunities_found": 2,
  "target_met": false,
  "urgent_mode": true
}
```

**File:** `daily_stats.json` (auto-created, do not delete)

---

## Critical Alerts

When daily target is missed, NEXUS creates a critical alert:

```json
{
  "alert_type": "DAILY_TARGET_MISSED",
  "severity": "CRITICAL",
  "timestamp": "2026-03-05T23:45:00",
  "message": "URGENT: Only found 1/3 opportunities today. Monthly bid target at risk!",
  "shortfall": 2,
  "action_required": "Review search criteria, expand NAICS codes, or manually search SAM.gov"
}
```

**File:** `critical_alerts.jsonl` (append-only, review daily)

---

## Running the Engine

### Option 1: Daemon Mode (Production)
```bash
./run_nexus_ingestion.sh
# Or manually:
python3 nexus_continuous_ingestion.py --daemon
```

Runs 24/7, enforces daily target automatically.

### Option 2: Manual Run
```bash
python3 nexus_continuous_ingestion.py --run-once
```

Shows daily target progress but does not enforce.

---

## When Target Is Missed

### Immediate Actions (Same Day):
1. **Check logs:** `tail -f nexus_ingestion.log`
2. **Expand search:** Add more NAICS codes to DDI_PROFILE
3. **Manual search:** Go to SAM.gov, search for "ALL" notice types
4. **Check alerts:** `cat critical_alerts.jsonl`

### Next Day:
1. **Review why:** Was it a slow day? System error? Wrong NAICS?
2. **Adjust parameters:** Maybe add more NAICS codes
3. **Make up shortfall:** Find 5 opportunities instead of 3

---

## Integration with Opportunity Hunter

The Opportunity Hunter interface shows:
- Current daily progress: `2/3 opportunities found today`
- Monthly projection: `On track for 15 bids this month`
- Urgency indicator: `⚠️ Need 1 more opportunity today`

---

## Success Metrics

### Green (Good):
- 3+ opportunities/day for 7+ consecutive days
- Monthly projection: 12+ bids
- Zero critical alerts

### Yellow (Warning):
- 2-3 days below target per week
- Monthly projection: 8-11 bids
- 1-2 critical alerts/week

### Red (Critical):
- Missing target 3+ days/week
- Monthly projection: <8 bids
- 3+ critical alerts/week

**Action:** Review search criteria, add NAICS codes, check system health

---

## This Is Not Optional

**This rule exists because:**
- DDI's revenue depends on consistent bidding
- 12+ bids/month is the minimum viable pipeline
- Missing a day compounds to missing the month
- The system enforces what humans forget

**NEXUS doesn't ask permission.**
**NEXUS doesn't make excuses.**
**NEXUS finds 3 opportunities every day.**

---

## Questions?

- **"What if there really are no opportunities?"**
  - Expand NAICS codes. Add related services. Check state/local.
  
- **"What if SAM.gov is down?"**
  - System logs error, checks again in 15 minutes. Alert if down >1 hour.
  
- **"Can I change the target?"**
  - Edit `DAILY_OPPORTUNITY_TARGET = 3` in `nexus_continuous_ingestion.py`
  - But don't lower it. The math doesn't work with fewer than 3.

---

*This rule is why NEXUS exists. This is the engine that drives revenue.*
