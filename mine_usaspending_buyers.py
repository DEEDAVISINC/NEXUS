#!/usr/bin/env python3
"""
NEXUS — USAspending Buyer Miner

Finds agencies that BUY what DDI offers — by querying USAspending.gov
for contract awards in DDI's NAICS codes. Outputs awarding agencies
(the buyers), NOT COs. CO lookup is separate (SAM.gov, FPDS, agency sites).

DDI Services → NAICS codes → USAspending awards → Awarding agencies = BUYERS

Run: python3 mine_usaspending_buyers.py
Output: USASPENDING_BUYERS.md
"""

import json
import requests
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

# DDI is a contract management firm (prime/sub model) — 50+ NAICS codes.
# Source: nexus_opportunity_hunter_api.DDI_PROFILE — keep in sync.
DDI_NAICS_BY_SERVICE = {
    "Healthcare, Testing & Compliance": ["621511", "621999", "621910", "541620", "541380"],
    "Fingerprinting, Background & Security": ["561611", "561612"],
    "Professional & Legal": ["541199", "541990", "561110", "561492", "541930"],
    "Management Consulting": ["541611", "541614", "541618", "541690", "541612"],
    "Staffing": ["561320", "561311"],
    "IT & Technology": ["541512", "541519", "541511", "518210"],
    "Transportation, Courier & Logistics": ["485991", "485999", "492110", "492210", "488510", "484210"],
    "Facilities, Construction & Grounds": ["561720", "561730", "561210", "561790", "561990", "236220", "238990", "238160", "238330"],
    "Events & Security": ["561920", "561621"],
    "Medical & Industrial Products": ["423450", "339113", "339112", "424210", "423850", "423840", "424120", "424490"],
    "Environmental & Emergency": ["562910", "562119", "562112"],
    "Document & Records": ["561410"],
    "Market Research & Community Health": ["541910", "541720", "624190", "624230", "624221"],
}

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_FILE = BASE_DIR / "USASPENDING_BUYERS.md"


def query_usaspending(naics_codes: list, min_amount: int = 10000, limit: int = 100) -> list:
    """Query USAspending for contract awards in given NAICS codes."""
    url = "https://api.usaspending.gov/api/v2/search/spending_by_award/"

    payload = {
        "filters": {
            "naics_codes": {"require": naics_codes},
            "award_type_codes": ["A", "B", "C", "D"],
            "award_amounts": [{"lower_bound": min_amount}],
            "time_period": [
                {
                    "start_date": (datetime.now() - timedelta(days=365 * 2)).strftime("%Y-%m-%d"),
                    "end_date": datetime.now().strftime("%Y-%m-%d"),
                }
            ],
        },
        "fields": [
            "Award ID",
            "Award Amount",
            "Recipient Name",
            "Awarding Agency",
            "Awarding Sub Agency",
            "Description",
            "Start Date",
            "End Date",
        ],
        "limit": limit,
        "page": 1,
        "sort": "Award Amount",
        "order": "desc",
    }

    try:
        resp = requests.post(url, json=payload, timeout=60)
        if resp.status_code != 200:
            print(f"   API error {resp.status_code}: {resp.text[:200]}")
            return []
        data = resp.json()
        return data.get("results", [])
    except Exception as e:
        print(f"   Error: {e}")
        return []


def main():
    print("=" * 70)
    print("NEXUS — USAspending Buyer Miner")
    print("Finding agencies that BUY what DDI offers")
    print("=" * 70)
    print()

    # Aggregate: agency -> {service_lane -> [awards]}
    agency_data = defaultdict(lambda: defaultdict(list))

    for service, naics_list in DDI_NAICS_BY_SERVICE.items():
        print(f"Querying {service} (NAICS {', '.join(naics_list)})...")
        # Query each NAICS separately (API can be finicky with multi-NAICS)
        results = []
        for naics in naics_list:
            results.extend(query_usaspending([naics], min_amount=25000, limit=100))

        for r in results:
            agency = r.get("Awarding Agency") or "Unknown"
            sub = r.get("Awarding Sub Agency") or ""
            key = f"{agency}" if not sub else f"{agency} — {sub}"
            agency_data[key][service].append({
                "amount": r.get("Award Amount", 0),
                "recipient": r.get("Recipient Name", ""),
                "award_id": r.get("Award ID", ""),
                "description": (r.get("Description") or "")[:120],
            })

        print(f"   Found {len(results)} awards")
        print()

    # Build output
    lines = [
        "# USAspending — Agencies Buying What DDI Offers",
        "",
        f"**Generated:** {datetime.now().strftime('%B %d, %Y')}",
        "**Source:** USAspending.gov API (contract awards, last 2 years)",
        "**Filter:** DDI's 50+ NAICS codes (contract management firm), awards ≥ $25K",
        "",
        "**Next step:** Look up COs for these agencies via SAM.gov, FPDS, or agency procurement sites.",
        "",
        "---",
        "",
    ]

    # Sort agencies by total spend (across all services)
    agency_totals = {}
    for agency_key, by_service in agency_data.items():
        total = sum(
            sum(a["amount"] for a in awards)
            for awards in by_service.values()
        )
        agency_totals[agency_key] = total

    for agency_key in sorted(agency_totals.keys(), key=lambda k: agency_totals[k], reverse=True):
        by_service = agency_data[agency_key]
        total_spend = agency_totals[agency_key]

        lines.append(f"## {agency_key}")
        lines.append("")
        lines.append(f"**Total spend (DDI-relevant):** ${total_spend:,.0f}")
        lines.append("")

        for service, awards in by_service.items():
            service_total = sum(a["amount"] for a in awards)
            lines.append(f"### {service} — ${service_total:,.0f}")
            lines.append("")
            lines.append("| Amount | Recipient | Award ID |")
            lines.append("|--------|-----------|----------|")

            for a in sorted(awards, key=lambda x: x["amount"], reverse=True)[:10]:
                amt = a["amount"]
                rec = (a["recipient"] or "")[:40]
                aid = (a["award_id"] or "")[:20]
                lines.append(f"| ${amt:,.0f} | {rec} | {aid} |")

            if len(awards) > 10:
                lines.append(f"| ... | *+{len(awards) - 10} more* | |")
            lines.append("")

        lines.append("**CO lookup:** SAM.gov → Search opportunities by agency | FPDS → Award detail")
        lines.append("")
        lines.append("---")
        lines.append("")

    OUTPUT_FILE.write_text("\n".join(lines), encoding="utf-8")
    print(f"Output: {OUTPUT_FILE}")
    print("=" * 70)


if __name__ == "__main__":
    main()
