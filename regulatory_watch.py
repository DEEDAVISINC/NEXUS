#!/usr/bin/env python3
"""
NEXUS Regulatory Watch — FAR / federal acquisition primary sources
===================================================================
Pulls authoritative signals (not SAM.gov) so solicitation responses track
real FAR/FAC activity. Human review before treating output as legal advice.

Sources (v1):
  - Federal Register API — GSA + "Federal Acquisition Regulation" term, dated window

Weekly cron example (Mondays 9 AM ET):
  0 9 * * 1 cd "/path/to/NEXUS BACKEND" && python3 regulatory_watch.py >> logs/regulatory_watch.log 2>&1

Or via scheduler:
  python3 nexus_scheduler.py --regulatory
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

import requests

# -----------------------------------------------------------------------------
# Paths
# -----------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parent
UPLOADS = ROOT / "uploads" / "regulatory_watch"
SNAPSHOT_PATH = UPLOADS / "snapshot.json"
CHANGE_LOG = ROOT / "REGULATORY_CHANGE_LOG.md"

FR_API = "https://www.federalregister.gov/api/v1/documents.json"

# Official reading list (no auto-fetch of full text in v1 — links only)
AUTHORITATIVE_FAR_LINKS = (
    "https://www.acquisition.gov/browse/index/far",
    "https://www.ecfr.gov/current/title-48/chapter-1",
    "https://www.federalregister.gov/agencies/general-services-administration",
)


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _load_snapshot() -> Dict[str, Any]:
    if not SNAPSHOT_PATH.exists():
        return {"seen_document_numbers": [], "last_run_iso": None}
    try:
        with open(SNAPSHOT_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {"seen_document_numbers": [], "last_run_iso": None}


def _save_snapshot(data: Dict[str, Any]) -> None:
    UPLOADS.mkdir(parents=True, exist_ok=True)
    tmp = SNAPSHOT_PATH.with_suffix(".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    tmp.replace(SNAPSHOT_PATH)


def fetch_gsa_far_documents(
    publication_date_gte: str, per_page: int = 50
) -> List[Dict[str, Any]]:
    """
    GSA-published Federal Register documents matching FAR-related term.
    publication_date_gte: YYYY-MM-DD
    """
    params: Dict[str, Any] = {
        "conditions[agencies][]": "general-services-administration",
        "conditions[term]": "Federal Acquisition Regulation",
        "conditions[publication_date][gte]": publication_date_gte,
        "per_page": per_page,
        "order": "newest",
    }
    r = requests.get(FR_API, params=params, timeout=90)
    r.raise_for_status()
    data = r.json()
    return list(data.get("results") or [])


def _format_doc_line(doc: Dict[str, Any]) -> str:
    num = doc.get("document_number") or doc.get("id") or "?"
    title = (doc.get("title") or "").strip()
    pub = doc.get("publication_date") or ""
    url = doc.get("html_url") or ""
    return f"- **{num}** ({pub}) — {title}\n  - {url}"


def append_change_log(
    new_docs: List[Dict[str, Any]], run_id: str, publication_window: str
) -> None:
    if not new_docs:
        return

    lines = [
        "",
        f"## Scan {run_id}",
        "",
        f"**Window:** Federal Register — GSA + FAR term, `publication_date >= {publication_window}`",
        "",
        "**New since last snapshot (review before relying in proposals):**",
        "",
    ]
    for d in new_docs:
        lines.append(_format_doc_line(d))
        lines.append("")

    lines.extend(
        [
            "**Human action:** Verify text on Federal Register / Acquisition.gov; update internal compliance notes if material.",
            "",
            "---",
            "",
        ]
    )

    existing = ""
    if CHANGE_LOG.exists():
        existing = CHANGE_LOG.read_text(encoding="utf-8")

    CHANGE_LOG.write_text(existing + "\n".join(lines), encoding="utf-8")


def ensure_change_log_header() -> None:
    if CHANGE_LOG.exists() and CHANGE_LOG.stat().st_size > 0:
        return
    CHANGE_LOG.write_text(
        "\n".join(
            [
                "# NEXUS — Regulatory change log (FAR / acquisition primary sources)",
                "",
                "**Purpose:** Append-only log when `regulatory_watch.py` finds **new** GSA/FAR-related Federal Register documents.",
                "",
                "**Not legal advice.** Confirm against https://www.acquisition.gov/browse/index/far and eCFR before citing in bids.",
                "",
                "**Authoritative URLs (manual reference):**",
                "",
                *[f"- {u}" for u in AUTHORITATIVE_FAR_LINKS],
                "",
                "---",
                "",
            ]
        ),
        encoding="utf-8",
    )


def run_scan(
    lookback_days: int = 14,
    dry_run: bool = False,
) -> Dict[str, Any]:
    ensure_change_log_header()
    snap = _load_snapshot()
    seen: Set[str] = set(snap.get("seen_document_numbers") or [])

    now = _utc_now()
    gte = (now - timedelta(days=lookback_days)).strftime("%Y-%m-%d")

    last_run = snap.get("last_run_iso")
    if last_run:
        try:
            lr = datetime.fromisoformat(last_run.replace("Z", "+00:00"))
            alt_gte = (lr - timedelta(days=1)).strftime("%Y-%m-%d")
            if alt_gte > gte:
                gte = alt_gte
        except ValueError:
            pass

    results = fetch_gsa_far_documents(publication_date_gte=gte)
    new_docs: List[Dict[str, Any]] = []
    new_numbers: List[str] = []
    bootstrap = not seen and not snap.get("last_run_iso")

    for doc in results:
        num = doc.get("document_number")
        if not num:
            continue
        if num not in seen:
            new_docs.append(doc)
            new_numbers.append(num)
        seen.add(num)

    run_id = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    payload = {
        "last_run_iso": run_id,
        "seen_document_numbers": sorted(seen)[-500:],
        "last_publication_date_gte": gte,
        "last_new_count": len(new_docs),
        "last_fetch_count": len(results),
    }

    if dry_run:
        return {
            "publication_date_gte": gte,
            "fetched": len(results),
            "new_documents": len(new_docs),
            "new_document_numbers": new_numbers,
            "dry_run": True,
            "bootstrap": bootstrap,
        }

    # First run: record IDs only — do not append a wall of historical FR notices.
    if bootstrap:
        _save_snapshot(payload)
        payload["bootstrap"] = True
        payload["note"] = "First run: snapshot seeded; no change-log spam. Future runs log only new document numbers."
        return payload

    if new_docs:
        to_log = new_docs[:40]
        if len(new_docs) > 40:
            to_log = to_log + [
                {
                    "document_number": "(truncated)",
                    "publication_date": "",
                    "title": f"{len(new_docs) - 40} additional new document(s) not listed — increase lookback or query FR API",
                    "html_url": "https://www.federalregister.gov/",
                }
            ]
        append_change_log(to_log, run_id, gte)
    _save_snapshot(payload)

    return {
        "publication_date_gte": gte,
        "fetched": len(results),
        "new_documents": len(new_docs),
        "new_document_numbers": new_numbers,
        "dry_run": False,
        "bootstrap": False,
    }


def main(argv: Optional[List[str]] = None) -> int:
    p = argparse.ArgumentParser(description="NEXUS regulatory watch (FAR / FR)")
    p.add_argument(
        "--lookback",
        type=int,
        default=14,
        help="Days for FR publication_date filter (default 14)",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Fetch and report only; do not write snapshot or log",
    )
    args = p.parse_args(argv)

    try:
        out = run_scan(lookback_days=args.lookback, dry_run=args.dry_run)
    except requests.RequestException as e:
        print(f"ERROR: network — {e}", file=sys.stderr)
        return 2
    except OSError as e:
        print(f"ERROR: filesystem — {e}", file=sys.stderr)
        return 3

    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
