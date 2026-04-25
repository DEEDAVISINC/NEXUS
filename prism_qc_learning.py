#!/usr/bin/env python3
"""
PRISM QC Learning Module
=========================
Tier 3: Pattern learning and anomaly detection for automated QC.

Capabilities:
1. Risk scoring — predict scanback quality from agent / service / client features;
   route high-risk to priority human review, low-risk to auto-approve + audit sample.
2. Agent quality profiling — track error rates, types, and correction turnaround;
   auto-trigger training requirements or suspension when patterns exceed thresholds.
3. Cross-form consistency (future) — compare extracted fields across documents.
4. Duplicate / fraud detection (future) — flag identical uploads or impossible timelines.

Data sources:
  - uploads/qc_reports/     (historical QC review outcomes)
  - uploads/prism/orders.json  (order data with auto_qc, scanback, qc_checklist)
  - uploads/prism/doc_ai_results/  (document AI pipeline outputs)

The risk model uses a lightweight gradient-based approach that can run without
heavy ML dependencies. For production at scale, swap in scikit-learn / XGBoost.

Reference: prism_ai_qc_methods plan — Tier 3
"""

import os
import json
import math
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import defaultdict
from flask import Blueprint, request, jsonify

prism_qc_learning = Blueprint('prism_qc_learning', __name__)

DATA_DIR = os.path.join(os.path.dirname(__file__), 'uploads', 'prism')
ORDERS_FILE = os.path.join(DATA_DIR, 'orders.json')
QC_REPORTS_DIR = os.path.join(os.path.dirname(__file__), 'uploads', 'qc_reports')
AGENT_PROFILES_FILE = os.path.join(DATA_DIR, 'agent_quality_profiles.json')
RISK_MODEL_FILE = os.path.join(DATA_DIR, 'risk_model_weights.json')

os.makedirs(QC_REPORTS_DIR, exist_ok=True)


def _load_json(filepath, default=None):
    if default is None:
        default = []
    try:
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                return json.load(f)
    except (json.JSONDecodeError, IOError):
        pass
    return default


def _save_json(filepath, data):
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2, default=str)


# ═══════════════════════════════════════════════════════════════════
# 1. RISK SCORING MODEL
# ═══════════════════════════════════════════════════════════════════

DEFAULT_WEIGHTS = {
    'agent_error_rate':       0.35,
    'service_type_risk':      0.20,
    'page_count_deficit':     0.15,
    'temporal_violations':    0.10,
    'auto_qc_fatal_count':   0.10,
    'attempt_number':         0.05,
    'time_of_day_risk':       0.05,
}

SERVICE_TYPE_BASE_RISK = {
    'dot':              0.6,
    'non-dot':          0.4,
    'dna':              0.5,
    'fingerprint':      0.3,
    'background':       0.3,
    'notary':           0.35,
    'ron':              0.4,
    'phlebotomy':       0.5,
    'nemt':             0.25,
    'medical_courier':  0.4,
    'courier':          0.15,
    'apostille':        0.3,
    'process':          0.35,
}

AUTO_APPROVE_THRESHOLD = 0.25
PRIORITY_REVIEW_THRESHOLD = 0.60


def load_risk_weights() -> dict:
    """Load trained risk model weights, falling back to defaults."""
    stored = _load_json(RISK_MODEL_FILE, {})
    if stored and 'weights' in stored:
        return stored['weights']
    return DEFAULT_WEIGHTS.copy()


