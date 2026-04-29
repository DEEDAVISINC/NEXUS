"""
PRISM NEMT Module — Non-Emergency Medical Transportation operations.

This module handles the PRISM-side of NEMT:
  - Trip orders (scheduling, dispatch, driver assignment)
  - Eligibility pre-check before dispatch
  - Prior auth lookup
  - Trip completion → auto-bridge to VERTEX NEMT billing (log_trip)
  - MCO payer directory
  - Revenue dashboard

VERTEX NEMT billing handles: claims, CMS-1500, invoices, ERA payments.

Provider Credentials:
  NPI:              1538939111   (from company_info)
  CHAMPS Provider:  6309049      (from company_info)
"""

from __future__ import annotations

import json
import os
import threading
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from flask import Blueprint, jsonify, request

# ─── NEXUS LEARNING ENGINE INTEGRATION ────────────────────────────────────────
try:
    from nexus_learning_engine import nxlearn
except ImportError:
    def nxlearn(*args, **kwargs):
        pass  # Graceful fallback if learning engine not available

from nemt_billing import (
    MICHIGAN_MCO_PAYERS,
    NEMT_BROKERS,
    PAYER_DEFAULT,
    check_member_eligibility_checklist,
    create_prior_auth,
    generate_claim,
    get_broker_list,
    get_mco_payer_list,
    get_nemt_summary,
    list_prior_auths,
    log_trip,
    update_broker_status,
)

prism_nemt = Blueprint("prism_nemt", __name__)

# ─────────────────────────────────────────────────────────────────────────────
# Local state — NEMT trip orders (distinct from VERTEX billing trips)
# ─────────────────────────────────────────────────────────────────────────────
_lock = threading.Lock()
_DATA: Optional[Dict[str, Any]] = None

TRANSPORT_TYPES = {
    "ambulatory": {
        "label": "Ambulatory (Seated)",
        "hcpcs_base": "T2002",
        "hcpcs_mileage": "T2003",
        "description": "Member can walk and transfer independently or with minimal assistance.",
    },
    "wheelchair": {
        "label": "Wheelchair Van",
        "hcpcs_base": "A0130",
        "hcpcs_mileage": "A0425",
        "description": "Member uses a wheelchair and cannot transfer to a standard seat.",
    },
    "stretcher": {
        "label": "Stretcher / Gurney",
        "hcpcs_base": "A0380",
        "hcpcs_mileage": "A0425",
        "description": "Member must remain supine during transport.",
    },
    "volunteer": {
        "label": "Volunteer Driver (Mileage Only)",
        "hcpcs_base": "T2001",
        "hcpcs_mileage": "T2001",
        "description": "Reimbursement for volunteer or personal vehicle mileage.",
    },
    "bus": {
        "label": "Public Transit / Bus Pass",
        "hcpcs_base": "T2005",
        "hcpcs_mileage": None,
        "description": "Bus ticket or transit pass assistance.",
    },
    "rx_standard": {
        "label": "Prescription Delivery (Standard)",
        "hcpcs_base": "T2002-RX",
        "hcpcs_mileage": "T2003-RX",
        "description": "Pharmacy-to-patient prescription delivery. Non-controlled. ID verification required.",
    },
    "rx_controlled": {
        "label": "Prescription Delivery (Controlled Substance)",
        "hcpcs_base": "S5001",
        "hcpcs_mileage": "T2003-RX",
        "description": "DEA Schedule II-V. Signature required, no leave-at-door. DDI driver only.",
    },
    "rx_cold_chain": {
        "label": "Prescription Delivery (Cold Chain)",
        "hcpcs_base": "S5000",
        "hcpcs_mileage": "T2003-RX",
        "description": "Temperature-sensitive medications (insulin, biologics). Insulated container + temp monitor required.",
    },
}

TRIP_STATUSES = ["scheduled", "dispatched", "in_progress", "completed", "cancelled", "no_show"]

