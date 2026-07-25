#!/usr/bin/env python3
"""
NEXUS GATEWAY — HR Onboarding API
====================================
GATEWAY is the NEXUS module name for this system (branding layer over the
original "HR Onboarding" build — routes stay at /nexus/hr/* for backend
stability; the display name across the frontend and the self-service
portal is GATEWAY). Named for the /can-work compliance gate at its core:
nobody touches an MCO-facing task until they've cleared the gate.

Automates the DDI New Hire Onboarding SOP (employees) and the DDI
Independent Contractor Onboarding SOP (1099s) — internal personnel only,
across all divisions (DEPOINTE, HAVEN, SHIELD, VITAL, ARENA/PRIME,
3D Ink Signatures/CNTDA, Freight 1st Direct, DEPOINTE DNA, Corporate/HR/Admin).

This is DISTINCT from:
  - GPSS SUPPLIERS / GPSS SUBCONTRACTORS  -> external vendors & project subs
  - PRISM FIELD AGENTS                    -> mobile field service dispatch
  (Both governed by NEXUS_ONBOARDING_SYSTEM.md's person-type pipeline.)

WHY THIS EXISTS: internal employees/contractors carry a different
compliance spine than field agents or subs — Form I-9 / E-Verify (employees
only), OIG LEIE + GSA SAM.gov exclusion screening (at hire + MONTHLY
thereafter), and CMS FDR training (First Tier, Downstream, and Related
entity — 42 CFR 422.504(d)) because DDI performs work under MCO/Medicaid
contracts (CareSource, HIDE SNP, etc.).

AUTOMATED SOP LOGIC IN THIS FILE (source: DDI New Hire Onboarding SOP +
DDI Independent Contractor Onboarding SOP):
  - 5-phase employee checklist / 4-phase contractor checklist, literal
    SOP item text, server-side single source of truth
  - 10-item training catalog with real recurrence rules per item:
      * refresher every 2 years   -> PII, Cultural Competence, Anti-Harassment
      * annual refresher          -> HIPAA
      * annual, reassigned at 11 months (not 12) -> General Compliance/FWA,
        Medicare Fraud & Abuse, Code of Conduct/COI re-attestation
      * annual, member-facing roles only          -> Recipient Rights,
        Abuse & Neglect Reporting
      * one-time, no recurrence                   -> E-Verify/I-9 Basics
                                                       (employees only)
  - Two-tier deadline: 30-day DDI internal target (all items) vs 90-day
    CMS hard compliance floor (General Compliance/FWA + Medicare Fraud &
    Abuse only) — a 30-day miss is a flag, a 90-day miss is a compliance
    event requiring investigation/remediation documentation
  - Contractor training is SCOPED, not blanket-assigned: each item carries
    a trigger condition; Engagement Manager marks each item
    applicable/not-applicable/pending before it is assigned. E-Verify/I-9
    never applies to contractors.
  - Monthly exclusion screening cadence (OIG LEIE + GSA SAM.gov), computed
    from the last logged screening date, not a fixed 30-day flat window
  - Annual FDR Compliance Attestation (org-level, calendar-year cycle,
    separate small Airtable table) per SOP Section 6
  - Worker-classification documentation (contractor track) per SOP
    Section 10.1 / contractor SOP Section 8 — bounded scope, own
    tools/schedule, other clients, no supervisory integration,
    deliverable-based pay, "routed to counsel" flag for unclear cases
  - 30-Day Check-In Agenda (SOP Section 8) as a structured, trackable
    sub-checklist attached to the employee day30 phase

Storage: Airtable ('NEXUS HR ONBOARDING' + 'NEXUS HR FDR ATTESTATION')
is primary, matching every other NEXUS system. Falls back to local JSON
automatically if Airtable isn't configured or a table doesn't exist yet —
same fallback pattern used in prism_compliance_api.py. Writes use
typecast=True so new single-select values (divisions, worker types) are
accepted without a manual Airtable schema edit.

EMPLOYEE/VENDOR NUMBER (added Jul 2026, revised TWICE same day per Dee —
(1) "should read in a way it's easy to know who what when where and why,"
then (2) "remove the DDI...it's redundant, we are DDI" + "how do i know
that a customer care agent is working in the HAP account, or the MOLINA
account, or how do we know if they are a manager, supervisor etc"): every
record gets a personnelNumber the moment onboarding STARTS, format
[DIVISION]-[ACCOUNT]-[LEVEL]-[EMP|VEN]-[YYMM]-[SEQ], e.g.
HAVN-CSRC-AGT-EMP-2607-0001 = HAVEN division, CareSource account, Agent
level, W-2 employee, started July 2026, 1st in that exact division+
account+level+type+month bucket. No "DDI-" prefix — redundant, every
record here already is DDI. ACCOUNT (NEXUS HR ACCOUNT CODES) and LEVEL
(NEXUS HR LEVEL CODES) are both live Airtable tables, same
zero-code-change pattern as the role email policy — Dee/HR add a new
client account the moment a contract goes live, and new seniority tiers
any time. EMP = W-2 employee, VEN = 1099 contractor (Dee's "vendor
number"). Blank/unmatched account falls back to GEN, blank/unmatched
level falls back to STF — never invents a code. See DIVISION_CODES,
ACCOUNT_CODE_FALLBACK, LEVEL_CODE_FALLBACK, and _next_personnel_number().

COMPANY EMAIL AUTO-PROVISIONING (added Jul 2026, revised same day per Dee):
NOT every hire gets a @deedavis.biz alias — only roles marked
REQUIRES_COMPANY_EMAIL = checked in the 'NEXUS HR ROLE EMAIL POLICY'
Airtable table (role_requires_company_email() reads it live, ~60s cache).
This is deliberately NOT a hardcoded Python list — Dee/HR add or remove
roles directly in Airtable and the change takes effect with zero code
changes and zero deploys (per Dee: "all of this is to be autogenerated
and automated"). Seeded Jul 2026 with 10 roles sourced directly from
existing NEXUS documentation (NEMT Coordinator, SHIELD Navigator, HAVEN
Navigator, Navigator Supervisor, Program Manager, Dispatch/PRISM
Coordinator, Billing/VERTEX Operations, Engagement Manager, Corporate
Admin, Compliance Officer) — none fabricated; each row's NOTES field
cites its source doc. If the table is ever emptied, everyone defaults to
False (safe default — no unrequested aliases). HR can also override the
role default either direction per hire via `provisionCompanyEmail:
true/false` on the POST /nexus/hr/onboarding body (captured as
companyEmailOverride, acted on later — see below).

TIMING: the email is NOT created at record creation. It's deferred until
CREDENTIALING IS COMPLETE — defined as the existing /can-work gate passing
(_can_work_internal(): first onboarding phase done, exclusion screening
clear, no CMS-hard-missed trainings). _maybe_provision_company_email() is
called from update_checklist(), update_training(), and log_screening() —
whichever mutation happens to flip the gate from False to True is what
triggers provisioning. This matches Dee's requirement: don't issue a
professional @deedavis.biz identity before someone is actually cleared to
work. If the role-email policy or role gating logic changes later
to mean something other than the /can-work gate for "credentialing
complete," update _maybe_provision_company_email() accordingly.

When provisioning does happen, it creates firstname.lastname@deedavis.biz
on ImprovMX (collision-safe — see improvmx_client.py), forwarding to their
personal email on file. GATEWAY sign-in always stays on the personal
email; the alias is just the professional-facing address for signatures/
correspondence. Never blocks any mutation if ImprovMX is unreachable —
failure is logged to companyEmailError and retryable via
POST .../provision-email (which bypasses all gating — explicit HR action).
On archive (offboarding), the alias is redirected to gc@deedavis.biz, never
deleted — so nothing incoming is lost.

SCHEMA SELF-HEALING (added Jul 2026): typecast=True does NOT auto-create
new Airtable fields, only new options on existing single-select fields —
so field creation is handled separately, automatically, via the Airtable
Metadata API (_airtable_ensure_fields(), requires an API key with
schema.bases:write, confirmed present Jul 2026). Runs once at module
import across HR_TABLE, ROLE_POLICY_TABLE, ACCOUNT_CODES_TABLE, and
LEVEL_CODES_TABLE (see REQUIRED_FIELDS), best-effort/non-blocking — if a
field is ever missing (new field added to this file later, or someone
deletes one in Airtable), it gets recreated on the next app restart with
no manual Airtable UI step. Never creates the TABLES themselves (only
fields on tables that already exist) — 'NEXUS HR ONBOARDING', 'NEXUS HR
FDR ATTESTATION', 'NEXUS HR ROLE EMAIL POLICY', 'NEXUS HR ACCOUNT CODES',
and 'NEXUS HR LEVEL CODES' already exist as of Jul 2026.

RETENTION RULE: Records are never hard-deleted. "Remove" from the roster
= archive (STATUS -> Archived). All logs (audit, exclusion screening) are
append-only — corrections are new entries, never overwrites. This matches
the SOP's 10-year CMS FDR retention requirement (42 CFR 422.504(d)).

Endpoints:
  GET    /nexus/hr/onboarding/config                     — phases/trainings/divisions/agenda config
  GET    /nexus/hr/onboarding                            — roster (list)
  POST   /nexus/hr/onboarding                            — add new hire/engagement
  GET    /nexus/hr/onboarding/<id>                       — single record detail (+ computed compliance state)
  PUT    /nexus/hr/onboarding/<id>/checklist              — toggle a checklist item
  PUT    /nexus/hr/onboarding/<id>/training               — update a training row (status/due/cert/applicable)
  POST   /nexus/hr/onboarding/<id>/screening              — log exclusion screening entry (append-only)
  POST   /nexus/hr/onboarding/<id>/provision-email        — (re)provision the firstname.lastname@deedavis.biz alias
  PUT    /nexus/hr/onboarding/<id>/classification         — worker-classification documentation (contractor)
  PUT    /nexus/hr/onboarding/<id>/agenda                 — 30-day check-in agenda toggle/notes
  PUT    /nexus/hr/onboarding/<id>/member-facing          — toggle member-facing designation
  PUT    /nexus/hr/onboarding/<id>/status                 — archive / reactivate (soft only)
  GET    /nexus/hr/onboarding/<id>/can-work                — compliance gate check
  GET    /nexus/hr/onboarding/alerts                      — overdue training / stale screenings / attestation
  GET    /nexus/hr/attestation                            — list annual FDR attestations
  POST   /nexus/hr/attestation                            — record/update an annual FDR attestation
  GET    /nexus/hr/role-email-policy                      — list roles + whether each gets a company email
  POST   /nexus/hr/role-email-policy                      — add/update a role's company-email policy (upsert)
  GET    /nexus/hr/account-codes                          — list client/MCO accounts + personnel-number codes
  POST   /nexus/hr/account-codes                          — add/update an account code (upsert)
  GET    /nexus/hr/level-codes                            — list seniority tiers + personnel-number codes
  POST   /nexus/hr/level-codes                            — add/update a level code (upsert)

GATEWAY SELF-SERVICE PORTAL (gateway.deedavis.biz — new hire/contractor
facing, magic-link auth, no NEXUS login, mirrors the portal.deedavis.biz
pattern used by PRISM client intake). These endpoints are looked up by
EMAIL, not internal record id, and return a sanitized subset of the record
— never the audit log, never other people's records:
  GET    /nexus/hr/onboarding/self?email=                — own record + document/acknowledgment catalog
  POST   /nexus/hr/onboarding/self/documents              — upload a required document (base64)
  POST   /nexus/hr/onboarding/self/acknowledge            — typed-name e-sign acknowledgment (handbook, NDA, etc.)
"""

import os
import json
import uuid
import calendar
import requests
from datetime import datetime, date, timedelta
from flask import Blueprint, request, jsonify

from improvmx_client import provision_employee_alias, update_alias, get_alias_map

hr_onboarding = Blueprint('hr_onboarding', __name__)

# Where an offboarded employee/contractor's @deedavis.biz alias redirects to
# instead of being deleted — matches the "never hard delete" retention rule.
OFFBOARD_ALIAS_FORWARD = "gc@deedavis.biz"

