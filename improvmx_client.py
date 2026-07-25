#!/usr/bin/env python3
"""
ImprovMX API client — email alias management for deedavis.biz
================================================================
Single source of truth for creating/updating/looking up email forwarding
aliases on the deedavis.biz domain. deedavis.biz uses ImprovMX for ALL
email — there are no hosted mailboxes, every alias (info@, gc@, qc@,
apar@, hr@, etc.) is forward-only. This module is that same mechanism,
made reusable so any NEXUS module (GATEWAY employee onboarding, GPSS
subcontractor onboarding, future modules) can provision a deedavis.biz
alias without hand-rolling curl calls again.

Auth: HTTP Basic, username "api", password = IMPROVMX_API_KEY (see .env).
Docs: https://improvmx.com/api/

IMPORTANT — API quirk discovered Jul 2026: the ImprovMX v3 API rejects
form-encoded PUT bodies with a bare 400 error. Always send JSON
(Content-Type: application/json). This module handles that correctly;
don't "simplify" it back to form-encoded data.
"""

import os
import re
import requests

IMPROVMX_BASE = "https://api.improvmx.com/v3"
DOMAIN = "deedavis.biz"
_TIMEOUT = 15


def _auth():
    key = os.environ.get("IMPROVMX_API_KEY", "")
    return ("api", key)


def _configured():
    return bool(os.environ.get("IMPROVMX_API_KEY"))


def get_domain_aliases():
    """Returns (aliases_list, error). aliases_list is a list of dicts:
    {'alias': 'gc', 'forward': 'ops.ddinc@gmail.com', 'id': 123, 'created': ...}
    On any failure, returns ([], error_message) — callers should treat an
    error here as "assume nothing, don't block the caller's real task."
    """
    if not _configured():
        return [], "IMPROVMX_API_KEY not set in .env"
    try:
        resp = requests.get(
            f"{IMPROVMX_BASE}/domains/{DOMAIN}",
            auth=_auth(), timeout=_TIMEOUT,
        )
        data = resp.json()
        if not data.get("success"):
            return [], data.get("error", f"HTTP {resp.status_code}")
        return data.get("domain", {}).get("aliases", []), None
    except Exception as e:
        return [], str(e)


def get_alias_map():
    """local-part (lowercase) -> forward address, for collision checks."""
    aliases, err = get_domain_aliases()
    if err:
        return {}, err
    return {a["alias"].lower(): a.get("forward", "") for a in aliases}, None


def create_alias(local_part, forward_to):
    """Create a new alias. Returns (success, alias_id_or_error_message)."""
    if not _configured():
        return False, "IMPROVMX_API_KEY not set in .env"
    try:
        resp = requests.post(
            f"{IMPROVMX_BASE}/domains/{DOMAIN}/aliases",
            auth=_auth(), timeout=_TIMEOUT,
            headers={"Content-Type": "application/json"},
            json={"alias": local_part, "forward": forward_to},
        )
        data = resp.json()
        if not data.get("success"):
            return False, data.get("error", f"HTTP {resp.status_code}")
        return True, data.get("alias", {}).get("id")
    except Exception as e:
        return False, str(e)


def update_alias(alias_id, forward_to):
    """Update an existing alias's forward address. JSON body — see module
    docstring, form-encoded bodies return a bare 400 from this API."""
    if not _configured():
        return False, "IMPROVMX_API_KEY not set in .env"
    try:
        resp = requests.put(
            f"{IMPROVMX_BASE}/domains/{DOMAIN}/aliases/{alias_id}",
            auth=_auth(), timeout=_TIMEOUT,
            headers={"Content-Type": "application/json"},
            json={"forward": forward_to},
        )
        data = resp.json()
        if not data.get("success"):
            return False, data.get("error", f"HTTP {resp.status_code}")
        return True, data.get("alias", {})
    except Exception as e:
        return False, str(e)


def delete_alias(alias_id):
    """Not used by the GATEWAY flow (we redirect on offboarding, never
    delete — see hr_onboarding_api.py). Provided for completeness."""
    if not _configured():
        return False, "IMPROVMX_API_KEY not set in .env"
    try:
        resp = requests.delete(
            f"{IMPROVMX_BASE}/domains/{DOMAIN}/aliases/{alias_id}",
            auth=_auth(), timeout=_TIMEOUT,
        )
        data = resp.json()
        return bool(data.get("success")), data.get("error")
    except Exception as e:
        return False, str(e)


def slugify_name(full_name):
    """'Jane A. Doe' -> ('jane', 'doe'). Best-effort: takes the first token
    as first name and the last token as last name, strips punctuation and
    middle names/initials. Returns (first, last) lowercase, or (None, None)
    if it can't extract two usable parts."""
    if not full_name:
        return None, None
    cleaned = re.sub(r"[^A-Za-z\s\-']", " ", full_name).strip()
    parts = [p for p in cleaned.split() if p]
    if len(parts) < 2:
        return None, None
    first = re.sub(r"[^a-z]", "", parts[0].lower())
    last = re.sub(r"[^a-z]", "", parts[-1].lower())
    if not first or not last:
        return None, None
    return first, last


def next_available_alias(full_name, existing_map=None):
    """Generate a collision-safe deedavis.biz local-part for a person's
    name, convention firstname.lastname. If that's taken, tries
    firstname.lastname2, firstname.lastname3, etc.

    existing_map: optional pre-fetched dict from get_alias_map() to avoid
    an extra API round-trip when provisioning several people at once.

    Returns (local_part, error). local_part is None if the name couldn't
    be slugified or the alias map couldn't be fetched.
    """
    first, last = slugify_name(full_name)
    if not first or not last:
        return None, f"Could not derive first/last name from '{full_name}' — needs at least two name parts"

    if existing_map is None:
        existing_map, err = get_alias_map()
        if err:
            return None, f"Could not check existing aliases: {err}"

    base = f"{first}.{last}"
    if base not in existing_map:
        return base, None
    n = 2
    while f"{base}{n}" in existing_map:
        n += 1
    return f"{base}{n}", None


def provision_employee_alias(full_name, forward_to):
    """One-call convenience: derive a collision-safe alias for full_name
    and create it on deedavis.biz, forwarding to forward_to.

    Returns dict: {
        'success': bool,
        'companyEmail': 'jane.doe@deedavis.biz' or None,
        'error': str or None,
    }
    Never raises — every failure mode is a returned dict so callers
    (like GATEWAY onboarding) can proceed with the rest of the record
    creation even if email provisioning fails.
    """
    if not forward_to:
        return {"success": False, "companyEmail": None,
                "error": "No forwarding email on file — cannot provision an alias with nowhere to forward to"}

    local_part, err = next_available_alias(full_name)
    if err:
        return {"success": False, "companyEmail": None, "error": err}

    ok, result = create_alias(local_part, forward_to)
    if not ok:
        return {"success": False, "companyEmail": None, "error": result}

    return {"success": True, "companyEmail": f"{local_part}@{DOMAIN}", "error": None}
