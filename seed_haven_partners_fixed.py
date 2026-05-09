"""
HAVEN — Complete Partner Network Database (FIXED)
Field names match HAVEN_NETWORK_REGISTRY_SCHEMA.md exactly.

Run:  python3 seed_haven_partners_fixed.py
"""
from __future__ import annotations

import os
import sys
import time

import requests
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

API_KEY = os.environ.get("AIRTABLE_API_KEY", "")
BASE_ID = os.environ.get("HAVEN_BASE_ID", "")

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}

# ═══════════════════════════════════════════════════════════════════════════════
# TRANSPORT PARTNERS — Fields per schema
# partner_type: Single Select (Rideshare / NEMT Fleet / Charter Bus / Medical Transport / Courier)
# states_served: Multiple Select (FL / TX / LA / National)
# agreement_status: Single Select (Prospect / Outreach / Negotiating / Signed / Active)
# ═══════════════════════════════════════════════════════════════════════════════

TRANSPORT_PARTNERS = [
    # NATIONAL
    {"company_name": "Uber Health", "partner_type": "Rideshare", "states_served": ["FL", "TX", "LA", "National"], "agreement_status": "Prospect", "notes": "National platform. Healthcare API. Contact form pending."},
    {"company_name": "Lyft Healthcare", "partner_type": "Rideshare", "states_served": ["FL", "TX", "LA", "National"], "agreement_status": "Outreach", "notes": "National platform. Contact form submitted May 8, 2026."},
    {"company_name": "ModivCare", "partner_type": "NEMT Fleet", "states_served": ["FL", "TX", "LA"], "agreement_status": "Prospect", "notes": "Largest national NEMT broker. Potential partner or competitor."},
    {"company_name": "MTM Inc", "partner_type": "NEMT Fleet", "states_served": ["FL", "TX"], "agreement_status": "Prospect", "notes": "Major NEMT broker. FL regions 3-8, TX statewide. MTM Link API."},
    {"company_name": "SafeRide Health", "partner_type": "NEMT Fleet", "states_served": ["TX"], "agreement_status": "Prospect", "notes": "TX NEMT broker. Real-time visibility."},
    # LOUISIANA
    {"company_name": "MediTrans Louisiana", "partner_type": "NEMT Fleet", "states_served": ["LA"], "agreement_status": "Prospect", "notes": "Serves 5 LA MCOs. Statewide CTN. (844) 349-4326."},
    {"company_name": "Verida Louisiana", "partner_type": "NEMT Fleet", "states_served": ["LA"], "agreement_status": "Prospect", "notes": "LA FFS Medicaid NEMT. (225) 726-2800."},
    # FLORIDA
    {"company_name": "MV Transportation Florida", "partner_type": "NEMT Fleet", "states_served": ["FL"], "agreement_status": "Prospect", "notes": "Major paratransit/NEMT fleet. Multiple FL counties."},
    {"company_name": "First Transit Florida", "partner_type": "NEMT Fleet", "states_served": ["FL"], "agreement_status": "Prospect", "notes": "Paratransit and fixed-route. FL counties."},
    # TEXAS
    {"company_name": "MV Transportation Texas", "partner_type": "NEMT Fleet", "states_served": ["TX"], "agreement_status": "Prospect", "notes": "Major TX paratransit. Houston, Dallas, San Antonio."},
    {"company_name": "RATP Dev Texas", "partner_type": "NEMT Fleet", "states_served": ["TX"], "agreement_status": "Prospect", "notes": "Houston METRO paratransit contractor."},
    # MICHIGAN
    {"company_name": "Trinity Transportation MI", "partner_type": "NEMT Fleet", "states_served": ["National"], "agreement_status": "Prospect", "notes": "SE Michigan NEMT. DDI potential sub."},
    {"company_name": "MedStar Transportation MI", "partner_type": "NEMT Fleet", "states_served": ["National"], "agreement_status": "Prospect", "notes": "Metro Detroit NEMT. Wheelchair/ambulatory."},
    {"company_name": "SMART Transit", "partner_type": "NEMT Fleet", "states_served": ["National"], "agreement_status": "Prospect", "notes": "SE Michigan public transit. Disaster staging connector."},
    # CHARTER
    {"company_name": "Greyhound Charter", "partner_type": "Charter Bus", "states_served": ["FL", "TX", "LA", "National"], "agreement_status": "Prospect", "notes": "National charter. Mass evacuation capacity."},
    {"company_name": "Vonlane Texas", "partner_type": "Charter Bus", "states_served": ["TX"], "agreement_status": "Prospect", "notes": "TX luxury motorcoach. Houston-Dallas-Austin."},
]