def compute_risk_score(order: dict, agent_profile: dict = None) -> dict:
    """Compute a 0-1 risk score for an incoming scanback.

    Features:
    - agent_error_rate: from agent quality profile (0-1)
    - service_type_risk: inherent complexity of the service type (0-1)
    - page_count_deficit: (expected - actual) / expected, clamped 0-1
    - temporal_violations: count of temporal issues from auto_qc
    - auto_qc_fatal_count: number of fatal flags from auto QC engine
    - attempt_number: which scanback attempt (higher = more risk)
    - time_of_day_risk: late-night submissions are higher risk
    """
    weights = load_risk_weights()
    features = {}

    # Agent error rate
    if agent_profile:
        features['agent_error_rate'] = min(agent_profile.get('error_rate', 0.0), 1.0)
    else:
        features['agent_error_rate'] = 0.3  # neutral prior

    # Service type risk
    svc = order.get('type', '')
    features['service_type_risk'] = SERVICE_TYPE_BASE_RISK.get(svc, 0.3)

    # Page count deficit
    auto_qc = order.get('auto_qc', {})
    sb = order.get('scanback', {})
    uploads = sb.get('uploads', [])
    if uploads:
        from prism_orders_api import SERVICE_EXPECTED_DOCS
        expected = SERVICE_EXPECTED_DOCS.get(svc, {}).get('pages', 1)
        actual = uploads[-1].get('pages', 0)
        deficit = max(0, expected - actual) / max(expected, 1)
        features['page_count_deficit'] = min(deficit, 1.0)
    else:
        features['page_count_deficit'] = 1.0

    # Temporal violations
    temporal_warnings = [w for w in auto_qc.get('warnings', []) if 'exceeds' in w.lower() or 'window' in w.lower()]
    features['temporal_violations'] = min(len(temporal_warnings) * 0.3, 1.0)

    # Auto QC fatal count
    fatal_count = len(auto_qc.get('fatal_flags', []))
    features['auto_qc_fatal_count'] = min(fatal_count * 0.25, 1.0)

    # Attempt number
    attempt = uploads[-1].get('attempt', 1) if uploads else 1
    features['attempt_number'] = min((attempt - 1) * 0.2, 1.0)

    # Time of day risk (submissions between 11pm-5am are higher risk)
    try:
        upload_time = uploads[-1].get('uploaded_at', '') if uploads else ''
        if upload_time:
            hour = datetime.fromisoformat(upload_time).hour
            features['time_of_day_risk'] = 0.5 if (hour >= 23 or hour < 5) else 0.0
        else:
            features['time_of_day_risk'] = 0.0
    except (ValueError, TypeError):
        features['time_of_day_risk'] = 0.0

    # Weighted sum
    score = sum(features.get(k, 0) * weights.get(k, 0) for k in weights)
    score = round(min(max(score, 0.0), 1.0), 4)

    if score <= AUTO_APPROVE_THRESHOLD:
        routing = 'auto_approve'
    elif score >= PRIORITY_REVIEW_THRESHOLD:
        routing = 'priority_review'
    else:
        routing = 'standard_review'

    return {
        'risk_score': score,
        'routing': routing,
        'features': features,
        'thresholds': {
            'auto_approve': AUTO_APPROVE_THRESHOLD,
            'priority_review': PRIORITY_REVIEW_THRESHOLD,
        },
        'scored_at': datetime.now().isoformat(),
    }


def train_risk_model(orders: list = None) -> dict:
    """Re-train risk model weights from historical QC outcomes.

    Uses a simple gradient descent on outcome prediction error:
    - For orders where scanback was 'Clean' → target = 0 (low risk was correct)
    - For orders where scanback had 'Errors Found' → target = 1 (high risk was correct)

    Returns updated weights and training stats.
    """
    if orders is None:
        orders = _load_json(ORDERS_FILE, [])

    labeled = []
    for o in orders:
        sb = o.get('scanback', {})
        if not sb:
            continue
        status = sb.get('status', '')
        if status == 'Clean':
            labeled.append((o, 0.0))
        elif status == 'Errors Found':
            labeled.append((o, 1.0))

    if len(labeled) < 10:
        return {
            'trained': False,
            'reason': f'Insufficient labeled data ({len(labeled)} orders, need >= 10)',
            'labeled_count': len(labeled),
        }

    weights = load_risk_weights()
    learning_rate = 0.01
    epochs = 50

    for _epoch in range(epochs):
        total_loss = 0.0
        for order, target in labeled:
            prediction = compute_risk_score(order)
            score = prediction['risk_score']
            error = target - score
            total_loss += error ** 2

            for key in weights:
                feat_val = prediction['features'].get(key, 0)
                weights[key] += learning_rate * error * feat_val
                weights[key] = max(0.01, min(weights[key], 1.0))

        # Normalize weights to sum to 1
        total = sum(weights.values())
        if total > 0:
            weights = {k: round(v / total, 4) for k, v in weights.items()}

    _save_json(RISK_MODEL_FILE, {
        'weights': weights,
        'trained_at': datetime.now().isoformat(),
        'labeled_count': len(labeled),
        'final_loss': round(total_loss / len(labeled), 6) if labeled else 0,
    })

    return {
        'trained': True,
        'weights': weights,
        'labeled_count': len(labeled),
        'final_loss': round(total_loss / len(labeled), 6) if labeled else 0,
        'trained_at': datetime.now().isoformat(),
    }


# ═══════════════════════════════════════════════════════════════════
# 2. AGENT QUALITY PROFILING
# ═══════════════════════════════════════════════════════════════════

TRAINING_TRIGGER_ERROR_RATE = 0.15
SUSPENSION_TRIGGER_ERROR_RATE = 0.30
MINIMUM_ORDERS_FOR_PROFILE = 5

