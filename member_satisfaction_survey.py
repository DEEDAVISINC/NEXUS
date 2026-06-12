"""
Member Trip Grade — SMS-first experience scorecard for audits.

After NEMT trip completion:
  1. SMS (~60 min post-dropoff) with mobile link to **grade** the trip (A–F)
  2. Reminder SMS if no grade submitted (default 24h)
  3. Portal backup gate if they log in before grading

No phone-call surveys — text/SMS only. One grade required per completed ride.

Grades stored in uploads/member_satisfaction/survey_log.json

Env:
  NEXUS_CONFIRM_BASE_URL / PRISM_VOICE_BASE_URL — survey link base
  MEMBER_SURVEY_DELAY_MINUTES — initial SMS delay (default 60)
  MEMBER_SURVEY_REMINDER_HOURS — reminder SMS if unanswered (default 24, 0=off)
  TWILIO_* — outbound SMS from 855-773-0035
"""

from __future__ import annotations

import csv
import io
import json
import logging
import os
import threading
import time
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from zoneinfo import ZoneInfo

from flask import Blueprint, Response, jsonify, render_template_string, request

from company_info import BRAND_NAME, member_care_phone_display

logger = logging.getLogger("nexus.member_survey")

EASTERN = ZoneInfo("America/Detroit")

VALID_GRADES = frozenset("ABCDF")
GRADE_TO_NUM = {"A": 5, "B": 4, "C": 3, "D": 2, "F": 1}
NUM_TO_GRADE = {5: "A", 4: "B", 3: "C", 2: "D", 1: "F"}
GRADE_LABELS = {
    "A": "Excellent",
    "B": "Good",
    "C": "Fair",
    "D": "Poor",
    "F": "Unacceptable",
}

_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
_LOG_DIR = os.path.join(_BASE_DIR, "uploads", "member_satisfaction")
_LOG_FILE = os.path.join(_LOG_DIR, "survey_log.json")
_AUDIT_DIR = os.path.join(_LOG_DIR, "audit")
os.makedirs(_LOG_DIR, exist_ok=True)
os.makedirs(_AUDIT_DIR, exist_ok=True)

member_survey = Blueprint("member_survey", __name__)

