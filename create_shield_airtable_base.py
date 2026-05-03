"""
SHIELD — Airtable Base Builder
Creates the `nexus_lead_screening` base with all 11 tables + fields,
then writes LEAD_SCREENING_BASE_ID into .env automatically.

Run once:  python3 create_shield_airtable_base.py
"""
from __future__ import annotations

import json
import os
import re
import sys
import time

import requests
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

API_KEY = os.environ.get("AIRTABLE_API_KEY", "")
WORKSPACE_ID = "wsp1XxpfjT8gDTIUJ"
BASE_NAME = "nexus_lead_screening"
META_URL = "https://api.airtable.com/v0/meta/bases"

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}

# ─────────────────────────────────────────────────────────────────────────────
# Field helpers
# ─────────────────────────────────────────────────────────────────────────────
def txt(name): return {"name": name, "type": "singleLineText"}
def mltext(name): return {"name": name, "type": "multilineText"}
def email_f(name): return {"name": name, "type": "email"}
def phone_f(name): return {"name": name, "type": "phoneNumber"}
def url_f(name): return {"name": name, "type": "url"}
def num(name, precision=2): return {"name": name, "type": "number", "options": {"precision": precision}}
def currency_f(name): return {"name": name, "type": "currency", "options": {"precision": 2, "symbol": "$"}}
def pct(name): return {"name": name, "type": "percent", "options": {"precision": 1}}
def chk(name): return {"name": name, "type": "checkbox", "options": {"icon": "check", "color": "greenBright"}}
def dt(name): return {"name": name, "type": "dateTime", "options": {"dateFormat": {"name": "us"}, "timeFormat": {"name": "12hour"}, "timeZone": "America/New_York"}}
def date_f(name): return {"name": name, "type": "date", "options": {"dateFormat": {"name": "us"}}}
def select(name, choices): return {"name": name, "type": "singleSelect", "options": {"choices": [{"name": c} for c in choices]}}
def multi(name, choices): return {"name": name, "type": "multipleSelects", "options": {"choices": [{"name": c} for c in choices]}}
def link(name, table): return {"name": name, "type": "multipleRecordLinks", "options": {"linkedTableId": table}}


# ─────────────────────────────────────────────────────────────────────────────
# Table schemas  (11 tables)
# Primary field is always first in the fields list.
# ─────────────────────────────────────────────────────────────────────────────

COUNTIES = ["Wayne", "Oakland", "Macomb", "Genesee", "Washtenaw", "Kent", "Muskegon", "Other"]

# Community SHIELD expanded service lines (5-pillar model)
SERVICE_LINES = [
    # Healthcare Access
    "NEMT", "Medical Courier", "Healthcare Navigation", "CHW Home Visit", "Nurse Home Visit",
    "Medical Monitoring", "Specimen Transport", "Lead Screening", "Lead Remediation",
    "Filter Safety Net", "CLPPP Follow-up",
    # Workforce Development
    "Drug Testing", "Fingerprinting", "Background Check", "Occupational Health",
    "DOT Physical", "Credentialing Support", "I-9 Verification",
    # Administrative Equity
    "Notary Services", "Apostille/Authentication", "Estate Planning", "Document Preparation",
    "Immigration Documents", "Vital Records", "Legal Document Support",
    # Family Stability
    "DNA Testing", "Housing Navigation", "Food Navigation", "MIBridges Benefits",
    "Court Document Support", "Child Support Navigation", "Utility Assistance",
    # Veteran Services
    "VA Navigation", "Veteran Employment", "Treatment Court Support",
    "Benefits Coordination", "DD-214 Support", "Veteran Housing",
]

