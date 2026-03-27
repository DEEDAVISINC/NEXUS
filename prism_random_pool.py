#!/usr/bin/env python3
"""
PRISM RANDOM POOL ENGINE
=========================
DOT-compliant random selection system for drug & alcohol testing programs.

Handles:
- Pool creation & management (DOT + non-DOT)
- Employee roster management
- Consortium pool logic (multiple employers, one pool)
- Scientifically valid random draws with full audit trail
- Notification tracking (DER notification, employee notification)
- Completion tracking (tested, missed, refused, alternate)
- Annual compliance rate calculation
- DOT MIS report data generation
- Draw scheduling (monthly, quarterly, custom)

Reference: 49 CFR Part 40, 49 CFR Part 382.305
"""

import json
import os
import random
import hashlib
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from flask import Blueprint, request, jsonify

prism_random = Blueprint('prism_random', __name__)

DATA_DIR = os.path.join(os.path.dirname(__file__), 'uploads', 'prism', 'random_pools')

DOT_RANDOM_RATES = {
    'FMCSA': {'drug': 0.50, 'alcohol': 0.10},
    'FTA':   {'drug': 0.50, 'alcohol': 0.10},
    'FAA':   {'drug': 0.25, 'alcohol': 0.10},
    'FRA':   {'drug': 0.50, 'alcohol': 0.25},
    'PHMSA': {'drug': 0.50, 'alcohol': 0.10},
    'USCG':  {'drug': 0.50, 'alcohol': None},
}

DRAW_FREQUENCIES = {
    'monthly': 12,
    'quarterly': 4,
    'semi_annual': 2,
    'annual': 1,
}


def _ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


def _pool_path(pool_id: str) -> str:
    return os.path.join(DATA_DIR, f'{pool_id}.json')


def _draws_path(pool_id: str) -> str:
    return os.path.join(DATA_DIR, f'{pool_id}_draws.json')


def _load_pool(pool_id: str) -> Optional[dict]:
    path = _pool_path(pool_id)
    if os.path.exists(path):
        with open(path, 'r') as f:
            return json.load(f)
    return None


def _save_pool(pool: dict):
    _ensure_data_dir()
    with open(_pool_path(pool['id']), 'w') as f:
        json.dump(pool, f, indent=2)


def _load_draws(pool_id: str) -> list:
    path = _draws_path(pool_id)
    if os.path.exists(path):
        with open(path, 'r') as f:
            return json.load(f)
    return []


def _save_draws(pool_id: str, draws: list):
    _ensure_data_dir()
    with open(_draws_path(pool_id), 'w') as f:
        json.dump(draws, f, indent=2)


def _generate_pool_id() -> str:
    return f"POOL-{uuid.uuid4().hex[:8].upper()}"


def _generate_draw_id() -> str:
    return f"DRAW-{uuid.uuid4().hex[:8].upper()}"


# ═══════════════════════════════════════════════════════════════════
# POOL MANAGEMENT
# ═══════════════════════════════════════════════════════════════════

