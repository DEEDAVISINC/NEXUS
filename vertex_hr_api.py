"""
VERTEX HR — workforce pay module (hours, rates, pay calculations).

GATEWAY is identity + clearance. VERTEX HR is compensation + payroll math.
Join key: personnelNumberCore (never invent a second employee ID).

See VERTEX_HR_MASTER.md.
"""
from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timedelta
from typing import Optional

from flask import Blueprint, jsonify, request

vertex_hr = Blueprint('vertex_hr', __name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'uploads', 'vertex_hr')
EMPLOYEES_FILE = os.path.join(DATA_DIR, 'employees.json')
TIMESHEETS_FILE = os.path.join(DATA_DIR, 'timesheets.json')
PAY_RUNS_FILE = os.path.join(DATA_DIR, 'pay_runs.json')

# Rough tax estimate defaults (Phase 1 — tighten with IRS/MI tables later)
# Pay rail: Deluxe eChecks. Tax rail: EFTPS.gov + Michigan / UIA.
FICA_RATE = 0.062
MEDICARE_RATE = 0.0145
FED_WITHHOLD_EST = 0.12
STATE_WITHHOLD_EST = 0.0425  # MI income tax estimate only
FUTA_RATE_EST = 0.006  # employer FUTA estimate (credit-reduced effective rate varies)
OT_MULTIPLIER = 1.5
STD_WEEKLY_HOURS = 40.0
BIWEEKLY_PERIODS_PER_YEAR = 26
TAX_DEPOSITS_FILE = os.path.join(DATA_DIR, 'tax_deposits.json')
COMPANY_FILE = os.path.join(DATA_DIR, 'company_settings.json')

# Biweekly anchor — periods are 14-day blocks from this Monday (adjust in company settings)
DEFAULT_PERIOD_ANCHOR = '2026-01-05'  # Monday


def _now() -> str:
    return datetime.now().isoformat()


def _ensure_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


def _load(path: str) -> list:
    _ensure_dir()
    if not os.path.exists(path):
        return []
    try:
        with open(path, 'r') as fp:
            data = json.load(fp)
            return data if isinstance(data, list) else []
    except Exception:
        return []


def _save(path: str, rows: list) -> None:
    _ensure_dir()
    with open(path, 'w') as fp:
        json.dump(rows, fp, indent=2)


def _load_obj(path: str) -> dict:
    _ensure_dir()
    if not os.path.exists(path):
        return {}
    try:
        with open(path, 'r') as fp:
            data = json.load(fp)
            return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _save_obj(path: str, obj: dict) -> None:
    _ensure_dir()
    with open(path, 'w') as fp:
        json.dump(obj, fp, indent=2)


def _default_company() -> dict:
    return {
        'legalName': 'Dee Davis Inc.',
        'ein': '',
        'michiganAccountId': '',
        'miUiaEmployerNumber': '',
        'miUiaRatePercent': None,  # e.g. 2.7 meaning 2.7%
        'federalDepositSchedule': 'monthly',  # monthly | semiweekly
        'defaultPayFrequency': 'biweekly',
        'periodAnchor': DEFAULT_PERIOD_ANCHOR,
        'payRail': 'Deluxe eChecks',
        'taxRails': ['EFTPS.gov', 'Michigan Treasury', 'Michigan UIA'],
        'address': '755 W. Big Beaver Rd., Suite 2020, Troy, Michigan 48084',
        'updatedAt': None,
        'updatedBy': None,
    }


def _get_company() -> dict:
    stored = _load_obj(COMPANY_FILE)
    base = _default_company()
    base.update(stored or {})
    return base


def _biweekly_period_for(day=None) -> dict:
    """Return periodStart/periodEnd for the biweekly block containing day."""
    company = _get_company()
    anchor_s = (company.get('periodAnchor') or DEFAULT_PERIOD_ANCHOR)[:10]
    try:
        anchor = datetime.strptime(anchor_s, '%Y-%m-%d').date()
    except ValueError:
        anchor = datetime.strptime(DEFAULT_PERIOD_ANCHOR, '%Y-%m-%d').date()
    day = day or datetime.now().date()
    if hasattr(day, 'date'):
        day = day.date()
    delta = (day - anchor).days
    # floor to period
    idx = delta // 14 if delta >= 0 else -((-delta - 1) // 14 + 1)
    start = anchor + timedelta(days=idx * 14)
    end = start + timedelta(days=13)
    return {
        'periodStart': start.isoformat(),
        'periodEnd': end.isoformat(),
        'payFrequency': 'biweekly',
        'label': f'{start.isoformat()} → {end.isoformat()}',
    }


def _capabilities() -> dict:
    return {
        'identity': 'GATEWAY sync (personnelNumberCore join key)',
        'roster': True,
        'rates': True,
        'timesheets': True,
        'approveRejectHours': True,
        'payCalc': True,
        'payRuns': True,
        'deluxeEcheckRegister': True,
        'markDeluxePaid': True,
        'taxLiabilityEftps': True,
        'taxLiabilityMichigan': True,
        'taxDepositLog': True,
        'companyTaxSettings': True,
        'employeeTaxProfile': True,
        'payStubs': True,
        'dashboard': True,
        'periodHelper': True,
        'notIncludedYet': [
            'Exact IRS Pub 15 wage-bracket withholding tables',
            'W-2/1099 PDF year-end package',
            'Auto-push OPS punches without Send to VERTEX button',
        ],
        'commandCenterUi': 'VERTEX → HR Payroll tab (VERTEXHRPanel)',
        'opsTimeclockFeed': 'POST /ops/timeclock/send-to-vertex → draft timesheet',
    }


def _gateway_records() -> list:
    from hr_onboarding_api import _load_all
    records, _ = _load_all()
    return records or []


def _can_work(rec: dict):
    from hr_onboarding_api import _can_work_internal
    return _can_work_internal(rec)


def _profile_from_gateway(rec: dict) -> dict:
    ok, reason = _can_work(rec)
    core = (rec.get('personnelNumberCore') or '').strip()
    return {
        'personnelNumberCore': core,
        'personnelNumber': rec.get('personnelNumber') or '',
        'gatewayId': rec.get('id'),
        'name': rec.get('name') or '',
        'email': (rec.get('email') or '').strip().lower(),
        'companyEmail': rec.get('companyEmail') or '',
        'workerType': rec.get('workerType') or 'employee',  # employee | contractor
        'employeeTypeLabel': (
            '1099 Contractor' if rec.get('workerType') == 'contractor' else 'W-2 Employee'
        ),
        'division': rec.get('division') or '',
        'account': rec.get('account') or '',
        'level': rec.get('level') or '',
        'status': rec.get('status') or '',
        'canWork': bool(ok),
        'canWorkReason': reason,
        'payable': bool(ok) and (rec.get('status') or '') == 'Active',
        'syncedAt': _now(),
    }


_VERTEX_OWNED_FIELDS = (
    'payType', 'hourlyRate', 'salaryAnnual', 'contractorRate',
    'payFrequency', 'otherDeductions', 'deductionNotes',
    'rateHistory', 'ytdGross', 'ytdNet', 'ytdFederalTax', 'ytdStateTax',
    'ytdFica', 'ytdMedicare',
    'ssnLast4', 'filingStatus', 'federalWithholdPct', 'stateWithholdPct',
    'stateWorked', 'w4Notes', 'deluxePayeeEmail', 'deluxePayeeName',
)


