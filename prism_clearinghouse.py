#!/usr/bin/env python3
"""
PRISM FMCSA CLEARINGHOUSE COMPLIANCE MODULE
=============================================
Manages all FMCSA Drug & Alcohol Clearinghouse obligations for Dee Davis Inc.
as a registered C/TPA (Consortium/Third Party Administrator).

NOTE: The FMCSA Clearinghouse does not offer a C/TPA-facing API.
Actions are performed via the web interface at clearinghouse.fmcsa.dot.gov.
This module manages the COMPLIANCE WORKFLOW — tracking what needs to happen,
when it must happen, and generating the action queue for DDI staff to execute.

C/TPA OBLIGATIONS (49 CFR Part 382 + FMCSA Clearinghouse):
- Report violations by close of 3rd business day after employer receives info
- Run pre-employment queries before driver begins safety-sensitive functions
- Run annual queries for all active drivers (once every 12 months)
- Report return-to-duty (RTD) negative test results
- Report follow-up testing completion
- Manage limited vs. full query consent

Reference: 49 CFR Part 382, FMCSA Clearinghouse Final Rule (Jan 2020),
           Clearinghouse II Final Rule (Nov 2024)
"""

import json
import os
import uuid
from datetime import datetime, timedelta, date
from typing import Dict, List, Optional, Tuple
from flask import Blueprint, request, jsonify

prism_clearinghouse = Blueprint('prism_clearinghouse', __name__)

# ═══════════════════════════════════════════════════════════════════
# DATA STORAGE
# ═══════════════════════════════════════════════════════════════════

DATA_DIR = os.path.join(os.path.dirname(__file__), 'uploads', 'prism', 'clearinghouse')

DRIVERS_FILE    = os.path.join(DATA_DIR, 'drivers.json')
QUERIES_FILE    = os.path.join(DATA_DIR, 'queries.json')
VIOLATIONS_FILE = os.path.join(DATA_DIR, 'violations.json')
RTD_FILE        = os.path.join(DATA_DIR, 'return_to_duty.json')
FOLLOWUP_FILE   = os.path.join(DATA_DIR, 'followup_tests.json')
EMPLOYERS_FILE  = os.path.join(DATA_DIR, 'employers.json')
ACTIONS_FILE    = os.path.join(DATA_DIR, 'action_queue.json')


def _ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


def _load(filepath: str) -> list:
    _ensure_data_dir()
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            return json.load(f)
    return []


def _save(filepath: str, data: list):
    _ensure_data_dir()
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2, default=str)


def _new_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:8].upper()}"


# ═══════════════════════════════════════════════════════════════════
# BUSINESS DAY UTILITIES
# ═══════════════════════════════════════════════════════════════════

def _is_business_day(d: date) -> bool:
    """Return True if d is Monday-Friday (no federal holiday check — conservative)."""
    return d.weekday() < 5


def _add_business_days(start: date, days: int) -> date:
    """Add N business days to start date."""
    current = start
    added = 0
    while added < days:
        current += timedelta(days=1)
        if _is_business_day(current):
            added += 1
    return current


def _business_days_between(start: date, end: date) -> int:
    """Count business days between two dates."""
    count = 0
    current = start
    while current < end:
        current += timedelta(days=1)
        if _is_business_day(current):
            count += 1
    return count


# ═══════════════════════════════════════════════════════════════════
# VIOLATION TYPES (49 CFR Part 382.107)
# ═══════════════════════════════════════════════════════════════════

VIOLATION_TYPES = {
    'POSITIVE_DRUG':       'Positive drug test result (confirmed by MRO)',
    'POSITIVE_ALCOHOL':    'Alcohol concentration ≥ 0.04',
    'REFUSAL_DRUG':        'Refusal to submit to drug test',
    'REFUSAL_ALCOHOL':     'Refusal to submit to alcohol test',
    'PROHIBITED_DRUG':     'On-duty drug use',
    'PROHIBITED_ALCOHOL':  'Pre-duty alcohol use (within 4 hours) or on-duty use',
    'ADULTERATED':         'Adulterated or substituted specimen',
    'INVALID_NO_EXPLAIN':  'Invalid result — no adequate medical explanation',
}

QUERY_TYPES = {
    'PRE_EMPLOYMENT': 'Pre-Employment Query — required before safety-sensitive duty',
    'ANNUAL':         'Annual Query — required once per 12-month period',
    'LIMITED':        'Limited Query — no driver consent needed, returns prohibited/not-prohibited only',
    'FULL':           'Full Query — requires driver consent, returns full violation history',
}

DRIVER_STATUSES = ['NOT_PROHIBITED', 'PROHIBITED', 'PENDING_RTD', 'UNKNOWN']


# ═══════════════════════════════════════════════════════════════════
# EMPLOYER MANAGEMENT
# ═══════════════════════════════════════════════════════════════════

def register_employer(
    employer_name: str,
    dot_number: str,
    contact_name: str,
    contact_email: str,
    contact_phone: str,
    dot_authority: str = 'FMCSA',
    notes: str = ''
) -> dict:
    """Register an employer in DDI's C/TPA account."""
    employers = _load(EMPLOYERS_FILE)

    # Check for duplicate DOT number
    for e in employers:
        if e.get('dot_number') == dot_number:
            return {'error': f'Employer with DOT# {dot_number} already registered', 'employer': e}

    employer = {
        'id':             _new_id('EMP'),
        'employer_name':  employer_name,
        'dot_number':     dot_number,
        'dot_authority':  dot_authority,
        'contact_name':   contact_name,
        'contact_email':  contact_email,
        'contact_phone':  contact_phone,
        'notes':          notes,
        'status':         'ACTIVE',
        'registered':     datetime.now().isoformat(),
        'driver_count':   0,
        'clearinghouse_authorized': False,
        'authorization_functions': [],
    }

    employers.append(employer)
    _save(EMPLOYERS_FILE, employers)
    return {
        'message': f'Employer {employer_name} registered',
        'employer_id': employer['id'],
        'next_step': (
            'Employer must log into clearinghouse.fmcsa.dot.gov, '
            'go to My Dashboard → Designate a C/TPA, search for Dee Davis Inc., '
            'and authorize: Report Violations, Report RTD Information, Conduct Queries.'
        ),
        'employer': employer,
    }