def create_pool(
    name: str,
    client_id: str,
    dot_authority: str = 'FMCSA',
    pool_type: str = 'DOT',
    frequency: str = 'quarterly',
    custom_drug_rate: float = None,
    custom_alcohol_rate: float = None,
    consortium: bool = False,
    employers: List[str] = None,
) -> dict:
    """
    Create a new random testing pool.

    Args:
        name: Pool name (e.g., "Wayne County DOT Random Pool")
        client_id: PRISM client ID
        dot_authority: FMCSA, FTA, FAA, FRA, PHMSA, USCG (for DOT pools)
        pool_type: DOT or NON_DOT
        frequency: monthly, quarterly, semi_annual, annual
        custom_drug_rate: Override the DOT minimum rate
        custom_alcohol_rate: Override the DOT minimum rate
        consortium: True if this is a consortium pool (multiple employers)
        employers: List of employer IDs in the consortium
    """
    if pool_type == 'DOT' and dot_authority not in DOT_RANDOM_RATES:
        return {'error': f'Unknown DOT authority: {dot_authority}'}

    if frequency not in DRAW_FREQUENCIES:
        return {'error': f'Invalid frequency: {frequency}. Use: {list(DRAW_FREQUENCIES.keys())}'}

    if pool_type == 'DOT':
        rates = DOT_RANDOM_RATES[dot_authority]
        drug_rate = custom_drug_rate if custom_drug_rate else rates['drug']
        alcohol_rate = custom_alcohol_rate if custom_alcohol_rate else rates['alcohol']
    else:
        drug_rate = custom_drug_rate or 0.50
        alcohol_rate = custom_alcohol_rate or 0.10

    pool = {
        'id': _generate_pool_id(),
        'name': name,
        'client_id': client_id,
        'pool_type': pool_type,
        'dot_authority': dot_authority if pool_type == 'DOT' else None,
        'consortium': consortium,
        'employers': employers or [client_id],
        'frequency': frequency,
        'draws_per_year': DRAW_FREQUENCIES[frequency],
        'annual_drug_rate': drug_rate,
        'annual_alcohol_rate': alcohol_rate,
        'per_draw_drug_rate': drug_rate / DRAW_FREQUENCIES[frequency],
        'per_draw_alcohol_rate': (alcohol_rate / DRAW_FREQUENCIES[frequency]) if alcohol_rate else None,
        'members': [],
        'status': 'ACTIVE',
        'program_year_start': datetime.now().strftime('%Y-01-01'),
        'created': datetime.now().isoformat(),
        'updated': datetime.now().isoformat(),
        'total_draws': 0,
        'current_year_stats': {
            'year': datetime.now().year,
            'drug_selections': 0,
            'drug_completions': 0,
            'alcohol_selections': 0,
            'alcohol_completions': 0,
            'refusals': 0,
            'no_shows': 0,
        },
    }

    _save_pool(pool)
    return pool


def add_member(
    pool_id: str,
    employee_id: str,
    name: str,
    employer_id: str = None,
    position: str = None,
    cdl_number: str = None,
    hire_date: str = None,
) -> dict:
    """Add an employee to a random pool."""
    pool = _load_pool(pool_id)
    if not pool:
        return {'error': f'Pool not found: {pool_id}'}

    for m in pool['members']:
        if m['employee_id'] == employee_id:
            return {'error': f'Employee {employee_id} already in pool'}

    member = {
        'employee_id': employee_id,
        'name': name,
        'employer_id': employer_id or pool['client_id'],
        'position': position,
        'cdl_number': cdl_number,
        'hire_date': hire_date,
        'status': 'ACTIVE',
        'added_date': datetime.now().isoformat(),
        'times_selected': 0,
        'times_tested': 0,
        'last_selected': None,
        'last_tested': None,
    }

    pool['members'].append(member)
    pool['updated'] = datetime.now().isoformat()
    _save_pool(pool)

    return {'message': f'Added {name} to pool', 'pool_size': len(pool['members'])}


def remove_member(pool_id: str, employee_id: str, reason: str = 'TERMINATED') -> dict:
    """Remove an employee from a random pool (soft delete — marks inactive)."""
    pool = _load_pool(pool_id)
    if not pool:
        return {'error': f'Pool not found: {pool_id}'}

    for m in pool['members']:
        if m['employee_id'] == employee_id:
            m['status'] = 'INACTIVE'
            m['removed_date'] = datetime.now().isoformat()
            m['removal_reason'] = reason
            pool['updated'] = datetime.now().isoformat()
            _save_pool(pool)
            return {'message': f'Removed {m["name"]} from pool', 'reason': reason}

    return {'error': f'Employee {employee_id} not found in pool'}


def bulk_import_members(pool_id: str, members: List[dict]) -> dict:
    """Import multiple employees into a pool at once."""
    pool = _load_pool(pool_id)
    if not pool:
        return {'error': f'Pool not found: {pool_id}'}

    added = 0
    skipped = 0
    existing_ids = {m['employee_id'] for m in pool['members']}

    for m in members:
        if m.get('employee_id') in existing_ids:
            skipped += 1
            continue

        member = {
            'employee_id': m.get('employee_id', f"EMP-{uuid.uuid4().hex[:6].upper()}"),
            'name': m.get('name', 'Unknown'),
            'employer_id': m.get('employer_id', pool['client_id']),
            'position': m.get('position'),
            'cdl_number': m.get('cdl_number'),
            'hire_date': m.get('hire_date'),
            'status': 'ACTIVE',
            'added_date': datetime.now().isoformat(),
            'times_selected': 0,
            'times_tested': 0,
            'last_selected': None,
            'last_tested': None,
        }
        pool['members'].append(member)
        existing_ids.add(member['employee_id'])
        added += 1

    pool['updated'] = datetime.now().isoformat()
    _save_pool(pool)

    return {
        'message': f'Imported {added} members, skipped {skipped} duplicates',
        'pool_size': len([m for m in pool['members'] if m['status'] == 'ACTIVE']),
    }


