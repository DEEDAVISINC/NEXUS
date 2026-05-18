#!/usr/bin/env python3
"""
NEXUS — Public Procurement Portal Scanner
Scans all verified public solicitation portals for opportunities DDI can bid on.
NO LOGIN REQUIRED — these are all publicly accessible.

Portals scanned:
  TIER 1 (Daily — High Volume):
    1. SAM.gov API — WOSB/EDWOSB set-asides
    2. BidNet Direct — 30,000+ nationwide public solicitations
    3. Texas ESBD — No login required
    4. New York NYSCR — 989+ opportunities
    5. Pennsylvania eMarketplace — Full public list
    6. Virginia eVA/VBO — Full public list
    7. South Carolina SCBO — Categorized ads

  TIER 2 (2-3x/week):
    8. Louisiana LaPAC
    9. Georgia GPR
    10. Indiana Business Opportunities
    11. Connecticut CTsource
    12. Delaware MyMarketplace
    13. DC OCP
    14. Alaska Online Public Notices
    15. Utah U3P
    16. MarylandBids.com — State and county opportunities

Run: python3 public_portal_scanner.py
     python3 public_portal_scanner.py --tier1    # Only high-volume sources
     python3 public_portal_scanner.py --report   # Generate report from cached data
"""

import os
import sys
import json
import re
import logging
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

# Logging
LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, "portal_scanner.log")),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger("portal_scanner")

# Output files
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_FILE = os.path.join(BASE_DIR, "portal_scan_results.json")
REPORT_FILE = os.path.join(BASE_DIR, "DAILY_OPPORTUNITIES_REPORT.md")

# DDI capability keywords for filtering
DDI_KEYWORDS = [
    # Facility Services
    "janitorial", "custodial", "cleaning", "landscaping", "grounds maintenance",
    "lawn", "mowing", "pest control", "hvac", "facility maintenance",
    "building maintenance", "pressure wash",
    # Construction & Trades
    "electrical", "plumbing", "concrete", "roofing", "painting", "fencing",
    "demolition", "renovation", "repair", "construction", "carpentry",
    "welding", "flooring",
    # Transportation & Logistics
    "transportation", "freight", "courier", "delivery", "fleet",
    "vehicle", "truck", "motor coach", "nemt", "ambulance",
    # AOG courier (not fuel) vs JETA jet fuel — both scanned; triage by title
    "aog", "aircraft on ground", "aviation courier",
    "jet fuel", "aviation fuel", "turbine fuel", "into-plane", "into plane",
    "jp-8", "fixed base operator", "airport fuel",
    # NEMT — Underserved Areas (nationwide)
    "medical transportation", "patient transport", "non-emergency medical",
    "paratransit", "demand response", "dial-a-ride",
    "veteran home", "veterans home", "state veteran",
    "corrections transport", "prisoner transport", "inmate transport",
    "doc transport", "detainee transport", "jail medical",
    "community mental health", "cmh transport", "behavioral health transport",
    "area agency on aging", "senior transport", "elderly transport",
    "tribal health", "tribal transport", "indian health service",
    "rural health", "rural transportation", "critical access hospital",
    "hcbs transport", "waiver transport", "developmental disabilities",
    "medically underserved", "health shortage",
    # Professional Services
    "staffing", "temporary", "administrative", "consulting", "management",
    "data entry", "front desk", "clerical", "it services", "training",
    "professional services",
    # Products & Equipment
    "supplies", "equipment", "tools", "safety", "ppe", "medical",
    "industrial", "office supplies", "furniture", "generator",
    "container", "modular", "parts", "cable", "valve", "pump",
    # Emergency
    "emergency", "disaster", "rapid", "temporary facility",
    # Drug Testing & Compliance
    "drug testing", "drug screen", "alcohol testing", "dot testing",
    "background check", "fingerprint", "livescan",
    # DNA & Lab
    "dna testing", "paternity", "specimen transport", "lab courier",
    # Notary
    "notary", "document services", "mobile notary",
]