def confirm_employer_authorization(employer_id: str, functions: List[str]) -> dict:
    """Mark employer as having authorized DDI in the Clearinghouse."""
    employers = _load(EMPLOYERS_FILE)
    for e in employers:
        if e['id'] == employer_id:
            e['clearinghouse_authorized'] = True
            e['authorization_functions'] = functions
            e['authorization_confirmed'] = datetime.now().isoformat()
            _save(EMPLOYERS_FILE, employers)
            return {'message': 'Authorization confirmed', 'employer': e}
    return {'error': f'Employer {employer_id} not found'}


# ═══════════════════════════════════════════════════════════════════
# DRIVER REGISTRY
# ═══════════════════════════════════════════════════════════════════

def register_driver(
    employer_id: str,
    first_name: str,
    last_name: str,
    cdl_number: str,
    cdl_state: str,
    date_of_birth: str,
    hire_date: str = None,
    notes: str = ''
) -> dict:
    """Register a CDL driver under an employer for Clearinghouse tracking."""
    drivers = _load(DRIVERS_FILE)

    # Check duplicate CDL
    for d in drivers:
        if d.get('cdl_number') == cdl_number and d.get('cdl_state') == cdl_state:
            if d.get('employer_id') == employer_id:
                return {'error': f'Driver CDL {cdl_number}/{cdl_state} already registered for this employer', 'driver': d}

    today = date.today()
    driver = {
        'id':                  _new_id('DRV'),
        'employer_id':         employer_id,
        'first_name':          first_name,
        'last_name':           last_name,
        'full_name':           f"{first_name} {last_name}",
        'cdl_number':          cdl_number,
        'cdl_state':           cdl_state.upper(),
        'date_of_birth':       date_of_birth,
        'hire_date':           hire_date or today.isoformat(),
        'clearinghouse_status': 'UNKNOWN',
        'last_query_date':     None,
        'last_query_type':     None,
        'annual_query_due':    None,
        'pre_employment_done': False,
        'pre_employment_date': None,
        'violations':          [],
        'prohibited':          False,
        'prohibited_since':    None,
        'rtd_status':          None,
        'notes':               notes,
        'active':              True,
        'registered':          datetime.now().isoformat(),
    }

    drivers.append(driver)
    _save(DRIVERS_FILE, drivers)

    # Update employer driver count
    employers = _load(EMPLOYERS_FILE)
    for e in employers:
        if e['id'] == employer_id:
            e['driver_count'] = sum(1 for d in drivers if d['employer_id'] == employer_id and d['active'])
    _save(EMPLOYERS_FILE, employers)

    return {
        'message': f'Driver {first_name} {last_name} registered',
        'driver_id': driver['id'],
        'action_required': 'Run pre-employment query before this driver begins safety-sensitive duty.',
        'driver': driver,
    }


def get_driver(driver_id: str) -> Optional[dict]:
    drivers = _load(DRIVERS_FILE)
    for d in drivers:
        if d['id'] == driver_id:
            return d
    return None


def get_employer_drivers(employer_id: str, active_only: bool = True) -> List[dict]:
    drivers = _load(DRIVERS_FILE)
    return [d for d in drivers if d['employer_id'] == employer_id and (not active_only or d['active'])]


def terminate_driver(driver_id: str, termination_date: str = None) -> dict:
    """Mark driver as inactive (terminated or transferred)."""
    drivers = _load(DRIVERS_FILE)
    for d in drivers:
        if d['id'] == driver_id:
            d['active'] = False
            d['termination_date'] = termination_date or date.today().isoformat()
            _save(DRIVERS_FILE, drivers)
            return {'message': f'Driver {d["full_name"]} marked inactive', 'driver': d}
    return {'error': f'Driver {driver_id} not found'}


# ═══════════════════════════════════════════════════════════════════
# QUERY MANAGEMENT
# ═══════════════════════════════════════════════════════════════════

def record_query(
    driver_id: str,
    employer_id: str,
    query_type: str,
    result_status: str,
    query_date: str = None,
    consent_obtained: bool = False,
    notes: str = ''
) -> dict:
    """
    Record a completed Clearinghouse query.

    query_type:    PRE_EMPLOYMENT | ANNUAL | LIMITED | FULL
    result_status: NOT_PROHIBITED | PROHIBITED | PENDING_RTD
    """
    if query_type not in QUERY_TYPES:
        return {'error': f'Invalid query type. Must be one of: {list(QUERY_TYPES.keys())}'}

    if result_status not in DRIVER_STATUSES:
        return {'error': f'Invalid status. Must be one of: {DRIVER_STATUSES}'}

    queries = _load(QUERIES_FILE)
    today = date.today()
    qdate = datetime.strptime(query_date, '%Y-%m-%d').date() if query_date else today

    query = {
        'id':                _new_id('QRY'),
        'driver_id':         driver_id,
        'employer_id':       employer_id,
        'query_type':        query_type,
        'query_type_label':  QUERY_TYPES[query_type],
        'query_date':        qdate.isoformat(),
        'result_status':     result_status,
        'consent_obtained':  consent_obtained,
        'notes':             notes,
        'recorded_at':       datetime.now().isoformat(),
        'recorded_by':       'PRISM/DDI',
    }

    queries.append(query)
    _save(QUERIES_FILE, queries)

    # Update driver record
    drivers = _load(DRIVERS_FILE)
    next_annual = _add_business_days(qdate, 0)  # start from query date
    next_annual_date = date(qdate.year + 1, qdate.month, qdate.day)

    for d in drivers:
        if d['id'] == driver_id:
            d['clearinghouse_status'] = result_status
            d['last_query_date'] = qdate.isoformat()
            d['last_query_type'] = query_type
            d['annual_query_due'] = next_annual_date.isoformat()

            if query_type == 'PRE_EMPLOYMENT':
                d['pre_employment_done'] = True
                d['pre_employment_date'] = qdate.isoformat()

            if result_status == 'PROHIBITED':
                d['prohibited'] = True
                d['prohibited_since'] = qdate.isoformat()
            elif result_status == 'NOT_PROHIBITED':
                d['prohibited'] = False

    _save(DRIVERS_FILE, drivers)

    response = {
        'message': f'{query_type} query recorded',
        'query_id': query['id'],
        'result': result_status,
        'next_annual_query_due': next_annual_date.isoformat(),
        'query': query,
    }

    if result_status == 'PROHIBITED':
        response['alert'] = (
            'DRIVER IS PROHIBITED. Must not perform safety-sensitive functions. '
            'Driver must complete RTD process before returning to duty. '
            'Contact SAP immediately.'
        )

    return response


