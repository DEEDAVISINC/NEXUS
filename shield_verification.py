"""
SHIELD Service Verification Engine
DEE DAVIS INC + CAUSE WE CARE

Automates two-way SMS confirmation loops that tie service-delivery verification
to payment eligibility.  Every activated service must pass through its
verification workflow before a billing record is created.

Flow:
  1. Service activated → verification_steps JSON seeded on the activation record
  2. Outbound SMS sent to contractor and/or family at each step
  3. Inbound SMS replies parsed → matching step marked complete
  4. All steps complete → status = "Verified Complete" → billing record created
  5. Overdue steps trigger escalation alerts to navigator / supervisor

Depends on:
  shield_notifications.py  — send_sms(), log_notification(), _clean_phone()
  shield_lead_screening.py — ShieldAirtableClient, table constants, helpers
"""

from __future__ import annotations

import json
import logging
import re
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from zoneinfo import ZoneInfo

from shield_notifications import send_sms, log_notification, _clean_phone
from shield_lead_screening import (
    ShieldAirtableClient,
    TABLE_ACTIVATIONS,
    TABLE_MILESTONES,
    TABLE_FAMILIES,
    TABLE_BILLING,
    TABLE_CONTRACTORS,
    TABLE_REFERRALS,
    _safe_all,
    _serialize,
)

# ─── NEXUS LEARNING ENGINE INTEGRATION ────────────────────────────────────────
try:
    from nexus_learning_engine import nxlearn
except ImportError:
    def nxlearn(*args, **kwargs):
        pass  # Graceful fallback if learning engine not available

logger = logging.getLogger("shield.verification")

EASTERN = ZoneInfo("America/New_York")
DDI_ADMIN_FEE_RATE = 0.225  # 22.5%

SHIELD_CPT_BILLING: Dict[str, Dict[str, Any]] = {
    "Lead Remediation Coordination":   {"cpt": "98960", "billing_type": "Admin Fee (22.5%)",  "payer": "MDHHS",            "rate_per_unit": None},
    "Housing Navigation":              {"cpt": "98960", "billing_type": "Admin Fee (22.5%)",  "payer": "MDHHS",            "rate_per_unit": None},
    "NEMT — Non-Emergency Medical Transportation": {"cpt": "T2002", "billing_type": "Medicaid NEMT", "payer": "Michigan Medicaid", "rate_per_unit": None},
    "Blood Lead Level (BLL) Testing":  {"cpt": "83655", "billing_type": "Medicaid CHW",       "payer": "Michigan Medicaid", "rate_per_unit": None},
    "CLPPP Case Management":           {"cpt": "98960", "billing_type": "Medicaid CHW",       "payer": "MDHHS",            "rate_per_unit": 25.0},
    "Community Health Worker Home Visit": {"cpt": "98960", "billing_type": "Medicaid CHW",    "payer": "Michigan Medicaid", "rate_per_unit": 25.0},
    "Nurse Home Visit":                {"cpt": "99345", "billing_type": "Admin Fee (22.5%)",  "payer": "Michigan Medicaid", "rate_per_unit": None},
    "Filter Safety Net / Drinking Water": {"cpt": "98960", "billing_type": "Admin Fee (22.5%)", "payer": "MDHHS",          "rate_per_unit": None},
    "MIBridges Benefits Navigation":   {"cpt": "98960", "billing_type": "Medicaid CHW",       "payer": "Michigan Medicaid", "rate_per_unit": 25.0},
}
_DEFAULT_BILLING_META = {"cpt": "98960", "billing_type": "Medicaid CHW", "payer": "Michigan Medicaid", "rate_per_unit": 25.0}


def _billing_meta_for(service_line: str) -> Dict[str, Any]:
    """Return CPT, billing type, payer, and rate for a service line."""
    return SHIELD_CPT_BILLING.get(service_line, _DEFAULT_BILLING_META)


def _now_eastern_iso() -> str:
    return datetime.now(EASTERN).isoformat()


def _envelope(success: bool, **payload) -> Dict[str, Any]:
    return {"success": success, **payload}


# ─────────────────────────────────────────────────────────────────────────────
# Verification Workflow Definitions — per service line
# ─────────────────────────────────────────────────────────────────────────────

