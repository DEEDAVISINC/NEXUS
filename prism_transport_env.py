#!/usr/bin/env python3
"""
PRISM — shared transport partner environment (Uber Health, Lyft, future).
============================================================================
Read-only helpers for NEXUS/PRISM. Credentials stay in .env (never commit).

Lyft API integration is not wired yet; use these names when building it.
"""

from __future__ import annotations

import os
from typing import Any, Dict

from dotenv import load_dotenv

load_dotenv()


def get_lyft_env() -> Dict[str, Any]:
    """Lyft Concierge / Business API placeholders (values from .env)."""
    cid = os.environ.get("LYFT_CLIENT_ID", "").strip()
    csec = os.environ.get("LYFT_CLIENT_SECRET", "").strip()
    pending = cid.lower() == "pending" or csec.lower() == "pending"
    return {
        "org_id": os.environ.get("LYFT_ORG_ID", "").strip(),
        "client_id": cid,
        "client_secret": csec,
        "credentials_pending": pending or not cid or not csec,
    }


def lyft_configured_for_api() -> bool:
    """True when Lyft client id/secret look like real values (not placeholders)."""
    e = get_lyft_env()
    if e["credentials_pending"]:
        return False
    return bool(e["client_id"] and e["client_secret"])
