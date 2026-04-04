#!/usr/bin/env python3
"""
PRISM BAT — BREATH ALCOHOL TESTING WORKFLOW
============================================
DOT-compliant Breath Alcohol Testing (BAT) procedures for PRISM.

Reference: 49 CFR Part 40 Subparts J & K (Alcohol Testing Personnel, Testing)
           DOT_DRUG_TESTING_QUICK_REFERENCE.md — Card 7 (Alcohol Test Results)
           FATAL_FLAW_CHECKLIST.md — Alcohol Test Fatal Flaws

KEY RULES:
- Screening: < 0.02 BrAC = negative (test complete)
- Screening ≥ 0.02: MUST wait minimum 15 minutes, then confirmation on EBT (not ASD)
- Confirmation < 0.02: negative for alcohol
- Confirmation 0.02–0.039: positive (low) — remove from safety-sensitive 8–24 hours
- Confirmation ≥ 0.04: positive (violation) — SAP, Clearinghouse if FMCSA, etc.
- Post-accident alcohol: within 8 hours (2 hours preferred)
- Fatal flaws: EBT not on CPL, air blank ≠ 0.00, no printed result, <15 min between tests, etc.
"""

import json
import os
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from flask import Blueprint, request, jsonify

prism_bat = Blueprint('prism_bat', __name__)

DATA_DIR = os.path.join(os.path.dirname(__file__), 'uploads', 'prism', 'bat')
ORDERS_FILE = os.path.join(DATA_DIR, 'bat_orders.json')


def _ensure():
    os.makedirs(DATA_DIR, exist_ok=True)


def _load_orders() -> list:
    _ensure()
    if os.path.exists(ORDERS_FILE):
        with open(ORDERS_FILE, 'r') as f:
            return json.load(f)
    return []


def _save_orders(orders: list):
    _ensure()
    with open(ORDERS_FILE, 'w') as f:
        json.dump(orders, f, indent=2, default=str)


def _new_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:8].upper()}"


# ═══════════════════════════════════════════════════════════════════
# RESULT INTERPRETATION (49 CFR Part 40 — Card 7)
# ═══════════════════════════════════════════════════════════════════

def interpret_screening(brac: float) -> dict:
    """Initial screening test result."""
    if brac < 0.02:
        return {
            'result': 'NEGATIVE',
            'brac': brac,
            'action': 'Test complete. No confirmation required.',
            'employer_action': 'None — donor may perform safety-sensitive functions.',
        }
    return {
        'result': 'SCREEN_POSITIVE',
        'brac': brac,
        'action': (
            'Screening ≥ 0.02. MUST wait minimum 15 minutes before confirmation test '
            'on EBT. Donor must not eat, drink, smoke, or put anything in mouth during wait.'
        ),
        'next_step': 'START_15_MINUTE_WAIT_THEN_CONFIRMATION',
    }


def interpret_confirmation(brac: float) -> dict:
    """Confirmation test result (after screening ≥ 0.02)."""
    if brac < 0.02:
        return {
            'result': 'NEGATIVE',
            'brac': brac,
            'category': 'negative',
            'action': 'Confirmation negative. Test complete.',
            'employer_action': 'Donor may return to safety-sensitive duties.',
        }
    if brac < 0.04:
        return {
            'result': 'POSITIVE_LOW',
            'brac': brac,
            'category': 'positive_low',
            'range': '0.02 – 0.039',
            'action': (
                'Positive (low). Remove from safety-sensitive duties for 8–24 hours '
                'per employer policy. Not always a DOT “violation” depending on mode — '
                'verify employer policy and modal rules.'
            ),
            'employer_action': 'Remove from safety-sensitive duties. Document.',
            'clearinghouse': 'May not require Clearinghouse report — confirm modal rules.',
        }
    return {
        'result': 'POSITIVE_VIOLATION',
        'brac': brac,
        'category': 'positive_violation',
        'range': '≥ 0.04',
        'action': (
            'Positive alcohol test (≥ 0.04). DOT violation. Remove from safety-sensitive '
            'duties immediately. SAP evaluation required. Report to FMCSA Clearinghouse if applicable.'
        ),
        'employer_action': 'Immediate removal, SAP referral, document violation.',
        'clearinghouse': 'Report to FMCSA Clearinghouse within 3 business days if FMCSA-regulated.',
    }


