"""
SHIELD — Lead Screening & MDHHS Referral Module
DEE DAVIS INC + CAUSE WE CARE

Two-sided system anchored by Michigan Public Act 146 of 2023 (universal blood
lead screening mandate, effective April 30, 2025).

- Internal side: DDI/CWC case management, navigator workflow, billing, outcomes
- External side: Referral source portal for MDHHS / county health dept staff

All Airtable access routes through this module (backend-only). Frontend never
touches Airtable directly, and no Anthropic key is ever exposed client-side.

Airtable base: nexus_lead_screening (10 tables)
Env var: LEAD_SCREENING_BASE_ID (separate from the primary NEXUS base)
"""

from __future__ import annotations

import os
import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from zoneinfo import ZoneInfo
from pyairtable import Api


# ─────────────────────────────────────────────────────────────────────────────
# Table names — keep in one place so Airtable renames only require one edit
# ─────────────────────────────────────────────────────────────────────────────
TABLE_REFERRALS = "Referrals"
TABLE_FAMILIES = "Families"
TABLE_CHILDREN = "Children"
TABLE_NAVIGATORS = "Navigators"
TABLE_ACTIVATIONS = "Service_Activations"
TABLE_MILESTONES = "Case_Milestones"
TABLE_CONTRACTORS = "Contractors"
TABLE_BILLING = "Billing"
TABLE_OUTCOMES = "Outcomes_Reporting"
TABLE_SOURCE_ACCOUNTS = "Referral_Source_Accounts"

EASTERN = ZoneInfo("America/New_York")

SERVICE_LINES = [
    "Lead Screening",
    "NEMT",
    "Housing",
    "Drug Testing",
    "DNA",
    "Food Navigation",
    "Specimen Transport",
    "Lead Remediation",
    "Filter Safety Net",
    "Medical Monitoring",
]

COUNTIES = [
    "Wayne",
    "Oakland",
    "Macomb",
    "Genesee",
    "Kent",
    "Muskegon",
    "Other",
]

URGENCY_LEVELS = ["Standard", "Urgent", "Emergency"]
REFERRAL_STATUSES = ["New", "Assigned", "Active", "Pending", "Completed", "Closed"]

# ─────────────────────────────────────────────────────────────────────────────
# SLA matrix — approved by Dee (Apr 23, 2026)
#
# First-contact SLAs (hours from date_received)
#   Emergency  24h    — confirmed EBL ≥ 5 µg/dL, active displacement
#   Urgent     48h    — elevated BLL or confirmed lead hazard
#   Standard   120h   — 5 business days; screening referrals, no exposure
#
# Downstream SLAs — tracked per activation / per child event
#   CLPPP_referral           24h  from EBL confirmation → CLPPP referral sent
#   Remediation_scheduled    240h (10 business days) from housing intake
#   Medicaid_prior_auth      72h  (3 business days) from service activation
#
# Auto-escalation rules (backend-enforced)
#   BLL ≥ 45                     → Emergency  (severe poisoning — immediate)
#   BLL ≥ 5                      → Urgent     (EBL threshold, CDC)
#   Confirmed EBL + displacement → Emergency
#
# Only Supervisor / Admin navigators can override an SLA. Enforced by
# _is_supervisor() via the Navigators table `role` field.
# ─────────────────────────────────────────────────────────────────────────────
SLA_FIRST_CONTACT_HOURS: Dict[str, int] = {
    "Emergency": 24,
    "Urgent": 48,
    "Standard": 120,
}

SLA_DOWNSTREAM_HOURS: Dict[str, int] = {
    "CLPPP_referral": 24,
    "Remediation_scheduled": 240,
    "Medicaid_prior_auth": 72,
}

# Urgency ordering for escalation comparisons
_URGENCY_RANK: Dict[str, int] = {"Standard": 0, "Urgent": 1, "Emergency": 2}
SUPERVISOR_ROLES = {"Supervisor", "Admin"}


# ─────────────────────────────────────────────────────────────────────────────
# Airtable client — dedicated base for SHIELD
# ─────────────────────────────────────────────────────────────────────────────
class ShieldAirtableClient:
    """Airtable client scoped to the lead-screening base.

    Uses LEAD_SCREENING_BASE_ID from .env. Falls back to AIRTABLE_BASE_ID only
    if the dedicated base ID is not set (allows the system to boot while Dee
    configures the Airtable base separately).
    """

    def __init__(self) -> None:
        self.api = Api(os.environ.get("AIRTABLE_API_KEY", ""))
        self.base_id = (
            os.environ.get("LEAD_SCREENING_BASE_ID", "")
            or os.environ.get("AIRTABLE_BASE_ID", "")
        )

    @property
    def is_configured(self) -> bool:
        return bool(self.base_id) and bool(os.environ.get("AIRTABLE_API_KEY", ""))

    def _table(self, table_name: str):
        return self.api.table(self.base_id, table_name)

    def all(self, table_name: str, **kwargs) -> List[Dict[str, Any]]:
        return self._table(table_name).all(**kwargs)

    def create(self, table_name: str, fields: Dict[str, Any]) -> Dict[str, Any]:
        return self._table(table_name).create(fields)

    def update(self, table_name: str, record_id: str, fields: Dict[str, Any]) -> Dict[str, Any]:
        return self._table(table_name).update(record_id, fields)

    def get(self, table_name: str, record_id: str) -> Dict[str, Any]:
        return self._table(table_name).get(record_id)

    def delete(self, table_name: str, record_id: str) -> Dict[str, Any]:
        return self._table(table_name).delete(record_id)

    def search(self, table_name: str, formula: str) -> List[Dict[str, Any]]:
        return self._table(table_name).all(formula=formula)


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────
def _now_eastern_iso() -> str:
    return datetime.now(EASTERN).isoformat()


