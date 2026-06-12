#!/usr/bin/env python3
"""
nexus_qc_engine.py — System-wide Quality Control spine

Nine universal pillars across GPSS / PRISM / VERTEX / COMPASS.
Shared QC record per unit of service; VERTEX billing gate reads pillar status.

Storage: nexus_qc_records.json, nexus_qc_contracts.json, nexus_qc_grievances.json
"""

from __future__ import annotations

import json
import logging
import os
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

try:
    from zoneinfo import ZoneInfo
except ImportError:
    from backports.zoneinfo import ZoneInfo  # type: ignore

EASTERN = ZoneInfo("America/Detroit")
logger = logging.getLogger("nexus_qc")

_BASE = os.path.dirname(os.path.abspath(__file__))
RECORDS_FILE = os.path.join(_BASE, "nexus_qc_records.json")
CONTRACTS_FILE = os.path.join(_BASE, "nexus_qc_contracts.json")
GRIEVANCES_FILE = os.path.join(_BASE, "nexus_qc_grievances.json")

PILLAR_STATUS_PASS = "pass"
PILLAR_STATUS_FAIL = "fail"
PILLAR_STATUS_PENDING = "pending"
PILLAR_STATUS_NA = "na"
PILLAR_STATUS_WARN = "warn"

# Pillars that must be PASS (not pending) before VERTEX may invoice
BILLING_BLOCKING_PILLARS = {1, 2, 3, 4, 5}
# Pillar 6 — survey may complete after trip; pending = warn only at billing
BILLING_WARN_PILLARS = {6}
# Pillar 8 — contract registration; pending blocks if strict contract check enabled
BILLING_CONTRACT_PILLARS = {8}


PILLAR_DEFINITIONS: Dict[int, Dict[str, Any]] = {
    1: {
        "id": 1,
        "name": "Authorization & scope",
        "module": "PRISM",
        "description": "Eligibility, prior auth, PO, SOW, trip authorization per plan rules.",
        "pass_criteria": "Member eligible; trip authorized or exempt per contract.",
        "mco_topics": [
            "trip authorization",
            "prior authorization",
            "eligibility verification",
            "medical necessity",
            "service scope",
        ],
    },
    2: {
        "id": 2,
        "name": "Credentialing",
        "module": "PRISM / Sub framework",
        "description": "Drivers, agents, subs — active credentials, background, insurance.",
        "pass_criteria": "Assigned fulfillment party credentialed and not expired.",
        "mco_topics": [
            "driver credentialing",
            "background checks",
            "vehicle registration",
            "provider enrollment",
            "subcontractor compliance",
        ],
    },
    3: {
        "id": 3,
        "name": "Execution standards",
        "module": "PRISM",
        "description": "Lane SOPs, timeliness, OTP, chain of custody, fatal-flaw rules.",
        "pass_criteria": "Service executed per lane SOP with required timestamps.",
        "mco_topics": [
            "on-time performance",
            "OTP",
            "service timeliness",
            "no-show",
            "will-call",
            "standards of service",
        ],
    },
    4: {
        "id": 4,
        "name": "Documentation",
        "module": "PRISM",
        "description": "Immutable record per unit of service — trip, test, scanback, filing.",
        "pass_criteria": "Proof record exists with IDs cross-linked to billing.",
        "mco_topics": [
            "trip documentation",
            "mileage",
            "pickup dropoff proof",
            "chain of custody",
            "scanback",
            "audit trail",
        ],
    },
    5: {
        "id": 5,
        "name": "Inspection / validation",
        "module": "PRISM",
        "description": "AI + human QC — scanbacks, DOT fatal flaws, trip validation.",
        "pass_criteria": "Inspection pass or corrected before release.",
        "mco_topics": [
            "quality inspection",
            "compliance review",
            "fatal flaw",
            "document inspection",
            "validation",
        ],
    },
    6: {
        "id": 6,
        "name": "Client / member experience",
        "module": "PRISM",
        "description": "Surveys, letter grades, grievances, member complaints.",
        "pass_criteria": "Grade captured or grievance logged per SLA; F/D escalated.",
        "mco_topics": [
            "member satisfaction",
            "CAHPS",
            "complaints",
            "grievances",
            "member experience",
            "survey",
            "letter grade",
        ],
    },
    7: {
        "id": 7,
        "name": "Billing integrity",
        "module": "VERTEX",
        "description": "Correct rate, units, payer ID, timely filing, denial scrub.",
        "pass_criteria": "Claim matches contract rate + documented service.",
        "mco_topics": [
            "billing accuracy",
            "claims",
            "rates",
            "HCPCS",
            "invoice",
            "payment",
            "denials",
            "fraud waste abuse",
        ],
    },
    8: {
        "id": 8,
        "name": "Regulatory & contract compliance",
        "module": "COMPASS",
        "description": "Training, plan manuals, HIPAA, FAR/DFAR, OSHA/DOT as applicable.",
        "pass_criteria": "Contract registered; required attestations current.",
        "mco_topics": [
            "HIPAA",
            "policy compliance",
            "training",
            "contract compliance",
            "regulatory",
            "attestation",
        ],
    },
    9: {
        "id": 9,
        "name": "Audit readiness",
        "module": "ALL",
        "description": "Pull any record + crosswalk to invoice in minutes.",
        "pass_criteria": "QC record + artifact links complete for this delivery.",
        "mco_topics": [
            "audit",
            "sample",
            "record retention",
            "quality packet",
            "desk review",
            "on-site audit",
        ],
    },
}


