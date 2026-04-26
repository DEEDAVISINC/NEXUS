"""
SHIELD Notification Engine
DEE DAVIS INC + CAUSE WE CARE

Centralized email (Airtable SendGrid) + SMS (Twilio) dispatch for the SHIELD
lead screening system. Every notification logs to the Notifications table in
Airtable so navigators can see delivery status on the dashboard.

Env vars required:
  TWILIO_ACCOUNT_SID    — Twilio account SID
  TWILIO_AUTH_TOKEN      — Twilio auth token
  TWILIO_FROM_NUMBER     — Twilio phone number (e.g. +13135550100)
  SENDGRID_API_KEY       — SendGrid API key
  SENDGRID_FROM_EMAIL    — Verified sender (e.g. care@causewecareorg.com)
  SHIELD_STATUS_URL      — Public URL for family status page (e.g. https://yoursite.com/status)

All optional at boot — if missing, that channel is disabled (not a crash).
Navigators see "SMS disabled" or "Email disabled" on the dashboard.
"""

from __future__ import annotations

import os
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from zoneinfo import ZoneInfo

logger = logging.getLogger("shield.notifications")

EASTERN = ZoneInfo("America/New_York")

# ─────────────────────────────────────────────────────────────────────────────
# Config — lazy-loaded from env
# ─────────────────────────────────────────────────────────────────────────────

def _twilio_configured() -> bool:
    return bool(os.environ.get("TWILIO_ACCOUNT_SID") and os.environ.get("TWILIO_AUTH_TOKEN") and os.environ.get("TWILIO_FROM_NUMBER"))

def _sendgrid_configured() -> bool:
    return bool(os.environ.get("SENDGRID_API_KEY") and os.environ.get("SENDGRID_FROM_EMAIL"))

def _status_url() -> str:
    return os.environ.get("SHIELD_STATUS_URL", "").rstrip("/") or ""


# ─────────────────────────────────────────────────────────────────────────────
# Message Templates — plain language, family-friendly
# ─────────────────────────────────────────────────────────────────────────────

def _sms_templates() -> Dict[str, str]:
    url = _status_url()
    status_link = f"\n\nTrack your progress anytime: {url}/status" if url else ""

    return {
        "referral_received": (
            "Hi {family_name} family — this is Cause We Care. We received your referral "
            "(case #{case_number}). Someone from our team will be reaching out to you soon. "
            "You're not alone in this. 💛{status_link}"
        ),
        "navigator_assigned": (
            "Good news! {navigator_name} from Cause We Care will be helping your family. "
            "You can call or text them directly at {navigator_phone}. "
            "They'll be reaching out shortly to introduce themselves. 💛"
        ),
        "appointment_scheduled": (
            "📅 You have an appointment coming up!\n\n"
            "{service_name}\n"
            "{appointment_date}\n"
            "{vendor}\n\n"
            "Questions? Text your navigator {navigator_name} at {navigator_phone}."
        ),
        "service_completed": (
            "✅ {service_name} is complete! One less thing to worry about. "
            "Your navigator {navigator_name} is keeping everything on track for your family. 💛"
        ),
        "case_closed": (
            "🎉 Great news — all of your family's services are complete! "
            "Case #{case_number} is now closed. If you ever need help again, "
            "Cause We Care is just a call or text away. We're proud of you. 💛"
        ),
        "appointment_reminder": (
            "⏰ Reminder: {service_name} tomorrow!\n\n"
            "{appointment_date}\n"
            "{vendor}\n\n"
            "Need to reschedule? Text {navigator_name} at {navigator_phone}."
        ),
    }


