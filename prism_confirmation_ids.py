"""
PRISM Confirmation & Exemption ID System
========================================

Member-facing confirmation numbers:
  {CONTRACT#}-DDI-{LANE}-{YYYYMMDD}-{SEQ4}-{CHK}

  CONTRACT# = DDI MCO/contract sequence (1=HAP CareSource, 2=BCBSM, …)
  LANE      = population lane (MOB-A, MOB-B, MOB-C, MOB-E, TPA-1 … TPA-9)
  Example:  1-DDI-MOB-A-20260607-0042-7

Staff exemption codes (rotating, hashed at rest, per MCO + program):
  EX-{CONTRACT#}-{LANE}-{YYYY}Q{Q}-{TYPE}-{RAND6}
  Example: EX-1-MOB-A-2026Q2-WVR-K7M3P9  (HAP CareSource · Plan NEMT)
  MCO-wide: EX-1-ALL-2026Q2-EXM-XXXXXX
  Legacy (migration): EX-{YYYY}Q{Q}-{TYPE}-{RAND6}

Env:
  PRISM_EXEMPTION_PEPPER        HMAC secret for code hashing
  PRISM_EXEMPTION_ADMIN_KEY     Bearer token for rotate/generate admin endpoints
  PRISM_EXEMPTION_ROTATION_DAYS Default 90 (quarterly)
"""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
import os
import re
import secrets
import string
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from zoneinfo import ZoneInfo

logger = logging.getLogger("prism.confirmation")

EASTERN = ZoneInfo("America/Detroit")

_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads", "prism")
_SEQ_FILE = os.path.join(_DATA_DIR, "confirmation_sequences.json")
_EXEMPT_FILE = os.path.join(_DATA_DIR, "exemption_codes.json")
_EXEMPT_AUDIT_FILE = os.path.join(_DATA_DIR, "exemption_audit.json")

LANE_TOKEN_RE = re.compile(r"^(?:MOB-[ABCE]|TPA-[1-9]|NAV-[A-Z0-9])$")

# DDI contract / MCO sequence — order secured (NOT claims payer ID on Availity)
CONTRACT_PAYER_REGISTRY: Dict[int, Dict[str, Any]] = {
    0: {
        "slug": "direct",
        "name": "DDI Direct / Non-MCO",
        "aliases": ["direct", "ddi direct", "non-mco", "commercial"],
    },
    1: {
        "slug": "hap_caresource",
        "name": "HAP CareSource",
        "aliases": ["hap", "caresource", "hap caresource", "health alliance plan"],
    },
    2: {
        "slug": "bcbsm",
        "name": "Blue Cross Complete / BCBSM",
        "aliases": ["bcbsm", "blue cross complete", "bcc", "blue cross complete of michigan"],
    },
    # 3: Molina — assign when contract executed
    # 4: Priority Health
    # 5: UnitedHealthcare Community Plan
    # 6: Aetna Better Health Michigan
}

CONFIRMATION_RE = re.compile(
    r"^(?P<payer>\d+)-DDI-(?P<lane>(?:MOB-[ABCE]|TPA-[1-9]|NAV-[A-Z0-9]))-(?P<date>\d{8})-(?P<seq>\d{4})-(?P<chk>\d)$"
)
# Migration: prior build included channel letter (V/W/P)
LEGACY_DDI_WITH_CH_RE = re.compile(
    r"^DDI-(?P<lane>(?:MOB-[ABCE]|TPA-[1-9]|NAV-[A-Z0-9]))-(?P<ch>[A-Z])-(?P<date>\d{8})-(?P<seq>\d{4})-(?P<chk>\d)$"
)
LEGACY_DDI_RE = re.compile(
    r"^DDI-(?P<lane>[A-Z0-9]{3})-(?P<ch>[A-Z])-(?P<date>\d{8})-(?P<seq>\d{4})-(?P<chk>\d)$"
)
LEGACY_RE = re.compile(r"^PRISM(-V)?-", re.I)
EXEMPTION_LANE_TOKEN = r"(?:MOB-[ABCE]|TPA-[1-9]|NAV-[A-Z0-9]|ALL)"
EXEMPTION_SCOPED_RE = re.compile(
    rf"^EX-(?P<payer>\d+)-(?P<lane>{EXEMPTION_LANE_TOKEN})-(?P<period>\d{{4}}Q[1-4])-(?P<typ>[A-Z]{{3}})-(?P<rand>[A-Z0-9]{{6}})$"
)
EXEMPTION_LEGACY_RE = re.compile(
    r"^EX-(?P<period>\d{4}Q[1-4])-(?P<typ>[A-Z]{3})-(?P<rand>[A-Z0-9]{6})$"
)