TABLES = [
    {
        "name": "Referrals",
        "description": "One row per referral intake. Hub table — all service activations, milestones, and billing link here.",
        "fields": [
            txt("referral_id"),           # primary — human-readable SHD-YYYY-NNNN
            select("status", ["New", "Assigned", "Active", "Pending", "Completed", "Closed"]),
            select("stage", ["Intake", "Triage", "Outreach", "Engaged", "In Service", "Closed"]),
            select("urgency", ["Standard", "Urgent", "Emergency"]),
            select("county", COUNTIES),
            txt("referral_source"),
            txt("referring_agency"),
            txt("case_worker_name"),
            email_f("case_worker_email"),
            phone_f("case_worker_phone"),
            multi("services_requested", SERVICE_LINES),
            txt("navigator_email"),
            txt("intake_method"),
            dt("date_received"),
            dt("first_contact_at"),
            # SLA override (supervisor-only)
            num("sla_override_hours", 1),
            mltext("sla_override_reason"),
            txt("sla_override_by"),
            dt("sla_override_at"),
            # Auto-escalation audit trail
            chk("urgency_auto_escalated"),
            txt("urgency_escalated_from"),
            mltext("urgency_escalated_reason"),
            dt("urgency_escalated_at"),
            # Pilot
            txt("pilot_id"),
            mltext("notes"),
        ],
    },
    {
        "name": "Families",
        "description": "Household-level record. One per family unit. Children link here.",
        "fields": [
            txt("family_name"),
            txt("primary_contact_name"),
            txt("address"),
            txt("city"),
            txt("zip"),
            select("county", COUNTIES),
            phone_f("primary_contact_phone"),
            email_f("primary_contact_email"),
            select("insurance_type", ["Medicaid / MIChild", "CHIP", "Private Insurance", "Uninsured", "Unknown"]),
            txt("medicaid_id"),
            txt("mco_plan"),
            chk("prior_auth_on_file"),
            txt("prior_auth_number"),
            txt("insurance_carrier"),
            txt("policy_number"),
            txt("group_number"),
            select("payment_source", [
                "County grant / LHD funded",
                "MDHHS pilot program",
                "Referring agency covers cost",
                "Sliding scale / pro bono",
                "Pending Medicaid enrollment",
                "Other / Unknown",
            ]),
            txt("payment_source_detail"),
            mltext("payment_notes"),
            chk("snap_enrolled"),
            select("language", ["English", "Spanish", "Arabic", "Bengali", "Other"]),
            chk("housing_instability"),
            chk("displacement_required"),
            txt("mdhhs_case_number"),
            select("status", ["Active", "Inactive", "Closed"]),
            mltext("notes"),
        ],
    },
    {
        "name": "Children",
        "description": "One row per child. Links to Families. BLL data drives urgency auto-escalation on linked Referrals.",
        "fields": [
            txt("child_name"),
            date_f("date_of_birth"),
            num("age_months", 0),
            num("blood_lead_level", 2),
            select("lead_test_status", ["Not Tested", "Tested - Normal", "Tested - Elevated", "Confirmed EBL"]),
            select("clppp_status", ["Not Referred", "Referred", "Enrolled", "Closed"]),
            txt("clppp_case_number"),
            dt("test_date"),
            dt("clppp_referral_date"),
            chk("filter_deployed"),
            chk("remediation_scheduled"),
            txt("pediatrician_name"),
            txt("school_or_program"),
            mltext("notes"),
        ],
    },
    {
        "name": "Navigators",
        "description": "CWC/DDI staff. Role field gates SLA override capability — Supervisor and Admin only.",
        "fields": [
            txt("name"),
            email_f("email"),
            phone_f("phone"),
            select("role", ["Navigator", "Supervisor", "Admin"]),
            select("status", ["Active", "Inactive", "On Leave"]),
            multi("assigned_counties", COUNTIES),
            txt("npi"),
            txt("credential"),
            date_f("hire_date"),
            mltext("notes"),
        ],
    },
    {
        "name": "Service_Activations",
        "description": "One row per service line activated per referral. DDI admin fee tracked here.",
        "fields": [
            txt("activation_id"),
            select("service_line", SERVICE_LINES),
            select("status", ["Pending", "Pending Approval", "Auth Requested", "Active", "In Progress", "Completed", "Delivered", "Verified Complete", "Denied", "Cancelled"]),
            dt("activated_date"),
            dt("completion_date"),
            txt("vendor"),
            txt("vendor_phone"),
            txt("authorization_number"),
            dt("appointment_date"),
            txt("navigator_name"),
            mltext("verification_steps"),
            txt("billed_to"),
            currency_f("service_rate"),
            pct("admin_fee_rate"),
            currency_f("admin_fee_amount"),
            txt("prior_auth_status"),
            txt("contractor_name"),
            mltext("notes"),
        ],
    },
    {
        "name": "Case_Milestones",
        "description": "Timestamped audit log of key events per referral. Append-only by design.",
        "fields": [
            select("milestone_type", [
                "Referral Received",
                "First Contact Attempt",
                "First Contact Made",
                "Triage Completed",
                "Navigator Assigned",
                "Family Engaged",
                "Blood Lead Test Scheduled",
                "Blood Lead Test Completed",
                "EBL Confirmed",
                "CLPPP Referral Sent",
                "Housing Intake Completed",
                "Service Activated",
                "Appointment Scheduled",
                "Service Completed",
                "Prior Auth Submitted",
                "Prior Auth Approved",
                "Remediation Scheduled",
                "Filter Deployed",
                "Case Review",
                "Case Closed",
                "SLA Override (Supervisor)",
                "SLA Override Cleared",
                "Urgency Auto-Escalated",
                "Navigator Note",
                "Activity Log",
                "Other",
            ]),
            dt("timestamp"),
            txt("recorded_by"),
            mltext("notes"),
        ],
    },
    {
        "name": "Contractors",
        "description": "External vendors DDI sub-contracts for service delivery (NEMT, remediation, couriers, etc.).",
        "fields": [
            txt("company_name"),
            select("service_line", SERVICE_LINES),
            txt("contact_name"),
            txt("contact_title"),
            email_f("contact_email"),
            phone_f("contact_phone"),
            select("status", ["Active", "Pending Credentialing", "Inactive", "Preferred"]),
            multi("counties_served", COUNTIES),
            txt("license_number"),
            date_f("contract_start"),
            date_f("contract_end"),
            currency_f("rate_per_unit"),
            txt("rate_unit"),
            mltext("notes"),
        ],
    },
    {
        "name": "Billing",
        "description": "Claim-level billing records. One row per claim submission. DDI admin fee tracked separately.",
        "fields": [
            txt("claim_id"),
            select("service_line", SERVICE_LINES),
            txt("billed_to"),
            txt("payer_type"),
            currency_f("service_amount"),
            currency_f("admin_fee_amount"),
            pct("admin_fee_rate"),
            currency_f("total_billed"),
            currency_f("amount_paid"),
            select("status", ["Draft", "Ready to Submit", "Submitted", "Paid", "Partial Pay", "Denied", "Appealed", "Void"]),
            date_f("date_of_service"),
            date_f("date_submitted"),
            date_f("date_paid"),
            txt("claim_number"),
            txt("denial_reason"),
            mltext("notes"),
        ],
    },
    {
        "name": "Outcomes_Reporting",
        "description": "90-day and final outcome snapshots per child/referral. Required for MDHHS pilot reporting.",
        "fields": [
            txt("outcome_id"),
            select("reporting_period", ["30-Day", "60-Day", "90-Day", "6-Month", "Final"]),
            select("outcome_type", [
                "Lead Test Completed",
                "BLL Normalized",
                "CLPPP Enrolled",
                "Housing Remediated",
                "Services Delivered - Full",
                "Services Delivered - Partial",
                "Family Disengaged",
                "Case Closed - Positive",
                "Case Closed - Incomplete",
            ]),
            date_f("outcome_date"),
            num("bll_at_open", 2),
            num("bll_at_close", 2),
            multi("services_delivered", SERVICE_LINES),
            chk("housing_remediated"),
            chk("enrolled_medicaid"),
            chk("clppp_enrolled"),
            chk("filter_installed"),
            txt("pilot_id"),
            txt("reporting_county"),
            select("reported_to", ["MDHHS", "CLPPP", "LHD", "MCO", "Internal Only"]),
            date_f("report_submitted_date"),
            mltext("notes"),
        ],
    },
    {
        "name": "Referral_Source_Accounts",
        "description": "Organizations that refer families to SHIELD (MDHHS, LHDs, pediatricians, CPS, etc.). Seeded with MDHHS + 6 LHD placeholders.",
        "fields": [
            txt("account_name"),
            select("agency_type", [
                "State Agency",
                "Local Health Department",
                "Hospital / Health System",
                "Pediatric Practice",
                "Child Protective Services",
                "School / Head Start",
                "Community Health Center",
                "MCO / Health Plan",
                "Other",
            ]),
            select("county", COUNTIES + ["Statewide", "Multiple"]),
            txt("contact_name"),
            txt("contact_title"),
            email_f("contact_email"),
            phone_f("contact_phone"),
            select("relationship_tier", [
                "Primary — Decision Maker",
                "Secondary",
                "Pending Introduction",
                "Outreach Only",
                "Inactive",
            ]),
            select("status", ["Active", "Pending", "Inactive", "Do Not Contact"]),
            date_f("first_contact_date"),
            date_f("last_contact_date"),
            dt("last_contact_datetime"),
            chk("mdhhs_facilitated_intro"),
            txt("mdhhs_intro_status"),
            mltext("notes"),
            url_f("portal_url"),
        ],
    },
    {
        "name": "Call_Log",
        "description": "Logged inbound and outbound calls by navigators. Linked to referrals for case history.",
        "fields": [
            txt("navigator_email"),
            txt("navigator_name"),
            txt("family_name"),
            txt("phone_number"),
            select("direction", ["Outbound", "Inbound"]),
            select("outcome", ["Reached — Appointment Set", "Reached — Info Provided", "Reached — Follow-Up Needed", "Voicemail Left", "No Answer", "Wrong Number", "Refused"]),
            num("duration_seconds"),
            mltext("notes"),
            dt("called_at"),
            txt("referral_id_text"),
        ],
    },
    {
        "name": "Notification_Log",
        "description": "Audit trail for every SMS and email sent by SHIELD. Linked to referrals for dashboard visibility.",
        "fields": [
            txt("notification_id"),
            select("channel", ["sms", "email"]),
            txt("template"),
            txt("to"),
            select("status", ["Sent", "Failed", "Skipped"]),
            txt("error"),
            dt("sent_at"),
            txt("referral_id_text"),
            txt("family_id_text"),
            mltext("raw_response"),
        ],
    },
]


