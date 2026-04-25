#!/usr/bin/env python3
"""Contra Costa BH DMC-ODS — Recovery vendor pool SOQ (RFQ_QUAL_F-Contr-0000000039) → GPSS OPPORTUNITIES."""

import os
from pathlib import Path

from dotenv import load_dotenv
from pyairtable import Api

load_dotenv()

AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY")
AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID")
OPPORTUNITIES_TABLE = "GPSS OPPORTUNITIES"

SOL = "RFQ_QUAL_F-Contr-0000000039"


def main() -> None:
    print("CCC Recovery / Employment Vendor Pool SOQ — Airtable\n")
    if not AIRTABLE_API_KEY or not AIRTABLE_BASE_ID:
        print("⚠️  Missing AIRTABLE creds; skipped.")
        return
    api = Api(AIRTABLE_API_KEY)
    table = api.table(AIRTABLE_BASE_ID, OPPORTUNITIES_TABLE)
    formula = f"{{RFP NUMBER}} = '{SOL}'"
    try:
        existing = table.all(formula=formula, max_records=3)
    except Exception as e:
        print(f"⚠️  Lookup error: {e}")
        existing = []
    if existing:
        print(f"⏭️  Already present: {SOL} ({len(existing)})")
        return
    row = {
        "Name": "Contra Costa BH — Recovery Residences / Employment Vendor Pool SOQ (2026-04-27 PDT)",
        "RFP NUMBER": SOL,
        "Deadline": "2026-04-27",
        "Source Status": "Active",
    }
    try:
        table.create(row)
        print(f"✅ Added: {SOL}")
    except Exception as e:
        err = str(e)
        if "INVALID_MULTIPLE_CHOICE" in err or "SINGLE_SELECT" in err:
            row["Source Status"] = "Monitoring"
            table.create(row)
            print("✅ Added (Monitoring)")
        else:
            print(f"❌ {e}")


if __name__ == "__main__":
    main()