# ═══════════════════════════════════════════════════════════════════
# BAT PROCEDURE — MASTER CHECKLIST
# ═══════════════════════════════════════════════════════════════════

BAT_PROCEDURE_STEPS = [
    {
        'step': 1,
        'phase': 'PRE_TEST',
        'name': 'Verify EBT Device',
        'instruction': (
            'Confirm device is an Evidentiary Breath Testing (EBT) device on the '
            'NHTSA Conforming Products List (CPL). Record make, model, and serial number on ATF.'
        ),
        'fatal_if_failed': True,
        'fatal_note': 'EBT not on CPL = invalid test',
    },
    {
        'step': 2,
        'phase': 'PRE_TEST',
        'name': 'Air Blank',
        'instruction': (
            'Perform air blank per device instructions. Air blank MUST read 0.00 before '
            'screening test. If not 0.00, do not proceed — device error.'
        ),
        'fatal_if_failed': True,
        'fatal_note': 'Air blank not 0.00 = CANCEL TEST',
    },
    {
        'step': 3,
        'phase': 'PRE_TEST',
        'name': 'Verify Donor Identity',
        'instruction': (
            'Government-issued photo ID. Confirm name matches testing authorization. '
            'Record ID type on ATF.'
        ),
        'fatal_if_failed': True,
    },
    {
        'step': 4,
        'phase': 'PRE_TEST',
        'name': 'Explain Procedure',
        'instruction': (
            'Explain screening test, possibility of 15-minute wait and confirmation test '
            'if screening is ≥ 0.02. Explain consequences of refusal.'
        ),
        'fatal_if_failed': False,
    },
    {
        'step': 5,
        'phase': 'ABSTENTION',
        'name': '15-Minute Abstention (Before Screening)',
        'instruction': (
            'Donor must not eat, drink, smoke, use mouthwash, or put anything in mouth for '
            '15 minutes before screening blow. Start timer. Observe or document start time.'
        ),
        'fatal_if_failed': False,
    },
    {
        'step': 6,
        'phase': 'SCREENING',
        'name': 'Screening Test (EBT)',
        'instruction': (
            'Donor provides breath sample per device instructions. BAT operates EBT. '
            'Result MUST print from EBT. Attach printed result to ATF.'
        ),
        'fatal_if_failed': True,
        'fatal_note': 'EBT fails to print result = CANCEL TEST',
    },
    {
        'step': 7,
        'phase': 'DECISION',
        'name': 'Evaluate Screening Result',
        'instruction': (
            'If BrAC < 0.02: NEGATIVE — test complete, go to Step 12 (documentation). '
            'If BrAC ≥ 0.02: proceed to Step 8 (15-minute wait — NOT optional).'
        ),
        'fatal_if_failed': False,
    },
    {
        'step': 8,
        'phase': 'WAIT',
        'name': '15-Minute Wait (Screen Positive Only)',
        'instruction': (
            'Minimum 15 minutes between end of screening blow and start of confirmation blow. '
            'Maximum 30 minutes recommended. Donor must NOT eat, drink, smoke, or put anything '
            'in mouth. If donor violates abstention during wait, document on ATF.'
        ),
        'fatal_if_failed': True,
        'fatal_note': 'Less than 15 minutes between screening and confirmation = FATAL FLAW',
        'skip_if': 'screening_negative',
    },
    {
        'step': 9,
        'phase': 'CONFIRMATION',
        'name': 'Air Blank Before Confirmation',
        'instruction': 'Repeat air blank. Must read 0.00 before confirmation test.',
        'fatal_if_failed': True,
    },
    {
        'step': 10,
        'phase': 'CONFIRMATION',
        'name': 'Confirmation Test (EBT Only)',
        'instruction': (
            'Second test MUST be on EBT — not an alcohol screening device (ASD). '
            'Donor blows. Print result. Attach to ATF.'
        ),
        'fatal_if_failed': True,
        'fatal_note': 'Confirmation on ASD instead of EBT = CANCEL TEST',
    },
    {
        'step': 11,
        'phase': 'DECISION',
        'name': 'Evaluate Confirmation Result',
        'instruction': (
            'Apply confirmation interpretation: <0.02 negative; 0.02–0.039 positive (low); '
            '≥0.04 positive (violation). Document all BrAC values on ATF.'
        ),
        'fatal_if_failed': False,
    },
    {
        'step': 12,
        'phase': 'CLOSE',
        'name': 'ATF Completion & Signatures',
        'instruction': (
            'BAT signs ATF. Employee signs ATF (or document refusal to sign). '
            'All printed EBT results attached. Copy to employer/DER as required.'
        ),
        'fatal_if_failed': True,
        'fatal_note': 'No BAT signature or no employee signature (uncorrected) = FATAL',
    },
]