VERIFICATION_WORKFLOWS: Dict[str, Dict[str, Any]] = {
    "Lead Remediation Coordination": {
        "steps": [
            {"key": "contractor_confirmed", "label": "Contractor confirmed on-site", "verify_by": "contractor_sms", "sla_hours": 2},
            {"key": "work_completed", "label": "Contractor reported work complete", "verify_by": "contractor_sms", "sla_hours": None},
            {"key": "evidence_uploaded", "label": "Clearance certificate uploaded", "verify_by": "navigator", "sla_hours": 48},
            {"key": "family_confirmed", "label": "Family confirmed service received", "verify_by": "family_sms", "sla_hours": 24},
        ],
        "auto_followup_days": [30, 60, 90],
    },
    "Housing Navigation": {
        "steps": [
            {"key": "placement_confirmed", "label": "Housing placement confirmed", "verify_by": "navigator", "sla_hours": 4},
            {"key": "family_checkin", "label": "Family checked in", "verify_by": "family_sms", "sla_hours": 4},
            {"key": "family_checkout", "label": "Family checked out (clearance received)", "verify_by": "family_sms", "sla_hours": None},
        ],
        "auto_followup_days": [],
    },
    "NEMT — Non-Emergency Medical Transportation": {
        "steps": [
            {"key": "ride_dispatched", "label": "Ride dispatched", "verify_by": "system", "sla_hours": None},
            {"key": "ride_completed", "label": "Ride completed", "verify_by": "system", "sla_hours": None},
            {"key": "family_confirmed", "label": "Family confirmed arrival", "verify_by": "family_sms", "sla_hours": 2},
        ],
        "auto_followup_days": [],
    },
    "Blood Lead Level (BLL) Testing": {
        "steps": [
            {"key": "test_scheduled", "label": "Test appointment scheduled", "verify_by": "navigator", "sla_hours": None},
            {"key": "test_completed", "label": "Test completed", "verify_by": "navigator", "sla_hours": None},
            {"key": "results_received", "label": "Results received and recorded", "verify_by": "navigator", "sla_hours": 72},
        ],
        "auto_followup_days": [90, 180],
    },
    "CLPPP Case Management": {
        "steps": [
            {"key": "referral_sent", "label": "CLPPP referral submitted", "verify_by": "navigator", "sla_hours": 24},
            {"key": "enrollment_confirmed", "label": "CLPPP enrollment confirmed", "verify_by": "navigator", "sla_hours": None},
        ],
        "auto_followup_days": [30, 90],
    },
    "Community Health Worker Home Visit": {
        "steps": [
            {"key": "visit_scheduled", "label": "Home visit scheduled", "verify_by": "navigator", "sla_hours": None},
            {"key": "navigator_arrived", "label": "Navigator arrived on-site", "verify_by": "navigator", "sla_hours": None},
            {"key": "visit_completed", "label": "Visit completed and documented", "verify_by": "navigator", "sla_hours": 4},
            {"key": "family_confirmed", "label": "Family confirmed visit", "verify_by": "family_sms", "sla_hours": 24},
        ],
        "auto_followup_days": [14, 30],
    },
    "Nurse Home Visit": {
        "steps": [
            {"key": "visit_scheduled", "label": "Nurse visit scheduled with agency", "verify_by": "navigator", "sla_hours": None},
            {"key": "nurse_confirmed", "label": "Nurse confirmed on-site", "verify_by": "contractor_sms", "sla_hours": 2},
            {"key": "visit_completed", "label": "Visit completed", "verify_by": "contractor_sms", "sla_hours": None},
            {"key": "report_received", "label": "Clinical report received", "verify_by": "navigator", "sla_hours": 48},
            {"key": "family_confirmed", "label": "Family confirmed visit", "verify_by": "family_sms", "sla_hours": 24},
        ],
        "auto_followup_days": [14, 30],
    },
    "Filter Safety Net / Drinking Water": {
        "steps": [
            {"key": "enrollment_submitted", "label": "Get Ahead of Lead enrollment submitted", "verify_by": "navigator", "sla_hours": None},
            {"key": "filter_delivered", "label": "Filter delivered/installed", "verify_by": "navigator", "sla_hours": None},
            {"key": "family_confirmed", "label": "Family confirmed filter received", "verify_by": "family_sms", "sla_hours": 24},
        ],
        "auto_followup_days": [90],
    },
    "MIBridges Benefits Navigation": {
        "steps": [
            {"key": "application_started", "label": "MIBridges application started", "verify_by": "navigator", "sla_hours": None},
            {"key": "application_submitted", "label": "Application submitted", "verify_by": "navigator", "sla_hours": None},
            {"key": "enrollment_confirmed", "label": "Benefits enrollment confirmed", "verify_by": "navigator", "sla_hours": None},
        ],
        "auto_followup_days": [30],
    },
}

_DEFAULT_WORKFLOW: Dict[str, Any] = {
    "steps": [
        {"key": "navigator_confirmed", "label": "Navigator confirmed completion", "verify_by": "navigator", "sla_hours": 48},
        {"key": "family_confirmed", "label": "Family confirmed service received", "verify_by": "family_sms", "sla_hours": 24},
    ],
    "auto_followup_days": [],
}


# ─────────────────────────────────────────────────────────────────────────────
# Verification SMS Templates
# ─────────────────────────────────────────────────────────────────────────────