def _merge_employee(existing: Optional[dict], profile: dict) -> dict:
    """Preserve VERTEX-owned compensation + tax fields across sync."""
    base = dict(existing or {})
    base.update(profile)
    base.setdefault('payType', 'hourly')  # hourly | salary | contractor | owner_draw
    base.setdefault('hourlyRate', 0.0)
    base.setdefault('salaryAnnual', 0.0)
    base.setdefault('contractorRate', 0.0)
    base.setdefault('payFrequency', 'biweekly')
    base.setdefault('otherDeductions', 0.0)
    base.setdefault('deductionNotes', '')
    base.setdefault('rateHistory', [])
    base.setdefault('ytdGross', 0.0)
    base.setdefault('ytdNet', 0.0)
    base.setdefault('ytdFederalTax', 0.0)
    base.setdefault('ytdStateTax', 0.0)
    base.setdefault('ytdFica', 0.0)
    base.setdefault('ytdMedicare', 0.0)
    base.setdefault('ssnLast4', '')
    base.setdefault('filingStatus', 'single')
    base.setdefault('federalWithholdPct', None)  # override estimate % if set
    base.setdefault('stateWithholdPct', None)
    base.setdefault('stateWorked', 'MI')
    base.setdefault('w4Notes', '')
    base.setdefault('deluxePayeeEmail', base.get('email') or '')
    base.setdefault('deluxePayeeName', base.get('name') or '')
    if existing:
        for k in _VERTEX_OWNED_FIELDS:
            if k in existing:
                base[k] = existing[k]
    return base


def _find_employee(core: str) -> Optional[dict]:
    core = (core or '').strip()
    for e in _load(EMPLOYEES_FILE):
        if (e.get('personnelNumberCore') or '') == core:
            return e
    return None


def _refresh_payable_from_gateway(emp: dict) -> dict:
    """Re-check GATEWAY can-work before paying."""
    from hr_onboarding_api import _find_by_email

    email = (emp.get('email') or '').strip().lower()
    if not email:
        emp['payable'] = False
        emp['canWorkReason'] = 'No email on VERTEX profile'
        return emp
    rec, _, _ = _find_by_email(email)
    if not rec:
        emp['payable'] = False
        emp['canWork'] = False
        emp['canWorkReason'] = 'No GATEWAY record'
        return emp
    ok, reason = _can_work(rec)
    emp['canWork'] = bool(ok)
    emp['canWorkReason'] = reason
    emp['status'] = rec.get('status') or emp.get('status')
    emp['payable'] = bool(ok) and (rec.get('status') or '') == 'Active'
    emp['personnelNumber'] = rec.get('personnelNumber') or emp.get('personnelNumber')
    emp['level'] = rec.get('level') or emp.get('level')
    emp['account'] = rec.get('account') or emp.get('account')
    emp['division'] = rec.get('division') or emp.get('division')
    return emp


def _period_bounds(start: str, end: str):
    try:
        d0 = datetime.strptime(start[:10], '%Y-%m-%d').date()
        d1 = datetime.strptime(end[:10], '%Y-%m-%d').date()
    except ValueError:
        return None, None
    if d1 < d0:
        return None, None
    return d0, d1


def _calc_gross(emp: dict, regular_hours: float, ot_hours: float) -> dict:
    pay_type = (emp.get('payType') or 'hourly').lower()
    worker = emp.get('workerType') or 'employee'
    regular_hours = max(0.0, float(regular_hours or 0))
    ot_hours = max(0.0, float(ot_hours or 0))

    if pay_type == 'salary':
        annual = float(emp.get('salaryAnnual') or 0)
        freq = (emp.get('payFrequency') or 'biweekly').lower()
        periods = BIWEEKLY_PERIODS_PER_YEAR if freq == 'biweekly' else (24 if freq == 'semimonthly' else 12)
        gross = round(annual / periods, 2) if annual else 0.0
        return {
            'gross': gross,
            'regularPay': gross,
            'otPay': 0.0,
            'regularHours': regular_hours,
            'otHours': ot_hours,
            'method': f'salary/{freq}',
        }

    rate = float(emp.get('contractorRate') or emp.get('hourlyRate') or 0)
    if pay_type == 'contractor' or worker == 'contractor':
        rate = float(emp.get('contractorRate') or emp.get('hourlyRate') or 0)
    elif pay_type == 'owner_draw':
        # Owner draw: treat as flat salary-like amount stored in salaryAnnual per period
        annual = float(emp.get('salaryAnnual') or 0)
        gross = round(annual / BIWEEKLY_PERIODS_PER_YEAR, 2) if annual else round(rate, 2)
        return {
            'gross': gross,
            'regularPay': gross,
            'otPay': 0.0,
            'regularHours': regular_hours,
            'otHours': 0.0,
            'method': 'owner_draw',
        }

    regular_pay = round(regular_hours * rate, 2)
    ot_pay = round(ot_hours * rate * OT_MULTIPLIER, 2)
    return {
        'gross': round(regular_pay + ot_pay, 2),
        'regularPay': regular_pay,
        'otPay': ot_pay,
        'regularHours': regular_hours,
        'otHours': ot_hours,
        'method': 'hourly' if worker != 'contractor' else 'contractor_hourly',
        'rateUsed': rate,
    }


def _calc_taxes(emp: dict, gross: float) -> dict:
    """Phase 1 estimates — VERTEX owns calc; deposit via EFTPS + MI/UIA."""
    worker = emp.get('workerType') or 'employee'
    pay_type = (emp.get('payType') or '').lower()
    other = float(emp.get('otherDeductions') or 0)

    if worker == 'contractor' or pay_type == 'contractor':
        return {
            'federalTax': 0.0,
            'stateTax': 0.0,
            'fica': 0.0,
            'medicare': 0.0,
            'otherDeductions': other,
            'taxesNote': '1099 — no W-2 withhold; contractor responsible for self-employment tax',
            'net': round(gross - other, 2),
        }

    if pay_type == 'owner_draw':
        return {
            'federalTax': 0.0,
            'stateTax': 0.0,
            'fica': 0.0,
            'medicare': 0.0,
            'otherDeductions': other,
            'taxesNote': 'Owner draw — track separately from W-2 payroll',
            'net': round(gross - other, 2),
        }

    fed_pct = emp.get('federalWithholdPct')
    state_pct = emp.get('stateWithholdPct')
    try:
        fed_rate = float(fed_pct) / 100.0 if fed_pct is not None else FED_WITHHOLD_EST
    except (TypeError, ValueError):
        fed_rate = FED_WITHHOLD_EST
    try:
        state_rate = float(state_pct) / 100.0 if state_pct is not None else STATE_WITHHOLD_EST
    except (TypeError, ValueError):
        state_rate = STATE_WITHHOLD_EST

    fed = round(gross * fed_rate, 2)
    state = round(gross * state_rate, 2)
    fica = round(gross * FICA_RATE, 2)
    medicare = round(gross * MEDICARE_RATE, 2)
    net = round(gross - fed - state - fica - medicare - other, 2)
    return {
        'federalTax': fed,
        'stateTax': state,
        'fica': fica,
        'medicare': medicare,
        'otherDeductions': other,
        'taxesNote': 'ESTIMATE — confirm before EFTPS/MI deposit; set withhold % on employee tax profile',
        'net': net,
    }


