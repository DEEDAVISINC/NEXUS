#!/usr/bin/env python3
"""
PRISM POCT — POINT OF CARE TESTING MODULE
==========================================
Manages rapid on-site drug testing using POCT (Point of Care Testing) cups.

Primary supplier: 12PanelNow ($2.09/cup — brenda@slashmedical.com)
Primary use cases: Courts, probation, child welfare, social services,
                   employer reasonable suspicion, pre-employment rapid screen

PANELS SUPPORTED:
  5-panel:  THC, Cocaine, Opiates, Amphetamines, Methamphetamines
  10-panel: 5-panel + Benzodiazepines, Barbiturates, Methadone, Propoxyphene, Oxycodone
  12-panel: 10-panel + Buprenorphine, PCP  (primary focus of this module)

POCT IS NON-DOT:
  DOT testing requires SAMHSA-certified lab analysis and MRO review.
  POCT is for non-DOT / non-regulated workplace testing only.
  Positive POCT results MUST be confirmed by lab before adverse action.

WORKFLOW:
  1. Order created → cup assigned from inventory
  2. Collector administers test (10-step procedure)
  3. Result read at 5 minutes
  4. Negative → documented, complete
  5. Non-Negative → send split specimen to lab for GC/MS confirmation
  6. Confirmed Positive → adverse action process, Clearinghouse if DOT-regulated driver
  7. All results logged with chain of custody

Reference: SAMHSA POCT guidelines, 49 CFR Part 40 (DOT POCT is prohibited for regulated testing)
"""

import json
import os
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from flask import Blueprint, request, jsonify

prism_poct = Blueprint('prism_poct', __name__)

# ═══════════════════════════════════════════════════════════════════
# DATA STORAGE
# ═══════════════════════════════════════════════════════════════════

DATA_DIR      = os.path.join(os.path.dirname(__file__), 'uploads', 'prism', 'poct')
ORDERS_FILE   = os.path.join(DATA_DIR, 'poct_orders.json')
INVENTORY_FILE = os.path.join(DATA_DIR, 'cup_inventory.json')
RESULTS_FILE  = os.path.join(DATA_DIR, 'poct_results.json')
CLIENTS_FILE  = os.path.join(DATA_DIR, 'poct_clients.json')


def _ensure():
    os.makedirs(DATA_DIR, exist_ok=True)


def _load(f):
    _ensure()
    return json.load(open(f)) if os.path.exists(f) else []


def _save(f, data):
    _ensure()
    with open(f, 'w') as fp:
        json.dump(data, fp, indent=2, default=str)


def _id(prefix):
    return f"{prefix}-{uuid.uuid4().hex[:8].upper()}"


# ═══════════════════════════════════════════════════════════════════
# PANEL DEFINITIONS
# ═══════════════════════════════════════════════════════════════════

PANELS = {
    '5': {
        'label':      '5-Panel',
        'substances': ['THC', 'Cocaine', 'Opiates', 'Amphetamines', 'Methamphetamines'],
        'cup_cost':   1.50,
        'ddi_rate':   75,
        'read_time_minutes': 5,
    },
    '10': {
        'label':      '10-Panel',
        'substances': [
            'THC', 'Cocaine', 'Opiates', 'Amphetamines', 'Methamphetamines',
            'Benzodiazepines', 'Barbiturates', 'Methadone', 'Propoxyphene', 'Oxycodone',
        ],
        'cup_cost':   1.85,
        'ddi_rate':   95,
        'read_time_minutes': 5,
    },
    '12': {
        'label':      '12-Panel',
        'substances': [
            'THC', 'Cocaine', 'Opiates', 'Amphetamines', 'Methamphetamines',
            'Benzodiazepines', 'Barbiturates', 'Methadone', 'Propoxyphene', 'Oxycodone',
            'Buprenorphine', 'PCP',
        ],
        'cup_cost':   2.09,   # 12PanelNow locked quote
        'ddi_rate':   70,
        'read_time_minutes': 5,
        'supplier':   '12PanelNow',
        'supplier_contact': 'brenda@slashmedical.com',
    },
}

