#!/usr/bin/env python3
"""
PRISM — SE Michigan Law Firm Mobile Notary Channel
==================================================
Canonical scheduling SOP, coverage schema, service menu/pricing summary, and
law-firm account intake field definitions. Single source of truth for NEXUS UI,
forms, and /prism/intake (channel=law_firm).

Standalone markdown in CLIENT OUTREACH is deprecated; use GET endpoints below.

Live county/agent/capacity data: uploads/prism/law_firm_coverage.json (editable without deploy).
"""

import json
import os
from typing import Optional, Tuple

from flask import Blueprint, jsonify

prism_law_firm_channel = Blueprint("prism_law_firm_channel", __name__)

_DATA_DIR = os.path.join(os.path.dirname(__file__), "uploads", "prism")
LAW_FIRM_COVERAGE_FILE = os.path.join(_DATA_DIR, "law_firm_coverage.json")

LAW_FIRM_CHANNEL_VERSION = "1.1.0"
PRICING_SOURCE_OF_TRUTH = "DDI_PROFESSIONAL_SERVICES_PRICING.md"
NOTARY_COMPLIANCE_REF = "COMPLIANCE_KNOWLEDGE/NOTARY_REFERENCE.md"

# --- Service menu: practice vertical → PRISM service lines (§3 / §4 / §7 / §6) ---
PRACTICE_VERTICALS = [
    {
        "id": "structured_settlement",
        "label": "Structured settlement / PI",
        "typical_needs": "Release packages, annuity paperwork, affidavits; injured client at home/hospital",
        "service_lines": ["§3 mobile", "facility surcharge if applicable", "RON if doc + state rules allow"],
        "price_indication": "Mobile $75–150 + $10/act + travel; +$75 hospital/jail/facility when applicable",
    },
    {
        "id": "estate_planning",
        "label": "Estate planning",
        "typical_needs": "Wills, trusts, POA, healthcare directives; elderly signers at residence",
        "service_lines": ["§4 CNTDA preferred for trust/estate packages"],
        "price_indication": "Trust package $150–250; POA/AHD $75–125 per set",
    },
    {
        "id": "real_estate_law",
        "label": "Real estate law",
        "typical_needs": "Deeds, seller/buyer packages, commercial closings",
        "service_lines": ["§7 signing agent for closing-style; simple deeds may be §3 + mobile"],
        "price_indication": "Loan signing $125–250; general doc signing $75–125",
    },
    {
        "id": "elder_law",
        "label": "Elder law",
        "typical_needs": "Guardianship, conservatorship, Medicaid planning; vulnerable signers",
        "service_lines": ["§4 + mobile", "witness add-on if needed"],
        "price_indication": "CNTDA bands + $50/witness if offered + travel",
    },
    {
        "id": "corporate_law",
        "label": "Corporate / business",
        "typical_needs": "Resolutions, formations, commercial RE",
        "service_lines": ["§3 mobile or RON (ZigSig)"],
        "price_indication": "Mobile band + per act; RON $25/session or platform quote",
    },
]

CORE_PRICE_ROWS = [
    {"item": "Notarial act (in-person §3)", "amount": "Up to $10 per act", "notes": "Michigan statutory max per completed act"},
    {"item": "Mobile notary (client location)", "amount": "$75–150 + per-act fees", "notes": "Convenience/travel band per price book"},
    {"item": "RON session", "amount": "$25/session or quoted", "notes": "ZigSig; KBA per platform"},
    {"item": "Witness", "amount": "$50", "notes": "Per witness, per signing (where offered)"},
    {"item": "Weekend surcharge", "amount": "+$50", "notes": "On top of base + travel"},
    {"item": "After-hours surcharge", "amount": "+$75", "notes": "On top of base + travel"},
    {"item": "Hospital/jail/facility", "amount": "+$75", "notes": "Specialized location"},
    {"item": "CNTDA trust/estate package", "amount": "$150–250", "notes": "Package pricing"},
    {"item": "Loan/RE signing agent §7", "amount": "$125–250 typical", "notes": "Complexity-driven"},
    {"item": "Court filing/runner local §6", "amount": "$50+ + fees", "notes": "Separate service line"},
]

TRAVEL_ZONES_TROY_HQ = [
    {"zone": 1, "miles": "0–15", "fee_usd": 25},
    {"zone": 2, "miles": "15–30", "fee_usd": 50},
    {"zone": 3, "miles": "30–50", "fee_usd": 75},
    {"zone": 4, "miles": "50+", "fee_usd": "100+"},
]