# Default scopes to rotate when ops runs first-time setup (HAP live + enterprise)
DEFAULT_EXEMPTION_SCOPES: List[Dict[str, Any]] = [
    {"contract_payer_id": 1, "lane": "MOB-A", "label": "HAP CareSource · Plan NEMT"},
    {"contract_payer_id": 1, "lane": "ALL", "label": "HAP CareSource · all programs"},
    {"contract_payer_id": 0, "lane": "ALL", "label": "DDI Direct · enterprise ops"},
]

SERVICE_TO_LANE: Dict[str, str] = {
    "nemt": "MOB-A",
    "transport": "MOB-A",
    "medical_courier": "MOB-A",
    "dot": "TPA-1",
    "phlebotomy": "TPA-1",
    "poct": "TPA-1",
    "lead": "TPA-1",
    "fingerprint": "TPA-2",
    "dna": "TPA-3",
    "notary": "TPA-4",
    "notary-law-firm": "TPA-4",
    "apostille": "TPA-4",
    "courier": "MOB-C",
    "freight": "MOB-C",
    "background": "TPA-7",
    "credentialing": "TPA-8",
    "workforce": "TPA-9",
    "navigation": "NAV-G",
    "benefits": "NAV-G",
    "event": "MOB-E",
    "event_mobility": "MOB-E",
    "haven": "MOB-B",
    "haven_transport": "MOB-B",
}

LANE_DESCRIPTIONS: Dict[str, str] = {
    "MOB-A": "Plan NEMT — enrolled members, authorized medical trips",
    "MOB-B": "HAVEN continuity transport — displaced members, disaster mobility",
    "MOB-C": "Freight & logistics — cargo, agencies, owner-operators",
    "MOB-E": "Event mobility — venues, conferences, attendee PUDO",
    "TPA-1": "Drug testing & occupational compliance",
    "TPA-2": "Identity & biometric credentialing",
    "TPA-3": "DNA & relationship testing",
    "TPA-4": "Notary & document services",
    "TPA-7": "Background screening",
    "TPA-8": "Medical credentialing",
    "TPA-9": "Workforce compliance",
    "NAV-G": "Navigation & SDOH — benefits enrollment",
}

CHANNEL_CODES: Dict[str, str] = {
    "voice": "V",
    "web": "W",
    "portal": "P",
    "agent": "A",
    "api": "X",
    "law_firm": "L",
    "sms": "S",
    "email": "E",
}

EXEMPTION_TYPES: Dict[str, str] = {
    "WVR": "Fee waiver — management authorized",
    "EXM": "Billing exempt — contract / MCO / government",
    "EXP": "Expedited / STAT handling",
    "OPS": "Internal ops bypass",
    "VIP": "Priority client handling",
}

DEFAULT_EXEMPTION_MAX_USES = {
    "WVR": 25,
    "EXM": 100,
    "EXP": 50,
    "OPS": 200,
    "VIP": 30,
}


def _ensure_dir() -> None:
    os.makedirs(_DATA_DIR, exist_ok=True)


def _load(path: str, default: Any) -> Any:
    _ensure_dir()
    if not os.path.isfile(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def _save(path: str, data: Any) -> None:
    _ensure_dir()
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)
    os.replace(tmp, path)


def _pepper() -> bytes:
    raw = (
        os.environ.get("PRISM_EXEMPTION_PEPPER")
        or os.environ.get("JWT_SECRET")
        or "prism-dev-pepper-change-in-production"
    )
    return raw.encode("utf-8")


def _check_digit(payload: str) -> str:
    total = 0
    for i, ch in enumerate(payload.replace("-", "")):
        if ch.isdigit():
            total += int(ch) * (i + 1)
        elif ch.isalpha():
            total += (ord(ch.upper()) - 55) * (i + 1)
    return str(total % 10)


