"""
HAVEN — Airtable Base Builder
Creates the `HAVEN_Network` base with all 7 tables + fields,
then writes HAVEN_BASE_ID into .env automatically.

Run once:  python3 create_haven_airtable_base.py
"""
from __future__ import annotations

import os
import re
import sys
import time

import requests
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

API_KEY = os.environ.get("AIRTABLE_API_KEY", "")
WORKSPACE_ID = "wsp1XxpfjT8gDTIUJ"
BASE_NAME = "HAVEN_Network"
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
def num(name, precision=0): return {"name": name, "type": "number", "options": {"precision": precision}}
def currency_f(name): return {"name": name, "type": "currency", "options": {"precision": 2, "symbol": "$"}}
def chk(name): return {"name": name, "type": "checkbox", "options": {"icon": "check", "color": "greenBright"}}
def dt(name): return {"name": name, "type": "dateTime", "options": {"dateFormat": {"name": "us"}, "timeFormat": {"name": "12hour"}, "timeZone": "America/New_York"}}
def date_f(name): return {"name": name, "type": "date", "options": {"dateFormat": {"name": "us"}}}
def select(name, choices): return {"name": name, "type": "singleSelect", "options": {"choices": [{"name": c} for c in choices]}}
def multi(name, choices): return {"name": name, "type": "multipleSelects", "options": {"choices": [{"name": c} for c in choices]}}
def attach(name): return {"name": name, "type": "multipleAttachments"}


# ─────────────────────────────────────────────────────────────────────────────
# Shared choices
# ─────────────────────────────────────────────────────────────────────────────

STATES = ["FL", "TX", "LA", "MI", "National"]

AGREEMENT_STATUS = ["Prospect", "Outreach", "Negotiating", "Signed", "Active", "Inactive"]

ACTIVATION_STATUS = ["🟢 Ready", "🟡 Limited", "🔴 Unavailable"]

TRANSPORT_TYPES = ["Rideshare", "NEMT Fleet", "Charter Bus", "Medical Transport", "Courier", "Ambulance"]

VEHICLE_TYPES = ["Sedan", "SUV", "Wheelchair Van", "Stretcher", "Bus", "Cargo Van", "Box Truck"]

HOUSING_CHAINS = ["Marriott", "Hilton", "IHG", "Wyndham", "Choice", "Best Western", "Extended Stay", "Independent", "Corporate Housing", "FEMA Trailer"]

HOUSING_TYPES = ["Hotel", "Extended Stay", "Corporate Housing", "Property Manager", "FEMA Trailer", "Short-Term Rental"]

ROOM_TYPES = ["Standard", "Suite", "ADA Accessible", "Pet-Friendly", "Kitchen", "Family"]

AMENITIES = ["WiFi", "Breakfast", "Laundry", "Pool", "Fitness", "Pet-Friendly", "Kitchen", "Parking"]

MEDICAL_TYPES = ["Home Health Agency", "DME Supplier", "Pharmacy", "Medical Courier", "Hospice", "Infusion"]

MEDICAL_SERVICES = ["Skilled Nursing", "PT", "OT", "Speech", "Home Health Aide", "Rx Delivery", "DME", "Oxygen", "CPAP", "Infusion", "Wound Care"]

LANGUAGES = ["English", "Spanish", "Vietnamese", "Creole", "French", "Other"]

MCO_PROGRAMS = ["Medicaid", "Medicare Advantage", "Dual Eligible", "CHIP", "Commercial"]

MCO_STATUS = ["Target", "Outreach", "Negotiating", "Credentialing", "Active", "Inactive"]

HAVEN_SERVICES = ["NEMT", "Housing", "Medical Continuity", "Evacuation", "Rx Coordination", "DME", "Home Health", "All HAVEN"]

EVENT_TYPES = ["Hurricane", "Tornado", "Flood", "Wildfire", "Winter Storm", "Earthquake", "Other"]

EVENT_STATUS = ["Pre-Event", "Active", "Recovery", "Closed"]

CASE_STATUS = ["Intake", "Active", "Resolved", "Closed"]

SPECIAL_NEEDS = ["Wheelchair", "Oxygen", "Dialysis", "Pediatric", "Elderly", "Pregnant", "Mental Health", "Bariatric", "Vent-Dependent"]