SCHEDULING_SOP = {
    "title": "Mobile Notary — Scheduling SOP (Law Firms / SE Michigan)",
    "intake_channels": [
        {"channel": "phone", "value": "248.376.4550", "use": "Same-day and complex packages"},
        {"channel": "email", "value": "info@deedavis.biz", "use": "Document count, location, deadline"},
        {"channel": "prism_intake", "value": "POST /prism/intake with channel law_firm", "use": "Repeat firms / portal"},
    ],
    "minimum_info_before_scheduling": [
        "Firm name",
        "Contact phone",
        "Service address",
        "Date/time window",
        "Document type (§3 vs §7 vs §4)",
        "Number of signers",
        "Witness needs",
        "Sensitivity (hospital/elder)",
    ],
    "ddi_initiated_scheduling_windows_et": "Default offer 12:00 PM – 6:00 PM ET weekdays (do not propose morning slots first)",
    "morning_if_firm_requests": "If firm or client names a morning time, may accept — document in booking notes",
    "after_hours_weekend": "Allowed with surcharges per price book; confirm in writing before dispatch",
    "confirmation_steps": [
        "Quote — total or NTE (mobile + acts + travel + surcharges)",
        "Confirm — email/text: date, time, address, on-site contact, parking, witnesses",
        "Calendar hold — internal + optional firm confirmation",
        "Optional day-before ping for high-value or facility jobs",
    ],
    "cutoffs": [
        {"request_type": "Standard mobile", "lead_time": "24+ hours preferred", "notes": ""},
        {"request_type": "Same-day", "lead_time": "4+ hours where possible", "notes": "Emergency/rush if <2h per price book"},
        {"request_type": "Hospital/SNF", "lead_time": "Extra buffer", "notes": "Confirm visitor policy with firm"},
    ],
    "cancellation_policy_draft": [
        "Firm cancels ≥24h: no fee (recommended) — lock in firm agreement",
        "Firm cancels <24h: optional flat fee or % of quoted mobile",
        "DDI cancels: reschedule priority or refund prepaid deposit",
    ],
    "execution_day": [
        "MiLONA + UPL boundaries — no legal advice",
        "CNTDA packages per training",
        "Log actual notarial acts for invoice",
    ],
    "post_appointment": ["Invoice 24–48h", "Net 15/30 monthly rollup if agreed", "Analytics by practice area"],
    "escalation": [
        "Signer capacity/ID issues — stop; attorney decides",
        "Document defects — do not notarize until corrected; notify firm same day",
    ],
    "compliance_cross_check": NOTARY_COMPLIANCE_REF,
}

COVERAGE_TEMPLATE = {
    "title": "Coverage & Availability (internal — fill via PRISM clients/agents or CRM)",
    "hq": {
        "dispatch_address": "755 W. Big Beaver Rd., Suite 2020, Troy, MI 48084",
        "scheduling_phone": "248.376.4550",
        "email": "info@deedavis.biz",
    },
    "county_rows_template": [
        "Oakland",
        "Wayne",
        "Macomb",
        "Washtenaw",
        "Livingston",
        "Genesee",
        "St. Clair",
        "Monroe",
    ],
    "per_county_fields": ["zone_1_to_4", "typical_travel_fee_usd", "covered_yes_no", "notes"],
    "agent_roster_fields": [
        "name_role",
        "mi_commission_numbers",
        "cntda_npr_signing_agent_flags",
        "typical_territory",
        "max_appointments_per_week",
    ],
    "capacity_fields": ["same_day_typical_per_day", "same_day_hard_max_per_day"],
    "platforms": [
        {"name": "Snapdocs", "purpose": "Title/signing overflow"},
        {"name": "ZigSig", "purpose": "RON"},
    ],
    "review_cadence": ["Monthly: roster and counties", "Before campaigns: verify stale data"],
}


def _default_live_coverage() -> dict:
    """Skeleton when JSON is missing or counties absent."""
    return {
        "updated_at": None,
        "hq_overrides": {},
        "counties": [
            {
                "name": n,
                "zone": None,
                "typical_travel_fee_usd": None,
                "covered": None,
                "notes": "",
            }
            for n in COVERAGE_TEMPLATE["county_rows_template"]
        ],
        "agents": [],
        "capacity": {"same_day_typical_per_day": None, "same_day_hard_max_per_day": None},
        "platforms": {"snapdocs": None, "zigsig": None},
        "out_of_zone_policy": None,
        "public_pitch_lines": [],
    }