def _split_ot(regular_hours: float, ot_hours: float) -> tuple:
    """If OT not provided, auto-split when regular > 40 for the period week-proxy (biweekly: 80)."""
    r = max(0.0, float(regular_hours or 0))
    o = max(0.0, float(ot_hours or 0))
    if o > 0:
        return r, o
    # Biweekly threshold = 80 hours before OT suggestion
    thresh = STD_WEEKLY_HOURS * 2
    if r > thresh:
        return thresh, round(r - thresh, 2)
    return r, 0.0


# ─── Routes ───────────────────────────────────────────────────────

@vertex_hr.route('/vertex/hr/health', methods=['GET'])
def hr_health():
    company = _get_company()
    return jsonify({
        'ok': True,
        'module': 'VERTEX HR',
        'phase': 1,
        'joinKey': 'personnelNumberCore',
        'identitySource': 'GATEWAY',
        'payRail': company.get('payRail'),
        'taxRails': company.get('taxRails'),
        'employees': len(_load(EMPLOYEES_FILE)),
        'timesheets': len(_load(TIMESHEETS_FILE)),
        'payRuns': len(_load(PAY_RUNS_FILE)),
        'taxDepositsLogged': len(_load(TAX_DEPOSITS_FILE)),
        'companyConfigured': bool(company.get('ein')),
        'miUiaRateSet': company.get('miUiaRatePercent') is not None,
        'capabilities': _capabilities(),
        'currentPeriod': _biweekly_period_for(),
        'master': 'VERTEX_HR_MASTER.md',
    })


@vertex_hr.route('/vertex/hr/capabilities', methods=['GET'])
def hr_capabilities():
    return jsonify({'ok': True, 'capabilities': _capabilities(), 'workflow': [
        '1. POST /employees/sync — pull GATEWAY roster',
        '2. PUT /employees/<core>/rate + /tax — set pay + withhold',
        '3. POST /timesheets → submit → approve',
        '4. POST /pay-runs/preview then POST /pay-runs',
        '5. GET /export/deluxe-pay — pay net via Deluxe eChecks',
        '6. POST /pay-runs/<id>/mark-deluxe-paid',
        '7. GET /tax-liability — deposit via EFTPS + MI/UIA',
        '8. POST /tax-deposits — log confirmation numbers',
    ]})


@vertex_hr.route('/vertex/hr/company', methods=['GET', 'PUT'])
def hr_company():
    if request.method == 'GET':
        return jsonify({'ok': True, 'company': _get_company()})
    data = request.get_json(silent=True) or {}
    company = _get_company()
    actor = (data.get('actorEmail') or data.get('email') or '').strip().lower()
    for key in (
        'legalName', 'ein', 'michiganAccountId', 'miUiaEmployerNumber',
        'federalDepositSchedule', 'defaultPayFrequency', 'periodAnchor',
        'address', 'payRail',
    ):
        if key in data and data[key] is not None:
            company[key] = data[key]
    if 'miUiaRatePercent' in data:
        try:
            company['miUiaRatePercent'] = float(data['miUiaRatePercent']) if data['miUiaRatePercent'] is not None else None
        except (TypeError, ValueError):
            return jsonify({'ok': False, 'error': 'miUiaRatePercent must be a number'}), 400
    if 'taxRails' in data and isinstance(data['taxRails'], list):
        company['taxRails'] = data['taxRails']
    company['updatedAt'] = _now()
    company['updatedBy'] = actor
    _save_obj(COMPANY_FILE, company)
    return jsonify({'ok': True, 'company': company})


@vertex_hr.route('/vertex/hr/period/current', methods=['GET'])
def hr_period_current():
    date_s = (request.args.get('date') or '').strip()[:10]
    day = None
    if date_s:
        try:
            day = datetime.strptime(date_s, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'ok': False, 'error': 'date must be YYYY-MM-DD'}), 400
    return jsonify({'ok': True, 'period': _biweekly_period_for(day), 'company': {
        'periodAnchor': _get_company().get('periodAnchor'),
        'defaultPayFrequency': _get_company().get('defaultPayFrequency'),
    }})


@vertex_hr.route('/vertex/hr/dashboard', methods=['GET'])
def hr_dashboard():
    emps = _load(EMPLOYEES_FILE)
    sheets = _load(TIMESHEETS_FILE)
    runs = _load(PAY_RUNS_FILE)
    deposits = _load(TAX_DEPOSITS_FILE)
    period = _biweekly_period_for()
    company = _get_company()

    payable = [e for e in emps if e.get('payable')]
    missing_rate = []
    for e in payable:
        pt = (e.get('payType') or 'hourly').lower()
        if pt == 'salary' and not float(e.get('salaryAnnual') or 0):
            missing_rate.append(e.get('personnelNumberCore'))
        elif pt in ('hourly', 'contractor') and not (
            float(e.get('hourlyRate') or 0) or float(e.get('contractorRate') or 0)
        ):
            missing_rate.append(e.get('personnelNumberCore'))

    pending_submit = [t for t in sheets if t.get('status') == 'Draft']
    pending_approve = [t for t in sheets if t.get('status') == 'Submitted']
    approved_open = [
        t for t in sheets
        if t.get('status') == 'Approved'
        and (t.get('periodStart') or '')[:10] == period['periodStart']
    ]
    finalized = [r for r in runs if r.get('status') == 'Finalized']
    unpaid_deluxe = [
        r for r in finalized
        if not r.get('deluxePaidAt')
    ]
    blockers = []
    if not company.get('ein'):
        blockers.append('Set company EIN (PUT /vertex/hr/company)')
    if company.get('miUiaRatePercent') is None:
        blockers.append('Set MI UIA rate percent (PUT /vertex/hr/company miUiaRatePercent)')
    if missing_rate:
        blockers.append(f'{len(missing_rate)} payable people missing rates')
    if pending_approve:
        blockers.append(f'{len(pending_approve)} timesheets awaiting approval')

    return jsonify({
        'ok': True,
        'period': period,
        'counts': {
            'employeesSynced': len(emps),
            'payable': len(payable),
            'missingRates': len(missing_rate),
            'timesheetsDraft': len(pending_submit),
            'timesheetsAwaitingApproval': len(pending_approve),
            'timesheetsApprovedThisPeriod': len(approved_open),
            'payRunsFinalized': len(finalized),
            'deluxeUnpaidPayRuns': len(unpaid_deluxe),
            'taxDepositsLogged': len(deposits),
        },
        'blockers': blockers,
        'nextActions': [a for a in [
            'Sync GATEWAY' if not emps else None,
            'Set company EIN / MI UIA rate' if blockers and ('EIN' in blockers[0] or 'UIA' in (blockers[0] if blockers else '')) else None,
            'Approve timesheets' if pending_approve else None,
            'Run payroll preview/finalize' if approved_open else None,
            'Pay Deluxe eChecks' if unpaid_deluxe else None,
            'Deposit taxes + log confirmations' if finalized else None,
        ] if a],
        'readyToRunPayroll': bool(approved_open) and not missing_rate,
    })


