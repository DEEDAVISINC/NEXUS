#!/usr/bin/env python3
"""
NEXUS HR Onboarding API
========================
Handles internal DDI personnel onboarding — W-2 Employees and 1099
Independent Contractors engaged directly by Dee Davis Inc. across all
divisions (DEPOINTE, HAVEN, SHIELD, VITAL, ARENA/PRIME, 3D Ink/CNTDA,
Freight 1st Direct, DEPOINTE DNA, Corporate/HR/Admin).

This is DISTINCT from:
  - GPSS SUPPLIERS / GPSS SUBCONTRACTORS  → external vendors & project subs
  - PRISM FIELD AGENTS                    → mobile field service dispatch
  (Both governed by NEXUS_ONBOARDING_SYSTEM.md's 3-person-type pipeline.)

This HR track exists because internal employees/contractors need a
different compliance spine: Form I-9 / E-Verify, OIG LEIE + GSA SAM.gov
exclusion screening (at hire + monthly), and CMS FDR training
(First Tier, Downstream, and Related entity — 42 CFR 422.504(d)) that
applies because DDI performs work under MCO/Medicaid contracts
(CareSource, HIDE SNP, etc. — see CLIENT OUTREACH/MICHIGAN MICH HIDE SNP/).

Storage: Airtable (table 'NEXUS HR ONBOARDING') is primary, matching
every other NEXUS system ("Airtable — the data backbone"). Falls back
to a local JSON file automatically if Airtable isn't configured or the
table doesn't exist yet, so this works day one without blocking on
Airtable setup — same fallback pattern used in prism_compliance_api.py.

RETENTION RULE: Records are never hard-deleted. "Remove" from the
roster = archive (STATUS -> Archived). The audit log is append-only.
This matches the tracker's own stated 10-year CMS FDR retention
requirement — a hard-delete "Remove" button would have violated it.

Endpoints:
  GET    /nexus/hr/onboarding/config                 — phases/trainings/divisions config
  GET    /nexus/hr/onboarding                        — roster (list)
  POST   /nexus/hr/onboarding                        — add new hire
  GET    /nexus/hr/onboarding/<record_id>            — single record detail
  PUT    /nexus/hr/onboarding/<record_id>/checklist   — toggle a checklist item
  PUT    /nexus/hr/onboarding/<record_id>/training    — update a training row
  POST   /nexus/hr/onboarding/<record_id>/screening   — log exclusion screening entry
  PUT    /nexus/hr/onboarding/<record_id>/status      — archive / reactivate (soft only)
  GET    /nexus/hr/onboarding/<record_id>/can-work    — compliance gate check
  GET    /nexus/hr/onboarding/alerts                  — overdue training / stale screenings
"""

import os
import json
import uuid
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify

hr_onboarding = Blueprint('hr_onboarding', __name__)

# ─── Storage config ──────────────────────────────────────────────
HR_TABLE = 'NEXUS HR ONBOARDING'
DATA_DIR = os.path.join(os.path.dirname(__file__), 'uploads', 'hr_onboarding')
LOCAL_FILE = os.path.join(DATA_DIR, 'roster.json')
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


def _airtable_table():
    api, base_id = get_airtable()
    if not api or not base_id:
        return None
    try:
        table = api.table(base_id, HR_TABLE)
        table.all(max_records=1)  # cheap probe — raises if table doesn't exist
        return table
    except Exception:
        return None


# ─── Config: phases + trainings (single source of truth, server-side) ──

PHASES_EMPLOYEE = [
    {'key': 'preboard', 'title': 'Phase 1 — Pre-Boarding', 'owner': 'HR', 'items': [
        'Offer letter signed and returned',
        'Background check initiated',
        'E-Verify case created',
        'OIG LEIE exclusion list screening completed (at hire)',
        'GSA SAM.gov exclusion/debarment screening completed (at hire)',
        'IT ticket submitted (email, NEXUS, PRISM if applicable, hardware)',
        'Division/manager assigned',
        'Start date and date of hire confirmed in writing',
    ]},
    {'key': 'day1', 'title': 'Phase 2 — Day One', 'owner': 'HR + Manager', 'items': [
        'I-9 completed in person (Section 1 + Section 2)',
        'Signed acknowledgments: Handbook, Code of Conduct/COI, NDA',
        'NEXUS account provisioned and tested',
        'Introduction to manager, division team, and "What are we not seeing?" principle',
        'Training assignment email sent',
    ]},
    {'key': 'week1', 'title': 'Phase 3 — Week One', 'owner': 'Manager', 'items': [
        'Division-specific systems walkthrough (PRISM / relevant NEXUS modules)',
        '"Coordinate, not provide" positioning review',
        'Shadow a live CS interaction or workflow',
        'Training progress check-in',
    ]},
    {'key': 'day30', 'title': 'Phase 4 — First 30 Days', 'owner': 'HR + Manager', 'items': [
        'All required trainings completed',
        'Role-specific competency check-in',
        '30-day check-in meeting held',
    ]},
    {'key': 'day6090', 'title': 'Phase 5 — 60/90-Day Check-Ins', 'owner': 'Manager', 'items': [
        '60-day: workload calibration, open questions addressed',
        '90-day: performance review, compliance training current, E-Verify/I-9 file complete',
    ]},
]

