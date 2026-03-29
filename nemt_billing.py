"""
VERTEX NEMT Medical Billing — trip logging, CMS-1500-style claims, ERA reconciliation.

Trips are stored locally (JSON) — no trip table in Airtable. Claims and payments use
VERTEX INVOICES and VERTEX REVENUE.

Rates: read at runtime from Airtable table "NEMT RATES" (HCPCS Code, Description, Rate Amount).
Use POST /vertex/nemt/rates/seed to create placeholder rows ($0.00) if the table is empty.

Provider credentials: company_info.NPI, company_info.CHAMPS_PROVIDER_ID.
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

# Placeholder rows for seed (Dee updates Rate Amount after HAP CareSource contract review).
SEED_PLACEHOLDER_ROWS: List[Dict[str, Any]] = [
    {F_HCPCS: "T2002", F_DESCRIPTION: "Ambulatory NEMT", F_RATE: 0},
    {F_HCPCS: "A0130", F_DESCRIPTION: "Wheelchair NEMT", F_RATE: 0},
    {F_HCPCS: "A0380", F_DESCRIPTION: "Stretcher NEMT", F_RATE: 0},
]

_lock = threading.Lock()
_DATA: Optional[Dict[str, Any]] = None


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
    n = 0
    try:
        for r in airtable.get_all_records("VERTEX INVOICES"):
            f = _record_fields(r)
            if f.get("Source System") != SOURCE_SYSTEM:
                continue
            inv = str(f.get("Invoice Number") or "")
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


def fetch_rates_map(airtable) -> Dict[str, Dict[str, Any]]:
    """HCPCS (upper) → amount, description, record_id."""
    rows = airtable.get_all_records(NEMT_RATES_TABLE)
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
        }
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
        "box_2_patient_id": t.get("member_medicaid_id"),
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
        "box_25_federal_tax_id": "EIN on file",
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
) -> Dict[str, Any]:
    hcpcs_code = (hcpcs_code or "").strip().upper()
    get_rate_amount_and_description(airtable, hcpcs_code)
    trip_id = str(uuid.uuid4())
    trip = {
        "trip_id": trip_id,
        "member_medicaid_id": (member_medicaid_id or "").strip(),
        "pickup_time": pickup_time,
        "dropoff_time": dropoff_time,
        "pickup_address": pickup_address,
        "dropoff_address": dropoff_address,
        "mileage": float(mileage) if mileage is not None else 0.0,
        "trip_purpose": trip_purpose,
        "hcpcs_code": hcpcs_code,
        "payer": (payer or PAYER_DEFAULT).strip(),
        "provider_npi": NPI,
        "champs_provider_id": CHAMPS_PROVIDER_ID,
        "created_at": _now_iso(),
        "status": "logged",
        "invoice_id": None,
        "invoice_number": None,
    }
    state = _load_state()
    state.setdefault("trips", {})[trip_id] = trip
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
    return {
        "Invoice Number": invoice_number,
        "Invoice Date": invoice_date_iso,
        "Due Date": due_date_iso,
        "Client Name": trip.get("payer") or PAYER_DEFAULT,
        "Source System": SOURCE_SYSTEM,
        "Source Record ID": trip["trip_id"],
        "Invoice Type": "CMS-1500 / NEMT / Factoring",
        "Line Items": line_items,
        "Subtotal": total,
        "Total Amount": total,
        "Payment Status": "Pending",
        "Payment Terms": "Net 30",
        "Notes": json.dumps(notes_obj, default=str),
        "Government Agency": REGION_LABEL,
        "Factoring Status": FACTORING_STATUS_UNFACTORED,
    }


def get_nemt_invoice_pdf_path_from_record(invoice_record: Any) -> Optional[str]:
    """Absolute path to factoring PDF from Notes JSON, if file exists."""
    fields = _record_fields(invoice_record)
    raw = fields.get("Notes") or ""
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
            fields.pop("Factoring Status", None)
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
    formula = (
        "AND({Source System}='NEMT',OR({Payment Status}='Pending',{Payment Status}='Unpaid'))"
    )
    try:
        return airtable.search_records("VERTEX INVOICES", formula)
    except Exception:
        all_inv = airtable.get_all_records("VERTEX INVOICES")
        out = []
        for rec in all_inv:
            f = _record_fields(rec)
            if f.get("Source System") != SOURCE_SYSTEM:
                continue
            ps = f.get("Payment Status")
            if ps in ("Pending", "Unpaid"):
                out.append(rec)
        return out


def get_nemt_revenue_total(airtable) -> float:
    """Sum VERTEX REVENUE for NEMT (ERA postings)."""
    try:
        rev = airtable.search_records("VERTEX REVENUE", "{Source System}='NEMT'")
    except Exception:
        rev = []
        for r in airtable.get_all_records("VERTEX REVENUE"):
            if _record_fields(r).get("Source System") == SOURCE_SYSTEM:
                rev.append(r)
    total = 0.0
    for r in rev:
        total += float(_record_fields(r).get("Amount") or 0)
    return round(total, 2)


def get_nemt_summary(airtable) -> Dict[str, Any]:
    pending = get_pending_claims(airtable)
    total_pending = sum(float(_record_fields(r).get("Total Amount") or 0) for r in pending)

    all_nemt = []
    for rec in airtable.get_all_records("VERTEX INVOICES"):
        if _record_fields(rec).get("Source System") == SOURCE_SYSTEM:
            all_nemt.append(rec)
    total_billed = sum(float(_record_fields(r).get("Total Amount") or 0) for r in all_nemt)

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
    inv = airtable.get_record("VERTEX INVOICES", invoice_id)
    fields = _record_fields(inv)
    if fields.get("Source System") != SOURCE_SYSTEM:
        raise ValueError("Invoice is not a NEMT claim")

    ps = fields.get("Payment Status")
    if ps == "Paid":
        raise ValueError("Invoice already marked Paid")

    total = float(fields.get("Total Amount") or 0)
    pay_amt = float(amount)
    if pay_amt <= 0:
        raise ValueError("Payment amount must be positive")

    new_status = "Paid" if pay_amt >= total - 0.01 else "Partial"

    update_fields: Dict[str, Any] = {
        "Payment Status": new_status,
        "Amount Paid": pay_amt,
    }
    if new_status == "Paid":
        update_fields["Factoring Status"] = FACTORING_STATUS_PAID
    try:
        airtable.update_record("VERTEX INVOICES", invoice_id, update_fields)
    except Exception as e:
        err = str(e).lower()
        if "factoring" in err or "unknown field" in err:
            update_fields.pop("Factoring Status", None)
            airtable.update_record("VERTEX INVOICES", invoice_id, update_fields)
        else:
            raise

    rev_date = payment_date or datetime.utcnow().date().isoformat()
    note_parts = [
        f"NEMT ERA — invoice {fields.get('Invoice Number')}",
        f"invoice_record={invoice_id}",
    ]
    if era_reference:
        note_parts.append(f"ref={era_reference}")
    if notes:
        note_parts.append(notes)

    revenue_fields = {
        "Revenue Date": rev_date,
        "Source": PAYER_DEFAULT,
        "Revenue Type": "NEMT Medicaid Payment",
        "Source System": SOURCE_SYSTEM,
        "Amount": pay_amt,
        "Payment Method": "ERA",
        "Taxable": True,
        "Recurring": False,
        "Notes": " | ".join(note_parts),
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