AGENT_PROFILE_TEMPLATE = {
    'agent_name': '',
    'total_orders': 0,
    'total_errors': 0,
    'error_rate': 0.0,
    'errors_by_type': {},
    'errors_by_service': {},
    'correction_turnaround_avg_hrs': 0.0,
    'last_error_date': None,
    'last_clean_date': None,
    'status': 'active',
    'training_required': False,
    'training_triggers': [],
    'suspension_flag': False,
    'suspension_reason': None,
    'profile_updated_at': None,
}


def load_agent_profiles() -> dict:
    """Load all agent quality profiles."""
    return _load_json(AGENT_PROFILES_FILE, {})


def save_agent_profiles(profiles: dict):
    _save_json(AGENT_PROFILES_FILE, profiles)


def get_or_create_profile(agent_name: str, profiles: dict = None) -> dict:
    """Get an existing profile or create a new one."""
    if profiles is None:
        profiles = load_agent_profiles()
    if agent_name not in profiles:
        profile = AGENT_PROFILE_TEMPLATE.copy()
        profile['agent_name'] = agent_name
        profile['errors_by_type'] = {}
        profile['errors_by_service'] = {}
        profile['training_triggers'] = []
        profiles[agent_name] = profile
    return profiles[agent_name]


def record_qc_outcome(
    agent_name: str,
    order_id: str,
    service_type: str,
    outcome: str,
    errors: list = None,
    correction_hours: float = None,
) -> dict:
    """Record a QC outcome for an agent and update their profile.

    outcome: 'clean' or 'errors'
    errors: list of error descriptions if outcome == 'errors'
    correction_hours: hours to correct (resubmit) if applicable
    """
    profiles = load_agent_profiles()
    profile = get_or_create_profile(agent_name, profiles)

    profile['total_orders'] += 1
    now_iso = datetime.now().isoformat()
    profile['profile_updated_at'] = now_iso

    if outcome == 'clean':
        profile['last_clean_date'] = now_iso
    elif outcome == 'errors':
        profile['total_errors'] += 1
        profile['last_error_date'] = now_iso

        if errors:
            for err in errors:
                err_type = err.get('type', 'unclassified') if isinstance(err, dict) else str(err)
                profile['errors_by_type'][err_type] = profile['errors_by_type'].get(err_type, 0) + 1

        profile['errors_by_service'][service_type] = profile['errors_by_service'].get(service_type, 0) + 1

        if correction_hours is not None:
            prev_avg = profile.get('correction_turnaround_avg_hrs', 0)
            n = profile['total_errors']
            profile['correction_turnaround_avg_hrs'] = round(
                ((prev_avg * (n - 1)) + correction_hours) / n, 2
            )

    # Update error rate
    if profile['total_orders'] > 0:
        profile['error_rate'] = round(profile['total_errors'] / profile['total_orders'], 4)

    # Evaluate thresholds
    profile['training_required'] = False
    profile['training_triggers'] = []
    profile['suspension_flag'] = False
    profile['suspension_reason'] = None

    if profile['total_orders'] >= MINIMUM_ORDERS_FOR_PROFILE:
        if profile['error_rate'] >= SUSPENSION_TRIGGER_ERROR_RATE:
            profile['suspension_flag'] = True
            profile['suspension_reason'] = (
                f'Error rate {profile["error_rate"]:.1%} exceeds suspension threshold '
                f'({SUSPENSION_TRIGGER_ERROR_RATE:.0%}) over {profile["total_orders"]} orders'
            )
            profile['status'] = 'suspended'
        elif profile['error_rate'] >= TRAINING_TRIGGER_ERROR_RATE:
            profile['training_required'] = True
            profile['status'] = 'training_required'

            top_errors = sorted(
                profile['errors_by_type'].items(),
                key=lambda x: x[1],
                reverse=True,
            )[:3]
            profile['training_triggers'] = [
                f'{etype}: {count} occurrence(s)' for etype, count in top_errors
            ]
        else:
            profile['status'] = 'active'

    # Persist
    profiles[agent_name] = profile
    save_agent_profiles(profiles)

    # Also log to QC reports
    report = {
        'order_id': order_id,
        'agent_name': agent_name,
        'service_type': service_type,
        'outcome': outcome,
        'errors': errors or [],
        'correction_hours': correction_hours,
        'error_rate_after': profile['error_rate'],
        'status_after': profile['status'],
        'recorded_at': now_iso,
    }
    report_path = os.path.join(QC_REPORTS_DIR, f'{order_id}_{agent_name}.json')
    try:
        _save_json(report_path, report)
    except IOError:
        pass

    return profile