# ─── Storage config ──────────────────────────────────────────────
HR_TABLE = 'NEXUS HR ONBOARDING'
ATTEST_TABLE = 'NEXUS HR FDR ATTESTATION'
ROLE_POLICY_TABLE = 'NEXUS HR ROLE EMAIL POLICY'
ACCOUNT_CODES_TABLE = 'NEXUS HR ACCOUNT CODES'
LEVEL_CODES_TABLE = 'NEXUS HR LEVEL CODES'
DATA_DIR = os.path.join(os.path.dirname(__file__), 'uploads', 'hr_onboarding')
LOCAL_FILE = os.path.join(DATA_DIR, 'roster.json')
ATTEST_LOCAL_FILE = os.path.join(DATA_DIR, 'fdr_attestation.json')
ROLE_POLICY_LOCAL_FILE = os.path.join(DATA_DIR, 'role_email_policy.json')
ACCOUNT_CODES_LOCAL_FILE = os.path.join(DATA_DIR, 'account_codes.json')
LEVEL_CODES_LOCAL_FILE = os.path.join(DATA_DIR, 'level_codes.json')
os.makedirs(DATA_DIR, exist_ok=True)


# ─── Schema self-healing (added Jul 2026) ─────────────────────────
# Uses the Airtable Metadata API to create missing FIELDS on tables that
# already exist. Never creates tables — only fields. Best-effort: any
# failure (no key, no write scope, network) is swallowed silently, because
# every read/write path already has its own local-JSON fallback regardless
# of whether this succeeds. This exists so "add a column to Airtable" is
# never a manual step again — see Dee: "all of this is to be autogenerated
# and automated."
REQUIRED_FIELDS = {
    HR_TABLE: [
        {'name': 'ROLE', 'type': 'singleLineText'},
        {'name': 'ACCOUNT', 'type': 'singleLineText'},
        {'name': 'LEVEL', 'type': 'singleLineText'},
        {'name': 'PERSONNEL_NUMBER', 'type': 'singleLineText'},
        {'name': 'COMPANY_EMAIL', 'type': 'singleLineText'},
        {'name': 'COMPANY_EMAIL_ERROR', 'type': 'singleLineText'},
        {'name': 'COMPANY_EMAIL_OVERRIDE', 'type': 'singleLineText'},
        {'name': 'COMPANY_EMAIL_DECLINED', 'type': 'checkbox', 'options': {'icon': 'check', 'color': 'greenBright'}},
    ],
    ROLE_POLICY_TABLE: [
        {'name': 'ROLE', 'type': 'singleLineText'},
        {'name': 'REQUIRES_COMPANY_EMAIL', 'type': 'checkbox', 'options': {'icon': 'check', 'color': 'greenBright'}},
        {'name': 'NOTES', 'type': 'singleLineText'},
    ],
    ACCOUNT_CODES_TABLE: [
        {'name': 'ACCOUNT_NAME', 'type': 'singleLineText'},
        {'name': 'ACCOUNT_CODE', 'type': 'singleLineText'},
        {'name': 'STATUS', 'type': 'singleLineText'},
        {'name': 'NOTES', 'type': 'singleLineText'},
    ],
    LEVEL_CODES_TABLE: [
        {'name': 'LEVEL_NAME', 'type': 'singleLineText'},
        {'name': 'LEVEL_CODE', 'type': 'singleLineText'},
        {'name': 'NOTES', 'type': 'singleLineText'},
    ],
}


def _airtable_ensure_fields():
    """Best-effort: create any REQUIRED_FIELDS missing from their Airtable
    table. Called once at module import. Silently no-ops without an API key,
    without schema.bases:write scope, or on any network failure."""
    api_key = os.environ.get('AIRTABLE_API_KEY', '')
    base_id = os.environ.get('AIRTABLE_BASE_ID', '')
    if not api_key or not base_id:
        return
    headers = {'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'}
    try:
        resp = requests.get(f'https://api.airtable.com/v0/meta/bases/{base_id}/tables', headers=headers, timeout=10)
        resp.raise_for_status()
        tables = {t['name']: t for t in resp.json().get('tables', [])}
    except Exception:
        return
    for table_name, specs in REQUIRED_FIELDS.items():
        table = tables.get(table_name)
        if not table:
            continue  # table doesn't exist — not this function's job to create tables
        existing = {f['name'] for f in table.get('fields', [])}
        for spec in specs:
            if spec['name'] in existing:
                continue
            try:
                requests.post(
                    f"https://api.airtable.com/v0/meta/bases/{base_id}/tables/{table['id']}/fields",
                    headers=headers, json=spec, timeout=10,
                )
            except Exception:
                pass  # best-effort only — local JSON fallback still protects reads/writes


def get_airtable():
    """Get Airtable API connection — mirrors prism_compliance_api.py pattern."""
    try:
        from pyairtable import Api
        api_key = os.environ.get('AIRTABLE_API_KEY', '')
        base_id = os.environ.get('AIRTABLE_BASE_ID', '')
        if not api_key or not base_id:
            return None, None
        return Api(api_key), base_id
    except ImportError:
        return None, None


def _airtable_table(table_name):
    api, base_id = get_airtable()
    if not api or not base_id:
        return None
    try:
        table = api.table(base_id, table_name)
        table.all(max_records=1)  # cheap probe — raises if table doesn't exist
        return table
    except Exception:
        return None


# Self-heal schema once, at import time — see _airtable_ensure_fields() above.
_airtable_ensure_fields()


# ═══════════════════════════════════════════════════════════════
# CONFIG — single source of truth, server-side (mirrors the SOP text)
# ═══════════════════════════════════════════════════════════════

PHASES_EMPLOYEE = [
    {'key': 'preboard', 'title': 'Phase 1 — Pre-Boarding', 'owner': 'HR', 'items': [
        'Offer letter signed and returned',
        'Background check initiated',
        'E-Verify case created (DDI is an E-Verify Program Administrator)',
        'OIG LEIE exclusion list screening completed (at hire)',
        'GSA SAM.gov exclusion/debarment screening completed (at hire)',
        'IT ticket submitted: email, NEXUS access, PRISM access (if role requires), hardware',
        'Division/manager assigned',
        'Start date and date of hire confirmed in writing (anchors CMS 90-day training deadline + 10-year retention)',
    ]},
    {'key': 'day1', 'title': 'Phase 2 — Day One', 'owner': 'HR + Direct Manager', 'items': [
        'I-9 completed in person (Section 1 by employee, Section 2 by authorized rep within 3 business days)',
        'Signed acknowledgments: Employee Handbook, Code of Conduct/Conflict of Interest, Confidentiality/NDA',
        'NEXUS account provisioned and tested',
        'Introduction to direct manager, division team, and "What are we not seeing?" principle',
        'Welcome/training assignment email sent',
    ]},
    {'key': 'week1', 'title': 'Phase 3 — Week One', 'owner': 'Direct Manager', 'items': [
        'Division-specific systems walkthrough (PRISM for CS/intake roles, relevant NEXUS modules)',
        '"Coordinate, not provide" language review — never "our drivers" / "we run the transportation program"',
        'Shadow a live CS interaction or workflow (Rolls Royce standard calibration)',
        'Training progress check-in (target: PII + HIPAA courses in progress)',
    ]},
    {'key': 'day30', 'title': 'Phase 4 — First 30 Days', 'owner': 'HR + Direct Manager', 'items': [
        'All required trainings completed (see Training tab)',
        'Role-specific competency check-in with manager',
        '30-day check-in meeting held (agenda below)',
    ]},
    {'key': 'day6090', 'title': 'Phase 5 — 60/90-Day Check-Ins', 'owner': 'Direct Manager', 'items': [
        '60-day: workload calibration, open questions addressed',
        '90-day: performance review, confirm all compliance training current, confirm E-Verify/I-9 file complete',
    ]},
]

PHASES_CONTRACTOR = [
    {'key': 'preengage', 'title': 'Phase 1 — Pre-Engagement', 'owner': 'HR/Contracts', 'items': [
        'Independent Contractor Agreement / MSA drafted and executed with specific written scope of work',
        'W-9 collected (NOT I-9 — E-Verify/I-9 do not apply to contractors; running E-Verify undermines status)',
        'OIG LEIE exclusion list screening completed',
        'GSA SAM.gov exclusion/debarment screening completed',
        'Business Associate Agreement (BAA) executed, if the engagement involves any access to PHI',
        'Certificate of insurance / liability coverage collected, if required by contract or MCO relationship',
        'Payment terms confirmed as deliverable/milestone-based (NOT an hourly wage structure mirroring payroll)',
        'Worker-classification basis documented and retained (see Classification tab) — before engagement starts',
    ]},
    {'key': 'engagestart', 'title': 'Phase 2 — Engagement Start', 'owner': 'HR/Contracts', 'items': [
        'Confidentiality/NDA signed',
        'Code of Conduct acknowledgment signed — framed as a contractual flow-down obligation, not employee handbook',
        'System access provisioned at minimum necessary scope for the engagement (not blanket NEXUS/PRISM access)',
        '"Coordinate, not provide" and confidentiality briefing',
        'Required compliance training assigned — scoped to actual engagement (see Training tab)',
    ]},
    {'key': 'ongoing', 'title': 'Phase 3 — Ongoing Engagement', 'owner': 'Engagement Manager', 'items': [
        'Training and exclusion screening confirmed current before any MCO-facing task',
        'Deliverable/milestone check-ins scheduled per the contract\'s own terms',
        'No fixed daily schedule, mandatory hours, or DDI-directed work method beyond scope of work',
    ]},
    {'key': 'renewal', 'title': 'Phase 4 — Renewal, Extension, or Termination', 'owner': 'HR/Contracts', 'items': [
        'Contract renewal/extension/termination decision made per the contract\'s own terms and notice provisions',
        'If renewed: exclusion screening and training currency re-verified before renewal is executed',
        'If terminated: system access revoked, final invoice reconciled, contractor file closed out to retention',
    ]},
]

# Training catalog — index order matches SOP Section 4 items #1-#10.
# recurrence codes:
#   refresher_2yr        -> one-time, refresher every 2 years (interval_months=24)
#   annual_refresher     -> one-time, annual refresher (interval_months=12)
#   annual_11mo_reassign -> annual, re-flagged 11 months after completion, not 12 (interval_months=11)
#   annual_member_facing -> one-time; recurs annually ONLY if the record is marked member-facing
#   one_time             -> no recurrence at all (employees only — never assigned to contractors)
TRAININGS = [
    {
        'name': 'Identifying and Safeguarding PII', 'source': 'DCSA',
        'recurrence': 'refresher_2yr', 'interval_months': 24,
        'recurrence_label': 'One-time, refresher every 2 years',
        'contractor_trigger': 'Contractor accesses any member/participant data',
        'contractor_default': 'pending',
    },
    {
        'name': 'HIPAA Training (Course For HIPAA — NA Learning Institute)', 'source': 'NA Learning Institute',
        'recurrence': 'annual_refresher', 'interval_months': 12,
        'recurrence_label': 'One-time, annual refresher',
        'contractor_trigger': "Contractor's scope involves PHI",
        'contractor_default': 'pending',
    },
    {
        'name': 'Medicare and Medicaid General Compliance Training (FWA)', 'source': 'DWC Training',
        'recurrence': 'annual_11mo_reassign', 'interval_months': 11, 'cms_hard_deadline_days': 90,
        'recurrence_label': 'Annual — required for all FDR-adjacent staff (reassigned at 11 months)',
        'contractor_trigger': "Contractor's scope touches Medicaid/Medicare-adjacent administrative or health services",
        'contractor_default': 'pending',
    },
    {
        'name': 'Medicare Fraud & Abuse', 'source': 'DWC Training',
        'recurrence': 'annual_11mo_reassign', 'interval_months': 11, 'cms_hard_deadline_days': 90,
        'recurrence_label': 'Annual (reassigned at 11 months)',
        'contractor_trigger': 'Same trigger as General Compliance/FWA',
        'contractor_default': 'pending',
    },
    {
        'name': 'Cultural Competence/Diversity', 'source': 'DWC Training',
        'recurrence': 'refresher_2yr', 'interval_months': 24,
        'recurrence_label': 'One-time, refresher every 2 years',
        'contractor_trigger': 'Contractor interacts with members directly',
        'contractor_default': 'pending',
    },
    {
        'name': 'Recipient Rights', 'source': 'DWC Training',
        'recurrence': 'annual_member_facing', 'interval_months': 12,
        'recurrence_label': 'One-time; refresher annually for member-facing roles',
        'contractor_trigger': 'Contractor interacts with members directly',
        'contractor_default': 'pending',
    },
    {
        'name': 'Abuse & Neglect: Reporting Requirements', 'source': 'DWC Training',
        'recurrence': 'annual_member_facing', 'interval_months': 12,
        'recurrence_label': 'One-time; refresher annually for member-facing roles',
        'contractor_trigger': 'Contractor interacts with members directly',
        'contractor_default': 'pending',
    },
    {
        'name': 'Anti-Harassment & Non-Discrimination', 'source': 'DWC Training',
        'recurrence': 'refresher_2yr', 'interval_months': 24,
        'recurrence_label': 'One-time, refresher every 2 years',
        'contractor_trigger': 'Contractor works on-site or with DDI staff regularly',
        'contractor_default': 'pending',
    },
    {
        'name': 'Code of Conduct / Conflict of Interest Attestation', 'source': 'Internal',
        'recurrence': 'annual_11mo_reassign', 'interval_months': 11,
        'recurrence_label': 'Annual re-attestation (reassigned at 11 months)',
        'contractor_trigger': 'All contractors',
        'contractor_default': 'yes',
    },
    {
        'name': 'E-Verify / Form I-9 Basics', 'source': 'E-Verify.gov',
        'recurrence': 'one_time', 'interval_months': None,
        'recurrence_label': 'One-time',
        'contractor_trigger': 'Does not apply — employment-eligibility mechanism, employees only',
        'contractor_default': 'no', 'employee_only': True,
    },
]

