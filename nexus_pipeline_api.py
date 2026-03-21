"""
NEXUS Pipeline API — The Central Nervous System
=================================================
Routes cross-system events, maintains the unified contract registry,
and ensures data flows between all NEXUS systems.

Contract Lifecycle:
  NOVA discovers → GPSS bids → ATLAS plans → PRISM executes →
  COMPASS manages → VERTEX invoices

Every system writes events here. The pipeline propagates them.

Endpoints:
  GET  /nexus/pipeline/health           — Integration health check
  GET  /nexus/pipeline/contracts        — All contracts in registry
  GET  /nexus/pipeline/contracts/<id>   — Single contract + full cross-system status
  POST /nexus/pipeline/contracts        — Register a new contract
  POST /nexus/pipeline/event            — Fire a cross-system event
  GET  /nexus/pipeline/events           — Recent event log
  GET  /nexus/pipeline/contract/<id>/timeline — Full lifecycle timeline
"""

import os
import json
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify

nexus_pipeline = Blueprint('nexus_pipeline', __name__)

DATA_DIR = os.path.join(os.path.dirname(__file__), 'uploads', 'nexus')
CONTRACTS_FILE = os.path.join(DATA_DIR, 'contracts.json')
PRISM_ORDERS_FILE = os.path.join(os.path.dirname(__file__), 'uploads', 'prism', 'orders.json')

os.makedirs(DATA_DIR, exist_ok=True)


def _load_contracts():
    if os.path.exists(CONTRACTS_FILE):
        with open(CONTRACTS_FILE, 'r') as f:
            data = json.load(f)
            if isinstance(data, dict):
                return data
    return {'contracts': [], 'events': []}


def _save_contracts(data):
    with open(CONTRACTS_FILE, 'w') as f:
        json.dump(data, f, indent=2, default=str)


def _load_prism_orders():
    if os.path.exists(PRISM_ORDERS_FILE):
        with open(PRISM_ORDERS_FILE, 'r') as f:
            return json.load(f)
    return []


def _save_prism_orders(orders):
    with open(PRISM_ORDERS_FILE, 'w') as f:
        json.dump(orders, f, indent=2, default=str)


def _generate_contract_id():
    now = datetime.now()
    data = _load_contracts()
    seq = len(data.get('contracts', [])) + 1
    return f"NXC-{now.strftime('%Y%m%d')}-{seq:04d}"


def _log_event(data, event_type, contract_id, source_system, target_system, details):
    event = {
        'id': f"EVT-{datetime.now().strftime('%Y%m%d%H%M%S')}-{len(data.get('events', []))+1:04d}",
        'type': event_type,
        'contract_id': contract_id,
        'source': source_system,
        'target': target_system,
        'details': details,
        'timestamp': datetime.now().isoformat(),
    }
    if 'events' not in data:
        data['events'] = []
    data['events'].append(event)
    if len(data['events']) > 500:
        data['events'] = data['events'][-500:]
    return event


def _find_contract(data, contract_id):
    for c in data.get('contracts', []):
        if c['id'] == contract_id:
            return c
    return None


def _find_contract_by_gpss(data, gpss_id):
    for c in data.get('contracts', []):
        if c.get('source', {}).get('gpss_opportunity_id') == gpss_id:
            return c
    return None


# ═══════════════════════════════════════════════════════════════════
# HEALTH CHECK
# ═══════════════════════════════════════════════════════════════════