FATAL_FLAWS_BAT = [
    {'id': 'EBT-1', 'text': 'EBT fails to print result', 'action': 'CANCEL TEST'},
    {'id': 'EBT-2', 'text': 'Air blank not 0.00', 'action': 'CANCEL TEST'},
    {'id': 'EBT-3', 'text': 'EBT not on NHTSA Conforming Products List', 'action': 'CANCEL TEST'},
    {'id': 'EBT-4', 'text': 'Device malfunction during test', 'action': 'CANCEL TEST'},
    {'id': 'ATF-1', 'text': 'No BAT signature on ATF', 'action': 'CANCEL TEST'},
    {'id': 'ATF-2', 'text': 'No employee signature on ATF (and not corrected)', 'action': 'CANCEL TEST'},
    {'id': 'ATF-3', 'text': 'Printed result not attached to ATF', 'action': 'CANCEL TEST'},
    {'id': 'PROC-1', 'text': 'Confirmation test not on EBT (ASD used)', 'action': 'CANCEL TEST'},
    {'id': 'PROC-2', 'text': 'Less than 15 minutes between screening and confirmation', 'action': 'CANCEL TEST'},
]


# ═══════════════════════════════════════════════════════════════════
# ORDER LIFECYCLE
# ═══════════════════════════════════════════════════════════════════

def create_bat_order(
    client_id: str,
    client_name: str,
    donor_name: str,
    test_reason: str,
    ebt_make: str = '',
    ebt_model: str = '',
    ebt_serial: str = '',
    bat_name: str = '',
    post_accident: bool = False,
    accident_time: str = '',
    employer_id: str = '',
    notes: str = '',
) -> dict:
    """Create a BAT order in PRE_TEST status."""
    orders = _load_orders()
    oid = _new_id('BAT')
    order = {
        'id': oid,
        'client_id': client_id,
        'client_name': client_name,
        'employer_id': employer_id,
        'donor_name': donor_name,
        'test_reason': test_reason,
        'ebt_make': ebt_make,
        'ebt_model': ebt_model,
        'ebt_serial': ebt_serial,
        'bat_name': bat_name,
        'post_accident': post_accident,
        'accident_time': accident_time,
        'status': 'PRE_TEST',
        'screening_brac': None,
        'screening_time': None,
        'wait_started': None,
        'wait_ended': None,
        'confirmation_brac': None,
        'confirmation_time': None,
        'final_interpretation': None,
        'procedure_steps': [{**s, 'completed': False, 'completed_at': None} for s in BAT_PROCEDURE_STEPS],
        'fatal_flaw_reported': None,
        'cancelled': False,
        'notes': notes,
        'created_at': datetime.now().isoformat(),
    }
    if post_accident and accident_time:
        try:
            at = datetime.fromisoformat(accident_time.replace('Z', '+00:00'))
            deadline = at + timedelta(hours=8)
            order['alcohol_test_deadline'] = deadline.isoformat()
            order['alcohol_test_note'] = 'DOT post-accident alcohol: complete within 8 hours of accident (2 hours preferred).'
        except Exception:
            order['alcohol_test_note'] = 'Document time of accident and complete alcohol test within 8 hours.'

    orders.append(order)
    _save_orders(orders)

    return {
        'message': 'BAT order created',
        'order_id': oid,
        'procedure': 'GET /prism/bat/procedure',
        'fatal_flaws': 'GET /prism/bat/fatal-flaws',
        'order': order,
    }