@vertex_hr.route('/vertex/hr/employees/sync', methods=['POST'])
def hr_employees_sync():
    """Pull Active GATEWAY roster into VERTEX HR (preserves rates)."""
    existing = {e.get('personnelNumberCore'): e for e in _load(EMPLOYEES_FILE) if e.get('personnelNumberCore')}
    synced = []
    skipped = []
    for rec in _gateway_records():
        if (rec.get('status') or '') not in ('Active', 'Onboarding', 'Pending'):
            # Still sync archived as not payable so history stays
            if (rec.get('status') or '') != 'Archived':
                skipped.append({'id': rec.get('id'), 'reason': 'status skipped'})
                continue
        core = (rec.get('personnelNumberCore') or '').strip()
        if not core:
            skipped.append({'id': rec.get('id'), 'reason': 'no personnelNumberCore'})
            continue
        profile = _profile_from_gateway(rec)
        if (rec.get('status') or '') == 'Archived':
            profile['payable'] = False
            profile['canWork'] = False
        merged = _merge_employee(existing.get(core), profile)
        existing[core] = merged
        synced.append(merged)

    rows = list(existing.values())
    rows.sort(key=lambda e: ((e.get('name') or '').lower(), e.get('personnelNumberCore') or ''))
    _save(EMPLOYEES_FILE, rows)
    return jsonify({
        'ok': True,
        'synced': len(synced),
        'total': len(rows),
        'skipped': skipped[:50],
        'employees': rows,
    })


@vertex_hr.route('/vertex/hr/employees', methods=['GET'])
def hr_employees_list():
    payable_only = (request.args.get('payable') or '').lower() in ('1', 'true', 'yes')
    q = (request.args.get('q') or '').strip().lower()
    rows = _load(EMPLOYEES_FILE)
    out = []
    for e in rows:
        if payable_only and not e.get('payable'):
            continue
        if q:
            blob = ' '.join([
                e.get('name') or '', e.get('email') or '',
                e.get('personnelNumber') or '', e.get('division') or '',
                e.get('account') or '', e.get('level') or '',
            ]).lower()
            if q not in blob:
                continue
        out.append(e)
    return jsonify({'ok': True, 'count': len(out), 'employees': out})


@vertex_hr.route('/vertex/hr/employees/<core>', methods=['GET'])
def hr_employee_get(core):
    emp = _find_employee(core)
    if not emp:
        return jsonify({'ok': False, 'error': 'Employee not in VERTEX HR — run /employees/sync'}), 404
    return jsonify({'ok': True, 'employee': emp})


@vertex_hr.route('/vertex/hr/employees/<core>/rate', methods=['PUT'])
def hr_employee_rate(core):
    data = request.get_json(silent=True) or {}
    rows = _load(EMPLOYEES_FILE)
    idx = next((i for i, e in enumerate(rows) if e.get('personnelNumberCore') == core), None)
    if idx is None:
        return jsonify({'ok': False, 'error': 'Employee not found — sync from GATEWAY first'}), 404

    emp = rows[idx]
    actor = (data.get('actorEmail') or data.get('email') or 'system').strip().lower()
    before = {
        'payType': emp.get('payType'),
        'hourlyRate': emp.get('hourlyRate'),
        'salaryAnnual': emp.get('salaryAnnual'),
        'contractorRate': emp.get('contractorRate'),
        'payFrequency': emp.get('payFrequency'),
    }
    for key in ('payType', 'payFrequency', 'deductionNotes', 'deluxePayeeEmail', 'deluxePayeeName'):
        if key in data and data[key] is not None:
            emp[key] = data[key]
    for key in ('hourlyRate', 'salaryAnnual', 'contractorRate', 'otherDeductions'):
        if key in data and data[key] is not None:
            try:
                emp[key] = float(data[key])
            except (TypeError, ValueError):
                return jsonify({'ok': False, 'error': f'{key} must be a number'}), 400

    hist = list(emp.get('rateHistory') or [])
    hist.append({'at': _now(), 'by': actor, 'before': before, 'after': {
        'payType': emp.get('payType'),
        'hourlyRate': emp.get('hourlyRate'),
        'salaryAnnual': emp.get('salaryAnnual'),
        'contractorRate': emp.get('contractorRate'),
        'payFrequency': emp.get('payFrequency'),
        'otherDeductions': emp.get('otherDeductions'),
    }})
    emp['rateHistory'] = hist[-50:]
    emp['rateUpdatedAt'] = _now()
    emp['rateUpdatedBy'] = actor
    rows[idx] = emp
    _save(EMPLOYEES_FILE, rows)
    return jsonify({'ok': True, 'employee': emp})


@vertex_hr.route('/vertex/hr/employees/<core>/tax', methods=['PUT'])
def hr_employee_tax(core):
    """W-4 style profile — withhold overrides for VERTEX calc."""
    data = request.get_json(silent=True) or {}
    rows = _load(EMPLOYEES_FILE)
    idx = next((i for i, e in enumerate(rows) if e.get('personnelNumberCore') == core), None)
    if idx is None:
        return jsonify({'ok': False, 'error': 'Employee not found'}), 404
    emp = rows[idx]
    for key in ('ssnLast4', 'filingStatus', 'stateWorked', 'w4Notes'):
        if key in data and data[key] is not None:
            emp[key] = str(data[key])[:80]
    for key in ('federalWithholdPct', 'stateWithholdPct'):
        if key in data:
            if data[key] is None or data[key] == '':
                emp[key] = None
            else:
                try:
                    emp[key] = float(data[key])
                except (TypeError, ValueError):
                    return jsonify({'ok': False, 'error': f'{key} must be a number'}), 400
    emp['taxProfileUpdatedAt'] = _now()
    emp['taxProfileUpdatedBy'] = (data.get('actorEmail') or data.get('email') or '').strip().lower()
    rows[idx] = emp
    _save(EMPLOYEES_FILE, rows)
    return jsonify({'ok': True, 'employee': emp})


def create_timesheet_from_ops(
    personnel_number_core: str,
    period_start: str,
    period_end: str,
    regular_hours: float,
    actor_email: str = '',
    notes: str = '',
    punch_ids: Optional[list] = None,
    ot_hours: float = 0.0,
) -> dict:
    """OPS timeclock → VERTEX HR draft timesheet (preserves payroll ownership in VERTEX)."""
    emp = _find_employee(personnel_number_core)
    if not emp:
        return {
            'ok': False,
            'error': 'Employee not in VERTEX HR — Sync GATEWAY in VERTEX first',
        }
    if not emp.get('payable'):
        return {
            'ok': False,
            'error': 'Not payable in VERTEX HR — GATEWAY can-work / status blocked',
            'canWorkReason': emp.get('canWorkReason'),
        }
    d0, d1 = _period_bounds(period_start, period_end)
    if not d0:
        return {'ok': False, 'error': 'periodStart and periodEnd required (YYYY-MM-DD)'}
    regular, ot = _split_ot(regular_hours, ot_hours)
    sheet = {
        'id': f'TS-{uuid.uuid4().hex[:10].upper()}',
        'personnelNumberCore': personnel_number_core,
        'personnelNumber': emp.get('personnelNumber'),
        'name': emp.get('name'),
        'email': emp.get('email') or actor_email,
        'workerType': emp.get('workerType'),
        'periodStart': period_start[:10],
        'periodEnd': period_end[:10],
        'regularHours': regular,
        'otHours': ot,
        'ptoHours': 0.0,
        'unpaidHours': 0.0,
        'notes': notes or 'OPS timeclock',
        'status': 'Draft',
        'source': 'ops-timeclock',
        'opsPunchIds': list(punch_ids or []),
        'createdAt': _now(),
        'createdBy': (actor_email or '').strip().lower(),
        'submittedAt': None,
        'approvedAt': None,
        'approvedBy': None,
    }
    rows = _load(TIMESHEETS_FILE)
    rows.append(sheet)
    _save(TIMESHEETS_FILE, rows)
    return {
        'ok': True,
        'timesheet': sheet,
        'hours': round(regular + ot, 2),
        'punchCount': len(punch_ids or []),
        'periodStart': period_start[:10],
        'periodEnd': period_end[:10],
    }