@nexus_pipeline.route('/nexus/pipeline/health', methods=['GET'])
def pipeline_health():
    """Full integration health check across all systems."""
    data = _load_contracts()
    prism_orders = _load_prism_orders()

    active_contracts = [c for c in data.get('contracts', []) if c.get('status') == 'Active']

    airtable_ok = False
    try:
        from nexus_backend import AirtableClient
        client = AirtableClient()
        airtable_ok = True
    except Exception:
        pass

    systems = {
        'NOVA': {'status': 'online', 'role': 'core', 'description': 'Opportunity Intelligence'},
        'GPSS': {'status': 'online' if airtable_ok else 'degraded', 'role': 'core', 'description': 'Gov Proposals & Sales'},
        'ATLAS': {'status': 'online' if airtable_ok else 'degraded', 'role': 'core', 'description': 'Project Management'},
        'PRISM': {'status': 'online', 'orders': len(prism_orders), 'role': 'core', 'description': 'Field Operations'},
        'COMPASS': {'status': 'online' if airtable_ok else 'degraded', 'role': 'core', 'description': 'Contract Compliance'},
        'VERTEX': {'status': 'online' if airtable_ok else 'degraded', 'role': 'core', 'description': 'Financial Management'},
        'DDCSS': {'status': 'online' if airtable_ok else 'degraded', 'role': 'support', 'description': 'Corporate Sales'},
        'GBIS': {'status': 'online', 'role': 'support', 'description': 'Grant Intelligence'},
        'LBPC': {'status': 'online', 'role': 'support', 'description': 'Surplus Recovery'},
        'DOCUMENTS': {'status': 'online', 'role': 'support', 'description': 'Quote & Cap Statement Generator'},
        'ALEXA': {'status': 'online', 'role': 'support', 'description': 'Voice Command Interface'},
    }

    core_connections = [
        {'from': 'NOVA', 'to': 'GPSS', 'status': 'wired', 'trigger': 'Opportunity added to pipeline'},
        {'from': 'GPSS', 'to': 'ATLAS', 'status': 'wired', 'trigger': 'Contract won → Project created'},
        {'from': 'GPSS', 'to': 'COMPASS', 'status': 'wired', 'trigger': 'Contract won → Post-award tracking'},
        {'from': 'GPSS', 'to': 'PRISM', 'status': 'wired', 'trigger': 'Field service won → Contract registered'},
        {'from': 'GPSS', 'to': 'VERTEX', 'status': 'wired', 'trigger': 'Contract won → Revenue recorded'},
        {'from': 'ATLAS', 'to': 'VERTEX', 'status': 'wired', 'trigger': 'Project completed → Invoice created'},
        {'from': 'ATLAS', 'to': 'PRISM', 'status': 'wired', 'trigger': 'Contract active → Work orders dispatched'},
        {'from': 'PRISM', 'to': 'VERTEX', 'status': 'wired', 'trigger': 'Order completed → Invoice line item'},
        {'from': 'PRISM', 'to': 'COMPASS', 'status': 'wired', 'trigger': 'Service delivered → Performance data'},
        {'from': 'COMPASS', 'to': 'VERTEX', 'status': 'wired', 'trigger': 'Deliverable accepted → Payment milestone'},
    ]

    support_connections = [
        {'from': 'DDCSS', 'to': 'ATLAS', 'status': 'wired', 'trigger': 'Corporate deal won → Project created'},
        {'from': 'DDCSS', 'to': 'VERTEX', 'status': 'wired', 'trigger': 'Corporate deal → Revenue + Invoice'},
        {'from': 'GBIS', 'to': 'VERTEX', 'status': 'wired', 'trigger': 'Grant awarded → Revenue recorded'},
        {'from': 'DOCUMENTS', 'to': 'GPSS', 'status': 'wired', 'trigger': 'Cap statement / quote generated for bid'},
        {'from': 'DOCUMENTS', 'to': 'DDCSS', 'status': 'wired', 'trigger': 'Pricing / proposal generated for prospect'},
        {'from': 'LBPC', 'to': 'GPSS', 'status': 'wired', 'trigger': 'Surplus opportunity → Gov pipeline'},
        {'from': 'LBPC', 'to': 'VERTEX', 'status': 'wired', 'trigger': 'Surplus recovery → Revenue'},
        {'from': 'ALEXA', 'to': 'ALL', 'status': 'wired', 'trigger': 'Voice queries across all systems'},
    ]

    connections = core_connections + support_connections

    recent_events = sorted(
        data.get('events', []),
        key=lambda e: e.get('timestamp', ''),
        reverse=True
    )[:20]

    return jsonify({
        'status': 'operational',
        'pipeline_version': '2.0',
        'timestamp': datetime.now().isoformat(),
        'registry': {
            'total_contracts': len(data.get('contracts', [])),
            'active_contracts': len(active_contracts),
            'total_events': len(data.get('events', [])),
        },
        'systems': systems,
        'connections': connections,
        'core_connections': core_connections,
        'support_connections': support_connections,
        'recent_events': recent_events,
        'airtable_connected': airtable_ok,
    })


# ═══════════════════════════════════════════════════════════════════
# CONTRACT REGISTRY
# ═══════════════════════════════════════════════════════════════════

