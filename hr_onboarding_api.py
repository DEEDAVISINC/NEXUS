#!/usr/bin/env python3
"""
NEXUS HR Onboarding API
========================
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
  PUT    /nexus/hr/onboarding/<id>/classification         — worker-classification documentation (contractor)
  PUT    /nexus/hr/onboarding/<id>/agenda                 — 30-day check-in agenda toggle/notes
  PUT    /nexus/hr/onboarding/<id>/member-facing          — toggle member-facing designation
  PUT    /nexus/hr/onboarding/<id>/status                 — archive / reactivate (soft only)
  GET    /nexus/hr/onboarding/<id>/can-work                — compliance gate check
  GET    /nexus/hr/onboarding/alerts                      — overdue training / stale screenings / attestation
  GET    /nexus/hr/attestation                            — list annual FDR attestations
  POST   /nexus/hr/attestation                            — record/update an annual FDR attestation
"""

import os
import json
import uuid
import calendar
from datetime import datetime, date, timedelta
from flask import Blueprint, request, jsonify

hr_onboarding = Blueprint('hr_onboarding', __name__)

# ─── Storage config ──────────────────────────────────────────────
HR_TABLE = 'NEXUS HR ONBOARDING'
ATTEST_TABLE = 'NEXUS HR FDR ATTESTATION'
DATA_DIR = os.path.join(os.path.dirname(__file__), 'uploads', 'hr_onboarding')
LOCAL_FILE = os.path.join(DATA_DIR, 'roster.json')
ATTEST_LOCAL_FILE = os.path.join(DATA_DIR, 'fdr_attestation.json')
os.makedirs(DATA_DIR, exist_ok=True)


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


def _new_record(name, worker_type, division, startdate, member_facing=True):
    worker_type = worker_type if worker_type in ('employee', 'contractor') else 'employee'
    phases = phases_for(worker_type)
    checklist = {p['key']: [False] * len(p['items']) for p in phases}
    now = datetime.utcnow().isoformat() + 'Z'
    return {
        'id': 'HR-' + uuid.uuid4().hex[:8].upper(),
        'name': name,
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
    rec = _new_record(name, data.get('workerType'), data.get('division'), data.get('startdate'), member_facing)
    actor = (data.get('actor') or '').strip() or 'unspecified'
    _log_audit(rec, actor, f'Record created by {actor}')
    _create(rec)
    return jsonify({'success': True, 'record': rec}), 201


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
    _persist(rec, records, from_airtable)
    return jsonify({'success': True, 'record': rec})


# ═══════════════════════════════════════════════════════════════
# COMPLIANCE GATE — mirrors PRISM's field-agent can-work check
# ═══════════════════════════════════════════════════════════════

@hr_onboarding.route('/nexus/hr/onboarding/<record_id>/can-work', methods=['GET'])
def can_work(record_id):
    rec, _, _ = _find(record_id)
    if not rec:
        return jsonify({'can_work': False, 'reason': 'not found'}), 404

    if rec.get('status') != 'Active':
        return jsonify({'can_work': False, 'reason': f'Onboarding status is {rec.get("status")}, not Active'})

    first_phase = phases_for(rec['workerType'])[0]
    first_phase_vals = rec.get('checklist', {}).get(first_phase['key'], [])
    if not first_phase_vals or not all(first_phase_vals):
        return jsonify({'can_work': False, 'reason': f'"{first_phase["title"]}" not complete'})

    screening = screening_compliance(rec)
    if screening['state'] in ('never_screened', 'flagged_open', 'overdue'):
        return jsonify({'can_work': False, 'reason': screening['detail']})

    for i, item in enumerate(TRAININGS):
        comp = training_compliance(rec, i, item)
        if comp['state'] == 'cms_hard_missed':
            return jsonify({'can_work': False, 'reason': f'{item["name"]}: {comp["detail"]}'})

    return jsonify({'can_work': True, 'reason': 'Compliant'})


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


def create_hr_onboarding_routes(app):
    """Optional explicit registration helper (mirrors haven_partner_onboarding.py style)."""
    app.register_blueprint(hr_onboarding)
