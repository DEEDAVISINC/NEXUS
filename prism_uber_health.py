#!/usr/bin/env python3
"""
PRISM — Uber Health Rides API integration
==========================================
NEMT / coordinated transportation: OAuth client-credentials, trip estimates,
sandbox run simulation, and passthrough helpers for future PRISM order flows.

Secrets (set in environment or .env — never commit):
  UBER_HEALTH_CLIENT_ID
  UBER_HEALTH_CLIENT_SECRET
  UBER_HEALTH_ORG_ID      (sent as x-uber-organizationuuid when required)

Optional:
  UBER_HEALTH_TOKEN_URL   (default: https://login.uber.com/oauth/v2/token)

Legacy aliases still supported: UBER_CLIENT_ID, UBER_CLIENT_SECRET, UBER_ORG_UUID, UBER_TOKEN_URL.

OpenAPI source of truth: ESSENTIALS/uber_health_rides_openapi.json
"""

from __future__ import annotations

import os
import threading
import time
from typing import Any, Dict, Optional

import requests
from dotenv import load_dotenv
from flask import Blueprint, jsonify, request

load_dotenv()

prism_uber_health = Blueprint("prism_uber_health", __name__)


def _env_first(*names: str, default: str = "") -> str:
    """Return the first non-empty environment value among names."""
    for n in names:
        v = os.environ.get(n, "").strip()
        if v:
            return v
    return default


# --- Endpoints (from OpenAPI) ---
UBER_DEFAULT_TOKEN_URL = _env_first(
    "UBER_HEALTH_TOKEN_URL", "UBER_TOKEN_URL", default="https://login.uber.com/oauth/v2/token"
)
UBER_API_PRODUCTION = "https://api.uber.com/v1"
UBER_API_SANDBOX = "https://sandbox-api.uber.com/v1"

# Recommended SF sandbox coordinates (documented in Uber Health Rides API)
SANDBOX_SF_PICKUP = {"latitude": 37.766192, "longitude": -122.400745}
SANDBOX_SF_DROPOFF = {"latitude": 37.75203, "longitude": -122.422065}

# Parent product type IDs (UberX, etc.) — see OpenAPI schema SandboxRunRequest
PRODUCT_UBERX = "6a8e56b8-914e-4b48-a387-e6ad21d9c00c"


class UberHealthClient:
    """Client-credentials OAuth + cached bearer token."""

    def __init__(self) -> None:
        self._client_id = _env_first("UBER_HEALTH_CLIENT_ID", "UBER_CLIENT_ID")
        self._client_secret = _env_first(
            "UBER_HEALTH_CLIENT_SECRET", "UBER_CLIENT_SECRET"
        )
        self._token_url = UBER_DEFAULT_TOKEN_URL
        self._org_uuid = _env_first("UBER_HEALTH_ORG_ID", "UBER_ORG_UUID") or None
        self._lock = threading.Lock()
        self._access_token: Optional[str] = None
        self._expires_at: float = 0.0

    def is_configured(self) -> bool:
        return bool(self._client_id and self._client_secret)

    def _fetch_token(self) -> Dict[str, Any]:
        if not self.is_configured():
            raise RuntimeError(
                "UBER_HEALTH_CLIENT_ID and UBER_HEALTH_CLIENT_SECRET must be set "
                "(or legacy UBER_CLIENT_ID / UBER_CLIENT_SECRET)"
            )
        r = requests.post(
            self._token_url,
            timeout=45,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={
                "client_id": self._client_id,
                "client_secret": self._client_secret,
                "grant_type": "client_credentials",
                "scope": "health",
            },
        )
        r.raise_for_status()
        return r.json()

    def get_access_token(self, force_refresh: bool = False) -> str:
        with self._lock:
            now = time.time()
            if (
                not force_refresh
                and self._access_token
                and now < self._expires_at - 120
            ):
                return self._access_token
            data = self._fetch_token()
            token = data.get("access_token")
            if not token:
                raise RuntimeError("token response missing access_token")
            self._access_token = token
            exp = int(data.get("expires_in", 2592000))
            self._expires_at = now + max(exp, 60)
            return self._access_token

    def _headers(self, json_body: bool = True) -> Dict[str, str]:
        h: Dict[str, str] = {
            "Authorization": f"Bearer {self.get_access_token()}",
        }
        if json_body:
            h["Content-Type"] = "application/json"
        if self._org_uuid:
            h["x-uber-organizationuuid"] = self._org_uuid
        return h

    def create_sandbox_run(
        self,
        body: Optional[Dict[str, Any]] = None,
    ) -> tuple[int, Any]:
        """POST /health/sandbox/run — sandbox host only."""
        if body is None:
            body = default_sandbox_run_body()
        url = f"{UBER_API_SANDBOX}/health/sandbox/run"
        r = requests.post(url, json=body, headers=self._headers(), timeout=60)
        try:
            payload = r.json()
        except Exception:
            payload = {"raw": r.text}
        return r.status_code, payload

    def create_trip_estimate(self, body: Dict[str, Any]) -> tuple[int, Any]:
        """POST /health/trips/estimates — production API base."""
        url = f"{UBER_API_PRODUCTION}/health/trips/estimates"
        r = requests.post(url, json=body, headers=self._headers(), timeout=60)
        try:
            payload = r.json()
        except Exception:
            payload = {"raw": r.text}
        return r.status_code, payload

    def status_dict(self) -> Dict[str, Any]:
        return {
            "configured": self.is_configured(),
            "token_cached": bool(self._access_token),
            "expires_at_epoch": self._expires_at if self._expires_at else None,
            "org_uuid_set": bool(self._org_uuid),
            "sandbox_base": UBER_API_SANDBOX,
            "production_base": UBER_API_PRODUCTION,
        }


