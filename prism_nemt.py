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
    prism_order_id: Optional[str] = None,
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
        "prism_order_id": (prism_order_id or "").strip() or None,
        "status": "scheduled",
        "created_at": _now_iso(),
        "dispatched_at": None,
        "completed_at": None,
        "vertex_trip_id": None,
        "vertex_invoice_id": None,
    }

    from nemt_billing import apply_hap_intake_defaults

    apply_hap_intake_defaults(order)
    if eligibility_verified:
        order["eligibility_verified"] = True

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


def find_nemt_order_by_prism_id(prism_order_id: str) -> Optional[Dict[str, Any]]:
    """Resolve linked NEMT order from PRISM confirmation / order id."""
    pid = (prism_order_id or "").strip()
    if not pid:
        return None
    state = _load_state()
    for order in state.get("orders", {}).values():
        if order.get("prism_order_id") == pid:
            return order
    for order in state.get("orders", {}).values():
        notes = order.get("notes") or ""
        if pid in notes:
            return order
    return None


ALLOWED_RIDE_TRACKING_HOSTS = frozenset(
    {
        "trip.uber.com",
        "lyft.com",
        "www.lyft.com",
        "ride.lyft.com",
        "lft.to",  # Lyft SMS short links
    }
)


def infer_fulfillment_platform_from_tracking_url(url: str) -> str:
    """Map guest tracking URL host → fulfillment platform key."""
    from urllib.parse import urlparse

    host = (urlparse((url or "").strip()).netloc or "").lower()
    if host == "trip.uber.com":
        return "uber_health"
    if host == "lft.to" or host.endswith("lyft.com"):
        return "lyft_healthcare"
    return ""


def validate_ride_tracking_url(url: str) -> str:
    """Official Uber Health / Lyft Concierge guest tracking links (open in new tab)."""
    from urllib.parse import urlparse

    u = (url or "").strip()
    if not u:
        raise ValueError("rider_tracking_url is required")
    parsed = urlparse(u)
    if parsed.scheme != "https":
        raise ValueError("Tracking URL must use HTTPS")
    host = (parsed.netloc or "").lower()
    if host not in ALLOWED_RIDE_TRACKING_HOSTS and not host.endswith(".lyft.com"):
        raise ValueError(
            "Tracking URL must be a valid HTTPS guest trip tracking link from dispatch"
        )
    return u


def _sync_ride_tracking_to_prism(nemt_order: Dict[str, Any]) -> None:
    """Mirror rider tracking URL onto linked PRISM order for portal.deedavis.biz."""
    prism_id = (nemt_order.get("prism_order_id") or "").strip()
    url = (nemt_order.get("rider_tracking_url") or "").strip()
    if not prism_id or not url:
        return
    try:
        from prism_orders_api import ORDERS_FILE, _load, _save

        orders = _load(ORDERS_FILE, [])
        for i, o in enumerate(orders):
            if o.get("id") != prism_id:
                continue
            details = dict(o.get("details") or {})
            details["ride_tracking_url"] = url
            details["ride_tracking_platform"] = (
                nemt_order.get("fulfillment_platform")
                or details.get("ride_tracking_platform")
                or ""
            )
            details["ride_tracking_updated_at"] = (
                nemt_order.get("rider_tracking_updated_at") or _now_iso()
            )
            orders[i]["details"] = details
            orders[i]["updated_at"] = _now_iso()
            raw_status = (o.get("status") or "").lower()
            if nemt_order.get("status") == "dispatched" or raw_status in (
                "confirmed",
                "scheduled",
                "new",
            ):
                orders[i]["status"] = "In Progress"
            _save(ORDERS_FILE, orders)
            return
    except Exception as exc:
        print(f"Ride tracking sync to PRISM skipped: {exc}")


def set_nemt_ride_tracking(
    order_id: str,
    rider_tracking_url: str,
    fulfillment_platform: Optional[str] = None,
) -> Dict[str, Any]:
    """Persist guest tracking link on NEMT order and push to client portal."""
    url = validate_ride_tracking_url(rider_tracking_url)
    state = _load_state()
    order = state.get("orders", {}).get(order_id)
    if not order:
        raise ValueError(f"NEMT order not found: {order_id}")

    platform = (fulfillment_platform or "").strip() or infer_fulfillment_platform_from_tracking_url(url)
    if platform:
        order["fulfillment_platform"] = platform
    order["rider_tracking_url"] = url
    order["rider_tracking_updated_at"] = _now_iso()
    state["orders"][order_id] = order
    _save_state(state)
    _sync_ride_tracking_to_prism(order)
    return order