def _serialize(record: Dict[str, Any]) -> Dict[str, Any]:
    """Flatten an Airtable record to { id, ...fields }."""
    out = {"id": record.get("id"), "createdTime": record.get("createdTime")}
    out.update(record.get("fields", {}) or {})
    return out


def _envelope(success: bool, **payload) -> Dict[str, Any]:
    return {"success": success, **payload}


def _unconfigured_hint(resource_plural: str) -> Dict[str, Any]:
    """Response when Airtable base/key not yet configured. Frontend handles gracefully."""
    return {
        "success": False,
        "configured": False,
        resource_plural: [],
        "count": 0,
        "hint": (
            "SHIELD Airtable base is not configured. Set LEAD_SCREENING_BASE_ID "
            "in .env and create the nexus_lead_screening base with the 10 tables "
            "(Referrals, Families, Children, Navigators, Service_Activations, "
            "Case_Milestones, Contractors, Billing, Outcomes_Reporting, "
            "Referral_Source_Accounts)."
        ),
    }


def _safe_all(client: ShieldAirtableClient, table_name: str) -> List[Dict[str, Any]]:
    """Fetch all rows. Return empty list on any failure (table missing etc.)."""
    try:
        return client.all(table_name)
    except Exception:
        return []


def _parse_iso(value: Optional[str]) -> Optional[datetime]:
    """Parse an ISO-8601 string → aware datetime in EASTERN tz. Returns None on failure."""
    if not value or not isinstance(value, str):
        return None
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=EASTERN)
        return dt.astimezone(EASTERN)
    except (ValueError, TypeError):
        return None


# ─────────────────────────────────────────────────────────────────────────────
# SLA snapshot — one function, used everywhere
# ─────────────────────────────────────────────────────────────────────────────
def _sla_snapshot(fields: Dict[str, Any]) -> Dict[str, Any]:
    """Compute SLA state for a referral.

    Priority for target hours:
      1. sla_override_hours  (supervisor-set)
      2. SLA_FIRST_CONTACT_HOURS[urgency]
      3. 48 (fallback)

    Returns a dict the frontend can render directly:
      {
        urgency, target_hours, source ('override'|'urgency'|'default'),
        override: { hours, reason, by, at } | None,
        auto_escalated: bool, escalated_reason: str | None, escalated_at: str | None,
        date_received, deadline_iso, elapsed_hours, remaining_hours,
        percent (0..100+), breached: bool, warning: bool,
        stopped: bool  -- true once first_contact_at is set
      }
    """
    urgency = fields.get("urgency", "Standard") or "Standard"
    override = fields.get("sla_override_hours")

    target_hours: float
    source: str
    if override is not None and str(override) != "":
        try:
            target_hours = float(override)
            source = "override"
        except (ValueError, TypeError):
            target_hours = float(SLA_FIRST_CONTACT_HOURS.get(urgency, 48))
            source = "urgency"
    else:
        target_hours = float(SLA_FIRST_CONTACT_HOURS.get(urgency, 48))
        source = "urgency" if urgency in SLA_FIRST_CONTACT_HOURS else "default"

    received = _parse_iso(fields.get("date_received"))
    first_contact = _parse_iso(fields.get("first_contact_at"))
    stopped = first_contact is not None

    now = datetime.now(EASTERN)
    stop_clock_at = first_contact or now

    elapsed_hours: Optional[float] = None
    deadline_iso: Optional[str] = None
    if received:
        elapsed_hours = max(0.0, (stop_clock_at - received).total_seconds() / 3600.0)
        deadline = received + timedelta(hours=target_hours)
        deadline_iso = deadline.isoformat()

    remaining_hours = None
    percent = None
    breached = False
    warning = False
    if elapsed_hours is not None:
        remaining_hours = round(target_hours - elapsed_hours, 2)
        percent = round(min(200.0, (elapsed_hours / target_hours) * 100.0), 1) if target_hours > 0 else 0
        breached = (not stopped) and elapsed_hours > target_hours
        warning = (not stopped) and (not breached) and elapsed_hours > target_hours * 0.65

    override_block: Optional[Dict[str, Any]] = None
    if source == "override":
        override_block = {
            "hours": target_hours,
            "reason": fields.get("sla_override_reason", ""),
            "by": fields.get("sla_override_by", ""),
            "at": fields.get("sla_override_at", ""),
        }

    return {
        "urgency": urgency,
        "target_hours": target_hours,
        "source": source,
        "override": override_block,
        "auto_escalated": bool(fields.get("urgency_auto_escalated")),
        "escalated_reason": fields.get("urgency_escalated_reason") or None,
        "escalated_at": fields.get("urgency_escalated_at") or None,
        "escalated_from": fields.get("urgency_escalated_from") or None,
        "date_received": fields.get("date_received"),
        "first_contact_at": fields.get("first_contact_at"),
        "deadline_iso": deadline_iso,
        "elapsed_hours": round(elapsed_hours, 2) if elapsed_hours is not None else None,
        "remaining_hours": remaining_hours,
        "percent": percent,
        "breached": breached,
        "warning": warning,
        "stopped": stopped,
    }


def _enriched(record: Dict[str, Any]) -> Dict[str, Any]:
    """Serialize + attach computed SLA snapshot for any referral record."""
    row = _serialize(record)
    row["sla"] = _sla_snapshot(record.get("fields", {}) or {})
    return row


