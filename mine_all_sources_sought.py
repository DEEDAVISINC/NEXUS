#!/usr/bin/env python3
"""
NEXUS — ALL Sources Sought Miner (No Set-Aside Filter)

Queries SAM.gov API for Sources Sought notices ONLY.
NO set-aside filter — returns ALL sources sought regardless of EDWOSB/WOSB/SB/8a/etc.

Notice type: r = Sources Sought
Posted: Last 14 days (configurable)
Excludes: Opportunities already in BIDS:RESOURCES

Output: ALL_SOURCES_SOUGHT.md

Run: python3 mine_all_sources_sought.py
"""

import json
import os
import re
import subprocess
from urllib.parse import urlencode
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Set

from dotenv import load_dotenv

load_dotenv()

# Paths
BASE_DIR = Path(__file__).resolve().parent
BIDS_DIR = BASE_DIR / "BIDS:RESOURCES"
OUTPUT_FILE = BASE_DIR / "ALL_SOURCES_SOUGHT.md"

# Sources Sought only
NOTICE_TYPE = "r"

# Known solicitation numbers to exclude (from BIDS:RESOURCES)
KNOWN_EXCLUDED = {
    "W912DR25QA005",
    "W911SA26QA093",
    "N6247324R0054",
    "36C24126Q0236",
    "W912EF26RSS03",
    "36C25026Q0216",
    "36C25626R0057",
    "36C25226Q0235",
    "36C25626Q0360",
    "36C24126Q0258",
    "W9127N26QA035",
    "190000000912",
}


def extract_existing_solicitation_ids() -> Set[str]:
    """Extract notice IDs and solicitation numbers from BIDS:RESOURCES."""
    excluded = set(KNOWN_EXCLUDED)

    if not BIDS_DIR.exists():
        return excluded

    sol_pattern = re.compile(
        r"\b(W91[A-Z0-9]{8,15}|36C[A-Z0-9]{8,15}|N62[A-Z0-9]{8,15}|SPE7[A-Z0-9]{8,15}|70B[A-Z0-9]{8,15}|19[0-9]{9,})\b",
        re.I,
    )

    for item in BIDS_DIR.iterdir():
        if item.is_dir():
            for match in sol_pattern.finditer(item.name):
                excluded.add(match.group(1).upper())

    return excluded