def record_screening(order_id: str, brac: float, ebt_printed: bool = True) -> dict:
    """Record screening BrAC and advance workflow."""
    orders = _load_orders()
    for o in orders:
        if o['id'] != order_id:
            continue
        if not ebt_printed:
            o['fatal_flaw_reported'] = 'EBT-1: EBT fails to print result'
            o['cancelled'] = True
            o['status'] = 'CANCELLED_FATAL'
            _save_orders(orders)
            return {'error': 'Fatal flaw: result must print from EBT', 'order_id': order_id}

        o['screening_brac'] = brac
        o['screening_time'] = datetime.now().isoformat()
        interp = interpret_screening(brac)

        if interp['result'] == 'NEGATIVE':
            o['status'] = 'COMPLETE_NEGATIVE'
            o['final_interpretation'] = interp
            o['confirmation_required'] = False
        else:
            o['status'] = 'AWAITING_15_MIN_WAIT'
            o['confirmation_required'] = True
            o['wait_started'] = datetime.now().isoformat()
            o['screening_interp'] = interp

        _save_orders(orders)
        return {
            'message': 'Screening recorded',
            'order_id': order_id,
            'screening_brac': brac,
            'interpretation': interp,
            'next': interp.get('next_step', 'DOCUMENT_AND_CLOSE'),
        }
    return {'error': f'Order {order_id} not found'}


def record_wait_complete(order_id: str) -> dict:
    """Mark 15-minute wait complete (validate elapsed time)."""
    orders = _load_orders()
    for o in orders:
        if o['id'] != order_id:
            continue
        if o['status'] != 'AWAITING_15_MIN_WAIT':
            return {'error': f'Order not awaiting wait: status={o["status"]}'}

        start = datetime.fromisoformat(o['wait_started'])
        now = datetime.now()
        elapsed = (now - start).total_seconds() / 60.0
        if elapsed < 15.0:
            return {
                'error': 'FATAL: Less than 15 minutes since screening. Wait longer before confirmation.',
                'elapsed_minutes': round(elapsed, 2),
                'required_minutes': 15,
            }

        o['wait_ended'] = now.isoformat()
        o['wait_elapsed_minutes'] = round(elapsed, 2)
        o['status'] = 'READY_FOR_CONFIRMATION'
        _save_orders(orders)
        return {
            'message': '15-minute wait satisfied',
            'order_id': order_id,
            'elapsed_minutes': round(elapsed, 2),
            'next': 'Conduct confirmation test on EBT — POST /prism/bat/orders/<id>/confirmation',
        }
    return {'error': f'Order {order_id} not found'}


