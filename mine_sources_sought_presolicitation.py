#!/usr/bin/env python3
"""
NEXUS — Sources Sought / Presolicitation / Special Notice / Intent to Sole Source Miner

Queries SAM.gov API for relationship-building notice types (NOT full solicitations):
  - r = Sources Sought
  - p = Presolicitation
  - s = Special Notice
  - i = Intent to Sole Source/Bundle

Filters: EDWOSB, WOSB, and Total Small Business (SBA) set-asides.
STRATEGY: Until 8(a) certified, search all DDI-eligible set-asides.
Posted: Last 14 days.
Excludes: Opportunities already in BIDS:RESOURCES.
RELEVANCE FILTER: Only returns opportunities matching DDI's actual service lanes.

DDI SERVICE LANES:
  1. Drug & Alcohol Testing (DOT/Non-DOT, occupational health screening)
  2. Biometric Fingerprinting & Background Checks (LiveScan / FD-258; channel per client — no DCSA SWFT claim)
  3. DNA / Genetic Testing (DePointe DNA — court-admissible)
  4. NEMT / Healthcare Transportation (NPI active, Uber Health partner)
  5. Freight Brokerage & Logistics (MC-1647572, DOT-4250594)
  5b. AOG courier — time-critical / aircraft-on-ground ground courier (Freight 1st Direct lane; not jet fuel)
  5c. JETA — jet fuel brokerage / into-plane supply (separate from AOG; combine only when solicitation is broker + delivery)
  6. Notary & Document Services (RON, mobile, apostille)
  7. Project Management & Consulting (ATLAS PM, federal contract execution)
  8. Staffing & Administrative Support (Michigan Personnel Agency License)
  9. Credentialing & Identity Verification (workforce compliance programs)

Run: python3 mine_sources_sought_presolicitation.py
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

from ddi_opportunity_fit import is_ddi_relevant

load_dotenv()

# Paths
BASE_DIR = Path(__file__).resolve().parent
BIDS_DIR = BASE_DIR / "BIDS:RESOURCES"
TODAY_STR = datetime.now().strftime("%b %d, %Y")
OUTPUT_FILE = BASE_DIR / f"NEW_SOURCES_SOUGHT_{datetime.now().strftime('%b%d').upper()}.md"

# DDI relevance: shared module `ddi_opportunity_fit` (keywords + NAICS + scoring)

# Notice types: relationship-building, NOT full solicitations
NOTICE_TYPES = [
    ("r", "Sources Sought"),
    ("p", "Presolicitation"),
    ("s", "Special Notice"),
    ("i", "Intent to Sole Source/Bundle"),
]

# EDWOSB / WOSB / Total SB set-aside filter values (until 8a certified, search all DDI-eligible)
ALLOWED_SET_ASIDES = [
    "EDWOSB",
    "WOSB",
    "Women-Owned Small Business",
    "Economically Disadvantaged Women-Owned Small Business",
    "SBA Certified EDWOSB",
    "SBA Certified WOSB",
    "SBA",  # Total Small Business Set-Aside (FAR 19.5)
    "Total Small Business",
]

# Known solicitation numbers to exclude (from user + BIDS:RESOURCES)
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

    # Federal solicitation ID pattern
    sol_pattern = re.compile(r"\b(W91[A-Z0-9]{8,15}|36C[A-Z0-9]{8,15}|N62[A-Z0-9]{8,15}|SPE7[A-Z0-9]{8,15}|70B[A-Z0-9]{8,15}|19[0-9]{9,})\b", re.I)

    # Scan folder names only (fast)
    for item in BIDS_DIR.iterdir():
        if item.is_dir():
            for match in sol_pattern.finditer(item.name):
                excluded.add(match.group(1).upper())

    return excluded


def is_edwosb_wosb(opp: Dict) -> bool:
    """Check if opportunity is EDWOSB or WOSB set-aside."""
    set_aside = str(opp.get("typeOfSetAside", "") or "").strip().upper()
    set_aside_desc = str(opp.get("typeOfSetAsideDescription", "") or "").strip().upper()

    for allowed in ALLOWED_SET_ASIDES:
        if allowed.upper() in set_aside or allowed.upper() in set_aside_desc:
            # Exclude SDVOSB, HUBZone, 8(a)
            if "SDVOSB" in set_aside or "SERVICE-DISABLED" in set_aside:
                return False
            if "HUBZONE" in set_aside:
                return False
            if "8(A)" in set_aside:
                return False
            return True
    return False


def search_sam_gov(notice_type: str, set_aside: str, days_back: int = 14) -> List[Dict]:
    """Search SAM.gov API for a single notice type and set-aside."""
    api_key = os.getenv("SAM_GOV_API_KEY", "DEMO_KEY")
    url = "https://api.sam.gov/opportunities/v2/search"

    params = {
        "api_key": api_key,
        "ptype": notice_type,
        "typeOfSetAside": set_aside,
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
            # Use curl (faster/more reliable than requests for SAM.gov)
            param_str = urlencode(params)
            cmd = ["curl", "-s", "-m", "20", f"{url}?{param_str}"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=25)
            if result.returncode != 0:
                print(f"   API error for ptype={notice_type} setAside={set_aside}")
                break

            data = json.loads(result.stdout) if result.stdout else {}
            opps = data.get("opportunitiesData", [])
            if not opps:
                break

            all_opps.extend(opps)

            # Pagination
            total = data.get("totalRecords", 0)
            if offset + len(opps) >= total or len(opps) < 100:
                break
            offset += 100
            time.sleep(1)  # Rate limit

        except Exception as e:
            print(f"   Error: {e}")
            break

    return all_opps


CO_OUTREACH_DIR = BASE_DIR / "BIDS:RESOURCES" / "FEDERAL CO OUTREACH PIPELINE" / "SEND_TO_BUYER"
CO_TRACKER_FILE = BASE_DIR / "BIDS:RESOURCES" / "FEDERAL CO OUTREACH PIPELINE" / "CO_OUTREACH_TRACKER.md"


def load_emailed_cos() -> Set[str]:
    """Load set of CO emails already tracked to avoid duplicates.
    
    Reads CO_OUTREACH_TRACKER.md and extracts the email column (index 3 in pipe-delimited rows).
    Also scans all columns for any email-looking string as a fallback.
    Handles messy tracker entries where status/notes are in the same cell as the email.
    """
    if not CO_TRACKER_FILE.exists():
        return set()
    content = CO_TRACKER_FILE.read_text(encoding="utf-8")
    emails = set()
    email_re = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")
    for line in content.splitlines():
        if "|" not in line:
            continue
        # Skip header rows
        if "CO Name" in line or "---" in line:
            continue
        parts = [p.strip() for p in line.split("|")]
        # Column index 3 is the email column per tracker format:
        # | CO Name | Agency | Email | Phone | Date Sent | Response | Sol# |
        if len(parts) >= 4:
            email_col = parts[3]
            found = email_re.findall(email_col)
            for e in found:
                emails.add(e.lower())
        # Fallback: scan all columns for any email address
        for part in parts:
            found = email_re.findall(part)
            for e in found:
                emails.add(e.lower())
    return emails


def generate_co_outreach_email(co: dict, opp: dict) -> str:
    """Generate a personalized capabilities outreach email for a CO."""
    first_name = (co.get("name") or "").split()[0] if co.get("name") else "there"
    agency_full = opp.get("agency", "your agency")
    agency_short = agency_full.split(".")[-1].strip() if "." in agency_full else agency_full
    set_aside = opp.get("set_aside", "WOSB")
    sa_label = "EDWOSB" if "EDWOSB" in set_aside.upper() else "WOSB"
    lane = opp.get("lane", "contract management and operational services")
    sol_num = opp.get("solicitation_number", "")
    sol_ref = f" (related to {sol_num})" if sol_num else ""

    email = f"""Subject: {sa_label} Introduction — Dee Davis Inc. | {lane}

