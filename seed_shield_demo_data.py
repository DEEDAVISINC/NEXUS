"""
Seed SHIELD with realistic demo data for the MDHHS presentation.
20 referrals across Wayne, Oakland, Macomb, Genesee counties.
Each with families, children (with BLL levels), service activations, and milestones.

Usage:
  python3 seed_shield_demo_data.py          # dry-run (prints what would be created)
  python3 seed_shield_demo_data.py --apply  # creates records in Airtable
"""

from __future__ import annotations
import os, sys, json, random
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from dotenv import load_dotenv

load_dotenv()

AIRTABLE_PAT = os.getenv("AIRTABLE_PAT") or os.getenv("AIRTABLE_API_KEY", "")
BASE_ID = os.getenv("LEAD_SCREENING_BASE_ID", "")
DRY_RUN = "--apply" not in sys.argv
ET = ZoneInfo("America/New_York")

if not DRY_RUN:
    from pyairtable import Api
    at = Api(AIRTABLE_PAT)

# ─── Demo families ──────────────────────────────────────────────────────────
DEMO_REFERRALS = [
    # Wayne County (8 referrals — highest volume, Flint-adjacent crisis awareness)
    {"county": "Wayne", "agency": "Wayne County Health Dept", "worker": "Maria Gonzalez", "urgency": "Emergency", "services": ["Blood Lead Level (BLL) Testing", "CLPPP Case Management", "Lead Remediation Coordination", "Housing Navigation"], "family": "Johnson", "children": [("Amari Johnson", 24, 12.3, "Completed"), ("Layla Johnson", 8, 6.1, "Completed")], "status": "Active", "stage": "In Service"},
    {"county": "Wayne", "agency": "MDHHS Region 10", "worker": "Angela Medina", "urgency": "Urgent", "services": ["Blood Lead Level (BLL) Testing", "NEMT — Non-Emergency Medical Transportation", "MIBridges Benefits Navigation"], "family": "Williams", "children": [("Jaylen Williams", 36, 7.8, "Completed")], "status": "Active", "stage": "Engaged"},
    {"county": "Wayne", "agency": "Wayne County Health Dept", "worker": "David Park", "urgency": "Standard", "services": ["Blood Lead Level (BLL) Testing", "Filter Safety Net / Drinking Water"], "family": "Davis", "children": [("Kaia Davis", 18, 4.2, "Completed")], "status": "Active", "stage": "Outreach"},
    {"county": "Wayne", "agency": "Detroit Health Dept", "worker": "Tanya Brooks", "urgency": "Emergency", "services": ["Blood Lead Level (BLL) Testing", "CLPPP Case Management", "Lead Remediation Coordination", "Community Health Worker Home Visit", "Housing Navigation"], "family": "Thomas", "children": [("Marcus Thomas", 14, 18.7, "Completed"), ("Nia Thomas", 30, 9.4, "Completed")], "status": "Active", "stage": "In Service"},
    {"county": "Wayne", "agency": "MDHHS Region 10", "worker": "Angela Medina", "urgency": "Standard", "services": ["Blood Lead Level (BLL) Testing", "MIBridges Benefits Navigation"], "family": "Robinson", "children": [("Elijah Robinson", 42, 3.1, "Completed")], "status": "Completed", "stage": "Closed"},
    {"county": "Wayne", "agency": "Dearborn Health Dept", "worker": "Fatima Hassan", "urgency": "Urgent", "services": ["Blood Lead Level (BLL) Testing", "NEMT — Non-Emergency Medical Transportation", "Filter Safety Net / Drinking Water"], "family": "Ahmed", "children": [("Yasmin Ahmed", 12, 8.9, "Completed")], "status": "Active", "stage": "In Service"},
    {"county": "Wayne", "agency": "Wayne County Health Dept", "worker": "Maria Gonzalez", "urgency": "Standard", "services": ["Blood Lead Level (BLL) Testing", "Community Health Worker Home Visit"], "family": "Garcia", "children": [("Sofia Garcia", 20, 2.8, "Pending")], "status": "Pending", "stage": "Intake"},
    {"county": "Wayne", "agency": "Detroit Health Dept", "worker": "Tanya Brooks", "urgency": "Urgent", "services": ["Blood Lead Level (BLL) Testing", "CLPPP Case Management", "Nurse Home Visit"], "family": "Brown", "children": [("Zion Brown", 16, 11.2, "Completed")], "status": "Active", "stage": "Engaged"},

    # Oakland County (5 referrals)
    {"county": "Oakland", "agency": "Oakland County Health Dept", "worker": "Jennifer Liu", "urgency": "Standard", "services": ["Blood Lead Level (BLL) Testing", "Filter Safety Net / Drinking Water"], "family": "Chen", "children": [("Lily Chen", 28, 3.9, "Completed")], "status": "Active", "stage": "Outreach"},
    {"county": "Oakland", "agency": "Oakland County Health Dept", "worker": "Jennifer Liu", "urgency": "Urgent", "services": ["Blood Lead Level (BLL) Testing", "CLPPP Case Management", "Lead Remediation Coordination"], "family": "Okonkwo", "children": [("Adaeze Okonkwo", 22, 9.6, "Completed"), ("Chidi Okonkwo", 48, 5.3, "Completed")], "status": "Active", "stage": "In Service"},
    {"county": "Oakland", "agency": "MDHHS Region 10", "worker": "Aimee Surma", "urgency": "Standard", "services": ["Blood Lead Level (BLL) Testing", "MIBridges Benefits Navigation", "Community Health Worker Home Visit"], "family": "Patel", "children": [("Arjun Patel", 15, 4.1, "Completed")], "status": "Active", "stage": "Engaged"},
    {"county": "Oakland", "agency": "Oakland County Health Dept", "worker": "Jennifer Liu", "urgency": "Emergency", "services": ["Blood Lead Level (BLL) Testing", "CLPPP Case Management", "Lead Remediation Coordination", "Housing Navigation", "NEMT — Non-Emergency Medical Transportation"], "family": "Miller", "children": [("Isaiah Miller", 10, 15.4, "Completed")], "status": "Active", "stage": "In Service"},
    {"county": "Oakland", "agency": "Pontiac Health Dept", "worker": "Robert Taylor", "urgency": "Standard", "services": ["Blood Lead Level (BLL) Testing"], "family": "Jackson", "children": [("Aaliyah Jackson", 32, 2.4, "Pending")], "status": "Pending", "stage": "Intake"},

    # Macomb County (4 referrals)
    {"county": "Macomb", "agency": "Macomb County Health Dept", "worker": "Susan O'Brien", "urgency": "Urgent", "services": ["Blood Lead Level (BLL) Testing", "CLPPP Case Management", "Filter Safety Net / Drinking Water"], "family": "Kowalski", "children": [("Emma Kowalski", 26, 7.2, "Completed")], "status": "Active", "stage": "In Service"},
    {"county": "Macomb", "agency": "Macomb County Health Dept", "worker": "Susan O'Brien", "urgency": "Standard", "services": ["Blood Lead Level (BLL) Testing", "Community Health Worker Home Visit", "MIBridges Benefits Navigation"], "family": "Smith", "children": [("Logan Smith", 38, 3.8, "Completed"), ("Olivia Smith", 14, 4.5, "Completed")], "status": "Active", "stage": "Engaged"},
    {"county": "Macomb", "agency": "MDHHS Region 10", "worker": "Angela Medina", "urgency": "Emergency", "services": ["Blood Lead Level (BLL) Testing", "CLPPP Case Management", "Lead Remediation Coordination", "Nurse Home Visit"], "family": "Nguyen", "children": [("Minh Nguyen", 19, 13.1, "Completed")], "status": "Active", "stage": "In Service"},
    {"county": "Macomb", "agency": "Macomb County Health Dept", "worker": "Susan O'Brien", "urgency": "Standard", "services": ["Blood Lead Level (BLL) Testing"], "family": "Martinez", "children": [("Diego Martinez", 40, 2.1, "Completed")], "status": "Completed", "stage": "Closed"},

    # Genesee County (3 referrals — Flint water crisis legacy)
    {"county": "Genesee", "agency": "Genesee County Health Dept", "worker": "Patricia Washington", "urgency": "Emergency", "services": ["Blood Lead Level (BLL) Testing", "CLPPP Case Management", "Lead Remediation Coordination", "Filter Safety Net / Drinking Water", "Housing Navigation", "Community Health Worker Home Visit"], "family": "Carter", "children": [("Destiny Carter", 11, 22.4, "Completed"), ("Jayden Carter", 36, 14.8, "Completed")], "status": "Active", "stage": "In Service"},
    {"county": "Genesee", "agency": "Genesee County Health Dept", "worker": "Patricia Washington", "urgency": "Urgent", "services": ["Blood Lead Level (BLL) Testing", "NEMT — Non-Emergency Medical Transportation", "MIBridges Benefits Navigation"], "family": "Wilson", "children": [("Aiden Wilson", 24, 8.3, "Completed")], "status": "Active", "stage": "Engaged"},
    {"county": "Genesee", "agency": "MDHHS — Flint Lead Recovery", "worker": "Aimee Surma", "urgency": "Standard", "services": ["Blood Lead Level (BLL) Testing", "Filter Safety Net / Drinking Water", "Community Health Worker Home Visit"], "family": "Taylor", "children": [("Chloe Taylor", 30, 5.7, "Completed")], "status": "Active", "stage": "Outreach"},
]

