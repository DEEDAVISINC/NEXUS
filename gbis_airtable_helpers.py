"""
GBIS — unified Airtable field names and create hooks (alerts).
All GRANT OPPORTUNITIES writes should use create_grant_opportunity().
"""
from __future__ import annotations

from datetime import date, datetime
from typing import Any, Dict, Optional

# Canonical field names (Title Case — match Airtable column names after migration).
FN = {
    "grant_name": "Grant Name",
    "funder_organization": "Funder Organization",
    "grant_url": "Grant URL",
    "eligibility": "Eligibility",
    "notes": "Notes",
    "grant_id": "Grant ID",
    "deadline": "Deadline",
    "entity": "Entity",
    "grant_source_type": "Grant Source Type",
    "recommendation": "Recommendation",
    "last_source_check": "Last Source Check",
    "priority_level": "Priority Level",
    "ddi_strategy": "DDI Strategy Note",
}


def grant_name_from_fields(fields: Dict[str, Any]) -> str:
    return (fields.get("Grant Name") or fields.get("GRANT NAME") or "").strip()


def entity_from_fields(fields: Dict[str, Any]) -> str:
    v = fields.get("Entity") or fields.get("ENTITY") or fields.get("Applicant Entity") or ""
    if isinstance(v, list) and v:
        v = v[0]
    return str(v).strip() if v else ""


def recommendation_from_fields(fields: Dict[str, Any]) -> str:
    return (fields.get("Recommendation") or fields.get("recommendation") or "").strip()


def create_grant_opportunity(airtable, record: Dict[str, Any]):
    """
    Create a GRANT OPPORTUNITIES row and run proactive alert hook.
    Returns the PyAirtable record.
    """
    created = airtable.create_record("GRANT OPPORTUNITIES", record)
    try:
        rid = created["id"] if isinstance(created, dict) else getattr(created, "id", None)
        merged = {**record}
        if rid:
            try:
                from gbis_notifications import notify_if_auto_pursue

                notify_if_auto_pursue(str(rid), merged)
            except Exception:
                pass
    except Exception:
        pass
    return created


def map_applicant_to_entity(applicant_label: str) -> str:
    """Map Research Lane applicant string to Entity single-select."""
    return entity_from_applicant_label(applicant_label)


def entity_from_applicant_label(label: str) -> str:
    """Map seed Applicant Entity / applicant text to Entity: DDI | CWC | BOTH."""
    if not label:
        return "DDI"
    t = label.strip()
    if t.upper() == "BOTH":
        return "BOTH"
    if "Teaming" in t or "DDI +" in t or "DDI + Cause" in t:
        return "BOTH"
    if "Cause We Care" in t:
        return "CWC"
    return "DDI"


def priority_to_recommendation(priority_level: str) -> str:
    pl = (priority_level or "").strip()
    if pl.startswith("Critical"):
        return "Auto-Pursue"
    if pl.startswith("High"):
        return "Review"
    if pl.startswith("Medium"):
        return "Consider"
    return "Skip"


def today_iso() -> str:
    return date.today().isoformat()
