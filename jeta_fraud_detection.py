"""
JETA — Fraud Detection & Deal Integrity (counterparty scoring, terminology blacklist,
stage gate catalog, dashboard alerts).

Used by api_server JETA routes. Scoring aligns with:
  0–2 flags → GREEN
  3–4 flags → YELLOW (manual review before proceeding)
  5+ flags → RED (blocked)
  Any CRITICAL → instant block regardless of count
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from jeta_compliance_layers import (
    _buyer_bool,
    _email_domain_is_consumer,
    find_jeta_blocked_term_findings,
)

# ─── NEXUS LEARNING ENGINE INTEGRATION ────────────────────────────────────────
try:
    from nexus_learning_engine import nxlearn
except ImportError:
    def nxlearn(*args, **kwargs):
        pass  # Graceful fallback if learning engine not available

# Re-export for callers that only need terminology scan
__all__ = [
    "score_counterparty_intake",
    "scan_deal_terminology_blacklist",
    "DEAL_STAGE_GATE_REQUIREMENTS",
    "build_jeta_dashboard_alerts",
    "evaluate_fraud_integrity_for_stage_transition",
]


def _tf(payload: Dict[str, Any], key: str) -> bool:
    return _buyer_bool(payload, key)


def _bad_product_blob(text: str) -> bool:
    if not text:
        return False
    cf = text.casefold()
    alnum = re.sub(r"[^a-z0-9]+", "", cf)
    if "jp54" in alnum or re.search(r"(?i)jp[\s\-]*54", text):
        return True
    if "mazut" in cf:
        return True
    if re.search(r"(?i)\b[Dd][26]\b", text) and re.search(
        r"(?i)(jet\s*fuel|\bjet[-\s]*a\b|aviation|turbine)", text
    ):
        return True
    return False


def _seller_red_flags(payload: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], bool]:
    """Returns (flags, critical)."""
    flags: List[Dict[str, Any]] = []
    critical = False

    blob = " ".join(
        str(payload.get(k) or "")
        for k in (
            "companyName",
            "contactName",
            "notes",
            "nextAction",
            "website",
            "sellerProductDescription",
        )
    )
    if _bad_product_blob(blob):
        flags.append(
            {"code": "SELLER_BAD_PRODUCT_TERM", "points": 1, "message": "Product or pitch text references JP54/JP-54/D6/D2 as jet or Mazut."}
        )

    legal = (payload.get("companyName") or "").strip()
    if len(legal) < 2:
        flags.append(
            {"code": "SELLER_NO_LEGAL_NAME", "points": 1, "message": "Company legal name missing or unusable."}
        )

    email = (payload.get("email") or "").strip()
    if email and _email_domain_is_consumer(email):
        flags.append(
            {"code": "SELLER_CONSUMER_EMAIL", "points": 1, "message": "Email uses a free/consumer domain (gmail/yahoo/hotmail-class)."}
        )

    notes = (payload.get("notes") or "").casefold()
    if "cannot disclose seller" in notes:
        flags.append(
            {"code": "SELLER_CANNOT_DISCLOSE_NOTES", "points": 1, "message": 'Notes contain "cannot disclose seller".'}
        )
        critical = True

    term = find_jeta_blocked_term_findings(blob)
    if term:
        critical = True
        for f in term:
            flags.append(
                {
                    "code": f.get("code", "BLACKLIST"),
                    "points": 0,
                    "critical": True,
                    "message": f.get("message", "Blocked terminology"),
                }
            )

    docs_ok = _tf(payload, "terminalStorageDocsUploaded")
    if not docs_ok:
        flags.append(
            {
                "code": "SELLER_NO_TERMINAL_STORAGE_DOCS",
                "points": 1,
                "message": "No terminal / storage documentation attested (terminalStorageDocsUploaded).",
            }
        )

    return flags, critical


def _buyer_red_flags(payload: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], bool]:
    flags: List[Dict[str, Any]] = []
    critical = False

    faa = (payload.get("faaRegistration") or "").strip()
    if len(faa) < 3:
        flags.append(
            {"code": "BUYER_NO_FAA", "points": 1, "message": "FAA registration / tail number not provided (faaRegistration)."}
        )

    if not _tf(payload, "aircraftOrFuelVerified") and not _tf(payload, "fuelConsumptionHistoryProvided"):
        flags.append(
            {
                "code": "BUYER_NO_FUEL_HISTORY", "points": 1,
                "message": "No fuel consumption history or aircraft/fuel verification (aircraftOrFuelVerified or fuelConsumptionHistoryProvided).",
            }
        )

    email = (payload.get("email") or "").strip()
    if email and _email_domain_is_consumer(email) and not _tf(payload, "businessEmailConfirmed"):
        flags.append(
            {"code": "BUYER_PERSONAL_EMAIL_ONLY", "points": 1, "message": "Personal / consumer email domain without business confirmation."}
        )

    if not _tf(payload, "aircraftOperationConfirmed") and not _tf(payload, "purchasingAuthorityConfirmed"):
        flags.append(
            {
                "code": "BUYER_AIRCRAFT_OP_UNCONFIRMED",
                "points": 1,
                "message": "Aircraft operation not confirmed (aircraftOperationConfirmed or purchasingAuthorityConfirmed).",
            }
        )

    blob = " ".join(str(payload.get(k) or "") for k in ("companyName", "notes", "nextAction", "email"))
    term = find_jeta_blocked_term_findings(blob)
    if term:
        critical = True
        for f in term:
            flags.append(
                {
                    "code": f.get("code", "BLACKLIST"),
                    "points": 0,
                    "critical": True,
                    "message": f.get("message", "Blocked terminology"),
                }
            )

    return flags, critical


def score_counterparty_intake(payload: Dict[str, Any], role: str) -> Dict[str, Any]:
    """
    role: 'seller' | 'buyer' (case-insensitive). Uses same camelCase keys as JETA buyer JSON.
    """
    r = (role or "buyer").strip().lower()
    if r in ("seller", "sell", "supplier"):
        flags, crit = _seller_red_flags(payload)
    else:
        flags, crit = _buyer_red_flags(payload)

    has_critical = crit or any(f.get("critical") for f in flags)
    non_crit = [f for f in flags if not f.get("critical")]
    tier_count = len(non_crit)

    if has_critical:
        tier = "CRITICAL_BLOCK"
        traffic = "red"
    elif tier_count >= 5:
        tier = "RED"
        traffic = "red"
    elif tier_count >= 3:
        tier = "YELLOW"
        traffic = "yellow"
    else:
        tier = "GREEN"
        traffic = "green"

    role_out = "seller" if r in ("seller", "sell", "supplier") else "buyer"
    
    # ─── LEARNING ENGINE: Log counterparty scoring ────────────────────────────
    counterparty_id = payload.get('id') or payload.get('companyName', 'unknown')[:20]
    action = 'counterparty_scored'
    if tier == "CRITICAL_BLOCK" or tier == "RED":
        action = 'fraud_flagged'
    nxlearn('jeta_fraud', str(counterparty_id), action, {
        'counterparty_type': role_out,
        'fraud_score': tier_count,
        'severity': tier,
        'flags_count': len(flags),
        'critical': has_critical,
    })
    
    return {
        "role": role_out,
        "flags": flags,
        "scoring_flag_count": tier_count,
        "tier": tier,
        "traffic_light": traffic,
        "critical_block": tier == "CRITICAL_BLOCK",
        "requires_manual_review_note": tier == "YELLOW",
        "blocked": tier in ("RED", "CRITICAL_BLOCK"),
    }


def scan_deal_terminology_blacklist(deal: Dict[str, Any], buyer: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Scan deal + optional buyer text for blocked terminology (CRITICAL)."""
    parts = [
        deal.get("dealName"),
        deal.get("dealDescription"),
        deal.get("supplySource"),
        deal.get("ncndaStatus"),
        deal.get("imfpaStatus"),
        deal.get("feeAgreementStatus"),
    ]
    if buyer:
        parts.extend(
            [
                buyer.get("companyName"),
                buyer.get("notes"),
                buyer.get("email"),
            ]
        )
    blob = "\n".join(str(p) for p in parts if p)
    findings = find_jeta_blocked_term_findings(blob)
    critical = len(findings) > 0
    return {
        "blacklist_critical": critical,
        "blacklist_findings": findings,
        "warning_messages": [f.get("message", "") for f in findings],
    }


