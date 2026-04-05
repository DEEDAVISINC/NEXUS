"""
VERTEX NEMT Medical Billing — trip logging, CMS-1500-style claims, ERA reconciliation.

Provider Credentials (Michigan MDHHS / CHAMPS):
  NPI:              1538939111
  CHAMPS Provider:  6309049

Trips are stored locally (JSON). Claims and payments use VERTEX INVOICES and VERTEX REVENUE.

Rates: pulled at runtime from Airtable "NEMT RATES" table.
Use POST /vertex/nemt/rates/seed to populate Michigan MDHHS fee-for-service rates.

Payers: HAP CareSource, Molina Healthcare Michigan, Priority Health, Aetna Better Health,
        McLaren Health Plan, Blue Cross Complete of Michigan.

Prior Auth:  stored in local JSON under state["prior_auths"].
Eligibility: required fields recorded per trip; verify via MCO portal before dispatch.
"""

from __future__ import annotations

import json
import os
import threading
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import subprocess

from company_info import (
    ADDRESS_FULL,
    CAGE_CODE,
    CHAMPS_PROVIDER_ID,
    COMPANY_NAME,
    EIN,
    NPI,
    OWNER_FULL_NAME,
    OWNER_TITLE,
)

# ─────────────────────────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────────────────────────

PAYER_DEFAULT = "HAP CareSource"
SOURCE_SYSTEM = "NEMT"
REGION_LABEL = "HAP CareSource Region 10"

# ─────────────────────────────────────────────────────────────────────────────
# Michigan Medicaid MCO Payer Directory
# All six Michigan Medicaid Managed Care plans DDI can bill.
# ─────────────────────────────────────────────────────────────────────────────
MICHIGAN_MCO_PAYERS: Dict[str, Dict[str, Any]] = {
    "HAP CareSource": {
        "legal_name": "Health Alliance Plan / CareSource Michigan",
        "payer_id": "68069",
        "region": "Region 10 (Southeast Michigan — Wayne, Oakland, Macomb, Monroe, Washtenaw, Livingston)",
        "billing_address": "2850 W. Grand Blvd., Detroit, MI 48202",
        "prior_auth_phone": "1-844-607-2831",
        "claims_portal": "https://michigan.caresource.com",
        "era_835": True,
    },
    "Molina Healthcare Michigan": {
        "legal_name": "Molina Healthcare of Michigan, Inc.",
        "payer_id": "38217",
        "region": "Statewide",
        "billing_address": "880 W. Long Lake Rd., Suite 600, Troy, MI 48098",
        "prior_auth_phone": "1-888-898-7969",
        "claims_portal": "https://provider.molinahealthcare.com",
        "era_835": True,
    },
    "Priority Health": {
        "legal_name": "Priority Health",
        "payer_id": "38217",
        "region": "Statewide (Priority Health Choice)",
        "billing_address": "1231 E. Beltline Ave. NE, Grand Rapids, MI 49525",
        "prior_auth_phone": "1-800-942-0954",
        "claims_portal": "https://www.priorityhealth.com/provider",
        "era_835": True,
    },
    "Aetna Better Health": {
        "legal_name": "Aetna Better Health of Michigan",
        "payer_id": "86047",
        "region": "Statewide",
        "billing_address": "1333 Brewster St., Ste 200, Detroit, MI 48207",
        "prior_auth_phone": "1-866-316-3784",
        "claims_portal": "https://providers.aetnabetterhealth.com/mi",
        "era_835": True,
    },
    "McLaren Health Plan": {
        "legal_name": "McLaren Health Plan Community",
        "payer_id": "38250",
        "region": "North and Central Michigan",
        "billing_address": "G-3235 Beecher Rd., Flint, MI 48532",
        "prior_auth_phone": "1-888-327-0671",
        "claims_portal": "https://www.mclarenhealthplan.org/provider",
        "era_835": True,
    },
    "Blue Cross Complete": {
        "legal_name": "Blue Cross Complete of Michigan",
        "payer_id": "95655",
        "region": "Statewide",
        "billing_address": "600 E. Lafayette Blvd., Detroit, MI 48226",
        "prior_auth_phone": "1-888-228-0657",
        "claims_portal": "https://www.bcbsm.com/providers",
        "era_835": True,
    },
}

