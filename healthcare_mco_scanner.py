#!/usr/bin/env python3
"""
NEXUS — Healthcare & MCO Opportunity Scanner
Scans MCO vendor portals, hospital RFP sites, and state Medicaid NEMT pages.

THIS IS WHAT WAS MISSING — commercial/enterprise healthcare search.

Sources:
  TIER 1 — State Medicaid NEMT/Transportation RFPs:
    1. Alabama Medicaid Procurement
    2. Arizona AHCCCS
    3. North Carolina Medicaid RFPs
    4. Illinois HFS Procurement
    5. Georgia DCH Procurement
    6. Colorado HCPF NEMT
    7. Ohio County JFS (NEMT RFPs)
    8. Texas HHSC (Open Enrollment)
    9. Florida AHCA
    10. Michigan MDHHS

  TIER 2 — Hospital System RFP Portals:
    1. University of Maryland Medical System (UMMS)
    2. Med Center Health
    3. Inspira Health
    4. ECMC (NY State Contract Reporter)
    5. Henry Ford Health (Michigan)
    6. Beaumont/Corewell Health (Michigan)

  TIER 3 — MCO Vendor Portals (require login — flag for manual check):
    1. Centene Supplier Portal
    2. Molina Healthcare Vendor
    3. UnitedHealth Group Supplier
    4. Anthem/Elevance Supplier
    5. Humana Supplier
    6. Aetna/CVS Health Supplier

Run: python3 healthcare_mco_scanner.py
     python3 healthcare_mco_scanner.py --tier1    # State Medicaid only
     python3 healthcare_mco_scanner.py --manual   # Generate manual check list
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
        logging.FileHandler(os.path.join(LOG_DIR, "healthcare_scanner.log")),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger("healthcare_scanner")

# Output files
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_FILE = os.path.join(BASE_DIR, "healthcare_scan_results.json")
REPORT_FILE = os.path.join(BASE_DIR, "HEALTHCARE_OPPORTUNITIES_REPORT.md")

# DDI healthcare keywords
HEALTHCARE_KEYWORDS = [
    # NEMT
    "nemt", "non-emergency medical transportation", "medical transportation",
    "patient transport", "medicaid transportation", "paratransit",
    "wheelchair transport", "ambulatory transport", "stretcher transport",
    "dialysis transport", "demand response",
    # Corrections/Veterans/Underserved
    "veteran", "veterans home", "corrections", "inmate", "prisoner",
    "behavioral health", "mental health", "senior transport", "elderly",
    "tribal", "rural health", "underserved",
    # Medical Courier
    "medical courier", "healthcare courier", "hospital courier",
    "medical delivery", "medical document delivery", "medical records delivery",
    "medical supply delivery", "dme delivery", "medical equipment delivery",
    "organ transport", "blood transport", "tissue transport",
    # Lab Courier / Specimen Transport
    "lab courier", "laboratory courier", "specimen transport",
    "specimen pickup", "specimen delivery", "specimen courier",
    "clinical specimen", "clinical sample", "lab sample",
    "diagnostic specimen", "pathology courier", "lab logistics",
    "reference lab", "newborn screening", "blood sample", "urine sample",
    # Pharmacy Courier
    "pharmacy courier", "pharmacy delivery", "prescription delivery",
    "medication delivery", "rx delivery", "pharmaceutical delivery",
    "pharmaceutical courier", "controlled substance delivery",
    "specialty pharmacy", "mail order pharmacy",
    "pharmacy distribution", "medication distribution",
    "drug distribution", "pharmaceutical distribution",
    "cold chain", "temperature controlled", "refrigerated delivery",
    # Legal Courier
    "legal courier", "court courier", "court filing",
    "legal document delivery", "process server", "process serving",
    "legal messenger", "court filing service", "legal filing",
    "document filing service", "court document", "legal records",
    "subpoena", "summons service",
    # General Courier
    "courier", "courier service", "delivery service",
    # Drug Testing Services
    "drug testing", "drug screen", "drug test", "drug and alcohol testing",
    "alcohol testing", "breath alcohol", "dot testing", "dot drug testing",
    "dot compliance", "fmcsa testing", "fta testing", "49 cfr part 40",
    "random drug testing", "random testing", "pre-employment drug",
    "post-accident testing", "reasonable suspicion", "return to duty",
    "workplace drug testing", "employee drug testing", "employee testing",
    "mro service", "medical review officer", "substance abuse testing",
    "substance abuse professional", "urine drug screen", "oral fluid testing",
    "hair follicle", "instant drug test", "rapid drug test",
    "samhsa certified", "c/tpa", "consortium", "clearinghouse",
    # Drug Testing Supplies
    "drug testing supplies", "drug test supplies", "drug test kit",
    "urine collection", "urine cup", "specimen cup", "collection cup",
    "collection kit", "drug screen cup", "5 panel", "10 panel", "12 panel",
    "oral fluid device", "breathalyzer", "chain of custody form", "ccf",
    # Occupational Health
    "occupational health", "dot physical", "pre-employment physical",
    # TPA Services
    "third party administrator", "tpa", "broker", "brokerage",
    "transportation broker", "nemt broker",
]


def is_relevant(title: str, description: str = "") -> bool:
    """Check if opportunity matches DDI healthcare capabilities."""
    text = f"{title} {description}".lower()
    for kw in HEALTHCARE_KEYWORDS:
        if kw in text:
            return True
    return False


# ============================================================================
# STATE MEDICAID NEMT PORTALS
# ============================================================================

def scan_alabama_medicaid() -> List[Dict]:
    """Scan Alabama Medicaid procurement page."""
    log.info("Scanning Alabama Medicaid...")
    opportunities = []
    try:
        url = "https://medicaid.alabama.gov/content/2.0_newsroom/2.4_Procurement.aspx"
        resp = requests.get(url, timeout=30)
        soup = BeautifulSoup(resp.text, "html.parser")
        
        for link in soup.find_all("a", href=True):
            text = link.get_text(strip=True)
            if is_relevant(text):
                opportunities.append({
                    "source": "Alabama Medicaid",
                    "title": text,
                    "link": link["href"] if link["href"].startswith("http") else f"https://medicaid.alabama.gov{link['href']}",
                    "state": "AL",
                    "type": "State Medicaid",
                })
    except Exception as e:
        log.error(f"Alabama Medicaid error: {e}")
    return opportunities


def scan_arizona_ahcccs() -> List[Dict]:
    """Scan Arizona AHCCCS solicitations."""
    log.info("Scanning Arizona AHCCCS...")
    opportunities = []
    try:
        url = "https://www.azahcccs.gov/PlansProviders/HealthPlans/purchasing.html"
        resp = requests.get(url, timeout=30)
        soup = BeautifulSoup(resp.text, "html.parser")
        
        for link in soup.find_all("a", href=True):
            text = link.get_text(strip=True)
            if is_relevant(text) or "rfp" in text.lower() or "solicitation" in text.lower():
                opportunities.append({
                    "source": "Arizona AHCCCS",
                    "title": text,
                    "link": link["href"] if link["href"].startswith("http") else f"https://www.azahcccs.gov{link['href']}",
                    "state": "AZ",
                    "type": "State Medicaid",
                })
    except Exception as e:
        log.error(f"Arizona AHCCCS error: {e}")
    return opportunities


def scan_north_carolina_medicaid() -> List[Dict]:
    """Scan NC Medicaid RFPs."""
    log.info("Scanning North Carolina Medicaid...")
    opportunities = []
    try:
        url = "https://medicaid.ncdhhs.gov/requests-proposals-rfps-and-requests-information-rfis"
        resp = requests.get(url, timeout=30)
        soup = BeautifulSoup(resp.text, "html.parser")
        
        for link in soup.find_all("a", href=True):
            text = link.get_text(strip=True)
            if is_relevant(text) or "rfp" in text.lower():
                opportunities.append({
                    "source": "NC Medicaid",
                    "title": text,
                    "link": link["href"] if link["href"].startswith("http") else f"https://medicaid.ncdhhs.gov{link['href']}",
                    "state": "NC",
                    "type": "State Medicaid",
                })
    except Exception as e:
        log.error(f"NC Medicaid error: {e}")
    return opportunities


def scan_illinois_hfs() -> List[Dict]:
    """Scan Illinois HFS procurement."""
    log.info("Scanning Illinois HFS...")
    opportunities = []
    try:
        url = "https://hfs.illinois.gov/info/procurement.html"
        resp = requests.get(url, timeout=30)
        soup = BeautifulSoup(resp.text, "html.parser")
        
        for link in soup.find_all("a", href=True):
            text = link.get_text(strip=True)
            if is_relevant(text) or "managed care" in text.lower() or "transportation" in text.lower():
                opportunities.append({
                    "source": "Illinois HFS",
                    "title": text,
                    "link": link["href"] if link["href"].startswith("http") else f"https://hfs.illinois.gov{link['href']}",
                    "state": "IL",
                    "type": "State Medicaid",
                })
    except Exception as e:
        log.error(f"Illinois HFS error: {e}")
    return opportunities


def scan_georgia_dch() -> List[Dict]:
    """Scan Georgia DCH procurement."""
    log.info("Scanning Georgia DCH...")
    opportunities = []
    try:
        url = "https://dch.georgia.gov/procurement"
        resp = requests.get(url, timeout=30)
        soup = BeautifulSoup(resp.text, "html.parser")
        
        for link in soup.find_all("a", href=True):
            text = link.get_text(strip=True)
            if is_relevant(text) or "rfp" in text.lower() or "managed care" in text.lower():
                opportunities.append({
                    "source": "Georgia DCH",
                    "title": text,
                    "link": link["href"] if link["href"].startswith("http") else f"https://dch.georgia.gov{link['href']}",
                    "state": "GA",
                    "type": "State Medicaid",
                })
    except Exception as e:
        log.error(f"Georgia DCH error: {e}")
    return opportunities


def scan_colorado_hcpf() -> List[Dict]:
    """Scan Colorado HCPF NEMT page."""
    log.info("Scanning Colorado HCPF...")
    opportunities = []
    try:
        url = "https://hcpf.colorado.gov/non-emergent-medical-transportation"
        resp = requests.get(url, timeout=30)
        soup = BeautifulSoup(resp.text, "html.parser")
        
        for link in soup.find_all("a", href=True):
            text = link.get_text(strip=True)
            if is_relevant(text) or "provider" in text.lower() or "enroll" in text.lower():
                opportunities.append({
                    "source": "Colorado HCPF",
                    "title": text,
                    "link": link["href"] if link["href"].startswith("http") else f"https://hcpf.colorado.gov{link['href']}",
                    "state": "CO",
                    "type": "State Medicaid NEMT",
                })
    except Exception as e:
        log.error(f"Colorado HCPF error: {e}")
    return opportunities


def scan_florida_ahca() -> List[Dict]:
    """Scan Florida AHCA procurement."""
    log.info("Scanning Florida AHCA...")
    opportunities = []
    try:
        url = "https://ahca.myflorida.com/Medicaid/statewide_mc/index.shtml"
        resp = requests.get(url, timeout=30)
        soup = BeautifulSoup(resp.text, "html.parser")
        
        for link in soup.find_all("a", href=True):
            text = link.get_text(strip=True)
            if is_relevant(text) or "procurement" in text.lower() or "rfp" in text.lower():
                opportunities.append({
                    "source": "Florida AHCA",
                    "title": text,
                    "link": link["href"] if link["href"].startswith("http") else f"https://ahca.myflorida.com{link['href']}",
                    "state": "FL",
                    "type": "State Medicaid",
                })
    except Exception as e:
        log.error(f"Florida AHCA error: {e}")
    return opportunities


def scan_texas_hhsc() -> List[Dict]:
    """Scan Texas HHSC procurement (including NEMT open enrollment)."""
    log.info("Scanning Texas HHSC...")
    opportunities = []
    try:
        url = "https://www.hhs.texas.gov/doing-business-hhs/contracting-hhs/contracting-opportunities"
        resp = requests.get(url, timeout=30)
        soup = BeautifulSoup(resp.text, "html.parser")
        
        for link in soup.find_all("a", href=True):
            text = link.get_text(strip=True)
            if is_relevant(text) or "nemt" in text.lower() or "transportation" in text.lower() or "open enrollment" in text.lower():
                opportunities.append({
                    "source": "Texas HHSC",
                    "title": text,
                    "link": link["href"] if link["href"].startswith("http") else f"https://www.hhs.texas.gov{link['href']}",
                    "state": "TX",
                    "type": "State Medicaid",
                })
    except Exception as e:
        log.error(f"Texas HHSC error: {e}")
    return opportunities


def scan_michigan_mdhhs() -> List[Dict]:
    """Scan Michigan MDHHS procurement."""
    log.info("Scanning Michigan MDHHS...")
    opportunities = []
    try:
        url = "https://www.michigan.gov/mdhhs/doing-business/contracts"
        resp = requests.get(url, timeout=30)
        soup = BeautifulSoup(resp.text, "html.parser")
        
        for link in soup.find_all("a", href=True):
            text = link.get_text(strip=True)
            if is_relevant(text) or "rfp" in text.lower() or "contract" in text.lower():
                opportunities.append({
                    "source": "Michigan MDHHS",
                    "title": text,
                    "link": link["href"] if link["href"].startswith("http") else f"https://www.michigan.gov{link['href']}",
                    "state": "MI",
                    "type": "State Medicaid",
                })
    except Exception as e:
        log.error(f"Michigan MDHHS error: {e}")
    return opportunities


# ============================================================================
# HOSPITAL SYSTEM RFP PORTALS
# ============================================================================

def scan_umms() -> List[Dict]:
    """Scan University of Maryland Medical System RFPs."""
    log.info("Scanning UMMS...")
    opportunities = []
    try:
        url = "https://www.umms.org/about/vendors-services/minority-business-program/open-rfp"
        resp = requests.get(url, timeout=30)
        soup = BeautifulSoup(resp.text, "html.parser")
        
        for item in soup.find_all(["h3", "h4", "li", "p"]):
            text = item.get_text(strip=True)
            if is_relevant(text) or "rfp" in text.lower() or "ambulance" in text.lower() or "transport" in text.lower():
                link = item.find("a")
                opportunities.append({
                    "source": "UMMS (Univ of Maryland)",
                    "title": text[:200],
                    "link": link["href"] if link and link.get("href") else url,
                    "state": "MD",
                    "type": "Hospital System",
                })
    except Exception as e:
        log.error(f"UMMS error: {e}")
    return opportunities


def scan_med_center_health() -> List[Dict]:
    """Scan Med Center Health procurement."""
    log.info("Scanning Med Center Health...")
    opportunities = []
    try:
        url = "https://medcenterhealth.org/procurement-opportunities/"
        resp = requests.get(url, timeout=30)
        soup = BeautifulSoup(resp.text, "html.parser")
        
        for item in soup.find_all(["h2", "h3", "p", "li"]):
            text = item.get_text(strip=True)
            if is_relevant(text) or "rfp" in text.lower():
                link = item.find("a")
                opportunities.append({
                    "source": "Med Center Health",
                    "title": text[:200],
                    "link": link["href"] if link and link.get("href") else url,
                    "state": "KY",
                    "type": "Hospital System",
                })
    except Exception as e:
        log.error(f"Med Center Health error: {e}")
    return opportunities


def scan_inspira_health() -> List[Dict]:
    """Scan Inspira Health RFPs."""
    log.info("Scanning Inspira Health...")
    opportunities = []
    try:
        url = "https://www.inspirahealthnetwork.org/about-us/request-proposals-rfp"
        resp = requests.get(url, timeout=30)
        soup = BeautifulSoup(resp.text, "html.parser")
        
        for item in soup.find_all(["h2", "h3", "p", "li"]):
            text = item.get_text(strip=True)
            if is_relevant(text) or "rfp" in text.lower():
                link = item.find("a")
                opportunities.append({
                    "source": "Inspira Health",
                    "title": text[:200],
                    "link": link["href"] if link and link.get("href") else url,
                    "state": "NJ",
                    "type": "Hospital System",
                })
    except Exception as e:
        log.error(f"Inspira Health error: {e}")
    return opportunities


# ============================================================================
# MCO VENDOR PORTALS (Manual Check List)
# ============================================================================

MCO_VENDOR_PORTALS = [
    {
        "name": "Centene Supplier Portal",
        "url": "https://www.centene.com/who-we-are/working-with-centene/supplier-registration.html",
        "brands": ["Sunshine Health (FL)", "Superior (TX)", "Peach State (GA)", "Buckeye (OH)", "Meridian (MI)"],
        "notes": "Requires login. Check for NEMT, transportation, courier RFPs.",
    },
    {
        "name": "Molina Healthcare Vendor Portal",
        "url": "https://www.molinahealthcare.com/providers/common/Pages/Vendors.aspx",
        "brands": ["Molina Michigan", "Molina Texas", "Molina Ohio", "Molina Florida"],
        "notes": "Requires login. NEMT and ancillary services.",
    },
    {
        "name": "UnitedHealth Group Supplier",
        "url": "https://www.uhc.com/supplier",
        "brands": ["UnitedHealthcare Community Plan", "Optum"],
        "notes": "Large MCO. Check for NEMT broker opportunities.",
    },
    {
        "name": "Elevance Health (Anthem) Supplier",
        "url": "https://www.elevancehealth.com/who-we-are/suppliers",
        "brands": ["Anthem BCBS", "Amerigroup", "Simply Healthcare"],
        "notes": "Multiple state Medicaid plans. NEMT opportunities.",
    },
    {
        "name": "Humana Supplier Portal",
        "url": "https://www.humana.com/about/suppliers",
        "brands": ["Humana Healthy Horizons"],
        "notes": "D-SNP and Medicaid plans.",
    },
    {
        "name": "Aetna/CVS Health Supplier",
        "url": "https://cvshealth.com/about-cvs-health/our-offerings/aetna/supplier-diversity",
        "brands": ["Aetna Better Health"],
        "notes": "Medicaid managed care in multiple states.",
    },
    {
        "name": "HAP (Health Alliance Plan) - Michigan",
        "url": "https://www.hap.org/providers",
        "brands": ["HAP CareSource"],
        "notes": "Michigan Medicaid. DDI has active contract.",
    },
    {
        "name": "McLaren Health Plan - Michigan",
        "url": "https://www.mclarenhealthplan.org/providers",
        "brands": ["McLaren Health Plan"],
        "notes": "Michigan Medicaid.",
    },
    {
        "name": "Priority Health - Michigan",
        "url": "https://www.priorityhealth.com/provider",
        "brands": ["Priority Health"],
        "notes": "Michigan Medicaid.",
    },
    {
        "name": "Blue Cross Complete - Michigan",
        "url": "https://www.bcbsm.com/providers/medicaid",
        "brands": ["Blue Cross Complete"],
        "notes": "Michigan Medicaid.",
    },
]


def generate_manual_checklist() -> str:
    """Generate manual check list for MCO portals that require login."""
    checklist = f"""# MCO VENDOR PORTAL MANUAL CHECK LIST