DIVISIONS = [
    'DEPOINTE (NEMT Coordination)', 'HAVEN', 'SHIELD', 'VITAL', 'ARENA/PRIME',
    '3D Ink Signatures/CNTDA', 'Freight 1st Direct', 'DEPOINTE DNA', 'Corporate/HR/Admin',
]

# ─── Company email policy (added Jul 2026) ────────────────────────
# NOT every hire gets a @deedavis.biz alias — only roles that actually need
# a professional-facing address (client/CO/vendor correspondence, signatures
# on documents, etc.). Policy lives in the 'NEXUS HR ROLE EMAIL POLICY'
# Airtable table, NOT a hardcoded list here — Dee/HR add/remove/edit rows
# directly in Airtable (ROLE, REQUIRES_COMPANY_EMAIL checkbox, NOTES) and
# it takes effect immediately, no code change, no deploy (per Dee: "all of
# this is to be autogenerated and automated"). Table starts EMPTY — no role
# fabricated without Dee's sign-off — so until rows are added, everyone
# defaults to False (no unrequested aliases). Falls back to the last-known
# policy mirrored to ROLE_POLICY_LOCAL_FILE if Airtable is unreachable.

_role_policy_cache = {'data': None, 'ts': 0.0}
ROLE_POLICY_CACHE_TTL = 60  # seconds


def _load_role_email_policy(force=False):
    now = datetime.utcnow().timestamp()
    if not force and _role_policy_cache['data'] is not None and (now - _role_policy_cache['ts']) < ROLE_POLICY_CACHE_TTL:
        return _role_policy_cache['data']
    table = _airtable_table(ROLE_POLICY_TABLE)
    rows = None
    if table is not None:
        try:
            rows = []
            for r in table.all():
                f = r.get('fields', {})
                role = (f.get('ROLE') or '').strip()
                if role:
                    rows.append({
                        'role': role,
                        'requiresCompanyEmail': bool(f.get('REQUIRES_COMPANY_EMAIL', False)),
                        'notes': f.get('NOTES', ''),
                    })
            with open(ROLE_POLICY_LOCAL_FILE, 'w') as fp:
                json.dump(rows, fp, indent=2)  # mirror for offline fallback
        except Exception:
            rows = None
    if rows is None:
        if os.path.exists(ROLE_POLICY_LOCAL_FILE):
            try:
                with open(ROLE_POLICY_LOCAL_FILE, 'r') as fp:
                    rows = json.load(fp)
            except Exception:
                rows = []
        else:
            rows = []
    _role_policy_cache['data'] = rows
    _role_policy_cache['ts'] = now
    return rows


def role_requires_company_email(role):
    """Case-insensitive exact match against the 'NEXUS HR ROLE EMAIL POLICY'
    Airtable table (~60s cache). Returns False (no email) for blank/
    unmatched roles, and False for everyone if the table is still empty —
    safer default than auto-creating aliases nobody asked for."""
    role = (role or '').strip().lower()
    if not role:
        return False
    for row in _load_role_email_policy():
        if row['role'].strip().lower() == role:
            return bool(row['requiresCompanyEmail'])
    return False


# ─── Employee / Vendor Number (added Jul 2026, revised twice same day per
# Dee: (1) "should read in a way it's easy to know who what when where and
# why," then (2) "remove the DDI...it's redundant, we are DDI" + "how do i
# know that a customer care agent is working in the HAP account, or the
# MOLINA account, or how do we know if they are a manager, supervisor
# etc") — Generated the moment onboarding STARTS (record creation), not at
# completion — distinct from the company email, which is deferred until
# credentialing clears (see _maybe_provision_company_email()).
#
# FORMAT:  [DIVISION]-[ACCOUNT]-[LEVEL]-[EMP|VEN]-[YYMM]-[SEQ]
# EXAMPLE: HAVN-HAP-AGT-EMP-2607-0001
#
# Decoded left to right:
#   HAVN  -> WHERE/WHY — division/program the hire serves (see
#            DIVISION_CODES below)
#   HAP   -> WHICH ACCOUNT/CLIENT this hire's work is tied to — HAP
#            CareSource, Molina, etc. See 'NEXUS HR ACCOUNT CODES'
#            Airtable table — GEN (general/not account-specific) if blank
#            or the account isn't a live, signed one yet. Answers "how do
#            I know a customer care agent is working the HAP account vs
#            the Molina account" — it's literally in the ID.
#   AGT   -> SENIORITY/LEVEL — Agent, Supervisor, Manager, Director, etc.
#            See 'NEXUS HR LEVEL CODES' Airtable table — STF (generic
#            staff, no specific tier) if blank/unmatched. Answers "how do
#            we know if they are a manager, supervisor, etc."
#   EMP   -> WHO/WHAT — worker type: EMP (W-2 employee) or VEN (1099
#            contractor/vendor — Dee's "vendor number")
#   2607  -> WHEN — YYMM of the person's start date (falls back to today's
#            date if startdate isn't set yet at creation time)
#   0001  -> sequence, scoped to that exact division+account+level+type+
#            month bucket (NOT a global counter) — keeps the number itself
#            meaningful instead of an opaque ever-growing count.
#
# No "DDI-" prefix — per Dee, redundant, since every record in this system
# already is DDI. ACCOUNT and LEVEL are both Airtable-backed (like the
# role email policy) — Dee/HR add new accounts the moment a contract goes
# live, and new level tiers any time, with zero code changes.

DIVISION_CODES = {
    'DEPOINTE (NEMT Coordination)': 'DPTE',
    'HAVEN': 'HAVN',
    'SHIELD': 'SHLD',
    'VITAL': 'VITL',
    'ARENA/PRIME': 'ARPR',
    '3D Ink Signatures/CNTDA': 'CNTD',
    'Freight 1st Direct': 'FRT1',
    'DEPOINTE DNA': 'DDNA',
    'Corporate/HR/Admin': 'CORP',
}
DIVISION_CODE_FALLBACK = 'GENL'  # division blank or not one of the above


def _division_code(division):
    return DIVISION_CODES.get((division or '').strip(), DIVISION_CODE_FALLBACK)


# ─── Account codes (which client/MCO contract a hire's work is tied to) ──
ACCOUNT_CODE_FALLBACK = 'GEN'  # blank, or not yet a live/signed account
_account_codes_cache = {'data': None, 'ts': 0.0}
ACCOUNT_CODES_CACHE_TTL = 60


def _load_account_codes(force=False):
    now = datetime.utcnow().timestamp()
    if not force and _account_codes_cache['data'] is not None and (now - _account_codes_cache['ts']) < ACCOUNT_CODES_CACHE_TTL:
        return _account_codes_cache['data']
    table = _airtable_table(ACCOUNT_CODES_TABLE)
    rows = None
    if table is not None:
        try:
            rows = []
            for r in table.all():
                f = r.get('fields', {})
                name = (f.get('ACCOUNT_NAME') or '').strip()
                code = (f.get('ACCOUNT_CODE') or '').strip()
                if name and code:
                    rows.append({'name': name, 'code': code, 'status': f.get('STATUS', ''), 'notes': f.get('NOTES', '')})
            with open(ACCOUNT_CODES_LOCAL_FILE, 'w') as fp:
                json.dump(rows, fp, indent=2)
        except Exception:
            rows = None
    if rows is None:
        if os.path.exists(ACCOUNT_CODES_LOCAL_FILE):
            try:
                with open(ACCOUNT_CODES_LOCAL_FILE, 'r') as fp:
                    rows = json.load(fp)
            except Exception:
                rows = []
        else:
            rows = []
    _account_codes_cache['data'] = rows
    _account_codes_cache['ts'] = now
    return rows


def _account_code(account_name):
    account_name = (account_name or '').strip().lower()
    if not account_name:
        return ACCOUNT_CODE_FALLBACK
    for row in _load_account_codes():
        if row['name'].strip().lower() == account_name:
            return row['code']
    return ACCOUNT_CODE_FALLBACK  # not blank, but not a recognized live account either — safe fallback, never invents a code


# ─── Level codes (seniority/hierarchy tier) ──────────────────────
LEVEL_CODE_FALLBACK = 'STF'  # blank/unmatched — generic staff, no specific tier
_level_codes_cache = {'data': None, 'ts': 0.0}
LEVEL_CODES_CACHE_TTL = 60


def _load_level_codes(force=False):
    now = datetime.utcnow().timestamp()
    if not force and _level_codes_cache['data'] is not None and (now - _level_codes_cache['ts']) < LEVEL_CODES_CACHE_TTL:
        return _level_codes_cache['data']
    table = _airtable_table(LEVEL_CODES_TABLE)
    rows = None
    if table is not None:
        try:
            rows = []
            for r in table.all():
                f = r.get('fields', {})
                name = (f.get('LEVEL_NAME') or '').strip()
                code = (f.get('LEVEL_CODE') or '').strip()
                if name and code:
                    rows.append({'name': name, 'code': code, 'notes': f.get('NOTES', '')})
            with open(LEVEL_CODES_LOCAL_FILE, 'w') as fp:
                json.dump(rows, fp, indent=2)
        except Exception:
            rows = None
    if rows is None:
        if os.path.exists(LEVEL_CODES_LOCAL_FILE):
            try:
                with open(LEVEL_CODES_LOCAL_FILE, 'r') as fp:
                    rows = json.load(fp)
            except Exception:
                rows = []
        else:
            rows = []
    _level_codes_cache['data'] = rows
    _level_codes_cache['ts'] = now
    return rows


def _level_code(level_name):
    level_name = (level_name or '').strip().lower()
    if not level_name:
        return LEVEL_CODE_FALLBACK
    for row in _load_level_codes():
        if row['name'].strip().lower() == level_name:
            return row['code']
    return LEVEL_CODE_FALLBACK


def personnel_number_label(worker_type):
    return 'Vendor Number' if worker_type == 'contractor' else 'Employee Number'