# ═══════════════════════════════════════════════════════════════════════════════
# HOUSING PARTNERS — Fields per schema
# property_name: Single Line Text (NOT company_name!)
# partner_type: Single Select (Hotel / Extended Stay / Corporate Housing / Property Manager / FEMA Trailer)
# chain_brand: Single Select (Marriott / Hilton / IHG / Wyndham / Choice / Independent / Extended Stay)
# state: Single Select (FL / TX / LA)
# agreement_status: Single Select
# ═══════════════════════════════════════════════════════════════════════════════

HOUSING_PARTNERS = [
    # NATIONAL CHAINS — Use "National" in notes since state is single select
    {"property_name": "Marriott Extended Stay Portfolio", "chain_brand": "Marriott", "partner_type": "Extended Stay", "state": "FL", "agreement_status": "Prospect", "notes": "National: Residence Inn, TownePlace. Red Cross partner. FL/TX/LA/MI coverage."},
    {"property_name": "Hilton Extended Stay Portfolio", "chain_brand": "Hilton", "partner_type": "Extended Stay", "state": "FL", "agreement_status": "Prospect", "notes": "National: Homewood, Home2, Embassy. FEMA experience. FL/TX/LA/MI coverage."},
    {"property_name": "Wyndham Extended Stay Portfolio", "chain_brand": "Wyndham", "partner_type": "Extended Stay", "state": "FL", "agreement_status": "Prospect", "notes": "National: Hawthorn, ECHO Suites, WaterWalk. FL/TX/LA/MI coverage."},
    {"property_name": "IHG Extended Stay Portfolio", "chain_brand": "IHG", "partner_type": "Extended Stay", "state": "FL", "agreement_status": "Prospect", "notes": "National: Candlewood, Staybridge. Pet-friendly. FL/TX/LA/MI coverage."},
    {"property_name": "Extended Stay America Corporate", "chain_brand": "Extended Stay", "partner_type": "Extended Stay", "state": "FL", "agreement_status": "Prospect", "notes": "Largest extended stay chain. 750+ locations. FEMA billing. FL/TX/LA/MI."},
    {"property_name": "Choice Hotels Extended Stay", "chain_brand": "Choice", "partner_type": "Extended Stay", "state": "FL", "agreement_status": "Prospect", "notes": "National: WoodSpring, MainStay. Budget extended stay. FL/TX/LA/MI."},
    {"property_name": "Best Western Extended Stay", "chain_brand": "Independent", "partner_type": "Extended Stay", "state": "FL", "agreement_status": "Prospect", "notes": "Executive Residency brand. Regional contacts needed. FL/TX/LA/MI."},
    # CORPORATE HOUSING
    {"property_name": "Synergy Global Housing", "chain_brand": "Independent", "partner_type": "Corporate Housing", "state": "FL", "agreement_status": "Prospect", "notes": "National: Formerly Oakwood. Furnished apts 30+ days. Insurance billing."},
    {"property_name": "National Corporate Housing", "chain_brand": "Independent", "partner_type": "Corporate Housing", "state": "FL", "agreement_status": "Prospect", "notes": "National furnished apartments. Disaster relocation experience."},
    {"property_name": "Furnished Finder Network", "chain_brand": "Independent", "partner_type": "Corporate Housing", "state": "FL", "agreement_status": "Prospect", "notes": "Platform connecting travelers with rentals. Travel nurse focus."},
    # DISASTER SPECIALISTS
    {"property_name": "SwiftResponse Travel", "chain_brand": "Independent", "partner_type": "Property Manager", "state": "FL", "agreement_status": "Prospect", "notes": "Emergency crew management. Real-time dashboard. All major chains. Competitor or partner."},
    {"property_name": "Sedgwick Temp Housing", "chain_brand": "Independent", "partner_type": "Property Manager", "state": "FL", "agreement_status": "Prospect", "notes": "Insurance claims TPA. Temp housing for property claims. Model to study."},
    {"property_name": "ApartmentFinder CoStar", "chain_brand": "Independent", "partner_type": "Property Manager", "state": "FL", "agreement_status": "Prospect", "notes": "Apartment listings. API available for vacancy searches."},
]