# What MCO / plan auditors typically request → pillar + how DDI delivers
MCO_REQUEST_INDEX: List[Dict[str, Any]] = [
    {
        "request": "Trip authorization / prior auth for sampled trips",
        "pillar": 1,
        "artifact": "QC record pillar 1 evidence + NEMT order prior_auth fields",
        "export": "/nexus/qc/mco/breakdown.html?payer={payer}",
        "sla": "≤ 2 business days",
    },
    {
        "request": "Driver and vehicle credentialing files",
        "pillar": 2,
        "artifact": "PRISM driver registry + sub COI (if brokered)",
        "export": "/nexus/qc/contract/{contract_id}",
        "sla": "≤ 2 business days",
    },
    {
        "request": "On-time performance (OTP) / timeliness report",
        "pillar": 3,
        "artifact": "Trip timestamps in QC record + monthly OTP rollup",
        "export": "/nexus/qc/mco/breakdown.html?payer={payer}",
        "sla": "≤ 5 business days",
    },
    {
        "request": "Trip logs / mileage / pickup-dropoff documentation",
        "pillar": 4,
        "artifact": "Per-trip JSON + HTML audit card",
        "export": "/prism/nemt/satisfaction/trip/{nemt_order_id}.html",
        "sla": "≤ 2 business days",
    },
    {
        "request": "Quality inspection / compliance validation",
        "pillar": 5,
        "artifact": "PRISM inspection result on order (or NEMT auto-validation)",
        "export": "/nexus/qc/record/{qc_id}",
        "sla": "≤ 2 business days",
    },
    {
        "request": "Member satisfaction / complaint / grievance data",
        "pillar": 6,
        "artifact": "Member Trip Grade Report + grievance log",
        "export": "/prism/nemt/satisfaction/mco-packet.html?payer={payer}",
        "sla": "≤ 2 business days",
    },
    {
        "request": "Claims / billing / rate verification",
        "pillar": 7,
        "artifact": "VERTEX invoice + trip crosswalk in QC record",
        "export": "/nexus/qc/record/{qc_id} (vertex_invoice_id)",
        "sla": "≤ 2 business days",
    },
    {
        "request": "HIPAA / policy / training attestations",
        "pillar": 8,
        "artifact": "QC_CONTRACT_PROFILE + COMPLIANCE/ folder",
        "export": "/nexus/qc/contract/{contract_id}",
        "sla": "≤ 5 business days",
    },
    {
        "request": "Full quality audit packet / desk review",
        "pillar": 9,
        "artifact": "MCO QC Master Breakdown (all pillars + trip register)",
        "export": "/nexus/qc/mco/breakdown.html?payer={payer}",
        "sla": "≤ 2 business days",
    },
]


