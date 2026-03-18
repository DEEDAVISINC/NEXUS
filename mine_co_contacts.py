#!/usr/bin/env python3
"""
NEXUS — Contracting Officer Contact Miner

Queries SAM.gov for recent opportunities in DDI's NAICS codes,
extracts CO name/email/phone from pointOfContact, deduplicates,
and outputs a directory grouped by agency.

USAspending tells us WHO buys. This tells us WHO to call.

Uses parallel requests to handle SAM.gov's slow API.

Run: python3 mine_co_contacts.py
Output: CO_CONTACTS_BY_AGENCY.md
"""

import os
import time
import requests
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_FILE = BASE_DIR / "CO_CONTACTS_BY_AGENCY.md"

SAM_API_URL = "https://api.sam.gov/opportunities/v2/search"
MAX_WORKERS = 5

# DDI is a contract management firm — 50+ NAICS codes grouped into lanes
DDI_NAICS_LANES = {
    "Healthcare & Testing":         ["621511", "621999", "621910"],
    "Environmental & Lab Testing":  ["541620", "541380"],
    "Background & Security":        ["561611", "561612"],
    "Professional & Legal":         ["541199", "561110", "561492"],
    "Management Consulting":        ["541611", "541618", "541690"],
    "Staffing":                     ["561320", "561311"],
    "IT & Technology":              ["541512", "541519"],
    "Courier & Logistics":          ["492110", "492210", "488510"],
    "NEMT & Transit":               ["485991", "485999", "484210"],
    "Facilities & Grounds":         ["561720", "561730", "561210"],
    "Construction":                 ["236220", "238990"],
    "Medical & Industrial Products":["423450", "339112", "423840", "423850"],
    "Environmental & Emergency":    ["562910", "562119", "624230"],
    "Document & Records":           ["561410"],
    "Market Research":              ["541910", "541720"],
}

NAICS_LABELS = {
    "621511": "Medical Labs", "621999": "Ambulatory Health", "621910": "Ambulance",
    "541620": "Environmental Consulting", "541380": "Testing Labs",
    "561611": "Investigation/Background", "561612": "Security Guards",
    "541199": "Legal Services", "561110": "Office Admin", "561492": "Court Reporting/Notary",
    "541611": "Admin Mgmt Consulting", "541618": "Other Mgmt Consulting", "541690": "Sci/Tech Consulting",
    "561320": "Temp Staffing", "561311": "Employment Placement",
    "541512": "Computer Systems Design", "541519": "Other Computer Services",
    "492110": "Couriers", "492210": "Local Delivery", "488510": "Freight Arrangement",
    "485991": "Special Needs Transit", "485999": "Other Transit", "484210": "Long-Dist Trucking",
    "561720": "Janitorial", "561730": "Landscaping", "561210": "Facilities Support",
    "236220": "Commercial Construction", "238990": "Specialty Contractors",
    "423450": "Medical Equipment", "339112": "Surgical Supplies",
    "423840": "Industrial Supplies", "423850": "Service Equipment",
    "562910": "Remediation", "562119": "Other Waste", "624230": "Emergency Services",
    "561410": "Document Services", "541910": "Market Research", "541720": "R&D Social Sci",
}


def query_one_naics(naics: str, api_key: str, days_back: int = 90) -> dict:
    """Query SAM.gov for one NAICS code. Returns {naics, contacts, error}."""
    posted_from = (datetime.now() - timedelta(days=days_back)).strftime("%m/%d/%Y")
    posted_to = datetime.now().strftime("%m/%d/%Y")

    params = {
        "api_key": api_key,
        "naics": naics,
        "limit": 50,
        "postedFrom": posted_from,
        "postedTo": posted_to,
    }

    label = NAICS_LABELS.get(naics, naics)

    try:
        resp = requests.get(SAM_API_URL, params=params, timeout=120)
        if resp.status_code == 403:
            return {"naics": naics, "label": label, "contacts": [], "error": "AUTH"}
        if resp.status_code != 200:
            return {"naics": naics, "label": label, "contacts": [], "error": f"HTTP {resp.status_code}"}

        opps = resp.json().get("opportunitiesData", [])
    except requests.exceptions.Timeout:
        return {"naics": naics, "label": label, "contacts": [], "error": "TIMEOUT"}
    except Exception as e:
        return {"naics": naics, "label": label, "contacts": [], "error": str(e)[:60]}

    contacts = []
    for opp in opps:
        poc_list = opp.get("pointOfContact")
        if not poc_list or not isinstance(poc_list, list):
            continue

        for poc in poc_list:
            email = (poc.get("email") or "").strip()
            name = (poc.get("fullName") or "").strip()
            phone = (poc.get("phone") or "").strip()
            title = (poc.get("title") or "").strip()

            if not email and not phone:
                continue

            contacts.append({
                "name": name,
                "email": email.lower() if email else "",
                "phone": phone,
                "title": title,
                "agency": opp.get("department", "") or "",
                "sub_agency": opp.get("subtier", "") or "",
                "office": opp.get("office", "") or "",
                "naics": opp.get("naicsCode", "") or naics,
                "opportunity": (opp.get("title", "") or "")[:120],
                "solicitation": opp.get("solicitationNumber", "") or "",
                "set_aside": (opp.get("typeOfSetAsideDescription", "") or opp.get("typeOfSetAside", "") or ""),
                "posted": opp.get("postedDate", "") or "",
                "sam_url": f"https://sam.gov/opp/{opp.get('noticeId', '')}" if opp.get('noticeId') else "",
            })

    return {"naics": naics, "label": label, "contacts": contacts, "error": None}