@vertex_hr.route('/vertex/hr/timesheets', methods=['GET', 'POST'])
def hr_timesheets():
    if request.method == 'GET':
        core = (request.args.get('personnelNumberCore') or request.args.get('core') or '').strip()
        status = (request.args.get('status') or '').strip()
        period_start = (request.args.get('periodStart') or '').strip()[:10]
        rows = _load(TIMESHEETS_FILE)
        out = []
        for t in rows:
            if core and t.get('personnelNumberCore') != core:
                continue
            if status and (t.get('status') or '') != status:
                continue
            if period_start and (t.get('periodStart') or '')[:10] != period_start:
                continue
            out.append(t)
        out.sort(key=lambda x: (x.get('periodStart') or '', x.get('name') or ''), reverse=True)
        return jsonify({'ok': True, 'count': len(out), 'timesheets': out})

    data = request.get_json(silent=True) or {}
    core = (data.get('personnelNumberCore') or data.get('core') or '').strip()
    emp = _find_employee(core)
    if not emp:
        return jsonify({'ok': False, 'error': 'Employee not in VERTEX HR — sync GATEWAY first'}), 404
    if not emp.get('payable') and not data.get('force'):
        return jsonify({
            'ok': False,
            'error': 'Not payable — GATEWAY can-work / status blocked',
            'canWorkReason': emp.get('canWorkReason'),
        }), 403

    start = (data.get('periodStart') or '')[:10]
    end = (data.get('periodEnd') or '')[:10]
    d0, d1 = _period_bounds(start, end)
    if not d0:
        return jsonify({'ok': False, 'error': 'periodStart and periodEnd required (YYYY-MM-DD)'}), 400

    regular = float(data.get('regularHours') or data.get('hours') or 0)
    ot = float(data.get('otHours') or 0)
    pto = float(data.get('ptoHours') or 0)
    unpaid = float(data.get('unpaidHours') or 0)
    regular, ot = _split_ot(regular, ot)

    sheet = {
        'id': f'TS-{uuid.uuid4().hex[:10].upper()}',
        'personnelNumberCore': core,
        'personnelNumber': emp.get('personnelNumber'),
        'name': emp.get('name'),
        'email': emp.get('email'),
        'workerType': emp.get('workerType'),
        'periodStart': start,
        'periodEnd': end,
        'regularHours': regular,
        'otHours': ot,
        'ptoHours': pto,
        'unpaidHours': unpaid,
        'notes': data.get('notes') or '',
        'status': 'Draft',
        'createdAt': _now(),
        'createdBy': (data.get('actorEmail') or data.get('email') or emp.get('email') or '').strip().lower(),
        'submittedAt': None,
        'approvedAt': None,
        'approvedBy': None,
    }
    rows = _load(TIMESHEETS_FILE)
    rows.append(sheet)
    _save(TIMESHEETS_FILE, rows)
    return jsonify({'ok': True, 'timesheet': sheet}), 201


@vertex_hr.route('/vertex/hr/timesheets/<sheet_id>/submit', methods=['POST'])
def hr_timesheet_submit(sheet_id):
    rows = _load(TIMESHEETS_FILE)
    idx = next((i for i, t in enumerate(rows) if t.get('id') == sheet_id), None)
    if idx is None:
        return jsonify({'ok': False, 'error': 'Timesheet not found'}), 404
    t = rows[idx]
    if t.get('status') not in ('Draft', 'Rejected'):
        return jsonify({'ok': False, 'error': f"Cannot submit from status {t.get('status')}"}), 409
    t['status'] = 'Submitted'
    t['submittedAt'] = _now()
    rows[idx] = t
    _save(TIMESHEETS_FILE, rows)
    return jsonify({'ok': True, 'timesheet': t})


@vertex_hr.route('/vertex/hr/timesheets/<sheet_id>/approve', methods=['POST'])
def hr_timesheet_approve(sheet_id):
    data = request.get_json(silent=True) or {}
    actor = (data.get('actorEmail') or data.get('email') or '').strip().lower()
    rows = _load(TIMESHEETS_FILE)
    idx = next((i for i, t in enumerate(rows) if t.get('id') == sheet_id), None)
    if idx is None:
        return jsonify({'ok': False, 'error': 'Timesheet not found'}), 404
    t = rows[idx]
    if t.get('status') not in ('Submitted', 'Draft'):
        return jsonify({'ok': False, 'error': f"Cannot approve from status {t.get('status')}"}), 409
    t['status'] = 'Approved'
    t['approvedAt'] = _now()
    t['approvedBy'] = actor or 'supervisor'
    if not t.get('submittedAt'):
        t['submittedAt'] = t['approvedAt']
    rows[idx] = t
    _save(TIMESHEETS_FILE, rows)
    return jsonify({'ok': True, 'timesheet': t})


@vertex_hr.route('/vertex/hr/timesheets/<sheet_id>/reject', methods=['POST'])
def hr_timesheet_reject(sheet_id):
    data = request.get_json(silent=True) or {}
    actor = (data.get('actorEmail') or data.get('email') or '').strip().lower()
    reason = (data.get('reason') or data.get('notes') or '').strip()
    rows = _load(TIMESHEETS_FILE)
    idx = next((i for i, t in enumerate(rows) if t.get('id') == sheet_id), None)
    if idx is None:
        return jsonify({'ok': False, 'error': 'Timesheet not found'}), 404
    t = rows[idx]
    if t.get('status') not in ('Submitted', 'Draft', 'Approved'):
        return jsonify({'ok': False, 'error': f"Cannot reject from status {t.get('status')}"}), 409
    if t.get('status') == 'Paid':
        return jsonify({'ok': False, 'error': 'Already in a pay run'}), 409
    t['status'] = 'Rejected'
    t['rejectedAt'] = _now()
    t['rejectedBy'] = actor
    t['rejectReason'] = reason
    rows[idx] = t
    _save(TIMESHEETS_FILE, rows)
    return jsonify({'ok': True, 'timesheet': t})


@vertex_hr.route('/vertex/hr/timesheets/<sheet_id>', methods=['PATCH'])
def hr_timesheet_patch(sheet_id):
    """Edit hours only while Draft or Rejected."""
    data = request.get_json(silent=True) or {}
    rows = _load(TIMESHEETS_FILE)
    idx = next((i for i, t in enumerate(rows) if t.get('id') == sheet_id), None)
    if idx is None:
        return jsonify({'ok': False, 'error': 'Timesheet not found'}), 404
    t = rows[idx]
    if t.get('status') not in ('Draft', 'Rejected'):
        return jsonify({'ok': False, 'error': 'Only Draft/Rejected timesheets can be edited'}), 409
    for key in ('regularHours', 'otHours', 'ptoHours', 'unpaidHours'):
        if key in data and data[key] is not None:
            try:
                t[key] = float(data[key])
            except (TypeError, ValueError):
                return jsonify({'ok': False, 'error': f'{key} must be a number'}), 400
    if 'notes' in data:
        t['notes'] = data.get('notes') or ''
    r, o = _split_ot(t.get('regularHours'), t.get('otHours'))
    t['regularHours'], t['otHours'] = r, o
    t['status'] = 'Draft'
    t['updatedAt'] = _now()
    rows[idx] = t
    _save(TIMESHEETS_FILE, rows)
    return jsonify({'ok': True, 'timesheet': t})