# ═══════════════════════════════════════════════════════════════════
# RANDOM DRAW ENGINE — Scientifically Valid, Auditable
# ═══════════════════════════════════════════════════════════════════

def perform_draw(
    pool_id: str,
    test_type: str = 'drug',
    draw_date: datetime = None,
    override_count: int = None,
    alternate_count: int = 2,
) -> dict:
    """
    Perform a DOT-compliant random draw.

    Requirements per 49 CFR Part 382.305:
    - Scientifically valid random number generator
    - Each employee has equal probability of selection
    - Selection is unannounced
    - Spread reasonably throughout the year

    Args:
        pool_id: Pool to draw from
        test_type: 'drug' or 'alcohol'
        draw_date: Date of draw (defaults to now)
        override_count: Force a specific number of selections (overrides rate calc)
        alternate_count: Number of alternates to select
    """
    pool = _load_pool(pool_id)
    if not pool:
        return {'error': f'Pool not found: {pool_id}'}

    if draw_date is None:
        draw_date = datetime.now()

    active_members = [m for m in pool['members'] if m['status'] == 'ACTIVE']
    pool_size = len(active_members)

    if pool_size == 0:
        return {'error': 'No active members in pool'}

    if test_type == 'alcohol' and pool.get('annual_alcohol_rate') is None:
        return {'error': f'Alcohol testing not applicable for {pool.get("dot_authority")}'}

    rate_key = f'per_draw_{test_type}_rate'
    per_draw_rate = pool.get(rate_key, 0)

    if override_count is not None:
        num_to_select = override_count
    else:
        num_to_select = max(1, round(pool_size * per_draw_rate))

    num_to_select = min(num_to_select, pool_size)
    alternate_count = min(alternate_count, pool_size - num_to_select)

    # Cryptographic seed for audit trail — date + pool ID + test type
    seed_string = f"{pool_id}_{test_type}_{draw_date.strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
    seed_hash = int(hashlib.sha256(seed_string.encode()).hexdigest(), 16) % (2**32)
    rng = random.Random(seed_hash)

    shuffled = list(active_members)
    rng.shuffle(shuffled)

    selected = shuffled[:num_to_select]
    alternates = shuffled[num_to_select:num_to_select + alternate_count]

    draw_id = _generate_draw_id()

    selections = []
    for emp in selected:
        selections.append({
            'employee_id': emp['employee_id'],
            'name': emp['name'],
            'employer_id': emp['employer_id'],
            'selection_type': 'PRIMARY',
            'status': 'SELECTED',
            'notified': False,
            'notified_date': None,
            'tested': False,
            'tested_date': None,
            'result': None,
            'notes': None,
        })

    alternate_records = []
    for emp in alternates:
        alternate_records.append({
            'employee_id': emp['employee_id'],
            'name': emp['name'],
            'employer_id': emp['employer_id'],
            'selection_type': 'ALTERNATE',
            'status': 'STANDBY',
            'replaces': None,
            'notified': False,
            'tested': False,
        })

    draw_record = {
        'draw_id': draw_id,
        'pool_id': pool_id,
        'pool_name': pool['name'],
        'draw_date': draw_date.isoformat(),
        'test_type': test_type,
        'dot_authority': pool.get('dot_authority'),
        'pool_size': pool_size,
        'annual_rate': pool.get(f'annual_{test_type}_rate'),
        'per_draw_rate': per_draw_rate,
        'num_selected': num_to_select,
        'num_alternates': len(alternate_records),
        'selections': selections,
        'alternates': alternate_records,
        'seed': seed_string,
        'seed_hash': seed_hash,
        'algorithm': 'SHA-256 seeded Fisher-Yates shuffle',
        'compliance_note': 'Each active member had equal probability of selection per 49 CFR Part 382.305',
        'status': 'PENDING_NOTIFICATION',
        'created': datetime.now().isoformat(),
    }

    draws = _load_draws(pool_id)
    draws.append(draw_record)
    _save_draws(pool_id, draws)

    for m in pool['members']:
        for s in selected:
            if m['employee_id'] == s['employee_id']:
                m['times_selected'] = m.get('times_selected', 0) + 1
                m['last_selected'] = draw_date.isoformat()

    stats_key = f'{test_type}_selections'
    pool['current_year_stats'][stats_key] = pool['current_year_stats'].get(stats_key, 0) + num_to_select
    pool['total_draws'] = pool.get('total_draws', 0) + 1
    pool['updated'] = datetime.now().isoformat()
    _save_pool(pool)

    return draw_record