Hi {first_name},

My name is Dieasha D. Davis, President & CEO of Dee Davis Inc. — a Michigan-based, federally certified Economically Disadvantaged Woman-Owned Small Business (EDWOSB).

I came across your procurement office at {agency_short}{sol_ref} and wanted to formally introduce Dee Davis Inc. and get on your radar for any upcoming WOSB or EDWOSB set-aside opportunities.

Dee Davis Inc. is a contract management firm that primes federal service contracts and coordinates delivery through vetted, qualified subcontractors and field partners. Our core service lanes include:

- Drug & Alcohol Testing (DOT/non-DOT, pre-employment, random, post-incident)
- Biometric Fingerprinting & Background Checks (LiveScan / FD-258; FBI/state channels per program)
- DNA & Genetic Testing (court-admissible, AABB-accredited network)
- Credentialing & Identity Verification (workforce compliance programs)
- NEMT & Healthcare Transportation (NPI active, Uber Health partner)
- Freight Brokerage & Logistics (MC-1647572 | US DOT-4250594)
- Project Management & Contract Execution Support
- Staffing & Administrative Support

We hold active EDWOSB, WOSB, WBENC, MBE, and SBE certifications, are SAM.gov registered (CAGE: 8UMX3 | UEI: HJB4KNYJVGZ1), and have an established subcontractor network across multiple states.