# ═══════════════════════════════════════════════════════════════════════════════
# MEDICAL PARTNERS — Fields per schema
# company_name: Single Line Text
# partner_type: Single Select (Home Health Agency / DME Supplier / Pharmacy / Medical Courier / Hospice)
# states_served: Multiple Select (FL / TX / LA)
# agreement_status: Single Select
# ═══════════════════════════════════════════════════════════════════════════════

MEDICAL_PARTNERS = [
    # NATIONAL HOME HEALTH
    {"company_name": "Amedisys Optum Home Health", "partner_type": "Home Health Agency", "states_served": ["LA", "FL", "TX"], "agreement_status": "Prospect", "notes": "Largest US HHA. HQ Baton Rouge. 332K patients. Now Optum."},
    {"company_name": "Enhabit Home Health", "partner_type": "Home Health Agency", "states_served": ["TX", "FL", "LA"], "agreement_status": "Prospect", "notes": "HQ Dallas. 172K patients. Strong TX/FL."},
    {"company_name": "AccentCare", "partner_type": "Home Health Agency", "states_served": ["TX", "FL"], "agreement_status": "Prospect", "notes": "HQ Dallas. 105K patients. Also hospice."},
    {"company_name": "Interim HealthCare", "partner_type": "Home Health Agency", "states_served": ["FL", "TX"], "agreement_status": "Prospect", "notes": "HQ Sunrise FL. Franchise. Also staffing."},
    {"company_name": "LHC Group Optum", "partner_type": "Home Health Agency", "states_served": ["LA", "TX", "FL"], "agreement_status": "Prospect", "notes": "HQ Lafayette LA. Strong Gulf Coast. Now Optum."},
    {"company_name": "BAYADA Home Health", "partner_type": "Home Health Agency", "states_served": ["FL", "TX"], "agreement_status": "Prospect", "notes": "National. Pediatric and behavioral specialties."},
    {"company_name": "Kindred at Home Humana", "partner_type": "Home Health Agency", "states_served": ["FL", "TX", "LA"], "agreement_status": "Prospect", "notes": "National. Now Humana owned."},
    # MICHIGAN HOME HEALTH
    {"company_name": "Henry Ford Home Health", "partner_type": "Home Health Agency", "states_served": ["LA"], "agreement_status": "Prospect", "notes": "MICHIGAN: Part of Henry Ford Health. Wayne/Oakland/Macomb."},
    {"company_name": "Superior Home Health MI", "partner_type": "Home Health Agency", "states_served": ["LA"], "agreement_status": "Prospect", "notes": "MICHIGAN: NP-led. Wayne/Oakland/Livingston/Genesee/Washtenaw."},
    {"company_name": "QCN Home Health Care", "partner_type": "Home Health Agency", "states_served": ["LA"], "agreement_status": "Prospect", "notes": "MICHIGAN: SE Michigan. 20+ years. Medicare certified."},
    {"company_name": "Integrity Home Health MI", "partner_type": "Home Health Agency", "states_served": ["LA"], "agreement_status": "Prospect", "notes": "MICHIGAN: Greater Detroit. 15 SE Michigan counties."},
    # DME
    {"company_name": "Rotech Healthcare", "partner_type": "DME Supplier", "states_served": ["FL", "TX", "LA"], "agreement_status": "Prospect", "notes": "National DME. Respiratory focus."},
    {"company_name": "AdaptHealth", "partner_type": "DME Supplier", "states_served": ["FL", "TX", "LA"], "agreement_status": "Prospect", "notes": "National DME. Respiratory and diabetes."},
    {"company_name": "Lincare", "partner_type": "DME Supplier", "states_served": ["FL", "TX", "LA"], "agreement_status": "Prospect", "notes": "National respiratory/oxygen. Critical for disaster O2."},
    {"company_name": "Apria Healthcare", "partner_type": "DME Supplier", "states_served": ["FL", "TX", "LA"], "agreement_status": "Prospect", "notes": "Now Owens & Minor. Large footprint."},
    # PHARMACY
    {"company_name": "CVS Health Caremark", "partner_type": "Pharmacy", "states_served": ["FL", "TX", "LA"], "agreement_status": "Prospect", "notes": "Largest US pharmacy. PBM. Emergency Rx fills."},
    {"company_name": "Walgreens", "partner_type": "Pharmacy", "states_served": ["FL", "TX", "LA"], "agreement_status": "Prospect", "notes": "National retail pharmacy. Emergency refills."},
    {"company_name": "Express Scripts Cigna", "partner_type": "Pharmacy", "states_served": ["FL", "TX", "LA"], "agreement_status": "Prospect", "notes": "Major PBM. Disaster Rx continuity protocols."},
    {"company_name": "OptumRx", "partner_type": "Pharmacy", "states_served": ["FL", "TX", "LA"], "agreement_status": "Prospect", "notes": "UHG PBM. Coordinates with Optum home health."},
    {"company_name": "Amazon Pharmacy", "partner_type": "Pharmacy", "states_served": ["FL", "TX", "LA"], "agreement_status": "Prospect", "notes": "Mail order + Prime same-day. Rapid disaster Rx."},
    # INFUSION
    {"company_name": "Option Care Health", "partner_type": "Pharmacy", "states_served": ["FL", "TX", "LA"], "agreement_status": "Prospect", "notes": "Largest home infusion. Critical for IV therapy continuity."},
    {"company_name": "PharMerica", "partner_type": "Pharmacy", "states_served": ["FL", "TX", "LA"], "agreement_status": "Prospect", "notes": "LTC pharmacy. Nursing facility Rx continuity."},
]


