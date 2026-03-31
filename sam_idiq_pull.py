#!/usr/bin/env python3
"""
Pull IDIQ / multiple-award style opportunities from SAM.gov and award intel from USASpending.

Requires: SAM_GOV_API_KEY in .env for SAM.gov (Get Opportunities Public API v2).
USASpending has no key requirement.

Outputs:
  data/sam_idiq_sam_gov_pull.json   — raw SAM opportunities (if API succeeds)
  data/sam_idiq_usaspending_pull.json — raw USASpending award rows
  SAM_IDIQ_PULL_LATEST.md           — human-readable summary

Run: python3 sam_idiq_pull.py
"""

from __future__ import annotations

import json
import os
import re
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Set
from urllib.parse import urlencode

import requests
from dotenv import load_dotenv

BASE = Path(__file__).resolve().parent
DATA = BASE / "data"
DATA.mkdir(parents=True, exist_ok=True)

SAM_URL = "https://api.sam.gov/opportunities/v2/search"
USASPEND_URL = "https://api.usaspending.gov/api/v2/search/spending_by_award/"

# Title search terms for SAM.gov (searches opportunity title field per GSA API docs)
SAM_TITLE_TERMS = [
    "IDIQ",
    "MATOC",
    "MACC",
    "Multiple Award",
    "GWAC",
    "Indefinite Delivery",
]

# USASpending keyword searches (award descriptions / derived text)
USA_KEYWORDS = ["IDIQ", "MATOC", "MACC", "INDEFINITE DELIVERY INDEFINITE"]


def _sam_search_term(
    api_key: str, title: str, days_back: int, session: requests.Session
) -> List[Dict[str, Any]]:
    posted_from = (datetime.now() - timedelta(days=days_back)).strftime("%m/%d/%Y")
    posted_to = datetime.now().strftime("%m/%d/%Y")
    out: List[Dict[str, Any]] = []
    offset = 0
    while True:
        params = {
            "api_key": api_key,
            "title": title,
            "postedFrom": posted_from,
            "postedTo": posted_to,
            "limit": 100,
            "offset": offset,
            "ptype": "o,p,k,r",
        }
        r = session.get(SAM_URL, params=params, timeout=(10, 60))
        if r.status_code != 200:
            raise RuntimeError(f"SAM {r.status_code}: {r.text[:800]}")
        data = r.json()
        batch = data.get("opportunitiesData") or []
        out.extend(batch)
        total = int(data.get("totalRecords") or 0)
        if offset + len(batch) >= total or len(batch) < 100:
            break
        offset += 100
        time.sleep(0.4)
    return out


def pull_sam(api_key: str, days_back: int = 120) -> List[Dict[str, Any]]:
    """Dedupe by noticeId; merge all title searches."""
    session = requests.Session()
    session.headers["User-Agent"] = "NEXUS-sam_idiq_pull/1.0 (Dee Davis Inc.)"
    seen: Set[str] = set()
    merged: List[Dict[str, Any]] = []
    for term in SAM_TITLE_TERMS:
        try:
            rows = _sam_search_term(api_key, term, days_back, session)
        except Exception as e:
            print(f"   SAM title={term!r} failed: {e}")
            continue
        for row in rows:
            nid = str(row.get("noticeId") or row.get("notice_id") or "")
            if nid and nid in seen:
                continue
            if nid:
                seen.add(nid)
            merged.append({**row, "_searchTitleTerm": term})
        print(f"   SAM title={term!r}: +{len(rows)} rows (merged total {len(merged)})")
        time.sleep(0.35)
    return merged


def pull_usaspending(pages: int = 3, per_page: int = 50) -> List[Dict[str, Any]]:
    """Recent contract awards whose text matches IDIQ-style keywords."""
    merged: Dict[str, Any] = {}
    for kw in USA_KEYWORDS:
        for page in range(1, pages + 1):
            payload = {
                "filters": {
                    "time_period": [
                        {
                            "start_date": (datetime.now() - timedelta(days=730)).strftime("%Y-%m-%d"),
                            "end_date": datetime.now().strftime("%Y-%m-%d"),
                        }
                    ],
                    "award_type_codes": ["A", "B", "C", "D"],
                    "keywords": [kw],
                },
                "fields": [
                    "Award ID",
                    "Award Amount",
                    "Description",
                    "Recipient Name",
                    "Awarding Agency",
                    "Start Date",
                ],
                "limit": per_page,
                "page": page,
                "sort": "Award Amount",
                "order": "desc",
            }
            r = requests.post(USASPEND_URL, json=payload, timeout=45)
            if r.status_code != 200:
                print(f"   USASpending keyword={kw!r} page={page}: {r.status_code}")
                continue
            data = r.json()
            for row in data.get("results") or []:
                aid = row.get("Award ID") or row.get("generated_internal_id")
                if aid and aid not in merged:
                    merged[aid] = {**row, "_keyword": kw}
                elif aid:
                    merged[aid]["_keywords_extra"] = merged[aid].get("_keywords_extra", []) + [kw]
        time.sleep(0.2)
    return list(merged.values())