# ─────────────────────────────────────────────────────────────────────────────
# NEMT Broker Network Directory
# Brokers dispatch trips TO DDI. DDI bills the broker (not the MCO directly).
# Broker pays DDI Net 7–30. Add broker as payer on log_trip() when trip comes via broker.
# ─────────────────────────────────────────────────────────────────────────────
NEMT_BROKERS: Dict[str, Dict[str, Any]] = {
    "Modivcare": {
        "legal_name": "Modivcare Solutions, LLC",
        "formerly": "LogistiCare",
        "michigan_mco_partners": ["HAP CareSource", "Aetna Better Health"],
        "provider_enrollment_url": "https://providerenrollment.modivcare.com",
        "provider_relations_phone": "1-877-898-9798",
        "provider_enrollment_email": "providerenrollment@modivcare.com",
        "dispatch_platform": "Modivcare Provider Portal + Phone",
        "payment_terms": "Net 15",
        "billing_address": "1000 Alderman Dr., Alpharetta, GA 30005",
        "registration_status": "NOT STARTED",
        "application_date": None,
        "approval_date": None,
        "notes": "Largest NEMT broker in Michigan. Priority registration.",
    },
    "MTM": {
        "legal_name": "Medical Transportation Management, Inc.",
        "formerly": None,
        "michigan_mco_partners": ["Molina Healthcare Michigan", "Blue Cross Complete"],
        "provider_enrollment_url": "https://www.mtm-inc.net/transportation/become-a-provider",
        "provider_relations_phone": "1-888-561-8747",
        "provider_enrollment_email": "providerenrollment@mtm-inc.net",
        "dispatch_platform": "MTM RouteMatch / Phone",
        "payment_terms": "Net 15",
        "billing_address": "16 Triad South Dr., St. Peters, MO 63376",
        "registration_status": "NOT STARTED",
        "application_date": None,
        "approval_date": None,
        "notes": "2-4 week credentialing. Requires phone interview.",
    },
    "Veyo": {
        "legal_name": "Veyo, LLC",
        "formerly": None,
        "michigan_mco_partners": ["Priority Health", "McLaren Health Plan"],
        "provider_enrollment_url": "https://veyo.com/transportation-providers",
        "provider_relations_phone": None,
        "provider_enrollment_email": "providers@veyo.com",
        "dispatch_platform": "Veyo Provider App (mobile)",
        "payment_terms": "Net 7-14",
        "billing_address": "2800 N Central Ave., Suite 1900, Phoenix, AZ 85004",
        "registration_status": "NOT STARTED",
        "application_date": None,
        "approval_date": None,
        "notes": "App-based. Drivers use Veyo Driver app. Fast onboarding.",
    },
    "SafeRide Health": {
        "legal_name": "SafeRide Health, Inc.",
        "formerly": None,
        "michigan_mco_partners": ["Various — growing Michigan presence"],
        "provider_enrollment_url": "https://www.saferidehealth.com/transportation-providers",
        "provider_relations_phone": None,
        "provider_enrollment_email": "providers@saferidehealth.com",
        "dispatch_platform": "SafeRide Provider Portal",
        "payment_terms": "Net 7",
        "billing_address": "Chicago, IL (national)",
        "registration_status": "NOT STARTED",
        "application_date": None,
        "approval_date": None,
        "notes": "Newer broker, less red tape. Fast payment. Good volume ramp.",
    },
    "Access2Care": {
        "legal_name": "Access2Care, LLC",
        "formerly": None,
        "michigan_mco_partners": ["Various MCO contracts"],
        "provider_enrollment_url": "https://www.access2care.net/provider-enrollment",
        "provider_relations_phone": "1-866-334-5818",
        "provider_enrollment_email": "providers@access2care.net",
        "dispatch_platform": "Access2Care Provider Portal",
        "payment_terms": "Net 30",
        "billing_address": "National",
        "registration_status": "NOT STARTED",
        "application_date": None,
        "approval_date": None,
        "notes": "Regional presence. Good backup network.",
    },
    "National MedTrans Network": {
        "legal_name": "National Medical Transit, Inc.",
        "formerly": "NMN",
        "michigan_mco_partners": ["Federal programs (VA, DoD)", "Various MCOs"],
        "provider_enrollment_url": "https://nationalmedicaltransit.com/provider-enrollment",
        "provider_relations_phone": None,
        "provider_enrollment_email": "enrollment@nationalmedicaltransit.com",
        "dispatch_platform": "NMN Provider Portal",
        "payment_terms": "Net 30",
        "billing_address": "National",
        "registration_status": "NOT STARTED",
        "application_date": None,
        "approval_date": None,
        "notes": "Good for VA/DoD trips. Federal NEMT opportunities.",
    },
}

# VERTEX CLIENTS — payer legal name & billing address for factoring invoices.
VERTEX_CLIENTS_TABLE = "VERTEX CLIENTS"
FC_NAME = "Client Name"
FC_LEGAL = "Legal Name"
FC_BILL_ADDR = "Billing Address"
FC_ADDR = "Address"

FACTORING_STATUS_UNFACTORED = "Unfactored"
FACTORING_STATUS_SUBMITTED = "Submitted for Factoring"
FACTORING_STATUS_FACTORED = "Factored"
FACTORING_STATUS_PAID = "Paid"

ASSIGNMENT_OF_BENEFITS = (
    "This invoice may be assigned to a third party factor. Debtor acknowledges that payment "
    "must be made directly to the assignee upon notification of assignment."
)
CERTIFICATION_STATEMENT = (
    "I certify that the services listed above were rendered as described and that this invoice is true and accurate."
)

# Airtable — create base table with these exact field names (single-line text + number).
NEMT_RATES_TABLE = "NEMT RATES"
F_HCPCS = "HCPCS Code"
F_DESCRIPTION = "Description"
F_RATE = "Rate Amount"