# Result interpretation
RESULT_CODES = {
    'NEG':     {'label': 'Negative',     'color': 'green',  'action': 'document_and_close'},
    'NON_NEG': {'label': 'Non-Negative', 'color': 'red',    'action': 'send_to_lab'},
    'INVALID': {'label': 'Invalid',      'color': 'yellow', 'action': 'retest'},
    'PENDING': {'label': 'Pending',      'color': 'gray',   'action': 'await_read_time'},
}

# 10-step POCT collection procedure
COLLECTION_PROCEDURE = [
    {
        'step': 1,
        'name': 'Verify Donor Identity',
        'instruction': 'Request government-issued photo ID. Confirm name matches the order. Record ID type and last 4 of ID number.',
        'critical': True,
    },
    {
        'step': 2,
        'name': 'Check for Adulteration',
        'instruction': 'Ask donor to empty pockets, remove outer garments. Check collection area for soap, cleaning agents, foreign substances. Secure water supply if available.',
        'critical': True,
    },
    {
        'step': 3,
        'name': 'Select and Inspect Cup',
        'instruction': 'Remove sealed cup from inventory. Inspect for damage, tampering, or broken seal. Record lot number. Do not open until ready to hand to donor.',
        'critical': True,
    },
    {
        'step': 4,
        'name': 'Instruct Donor',
        'instruction': 'Explain the collection process: donor provides urine specimen directly into the cup, fills to the fill line, caps the cup, and hands it directly to the collector.',
        'critical': False,
    },
    {
        'step': 5,
        'name': 'Direct Collection',
        'instruction': 'Hand sealed cup to donor. Donor enters restroom alone (or observed if required). Collector waits outside. Donor must return the capped cup directly to the collector.',
        'critical': True,
    },
    {
        'step': 6,
        'name': 'Check Temperature',
        'instruction': 'Immediately check temperature strip on cup. Acceptable range: 90°F-100°F (32°C-38°C). If outside range, document and treat as possible substitution — may require observed retest.',
        'critical': True,
    },
    {
        'step': 7,
        'name': 'Check Volume',
        'instruction': 'Confirm specimen fills to or above the minimum line. If insufficient, initiate shy bladder protocol: donor may drink up to 40 oz of water and wait up to 3 hours.',
        'critical': True,
    },
    {
        'step': 8,
        'name': 'Activate Test Strips',
        'instruction': 'Peel the label cover to expose the test strips. Do not agitate or tilt the cup. Set timer for exactly 5 minutes. Do not read results before 5 minutes.',
        'critical': True,
    },
    {
        'step': 9,
        'name': 'Read Results at 5 Minutes',
        'instruction': (
            'Read each test line at exactly 5 minutes. '
            'TWO lines (control + test) = NEGATIVE for that substance. '
            'ONE line (control only) = NON-NEGATIVE for that substance. '
            'NO lines = INVALID — retest required. '
            'Do not read results after 8 minutes (evaporation lines can appear).'
        ),
        'critical': True,
    },
    {
        'step': 10,
        'name': 'Document and Secure',
        'instruction': (
            'Record each substance result (NEG/NON-NEG). '
            'If ALL negative: document, seal cup, give donor copy of results if required, complete. '
            'If ANY non-negative: do NOT discard cup — retain for lab confirmation. '
            'Explain to donor that a non-negative screen requires lab confirmation before any action is taken.'
        ),
        'critical': True,
    },
]


# ═══════════════════════════════════════════════════════════════════
# CUP INVENTORY MANAGEMENT
# ═══════════════════════════════════════════════════════════════════