def get_existing_records(table_name: str, key_field: str) -> set[str]:
    """Return set of existing record key values."""
    url = f"https://api.airtable.com/v0/{BASE_ID}/{table_name}"
    params = {"fields[]": key_field}
    records = set()
    offset = None
    while True:
        if offset:
            params["offset"] = offset
        r = requests.get(url, headers=HEADERS, params=params, timeout=20)
        if not r.ok:
            break
        data = r.json()
        for rec in data.get("records", []):
            val = rec["fields"].get(key_field, "")
            if val:
                records.add(val)
        offset = data.get("offset")
        if not offset:
            break
    return records


def create_record(table_name: str, fields: dict, name_field: str) -> bool:
    url = f"https://api.airtable.com/v0/{BASE_ID}/{table_name}"
    payload = {"records": [{"fields": fields}]}
    r = requests.post(url, headers=HEADERS, json=payload, timeout=20)
    if not r.ok:
        print(f"    ✗ {fields.get(name_field)}: {r.status_code} {r.text[:300]}")
        return False
    print(f"  ✓ {fields.get(name_field)}")
    return True


def seed_table(table_name: str, records: list, key_field: str) -> tuple[int, int]:
    existing = get_existing_records(table_name, key_field)
    print(f"  Found {len(existing)} existing")
    created = skipped = 0
    for rec in records:
        name = rec.get(key_field, "")
        if name in existing:
            skipped += 1
            continue
        if create_record(table_name, rec, key_field):
            created += 1
        time.sleep(0.25)
    return created, skipped


def main() -> None:
    if not API_KEY or not BASE_ID:
        print("✗ Missing env vars"); sys.exit(1)

    print("\n" + "═"*60)
    print("  HAVEN Partner Network — MI, FL, TX, LA")
    print("═"*60)

    totals = {"c": 0, "s": 0}

    print("\n── TRANSPORT PARTNERS ──")
    c, s = seed_table("Transport_Partners", TRANSPORT_PARTNERS, "company_name")
    totals["c"] += c; totals["s"] += s
    print(f"  Created: {c} | Skipped: {s}")

    print("\n── HOUSING PARTNERS ──")
    c, s = seed_table("Housing_Partners", HOUSING_PARTNERS, "property_name")
    totals["c"] += c; totals["s"] += s
    print(f"  Created: {c} | Skipped: {s}")

    print("\n── MEDICAL PARTNERS ──")
    c, s = seed_table("Medical_Partners", MEDICAL_PARTNERS, "company_name")
    totals["c"] += c; totals["s"] += s
    print(f"  Created: {c} | Skipped: {s}")

    print("\n" + "═"*60)
    print(f"  TOTAL: {totals['c']} created, {totals['s']} skipped")
    print(f"  Transport: {len(TRANSPORT_PARTNERS)}")
    print(f"  Housing:   {len(HOUSING_PARTNERS)}")
    print(f"  Medical:   {len(MEDICAL_PARTNERS)}")
    print(f"  GRAND:     {len(TRANSPORT_PARTNERS)+len(HOUSING_PARTNERS)+len(MEDICAL_PARTNERS)}")
    print("═"*60 + "\n")


if __name__ == "__main__":
    main()