# Michigan MDHHS NEMT fee-for-service rates (FY 2024–2025 schedule).
# MCO negotiated rates may differ slightly — update in Airtable after contract review.
# Source: MDHHS Transportation Services Policy Manual + Medicaid Provider Directory.
SEED_PLACEHOLDER_ROWS: List[Dict[str, Any]] = [
    # Ambulatory (seated, no mobility aid)
    {F_HCPCS: "T2002", F_DESCRIPTION: "NEMT — Ambulatory, One-Way Base Trip", F_RATE: 17.34},
    # Per-mile for ambulatory loaded trips
    {F_HCPCS: "T2003", F_DESCRIPTION: "NEMT — Mileage Per Mile (Ambulatory Loaded)", F_RATE: 0.71},
    # Wheelchair van
    {F_HCPCS: "A0130", F_DESCRIPTION: "NEMT — Wheelchair Van, One-Way Base Trip", F_RATE: 46.52},
    # Wheelchair mileage
    {F_HCPCS: "A0425", F_DESCRIPTION: "NEMT — Mileage Per Mile (Wheelchair/Loaded)", F_RATE: 0.71},
    # Stretcher / gurney
    {F_HCPCS: "A0380", F_DESCRIPTION: "NEMT — Stretcher Transport, One-Way Base Trip", F_RATE: 107.18},
    # Waiting time (per 15 min beyond first 30 min)
    {F_HCPCS: "T2007", F_DESCRIPTION: "NEMT — Waiting Time per 15-Minute Increment", F_RATE: 6.25},
    # Volunteer / personal mileage reimbursement
    {F_HCPCS: "T2001", F_DESCRIPTION: "NEMT — Non-Emergency Transportation, per mile (Volunteer)", F_RATE: 0.67},
    # Bus/public transit pass assistance
    {F_HCPCS: "T2005", F_DESCRIPTION: "NEMT — Bus Ticket / Public Transit Assistance", F_RATE: 2.50},
    # Deadhead (unloaded return mileage — some MCOs pay separately)
    {F_HCPCS: "A0420", F_DESCRIPTION: "NEMT — Mileage Per Mile (Unloaded / Deadhead)", F_RATE: 0.40},
]

_lock = threading.Lock()
_DATA: Optional[Dict[str, Any]] = None

# Eligibility fields required on every trip before billing.
REQUIRED_ELIGIBILITY_FIELDS = [
    "member_medicaid_id",
    "member_name",
    "member_dob",
    "payer",
    "eligibility_verified",
]


def _data_file() -> str:
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "nemt_billing_data.json")


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
            _DATA = {"trips": {}}
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
# Prior Authorization
# ─────────────────────────────────────────────────────────────────────────────

def create_prior_auth(
    member_medicaid_id: str,
    member_name: str,
    payer: str,
    hcpcs_code: str,
    service_start_date: str,
    service_end_date: str,
    authorized_trips: int,
    auth_number: Optional[str] = None,
    notes: Optional[str] = None,
) -> Dict[str, Any]:
    """Record a prior authorization for NEMT service. Call BEFORE scheduling trips."""
    state = _load_state()
    auth_id = str(uuid.uuid4())
    auth = {
        "auth_id": auth_id,
        "member_medicaid_id": (member_medicaid_id or "").strip(),
        "member_name": (member_name or "").strip(),
        "payer": (payer or PAYER_DEFAULT).strip(),
        "hcpcs_code": (hcpcs_code or "").strip().upper(),
        "service_start_date": service_start_date,
        "service_end_date": service_end_date,
        "authorized_trips": int(authorized_trips),
        "trips_used": 0,
        "auth_number": (auth_number or "").strip() or None,
        "status": "active",
        "notes": notes or "",
        "created_at": _now_iso(),
        "payer_info": MICHIGAN_MCO_PAYERS.get(payer, {}),
    }
    state.setdefault("prior_auths", {})[auth_id] = auth
    _save_state(state)
    return auth


def get_prior_auth(auth_id: str) -> Optional[Dict[str, Any]]:
    return _load_state().get("prior_auths", {}).get(auth_id)


def list_prior_auths(member_medicaid_id: Optional[str] = None) -> List[Dict[str, Any]]:
    auths = list(_load_state().get("prior_auths", {}).values())
    if member_medicaid_id:
        auths = [a for a in auths if a.get("member_medicaid_id") == member_medicaid_id.strip()]
    auths.sort(key=lambda x: x.get("created_at") or "", reverse=True)
    return auths


def _consume_prior_auth(state: Dict[str, Any], auth_id: str) -> None:
    """Decrement remaining trips on a prior auth when a trip is logged against it."""
    auth = state.get("prior_auths", {}).get(auth_id)
    if not auth:
        return
    auth["trips_used"] = auth.get("trips_used", 0) + 1
    if auth["trips_used"] >= auth.get("authorized_trips", 0):
        auth["status"] = "exhausted"
    state["prior_auths"][auth_id] = auth


def get_mco_payer_list() -> List[Dict[str, Any]]:
    """All supported Michigan Medicaid MCOs with contact details."""
    return [
        {"payer_name": name, **info}
        for name, info in MICHIGAN_MCO_PAYERS.items()
    ]