def resolve_contract_payer_id(
    *,
    contract_payer_id: Optional[int] = None,
    payer_name: Optional[str] = None,
    client_company: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    service_key: Optional[str] = None,
) -> int:
    """
    Resolve DDI contract # for confirmation prefix.
    1 = HAP CareSource (first live MCO contract). 2 = BCBSM when secured.
    """
    details = details or {}

    explicit = contract_payer_id or details.get("contract_payer_id") or details.get("mco_contract_id")
    if explicit is not None:
        try:
            pid = int(explicit)
            if pid in CONTRACT_PAYER_REGISTRY:
                return pid
        except (TypeError, ValueError):
            pass

    haystack = " ".join(
        filter(
            None,
            [
                payer_name or "",
                client_company or "",
                details.get("payer", ""),
                details.get("mco", ""),
                details.get("program_type", ""),
            ],
        )
    ).lower()

    for pid, info in CONTRACT_PAYER_REGISTRY.items():
        if pid == 0:
            continue
        for alias in info.get("aliases", []):
            if alias in haystack:
                return pid

    # Live HAP voice line / default NEMT until multi-MCO routing selects payer
    if (service_key or "").lower() in ("nemt", "transport") or details.get("mobility_lane") == "MOB-A":
        return 1

    return 0


def contract_payer_label(payer_id: int) -> str:
    return CONTRACT_PAYER_REGISTRY.get(payer_id, {}).get("name", f"Contract {payer_id}")


def resolve_lane_code(
    service_key: str,
    details: Optional[Dict[str, Any]] = None,
    *,
    mobility_lane: Optional[str] = None,
) -> str:
    """Map intake to DDI population lane (MOB-A/B/C/E, TPA-1…9, NAV-G)."""
    details = details or {}
    explicit = (mobility_lane or details.get("mobility_lane") or "").strip().upper()
    if explicit and LANE_TOKEN_RE.match(explicit):
        return explicit

    program = (details.get("program_type") or details.get("program") or "").lower()
    if "haven" in program or details.get("haven_mode") or details.get("havens_mode"):
        return "MOB-B"

    return SERVICE_TO_LANE.get((service_key or "").strip().lower(), "MOB-A")


def channel_code(channel: Optional[str]) -> str:
    return CHANNEL_CODES.get((channel or "web").strip().lower(), "W")


def parse_confirmation_id(ref: str) -> Optional[Dict[str, str]]:
    ref = (ref or "").strip().upper()
    m = CONFIRMATION_RE.match(ref)
    if m:
        parts = m.groupdict()
        body = f"{parts['payer']}-DDI-{parts['lane']}-{parts['date']}-{parts['seq']}"
        if _check_digit(body) != parts["chk"]:
            return None
        return parts

    m = LEGACY_DDI_WITH_CH_RE.match(ref) or LEGACY_DDI_RE.match(ref)
    if m:
        parts = m.groupdict()
        body = f"DDI-{parts['lane']}-{parts['ch']}-{parts['date']}-{parts['seq']}"
        if _check_digit(body) != parts["chk"]:
            return None
        parts["payer"] = None
        return parts

    return None


def validate_confirmation_format(ref: str) -> bool:
    if parse_confirmation_id(ref):
        return True
    return bool(LEGACY_RE.match((ref or "").strip()))


def is_legacy_confirmation(ref: str) -> bool:
    return bool(LEGACY_RE.match((ref or "").strip())) and not parse_confirmation_id(ref)


def _next_sequence(payer_id: int, lane: str, day: str) -> int:
    data = _load(_SEQ_FILE, {})
    key = f"{day}:{payer_id}:{lane}"
    seq = int(data.get(key, 0)) + 1
    if seq > 9999:
        seq = 1
    data[key] = seq
    _save(_SEQ_FILE, data)
    return seq


def generate_confirmation_id(
    service_key: str,
    channel: Optional[str] = None,
    *,
    when: Optional[datetime] = None,
    details: Optional[Dict[str, Any]] = None,
    mobility_lane: Optional[str] = None,
    contract_payer_id: Optional[int] = None,
    payer_name: Optional[str] = None,
    client_company: Optional[str] = None,
) -> str:
    now = when or datetime.now(EASTERN)
    details = dict(details or {})
    if channel:
        details.setdefault("_intake_channel", channel_code(channel))
    lane = resolve_lane_code(service_key, details, mobility_lane=mobility_lane)
    payer_id = resolve_contract_payer_id(
        contract_payer_id=contract_payer_id,
        payer_name=payer_name,
        client_company=client_company,
        details=details,
        service_key=service_key,
    )
    day = now.strftime("%Y%m%d")
    seq = _next_sequence(payer_id, lane, day)
    body = f"{payer_id}-DDI-{lane}-{day}-{seq:04d}"
    return f"{body}-{_check_digit(body)}"