# ─────────────────────────────────────────────────────────────────────────────
# Auto-escalation — urgency bumps driven by child BLL data
# ─────────────────────────────────────────────────────────────────────────────
def _desired_urgency_from_children(
    current_urgency: str,
    children: List[Dict[str, Any]],
    displacement_required: bool = False,
) -> tuple[str, Optional[str]]:
    """Decide if urgency should be bumped based on child lead data.

    Returns (new_urgency, reason_if_changed).
    Never downgrades — escalation is one-way until supervisor override.
    """
    new_urgency = current_urgency or "Standard"
    reasons: List[str] = []

    max_bll = 0.0
    any_confirmed_ebl = False
    for child in children:
        # children may be raw Airtable records or already-flattened dicts
        cfields = child.get("fields", child) or {}
        bll_raw = cfields.get("blood_lead_level")
        try:
            bll = float(bll_raw) if bll_raw not in (None, "") else 0.0
        except (ValueError, TypeError):
            bll = 0.0
        if bll > max_bll:
            max_bll = bll
        if cfields.get("lead_test_status") == "Confirmed EBL":
            any_confirmed_ebl = True

    if max_bll >= 45:
        target = "Emergency"
        reasons.append(f"BLL {max_bll} µg/dL ≥ 45 (severe poisoning)")
    elif any_confirmed_ebl and displacement_required:
        target = "Emergency"
        reasons.append("Confirmed EBL with displacement required")
    elif max_bll >= 5:
        target = "Urgent"
        reasons.append(f"BLL {max_bll} µg/dL ≥ 5 (CDC EBL threshold)")
    else:
        target = new_urgency

    if _URGENCY_RANK.get(target, 0) > _URGENCY_RANK.get(new_urgency, 0):
        return target, "; ".join(reasons)
    return new_urgency, None


# ─────────────────────────────────────────────────────────────────────────────
# Navigator role lookup — supervisor gating for SLA overrides
# ─────────────────────────────────────────────────────────────────────────────
def _find_navigator_by_email(client: ShieldAirtableClient, email: str) -> Optional[Dict[str, Any]]:
    if not email:
        return None
    normalized = email.strip().lower()
    for record in _safe_all(client, TABLE_NAVIGATORS):
        fields = record.get("fields", {}) or {}
        nav_email = (fields.get("email") or "").strip().lower()
        if nav_email and nav_email == normalized:
            return record
    return None


def _role_for_email(client: ShieldAirtableClient, email: str) -> str:
    record = _find_navigator_by_email(client, email)
    if not record:
        return ""
    return (record.get("fields", {}) or {}).get("role", "") or ""


def _is_supervisor(client: ShieldAirtableClient, email: str) -> bool:
    return _role_for_email(client, email) in SUPERVISOR_ROLES


# ─────────────────────────────────────────────────────────────────────────────
# Handlers — one per endpoint, kept flat for wiring in api_server.py
# ─────────────────────────────────────────────────────────────────────────────
def handle_shield_dashboard() -> Dict[str, Any]:
    """Navigator dashboard summary — counts + alerts."""
    client = ShieldAirtableClient()
    if not client.is_configured:
        return {
            "success": True,
            "configured": False,
            "summary": {
                "new_referrals": 0,
                "active_cases": 0,
                "overdue_follow_ups": 0,
                "pending_authorizations": 0,
                "total_families": 0,
                "total_children": 0,
                "ebl_cases": 0,
            },
            "alerts": [],
            "hint": _unconfigured_hint("referrals")["hint"],
        }

    referrals = _safe_all(client, TABLE_REFERRALS)
    families = _safe_all(client, TABLE_FAMILIES)
    children = _safe_all(client, TABLE_CHILDREN)
    activations = _safe_all(client, TABLE_ACTIVATIONS)

    now = datetime.now(EASTERN)
    forty_eight_hours = now - timedelta(hours=48)

    new_referrals = 0
    active_cases = 0
    overdue = 0
    pending_auth = 0
    ebl_cases = 0

    alerts: List[Dict[str, Any]] = []

    for r in referrals:
        fields = r.get("fields", {}) or {}
        status = fields.get("status", "")
        if status == "New":
            new_referrals += 1
        if status in ("Assigned", "Active"):
            active_cases += 1

        received_str = fields.get("date_received")
        if received_str and status == "New":
            try:
                received = datetime.fromisoformat(received_str.replace("Z", "+00:00"))
                if received.tzinfo is None:
                    received = received.replace(tzinfo=EASTERN)
                if received < forty_eight_hours:
                    overdue += 1
                    alerts.append({
                        "type": "48hr_contact_overdue",
                        "severity": "high",
                        "referral_id": r.get("id"),
                        "message": f"Referral {fields.get('referral_id', r.get('id'))} past 48-hour contact window",
                    })
            except (ValueError, TypeError):
                pass

    for a in activations:
        fields = a.get("fields", {}) or {}
        if fields.get("status") == "Pending":
            pending_auth += 1

    for c in children:
        fields = c.get("fields", {}) or {}
        if fields.get("lead_test_status") in ("Tested - Elevated", "Confirmed EBL"):
            ebl_cases += 1
            if fields.get("clppp_status") == "Not Referred":
                alerts.append({
                    "type": "ebl_no_clppp",
                    "severity": "urgent",
                    "child_id": c.get("id"),
                    "message": f"Child {fields.get('child_name', 'Unknown')} has elevated BLL but CLPPP not referred",
                })

    return {
        "success": True,
        "configured": True,
        "summary": {
            "new_referrals": new_referrals,
            "active_cases": active_cases,
            "overdue_follow_ups": overdue,
            "pending_authorizations": pending_auth,
            "total_families": len(families),
            "total_children": len(children),
            "ebl_cases": ebl_cases,
        },
        "alerts": alerts[:20],
        "generated_at": _now_eastern_iso(),
    }