def add_inventory(
    panel: str,
    quantity: int,
    lot_number: str,
    expiration_date: str,
    supplier: str = '12PanelNow',
    cost_per_cup: float = None,
    po_number: str = '',
) -> dict:
    """Add a batch of POCT cups to inventory."""
    if panel not in PANELS:
        return {'error': f'Invalid panel. Must be one of: {list(PANELS.keys())}'}

    inventory = _load(INVENTORY_FILE)
    cost = cost_per_cup or PANELS[panel]['cup_cost']

    batch = {
        'id':              _id('INV'),
        'panel':           panel,
        'panel_label':     PANELS[panel]['label'],
        'quantity_added':  quantity,
        'quantity_remaining': quantity,
        'lot_number':      lot_number,
        'expiration_date': expiration_date,
        'supplier':        supplier,
        'cost_per_cup':    cost,
        'total_cost':      round(cost * quantity, 2),
        'po_number':       po_number,
        'added_at':        datetime.now().isoformat(),
        'active':          True,
    }

    inventory.append(batch)
    _save(INVENTORY_FILE, inventory)

    return {
        'message':        f'Added {quantity} {PANELS[panel]["label"]} cups to inventory',
        'batch_id':       batch['id'],
        'total_cost':     batch['total_cost'],
        'expires':        expiration_date,
        'batch':          batch,
    }


def get_inventory_status() -> dict:
    """Current cup inventory across all panels."""
    inventory = _load(INVENTORY_FILE)
    today = datetime.now().date()
    summary = {}

    for batch in inventory:
        if not batch['active'] or batch['quantity_remaining'] <= 0:
            continue
        panel = batch['panel']
        exp = datetime.strptime(batch['expiration_date'], '%Y-%m-%d').date()
        days_to_exp = (exp - today).days

        if panel not in summary:
            summary[panel] = {
                'panel_label': PANELS[panel]['label'],
                'total_cups':  0,
                'batches':     [],
                'alerts':      [],
            }

        summary[panel]['total_cups'] += batch['quantity_remaining']
        summary[panel]['batches'].append({
            'lot':       batch['lot_number'],
            'remaining': batch['quantity_remaining'],
            'expires':   batch['expiration_date'],
            'days_to_exp': days_to_exp,
        })

        if days_to_exp <= 30:
            summary[panel]['alerts'].append(f"LOT {batch['lot_number']}: expires in {days_to_exp} days")
        if batch['quantity_remaining'] <= 20:
            summary[panel]['alerts'].append(f"LOT {batch['lot_number']}: LOW STOCK ({batch['quantity_remaining']} remaining)")

    reorder_needed = [p for p, s in summary.items() if s['total_cups'] < 25]

    return {
        'inventory':        summary,
        'reorder_needed':   reorder_needed,
        'supplier':         '12PanelNow',
        'supplier_contact': 'brenda@slashmedical.com',
        'supplier_price':   '$2.09/cup (12-panel)',
        'generated_at':     datetime.now().isoformat(),
    }


def _consume_cup(panel: str) -> Optional[dict]:
    """Pull one cup from inventory (FIFO by expiration date)."""
    inventory = _load(INVENTORY_FILE)
    available = [
        b for b in inventory
        if b['panel'] == panel and b['active'] and b['quantity_remaining'] > 0
    ]
    if not available:
        return None

    # Use soonest-expiring batch first
    available.sort(key=lambda b: b['expiration_date'])
    batch = available[0]
    for b in inventory:
        if b['id'] == batch['id']:
            b['quantity_remaining'] -= 1
            if b['quantity_remaining'] == 0:
                b['active'] = False
            _save(INVENTORY_FILE, inventory)
            return {'lot_number': b['lot_number'], 'expiration_date': b['expiration_date'], 'batch_id': b['id']}

    return None


# ═══════════════════════════════════════════════════════════════════
# ORDER MANAGEMENT
# ═══════════════════════════════════════════════════════════════════