SERVICE_TYPES = ["Transport", "Housing", "Home Health", "DME", "Rx", "Evacuation", "Other"]

SERVICE_STATUS = ["Requested", "Scheduled", "In Progress", "Completed", "Cancelled", "Failed"]


# ─────────────────────────────────────────────────────────────────────────────
# Table schemas (7 tables)
# Primary field is always first in the fields list.
# ─────────────────────────────────────────────────────────────────────────────

TABLES = [
    {
        "name": "Transport_Partners",
        "description": "Rideshare, NEMT fleets, charter buses, medical transport, courier/delivery.",
        "fields": [
            txt("company_name"),  # primary
            txt("dba_name"),
            select("partner_type", TRANSPORT_TYPES),
            txt("contact_name"),
            email_f("contact_email"),
            phone_f("contact_phone"),
            mltext("address"),
            multi("states_served", STATES),
            mltext("counties_served"),
            multi("vehicle_types", VEHICLE_TYPES),
            num("fleet_size"),
            num("disaster_capacity"),
            chk("insurance_current"),
            date_f("insurance_expiry"),
            select("rate_type", ["Per Trip", "Per Mile", "Per Hour", "Flat Fee"]),
            currency_f("standard_rate"),
            currency_f("disaster_rate"),
            select("agreement_status", AGREEMENT_STATUS),
            date_f("agreement_date"),
            attach("agreement_file"),
            select("activation_status", ACTIVATION_STATUS),
            date_f("last_contact"),
            mltext("notes"),
        ],
    },
    {
        "name": "Housing_Partners",
        "description": "Hotels, extended stay, corporate housing, property managers.",
        "fields": [
            txt("property_name"),  # primary
            select("chain_brand", HOUSING_CHAINS),
            select("partner_type", HOUSING_TYPES),
            txt("contact_name"),
            email_f("contact_email"),
            phone_f("contact_phone"),
            mltext("address"),
            txt("city"),
            select("state", STATES),
            txt("county"),
            txt("zip"),
            num("total_rooms"),
            num("disaster_block"),
            multi("room_types", ROOM_TYPES),
            multi("amenities", AMENITIES),
            currency_f("standard_rate"),
            currency_f("disaster_rate"),
            chk("fema_approved"),
            chk("insurance_direct_bill"),
            select("agreement_status", AGREEMENT_STATUS),
            date_f("agreement_date"),
            attach("agreement_file"),
            select("activation_status", ACTIVATION_STATUS),
            num("current_availability"),
            date_f("last_contact"),
            mltext("notes"),
        ],
    },
    {
        "name": "Medical_Partners",
        "description": "Home health agencies, DME suppliers, pharmacies, medical couriers.",
        "fields": [
            txt("company_name"),  # primary
            select("partner_type", MEDICAL_TYPES),
            txt("license_number"),
            select("license_state", STATES),
            date_f("license_expiry"),
            chk("medicare_certified"),
            chk("medicaid_enrolled"),
            txt("contact_name"),
            email_f("contact_email"),
            phone_f("contact_phone"),
            mltext("address"),
            multi("states_served", STATES),
            mltext("counties_served"),
            multi("services_offered", MEDICAL_SERVICES),
            num("staff_count"),
            num("disaster_capacity"),
            multi("languages", LANGUAGES),
            chk("insurance_current"),
            date_f("insurance_expiry"),
            select("rate_type", ["Per Visit", "Per Hour", "Per Diem", "Per Item"]),
            currency_f("standard_rate"),
            currency_f("disaster_rate"),
            select("agreement_status", AGREEMENT_STATUS),
            date_f("agreement_date"),
            attach("agreement_file"),
            select("activation_status", ACTIVATION_STATUS),
            chk("24_7_available"),
            date_f("last_contact"),
            mltext("notes"),
        ],
    },
    {
        "name": "MCO_Contracts",
        "description": "Managed care organization relationships for HAVEN services.",
        "fields": [
            txt("mco_name"),  # primary
            txt("parent_company"),
            select("state", STATES),
            multi("program_type", MCO_PROGRAMS),
            num("member_count"),
            txt("contact_name"),
            email_f("contact_email"),
            phone_f("contact_phone"),
            multi("services_contracted", HAVEN_SERVICES),
            select("contract_status", MCO_STATUS),
            date_f("contract_start"),
            date_f("contract_end"),
            currency_f("contract_value"),
            currency_f("rates_transport"),
            currency_f("rates_housing"),
            currency_f("rates_medical"),
            select("credentialing_status", ["Not Started", "In Progress", "Complete"]),
            chk("portal_access"),
            url_f("portal_url"),
            txt("portal_login"),
            attach("agreement_file"),
            date_f("last_contact"),
            txt("next_action"),
            mltext("notes"),
        ],
    },
    {
        "name": "Disaster_Events",
        "description": "Active and historical disaster events being served.",
        "fields": [
            txt("event_name"),  # primary
            select("event_type", EVENT_TYPES),
            txt("fema_declaration"),
            date_f("declaration_date"),
            multi("states_affected", STATES),
            mltext("counties_affected"),
            select("event_status", EVENT_STATUS),
            date_f("activation_date"),
            date_f("deactivation_date"),
            num("cases_served"),
            num("transport_trips"),
            num("housing_placements"),
            num("medical_services"),
            currency_f("total_revenue"),
            currency_f("total_cost"),
            currency_f("margin"),
            mltext("lessons_learned"),
        ],
    },
    {
        "name": "Cases",
        "description": "Individual cases/families being served during disasters.",
        "fields": [
            txt("case_id"),  # primary — auto-generated or manual
            txt("event_name"),  # text link to Disaster_Events
            txt("mco_name"),  # text link to MCO_Contracts
            txt("member_id"),
            txt("member_name"),
            phone_f("member_phone"),
            email_f("member_email"),
            num("family_size"),
            multi("special_needs", SPECIAL_NEEDS),
            multi("languages", LANGUAGES),
            mltext("home_address"),
            mltext("current_location"),
            chk("needs_housing"),
            chk("needs_transport"),
            chk("needs_medical"),
            chk("needs_rx"),
            chk("needs_dme"),
            select("case_status", CASE_STATUS),
            txt("assigned_to"),
            date_f("intake_date"),
            date_f("resolution_date"),
            mltext("notes"),
        ],
    },
    {
        "name": "Service_Activations",
        "description": "Individual service requests within a case.",
        "fields": [
            txt("activation_id"),  # primary
            txt("case_id"),  # text link to Cases
            select("service_type", SERVICE_TYPES),
            txt("partner_name"),  # text — name of assigned vendor
            mltext("service_description"),
            date_f("scheduled_date"),
            txt("scheduled_time"),
            mltext("pickup_address"),
            mltext("destination_address"),
            select("service_status", SERVICE_STATUS),
            date_f("completion_date"),
            currency_f("vendor_cost"),
            currency_f("billable_amount"),
            chk("billed"),
            chk("paid"),
            mltext("notes"),
        ],
    },
]


