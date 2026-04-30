"""
COMPASS — Contract Operations Management & Post-Award System
=============================================================
Post-award contract execution: compliance, deliverables, CO communication,
modifications, performance reporting, sub oversight, payment tracking.

Sits between ATLAS (project plan) and VERTEX (financials).
Receives field service data from PRISM.

Flow:
  GPSS Win → ATLAS project → COMPASS contract → PRISM orders → VERTEX invoices
"""

import os
import json
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify

compass = Blueprint('compass', __name__)

# ─── NEXUS LEARNING ENGINE INTEGRATION ────────────────────────────────────────
try:
    from nexus_learning_engine import nxlearn
except ImportError:
    def nxlearn(*args, **kwargs):
        pass  # Graceful fallback if learning engine not available


def get_airtable():
    try:
        from pyairtable import Api
        token = os.environ.get('AIRTABLE_TOKEN') or os.environ.get('AIRTABLE_API_KEY', '')
        base_id = os.environ.get('AIRTABLE_BASE_ID', '')
        if token and base_id:
            return Api(token), base_id
    except Exception:
        pass
    return None, None


# ═══════════════════════════════════════════════════════════════════════════
# 1. CONTRACT MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════════

@compass.route('/compass/contracts', methods=['GET'])
def get_contracts():
    """Get all active contracts under management."""
    api, base_id = get_airtable()
    if not api or not base_id:
        return jsonify({'contracts': [], 'message': 'Airtable not configured'}), 200
    try:
        table = api.table(base_id, 'COMPASS Contracts')
        records = table.all()
        contracts = []
        for r in records:
            f = r.get('fields', {})
            contracts.append({
                'id': r['id'],
                'contract_number': f.get('Contract Number', ''),
                'title': f.get('Title', ''),
                'agency': f.get('Agency', ''),
                'value': f.get('Value', 0),
                'type': f.get('Contract Type', ''),
                'status': f.get('Status', 'Active'),
                'start_date': f.get('Start Date', ''),
                'end_date': f.get('End Date', ''),
                'pop': f.get('Period of Performance', ''),
                'co_name': f.get('CO Name', ''),
                'co_email': f.get('CO Email', ''),
                'cor_name': f.get('COR Name', ''),
                'naics': f.get('NAICS', ''),
                'set_aside': f.get('Set Aside', ''),
                'gpss_opportunity': f.get('GPSS Opportunity', []),
                'atlas_project': f.get('ATLAS Project', []),
                'prism_contract': f.get('PRISM Contract', []),
                'health_score': f.get('Health Score', 100),
                'compliance_status': f.get('Compliance Status', 'Green'),
                'invoiced_amount': f.get('Invoiced Amount', 0),
                'paid_amount': f.get('Paid Amount', 0),
                'deliverables_total': f.get('Deliverables Total', 0),
                'deliverables_complete': f.get('Deliverables Complete', 0),
                'next_report_due': f.get('Next Report Due', ''),
                'cpars_rating': f.get('CPARS Rating', ''),
                'created': f.get('Created Date', ''),
            })
        contracts.sort(key=lambda c: c.get('end_date', ''), reverse=True)
        return jsonify({'contracts': contracts})
    except Exception as e:
        return jsonify({'contracts': [], 'error': str(e)}), 200


