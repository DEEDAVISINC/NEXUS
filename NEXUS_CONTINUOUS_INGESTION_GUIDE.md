# NEXUS Continuous Ingestion Engine

## 🎯 CRITICAL BUSINESS RULE: 3 Opportunities Per Day

**NEXUS MUST find 3 NEW opportunities every single day.**

This is how DDI hits the 12+ bids per month target required to win contracts consistently.

**The Math:**
- 3 opportunities/day × 30 days = 90 opportunities/month
- 15% bid rate = 13-14 bids submitted
- 25% win rate = 3-4 contracts won per month
- **Revenue target: ACHIEVED**

**Without this rule:** Find 1 opportunity/day → 4 bids/month → 1 win/month → **FAILURE**

---

## Overview

The Opportunity Hunter is now powered by a **24/7 continuous data ingestion engine** that automatically mines opportunities from multiple sources and keeps your Airtable database fresh.

**Before:** Search interface over static data that goes stale  
**Now:** Living system that continuously ingests from federal, state, and local sources

---

## How It Works

### Data Sources (Continuous Polling)

| Source | Frequency | What It Gets |
|--------|-----------|--------------|
| **SAM.gov API** | Every 15 minutes | New federal opportunities, set-asides, modifications |
| **SAM.gov Presols** | Every hour | Presolicitations, sources sought, RFIs |
| **USASpending** | Daily 6 AM | Agency spending intelligence, incumbent data |
| **Michigan DTMB** | Daily | State procurement opportunities |
| **Local/Municipal** | Weekly | County and city opportunities |

### AI Scoring Pipeline

Every ingested opportunity automatically gets:
1. **Match Score** (0-100) based on DDI criteria
2. **Tier Classification** (excellent/good/moderate/develop)
3. **Bid Recommendation** (BID_NOW / STRONG_CONSIDER / EVALUATE / MONITOR)

### Auto-Alert System

- **Score ≥ 85:** Immediate high-priority alert
- **EDWOSB set-aside:** Automatic flag for priority handling
- **Presolicitation:** Auto-generates buyer outreach email draft
- **Deadline < 14 days:** Urgent action required flag

---

## Components

### 1. `nexus_continuous_ingestion.py`
The main engine. Runs as a daemon or scheduled job.

**Usage:**
```bash
# Run once (testing)
python3 nexus_continuous_ingestion.py --run-once

# Run continuously (production)
python3 nexus_continuous_ingestion.py --daemon

# SAM.gov only
python3 nexus_continuous_ingestion.py --sam-only
```

### 2. `nexus_opportunity_hunter_api.py` + **NOVA** (`NOVASystem.tsx`)
API endpoints for the Opportunity Hunter interface. **UI:** NEXUS frontend → **NOVA** (`/?view=opportunity-hunter`). Standalone `nexus_opportunity_hunter.html` retired.

**New Endpoints:**
- `GET /api/hunter/profile` — DDI profile + data freshness
- `POST /api/hunter/agencies` — Search agencies (internal + live)
- `POST /api/hunter/refresh` — Force immediate data refresh
- `GET /api/hunter/agency/<name>/scorecard` — Detailed scorecard

### 3. `run_nexus_ingestion.sh`
Convenience script to start the daemon.

```bash
./run_nexus_ingestion.sh
```

---

## Data Freshness Indicators

The Opportunity Hunter now shows:

```json
{
  "data_freshness": {
    "airtable": {
      "status": "fresh",  // fresh / stale / error
      "last_update": "2026-03-05T14:30:00",
      "record_count": 2847
    },
    "sam_gov": {
      "status": "fresh",
      "last_update": "2026-03-05 14:15:23"
    },
    "usaspending": {
      "status": "fresh",
      "last_update": "2026-03-05 06:00:45"
    }
  }
}
```

**Visual indicators:**
- 🟢 Fresh (updated within last 24 hours)
- 🟡 Stale (not updated in 24+ hours)
- 🔴 Error (connection/source issue)

---

## Search Modes

The Opportunity Hunter now supports 3 search modes:

### 1. Internal Database
Search only your existing Airtable opportunities.
- ✅ Fast, scored opportunities
- ❌ Only what you've already ingested

### 2. Live Federal Search
Query SAM.gov in real-time.
- ✅ Fresh opportunities not yet in your database
- ❌ Slower (API calls)

### 3. Combined (Recommended)
Internal + Live SAM.gov + USASpending intelligence.
- ✅ Most comprehensive
- ✅ Shows opportunities from multiple sources
- ✅ Identifies high-spending agencies even without active opportunities

---

## Deployment Options

### Option 1: Local Daemon (Development)
```bash
# Terminal 1: Start ingestion engine
./run_nexus_ingestion.sh

# Terminal 2: Start API server
python3 api_server.py

# Access Opportunity Hunter at: http://localhost:5000/hunter
```

### Option 2: Systemd Service (Production)
Create `/etc/systemd/system/nexus-ingestion.service`:

```ini
[Unit]
Description=NEXUS Continuous Data Ingestion
After=network.target

[Service]
Type=simple
User=deedavis
WorkingDirectory=/Users/deedavis/NEXUS BACKEND
Environment="AIRTABLE_API_KEY=your_key"
Environment="SAM_GOV_API_KEY=your_key"
ExecStart=/usr/bin/python3 /Users/deedavis/NEXUS BACKEND/nexus_continuous_ingestion.py --daemon
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable nexus-ingestion
sudo systemctl start nexus-ingestion
sudo systemctl status nexus-ingestion
```

### Option 3: Cron Job (Simple)
```bash
# Edit crontab
crontab -e

# Add entries
*/15 * * * * cd "/Users/deedavis/NEXUS BACKEND" && python3 nexus_continuous_ingestion.py --sam-only
0 6 * * * cd "/Users/deedavis/NEXUS BACKEND" && python3 nexus_continuous_ingestion.py --run-once
```

---

## File Structure

```
NEXUS BACKEND/
├── nexus_continuous_ingestion.py    # Main ingestion engine
├── nexus_opportunity_hunter_api.py  # API endpoints
├── run_nexus_ingestion.sh           # Daemon runner script
├── nexus_ingestion.log              # Ingestion logs (auto-created)
├── seen_notice_ids.json             # Deduplication tracking
├── high_score_alerts.jsonl          # High-score alerts log
├── logs/                            # Log directory
└── NEXUS_CONTINUOUS_INGESTION_GUIDE.md  # This file
```

---

## Monitoring

### Watch Live Logs
```bash
tail -f nexus_ingestion.log
```

### Check Daily Target Progress
```bash
curl http://localhost:5000/api/hunter/profile | jq .daily_target
```

**Response:**
```json
{
  "found": 2,
  "target": 3,
  "percentage": 66.7,
  "target_met": false,
  "remaining": 1,
  "monthly_projection": 8,
  "urgent": false
}
```

### Check Data Freshness
```bash
curl http://localhost:5000/api/hunter/profile | jq .data_freshness
```

### Force Immediate Refresh
```bash
curl -X POST http://localhost:5000/api/hunter/refresh
```

### Check Critical Alerts (Target Missed)
```bash
tail -f critical_alerts.jsonl
```

### View High-Score Alerts
```bash
tail -f high_score_alerts.jsonl
```

---

## Daily Target Enforcement

### How It Works

1. **Every 15 minutes:** System checks "Did we find 3 opportunities today?"
2. **Progress tracking:** Logs `2/3 opportunities found today (1 more needed)`
3. **Urgent mode:** After 8 PM if behind, expands search parameters
4. **End-of-day:** At 11:45 PM, generates alert if target missed

### Urgent Mode Triggers When:
- 8 PM hits and < 3 opportunities found
- Search expands to 72 hours back
- Additional NAICS codes searched
- Logs: `🚨 URGENT: Only 1/3 opportunities found!`

### Alert Levels

**Green (On Track):**
```
🎯 [DAILY TARGET] ACHIEVED! Found 3/3 opportunities today
   On track for 12+ bids this month
```

**Red (Missed):**
```
🚨 DAILY TARGET MISSED! Only found 1/3 opportunities
   Shortfall: 2 opportunities
   This puts monthly bid target (12+) at RISK
   CRITICAL ALERT saved to critical_alerts.jsonl
```

### Files Created
- `daily_stats.json` - Current day's progress
- `critical_alerts.jsonl` - Missed target alerts (append-only)
- `nexus_ingestion.log` - Real-time progress logs

---

## What This Solves

**Problem:** Searching stale data that misses new opportunities  
**Solution:** Continuous ingestion keeps data fresh within 15 minutes

**Problem:** Missing presolicitations that close before you see them  
**Solution:** Hourly presolicitation hunting with auto-alerts

**Problem:** Not knowing which agencies spend in your NAICS  
**Solution:** Daily USASpending sync builds agency intelligence

**Problem:** Discovering opportunities too late to bid  
**Solution:** Real-time alerts for high-score opportunities

---

## Next Steps

1. **Configure API keys** (if not already set)
   - SAM_GOV_API_KEY
   - AIRTABLE_API_KEY
   - AIRTABLE_BASE_ID

2. **Test the engine**
   ```bash
   python3 nexus_continuous_ingestion.py --run-once
   ```

3. **Start the daemon**
   ```bash
   ./run_nexus_ingestion.sh
   ```

4. **Open the Opportunity Hunter**
   ```
   http://localhost:5000/hunter
   ```

5. **Monitor for a day**
   Check `nexus_ingestion.log` and `high_score_alerts.jsonl`

---

## Integration with Existing NEXUS

The continuous ingestion engine integrates with:

- **AIRTABLE (69 tables)** — Stores all opportunities, agency intelligence, alerts
- **Opportunity Hunter** — Visual interface for searching combined data
- **NEXUS Stage Tracking** — Auto-assigns stages to new opportunities
- **Calendar System** — Auto-creates deadline reminders
- **Alert System** — High-score opportunities trigger notifications

**Data Flow:**
```
SAM.gov → Ingestion Engine → AI Scoring → Airtable → Opportunity Hunter
                ↓
        High Score? → Alert Dee → Auto-generate docs
```

---

*The Opportunity Hunter is now a living, breathing system that works 24/7 to find you opportunities. Not just a search box over stale data.*