# Human-readable gate checklist per deal stage (aligns with JETA_Deals pipeline + compliance layers).
DEAL_STAGE_GATE_REQUIREMENTS: Dict[str, List[str]] = {
    "Qualifying": [
        "Supply source identified before leaving Qualifying",
        "No blocked terminology in deal or counterparty text",
        "Counterparty intake scoring not RED / CRITICAL",
    ],
    "Supply Sourcing": [
        "Supply Source field populated and consistent with mandate",
        "NCNDA preparation: ICC 769 E alignment per policy",
        "Terminology blacklist clear on deal record",
    ],
    "NCNDA Pending": [
        "ICC Publication 769 E–compliant NCNDA generated; not generic floating",
        "Full legal names of both parties on NCNDA",
        "Specific deal description (not generic template)",
        "NCNDA sent and execution tracking started",
    ],
    "NCNDA Signed": [
        "NCNDA status reflects signed/executed before advancing",
        "Signed NCNDA uploaded and date-stamped when required by stage policy",
    ],
    "Docs Exchanged": [
        "FCO from seller and ICPO from buyer received",
        "FCO/ICPO reviewed — Jet-A or Jet A-1 only",
        "Fee agreement: per-gallon fee, payment trigger, signed before introduction (policy fields)",
        "If multi-broker chain: IMFPA generated and signed",
        "Fee agreement executed (checkbox) per docs-exchanged compliance",
    ],
    "IMFPA Executed": [
        "IMFPA lists all brokers by full legal name with exact percentages",
        "IMFPA locked after signatures; percentages total 100%",
        "IMFPA status reflects executed",
    ],
    "Closed Won": [
        "Fuel delivery confirmed; fee payment received or scheduled",
        "Deal file complete in JETA_Documents with linked rows",
        "Fee agreement and NCNDA closure criteria per compliance",
    ],
    "Closed Lost": [
        "Close-out documentation as per internal policy (optional)",
    ],
}