# Exclude keywords (things DDI definitely doesn't do)
EXCLUDE_KEYWORDS = [
    "software development", "web development", "it consulting",
    "legal services", "accounting", "audit", "architecture",
    "engineering design", "surveying", "laboratory",
    "food service", "catering",
]

MIN_DAYS_TO_BID = 5  # Minimum days remaining before deadline


def is_relevant_opportunity(title: str, description: str = "") -> bool:
    """Check if an opportunity matches DDI's capabilities."""
    text = f"{title} {description}".lower()

    # Check exclusions first
    for kw in EXCLUDE_KEYWORDS:
        if kw in text:
            return False

    # Check for matching keywords
    for kw in DDI_KEYWORDS:
        if kw in text:
            return True

    return False


def has_enough_time(deadline_str: str) -> bool:
    """Check if there are at least MIN_DAYS_TO_BID days before deadline."""
    if not deadline_str:
        return True  # No deadline listed = assume ok

    try:
        # Try common date formats
        for fmt in ["%m/%d/%Y", "%Y-%m-%d", "%B %d, %Y", "%b %d, %Y",
                    "%m-%d-%Y", "%m/%d/%y", "%Y-%m-%dT%H:%M:%S"]:
            try:
                deadline = datetime.strptime(deadline_str.strip()[:10], fmt)
                days_left = (deadline - datetime.now()).days
                return days_left >= MIN_DAYS_TO_BID
            except ValueError:
                continue
    except Exception:
        pass

    return True  # Can't parse = don't filter out


# ============================================================================
# PORTAL SCANNERS
# ============================================================================

def scan_sam_gov() -> List[Dict]:
    """Scan SAM.gov API for WOSB/EDWOSB set-aside opportunities."""
    log.info("Scanning SAM.gov for WOSB/EDWOSB opportunities...")
    opportunities = []

    api_key = os.getenv("SAM_GOV_API_KEY", "DEMO_KEY")

    # Search for WOSB set-asides posted in last 14 days
    params = {
        "api_key": api_key,
        "postedFrom": (datetime.now() - timedelta(days=14)).strftime("%m/%d/%Y"),
        "postedTo": datetime.now().strftime("%m/%d/%Y"),
        "ptype": "o,p,k",  # Solicitations, presolicitations, combined
        "limit": 100,
        "offset": 0,
    }

    # Scan for WOSB set-asides
    for set_aside in ["WOSB", "EDWOSB"]:
        params["typeOfSetAside"] = set_aside
        try:
            url = "https://api.sam.gov/opportunities/v2/search"
            resp = requests.get(url, params=params, timeout=30)
            if resp.status_code == 200:
                data = resp.json()
                for opp in data.get("opportunitiesData", []):
                    title = opp.get("title", "")
                    desc = opp.get("description", "")
                    deadline = opp.get("responseDeadLine", "")

                    if is_relevant_opportunity(title, desc) and has_enough_time(deadline):
                        opportunities.append({
                            "source": "SAM.gov",
                            "title": title,
                            "agency": opp.get("fullParentPathName", ""),
                            "deadline": deadline,
                            "set_aside": set_aside,
                            "url": f"https://sam.gov/opp/{opp.get('noticeId', '')}/view",
                            "type": opp.get("type", ""),
                            "posted": opp.get("postedDate", ""),
                            "naics": opp.get("naicsCode", ""),
                        })
                log.info(f"SAM.gov {set_aside}: found {len(data.get('opportunitiesData', []))} total, "
                         f"{len(opportunities)} relevant")
            else:
                log.warning(f"SAM.gov API returned {resp.status_code}")
        except Exception as e:
            log.error(f"SAM.gov {set_aside} scan failed: {e}")

    return opportunities


