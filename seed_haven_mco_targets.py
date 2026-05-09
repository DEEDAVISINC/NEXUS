"""
HAVEN — Seed MCO Targets
Populates MCO_Contracts table with FL/TX/LA Medicaid MCO targets
plus HAP CareSource (MI) as the credibility reference.

Run:  python3 seed_haven_mco_targets.py
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
# MCO Target Data
# ─────────────────────────────────────────────────────────────────────────────

MCO_TARGETS = [
    # ─── MICHIGAN (Credibility Reference) ───────────────────────────────────
    {
        "mco_name": "HAP CareSource",
        "parent_company": "CareSource",
        "state": "MI",
        "program_type": ["Medicaid"],
        "member_count": 4500,
        "contact_name": "Brian Grcevich",
        "contact_email": "Brian.Grcevich@CareSource.com",
        "services_contracted": ["NEMT"],
        "contract_status": "Active",
        "credentialing_status": "Complete",
        "portal_access": True,
        "notes": "LIVE as of May 6, 2026. Vendor ID: 100000469269. Rates: $28 standard, $35 ambulatory/wheelchair. INSTANT CREDIBILITY for HAVEN pitches.",
    },
    
    # ─── FLORIDA MCOs ───────────────────────────────────────────────────────
    {
        "mco_name": "Sunshine Health",
        "parent_company": "Centene",
        "state": "FL",
        "program_type": ["Medicaid", "Medicare Advantage"],
        "member_count": 2000000,
        "services_contracted": ["All HAVEN"],
        "contract_status": "Target",
        "credentialing_status": "Not Started",
        "notes": "Largest FL Medicaid MCO. Centene family — same parent as HAP CareSource.",
    },
    {
        "mco_name": "Molina Healthcare of Florida",
        "parent_company": "Molina Healthcare",
        "state": "FL",
        "program_type": ["Medicaid", "Medicare Advantage"],
        "member_count": 1500000,
        "services_contracted": ["All HAVEN"],
        "contract_status": "Target",
        "credentialing_status": "Not Started",
        "notes": "Major FL presence. Molina is also in TX and LA — potential multi-state relationship.",
    },
    {
        "mco_name": "Simply Healthcare",
        "parent_company": "Anthem / Elevance Health",
        "state": "FL",
        "program_type": ["Medicaid", "Medicare Advantage"],
        "member_count": 1000000,
        "services_contracted": ["All HAVEN"],
        "contract_status": "Target",
        "credentialing_status": "Not Started",
        "notes": "Anthem/Elevance family. Sister MCOs: Amerigroup TX, Healthy Blue LA.",
    },
    {
        "mco_name": "Humana Healthy Horizons Florida",
        "parent_company": "Humana",
        "state": "FL",
        "program_type": ["Medicaid", "Medicare Advantage", "Dual Eligible"],
        "member_count": 800000,
        "services_contracted": ["All HAVEN"],
        "contract_status": "Target",
        "credentialing_status": "Not Started",
        "notes": "Strong Medicare Advantage presence. Dual eligible population = high disaster vulnerability.",
    },
    {
        "mco_name": "Aetna Better Health of Florida",
        "parent_company": "CVS / Aetna",
        "state": "FL",
        "program_type": ["Medicaid"],
        "member_count": 600000,
        "services_contracted": ["All HAVEN"],
        "contract_status": "Target",
        "credentialing_status": "Not Started",
        "notes": "CVS integration could help with Rx continuity angle.",
    },
    {
        "mco_name": "Florida Community Care",
        "parent_company": "Independent",
        "state": "FL",
        "program_type": ["Medicaid"],
        "member_count": 400000,
        "services_contracted": ["All HAVEN"],
        "contract_status": "Target",
        "credentialing_status": "Not Started",
        "notes": "Provider-sponsored plan. May be more nimble than nationals.",
    },
    
    # ─── TEXAS MCOs ─────────────────────────────────────────────────────────
    {
        "mco_name": "Superior HealthPlan",
        "parent_company": "Centene",
        "state": "TX",
        "program_type": ["Medicaid", "CHIP"],
        "member_count": 2000000,
        "services_contracted": ["All HAVEN"],
        "contract_status": "Target",
        "credentialing_status": "Not Started",
        "notes": "Largest TX Medicaid MCO. Centene family — same parent as HAP CareSource.",
    },
    {
        "mco_name": "Molina Healthcare of Texas",
        "parent_company": "Molina Healthcare",
        "state": "TX",
        "program_type": ["Medicaid", "CHIP", "Medicare Advantage"],
        "member_count": 1500000,
        "services_contracted": ["All HAVEN"],
        "contract_status": "Target",
        "credentialing_status": "Not Started",
        "notes": "Multi-state relationship potential with Molina FL and LA.",
    },
    {
        "mco_name": "UnitedHealthcare Community Plan Texas",
        "parent_company": "UnitedHealth Group",
        "state": "TX",
        "program_type": ["Medicaid", "CHIP", "Dual Eligible"],
        "member_count": 1200000,
        "services_contracted": ["All HAVEN"],
        "contract_status": "Target",
        "credentialing_status": "Not Started",
        "notes": "UHC is also in LA. National relationship potential.",
    },
    {
        "mco_name": "Amerigroup Texas",
        "parent_company": "Anthem / Elevance Health",
        "state": "TX",
        "program_type": ["Medicaid", "CHIP"],
        "member_count": 1000000,
        "services_contracted": ["All HAVEN"],
        "contract_status": "Target",
        "credentialing_status": "Not Started",
        "notes": "Anthem/Elevance family. Sister MCOs: Simply Healthcare FL, Healthy Blue LA.",
    },
    {
        "mco_name": "Community Health Choice",
        "parent_company": "Independent (Harris Health System)",
        "state": "TX",
        "program_type": ["Medicaid", "CHIP"],
        "member_count": 500000,
        "services_contracted": ["All HAVEN"],
        "contract_status": "Target",
        "credentialing_status": "Not Started",
        "notes": "Houston-focused. Provider-sponsored plan.",
    },
    {
        "mco_name": "Dell Children's Health Plan",
        "parent_company": "Seton / Ascension",
        "state": "TX",
        "program_type": ["Medicaid", "CHIP"],
        "member_count": 300000,
        "services_contracted": ["All HAVEN"],
        "contract_status": "Target",
        "credentialing_status": "Not Started",
        "notes": "Austin-focused. Pediatric emphasis — family disaster services angle.",
    },
    
    # ─── LOUISIANA MCOs ─────────────────────────────────────────────────────
    {
        "mco_name": "Louisiana Healthcare Connections",
        "parent_company": "Centene",
        "state": "LA",
        "program_type": ["Medicaid"],
        "member_count": 500000,
        "services_contracted": ["All HAVEN"],
        "contract_status": "Target",
        "credentialing_status": "Not Started",
        "notes": "Centene family — same parent as HAP CareSource and Superior HealthPlan.",
    },
    {
        "mco_name": "Healthy Blue Louisiana",
        "parent_company": "Anthem / Elevance Health",
        "state": "LA",
        "program_type": ["Medicaid"],
        "member_count": 450000,
        "services_contracted": ["All HAVEN"],
        "contract_status": "Target",
        "credentialing_status": "Not Started",
        "notes": "Anthem/Elevance family. Sister MCOs: Simply Healthcare FL, Amerigroup TX.",
    },
    {
        "mco_name": "AmeriHealth Caritas Louisiana",
        "parent_company": "AmeriHealth Caritas",
        "state": "LA",
        "program_type": ["Medicaid"],
        "member_count": 400000,
        "services_contracted": ["All HAVEN"],
        "contract_status": "Target",
        "credentialing_status": "Not Started",
        "notes": "Strong Medicaid focus. AmeriHealth Caritas also in other states.",
    },
    {
        "mco_name": "Aetna Better Health of Louisiana",
        "parent_company": "CVS / Aetna",
        "state": "LA",
        "program_type": ["Medicaid"],
        "member_count": 350000,
        "services_contracted": ["All HAVEN"],
        "contract_status": "Target",
        "credentialing_status": "Not Started",
        "notes": "CVS integration for Rx continuity. Sister: Aetna Better Health FL.",
    },
    {
        "mco_name": "UnitedHealthcare Community Plan Louisiana",
        "parent_company": "UnitedHealth Group",
        "state": "LA",
        "program_type": ["Medicaid"],
        "member_count": 300000,
        "services_contracted": ["All HAVEN"],
        "contract_status": "Target",
        "credentialing_status": "Not Started",
        "notes": "UHC national network. Sister: UHC Community Plan TX.",
    },
]


def get_existing_records() -> set[str]:
    """Return set of existing MCO names to avoid duplicates."""
    url = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_NAME}"
    params = {"fields[]": "mco_name"}
    r = requests.get(url, headers=HEADERS, params=params, timeout=20)
    if not r.ok:
        return set()
    return {rec["fields"].get("mco_name", "") for rec in r.json().get("records", [])}


def create_record(fields: dict) -> bool:
    url = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_NAME}"
    payload = {"records": [{"fields": fields}]}
    r = requests.post(url, headers=HEADERS, json=payload, timeout=20)
    if not r.ok:
        print(f"    ✗ {fields.get('mco_name')}: {r.status_code} {r.text[:200]}")
        return False
    print(f"  ✓ {fields.get('mco_name')} ({fields.get('state')})")
    return True


def main() -> None:
    if not API_KEY:
        print("✗ AIRTABLE_API_KEY not found in .env. Aborting.")
        sys.exit(1)
    if not BASE_ID:
        print("✗ HAVEN_BASE_ID not found in .env. Run create_haven_airtable_base.py first.")
        sys.exit(1)

    print("\n══════════════════════════════════════════════════════")
    print("  HAVEN — Seed MCO Targets")
    print(f"  Base: {BASE_ID}")
    print(f"  Table: {TABLE_NAME}")
    print("══════════════════════════════════════════════════════\n")

    # Check for existing records
    print("Checking for existing records …")
    existing = get_existing_records()
    print(f"  Found {len(existing)} existing MCO(s)")

    # Create records
    print("\nSeeding MCO targets …")
    created = 0
    skipped = 0
    
    for mco in MCO_TARGETS:
        if mco["mco_name"] in existing:
            print(f"  – {mco['mco_name']} already exists, skipping")
            skipped += 1
            continue
        
        if create_record(mco):
            created += 1
        time.sleep(0.25)  # rate limit

    print(f"\n══════════════════════════════════════════════════════")
    print(f"  DONE.")
    print(f"  Created: {created}")
    print(f"  Skipped: {skipped}")
    print(f"  Total MCOs in database: {len(existing) + created}")
    print(f"\n  Breakdown by state:")
    
    by_state = {}
    for mco in MCO_TARGETS:
        st = mco["state"]
        by_state[st] = by_state.get(st, 0) + 1
    for st, count in sorted(by_state.items()):
        print(f"    • {st}: {count} MCOs")
    
    print(f"\n  Next steps:")
    print(f"    1. Open Airtable and review MCO_Contracts table")
    print(f"    2. Research specific contacts at each MCO")
    print(f"    3. Begin outreach sequence (after foreign corp registration)")
    print(f"══════════════════════════════════════════════════════\n")


if __name__ == "__main__":
    main()