def record_confirmation(order_id: str, brac: float, ebt_printed: bool = True) -> dict:
    """Record confirmation BrAC."""
    orders = _load_orders()
    for o in orders:
        if o['id'] != order_id:
            continue
        if o['status'] not in ('READY_FOR_CONFIRMATION', 'AWAITING_15_MIN_WAIT'):
            return {'error': f'Invalid status for confirmation: {o["status"]}'}

        if o['status'] == 'AWAITING_15_MIN_WAIT':
            start = datetime.fromisoformat(o['wait_started'])
            elapsed = (datetime.now() - start).total_seconds() / 60.0
            if elapsed < 15.0:
                o['fatal_flaw_reported'] = 'PROC-2: Less than 15 minutes between screening and confirmation'
                o['cancelled'] = True
                o['status'] = 'CANCELLED_FATAL'
                _save_orders(orders)
                return {'error': 'FATAL: Confirmation before 15 minutes elapsed', 'elapsed_minutes': round(elapsed, 2)}

        if not ebt_printed:
            o['fatal_flaw_reported'] = 'EBT-1'
            o['cancelled'] = True
            o['status'] = 'CANCELLED_FATAL'
            _save_orders(orders)
            return {'error': 'Fatal flaw: confirmation result must print from EBT'}

        o['confirmation_brac'] = brac
        o['confirmation_time'] = datetime.now().isoformat()
        final = interpret_confirmation(brac)
        o['final_interpretation'] = final
        o['status'] = 'COMPLETE_' + final['result']

        _save_orders(orders)

        out = {
            'message': 'Confirmation recorded',
            'order_id': order_id,
            'confirmation_brac': brac,
            'interpretation': final,
        }
        if final.get('result') == 'POSITIVE_VIOLATION':
            out['clearinghouse'] = {
                'note': 'If FMCSA-regulated driver, report alcohol violation per Clearinghouse rules.',
                'endpoint': 'POST /prism/clearinghouse/violations',
                'violation_type': 'POSITIVE_ALCOHOL',
            }
        return out
    return {'error': f'Order {order_id} not found'}


def complete_procedure_step(order_id: str, step_number: int) -> dict:
    orders = _load_orders()
    for o in orders:
        if o['id'] != order_id:
            continue
        for s in o.get('procedure_steps', []):
            if s.get('step') == step_number:
                s['completed'] = True
                s['completed_at'] = datetime.now().isoformat()
        _save_orders(orders)
        done = sum(1 for s in o['procedure_steps'] if s.get('completed'))
        return {'message': f'Step {step_number} marked complete', 'progress': f'{done}/12', 'order_id': order_id}
    return {'error': 'Order not found'}


def report_fatal_flaw(order_id: str, flaw_id: str, notes: str = '') -> dict:
    orders = _load_orders()
    for o in orders:
        if o['id'] != order_id:
            continue
        o['fatal_flaw_reported'] = flaw_id
        o['fatal_notes'] = notes
        o['cancelled'] = True
        o['status'] = 'CANCELLED_FATAL'
        _save_orders(orders)
        return {
            'message': 'Order cancelled due to fatal flaw',
            'order_id': order_id,
            'flaw_id': flaw_id,
            'action': 'Do not use results. Document and retain ATF per Part 40.',
        }
    return {'error': 'Order not found'}


def get_dashboard() -> dict:
    orders = _load_orders()
    open_o = [o for o in orders if o['status'] not in ('COMPLETE_NEGATIVE', 'COMPLETE_POSITIVE_LOW', 'COMPLETE_POSITIVE_VIOLATION', 'CANCELLED_FATAL') and not o.get('cancelled')]
    cancelled = len([o for o in orders if o['status'] == 'CANCELLED_FATAL'])
    return {
        'open_orders': len(open_o),
        'awaiting_wait': len([o for o in orders if o['status'] == 'AWAITING_15_MIN_WAIT']),
        'ready_confirmation': len([o for o in orders if o['status'] == 'READY_FOR_CONFIRMATION']),
        'cancelled_fatal': cancelled,
        'total_orders': len(orders),
        'generated_at': datetime.now().isoformat(),
    }


# ═══════════════════════════════════════════════════════════════════
# ROUTES
# ═══════════════════════════════════════════════════════════════════