# ─────────────────────────────────────────────────────────────────────────────
# Base creation functions
# ─────────────────────────────────────────────────────────────────────────────

def check_existing_base() -> str | None:
    """Return base ID if HAVEN_Network already exists."""
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
        content = content.rstrip("\n") + f"\n\n# HAVEN — Disaster Response Network Airtable base\n{key}={value}\n"
        action = "Added"
    with open(env_path, "w") as f:
        f.write(content)
    print(f"  ✓ {action} {key} in .env")


def main() -> None:
    if not API_KEY:
        print("✗ AIRTABLE_API_KEY not found in .env. Aborting.")
        sys.exit(1)

    print("\n══════════════════════════════════════════════════════")
    print("  HAVEN — Airtable Base Builder")
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
    write_env_var("HAVEN_BASE_ID", base_id)

    print(f"\n══════════════════════════════════════════════════════")
    print(f"  DONE.  Base ID: {base_id}")
    print(f"  HAVEN_BASE_ID written to .env")
    print(f"\n  Tables created:")
    for t in TABLES:
        print(f"    • {t['name']}")
    print(f"\n  Next steps:")
    print(f"    1. Open Airtable and verify the base structure")
    print(f"    2. Add views per HAVEN_NETWORK_REGISTRY_SCHEMA.md")
    print(f"    3. Begin seeding partner prospects")
    print(f"══════════════════════════════════════════════════════\n")


if __name__ == "__main__":
    main()