def _load_law_firm_coverage_live() -> Tuple[dict, bool, Optional[str]]:
    """
    Returns (live_dict, file_exists, parse_error_or_none).
    Invalid JSON returns defaults + error string for API visibility.
    """
    os.makedirs(_DATA_DIR, exist_ok=True)
    if not os.path.isfile(LAW_FIRM_COVERAGE_FILE):
        return _default_live_coverage(), False, None
    try:
        with open(LAW_FIRM_COVERAGE_FILE, encoding="utf-8") as f:
            raw = json.load(f)
    except OSError as e:
        return _default_live_coverage(), True, f"read_error: {e}"
    except json.JSONDecodeError as e:
        return _default_live_coverage(), True, f"json_error: {e}"

    if not isinstance(raw, dict):
        return _default_live_coverage(), True, "json_error: root must be an object"

    base = _default_live_coverage()
    # Merge known keys; file wins
    for k in (
        "updated_at",
        "hq_overrides",
        "counties",
        "agents",
        "capacity",
        "platforms",
        "out_of_zone_policy",
        "public_pitch_lines",
    ):
        if k in raw and raw[k] is not None:
            base[k] = raw[k]
    return base, True, None


def build_coverage_api_payload() -> dict:
    """Field schema + live data + merged HQ for GET /coverage and playbook."""
    live, exists, err = _load_law_firm_coverage_live()
    hq = dict(COVERAGE_TEMPLATE["hq"])
    overrides = live.get("hq_overrides") or {}
    if isinstance(overrides, dict):
        hq.update({k: v for k, v in overrides.items() if v is not None})

    payload = {
        "field_schema": COVERAGE_TEMPLATE,
        "live": live,
        "hq_effective": hq,
        "data_file": "uploads/prism/law_firm_coverage.json",
        "data_file_absolute": os.path.abspath(LAW_FIRM_COVERAGE_FILE),
        "file_exists": exists,
    }
    if err:
        payload["load_warning"] = err
    return payload


# JSON-field schema for forms + POST /prism/intake — nested under details.law_firm_account
LAW_FIRM_INTAKE_SCHEMA = {
    "version": LAW_FIRM_CHANNEL_VERSION,
    "channel_key": "law_firm",
    "service_key_for_intake": "notary-law-firm",
    "sections": [
        {
            "id": "firm",
            "title": "Firm information",
            "fields": [
                {"key": "law_firm_legal_name", "type": "string", "required": True},
                {"key": "law_firm_address", "type": "string", "label": "Primary office address"},
                {"key": "law_firm_billing_address", "type": "string", "label": "Billing address if different"},
                {"key": "law_firm_main_phone", "type": "string"},
                {"key": "law_firm_ap_email", "type": "string", "label": "Accounts payable email"},
            ],
        },
        {
            "id": "contacts",
            "title": "Contacts",
            "fields": [
                {"key": "contact_scheduling_name", "type": "string"},
                {"key": "contact_scheduling_title", "type": "string"},
                {"key": "contact_scheduling_phone", "type": "string"},
                {"key": "contact_scheduling_email", "type": "string"},
                {"key": "contact_attorney_name", "type": "string", "required": False},
                {"key": "contact_ap_name", "type": "string"},
                {"key": "contact_ap_email", "type": "string"},
            ],
        },
        {
            "id": "practice",
            "title": "Practice areas",
            "fields": [
                {
                    "key": "practice_areas",
                    "type": "multiselect",
                    "options": [
                        "structured_settlement_pi",
                        "estate_planning",
                        "real_estate",
                        "elder_law",
                        "corporate_business",
                        "other",
                    ],
                },
                {"key": "practice_areas_other", "type": "string"},
            ],
        },
        {
            "id": "service_needs",
            "title": "Service needs",
            "fields": [
                {"key": "typical_document_types", "type": "text"},
                {"key": "estimated_signings_per_month", "type": "enum", "options": ["1-2", "3-10", "10+"]},
                {"key": "usual_locations", "type": "string"},
                {"key": "witnesses_frequency", "type": "enum", "options": ["often", "sometimes", "rare_client_brings"]},
                {"key": "ron_acceptable", "type": "enum", "options": ["yes", "no", "ask_per_file"]},
            ],
        },
        {
            "id": "scheduling_prefs",
            "title": "Scheduling preferences",
            "fields": [
                {"key": "preferred_notice", "type": "string"},
                {"key": "blackout_times", "type": "string"},
                {
                    "key": "after_hours_weekend",
                    "type": "enum",
                    "options": ["rare", "occasional_expect_surcharge"],
                },
            ],
        },
        {
            "id": "billing",
            "title": "Billing",
            "fields": [
                {
                    "key": "payment_preference",
                    "type": "enum",
                    "options": ["card", "check", "ach", "net_15", "net_30"],
                },
                {"key": "po_required", "type": "boolean"},
                {"key": "po_format_notes", "type": "string"},
                {"key": "vendor_packet_status", "type": "enum", "options": ["requested", "sent", "na"]},
            ],
        },
        {
            "id": "compliance",
            "title": "Compliance & sensitivity",
            "fields": [
                {"key": "hipaa_phi_adjacent", "type": "boolean"},
                {"key": "hipaa_notes", "type": "text"},
                {"key": "minors_guardianship", "type": "boolean"},
                {"key": "special_access_jail_facility", "type": "boolean"},
            ],
        },
        {
            "id": "internal_ddi",
            "title": "Internal (DDI only)",
            "fields": [
                {"key": "account_opened_date", "type": "date_string"},
                {"key": "crm_airtable_id", "type": "string"},
                {"key": "fee_tier_notes", "type": "text"},
            ],
        },
    ],
}