def _email_templates() -> Dict[str, Dict[str, str]]:
    url = _status_url()
    status_line = f'<p>Track your family\'s progress anytime: <a href="{url}/status">{url}/status</a></p>' if url else ""

    return {
        "referral_received_family": {
            "subject": "Cause We Care received your referral — case #{case_number}",
            "html": (
                "<p>Hi {family_name} family,</p>"
                "<p>We received your information and your case number is <strong>#{case_number}</strong>. "
                "Please save this number — you can use it to check on your family's progress at any time.</p>"
                "{status_line}"
                "<p>A member of our team will be reaching out within 48 hours to introduce themselves and "
                "start coordinating your services. You don't have to figure this out alone.</p>"
                "<p>💛 <strong>Care. Navigate. Transform.</strong></p>"
                "<p>— The Cause We Care Team</p>"
            ),
        },
        "referral_received_caseworker": {
            "subject": "SHIELD referral confirmed — case #{case_number}",
            "html": (
                "<p>Hi {caseworker_name},</p>"
                "<p>Referral <strong>#{case_number}</strong> for the <strong>{family_name}</strong> family "
                "has been received and the SLA clock has started.</p>"
                "<ul>"
                "<li><strong>Case number:</strong> {case_number}</li>"
                "<li><strong>County:</strong> {county}</li>"
                "<li><strong>Urgency:</strong> {urgency}</li>"
                "<li><strong>First contact SLA:</strong> {sla_hours} hours</li>"
                "</ul>"
                "<p>You will be copied on status updates through service completion. "
                "If you need anything, reply to this email or contact your DDI/CWC liaison.</p>"
                "<p>— SHIELD · Dee Davis Inc + Cause We Care</p>"
            ),
        },
        "navigator_assigned_family": {
            "subject": "Meet your navigator — {navigator_name} from Cause We Care",
            "html": (
                "<p>Hi {family_name} family,</p>"
                "<p>Great news — <strong>{navigator_name}</strong> from Cause We Care has been assigned "
                "to help your family. They're your go-to person for everything.</p>"
                "<p><strong>Call or text:</strong> {navigator_phone}<br/>"
                "<strong>Email:</strong> {navigator_email}</p>"
                "<p>{navigator_name} will be reaching out shortly to say hello and schedule your first visit.</p>"
                "<p>💛 Care. Navigate. Transform.</p>"
                "<p>— Cause We Care</p>"
            ),
        },
        "case_closed_family": {
            "subject": "All done! Case #{case_number} complete 🎉",
            "html": (
                "<p>Hi {family_name} family,</p>"
                "<p>All of your services are complete and case <strong>#{case_number}</strong> is now closed.</p>"
                "<p>If you ever need help again, Cause We Care is always here. Just call or text us.</p>"
                "<p>We're proud of you. 💛</p>"
                "<p><strong>Care. Navigate. Transform.</strong><br/>"
                "<em>More than a mission — a movement.</em></p>"
                "<p>— The Cause We Care Team</p>"
            ),
        },
        "case_closed_caseworker": {
            "subject": "SHIELD case #{case_number} — closed, outcomes complete",
            "html": (
                "<p>Hi {caseworker_name},</p>"
                "<p>Case <strong>#{case_number}</strong> for the <strong>{family_name}</strong> family "
                "is now complete. All services have been delivered and the case is closed.</p>"
                "<ul>"
                "<li><strong>Services delivered:</strong> {services_list}</li>"
                "<li><strong>Duration:</strong> {duration_days} days</li>"
                "</ul>"
                "<p>Thank you for the referral. We're here whenever your next family needs help.</p>"
                "<p>— SHIELD · Dee Davis Inc + Cause We Care</p>"
            ),
        },
    }


# ─────────────────────────────────────────────────────────────────────────────
# Dispatch — SMS via Twilio
# ─────────────────────────────────────────────────────────────────────────────

