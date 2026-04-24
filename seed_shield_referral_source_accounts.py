"""
SHIELD — Referral Source Accounts seed

Populates the `Referral_Source_Accounts` Airtable table (base:
nexus_lead_screening) with the two confirmed MDHHS Environmental Health Bureau
contacts from the Apr 23, 2026 meeting, plus six Local Health Department (LHD)
director placeholder rows for the counties MDHHS committed to introduce us to.

Usage
─────
    python seed_shield_referral_source_accounts.py            # default: dry run
    python seed_shield_referral_source_accounts.py --apply    # actually upsert

Safety
──────
- Idempotent: looks up by email before creating. Updates in place if the record
  exists (so re-running never duplicates contacts).
- Uses the same `ShieldAirtableClient` the runtime API uses — so if SHIELD is
  configured, this script works; if not, it prints a clear hint and exits 0.
- Dry-run mode prints exactly what would be upserted without touching Airtable.

After running
─────────────
1. Verify rows exist in Airtable → nexus_lead_screening → Referral_Source_Accounts
2. As MDHHS-facilitated LHD introductions arrive, UPDATE the placeholder rows
   with the real director's name, email, and phone.
3. If the table is missing columns, the script reports which ones. Add the
   missing columns in Airtable, re-run.
"""

from __future__ import annotations

import argparse
import os
import sys
from typing import Any, Dict, List, Optional

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))
except ImportError:
    pass

from shield_lead_screening import (  # noqa: E402
    ShieldAirtableClient,
    TABLE_SOURCE_ACCOUNTS,
    _safe_all,
    _now_eastern_iso,
)


# ─────────────────────────────────────────────────────────────────────────────
# Seed definitions — post-Apr 23 MDHHS meeting
# ─────────────────────────────────────────────────────────────────────────────
MDHHS_CONTACTS: List[Dict[str, Any]] = [
    {
        "account_name": "MDHHS — Environmental Health Bureau (Care Coordination)",
        "agency_type": "State Agency",
        "county": "Statewide",
        "contact_name": "Angela Medina",
        "contact_title": "Care Coordination Section Manager, Division of Environmental Community Services",
        "contact_email": "MedinaA@michigan.gov",
        "contact_phone": "517-897-5203",
        "relationship_tier": "Primary — Decision Maker",
        "status": "Active",
        "first_contact_date": "2026-04-23",
        "notes": (
            "Met Apr 23, 2026 (3:00–3:30 PM ET, Teams). Received CWC+DDI navigation + "
            "program admin partnership model favorably. Confirmed timing is 'perfect' "
            "given PA 146 of 2023. Committed to LHD director intros in 6 counties. "
            "Brief + one-pager sent 4/23 at 7:04 PM. Follow-up meeting owed within 2 weeks. "
            "Reference: CWC_DDI_MDHHS_Meeting_Brief.pdf"
        ),
    },
    {
        "account_name": "MDHHS — Environmental Health Bureau",
        "agency_type": "State Agency",
        "county": "Statewide",
        "contact_name": "Aimee Surma",
        "contact_title": "Environmental Health Bureau",
        "contact_email": "SurmaA@michigan.gov",
        "contact_phone": "",
        "relationship_tier": "Secondary",
        "status": "Active",
        "first_contact_date": "2026-04-23",
        "notes": (
            "Met Apr 23, 2026 (3:00–3:30 PM ET, Teams). Sent follow-up email the same "
            "evening with MiLeadSafe + Apply for Home Lead Services links. Surfaced the "
            "housing + food navigation need during abatement discussion — personal emphasis. "
            "Brief + one-pager sent 4/23 at 7:04 PM."
        ),
    },
]