# ─────────────────────────────────────────────────────────────────────────────
# Step 1 — Create the base with the first table only
#          (Airtable requires at least one table on creation)
# Step 2 — Add remaining tables via PATCH /meta/bases/{baseId}/tables
# Step 3 — Write LEAD_SCREENING_BASE_ID to .env
# ─────────────────────────────────────────────────────────────────────────────

def check_existing_base() -> str | None:
    """Return base ID if nexus_lead_screening already exists."""
    r = requests.get(META_URL, headers=HEADERS, timeout=20)
    r.raise_for_status()
    for b in r.json().get("bases", []):
        if b.get("name") == BASE_NAME:
            return b["id"]
    return None


def create_base(first_table: dict) -> str:
    payload = {
        "name": BASE_NAME,
        "workspaceId": WORKSPACE_ID,
        "tables": [first_table],
    }
    r = requests.post(META_URL, headers=HEADERS, json=payload, timeout=30)
    if not r.ok:
        print("  ERROR creating base:", r.status_code, r.text[:600])
        sys.exit(1)
    data = r.json()
    base_id = data.get("id")
    print(f"  ✓ Base created: {BASE_NAME}  →  {base_id}")
    return base_id


def add_table(base_id: str, table: dict) -> str | None:
    url = f"https://api.airtable.com/v0/meta/bases/{base_id}/tables"
    r = requests.post(url, headers=HEADERS, json=table, timeout=30)
    if not r.ok:
        print(f"    ✗ {table['name']}: {r.status_code} {r.text[:300]}")
        return None
    tid = r.json().get("id")
    print(f"  ✓ Table: {table['name']}  →  {tid}")
    return tid