def get_annual_queries_due(days_ahead: int = 30) -> List[dict]:
    """
    Return all drivers whose annual Clearinghouse query is due within N days.
    Sorted by urgency (soonest first).
    """
    drivers = _load(DRIVERS_FILE)
    today = date.today()
    cutoff = today + timedelta(days=days_ahead)
    due = []

    for d in drivers:
        if not d['active']:
            continue
        if not d.get('annual_query_due'):
            # Never queried — flag as overdue
            due.append({
                'driver_id':     d['id'],
                'driver_name':   d['full_name'],
                'employer_id':   d['employer_id'],
                'cdl_number':    d['cdl_number'],
                'cdl_state':     d['cdl_state'],
                'due_date':      'OVERDUE — never queried',
                'days_until_due': -999,
                'urgency':       'OVERDUE',
                'action':        'Run ANNUAL query immediately at clearinghouse.fmcsa.dot.gov',
            })
        else:
            due_date = datetime.strptime(d['annual_query_due'], '%Y-%m-%d').date()
            if due_date <= cutoff:
                days_left = (due_date - today).days
                urgency = 'OVERDUE' if days_left < 0 else 'CRITICAL' if days_left <= 7 else 'WARNING'
                due.append({
                    'driver_id':      d['id'],
                    'driver_name':    d['full_name'],
                    'employer_id':    d['employer_id'],
                    'cdl_number':     d['cdl_number'],
                    'cdl_state':      d['cdl_state'],
                    'due_date':       due_date.isoformat(),
                    'days_until_due': days_left,
                    'last_query':     d.get('last_query_date'),
                    'urgency':        urgency,
                    'action':         (
                        f'Run ANNUAL query at clearinghouse.fmcsa.dot.gov for '
                        f'{d["full_name"]} (CDL {d["cdl_number"]}/{d["cdl_state"]})'
                    ),
                })

    due.sort(key=lambda x: x['days_until_due'])
    return due


# ═══════════════════════════════════════════════════════════════════
# VIOLATION REPORTING
# ═══════════════════════════════════════════════════════════════════

def report_violation(
    driver_id: str,
    employer_id: str,
    violation_type: str,
    violation_date: str,
    test_result_received_date: str,
    mro_name: str = '',
    lab_name: str = '',
    substance: str = '',
    alcohol_concentration: float = None,
    notes: str = ''
) -> dict:
    """
    Log a violation that must be reported to the FMCSA Clearinghouse.

    DEADLINE: Close of 3rd business day after employer receives the information.
    violation_date:              Date of the test / incident
    test_result_received_date:   Date employer (or DDI as C/TPA) received confirmed result
    """
    if violation_type not in VIOLATION_TYPES:
        return {'error': f'Invalid violation type. Must be one of: {list(VIOLATION_TYPES.keys())}'}

    received_date = datetime.strptime(test_result_received_date, '%Y-%m-%d').date()
    report_deadline = _add_business_days(received_date, 3)
    today = date.today()
    days_to_deadline = (report_deadline - today).days

    violations = _load(VIOLATIONS_FILE)

    violation = {
        'id':                         _new_id('VIO'),
        'driver_id':                  driver_id,
        'employer_id':                employer_id,
        'violation_type':             violation_type,
        'violation_type_label':       VIOLATION_TYPES[violation_type],
        'violation_date':             violation_date,
        'result_received_date':       test_result_received_date,
        'report_deadline':            report_deadline.isoformat(),
        'days_until_deadline':        days_to_deadline,
        'mro_name':                   mro_name,
        'lab_name':                   lab_name,
        'substance':                  substance,
        'alcohol_concentration':      alcohol_concentration,
        'notes':                      notes,
        'reported_to_clearinghouse':  False,
        'reported_date':              None,
        'clearinghouse_confirmation': None,
        'status':                     'PENDING_REPORT',
        'logged_at':                  datetime.now().isoformat(),
    }

    violations.append(violation)
    _save(VIOLATIONS_FILE, violations)

    # Mark driver as prohibited
    drivers = _load(DRIVERS_FILE)
    for d in drivers:
        if d['id'] == driver_id:
            d['prohibited'] = True
            d['prohibited_since'] = violation_date
            d['clearinghouse_status'] = 'PROHIBITED'
            d['violations'].append(violation['id'])
    _save(DRIVERS_FILE, drivers)

    urgency = 'OVERDUE' if days_to_deadline < 0 else 'CRITICAL' if days_to_deadline <= 1 else 'URGENT'

    return {
        'message':        'Violation logged. Report to Clearinghouse required.',
        'violation_id':   violation['id'],
        'report_deadline': report_deadline.isoformat(),
        'days_remaining': days_to_deadline,
        'urgency':        urgency,
        'action': (
            f'Log into clearinghouse.fmcsa.dot.gov → Report a Violation. '
            f'Select employer {employer_id}. Enter driver CDL info. '
            f'Select violation type: {VIOLATION_TYPES[violation_type]}. '
            f'DEADLINE: {report_deadline.isoformat()} (3 business days from result received).'
        ),
        'violation': violation,
    }


def confirm_violation_reported(violation_id: str, reported_date: str = None, confirmation_number: str = '') -> dict:
    """Mark a violation as successfully reported to the Clearinghouse."""
    violations = _load(VIOLATIONS_FILE)
    for v in violations:
        if v['id'] == violation_id:
            v['reported_to_clearinghouse'] = True
            v['reported_date'] = reported_date or date.today().isoformat()
            v['clearinghouse_confirmation'] = confirmation_number
            v['status'] = 'REPORTED'
            _save(VIOLATIONS_FILE, violations)
            return {
                'message': 'Violation marked as reported to Clearinghouse',
                'next_step': (
                    'Driver is in PROHIBITED status. '
                    'Refer driver to a qualified SAP. '
                    'Do not allow driver to perform safety-sensitive functions.'
                ),
                'violation': v,
            }
    return {'error': f'Violation {violation_id} not found'}


