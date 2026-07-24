"""
GBIS — unified Airtable field names and create hooks (alerts).
All GRANT OPPORTUNITIES writes should use create_grant_opportunity().

Airtable GRANT OPPORTUNITIES writable columns (verified June 2026):
  GRANT NAME, FUNDER ORGANIZATION, GRANT URL, ELIGIBILITY, NOTES

Computed / read-only in Airtable (never write):
  DISCOVERY DATE, OPPORTUNITY ID, APPLICATION WINDOW, DAYS UNTIL DEADLINE,
  LAST UPDATED, ROI RATING, Attachment Summary

Extra metadata (Grant ID, Entity, Source Type, Deadline, etc.) is packed into NOTES.
"""
from __future__ import annotations

import re
from datetime import date
from typing import Any, Dict, List, Optional

# Logical keys → Airtable column names
AIRTABLE_WRITABLE = {
    "grant_name": "GRANT NAME",
    "funder_organization": "FUNDER ORGANIZATION",
    "grant_url": "GRANT URL",
    "eligibility": "ELIGIBILITY",
    "notes": "NOTES",
}

# Backward-compatible FN map (logical → Airtable)
FN = {k: v for k, v in AIRTABLE_WRITABLE.items()}

# Keys packed into NOTES when not writable as columns
_NOTE_PACK_KEYS = (
    "grant id",
    "opportunity number",
    "deadline",
    "entity",
    "grant source type",
    "recommendation",
    "last source check",
    "priority level",
    "ddi strategy note",
    "applicant entity",
    "service lane",
    "research subtype",
    "funding type",
    "grant amount",
)

_KEY_ALIASES = {
    "grant name": "grant_name",
    "grant_name": "grant_name",
    "funder organization": "funder_organization",
    "funder_organization": "funder_organization",
    "grant url": "grant_url",
    "grant_url": "grant_url",
    "eligibility": "eligibility",
    "notes": "notes",
    "grant id": "grant_id_meta",
    "grant_id": "grant_id_meta",
    "opportunity number": "opportunity_number_meta",
    "opportunity_number": "opportunity_number_meta",
    "deadline": "deadline_meta",
    "entity": "entity_meta",
    "grant source type": "source_type_meta",
    "grant_source_type": "source_type_meta",
    "recommendation": "recommendation_meta",
    "last source check": "last_source_check_meta",
    "last_source_check": "last_source_check_meta",
    "priority level": "priority_level_meta",
    "priority_level": "priority_level_meta",
    "ddi strategy note": "ddi_strategy_meta",
    "ddi_strategy_note": "ddi_strategy_meta",
    "applicant entity": "applicant_entity_meta",
    "service lane": "service_lane_meta",
    "research subtype": "research_subtype_meta",
    "funding type": "funding_type_meta",
    "grant amount": "grant_amount_meta",
}


def _normalize_key(key: str) -> str:
    return _KEY_ALIASES.get(key.strip().lower(), key.strip().lower())


def _note_line(label: str, value: Any) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    return f"{label}: {text}"


def normalize_grant_record(record: Dict[str, Any]) -> Dict[str, Any]:
    """
    Map caller fields (Title Case or ALL CAPS) to Airtable-writable columns.
    Non-writable metadata is appended to NOTES.
    """
    grant_name = ""
    funder = ""
    url = ""
    eligibility = ""
    notes_body: List[str] = []
    packed: List[str] = []

    for key, value in record.items():
        if value is None or value == "":
            continue
        canon = _normalize_key(key)
        if canon == "grant_name":
            grant_name = str(value).strip()[:255]
        elif canon == "funder_organization":
            funder = str(value).strip()
        elif canon == "grant_url":
            url = str(value).strip()
        elif canon == "eligibility":
            eligibility = str(value).strip()
        elif canon == "notes":
            notes_body.append(str(value).strip())
        elif canon.endswith("_meta"):
            label = {
                "grant_id_meta": "GRANT ID",
                "opportunity_number_meta": "Opportunity Number",
                "deadline_meta": "Deadline",
                "entity_meta": "Entity",
                "source_type_meta": "Type",
                "recommendation_meta": "Recommendation",
                "last_source_check_meta": "Last Source Check",
                "priority_level_meta": "Priority",
                "ddi_strategy_meta": "DDI Strategy",
                "applicant_entity_meta": "Applicant",
                "service_lane_meta": "Lane",
                "research_subtype_meta": "Subtype",
                "funding_type_meta": "Funding",
                "grant_amount_meta": "Amount",
            }.get(canon, canon)
            line = _note_line(label, value)
            if line:
                packed.append(line)

    if not grant_name:
        raise ValueError("Grant record missing grant name")

    existing_notes = "\n".join(n for n in notes_body if n.strip())
    extra = "\n".join(packed)
    if existing_notes and extra:
        merged_notes = f"{existing_notes}\n{extra}"
    else:
        merged_notes = existing_notes or extra

    out: Dict[str, Any] = {
        AIRTABLE_WRITABLE["grant_name"]: grant_name,
        AIRTABLE_WRITABLE["funder_organization"]: funder or "Unknown",
        AIRTABLE_WRITABLE["grant_url"]: url or "https://www.grants.gov",
        AIRTABLE_WRITABLE["notes"]: merged_notes or "Imported by NEXUS GBIS",
    }
    if eligibility:
        out[AIRTABLE_WRITABLE["eligibility"]] = eligibility[:10000]
    return out