MILESTONE_TEMPLATES = {
    "Intake": ["Referral received", "Initial screening completed"],
    "Outreach": ["Referral received", "Navigator assigned", "First contact attempt"],
    "Engaged": ["Referral received", "Navigator assigned", "Family contacted", "Needs assessment completed"],
    "In Service": ["Referral received", "Navigator assigned", "Family contacted", "Needs assessment completed", "Services activated", "Home visit completed"],
    "Closed": ["Referral received", "Navigator assigned", "Family contacted", "Needs assessment completed", "Services activated", "Services delivered", "Outcomes documented", "Case closed"],
}

NAVIGATORS = [
    {"name": "Angela Johnson", "email": "angela.johnson@cwcare.org", "phone": "(313) 555-0101", "county": "Wayne"},
    {"name": "Keisha Williams", "email": "keisha.williams@cwcare.org", "phone": "(313) 555-0102", "county": "Wayne"},
    {"name": "Priya Sharma", "email": "priya.sharma@cwcare.org", "phone": "(248) 555-0103", "county": "Oakland"},
    {"name": "Michelle Torres", "email": "michelle.torres@cwcare.org", "phone": "(586) 555-0104", "county": "Macomb"},
    {"name": "Tamara Reed", "email": "tamara.reed@cwcare.org", "phone": "(810) 555-0105", "county": "Genesee"},
]