def build_jeta_dashboard_alerts(
    deals: List[Dict[str, Any]],
    buyers_by_id: Dict[str, Dict[str, Any]],
    *,
    now: Optional[datetime] = None,
) -> Dict[str, Any]:
    """
    Alerts for Dashboard: stuck deals, stale NCNDA, seller doc SLA.
    Uses createdTime on deals when stage-changed date unavailable.
    """
    now = now or datetime.now(timezone.utc)
    closed = frozenset({"Closed Won", "Closed Lost"})
    alerts: List[Dict[str, Any]] = []

    def parse_iso(s: Optional[str]) -> Optional[datetime]:
        if not s or not isinstance(s, str):
            return None
        m = re.match(r"^(\d{4})-(\d{2})-(\d{2})[T ](\d{2}):(\d{2})", s)
        if not m:
            return None
        try:
            return datetime(
                int(m.group(1)),
                int(m.group(2)),
                int(m.group(3)),
                int(m.group(4)),
                int(m.group(5)),
                tzinfo=timezone.utc,
            )
        except ValueError:
            return None

    for d in deals:
        stage = (d.get("dealStage") or "").strip()
        if stage in closed:
            continue
        cid = d.get("id") or ""
        created = parse_iso(d.get("createdTime"))
        if created:
            days_old = (now - created.replace(tzinfo=timezone.utc) if created.tzinfo is None else now - created).days
            if days_old >= 7:
                alerts.append(
                    {
                        "type": "DEAL_STUCK_STAGE",
                        "severity": "medium",
                        "deal_id": cid,
                        "deal_name": d.get("dealName") or "",
                        "buyer_name": d.get("buyerName") or "",
                        "stage": stage,
                        "message": f"Deal in stage {stage!r} for {days_old}+ days (record age) — review progression.",
                    }
                )

        nc = (d.get("ncndaStatus") or "").lower()
        signed = "sign" in nc or "execut" in nc
        if not signed and created:
            days_old = (now - created.replace(tzinfo=timezone.utc) if created.tzinfo is None else now - created).days
            if days_old >= 5 and stage in ("NCNDA Pending", "NCNDA Signed", "Supply Sourcing", "Qualifying"):
                alerts.append(
                    {
                        "type": "NCNDA_UNSIGNED_STALE",
                        "severity": "medium",
                        "deal_id": cid,
                        "deal_name": d.get("dealName") or "",
                        "message": "NCNDA does not appear signed/executed in status — 5+ days on record.",
                    }
                )

    for bid, b in buyers_by_id.items():
        bt = (b.get("buyerType") or "").lower()
        if "sell" not in bt:
            continue
        created = parse_iso(b.get("createdTime"))
        if not created:
            continue
        hours = (now - created.replace(tzinfo=timezone.utc) if created.tzinfo is None else now - created).total_seconds() / 3600.0
        if hours >= 72 and not _tf(b, "terminalStorageDocsUploaded"):
            alerts.append(
                {
                    "type": "SELLER_DOCS_SLA",
                    "severity": "high",
                    "buyer_id": bid,
                    "company_name": b.get("companyName") or "",
                    "message": "Seller-side counterparty: terminal/storage documentation not confirmed after 72h.",
                }
            )

    return {"generated_at": now.isoformat(), "alert_count": len(alerts), "alerts": alerts}