def search_sam_gov_sources_sought(days_back: int = 14) -> List[Dict]:
    """Search SAM.gov API for Sources Sought — NO set-aside filter."""
    api_key = os.getenv("SAM_GOV_API_KEY", "DEMO_KEY")
    url = "https://api.sam.gov/opportunities/v2/search"

    # Do NOT include typeOfSetAside — returns ALL set-asides
    params = {
        "api_key": api_key,
        "ptype": NOTICE_TYPE,
        "limit": 100,
        "offset": 0,
        "postedFrom": (datetime.now() - timedelta(days=days_back)).strftime("%m/%d/%Y"),
        "postedTo": datetime.now().strftime("%m/%d/%Y"),
    }

    all_opps = []
    offset = 0

    while True:
        params["offset"] = offset
        try:
            param_str = urlencode(params)
            cmd = ["curl", "-s", "-m", "25", f"{url}?{param_str}"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode != 0:
                print("   API error")
                break

            data = json.loads(result.stdout) if result.stdout else {}
            opps = data.get("opportunitiesData", [])
            if not opps:
                break

            all_opps.extend(opps)
            total = data.get("totalRecords", 0)
            if offset + len(opps) >= total or len(opps) < 100:
                break
            offset += 100
            time.sleep(1)  # Rate limit

        except Exception as e:
            print(f"   Error: {e}")
            break

    return all_opps


def main() -> None:
    print("=" * 70)
    print("NEXUS — ALL Sources Sought Miner (No Set-Aside Filter)")
    print("=" * 70)
    print()
    print("Notice type: Sources Sought (r) only")
    print("Set-aside filter: NONE (all set-asides)")
    print("Posted: Last 14 days")
    print()

    excluded_ids = extract_existing_solicitation_ids()
    print(f"Excluding {len(excluded_ids)} known opportunity IDs from BIDS:RESOURCES")
    print()

    print("Searching SAM.gov for Sources Sought...")
    raw = search_sam_gov_sources_sought(days_back=14)

    all_opportunities = []
    for opp in raw:
        notice_id = (opp.get("noticeId") or "").strip()
        sol_num = (opp.get("solicitationNumber") or "").strip()

        nid_upper = notice_id.upper() if notice_id else ""
        sol_upper = sol_num.upper() if sol_num else ""
        if nid_upper and nid_upper in excluded_ids:
            continue
        if sol_upper and sol_upper in excluded_ids:
            continue

        all_opportunities.append({
            "title": opp.get("title", "Untitled"),
            "agency": opp.get("fullParentPathName", "") or opp.get("department", "Unknown"),
            "notice_id": notice_id,
            "solicitation_number": sol_num,
            "set_aside": opp.get("typeOfSetAside", "") or opp.get("typeOfSetAsideDescription", "") or "—",
            "posted_date": opp.get("postedDate", ""),
            "response_deadline": opp.get("responseDeadLine", ""),
            "url": f"https://sam.gov/opp/{notice_id}/view" if notice_id else "",
        })

        if nid_upper:
            excluded_ids.add(nid_upper)
        if sol_upper:
            excluded_ids.add(sol_upper)

    # Deduplicate by notice_id
    seen = set()
    unique = []
    for opp in all_opportunities:
        nid = opp["notice_id"].upper()
        if nid and nid not in seen:
            seen.add(nid)
            unique.append(opp)

    print(f"Total Sources Sought found: {len(unique)}")
    print()

    # Sort by response deadline (soonest first), then by posted date
    def sort_key(o):
        rd = o.get("response_deadline") or ""
        pd = o.get("posted_date") or ""
        return (rd, pd)

    unique.sort(key=sort_key)

    # Write output
    now = datetime.now().strftime("%B %d, %Y")
    lines = [
        "# ALL Sources Sought — No Set-Aside Filter",
        "",
        f"**Generated by NEXUS** — {now}",
        "**Notice type:** Sources Sought only",
        "**Set-aside filter:** NONE (all set-asides: EDWOSB, WOSB, SB, 8a, HUBZone, SDVOSB, full & open, etc.)",
        "**Posted:** Last 14 days",
        "**Excluded:** Opportunities already in BIDS:RESOURCES",
        "",
        "---",
        "",
    ]

    if not unique:
        lines.extend([
            "No new Sources Sought found.",
            "",
            "All Sources Sought posted in the last 14 days are already tracked in BIDS:RESOURCES.",
            "",
        ])
    else:
        for i, opp in enumerate(unique, 1):
            block = [
                f"## {i}. {opp['title'][:120]}{'...' if len(opp['title']) > 120 else ''}",
                "",
                f"| Field | Value |",
                f"|-------|-------|",
                f"| **Title** | {opp['title']} |",
                f"| **Agency** | {opp['agency']} |",
                f"| **Notice ID** | {opp['notice_id']} |",
            ]
            if opp.get("solicitation_number"):
                block.append(f"| **Solicitation #** | {opp['solicitation_number']} |")
            block.extend([
                f"| **Set-Aside** | {opp['set_aside']} |",
                f"| **Posted** | {opp['posted_date']} |",
                f"| **Response Deadline** | {opp['response_deadline']} |",
                f"| **SAM.gov URL** | {opp['url']} |",
                "",
            ])
            lines.extend(block)

    OUTPUT_FILE.write_text("\n".join(lines), encoding="utf-8")
    print(f"Output written to: {OUTPUT_FILE}")
    print("=" * 70)


if __name__ == "__main__":
    main()
