"""
HAVEN — Complete Partner Network Database
Seeds Transport, Housing, and Medical partners for MI, FL, TX, LA

Run:  python3 seed_haven_partners_complete.py
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
# TRANSPORT PARTNERS
# ═══════════════════════════════════════════════════════════════════════════════

TRANSPORT_PARTNERS = [
    # ─── NATIONAL / MULTI-STATE ─────────────────────────────────────────────
    {
        "company_name": "Uber Health",
        "partner_type": ["Rideshare"],
        "service_states": ["MI", "FL", "TX", "LA"],
        "service_capabilities": ["Non-Emergency Transport", "Wheelchair Accessible", "Evacuation"],
        "compliance_status": "Not Started",
        "contract_status": "Target",
        "notes": "National platform. Healthcare API available. Lyft contact form submitted May 8 — Uber next.",
    },
    {
        "company_name": "Lyft Healthcare",
        "partner_type": ["Rideshare"],
        "service_states": ["MI", "FL", "TX", "LA"],
        "service_capabilities": ["Non-Emergency Transport", "Wheelchair Accessible", "Evacuation"],
        "compliance_status": "Not Started",
        "contract_status": "Target",
        "notes": "National platform. Healthcare partnerships. Contact form submitted May 8, 2026.",
    },
    {
        "company_name": "ModivCare (formerly LogistiCare)",
        "partner_type": ["NEMT Broker"],
        "service_states": ["FL", "TX", "LA"],
        "service_capabilities": ["Non-Emergency Transport", "Wheelchair Accessible", "Stretcher", "Bariatric"],
        "compliance_status": "Not Started",
        "contract_status": "Target",
        "notes": "Largest national NEMT broker. Could be partner OR competitor depending on structure.",
    },
    {
        "company_name": "MTM (Medical Transportation Management)",
        "partner_type": ["NEMT Broker"],
        "service_states": ["FL", "TX"],
        "service_capabilities": ["Non-Emergency Transport", "Wheelchair Accessible", "Stretcher"],
        "compliance_status": "Not Started",
        "contract_status": "Target",
        "notes": "Major NEMT broker. FL regions 3-8. TX statewide. MTM Link API available.",
    },
    {
        "company_name": "SafeRide Health",
        "partner_type": ["NEMT Broker"],
        "service_states": ["TX"],
        "service_capabilities": ["Non-Emergency Transport", "Wheelchair Accessible"],
        "compliance_status": "Not Started",
        "contract_status": "Target",
        "notes": "TX NEMT broker. Real-time visibility platform.",
    },
    
    # ─── LOUISIANA ──────────────────────────────────────────────────────────
    {
        "company_name": "MediTrans Louisiana",
        "partner_type": ["NEMT Broker"],
        "service_states": ["LA"],
        "service_capabilities": ["Non-Emergency Transport", "Wheelchair Accessible", "Stretcher"],
        "compliance_status": "Not Started",
        "contract_status": "Target",
        "notes": "Serves 5 LA MCOs: Aetna, AmeriHealth, Healthy Blue, Humana, LHCC. Statewide CTN.",
    },
    {
        "company_name": "Verida Louisiana",
        "partner_type": ["NEMT Broker"],
        "service_states": ["LA"],
        "service_capabilities": ["Non-Emergency Transport", "Wheelchair Accessible"],
        "compliance_status": "Not Started",
        "contract_status": "Target",
        "notes": "LA Fee-for-Service Medicaid NEMT. Phone: (225) 726-2800.",
    },
    
    # ─── FLORIDA ────────────────────────────────────────────────────────────
    {
        "company_name": "MV Transportation Florida",
        "partner_type": ["NEMT Fleet"],
        "service_states": ["FL"],
        "service_capabilities": ["Non-Emergency Transport", "Wheelchair Accessible", "Paratransit"],
        "compliance_status": "Not Started",
        "contract_status": "Target",
        "notes": "Major paratransit/NEMT fleet operator. FL locations.",
    },
    {
        "company_name": "First Transit Florida",
        "partner_type": ["NEMT Fleet"],
        "service_states": ["FL"],
        "service_capabilities": ["Non-Emergency Transport", "Wheelchair Accessible", "Paratransit"],
        "compliance_status": "Not Started",
        "contract_status": "Target",
        "notes": "Paratransit and fixed-route operator. Multiple FL counties.",
    },
    
    # ─── TEXAS ──────────────────────────────────────────────────────────────
    {
        "company_name": "MV Transportation Texas",
        "partner_type": ["NEMT Fleet"],
        "service_states": ["TX"],
        "service_capabilities": ["Non-Emergency Transport", "Wheelchair Accessible", "Paratransit"],
        "compliance_status": "Not Started",
        "contract_status": "Target",
        "notes": "Major TX paratransit operator. Houston, Dallas, San Antonio.",
    },
    {
        "company_name": "RATP Dev Texas",
        "partner_type": ["NEMT Fleet"],
        "service_states": ["TX"],
        "service_capabilities": ["Non-Emergency Transport", "Paratransit"],
        "compliance_status": "Not Started",
        "contract_status": "Target",
        "notes": "Houston METRO paratransit contractor.",
    },
    
    # ─── MICHIGAN ───────────────────────────────────────────────────────────
    {
        "company_name": "Trinity Transportation",
        "partner_type": ["NEMT Fleet"],
        "service_states": ["MI"],
        "service_capabilities": ["Non-Emergency Transport", "Wheelchair Accessible", "Stretcher"],
        "compliance_status": "Not Started",
        "contract_status": "Target",
        "notes": "SE Michigan NEMT provider. DDI potential subcontractor.",
    },
    {
        "company_name": "MedStar Transportation",
        "partner_type": ["NEMT Fleet"],
        "service_states": ["MI"],
        "service_capabilities": ["Non-Emergency Transport", "Wheelchair Accessible", "Stretcher"],
        "compliance_status": "Not Started",
        "contract_status": "Target",
        "notes": "Metro Detroit NEMT. Wheelchair and ambulatory.",
    },
    {
        "company_name": "SMART (Suburban Mobility Authority)",
        "partner_type": ["Public Transit"],
        "service_states": ["MI"],
        "service_capabilities": ["Paratransit", "Fixed Route"],
        "compliance_status": "Not Started",
        "contract_status": "Research",
        "notes": "SE Michigan public transit. Connector service for disaster staging.",
    },
    
    # ─── CHARTER / EVACUATION ───────────────────────────────────────────────
    {
        "company_name": "Greyhound Charter",
        "partner_type": ["Charter Bus"],
        "service_states": ["MI", "FL", "TX", "LA"],
        "service_capabilities": ["Evacuation", "Mass Transport"],
        "compliance_status": "Not Started",
        "contract_status": "Target",
        "notes": "National charter service. Mass evacuation capacity.",
    },
    {
        "company_name": "Vonlane (TX)",
        "partner_type": ["Charter Bus"],
        "service_states": ["TX"],
        "service_capabilities": ["Evacuation", "Luxury Transport"],
        "compliance_status": "Not Started",
        "contract_status": "Target",
        "notes": "TX luxury motorcoach. Houston-Dallas-Austin corridor.",
    },
]

# ═══════════════════════════════════════════════════════════════════════════════
# HOUSING PARTNERS
# ═══════════════════════════════════════════════════════════════════════════════

HOUSING_PARTNERS = [
    # ─── NATIONAL HOTEL CHAINS ──────────────────────────────────────────────
    {
        "company_name": "Marriott Extended Stay (Residence Inn, TownePlace)",
        "partner_type": ["Extended Stay Hotel"],
        "service_states": ["MI", "FL", "TX", "LA"],
        "room_capacity": 50000,
        "compliance_status": "Not Started",
        "contract_status": "Target",
        "notes": "Red Cross Disaster Responder Program partner. Insurance company billing experience. National footprint.",
    },
    {
        "company_name": "Hilton Extended Stay (Homewood, Home2, Embassy)",
        "partner_type": ["Extended Stay Hotel"],
        "service_states": ["MI", "FL", "TX", "LA"],
        "room_capacity": 40000,
        "compliance_status": "Not Started",
        "contract_status": "Target",
        "notes": "Full kitchens, free breakfast. Weekly/monthly rates. FEMA experience.",
    },
    {
        "company_name": "Wyndham Extended Stay (Hawthorn, ECHO Suites, WaterWalk)",
        "partner_type": ["Extended Stay Hotel"],
        "service_states": ["MI", "FL", "TX", "LA"],
        "room_capacity": 30000,
        "compliance_status": "Not Started",
        "contract_status": "Target",
        "notes": "Three extended stay brands. Free hot breakfast. Social hours at Hawthorn.",
    },
    {
        "company_name": "IHG (Candlewood Suites, Staybridge Suites)",
        "partner_type": ["Extended Stay Hotel"],
        "service_states": ["MI", "FL", "TX", "LA"],
        "room_capacity": 35000,
        "compliance_status": "Not Started",
        "contract_status": "Target",
        "notes": "Full kitchens. Pet-friendly options. Extended stay focus.",
    },
    {
        "company_name": "Extended Stay America",
        "partner_type": ["Extended Stay Hotel"],
        "service_states": ["MI", "FL", "TX", "LA"],
        "room_capacity": 75000,
        "compliance_status": "Not Started",
        "contract_status": "Target",
        "notes": "Largest extended stay chain. 750+ locations. FEMA/insurance billing experience.",
    },
    {
        "company_name": "Choice Hotels (WoodSpring Suites, MainStay Suites)",
        "partner_type": ["Extended Stay Hotel"],
        "service_states": ["MI", "FL", "TX", "LA"],
        "room_capacity": 25000,
        "compliance_status": "Not Started",
        "contract_status": "Target",
        "notes": "Economy extended stay. Good for budget-conscious disaster housing.",
    },
    {
        "company_name": "Best Western (Executive Residency)",
        "partner_type": ["Extended Stay Hotel"],
        "service_states": ["MI", "FL", "TX", "LA"],
        "room_capacity": 15000,
        "compliance_status": "Not Started",
        "contract_status": "Target",
        "notes": "Extended stay brand. Independent franchise model — regional contacts needed.",
    },
    
    # ─── CORPORATE HOUSING ──────────────────────────────────────────────────
    {
        "company_name": "Oakwood (now Synergy Global Housing)",
        "partner_type": ["Corporate Housing"],
        "service_states": ["MI", "FL", "TX", "LA"],
        "room_capacity": 10000,
        "compliance_status": "Not Started",
        "contract_status": "Target",
        "notes": "Furnished apartments. 30+ day stays. Insurance/corporate billing.",
    },
    {
        "company_name": "National Corporate Housing",
        "partner_type": ["Corporate Housing"],
        "service_states": ["MI", "FL", "TX", "LA"],
        "room_capacity": 8000,
        "compliance_status": "Not Started",
        "contract_status": "Target",
        "notes": "Furnished apartments nationwide. Disaster relocation experience.",
    },
    {
        "company_name": "Furnished Finder",
        "partner_type": ["Corporate Housing Marketplace"],
        "service_states": ["MI", "FL", "TX", "LA"],
        "room_capacity": 100000,
        "compliance_status": "Not Started",
        "contract_status": "Research",
        "notes": "Platform connecting travelers with furnished rentals. Travel nurse focus but disaster applicable.",
    },
    
    # ─── DISASTER SPECIALISTS ───────────────────────────────────────────────
    {
        "company_name": "SwiftResponse Travel",
        "partner_type": ["Disaster Housing Coordinator"],
        "service_states": ["MI", "FL", "TX", "LA"],
        "room_capacity": 0,
        "compliance_status": "Not Started",
        "contract_status": "Target",
        "notes": "Emergency crew management. Real-time hotel dashboard. All major chains. 24/7 service. Potential COMPETITOR or partner.",
    },
    {
        "company_name": "Sedgwick Temporary Housing",
        "partner_type": ["Insurance Housing Coordinator"],
        "service_states": ["MI", "FL", "TX", "LA"],
        "room_capacity": 0,
        "compliance_status": "Not Started",
        "contract_status": "Research",
        "notes": "Insurance claims TPA. Temporary housing coordination for property claims. Model to study.",
    },
    
    # ─── REGIONAL / STATE-SPECIFIC ──────────────────────────────────────────
    {
        "company_name": "ApartmentFinder / CoStar",
        "partner_type": ["Apartment Marketplace"],
        "service_states": ["MI", "FL", "TX", "LA"],
        "room_capacity": 0,
        "compliance_status": "Not Started",
        "contract_status": "Research",
        "notes": "Apartment listings platform. API available for vacancy searches.",
    },
]

# ═══════════════════════════════════════════════════════════════════════════════
# MEDICAL PARTNERS (Home Health, DME, Pharmacy, Rx Continuity)
# ═══════════════════════════════════════════════════════════════════════════════

MEDICAL_PARTNERS = [
    # ─── NATIONAL HOME HEALTH ───────────────────────────────────────────────
    {
        "company_name": "Amedisys (now Optum Home Health)",
        "partner_type": ["Home Health Agency"],
        "service_states": ["LA", "FL", "TX"],
        "service_capabilities": ["Skilled Nursing", "PT/OT/ST", "Home Health Aide", "Medical Social Work"],
        "compliance_status": "Not Started",
        "contract_status": "Target",
        "notes": "Largest US home health agency. HQ in Baton Rouge LA. Acquired by UHG/Optum 2025. 332K patients.",
    },
    {
        "company_name": "Enhabit Home Health & Hospice",
        "partner_type": ["Home Health Agency"],
        "service_states": ["TX", "FL", "LA"],
        "service_capabilities": ["Skilled Nursing", "PT/OT/ST", "Home Health Aide", "Hospice"],
        "compliance_status": "Not Started",
        "contract_status": "Target",
        "notes": "HQ in Dallas TX. 172K patients. Strong TX/FL presence.",
    },
    {
        "company_name": "AccentCare",
        "partner_type": ["Home Health Agency"],
        "service_states": ["TX", "FL"],
        "service_capabilities": ["Skilled Nursing", "PT/OT/ST", "Personal Care", "Hospice"],
        "compliance_status": "Not Started",
        "contract_status": "Target",
        "notes": "HQ in Dallas TX. 105K patients. Also operates hospice.",
    },
    {
        "company_name": "Interim HealthCare",
        "partner_type": ["Home Health Agency"],
        "service_states": ["FL", "TX", "MI"],
        "service_capabilities": ["Skilled Nursing", "PT/OT/ST", "Home Health Aide", "Staffing"],
        "compliance_status": "Not Started",
        "contract_status": "Target",
        "notes": "HQ in Sunrise FL. Franchise model. Also does healthcare staffing.",
    },
    {
        "company_name": "LHC Group",
        "partner_type": ["Home Health Agency"],
        "service_states": ["LA", "TX", "FL"],
        "service_capabilities": ["Skilled Nursing", "PT/OT/ST", "Hospice"],
        "compliance_status": "Not Started",
        "contract_status": "Target",
        "notes": "HQ in Lafayette LA. Strong Gulf Coast presence. Now part of UHG/Optum.",
    },
    {
        "company_name": "BAYADA Home Health Care",
        "partner_type": ["Home Health Agency"],
        "service_states": ["FL", "TX", "MI"],
        "service_capabilities": ["Skilled Nursing", "PT/OT/ST", "Pediatric", "Behavioral Health"],
        "compliance_status": "Not Started",
        "contract_status": "Target",
        "notes": "National provider. Pediatric and behavioral health specialties.",
    },
    {
        "company_name": "Kindred at Home",
        "partner_type": ["Home Health Agency"],
        "service_states": ["FL", "TX", "LA"],
        "service_capabilities": ["Skilled Nursing", "PT/OT/ST", "Hospice"],
        "compliance_status": "Not Started",
        "contract_status": "Target",
        "notes": "Major national provider. Now part of Humana.",
    },
    
    # ─── MICHIGAN HOME HEALTH ───────────────────────────────────────────────
    {
        "company_name": "Henry Ford Home Health Care",
        "partner_type": ["Home Health Agency"],
        "service_states": ["MI"],
        "service_capabilities": ["Skilled Nursing", "PT/OT/ST", "Infusion", "Wound Care", "Transplant"],
        "compliance_status": "Not Started",
        "contract_status": "Target",
        "notes": "Part of Henry Ford Health. Serves Wayne, Oakland, Macomb, Jackson counties. Specialty programs.",
    },
    {
        "company_name": "Superior Home Health of Michigan",
        "partner_type": ["Home Health Agency"],
        "service_states": ["MI"],
        "service_capabilities": ["Skilled Nursing", "PT/OT/ST", "Wound Care"],
        "compliance_status": "Not Started",
        "contract_status": "Target",
        "notes": "NP-led agency. Wayne, Oakland, Livingston, Genesee, Washtenaw counties.",
    },
    {
        "company_name": "QCN Home Health Care",
        "partner_type": ["Home Health Agency"],
        "service_states": ["MI"],
        "service_capabilities": ["Skilled Nursing", "Infusion", "PT/OT/ST"],
        "compliance_status": "Not Started",
        "contract_status": "Target",
        "notes": "SE Michigan. 20+ years. Medicare certified.",
    },
    {
        "company_name": "Integrity Home Health Care",
        "partner_type": ["Home Health Agency"],
        "service_states": ["MI"],
        "service_capabilities": ["Skilled Nursing", "PT/OT/ST"],
        "compliance_status": "Not Started",
        "contract_status": "Target",
        "notes": "Greater Detroit. 15 SE Michigan counties.",
    },
    
    # ─── DME PROVIDERS ──────────────────────────────────────────────────────
    {
        "company_name": "Rotech Healthcare",
        "partner_type": ["DME Provider"],
        "service_states": ["FL", "TX", "LA", "MI"],
        "service_capabilities": ["Respiratory", "Sleep Therapy", "Mobility", "Wound Care"],
        "compliance_status": "Not Started",
        "contract_status": "Target",
        "notes": "National DME provider. Respiratory focus. Good disaster DME continuity partner.",
    },
    {
        "company_name": "AdaptHealth",
        "partner_type": ["DME Provider"],
        "service_states": ["FL", "TX", "LA", "MI"],
        "service_capabilities": ["Respiratory", "Diabetes", "Mobility", "Sleep Therapy"],
        "compliance_status": "Not Started",
        "contract_status": "Target",
        "notes": "Major national DME. Strong respiratory and diabetes supply.",
    },
    {
        "company_name": "Lincare",
        "partner_type": ["DME Provider"],
        "service_states": ["FL", "TX", "LA", "MI"],
        "service_capabilities": ["Respiratory", "Oxygen", "Sleep Therapy", "Infusion"],
        "compliance_status": "Not Started",
        "contract_status": "Target",
        "notes": "National respiratory/oxygen provider. Critical for disaster O2 continuity.",
    },
    {
        "company_name": "Apria Healthcare",
        "partner_type": ["DME Provider"],
        "service_states": ["FL", "TX", "LA", "MI"],
        "service_capabilities": ["Respiratory", "Sleep Therapy", "Negative Pressure Wound", "Enteral"],
        "compliance_status": "Not Started",
        "contract_status": "Target",
        "notes": "Now part of Owens & Minor. Large footprint.",
    },
    
    # ─── PHARMACY / RX CONTINUITY ───────────────────────────────────────────
    {
        "company_name": "CVS Health / Caremark",
        "partner_type": ["Pharmacy", "PBM"],
        "service_states": ["MI", "FL", "TX", "LA"],
        "service_capabilities": ["Retail Pharmacy", "Specialty Pharmacy", "Mail Order", "PBM"],
        "compliance_status": "Not Started",
        "contract_status": "Target",
        "notes": "Largest US pharmacy chain. PBM capabilities. Emergency Rx fills.",
    },
    {
        "company_name": "Walgreens",
        "partner_type": ["Pharmacy"],
        "service_states": ["MI", "FL", "TX", "LA"],
        "service_capabilities": ["Retail Pharmacy", "Specialty Pharmacy", "Immunizations"],
        "compliance_status": "Not Started",
        "contract_status": "Target",
        "notes": "National retail pharmacy. Emergency refill programs.",
    },
    {
        "company_name": "Express Scripts (Cigna)",
        "partner_type": ["PBM"],
        "service_states": ["MI", "FL", "TX", "LA"],
        "service_capabilities": ["Mail Order", "Specialty Pharmacy", "PBM"],
        "compliance_status": "Not Started",
        "contract_status": "Target",
        "notes": "Major PBM. Disaster Rx continuity protocols.",
    },
    {
        "company_name": "OptumRx",
        "partner_type": ["PBM"],
        "service_states": ["MI", "FL", "TX", "LA"],
        "service_capabilities": ["Mail Order", "Specialty Pharmacy", "PBM"],
        "compliance_status": "Not Started",
        "contract_status": "Target",
        "notes": "UHG PBM. Coordinates with Optum home health for continuity.",
    },
    {
        "company_name": "Amazon Pharmacy",
        "partner_type": ["Pharmacy"],
        "service_states": ["MI", "FL", "TX", "LA"],
        "service_capabilities": ["Mail Order", "Same-Day Delivery"],
        "compliance_status": "Not Started",
        "contract_status": "Research",
        "notes": "Mail order + Prime same-day. Potential rapid Rx delivery in disasters.",
    },
    
    # ─── SPECIALTY / INFUSION ───────────────────────────────────────────────
    {
        "company_name": "BioScrip / Option Care Health",
        "partner_type": ["Infusion Pharmacy"],
        "service_states": ["FL", "TX", "LA", "MI"],
        "service_capabilities": ["Home Infusion", "Specialty Pharmacy", "Nursing Support"],
        "compliance_status": "Not Started",
        "contract_status": "Target",
        "notes": "Largest independent home infusion provider. Critical for IV therapy continuity.",
    },
    {
        "company_name": "PharMerica",
        "partner_type": ["Pharmacy"],
        "service_states": ["FL", "TX", "LA", "MI"],
        "service_capabilities": ["LTC Pharmacy", "Specialty Pharmacy"],
        "compliance_status": "Not Started",
        "contract_status": "Target",
        "notes": "Long-term care pharmacy. Nursing facility Rx continuity.",
    },
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
        print(f"    ✗ {fields.get(name_field)}: {r.status_code} {r.text[:200]}")
        return False
    states = fields.get("service_states", [""])
    state_str = ", ".join(states) if isinstance(states, list) else states
    print(f"  ✓ {fields.get(name_field)} ({state_str})")
    return True


def seed_table(table_name: str, records: list, key_field: str) -> tuple[int, int]:
    """Seed records into a table. Returns (created, skipped)."""
    existing = get_existing_records(table_name, key_field)
    print(f"  Found {len(existing)} existing record(s)")
    
    created = 0
    skipped = 0
    
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
        print("✗ Missing AIRTABLE_API_KEY or HAVEN_BASE_ID in .env")
        sys.exit(1)

    print("\n" + "═" * 60)
    print("  HAVEN — Complete Partner Network Database")
    print(f"  Base: {BASE_ID}")
    print("═" * 60)

    totals = {"created": 0, "skipped": 0}

    # ─── TRANSPORT PARTNERS ─────────────────────────────────────────────────
    print("\n┌─ TRANSPORT PARTNERS ─────────────────────────────────────┐")
    created, skipped = seed_table("Transport_Partners", TRANSPORT_PARTNERS, "company_name")
    totals["created"] += created
    totals["skipped"] += skipped
    print(f"└─ Created: {created} | Skipped: {skipped} ─────────────────────┘")

    # ─── HOUSING PARTNERS ───────────────────────────────────────────────────
    print("\n┌─ HOUSING PARTNERS ───────────────────────────────────────┐")
    created, skipped = seed_table("Housing_Partners", HOUSING_PARTNERS, "company_name")
    totals["created"] += created
    totals["skipped"] += skipped
    print(f"└─ Created: {created} | Skipped: {skipped} ─────────────────────┘")

    # ─── MEDICAL PARTNERS ───────────────────────────────────────────────────
    print("\n┌─ MEDICAL PARTNERS ───────────────────────────────────────┐")
    created, skipped = seed_table("Medical_Partners", MEDICAL_PARTNERS, "company_name")
    totals["created"] += created
    totals["skipped"] += skipped
    print(f"└─ Created: {created} | Skipped: {skipped} ─────────────────────┘")

    # ─── SUMMARY ────────────────────────────────────────────────────────────
    print("\n" + "═" * 60)
    print("  COMPLETE")
    print(f"  Total Created: {totals['created']}")
    print(f"  Total Skipped: {totals['skipped']}")
    print("\n  Partner counts:")
    print(f"    • Transport: {len(TRANSPORT_PARTNERS)} partners")
    print(f"    • Housing:   {len(HOUSING_PARTNERS)} partners")
    print(f"    • Medical:   {len(MEDICAL_PARTNERS)} partners")
    print(f"    • TOTAL:     {len(TRANSPORT_PARTNERS) + len(HOUSING_PARTNERS) + len(MEDICAL_PARTNERS)} partners")
    print("\n  Coverage:")
    print(f"    • Michigan (MI): Home state")
    print(f"    • Florida (FL):  Hurricane corridor")
    print(f"    • Texas (TX):    Hurricane + winter storm")
    print(f"    • Louisiana (LA): Hurricane alley")
    print("═" * 60 + "\n")


if __name__ == "__main__":
    main()