def link_prism_nemt_order(prism_order_id: str, nemt_order_id: str) -> None:
    """Persist PRISM ↔ NEMT link on the PRISM order details blob."""
    try:
        from prism_orders_api import ORDERS_FILE, _load, _save

        orders = _load(ORDERS_FILE, [])
        for i, o in enumerate(orders):
            if o.get("id") == prism_order_id:
                details = dict(o.get("details") or {})
                details["nemt_order_id"] = nemt_order_id
                orders[i]["details"] = details
                orders[i]["updated_at"] = _now_iso()
                _save(ORDERS_FILE, orders)
                return
    except Exception as exc:
        print(f"PRISM↔NEMT link skipped: {exc}")


def _map_trip_type_label_to_transport(trip_type: str) -> str:
    t = (trip_type or "").lower()
    if "wheel" in t or "wav" in t:
        return "wheelchair"
    if "stretcher" in t or "bls" in t:
        return "stretcher"
    return "ambulatory"


def _intake_transport_type(order: Dict[str, Any], data: Dict[str, Any]) -> str:
    details = order.get("details") or data.get("details") or {}
    trip_type = details.get("trip_type") or data.get("trip_type") or ""
    if trip_type:
        return _map_trip_type_label_to_transport(trip_type)
    tt = (data.get("transport_type") or details.get("transport_type") or "").lower()
    if tt in TRANSPORT_TYPES:
        return tt
    return "ambulatory"


def _intake_payer(order: Dict[str, Any], data: Dict[str, Any]) -> str:
    details = order.get("details") or data.get("details") or {}
    for src in (
        details.get("payer"),
        data.get("payer"),
        data.get("client_company"),
        order.get("client"),
    ):
        if not src:
            continue
        s = str(src).strip()
        if "caresource" in s.lower() or s.lower().startswith("hap"):
            return "HAP CareSource"
        if s:
            return s
    program = (details.get("program_type") or details.get("mobility_lane") or "").lower()
    if any(k in program for k in ("medicaid", "mco", "mob-a", "hap", "plan nemt")):
        return "HAP CareSource"
    return PAYER_DEFAULT


def _normalize_intake_date(raw: str) -> str:
    s = (raw or "").strip()
    if not s:
        return ""
    if "/" in s:
        for fmt in ("%m/%d/%Y", "%m/%d/%y"):
            try:
                return datetime.strptime(s, fmt).strftime("%Y-%m-%d")
            except ValueError:
                continue
    return s


