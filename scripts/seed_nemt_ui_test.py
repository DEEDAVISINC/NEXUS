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
    nemt_id = intake.get("nemt_order_id") or (order.get("details") or {}).get("nemt_order_id")
    if not prism_id:
        print("FAIL: no PRISM order id", intake, file=sys.stderr)
        return 1

    if not nemt_id:
        print("FAIL: NEMT auto-link missing — deploy latest prism_nemt.py + prism_orders_api.py", intake, file=sys.stderr)
        return 1

    print(json.dumps({"prism_order_id": prism_id, "nemt_order_id": nemt_id, "nemt_linked": True}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
