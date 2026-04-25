#!/usr/bin/env python3
"""
SAM.gov Contracting Officer → GPSS CONTACTS sync.

Companion to mine_co_contacts.py: uses the same SAM.gov NAICS-based
pointOfContact extraction, but persists each CO to the GPSS CONTACTS
table (dedupe by email) so they become outreach-ready records instead
of a static markdown briefing.

Callable two ways:
  1) Import and call upsert_pocs_for_opp(opp_json, ...) from any miner
     that already has the raw SAM.gov response on hand.
  2) Run standalone / from the scheduler to batch-pull recent opps:
       python3 sam_co_contact_sync.py [--days 30] [--dry-run]
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

log = logging.getLogger("sam_co_contact_sync")

CONTACTS_TABLE = "GPSS CONTACTS"
MAX_WORKERS = 5


# ─────────────────────────────────────────────────────────────────────────────
# POC extraction (works on a single SAM.gov opportunity dict)
# ─────────────────────────────────────────────────────────────────────────────

def _poc_name(poc: Dict[str, Any]) -> str:
    name = (poc.get("fullName") or "").strip()
    if not name:
        first = (poc.get("firstName") or "").strip()
        last = (poc.get("lastName") or "").strip()
        name = f"{first} {last}".strip()
    return name


def extract_pocs(opp: Dict[str, Any]) -> List[Dict[str, str]]:
    """Normalize SAM.gov pointOfContact (list or dict) into a flat list."""
    raw = opp.get("pointOfContact") or []
    if isinstance(raw, dict):
        raw = [raw]
    if not isinstance(raw, list):
        return []

    out: List[Dict[str, str]] = []
    for poc in raw:
        if not isinstance(poc, dict):
            continue
        email = (poc.get("email") or "").strip().lower()
        if not email:
            # No email → can't dedupe reliably. SAM almost always has email for COs.
            continue
        out.append(
            {
                "name": _poc_name(poc) or "(name not provided)",
                "email": email,
                "phone": (poc.get("phone") or "").strip(),
                "fax": (poc.get("fax") or "").strip(),
                "title": (poc.get("title") or "").strip() or "Contracting Officer",
                "type": (poc.get("type") or "").strip().lower() or "primary",
            }
        )
    return out


# ─────────────────────────────────────────────────────────────────────────────
# Airtable upsert
# ─────────────────────────────────────────────────────────────────────────────

def _escape_formula(value: str) -> str:
    return value.replace("'", r"\'")


def _build_notes(poc: Dict[str, str], opp: Dict[str, Any]) -> str:
    title = (opp.get("title") or "").strip()
    sol = (opp.get("solicitationNumber") or "").strip()
    notice_id = (opp.get("noticeId") or "").strip()
    agency = (opp.get("fullParentPathName") or opp.get("department") or "").strip()
    set_aside = (
        opp.get("typeOfSetAsideDescription")
        or opp.get("typeOfSetAside")
        or ""
    ).strip()
    naics = (opp.get("naicsCode") or "").strip()
    deadline = (opp.get("responseDeadLine") or "")[:10]
    url = f"https://sam.gov/opp/{notice_id}/view" if notice_id else ""

    parts: List[str] = [
        "Auto-synced from SAM.gov pointOfContact.",
        f"Opportunity: {title}" if title else "",
        f"Solicitation: {sol}" if sol else "",
        f"Agency path: {agency}" if agency else "",
        f"NAICS: {naics}" if naics else "",
        f"Set-aside: {set_aside}" if set_aside else "",
        f"Response deadline: {deadline}" if deadline else "",
        f"URL: {url}" if url else "",
        f"POC type: {poc.get('type') or 'primary'}",
        f"Last sync: {datetime.now().strftime('%Y-%m-%d')}",
    ]
    return "\n".join(p for p in parts if p)


def _merge_notes(old: Optional[str], new: str, max_entries: int = 6) -> str:
    old = (old or "").strip()
    if not old:
        return new
    combined = f"{new}\n\n--- previous sync ---\n{old}"
    blocks = combined.split("\n\n--- previous sync ---\n")
    return "\n\n--- previous sync ---\n".join(blocks[:max_entries])[:8000]


def _contact_fields(poc: Dict[str, str], opp: Dict[str, Any]) -> Dict[str, Any]:
    agency = (
        opp.get("fullParentPathName")
        or opp.get("department")
        or "SAM.gov — agency TBD"
    ).strip()
    title = poc.get("title") or "Contracting Officer"
    phone = poc.get("phone") or ""
    return {
        "Name": poc["name"],
        "Email": poc["email"],
        "Title": title if not phone else f"{title} — {phone}",
        "Organization": agency,
        "Role Category": "Buyer",
        "Notes": _build_notes(poc, opp),
    }


def upsert_pocs_for_opp(
    opp: Dict[str, Any],
    airtable_client=None,
    dry_run: bool = False,
) -> Dict[str, int]:
    """Extract POCs from one opportunity dict and upsert into GPSS CONTACTS.

    Returns: {'extracted': n, 'created': n, 'updated': n, 'skipped': n}
    """
    stats = {"extracted": 0, "created": 0, "updated": 0, "skipped": 0}
    pocs = extract_pocs(opp)
    stats["extracted"] = len(pocs)
    if not pocs:
        return stats

    if dry_run or airtable_client is None:
        return stats

    for poc in pocs:
        email = poc["email"]
        try:
            formula = f"LOWER({{Email}}) = '{_escape_formula(email)}'"
            existing = airtable_client.search_records(CONTACTS_TABLE, formula)
        except Exception as e:
            log.warning("search failed for %s: %s", email, e)
            stats["skipped"] += 1
            continue

        fields = _contact_fields(poc, opp)
        try:
            if existing:
                rec_id = existing[0]["id"]
                fields["Notes"] = _merge_notes(
                    existing[0].get("fields", {}).get("Notes"),
                    fields["Notes"],
                )
                airtable_client.update_record(CONTACTS_TABLE, rec_id, fields)
                stats["updated"] += 1
            else:
                airtable_client.create_record(CONTACTS_TABLE, fields)
                stats["created"] += 1
        except Exception as e:
            log.warning("upsert failed for %s: %s", email, e)
            stats["skipped"] += 1

    return stats


# ─────────────────────────────────────────────────────────────────────────────
# Batch: NAICS-driven SAM.gov sweep (reuses mine_co_contacts.query_one_naics)
# ─────────────────────────────────────────────────────────────────────────────

def _iter_naics() -> List[str]:
    from mine_co_contacts import DDI_NAICS_LANES  # type: ignore

    codes: List[str] = []
    for lane_codes in DDI_NAICS_LANES.values():
        codes.extend(lane_codes)
    return codes


def _fetch_opps_for_naics(naics: str, api_key: str, days_back: int) -> List[Dict[str, Any]]:
    """Query SAM.gov for one NAICS code and return the raw opportunity list."""
    import requests
    from datetime import timedelta

    posted_from = (datetime.now() - timedelta(days=days_back)).strftime("%m/%d/%Y")
    posted_to = datetime.now().strftime("%m/%d/%Y")
    params = {
        "api_key": api_key,
        # ncode is the canonical SAM.gov v2 NAICS filter; "naics" is silently ignored.
        "ncode": naics,
        "limit": 100,
        "postedFrom": posted_from,
        "postedTo": posted_to,
    }
    try:
        resp = requests.get(
            "https://api.sam.gov/opportunities/v2/search",
            params=params,
            timeout=120,
        )
    except Exception as e:
        log.warning("SAM request failed for NAICS %s: %s", naics, e)
        return []

    if resp.status_code == 401 or resp.status_code == 403:
        log.warning("SAM auth failure for NAICS %s: HTTP %s", naics, resp.status_code)
        return []
    if resp.status_code != 200:
        log.warning("SAM HTTP %s for NAICS %s", resp.status_code, naics)
        return []
    return resp.json().get("opportunitiesData") or []


def sync_co_contacts_from_sam(
    days_back: int = 30,
    dry_run: bool = False,
    limit_naics: Optional[int] = None,
) -> Dict[str, Any]:
    """Sweep SAM.gov across DDI's NAICS codes and upsert every POC into GPSS CONTACTS.

    Args:
        days_back: how many days of postedDate to scan.
        dry_run: skip Airtable writes (still hits SAM.gov).
        limit_naics: only query the first N NAICS codes. ~50 full sweep is
            bandwidth-heavy; pass e.g. 5 for a quick targeted run.
    """
    api_key = (os.environ.get("SAM_GOV_API_KEY") or "").strip()
    if not api_key or api_key.upper() == "DEMO_KEY":
        return {"ok": False, "reason": "no_sam_api_key"}

    naics_codes = _iter_naics()
    if limit_naics is not None and limit_naics > 0:
        naics_codes = naics_codes[:limit_naics]

    airtable_client = None
    if not dry_run:
        try:
            sys.path.insert(0, str(BASE_DIR))
            from nexus_backend import AirtableClient

            airtable_client = AirtableClient()
        except Exception as e:
            log.warning("AirtableClient unavailable: %s (running dry)", e)
            dry_run = True

    totals = {
        "naics_queried": 0,
        "opps_seen": 0,
        "pocs_extracted": 0,
        "created": 0,
        "updated": 0,
        "skipped": 0,
        "auth_failures": 0,
    }
    seen_notices: set[str] = set()

    log.info(
        "sam_co_contact_sync: sweeping %s NAICS codes, last %s days, dry_run=%s",
        len(naics_codes),
        days_back,
        dry_run,
    )
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {
            executor.submit(_fetch_opps_for_naics, naics, api_key, days_back): naics
            for naics in naics_codes
        }
        for future in as_completed(futures):
            naics = futures[future]
            totals["naics_queried"] += 1
            try:
                opps = future.result() or []
            except Exception as e:
                log.warning("NAICS %s fetch errored: %s", naics, e)
                continue

            naics_pocs = 0
            naics_created = 0
            naics_updated = 0
            for opp in opps:
                nid = (opp.get("noticeId") or "").strip()
                if nid and nid in seen_notices:
                    continue
                if nid:
                    seen_notices.add(nid)
                totals["opps_seen"] += 1
                stats = upsert_pocs_for_opp(opp, airtable_client=airtable_client, dry_run=dry_run)
                naics_pocs += stats["extracted"]
                naics_created += stats["created"]
                naics_updated += stats["updated"]
                totals["pocs_extracted"] += stats["extracted"]
                totals["created"] += stats["created"]
                totals["updated"] += stats["updated"]
                totals["skipped"] += stats["skipped"]

            log.info(
                "[%s/%s] NAICS %s: %s opps → %s POCs (%s new, %s updated)",
                totals["naics_queried"],
                len(naics_codes),
                naics,
                len(opps),
                naics_pocs,
                naics_created,
                naics_updated,
            )

    totals.update(
        {
            "ok": True,
            "dry_run": dry_run,
            "days_back": days_back,
            "generated_at": datetime.now().isoformat(timespec="seconds"),
        }
    )
    return totals


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    ap = argparse.ArgumentParser(
        description="Sync SAM.gov contracting officers into GPSS CONTACTS"
    )
    ap.add_argument("--days", type=int, default=30, help="Look-back window (days)")
    ap.add_argument("--dry-run", action="store_true", help="Do not write to Airtable")
    ap.add_argument(
        "--limit-naics",
        type=int,
        default=None,
        help="Only sweep the first N NAICS codes (full list is ~50, bandwidth-heavy)",
    )
    args = ap.parse_args()

    result = sync_co_contacts_from_sam(
        days_back=args.days,
        dry_run=args.dry_run,
        limit_naics=args.limit_naics,
    )
    print(json.dumps(result, indent=2))
    if not result.get("ok"):
        sys.exit(1)


if __name__ == "__main__":
    main()