def create_poct_order(
    client_id: str,
    client_name: str,
    donor_name: str,
    donor_id_type: str,
    donor_id_last4: str,
    panel: str = '12',
    reason: str = '',
    employer_id: str = '',
    observer_required: bool = False,
    notes: str = '',
) -> dict:
    """Create a new POCT order and assign a cup from inventory."""
    if panel not in PANELS:
        return {'error': f'Invalid panel. Must be one of: {list(PANELS.keys())}'}

    cup = _consume_cup(panel)
    if not cup:
        return {
            'error': f'No {PANELS[panel]["label"]} cups available in inventory.',
            'action': f'Order more cups from 12PanelNow (brenda@slashmedical.com). Current cost: ${PANELS[panel]["cup_cost"]}/cup.',
        }

    orders = _load(ORDERS_FILE)
    order = {
        'id':                _id('POCT'),
        'client_id':         client_id,
        'client_name':       client_name,
        'employer_id':       employer_id,
        'donor_name':        donor_name,
        'donor_id_type':     donor_id_type,
        'donor_id_last4':    donor_id_last4,
        'panel':             panel,
        'panel_label':       PANELS[panel]['label'],
        'substances_tested': PANELS[panel]['substances'],
        'reason':            reason,
        'observer_required': observer_required,
        'cup_lot_number':    cup['lot_number'],
        'cup_expiration':    cup['expiration_date'],
        'cup_batch_id':      cup['batch_id'],
        'cup_cost':          PANELS[panel]['cup_cost'],
        'ddi_rate':          PANELS[panel]['ddi_rate'],
        'status':            'COLLECTION_IN_PROGRESS',
        'collection_started': datetime.now().isoformat(),
        'collection_completed': None,
        'result_read_time':  None,
        'results':           {},
        'overall_result':    'PENDING',
        'lab_confirmation_required': False,
        'lab_order_id':      None,
        'adverse_action_eligible': False,
        'notes':             notes,
        'created_at':        datetime.now().isoformat(),
        'procedure_steps':   [
            {**step, 'completed': False, 'completed_at': None}
            for step in COLLECTION_PROCEDURE
        ],
    }

    orders.append(order)
    _save(ORDERS_FILE, orders)

    read_deadline = datetime.now() + timedelta(minutes=PANELS[panel]['read_time_minutes'])

    return {
        'message':          f'POCT order created — {PANELS[panel]["label"]} cup assigned',
        'order_id':         order['id'],
        'cup_lot':          cup['lot_number'],
        'cup_expires':      cup['expiration_date'],
        'panel':            PANELS[panel]['label'],
        'substances':       PANELS[panel]['substances'],
        'read_at':          f'READ RESULTS AT EXACTLY 5 MINUTES — {read_deadline.strftime("%I:%M %p")}',
        'procedure':        f'Follow 10-step collection procedure. GET /prism/poct/procedure',
        'ddi_rate':         PANELS[panel]['ddi_rate'],
        'order':            order,
    }