def update_selection_status(
    pool_id: str,
    draw_id: str,
    employee_id: str,
    status: str,
    tested_date: str = None,
    result: str = None,
    notes: str = None,
) -> dict:
    """
    Update the status of a selected employee after a draw.

    Valid statuses: NOTIFIED, TESTED, MISSED, REFUSED, CANCELLED
    Valid results: NEGATIVE, POSITIVE, NEGATIVE_DILUTE, CANCELLED, REFUSAL
    """
    valid_statuses = ['SELECTED', 'NOTIFIED', 'TESTED', 'MISSED', 'REFUSED', 'CANCELLED']
    if status not in valid_statuses:
        return {'error': f'Invalid status. Use: {valid_statuses}'}

    draws = _load_draws(pool_id)
    pool = _load_pool(pool_id)
    if not pool:
        return {'error': f'Pool not found: {pool_id}'}

    for draw in draws:
        if draw['draw_id'] != draw_id:
            continue

        for sel in draw['selections']:
            if sel['employee_id'] != employee_id:
                continue

            sel['status'] = status

            if status == 'NOTIFIED':
                sel['notified'] = True
                sel['notified_date'] = datetime.now().isoformat()

            if status == 'TESTED':
                sel['tested'] = True
                sel['tested_date'] = tested_date or datetime.now().isoformat()
                sel['result'] = result
                test_type = draw['test_type']
                pool['current_year_stats'][f'{test_type}_completions'] = \
                    pool['current_year_stats'].get(f'{test_type}_completions', 0) + 1

                for m in pool['members']:
                    if m['employee_id'] == employee_id:
                        m['times_tested'] = m.get('times_tested', 0) + 1
                        m['last_tested'] = sel['tested_date']

            if status == 'REFUSED':
                sel['result'] = 'REFUSAL'
                pool['current_year_stats']['refusals'] = \
                    pool['current_year_stats'].get('refusals', 0) + 1

            if status == 'MISSED':
                pool['current_year_stats']['no_shows'] = \
                    pool['current_year_stats'].get('no_shows', 0) + 1

            if notes:
                sel['notes'] = notes

            _save_draws(pool_id, draws)
            pool['updated'] = datetime.now().isoformat()
            _save_pool(pool)

            return {'message': f'Updated {employee_id} to {status}', 'draw_id': draw_id}

    return {'error': f'Selection not found for {employee_id} in draw {draw_id}'}


def activate_alternate(
    pool_id: str,
    draw_id: str,
    alternate_employee_id: str,
    replaces_employee_id: str,
    reason: str = 'Primary unavailable',
) -> dict:
    """Promote an alternate to primary when a selected employee can't be tested."""
    draws = _load_draws(pool_id)

    for draw in draws:
        if draw['draw_id'] != draw_id:
            continue

        alt = None
        for a in draw['alternates']:
            if a['employee_id'] == alternate_employee_id:
                alt = a
                break

        if not alt:
            return {'error': f'Alternate {alternate_employee_id} not found in draw'}

        alt['selection_type'] = 'PRIMARY_REPLACEMENT'
        alt['status'] = 'SELECTED'
        alt['replaces'] = replaces_employee_id

        draw['selections'].append({
            'employee_id': alt['employee_id'],
            'name': alt['name'],
            'employer_id': alt['employer_id'],
            'selection_type': 'ALTERNATE_ACTIVATED',
            'status': 'SELECTED',
            'replaces': replaces_employee_id,
            'reason': reason,
            'notified': False,
            'notified_date': None,
            'tested': False,
            'tested_date': None,
            'result': None,
            'notes': f'Alternate for {replaces_employee_id}: {reason}',
        })

        _save_draws(pool_id, draws)
        return {'message': f'Activated alternate {alt["name"]} replacing {replaces_employee_id}'}

    return {'error': f'Draw {draw_id} not found'}