def _next_personnel_number(worker_type, division=None, startdate=None, account=None, level=None):
    """Builds the [DIVISION]-[ACCOUNT]-[LEVEL]-[EMP|VEN]-[YYMM]-[SEQ] code
    described above. Sequence is scoped to that exact division+account+
    level+type+month bucket (based on the highest number already issued in
    that bucket, across whichever backend is active — Airtable or local,
    see _load_all()). Not concurrency-safe against simultaneous adds, but
    DDI's hiring volume/admin-driven flow makes that an acceptable risk;
    revisit if that ever changes."""
    type_code = 'VEN' if worker_type == 'contractor' else 'EMP'
    div_code = _division_code(division)
    acct_code = _account_code(account)
    lvl_code = _level_code(level)
    dt = parse_date(startdate) or today_utc()
    prefix = f'{div_code}-{acct_code}-{lvl_code}-{type_code}-{dt.strftime("%y%m")}-'
    records, _ = _load_all()
    max_n = 0
    for r in records:
        num = r.get('personnelNumber') or ''
        if num.startswith(prefix):
            try:
                max_n = max(max_n, int(num[len(prefix):]))
            except ValueError:
                pass
    return f'{prefix}{max_n + 1:04d}'

# ─── GATEWAY self-service catalogs ────────────────────────────────
# What the new hire/contractor is asked to upload or e-sign themselves,
# via the GATEWAY portal (gateway.deedavis.biz), keyed by workerType.
# 'key' must be unique within its list and is what the portal posts back —
# never rename an existing key once contractors/employees may have used it,
# only add new ones or retire (leave the key, drop from the active list).
SELF_SERVICE_DOCUMENTS = {
    'employee': [
        {'key': 'i9_list_a_or_c', 'label': "I-9 Supporting Document — List A or List C (e.g. Passport, Social Security Card)"},
        {'key': 'i9_list_b', 'label': "I-9 Supporting Document — List B (e.g. Driver's License / State ID)"},
        {'key': 'offer_letter_signed', 'label': 'Signed Offer Letter'},
    ],
    'contractor': [
        {'key': 'w9', 'label': 'W-9'},
        {'key': 'coi', 'label': 'Certificate of Insurance (if required by the engagement)'},
        {'key': 'ic_agreement_signed', 'label': 'Signed Independent Contractor Agreement / MSA'},
    ],
}

SELF_SERVICE_ACKNOWLEDGMENTS = {
    'employee': [
        {'key': 'handbook', 'label': 'Employee Handbook'},
        {'key': 'coi_policy', 'label': 'Code of Conduct / Conflict of Interest Policy'},
        {'key': 'nda', 'label': 'Confidentiality / NDA'},
    ],
    'contractor': [
        {'key': 'coi_policy', 'label': 'Code of Conduct (Contractor Flow-Down Obligation)'},
        {'key': 'nda', 'label': 'Confidentiality / NDA'},
    ],
}

DOCUMENTS_TABLE_FIELD = 'DOCUMENTS'  # Airtable multipleAttachments field name (see migrate_gateway_fields.py)

# 30-Day Check-In Agenda — SOP Section 8, tracked as a structured sub-checklist
# on the employee day30 phase (contractors don't get calendar-based "check-ins").
AGENDAS = {
    'day30': [
        'Training completion status (all 10 items, or documented exception with new due date)',
        'Role clarity — any confusion on "coordinate, not provide" positioning',
        'Systems comfort (NEXUS, PRISM)',
        'Open questions or blockers',
        'Manager feedback / any performance flags',
    ],
}

INTERNAL_TARGET_DAYS = 30      # DDI internal target for all 10 training items, from date of hire
CMS_HARD_DEADLINE_DAYS = 90    # CMS regulatory floor — General Compliance/FWA + Medicare Fraud & Abuse only
SCREENING_CADENCE_MONTHS = 1   # OIG LEIE + GSA SAM.gov re-screening — monthly, for the life of employment/engagement


# ─── Date helpers ────────────────────────────────────────────────