def record_results(
    order_id: str,
    results: Dict[str, str],
    collector_name: str,
    read_time: str = None,
    temperature_ok: bool = True,
    temperature_reading: str = '',
    notes: str = '',
) -> dict:
    """
    Record POCT results for an order.

    results: dict of substance → result code
    Example: { 'THC': 'NEG', 'Cocaine': 'NEG', 'Opiates': 'NON_NEG', ... }

    Result codes: NEG | NON_NEG | INVALID
    """
    orders = _load(ORDERS_FILE)
    for order in orders:
        if order['id'] != order_id:
            continue

        now = datetime.now()
        non_negatives = [s for s, r in results.items() if r == 'NON_NEG']
        invalids = [s for s, r in results.items() if r == 'INVALID']

        # Determine overall result
        if invalids:
            overall = 'INVALID'
        elif non_negatives:
            overall = 'NON_NEG'
        else:
            overall = 'NEG'

        order['results'] = results
        order['overall_result'] = overall
        order['collection_completed'] = now.isoformat()
        order['result_read_time'] = read_time or now.isoformat()
        order['collector_name'] = collector_name
        order['temperature_ok'] = temperature_ok
        order['temperature_reading'] = temperature_reading
        order['notes'] = notes
        order['lab_confirmation_required'] = overall == 'NON_NEG'
        order['adverse_action_eligible'] = False  # not until lab confirms

        if overall == 'NEG':
            order['status'] = 'COMPLETE_NEGATIVE'
            order['next_action'] = 'Document result. Provide donor copy if required. Order complete.'
        elif overall == 'NON_NEG':
            order['status'] = 'PENDING_LAB_CONFIRMATION'
            order['next_action'] = (
                f'NON-NEGATIVE on: {", ".join(non_negatives)}. '
                'DO NOT take adverse action yet. '
                'Send split specimen to lab for GC/MS confirmation. '
                'Use POST /prism/poct/<order_id>/send-to-lab'
            )
        elif overall == 'INVALID':
            order['status'] = 'INVALID_RETEST_REQUIRED'
            order['next_action'] = (
                'Invalid result — no test lines appeared. '
                'Assign a new cup and retest immediately. '
                'Possible adulteration — consider observed collection.'
            )

        _save(ORDERS_FILE, orders)

        response = {
            'message':       f'Results recorded — {overall}',
            'order_id':      order_id,
            'overall_result': overall,
            'non_negatives': non_negatives,
            'invalids':      invalids,
            'status':        order['status'],
            'next_action':   order['next_action'],
            'results':       results,
        }

        if overall == 'NON_NEG':
            response['important'] = [
                '⚠️ NON-NEGATIVE is a SCREEN RESULT — not a confirmed positive',
                '⚠️ Do NOT tell donor they "failed" — say the screen requires lab confirmation',
                '⚠️ Do NOT take adverse employment action until lab confirms',
                '⚠️ Retain the cup — do not discard',
                f'⚠️ Non-negative substances: {", ".join(non_negatives)}',
            ]

        return response

    return {'error': f'Order {order_id} not found'}


def send_to_lab(
    order_id: str,
    lab_name: str = 'Quest Diagnostics',
    tracking_number: str = '',
    notes: str = '',
) -> dict:
    """
    Initiate lab confirmation for a non-negative POCT result.
    Routes through the service router for lab partner assignment.
    """
    orders = _load(ORDERS_FILE)
    for order in orders:
        if order['id'] != order_id:
            continue

        if order['overall_result'] != 'NON_NEG':
            return {'error': f'Order {order_id} result is {order["overall_result"]} — lab confirmation only needed for NON_NEG'}

        lab_order_id = _id('LAB')
        order['status'] = 'LAB_CONFIRMATION_SENT'
        order['lab_order_id'] = lab_order_id
        order['lab_name'] = lab_name
        order['lab_tracking_number'] = tracking_number
        order['lab_sent_at'] = datetime.now().isoformat()
        order['lab_result'] = None
        order['lab_result_date'] = None

        _save(ORDERS_FILE, orders)

        return {
            'message':       f'Specimen sent to {lab_name} for GC/MS confirmation',
            'order_id':      order_id,
            'lab_order_id':  lab_order_id,
            'lab':           lab_name,
            'tracking':      tracking_number,
            'non_negatives': [s for s, r in order['results'].items() if r == 'NON_NEG'],
            'expected_turnaround': '24-72 hours',
            'next_step':     f'Record lab result when received: POST /prism/poct/{order_id}/lab-result',
            'billing_note':  f'Charge client additional $85 for lab confirmation (DDI rate). Cost to DDI: ~$40-55.',
        }

    return {'error': f'Order {order_id} not found'}