def _build_pay_lines(period_start: str, period_end: str, timesheet_ids: Optional[list] = None) -> list:
    sheets = _load(TIMESHEETS_FILE)
    approved = [
        t for t in sheets
        if t.get('status') == 'Approved'
        and (t.get('periodStart') or '')[:10] == period_start[:10]
        and (t.get('periodEnd') or '')[:10] == period_end[:10]
        and (not timesheet_ids or t.get('id') in timesheet_ids)
    ]
    lines = []
    for t in approved:
        emp = _find_employee(t.get('personnelNumberCore') or '')
        if not emp:
            continue
        if not emp.get('payable'):
            lines.append({
                'personnelNumberCore': t.get('personnelNumberCore'),
                'name': t.get('name'),
                'error': 'not payable',
                'timesheetId': t.get('id'),
            })
            continue
        gross_info = _calc_gross(emp, t.get('regularHours'), t.get('otHours'))
        tax = _calc_taxes(emp, gross_info['gross'])
        lines.append({
            'timesheetId': t.get('id'),
            'personnelNumberCore': emp.get('personnelNumberCore'),
            'personnelNumber': emp.get('personnelNumber'),
            'name': emp.get('name'),
            'email': emp.get('email'),
            'workerType': emp.get('workerType'),
            'employeeTypeLabel': emp.get('employeeTypeLabel'),
            'payType': emp.get('payType'),
            'account': emp.get('account'),
            'division': emp.get('division'),
            **gross_info,
            **tax,
            'paymentStatus': 'Pending',
        })
    return lines


@vertex_hr.route('/vertex/hr/pay-runs/preview', methods=['POST'])
def hr_pay_run_preview():
    data = request.get_json(silent=True) or {}
    start = (data.get('periodStart') or '')[:10]
    end = (data.get('periodEnd') or '')[:10]
    if not _period_bounds(start, end)[0]:
        return jsonify({'ok': False, 'error': 'periodStart and periodEnd required'}), 400
    lines = _build_pay_lines(start, end, data.get('timesheetIds'))
    ok_lines = [l for l in lines if not l.get('error')]
    return jsonify({
        'ok': True,
        'periodStart': start,
        'periodEnd': end,
        'lineCount': len(ok_lines),
        'grossTotal': round(sum(l.get('gross') or 0 for l in ok_lines), 2),
        'netTotal': round(sum(l.get('net') or 0 for l in ok_lines), 2),
        'lines': lines,
        'note': 'Preview only — POST /vertex/hr/pay-runs to finalize',
    })


@vertex_hr.route('/vertex/hr/pay-runs', methods=['GET', 'POST'])
def hr_pay_runs():
    if request.method == 'GET':
        rows = _load(PAY_RUNS_FILE)
        rows.sort(key=lambda r: r.get('createdAt') or '', reverse=True)
        return jsonify({'ok': True, 'count': len(rows), 'payRuns': rows})

    data = request.get_json(silent=True) or {}
    start = (data.get('periodStart') or '')[:10]
    end = (data.get('periodEnd') or '')[:10]
    if not _period_bounds(start, end)[0]:
        return jsonify({'ok': False, 'error': 'periodStart and periodEnd required'}), 400

    # Prevent duplicate finalize for same period
    existing = _load(PAY_RUNS_FILE)
    for pr in existing:
        if (
            pr.get('status') == 'Finalized'
            and (pr.get('periodStart') or '')[:10] == start
            and (pr.get('periodEnd') or '')[:10] == end
        ):
            return jsonify({
                'ok': False,
                'error': 'Pay run already finalized for this period',
                'payRunId': pr.get('id'),
            }), 409

    # Fresh GATEWAY can-work check before finalize
    emps = _load(EMPLOYEES_FILE)
    by_core = {e.get('personnelNumberCore'): i for i, e in enumerate(emps)}
    for core, i in list(by_core.items()):
        emps[i] = _refresh_payable_from_gateway(emps[i])
    _save(EMPLOYEES_FILE, emps)

    lines = _build_pay_lines(start, end, data.get('timesheetIds'))
    ok_lines = [l for l in lines if not l.get('error')]
    if not ok_lines:
        return jsonify({
            'ok': False,
            'error': 'No approved payable timesheets for this period',
            'errors': [l for l in lines if l.get('error')],
        }), 400

    # Attach Deluxe payee fields
    for line in ok_lines:
        i = by_core.get(line.get('personnelNumberCore'))
        if i is not None:
            emp = emps[i]
            line['deluxePayeeName'] = emp.get('deluxePayeeName') or emp.get('name')
            line['deluxePayeeEmail'] = emp.get('deluxePayeeEmail') or emp.get('email')
            line['ssnLast4'] = emp.get('ssnLast4') or ''
        line['deluxePaid'] = False
        line['paymentMethod'] = 'Deluxe eCheck'

    actor = (data.get('actorEmail') or data.get('email') or 'system').strip().lower()
    force = bool(data.get('force'))
    company = _get_company()
    pay_run = {
        'id': f'PAY-{datetime.now().strftime("%Y%m%d")}-{uuid.uuid4().hex[:6].upper()}',
        'periodStart': start,
        'periodEnd': end,
        'status': 'Finalized',
        'createdAt': _now(),
        'createdBy': actor,
        'paymentDate': (data.get('paymentDate') or end)[:10],
        'lineCount': len(ok_lines),
        'grossTotal': round(sum(l.get('gross') or 0 for l in ok_lines), 2),
        'netTotal': round(sum(l.get('net') or 0 for l in ok_lines), 2),
        'federalTaxTotal': round(sum(l.get('federalTax') or 0 for l in ok_lines), 2),
        'stateTaxTotal': round(sum(l.get('stateTax') or 0 for l in ok_lines), 2),
        'ficaTotal': round(sum(l.get('fica') or 0 for l in ok_lines), 2),
        'medicareTotal': round(sum(l.get('medicare') or 0 for l in ok_lines), 2),
        'lines': ok_lines,
        'errors': [l for l in lines if l.get('error')],
        'payRail': 'Deluxe eChecks',
        'deluxePaidAt': None,
        'deluxePaidBy': None,
        'taxesDeposited': False,
        'companyEinSet': bool(company.get('ein')),
        'force': force,
        'note': 'Finalize locked. Next: Deluxe eChecks for net → EFTPS/MI for taxes → log deposits',
    }

    sheets = _load(TIMESHEETS_FILE)
    locked_ids = {l.get('timesheetId') for l in ok_lines}
    for i, t in enumerate(sheets):
        if t.get('id') in locked_ids:
            t['status'] = 'Paid'
            t['payRunId'] = pay_run['id']
            sheets[i] = t
    _save(TIMESHEETS_FILE, sheets)

    emps = _load(EMPLOYEES_FILE)
    by_core = {e.get('personnelNumberCore'): i for i, e in enumerate(emps)}
    for line in ok_lines:
        i = by_core.get(line.get('personnelNumberCore'))
        if i is None:
            continue
        emps[i]['ytdGross'] = round(float(emps[i].get('ytdGross') or 0) + float(line.get('gross') or 0), 2)
        emps[i]['ytdNet'] = round(float(emps[i].get('ytdNet') or 0) + float(line.get('net') or 0), 2)
        emps[i]['ytdFederalTax'] = round(float(emps[i].get('ytdFederalTax') or 0) + float(line.get('federalTax') or 0), 2)
        emps[i]['ytdStateTax'] = round(float(emps[i].get('ytdStateTax') or 0) + float(line.get('stateTax') or 0), 2)
        emps[i]['ytdFica'] = round(float(emps[i].get('ytdFica') or 0) + float(line.get('fica') or 0), 2)
        emps[i]['ytdMedicare'] = round(float(emps[i].get('ytdMedicare') or 0) + float(line.get('medicare') or 0), 2)
    _save(EMPLOYEES_FILE, emps)

    existing.append(pay_run)
    _save(PAY_RUNS_FILE, existing)
    return jsonify({
        'ok': True,
        'payRun': pay_run,
        'next': [
            f"GET /vertex/hr/export/deluxe-pay?id={pay_run['id']}",
            f"POST /vertex/hr/pay-runs/{pay_run['id']}/mark-deluxe-paid",
            f"GET /vertex/hr/tax-liability?payRunId={pay_run['id']}",
            'POST /vertex/hr/tax-deposits',
        ],
    }), 201


