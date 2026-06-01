#!/usr/bin/env python3
"""
NEXUS RADAR — Digital Navigation / Benefits Enrollment lane (SAM.gov)

Searches SAM.gov for digital navigator, benefits navigation, SDOH, and enrollment
assistance opportunities. Writes digital_nav_sam_cache.json for briefings.

Run:  python3 mine_digital_navigation_sam.py
"""

from __future__ import annotations

import json
import logging
import os
import re
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Set

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

log = logging.getLogger(__name__)

CACHE_FILE = BASE_DIR / "digital_nav_sam_cache.json"
SAM_URL = "https://api.sam.gov/opportunities/v2/search"

NAICS_CODES = ("624190", "624210", "561499", "541720", "624230")

KEYWORD_QUERIES = [
    "digital navigator",
    "benefits navigation",
    "enrollment assistance",
    "digital equity",
    "digital inclusion",
    "community health worker",
    "SHIP counselor",
    "ACA navigator",
    "health-related social needs",
    "HRSN",
    "information and referral",
    "broadband adoption",
]

LANE_PATTERNS = re.compile(
    r"digital\s*navigator|benefits\s*navig|enrollment\s*assist|digital\s*equity|"
    r"digital\s*inclusion|community\s*health\s*worker|\bchw\b|ship\s*counsel|"
    r"aca\s*navigator|health.related\s*social|hrsn|information\s*and\s*referral|"
    r"211\s*service|broadband\s*adoption|affordable\s*connectivity|"
    r"social\s*determinants|resource\s*navig|benefits\s*enrollment",
    re.I,
)


def _fetch(
    api_key: str,
    posted_from: str,
    posted_to: str,
    *,
    ncode: str | None = None,
    q: str | None = None,
    limit: int = 100,
) -> List[Dict[str, Any]]:
    import json as _json
    import urllib.error
    import urllib.parse
    import urllib.request

    params: Dict[str, Any] = {
        "api_key": api_key,
        "postedFrom": posted_from,
        "postedTo": posted_to,
        "limit": limit,
        "offset": 0,
        "ptype": "o,k,r,s,p",
    }
    if ncode:
        params["ncode"] = ncode
    if q:
        params["q"] = q

    url = f"{SAM_URL}?{urllib.parse.urlencode(params)}"
    try:
        with urllib.request.urlopen(url, timeout=120) as resp:
            data = _json.loads(resp.read())
    except (urllib.error.URLError, TimeoutError, _json.JSONDecodeError) as exc:
        log.warning("digital_nav SAM ncode=%s q=%s: %s", ncode, q, exc)
        return []

    time.sleep(0.5)
    return data.get("opportunitiesData") or []


def _normalize(opp: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "title": opp.get("title") or "",
        "solicitationNumber": opp.get("solicitationNumber") or "",
        "department": opp.get("department") or opp.get("fullParentPathName") or "",
        "responseDeadLine": opp.get("responseDeadLine") or "",
        "postedDate": opp.get("postedDate") or "",
        "naicsCode": opp.get("naicsCode") or "",
        "typeOfSetAside": opp.get("typeOfSetAsideDescription") or opp.get("typeOfSetAside") or "",
        "type": opp.get("type") or "",
        "uiLink": opp.get("uiLink") or "",
    }


def run_digital_nav_scan(days_back: int = 90) -> Dict[str, Any]:
    api_key = (os.environ.get("SAM_GOV_API_KEY") or "").strip()
    if not api_key or api_key.upper() == "DEMO_KEY":
        return {
            "ok": False,
            "skipped": True,
            "reason": "no_sam_api_key",
            "count": 0,
            "opportunities": [],
        }

    posted_to = datetime.now().strftime("%m/%d/%Y")
    posted_from = (datetime.now() - timedelta(days=days_back)).strftime("%m/%d/%Y")

    seen: Set[str] = set()
    results: List[Dict[str, Any]] = []

    for nc in NAICS_CODES:
        for opp in _fetch(api_key, posted_from, posted_to, ncode=nc):
            sid = opp.get("solicitationNumber") or opp.get("noticeId") or ""
            if sid and sid in seen:
                continue
            if sid:
                seen.add(sid)
            row = _normalize(opp)
            row["matchReason"] = f"NAICS {nc}"
            results.append(row)

    for kw in KEYWORD_QUERIES:
        for opp in _fetch(api_key, posted_from, posted_to, q=kw):
            sid = opp.get("solicitationNumber") or opp.get("noticeId") or ""
            title = opp.get("title") or ""
            desc = opp.get("description") or ""
            if not LANE_PATTERNS.search(f"{title} {desc}"):
                continue
            if sid and sid in seen:
                continue
            if sid:
                seen.add(sid)
            row = _normalize(opp)
            row["matchReason"] = f"keyword: {kw}"
            results.append(row)

    payload = {
        "ok": True,
        "scannedAt": datetime.now().isoformat(),
        "postedFrom": posted_from,
        "postedTo": posted_to,
        "count": len(results),
        "opportunities": sorted(results, key=lambda x: x.get("responseDeadLine") or "9999"),
    }

    CACHE_FILE.write_text(json.dumps(payload, indent=2))
    log.info("digital_nav_sam: wrote %s (%d opps)", CACHE_FILE.name, len(results))
    return payload


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    out = run_digital_nav_scan()
    print(json.dumps({"ok": out.get("ok"), "count": out.get("count"), "cache": str(CACHE_FILE)}, indent=2))
    for o in (out.get("opportunities") or [])[:20]:
        print("---")
        print(o.get("title", "")[:100])
        print(o.get("solicitationNumber", ""))
        print(o.get("responseDeadLine", "")[:10] if o.get("responseDeadLine") else "")
        print(o.get("matchReason", ""))