def _counterparty_role_from_buyer(buyer: Dict[str, Any]) -> str:
    bt = (buyer.get("buyerType") or "").lower()
    if "sell" in bt:
        return "seller"
    return "buyer"


def evaluate_fraud_integrity_for_stage_transition(
    deal_before: Dict[str, Any],
    deal_patch: Dict[str, Any],
    buyer: Dict[str, Any],
    new_stage: str,
) -> Dict[str, Any]:
    """
    Fraud / integrity checks when a JETA_Deals row changes stage (Layer 2 supplement).
    Returns flags for api_server to merge with compliance (blacklist CRITICAL, counterparty RED/CRITICAL).
    YELLOW counterparty tier requires acknowledgeManualReview + complianceReviewLogged (caller enforces).
    """
    merged = {**deal_before, **deal_patch}
    merged["dealStage"] = new_stage
    role = _counterparty_role_from_buyer(buyer)

    unmet: List[str] = []
    terminology = scan_deal_terminology_blacklist(merged, buyer)
    blacklist_critical = bool(terminology.get("blacklist_critical"))
    if blacklist_critical:
        for w in terminology.get("warning_messages") or []:
            if (w or "").strip():
                unmet.append(w.strip())

    score = score_counterparty_intake(buyer, role)
    tier = score.get("tier") or "GREEN"
    blocks_transition = blacklist_critical or tier in ("RED", "CRITICAL_BLOCK")
    if tier == "CRITICAL_BLOCK":
        unmet.append("Counterparty fraud: CRITICAL_BLOCK — cannot advance this deal.")
    elif tier == "RED":
        unmet.append("Counterparty fraud score RED — deal progression blocked.")
    elif tier == "YELLOW":
        unmet.append(
            "Counterparty fraud score YELLOW — acknowledge manual review and ensure compliance review is logged before advancing."
        )

    ds = (new_stage or "").strip()

    # Deduplicate while preserving order
    seen: set = set()
    deduped: List[str] = []
    for u in unmet:
        if u in seen:
            continue
        seen.add(u)
        deduped.append(u)

    return {
        "terminology_scan": terminology,
        "counterparty_fraud": score,
        "unmet_conditions": deduped,
        "blocks_transition": blocks_transition,
        "requires_yellow_ack": tier == "YELLOW",
        "gate_catalog_stage": DEAL_STAGE_GATE_REQUIREMENTS.get(ds, []),
    }