def scan_bidnet_direct() -> List[Dict]:
    """Scan BidNet Direct public solicitations page."""
    log.info("Scanning BidNet Direct (nationwide)...")
    opportunities = []

    # BidNet has public open solicitations page
    # We scan by DDI-relevant keywords
    search_terms = [
        "janitorial", "landscaping", "maintenance", "supplies",
        "transportation", "cleaning", "construction", "staffing",
        "equipment", "vehicle", "electrical", "plumbing",
    ]

    for term in search_terms:
        try:
            url = f"https://www.bidnetdirect.com/solicitations/open-bids?SearchTitle={term}"
            headers = {"User-Agent": "Mozilla/5.0"}
            resp = requests.get(url, headers=headers, timeout=20)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, "html.parser")
                # BidNet uses dynamic loading but basic results are in HTML
                for item in soup.select("a[href*='/solicitations/open-bids/']"):
                    title = item.get_text(strip=True)
                    href = item.get("href", "")

                    if title and is_relevant_opportunity(title):
                        # Try to find closing date nearby
                        parent = item.find_parent("div") or item.find_parent("tr")
                        deadline = ""
                        if parent:
                            date_el = parent.find(string=re.compile(r"Closing"))
                            if date_el:
                                deadline = date_el.strip()

                        if has_enough_time(deadline):
                            full_url = f"https://www.bidnetdirect.com{href}" if href.startswith("/") else href
                            opportunities.append({
                                "source": "BidNet Direct",
                                "title": title,
                                "agency": "",
                                "deadline": deadline,
                                "set_aside": "",
                                "url": full_url,
                                "type": "Solicitation",
                                "posted": "",
                                "search_term": term,
                            })

            # Be respectful
            import time
            time.sleep(1)

        except Exception as e:
            log.warning(f"BidNet search '{term}' failed: {e}")

    # Deduplicate by URL
    seen_urls = set()
    unique = []
    for opp in opportunities:
        if opp["url"] not in seen_urls:
            seen_urls.add(opp["url"])
            unique.append(opp)

    log.info(f"BidNet Direct: found {len(unique)} relevant opportunities")
    return unique


def scan_mitn() -> List[Dict]:
    """Scan MITN (Michigan) public solicitations."""
    log.info("Scanning MITN (Michigan)...")
    opportunities = []

    try:
        url = "https://www.bidnetdirect.com/mitn/solicitations/open-bids"
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(url, headers=headers, timeout=20)

        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")
            for item in soup.select("a[href*='/solicitations/open-bids/']"):
                title = item.get_text(strip=True)
                href = item.get("href", "")

                if title and len(title) > 5 and is_relevant_opportunity(title):
                    full_url = f"https://www.bidnetdirect.com{href}" if href.startswith("/") else href
                    opportunities.append({
                        "source": "MITN (Michigan)",
                        "title": title,
                        "agency": "Michigan Local Government",
                        "deadline": "",
                        "set_aside": "",
                        "url": full_url,
                        "type": "Solicitation",
                        "posted": "",
                    })

        log.info(f"MITN: found {len(opportunities)} relevant opportunities")
    except Exception as e:
        log.error(f"MITN scan failed: {e}")

    return opportunities


def scan_texas_esbd() -> List[Dict]:
    """Scan Texas ESBD — no login required."""
    log.info("Scanning Texas ESBD...")
    opportunities = []

    try:
        url = "https://www.txsmartbuy.com/esbd"
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(url, headers=headers, timeout=20)

        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")
            # ESBD lists solicitations in table rows
            for row in soup.select("table tr, .solicitation-item, a[href*='esbd']"):
                text = row.get_text(strip=True)
                if text and is_relevant_opportunity(text):
                    href = ""
                    link = row.find("a", href=True)
                    if link:
                        href = link["href"]
                        if not href.startswith("http"):
                            href = f"https://www.txsmartbuy.com{href}"

                    opportunities.append({
                        "source": "Texas ESBD",
                        "title": text[:200],
                        "agency": "State of Texas",
                        "deadline": "",
                        "set_aside": "",
                        "url": href,
                        "type": "Solicitation",
                        "posted": "",
                    })

        log.info(f"Texas ESBD: found {len(opportunities)} relevant opportunities")
    except Exception as e:
        log.error(f"Texas ESBD scan failed: {e}")

    return opportunities


