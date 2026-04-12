"""
JETA COURTIÈRE — three-layer compliance framework (counterparty, gates, monitoring).

Layer 1 — Counterparty intake screening (new buyer / counterparty records).
Layer 2 — Deal progression gates (stage transitions).
Layer 3 — Continuous deal monitoring (batch; intended to run on a 24h schedule).

Integrations: called from api_server.py JETA routes. Extend rules here without
changing route shape; optional env:

  JETA_BLOCKED_TERMS_EXTRA — |||-separated phrases; any substring match in screened
    text adds a CRITICAL blocked-term finding (Layer 1 + Layer 2).

Built-in BLOCKED TERMS (CRITICAL / instant block): JP54, JP-54, D6/D2 as jet fuel,
Mazut, end seller, top seller, direct to refinery, 100% guarantee of product,
buyer/seller through relative, cannot disclose seller, IMFPA before information,
send LOI to end seller — see find_jeta_blocked_term_findings.

  JETA_SANCTIONS_BLOCKLIST — comma-separated substrings; company names containing
    any token trigger CRITICAL (instant block) on Layer 1 (case-insensitive).
  JETA_CONSUMER_EMAIL_DOMAINS — optional comma-separated domains treated as free/consumer
    unless businessEmailConfirmed is set (merged with built-in list).

Traffic-light (non-critical findings only; CRITICAL bypasses counts):
  0–2 flags: GREEN — proceed normally
  3–4 flags: YELLOW — manual review (acknowledgeManualReview required to proceed)
  5+ flags: RED — blocked; reasons logged server-side
  CRITICAL severity: instant block regardless of count

Counterparty readiness (Layer 1; all required for intake / stored on buyer):
  — Legal entity name confirmed (legalEntityConfirmed)
  — Aircraft or fuel consumption verified — FAA lookup or docs (aircraftOrFuelVerified)
  — Contact is confirmed purchasing authority (purchasingAuthorityConfirmed)
  — Counterparty score GREEN, or YELLOW with compliance review logged on record
    (complianceReviewLogged). YELLOW API actions also require acknowledgeManualReview
    + complianceReviewLogged.
  — No CRITICAL flags on the screening record (sanctions / instant-stop rules).
  — Business-domain email: not a free-consumer domain unless businessEmailConfirmed.
  — At least one outreach row in JETA_Outreach for this buyer (enforced once buyer id exists;
    optional outreachRowCount on the buyer dict from api_server).
  — Response received and logged on an outreach row (outreachResponseLogged from api_server
    once buyer id exists).
  — Current fuel benchmark captured — approximate PPG on buyer (fuelBenchmarkPpg).
  — Contract status known — branded or independent (contractStatus).
  — Volume per month documented (volumePerMonth, gallons/month or consistent unit, > 0).
  — Buyer confirmed not locked in exclusive long-term contract (notExclusiveLongTermContract).
  — Decision maker documented by name and title (decisionMakerName, decisionMakerTitle).

NCNDA document compliance (Layer 2 when deal stage advances to NCNDA Pending or later,
except Closed Lost): ICC Publication 769 E–style NCNDA generated, not a generic floating
template, both parties’ full legal names on the deal, document sent and execution tracked
(see evaluate_ncnda_document_compliance / ncnda_readiness on gate responses).

Docs-exchanged compliance (Layer 2 at Docs Exchanged or later, except Closed Lost): signed
NCNDA uploaded and date-stamped; FCO from seller; ICPO from buyer; both reviewed for Jet-A /
Jet A-1 only; if multiple brokers, IMFPA generated and signed; fee agreement executed
(docs_readiness on gate responses).

Closed Won compliance (Layer 2 only when target stage is Closed Won): fuel delivery
confirmed; fee payment received or scheduled; deal file complete with rows in JETA_Documents
(api_server passes jetaDocumentsCountForDeal) — closure_readiness on gate responses.

NCNDA / IMFPA / Fee Agreement document policy: see evaluate_ncnda_document_compliance,
evaluate_imfpa_document_compliance, evaluate_fee_agreement_document_compliance (readiness on
gate responses when stage gates apply).
"""

from __future__ import annotations

import os
import re
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional

# ---------------------------------------------------------------------------
# Layer 1 — Intake screening
# ---------------------------------------------------------------------------

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

_DEFAULT_CONSUMER_EMAIL_DOMAINS = frozenset(
    {
        "gmail.com",
        "googlemail.com",
        "yahoo.com",
        "yahoo.co.uk",
        "hotmail.com",
        "outlook.com",
        "live.com",
        "msn.com",
        "icloud.com",
        "me.com",
        "mac.com",
        "aol.com",
        "protonmail.com",
        "proton.me",
        "mail.com",
        "gmx.com",
        "gmx.net",
        "yandex.com",
        "hey.com",
        "pm.me",
    }
)


def _consumer_email_domains() -> set:
    d = set(_DEFAULT_CONSUMER_EMAIL_DOMAINS)
    raw = (os.environ.get("JETA_CONSUMER_EMAIL_DOMAINS") or "").strip()
    if raw:
        d |= {x.strip().lower() for x in raw.split(",") if x.strip()}
    return d


def _email_domain_is_consumer(email: str) -> bool:
    m = re.match(r"^[^@\s]+@([^@\s]+)$", (email or "").strip().lower())
    if not m:
        return False
    return m.group(1) in _consumer_email_domains()


_RE_JP54 = re.compile(r"(?i)jp[\s\-]*54")


def _jeta_join_screening_text(*parts: Any) -> str:
    chunks: List[str] = []
    for p in parts:
        if p is None:
            continue
        s = str(p).strip()
        if s:
            chunks.append(s)
    return "\n".join(chunks)