def create_nemt_from_prism_intake(order: Dict[str, Any], data: Dict[str, Any]) -> Optional[str]:
    """
    Create and link a NEMT ops order from a PRISM intake submission (web portal, voice, API).

    Returns the NEMT order_id when created or already linked; None when not applicable or skipped.
    """
    svc_key = (order.get("service_key") or data.get("service_key") or "").lower()
    if svc_key not in ("nemt", "transport"):
        return None

    prism_id = (order.get("id") or "").strip()
    if not prism_id:
        return None

    if data.get("skip_nemt_auto_link"):
        return None

    existing = find_nemt_order_by_prism_id(prism_id)
    if existing:
        return existing.get("order_id")

    details = dict(order.get("details") or data.get("details") or {})
    channel = (data.get("channel") or order.get("channel") or "").strip().lower()
    intake_channel = (details.get("intake_channel") or "").strip().lower()
    voice_intake = channel == "voice" or intake_channel == "voice_ai"

    pickup = (
        details.get("pickup_address")
        or data.get("subject_location")
        or order.get("address")
        or ""
    ).strip()
    dropoff = (
        details.get("dropoff_address")
        or data.get("collection_site")
        or order.get("collection_site")
        or ""
    ).strip()
    if not pickup or not dropoff:
        print(f"NEMT auto-link skipped for {prism_id}: missing pickup or dropoff")
        return None

    member_id = (
        details.get("member_id")
        or data.get("subject_id")
        or order.get("subject_id")
        or ""
    ).strip()
    member_name = (order.get("signer") or "").strip()
    if not member_name:
        member_name = f"{data.get('subject_first', '')} {data.get('subject_last', '')}".strip()
    member_dob = (
        order.get("subject_dob") or data.get("subject_dob") or "Pending verification"
    ).strip()

    transport = _intake_transport_type(order, data)
    payer = _intake_payer(order, data)

    sched_date = _normalize_intake_date(data.get("sched_date") or order.get("date") or "")
    sched_time = (data.get("sched_time") or order.get("time") or "").strip()
    pickup_time = f"{sched_date} {sched_time}".strip() or sched_date or "TBD"

    purpose = (
        details.get("appointment_purpose")
        or details.get("nemt_purpose")
        or "Medical appointment"
    ).strip()

    notes_parts: List[str] = []
    base_notes = (order.get("notes") or data.get("notes") or "").strip()
    if base_notes:
        notes_parts.append(base_notes)
    if details.get("rebook_mode"):
        notes_parts.append(
            f"Rebook: {details.get('rebook_mode')} from {details.get('rebook_source_id', '')}"
        )
    if details.get("trip_direction") == "return":
        notes_parts.append(
            f"Return leg linked to {details.get('linked_outbound_trip_id', '')}"
        )
    notes_parts.append(f"Intake channel: {channel or intake_channel or 'web'}")
    notes = " · ".join(notes_parts)

    try:
        nemt_order = create_nemt_order(
            member_medicaid_id=member_id,
            member_name=member_name,
            member_dob=member_dob,
            payer=payer,
            transport_type=transport,
            pickup_address=pickup,
            dropoff_address=dropoff,
            pickup_time=pickup_time,
            trip_purpose=purpose,
            notes=notes,
            prism_order_id=prism_id,
            eligibility_verified=voice_intake,
        )
        nemt_id = nemt_order.get("order_id")
        if nemt_id:
            link_prism_nemt_order(prism_id, nemt_id)
            return nemt_id
    except Exception as exc:
        print(f"NEMT auto-link failed for {prism_id}: {exc}")
    return None


def _sync_prism_order_status(
    prism_order_id: str,
    status: str,
    *,
    notify: bool = True,
    details_patch: Optional[Dict[str, Any]] = None,
) -> None:
    """Mirror NEMT ops milestones on linked PRISM order (portal + notifications)."""
    if not prism_order_id:
        return
    try:
        from prism_orders_api import sync_prism_order_status

        sync_prism_order_status(
            prism_order_id,
            status,
            notify=notify,
            details_patch=details_patch,
        )
    except Exception as exc:
        print(f"PRISM order sync skipped: {exc}")


def _sync_prism_order_complete(prism_order_id: str, vertex_invoice_id: Optional[str] = None) -> None:
    """Mark PRISM intake order Complete after NEMT trip closes."""
    patch = {"vertex_invoice_id": vertex_invoice_id} if vertex_invoice_id else None
    _sync_prism_order_status(prism_order_id, "Complete", notify=True, details_patch=patch)


