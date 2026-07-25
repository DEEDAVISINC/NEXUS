"""
NEXUS OPS — workforce session + PRISM Desk façade (Phase A/B).

Auth JWT lives on Netlify ops-portal (OPS_AUTH_SECRET). These routes are called
after the function verifies the session email.

See NEXUS_OPS_MASTER.md.
"""
from __future__ import annotations

import json
import os
from datetime import datetime

from flask import Blueprint, jsonify, request

ops_portal = Blueprint('ops_portal', __name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OPS_DATA_DIR = os.path.join(BASE_DIR, 'uploads', 'ops')
DEMO_QUEUE_FILE = os.path.join(OPS_DATA_DIR, 'prism_demo_queue.json')

LEVEL_TO_ROLE = {
    'SUP': 'supervisor',
    'DIR': 'supervisor',
    'MGR': 'manager',
    'AGT': 'cca',
    'STF': 'cca',
}

PHASE_DESKS = [
    {
        'id': 'prism',
        'label': 'PRISM Desk',
        'status': 'ready',
        'description': 'Trip / member coordination queues (account-scoped)',
    },
    {
        'id': 'claims',
        'label': 'Claims',
        'status': 'coming_soon',
        'description': 'Data entry + manager authorization (Phase D)',
    },
]

# Trip payer / client label → HR account code(s)
PAYER_TO_CODES = {
    'hap caresource': ['CSRC'],
    'hap': ['CSRC'],
    'caresource': ['CSRC'],
    'caresource michigan': ['CSRC'],
    'molina': ['MOLN'],
    'molina healthcare': ['MOLN'],
    'molina healthcare of michigan': ['MOLN'],
    'molina healthcare michigan': ['MOLN'],
    'cts': ['CTS'],
    'community transition': ['CTS'],
    'meridian': ['MER'],
    'meridian health plan': ['MER'],
    'haven': ['HAVN'],
}

OPS_ALLOWED_STATUSES = {
    'New', 'In Progress', 'Pending Info', 'Scheduled', 'Dispatched',
    'On Hold', 'Agent Assigned',
}


def _accounts_list(account_field: str) -> list:
    from hr_onboarding_api import _account_code, _account_emoji

    parts = [p.strip() for p in (account_field or '').split(',') if p.strip()]
    out = []
    for name in parts:
        out.append({
            'name': name,
            'code': _account_code(name),
            'emoji': _account_emoji(name) or '',
        })
    return out


def _role_from_level(level_name: str) -> str:
    from hr_onboarding_api import _level_code

    code = (_level_code(level_name) or 'STF').upper()
    return LEVEL_TO_ROLE.get(code, 'cca')


def _build_session_payload(rec: dict) -> dict:
    from hr_onboarding_api import _can_work_internal, _level_code

    ok, reason = _can_work_internal(rec)
    role = _role_from_level(rec.get('level') or '')
    accounts = _accounts_list(rec.get('account') or '')
    desks = []
    for d in PHASE_DESKS:
        entry = dict(d)
        if d['id'] == 'prism':
            entry['unlocked'] = bool(ok)
            entry['lockReason'] = None if ok else reason
        else:
            entry['unlocked'] = False
            entry['lockReason'] = 'Coming in a later phase'
        desks.append(entry)

    return {
        'ok': True,
        'person': {
            'id': rec.get('id'),
            'name': rec.get('name') or '',
            'email': rec.get('email') or '',
            'companyEmail': rec.get('companyEmail') or '',
            'workerType': rec.get('workerType') or '',
            'roleTitle': rec.get('role') or '',
            'division': rec.get('division') or '',
            'level': rec.get('level') or '',
            'levelCode': _level_code(rec.get('level') or ''),
            'personnelNumber': rec.get('personnelNumber') or '',
            'status': rec.get('status') or '',
        },
        'opsRole': role,
        'accounts': accounts,
        'desks': desks,
        'canWork': bool(ok),
        'canWorkReason': reason,
        'sessionPolicy': {
            'idleMinutes': 15,
            'warnMinutes': 13,
            'absoluteHours': 12,
        },
    }


def _person_from_email(email: str):
    from hr_onboarding_api import _find_by_email, _can_work_internal

    email = (email or '').strip().lower()
    if not email or '@' not in email:
        return None, None, 'Valid email required'
    rec, _, _ = _find_by_email(email)
    if not rec:
        return None, None, 'No active GATEWAY record for that email'
    ok, reason = _can_work_internal(rec)
    return rec, ok, reason


def _codes_for_payer(*labels) -> set:
    codes = set()
    for raw in labels:
        s = (raw or '').strip().lower()
        if not s:
            continue
        if s in PAYER_TO_CODES:
            codes.update(PAYER_TO_CODES[s])
            continue
        for key, vals in PAYER_TO_CODES.items():
            if key in s or s in key:
                codes.update(vals)
    return codes


def _order_payer(order: dict) -> str:
    details = order.get('details') or {}
    return (
        details.get('payer')
        or details.get('payer_name')
        or order.get('payer')
        or order.get('client')
        or ''
    )


def _order_account_codes(order: dict) -> set:
    payer = _order_payer(order)
    client = order.get('client') or ''
    codes = _codes_for_payer(payer, client)
    if order.get('ops_account_code'):
        codes.add(str(order['ops_account_code']).upper())
    return codes


def _member_name(order: dict) -> str:
    details = order.get('details') or {}
    return (
        order.get('signer')
        or details.get('member_name')
        or order.get('subject_name')
        or 'Member'
    )


def _mask_id(value: str) -> str:
    s = ''.join(ch for ch in str(value or '') if ch.isalnum())
    if len(s) < 4:
        return ''
    return '••••' + s[-4:]


def _sla_age_minutes(order: dict) -> int:
    raw = order.get('created_at') or order.get('ops_created_at') or ''
    if not raw:
        return 0
    try:
        ts = datetime.fromisoformat(raw.replace('Z', ''))
        return max(0, int((datetime.now() - ts).total_seconds() // 60))
    except Exception:
        return 0


def _queue_card(order: dict) -> dict:
    details = order.get('details') or {}
    medicaid = details.get('member_medicaid_id') or details.get('medicaid_id') or ''
    payer = _order_payer(order)
    codes = list(_order_account_codes(order))
    return {
        'id': order.get('id'),
        'nemtOrderId': details.get('nemt_order_id') or order.get('nemt_order_id'),
        'status': order.get('status') or 'New',
        'payer': payer,
        'accountCode': codes[0] if codes else '',
        'accountCodes': codes,
        'memberName': _member_name(order),
        'memberIdLast4': _mask_id(medicaid),
        'pickupTime': details.get('pickup_time') or order.get('time') or '',
        'pickupDate': details.get('pickup_date') or order.get('date') or '',
        'priority': order.get('priority') or 'Standard',
        'notesPreview': (order.get('notes') or '')[:160],
        'notes': order.get('notes') or '',
        'claimedBy': order.get('ops_claimed_by'),
        'claimedEmail': order.get('ops_claimed_email'),
        'claimedAt': order.get('ops_claimed_at'),
        'slaAgeMinutes': _sla_age_minutes(order),
        'type': order.get('type') or order.get('service_key') or 'nemt',
        'isDemo': bool(order.get('ops_demo')),
    }


def _load_demo_orders() -> list:
    os.makedirs(OPS_DATA_DIR, exist_ok=True)
    if not os.path.exists(DEMO_QUEUE_FILE):
        demo = [
            {
                'id': 'OPS-DEMO-HAP-001',
                'status': 'New',
                'type': 'nemt',
                'service_key': 'nemt',
                'client': 'HAP CareSource Member',
                'signer': 'Jordan Avery',
                'priority': 'Same Day',
                'notes': 'Demo trip — dialysis return. Confirm pickup window.',
                'date': datetime.now().strftime('%Y-%m-%d'),
                'time': '14:30',
                'created_at': datetime.now().isoformat(),
                'ops_demo': True,
                'ops_account_code': 'CSRC',
                'details': {
                    'payer': 'HAP CareSource',
                    'member_medicaid_id': 'MC123456789',
                    'pickup_date': datetime.now().strftime('%Y-%m-%d'),
                    'pickup_time': '14:30',
                },
            },
            {
                'id': 'OPS-DEMO-HAP-002',
                'status': 'New',
                'type': 'nemt',
                'service_key': 'nemt',
                'client': 'HAP CareSource Member',
                'signer': 'Riley Morgan',
                'priority': 'Standard',
                'notes': 'Demo trip — specialist follow-up. Needs eligibility check.',
                'date': datetime.now().strftime('%Y-%m-%d'),
                'time': '16:00',
                'created_at': datetime.now().isoformat(),
                'ops_demo': True,
                'ops_account_code': 'CSRC',
                'details': {
                    'payer': 'HAP CareSource',
                    'member_medicaid_id': 'MC987654321',
                    'pickup_date': datetime.now().strftime('%Y-%m-%d'),
                    'pickup_time': '16:00',
                },
            },
            {
                'id': 'OPS-DEMO-MOL-001',
                'status': 'New',
                'type': 'nemt',
                'service_key': 'nemt',
                'client': 'Molina Member',
                'signer': 'Casey Quinn',
                'priority': 'STAT',
                'notes': 'Demo Molina trip — only visible to Molina-assigned CCAs.',
                'date': datetime.now().strftime('%Y-%m-%d'),
                'time': '11:15',
                'created_at': datetime.now().isoformat(),
                'ops_demo': True,
                'ops_account_code': 'MOLN',
                'details': {
                    'payer': 'Molina Healthcare Michigan',
                    'member_medicaid_id': 'ML555444333',
                    'pickup_date': datetime.now().strftime('%Y-%m-%d'),
                    'pickup_time': '11:15',
                },
            },
        ]
        with open(DEMO_QUEUE_FILE, 'w') as fp:
            json.dump(demo, fp, indent=2)
        return demo
    try:
        with open(DEMO_QUEUE_FILE, 'r') as fp:
            return json.load(fp) or []
    except Exception:
        return []


def _save_demo_orders(orders: list) -> None:
    os.makedirs(OPS_DATA_DIR, exist_ok=True)
    with open(DEMO_QUEUE_FILE, 'w') as fp:
        json.dump(orders, fp, indent=2)


def _all_orders() -> list:
    from prism_orders_api import ORDERS_FILE, _load

    real = _load(ORDERS_FILE, []) or []
    # Prefer real NEMT/PRISM work; always include demo store for empty / training
    demo = _load_demo_orders()
    # De-dupe by id (real wins)
    seen = {o.get('id') for o in real}
    merged = list(real)
    for d in demo:
        if d.get('id') not in seen:
            merged.append(d)
    return merged


def _find_order(order_id: str):
    from prism_orders_api import ORDERS_FILE, _load, _save

    orders = _load(ORDERS_FILE, []) or []
    for i, o in enumerate(orders):
        if o.get('id') == order_id:
            return o, i, orders, 'real', ORDERS_FILE, _save
    demo = _load_demo_orders()
    for i, o in enumerate(demo):
        if o.get('id') == order_id:
            return o, i, demo, 'demo', DEMO_QUEUE_FILE, None
    return None, None, None, None, None, None


def _persist_order(store, orders, kind, save_fn):
    if kind == 'real' and save_fn:
        from prism_orders_api import ORDERS_FILE
        save_fn(ORDERS_FILE, orders)
    else:
        _save_demo_orders(orders)


def _account_filter_codes(rec: dict) -> set:
    accounts = _accounts_list(rec.get('account') or '')
    codes = {a['code'] for a in accounts if a.get('code')}
    # CareSource HR name also maps to CSRC even if code lookup fails
    for a in accounts:
        name = (a.get('name') or '').lower()
        codes |= _codes_for_payer(name)
    return codes


def _can_see_order(order: dict, account_codes: set, ops_role: str) -> bool:
    if not account_codes:
        # No account assignment — supervisors see all; CCAs see nothing yet
        return ops_role in ('supervisor', 'manager')
    order_codes = _order_account_codes(order)
    if not order_codes:
        return ops_role in ('supervisor', 'manager')
    return bool(order_codes & account_codes)


# ─── Session / health ─────────────────────────────────────────────

@ops_portal.route('/ops/session', methods=['GET'])
def ops_session():
    email = (request.args.get('email') or '').strip().lower()
    rec, ok, reason = _person_from_email(email)
    if reason == 'Valid email required':
        return jsonify({'ok': False, 'error': reason}), 400
    if not rec:
        return jsonify({
            'ok': False,
            'error': 'No active GATEWAY record for that email. Finish onboarding at gateway.deedavis.biz or ask HR.',
        }), 404
    return jsonify(_build_session_payload(rec))


@ops_portal.route('/ops/health', methods=['GET'])
def ops_health():
    return jsonify({'ok': True, 'service': 'nexus-ops-api', 'phase': 'B'})


# ─── PRISM Desk queue ─────────────────────────────────────────────

@ops_portal.route('/ops/prism/queue', methods=['GET'])
def ops_prism_queue():
    email = (request.args.get('email') or '').strip().lower()
    rec, can_work, reason = _person_from_email(email)
    if not rec:
        return jsonify({'ok': False, 'error': reason or 'Unauthorized'}), 404 if 'GATEWAY' in (reason or '') else 400
    if not can_work:
        return jsonify({
            'ok': False,
            'error': 'Desks locked — GATEWAY can-work failed',
            'canWorkReason': reason,
            'items': [],
        }), 403

    ops_role = _role_from_level(rec.get('level') or '')
    account_codes = _account_filter_codes(rec)
    mine = request.args.get('mine', '').lower() in ('1', 'true', 'yes')

    items = []
    for order in _all_orders():
        status = (order.get('status') or '').lower()
        if status in ('complete', 'completed', 'cancelled', 'canceled'):
            continue
        if not _can_see_order(order, account_codes, ops_role):
            continue
        claimed_email = (order.get('ops_claimed_email') or '').lower()
        if mine and claimed_email != email:
            continue
        # Default board: unclaimed OR claimed by me
        if not mine and claimed_email and claimed_email != email and ops_role == 'cca':
            continue
        items.append(_queue_card(order))

    items.sort(key=lambda x: (-(1 if x.get('priority') == 'STAT' else 0), -x.get('slaAgeMinutes', 0)))
    return jsonify({
        'ok': True,
        'items': items,
        'total': len(items),
        'accountCodes': sorted(account_codes),
        'opsRole': ops_role,
        'email': email,
    })


@ops_portal.route('/ops/prism/items/<order_id>/claim', methods=['POST'])
def ops_prism_claim(order_id):
    data = request.get_json(silent=True) or {}
    email = (data.get('email') or request.args.get('email') or '').strip().lower()
    rec, can_work, reason = _person_from_email(email)
    if not rec:
        return jsonify({'ok': False, 'error': reason or 'Unauthorized'}), 404
    if not can_work:
        return jsonify({'ok': False, 'error': 'can-work blocked', 'canWorkReason': reason}), 403

    ops_role = _role_from_level(rec.get('level') or '')
    account_codes = _account_filter_codes(rec)
    order, idx, orders, kind, _, save_fn = _find_order(order_id)
    if not order:
        return jsonify({'ok': False, 'error': 'Item not found'}), 404
    if not _can_see_order(order, account_codes, ops_role):
        return jsonify({'ok': False, 'error': 'Not in your account queue'}), 403

    claimed = (order.get('ops_claimed_email') or '').lower()
    if claimed and claimed != email:
        return jsonify({
            'ok': False,
            'error': f'Already claimed by {order.get("ops_claimed_by") or claimed}',
            'item': _queue_card(order),
        }), 409

    order['ops_claimed_by'] = rec.get('name') or email
    order['ops_claimed_email'] = email
    order['ops_claimed_at'] = datetime.now().isoformat()
    if (order.get('status') or '').lower() in ('', 'new'):
        order['status'] = 'In Progress'
    order['updated_at'] = datetime.now().isoformat()
    orders[idx] = order
    _persist_order(None, orders, kind, save_fn)

    return jsonify({'ok': True, 'item': _queue_card(order)})


@ops_portal.route('/ops/prism/items/<order_id>/release', methods=['POST'])
def ops_prism_release(order_id):
    data = request.get_json(silent=True) or {}
    email = (data.get('email') or request.args.get('email') or '').strip().lower()
    force = bool(data.get('force'))
    rec, can_work, reason = _person_from_email(email)
    if not rec:
        return jsonify({'ok': False, 'error': reason or 'Unauthorized'}), 404
    if not can_work:
        return jsonify({'ok': False, 'error': 'can-work blocked', 'canWorkReason': reason}), 403

    ops_role = _role_from_level(rec.get('level') or '')
    order, idx, orders, kind, _, save_fn = _find_order(order_id)
    if not order:
        return jsonify({'ok': False, 'error': 'Item not found'}), 404

    claimed = (order.get('ops_claimed_email') or '').lower()
    if claimed and claimed != email and not (force and ops_role in ('supervisor', 'manager')):
        return jsonify({'ok': False, 'error': 'Only the claim owner or a supervisor can release'}), 403

    order['ops_claimed_by'] = None
    order['ops_claimed_email'] = None
    order['ops_claimed_at'] = None
    order['ops_released_at'] = datetime.now().isoformat()
    order['ops_released_by'] = email
    if (order.get('status') or '') == 'In Progress':
        order['status'] = 'New'
    order['updated_at'] = datetime.now().isoformat()
    orders[idx] = order
    _persist_order(None, orders, kind, save_fn)

    return jsonify({'ok': True, 'item': _queue_card(order)})


@ops_portal.route('/ops/prism/items/<order_id>', methods=['GET', 'PATCH'])
def ops_prism_item(order_id):
    if request.method == 'GET':
        email = (request.args.get('email') or '').strip().lower()
        rec, can_work, reason = _person_from_email(email)
        if not rec:
            return jsonify({'ok': False, 'error': reason or 'Unauthorized'}), 404
        if not can_work:
            return jsonify({'ok': False, 'error': 'can-work blocked'}), 403
        ops_role = _role_from_level(rec.get('level') or '')
        account_codes = _account_filter_codes(rec)
        order, _, _, _, _, _ = _find_order(order_id)
        if not order:
            return jsonify({'ok': False, 'error': 'Item not found'}), 404
        if not _can_see_order(order, account_codes, ops_role):
            return jsonify({'ok': False, 'error': 'Not in your account queue'}), 403
        return jsonify({'ok': True, 'item': _queue_card(order)})

    data = request.get_json(silent=True) or {}
    email = (data.get('email') or request.args.get('email') or '').strip().lower()
    rec, can_work, reason = _person_from_email(email)
    if not rec:
        return jsonify({'ok': False, 'error': reason or 'Unauthorized'}), 404
    if not can_work:
        return jsonify({'ok': False, 'error': 'can-work blocked'}), 403

    ops_role = _role_from_level(rec.get('level') or '')
    account_codes = _account_filter_codes(rec)
    order, idx, orders, kind, _, save_fn = _find_order(order_id)
    if not order:
        return jsonify({'ok': False, 'error': 'Item not found'}), 404
    if not _can_see_order(order, account_codes, ops_role):
        return jsonify({'ok': False, 'error': 'Not in your account queue'}), 403

    claimed = (order.get('ops_claimed_email') or '').lower()
    if claimed and claimed != email and ops_role == 'cca':
        return jsonify({'ok': False, 'error': 'Claim this item before editing'}), 403

    if 'notes' in data:
        order['notes'] = str(data.get('notes') or '')
    if 'status' in data:
        new_status = str(data.get('status') or '').strip()
        if new_status and new_status not in OPS_ALLOWED_STATUSES:
            return jsonify({
                'ok': False,
                'error': f'Status not allowed from OPS: {new_status}',
                'allowed': sorted(OPS_ALLOWED_STATUSES),
            }), 400
        if new_status:
            order['status'] = new_status

    order['updated_at'] = datetime.now().isoformat()
    order['ops_last_edit_by'] = email
    orders[idx] = order
    _persist_order(None, orders, kind, save_fn)
    return jsonify({'ok': True, 'item': _queue_card(order)})