def get_broker_list() -> List[Dict[str, Any]]:
    """All NEMT brokers DDI is registering with, plus registration status."""
    return [
        {"broker_name": name, **info}
        for name, info in NEMT_BROKERS.items()
    ]


def update_broker_status(broker_name: str, status: str, application_date: Optional[str] = None, approval_date: Optional[str] = None) -> Dict[str, Any]:
    """Update registration status for a broker."""
    if broker_name not in NEMT_BROKERS:
        raise ValueError(f"Unknown broker: {broker_name}. Valid: {list(NEMT_BROKERS.keys())}")
    NEMT_BROKERS[broker_name]["registration_status"] = status
    if application_date:
        NEMT_BROKERS[broker_name]["application_date"] = application_date
    if approval_date:
        NEMT_BROKERS[broker_name]["approval_date"] = approval_date
    return {"broker_name": broker_name, **NEMT_BROKERS[broker_name]}


def check_member_eligibility_checklist(trip_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run the NEMT eligibility pre-check before accepting a trip.
    Returns a pass/fail checklist — driver cannot dispatch until all PASS.
    """
    checks = []

    def _chk(item: str, passed: bool, action: Optional[str] = None) -> None:
        checks.append({"item": item, "status": "PASS" if passed else "FAIL", "action": action})

    mid = (trip_data.get("member_medicaid_id") or "").strip()
    _chk("Member Medicaid ID present", bool(mid))
    _chk("Member name recorded", bool((trip_data.get("member_name") or "").strip()))
    _chk("Member DOB recorded", bool((trip_data.get("member_dob") or "").strip()))
    _chk(
        "Eligibility verified with MCO",
        bool(trip_data.get("eligibility_verified")),
        action=f"Call {MICHIGAN_MCO_PAYERS.get(trip_data.get('payer',''), {}).get('prior_auth_phone', 'MCO')} or check MCO portal",
    )
    _chk(
        "Prior auth on file (if required)",
        bool(trip_data.get("prior_auth_id") or trip_data.get("prior_auth_number")),
        action="Obtain prior auth before non-urgent scheduled trips",
    )
    _chk("Pickup address complete", bool((trip_data.get("pickup_address") or "").strip()))
    _chk("Destination address complete", bool((trip_data.get("dropoff_address") or "").strip()))
    _chk("Medical appointment documented", bool((trip_data.get("trip_purpose") or "").strip()))
    _chk("HCPCS code assigned", bool((trip_data.get("hcpcs_code") or "").strip()))

    failed = [c for c in checks if c["status"] == "FAIL"]
    return {
        "eligible_to_dispatch": len(failed) == 0,
        "failed_count": len(failed),
        "checks": checks,
    }


def _record_fields(rec: Any) -> Dict[str, Any]:
    """pyairtable Record or dict → fields dict."""
    if isinstance(rec, dict):
        return dict(rec.get("fields") or {})
    raw = getattr(rec, "fields", None)
    return dict(raw) if raw is not None else {}


def _record_id(rec: Any) -> Optional[str]:
    if isinstance(rec, dict):
        return rec.get("id")
    return getattr(rec, "id", None)


def lookup_vertex_client(airtable, payer_name: str) -> Dict[str, str]:
    """Legal name + billing address from VERTEX CLIENTS (best-effort match)."""
    payer = (payer_name or "").strip()
    if not payer:
        return {"legal_name": PAYER_DEFAULT, "billing_address": ""}
    try:
        rows = airtable.get_all_records(VERTEX_CLIENTS_TABLE)
    except Exception:
        return {"legal_name": payer, "billing_address": ""}
    pl = payer.lower()
    for r in rows:
        f = _record_fields(r)
        cn = (f.get(FC_NAME) or "").strip()
        ln = (f.get(FC_LEGAL) or "").strip()
        if pl == cn.lower() or (ln and pl == ln.lower()):
            addr = f.get(FC_BILL_ADDR) or f.get(FC_ADDR) or ""
            display = ln or cn or payer
            return {"legal_name": display, "billing_address": str(addr).strip()}
    return {"legal_name": payer, "billing_address": ""}


def _next_nemt_invoice_number(airtable) -> str:
    """Sequential NEMT-INV-000001 across VERTEX INVOICES rows with Source System NEMT."""
    from api_server import VI
    n = 0
    try:
        for r in airtable.get_all_records("VERTEX INVOICES"):
            f = _record_fields(r)
            if f.get(VI['source_system']) != SOURCE_SYSTEM:
                continue
            inv = str(f.get(VI['invoice_number']) or "")
            if inv.startswith("NEMT-INV-"):
                try:
                    n = max(n, int(inv.replace("NEMT-INV-", "").strip()))
                except ValueError:
                    pass
    except Exception:
        pass
    return f"NEMT-INV-{n + 1:06d}"


def _invoice_output_dir() -> str:
    d = os.path.join(os.path.dirname(os.path.abspath(__file__)), "GENERATED_VERTEX_INVOICES", "NEMT")
    os.makedirs(d, exist_ok=True)
    return d


def write_pdf_from_html(html_path: str, pdf_path: str) -> bool:
    """NEXUS standard: wkhtmltopdf first, then WeasyPrint (same as /api/rfp/generate)."""
    pdf_generated = False
    try:
        result = subprocess.run(
            [
                "wkhtmltopdf",
                "--page-size",
                "Letter",
                "--margin-top",
                "15mm",
                "--margin-bottom",
                "15mm",
                "--margin-left",
                "15mm",
                "--margin-right",
                "15mm",
                "--enable-local-file-access",
                html_path,
                pdf_path,
            ],
            capture_output=True,
            timeout=45,
        )
        if result.returncode == 0:
            pdf_generated = True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    if not pdf_generated:
        try:
            from weasyprint import HTML

            HTML(filename=html_path).write_pdf(pdf_path)
            pdf_generated = True
        except ImportError:
            pass
    return pdf_generated


def _service_date_display(trip: Dict[str, Any]) -> str:
    pt = trip.get("pickup_time") or ""
    if len(pt) >= 10:
        return pt[:10]
    return pt or "—"


def _builtin_rates_map() -> Dict[str, Dict[str, Any]]:
    """Michigan MDHHS rates built into the system as fallback when Airtable table is unavailable."""
    m: Dict[str, Dict[str, Any]] = {}
    for row in SEED_PLACEHOLDER_ROWS:
        code = (row[F_HCPCS] or "").strip().upper()
        m[code] = {
            "amount": float(row[F_RATE]),
            "description": row[F_DESCRIPTION],
            "record_id": None,
            "source": "builtin_mdhhs",
        }
    return m


def fetch_rates_map(airtable) -> Dict[str, Dict[str, Any]]:
    """HCPCS (upper) → amount, description, record_id.
    Falls back to built-in Michigan MDHHS rates if Airtable table is missing or inaccessible."""
    try:
        rows = airtable.get_all_records(NEMT_RATES_TABLE)
    except Exception:
        # Table not yet created in Airtable — use built-in Michigan MDHHS rates
        return _builtin_rates_map()

    m: Dict[str, Dict[str, Any]] = {}
    for r in rows:
        f = _record_fields(r)
        code = (f.get(F_HCPCS) or "").strip().upper()
        if not code:
            continue
        rid = _record_id(r)
        m[code] = {
            "amount": float(f.get(F_RATE) if f.get(F_RATE) is not None else 0),
            "description": (f.get(F_DESCRIPTION) or "").strip(),
            "record_id": rid,
            "source": "airtable",
        }

    # If Airtable table exists but is empty, merge in builtins for any missing codes
    builtins = _builtin_rates_map()
    for code, info in builtins.items():
        if code not in m:
            m[code] = info

    return m


def list_nemt_rates(airtable) -> List[Dict[str, Any]]:
    """Normalized rows for API / frontend."""
    out: List[Dict[str, Any]] = []
    for r in airtable.get_all_records(NEMT_RATES_TABLE):
        f = _record_fields(r)
        out.append(
            {
                "id": _record_id(r),
                "hcpcs_code": (f.get(F_HCPCS) or "").strip(),
                "description": f.get(F_DESCRIPTION) or "",
                "rate_amount": float(f.get(F_RATE) if f.get(F_RATE) is not None else 0),
            }
        )
    out.sort(key=lambda x: (x.get("hcpcs_code") or ""))
    return out


def get_rate_amount_and_description(airtable, hcpcs: str) -> Tuple[float, str]:
    h = (hcpcs or "").strip().upper()
    m = fetch_rates_map(airtable)
    if h not in m:
        raise ValueError(
            f"HCPCS {hcpcs!r} is not in the NEMT RATES table. Add it in Airtable or VERTEX NEMT Billing."
        )
    return m[h]["amount"], m[h]["description"]


def seed_placeholder_rates(airtable) -> Dict[str, Any]:
    """Insert T2002 / A0130 / A0380 at $0.00 when missing."""
    existing = airtable.get_all_records(NEMT_RATES_TABLE)
    codes_present = {
        (_record_fields(r).get(F_HCPCS) or "").strip().upper() for r in existing
    }
    created: List[Any] = []
    for row in SEED_PLACEHOLDER_ROWS:
        code = (row[F_HCPCS] or "").strip().upper()
        if code in codes_present:
            continue
        rec = airtable.create_record(NEMT_RATES_TABLE, dict(row))
        created.append(rec)
        codes_present.add(code)
    return {"success": True, "created_count": len(created), "records": created}


def update_nemt_rate(
    airtable,
    record_id: str,
    hcpcs_code: Optional[str] = None,
    description: Optional[str] = None,
    rate_amount: Optional[float] = None,
) -> Any:
    fields: Dict[str, Any] = {}
    if hcpcs_code is not None:
        fields[F_HCPCS] = hcpcs_code.strip().upper()
    if description is not None:
        fields[F_DESCRIPTION] = description
    if rate_amount is not None:
        fields[F_RATE] = float(rate_amount)
    if not fields:
        raise ValueError("No fields to update")
    return airtable.update_record(NEMT_RATES_TABLE, record_id, fields)


def build_cms1500_payload(
    trip: Dict[str, Any],
    invoice_number: str,
    line_charge: float,
) -> Dict[str, Any]:
    """CMS-1500-oriented structure for Notes / audit (not a paper form engine)."""
    t = trip
    return {
        "form": "CMS-1500",
        "invoice_number": invoice_number,
        "box_1_insurance_type": "Medicaid",
        "box_2_patient_name": t.get("member_name"),
        "box_2_patient_id": t.get("member_medicaid_id"),
        "box_2_patient_dob": t.get("member_dob"),
        "box_20_outside_lab": "No",
        "box_21_diagnosis": [],
        "box_24_service_lines": [
            {
                "date_of_service_from": (t.get("pickup_time") or "")[:10],
                "date_of_service_to": (t.get("dropoff_time") or "")[:10],
                "place_of_service": "41",
                "emergency": "N",
                "cpt_hcpcs": t.get("hcpcs_code"),
                "modifier": "",
                "diagnosis_pointer": "1",
                "charges": round(line_charge, 2),
                "units": 1,
            }
        ],
        "box_23_prior_auth": t.get("prior_auth_number"),
        "box_25_federal_tax_id": EIN,
        "box_33_billing_provider_name": COMPANY_NAME,
        "box_33_billing_provider_npi": NPI,
        "box_33a_billing_provider_id": CHAMPS_PROVIDER_ID,
        "payer": t.get("payer") or PAYER_DEFAULT,
        "region": REGION_LABEL,
        "trip": {
            "pickup_time": t.get("pickup_time"),
            "dropoff_time": t.get("dropoff_time"),
            "pickup_address": t.get("pickup_address"),
            "dropoff_address": t.get("dropoff_address"),
            "mileage": t.get("mileage"),
            "trip_purpose": t.get("trip_purpose"),
        },
    }


def log_trip(
    airtable,
    member_medicaid_id: str,
    pickup_time: str,
    dropoff_time: str,
    pickup_address: str,
    dropoff_address: str,
    mileage: float,
    trip_purpose: str,
    hcpcs_code: str,
    payer: Optional[str] = None,
    # Eligibility / prior auth fields (required for clean billing)
    member_name: Optional[str] = None,
    member_dob: Optional[str] = None,
    eligibility_verified: bool = False,
    prior_auth_id: Optional[str] = None,
    prior_auth_number: Optional[str] = None,
    driver_name: Optional[str] = None,
    vehicle_id: Optional[str] = None,
    prism_order_id: Optional[str] = None,
) -> Dict[str, Any]:
    hcpcs_code = (hcpcs_code or "").strip().upper()
    get_rate_amount_and_description(airtable, hcpcs_code)
    payer_name = (payer or PAYER_DEFAULT).strip()
    trip_id = str(uuid.uuid4())
    trip = {
        "trip_id": trip_id,
        "member_medicaid_id": (member_medicaid_id or "").strip(),
        "member_name": (member_name or "").strip(),
        "member_dob": (member_dob or "").strip(),
        "pickup_time": pickup_time,
        "dropoff_time": dropoff_time,
        "pickup_address": pickup_address,
        "dropoff_address": dropoff_address,
        "mileage": float(mileage) if mileage is not None else 0.0,
        "trip_purpose": trip_purpose,
        "hcpcs_code": hcpcs_code,
        "payer": payer_name,
        "payer_id": MICHIGAN_MCO_PAYERS.get(payer_name, {}).get("payer_id"),
        "provider_npi": NPI,
        "champs_provider_id": CHAMPS_PROVIDER_ID,
        "eligibility_verified": bool(eligibility_verified),
        "prior_auth_id": prior_auth_id or None,
        "prior_auth_number": prior_auth_number or None,
        "driver_name": driver_name or None,
        "vehicle_id": vehicle_id or None,
        "prism_order_id": prism_order_id or None,
        "created_at": _now_iso(),
        "status": "logged",
        "invoice_id": None,
        "invoice_number": None,
    }
    state = _load_state()
    state.setdefault("trips", {})[trip_id] = trip
    # Consume a prior auth trip unit if auth_id is provided
    if prior_auth_id:
        _consume_prior_auth(state, prior_auth_id)
    _save_state(state)
    return trip


def _invoice_fields_for_claim(
    trip: Dict[str, Any],
    invoice_number: str,
    total: float,
    line_description: str,
    invoice_date_iso: str,
    due_date_iso: str,
    nemt_html_path: Optional[str] = None,
    nemt_pdf_path: Optional[str] = None,
    pdf_generated: bool = False,
) -> Dict[str, Any]:
    cms = build_cms1500_payload(trip, invoice_number, total)
    line_items = json.dumps(
        [
            {
                "description": line_description,
                "hcpcs": trip["hcpcs_code"],
                "quantity": 1,
                "rate": total,
                "amount": total,
            }
        ],
        default=str,
    )
    notes_obj = {
        "vertex_module": "NEMT",
        "cms1500": cms,
        "trip_id": trip["trip_id"],
        "factoring_compliance": True,
        "nemt_invoice_html": nemt_html_path,
        "nemt_invoice_pdf": nemt_pdf_path,
        "pdf_generated": pdf_generated,
    }
    from api_server import VI
    return {
        VI['invoice_number']:  invoice_number,
        VI['invoice_date']:    invoice_date_iso,
        VI['due_date']:        due_date_iso,
        VI['client_name']:     trip.get("payer") or PAYER_DEFAULT,
        VI['source_system']:   SOURCE_SYSTEM,
        VI['source_record']:   trip["trip_id"],
        VI['invoice_type']:    "CMS-1500 / NEMT / Factoring",
        VI['line_items']:      line_items,
        VI['subtotal']:        total,
        VI['total_amount']:    total,
        VI['payment_status']:  "Unpaid",
        VI['payment_terms']:   "Net 30",
        VI['notes']:           json.dumps(notes_obj, default=str),
        VI['government_agency']: REGION_LABEL,
        VI['factoring_status']:  FACTORING_STATUS_UNFACTORED,
    }


def get_nemt_invoice_pdf_path_from_record(invoice_record: Any) -> Optional[str]:
    """Absolute path to factoring PDF from Notes JSON, if file exists."""
    from api_server import VI
    fields = _record_fields(invoice_record)
    raw = fields.get(VI['notes']) or ""
    try:
        if raw.strip().startswith("{"):
            notes = json.loads(raw)
        else:
            return None
    except json.JSONDecodeError:
        return None
    p = notes.get("nemt_invoice_pdf")
    if p and isinstance(p, str) and os.path.isfile(p):
        return p
    return None


def generate_claim(airtable, trip_id: str) -> Dict[str, Any]:
    from nemt_factoring_invoice_html import generate_nemt_factoring_invoice_html

    state = _load_state()
    trip = state.get("trips", {}).get(trip_id)
    if not trip:
        raise ValueError(f"Trip not found: {trip_id}")
    if trip.get("invoice_id"):
        raise ValueError("Trip already converted to a claim")

    total, desc = get_rate_amount_and_description(airtable, trip["hcpcs_code"])
    payer = trip.get("payer") or PAYER_DEFAULT
    client = lookup_vertex_client(airtable, payer)
    invoice_number = _next_nemt_invoice_number(airtable)

    inv_date = datetime.utcnow().date()
    due_date = inv_date + timedelta(days=30)
    inv_date_iso = inv_date.isoformat()
    due_date_iso = due_date.isoformat()
    inv_date_disp = inv_date.strftime("%B %d, %Y")
    due_date_disp = due_date.strftime("%B %d, %Y")

    safe_file = invoice_number.replace("/", "-")
    out_dir = _invoice_output_dir()
    html_path = os.path.join(out_dir, f"{safe_file}.html")
    pdf_path = os.path.join(out_dir, f"{safe_file}.pdf")

    ctx = {
        "invoice_number": invoice_number,
        "invoice_date_display": inv_date_disp,
        "due_date_display": due_date_disp,
        "payment_terms": "Net 30",
        "vendor_name": COMPANY_NAME,
        "vendor_address": ADDRESS_FULL,
        "ein": EIN,
        "cage": CAGE_CODE,
        "npi": NPI,
        "payer_legal_name": client["legal_name"],
        "payer_address": client["billing_address"],
        "service_date_display": _service_date_display(trip),
        "member_id": trip.get("member_medicaid_id"),
        "trip_origin": trip.get("pickup_address"),
        "trip_destination": trip.get("dropoff_address"),
        "hcpcs_code": trip["hcpcs_code"],
        "service_type_label": desc,
        "unit_quantity": 1,
        "unit_rate": total,
        "total_amount": total,
        "assignment_language": ASSIGNMENT_OF_BENEFITS,
        "certification_language": CERTIFICATION_STATEMENT,
        "signer_name": OWNER_FULL_NAME,
        "signer_title": OWNER_TITLE,
    }
    html_body = generate_nemt_factoring_invoice_html(ctx)
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_body)
    pdf_ok = write_pdf_from_html(html_path, pdf_path)

    line_desc = f"NEMT {desc} — {trip['hcpcs_code']}"
    fields = _invoice_fields_for_claim(
        trip,
        invoice_number,
        total,
        line_desc,
        invoice_date_iso=inv_date_iso,
        due_date_iso=due_date_iso,
        nemt_html_path=html_path,
        nemt_pdf_path=pdf_path,
        pdf_generated=pdf_ok,
    )
    try:
        created = airtable.create_record("VERTEX INVOICES", fields)
    except Exception as e:
        err = str(e).lower()
        if "factoring" in err or "unknown field" in err:
            from api_server import VI
            fields.pop(VI['factoring_status'], None)
            created = airtable.create_record("VERTEX INVOICES", fields)
        else:
            raise
    inv_id = created.get("id") if isinstance(created, dict) else getattr(created, "id", None)
    trip["status"] = "claimed"
    trip["invoice_id"] = inv_id
    trip["invoice_number"] = invoice_number
    trip["claimed_at"] = _now_iso()
    state["trips"][trip_id] = trip
    _save_state(state)

    notes_parsed = json.loads(fields["Notes"])
    return {
        "success": True,
        "trip": trip,
        "invoice": created,
        "cms1500": notes_parsed.get("cms1500"),
        "factoring_invoice": {
            "html_path": html_path,
            "pdf_path": pdf_path,
            "pdf_generated": pdf_ok,
        },
    }


def get_pending_claims(airtable) -> List[Dict[str, Any]]:
    from api_server import VI
    ss = VI['source_system']
    ps_field = VI['payment_status']
    formula = f"AND({{{ss}}}='NEMT',OR({{{ps_field}}}='Unpaid',{{{ps_field}}}='Partial'))"
    try:
        return airtable.search_records("VERTEX INVOICES", formula)
    except Exception:
        all_inv = airtable.get_all_records("VERTEX INVOICES")
        out = []
        for rec in all_inv:
            f = _record_fields(rec)
            if f.get(ss) != SOURCE_SYSTEM:
                continue
            ps = f.get(ps_field)
            if ps in ("Unpaid", "Partial"):
                out.append(rec)
        return out


def get_nemt_revenue_total(airtable) -> float:
    """Sum VERTEX REVENUE for NEMT (ERA postings)."""
    from api_server import VI, VR
    try:
        rev = airtable.search_records("VERTEX REVENUE", f"{{{VR['source_system']}}}='NEMT'")
    except Exception:
        rev = []
        for r in airtable.get_all_records("VERTEX REVENUE"):
            if _record_fields(r).get(VR['source_system']) == SOURCE_SYSTEM:
                rev.append(r)
    from api_server import VI, VR
    total = 0.0
    for r in rev:
        total += float(_record_fields(r).get(VR['amount']) or 0)
    return round(total, 2)


def get_nemt_summary(airtable) -> Dict[str, Any]:
    from api_server import VI, VR
    pending = get_pending_claims(airtable)
    total_pending = sum(float(_record_fields(r).get(VI['total_amount']) or 0) for r in pending)

    all_nemt = []
    for rec in airtable.get_all_records("VERTEX INVOICES"):
        if _record_fields(rec).get(VI['source_system']) == SOURCE_SYSTEM:
            all_nemt.append(rec)
    total_billed = sum(float(_record_fields(r).get(VI['total_amount']) or 0) for r in all_nemt)

    received = get_nemt_revenue_total(airtable)

    return {
        "total_billed_pending": round(total_pending, 2),
        "total_billed_all_claims": round(total_billed, 2),
        "total_received": received,
        "pending_count": len(pending),
    }


def post_payment(
    airtable,
    invoice_id: str,
    amount: float,
    payment_date: Optional[str] = None,
    era_reference: Optional[str] = None,
    notes: Optional[str] = None,
) -> Dict[str, Any]:
    from api_server import VI, VR
    inv = airtable.get_record("VERTEX INVOICES", invoice_id)
    fields = _record_fields(inv)
    if fields.get(VI['source_system']) != SOURCE_SYSTEM:
        raise ValueError("Invoice is not a NEMT claim")

    ps = fields.get(VI['payment_status'])
    if ps == "Paid":
        raise ValueError("Invoice already marked Paid")

    total = float(fields.get(VI['total_amount']) or 0)
    pay_amt = float(amount)
    if pay_amt <= 0:
        raise ValueError("Payment amount must be positive")

    new_status = "Paid" if pay_amt >= total - 0.01 else "Partial"

    update_fields: Dict[str, Any] = {
        VI['payment_status']: new_status,
        VI['amount_paid']:    pay_amt,
    }
    if new_status == "Paid":
        update_fields[VI['factoring_status']] = FACTORING_STATUS_PAID
    try:
        airtable.update_record("VERTEX INVOICES", invoice_id, update_fields)
    except Exception as e:
        err = str(e).lower()
        if "factoring" in err or "unknown field" in err:
            update_fields.pop(VI['factoring_status'], None)
            airtable.update_record("VERTEX INVOICES", invoice_id, update_fields)
        else:
            raise

    rev_date = payment_date or datetime.utcnow().date().isoformat()
    note_parts = [
        f"NEMT ERA — invoice {fields.get(VI['invoice_number'])}",
        f"invoice_record={invoice_id}",
    ]
    if era_reference:
        note_parts.append(f"ref={era_reference}")
    if notes:
        note_parts.append(notes)

    revenue_fields = {
        VR['revenue_date']:   rev_date,
        VR['source']:         PAYER_DEFAULT,
        VR['revenue_type']:   "NEMT Medicaid Payment",
        VR['source_system']:  SOURCE_SYSTEM,
        VR['amount']:         pay_amt,
        VR['payment_method']: "ERA",
        VR['taxable']:        True,
        VR['recurring']:      False,
        VR['notes']:          " | ".join(note_parts),
    }
    revenue = airtable.create_record("VERTEX REVENUE", revenue_fields)

    return {
        "success": True,
        "invoice_id": invoice_id,
        "invoice_update": update_fields,
        "revenue": revenue,
    }


def list_logged_trips() -> List[Dict[str, Any]]:
    state = _load_state()
    trips = list(state.get("trips", {}).values())
    trips.sort(key=lambda x: x.get("created_at") or "", reverse=True)
    return trips
