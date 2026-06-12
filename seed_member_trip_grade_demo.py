#!/usr/bin/env python3
"""
Seed demo member trip grades for HAP CareSource MCO packet preview.

Safe for production demo data — clearly labeled DEMO refs. Re-run replaces same demo IDs.

Usage (PythonAnywhere):
  cd ~/nexus-backend
  python3 seed_member_trip_grade_demo.py
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

EASTERN = ZoneInfo("America/Detroit")

DEMO_PREFIX = "DEMO-HAP-GRADE-"
DEMO_NEMT_IDS = (f"{DEMO_PREFIX}001", f"{DEMO_PREFIX}002", f"{DEMO_PREFIX}003")


def _iso(days_ago: int, hour: int, minute: int = 0) -> str:
    dt = datetime.now(EASTERN) - timedelta(days=days_ago)
    dt = dt.replace(hour=hour, minute=minute, second=0, microsecond=0)
    return dt.isoformat()


def _demo_records() -> list:
    base_snap = {
        "transport_type": "nemt_standard",
        "transport_label": "NEMT — Ambulatory",
        "hcpcs_code": "A0100",
        "eligibility_verified": True,
        "fulfillment_platform": "DDI-managed network",
        "nemt_status_at_grade_queue": "completed",
    }

    return [
        {
            "token": uuid.uuid4().hex,
            "status": "completed",
            "record_type": "member_trip_grade_audit",
            "demo_record": True,
            "nemt_order_id": DEMO_NEMT_IDS[0],
            "prism_order_id": "PRISM-DEMO-1001",
            "vertex_trip_id": "VTX-DEMO-88421",
            "member_name": "Maria S.",
            "member_email": "maria.s.demo@example.com",
            "member_phone": "+13135550101",
            "member_phone_masked": "***-***-0101",
            "payer": "HAP CareSource",
            "trip_purpose": "Primary care appointment",
            "driver_name": "J. Williams",
            "trip_ref": "PRISM-DEMO-1001",
            "trip_snapshot": {
                **base_snap,
                "pickup_time": "May 28, 2026 9:00 AM ET",
                "appointment_time": "May 28, 2026 10:00 AM ET",
                "actual_pickup_time": "May 28, 2026 8:52 AM ET",
                "actual_dropoff_time": "May 28, 2026 9:38 AM ET",
                "actual_mileage": "12.4",
                "pickup_address": "1842 Oak Valley Dr, Southfield, MI 48076",
                "dropoff_address": "Henry Ford Medical Center — 6777 W Maple Rd, West Bloomfield, MI 48322",
                "member_medicaid_id_masked": "****7821",
                "member_dob": "1968-03-14",
                "vehicle_id": "DDI-MI-042",
                "prior_auth_number": "PA-HAP-2026-44821",
                "prism_order_id": "PRISM-DEMO-1001",
                "vertex_trip_id": "VTX-DEMO-88421",
                "vertex_invoice_id": "INV-DEMO-20260528-001",
            },
            "completed_at": _iso(3, 10, 15),
            "created_at": _iso(3, 10, 20),
            "sent_at": _iso(3, 11, 20),
            "reminder_sent_at": None,
            "responded_at": _iso(3, 14, 5),
            "ddi_grade": "A",
            "driver_grade": "A",
            "trip_grade": "B",
            "overall_grade": "A",
            "ddi_rating": 5,
            "driver_rating": 5,
            "trip_rating": 4,
            "overall_average": 4.67,
            "comments": "Driver was professional and on time. Short wait at pickup would make it perfect.",
            "response_channel": "sms",
            "survey_url": "https://deedavis.pythonanywhere.com/member/survey/demo-seed-001",
            "portal_only": False,
        },
        {
            "token": uuid.uuid4().hex,
            "status": "completed",
            "record_type": "member_trip_grade_audit",
            "demo_record": True,
            "nemt_order_id": DEMO_NEMT_IDS[1],
            "prism_order_id": "PRISM-DEMO-1002",
            "vertex_trip_id": "VTX-DEMO-88422",
            "member_name": "Robert T.",
            "member_email": "robert.t.demo@example.com",
            "member_phone": "+13135550202",
            "member_phone_masked": "***-***-0202",
            "payer": "HAP CareSource",
            "trip_purpose": "Dialysis",
            "driver_name": "A. Johnson",
            "trip_ref": "PRISM-DEMO-1002",
            "trip_snapshot": {
                **base_snap,
                "transport_type": "nemt_wheelchair",
                "transport_label": "NEMT — Wheelchair",
                "hcpcs_code": "A0130",
                "pickup_time": "May 29, 2026 5:30 AM ET",
                "appointment_time": "May 29, 2026 6:00 AM ET",
                "actual_pickup_time": "May 29, 2026 5:28 AM ET",
                "actual_dropoff_time": "May 29, 2026 5:55 AM ET",
                "actual_mileage": "8.1",
                "pickup_address": "910 Riverside Ave, Detroit, MI 48207",
                "dropoff_address": "DaVita Dialysis — 3990 John R St, Detroit, MI 48201",
                "member_medicaid_id_masked": "****3390",
                "member_dob": "1955-11-02",
                "vehicle_id": "DDI-MI-018",
                "prior_auth_number": "PA-HAP-2026-44822",
                "prism_order_id": "PRISM-DEMO-1002",
                "vertex_trip_id": "VTX-DEMO-88422",
                "vertex_invoice_id": "INV-DEMO-20260529-002",
            },
            "completed_at": _iso(2, 7, 0),
            "created_at": _iso(2, 7, 5),
            "sent_at": _iso(2, 8, 0),
            "reminder_sent_at": _iso(1, 8, 0),
            "responded_at": _iso(1, 9, 40),
            "ddi_grade": "B",
            "driver_grade": "A",
            "trip_grade": "A",
            "overall_grade": "A",
            "ddi_rating": 4,
            "driver_rating": 5,
            "trip_rating": 5,
            "overall_average": 4.67,
            "comments": "Early morning dialysis trip — driver was waiting when I came out. Very helpful with the chair.",
            "response_channel": "portal",
            "survey_url": "https://deedavis.pythonanywhere.com/member/survey/demo-seed-002",
            "portal_only": False,
        },
        {
            "token": uuid.uuid4().hex,
            "status": "sent",
            "record_type": "member_trip_grade_audit",
            "demo_record": True,
            "nemt_order_id": DEMO_NEMT_IDS[2],
            "prism_order_id": "PRISM-DEMO-1003",
            "vertex_trip_id": "VTX-DEMO-88423",
            "member_name": "Denise M.",
            "member_email": "denise.m.demo@example.com",
            "member_phone": "+13135550303",
            "member_phone_masked": "***-***-0303",
            "payer": "HAP CareSource",
            "trip_purpose": "Pharmacy",
            "driver_name": "K. Brown",
            "trip_ref": "PRISM-DEMO-1003",
            "trip_snapshot": {
                **base_snap,
                "pickup_time": "May 30, 2026 2:00 PM ET",
                "appointment_time": "May 30, 2026 2:30 PM ET",
                "actual_pickup_time": "May 30, 2026 1:58 PM ET",
                "actual_dropoff_time": "May 30, 2026 2:22 PM ET",
                "actual_mileage": "5.6",
                "pickup_address": "4550 Cass Ave, Detroit, MI 48201",
                "dropoff_address": "CVS Pharmacy — 2900 E Grand Blvd, Detroit, MI 48202",
                "member_medicaid_id_masked": "****5512",
                "member_dob": "1972-07-21",
                "vehicle_id": "DDI-MI-031",
                "prior_auth_number": "PA-HAP-2026-44823",
                "prism_order_id": "PRISM-DEMO-1003",
                "vertex_trip_id": "VTX-DEMO-88423",
            },
            "completed_at": _iso(1, 14, 30),
            "created_at": _iso(1, 14, 35),
            "sent_at": _iso(1, 15, 35),
            "reminder_sent_at": None,
            "responded_at": None,
            "ddi_grade": None,
            "driver_grade": None,
            "trip_grade": None,
            "overall_grade": None,
            "ddi_rating": None,
            "driver_rating": None,
            "trip_rating": None,
            "overall_average": None,
            "comments": None,
            "response_channel": None,
            "survey_url": "https://deedavis.pythonanywhere.com/member/survey/demo-seed-003",
            "portal_only": False,
        },
    ]


def main() -> None:
    from member_satisfaction_survey import (
        _AUDIT_DIR,
        _load_log,
        _save_log,
        _write_audit_archive,
    )
    from member_trip_grade_audit_report import write_trip_audit_html

    log = _load_log()
    log = [r for r in log if not str(r.get("nemt_order_id", "")).startswith(DEMO_PREFIX)]
    demos = _demo_records()

    for rec in demos:
        if rec.get("status") == "completed":
            rec["audit_archive_path"] = _write_audit_archive(rec)
            try:
                rec["audit_html_path"] = write_trip_audit_html(rec, _AUDIT_DIR)
            except Exception as exc:
                rec["audit_html_path"] = None
                print(f"  ⚠ HTML archive failed for {rec['nemt_order_id']}: {exc}")

    log.extend(demos)
    _save_log(log)

    try:
        from seed_nexus_qc_demo import seed_qc_demo

        qc = seed_qc_demo(sync_grades=True)
        print(f"   QC demo: {len(qc['qc_ids'])} records → {qc['breakdown_url']}")
    except Exception as exc:
        print(f"  ⚠ QC demo seed skipped: {exc}")

    completed = sum(1 for r in demos if r.get("status") == "completed")
    pending = sum(1 for r in demos if r.get("status") != "completed")
    print(f"✅ Demo trip grades seeded — {completed} completed, {pending} awaiting grade")
    print(f"   Log: uploads/member_satisfaction/survey_log.json")
    print(f"   Preview: https://deedavis.pythonanywhere.com/prism/nemt/satisfaction/mco-packet.html?payer=HAP%20CareSource")


if __name__ == "__main__":
    main()
