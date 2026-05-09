"""
HAVEN — Regional Housing & Medical Partners
Specific providers in FL, TX, LA, MI — not just national chains.

Run:  python3 seed_haven_housing_medical_regional.py
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
# REGIONAL HOUSING PARTNERS
# ═══════════════════════════════════════════════════════════════════════════════

HOUSING_REGIONAL = [
    # ─── TEXAS ──────────────────────────────────────────────────────────────
    {
        "property_name": "Lodgeur Corporate Housing Houston",
        "chain_brand": "Independent",
        "partner_type": "Corporate Housing",
        "state": "TX",
        "agreement_status": "Prospect",
        "notes": "DISASTER SPECIALIST: Houston. 7,500+ guests. Midtown, Medical Center, Energy Corridor. Insurance relocation experience. 14-day notice termination. Priority target.",
    },
    {
        "property_name": "Houston Corporate Housing",
        "chain_brand": "Independent",
        "partner_type": "Corporate Housing",
        "state": "TX",
        "agreement_status": "Prospect",
        "notes": "DISASTER SPECIALIST: Can locate 1-50 units quickly. Shell Oil, UBS corporate relocations. Hurricane experience.",
    },
    {
        "property_name": "Globe Quarters Dallas",
        "chain_brand": "Independent",
        "partner_type": "Corporate Housing",
        "state": "TX",
        "agreement_status": "Prospect",
        "notes": "Uptown Dallas. Fitness, pool, business center, concierge. Extended stay corporate.",
    },
    {
        "property_name": "Staybridge Suites Houston Galleria",
        "chain_brand": "IHG",
        "partner_type": "Extended Stay",
        "state": "TX",
        "agreement_status": "Prospect",
        "notes": "IHG property. Full kitchens, sofa beds. Houston Galleria area.",
    },
    
    # ─── FLORIDA ────────────────────────────────────────────────────────────
    {
        "property_name": "FEMA TSA Hotel Network FL",
        "chain_brand": "Independent",
        "partner_type": "Hotel",
        "state": "FL",
        "agreement_status": "Prospect",
        "notes": "FEMA TSA: 52 FL counties approved. FEMAemergencyhotels.com. Helene/Milton survivors. DDI can coordinate placements.",
    },
    
    # ─── LOUISIANA ──────────────────────────────────────────────────────────
    {
        "property_name": "Louisiana Ida Sheltering Program",
        "chain_brand": "Independent",
        "partner_type": "FEMA Trailer",
        "state": "LA",
        "agreement_status": "Prospect",
        "notes": "STATE PROGRAM: Travel trailers + temp housing. idashelteringla.com. (844) 268-0301. Hurricane experience.",
    },
]

# ═══════════════════════════════════════════════════════════════════════════════
# REGIONAL MEDICAL PARTNERS — HOME HEALTH
# ═══════════════════════════════════════════════════════════════════════════════

MEDICAL_HOME_HEALTH = [
    # ─── FLORIDA ────────────────────────────────────────────────────────────
    {
        "company_name": "CenterWell Home Health FL",
        "partner_type": "Home Health Agency",
        "states_served": ["FL"],
        "agreement_status": "Prospect",
        "notes": "Jacksonville + statewide. 4.2-star CMS rating. Humana subsidiary. Skilled nursing, PT/OT/ST, aides. Priority target.",
    },
    {
        "company_name": "The Palace at Home Miami",
        "partner_type": "Home Health Agency",
        "states_served": ["FL"],
        "agreement_status": "Prospect",
        "notes": "Miami-Dade/Broward. Top 100 US Agency. Since 1997. Skilled nursing, rehab, aides.",
    },
    {
        "company_name": "BayCare HomeCare Tampa",
        "partner_type": "Home Health Agency",
        "states_served": ["FL"],
        "agreement_status": "Prospect",
        "notes": "Tampa Bay, 7 counties. 4.5-star CMS. Joint Commission accredited. Since 1976. Priority target.",
    },
    
    # ─── TEXAS ──────────────────────────────────────────────────────────────
    {
        "company_name": "CenterWell Home Health TX",
        "partner_type": "Home Health Agency",
        "states_served": ["TX"],
        "agreement_status": "Prospect",
        "notes": "San Antonio + statewide. 4.2-star CMS. Humana subsidiary. Priority target.",
    },
    {
        "company_name": "Signature Health Services Houston",
        "partner_type": "Home Health Agency",
        "states_served": ["TX"],
        "agreement_status": "Prospect",
        "notes": "Houston/SE Texas. 4.5-star rating. 7 counties. Since 1995. Priority target.",
    },
    {
        "company_name": "Provista Healthcare TX",
        "partner_type": "Home Health Agency",
        "states_served": ["TX"],
        "agreement_status": "Prospect",
        "notes": "DFW, San Antonio, Austin, Houston, Corpus Christi, El Paso. 20+ years. ACHC accredited.",
    },
    {
        "company_name": "Lucent Health Group Dallas",
        "partner_type": "Home Health Agency",
        "states_served": ["TX"],
        "agreement_status": "Prospect",
        "notes": "Dallas County. Skilled nursing, therapy, companion care.",
    },
    {
        "company_name": "Pathfinder Home Health TX",
        "partner_type": "Home Health Agency",
        "states_served": ["TX"],
        "agreement_status": "Prospect",
        "notes": "Medicare certified, state licensed. Multiple TX locations.",
    },
    
    # ─── LOUISIANA ──────────────────────────────────────────────────────────
    {
        "company_name": "Pulse Home Health Care LA",
        "partner_type": "Home Health Agency",
        "states_served": ["LA"],
        "agreement_status": "Prospect",
        "notes": "New Orleans (Southshore/Northshore). 4-star Medicare. HomeCare Elite 7x. #1 LA patient satisfaction. Priority target.",
    },
    {
        "company_name": "Ochsner Home Health New Orleans",
        "partner_type": "Home Health Agency",
        "states_served": ["LA"],
        "agreement_status": "Prospect",
        "notes": "Metairie. Part of Ochsner Health System. Full services + infusion + wound care. (504) 208-3582. Priority target.",
    },
    {
        "company_name": "Ochsner Home Health Baton Rouge",
        "partner_type": "Home Health Agency",
        "states_served": ["LA"],
        "agreement_status": "Prospect",
        "notes": "Baton Rouge. Part of Ochsner. (225) 952-8440.",
    },
    {
        "company_name": "Southeast Louisiana Home Health",
        "partner_type": "Home Health Agency",
        "states_served": ["LA"],
        "agreement_status": "Prospect",
        "notes": "Since 1971. 4-star Medicare. Skilled nursing, PT/OT/ST, aides, social work. (985) 892-8008.",
    },
]

# ═══════════════════════════════════════════════════════════════════════════════
# REGIONAL MEDICAL PARTNERS — DME
# ═══════════════════════════════════════════════════════════════════════════════

MEDICAL_DME = [
    # ─── FLORIDA ────────────────────────────────────────────────────────────
    {
        "company_name": "JC Home Medical Jacksonville",
        "partner_type": "DME Supplier",
        "states_served": ["FL"],
        "agreement_status": "Prospect",
        "notes": "Jacksonville. CPAP/BiPAP, portable O2, wheelchairs (rental). Medicare/Medicaid. Respiratory + wound care therapists. Priority target.",
    },
    {
        "company_name": "Care Medical Supplies FL",
        "partner_type": "DME Supplier",
        "states_served": ["FL"],
        "agreement_status": "Prospect",
        "notes": "West Palm Beach + statewide delivery. CPAP, O2, wheelchairs, scooters. Medicare/Medicaid. Sales + rentals.",
    },
    {
        "company_name": "Uni Medical Supplies FL",
        "partner_type": "DME Supplier",
        "states_served": ["FL"],
        "agreement_status": "Prospect",
        "notes": "Statewide FL. CPAP, O2, wheelchairs, walkers, hospital beds. Same/next day delivery. Medicare/Medicaid.",
    },
    {
        "company_name": "DME Respiratory Port St Lucie",
        "partner_type": "DME Supplier",
        "states_served": ["FL"],
        "agreement_status": "Prospect",
        "notes": "SE Florida. Since 2011. CPAP/BiPAP, home O2, hospital beds, power wheelchairs/scooters. Medicare/Medicaid certified.",
    },
    {
        "company_name": "Kinxo Medical FL",
        "partner_type": "DME Supplier",
        "states_served": ["FL"],
        "agreement_status": "Prospect",
        "notes": "AHCA licensed, BOC accredited. O2, hospital beds, wheelchairs, respiratory. Serves hospitals, HHAs, rehab.",
    },
]


def get_existing(table: str, key: str) -> set[str]:
    url = f"https://api.airtable.com/v0/{BASE_ID}/{table}"
    params = {"fields[]": key}
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
            val = rec["fields"].get(key, "")
            if val:
                records.add(val)
        offset = data.get("offset")
        if not offset:
            break
    return records


def create_record(table: str, fields: dict, name_field: str) -> bool:
    url = f"https://api.airtable.com/v0/{BASE_ID}/{table}"
    payload = {"records": [{"fields": fields}]}
    r = requests.post(url, headers=HEADERS, json=payload, timeout=20)
    if not r.ok:
        print(f"    ✗ {fields.get(name_field)}: {r.status_code}")
        return False
    print(f"  ✓ {fields.get(name_field)}")
    return True


def seed_table(table: str, records: list, key: str) -> tuple[int, int]:
    existing = get_existing(table, key)
    print(f"  Found {len(existing)} existing")
    created = skipped = 0
    for rec in records:
        name = rec.get(key, "")
        if name in existing:
            skipped += 1
            continue
        if create_record(table, rec, key):
            created += 1
        time.sleep(0.25)
    return created, skipped


def main() -> None:
    if not API_KEY or not BASE_ID:
        print("✗ Missing env vars")
        sys.exit(1)

    print("\n" + "═" * 60)
    print("  HAVEN — Regional Housing & Medical Partners")
    print("  FL, TX, LA specific providers")
    print("═" * 60)

    totals = {"c": 0, "s": 0}

    print("\n── HOUSING (Regional) ──")
    c, s = seed_table("Housing_Partners", HOUSING_REGIONAL, "property_name")
    totals["c"] += c
    totals["s"] += s
    print(f"  Created: {c} | Skipped: {s}")

    print("\n── MEDICAL: Home Health (Regional) ──")
    c, s = seed_table("Medical_Partners", MEDICAL_HOME_HEALTH, "company_name")
    totals["c"] += c
    totals["s"] += s
    print(f"  Created: {c} | Skipped: {s}")

    print("\n── MEDICAL: DME (Regional) ──")
    c, s = seed_table("Medical_Partners", MEDICAL_DME, "company_name")
    totals["c"] += c
    totals["s"] += s
    print(f"  Created: {c} | Skipped: {s}")

    print("\n" + "═" * 60)
    print(f"  COMPLETE")
    print(f"  Total Created: {totals['c']}")
    print(f"  Total Skipped: {totals['s']}")
    print(f"\n  Regional partners added:")
    print(f"    • Housing:     {len(HOUSING_REGIONAL)} (TX disaster specialists, FEMA networks)")
    print(f"    • Home Health: {len(MEDICAL_HOME_HEALTH)} (FL, TX, LA regional HHAs)")
    print(f"    • DME:         {len(MEDICAL_DME)} (FL regional DME suppliers)")
    print("═" * 60 + "\n")


if __name__ == "__main__":
    main()