def find_jeta_blocked_term_findings(text: str) -> List[Dict[str, Any]]:
    """
    Return CRITICAL findings for policy-blocked phrases (JP54, Mazut, scam patterns, etc.).
    Scans free text from buyer/deal fields — case-insensitive where noted.
    """
    if not (text or "").strip():
        return []
    findings: List[Dict[str, Any]] = []
    seen: set = set()
    t = text
    cf = text.casefold()
    alnum_only = re.sub(r"[^a-z0-9]+", "", cf)

    def add(code: str, message: str) -> None:
        if code in seen:
            return
        seen.add(code)
        findings.append({"code": code, "severity": "critical", "message": message})

    if _RE_JP54.search(t) or "jp54" in alnum_only:
        add("BLOCKED_TERM_JP54", "Blocked term: JP54 / JP-54 is not permitted.")

    if re.search(r"(?i)\b[Dd][26]\b", t) and re.search(
        r"(?i)(jet\s*fuel|\bjet[-\s]*a\b|jet[-\s]*a[-\s]*1|aviation\s*fuel|turbine\s*fuel|\bjp\s*8\b)",
        t,
    ):
        add(
            "BLOCKED_TERM_D6_D2_JET",
            "Blocked term: D6 or D2 referenced in a jet/aviation fuel context is not permitted.",
        )

    if "mazut" in cf:
        add("BLOCKED_TERM_MAZUT", "Blocked term: Mazut.")

    if re.search(r"(?i)\bend\s+seller\b", t):
        add(
            "BLOCKED_TERM_END_SELLER",
            'Blocked term: "end seller" without an identified legal entity.',
        )

    if re.search(r"(?i)\btop\s+seller\b", t):
        add("BLOCKED_TERM_TOP_SELLER", 'Blocked term: "top seller".')

    if re.search(r"(?i)direct\s+to\s+refinery", t):
        add(
            "BLOCKED_TERM_DIRECT_TO_REFINERY",
            'Blocked term: "direct to refinery" without a named refinery.',
        )

    if re.search(r"(?i)100\s*%\s*guarantee\s+of\s+product", t):
        add(
            "BLOCKED_TERM_100_PCT_GUARANTEE",
            'Blocked term: "100% guarantee of product".',
        )

    if re.search(
        r"(?i)(.{0,80}\b(buyer|seller)\b.{0,80}through\s+(my\s+)?(uncle|friend|relative|cousin)|through\s+(my\s+)?(uncle|friend|relative|cousin).{0,80}\b(buyer|seller)\b)",
        t,
    ):
        add(
            "BLOCKED_TERM_RELATION_CHAIN",
            'Blocked term: buyer/seller introduced only through uncle/friend/relative.',
        )

    if re.search(r"(?i)cannot\s+disclose\s+seller", t):
        add(
            "BLOCKED_TERM_CANNOT_DISCLOSE_SELLER",
            'Blocked term: "cannot disclose seller" / non-disclosure of seller identity.',
        )

    if re.search(
        r"(?i)(sign\s+imfpa\s+first|imfpa\s+first.{0,30}before.{0,50}information|before\s+any\s+information.{0,50}imfpa)",
        t,
    ):
        add(
            "BLOCKED_TERM_IMFPA_FIRST_NO_INFO",
            'Blocked term: sign IMFPA before receiving material information.',
        )

    if re.search(r"(?i)send\s+(an?\s+)?loi\s+to\s+(the\s+)?end\s+seller", t):
        add(
            "BLOCKED_TERM_LOI_END_SELLER",
            'Blocked term: send LOI to end seller.',
        )

    extra = (os.environ.get("JETA_BLOCKED_TERMS_EXTRA") or "").strip()
    if extra:
        for i, phrase in enumerate(p.strip() for p in extra.split("|||") if p.strip()):
            if phrase.casefold() in cf:
                add(
                    f"BLOCKED_TERM_EXTRA_{i}",
                    f"Blocked term (policy list): {phrase!r}.",
                )

    return findings


def _severity_lower(f: Dict[str, Any]) -> str:
    return (f.get("severity") or "").strip().lower()