QUOTE_RULES = {
    "summary": "Firm may receive a total price per engagement; breakout notarial acts vs travel on request",
    "how_to_read_service_lines": [
        "§3 MiLONA: up to $10 per notarial act + mobile/scheduling as quoted",
        "§4 CNTDA: estate/trust/POA/AHD packages — document-agent pricing",
        "§7: loan/RE closing packages — signing-agent pricing, not §3-only",
        "§6: courier/filing separate when quoted upfront",
    ],
    "law_firm_account_terms_default": [
        "Payment: card, check, Zelle; Net 15/30 for approved accounts",
        "Cancellation: per SCHEDULING_SOP — align written firm agreement",
    ],
    "pre_appointment_requirements": [
        "Valid ID per signer",
        "Document package complete unless attorney authorizes limited execution",
        "Expected number of notarial acts for quote",
        "Witness plan (client-supplied vs DDI)",
    ],
}


def _playbook_bundle():
    return {
        "channel": "se_michigan_law_firm_notary",
        "version": LAW_FIRM_CHANNEL_VERSION,
        "pricing_source_of_truth": PRICING_SOURCE_OF_TRUTH,
        "practice_verticals": PRACTICE_VERTICALS,
        "core_price_rows": CORE_PRICE_ROWS,
        "travel_zones_from_troy": TRAVEL_ZONES_TROY_HQ,
        "scheduling_sop": SCHEDULING_SOP,
        "coverage": build_coverage_api_payload(),
        "intake_schema": LAW_FIRM_INTAKE_SCHEMA,
        "quote_rules": QUOTE_RULES,
    }


@prism_law_firm_channel.route("/prism/law-firm-channel", methods=["GET"])
def get_law_firm_channel_playbook():
    """Full SE Michigan law-firm notary playbook (scheduling, coverage schema, menu, intake schema)."""
    return jsonify(_playbook_bundle())


@prism_law_firm_channel.route("/prism/law-firm-channel/scheduling", methods=["GET"])
def get_scheduling_only():
    return jsonify(SCHEDULING_SOP)


@prism_law_firm_channel.route("/prism/law-firm-channel/coverage", methods=["GET"])
def get_coverage_only():
    """Field schema + live counties/agents from uploads/prism/law_firm_coverage.json."""
    return jsonify(build_coverage_api_payload())


@prism_law_firm_channel.route("/prism/law-firm-channel/intake-schema", methods=["GET"])
def get_intake_schema_only():
    return jsonify(LAW_FIRM_INTAKE_SCHEMA)


@prism_law_firm_channel.route("/prism/law-firm-channel/service-menu", methods=["GET"])
def get_service_menu():
    return jsonify(
        {
            "practice_verticals": PRACTICE_VERTICALS,
            "core_price_rows": CORE_PRICE_ROWS,
            "travel_zones": TRAVEL_ZONES_TROY_HQ,
            "quote_rules": QUOTE_RULES,
            "pricing_source_of_truth": PRICING_SOURCE_OF_TRUTH,
        }
    )


def extract_law_firm_account_payload(data: dict) -> dict:
    """
    Pull law-firm account fields from flat intake POST body into a structured dict.
    Used by prism_orders_api when channel=law_firm or service_key=notary-law-firm.
    """
    if not data:
        return {}
    keys = set()
    for sec in LAW_FIRM_INTAKE_SCHEMA.get("sections", []):
        for f in sec.get("fields", []):
            keys.add(f["key"])

    out = {}
    for k in keys:
        if k in data and data[k] is not None:
            out[k] = data[k]
    # Allow nested object from clients
    nested = data.get("law_firm_account")
    if isinstance(nested, dict):
        out.update({k: v for k, v in nested.items() if v is not None})
    return out