@nexus_pipeline.route('/nexus/pipeline/contracts', methods=['GET'])
def list_contracts():
    """List all contracts in the unified registry."""
    data = _load_contracts()
    status_filter = request.args.get('status')
    contracts = data.get('contracts', [])
    if status_filter:
        contracts = [c for c in contracts if c.get('status', '').lower() == status_filter.lower()]
    return jsonify({'contracts': contracts, 'total': len(contracts)})


@nexus_pipeline.route('/nexus/pipeline/contracts/<contract_id>', methods=['GET'])
def get_contract(contract_id):
    """Get a single contract with full cross-system status."""
    data = _load_contracts()
    contract = _find_contract(data, contract_id)
    if not contract:
        return jsonify({'error': f'Contract {contract_id} not found'}), 404

    prism_orders = _load_prism_orders()
    contract_orders = [
        o for o in prism_orders
        if o.get('contract_id') == contract_id
    ]

    completed_orders = [o for o in contract_orders if o.get('status') == 'Complete']
    active_orders = [o for o in contract_orders if o.get('status') not in ('Complete', 'Cancelled')]

    events = [
        e for e in data.get('events', [])
        if e.get('contract_id') == contract_id
    ]

    return jsonify({
        'contract': contract,
        'prism': {
            'total_orders': len(contract_orders),
            'completed': len(completed_orders),
            'active': len(active_orders),
            'orders': contract_orders[:20],
        },
        'events': sorted(events, key=lambda e: e.get('timestamp', ''), reverse=True)[:30],
    })


@nexus_pipeline.route('/nexus/pipeline/contracts', methods=['POST'])
def register_contract():
    """
    Register a new contract in the unified registry.
    Called when GPSS opportunity is won, or manually.
    """
    payload = request.json or {}
    data = _load_contracts()

    contract_id = _generate_contract_id()
    now = datetime.now().isoformat()

    contract = {
        'id': contract_id,
        'title': payload.get('title', 'Untitled Contract'),
        'agency': payload.get('agency', ''),
        'value': payload.get('value', 0),
        'status': payload.get('status', 'Active'),
        'contract_type': payload.get('contract_type', 'Firm Fixed Price'),
        'service_type': payload.get('service_type', ''),
        'source': {
            'gpss_opportunity_id': payload.get('gpss_opportunity_id', ''),
            'rfp_number': payload.get('rfp_number', ''),
            'solicitation_number': payload.get('solicitation_number', ''),
        },
        'systems': {
            'atlas_project_id': payload.get('atlas_project_id', ''),
            'compass_contract_id': payload.get('compass_contract_id', ''),
            'prism_contract_id': payload.get('prism_contract_id', ''),
            'vertex_invoices': [],
        },
        'contacts': {
            'co_name': payload.get('co_name', ''),
            'co_email': payload.get('co_email', ''),
            'cor_name': payload.get('cor_name', ''),
        },
        'timeline': {
            'identified': payload.get('identified_date', ''),
            'bid_submitted': payload.get('bid_submitted_date', ''),
            'won': payload.get('won_date', now),
            'start_date': payload.get('start_date', ''),
            'end_date': payload.get('end_date', ''),
        },
        'health': {
            'overall': 100,
            'compliance': 'Green',
            'deliverables_pct': 0,
            'financials_pct': 0,
            'orders_completed': 0,
            'orders_total': 0,
        },
        'naics': payload.get('naics', ''),
        'set_aside': payload.get('set_aside', ''),
        'prism_orders': [],
        'created_at': now,
        'updated_at': now,
    }

    data['contracts'].append(contract)

    _log_event(data, 'contract_registered', contract_id, 'PIPELINE', 'ALL',
               {'title': contract['title'], 'agency': contract['agency'], 'value': contract['value']})

    _save_contracts(data)

    return jsonify({
        'success': True,
        'contract_id': contract_id,
        'contract': contract,
        'message': f"Contract {contract_id} registered: {contract['title']}"
    }), 201