**Generated:** {datetime.now().strftime("%B %d, %Y at %I:%M %p")}

These portals require login. Check each one for NEMT, transportation, and courier RFPs.

---

"""
    for portal in MCO_VENDOR_PORTALS:
        checklist += f"""## {portal['name']}
- **URL:** {portal['url']}
- **Brands:** {', '.join(portal['brands'])}
- **Notes:** {portal['notes']}
- [ ] Checked today

---

"""
    return checklist


# ============================================================================
# MAIN SCANNER
# ============================================================================

def run_scan(tier1_only: bool = False) -> Dict:
    """Run the healthcare portal scan."""
    log.info("=" * 60)
    log.info("NEXUS HEALTHCARE & MCO SCANNER — Starting")
    log.info(f"Mode: {'Tier 1 (State Medicaid) Only' if tier1_only else 'Full Scan'}")
    log.info("=" * 60)

    all_opportunities = []

    # TIER 1 — State Medicaid NEMT portals
    state_scanners = [
        ("Alabama Medicaid", scan_alabama_medicaid),
        ("Arizona AHCCCS", scan_arizona_ahcccs),
        ("North Carolina Medicaid", scan_north_carolina_medicaid),
        ("Illinois HFS", scan_illinois_hfs),
        ("Georgia DCH", scan_georgia_dch),
        ("Colorado HCPF", scan_colorado_hcpf),
        ("Florida AHCA", scan_florida_ahca),
        ("Texas HHSC", scan_texas_hhsc),
        ("Michigan MDHHS", scan_michigan_mdhhs),
    ]

    for name, scanner_func in state_scanners:
        try:
            results = scanner_func()
            all_opportunities.extend(results)
            log.info(f"  {name}: {len(results)} matches")
        except Exception as e:
            log.error(f"  {name}: FAILED — {e}")

    # TIER 2 — Hospital Systems (unless tier1_only)
    if not tier1_only:
        hospital_scanners = [
            ("UMMS", scan_umms),
            ("Med Center Health", scan_med_center_health),
            ("Inspira Health", scan_inspira_health),
        ]

        for name, scanner_func in hospital_scanners:
            try:
                results = scanner_func()
                all_opportunities.extend(results)
                log.info(f"  {name}: {len(results)} matches")
            except Exception as e:
                log.error(f"  {name}: FAILED — {e}")

    # Deduplicate
    seen = set()
    unique = []
    for opp in all_opportunities:
        key = opp["title"][:50].lower()
        if key not in seen:
            seen.add(key)
            unique.append(opp)

    log.info(f"\nTotal unique opportunities: {len(unique)}")

    # Save results
    results = {
        "scan_date": datetime.now().isoformat(),
        "total_found": len(unique),
        "opportunities": unique,
    }

    with open(RESULTS_FILE, "w") as f:
        json.dump(results, f, indent=2, default=str)
    log.info(f"Results saved to {RESULTS_FILE}")

    # Generate report
    report = generate_report(unique)
    with open(REPORT_FILE, "w") as f:
        f.write(report)
    log.info(f"Report saved to {REPORT_FILE}")

    # Generate MCO manual checklist
    checklist = generate_manual_checklist()
    checklist_file = os.path.join(BASE_DIR, "MCO_PORTAL_DAILY_CHECKLIST.md")
    with open(checklist_file, "w") as f:
        f.write(checklist)
    log.info(f"MCO checklist saved to {checklist_file}")

    log.info("=" * 60)
    log.info(f"SCAN COMPLETE — {len(unique)} opportunities found")
    log.info("=" * 60)

    return results


def generate_report(opportunities: List[Dict]) -> str:
    """Generate markdown report."""
    report = f"""# HEALTHCARE & MCO OPPORTUNITIES REPORT — {datetime.now().strftime("%B %d, %Y at %I:%M %p")}