# Fulfillment routing: which platform handles which transport type
# Uber Health = ambulatory (standard UberX)
# Lyft Healthcare = wheelchair (lyft_wav) + ambulatory fallback
# Stretcher = neither — requires a dedicated medical transport subcontractor
FULFILLMENT_ROUTING = {
    "ambulatory":   {"primary": "uber_health",      "fallback": "lyft_healthcare", "platform_type": "lyft"},
    "wheelchair":   {"primary": "lyft_healthcare",  "fallback": None,              "platform_type": "lyft_wav"},
    "stretcher":    {"primary": "subcontractor",    "fallback": None,              "platform_type": None},
    "volunteer":    {"primary": "manual",           "fallback": None,              "platform_type": None},
    "bus":          {"primary": "manual",           "fallback": None,              "platform_type": None},
    "rx_standard":  {"primary": "uber_health",      "fallback": "ddi_driver",      "platform_type": "delivery"},
    "rx_controlled": {"primary": "ddi_driver",       "fallback": None,              "platform_type": None},
    "rx_cold_chain": {"primary": "ddi_driver",       "fallback": None,              "platform_type": None},
}


def _data_file() -> str:
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "prism_nemt_data.json")


def _load_state() -> Dict[str, Any]:
    global _DATA
    with _lock:
        if _DATA is not None:
            return _DATA
        path = _data_file()
        if os.path.isfile(path):
            with open(path, "r", encoding="utf-8") as f:
                _DATA = json.load(f)
        else:
            _DATA = {"orders": {}, "drivers": {}}
        return _DATA


def _save_state(state: Dict[str, Any]) -> None:
    path = _data_file()
    tmp = path + ".tmp"
    with _lock:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2, default=str)
        os.replace(tmp, path)


def _now_iso() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


# ─────────────────────────────────────────────────────────────────────────────
# Core functions
# ─────────────────────────────────────────────────────────────────────────────

def create_nemt_order(
    member_medicaid_id: str,
    member_name: str,
    member_dob: str,
    payer: str,
    transport_type: str,
    pickup_address: str,
    dropoff_address: str,
    pickup_time: str,
    appointment_time: Optional[str] = None,
    trip_purpose: str = "Medical appointment",
    mileage: float = 0.0,
    eligibility_verified: bool = False,
    prior_auth_id: Optional[str] = None,
    prior_auth_number: Optional[str] = None,
    driver_name: Optional[str] = None,
    vehicle_id: Optional[str] = None,
    notes: Optional[str] = None,
) -> Dict[str, Any]:
    transport = TRANSPORT_TYPES.get(transport_type)
    if not transport:
        raise ValueError(
            f"Invalid transport_type '{transport_type}'. Valid: {list(TRANSPORT_TYPES.keys())}"
        )

    order_id = str(uuid.uuid4())
    order = {
        "order_id": order_id,
        "member_medicaid_id": (member_medicaid_id or "").strip(),
        "member_name": (member_name or "").strip(),
        "member_dob": (member_dob or "").strip(),
        "payer": (payer or PAYER_DEFAULT).strip(),
        "transport_type": transport_type,
        "transport_label": transport["label"],
        "hcpcs_code": transport["hcpcs_base"],
        "pickup_address": (pickup_address or "").strip(),
        "dropoff_address": (dropoff_address or "").strip(),
        "pickup_time": pickup_time,
        "appointment_time": appointment_time,
        "trip_purpose": (trip_purpose or "Medical appointment").strip(),
        "mileage": float(mileage) if mileage else 0.0,
        "eligibility_verified": bool(eligibility_verified),
        "prior_auth_id": prior_auth_id or None,
        "prior_auth_number": prior_auth_number or None,
        "driver_name": driver_name or None,
        "vehicle_id": vehicle_id or None,
        "notes": notes or "",
        "status": "scheduled",
        "created_at": _now_iso(),
        "dispatched_at": None,
        "completed_at": None,
        "vertex_trip_id": None,
        "vertex_invoice_id": None,
    }

    # Run eligibility checklist
    checklist = check_member_eligibility_checklist(order)
    order["eligibility_checklist"] = checklist

    state = _load_state()
    state.setdefault("orders", {})[order_id] = order
    _save_state(state)

    # ─── LEARNING ENGINE: Log trip scheduled ──────────────────────────────────
    nxlearn('transport', order_id, 'trip_scheduled', {
        'transport_type': transport_type,
        'region': 'MI',  # All Michigan Medicaid for now
        'mco_id': payer,
        'trip_distance': mileage,
    })

    return order


