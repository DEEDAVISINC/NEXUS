#!/usr/bin/env python3
"""
NEXUS — AOG / 488190 SAM.gov scan (Freight 1st Direct lane)

Runs automatically from nexus_scheduler.py --mine (federal mining loop).
Reads SAM_GOV_API_KEY from the environment (loads repo `.env` from disk so cwd does not matter).

Writes: aog_sam_cache.json (project root) for dashboards / briefings.
"""

from __future__ import annotations

import json
import logging
import os
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Set

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
# Same .env as the rest of NEXUS — explicit path so cron/IDE cwd never hides the key
load_dotenv(BASE_DIR / ".env")

log = logging.getLogger(__name__)

CACHE_FILE = BASE_DIR / "aog_sam_cache.json"
SAM_URL = "https://api.sam.gov/prod/opportunities/v1/search"

JETA_PATTERNS = re.compile(
    r"into[- ]?plane|jet\s*a[- ]?1|jp[- ]?8|aviation\s*fuel|jet\s*fuel|"
    r"turbine\s*fuel|fbo\s*fuel|fuel\s*farm|avgas|flight\s*line\s*fuel",
    re.I,
)
AOG_PATTERNS = re.compile(
    r"aog|aircraft\s*on\s*ground|aviation\s*courier|aircraft\s*parts\s*courier|aog\s*courier|aog\s*delivery",
    re.I,
)

QUERIES = ['"488190"', "AOG", "aircraft on ground", "aviation courier"]


def classify_lane(title: str, naics_hint: str) -> str:
    t = title or ""
    if JETA_PATTERNS.search(t):
        return "JETA_FUEL"
    if AOG_PATTERNS.search(t):
        return "AOG_COURIER"
    if (naics_hint or "").strip() == "488190":
        return "TRIAGE_488190"
    return "OTHER"


def _fetch(api_key: str, q: str, posted_from: str, posted_to: str, limit: int = 100) -> List[Dict[str, Any]]:
    try:
        import requests
    except ImportError:
        log.warning("mine_aog_sam: requests not installed")
        return []

    params = {
        "api_key": api_key,
        "q": q,
        "postedFrom": posted_from,
        "postedTo": posted_to,
        "limit": limit,
        "offset": 0,
    }
    r = requests.get(SAM_URL, params=params, timeout=120)
    if r.status_code != 200:
        log.warning("mine_aog_sam: SAM %s for q=%s: %s", r.status_code, q, r.text[:200])
        return []
    data = r.json() or {}
    return data.get("opportunitiesData") or []


def run_aog_sam_scan(days_back: int = 90) -> Dict[str, Any]:
    """
    Query SAM for NAICS 488190 + AOG/aviation courier keywords; triage JETA vs AOG.
    Returns summary dict; writes aog_sam_cache.json on success.
    """
    api_key = (os.environ.get("SAM_GOV_API_KEY") or "").strip()
    if not api_key or api_key.upper() == "DEMO_KEY":
        log.debug("mine_aog_sam: SAM_GOV_API_KEY missing or DEMO_KEY — skip")
        return {
            "ok": False,
            "skipped": True,
            "reason": "no_sam_api_key",
            "count": 0,
            "aog_courier_count": 0,
            "opportunities": [],
        }

    posted_to = datetime.now().strftime("%m/%d/%Y")
    posted_from = (datetime.now() - timedelta(days=days_back)).strftime("%m/%d/%Y")

    seen: Set[str] = set()
    rows: List[Dict[str, Any]] = []

    for q in QUERIES:
        opps = _fetch(api_key, q, posted_from, posted_to)
        for opp in opps:
            nid = (opp.get("noticeId") or "").strip()
            if not nid or nid in seen:
                continue
            seen.add(nid)
            title = opp.get("title") or ""
            naics = str(opp.get("naicsCode") or opp.get("naics") or "")[:32]
            lane = classify_lane(title, naics)
            sol = opp.get("solicitationNumber") or ""
            agency = opp.get("agency") or ""
            posted = (opp.get("postedDate") or "")[:10]
            deadline = (opp.get("responseDeadLine") or "")[:19]
            set_aside = opp.get("typeOfSetAsideDescription") or opp.get("setAside") or ""

            rows.append(
                {
                    "noticeId": nid,
                    "title": title[:500],
                    "solicitationNumber": sol,
                    "agency": agency[:300],
                    "naicsCode": naics,
                    "lane": lane,
                    "postedDate": posted,
                    "responseDeadLine": deadline,
                    "setAside": str(set_aside)[:120],
                    "url": f"https://sam.gov/opp/{nid}/view",
                }
            )

    rows.sort(key=lambda x: (x["lane"] != "AOG_COURIER", x.get("postedDate") or ""))

    aog_n = sum(1 for r in rows if r["lane"] == "AOG_COURIER")
    out = {
        "ok": True,
        "skipped": False,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "posted_from": posted_from,
        "posted_to": posted_to,
        "days_back": days_back,
        "count": len(rows),
        "aog_courier_count": aog_n,
        "triage_488190_count": sum(1 for r in rows if r["lane"] == "TRIAGE_488190"),
        "jeta_fuel_count": sum(1 for r in rows if r["lane"] == "JETA_FUEL"),
        "opportunities": rows,
    }

    try:
        CACHE_FILE.write_text(json.dumps(out, indent=2), encoding="utf-8")
        log.info(
            "mine_aog_sam: wrote %s (%s notices, %s AOG_COURIER)",
            CACHE_FILE.name,
            len(rows),
            aog_n,
        )
    except OSError as e:
        log.warning("mine_aog_sam: could not write cache: %s", e)

    return out


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    r = run_aog_sam_scan(days_back=90)
    if r.get("skipped"):
        print(r.get("reason", "skipped"), file=sys.stderr)
        sys.exit(1)
    print(json.dumps({k: v for k, v in r.items() if k != "opportunities"}, indent=2))
    print(f"\nFull list: {CACHE_FILE}")


if __name__ == "__main__":
    main()