def generate_case_number(idx: int) -> str:
    return f"SHD-2026-{str(idx + 1).zfill(4)}"


def random_date_recent(days_back: int = 30) -> datetime:
    return datetime.now(ET) - timedelta(days=random.randint(1, days_back), hours=random.randint(0, 12))


def run():
    print(f"{'DRY RUN' if DRY_RUN else 'APPLYING'} — seeding {len(DEMO_REFERRALS)} demo referrals\n")

    for idx, ref in enumerate(DEMO_REFERRALS):
        case_num = generate_case_number(idx)
        date_received = random_date_recent(45)
        first_contact = date_received + timedelta(hours=random.randint(4, 36)) if ref["stage"] != "Intake" else None

        # Referral record
        referral_fields = {
            "referral_id": case_num,
            "date_received": date_received.isoformat(),
            "first_contact_at": first_contact.isoformat() if first_contact else None,
            "referral_source": "MDHHS / LHD",
            "referring_agency": ref["agency"],
            "case_worker_name": ref["worker"],
            "county": ref["county"],
            "services_requested": json.dumps(ref["services"]),
            "urgency": ref["urgency"],
            "status": ref["status"],
            "intake_method": "Portal",
        }

        print(f"  [{case_num}] {ref['family']} Family — {ref['county']} — {ref['urgency']} — {len(ref['children'])} children — {len(ref['services'])} services")

        if not DRY_RUN:
            r = at.table(BASE_ID, "Referrals").create(referral_fields)
            ref_airtable_id = r["id"]

            nav = next((n for n in NAVIGATORS if n["county"] == ref["county"]), NAVIGATORS[0])

            # Family
            fam = at.table(BASE_ID, "Families").create({
                "family_name": ref["family"],
                "primary_contact_name": ref["family"],
                "primary_contact_phone": f"(313) 555-{random.randint(1000, 9999)}",
                "primary_contact_email": f"{ref['family'].lower()}@example.com",
                "address": f"{random.randint(100, 9999)} {random.choice(['Woodward', 'Michigan', 'Grand River', 'Gratiot', 'Telegraph', 'Mound', 'Van Dyke'])} Ave",
                "city": f"{ref['county']} County",
                "county": ref["county"],
                "insurance_type": random.choice(["Medicaid / MIChild", "CHIP", "Private Insurance"]),
                "language": random.choice(["English", "English", "English", "Spanish", "Arabic"]),
                "status": "Active",
            })

            # Link family to referral
            try:
                at.table(BASE_ID, "Referrals").update(ref_airtable_id, {"family_id": [fam["id"]], "navigator_email": nav["email"]})
            except Exception:
                pass

            # Children
            BLL_TO_STATUS = {True: "Confirmed EBL", False: "Tested - Normal"}
            for child_name, age_months, bll, _ in ref["children"]:
                test_status = "Confirmed EBL" if bll >= 5 else "Tested - Normal"
                clppp = "Enrolled" if bll >= 5 else "Not Referred"
                at.table(BASE_ID, "Children").create({
                    "child_name": child_name,
                    "age_months": age_months,
                    "blood_lead_level": bll,
                    "lead_test_status": test_status,
                    "clppp_status": clppp,
                    "family_id": [fam["id"]],
                })

            # Service activations
            for svc in ref["services"]:
                status = "Completed" if ref["stage"] == "Closed" else "Active" if ref["stage"] == "In Service" else "Pending"
                at.table(BASE_ID, "Service_Activations").create({
                    "referral_id": [ref_airtable_id],
                    "service_line": svc,
                    "status": status,
                    "activated_date": date_received.isoformat(),
                    "navigator_name": nav["name"],
                    "vendor": random.choice(["CWC Internal", "DDI Partner", "County Health Dept"]),
                })

            # Milestones — use valid milestone_type values
            STAGE_MILESTONES = {
                "Intake": ["Referral Received"],
                "Outreach": ["Referral Received", "Navigator Assigned", "First Contact Attempt"],
                "Engaged": ["Referral Received", "Navigator Assigned", "First Contact Made", "Family Engaged"],
                "In Service": ["Referral Received", "Navigator Assigned", "First Contact Made", "Family Engaged", "Service Activated"],
                "Closed": ["Referral Received", "Navigator Assigned", "First Contact Made", "Family Engaged", "Service Activated", "Service Completed", "Case Closed"],
            }
            milestones = STAGE_MILESTONES.get(ref["stage"], ["Referral Received"])
            for j, ms in enumerate(milestones):
                ms_date = date_received + timedelta(days=j * random.randint(1, 3))
                at.table(BASE_ID, "Case_Milestones").create({
                    "referral_id": [ref_airtable_id],
                    "milestone_type": ms,
                    "timestamp": ms_date.isoformat(),
                    "recorded_by": nav["name"],
                    "notes": f"Demo data — {ms}",
                })

    # ─── Seed Navigators table ───────────────────────────────────────────
    nav_count = 0
    if not DRY_RUN:
        print("\n  Seeding Navigators table...")
        for nav in NAVIGATORS:
            try:
                at.table(BASE_ID, "Navigators").create({
                    "name": nav["name"],
                    "email": nav["email"],
                    "phone": nav["phone"],
                    "county": nav["county"],
                    "role": "Navigator",
                    "status": "Active",
                })
                nav_count += 1
            except Exception as e:
                print(f"    ⚠ Navigator {nav['name']}: {e}")
        # Dee Davis as Ultimate Supervisor
        try:
            at.table(BASE_ID, "Navigators").create({
                "name": "Dee Davis",
                "email": "dee@deedavisinc.com",
                "phone": "(313) 555-0100",
                "county": "All",
                "role": "Ultimate Supervisor",
                "supervisor_access": True,
                "status": "Active",
            })
            nav_count += 1
        except Exception as e:
            print(f"    ⚠ Dee Davis: {e}")
        print(f"  ✓ {nav_count} navigators created")
    else:
        nav_count = len(NAVIGATORS) + 1
        print(f"\n  Would create {nav_count} navigators (including Dee Davis as Ultimate Supervisor)")

    total_children = sum(len(r["children"]) for r in DEMO_REFERRALS)
    ebl = sum(1 for r in DEMO_REFERRALS for _, _, bll, _ in r["children"] if bll >= 5)
    print(f"\n{'Would create' if DRY_RUN else 'Created'}:")
    print(f"  {len(DEMO_REFERRALS)} referrals")
    print(f"  {len(DEMO_REFERRALS)} families")
    print(f"  {total_children} children ({ebl} with EBL >= 5 µg/dL)")
    print(f"  {nav_count} navigators")
    print(f"  Across: Wayne ({sum(1 for r in DEMO_REFERRALS if r['county']=='Wayne')}), "
          f"Oakland ({sum(1 for r in DEMO_REFERRALS if r['county']=='Oakland')}), "
          f"Macomb ({sum(1 for r in DEMO_REFERRALS if r['county']=='Macomb')}), "
          f"Genesee ({sum(1 for r in DEMO_REFERRALS if r['county']=='Genesee')})")

    if DRY_RUN:
        print("\nRun with --apply to create these records in Airtable.")


if __name__ == "__main__":
    run()