PHASES_CONTRACTOR = [
    {'key': 'preengage', 'title': 'Phase 1 — Pre-Engagement', 'owner': 'HR/Contracts', 'items': [
        'Independent Contractor Agreement / MSA signed and executed',
        'W-9 collected (not I-9 — E-Verify/I-9 do not apply to contractors)',
        'OIG LEIE exclusion list screening completed',
        'GSA SAM.gov exclusion/debarment screening completed',
        'Business Associate Agreement (BAA) executed, if PHI access required',
        'Certificate of insurance / liability coverage on file, if required',
        'Scope of work / deliverables defined in writing',
        'Worker-classification basis documented and retained in contractor file',
    ]},
    {'key': 'engagestart', 'title': 'Phase 2 — Engagement Start', 'owner': 'HR/Contracts', 'items': [
        'Signed Confidentiality/NDA and Code of Conduct acknowledgment (contractual flow-down)',
        'System access provisioned at minimum necessary scope for the engagement',
        '"Coordinate, not provide" and confidentiality briefing',
        'Required compliance training assigned',
    ]},
    {'key': 'ongoing', 'title': 'Phase 3 — Ongoing', 'owner': 'Engagement Manager', 'items': [
        'Training and exclusion screening verified current before any MCO-facing task',
        'Deliverable/milestone check-ins per contract terms (not calendar-based performance review)',
        'Contract renewal, extension, or termination determination per contract terms',
    ]},
]

TRAININGS = [
    {'name': 'Identifying and Safeguarding PII', 'recurring': False},
    {'name': 'HIPAA Training (Course For HIPAA)', 'recurring': False},
    {'name': 'Medicare/Medicaid General Compliance (FWA)', 'recurring': True},
    {'name': 'Medicare Fraud & Abuse', 'recurring': True},
    {'name': 'Cultural Competence/Diversity', 'recurring': False},
    {'name': 'Recipient Rights', 'recurring': False},
    {'name': 'Abuse & Neglect: Reporting Requirements', 'recurring': False},
    {'name': 'Anti-Harassment & Non-Discrimination', 'recurring': False},
    {'name': 'Code of Conduct / COI Attestation', 'recurring': True},
    {'name': 'E-Verify / Form I-9 Basics', 'recurring': False},
]

DIVISIONS = [
    'DEPOINTE (NEMT Coordination)', 'HAVEN', 'SHIELD', 'VITAL', 'ARENA/PRIME',
    '3D Ink Signatures/CNTDA', 'Freight 1st Direct', 'DEPOINTE DNA', 'Corporate/HR/Admin',
]

FWA_TRAINING_NAME = 'Medicare/Medicaid General Compliance (FWA)'
FWA_DEADLINE_DAYS = 90
SCREENING_STALE_DAYS = 30


def phases_for(worker_type):
    return PHASES_CONTRACTOR if worker_type == 'contractor' else PHASES_EMPLOYEE