# ═══════════════════════════════════════════════════════════════════
# COMPLIANCE TRACKING
# ═══════════════════════════════════════════════════════════════════

def get_compliance_status(pool_id: str, year: int = None) -> dict:
    """
    Calculate whether the pool is on track to meet annual testing rates.

    Returns current completion rate vs required rate, with projected year-end status.
    """
    pool = _load_pool(pool_id)
    if not pool:
        return {'error': f'Pool not found: {pool_id}'}

    if year is None:
        year = datetime.now().year

    draws = _load_draws(pool_id)
    year_draws = [d for d in draws if d['draw_date'].startswith(str(year))]

    active_count = len([m for m in pool['members'] if m['status'] == 'ACTIVE'])
    if active_count == 0:
        return {'error': 'No active members in pool'}

    now = datetime.now()
    day_of_year = now.timetuple().tm_yday
    year_progress = day_of_year / 365.0

    drug_required = pool.get('annual_drug_rate', 0.50)
    alcohol_required = pool.get('annual_alcohol_rate', 0.10)

    drug_selections = sum(len(d['selections']) for d in year_draws if d['test_type'] == 'drug')
    drug_completions = sum(
        1 for d in year_draws if d['test_type'] == 'drug'
        for s in d['selections'] if s.get('tested')
    )
    alcohol_selections = sum(len(d['selections']) for d in year_draws if d['test_type'] == 'alcohol')
    alcohol_completions = sum(
        1 for d in year_draws if d['test_type'] == 'alcohol'
        for s in d['selections'] if s.get('tested')
    )

    drug_target = round(active_count * drug_required)
    drug_actual_rate = drug_completions / active_count if active_count > 0 else 0
    drug_on_track = drug_actual_rate >= (drug_required * year_progress * 0.85)

    alcohol_target = round(active_count * alcohol_required) if alcohol_required else 0
    alcohol_actual_rate = alcohol_completions / active_count if active_count > 0 else 0
    alcohol_on_track = alcohol_actual_rate >= (alcohol_required * year_progress * 0.85) if alcohol_required else True

    remaining_draws = pool['draws_per_year'] - len(year_draws)
    drug_remaining = max(0, drug_target - drug_completions)
    alcohol_remaining = max(0, alcohol_target - alcohol_completions)

    return {
        'pool_id': pool_id,
        'pool_name': pool['name'],
        'year': year,
        'active_members': active_count,
        'year_progress': f'{year_progress:.0%}',
        'draws_completed': len(year_draws),
        'draws_remaining': remaining_draws,
        'drug_testing': {
            'annual_rate_required': f'{drug_required:.0%}',
            'target_tests': drug_target,
            'selections_ytd': drug_selections,
            'completions_ytd': drug_completions,
            'actual_rate': f'{drug_actual_rate:.0%}',
            'remaining_needed': drug_remaining,
            'on_track': drug_on_track,
            'status': 'ON TRACK' if drug_on_track else 'BEHIND — ACTION NEEDED',
        },
        'alcohol_testing': {
            'annual_rate_required': f'{alcohol_required:.0%}' if alcohol_required else 'N/A',
            'target_tests': alcohol_target,
            'selections_ytd': alcohol_selections,
            'completions_ytd': alcohol_completions,
            'actual_rate': f'{alcohol_actual_rate:.0%}',
            'remaining_needed': alcohol_remaining,
            'on_track': alcohol_on_track,
            'status': 'ON TRACK' if alcohol_on_track else 'BEHIND — ACTION NEEDED',
        },
        'issues': {
            'refusals': pool['current_year_stats'].get('refusals', 0),
            'no_shows': pool['current_year_stats'].get('no_shows', 0),
        },
        'timestamp': datetime.now().isoformat(),
    }


# ═══════════════════════════════════════════════════════════════════
# MIS REPORT DATA — DOT Annual Reporting
# ═══════════════════════════════════════════════════════════════════

