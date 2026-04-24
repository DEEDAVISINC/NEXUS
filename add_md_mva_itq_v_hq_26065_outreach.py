#!/usr/bin/env python3
"""
MD MVA ITQ V-HQ-26065-S — Courier Services
Adds procurement contact + opportunity row to Airtable (see tracked_state_opportunities.json for full ITQ text).
ITQ: no-cost to state; application due 2026-05-06 1:00 PM ET.
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from pyairtable import Api

load_dotenv()

REPO = Path(__file__).resolve().parent

AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY")
AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID")
CONTACTS_TABLE = "GPSS CONTACTS"
OPPORTUNITIES_TABLE = "GPSS OPPORTUNITIES"

SOL = "V-HQ-26065-S"


def add_or_update_contact(api: Api) -> None:
    table = api.table(AIRTABLE_BASE_ID, CONTACTS_TABLE)
    row = {
        "Name": "Gayloy Martin",
        "Email": "gmartin5@mdot.maryland.gov",
        "Title": f"MVA Procurement Officer — ITQ {SOL} Courier — 410-768-7640",
        "Organization": "Maryland Motor Vehicle Administration (MVA) / MDOT",
        "Role Category": "Buyer",
        "Notes": "ITQ V-HQ-26065-S Courier Services (eMMA). questions by 2026-04-21 1pm ET; applications due 2026-05-06 1pm ET. No-cost to state model — couriers paid by dealers/ERT. Ritchie Hwy Glen Burnie. Added 2026-04-23 from ITQ PDF.",
    }
    formula = f"{{Email}} = 'gmartin5@mdot.maryland.gov'"
    existing = table.all(formula=formula, max_records=1)
    if existing:
        table.update(existing[0]["id"], row)
        print(f"✅ Updated contact: {row['Name']}")
    else:
        table.create(row)
        print(f"✅ Added contact: {row['Name']}")


def add_opportunity_if_absent(api: Api) -> None:
    table = api.table(AIRTABLE_BASE_ID, OPPORTUNITIES_TABLE)
    formula = f"{{RFP NUMBER}} = '{SOL}'"
    try:
        existing = table.all(formula=formula, max_records=3)
    except Exception as e:
        print(f"⚠️  Opportunity lookup failed: {e}")
        existing = []
    if existing:
        print(f"⏭️  GPSS OPPORTUNITIES already has {SOL} — skip ({len(existing)}).")
        return
    row = {
        "Name": f"MD MVA — ITQ {SOL} Courier (no-cost to state; due 2026-05-06 1pm ET)",
        "RFP NUMBER": SOL,
        "Deadline": "2026-05-06",
        "Source Status": "Active",
    }
    try:
        table.create(row)
        print(f"✅ Added opportunity: {SOL}")
    except Exception as e:
        err = str(e)
        if "INVALID_MULTIPLE_CHOICE" in err or "SINGLE_SELECT" in err:
            row["Source Status"] = "Monitoring"
            try:
                table.create(row)
                print(f"✅ Added opportunity (Monitoring): {SOL}")
            except Exception as e2:
                print(f"❌ {e2}")
        else:
            print(f"❌ {e}")


def main() -> None:
    print("MD MVA ITQ V-HQ-26065-S — Airtable sync\n")
    if not AIRTABLE_API_KEY or not AIRTABLE_BASE_ID:
        print("⚠️  Missing AIRTABLE creds; skipped.")
        return
    api = Api(AIRTABLE_API_KEY)
    add_or_update_contact(api)
    add_opportunity_if_absent(api)
    print("Done.")


if __name__ == "__main__":
    main()
