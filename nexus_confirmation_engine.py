#!/usr/bin/env python3
"""
NEXUS Confirmation Engine
=========================
System-wide appointment / meeting / signing confirmation layer for Dee Davis Inc.

When ANY scheduled event is created — PRISM appointment, notary signing, CO meeting,
calendar event — call `send_confirmation_request()`. The other party gets an email
AND a text immediately, both requesting confirmation. Status is tracked. Reminders
fire automatically if no response.

Reuses Twilio + SendGrid from shield_notifications.py — no new credentials needed.

Env vars (shared with SHIELD):
  TWILIO_ACCOUNT_SID      Twilio account SID
  TWILIO_AUTH_TOKEN       Twilio auth token
  TWILIO_FROM_NUMBER      Twilio sending number (+1XXXXXXXXXX)
  SENDGRID_API_KEY        SendGrid API key
  SENDGRID_FROM_EMAIL     Verified sender (e.g. info@deedavis.biz)
  NEXUS_CONFIRM_BASE_URL  Public base URL for confirmation links (e.g. https://nexus.deedavis.biz)

Confirmation log: uploads/confirmations/confirmation_log.json
"""

from __future__ import annotations

import os
import json
import uuid
import logging
import threading
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from zoneinfo import ZoneInfo

logger = logging.getLogger("nexus.confirmation")

from company_info import BRAND_NAME, COMPANY_NAME, member_care_phone_display, PHONE_PRIMARY

EASTERN = ZoneInfo("America/Detroit")

# ─────────────────────────────────────────────────────────────────────────────
# Storage
# ─────────────────────────────────────────────────────────────────────────────

_BASE_DIR = os.path.dirname(__file__)
_LOG_DIR  = os.path.join(_BASE_DIR, "uploads", "confirmations")
_LOG_FILE = os.path.join(_LOG_DIR, "confirmation_log.json")
os.makedirs(_LOG_DIR, exist_ok=True)


def _load_log() -> List[Dict[str, Any]]:
    if not os.path.exists(_LOG_FILE):
        return []
    try:
        with open(_LOG_FILE) as f:
            return json.load(f)
    except Exception:
        return []


def _save_log(records: List[Dict[str, Any]]) -> None:
    with open(_LOG_FILE, "w") as f:
        json.dump(records, f, indent=2)


# ─────────────────────────────────────────────────────────────────────────────
# Config helpers (mirror shield_notifications pattern)
# ─────────────────────────────────────────────────────────────────────────────

def _twilio_ok() -> bool:
    return bool(
        os.environ.get("TWILIO_ACCOUNT_SID")
        and os.environ.get("TWILIO_AUTH_TOKEN")
        and os.environ.get("TWILIO_FROM_NUMBER")
    )


def _sendgrid_ok() -> bool:
    return bool(
        os.environ.get("SENDGRID_API_KEY")
        and os.environ.get("SENDGRID_FROM_EMAIL")
    )


def _confirm_url(token: str) -> str:
    base = os.environ.get("NEXUS_CONFIRM_BASE_URL", "").rstrip("/")
    if not base:
        return ""
    return f"{base}/nexus/confirm/{token}"


def _clean_phone(raw: str) -> str:
    """Strip formatting, ensure E.164."""
    import re
    digits = re.sub(r"\D", "", raw or "")
    if len(digits) == 10:
        return f"+1{digits}"
    if len(digits) == 11 and digits.startswith("1"):
        return f"+{digits}"
    return f"+{digits}" if digits else ""


# ─────────────────────────────────────────────────────────────────────────────
# Event type labels — used in messages
# ─────────────────────────────────────────────────────────────────────────────

_EVENT_LABELS: Dict[str, str] = {
    "prism_appointment":  "appointment",
    "notary_signing":     "notary signing",
    "co_meeting":         "meeting",
    "calendar_event":     "meeting",
    "dna_collection":     "DNA collection appointment",
    "fingerprint":        "fingerprinting appointment",
    "drug_test":          "drug testing appointment",
    "occ_health":         "occupational health appointment",
    "nemt_ride":          "transport pickup",
    "general":            "appointment",
}