def confirmation_display_meta(ref: str, *, channel: Optional[str] = None) -> Dict[str, Any]:
    parsed = parse_confirmation_id(ref)
    if not parsed:
        return {"ref": ref, "format": "legacy" if is_legacy_confirmation(ref) else "unknown"}
    ch_rev = {v: k for k, v in CHANNEL_CODES.items()}
    lane = parsed["lane"]
    payer_raw = parsed.get("payer")
    payer_id = int(payer_raw) if payer_raw else None
    ch_code = parsed.get("ch") or channel
    meta: Dict[str, Any] = {
        "ref": ref,
        "format": "ddi_contract_lane" if payer_id is not None else "ddi_structured_legacy",
        "contract_payer_id": payer_id,
        "contract_payer_name": contract_payer_label(payer_id) if payer_id is not None else None,
        "population_lane": lane,
        "lane_description": LANE_DESCRIPTIONS.get(lane, lane),
        "date": parsed["date"],
        "sequence": parsed["seq"],
        "check_digit": parsed["chk"],
    }
    if ch_code:
        meta["channel"] = ch_rev.get(ch_code, ch_code) if len(str(ch_code)) == 1 else ch_code
    return meta


def lookup_confirmation_public(
    ref: str,
    orders: List[Dict[str, Any]],
    *,
    phone_last4: Optional[str] = None,
) -> Dict[str, Any]:
    ref = (ref or "").strip()
    order = next((o for o in orders if o.get("id") == ref or o.get("confirmation_ref") == ref), None)
    if not order:
        return {"found": False, "message": "Confirmation not found."}

    voice = order.get("channel") == "voice" or (order.get("details") or {}).get("intake_channel") == "voice_ai"
    if voice:
        stored_last4 = (order.get("details") or {}).get("confirmation_phone_last4", "")
        if stored_last4 and phone_last4:
            if re.sub(r"\D", "", phone_last4)[-4:] != stored_last4:
                return {"found": False, "message": "Confirmation not found."}
        elif stored_last4 and not phone_last4:
            return {
                "found": True,
                "requires_verification": True,
                "message": "Enter the last four digits of the phone number used when booking.",
            }

    return {
        "found": True,
        "ref": ref,
        "status": order.get("status", "Unknown"),
        "service": order.get("service_label") or order.get("type", ""),
        "date": order.get("date", ""),
        "time": order.get("time", ""),
        "meta": confirmation_display_meta(ref),
    }


def _hash_exemption(plain: str) -> str:
    return hmac.new(_pepper(), plain.strip().upper().encode("utf-8"), hashlib.sha256).hexdigest()


def _current_period(when: Optional[datetime] = None) -> str:
    now = when or datetime.now(EASTERN)
    q = (now.month - 1) // 3 + 1
    return f"{now.year}Q{q}"


def _period_end(period: str) -> str:
    year = int(period[:4])
    q = int(period[-1])
    end_month = q * 3
    if end_month == 12:
        end = datetime(year, 12, 31, tzinfo=EASTERN)
    else:
        end = datetime(year, end_month + 1, 1, tzinfo=EASTERN) - timedelta(days=1)
    return end.date().isoformat()


def _rand_suffix(n: int = 6) -> str:
    alphabet = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(n))


def exemption_lane_token(lane: Optional[str]) -> str:
    token = (lane or "ALL").strip().upper()
    if token == "ALL":
        return "ALL"
    if LANE_TOKEN_RE.match(token):
        return token
    return "ALL"


def exemption_scope_key(contract_payer_id: int, lane: str) -> str:
    return f"{int(contract_payer_id)}:{exemption_lane_token(lane)}"


def parse_exemption_code(plain: str) -> Optional[Dict[str, str]]:
    code = (plain or "").strip().upper()
    m = EXEMPTION_SCOPED_RE.match(code)
    if m:
        parts = dict(m.groupdict())
        parts["format"] = "scoped"
        return parts
    m = EXEMPTION_LEGACY_RE.match(code)
    if m:
        parts = dict(m.groupdict())
        parts["format"] = "legacy"
        parts["payer"] = None
        parts["lane"] = None
        return parts
    return None