def generate_mis_report(pool_id: str, year: int = None) -> dict:
    """
    Generate data for the DOT MIS (Management Information System) annual report.

    Required by 49 CFR Part 40 Subpart Q / Part 382.403.
    Filed annually to the relevant DOT agency.
    """
    pool = _load_pool(pool_id)
    if not pool:
        return {'error': f'Pool not found: {pool_id}'}

    if year is None:
        year = datetime.now().year

    draws = _load_draws(pool_id)
    year_draws = [d for d in draws if d['draw_date'].startswith(str(year))]

    all_members_ever = pool['members']
    active_at_year_end = [m for m in all_members_ever if m['status'] == 'ACTIVE']

    drug_draws = [d for d in year_draws if d['test_type'] == 'drug']
    alcohol_draws = [d for d in year_draws if d['test_type'] == 'alcohol']

    def count_results(draw_list, result_value):
        return sum(
            1 for d in draw_list
            for s in d['selections']
            if s.get('result') == result_value
        )

    def count_status(draw_list, status_value):
        return sum(
            1 for d in draw_list
            for s in d['selections']
            if s.get('status') == status_value
        )

    drug_tested = count_status(drug_draws, 'TESTED')
    drug_positive = count_results(drug_draws, 'POSITIVE')
    drug_negative = count_results(drug_draws, 'NEGATIVE')
    drug_negative_dilute = count_results(drug_draws, 'NEGATIVE_DILUTE')
    drug_refused = count_status(drug_draws, 'REFUSED')
    drug_cancelled = count_results(drug_draws, 'CANCELLED')

    alcohol_tested = count_status(alcohol_draws, 'TESTED')
    alcohol_positive_low = 0  # 0.02-0.039 — would need BAC field
    alcohol_positive_high = count_results(alcohol_draws, 'POSITIVE')
    alcohol_negative = count_results(alcohol_draws, 'NEGATIVE')
    alcohol_refused = count_status(alcohol_draws, 'REFUSED')

    return {
        'report_type': 'DOT MIS Annual Report Data',
        'pool_id': pool_id,
        'pool_name': pool['name'],
        'dot_authority': pool.get('dot_authority'),
        'reporting_year': year,
        'employer_info': {
            'company': 'Dee Davis Inc. (C/TPA)',
            'address': '755 W. Big Beaver Rd., Suite 2020, Troy, MI 48084',
            'phone': '248.376.4550',
            'email': 'info@deedavis.biz',
        },
        'covered_employees': {
            'total_subject_to_testing': len(active_at_year_end),
            'total_in_random_pool': len(active_at_year_end),
        },
        'drug_testing': {
            'random': {
                'tested': drug_tested,
                'positive': drug_positive,
                'negative': drug_negative,
                'negative_dilute': drug_negative_dilute,
                'refusals': drug_refused,
                'cancelled': drug_cancelled,
            },
        },
        'alcohol_testing': {
            'random': {
                'tested': alcohol_tested,
                'positive_below_04': alcohol_positive_low,
                'positive_04_or_above': alcohol_positive_high,
                'negative': alcohol_negative,
                'refusals': alcohol_refused,
            },
        },
        'compliance_rate': {
            'drug': f'{(drug_tested / len(active_at_year_end) * 100):.1f}%' if active_at_year_end else '0%',
            'alcohol': f'{(alcohol_tested / len(active_at_year_end) * 100):.1f}%' if active_at_year_end else '0%',
        },
        'generated': datetime.now().isoformat(),
        'note': 'This data feeds the DOT MIS annual report form. Verify all numbers before submission.',
    }


# ═══════════════════════════════════════════════════════════════════
# DRAW SCHEDULING
# ═══════════════════════════════════════════════════════════════════

def get_next_draw_date(pool_id: str) -> dict:
    """Calculate when the next draw should occur based on frequency and last draw."""
    pool = _load_pool(pool_id)
    if not pool:
        return {'error': f'Pool not found: {pool_id}'}

    draws = _load_draws(pool_id)
    frequency = pool.get('frequency', 'quarterly')
    interval_days = 365 // DRAW_FREQUENCIES[frequency]

    if not draws:
        next_date = datetime.now()
        return {
            'pool_id': pool_id,
            'next_draw_date': next_date.strftime('%Y-%m-%d'),
            'message': 'No previous draws — first draw should happen now',
            'overdue': True,
        }

    last_draw_date = max(datetime.fromisoformat(d['draw_date']) for d in draws)
    next_date = last_draw_date + timedelta(days=interval_days)
    overdue = datetime.now() > next_date

    return {
        'pool_id': pool_id,
        'last_draw_date': last_draw_date.strftime('%Y-%m-%d'),
        'next_draw_date': next_date.strftime('%Y-%m-%d'),
        'frequency': frequency,
        'overdue': overdue,
        'days_until': (next_date - datetime.now()).days if not overdue else 0,
        'message': 'OVERDUE — draw needed immediately' if overdue else f'Next draw in {(next_date - datetime.now()).days} days',
    }