_SURVEY_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1">
<title>Grade Your Trip — {{ brand }}</title>
<style>
  *{box-sizing:border-box;margin:0;padding:0}
  body{font-family:system-ui,-apple-system,sans-serif;background:#0f172a;min-height:100vh;padding:16px 12px 32px}
  .card{max-width:440px;margin:0 auto;background:#fff;border-radius:18px;padding:24px 18px 22px;box-shadow:0 16px 40px rgba(0,0,0,.35)}
  .badge{display:inline-block;font-size:10px;font-weight:800;letter-spacing:.5px;text-transform:uppercase;color:#6d28d9;background:#ede9fe;padding:5px 10px;border-radius:999px;margin-bottom:10px}
  h1{font-size:22px;color:#0f172a;margin-bottom:6px;line-height:1.25}
  .sub{font-size:14px;color:#64748b;margin-bottom:16px;line-height:1.55}
  .ref{font-size:12px;color:#94a3b8;margin-bottom:6px}
  .scale{font-size:11px;color:#64748b;margin-bottom:18px;line-height:1.45}
  label.field{display:block;font-size:13px;font-weight:700;color:#334155;margin:16px 0 8px}
  .grade-row{display:flex;gap:6px}
  .grade-row input{position:absolute;opacity:0;width:0;height:0}
  .grade-row label{
    flex:1;text-align:center;padding:11px 4px 9px;border:2px solid #e2e8f0;border-radius:12px;
    font-weight:800;font-size:20px;line-height:1;color:#475569;cursor:pointer;transition:all .12s
  }
  .grade-row label span{display:block;font-size:8px;font-weight:700;margin-top:5px;text-transform:uppercase;letter-spacing:.3px;color:#94a3b8}
  .grade-row input:checked+label{border-color:#0f172a;background:#0f172a;color:#fff}
  .grade-row input:checked+label span{color:#cbd5e1}
  textarea{width:100%;border:1px solid #e2e8f0;border-radius:10px;padding:12px;font-size:16px;min-height:72px;margin-top:6px;resize:vertical}
  button{width:100%;margin-top:20px;padding:15px;background:#0f172a;color:#fff;border:none;border-radius:12px;font-size:17px;font-weight:700;cursor:pointer}
  button:disabled{opacity:.5}
  .done{text-align:center;padding:32px 12px}
  .done h2{color:#059669;font-size:22px;margin-bottom:12px}
  .err{color:#dc2626;font-size:14px;margin-top:12px}
  .foot{font-size:11px;color:#94a3b8;margin-top:16px;line-height:1.5}
</style>
</head>
<body>
<div class="card">
{% if submitted %}
  <div class="done">
    <h2>Thank you!</h2>
    <p style="color:#475569;font-size:15px;line-height:1.6">Your trip grade is recorded. This helps {{ brand }} improve every ride.</p>
    <p class="foot" style="margin-top:20px">Need help? Text {{ care_phone }}</p>
  </div>
{% elif error %}
  <h1>Grade form unavailable</h1>
  <p class="sub">{{ error }}</p>
  <p class="foot">Text {{ care_phone }} for member care.</p>
{% else %}
  <div class="badge">Trip grade — required</div>
  <h1>Grade your trip</h1>
  <p class="sub">Hi{% if first_name %} {{ first_name }}{% endif %} — tap a letter grade for each part of your ride. Takes about 30 seconds.</p>
  <p class="ref">Trip: {{ ref }}</p>
  <p class="scale">A = Excellent · B = Good · C = Fair · D = Poor · F = Unacceptable</p>
  <form method="post" action="">
    <label class="field">{{ brand }} overall</label>
    <div class="grade-row">
      {% for g, lbl in grades %}
      <input type="radio" name="ddi_grade" id="ddi-{{ g }}" value="{{ g }}" required>
      <label for="ddi-{{ g }}">{{ g }}<span>{{ lbl }}</span></label>
      {% endfor %}
    </div>
    <label class="field">Driver / travel companion</label>
    <div class="grade-row">
      {% for g, lbl in grades %}
      <input type="radio" name="driver_grade" id="drv-{{ g }}" value="{{ g }}" required>
      <label for="drv-{{ g }}">{{ g }}<span>{{ lbl }}</span></label>
      {% endfor %}
    </div>
    <label class="field">Trip comfort &amp; travel</label>
    <div class="grade-row">
      {% for g, lbl in grades %}
      <input type="radio" name="trip_grade" id="trip-{{ g }}" value="{{ g }}" required>
      <label for="trip-{{ g }}">{{ g }}<span>{{ lbl }}</span></label>
      {% endfor %}
    </div>
    <label class="field">Optional comment</label>
    <textarea name="comments" maxlength="1000" placeholder="Anything we should know? (optional)"></textarea>
    <button type="submit">Submit grade</button>
  </form>
  <p class="foot">Grades support quality records for health plan audits. No PHI in comments please.</p>
{% endif %}
</div>
</body>
</html>
"""

_GRADE_OPTIONS = [(g, GRADE_LABELS[g]) for g in "ABCDF"]


def _base_url() -> str:
    for key in ("NEXUS_CONFIRM_BASE_URL", "PRISM_VOICE_BASE_URL"):
        val = (os.environ.get(key) or "").strip().rstrip("/")
        if val:
            return val
    return "https://deedavis.pythonanywhere.com"


def _survey_delay_seconds() -> int:
    try:
        mins = int(os.environ.get("MEMBER_SURVEY_DELAY_MINUTES", "60"))
        return max(0, mins) * 60
    except ValueError:
        return 3600


def _survey_reminder_seconds() -> int:
    try:
        hours = int(os.environ.get("MEMBER_SURVEY_REMINDER_HOURS", "24"))
        return max(0, hours) * 3600
    except ValueError:
        return 86400


def _normalize_grade(raw: Optional[str]) -> Optional[str]:
    g = (raw or "").strip().upper()
    return g if g in VALID_GRADES else None


def _coerce_category(grade: Optional[str], rating: Optional[int]) -> Tuple[int, str]:
    g = _normalize_grade(grade)
    if g:
        return GRADE_TO_NUM[g], g
    if rating is not None:
        n = max(1, min(5, int(rating)))
        return n, NUM_TO_GRADE[n]
    raise ValueError("grade or rating required")


def _composite_grade(avg: float) -> str:
    return NUM_TO_GRADE.get(max(1, min(5, round(avg))), "C")


def _load_log() -> List[Dict[str, Any]]:
    if not os.path.isfile(_LOG_FILE):
        return []
    try:
        with open(_LOG_FILE, encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except Exception:
        return []


def _save_log(records: List[Dict[str, Any]]) -> None:
    tmp = _LOG_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, default=str)
    os.replace(tmp, _LOG_FILE)


def _clean_phone(raw: str) -> str:
    digits = "".join(c for c in (raw or "") if c.isdigit())
    if len(digits) == 10:
        return "+1" + digits
    if len(digits) == 11 and digits.startswith("1"):
        return "+" + digits
    return raw or ""


def _twilio_ok() -> bool:
    return bool(
        os.environ.get("TWILIO_ACCOUNT_SID")
        and os.environ.get("TWILIO_AUTH_TOKEN")
        and os.environ.get("TWILIO_FROM_NUMBER")
    )


def _send_sms(to: str, body: str) -> Dict[str, Any]:
    if not _twilio_ok():
        return {"success": False, "skipped": True, "error": "Twilio not configured"}
    try:
        from twilio.rest import Client

        client = Client(
            os.environ["TWILIO_ACCOUNT_SID"],
            os.environ["TWILIO_AUTH_TOKEN"],
        )
        msg = client.messages.create(
            body=body,
            from_=os.environ["TWILIO_FROM_NUMBER"],
            to=_clean_phone(to),
        )
        return {"success": True, "sid": msg.sid}
    except Exception as exc:
        logger.warning("Survey SMS failed: %s", exc)
        return {"success": False, "error": str(exc)}


def _first_name(full: str) -> str:
    parts = (full or "").strip().split()
    return parts[0] if parts else ""


def _normalize_email(raw: str) -> str:
    return (raw or "").strip().lower()


def _resolve_member_email_from_prism(prism_order_id: Optional[str]) -> str:
    pid = (prism_order_id or "").strip()
    if not pid:
        return ""
    try:
        from prism_orders_api import ORDERS_FILE, _load

        for order in _load(ORDERS_FILE, []):
            if order.get("id") == pid:
                for key in ("client_email", "subject_email"):
                    val = _normalize_email(order.get(key) or "")
                    if val and "@" in val:
                        return val
    except Exception:
        pass
    return ""


def _survey_awaiting_response(rec: Dict[str, Any]) -> bool:
    return rec.get("status") in ("pending", "sent", "send_failed", "portal_required", "reminded")


def _portal_survey_payload(rec: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "token": rec.get("token"),
        "trip_ref": rec.get("trip_ref"),
        "prism_order_id": rec.get("prism_order_id"),
        "nemt_order_id": rec.get("nemt_order_id"),
        "member_name": rec.get("member_name"),
        "payer": rec.get("payer"),
        "trip_purpose": rec.get("trip_purpose"),
        "completed_at": rec.get("completed_at"),
        "driver_name": rec.get("driver_name"),
    }


def get_pending_surveys_for_member(
    email: str,
    phone: str = "",
    prism_order_ids: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    """Pending (ungraded) trips for portal gate — one grade required per completed ride."""
    email_norm = _normalize_email(email)
    phone_norm = _clean_phone(phone)
    order_ids = {str(x).strip() for x in (prism_order_ids or []) if str(x).strip()}

    pending: List[Dict[str, Any]] = []
    for rec in _load_log():
        if not _survey_awaiting_response(rec):
            continue
        rec_email = _normalize_email(rec.get("member_email") or "")
        rec_phone = _clean_phone(rec.get("member_phone") or _resolve_member_phone(rec))
        prism_id = (rec.get("prism_order_id") or rec.get("trip_ref") or "").strip()
        match = False
        if email_norm and rec_email and rec_email == email_norm:
            match = True
        elif phone_norm and rec_phone and rec_phone == phone_norm:
            match = True
        elif prism_id and prism_id in order_ids:
            match = True
        if match:
            pending.append(_portal_survey_payload(rec))

    pending.sort(key=lambda x: x.get("completed_at") or "")
    return pending


def queue_trip_satisfaction_survey(
    *,
    nemt_order_id: str,
    member_name: str,
    member_phone: str,
    payer: str = "",
    trip_purpose: str = "",
    prism_order_id: Optional[str] = None,
    vertex_trip_id: Optional[str] = None,
    driver_name: Optional[str] = None,
    completed_at: Optional[str] = None,
    member_email: Optional[str] = None,
) -> Dict[str, Any]:
    """Queue one trip grade. SMS after delay when phone on file; portal backup if not."""
    existing = next(
        (r for r in _load_log() if r.get("nemt_order_id") == nemt_order_id),
        None,
    )
    if existing:
        return {
            "success": True,
            "token": existing.get("token"),
            "survey_url": existing.get("survey_url"),
            "already_queued": True,
        }

    phone = _clean_phone(member_phone)
    email = _normalize_email(member_email or "")
    if not email and prism_order_id:
        email = _resolve_member_email_from_prism(prism_order_id)

    token = uuid.uuid4().hex
    ref = prism_order_id or nemt_order_id
    trip_snapshot = _build_trip_audit_snapshot(nemt_order_id)
    record = {
        "token": token,
        "status": "pending",
        "record_type": "member_trip_grade_audit",
        "nemt_order_id": nemt_order_id,
        "prism_order_id": prism_order_id,
        "vertex_trip_id": vertex_trip_id or trip_snapshot.get("vertex_trip_id"),
        "member_name": member_name,
        "member_email": email or None,
        "member_phone": phone or None,
        "member_phone_masked": f"***-***-{phone[-4:]}" if len(phone) >= 4 else "",
        "payer": payer,
        "trip_purpose": trip_purpose,
        "driver_name": driver_name or trip_snapshot.get("driver_name"),
        "trip_ref": ref,
        "trip_snapshot": trip_snapshot,
        "completed_at": completed_at or datetime.now(EASTERN).isoformat(),
        "survey_url": f"{_base_url()}/member/survey/{token}",
        "created_at": datetime.now(EASTERN).isoformat(),
        "sent_at": None,
        "reminder_sent_at": None,
        "responded_at": None,
        "ddi_grade": None,
        "driver_grade": None,
        "trip_grade": None,
        "overall_grade": None,
        "ddi_rating": None,
        "driver_rating": None,
        "trip_rating": None,
        "comments": None,
        "overall_average": None,
        "response_channel": None,
        "audit_archive_path": None,
    }
    log = _load_log()
    if not phone:
        record["status"] = "portal_required"
        record["portal_only"] = True
    log.append(record)
    _save_log(log)

    if not phone:
        return {
            "success": True,
            "token": token,
            "survey_url": record["survey_url"],
            "portal_only": True,
        }

    delay = _survey_delay_seconds()

    def _send_later() -> None:
        if delay:
            time.sleep(delay)
        _deliver_survey_sms(token)

    threading.Thread(target=_send_later, daemon=True).start()
    return {"success": True, "token": token, "survey_url": record["survey_url"], "delay_seconds": delay}


def _sms_grade_body(first: str, url: str, *, reminder: bool = False) -> str:
    care = member_care_phone_display()
    if reminder:
        return (
            f"{BRAND_NAME}: Reminder — grade your recent trip (A–F, ~30 sec). "
            f"Required before your next ride: {url} "
            f"Help? Text {care}"
        )
    name = f"Hi {first} — " if first else ""
    return (
        f"{BRAND_NAME}: {name}grade your trip (A–F). "
        f"Tap to rate DDI, driver & ride (~30 sec): {url} "
        f"Help? Text {care}"
    )


def _deliver_survey_sms(token: str) -> None:
    log = _load_log()
    rec = next((r for r in log if r.get("token") == token), None)
    if not rec or rec.get("status") != "pending":
        return
    if rec.get("sent_at"):
        return

    phone = _clean_phone(rec.get("member_phone") or "") or _resolve_member_phone(rec)
    if not phone:
        rec["status"] = "send_failed"
        rec["send_error"] = "no_phone"
        _update_log_record(log, rec)
        return

    first = _first_name(rec.get("member_name", ""))
    url = rec.get("survey_url") or f"{_base_url()}/member/survey/{token}"
    result = _send_sms(phone, _sms_grade_body(first, url, reminder=False))
    rec["sent_at"] = datetime.now(EASTERN).isoformat()
    if result.get("success"):
        rec["status"] = "sent"
        _update_log_record(log, rec)
        _schedule_survey_reminder(token)
    else:
        rec["status"] = "send_failed"
        rec["send_error"] = result.get("error", "unknown")
        _update_log_record(log, rec)


def _schedule_survey_reminder(token: str) -> None:
    delay = _survey_reminder_seconds()
    if delay <= 0:
        return

    def _remind_later() -> None:
        time.sleep(delay)
        _deliver_survey_reminder_sms(token)

    threading.Thread(target=_remind_later, daemon=True).start()


def _deliver_survey_reminder_sms(token: str) -> None:
    log = _load_log()
    rec = next((r for r in log if r.get("token") == token), None)
    if not rec or not _survey_awaiting_response(rec):
        return
    if rec.get("reminder_sent_at"):
        return

    phone = _clean_phone(rec.get("member_phone") or "") or _resolve_member_phone(rec)
    if not phone:
        return

    first = _first_name(rec.get("member_name", ""))
    url = rec.get("survey_url") or f"{_base_url()}/member/survey/{token}"
    result = _send_sms(phone, _sms_grade_body(first, url, reminder=True))
    if result.get("success"):
        rec["reminder_sent_at"] = datetime.now(EASTERN).isoformat()
        rec["status"] = "reminded"
        _update_log_record(log, rec)


def _update_log_record(log: List[Dict[str, Any]], rec: Dict[str, Any]) -> None:
    token = rec.get("token")
    for i, r in enumerate(log):
        if r.get("token") == token:
            log[i] = rec
            break
    _save_log(log)


def _resolve_nemt_order(nemt_order_id: str) -> Dict[str, Any]:
    oid = (nemt_order_id or "").strip()
    if not oid:
        return {}
    try:
        from prism_nemt import _load_state

        return dict(_load_state().get("orders", {}).get(oid, {}) or {})
    except Exception:
        return {}


def _mask_medicaid_id(raw: str) -> str:
    s = (raw or "").strip()
    if len(s) <= 4:
        return "****" if s else ""
    return f"{'*' * (len(s) - 4)}{s[-4:]}"


def _build_trip_audit_snapshot(nemt_order_id: str) -> Dict[str, Any]:
    """Detailed trip context stored with each survey record for MCO audit files."""
    order = _resolve_nemt_order(nemt_order_id)
    if not order:
        return {}
    return {
        "transport_type": order.get("transport_type"),
        "transport_label": order.get("transport_label"),
        "hcpcs_code": order.get("hcpcs_code"),
        "pickup_time": order.get("pickup_time"),
        "appointment_time": order.get("appointment_time"),
        "actual_pickup_time": order.get("actual_pickup_time"),
        "actual_dropoff_time": order.get("actual_dropoff_time"),
        "actual_mileage": order.get("actual_mileage"),
        "pickup_address": order.get("pickup_address"),
        "dropoff_address": order.get("dropoff_address"),
        "member_medicaid_id_masked": _mask_medicaid_id(order.get("member_medicaid_id", "")),
        "member_dob": order.get("member_dob"),
        "vehicle_id": order.get("vehicle_id"),
        "fulfillment_platform": order.get("fulfillment_platform"),
        "eligibility_verified": order.get("eligibility_verified"),
        "prior_auth_number": order.get("prior_auth_number"),
        "prism_order_id": order.get("prism_order_id"),
        "vertex_trip_id": order.get("vertex_trip_id"),
        "vertex_invoice_id": order.get("vertex_invoice_id"),
        "nemt_status_at_grade_queue": order.get("status"),
    }


def _write_audit_archive(rec: Dict[str, Any]) -> str:
    """
    Immutable per-trip audit file — one JSON per completed grade.
    Path: uploads/member_satisfaction/audit/YYYY/YYYY-MM-DD_{nemt_order_id}.json
    """
    completed = (rec.get("responded_at") or rec.get("completed_at") or datetime.now(EASTERN).isoformat())
    try:
        dt = datetime.fromisoformat(completed.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=EASTERN)
        else:
            dt = dt.astimezone(EASTERN)
    except Exception:
        dt = datetime.now(EASTERN)

    year_dir = os.path.join(_AUDIT_DIR, dt.strftime("%Y"))
    os.makedirs(year_dir, exist_ok=True)
    nemt_id = (rec.get("nemt_order_id") or rec.get("token") or "unknown").replace("/", "-")
    filename = f"{dt.strftime('%Y-%m-%d')}_{nemt_id}.json"
    path = os.path.join(year_dir, filename)

    payload = {
        "audit_type": "member_trip_grade",
        "brand": BRAND_NAME,
        "archived_at": datetime.now(EASTERN).isoformat(),
        **rec,
    }
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, default=str)
    os.replace(tmp, path)
    return path


def _resolve_member_phone(rec: Dict[str, Any]) -> str:
    stored = _clean_phone(rec.get("member_phone") or "")
    if stored:
        return stored
    oid = rec.get("nemt_order_id")
    if not oid:
        return ""
    try:
        from prism_nemt import _load_state

        order = _load_state().get("orders", {}).get(oid, {})
        for key in ("member_phone", "subject_phone", "client_phone", "phone"):
            val = order.get(key)
            if val:
                return _clean_phone(str(val))
    except Exception:
        pass
    return ""


def submit_survey_response(
    token: str,
    *,
    ddi_rating: Optional[int] = None,
    driver_rating: Optional[int] = None,
    trip_rating: Optional[int] = None,
    ddi_grade: Optional[str] = None,
    driver_grade: Optional[str] = None,
    trip_grade: Optional[str] = None,
    comments: str = "",
    response_channel: str = "sms",
) -> Dict[str, Any]:
    log = _load_log()
    rec = next((r for r in log if r.get("token") == token), None)
    if not rec:
        return {"success": False, "error": "Survey not found"}
    if rec.get("status") == "completed":
        return {"success": True, "already": True, "record": rec}

    try:
        ddi_n, ddi_g = _coerce_category(ddi_grade, ddi_rating)
        drv_n, drv_g = _coerce_category(driver_grade, driver_rating)
        trip_n, trip_g = _coerce_category(trip_grade, trip_rating)
    except ValueError:
        return {"success": False, "error": "Each category needs a letter grade (A–F)"}

    avg = round((ddi_n + drv_n + trip_n) / 3, 2)
    og = _composite_grade(avg)

    rec.update({
        "status": "completed",
        "responded_at": datetime.now(EASTERN).isoformat(),
        "response_channel": (response_channel or "sms").strip()[:32],
        "ddi_grade": ddi_g,
        "driver_grade": drv_g,
        "trip_grade": trip_g,
        "overall_grade": og,
        "ddi_rating": ddi_n,
        "driver_rating": drv_n,
        "trip_rating": trip_n,
        "comments": (comments or "").strip()[:1000] or None,
        "overall_average": avg,
    })
    if not rec.get("trip_snapshot"):
        rec["trip_snapshot"] = _build_trip_audit_snapshot(rec.get("nemt_order_id") or "")
    archive_path = _write_audit_archive(rec)
    rec["audit_archive_path"] = archive_path
    try:
        from member_trip_grade_audit_report import write_trip_audit_html

        rec["audit_html_path"] = write_trip_audit_html(rec, _AUDIT_DIR)
    except Exception as exc:
        logger.warning("Trip grade HTML archive failed: %s", exc)
        rec["audit_html_path"] = None
    _update_log_record(log, rec)

    nxlearn_survey(rec)
    return {"success": True, "record": rec}


def nxlearn_survey(rec: Dict[str, Any]) -> None:
    try:
        from nexus_learning_engine import nxlearn

        nxlearn("transport", rec.get("nemt_order_id", ""), "member_satisfaction", {
            "ddi_grade": rec.get("ddi_grade"),
            "driver_grade": rec.get("driver_grade"),
            "trip_grade": rec.get("trip_grade"),
            "overall_grade": rec.get("overall_grade"),
            "ddi_rating": rec.get("ddi_rating"),
            "driver_rating": rec.get("driver_rating"),
            "trip_rating": rec.get("trip_rating"),
            "overall_average": rec.get("overall_average"),
            "payer": rec.get("payer"),
        })
    except Exception:
        pass


def audit_summary(payer: Optional[str] = None) -> Dict[str, Any]:
    """Aggregate trip grades for MCO / internal audits."""
    records = _load_log()
    if payer:
        pl = payer.lower()
        records = [r for r in records if pl in (r.get("payer") or "").lower()]

    completed = [r for r in records if r.get("status") == "completed"]
    sent = [r for r in records if r.get("sent_at")]
    pending = [r for r in records if _survey_awaiting_response(r)]

    def _avg(field: str) -> Optional[float]:
        vals = [r[field] for r in completed if r.get(field) is not None]
        return round(sum(vals) / len(vals), 2) if vals else None

    def _grade_pct(letter: str) -> Optional[float]:
        grades = [r.get("overall_grade") for r in completed if r.get("overall_grade")]
        if not grades:
            return None
        return round(sum(1 for g in grades if g == letter) / len(grades) * 100, 1)

    return {
        "brand": BRAND_NAME,
        "generated_at": datetime.now(EASTERN).isoformat(),
        "payer_filter": payer,
        "scale": "A=Excellent(5) B=Good(4) C=Fair(3) D=Poor(2) F=Unacceptable(1)",
        "totals": {
            "surveys_queued": len(records),
            "sms_sent": len(sent),
            "grades_completed": len(completed),
            "awaiting_grade": len(pending),
            "response_rate_pct": round(len(completed) / len(sent) * 100, 1) if sent else 0,
        },
        "averages_numeric_1_to_5": {
            "ddi_overall": _avg("ddi_rating"),
            "driver_experience": _avg("driver_rating"),
            "trip_travel_experience": _avg("trip_rating"),
            "composite": _avg("overall_average"),
        },
        "overall_grade_distribution_pct": {
            g: _grade_pct(g) for g in "ABCDF"
        },
        "recent_grades": sorted(
            completed,
            key=lambda x: x.get("responded_at") or "",
            reverse=True,
        )[:25],
    }


def export_audit_csv(payer: Optional[str] = None) -> str:
    records = _load_log()
    if payer:
        pl = payer.lower()
        records = [r for r in records if pl in (r.get("payer") or "").lower()]

    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow([
        "Trip Ref", "Payer", "Member Name", "Trip Purpose", "Transport Type",
        "Pickup Time", "Actual Pickup", "Actual Dropoff", "Mileage",
        "Pickup Address", "Dropoff Address", "Trip Completed At",
        "Grade SMS Sent", "Reminder SMS", "Graded At",
        "DDI Grade", "Driver Grade", "Trip Grade", "Overall Grade",
        "DDI (1-5)", "Driver (1-5)", "Trip (1-5)", "Composite Avg",
        "Comments", "Channel", "Driver Name", "Vehicle ID",
        "NEMT Order ID", "PRISM Order ID", "VERTEX Trip ID", "Audit File",
    ])
    for r in sorted(records, key=lambda x: x.get("completed_at") or ""):
        snap = r.get("trip_snapshot") or {}
        writer.writerow([
            r.get("trip_ref"),
            r.get("payer"),
            r.get("member_name"),
            r.get("trip_purpose"),
            snap.get("transport_label") or snap.get("transport_type"),
            snap.get("pickup_time"),
            snap.get("actual_pickup_time"),
            snap.get("actual_dropoff_time"),
            snap.get("actual_mileage"),
            snap.get("pickup_address"),
            snap.get("dropoff_address"),
            r.get("completed_at"),
            r.get("sent_at"),
            r.get("reminder_sent_at"),
            r.get("responded_at"),
            r.get("ddi_grade"),
            r.get("driver_grade"),
            r.get("trip_grade"),
            r.get("overall_grade"),
            r.get("ddi_rating"),
            r.get("driver_rating"),
            r.get("trip_rating"),
            r.get("overall_average"),
            r.get("comments") or "",
            r.get("response_channel") or "",
            r.get("driver_name") or "",
            snap.get("vehicle_id") or "",
            r.get("nemt_order_id"),
            r.get("prism_order_id"),
            r.get("vertex_trip_id"),
            r.get("audit_archive_path") or "",
        ])
    return buf.getvalue()


def _render_survey_page(**kwargs):
    return render_template_string(
        _SURVEY_PAGE,
        grades=_GRADE_OPTIONS,
        **kwargs,
    )


# ─── Flask routes ─────────────────────────────────────────────────────────────

@member_survey.route("/member/survey/<token>", methods=["GET"])
def survey_form(token: str):
    log = _load_log()
    rec = next((r for r in log if r.get("token") == token), None)
    care = member_care_phone_display()
    if not rec:
        return _render_survey_page(
            brand=BRAND_NAME,
            care_phone=care,
            error="This grade link has expired or is invalid.",
            submitted=False,
        ), 404
    if rec.get("status") == "completed":
        return _render_survey_page(
            brand=BRAND_NAME,
            care_phone=care,
            submitted=True,
            error=None,
        )
    return _render_survey_page(
        brand=BRAND_NAME,
        care_phone=care,
        first_name=_first_name(rec.get("member_name", "")),
        ref=rec.get("trip_ref", ""),
        submitted=False,
        error=None,
    )


@member_survey.route("/member/survey/<token>", methods=["POST"])
def survey_submit(token: str):
    care = member_care_phone_display()
    ddi_g = request.form.get("ddi_grade") or request.form.get("ddi_rating")
    drv_g = request.form.get("driver_grade") or request.form.get("driver_rating")
    trip_g = request.form.get("trip_grade") or request.form.get("trip_rating")

    result = submit_survey_response(
        token,
        ddi_grade=str(ddi_g) if ddi_g and not str(ddi_g).isdigit() else None,
        driver_grade=str(drv_g) if drv_g and not str(drv_g).isdigit() else None,
        trip_grade=str(trip_g) if trip_g and not str(trip_g).isdigit() else None,
        ddi_rating=int(ddi_g) if str(ddi_g or "").isdigit() else None,
        driver_rating=int(drv_g) if str(drv_g or "").isdigit() else None,
        trip_rating=int(trip_g) if str(trip_g or "").isdigit() else None,
        comments=request.form.get("comments", ""),
        response_channel="sms_link",
    )
    if not result.get("success"):
        return _render_survey_page(
            brand=BRAND_NAME,
            care_phone=care,
            error=result.get("error", "Please select a grade (A–F) for each category."),
            submitted=False,
        ), 400

    return _render_survey_page(
        brand=BRAND_NAME,
        care_phone=care,
        submitted=True,
        error=None,
    )


@member_survey.route("/prism/nemt/satisfaction/pending", methods=["GET"])
def satisfaction_pending():
    """Portal gate: ungraded trips for this member."""
    email = _normalize_email(request.args.get("email") or "")
    phone = (request.args.get("phone") or "").strip()
    raw_ids = request.args.get("order_ids") or ""
    prism_order_ids = [x.strip() for x in raw_ids.split(",") if x.strip()]
    if not email and not phone and not prism_order_ids:
        return jsonify({"error": "email, phone, or order_ids required"}), 400
    pending = get_pending_surveys_for_member(email, phone=phone, prism_order_ids=prism_order_ids)
    return jsonify({
        "pending": pending,
        "count": len(pending),
        "requires_grade_before_schedule": len(pending) > 0,
        "requires_survey_before_schedule": len(pending) > 0,
        "email": email or None,
    })


@member_survey.route("/prism/nemt/satisfaction/submit", methods=["POST"])
def satisfaction_submit_json():
    """JSON grade submit — portal modal or mobile client."""
    data = request.get_json(force=True, silent=True) or {}
    token = (data.get("token") or "").strip()
    if not token:
        return jsonify({"success": False, "error": "token required"}), 400

    result = submit_survey_response(
        token,
        ddi_grade=data.get("ddi_grade"),
        driver_grade=data.get("driver_grade"),
        trip_grade=data.get("trip_grade"),
        ddi_rating=data.get("ddi_rating"),
        driver_rating=data.get("driver_rating"),
        trip_rating=data.get("trip_rating"),
        comments=(data.get("comments") or ""),
        response_channel=(data.get("channel") or "portal"),
    )
    if not result.get("success"):
        status = 400 if "grade" in (result.get("error") or "").lower() else 404
        return jsonify(result), status
    return jsonify(result)


@member_survey.route("/prism/nemt/satisfaction/mco-packet.html", methods=["GET"])
def satisfaction_mco_packet_html():
    """Beautiful print-ready MCO quality packet — all graded trips for a payer."""
    payer = (request.args.get("payer") or "").strip()
    records = _load_log()
    if payer:
        pl = payer.lower()
        records = [r for r in records if pl in (r.get("payer") or "").lower()]
    from member_trip_grade_audit_report import render_mco_packet_html

    html_out = render_mco_packet_html(payer, records, audit_summary(payer=payer or None))
    return Response(html_out, mimetype="text/html; charset=utf-8")


@member_survey.route("/prism/nemt/satisfaction/trip/<nemt_order_id>.html", methods=["GET"])
def satisfaction_trip_html(nemt_order_id: str):
    """Beautiful print-ready single-trip grade record."""
    oid = (nemt_order_id or "").strip()
    rec = next((r for r in _load_log() if r.get("nemt_order_id") == oid), None)
    if not rec:
        return Response("<h1>Trip record not found</h1>", status=404, mimetype="text/html")
    from member_trip_grade_audit_report import render_trip_detail_html

    return Response(render_trip_detail_html(rec), mimetype="text/html; charset=utf-8")


@member_survey.route("/prism/nemt/satisfaction/record/<nemt_order_id>", methods=["GET"])
def satisfaction_record_detail(nemt_order_id: str):
    """Full audit record for one trip (master log + archive path)."""
    oid = (nemt_order_id or "").strip()
    rec = next((r for r in _load_log() if r.get("nemt_order_id") == oid), None)
    if not rec:
        return jsonify({"error": "No survey record for this trip"}), 404
    return jsonify({"record": rec})


@member_survey.route("/prism/nemt/satisfaction/summary", methods=["GET"])
def satisfaction_summary():
    payer = request.args.get("payer")
    return jsonify(audit_summary(payer=payer))


@member_survey.route("/prism/nemt/satisfaction/export.csv", methods=["GET"])
def satisfaction_export_csv():
    payer = request.args.get("payer")
    csv_data = export_audit_csv(payer=payer)
    filename = f"ddi_trip_grades_{datetime.now(EASTERN).strftime('%Y%m%d')}.csv"
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