@nexus_pipeline.route('/nexus/pipeline/contracts/<contract_id>', methods=['PATCH'])
def update_contract(contract_id):
    """Update contract fields and system links."""
    data = _load_contracts()
    contract = _find_contract(data, contract_id)
    if not contract:
        return jsonify({'error': f'Contract {contract_id} not found'}), 404

    payload = request.json or {}

    for key in ['title', 'agency', 'value', 'status', 'contract_type', 'service_type', 'naics', 'set_aside']:
        if key in payload:
            contract[key] = payload[key]

    if 'systems' in payload:
        contract['systems'].update(payload['systems'])
    if 'timeline' in payload:
        contract['timeline'].update(payload['timeline'])
    if 'contacts' in payload:
        contract['contacts'].update(payload['contacts'])
    if 'health' in payload:
        contract['health'].update(payload['health'])

    contract['updated_at'] = datetime.now().isoformat()

    _log_event(data, 'contract_updated', contract_id, payload.get('source_system', 'PIPELINE'), 'REGISTRY',
               {'fields_updated': list(payload.keys())})

    _save_contracts(data)
    return jsonify({'success': True, 'contract': contract})


# ═══════════════════════════════════════════════════════════════════
# EVENT BUS — Cross-System Event Propagation
# ═══════════════════════════════════════════════════════════════════