# ─────────────────────────────────────────────────────────────────────────────
# Message builders — WHO / WHAT / WHEN / WHERE / WHY in every message
# ─────────────────────────────────────────────────────────────────────────────

def _build_sms(event_type: str, party_name: str, dt_str: str,
               location: str, confirm_url: str, ref: str,
               who: str = "", what: str = "", why: str = "",
               bring: str = "") -> str:
    """
    Args:
        who:   Who from DDI they're meeting / who is performing the service
        what:  Specific description of what's happening
        why:   Purpose / reason for the appointment
        bring: What the person needs to bring or prepare
    """
    label = _EVENT_LABELS.get(event_type, "appointment")
    what_line  = what  or label.capitalize()
    care = member_care_phone_display()
    who_line   = who   or f"{BRAND_NAME} ({care})"
    why_line   = why   or ""
    bring_line = bring or ""

    lines = [
        f"Hi {party_name} — {BRAND_NAME} here.",
        "",
        f"Here are your details for your upcoming {label}:",
        "",
        f"👤 WHO:   {who_line}",
        f"📋 WHAT:  {what_line}",
        f"📅 WHEN:  {dt_str}",
        f"📍 WHERE: {location}",
    ]
    if why_line:
        lines.append(f"📌 WHY:   {why_line}")
    if bring_line:
        lines.append(f"🎒 BRING: {bring_line}")

    lines += ["", f"Ref: {ref}", ""]

    if confirm_url:
        lines += [f"Confirm here: {confirm_url}", "", "— or —", ""]
    lines.append("Reply CONFIRM to confirm or CANCEL to cancel.")
    lines.append(f"Questions? Call/text {care}")

    return "\n".join(lines)