## Generated by NEXUS Healthcare Scanner

**Total Opportunities Found:** {len(opportunities)}
**Filtered for DDI NEMT/Healthcare capabilities**

---

"""
    # Group by source
    by_source = {}
    for opp in opportunities:
        source = opp.get("source", "Unknown")
        if source not in by_source:
            by_source[source] = []
        by_source[source].append(opp)

    for source, opps in by_source.items():
        report += f"## {source} ({len(opps)} opportunities)\n\n"
        for i, opp in enumerate(opps, 1):
            report += f"### {i}. {opp['title']}\n"
            report += f"- **State:** {opp.get('state', 'N/A')}\n"
            report += f"- **Type:** {opp.get('type', 'N/A')}\n"
            report += f"- **Link:** {opp.get('link', 'N/A')}\n\n"
        report += "---\n\n"

    report += """## MCO VENDOR PORTALS (Manual Check Required)

The following MCO portals require login and must be checked manually:

"""
    for portal in MCO_VENDOR_PORTALS:
        report += f"- [ ] **{portal['name']}** — {portal['url']}\n"

    report += """

---

*Generated by NEXUS Healthcare & MCO Scanner*
*Sources: State Medicaid portals, Hospital RFP sites, MCO vendor portals*
"""
    return report


if __name__ == "__main__":
    tier1_only = "--tier1" in sys.argv
    manual_only = "--manual" in sys.argv

    if manual_only:
        checklist = generate_manual_checklist()
        checklist_file = os.path.join(BASE_DIR, "MCO_PORTAL_DAILY_CHECKLIST.md")
        with open(checklist_file, "w") as f:
            f.write(checklist)
        print(f"MCO checklist generated: {checklist_file}")
    else:
        run_scan(tier1_only=tier1_only)
