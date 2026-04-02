# NEXUS Regulatory Watch — FAR / acquisition primary sources

## What it does

- **`regulatory_watch.py`** queries the **Federal Register API** for **General Services Administration** documents whose text matches **“Federal Acquisition Regulation”**, within a rolling publication window.
- Compares results to a local snapshot (`uploads/regulatory_watch/snapshot.json`) and **appends only new Federal Register document numbers** to **`REGULATORY_CHANGE_LOG.md`**.
- **First run** seeds the snapshot **without** dumping historical rows into the log (avoids spam).

This is **not** SAM.gov. It does **not** replace counsel, FAR reading, or solicitation-specific clause review. It **flags** official FR activity tied to GSA/FAR so NEXUS can stay **aware** without manual paste.

## What it does *not* do (v1)

- Full-text ingest of the FAR from Acquisition.gov (HTML) or eCFR (large payloads).
- Automatic updates to `COMPLIANCE_KNOWLEDGE/` or proposal templates — **human review** after each log entry.

## How to run

```bash
cd "/Users/deedavis/NEXUS BACKEND"
python3 regulatory_watch.py
```

Dry run (no files written):

```bash
python3 regulatory_watch.py --dry-run
```

Wider window (default 14 days):

```bash
python3 regulatory_watch.py --lookback 21
```

Scheduler (same as weekly cron):

```bash
python3 nexus_scheduler.py --regulatory
```

**Continuous scheduler** (`nexus_scheduler.py --loop`) runs regulatory watch **once every 7 days** alongside other jobs.

## Cron (weekly)

```cron
0 9 * * 1 cd "/Users/deedavis/NEXUS BACKEND" && python3 nexus_scheduler.py --regulatory >> logs/regulatory_watch.log 2>&1
```

## Authoritative sources (manual)

| Need | URL |
|------|-----|
| FAR (working copy) | https://www.acquisition.gov/browse/index/far |
| eCFR Title 48 | https://www.ecfr.gov/current/title-48/chapter-1 |
| Federal Register (GSA) | https://www.federalregister.gov/agencies/general-services-administration |

## Files

| File | Role |
|------|------|
| `regulatory_watch.py` | Scanner |
| `REGULATORY_CHANGE_LOG.md` | Append-only human-readable log |
| `uploads/regulatory_watch/snapshot.json` | Seen FR document numbers |

---

*Dee Davis Inc. — NEXUS automation. Not legal advice.*