def apply_traffic_light(findings: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Map findings to GREEN / YELLOW / RED. CRITICAL findings force RED + instant block
    regardless of how many other findings exist.
    """
    critical_flags = [f for f in findings if _severity_lower(f) == "critical"]
    non_critical = [f for f in findings if _severity_lower(f) != "critical"]
    n = len(non_critical)

    if critical_flags:
        return {
            "traffic_light": "red",
            "critical_block": True,
            "scoring_flag_count": n,
            "flag_count": len(findings),
            "critical_flags": critical_flags,
            "requires_manual_review": False,
            "may_proceed_with_ack": False,
            "deal_blocked": True,
        }

    if n <= 2:
        tl = "green"
    elif n <= 4:
        tl = "yellow"
    else:
        tl = "red"

    return {
        "traffic_light": tl,
        "critical_block": False,
        "scoring_flag_count": n,
        "flag_count": n,
        "critical_flags": [],
        "requires_manual_review": tl == "yellow",
        "may_proceed_with_ack": tl == "yellow",
        "deal_blocked": tl == "red",
    }


def may_proceed_traffic_light(
    compliance: Dict[str, Any],
    acknowledge_manual_review: bool,
    compliance_review_logged: bool = False,
) -> bool:
    """
    Whether an intake or stage change may proceed given traffic-light rules.
    YELLOW requires both acknowledgeManualReview and complianceReviewLogged on the counterparty.
    """
    if compliance.get("critical_block"):
        return False
    if compliance.get("deal_blocked"):
        return False
    tl = compliance.get("traffic_light")
    if tl == "yellow":
        return acknowledge_manual_review is True and compliance_review_logged is True
    return tl == "green"


def _fuel_benchmark_ppg_ok(buyer: Dict[str, Any]) -> bool:
    v = buyer.get("fuelBenchmarkPpg")
    if v is None or v == "":
        return False
    try:
        return float(v) > 0
    except (TypeError, ValueError):
        return False


def _contract_status_known_ok(buyer: Dict[str, Any]) -> bool:
    s = (buyer.get("contractStatus") or "").strip().lower()
    return s in ("branded", "independent")


def _volume_per_month_ok(buyer: Dict[str, Any]) -> bool:
    v = buyer.get("volumePerMonth")
    if v is None or v == "":
        return False
    try:
        return float(v) > 0
    except (TypeError, ValueError):
        return False


def _decision_maker_documented_ok(buyer: Dict[str, Any]) -> bool:
    n = (buyer.get("decisionMakerName") or "").strip()
    t = (buyer.get("decisionMakerTitle") or "").strip()
    return len(n) > 0 and len(t) > 0


def _buyer_bool(buyer: Dict[str, Any], key: str) -> bool:
    v = buyer.get(key)
    if v is True:
        return True
    if v in (False, None, "", []):
        return False
    if isinstance(v, str):
        return v.strip().lower() in ("true", "1", "yes", "y", "checked")
    return bool(v)


def _sanctions_blocklist() -> List[str]:
    raw = (os.environ.get("JETA_SANCTIONS_BLOCKLIST") or "").strip()
    if not raw:
        return []
    return [x.strip().lower() for x in raw.split(",") if x.strip()]


def run_layer1_intake_screening(buyer: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run when a new counterparty (buyer) is created.

    Returns:
      layer, passed (green-only without ack), risk_level, findings, traffic_light fields,
      readiness (no_critical_flags, business_domain_email_ok, outreach_logged, …), screened_at.

    Pass outreachRowCount: int when buyer id is set (from api_server) to enforce JETA_Outreach.
    """
    findings: List[Dict[str, str]] = []

    company = (buyer.get("companyName") or "").strip()
    contact = (buyer.get("contactName") or "").strip()
    email = (buyer.get("email") or "").strip()
    state = (buyer.get("state") or "").strip()

    if not company:
        findings.append(
            {
                "code": "MISSING_COMPANY",
                "severity": "high",
                "message": "Company name is required for counterparty intake.",
            }
        )
    if not contact:
        findings.append(
            {
                "code": "MISSING_CONTACT",
                "severity": "medium",
                "message": "Contact name should be provided before substantive engagement.",
            }
        )
    if email and not _EMAIL_RE.match(email):
        findings.append(
            {
                "code": "INVALID_EMAIL",
                "severity": "medium",
                "message": "Email format appears invalid.",
            }
        )
    if not email:
        findings.append(
            {
                "code": "MISSING_EMAIL",
                "severity": "medium",
                "message": "Email is recommended for audit trail and outreach.",
            }
        )
    if state and len(state) != 2:
        findings.append(
            {
                "code": "STATE_FORMAT",
                "severity": "low",
                "message": "Use 2-letter state/province code where applicable.",
            }
        )

    comp_lower = company.lower()
    for token in _sanctions_blocklist():
        if token and token in comp_lower:
            findings.append(
                {
                    "code": "SANCTIONS_KEYWORD",
                    "severity": "critical",
                    "message": f"Company name matches blocklist token: {token!r}. Blocked — sanctions / compliance.",
                }
            )

    legal_ok = _buyer_bool(buyer, "legalEntityConfirmed")
    fuel_ok = _buyer_bool(buyer, "aircraftOrFuelVerified")
    auth_ok = _buyer_bool(buyer, "purchasingAuthorityConfirmed")
    crm_logged = _buyer_bool(buyer, "complianceReviewLogged")

    if not legal_ok:
        findings.append(
            {
                "code": "LEGAL_ENTITY_NOT_CONFIRMED",
                "severity": "medium",
                "message": "Buyer legal entity name must be confirmed before substantive engagement.",
            }
        )
    if not fuel_ok:
        findings.append(
            {
                "code": "AIRCRAFT_OR_FUEL_NOT_VERIFIED",
                "severity": "medium",
                "message": "Aircraft tail / fuel consumption must be verified (FAA lookup or supporting docs).",
            }
        )
    if not auth_ok:
        findings.append(
            {
                "code": "PURCHASING_AUTHORITY_NOT_CONFIRMED",
                "severity": "medium",
                "message": "Contact must be confirmed as purchasing authority (or documented delegation).",
            }
        )

    business_email_conf = _buyer_bool(buyer, "businessEmailConfirmed")
    business_email_ok = False
    if email and _EMAIL_RE.match(email):
        if _email_domain_is_consumer(email):
            if business_email_conf:
                business_email_ok = True
            else:
                findings.append(
                    {
                        "code": "CONSUMER_OR_FREE_EMAIL_DOMAIN",
                        "severity": "medium",
                        "message": "Use a business-domain email or confirm this address (businessEmailConfirmed).",
                    }
                )
        else:
            business_email_ok = True

    has_buyer_id = bool((buyer.get("id") or "").strip())
    oc = buyer.get("outreachRowCount")
    outreach_ok = True
    if has_buyer_id:
        if not isinstance(oc, int) or oc < 0:
            outreach_ok = False
        else:
            outreach_ok = oc > 0
        if not outreach_ok:
            findings.append(
                {
                    "code": "OUTREACH_NOT_LOGGED",
                    "severity": "medium",
                    "message": "At least one outreach touch must be logged in JETA_Outreach for this buyer.",
                }
            )

    response_received_logged = True
    if has_buyer_id:
        if outreach_ok:
            response_received_logged = _buyer_bool(buyer, "outreachResponseLogged")
            if not response_received_logged:
                findings.append(
                    {
                        "code": "OUTREACH_RESPONSE_NOT_LOGGED",
                        "severity": "medium",
                        "message": "Response received (or response status) must be logged on JETA_Outreach.",
                    }
                )
        else:
            response_received_logged = False

    fuel_benchmark_ok = _fuel_benchmark_ppg_ok(buyer)
    if not fuel_benchmark_ok:
        findings.append(
            {
                "code": "FUEL_BENCHMARK_PPG_MISSING",
                "severity": "medium",
                "message": "Current fuel benchmark (approximate PPG) must be captured on the buyer record.",
            }
        )

    contract_status_ok = _contract_status_known_ok(buyer)
    if not contract_status_ok:
        findings.append(
            {
                "code": "CONTRACT_STATUS_UNKNOWN",
                "severity": "medium",
                "message": "Contract status must be recorded as branded or independent.",
            }
        )

    volume_per_month_ok = _volume_per_month_ok(buyer)
    if not volume_per_month_ok:
        findings.append(
            {
                "code": "VOLUME_PER_MONTH_NOT_DOCUMENTED",
                "severity": "medium",
                "message": "Volume per month must be documented on the buyer record (positive number).",
            }
        )

    not_exclusive_ok = _buyer_bool(buyer, "notExclusiveLongTermContract")
    if not not_exclusive_ok:
        findings.append(
            {
                "code": "EXCLUSIVE_LONG_TERM_LOCK_NOT_CLEARED",
                "severity": "medium",
                "message": "Confirm buyer is not locked in an exclusive long-term fuel contract (notExclusiveLongTermContract).",
            }
        )

    decision_maker_ok = _decision_maker_documented_ok(buyer)
    if not decision_maker_ok:
        findings.append(
            {
                "code": "DECISION_MAKER_NOT_DOCUMENTED",
                "severity": "medium",
                "message": "Decision maker must be recorded with name and title.",
            }
        )

    screening_blob = _jeta_join_screening_text(
        buyer.get("companyName"),
        buyer.get("contactName"),
        buyer.get("email"),
        buyer.get("phone"),
        buyer.get("notes"),
        buyer.get("nextAction"),
        buyer.get("website"),
        buyer.get("city"),
        buyer.get("state"),
        buyer.get("airport"),
        buyer.get("buyerType"),
    )
    findings.extend(find_jeta_blocked_term_findings(screening_blob))

    severities = [f.get("severity") for f in findings]
    if "critical" in severities:
        risk = "high"
    elif "high" in severities:
        risk = "high"
    elif "medium" in severities:
        risk = "medium"
    else:
        risk = "low"

    traffic = apply_traffic_light(findings)
    tl = traffic.get("traffic_light")
    crit = bool(traffic.get("critical_block"))
    no_critical_flags = not crit

    if crit or tl == "red":
        score_ok = False
    elif tl == "green":
        score_ok = True
    elif tl == "yellow":
        score_ok = crm_logged
    else:
        score_ok = False

    readiness = {
        "no_critical_flags": no_critical_flags,
        "legal_entity_confirmed": legal_ok,
        "aircraft_or_fuel_verified": fuel_ok,
        "purchasing_authority_confirmed": auth_ok,
        "counterparty_score_ok": score_ok,
        "business_domain_email_ok": business_email_ok,
        "outreach_logged": outreach_ok,
        "response_received_logged": response_received_logged,
        "fuel_benchmark_ppg_captured": fuel_benchmark_ok,
        "contract_status_known": contract_status_ok,
        "volume_per_month_documented": volume_per_month_ok,
        "not_exclusive_long_term_contract_confirmed": not_exclusive_ok,
        "decision_maker_documented": decision_maker_ok,
        "all_met": bool(
            no_critical_flags
            and legal_ok
            and fuel_ok
            and auth_ok
            and score_ok
            and business_email_ok
            and outreach_ok
            and response_received_logged
            and fuel_benchmark_ok
            and contract_status_ok
            and volume_per_month_ok
            and not_exclusive_ok
            and decision_maker_ok
        ),
    }

    passed = may_proceed_traffic_light(traffic, False, False) and readiness["all_met"]

    out: Dict[str, Any] = {
        "layer": 1,
        "passed": passed,
        "risk_level": risk,
        "findings": findings,
        "readiness": readiness,
        "screened_at": datetime.utcnow().isoformat() + "Z",
    }
    out.update(traffic)
    return out


# ---------------------------------------------------------------------------
# Layer 2 — Deal progression gates
# ---------------------------------------------------------------------------

JETA_DEAL_STAGES_ORDER = [
    "Qualifying",
    "Supply Sourcing",
    "NCNDA Pending",
    "NCNDA Signed",
    "Docs Exchanged",
    "IMFPA Executed",
    "Closed Won",
    "Closed Lost",
]


def _stage_index(stage: str) -> int:
    s = (stage or "").strip()
    try:
        return JETA_DEAL_STAGES_ORDER.index(s)
    except ValueError:
        return -1


GateFn = Callable[[Dict[str, Any], Dict[str, Any], str], Optional[str]]


def _gate_supply_sourcing(deal: Dict[str, Any], buyer: Dict[str, Any], target: str) -> Optional[str]:
    if target != "Supply Sourcing":
        return None
    src = (deal.get("supplySource") or "").strip()
    if not src:
        return "Supply Source must be identified before leaving Qualifying."
    return None


def _gate_ncnda_signed(deal: Dict[str, Any], buyer: Dict[str, Any], target: str) -> Optional[str]:
    if target != "NCNDA Signed":
        return None
    st = (deal.get("ncndaStatus") or "").lower()
    if "signed" not in st and "executed" not in st:
        return "NCNDA documentation should be signed (or marked Signed in CRM) before advancing to NCNDA Signed."
    return None


def _gate_imfpa_executed(deal: Dict[str, Any], buyer: Dict[str, Any], target: str) -> Optional[str]:
    if target != "IMFPA Executed":
        return None
    st = (deal.get("imfpaStatus") or "").lower()
    if "execut" not in st and "signed" not in st:
        return "IMFPA should be executed or marked before stage IMFPA Executed."
    return None


def _gate_closed_won(deal: Dict[str, Any], buyer: Dict[str, Any], target: str) -> Optional[str]:
    if target != "Closed Won":
        return None
    fee = (deal.get("feeAgreementStatus") or "").lower()
    if not fee or ("signed" not in fee and "complete" not in fee):
        return "Fee Agreement status should reflect signed/completed documentation before Closed Won."
    return None


_DEFAULT_GATES: List[GateFn] = [
    _gate_supply_sourcing,
    _gate_ncnda_signed,
    _gate_imfpa_executed,
    _gate_closed_won,
]


def _ncnda_gate_applies(to_stage: str) -> bool:
    """Require ICC 769E / NCNDA checklist when moving into NCNDA work or beyond; not for Closed Lost."""
    ts = (to_stage or "").strip()
    if ts == "Closed Lost":
        return False
    i_new = _stage_index(ts)
    if i_new < 0:
        return False
    try:
        need = JETA_DEAL_STAGES_ORDER.index("NCNDA Pending")
    except ValueError:
        return False
    return i_new >= need


def evaluate_ncnda_document_compliance(deal: Dict[str, Any]) -> Dict[str, Any]:
    """
    ICC Publication 769 E–aligned NCNDA checklist on the deal record (serialized camelCase).

    Fields:
      icc769NcndaGenerated, ncndaIcc769eReferencedInDocument (body cites ICC Pub 769 E),
      notGenericNcndaTemplate, ncndaDealDescriptionSpecificNotGeneric,
      ncndaGenericFloatingInvalidOnUpload (generic floating NCNDA invalidated on upload),
      ncndaBuyerPartyLegalName, ncndaJetaPartyLegalName,
      ncndaDocumentSent, ncndaExecutionTracked
    """
    findings: List[Dict[str, Any]] = []

    icc = _buyer_bool(deal, "icc769NcndaGenerated")
    icc_in_doc = _buyer_bool(deal, "ncndaIcc769eReferencedInDocument")
    not_generic = _buyer_bool(deal, "notGenericNcndaTemplate")
    specific_deal = _buyer_bool(deal, "ncndaDealDescriptionSpecificNotGeneric")
    generic_invalid_upload = _buyer_bool(deal, "ncndaGenericFloatingInvalidOnUpload")
    # If already confirmed non–generic floating template, invalid-upload workflow N/A.
    upload_policy_ok = generic_invalid_upload or not_generic
    buyer_legal = (deal.get("ncndaBuyerPartyLegalName") or "").strip()
    jeta_legal = (deal.get("ncndaJetaPartyLegalName") or "").strip()
    parties_ok = len(buyer_legal) > 0 and len(jeta_legal) > 0
    sent = _buyer_bool(deal, "ncndaDocumentSent")
    tracked = _buyer_bool(deal, "ncndaExecutionTracked")
    sent_tracked_ok = sent and tracked

    if not icc:
        findings.append(
            {
                "code": "ICC769_NCNDA_NOT_GENERATED",
                "severity": "medium",
                "message": "Generate an ICC Publication 769 E–compliant NCNDA (icc769NcndaGenerated).",
            }
        )
    if not icc_in_doc:
        findings.append(
            {
                "code": "NCNDA_ICC769E_NOT_REFERENCED_IN_DOCUMENT",
                "severity": "medium",
                "message": "Executed NCNDA must reference ICC Publication 769 E in the document body (ncndaIcc769eReferencedInDocument).",
            }
        )
    if not not_generic:
        findings.append(
            {
                "code": "GENERIC_FLOATING_NCNDA",
                "severity": "medium",
                "message": "NCNDA must not be a generic floating template; confirm bespoke ICC-aligned doc (notGenericNcndaTemplate).",
            }
        )
    if not specific_deal:
        findings.append(
            {
                "code": "NCNDA_DEAL_DESCRIPTION_GENERIC",
                "severity": "medium",
                "message": "NCNDA must contain a specific deal description — not generic (ncndaDealDescriptionSpecificNotGeneric).",
            }
        )
    if not upload_policy_ok:
        findings.append(
            {
                "code": "NCNDA_GENERIC_UPLOAD_NOT_INVALIDATED",
                "severity": "medium",
                "message": "Generic floating NCNDA uploads must be marked invalid on upload when detected, or confirm non–generic NCNDA (ncndaGenericFloatingInvalidOnUpload / notGenericNcndaTemplate).",
            }
        )
    if not parties_ok:
        findings.append(
            {
                "code": "NCNDA_PARTIES_LEGAL_NAME_MISSING",
                "severity": "medium",
                "message": "Both parties must be identified by full legal name (ncndaBuyerPartyLegalName, ncndaJetaPartyLegalName).",
            }
        )
    if not sent:
        findings.append(
            {
                "code": "NCNDA_DOCUMENT_NOT_SENT",
                "severity": "medium",
                "message": "NCNDA document must be sent to the counterparty (ncndaDocumentSent).",
            }
        )
    if not tracked:
        findings.append(
            {
                "code": "NCNDA_EXECUTION_NOT_TRACKED",
                "severity": "medium",
                "message": "NCNDA execution must be tracked in CRM (ncndaExecutionTracked).",
            }
        )

    readiness = {
        "icc769_compliant_ncnda_generated": icc,
        "icc769_referenced_in_ncnda_document": icc_in_doc,
        "not_generic_floating_ncnda": not_generic,
        "specific_deal_description_not_generic": specific_deal,
        "generic_floating_invalid_on_upload": upload_policy_ok,
        "both_parties_full_legal_name": parties_ok,
        "document_sent_and_execution_tracked": sent_tracked_ok,
        "all_met": bool(
            icc
            and icc_in_doc
            and not_generic
            and specific_deal
            and upload_policy_ok
            and parties_ok
            and sent_tracked_ok
        ),
    }
    return {"findings": findings, "readiness": readiness}


def _imfpa_document_gate_applies(to_stage: str) -> bool:
    if (to_stage or "").strip() == "Closed Lost":
        return False
    i_new = _stage_index(to_stage)
    if i_new < 0:
        return False
    try:
        need = JETA_DEAL_STAGES_ORDER.index("IMFPA Executed")
    except ValueError:
        return False
    return i_new >= need


def _imfpa_broker_percentage_total_ok(deal: Dict[str, Any]) -> bool:
    raw = deal.get("imfpaBrokerChainPercentageTotal")
    if raw is None or str(raw).strip() == "":
        return _buyer_bool(deal, "imfpaPercentagesTotalValid")
    try:
        return abs(float(raw) - 100.0) <= 0.02
    except (TypeError, ValueError):
        return False


def evaluate_imfpa_document_compliance(deal: Dict[str, Any]) -> Dict[str, Any]:
    """
    IMFPA content / execution policy (deal record).

    Fields:
      imfpaAllBrokersFullLegalNamesListed, imfpaExactPercentagePerPartySpecified,
      imfpaLockedAfterAllSignaturesNoEdits, imfpaPercentagesTotalValid,
      imfpaBrokerChainPercentageTotal (optional; must sum to 100 when set)
    """
    findings: List[Dict[str, Any]] = []

    brokers = _buyer_bool(deal, "imfpaAllBrokersFullLegalNamesListed")
    pct_each = _buyer_bool(deal, "imfpaExactPercentagePerPartySpecified")
    locked = _buyer_bool(deal, "imfpaLockedAfterAllSignaturesNoEdits")
    pct_tot_ok = _imfpa_broker_percentage_total_ok(deal)

    if not brokers:
        findings.append(
            {
                "code": "IMFPA_BROKERS_LEGAL_NAMES_MISSING",
                "severity": "medium",
                "message": "IMFPA must list every broker in the chain by full legal name (imfpaAllBrokersFullLegalNamesListed).",
            }
        )
    if not pct_each:
        findings.append(
            {
                "code": "IMFPA_PERCENTAGES_PER_PARTY_MISSING",
                "severity": "medium",
                "message": "IMFPA must specify exact percentage for each party (imfpaExactPercentagePerPartySpecified).",
            }
        )
    if not locked:
        findings.append(
            {
                "code": "IMFPA_NOT_LOCKED_POST_SIGNATURE",
                "severity": "medium",
                "message": "IMFPA must be locked after all parties sign — no further edits (imfpaLockedAfterAllSignaturesNoEdits).",
            }
        )
    if not pct_tot_ok:
        findings.append(
            {
                "code": "IMFPA_PERCENTAGE_TOTAL_INVALID",
                "severity": "medium",
                "message": "Broker-chain percentages must total 100% (imfpaBrokerChainPercentageTotal or imfpaPercentagesTotalValid).",
            }
        )

    readiness = {
        "all_brokers_full_legal_names": brokers,
        "exact_percentage_per_party": pct_each,
        "locked_after_all_signatures": locked,
        "percentages_total_valid": pct_tot_ok,
        "all_met": bool(brokers and pct_each and locked and pct_tot_ok),
    }
    return {"findings": findings, "readiness": readiness}


def _fee_agreement_document_gate_applies(to_stage: str) -> bool:
    if (to_stage or "").strip() == "Closed Lost":
        return False
    i_new = _stage_index(to_stage)
    if i_new < 0:
        return False
    try:
        need = JETA_DEAL_STAGES_ORDER.index("Docs Exchanged")
    except ValueError:
        return False
    return i_new >= need


def _fee_exact_per_gallon_ok(deal: Dict[str, Any]) -> bool:
    if _buyer_bool(deal, "feeAgreementExactPerGallonSpecified"):
        return True
    try:
        return float(deal.get("jetaFeePerGallon") or 0) > 0
    except (TypeError, ValueError):
        return False


def evaluate_fee_agreement_document_compliance(deal: Dict[str, Any]) -> Dict[str, Any]:
    """
    Fee agreement policy: per-gallon fee, payment trigger, signed before introduction.

    Fields:
      feeAgreementExactPerGallonSpecified (or jetaFeePerGallon > 0),
      feeAgreementPaymentTriggerSpecified,
      feeAgreementSignedBeforeIntroduction
    """
    findings: List[Dict[str, Any]] = []

    pg_ok = _fee_exact_per_gallon_ok(deal)
    trig = _buyer_bool(deal, "feeAgreementPaymentTriggerSpecified")
    before_intro = _buyer_bool(deal, "feeAgreementSignedBeforeIntroduction")

    if not pg_ok:
        findings.append(
            {
                "code": "FEE_AGREEMENT_PER_GALLON_MISSING",
                "severity": "medium",
                "message": "Fee agreement must specify exact per-gallon fee (feeAgreementExactPerGallonSpecified or jetaFeePerGallon).",
            }
        )
    if not trig:
        findings.append(
            {
                "code": "FEE_AGREEMENT_PAYMENT_TRIGGER_MISSING",
                "severity": "medium",
                "message": "Fee agreement must specify payment trigger — delivery, invoice, or net terms (feeAgreementPaymentTriggerSpecified).",
            }
        )
    if not before_intro:
        findings.append(
            {
                "code": "FEE_AGREEMENT_NOT_SIGNED_BEFORE_INTRO",
                "severity": "medium",
                "message": "Fee agreement must be signed before introduction is made (feeAgreementSignedBeforeIntroduction).",
            }
        )

    readiness = {
        "exact_per_gallon_fee": pg_ok,
        "payment_trigger_specified": trig,
        "signed_before_introduction": before_intro,
        "all_met": bool(pg_ok and trig and before_intro),
    }
    return {"findings": findings, "readiness": readiness}


def _docs_exchanged_gate_applies(to_stage: str) -> bool:
    """Require FCO/ICPO / NCNDA upload checklist when entering Docs Exchanged or later."""
    ts = (to_stage or "").strip()
    if ts == "Closed Lost":
        return False
    i_new = _stage_index(ts)
    if i_new < 0:
        return False
    try:
        need = JETA_DEAL_STAGES_ORDER.index("Docs Exchanged")
    except ValueError:
        return False
    return i_new >= need


def evaluate_docs_exchanged_compliance(deal: Dict[str, Any]) -> Dict[str, Any]:
    """
    Post–NCNDA signed document checklist (deal record, camelCase).

    Fields:
      signedNcndaUploadedDateStamped, fcoReceivedFromSeller, icpoReceivedFromBuyer,
      fcoIcpoProductJetAA1Only (FCO/ICPO reviewed — Jet-A or Jet A-1 only),
      multipleBrokersInChain, imfpaGeneratedSignedBrokerChain (required if multi-broker),
      feeAgreementExecuted
    """
    findings: List[Dict[str, Any]] = []

    ncnda_up = _buyer_bool(deal, "signedNcndaUploadedDateStamped")
    fco = _buyer_bool(deal, "fcoReceivedFromSeller")
    icpo = _buyer_bool(deal, "icpoReceivedFromBuyer")
    jet_only = _buyer_bool(deal, "fcoIcpoProductJetAA1Only")
    multi = _buyer_bool(deal, "multipleBrokersInChain")
    imfpa_chain = _buyer_bool(deal, "imfpaGeneratedSignedBrokerChain")
    fee_ex = _buyer_bool(deal, "feeAgreementExecuted")

    imfpa_broker_ok = True
    if multi:
        imfpa_broker_ok = imfpa_chain

    if not ncnda_up:
        findings.append(
            {
                "code": "SIGNED_NCNDA_NOT_UPLOADED_OR_STAMPED",
                "severity": "medium",
                "message": "Signed NCNDA must be uploaded and date-stamped (signedNcndaUploadedDateStamped).",
            }
        )
    if not fco:
        findings.append(
            {
                "code": "FCO_NOT_RECEIVED",
                "severity": "medium",
                "message": "Full Corporate Offer (FCO) must be received from the seller (fcoReceivedFromSeller).",
            }
        )
    if not icpo:
        findings.append(
            {
                "code": "ICPO_NOT_RECEIVED",
                "severity": "medium",
                "message": "Irrevocable Corporate Purchase Order (ICPO) must be received from the buyer (icpoReceivedFromBuyer).",
            }
        )
    if not jet_only:
        findings.append(
            {
                "code": "FCO_ICPO_PRODUCT_NOT_JET_A",
                "severity": "medium",
                "message": "FCO and ICPO must be reviewed — product specification Jet-A or Jet A-1 only (fcoIcpoProductJetAA1Only).",
            }
        )
    if multi and not imfpa_chain:
        findings.append(
            {
                "code": "IMFPA_BROKER_CHAIN_INCOMPLETE",
                "severity": "medium",
                "message": "Multiple brokers in chain: IMFPA must be generated and signed (imfpaGeneratedSignedBrokerChain).",
            }
        )
    if not fee_ex:
        findings.append(
            {
                "code": "FEE_AGREEMENT_NOT_EXECUTED",
                "severity": "medium",
                "message": "Fee agreement must be executed (feeAgreementExecuted).",
            }
        )

    readiness = {
        "signed_ncnda_uploaded_date_stamped": ncnda_up,
        "fco_received_from_seller": fco,
        "icpo_received_from_buyer": icpo,
        "fco_icpo_reviewed_jet_a_a1_only": jet_only,
        "imfpa_broker_chain_ok": imfpa_broker_ok,
        "fee_agreement_executed": fee_ex,
        "all_met": bool(
            ncnda_up
            and fco
            and icpo
            and jet_only
            and imfpa_broker_ok
            and fee_ex
        ),
    }
    return {"findings": findings, "readiness": readiness}


def _closed_won_gate_applies(to_stage: str) -> bool:
    return (to_stage or "").strip() == "Closed Won"


def evaluate_deal_closure_compliance(deal: Dict[str, Any]) -> Dict[str, Any]:
    """
    Final closure checklist before Closed Won (deal record + virtual jetaDocumentsCountForDeal).

    Fields:
      fuelDeliveryConfirmed, feePaymentReceivedOrScheduled, dealFileCompleteInDocuments,
      jetaDocumentsCountForDeal (int, injected by api_server — not stored on JETA_Deals)
    """
    findings: List[Dict[str, Any]] = []

    fuel = _buyer_bool(deal, "fuelDeliveryConfirmed")
    fee_ps = _buyer_bool(deal, "feePaymentReceivedOrScheduled")
    file_flag = _buyer_bool(deal, "dealFileCompleteInDocuments")
    raw_c = deal.get("jetaDocumentsCountForDeal")
    try:
        doc_count = int(raw_c) if raw_c is not None else 0
    except (TypeError, ValueError):
        doc_count = 0
    documents_ok = file_flag and doc_count > 0

    if not fuel:
        findings.append(
            {
                "code": "FUEL_DELIVERY_NOT_CONFIRMED",
                "severity": "medium",
                "message": "Fuel delivery must be confirmed (fuelDeliveryConfirmed).",
            }
        )
    if not fee_ps:
        findings.append(
            {
                "code": "FEE_PAYMENT_NOT_RECEIVED_OR_SCHEDULED",
                "severity": "medium",
                "message": "Fee payment must be received or scheduled per agreement (feePaymentReceivedOrScheduled).",
            }
        )
    if not documents_ok:
        findings.append(
            {
                "code": "DEAL_FILE_NOT_ARCHIVED_IN_DOCUMENTS",
                "severity": "medium",
                "message": "Deal file must be complete and archived in JETA_Documents — confirm dealFileCompleteInDocuments and at least one document row linked to this deal (jetaDocumentsCountForDeal).",
            }
        )

    readiness = {
        "fuel_delivery_confirmed": fuel,
        "fee_payment_received_or_scheduled": fee_ps,
        "deal_file_archived_in_documents": documents_ok,
        "jeta_documents_count": doc_count,
        "all_met": bool(fuel and fee_ps and documents_ok),
    }
    return {"findings": findings, "readiness": readiness}


def run_layer2_deal_progression_gate(
    deal_before: Dict[str, Any],
    deal_after_fields: Dict[str, Any],
    buyer: Dict[str, Any],
    new_stage: str,
) -> Dict[str, Any]:
    """
    Run when a deal attempts to move stages (deal_after_fields merged view optional).

    Returns: layer, blockers, findings, traffic_light fields, from_stage, to_stage,
      ncnda_readiness, fee_agreement_readiness (Docs Exchanged+), imfpa_document_readiness
      (IMFPA Executed+), docs_readiness (Docs Exchanged+), closure_readiness (Closed Won only),
      allowed (green without ack only; use may_proceed_traffic_light with acknowledgeManualReview)
    """
    old_stage = (deal_before.get("dealStage") or "").strip()
    to_stage = (new_stage or "").strip()
    merged = {**deal_before, **deal_after_fields}
    merged["dealStage"] = to_stage

    blockers: List[str] = []
    findings: List[Dict[str, Any]] = []
    i_old, i_new = _stage_index(old_stage), _stage_index(to_stage)
    if i_new < 0:
        msg = f"Unknown target stage: {to_stage!r}"
        blockers.append(msg)
        findings.append(
            {
                "code": "UNKNOWN_STAGE",
                "severity": "critical",
                "message": msg,
            }
        )
    if i_old >= 0 and i_new >= 0 and i_new < i_old and to_stage != "Closed Lost":
        # Allow backward moves except explicit policy — warn only, do not block by default
        pass

    deal_text = _jeta_join_screening_text(
        merged.get("dealName"),
        merged.get("dealDescription"),
        merged.get("supplySource"),
        merged.get("ncndaStatus"),
        merged.get("imfpaStatus"),
        merged.get("feeAgreementStatus"),
    )
    buyer_text = _jeta_join_screening_text(
        buyer.get("companyName"),
        buyer.get("contactName"),
        buyer.get("email"),
        buyer.get("notes"),
        buyer.get("nextAction"),
    )
    findings.extend(find_jeta_blocked_term_findings(_jeta_join_screening_text(deal_text, buyer_text)))

    for idx, gate in enumerate(_DEFAULT_GATES):
        msg = gate(merged, buyer, to_stage)
        if msg:
            blockers.append(msg)
            findings.append(
                {
                    "code": f"GATE_{idx}_{gate.__name__.lstrip('_')}",
                    "severity": "high",
                    "message": msg,
                }
            )

    ncnda_readiness: Optional[Dict[str, Any]] = None
    if i_new >= 0 and _ncnda_gate_applies(to_stage):
        nc = evaluate_ncnda_document_compliance(merged)
        findings.extend(nc["findings"])
        ncnda_readiness = nc["readiness"]

    fee_agreement_readiness: Optional[Dict[str, Any]] = None
    if i_new >= 0 and _fee_agreement_document_gate_applies(to_stage):
        fe = evaluate_fee_agreement_document_compliance(merged)
        findings.extend(fe["findings"])
        fee_agreement_readiness = fe["readiness"]

    imfpa_document_readiness: Optional[Dict[str, Any]] = None
    if i_new >= 0 and _imfpa_document_gate_applies(to_stage):
        imd = evaluate_imfpa_document_compliance(merged)
        findings.extend(imd["findings"])
        imfpa_document_readiness = imd["readiness"]

    docs_readiness: Optional[Dict[str, Any]] = None
    if i_new >= 0 and _docs_exchanged_gate_applies(to_stage):
        dc = evaluate_docs_exchanged_compliance(merged)
        findings.extend(dc["findings"])
        docs_readiness = dc["readiness"]

    closure_readiness: Optional[Dict[str, Any]] = None
    if i_new >= 0 and _closed_won_gate_applies(to_stage):
        cl = evaluate_deal_closure_compliance(merged)
        findings.extend(cl["findings"])
        closure_readiness = cl["readiness"]

    traffic = apply_traffic_light(findings)
    allowed = may_proceed_traffic_light(traffic, False, False)

    out: Dict[str, Any] = {
        "layer": 2,
        "allowed": allowed,
        "blockers": blockers,
        "findings": findings,
        "from_stage": old_stage,
        "to_stage": to_stage,
        "checked_at": datetime.utcnow().isoformat() + "Z",
    }
    if ncnda_readiness is not None:
        out["ncnda_readiness"] = ncnda_readiness
    if fee_agreement_readiness is not None:
        out["fee_agreement_readiness"] = fee_agreement_readiness
    if imfpa_document_readiness is not None:
        out["imfpa_document_readiness"] = imfpa_document_readiness
    if docs_readiness is not None:
        out["docs_readiness"] = docs_readiness
    if closure_readiness is not None:
        out["closure_readiness"] = closure_readiness
    out.update(traffic)
    return out


# ---------------------------------------------------------------------------
# Layer 3 — Continuous monitoring (batch)
# ---------------------------------------------------------------------------

def _parse_date(s: Optional[str]) -> Optional[datetime]:
    if not s or not isinstance(s, str):
        return None
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})", s.strip())
    if not m:
        return None
    try:
        return datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    except ValueError:
        return None