def _build_email(event_type: str, party_name: str, dt_str: str,
                 location: str, confirm_url: str, ref: str,
                 notes: str,
                 who: str = "", what: str = "", why: str = "",
                 bring: str = "") -> Dict[str, str]:
    label     = _EVENT_LABELS.get(event_type, "appointment")
    label_cap = label.capitalize()
    what_val  = what  or label_cap
    who_val   = who   or BRAND_NAME
    why_val   = why   or "—"
    bring_val = bring or ""

    confirm_btn = ""
    if confirm_url:
        confirm_btn = (
            f'<p style="margin:24px 0;">'
            f'<a href="{confirm_url}" style="background:#1e40af;color:#fff;padding:14px 32px;'
            f'border-radius:6px;text-decoration:none;font-weight:bold;font-size:15px;">'
            f'✅ Confirm My {label_cap}</a>'
            f'&nbsp;&nbsp;'
            f'<a href="{confirm_url.replace("/confirm/", "/cancel/")}" '
            f'style="background:#dc2626;color:#fff;padding:14px 24px;'
            f'border-radius:6px;text-decoration:none;font-weight:bold;font-size:15px;">'
            f'❌ Cancel</a></p>'
            f'<p style="color:#6b7280;font-size:13px;">'
            f'Or reply <strong>CONFIRM</strong> or <strong>CANCEL</strong> to this email.</p>'
        )
    else:
        confirm_btn = (
            '<p style="color:#374151;font-size:14px;">'
            'Reply <strong>CONFIRM</strong> to confirm or <strong>CANCEL</strong> to cancel.</p>'
        )

    bring_row = (
        f'<tr><td style="padding:10px 14px;background:#eff6ff;font-weight:bold;'
        f'border:1px solid #bfdbfe;width:130px;">🎒 Bring / Prep</td>'
        f'<td style="padding:10px 14px;border:1px solid #bfdbfe;">{bring_val}</td></tr>'
    ) if bring_val else ""

    notes_block = (
        f'<div style="background:#fefce8;border:1px solid #fde047;border-radius:6px;'
        f'padding:14px 16px;margin:16px 0;">'
        f'<strong>📝 Additional Notes:</strong><br/>{notes}</div>'
    ) if notes else ""

    care = member_care_phone_display()
    html = f"""
<div style="font-family:Arial,sans-serif;max-width:580px;margin:0 auto;color:#111;">
  <div style="background:#1e40af;padding:22px 28px;border-radius:8px 8px 0 0;">
    <h2 style="color:#fff;margin:0;font-size:20px;">
      {label_cap} — Please Confirm
    </h2>
    <p style="color:#bfdbfe;margin:6px 0 0;font-size:14px;">{BRAND_NAME} · info@deedavis.biz · {care}</p>
  </div>
  <div style="background:#f9fafb;padding:28px;border:1px solid #e5e7eb;border-radius:0 0 8px 8px;">
    <p style="font-size:16px;">Hi <strong>{party_name}</strong>,</p>
    <p>Please review and confirm the details below for your upcoming {label}.</p>

    <table style="width:100%;border-collapse:collapse;margin:20px 0;">
      <tr>
        <td style="padding:10px 14px;background:#eff6ff;font-weight:bold;
                   border:1px solid #bfdbfe;width:130px;">👤 Who</td>
        <td style="padding:10px 14px;border:1px solid #bfdbfe;">{who_val}</td>
      </tr>
      <tr>
        <td style="padding:10px 14px;background:#eff6ff;font-weight:bold;
                   border:1px solid #bfdbfe;">📋 What</td>
        <td style="padding:10px 14px;border:1px solid #bfdbfe;">{what_val}</td>
      </tr>
      <tr>
        <td style="padding:10px 14px;background:#eff6ff;font-weight:bold;
                   border:1px solid #bfdbfe;">📅 When</td>
        <td style="padding:10px 14px;border:1px solid #bfdbfe;"><strong>{dt_str}</strong></td>
      </tr>
      <tr>
        <td style="padding:10px 14px;background:#eff6ff;font-weight:bold;
                   border:1px solid #bfdbfe;">📍 Where</td>
        <td style="padding:10px 14px;border:1px solid #bfdbfe;">{location}</td>
      </tr>
      <tr>
        <td style="padding:10px 14px;background:#eff6ff;font-weight:bold;
                   border:1px solid #bfdbfe;">📌 Why</td>
        <td style="padding:10px 14px;border:1px solid #bfdbfe;">{why_val}</td>
      </tr>
      {bring_row}
      <tr>
        <td style="padding:10px 14px;background:#eff6ff;font-weight:bold;
                   border:1px solid #bfdbfe;">🔖 Reference</td>
        <td style="padding:10px 14px;border:1px solid #bfdbfe;color:#6b7280;font-size:13px;">{ref}</td>
      </tr>
    </table>

    {notes_block}
    {confirm_btn}

    <hr style="border:none;border-top:1px solid #e5e7eb;margin:24px 0;"/>
    <p style="color:#6b7280;font-size:13px;">
      Need to reschedule? Call or text <strong>{care}</strong> or reply to this email.<br/>
      <strong>{BRAND_NAME}</strong> · 755 W. Big Beaver Rd., Suite 2020, Troy, MI 48084<br/>
      Legal entity: {COMPANY_NAME} · Member care: {care}<br/>
      Office: {PHONE_PRIMARY} · EDWOSB · WOSB · MBE · info@deedavis.biz
    </p>
  </div>
</div>
"""
    return {
        "subject": f"Please confirm: {what_val} — {dt_str}",
        "html": html,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Delivery — thin wrappers that call Twilio / SendGrid directly
#            (same pattern as shield_notifications.py, no import dependency)
# ─────────────────────────────────────────────────────────────────────────────

def _send_sms_raw(to: str, body: str) -> Dict[str, Any]:
    if not _twilio_ok():
        return {"success": False, "channel": "sms", "error": "Twilio not configured", "skipped": True}
    phone = _clean_phone(to)
    if not phone:
        return {"success": False, "channel": "sms", "error": "Invalid phone number"}
    try:
        from twilio.rest import Client
        cl = Client(os.environ["TWILIO_ACCOUNT_SID"], os.environ["TWILIO_AUTH_TOKEN"])
        msg = cl.messages.create(body=body, from_=os.environ["TWILIO_FROM_NUMBER"], to=phone)
        return {"success": True, "channel": "sms", "sid": msg.sid, "to": phone}
    except Exception as exc:
        logger.error("Twilio error: %s", exc)
        return {"success": False, "channel": "sms", "error": str(exc)}


def _send_email_raw(to: str, subject: str, html: str, cc: Optional[str] = None) -> Dict[str, Any]:
    if not _sendgrid_ok():
        return {"success": False, "channel": "email", "error": "SendGrid not configured", "skipped": True}
    try:
        import sendgrid as sg_module
        from sendgrid.helpers.mail import Mail, Email, To, Content, Cc
        sg = sg_module.SendGridAPIClient(os.environ["SENDGRID_API_KEY"])
        mail = Mail(
            from_email=Email(os.environ["SENDGRID_FROM_EMAIL"]),
            to_emails=To(to),
            subject=subject,
        )
        mail.content = [Content("text/html", html)]
        if cc:
            mail.cc = [Cc(cc)]
        resp = sg.client.mail.send.post(request_body=mail.get())
        return {"success": resp.status_code in (200, 202), "channel": "email",
                "status_code": resp.status_code, "to": to}
    except Exception as exc:
        logger.error("SendGrid error: %s", exc)
        return {"success": False, "channel": "email", "error": str(exc)}


# ─────────────────────────────────────────────────────────────────────────────
# Log helpers
# ─────────────────────────────────────────────────────────────────────────────

def _log_record(token: str, event_type: str, party_name: str,
                party_email: str, party_phone: str, dt_str: str,
                location: str, internal_id: str, notes: str,
                who: str = "", what: str = "", why: str = "",
                bring: str = "") -> Dict[str, Any]:
    record = {
        "token": token,
        "event_type": event_type,
        "party_name": party_name,
        "party_email": party_email,
        "party_phone": party_phone,
        "datetime_str": dt_str,
        "location": location,
        "internal_id": internal_id,
        "notes": notes,
        "who": who,
        "what": what,
        "why": why,
        "bring": bring,
        "status": "pending",           # pending | confirmed | cancelled | no_response
        "created_at": datetime.now(EASTERN).isoformat(),
        "confirmed_at": None,
        "reminder_1_sent": False,       # 2-hour reminder
        "reminder_2_sent": False,       # 24-hour escalation to Dee
        "sms_result": None,
        "email_result": None,
    }
    log = _load_log()
    log.insert(0, record)
    _save_log(log)
    return record


def _update_log(token: str, **kwargs: Any) -> None:
    log = _load_log()
    for rec in log:
        if rec.get("token") == token:
            rec.update(kwargs)
            break
    _save_log(log)


# ─────────────────────────────────────────────────────────────────────────────
# Reminder scheduler — runs in a background thread
# ─────────────────────────────────────────────────────────────────────────────

def _schedule_reminders(token: str, party_phone: str, party_email: str,
                         party_name: str, event_type: str,
                         dt_str: str, location: str) -> None:
    """
    Non-blocking: waits 2 hours for confirmation, then sends a reminder.
    After another 22 hours (24h total), alerts Dee if still unconfirmed.
    """
    import time

    def _run() -> None:
        # ── 2-hour reminder ──────────────────────────────────────────────
        time.sleep(2 * 3600)
        log = _load_log()
        rec = next((r for r in log if r["token"] == token), None)
        if rec and rec["status"] == "pending":
            label = _EVENT_LABELS.get(event_type, "appointment")
            body = (
                f"Reminder: Your {label} with {BRAND_NAME} on {dt_str} "
                f"at {location} is still awaiting confirmation.\n"
                f"Reply CONFIRM to confirm or CANCEL to cancel."
            )
            if party_phone:
                _send_sms_raw(party_phone, body)
            _update_log(token, reminder_1_sent=True)

        # ── 24-hour escalation to Dee ────────────────────────────────────
        time.sleep(22 * 3600)
        log = _load_log()
        rec = next((r for r in log if r["token"] == token), None)
        if rec and rec["status"] == "pending":
            label = _EVENT_LABELS.get(event_type, "appointment")
            alert = (
                f"⚠️ NEXUS ALERT: No confirmation received from {party_name} "
                f"for {label} on {dt_str} at {location}. "
                f"Manual follow-up needed. Ref: {token[:12]}"
            )
            dee_phone = os.environ.get("DEE_PHONE", "")
            dee_email = os.environ.get("NEXUS_EMAIL", "info@deedavis.biz")
            if dee_phone:
                _send_sms_raw(dee_phone, alert)
            if dee_email:
                _send_email_raw(
                    dee_email,
                    f"⚠️ No confirmation — {party_name} / {label}",
                    f"<p>{alert}</p>",
                )
            _update_log(token, reminder_2_sent=True, status="no_response")

    t = threading.Thread(target=_run, daemon=True)
    t.start()


# ─────────────────────────────────────────────────────────────────────────────
# PUBLIC API
# ─────────────────────────────────────────────────────────────────────────────

def send_confirmation_request(
    event_type: str,
    party_name: str,
    party_email: str,
    party_phone: str,
    datetime_str: str,
    location: str,
    internal_id: str,
    notes: str = "",
    cc_dee: bool = True,
    who: str = "",
    what: str = "",
    why: str = "",
    bring: str = "",
) -> Dict[str, Any]:
    """
    Send an email + SMS confirmation request to the other party.

    Args:
        event_type:   One of the keys in _EVENT_LABELS (e.g. 'prism_appointment',
                      'notary_signing', 'co_meeting', 'calendar_event', 'general')
        party_name:   Recipient's name
        party_email:  Recipient's email address (empty string = skip email)
        party_phone:  Recipient's phone (any format — cleaned internally)
        datetime_str: Human-readable date/time ("Mon May 5, 2026 at 2:00 PM ET")
        location:     Address or "Zoom / Video Call" etc.
        internal_id:  PRISM order ID, calendar event ID, etc. (for reference)
        notes:        Optional extra detail shown in email
        cc_dee:       CC info@deedavis.biz on the confirmation email (default True)
        who:          WHO — who they're meeting / who is performing the service
                      e.g. "Dieasha D. Davis, President & CEO, Dee Davis Inc."
                      e.g. "Mobile collector assigned by Dee Davis Inc."
        what:         WHAT — specific description of what's happening
                      e.g. "DOT urine drug screen (5-panel)"
                      e.g. "Notary signing — loan closing documents"
                      e.g. "Capability statement review call"
        why:          WHY — purpose / reason
                      e.g. "Required for pre-employment clearance"
                      e.g. "Per your request for notarized affidavit"
                      e.g. "Follow-up to solicitation W912DR25QA005"
        bring:        What they need to bring or prepare
                      e.g. "Government-issued photo ID required"
                      e.g. "Bring all pages of the loan documents"

    Returns:
        Dict with token, confirm_url, sms_result, email_result, status
    """
    token = uuid.uuid4().hex
    url   = _confirm_url(token)
    cc    = "info@deedavis.biz" if cc_dee else None

    # Build messages — full who/what/when/where/why in both channels
    sms_body   = _build_sms(event_type, party_name, datetime_str, location,
                             url, internal_id, who=who, what=what, why=why, bring=bring)
    email_tmpl = _build_email(event_type, party_name, datetime_str, location,
                               url, internal_id, notes,
                               who=who, what=what, why=why, bring=bring)

    # Log first (so reminders can find it even if sends are slow)
    _log_record(token, event_type, party_name, party_email, party_phone,
                datetime_str, location, internal_id, notes,
                who=who, what=what, why=why, bring=bring)

    # Dispatch — fire both channels
    sms_result   = _send_sms_raw(party_phone, sms_body) if party_phone else {"skipped": True, "reason": "no phone"}
    email_result = _send_email_raw(party_email, email_tmpl["subject"], email_tmpl["html"], cc=cc) \
                   if party_email else {"skipped": True, "reason": "no email"}

    # Persist delivery results
    _update_log(token, sms_result=sms_result, email_result=email_result)

    # Start reminder thread
    _schedule_reminders(token, party_phone, party_email, party_name,
                        event_type, datetime_str, location)

    logger.info("Confirmation sent | token=%s | party=%s | event=%s | sms=%s | email=%s",
                token, party_name, event_type,
                sms_result.get("success"), email_result.get("success"))

    return {
        "token": token,
        "confirm_url": url,
        "sms_result": sms_result,
        "email_result": email_result,
        "status": "sent",
    }


def mark_confirmed(token: str, channel: str = "link") -> Dict[str, Any]:
    """
    Mark a confirmation as confirmed. Called by the /nexus/confirm/<token> endpoint
    or when an inbound SMS keyword CONFIRM is received.
    """
    log = _load_log()
    rec = next((r for r in log if r["token"] == token), None)
    if not rec:
        return {"success": False, "error": "Token not found"}

    if rec["status"] in ("confirmed", "cancelled"):
        return {"success": True, "already": True, "status": rec["status"]}

    _update_log(token, status="confirmed",
                confirmed_at=datetime.now(EASTERN).isoformat(),
                confirmed_via=channel)

    # Notify Dee that confirmation came in
    dee_email = os.environ.get("NEXUS_EMAIL", "info@deedavis.biz")
    label = _EVENT_LABELS.get(rec.get("event_type", "general"), "appointment")
    _send_email_raw(
        dee_email,
        f"✅ Confirmed — {rec['party_name']} / {label}",
        f"<p><strong>{rec['party_name']}</strong> confirmed their "
        f"{label} on <strong>{rec['datetime_str']}</strong> "
        f"at <strong>{rec['location']}</strong> via {channel}.</p>"
        f"<p>Ref: {rec['internal_id']}</p>",
    )

    return {"success": True, "status": "confirmed", "party": rec["party_name"]}


def mark_cancelled(token: str, channel: str = "link") -> Dict[str, Any]:
    """Mark a confirmation as cancelled."""
    log = _load_log()
    rec = next((r for r in log if r["token"] == token), None)
    if not rec:
        return {"success": False, "error": "Token not found"}

    _update_log(token, status="cancelled",
                confirmed_at=datetime.now(EASTERN).isoformat(),
                confirmed_via=channel)

    # Alert Dee immediately on cancellation
    dee_phone = os.environ.get("DEE_PHONE", "")
    dee_email = os.environ.get("NEXUS_EMAIL", "info@deedavis.biz")
    label = _EVENT_LABELS.get(rec.get("event_type", "general"), "appointment")

    alert_body = (
        f"❌ CANCELLED: {rec['party_name']} cancelled their "
        f"{label} on {rec['datetime_str']} at {rec['location']}. "
        f"Ref: {rec['internal_id']}"
    )
    if dee_phone:
        _send_sms_raw(dee_phone, alert_body)
    _send_email_raw(
        dee_email,
        f"❌ Cancelled — {rec['party_name']} / {label}",
        f"<p>{alert_body}</p>",
    )
    return {"success": True, "status": "cancelled", "party": rec["party_name"]}


def get_confirmation_status(token: str) -> Optional[Dict[str, Any]]:
    """Look up confirmation status by token."""
    log = _load_log()
    return next((r for r in log if r["token"] == token), None)


def get_pending_confirmations() -> List[Dict[str, Any]]:
    """Return all confirmations still awaiting a response."""
    return [r for r in _load_log() if r.get("status") == "pending"]