def main():
    api_key = os.environ.get("SAM_GOV_API_KEY", "")
    if not api_key:
        print("ERROR: SAM_GOV_API_KEY not set.")
        return

    all_naics = []
    for codes in DDI_NAICS_LANES.values():
        all_naics.extend(codes)

    print("=" * 70)
    print("NEXUS — Contracting Officer Contact Miner")
    print(f"Querying SAM.gov for {len(all_naics)} NAICS codes ({MAX_WORKERS} parallel)")
    print("=" * 70)
    print()

    all_contacts = []
    completed = 0
    auth_failed = False

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {}
        for naics in all_naics:
            f = executor.submit(query_one_naics, naics, api_key, 90)
            futures[f] = naics

        for future in as_completed(futures):
            completed += 1
            result = future.result()
            naics = result["naics"]
            label = result["label"]

            if result["error"] == "AUTH":
                print(f"  AUTH FAILED — check SAM_GOV_API_KEY")
                auth_failed = True
                executor.shutdown(wait=False, cancel_futures=True)
                break
            elif result["error"]:
                print(f"  [{completed}/{len(all_naics)}] {naics} ({label}): {result['error']}")
            else:
                print(f"  [{completed}/{len(all_naics)}] {naics} ({label}): {len(result['contacts'])} contacts")
                all_contacts.extend(result["contacts"])

    if auth_failed:
        return

    print(f"\nRaw contacts collected: {len(all_contacts)}")

    # Deduplicate by email
    seen = {}
    for c in all_contacts:
        key = c["email"] or f"{c['name']}|{c['phone']}"
        if not key or key == "|":
            continue
        if key not in seen:
            seen[key] = c
        else:
            existing = seen[key]
            if not existing["name"] and c["name"]:
                existing["name"] = c["name"]
            if not existing["phone"] and c["phone"]:
                existing["phone"] = c["phone"]
            if not existing["title"] and c["title"]:
                existing["title"] = c["title"]

    unique = list(seen.values())
    print(f"Unique contacts: {len(unique)}")

    # Group by agency
    by_agency = defaultdict(list)
    for c in unique:
        by_agency[c["agency"] or "Unknown"].append(c)

    sorted_agencies = sorted(by_agency.keys(), key=lambda a: len(by_agency[a]), reverse=True)

    # Build output
    lines = [
        "# Contracting Officer Contacts — Agencies That Buy What DDI Sells",
        "",
        f"**Generated:** {datetime.now().strftime('%B %d, %Y')}",
        f"**Source:** SAM.gov API (opportunities posted in last 90 days)",
        f"**Coverage:** DDI's {len(all_naics)} NAICS codes across {len(DDI_NAICS_LANES)} service lanes",
        f"**Total Unique Contacts:** {len(unique)}",
        f"**Total Agencies:** {len(sorted_agencies)}",
        "",
        "**These are the people who post opportunities in DDI's lanes. Email them.**",
        "",
        "---",
        "",
        "## Quick Stats",
        "",
        "| Metric | Count |",
        "|--------|-------|",
        f"| Unique CO Contacts | {len(unique)} |",
        f"| Agencies Represented | {len(sorted_agencies)} |",
        f"| Contacts with Email | {sum(1 for c in unique if c['email'])} |",
        f"| Contacts with Phone | {sum(1 for c in unique if c['phone'])} |",
        "",
        "---",
        "",
    ]

    for agency in sorted_agencies:
        contacts = by_agency[agency]
        lines.append(f"## {agency}")
        lines.append("")

        by_office = defaultdict(list)
        for c in contacts:
            office_key = c.get("sub_agency") or c.get("office") or "General"
            by_office[office_key].append(c)

        for office, office_contacts in sorted(by_office.items()):
            if office != "General" and office != agency:
                lines.append(f"### {office}")
                lines.append("")

            lines.append("| Name | Email | Phone | Title | NAICS | Recent Opportunity |")
            lines.append("|------|-------|-------|-------|-------|-------------------|")

            for c in sorted(office_contacts, key=lambda x: x["name"]):
                name = c["name"] or "—"
                email = c["email"] or "—"
                phone = c["phone"] or "—"
                title_val = c["title"] or "—"
                naics_val = c["naics"] or "—"
                opp = c["opportunity"][:60] if c["opportunity"] else "—"
                lines.append(f"| {name} | {email} | {phone} | {title_val} | {naics_val} | {opp} |")

            lines.append("")

        lines.append("---")
        lines.append("")

    # Appendix A-Z
    lines.append("## Appendix: All Contacts A-Z")
    lines.append("")
    lines.append("| Name | Email | Phone | Agency | Sub-Agency |")
    lines.append("|------|-------|-------|--------|------------|")

    for c in sorted(unique, key=lambda x: (x["name"] or "zzz").lower()):
        name = c["name"] or "—"
        email = c["email"] or "—"
        phone = c["phone"] or "—"
        agency = c["agency"] or "—"
        sub = c["sub_agency"] or "—"
        lines.append(f"| {name} | {email} | {phone} | {agency} | {sub} |")

    lines.append("")
    lines.append("---")
    lines.append(f"*Generated {datetime.now().strftime('%B %d, %Y %I:%M %p')} by NEXUS CO Contact Miner*")

    OUTPUT_FILE.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nOutput: {OUTPUT_FILE}")
    print(f"Agencies: {len(sorted_agencies)}")
    print(f"Unique contacts: {len(unique)}")
    print("=" * 70)


if __name__ == "__main__":
    main()