def _now_iso() -> str:
    return datetime.now(EASTERN).isoformat()


def _load_json(path: str, default: Any) -> Any:
    if not os.path.isfile(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as exc:
        logger.warning("Could not load %s: %s", path, exc)
        return default


def _save_json(path: str, data: Any) -> None:
    tmp = f"{path}.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    os.replace(tmp, path)


def _empty_pillars() -> Dict[str, Dict[str, Any]]:
    out: Dict[str, Dict[str, Any]] = {}
    for pid, meta in PILLAR_DEFINITIONS.items():
        out[str(pid)] = {
            "status": PILLAR_STATUS_PENDING,
            "module": meta["module"],
            "evidence": {},
            "notes": "",
            "updated_at": None,
        }
    return out


def _new_qc_id() -> str:
    return f"QC-{datetime.now(EASTERN).strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"


def list_records(
    *,
    payer: Optional[str] = None,
    contract_id: Optional[str] = None,
    service_lane: Optional[str] = None,
    limit: int = 500,
) -> List[Dict[str, Any]]:
    records = _load_json(RECORDS_FILE, [])
    out = records
    if payer:
        pl = payer.strip().lower()
        out = [r for r in out if (r.get("payer") or r.get("buyer_name") or "").lower().find(pl) >= 0]
    if contract_id:
        out = [r for r in out if r.get("contract_id") == contract_id]
    if service_lane:
        out = [r for r in out if r.get("service_lane") == service_lane]
    out.sort(key=lambda r: r.get("updated_at") or "", reverse=True)
    return out[:limit]


def get_record_by_id(qc_id: str) -> Optional[Dict[str, Any]]:
    for rec in _load_json(RECORDS_FILE, []):
        if rec.get("qc_id") == qc_id:
            return rec
    return None


def find_record(
    *,
    nemt_order_id: Optional[str] = None,
    prism_order_id: Optional[str] = None,
    vertex_trip_id: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    records = _load_json(RECORDS_FILE, [])
    for rec in records:
        if nemt_order_id and rec.get("nemt_order_id") == nemt_order_id:
            return rec
        if prism_order_id and rec.get("prism_order_id") == prism_order_id:
            return rec
        if vertex_trip_id and rec.get("vertex_trip_id") == vertex_trip_id:
            return rec
    return None


def upsert_record(
    *,
    service_lane: str,
    delivery_unit_type: str = "trip",
    buyer_name: str = "",
    payer: str = "",
    contract_id: str = "",
    nemt_order_id: Optional[str] = None,
    prism_order_id: Optional[str] = None,
    vertex_trip_id: Optional[str] = None,
    vertex_invoice_id: Optional[str] = None,
    pillar_updates: Optional[Dict[int, Dict[str, Any]]] = None,
    artifacts: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    records = _load_json(RECORDS_FILE, [])
    existing = find_record(
        nemt_order_id=nemt_order_id,
        prism_order_id=prism_order_id,
        vertex_trip_id=vertex_trip_id,
    )
    now = _now_iso()
    if existing:
        rec = existing
    else:
        rec = {
            "qc_id": _new_qc_id(),
            "created_at": now,
            "service_lane": service_lane,
            "delivery_unit_type": delivery_unit_type,
            "buyer_name": buyer_name,
            "payer": payer or buyer_name,
            "contract_id": contract_id,
            "nemt_order_id": nemt_order_id,
            "prism_order_id": prism_order_id,
            "vertex_trip_id": vertex_trip_id,
            "vertex_invoice_id": vertex_invoice_id,
            "pillars": _empty_pillars(),
            "gate_billing": {"status": "open", "checked_at": None, "blocked_by": [], "warnings": []},
            "artifacts": {},
        }
        records.append(rec)

    rec["updated_at"] = now
    if buyer_name:
        rec["buyer_name"] = buyer_name
    if payer:
        rec["payer"] = payer
    if contract_id:
        rec["contract_id"] = contract_id
    if nemt_order_id:
        rec["nemt_order_id"] = nemt_order_id
    if prism_order_id:
        rec["prism_order_id"] = prism_order_id
    if vertex_trip_id:
        rec["vertex_trip_id"] = vertex_trip_id
    if vertex_invoice_id:
        rec["vertex_invoice_id"] = vertex_invoice_id

    if artifacts:
        rec.setdefault("artifacts", {}).update({k: v for k, v in artifacts.items() if v})

    if pillar_updates:
        for pid, patch in pillar_updates.items():
            key = str(pid)
            pillar = rec["pillars"].setdefault(key, _empty_pillars()[key])
            if patch.get("status"):
                pillar["status"] = patch["status"]
            if patch.get("evidence") is not None:
                pillar["evidence"] = {**pillar.get("evidence", {}), **patch["evidence"]}
            if patch.get("notes") is not None:
                pillar["notes"] = patch["notes"]
            pillar["updated_at"] = now

    _recompute_audit_pillar(rec)
    gate = evaluate_billing_gate(rec)
    rec["gate_billing"] = gate

    if existing:
        idx = next(i for i, r in enumerate(records) if r["qc_id"] == rec["qc_id"])
        records[idx] = rec
    _save_json(RECORDS_FILE, records)
    return rec


def update_pillar(
    qc_id: str,
    pillar_id: int,
    *,
    status: str,
    evidence: Optional[Dict[str, Any]] = None,
    notes: str = "",
) -> Optional[Dict[str, Any]]:
    rec = get_record_by_id(qc_id)
    if not rec:
        return None
    records = _load_json(RECORDS_FILE, [])
    key = str(pillar_id)
    now = _now_iso()
    pillar = rec["pillars"].setdefault(key, _empty_pillars()[key])
    pillar["status"] = status
    if evidence:
        pillar["evidence"] = {**pillar.get("evidence", {}), **evidence}
    if notes:
        pillar["notes"] = notes
    pillar["updated_at"] = now
    rec["updated_at"] = now
    _recompute_audit_pillar(rec)
    rec["gate_billing"] = evaluate_billing_gate(rec)
    idx = next(i for i, r in enumerate(records) if r["qc_id"] == qc_id)
    records[idx] = rec
    _save_json(RECORDS_FILE, records)
    return rec


def _recompute_audit_pillar(rec: Dict[str, Any]) -> None:
    """Pillar 9 = audit readiness derived from other pillars + artifacts."""
    pillars = rec.get("pillars", {})
    required = ["1", "2", "3", "4", "5"]
    all_pass = all(pillars.get(k, {}).get("status") == PILLAR_STATUS_PASS for k in required)
    has_links = bool(rec.get("nemt_order_id") or rec.get("prism_order_id"))
    arts = rec.get("artifacts") or {}
    p9 = pillars.setdefault("9", _empty_pillars()["9"])
    if all_pass and has_links:
        p9["status"] = PILLAR_STATUS_PASS
        p9["evidence"] = {
            "qc_id": rec.get("qc_id"),
            "artifact_keys": list(arts.keys()),
        }
    elif any(pillars.get(k, {}).get("status") == PILLAR_STATUS_FAIL for k in required):
        p9["status"] = PILLAR_STATUS_FAIL
    else:
        p9["status"] = PILLAR_STATUS_PENDING
    p9["updated_at"] = _now_iso()


def evaluate_billing_gate(rec: Dict[str, Any]) -> Dict[str, Any]:
    pillars = rec.get("pillars", {})
    blocked: List[int] = []
    warnings: List[int] = []

    for pid in BILLING_BLOCKING_PILLARS:
        st = pillars.get(str(pid), {}).get("status", PILLAR_STATUS_PENDING)
        if st == PILLAR_STATUS_FAIL:
            blocked.append(pid)
        elif st == PILLAR_STATUS_PENDING:
            blocked.append(pid)

    for pid in BILLING_WARN_PILLARS:
        st = pillars.get(str(pid), {}).get("status", PILLAR_STATUS_PENDING)
        if st in (PILLAR_STATUS_FAIL, PILLAR_STATUS_PENDING):
            warnings.append(pid)

    contract = get_contract(rec.get("contract_id") or "")
    p8 = pillars.get("8", {})
    if rec.get("contract_id") and not contract:
        if p8.get("status") != PILLAR_STATUS_PASS:
            blocked.append(8)
    elif contract:
        if p8.get("status") != PILLAR_STATUS_PASS:
            p8["status"] = PILLAR_STATUS_PASS
            p8["updated_at"] = _now_iso()

    allowed = len(blocked) == 0
    return {
        "status": "released" if allowed else "held",
        "allowed": allowed,
        "checked_at": _now_iso(),
        "blocked_by": blocked,
        "warnings": warnings,
    }


def assert_vertex_billing_gate(
    *,
    nemt_order_id: Optional[str] = None,
    prism_order_id: Optional[str] = None,
    vertex_trip_id: Optional[str] = None,
    force: bool = False,
    override_reason: str = "",
) -> Dict[str, Any]:
    """
    VERTEX billing gate — raise ValueError if blocked.
    force=True logs override (Dee only — API should require auth in production).
    """
    rec = find_record(
        nemt_order_id=nemt_order_id,
        prism_order_id=prism_order_id,
        vertex_trip_id=vertex_trip_id,
    )
    if not rec:
        return {
            "allowed": True,
            "skipped": True,
            "reason": "No QC record — gate not enforced (legacy trip)",
        }

    gate = evaluate_billing_gate(rec)
    rec["gate_billing"] = gate
    if force and not gate["allowed"]:
        gate = {
            **gate,
            "allowed": True,
            "status": "released_override",
            "override_reason": override_reason or "Manual override",
            "override_at": _now_iso(),
        }
        rec["gate_billing"] = gate
        records = _load_json(RECORDS_FILE, [])
        idx = next(i for i, r in enumerate(records) if r["qc_id"] == rec["qc_id"])
        records[idx] = rec
        _save_json(RECORDS_FILE, records)
        logger.warning("QC billing gate OVERRIDE qc_id=%s reason=%s", rec["qc_id"], override_reason)
        return gate

    if not gate["allowed"]:
        blocked_names = [PILLAR_DEFINITIONS[p]["name"] for p in gate.get("blocked_by", [])]
        raise ValueError(
            f"VERTEX billing blocked by QC gate — pillars: {gate.get('blocked_by')} "
            f"({', '.join(blocked_names)})"
        )
    return gate


def sync_nemt_trip_from_order(order: Dict[str, Any]) -> Dict[str, Any]:
    """Build/update QC record from completed NEMT order dict."""
    oid = order.get("order_id") or order.get("id")
    contract_id = order.get("contract_id") or order.get("qc_contract_id") or ""
    payer = order.get("payer") or order.get("buyer_name") or ""

    # Pillar 1 — authorization
    p1_status = PILLAR_STATUS_PASS if order.get("eligibility_verified") or order.get("prior_auth_number") else PILLAR_STATUS_PENDING
    if order.get("prior_auth_id") or order.get("prior_auth_number"):
        p1_status = PILLAR_STATUS_PASS

    # Pillar 2 — credentialing
    p2_status = PILLAR_STATUS_PASS if order.get("driver_name") else PILLAR_STATUS_PENDING

    # Pillar 3 — execution
    p3_status = PILLAR_STATUS_PASS if order.get("status") == "completed" and order.get("completed_at") else PILLAR_STATUS_PENDING

    # Pillar 4 — documentation
    p4_status = PILLAR_STATUS_PASS if order.get("actual_pickup_time") and order.get("actual_dropoff_time") else PILLAR_STATUS_PENDING

    # Pillar 5 — inspection (NEMT: auto-pass when execution + mileage present)
    mileage = order.get("actual_mileage") or order.get("mileage")
    p5_status = PILLAR_STATUS_PASS if p3_status == PILLAR_STATUS_PASS and mileage is not None else PILLAR_STATUS_PENDING

    # Pillar 6 — member experience (survey queued after complete)
    p6_status = PILLAR_STATUS_PENDING

    # Pillar 7 — billing (pending until invoice)
    p7_status = PILLAR_STATUS_PASS if order.get("vertex_invoice_id") else PILLAR_STATUS_PENDING

    # Pillar 8 — contract
    contract = get_contract(contract_id) if contract_id else None
    if not contract_id and payer:
        contract = find_contract_by_payer(payer)
        if contract:
            contract_id = contract.get("contract_id", "")
    p8_status = PILLAR_STATUS_PASS if contract else PILLAR_STATUS_PENDING

    artifacts: Dict[str, str] = {}
    nemt_id = oid
    if nemt_id:
        artifacts["trip_html"] = f"/prism/nemt/satisfaction/trip/{nemt_id}.html"
    if payer:
        artifacts["mco_grade_packet"] = f"/prism/nemt/satisfaction/mco-packet.html?payer={payer}"

    rec = upsert_record(
        service_lane="nemt",
        delivery_unit_type="trip",
        buyer_name=payer,
        payer=payer,
        contract_id=contract_id,
        nemt_order_id=oid,
        prism_order_id=order.get("prism_order_id"),
        vertex_trip_id=order.get("vertex_trip_id"),
        vertex_invoice_id=order.get("vertex_invoice_id"),
        pillar_updates={
            1: {
                "status": p1_status,
                "evidence": {
                    "eligibility_verified": order.get("eligibility_verified"),
                    "prior_auth_number": order.get("prior_auth_number"),
                    "prior_auth_id": order.get("prior_auth_id"),
                },
            },
            2: {
                "status": p2_status,
                "evidence": {
                    "driver_name": order.get("driver_name"),
                    "vehicle_id": order.get("vehicle_id"),
                },
            },
            3: {
                "status": p3_status,
                "evidence": {
                    "completed_at": order.get("completed_at"),
                    "actual_pickup_time": order.get("actual_pickup_time"),
                    "actual_dropoff_time": order.get("actual_dropoff_time"),
                },
            },
            4: {
                "status": p4_status,
                "evidence": {
                    "mileage": mileage,
                    "pickup_address": order.get("pickup_address"),
                    "dropoff_address": order.get("dropoff_address"),
                    "trip_purpose": order.get("trip_purpose"),
                },
            },
            5: {"status": p5_status, "evidence": {"validation": "nemt_auto"}},
            6: {"status": p6_status, "evidence": {"survey": "queued_post_complete"}},
            7: {
                "status": p7_status,
                "evidence": {
                    "vertex_trip_id": order.get("vertex_trip_id"),
                    "vertex_invoice_id": order.get("vertex_invoice_id"),
                    "hcpcs_code": order.get("hcpcs_code"),
                },
            },
            8: {
                "status": p8_status,
                "evidence": {"contract_id": contract_id or None},
            },
        },
        artifacts=artifacts,
    )
    return rec


def sync_member_grade_to_qc(survey_record: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Update pillar 6 when member submits trip grade."""
    rec = find_record(nemt_order_id=survey_record.get("nemt_order_id"))
    if not rec:
        return None
    og = survey_record.get("overall_grade") or ""
    status = PILLAR_STATUS_PASS
    if og in ("F", "D"):
        status = PILLAR_STATUS_WARN
    arts = {
        "member_grade_html": survey_record.get("audit_html_path"),
        "member_grade_json": survey_record.get("audit_archive_path"),
    }
    return update_pillar(
        rec["qc_id"],
        6,
        status=status,
        evidence={
            "overall_grade": og,
            "ddi_grade": survey_record.get("ddi_grade"),
            "driver_grade": survey_record.get("driver_grade"),
            "trip_grade": survey_record.get("trip_grade"),
            "responded_at": survey_record.get("responded_at"),
        },
        notes=f"Member grade {og}" if og else "",
    )


def mark_billing_complete(
    *,
    nemt_order_id: Optional[str] = None,
    vertex_trip_id: Optional[str] = None,
    vertex_invoice_id: str,
    invoice_number: str = "",
) -> Optional[Dict[str, Any]]:
    rec = find_record(nemt_order_id=nemt_order_id, vertex_trip_id=vertex_trip_id)
    if not rec:
        return None
    return update_pillar(
        rec["qc_id"],
        7,
        status=PILLAR_STATUS_PASS,
        evidence={
            "vertex_invoice_id": vertex_invoice_id,
            "invoice_number": invoice_number,
        },
        notes="VERTEX claim generated",
    )


# ─── Contract registry ─────────────────────────────────────────────────────

def list_contracts() -> List[Dict[str, Any]]:
    return _load_json(CONTRACTS_FILE, [])


def get_contract(contract_id: str) -> Optional[Dict[str, Any]]:
    if not contract_id:
        return None
    for c in _load_json(CONTRACTS_FILE, []):
        if c.get("contract_id") == contract_id:
            return c
    return None


def find_contract_by_payer(payer: str) -> Optional[Dict[str, Any]]:
    if not payer:
        return None
    pl = payer.strip().lower()
    for c in _load_json(CONTRACTS_FILE, []):
        for field in ("payer", "buyer_name", "plan_name"):
            val = (c.get(field) or "").lower()
            if pl in val or val in pl:
                return c
    return None


def register_contract(payload: Dict[str, Any]) -> Dict[str, Any]:
    contracts = _load_json(CONTRACTS_FILE, [])
    cid = payload.get("contract_id") or f"CTR-{uuid.uuid4().hex[:8].upper()}"
    now = _now_iso()
    existing = get_contract(cid)
    entry = {
        "contract_id": cid,
        "buyer_name": payload.get("buyer_name", ""),
        "payer": payload.get("payer") or payload.get("buyer_name", ""),
        "plan_name": payload.get("plan_name", ""),
        "service_lanes": payload.get("service_lanes") or ["nemt"],
        "vendor_id": payload.get("vendor_id", ""),
        "pop_start": payload.get("pop_start"),
        "pop_end": payload.get("pop_end"),
        "qc_contact": payload.get("qc_contact", ""),
        "profile_path": payload.get("profile_path", ""),
        "registered_at": existing.get("registered_at") if existing else now,
        "updated_at": now,
    }
    if existing:
        idx = next(i for i, c in enumerate(contracts) if c["contract_id"] == cid)
        contracts[idx] = {**existing, **entry}
    else:
        contracts.append(entry)
    _save_json(CONTRACTS_FILE, contracts)
    return entry


def ensure_hap_contract_seed() -> Dict[str, Any]:
    """Seed HAP CareSource contract if missing (vendor ID from ops docs)."""
    existing = find_contract_by_payer("HAP")
    if existing:
        return existing
    return register_contract({
        "contract_id": "HAP-CARESOURCE-NEMT",
        "buyer_name": "HAP CareSource",
        "payer": "HAP CareSource",
        "plan_name": "HAP CareSource Medicaid",
        "service_lanes": ["nemt"],
        "vendor_id": "100000469269",
        "profile_path": "BIDS:RESOURCES/HAP CARESOURCE NEMT NETWORK/QC_CONTRACT_PROFILE.md",
    })


# ─── Grievances (system-wide stub — all lanes) ─────────────────────────────

def log_grievance(payload: Dict[str, Any]) -> Dict[str, Any]:
    grievances = _load_json(GRIEVANCES_FILE, [])
    gid = payload.get("grievance_id") or f"GRV-{datetime.now(EASTERN).strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
    entry = {
        "grievance_id": gid,
        "created_at": _now_iso(),
        "status": payload.get("status", "open"),
        "source": payload.get("source", "member"),
        "payer": payload.get("payer", ""),
        "contract_id": payload.get("contract_id", ""),
        "nemt_order_id": payload.get("nemt_order_id"),
        "prism_order_id": payload.get("prism_order_id"),
        "description": (payload.get("description") or "")[:2000],
        "severity": payload.get("severity", "standard"),
        "due_response_by": payload.get("due_response_by"),
        "resolution": payload.get("resolution"),
    }
    grievances.append(entry)
    _save_json(GRIEVANCES_FILE, grievances)

    if payload.get("nemt_order_id"):
        rec = find_record(nemt_order_id=payload["nemt_order_id"])
        if rec:
            update_pillar(
                rec["qc_id"],
                6,
                status=PILLAR_STATUS_WARN,
                evidence={"grievance_id": gid},
                notes="Open grievance logged",
            )
    return entry


def list_grievances(
    *,
    payer: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 200,
) -> List[Dict[str, Any]]:
    items = _load_json(GRIEVANCES_FILE, [])
    if payer:
        pl = payer.lower()
        items = [g for g in items if pl in (g.get("payer") or "").lower()]
    if status:
        items = [g for g in items if g.get("status") == status]
    items.sort(key=lambda g: g.get("created_at") or "", reverse=True)
    return items[:limit]


# ─── MCO breakdown aggregates ───────────────────────────────────────────────

def build_mco_breakdown_data(
    *,
    payer: Optional[str] = None,
    contract_id: Optional[str] = None,
) -> Dict[str, Any]:
    ensure_hap_contract_seed()
    records = list_records(payer=payer, contract_id=contract_id)
    contract = get_contract(contract_id) if contract_id else find_contract_by_payer(payer or "")

    pillar_summary: Dict[str, Dict[str, int]] = {}
    for pid in PILLAR_DEFINITIONS:
        pillar_summary[str(pid)] = {"pass": 0, "fail": 0, "pending": 0, "warn": 0, "na": 0}

    for rec in records:
        for key, pillar in rec.get("pillars", {}).items():
            st = pillar.get("status", PILLAR_STATUS_PENDING)
            bucket = pillar_summary.setdefault(key, {"pass": 0, "fail": 0, "pending": 0, "warn": 0, "na": 0})
            if st in bucket:
                bucket[st] += 1

    grievances = list_grievances(payer=payer)
    open_grv = [g for g in grievances if g.get("status") == "open"]

    return {
        "generated_at": _now_iso(),
        "payer": payer or (contract or {}).get("payer"),
        "contract": contract,
        "pillar_definitions": PILLAR_DEFINITIONS,
        "pillar_summary": pillar_summary,
        "mco_request_index": MCO_REQUEST_INDEX,
        "delivery_count": len(records),
        "records": records,
        "grievances_open": len(open_grv),
        "grievances_total": len(grievances),
        "grievances": grievances[:50],
        "exports": {
            "member_trip_grade_packet": f"/prism/nemt/satisfaction/mco-packet.html?payer={payer or ''}",
            "qc_master_breakdown": f"/nexus/qc/mco/breakdown.html?payer={payer or ''}",
            "grievance_log": "/nexus/qc/grievances",
        },
    }


def match_mco_request(query: str) -> List[Dict[str, Any]]:
    """Map free-text MCO audit question to pillars + export paths."""
    q = (query or "").lower()
    hits: List[Dict[str, Any]] = []
    for item in MCO_REQUEST_INDEX:
        score = 0
        for topic in PILLAR_DEFINITIONS.get(item["pillar"], {}).get("mco_topics", []):
            if topic in q or any(word in q for word in topic.split()):
                score += 2
        if item["request"].lower() in q or score > 0:
            hits.append({**item, "match_score": score})
    hits.sort(key=lambda x: x.get("match_score", 0), reverse=True)
    return hits[:10]