def build_all_profiles_from_history() -> dict:
    """Rebuild all agent profiles from order history. Useful for initial setup
    or periodic recalibration."""
    orders = _load_json(ORDERS_FILE, [])
    profiles = {}

    for o in orders:
        agent = o.get('agent', '')
        if not agent:
            continue
        sb = o.get('scanback', {})
        if not sb:
            continue

        status = sb.get('status', '')
        svc = o.get('type', '')
        order_id = o.get('id', '')

        if status == 'Clean':
            record_qc_outcome(agent, order_id, svc, 'clean')
        elif status == 'Errors Found':
            latest = sb.get('uploads', [{}])[-1] if sb.get('uploads') else {}
            errors = latest.get('errors', [])
            record_qc_outcome(agent, order_id, svc, 'errors', errors=errors)

    return load_agent_profiles()


def get_agents_needing_action() -> dict:
    """Return agents who need training or are suspended."""
    profiles = load_agent_profiles()
    training_needed = []
    suspended = []

    for name, profile in profiles.items():
        if profile.get('suspension_flag'):
            suspended.append({
                'agent': name,
                'error_rate': profile['error_rate'],
                'total_orders': profile['total_orders'],
                'reason': profile.get('suspension_reason', ''),
            })
        elif profile.get('training_required'):
            training_needed.append({
                'agent': name,
                'error_rate': profile['error_rate'],
                'total_orders': profile['total_orders'],
                'triggers': profile.get('training_triggers', []),
            })

    return {
        'training_needed': training_needed,
        'suspended': suspended,
        'total_agents': len(profiles),
        'checked_at': datetime.now().isoformat(),
    }


# ═══════════════════════════════════════════════════════════════════
# 3. DUPLICATE / ANOMALY DETECTION (foundation)
# ═══════════════════════════════════════════════════════════════════

def check_duplicate_upload(image_hash: str, order_id: str) -> dict:
    """Check if the same image (by hash) was uploaded for a different order.
    Flags potential fraud or accidental reuse."""
    orders = _load_json(ORDERS_FILE, [])
    matches = []

    for o in orders:
        if o.get('id') == order_id:
            continue
        sb = o.get('scanback', {})
        for upload in sb.get('uploads', []):
            for fh in upload.get('file_hashes', []):
                if fh == image_hash:
                    matches.append({
                        'order_id': o['id'],
                        'agent': o.get('agent', ''),
                        'uploaded_at': upload.get('uploaded_at', ''),
                    })

    return {
        'hash': image_hash,
        'duplicate_found': len(matches) > 0,
        'matches': matches,
        'checked_at': datetime.now().isoformat(),
    }


def detect_impossible_timeline(agent_name: str, window_hours: int = 2) -> list:
    """Flag orders by the same agent that are physically impossible
    (e.g., two collections 200 miles apart within a short window)."""
    orders = _load_json(ORDERS_FILE, [])
    agent_orders = [
        o for o in orders
        if o.get('agent') == agent_name and o.get('details', {}).get('collection_time')
    ]
    agent_orders.sort(key=lambda x: x['details']['collection_time'])

    flags = []
    for i in range(len(agent_orders) - 1):
        curr = agent_orders[i]
        nxt = agent_orders[i + 1]
        try:
            t1 = datetime.fromisoformat(curr['details']['collection_time'])
            t2 = datetime.fromisoformat(nxt['details']['collection_time'])
            gap_hrs = (t2 - t1).total_seconds() / 3600
            if gap_hrs < window_hours:
                loc1 = curr.get('address', 'unknown')
                loc2 = nxt.get('address', 'unknown')
                if loc1 != loc2:
                    flags.append({
                        'order_1': curr['id'],
                        'order_2': nxt['id'],
                        'location_1': loc1,
                        'location_2': loc2,
                        'gap_hours': round(gap_hrs, 2),
                        'note': f'Same agent, different locations, {gap_hrs:.1f}h apart — verify feasibility',
                    })
        except (ValueError, TypeError, KeyError):
            continue

    return flags


# ═══════════════════════════════════════════════════════════════════
# API ROUTES
# ═══════════════════════════════════════════════════════════════════

@prism_qc_learning.route('/prism/qc-learning/risk-score', methods=['POST'])
def api_risk_score():
    """Compute risk score for an order.
    Body: { order_id: "ORD-2026-001" } or { order: {full order object} }"""
    data = request.get_json(silent=True) or {}

    if 'order' in data:
        order = data['order']
    else:
        order_id = data.get('order_id', '')
        orders = _load_json(ORDERS_FILE, [])
        order = next((o for o in orders if o.get('id') == order_id), None)
        if not order:
            return jsonify({'error': 'Order not found'}), 404

    agent_name = order.get('agent', '')
    agent_profile = None
    if agent_name:
        profiles = load_agent_profiles()
        agent_profile = profiles.get(agent_name)

    result = compute_risk_score(order, agent_profile)
    return jsonify(result)