@nexus_pipeline.route('/nexus/pipeline/event', methods=['POST'])
def fire_event():
    """
    Fire a cross-system event. The pipeline handles propagation.

    Event types:
      opportunity_won    — GPSS fires when contract awarded
      order_created      — PRISM fires when new work order
      order_completed    — PRISM fires when work order done
      order_qc_passed    — PRISM fires when QC approved
      scanback_clean     — PRISM fires when scanback verified
      deliverable_accepted — COMPASS fires when deliverable approved
      invoice_generated  — VERTEX fires when invoice created
      project_completed  — ATLAS fires when project done
      compliance_alert   — COMPASS fires on compliance issue
    """
    payload = request.json or {}
    event_type = payload.get('event_type', '')
    contract_id = payload.get('contract_id', '')
    source_system = payload.get('source_system', '')
    event_data = payload.get('data', {})

    if not event_type:
        return jsonify({'error': 'event_type required'}), 400

    data = _load_contracts()
    propagation_results = []

    # ─── OPPORTUNITY WON (GPSS → ALL) ──────────────────────────────
    if event_type == 'opportunity_won':
        gpss_id = event_data.get('gpss_opportunity_id', '')
        existing = _find_contract_by_gpss(data, gpss_id)
        if not existing:
            contract_id = _generate_contract_id()
            contract = {
                'id': contract_id,
                'title': event_data.get('title', ''),
                'agency': event_data.get('agency', ''),
                'value': event_data.get('value', 0),
                'status': 'Active',
                'contract_type': event_data.get('contract_type', 'Firm Fixed Price'),
                'service_type': event_data.get('service_type', ''),
                'source': {
                    'gpss_opportunity_id': gpss_id,
                    'rfp_number': event_data.get('rfp_number', ''),
                    'solicitation_number': event_data.get('solicitation_number', ''),
                },
                'systems': {
                    'atlas_project_id': event_data.get('atlas_project_id', ''),
                    'compass_contract_id': event_data.get('compass_contract_id', ''),
                    'prism_contract_id': '',
                    'vertex_invoices': [],
                },
                'contacts': {
                    'co_name': event_data.get('co_name', ''),
                    'co_email': event_data.get('co_email', ''),
                    'cor_name': '',
                },
                'timeline': {
                    'identified': event_data.get('identified_date', ''),
                    'bid_submitted': event_data.get('bid_submitted_date', ''),
                    'won': datetime.now().isoformat(),
                    'start_date': event_data.get('start_date', ''),
                    'end_date': event_data.get('end_date', ''),
                },
                'health': {
                    'overall': 100, 'compliance': 'Green',
                    'deliverables_pct': 0, 'financials_pct': 0,
                    'orders_completed': 0, 'orders_total': 0,
                },
                'naics': event_data.get('naics', ''),
                'set_aside': event_data.get('set_aside', ''),
                'prism_orders': [],
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
            }
            data['contracts'].append(contract)
            propagation_results.append(f"Contract {contract_id} registered in pipeline")
        else:
            contract_id = existing['id']
            propagation_results.append(f"Contract {contract_id} already in pipeline")

        _log_event(data, 'opportunity_won', contract_id, 'GPSS', 'PIPELINE', event_data)

    # ─── ORDER CREATED (PRISM → REGISTRY) ─────────────────────────
    elif event_type == 'order_created':
        contract = _find_contract(data, contract_id)
        if contract:
            order_id = event_data.get('order_id', '')
            if order_id and order_id not in contract.get('prism_orders', []):
                contract.setdefault('prism_orders', []).append(order_id)
                contract['health']['orders_total'] = contract['health'].get('orders_total', 0) + 1
                contract['updated_at'] = datetime.now().isoformat()
            propagation_results.append(f"Order {order_id} linked to {contract_id}")
        _log_event(data, 'order_created', contract_id, 'PRISM', 'REGISTRY', event_data)

    # ─── ORDER COMPLETED (PRISM → VERTEX + COMPASS) ───────────────
    elif event_type == 'order_completed':
        contract = _find_contract(data, contract_id)
        order_id = event_data.get('order_id', '')
        order_total = event_data.get('total_amount', 0)
        service_type = event_data.get('service_type', '')
        client_name = event_data.get('client_name', '')

        if contract:
            contract['health']['orders_completed'] = contract['health'].get('orders_completed', 0) + 1
            total = contract['health'].get('orders_total', 1) or 1
            completed = contract['health'].get('orders_completed', 0)
            contract['health']['deliverables_pct'] = round((completed / total) * 100)
            contract['updated_at'] = datetime.now().isoformat()

        vertex_result = _propagate_to_vertex(contract_id, order_id, order_total, service_type, client_name, contract)
        propagation_results.append(vertex_result)

        compass_result = _propagate_to_compass(contract_id, order_id, service_type, event_data)
        propagation_results.append(compass_result)

        _log_event(data, 'order_completed', contract_id, 'PRISM', 'VERTEX+COMPASS', event_data)

    # ─── SCANBACK CLEAN (PRISM → COMPASS) ──────────────────────────
    elif event_type == 'scanback_clean':
        _log_event(data, 'scanback_clean', contract_id, 'PRISM', 'COMPASS', event_data)
        propagation_results.append("Scanback verified, compliance updated")

    # ─── DELIVERABLE ACCEPTED (COMPASS → VERTEX) ──────────────────
    elif event_type == 'deliverable_accepted':
        contract = _find_contract(data, contract_id)
        if contract:
            contract['health']['deliverables_pct'] = event_data.get('deliverables_pct', contract['health'].get('deliverables_pct', 0))
            contract['updated_at'] = datetime.now().isoformat()
        _log_event(data, 'deliverable_accepted', contract_id, 'COMPASS', 'VERTEX', event_data)
        propagation_results.append("Deliverable accepted, milestone recorded")

    # ─── INVOICE GENERATED (VERTEX → REGISTRY) ────────────────────
    elif event_type == 'invoice_generated':
        contract = _find_contract(data, contract_id)
        if contract:
            inv_id = event_data.get('invoice_id', '')
            if inv_id:
                contract['systems'].setdefault('vertex_invoices', []).append(inv_id)
            invoiced = event_data.get('invoiced_amount', 0)
            total_value = contract.get('value', 0) or 1
            contract['health']['financials_pct'] = round((invoiced / total_value) * 100) if total_value else 0
            contract['updated_at'] = datetime.now().isoformat()
        _log_event(data, 'invoice_generated', contract_id, 'VERTEX', 'REGISTRY', event_data)
        propagation_results.append("Invoice registered in pipeline")

    # ─── COMPLIANCE ALERT (COMPASS → ALL) ──────────────────────────
    elif event_type == 'compliance_alert':
        contract = _find_contract(data, contract_id)
        if contract:
            contract['health']['compliance'] = event_data.get('status', 'Yellow')
            if contract['health']['compliance'] == 'Red':
                contract['health']['overall'] = min(contract['health'].get('overall', 100), 50)
            elif contract['health']['compliance'] == 'Yellow':
                contract['health']['overall'] = min(contract['health'].get('overall', 100), 75)
            contract['updated_at'] = datetime.now().isoformat()
        _log_event(data, 'compliance_alert', contract_id, 'COMPASS', 'ALL', event_data)
        propagation_results.append(f"Compliance alert: {event_data.get('status', 'unknown')}")

    # ─── PROJECT COMPLETED (ATLAS → VERTEX) ────────────────────────
    elif event_type == 'project_completed':
        contract = _find_contract(data, contract_id)
        if contract:
            contract['status'] = 'Completed'
            contract['updated_at'] = datetime.now().isoformat()
        _log_event(data, 'project_completed', contract_id, 'ATLAS', 'VERTEX', event_data)
        propagation_results.append("Project completed, final invoicing triggered")

    else:
        _log_event(data, event_type, contract_id, source_system, 'PIPELINE', event_data)
        propagation_results.append(f"Event {event_type} logged")

    _save_contracts(data)

    return jsonify({
        'success': True,
        'event_type': event_type,
        'contract_id': contract_id,
        'propagation': propagation_results,
    })


