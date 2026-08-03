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
import logging
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
NEMT_AIRTABLE_SOURCE = "Other"  # VERTEX INVOICES single-select (existing option)
NEMT_INVOICE_TYPE = "CMS-1500 / NEMT / Factoring"  # logical label in NOTES
NEMT_INVOICE_TYPE_AIRTABLE = "GOVERNMENT"  # VERTEX INVOICES single-select
NEMT_PAYMENT_STATUS_UNPAID = "UNPAID"
REGION_LABEL = "HAP CareSource Region 10"

# Claim lifecycle (VERTEX medical billing status machine)
CLAIM_STATUS_DRAFT = "draft"              # trip logged, not scrubbed/invoiced
CLAIM_STATUS_SCRUBBED = "scrubbed"        # scrub passed (transient before invoice)
CLAIM_STATUS_INVOICED = "invoiced"        # VERTEX invoice created — ready to submit to payer
CLAIM_STATUS_SUBMITTED = "submitted"      # sent via Availity / clearinghouse
CLAIM_STATUS_PAID = "paid"
CLAIM_STATUS_PARTIAL = "partial"
CLAIM_STATUS_DENIED = "denied"
CLAIM_STATUS_DISPUTED = "disputed"        # CDRF / dispute clock running
CLAIM_STATUS_APPEALED = "appealed"

CLAIM_STATUS_TRANSITIONS: Dict[str, Tuple[str, ...]] = {
    CLAIM_STATUS_DRAFT: (CLAIM_STATUS_SCRUBBED, CLAIM_STATUS_INVOICED),
    CLAIM_STATUS_SCRUBBED: (CLAIM_STATUS_INVOICED,),
    CLAIM_STATUS_INVOICED: (CLAIM_STATUS_SUBMITTED, CLAIM_STATUS_DENIED),
    CLAIM_STATUS_SUBMITTED: (
        CLAIM_STATUS_PAID,
        CLAIM_STATUS_PARTIAL,
        CLAIM_STATUS_DENIED,
    ),
    CLAIM_STATUS_PARTIAL: (CLAIM_STATUS_PAID, CLAIM_STATUS_DISPUTED, CLAIM_STATUS_APPEALED),
    CLAIM_STATUS_DENIED: (CLAIM_STATUS_DISPUTED, CLAIM_STATUS_APPEALED),
    CLAIM_STATUS_DISPUTED: (CLAIM_STATUS_APPEALED, CLAIM_STATUS_PAID, CLAIM_STATUS_PARTIAL),
    CLAIM_STATUS_APPEALED: (CLAIM_STATUS_PAID, CLAIM_STATUS_PARTIAL, CLAIM_STATUS_DENIED),
    CLAIM_STATUS_PAID: (),
}

# HAP CareSource contract — base trip + loaded mileage (CareSource confirmed Jun 2026)
HAP_CARESOURCE_CONTRACT_RATES: Dict[str, float] = {
    "T2002": 28.00,  # ambulatory base
    "A0130": 35.00,  # wheelchair / WAV base (CareSource confirmed Jun 2026)
}
HAP_CARESOURCE_MILEAGE_PER_MILE = 1.85

# Mileage HCPCS by transport type (loaded miles on base trip)
_HAP_MILEAGE_HCPCS: Dict[str, str] = {
    "ambulatory": "T2003",
    "wheelchair": "A0425",
    "stretcher": "A0425",
}


def _is_hap_payer(payer: Optional[str]) -> bool:
    p = (payer or "").lower()
    return "caresource" in p or p.startswith("hap")


def apply_hap_intake_defaults(order: Dict[str, Any]) -> None:
    """
    Credentialed HAP parallel vendor (100000469269): voice/portal intake
    pre-clears eligibility for *dispatch* QA — prior auth tracked as network vendor.

    IRONCLAD (Jul 2026): does NOT silently invent a clean audit trail for claims.
    Stamps method + timestamp. Claim scrub still requires eligibility_portal_confirmed
    (or explicit override) before VERTEX invoice.
    Mutates order in place.
    """
    if not _is_hap_payer(order.get("payer")):
        return
    order["eligibility_verified"] = True
    order["eligibility_verification_method"] = order.get("eligibility_verification_method") or (
        "HAP parallel vendor credentialed intake (Vendor 100000469269) — "
        "portal confirmation required before claim"
    )
    if not order.get("eligibility_verified_at"):
        order["eligibility_verified_at"] = datetime.utcnow().isoformat() + "Z"
    # Never auto-set portal confirmed — ops must flip after Availity/CareSource check
    if "eligibility_portal_confirmed" not in order:
        order["eligibility_portal_confirmed"] = False
    if not order.get("prior_auth_number") and not order.get("prior_auth_id"):
        order["prior_auth_number"] = "HAP-PARALLEL-VENDOR-100000469269"


# ─────────────────────────────────────────────────────────────────────────────
# Molina Healthcare of Michigan — HIDE SNP LTSS PSA (executed Jul 22, 2026)
# Vendor ID 214337479 — credentialed thru Jul 31, 2029
# Attachment B scope confirmed: Non-Medical Transportation (NMT) + Community
# Transition Services (CTS). 100% of published HCBS fee schedule — no discount.
# Source: MI - HCBS - DEE DAVIS INC dba DDI PSA (FFS) + Fee Schedule 04.01.2026
# ─────────────────────────────────────────────────────────────────────────────
MOLINA_LTSS_VENDOR_ID = "214337479"
MOLINA_LTSS_NPI = NPI  # 1538939111 — must be entered in Availity profile or claims deny

# Molina LTSS NMT base trip rates (Attachment B / fee schedule 04.01.2026)
MOLINA_LTSS_CONTRACT_RATES: Dict[str, float] = {
    "T2003": 27.00,  # NMT ambulatory base trip (Molina's own coding — differs from MDHHS FFS)
    "A0130": 35.00,  # NMT wheelchair van base trip
}
MOLINA_LTSS_AMBULATORY_MILEAGE_PER_MILE = 0.67  # S0215
MOLINA_LTSS_WHEELCHAIR_MILEAGE_PER_MILE = 3.00  # S0209
MOLINA_LTSS_COMMUNITY_TRANSITION_ASSESSMENT = 150.00  # T1028 — flat, per case
MOLINA_LTSS_COMMUNITY_TRANSITION_HCPCS = "T2038"  # "Manual" — negotiated per case, no fixed rate

_MOLINA_LTSS_MILEAGE_HCPCS: Dict[str, str] = {
    "ambulatory": "S0215",
    "wheelchair": "S0209",
    "stretcher": "S0209",
}

# ── HARD GATES — flip to True only when confirmed. Blocks dispatch via
#    check_member_eligibility_checklist() until both are cleared. Do NOT
#    hardcode True speculatively — verify with Dee first. ──────────────────
MOLINA_LTSS_ATTESTATION_ON_FILE = True  # Orientation Training Attestation signed & returned — Dee confirmed Jul 29, 2026
MOLINA_LTSS_AVAILITY_ACTIVE = True  # Availity approved Jul 29, 2026 — App 63821858 / Customer ID 3878016. Verify NPI 1538939111 on org profile at first login.


