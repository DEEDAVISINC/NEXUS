#!/usr/bin/env python3
"""
Cleanup stale NEXUS deadline noise — calendars + deadline_alerts.

Moves past auto-generated BID DEADLINE / BID DUE .ics files out of calendars/
so the dashboard, /calendar/feed.ics, and Apple Calendar stop showing dead bids.

Protects hand-made meetings / outreach / ops events (non-bid summaries).

Usage:
  python3 cleanup_stale_nexus_deadlines.py           # dry-run
  python3 cleanup_stale_nexus_deadlines.py --apply   # execute
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
from datetime import date, datetime
from pathlib import Path

BASE = Path(__file__).resolve().parent
CAL_DIR = BASE / "calendars"
ARCHIVE_DIR = CAL_DIR / "ARCHIVE_EXPIRED"
ALERTS_PATH = BASE / "deadline_alerts.json"
REPORT_PATH = BASE / "logs" / "stale_deadline_cleanup_last_run.json"

BID_SUMMARY_MARKERS = (
    "BID DEADLINE",
    "BID DUE",
    "CRITICAL BID DEADLINE",
)

# Never archive these even if date is past (hand-crafted / relationship)
PROTECT_NAME_MARKERS = (
    "MEETING",
    "GOVCON",
    "NOTARY",
    "SHIELD",
    "OUTREACH",
    "CARESOURCE",
    "MOLINA",
    "HAP_",
    "UBER_",
    "FOLLOW",
    "CALL_",
    "ORIENTATION",
    "CWC_",
    "SCHEDULED",
    "EMERGENCY",
    "SIGNING",
)


def _parse_dtstart(text: str) -> date | None:
    m = re.search(r"DTSTART(?:;[^:]*)?:(\d{8})", text)
    if not m:
        return None
    return datetime.strptime(m.group(1), "%Y%m%d").date()


def _summary(text: str) -> str:
    m = re.search(r"^SUMMARY:(.*)$", text, re.MULTILINE)
    return (m.group(1).strip() if m else "").upper()


def _is_auto_bid_event(text: str, filename: str) -> bool:
    summary = _summary(text)
    if any(marker in summary for marker in BID_SUMMARY_MARKERS):
        return True
    # Airtable auto files often carry UID *@nexus.deedavis.biz and BID emoji
    if "@nexus.deedavis.biz" in text and ("BID" in summary or "DEADLINE" in summary):
        return True
    upper = filename.upper()
    if any(p in upper for p in PROTECT_NAME_MARKERS):
        return False
    return False


def _is_protected(filename: str, text: str) -> bool:
    upper = filename.upper()
    if any(p in upper for p in PROTECT_NAME_MARKERS):
        return True
    summary = _summary(text)
    # Meetings / calls without bid markers
    if any(k in summary for k in ("MEETING", "CALL", "ZOOM", "ORIENTATION", "SIGNING")):
        if not any(m in summary for m in BID_SUMMARY_MARKERS):
            return True
    return False


def archive_past_bid_ics(*, today: date, apply: bool) -> dict:
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    moved = []
    kept_future = 0
    kept_protected = 0
    kept_non_bid_past = 0
    skipped_unknown = 0

    for path in sorted(CAL_DIR.glob("*.ics")):
        try:
            text = path.read_text(errors="ignore")
        except OSError:
            continue
        event_date = _parse_dtstart(text)
        if event_date is None:
            skipped_unknown += 1
            continue
        if event_date >= today:
            kept_future += 1
            continue
        if _is_protected(path.name, text):
            kept_protected += 1
            continue
        if not _is_auto_bid_event(text, path.name):
            kept_non_bid_past += 1
            continue

        dest = ARCHIVE_DIR / path.name
        moved.append({"file": path.name, "date": event_date.isoformat()})
        if apply:
            if dest.exists():
                dest = ARCHIVE_DIR / f"{path.stem}__dup{path.suffix}"
            shutil.move(str(path), str(dest))

    return {
        "moved_count": len(moved),
        "moved_sample": moved[:15],
        "kept_future": kept_future,
        "kept_protected_past": kept_protected,
        "kept_non_bid_past": kept_non_bid_past,
        "skipped_unknown_date": skipped_unknown,
        "archive_dir": str(ARCHIVE_DIR),
    }


def prune_deadline_alerts(*, today: date, apply: bool) -> dict:
    if not ALERTS_PATH.exists():
        return {"exists": False}
    data = json.loads(ALERTS_PATH.read_text())
    alerts = data.get("alerts") or []
    keep = []
    dropped_expired = 0
    for alert in alerts:
        level = (alert.get("alert_level") or "").upper()
        hours = alert.get("hours_left")
        deadline = str(alert.get("deadline") or "")[:10]
        past = False
        if isinstance(hours, (int, float)) and hours < 0:
            past = True
        elif deadline:
            try:
                past = datetime.strptime(deadline, "%Y-%m-%d").date() < today
            except ValueError:
                past = level == "EXPIRED"
        else:
            past = level == "EXPIRED"
        if past or level == "EXPIRED":
            dropped_expired += 1
            continue
        keep.append(alert)

    if apply:
        ALERTS_PATH.write_text(
            json.dumps(
                {"alerts": keep, "checked_at": datetime.now().isoformat(), "pruned_at": datetime.now().isoformat()},
                indent=2,
            )
            + "\n"
        )

    return {
        "exists": True,
        "before": len(alerts),
        "after": len(keep),
        "dropped_expired": dropped_expired,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="Execute moves/writes (default is dry-run)")
    parser.add_argument("--as-of", default=None, help="YYYY-MM-DD override (default: today America/Detroit-ish local)")
    args = parser.parse_args()

    today = datetime.strptime(args.as_of, "%Y-%m-%d").date() if args.as_of else date.today()
    mode = "APPLY" if args.apply else "DRY-RUN"

    cal = archive_past_bid_ics(today=today, apply=args.apply)
    alerts = prune_deadline_alerts(today=today, apply=args.apply)

    report = {
        "mode": mode,
        "as_of": today.isoformat(),
        "run_at": datetime.now().isoformat(),
        "calendars": cal,
        "deadline_alerts": alerts,
    }
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2) + "\n")

    print(f"[{mode}] as_of={today}")
    print(f"  Calendar past bid ICS to archive: {cal['moved_count']}")
    print(f"  Kept future: {cal['kept_future']} | protected past: {cal['kept_protected_past']} | non-bid past: {cal['kept_non_bid_past']}")
    if alerts.get("exists"):
        print(f"  deadline_alerts.json: {alerts['before']} → {alerts['after']} (dropped {alerts['dropped_expired']} expired)")
    print(f"  Report: {REPORT_PATH}")
    if not args.apply:
        print("\nRe-run with --apply to execute.")


if __name__ == "__main__":
    main()
