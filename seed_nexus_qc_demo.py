#!/usr/bin/env python3
"""
Seed demo QC records for HAP CareSource MCO breakdown preview.

Pairs with seed_member_trip_grade_demo.py (same DEMO-HAP-GRADE-* trip IDs).

Usage:
  python3 seed_nexus_qc_demo.py
  python3 seed_member_trip_grade_demo.py   # also runs QC seed at end
"""

from __future__ import annotations

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

EASTERN = ZoneInfo("America/Detroit")
DEMO_PREFIX = "DEMO-HAP-GRADE-"
DEMO_NEMT_IDS = (f"{DEMO_PREFIX}001", f"{DEMO_PREFIX}002", f"{DEMO_PREFIX}003")


def _iso(days_ago: int, hour: int, minute: int = 0) -> str:
    dt = datetime.now(EASTERN) - timedelta(days=days_ago)
    dt = dt.replace(hour=hour, minute=minute, second=0, microsecond=0)
    return dt.isoformat()


def _demo_orders() -> list:
    return [
        {
            "order_id": DEMO_NEMT_IDS[0],
            "payer": "HAP CareSource",
            "contract_id": "HAP-CARESOURCE-NEMT",
            "status": "completed",
            "completed_at": _iso(3, 10, 15),
            "actual_pickup_time": _iso(3, 8, 52),
            "actual_dropoff_time": _iso(3, 9, 38),
            "actual_mileage": 12.4,
            "mileage": 12.4,
            "eligibility_verified": True,
            "prior_auth_number": "PA-HAP-2026-44821",
            "driver_name": "J. Williams",
            "vehicle_id": "DDI-MI-042",
            "pickup_address": "1842 Oak Valley Dr, Southfield, MI 48076",
            "dropoff_address": "Henry Ford Medical Center — West Bloomfield, MI",
            "trip_purpose": "Primary care appointment",
            "hcpcs_code": "A0100",
            "prism_order_id": "PRISM-DEMO-1001",
            "vertex_trip_id": "VTX-DEMO-88421",
            "vertex_invoice_id": "INV-DEMO-20260528-001",
        },
        {
            "order_id": DEMO_NEMT_IDS[1],
            "payer": "HAP CareSource",
            "contract_id": "HAP-CARESOURCE-NEMT",
            "status": "completed",
            "completed_at": _iso(2, 7, 0),
            "actual_pickup_time": _iso(2, 5, 28),
            "actual_dropoff_time": _iso(2, 5, 55),
            "actual_mileage": 8.1,
            "mileage": 8.1,
            "eligibility_verified": True,
            "prior_auth_number": "PA-HAP-2026-44822",
            "driver_name": "A. Johnson",
            "vehicle_id": "DDI-MI-018",
            "pickup_address": "910 Riverside Ave, Detroit, MI 48207",
            "dropoff_address": "DaVita Dialysis — Detroit, MI",
            "trip_purpose": "Dialysis",
            "hcpcs_code": "A0130",
            "prism_order_id": "PRISM-DEMO-1002",
            "vertex_trip_id": "VTX-DEMO-88422",
            "vertex_invoice_id": "INV-DEMO-20260529-002",
        },
        {
            "order_id": DEMO_NEMT_IDS[2],
            "payer": "HAP CareSource",
            "contract_id": "HAP-CARESOURCE-NEMT",
            "status": "completed",
            "completed_at": _iso(1, 14, 30),
            "actual_pickup_time": _iso(1, 13, 58),
            "actual_dropoff_time": _iso(1, 14, 22),
            "actual_mileage": 5.6,
            "mileage": 5.6,
            "eligibility_verified": True,
            "prior_auth_number": "PA-HAP-2026-44823",
            "driver_name": "K. Brown",
            "vehicle_id": "DDI-MI-031",
            "pickup_address": "4550 Cass Ave, Detroit, MI 48201",
            "dropoff_address": "CVS Pharmacy — Detroit, MI",
            "trip_purpose": "Pharmacy",
            "hcpcs_code": "A0100",
            "prism_order_id": "PRISM-DEMO-1003",
            "vertex_trip_id": "VTX-DEMO-88423",
            "vertex_invoice_id": None,
        },
    ]


def seed_qc_demo(*, sync_grades: bool = True) -> dict:
    import nexus_qc_engine as qc
    from nexus_qc_engine import (
        PILLAR_STATUS_PASS,
        PILLAR_STATUS_PENDING,
        ensure_hap_contract_seed,
        list_records,
        sync_member_grade_to_qc,
        sync_nemt_trip_from_order,
        update_pillar,
    )

    ensure_hap_contract_seed()

    records = qc._load_json(qc.RECORDS_FILE, [])
    records = [r for r in records if not str(r.get("nemt_order_id", "")).startswith(DEMO_PREFIX)]
    qc._save_json(qc.RECORDS_FILE, records)

    created = []
    for order in _demo_orders():
        rec = sync_nemt_trip_from_order(order)
        # Demo polish — pillar 6 from grades where completed
        idx = DEMO_NEMT_IDS.index(order["order_id"])
        if idx < 2:
            update_pillar(
                rec["qc_id"],
                6,
                status=PILLAR_STATUS_PASS if idx == 0 else PILLAR_STATUS_PASS,
                evidence={"overall_grade": "A", "demo": True},
                notes="Demo member grade on file",
            )
        else:
            update_pillar(
                rec["qc_id"],
                6,
                status=PILLAR_STATUS_PENDING,
                evidence={"survey": "sent_awaiting_response"},
                notes="Demo — grade pending",
            )
        if order.get("vertex_invoice_id"):
            update_pillar(
                rec["qc_id"],
                7,
                status=PILLAR_STATUS_PASS,
                evidence={
                    "vertex_invoice_id": order["vertex_invoice_id"],
                    "demo": True,
                },
                notes="Demo invoice on file",
            )
        else:
            update_pillar(
                rec["qc_id"],
                7,
                status=PILLAR_STATUS_PENDING,
                evidence={},
                notes="Trip complete — invoice pending",
            )
        created.append(rec["qc_id"])

    if sync_grades:
        try:
            from member_satisfaction_survey import _load_log

            for survey in _load_log():
                if str(survey.get("nemt_order_id", "")).startswith(DEMO_PREFIX):
                    if survey.get("status") == "completed":
                        sync_member_grade_to_qc(survey)
        except ImportError:
            pass

    payer_records = list_records(payer="HAP", limit=100)
    return {
        "qc_ids": created,
        "total_hap_records": len(payer_records),
        "breakdown_url": "/nexus/qc/mco/breakdown.html?payer=HAP%20CareSource",
    }


def main() -> None:
    result = seed_qc_demo()
    print(f"✅ Demo QC records seeded — {len(result['qc_ids'])} trips")
    for qid in result["qc_ids"]:
        print(f"   · {qid}")
    print(f"   HAP register total: {result['total_hap_records']} records")
    print(f"   Preview: https://deedavis.pythonanywhere.com{result['breakdown_url']}")


if __name__ == "__main__":
    main()