# MDHHS committed to introduce CWC+DDI to LHD directors in these six counties.
# Create placeholders now so inbound intros have a home and everyone on the team
# knows an intro is expected. Update in place when the real director is known.
LHD_PLACEHOLDERS: List[Dict[str, Any]] = [
    {
        "account_name": "Wayne County Health Department (pending MDHHS intro)",
        "agency_type": "Local Health Department",
        "county": "Wayne",
        "contact_name": "(pending — MDHHS-facilitated intro)",
        "contact_title": "Health Department Director",
        "contact_email": "",
        "contact_phone": "",
        "relationship_tier": "Pending Introduction",
        "status": "Pending",
        "notes": "MDHHS committed 4/23/2026 to share CWC+DDI brief + one-pager with the Wayne County LHD director and facilitate an intro once reviewed. Update this record when the real director name/contact arrives.",
    },
    {
        "account_name": "Oakland County Health Department (pending MDHHS intro)",
        "agency_type": "Local Health Department",
        "county": "Oakland",
        "contact_name": "(pending — MDHHS-facilitated intro)",
        "contact_title": "Health Department Director",
        "contact_email": "",
        "contact_phone": "",
        "relationship_tier": "Pending Introduction",
        "status": "Pending",
        "notes": "MDHHS committed 4/23/2026 to share CWC+DDI brief + one-pager with the Oakland County LHD director and facilitate an intro once reviewed.",
    },
    {
        "account_name": "Macomb County Health Department (pending MDHHS intro)",
        "agency_type": "Local Health Department",
        "county": "Macomb",
        "contact_name": "(pending — MDHHS-facilitated intro)",
        "contact_title": "Health Department Director",
        "contact_email": "",
        "contact_phone": "",
        "relationship_tier": "Pending Introduction",
        "status": "Pending",
        "notes": "MDHHS committed 4/23/2026 to share CWC+DDI brief + one-pager with the Macomb County LHD director and facilitate an intro once reviewed.",
    },
    {
        "account_name": "Genesee County Health Department (pending MDHHS intro)",
        "agency_type": "Local Health Department",
        "county": "Genesee",
        "contact_name": "(pending — MDHHS-facilitated intro)",
        "contact_title": "Health Department Director",
        "contact_email": "",
        "contact_phone": "",
        "relationship_tier": "Pending Introduction",
        "status": "Pending",
        "notes": "MDHHS committed 4/23/2026 to share CWC+DDI brief + one-pager with the Genesee County LHD director and facilitate an intro once reviewed. Flint water context makes this a high-priority follow-up.",
    },
    {
        "account_name": "Kent County Health Department — Grand Rapids (pending MDHHS intro)",
        "agency_type": "Local Health Department",
        "county": "Kent",
        "contact_name": "(pending — MDHHS-facilitated intro)",
        "contact_title": "Health Department Director",
        "contact_email": "",
        "contact_phone": "",
        "relationship_tier": "Pending Introduction",
        "status": "Pending",
        "notes": "MDHHS committed 4/23/2026 to share CWC+DDI brief + one-pager with the Kent County (Grand Rapids) LHD director and facilitate an intro once reviewed.",
    },
    {
        "account_name": "Muskegon County Health Department (pending MDHHS intro)",
        "agency_type": "Local Health Department",
        "county": "Muskegon",
        "contact_name": "(pending — MDHHS-facilitated intro)",
        "contact_title": "Health Department Director",
        "contact_email": "",
        "contact_phone": "",
        "relationship_tier": "Pending Introduction",
        "status": "Pending",
        "notes": "MDHHS committed 4/23/2026 to share CWC+DDI brief + one-pager with the Muskegon County LHD director and facilitate an intro once reviewed.",
    },
]


def _find_existing(
    existing: List[Dict[str, Any]], email: str, fallback_name: str
) -> Optional[Dict[str, Any]]:
    """Find existing record by contact_email (primary) or account_name (fallback)."""
    email_n = (email or "").strip().lower()
    name_n = (fallback_name or "").strip().lower()
    for record in existing:
        fields = record.get("fields", {}) or {}
        rec_email = (fields.get("contact_email") or "").strip().lower()
        rec_name = (fields.get("account_name") or "").strip().lower()
        if email_n and rec_email and rec_email == email_n:
            return record
        if not email_n and name_n and rec_name == name_n:
            return record
    return None


def _stamp(fields: Dict[str, Any]) -> Dict[str, Any]:
    """Add last_updated timestamp if the table supports it."""
    return {**fields, "last_updated": _now_eastern_iso()}


def seed(apply_changes: bool) -> int:
    client = ShieldAirtableClient()
    if not client.is_configured:
        print(
            "SHIELD Airtable base is not configured. Set LEAD_SCREENING_BASE_ID (and "
            "AIRTABLE_API_KEY) in .env, then re-run.",
            file=sys.stderr,
        )
        return 0  # not an error — just not yet possible

    mode = "APPLY" if apply_changes else "DRY-RUN"
    print(f"[SHIELD seed · {mode}] Target table: {TABLE_SOURCE_ACCOUNTS}")
    print(f"[SHIELD seed · {mode}] Base ID: {client.base_id}")
    print()

    existing = _safe_all(client, TABLE_SOURCE_ACCOUNTS)
    print(f"[SHIELD seed] Found {len(existing)} existing rows in {TABLE_SOURCE_ACCOUNTS}.")
    print()

    created = 0
    updated = 0
    skipped = 0

    all_rows = MDHHS_CONTACTS + LHD_PLACEHOLDERS
    for row in all_rows:
        email = row.get("contact_email") or ""
        name = row.get("account_name") or ""
        match = _find_existing(existing, email, name)

        label = f"{row.get('county', '—')} · {row.get('contact_name') or row.get('account_name')}"

        if match:
            match_id = match.get("id")
            print(f"  ↻  UPDATE   {label}  (id={match_id})")
            if apply_changes:
                try:
                    client.update(TABLE_SOURCE_ACCOUNTS, match_id, _stamp(row))
                    updated += 1
                except Exception as exc:
                    print(f"     ⚠️  update failed: {exc}")
                    skipped += 1
            else:
                updated += 1
        else:
            print(f"  ✚  CREATE   {label}")
            if apply_changes:
                try:
                    client.create(TABLE_SOURCE_ACCOUNTS, _stamp(row))
                    created += 1
                except Exception as exc:
                    print(f"     ⚠️  create failed: {exc}")
                    skipped += 1
            else:
                created += 1

    print()
    print(f"[SHIELD seed · {mode}] Done. created={created}  updated={updated}  skipped={skipped}")
    if not apply_changes:
        print("[SHIELD seed] No changes applied. Re-run with --apply to write.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Seed SHIELD Referral_Source_Accounts.")
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Actually write changes to Airtable (default is dry-run).",
    )
    args = parser.parse_args()
    return seed(apply_changes=args.apply)


if __name__ == "__main__":
    sys.exit(main())