def get_all_pools() -> list:
    """List all random pools."""
    _ensure_data_dir()
    pools = []
    for f in os.listdir(DATA_DIR):
        if f.endswith('.json') and not f.endswith('_draws.json'):
            with open(os.path.join(DATA_DIR, f), 'r') as fh:
                pool = json.load(fh)
                pools.append({
                    'id': pool['id'],
                    'name': pool['name'],
                    'client_id': pool['client_id'],
                    'pool_type': pool['pool_type'],
                    'dot_authority': pool.get('dot_authority'),
                    'active_members': len([m for m in pool['members'] if m['status'] == 'ACTIVE']),
                    'frequency': pool['frequency'],
                    'total_draws': pool.get('total_draws', 0),
                    'status': pool['status'],
                })
    return pools


# ═══════════════════════════════════════════════════════════════════
# DER NOTIFICATION GENERATOR
# ═══════════════════════════════════════════════════════════════════

def generate_der_notification(pool_id: str, draw_id: str) -> dict:
    """
    Generate the Designated Employer Representative (DER) notification
    for a completed random draw. This is what gets sent to the employer.
    """
    pool = _load_pool(pool_id)
    if not pool:
        return {'error': f'Pool not found: {pool_id}'}

    draws = _load_draws(pool_id)
    draw = None
    for d in draws:
        if d['draw_id'] == draw_id:
            draw = d
            break

    if not draw:
        return {'error': f'Draw {draw_id} not found'}

    selected_names = [s['name'] for s in draw['selections'] if s['selection_type'] in ('PRIMARY', 'ALTERNATE_ACTIVATED')]
    alternate_names = [a['name'] for a in draw['alternates'] if a['status'] == 'STANDBY']

    return {
        'draw_id': draw_id,
        'pool_name': pool['name'],
        'test_type': draw['test_type'].upper(),
        'draw_date': draw['draw_date'],
        'notification': {
            'to': 'Designated Employer Representative (DER)',
            'from': 'Dee Davis Inc. — C/TPA',
            'subject': f'CONFIDENTIAL: Random {draw["test_type"].title()} Testing Selection — {draw["draw_date"][:10]}',
            'body': (
                f'Random {draw["test_type"]} testing selection has been completed for {pool["name"]}.\n\n'
                f'Pool size: {draw["pool_size"]} employees\n'
                f'Selected for testing: {len(selected_names)}\n\n'
                f'SELECTED EMPLOYEES:\n' +
                '\n'.join(f'  - {name}' for name in selected_names) +
                '\n\nALTERNATES (use if primary is unavailable):\n' +
                '\n'.join(f'  - {name}' for name in alternate_names) +
                '\n\nIMPORTANT:\n'
                '- Notify selected employees IMMEDIATELY\n'
                '- Testing must be UNANNOUNCED — do not give advance warning\n'
                '- Selected employees must report for testing on the same day notified\n'
                '- Failure to appear = REFUSAL = treated as positive result\n'
                '- Contact DDI at 248.376.4550 for collection scheduling\n'
            ),
        },
        'action_required': 'Notify selected employees and schedule collection with DDI',
    }


# ═══════════════════════════════════════════════════════════════════
# API ENDPOINTS
# ═══════════════════════════════════════════════════════════════════

@prism_random.route('/prism/random-pools', methods=['GET'])
def api_list_pools():
    """List all random testing pools."""
    return jsonify(get_all_pools())


@prism_random.route('/prism/random-pools', methods=['POST'])
def api_create_pool():
    """Create a new random testing pool."""
    data = request.json or {}
    result = create_pool(
        name=data.get('name', 'Unnamed Pool'),
        client_id=data.get('client_id', ''),
        dot_authority=data.get('dot_authority', 'FMCSA'),
        pool_type=data.get('pool_type', 'DOT'),
        frequency=data.get('frequency', 'quarterly'),
        custom_drug_rate=data.get('custom_drug_rate'),
        custom_alcohol_rate=data.get('custom_alcohol_rate'),
        consortium=data.get('consortium', False),
        employers=data.get('employers'),
    )
    return jsonify(result), 201 if 'id' in result else 400