def run_layer3_continuous_monitoring(
    deals: List[Dict[str, Any]],
    buyers_by_id: Dict[str, Dict[str, Any]],
    outreach_rows: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Run across all active deals (typically daily).

    deals: serialized JETA deals (camelCase from API).
    buyers_by_id: buyer id -> serialized buyer.
    outreach_rows: raw outreach serialized rows with buyerId, touchDate.
    """
    today = datetime.utcnow().date()
    week_ago = today - timedelta(days=7)

    last_touch_by_buyer: Dict[str, datetime] = {}
    for row in outreach_rows:
        bid = row.get("buyerId") or ""
        if not bid:
            continue
        td = _parse_date(row.get("touchDate"))
        if not td:
            continue
        d = datetime(td.year, td.month, td.day)
        prev = last_touch_by_buyer.get(bid)
        if prev is None or d > prev:
            last_touch_by_buyer[bid] = d

    closed = frozenset({"Closed Won", "Closed Lost"})
    alerts: List[Dict[str, Any]] = []

    for deal in deals:
        stage = (deal.get("dealStage") or "").strip()
        if stage in closed:
            continue
        deal_id = deal.get("id") or ""
        bid = deal.get("buyerId") or ""
        buyer = buyers_by_id.get(bid, {})
        ntd = _parse_date(buyer.get("nextTouchDate"))
        if ntd and ntd.date() <= today:
            alerts.append(
                {
                    "type": "OUTREACH_DUE",
                    "severity": "medium",
                    "deal_id": deal_id,
                    "buyer_id": bid,
                    "message": "Buyer next touch date is due or overdue.",
                }
            )

        lt = last_touch_by_buyer.get(bid)
        lcd = _parse_date(buyer.get("lastContactDate"))
        last_act = lt
        if lcd:
            lcd_d = datetime(lcd.year, lcd.month, lcd.day)
            if last_act is None or lcd_d > last_act:
                last_act = lcd_d
        if last_act is None or last_act.date() < week_ago:
            alerts.append(
                {
                    "type": "STALE_ACTIVITY",
                    "severity": "medium",
                    "deal_id": deal_id,
                    "buyer_id": bid,
                    "message": "No outreach or last-contact activity in the last 7 days.",
                }
            )

        vol = float(deal.get("volumeGallons") or 0)
        if vol <= 0 and stage not in ("Qualifying",):
            alerts.append(
                {
                    "type": "ZERO_VOLUME",
                    "severity": "low",
                    "deal_id": deal_id,
                    "buyer_id": bid,
                    "message": "Deal volume is zero while stage has advanced past Qualifying.",
                }
            )

    return {
        "layer": 3,
        "run_at": datetime.utcnow().isoformat() + "Z",
        "active_deals_scanned": sum(1 for d in deals if (d.get("dealStage") or "") not in closed),
        "alert_count": len(alerts),
        "alerts": alerts,
    }