@vertex_hr.route('/vertex/hr/pay-runs/<pay_run_id>', methods=['GET'])
def hr_pay_run_get(pay_run_id):
    for pr in _load(PAY_RUNS_FILE):
        if pr.get('id') == pay_run_id:
            return jsonify({'ok': True, 'payRun': pr})
    return jsonify({'ok': False, 'error': 'Pay run not found'}), 404


@vertex_hr.route('/vertex/hr/export/deluxe-pay', methods=['GET'])
def hr_export_deluxe_pay():
    """Net-pay register for Deluxe eChecks (pay people — not taxes)."""
    pay_run_id = (request.args.get('id') or '').strip()
    runs = _load(PAY_RUNS_FILE)
    pr = None
    if pay_run_id:
        pr = next((r for r in runs if r.get('id') == pay_run_id), None)
    else:
        finalized = [r for r in runs if r.get('status') == 'Finalized']
        finalized.sort(key=lambda r: r.get('createdAt') or '', reverse=True)
        pr = finalized[0] if finalized else None
    if not pr:
        return jsonify({'ok': False, 'error': 'No finalized pay run'}), 404

    rows = []
    for line in pr.get('lines') or []:
        rows.append({
            'payee_name': line.get('deluxePayeeName') or line.get('name'),
            'email': line.get('deluxePayeeEmail') or line.get('email'),
            'personnel_number': line.get('personnelNumber'),
            'personnel_number_core': line.get('personnelNumberCore'),
            'type': line.get('employeeTypeLabel'),
            'gross': line.get('gross'),
            'net_pay': line.get('net'),
            'deluxe_paid': bool(line.get('deluxePaid')),
            'payment_method': 'Deluxe eCheck',
            'period_start': pr.get('periodStart'),
            'period_end': pr.get('periodEnd'),
            'payment_date': pr.get('paymentDate'),
            'memo': f"DDI payroll {pr.get('id')} {pr.get('periodStart')}–{pr.get('periodEnd')}",
        })
    unpaid = [r for r in rows if not r.get('deluxe_paid')]
    return jsonify({
        'ok': True,
        'payRunId': pr.get('id'),
        'format': 'deluxe_echeck_register',
        'netTotal': pr.get('netTotal'),
        'unpaidCount': len(unpaid),
        'deluxePaidAt': pr.get('deluxePaidAt'),
        'rows': rows,
        'note': 'Pay unpaid net amounts via Deluxe eChecks. Then POST .../mark-deluxe-paid. Taxes → /tax-liability',
    })


@vertex_hr.route('/vertex/hr/pay-runs/<pay_run_id>/mark-deluxe-paid', methods=['POST'])
def hr_mark_deluxe_paid(pay_run_id):
    data = request.get_json(silent=True) or {}
    actor = (data.get('actorEmail') or data.get('email') or '').strip().lower()
    confirmation = (data.get('confirmationNumber') or data.get('batchId') or '').strip()
    runs = _load(PAY_RUNS_FILE)
    idx = next((i for i, r in enumerate(runs) if r.get('id') == pay_run_id), None)
    if idx is None:
        return jsonify({'ok': False, 'error': 'Pay run not found'}), 404
    pr = runs[idx]
    cores = data.get('personnelNumberCores') or data.get('cores')
    for line in pr.get('lines') or []:
        if cores and line.get('personnelNumberCore') not in cores:
            continue
        line['deluxePaid'] = True
        line['deluxePaidAt'] = _now()
    pr['deluxePaidAt'] = _now()
    pr['deluxePaidBy'] = actor
    pr['deluxeConfirmation'] = confirmation
    runs[idx] = pr
    _save(PAY_RUNS_FILE, runs)
    return jsonify({'ok': True, 'payRun': pr})


@vertex_hr.route('/vertex/hr/pay-runs/<pay_run_id>/stub/<core>', methods=['GET'])
def hr_pay_stub(pay_run_id, core):
    for pr in _load(PAY_RUNS_FILE):
        if pr.get('id') != pay_run_id:
            continue
        for line in pr.get('lines') or []:
            if line.get('personnelNumberCore') == core:
                emp = _find_employee(core) or {}
                return jsonify({
                    'ok': True,
                    'stub': {
                        'employer': _get_company().get('legalName'),
                        'payRunId': pay_run_id,
                        'periodStart': pr.get('periodStart'),
                        'periodEnd': pr.get('periodEnd'),
                        'paymentDate': pr.get('paymentDate'),
                        'paymentMethod': 'Deluxe eCheck',
                        'employee': {
                            'name': line.get('name'),
                            'personnelNumber': line.get('personnelNumber'),
                            'ssnLast4': line.get('ssnLast4') or emp.get('ssnLast4') or '',
                            'workerType': line.get('workerType'),
                        },
                        'hours': {
                            'regular': line.get('regularHours'),
                            'ot': line.get('otHours'),
                        },
                        'earnings': {
                            'regularPay': line.get('regularPay'),
                            'otPay': line.get('otPay'),
                            'gross': line.get('gross'),
                        },
                        'deductions': {
                            'federalTax': line.get('federalTax'),
                            'stateTax': line.get('stateTax'),
                            'fica': line.get('fica'),
                            'medicare': line.get('medicare'),
                            'other': line.get('otherDeductions'),
                        },
                        'net': line.get('net'),
                        'ytd': {
                            'gross': emp.get('ytdGross'),
                            'net': emp.get('ytdNet'),
                            'federalTax': emp.get('ytdFederalTax'),
                            'stateTax': emp.get('ytdStateTax'),
                            'fica': emp.get('ytdFica'),
                            'medicare': emp.get('ytdMedicare'),
                        },
                    },
                })
    return jsonify({'ok': False, 'error': 'Stub not found'}), 404


# Keep old path as alias so nothing breaks if bookmarked
@vertex_hr.route('/vertex/hr/export/gusto', methods=['GET'])
def hr_export_gusto_alias():
    return hr_export_deluxe_pay()


