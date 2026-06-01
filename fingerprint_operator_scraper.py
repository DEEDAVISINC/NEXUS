"""
Fingerprint Operator Scraper — DDI+Lakota Network Recruitment Tool

Scrapes state-level livescan operator registries to build a database
of independent fingerprint operators for the DDI+Lakota nationwide
fingerprinting platform.

Usage:
    python fingerprint_operator_scraper.py --state FL
    python fingerprint_operator_scraper.py --state CA
    python fingerprint_operator_scraper.py --all-available
    python fingerprint_operator_scraper.py --search-google --state TX
"""

import requests
import json
import csv
import re
import os
import argparse
from datetime import datetime
from bs4 import BeautifulSoup
from urllib.parse import urljoin

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "FINGERPRINT_OPERATOR_RECRUITMENT", "scraped_data")
MASTER_DB = os.path.join(os.path.dirname(__file__), "FINGERPRINT_OPERATOR_RECRUITMENT", "operator_database.json")

EXCLUDE_COMPANIES = [
    "fieldprint", "identogo", "idemia", "certifix", "accurate biometrics",
    "morphotrust", "3m cogent", "nec", "crossmatch",
]

STATE_REGISTRIES = {
    "FL": {
        "name": "Florida",
        "authority": "FDLE",
        "url": "https://www.fdle.state.fl.us/criminal-history-records/documents/internetdoc_serviceproviders.aspx",
        "method": "scrape_html",
        "est_operators": 439,
    },
    "CA": {
        "name": "California",
        "authority": "CA DOJ",
        "url": "https://oag.ca.gov/fingerprints/locations",
        "method": "scrape_html",
        "est_operators": 500,
    },
    "IL": {
        "name": "Illinois",
        "authority": "IL State Police / IDFPR",
        "url": "https://isp.illinois.gov/BureauOfIdentification/BecomeVendor",
        "method": "contact_required",
        "phone": "(217) 785-2394",
        "est_operators": 100,
    },
    "AR": {
        "name": "Arkansas",
        "authority": "AR State Police AFIS",
        "url": None,
        "method": "contact_required",
        "phone": "(501) 618-8504",
        "est_operators": 50,
    },
    "NY": {
        "name": "New York",
        "authority": "NY DCJS",
        "url": None,
        "method": "contact_required",
        "phone": "(518) 457-6113",
        "est_operators": 200,
    },
    "TX": {
        "name": "Texas",
        "authority": "TX DPS",
        "url": None,
        "method": "contact_required",
        "phone": "(512) 424-2474",
        "est_operators": 300,
    },
    "PA": {
        "name": "Pennsylvania",
        "authority": "PA State Police",
        "url": None,
        "method": "contact_required",
        "phone": "(717) 783-5592",
        "est_operators": 150,
    },
    "OH": {
        "name": "Ohio",
        "authority": "OH BCI",
        "url": None,
        "method": "contact_required",
        "phone": "(740) 845-2000",
        "est_operators": 100,
    },
    "GA": {
        "name": "Georgia",
        "authority": "GA GCIC",
        "url": None,
        "method": "contact_required",
        "phone": "(404) 244-2601",
        "est_operators": 100,
    },
    "NC": {
        "name": "North Carolina",
        "authority": "NC SBI",
        "url": None,
        "method": "contact_required",
        "phone": "(919) 662-4500",
        "est_operators": 100,
    },
    "MI": {
        "name": "Michigan",
        "authority": "MI State Police",
        "url": None,
        "method": "contact_required",
        "phone": "(517) 241-1935",
        "est_operators": 75,
    },
    "VA": {
        "name": "Virginia",
        "authority": "VA State Police",
        "url": None,
        "method": "contact_required",
        "phone": "(804) 674-2000",
        "est_operators": 100,
    },
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
}


def load_master_db():
    if os.path.exists(MASTER_DB):
        with open(MASTER_DB, "r") as f:
            return json.load(f)
    return {"operators": [], "last_updated": None, "stats": {}}