def dispatch_order(
    order_id: str,
    fulfillment_platform: Optional[str] = None,
    member_phone: Optional[str] = None,
    pickup_lat: Optional[float] = None,
    pickup_lng: Optional[float] = None,
    dropoff_lat: Optional[float] = None,
    dropoff_lng: Optional[float] = None,
    rider_tracking_url: Optional[str] = None,
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

    prism_id = order.get("prism_order_id")
    if prism_id:
        _sync_prism_order_status(prism_id, "In Progress", notify=True)

    tracking_error = None
    if rider_tracking_url:
        try:
            tracking_platform = (
                infer_fulfillment_platform_from_tracking_url(rider_tracking_url) or platform
            )
            order = set_nemt_ride_tracking(
                order_id,
                rider_tracking_url,
                fulfillment_platform=tracking_platform,
            )
        except ValueError as exc:
            tracking_error = str(exc)

    # ─── LEARNING ENGINE: Log driver assigned ─────────────────────────────────
    nxlearn('transport', order_id, 'driver_assigned', {
        'transport_type': transport_type,
        'fulfillment_partner': platform,
        'mco_id': order.get('payer'),
        'region': 'MI',
    })

    result: Dict[str, Any] = {"order": order, "dispatch": platform_response}
    if tracking_error:
        result["tracking_url_error"] = tracking_error
    return result


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
        prism_order_id=order.get("prism_order_id") or order_id,
        transport_type=order.get("transport_type"),
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

    vertex_invoice_id = None
    if claim_result and isinstance(claim_result, dict):
        vertex_invoice_id = (claim_result.get("invoice") or {}).get("id")

    prism_id = order.get("prism_order_id")
    if prism_id:
        _sync_prism_order_complete(prism_id, vertex_invoice_id)

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
# Confirmation helpers
# ─────────────────────────────────────────────────────────────────────────────

_TRANSPORT_LABELS = {
    "ambulatory":    "ambulatory transport (standard vehicle)",
    "wheelchair":    "wheelchair-accessible van transport",
    "stretcher":     "stretcher / gurney transport",
    "volunteer":     "volunteer driver transport",
    "bus":           "public transit pass",
    "rx_standard":   "prescription delivery",
    "rx_controlled": "controlled substance prescription delivery",
    "rx_cold_chain": "cold-chain prescription delivery",
}

_BRING_BY_TRANSPORT = {
    "ambulatory":    "Be ready at your pickup address at the scheduled time. Have your Medicaid ID available.",
    "wheelchair":    "Have your wheelchair secured and be ready at your pickup address. Have your Medicaid ID available.",
    "stretcher":     "Medical transport crew will assist. Have your Medicaid ID and any required paperwork ready.",
    "rx_standard":   "A valid photo ID is required for delivery. Someone must be present to sign.",
    "rx_controlled": "A valid photo ID is REQUIRED. You must sign in person — no leave-at-door.",
    "rx_cold_chain": "A valid photo ID required. Please have refrigerator space ready for temperature-sensitive medication.",
}


def _send_nemt_confirmation_async(order: Dict[str, Any], req_data: Dict[str, Any]) -> None:
    """
    Send initial appointment confirmation + schedule day-of reminder for NEMT.
    En route / arrived / completion tracking is handled by Uber Health /
    Lyft Healthcare webhooks once API credentials are active.
    """
    phone = (req_data.get("member_phone") or "").strip()
    email = (req_data.get("member_email") or "").strip()

    if not phone and not email:
        return

    transport_type = order.get("transport_type", "ambulatory")
    what_str  = _TRANSPORT_LABELS.get(transport_type, "medical transport")
    bring_str = _BRING_BY_TRANSPORT.get(transport_type, "Have your Medicaid ID available.")
    pickup    = order.get("pickup_address", "your pickup address")
    dropoff   = order.get("dropoff_address", "your destination")
    pickup_t  = order.get("pickup_time", "")
    appt_t    = order.get("appointment_time", "")
    purpose   = order.get("trip_purpose", "Medical appointment")
    ref       = order.get("order_id", "")
    name      = order.get("member_name", "there")
    payer     = order.get("payer", "")

    dt_str   = pickup_t
    location = f"Pickup: {pickup} → Drop-off: {dropoff}"
    why_str  = f"{purpose}" + (f" · Payer: {payer}" if payer else "")
    if appt_t:
        why_str += f" · Appointment time at destination: {appt_t}"

    def _do() -> None:
        try:
            # Add to NEXUS calendar
            from nexus_calendar_service import create_calendar_event
            create_calendar_event(
                title=f"NEMT — {name} → {dropoff.split(',')[0]}",
                start_iso=pickup_t if "T" in pickup_t else pickup_t + "T09:00:00",
                location=location,
                description=f"{why_str}\n{bring_str}",
                system="NEMT",
                event_type="ride",
                internal_id=ref,
                party_name=name,
                party_email=email,
                party_phone=phone,
            )
        except Exception:
            pass
        try:
            from nexus_confirmation_engine import send_confirmation_request
            send_confirmation_request(
                event_type="nemt_ride",
                party_name=name,
                party_email=email,
                party_phone=phone,
                datetime_str=dt_str,
                location=location,
                internal_id=ref,
                notes=order.get("notes", ""),
                who="Dee Davis Inc. NEMT — your driver will be assigned before pickup",
                what=what_str.capitalize(),
                why=why_str,
                bring=bring_str,
            )
            # Day-of reminder via PRISM orders helper
            # Build a minimal order-shaped dict so _fire_dayon_reminder works
            from prism_orders_api import _fire_dayon_reminder
            proxy = {
                "service_key": "nemt",
                "subject_phone": phone,
                "client_phone": phone,
                "date": pickup_t.split("T")[0] if "T" in pickup_t else pickup_t.split(" ")[0],
                "time": pickup_t.split("T")[1][:5] if "T" in pickup_t else "",
                "timezone": "ET",
                "address": pickup,
                "collection_site": "",
                "id": ref,
                "service_label": what_str,
                "notes": order.get("notes", ""),
            }
            _fire_dayon_reminder(proxy)
        except Exception as exc:
            import logging
            logging.getLogger("prism.nemt").warning("Confirmation engine error: %s", exc)

    threading.Thread(target=_do, daemon=True).start()


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
            prism_order_id=data.get("prism_order_id"),
        )
        if data.get("prism_order_id") and order.get("order_id"):
            link_prism_nemt_order(data["prism_order_id"], order["order_id"])
        # ── Initial appointment confirmation + day-of reminder ──────────────
        # En route / arrived / departed tracking comes from Uber Health /
        # Lyft Healthcare webhooks once API credentials are active.
        _send_nemt_confirmation_async(order, data)
        return jsonify(order), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@prism_nemt.route("/prism/nemt/orders/by-prism/<prism_id>", methods=["GET"])
