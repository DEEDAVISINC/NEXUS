"""
HAVEN — Complete MCO Database
Adds ALL FL/TX/LA Medicaid MCOs (not just priority targets).
Also removes UHC Louisiana (dropped April 2026 per LDH).

Run:  python3 seed_haven_mco_complete.py
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
TABLE_NAME = "MCO_Contracts"

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}

# ─────────────────────────────────────────────────────────────────────────────
# ADDITIONAL MCOs (not in original seed)
# Source: FL AHCA SMMC 2025-2030, TX HHSC, LA LDH April 2026
# ─────────────────────────────────────────────────────────────────────────────

ADDITIONAL_MCOS = [
    # ─── FLORIDA — Additional MCOs from SMMC 2025-2030 ──────────────────────
    {
        "mco_name": "Community Care Plan",
        "parent_company": "Broward Health (Independent)",
        "state": "FL",
        "program_type": ["Medicaid"],
        "member_count": 200000,
        "services_contracted": ["All HAVEN"],
        "contract_status": "Target",
        "credentialing_status": "Not Started",
        "notes": "Regions E-I (Central/South FL). Provider-sponsored plan via Broward Health.",
    },
    {
        "mco_name": "UnitedHealthcare of Florida",
        "parent_company": "UnitedHealth Group",
        "state": "FL",
        "program_type": ["Medicaid", "Medicare Advantage"],
        "member_count": 800000,
        "services_contracted": ["All HAVEN"],
        "contract_status": "Target",
        "credentialing_status": "Not Started",
        "notes": "Regions B, D, I. UHC national network. Note: Still active in FL unlike LA.",
    },
    
    # ─── TEXAS — Additional MCOs from HHSC ──────────────────────────────────
    {
        "mco_name": "Aetna Better Health of Texas",
        "parent_company": "CVS / Aetna",
        "state": "TX",
        "program_type": ["Medicaid", "CHIP"],
        "member_count": 400000,
        "services_contracted": ["All HAVEN"],
        "contract_status": "Target",
        "credentialing_status": "Not Started",
        "notes": "CVS integration for Rx continuity. Sister plans in FL and LA.",
    },
    {
        "mco_name": "Blue Cross Blue Shield of Texas",
        "parent_company": "HCSC (Health Care Service Corporation)",
        "state": "TX",
        "program_type": ["Medicaid", "CHIP"],
        "member_count": 600000,
        "services_contracted": ["All HAVEN"],
        "contract_status": "Target",
        "credentialing_status": "Not Started",
        "notes": "BCBS TX is part of HCSC, largest customer-owned health insurer in US.",
    },
    {
        "mco_name": "Community First Health Plans",
        "parent_company": "University Health (San Antonio)",
        "state": "TX",
        "program_type": ["Medicaid", "CHIP"],
        "member_count": 350000,
        "services_contracted": ["All HAVEN"],
        "contract_status": "Target",
        "credentialing_status": "Not Started",
        "notes": "San Antonio/Bexar County focus. Provider-sponsored by University Health.",
    },
    {
        "mco_name": "Driscoll Health Plan",
        "parent_company": "Driscoll Children's Hospital",
        "state": "TX",
        "program_type": ["Medicaid", "CHIP"],
        "member_count": 250000,
        "services_contracted": ["All HAVEN"],
        "contract_status": "Target",
        "credentialing_status": "Not Started",
        "notes": "South Texas / Coastal Bend focus. Pediatric emphasis — disaster evacuation angle.",
    },
    {
        "mco_name": "El Paso First Health Plans",
        "parent_company": "El Paso First (Independent)",
        "state": "TX",
        "program_type": ["Medicaid", "CHIP"],
        "member_count": 200000,
        "services_contracted": ["All HAVEN"],
        "contract_status": "Target",
        "credentialing_status": "Not Started",
        "notes": "El Paso County focus. Border region — unique disaster considerations.",
    },
    {
        "mco_name": "Texas Children's Health Plan",
        "parent_company": "Texas Children's Hospital",
        "state": "TX",
        "program_type": ["Medicaid", "CHIP"],
        "member_count": 500000,
        "services_contracted": ["All HAVEN"],
        "contract_status": "Target",
        "credentialing_status": "Not Started",
        "notes": "Houston metro focus. Children's hospital-sponsored — pediatric disaster needs.",
    },
    {
        "mco_name": "Sendero Health Plans",
        "parent_company": "Central Health (Travis County)",
        "state": "TX",
        "program_type": ["Medicaid"],
        "member_count": 150000,
        "services_contracted": ["All HAVEN"],
        "contract_status": "Target",
        "credentialing_status": "Not Started",
        "notes": "Austin/Travis County focus. Provider-sponsored by Central Health.",
    },
    {
        "mco_name": "Parkland Community Health Plan",
        "parent_company": "Parkland Health",
        "state": "TX",
        "program_type": ["Medicaid", "CHIP"],
        "member_count": 300000,
        "services_contracted": ["All HAVEN"],
        "contract_status": "Target",
        "credentialing_status": "Not Started",
        "notes": "Dallas County focus. Provider-sponsored by Parkland Hospital.",
    },
    {
        "mco_name": "Cook Children's Health Plan",
        "parent_company": "Cook Children's Medical Center",
        "state": "TX",
        "program_type": ["Medicaid", "CHIP"],
        "member_count": 200000,
        "services_contracted": ["All HAVEN"],
        "contract_status": "Target",
        "credentialing_status": "Not Started",
        "notes": "Fort Worth/Tarrant County focus. Pediatric emphasis.",
    },
    {
        "mco_name": "FirstCare Health Plans",
        "parent_company": "Covenant Health System",
        "state": "TX",
        "program_type": ["Medicaid", "CHIP"],
        "member_count": 150000,
        "services_contracted": ["All HAVEN"],
        "contract_status": "Target",
        "credentialing_status": "Not Started",
        "notes": "West Texas/Lubbock focus. Rural coverage important for disaster response.",
    },
    {
        "mco_name": "Scott & White Health Plan",
        "parent_company": "Baylor Scott & White Health",
        "state": "TX",
        "program_type": ["Medicaid", "CHIP"],
        "member_count": 250000,
        "services_contracted": ["All HAVEN"],
        "contract_status": "Target",
        "credentialing_status": "Not Started",
        "notes": "Central Texas focus. Large integrated health system.",
    },
    
    # ─── LOUISIANA — Humana (was missing) ───────────────────────────────────
    {
        "mco_name": "Humana Healthy Horizons Louisiana",
        "parent_company": "Humana",
        "state": "LA",
        "program_type": ["Medicaid"],
        "member_count": 300000,
        "services_contracted": ["All HAVEN"],
        "contract_status": "Target",
        "credentialing_status": "Not Started",
        "notes": "Humana entered LA Medicaid. Sister: Humana Healthy Horizons FL.",
    },
]

# MCO to DELETE (UHC Louisiana dropped as of April 2026 per LDH)
MCO_TO_DELETE = "UnitedHealthcare Community Plan Louisiana"


def get_existing_records() -> dict[str, str]:
    """Return dict of MCO name -> record ID."""
    url = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_NAME}"
    params = {"fields[]": "mco_name"}
    records = {}
    
    offset = None
    while True:
        if offset:
            params["offset"] = offset
        r = requests.get(url, headers=HEADERS, params=params, timeout=20)
        if not r.ok:
            break
        data = r.json()
        for rec in data.get("records", []):
            name = rec["fields"].get("mco_name", "")
            records[name] = rec["id"]
        offset = data.get("offset")
        if not offset:
            break
    return records


def create_record(fields: dict) -> bool:
    url = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_NAME}"
    payload = {"records": [{"fields": fields}]}
    r = requests.post(url, headers=HEADERS, json=payload, timeout=20)
    if not r.ok:
        print(f"    ✗ {fields.get('mco_name')}: {r.status_code} {r.text[:200]}")
        return False
    print(f"  ✓ Added: {fields.get('mco_name')} ({fields.get('state')})")
    return True


def delete_record(record_id: str, name: str) -> bool:
    url = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_NAME}/{record_id}"
    r = requests.delete(url, headers=HEADERS, timeout=20)
    if not r.ok:
        print(f"    ✗ Delete {name}: {r.status_code}")
        return False
    print(f"  ✓ Deleted: {name} (dropped by LDH April 2026)")
    return True


def main() -> None:
    if not API_KEY or not BASE_ID:
        print("✗ Missing AIRTABLE_API_KEY or HAVEN_BASE_ID in .env")
        sys.exit(1)

    print("\n══════════════════════════════════════════════════════")
    print("  HAVEN — Complete MCO Database Update")
    print(f"  Base: {BASE_ID}")
    print("══════════════════════════════════════════════════════\n")

    # Get existing records
    print("Fetching existing MCOs …")
    existing = get_existing_records()
    print(f"  Found {len(existing)} existing MCO(s)")

    # Delete UHC Louisiana (dropped April 2026)
    print("\nChecking for MCOs to remove …")
    if MCO_TO_DELETE in existing:
        delete_record(existing[MCO_TO_DELETE], MCO_TO_DELETE)
        del existing[MCO_TO_DELETE]
    else:
        print(f"  – {MCO_TO_DELETE} not found (already removed or never added)")

    # Add new MCOs
    print("\nAdding additional MCOs …")
    created = 0
    skipped = 0
    
    for mco in ADDITIONAL_MCOS:
        if mco["mco_name"] in existing:
            print(f"  – {mco['mco_name']} already exists, skipping")
            skipped += 1
            continue
        
        if create_record(mco):
            created += 1
        time.sleep(0.25)

    # Final count
    print(f"\n══════════════════════════════════════════════════════")
    print(f"  COMPLETE.")
    print(f"  Added: {created}")
    print(f"  Skipped: {skipped}")
    print(f"  Deleted: 1 (UHC Louisiana)")
    print(f"  Total MCOs in database: {len(existing) + created}")
    
    # State breakdown
    print(f"\n  Final breakdown by state:")
    
    # Re-fetch for accurate count
    final = get_existing_records()
    by_state: dict[str, int] = {}
    
    # We need to fetch full records to count by state
    url = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_NAME}"
    params = {"fields[]": "state"}
    offset = None
    while True:
        if offset:
            params["offset"] = offset
        r = requests.get(url, headers=HEADERS, params=params, timeout=20)
        if not r.ok:
            break
        data = r.json()
        for rec in data.get("records", []):
            st = rec["fields"].get("state", "Unknown")
            by_state[st] = by_state.get(st, 0) + 1
        offset = data.get("offset")
        if not offset:
            break
    
    for st, count in sorted(by_state.items()):
        print(f"    • {st}: {count} MCOs")
    
    print(f"\n══════════════════════════════════════════════════════\n")


if __name__ == "__main__":
    main()