VERIFICATION_SMS_TEMPLATES: Dict[str, str] = {
    "contractor_dispatch": (
        "SHIELD Service Request: {service_name} at {address}. "
        "Scheduled: {scheduled_date}. Reply CONFIRM when you arrive on-site. "
        "Case #{case_number}."
    ),
    "contractor_completion": (
        "Please reply DONE when {service_name} is complete at {address}. "
        "You may also text a photo of completed work. Case #{case_number}."
    ),
    "family_confirm_service": (
        "Hi {family_name} family \u2014 did you receive your {service_name} service? "
        "Reply YES to confirm, or NO if there was an issue. "
        "Your navigator {navigator_name} is here to help. \U0001f49b"
    ),
    "family_confirm_checkin": (
        "Hi {family_name} family \u2014 have you checked into your temporary housing? "
        "Reply YES once you're settled. If you need help, text {navigator_phone}. \U0001f49b"
    ),
    "family_confirm_ride": (
        "Hi {family_name} family \u2014 did you arrive safely at your appointment? "
        "Reply YES to confirm. \U0001f49b"
    ),
    "overdue_alert_navigator": (
        "\u26a0\ufe0f SHIELD Alert: {service_name} for {family_name} family (#{case_number}) "
        "has an overdue verification step: {step_label}. "
        "Expected within {sla_hours}h \u2014 now {hours_overdue}h overdue. Please investigate."
    ),
    "overdue_alert_supervisor": (
        "\U0001f6a8 SHIELD Escalation: {service_name} for {family_name} family (#{case_number}) \u2014 "
        "{step_label} is {hours_overdue}h overdue (SLA: {sla_hours}h). "
        "Navigator has been notified. Supervisor review required."
    ),
}

# Inbound SMS keywords mapped to intent
_POSITIVE_KEYWORDS = {"confirm", "confirmed", "done", "yes", "arrived", "checked-in", "checkedin", "complete", "completed", "y"}
_NEGATIVE_KEYWORDS = {"no", "help", "issue", "problem", "n"}


# ─────────────────────────────────────────────────────────────────────────────
# Workflow Lookup
# ─────────────────────────────────────────────────────────────────────────────

def get_verification_workflow(service_line: str) -> Dict[str, Any]:
    """Return the verification workflow config for a service line.

    Matches by exact key first, then by case-insensitive substring so short
    names like "Housing" still resolve to "Housing Navigation".
    """
    if service_line in VERIFICATION_WORKFLOWS:
        return VERIFICATION_WORKFLOWS[service_line]

    lower = service_line.lower()
    for key, wf in VERIFICATION_WORKFLOWS.items():
        if lower in key.lower() or key.lower() in lower:
            return wf

    return _DEFAULT_WORKFLOW


# ─────────────────────────────────────────────────────────────────────────────
# Seed / Read verification steps on an activation
# ─────────────────────────────────────────────────────────────────────────────