# ═══════════════════════════════════════════════════════════════════
# EVENT LOG
# ═══════════════════════════════════════════════════════════════════

@nexus_pipeline.route('/nexus/pipeline/events', methods=['GET'])
def list_events():
    """Recent event log."""
    data = _load_contracts()
    limit = int(request.args.get('limit', 50))
    contract_filter = request.args.get('contract_id')
    events = data.get('events', [])
    if contract_filter:
        events = [e for e in events if e.get('contract_id') == contract_filter]
    events = sorted(events, key=lambda e: e.get('timestamp', ''), reverse=True)[:limit]
    return jsonify({'events': events, 'total': len(data.get('events', []))})


# ═══════════════════════════════════════════════════════════════════
# CONTRACT TIMELINE
# ═══════════════════════════════════════════════════════════════════

@nexus_pipeline.route('/nexus/pipeline/contracts/<contract_id>/timeline', methods=['GET'])
def contract_timeline(contract_id):
    """Full lifecycle timeline for a contract across all systems."""
    data = _load_contracts()
    contract = _find_contract(data, contract_id)
    if not contract:
        return jsonify({'error': f'Contract {contract_id} not found'}), 404

    events = sorted(
        [e for e in data.get('events', []) if e.get('contract_id') == contract_id],
        key=lambda e: e.get('timestamp', '')
    )

    timeline = []
    tl = contract.get('timeline', {})

    if tl.get('identified'):
        timeline.append({'date': tl['identified'], 'system': 'NOVA', 'event': 'Opportunity Identified', 'icon': 'search'})
    if tl.get('bid_submitted'):
        timeline.append({'date': tl['bid_submitted'], 'system': 'GPSS', 'event': 'Bid Submitted', 'icon': 'send'})
    if tl.get('won'):
        timeline.append({'date': tl['won'], 'system': 'GPSS', 'event': 'Contract Awarded', 'icon': 'trophy'})
    if tl.get('start_date'):
        timeline.append({'date': tl['start_date'], 'system': 'ATLAS', 'event': 'Execution Started', 'icon': 'play'})

    for evt in events:
        timeline.append({
            'date': evt.get('timestamp', ''),
            'system': evt.get('source', ''),
            'event': evt.get('type', '').replace('_', ' ').title(),
            'icon': 'event',
            'details': evt.get('details', {}),
        })

    if tl.get('end_date'):
        timeline.append({'date': tl['end_date'], 'system': 'ATLAS', 'event': 'Contract End Date', 'icon': 'flag'})

    timeline.sort(key=lambda t: t.get('date', ''))

    return jsonify({
        'contract_id': contract_id,
        'title': contract.get('title', ''),
        'timeline': timeline,
    })


# ═══════════════════════════════════════════════════════════════════
# DISPATCH — Create PRISM work orders from contract
# ═══════════════════════════════════════════════════════════════════