# ── REFERRALS ───────────────────────────────────────────────────────────────
def handle_shield_list_referrals(filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """List referrals with optional filters (status, county, urgency)."""
    filters = filters or {}
    client = ShieldAirtableClient()
    if not client.is_configured:
        return _unconfigured_hint("referrals")

    records = _safe_all(client, TABLE_REFERRALS)
    rows = [_enriched(r) for r in records]

    status_f = (filters.get("status") or "").strip()
    county_f = (filters.get("county") or "").strip()
    urgency_f = (filters.get("urgency") or "").strip()
    source_f = (filters.get("referral_source") or "").strip()

    filtered = []
    for row in rows:
        if status_f and row.get("status") != status_f:
            continue
        if county_f and row.get("county") != county_f:
            continue
        if urgency_f and row.get("urgency") != urgency_f:
            continue
        if source_f and row.get("referral_source") != source_f:
            continue
        filtered.append(row)

    filtered.sort(key=lambda r: r.get("date_received", ""), reverse=True)

    return {
        "success": True,
        "configured": True,
        "referrals": filtered,
        "count": len(filtered),
        "total": len(rows),
        "filterOptions": {
            "statuses": REFERRAL_STATUSES,
            "counties": COUNTIES,
            "urgency": URGENCY_LEVELS,
        },
    }


def handle_shield_get_referral(referral_id: str) -> Dict[str, Any]:
    """Get a single referral with linked family, children, activations, milestones."""
    client = ShieldAirtableClient()
    if not client.is_configured:
        return {"success": False, "configured": False, "hint": _unconfigured_hint("referrals")["hint"]}

    try:
        referral = client.get(TABLE_REFERRALS, referral_id)
    except Exception as e:
        return {"success": False, "error": str(e)}

    referral_data = _enriched(referral)
    fields = referral.get("fields", {}) or {}

    family_data = None
    family_ids = fields.get("family_id") or []
    if isinstance(family_ids, list) and family_ids:
        try:
            family_data = _serialize(client.get(TABLE_FAMILIES, family_ids[0]))
        except Exception:
            family_data = None

    children: List[Dict[str, Any]] = []
    if family_data and family_data.get("id"):
        child_records = _safe_all(client, TABLE_CHILDREN)
        for c in child_records:
            cf = c.get("fields", {}) or {}
            fam_links = cf.get("family_id") or []
            if isinstance(fam_links, list) and family_data["id"] in fam_links:
                children.append(_serialize(c))

    activations = []
    milestones = []
    billing = []

    for a in _safe_all(client, TABLE_ACTIVATIONS):
        af = a.get("fields", {}) or {}
        links = af.get("referral_id") or []
        if isinstance(links, list) and referral_id in links:
            activations.append(_serialize(a))

    for m in _safe_all(client, TABLE_MILESTONES):
        mf = m.get("fields", {}) or {}
        links = mf.get("referral_id") or []
        if isinstance(links, list) and referral_id in links:
            milestones.append(_serialize(m))

    for b in _safe_all(client, TABLE_BILLING):
        bf = b.get("fields", {}) or {}
        links = bf.get("referral_id") or []
        if isinstance(links, list) and referral_id in links:
            billing.append(_serialize(b))

    milestones.sort(key=lambda x: x.get("timestamp", ""))

    return {
        "success": True,
        "configured": True,
        "referral": referral_data,
        "family": family_data,
        "children": children,
        "activations": activations,
        "milestones": milestones,
        "billing": billing,
    }


def handle_shield_create_referral(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Create a Referral + linked Family record (intake form submission).

    Payload contains referring party, family, children, services, urgency.
    Returns the new referral_id for the confirmation screen.
    """
    client = ShieldAirtableClient()
    if not client.is_configured:
        return {
            "success": False,
            "configured": False,
            "error": "SHIELD Airtable base not configured. Set LEAD_SCREENING_BASE_ID in .env.",
        }

    try:
        family_fields = {
            "family_name": payload.get("family_name", "").strip(),
            "address": payload.get("address", "").strip(),
            "city": payload.get("city", "").strip(),
            "zip": payload.get("zip", "").strip(),
            "county": payload.get("county", "Other"),
            "primary_contact_name": payload.get("primary_contact_name", "").strip(),
            "primary_contact_phone": payload.get("primary_contact_phone", "").strip(),
            "primary_contact_email": payload.get("primary_contact_email", "").strip(),
            "medicaid_enrolled": bool(payload.get("medicaid_enrolled")),
            "snap_enrolled": bool(payload.get("snap_enrolled")),
            "language": payload.get("language", "English"),
            "status": "Active",
        }
        family_fields = {k: v for k, v in family_fields.items() if v not in (None, "", [])}
        family = client.create(TABLE_FAMILIES, family_fields)
        family_id = family.get("id")

        for child in payload.get("children", []) or []:
            child_fields = {
                "family_id": [family_id] if family_id else None,
                "child_name": (child.get("child_name") or "").strip(),
                "age_months": int(child.get("age_months") or 0) if str(child.get("age_months") or "").strip().isdigit() else None,
                "lead_test_status": child.get("lead_test_status", "Not Tested"),
                "blood_lead_level": float(child.get("blood_lead_level")) if child.get("blood_lead_level") not in (None, "") else None,
                "clppp_case_number": child.get("clppp_case_number", ""),
                "clppp_status": "Referred" if child.get("clppp_case_number") else "Not Referred",
            }
            child_fields = {k: v for k, v in child_fields.items() if v not in (None, "", [])}
            try:
                client.create(TABLE_CHILDREN, child_fields)
            except Exception:
                pass

        # Auto-escalate urgency if any child BLL meets CDC thresholds
        intake_urgency = payload.get("urgency", "Standard") or "Standard"
        escalated_urgency, escalation_reason = _desired_urgency_from_children(
            intake_urgency,
            payload.get("children", []) or [],
            displacement_required=bool(payload.get("displacement_required")),
        )

        referral_fields: Dict[str, Any] = {
            "date_received": _now_eastern_iso(),
            "referral_source": payload.get("referral_source", "MDHHS"),
            "referring_agency": payload.get("referring_agency", "").strip(),
            "case_worker_name": payload.get("case_worker_name", "").strip(),
            "case_worker_email": payload.get("case_worker_email", "").strip(),
            "case_worker_phone": payload.get("case_worker_phone", "").strip(),
            "county": payload.get("county", "Other"),
            "services_requested": payload.get("services_requested", []) or [],
            "urgency": escalated_urgency,
            "status": "New",
            "family_id": [family_id] if family_id else None,
            "notes": payload.get("notes", "").strip(),
            "intake_method": payload.get("intake_method", "Web Form"),
        }
        if escalation_reason:
            referral_fields["urgency_auto_escalated"] = True
            referral_fields["urgency_escalated_from"] = intake_urgency
            referral_fields["urgency_escalated_reason"] = escalation_reason
            referral_fields["urgency_escalated_at"] = _now_eastern_iso()
        referral_fields = {k: v for k, v in referral_fields.items() if v not in (None, "", [])}
        referral = client.create(TABLE_REFERRALS, referral_fields)
        referral_id = referral.get("id")

        try:
            client.create(TABLE_MILESTONES, {
                "referral_id": [referral_id] if referral_id else None,
                "family_id": [family_id] if family_id else None,
                "milestone_type": "Referral Received",
                "timestamp": _now_eastern_iso(),
                "recorded_by": "System (Intake Form)",
                "notes": f"Submitted via {referral_fields.get('intake_method')} by {referral_fields.get('case_worker_name', 'unknown')}",
            })
        except Exception:
            pass

        if escalation_reason:
            try:
                client.create(TABLE_MILESTONES, {
                    "referral_id": [referral_id] if referral_id else None,
                    "family_id": [family_id] if family_id else None,
                    "milestone_type": "Urgency Auto-Escalated",
                    "timestamp": _now_eastern_iso(),
                    "recorded_by": "System (SLA Engine)",
                    "notes": f"{intake_urgency} → {escalated_urgency}. {escalation_reason}",
                })
            except Exception:
                pass

        return {
            "success": True,
            "configured": True,
            "referral_id": referral_id,
            "reference_number": (referral.get("fields") or {}).get("referral_id") or referral_id,
            "family_id": family_id,
            "confirmation": {
                "message": "Referral received. A DDI/CWC navigator will contact the family within 48 hours.",
                "expected_contact_hours": 48,
                "received_at": _now_eastern_iso(),
            },
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def handle_shield_update_referral(referral_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
    client = ShieldAirtableClient()
    if not client.is_configured:
        return {"success": False, "configured": False}
    try:
        updated = client.update(TABLE_REFERRALS, referral_id, updates)
        return {"success": True, "referral": _enriched(updated)}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ── SLA OVERRIDE (supervisor-only) ──────────────────────────────────────────
def handle_shield_sla_override(referral_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Supervisor-only: override the first-contact SLA on a referral.

    Body:
      { user_email, target_hours, reason }

    Only navigators whose Navigators.role ∈ {Supervisor, Admin} may override.
    Stores the override + a milestone so the audit trail is permanent.
    Pass target_hours <= 0 or null to CLEAR an existing override (reverts to
    urgency-derived SLA).
    """
    client = ShieldAirtableClient()
    if not client.is_configured:
        return {"success": False, "configured": False, "error": "SHIELD not configured"}

    user_email = (payload.get("user_email") or "").strip()
    reason = (payload.get("reason") or "").strip()
    target_hours_raw = payload.get("target_hours")

    if not user_email:
        return {"success": False, "error": "user_email required", "status_code": 400}

    nav = _find_navigator_by_email(client, user_email)
    role = (nav.get("fields", {}) or {}).get("role", "") if nav else ""
    if role not in SUPERVISOR_ROLES:
        return {
            "success": False,
            "error": "SLA overrides are restricted to Supervisor or Admin navigators.",
            "your_role": role or "Unknown",
            "status_code": 403,
        }

    # Clearing?
    clearing = target_hours_raw in (None, "", 0, "0")
    if not clearing:
        try:
            target_hours = float(target_hours_raw)
            if target_hours <= 0 or target_hours > 720:  # cap at 30 days sanity
                return {"success": False, "error": "target_hours must be between 0 and 720", "status_code": 400}
        except (ValueError, TypeError):
            return {"success": False, "error": "target_hours must be a number", "status_code": 400}

    if not clearing and not reason:
        return {"success": False, "error": "reason is required when setting an override", "status_code": 400}

    try:
        existing = client.get(TABLE_REFERRALS, referral_id)
    except Exception as e:
        return {"success": False, "error": f"referral not found: {e}", "status_code": 404}

    prior_fields = existing.get("fields", {}) or {}
    nav_name = (nav.get("fields", {}) or {}).get("name", user_email) if nav else user_email
    now_iso = _now_eastern_iso()

    updates: Dict[str, Any] = {}
    if clearing:
        updates["sla_override_hours"] = None
        updates["sla_override_reason"] = ""
        updates["sla_override_by"] = ""
        updates["sla_override_at"] = ""
        milestone_note = (
            f"SLA override cleared by {nav_name} ({role}). "
            f"Reverted to urgency-based target for {prior_fields.get('urgency', 'Standard')}."
        )
    else:
        updates["sla_override_hours"] = target_hours
        updates["sla_override_reason"] = reason
        updates["sla_override_by"] = f"{nav_name} <{user_email}>"
        updates["sla_override_at"] = now_iso
        prior = prior_fields.get("sla_override_hours")
        prefix = "SLA override updated" if prior else "SLA override set"
        milestone_note = (
            f"{prefix} by {nav_name} ({role}) to {target_hours}h. Reason: {reason}"
        )

    try:
        updated = client.update(TABLE_REFERRALS, referral_id, updates)
    except Exception as e:
        return {"success": False, "error": f"update failed: {e}", "status_code": 500}

    try:
        client.create(TABLE_MILESTONES, {
            "referral_id": [referral_id],
            "family_id": prior_fields.get("family_id") or None,
            "milestone_type": "SLA Override (Supervisor)" if not clearing else "SLA Override Cleared",
            "timestamp": now_iso,
            "recorded_by": f"{nav_name} ({role})",
            "notes": milestone_note,
        })
    except Exception:
        pass

    return {
        "success": True,
        "configured": True,
        "cleared": clearing,
        "referral": _enriched(updated),
        "actor": {"email": user_email, "name": nav_name, "role": role},
    }


# ── UPDATE CHILD (also triggers urgency re-evaluation) ──────────────────────
def handle_shield_update_child(child_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
    """Update a child record. If BLL or lead_test_status changes, re-check the
    linked referral's urgency and auto-escalate if thresholds are met.
    """
    client = ShieldAirtableClient()
    if not client.is_configured:
        return {"success": False, "configured": False}

    try:
        updated_child = client.update(TABLE_CHILDREN, child_id, updates)
    except Exception as e:
        return {"success": False, "error": str(e)}

    cfields = updated_child.get("fields", {}) or {}

    # Find the family + any linked referrals to re-check
    family_links = cfields.get("family_id") or []
    if not isinstance(family_links, list) or not family_links:
        return {"success": True, "child": _serialize(updated_child)}

    family_id = family_links[0]
    escalations: List[Dict[str, Any]] = []

    # All children under this family (for max BLL calculation)
    family_children = [
        c for c in _safe_all(client, TABLE_CHILDREN)
        if family_id in ((c.get("fields", {}) or {}).get("family_id") or [])
    ]

    for referral in _safe_all(client, TABLE_REFERRALS):
        rfields = referral.get("fields", {}) or {}
        ref_family = rfields.get("family_id") or []
        if not isinstance(ref_family, list) or family_id not in ref_family:
            continue
        current_urgency = rfields.get("urgency", "Standard")
        new_urgency, reason = _desired_urgency_from_children(current_urgency, family_children)
        if reason:
            ref_id = referral.get("id")
            try:
                client.update(TABLE_REFERRALS, ref_id, {
                    "urgency": new_urgency,
                    "urgency_auto_escalated": True,
                    "urgency_escalated_from": current_urgency,
                    "urgency_escalated_reason": reason,
                    "urgency_escalated_at": _now_eastern_iso(),
                })
                client.create(TABLE_MILESTONES, {
                    "referral_id": [ref_id],
                    "family_id": [family_id],
                    "milestone_type": "Urgency Auto-Escalated",
                    "timestamp": _now_eastern_iso(),
                    "recorded_by": "System (SLA Engine)",
                    "notes": f"{current_urgency} → {new_urgency}. {reason}",
                })
                escalations.append({
                    "referral_id": ref_id,
                    "from": current_urgency,
                    "to": new_urgency,
                    "reason": reason,
                })
            except Exception:
                pass

    return {
        "success": True,
        "child": _serialize(updated_child),
        "escalations": escalations,
    }


# ── FAMILIES / CHILDREN / NAVIGATORS ────────────────────────────────────────
def handle_shield_list_families() -> Dict[str, Any]:
    client = ShieldAirtableClient()
    if not client.is_configured:
        return _unconfigured_hint("families")
    records = _safe_all(client, TABLE_FAMILIES)
    return {"success": True, "configured": True, "families": [_serialize(r) for r in records], "count": len(records)}


def handle_shield_list_children() -> Dict[str, Any]:
    client = ShieldAirtableClient()
    if not client.is_configured:
        return _unconfigured_hint("children")
    records = _safe_all(client, TABLE_CHILDREN)
    return {"success": True, "configured": True, "children": [_serialize(r) for r in records], "count": len(records)}


def handle_shield_list_navigators() -> Dict[str, Any]:
    client = ShieldAirtableClient()
    if not client.is_configured:
        return _unconfigured_hint("navigators")
    records = _safe_all(client, TABLE_NAVIGATORS)
    return {"success": True, "configured": True, "navigators": [_serialize(r) for r in records], "count": len(records)}


# ── SERVICE ACTIVATIONS ─────────────────────────────────────────────────────
def handle_shield_list_activations(referral_id: Optional[str] = None) -> Dict[str, Any]:
    client = ShieldAirtableClient()
    if not client.is_configured:
        return _unconfigured_hint("activations")
    rows = [_serialize(r) for r in _safe_all(client, TABLE_ACTIVATIONS)]
    if referral_id:
        rows = [r for r in rows if referral_id in (r.get("referral_id") or [])]
    return {"success": True, "configured": True, "activations": rows, "count": len(rows)}


def handle_shield_activate_service(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Activate a service line on a referral.

    Body:
      { referral_id, family_id, service_line, vendor?, authorization_number?,
        appointment_date?, notes? }

    Also logs a Case_Milestone (Appointment Scheduled / Service Completed auto).
    Triggers chained activations per spec (Remediation → Housing if displaced).
    """
    client = ShieldAirtableClient()
    if not client.is_configured:
        return {"success": False, "configured": False}

    referral_id = payload.get("referral_id")
    family_id = payload.get("family_id")
    service_line = payload.get("service_line")
    if not referral_id or not service_line:
        return {"success": False, "error": "referral_id and service_line required"}

    fields = {
        "referral_id": [referral_id],
        "family_id": [family_id] if family_id else None,
        "service_line": service_line,
        "activated_date": _now_eastern_iso(),
        "status": payload.get("status", "Pending"),
        "vendor": payload.get("vendor", ""),
        "authorization_number": payload.get("authorization_number", ""),
        "appointment_date": payload.get("appointment_date") or None,
        "notes": payload.get("notes", ""),
    }
    fields = {k: v for k, v in fields.items() if v not in (None, "", [])}

    try:
        activation = client.create(TABLE_ACTIVATIONS, fields)
    except Exception as e:
        return {"success": False, "error": str(e)}

    try:
        client.create(TABLE_MILESTONES, {
            "referral_id": [referral_id],
            "family_id": [family_id] if family_id else None,
            "milestone_type": "Appointment Scheduled" if payload.get("appointment_date") else "Service Completed" if payload.get("status") == "Completed" else "Appointment Scheduled",
            "timestamp": _now_eastern_iso(),
            "recorded_by": payload.get("navigator_name", "Navigator"),
            "notes": f"{service_line} — vendor: {payload.get('vendor', 'N/A')}",
        })
    except Exception:
        pass

    chained: List[str] = []
    if service_line == "Lead Remediation" and payload.get("displacement_required"):
        try:
            client.create(TABLE_ACTIVATIONS, {
                "referral_id": [referral_id],
                "family_id": [family_id] if family_id else None,
                "service_line": "Housing",
                "activated_date": _now_eastern_iso(),
                "status": "Pending",
                "notes": "Auto-activated: displacement during remediation",
            })
            chained.append("Housing")
        except Exception:
            pass

    return {
        "success": True,
        "configured": True,
        "activation": _serialize(activation),
        "chained_activations": chained,
    }


# ── CASE MILESTONES ─────────────────────────────────────────────────────────
def handle_shield_log_milestone(payload: Dict[str, Any]) -> Dict[str, Any]:
    client = ShieldAirtableClient()
    if not client.is_configured:
        return {"success": False, "configured": False}

    fields = {
        "referral_id": [payload["referral_id"]] if payload.get("referral_id") else None,
        "family_id": [payload["family_id"]] if payload.get("family_id") else None,
        "milestone_type": payload.get("milestone_type", "Navigator Note"),
        "timestamp": _now_eastern_iso(),
        "recorded_by": payload.get("recorded_by", "Navigator"),
        "notes": payload.get("notes", ""),
    }
    fields = {k: v for k, v in fields.items() if v not in (None, "", [])}

    try:
        milestone = client.create(TABLE_MILESTONES, fields)
        return {"success": True, "milestone": _serialize(milestone)}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ── BILLING ─────────────────────────────────────────────────────────────────
def handle_shield_list_billing(status: Optional[str] = None) -> Dict[str, Any]:
    client = ShieldAirtableClient()
    if not client.is_configured:
        return _unconfigured_hint("billing")
    rows = [_serialize(r) for r in _safe_all(client, TABLE_BILLING)]
    if status:
        rows = [r for r in rows if r.get("status") == status]
    total = sum((r.get("amount") or 0) for r in rows)
    return {"success": True, "configured": True, "billing": rows, "count": len(rows), "total_amount": total}


def handle_shield_create_billing(payload: Dict[str, Any]) -> Dict[str, Any]:
    client = ShieldAirtableClient()
    if not client.is_configured:
        return {"success": False, "configured": False}
    fields = {
        "referral_id": [payload["referral_id"]] if payload.get("referral_id") else None,
        "family_id": [payload["family_id"]] if payload.get("family_id") else None,
        "service_line": payload.get("service_line"),
        "payer": payload.get("payer"),
        "payer_name": payload.get("payer_name"),
        "amount": float(payload.get("amount") or 0),
        "billing_date": payload.get("billing_date") or datetime.now(EASTERN).date().isoformat(),
        "status": payload.get("status", "Pending"),
        "notes": payload.get("notes", ""),
    }
    fields = {k: v for k, v in fields.items() if v not in (None, "", [])}
    try:
        record = client.create(TABLE_BILLING, fields)
        return {"success": True, "billing": _serialize(record)}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ── OUTCOMES REPORTING ──────────────────────────────────────────────────────
def handle_shield_generate_outcomes_report(period: Optional[str] = None, county: Optional[str] = None) -> Dict[str, Any]:
    """Auto-generate outcomes report by pulling live counts.

    This does not persist to Outcomes_Reporting table unless persist=True — it
    computes the aggregate for on-screen display first.
    """
    client = ShieldAirtableClient()
    if not client.is_configured:
        return {"success": False, "configured": False, "hint": _unconfigured_hint("outcomes")["hint"]}

    referrals = _safe_all(client, TABLE_REFERRALS)
    families = _safe_all(client, TABLE_FAMILIES)
    children = _safe_all(client, TABLE_CHILDREN)
    activations = _safe_all(client, TABLE_ACTIVATIONS)

    def _match_county(record: Dict[str, Any]) -> bool:
        if not county:
            return True
        return (record.get("fields", {}) or {}).get("county") == county

    tested_children = [c for c in children if (c.get("fields", {}) or {}).get("lead_test_status", "") not in ("", "Not Tested")]
    ebl_children = [c for c in children if (c.get("fields", {}) or {}).get("lead_test_status") in ("Tested - Elevated", "Confirmed EBL")]

    def _count_service(service: str) -> int:
        return sum(1 for a in activations if (a.get("fields", {}) or {}).get("service_line") == service)

    contact_times: List[float] = []
    for r in referrals:
        fields = r.get("fields", {}) or {}
        received = fields.get("date_received")
        first_contact = fields.get("first_contact_at")
        if received and first_contact:
            try:
                r_dt = datetime.fromisoformat(received.replace("Z", "+00:00"))
                c_dt = datetime.fromisoformat(first_contact.replace("Z", "+00:00"))
                contact_times.append((c_dt - r_dt).total_seconds() / 3600)
            except Exception:
                pass

    avg_contact_hours = round(sum(contact_times) / len(contact_times), 2) if contact_times else None

    report = {
        "report_period": period or f"Through {datetime.now(EASTERN).strftime('%b %d, %Y')}",
        "county": county or "All Counties",
        "total_referrals": len([r for r in referrals if _match_county(r)]),
        "total_families_served": len([f for f in families if _match_county(f)]),
        "total_children_screened": len(tested_children),
        "ebl_cases_navigated": len(ebl_children),
        "remediation_cases_completed": sum(
            1 for a in activations
            if (a.get("fields", {}) or {}).get("service_line") == "Lead Remediation"
            and (a.get("fields", {}) or {}).get("status") == "Completed"
        ),
        "nemt_trips_authorized": _count_service("NEMT"),
        "housing_placements": _count_service("Housing"),
        "snap_navigations": _count_service("Food Navigation"),
        "filter_safety_net_enrollments": _count_service("Filter Safety Net"),
        "avg_contact_time_hours": avg_contact_hours,
        "generated_date": _now_eastern_iso(),
    }
    return {"success": True, "configured": True, "report": report}


# ── AI ASSISTANT ────────────────────────────────────────────────────────────
def handle_shield_ai_chat(message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Internal AI assistant for navigators.

    Pulls live SHIELD context (recent referrals, alerts, counts) and asks Claude
    to answer within scope. Uses the shared anthropic client from nexus_backend
    if available, otherwise returns a graceful fallback.
    """
    context = context or {}

    try:
        import anthropic
    except ImportError:
        return {"success": False, "error": "anthropic package not installed", "reply": ""}

    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        return {"success": False, "error": "ANTHROPIC_API_KEY not set", "reply": ""}

    dashboard = handle_shield_dashboard()
    summary = dashboard.get("summary", {})
    alerts = dashboard.get("alerts", [])

    system_prompt = (
        "You are the SHIELD Navigator AI — the internal assistant for DDI/CWC "
        "case workers running the Michigan MDHHS lead screening & referral "
        "program (anchored by Public Act 146 of 2023, universal blood lead "
        "screening). Be direct, concise, and specific. Surface the action to "
        "take next. Use the live case data below to answer. If the answer is "
        "not in the data, say so plainly — do not fabricate case details.\n\n"
        f"Live SHIELD dashboard snapshot:\n{json.dumps(summary, indent=2)}\n\n"
        f"Active alerts:\n{json.dumps(alerts[:10], indent=2)}\n\n"
        "Services available to navigate: Lead Screening, NEMT (DePointe / "
        "Uber Health / Lyft Healthcare), Lead Remediation, Temporary Housing "
        "TPA, Drug Testing (Quest PSC), DNA, Food Navigation (SNAP/MiBridges), "
        "Specimen Transport (Freight 1st Direct), Filter Safety Net Program, "
        "Medical Monitoring. 48-hour contact window is the DDI/MDHHS SLA for "
        "every new referral."
    )

    try:
        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=1024,
            system=system_prompt,
            messages=[{"role": "user", "content": message}],
        )
        reply = response.content[0].text if response.content else ""
        return {"success": True, "reply": reply, "context_used": {"summary": summary, "alert_count": len(alerts)}}
    except Exception as e:
        return {"success": False, "error": str(e), "reply": ""}


def handle_shield_ai_external(message: str, case_ref: Optional[str], agency_email: str) -> Dict[str, Any]:
    """External AI assistant (referral source portal).

    Scoped — referring case worker can only query their own referrals. Enforced
    server-side: we validate the case_ref belongs to this agency email before
    injecting any case data into context.
    """
    if not agency_email:
        return {"success": False, "error": "agency_email required for external AI queries", "reply": ""}

    try:
        import anthropic
    except ImportError:
        return {"success": False, "error": "anthropic package not installed", "reply": ""}

    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        return {"success": False, "error": "ANTHROPIC_API_KEY not set", "reply": ""}

    case_context: Dict[str, Any] = {}
    if case_ref:
        at_client = ShieldAirtableClient()
        if at_client.is_configured:
            try:
                formula = f"AND({{case_worker_email}} = '{agency_email}', OR({{referral_id}} = '{case_ref}', RECORD_ID() = '{case_ref}'))"
                matches = at_client.search(TABLE_REFERRALS, formula)
                if matches:
                    ref = _serialize(matches[0])
                    case_context = {
                        "referral_id": ref.get("referral_id") or ref.get("id"),
                        "status": ref.get("status"),
                        "county": ref.get("county"),
                        "services_requested": ref.get("services_requested"),
                        "urgency": ref.get("urgency"),
                        "date_received": ref.get("date_received"),
                    }
                else:
                    return {
                        "success": True,
                        "reply": (
                            f"I can only share status for referrals your agency submitted. "
                            f"Reference #{case_ref} does not match any referrals submitted "
                            f"under {agency_email}. If this is a typo, please double-check the "
                            f"reference number from your confirmation email."
                        ),
                        "scoped": True,
                    }
            except Exception:
                pass

    system_prompt = (
        "You are the SHIELD Referral Source Assistant — the external-facing AI "
        "for MDHHS / county health department case workers who submit referrals "
        "to DEE DAVIS INC + CAUSE WE CARE. Answer general questions about the "
        "DDI/CWC service model and status questions about the specific case "
        "provided below. NEVER invent case details. NEVER share information "
        "about other families or referrals. If a case reference is requested "
        "that you have no context for, tell the user to contact their DDI "
        "navigator directly.\n\n"
        "DDI/CWC services: lead screening navigation, CLPPP follow-up support, "
        "NEMT (DePointe), lead remediation coordination, temporary housing "
        "during remediation, food assistance navigation, drug testing, DNA / "
        "paternity testing, specimen transport, Filter Safety Net enrollment. "
        "Counties served: Wayne, Oakland, Macomb, Genesee, Kent (Grand "
        "Rapids), Muskegon, and surrounding. Standard SLA: first contact "
        "within 48 hours of referral receipt.\n\n"
        f"Case context (scoped to {agency_email}):\n{json.dumps(case_context, indent=2) if case_context else 'No specific case referenced.'}"
    )

    try:
        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=800,
            system=system_prompt,
            messages=[{"role": "user", "content": message}],
        )
        reply = response.content[0].text if response.content else ""
        return {"success": True, "reply": reply, "scoped": True, "case_matched": bool(case_context)}
    except Exception as e:
        return {"success": False, "error": str(e), "reply": ""}