def route_by_prism_order(prism_id: str):
    order = find_nemt_order_by_prism_id(prism_id)
    if not order:
        return jsonify({
            "error": "No NEMT order linked to this PRISM order",
            "prism_order_id": prism_id,
        }), 404
    return jsonify(order)


@prism_nemt.route("/prism/nemt/orders/<order_id>/verify-eligibility", methods=["POST"])
def route_verify_eligibility(order_id: str):
    """Ops QA: mark eligibility verified and refresh dispatch checklist."""
    from nemt_billing import apply_hap_intake_defaults, check_member_eligibility_checklist

    data = request.get_json(force=True) or {}
    state = _load_state()
    order = state.get("orders", {}).get(order_id)
    if not order:
        return jsonify({"error": "Order not found"}), 404

    apply_hap_intake_defaults(order)
    order["eligibility_verified"] = True
    order["eligibility_verified_at"] = _now_iso()
    if data.get("prior_auth_number"):
        order["prior_auth_number"] = data["prior_auth_number"]
    if data.get("prior_auth_id"):
        order["prior_auth_id"] = data["prior_auth_id"]

    checklist = check_member_eligibility_checklist(order)
    order["eligibility_checklist"] = checklist
    state["orders"][order_id] = order
    _save_state(state)

    prism_id = order.get("prism_order_id")
    if prism_id:
        _sync_prism_order_status(prism_id, "Confirmed", notify=True)

    return jsonify({"order": order, "checklist": checklist})


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
            rider_tracking_url=data.get("rider_tracking_url"),
        )
        return jsonify(result)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@prism_nemt.route("/prism/nemt/orders/<order_id>/ride-tracking", methods=["POST"])
def route_set_ride_tracking(order_id: str):
    """
    Ops: paste guest trip tracking link after manual dashboard dispatch.
    Body: { "rider_tracking_url": "<https tracking URL>", "fulfillment_platform": "uber_health|lyft_healthcare" (optional — auto-detected) }
    """
    data = request.get_json(force=True) or {}
    try:
        order = set_nemt_ride_tracking(
            order_id,
            data.get("rider_tracking_url", ""),
            fulfillment_platform=data.get("fulfillment_platform"),
        )
        return jsonify({"success": True, "order": order, "ride_tracking_url": order.get("rider_tracking_url")})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@prism_nemt.route("/prism/nemt/orders/<order_id>/complete", methods=["POST"])
def route_complete(order_id: str):
    from nexus_backend import AirtableClient
    data = request.get_json(force=True) or {}
    required = ["actual_pickup_time", "actual_dropoff_time", "actual_mileage"]
    missing = [f for f in required if not data.get(f) and data.get(f) != 0]
    if missing:
        return jsonify({"error": f"Missing: {', '.join(missing)}"}), 400
    try:
        airtable = AirtableClient()
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
    from nexus_backend import AirtableClient
    try:
        airtable = AirtableClient()
        return jsonify(get_nemt_summary(airtable))
    except Exception as e:
        return jsonify({"error": str(e)}), 500