@prism_qc_learning.route('/prism/qc-learning/train', methods=['POST'])
def api_train_model():
    """Re-train the risk scoring model from historical QC outcomes."""
    result = train_risk_model()
    return jsonify(result)


@prism_qc_learning.route('/prism/qc-learning/agent-profile/<agent_name>', methods=['GET'])
def api_get_agent_profile(agent_name):
    """Get the quality profile for a specific agent."""
    profiles = load_agent_profiles()
    profile = profiles.get(agent_name)
    if not profile:
        return jsonify({'error': f'No profile for agent: {agent_name}'}), 404
    return jsonify(profile)


@prism_qc_learning.route('/prism/qc-learning/agent-profiles', methods=['GET'])
def api_list_agent_profiles():
    """List all agent quality profiles with summary stats."""
    profiles = load_agent_profiles()
    summary = []
    for name, p in profiles.items():
        summary.append({
            'agent': name,
            'total_orders': p.get('total_orders', 0),
            'error_rate': p.get('error_rate', 0),
            'status': p.get('status', 'active'),
            'training_required': p.get('training_required', False),
            'suspension_flag': p.get('suspension_flag', False),
        })
    summary.sort(key=lambda x: x['error_rate'], reverse=True)
    return jsonify({'profiles': summary, 'total': len(summary)})


@prism_qc_learning.route('/prism/qc-learning/record-outcome', methods=['POST'])
def api_record_outcome():
    """Record a QC outcome for an agent.
    Body: { agent_name, order_id, service_type, outcome: "clean"|"errors", errors: [...], correction_hours }"""
    data = request.get_json(silent=True) or {}
    required = ['agent_name', 'order_id', 'service_type', 'outcome']
    missing = [k for k in required if not data.get(k)]
    if missing:
        return jsonify({'error': f'Missing required fields: {", ".join(missing)}'}), 400

    profile = record_qc_outcome(
        agent_name=data['agent_name'],
        order_id=data['order_id'],
        service_type=data['service_type'],
        outcome=data['outcome'],
        errors=data.get('errors'),
        correction_hours=data.get('correction_hours'),
    )
    return jsonify({'success': True, 'profile': profile})


@prism_qc_learning.route('/prism/qc-learning/agents-action-needed', methods=['GET'])
def api_agents_action_needed():
    """Get agents who need training or are flagged for suspension."""
    result = get_agents_needing_action()
    return jsonify(result)


@prism_qc_learning.route('/prism/qc-learning/rebuild-profiles', methods=['POST'])
def api_rebuild_profiles():
    """Rebuild all agent profiles from order history."""
    profiles = build_all_profiles_from_history()
    return jsonify({
        'success': True,
        'agents_profiled': len(profiles),
        'rebuilt_at': datetime.now().isoformat(),
    })


@prism_qc_learning.route('/prism/qc-learning/check-duplicate', methods=['POST'])
def api_check_duplicate():
    """Check if an uploaded image hash was already used on another order.
    Body: { image_hash: "<sha256>", order_id: "ORD-2026-001" }"""
    data = request.get_json(silent=True) or {}
    image_hash = data.get('image_hash', '')
    order_id = data.get('order_id', '')
    if not image_hash:
        return jsonify({'error': 'image_hash is required'}), 400
    result = check_duplicate_upload(image_hash, order_id)
    return jsonify(result)


@prism_qc_learning.route('/prism/qc-learning/timeline-anomalies/<agent_name>', methods=['GET'])
def api_timeline_anomalies(agent_name):
    """Detect impossible timelines for an agent."""
    window = request.args.get('window_hours', 2, type=int)
    flags = detect_impossible_timeline(agent_name, window)
    return jsonify({
        'agent': agent_name,
        'anomalies': flags,
        'count': len(flags),
        'window_hours': window,
    })


@prism_qc_learning.route('/prism/qc-learning/model-weights', methods=['GET'])
def api_get_model_weights():
    """Return current risk model weights."""
    weights = load_risk_weights()
    return jsonify({
        'weights': weights,
        'thresholds': {
            'auto_approve': AUTO_APPROVE_THRESHOLD,
            'priority_review': PRIORITY_REVIEW_THRESHOLD,
        },
    })