def get_pending_violations() -> List[dict]:
    """Return all violations not yet reported to the Clearinghouse, sorted by deadline."""
    violations = _load(VIOLATIONS_FILE)
    today = date.today()
    pending = []

    for v in violations:
        if not v.get('reported_to_clearinghouse'):
            deadline = datetime.strptime(v['report_deadline'], '%Y-%m-%d').date()
            days_left = (deadline - today).days
            v['days_until_deadline'] = days_left
            v['urgency'] = 'OVERDUE' if days_left < 0 else 'CRITICAL' if days_left <= 1 else 'URGENT' if days_left <= 3 else 'DUE_SOON'
            pending.append(v)

    pending.sort(key=lambda x: x['days_until_deadline'])
    return pending


# ═══════════════════════════════════════════════════════════════════
# RETURN TO DUTY (RTD) TRACKING
# ═══════════════════════════════════════════════════════════════════

def open_rtd_case(
    driver_id: str,
    employer_id: str,
    violation_id: str,
    sap_name: str = '',
    sap_credentials: str = '',
    initial_evaluation_date: str = None,
    notes: str = ''
) -> dict:
    """
    Open a Return-to-Duty case for a prohibited driver.

    RTD Process (49 CFR Part 40 Subpart O):
    1. Driver referred to qualified SAP
    2. SAP initial evaluation
    3. SAP-prescribed education/treatment
    4. SAP follow-up evaluation (determines RTD readiness)
    5. Employer-ordered RTD test (negative result required)
    6. DDI reports negative RTD test to Clearinghouse
    7. Driver may return to safety-sensitive duty
    8. Follow-up testing plan begins (minimum 6 tests, 12 months)
    """
    rtd_records = _load(RTD_FILE)

    rtd = {
        'id':                       _new_id('RTD'),
        'driver_id':                driver_id,
        'employer_id':              employer_id,
        'violation_id':             violation_id,
        'sap_name':                 sap_name,
        'sap_credentials':          sap_credentials,
        'initial_evaluation_date':  initial_evaluation_date,
        'treatment_plan':           '',
        'follow_up_evaluation_date': None,
        'rtd_test_ordered_date':    None,
        'rtd_test_completed_date':  None,
        'rtd_test_result':          None,
        'reported_to_clearinghouse': False,
        'clearinghouse_reported_date': None,
        'rtd_complete':             False,
        'rtd_complete_date':        None,
        'follow_up_plan_start':     None,
        'notes':                    notes,
        'opened_at':                datetime.now().isoformat(),
        'status':                   'SAP_EVALUATION',
        'steps_completed': [],
        'steps_pending': [
            'SAP initial evaluation',
            'SAP-prescribed education/treatment',
            'SAP follow-up evaluation',
            'Employer-ordered RTD test',
            'Report negative RTD test to Clearinghouse',
            'Driver returned to duty',
            'Follow-up testing plan initiated',
        ],
    }

    rtd_records.append(rtd)
    _save(RTD_FILE, rtd_records)

    # Update driver RTD status
    drivers = _load(DRIVERS_FILE)
    for d in drivers:
        if d['id'] == driver_id:
            d['rtd_status'] = 'IN_PROGRESS'
            d['clearinghouse_status'] = 'PENDING_RTD'
    _save(DRIVERS_FILE, drivers)

    return {
        'message':  'RTD case opened',
        'rtd_id':   rtd['id'],
        'next_step': 'Driver must be evaluated by a qualified SAP before any treatment begins.',
        'sap_resources': 'FMCSA SAP registry: https://www.saplist.com or search FMCSA.dot.gov for certified SAPs',
        'rtd': rtd,
    }


def update_rtd_status(rtd_id: str, update: dict) -> dict:
    """
    Update an RTD case with new progress.

    Accepted update keys:
    - sap_name, sap_credentials
    - initial_evaluation_date
    - treatment_plan
    - follow_up_evaluation_date
    - rtd_test_ordered_date
    - rtd_test_completed_date
    - rtd_test_result ('NEGATIVE' or 'POSITIVE')
    - reported_to_clearinghouse (bool)
    - clearinghouse_reported_date
    - notes
    """
    rtd_records = _load(RTD_FILE)
    for rtd in rtd_records:
        if rtd['id'] == rtd_id:
            for key, val in update.items():
                if key in rtd:
                    rtd[key] = val

            # Auto-advance status
            if update.get('rtd_test_result') == 'NEGATIVE' and not rtd.get('reported_to_clearinghouse'):
                rtd['status'] = 'RTD_TEST_NEGATIVE_PENDING_REPORT'
                rtd['steps_completed'].append('RTD test completed — negative result')

            if update.get('reported_to_clearinghouse') and update.get('rtd_test_result') == 'NEGATIVE':
                rtd['status'] = 'CLEARED'
                rtd['rtd_complete'] = True
                rtd['rtd_complete_date'] = date.today().isoformat()
                rtd['follow_up_plan_start'] = date.today().isoformat()
                rtd['steps_completed'].append('Reported negative RTD result to Clearinghouse')
                rtd['steps_completed'].append('Driver cleared — returned to duty')

                # Update driver status
                drivers = _load(DRIVERS_FILE)
                for d in drivers:
                    if d['id'] == rtd['driver_id']:
                        d['prohibited'] = False
                        d['rtd_status'] = 'COMPLETE'
                        d['clearinghouse_status'] = 'NOT_PROHIBITED'
                _save(DRIVERS_FILE, drivers)

            _save(RTD_FILE, rtd_records)

            response = {'message': 'RTD case updated', 'rtd': rtd}

            if rtd['status'] == 'RTD_TEST_NEGATIVE_PENDING_REPORT':
                response['action'] = (
                    'REPORT RTD RESULT TO CLEARINGHOUSE NOW: '
                    'Log into clearinghouse.fmcsa.dot.gov → Report RTD Information. '
                    'Enter the negative RTD test result. '
                    'Driver cannot return to duty until this is reported.'
                )

            if rtd['status'] == 'CLEARED':
                response['next_step'] = (
                    f'Driver {rtd["driver_id"]} cleared for duty. '
                    f'Begin follow-up testing plan immediately. '
                    f'Minimum 6 follow-up tests required in the next 12 months.'
                )

            return response

    return {'error': f'RTD case {rtd_id} not found'}