def grant_name_from_fields(fields: Dict[str, Any]) -> str:
    return (fields.get("GRANT NAME") or fields.get("Grant Name") or "").strip()


def grant_id_from_fields(fields: Dict[str, Any]) -> str:
    direct = fields.get("Grant ID") or fields.get("GRANT ID") or ""
    if direct:
        return str(direct).strip()
    notes = fields.get("NOTES") or fields.get("Notes") or ""
    m = re.search(r"(?:GRANT ID|Grant ID):\s*(\S+)", str(notes), re.I)
    return m.group(1).strip() if m else ""


def note_value(fields: Dict[str, Any], label: str) -> str:
    notes = str(fields.get("NOTES") or fields.get("Notes") or "")
    m = re.search(rf"(?:{re.escape(label)}):\s*(.+)$", notes, re.I | re.M)
    return m.group(1).strip() if m else ""


def entity_from_fields(fields: Dict[str, Any]) -> str:
    v = (
        fields.get("Entity")
        or fields.get("ENTITY")
        or fields.get("Applicant Entity")
        or note_value(fields, "Entity")
        or note_value(fields, "Applicant")
        or ""
    )
    if isinstance(v, list) and v:
        v = v[0]
    return str(v).strip() if v else ""


def source_type_from_fields(fields: Dict[str, Any]) -> str:
    v = fields.get("Grant Source Type") or fields.get("GRANT SOURCE TYPE") or note_value(fields, "Type")
    return str(v).strip() if v else ""


def recommendation_from_fields(fields: Dict[str, Any]) -> str:
    return (
        fields.get("Recommendation")
        or fields.get("RECOMMENDATION")
        or note_value(fields, "Recommendation")
        or ""
    ).strip()


def create_grant_opportunity(airtable, record: Dict[str, Any]):
    """
    Create a GRANT OPPORTUNITIES row and run proactive alert hook.
    Returns the PyAirtable record.
    """
    payload = normalize_grant_record(record)
    created = airtable.create_record("GRANT OPPORTUNITIES", payload)
    try:
        rid = created["id"] if isinstance(created, dict) else getattr(created, "id", None)
        if rid:
            try:
                from gbis_notifications import notify_if_auto_pursue

                notify_if_auto_pursue(str(rid), payload)
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


def applicant_label_from_entity_code(code: str) -> str:
    c = (code or "").upper()
    if c == "BOTH":
        return "DDI + Cause We Care (Teaming)"
    if c == "CWC":
        return "Cause We Care"
    return "DDI"


def classify_grant_entity(
    title: str = "",
    funder: str = "",
    description: str = "",
    eligibility: str = "",
    notes: str = "",
) -> str:
    """Return Entity code: CWC | BOTH | DDI."""
    from nexus_backend import ResearchLaneDetector

    desc = description or notes
    applicant = ResearchLaneDetector().assign_applicant_entity(
        funder=funder,
        description=desc,
        title=title,
        eligibility=eligibility,
    )
    return entity_from_applicant_label(applicant)