def _read_steps(activation: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Parse the verification_steps JSON string from an activation record."""
    fields = activation.get("fields") or activation
    raw = fields.get("verification_steps", "")
    if not raw:
        return []
    try:
        return json.loads(raw) if isinstance(raw, str) else raw
    except (json.JSONDecodeError, TypeError):
        return []


def _write_steps(client: ShieldAirtableClient, activation_id: str, steps: List[Dict[str, Any]]) -> None:
    """Persist the verification_steps JSON string back to Airtable."""
    client.update(TABLE_ACTIVATIONS, activation_id, {
        "verification_steps": json.dumps(steps),
    })


def seed_verification_steps(client: ShieldAirtableClient, activation_id: str, service_line: str) -> List[Dict[str, Any]]:
    """Initialise verification steps on a freshly-created activation record.

    Called once when a service activation is created.  Does NOT overwrite if
    steps already exist (idempotent).
    """
    try:
        record = client.get(TABLE_ACTIVATIONS, activation_id)
        existing = _read_steps(record)
        if existing:
            return existing

        wf = get_verification_workflow(service_line)
        steps = []
        for defn in wf["steps"]:
            steps.append({
                "key": defn["key"],
                "label": defn["label"],
                "verify_by": defn["verify_by"],
                "sla_hours": defn["sla_hours"],
                "completed_at": None,
                "verified_by": None,
                "evidence": None,
                "seeded_at": _now_eastern_iso(),
            })
        _write_steps(client, activation_id, steps)
        logger.info(f"Seeded {len(steps)} verification steps for activation {activation_id}")
        
        # ─── LEARNING ENGINE: Log verification started ────────────────────────
        nxlearn('shield_verification', activation_id, 'verification_started', {
            'service_type': service_line,
            'steps_required': len(steps),
        })
        
        return steps
    except Exception as exc:
        logger.error(f"seed_verification_steps failed for {activation_id}: {exc}")
        return []


# ─────────────────────────────────────────────────────────────────────────────
# Read Verification Status
# ─────────────────────────────────────────────────────────────────────────────

def get_activation_verification_status(client: ShieldAirtableClient, activation_id: str) -> Dict[str, Any]:
    """Return the full verification state for a service activation."""
    try:
        record = client.get(TABLE_ACTIVATIONS, activation_id)
        fields = record.get("fields") or {}
        service_line = fields.get("service_line", "")
        steps = _read_steps(record)

        if not steps:
            wf = get_verification_workflow(service_line)
            steps = [{
                "key": d["key"], "label": d["label"], "verify_by": d["verify_by"],
                "sla_hours": d["sla_hours"], "completed_at": None, "verified_by": None, "evidence": None,
            } for d in wf["steps"]]

        done = [s for s in steps if s.get("completed_at")]
        total = len(steps)
        all_verified = len(done) == total and total > 0

        now = datetime.now(EASTERN)
        overdue: List[Dict[str, Any]] = []
        next_step: Optional[Dict[str, Any]] = None

        for s in steps:
            if s.get("completed_at"):
                continue
            if next_step is None:
                next_step = s
            sla = s.get("sla_hours")
            if sla is not None:
                seeded = s.get("seeded_at") or fields.get("activated_at") or fields.get("createdTime", "")
                if seeded:
                    try:
                        seed_dt = datetime.fromisoformat(seeded)
                        deadline = seed_dt + timedelta(hours=sla)
                        if now > deadline:
                            overdue.append({**s, "deadline": deadline.isoformat(), "hours_overdue": round((now - deadline).total_seconds() / 3600, 1)})
                    except (ValueError, TypeError):
                        pass

        return _envelope(
            True,
            activation_id=activation_id,
            service_line=service_line,
            steps=steps,
            progress=f"{len(done)}/{total}",
            percent=round(len(done) / total * 100) if total else 0,
            all_verified=all_verified,
            payment_eligible=all_verified,
            next_step=next_step,
            overdue_steps=overdue,
        )
    except Exception as exc:
        logger.error(f"get_activation_verification_status failed: {exc}")
        return _envelope(False, error=str(exc))


# ─────────────────────────────────────────────────────────────────────────────
# Complete a Verification Step
# ─────────────────────────────────────────────────────────────────────────────

def complete_verification_step(
    client: ShieldAirtableClient,
    activation_id: str,
    step_key: str,
    verified_by: str,
    evidence: str = "",
) -> Dict[str, Any]:
    """Mark a single verification step as complete.

    If all steps become complete the activation status is set to
    "Verified Complete" and a billing record is created.
    """
    try:
        record = client.get(TABLE_ACTIVATIONS, activation_id)
        fields = record.get("fields") or {}
        steps = _read_steps(record)

        if not steps:
            return _envelope(False, error="No verification steps found on this activation")

        found = False
        for s in steps:
            if s["key"] == step_key:
                if s.get("completed_at"):
                    return _envelope(True, message="Step already completed", activation_id=activation_id)
                s["completed_at"] = _now_eastern_iso()
                s["verified_by"] = verified_by
                s["evidence"] = evidence or None
                found = True
                break

        if not found:
            return _envelope(False, error=f"Step key '{step_key}' not found")

        _write_steps(client, activation_id, steps)

        # Log milestone
        _log_milestone(client, activation_id, fields, f"Verification step complete: {step_key}", verified_by)
        
        # ─── LEARNING ENGINE: Log step completed ──────────────────────────────
        nxlearn('shield_verification', activation_id, 'step_completed', {
            'service_type': fields.get('service_line', ''),
            'step_key': step_key,
            'verified_by': verified_by,
        })

        all_done = all(s.get("completed_at") for s in steps)
        billing_result = None

        if all_done:
            client.update(TABLE_ACTIVATIONS, activation_id, {"status": "Verified Complete"})
            _log_milestone(client, activation_id, fields, "Service Verified — Payment Eligible", "system")
            
            # ─── LEARNING ENGINE: Log verification passed ─────────────────────
            nxlearn('shield_verification', activation_id, 'verification_passed', {
                'service_type': fields.get('service_line', ''),
                'steps_completed': len(steps),
            })

            referral_ids = fields.get("referral_id") or []
            referral_id = referral_ids[0] if isinstance(referral_ids, list) and referral_ids else (referral_ids if isinstance(referral_ids, str) else "")
            family_ids = fields.get("family_id") or []
            family_id = family_ids[0] if isinstance(family_ids, list) and family_ids else (family_ids if isinstance(family_ids, str) else "")

            billing_result = create_billing_on_verified(client, activation_id, referral_id, family_id)

        status = get_activation_verification_status(client, activation_id)
        status["billing"] = billing_result
        return status

    except Exception as exc:
        logger.error(f"complete_verification_step failed: {exc}")
        return _envelope(False, error=str(exc))


# ─────────────────────────────────────────────────────────────────────────────
# Inbound SMS Handler
# ─────────────────────────────────────────────────────────────────────────────

def handle_inbound_verification(client: ShieldAirtableClient, from_number: str, body: str) -> Dict[str, Any]:
    """Process an inbound SMS reply for service verification.

    Called by the Twilio webhook handler.  Matches the sender phone to a
    contractor or family, finds their most-recent active activation, parses
    the reply for keywords, and completes the appropriate verification step.
    """
    try:
        cleaned = _clean_phone(from_number)
        if not cleaned:
            return _envelope(False, error="Could not parse inbound phone number")

        words = set(re.split(r"[\s,;.!?]+", body.strip().lower()))
        is_positive = bool(words & _POSITIVE_KEYWORDS)
        is_negative = bool(words & _NEGATIVE_KEYWORDS)

        # Identify sender: contractor or family?
        sender_type, sender_record = _identify_sender(client, cleaned)
        if not sender_type:
            logger.warning(f"Inbound SMS from unrecognised number: {cleaned}")
            return _envelope(False, error="Phone number not matched to contractor or family")

        # Find the most recent active activation for this sender
        activation, act_fields = _find_active_activation(client, sender_type, sender_record)
        if not activation:
            return _envelope(False, error="No active service activation found for this sender")

        activation_id = activation["id"]

        if is_negative:
            _escalate_negative_reply(client, activation_id, act_fields, sender_type, body)
            return _envelope(True, action="escalated", activation_id=activation_id, message="Negative reply — navigator notified")

        if not is_positive:
            return _envelope(False, error="Reply not understood", body=body)

        # Determine which step to complete based on sender type
        steps = _read_steps(activation)
        step_key = _pick_completable_step(steps, sender_type)
        if not step_key:
            return _envelope(True, message="No pending verification step for this sender type", activation_id=activation_id)

        verified_by = f"{sender_type}_sms:{cleaned}"
        result = complete_verification_step(client, activation_id, step_key, verified_by, evidence=body)

        # Log to Notification_Log
        log_notification(client, {
            "success": True,
            "channel": "sms_inbound",
            "template": "verification_reply",
            "to": cleaned,
            "sent_at": _now_eastern_iso(),
        }, family_id=_extract_link_id(act_fields, "family_id"))

        return result

    except Exception as exc:
        logger.error(f"handle_inbound_verification failed: {exc}")
        return _envelope(False, error=str(exc))


# ─────────────────────────────────────────────────────────────────────────────
# Send Outbound Verification Request
# ─────────────────────────────────────────────────────────────────────────────

def send_verification_request(client: ShieldAirtableClient, activation_id: str, step_key: str) -> Dict[str, Any]:
    """Send an outbound SMS requesting verification for a specific step."""
    try:
        record = client.get(TABLE_ACTIVATIONS, activation_id)
        fields = record.get("fields") or {}
        steps = _read_steps(record)

        target_step = None
        for s in steps:
            if s["key"] == step_key:
                target_step = s
                break
        if not target_step:
            return _envelope(False, error=f"Step key '{step_key}' not found")
        if target_step.get("completed_at"):
            return _envelope(True, message="Step already complete — no SMS sent")

        verify_by = target_step.get("verify_by", "")
        service_name = fields.get("service_line", "Service")
        case_number = fields.get("case_number", "")

        family_id = _extract_link_id(fields, "family_id")
        family_name = _resolve_family_name(client, family_id)
        family_phone = _resolve_family_phone(client, family_id)
        navigator_name = fields.get("navigator_name", "your navigator")
        navigator_phone = fields.get("navigator_phone", "")
        address = fields.get("address", "the scheduled location")
        scheduled_date = fields.get("scheduled_date", "")

        context = {
            "service_name": service_name,
            "case_number": case_number,
            "family_name": family_name,
            "navigator_name": navigator_name,
            "navigator_phone": navigator_phone,
            "address": address,
            "scheduled_date": scheduled_date,
        }

        if verify_by == "contractor_sms":
            contractor_phone = _resolve_contractor_phone(client, fields)
            if not contractor_phone:
                return _envelope(False, error="No contractor phone on record")
            template_key = _pick_contractor_template(step_key)
            sms_body = _render_verification_sms(template_key, context)
            result = _send_raw_sms(contractor_phone, sms_body)
            log_notification(client, result, family_id=family_id)
            return _envelope(result.get("success", False), sms=result, step_key=step_key)

        elif verify_by == "family_sms":
            if not family_phone:
                return _envelope(False, error="No family phone on record")
            template_key = _pick_family_template(step_key, service_name)
            sms_body = _render_verification_sms(template_key, context)
            result = _send_raw_sms(family_phone, sms_body)
            log_notification(client, result, family_id=family_id)
            return _envelope(result.get("success", False), sms=result, step_key=step_key)

        elif verify_by in ("navigator", "system"):
            return _envelope(True, message=f"Step '{step_key}' is verified by {verify_by} — no SMS required")

        return _envelope(False, error=f"Unknown verify_by value: {verify_by}")

    except Exception as exc:
        logger.error(f"send_verification_request failed: {exc}")
        return _envelope(False, error=str(exc))


# ─────────────────────────────────────────────────────────────────────────────
# Overdue Scanner
# ─────────────────────────────────────────────────────────────────────────────

def check_overdue_verifications(client: ShieldAirtableClient) -> List[Dict[str, Any]]:
    """Scan all active service activations for overdue verification steps.

    Intended to be called periodically (e.g. every hour by a scheduler).
    Returns a list of overdue items with escalation details.
    """
    overdue_items: List[Dict[str, Any]] = []
    try:
        activations = _safe_all(client, TABLE_ACTIVATIONS)
        now = datetime.now(EASTERN)

        for act in activations:
            fields = act.get("fields") or {}
            status = fields.get("status", "")
            if status in ("Verified Complete", "Closed", "Cancelled"):
                continue

            steps = _read_steps(act)
            if not steps:
                continue

            activation_id = act.get("id", "")
            service_line = fields.get("service_line", "")
            case_number = fields.get("case_number", "")
            family_id = _extract_link_id(fields, "family_id")
            family_name = _resolve_family_name(client, family_id)

            for s in steps:
                if s.get("completed_at"):
                    continue
                sla = s.get("sla_hours")
                if sla is None:
                    continue

                seeded = s.get("seeded_at") or fields.get("activated_at") or ""
                if not seeded:
                    continue

                try:
                    seed_dt = datetime.fromisoformat(seeded)
                    deadline = seed_dt + timedelta(hours=sla)
                except (ValueError, TypeError):
                    continue

                if now <= deadline:
                    continue

                hours_overdue = round((now - deadline).total_seconds() / 3600, 1)

                overdue_items.append({
                    "activation_id": activation_id,
                    "service_line": service_line,
                    "case_number": case_number,
                    "family_name": family_name,
                    "step_key": s["key"],
                    "step_label": s["label"],
                    "sla_hours": sla,
                    "hours_overdue": hours_overdue,
                    "escalation": "supervisor" if hours_overdue > sla * 2 else "navigator",
                })

    except Exception as exc:
        logger.error(f"check_overdue_verifications failed: {exc}")

    return overdue_items


def send_overdue_alerts(client: ShieldAirtableClient) -> List[Dict[str, Any]]:
    """Check for overdue steps and send escalation SMS to navigators/supervisors."""
    results: List[Dict[str, Any]] = []
    overdue = check_overdue_verifications(client)

    for item in overdue:
        context = {
            "service_name": item["service_line"],
            "family_name": item["family_name"],
            "case_number": item["case_number"],
            "step_label": item["step_label"],
            "sla_hours": item["sla_hours"],
            "hours_overdue": item["hours_overdue"],
        }

        try:
            activation = client.get(TABLE_ACTIVATIONS, item["activation_id"])
            act_fields = activation.get("fields") or {}
        except Exception:
            continue

        navigator_phone = act_fields.get("navigator_phone", "")
        if navigator_phone:
            body = _render_verification_sms("overdue_alert_navigator", context)
            r = _send_raw_sms(navigator_phone, body)
            log_notification(client, r, family_id=_extract_link_id(act_fields, "family_id"))
            results.append(r)

        if item["escalation"] == "supervisor":
            supervisor_phone = act_fields.get("supervisor_phone", "")
            if supervisor_phone:
                body = _render_verification_sms("overdue_alert_supervisor", context)
                r = _send_raw_sms(supervisor_phone, body)
                log_notification(client, r, family_id=_extract_link_id(act_fields, "family_id"))
                results.append(r)

    return results


# ─────────────────────────────────────────────────────────────────────────────
# Auto-Billing on Verified Complete
# ─────────────────────────────────────────────────────────────────────────────

def create_billing_on_verified(
    client: ShieldAirtableClient,
    activation_id: str,
    referral_id: str,
    family_id: str,
) -> Dict[str, Any]:
    """Create a billing record when a service reaches Verified Complete."""
    try:
        record = client.get(TABLE_ACTIVATIONS, activation_id)
        fields = record.get("fields") or {}

        service_line = fields.get("service_line", "")
        service_amount = float(fields.get("service_amount", 0) or 0)

        admin_fee = round(service_amount * DDI_ADMIN_FEE_RATE, 2)
        total_billed = round(service_amount + admin_fee, 2)

        billing_fields: Dict[str, Any] = {
            "service_line": service_line,
            "service_amount": service_amount,
            "admin_fee_rate": DDI_ADMIN_FEE_RATE,
            "admin_fee_amount": admin_fee,
            "total_billed": total_billed,
            "status": "Ready to Submit",
            "date_of_service": fields.get("completed_at") or fields.get("activated_at") or _now_eastern_iso(),
            "created_at": _now_eastern_iso(),
        }
        if activation_id:
            billing_fields["activation_id"] = [activation_id]
        if referral_id:
            billing_fields["referral_id"] = [referral_id]
        if family_id:
            billing_fields["family_id"] = [family_id]

        billing_fields = {k: v for k, v in billing_fields.items() if v not in (None, "", [], 0)}
        if service_amount > 0:
            billing_fields["service_amount"] = service_amount

        created = client.create(TABLE_BILLING, billing_fields)

        logger.info(f"Billing record created for activation {activation_id}: ${total_billed}")

        try:
            from vertex_automation import vertex_auto_trigger
            family_name = _resolve_family_name(client, family_id)
            meta = _billing_meta_for(service_line)
            vertex_auto_trigger(
                "shield.service.verified",
                source_record_id=activation_id,
                data={
                    "service_line": service_line,
                    "family_name": family_name,
                    "case_number": fields.get("case_number", ""),
                    "county": fields.get("county", ""),
                    "service_amount": service_amount,
                    "admin_fee_rate": DDI_ADMIN_FEE_RATE,
                    "cpt_code": fields.get("cpt_code") or meta["cpt"],
                    "billing_type": fields.get("billing_type") or meta["billing_type"],
                    "payer": fields.get("payer") or meta["payer"],
                    "navigator_name": fields.get("navigator_name", ""),
                },
            )
        except Exception:
            logger.warning(f"VERTEX auto-trigger failed for activation {activation_id} — billing record still created")

        return _envelope(True, billing_id=created.get("id"), total_billed=total_billed, admin_fee=admin_fee)

    except Exception as exc:
        logger.error(f"create_billing_on_verified failed for {activation_id}: {exc}")
        return _envelope(False, error=str(exc))


# ─────────────────────────────────────────────────────────────────────────────
# Internal Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _log_milestone(
    client: ShieldAirtableClient,
    activation_id: str,
    act_fields: Dict[str, Any],
    description: str,
    actor: str,
) -> None:
    """Write a milestone entry to Case_Milestones."""
    try:
        referral_id = _extract_link_id(act_fields, "referral_id")
        milestone_fields: Dict[str, Any] = {
            "description": description,
            "actor": actor,
            "timestamp": _now_eastern_iso(),
        }
        if activation_id:
            milestone_fields["activation_id"] = [activation_id]
        if referral_id:
            milestone_fields["referral_id"] = [referral_id]
        milestone_fields = {k: v for k, v in milestone_fields.items() if v not in (None, "", [])}
        client.create(TABLE_MILESTONES, milestone_fields)
    except Exception as exc:
        logger.warning(f"Failed to log milestone: {exc}")


def _extract_link_id(fields: Dict[str, Any], key: str) -> str:
    """Pull a single record ID from an Airtable linked-record field."""
    val = fields.get(key)
    if isinstance(val, list) and val:
        return val[0]
    if isinstance(val, str):
        return val
    return ""


def _resolve_family_phone(client: ShieldAirtableClient, family_id: str) -> str:
    if not family_id:
        return ""
    try:
        fam = client.get(TABLE_FAMILIES, family_id)
        return ((fam.get("fields") or {}).get("primary_contact_phone") or
                (fam.get("fields") or {}).get("phone") or "")
    except Exception:
        return ""


def _resolve_family_name(client: ShieldAirtableClient, family_id: str) -> str:
    if not family_id:
        return ""
    try:
        fam = client.get(TABLE_FAMILIES, family_id)
        return (fam.get("fields") or {}).get("family_name", "")
    except Exception:
        return ""


def _resolve_contractor_phone(client: ShieldAirtableClient, act_fields: Dict[str, Any]) -> str:
    """Look up the contractor phone from the activation's linked contractor."""
    contractor_id = _extract_link_id(act_fields, "contractor_id")
    if not contractor_id:
        return act_fields.get("contractor_phone", "")
    try:
        rec = client.get(TABLE_CONTRACTORS, contractor_id)
        return ((rec.get("fields") or {}).get("phone") or
                (rec.get("fields") or {}).get("primary_phone") or "")
    except Exception:
        return ""


def _identify_sender(
    client: ShieldAirtableClient, phone: str
) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
    """Match an inbound phone number to a contractor or family record.

    Returns (sender_type, record) where sender_type is 'contractor' or 'family'.
    """
    phone_digits = re.sub(r"\D", "", phone)

    # Check contractors first (more specific match)
    try:
        for rec in _safe_all(client, TABLE_CONTRACTORS):
            f = rec.get("fields") or {}
            for field_name in ("phone", "primary_phone", "mobile"):
                raw = f.get(field_name, "")
                if raw and re.sub(r"\D", "", raw) == phone_digits:
                    return "contractor", rec
    except Exception:
        pass

    # Check families
    try:
        for rec in _safe_all(client, TABLE_FAMILIES):
            f = rec.get("fields") or {}
            for field_name in ("primary_contact_phone", "phone", "mobile"):
                raw = f.get(field_name, "")
                if raw and re.sub(r"\D", "", raw) == phone_digits:
                    return "family", rec
    except Exception:
        pass

    return None, None


def _find_active_activation(
    client: ShieldAirtableClient,
    sender_type: str,
    sender_record: Dict[str, Any],
) -> Tuple[Optional[Dict[str, Any]], Dict[str, Any]]:
    """Find the most recent non-closed activation for the sender.

    For contractors, matches on contractor_id linked field.
    For families, matches on family_id linked field.
    """
    sender_id = sender_record.get("id", "")
    link_field = "contractor_id" if sender_type == "contractor" else "family_id"

    try:
        activations = _safe_all(client, TABLE_ACTIVATIONS)
        candidates = []
        for act in activations:
            fields = act.get("fields") or {}
            if fields.get("status") in ("Verified Complete", "Closed", "Cancelled"):
                continue
            linked = fields.get(link_field) or []
            linked_ids = linked if isinstance(linked, list) else [linked]
            if sender_id in linked_ids:
                candidates.append(act)

        if not candidates:
            return None, {}

        # Pick most recent by created time
        candidates.sort(key=lambda a: a.get("createdTime", ""), reverse=True)
        best = candidates[0]
        return best, best.get("fields") or {}
    except Exception:
        return None, {}


def _pick_completable_step(steps: List[Dict[str, Any]], sender_type: str) -> Optional[str]:
    """Find the first incomplete step that matches the sender's verify_by type."""
    target = f"{sender_type}_sms"
    for s in steps:
        if s.get("completed_at"):
            continue
        if s.get("verify_by") == target:
            return s["key"]
    return None


def _pick_contractor_template(step_key: str) -> str:
    """Choose the right outbound template based on the step."""
    if "confirm" in step_key or "arrived" in step_key:
        return "contractor_dispatch"
    return "contractor_completion"


def _pick_family_template(step_key: str, service_name: str) -> str:
    """Choose the right outbound family template based on the step."""
    lower = step_key.lower()
    if "checkin" in lower or "check_in" in lower:
        return "family_confirm_checkin"
    if "ride" in lower or "arrival" in lower:
        return "family_confirm_ride"
    return "family_confirm_service"


def _render_verification_sms(template_key: str, context: Dict[str, Any]) -> str:
    """Render a verification SMS template with context values."""
    template = VERIFICATION_SMS_TEMPLATES.get(template_key, "")
    if not template:
        return f"SHIELD Verification: Please reply CONFIRM or YES. (ref: {context.get('case_number', 'N/A')})"
    safe_ctx = {k: str(v) if v is not None else "" for k, v in context.items()}
    try:
        return template.format(**safe_ctx)
    except KeyError as exc:
        logger.warning(f"SMS template render missing key {exc} in template '{template_key}'")
        return template.format_map(_SafeFormatDict(safe_ctx))


class _SafeFormatDict(dict):
    """Dict subclass that returns placeholder text for missing keys."""
    def __missing__(self, key: str) -> str:
        return f"[{key}]"


def _send_raw_sms(to_number: str, body: str) -> Dict[str, Any]:
    """Send a raw SMS body through Twilio (bypasses template lookup in send_sms)."""
    import os
    from shield_notifications import _twilio_configured, _clean_phone as clean

    if not _twilio_configured():
        return {"success": False, "channel": "sms", "error": "Twilio not configured", "skipped": True}

    to_clean = clean(to_number)
    if not to_clean:
        return {"success": False, "channel": "sms", "error": "Invalid phone number"}

    try:
        from twilio.rest import Client
        twilio = Client(
            os.environ["TWILIO_ACCOUNT_SID"],
            os.environ["TWILIO_AUTH_TOKEN"],
        )
        message = twilio.messages.create(
            body=body,
            from_=os.environ["TWILIO_FROM_NUMBER"],
            to=to_clean,
        )
        logger.info(f"Verification SMS sent → {to_clean} (SID: {message.sid})")
        return {
            "success": True,
            "channel": "sms",
            "template": "verification_raw",
            "to": to_clean,
            "twilio_sid": message.sid,
            "status": message.status,
            "sent_at": _now_eastern_iso(),
        }
    except Exception as exc:
        logger.error(f"Verification SMS failed → {to_clean}: {exc}")
        return {"success": False, "channel": "sms", "error": str(exc)}


def _escalate_negative_reply(
    client: ShieldAirtableClient,
    activation_id: str,
    act_fields: Dict[str, Any],
    sender_type: str,
    body: str,
) -> None:
    """Handle a NO/HELP reply by alerting the navigator."""
    _log_milestone(client, activation_id, act_fields, f"Negative SMS reply from {sender_type}: {body[:200]}", f"{sender_type}_sms")

    navigator_phone = act_fields.get("navigator_phone", "")
    if not navigator_phone:
        return

    family_id = _extract_link_id(act_fields, "family_id")
    family_name = _resolve_family_name(client, family_id)
    service_line = act_fields.get("service_line", "Service")
    case_number = act_fields.get("case_number", "")

    alert = (
        f"\u26a0\ufe0f SHIELD: {sender_type.title()} replied \"{body[:80]}\" "
        f"for {service_line} ({family_name} family, #{case_number}). "
        f"Please follow up."
    )
    r = _send_raw_sms(navigator_phone, alert)
    log_notification(client, r, family_id=family_id)
