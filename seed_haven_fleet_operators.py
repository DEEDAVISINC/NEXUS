"""
HAVEN — Fleet Operators (Stretcher, Bariatric, Specialized)
These fill the void that Uber/Lyft don't cover.

Run:  python3 seed_haven_fleet_operators.py
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
# FLEET OPERATORS — Stretcher, Bariatric, Wheelchair (not brokers!)
# ═══════════════════════════════════════════════════════════════════════════════

FLEET_OPERATORS = [
    # ─── FLORIDA ────────────────────────────────────────────────────────────
    {
        "company_name": "Stellar Transportation FL",
        "partner_type": "NEMT Fleet",
        "states_served": ["FL"],
        "agreement_status": "Prospect",
        "notes": "STRETCHER: Statewide FL, 150+ mile trips, multiple stretchers per vehicle, Stryker/Ferno equipment, 2-person crews. Priority target.",
    },
    {
        "company_name": "Florida Medical Transport",
        "partner_type": "NEMT Fleet",
        "states_served": ["FL"],
        "agreement_status": "Prospect",
        "notes": "STRETCHER/WHEELCHAIR: Statewide FL, since 2012, claims #1 FL provider. Ambulatory, wheelchair, stretcher.",
    },
    {
        "company_name": "Jano Med-Ride",
        "partner_type": "NEMT Fleet",
        "states_served": ["FL"],
        "agreement_status": "Prospect",
        "notes": "BARIATRIC: Broward/Palm Beach/Miami-Dade. Up to 750 lbs capacity. 2-person crews. Bed-bound specialists.",
    },
    {
        "company_name": "ITDV Medical Transportation",
        "partner_type": "NEMT Fleet",
        "states_served": ["FL"],
        "agreement_status": "Prospect",
        "notes": "STRETCHER: South FL (Fort Lauderdale area). Hollywood, Pembroke Pines, Pompano Beach. (954) 348-5501.",
    },
    {
        "company_name": "Volusia Medical Transport",
        "partner_type": "NEMT Fleet",
        "states_served": ["FL"],
        "agreement_status": "Prospect",
        "notes": "STRETCHER/WHEELCHAIR: Volusia County. ADA-approved, hydraulic lifts. (386) 576-7503.",
    },
    
    # ─── TEXAS ──────────────────────────────────────────────────────────────
    {
        "company_name": "PrimeCare Transports TX",
        "partner_type": "NEMT Fleet",
        "states_served": ["TX"],
        "agreement_status": "Prospect",
        "notes": "BARIATRIC: Statewide TX (Dallas, Fort Worth, Houston, Austin). Up to 650 lbs. Stretcher, wheelchair, long-distance. Since 2005. Priority target.",
    },
    {
        "company_name": "Safe Medical Transport TX",
        "partner_type": "NEMT Fleet",
        "states_served": ["TX"],
        "agreement_status": "Prospect",
        "notes": "STRETCHER/BARIATRIC: Dallas + statewide. 24/7. Bariatric up to 500 lbs. Stair lifter. Long-distance.",
    },
    {
        "company_name": "Healthlift Medical Transportation",
        "partner_type": "NEMT Fleet",
        "states_served": ["TX"],
        "agreement_status": "Prospect",
        "notes": "BARIATRIC: Houston metro + statewide. 24/7. Bariatric, wheelchair, Broda chair. GPS/AI dash cams. Priority target.",
    },
    {
        "company_name": "Medixcar TX",
        "partner_type": "NEMT Fleet",
        "states_served": ["TX"],
        "agreement_status": "Prospect",
        "notes": "BARIATRIC: North Texas. Since 2009. Bariatric up to 475 lbs with O2. Broda chairs. Bed-to-bed.",
    },
    {
        "company_name": "Texana Medical Transportation",
        "partner_type": "NEMT Fleet",
        "states_served": ["TX"],
        "agreement_status": "Prospect",
        "notes": "WHEELCHAIR: Dallas. Hydraulic lifts, rear ramps. Custom services.",
    },
    
    # ─── LOUISIANA ──────────────────────────────────────────────────────────
    {
        "company_name": "SPD LLC Louisiana",
        "partner_type": "NEMT Fleet",
        "states_served": ["LA"],
        "agreement_status": "Prospect",
        "notes": "STRETCHER/WHEELCHAIR: Metairie, 18+ years experience. Statewide potential. (877) 577-1440. Priority target.",
    },
    {
        "company_name": "A-MED Ambulance LA",
        "partner_type": "NEMT Fleet",
        "states_served": ["LA"],
        "agreement_status": "Prospect",
        "notes": "WHEELCHAIR: Largest wheelchair fleet in Greater New Orleans. Since 1996. CPR/first aid certified. Priority target.",
    },
    {
        "company_name": "Dave Transportation LA",
        "partner_type": "NEMT Fleet",
        "states_served": ["LA"],
        "agreement_status": "Prospect",
        "notes": "WHEELCHAIR: New Orleans. 24/7. ADA-compliant, any wheelchair size. 6+ years.",
    },
    
    # ─── MICHIGAN ───────────────────────────────────────────────────────────
    {
        "company_name": "HOUR Transportation MI",
        "partner_type": "NEMT Fleet",
        "states_served": ["National"],
        "agreement_status": "Prospect",
        "notes": "BARIATRIC: Southfield-based, 20 vehicles. Bariatric up to 400 lbs. Branches: Ann Arbor, Flint, Shelby Twp. 24/7/365. (248) 569-7500. Priority target.",
    },
    {
        "company_name": "Safe Care Transports MI",
        "partner_type": "NEMT Fleet",
        "states_served": ["National"],
        "agreement_status": "Prospect",
        "notes": "STRETCHER: Statewide MI. Stretcher alternative transport. 24/7. GPS-equipped. Live dispatch.",
    },
    {
        "company_name": "MediTrans Michigan",
        "partner_type": "NEMT Fleet",
        "states_served": ["National"],
        "agreement_status": "Prospect",
        "notes": "WHEELCHAIR: Metro Detroit since 2009. Sedans, mini-vans, wheelchair-lift vans.",
    },
    {
        "company_name": "M&T Medical Transportation MI",
        "partner_type": "NEMT Fleet",
        "states_served": ["National"],
        "agreement_status": "Prospect",
        "notes": "WHEELCHAIR: Detroit. BBB accredited. Auto accident claims. Wheelchair accessible.",
    },
    {
        "company_name": "Harmony Transportation MI",
        "partner_type": "NEMT Fleet",
        "states_served": ["National"],
        "agreement_status": "Prospect",
        "notes": "WHEELCHAIR: Tri-county Detroit. Handicap-accessible. Hydraulic lifts.",
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


def main() -> None:
    if not API_KEY or not BASE_ID:
        print("✗ Missing env vars")
        sys.exit(1)

    print("\n" + "═" * 60)
    print("  HAVEN — Fleet Operators (Stretcher/Bariatric/Specialized)")
    print("  Filling the gap Uber/Lyft don't cover")
    print("═" * 60 + "\n")

    existing = get_existing("Transport_Partners", "company_name")
    print(f"Found {len(existing)} existing transport partners\n")

    created = 0
    skipped = 0

    for op in FLEET_OPERATORS:
        if op["company_name"] in existing:
            print(f"  – {op['company_name']} exists, skipping")
            skipped += 1
            continue
        if create_record("Transport_Partners", op, "company_name"):
            created += 1
        time.sleep(0.25)

    print("\n" + "═" * 60)
    print(f"  COMPLETE")
    print(f"  Created: {created}")
    print(f"  Skipped: {skipped}")
    print(f"\n  Fleet operators by state:")
    print(f"    • Florida:   5 (Stellar, FL Medical, Jano, ITDV, Volusia)")
    print(f"    • Texas:     5 (PrimeCare, Safe Medical, Healthlift, Medixcar, Texana)")
    print(f"    • Louisiana: 3 (SPD, A-MED, Dave)")
    print(f"    • Michigan:  5 (HOUR, Safe Care, MediTrans MI, M&T, Harmony)")
    print(f"\n  Capabilities filled:")
    print(f"    ✓ Stretcher transport")
    print(f"    ✓ Bariatric (up to 750 lbs)")
    print(f"    ✓ Wheelchair (hydraulic lifts)")
    print(f"    ✓ Long-distance")
    print(f"    ✓ 24/7 availability")
    print("═" * 60 + "\n")


if __name__ == "__main__":
    main()