def save_master_db(db):
    db["last_updated"] = datetime.now().isoformat()
    os.makedirs(os.path.dirname(MASTER_DB), exist_ok=True)
    with open(MASTER_DB, "w") as f:
        json.dump(db, f, indent=2)
    print(f"[+] Saved {len(db['operators'])} operators to {MASTER_DB}")


def is_excluded(name):
    name_lower = name.lower()
    return any(ex in name_lower for ex in EXCLUDE_COMPANIES)


def scrape_florida():
    """Scrape FDLE registered livescan submitters page."""
    print("[*] Scraping Florida FDLE operator list...")
    url = STATE_REGISTRIES["FL"]["url"]

    try:
        resp = requests.get(url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
    except Exception as e:
        print(f"[!] Failed to fetch FL page: {e}")
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    text = soup.get_text()

    operators = []
    lines = text.split("\n")

    current_op = {}
    for line in lines:
        line = line.strip()
        if not line:
            if current_op.get("name"):
                if not is_excluded(current_op["name"]):
                    current_op["state"] = "FL"
                    current_op["source"] = "FDLE Registry"
                    current_op["scraped_date"] = datetime.now().isoformat()
                    operators.append(current_op)
                current_op = {}
            continue

        if line.startswith("#") or (len(line) > 3 and not line.startswith("Phone") and not line.startswith("E-mail") and not line.startswith("Contact")):
            if "Phone" not in line and "E-mail" not in line and "Contact" not in line:
                if not current_op.get("name"):
                    cleaned = re.sub(r"^[#\s\d]*", "", line).strip()
                    if cleaned and len(cleaned) > 2:
                        current_op["name"] = cleaned

        phone_match = re.search(r"Phone.*?:\s*([\(\)\d\s\-\.]+)", line)
        if phone_match:
            current_op["phone"] = phone_match.group(1).strip()

        email_match = re.search(r"E-mail.*?:\s*(\S+@\S+)", line, re.IGNORECASE)
        if email_match:
            current_op["email"] = email_match.group(1).strip()

        contact_match = re.search(r"Contact.*?(?:Name|Person):\s*(.+)", line, re.IGNORECASE)
        if contact_match:
            current_op["contact_person"] = contact_match.group(1).strip()

        url_match = re.search(r"https?://\S+", line)
        if url_match:
            current_op["website"] = url_match.group(0).rstrip(")")

        if "Hard Card Scanning Capable" in line:
            current_op["hard_card_capable"] = True

        if "Mobile" in line or "mobile" in line:
            current_op["mobile_capable"] = True

    if current_op.get("name") and not is_excluded(current_op["name"]):
        current_op["state"] = "FL"
        current_op["source"] = "FDLE Registry"
        current_op["scraped_date"] = datetime.now().isoformat()
        operators.append(current_op)

    print(f"[+] Found {len(operators)} FL operators (excluding major networks)")
    return operators


def scrape_california():
    """Scrape CA DOJ livescan locations page."""
    print("[*] Scraping California DOJ operator list...")
    url = STATE_REGISTRIES["CA"]["url"]

    try:
        resp = requests.get(url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
    except Exception as e:
        print(f"[!] Failed to fetch CA page: {e}")
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    text = soup.get_text()

    operators = []
    lines = text.split("\n")

    for line in lines:
        line = line.strip()
        if not line or len(line) < 5:
            continue

        if any(keyword in line.lower() for keyword in ["mobile notary", "live scan", "livescan", "fingerprint"]):
            if not is_excluded(line):
                op = {
                    "name": line.strip(),
                    "state": "CA",
                    "source": "CA DOJ Live Scan Locations",
                    "scraped_date": datetime.now().isoformat(),
                }
                if "mobile" in line.lower():
                    op["mobile_capable"] = True
                if "notary" in line.lower():
                    op["also_notary"] = True
                operators.append(op)

    seen = set()
    unique_ops = []
    for op in operators:
        if op["name"] not in seen:
            seen.add(op["name"])
            unique_ops.append(op)

    print(f"[+] Found {len(unique_ops)} CA operators (excluding major networks)")
    return unique_ops


def search_google_maps(state_name, metro_areas=None):
    """
    Generate Google Maps search URLs for manual operator discovery.
    (Automated Google scraping violates ToS — this generates the search links.)
    """
    if metro_areas is None:
        metro_areas = [state_name]

    searches = []
    for area in metro_areas:
        searches.append({
            "area": area,
            "search_url": f"https://www.google.com/maps/search/independent+livescan+fingerprinting+{area.replace(' ', '+')}",
            "alt_search": f"https://www.google.com/maps/search/mobile+fingerprinting+{area.replace(' ', '+')}",
        })

    return searches


METRO_AREAS = {
    "TX": ["Houston TX", "Dallas TX", "San Antonio TX", "Austin TX", "Fort Worth TX", "El Paso TX"],
    "NY": ["New York City", "Buffalo NY", "Rochester NY", "Albany NY", "Syracuse NY"],
    "PA": ["Philadelphia PA", "Pittsburgh PA", "Allentown PA", "Erie PA", "Harrisburg PA"],
    "OH": ["Columbus OH", "Cleveland OH", "Cincinnati OH", "Toledo OH", "Akron OH"],
    "GA": ["Atlanta GA", "Augusta GA", "Savannah GA", "Columbus GA", "Macon GA"],
    "NC": ["Charlotte NC", "Raleigh NC", "Greensboro NC", "Durham NC", "Fayetteville NC"],
    "MI": ["Detroit MI", "Grand Rapids MI", "Warren MI", "Lansing MI", "Ann Arbor MI"],
    "VA": ["Virginia Beach VA", "Norfolk VA", "Richmond VA", "Arlington VA", "Alexandria VA"],
    "IL": ["Chicago IL", "Aurora IL", "Naperville IL", "Joliet IL", "Rockford IL"],
    "FL": ["Miami FL", "Orlando FL", "Tampa FL", "Jacksonville FL", "Fort Lauderdale FL"],
    "CA": ["Los Angeles CA", "San Francisco CA", "San Diego CA", "Sacramento CA", "San Jose CA"],
}


def generate_state_report(state_code):
    """Generate a recruitment action report for a specific state."""
    reg = STATE_REGISTRIES.get(state_code)
    if not reg:
        print(f"[!] No registry info for {state_code}")
        return

    report = f"""
# {reg['name']} ({state_code}) — Operator Recruitment Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Registry Authority: {reg['authority']}
## Method: {reg['method']}
## Estimated Operators: {reg['est_operators']}
"""

    if reg["method"] == "scrape_html" and reg.get("url"):
        report += f"\n## Public Registry URL\n{reg['url']}\n\nThis state has a scrapeable public registry. Run the scraper to pull operator data.\n"
    elif reg["method"] == "contact_required":
        report += f"\n## Contact Required\nPhone: {reg.get('phone', 'Unknown')}\n\nThis state requires a phone call or email to request the operator list.\n"

    metros = METRO_AREAS.get(state_code, [f"{reg['name']}"])
    searches = search_google_maps(reg["name"], metros)

    report += "\n## Google Maps Search Links (Manual Discovery)\n"
    for s in searches:
        report += f"\n### {s['area']}\n- Livescan: {s['search_url']}\n- Mobile: {s['alt_search']}\n"

    report_path = os.path.join(OUTPUT_DIR, f"{state_code}_recruitment_report.md")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(report_path, "w") as f:
        f.write(report)

    print(f"[+] Report saved to {report_path}")
    return report


def export_csv():
    """Export master database to CSV for spreadsheet use."""
    db = load_master_db()
    if not db["operators"]:
        print("[!] No operators in database")
        return

    csv_path = os.path.join(OUTPUT_DIR, "operator_database.csv")
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)

    fieldnames = ["name", "state", "contact_person", "phone", "email", "website",
                  "mobile_capable", "hard_card_capable", "also_notary", "source",
                  "status", "scraped_date"]

    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for op in db["operators"]:
            writer.writerow(op)

    print(f"[+] Exported {len(db['operators'])} operators to {csv_path}")


def run_stats(db):
    """Calculate coverage statistics."""
    states = {}
    for op in db["operators"]:
        st = op.get("state", "Unknown")
        states[st] = states.get(st, 0) + 1

    db["stats"] = {
        "total_operators": len(db["operators"]),
        "states_covered": len(states),
        "operators_by_state": dict(sorted(states.items())),
        "coverage_pct": round(len(states) / 53 * 100, 1),
    }

    print(f"\n--- COVERAGE STATS ---")
    print(f"Total Operators: {db['stats']['total_operators']}")
    print(f"States Covered: {db['stats']['states_covered']} / 53 ({db['stats']['coverage_pct']}%)")
    print(f"\nBy State:")
    for st, count in db["stats"]["operators_by_state"].items():
        print(f"  {st}: {count}")
    print("---\n")


def main():
    parser = argparse.ArgumentParser(description="DDI Fingerprint Operator Scraper")
    parser.add_argument("--state", type=str, help="State code to scrape (e.g., FL, CA)")
    parser.add_argument("--all-available", action="store_true", help="Scrape all states with public registries")
    parser.add_argument("--search-google", action="store_true", help="Generate Google Maps search links for a state")
    parser.add_argument("--report", type=str, help="Generate recruitment report for a state")
    parser.add_argument("--export-csv", action="store_true", help="Export database to CSV")
    parser.add_argument("--stats", action="store_true", help="Show coverage statistics")
    args = parser.parse_args()

    db = load_master_db()

    if args.export_csv:
        export_csv()
        return

    if args.stats:
        run_stats(db)
        return

    if args.report:
        generate_state_report(args.report.upper())
        return

    if args.search_google and args.state:
        state = args.state.upper()
        reg = STATE_REGISTRIES.get(state)
        state_name = reg["name"] if reg else state
        metros = METRO_AREAS.get(state, [state_name])
        searches = search_google_maps(state_name, metros)
        print(f"\nGoogle Maps Search Links for {state_name}:")
        for s in searches:
            print(f"\n  {s['area']}:")
            print(f"    Livescan: {s['search_url']}")
            print(f"    Mobile:   {s['alt_search']}")
        return

    if args.state:
        state = args.state.upper()
        if state == "FL":
            operators = scrape_florida()
        elif state == "CA":
            operators = scrape_california()
        else:
            reg = STATE_REGISTRIES.get(state)
            if reg and reg["method"] == "contact_required":
                print(f"\n[!] {reg['name']} requires direct contact to obtain operator list.")
                print(f"    Authority: {reg['authority']}")
                print(f"    Phone: {reg.get('phone', 'Unknown')}")
                print(f"\n    Action: Call them and request the list of certified livescan operators.")
                generate_state_report(state)
                return
            else:
                print(f"[!] No scraper available for {state}. Use --search-google --state {state} for manual discovery.")
                generate_state_report(state)
                return

        existing_names = {op["name"] for op in db["operators"]}
        new_ops = [op for op in operators if op["name"] not in existing_names]
        db["operators"].extend(new_ops)
        print(f"[+] Added {len(new_ops)} new operators ({len(operators) - len(new_ops)} duplicates skipped)")

        run_stats(db)
        save_master_db(db)

    elif args.all_available:
        for state_code, reg in STATE_REGISTRIES.items():
            if reg["method"] == "scrape_html":
                print(f"\n{'='*50}")
                if state_code == "FL":
                    operators = scrape_florida()
                elif state_code == "CA":
                    operators = scrape_california()
                else:
                    continue

                existing_names = {op["name"] for op in db["operators"]}
                new_ops = [op for op in operators if op["name"] not in existing_names]
                db["operators"].extend(new_ops)
                print(f"[+] Added {len(new_ops)} new operators from {reg['name']}")

        run_stats(db)
        save_master_db(db)

    else:
        parser.print_help()
        print("\n\nAvailable states with registries:")
        for code, reg in STATE_REGISTRIES.items():
            method_label = "SCRAPEABLE" if reg["method"] == "scrape_html" else "CALL REQUIRED"
            print(f"  {code} — {reg['name']} ({reg['authority']}) [{method_label}] ~{reg['est_operators']} operators")


if __name__ == "__main__":
    main()