def scan_south_carolina_scbo() -> List[Dict]:
    """Scan South Carolina Business Opportunities."""
    log.info("Scanning South Carolina SCBO...")
    opportunities = []

    try:
        url = "https://scbo.sc.gov/"
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(url, headers=headers, timeout=20)

        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")
            for link in soup.find_all("a", href=True):
                text = link.get_text(strip=True)
                if text and is_relevant_opportunity(text):
                    href = link["href"]
                    if not href.startswith("http"):
                        href = f"https://scbo.sc.gov{href}"
                    opportunities.append({
                        "source": "SC SCBO",
                        "title": text[:200],
                        "agency": "State of South Carolina",
                        "deadline": "",
                        "url": href,
                        "type": "Solicitation",
                        "posted": "",
                    })

        log.info(f"SC SCBO: found {len(opportunities)} relevant opportunities")
    except Exception as e:
        log.error(f"SC SCBO scan failed: {e}")

    return opportunities


def scan_virginia_eva() -> List[Dict]:
    """Scan Virginia eVA public opportunities."""
    log.info("Scanning Virginia eVA...")
    opportunities = []

    try:
        url = "https://eva.virginia.gov/pages/eva-public-solicitations.htm"
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(url, headers=headers, timeout=20)

        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")
            for link in soup.find_all("a", href=True):
                text = link.get_text(strip=True)
                if text and is_relevant_opportunity(text):
                    href = link["href"]
                    if not href.startswith("http"):
                        href = f"https://eva.virginia.gov{href}"
                    opportunities.append({
                        "source": "Virginia eVA",
                        "title": text[:200],
                        "agency": "Commonwealth of Virginia",
                        "deadline": "",
                        "url": href,
                        "type": "Solicitation",
                        "posted": "",
                    })

        log.info(f"Virginia eVA: found {len(opportunities)} relevant opportunities")
    except Exception as e:
        log.error(f"Virginia eVA scan failed: {e}")

    return opportunities


def scan_indiana() -> List[Dict]:
    """Scan Indiana Business Opportunities."""
    log.info("Scanning Indiana procurement...")
    opportunities = []

    try:
        url = "https://www.in.gov/idoa/procurement/current-business-opportunities/"
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(url, headers=headers, timeout=20)

        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")
            for row in soup.select("table tr"):
                text = row.get_text(strip=True)
                if text and is_relevant_opportunity(text):
                    link = row.find("a", href=True)
                    href = link["href"] if link else ""
                    if href and not href.startswith("http"):
                        href = f"https://www.in.gov{href}"
                    opportunities.append({
                        "source": "Indiana",
                        "title": text[:200],
                        "agency": "State of Indiana",
                        "deadline": "",
                        "url": href,
                        "type": "Solicitation",
                        "posted": "",
                    })

        log.info(f"Indiana: found {len(opportunities)} relevant opportunities")
    except Exception as e:
        log.error(f"Indiana scan failed: {e}")

    return opportunities


def scan_louisiana_lapac() -> List[Dict]:
    """Scan Louisiana LaPAC public bids."""
    log.info("Scanning Louisiana LaPAC...")
    opportunities = []

    try:
        url = "https://wwwcfprd.doa.louisiana.gov/OSP/LaPAC/pubMain.cfm"
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(url, headers=headers, timeout=20)

        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")
            for link in soup.find_all("a", href=True):
                text = link.get_text(strip=True)
                if text and is_relevant_opportunity(text):
                    href = link["href"]
                    if not href.startswith("http"):
                        href = f"https://wwwcfprd.doa.louisiana.gov{href}"
                    opportunities.append({
                        "source": "Louisiana LaPAC",
                        "title": text[:200],
                        "agency": "State of Louisiana",
                        "deadline": "",
                        "url": href,
                        "type": "Solicitation",
                        "posted": "",
                    })

        log.info(f"Louisiana LaPAC: found {len(opportunities)} relevant opportunities")
    except Exception as e:
        log.error(f"Louisiana LaPAC scan failed: {e}")

    return opportunities