def add_months(d, months):
    """Add calendar months to a date, clamping day-of-month to the target month's length."""
    total = d.month - 1 + months
    year = d.year + total // 12
    month = total % 12 + 1
    day = min(d.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def parse_date(s):
    if not s:
        return None
    try:
        return datetime.strptime(str(s)[:10], '%Y-%m-%d').date()
    except ValueError:
        return None


def today_utc():
    return datetime.utcnow().date()


def phases_for(worker_type):
    return PHASES_CONTRACTOR if worker_type == 'contractor' else PHASES_EMPLOYEE


# ─── Record construction ─────────────────────────────────────────

def _training_rows(worker_type):
    rows = []
    for item in TRAININGS:
        row = {'status': 'Not Started', 'due': '', 'certRef': '', 'completedBy': '', 'completedDate': ''}
        if worker_type == 'contractor':
            row['applicable'] = item.get('contractor_default', 'pending')
        else:
            # Employees get all 10 items — none are contractor-scoped.
            row['applicable'] = 'yes'
        rows.append(row)
    return rows


def _default_agenda():
    return {k: {'items': [False] * len(v), 'notes': ''} for k, v in AGENDAS.items()}


def _default_classification():
    return {
        'boundedScope': False, 'ownToolsSchedule': False, 'worksOtherClients': False,
        'noSupervisoryIntegration': False, 'deliverableBasedPay': False,
        'notes': '', 'routedToCounsel': False, 'routedDate': '',
    }


def _new_record(name, worker_type, division, startdate, member_facing=True, email='', role='',
                 company_email_override=None, account='', level=''):
    worker_type = worker_type if worker_type in ('employee', 'contractor') else 'employee'
    phases = phases_for(worker_type)
    checklist = {p['key']: [False] * len(p['items']) for p in phases}
    now = datetime.utcnow().isoformat() + 'Z'
    return {
        'id': 'HR-' + uuid.uuid4().hex[:8].upper(),
        'name': name,
        'email': (email or '').strip().lower(),
        'role': (role or '').strip(),
        'account': (account or '').strip(),    # which client/MCO contract this hire's work is tied to (blank = general, not account-specific)
        'level': (level or '').strip(),        # seniority tier — Agent/Supervisor/Manager/Director etc (blank = generic staff)
        'personnelNumber': _next_personnel_number(worker_type, division, startdate, account, level),  # Employee/Vendor Number — generated NOW, at onboarding start
        'companyEmail': '',                    # provisioned later, on credentialing completion — see _maybe_provision_company_email()
        'companyEmailError': '',                # set if provisioning attempt failed, so HR knows to retry manually
        'companyEmailOverride': company_email_override,  # True/False/None — HR override of the role-based default, captured at creation, acted on at credentialing completion
        'companyEmailDeclined': False,          # set True if HR explicitly declines — stops repeat eligibility checks
        'workerType': worker_type,
        'division': division or '',
        'startdate': startdate or '',
        'status': 'Active',
        'memberFacing': bool(member_facing),
        'checklist': checklist,
        'training': _training_rows(worker_type),
        'exclusionLog': [],
        'classification': _default_classification() if worker_type == 'contractor' else None,
        'agenda': _default_agenda(),
        'documents': [],
        'acknowledgments': [],
        'auditLog': [{'ts': now, 'actor': 'system', 'action': 'Record created'}],
        'created': now,
        'airtable_id': None,
    }


def _log_audit(rec, actor, action):
    rec.setdefault('auditLog', []).append({
        'ts': datetime.utcnow().isoformat() + 'Z',
        'actor': (actor or '').strip() or 'unspecified',
        'action': action,
    })


# ─── Local JSON fallback (roster) ────────────────────────────────

def _load_local():
    if os.path.exists(LOCAL_FILE):
        try:
            with open(LOCAL_FILE, 'r') as f:
                data = json.load(f)
                if isinstance(data, dict) and 'records' in data:
                    return data['records']
        except Exception:
            pass
    return []


def _save_local(records):
    with open(LOCAL_FILE, 'w') as f:
        json.dump({'records': records}, f, indent=2, default=str)


# ─── Airtable <-> record serialization (roster) ──────────────────

def _record_to_fields(rec):
    return {
        'RECORD_ID': rec['id'],
        'NAME': rec['name'],
        'EMAIL': rec.get('email', ''),
        'ROLE': rec.get('role', ''),
        'ACCOUNT': rec.get('account', ''),
        'LEVEL': rec.get('level', ''),
        'PERSONNEL_NUMBER': rec.get('personnelNumber', ''),
        'COMPANY_EMAIL': rec.get('companyEmail', ''),
        'COMPANY_EMAIL_ERROR': rec.get('companyEmailError', ''),
        'COMPANY_EMAIL_OVERRIDE': (
            '' if rec.get('companyEmailOverride') is None
            else ('yes' if rec.get('companyEmailOverride') else 'no')
        ),
        'COMPANY_EMAIL_DECLINED': bool(rec.get('companyEmailDeclined', False)),
        'WORKER_TYPE': 'Contractor (1099)' if rec['workerType'] == 'contractor' else 'Employee (W-2)',
        'DIVISION': rec.get('division', ''),
        'START_DATE': rec.get('startdate') or None,
        'STATUS': rec.get('status', 'Active'),
        'MEMBER_FACING': bool(rec.get('memberFacing', True)),
        'CHECKLIST_JSON': json.dumps(rec.get('checklist', {})),
        'TRAINING_JSON': json.dumps(rec.get('training', [])),
        'EXCLUSION_LOG_JSON': json.dumps(rec.get('exclusionLog', [])),
        'CLASSIFICATION_JSON': json.dumps(rec.get('classification')) if rec.get('classification') else '',
        'AGENDA_JSON': json.dumps(rec.get('agenda', {})),
        'DOCUMENTS_JSON': json.dumps(rec.get('documents', [])),
        'ACKNOWLEDGMENTS_JSON': json.dumps(rec.get('acknowledgments', [])),
        'AUDIT_LOG_JSON': json.dumps(rec.get('auditLog', [])),
    }


def _fields_to_record(airtable_record):
    f = airtable_record.get('fields', {})
    worker_type = 'contractor' if str(f.get('WORKER_TYPE', '')).startswith('Contractor') else 'employee'

    def _jload(key, default):
        try:
            return json.loads(f.get(key) or 'null') or default
        except Exception:
            return default

    return {
        'id': f.get('RECORD_ID') or airtable_record.get('id'),
        'name': f.get('NAME', ''),
        'email': (f.get('EMAIL', '') or '').strip().lower(),
        'role': f.get('ROLE', ''),
        'account': f.get('ACCOUNT', ''),
        'level': f.get('LEVEL', ''),
        'personnelNumber': f.get('PERSONNEL_NUMBER', ''),
        'companyEmail': f.get('COMPANY_EMAIL', ''),
        'companyEmailError': f.get('COMPANY_EMAIL_ERROR', ''),
        'companyEmailOverride': (
            None if f.get('COMPANY_EMAIL_OVERRIDE', '') not in ('yes', 'no')
            else f.get('COMPANY_EMAIL_OVERRIDE') == 'yes'
        ),
        'companyEmailDeclined': bool(f.get('COMPANY_EMAIL_DECLINED', False)),
        'workerType': worker_type,
        'division': f.get('DIVISION', ''),
        'startdate': f.get('START_DATE', ''),
        'status': f.get('STATUS', 'Active'),
        'memberFacing': bool(f.get('MEMBER_FACING', True)),
        'checklist': _jload('CHECKLIST_JSON', {}),
        'training': _jload('TRAINING_JSON', []),
        'exclusionLog': _jload('EXCLUSION_LOG_JSON', []),
        'classification': _jload('CLASSIFICATION_JSON', None) if worker_type == 'contractor' else None,
        'agenda': _jload('AGENDA_JSON', _default_agenda()),
        'documents': _jload('DOCUMENTS_JSON', []),
        'acknowledgments': _jload('ACKNOWLEDGMENTS_JSON', []),
        'auditLog': _jload('AUDIT_LOG_JSON', []),
        'created': airtable_record.get('createdTime', ''),
        'airtable_id': airtable_record.get('id'),
    }


# ─── Unified data access (Airtable primary, local fallback) ─────

def _load_all():
    table = _airtable_table(HR_TABLE)
    if table is not None:
        try:
            return [_fields_to_record(r) for r in table.all()], True
        except Exception:
            pass
    return _load_local(), False


def _find(record_id):
    records, from_airtable = _load_all()
    for r in records:
        if r['id'] == record_id:
            return r, records, from_airtable
    return None, records, from_airtable


def _find_by_email(email):
    """Lookup for the GATEWAY self-service portal — matches on EMAIL, active
    records only (an archived record has no portal access)."""
    email = (email or '').strip().lower()
    if not email:
        return None, [], False
    records, from_airtable = _load_all()
    for r in records:
        if (r.get('email') or '').strip().lower() == email and r.get('status', 'Active') == 'Active':
            return r, records, from_airtable
    return None, records, from_airtable


def _persist(rec, records, from_airtable):
    """Save one record back to whichever store it came from. typecast=True lets
    Airtable accept new single-select values (divisions, statuses) automatically."""
    if from_airtable:
        table = _airtable_table(HR_TABLE)
        if table is not None:
            try:
                if rec.get('airtable_id'):
                    table.update(rec['airtable_id'], _record_to_fields(rec), typecast=True)
                else:
                    created = table.create(_record_to_fields(rec), typecast=True)
                    rec['airtable_id'] = created.get('id')
                return
            except Exception:
                pass
    # Local fallback path — replace or append, then save whole roster
    local = _load_local()
    idx = next((i for i, r in enumerate(local) if r['id'] == rec['id']), None)
    if idx is not None:
        local[idx] = rec
    else:
        local.append(rec)
    _save_local(local)


def _create(rec):
    table = _airtable_table(HR_TABLE)
    if table is not None:
        try:
            created = table.create(_record_to_fields(rec), typecast=True)
            rec['airtable_id'] = created.get('id')
            return
        except Exception:
            pass
    local = _load_local()
    local.append(rec)
    _save_local(local)


# ─── Annual FDR Attestation — local fallback + Airtable ─────────

def _load_attestations_local():
    if os.path.exists(ATTEST_LOCAL_FILE):
        try:
            with open(ATTEST_LOCAL_FILE, 'r') as f:
                data = json.load(f)
                if isinstance(data, dict) and 'records' in data:
                    return data['records']
        except Exception:
            pass
    return []


def _save_attestations_local(records):
    with open(ATTEST_LOCAL_FILE, 'w') as f:
        json.dump({'records': records}, f, indent=2, default=str)


def _attestation_to_fields(rec):
    return {
        'YEAR': rec['year'],
        'ATTESTED': bool(rec.get('attested', True)),
        'ATTESTOR_NAME': rec.get('attestorName', ''),
        'ATTESTED_DATE': rec.get('attestedDate') or None,
        'REFERENCE_NOTES': rec.get('referenceNotes', ''),
        'CREATED_AT': rec.get('created', ''),
        'UPDATED_AT': datetime.utcnow().isoformat() + 'Z',
    }


def _fields_to_attestation(airtable_record):
    f = airtable_record.get('fields', {})
    return {
        'year': f.get('YEAR'),
        'attested': bool(f.get('ATTESTED', False)),
        'attestorName': f.get('ATTESTOR_NAME', ''),
        'attestedDate': f.get('ATTESTED_DATE', ''),
        'referenceNotes': f.get('REFERENCE_NOTES', ''),
        'created': f.get('CREATED_AT', ''),
        'airtable_id': airtable_record.get('id'),
    }


def _load_attestations():
    table = _airtable_table(ATTEST_TABLE)
    if table is not None:
        try:
            return [_fields_to_attestation(r) for r in table.all()], True
        except Exception:
            pass
    return _load_attestations_local(), False


def _persist_attestation(rec, records, from_airtable):
    if from_airtable:
        table = _airtable_table(ATTEST_TABLE)
        if table is not None:
            try:
                if rec.get('airtable_id'):
                    table.update(rec['airtable_id'], _attestation_to_fields(rec), typecast=True)
                else:
                    created = table.create(_attestation_to_fields(rec), typecast=True)
                    rec['airtable_id'] = created.get('id')
                return
            except Exception:
                pass
    local = _load_attestations_local()
    idx = next((i for i, r in enumerate(local) if r.get('year') == rec.get('year')), None)
    if idx is not None:
        local[idx] = rec
    else:
        local.append(rec)
    _save_attestations_local(local)


# ═══════════════════════════════════════════════════════════════
# COMPLIANCE ENGINE — training recurrence + screening cadence
# ═══════════════════════════════════════════════════════════════

def training_compliance(rec, idx, item, today=None):
    """Compute the live compliance state of one training item on one record.

    Returns dict: state, severity ('none'|'info'|'warning'|'critical'),
    nextDue (iso date or None), detail (human-readable string).
    """
    today = today or today_utc()
    worker_type = rec.get('workerType', 'employee')
    rows = rec.get('training') or []
    t = rows[idx] if idx < len(rows) else {}
    hire_date = parse_date(rec.get('startdate'))

    # Contractor scoping — E-Verify/I-9 never applies to contractors
    if worker_type == 'contractor':
        if item.get('employee_only'):
            return {'state': 'not_applicable', 'severity': 'none', 'nextDue': None,
                    'detail': 'Does not apply to contractors (employment-eligibility mechanism)'}
        applicable = t.get('applicable', item.get('contractor_default', 'pending'))
        if applicable == 'no':
            return {'state': 'not_applicable', 'severity': 'none', 'nextDue': None,
                    'detail': 'Marked not applicable to this engagement\'s scope'}
        if applicable == 'pending':
            return {'state': 'pending_scoping', 'severity': 'info', 'nextDue': None,
                    'detail': 'Engagement Manager has not yet scoped this item to the contract'}

    status = t.get('status', 'Not Started')

    if status != 'Complete':
        if not hire_date:
            return {'state': 'pending', 'severity': 'none', 'nextDue': None, 'detail': 'No date of hire/engagement on file'}
        soft_deadline = hire_date + timedelta(days=INTERNAL_TARGET_DAYS)
        hard_days = item.get('cms_hard_deadline_days')
        if hard_days:
            hard_deadline = hire_date + timedelta(days=hard_days)
            if today > hard_deadline:
                return {'state': 'cms_hard_missed', 'severity': 'critical', 'nextDue': hard_deadline.isoformat(),
                        'detail': f'CMS {hard_days}-day compliance floor missed — investigation/remediation required'}
            if today > soft_deadline:
                return {'state': 'internal_target_missed', 'severity': 'warning', 'nextDue': hard_deadline.isoformat(),
                        'detail': f'Past DDI\'s {INTERNAL_TARGET_DAYS}-day internal target; CMS hard floor is {hard_days} days'}
            return {'state': 'pending', 'severity': 'none', 'nextDue': soft_deadline.isoformat(), 'detail': 'Not yet due'}
        if today > soft_deadline:
            return {'state': 'internal_target_missed', 'severity': 'warning', 'nextDue': soft_deadline.isoformat(),
                    'detail': f'Past DDI\'s {INTERNAL_TARGET_DAYS}-day internal target'}
        return {'state': 'pending', 'severity': 'none', 'nextDue': soft_deadline.isoformat(), 'detail': 'Not yet due'}

    # Completed at least once — evaluate recurrence
    recurrence = item.get('recurrence')
    if recurrence == 'one_time':
        return {'state': 'ok', 'severity': 'none', 'nextDue': None, 'detail': 'One-time — no recurrence'}

    if recurrence == 'annual_member_facing' and not rec.get('memberFacing', True):
        return {'state': 'ok', 'severity': 'none', 'nextDue': None,
                'detail': 'One-time — role not marked member-facing, no annual recurrence'}

    completed_date = parse_date(t.get('completedDate'))
    if not completed_date:
        return {'state': 'ok', 'severity': 'none', 'nextDue': None, 'detail': 'Complete (no completion date on file)'}

    interval = item.get('interval_months') or 12
    next_due = add_months(completed_date, interval)
    if today > next_due:
        return {'state': 'recurrence_due', 'severity': 'warning', 'nextDue': next_due.isoformat(),
                'detail': f'Recurrence lapsed — {item.get("recurrence_label", "")}'}
    return {'state': 'ok', 'severity': 'none', 'nextDue': next_due.isoformat(),
            'detail': f'Current — next due {next_due.isoformat()}'}


def all_training_compliance(rec, today=None):
    return [training_compliance(rec, i, item, today) for i, item in enumerate(TRAININGS)]


def screening_compliance(rec, today=None):
    """Monthly OIG LEIE + GSA SAM.gov screening cadence, per SOP Section 5."""
    today = today or today_utc()
    log = rec.get('exclusionLog', [])
    hire_date = parse_date(rec.get('startdate'))

    dated_entries = [(parse_date(e.get('date')), e) for e in log if parse_date(e.get('date'))]
    dated_entries.sort(key=lambda pair: pair[0])

    if not dated_entries:
        if hire_date and today >= hire_date:
            return {'state': 'never_screened', 'severity': 'critical', 'nextDue': hire_date.isoformat(),
                    'detail': 'No OIG LEIE / GSA SAM.gov screening on file — required at hire/engagement'}
        return {'state': 'pending', 'severity': 'none', 'nextDue': None, 'detail': 'Not yet due'}

    last_date, last_entry = dated_entries[-1]
    flagged_open = str(last_entry.get('result', '')).startswith('Flagged')
    next_due = add_months(last_date, SCREENING_CADENCE_MONTHS)

    if flagged_open:
        return {'state': 'flagged_open', 'severity': 'critical', 'nextDue': next_due.isoformat(),
                'detail': f'Open flagged exclusion match ({last_date.isoformat()}) — escalate to Compliance before further MCO-facing work'}
    if today > next_due:
        return {'state': 'overdue', 'severity': 'warning', 'nextDue': next_due.isoformat(),
                'detail': f'Monthly re-screen overdue — last screened {last_date.isoformat()}'}
    return {'state': 'ok', 'severity': 'none', 'nextDue': next_due.isoformat(),
            'detail': f'Current — next screening due {next_due.isoformat()}'}


def _progress(rec):
    total = 0
    done = 0
    for p in phases_for(rec['workerType']):
        vals = rec.get('checklist', {}).get(p['key'], [])
        total += len(p['items'])
        done += sum(1 for v in vals if v)
    for i, item in enumerate(TRAININGS):
        comp = training_compliance(rec, i, item)
        if comp['state'] == 'not_applicable':
            continue
        total += 1
        rows = rec.get('training') or []
        if idx_status_complete(rows, i):
            done += 1
    return round((done / total) * 100) if total else 0


def idx_status_complete(rows, idx):
    return idx < len(rows) and rows[idx].get('status') == 'Complete'


# ═══════════════════════════════════════════════════════════════
# CONFIG ENDPOINT
# ═══════════════════════════════════════════════════════════════

@hr_onboarding.route('/nexus/hr/onboarding/config', methods=['GET'])
def get_config():
    return jsonify({
        'phases_employee': PHASES_EMPLOYEE,
        'phases_contractor': PHASES_CONTRACTOR,
        'trainings': TRAININGS,
        'divisions': DIVISIONS,
        'agendas': AGENDAS,
        'internal_target_days': INTERNAL_TARGET_DAYS,
        'cms_hard_deadline_days': CMS_HARD_DEADLINE_DAYS,
        'screening_cadence_months': SCREENING_CADENCE_MONTHS,
        'self_service_documents': SELF_SERVICE_DOCUMENTS,
        'self_service_acknowledgments': SELF_SERVICE_ACKNOWLEDGMENTS,
    })


# ═══════════════════════════════════════════════════════════════
# ROSTER — LIST / CREATE
# ═══════════════════════════════════════════════════════════════

@hr_onboarding.route('/nexus/hr/onboarding', methods=['GET'])
def list_roster():
    records, from_airtable = _load_all()
    include_archived = request.args.get('include_archived', '').lower() == 'true'
    if not include_archived:
        records = [r for r in records if r.get('status', 'Active') != 'Archived']
    roster = [{
        'id': r['id'],
        'name': r['name'],
        'role': r.get('role', ''),
        'account': r.get('account', ''),
        'level': r.get('level', ''),
        'personnelNumber': r.get('personnelNumber', ''),
        'companyEmail': r.get('companyEmail', ''),
        'workerType': r['workerType'],
        'division': r.get('division', ''),
        'startdate': r.get('startdate', ''),
        'status': r.get('status', 'Active'),
        'memberFacing': r.get('memberFacing', True),
        'progress': _progress(r),
        'screening': screening_compliance(r)['state'],
    } for r in records]
    return jsonify({
        'roster': roster,
        'count': len(roster),
        'source': 'airtable' if from_airtable else 'local',
    })


@hr_onboarding.route('/nexus/hr/onboarding', methods=['POST'])
def add_hire():
    data = request.get_json(force=True) or {}
    name = (data.get('name') or '').strip()
    if not name:
        return jsonify({'error': 'name is required'}), 400
    member_facing = data.get('memberFacing', True)
    email = (data.get('email') or '').strip().lower()
    role = (data.get('role') or '').strip()
    account = (data.get('account') or '').strip()  # which client/MCO contract — see NEXUS HR ACCOUNT CODES
    level = (data.get('level') or '').strip()      # seniority tier — see NEXUS HR LEVEL CODES
    override = data.get('provisionCompanyEmail')  # True/False/None — HR override of role-based default
    rec = _new_record(name, data.get('workerType'), data.get('division'), data.get('startdate'),
                       member_facing, email, role, company_email_override=override,
                       account=account, level=level)
    actor = (data.get('actor') or '').strip() or 'unspecified'

    label = personnel_number_label(rec['workerType'])
    _log_audit(rec, actor, f'Record created by {actor} — {label} assigned: {rec["personnelNumber"]}')
    if email:
        _log_audit(rec, actor, f'GATEWAY portal access enabled for {email}')

    # Company email is NOT provisioned here. It's deferred until
    # credentialing actually clears (the can-work gate) — see
    # _maybe_provision_company_email(), triggered from update_checklist(),
    # update_training(), and log_screening(). This just records the
    # eligibility decision now so the reasoning is visible in the audit log
    # from day one, even though the API call happens later.
    if override is False:
        rec['companyEmailDeclined'] = True
        _log_audit(rec, actor, 'Company email explicitly declined by HR for this hire')
    else:
        eligible = bool(override) if override is not None else role_requires_company_email(role)
        if eligible:
            _log_audit(rec, actor, f'Company email will be provisioned once credentialing clears (role: "{role or "unspecified"}"'
                                    + (', HR override: yes' if override else '') + ')')
        else:
            reason = f'role "{role}" not on the company-email list' if role else 'no role specified'
            _log_audit(rec, actor, f'Company email not provisioned — {reason}')

    _create(rec)
    return jsonify({'success': True, 'record': rec}), 201


@hr_onboarding.route('/nexus/hr/onboarding/<record_id>/provision-email', methods=['POST'])
def retry_provision_email(record_id):
    """Manual retry/override for company email provisioning — use when the
    automatic attempt at add_hire() failed (ImprovMX API down, name couldn't
    be slugified, etc.), or to re-point the alias's forward address."""
    data = request.get_json(force=True) or {}
    actor = (data.get('actor') or '').strip() or 'unspecified'
    forward_override = (data.get('forwardTo') or '').strip().lower()

    rec, records, from_airtable = _find(record_id)
    if not rec:
        return jsonify({'error': 'not found'}), 404

    forward_to = forward_override or rec.get('email', '')
    result = provision_employee_alias(rec['name'], forward_to)
    if result['success']:
        rec['companyEmail'] = result['companyEmail']
        rec['companyEmailError'] = ''
        rec['companyEmailDeclined'] = False  # manual trigger overrides any earlier decline
        _log_audit(rec, actor, f'Company email provisioned (manual override): {result["companyEmail"]} -> forwards to {forward_to}')
    else:
        rec['companyEmailError'] = result['error']
        _log_audit(rec, actor, f'Company email provisioning retry FAILED: {result["error"]}')

    _persist(rec, records, from_airtable)
    return jsonify({'success': result['success'], 'record': rec, 'error': result.get('error')})


# ═══════════════════════════════════════════════════════════════
# SINGLE RECORD — DETAIL / MUTATIONS
# ═══════════════════════════════════════════════════════════════

@hr_onboarding.route('/nexus/hr/onboarding/<record_id>', methods=['GET'])
def get_detail(record_id):
    rec, _, _ = _find(record_id)
    if not rec:
        return jsonify({'error': 'not found'}), 404
    rec['_progress'] = _progress(rec)
    rec['_trainingCompliance'] = all_training_compliance(rec)
    rec['_screening'] = screening_compliance(rec)
    return jsonify(rec)


@hr_onboarding.route('/nexus/hr/onboarding/<record_id>/checklist', methods=['PUT'])
def update_checklist(record_id):
    data = request.get_json(force=True) or {}
    phase = data.get('phase')
    idx = data.get('index')
    checked = bool(data.get('checked'))
    actor = (data.get('actor') or '').strip() or 'unspecified'

    rec, records, from_airtable = _find(record_id)
    if not rec:
        return jsonify({'error': 'not found'}), 404
    phase_def = next((p for p in phases_for(rec['workerType']) if p['key'] == phase), None)
    if phase_def is None or idx is None or not (0 <= int(idx) < len(phase_def['items'])):
        return jsonify({'error': 'invalid phase/index'}), 400

    idx = int(idx)
    rec['checklist'].setdefault(phase, [False] * len(phase_def['items']))
    rec['checklist'][phase][idx] = checked
    item_label = phase_def['items'][idx]
    _log_audit(rec, actor, f'{"Checked" if checked else "Unchecked"}: "{item_label}" ({phase})')
    _maybe_provision_company_email(rec, actor)
    _persist(rec, records, from_airtable)
    rec['_progress'] = _progress(rec)
    return jsonify({'success': True, 'record': rec})


@hr_onboarding.route('/nexus/hr/onboarding/<record_id>/training', methods=['PUT'])
def update_training(record_id):
    data = request.get_json(force=True) or {}
    idx = data.get('index')
    field = data.get('field')
    value = data.get('value', '')
    actor = (data.get('actor') or '').strip() or 'unspecified'
    allowed_fields = {'status', 'due', 'certRef', 'completedBy', 'applicable'}

    if field not in allowed_fields or idx is None or not (0 <= int(idx) < len(TRAININGS)):
        return jsonify({'error': 'invalid field/index'}), 400

    rec, records, from_airtable = _find(record_id)
    if not rec:
        return jsonify({'error': 'not found'}), 404

    idx = int(idx)
    while len(rec['training']) <= idx:
        rec['training'].append({'status': 'Not Started', 'due': '', 'certRef': '', 'completedBy': '',
                                 'completedDate': '', 'applicable': 'yes'})

    old_value = rec['training'][idx].get(field, '')
    rec['training'][idx][field] = value
    if field == 'status' and value == 'Complete':
        rec['training'][idx]['completedDate'] = datetime.utcnow().strftime('%Y-%m-%d')

    training_name = TRAININGS[idx]['name']
    if field == 'applicable':
        label = {'yes': 'Applicable', 'no': 'Not applicable', 'pending': 'Pending scoping'}.get(value, value)
        _log_audit(rec, actor, f'Training "{training_name}" scoping decision: {label}')
    else:
        _log_audit(rec, actor, f'Training "{training_name}" {field} changed: {old_value or "(blank)"} -> {value or "(blank)"}')
    _maybe_provision_company_email(rec, actor)
    _persist(rec, records, from_airtable)
    rec['_progress'] = _progress(rec)
    return jsonify({'success': True, 'record': rec})


@hr_onboarding.route('/nexus/hr/onboarding/<record_id>/screening', methods=['POST'])
def log_screening(record_id):
    data = request.get_json(force=True) or {}
    date_str = data.get('date')
    result = data.get('result') or 'Clear'
    notes = (data.get('notes') or '').strip()
    actor = (data.get('actor') or '').strip() or 'unspecified'
    if not date_str:
        return jsonify({'error': 'date is required'}), 400

    rec, records, from_airtable = _find(record_id)
    if not rec:
        return jsonify({'error': 'not found'}), 404

    entry = {'date': date_str, 'result': result, 'notes': notes, 'loggedBy': actor,
             'ts': datetime.utcnow().isoformat() + 'Z'}
    rec.setdefault('exclusionLog', []).append(entry)
    flagged = str(result).startswith('Flagged')
    _log_audit(rec, actor,
               f'Exclusion screening logged: {date_str}, result: {result}' + (f', notes: {notes}' if notes else ''))
    if flagged:
        _log_audit(rec, 'system', f'FLAGGED SCREENING — escalate to Compliance immediately ({date_str})')
    if not flagged:
        _maybe_provision_company_email(rec, actor)
    _persist(rec, records, from_airtable)
    return jsonify({'success': True, 'record': rec, 'flagged': flagged})


@hr_onboarding.route('/nexus/hr/onboarding/<record_id>/classification', methods=['PUT'])
def update_classification(record_id):
    """Worker-classification documentation — SOP Section 10.1 (employee SOP) /
    Section 8 (contractor SOP). Documentation, not legal advice; a genuinely
    unclear case should be routed to counsel before onboarding proceeds."""
    data = request.get_json(force=True) or {}
    actor = (data.get('actor') or '').strip() or 'unspecified'

    rec, records, from_airtable = _find(record_id)
    if not rec:
        return jsonify({'error': 'not found'}), 404
    if rec['workerType'] != 'contractor':
        return jsonify({'error': 'classification documentation applies to the contractor track only'}), 400

    cls = rec.get('classification') or _default_classification()
    bool_fields = ['boundedScope', 'ownToolsSchedule', 'worksOtherClients', 'noSupervisoryIntegration',
                   'deliverableBasedPay', 'routedToCounsel']
    changed = []
    for f in bool_fields:
        if f in data:
            new_val = bool(data[f])
            if cls.get(f) != new_val:
                changed.append(f)
            cls[f] = new_val
    if 'notes' in data:
        cls['notes'] = data['notes']
    if cls.get('routedToCounsel') and not cls.get('routedDate'):
        cls['routedDate'] = datetime.utcnow().strftime('%Y-%m-%d')
    rec['classification'] = cls

    if changed:
        _log_audit(rec, actor, f'Worker classification documentation updated: {", ".join(changed)}')
    else:
        _log_audit(rec, actor, 'Worker classification notes updated')
    _persist(rec, records, from_airtable)
    return jsonify({'success': True, 'record': rec})


@hr_onboarding.route('/nexus/hr/onboarding/<record_id>/agenda', methods=['PUT'])
def update_agenda(record_id):
    """30-Day Check-In Agenda — SOP Section 8. Generic by phase key (currently 'day30')."""
    data = request.get_json(force=True) or {}
    phase = data.get('phase', 'day30')
    idx = data.get('index')
    checked = data.get('checked')
    notes = data.get('notes')
    actor = (data.get('actor') or '').strip() or 'unspecified'

    if phase not in AGENDAS:
        return jsonify({'error': 'unknown agenda phase'}), 400

    rec, records, from_airtable = _find(record_id)
    if not rec:
        return jsonify({'error': 'not found'}), 404

    rec.setdefault('agenda', _default_agenda())
    rec['agenda'].setdefault(phase, {'items': [False] * len(AGENDAS[phase]), 'notes': ''})

    if idx is not None and checked is not None and 0 <= int(idx) < len(AGENDAS[phase]):
        idx = int(idx)
        rec['agenda'][phase]['items'][idx] = bool(checked)
        _log_audit(rec, actor, f'{phase} check-in agenda item {"covered" if checked else "uncovered"}: "{AGENDAS[phase][idx]}"')
    if notes is not None:
        rec['agenda'][phase]['notes'] = notes
        _log_audit(rec, actor, f'{phase} check-in agenda notes updated')

    _persist(rec, records, from_airtable)
    return jsonify({'success': True, 'record': rec})


@hr_onboarding.route('/nexus/hr/onboarding/<record_id>/member-facing', methods=['PUT'])
def update_member_facing(record_id):
    data = request.get_json(force=True) or {}
    member_facing = bool(data.get('memberFacing', True))
    actor = (data.get('actor') or '').strip() or 'unspecified'

    rec, records, from_airtable = _find(record_id)
    if not rec:
        return jsonify({'error': 'not found'}), 404

    old = rec.get('memberFacing', True)
    rec['memberFacing'] = member_facing
    if old != member_facing:
        _log_audit(rec, actor,
                   f'Member-facing designation changed: {old} -> {member_facing} '
                   f'(affects Recipient Rights / Abuse & Neglect annual recurrence)')
    _persist(rec, records, from_airtable)
    return jsonify({'success': True, 'record': rec})


@hr_onboarding.route('/nexus/hr/onboarding/<record_id>/status', methods=['PUT'])
def update_status(record_id):
    """Archive or reactivate. NEVER a hard delete — 10-year CMS FDR retention applies."""
    data = request.get_json(force=True) or {}
    new_status = data.get('status')
    actor = (data.get('actor') or '').strip() or 'unspecified'
    if new_status not in ('Active', 'Archived'):
        return jsonify({'error': 'status must be Active or Archived'}), 400

    rec, records, from_airtable = _find(record_id)
    if not rec:
        return jsonify({'error': 'not found'}), 404

    old_status = rec.get('status', 'Active')
    rec['status'] = new_status
    _log_audit(rec, actor, f'Status changed: {old_status} -> {new_status} (record retained — not deleted)')

    # Offboarding: redirect the alias instead of deleting it, so nothing
    # incoming gets lost — matches the "never hard delete" retention rule.
    company_email = rec.get('companyEmail', '')
    if new_status == 'Archived' and company_email:
        alias_map, err = get_alias_map()
        local_part = company_email.split('@')[0]
        alias_id = None
        if not err:
            # get_alias_map() doesn't carry ids — re-fetch raw list for the id.
            from improvmx_client import get_domain_aliases
            raw, err2 = get_domain_aliases()
            if not err2:
                match = next((a for a in raw if a.get('alias', '').lower() == local_part), None)
                alias_id = match.get('id') if match else None
        if alias_id:
            ok, result = update_alias(alias_id, OFFBOARD_ALIAS_FORWARD)
            if ok:
                _log_audit(rec, 'system', f'Offboarding: {company_email} redirected to {OFFBOARD_ALIAS_FORWARD} (not deleted)')
            else:
                _log_audit(rec, 'system', f'Offboarding alias redirect FAILED: {result} — {company_email} still forwards to old address, update manually')
        else:
            _log_audit(rec, 'system', f'Offboarding: could not locate {company_email} on ImprovMX to redirect — update manually if needed')
    elif new_status == 'Active' and old_status == 'Archived' and company_email:
        _log_audit(rec, 'system', f'Reactivated — {company_email} still points to {OFFBOARD_ALIAS_FORWARD}; update manually via /provision-email if it should forward to this person again')

    _persist(rec, records, from_airtable)
    return jsonify({'success': True, 'record': rec})


# ═══════════════════════════════════════════════════════════════
# COMPLIANCE GATE — mirrors PRISM's field-agent can-work check
# ═══════════════════════════════════════════════════════════════

def _can_work_internal(rec):
    """Shared logic behind the /can-work endpoint AND the company-email
    auto-provisioning trigger — 'credentialing complete' is defined as
    this gate passing. Returns (bool, reason_string)."""
    if rec.get('status') != 'Active':
        return False, f'Onboarding status is {rec.get("status")}, not Active'

    first_phase = phases_for(rec['workerType'])[0]
    first_phase_vals = rec.get('checklist', {}).get(first_phase['key'], [])
    if not first_phase_vals or not all(first_phase_vals):
        return False, f'"{first_phase["title"]}" not complete'

    screening = screening_compliance(rec)
    if screening['state'] in ('never_screened', 'flagged_open', 'overdue'):
        return False, screening['detail']

    for i, item in enumerate(TRAININGS):
        comp = training_compliance(rec, i, item)
        if comp['state'] == 'cms_hard_missed':
            return False, f'{item["name"]}: {comp["detail"]}'

    return True, 'Compliant'


def _maybe_provision_company_email(rec, actor='system'):
    """Fires on every credentialing-relevant mutation (checklist, training,
    screening). Idempotent no-op unless ALL of these are true:
      - not already provisioned (or explicitly declined)
      - role requires it (or HR override says yes) — see role_requires_company_email()
      - the can-work gate now passes (credentialing complete)
    Call this right before _persist()/_create() in any endpoint that could
    flip the can-work gate from False to True."""
    if rec.get('companyEmail'):
        return  # already provisioned — no-op
    if rec.get('companyEmailDeclined'):
        return  # HR explicitly said no for this hire — don't re-check every time

    override = rec.get('companyEmailOverride')  # True / False / None
    eligible = bool(override) if override is not None else role_requires_company_email(rec.get('role'))
    if not eligible:
        return

    ok, reason = _can_work_internal(rec)
    if not ok:
        return  # credentialing not complete yet — check again on the next mutation

    result = provision_employee_alias(rec['name'], rec.get('email', ''))
    if result['success']:
        rec['companyEmail'] = result['companyEmail']
        _log_audit(rec, 'system', f'Credentialing complete — company email provisioned: {result["companyEmail"]} -> forwards to {rec.get("email", "")}')
    else:
        rec['companyEmailError'] = result['error']
        _log_audit(rec, 'system', f'Credentialing complete but company email provisioning FAILED: {result["error"]} — retry via /provision-email')


@hr_onboarding.route('/nexus/hr/onboarding/<record_id>/can-work', methods=['GET'])
def can_work(record_id):
    rec, _, _ = _find(record_id)
    if not rec:
        return jsonify({'can_work': False, 'reason': 'not found'}), 404

    ok, reason = _can_work_internal(rec)
    return jsonify({'can_work': ok, 'reason': reason})


# ═══════════════════════════════════════════════════════════════
# ANNUAL FDR COMPLIANCE ATTESTATION — SOP Section 6
# ═══════════════════════════════════════════════════════════════

@hr_onboarding.route('/nexus/hr/attestation', methods=['GET'])
def list_attestations():
    records, from_source = _load_attestations()
    records.sort(key=lambda r: r.get('year') or 0, reverse=True)
    return jsonify({'attestations': records, 'source': 'airtable' if from_source else 'local'})


@hr_onboarding.route('/nexus/hr/attestation', methods=['POST'])
def upsert_attestation():
    data = request.get_json(force=True) or {}
    year = data.get('year')
    attestor_name = (data.get('attestorName') or '').strip()
    attested_date = data.get('attestedDate') or datetime.utcnow().strftime('%Y-%m-%d')
    reference_notes = data.get('referenceNotes', '')
    actor = (data.get('actor') or attestor_name or '').strip() or 'unspecified'

    if not year or not attestor_name:
        return jsonify({'error': 'year and attestorName are required'}), 400

    records, from_airtable = _load_attestations()
    existing = next((r for r in records if r.get('year') == year), None)
    rec = existing or {'year': year, 'created': datetime.utcnow().isoformat() + 'Z'}
    rec.update({
        'attested': True,
        'attestorName': attestor_name,
        'attestedDate': attested_date,
        'referenceNotes': reference_notes,
    })
    _persist_attestation(rec, records, from_airtable)
    return jsonify({'success': True, 'attestation': rec, 'actor': actor}), 201


# ═══════════════════════════════════════════════════════════════
# ROLE EMAIL POLICY — which roles get a @deedavis.biz alias
# ═══════════════════════════════════════════════════════════════
# Backed by the 'NEXUS HR ROLE EMAIL POLICY' Airtable table. These two
# endpoints let Dee/HR manage the policy from inside NEXUS/GATEWAY without
# ever opening Airtable directly — editing the Airtable table works too,
# both paths write/read the same table. See role_requires_company_email().

@hr_onboarding.route('/nexus/hr/role-email-policy', methods=['GET'])
def list_role_email_policy():
    rows = _load_role_email_policy(force=True)
    return jsonify({'policy': rows, 'count': len(rows)})


@hr_onboarding.route('/nexus/hr/role-email-policy', methods=['POST'])
def upsert_role_email_policy():
    data = request.get_json(force=True) or {}
    role = (data.get('role') or '').strip()
    requires = bool(data.get('requiresCompanyEmail', False))
    notes = (data.get('notes') or '').strip()
    actor = (data.get('actor') or '').strip() or 'unspecified'

    if not role:
        return jsonify({'error': 'role is required'}), 400

    table = _airtable_table(ROLE_POLICY_TABLE)
    if table is None:
        return jsonify({'error': 'NEXUS HR ROLE EMAIL POLICY table is unreachable — check Airtable config'}), 503

    try:
        existing = next((r for r in table.all() if (r.get('fields', {}).get('ROLE') or '').strip().lower() == role.lower()), None)
        fields = {'ROLE': role, 'REQUIRES_COMPANY_EMAIL': requires, 'NOTES': notes}
        if existing:
            table.update(existing['id'], fields, typecast=True)
        else:
            table.create(fields, typecast=True)
    except Exception as e:
        return jsonify({'error': f'failed to write policy: {e}'}), 502

    _load_role_email_policy(force=True)  # refresh cache immediately
    return jsonify({'success': True, 'role': role, 'requiresCompanyEmail': requires, 'actor': actor}), 201


# ═══════════════════════════════════════════════════════════════
# ACCOUNT CODES — which client/MCO contract a hire's personnel number
# encodes (e.g. CareSource -> CSRC, Molina -> MOLN)
# ═══════════════════════════════════════════════════════════════
# Backed by the 'NEXUS HR ACCOUNT CODES' Airtable table. Added per Dee:
# "how do i know that a customer care agent is working in the HAP account,
# or the MOLINA account" — the code is baked into the personnel number
# itself (see _next_personnel_number()). Dee/HR add a new account the
# moment a contract goes live — no code changes needed.

@hr_onboarding.route('/nexus/hr/account-codes', methods=['GET'])
def list_account_codes():
    rows = _load_account_codes(force=True)
    return jsonify({'accounts': rows, 'count': len(rows), 'fallbackCode': ACCOUNT_CODE_FALLBACK})


@hr_onboarding.route('/nexus/hr/account-codes', methods=['POST'])
def upsert_account_code():
    data = request.get_json(force=True) or {}
    name = (data.get('name') or '').strip()
    code = (data.get('code') or '').strip().upper()
    status = (data.get('status') or '').strip()
    notes = (data.get('notes') or '').strip()
    actor = (data.get('actor') or '').strip() or 'unspecified'

    if not name or not code:
        return jsonify({'error': 'name and code are both required'}), 400

    table = _airtable_table(ACCOUNT_CODES_TABLE)
    if table is None:
        return jsonify({'error': 'NEXUS HR ACCOUNT CODES table is unreachable — check Airtable config'}), 503

    try:
        existing = next((r for r in table.all() if (r.get('fields', {}).get('ACCOUNT_NAME') or '').strip().lower() == name.lower()), None)
        fields = {'ACCOUNT_NAME': name, 'ACCOUNT_CODE': code, 'STATUS': status, 'NOTES': notes}
        if existing:
            table.update(existing['id'], fields, typecast=True)
        else:
            table.create(fields, typecast=True)
    except Exception as e:
        return jsonify({'error': f'failed to write account code: {e}'}), 502

    _load_account_codes(force=True)  # refresh cache immediately
    return jsonify({'success': True, 'name': name, 'code': code, 'status': status, 'actor': actor}), 201


# ═══════════════════════════════════════════════════════════════
# LEVEL CODES — seniority/hierarchy tier a hire's personnel number
# encodes (e.g. Agent -> AGT, Manager -> MGR)
# ═══════════════════════════════════════════════════════════════
# Backed by the 'NEXUS HR LEVEL CODES' Airtable table. Added per Dee:
# "how do we know if they are a manager, supervisor etc" — the code is
# baked into the personnel number itself (see _next_personnel_number()).

@hr_onboarding.route('/nexus/hr/level-codes', methods=['GET'])
def list_level_codes():
    rows = _load_level_codes(force=True)
    return jsonify({'levels': rows, 'count': len(rows), 'fallbackCode': LEVEL_CODE_FALLBACK})


@hr_onboarding.route('/nexus/hr/level-codes', methods=['POST'])
def upsert_level_code():
    data = request.get_json(force=True) or {}
    name = (data.get('name') or '').strip()
    code = (data.get('code') or '').strip().upper()
    notes = (data.get('notes') or '').strip()
    actor = (data.get('actor') or '').strip() or 'unspecified'

    if not name or not code:
        return jsonify({'error': 'name and code are both required'}), 400

    table = _airtable_table(LEVEL_CODES_TABLE)
    if table is None:
        return jsonify({'error': 'NEXUS HR LEVEL CODES table is unreachable — check Airtable config'}), 503

    try:
        existing = next((r for r in table.all() if (r.get('fields', {}).get('LEVEL_NAME') or '').strip().lower() == name.lower()), None)
        fields = {'LEVEL_NAME': name, 'LEVEL_CODE': code, 'NOTES': notes}
        if existing:
            table.update(existing['id'], fields, typecast=True)
        else:
            table.create(fields, typecast=True)
    except Exception as e:
        return jsonify({'error': f'failed to write level code: {e}'}), 502

    _load_level_codes(force=True)  # refresh cache immediately
    return jsonify({'success': True, 'name': name, 'code': code, 'actor': actor}), 201


# ═══════════════════════════════════════════════════════════════
# ALERTS — for LandingPage feed + COMPASS FDR audit readiness
# ═══════════════════════════════════════════════════════════════

@hr_onboarding.route('/nexus/hr/onboarding/alerts', methods=['GET'])
def get_alerts():
    records, _ = _load_all()
    records = [r for r in records if r.get('status', 'Active') == 'Active']
    today = today_utc()

    cms_hard_missed, internal_target_missed, recurrence_due, pending_scoping = [], [], [], []
    screening_flagged, screening_never, screening_overdue = [], [], []

    for r in records:
        base = {'id': r['id'], 'name': r['name'], 'division': r.get('division', ''), 'workerType': r['workerType']}

        for i, item in enumerate(TRAININGS):
            comp = training_compliance(r, i, item, today)
            row = dict(base, training=item['name'], nextDue=comp['nextDue'], detail=comp['detail'])
            if comp['state'] == 'cms_hard_missed':
                cms_hard_missed.append(row)
            elif comp['state'] == 'internal_target_missed':
                internal_target_missed.append(row)
            elif comp['state'] == 'recurrence_due':
                recurrence_due.append(row)
            elif comp['state'] == 'pending_scoping':
                pending_scoping.append(row)

        screening = screening_compliance(r, today)
        row = dict(base, detail=screening['detail'], nextDue=screening['nextDue'])
        if screening['state'] == 'flagged_open':
            screening_flagged.append(row)
        elif screening['state'] == 'never_screened':
            screening_never.append(row)
        elif screening['state'] == 'overdue':
            screening_overdue.append(row)

    attestations, _ = _load_attestations()
    current_year = today.year
    current_year_attested = any(a.get('year') == current_year and a.get('attested') for a in attestations)

    alert_count = (len(cms_hard_missed) + len(internal_target_missed) + len(recurrence_due)
                   + len(screening_flagged) + len(screening_never) + len(screening_overdue)
                   + (0 if current_year_attested else 1))

    return jsonify({
        # Backward-compatible aliases used by earlier dashboard build
        'fwa_training_overdue': cms_hard_missed,
        'screening_stale': screening_overdue + screening_never,
        'flagged_screenings_open': screening_flagged,
        # Full detail
        'training_cms_hard_missed': cms_hard_missed,
        'training_internal_target_missed': internal_target_missed,
        'training_recurrence_due': recurrence_due,
        'training_pending_scoping': pending_scoping,
        'screening_flagged_open': screening_flagged,
        'screening_never': screening_never,
        'screening_overdue': screening_overdue,
        'fdr_attestation_current_year': current_year,
        'fdr_attestation_on_file': current_year_attested,
        'active_count': len(records),
        'alert_count': alert_count,
    })


# ═══════════════════════════════════════════════════════════════
# GATEWAY SELF-SERVICE PORTAL — gateway.deedavis.biz
# Looked up by EMAIL only. Never returns auditLog, exclusionLog detail
# beyond the computed screening summary, or classification.routedToCounsel
# notes — this is the new hire/contractor's own view, not the HR admin view.
# ═══════════════════════════════════════════════════════════════

import base64
import re as _re

DOCS_DIR = os.path.join(DATA_DIR, 'documents')
os.makedirs(DOCS_DIR, exist_ok=True)


def _safe_filename(name):
    name = os.path.basename(name or 'upload')
    name = _re.sub(r'[^A-Za-z0-9._-]', '_', name)
    return name[:120] or 'upload'


def _sanitized_self_record(rec):
    """The subset of a GATEWAY record that's safe to hand back to the
    new hire/contractor themselves over the portal."""
    doc_catalog = SELF_SERVICE_DOCUMENTS.get(rec['workerType'], [])
    ack_catalog = SELF_SERVICE_ACKNOWLEDGMENTS.get(rec['workerType'], [])
    uploaded_keys = {d.get('key') for d in rec.get('documents', [])}
    acked_keys = {a.get('key') for a in rec.get('acknowledgments', [])}

    return {
        'id': rec['id'],
        'name': rec['name'],
        'email': rec.get('email', ''),
        'role': rec.get('role', ''),
        'account': rec.get('account', ''),
        'level': rec.get('level', ''),
        'personnelNumber': rec.get('personnelNumber', ''),
        'companyEmail': rec.get('companyEmail', ''),
        'workerType': rec['workerType'],
        'division': rec.get('division', ''),
        'startdate': rec.get('startdate', ''),
        'status': rec.get('status', 'Active'),
        'progress': _progress(rec),
        'phases': [{
            'key': p['key'], 'title': p['title'], 'owner': p['owner'], 'items': p['items'],
            'checked': rec.get('checklist', {}).get(p['key'], [False] * len(p['items'])),
        } for p in phases_for(rec['workerType'])],
        'training': [{
            'name': TRAININGS[i]['name'],
            'recurrence_label': TRAININGS[i]['recurrence_label'],
            'status': (rec.get('training') or [{}])[i].get('status', 'Not Started') if i < len(rec.get('training') or []) else 'Not Started',
            **training_compliance(rec, i, item),
        } for i, item in enumerate(TRAININGS)],
        'screening': screening_compliance(rec),
        'documents': {
            'catalog': [dict(d, uploaded=(d['key'] in uploaded_keys)) for d in doc_catalog],
            'uploaded': rec.get('documents', []),
        },
        'acknowledgments': {
            'catalog': [dict(a, acknowledged=(a['key'] in acked_keys)) for a in ack_catalog],
            'signed': rec.get('acknowledgments', []),
        },
    }


@hr_onboarding.route('/nexus/hr/onboarding/self', methods=['GET'])
def get_self_record():
    email = request.args.get('email', '')
    rec, _, _ = _find_by_email(email)
    if not rec:
        return jsonify({'error': 'No active GATEWAY record found for that email. Ask HR to confirm your record.'}), 404
    return jsonify({'success': True, 'record': _sanitized_self_record(rec)})


@hr_onboarding.route('/nexus/hr/onboarding/self/documents', methods=['POST'])
def upload_self_document():
    data = request.get_json(force=True) or {}
    email = data.get('email', '')
    doc_key = (data.get('docType') or '').strip()
    filename = _safe_filename(data.get('filename'))
    content_b64 = data.get('contentBase64') or ''
    content_type = data.get('contentType') or 'application/octet-stream'

    rec, records, from_airtable = _find_by_email(email)
    if not rec:
        return jsonify({'error': 'No active GATEWAY record found for that email'}), 404

    catalog = SELF_SERVICE_DOCUMENTS.get(rec['workerType'], [])
    if doc_key not in {d['key'] for d in catalog}:
        return jsonify({'error': f'"{doc_key}" is not a required document for this worker type'}), 400
    if not content_b64:
        return jsonify({'error': 'contentBase64 is required'}), 400

    try:
        raw = base64.b64decode(content_b64)
    except Exception:
        return jsonify({'error': 'contentBase64 could not be decoded'}), 400

    if len(raw) > 8 * 1024 * 1024:
        return jsonify({'error': 'File too large — 8MB max. Call 855-773-0035 for help.'}), 400

    label = next((d['label'] for d in catalog if d['key'] == doc_key), doc_key)
    now = datetime.utcnow().isoformat() + 'Z'

    # Local disk copy — always, this is the durable record regardless of Airtable state.
    rec_dir = os.path.join(DOCS_DIR, rec['id'])
    os.makedirs(rec_dir, exist_ok=True)
    stored_name = f'{doc_key}__{filename}'
    with open(os.path.join(rec_dir, stored_name), 'wb') as f:
        f.write(raw)

    doc_entry = {
        'key': doc_key, 'label': label, 'filename': filename,
        'uploadedAt': now, 'sizeBytes': len(raw), 'localPath': stored_name, 'attachmentUrl': None,
    }

    # Best-effort push to Airtable's native attachment field so it shows up
    # on the record in NEXUS, not just on disk.
    if from_airtable and rec.get('airtable_id'):
        try:
            table = _airtable_table(HR_TABLE)
            if table is not None:
                result = table.upload_attachment(
                    rec['airtable_id'], DOCUMENTS_TABLE_FIELD, filename,
                    content=raw, content_type=content_type,
                )
                # Airtable's response keys the attachment list by FIELD ID, not
                # field name — find the list containing our just-uploaded filename.
                for field_val in (result.get('fields') or {}).values():
                    if isinstance(field_val, list) and field_val and isinstance(field_val[0], dict) and 'url' in field_val[0]:
                        match = next((a for a in field_val if a.get('filename') == filename), field_val[-1])
                        doc_entry['attachmentUrl'] = match.get('url')
                        break
        except Exception:
            pass  # local copy already saved — Airtable attachment is a bonus, not a blocker

    # Replace any prior upload for this same doc key (re-upload overwrites the record, not the disk file).
    docs = [d for d in rec.get('documents', []) if d.get('key') != doc_key]
    docs.append(doc_entry)
    rec['documents'] = docs
    _log_audit(rec, f'self-service ({rec.get("email", "")})', f'Document uploaded: {label} ({filename})')
    _persist(rec, records, from_airtable)

    return jsonify({'success': True, 'document': doc_entry})


@hr_onboarding.route('/nexus/hr/onboarding/self/acknowledge', methods=['POST'])
def acknowledge_self():
    """Typed-name + timestamp + IP acknowledgment — the e-signature
    equivalent for handbook/NDA/Code-of-Conduct items in the portal."""
    data = request.get_json(force=True) or {}
    email = data.get('email', '')
    ack_key = (data.get('itemKey') or '').strip()
    typed_name = (data.get('typedName') or '').strip()

    if not typed_name:
        return jsonify({'error': 'typedName is required to acknowledge'}), 400

    rec, records, from_airtable = _find_by_email(email)
    if not rec:
        return jsonify({'error': 'No active GATEWAY record found for that email'}), 404

    catalog = SELF_SERVICE_ACKNOWLEDGMENTS.get(rec['workerType'], [])
    label = next((a['label'] for a in catalog if a['key'] == ack_key), None)
    if not label:
        return jsonify({'error': f'"{ack_key}" is not a required acknowledgment for this worker type'}), 400

    now = datetime.utcnow().isoformat() + 'Z'
    entry = {
        'key': ack_key, 'label': label, 'typedName': typed_name,
        'ip': request.headers.get('X-Forwarded-For', request.remote_addr or ''),
        'ts': now,
    }
    acks = [a for a in rec.get('acknowledgments', []) if a.get('key') != ack_key]
    acks.append(entry)
    rec['acknowledgments'] = acks
    _log_audit(rec, f'self-service ({rec.get("email", "")})',
               f'Acknowledged/e-signed: "{label}" (typed name: {typed_name})')
    _persist(rec, records, from_airtable)

    return jsonify({'success': True, 'acknowledgment': entry})


def create_hr_onboarding_routes(app):
    """Optional explicit registration helper (mirrors haven_partner_onboarding.py style)."""
    app.register_blueprint(hr_onboarding)