_client: Optional[UberHealthClient] = None


def get_uber_health_client() -> UberHealthClient:
    global _client
    if _client is None:
        _client = UberHealthClient()
    return _client


def default_sandbox_run_body() -> Dict[str, Any]:
    return {
        "driver_locations": [dict(SANDBOX_SF_PICKUP)],
        "pickup_location": dict(SANDBOX_SF_PICKUP),
        "dropoff_location": dict(SANDBOX_SF_DROPOFF),
        "parent_product_type_id": PRODUCT_UBERX,
        "preferences": {"auto_accept_trip": False},
    }


def on_demand_estimate_body(
    pickup_lat: float,
    pickup_lng: float,
    dropoff_lat: float,
    dropoff_lng: float,
) -> Dict[str, Any]:
    """OpenAPI OnDemandEstimateRequest uses pickup/dropoff (not *_location)."""
    return {
        "pickup": {"latitude": pickup_lat, "longitude": pickup_lng},
        "dropoff": {"latitude": dropoff_lat, "longitude": dropoff_lng},
    }


# --- HTTP routes (server-side token; do not expose secrets) ---


@prism_uber_health.route("/prism/uber-health/status", methods=["GET"])
def uber_health_status():
    """Return configuration and token cache state (no secrets)."""
    c = get_uber_health_client()
    return jsonify(c.status_dict())


@prism_uber_health.route("/prism/uber-health/sandbox/run", methods=["POST"])
def uber_health_sandbox_run():
    """
    Create a sandbox run. Optional JSON body; if empty, uses default SF test coordinates.
    """
    c = get_uber_health_client()
    if not c.is_configured():
        return jsonify({"error": "Uber Health credentials not configured"}), 503
    body = request.get_json(silent=True)
    if not body:
        body = default_sandbox_run_body()
    status, payload = c.create_sandbox_run(body)
    return jsonify(payload), status


@prism_uber_health.route("/prism/uber-health/trips/estimates", methods=["POST"])
def uber_health_trip_estimates():
    """
    Proxy to Create Health Trip Estimates (production API).
    Body must match OpenAPI OnDemandEstimateRequest (pickup/dropoff coordinates).
    """
    c = get_uber_health_client()
    if not c.is_configured():
        return jsonify({"error": "Uber Health credentials not configured"}), 503
    body = request.get_json(silent=True)
    if not body:
        return jsonify({"error": "JSON body required"}), 400
    status, payload = c.create_trip_estimate(body)
    return jsonify(payload), status