I'd love to be added to your interested vendors list and to receive notifications for any upcoming WOSB or EDWOSB set-aside opportunities. A full capability statement is available upon request.

Thank you for your time, {first_name} — I look forward to the possibility of supporting {agency_short}.

Warm regards,

Dieasha D. Davis
President & CEO
Dee Davis Inc.
755 W. Big Beaver Rd., Suite 2020 | Troy, MI 48084
(248) 376-4550 | info@deedavis.biz | deedavis.biz
CAGE: 8UMX3 | UEI: HJB4KNYJVGZ1 | SAM: Active
EDWOSB | WOSB | WBENC | MBE | SBE | E-Verify"""
    return email


def generate_co_outreach_batch(opportunities: list) -> None:
    """
    For every unique CO found in the opportunity list, generate a ready-to-send
    outreach email and save to FEDERAL CO OUTREACH PIPELINE/SEND_TO_BUYER/.
    Also update the CO tracker log.
    """
    CO_OUTREACH_DIR.mkdir(parents=True, exist_ok=True)

    already_emailed = load_emailed_cos()
    new_cos = []
    seen_this_run: Set[str] = set()

    for opp in opportunities:
        co = opp.get("co", {})
        email_addr = (co.get("email") or "").strip().lower()
        if not email_addr or not co.get("name"):
            continue
        if email_addr in already_emailed:
            continue
        if email_addr in seen_this_run:
            continue
        seen_this_run.add(email_addr)
        new_cos.append((co, opp))

    if not new_cos:
        print("CO Outreach: No new COs found (all previously contacted or no contact info).")
        return

    today_str = datetime.now().strftime("%b%d_%Y").upper()
    outreach_file = CO_OUTREACH_DIR / f"CO_OUTREACH_{today_str}.md"

    lines = [
        f"# Federal CO Capabilities Outreach — {datetime.now().strftime('%B %d, %Y')}",
        f"## Auto-generated by NEXUS Mine Script",
        f"## {len(new_cos)} new COs found — Copy each email below and send from info@deedavis.biz",
        "",
        "---",
        "",
    ]

    tracker_rows = []
    for idx, (co, opp) in enumerate(new_cos, 1):
        email_body = generate_co_outreach_email(co, opp)
        agency_short = opp.get("agency", "").split(".")[-1].strip() if "." in opp.get("agency", "") else opp.get("agency", "Unknown")
        lines.extend([
            f"## EMAIL {idx} — {co.get('name', 'Unknown')} | {agency_short}",
            f"**TO:** {co.get('email', '')}",
            f"**Phone:** {co.get('phone', 'N/A')}",
            f"**Related Opp:** {opp.get('title', '')[:80]}",
            f"**Solicitation:** {opp.get('solicitation_number', 'N/A')}",
            f"**Set-Aside:** {opp.get('set_aside', '')}",
            "",
            "```",
            email_body,
            "```",
            "",
            "---",
            "",
        ])
        tracker_rows.append(
            f"| {co.get('name','')} | {agency_short} | {co.get('email','')} | {co.get('phone','')} | {datetime.now().strftime('%Y-%m-%d')} | | {opp.get('solicitation_number','N/A')} |"
        )

    outreach_file.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nCO Outreach Emails: {outreach_file}")
    print(f"   → {len(new_cos)} new COs ready to contact")

    # Update tracker log
    if not CO_TRACKER_FILE.exists():
        header = [
            "# Federal CO Outreach Tracker",
            "## Every CO DDI has contacted — deduplicated across all NEXUS runs",
            "",
            "| CO Name | Agency | Email | Phone | Date Sent | Response | Sol# |",
            "|---|---|---|---|---|---|---|",
        ]
        CO_TRACKER_FILE.write_text("\n".join(header) + "\n", encoding="utf-8")

    with CO_TRACKER_FILE.open("a", encoding="utf-8") as f:
        for row in tracker_rows:
            f.write(row + "\n")

    print(f"   → Tracker updated: {CO_TRACKER_FILE.name}")


def get_notice_type_name(code: str) -> str:
    """Convert SAM.gov notice type code to readable name."""
    mapping = {
        "r": "Sources Sought",
        "p": "Presolicitation",
        "s": "Special Notice",
        "i": "Intent to Sole Source/Bundle",
        "o": "Solicitation",
        "k": "Combined Synopsis/Solicitation",
        "a": "Award",
    }
    return mapping.get(str(code).lower(), str(code))


def main() -> None:
    print("=" * 70)
    print("NEXUS — DDI Sources Sought / Presolicitation Miner (Relevance-Filtered)")
    print("=" * 70)
    print()
    print("Notice types: r (Sources Sought), p (Presolicitation), s (Special Notice), i (Intent to Sole Source)")
    print("Set-aside filter: EDWOSB, WOSB, SBA")
    print("Relevance filter: DDI service lanes only (drug testing, fingerprinting, DNA, NEMT, freight, notary, staffing, consulting)")
    print("Posted: Last 14 days")
    print()

    # Build exclusion set
    excluded_ids = extract_existing_solicitation_ids()
    print(f"Excluding {len(excluded_ids)} known opportunity IDs from BIDS:RESOURCES")
    print()

    all_raw = []
    skipped_irrelevant = 0

    for notice_code, notice_name in NOTICE_TYPES:
        for set_aside in ["EDWOSB", "WOSB", "SBA"]:
            try:
                print(f"Searching {notice_name} ({set_aside})...")
                raw = search_sam_gov(notice_code, set_aside, days_back=14)
                before = len(all_raw)

                for opp in raw:
                    notice_id = (opp.get("noticeId") or "").strip()
                    sol_num = (opp.get("solicitationNumber") or "").strip()
                    nid_upper = notice_id.upper() if notice_id else ""
                    sol_upper = sol_num.upper() if sol_num else ""

                    # Skip already-tracked opportunities
                    if nid_upper and nid_upper in excluded_ids:
                        continue
                    if sol_upper and sol_upper in excluded_ids:
                        continue

                    # ── DDI RELEVANCE FILTER ──
                    relevant, lane = is_ddi_relevant(opp)
                    if not relevant:
                        skipped_irrelevant += 1
                        continue

                    # Extract CO contact info
                    poc_list = opp.get("pointOfContact") or []
                    co_info = {}
                    if poc_list and isinstance(poc_list, list):
                        primary = next((p for p in poc_list if p.get("type") == "primary"), poc_list[0] if poc_list else {})
                        co_info = {
                            "name": primary.get("fullName", ""),
                            "email": primary.get("email", ""),
                            "phone": primary.get("phone", ""),
                        }

                    all_raw.append({
                        "title": opp.get("title", "Untitled"),
                        "agency": opp.get("fullParentPathName", "") or opp.get("department", "Unknown"),
                        "notice_id": notice_id,
                        "solicitation_number": sol_num,
                        "type": get_notice_type_name(opp.get("type", notice_code)),
                        "set_aside": opp.get("typeOfSetAside", "") or opp.get("typeOfSetAsideDescription", "") or set_aside,
                        "posted_date": opp.get("postedDate", ""),
                        "response_deadline": opp.get("responseDeadLine", ""),
                        "url": f"https://sam.gov/opp/{notice_id}/view" if notice_id else "",
                        "lane": lane,
                        "naics": str(opp.get("naicsCode") or ""),
                        "place_of_performance": (opp.get("placeOfPerformance") or {}).get("state", {}).get("name", "") if isinstance(opp.get("placeOfPerformance"), dict) else "",
                        "co": co_info,
                    })

                    if nid_upper:
                        excluded_ids.add(nid_upper)
                    if sol_upper:
                        excluded_ids.add(sol_upper)

                print(f"   Found {len(raw)}, {len(all_raw) - before} relevant")
            except Exception as e:
                print(f"   Error: {e}")
            time.sleep(1)

    # Deduplicate by notice_id
    seen = set()
    unique = []
    for opp in all_raw:
        nid = opp["notice_id"].upper()
        if nid and nid not in seen:
            seen.add(nid)
            unique.append(opp)

    # Sort by deadline (soonest first), then by set-aside priority (EDWOSB > WOSB > SBA)
    def sort_key(o):
        dl = o.get("response_deadline") or "9999"
        sa_priority = {"EDWOSB": 0, "WOSB": 1}.get(o.get("set_aside", "").upper(), 2)
        return (dl[:10], sa_priority)

    unique.sort(key=sort_key)

    # Group by lane
    by_lane: Dict[str, list] = {}
    for opp in unique:
        lane = opp["lane"].replace(" (desc)", "")
        by_lane.setdefault(lane, []).append(opp)

    print()
    print(f"Scanned: {skipped_irrelevant + len(unique)} | Irrelevant (filtered out): {skipped_irrelevant} | DDI-relevant: {len(unique)}")
    print()

    # Write output
    today = datetime.now().strftime("%B %d, %Y")
    lines = [
        f"# DDI Opportunity Intelligence — Sources Sought & Presolicitations",
        f"## {today}",
        "",
        "**Generated by NEXUS** — Filtered to DDI service lanes only",
        "**Set-asides:** EDWOSB / WOSB / Total Small Business",
        "**Notice types:** Sources Sought, Presolicitation, Special Notice, Intent to Sole Source",
        "**Posted:** Last 14 days | **Sorted:** Soonest deadline first",
        "",
        "---",
        "",
        "## DDI SERVICE LANES IN THIS REPORT",
        "",
    ]

    for lane, opps in sorted(by_lane.items()):
        lines.append(f"- **{lane}** — {len(opps)} opportunities")
    lines.extend(["", f"**Total:** {len(unique)} DDI-relevant opportunities ({skipped_irrelevant} irrelevant filtered out)", "", "---", ""])

    if not unique:
        lines.extend([
            "No DDI-relevant opportunities found in the last 14 days.",
            "Check back tomorrow — SAM.gov posts new notices daily.",
            "",
        ])
    else:
        counter = 1
        for lane, opps in sorted(by_lane.items()):
            lines.extend([f"## 🎯 {lane.upper()}", ""])
            for opp in opps:
                deadline_str = opp["response_deadline"][:10] if opp["response_deadline"] else "No deadline listed"
                sa = opp["set_aside"]
                sa_badge = "🔴 EDWOSB" if "EDWOSB" in sa.upper() else ("🟡 WOSB" if "WOSB" in sa.upper() else "🟢 SBA")
                state = f" | {opp['place_of_performance']}" if opp.get("place_of_performance") else ""

                block = [
                    f"### {counter}. {opp['title'][:120]}{'...' if len(opp['title']) > 120 else ''}",
                    "",
                    f"| Field | Value |",
                    f"|-------|-------|",
                    f"| **Set-Aside** | {sa_badge} {sa} |",
                    f"| **Type** | {opp['type']} |",
                    f"| **Agency** | {opp['agency'].split('.')[-1].strip() if '.' in opp['agency'] else opp['agency']} |",
                    f"| **Full Agency Path** | {opp['agency']} |",
                ]
                if opp.get("solicitation_number"):
                    block.append(f"| **Solicitation #** | {opp['solicitation_number']} |")
                if opp.get("naics"):
                    block.append(f"| **NAICS** | {opp['naics']} |")
                if opp.get("place_of_performance"):
                    block.append(f"| **State** | {opp['place_of_performance']} |")
                block.extend([
                    f"| **Posted** | {opp['posted_date'][:10] if opp['posted_date'] else 'Unknown'} |",
                    f"| **Response Deadline** | **{deadline_str}** |",
                    f"| **SAM.gov** | {opp['url']} |",
                    "",
                ])
                lines.extend(block)
                counter += 1

    OUTPUT_FILE.write_text("\n".join(lines), encoding="utf-8")
    print(f"Output: {OUTPUT_FILE}")

    # ── AUTO-GENERATE CO OUTREACH EMAILS ──────────────────────────────────────
    print()
    print("Generating CO outreach emails for all new COs found...")
    generate_co_outreach_batch(unique)
    print("=" * 70)


if __name__ == "__main__":
    main()