@vertex_hr.route('/vertex/hr/tax-liability', methods=['GET'])
def hr_tax_liability():
    """
    Tax deposit worksheet from finalized pay runs.
    Submit federal via EFTPS.gov; Michigan income + UIA via state portals.
    """
    start = (request.args.get('periodStart') or request.args.get('start') or '').strip()[:10]
    end = (request.args.get('periodEnd') or request.args.get('end') or '').strip()[:10]
    pay_run_id = (request.args.get('payRunId') or request.args.get('id') or '').strip()

    runs = [r for r in _load(PAY_RUNS_FILE) if r.get('status') == 'Finalized']
    if pay_run_id:
        runs = [r for r in runs if r.get('id') == pay_run_id]
    elif start or end:
        filtered = []
        for r in runs:
            rs = (r.get('periodStart') or '')[:10]
            re_ = (r.get('periodEnd') or '')[:10]
            if start and rs < start:
                continue
            if end and re_ > end:
                continue
            filtered.append(r)
        runs = filtered

    fed_income = 0.0
    ee_fica = 0.0
    ee_medicare = 0.0
    state_income = 0.0
    w2_gross = 0.0
    contractor_gross = 0.0
    net_paid = 0.0
    people = set()

    for pr in runs:
        for line in pr.get('lines') or []:
            people.add(line.get('personnelNumberCore') or line.get('email'))
            net_paid += float(line.get('net') or 0)
            wt = line.get('workerType') or 'employee'
            if wt == 'contractor' or (line.get('payType') or '') == 'contractor':
                contractor_gross += float(line.get('gross') or 0)
                continue
            if (line.get('payType') or '') == 'owner_draw':
                continue
            g = float(line.get('gross') or 0)
            w2_gross += g
            fed_income += float(line.get('federalTax') or 0)
            ee_fica += float(line.get('fica') or 0)
            ee_medicare += float(line.get('medicare') or 0)
            state_income += float(line.get('stateTax') or 0)

    # Employer match (same rates Phase 1)
    er_fica = round(ee_fica, 2)  # match employee FICA withheld on same wages
    er_medicare = round(ee_medicare, 2)
    futa_est = round(w2_gross * FUTA_RATE_EST, 2)
    company = _get_company()
    uia_rate = company.get('miUiaRatePercent')
    mi_uia_amount = None
    mi_uia_note = 'Set miUiaRatePercent on PUT /vertex/hr/company to auto-calc'
    if uia_rate is not None:
        try:
            mi_uia_amount = round(w2_gross * (float(uia_rate) / 100.0), 2)
            mi_uia_note = f'W-2 gross × {uia_rate}% employer UIA rate (confirm wage base / experience rate)'
        except (TypeError, ValueError):
            pass

    federal_941_deposit = round(fed_income + ee_fica + ee_medicare + er_fica + er_medicare, 2)

    return jsonify({
        'ok': True,
        'payRail': 'Deluxe eChecks (net pay to people)',
        'taxRails': {
            'federal': 'EFTPS.gov',
            'michiganIncome': 'Michigan Treasury / Business Tax portal',
            'michiganUnemployment': 'Michigan UIA',
        },
        'company': {
            'legalName': company.get('legalName'),
            'ein': company.get('ein') or '(set EIN)',
            'federalDepositSchedule': company.get('federalDepositSchedule'),
            'miUiaEmployerNumber': company.get('miUiaEmployerNumber') or '',
            'miUiaRatePercent': uia_rate,
        },
        'periodStart': start or None,
        'periodEnd': end or None,
        'payRunIds': [r.get('id') for r in runs],
        'payRunCount': len(runs),
        'peopleCount': len([p for p in people if p]),
        'w2Gross': round(w2_gross, 2),
        'contractorGross': round(contractor_gross, 2),
        'netPaidViaDeluxe': round(net_paid, 2),
        'deposits': {
            'eftps_941_style': {
                'label': 'Federal deposit (employee FIT + SS/Med EE+ER)',
                'amount': federal_941_deposit,
                'breakdown': {
                    'federalIncomeTaxWithheld': round(fed_income, 2),
                    'socialSecurityEmployee': round(ee_fica, 2),
                    'socialSecurityEmployer': er_fica,
                    'medicareEmployee': round(ee_medicare, 2),
                    'medicareEmployer': er_medicare,
                },
                'where': 'https://www.eftps.gov',
            },
            'eftps_futa_940_est': {
                'label': 'FUTA estimate (verify credit reduction / wage base)',
                'amount': futa_est,
                'where': 'https://www.eftps.gov',
            },
            'michigan_income_withholding': {
                'label': 'Michigan income tax withheld',
                'amount': round(state_income, 2),
                'where': 'Michigan Treasury business portal',
            },
            'michigan_uia': {
                'label': 'Michigan UIA (employer unemployment)',
                'amount': mi_uia_amount,
                'note': mi_uia_note,
                'where': 'Michigan UIA employer portal',
            },
        },
        'checklist': [
            'Pay net wages via Deluxe eChecks (export/deluxe-pay)',
            'Mark pay run Deluxe-paid',
            'Deposit federal 941-style amount in EFTPS',
            'Deposit MI income withholding',
            'Deposit MI UIA (if amount shown)',
            'POST each deposit to /vertex/hr/tax-deposits with confirmation #',
        ],
        'estimatesNote': (
            'Amounts come from finalized VERTEX pay runs (estimate withhold %). '
            'Confirm before depositing. Log via POST /vertex/hr/tax-deposits.'
        ),
    })


@vertex_hr.route('/vertex/hr/tax-deposits', methods=['GET', 'POST'])
def hr_tax_deposits():
    """Log EFTPS / MI / UIA deposits so VERTEX tracks what was submitted."""
    if request.method == 'GET':
        rows = _load(TAX_DEPOSITS_FILE)
        rows.sort(key=lambda r: r.get('depositedAt') or '', reverse=True)
        return jsonify({'ok': True, 'count': len(rows), 'deposits': rows})

    data = request.get_json(silent=True) or {}
    channel = (data.get('channel') or '').strip().lower()  # eftps | mi_income | mi_uia
    amount = data.get('amount')
    if channel not in ('eftps', 'mi_income', 'mi_uia', 'other'):
        return jsonify({'ok': False, 'error': 'channel must be eftps|mi_income|mi_uia|other'}), 400
    try:
        amount_f = float(amount)
    except (TypeError, ValueError):
        return jsonify({'ok': False, 'error': 'amount required'}), 400

    entry = {
        'id': f'TAX-{uuid.uuid4().hex[:10].upper()}',
        'channel': channel,
        'amount': amount_f,
        'confirmationNumber': (data.get('confirmationNumber') or data.get('confirmation') or '').strip(),
        'periodStart': (data.get('periodStart') or '')[:10],
        'periodEnd': (data.get('periodEnd') or '')[:10],
        'payRunId': data.get('payRunId') or '',
        'depositedAt': (data.get('depositedAt') or _now())[:19],
        'actorEmail': (data.get('actorEmail') or data.get('email') or '').strip().lower(),
        'notes': data.get('notes') or '',
        'createdAt': _now(),
    }
    rows = _load(TAX_DEPOSITS_FILE)
    rows.append(entry)
    _save(TAX_DEPOSITS_FILE, rows)
    return jsonify({'ok': True, 'deposit': entry}), 201