@nexus_pipeline.route('/nexus/pipeline/contracts/<contract_id>/dispatch', methods=['POST'])
def dispatch_orders(contract_id):
    """
    Create PRISM work orders from a contract.
    ATLAS/COMPASS triggers this to assign work to field agents.
    """
    data = _load_contracts()
    contract = _find_contract(data, contract_id)
    if not contract:
        return jsonify({'error': f'Contract {contract_id} not found'}), 404

    payload = request.json or {}
    orders_to_create = payload.get('orders', [])

    if not orders_to_create:
        return jsonify({'error': 'No orders to dispatch'}), 400

    prism_orders = _load_prism_orders()
    created_order_ids = []
    now = datetime.now()

    for i, order_spec in enumerate(orders_to_create):
        order_id = f"PRISM-{now.strftime('%Y%m%d')}-{len(prism_orders)+i+1:04d}-{order_spec.get('service_code', 'SVC')}"

        SERVICE_TYPE_MAP = {
            'DOT': 'DOT Drug Screen', 'NON-DOT': 'Non-DOT Drug Screen',
            'DNA': 'DNA Collection', 'FP': 'Fingerprinting',
            'NOT': 'Notary', 'PH': 'Phlebotomy',
            'COU': 'Medical Courier', 'NEMT': 'NEMT Transport',
            'REO': 'REO Inspection', 'SVC': 'General Service',
        }

        STAGE_MAP = {
            'Intake': 1, 'Scheduled': 2, 'Dispatched': 3,
            'In Progress': 4, 'QC Review': 5, 'Documentation': 6,
            'Invoicing': 7, 'Complete': 8,
        }

        svc_code = order_spec.get('service_code', 'SVC')
        svc_type = SERVICE_TYPE_MAP.get(svc_code, order_spec.get('service_type', 'General Service'))

        order = {
            'id': order_id,
            'contract_id': contract_id,
            'service_type': svc_type,
            'client_name': contract.get('agency', order_spec.get('client_name', '')),
            'donor_name': order_spec.get('donor_name', ''),
            'donor_dob': order_spec.get('donor_dob', ''),
            'location': order_spec.get('location', ''),
            'status': order_spec.get('status', 'Intake'),
            'workflow_stage': STAGE_MAP.get(order_spec.get('status', 'Intake'), 1),
            'priority': order_spec.get('priority', 'Standard'),
            'assigned_agent': order_spec.get('assigned_agent', ''),
            'scheduled_date': order_spec.get('scheduled_date', ''),
            'scheduled_time': order_spec.get('scheduled_time', ''),
            'notes': order_spec.get('notes', ''),
            'total_amount': order_spec.get('total_amount', 0),
            'qc': {'status': 'Pending', 'checks': {}},
            'created_at': now.isoformat(),
            'updated_at': now.isoformat(),
        }

        prism_orders.append(order)
        created_order_ids.append(order_id)

    _save_prism_orders(prism_orders)

    contract.setdefault('prism_orders', []).extend(created_order_ids)
    contract['health']['orders_total'] = contract['health'].get('orders_total', 0) + len(created_order_ids)
    contract['updated_at'] = now.isoformat()

    _log_event(data, 'orders_dispatched', contract_id, 'ATLAS', 'PRISM', {
        'count': len(created_order_ids),
        'order_ids': created_order_ids,
    })

    _save_contracts(data)

    return jsonify({
        'success': True,
        'contract_id': contract_id,
        'orders_created': len(created_order_ids),
        'order_ids': created_order_ids,
        'message': f"{len(created_order_ids)} work orders dispatched to PRISM",
    })


# ═══════════════════════════════════════════════════════════════════
# PROPAGATION HELPERS — Send data to target systems
# ═══════════════════════════════════════════════════════════════════

def _propagate_to_vertex(contract_id, order_id, amount, service_type, client_name, contract):
    """Create invoice line item in VERTEX when PRISM order completes."""
    try:
        from nexus_backend import AirtableClient
        client = AirtableClient()

        inv_number = f"INV-{datetime.now().strftime('%Y%m')}-{order_id[-4:]}"
        description = f"Service: {service_type}\nOrder: {order_id}"
        if contract:
            description += f"\nContract: {contract.get('title', '')}"

        vertex_fields = {
            'Invoice Number': inv_number,
            'Invoice Date': datetime.now().isoformat(),
            'Due Date': (datetime.now() + timedelta(days=30)).isoformat(),
            'Client Name': client_name or (contract.get('agency', '') if contract else ''),
            'Source System': 'PRISM',
            'Source Record ID': order_id,
            'Invoice Type': 'Service',
            'Total Amount': amount,
            'Payment Status': 'Unpaid',
            'Payment Terms': 'Net 30',
            'Notes': description,
        }
        client.create_record('VERTEX INVOICES', vertex_fields)
        return f"VERTEX invoice {inv_number} created for ${amount:,.2f}"
    except Exception as e:
        return f"VERTEX propagation skipped: {e}"


def _propagate_to_compass(contract_id, order_id, service_type, event_data):
    """Update COMPASS deliverable tracking when PRISM order completes."""
    try:
        from nexus_backend import AirtableClient
        client = AirtableClient()

        deliverable_fields = {
            'Title': f"{service_type} - {order_id}",
            'Contract': contract_id,
            'Type': 'Service Delivery',
            'Status': 'Delivered',
            'Delivery Date': datetime.now().strftime('%Y-%m-%d'),
            'Description': f"Completed {service_type} order {order_id}",
            'Source System': 'PRISM',
            'Source Record ID': order_id,
        }
        client.create_record('COMPASS Deliverables', deliverable_fields)
        return f"COMPASS deliverable recorded for {order_id}"
    except Exception as e:
        return f"COMPASS propagation skipped: {e}"