def record_lab_result(
    order_id: str,
    lab_result: str,
    confirmed_substances: List[str] = None,
    mro_name: str = '',
    lab_report_number: str = '',
) -> dict:
    """
    Record the final lab confirmation result.

    lab_result: 'NEGATIVE' | 'POSITIVE' | 'INVALID'
    confirmed_substances: list of substances confirmed positive by lab
    """
    orders = _load(ORDERS_FILE)
    for order in orders:
        if order['id'] != order_id:
            continue

        now = datetime.now()
        order['lab_result'] = lab_result
        order['lab_result_date'] = now.isoformat()
        order['lab_confirmed_substances'] = confirmed_substances or []
        order['mro_name'] = mro_name
        order['lab_report_number'] = lab_report_number

        if lab_result == 'NEGATIVE':
            order['status'] = 'COMPLETE_LAB_NEGATIVE'
            order['adverse_action_eligible'] = False
            order['next_action'] = 'Lab confirmed negative. No adverse action. Document and close.'
        elif lab_result == 'POSITIVE':
            order['status'] = 'COMPLETE_LAB_POSITIVE'
            order['adverse_action_eligible'] = True
            order['next_action'] = (
                f'CONFIRMED POSITIVE: {", ".join(confirmed_substances or [])}. '
                'Employer may now take adverse action per their policy. '
                'If driver is DOT-regulated: report to FMCSA Clearinghouse within 3 business days. '
                'Use POST /prism/router/hooks/positive-test to generate Clearinghouse package.'
            )
        else:
            order['status'] = 'COMPLETE_LAB_INVALID'
            order['adverse_action_eligible'] = False
            order['next_action'] = 'Lab result invalid. Consult MRO for guidance on next steps.'

        _save(ORDERS_FILE, orders)

        response = {
            'message':                f'Lab result recorded — {lab_result}',
            'order_id':               order_id,
            'lab_result':             lab_result,
            'confirmed_substances':   confirmed_substances or [],
            'status':                 order['status'],
            'adverse_action_eligible': order['adverse_action_eligible'],
            'next_action':            order['next_action'],
        }

        if lab_result == 'POSITIVE' and order.get('employer_id'):
            response['clearinghouse_check'] = {
                'note':     'If this driver is DOT-regulated, report to FMCSA Clearinghouse within 3 business days.',
                'endpoint': 'POST /prism/clearinghouse/violations',
                'router':   'POST /prism/router/hooks/positive-test',
            }

        return response

    return {'error': f'Order {order_id} not found'}


def complete_procedure_step(order_id: str, step_number: int) -> dict:
    """Mark a collection procedure step as complete."""
    orders = _load(ORDERS_FILE)
    for order in orders:
        if order['id'] != order_id:
            continue
        for step in order.get('procedure_steps', []):
            if step['step'] == step_number:
                step['completed'] = True
                step['completed_at'] = datetime.now().isoformat()
        _save(ORDERS_FILE, orders)
        completed = sum(1 for s in order['procedure_steps'] if s['completed'])
        total = len(order['procedure_steps'])
        return {
            'message':   f'Step {step_number} completed',
            'progress':  f'{completed}/{total} steps complete',
            'order_id':  order_id,
        }
    return {'error': f'Order {order_id} not found'}


# ═══════════════════════════════════════════════════════════════════
# REVENUE & REPORTING
# ═══════════════════════════════════════════════════════════════════

def get_revenue_report(client_id: str = None, days: int = 30) -> dict:
    """POCT revenue summary for a date range."""
    orders = _load(ORDERS_FILE)
    cutoff = (datetime.now() - timedelta(days=days)).isoformat()
    filtered = [
        o for o in orders
        if o['created_at'] >= cutoff and (not client_id or o['client_id'] == client_id)
    ]

    total_revenue = sum(o['ddi_rate'] for o in filtered)
    total_cups = len(filtered)
    total_cup_cost = sum(o.get('cup_cost', 0) for o in filtered)

    lab_confirmations = [o for o in filtered if o.get('lab_order_id')]
    lab_revenue = len(lab_confirmations) * 85   # $85 DDI rate for confirmation
    lab_cost = len(lab_confirmations) * 47      # ~$47 avg DDI cost

    negatives = len([o for o in filtered if 'NEGATIVE' in o.get('overall_result', '')])
    non_negatives = len([o for o in filtered if 'NON_NEG' in o.get('overall_result', '')])
    confirmed_positives = len([o for o in filtered if o.get('lab_result') == 'POSITIVE'])

    total_rev = total_revenue + lab_revenue
    total_cost = total_cup_cost + lab_cost + (len(filtered) * 5)  # $5/test admin supplies
    total_margin = total_rev - total_cost

    return {
        'period_days':        days,
        'client_id':          client_id or 'ALL',
        'total_tests':        total_cups,
        'test_revenue':       total_revenue,
        'lab_confirmation_revenue': lab_revenue,
        'total_revenue':      total_rev,
        'total_cost':         round(total_cost, 2),
        'total_margin':       round(total_margin, 2),
        'margin_pct':         f'{round(total_margin / total_rev * 100, 1) if total_rev else 0}%',
        'results_breakdown': {
            'negative':           negatives,
            'non_negative_screen': non_negatives,
            'confirmed_positive': confirmed_positives,
            'non_negative_rate':  f'{round(non_negatives / total_cups * 100, 1) if total_cups else 0}%',
        },
        'generated_at': datetime.now().isoformat(),
    }