def send_sms(to_number: str, template_key: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """Send an SMS via Twilio. Returns delivery status for logging."""
    if not _twilio_configured():
        return {"success": False, "channel": "sms", "error": "Twilio not configured", "skipped": True}

    to_clean = _clean_phone(to_number)
    if not to_clean:
        return {"success": False, "channel": "sms", "error": "Invalid phone number"}

    templates = _sms_templates()
    template = templates.get(template_key)
    if not template:
        return {"success": False, "channel": "sms", "error": f"Unknown template: {template_key}"}

    context["status_link"] = f"\n\nTrack your progress: {_status_url()}/status" if _status_url() else ""
    body = template.format(**{k: str(v) for k, v in context.items()})

    try:
        from twilio.rest import Client
        client = Client(
            os.environ["TWILIO_ACCOUNT_SID"],
            os.environ["TWILIO_AUTH_TOKEN"],
        )
        message = client.messages.create(
            body=body,
            from_=os.environ["TWILIO_FROM_NUMBER"],
            to=to_clean,
        )
        logger.info(f"SMS sent: {template_key} → {to_clean} (SID: {message.sid})")
        return {
            "success": True,
            "channel": "sms",
            "template": template_key,
            "to": to_clean,
            "twilio_sid": message.sid,
            "status": message.status,
            "sent_at": datetime.now(EASTERN).isoformat(),
        }
    except Exception as e:
        logger.error(f"SMS failed: {template_key} → {to_clean}: {e}")
        return {"success": False, "channel": "sms", "error": str(e), "template": template_key}


# ─────────────────────────────────────────────────────────────────────────────
# Dispatch — Email via SendGrid
# ─────────────────────────────────────────────────────────────────────────────

def send_email(to_email: str, template_key: str, context: Dict[str, Any], cc: Optional[str] = None) -> Dict[str, Any]:
    """Send an email via SendGrid. Returns delivery status for logging."""
    if not _sendgrid_configured():
        return {"success": False, "channel": "email", "error": "SendGrid not configured", "skipped": True}

    if not to_email or "@" not in to_email:
        return {"success": False, "channel": "email", "error": "Invalid email address"}

    templates = _email_templates()
    template = templates.get(template_key)
    if not template:
        return {"success": False, "channel": "email", "error": f"Unknown template: {template_key}"}

    context["status_line"] = f'<p>Track progress: <a href="{_status_url()}/status">{_status_url()}/status</a></p>' if _status_url() else ""
    subject = template["subject"].format(**{k: str(v) for k, v in context.items()})
    html_body = template["html"].format(**{k: str(v) for k, v in context.items()})

    try:
        import sendgrid
        from sendgrid.helpers.mail import Mail, Email, To, Content, Cc

        sg = sendgrid.SendGridAPIClient(api_key=os.environ["SENDGRID_API_KEY"])
        from_email = Email(os.environ["SENDGRID_FROM_EMAIL"], "Cause We Care")
        to_addr = To(to_email)
        content = Content("text/html", html_body)
        mail = Mail(from_email, to_addr, subject, content)

        if cc and "@" in cc:
            mail.add_cc(Cc(cc))

        response = sg.client.mail.send.post(request_body=mail.get())
        status_code = response.status_code

        logger.info(f"Email sent: {template_key} → {to_email} (status: {status_code})")
        return {
            "success": status_code in (200, 201, 202),
            "channel": "email",
            "template": template_key,
            "to": to_email,
            "cc": cc,
            "status_code": status_code,
            "sent_at": datetime.now(EASTERN).isoformat(),
        }
    except Exception as e:
        logger.error(f"Email failed: {template_key} → {to_email}: {e}")
        return {"success": False, "channel": "email", "error": str(e), "template": template_key}


# ─────────────────────────────────────────────────────────────────────────────
# Notification Log — write to Airtable so dashboard can display history
# ─────────────────────────────────────────────────────────────────────────────

TABLE_NOTIFICATIONS = "Notification_Log"

def log_notification(client: Any, result: Dict[str, Any], referral_id: Optional[str] = None, family_id: Optional[str] = None) -> None:
    """Log a send attempt (success or failure) to Airtable for dashboard visibility."""
    try:
        fields = {
            "channel": result.get("channel", "unknown"),
            "template": result.get("template", ""),
            "to": result.get("to", ""),
            "status": "Sent" if result.get("success") else ("Skipped" if result.get("skipped") else "Failed"),
            "error": result.get("error", ""),
            "sent_at": result.get("sent_at", datetime.now(EASTERN).isoformat()),
            "raw_response": json.dumps({k: v for k, v in result.items() if k not in ("success",)})[:1000],
        }
        if referral_id:
            fields["referral_id"] = [referral_id]
        if family_id:
            fields["family_id"] = [family_id]
        fields = {k: v for k, v in fields.items() if v not in (None, "", [])}
        client.create(TABLE_NOTIFICATIONS, fields)
    except Exception as e:
        logger.warning(f"Failed to log notification: {e}")


# ─────────────────────────────────────────────────────────────────────────────
# High-level triggers — called from shield_lead_screening.py
# ─────────────────────────────────────────────────────────────────────────────

SLA_HOURS = {"Emergency": 24, "Urgent": 48, "Standard": 120}


def notify_referral_received(
    client: Any,
    case_number: str,
    family_name: str,
    family_phone: str,
    family_email: str,
    caseworker_name: str,
    caseworker_email: str,
    county: str,
    urgency: str,
    referral_id: Optional[str] = None,
    family_id: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Fire all notifications when a new referral is created."""
    results = []
    ctx = {
        "case_number": case_number,
        "family_name": family_name,
        "county": county,
        "urgency": urgency,
        "caseworker_name": caseworker_name or "Case Worker",
        "sla_hours": SLA_HOURS.get(urgency, 120),
    }

    if family_phone:
        r = send_sms(family_phone, "referral_received", {**ctx})
        log_notification(client, r, referral_id, family_id)
        results.append(r)

    if family_email:
        r = send_email(family_email, "referral_received_family", {**ctx})
        log_notification(client, r, referral_id, family_id)
        results.append(r)

    if caseworker_email:
        r = send_email(caseworker_email, "referral_received_caseworker", {**ctx})
        log_notification(client, r, referral_id, family_id)
        results.append(r)

    return results


def notify_navigator_assigned(
    client: Any,
    case_number: str,
    family_name: str,
    family_phone: str,
    family_email: str,
    navigator_name: str,
    navigator_phone: str,
    navigator_email: str,
    referral_id: Optional[str] = None,
    family_id: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Fire notifications when a navigator is assigned to a case."""
    results = []
    ctx = {
        "case_number": case_number,
        "family_name": family_name,
        "navigator_name": navigator_name,
        "navigator_phone": navigator_phone,
        "navigator_email": navigator_email or "",
    }

    if family_phone:
        r = send_sms(family_phone, "navigator_assigned", {**ctx})
        log_notification(client, r, referral_id, family_id)
        results.append(r)

    if family_email:
        r = send_email(family_email, "navigator_assigned_family", {**ctx})
        log_notification(client, r, referral_id, family_id)
        results.append(r)

    return results


def notify_appointment_scheduled(
    client: Any,
    family_name: str,
    family_phone: str,
    service_name: str,
    appointment_date: str,
    vendor: str,
    navigator_name: str,
    navigator_phone: str,
    referral_id: Optional[str] = None,
    family_id: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Text the family when an appointment is scheduled."""
    results = []
    try:
        dt = datetime.fromisoformat(appointment_date.replace("Z", "+00:00"))
        friendly_date = dt.strftime("%A, %B %d at %I:%M %p")
    except Exception:
        friendly_date = appointment_date

    ctx = {
        "family_name": family_name,
        "service_name": service_name,
        "appointment_date": friendly_date,
        "vendor": f"at {vendor}" if vendor else "",
        "navigator_name": navigator_name or "your navigator",
        "navigator_phone": navigator_phone or "",
    }

    if family_phone:
        r = send_sms(family_phone, "appointment_scheduled", {**ctx})
        log_notification(client, r, referral_id, family_id)
        results.append(r)

    return results


def notify_service_completed(
    client: Any,
    family_name: str,
    family_phone: str,
    service_name: str,
    navigator_name: str,
    referral_id: Optional[str] = None,
    family_id: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Text the family when a service is completed."""
    results = []
    ctx = {
        "family_name": family_name,
        "service_name": service_name,
        "navigator_name": navigator_name or "your navigator",
    }

    if family_phone:
        r = send_sms(family_phone, "service_completed", {**ctx})
        log_notification(client, r, referral_id, family_id)
        results.append(r)

    return results


def notify_case_closed(
    client: Any,
    case_number: str,
    family_name: str,
    family_phone: str,
    family_email: str,
    caseworker_name: str,
    caseworker_email: str,
    services_list: str,
    duration_days: int,
    referral_id: Optional[str] = None,
    family_id: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Fire all notifications when a case is closed."""
    results = []
    ctx = {
        "case_number": case_number,
        "family_name": family_name,
        "caseworker_name": caseworker_name or "Case Worker",
        "services_list": services_list,
        "duration_days": duration_days,
    }

    if family_phone:
        r = send_sms(family_phone, "case_closed", {**ctx})
        log_notification(client, r, referral_id, family_id)
        results.append(r)

    if family_email:
        r = send_email(family_email, "case_closed_family", {**ctx})
        log_notification(client, r, referral_id, family_id)
        results.append(r)

    if caseworker_email:
        r = send_email(caseworker_email, "case_closed_caseworker", {**ctx})
        log_notification(client, r, referral_id, family_id)
        results.append(r)

    return results


# ─────────────────────────────────────────────────────────────────────────────
# Status check — for dashboard display
# ─────────────────────────────────────────────────────────────────────────────

def notification_channels_status() -> Dict[str, Any]:
    """Return which channels are active — shown on SHIELD dashboard."""
    return {
        "sms": {"enabled": _twilio_configured(), "provider": "Twilio"},
        "email": {"enabled": _sendgrid_configured(), "provider": "SendGrid"},
        "status_page": {"enabled": bool(_status_url()), "url": _status_url()},
    }


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _clean_phone(raw: str) -> str:
    """Normalize a phone number to E.164 (+1XXXXXXXXXX)."""
    digits = "".join(c for c in (raw or "") if c.isdigit())
    if len(digits) == 10:
        return f"+1{digits}"
    if len(digits) == 11 and digits.startswith("1"):
        return f"+{digits}"
    if digits.startswith("+") or len(digits) > 11:
        return raw.strip()
    return ""
