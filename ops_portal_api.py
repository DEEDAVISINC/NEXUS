"""
NEXUS OPS — workforce session + PRISM Desk façade (Phase A/B).

Auth JWT lives on Netlify ops-portal (OPS_AUTH_SECRET). These routes are called
after the function verifies the session email.

See NEXUS_OPS_MASTER.md.
"""
from __future__ import annotations

import json
import os
import re
from datetime import datetime, timedelta
from typing import Optional

from flask import Blueprint, jsonify, request

ops_portal = Blueprint('ops_portal', __name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OPS_DATA_DIR = os.path.join(BASE_DIR, 'uploads', 'ops')
DEMO_QUEUE_FILE = os.path.join(OPS_DATA_DIR, 'prism_demo_queue.json')
TIMECLOCK_FILE = os.path.join(OPS_DATA_DIR, 'timeclock.json')

# Build-time unlock: finish OPS without blocking on unfinished GATEWAY Phase 1.
# Set OPS_RELAX_CAN_WORK=0 (or remove) when portals are wired for production.
def _relax_can_work() -> bool:
    return os.environ.get('OPS_RELAX_CAN_WORK', '').strip().lower() in ('1', 'true', 'yes', 'on')


def _effective_can_work(rec: dict):
    """Returns (ok, reason, relaxed). GATEWAY truth always computed; relax only for OPS desks."""
    from hr_onboarding_api import _can_work_internal

    ok, reason = _can_work_internal(rec)
    if ok:
        return True, reason, False
    if _relax_can_work() and (rec.get('status') or '') == 'Active':
        return True, f'OPS build mode — GATEWAY still blocked: {reason}', True
    return False, reason, False

LEVEL_TO_ROLE = {
    'SUP': 'supervisor',
    'DIR': 'supervisor',
    'MGR': 'manager',
    'ADM': 'admin',
    'OWN': 'admin',
    'CEO': 'admin',
    'AGT': 'cca',
    'STF': 'cca',
}

# Ultimate owner key — Dieasha D. Davis / info@deedavis.biz
# Maps to opsRole=admin: all sectors + all supervisor abilities + all management abilities.
# Same site ops.deedavis.biz — role floors (care / supervisor / management / owner).
OPS_OWNER_EMAILS = frozenset({
    'info@deedavis.biz',  # primary ultimate key
    'dieasha@deedavis.biz',
    'dee@deedavis.biz',
})

PHASE_DESKS = [
    {
        'id': 'prism',
        'label': 'PRISM Desk',
        'status': 'ready',
        'description': 'Orders, agents, live board — scoped to your employed accounts (owners see all)',
    },
    {
        'id': 'claims',
        'label': 'Claims',
        'status': 'coming_soon',
        'description': 'Data entry + manager authorization (Phase D)',
    },
]

# Trip payer / client label → HR account code(s)
# Molina HIDE SNP PSA = TWO lanes (never collapse to NEMT-only):
#   MOLN = NMT / NEMT dispatch
#   CTS  = Community Transition Services (Attachment B / T2038) — separate PRISM lifecycle
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
    'community transition services': ['CTS'],
    'molina cts': ['CTS'],
    'molina community transition': ['CTS'],
    'meridian': ['MER'],
    'meridian health plan': ['MER'],
    'haven': ['HAVN'],
}

# GATEWAY "Molina" assignment includes the CTS product lane under the same PSA.
# CTS-only assignment does NOT auto-open all Molina NMT (keep CTS scoped).
RELATED_ACCOUNT_CODES = {
    'MOLN': frozenset({'CTS'}),
}

OPS_ALLOWED_STATUSES = {
    'New', 'In Progress', 'Pending Info', 'Scheduled', 'Dispatched',
    'On Hold', 'Agent Assigned', 'Complete', 'Completed',
}

# Care-desk status (emoji chips) — maps to PRISM status for write-back
CARE_STATUSES = {
    'New': {'emoji': '🆕', 'label': 'New', 'prism': 'New'},
    'Working': {'emoji': '🔧', 'label': 'Working', 'prism': 'In Progress'},
    'Waiting on Auth': {'emoji': '⏳', 'label': 'Waiting on Auth', 'prism': 'Pending Info'},
    'Done': {'emoji': '✅', 'label': 'Done', 'prism': 'Complete'},
}

SLA_HOURS_BY_PRIORITY = {
    'STAT': 2,
    'Same Day': 8,
    'Standard': 24,
}

STEPPER = ('Received', 'Assigned', 'In Progress', 'Completed')


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


def _role_from_level(level_name: str, email: str = '') -> str:
    """Map GATEWAY level → OPS role. Owner/exec emails always get admin (full PRISM view)."""
    from hr_onboarding_api import _level_code

    em = (email or '').strip().lower()
    if em in OPS_OWNER_EMAILS:
        return 'admin'
    name = (level_name or '').strip().lower()
    if any(k in name for k in ('president', 'ceo', 'owner', 'admin', 'executive')):
        return 'admin'
    if 'director' in name:
        return 'supervisor'
    if 'manager' in name:
        return 'manager'
    if 'supervisor' in name:
        return 'supervisor'
    code = (_level_code(level_name) or 'STF').upper()
    return LEVEL_TO_ROLE.get(code, 'cca')


def _build_session_payload(rec: dict) -> dict:
    from hr_onboarding_api import _level_code

    ok, reason, relaxed = _effective_can_work(rec)
    role = _role_from_level(rec.get('level') or '', rec.get('email') or '')
    accounts = _accounts_list(rec.get('account') or '')
    # Surface CTS as a related Molina lane when Molina is assigned but CTS isn't listed yet
    account_codes = {a.get('code') for a in accounts if a.get('code')}
    if 'MOLN' in account_codes and 'CTS' not in account_codes:
        accounts.append({
            'name': 'CTS (Molina HIDE SNP — Community Transition)',
            'code': 'CTS',
            'emoji': '🏠',
            'relatedTo': 'MOLN',
        })
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
            'personnelNumberCore': rec.get('personnelNumberCore') or '',
            'status': rec.get('status') or '',
        },
        'opsRole': role,
        'floor': _floor_for_role(role),
        'capabilities': _capabilities_for_role(role),
        'accounts': accounts,
        'accountCodes': sorted(_account_filter_codes(rec)),
        'seeAllAccounts': _sees_all_accounts(role),
        'desks': desks,
        'canWork': bool(ok),
        'canWorkReason': reason,
        'canWorkRelaxed': bool(relaxed),
        'relaxCanWorkEnv': _relax_can_work(),
        'sessionPolicy': {
            'idleMinutes': 15,
            'warnMinutes': 13,
            'absoluteHours': 12,
        },
        'opsReadiness': {
            'gatewayCanWorkEnforced': not _relax_can_work(),
            'toGoLive': [
                'Finish GATEWAY can-work for Active workforce',
                'Unset OPS_RELAX_CAN_WORK on PythonAnywhere (or set =0)',
                'Prefer real PRISM orders; use Hide demo in queue when training done',
            ] if _relax_can_work() else [],
        },
    }


def _person_from_email(email: str):
    from hr_onboarding_api import _find_by_email

    email = (email or '').strip().lower()
    if not email or '@' not in email:
        return None, None, 'Valid email required'
    rec, _, _ = _find_by_email(email)
    if not rec:
        return None, None, 'No active GATEWAY record for that email'
    ok, reason, _relaxed = _effective_can_work(rec)
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


def _order_service_lane(order: dict) -> str:
    """Return care product lane: cts | nmt | nemt | other."""
    details = order.get('details') or {}
    blob = ' '.join([
        str(order.get('type') or ''),
        str(order.get('service_key') or ''),
        str(details.get('service_type') or ''),
        str(details.get('service_lane') or ''),
        str(order.get('ops_account_code') or ''),
        str(order.get('notes') or '')[:80],
    ]).lower()
    if 'cts' in blob or 'community transition' in blob or 't2038' in blob:
        return 'cts'
    if 'nmt' in blob or 'non-medical' in blob or 'non medical' in blob:
        return 'nmt'
    if 'nemt' in blob:
        return 'nemt'
    return (order.get('service_key') or order.get('type') or 'other').lower()


def _order_account_codes(order: dict) -> set:
    payer = _order_payer(order)
    client = order.get('client') or ''
    codes = _codes_for_payer(payer, client)
    if order.get('ops_account_code'):
        codes.add(str(order['ops_account_code']).upper())
    # Molina CTS referrals must route to CTS even when payer string is Molina
    if _order_service_lane(order) == 'cts':
        codes.discard('MOLN')
        codes.add('CTS')
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


def _parse_ts(raw: str):
    if not raw:
        return None
    try:
        return datetime.fromisoformat(str(raw).replace('Z', ''))
    except Exception:
        return None


