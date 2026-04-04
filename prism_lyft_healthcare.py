"""
PRISM — Lyft Healthcare (Lyft Concierge) Integration
=====================================================
Lyft Healthcare provides on-demand and scheduled rides for NEMT.
DDI uses Lyft Healthcare as a fulfillment partner — Lyft provides the driver
and vehicle, DDI handles dispatch coordination, billing, and compliance.

Lyft Healthcare advantages over Uber Health:
  - WAV (Wheelchair Accessible Vehicle) rides available in Metro Detroit
  - Scheduled rides up to 7 days in advance
  - HIPAA Business Associate Agreement (BAA) available
  - Lyft Concierge dashboard for fleet/coordinator management

Secrets (set in .env — never commit):
  LYFT_HEALTHCARE_CLIENT_ID
  LYFT_HEALTHCARE_CLIENT_SECRET
  LYFT_HEALTHCARE_ACCOUNT_ID     (Concierge account identifier)

Lyft Healthcare API base: https://api.lyft.com
Sandbox: use mock/test credentials — Lyft does not have a separate sandbox host
"""

from __future__ import annotations

import os
import threading
import time
from typing import Any, Dict, List, Optional

import requests
from dotenv import load_dotenv
from flask import Blueprint, jsonify, request

load_dotenv()

prism_lyft_healthcare = Blueprint("prism_lyft_healthcare", __name__)

LYFT_API_BASE = "https://api.lyft.com"
LYFT_TOKEN_URL = "https://api.lyft.com/oauth/token"

# Lyft ride type IDs relevant to NEMT
LYFT_RIDE_TYPES = {
    "lyft":         "lyft",           # Standard — ambulatory, seated
    "lyft_xl":      "lyft_xl",        # XL van — multiple passengers or equipment
    "lyft_wav":     "lyft_wav",       # Wheelchair Accessible Vehicle
    "lyft_lux":     "lyft_lux",       # Premium (rarely needed for NEMT)
}

# NEMT transport type → preferred Lyft ride type
NEMT_TYPE_TO_LYFT = {
    "ambulatory":   "lyft",
    "wheelchair":   "lyft_wav",
    "stretcher":    None,             # Lyft cannot fulfill stretcher transport
    "volunteer":    None,             # Not applicable
    "bus":          None,             # Not applicable
}


def _env(name: str, default: str = "") -> str:
    return os.environ.get(name, "").strip() or default