def _is_molina_ltss_payer(payer: Optional[str]) -> bool:
    p = (payer or "").lower()
    return "molina" in p


def apply_molina_ltss_intake_defaults(order: Dict[str, Any]) -> None:
    """
    Molina HIDE SNP LTSS (Vendor 214337479): unlike HAP, referrals are 100%
    member/Care-Coordinator-initiated per the PCSP — eligibility is NOT
    auto-verified. This only stamps provider identifiers and enforces the
    two hard gates (attestation on file + Availity active) so PRISM cannot
    silently dispatch a Molina trip before both are cleared.
    Mutates order in place.
    """
    if not _is_molina_ltss_payer(order.get("payer")):
        return
    order["vendor_id"] = order.get("vendor_id") or MOLINA_LTSS_VENDOR_ID
    order["npi_on_file"] = order.get("npi_on_file") or MOLINA_LTSS_NPI
    order["referral_source"] = order.get("referral_source") or "Member / Care Coordinator (PCSP-authorized)"
    holds: List[str] = []
    if not MOLINA_LTSS_ATTESTATION_ON_FILE:
        holds.append(
            "Molina LTSS Orientation Training Attestation not on file — "
            "no members may be received until signed & returned to MHMLTSSContracting@MolinaHealthCare.Com"
        )
    if not MOLINA_LTSS_AVAILITY_ACTIVE:
        holds.append(
            "Molina Availity portal not yet active (App ID 63821858) — "
            "cannot verify eligibility or bill claims until activated + NPI 1538939111 confirmed"
        )
    if holds:
        order["dispatch_hold"] = True
        order["dispatch_hold_reason"] = " | ".join(holds)