def dispatch_order(
    order_id: str,
    fulfillment_platform: Optional[str] = None,
    member_phone: Optional[str] = None,
    pickup_lat: Optional[float] = None,
    pickup_lng: Optional[float] = None,
    dropoff_lat: Optional[float] = None,
    dropoff_lng: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Dispatch a NEMT order via Uber Health or Lyft Healthcare.
    Platform is auto-selected based on transport_type unless overridden.

    For ambulatory trips  → Uber Health (UberX)
    For wheelchair trips  → Lyft Healthcare (lyft_wav)
    For stretcher trips   → manual subcontractor (Lyft/Uber cannot fulfill)
    """
    state = _load_state()
    order = state.get("orders", {}).get(order_id)
    if not order:
        raise ValueError(f"NEMT order not found: {order_id}")
    if order["status"] not in ("scheduled",):
        raise ValueError(f"Cannot dispatch order with status '{order['status']}'")

    checklist = order.get("eligibility_checklist") or check_member_eligibility_checklist(order)
    if not checklist.get("eligible_to_dispatch"):
        failed = [c["item"] for c in checklist.get("checks", []) if c["status"] == "FAIL"]
        raise ValueError(f"Member not cleared for dispatch. Failed checks: {', '.join(failed)}")

    transport_type = order.get("transport_type", "ambulatory")
    routing = FULFILLMENT_ROUTING.get(transport_type, {})
    platform = fulfillment_platform or routing.get("primary", "uber_health")

    platform_ride_id = None
    platform_response = None

    # ── Uber Health dispatch ───────────────────────────────────────────────
    if platform == "uber_health":
        if pickup_lat and pickup_lng and dropoff_lat and dropoff_lng:
            try:
                from prism_uber_health import get_uber_health_client
                uber = get_uber_health_client()
                if uber.is_configured():
                    body = {
                        "pickup": {"latitude": pickup_lat, "longitude": pickup_lng},
                        "dropoff": {"latitude": dropoff_lat, "longitude": dropoff_lng},
                    }
                    status_code, resp = uber.create_trip_estimate(body)
                    platform_response = {"platform": "uber_health", "status": status_code, "response": resp}
            except Exception as exc:
                platform_response = {"platform": "uber_health", "error": str(exc)}
        else:
            platform_response = {
                "platform": "uber_health",
                "note": "Coordinates not provided — log into Uber Health dashboard to dispatch manually.",
                "dashboard": "https://health.uber.com",
            }

    # ── Lyft Healthcare dispatch ───────────────────────────────────────────
    elif platform == "lyft_healthcare":
        if pickup_lat and pickup_lng and dropoff_lat and dropoff_lng and member_phone:
            try:
                from prism_lyft_healthcare import get_lyft_healthcare_client, get_lyft_ride_type_for_nemt
                lyft = get_lyft_healthcare_client()
                if lyft.is_configured():
                    ride_type = get_lyft_ride_type_for_nemt(transport_type) or "lyft"
                    status_code, resp = lyft.request_ride(
                        ride_type=ride_type,
                        origin_lat=pickup_lat,
                        origin_lng=pickup_lng,
                        destination_lat=dropoff_lat,
                        destination_lng=dropoff_lng,
                        origin_address=order["pickup_address"],
                        destination_address=order["dropoff_address"],
                        passenger_name=order.get("member_name", "Member"),
                        passenger_phone=member_phone,
                        scheduled_at=order.get("pickup_time"),
                        notes=order.get("trip_purpose"),
                    )
                    platform_response = {"platform": "lyft_healthcare", "status": status_code, "response": resp}
                    if status_code in (200, 201):
                        platform_ride_id = resp.get("id") or resp.get("ride_id")
            except Exception as exc:
                platform_response = {"platform": "lyft_healthcare", "error": str(exc)}
        else:
            platform_response = {
                "platform": "lyft_healthcare",
                "note": "Coordinates and member phone needed to book via API — or use Lyft Concierge dashboard.",
                "dashboard": "https://concierge.lyft.com",
            }

    # ── Stretcher / manual ────────────────────────────────────────────────
    else:
        platform_response = {
            "platform": platform,
            "note": f"Transport type '{transport_type}' cannot be fulfilled by Uber Health or Lyft Healthcare. Assign a medical transport subcontractor manually.",
        }

    order["status"] = "dispatched"
    order["dispatched_at"] = _now_iso()
    order["fulfillment_platform"] = platform
    order["platform_ride_id"] = platform_ride_id
    order["platform_response"] = platform_response
    state["orders"][order_id] = order
    _save_state(state)

    # ─── LEARNING ENGINE: Log driver assigned ─────────────────────────────────
    nxlearn('transport', order_id, 'driver_assigned', {
        'transport_type': transport_type,
        'fulfillment_partner': platform,
        'mco_id': order.get('payer'),
        'region': 'MI',
    })

    return {"order": order, "dispatch": platform_response}


def complete_trip(
    airtable,
    order_id: str,
    actual_pickup_time: str,
    actual_dropoff_time: str,
    actual_mileage: float,
    auto_generate_claim: bool = False,
) -> Dict[str, Any]:
    """
    Mark trip complete and bridge to VERTEX billing via log_trip.
    If auto_generate_claim=True, immediately creates the VERTEX invoice.
    """
    state = _load_state()
    order = state.get("orders", {}).get(order_id)
    if not order:
        raise ValueError(f"NEMT order not found: {order_id}")
    if order["status"] not in ("dispatched", "in_progress"):
        raise ValueError(f"Cannot complete order with status '{order['status']}'")

    order["status"] = "completed"
    order["completed_at"] = _now_iso()
    order["actual_pickup_time"] = actual_pickup_time
    order["actual_dropoff_time"] = actual_dropoff_time
    order["actual_mileage"] = float(actual_mileage) if actual_mileage else order.get("mileage", 0.0)

    # ── Bridge to VERTEX billing ────────────────────────────────────────────
    vertex_trip = log_trip(
        airtable=airtable,
        member_medicaid_id=order["member_medicaid_id"],
        pickup_time=actual_pickup_time,
        dropoff_time=actual_dropoff_time,
        pickup_address=order["pickup_address"],
        dropoff_address=order["dropoff_address"],
        mileage=order["actual_mileage"],
        trip_purpose=order["trip_purpose"],
        hcpcs_code=order["hcpcs_code"],
        payer=order["payer"],
        member_name=order.get("member_name"),
        member_dob=order.get("member_dob"),
        eligibility_verified=order.get("eligibility_verified", False),
        prior_auth_id=order.get("prior_auth_id"),
        prior_auth_number=order.get("prior_auth_number"),
        driver_name=order.get("driver_name"),
        vehicle_id=order.get("vehicle_id"),
        prism_order_id=order_id,
    )
    order["vertex_trip_id"] = vertex_trip["trip_id"]

    claim_result = None
    if auto_generate_claim:
        try:
            claim_result = generate_claim(airtable, vertex_trip["trip_id"])
            order["vertex_invoice_id"] = claim_result.get("invoice", {}).get("id")
        except Exception as exc:
            claim_result = {"error": str(exc)}

    state["orders"][order_id] = order
    _save_state(state)

    # ─── LEARNING ENGINE: Log trip completed ──────────────────────────────────
    nxlearn('transport', order_id, 'trip_completed', {
        'transport_type': order.get('transport_type'),
        'trip_distance': order.get('actual_mileage', 0),
        'fulfillment_partner': order.get('fulfillment_platform'),
        'mco_id': order.get('payer'),
        'region': 'MI',
    })

    return {
        "order": order,
        "vertex_trip": vertex_trip,
        "claim": claim_result,
    }


def register_driver(
    name: str,
    license_number: str,
    phone: str,
    vehicle_year: int,
    vehicle_make: str,
    vehicle_model: str,
    vehicle_vin: str,
    vehicle_plate: str,
    wheelchair_equipped: bool = False,
    stretcher_equipped: bool = False,
    contractor_type: str = "1099",
    background_check_date: Optional[str] = None,
    background_check_cleared: bool = False,
    hipaa_trained: bool = False,
    mvr_clear: bool = False,
    insurance_verified: bool = False,
    service_counties: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Register a 1099 contractor driver. DDI does not own the vehicle —
    driver provides their own vehicle and operates under DDI's DOT authority.
    """
    driver_id = str(uuid.uuid4())
    # Derive a vehicle_id from plate for backward compat
    vehicle_id = f"VEH-{(vehicle_plate or 'UNKNOWN').upper().replace(' ', '')}"
    driver = {
        "driver_id": driver_id,
        "name": name,
        "license_number": license_number,
        "phone": phone,
        "contractor_type": contractor_type,
        "vehicle": {
            "vehicle_id": vehicle_id,
            "year": vehicle_year,
            "make": vehicle_make,
            "model": vehicle_model,
            "vin": vehicle_vin,
            "plate": vehicle_plate,
            "owner": "driver_owned",
        },
        "wheelchair_equipped": bool(wheelchair_equipped),
        "stretcher_equipped": bool(stretcher_equipped),
        "service_counties": service_counties or ["Wayne", "Oakland", "Macomb"],
        "compliance": {
            "background_check_date": background_check_date,
            "background_check_cleared": bool(background_check_cleared),
            "hipaa_trained": bool(hipaa_trained),
            "mvr_clear": bool(mvr_clear),
            "insurance_verified": bool(insurance_verified),
        },
        "clearance_status": _driver_clearance_status(
            background_check_cleared, hipaa_trained, mvr_clear, insurance_verified
        ),
        "status": "active",
        "created_at": _now_iso(),
        "trips_completed": 0,
    }
    state = _load_state()
    state.setdefault("drivers", {})[driver_id] = driver
    _save_state(state)
    return driver


def _driver_clearance_status(bg: bool, hipaa: bool, mvr: bool, ins: bool) -> str:
    """CLEARED = all 4 compliance items done. PENDING = at least one missing."""
    if bg and hipaa and mvr and ins:
        return "CLEARED"
    missing = []
    if not bg:
        missing.append("background_check")
    if not hipaa:
        missing.append("hipaa_training")
    if not mvr:
        missing.append("mvr")
    if not ins:
        missing.append("insurance")
    return f"PENDING — missing: {', '.join(missing)}"


def get_dashboard() -> Dict[str, Any]:
    state = _load_state()
    orders = list(state.get("orders", {}).values())
    by_status: Dict[str, int] = {}
    for o in orders:
        s = o.get("status", "unknown")
        by_status[s] = by_status.get(s, 0) + 1

    pending_billing = [
        {
            "order_id": o["order_id"],
            "member_name": o.get("member_name"),
            "payer": o.get("payer"),
            "completed_at": o.get("completed_at"),
        }
        for o in orders
        if o.get("status") == "completed" and not o.get("vertex_invoice_id")
    ]

    drivers = list(state.get("drivers", {}).values())
    cleared_drivers = [d for d in drivers if d.get("clearance_status") == "CLEARED"]
    wheelchair_drivers = [d for d in cleared_drivers if d.get("wheelchair_equipped")]

    return {
        "total_orders": len(orders),
        "by_status": by_status,
        "pending_billing_count": len(pending_billing),
        "pending_billing": pending_billing[:20],
        "driver_network": {
            "total_registered": len(drivers),
            "cleared_to_dispatch": len(cleared_drivers),
            "pending_compliance": len(drivers) - len(cleared_drivers),
            "wheelchair_capable": len(wheelchair_drivers),
            "model": "1099 contractor — drivers provide own vehicles",
        },
        "broker_registrations": {
            b["broker_name"]: b["registration_status"]
            for b in get_broker_list()
        },
        "supported_mco_payers": len(MICHIGAN_MCO_PAYERS),
        "transport_types": list(TRANSPORT_TYPES.keys()),
    }


# ─────────────────────────────────────────────────────────────────────────────
# API Routes
# ─────────────────────────────────────────────────────────────────────────────

@prism_nemt.route("/prism/nemt/dashboard", methods=["GET"])
def route_nemt_dashboard():
    return jsonify(get_dashboard())


@prism_nemt.route("/prism/nemt/payers", methods=["GET"])
def route_nemt_payers():
    """Michigan Medicaid MCO payer directory with contact info."""
    return jsonify({"payers": get_mco_payer_list()})


@prism_nemt.route("/prism/nemt/brokers", methods=["GET"])
def route_nemt_brokers():
    """NEMT broker network directory with registration status."""
    return jsonify({"brokers": get_broker_list(), "total": len(NEMT_BROKERS)})


@prism_nemt.route("/prism/nemt/brokers/<broker_name>/status", methods=["PATCH"])
def route_update_broker_status(broker_name: str):
    """Update registration status for a broker. Status values: NOT STARTED, APPLIED, CREDENTIALING, APPROVED, ACTIVE."""
    data = request.get_json(force=True) or {}
    status = data.get("status", "").strip()
    if not status:
        return jsonify({"error": "status required"}), 400
    try:
        result = update_broker_status(
            broker_name=broker_name,
            status=status,
            application_date=data.get("application_date"),
            approval_date=data.get("approval_date"),
        )
        return jsonify(result)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@prism_nemt.route("/prism/nemt/transport-types", methods=["GET"])
def route_transport_types():
    return jsonify({"transport_types": TRANSPORT_TYPES})


@prism_nemt.route("/prism/nemt/orders", methods=["GET"])
def route_list_orders():
    state = _load_state()
    orders = list(state.get("orders", {}).values())
    status_filter = request.args.get("status")
    if status_filter:
        orders = [o for o in orders if o.get("status") == status_filter]
    orders.sort(key=lambda x: x.get("created_at") or "", reverse=True)
    return jsonify({"orders": orders, "count": len(orders)})


@prism_nemt.route("/prism/nemt/orders", methods=["POST"])
def route_create_order():
    data = request.get_json(force=True) or {}
    required = ["member_medicaid_id", "member_name", "member_dob", "payer",
                "transport_type", "pickup_address", "dropoff_address", "pickup_time"]
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400
    try:
        order = create_nemt_order(
            member_medicaid_id=data["member_medicaid_id"],
            member_name=data["member_name"],
            member_dob=data["member_dob"],
            payer=data["payer"],
            transport_type=data["transport_type"],
            pickup_address=data["pickup_address"],
            dropoff_address=data["dropoff_address"],
            pickup_time=data["pickup_time"],
            appointment_time=data.get("appointment_time"),
            trip_purpose=data.get("trip_purpose", "Medical appointment"),
            mileage=float(data.get("mileage", 0)),
            eligibility_verified=bool(data.get("eligibility_verified", False)),
            prior_auth_id=data.get("prior_auth_id"),
            prior_auth_number=data.get("prior_auth_number"),
            driver_name=data.get("driver_name"),
            vehicle_id=data.get("vehicle_id"),
            notes=data.get("notes"),
        )
        return jsonify(order), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@prism_nemt.route("/prism/nemt/orders/<order_id>", methods=["GET"])
def route_get_order(order_id: str):
    state = _load_state()
    order = state.get("orders", {}).get(order_id)
    if not order:
        return jsonify({"error": "Order not found"}), 404
    return jsonify(order)


@prism_nemt.route("/prism/nemt/orders/<order_id>/dispatch", methods=["POST"])
def route_dispatch(order_id: str):
    """
    Dispatch via Uber Health or Lyft Healthcare.
    Body params (all optional — system auto-selects platform by transport_type):
      fulfillment_platform: "uber_health" | "lyft_healthcare" (auto if omitted)
      member_phone:         required for Lyft API booking
      pickup_lat/lng:       required for API booking (omit to use dashboard manually)
      dropoff_lat/lng:      required for API booking
    """
    data = request.get_json(force=True) or {}
    try:
        result = dispatch_order(
            order_id=order_id,
            fulfillment_platform=data.get("fulfillment_platform"),
            member_phone=data.get("member_phone"),
            pickup_lat=data.get("pickup_lat"),
            pickup_lng=data.get("pickup_lng"),
            dropoff_lat=data.get("dropoff_lat"),
            dropoff_lng=data.get("dropoff_lng"),
        )
        return jsonify(result)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@prism_nemt.route("/prism/nemt/orders/<order_id>/complete", methods=["POST"])
def route_complete(order_id: str):
    from nexus_scheduler import get_airtable_client
    data = request.get_json(force=True) or {}
    required = ["actual_pickup_time", "actual_dropoff_time", "actual_mileage"]
    missing = [f for f in required if not data.get(f) and data.get(f) != 0]
    if missing:
        return jsonify({"error": f"Missing: {', '.join(missing)}"}), 400
    try:
        airtable = get_airtable_client()
        result = complete_trip(
            airtable=airtable,
            order_id=order_id,
            actual_pickup_time=data["actual_pickup_time"],
            actual_dropoff_time=data["actual_dropoff_time"],
            actual_mileage=float(data["actual_mileage"]),
            auto_generate_claim=bool(data.get("auto_generate_claim", False)),
        )
        return jsonify(result)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@prism_nemt.route("/prism/nemt/orders/<order_id>/eligibility", methods=["GET"])
def route_eligibility_check(order_id: str):
    state = _load_state()
    order = state.get("orders", {}).get(order_id)
    if not order:
        return jsonify({"error": "Order not found"}), 404
    return jsonify(check_member_eligibility_checklist(order))


@prism_nemt.route("/prism/nemt/prior-auths", methods=["GET"])
def route_list_prior_auths():
    mid = request.args.get("member_medicaid_id")
    return jsonify({"prior_auths": list_prior_auths(mid)})


@prism_nemt.route("/prism/nemt/prior-auths", methods=["POST"])
def route_create_prior_auth():
    data = request.get_json(force=True) or {}
    required = ["member_medicaid_id", "member_name", "payer", "hcpcs_code",
                "service_start_date", "service_end_date", "authorized_trips"]
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({"error": f"Missing: {', '.join(missing)}"}), 400
    try:
        auth = create_prior_auth(
            member_medicaid_id=data["member_medicaid_id"],
            member_name=data["member_name"],
            payer=data["payer"],
            hcpcs_code=data["hcpcs_code"],
            service_start_date=data["service_start_date"],
            service_end_date=data["service_end_date"],
            authorized_trips=int(data["authorized_trips"]),
            auth_number=data.get("auth_number"),
            notes=data.get("notes"),
        )
        return jsonify(auth), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@prism_nemt.route("/prism/nemt/drivers", methods=["GET"])
def route_list_drivers():
    state = _load_state()
    drivers = list(state.get("drivers", {}).values())
    return jsonify({"drivers": drivers})


@prism_nemt.route("/prism/nemt/drivers", methods=["POST"])
def route_register_driver():
    data = request.get_json(force=True) or {}
    required = ["name", "license_number", "phone",
                "vehicle_year", "vehicle_make", "vehicle_model", "vehicle_vin", "vehicle_plate"]
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({"error": f"Missing: {', '.join(missing)}"}), 400
    driver = register_driver(
        name=data["name"],
        license_number=data["license_number"],
        phone=data["phone"],
        vehicle_year=int(data["vehicle_year"]),
        vehicle_make=data["vehicle_make"],
        vehicle_model=data["vehicle_model"],
        vehicle_vin=data["vehicle_vin"],
        vehicle_plate=data["vehicle_plate"],
        wheelchair_equipped=bool(data.get("wheelchair_equipped", False)),
        stretcher_equipped=bool(data.get("stretcher_equipped", False)),
        contractor_type=data.get("contractor_type", "1099"),
        background_check_date=data.get("background_check_date"),
        background_check_cleared=bool(data.get("background_check_cleared", False)),
        hipaa_trained=bool(data.get("hipaa_trained", False)),
        mvr_clear=bool(data.get("mvr_clear", False)),
        insurance_verified=bool(data.get("insurance_verified", False)),
        service_counties=data.get("service_counties"),
    )
    return jsonify(driver), 201


@prism_nemt.route("/prism/nemt/vertex-summary", methods=["GET"])
def route_vertex_summary():
    """Billing summary from VERTEX — pending claims, total billed, total received."""
    from nexus_scheduler import get_airtable_client
    try:
        airtable = get_airtable_client()
        return jsonify(get_nemt_summary(airtable))
    except Exception as e:
        return jsonify({"error": str(e)}), 500