@prism_bat.route('/prism/bat/procedure', methods=['GET'])
def api_procedure():
    return jsonify({
        'title': 'DOT Breath Alcohol Testing (BAT) — Procedure Checklist',
        'reference': '49 CFR Part 40 Subparts J & K',
        'screening_rule': '< 0.02 = negative (no confirmation). ≥ 0.02 = 15-min wait + confirmation on EBT.',
        'confirmation_rules': {
            'negative': '< 0.02',
            'positive_low': '0.02 – 0.039',
            'positive_violation': '≥ 0.04',
        },
        'steps': BAT_PROCEDURE_STEPS,
        'step_count': len(BAT_PROCEDURE_STEPS),
    })


@prism_bat.route('/prism/bat/fatal-flaws', methods=['GET'])
def api_fatal_flaws():
    return jsonify({'fatal_flaws': FATAL_FLAWS_BAT, 'source': 'FATAL_FLAW_CHECKLIST.md — Alcohol Test'})


@prism_bat.route('/prism/bat/interpret', methods=['POST'])
def api_interpret():
    """Utility: interpret screening or confirmation BrAC without an order."""
    data = request.get_json() or {}
    phase = data.get('phase', 'screening')
    brac = float(data.get('brac', -1))
    if phase == 'screening':
        return jsonify(interpret_screening(brac))
    return jsonify(interpret_confirmation(brac))


@prism_bat.route('/prism/bat/orders', methods=['GET'])
def api_list_orders():
    status = request.args.get('status')
    orders = _load_orders()
    if status:
        orders = [o for o in orders if o.get('status') == status]
    return jsonify({'orders': orders, 'count': len(orders)})


@prism_bat.route('/prism/bat/orders', methods=['POST'])
def api_create_order():
    data = request.get_json() or {}
    req = ['client_id', 'client_name', 'donor_name', 'test_reason']
    for f in req:
        if not data.get(f):
            return jsonify({'error': f'Missing: {f}'}), 400
    return jsonify(create_bat_order(
        client_id=data['client_id'],
        client_name=data['client_name'],
        donor_name=data['donor_name'],
        test_reason=data['test_reason'],
        ebt_make=data.get('ebt_make', ''),
        ebt_model=data.get('ebt_model', ''),
        ebt_serial=data.get('ebt_serial', ''),
        bat_name=data.get('bat_name', ''),
        post_accident=data.get('post_accident', False),
        accident_time=data.get('accident_time', ''),
        employer_id=data.get('employer_id', ''),
        notes=data.get('notes', ''),
    )), 201


@prism_bat.route('/prism/bat/orders/<order_id>/screening', methods=['POST'])
def api_screening(order_id):
    data = request.get_json() or {}
    if 'brac' not in data:
        return jsonify({'error': 'brac required (e.g. 0.018)'}), 400
    return jsonify(record_screening(order_id, float(data['brac']), data.get('ebt_printed', True)))


@prism_bat.route('/prism/bat/orders/<order_id>/wait-complete', methods=['POST'])
def api_wait_complete(order_id):
    return jsonify(record_wait_complete(order_id))


@prism_bat.route('/prism/bat/orders/<order_id>/confirmation', methods=['POST'])
def api_confirmation(order_id):
    data = request.get_json() or {}
    if 'brac' not in data:
        return jsonify({'error': 'brac required'}), 400
    return jsonify(record_confirmation(order_id, float(data['brac']), data.get('ebt_printed', True)))


@prism_bat.route('/prism/bat/orders/<order_id>/step/<int:step>', methods=['POST'])
def api_step(order_id, step):
    return jsonify(complete_procedure_step(order_id, step))


@prism_bat.route('/prism/bat/orders/<order_id>/fatal-flaw', methods=['POST'])
def api_fatal(order_id):
    data = request.get_json() or {}
    if not data.get('flaw_id'):
        return jsonify({'error': 'flaw_id required (see GET /prism/bat/fatal-flaws)'}), 400
    return jsonify(report_fatal_flaw(order_id, data['flaw_id'], data.get('notes', '')))


@prism_bat.route('/prism/bat/dashboard', methods=['GET'])
def api_dashboard():
    return jsonify(get_dashboard())