def _scope_matches_request(
    entry: Dict[str, Any],
    *,
    contract_payer_id: Optional[int] = None,
    lane: Optional[str] = None,
) -> bool:
    """Code must belong to the order's MCO/program (or MCO-wide ALL lane)."""
    if contract_payer_id is None and not lane:
        return True

    ep = entry.get("contract_payer_id")
    el = (entry.get("lane") or "").upper()
    if ep is None and not el:
        return True  # legacy global — honored during migration

    req_payer = int(contract_payer_id) if contract_payer_id is not None else None
    req_lane = exemption_lane_token(lane) if lane else None

    if req_payer is not None and ep is not None and int(ep) != req_payer:
        return False
    if req_lane and el and el not in ("ALL", req_lane):
        return False
    return True


def _load_exemption_registry() -> Dict[str, Any]:
    reg = _load(_EXEMPT_FILE, {})
    if not reg.get("period"):
        reg = {"period": _current_period(), "expires": _period_end(_current_period()), "codes": []}
        _save(_EXEMPT_FILE, reg)
    return reg


def _active_codes_by_scope(reg: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
    grouped: Dict[str, List[Dict[str, Any]]] = {}
    for c in reg.get("codes", []):
        if not c.get("active"):
            continue
        scope = c.get("scope") or exemption_scope_key(
            int(c.get("contract_payer_id", 0)),
            c.get("lane") or "ALL",
        )
        grouped.setdefault(scope, []).append(c)
    return grouped


def exemption_status(*, contract_payer_id: Optional[int] = None, lane: Optional[str] = None) -> Dict[str, Any]:
    reg = _load_exemption_registry()
    grouped = _active_codes_by_scope(reg)
    scopes_out: List[Dict[str, Any]] = []
    for scope, codes in sorted(grouped.items()):
        payer_s, lane_s = scope.split(":", 1)
        pid = int(payer_s)
        if contract_payer_id is not None and pid != int(contract_payer_id):
            continue
        if lane and lane_s not in (exemption_lane_token(lane), "ALL"):
            continue
        scopes_out.append(
            {
                "scope": scope,
                "contract_payer_id": pid,
                "contract_payer_name": contract_payer_label(pid),
                "lane": lane_s,
                "lane_description": LANE_DESCRIPTIONS.get(lane_s, "All programs under contract" if lane_s == "ALL" else lane_s),
                "active_code_count": len(codes),
                "types_active": sorted({c.get("type") for c in codes if c.get("type")}),
            }
        )

    active = [c for c in reg.get("codes", []) if c.get("active")]
    return {
        "period": reg.get("period"),
        "expires": reg.get("expires"),
        "active_code_count": len(active),
        "scopes": scopes_out,
        "default_scopes": DEFAULT_EXEMPTION_SCOPES,
        "types": list(EXEMPTION_TYPES.keys()),
        "rotation_days": int(os.environ.get("PRISM_EXEMPTION_ROTATION_DAYS", "90")),
        "next_rotation_recommended": reg.get("expires"),
    }


def _audit_exemption(event: str, detail: Dict[str, Any]) -> None:
    log = _load(_EXEMPT_AUDIT_FILE, [])
    log.insert(0, {"at": datetime.now(EASTERN).isoformat(), "event": event, **detail})
    _save(_EXEMPT_AUDIT_FILE, log[:500])


def validate_exemption_code(
    plain: str,
    *,
    email: str = "",
    context: str = "",
    contract_payer_id: Optional[int] = None,
    lane: Optional[str] = None,
    mobility_lane: Optional[str] = None,
) -> Dict[str, Any]:
    code = (plain or "").strip().upper()
    if not code:
        return {"valid": False, "message": "Exemption code required."}

    parsed = parse_exemption_code(code)
    if not parsed:
        return {"valid": False, "message": f'Code "{code}" format not recognized.'}

    req_lane = mobility_lane or lane
    if contract_payer_id is None and parsed.get("payer") is not None:
        contract_payer_id = int(parsed["payer"])

    reg = _load_exemption_registry()
    today = datetime.now(EASTERN).date().isoformat()
    if reg.get("expires") and today > reg["expires"]:
        return {
            "valid": False,
            "message": "Exemption period expired — request a current code from DDI ops.",
            "period_expired": True,
        }

    code_hash = _hash_exemption(code)
    candidates = [
        c for c in reg.get("codes", []) if c.get("hash") == code_hash and c.get("active")
    ]
    entry = next(
        (
            c
            for c in candidates
            if _scope_matches_request(
                c,
                contract_payer_id=contract_payer_id,
                lane=req_lane,
            )
        ),
        None,
    )
    if not entry:
        if candidates:
            msg = "This exemption code is not valid for this MCO/program."
        else:
            msg = f'Code "{code}" not recognized or inactive.'
        _audit_exemption(
            "rejected",
            {
                "code_prefix": code[:20],
                "email": email,
                "context": context,
                "contract_payer_id": contract_payer_id,
                "lane": req_lane,
            },
        )
        return {"valid": False, "message": msg, "scope_mismatch": bool(candidates)}

    uses = int(entry.get("uses", 0))
    max_uses = int(entry.get("max_uses", 50))
    if uses >= max_uses:
        return {"valid": False, "message": "This exemption code has reached its use limit."}

    entry["uses"] = uses + 1
    entry["last_used"] = datetime.now(EASTERN).isoformat()
    _save(_EXEMPT_FILE, reg)
    _audit_exemption(
        "accepted",
        {
            "type": entry.get("type"),
            "scope": entry.get("scope"),
            "email": email,
            "context": context,
            "uses": entry["uses"],
        },
    )

    typ = entry.get("type", "OPS")
    ep = entry.get("contract_payer_id")
    el = entry.get("lane")
    return {
        "valid": True,
        "code": code,
        "type": typ.lower(),
        "exemption_type": typ,
        "source": "rotating_exemption",
        "contract_payer_id": ep,
        "contract_payer_name": contract_payer_label(int(ep)) if ep is not None else None,
        "lane": el,
        "scope": entry.get("scope"),
        "message": EXEMPTION_TYPES.get(typ, "Exemption accepted."),
        "uses_remaining": max(0, max_uses - entry["uses"]),
    }


def _normalize_rotate_scopes(
    *,
    contract_payer_id: Optional[int] = None,
    lane: Optional[str] = None,
    scopes: Optional[List[Dict[str, Any]]] = None,
    setup_defaults: bool = False,
) -> List[Dict[str, Any]]:
    if setup_defaults:
        return [dict(s) for s in DEFAULT_EXEMPTION_SCOPES]
    if scopes:
        out: List[Dict[str, Any]] = []
        for s in scopes:
            pid = int(s.get("contract_payer_id", 0))
            if pid not in CONTRACT_PAYER_REGISTRY:
                continue
            out.append(
                {
                    "contract_payer_id": pid,
                    "lane": exemption_lane_token(s.get("lane")),
                    "label": s.get("label") or contract_payer_label(pid),
                }
            )
        return out
    if contract_payer_id is not None:
        pid = int(contract_payer_id)
        if pid not in CONTRACT_PAYER_REGISTRY:
            return []
        return [
            {
                "contract_payer_id": pid,
                "lane": exemption_lane_token(lane or ("MOB-A" if pid == 1 else "ALL")),
                "label": contract_payer_label(pid),
            }
        ]
    return []


def rotate_exemption_codes(
    *,
    period: Optional[str] = None,
    types: Optional[List[str]] = None,
    contract_payer_id: Optional[int] = None,
    lane: Optional[str] = None,
    scopes: Optional[List[Dict[str, Any]]] = None,
    setup_defaults: bool = False,
    deactivate_previous: bool = True,
) -> Dict[str, Any]:
    period = period or _current_period()
    types = types or list(EXEMPTION_TYPES.keys())
    scope_list = _normalize_rotate_scopes(
        contract_payer_id=contract_payer_id,
        lane=lane,
        scopes=scopes,
        setup_defaults=setup_defaults,
    )
    if not scope_list:
        return {
            "error": "Specify contract_payer_id + lane, scopes[], or setup_defaults=true",
            "example_scoped_code": "EX-1-MOB-A-2026Q2-WVR-K7M3P9",
        }

    reg = _load_exemption_registry()
    target_scopes = {exemption_scope_key(s["contract_payer_id"], s["lane"]) for s in scope_list}

    if deactivate_previous:
        for c in reg.get("codes", []):
            cscope = c.get("scope") or exemption_scope_key(
                int(c.get("contract_payer_id", 0)),
                c.get("lane") or "ALL",
            )
            if cscope in target_scopes:
                c["active"] = False

    plaintext_codes: Dict[str, Dict[str, str]] = {}
    new_entries: List[Dict[str, Any]] = []

    for scope_def in scope_list:
        pid = int(scope_def["contract_payer_id"])
        lane_token = exemption_lane_token(scope_def["lane"])
        scope = exemption_scope_key(pid, lane_token)
        plaintext_codes[scope] = {}

        for typ in types:
            typ = typ.upper()
            if typ not in EXEMPTION_TYPES:
                continue
            plain = f"EX-{pid}-{lane_token}-{period}-{typ}-{_rand_suffix()}"
            plaintext_codes[scope][typ] = plain
            new_entries.append(
                {
                    "hash": _hash_exemption(plain),
                    "type": typ,
                    "period": period,
                    "contract_payer_id": pid,
                    "lane": lane_token,
                    "scope": scope,
                    "max_uses": DEFAULT_EXEMPTION_MAX_USES.get(typ, 50),
                    "uses": 0,
                    "active": True,
                    "created": datetime.now(EASTERN).isoformat(),
                }
            )

    reg["period"] = period
    reg["expires"] = _period_end(period)
    reg.setdefault("codes", [])
    reg["codes"] = new_entries + reg["codes"]
    _save(_EXEMPT_FILE, reg)
    _audit_exemption(
        "rotated",
        {"period": period, "types": types, "scopes": sorted(target_scopes)},
    )

    return {
        "period": period,
        "expires": reg["expires"],
        "scopes_rotated": [
            {
                "scope": exemption_scope_key(s["contract_payer_id"], s["lane"]),
                "contract_payer_id": s["contract_payer_id"],
                "contract_payer_name": contract_payer_label(int(s["contract_payer_id"])),
                "lane": exemption_lane_token(s["lane"]),
                "label": s.get("label"),
            }
            for s in scope_list
        ],
        "codes": plaintext_codes,
        "codes_flat": {f"{scope}:{typ}": val for scope, by_typ in plaintext_codes.items() for typ, val in by_typ.items()},
        "message": "Store these codes securely — they cannot be retrieved again.",
    }


def admin_authorized(auth_header: Optional[str]) -> bool:
    expected = (os.environ.get("PRISM_EXEMPTION_ADMIN_KEY") or "").strip()
    if not expected or not auth_header:
        return False
    token = auth_header.replace("Bearer", "").strip()
    return hmac.compare_digest(token, expected)


def format_schema_public() -> Dict[str, Any]:
    return {
        "confirmation_format": "{CONTRACT#}-DDI-{LANE}-{YYYYMMDD}-{SEQ4}-{CHK}",
        "confirmation_example": "1-DDI-MOB-A-20260607-0042-7",
        "contract_payer_registry": {
            str(k): v["name"] for k, v in CONTRACT_PAYER_REGISTRY.items()
        },
        "population_lanes": LANE_DESCRIPTIONS,
        "service_to_lane_default": SERVICE_TO_LANE,
        "channel_codes": CHANNEL_CODES,
        "channel_note": "Channel (V/W/P) stored on order metadata — not in public confirmation string.",
        "exemption_format": "EX-{CONTRACT#}-{LANE}-{YYYY}Q{Q}-{TYPE}-{RAND6}",
        "exemption_example": "EX-1-MOB-A-2026Q2-WVR-K7M3P9",
        "exemption_example_mco_wide": "EX-1-ALL-2026Q2-EXM-K7M3P9",
        "exemption_legacy_format": "EX-{YYYY}Q{Q}-{TYPE}-{RAND6}",
        "exemption_lane_note": "Use ALL for MCO-wide codes; MOB-A/TPA-1/etc. for program-specific.",
        "exemption_default_scopes": DEFAULT_EXEMPTION_SCOPES,
        "exemption_types": EXEMPTION_TYPES,
        "lane_reference": "NEXUS_LEARNING/DDI_SERVICE_POPULATION_LANES.md",
        "fraud_controls": [
            "Check digit on every confirmation number",
            "Daily sequence per contract payer + population lane",
            "Contract # identifies which MCO/agreement (1=HAP, 2=BCBSM, …)",
            "Exemption codes scoped per contract + program lane (EX-1-MOB-A-…)",
            "MCO-wide codes use ALL lane (EX-1-ALL-…)",
            "Exemption codes stored hashed — plaintext shown once at rotation",
            "Exemption period expiry (default quarterly)",
            "Per-code use limits with audit log",
            "Validation rejects wrong MCO/program scope",
            "Public status lookup requires phone last-4 for voice bookings",
            "Legacy PRISM-* and DDI-* refs still honored during migration",
        ],
    }