def get_dashboard() -> dict:
    """POCT operations dashboard."""
    orders = _load(ORDERS_FILE)
    inventory = get_inventory_status()

    pending_lab = [o for o in orders if o['status'] == 'PENDING_LAB_CONFIRMATION']
    lab_sent = [o for o in orders if o['status'] == 'LAB_CONFIRMATION_SENT']
    awaiting_results = [o for o in orders if o['status'] == 'COLLECTION_IN_PROGRESS']
    confirmed_positives = [o for o in orders if o.get('lab_result') == 'POSITIVE']

    alerts = []
    if pending_lab:
        alerts.append(f'{len(pending_lab)} non-negative orders need to be sent to lab for confirmation')
    if inventory.get('reorder_needed'):
        alerts.append(f'Reorder needed: {", ".join(inventory["reorder_needed"])}-panel cups')
    for panel, data in inventory.get('inventory', {}).items():
        alerts.extend(data.get('alerts', []))

    return {
        'generated_at':          datetime.now().isoformat(),
        'orders': {
            'in_progress':       len(awaiting_results),
            'pending_lab':       len(pending_lab),
            'awaiting_lab_result': len(lab_sent),
            'confirmed_positive': len(confirmed_positives),
        },
        'inventory':             inventory['inventory'],
        'reorder_needed':        inventory['reorder_needed'],
        'alerts':                alerts,
        'revenue_30_days':       get_revenue_report(days=30),
        'supplier':              '12PanelNow | brenda@slashmedical.com | $2.09/cup (12-panel)',
    }


# ═══════════════════════════════════════════════════════════════════
# API ROUTES
# ═══════════════════════════════════════════════════════════════════

@prism_poct.route('/prism/poct/dashboard', methods=['GET'])
def api_dashboard():
    return jsonify(get_dashboard())


@prism_poct.route('/prism/poct/procedure', methods=['GET'])
def api_collection_procedure():
    """Return the full 10-step POCT collection procedure."""
    panel = request.args.get('panel', '12')
    return jsonify({
        'panel':     PANELS.get(panel, {}).get('label', '12-Panel'),
        'steps':     COLLECTION_PROCEDURE,
        'read_time': f'{PANELS.get(panel, PANELS["12"])["read_time_minutes"]} minutes',
        'warning':   'Do NOT read results before 5 minutes. Do NOT read after 8 minutes.',
    })


@prism_poct.route('/prism/poct/panels', methods=['GET'])
def api_panels():
    """List all supported panels with pricing."""
    return jsonify({'panels': PANELS})


# --- Inventory ---

@prism_poct.route('/prism/poct/inventory', methods=['GET'])
def api_inventory():
    return jsonify(get_inventory_status())


@prism_poct.route('/prism/poct/inventory', methods=['POST'])
def api_add_inventory():
    data = request.get_json() or {}
    required = ['panel', 'quantity', 'lot_number', 'expiration_date']
    for f in required:
        if not data.get(f):
            return jsonify({'error': f'Missing required field: {f}'}), 400
    result = add_inventory(
        panel=data['panel'],
        quantity=int(data['quantity']),
        lot_number=data['lot_number'],
        expiration_date=data['expiration_date'],
        supplier=data.get('supplier', '12PanelNow'),
        cost_per_cup=data.get('cost_per_cup'),
        po_number=data.get('po_number', ''),
    )
    return jsonify(result), 201