# ═══════════════════════════════════════════════════════════════════
# FOLLOW-UP TESTING SCHEDULE (49 CFR §40.307)
# ═══════════════════════════════════════════════════════════════════

def create_followup_plan(
    driver_id: str,
    employer_id: str,
    rtd_id: str,
    rtd_date: str,
    num_tests: int = 6,
    plan_months: int = 12,
    sap_prescribed_additional: bool = False,
    notes: str = ''
) -> dict:
    """
    Create a follow-up testing plan per 49 CFR §40.307.

    MINIMUMS (SAP may require more):
    - At least 6 tests in first 12 months after RTD
    - May extend up to 5 years
    - Tests must be unannounced
    - Frequency determined by SAP
    - DDI manages the schedule as C/TPA
    """
    rtd_start = datetime.strptime(rtd_date, '%Y-%m-%d').date()
    plan_end = date(rtd_start.year + (plan_months // 12), rtd_start.month, rtd_start.day)

    followup = _load(FOLLOWUP_FILE)

    # Generate evenly-spaced test schedule
    total_days = (plan_end - rtd_start).days
    interval = total_days // num_tests
    tests = []
    for i in range(1, num_tests + 1):
        scheduled_date = rtd_start + timedelta(days=interval * i)
        tests.append({
            'test_number':      i,
            'scheduled_window': scheduled_date.isoformat(),
            'completed':        False,
            'completed_date':   None,
            'result':           None,
            'order_id':         None,
            'notified':         False,
        })

    plan = {
        'id':                        _new_id('FUP'),
        'driver_id':                 driver_id,
        'employer_id':               employer_id,
        'rtd_id':                    rtd_id,
        'rtd_date':                  rtd_date,
        'plan_start':                rtd_date,
        'plan_end':                  plan_end.isoformat(),
        'num_tests_required':        num_tests,
        'num_tests_completed':       0,
        'plan_months':               plan_months,
        'sap_prescribed_additional': sap_prescribed_additional,
        'tests':                     tests,
        'notes':                     notes,
        'active':                    True,
        'completed':                 False,
        'created_at':                datetime.now().isoformat(),
    }

    followup.append(plan)
    _save(FOLLOWUP_FILE, followup)

    return {
        'message':           f'Follow-up testing plan created — {num_tests} tests over {plan_months} months',
        'plan_id':           plan['id'],
        'plan_end':          plan_end.isoformat(),
        'first_test_window': tests[0]['scheduled_window'] if tests else None,
        'reminder':          'All follow-up tests must be UNANNOUNCED. Notify driver same day test is ordered.',
        'plan':              plan,
    }


def record_followup_test(plan_id: str, test_number: int, completed_date: str, result: str, order_id: str = '') -> dict:
    """Mark a follow-up test as completed."""
    followup = _load(FOLLOWUP_FILE)
    for plan in followup:
        if plan['id'] == plan_id:
            for test in plan['tests']:
                if test['test_number'] == test_number:
                    test['completed'] = True
                    test['completed_date'] = completed_date
                    test['result'] = result
                    test['order_id'] = order_id
                    plan['num_tests_completed'] += 1
                    break

            if plan['num_tests_completed'] >= plan['num_tests_required']:
                plan['completed'] = True
                plan['active'] = False

            _save(FOLLOWUP_FILE, followup)

            response = {
                'message':        f'Follow-up test {test_number} recorded',
                'tests_completed': plan['num_tests_completed'],
                'tests_required':  plan['num_tests_required'],
                'result':          result,
                'plan_complete':   plan['completed'],
            }

            if result == 'POSITIVE':
                response['alert'] = (
                    'POSITIVE follow-up test. Driver is again PROHIBITED. '
                    'Report to FMCSA Clearinghouse within 3 business days. '
                    'Driver must restart RTD process from the beginning.'
                )

            return response

    return {'error': f'Follow-up plan {plan_id} not found'}


def get_followup_tests_due(days_ahead: int = 14) -> List[dict]:
    """Return follow-up tests due within the next N days."""
    followup = _load(FOLLOWUP_FILE)
    today = date.today()
    cutoff = today + timedelta(days=days_ahead)
    due = []

    for plan in followup:
        if not plan['active']:
            continue
        for test in plan['tests']:
            if test['completed']:
                continue
            try:
                window = datetime.strptime(test['scheduled_window'], '%Y-%m-%d').date()
            except Exception:
                continue
            if window <= cutoff:
                days_left = (window - today).days
                due.append({
                    'plan_id':       plan['id'],
                    'driver_id':     plan['driver_id'],
                    'employer_id':   plan['employer_id'],
                    'test_number':   test['test_number'],
                    'scheduled':     test['scheduled_window'],
                    'days_until':    days_left,
                    'urgency':       'OVERDUE' if days_left < 0 else 'THIS_WEEK' if days_left <= 7 else 'UPCOMING',
                    'action':        (
                        f'Order unannounced follow-up test for driver {plan["driver_id"]}. '
                        f'Test #{test["test_number"]} of {plan["num_tests_required"]}.'
                    ),
                })

    due.sort(key=lambda x: x['days_until'])
    return due


# ═══════════════════════════════════════════════════════════════════
# ACTION QUEUE — DAILY CLEARINGHOUSE TO-DO LIST
# ═══════════════════════════════════════════════════════════════════

def build_action_queue() -> dict:
    """
    Generate today's complete Clearinghouse action queue.
    This is what DDI staff opens every morning before anything else.
    """
    today = date.today()

    # 1. Violations pending report (sorted by deadline)
    pending_violations = get_pending_violations()

    # 2. Annual queries due within 30 days
    queries_due = get_annual_queries_due(days_ahead=30)

    # 3. Pre-employment queries needed (active drivers, no pre-employment done)
    drivers = _load(DRIVERS_FILE)
    preemployment_needed = [
        {
            'driver_id':   d['id'],
            'driver_name': d['full_name'],
            'employer_id': d['employer_id'],
            'hire_date':   d['hire_date'],
            'cdl_number':  d['cdl_number'],
            'cdl_state':   d['cdl_state'],
            'action':      (
                f'Run PRE-EMPLOYMENT query at clearinghouse.fmcsa.dot.gov for '
                f'{d["full_name"]} (CDL {d["cdl_number"]}/{d["cdl_state"]}). '
                f'Must complete before driver begins safety-sensitive duty.'
            ),
        }
        for d in drivers if d['active'] and not d.get('pre_employment_done')
    ]

    # 4. Follow-up tests due within 14 days
    followup_due = get_followup_tests_due(days_ahead=14)

    # 5. RTD tests pending Clearinghouse report
    rtd_records = _load(RTD_FILE)
    rtd_pending_report = [
        r for r in rtd_records
        if r.get('rtd_test_result') == 'NEGATIVE' and not r.get('reported_to_clearinghouse')
    ]

    # 6. Employer authorization missing
    employers = _load(EMPLOYERS_FILE)
    unauthorized_employers = [
        e for e in employers if e['status'] == 'ACTIVE' and not e.get('clearinghouse_authorized')
    ]

    # Build priority order
    critical = []
    warning = []
    routine = []

    for v in pending_violations:
        item = {
            'type':     'VIOLATION_REPORT',
            'priority': 'CRITICAL' if v['days_until_deadline'] <= 1 else 'URGENT',
            'deadline': v['report_deadline'],
            'summary':  f'Report {v["violation_type_label"]} for driver {v["driver_id"]}',
            'action':   v.get('action', 'Report violation at clearinghouse.fmcsa.dot.gov'),
            'id':       v['id'],
        }
        critical.append(item) if v['days_until_deadline'] <= 1 else warning.append(item)

    for r in rtd_pending_report:
        critical.append({
            'type':     'RTD_REPORT',
            'priority': 'CRITICAL',
            'deadline': 'IMMEDIATE',
            'summary':  f'Report negative RTD result for driver {r["driver_id"]}',
            'action':   'Log into clearinghouse.fmcsa.dot.gov → Report RTD Information',
            'id':       r['id'],
        })

    for p in preemployment_needed:
        critical.append({
            'type':     'PRE_EMPLOYMENT_QUERY',
            'priority': 'CRITICAL',
            'deadline': 'Before safety-sensitive duty',
            'summary':  f'Pre-employment query needed: {p["driver_name"]}',
            'action':   p['action'],
            'id':       p['driver_id'],
        })

    for q in queries_due:
        item = {
            'type':     'ANNUAL_QUERY',
            'priority': q['urgency'],
            'deadline': q.get('due_date', 'OVERDUE'),
            'summary':  f'Annual query due: {q["driver_name"]}',
            'action':   q['action'],
            'id':       q['driver_id'],
        }
        warning.append(item) if q['urgency'] in ('WARNING', 'UPCOMING') else critical.append(item)

    for f in followup_due:
        item = {
            'type':     'FOLLOWUP_TEST',
            'priority': f['urgency'],
            'deadline': f['scheduled'],
            'summary':  f'Follow-up test due: driver {f["driver_id"]} (test #{f["test_number"]})',
            'action':   f['action'],
            'id':       f['plan_id'],
        }
        warning.append(item)

    for e in unauthorized_employers:
        routine.append({
            'type':     'EMPLOYER_AUTHORIZATION',
            'priority': 'ROUTINE',
            'deadline': 'ASAP',
            'summary':  f'Clearinghouse authorization needed: {e["employer_name"]}',
            'action':   (
                f'Have {e["employer_name"]} log into clearinghouse.fmcsa.dot.gov '
                f'and designate Dee Davis Inc. as their C/TPA with full authorization.'
            ),
            'id':       e['id'],
        })

    return {
        'generated_at':     datetime.now().isoformat(),
        'date':             today.isoformat(),
        'clearinghouse_url': 'https://clearinghouse.fmcsa.dot.gov',
        'total_actions':    len(critical) + len(warning) + len(routine),
        'critical':         critical,
        'warning':          warning,
        'routine':          routine,
        'summary': {
            'violations_pending_report':   len(pending_violations),
            'annual_queries_due_30_days':  len(queries_due),
            'preemployment_queries_needed': len(preemployment_needed),
            'followup_tests_due_14_days':  len(followup_due),
            'rtd_results_pending_report':  len(rtd_pending_report),
            'employers_not_authorized':    len(unauthorized_employers),
        },
    }


# ═══════════════════════════════════════════════════════════════════
# MIS ANNUAL REPORT DATA
# ═══════════════════════════════════════════════════════════════════

def generate_mis_data(employer_id: str, report_year: int) -> dict:
    """
    Generate DOT MIS (Management Information System) report data
    for a given employer and year.

    Employers must submit MIS data to their DOT modal agency annually.
    As C/TPA, DDI compiles this data.
    """
    queries = _load(QUERIES_FILE)
    violations = _load(VIOLATIONS_FILE)
    drivers = _load(DRIVERS_FILE)
    rtd_records = _load(RTD_FILE)

    # Filter to this employer and year
    emp_drivers = [d for d in drivers if d['employer_id'] == employer_id]
    driver_ids = {d['id'] for d in emp_drivers}

    def in_year(date_str):
        try:
            return datetime.strptime(date_str[:10], '%Y-%m-%d').year == report_year
        except Exception:
            return False

    emp_queries = [q for q in queries if q['employer_id'] == employer_id and in_year(q['query_date'])]
    emp_violations = [v for v in violations if v['employer_id'] == employer_id and in_year(v['violation_date'])]
    emp_rtd = [r for r in rtd_records if r['employer_id'] == employer_id]

    pre_employment_queries = [q for q in emp_queries if q['query_type'] == 'PRE_EMPLOYMENT']
    annual_queries = [q for q in emp_queries if q['query_type'] == 'ANNUAL']
    prohibited_results = [q for q in emp_queries if q['result_status'] == 'PROHIBITED']

    return {
        'employer_id':         employer_id,
        'report_year':         report_year,
        'generated_at':        datetime.now().isoformat(),
        'ctpa':                'Dee Davis Inc. — C/TPA',
        'ctpa_cage':           '8UMX3',
        'driver_count':        len(emp_drivers),
        'active_drivers':      len([d for d in emp_drivers if d['active']]),
        'queries': {
            'pre_employment_total':    len(pre_employment_queries),
            'annual_total':            len(annual_queries),
            'total_queries':           len(emp_queries),
            'prohibited_found':        len(prohibited_results),
        },
        'violations': {
            'total':                   len(emp_violations),
            'positive_drug':           len([v for v in emp_violations if v['violation_type'] == 'POSITIVE_DRUG']),
            'positive_alcohol':        len([v for v in emp_violations if v['violation_type'] == 'POSITIVE_ALCOHOL']),
            'refusals':                len([v for v in emp_violations if 'REFUSAL' in v['violation_type']]),
            'reported_on_time':        len([v for v in emp_violations if v.get('reported_to_clearinghouse')]),
        },
        'return_to_duty': {
            'cases_opened':    len([r for r in emp_rtd if in_year(r['opened_at'])]),
            'cases_cleared':   len([r for r in emp_rtd if r.get('rtd_complete') and in_year(r.get('rtd_complete_date', ''))]),
            'cases_pending':   len([r for r in emp_rtd if not r.get('rtd_complete')]),
        },
        'compliance_notes': (
            'Data compiled by Dee Davis Inc. as registered C/TPA. '
            'Submit to DOT modal agency (FMCSA for trucking) by March 15 of the following year.'
        ),
    }


# ═══════════════════════════════════════════════════════════════════
# STATS / DASHBOARD
# ═══════════════════════════════════════════════════════════════════

def get_dashboard() -> dict:
    """Summary dashboard for all Clearinghouse activity."""
    employers = _load(EMPLOYERS_FILE)
    drivers = _load(DRIVERS_FILE)
    queries = _load(QUERIES_FILE)
    violations = _load(VIOLATIONS_FILE)
    rtd_records = _load(RTD_FILE)
    followup = _load(FOLLOWUP_FILE)

    prohibited_drivers = [d for d in drivers if d['active'] and d.get('prohibited')]
    pending_violations = get_pending_violations()
    queries_due_30 = get_annual_queries_due(30)
    followup_due_14 = get_followup_tests_due(14)

    return {
        'generated_at':           datetime.now().isoformat(),
        'employers': {
            'total':              len(employers),
            'authorized':         len([e for e in employers if e.get('clearinghouse_authorized')]),
            'pending_auth':       len([e for e in employers if not e.get('clearinghouse_authorized')]),
        },
        'drivers': {
            'total_active':       len([d for d in drivers if d['active']]),
            'prohibited':         len(prohibited_drivers),
            'in_rtd_process':     len([d for d in drivers if d.get('rtd_status') == 'IN_PROGRESS']),
            'no_pre_employment':  len([d for d in drivers if d['active'] and not d.get('pre_employment_done')]),
        },
        'violations': {
            'total_logged':       len(violations),
            'pending_report':     len(pending_violations),
            'overdue':            len([v for v in pending_violations if v.get('days_until_deadline', 0) < 0]),
        },
        'queries': {
            'total_run':          len(queries),
            'annual_due_30_days': len(queries_due_30),
        },
        'followup': {
            'active_plans':       len([p for p in followup if p['active']]),
            'tests_due_14_days':  len(followup_due_14),
        },
        'action_items': len(pending_violations) + len([d for d in drivers if d['active'] and not d.get('pre_employment_done')]) + len(queries_due_30),
    }


# ═══════════════════════════════════════════════════════════════════
# API ROUTES
# ═══════════════════════════════════════════════════════════════════

@prism_clearinghouse.route('/prism/clearinghouse/dashboard', methods=['GET'])
def api_dashboard():
    """Full Clearinghouse compliance dashboard."""
    return jsonify(get_dashboard())


@prism_clearinghouse.route('/prism/clearinghouse/action-queue', methods=['GET'])
def api_action_queue():
    """Today's Clearinghouse action queue — what DDI needs to do RIGHT NOW."""
    return jsonify(build_action_queue())


# --- Employer Routes ---

@prism_clearinghouse.route('/prism/clearinghouse/employers', methods=['GET'])
def api_list_employers():
    employers = _load(EMPLOYERS_FILE)
    return jsonify({'employers': employers, 'count': len(employers)})


@prism_clearinghouse.route('/prism/clearinghouse/employers', methods=['POST'])
def api_register_employer():
    data = request.get_json() or {}
    required = ['employer_name', 'dot_number', 'contact_name', 'contact_email', 'contact_phone']
    for field in required:
        if not data.get(field):
            return jsonify({'error': f'Missing required field: {field}'}), 400
    result = register_employer(**{k: data[k] for k in required}, **{k: data.get(k, '') for k in ['dot_authority', 'notes']})
    return jsonify(result), 201


@prism_clearinghouse.route('/prism/clearinghouse/employers/<employer_id>/authorize', methods=['POST'])
def api_confirm_authorization(employer_id):
    data = request.get_json() or {}
    functions = data.get('functions', ['Report Violations', 'Report RTD Information', 'Conduct Queries'])
    return jsonify(confirm_employer_authorization(employer_id, functions))


# --- Driver Routes ---

@prism_clearinghouse.route('/prism/clearinghouse/drivers', methods=['GET'])
def api_list_drivers():
    employer_id = request.args.get('employer_id')
    active_only = request.args.get('active_only', 'true').lower() == 'true'
    drivers = _load(DRIVERS_FILE)
    if employer_id:
        drivers = [d for d in drivers if d['employer_id'] == employer_id]
    if active_only:
        drivers = [d for d in drivers if d['active']]
    return jsonify({'drivers': drivers, 'count': len(drivers)})


@prism_clearinghouse.route('/prism/clearinghouse/drivers', methods=['POST'])
def api_register_driver():
    data = request.get_json() or {}
    required = ['employer_id', 'first_name', 'last_name', 'cdl_number', 'cdl_state', 'date_of_birth']
    for field in required:
        if not data.get(field):
            return jsonify({'error': f'Missing required field: {field}'}), 400
    result = register_driver(**{k: data[k] for k in required}, **{k: data.get(k, '') for k in ['hire_date', 'notes']})
    return jsonify(result), 201


@prism_clearinghouse.route('/prism/clearinghouse/drivers/<driver_id>', methods=['GET'])
def api_get_driver(driver_id):
    driver = get_driver(driver_id)
    if not driver:
        return jsonify({'error': 'Driver not found'}), 404
    return jsonify(driver)


@prism_clearinghouse.route('/prism/clearinghouse/drivers/<driver_id>/terminate', methods=['POST'])
def api_terminate_driver(driver_id):
    data = request.get_json() or {}
    return jsonify(terminate_driver(driver_id, data.get('termination_date')))


# --- Query Routes ---

@prism_clearinghouse.route('/prism/clearinghouse/queries', methods=['POST'])
def api_record_query():
    data = request.get_json() or {}
    required = ['driver_id', 'employer_id', 'query_type', 'result_status']
    for field in required:
        if not data.get(field):
            return jsonify({'error': f'Missing required field: {field}'}), 400
    result = record_query(
        driver_id=data['driver_id'],
        employer_id=data['employer_id'],
        query_type=data['query_type'],
        result_status=data['result_status'],
        query_date=data.get('query_date'),
        consent_obtained=data.get('consent_obtained', False),
        notes=data.get('notes', ''),
    )
    return jsonify(result), 201


@prism_clearinghouse.route('/prism/clearinghouse/queries/annual-due', methods=['GET'])
def api_annual_queries_due():
    days = int(request.args.get('days', 30))
    return jsonify({'due': get_annual_queries_due(days), 'days_ahead': days})


@prism_clearinghouse.route('/prism/clearinghouse/queries/types', methods=['GET'])
def api_query_types():
    return jsonify(QUERY_TYPES)


# --- Violation Routes ---

@prism_clearinghouse.route('/prism/clearinghouse/violations', methods=['POST'])
def api_report_violation():
    data = request.get_json() or {}
    required = ['driver_id', 'employer_id', 'violation_type', 'violation_date', 'test_result_received_date']
    for field in required:
        if not data.get(field):
            return jsonify({'error': f'Missing required field: {field}'}), 400
    result = report_violation(
        driver_id=data['driver_id'],
        employer_id=data['employer_id'],
        violation_type=data['violation_type'],
        violation_date=data['violation_date'],
        test_result_received_date=data['test_result_received_date'],
        mro_name=data.get('mro_name', ''),
        lab_name=data.get('lab_name', ''),
        substance=data.get('substance', ''),
        alcohol_concentration=data.get('alcohol_concentration'),
        notes=data.get('notes', ''),
    )
    return jsonify(result), 201


@prism_clearinghouse.route('/prism/clearinghouse/violations/pending', methods=['GET'])
def api_pending_violations():
    return jsonify({'pending': get_pending_violations(), 'count': len(get_pending_violations())})


@prism_clearinghouse.route('/prism/clearinghouse/violations/<violation_id>/confirm-reported', methods=['POST'])
def api_confirm_violation_reported(violation_id):
    data = request.get_json() or {}
    return jsonify(confirm_violation_reported(
        violation_id,
        reported_date=data.get('reported_date'),
        confirmation_number=data.get('confirmation_number', ''),
    ))


@prism_clearinghouse.route('/prism/clearinghouse/violations/types', methods=['GET'])
def api_violation_types():
    return jsonify(VIOLATION_TYPES)


# --- Return to Duty Routes ---

@prism_clearinghouse.route('/prism/clearinghouse/rtd', methods=['POST'])
def api_open_rtd():
    data = request.get_json() or {}
    required = ['driver_id', 'employer_id', 'violation_id']
    for field in required:
        if not data.get(field):
            return jsonify({'error': f'Missing required field: {field}'}), 400
    result = open_rtd_case(
        driver_id=data['driver_id'],
        employer_id=data['employer_id'],
        violation_id=data['violation_id'],
        sap_name=data.get('sap_name', ''),
        sap_credentials=data.get('sap_credentials', ''),
        initial_evaluation_date=data.get('initial_evaluation_date'),
        notes=data.get('notes', ''),
    )
    return jsonify(result), 201


@prism_clearinghouse.route('/prism/clearinghouse/rtd/<rtd_id>', methods=['PATCH'])
def api_update_rtd(rtd_id):
    data = request.get_json() or {}
    return jsonify(update_rtd_status(rtd_id, data))


@prism_clearinghouse.route('/prism/clearinghouse/rtd', methods=['GET'])
def api_list_rtd():
    rtd_records = _load(RTD_FILE)
    active_only = request.args.get('active_only', 'true').lower() == 'true'
    if active_only:
        rtd_records = [r for r in rtd_records if not r.get('rtd_complete')]
    return jsonify({'rtd_cases': rtd_records, 'count': len(rtd_records)})


# --- Follow-Up Testing Routes ---

@prism_clearinghouse.route('/prism/clearinghouse/followup', methods=['POST'])
def api_create_followup_plan():
    data = request.get_json() or {}
    required = ['driver_id', 'employer_id', 'rtd_id', 'rtd_date']
    for field in required:
        if not data.get(field):
            return jsonify({'error': f'Missing required field: {field}'}), 400
    result = create_followup_plan(
        driver_id=data['driver_id'],
        employer_id=data['employer_id'],
        rtd_id=data['rtd_id'],
        rtd_date=data['rtd_date'],
        num_tests=data.get('num_tests', 6),
        plan_months=data.get('plan_months', 12),
        sap_prescribed_additional=data.get('sap_prescribed_additional', False),
        notes=data.get('notes', ''),
    )
    return jsonify(result), 201


@prism_clearinghouse.route('/prism/clearinghouse/followup/<plan_id>/tests/<int:test_number>', methods=['POST'])
def api_record_followup_test(plan_id, test_number):
    data = request.get_json() or {}
    if not data.get('completed_date') or not data.get('result'):
        return jsonify({'error': 'completed_date and result are required'}), 400
    return jsonify(record_followup_test(plan_id, test_number, data['completed_date'], data['result'], data.get('order_id', '')))


@prism_clearinghouse.route('/prism/clearinghouse/followup/due', methods=['GET'])
def api_followup_due():
    days = int(request.args.get('days', 14))
    return jsonify({'due': get_followup_tests_due(days), 'days_ahead': days})


# --- MIS Report ---

@prism_clearinghouse.route('/prism/clearinghouse/mis-report', methods=['GET'])
def api_mis_report():
    employer_id = request.args.get('employer_id')
    report_year = int(request.args.get('year', datetime.now().year - 1))
    if not employer_id:
        return jsonify({'error': 'employer_id query parameter required'}), 400
    return jsonify(generate_mis_data(employer_id, report_year))