def get_existing_tables(base_id: str) -> dict[str, str]:
    """Return {table_name: table_id} for existing tables in the base."""
    url = f"https://api.airtable.com/v0/meta/bases/{base_id}/tables"
    r = requests.get(url, headers=HEADERS, timeout=20)
    if not r.ok:
        return {}
    return {t["name"]: t["id"] for t in r.json().get("tables", [])}


def write_env_var(key: str, value: str) -> None:
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    with open(env_path, "r") as f:
        content = f.read()
    if re.search(rf"^{key}\s*=", content, re.MULTILINE):
        content = re.sub(rf"^{key}\s*=.*$", f"{key}={value}", content, flags=re.MULTILINE)
        action = "Updated"
    else:
        content = content.rstrip("\n") + f"\n\n# SHIELD — Lead Screening Airtable base\n{key}={value}\n"
        action = "Added"
    with open(env_path, "w") as f:
        f.write(content)
    print(f"  ✓ {action} {key} in .env")


def main() -> None:
    if not API_KEY:
        print("✗ AIRTABLE_API_KEY not found in .env. Aborting.")
        sys.exit(1)

    print("\n══════════════════════════════════════════════════════")
    print("  SHIELD — Airtable Base Builder")
    print(f"  Target workspace: {WORKSPACE_ID}")
    print("══════════════════════════════════════════════════════\n")

    # ── Check if base already exists ──────────────────────────────────────────
    print("Checking for existing base …")
    existing_id = check_existing_base()
    if existing_id:
        print(f"  ✓ Base already exists: {existing_id}")
        base_id = existing_id
    else:
        # ── Create base with first table ──────────────────────────────────────
        print(f"\nCreating base '{BASE_NAME}' …")
        first_table = {k: v for k, v in TABLES[0].items() if k != "description"}
        base_id = create_base(first_table)

    # ── Check which tables already exist ──────────────────────────────────────
    print("\nInspecting existing tables …")
    existing = get_existing_tables(base_id)
    print(f"  Found {len(existing)} existing table(s): {list(existing.keys()) or 'none'}")

    # ── Create missing tables ──────────────────────────────────────────────────
    start_idx = 0 if not existing else 0
    print("\nCreating missing tables …")
    for table in TABLES:
        if table["name"] in existing:
            print(f"  – {table['name']} already exists, skipping")
            continue
        payload = {k: v for k, v in table.items() if k != "description"}
        add_table(base_id, payload)
        time.sleep(0.4)  # stay well inside Airtable rate limits

    # ── Write base ID to .env ─────────────────────────────────────────────────
    print("\nUpdating .env …")
    write_env_var("LEAD_SCREENING_BASE_ID", base_id)

    print(f"\n══════════════════════════════════════════════════════")
    print(f"  DONE.  Base ID: {base_id}")
    print(f"  LEAD_SCREENING_BASE_ID written to .env")
    print(f"\n  Next step:")
    print(f"    python3 seed_shield_referral_source_accounts.py --apply")
    print(f"  This will seed Angela Medina, Aimee Surma + 6 LHD placeholders")
    print(f"  into the Referral_Source_Accounts table.")
    print(f"══════════════════════════════════════════════════════\n")


if __name__ == "__main__":
    main()