def _new_record(name, worker_type, division, startdate):
    worker_type = worker_type if worker_type in ('employee', 'contractor') else 'employee'
    phases = phases_for(worker_type)
    checklist = {p['key']: [False] * len(p['items']) for p in phases}
    training = [{'status': 'Not Started', 'due': '', 'certRef': '', 'completedBy': '', 'completedDate': ''}
                for _ in TRAININGS]
    now = datetime.utcnow().isoformat() + 'Z'
    return {
        'id': 'HR-' + uuid.uuid4().hex[:8].upper(),
        'name': name,
        'workerType': worker_type,
        'division': division or '',
        'startdate': startdate or '',
        'status': 'Active',
        'checklist': checklist,
        'training': training,
        'exclusionLog': [],
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


# ─── Local JSON fallback ─────────────────────────────────────────

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


# ─── Airtable <-> record serialization ───────────────────────────

def _record_to_fields(rec):
    return {
        'RECORD_ID': rec['id'],
        'NAME': rec['name'],
        'WORKER_TYPE': 'Contractor (1099)' if rec['workerType'] == 'contractor' else 'Employee (W-2)',
        'DIVISION': rec.get('division', ''),
        'START_DATE': rec.get('startdate') or None,
        'STATUS': rec.get('status', 'Active'),
        'CHECKLIST_JSON': json.dumps(rec.get('checklist', {})),
        'TRAINING_JSON': json.dumps(rec.get('training', [])),
        'EXCLUSION_LOG_JSON': json.dumps(rec.get('exclusionLog', [])),
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
        'checklist': _jload('CHECKLIST_JSON', {}),
        'training': _jload('TRAINING_JSON', []),
        'exclusionLog': _jload('EXCLUSION_LOG_JSON', []),
        'auditLog': _jload('AUDIT_LOG_JSON', []),
        'created': airtable_record.get('createdTime', ''),
        'airtable_id': airtable_record.get('id'),
    }


# ─── Unified data access (Airtable primary, local fallback) ─────

def _load_all():
    table = _airtable_table()
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
    """Save one record back to whichever store it came from."""
    if from_airtable:
        table = _airtable_table()
        if table is not None:
            try:
                if rec.get('airtable_id'):
                    table.update(rec['airtable_id'], _record_to_fields(rec))
                else:
                    created = table.create(_record_to_fields(rec))
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
    table = _airtable_table()
    if table is not None:
        try:
            created = table.create(_record_to_fields(rec))
            rec['airtable_id'] = created.get('id')
            return
        except Exception:
            pass
    local = _load_local()
    local.append(rec)
    _save_local(local)


# ═══════════════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════════════

@hr_onboarding.route('/nexus/hr/onboarding/config', methods=['GET'])
def get_config():
    return jsonify({
        'phases_employee': PHASES_EMPLOYEE,
        'phases_contractor': PHASES_CONTRACTOR,
        'trainings': TRAININGS,
        'divisions': DIVISIONS,
        'fwa_training_name': FWA_TRAINING_NAME,
        'fwa_deadline_days': FWA_DEADLINE_DAYS,
        'screening_stale_days': SCREENING_STALE_DAYS,
    })


# ═══════════════════════════════════════════════════════════════
# ROSTER — LIST / CREATE
# ═══════════════════════════════════════════════════════════════

def _progress(rec):
    total = 0
    done = 0
    for p in phases_for(rec['workerType']):
        vals = rec.get('checklist', {}).get(p['key'], [])
        total += len(p['items'])
        done += sum(1 for v in vals if v)
    for t in rec.get('training', []):
        total += 1
        if t.get('status') == 'Complete':
            done += 1
    return round((done / total) * 100) if total else 0


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
        'progress': _progress(r),
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
    rec = _new_record(name, data.get('workerType'), data.get('division'), data.get('startdate'))
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
    allowed_fields = {'status', 'due', 'certRef', 'completedBy'}

    if field not in allowed_fields or idx is None or not (0 <= int(idx) < len(TRAININGS)):
        return jsonify({'error': 'invalid field/index'}), 400

    rec, records, from_airtable = _find(record_id)
    if not rec:
        return jsonify({'error': 'not found'}), 404

    idx = int(idx)
    while len(rec['training']) <= idx:
        rec['training'].append({'status': 'Not Started', 'due': '', 'certRef': '', 'completedBy': '', 'completedDate': ''})

    old_value = rec['training'][idx].get(field, '')
    rec['training'][idx][field] = value
    if field == 'status' and value == 'Complete' and not rec['training'][idx].get('completedDate'):
        rec['training'][idx]['completedDate'] = datetime.utcnow().strftime('%Y-%m-%d')

    training_name = TRAININGS[idx]['name']
    _log_audit(rec, actor, f'Training "{training_name}" {field} changed: {old_value or "(blank)"} -> {value or "(blank)"}')
    _persist(rec, records, from_airtable)
    rec['_progress'] = _progress(rec)
    return jsonify({'success': True, 'record': rec})


@hr_onboarding.route('/nexus/hr/onboarding/<record_id>/screening', methods=['POST'])
def log_screening(record_id):
    data = request.get_json(force=True) or {}
    date = data.get('date')
    result = data.get('result') or 'Clear'
    notes = (data.get('notes') or '').strip()
    actor = (data.get('actor') or '').strip() or 'unspecified'
    if not date:
        return jsonify({'error': 'date is required'}), 400

    rec, records, from_airtable = _find(record_id)
    if not rec:
        return jsonify({'error': 'not found'}), 404

    entry = {'date': date, 'result': result, 'notes': notes, 'loggedBy': actor,
              'ts': datetime.utcnow().isoformat() + 'Z'}
    rec.setdefault('exclusionLog', []).append(entry)
    flagged = str(result).startswith('Flagged')
    _log_audit(rec, actor,
               f'Exclusion screening logged: {date}, result: {result}' + (f', notes: {notes}' if notes else ''))
    if flagged:
        _log_audit(rec, 'system', f'⚠️ FLAGGED SCREENING — escalate to Compliance immediately ({date})')
    _persist(rec, records, from_airtable)
    return jsonify({'success': True, 'record': rec, 'flagged': flagged})


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
        return jsonify({'can_work': False,
                         'reason': f'"{first_phase["title"]}" not complete'})

    open_flag = any(str(e.get('result', '')).startswith('Flagged') for e in rec.get('exclusionLog', []))
    if open_flag:
        return jsonify({'can_work': False, 'reason': 'Open flagged exclusion screening — escalate to Compliance'})

    if not rec.get('exclusionLog'):
        return jsonify({'can_work': False, 'reason': 'No exclusion screening on file (OIG LEIE / GSA SAM.gov required)'})

    return jsonify({'can_work': True, 'reason': 'Compliant'})


# ═══════════════════════════════════════════════════════════════
# ALERTS — for LandingPage feed + COMPASS FDR audit readiness
# ═══════════════════════════════════════════════════════════════

@hr_onboarding.route('/nexus/hr/onboarding/alerts', methods=['GET'])
def get_alerts():
    records, _ = _load_all()
    records = [r for r in records if r.get('status', 'Active') == 'Active']
    today = datetime.utcnow().date()
    fwa_overdue, screening_stale, flagged_open = [], [], []

    for r in records:
        # FWA training deadline: 90 days from start date, then annual (recurring flagged same way
        # once due date passes — 'due' field drives recurring cadence once initially completed).
        try:
            start = datetime.strptime(r.get('startdate', ''), '%Y-%m-%d').date() if r.get('startdate') else None
        except ValueError:
            start = None
        fwa_idx = next((i for i, t in enumerate(TRAININGS) if t['name'] == FWA_TRAINING_NAME), None)
        if fwa_idx is not None and start:
            fwa = (r.get('training') or [{}] * len(TRAININGS))[fwa_idx] if len(r.get('training', [])) > fwa_idx else {}
            deadline = start + timedelta(days=FWA_DEADLINE_DAYS)
            if fwa.get('status') != 'Complete' and today > deadline:
                fwa_overdue.append({'id': r['id'], 'name': r['name'], 'division': r.get('division', ''),
                                     'deadline': deadline.isoformat()})

        # Screening staleness
        log = r.get('exclusionLog', [])
        if not log:
            if start and today > start + timedelta(days=SCREENING_STALE_DAYS):
                screening_stale.append({'id': r['id'], 'name': r['name'], 'last_screened': None})
        else:
            last = max((e.get('date', '') for e in log if e.get('date')), default='')
            if last:
                try:
                    last_date = datetime.strptime(last, '%Y-%m-%d').date()
                    if today > last_date + timedelta(days=SCREENING_STALE_DAYS):
                        screening_stale.append({'id': r['id'], 'name': r['name'], 'last_screened': last})
                except ValueError:
                    pass
        if any(str(e.get('result', '')).startswith('Flagged') for e in log):
            flagged_open.append({'id': r['id'], 'name': r['name']})

    return jsonify({
        'fwa_training_overdue': fwa_overdue,
        'screening_stale': screening_stale,
        'flagged_screenings_open': flagged_open,
        'active_count': len(records),
        'alert_count': len(fwa_overdue) + len(screening_stale) + len(flagged_open),
    })


def create_hr_onboarding_routes(app):
    """Optional explicit registration helper (mirrors haven_partner_onboarding.py style)."""
    app.register_blueprint(hr_onboarding)