class LyftHealthcareClient:
    """OAuth client-credentials + cached bearer token for Lyft Healthcare API."""

    def __init__(self) -> None:
        self._client_id = _env("LYFT_HEALTHCARE_CLIENT_ID")
        self._client_secret = _env("LYFT_HEALTHCARE_CLIENT_SECRET")
        self._account_id = _env("LYFT_HEALTHCARE_ACCOUNT_ID") or None
        self._lock = threading.Lock()
        self._access_token: Optional[str] = None
        self._expires_at: float = 0.0

    def is_configured(self) -> bool:
        return bool(self._client_id and self._client_secret)

    def _fetch_token(self) -> Dict[str, Any]:
        if not self.is_configured():
            raise RuntimeError(
                "LYFT_HEALTHCARE_CLIENT_ID and LYFT_HEALTHCARE_CLIENT_SECRET must be set in .env"
            )
        r = requests.post(
            LYFT_TOKEN_URL,
            timeout=30,
            auth=(self._client_id, self._client_secret),
            data={"grant_type": "client_credentials", "scope": "rides.request public"},
        )
        r.raise_for_status()
        return r.json()

    def get_access_token(self, force_refresh: bool = False) -> str:
        with self._lock:
            now = time.time()
            if not force_refresh and self._access_token and now < self._expires_at - 120:
                return self._access_token
            data = self._fetch_token()
            token = data.get("access_token")
            if not token:
                raise RuntimeError("Lyft token response missing access_token")
            self._access_token = token
            exp = int(data.get("expires_in", 3600))
            self._expires_at = now + max(exp, 60)
            return self._access_token

    def _headers(self) -> Dict[str, str]:
        h = {
            "Authorization": f"Bearer {self.get_access_token()}",
            "Content-Type": "application/json",
        }
        if self._account_id:
            h["X-Lyft-Account-Id"] = self._account_id
        return h

    def get_ride_types(self, lat: float, lng: float) -> tuple[int, Any]:
        """GET /v1/ridetypes — available ride types at a location."""
        url = f"{LYFT_API_BASE}/v1/ridetypes"
        r = requests.get(url, headers=self._headers(), params={"lat": lat, "lng": lng}, timeout=30)
        try:
            return r.status_code, r.json()
        except Exception:
            return r.status_code, {"raw": r.text}

    def get_cost_estimate(
        self,
        ride_type: str,
        start_lat: float,
        start_lng: float,
        end_lat: float,
        end_lng: float,
    ) -> tuple[int, Any]:
        """GET /v1/cost — fare estimate before booking."""
        url = f"{LYFT_API_BASE}/v1/cost"
        params = {
            "ride_type": ride_type,
            "start_lat": start_lat,
            "start_lng": start_lng,
            "end_lat": end_lat,
            "end_lng": end_lng,
        }
        r = requests.get(url, headers=self._headers(), params=params, timeout=30)
        try:
            return r.status_code, r.json()
        except Exception:
            return r.status_code, {"raw": r.text}

    def request_ride(
        self,
        ride_type: str,
        origin_lat: float,
        origin_lng: float,
        destination_lat: float,
        destination_lng: float,
        origin_address: str,
        destination_address: str,
        passenger_name: str,
        passenger_phone: str,
        scheduled_at: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> tuple[int, Any]:
        """POST /v1/rides — book a ride on behalf of a member."""
        body: Dict[str, Any] = {
            "ride_type": ride_type,
            "origin": {
                "lat": origin_lat,
                "lng": origin_lng,
                "address": origin_address,
            },
            "destination": {
                "lat": destination_lat,
                "lng": destination_lng,
                "address": destination_address,
            },
            "passenger": {
                "first_name": passenger_name.split()[0] if passenger_name else "Member",
                "last_name": " ".join(passenger_name.split()[1:]) if len(passenger_name.split()) > 1 else "",
                "phone_number": passenger_phone,
            },
        }
        if scheduled_at:
            body["scheduled_at"] = scheduled_at
        if notes:
            body["origin"]["notes"] = notes
        url = f"{LYFT_API_BASE}/v1/rides"
        r = requests.post(url, json=body, headers=self._headers(), timeout=45)
        try:
            return r.status_code, r.json()
        except Exception:
            return r.status_code, {"raw": r.text}

    def get_ride_status(self, ride_id: str) -> tuple[int, Any]:
        """GET /v1/rides/{id} — check status of a booked ride."""
        url = f"{LYFT_API_BASE}/v1/rides/{ride_id}"
        r = requests.get(url, headers=self._headers(), timeout=30)
        try:
            return r.status_code, r.json()
        except Exception:
            return r.status_code, {"raw": r.text}

    def cancel_ride(self, ride_id: str, reason: Optional[str] = None) -> tuple[int, Any]:
        """POST /v1/rides/{id}/cancel."""
        url = f"{LYFT_API_BASE}/v1/rides/{ride_id}/cancel"
        body = {}
        if reason:
            body["cancel_confirmation_token"] = reason
        r = requests.post(url, json=body, headers=self._headers(), timeout=30)
        try:
            return r.status_code, r.json()
        except Exception:
            return r.status_code, {"raw": r.text}

    def status_dict(self) -> Dict[str, Any]:
        return {
            "configured": self.is_configured(),
            "token_cached": bool(self._access_token),
            "expires_at_epoch": self._expires_at if self._expires_at else None,
            "account_id_set": bool(self._account_id),
            "api_base": LYFT_API_BASE,
            "wav_available": True,
            "scheduled_rides": True,
            "baa_available": True,
        }


_lyft_client: Optional[LyftHealthcareClient] = None


def get_lyft_healthcare_client() -> LyftHealthcareClient:
    global _lyft_client
    if _lyft_client is None:
        _lyft_client = LyftHealthcareClient()
    return _lyft_client


def get_lyft_ride_type_for_nemt(transport_type: str) -> Optional[str]:
    """Map PRISM transport type to Lyft ride type. Returns None if Lyft cannot fulfill."""
    return NEMT_TYPE_TO_LYFT.get(transport_type)


# ─────────────────────────────────────────────────────────────────────────────
# API Routes
# ─────────────────────────────────────────────────────────────────────────────

@prism_lyft_healthcare.route("/prism/lyft-healthcare/status", methods=["GET"])
def lyft_status():
    return jsonify(get_lyft_healthcare_client().status_dict())


@prism_lyft_healthcare.route("/prism/lyft-healthcare/ride-types", methods=["GET"])
def lyft_ride_types():
    """Available Lyft ride types at a given lat/lng."""
    lat = request.args.get("lat", type=float)
    lng = request.args.get("lng", type=float)
    if not lat or not lng:
        return jsonify({"error": "lat and lng required"}), 400
    c = get_lyft_healthcare_client()
    if not c.is_configured():
        return jsonify({"error": "Lyft Healthcare credentials not configured", "env_vars_needed": ["LYFT_HEALTHCARE_CLIENT_ID", "LYFT_HEALTHCARE_CLIENT_SECRET"]}), 503
    status, payload = c.get_ride_types(lat, lng)
    return jsonify(payload), status


@prism_lyft_healthcare.route("/prism/lyft-healthcare/estimate", methods=["POST"])
def lyft_cost_estimate():
    """Fare estimate for a NEMT trip before booking."""
    data = request.get_json(force=True) or {}
    required = ["ride_type", "start_lat", "start_lng", "end_lat", "end_lng"]
    missing = [f for f in required if data.get(f) is None]
    if missing:
        return jsonify({"error": f"Missing: {', '.join(missing)}"}), 400
    c = get_lyft_healthcare_client()
    if not c.is_configured():
        return jsonify({"error": "Lyft Healthcare credentials not configured"}), 503
    status, payload = c.get_cost_estimate(
        data["ride_type"], data["start_lat"], data["start_lng"],
        data["end_lat"], data["end_lng"],
    )
    return jsonify(payload), status


@prism_lyft_healthcare.route("/prism/lyft-healthcare/rides", methods=["POST"])
def lyft_request_ride():
    """Book a Lyft Healthcare ride for a member."""
    data = request.get_json(force=True) or {}
    required = ["ride_type", "origin_lat", "origin_lng", "destination_lat", "destination_lng",
                "origin_address", "destination_address", "passenger_name", "passenger_phone"]
    missing = [f for f in required if not data.get(f) and data.get(f) != 0]
    if missing:
        return jsonify({"error": f"Missing: {', '.join(missing)}"}), 400
    c = get_lyft_healthcare_client()
    if not c.is_configured():
        return jsonify({"error": "Lyft Healthcare credentials not configured"}), 503
    status, payload = c.request_ride(
        ride_type=data["ride_type"],
        origin_lat=data["origin_lat"],
        origin_lng=data["origin_lng"],
        destination_lat=data["destination_lat"],
        destination_lng=data["destination_lng"],
        origin_address=data["origin_address"],
        destination_address=data["destination_address"],
        passenger_name=data["passenger_name"],
        passenger_phone=data["passenger_phone"],
        scheduled_at=data.get("scheduled_at"),
        notes=data.get("notes"),
    )
    return jsonify(payload), status


@prism_lyft_healthcare.route("/prism/lyft-healthcare/rides/<ride_id>", methods=["GET"])
def lyft_ride_status(ride_id: str):
    c = get_lyft_healthcare_client()
    if not c.is_configured():
        return jsonify({"error": "Lyft Healthcare credentials not configured"}), 503
    status, payload = c.get_ride_status(ride_id)
    return jsonify(payload), status


@prism_lyft_healthcare.route("/prism/lyft-healthcare/rides/<ride_id>/cancel", methods=["POST"])
def lyft_cancel_ride(ride_id: str):
    data = request.get_json(force=True) or {}
    c = get_lyft_healthcare_client()
    if not c.is_configured():
        return jsonify({"error": "Lyft Healthcare credentials not configured"}), 503
    status, payload = c.cancel_ride(ride_id, reason=data.get("reason"))
    return jsonify(payload), status


@prism_lyft_healthcare.route("/prism/lyft-healthcare/nemt-ride-types", methods=["GET"])
def lyft_nemt_types():
    """Show which PRISM transport types map to which Lyft ride types."""
    return jsonify({
        "mapping": NEMT_TYPE_TO_LYFT,
        "lyft_ride_types": LYFT_RIDE_TYPES,
        "note": "Stretcher transport cannot be fulfilled by Lyft — use a dedicated medical transport sub.",
    })
