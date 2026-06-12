#!/usr/bin/env python3
"""NEXUS QC API — MCO breakdown, billing gate, grievances, contract registry."""

from __future__ import annotations

import logging

from flask import Blueprint, Response, jsonify, request

from nexus_qc_engine import (
    MCO_REQUEST_INDEX,
    PILLAR_DEFINITIONS,
    assert_vertex_billing_gate,
    build_mco_breakdown_data,
    ensure_hap_contract_seed,
    find_record,
    get_contract,
    get_record_by_id,
    list_contracts,
    list_grievances,
    list_records,
    log_grievance,
    match_mco_request,
    register_contract,
    sync_nemt_trip_from_order,
    update_pillar,
)
from nexus_qc_mco_audit_report import render_mco_breakdown_html

logger = logging.getLogger("nexus_qc_api")

nexus_qc = Blueprint("nexus_qc", __name__)


@nexus_qc.route("/nexus/qc/health", methods=["GET"])
def qc_health():
    ensure_hap_contract_seed()
    records = list_records(limit=1)
    return jsonify({
        "status": "ok",
        "service": "NEXUS QC Engine",
        "pillars": len(PILLAR_DEFINITIONS),
        "records_count": len(list_records(limit=10000)),
        "contracts_count": len(list_contracts()),
        "mco_request_index_entries": len(MCO_REQUEST_INDEX),
        "sample_record": records[0]["qc_id"] if records else None,
    })


@nexus_qc.route("/nexus/qc/pillars", methods=["GET"])
def qc_pillars():
    return jsonify({"pillars": PILLAR_DEFINITIONS, "mco_request_index": MCO_REQUEST_INDEX})


@nexus_qc.route("/nexus/qc/mco/match", methods=["GET", "POST"])
def qc_mco_match():
    q = request.args.get("q") or (request.get_json(silent=True) or {}).get("query", "")
    if not q:
        return jsonify({"error": "Provide query via ?q= or JSON {query}"}), 400
    return jsonify({"query": q, "matches": match_mco_request(q)})


@nexus_qc.route("/nexus/qc/records", methods=["GET"])
def qc_list_records():
    payer = request.args.get("payer")
    contract_id = request.args.get("contract_id")
    lane = request.args.get("service_lane")
    limit = min(int(request.args.get("limit", 200)), 1000)
    return jsonify({
        "records": list_records(payer=payer, contract_id=contract_id, service_lane=lane, limit=limit),
        "total": len(list_records(payer=payer, contract_id=contract_id, service_lane=lane, limit=10000)),
    })


@nexus_qc.route("/nexus/qc/record/<qc_id>", methods=["GET"])
def qc_get_record(qc_id: str):
    rec = get_record_by_id(qc_id)
    if not rec:
        return jsonify({"error": "QC record not found"}), 404
    return jsonify(rec)


@nexus_qc.route("/nexus/qc/record/<qc_id>/pillar/<int:pillar_id>", methods=["PATCH", "POST"])
def qc_update_pillar(qc_id: str, pillar_id: int):
    data = request.get_json(silent=True) or {}
    status = data.get("status")
    if not status:
        return jsonify({"error": "status required"}), 400
    rec = update_pillar(
        qc_id,
        pillar_id,
        status=status,
        evidence=data.get("evidence"),
        notes=data.get("notes", ""),
    )
    if not rec:
        return jsonify({"error": "QC record not found"}), 404
    return jsonify(rec)


@nexus_qc.route("/nexus/qc/gate/check", methods=["POST"])
def qc_gate_check():
    data = request.get_json(silent=True) or {}
    try:
        gate = assert_vertex_billing_gate(
            nemt_order_id=data.get("nemt_order_id"),
            prism_order_id=data.get("prism_order_id"),
            vertex_trip_id=data.get("vertex_trip_id"),
            force=bool(data.get("force")),
            override_reason=data.get("override_reason", ""),
        )
        return jsonify(gate)
    except ValueError as exc:
        return jsonify({"allowed": False, "error": str(exc)}), 403


@nexus_qc.route("/nexus/qc/mco/breakdown", methods=["GET"])
def qc_mco_breakdown_json():
    payer = request.args.get("payer")
    contract_id = request.args.get("contract_id")
    return jsonify(build_mco_breakdown_data(payer=payer, contract_id=contract_id))


@nexus_qc.route("/nexus/qc/mco/breakdown.html", methods=["GET"])
def qc_mco_breakdown_html():
    payer = request.args.get("payer")
    contract_id = request.args.get("contract_id")
    html_body = render_mco_breakdown_html(payer=payer, contract_id=contract_id)
    return Response(html_body, mimetype="text/html; charset=utf-8")


@nexus_qc.route("/nexus/qc/contracts", methods=["GET", "POST"])
def qc_contracts():
    if request.method == "GET":
        return jsonify({"contracts": list_contracts()})
    data = request.get_json(silent=True) or {}
    if not data.get("buyer_name") and not data.get("payer"):
        return jsonify({"error": "buyer_name or payer required"}), 400
    entry = register_contract(data)
    return jsonify(entry), 201


@nexus_qc.route("/nexus/qc/contract/<contract_id>", methods=["GET"])
def qc_contract_detail(contract_id: str):
    c = get_contract(contract_id)
    if not c:
        return jsonify({"error": "Contract not found"}), 404
    recs = list_records(contract_id=contract_id, limit=500)
    return jsonify({"contract": c, "qc_records": recs, "delivery_count": len(recs)})


@nexus_qc.route("/nexus/qc/grievances", methods=["GET", "POST"])
def qc_grievances():
    if request.method == "GET":
        payer = request.args.get("payer")
        status = request.args.get("status")
        return jsonify({"grievances": list_grievances(payer=payer, status=status)})
    data = request.get_json(silent=True) or {}
    if not data.get("description"):
        return jsonify({"error": "description required"}), 400
    return jsonify(log_grievance(data)), 201


@nexus_qc.route("/nexus/qc/sync/nemt", methods=["POST"])
def qc_sync_nemt():
    """Manual sync — normally called from complete_trip."""
    data = request.get_json(silent=True) or {}
    if not data.get("order_id") and not data.get("id"):
        return jsonify({"error": "order payload required"}), 400
    rec = sync_nemt_trip_from_order(data)
    return jsonify(rec)