@prism_random.route('/prism/random-pools/<pool_id>', methods=['GET'])
def api_get_pool(pool_id):
    """Get pool details including roster."""
    pool = _load_pool(pool_id)
    if not pool:
        return jsonify({'error': 'Pool not found'}), 404
    return jsonify(pool)


@prism_random.route('/prism/random-pools/<pool_id>/members', methods=['POST'])
def api_add_member(pool_id):
    """Add a member to the pool."""
    data = request.json or {}
    result = add_member(
        pool_id=pool_id,
        employee_id=data.get('employee_id', f"EMP-{uuid.uuid4().hex[:6].upper()}"),
        name=data.get('name', ''),
        employer_id=data.get('employer_id'),
        position=data.get('position'),
        cdl_number=data.get('cdl_number'),
        hire_date=data.get('hire_date'),
    )
    return jsonify(result)


@prism_random.route('/prism/random-pools/<pool_id>/members/bulk', methods=['POST'])
def api_bulk_import(pool_id):
    """Bulk import members into the pool."""
    data = request.json or {}
    members = data.get('members', [])
    result = bulk_import_members(pool_id, members)
    return jsonify(result)


@prism_random.route('/prism/random-pools/<pool_id>/members/<employee_id>', methods=['DELETE'])
def api_remove_member(pool_id, employee_id):
    """Remove a member from the pool."""
    data = request.json or {}
    result = remove_member(pool_id, employee_id, reason=data.get('reason', 'TERMINATED'))
    return jsonify(result)


@prism_random.route('/prism/random-pools/<pool_id>/draw', methods=['POST'])
def api_perform_draw(pool_id):
    """Perform a random draw."""
    data = request.json or {}
    result = perform_draw(
        pool_id=pool_id,
        test_type=data.get('test_type', 'drug'),
        override_count=data.get('override_count'),
        alternate_count=data.get('alternate_count', 2),
    )
    return jsonify(result)


@prism_random.route('/prism/random-pools/<pool_id>/draws', methods=['GET'])
def api_get_draws(pool_id):
    """Get all draws for a pool."""
    draws = _load_draws(pool_id)
    return jsonify(draws)


@prism_random.route('/prism/random-pools/<pool_id>/draws/<draw_id>/update', methods=['POST'])
def api_update_selection(pool_id, draw_id):
    """Update a selection status (notified, tested, missed, refused)."""
    data = request.json or {}
    result = update_selection_status(
        pool_id=pool_id,
        draw_id=draw_id,
        employee_id=data.get('employee_id', ''),
        status=data.get('status', ''),
        tested_date=data.get('tested_date'),
        result=data.get('result'),
        notes=data.get('notes'),
    )
    return jsonify(result)


@prism_random.route('/prism/random-pools/<pool_id>/draws/<draw_id>/activate-alternate', methods=['POST'])
def api_activate_alternate(pool_id, draw_id):
    """Activate an alternate to replace a primary selection."""
    data = request.json or {}
    result = activate_alternate(
        pool_id=pool_id,
        draw_id=draw_id,
        alternate_employee_id=data.get('alternate_employee_id', ''),
        replaces_employee_id=data.get('replaces_employee_id', ''),
        reason=data.get('reason', 'Primary unavailable'),
    )
    return jsonify(result)


@prism_random.route('/prism/random-pools/<pool_id>/compliance', methods=['GET'])
def api_compliance_status(pool_id):
    """Get compliance status — are we hitting annual rates?"""
    year = request.args.get('year', type=int)
    result = get_compliance_status(pool_id, year)
    return jsonify(result)


@prism_random.route('/prism/random-pools/<pool_id>/mis-report', methods=['GET'])
def api_mis_report(pool_id):
    """Generate MIS report data for DOT annual filing."""
    year = request.args.get('year', type=int)
    result = generate_mis_report(pool_id, year)
    return jsonify(result)


@prism_random.route('/prism/random-pools/<pool_id>/next-draw', methods=['GET'])
def api_next_draw(pool_id):
    """Check when the next draw should occur."""
    result = get_next_draw_date(pool_id)
    return jsonify(result)


@prism_random.route('/prism/random-pools/<pool_id>/draws/<draw_id>/notification', methods=['GET'])
def api_der_notification(pool_id, draw_id):
    """Generate DER notification for a completed draw."""
    result = generate_der_notification(pool_id, draw_id)
    return jsonify(result)
