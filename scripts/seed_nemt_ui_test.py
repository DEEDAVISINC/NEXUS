#!/usr/bin/env python3
"""Seed a PRISM + NEMT linked order for Transport division UI button testing."""

import json
import os
import sys
import urllib.request

API = os.environ.get("NEXUS_API_BASE", "http://127.0.0.1:8000")


def _post(path: str, payload: dict) -> dict:
    req = urllib.request.Request(
        f"{API}{path}",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode())


def main() -> int:
    intake = _post(
        "/prism/intake",
        {
            "service_key": "nemt",
            "service_label": "NEMT & Medical Mobility",
            "channel": "ui_test",
            "client_company": "HAP CareSource Member",
            "subject_first": "UI Button",
            "subject_last": "Test Member",
            "subject_phone": "7344138310",
            "subject_dob": "01/01/1980",
            "subject_location": "100 UI Test St, Detroit MI 48201",
            "collection_site": "200 Clinic Rd, Detroit MI 48202",
            "sched_date": "2026-06-10",
            "sched_time": "2:00 PM",
            "notes": "UI button test seed — safe to complete",
            "details": {
                "member_id": "UI-TEST-001",
                "trip_type": "Ambulatory",
                "mobility_lane": "MOB-A",
            },
            "billing_tier": "contract",
            "payment_method": "mco_billing",
            "order_total": 0,
        },
    )
    order = intake.get("order") or {}
    prism_id = order.get("id") or intake.get("confirmation")
    if not prism_id:
        print("FAIL: no PRISM order id", intake, file=sys.stderr)
        return 1

    nemt = _post(
        "/prism/nemt/orders",
        {
            "member_medicaid_id": "UI-TEST-001",
            "member_name": "UI Button Test Member",
            "member_dob": "01/01/1980",
            "payer": "HAP CareSource",
            "transport_type": "ambulatory",
            "pickup_address": "100 UI Test St, Detroit MI 48201",
            "dropoff_address": "200 Clinic Rd, Detroit MI 48202",
            "pickup_time": "2026-06-10 14:00",
            "trip_purpose": "Medical appointment",
            "eligibility_verified": True,
            "prism_order_id": prism_id,
            "notes": f"UI button test · PRISM {prism_id}",
        },
    )
    nemt_id = nemt.get("order_id")
    print(json.dumps({"prism_order_id": prism_id, "nemt_order_id": nemt_id, "status": nemt.get("status")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