def scan_connecticut() -> List[Dict]:
    """Scan Connecticut CTsource — registration NOT required to view."""
    log.info("Scanning Connecticut CTsource...")
    opportunities = []

    try:
        url = "https://portal.ct.gov/DAS/CTSource/BidBoard"
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(url, headers=headers, timeout=20)

        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")
            for link in soup.find_all("a", href=True):
                text = link.get_text(strip=True)
                if text and is_relevant_opportunity(text):
                    href = link["href"]
                    if not href.startswith("http"):
                        href = f"https://portal.ct.gov{href}"
                    opportunities.append({
                        "source": "Connecticut CTsource",
                        "title": text[:200],
                        "agency": "State of Connecticut",
                        "deadline": "",
                        "url": href,
                        "type": "Solicitation",
                        "posted": "",
                    })

        log.info(f"Connecticut: found {len(opportunities)} relevant opportunities")
    except Exception as e:
        log.error(f"Connecticut scan failed: {e}")

    return opportunities


# ============================================================================
# REPORT GENERATION
# ============================================================================

def generate_report(all_opportunities: List[Dict]) -> str:
    """Generate a markdown report of found opportunities."""
    now = datetime.now().strftime("%B %d, %Y at %I:%M %p")

    report = f"""# DAILY OPPORTUNITY REPORT — {now}
## Generated by NEXUS Public Portal Scanner

**Total Opportunities Found:** {len(all_opportunities)}
**Minimum Days to Bid:** {MIN_DAYS_TO_BID}+
**Filtered for DDI capabilities only**

---

"""
    # Group by source
    by_source = {}
    for opp in all_opportunities:
        source = opp.get("source", "Unknown")
        if source not in by_source:
            by_source[source] = []
        by_source[source].append(opp)

    for source, opps in sorted(by_source.items()):
        report += f"## {source} ({len(opps)} opportunities)\n\n"
        for i, opp in enumerate(opps, 1):
            title = opp.get("title", "Untitled")
            agency = opp.get("agency", "")
            deadline = opp.get("deadline", "Not specified")
            url = opp.get("url", "")
            set_aside = opp.get("set_aside", "")

            report += f"### {i}. {title}\n"
            if agency:
                report += f"- **Agency:** {agency}\n"
            if deadline:
                report += f"- **Deadline:** {deadline}\n"
            if set_aside:
                report += f"- **Set-Aside:** {set_aside}\n"
            if url:
                report += f"- **Link:** {url}\n"
            report += "\n"

        report += "---\n\n"

    report += """## ACTION REQUIRED

Review the opportunities above and mark which ones to pursue.
For each "YES" opportunity, create a bid folder using the standard workflow.

---

*Generated by NEXUS Public Portal Scanner*
*Portals checked: SAM.gov, BidNet Direct, MITN, Texas ESBD, Virginia eVA, South Carolina SCBO, Indiana, Louisiana, Connecticut, MarylandBids.com*
"""
    return report


# ============================================================================
# MARYLAND BIDS
# ============================================================================

def scan_maryland_bids() -> List[Dict]:
    """Scan MarylandBids.com for state/county opportunities."""
    log.info("Scanning MarylandBids.com...")
    opportunities = []

    try:
        url = "https://www.marylandbids.com/bids.aspx"
        headers = {"User-Agent": "Mozilla/5.0 (compatible; DDI-NEXUS/1.0)"}
        resp = requests.get(url, headers=headers, timeout=30)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")

        # Find bid listings
        for row in soup.find_all("tr"):
            try:
                cells = row.find_all("td")
                if len(cells) < 3:
                    continue

                title = cells[0].get_text(strip=True) if cells else ""
                if not title:
                    continue

                # Get link if available
                link_tag = cells[0].find("a")
                link = f"https://www.marylandbids.com{link_tag['href']}" if link_tag and link_tag.get("href") else ""

                agency = cells[1].get_text(strip=True) if len(cells) > 1 else ""
                deadline = cells[2].get_text(strip=True) if len(cells) > 2 else ""

                # Check relevance
                if not is_relevant_opportunity(title, agency):
                    continue

                # Check deadline
                if not has_enough_time(deadline):
                    continue

                opportunities.append({
                    "source": "MarylandBids.com",
                    "title": title,
                    "agency": agency,
                    "deadline": deadline,
                    "link": link,
                    "state": "MD",
                })

            except Exception:
                continue

    except Exception as e:
        log.error(f"MarylandBids.com error: {e}")

    return opportunities