@compass.route('/compass/contracts', methods=['POST'])
def create_contract():
    """Create a new contract for post-award management."""
    data = request.json or {}
    api, base_id = get_airtable()
    if not api or not base_id:
        return jsonify({'error': 'Airtable not configured'}), 503

    try:
        table = api.table(base_id, 'COMPASS Contracts')
        fields = {
            'Contract Number': data.get('contract_number', ''),
            'Title': data.get('title', ''),
            'Agency': data.get('agency', ''),
            'Value': data.get('value', 0),
            'Contract Type': data.get('type', 'Firm Fixed Price'),
            'Status': 'Active',
            'Start Date': data.get('start_date', datetime.now().strftime('%Y-%m-%d')),
            'End Date': data.get('end_date', ''),
            'Period of Performance': data.get('pop', ''),
            'CO Name': data.get('co_name', ''),
            'CO Email': data.get('co_email', ''),
            'COR Name': data.get('cor_name', ''),
            'NAICS': data.get('naics', ''),
            'Set Aside': data.get('set_aside', ''),
            'Health Score': 100,
            'Compliance Status': 'Green',
            'Created Date': datetime.now().isoformat(),
        }
        if data.get('gpss_opportunity_id'):
            fields['GPSS Opportunity'] = [data['gpss_opportunity_id']]
        if data.get('atlas_project_id'):
            fields['ATLAS Project'] = [data['atlas_project_id']]

        record = table.create(fields)

        # Advisor
        try:
            from nexus_advisor import advise
            advisor = advise('compass', 'contract_activated', {
                'agency': data.get('agency', ''),
                'value': data.get('value', 0),
                'type': data.get('type', ''),
            })
        except Exception:
            advisor = None

        return jsonify({
            'success': True,
            'contract': {'id': record['id'], **fields},
            'advisor': advisor,
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@compass.route('/compass/contracts/<contract_id>', methods=['GET'])
def get_contract(contract_id):
    """Get full contract detail with all related data."""
    api, base_id = get_airtable()
    if not api or not base_id:
        return jsonify({'error': 'Airtable not configured'}), 503
    try:
        table = api.table(base_id, 'COMPASS Contracts')
        record = table.get(contract_id)
        f = record.get('fields', {})

        deliverables = []
        try:
            d_table = api.table(base_id, 'COMPASS Deliverables')
            d_records = d_table.all(formula=f"FIND('{contract_id}', ARRAYJOIN({{Contract}}, ','))")
            for d in d_records:
                df = d.get('fields', {})
                deliverables.append({
                    'id': d['id'],
                    'title': df.get('Title', ''),
                    'status': df.get('Status', 'Pending'),
                    'due_date': df.get('Due Date', ''),
                    'completed_date': df.get('Completed Date', ''),
                    'type': df.get('Type', ''),
                })
        except Exception:
            pass

        comms = []
        try:
            c_table = api.table(base_id, 'COMPASS Communications')
            c_records = c_table.all(formula=f"FIND('{contract_id}', ARRAYJOIN({{Contract}}, ','))")
            for c in c_records:
                cf = c.get('fields', {})
                comms.append({
                    'id': c['id'],
                    'date': cf.get('Date', ''),
                    'type': cf.get('Type', ''),
                    'subject': cf.get('Subject', ''),
                    'summary': cf.get('Summary', ''),
                    'direction': cf.get('Direction', ''),
                    'contact': cf.get('Contact', ''),
                })
        except Exception:
            pass

        mods = []
        try:
            m_table = api.table(base_id, 'COMPASS Modifications')
            m_records = m_table.all(formula=f"FIND('{contract_id}', ARRAYJOIN({{Contract}}, ','))")
            for m in m_records:
                mf = m.get('fields', {})
                mods.append({
                    'id': m['id'],
                    'mod_number': mf.get('Mod Number', ''),
                    'type': mf.get('Type', ''),
                    'description': mf.get('Description', ''),
                    'value_change': mf.get('Value Change', 0),
                    'status': mf.get('Status', ''),
                    'date': mf.get('Date', ''),
                })
        except Exception:
            pass

        return jsonify({
            'contract': {
                'id': record['id'],
                **{k: v for k, v in f.items()},
            },
            'deliverables': deliverables,
            'communications': comms,
            'modifications': mods,
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@compass.route('/compass/contracts/<contract_id>', methods=['PUT'])
def update_contract(contract_id):
    """Update contract fields."""
    data = request.json or {}
    api, base_id = get_airtable()
    if not api or not base_id:
        return jsonify({'error': 'Airtable not configured'}), 503
    try:
        table = api.table(base_id, 'COMPASS Contracts')
        update = {}
        field_map = {
            'status': 'Status', 'health_score': 'Health Score',
            'compliance_status': 'Compliance Status', 'co_name': 'CO Name',
            'co_email': 'CO Email', 'cor_name': 'COR Name',
            'end_date': 'End Date', 'cpars_rating': 'CPARS Rating',
            'next_report_due': 'Next Report Due', 'notes': 'Notes',
            'invoiced_amount': 'Invoiced Amount', 'paid_amount': 'Paid Amount',
        }
        for k, v in field_map.items():
            if k in data:
                update[v] = data[k]

        old_record = table.get(contract_id)
        old_status = old_record['fields'].get('Status', '')
        table.update(contract_id, update)

        new_status = update.get('Status', old_status)

        # Contract completed — trigger debrief
        advisor_insight = None
        if new_status == 'Completed' and old_status != 'Completed':
            try:
                from nexus_advisor import debrief as advisor_debrief, log_growth
                advisor_insight = advisor_debrief('contract_complete', {
                    'agency': old_record['fields'].get('Agency', ''),
                    'value': old_record['fields'].get('Value', 0),
                })
            except Exception:
                pass

            # VERTEX: Mark revenue as realized
            try:
                from nexus_backend import AirtableClient
                ac = AirtableClient()
                ac.create_record('VERTEX REVENUE', {
                    'Date': datetime.now().strftime('%Y-%m-%d'),
                    'Source System': 'COMPASS',
                    'Source Record ID': contract_id,
                    'Client Name': old_record['fields'].get('Agency', ''),
                    'Amount': old_record['fields'].get('Value', 0),
                    'Category': 'Contract Completed',
                    'Status': 'Realized',
                })
            except Exception:
                pass

        return jsonify({'success': True, 'advisor': advisor_insight})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ═══════════════════════════════════════════════════════════════════════════
# 2. DELIVERABLE TRACKING
# ═══════════════════════════════════════════════════════════════════════════

@compass.route('/compass/deliverables', methods=['POST'])
def create_deliverable():
    """Add a deliverable to a contract."""
    data = request.json or {}
    api, base_id = get_airtable()
    if not api or not base_id:
        return jsonify({'error': 'Airtable not configured'}), 503
    try:
        table = api.table(base_id, 'COMPASS Deliverables')
        fields = {
            'Title': data.get('title', ''),
            'Type': data.get('type', 'Report'),
            'Status': 'Pending',
            'Due Date': data.get('due_date', ''),
            'Description': data.get('description', ''),
            'CLIN': data.get('clin', ''),
            'Quantity': data.get('quantity', 1),
        }
        if data.get('contract_id'):
            fields['Contract'] = [data['contract_id']]

        record = table.create(fields)

        # Update contract deliverable count
        if data.get('contract_id'):
            try:
                c_table = api.table(base_id, 'COMPASS Contracts')
                contract = c_table.get(data['contract_id'])
                total = (contract['fields'].get('Deliverables Total', 0) or 0) + 1
                c_table.update(data['contract_id'], {'Deliverables Total': total})
            except Exception:
                pass

        return jsonify({'success': True, 'deliverable': {'id': record['id'], **fields}}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@compass.route('/compass/deliverables/<deliverable_id>', methods=['PUT'])
def update_deliverable(deliverable_id):
    """Update deliverable status."""
    data = request.json or {}
    api, base_id = get_airtable()
    if not api or not base_id:
        return jsonify({'error': 'Airtable not configured'}), 503
    try:
        table = api.table(base_id, 'COMPASS Deliverables')
        update = {}
        if 'status' in data:
            update['Status'] = data['status']
        if 'completed_date' in data:
            update['Completed Date'] = data['completed_date']
        if 'notes' in data:
            update['Notes'] = data['notes']

        old = table.get(deliverable_id)
        table.update(deliverable_id, update)

        # If completed, update contract count + advisor
        if data.get('status') == 'Completed' and old['fields'].get('Status') != 'Completed':
            if update.get('Completed Date') is None:
                table.update(deliverable_id, {'Completed Date': datetime.now().strftime('%Y-%m-%d')})
            contract_links = old['fields'].get('Contract', [])
            if contract_links:
                try:
                    c_table = api.table(base_id, 'COMPASS Contracts')
                    contract = c_table.get(contract_links[0])
                    complete = (contract['fields'].get('Deliverables Complete', 0) or 0) + 1
                    c_table.update(contract_links[0], {'Deliverables Complete': complete})
                except Exception:
                    pass

            try:
                from nexus_advisor import advise
                return jsonify({
                    'success': True,
                    'advisor': advise('compass', 'deliverable_completed', {
                        'title': old['fields'].get('Title', ''),
                    }),
                })
            except Exception:
                pass

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ═══════════════════════════════════════════════════════════════════════════
# 3. CO / COR COMMUNICATION LOG
# ═══════════════════════════════════════════════════════════════════════════

@compass.route('/compass/communications', methods=['POST'])
def log_communication():
    """Log a communication with the CO/COR."""
    data = request.json or {}
    api, base_id = get_airtable()
    if not api or not base_id:
        return jsonify({'error': 'Airtable not configured'}), 503
    try:
        table = api.table(base_id, 'COMPASS Communications')
        fields = {
            'Date': data.get('date', datetime.now().strftime('%Y-%m-%d')),
            'Type': data.get('type', 'Email'),
            'Direction': data.get('direction', 'Outbound'),
            'Subject': data.get('subject', ''),
            'Summary': data.get('summary', ''),
            'Contact': data.get('contact', ''),
            'Follow Up Required': data.get('follow_up', False),
            'Follow Up Date': data.get('follow_up_date', ''),
        }
        if data.get('contract_id'):
            fields['Contract'] = [data['contract_id']]

        record = table.create(fields)
        return jsonify({'success': True, 'communication': {'id': record['id'], **fields}}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@compass.route('/compass/communications/<contract_id>', methods=['GET'])
def get_communications(contract_id):
    """Get all communications for a contract."""
    api, base_id = get_airtable()
    if not api or not base_id:
        return jsonify({'communications': []}), 200
    try:
        table = api.table(base_id, 'COMPASS Communications')
        records = table.all(formula=f"FIND('{contract_id}', ARRAYJOIN({{Contract}}, ','))")
        comms = []
        for r in records:
            f = r.get('fields', {})
            comms.append({
                'id': r['id'],
                'date': f.get('Date', ''),
                'type': f.get('Type', ''),
                'direction': f.get('Direction', ''),
                'subject': f.get('Subject', ''),
                'summary': f.get('Summary', ''),
                'contact': f.get('Contact', ''),
                'follow_up': f.get('Follow Up Required', False),
                'follow_up_date': f.get('Follow Up Date', ''),
            })
        comms.sort(key=lambda c: c.get('date', ''), reverse=True)
        return jsonify({'communications': comms})
    except Exception as e:
        return jsonify({'communications': [], 'error': str(e)}), 200


# ═══════════════════════════════════════════════════════════════════════════
# 4. CONTRACT MODIFICATIONS
# ═══════════════════════════════════════════════════════════════════════════

@compass.route('/compass/modifications', methods=['POST'])
def create_modification():
    """Log a contract modification."""
    data = request.json or {}
    api, base_id = get_airtable()
    if not api or not base_id:
        return jsonify({'error': 'Airtable not configured'}), 503
    try:
        table = api.table(base_id, 'COMPASS Modifications')
        fields = {
            'Mod Number': data.get('mod_number', ''),
            'Type': data.get('type', 'Administrative'),
            'Description': data.get('description', ''),
            'Value Change': data.get('value_change', 0),
            'Status': data.get('status', 'Pending'),
            'Date': data.get('date', datetime.now().strftime('%Y-%m-%d')),
        }
        if data.get('contract_id'):
            fields['Contract'] = [data['contract_id']]

        record = table.create(fields)

        # If mod changes value, update contract value
        if data.get('status') == 'Executed' and data.get('value_change', 0) != 0:
            try:
                contract_id = data['contract_id']
                c_table = api.table(base_id, 'COMPASS Contracts')
                contract = c_table.get(contract_id)
                new_value = (contract['fields'].get('Value', 0) or 0) + data['value_change']
                c_table.update(contract_id, {'Value': new_value})
            except Exception:
                pass

        advisor = None
        try:
            from nexus_advisor import advise
            advisor = advise('compass', 'modification_logged', {
                'type': data.get('type', ''),
                'value_change': data.get('value_change', 0),
            })
        except Exception:
            pass

        return jsonify({
            'success': True,
            'modification': {'id': record['id'], **fields},
            'advisor': advisor,
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ═══════════════════════════════════════════════════════════════════════════
# 5. PERFORMANCE & COMPLIANCE
# ═══════════════════════════════════════════════════════════════════════════

@compass.route('/compass/contracts/<contract_id>/health', methods=['GET'])
def get_contract_health(contract_id):
    """Calculate contract health score based on deliverables, compliance, payments."""
    api, base_id = get_airtable()
    if not api or not base_id:
        return jsonify({'error': 'Airtable not configured'}), 503
    try:
        c_table = api.table(base_id, 'COMPASS Contracts')
        contract = c_table.get(contract_id)
        f = contract.get('fields', {})

        total_del = f.get('Deliverables Total', 0) or 0
        complete_del = f.get('Deliverables Complete', 0) or 0
        invoiced = f.get('Invoiced Amount', 0) or 0
        paid = f.get('Paid Amount', 0) or 0
        value = f.get('Value', 0) or 1

        # Score components (0-100 each)
        delivery_score = round((complete_del / max(total_del, 1)) * 100)

        payment_score = 100
        if invoiced > 0:
            payment_score = round((paid / invoiced) * 100)

        burn_rate = round((invoiced / max(value, 1)) * 100)
        burn_score = 100 if burn_rate <= 80 else max(0, 100 - (burn_rate - 80) * 5)

        # Check overdue deliverables
        overdue_count = 0
        try:
            d_table = api.table(base_id, 'COMPASS Deliverables')
            deliverables = d_table.all(formula=f"FIND('{contract_id}', ARRAYJOIN({{Contract}}, ','))")
            today = datetime.now().strftime('%Y-%m-%d')
            for d in deliverables:
                df = d.get('fields', {})
                if df.get('Status') != 'Completed' and df.get('Due Date', '9999') < today:
                    overdue_count += 1
        except Exception:
            pass
        timeliness_score = max(0, 100 - (overdue_count * 20))

        composite = round((delivery_score * 0.35 + payment_score * 0.25 +
                           burn_score * 0.2 + timeliness_score * 0.2))

        if composite >= 85:
            status = 'Green'
            cpars_prediction = 'Satisfactory or above'
        elif composite >= 65:
            status = 'Yellow'
            cpars_prediction = 'Marginal — needs improvement before CPARS'
        else:
            status = 'Red'
            cpars_prediction = 'Unsatisfactory risk — immediate action required'

        # Update contract health
        c_table.update(contract_id, {
            'Health Score': composite,
            'Compliance Status': status,
        })

        return jsonify({
            'health_score': composite,
            'status': status,
            'components': {
                'delivery': {'score': delivery_score, 'weight': 35, 'detail': f'{complete_del}/{total_del} deliverables complete'},
                'payment': {'score': payment_score, 'weight': 25, 'detail': f'${paid:,.0f} of ${invoiced:,.0f} invoiced received'},
                'burn_rate': {'score': burn_score, 'weight': 20, 'detail': f'{burn_rate}% of contract value invoiced'},
                'timeliness': {'score': timeliness_score, 'weight': 20, 'detail': f'{overdue_count} overdue deliverables'},
            },
            'cpars_prediction': cpars_prediction,
            'overdue_deliverables': overdue_count,
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@compass.route('/compass/contracts/<contract_id>/performance-report', methods=['POST'])
def generate_performance_report(contract_id):
    """Generate a monthly performance report for the CO."""
    api, base_id = get_airtable()
    if not api or not base_id:
        return jsonify({'error': 'Airtable not configured'}), 503
    try:
        c_table = api.table(base_id, 'COMPASS Contracts')
        contract = c_table.get(contract_id)
        f = contract.get('fields', {})

        report_period = request.json.get('period', datetime.now().strftime('%B %Y'))

        deliverables_completed = []
        deliverables_upcoming = []
        try:
            d_table = api.table(base_id, 'COMPASS Deliverables')
            d_records = d_table.all(formula=f"FIND('{contract_id}', ARRAYJOIN({{Contract}}, ','))")
            for d in d_records:
                df = d.get('fields', {})
                item = {'title': df.get('Title', ''), 'due': df.get('Due Date', ''), 'status': df.get('Status', '')}
                if df.get('Status') == 'Completed':
                    deliverables_completed.append(item)
                else:
                    deliverables_upcoming.append(item)
        except Exception:
            pass

        report = {
            'contract_number': f.get('Contract Number', ''),
            'agency': f.get('Agency', ''),
            'report_period': report_period,
            'generated_date': datetime.now().isoformat(),
            'executive_summary': {
                'contract_value': f.get('Value', 0),
                'invoiced_to_date': f.get('Invoiced Amount', 0),
                'deliverables_total': f.get('Deliverables Total', 0),
                'deliverables_complete': f.get('Deliverables Complete', 0),
                'health_score': f.get('Health Score', 100),
                'compliance_status': f.get('Compliance Status', 'Green'),
            },
            'deliverables_completed_this_period': deliverables_completed[-5:],
            'deliverables_upcoming': deliverables_upcoming[:5],
            'issues': [],
            'next_period_plan': [],
        }

        # Set next report due
        next_month = datetime.now().replace(day=1) + timedelta(days=32)
        next_due = next_month.replace(day=5).strftime('%Y-%m-%d')
        c_table.update(contract_id, {'Next Report Due': next_due})

        try:
            from nexus_advisor import advise
            report['advisor'] = advise('compass', 'report_generated', {
                'agency': f.get('Agency', ''),
            })
        except Exception:
            pass

        return jsonify({'success': True, 'report': report})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ═══════════════════════════════════════════════════════════════════════════
# 6. DASHBOARD STATS
# ═══════════════════════════════════════════════════════════════════════════

@compass.route('/compass/stats', methods=['GET'])
def compass_stats():
    """Dashboard statistics for COMPASS."""
    api, base_id = get_airtable()
    if not api or not base_id:
        return jsonify({
            'active_contracts': 0, 'total_value': 0,
            'deliverables_pending': 0, 'overdue': 0,
            'health_avg': 0, 'invoiced': 0, 'paid': 0,
        })
    try:
        table = api.table(base_id, 'COMPASS Contracts')
        records = table.all()

        active = [r for r in records if r['fields'].get('Status') == 'Active']
        total_value = sum(r['fields'].get('Value', 0) or 0 for r in active)
        total_invoiced = sum(r['fields'].get('Invoiced Amount', 0) or 0 for r in active)
        total_paid = sum(r['fields'].get('Paid Amount', 0) or 0 for r in active)
        total_del = sum(r['fields'].get('Deliverables Total', 0) or 0 for r in active)
        complete_del = sum(r['fields'].get('Deliverables Complete', 0) or 0 for r in active)
        health_scores = [r['fields'].get('Health Score', 100) for r in active if r['fields'].get('Health Score')]
        avg_health = round(sum(health_scores) / max(len(health_scores), 1))

        return jsonify({
            'active_contracts': len(active),
            'total_contracts': len(records),
            'total_value': total_value,
            'invoiced': total_invoiced,
            'paid': total_paid,
            'outstanding': total_invoiced - total_paid,
            'deliverables_total': total_del,
            'deliverables_complete': complete_del,
            'deliverables_pending': total_del - complete_del,
            'health_avg': avg_health,
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