def write_markdown(
    sam_rows: List[Dict[str, Any]],
    usa_rows: List[Dict[str, Any]],
    sam_error: str | None,
) -> None:
    lines = [
        f"# SAM / USASpending IDIQ-style pull — {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "Auto-generated by `sam_idiq_pull.py`.",
        "",
        "## SAM.gov — active opportunities (title search)",
        "",
    ]
    if sam_error:
        lines.append(f"**SAM.gov:** not loaded — {sam_error}")
        lines.append("")
        lines.append(
            "To load SAM rows: set `SAM_GOV_API_KEY` in `.env` and run `python3 sam_idiq_pull.py` where `api.sam.gov` is reachable."
        )
    elif not sam_rows:
        lines.append("**No rows** — API returned empty for all title terms in the date window.")
    else:
        lines.append(f"**Count:** {len(sam_rows)}")
        lines.append("")
        lines.append("| Title | Agency | Solicitation | Posted | Deadline | Link |")
        lines.append("|---|---|---|---|---|---|")
        for r in sam_rows[:150]:
            title = (r.get("title") or "")[:120].replace("|", "/")
            agency = (r.get("department") or r.get("fullParentPathName") or "")[:80].replace("|", "/")
            sol = (r.get("solicitationNumber") or "")[:40]
            posted = (r.get("postedDate") or "")[:16]
            dl = (r.get("responseDeadLine") or "")[:16]
            nid = r.get("noticeId") or ""
            link = f"https://sam.gov/opp/{nid}/view" if nid else ""
            lines.append(f"| {title} | {agency} | {sol} | {posted} | {dl} | {link} |")
        if len(sam_rows) > 150:
            lines.append(f"| … | *{len(sam_rows) - 150} more in JSON* | | | | |")
    lines.extend(
        [
            "",
            "## USASpending — award descriptions (keyword: IDIQ / MATOC / MACC family)",
            "",
            "*Use for incumbent / vehicle intelligence; awards are not active SAM solicitations.*",
            "",
        ]
    )
    lines.append(f"**Count:** {len(usa_rows)} (deduped by Award ID)")
    lines.append("")
    lines.append("| Award ID | Amount | Agency | Recipient | Start | Summary |")
    lines.append("|---|---:|---|---|---|---|")
    rx = re.compile(r"\s+")
    for r in sorted(usa_rows, key=lambda x: float(x.get("Award Amount") or 0), reverse=True)[:80]:
        aid = (r.get("Award ID") or "")[:40]
        amt = r.get("Award Amount")
        try:
            amt_s = f"${float(amt):,.0f}" if amt is not None else ""
        except (TypeError, ValueError):
            amt_s = str(amt)
        ag = (r.get("Awarding Agency") or "")[:40].replace("|", "/")
        rec = (r.get("Recipient Name") or "")[:35].replace("|", "/")
        sd = (r.get("Start Date") or "")[:12]
        desc = r.get("Description") or ""
        desc = rx.sub(" ", desc)[:160].replace("|", "/")
        lines.append(f"| {aid} | {amt_s} | {ag} | {rec} | {sd} | {desc} |")
    if len(usa_rows) > 80:
        lines.append(f"| … | | | | | *{len(usa_rows) - 80} more in JSON* |")
    lines.append("")
    (BASE / "SAM_IDIQ_PULL_LATEST.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    load_dotenv(BASE / ".env")
    api_key = (os.getenv("SAM_GOV_API_KEY") or "").strip()

    print("USASpending (no key required)...")
    usa = pull_usaspending()
    (DATA / "sam_idiq_usaspending_pull.json").write_text(
        json.dumps(usa, indent=2, default=str), encoding="utf-8"
    )
    print(f"   USASpending: {len(usa)} deduped awards")

    sam_rows: List[Dict[str, Any]] = []
    sam_err: str | None = None
    if not api_key:
        sam_err = "SAM_GOV_API_KEY not set"
        print(sam_err)
    else:
        print("SAM.gov Get Opportunities API...")
        try:
            sam_rows = pull_sam(api_key, days_back=120)
            (DATA / "sam_idiq_sam_gov_pull.json").write_text(
                json.dumps(sam_rows, indent=2, default=str), encoding="utf-8"
            )
            print(f"   SAM.gov: {len(sam_rows)} opportunities")
        except Exception as e:
            sam_err = str(e)
            print(f"   SAM error: {e}")

    write_markdown(sam_rows, usa, sam_err)
    print(f"Wrote {BASE / 'SAM_IDIQ_PULL_LATEST.md'}")


if __name__ == "__main__":
    main()