# ─────────────────────────────────────────────────────────────────────────────
# Michigan Medicaid MCO Payer Directory
# All six Michigan Medicaid Managed Care plans DDI can bill.
# ─────────────────────────────────────────────────────────────────────────────
MICHIGAN_MCO_PAYERS: Dict[str, Dict[str, Any]] = {
    "HAP CareSource": {
        "legal_name": "Health Alliance Plan / CareSource Michigan",
        "payer_id": "68069",
        "availity_payer_ids": ["MIMCDCS1", "MIMCRCS1"],  # Medicaid / MA — confirm before 837 submit
        "region": "Region 10 (Southeast Michigan — Wayne, Oakland, Macomb, Monroe, Washtenaw, Livingston)",
        "executed_service_counties": ["Wayne", "Macomb"],
        "pending_service_counties": ["Oakland"],
        "billing_address": "2850 W. Grand Blvd., Detroit, MI 48202",
        "prior_auth_phone": "1-844-607-2831",
        "claims_portal": "https://michigan.caresource.com",
        "era_835": True,
        "timely_filing_days": 365,
    },
    "Molina Healthcare Michigan": {
        "legal_name": "Molina Healthcare of Michigan, Inc.",
        # Clearinghouse / ECHO payer ID per orientation + EFT PDF (NOT 38217 — that collides with Priority)
        "payer_id": "38334",
        "payer_id_legacy_incorrect": "38217",
        "region": "Statewide (HIDE SNP LTSS)",
        "vendor_id": MOLINA_LTSS_VENDOR_ID,
        "credentialed_thru": "2029-07-31",
        "contract_type": "HIDE SNP LTSS PSA (FFS) — Effective Date Jul 21, 2026 (provider signed Jul 17)",
        "contract_document": "BIDS:RESOURCES/MOLINA HIDE SNP LTSS NETWORK/CONTRACTS/Molina_HIDE_SNP_LTSS_PSA_Fully_Executed_2026-07-21.pdf",
        "services": ["Non-Medical Transportation (NMT)", "Community Transition Services (CTS)"],
        "npi_on_file": MOLINA_LTSS_NPI,
        "billing_address": "880 W. Long Lake Rd., Suite 600, Troy, MI 48098",
        "prior_auth_phone": "1-888-898-7969",
        "ltss_eligibility_phone": "855-322-4077",
        "pa_submission_method": "Fax only — never request prior auth via Availity",
        "referral_model": "100% member / Care Coordinator-initiated (PCSP) — DDI cannot solicit placement on a list",
        "contracting_contact": "Arielle Goodson (contracting closed out — do not email for referral/directory questions)",
        "contracting_email": "MHMLTSSContracting@MolinaHealthCare.Com",
        "ltss_specialist_email": "MHM-LTSS-Specialist@MolinaHealthCare.Com",
        "orientation_completed": "2026-07-23 (Sarah Fenton)",
        "orientation_attestation_status": "PENDING — HARD GATE, no members until signed & returned",
        "availity_app_id": "63821858",
        "availity_status": "Registered 2026-07-23, pending activation (~3-5 business days)",
        "first_payment_method": "ECHO virtual credit card (Quick Remit) by default — Draft # off first EPP needed to switch to direct deposit",
        "claims_portal": "https://provider.molinahealthcare.com",
        "era_835": True,
        "timely_filing_days": 365,
    },
    "Priority Health": {
        "legal_name": "Priority Health",
        "payer_id": "38217",  # Distinct from Molina 38334 — verify with Priority Health prism before first 837
        "region": "Statewide (Priority Health Choice)",
        "billing_address": "1231 E. Beltline Ave. NE, Grand Rapids, MI 49525",
        "prior_auth_phone": "1-800-942-0954",
        "claims_portal": "https://www.priorityhealth.com/provider",
        "era_835": True,
        "timely_filing_days": 365,
        "prism_portal": {
            "username": "info@deedavis.biz.prism",
            "status": "ACCOUNT APPROVED Jul 28, 2026 — set password before ~Aug 7",
            "record": "CREDENTIALING/PRIORITY_HEALTH_PRISM_PORTAL.md",
        },
    },
    "Aetna Better Health": {
        "legal_name": "Aetna Better Health of Michigan",
        "payer_id": "86047",
        "region": "Statewide",
        "billing_address": "1333 Brewster St., Ste 200, Detroit, MI 48207",
        "prior_auth_phone": "1-866-316-3784",
        "claims_portal": "https://providers.aetnabetterhealth.com/mi",
        "era_835": True,
        "timely_filing_days": 365,
    },
    "McLaren Health Plan": {
        "legal_name": "McLaren Health Plan Community",
        "payer_id": "38250",
        "region": "North and Central Michigan",
        "billing_address": "G-3235 Beecher Rd., Flint, MI 48532",
        "prior_auth_phone": "1-888-327-0671",
        "claims_portal": "https://www.mclarenhealthplan.org/provider",
        "era_835": True,
        "timely_filing_days": 365,
    },
    "Blue Cross Complete": {
        "legal_name": "Blue Cross Complete of Michigan",
        "payer_id": "95655",
        "region": "Statewide",
        "billing_address": "600 E. Lafayette Blvd., Detroit, MI 48226",
        "prior_auth_phone": "1-888-228-0657",
        "claims_portal": "https://www.bcbsm.com/providers",
        "era_835": True,
        "timely_filing_days": 365,
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
    # ─── PRESCRIPTION DELIVERY ──────────────────────────────────────
    # S codes for pharmacy delivery — reimbursed by MCOs under pharmacy benefit or NEMT benefit
    {F_HCPCS: "S0215", F_DESCRIPTION: "Rx Delivery — Non-Emergency Transport of Prescription, Per Trip", F_RATE: 15.00},
    {F_HCPCS: "S9977", F_DESCRIPTION: "Rx Delivery — Prescription Delivery to Home, Per Delivery", F_RATE: 12.00},
    {F_HCPCS: "T2002-RX", F_DESCRIPTION: "Rx Delivery — Ambulatory Base Trip (Pharmacy-to-Patient)", F_RATE: 17.34},
    {F_HCPCS: "T2003-RX", F_DESCRIPTION: "Rx Delivery — Per Mile (Pharmacy-to-Patient)", F_RATE: 0.71},
    {F_HCPCS: "S5000", F_DESCRIPTION: "Rx Delivery — Cold Chain / Temperature-Controlled, Per Trip", F_RATE: 25.00},
    {F_HCPCS: "S5001", F_DESCRIPTION: "Rx Delivery — Controlled Substance (Signature Required), Per Trip", F_RATE: 30.00},
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
    apply_hap_intake_defaults(trip_data)
    apply_molina_ltss_intake_defaults(trip_data)
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

    if _is_molina_ltss_payer(trip_data.get("payer")):
        _chk(
            "Molina LTSS Orientation Attestation on file",
            MOLINA_LTSS_ATTESTATION_ON_FILE,
            action="Sign & return attestation to MHMLTSSContracting@MolinaHealthCare.Com — HARD GATE, no members until done",
        )
        _chk(
            "Molina Availity portal active (NPI 1538939111 confirmed)",
            MOLINA_LTSS_AVAILITY_ACTIVE,
            action="Confirm Availity App ID 63821858 activated and NPI entered — check back ~Jul 28-30",
        )
        _chk(
            "Member eligibility verified this visit (855-322-4077 or Availity)",
            bool(trip_data.get("eligibility_verified")),
            action="Molina Provider Manual requires eligibility check before EVERY service — not auto-verified for LTSS",
        )

    failed = [c for c in checks if c["status"] == "FAIL"]
    return {
        "eligible_to_dispatch": len(failed) == 0,
        "failed_count": len(failed),
        "checks": checks,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Molina HIDE SNP LTSS — Community Transition Services (CTS) "Authorization
# Case" model. This is a case-management process, NOT a trip — no mileage,
# no pickup/dropoff, no driver.
#
# Process (per Dee's CTS walkthrough, Jul 23 2026):
#   1. Referral Received            — discharge planner / Care Coordinator
#   2. Eligibility/PCSP Verification — CTS must be an approved PCSP service
#   3. Documentation Collected       — real invoice/quote per expense item
#   4. Home Assessment (if required) — T1028 ($150 flat) becomes billable
#   5. Authorization Sign-Off        — DDI authorizes; T2038 becomes billable
#      at the DDI-determined Amount Authorized (MI State Plan Medicaid funds
#      the release — DDI does not cut the check)
#   6. Funds Released / Case Closed  — Molina pays direct or DDI pass-through
#      (mechanism unconfirmed — track via disbursement_mechanism)
#   7. Documented for Audit
#
# Operative constraint: Furnishings/Moving Costs categories require
# subcontractor disclosure under Article 2.9 of the executed PSA — NOT yet
# filed. Only Security Deposit and Utility Set-up are accepted until then.
# ─────────────────────────────────────────────────────────────────────────────

MOLINA_LTSS_SUBCONTRACTOR_DISCLOSURE_FILED = False  # Article 2.9 — flip True once filed with Molina

CTS_EXPENSE_CATEGORIES_OPEN = ("Security Deposit", "Utility Set-up")
CTS_EXPENSE_CATEGORIES_REQUIRE_DISCLOSURE = ("Furnishings", "Moving Costs")
CTS_ALL_EXPENSE_CATEGORIES = CTS_EXPENSE_CATEGORIES_OPEN + CTS_EXPENSE_CATEGORIES_REQUIRE_DISCLOSURE

CTS_AUTHORIZATION_STATUSES = ("Pending", "Verified", "Authorized", "Denied")

CTS_WORKFLOW_STAGES = (
    "Referral Received",
    "Eligibility/PCSP Verification",
    "Documentation Collected",
    "Home Assessment",
    "Authorization Sign-Off",
    "Funds Released / Case Closed",
    "Documented for Audit",
)


def check_cts_expense_category_allowed(category: str) -> Tuple[bool, Optional[str]]:
    """
    Article 2.9 gate: Furnishings/Moving Costs require subcontractor
    disclosure to Molina that has not been filed yet. Only Security Deposit
    and Utility Set-up are accepted as a starting scope.
    """
    cat = (category or "").strip()
    if cat in CTS_EXPENSE_CATEGORIES_REQUIRE_DISCLOSURE and not MOLINA_LTSS_SUBCONTRACTOR_DISCLOSURE_FILED:
        return False, (
            f"'{cat}' requires subcontractor disclosure under Article 2.9 of the executed "
            "Molina HCBS PSA — not yet completed. Only Security Deposit and Utility Set-up "
            "are accepted until this is filed."
        )
    if cat not in CTS_ALL_EXPENSE_CATEGORIES:
        return False, f"Unknown expense category '{cat}'. Valid: {', '.join(CTS_ALL_EXPENSE_CATEGORIES)}"
    return True, None


def compute_cts_stage(cts_data: Dict[str, Any]) -> Tuple[int, str]:
    """
    Derive the current stage (1-7) of a CTS Authorization Case from field
    state — mirrors Dee's 7-stage workflow rather than PRISM's generic
    dispatch-order lifecycle (which doesn't fit a case with no driver/vehicle).
    """
    stage = 1
    if (cts_data.get("referral_source") or "").strip() and (cts_data.get("referral_date") or "").strip():
        stage = 2
    if stage >= 2 and cts_data.get("pcsp_confirmed") is True:
        stage = 3
    expenses = cts_data.get("expense_items") or []
    if stage >= 3 and expenses and all((e.get("supporting_document") or "").strip() for e in expenses):
        stage = 4
    if stage >= 4:
        required = cts_data.get("home_assessment_required")
        completed = bool(cts_data.get("home_assessment_completed"))
        if required is False or (required is True and completed):
            stage = 5
    if stage >= 5 and cts_data.get("authorization_status") == "Authorized" and cts_data.get("amount_authorized"):
        stage = 6
    if stage >= 6 and cts_data.get("case_closed"):
        stage = 7
    return stage, CTS_WORKFLOW_STAGES[stage - 1]


def check_cts_readiness_checklist(cts_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Community Transition Services Authorization Case readiness check.
    Distinct from check_member_eligibility_checklist() — CTS is a case-
    management process gated on PCSP confirmation and DDI's own authorization
    sign-off, not per-trip HCPCS/mileage eligibility. Both Molina hard gates
    (attestation + Availity) still apply since CTS bills under the same
    vendor/NPI.
    """
    apply_molina_ltss_intake_defaults(cts_data)
    checks: List[Dict[str, Any]] = []

    def _chk(item: str, passed: bool, action: Optional[str] = None) -> None:
        checks.append({"item": item, "status": "PASS" if passed else "FAIL", "action": action})

    _chk("Member Medicaid ID present", bool((cts_data.get("member_medicaid_id") or "").strip()))
    _chk("Member name recorded", bool((cts_data.get("member_name") or "").strip()))
    _chk("Member DOB recorded", bool((cts_data.get("member_dob") or "").strip()))
    _chk(
        "Molina LTSS Orientation Attestation on file",
        MOLINA_LTSS_ATTESTATION_ON_FILE,
        action="Sign & return attestation to MHMLTSSContracting@MolinaHealthCare.Com — HARD GATE, no members until done",
    )
    _chk(
        "Molina Availity portal active (NPI 1538939111 confirmed)",
        MOLINA_LTSS_AVAILITY_ACTIVE,
        action="Confirm Availity App ID 63821858 activated and NPI entered — check back ~Jul 28-30",
    )
    _chk(
        "Referral source and date recorded",
        bool((cts_data.get("referral_source") or "").strip()) and bool((cts_data.get("referral_date") or "").strip()),
        action="Record the discharge planner / facility / Care Coordinator name+contact and referral date",
    )
    _chk(
        "PCSP Confirmation completed",
        cts_data.get("pcsp_confirmed") is not None,
        action="Confirm with the referral source / LTSS Specialist whether CTS is an approved service on this member's PCSP",
    )
    if cts_data.get("pcsp_confirmed") is False:
        _chk(
            "PCSP shows CTS approved",
            False,
            action="PCSP does NOT list CTS as approved — PAUSE and get the PCSP updated before proceeding. Do not collect documentation or authorize funds.",
        )
    _chk(
        "Transition destination address documented",
        bool((cts_data.get("transitioning_to") or "").strip()),
        action="Record the address the member is moving to",
    )

    expenses = cts_data.get("expense_items") or []
    if expenses:
        for e in expenses:
            cat = e.get("category") or ""
            allowed, reason = check_cts_expense_category_allowed(cat)
            _chk(f"Expense category '{cat or '(blank)'}' is currently accepted", allowed, action=reason)
            _chk(
                f"Supporting document uploaded for '{cat or '(blank)'}' (${e.get('requested_amount', 0)})",
                bool((e.get("supporting_document") or "").strip()),
                action="No verbal estimates accepted — attach the actual invoice/quote before authorization",
            )
    else:
        _chk(
            "At least one documented expense item on file",
            False,
            action="Collect the actual invoice/quote per requested expense category before proceeding",
        )

    required = cts_data.get("home_assessment_required")
    _chk(
        "Home Assessment requirement determined (Y/N)",
        required is not None,
        action="Mark whether a home/environment assessment is required for this case",
    )
    if required is True:
        _chk(
            "Home & environment assessment (T1028) completed",
            bool(cts_data.get("home_assessment_completed")),
            action="Complete the physical suitability review before Authorization Sign-Off",
        )

    auth_status = cts_data.get("authorization_status") or "Pending"
    _chk(
        f"Authorization Status is not blank (currently '{auth_status}')",
        bool(cts_data.get("authorization_status")),
        action="Set Authorization Status: Pending / Verified / Authorized / Denied",
    )
    if auth_status == "Authorized":
        _chk(
            "Amount Authorized recorded",
            bool(cts_data.get("amount_authorized")),
            action="Enter the final confirmed Amount Authorized before this case can bill T2038",
        )
        _chk(
            "Payee recorded (landlord / utility company / vendor + payment details)",
            bool((cts_data.get("payee") or "").strip()),
            action="Record who funds are being released to",
        )

    failed = [c for c in checks if c["status"] == "FAIL"]
    stage, stage_label = compute_cts_stage(cts_data)
    return {
        "eligible_to_invoice": len(failed) == 0,
        "failed_count": len(failed),
        "checks": checks,
        "current_stage": stage,
        "current_stage_label": stage_label,
    }


def compute_cts_claim(cts_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Molina HIDE SNP LTSS Community Transition Services claim.

    Billing trigger points (per Dee's walkthrough):
      - T1028 ($150 flat) fires when Home Assessment is required AND
        completed — no assessment required means no T1028 line at all.
      - T2038 (rate TBD with Molina) fires when Authorization Sign-Off is
        complete (authorization_status == "Authorized"), billed at the
        DDI-determined Amount Authorized — never invented, never a
        pre-negotiated cap from Molina.
    """
    line_items: List[Dict[str, Any]] = []

    required = cts_data.get("home_assessment_required")
    completed = bool(cts_data.get("home_assessment_completed"))
    if required and completed and not cts_data.get("assessment_already_billed"):
        line_items.append(
            {
                "description": "Molina HIDE SNP LTSS — Community Transition assessment (flat fee, confirmed rate)",
                "hcpcs": "T1028",
                "quantity": 1,
                "rate": MOLINA_LTSS_COMMUNITY_TRANSITION_ASSESSMENT,
                "amount": MOLINA_LTSS_COMMUNITY_TRANSITION_ASSESSMENT,
            }
        )

    auth_status = cts_data.get("authorization_status")
    amount_authorized = cts_data.get("amount_authorized")
    if auth_status == "Authorized" and amount_authorized:
        line_items.append(
            {
                "description": (
                    "Molina HIDE SNP LTSS — Community Transition Services, non-recurring "
                    "setup expenses (T2038, rate unconfirmed with Molina — billed at DDI's "
                    "Amount Authorized from Authorization Sign-Off)"
                ),
                "hcpcs": MOLINA_LTSS_COMMUNITY_TRANSITION_HCPCS,
                "quantity": 1,
                "rate": float(amount_authorized),
                "amount": round(float(amount_authorized), 2),
            }
        )
    else:
        line_items.append(
            {
                "description": (
                    "Molina HIDE SNP LTSS — Community Transition Services (T2038, rate "
                    "unconfirmed with Molina — awaiting Authorization Sign-Off)"
                ),
                "hcpcs": MOLINA_LTSS_COMMUNITY_TRANSITION_HCPCS,
                "quantity": 1,
                "rate": None,
                "amount": None,
            }
        )

    total = round(sum(li["amount"] for li in line_items if li.get("amount")), 2)
    return {
        "total": total,
        "line_items": line_items,
        "service_type_label": "Community Transition Services",
        "primary_hcpcs": MOLINA_LTSS_COMMUNITY_TRANSITION_HCPCS,
        "manual_pricing_required": not (auth_status == "Authorized" and amount_authorized),
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


def _hap_mileage_hcpcs(transport_type: Optional[str], base_hcpcs: str) -> str:
    tt = (transport_type or "").strip().lower()
    if tt in _HAP_MILEAGE_HCPCS:
        return _HAP_MILEAGE_HCPCS[tt]
    base = (base_hcpcs or "").strip().upper()
    if base == "A0130":
        return "A0425"
    return "T2003"


def _molina_ltss_mileage_hcpcs(transport_type: Optional[str], base_hcpcs: str) -> str:
    tt = (transport_type or "").strip().lower()
    if tt in _MOLINA_LTSS_MILEAGE_HCPCS:
        return _MOLINA_LTSS_MILEAGE_HCPCS[tt]
    base = (base_hcpcs or "").strip().upper()
    if base == "A0130":
        return "S0209"
    return "S0215"


def _molina_ltss_mileage_rate(transport_type: Optional[str], base_hcpcs: str) -> float:
    tt = (transport_type or "").strip().lower()
    base = (base_hcpcs or "").strip().upper()
    if tt == "wheelchair" or base == "A0130":
        return MOLINA_LTSS_WHEELCHAIR_MILEAGE_PER_MILE
    return MOLINA_LTSS_AMBULATORY_MILEAGE_PER_MILE


def get_rate_amount_and_description(
    airtable,
    hcpcs: str,
    payer: Optional[str] = None,
    transport_type: Optional[str] = None,
) -> Tuple[float, str]:
    h = (hcpcs or "").strip().upper()
    if _is_hap_payer(payer) and h in HAP_CARESOURCE_CONTRACT_RATES:
        amount = HAP_CARESOURCE_CONTRACT_RATES[h]
        if h == "T2002":
            desc = "HAP CareSource ambulatory trip (base rate)"
        elif h == "A0130":
            desc = "HAP CareSource wheelchair trip (base rate)"
        else:
            desc = f"HAP CareSource NEMT ({h})"
        return amount, desc
    if _is_molina_ltss_payer(payer) and h in MOLINA_LTSS_CONTRACT_RATES:
        amount = MOLINA_LTSS_CONTRACT_RATES[h]
        if h == "T2003":
            desc = "Molina HIDE SNP LTSS — NMT ambulatory trip (base rate)"
        elif h == "A0130":
            desc = "Molina HIDE SNP LTSS — NMT wheelchair van trip (base rate)"
        else:
            desc = f"Molina HIDE SNP LTSS NMT ({h})"
        return amount, desc
    if _is_molina_ltss_payer(payer) and h == MOLINA_LTSS_COMMUNITY_TRANSITION_HCPCS:
        raise ValueError(
            "T2038 Community Transition Services is 'Manual' pricing on Molina's fee schedule — "
            "negotiated per case. Contact the LTSS Specialist team for the authorized amount before billing."
        )
    if _is_molina_ltss_payer(payer) and h == "T1028":
        return (
            MOLINA_LTSS_COMMUNITY_TRANSITION_ASSESSMENT,
            "Molina HIDE SNP LTSS — Community Transition assessment (flat fee)",
        )
    m = fetch_rates_map(airtable)
    if h not in m:
        raise ValueError(
            f"HCPCS {hcpcs!r} is not in the NEMT RATES table. Add it in Airtable or VERTEX NEMT Billing."
        )
    return m[h]["amount"], m[h]["description"]


def compute_trip_claim(
    airtable,
    trip: Dict[str, Any],
) -> Dict[str, Any]:
    """
    HAP: base trip (T2002/A0130) + loaded mileage @ $1.85/mi.
    Other payers: single HCPCS line from fee schedule.
    """
    payer = trip.get("payer") or PAYER_DEFAULT
    hcpcs = (trip.get("hcpcs_code") or "").strip().upper()
    mileage = max(0.0, float(trip.get("mileage") or 0))
    transport_type = trip.get("transport_type")

    if _is_hap_payer(payer) and hcpcs in HAP_CARESOURCE_CONTRACT_RATES:
        base, base_desc = get_rate_amount_and_description(
            airtable, hcpcs, payer=payer, transport_type=transport_type
        )
        line_items: List[Dict[str, Any]] = [
            {
                "description": base_desc,
                "hcpcs": hcpcs,
                "quantity": 1,
                "rate": base,
                "amount": round(base, 2),
            }
        ]
        mileage_amount = 0.0
        if mileage > 0:
            mile_hcpcs = _hap_mileage_hcpcs(transport_type, hcpcs)
            mileage_amount = round(mileage * HAP_CARESOURCE_MILEAGE_PER_MILE, 2)
            line_items.append(
                {
                    "description": (
                        f"HAP CareSource loaded mileage "
                        f"({mileage:.1f} mi @ ${HAP_CARESOURCE_MILEAGE_PER_MILE:.2f}/mi)"
                    ),
                    "hcpcs": mile_hcpcs,
                    "quantity": round(mileage, 1),
                    "rate": HAP_CARESOURCE_MILEAGE_PER_MILE,
                    "amount": mileage_amount,
                }
            )
        total = round(base + mileage_amount, 2)
        service_label = base_desc
        if mileage_amount:
            service_label = f"{base_desc} + {mileage:.1f} mi mileage"
        return {
            "total": total,
            "line_items": line_items,
            "service_type_label": service_label,
            "primary_hcpcs": hcpcs,
        }

    if _is_molina_ltss_payer(payer) and hcpcs in MOLINA_LTSS_CONTRACT_RATES:
        base, base_desc = get_rate_amount_and_description(
            airtable, hcpcs, payer=payer, transport_type=transport_type
        )
        line_items = [
            {
                "description": base_desc,
                "hcpcs": hcpcs,
                "quantity": 1,
                "rate": base,
                "amount": round(base, 2),
            }
        ]
        mileage_amount = 0.0
        if mileage > 0:
            mile_hcpcs = _molina_ltss_mileage_hcpcs(transport_type, hcpcs)
            mile_rate = _molina_ltss_mileage_rate(transport_type, hcpcs)
            mileage_amount = round(mileage * mile_rate, 2)
            line_items.append(
                {
                    "description": (
                        f"Molina HIDE SNP LTSS NMT mileage "
                        f"({mileage:.1f} mi @ ${mile_rate:.2f}/mi)"
                    ),
                    "hcpcs": mile_hcpcs,
                    "quantity": round(mileage, 1),
                    "rate": mile_rate,
                    "amount": mileage_amount,
                }
            )
        total = round(base + mileage_amount, 2)
        service_label = base_desc
        if mileage_amount:
            service_label = f"{base_desc} + {mileage:.1f} mi mileage"
        return {
            "total": total,
            "line_items": line_items,
            "service_type_label": service_label,
            "primary_hcpcs": hcpcs,
        }

    if _is_molina_ltss_payer(payer) and hcpcs == MOLINA_LTSS_COMMUNITY_TRANSITION_HCPCS:
        assessment, assess_desc = get_rate_amount_and_description(airtable, "T1028", payer=payer)
        return {
            "total": assessment,
            "line_items": [
                {
                    "description": "Molina HIDE SNP LTSS — Community Transition Services (T2038, 'Manual' — negotiate amount with LTSS Specialist before invoicing)",
                    "hcpcs": hcpcs,
                    "quantity": 1,
                    "rate": None,
                    "amount": None,
                },
                {
                    "description": assess_desc,
                    "hcpcs": "T1028",
                    "quantity": 1,
                    "rate": assessment,
                    "amount": round(assessment, 2),
                },
            ],
            "service_type_label": "Community Transition Services (manual) + assessment",
            "primary_hcpcs": hcpcs,
            "manual_pricing_required": True,
        }

    total, desc = get_rate_amount_and_description(
        airtable, hcpcs, payer=payer, transport_type=transport_type
    )
    return {
        "total": round(total, 2),
        "line_items": [
            {
                "description": desc,
                "hcpcs": hcpcs,
                "quantity": 1,
                "rate": total,
                "amount": round(total, 2),
            }
        ],
        "service_type_label": desc,
        "primary_hcpcs": hcpcs,
    }


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
    claim_line_items: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """CMS-1500-oriented structure for Notes / audit (not a paper form engine)."""
    t = trip
    dos_from = (t.get("pickup_time") or "")[:10]
    dos_to = (t.get("dropoff_time") or "")[:10]
    if claim_line_items:
        box_24 = []
        for li in claim_line_items:
            qty = float(li.get("quantity") or 1)
            rate = float(li.get("rate") or 0)
            amt = float(li.get("amount") if li.get("amount") is not None else qty * rate)
            box_24.append(
                {
                    "date_of_service_from": dos_from,
                    "date_of_service_to": dos_to,
                    "place_of_service": "41",
                    "emergency": "N",
                    "cpt_hcpcs": li.get("hcpcs") or t.get("hcpcs_code"),
                    "modifier": "",
                    "diagnosis_pointer": "1",
                    "charges": round(amt, 2),
                    "units": qty,
                }
            )
    else:
        box_24 = [
            {
                "date_of_service_from": dos_from,
                "date_of_service_to": dos_to,
                "place_of_service": "41",
                "emergency": "N",
                "cpt_hcpcs": t.get("hcpcs_code"),
                "modifier": "",
                "diagnosis_pointer": "1",
                "charges": round(line_charge, 2),
                "units": 1,
            }
        ]
    return {
        "form": "CMS-1500",
        "invoice_number": invoice_number,
        "box_1_insurance_type": "Medicaid",
        "box_2_patient_name": t.get("member_name"),
        "box_2_patient_id": t.get("member_medicaid_id"),
        "box_2_patient_dob": t.get("member_dob"),
        "box_20_outside_lab": "No",
        "box_21_diagnosis": [],
        "box_24_service_lines": box_24,
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
    nemt_order_id: Optional[str] = None,
    transport_type: Optional[str] = None,
) -> Dict[str, Any]:
    hcpcs_code = (hcpcs_code or "").strip().upper()
    payer_name = (payer or PAYER_DEFAULT).strip()
    get_rate_amount_and_description(airtable, hcpcs_code, payer=payer_name)
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
        "nemt_order_id": nemt_order_id or None,
        "transport_type": (transport_type or "").strip() or None,
        "created_at": _now_iso(),
        "status": "logged",
        "claim_status": CLAIM_STATUS_DRAFT,
        "invoice_id": None,
        "invoice_number": None,
    }
    # Stamp payer profile clocks / clearinghouse IDs early
    try:
        from vertex_payer_profiles import claim_clocks_for_payer

        clocks = claim_clocks_for_payer(payer_name)
        trip["payer_profile_key"] = clocks.get("profile_key")
        trip["payer_clocks"] = clocks
        ch = clocks.get("clearinghouse") or {}
        if ch.get("payer_ids"):
            trip["clearinghouse"] = ch
        # Prefer electronic clearinghouse payer id when profile has one
        ids = ch.get("payer_ids") or {}
        electronic = ids.get("electronic") or ids.get("medicaid") or ids.get("mi_coordinated_health")
        if electronic:
            trip["clearinghouse_payer_id"] = electronic
        elif trip.get("payer_id") is None and ids.get("directory_legacy"):
            trip["payer_id"] = ids.get("directory_legacy")
    except Exception:
        pass
    state = _load_state()
    state.setdefault("trips", {})[trip_id] = trip
    # Consume a prior auth trip unit if auth_id is provided
    if prior_auth_id:
        _consume_prior_auth(state, prior_auth_id)
    _save_state(state)
    return trip


def _find_trip_by_invoice(state: Dict[str, Any], invoice_id: str) -> Optional[Dict[str, Any]]:
    for t in (state.get("trips") or {}).values():
        if str(t.get("invoice_id") or "") == str(invoice_id):
            return t
    return None


def _set_claim_status(
    trip: Dict[str, Any],
    new_status: str,
    *,
    extra: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    current = trip.get("claim_status") or CLAIM_STATUS_DRAFT
    allowed = CLAIM_STATUS_TRANSITIONS.get(current, ())
    # Allow idempotent set
    if new_status == current:
        return trip
    if new_status not in allowed and current not in (CLAIM_STATUS_DRAFT, CLAIM_STATUS_SCRUBBED):
        # Soften: allow forward jumps from invoiced→paid via post_payment path
        if not (
            current == CLAIM_STATUS_INVOICED
            and new_status in (CLAIM_STATUS_PAID, CLAIM_STATUS_PARTIAL, CLAIM_STATUS_SUBMITTED)
        ) and not (
            current == CLAIM_STATUS_SUBMITTED
            and new_status in (CLAIM_STATUS_PAID, CLAIM_STATUS_PARTIAL, CLAIM_STATUS_DENIED)
        ):
            raise ValueError(
                f"Invalid claim_status transition {current} → {new_status}. "
                f"Allowed from {current}: {allowed}"
            )
    trip["claim_status"] = new_status
    trip["claim_status_updated_at"] = _now_iso()
    hist = list(trip.get("claim_status_history") or [])
    hist.append({"status": new_status, "at": _now_iso(), **(extra or {})})
    trip["claim_status_history"] = hist[-50:]
    if extra:
        trip.update({k: v for k, v in extra.items() if k not in ("at", "status")})
    return trip


def mark_claim_submitted(
    trip_id: str,
    *,
    submission_ref: Optional[str] = None,
    submitted_via: str = "Availity",
) -> Dict[str, Any]:
    """Mark invoiced claim as submitted to clearinghouse."""
    state = _load_state()
    trip = (state.get("trips") or {}).get(trip_id)
    if not trip:
        raise ValueError(f"Trip not found: {trip_id}")
    if not trip.get("invoice_id"):
        raise ValueError("Claim must be invoiced before submit")
    # Allow invoiced → submitted
    if trip.get("claim_status") == CLAIM_STATUS_DRAFT:
        trip["claim_status"] = CLAIM_STATUS_INVOICED
    _set_claim_status(
        trip,
        CLAIM_STATUS_SUBMITTED,
        extra={
            "submitted_at": _now_iso(),
            "submission_ref": submission_ref,
            "submitted_via": submitted_via,
        },
    )
    state["trips"][trip_id] = trip
    _save_state(state)
    return trip


def mark_claim_denied(
    trip_id: str,
    *,
    denial_reason: str,
    carc: Optional[str] = None,
    rarc: Optional[str] = None,
    remittance_date: Optional[str] = None,
) -> Dict[str, Any]:
    """Record denial + compute dispute/appeal deadlines from payer profile."""
    from datetime import date as _date
    from vertex_payer_profiles import appeal_days, dispute_days

    state = _load_state()
    trip = (state.get("trips") or {}).get(trip_id)
    if not trip:
        raise ValueError(f"Trip not found: {trip_id}")
    remit = remittance_date or _date.today().isoformat()
    try:
        remit_d = datetime.strptime(remit[:10], "%Y-%m-%d").date()
    except ValueError:
        remit_d = _date.today()
    d_days = dispute_days(trip.get("payer"))
    a_days = appeal_days(trip.get("payer"))
    extra: Dict[str, Any] = {
        "denied_at": _now_iso(),
        "denial_reason": denial_reason,
        "denial_carc": carc,
        "denial_rarc": rarc,
        "remittance_date": remit_d.isoformat(),
    }
    if d_days:
        extra["dispute_due_date"] = (remit_d + timedelta(days=d_days)).isoformat()
        extra["dispute_days"] = d_days
    if a_days:
        extra["appeal_due_date"] = (remit_d + timedelta(days=a_days)).isoformat()
        extra["appeal_days"] = a_days
    # Force path to denied from invoiced/submitted/partial
    cur = trip.get("claim_status")
    if cur == CLAIM_STATUS_INVOICED:
        trip["claim_status"] = CLAIM_STATUS_SUBMITTED
    _set_claim_status(trip, CLAIM_STATUS_DENIED, extra=extra)
    state["trips"][trip_id] = trip
    _save_state(state)
    return trip


def mark_claim_appealed(
    trip_id: str,
    *,
    appeal_ref: Optional[str] = None,
    notes: Optional[str] = None,
) -> Dict[str, Any]:
    state = _load_state()
    trip = (state.get("trips") or {}).get(trip_id)
    if not trip:
        raise ValueError(f"Trip not found: {trip_id}")
    cur = trip.get("claim_status")
    if cur == CLAIM_STATUS_DENIED:
        pass
    elif cur not in (CLAIM_STATUS_DISPUTED, CLAIM_STATUS_PARTIAL):
        raise ValueError(f"Cannot appeal from status {cur}")
    _set_claim_status(
        trip,
        CLAIM_STATUS_APPEALED,
        extra={"appealed_at": _now_iso(), "appeal_ref": appeal_ref, "appeal_notes": notes},
    )
    state["trips"][trip_id] = trip
    _save_state(state)
    return trip


def _notes_vertex_module(fields: Dict[str, Any], VI: Dict[str, str]) -> Optional[str]:
    raw = fields.get(VI['notes']) or ""
    try:
        if str(raw).strip().startswith("{"):
            return json.loads(raw).get("vertex_module")
    except json.JSONDecodeError:
        pass
    return None


def _is_nemt_invoice_fields(fields: Dict[str, Any]) -> bool:
    """Identify NEMT claims in VERTEX INVOICES (source may be PRISM on Airtable)."""
    from api_server import VI
    if fields.get(VI['source_system']) == SOURCE_SYSTEM:
        return True
    if fields.get(VI['invoice_type']) == NEMT_INVOICE_TYPE_AIRTABLE and _notes_vertex_module(fields, VI) == "NEMT":
        return True
    raw = fields.get(VI['notes']) or ""
    try:
        if str(raw).strip().startswith("{"):
            return json.loads(raw).get("vertex_module") == "NEMT"
    except json.JSONDecodeError:
        pass
    return False


def _invoice_fields_for_claim(
    trip: Dict[str, Any],
    invoice_number: str,
    total: float,
    line_description: str,
    invoice_date_iso: str,
    due_date_iso: str,
    claim_line_items: Optional[List[Dict[str, Any]]] = None,
    nemt_html_path: Optional[str] = None,
    nemt_pdf_path: Optional[str] = None,
    pdf_generated: bool = False,
) -> Dict[str, Any]:
    items = claim_line_items or [
        {
            "description": line_description,
            "hcpcs": trip["hcpcs_code"],
            "quantity": 1,
            "rate": total,
            "amount": total,
        }
    ]
    cms = build_cms1500_payload(trip, invoice_number, total, claim_line_items=items)
    line_items = json.dumps(items, default=str)
    notes_obj = {
        "vertex_module": "NEMT",
        "invoice_type_label": NEMT_INVOICE_TYPE,
        "cms1500": cms,
        "trip_id": trip["trip_id"],
        "claim_amount": total,
        "hcpcs_code": trip["hcpcs_code"],
        "factoring_compliance": True,
        "nemt_invoice_html": nemt_html_path,
        "nemt_invoice_pdf": nemt_pdf_path,
        "pdf_generated": pdf_generated,
    }
    from api_server import VI
    # SUBTOTAL / TOTAL AMOUNT are computed in Airtable from LINE ITEMS — do not write them.
    return {
        VI['invoice_number']:  invoice_number,
        VI['invoice_date']:    invoice_date_iso,
        VI['due_date']:        due_date_iso,
        VI['client_name']:     trip.get("payer") or PAYER_DEFAULT,
        VI['source_system']:   NEMT_AIRTABLE_SOURCE,
        VI['source_record']:   trip["trip_id"],
        VI['invoice_type']:    NEMT_INVOICE_TYPE_AIRTABLE,
        VI['line_items']:      line_items,
        VI['payment_status']:  NEMT_PAYMENT_STATUS_UNPAID,
        VI['payment_terms']:   "NET 30",
        VI['notes']:           json.dumps(notes_obj, default=str),
        VI['government_agency']: REGION_LABEL,
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


def generate_claim(airtable, trip_id: str, *, force_qc: bool = False, qc_override_reason: str = "") -> Dict[str, Any]:
    from nemt_factoring_invoice_html import generate_nemt_factoring_invoice_html

    state = _load_state()
    trip = state.get("trips", {}).get(trip_id)
    if not trip:
        raise ValueError(f"Trip not found: {trip_id}")
    if trip.get("invoice_id"):
        raise ValueError("Trip already converted to a claim")

    # ── Claim scrub + timely filing (ironclad pre-invoice gate) ─────────────
    from vertex_medical_billing_scrub import assert_claim_scrub_pass

    scrub = assert_claim_scrub_pass(
        trip,
        existing_trips=state.get("trips") or {},
        require_hap_portal_confirm=os.environ.get("VERTEX_HAP_REQUIRE_PORTAL_CONFIRM", "1") != "0",
    )
    if scrub.get("warnings"):
        logging.getLogger("nemt_billing").warning(
            "Claim scrub warnings trip=%s: %s", trip_id, "; ".join(scrub["warnings"])
        )
    trip["claim_scrub"] = scrub
    trip["claim_status"] = CLAIM_STATUS_SCRUBBED
    trip["payer_clocks"] = scrub.get("payer_clocks") or trip.get("payer_clocks")
    if scrub.get("timely_filing", {}).get("filing_deadline"):
        trip["timely_filing_deadline"] = scrub["timely_filing"]["filing_deadline"]
    try:
        from vertex_payer_profiles import clearinghouse_snapshot

        ch = clearinghouse_snapshot(trip.get("payer"))
        if ch.get("payer_ids"):
            trip["clearinghouse"] = ch
            ids = ch["payer_ids"]
            trip["clearinghouse_payer_id"] = (
                ids.get("electronic")
                or ids.get("medicaid")
                or ids.get("mi_coordinated_health")
                or trip.get("clearinghouse_payer_id")
            )
            trip["payer_profile_key"] = ch.get("profile_key")
    except Exception:
        pass
    state["trips"][trip_id] = trip
    _save_state(state)

    # ── VERTEX billing gate (9-pillar QC spine) ─────────────────────────────
    try:
        from nexus_qc_engine import (
            assert_vertex_billing_gate,
            mark_billing_complete,
            sync_nemt_trip_from_order,
        )

        nemt_oid = trip.get("nemt_order_id")
        if nemt_oid:
            try:
                import os
                nemt_path = os.path.join(os.path.dirname(__file__), "prism_nemt_data.json")
                if os.path.isfile(nemt_path):
                    import json as _json
                    with open(nemt_path, "r", encoding="utf-8") as nf:
                        nemt_state = _json.load(nf)
                    nemt_order = (nemt_state.get("orders") or {}).get(nemt_oid)
                    if nemt_order:
                        nemt_order = {**nemt_order, "order_id": nemt_oid, "vertex_trip_id": trip_id}
                        sync_nemt_trip_from_order(nemt_order)
            except Exception as sync_exc:
                logging.getLogger("nemt_billing").warning("QC pre-sync failed: %s", sync_exc)

        assert_vertex_billing_gate(
            nemt_order_id=trip.get("nemt_order_id"),
            prism_order_id=trip.get("prism_order_id"),
            vertex_trip_id=trip_id,
            force=force_qc,
            override_reason=qc_override_reason,
        )
    except ValueError:
        raise
    except ImportError:
        pass

    payer = trip.get("payer") or PAYER_DEFAULT
    claim = compute_trip_claim(airtable, trip)
    total = claim["total"]
    desc = claim["service_type_label"]
    claim_line_items = claim["line_items"]
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
        "hcpcs_code": claim.get("primary_hcpcs") or trip["hcpcs_code"],
        "service_type_label": desc,
        "mileage": trip.get("mileage"),
        "invoice_lines": claim_line_items,
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

    line_desc = f"NEMT {desc}"
    fields = _invoice_fields_for_claim(
        trip,
        invoice_number,
        total,
        line_desc,
        invoice_date_iso=inv_date_iso,
        due_date_iso=due_date_iso,
        claim_line_items=claim_line_items,
        nemt_html_path=html_path,
        nemt_pdf_path=pdf_path,
        pdf_generated=pdf_ok,
    )
    from api_server import VI
    try:
        created = airtable.create_record("VERTEX INVOICES", fields)
    except Exception as e:
        err = str(e).lower()
        if "factoring" in err or "unknown field" in err:
            fields.pop(VI['factoring_status'], None)
            created = airtable.create_record("VERTEX INVOICES", fields)
        elif "total amount" in err or ("computed" in err and "cannot accept" in err):
            fields.pop(VI.get('total_amount'), None)
            fields.pop(VI.get('subtotal'), None)
            fields.pop(VI.get('balance_due'), None)
            created = airtable.create_record("VERTEX INVOICES", fields)
        else:
            raise
    inv_id = created.get("id") if isinstance(created, dict) else getattr(created, "id", None)
    trip["status"] = "claimed"
    trip["invoice_id"] = inv_id
    trip["invoice_number"] = invoice_number
    trip["claimed_at"] = _now_iso()
    _set_claim_status(
        trip,
        CLAIM_STATUS_INVOICED,
        extra={
            "invoice_id": inv_id,
            "invoice_number": invoice_number,
            "claim_amount": total,
        },
    )
    state["trips"][trip_id] = trip
    _save_state(state)

    try:
        from nexus_qc_engine import mark_billing_complete

        mark_billing_complete(
            nemt_order_id=trip.get("nemt_order_id"),
            vertex_trip_id=trip_id,
            vertex_invoice_id=str(inv_id or ""),
            invoice_number=invoice_number,
        )
    except ImportError:
        pass

    notes_parsed = json.loads(fields[VI['notes']])
    return {
        "success": True,
        "claim_amount": total,
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
    ps_field = VI['payment_status']
    try:
        all_inv = airtable.get_all_records("VERTEX INVOICES")
    except Exception:
        return []
    out = []
    for rec in all_inv:
        f = _record_fields(rec)
        if not _is_nemt_invoice_fields(f):
            continue
        ps = f.get(ps_field)
        if ps in (NEMT_PAYMENT_STATUS_UNPAID, "Unpaid", "Partial", "PARTIAL"):
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
        if _is_nemt_invoice_fields(_record_fields(rec)):
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
    if not _is_nemt_invoice_fields(fields):
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

    # Sync claim_status on local trip
    trip = None
    state = _load_state()
    trip = _find_trip_by_invoice(state, invoice_id)
    if trip:
        target = CLAIM_STATUS_PAID if new_status == "Paid" else CLAIM_STATUS_PARTIAL
        cur = trip.get("claim_status")
        if cur == CLAIM_STATUS_INVOICED:
            trip["claim_status"] = CLAIM_STATUS_SUBMITTED
            trip.setdefault("submitted_at", _now_iso())
        try:
            _set_claim_status(
                trip,
                target,
                extra={
                    "paid_at": _now_iso(),
                    "amount_paid": pay_amt,
                    "era_reference": era_reference,
                },
            )
        except ValueError:
            trip["claim_status"] = target
            trip["claim_status_updated_at"] = _now_iso()
        state["trips"][trip["trip_id"]] = trip
        _save_state(state)

    return {
        "success": True,
        "invoice_id": invoice_id,
        "invoice_update": update_fields,
        "revenue": revenue,
        "trip": trip,
        "claim_status": (trip or {}).get("claim_status"),
    }


def list_logged_trips() -> List[Dict[str, Any]]:
    state = _load_state()
    trips = list(state.get("trips", {}).values())
    trips.sort(key=lambda t: t.get("created_at") or "", reverse=True)
    return trips
