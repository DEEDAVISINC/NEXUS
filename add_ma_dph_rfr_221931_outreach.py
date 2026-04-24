#!/usr/bin/env python3
"""
MA DPH RFR 221931 — Courier Services
Adds opportunity metadata + buyer contacts to NEXUS (Airtable) and updates tracked_state_opportunities.json.
"""

import json
import os
from datetime import date
from pathlib import Path

from dotenv import load_dotenv
from pyairtable import Api

load_dotenv()

REPO = Path(__file__).resolve().parent
TRACKED_JSON = REPO / "tracked_state_opportunities.json"

AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY")
AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID")
CONTACTS_TABLE = "GPSS CONTACTS"
OPPORTUNITIES_TABLE = "GPSS OPPORTUNITIES"


def load_tracked() -> dict:
    if not TRACKED_JSON.is_file():
        return {"version": 1, "updated": str(date.today()), "opportunities": []}
    with open(TRACKED_JSON, "r", encoding="utf-8") as f:
        return json.load(f)


def save_tracked(data: dict) -> None:
    data["updated"] = str(date.today())
    with open(TRACKED_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def ensure_opportunity_in_json() -> None:
    """Idempotent: MA DPH RFR 221931 block is the canonical entry in tracked_state_opportunities.json."""
    data = load_tracked()
    ids = {o.get("id") for o in data.get("opportunities", [])}
    if "ma-dph-rfr-221931-courier" in ids:
        return
    # Should already exist from repo seed; if missing, append minimal stub
    data.setdefault("opportunities", []).append(
        {
            "id": "ma-dph-rfr-221931-courier",
            "title": "Courier Services",
            "rfr_number": "RFR 221931",
            "opportunity_identifier": "BD-21-1031-ADMIN-ADM08-60554",
            "notes": "Seeded from add_ma_dph_rfr_221931_outreach.py — fill from tracked file or portal.",
        }
    )
    save_tracked(data)


def add_or_update_contacts(api: Api) -> None:
    table = api.table(AIRTABLE_BASE_ID, CONTACTS_TABLE)

    contacts = [
        {
            "Name": "David Harvey",
            "Email": "david.harvey@mass.gov",
            "Title": "MA DPH — Contact (RFR 221931 Courier Services)",
            "Organization": "Massachusetts Department of Public Health (DPH)",
            "Role Category": "Buyer",
            "Notes": "Listed contact on RFR 221931 Courier Services. Opportunity ID BD-21-1031-ADMIN-ADM08-60554. Use registered-vendor follow-up tone (MA state). Added 2026-04-23.",
        },
        {
            "Name": "Elizabeth Nguyen-Vu",
            "Email": "dphprocurementteam@state.ma.us",
            "Title": "Purchaser, DPH Procurement — Phone: 617-624-5800",
            "Organization": "Massachusetts Department of Public Health (DPH)",
            "Role Category": "Buyer",
            "Notes": "Purchaser for RFR 221931 Courier Services. Team inbox dphprocurementteam@state.ma.us. Listing due / contract horizon 2031-06-30 (long-range monitor). Added 2026-04-23.",
        },
    ]

    for row in contacts:
        email = row["Email"]
        formula = f"{{Email}} = '{email}'"
        try:
            existing = table.all(formula=formula, max_records=1)
        except Exception:
            existing = []
        if existing:
            table.update(existing[0]["id"], row)
            print(f"✅ Updated contact: {row['Name']} <{email}>")
        else:
            table.create(row)
            print(f"✅ Added contact: {row['Name']} <{email}>")


def add_opportunity_if_absent(api: Api) -> None:
    table = api.table(AIRTABLE_BASE_ID, OPPORTUNITIES_TABLE)
    sol = "RFR 221931"
    try:
        # Airtable: single braces around field name — use {{ in f-string for literal { }
        formula = f"{{RFP NUMBER}} = '{sol}'"
        existing = table.all(formula=formula, max_records=3)
    except Exception as e:
        print(f"⚠️  Could not query opportunities by RFP (field name may differ): {e}")
        existing = []

    if existing:
        print(f"⏭️  GPSS OPPORTUNITIES already has RFR 221931 — skipping create ({len(existing)} match(es)).")
        return

    row = {
        "Name": "MA DPH — RFR 221931 Courier Services (Long-range monitor; due 2031-06-30)",
        "RFP NUMBER": sol,
        "Deadline": "2031-06-30",
        "Source Status": "Monitoring",
    }
    try:
        table.create(row)
        print("✅ Added opportunity to GPSS OPPORTUNITIES: RFR 221931")
    except Exception as e:
        err = str(e)
        if "Unknown field" in err or "INVALID_MULTIPLE_CHOICE_OPTIONS" in err or "SINGLE_SELECT" in err:
            row_alt = {
                "Name": row["Name"],
                "RFP NUMBER": sol,
                "Deadline": "2031-06-30",
                "Source Status": "Active",
            }
            try:
                table.create(row_alt)
                print("✅ Added opportunity (fallback Source Status=Active).")
            except Exception as e2:
                print(f"❌ Could not add opportunity: {e2}")
        else:
            print(f"❌ Could not add opportunity: {e}")


def main() -> None:
    print("\n" + "=" * 72)
    print("MA DPH RFR 221931 — NEXUS intake (local JSON + Airtable)")
    print("=" * 72 + "\n")

    ensure_opportunity_in_json()
    print(f"📁 Local: {TRACKED_JSON.name}")

    if not AIRTABLE_API_KEY or not AIRTABLE_BASE_ID:
        print("⚠️  AIRTABLE_API_KEY or AIRTABLE_BASE_ID not set — skipped Airtable sync.")
        return

    api = Api(AIRTABLE_API_KEY)
    add_or_update_contacts(api)
    add_opportunity_if_absent(api)
    print("\nDone.\n")


if __name__ == "__main__":
    main()