def _sla_age_minutes(order: dict) -> int:
    ts = _parse_ts(order.get('created_at') or order.get('ops_created_at') or '')
    if not ts:
        return 0
    return max(0, int((datetime.now() - ts).total_seconds() // 60))


def _sla_due_at(order: dict):
    explicit = _parse_ts(order.get('ops_sla_due_at') or '')
    if explicit:
        return explicit
    created = _parse_ts(order.get('created_at') or order.get('ops_created_at') or '')
    if not created:
        return None
    hours = SLA_HOURS_BY_PRIORITY.get(order.get('priority') or 'Standard', 24)
    return created + timedelta(hours=hours)


def _sla_payload(order: dict) -> dict:
    due = _sla_due_at(order)
    if not due:
        return {
            'slaAgeMinutes': _sla_age_minutes(order),
            'slaDueAt': None,
            'slaMinutesRemaining': None,
            'slaTone': 'unknown',
            'slaEmoji': '⚪',
            'slaLabel': 'No SLA',
        }
    remaining = int((due - datetime.now()).total_seconds() // 60)
    if remaining < 0:
        tone, emoji, label = 'overdue', '🔴', 'Overdue'
    elif remaining <= 60:
        tone, emoji, label = 'tight', '🟡', 'Tight'
    else:
        tone, emoji, label = 'ok', '🟢', 'On track'
    return {
        'slaAgeMinutes': _sla_age_minutes(order),
        'slaDueAt': due.isoformat(),
        'slaMinutesRemaining': remaining,
        'slaTone': tone,
        'slaEmoji': emoji,
        'slaLabel': label,
    }


def _care_status_from_order(order: dict) -> str:
    explicit = (order.get('ops_care_status') or '').strip()
    if explicit in CARE_STATUSES:
        return explicit
    status = (order.get('status') or 'New').strip().lower()
    if status in ('complete', 'completed', 'done', 'cancelled', 'canceled'):
        return 'Done'
    if status in ('pending info', 'on hold', 'waiting'):
        return 'Waiting on Auth'
    if order.get('ops_claimed_email') or status in (
        'in progress', 'agent assigned', 'scheduled', 'dispatched', 'working'
    ):
        return 'Working'
    return 'New'


def _stepper_state(order: dict) -> dict:
    care = _care_status_from_order(order)
    claimed = bool(order.get('ops_claimed_email'))
    if care == 'Done':
        step = 3
    elif care in ('Working', 'Waiting on Auth'):
        step = 2
    elif claimed:
        step = 1
    else:
        step = 0
    return {
        'steps': list(STEPPER),
        'activeIndex': step,
        'activeLabel': STEPPER[step],
    }


def _ensure_activity(order: dict) -> list:
    log = order.get('ops_activity')
    if not isinstance(log, list):
        log = []
        order['ops_activity'] = log
    return log


def _append_activity(order: dict, actor_name: str, actor_email: str, entry_type: str, text: str):
    log = _ensure_activity(order)
    log.append({
        'ts': datetime.utcnow().isoformat() + 'Z',
        'actor': actor_name or actor_email,
        'actorEmail': actor_email,
        'type': entry_type,
        'text': (text or '').strip(),
    })


def _matches_search(order: dict, q: str) -> bool:
    if not q:
        return True
    needle = q.strip().lower()
    if not needle:
        return True
    details = order.get('details') or {}
    hay = ' '.join([
        str(order.get('id') or ''),
        str(_member_name(order) or ''),
        str(_order_payer(order) or ''),
        str(details.get('member_medicaid_id') or ''),
        str(details.get('medicaid_id') or ''),
        str(details.get('member_phone') or details.get('phone') or ''),
        str(details.get('authorization') or details.get('auth_number') or order.get('authorization') or ''),
        str(order.get('notes') or ''),
        str(order.get('ops_claimed_by') or ''),
    ]).lower()
    return needle in hay


def _queue_card(order: dict, detail: bool = False) -> dict:
    details = order.get('details') or {}
    medicaid = details.get('member_medicaid_id') or details.get('medicaid_id') or ''
    phone = details.get('member_phone') or details.get('phone') or order.get('phone') or ''
    auth = details.get('authorization') or details.get('auth_number') or order.get('authorization') or ''
    payer = _order_payer(order)
    codes = list(_order_account_codes(order))
    care = _care_status_from_order(order)
    care_meta = CARE_STATUSES[care]
    sla = _sla_payload(order)
    card = {
        'id': order.get('id'),
        'nemtOrderId': details.get('nemt_order_id') or order.get('nemt_order_id'),
        'status': order.get('status') or 'New',
        'careStatus': care,
        'careEmoji': care_meta['emoji'],
        'careLabel': care_meta['label'],
        'payer': payer,
        'accountCode': codes[0] if codes else '',
        'accountCodes': codes,
        'memberName': _member_name(order),
        'memberIdLast4': _mask_id(medicaid),
        'memberId': medicaid if detail else '',
        'memberPhone': phone,
        'authorization': auth,
        'serviceType': order.get('type') or order.get('service_key') or details.get('service_type') or 'nemt',
        'serviceLane': _order_service_lane(order),
        'dateReceived': (order.get('created_at') or order.get('ops_created_at') or '')[:10],
        'intakeNotes': order.get('notes') or details.get('intake_notes') or '',
        'pickupTime': details.get('pickup_time') or order.get('time') or '',
        'pickupDate': details.get('pickup_date') or order.get('date') or '',
        'priority': order.get('priority') or 'Standard',
        'notesPreview': (order.get('notes') or '')[:160],
        'notes': order.get('notes') or '',
        'callbackAt': order.get('ops_callback_at') or '',
        'callbackNote': order.get('ops_callback_note') or '',
        'claimedBy': order.get('ops_claimed_by'),
        'claimedEmail': order.get('ops_claimed_email'),
        'claimedAt': order.get('ops_claimed_at'),
        'assignmentRequests': [
            {
                'email': r.get('email'),
                'name': r.get('name') or r.get('email'),
                'at': r.get('at') or '',
            }
            for r in _request_entries(order)
        ],
        'requestCount': len(_request_entries(order)),
        'stepper': _stepper_state(order),
        'type': order.get('type') or order.get('service_key') or 'nemt',
        'isDemo': bool(order.get('ops_demo')),
        'needsForceRelease': (
            bool(order.get('ops_claimed_email'))
            and (care in ('Working', 'Waiting on Auth') or (order.get('status') or '') == 'In Progress')
        ),
        **sla,
    }
    if detail:
        card['activity'] = list(_ensure_activity(order))
        card['allowedCareStatuses'] = [
            {'key': k, 'emoji': v['emoji'], 'label': v['label']} for k, v in CARE_STATUSES.items()
        ]
        card['calendarEvents'] = _order_to_calendar_events(order)
    return card


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
                'notes': 'Demo Molina NMT — Molina-assigned CCAs (MOLN + CTS lanes).',
                'date': datetime.now().strftime('%Y-%m-%d'),
                'time': '11:15',
                'created_at': datetime.now().isoformat(),
                'ops_demo': True,
                'ops_account_code': 'MOLN',
                'details': {
                    'payer': 'Molina Healthcare Michigan',
                    'service_lane': 'nmt',
                    'member_medicaid_id': 'ML555444333',
                    'pickup_date': datetime.now().strftime('%Y-%m-%d'),
                    'pickup_time': '11:15',
                },
            },
            {
                'id': 'OPS-DEMO-MOL-CTS-001',
                'status': 'New',
                'type': 'cts',
                'service_key': 'cts',
                'client': 'Molina CTS Member',
                'signer': 'Avery Brooks',
                'priority': 'Standard',
                'notes': 'Demo Molina CTS (T2038) — not NMT. Visible on Molina or CTS assignment.',
                'date': datetime.now().strftime('%Y-%m-%d'),
                'time': '13:00',
                'created_at': datetime.now().isoformat(),
                'ops_demo': True,
                'ops_account_code': 'CTS',
                'details': {
                    'payer': 'Molina Healthcare Michigan',
                    'service_type': 'cts',
                    'service_lane': 'cts',
                    'member_medicaid_id': 'ML777888999',
                    'pickup_date': (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d'),
                    'pickup_time': '10:00',
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
    # Molina assignment → also CTS lane (same PSA; CTS is not a separate MCO)
    expanded = set(codes)
    for code in codes:
        expanded |= RELATED_ACCOUNT_CODES.get(str(code).upper(), frozenset())
    return expanded


def _sees_all_accounts(ops_role: str) -> bool:
    """Only owner/admin sees every sector. Everyone else is account-scoped."""
    return ops_role == 'admin'


def _can_see_order(order: dict, account_codes: set, ops_role: str) -> bool:
    # Owner/admin — full company queue. Agents, supervisors, managers — employed sectors only.
    if _sees_all_accounts(ops_role):
        return True
    if not account_codes:
        return False
    order_codes = _order_account_codes(order)
    if not order_codes:
        return False
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
    relax = _relax_can_work()
    return jsonify({
        'ok': True,
        'service': 'nexus-ops-api',
        'phase': 'C-floors',
        'relaxCanWork': relax,
        'productionReadyHint': (
            'Set OPS_RELAX_CAN_WORK=0 (or unset) on PythonAnywhere when GATEWAY can-work is real for the workforce.'
            if relax else 'GATEWAY can-work is enforced (relax mode off).'
        ),
        'features': [
            'sla', 'activity', 'search', 'mine-pool', 'my-day',
            'assign', 'batch-assign', 'agents', 'calendar',
            'supervisor-assign-only', 'request', 'force-release',
            'demo-filter', 'role-floors', 'request-inbox', 'aging', 'workforce-readiness',
            'timeclock',
        ],
        'timeclock': True,
    })


# ─── Timeclock (OPS owns punches → VERTEX HR owns pay) ─────────────

def _tc_now():
    return datetime.utcnow().replace(microsecond=0).isoformat() + 'Z'


def _tc_today_et() -> str:
    try:
        from zoneinfo import ZoneInfo
        return datetime.now(ZoneInfo('America/Detroit')).strftime('%Y-%m-%d')
    except Exception:
        return datetime.utcnow().strftime('%Y-%m-%d')


def _tc_load() -> list:
    os.makedirs(OPS_DATA_DIR, exist_ok=True)
    if not os.path.isfile(TIMECLOCK_FILE):
        return []
    try:
        with open(TIMECLOCK_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except Exception:
        return []


def _tc_save(rows: list) -> None:
    os.makedirs(OPS_DATA_DIR, exist_ok=True)
    with open(TIMECLOCK_FILE, 'w', encoding='utf-8') as f:
        json.dump(rows, f, indent=2)


def _tc_parse(iso: str):
    if not iso:
        return None
    try:
        return datetime.fromisoformat(str(iso).replace('Z', ''))
    except ValueError:
        return None


def _tc_minutes(in_at: str, out_at: Optional[str] = None) -> float:
    start = _tc_parse(in_at)
    end = _tc_parse(out_at) if out_at else datetime.utcnow()
    if not start or not end:
        return 0.0
    secs = (end - start).total_seconds()
    if secs <= 0:
        return 0.0
    # Sub-minute punches still count (min ~1 second → 0.02 min)
    return max(0.02, round(secs / 60.0, 2))


def _tc_open_for(email: str, rows: Optional[list] = None):
    email = (email or '').strip().lower()
    rows = rows if rows is not None else _tc_load()
    for p in reversed(rows):
        if (p.get('email') or '').lower() == email and not p.get('outAt'):
            return p
    return None


def _tc_status_payload(rec: dict, email: str) -> dict:
    rows = _tc_load()
    open_punch = _tc_open_for(email, rows)
    today = _tc_today_et()
    today_rows = []
    today_minutes = 0.0
    for p in rows:
        if (p.get('email') or '').lower() != email:
            continue
        in_day = (p.get('inAt') or '')[:10]
        # Compare UTC date slice — also match ET day via inAtEt if present
        day_key = (p.get('inAtEt') or in_day)[:10]
        if day_key != today and in_day != today:
            continue
        mins = p.get('minutes')
        if mins is None:
            mins = _tc_minutes(p.get('inAt'), p.get('outAt'))
        today_minutes += float(mins or 0)
        today_rows.append({
            **p,
            'elapsedMinutes': mins if p.get('outAt') else _tc_minutes(p.get('inAt')),
        })
    open_elapsed = _tc_minutes(open_punch['inAt']) if open_punch else 0.0
    last_active = (open_punch or {}).get('lastActiveAt')
    work_events = int((open_punch or {}).get('workEvents') or 0)
    return {
        'ok': True,
        'module': 'OPS timeclock',
        'mode': 'session',  # OPS login = on the clock
        'email': email,
        'name': rec.get('name') or '',
        'personnelNumberCore': rec.get('personnelNumberCore') or '',
        'personnelNumber': rec.get('personnelNumber') or '',
        'clockedIn': bool(open_punch),
        'onShift': bool(open_punch),
        'openPunch': open_punch,
        'openElapsedMinutes': open_elapsed,
        'lastActiveAt': last_active,
        'workEvents': work_events,
        'today': today,
        'todayMinutes': round(today_minutes, 2),
        'todayHours': round(today_minutes / 60.0, 2),
        'todayPunches': today_rows,
        'timezone': 'America/Detroit',
    }


def _tc_ensure_in(rec: dict, email: str, source: str = 'ops-login', note: str = ''):
    """OPS sign-in = clock in. Idempotent if already on shift."""
    rows = _tc_load()
    open_punch = _tc_open_for(email, rows)
    now = _tc_now()
    if open_punch:
        for i, p in enumerate(rows):
            if p.get('id') == open_punch.get('id'):
                p['lastActiveAt'] = now
                p['sessionSource'] = p.get('sessionSource') or source
                rows[i] = p
                open_punch = p
                break
        _tc_save(rows)
        return open_punch, False  # already in
    import uuid
    punch = {
        'id': f'TC-{uuid.uuid4().hex[:10].upper()}',
        'email': email,
        'name': rec.get('name') or '',
        'personnelNumberCore': rec.get('personnelNumberCore') or '',
        'personnelNumber': rec.get('personnelNumber') or '',
        'inAt': now,
        'inAtEt': _tc_today_et(),
        'outAt': None,
        'minutes': None,
        'lastActiveAt': now,
        'workEvents': 0,
        'note': (note or '')[:200],
        'source': source,
        'sessionSource': source,
    }
    rows.append(punch)
    _tc_save(rows)
    return punch, True


def _tc_heartbeat(email: str, work_event: bool = False, event_label: str = ''):
    """Mark activity while logged into OPS (work being done)."""
    rows = _tc_load()
    open_punch = _tc_open_for(email, rows)
    if not open_punch:
        return None
    now = _tc_now()
    for i, p in enumerate(rows):
        if p.get('id') == open_punch.get('id'):
            p['lastActiveAt'] = now
            if work_event:
                p['workEvents'] = int(p.get('workEvents') or 0) + 1
                if event_label:
                    hist = list(p.get('workEventLog') or [])
                    hist.append({'at': now, 'event': str(event_label)[:40]})
                    p['workEventLog'] = hist[-50:]
            rows[i] = p
            open_punch = p
            break
    _tc_save(rows)
    return open_punch


@ops_portal.route('/ops/timeclock/status', methods=['GET', 'POST'])
def ops_timeclock_status():
    data = request.get_json(silent=True) or {}
    email = (request.args.get('email') or data.get('email') or '').strip().lower()
    rec, ok, reason = _person_from_email(email)
    if not rec:
        return jsonify({'ok': False, 'error': reason or 'Unknown email'}), 404
    payload = _tc_status_payload(rec, email)
    payload['canWork'] = bool(ok)
    payload['canWorkReason'] = reason
    return jsonify(payload)


@ops_portal.route('/ops/timeclock/clock-in', methods=['POST'])
@ops_portal.route('/ops/timeclock/session-start', methods=['POST'])
def ops_timeclock_clock_in():
    """OPS login / session start → on the clock (idempotent)."""
    data = request.get_json(silent=True) or {}
    email = (data.get('email') or '').strip().lower()
    rec, ok, reason = _person_from_email(email)
    if not rec:
        return jsonify({'ok': False, 'error': reason or 'Unknown email'}), 404
    if not ok:
        return jsonify({
            'ok': False,
            'error': 'Cannot start shift — GATEWAY can-work blocked',
            'canWorkReason': reason,
        }), 403
    source = (data.get('source') or 'ops-login').strip()[:40] or 'ops-login'
    punch, created = _tc_ensure_in(rec, email, source=source, note=data.get('note') or '')
    return jsonify({
        'ok': True,
        'created': created,
        'punch': punch,
        'status': _tc_status_payload(rec, email),
    }), (201 if created else 200)


@ops_portal.route('/ops/timeclock/heartbeat', methods=['POST'])
def ops_timeclock_heartbeat():
    """Activity while signed into OPS — proves work is happening on shift."""
    data = request.get_json(silent=True) or {}
    email = (data.get('email') or '').strip().lower()
    rec, ok, reason = _person_from_email(email)
    if not rec:
        return jsonify({'ok': False, 'error': reason or 'Unknown email'}), 404
    if not ok:
        return jsonify({'ok': False, 'error': 'can-work blocked', 'canWorkReason': reason}), 403
    work_event = bool(data.get('workEvent') or data.get('work'))
    event_label = (data.get('event') or data.get('label') or '').strip()
    # Auto-start shift if they somehow have a session without a punch
    open_punch = _tc_open_for(email)
    if not open_punch:
        punch, _ = _tc_ensure_in(rec, email, source='ops-heartbeat')
        open_punch = punch
    else:
        open_punch = _tc_heartbeat(email, work_event=work_event, event_label=event_label)
    return jsonify({
        'ok': True,
        'punch': open_punch,
        'status': _tc_status_payload(rec, email),
    })


@ops_portal.route('/ops/timeclock/clock-out', methods=['POST'])
@ops_portal.route('/ops/timeclock/session-end', methods=['POST'])
def ops_timeclock_clock_out():
    """OPS sign-out / idle logout → end shift. Soft-OK if already out."""
    data = request.get_json(silent=True) or {}
    email = (data.get('email') or '').strip().lower()
    rec, ok, reason = _person_from_email(email)
    if not rec:
        return jsonify({'ok': False, 'error': reason or 'Unknown email'}), 404
    rows = _tc_load()
    open_punch = _tc_open_for(email, rows)
    if not open_punch:
        return jsonify({
            'ok': True,
            'alreadyOut': True,
            'status': _tc_status_payload(rec, email),
        })
    now = _tc_now()
    mins = _tc_minutes(open_punch.get('inAt'), now)
    reason_out = (data.get('reason') or data.get('source') or 'ops-logout').strip()[:40]
    for i, p in enumerate(rows):
        if p.get('id') == open_punch.get('id'):
            p['outAt'] = now
            p['minutes'] = mins
            p['outReason'] = reason_out
            p['lastActiveAt'] = p.get('lastActiveAt') or now
            if data.get('note'):
                p['note'] = ((p.get('note') or '') + ' ' + str(data.get('note')))[:200].strip()
            rows[i] = p
            open_punch = p
            break
    _tc_save(rows)
    return jsonify({'ok': True, 'punch': open_punch, 'status': _tc_status_payload(rec, email)})


@ops_portal.route('/ops/timeclock/send-to-vertex', methods=['POST'])
def ops_timeclock_send_to_vertex():
    """Roll closed punches in a pay period into a VERTEX HR timesheet draft."""
    data = request.get_json(silent=True) or {}
    email = (data.get('email') or '').strip().lower()
    rec, ok, reason = _person_from_email(email)
    if not rec:
        return jsonify({'ok': False, 'error': reason or 'Unknown email'}), 404
    core = (rec.get('personnelNumberCore') or '').strip()
    if not core:
        return jsonify({'ok': False, 'error': 'No personnelNumberCore on GATEWAY record'}), 400

    try:
        from vertex_hr_api import _biweekly_period_for, _find_employee, create_timesheet_from_ops
    except ImportError:
        create_timesheet_from_ops = None
        _biweekly_period_for = None
        _find_employee = None

    period_start = (data.get('periodStart') or '')[:10]
    period_end = (data.get('periodEnd') or '')[:10]
    if (not period_start or not period_end) and _biweekly_period_for:
        period = _biweekly_period_for()
        period_start = period.get('periodStart') or period_start
        period_end = period.get('periodEnd') or period_end
    if not period_start or not period_end:
        return jsonify({'ok': False, 'error': 'periodStart and periodEnd required'}), 400

    rows = _tc_load()
    total_mins = 0.0
    punch_ids = []
    for p in rows:
        if (p.get('email') or '').lower() != email:
            continue
        if not p.get('outAt'):
            continue
        day = (p.get('inAtEt') or p.get('inAt') or '')[:10]
        if day < period_start or day > period_end:
            continue
        total_mins += float(p.get('minutes') or _tc_minutes(p.get('inAt'), p.get('outAt')))
        punch_ids.append(p.get('id'))

    hours = round(total_mins / 60.0, 2)
    if hours <= 0:
        return jsonify({
            'ok': False,
            'error': 'No closed punches in this period',
            'periodStart': period_start,
            'periodEnd': period_end,
        }), 400

    # Prefer dedicated helper; fall back to inline create
    if create_timesheet_from_ops:
        result = create_timesheet_from_ops(
            personnel_number_core=core,
            period_start=period_start,
            period_end=period_end,
            regular_hours=hours,
            actor_email=email,
            notes=f'OPS timeclock ({len(punch_ids)} punches)',
            punch_ids=punch_ids,
        )
        return jsonify(result), (201 if result.get('ok') else 400)

    # Inline fallback via VERTEX API module internals
    try:
        from vertex_hr_api import _load as _vload, _save as _vsave, TIMESHEETS_FILE, _split_ot
        import uuid
        emp = _find_employee(core) if _find_employee else None
        if not emp:
            return jsonify({
                'ok': False,
                'error': 'Employee not in VERTEX HR — Sync GATEWAY in VERTEX first',
            }), 404
        regular, ot = _split_ot(hours, 0)
        sheet = {
            'id': f'TS-{uuid.uuid4().hex[:10].upper()}',
            'personnelNumberCore': core,
            'personnelNumber': emp.get('personnelNumber'),
            'name': emp.get('name'),
            'email': emp.get('email') or email,
            'workerType': emp.get('workerType'),
            'periodStart': period_start,
            'periodEnd': period_end,
            'regularHours': regular,
            'otHours': ot,
            'ptoHours': 0,
            'unpaidHours': 0,
            'notes': f'OPS timeclock ({len(punch_ids)} punches)',
            'status': 'Draft',
            'source': 'ops-timeclock',
            'opsPunchIds': punch_ids,
            'createdAt': _tc_now(),
            'createdBy': email,
            'submittedAt': None,
            'approvedAt': None,
            'approvedBy': None,
        }
        sheets = _vload(TIMESHEETS_FILE)
        sheets.append(sheet)
        _vsave(TIMESHEETS_FILE, sheets)
        return jsonify({
            'ok': True,
            'timesheet': sheet,
            'hours': hours,
            'punchCount': len(punch_ids),
            'periodStart': period_start,
            'periodEnd': period_end,
        }), 201
    except Exception as e:
        return jsonify({'ok': False, 'error': f'Could not create VERTEX timesheet: {e}'}), 500


def _is_supervisor_role(ops_role: str) -> bool:
    """Floor-control assign rights (supervisor, manager, admin/owner). Visibility is separate."""
    return ops_role in ('supervisor', 'manager', 'admin')


def _is_manager_role(ops_role: str) -> bool:
    """Management floor + oversight (manager, admin/owner)."""
    return ops_role in ('manager', 'admin')


def _floor_for_role(ops_role: str) -> str:
    if ops_role == 'admin':
        return 'owner'
    if ops_role == 'manager':
        return 'management'
    if ops_role == 'supervisor':
        return 'supervisor'
    return 'care'


def _capabilities_for_role(ops_role: str) -> dict:
    """Role-floor capability matrix. Supervisors keep Care desk (assign-to-self)."""
    is_sup = _is_supervisor_role(ops_role)
    is_mgr = _is_manager_role(ops_role)
    is_admin = ops_role == 'admin'
    is_cca = ops_role == 'cca'
    return {
        'careDesk': True,
        'requestWork': is_cca or is_admin,
        'assign': is_sup,
        'batchAssign': is_sup,
        'forceRelease': is_sup,
        'liveBoard': is_sup,
        'agentNetwork': is_sup,
        'dayCalendar': True,
        'requestInbox': is_sup,
        'agingBoard': is_sup,
        'agingEscalate': is_mgr,
        'workforceReadiness': is_mgr,
        'managementFloor': is_mgr,
        'claimsAuthorize': False,
        'breakGlass': is_mgr,
        'seeAllSectors': is_admin,
    }


def _request_entries(order: dict) -> list:
    raw = order.get('ops_assignment_requests')
    if isinstance(raw, list):
        return [r for r in raw if isinstance(r, dict) and r.get('email')]
    return []


def _assign_order_fields(order: dict, assignee_name: str, assignee_email: str, actor_name: str, actor_email: str):
    """Write assignment onto PRISM order (source of record). Supervisor path only."""
    order['ops_claimed_by'] = assignee_name
    order['ops_claimed_email'] = assignee_email
    order['ops_claimed_at'] = datetime.now().isoformat()
    order['ops_care_status'] = 'Working'
    if (order.get('status') or '').lower() in ('', 'new'):
        order['status'] = 'In Progress'
    # Clear pending requests once assigned
    order['ops_assignment_requests'] = []
    _append_activity(
        order, actor_name, actor_email, 'assign',
        f'👤 Assigned to {assignee_name} by supervisor',
    )
    order['updated_at'] = datetime.now().isoformat()
    order['ops_last_edit_by'] = actor_email


def _resolve_assignee(assignee_email: str, assignee_name: str = ''):
    from hr_onboarding_api import _find_by_email

    email = (assignee_email or '').strip().lower()
    name = (assignee_name or '').strip()
    if not email or '@' not in email:
        return None, None, 'assigneeEmail required'
    assignee_rec, _, _ = _find_by_email(email)
    if assignee_rec and assignee_rec.get('name'):
        name = assignee_rec.get('name')
    if not name:
        name = email.split('@')[0]
    return name, email, None


def _list_agent_network(viewer_codes: set, ops_role: str) -> list:
    """Active GATEWAY people for the agent network.

    Owner/admin: full network. Supervisors/managers: agents who share employed sectors.
    """
    from hr_onboarding_api import _load_all

    records, _ = _load_all()
    agents = []
    see_all = _sees_all_accounts(ops_role)
    for r in records:
        if (r.get('status') or 'Active') != 'Active':
            continue
        role = _role_from_level(r.get('level') or '', r.get('email') or '')
        codes = _account_filter_codes(r)
        if not see_all:
            if not viewer_codes:
                continue
            if not codes or not (codes & viewer_codes):
                continue
        ok, reason, relaxed = _effective_can_work(r)
        agents.append({
            'id': r.get('id'),
            'name': r.get('name') or '',
            'email': (r.get('email') or '').strip().lower(),
            'level': r.get('level') or '',
            'opsRole': role,
            'accounts': _accounts_list(r.get('account') or ''),
            'accountCodes': sorted(codes),
            'canWork': bool(ok),
            'canWorkReason': reason,
            'canWorkRelaxed': bool(relaxed),
            'division': r.get('division') or '',
        })
    agents.sort(key=lambda a: ((a.get('name') or '').lower(), a.get('email') or ''))
    return agents


def _combine_local_dt(date_s: str, time_s: str) -> Optional[datetime]:
    """Build a local datetime from PRISM pickup date + time fields."""
    d = (date_s or '').strip()[:10]
    t = (time_s or '').strip()
    if not d:
        return None
    if not t:
        t = '09:00'
    # Accept HH:MM or HH:MM:SS
    if re.match(r'^\d{1,2}:\d{2}$', t):
        t = t + ':00'
    try:
        return datetime.fromisoformat(f'{d}T{t}')
    except ValueError:
        try:
            return datetime.strptime(f'{d} {t[:5]}', '%Y-%m-%d %H:%M')
        except ValueError:
            return None


def _order_to_calendar_events(order: dict) -> list:
    """
    PRISM is system of record. Calendar events are derived from the order.
    Never invent a second store for OPS — optional nexus_calendar sync is write-behind only.
    """
    events = []
    oid = order.get('id') or ''
    member = _member_name(order) or 'Member'
    payer = _order_payer(order) or ''
    details = order.get('details') or {}
    care = _care_status_from_order(order)

    pickup_dt = _combine_local_dt(
        details.get('pickup_date') or order.get('date') or '',
        details.get('pickup_time') or order.get('time') or '',
    )
    if pickup_dt and care != 'Done':
        events.append({
            'id': f'prism-pickup-{oid}',
            'source': 'prism',
            'kind': 'pickup',
            'emoji': '🚗',
            'title': f'Pickup — {member}',
            'startAt': pickup_dt.isoformat(),
            'endAt': (pickup_dt + timedelta(minutes=45)).isoformat(),
            'orderId': oid,
            'memberName': member,
            'payer': payer,
            'careStatus': care,
            'claimedBy': order.get('ops_claimed_by'),
            'claimedEmail': order.get('ops_claimed_email'),
            'note': (order.get('notes') or '')[:120],
            'priority': order.get('priority') or 'Standard',
        })

    cb_raw = order.get('ops_callback_at') or details.get('callback_at') or ''
    cb_dt = _parse_ts(cb_raw) if cb_raw else None
    if cb_dt and care != 'Done':
        events.append({
            'id': f'prism-callback-{oid}',
            'source': 'prism',
            'kind': 'callback',
            'emoji': '📞',
            'title': f'Callback — {member}',
            'startAt': cb_dt.isoformat(),
            'endAt': (cb_dt + timedelta(minutes=15)).isoformat(),
            'orderId': oid,
            'memberName': member,
            'payer': payer,
            'careStatus': care,
            'claimedBy': order.get('ops_claimed_by'),
            'claimedEmail': order.get('ops_claimed_email'),
            'note': (order.get('ops_callback_note') or '')[:160],
            'priority': order.get('priority') or 'Standard',
        })

    return events


def _sync_prism_event_to_nexus_calendar(event: dict, actor_email: str) -> Optional[str]:
    """Best-effort write-behind to shared NEXUS calendar. OPS never depends on this."""
    try:
        from nexus_calendar_service import create_calendar_event
        created = create_calendar_event(
            title=event.get('title') or 'PRISM event',
            start_iso=event.get('startAt') or '',
            end_iso=event.get('endAt'),
            description=event.get('note') or '',
            system='PRISM',
            event_type='ride' if event.get('kind') == 'pickup' else 'call',
            internal_id=event.get('orderId') or '',
            owner_id=actor_email or 'ops',
            assigned_to=event.get('claimedEmail') or actor_email or '',
            party_name=event.get('memberName') or '',
            visibility='assigned',
        )
        return created.get('id')
    except Exception:
        return None


def _is_today(raw: str) -> bool:
    ts = _parse_ts(raw or '')
    if not ts:
        return False
    return ts.date() == datetime.now().date()


def _order_completed_today(order: dict) -> bool:
    care = _care_status_from_order(order)
    if care != 'Done':
        status = (order.get('status') or '').lower()
        if status not in ('complete', 'completed', 'done'):
            return False
    return _is_today(order.get('updated_at') or order.get('ops_completed_at') or '')


@ops_portal.route('/ops/prism/day', methods=['GET'])
def ops_prism_day():
    """My Day / Team View — simple counts from the care-desk spec."""
    email = (request.args.get('email') or '').strip().lower()
    rec, can_work, reason = _person_from_email(email)
    if not rec:
        return jsonify({'ok': False, 'error': reason or 'Unauthorized'}), 404 if 'GATEWAY' in (reason or '') else 400
    if not can_work:
        return jsonify({'ok': False, 'error': 'Desks locked — GATEWAY can-work failed', 'canWorkReason': reason}), 403

    ops_role = _role_from_level(rec.get('level') or '', email)
    account_codes = _account_filter_codes(rec)
    team = _is_supervisor_role(ops_role)  # includes owner/admin

    new_today = 0
    overdue = 0
    completed_today = 0
    working = 0
    close_minutes = []
    by_agent = {}

    for order in _all_orders():
        if not _can_see_order(order, account_codes, ops_role):
            continue
        care = _care_status_from_order(order)
        claimed_email = (order.get('ops_claimed_email') or '').lower()
        claimed_by = order.get('ops_claimed_by') or claimed_email or 'Unassigned'

        if not team and claimed_email and claimed_email != email and care != 'Done':
            # CCA day view: only their work + unclaimed pool pressure still counted in overdue? Spec: personal
            if care != 'Done':
                continue

        if _is_today(order.get('created_at') or order.get('ops_created_at') or ''):
            new_today += 1

        sla = _sla_payload(order)
        if care != 'Done' and sla.get('slaTone') == 'overdue':
            if team or not claimed_email or claimed_email == email:
                overdue += 1

        if care in ('Working', 'Waiting on Auth'):
            if team or claimed_email == email:
                working += 1

        if _order_completed_today(order):
            if team or claimed_email == email or (order.get('ops_last_edit_by') or '').lower() == email:
                completed_today += 1
                created = order.get('created_at') or order.get('ops_created_at') or ''
                done_at = order.get('ops_completed_at') or order.get('updated_at') or ''
                try:
                    c_dt = datetime.fromisoformat(str(created).replace('Z', ''))
                    d_dt = datetime.fromisoformat(str(done_at).replace('Z', ''))
                    mins = int((d_dt - c_dt).total_seconds() / 60)
                    if mins >= 0:
                        close_minutes.append(mins)
                except (TypeError, ValueError):
                    pass

        if team and care != 'Done':
            key = claimed_email or '_pool'
            label = claimed_by if claimed_email else '🌊 Pool'
            row = by_agent.setdefault(key, {
                'email': claimed_email or '',
                'name': label,
                'open': 0,
                'overdue': 0,
                'working': 0,
            })
            row['open'] += 1
            if sla.get('slaTone') == 'overdue':
                row['overdue'] += 1
            if care in ('Working', 'Waiting on Auth'):
                row['working'] += 1

    agents = sorted(by_agent.values(), key=lambda a: (-a['overdue'], -a['open'], a['name'].lower()))
    avg_close = int(round(sum(close_minutes) / len(close_minutes))) if close_minutes else None
    return jsonify({
        'ok': True,
        'teamView': team,
        'opsRole': ops_role,
        'email': email,
        'counts': {
            'newToday': new_today,
            'overdue': overdue,
            'completedToday': completed_today,
            'working': working,
            'avgMinutesToClose': avg_close,
        },
        'byAgent': agents if team else [],
    })


@ops_portal.route('/ops/prism/calendar', methods=['GET'])
def ops_prism_calendar():
    """
    Care-desk calendar — always derived from PRISM orders (pickups + callbacks).
    Query: email, date=YYYY-MM-DD (default today), days=1..7
    """
    email = (request.args.get('email') or '').strip().lower()
    rec, can_work, reason = _person_from_email(email)
    if not rec:
        return jsonify({'ok': False, 'error': reason or 'Unauthorized'}), 404 if 'GATEWAY' in (reason or '') else 400
    if not can_work:
        return jsonify({'ok': False, 'error': 'Desks locked — GATEWAY can-work failed', 'canWorkReason': reason}), 403

    ops_role = _role_from_level(rec.get('level') or '', email)
    account_codes = _account_filter_codes(rec)
    team = _is_supervisor_role(ops_role)  # includes owner/admin

    date_s = (request.args.get('date') or '').strip()[:10]
    try:
        day0 = datetime.strptime(date_s, '%Y-%m-%d').date() if date_s else datetime.now().date()
    except ValueError:
        day0 = datetime.now().date()
    try:
        span = max(1, min(7, int(request.args.get('days') or '1')))
    except ValueError:
        span = 1
    day_end = day0 + timedelta(days=span)

    events = []
    for order in _all_orders():
        if not _can_see_order(order, account_codes, ops_role):
            continue
        claimed_email = (order.get('ops_claimed_email') or '').lower()
        if not team and claimed_email and claimed_email != email:
            # CCA: own cases + unclaimed pool times they may grab
            if claimed_email:
                continue
        for ev in _order_to_calendar_events(order):
            start = _parse_ts(ev.get('startAt') or '')
            if not start:
                continue
            if day0 <= start.date() < day_end:
                events.append(ev)

    events.sort(key=lambda e: e.get('startAt') or '')
    return jsonify({
        'ok': True,
        'sourceOfRecord': 'PRISM',
        'date': day0.isoformat(),
        'days': span,
        'teamView': team,
        'events': events,
        'count': len(events),
    })


@ops_portal.route('/ops/prism/items/<order_id>/callback', methods=['POST'])
def ops_prism_callback(order_id):
    """Schedule a callback on the PRISM order (system of record), then sync calendar best-effort."""
    data = request.get_json(silent=True) or {}
    email = (data.get('email') or request.args.get('email') or '').strip().lower()
    callback_at = (data.get('callbackAt') or data.get('callback_at') or '').strip()
    note = (data.get('note') or data.get('callbackNote') or '').strip()

    rec, can_work, reason = _person_from_email(email)
    if not rec:
        return jsonify({'ok': False, 'error': reason or 'Unauthorized'}), 404 if 'GATEWAY' in (reason or '') else 400
    if not can_work:
        return jsonify({'ok': False, 'error': 'Desks locked — GATEWAY can-work failed'}), 403

    ops_role = _role_from_level(rec.get('level') or '', email)
    account_codes = _account_filter_codes(rec)
    order, idx, orders, kind, _, save_fn = _find_order(order_id)
    if not order:
        return jsonify({'ok': False, 'error': 'Item not found'}), 404
    if not _can_see_order(order, account_codes, ops_role):
        return jsonify({'ok': False, 'error': 'Not in your account queue'}), 403

    cb_dt = _parse_ts(callback_at)
    if not cb_dt:
        return jsonify({'ok': False, 'error': 'callbackAt required (ISO datetime)'}), 400

    actor = rec.get('name') or email
    order['ops_callback_at'] = cb_dt.isoformat()
    if note:
        order['ops_callback_note'] = note
    order['updated_at'] = datetime.now().isoformat()
    order['ops_last_edit_by'] = email
    when_label = cb_dt.strftime('%b %d %I:%M %p').replace(' 0', ' ')
    _append_activity(
        order, actor, email, 'callback',
        f'📞 Callback scheduled for {when_label}' + (f' — {note}' if note else ''),
    )
    orders[idx] = order
    _persist_order(None, orders, kind, save_fn)

    # Build PRISM-derived event + optional write-behind to nexus calendar
    cal_events = _order_to_calendar_events(order)
    callback_ev = next((e for e in cal_events if e.get('kind') == 'callback'), None)
    nexus_id = None
    if callback_ev:
        nexus_id = _sync_prism_event_to_nexus_calendar(callback_ev, email)

    return jsonify({
        'ok': True,
        'item': _queue_card(order, detail=True),
        'calendarEvent': callback_ev,
        'nexusCalendarId': nexus_id,
        'sourceOfRecord': 'PRISM',
    })


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

    ops_role = _role_from_level(rec.get('level') or '', email)
    account_codes = _account_filter_codes(rec)
    mine_flag = request.args.get('mine', '').lower() in ('1', 'true', 'yes')
    view = (request.args.get('view') or ('mine' if mine_flag else 'all')).strip().lower()
    if view not in ('mine', 'pool', 'all', 'live'):
        view = 'all'
    q = (request.args.get('q') or '').strip()
    # demo filter: all | hide | only  (default all while training; hide for production desk)
    demo_mode = (request.args.get('demo') or request.args.get('demoMode') or 'all').strip().lower()
    if demo_mode not in ('all', 'hide', 'only'):
        demo_mode = 'all'
    # live = everything open + completed/cancelled today (full PRISM picture)
    include_closed = view in ('all', 'live') or _is_supervisor_role(ops_role)

    items = []
    demo_count = 0
    real_count = 0
    for order in _all_orders():
        is_demo = bool(order.get('ops_demo'))
        if demo_mode == 'hide' and is_demo:
            continue
        if demo_mode == 'only' and not is_demo:
            continue
        care = _care_status_from_order(order)
        status = (order.get('status') or '').lower()
        closed = care == 'Done' or status in ('complete', 'completed', 'cancelled', 'canceled')
        if closed and view not in ('all', 'live'):
            continue
        if closed and view == 'live' and not (
            _is_today(order.get('updated_at') or '') or _order_completed_today(order)
        ):
            continue
        if not _can_see_order(order, account_codes, ops_role):
            continue
        if not _matches_search(order, q):
            continue
        claimed_email = (order.get('ops_claimed_email') or '').lower()
        if view == 'mine' and claimed_email != email:
            continue
        if view == 'pool' and claimed_email:
            continue
        # CCAs on "all": only mine + unassigned (never other agents' cases)
        if view == 'all' and claimed_email and claimed_email != email and ops_role == 'cca':
            continue
        card = _queue_card(order)
        items.append(card)
        if is_demo:
            demo_count += 1
        else:
            real_count += 1

    def sort_key(x):
        rem = x.get('slaMinutesRemaining')
        if rem is None:
            rem = 99999
        return (
            0 if x.get('slaTone') == 'overdue' else 1 if x.get('slaTone') == 'tight' else 2,
            rem,
            0 if x.get('priority') == 'STAT' else 1,
        )

    items.sort(key=sort_key)
    return jsonify({
        'ok': True,
        'items': items,
        'total': len(items),
        'view': view,
        'q': q,
        'demoMode': demo_mode,
        'counts': {'demo': demo_count, 'real': real_count, 'total': len(items)},
        'seeAll': _sees_all_accounts(ops_role),
        'accountCodes': sorted(account_codes),
        'opsRole': ops_role,
        'email': email,
        'includeClosed': include_closed,
    })


@ops_portal.route('/ops/prism/agents', methods=['GET'])
def ops_prism_agents():
    """Agent network — who supervisors can batch-assign work to (same employed sectors)."""
    email = (request.args.get('email') or '').strip().lower()
    rec, can_work, reason = _person_from_email(email)
    if not rec:
        return jsonify({'ok': False, 'error': reason or 'Unauthorized'}), 404 if 'GATEWAY' in (reason or '') else 400
    if not can_work:
        return jsonify({'ok': False, 'error': 'Desks locked — GATEWAY can-work failed'}), 403

    ops_role = _role_from_level(rec.get('level') or '', email)
    if not _is_supervisor_role(ops_role):
        return jsonify({'ok': False, 'error': 'Only supervisors can view the agent network'}), 403

    account_codes = _account_filter_codes(rec)
    agents = _list_agent_network(account_codes, ops_role)
    return jsonify({
        'ok': True,
        'agents': agents,
        'count': len(agents),
        'opsRole': ops_role,
        'seeAll': _sees_all_accounts(ops_role),
        'accountCodes': sorted(account_codes),
        'note': 'Network scoped to your employed accounts (owners see all)',
    })


def _auth_floor_user(require_supervisor: bool = False, require_manager: bool = False):
    """Shared gate for oversight endpoints. Returns (rec, email, ops_role, account_codes, error_response)."""
    email = (request.args.get('email') or '').strip().lower()
    rec, can_work, reason = _person_from_email(email)
    if not rec:
        return None, email, None, set(), (
            jsonify({'ok': False, 'error': reason or 'Unauthorized'}),
            404 if 'GATEWAY' in (reason or '') else 400,
        )
    if not can_work:
        return None, email, None, set(), (
            jsonify({'ok': False, 'error': 'Desks locked — GATEWAY can-work failed', 'canWorkReason': reason}),
            403,
        )
    ops_role = _role_from_level(rec.get('level') or '', email)
    if require_manager and not _is_manager_role(ops_role):
        return None, email, ops_role, set(), (
            jsonify({'ok': False, 'error': 'Management floor only', 'code': 'MANAGEMENT_FLOOR'}),
            403,
        )
    if require_supervisor and not _is_supervisor_role(ops_role):
        return None, email, ops_role, set(), (
            jsonify({'ok': False, 'error': 'Supervisor or management floor only', 'code': 'SUPERVISOR_FLOOR'}),
            403,
        )
    return rec, email, ops_role, _account_filter_codes(rec), None


@ops_portal.route('/ops/prism/requests', methods=['GET'])
def ops_prism_requests():
    """Pending assignment requests — supervisor + management floors."""
    rec, email, ops_role, account_codes, err = _auth_floor_user(require_supervisor=True)
    if err:
        return err

    pending = []
    for order in _all_orders():
        if not _can_see_order(order, account_codes, ops_role):
            continue
        if order.get('ops_claimed_email'):
            continue
        reqs = _request_entries(order)
        if not reqs:
            continue
        card = _queue_card(order, detail=False)
        pending.append({
            'id': card.get('id'),
            'memberName': card.get('memberName'),
            'payer': card.get('payer'),
            'lane': card.get('serviceLane') or card.get('lane'),
            'priority': card.get('priority'),
            'slaTone': card.get('slaTone'),
            'slaLabel': card.get('slaLabel'),
            'isDemo': card.get('isDemo'),
            'requestCount': len(reqs),
            'requests': [
                {
                    'email': (r.get('email') or '').strip().lower(),
                    'name': r.get('name') or r.get('email') or '',
                    'at': r.get('at') or r.get('requestedAt') or '',
                }
                for r in reqs
            ],
        })
    pending.sort(key=lambda r: (-r.get('requestCount', 0), (r.get('memberName') or '').lower()))
    return jsonify({
        'ok': True,
        'opsRole': ops_role,
        'floor': _floor_for_role(ops_role),
        'count': len(pending),
        'items': pending,
    })


def _overdue_minutes_past(card: dict) -> int:
    """Minutes past SLA due (0 if not overdue / unknown)."""
    rem = card.get('slaMinutesRemaining')
    if rem is None:
        return 0
    try:
        rem_i = int(rem)
    except (TypeError, ValueError):
        return 0
    return max(0, -rem_i)


def _overdue_severity(minutes_past: int, priority: str) -> dict:
    """How late — Critical / High / Moderate."""
    pri = (priority or 'Standard').strip().lower()
    if pri == 'stat' or minutes_past >= 240:
        return {
            'key': 'critical',
            'label': 'Critical',
            'emoji': '🟥',
            'hint': 'STAT or 4h+ past due',
        }
    if minutes_past >= 60:
        return {
            'key': 'high',
            'label': 'High',
            'emoji': '🟠',
            'hint': '1–4 hours past due',
        }
    return {
        'key': 'moderate',
        'label': 'Just breached',
        'emoji': '🟡',
        'hint': 'Under 1 hour past due',
    }


def _overdue_reason(care: str, claimed_by: str, priority: str) -> dict:
    """Why it's stuck — primary action category (one per item)."""
    pri = (priority or 'Standard').strip().lower()
    if pri == 'stat':
        return {
            'key': 'stat',
            'label': 'STAT overdue',
            'emoji': '⚡',
            'hint': 'Priority STAT — jump the line',
        }
    if not claimed_by:
        return {
            'key': 'unassigned',
            'label': 'Unassigned overdue',
            'emoji': '🌊',
            'hint': 'Nobody owns it — assign now',
        }
    if care == 'Waiting on Auth':
        return {
            'key': 'waitingAuth',
            'label': 'Waiting on Auth overdue',
            'emoji': '⏳',
            'hint': 'Blocked on auth / info',
        }
    return {
        'key': 'stalled',
        'label': 'With agent — stalled',
        'emoji': '👤',
        'hint': 'Assigned but past SLA',
    }


# Human sector labels for OPS desks (never show raw HR codes to workforce).
# Internal GATEWAY codes stay on accountCode for routing only.
#
# WHEN A NEW CONTRACT LANDS:
#   1. Add GATEWAY account code (NEXUS HR ACCOUNT CODES) + PAYER_TO_CODES map
#   2. Add a row here: 'BUYER-LANE' → emoji, label, hint, accountCode
#   3. Teach _overdue_sector() how to detect it (payer / code / lane)
# Naming: BUYER-LANE (HAP-NEMT, MOL-CTS). Add more as contracts are secured.
SECTOR_DISPLAY = {
    'HAP-NEMT': {
        'emoji': '💚',
        'label': 'HAP-NEMT',
        'hint': 'HAP CareSource — NEMT / care coordination',
        'accountCode': 'CSRC',
    },
    'MOL-NEMT': {
        'emoji': 'Ⓜ️',
        'label': 'MOL-NEMT',
        'hint': 'Molina — NMT / NEMT dispatch',
        'accountCode': 'MOLN',
    },
    'MOL-CTS': {
        'emoji': '🏠',
        'label': 'MOL-CTS',
        'hint': 'Molina — Community Transition Services (CTS)',
        'accountCode': 'CTS',
    },
    'MER-NEMT': {
        'emoji': '💙',
        'label': 'MER-NEMT',
        'hint': 'Meridian — NEMT',
        'accountCode': 'MER',
    },
    'HAVN': {
        'emoji': '🛟',
        'label': 'HAVN',
        'hint': 'HAVEN — disaster / continuity transport',
        'accountCode': 'HAVN',
    },
}


def _overdue_sector(card: dict) -> dict:
    """Human sector bucket: HAP-NEMT, MOL-NEMT, MOL-CTS, MER-NEMT, HAVN."""
    codes = [str(c).upper() for c in (card.get('accountCodes') or []) if c]
    code = (card.get('accountCode') or (codes[0] if codes else '') or '').strip().upper()
    lane = (card.get('serviceLane') or card.get('lane') or '').strip().lower()
    payer = (card.get('payer') or '').strip().lower()

    # Resolve product lane first (CTS is its own Molina sector)
    is_cts = (
        code == 'CTS'
        or 'CTS' in codes
        or lane in ('cts', 'community transition', 'community transition services')
        or 'cts' in payer
    )
    is_hap = code == 'CSRC' or 'CSRC' in codes or 'hap' in payer or 'caresource' in payer
    is_mol = code == 'MOLN' or 'MOLN' in codes or 'molina' in payer
    is_mer = code == 'MER' or 'MER' in codes or 'meridian' in payer
    is_havn = code == 'HAVN' or 'HAVN' in codes or 'haven' in payer

    if is_cts:
        key = 'MOL-CTS'
    elif is_hap:
        key = 'HAP-NEMT'
    elif is_mol:
        key = 'MOL-NEMT'
    elif is_mer:
        key = 'MER-NEMT'
    elif is_havn:
        key = 'HAVN'
    else:
        key = 'OTHER'

    meta = SECTOR_DISPLAY.get(key)
    if meta:
        return {
            'key': key,
            'label': meta['label'],
            'emoji': meta['emoji'],
            'hint': meta['hint'],
            'accountCode': meta['accountCode'],  # internal only
        }
    return {
        'key': 'OTHER',
        'label': 'OTHER',
        'emoji': '❓',
        'hint': 'Unmapped sector — check payer / account on referral',
        'accountCode': code or 'UNKNOWN',
    }


@ops_portal.route('/ops/prism/aging', methods=['GET'])
def ops_prism_aging():
    """Aging / SLA breach board — overdue categorized by severity + reason."""
    rec, email, ops_role, account_codes, err = _auth_floor_user(require_supervisor=True)
    if err:
        return err

    buckets = {
        'unassigned': [],
        'tight': [],
        'overdue': [],
        'waitingAuth': [],
    }
    # Overdue taxonomy (actionable)
    overdue_by_severity = {
        'critical': [],
        'high': [],
        'moderate': [],
    }
    overdue_by_reason = {
        'stat': [],
        'unassigned': [],
        'waitingAuth': [],
        'stalled': [],
    }
    overdue_by_sector = {}  # code -> {meta, items}

    for order in _all_orders():
        if not _can_see_order(order, account_codes, ops_role):
            continue
        care = _care_status_from_order(order)
        if care == 'Done':
            continue
        card = _queue_card(order, detail=False)
        row = {
            'id': card.get('id'),
            'memberName': card.get('memberName'),
            'payer': card.get('payer'),
            'lane': card.get('serviceLane') or card.get('lane'),
            'accountCode': card.get('accountCode'),
            'accountCodes': card.get('accountCodes') or [],
            'priority': card.get('priority'),
            'careStatus': care,
            'careLabel': card.get('careLabel'),
            'claimedBy': card.get('claimedBy'),
            'claimedEmail': card.get('claimedEmail'),
            'slaTone': card.get('slaTone'),
            'slaLabel': card.get('slaLabel'),
            'requestCount': card.get('requestCount') or 0,
            'isDemo': card.get('isDemo'),
            'slaAgeMinutes': card.get('slaAgeMinutes'),
            'slaMinutesRemaining': card.get('slaMinutesRemaining'),
        }
        if not card.get('claimedBy'):
            buckets['unassigned'].append(row)
        if care == 'Waiting on Auth':
            buckets['waitingAuth'].append(row)
        if card.get('slaTone') == 'overdue':
            past = _overdue_minutes_past(card)
            sev = _overdue_severity(past, card.get('priority') or 'Standard')
            reason = _overdue_reason(care, card.get('claimedBy') or '', card.get('priority') or 'Standard')
            sector = _overdue_sector(card)
            enriched = dict(row)
            enriched['minutesPastDue'] = past
            enriched['severity'] = sev
            enriched['reason'] = reason
            enriched['sector'] = sector
            enriched['accountCode'] = sector.get('accountCode') or row.get('accountCode')
            enriched['slaLabel'] = f"{sev['emoji']} {sev['label']} · {past}m late"
            buckets['overdue'].append(enriched)
            overdue_by_severity.setdefault(sev['key'], []).append(enriched)
            overdue_by_reason.setdefault(reason['key'], []).append(enriched)
            sk = sector['key']
            if sk not in overdue_by_sector:
                overdue_by_sector[sk] = {
                    'key': sk,
                    'label': sector['label'],
                    'emoji': sector['emoji'],
                    'hint': sector['hint'],
                    'accountCode': sk,
                    'items': [],
                }
            overdue_by_sector[sk]['items'].append(enriched)
        elif card.get('slaTone') == 'tight':
            buckets['tight'].append(row)

    def _sort_overdue(rows: list) -> list:
        return sorted(
            rows,
            key=lambda r: (
                -(r.get('minutesPastDue') or 0),
                0 if (r.get('priority') or '').lower() == 'stat' else 1,
                (r.get('memberName') or '').lower(),
            ),
        )

    buckets['overdue'] = _sort_overdue(buckets['overdue'])
    for key in overdue_by_severity:
        overdue_by_severity[key] = _sort_overdue(overdue_by_severity[key])
    for key in overdue_by_reason:
        overdue_by_reason[key] = _sort_overdue(overdue_by_reason[key])
    for sk, block in overdue_by_sector.items():
        block['items'] = _sort_overdue(block['items'])
        block['count'] = len(block['items'])

    # Prefer known human sector order; OTHER last
    sector_order = ['HAP-NEMT', 'MOL-NEMT', 'MOL-CTS', 'MER-NEMT', 'HAVN']
    def _sector_sort_key(item):
        k = item[0]
        if k == 'OTHER':
            return (2, k)
        if k in sector_order:
            return (0, sector_order.index(k))
        return (1, k)

    by_sector_out = {}
    for sk, block in sorted(overdue_by_sector.items(), key=_sector_sort_key):
        by_sector_out[sk] = block

    for key in ('unassigned', 'tight', 'waitingAuth'):
        buckets[key].sort(key=lambda r: (
            0 if r.get('slaTone') == 'overdue' else 1,
            (r.get('memberName') or '').lower(),
        ))

    return jsonify({
        'ok': True,
        'opsRole': ops_role,
        'floor': _floor_for_role(ops_role),
        'canEscalate': _is_manager_role(ops_role),
        'counts': {k: len(v) for k, v in buckets.items()},
        'buckets': buckets,
        'overdueCategories': {
            'bySeverity': {
                'critical': {
                    'key': 'critical',
                    'label': 'Critical',
                    'emoji': '🟥',
                    'hint': 'STAT or 4h+ past due',
                    'count': len(overdue_by_severity['critical']),
                    'items': overdue_by_severity['critical'],
                },
                'high': {
                    'key': 'high',
                    'label': 'High',
                    'emoji': '🟠',
                    'hint': '1–4 hours past due',
                    'count': len(overdue_by_severity['high']),
                    'items': overdue_by_severity['high'],
                },
                'moderate': {
                    'key': 'moderate',
                    'label': 'Just breached',
                    'emoji': '🟡',
                    'hint': 'Under 1 hour past due',
                    'count': len(overdue_by_severity['moderate']),
                    'items': overdue_by_severity['moderate'],
                },
            },
            'byReason': {
                'stat': {
                    'key': 'stat',
                    'label': 'STAT overdue',
                    'emoji': '⚡',
                    'hint': 'Priority STAT — jump the line',
                    'count': len(overdue_by_reason['stat']),
                    'items': overdue_by_reason['stat'],
                },
                'unassigned': {
                    'key': 'unassigned',
                    'label': 'Unassigned overdue',
                    'emoji': '🌊',
                    'hint': 'Nobody owns it — assign now',
                    'count': len(overdue_by_reason['unassigned']),
                    'items': overdue_by_reason['unassigned'],
                },
                'waitingAuth': {
                    'key': 'waitingAuth',
                    'label': 'Waiting on Auth overdue',
                    'emoji': '⏳',
                    'hint': 'Blocked on auth / info',
                    'count': len(overdue_by_reason['waitingAuth']),
                    'items': overdue_by_reason['waitingAuth'],
                },
                'stalled': {
                    'key': 'stalled',
                    'label': 'With agent — stalled',
                    'emoji': '👤',
                    'hint': 'Assigned but past SLA',
                    'count': len(overdue_by_reason['stalled']),
                    'items': overdue_by_reason['stalled'],
                },
            },
            'bySector': by_sector_out,
        },
    })


@ops_portal.route('/ops/prism/readiness', methods=['GET'])
def ops_prism_readiness():
    """Workforce readiness — who in my sectors is blocked on GATEWAY can-work. Management floor."""
    rec, email, ops_role, account_codes, err = _auth_floor_user(require_manager=True)
    if err:
        return err

    people = _list_agent_network(account_codes, ops_role)
    ready = []
    blocked = []
    relaxed = []
    for p in people:
        row = {
            'name': p.get('name'),
            'email': p.get('email'),
            'opsRole': p.get('opsRole'),
            'level': p.get('level'),
            'accountCodes': p.get('accountCodes') or [],
            'canWork': p.get('canWork'),
            'canWorkReason': p.get('canWorkReason'),
            'canWorkRelaxed': p.get('canWorkRelaxed'),
        }
        if p.get('canWorkRelaxed'):
            relaxed.append(row)
        elif p.get('canWork'):
            ready.append(row)
        else:
            blocked.append(row)

    return jsonify({
        'ok': True,
        'opsRole': ops_role,
        'floor': _floor_for_role(ops_role),
        'counts': {
            'ready': len(ready),
            'blocked': len(blocked),
            'relaxed': len(relaxed),
            'total': len(people),
        },
        'ready': ready,
        'blocked': blocked,
        'relaxed': relaxed,
        'note': 'Management floor — GATEWAY can-work status for employed sectors (owners see all)',
    })


@ops_portal.route('/ops/prism/live', methods=['GET'])
def ops_prism_live():
    """
    PRISM operations board for your employed sectors.
    Supervisors / managers / owners only. Owners see all accounts.
    """
    email = (request.args.get('email') or '').strip().lower()
    rec, can_work, reason = _person_from_email(email)
    if not rec:
        return jsonify({'ok': False, 'error': reason or 'Unauthorized'}), 404 if 'GATEWAY' in (reason or '') else 400
    if not can_work:
        return jsonify({'ok': False, 'error': 'Desks locked — GATEWAY can-work failed'}), 403

    ops_role = _role_from_level(rec.get('level') or '', email)
    if not _is_supervisor_role(ops_role):
        return jsonify({'ok': False, 'error': 'Only supervisors/managers/owners can open the live PRISM board'}), 403

    account_codes = _account_filter_codes(rec)
    by_care = {k: 0 for k in CARE_STATUSES}
    by_lane = {}
    by_agent = {}
    overdue = 0
    unassigned = 0
    recent = []
    open_items = []
    completed_today = 0

    for order in _all_orders():
        if not _can_see_order(order, account_codes, ops_role):
            continue
        care = _care_status_from_order(order)
        lane = _order_service_lane(order)
        by_care[care] = by_care.get(care, 0) + 1
        by_lane[lane] = by_lane.get(lane, 0) + 1
        if _order_completed_today(order):
            completed_today += 1
        sla = _sla_payload(order)
        claimed = order.get('ops_claimed_by') or ''
        claimed_email = (order.get('ops_claimed_email') or '').lower()
        if care != 'Done':
            if not claimed_email:
                unassigned += 1
            if sla.get('slaTone') == 'overdue':
                overdue += 1
            key = claimed_email or '_pool'
            label = claimed if claimed_email else '🌊 Unassigned'
            row = by_agent.setdefault(key, {
                'email': claimed_email, 'name': label, 'open': 0, 'overdue': 0, 'working': 0,
            })
            row['open'] += 1
            if sla.get('slaTone') == 'overdue':
                row['overdue'] += 1
            if care in ('Working', 'Waiting on Auth'):
                row['working'] += 1
            open_items.append(_queue_card(order))

        for entry in (_ensure_activity(order) or [])[-3:]:
            recent.append({
                'orderId': order.get('id'),
                'memberName': _member_name(order),
                'payer': _order_payer(order),
                'lane': lane,
                'ts': entry.get('ts'),
                'actor': entry.get('actor'),
                'text': entry.get('text'),
            })

    recent.sort(key=lambda r: r.get('ts') or '', reverse=True)
    open_items.sort(key=lambda x: (
        0 if x.get('slaTone') == 'overdue' else 1,
        x.get('slaMinutesRemaining') if x.get('slaMinutesRemaining') is not None else 99999,
    ))
    agents = sorted(by_agent.values(), key=lambda a: (-a['overdue'], -a['open'], a['name'].lower()))

    return jsonify({
        'ok': True,
        'sourceOfRecord': 'PRISM',
        'opsRole': ops_role,
        'seeAll': _sees_all_accounts(ops_role),
        'accountCodes': sorted(account_codes),
        'counts': {
            'open': len(open_items),
            'unassigned': unassigned,
            'overdue': overdue,
            'byCare': by_care,
            'byLane': by_lane,
            'completedToday': completed_today,
        },
        'byAgent': agents,
        'openItems': open_items[:100],
        'recentActivity': recent[:40],
        'agentsOnNetwork': len(_list_agent_network(account_codes, ops_role)),
    })


@ops_portal.route('/ops/prism/items/<order_id>/claim', methods=['POST'])
def ops_prism_claim(order_id):
    """DISABLED — agents cannot self-assign. Use /request; supervisors use /assign."""
    return jsonify({
        'ok': False,
        'error': 'Agents cannot assign themselves. Use Request — a supervisor or manager must assign.',
        'code': 'SUPERVISOR_ASSIGN_ONLY',
    }), 403


@ops_portal.route('/ops/prism/items/<order_id>/request', methods=['POST'])
def ops_prism_request(order_id):
    """Agent requests assignment. Does NOT assign — supervisor/manager decides."""
    data = request.get_json(silent=True) or {}
    email = (data.get('email') or request.args.get('email') or '').strip().lower()
    rec, can_work, reason = _person_from_email(email)
    if not rec:
        return jsonify({'ok': False, 'error': reason or 'Unauthorized'}), 404
    if not can_work:
        return jsonify({'ok': False, 'error': 'can-work blocked', 'canWorkReason': reason}), 403

    ops_role = _role_from_level(rec.get('level') or '', email)
    account_codes = _account_filter_codes(rec)
    order, idx, orders, kind, _, save_fn = _find_order(order_id)
    if not order:
        return jsonify({'ok': False, 'error': 'Item not found'}), 404
    if not _can_see_order(order, account_codes, ops_role):
        return jsonify({'ok': False, 'error': 'Not in your employed sectors'}), 403
    if order.get('ops_claimed_email'):
        return jsonify({'ok': False, 'error': 'Already assigned — cannot request'}), 409

    requests_list = _request_entries(order)
    if any((r.get('email') or '').lower() == email for r in requests_list):
        return jsonify({
            'ok': True,
            'alreadyRequested': True,
            'item': _queue_card(order, detail=True),
            'message': 'Request already on file — waiting for supervisor',
        })

    actor = rec.get('name') or email
    requests_list.append({
        'email': email,
        'name': actor,
        'at': datetime.now().isoformat(),
    })
    order['ops_assignment_requests'] = requests_list
    _append_activity(order, actor, email, 'request', f'🙋 {actor} requested assignment')
    order['updated_at'] = datetime.now().isoformat()
    orders[idx] = order
    _persist_order(None, orders, kind, save_fn)
    return jsonify({
        'ok': True,
        'alreadyRequested': False,
        'item': _queue_card(order, detail=True),
        'message': 'Request sent — supervisor or manager must assign',
    })


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

    ops_role = _role_from_level(rec.get('level') or '', email)
    if not _is_supervisor_role(ops_role):
        return jsonify({
            'ok': False,
            'error': 'Only supervisors can release work back to the unassigned queue',
            'code': 'SUPERVISOR_ASSIGN_ONLY',
        }), 403

    account_codes = _account_filter_codes(rec)
    order, idx, orders, kind, _, save_fn = _find_order(order_id)
    if not order:
        return jsonify({'ok': False, 'error': 'Item not found'}), 404
    if not _can_see_order(order, account_codes, ops_role):
        return jsonify({'ok': False, 'error': 'Not in your employed sectors'}), 403

    if not order.get('ops_claimed_email'):
        return jsonify({'ok': False, 'error': 'Already unassigned'}), 409

    care = _care_status_from_order(order)
    needs_force = care in ('Working', 'Waiting on Auth') or (order.get('status') or '') == 'In Progress'
    if needs_force and not force:
        return jsonify({
            'ok': False,
            'error': 'This referral is in progress — confirm force unassign',
            'code': 'FORCE_RELEASE_REQUIRED',
            'careStatus': care,
            'assignedTo': order.get('ops_claimed_by'),
            'hint': 'POST again with force=true to pull it back to the unassigned pool',
        }), 409

    prev = order.get('ops_claimed_by') or order.get('ops_claimed_email')
    order['ops_claimed_by'] = None
    order['ops_claimed_email'] = None
    order['ops_claimed_at'] = None
    order['ops_released_at'] = datetime.now().isoformat()
    order['ops_released_by'] = email
    order['ops_force_released'] = bool(force and needs_force)
    order['ops_care_status'] = 'New'
    if (order.get('status') or '') == 'In Progress':
        order['status'] = 'New'
    actor = rec.get('name') or email
    note = (
        f'⚠️ Force-unassigned from {prev} by supervisor (was {care})'
        if force and needs_force else
        f'↩️ Released back to unassigned queue (was {prev})'
    )
    _append_activity(order, actor, email, 'force_release' if (force and needs_force) else 'release', note)
    order['updated_at'] = datetime.now().isoformat()
    orders[idx] = order
    _persist_order(None, orders, kind, save_fn)

    return jsonify({
        'ok': True,
        'forced': bool(force and needs_force),
        'item': _queue_card(order, detail=True),
    })


@ops_portal.route('/ops/prism/assign-batch', methods=['POST'])
def ops_prism_assign_batch():
    """Supervisor batch-assign many orders/clients to one agent (within employed sectors)."""
    data = request.get_json(silent=True) or {}
    email = (data.get('email') or request.args.get('email') or '').strip().lower()
    assignee_email = (data.get('assigneeEmail') or data.get('assignee_email') or '').strip().lower()
    assignee_name = (data.get('assigneeName') or data.get('assignee_name') or '').strip()
    order_ids = data.get('orderIds') or data.get('order_ids') or data.get('ids') or []
    if isinstance(order_ids, str):
        order_ids = [x.strip() for x in order_ids.split(',') if x.strip()]

    rec, can_work, reason = _person_from_email(email)
    if not rec:
        return jsonify({'ok': False, 'error': reason or 'Unauthorized'}), 404
    if not can_work:
        return jsonify({'ok': False, 'error': 'can-work blocked', 'canWorkReason': reason}), 403

    ops_role = _role_from_level(rec.get('level') or '', email)
    if not _is_supervisor_role(ops_role):
        return jsonify({'ok': False, 'error': 'Only supervisors can assign clients to agents'}), 403

    name, a_email, err = _resolve_assignee(assignee_email, assignee_name)
    if err:
        return jsonify({'ok': False, 'error': err}), 400
    if not order_ids:
        return jsonify({'ok': False, 'error': 'orderIds required'}), 400

    account_codes = _account_filter_codes(rec)
    actor = rec.get('name') or email
    assigned = []
    errors = []

    for oid in order_ids:
        order, idx, orders, kind, _, save_fn = _find_order(str(oid))
        if not order:
            errors.append({'id': oid, 'error': 'not found'})
            continue
        if not _can_see_order(order, account_codes, ops_role):
            errors.append({'id': oid, 'error': 'outside your employed sectors'})
            continue
        _assign_order_fields(order, name, a_email, actor, email)
        orders[idx] = order
        _persist_order(None, orders, kind, save_fn)
        assigned.append(_queue_card(order))

    return jsonify({
        'ok': True,
        'assignedCount': len(assigned),
        'assigned': assigned,
        'errors': errors,
        'assigneeEmail': a_email,
        'assigneeName': name,
    })


@ops_portal.route('/ops/prism/items/<order_id>/assign', methods=['POST'])
def ops_prism_assign(order_id):
    """Supervisor/manager assign to a specific agent email (within employed sectors)."""
    data = request.get_json(silent=True) or {}
    email = (data.get('email') or request.args.get('email') or '').strip().lower()
    assignee_email = (data.get('assigneeEmail') or data.get('assignee_email') or '').strip().lower()
    assignee_name = (data.get('assigneeName') or data.get('assignee_name') or '').strip()

    rec, can_work, reason = _person_from_email(email)
    if not rec:
        return jsonify({'ok': False, 'error': reason or 'Unauthorized'}), 404
    if not can_work:
        return jsonify({'ok': False, 'error': 'can-work blocked', 'canWorkReason': reason}), 403

    ops_role = _role_from_level(rec.get('level') or '', email)
    if not _is_supervisor_role(ops_role):
        return jsonify({'ok': False, 'error': 'Only supervisors can assign clients to agents'}), 403

    name, a_email, err = _resolve_assignee(assignee_email, assignee_name)
    if err:
        return jsonify({'ok': False, 'error': err}), 400

    account_codes = _account_filter_codes(rec)
    order, idx, orders, kind, _, save_fn = _find_order(order_id)
    if not order:
        return jsonify({'ok': False, 'error': 'Item not found'}), 404
    if not _can_see_order(order, account_codes, ops_role):
        return jsonify({'ok': False, 'error': 'Not in your employed sectors'}), 403

    _assign_order_fields(order, name, a_email, rec.get('name') or email, email)
    orders[idx] = order
    _persist_order(None, orders, kind, save_fn)
    return jsonify({'ok': True, 'item': _queue_card(order, detail=True)})


@ops_portal.route('/ops/prism/items/<order_id>', methods=['GET', 'PATCH'])
def ops_prism_item(order_id):
    if request.method == 'GET':
        email = (request.args.get('email') or '').strip().lower()
        rec, can_work, reason = _person_from_email(email)
        if not rec:
            return jsonify({'ok': False, 'error': reason or 'Unauthorized'}), 404
        if not can_work:
            return jsonify({'ok': False, 'error': 'can-work blocked'}), 403
        ops_role = _role_from_level(rec.get('level') or '', email)
        account_codes = _account_filter_codes(rec)
        order, _, _, _, _, _ = _find_order(order_id)
        if not order:
            return jsonify({'ok': False, 'error': 'Item not found'}), 404
        if not _can_see_order(order, account_codes, ops_role):
            return jsonify({'ok': False, 'error': 'Not in your account queue'}), 403
        return jsonify({'ok': True, 'item': _queue_card(order, detail=True)})

    data = request.get_json(silent=True) or {}
    email = (data.get('email') or request.args.get('email') or '').strip().lower()
    rec, can_work, reason = _person_from_email(email)
    if not rec:
        return jsonify({'ok': False, 'error': reason or 'Unauthorized'}), 404
    if not can_work:
        return jsonify({'ok': False, 'error': 'can-work blocked'}), 403

    ops_role = _role_from_level(rec.get('level') or '', email)
    account_codes = _account_filter_codes(rec)
    order, idx, orders, kind, _, save_fn = _find_order(order_id)
    if not order:
        return jsonify({'ok': False, 'error': 'Item not found'}), 404
    if not _can_see_order(order, account_codes, ops_role):
        return jsonify({'ok': False, 'error': 'Not in your account queue'}), 403

    claimed = (order.get('ops_claimed_email') or '').lower()
    if claimed and claimed != email and ops_role == 'cca':
        return jsonify({
            'ok': False,
            'error': 'This order is assigned to another agent. Only they (or a supervisor) can edit it.',
        }), 403

    actor = rec.get('name') or email

    # Immutable activity note (preferred path for care desk)
    activity_note = (data.get('activityNote') or data.get('activity_note') or '').strip()
    if activity_note:
        _append_activity(order, actor, email, 'note', activity_note)
        # Keep a short rolling preview on notes for list cards
        order['notes'] = activity_note

    care_status = (data.get('careStatus') or data.get('care_status') or '').strip()
    if care_status:
        if care_status not in CARE_STATUSES:
            return jsonify({
                'ok': False,
                'error': f'careStatus must be one of: {", ".join(CARE_STATUSES)}',
            }), 400
        prev = _care_status_from_order(order)
        order['ops_care_status'] = care_status
        order['status'] = CARE_STATUSES[care_status]['prism']
        if care_status == 'Done':
            order['ops_completed_at'] = datetime.now().isoformat()
        if care_status != prev:
            meta = CARE_STATUSES[care_status]
            _append_activity(
                order, actor, email, 'status',
                f'{meta["emoji"]} Status → {meta["label"]}',
            )

    # Legacy free-text notes overwrite (still logged)
    if 'notes' in data and not activity_note:
        new_notes = str(data.get('notes') or '')
        if new_notes != (order.get('notes') or ''):
            order['notes'] = new_notes
            if new_notes.strip():
                _append_activity(order, actor, email, 'note', new_notes.strip())

    if 'status' in data and not care_status:
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
    return jsonify({'ok': True, 'item': _queue_card(order, detail=True)})