def _replace_note_line(notes: str, label: str, value: str) -> str:
    pattern = rf"(?m)^{re.escape(label)}:\s*.*$"
    line = f"{label}: {value}"
    if re.search(pattern, notes):
        return re.sub(pattern, line, notes, count=1)
    return (notes.rstrip() + "\n" + line).strip() if notes.strip() else line


def refresh_entity_in_notes(notes: str, entity_code: str) -> str:
    """Update Entity + Applicant lines inside NOTES blob."""
    label = applicant_label_from_entity_code(entity_code)
    out = _replace_note_line(notes or "", "Applicant", label)
    out = _replace_note_line(out, "Entity", entity_code)
    return out


def refresh_amount_in_notes(notes: str, amount_line: str) -> str:
    """Insert or replace Amount: line in NOTES."""
    if not amount_line:
        return notes or ""
    return _replace_note_line(notes or "", "Amount", amount_line.replace("Amount: ", "", 1))


def backfill_grant_amounts(airtable, dry_run: bool = False, limit: Optional[int] = None) -> Dict[str, int]:
    """
    Fetch award amounts for live Grants.gov rows and sync Amount in NOTES.
    """
    from grant_amount_fetcher import fetch_grant_amounts

    stats = {"updated": 0, "skipped": 0, "errors": 0, "no_data": 0}
    records = airtable.get_all_records("GRANT OPPORTUNITIES")
    processed = 0
    for row in records:
        if limit is not None and processed >= limit:
            break
        fields = row.get("fields", {})
        url = (fields.get("GRANT URL") or "").lower()
        if "grants.gov/search-results-detail" not in url:
            stats["skipped"] += 1
            continue
        processed += 1
        title = grant_name_from_fields(fields)
        grant_id = grant_id_from_fields(fields)
        notes = fields.get("NOTES") or ""
        opp_num = note_value(fields, "Opportunity Number")
        existing_amount = note_value(fields, "Amount")
        if existing_amount and (
            "Program pool:" in existing_amount
            or "/award" in existing_amount
            or re.search(r"~\d+ awards", existing_amount)
        ):
            stats["skipped"] += 1
            continue
        try:
            info = fetch_grant_amounts(
                grant_id=grant_id,
                title=title,
                opportunity_number=opp_num,
            )
        except Exception:
            stats["errors"] += 1
            continue
        if not info or not info.display_line():
            stats["no_data"] += 1
            continue
        new_notes = refresh_amount_in_notes(notes, info.display_line())
        if opp_num != info.opportunity_number and info.opportunity_number:
            new_notes = _replace_note_line(new_notes, "Opportunity Number", info.opportunity_number)
        if new_notes.strip() == notes.strip():
            stats["skipped"] += 1
            continue
        if dry_run:
            stats["updated"] += 1
            continue
        try:
            airtable.update_record("GRANT OPPORTUNITIES", row["id"], {"NOTES": new_notes})
            stats["updated"] += 1
        except Exception:
            stats["errors"] += 1
    return stats


def backfill_live_grant_entities(airtable, dry_run: bool = False) -> Dict[str, int]:
    """
    Re-classify live Grants.gov rows and sync Entity/Applicant in NOTES.
    Returns counts: updated, skipped, errors.
    """
    stats = {"updated": 0, "skipped": 0, "errors": 0}
    records = airtable.get_all_records("GRANT OPPORTUNITIES")
    for row in records:
        fields = row.get("fields", {})
        url = (fields.get("GRANT URL") or "").lower()
        if "grants.gov/search-results-detail" not in url:
            stats["skipped"] += 1
            continue
        title = grant_name_from_fields(fields)
        funder = fields.get("FUNDER ORGANIZATION") or ""
        eligibility = fields.get("ELIGIBILITY") or ""
        notes = fields.get("NOTES") or ""
        stored = entity_from_fields(fields)
        new_code = classify_grant_entity(
            title=title,
            funder=funder,
            eligibility=eligibility,
            notes=notes,
        )
        if stored == new_code:
            stats["skipped"] += 1
            continue
        new_notes = refresh_entity_in_notes(notes, new_code)
        if dry_run:
            stats["updated"] += 1
            continue
        try:
            airtable.update_record(
                "GRANT OPPORTUNITIES",
                row["id"],
                {"NOTES": new_notes},
            )
            stats["updated"] += 1
        except Exception:
            stats["errors"] += 1
    return stats