# --- Orders ---

@prism_poct.route('/prism/poct/orders', methods=['GET'])
def api_list_orders():
    orders = _load(ORDERS_FILE)
    status_filter = request.args.get('status')
    client_filter = request.args.get('client_id')
    if status_filter:
        orders = [o for o in orders if o['status'] == status_filter]
    if client_filter:
        orders = [o for o in orders if o['client_id'] == client_filter]
    return jsonify({'orders': orders, 'count': len(orders)})


@prism_poct.route('/prism/poct/orders', methods=['POST'])
def api_create_order():
    data = request.get_json() or {}
    required = ['client_id', 'client_name', 'donor_name', 'donor_id_type', 'donor_id_last4']
    for f in required:
        if not data.get(f):
            return jsonify({'error': f'Missing required field: {f}'}), 400
    result = create_poct_order(
        client_id=data['client_id'],
        client_name=data['client_name'],
        donor_name=data['donor_name'],
        donor_id_type=data['donor_id_type'],
        donor_id_last4=data['donor_id_last4'],
        panel=data.get('panel', '12'),
        reason=data.get('reason', ''),
        employer_id=data.get('employer_id', ''),
        observer_required=data.get('observer_required', False),
        notes=data.get('notes', ''),
    )
    status = 400 if 'error' in result else 201
    return jsonify(result), status


@prism_poct.route('/prism/poct/orders/<order_id>', methods=['GET'])
def api_get_order(order_id):
    orders = _load(ORDERS_FILE)
    for o in orders:
        if o['id'] == order_id:
            return jsonify(o)
    return jsonify({'error': 'Order not found'}), 404


@prism_poct.route('/prism/poct/orders/<order_id>/procedure/<int:step>', methods=['POST'])
def api_complete_step(order_id, step):
    return jsonify(complete_procedure_step(order_id, step))


@prism_poct.route('/prism/poct/orders/<order_id>/results', methods=['POST'])
def api_record_results(order_id):
    data = request.get_json() or {}
    if not data.get('results') or not data.get('collector_name'):
        return jsonify({'error': 'results and collector_name are required'}), 400
    result = record_results(
        order_id=order_id,
        results=data['results'],
        collector_name=data['collector_name'],
        read_time=data.get('read_time'),
        temperature_ok=data.get('temperature_ok', True),
        temperature_reading=data.get('temperature_reading', ''),
        notes=data.get('notes', ''),
    )
    return jsonify(result)


@prism_poct.route('/prism/poct/orders/<order_id>/send-to-lab', methods=['POST'])
def api_send_to_lab(order_id):
    data = request.get_json() or {}
    result = send_to_lab(
        order_id=order_id,
        lab_name=data.get('lab_name', 'Quest Diagnostics'),
        tracking_number=data.get('tracking_number', ''),
        notes=data.get('notes', ''),
    )
    return jsonify(result)


@prism_poct.route('/prism/poct/orders/<order_id>/lab-result', methods=['POST'])
def api_lab_result(order_id):
    data = request.get_json() or {}
    if not data.get('lab_result'):
        return jsonify({'error': 'lab_result is required (NEGATIVE | POSITIVE | INVALID)'}), 400
    result = record_lab_result(
        order_id=order_id,
        lab_result=data['lab_result'],
        confirmed_substances=data.get('confirmed_substances', []),
        mro_name=data.get('mro_name', ''),
        lab_report_number=data.get('lab_report_number', ''),
    )
    return jsonify(result)


# --- Revenue ---

@prism_poct.route('/prism/poct/revenue', methods=['GET'])
def api_revenue():
    client_id = request.args.get('client_id')
    days = int(request.args.get('days', 30))
    return jsonify(get_revenue_report(client_id=client_id, days=days))