# ============================================================================
# MAIN
# ============================================================================

def run_scan(tier1_only: bool = False) -> Dict:
    """Run the full portal scan."""
    log.info("=" * 60)
    log.info("NEXUS PUBLIC PORTAL SCANNER — Starting")
    log.info(f"Mode: {'Tier 1 Only' if tier1_only else 'Full Scan'}")
    log.info(f"Min days to bid: {MIN_DAYS_TO_BID}")
    log.info("=" * 60)

    all_opportunities = []

    # TIER 1 — Always scan
    scanners_tier1 = [
        ("SAM.gov", scan_sam_gov),
        ("BidNet Direct", scan_bidnet_direct),
        ("MITN (Michigan)", scan_mitn),
        ("Texas ESBD", scan_texas_esbd),
    ]

    # TIER 2 — Additional portals
    scanners_tier2 = [
        ("Virginia eVA", scan_virginia_eva),
        ("South Carolina SCBO", scan_south_carolina_scbo),
        ("Indiana", scan_indiana),
        ("Louisiana LaPAC", scan_louisiana_lapac),
        ("Connecticut CTsource", scan_connecticut),
        ("MarylandBids.com", scan_maryland_bids),
    ]

    scanners = scanners_tier1 if tier1_only else scanners_tier1 + scanners_tier2

    for name, scanner_func in scanners:
        try:
            results = scanner_func()
            all_opportunities.extend(results)
            log.info(f"  {name}: {len(results)} matches")
        except Exception as e:
            log.error(f"  {name}: FAILED — {e}")

    # Deduplicate by title similarity
    seen_titles = set()
    unique_opportunities = []
    for opp in all_opportunities:
        title_key = opp["title"].lower()[:60]
        if title_key not in seen_titles:
            seen_titles.add(title_key)
            unique_opportunities.append(opp)

    log.info(f"\nTotal unique opportunities: {len(unique_opportunities)}")

    # Save results
    results = {
        "scan_date": datetime.now().isoformat(),
        "total_found": len(unique_opportunities),
        "min_days_to_bid": MIN_DAYS_TO_BID,
        "opportunities": unique_opportunities,
    }

    with open(RESULTS_FILE, "w") as f:
        json.dump(results, f, indent=2, default=str)
    log.info(f"Results saved to {RESULTS_FILE}")

    # Generate report
    report = generate_report(unique_opportunities)
    with open(REPORT_FILE, "w") as f:
        f.write(report)
    log.info(f"Report saved to {REPORT_FILE}")

    log.info("=" * 60)
    log.info(f"SCAN COMPLETE — {len(unique_opportunities)} opportunities found")
    log.info("=" * 60)

    return results


if __name__ == "__main__":
    tier1_only = "--tier1" in sys.argv
    report_only = "--report" in sys.argv

    if report_only:
        # Just regenerate report from cached data
        if os.path.exists(RESULTS_FILE):
            with open(RESULTS_FILE) as f:
                data = json.load(f)
            report = generate_report(data.get("opportunities", []))
            with open(REPORT_FILE, "w") as f:
                f.write(report)
            print(f"Report regenerated: {REPORT_FILE}")
        else:
            print("No cached results. Run a scan first.")
    else:
        run_scan(tier1_only=tier1_only)
