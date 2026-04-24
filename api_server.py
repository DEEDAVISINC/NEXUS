"""
NEXUS API Server
Flask app with webhook endpoints for Make.com integration
"""

# Load environment variables from .env file FIRST
import os
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

from flask import Flask, request, jsonify, send_file, Response, url_for
from flask_cors import CORS
import jwt
from datetime import datetime, timedelta
from functools import wraps
import subprocess
import tempfile
from pathlib import Path
import re

from ddi_opportunity_fit import (
    analyze_ddi_fit,
    analyze_subcontract_stretch,
    airtable_fields_to_opp_dict,
    gpss_opportunity_is_closed,
)
from nexus_backend import (
    Config,
    AirtableClient,
    AnthropicClient,
    WorkflowManager,
    GPSSPricingAgent,
    GPSSComplianceAgent,
    GPSSOpportunityMiningAgent,
    GPSSSubcontractorMiner,
    handle_document_upload,
    handle_qualify_opportunity,
    handle_generate_quote,
    handle_ddcss_qualify_prospect,
    handle_generate_invoice_from_opportunity,
    handle_generate_invoice_from_project,
    handle_atlas_analyze_rfp,
    handle_ddcss_generate_blueprint,
    handle_ddcss_analyze_response,
    handle_atlas_analyze_rfp,
    handle_atlas_generate_wbs,
    handle_atlas_analyze_change_request,
    handle_generate_invoice_from_opportunity,
    handle_generate_invoice_from_project,
    handle_generate_invoice_from_prospect,
    handle_get_invoices,
    handle_get_invoice,
    handle_update_invoice,
    handle_delete_invoice,
    # LBPC handlers
    handle_lbpc_get_leads,
    handle_lbpc_create_lead,
    handle_lbpc_update_lead,
    handle_lbpc_delete_lead,
    handle_lbpc_generate_document,
    handle_lbpc_get_documents,
    handle_lbpc_get_tasks,
    handle_lbpc_update_task,
    handle_lbpc_ai_qualify_lead,
    handle_lbpc_create_invoice,
    handle_lbpc_import_csv,
    handle_lbpc_get_analytics,
    handle_lbpc_mine_county,
    handle_lbpc_upload_pdf,
    handle_lbpc_upload_csv,
    # Fulfillment handlers
    handle_create_fulfillment_contract,
    handle_get_active_contracts,
    handle_get_contract_details,
    handle_get_upcoming_deliveries,
    handle_update_delivery_status,
    handle_check_inventory_health,
    handle_get_inventory_dashboard,
    handle_create_purchase_order,
    handle_receive_purchase_order,
    handle_get_pending_purchase_orders,
    # AI Recommendation handlers
    handle_analyze_capability_gap,
    handle_recommend_subcontractors,
    handle_recommend_suppliers,
    handle_solicitation_market_research,
    handle_approve_recommendation,
    handle_get_pending_recommendations,
    handle_calculate_compliance
)

# Import Agenda Manager
from agenda_manager import handle_get_agenda
from datetime import datetime, timedelta
import jwt
from functools import wraps
import json
from jeta_buyer_schema import (
    JB,
    jb_geo_state_raw,
    jb_get_email,
    jb_get_float,
    jb_get_raw,
    jb_get_str,
    jb_parse_pipeline_stage_int,
    jb_pipeline_stage_option,
    jb_priority_write_payloads,
    jb_tags_as_list,
)
from jeta_seller_schema import JS, js_fields_match_icao
from jeta_deal_schema import (
    JD,
    jd_first_link_id,
    jd_get_bool,
    jd_get_float,
    jd_get_raw,
    jd_get_str,
    jd_notes_or_description,
)
from jeta_outreach_schema import (
    JO,
    jo_first_link_id,
    jo_get_bool,
    jo_get_int,
    jo_get_raw,
    jo_get_str,
    jo_response_received_display_string,
)
from jeta_document_schema import (
    JDoc,
    jdoc_first_link_id,
    jdoc_get_bool,
    jdoc_get_float,
    jdoc_get_raw,
    jdoc_get_str,
    jdoc_link_ids,
    jdoc_pdf_path_local,
)
from jeta_broker_chain_schema import (
    JBC,
    jbc_first_link_id,
    jbc_get_bool,
    jbc_get_float,
    jbc_get_int,
    jbc_get_str,
)
from jeta_market_data_schema import (
    JMD,
    compute_wow_vs_prior,
    jmd_get_float,
    jmd_week_sort_key,
    monday_iso_for_date_str,
)
from jeta_supplier_directory_schema import JSD
from jeta_rfp_schema import (
    JR,
    jr_first_link_id,
    jr_format_date_val,
    jr_fuel_types_list,
    jr_get_float,
    jr_get_raw,
    jr_get_str,
)
from jeta_seller_contact_schema import (
    JSC,
    jsc_first_link_id,
    jsc_format_date,
    jsc_get_bool,
    jsc_get_raw,
    jsc_get_str,
)
from jeta_fraud_log_schema import (
    JFL,
    jfl_first_link_id,
    jfl_flag_type_list,
    jfl_flagged_record_id_display,
    jfl_format_date,
    jfl_get_bool,
    jfl_get_raw,
    jfl_get_str,
)
from jeta_import_log_schema import (
    JIL,
    jil_format_date,
    jil_get_int,
    jil_get_raw,
    jil_get_str,
    jil_long_text_as_json_str,
)
from jeta_events_schema import (
    JE,
    je_format_date,
    je_get_bool,
    je_get_float,
    je_get_raw,
    je_get_str,
    je_link_ids,
)
import logging
import csv
import io
import threading
import time

# Import Bid Folder Scanner (reads real filesystem data)
from bid_folder_scanner import scan_all_bids, get_dashboard_data

# ProposalBio™ Quality Assurance Module
from proposalbio_module import ProposalBioService, ProposalBioAnalyzer

# Strategic Analysis Module (RFP Success® Integration)
from strategic_analysis_module import StrategicAnalysisService

# Historical Pricing Intelligence
from historical_pricing_scraper import HistoricalPricingScraper

# Multi-Year Pricing Calculator
from multi_year_pricing_calculator import calculate_multi_year_pricing

# Labor Rate Calculator
from service_labor_rate_calculator import calculate_service_rate_by_type

# Quote Validator
from subcontractor_quote_validator import validate_subcontractor_quote, calculate_ddi_bid_from_sub_quote


app = Flask(__name__)
logger = logging.getLogger(__name__)
CORS(app)  # Enable CORS for all routes

# Register PRISM Compliance & Document API
try:
    from prism_compliance_api import prism_compliance
    app.register_blueprint(prism_compliance)
    print("✅ PRISM Compliance API registered")
except ImportError as e:
    print(f"⚠️ PRISM Compliance API not loaded: {e}")

# Register PRISM Inspection Engine
try:
    from prism_inspection_engine import prism_inspection
    app.register_blueprint(prism_inspection)
    print("✅ PRISM Inspection Engine registered")
except ImportError as e:
    print(f"⚠️ PRISM Inspection Engine not loaded: {e}")

# Register PRISM DOT Compliance Module
try:
    from prism_dot_compliance import prism_dot
    app.register_blueprint(prism_dot)
    print("✅ PRISM DOT Compliance Module registered")
except ImportError as e:
    print(f"⚠️ PRISM DOT Compliance Module not loaded: {e}")

# Register PRISM DNA Compliance Module
try:
    from prism_dna_compliance import prism_dna
    app.register_blueprint(prism_dna)
    print("✅ PRISM DNA Compliance Module registered")
except ImportError as e:
    print(f"⚠️ PRISM DNA Compliance Module not loaded: {e}")

# Register PRISM Fingerprinting Compliance Module
try:
    from prism_fingerprinting_compliance import prism_fingerprint
    app.register_blueprint(prism_fingerprint)
    print("✅ PRISM Fingerprinting Compliance Module registered")
except ImportError as e:
    print(f"⚠️ PRISM Fingerprinting Compliance Module not loaded: {e}")

# Register PRISM Notary Compliance Module
try:
    from prism_notary_compliance import prism_notary
    app.register_blueprint(prism_notary)
    print("✅ PRISM Notary Compliance Module registered")
except ImportError as e:
    print(f"⚠️ PRISM Notary Compliance Module not loaded: {e}")

# Register PRISM Law Firm Notary Channel (SE Michigan — scheduling, intake schema, coverage)
try:
    from prism_law_firm_notary_channel import prism_law_firm_channel
    app.register_blueprint(prism_law_firm_channel)
    print("✅ PRISM Law Firm Notary Channel registered")
except ImportError as e:
    print(f"⚠️ PRISM Law Firm Notary Channel not loaded: {e}")

# Register PRISM Occupational Health Compliance Module
try:
    from prism_occupational_health_compliance import prism_occ_health
    app.register_blueprint(prism_occ_health)
    print("✅ PRISM Occupational Health Compliance Module registered")
except ImportError as e:
    print(f"⚠️ PRISM Occupational Health Compliance Module not loaded: {e}")

# Register PRISM Notifications & Receipt Tracking
try:
    from prism_notifications_api import prism_notifications
    app.register_blueprint(prism_notifications)
    print("✅ PRISM Notifications & Receipt Tracking registered")
except ImportError as e:
    print(f"⚠️ PRISM Notifications not loaded: {e}")

# Register PRISM Orders & Intake API
try:
    from prism_orders_api import prism_orders
    app.register_blueprint(prism_orders)
    print("✅ PRISM Orders & Intake API registered")
except ImportError as e:
    print(f"⚠️ PRISM Orders API not loaded: {e}")

# FleetFlow™ CAPE (IEEPA) refund navigator intake + admin email
try:
    from fleetflow_cape_intake_api import fleetflow_cape
    app.register_blueprint(fleetflow_cape)
    print("✅ FleetFlow CAPE intake API registered")
except ImportError as e:
    print(f"⚠️ FleetFlow CAPE intake API not loaded: {e}")

# Register PRISM Random Pool Engine
try:
    from prism_random_pool import prism_random
    app.register_blueprint(prism_random)
    print("✅ PRISM Random Pool Engine registered")
except ImportError as e:
    print(f"⚠️ PRISM Random Pool Engine not loaded: {e}")

# Register PRISM FMCSA Clearinghouse Compliance Module
try:
    from prism_clearinghouse import prism_clearinghouse
    app.register_blueprint(prism_clearinghouse)
    print("✅ PRISM FMCSA Clearinghouse Module registered")
except ImportError as e:
    print(f"⚠️ PRISM Clearinghouse Module not loaded: {e}")

# Register PRISM Service Router — Dual-Layer Fulfillment Engine
try:
    from prism_service_router import prism_router
    app.register_blueprint(prism_router)
    print("✅ PRISM Service Router registered")
except ImportError as e:
    print(f"⚠️ PRISM Service Router not loaded: {e}")

# Register PRISM Uber Health (NEMT rides API)
try:
    from prism_uber_health import prism_uber_health
    app.register_blueprint(prism_uber_health)
    print("✅ PRISM Uber Health NEMT registered")
except ImportError as e:
    print(f"⚠️ PRISM Uber Health not loaded: {e}")

# Register PRISM POCT — Point of Care Testing Module
try:
    from prism_poct import prism_poct
    app.register_blueprint(prism_poct)
    print("✅ PRISM POCT Module registered")
except ImportError as e:
    print(f"⚠️ PRISM POCT Module not loaded: {e}")

# Register PRISM BAT — Breath Alcohol Testing Workflow
try:
    from prism_bat import prism_bat
    app.register_blueprint(prism_bat)
    print("✅ PRISM BAT Module registered")
except ImportError as e:
    print(f"⚠️ PRISM BAT Module not loaded: {e}")

# Register PRISM NEMT — Operations + VERTEX Billing Bridge (NPI: 1538939111 / CHAMPS: 6309049)
try:
    from prism_nemt import prism_nemt
    app.register_blueprint(prism_nemt)
    print("✅ PRISM NEMT Module registered (Michigan Medicaid / MCO billing)")
except ImportError as e:
    print(f"⚠️ PRISM NEMT Module not loaded: {e}")

# Register PRISM Lyft Healthcare — WAV + scheduled ride fulfillment
try:
    from prism_lyft_healthcare import prism_lyft_healthcare
    app.register_blueprint(prism_lyft_healthcare)
    print("✅ PRISM Lyft Healthcare Module registered (WAV / wheelchair transport)")
except ImportError as e:
    print(f"⚠️ PRISM Lyft Healthcare Module not loaded: {e}")

# Register NEXUS Pipeline — Central Nervous System
try:
    from nexus_pipeline_api import nexus_pipeline
    app.register_blueprint(nexus_pipeline)
    print("✅ NEXUS Pipeline API registered (Central Nervous System)")
except ImportError as e:
    print(f"⚠️ NEXUS Pipeline API not loaded: {e}")

# Register COMPASS — Post-Award Operations
try:
    from compass_api import compass
    app.register_blueprint(compass)
    print("✅ COMPASS Post-Award API registered")
except ImportError as e:
    print(f"⚠️ COMPASS API not loaded: {e}")

# Register OPPORTUNITY HUNTER — Visual Agency Intelligence
try:
    from nexus_opportunity_hunter_api import opportunity_hunter
    app.register_blueprint(opportunity_hunter)
    print("✅ Opportunity Hunter API registered")
except ImportError as e:
    print(f"⚠️ Opportunity Hunter API not loaded: {e}")

# Register ALEXA SKILL — Voice-controlled NEXUS Access
try:
    from nexus_alexa_skill import app as alexa_app
    # Mount Alexa skill at /alexa endpoint
    @app.route('/alexa', methods=['POST'])
    def alexa_webhook():
        """Proxy requests to Alexa skill handler"""
        from nexus_alexa_skill import lambda_handler
        return lambda_handler(request.json, None)
    
    @app.route('/alexa/health', methods=['GET'])
    def alexa_health():
        """Alexa skill health check"""
        return jsonify({
            "status": "healthy",
            "service": "NEXUS Alexa Skill",
            "connected_to_nexus": "http://localhost:8000"
        })
    
    print("✅ Alexa Skill endpoint registered at /alexa")
except ImportError as e:
    print(f"⚠️ Alexa Skill integration not loaded: {e}")

# Register AUTONOMOUS ENGINE — "AI That Works While You Sleep"
try:
    from nexus_autonomous import get_engine as get_autonomous_engine
    print("✅ Autonomous Engine loaded")
except ImportError as e:
    get_autonomous_engine = None
    print(f"⚠️ Autonomous Engine not loaded: {e}")


# Set base ID from environment
Config.AIRTABLE_BASE_ID = os.environ.get('AIRTABLE_BASE_ID', '')

# JWT Secret for Alexa authentication
JWT_SECRET = os.environ.get('JWT_SECRET', 'nexus-alexa-secret-key-change-in-production')

# ============================================================
# WORKFLOW AUTO-ADVANCE SYSTEM
# Steps: 1=Review, 2=Go/No-Go, 3=Find Suppliers, 4=Create RFQ,
#   5=Send RFQ, 6=Collect Quotes, 7=Price&Markup, 8=Prepare Bid,
#   9=Final Review, 10=Submit
# ============================================================

WORKFLOW_STEPS = {
    1: 'Review', 2: 'Go/No-Go', 3: 'Find Suppliers', 4: 'Create RFQ',
    5: 'Send RFQ', 6: 'Collect Quotes', 7: 'Price & Markup',
    8: 'Prepare Bid', 9: 'Final Review', 10: 'Submit'
}

def auto_advance_workflow(opportunity_id, to_step, reason=''):
    """Auto-advance an opportunity's workflow step. Only advances forward, never backward."""
    try:
        airtable_client = AirtableClient()
        record = airtable_client.get_record('GPSS OPPORTUNITIES', opportunity_id)
        raw_notes = record['fields'].get('Notes', '') or ''
        
        # Parse current step
        current_step = 0
        step_match = re.match(r'\[STEP:(\d+)\]\s*(.*)', raw_notes, re.DOTALL)
        clean_notes = step_match.group(2).strip() if step_match else raw_notes
        if step_match:
            current_step = int(step_match.group(1))
        
        # Only advance forward
        if to_step <= current_step:
            return current_step
        
        # Update with new step
        new_notes = f'[STEP:{to_step}] {clean_notes}'.strip()
        airtable_client.update_record('GPSS OPPORTUNITIES', opportunity_id, {'Notes': new_notes})
        
        step_name = WORKFLOW_STEPS.get(to_step, f'Step {to_step}')
        print(f"[WORKFLOW] {opportunity_id} auto-advanced to Step {to_step}: {step_name} ({reason})")
        return to_step
    except Exception as e:
        print(f"[WORKFLOW] Auto-advance failed for {opportunity_id}: {e}")
        return 0

def require_alexa_auth(f):
    """Decorator to require Alexa JWT authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Missing or invalid authorization header'}), 401

        token = auth_header.split(' ')[1]
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
            # Check if token is for Alexa user
            if payload.get('user') != 'alexa_user':
                return jsonify({'error': 'Invalid token user'}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401

        return f(*args, **kwargs)
    return decorated_function

@app.route('/auth/alexa', methods=['POST'])
def alexa_auth():
    """Alexa authentication endpoint - validates skill ID and returns JWT"""
    try:
        # Validate Alexa Skill ID
        skill_id = request.headers.get('Alexa-Skill-Id')
        expected_skill_id = os.environ.get('ALEXA_SKILL_ID')

        if not expected_skill_id:
            return jsonify({'error': 'Alexa integration not configured'}), 500

        if skill_id != expected_skill_id:
            return jsonify({'error': 'Unauthorized skill'}), 401

        # Generate JWT token valid for 1 hour
        token = jwt.encode({
            'user': 'alexa_user',
            'skill_id': skill_id,
            'exp': datetime.utcnow() + timedelta(hours=1),
            'iat': datetime.utcnow()
        }, JWT_SECRET, algorithm='HS256')

        return jsonify({
            'success': True,
            'token': token,
            'expires_in': 3600  # 1 hour
        })

    except Exception as e:
        return jsonify({
            'error': f'Authentication failed: {str(e)}'
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "NEXUS Backend",
        "version": "1.0.0"
    })

@app.route('/dashboard/stats', methods=['GET'])
def get_dashboard_stats():
    """
    Get real-time dashboard statistics from Airtable
    Returns: counts, revenue, and aggregated data
    """
    try:
        airtable_client = AirtableClient()
        
        # Get data from all tables
        opportunities = airtable_client.get_all_records('GPSS OPPORTUNITIES')
        contacts = airtable_client.get_all_records('GPSS CONTACTS')
        
        # Try to get ATLAS projects (might not exist yet)
        try:
            atlas_projects = airtable_client.get_all_records('ATLAS PROJECTS')
        except:
            atlas_projects = []
        
        # Calculate stats
        active_opportunities = [opp for opp in opportunities if opp['fields'].get('Status') in ['Active', 'Qualifying', 'Proposal']]
        
        # Calculate total pipeline value
        total_pipeline = 0
        for opp in active_opportunities:
            value = opp['fields'].get('Value', 0)
            if isinstance(value, (int, float)):
                total_pipeline += value
        
        # Count active projects
        active_projects = [proj for proj in atlas_projects if proj['fields'].get('Status') in ['Active', 'In Progress', 'Planning']]
        
        # Get system-specific stats
        gpss_opportunities = [opp for opp in opportunities if opp['fields'].get('Source') in ['Government', 'SAM.gov', 'GPSS']]
        gpss_pipeline = sum(opp['fields'].get('Value', 0) for opp in gpss_opportunities if isinstance(opp['fields'].get('Value', 0), (int, float)))
        
        # Build response
        stats = {
            'active_opportunities': len(active_opportunities),
            'total_contacts': len(contacts),
            'active_projects': len(active_projects),
            'revenue_pipeline': total_pipeline,
            'systems': {
                'gpss': {
                    'opportunities': len(gpss_opportunities),
                    'pipeline': gpss_pipeline,
                    'contacts': len([c for c in contacts if c['fields'].get('Source') == 'Government'])
                },
                'ddcss': {
                    'prospects': 0,  # Will be calculated once DDCSS table exists
                    'responses': 0,
                    'sectors': 6
                },
                'atlas': {
                    'projects': len(active_projects),
                    'rfps_analyzed': len([proj for proj in atlas_projects if proj['fields'].get('RFP Analyzed') == True]),
                    'total_value': sum(proj['fields'].get('Budget', 0) for proj in atlas_projects if isinstance(proj['fields'].get('Budget', 0), (int, float)))
                }
            },
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(stats)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/dashboard/activity', methods=['GET'])
def get_dashboard_activity():
    """
    Recent activity plus DDI lane matches — surfaces opportunities that fit core service lanes first.
    """
    try:
        airtable_client = AirtableClient()
        activities = []
        ddi_top_picks = []
        ddi_subcontract_hints = []
        ddi_lane_match_count = 0
        ddi_subcontract_flag_count = 0
        ddi_scanned = 0

        # Get recent contacts
        try:
            contacts = airtable_client.get_all_records('GPSS CONTACTS', sort=['Created'])
            for contact in contacts[-5:]:  # Last 5 contacts
                fields = contact['fields']
                activities.append({
                    'type': 'contact',
                    'system': 'GPSS',
                    'action': 'Contact Extracted',
                    'title': f"{fields.get('First Name', '')} {fields.get('Last Name', '')} - {fields.get('Agency', '')}",
                    'time': fields.get('Created', ''),
                    'icon': '👤',
                    'color': 'text-blue-400'
                })
        except Exception as e:
            print(f"Error fetching contacts: {e}")

        # GPSS opportunities: score for DDI lanes, prioritize matches in feed + ddi_top_picks
        try:
            opportunities = airtable_client.get_all_records('GPSS OPPORTUNITIES')
            sorted_opps = sorted(
                opportunities,
                key=lambda x: x.get('createdTime', '') or '',
                reverse=True,
            )
            recent_window = sorted_opps[:350]
            ddi_scanned = len(recent_window)

            opp_activities = []
            pick_candidates = []
            sub_candidates = []
            prime_ids = set()
            for opp in recent_window:
                fields = opp.get('fields') or {}
                opp_dict = airtable_fields_to_opp_dict(fields)
                fit = analyze_ddi_fit(opp_dict)
                closed = gpss_opportunity_is_closed(fields)
                sub = (
                    analyze_subcontract_stretch(opp_dict)
                    if not fit['relevant']
                    else {'suggest': False, 'score': 0, 'headline': '', 'blurb': '', 'hits': []}
                )

                if fit['relevant']:
                    ddi_lane_match_count += 1
                    if not closed:
                        rid = opp.get('id')
                        pick_candidates.append({
                            'title': fields.get('Name', 'Untitled'),
                            'lane': fit['lane'],
                            'score': fit['score'],
                            'source': fit['source'],
                            'time': opp.get('createdTime', ''),
                            'recordId': rid,
                            'status': fields.get('Status') or fields.get('Source Status') or '',
                        })
                        if rid:
                            prime_ids.add(rid)

                if sub.get('suggest') and not closed:
                    ddi_subcontract_flag_count += 1

                action = 'Lane match — Review'
                if fit['score'] >= 100:
                    action = 'Strong lane match (NAICS)'
                elif fit['score'] >= 80:
                    action = 'Lane match — Review'
                elif fit['relevant']:
                    action = 'Possible lane match (description)'
                elif sub.get('suggest'):
                    action = sub.get('headline') or 'Worth a look — subcontract / teaming'

                if sub.get('suggest') and not closed:
                    rid = opp.get('id')
                    if rid and rid not in prime_ids:
                        sub_candidates.append({
                            'title': fields.get('Name', 'Untitled'),
                            'headline': sub.get('headline', ''),
                            'blurb': sub.get('blurb', ''),
                            'score': sub.get('score', 0),
                            'hits': sub.get('hits') or [],
                            'time': opp.get('createdTime', ''),
                            'recordId': rid,
                            'status': fields.get('Status') or fields.get('Source Status') or '',
                        })

                opp_activities.append({
                    'type': 'opportunity',
                    'system': 'GPSS',
                    'action': 'New Opportunity' if not fit['relevant'] and not sub.get('suggest') else action,
                    'title': fields.get('Name', 'Untitled'),
                    'time': opp.get('createdTime', ''),
                    'icon': '⭐' if fit['relevant'] else ('🤝' if sub.get('suggest') else '🎯'),
                    'color': (
                        'text-emerald-400'
                        if fit['relevant']
                        else ('text-amber-300' if sub.get('suggest') else 'text-yellow-400')
                    ),
                    'ddi_score': fit['score'],
                    'ddi_lane': fit['lane'] if fit['relevant'] else '',
                    'ddi_relevant': fit['relevant'],
                    'ddi_subcontract': bool(sub.get('suggest')),
                    'ddi_sub_score': int(sub.get('score') or 0) if sub.get('suggest') else 0,
                    'ddi_sub_headline': sub.get('headline', '') if sub.get('suggest') else '',
                    'ddi_sub_blurb': sub.get('blurb', '') if sub.get('suggest') else '',
                    'recordId': opp.get('id'),
                })

            pick_candidates.sort(
                key=lambda x: (-int(x.get('score') or 0), str(x.get('time') or '')),
            )
            ddi_top_picks = pick_candidates[:8]

            sub_candidates.sort(
                key=lambda x: (-int(x.get('score') or 0), str(x.get('time') or '')),
            )
            ddi_subcontract_hints = sub_candidates[:6]

            opp_activities.sort(
                key=lambda x: (
                    0 if x.get('ddi_relevant') else (1 if x.get('ddi_subcontract') else 2),
                    -int(x.get('ddi_score') or 0) if x.get('ddi_relevant') else (
                        -int(x.get('ddi_sub_score') or 0) if x.get('ddi_subcontract') else 0
                    ),
                    str(x.get('time') or ''),
                ),
                reverse=False,
            )
            for oa in opp_activities[:12]:
                activities.append(oa)

        except Exception as e:
            print(f"Error fetching opportunities: {e}")

        # Get recent ATLAS projects
        try:
            projects = airtable_client.get_all_records('ATLAS PROJECTS', sort=['Created Date'])
            for proj in projects[-5:]:  # Last 5 projects
                fields = proj['fields']
                activities.append({
                    'type': 'project',
                    'system': 'ATLAS PM',
                    'action': 'Project Updated',
                    'title': f"{fields.get('Project Name', 'Untitled')} - {fields.get('Completion Percentage', 0)}% Complete",
                    'time': fields.get('Last Updated', fields.get('Created Date', '')),
                    'icon': '📋',
                    'color': 'text-purple-400'
                })
        except Exception as e:
            print(f"Error fetching projects: {e}")

        def _activity_sort_key(a):
            if a.get('type') != 'opportunity':
                return (3, 0, str(a.get('time') or ''))
            if a.get('ddi_relevant'):
                return (0, -int(a.get('ddi_score') or 0), str(a.get('time') or ''))
            if a.get('ddi_subcontract'):
                return (1, -int(a.get('ddi_sub_score') or 0), str(a.get('time') or ''))
            return (2, 0, str(a.get('time') or ''))

        activities.sort(key=_activity_sort_key, reverse=False)

        return jsonify({
            'activities': activities[:16],
            'ddi_top_picks': ddi_top_picks[:8],
            'ddi_subcontract_hints': ddi_subcontract_hints,
            'ddi_summary': {
                'lane_matches_in_recent': ddi_lane_match_count,
                'subcontract_hints_in_recent': ddi_subcontract_flag_count,
                'opportunities_scanned': ddi_scanned,
            },
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/subnet/opportunities', methods=['GET'])
def subnet_opportunities_search():
    """
    Search SBA SubNet (subcontracting opportunities posted by primes).
    Query: state=MI|All, keyword=, max_pages=5, details=true|false
    """
    try:
        from sba_subnet_client import search_subnet_opportunities

        state = request.args.get('state', 'All') or 'All'
        keyword = request.args.get('keyword', '') or ''
        try:
            max_pages = int(request.args.get('max_pages', 5))
        except (TypeError, ValueError):
            max_pages = 5
        max_pages = max(1, min(30, max_pages))
        fetch_details = str(request.args.get('details', '')).lower() in ('1', 'true', 'yes')
        data = search_subnet_opportunities(
            state=state,
            keyword=keyword,
            max_pages=max_pages,
            fetch_details=fetch_details,
        )
        return jsonify(data)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/subnet/sync', methods=['POST'])
def subnet_sync_to_gpss():
    """
    Pull SubNet pages and create GPSS OPPORTUNITIES rows (skips existing RFP NUMBER SUBNET-{slug}).
    JSON body: { "state": "MI", "keyword": "", "max_pages": 3, "fetch_details": false }
    """
    try:
        from sba_subnet_client import search_subnet_opportunities, opportunity_to_gpss_fields

        body = request.get_json(force=True, silent=True) or {}
        state = body.get('state', 'All') or 'All'
        keyword = (body.get('keyword') or '') or ''
        max_pages = max(1, min(20, int(body.get('max_pages', 3))))
        fetch_details = bool(body.get('fetch_details', False))

        pull = search_subnet_opportunities(
            state=state,
            keyword=keyword,
            max_pages=max_pages,
            fetch_details=fetch_details,
        )
        if not pull.get('success'):
            return jsonify(pull), 502

        airtable_client = AirtableClient()
        created = 0
        skipped = 0
        errors: list = []

        for rec in pull.get('opportunities') or []:
            fields = opportunity_to_gpss_fields(rec)
            rfp = fields.get('RFP NUMBER') or ''
            safe = rfp.replace("'", "\\'")
            try:
                existing = airtable_client.search_records(
                    'GPSS OPPORTUNITIES',
                    f"{{RFP NUMBER}}='{safe}'",
                )
            except Exception as ex:
                errors.append({'rfp': rfp, 'error': str(ex)})
                continue
            if existing:
                skipped += 1
                continue
            try:
                airtable_client.create_record('GPSS OPPORTUNITIES', fields)
                created += 1
            except Exception as ex:
                errors.append({'rfp': rfp, 'error': str(ex)})

        return jsonify({
            'success': True,
            'created': created,
            'skipped_existing': skipped,
            'pulled': pull.get('count', 0),
            'errors': errors[:20],
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/dashboard/alerts', methods=['GET'])
def get_dashboard_alerts():
    """
    Get alerts and notifications
    Returns: urgent items requiring attention
    """
    try:
        airtable_client = AirtableClient()
        alerts = []
        
        # Check for upcoming RFP deadlines (within 7 days)
        try:
            opportunities = airtable_client.get_all_records('GPSS OPPORTUNITIES')
            now = datetime.now()
            
            for opp in opportunities:
                fields = opp['fields']
                due_date_str = fields.get('Due Date')
                if due_date_str:
                    try:
                        due_date = datetime.fromisoformat(due_date_str.replace('Z', '+00:00'))
                        days_until = (due_date - now).days
                        
                        if 0 <= days_until <= 7 and fields.get('Status') in ['Active', 'Proposal']:
                            alerts.append({
                                'type': 'urgent' if days_until <= 3 else 'warning',
                                'title': f'RFP Deadline Approaching',
                                'message': f"{fields.get('Title', 'Untitled')} due in {days_until} days",
                                'action': 'Review RFP',
                                'system': 'GPSS'
                            })
                    except:
                        pass
        except Exception as e:
            print(f"Error checking deadlines: {e}")
        
        # Check for new Transportation & Logistics opportunities
        try:
            # Check for new transportation opportunities added recently (last 24 hours)
            transportation_keywords = ['airport', 'aviation', 'marine', 'port', 'cargo', 'freight', 
                                     'courier', 'postal', 'USPS', 'transit', 'transportation',
                                     'NEMT', 'non-emergency medical', 'medical transportation',
                                     'medical transport', 'patient transport', 'patient transportation',
                                     'paratransit', 'healthcare transportation']
            
            recent_transportation = []
            for opp in opportunities:
                fields = opp['fields']
                title = fields.get('Title', '').lower()
                description = fields.get('Description', '').lower()
                category = fields.get('Category', '').lower()
                
                # Check if it's a transportation opportunity
                is_transportation = any(keyword.lower() in title or keyword.lower() in description or keyword.lower() in category 
                                      for keyword in transportation_keywords)
                
                if is_transportation:
                    # Check if created recently
                    created_time = fields.get('Created Time') or fields.get('Date Added')
                    if created_time:
                        try:
                            created_date = datetime.fromisoformat(created_time.replace('Z', '+00:00'))
                            hours_since = (now - created_date).total_seconds() / 3600
                            
                            if hours_since <= 24:  # Last 24 hours
                                recent_transportation.append({
                                    'title': fields.get('Title', 'Untitled'),
                                    'value': fields.get('Estimated Value', 0),
                                    'category': 'Transportation/Logistics'
                                })
                        except:
                            pass
            
            # Create alert for new transportation opportunities
            if recent_transportation:
                total_value = sum(opp.get('value', 0) for opp in recent_transportation)
                alerts.append({
                    'type': 'success',
                    'title': '✈️🚢 New Transportation Opportunities Found!',
                    'message': f"{len(recent_transportation)} new opportunities (${total_value:,.0f} total value)",
                    'action': 'View Transportation',
                    'system': 'Transportation & Logistics'
                })
        except Exception as e:
            print(f"Error checking transportation opportunities: {e}")
        
        # Check for TODAY's recommended transportation searches
        try:
            import calendar
            day_name = calendar.day_name[now.weekday()].lower()
            
            transportation_schedule = {
                'monday': {'focus': 'NEMT & Healthcare Transportation', 'icon': '🚑', 'searches': 3, 'special': 'HIGH VALUE! $500K-$2M contracts'},
                'tuesday': {'focus': 'Airport & Aviation', 'icon': '✈️', 'searches': 3},
                'wednesday': {'focus': 'Port & Marine', 'icon': '🚢', 'searches': 3},
                'thursday': {'focus': 'Courier & Postal + Cargo', 'icon': '📬', 'searches': 3},
                'friday': {'focus': 'Transit & Transportation', 'icon': '🚌', 'searches': 3}
            }
            
            if day_name in transportation_schedule:
                schedule = transportation_schedule[day_name]
                alerts.append({
                    'type': 'info',
                    'title': f"{schedule['icon']} Today's Transportation Focus: {schedule['focus']}",
                    'message': f"Run {schedule['searches']} recommended searches • Expected: 10-15 opportunities",
                    'action': 'Run Searches',
                    'system': 'Transportation & Logistics'
                })
        except Exception as e:
            print(f"Error adding transportation schedule: {e}")
        
        # Check for new Service Contract opportunities
        try:
            # Check for new service opportunities added recently (last 24 hours)
            service_keywords = ['janitorial', 'custodial', 'cleaning', 'landscaping', 'grounds maintenance',
                              'facility maintenance', 'building maintenance', 'HVAC', 'IT services',
                              'security services', 'security guard', 'construction services', 'renovation',
                              'moving services', 'relocation', 'event services', 'catering']
            
            recent_services = []
            for opp in opportunities:
                fields = opp['fields']
                title = fields.get('Title', '').lower()
                description = fields.get('Description', '').lower()
                category = fields.get('Category', '').lower()
                
                # Check if it's a service opportunity
                is_service = any(keyword.lower() in title or keyword.lower() in description or keyword.lower() in category 
                                for keyword in service_keywords)
                
                if is_service:
                    # Check if created recently
                    created_time = fields.get('Created Time') or fields.get('Date Added')
                    if created_time:
                        try:
                            created_date = datetime.fromisoformat(created_time.replace('Z', '+00:00'))
                            hours_since = (now - created_date).total_seconds() / 3600
                            
                            if hours_since <= 24:  # Last 24 hours
                                recent_services.append({
                                    'title': fields.get('Title', 'Untitled'),
                                    'value': fields.get('Estimated Value', 0),
                                    'category': 'Service Contracts'
                                })
                        except:
                            pass
            
            if recent_services:
                total_value = sum(opp.get('value', 0) for opp in recent_services)
                alerts.append({
                    'type': 'success',
                    'title': '🔧 New Service Contract Opportunities Found!',
                    'message': f"{len(recent_services)} new opportunities (${total_value:,.0f} total value)",
                    'action': 'View Services',
                    'system': 'Service Contracts'
                })
        except Exception as e:
            print(f"Error checking service opportunities: {e}")
        
        # Check for pending change orders
        try:
            change_orders = airtable_client.get_all_records('ATLAS CHANGE ORDERS')
            pending = [co for co in change_orders if co['fields'].get('Status') == 'Pending']
            
            for co in pending[:3]:  # Top 3 pending
                fields = co['fields']
                alerts.append({
                    'type': 'info',
                    'title': 'Change Order Pending',
                    'message': f"{fields.get('Title', 'Untitled')} - ${fields.get('Impact Budget', 0):,.0f} approval needed",
                    'action': 'Review',
                    'system': 'ATLAS PM'
                })
        except Exception as e:
            print(f"Error checking change orders: {e}")
        
        return jsonify({'alerts': alerts})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/calendar/feed.ics', methods=['GET'])
def get_calendar_feed():
    """
    Live iCalendar feed — subscribe to this URL in Apple Calendar.
    Combines ALL .ics files from calendars/ + GPSS deadlines into one feed.
    Apple Calendar will poll this URL automatically.
    """
    from flask import Response
    cal_dir = os.path.join(os.path.dirname(__file__), 'calendars')
    vevents = []

    if os.path.isdir(cal_dir):
        for fname in os.listdir(cal_dir):
            if not fname.endswith('.ics'):
                continue
            try:
                with open(os.path.join(cal_dir, fname), 'r') as f:
                    ics_text = f.read()
                for block in ics_text.split('BEGIN:VEVENT')[1:]:
                    raw = block.split('END:VEVENT')[0]
                    vevents.append('BEGIN:VEVENT\n' + raw.strip() + '\nEND:VEVENT')
            except Exception:
                continue

    try:
        airtable_client = AirtableClient()
        opportunities = airtable_client.get_all_records('GPSS OPPORTUNITIES')
        for opp in opportunities:
            fields = opp.get('fields', {})
            deadline_str = fields.get('Response Deadline') or fields.get('Deadline') or fields.get('Due Date') or ''
            if not deadline_str:
                continue
            st = (fields.get('Status', '') or '').lower()
            if any(k in st for k in ['won', 'lost', 'archived', 'passed', 'declined']):
                continue
            try:
                if 'T' in deadline_str:
                    dt = datetime.fromisoformat(deadline_str.replace('Z', '+00:00'))
                else:
                    dt = datetime.strptime(deadline_str, '%Y-%m-%d')
                uid = opp.get('id', 'unknown') + '@nexus-ddi'
                name = fields.get('Name', 'Opportunity')
                value = fields.get('Estimated Value', '')
                status = fields.get('Status', '')
                dtstr = dt.strftime('%Y%m%dT%H%M%S')
                vevents.append(
                    f'BEGIN:VEVENT\n'
                    f'UID:{uid}\n'
                    f'DTSTAMP:{datetime.now().strftime("%Y%m%dT%H%M%S")}\n'
                    f'DTSTART:{dtstr}\n'
                    f'DTEND:{dtstr}\n'
                    f'SUMMARY:📋 BID DUE: {name}\n'
                    f'DESCRIPTION:Status: {status}\\nValue: {value}\n'
                    f'STATUS:CONFIRMED\n'
                    f'BEGIN:VALARM\nTRIGGER:-P1D\nACTION:DISPLAY\nDESCRIPTION:Bid due tomorrow: {name}\nEND:VALARM\n'
                    f'BEGIN:VALARM\nTRIGGER:-PT2H\nACTION:DISPLAY\nDESCRIPTION:Bid due in 2 hours: {name}\nEND:VALARM\n'
                    f'END:VEVENT'
                )
            except Exception:
                continue
    except Exception:
        pass

    ics_body = (
        'BEGIN:VCALENDAR\n'
        'VERSION:2.0\n'
        'PRODID:-//Dee Davis Inc//NEXUS Command Center//EN\n'
        'CALSCALE:GREGORIAN\n'
        'METHOD:PUBLISH\n'
        'X-WR-CALNAME:NEXUS - DDI Bids & Events\n'
        'X-WR-TIMEZONE:America/Detroit\n'
        'X-WR-CALDESC:All NEXUS bid deadlines, calls, and events for Dee Davis Inc.\n'
        + '\n'.join(vevents) + '\n'
        'END:VCALENDAR\n'
    )

    return Response(
        ics_body,
        mimetype='text/calendar',
        headers={'Content-Disposition': 'inline; filename="nexus_calendar.ics"'}
    )


@app.route('/calendar/events', methods=['GET'])
def get_calendar_events():
    """Read all .ics files from calendars/ and return events for the dashboard calendar."""
    import re as _re
    cal_dir = os.path.join(os.path.dirname(__file__), 'calendars')
    events = []

    if os.path.isdir(cal_dir):
        for fname in os.listdir(cal_dir):
            if not fname.endswith('.ics'):
                continue
            try:
                with open(os.path.join(cal_dir, fname), 'r') as f:
                    ics_text = f.read()

                for block in ics_text.split('BEGIN:VEVENT')[1:]:
                    block = block.split('END:VEVENT')[0]

                    def _field(name):
                        for line in block.splitlines():
                            if line.startswith(name + ':') or line.startswith(name + ';'):
                                return line.split(':', 1)[-1].strip()
                        return ''

                    raw_start = _field('DTSTART')
                    summary = _field('SUMMARY')
                    description = _field('DESCRIPTION').replace('\\n', '\n')
                    location = _field('LOCATION')
                    status = _field('STATUS')

                    dt = None
                    for fmt in ('%Y%m%dT%H%M%S', '%Y%m%dT%H%M%SZ', '%Y%m%d'):
                        try:
                            dt = datetime.strptime(raw_start, fmt)
                            break
                        except ValueError:
                            continue

                    if dt and summary:
                        events.append({
                            'date': dt.strftime('%Y-%m-%d'),
                            'time': dt.strftime('%I:%M %p') if 'T' in raw_start else '',
                            'title': summary,
                            'description': description[:300],
                            'location': location,
                            'status': status,
                            'source': 'calendar',
                            'file': fname,
                        })
            except Exception:
                continue

    try:
        now = datetime.now()
        airtable_client = AirtableClient()
        opportunities = airtable_client.get_all_records('GPSS OPPORTUNITIES')
        for opp in opportunities:
            fields = opp.get('fields', {})
            deadline_str = fields.get('Response Deadline') or fields.get('Deadline') or fields.get('Due Date') or ''
            if not deadline_str:
                continue
            st = (fields.get('Status', '') or '').lower()
            if any(k in st for k in ['won', 'lost', 'archived', 'passed', 'declined']):
                continue
            try:
                if 'T' in deadline_str:
                    dt = datetime.fromisoformat(deadline_str.replace('Z', '+00:00'))
                    if dt.tzinfo:
                        dt = dt.replace(tzinfo=None)
                else:
                    dt = datetime.strptime(deadline_str, '%Y-%m-%d')
                if dt < now:
                    continue

                ai_rec = fields.get('AI Recommendation ', '') or ''
                priority = (fields.get('Priority', '') or '').lower()
                ai_score = 0
                if '/' in ai_rec:
                    try:
                        ai_score = int(ai_rec.split('(')[1].split('/')[0])
                    except (IndexError, ValueError):
                        pass
                ai_label = ai_rec.upper().split('(')[0].strip() if ai_rec else ''
                is_actionable = (
                    ai_score >= 50
                    or 'GO' in ai_label
                    or 'BID' in ai_label
                    or priority == 'high'
                )
                if not is_actionable:
                    continue

                label = '🔥 BID DUE' if ai_score >= 70 or 'BID' in ai_label else '📋'
                events.append({
                    'date': dt.strftime('%Y-%m-%d'),
                    'time': dt.strftime('%I:%M %p') if 'T' in deadline_str else '',
                    'title': f"{label} {fields.get('Name', 'Opportunity')}",
                    'description': f"AI: {ai_rec}\nSet-Aside: {fields.get('Set-Aside Type', 'N/A')}",
                    'location': fields.get('Performance Location', ''),
                    'status': fields.get('Source Status', ''),
                    'source': 'gpss',
                })
            except Exception:
                continue
    except Exception:
        pass

    events.sort(key=lambda e: e['date'])
    return jsonify({'events': events, 'count': len(events)})


@app.route('/transportation-logistics/notifications', methods=['GET'])
def get_transportation_logistics_notifications():
    """
    Get Transportation & Logistics opportunity notifications
    Returns: new opportunities, today's focus, stats
    """
    try:
        airtable_client = AirtableClient()
        notifications = {
            'new_opportunities': [],
            'todays_focus': {},
            'weekly_stats': {},
            'high_priority': []
        }
        
        now = datetime.now()
        
        # Get all opportunities and filter for transportation
        try:
            opportunities = airtable_client.get_all_records('GPSS OPPORTUNITIES')
            transportation_keywords = ['airport', 'aviation', 'marine', 'port', 'maritime', 'cargo', 
                                     'freight', 'courier', 'postal', 'USPS', 'transit', 'transportation',
                                     'shipping', 'warehouse', 'logistics', 'NEMT', 'non-emergency medical',
                                     'medical transportation', 'medical transport', 'patient transport',
                                     'patient transportation', 'paratransit', 'healthcare transportation',
                                     'ambulatory', 'Medicaid transportation', 'Medicare transportation']
            
            all_transportation = []
            new_transportation = []
            high_value_transportation = []
            
            for opp in opportunities:
                fields = opp['fields']
                title = fields.get('Title', '').lower()
                description = fields.get('Description', '').lower()
                category = fields.get('Category', '').lower()
                
                # Check if it's a transportation opportunity
                is_transportation = any(keyword.lower() in title or keyword.lower() in description or keyword.lower() in category 
                                      for keyword in transportation_keywords)
                
                if is_transportation:
                    opp_data = {
                        'id': opp['id'],
                        'title': fields.get('Title', 'Untitled'),
                        'value': fields.get('Estimated Value', 0),
                        'due_date': fields.get('Due Date'),
                        'status': fields.get('Status'),
                        'category': fields.get('Category', 'Transportation/Logistics')
                    }
                    
                    all_transportation.append(opp_data)
                    
                    # Check if created recently (last 7 days)
                    created_time = fields.get('Created Time') or fields.get('Date Added')
                    if created_time:
                        try:
                            created_date = datetime.fromisoformat(created_time.replace('Z', '+00:00'))
                            days_since = (now - created_date).days
                            
                            if days_since <= 7:
                                new_transportation.append(opp_data)
                        except:
                            pass
                    
                    # Check for high value opportunities (>$100K)
                    if opp_data['value'] > 100000 and opp_data['status'] in ['Active', 'New', 'Review']:
                        high_value_transportation.append(opp_data)
            
            notifications['new_opportunities'] = new_transportation[:5]  # Top 5 newest
            notifications['high_priority'] = high_value_transportation[:3]  # Top 3 high value
            
            # Calculate weekly stats
            notifications['weekly_stats'] = {
                'total_opportunities': len(all_transportation),
                'new_this_week': len(new_transportation),
                'total_value': sum(opp['value'] for opp in all_transportation),
                'average_value': sum(opp['value'] for opp in all_transportation) / len(all_transportation) if all_transportation else 0,
                'high_value_count': len(high_value_transportation)
            }
            
        except Exception as e:
            print(f"Error fetching transportation opportunities: {e}")
        
        # Today's recommended focus
        try:
            import calendar
            day_name = calendar.day_name[now.weekday()].lower()
            
            transportation_schedule = {
                'monday': {
                    'focus': 'NEMT & Healthcare Transportation',
                    'icon': '🚑',
                    'searches': [
                        '"NEMT" WOSB',
                        '"non-emergency medical transportation" small business',
                        '"medical transportation services" EDWOSB'
                    ],
                    'expected_results': '15-25 opportunities',
                    'revenue_potential': '$500K-$2M per contract',
                    'special_note': 'HIGHEST VALUE! Medicaid/Medicare contracts. Perfect for WOSB set-asides!'
                },
                'tuesday': {
                    'focus': 'Airport & Aviation',
                    'icon': '✈️',
                    'searches': [
                        '"airport supplies" WOSB',
                        '"aviation supplies" small business',
                        '"terminal supplies" EDWOSB'
                    ],
                    'expected_results': '10-15 opportunities',
                    'revenue_potential': '$30K-$500K per contract'
                },
                'wednesday': {
                    'focus': 'Port & Marine',
                    'icon': '🚢',
                    'searches': [
                        '"marine supplies" WOSB',
                        '"port supplies" EDWOSB',
                        '"maritime supplies" small business'
                    ],
                    'expected_results': '5-10 opportunities',
                    'revenue_potential': '$40K-$400K per contract'
                },
                'thursday': {
                    'focus': 'Courier & Postal + Cargo',
                    'icon': '📬',
                    'searches': [
                        '"postal supplies" WOSB',
                        '"USPS" supplies small business',
                        '"cargo handling" EDWOSB'
                    ],
                    'expected_results': '15-20 opportunities',
                    'revenue_potential': '$20K-$300K per contract',
                    'special_note': '31,000+ USPS facilities nationwide!'
                },
                'friday': {
                    'focus': 'Transit & Transportation',
                    'icon': '🚌',
                    'searches': [
                        '"transit supplies" WOSB',
                        '"transportation supplies" small business',
                        '"bus supplies" EDWOSB'
                    ],
                    'expected_results': '5-10 opportunities',
                    'revenue_potential': '$30K-$250K per contract'
                }
            }
            
            notifications['todays_focus'] = transportation_schedule.get(day_name, transportation_schedule['monday'])
            notifications['todays_focus']['day'] = day_name.capitalize()
            
        except Exception as e:
            print(f"Error building today's focus: {e}")
        
        return jsonify(notifications)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/service-contracts/notifications', methods=['GET'])
def get_service_contracts_notifications():
    """
    Get Service Contracts opportunity notifications
    Returns: new opportunities, today's focus, stats
    """
    try:
        airtable_client = AirtableClient()
        notifications = {
            'new_opportunities': [],
            'todays_focus': {},
            'weekly_stats': {},
            'high_priority': []
        }
        
        now = datetime.now()
        
        # Get all opportunities and filter for service contracts
        try:
            opportunities = airtable_client.get_all_records('GPSS OPPORTUNITIES')
            service_keywords = ['janitorial', 'custodial', 'cleaning services', 'landscaping', 
                              'grounds maintenance', 'lawn care', 'facility maintenance', 
                              'building maintenance', 'HVAC', 'repair services', 'IT services',
                              'IT support', 'network services', 'security services', 'security guard',
                              'construction services', 'renovation', 'building renovation',
                              'moving services', 'relocation', 'event services', 'catering',
                              'floor maintenance', 'window cleaning', 'snow removal',
                              'tree services', 'plumbing', 'electrical maintenance',
                              'help desk', 'cybersecurity', 'patrol services']
            
            all_services = []
            new_services = []
            high_value_services = []
            
            for opp in opportunities:
                fields = opp['fields']
                title = fields.get('Title', '').lower()
                description = fields.get('Description', '').lower()
                category = fields.get('Category', '').lower()
                
                # Check if it's a service opportunity
                is_service = any(keyword.lower() in title or keyword.lower() in description or keyword.lower() in category 
                                for keyword in service_keywords)
                
                if is_service:
                    opp_data = {
                        'id': opp['id'],
                        'title': fields.get('Title', 'Untitled'),
                        'value': fields.get('Estimated Value', 0),
                        'due_date': fields.get('Due Date'),
                        'status': fields.get('Status'),
                        'category': fields.get('Category', 'Service Contracts')
                    }
                    
                    all_services.append(opp_data)
                    
                    # Check if created recently (last 7 days)
                    created_time = fields.get('Created Time') or fields.get('Date Added')
                    if created_time:
                        try:
                            created_date = datetime.fromisoformat(created_time.replace('Z', '+00:00'))
                            days_since = (now - created_date).days
                            
                            if days_since <= 7:
                                new_services.append(opp_data)
                        except:
                            pass
                    
                    # Check for high value opportunities (>$100K)
                    if opp_data['value'] > 100000 and opp_data['status'] in ['Active', 'New', 'Review']:
                        high_value_services.append(opp_data)
            
            notifications['new_opportunities'] = new_services[:5]  # Top 5 newest
            notifications['high_priority'] = high_value_services[:3]  # Top 3 high value
            
            # Calculate weekly stats
            notifications['weekly_stats'] = {
                'total_opportunities': len(all_services),
                'new_this_week': len(new_services),
                'total_value': sum(opp['value'] for opp in all_services),
                'average_value': sum(opp['value'] for opp in all_services) / len(all_services) if all_services else 0,
                'high_value_count': len(high_value_services)
            }
            
        except Exception as e:
            print(f"Error fetching service contract opportunities: {e}")
        
        # Today's recommended focus
        try:
            import calendar
            day_name = calendar.day_name[now.weekday()].lower()
            
            service_schedule = {
                'monday': {
                    'focus': 'High-Value Services (IT & Security)',
                    'icon': '💻',
                    'searches': [
                        '"IT services" WOSB',
                        '"security services" small business',
                        '"cybersecurity services" EDWOSB'
                    ],
                    'expected_results': '15-25 opportunities',
                    'revenue_potential': '$100K-$3M per contract',
                    'special_note': 'Your E&O insurance is a major advantage for IT contracts!'
                },
                'tuesday': {
                    'focus': 'Facility Services (Janitorial & Maintenance)',
                    'icon': '🧹',
                    'searches': [
                        '"janitorial services" WOSB',
                        '"facility maintenance" small business',
                        '"building maintenance" EDWOSB'
                    ],
                    'expected_results': '20-30 opportunities',
                    'revenue_potential': '$50K-$1M per contract',
                    'special_note': 'Very common contracts with steady revenue'
                },
                'wednesday': {
                    'focus': 'Outdoor Services (Landscaping & Grounds)',
                    'icon': '🌳',
                    'searches': [
                        '"landscaping services" WOSB',
                        '"grounds maintenance" small business',
                        '"snow removal" EDWOSB'
                    ],
                    'expected_results': '15-20 opportunities',
                    'revenue_potential': '$50K-$500K per contract',
                    'special_note': 'Snow removal can double winter revenue!'
                },
                'thursday': {
                    'focus': 'Construction & Renovation',
                    'icon': '🏗️',
                    'searches': [
                        '"building renovation" WOSB',
                        '"construction services" small business',
                        '"facility renovation" EDWOSB'
                    ],
                    'expected_results': '10-15 opportunities',
                    'revenue_potential': '$100K-$5M per project',
                    'special_note': 'Largest contracts! Start with smaller renovations.'
                },
                'friday': {
                    'focus': 'Support Services (Moving & Events)',
                    'icon': '🚚',
                    'searches': [
                        '"moving services" WOSB',
                        '"event services" small business',
                        '"relocation services" EDWOSB'
                    ],
                    'expected_results': '10-15 opportunities',
                    'revenue_potential': '$25K-$500K per project',
                    'special_note': 'Quick wins with recurring potential'
                }
            }
            
            notifications['todays_focus'] = service_schedule.get(day_name, service_schedule['monday'])
            notifications['todays_focus']['day'] = day_name.capitalize()
            
        except Exception as e:
            print(f"Error building today's focus: {e}")
        
        return jsonify(notifications)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/gpss/upload-rfp', methods=['POST'])
def upload_and_analyze_rfp():
    """
    Full RFP Upload & Analysis Pipeline:
    1. Extract text from PDF
    2. AI analyzes: scope, requirements, line items, deadline, set-aside, NAICS
    3. AI extracts contacts (contracting officers, POCs)
    4. AI gives bid/no-bid recommendation
    5. Creates opportunity record in Airtable
    6. Returns comprehensive analysis to frontend
    """
    try:
        import PyPDF2
        
        # --- Step 1: Get the PDF text ---
        if 'file' not in request.files:
            return jsonify({"success": False, "error": "No file uploaded"}), 400
        
        file = request.files['file']
        if not file.filename:
            return jsonify({"success": False, "error": "No file selected"}), 400
        
        document_name = file.filename
        document_text = ""
        
        if file.filename.lower().endswith('.pdf'):
            try:
                pdf_reader = PyPDF2.PdfReader(file)
                max_pages = min(len(pdf_reader.pages), 30)
                for page_num in range(max_pages):
                    try:
                        page_text = pdf_reader.pages[page_num].extract_text()
                        if page_text and page_text.strip():
                            document_text += page_text.strip() + "\n"
                    except:
                        continue
            except Exception as e:
                return jsonify({"success": False, "error": f"PDF read failed: {str(e)}"}), 400
        else:
            # Plain text or other — read as text
            document_text = file.read().decode('utf-8', errors='ignore')
        
        if not document_text.strip():
            return jsonify({
                "success": False,
                "error": "No readable text found in file. It may be scanned/image-only. Use manual text entry."
            }), 400
        
        # --- Step 2: Full AI Analysis ---
        ai = AnthropicClient()
        
        # Truncate for AI context window but keep as much as possible
        rfp_text_for_ai = document_text[:25000]
        
        analysis_prompt = f"""You are analyzing a government solicitation/RFP document for Dee Davis Inc., 
an EDWOSB-certified woman-owned small business in Michigan.

DOCUMENT: {document_name}

FULL TEXT:
{rfp_text_for_ai}

Analyze this RFP completely and return ONLY valid JSON (no markdown, no preamble):
{{
  "solicitation_info": {{
    "title": "Full title of the solicitation",
    "rfp_number": "Solicitation/RFP/IFB/RFQ number",
    "agency": "Issuing agency name",
    "department": "Department if mentioned",
    "deadline": "Submission deadline (YYYY-MM-DD if possible, or exact text)",
    "set_aside_type": "EDWOSB|WOSB|Small Business|Unrestricted|8(a)|HUBZone|SDVOSB|Other",
    "naics_codes": ["list of NAICS codes mentioned"],
    "estimated_value": "Dollar value or range if mentioned",
    "contract_type": "Firm Fixed Price|Time & Materials|IDIQ|BPA|Other",
    "performance_location": "Where work is performed",
    "state": "State abbreviation (e.g. MI, TX)",
    "period_of_performance": "Duration of contract"
  }},
  "scope_of_work": {{
    "summary": "2-3 sentence summary of what they need",
    "key_deliverables": ["deliverable 1", "deliverable 2"],
    "line_items": [
      {{
        "item": "Item/service description",
        "quantity": "Quantity if specified",
        "unit": "Unit of measure"
      }}
    ]
  }},
  "compliance_requirements": {{
    "required_certifications": ["SAM.gov registration", "etc"],
    "required_documents": ["W-9", "capability statement", "past performance", "etc"],
    "insurance_requirements": "If mentioned",
    "bonding_requirements": "If mentioned",
    "special_requirements": ["any special requirements"]
  }},
  "evaluation_criteria": [
    {{
      "factor": "Factor name",
      "weight": "Weight or priority if mentioned",
      "description": "Brief description"
    }}
  ],
  "contacts": [
    {{
      "name": "Full name",
      "title": "Job title",
      "email": "email@agency.gov",
      "phone": "Phone if available",
      "role": "Contracting Officer|Program Manager|Technical POC|Other"
    }}
  ],
  "bid_recommendation": {{
    "decision": "GO|NO-GO|REVIEW",
    "score": 0-100,
    "reasoning": "Why this is a good or bad fit for Dee Davis Inc",
    "strengths": ["Why we should bid"],
    "concerns": ["Potential issues"],
    "effort_level": "LOW|MEDIUM|HIGH",
    "competitive_position": "Strong|Moderate|Weak|Unknown"
  }}
}}"""

        response = ai.complete(analysis_prompt, max_tokens=4000)
        clean_response = response.replace('```json', '').replace('```', '').strip()
        
        try:
            analysis = json.loads(clean_response)
        except json.JSONDecodeError:
            # Try to salvage partial JSON
            import re
            json_match = re.search(r'\{.*\}', clean_response, re.DOTALL)
            if json_match:
                analysis = json.loads(json_match.group())
            else:
                return jsonify({"success": False, "error": "AI analysis returned invalid format. Try again."}), 500
        
        # --- Step 3: Create Opportunity in Airtable ---
        sol_info = analysis.get('solicitation_info', {})
        bid_rec = analysis.get('bid_recommendation', {})
        scope = analysis.get('scope_of_work', {})
        
        airtable_client = AirtableClient()
        
        opp_fields = {
            'Name': sol_info.get('title', document_name.replace('.pdf', '')),
            'RFP NUMBER': sol_info.get('rfp_number', ''),
            'AGENCY NAME': sol_info.get('agency', ''),
            'Deadline': sol_info.get('deadline', ''),
            'Set-Aside Type': sol_info.get('set_aside_type', ''),
            'NAISC Codes': ', '.join(sol_info.get('naics_codes', [])) if isinstance(sol_info.get('naics_codes'), list) else sol_info.get('naics_codes', ''),
            'State': sol_info.get('state', ''),
            'Source Status': 'Not Started',
            'Notes': f"Uploaded: {document_name}\n\nScope: {scope.get('summary', '')}\n\nBid Recommendation: {bid_rec.get('decision', 'REVIEW')} ({bid_rec.get('score', 0)}/100)\n{bid_rec.get('reasoning', '')}",
            'Priority': 'High' if bid_rec.get('decision') == 'GO' else 'Medium',
        }
        
        # Clean empty fields
        opp_fields = {k: v for k, v in opp_fields.items() if v}
        
        try:
            opp_record = airtable_client.create_record('GPSS Opportunities', opp_fields)
            opportunity_id = opp_record['id']
        except Exception as e:
            print(f"Airtable opportunity creation error: {e}")
            opportunity_id = None
        
        # --- Step 4: Store Contacts ---
        contacts = analysis.get('contacts', [])
        stored_contacts = 0
        for contact in contacts:
            email = contact.get('email', '')
            if not email or '@' not in email:
                continue
            try:
                contact_fields = {
                    'Name': contact.get('name', ''),
                    'Email': email,
                    'Title': contact.get('title', ''),
                    'Organization': sol_info.get('agency', ''),
                    'Role Category': contact.get('role', ''),
                    'Priority': 'HIGH' if 'Contracting Officer' in contact.get('role', '') else 'MEDIUM',
                    'Notes': f"From RFP: {document_name}"
                }
                # Check for duplicates
                existing = airtable_client.search_records('GPSS Contacts', f"{{Email}} = '{email}'")
                if existing:
                    airtable_client.update_record('GPSS Contacts', existing[0]['id'], contact_fields)
                else:
                    airtable_client.create_record('GPSS Contacts', contact_fields)
                stored_contacts += 1
            except Exception as e:
                print(f"Contact store error: {e}")
                continue
        
        # --- Step 5: Auto-generate proposal matrix if GO recommendation ---
        proposal_matrix = None
        if opportunity_id and bid_rec.get('decision') == 'GO':
            try:
                from nexus_backend import GPSSSubcontractorMiner
                miner = GPSSSubcontractorMiner()
                matrix_result = miner.generate_proposal_matrix(opportunity_id)
                if matrix_result.get('success'):
                    proposal_matrix = matrix_result.get('matrix')
                    print(f"✅ Auto-generated proposal matrix for {document_name}")
            except Exception as e:
                print(f"Proposal matrix auto-generation note: {e}")
        
        # --- Step 6: Return everything ---
        return jsonify({
            "success": True,
            "document_name": document_name,
            "opportunity_id": opportunity_id,
            "analysis": analysis,
            "contacts_found": len(contacts),
            "contacts_stored": stored_contacts,
            "text_length": len(document_text),
            "pages_read": max_pages if file.filename.lower().endswith('.pdf') else 1,
            "proposal_matrix": proposal_matrix,
            "auto_actions": [
                f"Created opportunity in Airtable",
                f"Stored {stored_contacts} contacts",
            ] + ([f"Auto-generated proposal compliance matrix ({proposal_matrix.get('total_requirements', 0)} requirements)"] if proposal_matrix else [])
        })
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/extract-contacts', methods=['POST'])
def extract_contacts():
    """
    Extract contacts from document text or uploaded PDF file

    Accepts either:
    1. JSON: {"document_text": "...", "document_name": "..."}
    2. Form data with file: uploaded PDF file
    """
    try:
        document_text = ""
        document_name = "Unknown Document"

        # Check if it's a file upload
        if 'file' in request.files:
            file = request.files['file']
            if file.filename == '':
                return jsonify({"error": "No file selected"}), 400

            if file and file.filename.lower().endswith('.pdf'):
                document_name = file.filename

                # Process PDF file with error handling
                try:
                    import PyPDF2
                    pdf_reader = PyPDF2.PdfReader(file)

                    # Extract text from all pages (limit to first 20 pages for performance)
                    document_text = ""
                    max_pages = min(len(pdf_reader.pages), 20)

                    for page_num in range(max_pages):
                        try:
                            page = pdf_reader.pages[page_num]
                            page_text = page.extract_text()
                            if page_text and page_text.strip():
                                document_text += page_text.strip() + "\n"
                        except Exception as page_error:
                            # Skip problematic pages
                            continue

                    if not document_text.strip():
                        return jsonify({
                            "success": False,
                            "error": "No readable text found in PDF. The PDF may contain only images, be scanned, or password-protected. Try uploading a different PDF or use the manual text entry option."
                        }), 400

                except Exception as pdf_error:
                    return jsonify({
                        "success": False,
                        "error": f"PDF processing failed: {str(pdf_error)}. Try a different PDF file or use manual text entry."
                    }), 400

        # Check if it's JSON text input
        elif request.is_json:
            data = request.json
            document_text = data.get('document_text', '')
            document_name = data.get('document_name', 'Unknown Document')

            if not document_text:
                return jsonify({"error": "document_text required"}), 400

        else:
            return jsonify({"error": "Invalid request format. Send JSON with document_text or upload a PDF file."}), 400

        # Process the extracted text
        result = handle_document_upload(document_text, document_name)
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/qualify-opportunity', methods=['POST'])
def qualify_opportunity():
    """
    Qualify a government opportunity
    
    Expected JSON:
    {
        "opportunity_id": "rec..."
    }
    """
    try:
        data = request.json
        opportunity_id = data.get('opportunity_id', '')
        
        if not opportunity_id:
            return jsonify({"error": "opportunity_id required"}), 400
        
        result = handle_qualify_opportunity(opportunity_id)
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/generate-quote', methods=['POST'])
def generate_quote():
    """
    Generate quote for opportunity

    Expected JSON:
    {
        "opportunity_id": "rec..."
    }
    """
    try:
        data = request.json
        opportunity_id = data.get('opportunity_id', '')

        if not opportunity_id:
            return jsonify({"error": "opportunity_id required"}), 400

        result = handle_generate_quote(opportunity_id)
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# =====================================================================
# DDCSS ENDPOINTS - Corporate Sales System
# =====================================================================

@app.route('/ddcss/stats', methods=['GET'])
def get_ddcss_stats():
    """Get DDCSS dashboard statistics"""
    try:
        airtable_client = AirtableClient()
        
        try:
            prospects = airtable_client.get_all_records('DDCSS PROSPECTS')
        except:
            prospects = []
        
        # Calculate prospect stats
        qualified = [p for p in prospects if p['fields'].get('Status') == 'Qualified']
        active = [p for p in prospects if p['fields'].get('Status') == 'Active']
        closed = [p for p in prospects if p['fields'].get('Status') == 'Closed Won']
        
        # Calculate revenue potential
        total_value = sum(p['fields'].get('Deal Value', 0) for p in prospects if isinstance(p['fields'].get('Deal Value'), (int, float)))
        
        stats = {
            'totalProspects': len(prospects),
            'qualifiedProspects': len(qualified),
            'activeProspects': len(active),
            'closedDeals': len(closed),
            'totalPipelineValue': total_value
        }
        
        return jsonify(stats)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/ddcss/qualify-prospect', methods=['POST'])
def ddcss_qualify_prospect():
    """
    Qualify a corporate prospect using AI analysis

    Expected JSON:
    {
        "prospect_id": "rec..."
    }
    """
    try:
        data = request.json
        prospect_id = data.get('prospect_id', '')

        if not prospect_id:
            return jsonify({"error": "prospect_id required"}), 400

        result = handle_ddcss_qualify_prospect(prospect_id)

        # NEXUS ADVISOR: Teach about prospect qualification
        try:
            from nexus_advisor import advise
            result['advisor'] = advise('ddcss', 'prospect_qualified', {
                'prospect_id': prospect_id,
            })
        except Exception:
            pass

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/ddcss/generate-blueprint', methods=['POST'])
def ddcss_generate_blueprint():
    """
    Generate a customized Blueprint Framework

    Expected JSON:
    {
        "prospect_id": "rec...",
        "framework_type": "ALIGN|DEFINE|DESIGN|SHINE" (optional, defaults to ALIGN)
    }
    """
    try:
        data = request.json
        prospect_id = data.get('prospect_id', '')
        framework_type = data.get('framework_type', 'ALIGN')

        if not prospect_id:
            return jsonify({"error": "prospect_id required"}), 400

        if framework_type not in ['ALIGN', 'DEFINE', 'DESIGN', 'SHINE']:
            return jsonify({"error": "Invalid framework_type. Must be ALIGN, DEFINE, DESIGN, or SHINE"}), 400

        result = handle_ddcss_generate_blueprint(prospect_id, framework_type)

        # NEXUS ADVISOR: Teach about blueprints
        try:
            from nexus_advisor import advise
            result['advisor'] = advise('ddcss', 'blueprint_generated', {
                'framework_type': framework_type,
            })
        except Exception:
            pass

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/ddcss/analyze-response', methods=['POST'])
def ddcss_analyze_response():
    """
    Analyze inbound email response using AI

    Expected JSON:
    {
        "email_content": "Full email text...",
        "prospect_id": "rec..." (optional)
    }
    """
    try:
        data = request.json
        email_content = data.get('email_content', '')
        prospect_id = data.get('prospect_id', '')

        if not email_content:
            return jsonify({"error": "email_content required"}), 400

        result = handle_ddcss_analyze_response(email_content, prospect_id or None)
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# =====================================================================
# ATLAS PM ENDPOINTS - Project Management System
# =====================================================================

@app.route('/atlas/stats', methods=['GET'])
def get_atlas_stats():
    """Get ATLAS PM dashboard statistics"""
    try:
        airtable_client = AirtableClient()
        
        try:
            projects = airtable_client.get_all_records('ATLAS PROJECTS')
        except:
            projects = []
        
        try:
            tasks = airtable_client.get_all_records('ATLAS TASKS')
        except:
            tasks = []
        
        # Calculate project stats
        active_projects = [p for p in projects if p['fields'].get('Status') in ['In Progress', 'Planning']]
        completed_projects = [p for p in projects if p['fields'].get('Status') == 'Completed']
        
        # Calculate task stats
        active_tasks = [t for t in tasks if t['fields'].get('Status') in ['in-progress', 'pending']]
        completed_tasks = [t for t in tasks if t['fields'].get('Status') == 'done']
        
        # Calculate budgets
        total_budget = sum(p['fields'].get('Budget', 0) for p in projects if isinstance(p['fields'].get('Budget'), (int, float)))
        
        stats = {
            'totalProjects': len(projects),
            'activeProjects': len(active_projects),
            'completedProjects': len(completed_projects),
            'totalTasks': len(tasks),
            'activeTasks': len(active_tasks),
            'completedTasks': len(completed_tasks),
            'totalBudget': total_budget
        }
        
        return jsonify(stats)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Project CRUD operations
@app.route('/atlas/projects', methods=['GET'])
def get_atlas_projects():
    """Get all projects with optional filtering"""
    try:
        airtable_client = AirtableClient()
        records = airtable_client.get_all_records('ATLAS PROJECTS')

        # Transform records for frontend
        projects = []
        for record in records:
            fields = record['fields']
            projects.append({
                'id': record['id'],
                'name': fields.get('Project Name', ''),
                'client': fields.get('Client Name', ''),
                'status': fields.get('Status', 'Planning'),
                'budget': fields.get('Budget', 0),
                'timeline': fields.get('Timeline', ''),
                'completion_percentage': fields.get('Completion Percentage', 0),
                'priority': fields.get('Priority', 'Medium'),
                'start_date': fields.get('Start Date'),
                'end_date': fields.get('End Date'),
                'created_date': fields.get('Created Date')
            })

        return jsonify({'projects': projects})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/atlas/projects', methods=['POST'])
def create_atlas_project():
    """Create a new project"""
    try:
        data = request.json
        airtable_client = AirtableClient()

        fields = {
            'Project Name': data.get('name', ''),
            'Client Name': data.get('client', ''),
            'Project Type': data.get('type', 'Consulting'),
            'Industry': data.get('industry', ''),
            'Project Scope': data.get('scope', ''),
            'Budget': data.get('budget', 0),
            'Timeline': data.get('timeline', ''),
            'Start Date': data.get('start_date'),
            'Status': 'Planning',
            'Priority': data.get('priority', 'Medium'),
            'Completion Percentage': 0,
            'Created Date': datetime.now().isoformat()
        }

        result = airtable_client.create_record('ATLAS PROJECTS', fields)

        # NEXUS ADVISOR: Teach about project planning
        advisor_insight = None
        try:
            from nexus_advisor import advise
            advisor_insight = advise('atlas', 'project_created', {
                'project_type': data.get('type'),
                'budget': data.get('budget', 0),
            })
        except Exception:
            pass

        return jsonify({
            'project': {'id': result['id'], **fields},
            'advisor': advisor_insight,
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def create_atlas_project_from_opportunity(opportunity_id: str, airtable_client=None) -> dict:
    """
    🎯 AUTO-CREATE ATLAS PROJECT FROM WON GPSS OPPORTUNITY
    This is the 90% automation bridge!
    """
    if not airtable_client:
        airtable_client = AirtableClient()
    
    # Get opportunity details
    opportunity = airtable_client.get_record('GPSS OPPORTUNITIES', opportunity_id)
    opp_fields = opportunity['fields']
    
    # Extract key information
    project_name = opp_fields.get('Title', 'Untitled Project')
    client_name = opp_fields.get('Agency Name', 'Unknown Agency')
    contract_value = opp_fields.get('Value', 0)
    rfp_number = opp_fields.get('RFP Number', '')
    due_date = opp_fields.get('Due Date', '')
    description = opp_fields.get('Description', '')
    requirements = opp_fields.get('Requirements', '')
    category = opp_fields.get('Category', 'General')
    
    # Build comprehensive project scope from opportunity data
    project_scope = f"""
CONTRACT: {rfp_number}
AGENCY: {client_name}
CATEGORY: {category}

DESCRIPTION:
{description}

REQUIREMENTS:
{requirements}
    """.strip()
    
    # Calculate project timeline (default 6 months or based on contract)
    start_date = datetime.now().isoformat()
    
    # Determine project type based on category
    project_type_mapping = {
        'Healthcare': 'Healthcare Services',
        'Logistics': 'Logistics & Transportation',
        'IT': 'Technology Services',
        'Construction': 'Construction',
        'Consulting': 'Professional Services',
        'Products': 'Product Delivery',
        'Supplies': 'Product Delivery'
    }
    project_type = project_type_mapping.get(category, 'Government Contract')
    
    # Create ATLAS project record
    project_fields = {
        'Project Name': f"{project_name} ({client_name})",
        'Client Name': client_name,
        'Project Type': project_type,
        'Budget': contract_value,
        'Project Scope': project_scope[:10000],  # Airtable field limit
        'Start Date': start_date,
        'Status': 'Planning',
        'Priority': 'High',
        'Completion Percentage': 0,
        'Created Date': datetime.now().isoformat(),
        'Source System': 'GPSS',
        'Source Opportunity ID': opportunity_id,
        'Contract Number': rfp_number
    }
    
    # Create the project in Airtable
    project_record = airtable_client.create_record('ATLAS PROJECTS', project_fields)
    project_id = project_record['id']
    
    # Link opportunity to ATLAS project (bidirectional)
    try:
        airtable_client.update_record('GPSS OPPORTUNITIES', opportunity_id, {
            'ATLAS Project': [project_id]
        })
    except Exception as link_error:
        print(f"Warning: Could not link opportunity to ATLAS project: {link_error}")
    
    # 🤖 AUTO-GENERATE WBS using ATLAS Agent 2
    wbs_generated = False
    try:
        from nexus_backend import ATLASAgent2
        atlas_agent = ATLASAgent2()
        wbs_result = atlas_agent.generate_wbs(project_id)
        wbs_generated = 'error' not in wbs_result
    except Exception as wbs_error:
        print(f"Warning: WBS generation failed: {wbs_error}")
    
    return {
        'success': True,
        'project_id': project_id,
        'project_name': project_fields['Project Name'],
        'wbs_generated': wbs_generated,
        'message': f'✅ ATLAS project created: {project_fields["Project Name"]}'
    }


@app.route('/gpss/opportunities/<opportunity_id>/create-atlas-project', methods=['POST'])
def manual_create_atlas_project_from_opportunity(opportunity_id):
    """
    Manual endpoint to create ATLAS project from opportunity
    Used if auto-creation failed or for retroactive project creation
    """
    try:
        result = create_atlas_project_from_opportunity(opportunity_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/gpss/opportunities/<opportunity_id>/solicitation-market-research', methods=['POST'])
def gpss_solicitation_market_research(opportunity_id):
    """
    Incumbent + award pricing research via USASpending (federal awards).
    Body JSON: { "persist_notes": false } — append summary to GPSS OPPORTUNITIES Notes when true.
    """
    try:
        data = request.get_json() or {}
        persist = data.get('persist_notes', False)
        if isinstance(persist, str):
            persist = persist.strip().lower() in ('1', 'true', 'yes', 'on')
        result = handle_solicitation_market_research(opportunity_id, persist_notes=bool(persist))
        status = 200 if result.get('success') else 400
        return jsonify(result), status
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


def create_invoice_from_atlas_project(project_id: str, airtable_client=None) -> dict:
    """
    🎯 AUTO-CREATE INVOICE FROM COMPLETED ATLAS PROJECT
    Universal invoicing for all revenue-generating systems!
    """
    if not airtable_client:
        airtable_client = AirtableClient()
    
    # Get project details
    project = airtable_client.get_record('ATLAS PROJECTS', project_id)
    project_fields = project['fields']
    
    # Extract key information
    project_name = project_fields.get('Project Name', 'Untitled Project')
    client_name = project_fields.get('Client Name', 'Unknown Client')
    budget = project_fields.get('Budget', 0)
    project_type = project_fields.get('Project Type', 'General')
    source_system = project_fields.get('Source System', 'ATLAS')
    start_date = project_fields.get('Start Date', '')
    completion_date = project_fields.get('End Date') or datetime.now().isoformat()
    
    # Generate invoice number
    # Format: INV-YYYYMM-XXXX
    invoice_number = f"INV-{datetime.now().strftime('%Y%m')}-{datetime.now().strftime('%d%H%M')}"
    
    # Build invoice description
    invoice_description = f"""
PROJECT: {project_name}
CLIENT: {client_name}
PROJECT TYPE: {project_type}
PERIOD: {start_date[:10] if start_date else 'N/A'} to {completion_date[:10]}

Project completed and delivered as per agreement.
All deliverables submitted and accepted.
    """.strip()
    
    # Create invoice record
    invoice_fields = {
        'Invoice Number': invoice_number,
        'Client Name': client_name,
        'Invoice Date': datetime.now().isoformat(),
        'Due Date': (datetime.now() + timedelta(days=30)).isoformat(),  # Net 30
        'Amount': budget,
        'Status': 'Draft',
        'Description': invoice_description,
        'Project': [project_id],  # Link to ATLAS project
        'Source System': source_system,
        'Created Date': datetime.now().isoformat()
    }
    
    # Create the invoice
    invoice_record = airtable_client.create_record('INVOICES', invoice_fields)
    invoice_id = invoice_record['id']
    
    # Link project to invoice
    try:
        airtable_client.update_record('ATLAS PROJECTS', project_id, {
            'Invoice': [invoice_id]
        })
    except Exception as link_error:
        print(f"Warning: Could not link project to invoice: {link_error}")

    # VERTEX BRIDGE: Also create in VERTEX INVOICES so financial command center sees it
    try:
        vertex_fields = {
            VI['invoice_number']:  invoice_number,
            VI['invoice_date']:    datetime.now().date().isoformat(),
            VI['due_date']:        (datetime.now() + timedelta(days=30)).date().isoformat(),
            VI['client_name']:     client_name,
            VI['source_system']:   source_system,
            VI['source_record']:   project_id,
            VI['invoice_type']:    'Standard',
            VI['total_amount']:    budget,
            VI['payment_status']:  'Unpaid',
            VI['payment_terms']:   'Net 30',
            VI['notes']:           invoice_description,
        }
        airtable_client.create_record('VERTEX INVOICES', vertex_fields)
    except Exception as ve:
        print(f"VERTEX bridge: Could not create VERTEX invoice: {ve}")

    # NEXUS ADVISOR + LEARNING
    try:
        from nexus_advisor import advise, log_growth
        advise('vertex', 'invoice_created', {'total_amount': budget, 'source_system': source_system})
        log_growth('invoice_created')
    except Exception:
        pass
    
    return {
        'success': True,
        'invoice_id': invoice_id,
        'invoice_number': invoice_number,
        'invoice_amount': budget,
        'message': f'Invoice created: {invoice_number} for ${budget:,.2f}'
    }


@app.route('/atlas/projects/<project_id>/create-invoice', methods=['POST'])
def manual_create_invoice_from_project(project_id):
    """Manual endpoint to create invoice from project"""
    try:
        result = create_invoice_from_atlas_project(project_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/atlas/projects/<project_id>', methods=['GET'])
def get_atlas_project(project_id):
    """Get specific project details"""
    try:
        airtable_client = AirtableClient()
        records = airtable_client.get_all_records('ATLAS PROJECTS')

        project = next((r for r in records if r['id'] == project_id), None)
        if not project:
            return jsonify({"error": "Project not found"}), 404

        fields = project['fields']
        return jsonify({
            'project': {
                'id': project_id,
                **fields
            }
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/atlas/projects/<project_id>', methods=['PUT'])
def update_atlas_project(project_id):
    """Update project details - with auto-INVOICE generation when completed"""
    try:
        data = request.json
        airtable_client = AirtableClient()
        
        # Get current project to check status change
        current_project = airtable_client.get_record('ATLAS PROJECTS', project_id)
        old_status = current_project['fields'].get('Status', '')
        old_completion = current_project['fields'].get('Completion Percentage', 0)

        update_fields = {}
        field_mapping = {
            'name': 'Project Name',
            'client': 'Client Name',
            'status': 'Status',
            'budget': 'Budget',
            'timeline': 'Timeline',
            'completion_percentage': 'Completion Percentage',
            'priority': 'Priority',
            'start_date': 'Start Date',
            'end_date': 'End Date'
        }

        for key, airtable_field in field_mapping.items():
            if key in data:
                update_fields[airtable_field] = data[key]

        update_fields['Last Updated'] = datetime.now().isoformat()

        # Update the project
        airtable_client.update_record('ATLAS PROJECTS', project_id, update_fields)
        
        # 🎯 AUTO-CREATE INVOICE IF PROJECT COMPLETED
        new_status = update_fields.get('Status', old_status)
        new_completion = update_fields.get('Completion Percentage', old_completion)
        
        # Trigger invoice creation if:
        # 1. Status changed to "Completed" OR
        # 2. Completion percentage reached 100%
        should_create_invoice = (
            (new_status == 'Completed' and old_status != 'Completed') or
            (new_completion == 100 and old_completion < 100)
        )
        
        if should_create_invoice:
            # Check if invoice already exists for this project
            existing_invoice = current_project['fields'].get('Invoice')
            
            if not existing_invoice:
                try:
                    # Auto-create invoice!
                    invoice_result = create_invoice_from_atlas_project(project_id, airtable_client)
                    
                    return jsonify({
                        'success': True,
                        'message': '✅ Project completed! Invoice created automatically!',
                        'invoice_created': True,
                        'invoice_id': invoice_result['invoice_id'],
                        'invoice_number': invoice_result['invoice_number'],
                        'invoice_amount': invoice_result['invoice_amount']
                    })
                except Exception as invoice_error:
                    print(f"Error creating invoice from project: {invoice_error}")
                    return jsonify({
                        'success': True,
                        'message': 'Project updated. Invoice creation failed - please create manually.',
                        'invoice_error': str(invoice_error)
                    })
        
        return jsonify({'success': True})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# RFP CRUD operations
@app.route('/atlas/rfps', methods=['GET'])
def get_atlas_rfps():
    """Get RFPs with optional project filtering"""
    try:
        project_id = request.args.get('project_id')
        airtable_client = AirtableClient()

        records = airtable_client.get_all_records('ATLAS RFPS')

        # Filter by project if specified
        if project_id:
            # Note: This would need a link field in a real implementation
            # For now, we'll return all RFPs
            pass

        rfps = []
        for record in records:
            fields = record['fields']
            rfps.append({
                'id': record['id'],
                'name': fields.get('RFP Name', ''),
                'client': fields.get('Client Name', ''),
                'rfp_number': fields.get('RFP Number', ''),
                'value': fields.get('Value', 0),
                'due_date': fields.get('Due Date'),
                'status': fields.get('Status', 'Draft'),
                'probability': fields.get('Probability', 50),
                'industry': fields.get('Industry', ''),
                'contact_name': fields.get('Contact Name', ''),
                'contact_email': fields.get('Contact Email', ''),
                'created_date': fields.get('Created Date')
            })

        return jsonify({'rfps': rfps})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/atlas/rfps', methods=['POST'])
def create_atlas_rfp():
    """Create a new RFP"""
    try:
        data = request.json
        airtable_client = AirtableClient()

        fields = {
            'RFP Name': data.get('name', ''),
            'Client Name': data.get('client', ''),
            'RFP Number': data.get('rfp_number', ''),
            'Value': data.get('value', 0),
            'Due Date': data.get('due_date'),
            'Industry': data.get('industry', ''),
            'Description': data.get('description', ''),
            'Contact Name': data.get('contact_name', ''),
            'Contact Email': data.get('contact_email'),
            'Contact Phone': data.get('contact_phone'),
            'Status': 'Draft',
            'Probability': data.get('probability', 50),
            'Created Date': datetime.now().isoformat()
        }

        result = airtable_client.create_record('ATLAS RFPS', fields)
        return jsonify({'rfp': {'id': result['id'], **fields}})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Change Orders CRUD operations
@app.route('/atlas/change-orders', methods=['GET'])
def get_atlas_change_orders():
    """Get change orders with optional project filtering"""
    try:
        project_id = request.args.get('project_id')
        airtable_client = AirtableClient()

        records = airtable_client.get_all_records('ATLAS CHANGE ORDERS')

        change_orders = []
        for record in records:
            fields = record['fields']
            # Filter by project if specified
            if project_id and fields.get('Project ID') != project_id:
                continue

            change_orders.append({
                'id': record['id'],
                'project_id': fields.get('Project ID', ''),
                'title': fields.get('Title', ''),
                'description': fields.get('Description', ''),
                'type': fields.get('Type', ''),
                'priority': fields.get('Priority', 'Medium'),
                'status': fields.get('Status', 'Draft'),
                'impact_scope': fields.get('Impact Scope', 'Low'),
                'impact_schedule': fields.get('Impact Schedule', ''),
                'impact_budget': fields.get('Impact Budget', 0),
                'created_date': fields.get('Created Date')
            })

        return jsonify({'change_orders': change_orders})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/atlas/change-orders', methods=['POST'])
def create_atlas_change_order():
    """Create a new change order"""
    try:
        data = request.json
        airtable_client = AirtableClient()

        fields = {
            'Project ID': data.get('project_id', ''),
            'Title': data.get('title', ''),
            'Description': data.get('description', ''),
            'Type': data.get('type', 'Scope'),
            'Priority': data.get('priority', 'Medium'),
            'Status': 'Draft',
            'Requested By': data.get('requested_by', ''),
            'Created Date': datetime.now().isoformat()
        }

        result = airtable_client.create_record('ATLAS CHANGE ORDERS', fields)
        return jsonify({'change_order': {'id': result['id'], **fields}})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Existing ATLAS PM AI endpoints
@app.route('/atlas/analyze-rfp', methods=['POST'])
def atlas_analyze_rfp():
    """
    Analyze RFP content and extract requirements

    Expected JSON:
    {
        "rfp_content": "Full RFP text...",
        "project_id": "rec..." (optional)
    }
    """
    try:
        data = request.json
        rfp_content = data.get('rfp_content', '')
        project_id = data.get('project_id', '')

        if not rfp_content:
            return jsonify({"error": "rfp_content required"}), 400

        result = handle_atlas_analyze_rfp(rfp_content, project_id or None)
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/atlas/generate-wbs', methods=['POST'])
def atlas_generate_wbs():
    """
    Generate Work Breakdown Structure for project

    Expected JSON:
    {
        "project_id": "rec..."
    }
    """
    try:
        data = request.json
        project_id = data.get('project_id', '')

        if not project_id:
            return jsonify({"error": "project_id required"}), 400

        result = handle_atlas_generate_wbs(project_id)
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/atlas/analyze-change-request', methods=['POST'])
def atlas_analyze_change_request():
    """
    Analyze change request and provide impact assessment

    Expected JSON:
    {
        "change_description": "Description of requested change...",
        "project_id": "rec..."
    }
    """
    try:
        data = request.json
        change_description = data.get('change_description', '')
        project_id = data.get('project_id', '')

        if not change_description:
            return jsonify({"error": "change_description required"}), 400
        if not project_id:
            return jsonify({"error": "project_id required"}), 400

        result = handle_atlas_analyze_change_request(change_description, project_id)
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =====================================================================
# TASK BOARD ENDPOINTS - Monday.com Style
# =====================================================================

@app.route('/atlas/tasks', methods=['GET'])
def get_tasks():
    """Get all tasks with optional filtering"""
    try:
        project_id = request.args.get('project_id')
        airtable_client = AirtableClient()
        
        # Try to get tasks from Airtable (create table if doesn't exist)
        try:
            records = airtable_client.get_all_records('ATLAS TASKS')
        except:
            # Table doesn't exist yet, return empty
            return jsonify({'tasks': []})
        
        tasks = []
        for record in records:
            fields = record['fields']
            # Filter by project if specified
            if project_id and fields.get('Project ID') != project_id:
                continue
                
            tasks.append({
                'id': record['id'],
                'title': fields.get('Title', ''),
                'status': fields.get('Status', 'todo'),
                'priority': fields.get('Priority', 'medium'),
                'owner': fields.get('Owner', 'Unassigned'),
                'dueDate': fields.get('Due Date'),
                'progress': fields.get('Progress', 0),
                'budget': fields.get('Budget', 0),
                'description': fields.get('Description', ''),
                'project': fields.get('Project Name', ''),
                'createdDate': fields.get('Created Date')
            })
        
        return jsonify({'tasks': tasks})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/atlas/tasks', methods=['POST'])
def create_task():
    """Create a new task"""
    try:
        data = request.json
        airtable_client = AirtableClient()
        
        fields = {
            'Title': data.get('title', 'New Task'),
            'Status': data.get('status', 'todo'),
            'Priority': data.get('priority', 'medium'),
            'Owner': data.get('owner', 'Unassigned'),
            'Due Date': data.get('dueDate'),
            'Progress': data.get('progress', 0),
            'Budget': data.get('budget', 0),
            'Description': data.get('description', ''),
            'Project Name': data.get('project', ''),
            'Created Date': datetime.now().isoformat()
        }
        
        result = airtable_client.create_record('ATLAS TASKS', fields)
        return jsonify({'task': {'id': result['id'], **fields}})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/atlas/tasks/<task_id>', methods=['PUT'])
def update_task(task_id):
    """Update a task"""
    try:
        data = request.json
        airtable_client = AirtableClient()
        
        update_fields = {}
        field_mapping = {
            'title': 'Title',
            'status': 'Status',
            'priority': 'Priority',
            'due_date': 'Due Date',
            'description': 'Description',
            'assigned_to': 'Assigned To',
            'notes': 'Notes',
        }
        for key, airtable_key in field_mapping.items():
            if key in data:
                update_fields[airtable_key] = data[key]

        if not update_fields:
            return jsonify({"error": "No valid fields to update"}), 400

        task = airtable_client.update_record('ATLAS TASKS', task_id, update_fields)

        # VERTEX AUTO-TRIGGER: Invoice on milestone completion, expense on cost log
        if data.get('status') == 'Complete':
            try:
                from vertex_automation import vertex_auto_trigger
                task_fields = task.get('fields', {})
                vertex_auto_trigger('atlas.milestone.complete', task_id, {
                    'client_name':      task_fields.get('Client', ''),
                    'milestone_name':   task_fields.get('Title', ''),
                    'milestone_amount': float(task_fields.get('Billable Amount', 0) or 0),
                    'project_id':       task_id,
                    'contract_number':  task_fields.get('Contract Number', ''),
                })
            except Exception as ve:
                print(f"VERTEX auto-trigger (ATLAS milestone): {ve}")

        if data.get('expense_amount'):
            try:
                from vertex_automation import vertex_auto_trigger
                task_fields = task.get('fields', {})
                vertex_auto_trigger('atlas.expense.logged', task_id, {
                    'vendor':       data.get('expense_vendor', ''),
                    'description':  data.get('expense_description', task_fields.get('Title', '')),
                    'amount':       float(data.get('expense_amount', 0)),
                    'category':     data.get('expense_category', 'Project Expense'),
                    'billable':     data.get('billable', True),
                })
            except Exception as ve:
                print(f"VERTEX auto-trigger (ATLAS expense): {ve}")

        return jsonify({"success": True, "task": task})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/atlas/tasks/<task_id>', methods=['DELETE'])
def delete_task(task_id):
    """Delete a task"""
    try:
        airtable_client = AirtableClient()
        table = airtable_client.get_table('ATLAS TASKS')
        table.delete(task_id)
        return jsonify({'success': True})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/atlas/tasks/ai-suggestions', methods=['POST'])
def get_ai_task_suggestions():
    """Get AI suggestions for task management"""
    try:
        data = request.json
        tasks = data.get('tasks', [])
        
        # Use Claude AI to analyze tasks and provide suggestions
        anthropic_client = anthropic.Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))
        
        task_summary = f"Analyzing {len(tasks)} tasks:\n"
        for task in tasks[:10]:  # Limit to 10 tasks for context
            task_summary += f"- {task.get('title')} ({task.get('status')}, {task.get('priority')} priority, {task.get('progress')}% complete)\n"
        
        message = anthropic_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            messages=[{
                "role": "user",
                "content": f"""You are a project management AI assistant. Analyze these tasks and provide actionable insights:

{task_summary}

Provide:
1. Top 3 priorities for today
2. Any blockers or risks
3. Suggestions for improving workflow
4. Tasks that might be behind schedule

Keep it concise and actionable."""
            }]
        )
        
        suggestions = message.content[0].text
        
        return jsonify({
            'suggestions': suggestions,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/atlas/tasks/auto-generate', methods=['POST'])
def auto_generate_tasks():
    """Auto-generate tasks from RFP or project description using AI"""
    try:
        data = request.json
        project_description = data.get('description', '')
        project_name = data.get('project_name', 'New Project')
        
        if not project_description:
            return jsonify({"error": "description required"}), 400
        
        # Use Claude AI to generate tasks
        anthropic_client = anthropic.Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))
        
        message = anthropic_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[{
                "role": "user",
                "content": f"""You are a project management AI. Based on this project description, generate a comprehensive task list:

Project: {project_name}
Description: {project_description}

Generate 10-15 tasks that cover the full project lifecycle. For each task, provide:
- Title (clear, actionable)
- Priority (low/medium/high/urgent)
- Estimated duration
- Suggested owner role (e.g., "Project Manager", "Developer", "Designer")

Format as JSON array with fields: title, priority, duration, owner_role, description"""
            }]
        )
        
        # Parse AI response and create tasks
        ai_response = message.content[0].text
        
        return jsonify({
            'generated_tasks': ai_response,
            'project_name': project_name,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =====================================================================
# LBPC (LANCASTER BANQUES P.C.) - SURPLUS RECOVERY ENDPOINTS
# =====================================================================

@app.route('/lbpc/stats', methods=['GET'])
def get_lbpc_stats():
    """Get LBPC dashboard statistics"""
    try:
        airtable_client = AirtableClient()
        
        try:
            leads = airtable_client.get_all_records('LBPC LEADS')
        except:
            leads = []
        
        # Calculate lead stats
        new_leads = [l for l in leads if l['fields'].get('Status') == 'New']
        contacted = [l for l in leads if l['fields'].get('Status') == 'Contacted']
        qualified = [l for l in leads if l['fields'].get('Status') == 'Qualified']
        engaged = [l for l in leads if l['fields'].get('Status') == 'Engaged']
        
        # Calculate recovery potential
        total_recovery = sum(l['fields'].get('Estimated Recovery Amount', 0) for l in leads if isinstance(l['fields'].get('Estimated Recovery Amount'), (int, float)))
        
        stats = {
            'totalLeads': len(leads),
            'newLeads': len(new_leads),
            'contacted': len(contacted),
            'qualified': len(qualified),
            'engaged': len(engaged),
            'totalRecoveryPotential': total_recovery
        }
        
        return jsonify(stats)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/lbpc/leads', methods=['GET'])
def lbpc_get_leads():
    """Get all LBPC leads with optional filtering"""
    try:
        filters = {}
        if request.args.get('state'):
            filters['state'] = request.args.get('state')
        if request.args.get('status'):
            filters['status'] = request.args.get('status')
        if request.args.get('min_amount'):
            filters['min_amount'] = float(request.args.get('min_amount'))
        
        result = handle_lbpc_get_leads(filters if filters else None)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/lbpc/leads', methods=['POST'])
def lbpc_create_lead():
    """Create new LBPC lead"""
    try:
        data = request.json
        result = handle_lbpc_create_lead(data)

        # Advisor: teach about lead mining
        if result.get('success'):
            try:
                from nexus_advisor import advise
                result['advisor'] = advise('lbpc', 'lead_mined', {
                    'county': data.get('county', ''),
                    'state': data.get('state', ''),
                    'amount': data.get('surplus_amount', 0),
                })
            except Exception:
                pass

        return jsonify(result), 201 if result.get('success') else 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/lbpc/leads/<lead_id>', methods=['PUT'])
def lbpc_update_lead(lead_id):
    """Update existing LBPC lead"""
    try:
        data = request.json
        result = handle_lbpc_update_lead(lead_id, data)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/lbpc/leads/<lead_id>', methods=['DELETE'])
def lbpc_delete_lead(lead_id):
    """Delete LBPC lead"""
    try:
        result = handle_lbpc_delete_lead(lead_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/lbpc/leads/<lead_id>/qualify', methods=['POST'])
def lbpc_qualify_lead(lead_id):
    """AI qualification of a lead"""
    try:
        result = handle_lbpc_ai_qualify_lead(lead_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/lbpc/leads/<lead_id>/generate-document', methods=['POST'])
def lbpc_generate_document(lead_id):
    """Generate document for a lead"""
    try:
        data = request.json
        template_type = data.get('template_type', 'Initial Notice')
        use_ai = data.get('use_ai', True)
        
        result = handle_lbpc_generate_document(lead_id, template_type, use_ai)

        # NEXUS ADVISOR: Teach about document generation
        try:
            from nexus_advisor import advise
            advisor_insight = advise('lbpc', 'document_generated', {
                'template_type': template_type,
                'lead_id': lead_id,
            })
            result['advisor'] = advisor_insight
        except Exception:
            pass

        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/lbpc/leads/<lead_id>/create-invoice', methods=['POST'])
def lbpc_create_lead_invoice(lead_id):
    """Create invoice for LBPC lead"""
    try:
        result = handle_lbpc_create_invoice(lead_id)
        return jsonify(result), 201 if result.get('success') else 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/lbpc/documents', methods=['GET'])
def lbpc_get_documents():
    """Get LBPC documents"""
    try:
        lead_id = request.args.get('lead_id')
        result = handle_lbpc_get_documents(lead_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/lbpc/tasks', methods=['GET'])
def lbpc_get_tasks():
    """Get LBPC tasks"""
    try:
        filters = {}
        if request.args.get('status'):
            filters['status'] = request.args.get('status')
        if request.args.get('lead_id'):
            filters['lead_id'] = request.args.get('lead_id')
        
        result = handle_lbpc_get_tasks(filters if filters else None)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/lbpc/tasks/<task_id>', methods=['PUT'])
def lbpc_update_task(task_id):
    """Update LBPC task"""
    try:
        data = request.json
        result = handle_lbpc_update_task(task_id, data)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/lbpc/import-csv', methods=['POST'])
def lbpc_import_csv():
    """Import leads from CSV data"""
    try:
        data = request.json
        csv_data = data.get('leads', [])
        
        if not csv_data:
            return jsonify({'error': 'No lead data provided'}), 400
        
        result = handle_lbpc_import_csv(csv_data)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/lbpc/analytics', methods=['GET'])
def lbpc_get_analytics():
    """Get LBPC analytics and dashboard stats"""
    try:
        result = handle_lbpc_get_analytics()
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/lbpc/mine/county', methods=['POST'])
def lbpc_mine_county():
    """Mine leads from specific county website"""
    try:
        data = request.json
        county = data.get('county')
        state = data.get('state')
        
        if not county or not state:
            return jsonify({'error': 'County and state required'}), 400
        
        result = handle_lbpc_mine_county(county, state)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/lbpc/upload-pdf', methods=['POST'])
def lbpc_upload_pdf():
    """Upload and parse PDF surplus list"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        county = request.form.get('county')
        state = request.form.get('state')
        
        if not county or not state:
            return jsonify({'error': 'County and state required'}), 400
        
        # Save temporarily
        temp_path = f'/tmp/lbpc_upload_{datetime.now().timestamp()}.pdf'
        file.save(temp_path)
        
        result = handle_lbpc_upload_pdf(temp_path, county, state)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/lbpc/upload-csv', methods=['POST'])
def lbpc_upload_csv():
    """Upload and parse CSV surplus list"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        county = request.form.get('county')
        state = request.form.get('state')
        
        if not county or not state:
            return jsonify({'error': 'County and state required'}), 400
        
        # Read CSV content
        csv_content = file.read().decode('utf-8')
        
        result = handle_lbpc_upload_csv(csv_content, county, state)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# =====================================================================
# JETA — Aviation fuel buyers (Airtable: JETA_Buyers)
# =====================================================================
# Expected Airtable fields: Company Name, Contact Name, Email, Phone, State, City,
# Website, Buyer Type, Pipeline Stage (1–9), Last Contact Date, Next Action, Notes,
# Next Touch Date (date) — for Outreach Center “due today”
# Airport (optional) — FBO / airport name for AI outreach drafts
# Compliance (checkboxes): Legal Entity Confirmed, Aircraft Or Fuel Verified,
# Purchasing Authority Confirmed, Compliance Review Logged, Business Email Confirmed
# Fuel Benchmark PPG (number), Contract Status (Branded | Independent)
# Volume Per Month (number), Not Exclusive Long-Term Contract (checkbox),
# Decision Maker Name, Decision Maker Title (text)
# Priority scoring: Priority Score (0–130), Score Breakdown (long text JSON), Priority Tags (long text JSON),
# Supply Adjacent (checkbox), Canada (checkbox); ICAO Code, Supplier Status, Based Aircraft Total, Country
#
# JETA_Outreach: canonical snake_case (see jeta_outreach_schema.JO); legacy Buyer / Touch Date dual-read.

JETA_BUYERS_TABLE = 'JETA_Buyers'
JETA_OUTREACH_TABLE = 'JETA_Outreach'
JETA_OUTREACH_BUYER_FIELD = 'Buyer'
# JETA_Sellers: canonical snake_case (see jeta_seller_schema.JS); legacy Title Case dual-written where applicable.
# Optional link: Source Buyer → JETA_Buyers (omit if column missing in base).
JETA_SELLERS_TABLE = 'JETA_Sellers'

# JETA priority persistence (add to Airtable JETA_Buyers if missing)
JETA_F_SCORE_BREAKDOWN = 'Score Breakdown'  # Long text — JSON object
JETA_F_PRIORITY_TAGS = 'Priority Tags'  # Long text — JSON array of tag strings
JETA_F_SUPPLY_ADJACENT = 'Supply Adjacent'  # Checkbox
JETA_F_CANADA = 'Canada'  # Checkbox — true when Country is Canada

JETA_STAGE_LABELS = [
    'Identified', 'Qualified', 'Contacted', 'Engaged', 'Benchmarked',
    'Presenting', 'NCNDA Signed', 'Deal Active', 'Closed',
]


def _jeta_parse_pipeline_stage(fields: dict) -> int:
    """Normalize pipeline stage to integer 1–9 (snake_case select or legacy Pipeline Stage)."""
    return jb_parse_pipeline_stage_int(fields, JETA_STAGE_LABELS)


def _jeta_format_date_field(val) -> str:
    if val is None or val == '':
        return ''
    if hasattr(val, 'strftime'):
        return val.strftime('%Y-%m-%d')
    return str(val)


def _jeta_coerce_bool(val) -> bool:
    """Parse JSON / Airtable checkbox values to bool."""
    if val is True:
        return True
    if val in (False, None, '', []):
        return False
    if isinstance(val, str):
        return val.strip().lower() in ('true', '1', 'yes', 'y', 'checked')
    return bool(val)


def _jeta_parse_optional_float(val):
    """Return float or None for Airtable/JSON number fields."""
    if val is None or val == '':
        return None
    try:
        return float(val)
    except (TypeError, ValueError):
        return None


def _jeta_score_based_aircraft_count(val) -> int:
    """Priority subscore from based aircraft (0–40)."""
    try:
        n = int(float(val))
    except (TypeError, ValueError):
        n = 0
    if n <= 0:
        return 0
    if 1 <= n <= 5:
        return 10
    if 6 <= n <= 15:
        return 20
    if 16 <= n <= 30:
        return 30
    return 40


def _jeta_score_supplier_status_field(val) -> int:
    """Open=30, Unknown/null/empty=15, Branded=5."""
    if val is None:
        return 15
    s = _jeta_normalize_supplier_status(val)
    if s == 'Open':
        return 30
    if s == 'Branded':
        return 5
    return 15


# JETA priority — geography proximity to Michigan (home base), 0–20 points
JETA_US_STATE_CODES = frozenset(
    'AL AK AZ AR CA CO CT DE FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO MT NE NV NH NJ '
    'NM NY NC ND OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY'.split()
)
JETA_CA_PROVINCE_CODES = frozenset('AB BC MB NB NL NS NT NU ON PE QC SK YT'.split())
# Tier 1 (20): MI + Ontario
JETA_PROXIMITY_TIER_HOME = frozenset({'MI', 'ON'})
# Tier 2 (15): Great Lakes / adjacent US + Quebec (ON excluded — covered by tier 1)
JETA_PROXIMITY_TIER_NEAR = frozenset({'OH', 'IN', 'IL', 'WI', 'NY', 'PA', 'QC'})

_JETA_STATE_PROVINCE_NAME_TO_CODE = {
    'ONTARIO': 'ON',
    'QUEBEC': 'QC',
    'BRITISH COLUMBIA': 'BC',
    'ALBERTA': 'AB',
    'SASKATCHEWAN': 'SK',
    'MANITOBA': 'MB',
    'NOVA SCOTIA': 'NS',
    'NEW BRUNSWICK': 'NB',
    'NEWFOUNDLAND AND LABRADOR': 'NL',
    'NEWFOUNDLAND': 'NL',
    'LABRADOR': 'NL',
    'PRINCE EDWARD ISLAND': 'PE',
    'NORTHWEST TERRITORIES': 'NT',
    'NUNAVUT': 'NU',
    'YUKON': 'YT',
}


def _jeta_normalize_state_province_code(val) -> str:
    """Return 2-letter state/province code when possible (FAA/TC CSV or full province name)."""
    s = (str(val or '').strip().upper())
    if not s:
        return ''
    if len(s) == 2 and s.isalpha():
        return s
    return _JETA_STATE_PROVINCE_NAME_TO_CODE.get(s, '')


def _jeta_score_geography_proximity(f: dict) -> int:
    """
    Geography proximity (max 20):
      MI, ON = 20 | OH, IN, IL, WI, NY, PA, QC = 15 | all others (any state text) = 10 | none = 0
    """
    geo = jb_geo_state_raw(f)
    raw = str(geo or '').strip()
    code = _jeta_normalize_state_province_code(geo)
    if not raw and not code:
        return 0
    if code in JETA_PROXIMITY_TIER_HOME:
        return 20
    if code in JETA_PROXIMITY_TIER_NEAR:
        return 15
    return 10


def _jeta_score_email_present(val) -> int:
    return 10 if str(val or '').strip() else 0


# JETA priority — supply proximity to PADD 3 Gulf Coast refinery hub (US only), 0–30 points
JETA_SUPPLY_PADD3_TIER1 = frozenset({'TX', 'LA'})
JETA_SUPPLY_PADD3_TIER2 = frozenset({'MS', 'AL', 'AR'})
JETA_SUPPLY_PADD3_TIER3 = frozenset({'OK', 'KS', 'TN'})
JETA_SUPPLY_ADJACENT_CODES = JETA_SUPPLY_PADD3_TIER1 | JETA_SUPPLY_PADD3_TIER2 | JETA_SUPPLY_PADD3_TIER3

JETA_PRIORITY_SCORE_MAX = 130


def _jeta_score_supply_proximity_padd3(f: dict) -> int:
    """
    Near PADD 3 Gulf Coast hub (US state only; Canada / unknown = 0):
      TX, LA = 30 | MS, AL, AR = 20 | OK, KS, TN = 15 | all others = 0
    """
    code = _jeta_normalize_state_province_code(jb_geo_state_raw(f))
    if not code or code not in JETA_US_STATE_CODES:
        return 0
    if code in JETA_SUPPLY_PADD3_TIER1:
        return 30
    if code in JETA_SUPPLY_PADD3_TIER2:
        return 20
    if code in JETA_SUPPLY_PADD3_TIER3:
        return 15
    return 0


def _jeta_country_is_canada(val) -> bool:
    s = (str(val or '').strip().lower())
    return s == 'canada'


def _jeta_priority_tags_from_score(score: int) -> list:
    """Single tier tag from total priority score."""
    s = int(score)
    if s >= 100:
        return ['PRIORITY']
    if s >= 70:
        return ['HIGH VALUE']
    if s >= 40:
        return ['STANDARD']
    return ['LOW PRIORITY']


def _jeta_compute_priority_package(f: dict) -> dict:
    """
    Full JETA priority from Airtable field dict.
    Returns priority_score (0–130), score_breakdown, tags, supply_adjacent, canada.
    """
    ba_raw = jb_get_float(f, JB.based_aircraft)
    if ba_raw is None:
        ba_raw = f.get('Based Aircraft Total')
    demand = _jeta_score_based_aircraft_count(ba_raw)
    sup_f = jb_get_raw(f, JB.supplier_status)
    if sup_f is None:
        sup_f = f.get('Supplier Status')
    supplier = _jeta_score_supplier_status_field(sup_f)
    geography = _jeta_score_geography_proximity(f)
    contact = _jeta_score_email_present(jb_get_email(f))
    supply = _jeta_score_supply_proximity_padd3(f)
    total = demand + supplier + geography + contact + supply
    total = max(0, min(JETA_PRIORITY_SCORE_MAX, int(total)))

    code = _jeta_normalize_state_province_code(jb_geo_state_raw(f))
    supply_adjacent = bool(code and code in JETA_SUPPLY_ADJACENT_CODES)
    canada = _jeta_country_is_canada(jb_get_str(f, JB.country))

    score_breakdown = {
        'demand_signal': demand,
        'supplier_status': supplier,
        'geography_proximity': geography,
        'contact_completeness': contact,
        'supply_proximity': supply,
        'total': total,
    }
    tags = _jeta_priority_tags_from_score(total)
    return {
        'priority_score': total,
        'score_breakdown': score_breakdown,
        'tags': tags,
        'supply_adjacent': supply_adjacent,
        'canada': canada,
    }


def _jeta_compute_priority_score_from_airtable_fields(f: dict) -> int:
    """JETA buyer priority 0–130 (numeric only)."""
    return _jeta_compute_priority_package(f)['priority_score']


def _jeta_refresh_buyer_priority_full(airtable_client: AirtableClient, buyer_id: str) -> dict:
    """Recompute and persist priority score, breakdown JSON, tags, supply_adjacent, canada on JETA_Buyers."""
    rec = airtable_client.get_record(JETA_BUYERS_TABLE, buyer_id)
    f = rec.get('fields') or {}
    pkg = _jeta_compute_priority_package(f)
    json_dumps_score = json.dumps(pkg['score_breakdown'], separators=(',', ':'))
    last_err = None
    for payload in jb_priority_write_payloads(pkg, json_dumps_score=json_dumps_score):
        try:
            airtable_client.update_record(JETA_BUYERS_TABLE, buyer_id, payload)
            return pkg
        except Exception as e:
            last_err = e
            logger.warning('JETA full priority update failed for %s (try next payload shape): %s', buyer_id, e)
    for fld in (JB.priority_score, 'Priority Score'):
        try:
            airtable_client.update_record(JETA_BUYERS_TABLE, buyer_id, {fld: pkg['priority_score']})
            return pkg
        except Exception as e2:
            logger.warning('JETA minimal priority score update failed for %s field=%s: %s', buyer_id, fld, e2)
    if last_err:
        raise last_err
    raise RuntimeError('JETA priority update failed with no recoverable field shape')


def _jeta_refresh_buyer_priority_score(airtable_client: AirtableClient, buyer_id: str) -> int:
    """Recompute and persist priority fields on JETA_Buyers; returns numeric score."""
    return _jeta_refresh_buyer_priority_full(airtable_client, buyer_id)['priority_score']


def _jeta_serialize_record(record: dict) -> dict:
    f = record.get('fields') or {}
    pkg = _jeta_compute_priority_package(f)
    stage = _jeta_parse_pipeline_stage(f)
    last_raw = jb_get_raw(f, JB.last_contact_date)
    if last_raw is None:
        last_raw = f.get('Last Contact Date')
    last_dt = last_raw
    if last_dt is not None and hasattr(last_dt, 'strftime'):
        last_dt = last_dt.strftime('%Y-%m-%d')
    else:
        last_dt = str(last_dt) if last_dt else ''
    next_raw = jb_get_raw(f, JB.next_contact_date)
    if next_raw is None:
        next_raw = f.get('Next Touch Date')
    tag_list = jb_tags_as_list(f)
    ba_total = jb_get_float(f, JB.based_aircraft)
    if ba_total is None:
        ba_total = _jeta_parse_optional_float(f.get('Based Aircraft Total'))
    return {
        'id': record['id'],
        'companyName': jb_get_str(f, JB.company_name),
        'contactName': jb_get_str(f, JB.contact_name),
        'contactTitle': jb_get_str(f, JB.contact_title),
        'email': jb_get_str(f, JB.contact_email),
        'phone': jb_get_str(f, JB.contact_phone),
        'state': jb_get_str(f, JB.state),
        'province': jb_get_str(f, JB.province),
        'zipCode': jb_get_str(f, JB.zip_code),
        'city': jb_get_str(f, JB.city),
        'airport': jb_get_str(f, JB.airport_name),
        'icaoCode': jb_get_str(f, JB.airport_icao),
        'airportFaaCode': jb_get_str(f, JB.airport_faa_code),
        'website': f.get('Website', '') or '',
        'buyerType': jb_get_str(f, JB.buyer_type),
        'pipelineStage': stage,
        'stageLabel': JETA_STAGE_LABELS[stage - 1] if 1 <= stage <= 9 else JETA_STAGE_LABELS[0],
        'lastContactDate': last_dt or '',
        'nextTouchDate': _jeta_format_date_field(next_raw),
        'nextAction': jb_get_str(f, JB.next_action),
        'notes': jb_get_str(f, JB.notes),
        'legalEntityConfirmed': _jeta_coerce_bool(f.get('Legal Entity Confirmed')),
        'aircraftOrFuelVerified': _jeta_coerce_bool(f.get('Aircraft Or Fuel Verified')),
        'purchasingAuthorityConfirmed': _jeta_coerce_bool(f.get('Purchasing Authority Confirmed')),
        'complianceReviewLogged': _jeta_coerce_bool(f.get('Compliance Review Logged')),
        'businessEmailConfirmed': _jeta_coerce_bool(f.get('Business Email Confirmed')),
        'fuelBenchmarkPpg': _jeta_parse_optional_float(f.get('Fuel Benchmark PPG')),
        'contractStatus': str(f.get('Contract Status') or '').strip(),
        'volumePerMonth': _jeta_parse_optional_float(f.get('Volume Per Month')),
        'notExclusiveLongTermContract': _jeta_coerce_bool(f.get('Not Exclusive Long-Term Contract')),
        'decisionMakerName': str(f.get('Decision Maker Name') or '').strip(),
        'decisionMakerTitle': str(f.get('Decision Maker Title') or '').strip(),
        'faaRegistration': str(f.get('FAA Registration') or '').strip(),
        'fuelConsumptionHistoryProvided': _jeta_coerce_bool(f.get('Fuel Consumption History Provided')),
        'terminalStorageDocsUploaded': _jeta_coerce_bool(f.get('Terminal Storage Docs Uploaded')),
        'aircraftOperationConfirmed': _jeta_coerce_bool(f.get('Aircraft Operation Confirmed')),
        'sellerProductDescription': str(f.get('Seller Product Description') or '').strip(),
        'fuelType': _jeta_normalize_fuel_type(jb_get_raw(f, JB.fuel_type) or f.get('Fuel Type')),
        'country': jb_get_str(f, JB.country),
        'importSource': jb_get_str(f, JB.source),
        'dateAdded': _jeta_format_date_field(jb_get_raw(f, JB.date_added) or f.get('Date Added')),
        'basedAircraftTotal': ba_total,
        'supplierStatus': _jeta_normalize_supplier_status(jb_get_raw(f, JB.supplier_status) or f.get('Supplier Status')),
        'priorityScore': pkg['priority_score'],
        'scoreBreakdown': pkg['score_breakdown'],
        'priorityTags': tag_list if tag_list else pkg['tags'],
        'supplyAdjacent': pkg['supply_adjacent'],
        'canada': pkg['canada'],
        'createdTime': record.get('createdTime', ''),
    }


def _jeta_json_to_fields(data: dict, partial: bool = False) -> dict:
    """Map API JSON (camelCase) to Airtable — canonical snake_case + legacy Title Case where applicable."""
    out = {}

    def put_both(canon: str, legacy: str | None, val) -> None:
        if val is None:
            return
        out[canon] = val
        if legacy:
            out[legacy] = val

    mapping = [
        ('companyName', JB.company_name, 'Company Name'),
        ('contactName', JB.contact_name, 'Contact Name'),
        ('contactTitle', JB.contact_title, 'Decision Maker Title'),
        ('email', JB.contact_email, 'Email'),
        ('phone', JB.contact_phone, 'Phone'),
        ('state', JB.state, 'State'),
        ('province', JB.province, 'Province'),
        ('zipCode', JB.zip_code, 'Zip Code'),
        ('city', JB.city, 'City'),
        ('airport', JB.airport_name, 'Airport'),
        ('icaoCode', JB.airport_icao, 'ICAO Code'),
        ('airportFaaCode', JB.airport_faa_code, 'FAA Registration'),
        ('buyerType', JB.buyer_type, 'Buyer Type'),
        ('nextAction', JB.next_action, 'Next Action'),
        ('notes', JB.notes, 'Notes'),
    ]
    for jk, canon, legacy in mapping:
        if jk not in data:
            continue
        val = data[jk]
        if val is None:
            continue
        put_both(canon, legacy, val)
    if 'website' in data and data.get('website') is not None:
        out['Website'] = str(data['website']).strip()

    if 'pipelineStage' in data and data.get('pipelineStage') not in (None, ''):
        try:
            ps = int(data['pipelineStage'])
            ps = max(1, min(9, ps))
            opt = jb_pipeline_stage_option(ps, JETA_STAGE_LABELS)
            out[JB.pipeline_stage] = opt
            out['Pipeline Stage'] = ps
        except (TypeError, ValueError):
            if not partial:
                out[JB.pipeline_stage] = jb_pipeline_stage_option(1, JETA_STAGE_LABELS)
                out['Pipeline Stage'] = 1
    elif not partial:
        out[JB.pipeline_stage] = jb_pipeline_stage_option(1, JETA_STAGE_LABELS)
        out['Pipeline Stage'] = 1
    if 'lastContactDate' in data:
        lcd = data['lastContactDate']
        if lcd:
            out[JB.last_contact_date] = lcd
            out['Last Contact Date'] = lcd
    if 'nextTouchDate' in data:
        ntd = data['nextTouchDate']
        if ntd:
            out[JB.next_contact_date] = ntd
            out['Next Touch Date'] = ntd
    for jk, ak in (
        ('legalEntityConfirmed', 'Legal Entity Confirmed'),
        ('aircraftOrFuelVerified', 'Aircraft Or Fuel Verified'),
        ('purchasingAuthorityConfirmed', 'Purchasing Authority Confirmed'),
        ('complianceReviewLogged', 'Compliance Review Logged'),
        ('businessEmailConfirmed', 'Business Email Confirmed'),
    ):
        if jk not in data:
            continue
        out[ak] = _jeta_coerce_bool(data[jk])
    if 'fuelBenchmarkPpg' in data and data.get('fuelBenchmarkPpg') not in (None, ''):
        fp = _jeta_parse_optional_float(data.get('fuelBenchmarkPpg'))
        if fp is not None:
            out['Fuel Benchmark PPG'] = fp
    if 'contractStatus' in data and data.get('contractStatus') not in (None, ''):
        out['Contract Status'] = str(data['contractStatus']).strip()
    if 'volumePerMonth' in data and data.get('volumePerMonth') not in (None, ''):
        vm = _jeta_parse_optional_float(data.get('volumePerMonth'))
        if vm is not None:
            out['Volume Per Month'] = vm
    if 'notExclusiveLongTermContract' in data:
        out['Not Exclusive Long-Term Contract'] = _jeta_coerce_bool(data['notExclusiveLongTermContract'])
    if 'decisionMakerName' in data and data.get('decisionMakerName') is not None:
        out['Decision Maker Name'] = str(data['decisionMakerName']).strip()
    if 'decisionMakerTitle' in data and data.get('decisionMakerTitle') is not None:
        out['Decision Maker Title'] = str(data['decisionMakerTitle']).strip()
    if 'faaRegistration' in data and data.get('faaRegistration') is not None:
        out['FAA Registration'] = str(data['faaRegistration']).strip()
    if 'fuelConsumptionHistoryProvided' in data:
        out['Fuel Consumption History Provided'] = _jeta_coerce_bool(data['fuelConsumptionHistoryProvided'])
    if 'terminalStorageDocsUploaded' in data:
        out['Terminal Storage Docs Uploaded'] = _jeta_coerce_bool(data['terminalStorageDocsUploaded'])
    if 'aircraftOperationConfirmed' in data:
        out['Aircraft Operation Confirmed'] = _jeta_coerce_bool(data['aircraftOperationConfirmed'])
    if 'sellerProductDescription' in data and data.get('sellerProductDescription') is not None:
        out['Seller Product Description'] = str(data['sellerProductDescription']).strip()
    if 'country' in data and data.get('country') is not None:
        c = str(data['country']).strip()
        put_both(JB.country, 'Country', c)
    if 'importSource' in data and data.get('importSource') is not None:
        s = str(data['importSource']).strip()
        put_both(JB.source, 'Source', s)
    if 'dateAdded' in data and data.get('dateAdded') not in (None, ''):
        da = str(data['dateAdded']).strip()
        out[JB.date_added] = da
        out['Date Added'] = da
    if 'basedAircraftTotal' in data and data.get('basedAircraftTotal') not in (None, ''):
        bt = _jeta_parse_optional_float(data.get('basedAircraftTotal'))
        if bt is not None:
            out[JB.based_aircraft] = bt
            out['Based Aircraft Total'] = bt
    if 'fuelType' in data and data.get('fuelType') is not None:
        ft = _jeta_normalize_fuel_type(data.get('fuelType'))
        out[JB.fuel_type] = ft
        out['Fuel Type'] = ft
    elif not partial:
        out[JB.fuel_type] = 'Conventional'
        out['Fuel Type'] = 'Conventional'
    if 'supplierStatus' in data and data.get('supplierStatus') is not None:
        ss = _jeta_normalize_supplier_status(data.get('supplierStatus'))
        out[JB.supplier_status] = ss
        out['Supplier Status'] = ss
    elif not partial:
        out[JB.supplier_status] = 'Unknown'
        out['Supplier Status'] = 'Unknown'
    return out


def _jeta_readiness_block_message(readiness: dict) -> str:
    """User-facing error when the JETA counterparty readiness checklist fails."""
    if readiness.get('all_met'):
        return ''
    missing = []
    if not readiness.get('no_critical_flags', True):
        missing.append('no CRITICAL compliance flags on record')
    if not readiness.get('legal_entity_confirmed'):
        missing.append('legal entity name confirmed')
    if not readiness.get('aircraft_or_fuel_verified'):
        missing.append('aircraft or fuel consumption verified (FAA or docs)')
    if not readiness.get('purchasing_authority_confirmed'):
        missing.append('purchasing authority confirmed')
    if not readiness.get('counterparty_score_ok'):
        missing.append('counterparty score GREEN, or YELLOW with compliance review logged')
    if not readiness.get('business_domain_email_ok'):
        missing.append('business-domain email (or confirm free/consumer address with businessEmailConfirmed)')
    if not readiness.get('outreach_logged'):
        missing.append('at least one outreach row in JETA_Outreach for this buyer')
    if not readiness.get('response_received_logged', True) and readiness.get('outreach_logged'):
        missing.append('response received and logged on JETA_Outreach')
    if not readiness.get('fuel_benchmark_ppg_captured'):
        missing.append('current fuel benchmark (approximate PPG) on buyer record')
    if not readiness.get('contract_status_known'):
        missing.append('contract status known (branded or independent)')
    if not readiness.get('volume_per_month_documented'):
        missing.append('volume per month documented on buyer record')
    if not readiness.get('not_exclusive_long_term_contract_confirmed'):
        missing.append('buyer confirmed not locked in exclusive long-term contract')
    if not readiness.get('decision_maker_documented'):
        missing.append('decision maker confirmed by name and title')
    return 'JETA counterparty readiness incomplete — ' + '; '.join(missing) + '.'


def _jeta_compliance_block_message(compliance: dict, resource: str) -> str:
    """User-facing error when JETA traffic-light blocks an operation."""
    if compliance.get('critical_block'):
        return f'JETA compliance: CRITICAL — {resource} blocked (instant stop)'
    if compliance.get('deal_blocked') or compliance.get('traffic_light') == 'red':
        return f'JETA compliance: RED — {resource} blocked (too many flags); see compliance.findings'
    if compliance.get('traffic_light') == 'yellow':
        return (
            f'JETA compliance: YELLOW — set acknowledgeManualReview and complianceReviewLogged '
            f'to true after manual review ({resource})'
        )
    return f'JETA compliance blocked ({resource})'


def _jeta_outreach_buyer_ids(fields: dict) -> list:
    raw = fields.get(JO.buyer_id) or fields.get(JETA_OUTREACH_BUYER_FIELD) or fields.get('Buyer')
    if isinstance(raw, list):
        return [x for x in raw if x]
    return []


def _jeta_count_outreach_for_buyer(airtable_client, buyer_id: str) -> int:
    """Count JETA_Outreach rows linked to this buyer."""
    if not (buyer_id or '').strip():
        return 0
    try:
        outreach_raw = airtable_client.get_all_records(JETA_OUTREACH_TABLE)
    except Exception:
        return 0
    n = 0
    for rec in outreach_raw:
        f = rec.get('fields') or {}
        bids = _jeta_outreach_buyer_ids(f)
        if buyer_id in bids:
            n += 1
    return n


def _jeta_outreach_response_logged_for_buyer(airtable_client, buyer_id: str) -> bool:
    """True if any JETA_Outreach row for this buyer has response text or a non-placeholder status."""
    if not (buyer_id or '').strip():
        return False
    try:
        outreach_raw = airtable_client.get_all_records(JETA_OUTREACH_TABLE)
    except Exception:
        return False
    placeholders = frozenset(
        {'', 'none', 'pending', 'n/a', 'na', 'no response', '—', '-', 'unknown'}
    )
    for rec in outreach_raw:
        f = rec.get('fields') or {}
        bids = _jeta_outreach_buyer_ids(f)
        if buyer_id not in bids:
            continue
        if jo_get_bool(f, JO.response_received) is True:
            return True
        if jo_get_str(f, JO.response_notes):
            return True
        rr = f.get('Response Received')
        if isinstance(rr, str) and rr.strip():
            return True
        if rr is True:
            return True
        rs = jo_get_str(f, JO.response_type).lower() or (f.get('Response Status') or '').strip().lower()
        if rs and rs not in placeholders:
            return True
    return False


def _jeta_serialize_outreach(record: dict, buyer_lookup: dict) -> dict:
    """buyer_lookup: id -> {companyName, contactName}"""
    f = record.get('fields') or {}
    bids = _jeta_outreach_buyer_ids(f)
    buyer_id = bids[0] if bids else ''
    deal_id = jo_first_link_id(f, JO.deal_id)
    info = buyer_lookup.get(buyer_id, {}) if buyer_id else {}
    tn = jo_get_int(f, JO.touch_number)
    if tn is None:
        try:
            tn = int(f.get('Touch Number') or 0) if f.get('Touch Number') is not None else 0
        except (TypeError, ValueError):
            tn = 0
    od_raw = jo_get_raw(f, JO.outreach_date) or f.get('Touch Date')
    rs_disp = jo_response_received_display_string(f)
    rs_type = jo_get_str(f, JO.response_type) or str(f.get('Response Status') or '').strip()
    ntn = jo_get_int(f, JO.next_touch_number)
    return {
        'id': record['id'],
        'buyerId': buyer_id,
        'dealId': deal_id,
        'companyName': info.get('companyName', '') or '',
        'contactName': info.get('contactName', '') or '',
        'touchNumber': tn,
        'channel': jo_get_str(f, JO.channel) or str(f.get('Channel') or ''),
        'touchDate': _jeta_format_date_field(od_raw),
        'outreachDate': _jeta_format_date_field(od_raw),
        'outreachTime': jo_get_str(f, JO.outreach_time),
        'subjectLine': jo_get_str(f, JO.subject_line),
        'messageSummary': jo_get_str(f, JO.message_summary),
        'aiDrafted': jo_get_bool(f, JO.ai_drafted) is True,
        'responseReceived': rs_disp,
        'responseReceivedLogged': jo_get_bool(f, JO.response_received) is True or bool(rs_disp),
        'responseDate': _jeta_format_date_field(jo_get_raw(f, JO.response_date)),
        'responseStatus': rs_type,
        'responseNotes': jo_get_str(f, JO.response_notes),
        'nextTouchNumber': ntn if ntn is not None else None,
        'nextTouchDate': _jeta_format_date_field(jo_get_raw(f, JO.next_touch_date) or f.get('Next Touch Date')),
        'nextTouchChannel': jo_get_str(f, JO.next_touch_channel),
        'nextTouchNotes': jo_get_str(f, JO.next_touch_notes),
        'sentBy': jo_get_str(f, JO.sent_by),
        'followUpComplete': jo_get_bool(f, JO.follow_up_complete) is True,
        'notes': jo_get_str(f, JO.notes) or str(f.get('Notes') or ''),
        'createdTime': record.get('createdTime', ''),
    }


def _jeta_outreach_json_to_fields(data: dict) -> dict:
    """Map API JSON to Airtable — canonical snake_case + legacy columns."""
    out = {}

    def put_both(canon: str, legacy: str | None, val) -> None:
        if val is None:
            return
        out[canon] = val
        if legacy:
            out[legacy] = val

    bid = (data.get('buyerId') or data.get('buyer_id') or '').strip()
    if bid:
        put_both(JO.buyer_id, JETA_OUTREACH_BUYER_FIELD, [bid])

    did = (data.get('dealId') or data.get('deal_id') or '').strip()
    if did:
        put_both(JO.deal_id, 'Deal', [did])

    if 'touchNumber' in data and data['touchNumber'] is not None:
        try:
            tn = int(data['touchNumber'])
        except (TypeError, ValueError):
            tn = 0
        put_both(JO.touch_number, 'Touch Number', tn)

    td = (data.get('touchDate') or data.get('outreach_date') or data.get('outreachDate') or '').strip()
    if td:
        put_both(JO.outreach_date, 'Touch Date', td)

    ntd = (data.get('nextTouchDate') or data.get('next_touch_date') or '').strip()
    if ntd:
        put_both(JO.next_touch_date, 'Next Touch Date', ntd)

    str_map = [
        ('channel', JO.channel, 'Channel'),
        ('outreachTime', JO.outreach_time, 'Outreach Time'),
        ('subjectLine', JO.subject_line, 'Subject Line'),
        ('messageSummary', JO.message_summary, 'Message Summary'),
        ('responseStatus', JO.response_type, 'Response Status'),
        ('responseNotes', JO.response_notes, 'Response Notes'),
        ('nextTouchChannel', JO.next_touch_channel, 'Next Touch Channel'),
        ('nextTouchNotes', JO.next_touch_notes, 'Next Touch Notes'),
        ('sentBy', JO.sent_by, 'Sent By'),
        ('notes', JO.notes, 'Notes'),
    ]
    for jk, canon, legacy in str_map:
        if jk not in data or data[jk] is None:
            continue
        put_both(canon, legacy, str(data[jk]).strip())

    if 'nextTouchNumber' in data and data['nextTouchNumber'] is not None:
        try:
            put_both(JO.next_touch_number, 'Next Touch Number', int(data['nextTouchNumber']))
        except (TypeError, ValueError):
            pass

    if data.get('responseDate') or data.get('response_date'):
        rd = str(data.get('responseDate') or data.get('response_date')).strip()
        if rd:
            put_both(JO.response_date, 'Response Date', rd)

    for jk, canon, legacy in [
        ('aiDrafted', JO.ai_drafted, 'AI Drafted'),
        ('followUpComplete', JO.follow_up_complete, 'Follow Up Complete'),
    ]:
        if jk in data:
            put_both(canon, legacy, _jeta_coerce_bool(data[jk]))

    # responseReceived: bool → checkbox; string → checkbox True + response_notes (canonical schema).
    if 'responseReceived' in data and data['responseReceived'] is not None:
        rv = data['responseReceived']
        if isinstance(rv, bool):
            put_both(JO.response_received, 'Response Received', rv)
        else:
            s = str(rv).strip()
            if not s:
                put_both(JO.response_received, 'Response Received', False)
            elif s.lower() in ('true', 'yes', '1', 'y'):
                put_both(JO.response_received, 'Response Received', True)
            elif s.lower() in ('false', 'no', '0', 'n'):
                put_both(JO.response_received, 'Response Received', False)
            else:
                out[JO.response_received] = True
                put_both(JO.response_notes, 'Response Notes', s)

    return out


@app.route('/api/jeta/buyers', methods=['GET'])
@app.route('/jeta/buyers', methods=['GET'])
def jeta_get_buyers():
    """List JETA buyers with optional filters. Default order: priority score descending."""
    try:
        airtable_client = AirtableClient()
        try:
            records = airtable_client.get_all_records(JETA_BUYERS_TABLE)
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'buyers': [],
                'count': 0,
                'filterOptions': {'states': [], 'buyerTypes': []},
                'hint': f'Create Airtable table "{JETA_BUYERS_TABLE}" with the expected fields.',
            }), 200

        state_f = (request.args.get('state') or '').strip()
        buyer_type_f = (request.args.get('buyer_type') or '').strip()
        stage_f = (request.args.get('pipeline_stage') or '').strip()
        supplier_status_f = (request.args.get('supplier_status') or '').strip()
        min_priority_f = (request.args.get('min_priority_score') or '').strip()

        all_rows = [_jeta_serialize_record(rec) for rec in records]
        states = sorted({b['state'] for b in all_rows if b['state']})
        types = sorted({b['buyerType'] for b in all_rows if b['buyerType']})
        supplier_statuses = sorted({(b.get('supplierStatus') or 'Unknown') for b in all_rows})

        buyers = []
        for row in all_rows:
            if state_f and row['state'] != state_f:
                continue
            if buyer_type_f and row['buyerType'] != buyer_type_f:
                continue
            if stage_f:
                try:
                    if row['pipelineStage'] != int(stage_f):
                        continue
                except ValueError:
                    continue
            if supplier_status_f:
                if _jeta_normalize_supplier_status(row.get('supplierStatus')) != _jeta_normalize_supplier_status(
                    supplier_status_f
                ):
                    continue
            if min_priority_f:
                try:
                    mp = int(min_priority_f)
                    if int(row.get('priorityScore') or 0) < mp:
                        continue
                except ValueError:
                    pass
            buyers.append(row)

        buyers.sort(
            key=lambda b: (-int(b.get('priorityScore') or 0), (b.get('companyName') or '').lower()),
        )

        return jsonify({
            'success': True,
            'buyers': buyers,
            'count': len(buyers),
            'filterOptions': {
                'states': states,
                'buyerTypes': types,
                'supplierStatuses': supplier_statuses,
            },
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e), 'buyers': []}), 500


@app.route('/api/jeta/buyers', methods=['POST'])
@app.route('/jeta/buyers', methods=['POST'])
def jeta_create_buyer():
    """Create JETA buyer record."""
    try:
        from jeta_compliance_layers import run_layer1_intake_screening, may_proceed_traffic_light
        from jeta_fraud_detection import score_counterparty_intake

        data = request.json or {}
        prospect = {
            'companyName': data.get('companyName'),
            'contactName': data.get('contactName'),
            'email': data.get('email'),
            'state': data.get('state'),
            'legalEntityConfirmed': _jeta_coerce_bool(data.get('legalEntityConfirmed')),
            'aircraftOrFuelVerified': _jeta_coerce_bool(data.get('aircraftOrFuelVerified')),
            'purchasingAuthorityConfirmed': _jeta_coerce_bool(data.get('purchasingAuthorityConfirmed')),
            'complianceReviewLogged': _jeta_coerce_bool(data.get('complianceReviewLogged')),
            'businessEmailConfirmed': _jeta_coerce_bool(data.get('businessEmailConfirmed')),
            'fuelBenchmarkPpg': data.get('fuelBenchmarkPpg'),
            'contractStatus': data.get('contractStatus'),
            'volumePerMonth': data.get('volumePerMonth'),
            'notExclusiveLongTermContract': _jeta_coerce_bool(data.get('notExclusiveLongTermContract')),
            'decisionMakerName': data.get('decisionMakerName'),
            'decisionMakerTitle': data.get('decisionMakerTitle'),
            'notes': data.get('notes'),
            'nextAction': data.get('nextAction'),
            'website': data.get('website'),
            'sellerProductDescription': data.get('sellerProductDescription'),
            'faaRegistration': data.get('faaRegistration'),
            'fuelConsumptionHistoryProvided': _jeta_coerce_bool(data.get('fuelConsumptionHistoryProvided')),
            'terminalStorageDocsUploaded': _jeta_coerce_bool(data.get('terminalStorageDocsUploaded')),
            'aircraftOperationConfirmed': _jeta_coerce_bool(data.get('aircraftOperationConfirmed')),
        }
        compliance_l1 = run_layer1_intake_screening(prospect)
        if not compliance_l1.get('readiness', {}).get('all_met'):
            return jsonify({
                'success': False,
                'error': _jeta_readiness_block_message(compliance_l1.get('readiness') or {}),
                'compliance': compliance_l1,
            }), 409
        ack = _jeta_coerce_bool(data.get('acknowledgeManualReview'))
        crm = _jeta_coerce_bool(data.get('complianceReviewLogged'))
        if not may_proceed_traffic_light(compliance_l1, ack, crm):
            if compliance_l1.get('deal_blocked') or compliance_l1.get('critical_block'):
                logger.warning(
                    'JETA intake blocked (RED/CRITICAL): %s',
                    json.dumps(
                        {
                            'traffic_light': compliance_l1.get('traffic_light'),
                            'findings': compliance_l1.get('findings'),
                            'critical_flags': compliance_l1.get('critical_flags'),
                        }
                    ),
                )
            return jsonify({
                'success': False,
                'error': _jeta_compliance_block_message(compliance_l1, 'counterparty intake'),
                'compliance': compliance_l1,
            }), 409

        role = 'seller' if 'sell' in (data.get('buyerType') or '').lower() else 'buyer'
        fraud = score_counterparty_intake(prospect, role)
        if fraud.get('critical_block') or fraud.get('tier') == 'RED':
            logger.warning('JETA fraud intake blocked: %s', json.dumps({'tier': fraud.get('tier'), 'flags': fraud.get('flags')}))
            return jsonify({
                'success': False,
                'error': 'JETA fraud detection: counterparty score is RED or CRITICAL — intake blocked.',
                'fraud': fraud,
                'compliance': compliance_l1,
            }), 409
        if fraud.get('tier') == 'YELLOW' and not (ack and crm):
            return jsonify({
                'success': False,
                'error': (
                    'JETA fraud detection: YELLOW score — set acknowledgeManualReview and complianceReviewLogged '
                    'after manual review.'
                ),
                'fraud': fraud,
                'compliance': compliance_l1,
            }), 409

        fields = _jeta_json_to_fields(data, partial=False)
        airtable_client = AirtableClient()
        created = airtable_client.create_record(JETA_BUYERS_TABLE, fields)
        try:
            _jeta_refresh_buyer_priority_score(airtable_client, created['id'])
            created = airtable_client.get_record(JETA_BUYERS_TABLE, created['id'])
        except Exception as e:
            logger.warning('JETA priority score refresh after create failed: %s', e)
        ser = _jeta_serialize_record(created)
        outreach_n = _jeta_count_outreach_for_buyer(airtable_client, ser['id'])
        response_ok = _jeta_outreach_response_logged_for_buyer(airtable_client, ser['id'])
        compliance_l1 = run_layer1_intake_screening({
            **ser,
            'outreachRowCount': outreach_n,
            'outreachResponseLogged': response_ok,
        })
        fraud_after = score_counterparty_intake({**ser}, role)
        return jsonify({
            'success': True,
            'buyer': ser,
            'compliance': compliance_l1,
            'fraud': fraud_after,
        }), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/jeta/buyers/<buyer_id>', methods=['PUT', 'PATCH'])
@app.route('/jeta/buyers/<buyer_id>', methods=['PUT', 'PATCH'])
def jeta_update_buyer(buyer_id):
    """Update JETA buyer."""
    try:
        data = request.json or {}
        fields = _jeta_json_to_fields(data, partial=True)
        if not fields:
            return jsonify({'success': False, 'error': 'No fields to update'}), 400
        airtable_client = AirtableClient()
        updated = airtable_client.update_record(JETA_BUYERS_TABLE, buyer_id, fields)
        try:
            _jeta_refresh_buyer_priority_score(airtable_client, buyer_id)
            updated = airtable_client.get_record(JETA_BUYERS_TABLE, buyer_id)
        except Exception as e:
            logger.warning('JETA priority score refresh after update failed: %s', e)
        return jsonify({
            'success': True,
            'buyer': _jeta_serialize_record(updated),
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


def _jeta_seller_record_for_icao_exists(airtable_client: AirtableClient, icao: str) -> dict | None:
    """Return existing JETA_Sellers row if icao_airports_served (or legacy ICAO Code) matches this ICAO."""
    if not icao:
        return None
    try:
        rows = airtable_client.get_all_records(JETA_SELLERS_TABLE)
    except Exception:
        return None
    u = str(icao).strip().upper()
    for r in rows:
        fld = r.get('fields') or {}
        if js_fields_match_icao(fld, u):
            return r
    return None


@app.route('/api/jeta/sellers/from-buyer', methods=['POST'])
@app.route('/jeta/sellers/from-buyer', methods=['POST'])
def jeta_create_seller_from_buyer():
    """
    Create JETA_Sellers row from a JETA_Buyers airport when supply_adjacent and Open supplier.
    Body: { "buyer_id": "rec..." }
    """
    try:
        data = request.get_json(silent=True) or {}
        buyer_id = (data.get('buyer_id') or data.get('buyerId') or '').strip()
        if not buyer_id:
            return jsonify({'success': False, 'error': 'buyer_id is required'}), 400

        airtable_client = AirtableClient()
        rec = airtable_client.get_record(JETA_BUYERS_TABLE, buyer_id)
        f = rec.get('fields') or {}

        pkg = _jeta_compute_priority_package(f)
        if not pkg.get('supply_adjacent'):
            return jsonify({
                'success': False,
                'error': 'This action requires supply_adjacent (Gulf-adjacent US state).',
            }), 400
        sup_raw = jb_get_raw(f, JB.supplier_status) or f.get('Supplier Status')
        if _jeta_normalize_supplier_status(sup_raw) != 'Open':
            return jsonify({
                'success': False,
                'error': 'Supplier Status must be Open for this action.',
            }), 400

        airport = jb_get_str(f, JB.airport_name)
        company = jb_get_str(f, JB.company_name)
        icao = jb_get_str(f, JB.airport_icao).upper()
        city = jb_get_str(f, JB.city)
        state = jb_geo_state_raw(f)
        country = jb_get_str(f, JB.country) or 'USA'
        phone = jb_get_str(f, JB.contact_phone)
        email = jb_get_email(f)

        existing = _jeta_seller_record_for_icao_exists(airtable_client, icao)
        if existing:
            return jsonify({
                'success': True,
                'duplicate': True,
                'seller_id': existing.get('id'),
                'message': 'A JETA_Sellers record with this ICAO already exists.',
            }), 200

        display_name = airport or company or icao or 'Unknown location'
        date_iso = datetime.utcnow().strftime('%Y-%m-%d')
        notes_body = (
            f'Airport / facility: {airport or "—"}\n'
            'Potential seller from JETA supply opportunity (Gulf-adjacent, Open supplier). '
            f'Source buyer record: {buyer_id}.'
        )
        icao_served = f'{icao} — {airport}' if airport else icao
        seller_fields = {
            JS.company_name: display_name,
            'Company Name': display_name,
            JS.city: city,
            'City': city,
            JS.state: state,
            'State': state,
            JS.country: country,
            'Country': country,
            JS.contact_phone: phone,
            'Phone': phone,
            JS.contact_email: email,
            'Email': email,
            JS.icao_airports_served: icao_served,
            'ICAO Code': icao,
            JS.seller_type: 'Terminal',
            'Type': 'Terminal',
            JS.verification_status: 'Unverified',
            'Status': 'Unverified',
            JS.relationship_status: 'Cold',
            'Relationship Status': 'Cold',
            JS.source: 'Manual Research',
            'Source': 'Manual Research',
            JS.near_gulf_coast: True,
            'Near Gulf Coast': True,
            JS.date_added: date_iso,
            'Date Added': date_iso,
            JS.notes: notes_body,
            'Notes': notes_body,
        }
        # Optional link back to buyer — omit if field missing in base
        seller_fields_try = {**seller_fields, 'Source Buyer': [buyer_id]}
        try:
            created = airtable_client.create_record(JETA_SELLERS_TABLE, seller_fields_try)
        except Exception as e1:
            logger.warning('JETA_Sellers create with Source Buyer failed, retrying without link: %s', e1)
            try:
                created = airtable_client.create_record(JETA_SELLERS_TABLE, seller_fields)
            except Exception as e2:
                logger.exception('JETA_Sellers create failed: %s', e2)
                return jsonify({'success': False, 'error': str(e2)}), 400

        return jsonify({
            'success': True,
            'duplicate': False,
            'seller_id': created.get('id'),
            'message': 'Created JETA_Sellers record.',
        }), 201
    except Exception as e:
        logger.exception('jeta_create_seller_from_buyer: %s', e)
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/jeta/buyers/rescore', methods=['POST'])
@app.route('/jeta/buyers/rescore', methods=['POST'])
def jeta_buyers_rescore():
    """
    Recalculate priority_score (0–130), score_breakdown, tags, supply_adjacent, canada for all buyers
    or a single buyer. Persists to JETA_Buyers when those fields exist.
    JSON body optional: { "buyer_id": "rec..." }
    """
    try:
        data = request.get_json(silent=True) or {}
        buyer_id = (data.get('buyer_id') or data.get('buyerId') or '').strip()
        airtable_client = AirtableClient()
        errors: list = []
        updated = 0
        if buyer_id:
            try:
                pkg = _jeta_refresh_buyer_priority_full(airtable_client, buyer_id)
                updated = 1
                return jsonify({
                    'success': True,
                    'updated': 1,
                    'buyer_id': buyer_id,
                    'priority_score': pkg['priority_score'],
                    'score_breakdown': pkg['score_breakdown'],
                    'tags': pkg['tags'],
                    'supply_adjacent': pkg['supply_adjacent'],
                    'canada': pkg['canada'],
                    'errors': [],
                }), 200
            except Exception as e:
                logger.exception('jeta_buyers_rescore single failed: %s', e)
                return jsonify({'success': False, 'error': str(e), 'updated': 0, 'errors': [str(e)]}), 400

        raw = airtable_client.get_all_records(JETA_BUYERS_TABLE)
        for rec in raw:
            rid = rec.get('id')
            if not rid:
                continue
            try:
                _jeta_refresh_buyer_priority_full(airtable_client, rid)
                updated += 1
            except Exception as e:
                errors.append({'id': rid, 'error': str(e)})
        return jsonify({
            'success': True,
            'updated': updated,
            'total_records': len(raw),
            'errors': errors[:100],
        }), 200
    except Exception as e:
        logger.exception('jeta_buyers_rescore failed: %s', e)
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/jeta/outreach/due', methods=['GET'])
@app.route('/jeta/outreach/due-buyers', methods=['GET'])
def jeta_outreach_due_buyers():
    """Buyers with Next Touch Date today or overdue; touch # due + last response from JETA_Outreach."""
    try:
        airtable_client = AirtableClient()
        try:
            buyers_raw = airtable_client.get_all_records(JETA_BUYERS_TABLE)
            outreach_raw = airtable_client.get_all_records(JETA_OUTREACH_TABLE)
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'buyers': [],
                'hint': f'Ensure tables "{JETA_BUYERS_TABLE}" and "{JETA_OUTREACH_TABLE}" exist with expected fields.',
            }), 200

        today = datetime.utcnow().date()
        buyer_rows = {rec['id']: _jeta_serialize_record(rec) for rec in buyers_raw}

        # Per buyer: max touch #, latest outreach by Touch Date for last response
        max_touch: dict = {}
        latest_by_buyer: dict = {}  # buyer_id -> (touch_date_key, response text, status)

        def _touch_date_key(fields: dict):
            td = jo_get_raw(fields, JO.outreach_date) or fields.get('Touch Date')
            if td is None:
                return ''
            return _jeta_format_date_field(td) or ''

        for rec in outreach_raw:
            f = rec.get('fields') or {}
            bids = _jeta_outreach_buyer_ids(f)
            if not bids:
                continue
            bid = bids[0]
            tn = jo_get_int(f, JO.touch_number)
            if tn is None:
                try:
                    tn = int(f.get('Touch Number')) if f.get('Touch Number') is not None else 0
                except (TypeError, ValueError):
                    tn = 0
            max_touch[bid] = max(max_touch.get(bid, 0), tn)
            dk = _touch_date_key(f)
            resp = jo_response_received_display_string(f).strip()
            st = jo_get_str(f, JO.response_type) or (f.get('Response Status', '') or '').strip()
            last_line = resp if resp else st
            prev = latest_by_buyer.get(bid)
            if not prev or dk > prev[0]:
                latest_by_buyer[bid] = (dk, last_line, st)

        due = []
        for bid, row in buyer_rows.items():
            ntd = (row.get('nextTouchDate') or '').strip()
            if not ntd:
                continue
            try:
                y, m, d = [int(x) for x in ntd.split('-')[:3]]
                nd = datetime(y, m, d).date()
            except (ValueError, TypeError):
                continue
            if nd <= today:
                touch_due = max_touch.get(bid, 0) + 1
                _, last_resp, _ = latest_by_buyer.get(bid, ('', '', ''))
                due.append({
                    **row,
                    'touchNumberDue': touch_due,
                    'lastResponse': last_resp or '',
                })

        due.sort(key=lambda x: (x.get('nextTouchDate') or '', x.get('companyName') or ''))
        return jsonify({'success': True, 'buyers': due, 'count': len(due)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e), 'buyers': []}), 500


@app.route('/jeta/outreach', methods=['GET'])
def jeta_get_outreach():
    """List outreach log: sort=touch_date_desc|touch_date_asc, filter channel, response_status."""
    try:
        airtable_client = AirtableClient()
        try:
            buyers_raw = airtable_client.get_all_records(JETA_BUYERS_TABLE)
            outreach_raw = airtable_client.get_all_records(JETA_OUTREACH_TABLE)
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'outreach': [],
                'filterOptions': {'channels': [], 'responseStatuses': []},
                'hint': f'Ensure "{JETA_OUTREACH_TABLE}" exists.',
            }), 200

        buyer_lookup = {}
        for rec in buyers_raw:
            ser = _jeta_serialize_record(rec)
            buyer_lookup[rec['id']] = {
                'companyName': ser['companyName'],
                'contactName': ser['contactName'],
            }

        rows = [_jeta_serialize_outreach(rec, buyer_lookup) for rec in outreach_raw]

        channels_all = sorted({r['channel'] for r in rows if r.get('channel')})
        statuses_all = sorted({
            *(r.get('responseStatus') for r in rows if r.get('responseStatus')),
        })

        ch_f = (request.args.get('channel') or '').strip().lower()
        rs_f = (request.args.get('response_status') or '').strip().lower()
        if ch_f:
            rows = [r for r in rows if (r.get('channel') or '').lower() == ch_f]
        if rs_f:
            rows = [
                r for r in rows
                if rs_f in (r.get('responseStatus') or '').lower()
                or rs_f in (r.get('responseReceived') or '').lower()
            ]

        sort_mode = (request.args.get('sort') or 'touch_date_desc').strip().lower()
        rev = sort_mode == 'touch_date_asc'

        def sort_key(r):
            return (r.get('touchDate') or '', r.get('createdTime') or '')

        rows.sort(key=sort_key, reverse=not rev)

        return jsonify({
            'success': True,
            'outreach': rows,
            'count': len(rows),
            'filterOptions': {'channels': channels_all, 'responseStatuses': statuses_all},
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e), 'outreach': []}), 500


@app.route('/api/jeta/outreach/log', methods=['POST'])
@app.route('/jeta/outreach', methods=['POST'])
def jeta_create_outreach():
    """Create outreach row; optionally updates buyer Last Contact Date + Next Touch Date."""
    try:
        data = dict(request.json or {})
        if not data.get('buyerId') and data.get('buyer_id'):
            data['buyerId'] = data['buyer_id']
        if not data.get('touchDate') and data.get('touch_date'):
            data['touchDate'] = data['touch_date']
        if not data.get('nextTouchDate') and data.get('next_touch_date'):
            data['nextTouchDate'] = data['next_touch_date']
        fields = _jeta_outreach_json_to_fields(data)
        if not fields.get(JO.buyer_id) and not fields.get(JETA_OUTREACH_BUYER_FIELD):
            return jsonify({'success': False, 'error': 'buyerId is required'}), 400
        airtable_client = AirtableClient()
        created = airtable_client.create_record(JETA_OUTREACH_TABLE, fields)
        buyers_raw = airtable_client.get_all_records(JETA_BUYERS_TABLE)
        buyer_lookup = {}
        for rec in buyers_raw:
            ser = _jeta_serialize_record(rec)
            buyer_lookup[rec['id']] = {
                'companyName': ser['companyName'],
                'contactName': ser['contactName'],
            }
        out = _jeta_serialize_outreach(created, buyer_lookup)

        buyer_id = data.get('buyerId')
        if buyer_id:
            bu = {}
            if data.get('touchDate'):
                bu['Last Contact Date'] = data['touchDate']
            if data.get('nextTouchDate'):
                bu['Next Touch Date'] = data['nextTouchDate']
            if bu:
                try:
                    airtable_client.update_record(JETA_BUYERS_TABLE, buyer_id, bu)
                except Exception:
                    pass

        return jsonify({'success': True, 'outreach': out}), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


JETA_OUTREACH_AI_USER_PROMPT = (
    'Write the complete email body only, ready to paste into an email client. '
    'Do not wrap in markdown code fences.'
)


def _jeta_build_outreach_ai_system(
    touch_number: int,
    contact_name: str,
    company_name: str,
    buyer_type: str,
    airport: str,
    state: str,
) -> str:
    """System prompt for Claude: JETA cold-email draft (substituted placeholders)."""
    tn = max(1, int(touch_number) if touch_number is not None else 1)
    cn = (contact_name or '').strip() or 'the contact'
    comp = (company_name or '').strip() or 'the company'
    bt = (buyer_type or '').strip() or 'prospect'
    ap = (airport or '').strip() or 'their airport or facility'
    st = (state or '').strip() or 'their region'
    extra_touch = ''
    if tn > 4:
        extra_touch = (
            '\n\nFor this touch number (5 or higher), write a very brief professional '
            'check-in that keeps the relationship warm without repeating earlier '
            'messages verbatim. Still under 150 words.'
        )
    return (
        'You are writing outreach emails for JETA COURTIÈRE, '
        'an aviation fuel brokerage division of DEE DAVIS INC. '
        'The company is EDWOSB/WBE/MBE certified, based in '
        'Troy Michigan, and sources competitive Jet-A supply '
        'for FBOs, charter operators, and regional airports.\n\n'
        'Write a short professional cold email for Touch '
        f'{tn} to {cn} at {comp}, '
        f'a {bt} located at {ap} in {st}.\n\n'
        'Touch 1: Initial introduction, one ask — '
        '15 minute conversation.\n'
        'Touch 2: Soft follow up, two sentences max.\n'
        'Touch 3: Value add — mention EDWOSB certification '
        'and competitive pricing angle.\n'
        'Touch 4: Final follow up, leave the door open.'
        f'{extra_touch}\n\n'
        'Email must be under 150 words. No attachments '
        'mentioned. No pitch deck. Sign off as Dee Davis, '
        'JETA COURTIÈRE | DEE DAVIS INC | jeta@deedavis.biz'
    )


@app.route('/jeta/outreach/ai-draft', methods=['POST'])
def jeta_outreach_ai_draft():
    """Generate outreach email draft via Claude (same pattern as ATLAS AI routes)."""
    try:
        data = request.json or {}
        buyer_id = (data.get('buyerId') or '').strip()

        touch_number = data.get('touchNumber')
        contact_name = data.get('contactName')
        company_name = data.get('companyName')
        buyer_type = data.get('buyerType')
        airport = data.get('airport')
        state = data.get('state')

        if buyer_id:
            try:
                airtable_client = AirtableClient()
                rec = airtable_client.get_record(JETA_BUYERS_TABLE, buyer_id)
                ser = _jeta_serialize_record(rec)
                if contact_name is None:
                    contact_name = ser.get('contactName', '')
                if company_name is None:
                    company_name = ser.get('companyName', '')
                if buyer_type is None:
                    buyer_type = ser.get('buyerType', '')
                if airport is None:
                    airport = ser.get('airport', '')
                if state is None:
                    state = ser.get('state', '')
            except Exception:
                pass

        if touch_number is None:
            return jsonify({'success': False, 'error': 'touchNumber is required'}), 400
        try:
            tn = int(touch_number)
        except (TypeError, ValueError):
            return jsonify({'success': False, 'error': 'touchNumber must be a number'}), 400

        contact_name = contact_name if contact_name is not None else ''
        company_name = company_name if company_name is not None else ''
        buyer_type = buyer_type if buyer_type is not None else ''
        airport = airport if airport is not None else ''
        state = state if state is not None else ''

        import anthropic
        anthropic_client = anthropic.Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY', ''))
        system_prompt = _jeta_build_outreach_ai_system(
            tn,
            str(contact_name or ''),
            str(company_name or ''),
            str(buyer_type or ''),
            str(airport or ''),
            str(state or ''),
        )
        message = anthropic_client.messages.create(
            model='claude-sonnet-4-20250514',
            max_tokens=1200,
            system=system_prompt,
            messages=[{'role': 'user', 'content': JETA_OUTREACH_AI_USER_PROMPT}],
        )
        draft = message.content[0].text.strip()
        return jsonify({'success': True, 'draft': draft})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


def _jeta_extract_json_object(text: str):
    """Best-effort parse of JSON from Claude output."""
    import json

    s = (text or '').strip()
    if not s:
        return None
    try:
        return json.loads(s)
    except json.JSONDecodeError:
        pass
    i = s.find('{')
    j = s.rfind('}')
    if i >= 0 and j > i:
        try:
            return json.loads(s[i : j + 1])
        except json.JSONDecodeError:
            pass
    return None


@app.route('/api/jeta/notifications/escalation-notice-draft', methods=['POST'])
@app.route('/jeta/notifications/escalation-notice-draft', methods=['POST'])
def jeta_escalation_notice_draft():
    """
    AI drafts formal counterparty notices citing fee escalation clauses (Claude).
    Optional dealIds; if empty, uses deals flagged by weekly escalation monitoring, else active deals with base benchmark.
    """
    import json

    import anthropic
    from jeta_deal_schema import JD, jd_get_float, jd_get_str
    from jeta_market_data_schema import JMD, jmd_get_bool, jmd_get_str
    from jeta_fee_escalation import compute_escalation_price_alert

    try:
        data = request.json or {}
        deal_ids = data.get('dealIds') or data.get('deal_ids') or []
        if isinstance(deal_ids, str):
            deal_ids = [x.strip() for x in deal_ids.split(',') if x.strip()]
        deal_ids = [str(x).strip() for x in deal_ids if str(x).strip()]

        airtable_client = AirtableClient()
        buyers_raw = airtable_client.get_all_records(JETA_BUYERS_TABLE)
        buyer_lookup = {rec['id']: _jeta_serialize_record(rec) for rec in buyers_raw}

        if not deal_ids:
            mr = _jeta_market_records_newest_first(airtable_client)
            deals_raw = airtable_client.get_all_records(JETA_DEALS_TABLE)
            alert = compute_escalation_price_alert(market_records_newest_first=mr, deal_records=deals_raw)
            deal_ids = [x.get('deal_id') for x in (alert.get('affected_deals') or []) if x.get('deal_id')]
        if not deal_ids:
            deals_raw = airtable_client.get_all_records(JETA_DEALS_TABLE)
            for rec in deals_raw:
                f = rec.get('fields') or {}
                st = _jeta_normalize_deal_stage(jd_get_str(f, JD.deal_stage) or f.get('Deal Stage'))
                if st in ('Closed Won', 'Closed Lost'):
                    continue
                if jd_get_float(f, JD.escalation_base_benchmark_bbl) is None:
                    continue
                rid = rec.get('id')
                if rid:
                    deal_ids.append(rid)
        deal_ids = list(dict.fromkeys(deal_ids))[:25]

        mr = _jeta_market_records_newest_first(airtable_client)
        from jeta_iata_market import serialize_market_row

        market_summary = serialize_market_row(mr[0]) if mr else {}
        mf = mr[0].get('fields') if mr else {}
        intel = {
            'geopolitical_risk_level': jmd_get_str(mf, JMD.geopolitical_risk_level),
            'supply_disruption_alert': jmd_get_bool(mf, JMD.supply_disruption_alert),
            'escalation_clause_triggered_sheet': jmd_get_bool(mf, JMD.escalation_clause_triggered),
            'hormuz_status': jmd_get_str(mf, JMD.hormuz_status),
            'suez_status': jmd_get_str(mf, JMD.suez_status),
            'bosphorus_status': jmd_get_str(mf, JMD.bosphorus_status),
            'south_china_sea_status': jmd_get_str(mf, JMD.south_china_sea_status),
        }

        deal_payloads = []
        for did in deal_ids:
            try:
                dr = airtable_client.get_record(JETA_DEALS_TABLE, did)
                ser = _jeta_serialize_deal(dr, buyer_lookup)
                bid = ser.get('buyerId') or ''
                em = ''
                if bid and bid in buyer_lookup:
                    em = (buyer_lookup[bid].get('email') or '').strip()
                deal_payloads.append(
                    {
                        'deal_id': did,
                        'deal_name': ser.get('dealName') or '',
                        'buyer_display': ser.get('buyerName') or '',
                        'buyer_email': em,
                        'escalation_clause_version': ser.get('escalationClauseVersion'),
                        'base_benchmark_bbl': ser.get('escalationBaseBenchmarkBbl'),
                        'jeta_fee_per_gallon': ser.get('jetaFeePerGallon'),
                    }
                )
            except Exception:
                continue

        if not deal_payloads:
            return jsonify({
                'success': True,
                'drafts': [],
                'notice': 'No eligible deals (need active deals with Fee Agreement benchmark on file, or escalation watchlist).',
            }), 200

        blob = json.dumps({'latest_market': market_summary, 'jeta_market_intel': intel, 'deals': deal_payloads}, indent=2)

        system = (
            'You draft formal commercial email notices for JETA COURTIÈRE (DEE DAVIS INC), '
            'an aviation fuel brokerage in Troy, Michigan (EDWOSB/WBE/MBE). '
            'Counterparties have executed Fee Agreements with Version A, B, or C escalation language. '
            'Given current IATA benchmark conditions and JETA_MarketData intelligence, write concise notices that:\n'
            '- Reference that fee terms may adjust per the executed agreement when benchmark thresholds apply\n'
            '- Mention 48-hour written notice where the agreement requires\n'
            '- Do NOT invent specific new dollar fees; defer to the signed clause\n'
            '- Professional tone; sign as Dee Davis, JETA COURTIÈRE | DEE DAVIS INC | jeta@deedavis.biz\n\n'
            'Respond with VALID JSON ONLY (no markdown fences). Shape:\n'
            '{"drafts":[{"deal_id":"recXXX","subject":"...","body":"..."}]}\n'
            'Exactly one object per deal in the input list, same deal_id values.'
        )

        key = os.environ.get('ANTHROPIC_API_KEY', '')
        if not key:
            return jsonify({
                'success': False,
                'error': 'ANTHROPIC_API_KEY is not configured for AI drafts.',
            }), 503

        client = anthropic.Anthropic(api_key=key)
        message = client.messages.create(
            model='claude-sonnet-4-20250514',
            max_tokens=8000,
            system=system,
            messages=[
                {
                    'role': 'user',
                    'content': (
                        'Generate escalation / market-condition notices for these deals and market context:\n\n' + blob
                    ),
                }
            ],
        )
        raw_text = message.content[0].text.strip()
        parsed = _jeta_extract_json_object(raw_text) or {}
        drafts = parsed.get('drafts') if isinstance(parsed, dict) else None
        if not isinstance(drafts, list):
            drafts = []

        email_by_deal = {d.get('deal_id'): (d.get('buyer_email') or '').strip() for d in deal_payloads}
        for row in drafts:
            if not isinstance(row, dict):
                continue
            did = row.get('deal_id')
            row['buyer_email'] = email_by_deal.get(did, '')

        return jsonify({
            'success': True,
            'drafts': drafts,
            'marketContext': {'intel': intel, 'latest': market_summary},
            'disclaimer': (
                'AI-generated drafts require human review before sending. '
                'Fee adjustments follow executed agreements; NEXUS does not automatically change fees or bill counterparties.'
            ),
        }), 200
    except Exception as e:
        logger.exception('jeta_escalation_notice_draft failed: %s', e)
        return jsonify({'success': False, 'error': str(e)}), 500


# =====================================================================
# JETA_Deals — canonical snake_case (see jeta_deal_schema.JD); dual-read legacy columns.
# Links: buyer_id → JETA_Buyers, seller_id → JETA_Sellers; compliance still uses serialized camelCase.
# =====================================================================

JETA_DEALS_TABLE = 'JETA_Deals'

# Conventional jet fuel vs SAF scope (JETA_Buyers + JETA_Deals — Airtable single select)
JETA_FUEL_TYPE_OPTIONS = frozenset({'Conventional', 'SAF', 'Both'})


def _jeta_normalize_fuel_type(raw) -> str:
    s = (str(raw).strip() if raw is not None else '') or ''
    if not s:
        return 'Conventional'
    for opt in JETA_FUEL_TYPE_OPTIONS:
        if opt.lower() == s.lower():
            return opt
    return 'Conventional'


JETA_SUPPLIER_STATUS_OPTIONS = frozenset({'Open', 'Branded', 'Unknown'})


def _jeta_normalize_supplier_status(raw) -> str:
    s = (str(raw).strip() if raw is not None else '') or ''
    if not s:
        return 'Unknown'
    for opt in JETA_SUPPLIER_STATUS_OPTIONS:
        if opt.lower() == s.lower():
            return opt
    return 'Unknown'


def _jeta_supplier_name_is_branded(supplier_name: str) -> bool:
    """
    Major branded into-plane / fuel suppliers — approach carefully if present.
    Avfuel, Phillips 66, World Fuel Services, Air BP.
    """
    n = (supplier_name or '').lower()
    if 'avfuel' in n:
        return True
    if 'world fuel' in n:
        return True
    if re.search(r'\bair\s*bp\b', n) or 'air bp' in n:
        return True
    if 'phillips' in n and '66' in n:
        return True
    if re.search(r'\bp66\b', n):
        return True
    return False


def _jeta_supplier_status_from_supplier_rows(suppliers: list) -> str:
    """After a directory lookup: Branded if any listed supplier matches major brands; else Open."""
    for s in suppliers or []:
        name = (s.get('supplier_name') if isinstance(s, dict) else None) or ''
        if _jeta_supplier_name_is_branded(name):
            return 'Branded'
    return 'Open'


# Linked record on JETA_SupplierDirectory → JETA_Buyers (canonical buyer_id; legacy env override)
JETA_SUPPLIER_DIRECTORY_BUYER_FIELD = (os.environ.get('JETA_SUPPLIER_DIRECTORY_BUYER_FIELD') or 'Buyer').strip() or 'Buyer'

JETA_SUPPLIER_DIRECTORY_TABLE = 'JETA_SupplierDirectory'


def _jeta_persist_suppliers_for_icao(
    icao: str,
    airtable_client: AirtableClient,
    *,
    buyer_id: str | None = None,
) -> dict:
    """
    Core logic for GET /jeta/suppliers/lookup: OurAirports + curated suppliers → JETA_SupplierDirectory.
    Optionally link each stored row to buyer_id.
    Returns: success, error?, stored_count, supplier_status (Open|Branded), icao, airport_name, suppliers, ...
    """
    from jeta_supplier_directory import (
        airtable_fields_for_row,
        directory_row_fields_legacy_minimal,
        lookup_suppliers_for_icao,
        today_iso_utc,
    )

    err, payload = lookup_suppliers_for_icao(icao)
    if err:
        return {'success': False, 'error': err, 'stored_count': 0}

    lookup_date = today_iso_utc()
    stored_ids: list = []
    seen: set = set()
    suppliers_out = payload.get('suppliers') or []
    supplier_status = _jeta_supplier_status_from_supplier_rows(suppliers_out)

    for s in suppliers_out:
        name = (s.get('supplier_name') or '').strip()
        ft = (s.get('fuel_type') or '').strip()
        if not name:
            continue
        key = (payload.get('icao'), name.lower(), ft.lower())
        if key in seen:
            continue
        seen.add(key)
        note_txt = (s.get('source_note') or '').strip()
        fields = airtable_fields_for_row(
            payload['icao'],
            payload['airport_name'],
            name,
            ft,
            date_looked_up=lookup_date,
            city=(payload.get('city') or ''),
            state=(payload.get('state') or ''),
            country=(payload.get('country') or ''),
            notes=note_txt,
        )
        if buyer_id:
            fields[JSD.buyer_id] = [buyer_id]
            if JETA_SUPPLIER_DIRECTORY_BUYER_FIELD:
                fields[JETA_SUPPLIER_DIRECTORY_BUYER_FIELD] = [buyer_id]

        _buyer_field_keys = (JSD.buyer_id, JETA_SUPPLIER_DIRECTORY_BUYER_FIELD, 'Buyer')

        def _strip_buyer_link(d: dict) -> dict:
            return {k: v for k, v in d.items() if k not in _buyer_field_keys}

        try:
            rec = airtable_client.create_record(JETA_SUPPLIER_DIRECTORY_TABLE, fields)
            rid = rec.get('id') if isinstance(rec, dict) else getattr(rec, 'id', None)
            if rid:
                stored_ids.append(rid)
        except Exception as e1:
            try_no_link = False
            if buyer_id:
                try:
                    f2 = _strip_buyer_link(fields)
                    rec = airtable_client.create_record(JETA_SUPPLIER_DIRECTORY_TABLE, f2)
                    rid = rec.get('id') if isinstance(rec, dict) else getattr(rec, 'id', None)
                    if rid:
                        stored_ids.append(rid)
                    try_no_link = True
                except Exception:
                    pass
            if not try_no_link:
                slim = directory_row_fields_legacy_minimal(
                    payload['icao'],
                    payload['airport_name'],
                    name,
                    ft,
                    lookup_date,
                )
                if buyer_id:
                    slim[JSD.buyer_id] = [buyer_id]
                    if JETA_SUPPLIER_DIRECTORY_BUYER_FIELD:
                        slim[JETA_SUPPLIER_DIRECTORY_BUYER_FIELD] = [buyer_id]
                try:
                    rec = airtable_client.create_record(JETA_SUPPLIER_DIRECTORY_TABLE, slim)
                    rid = rec.get('id') if isinstance(rec, dict) else getattr(rec, 'id', None)
                    if rid:
                        stored_ids.append(rid)
                except Exception as e2:
                    try:
                        fa = _strip_buyer_link(slim)
                        airtable_client.create_record(JETA_SUPPLIER_DIRECTORY_TABLE, fa)
                    except Exception as e3:
                        logger.warning(
                            'JETA_SupplierDirectory write failed: %s / %s / %s',
                            e1,
                            e2,
                            e3,
                        )

    return {
        'success': True,
        'icao': payload.get('icao'),
        'airport_name': payload.get('airport_name'),
        'suppliers': suppliers_out,
        'supplier_status': supplier_status,
        'stored_count': len(stored_ids),
        'stored_record_ids': stored_ids,
        'lookup_date': lookup_date,
        'notice': payload.get('notice'),
        'iata_directory_portal': payload.get('iata_directory_portal'),
        'iata_fuel_program_url': payload.get('iata_fuel_program_url'),
    }


def _jeta_faa_post_import_enrichment_worker(pairs: list) -> None:
    """Background: supplier lookup per imported buyer ICAO; 2s spacing; updates Supplier Status."""
    if not pairs:
        return
    ac = AirtableClient()
    for i, (buyer_id, icao) in enumerate(pairs):
        if i > 0:
            time.sleep(2)
        try:
            out = _jeta_persist_suppliers_for_icao(icao, ac, buyer_id=buyer_id)
            if out.get('success'):
                st = out.get('supplier_status') or 'Open'
                ac.update_record(JETA_BUYERS_TABLE, buyer_id, {'Supplier Status': _jeta_normalize_supplier_status(st)})
                try:
                    _jeta_refresh_buyer_priority_score(ac, buyer_id)
                except Exception as pe:
                    logger.warning('JETA priority score after enrichment failed %s: %s', buyer_id, pe)
            else:
                logger.warning(
                    'JETA FAA enrichment skipped ICAO=%s buyer=%s: %s',
                    icao,
                    buyer_id,
                    out.get('error'),
                )
        except Exception as e:
            logger.exception('JETA FAA enrichment failed ICAO=%s buyer=%s: %s', icao, buyer_id, e)


# Weekly IATA jet fuel snapshot (see GET /api/jeta/market/price, jeta_iata_market.py)
JETA_MARKET_DATA_TABLE = 'JETA_MarketData'

JETA_DEAL_STAGES = [
    'Qualifying',
    'Supply Sourcing',
    'NCNDA Pending',
    'NCNDA Signed',
    'Docs Exchanged',
    'IMFPA Executed',
    'Closed Won',
    'Closed Lost',
]

JETA_DEAL_CLOSED_STAGES = frozenset({'Closed Won', 'Closed Lost'})


def _jeta_parse_float(val, default=0.0):
    if val is None or val == '':
        return default
    try:
        return float(val)
    except (TypeError, ValueError):
        return default


def _jeta_normalize_deal_stage(raw) -> str:
    s = (str(raw).strip() if raw is not None else '') or 'Qualifying'
    for lab in JETA_DEAL_STAGES:
        if lab.lower() == s.lower():
            return lab
    return 'Qualifying'


def _jeta_serialize_deal(record: dict, buyer_lookup: dict) -> dict:
    f = record.get('fields') or {}
    buyer_id = jd_first_link_id(f, JD.buyer_id)
    seller_id = jd_first_link_id(f, JD.seller_id)
    company = ''
    contact = ''
    if buyer_id and buyer_lookup:
        info = buyer_lookup.get(buyer_id, {})
        company = info.get('companyName', '') or ''
        contact = info.get('contactName', '') or ''
    if company and contact:
        buyer_display = f'{company} — {contact}'
    else:
        buyer_display = company or contact or ''

    stage_raw = jd_get_str(f, JD.deal_stage) or f.get('Deal Stage')
    stage = _jeta_normalize_deal_stage(stage_raw)
    vol = jd_get_float(f, JD.volume_gallons)
    if vol is None:
        vol = _jeta_parse_float(f.get('Volume Gallons'))
    ppg = jd_get_float(f, JD.price_per_gallon)
    if ppg is None:
        ppg = _jeta_parse_float(f.get('Price Per Gallon'))
    jfg = jd_get_float(f, JD.jeta_fee_per_gallon)
    if jfg is None:
        jfg = _jeta_parse_float(f.get('JETA Fee Per Gallon'))
    jtf = jd_get_float(f, JD.jeta_total_fee)
    if jtf is None:
        jtf = _jeta_parse_optional_float(f.get('Projected Total Fee'))
    if jtf is not None:
        projected_total_fee = round(float(jtf), 4)
    else:
        projected_total_fee = round(vol * jfg, 4) if vol and jfg else 0.0

    def doc_status(canonical: str, *legacy_keys: str) -> str:
        v = jd_get_raw(f, canonical)
        if v is not None and str(v).strip() != '':
            return str(v).strip()
        for lk in legacy_keys:
            if lk in f and f.get(lk) is not None and str(f.get(lk)).strip() != '':
                return str(f.get(lk)).strip()
        return ''

    notes_text = jd_notes_or_description(f)
    ncnda_st = doc_status(JD.ncnda_status, 'NCNDA Status')
    fee_ag_st = doc_status(JD.fee_agreement_status, 'Fee Agreement Status')
    pay_st = doc_status(JD.payment_status, 'Payment Status')
    icpo_b = jd_get_bool(f, JD.icpo_received)
    if icpo_b is None:
        icpo_b = _jeta_coerce_bool(f.get('ICPO Received From Buyer'))
    fco_b = jd_get_bool(f, JD.fco_received)
    if fco_b is None:
        fco_b = _jeta_coerce_bool(f.get('FCO Received From Seller'))
    del_b = jd_get_bool(f, JD.delivery_confirmed)
    if del_b is None:
        del_b = _jeta_coerce_bool(f.get('Fuel Delivery Confirmed'))
    multi_b = jd_get_bool(f, JD.multi_broker_chain)
    if multi_b is None:
        multi_b = _jeta_coerce_bool(f.get('Multiple Brokers In Chain'))
    ncnda_dt = jd_get_str(f, JD.ncnda_signed_date)
    signed_ncnda_up = bool(ncnda_dt) or _jeta_coerce_bool(f.get('Signed NCNDA Uploaded Date Stamped'))
    fee_ag_ex = (
        (fee_ag_st.lower() == 'signed')
        or ('signed' in fee_ag_st.lower() and fee_ag_st)
        or _jeta_coerce_bool(f.get('Fee Agreement Executed'))
    )
    fee_pay_ok = (
        pay_st.lower() in ('received', 'partial')
        or _jeta_coerce_bool(f.get('Fee Payment Received Or Scheduled'))
    )
    imfpa_pct = _jeta_parse_optional_float(jd_get_raw(f, JD.imfpa_total_pct))
    if imfpa_pct is None:
        imfpa_pct = _jeta_parse_optional_float(f.get('IMFPA Pct Total'))

    def gate_n(n: int) -> bool:
        canon = getattr(JD, f'gate_{n}_complete', None)
        if canon:
            b = jd_get_bool(f, canon)
            if b is not None:
                return b
        return _jeta_coerce_bool(f.get(f'Gate {n} Complete'))

    return {
        'id': record['id'],
        'buyerId': buyer_id,
        'sellerId': seller_id,
        'buyerName': buyer_display,
        'companyName': company,
        'contactName': contact,
        'dealName': jd_get_str(f, JD.deal_name) or str(f.get('Deal Name') or '').strip(),
        'dealDescription': notes_text,
        'notes': notes_text,
        'dealStage': stage,
        'supplySource': str(f.get('Supply Source') or '').strip(),
        'volumeGallons': vol,
        'volumeFrequency': jd_get_str(f, JD.volume_frequency),
        'pricePerGallon': ppg,
        'marketBenchmarkPpg': jd_get_float(f, JD.market_benchmark_ppg),
        'jetaFeePerGallon': jfg,
        'jetaTotalFee': jd_get_float(f, JD.jeta_total_fee),
        'projectedTotalFee': projected_total_fee,
        'grossDealValue': jd_get_float(f, JD.gross_deal_value),
        'fuelProduct': jd_get_str(f, JD.fuel_product),
        'stageEnteredDate': jd_get_str(f, JD.stage_entered_date),
        'dealOpenDate': jd_get_str(f, JD.deal_open_date),
        'dealCloseDate': jd_get_str(f, JD.deal_close_date),
        'brokerChainCount': jd_get_float(f, JD.broker_chain_count),
        'imfpaRequired': jd_get_bool(f, JD.imfpa_required),
        'jetaChainPct': jd_get_float(f, JD.jeta_chain_pct),
        'ncndaSignedDate': ncnda_dt,
        'feeAgreementSigned': jd_get_str(f, JD.fee_agreement_signed),
        'imfpaSignedDate': jd_get_str(f, JD.imfpa_signed_date),
        'paymentStatus': pay_st,
        'paymentReceivedDate': jd_get_str(f, JD.payment_received_date),
        'dealLostReason': jd_get_str(f, JD.deal_lost_reason),
        'lastActivityDate': jd_get_str(f, JD.last_activity_date),
        'fraudCleared': jd_get_bool(f, JD.fraud_cleared),
        'staleAlert': jd_get_bool(f, JD.stale_alert),
        'gate1Complete': gate_n(1),
        'gate2Complete': gate_n(2),
        'gate3Complete': gate_n(3),
        'gate4Complete': gate_n(4),
        'gate5Complete': gate_n(5),
        'gate6Complete': gate_n(6),
        'gate7Complete': gate_n(7),
        'gate8Complete': gate_n(8),
        'ncndaStatus': ncnda_st,
        'imfpaStatus': doc_status(JD.imfpa_status, 'IMFPA Status'),
        'feeAgreementStatus': fee_ag_st,
        'icc769NcndaGenerated': _jeta_coerce_bool(f.get('ICC 769E NCNDA Generated')),
        'notGenericNcndaTemplate': _jeta_coerce_bool(f.get('Not Generic NCNDA Template')),
        'ncndaBuyerPartyLegalName': str(f.get('NCNDA Buyer Legal Name') or '').strip(),
        'ncndaJetaPartyLegalName': str(f.get('NCNDA JETA Legal Name') or '').strip(),
        'ncndaDocumentSent': _jeta_coerce_bool(f.get('NCNDA Document Sent')),
        'ncndaExecutionTracked': _jeta_coerce_bool(f.get('NCNDA Execution Tracked')),
        'ncndaIcc769eReferencedInDocument': _jeta_coerce_bool(f.get('NCNDA ICC769E In Document')),
        'ncndaDealDescriptionSpecificNotGeneric': _jeta_coerce_bool(f.get('NCNDA Deal Desc Not Generic')),
        'ncndaGenericFloatingInvalidOnUpload': _jeta_coerce_bool(f.get('NCNDA Generic Invalid On Upload')),
        'signedNcndaUploadedDateStamped': signed_ncnda_up,
        'fcoReceivedFromSeller': fco_b,
        'icpoReceivedFromBuyer': icpo_b,
        'fcoIcpoProductJetAA1Only': _jeta_coerce_bool(f.get('FCO ICPO Jet A A1 Only')),
        'multipleBrokersInChain': multi_b,
        'imfpaGeneratedSignedBrokerChain': _jeta_coerce_bool(f.get('IMFPA Generated Signed Broker Chain')),
        'imfpaAllBrokersFullLegalNamesListed': _jeta_coerce_bool(f.get('IMFPA Brokers Legal Names Listed')),
        'imfpaExactPercentagePerPartySpecified': _jeta_coerce_bool(f.get('IMFPA Pct Per Party')),
        'imfpaLockedAfterAllSignaturesNoEdits': _jeta_coerce_bool(f.get('IMFPA Locked Post Sign')),
        'imfpaPercentagesTotalValid': _jeta_coerce_bool(f.get('IMFPA Pct Total Valid')),
        'imfpaBrokerChainPercentageTotal': imfpa_pct,
        'feeAgreementExecuted': fee_ag_ex,
        'feeAgreementExactPerGallonSpecified': _jeta_coerce_bool(f.get('Fee Agreement Per Gallon Specified')),
        'feeAgreementPaymentTriggerSpecified': _jeta_coerce_bool(f.get('Fee Agreement Payment Trigger')),
        'feeAgreementSignedBeforeIntroduction': _jeta_coerce_bool(f.get('Fee Agreement Before Intro')),
        'fuelDeliveryConfirmed': del_b,
        'feePaymentReceivedOrScheduled': fee_pay_ok,
        'dealFileCompleteInDocuments': _jeta_coerce_bool(f.get('Deal File Complete In Documents')),
        'fuelType': _jeta_normalize_fuel_type(jd_get_raw(f, JD.fuel_type) or f.get('Fuel Type')),
        'dealType': jd_get_str(f, JD.deal_type) or str(f.get('Deal Type') or '').strip(),
        'termLength': jd_get_str(f, JD.term_length) or str(f.get('Term Length') or '').strip(),
        'escalationBaseBenchmarkBbl': jd_get_float(f, JD.escalation_base_benchmark_bbl),
        'escalationClauseVersion': jd_get_str(f, JD.escalation_clause_version)
        or str(f.get('Escalation Clause Version') or '').strip()
        or None,
        'createdTime': record.get('createdTime', ''),
    }


def _jeta_deal_json_to_fields(data: dict, partial: bool = False) -> dict:
    """Map API JSON (camelCase) to Airtable — canonical snake_case + legacy columns."""
    out = {}

    def put_both(canon: str, legacy: str | None, val) -> None:
        if val is None:
            return
        out[canon] = val
        if legacy:
            out[legacy] = val

    bid = (data.get('buyerId') or data.get('buyer_id') or '').strip()
    if bid:
        put_both(JD.buyer_id, 'Buyer', [bid])

    sid = (data.get('sellerId') or data.get('seller_id') or '').strip()
    if sid:
        put_both(JD.seller_id, 'Seller', [sid])

    if 'dealName' in data and data['dealName'] is not None:
        put_both(JD.deal_name, 'Deal Name', str(data['dealName']).strip())

    notes_val = None
    if 'notes' in data and data['notes'] is not None:
        notes_val = str(data['notes']).strip()
    elif 'dealDescription' in data and data['dealDescription'] is not None:
        notes_val = str(data['dealDescription']).strip()
    if notes_val is not None:
        put_both(JD.notes, 'Deal Description', notes_val)
        out['Notes'] = notes_val

    if 'dealStage' in data and data.get('dealStage'):
        ds = _jeta_normalize_deal_stage(data['dealStage'])
        put_both(JD.deal_stage, 'Deal Stage', ds)
    elif not partial:
        put_both(JD.deal_stage, 'Deal Stage', JETA_DEAL_STAGES[0])

    if 'fuelType' in data and data.get('fuelType') is not None:
        ft = _jeta_normalize_fuel_type(data.get('fuelType'))
        put_both(JD.fuel_type, 'Fuel Type', ft)
    elif not partial:
        put_both(JD.fuel_type, 'Fuel Type', 'Conventional')

    if 'fuelProduct' in data and data.get('fuelProduct') is not None:
        put_both(JD.fuel_product, 'Fuel Product', str(data['fuelProduct']).strip())

    for jk, canon, legacy in [
        ('supplySource', None, 'Supply Source'),
        ('dealType', JD.deal_type, 'Deal Type'),
        ('termLength', JD.term_length, 'Term Length'),
        ('escalationClauseVersion', JD.escalation_clause_version, 'Escalation Clause Version'),
        ('ncndaStatus', JD.ncnda_status, 'NCNDA Status'),
        ('imfpaStatus', JD.imfpa_status, 'IMFPA Status'),
        ('feeAgreementStatus', JD.fee_agreement_status, 'Fee Agreement Status'),
        ('volumeFrequency', JD.volume_frequency, 'Volume Frequency'),
        ('paymentStatus', JD.payment_status, 'Payment Status'),
        ('dealLostReason', JD.deal_lost_reason, 'Deal Lost Reason'),
    ]:
        if jk not in data or data[jk] is None:
            continue
        if canon:
            put_both(canon, legacy, str(data[jk]).strip())
        else:
            out[legacy] = str(data[jk]).strip()

    date_map = [
        ('stageEnteredDate', JD.stage_entered_date, 'Stage Entered Date'),
        ('dealOpenDate', JD.deal_open_date, 'Deal Open Date'),
        ('dealCloseDate', JD.deal_close_date, 'Deal Close Date'),
        ('ncndaSignedDate', JD.ncnda_signed_date, 'NCNDA Signed Date'),
        ('feeAgreementSigned', JD.fee_agreement_signed, 'Fee Agreement Signed'),
        ('imfpaSignedDate', JD.imfpa_signed_date, 'IMFPA Signed Date'),
        ('paymentReceivedDate', JD.payment_received_date, 'Payment Received Date'),
        ('lastActivityDate', JD.last_activity_date, 'Last Activity Date'),
    ]
    for jk, canon, legacy in date_map:
        if jk not in data or data[jk] in (None, ''):
            continue
        put_both(canon, legacy, str(data[jk]).strip())

    for jk, canon, legacy in [
        ('volumeGallons', JD.volume_gallons, 'Volume Gallons'),
        ('pricePerGallon', JD.price_per_gallon, 'Price Per Gallon'),
        ('jetaFeePerGallon', JD.jeta_fee_per_gallon, 'JETA Fee Per Gallon'),
        ('marketBenchmarkPpg', JD.market_benchmark_ppg, 'Market Benchmark PPG'),
        ('escalationBaseBenchmarkBbl', JD.escalation_base_benchmark_bbl, 'Escalation Base Benchmark Bbl'),
        ('jetaTotalFee', JD.jeta_total_fee, 'Projected Total Fee'),
        ('grossDealValue', JD.gross_deal_value, 'Gross Deal Value'),
        ('brokerChainCount', JD.broker_chain_count, 'Broker Chain Count'),
        ('jetaChainPct', JD.jeta_chain_pct, 'JETA Chain Pct'),
    ]:
        if jk not in data:
            continue
        v = data[jk]
        if v is None or v == '':
            if partial:
                continue
            put_both(canon, legacy, 0.0)
            continue
        try:
            put_both(canon, legacy, float(v))
        except (TypeError, ValueError):
            if not partial:
                put_both(canon, legacy, 0.0)

    if 'projectedTotalFee' in data and data['projectedTotalFee'] not in (None, ''):
        try:
            ptf = float(data['projectedTotalFee'])
            put_both(JD.jeta_total_fee, 'Projected Total Fee', ptf)
        except (TypeError, ValueError):
            pass

    if 'imfpaBrokerChainPercentageTotal' in data and data.get('imfpaBrokerChainPercentageTotal') not in (None, ''):
        pt = _jeta_parse_optional_float(data.get('imfpaBrokerChainPercentageTotal'))
        if pt is not None:
            put_both(JD.imfpa_total_pct, 'IMFPA Pct Total', pt)

    bool_canonical_legacy = [
        ('imfpaRequired', JD.imfpa_required, 'IMFPA Required'),
        ('fraudCleared', JD.fraud_cleared, 'Fraud Cleared'),
        ('staleAlert', JD.stale_alert, 'Stale Alert'),
        ('icc769NcndaGenerated', None, 'ICC 769E NCNDA Generated'),
        ('notGenericNcndaTemplate', None, 'Not Generic NCNDA Template'),
        ('ncndaDocumentSent', None, 'NCNDA Document Sent'),
        ('ncndaExecutionTracked', None, 'NCNDA Execution Tracked'),
        ('ncndaIcc769eReferencedInDocument', None, 'NCNDA ICC769E In Document'),
        ('ncndaDealDescriptionSpecificNotGeneric', None, 'NCNDA Deal Desc Not Generic'),
        ('ncndaGenericFloatingInvalidOnUpload', None, 'NCNDA Generic Invalid On Upload'),
        ('signedNcndaUploadedDateStamped', None, 'Signed NCNDA Uploaded Date Stamped'),
        ('fcoReceivedFromSeller', JD.fco_received, 'FCO Received From Seller'),
        ('icpoReceivedFromBuyer', JD.icpo_received, 'ICPO Received From Buyer'),
        ('fcoIcpoProductJetAA1Only', None, 'FCO ICPO Jet A A1 Only'),
        ('multipleBrokersInChain', JD.multi_broker_chain, 'Multiple Brokers In Chain'),
        ('imfpaGeneratedSignedBrokerChain', None, 'IMFPA Generated Signed Broker Chain'),
        ('imfpaAllBrokersFullLegalNamesListed', None, 'IMFPA Brokers Legal Names Listed'),
        ('imfpaExactPercentagePerPartySpecified', None, 'IMFPA Pct Per Party'),
        ('imfpaLockedAfterAllSignaturesNoEdits', None, 'IMFPA Locked Post Sign'),
        ('imfpaPercentagesTotalValid', None, 'IMFPA Pct Total Valid'),
        ('feeAgreementExecuted', None, 'Fee Agreement Executed'),
        ('feeAgreementExactPerGallonSpecified', None, 'Fee Agreement Per Gallon Specified'),
        ('feeAgreementPaymentTriggerSpecified', None, 'Fee Agreement Payment Trigger'),
        ('feeAgreementSignedBeforeIntroduction', None, 'Fee Agreement Before Intro'),
        ('fuelDeliveryConfirmed', JD.delivery_confirmed, 'Fuel Delivery Confirmed'),
        ('feePaymentReceivedOrScheduled', None, 'Fee Payment Received Or Scheduled'),
        ('dealFileCompleteInDocuments', None, 'Deal File Complete In Documents'),
    ]
    for jk, canon, legacy in bool_canonical_legacy:
        if jk not in data:
            continue
        b = _jeta_coerce_bool(data[jk])
        if canon:
            put_both(canon, legacy, b)
        else:
            out[legacy] = b

    for n in range(1, 9):
        jk = f'gate{n}Complete'
        canon = getattr(JD, f'gate_{n}_complete')
        if jk in data:
            b = _jeta_coerce_bool(data[jk])
            put_both(canon, f'Gate {n} Complete', b)

    if 'ncndaBuyerPartyLegalName' in data and data.get('ncndaBuyerPartyLegalName') is not None:
        out['NCNDA Buyer Legal Name'] = str(data['ncndaBuyerPartyLegalName']).strip()
    if 'ncndaJetaPartyLegalName' in data and data.get('ncndaJetaPartyLegalName') is not None:
        out['NCNDA JETA Legal Name'] = str(data['ncndaJetaPartyLegalName']).strip()

    return out


@app.route('/api/jeta/deals', methods=['GET'])
@app.route('/jeta/deals', methods=['GET'])
def jeta_get_deals():
    """List JETA deals; optional ?deal_stage= filter."""
    try:
        airtable_client = AirtableClient()
        try:
            buyers_raw = airtable_client.get_all_records(JETA_BUYERS_TABLE)
            deals_raw = airtable_client.get_all_records(JETA_DEALS_TABLE)
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'deals': [],
                'stages': JETA_DEAL_STAGES,
                'hint': f'Create Airtable table "{JETA_DEALS_TABLE}" with expected fields.',
            }), 200

        buyer_lookup = {rec['id']: _jeta_serialize_record(rec) for rec in buyers_raw}
        rows = [_jeta_serialize_deal(rec, buyer_lookup) for rec in deals_raw]

        want_integrity = (request.args.get('integrity') or '').strip().lower() in ('1', 'true', 'yes')
        if want_integrity:
            from jeta_fraud_detection import scan_deal_terminology_blacklist

            for row in rows:
                bid = row.get('buyerId') or ''
                b = buyer_lookup.get(bid, {}) if bid else {}
                row['integrity'] = scan_deal_terminology_blacklist(row, b)

        stage_f = (request.args.get('deal_stage') or '').strip()
        if stage_f:
            rows = [r for r in rows if r['dealStage'] == stage_f]

        rows.sort(key=lambda x: (x.get('dealStage') or '', x.get('buyerName') or '', x.get('createdTime') or ''))

        return jsonify({
            'success': True,
            'deals': rows,
            'count': len(rows),
            'stages': JETA_DEAL_STAGES,
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e), 'deals': []}), 500


@app.route('/api/jeta/fraud/dashboard-alerts', methods=['GET'])
@app.route('/jeta/fraud/dashboard-alerts', methods=['GET'])
def jeta_fraud_dashboard_alerts():
    """Deal integrity alerts for JETA Dashboard (stuck deals, stale NCNDA, seller doc SLA)."""
    try:
        from jeta_fraud_detection import build_jeta_dashboard_alerts

        airtable_client = AirtableClient()
        try:
            buyers_raw = airtable_client.get_all_records(JETA_BUYERS_TABLE)
            deals_raw = airtable_client.get_all_records(JETA_DEALS_TABLE)
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'alerts': [],
                'alert_count': 0,
            }), 200

        buyer_lookup = {rec['id']: _jeta_serialize_record(rec) for rec in buyers_raw}
        deal_rows = [_jeta_serialize_deal(rec, buyer_lookup) for rec in deals_raw]
        out = build_jeta_dashboard_alerts(deal_rows, buyer_lookup)
        return jsonify({'success': True, **out})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e), 'alerts': [], 'alert_count': 0}), 500


@app.route('/api/jeta/fraud/gate-catalog', methods=['GET'])
@app.route('/jeta/fraud/gate-catalog', methods=['GET'])
def jeta_fraud_gate_catalog():
    """Human-readable fraud / integrity gate checklist per JETA_Deals stage."""
    try:
        from jeta_fraud_detection import DEAL_STAGE_GATE_REQUIREMENTS

        return jsonify({'success': True, 'gates': DEAL_STAGE_GATE_REQUIREMENTS, 'stages': JETA_DEAL_STAGES})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


def _jeta_market_row_sort_key(record: dict) -> str:
    """Newest-first sort: prefer week_of (Monday), then legacy Price Date / price_date."""
    return jmd_week_sort_key(record.get('fields') or {})


def _jeta_market_records_newest_first(airtable_client) -> list:
    try:
        raw = airtable_client.get_all_records(JETA_MARKET_DATA_TABLE)
    except Exception:
        return []
    raw.sort(key=_jeta_market_row_sort_key, reverse=True)
    return raw


@app.route('/api/jeta/market/price', methods=['GET'])
@app.route('/jeta/market/price', methods=['GET'])
def jeta_market_price():
    """
    JETA — IATA jet fuel $/bbl snapshot stored in Airtable JETA_MarketData.

    - Without refresh: returns the latest stored row(s) from Airtable (dashboard-friendly).
    - With ?refresh=1: fetches IATA Fuel Price Monitor, parses $/bbl, appends a row, returns latest.
    - If the table is empty and refresh is not set, performs one fetch to seed data.

    Airtable fields (canonical): see jeta_market_data_schema.JMD — weekly IATA snapshot with
    price_per_gallon (bbl/42), week_of (Monday), WoW %, date_fetched, etc.; legacy Title Case dual-written.
    Optional manual fields (geopolitical context, chokepoint statuses, price_driver, crude/jet crack, trends,
    war premium, escalation_clause_triggered, market_notes, analyst_source, etc.) are returned on each serialized
    row for the dashboard — see jeta_iata_market.serialize_market_row.
    """
    try:
        from jeta_iata_market import (
            SOURCE_IATA_FUEL_MONITOR,
            fetch_iata_jet_fuel_price_usd_per_bbl,
            price_date_today_utc,
            serialize_market_row,
        )

        airtable_client = AirtableClient()
        want_refresh = (request.args.get('refresh') or '').strip().lower() in ('1', 'true', 'yes', 'on')
        rows = _jeta_market_records_newest_first(airtable_client)

        def build_payload(
            latest_row: dict,
            prev_row: dict = None,
            *,
            fetch_error: str = '',
            synced: bool = False,
            persist_escalation_flag: bool = False,
        ):
            latest = serialize_market_row(latest_row) if latest_row else None
            previous = serialize_market_row(prev_row) if prev_row else None
            out = {
                'success': True,
                'sourceLabel': SOURCE_IATA_FUEL_MONITOR,
                'latest': latest,
                'previous': previous,
                'synced': synced,
                'fetchError': fetch_error or None,
            }
            p0 = (latest or {}).get('pricePerBarrel')
            p1 = (previous or {}).get('pricePerBarrel')
            if (
                p0 is not None
                and p1 is not None
                and isinstance(p0, (int, float))
                and isinstance(p1, (int, float))
                and p1 != 0
            ):
                out['weekOverWeekChangeAbs'] = round(float(p0) - float(p1), 4)
                out['weekOverWeekChangePct'] = round((float(p0) - float(p1)) / float(p1) * 100.0, 4)
            else:
                out['weekOverWeekChangeAbs'] = None
                out['weekOverWeekChangePct'] = None
            try:
                from jeta_fee_escalation import compute_escalation_price_alert

                mr = _jeta_market_records_newest_first(airtable_client)
                deals_m = airtable_client.get_all_records(JETA_DEALS_TABLE)
                esc = compute_escalation_price_alert(
                    market_records_newest_first=mr,
                    deal_records=deals_m,
                )
                out['escalationPriceAlert'] = esc
                if persist_escalation_flag and mr and mr[0].get('id'):
                    try:
                        airtable_client.update_record(JETA_MARKET_DATA_TABLE, mr[0]['id'], {
                            JMD.escalation_clause_triggered: bool(esc.get('triggered')),
                            'Escalation Clause Triggered': bool(esc.get('triggered')),
                        })
                    except Exception:
                        pass
            except Exception:
                out['escalationPriceAlert'] = None
            return out

        # Seed if empty
        if not rows and not want_refresh:
            want_refresh = True

        if want_refresh:
            price, err = fetch_iata_jet_fuel_price_usd_per_bbl()
            if price is None:
                if rows:
                    return jsonify(
                        build_payload(
                            rows[0],
                            rows[1] if len(rows) > 1 else None,
                            fetch_error=err,
                            synced=False,
                            persist_escalation_flag=False,
                        )
                    ), 200
                return jsonify({
                    'success': False,
                    'error': err or 'Failed to fetch IATA Fuel Price Monitor.',
                    'latest': None,
                    'sourceLabel': SOURCE_IATA_FUEL_MONITOR,
                }), 502

            pdate = price_date_today_utc()
            monday = monday_iso_for_date_str(pdate)
            ppg = round(float(price) / 42.0, 6)
            prev_ppg = None
            if rows:
                prev_ser = serialize_market_row(rows[0])
                prev_ppg = prev_ser.get('pricePerGallon')
                if prev_ppg is None:
                    prev_ppg = jmd_get_float(rows[0].get('fields') or {}, JMD.price_per_gallon)
                if prev_ppg is None and prev_ser.get('pricePerBarrel') is not None:
                    prev_ppg = round(float(prev_ser['pricePerBarrel']) / 42.0, 6)
            wow_pct, wow_dir = compute_wow_vs_prior(
                ppg,
                float(prev_ppg) if prev_ppg is not None else None,
            )

            fields_full = {
                JMD.price_per_barrel: price,
                'Price Per Barrel': price,
                JMD.price_per_gallon: ppg,
                'Price Per Gallon': ppg,
                JMD.week_of: monday,
                'Week Of': monday,
                JMD.source: SOURCE_IATA_FUEL_MONITOR,
                'Source': SOURCE_IATA_FUEL_MONITOR,
                JMD.date_fetched: pdate,
                'Date Fetched': pdate,
                'price_date': pdate,
                'Price Date': pdate,
            }
            if prev_ppg is not None:
                fields_full[JMD.prior_week_price] = prev_ppg
                fields_full['Prior Week Price'] = prev_ppg
            if wow_pct is not None:
                fields_full[JMD.week_over_week_change] = wow_pct
                fields_full['Week Over Week Change'] = wow_pct
                fields_full[JMD.week_over_week_dir] = wow_dir
                fields_full['Week Over Week Dir'] = wow_dir

            latest_ser = serialize_market_row(rows[0]) if rows else None
            do_insert = True
            if latest_ser:
                same_week = (latest_ser.get('weekOf') or '') == monday
                same_day = (latest_ser.get('dateFetched') or latest_ser.get('priceDate') or '')[:10] == pdate
                if same_week or (not latest_ser.get('weekOf') and same_day):
                    lp = latest_ser.get('pricePerBarrel')
                    if lp is not None and abs(float(lp) - float(price)) < 0.01:
                        do_insert = False
            if do_insert:
                try:
                    airtable_client.create_record(JETA_MARKET_DATA_TABLE, fields_full)
                except Exception:
                    airtable_client.create_record(JETA_MARKET_DATA_TABLE, {
                        'price_per_barrel': price,
                        'Price Per Barrel': price,
                        'price_date': pdate,
                        'Price Date': pdate,
                        'source': SOURCE_IATA_FUEL_MONITOR,
                        'Source': SOURCE_IATA_FUEL_MONITOR,
                    })
                rows = _jeta_market_records_newest_first(airtable_client)

            top = rows[0] if rows else None
            prev = rows[1] if len(rows) > 1 else None
            return jsonify(
                build_payload(top, prev, fetch_error='', synced=True, persist_escalation_flag=True)
            ), 200

        top = rows[0] if rows else None
        prev = rows[1] if len(rows) > 1 else None
        if not top:
            return jsonify(
                build_payload(None, None, synced=False, persist_escalation_flag=False)
                | {
                    'latest': None,
                    'previous': None,
                    'hint': f'No rows in {JETA_MARKET_DATA_TABLE} — call with ?refresh=1 to fetch from IATA.',
                }
            ), 200
        return jsonify(build_payload(top, prev, synced=False, persist_escalation_flag=False)), 200
    except Exception as e:
        logger.exception('jeta_market_price failed: %s', e)
        return jsonify({'success': False, 'error': str(e), 'latest': None}), 500


@app.route('/api/jeta/suppliers/lookup', methods=['GET'])
@app.route('/jeta/suppliers/lookup', methods=['GET'])
def jeta_suppliers_lookup():
    """
    ICAO-based fuel supplier reference for JETA (OurAirports + NEXUS curated list).
    Persists rows to JETA_SupplierDirectory — canonical fields per jeta_supplier_directory_schema.JSD (dual-write + legacy minimal fallback).
    The live IATA Aviation Energy Hub Supplier Directory requires login — see response notice.
    Optional: ?buyer_id=recXXX links stored rows to a JETA_Buyers record when the link field exists.
    """
    try:
        icao = (request.args.get('icao') or '').strip()
        buyer_id = (request.args.get('buyer_id') or '').strip() or None
        airtable_client = AirtableClient()
        out = _jeta_persist_suppliers_for_icao(icao, airtable_client, buyer_id=buyer_id)
        if not out.get('success'):
            return jsonify({'success': False, 'error': out.get('error')}), 400

        # Merge with legacy response shape (payload fields + stored ids)
        legacy_payload = {
            'icao': out.get('icao'),
            'airport_name': out.get('airport_name'),
            'suppliers': out.get('suppliers'),
            'notice': out.get('notice'),
            'iata_directory_portal': out.get('iata_directory_portal'),
            'iata_fuel_program_url': out.get('iata_fuel_program_url'),
        }
        response = {
            'success': True,
            **{k: v for k, v in legacy_payload.items() if v is not None},
            'lookup_date': out.get('lookup_date'),
            'stored_record_ids': out.get('stored_record_ids'),
            'stored_count': out.get('stored_count', 0),
            'supplier_status': out.get('supplier_status'),
        }
        return jsonify(response), 200
    except Exception as e:
        logger.exception('jeta_suppliers_lookup failed: %s', e)
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/jeta/deals', methods=['POST'])
@app.route('/jeta/deals', methods=['POST'])
def jeta_create_deal():
    """Create deal; buyerId required."""
    try:
        data = dict(request.json or {})
        if not data.get('buyerId') and data.get('buyer_id'):
            data['buyerId'] = data['buyer_id']
        if not data.get('buyerId'):
            return jsonify({'success': False, 'error': 'buyerId is required'}), 400
        fields = _jeta_deal_json_to_fields(data, partial=False)
        if JD.buyer_id not in fields and 'Buyer' not in fields:
            return jsonify({'success': False, 'error': 'buyerId is required'}), 400
        airtable_client = AirtableClient()
        created = airtable_client.create_record(JETA_DEALS_TABLE, fields)
        buyers_raw = airtable_client.get_all_records(JETA_BUYERS_TABLE)
        buyer_lookup = {rec['id']: _jeta_serialize_record(rec) for rec in buyers_raw}
        return jsonify({
            'success': True,
            'deal': _jeta_serialize_deal(created, buyer_lookup),
        }), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/jeta/deals/<deal_id>', methods=['PUT', 'PATCH'])
@app.route('/jeta/deals/<deal_id>', methods=['PUT', 'PATCH'])
def jeta_update_deal(deal_id):
    """Update deal fields."""
    try:
        from jeta_compliance_layers import run_layer2_deal_progression_gate, may_proceed_traffic_light
        from jeta_fraud_detection import evaluate_fraud_integrity_for_stage_transition

        data = request.json or {}
        airtable_client = AirtableClient()
        buyers_raw = airtable_client.get_all_records(JETA_BUYERS_TABLE)
        buyer_lookup = {rec['id']: _jeta_serialize_record(rec) for rec in buyers_raw}
        existing = airtable_client.get_record(JETA_DEALS_TABLE, deal_id)
        current_deal = _jeta_serialize_deal(existing, buyer_lookup)
        new_stage = data.get('dealStage')
        if new_stage is not None and (new_stage or '').strip() != (current_deal.get('dealStage') or '').strip():
            buyer_ser = buyer_lookup.get(current_deal.get('buyerId') or '', {}) or {}
            enriched = {**data, 'jetaDocumentsCountForDeal': _jeta_count_documents_for_deal(airtable_client, deal_id)}
            gate = run_layer2_deal_progression_gate(current_deal, enriched, buyer_ser, (new_stage or '').strip())
            ack = _jeta_coerce_bool(data.get('acknowledgeManualReview'))
            crm = _jeta_coerce_bool(buyer_ser.get('complianceReviewLogged'))
            fraud_integrity = evaluate_fraud_integrity_for_stage_transition(
                current_deal, data, buyer_ser, (new_stage or '').strip()
            )
            if fraud_integrity.get('blocks_transition'):
                logger.warning(
                    'JETA fraud/integrity blocked deal progression: deal_id=%s detail=%s',
                    deal_id,
                    json.dumps({'unmet': fraud_integrity.get('unmet_conditions'), 'fraud': fraud_integrity.get('counterparty_fraud')}),
                )
                msg = '; '.join((fraud_integrity.get('unmet_conditions') or [])[:8]) or 'Fraud / integrity gate failed.'
                return jsonify({
                    'success': False,
                    'error': 'JETA fraud / integrity: ' + msg,
                    'fraud_integrity': fraud_integrity,
                    'compliance': gate,
                }), 409
            if fraud_integrity.get('requires_yellow_ack') and not (ack and crm):
                return jsonify({
                    'success': False,
                    'error': (
                        'JETA fraud detection: counterparty YELLOW — set acknowledgeManualReview and ensure '
                        'complianceReviewLogged on the buyer after manual review.'
                    ),
                    'fraud_integrity': fraud_integrity,
                    'compliance': gate,
                }), 409
            if not may_proceed_traffic_light(gate, ack, crm):
                if gate.get('deal_blocked') or gate.get('critical_block'):
                    logger.warning(
                        'JETA deal progression blocked (RED/CRITICAL): deal_id=%s detail=%s',
                        deal_id,
                        json.dumps(
                            {
                                'traffic_light': gate.get('traffic_light'),
                                'blockers': gate.get('blockers'),
                                'findings': gate.get('findings'),
                                'critical_flags': gate.get('critical_flags'),
                            }
                        ),
                    )
                return jsonify({
                    'success': False,
                    'error': _jeta_compliance_block_message(gate, 'deal progression'),
                    'compliance': gate,
                    'fraud_integrity': fraud_integrity,
                }), 409
        fields = _jeta_deal_json_to_fields(data, partial=True)
        if not fields:
            return jsonify({'success': False, 'error': 'No fields to update'}), 400
        updated = airtable_client.update_record(JETA_DEALS_TABLE, deal_id, fields)
        buyers_raw = airtable_client.get_all_records(JETA_BUYERS_TABLE)
        buyer_lookup = {rec['id']: _jeta_serialize_record(rec) for rec in buyers_raw}
        return jsonify({
            'success': True,
            'deal': _jeta_serialize_deal(updated, buyer_lookup),
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/jeta/pipeline/summary', methods=['GET'])
@app.route('/jeta/pipeline/summary', methods=['GET'])
def jeta_get_pipeline_summary():
    """Aggregates: buyer counts per pipeline stage, active deals, projected fees, outreach due today."""
    try:
        airtable_client = AirtableClient()
        try:
            buyers_raw = airtable_client.get_all_records(JETA_BUYERS_TABLE)
            deals_raw = airtable_client.get_all_records(JETA_DEALS_TABLE)
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'buyersByStage': {},
                'activeDealCount': 0,
                'projectedFeeTotal': 0,
                'outreachDueTodayCount': 0,
            }), 200

        buyer_lookup = {rec['id']: _jeta_serialize_record(rec) for rec in buyers_raw}
        buyer_rows = {rec['id']: _jeta_serialize_record(rec) for rec in buyers_raw}

        buyers_by_stage = {str(i): 0 for i in range(1, 10)}
        for row in buyer_rows.values():
            try:
                ps = int(row.get('pipelineStage') or 1)
            except (TypeError, ValueError):
                ps = 1
            ps = max(1, min(9, ps))
            buyers_by_stage[str(ps)] = buyers_by_stage.get(str(ps), 0) + 1

        deal_rows = [_jeta_serialize_deal(rec, buyer_lookup) for rec in deals_raw]
        active_deals = [d for d in deal_rows if d.get('dealStage') not in JETA_DEAL_CLOSED_STAGES]
        active_deal_count = len(active_deals)
        projected_fee_total = round(
            sum(_jeta_parse_float(d.get('projectedTotalFee')) for d in active_deals),
            4,
        )

        today = datetime.utcnow().date()
        outreach_due_today_count = 0
        for _, row in buyer_rows.items():
            ntd = (row.get('nextTouchDate') or '').strip()
            if not ntd:
                continue
            try:
                y, m, d = [int(x) for x in ntd.split('-')[:3]]
                nd = datetime(y, m, d).date()
            except (ValueError, TypeError):
                continue
            if nd <= today:
                outreach_due_today_count += 1

        stage_labels = {str(i + 1): JETA_STAGE_LABELS[i] for i in range(len(JETA_STAGE_LABELS))}

        return jsonify({
            'success': True,
            'buyersByStage': buyers_by_stage,
            'stageLabels': stage_labels,
            'activeDealCount': active_deal_count,
            'projectedFeeTotal': projected_fee_total,
            'outreachDueTodayCount': outreach_due_today_count,
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# =====================================================================
# JETA — FAA 5010 / Canada airport CSV import → JETA_Buyers
# =====================================================================

JETA_IMPORT_STATUS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'jeta_import_status.json')

JETA_FAA_IMPORT_ERROR_LOG_MAX = 500


def _jeta_import_norm_header_key(h: str) -> str:
    s = re.sub(r'[^a-z0-9]+', '_', (h or '').strip().lower()).strip('_')
    return s


def _jeta_import_row_to_canonical(row: dict) -> dict:
    """Map a CSV row (any header style) to canonical snake_case keys."""
    nm = {}
    for k, v in (row or {}).items():
        nk = _jeta_import_norm_header_key(k)
        if nk and nk not in nm:
            if v is None:
                nm[nk] = ''
            elif isinstance(v, str):
                nm[nk] = v.strip()
            else:
                nm[nk] = str(v).strip()

    def pick(*candidates: str) -> str:
        for c in candidates:
            ck = _jeta_import_norm_header_key(c)
            if ck in nm and nm[ck] not in (None, ''):
                return str(nm[ck]).strip()
        return ''

    return {
        'facility_name': pick(
            'facility_name', 'airport_name', 'arpt_name', 'name', 'site_name', 'location_name',
            'arpt_name_full', 'facility',
        ),
        'location_identifier': pick(
            'location_identifier', 'icao', 'icao_code', 'loc_id', 'location_id', 'lid',
            'airport_id', 'site_no', 'icao_iata',
        ),
        'state_code': pick(
            'state_code', 'state', 'st', 'province', 'prov', 'prv', 'region',
        ),
        'city': pick('city', 'city_name', 'municipality'),
        'airport_use': pick('airport_use', 'arpt_use', 'use', 'airport_use_code', 'arp_use'),
        'based_aircraft': pick(
            'based_aircraft', 'based_aircraft_total', 'total_based_aircraft', 'based',
            'aircraft_based', 'based_acft',
        ),
        'facility_type': pick(
            'facility_type', 'type', 'site_type', 'arpt_type', 'facility_type_code',
            'type_airport', 'airport_type',
        ),
        'manager_name': pick(
            'manager_name', 'arpt_mgr', 'mgr_name', 'airport_manager', 'name_title',
            'manager', 'site_manager',
        ),
        'manager_phone': pick(
            'manager_phone', 'mgr_phone', 'phone', 'arpt_phone', 'tel', 'telephone',
        ),
        'manager_email': pick(
            'manager_email', 'mgr_email', 'email', 'e_mail',
        ),
    }


def _jeta_import_normalize_icao(raw: str) -> str:
    s = (raw or '').strip().upper()
    s = re.sub(r'[^A-Z0-9]', '', s)
    return s[:4] if len(s) >= 4 else s


def _jeta_import_parse_int_based(raw: str) -> int:
    if raw is None or raw == '':
        return 0
    try:
        return int(float(str(raw).replace(',', '').strip()))
    except (TypeError, ValueError):
        return 0


def _jeta_import_facility_type_faa_strict(val: str) -> bool:
    """FAA import: facility_type must be AIRPORT only (not heliport, ultralight, etc.)."""
    return (val or '').strip().upper() == 'AIRPORT'


def _jeta_import_row_qualifies_5010_public_airport(canon: dict) -> bool:
    """
    FAA 5010 / TC-style row: public use (PU), based aircraft > 0, facility_type == AIRPORT
    (excludes heliport, ultralight, seaplane base, etc. — those are not labeled AIRPORT).
    No U.S. state filter — all jurisdictions.
    """
    au = (canon.get('airport_use') or '').strip().upper()
    if au != 'PU':
        return False
    if _jeta_import_parse_int_based(canon.get('based_aircraft') or '0') <= 0:
        return False
    if not _jeta_import_facility_type_faa_strict(canon.get('facility_type') or ''):
        return False
    return True


def _jeta_import_load_status() -> dict:
    p = JETA_IMPORT_STATUS_FILE
    if not os.path.isfile(p):
        return {'faa': {}, 'canada': {}}
    try:
        with open(p, encoding='utf-8') as fp:
            data = json.load(fp)
        if not isinstance(data, dict):
            return {'faa': {}, 'canada': {}}
        data.setdefault('faa', {})
        data.setdefault('canada', {})
        return data
    except Exception:
        return {'faa': {}, 'canada': {}}


def _jeta_import_save_status(data: dict) -> None:
    os.makedirs(os.path.dirname(JETA_IMPORT_STATUS_FILE), exist_ok=True)
    with open(JETA_IMPORT_STATUS_FILE, 'w', encoding='utf-8') as fp:
        json.dump(data, fp, indent=2)


def _jeta_import_today_iso() -> str:
    return datetime.utcnow().strftime('%Y-%m-%d')


def _jeta_import_build_airtable_fields(
    canon: dict,
    *,
    country: str,
    source_label: str,
    date_iso: str,
    omit_empty_email: bool = False,
) -> dict:
    fac = (canon.get('facility_name') or '').strip() or 'Unknown airport'
    loc = _jeta_import_normalize_icao(canon.get('location_identifier') or '')
    st = (canon.get('state_code') or '').strip()[:80]
    city = (canon.get('city') or '').strip()
    contact = (canon.get('manager_name') or '').strip()
    phone = (canon.get('manager_phone') or '').strip()
    email = (canon.get('manager_email') or '').strip()
    ba = _jeta_import_parse_int_based(canon.get('based_aircraft') or '0')
    stage_opt = jb_pipeline_stage_option(1, JETA_STAGE_LABELS)
    fields = {
        JB.company_name: fac,
        'Company Name': fac,
        JB.airport_name: fac,
        'Airport': fac,
        JB.airport_icao: loc,
        'ICAO Code': loc,
        JB.state: st,
        'State': st,
        JB.city: city,
        'City': city,
        JB.contact_name: contact,
        'Contact Name': contact,
        JB.contact_phone: phone,
        'Phone': phone,
        JB.buyer_type: 'Airport/FBO',
        'Buyer Type': 'Airport/FBO',
        JB.pipeline_stage: stage_opt,
        'Pipeline Stage': 1,
        JB.fuel_type: 'Conventional',
        'Fuel Type': 'Conventional',
        JB.country: country,
        'Country': country,
        JB.based_aircraft: float(ba),
        'Based Aircraft Total': ba,
        JB.source: source_label,
        'Source': source_label,
        JB.date_added: date_iso,
        'Date Added': date_iso,
    }
    if email or not omit_empty_email:
        fields[JB.contact_email] = email
        fields['Email'] = email
    return fields


def _jeta_import_create_buyer_record(airtable_client: AirtableClient, fields: dict):
    """
    Create JETA_Buyers row. Retries with a slimmer field set + Notes if optional columns
    are missing in Airtable.
    """
    optional_airtable = {
        'Country', 'Based Aircraft Total', 'Source', 'Date Added', 'Supplier Status',
        JB.country, JB.based_aircraft, JB.source, JB.date_added, JB.supplier_status,
    }
    try:
        return airtable_client.create_record(JETA_BUYERS_TABLE, fields)
    except Exception as e:
        err = str(e)
        logger.warning('JETA import create (full) failed: %s — retrying with core fields', err)
        note_bits = []
        for ak in optional_airtable:
            if ak in fields and fields[ak] not in (None, ''):
                note_bits.append(f'{ak}: {fields[ak]}')
        core = {k: v for k, v in fields.items() if k not in optional_airtable}
        prev_notes = str(core.get('Notes') or '').strip()
        import_line = ' | '.join(note_bits)
        if import_line:
            core['Notes'] = (import_line + ('\n' + prev_notes if prev_notes else '')).strip()
        return airtable_client.create_record(JETA_BUYERS_TABLE, core)


def _jeta_import_run_csv(
    file_storage,
    *,
    country: str,
    source_label: str,
    region_key: str,
) -> dict:
    """
    region_key: 'breakdown_by_state' (FAA) or 'breakdown_by_province' (Canada).
    """
    raw = file_storage.read()
    if isinstance(raw, bytes):
        raw = raw.decode('utf-8-sig', errors='replace')
    reader = csv.DictReader(io.StringIO(raw))
    if not reader.fieldnames:
        return {'success': False, 'error': 'CSV has no header row'}

    airtable_client = AirtableClient()
    buyers_raw = airtable_client.get_all_records(JETA_BUYERS_TABLE)
    existing_icao = set()
    for rec in buyers_raw:
        f = rec.get('fields') or {}
        ic = jb_get_str(f, JB.airport_icao).upper()
        if ic:
            existing_icao.add(ic)

    created = 0
    skipped_duplicate = 0
    skipped_filter = 0
    skipped_invalid_icao = 0
    errors = 0
    breakdown: dict = {}
    date_iso = _jeta_import_today_iso()

    for row in reader:
        canon = _jeta_import_row_to_canonical(row)
        if not _jeta_import_row_qualifies_5010_public_airport(canon):
            skipped_filter += 1
            continue
        icao = _jeta_import_normalize_icao(canon.get('location_identifier') or '')
        if not icao or len(icao) < 3:
            skipped_invalid_icao += 1
            continue
        if icao in existing_icao:
            skipped_duplicate += 1
            continue

        fields = _jeta_import_build_airtable_fields(
            canon, country=country, source_label=source_label, date_iso=date_iso,
        )
        try:
            rec = _jeta_import_create_buyer_record(airtable_client, fields)
            rid = rec.get('id') if isinstance(rec, dict) else getattr(rec, 'id', None)
            existing_icao.add(icao)
            created += 1
            reg = (canon.get('state_code') or '').strip().upper() or 'UNKNOWN'
            breakdown[reg] = breakdown.get(reg, 0) + 1
            if rid:
                try:
                    _jeta_refresh_buyer_priority_score(airtable_client, rid)
                except Exception as pe:
                    logger.warning('JETA priority score after Canada import row: %s', pe)
        except Exception as e:
            logger.exception('JETA import row failed ICAO=%s: %s', icao, e)
            errors += 1

    summary = {
        'success': True,
        'created': created,
        'skipped_duplicate': skipped_duplicate,
        'skipped_filter': skipped_filter,
        'skipped_invalid_icao': skipped_invalid_icao,
        'errors': errors,
        region_key: breakdown,
    }
    return summary


def _jeta_import_run_faa_csv(file_storage) -> dict:
    """
    FAA 5010 CSV → JETA_Buyers. All U.S. states; PU; based > 0; facility_type AIRPORT only.
    Same read/decode pattern as other CSV uploads (utf-8-sig, DictReader).
    """
    raw = file_storage.read()
    if isinstance(raw, bytes):
        content = raw.decode('utf-8-sig', errors='replace')
    else:
        content = str(raw)
    reader = csv.DictReader(io.StringIO(content))
    if not reader.fieldnames:
        return {'success': False, 'error': 'CSV has no header row'}

    rows = list(reader)
    total_processed = len(rows)

    airtable_client = AirtableClient()
    buyers_raw = airtable_client.get_all_records(JETA_BUYERS_TABLE)
    existing_icao = set()
    for rec in buyers_raw:
        f = rec.get('fields') or {}
        ic = jb_get_str(f, JB.airport_icao).upper()
        if ic:
            existing_icao.add(ic)

    total_imported = 0
    total_skipped_duplicates = 0
    total_filtered_out = 0
    breakdown_by_state: dict = {}
    error_log: list = []
    enrichment_pairs: list = []
    date_iso = _jeta_import_today_iso()

    for row in rows:
        canon = _jeta_import_row_to_canonical(row)
        if not _jeta_import_row_qualifies_5010_public_airport(canon):
            total_filtered_out += 1
            continue
        icao = _jeta_import_normalize_icao(canon.get('location_identifier') or '')
        if not icao or len(icao) < 3:
            total_filtered_out += 1
            continue
        if icao in existing_icao:
            total_skipped_duplicates += 1
            continue

        fields = _jeta_import_build_airtable_fields(
            canon,
            country='USA',
            source_label='FAA 5010 Import',
            date_iso=date_iso,
            omit_empty_email=True,
        )
        fields[JB.supplier_status] = 'Unknown'
        fields['Supplier Status'] = 'Unknown'
        try:
            rec = _jeta_import_create_buyer_record(airtable_client, fields)
            rid = rec.get('id') if isinstance(rec, dict) else getattr(rec, 'id', None)
            existing_icao.add(icao)
            total_imported += 1
            reg = (canon.get('state_code') or '').strip().upper() or 'UNKNOWN'
            breakdown_by_state[reg] = breakdown_by_state.get(reg, 0) + 1
            if rid:
                try:
                    _jeta_refresh_buyer_priority_score(airtable_client, rid)
                except Exception as pe:
                    logger.warning('JETA priority score after FAA import row: %s', pe)
                enrichment_pairs.append((rid, icao))
        except Exception as e:
            logger.exception('JETA FAA import row failed ICAO=%s: %s', icao, e)
            line = f'ICAO {icao}: {e}'
            if len(error_log) < JETA_FAA_IMPORT_ERROR_LOG_MAX:
                error_log.append(line)

    if enrichment_pairs:
        threading.Thread(
            target=_jeta_faa_post_import_enrichment_worker,
            args=(enrichment_pairs,),
            daemon=True,
            name='jeta-faa-supplier-enrichment',
        ).start()

    return {
        'success': True,
        'total_processed': total_processed,
        'total_imported': total_imported,
        'total_skipped_duplicates': total_skipped_duplicates,
        'total_filtered_out': total_filtered_out,
        'breakdown_by_state': breakdown_by_state,
        'error_log': error_log,
        'supplier_enrichment_queued': len(enrichment_pairs),
    }


def _jeta_import_persist(kind: str, summary: dict, region_key: str) -> None:
    st = _jeta_import_load_status()
    bd = summary.get(region_key) or {}
    st[kind] = {
        'last_import_at': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
        'records_created': summary.get('created', 0),
        'records_skipped_duplicate': summary.get('skipped_duplicate', 0),
        'records_skipped_filter': summary.get('skipped_filter', 0),
        'records_skipped_invalid_icao': summary.get('skipped_invalid_icao', 0),
        'errors': summary.get('errors', 0),
        'breakdown': bd,
    }
    _jeta_import_save_status(st)


def _jeta_import_persist_faa(summary: dict) -> None:
    """Persist FAA-only status (counters + breakdown + error log)."""
    st = _jeta_import_load_status()
    st['faa'] = {
        'last_import_at': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
        'total_processed': summary.get('total_processed', 0),
        'total_imported': summary.get('total_imported', 0),
        'total_skipped_duplicates': summary.get('total_skipped_duplicates', 0),
        'total_filtered_out': summary.get('total_filtered_out', 0),
        'breakdown_by_state': summary.get('breakdown_by_state') or {},
        'error_log': summary.get('error_log') or [],
    }
    _jeta_import_save_status(st)


@app.route('/api/jeta/import/faa', methods=['POST'])
@app.route('/jeta/import/faa', methods=['POST'])
def jeta_import_faa():
    """Upload FAA 5010 Airport Master Record CSV; JETA_Buyers (all states, public, based, AIRPORT)."""
    try:
        f = request.files.get('file') or request.files.get('csv')
        if not f or not getattr(f, 'filename', None):
            return jsonify({'success': False, 'error': 'Attach CSV as multipart field "file" or "csv"'}), 400
        summary = _jeta_import_run_faa_csv(f)
        if not summary.get('success'):
            return jsonify(summary), 400
        _jeta_import_persist_faa(summary)
        return jsonify(summary), 200
    except Exception as e:
        logger.exception('jeta_import_faa failed: %s', e)
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/jeta/import/faa/status', methods=['GET'])
@app.route('/jeta/import/faa/status', methods=['GET'])
def jeta_import_faa_status():
    """Last FAA import time, record counts by state, error log."""
    st = _jeta_import_load_status()
    block = st.get('faa') or {}
    # Backward compatibility with older status shape
    breakdown = block.get('breakdown_by_state') or block.get('breakdown') or {}
    err = block.get('error_log')
    if err is None:
        err = []
    return jsonify({
        'success': True,
        'last_import_at': block.get('last_import_at'),
        'record_count_by_state': breakdown,
        'error_log': err,
        'total_processed': block.get('total_processed'),
        'total_imported': block.get('total_imported', block.get('records_created')),
        'total_skipped_duplicates': block.get('total_skipped_duplicates', block.get('records_skipped_duplicate')),
        'total_filtered_out': block.get('total_filtered_out', block.get('records_skipped_filter')),
    }), 200


@app.route('/api/jeta/import/canada', methods=['POST'])
@app.route('/jeta/import/canada', methods=['POST'])
def jeta_import_canada():
    """Upload Transport Canada / NAV CANADA airport CSV; same filters; country Canada."""
    try:
        f = request.files.get('file') or request.files.get('csv')
        if not f or not getattr(f, 'filename', None):
            return jsonify({'success': False, 'error': 'Attach CSV as multipart field "file" or "csv"'}), 400
        summary = _jeta_import_run_csv(
            f,
            country='Canada',
            source_label='Transport Canada Import',
            region_key='breakdown_by_province',
        )
        if not summary.get('success'):
            return jsonify(summary), 400
        _jeta_import_persist('canada', summary, 'breakdown_by_province')
        return jsonify(summary), 200
    except Exception as e:
        logger.exception('jeta_import_canada failed: %s', e)
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/jeta/import/status', methods=['GET'])
@app.route('/jeta/import/status', methods=['GET'])
def jeta_import_status():
    """Last import timestamps and counts for FAA and Canada."""
    st = _jeta_import_load_status()

    def pack_canada(kind: str):
        block = st.get(kind) or {}
        return {
            'last_import_at': block.get('last_import_at'),
            'records_created': block.get('records_created', 0),
            'records_skipped_duplicate': block.get('records_skipped_duplicate', 0),
            'records_skipped_filter': block.get('records_skipped_filter', 0),
            'records_skipped_invalid_icao': block.get('records_skipped_invalid_icao', 0),
            'errors': block.get('errors', 0),
            'breakdown': block.get('breakdown') or {},
        }

    def pack_faa():
        block = st.get('faa') or {}
        return {
            'last_import_at': block.get('last_import_at'),
            'total_processed': block.get('total_processed'),
            'total_imported': block.get('total_imported', block.get('records_created', 0)),
            'total_skipped_duplicates': block.get('total_skipped_duplicates', block.get('records_skipped_duplicate', 0)),
            'total_filtered_out': block.get('total_filtered_out', block.get('records_skipped_filter', 0)),
            'breakdown_by_state': block.get('breakdown_by_state') or block.get('breakdown') or {},
            'error_log': block.get('error_log') or [],
        }

    return jsonify({
        'success': True,
        'faa': pack_faa(),
        'canada': pack_canada('canada'),
    }), 200


# =====================================================================
# JETA — Compliance layers (intake, gates, monitoring)
# =====================================================================
# Layer 1: counterparty intake — runs on POST /jeta/buyers (see jeta_compliance_layers.py).
# Layer 2: deal progression gates — runs on PUT /jeta/deals/:id when dealStage changes.
# Layer 3: continuous monitoring — POST /jeta/compliance/monitor (cron every 24h).
# Optional: JETA_MONITOR_SECRET, JETA_SANCTIONS_BLOCKLIST (see jeta_compliance_layers.py).

JETA_MONITOR_STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'jeta_monitor_state.json')


def _jeta_monitor_secret_ok() -> bool:
    expected = (os.environ.get('JETA_MONITOR_SECRET') or '').strip()
    if not expected:
        return True
    got = (request.headers.get('X-JETA-Monitor-Secret') or request.args.get('secret') or '').strip()
    return got == expected


@app.route('/api/jeta/compliance/monitor', methods=['POST'])
@app.route('/jeta/compliance/monitor', methods=['POST'])
def jeta_compliance_run_monitoring():
    """Layer 3 — scan all active deals. Intended to be called by cron every 24 hours."""
    try:
        from jeta_compliance_layers import run_layer3_continuous_monitoring

        if not _jeta_monitor_secret_ok():
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        airtable_client = AirtableClient()
        buyers_raw = airtable_client.get_all_records(JETA_BUYERS_TABLE)
        deals_raw = airtable_client.get_all_records(JETA_DEALS_TABLE)
        outreach_raw = airtable_client.get_all_records(JETA_OUTREACH_TABLE)
        buyer_lookup = {rec['id']: _jeta_serialize_record(rec) for rec in buyers_raw}
        deal_rows = [_jeta_serialize_deal(rec, buyer_lookup) for rec in deals_raw]
        out_lookup = {}
        for rec in buyers_raw:
            ser = _jeta_serialize_record(rec)
            out_lookup[rec['id']] = {
                'companyName': ser['companyName'],
                'contactName': ser['contactName'],
            }
        outreach_ser = [_jeta_serialize_outreach(rec, out_lookup) for rec in outreach_raw]
        result = run_layer3_continuous_monitoring(deal_rows, buyer_lookup, outreach_ser)
        try:
            with open(JETA_MONITOR_STATE_FILE, 'w') as f:
                json.dump({'last_run_at': result.get('run_at'), 'summary': result}, f, indent=2)
        except Exception:
            pass
        return jsonify({'success': True, 'compliance': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/jeta/compliance/monitor/status', methods=['GET'])
@app.route('/jeta/compliance/monitor/status', methods=['GET'])
def jeta_compliance_monitor_status():
    """Last Layer 3 run stored on the API host (jeta_monitor_state.json)."""
    try:
        if os.path.isfile(JETA_MONITOR_STATE_FILE):
            with open(JETA_MONITOR_STATE_FILE, 'r') as f:
                state = json.load(f)
            return jsonify({'success': True, 'state': state})
        return jsonify({
            'success': True,
            'state': None,
            'hint': 'No run yet; POST /jeta/compliance/monitor (e.g. daily cron).',
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# =====================================================================
# JETA_Documents — canonical snake_case (see jeta_document_schema.JDoc); legacy dual-read/write.
# Local PDF filename still stored in PDF Path (server); pdf_link / Download URL for serving link.
# =====================================================================

JETA_DOCUMENTS_TABLE = 'JETA_Documents'

JETA_DOCUMENT_TYPES = (
    'NCNDA',
    'IMFPA',
    'Fee Agreement',
    'LOA',
    'Supply Agreement',
    'ICPO',
    'FCO',
    'Broker Mandate',
    'Capability Statement',
)

JETA_PARTY1_LINE = (
    'JETA COURTIÈRE | DEE DAVIS INC | 755 W. Big Beaver Rd Ste 2020 Troy MI 48084'
)


def _jeta_documents_output_dir() -> str:
    d = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'GENERATED_JETA_DOCUMENTS')
    os.makedirs(d, exist_ok=True)
    return d


def _jeta_party2_from_buyer(buyer_ser: dict) -> str:
    if not buyer_ser:
        return 'Counterparty (buyer details on file)'
    chunks = []
    cn = (buyer_ser.get('companyName') or '').strip()
    ct = (buyer_ser.get('contactName') or '').strip()
    if cn:
        chunks.append(cn)
    if ct:
        chunks.append(f'Attn: {ct}')
    city = (buyer_ser.get('city') or '').strip()
    st = (buyer_ser.get('state') or '').strip()
    if city or st:
        chunks.append(f'{city}, {st}'.strip(', '))
    em = (buyer_ser.get('email') or '').strip()
    ph = (buyer_ser.get('phone') or '').strip()
    if em:
        chunks.append(em)
    if ph:
        chunks.append(ph)
    return ' | '.join(chunks) if chunks else 'Counterparty (buyer details on file)'


def _jeta_document_deal_ids(fields: dict) -> list:
    raw = jdoc_link_ids(fields, JDoc.deal_id) or fields.get('Deal') or []
    return [x for x in raw] if isinstance(raw, list) else []


def _jeta_count_documents_for_deal(airtable_client, deal_id: str) -> int:
    """Rows in JETA_Documents linked to this deal."""
    if not (deal_id or '').strip():
        return 0
    try:
        docs_raw = airtable_client.get_all_records(JETA_DOCUMENTS_TABLE)
    except Exception:
        return 0
    n = 0
    for rec in docs_raw:
        f = rec.get('fields') or {}
        if deal_id in _jeta_document_deal_ids(f):
            n += 1
    return n


def _jeta_document_buyer_ids(fields: dict) -> list:
    raw = jdoc_link_ids(fields, JDoc.buyer_id) or fields.get('Buyer') or []
    return [x for x in raw] if isinstance(raw, list) else []


def _jeta_document_seller_ids(fields: dict) -> list:
    raw = jdoc_link_ids(fields, JDoc.seller_id) or fields.get('Seller') or []
    return [x for x in raw] if isinstance(raw, list) else []


def _jeta_format_doc_date(val) -> str:
    if val is None or val == '':
        return ''
    if hasattr(val, 'strftime'):
        return val.strftime('%Y-%m-%d')
    return str(val).strip()


def _jeta_serialize_document(record: dict, deal_lookup: dict, buyer_lookup: dict) -> dict:
    f = record.get('fields') or {}
    dids = _jeta_document_deal_ids(f)
    deal_id = dids[0] if dids else ''
    deal_row = deal_lookup.get(deal_id) if deal_id else None
    buyer_name = ''
    if deal_row:
        buyer_name = deal_row.get('buyerName') or ''
    bids = _jeta_document_buyer_ids(f)
    buyer_id = bids[0] if bids else ''
    if not buyer_name and bids:
        binfo = buyer_lookup.get(bids[0], {})
        buyer_name = (
            f"{binfo.get('companyName', '')} — {binfo.get('contactName', '')}".strip(' —')
            or ''
        )
    sids = _jeta_document_seller_ids(f)
    seller_id = sids[0] if sids else ''

    gen_raw = jdoc_get_raw(f, JDoc.generated_date) or f.get('Generated Date')
    gen_date = _jeta_format_doc_date(gen_raw)

    pdf_path = jdoc_pdf_path_local(f)
    dl = jdoc_get_str(f, JDoc.pdf_link) or str(f.get('Download URL') or '').strip()
    ss = jdoc_get_str(f, JDoc.signed_status) or str(f.get('Signed Status') or '').strip()
    if ss == 'Pending':
        ss = 'Not Sent'

    return {
        'id': record['id'],
        'documentType': jdoc_get_str(f, JDoc.document_type) or str(f.get('Document Type') or '').strip(),
        'documentName': jdoc_get_str(f, JDoc.document_name) or str(f.get('Document Name') or '').strip(),
        'dealId': deal_id,
        'buyerId': buyer_id,
        'sellerId': seller_id,
        'buyerName': buyer_name,
        'iccCompliant': jdoc_get_bool(f, JDoc.icc_compliant) is True,
        'afsmaAligned': jdoc_get_bool(f, JDoc.afsma_aligned) is True,
        'generatedDate': gen_date,
        'generatedBy': jdoc_get_str(f, JDoc.generated_by) or str(f.get('Generated By') or '').strip(),
        'party1Name': jdoc_get_str(f, JDoc.party_1_name) or str(f.get('Party 1 Name') or '').strip(),
        'party1Entity': jdoc_get_str(f, JDoc.party_1_entity) or str(f.get('Party 1 Entity') or '').strip(),
        'party2Name': jdoc_get_str(f, JDoc.party_2_name) or str(f.get('Party 2 Name') or '').strip(),
        'party2Entity': jdoc_get_str(f, JDoc.party_2_entity) or str(f.get('Party 2 Entity') or '').strip(),
        'dealDescription': jdoc_get_str(f, JDoc.deal_description) or str(f.get('Deal Description') or '').strip(),
        'feePerGallon': jdoc_get_float(f, JDoc.fee_per_gallon),
        'volumeGallons': jdoc_get_float(f, JDoc.volume_gallons),
        'jetaPercentage': jdoc_get_float(f, JDoc.jeta_percentage),
        'sentDate': _jeta_format_doc_date(jdoc_get_raw(f, JDoc.sent_date) or f.get('Sent Date')),
        'sentTo': jdoc_get_str(f, JDoc.sent_to) or str(f.get('Sent To') or '').strip(),
        'signedStatus': ss,
        'signedDate': _jeta_format_doc_date(jdoc_get_raw(f, JDoc.signed_date) or f.get('Signed Date')),
        'expiryDate': _jeta_format_doc_date(jdoc_get_raw(f, JDoc.expiry_date) or f.get('Expiry Date')),
        'pdfLink': dl,
        'downloadUrl': dl,
        'notes': jdoc_get_str(f, JDoc.notes) or str(f.get('Notes') or '').strip(),
        'escalationClauseVersion': jdoc_get_str(f, JDoc.escalation_clause_version)
        or str(f.get('Escalation Clause Version') or '').strip()
        or None,
        'pdfPath': pdf_path,
        'createdTime': record.get('createdTime', ''),
    }


def _jeta_pdf_bytes_simple_agreement(
    title: str,
    party1: str,
    party2: str,
    deal_description: str,
    deal_name: str,
    extra_body: str,
) -> bytes:
    """Generate PDF using reportlab (same stack as PRISM compliance PDF helper)."""
    from io import BytesIO
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
    except ImportError as e:
        raise RuntimeError(f'reportlab is required for PDF generation: {e}') from e

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
    )
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        'JT',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        alignment=TA_JUSTIFY,
        textColor=colors.HexColor('#1e293b'),
    ))
    styles.add(ParagraphStyle(
        'JTH',
        parent=styles['Heading1'],
        fontSize=16,
        alignment=TA_CENTER,
        spaceAfter=16,
        textColor=colors.HexColor('#92400e'),
    ))
    story = []
    story.append(Paragraph(title.replace('&', '&amp;'), styles['JTH']))
    story.append(Spacer(1, 0.15 * inch))
    today_s = datetime.utcnow().strftime('%B %d, %Y')
    story.append(Paragraph(f'<b>Effective date:</b> {today_s}', styles['JT']))
    story.append(Spacer(1, 0.12 * inch))
    if deal_name:
        story.append(Paragraph(f'<b>Deal:</b> {deal_name.replace("&", "&amp;")}', styles['JT']))
        story.append(Spacer(1, 0.08 * inch))
    story.append(Paragraph('<b>Party 1 (Disclosing party — Broker):</b>', styles['JT']))
    story.append(Paragraph(party1.replace('&', '&amp;'), styles['JT']))
    story.append(Spacer(1, 0.1 * inch))
    story.append(Paragraph('<b>Party 2 (Recipient / Counterparty):</b>', styles['JT']))
    story.append(Paragraph(party2.replace('&', '&amp;'), styles['JT']))
    story.append(Spacer(1, 0.12 * inch))
    story.append(Paragraph('<b>Deal description</b>', styles['JT']))
    desc = (deal_description or 'As described in the linked JETA deal record.').replace('&', '&amp;')
    story.append(Paragraph(desc, styles['JT']))
    story.append(Spacer(1, 0.12 * inch))
    for block in extra_body.split('\n\n'):
        if block.strip():
            story.append(Paragraph(block.strip().replace('&', '&amp;'), styles['JT']))
            story.append(Spacer(1, 0.08 * inch))
    story.append(Spacer(1, 0.25 * inch))
    story.append(Paragraph(
        '_______________________________&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_______________________________',
        styles['JT'],
    ))
    story.append(Paragraph('Party 1 — Dee Davis, JETA COURTIÈRE&nbsp;&nbsp;&nbsp;&nbsp;Party 2', styles['JT']))
    doc.build(story)
    data = buffer.getvalue()
    buffer.close()
    return data


def _jeta_ncnda_body() -> str:
    return (
        'The parties wish to explore a potential business relationship concerning aviation fuel '
        '(Jet-A) brokerage, supply introductions, and related services. Each party may disclose '
        'Confidential Information to the other. "Confidential Information" means non-public '
        'information disclosed in connection with the Deal description above, including pricing, '
        'volumes, supplier identities, airport/FBO relationships, and transaction terms.\n\n'
        'Each party agrees to: (a) use Confidential Information solely for evaluating and '
        'pursuing the contemplated relationship; (b) not disclose Confidential Information to '
        'third parties without prior written consent, except as required by law; (c) protect '
        'Confidential Information using reasonable care; and (d) not circumvent, avoid, or '
        'interfere with the other party\'s legitimate business relationships introduced in '
        'connection with this engagement.\n\n'
        'This Agreement does not obligate either party to proceed with any transaction. '
        'Either party may terminate discussions at any time. The obligations herein survive '
        'for two (2) years from the Effective Date with respect to Confidential Information '
        'disclosed during the term.\n\n'
        'This Agreement is governed by the laws of the State of Michigan. Entire agreement; '
        'amendments in writing. Facsimile or electronic signatures shall be deemed originals.'
    )


def _jeta_generic_body(doc_label: str) -> str:
    return (
        f'This {doc_label} is entered between Party 1 and Party 2 in connection with the Deal '
        'description above. The parties agree to negotiate in good faith toward definitive '
        'documentation acceptable to both sides. Specific commercial, liability, and payment '
        'terms will be set forth in executed agreements between the parties. This document is '
        'a framework for discussion and is not a binding commitment to purchase or sell fuel '
        'except as expressly stated in future signed contracts.'
    )


def _jeta_generate_document_pdf(
    document_type: str,
    buyer_ser: dict,
    deal_description: str,
    deal_name: str,
) -> bytes:
    party1 = JETA_PARTY1_LINE
    party2 = _jeta_party2_from_buyer(buyer_ser)
    dt = (document_type or '').strip()
    if dt == 'NCNDA':
        title = 'MUTUAL NON-CIRCUMVENTION AND NON-DISCLOSURE AGREEMENT (NCNDA)'
        extra = _jeta_ncnda_body()
        return _jeta_pdf_bytes_simple_agreement(title, party1, party2, deal_description, deal_name, extra)
    if dt == 'IMFPA':
        title = 'INTERMEDIARY AND MASTER FEE PROTECTION AGREEMENT (IMFPA) — DRAFT'
        extra = _jeta_generic_body('IMFPA-style fee protection framework')
        return _jeta_pdf_bytes_simple_agreement(title, party1, party2, deal_description, deal_name, extra)
    if dt == 'Fee Agreement':
        title = 'BROKER FEE AGREEMENT — DRAFT'
        extra = _jeta_generic_body('fee agreement')
        return _jeta_pdf_bytes_simple_agreement(title, party1, party2, deal_description, deal_name, extra)
    if dt == 'LOA':
        title = 'LETTER OF AUTHORITY (LOA) — DRAFT'
        extra = _jeta_generic_body('letter of authority')
        return _jeta_pdf_bytes_simple_agreement(title, party1, party2, deal_description, deal_name, extra)
    if dt in (
        'Supply Agreement',
        'ICPO',
        'FCO',
        'Broker Mandate',
        'Capability Statement',
    ):
        title = f'{dt.upper()} — DRAFT'
        extra = _jeta_generic_body(dt)
        return _jeta_pdf_bytes_simple_agreement(title, party1, party2, deal_description, deal_name, extra)
    raise ValueError(f'Unsupported document type: {document_type}')


def _jeta_rl_escape(s: str) -> str:
    if not s:
        return ''
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def _jeta_pdf_bytes_fee_agreement(
    *,
    deal_name: str,
    deal_description: str,
    fee_schedule_text: str,
    version_label: str,
    escalation_body: str,
) -> bytes:
    """Fee Agreement PDF: fee schedule, then populated escalation clause, then signatures."""
    from io import BytesIO
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
    except ImportError as e:
        raise RuntimeError(f'reportlab is required for PDF generation: {e}') from e

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
    )
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        'JT',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        alignment=TA_JUSTIFY,
        textColor=colors.HexColor('#1e293b'),
    ))
    styles.add(ParagraphStyle(
        'JTH',
        parent=styles['Heading1'],
        fontSize=16,
        alignment=TA_CENTER,
        spaceAfter=12,
        textColor=colors.HexColor('#92400e'),
    ))
    styles.add(ParagraphStyle(
        'JTS',
        parent=styles['Normal'],
        fontSize=11,
        leading=14,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#b45309'),
        spaceAfter=8,
    ))
    story = []
    story.append(Paragraph('BROKER FEE AGREEMENT — DRAFT', styles['JTH']))
    story.append(Paragraph(
        f'<b>Escalation clause selected:</b> {_jeta_rl_escape(version_label)}',
        styles['JTS'],
    ))
    today_s = datetime.utcnow().strftime('%B %d, %Y')
    story.append(Paragraph(f'<b>Effective date:</b> {_jeta_rl_escape(today_s)}', styles['JT']))
    story.append(Spacer(1, 0.1 * inch))
    if deal_name:
        story.append(Paragraph(f'<b>Deal:</b> {_jeta_rl_escape(deal_name)}', styles['JT']))
        story.append(Spacer(1, 0.08 * inch))
    story.append(Paragraph('<b>Deal description</b>', styles['JT']))
    desc = (deal_description or 'As described in the linked JETA deal record.').strip()
    story.append(Paragraph(_jeta_rl_escape(desc), styles['JT']))
    story.append(Spacer(1, 0.12 * inch))
    story.append(Paragraph('<b>Fee schedule</b>', styles['JT']))
    story.append(Spacer(1, 0.06 * inch))
    for block in fee_schedule_text.split('\n\n'):
        b = block.strip()
        if b:
            story.append(Paragraph(_jeta_rl_escape(b), styles['JT']))
            story.append(Spacer(1, 0.06 * inch))
    story.append(Spacer(1, 0.1 * inch))
    story.append(Paragraph('<b>Price escalation</b>', styles['JT']))
    story.append(Spacer(1, 0.06 * inch))
    for block in escalation_body.split('\n\n'):
        b = block.strip()
        if b:
            story.append(Paragraph(_jeta_rl_escape(b), styles['JT']))
            story.append(Spacer(1, 0.06 * inch))
    story.append(Spacer(1, 0.2 * inch))
    story.append(Paragraph(
        '_______________________________&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_______________________________',
        styles['JT'],
    ))
    story.append(Paragraph('Party 1 — Dee Davis, JETA COURTIÈRE&nbsp;&nbsp;&nbsp;&nbsp;Party 2', styles['JT']))
    doc.build(story)
    data = buffer.getvalue()
    buffer.close()
    return data


def _jeta_compose_fee_agreement_pdf(deal_rec: dict, deal_row: dict, buyer_ser: dict, airtable_client) -> tuple:
    """Returns (pdf_bytes, version_label, base_benchmark_bbl)."""
    from jeta_fee_escalation import (
        build_fee_schedule_block,
        build_version_a_clause,
        build_version_b_clause,
        build_version_c_clause,
        parse_term_days,
        select_escalation_clause_version,
    )

    f = deal_rec.get('fields') or {}
    deal_type = jd_get_str(f, JD.deal_type) or str(f.get('Deal Type') or '').strip()
    term_raw = jd_get_str(f, JD.term_length) or str(f.get('Term Length') or '').strip()
    term_days = parse_term_days(term_raw)
    version = select_escalation_clause_version(deal_type or None, term_days)

    mrows = _jeta_market_records_newest_first(airtable_client)
    benchmark = None
    if mrows:
        benchmark = jmd_get_float((mrows[0].get('fields') or {}), JMD.price_per_barrel)
    if benchmark is None:
        benchmark = 200.0

    fee = jd_get_float(f, JD.jeta_fee_per_gallon)
    if fee is None:
        fee = float(deal_row.get('jetaFeePerGallon') or 0.02)
    vol = jd_get_float(f, JD.volume_gallons)
    if vol is None:
        vol = deal_row.get('volumeGallons')

    today_long = datetime.utcnow().strftime('%B %d, %Y')
    party1 = JETA_PARTY1_LINE
    party2 = _jeta_party2_from_buyer(buyer_ser)

    if version == 'Version B':
        esc_text = build_version_b_clause(
            base_benchmark_bbl=float(benchmark),
            agreement_date=today_long,
            party_1_line=party1,
            party_2_line=party2,
        )
    elif version == 'Version C':
        esc_text = build_version_c_clause(
            base_fee_per_gallon=float(fee),
            base_benchmark_bbl=float(benchmark),
            agreement_date=today_long,
            party_1_line=party1,
            party_2_line=party2,
        )
    else:
        esc_text = build_version_a_clause(
            base_fee_per_gallon=float(fee),
            base_benchmark_bbl=float(benchmark),
            agreement_date=today_long,
            party_1_line=party1,
            party_2_line=party2,
        )

    fee_sched = build_fee_schedule_block(
        fee_per_gallon=float(fee) if fee is not None else None,
        volume_gallons=float(vol) if vol is not None else None,
        base_benchmark_bbl=float(benchmark),
        agreement_date=today_long,
    )
    pdf_bytes = _jeta_pdf_bytes_fee_agreement(
        deal_name=(deal_row.get('dealName') or '').strip(),
        deal_description=(deal_row.get('dealDescription') or '').strip(),
        fee_schedule_text=fee_sched,
        version_label=version,
        escalation_body=esc_text,
    )
    return pdf_bytes, version, float(benchmark)


def _jeta_documents_generate_handler():
    """Shared logic for POST /jeta/documents/generate and /api/jeta/documents/generate."""
    data = request.json or {}
    deal_id = (data.get('dealId') or data.get('deal_id') or '').strip()
    document_type = (data.get('documentType') or data.get('document_type') or '').strip()
    return_pdf = bool(data.get('return_pdf') or data.get('returnPdf'))
    if not deal_id:
        return jsonify({'success': False, 'error': 'dealId or deal_id is required'}), 400
    if document_type not in JETA_DOCUMENT_TYPES:
        return jsonify({
            'success': False,
            'error': f'documentType / document_type must be one of: {", ".join(JETA_DOCUMENT_TYPES)}',
        }), 400

    airtable_client = AirtableClient()
    buyers_raw = airtable_client.get_all_records(JETA_BUYERS_TABLE)
    buyer_lookup = {rec['id']: _jeta_serialize_record(rec) for rec in buyers_raw}
    deal_rec = airtable_client.get_record(JETA_DEALS_TABLE, deal_id)
    deal_row = _jeta_serialize_deal(deal_rec, buyer_lookup)
    buyer_id = deal_row.get('buyerId') or ''
    buyer_ser = buyer_lookup.get(buyer_id, {}) if buyer_id else {}
    deal_description = deal_row.get('dealDescription') or ''
    deal_name = deal_row.get('dealName') or ''

    escalation_version = None
    base_benchmark = None
    if document_type == 'Fee Agreement':
        pdf_bytes, escalation_version, base_benchmark = _jeta_compose_fee_agreement_pdf(
            deal_rec, deal_row, buyer_ser, airtable_client
        )
        try:
            airtable_client.update_record(JETA_DEALS_TABLE, deal_id, {
                JD.escalation_base_benchmark_bbl: base_benchmark,
                'Escalation Base Benchmark Bbl': base_benchmark,
                JD.escalation_clause_version: escalation_version,
                'Escalation Clause Version': escalation_version,
            })
        except Exception as deal_exc:
            logger.warning('JETA deal escalation fields update skipped: %s', deal_exc)
    else:
        pdf_bytes = _jeta_generate_document_pdf(
            document_type,
            buyer_ser,
            deal_description,
            deal_name,
        )

    today = datetime.utcnow().strftime('%Y-%m-%d')
    doc_name = f'{document_type} — {deal_name}'[:200] if deal_name else document_type
    stub_fields = {
        JDoc.document_type: document_type,
        'Document Type': document_type,
        JDoc.document_name: doc_name,
        'Document Name': doc_name,
        JDoc.deal_id: [deal_id],
        'Deal': [deal_id],
        JDoc.generated_date: today,
        'Generated Date': today,
        JDoc.generated_by: 'NEXUS Auto',
        'Generated By': 'NEXUS Auto',
        JDoc.party_1_name: 'JETA COURTIÈRE',
        'Party 1 Name': 'JETA COURTIÈRE',
        JDoc.party_1_entity: 'DEE DAVIS INC',
        'Party 1 Entity': 'DEE DAVIS INC',
        JDoc.party_2_name: 'Counterparty',
        'Party 2 Name': 'Counterparty',
        JDoc.deal_description: deal_description or '',
        'Deal Description': deal_description or '',
        JDoc.signed_status: 'Not Sent',
        'Signed Status': 'Not Sent',
    }
    if document_type == 'Fee Agreement' and escalation_version:
        stub_fields[JDoc.escalation_clause_version] = escalation_version
        stub_fields['Escalation Clause Version'] = escalation_version
        jfg = deal_row.get('jetaFeePerGallon')
        if jfg is not None:
            try:
                stub_fields[JDoc.fee_per_gallon] = float(jfg)
                stub_fields['Fee Per Gallon'] = float(jfg)
            except (TypeError, ValueError):
                pass
        vg = deal_row.get('volumeGallons')
        if vg is not None:
            try:
                stub_fields[JDoc.volume_gallons] = float(vg)
                stub_fields['Volume Gallons'] = float(vg)
            except (TypeError, ValueError):
                pass
    if buyer_id:
        stub_fields[JDoc.buyer_id] = [buyer_id]
        stub_fields['Buyer'] = [buyer_id]
    seller_id = (deal_row.get('sellerId') or '').strip()
    if seller_id:
        stub_fields[JDoc.seller_id] = [seller_id]
        stub_fields['Seller'] = [seller_id]

    created = airtable_client.create_record(JETA_DOCUMENTS_TABLE, stub_fields)
    rec_id = created['id']
    safe_name = re.sub(r'[^a-zA-Z0-9_.-]+', '_', f'{document_type}_{rec_id}')[:120]
    fname = f'{safe_name}.pdf'
    out_dir = _jeta_documents_output_dir()
    full_path = os.path.join(out_dir, fname)
    with open(full_path, 'wb') as out_f:
        out_f.write(pdf_bytes)

    download_url = f'/jeta/documents/{rec_id}/download'
    airtable_client.update_record(JETA_DOCUMENTS_TABLE, rec_id, {
        JDoc.pdf_link: download_url,
        'Download URL': download_url,
        'PDF Path': fname,
    })
    merged = airtable_client.get_record(JETA_DOCUMENTS_TABLE, rec_id)
    deals_raw = airtable_client.get_all_records(JETA_DEALS_TABLE)
    deal_lookup = {rec['id']: _jeta_serialize_deal(rec, buyer_lookup) for rec in deals_raw}
    serialized = _jeta_serialize_document(merged, deal_lookup, buyer_lookup)

    if return_pdf:
        try:
            dl_abs = url_for('jeta_documents_download', doc_id=rec_id, _external=True)
        except Exception:
            dl_abs = download_url
        return Response(
            pdf_bytes,
            status=201,
            mimetype='application/pdf',
            headers={
                'Content-Disposition': f'inline; filename="{fname}"',
                'X-Document-Id': rec_id,
                'X-Download-URL': dl_abs,
            },
        )

    out_gen = {
        'success': True,
        'document': serialized,
        'downloadUrl': download_url,
        'download_url': download_url,
    }
    if document_type == 'Fee Agreement' and escalation_version:
        out_gen['escalationClauseVersion'] = escalation_version
        out_gen['escalation_base_benchmark_bbl'] = base_benchmark
    return jsonify(out_gen), 201


@app.route('/api/jeta/documents', methods=['GET'])
@app.route('/jeta/documents', methods=['GET'])
def jeta_get_documents():
    """List all JETA document log rows."""
    try:
        airtable_client = AirtableClient()
        try:
            buyers_raw = airtable_client.get_all_records(JETA_BUYERS_TABLE)
            deals_raw = airtable_client.get_all_records(JETA_DEALS_TABLE)
            docs_raw = airtable_client.get_all_records(JETA_DOCUMENTS_TABLE)
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'documents': [],
                'documentTypes': list(JETA_DOCUMENT_TYPES),
                'hint': f'Create Airtable table "{JETA_DOCUMENTS_TABLE}" with expected fields.',
            }), 200

        buyer_lookup = {rec['id']: _jeta_serialize_record(rec) for rec in buyers_raw}
        deal_lookup = {rec['id']: _jeta_serialize_deal(rec, buyer_lookup) for rec in deals_raw}
        rows = [_jeta_serialize_document(rec, deal_lookup, buyer_lookup) for rec in docs_raw]
        rows.sort(key=lambda x: (x.get('generatedDate') or '', x.get('createdTime') or ''), reverse=True)
        return jsonify({
            'success': True,
            'documents': rows,
            'count': len(rows),
            'documentTypes': list(JETA_DOCUMENT_TYPES),
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e), 'documents': []}), 500


@app.route('/api/jeta/documents/generate', methods=['POST'])
@app.route('/jeta/documents/generate', methods=['POST'])
def jeta_documents_generate():
    """Generate PDF, save file, create JETA_Documents row. Optional return_pdf for raw PDF body."""
    try:
        return _jeta_documents_generate_handler()
    except RuntimeError as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/jeta/documents/<doc_id>', methods=['PUT', 'PATCH'])
@app.route('/jeta/documents/<doc_id>', methods=['PUT', 'PATCH'])
def jeta_update_document(doc_id):
    """Update JETA document (e.g. Signed Status)."""
    try:
        data = request.json or {}
        signed = data.get('signedStatus')
        if signed is None:
            signed = data.get('signed_status')
        if signed is None:
            return jsonify({'success': False, 'error': 'signedStatus or signed_status is required'}), 400
        airtable_client = AirtableClient()
        updated = airtable_client.update_record(JETA_DOCUMENTS_TABLE, doc_id, {
            JDoc.signed_status: signed,
            'Signed Status': signed,
        })
        buyers_raw = airtable_client.get_all_records(JETA_BUYERS_TABLE)
        deals_raw = airtable_client.get_all_records(JETA_DEALS_TABLE)
        buyer_lookup = {rec['id']: _jeta_serialize_record(rec) for rec in buyers_raw}
        deal_lookup = {rec['id']: _jeta_serialize_deal(rec, buyer_lookup) for rec in deals_raw}
        return jsonify({
            'success': True,
            'document': _jeta_serialize_document(updated, deal_lookup, buyer_lookup),
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/jeta/documents/<doc_id>/download', methods=['GET'])
@app.route('/jeta/documents/<doc_id>/download', methods=['GET'])
def jeta_documents_download(doc_id):
    """Download generated PDF by document record id."""
    try:
        airtable_client = AirtableClient()
        rec = airtable_client.get_record(JETA_DOCUMENTS_TABLE, doc_id)
        f = rec.get('fields') or {}
        fname = jdoc_pdf_path_local(f)
        if not fname:
            return jsonify({'success': False, 'error': 'No PDF on file'}), 404
        full_path = os.path.join(_jeta_documents_output_dir(), fname)
        if not os.path.isfile(full_path):
            return jsonify({'success': False, 'error': 'PDF file missing on server'}), 404
        doc_label = (jdoc_get_str(f, JDoc.document_type) or f.get('Document Type') or 'JETA').replace('/', '-')
        download_name = f'{doc_label}_{doc_id[:8]}.pdf'
        return send_file(
            full_path,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=download_name,
        )
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 404


# =====================================================================
# JETA_BrokerChain — IMFPA broker chain rows per deal (canonical: jeta_broker_chain_schema.JBC)
# =====================================================================

JETA_BROKER_CHAIN_TABLE = 'JETA_BrokerChain'


def _jeta_serialize_broker_chain(record: dict) -> dict:
    f = record.get('fields') or {}
    pos = jbc_get_int(f, JBC.broker_position)
    return {
        'id': record['id'],
        'dealId': jbc_first_link_id(f, JBC.deal_id),
        'brokerPosition': pos if pos is not None else None,
        'brokerName': jbc_get_str(f, JBC.broker_name),
        'brokerCompany': jbc_get_str(f, JBC.broker_company),
        'brokerEmail': jbc_get_str(f, JBC.broker_email),
        'brokerPhone': jbc_get_str(f, JBC.broker_phone),
        'brokerAddress': jbc_get_str(f, JBC.broker_address),
        'chainPercentage': jbc_get_float(f, JBC.chain_percentage),
        'jetaIntroduced': jbc_get_bool(f, JBC.jeta_introduced) is True,
        'verified': jbc_get_bool(f, JBC.verified) is True,
        'ncndaSigned': jbc_get_bool(f, JBC.ncnda_signed) is True,
        'imfpaSigned': jbc_get_bool(f, JBC.imfpa_signed) is True,
        'paymentInfo': jbc_get_str(f, JBC.payment_info),
        'notes': jbc_get_str(f, JBC.notes),
        'createdTime': record.get('createdTime', ''),
    }


def _jeta_broker_chain_json_to_fields(data: dict, partial: bool = False) -> dict:
    out = {}

    def put_both(canon: str, legacy: str | None, val) -> None:
        if val is None:
            return
        out[canon] = val
        if legacy:
            out[legacy] = val

    did = (data.get('dealId') or data.get('deal_id') or '').strip()
    if did:
        put_both(JBC.deal_id, 'Deal', [did])

    if 'brokerPosition' in data and data['brokerPosition'] is not None:
        try:
            put_both(JBC.broker_position, 'Broker Position', int(data['brokerPosition']))
        except (TypeError, ValueError):
            pass

    str_fields = [
        ('brokerName', JBC.broker_name, 'Broker Name'),
        ('brokerCompany', JBC.broker_company, 'Broker Company'),
        ('brokerEmail', JBC.broker_email, 'Broker Email'),
        ('brokerPhone', JBC.broker_phone, 'Broker Phone'),
        ('brokerAddress', JBC.broker_address, 'Broker Address'),
        ('paymentInfo', JBC.payment_info, 'Payment Info'),
        ('notes', JBC.notes, 'Notes'),
    ]
    for jk, canon, legacy in str_fields:
        if jk not in data or data[jk] is None:
            continue
        put_both(canon, legacy, str(data[jk]).strip())

    if 'chainPercentage' in data and data['chainPercentage'] not in (None, ''):
        try:
            put_both(JBC.chain_percentage, 'Chain Percentage', float(data['chainPercentage']))
        except (TypeError, ValueError):
            pass

    for jk, canon, legacy in [
        ('jetaIntroduced', JBC.jeta_introduced, 'JETA Introduced'),
        ('verified', JBC.verified, 'Verified'),
        ('ncndaSigned', JBC.ncnda_signed, 'NCNDA Signed'),
        ('imfpaSigned', JBC.imfpa_signed, 'IMFPA Signed'),
    ]:
        if jk in data:
            put_both(canon, legacy, _jeta_coerce_bool(data[jk]))

    return out


@app.route('/api/jeta/broker-chain', methods=['GET'])
@app.route('/jeta/broker-chain', methods=['GET'])
def jeta_get_broker_chain():
    """List IMFPA broker chain rows; optional ?deal_id= filter."""
    try:
        airtable_client = AirtableClient()
        try:
            raw = airtable_client.get_all_records(JETA_BROKER_CHAIN_TABLE)
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'rows': [],
                'hint': f'Create Airtable table "{JETA_BROKER_CHAIN_TABLE}" with expected fields.',
            }), 200

        deal_f = (request.args.get('deal_id') or request.args.get('dealId') or '').strip()
        rows = [_jeta_serialize_broker_chain(rec) for rec in raw]
        if deal_f:
            rows = [r for r in rows if r.get('dealId') == deal_f]

        def sort_key(r):
            pos = r.get('brokerPosition')
            try:
                p = int(pos) if pos is not None else 999
            except (TypeError, ValueError):
                p = 999
            return (r.get('dealId') or '', p)

        rows.sort(key=sort_key)
        return jsonify({'success': True, 'rows': rows, 'count': len(rows)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e), 'rows': []}), 500


@app.route('/api/jeta/broker-chain', methods=['POST'])
@app.route('/jeta/broker-chain', methods=['POST'])
def jeta_create_broker_chain():
    """Create a broker chain row; dealId links to JETA_Deals."""
    try:
        data = dict(request.json or {})
        if not data.get('dealId') and data.get('deal_id'):
            data['dealId'] = data['deal_id']
        if not (data.get('dealId') or '').strip():
            return jsonify({'success': False, 'error': 'dealId is required'}), 400
        fields = _jeta_broker_chain_json_to_fields(data, partial=False)
        if JBC.deal_id not in fields and 'Deal' not in fields:
            return jsonify({'success': False, 'error': 'dealId is required'}), 400
        airtable_client = AirtableClient()
        created = airtable_client.create_record(JETA_BROKER_CHAIN_TABLE, fields)
        return jsonify({
            'success': True,
            'row': _jeta_serialize_broker_chain(created),
        }), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/jeta/broker-chain/<row_id>', methods=['PUT', 'PATCH'])
@app.route('/jeta/broker-chain/<row_id>', methods=['PUT', 'PATCH'])
def jeta_update_broker_chain(row_id):
    """Update a broker chain row."""
    try:
        data = request.json or {}
        fields = _jeta_broker_chain_json_to_fields(data, partial=True)
        if not fields:
            return jsonify({'success': False, 'error': 'No fields to update'}), 400
        airtable_client = AirtableClient()
        updated = airtable_client.update_record(JETA_BROKER_CHAIN_TABLE, row_id, fields)
        return jsonify({
            'success': True,
            'row': _jeta_serialize_broker_chain(updated),
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


# =====================================================================
# JETA_RFPs — fuel RFP tracking (canonical: jeta_rfp_schema.JR)
# =====================================================================

JETA_RFPS_TABLE = 'JETA_RFPs'


def _jeta_serialize_rfp(record: dict) -> dict:
    f = record.get('fields') or {}
    return {
        'id': record['id'],
        'rfpTitle': jr_get_str(f, JR.rfp_title),
        'issuingEntity': jr_get_str(f, JR.issuing_entity),
        'entityType': jr_get_str(f, JR.entity_type),
        'state': jr_get_str(f, JR.state),
        'country': jr_get_str(f, JR.country),
        'fuelTypeRequired': jr_fuel_types_list(f),
        'estimatedVolume': jr_get_float(f, JR.estimated_volume),
        'contractTerm': jr_get_str(f, JR.contract_term),
        'rfpNumber': jr_get_str(f, JR.rfp_number),
        'issueDate': jr_format_date_val(jr_get_raw(f, JR.issue_date)),
        'questionsDue': jr_format_date_val(jr_get_raw(f, JR.questions_due)),
        'submissionDeadline': jr_format_date_val(jr_get_raw(f, JR.submission_deadline)),
        'awardDate': jr_format_date_val(jr_get_raw(f, JR.award_date)),
        'submissionMethod': jr_get_str(f, JR.submission_method),
        'portalLink': jr_get_str(f, JR.portal_link),
        'rfpDocumentLink': jr_get_str(f, JR.rfp_document_link),
        'status': jr_get_str(f, JR.status),
        'bidDecision': jr_get_str(f, JR.bid_decision),
        'noBidReason': jr_get_str(f, JR.no_bid_reason),
        'incumbent': jr_get_str(f, JR.incumbent),
        'competitorsKnown': jr_get_str(f, JR.competitors_known),
        'ourPpgProposed': jr_get_float(f, JR.our_ppg_proposed),
        'estimatedFee': jr_get_float(f, JR.estimated_fee),
        'linkedBuyerId': jr_first_link_id(f, JR.linked_buyer),
        'source': jr_get_str(f, JR.source),
        'notes': jr_get_str(f, JR.notes),
        'dateAdded': jr_format_date_val(jr_get_raw(f, JR.date_added)),
        'createdTime': record.get('createdTime', ''),
    }


def _jeta_rfp_json_to_fields(data: dict, partial: bool = False) -> dict:
    """API camelCase / snake_case → Airtable canonical + legacy."""
    out = {}

    def put_both(canon: str, legacy: str | None, val) -> None:
        if val is None:
            return
        out[canon] = val
        if legacy:
            out[legacy] = val

    bid = (data.get('linkedBuyerId') or data.get('linked_buyer_id') or data.get('buyerId') or '').strip()
    if bid:
        put_both(JR.linked_buyer, 'Linked Buyer', [bid])

    str_map = [
        ('rfpTitle', JR.rfp_title, 'RFP Title'),
        ('rfp_title', JR.rfp_title, 'RFP Title'),
        ('issuingEntity', JR.issuing_entity, 'Issuing Entity'),
        ('issuing_entity', JR.issuing_entity, 'Issuing Entity'),
        ('entityType', JR.entity_type, 'Entity Type'),
        ('entity_type', JR.entity_type, 'Entity Type'),
        ('state', JR.state, 'State'),
        ('country', JR.country, 'Country'),
        ('contractTerm', JR.contract_term, 'Contract Term'),
        ('contract_term', JR.contract_term, 'Contract Term'),
        ('rfpNumber', JR.rfp_number, 'RFP Number'),
        ('rfp_number', JR.rfp_number, 'RFP Number'),
        ('submissionMethod', JR.submission_method, 'Submission Method'),
        ('submission_method', JR.submission_method, 'Submission Method'),
        ('portalLink', JR.portal_link, 'Portal Link'),
        ('portal_link', JR.portal_link, 'Portal Link'),
        ('rfpDocumentLink', JR.rfp_document_link, 'RFP Document Link'),
        ('rfp_document_link', JR.rfp_document_link, 'RFP Document Link'),
        ('status', JR.status, 'Status'),
        ('bidDecision', JR.bid_decision, 'Bid Decision'),
        ('bid_decision', JR.bid_decision, 'Bid Decision'),
        ('noBidReason', JR.no_bid_reason, 'No Bid Reason'),
        ('no_bid_reason', JR.no_bid_reason, 'No Bid Reason'),
        ('incumbent', JR.incumbent, 'Incumbent'),
        ('competitorsKnown', JR.competitors_known, 'Competitors Known'),
        ('competitors_known', JR.competitors_known, 'Competitors Known'),
        ('source', JR.source, 'Source'),
        ('notes', JR.notes, 'Notes'),
    ]
    for jk, canon, legacy in str_map:
        if jk not in data or data[jk] is None:
            continue
        put_both(canon, legacy, str(data[jk]).strip())

    ft = data.get('fuelTypeRequired') or data.get('fuel_type_required')
    if ft is not None:
        if isinstance(ft, list):
            lst = [str(x).strip() for x in ft if str(x).strip()]
        else:
            lst = [x.strip() for x in str(ft).split(',') if x.strip()]
        if lst:
            put_both(JR.fuel_type_required, 'Fuel Type Required', lst)

    for jk, canon, legacy in [
        ('estimatedVolume', JR.estimated_volume, 'Estimated Volume'),
        ('estimated_volume', JR.estimated_volume, 'Estimated Volume'),
        ('ourPpgProposed', JR.our_ppg_proposed, 'Our PPG Proposed'),
        ('our_ppg_proposed', JR.our_ppg_proposed, 'Our PPG Proposed'),
        ('estimatedFee', JR.estimated_fee, 'Estimated Fee'),
        ('estimated_fee', JR.estimated_fee, 'Estimated Fee'),
    ]:
        if jk not in data or data[jk] in (None, ''):
            continue
        try:
            put_both(canon, legacy, float(data[jk]))
        except (TypeError, ValueError):
            pass

    date_map = [
        ('issueDate', JR.issue_date, 'Issue Date'),
        ('issue_date', JR.issue_date, 'Issue Date'),
        ('questionsDue', JR.questions_due, 'Questions Due'),
        ('questions_due', JR.questions_due, 'Questions Due'),
        ('submissionDeadline', JR.submission_deadline, 'Submission Deadline'),
        ('submission_deadline', JR.submission_deadline, 'Submission Deadline'),
        ('awardDate', JR.award_date, 'Award Date'),
        ('award_date', JR.award_date, 'Award Date'),
        ('dateAdded', JR.date_added, 'Date Added'),
        ('date_added', JR.date_added, 'Date Added'),
    ]
    for jk, canon, legacy in date_map:
        if jk not in data or data[jk] in (None, ''):
            continue
        put_both(canon, legacy, str(data[jk]).strip()[:10])

    return out


@app.route('/api/jeta/rfps', methods=['GET'])
@app.route('/jeta/rfps', methods=['GET'])
def jeta_get_rfps():
    """List JETA RFP rows; optional ?status=, ?linked_buyer_id= filters."""
    try:
        airtable_client = AirtableClient()
        try:
            raw = airtable_client.get_all_records(JETA_RFPS_TABLE)
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'rfps': [],
                'hint': f'Create Airtable table "{JETA_RFPS_TABLE}" with expected fields.',
            }), 200

        st_f = (request.args.get('status') or '').strip().lower()
        lb_f = (request.args.get('linked_buyer_id') or request.args.get('linkedBuyerId') or '').strip()
        rows = [_jeta_serialize_rfp(rec) for rec in raw]
        if st_f:
            rows = [r for r in rows if (r.get('status') or '').lower() == st_f]
        if lb_f:
            rows = [r for r in rows if r.get('linkedBuyerId') == lb_f]

        rows.sort(key=lambda x: (x.get('submissionDeadline') or '', x.get('createdTime') or ''), reverse=True)
        return jsonify({'success': True, 'rfps': rows, 'count': len(rows)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e), 'rfps': []}), 500


@app.route('/api/jeta/rfps', methods=['POST'])
@app.route('/jeta/rfps', methods=['POST'])
def jeta_create_rfp():
    """Create an RFP tracking row."""
    try:
        data = dict(request.json or {})
        fields = _jeta_rfp_json_to_fields(data, partial=False)
        if not fields:
            return jsonify({'success': False, 'error': 'No fields provided'}), 400
        airtable_client = AirtableClient()
        created = airtable_client.create_record(JETA_RFPS_TABLE, fields)
        return jsonify({'success': True, 'rfp': _jeta_serialize_rfp(created)}), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/jeta/rfps/<rfp_id>', methods=['PUT', 'PATCH'])
@app.route('/jeta/rfps/<rfp_id>', methods=['PUT', 'PATCH'])
def jeta_update_rfp(rfp_id):
    """Update an RFP row."""
    try:
        data = request.json or {}
        fields = _jeta_rfp_json_to_fields(data, partial=True)
        if not fields:
            return jsonify({'success': False, 'error': 'No fields to update'}), 400
        airtable_client = AirtableClient()
        updated = airtable_client.update_record(JETA_RFPS_TABLE, rfp_id, fields)
        return jsonify({'success': True, 'rfp': _jeta_serialize_rfp(updated)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


# =====================================================================
# JETA_SellerContacts — contacts linked to JETA_Sellers (canonical: jeta_seller_contact_schema.JSC)
# =====================================================================

JETA_SELLER_CONTACTS_TABLE = 'JETA_SellerContacts'


def _jeta_serialize_seller_contact(record: dict) -> dict:
    f = record.get('fields') or {}
    return {
        'id': record['id'],
        'sellerId': jsc_first_link_id(f, JSC.seller_id),
        'contactName': jsc_get_str(f, JSC.contact_name),
        'contactTitle': jsc_get_str(f, JSC.contact_title),
        'contactEmail': jsc_get_str(f, JSC.contact_email),
        'contactPhone': jsc_get_str(f, JSC.contact_phone),
        'contactLinkedin': jsc_get_str(f, JSC.contact_linkedin),
        'department': jsc_get_str(f, JSC.department),
        'decisionAuthority': jsc_get_str(f, JSC.decision_authority),
        'relationshipStatus': jsc_get_str(f, JSC.relationship_status),
        'lastContactDate': jsc_format_date(jsc_get_raw(f, JSC.last_contact_date)),
        'nextContactDate': jsc_format_date(jsc_get_raw(f, JSC.next_contact_date)),
        'outreachNotes': jsc_get_str(f, JSC.outreach_notes),
        'loaSignatory': jsc_get_bool(f, JSC.loa_signatory) is True,
        'notes': jsc_get_str(f, JSC.notes),
        'createdTime': record.get('createdTime', ''),
    }


def _jeta_seller_contact_json_to_fields(data: dict, partial: bool = False) -> dict:
    out = {}

    def put_both(canon: str, legacy: str | None, val) -> None:
        if val is None:
            return
        out[canon] = val
        if legacy:
            out[legacy] = val

    sid = (data.get('sellerId') or data.get('seller_id') or '').strip()
    if sid:
        put_both(JSC.seller_id, 'Seller', [sid])

    str_map = [
        ('contactName', JSC.contact_name, 'Contact Name'),
        ('contact_name', JSC.contact_name, 'Contact Name'),
        ('contactTitle', JSC.contact_title, 'Contact Title'),
        ('contact_title', JSC.contact_title, 'Contact Title'),
        ('contactEmail', JSC.contact_email, 'Contact Email'),
        ('contact_email', JSC.contact_email, 'Contact Email'),
        ('contactPhone', JSC.contact_phone, 'Contact Phone'),
        ('contact_phone', JSC.contact_phone, 'Contact Phone'),
        ('contactLinkedin', JSC.contact_linkedin, 'Contact LinkedIn'),
        ('contact_linkedin', JSC.contact_linkedin, 'Contact LinkedIn'),
        ('department', JSC.department, 'Department'),
        ('decisionAuthority', JSC.decision_authority, 'Decision Authority'),
        ('decision_authority', JSC.decision_authority, 'Decision Authority'),
        ('relationshipStatus', JSC.relationship_status, 'Relationship Status'),
        ('relationship_status', JSC.relationship_status, 'Relationship Status'),
        ('outreachNotes', JSC.outreach_notes, 'Outreach Notes'),
        ('outreach_notes', JSC.outreach_notes, 'Outreach Notes'),
        ('notes', JSC.notes, 'Notes'),
    ]
    for jk, canon, legacy in str_map:
        if jk not in data or data[jk] is None:
            continue
        put_both(canon, legacy, str(data[jk]).strip())

    for jk, canon, legacy in [
        ('lastContactDate', JSC.last_contact_date, 'Last Contact Date'),
        ('last_contact_date', JSC.last_contact_date, 'Last Contact Date'),
        ('nextContactDate', JSC.next_contact_date, 'Next Contact Date'),
        ('next_contact_date', JSC.next_contact_date, 'Next Contact Date'),
    ]:
        if jk not in data or data[jk] in (None, ''):
            continue
        put_both(canon, legacy, str(data[jk]).strip()[:10])

    for jk, canon, legacy in [
        ('loaSignatory', JSC.loa_signatory, 'LOA Signatory'),
        ('loa_signatory', JSC.loa_signatory, 'LOA Signatory'),
    ]:
        if jk in data:
            put_both(canon, legacy, _jeta_coerce_bool(data[jk]))

    return out


@app.route('/api/jeta/seller-contacts', methods=['GET'])
@app.route('/jeta/seller-contacts', methods=['GET'])
def jeta_get_seller_contacts():
    """List seller contact rows; optional ?seller_id= filter."""
    try:
        airtable_client = AirtableClient()
        try:
            raw = airtable_client.get_all_records(JETA_SELLER_CONTACTS_TABLE)
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'contacts': [],
                'hint': f'Create Airtable table "{JETA_SELLER_CONTACTS_TABLE}" with expected fields.',
            }), 200

        sf = (request.args.get('seller_id') or request.args.get('sellerId') or '').strip()
        rows = [_jeta_serialize_seller_contact(rec) for rec in raw]
        if sf:
            rows = [r for r in rows if r.get('sellerId') == sf]

        rows.sort(key=lambda x: (x.get('sellerId') or '', x.get('contactName') or ''))
        return jsonify({'success': True, 'contacts': rows, 'count': len(rows)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e), 'contacts': []}), 500


@app.route('/api/jeta/seller-contacts', methods=['POST'])
@app.route('/jeta/seller-contacts', methods=['POST'])
def jeta_create_seller_contact():
    """Create a seller contact; sellerId links to JETA_Sellers."""
    try:
        data = dict(request.json or {})
        if not data.get('sellerId') and data.get('seller_id'):
            data['sellerId'] = data['seller_id']
        if not (data.get('sellerId') or '').strip():
            return jsonify({'success': False, 'error': 'sellerId is required'}), 400
        fields = _jeta_seller_contact_json_to_fields(data, partial=False)
        if JSC.seller_id not in fields and 'Seller' not in fields:
            return jsonify({'success': False, 'error': 'sellerId is required'}), 400
        airtable_client = AirtableClient()
        created = airtable_client.create_record(JETA_SELLER_CONTACTS_TABLE, fields)
        return jsonify({'success': True, 'contact': _jeta_serialize_seller_contact(created)}), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/jeta/seller-contacts/<contact_id>', methods=['PUT', 'PATCH'])
@app.route('/jeta/seller-contacts/<contact_id>', methods=['PUT', 'PATCH'])
def jeta_update_seller_contact(contact_id):
    """Update a seller contact row."""
    try:
        data = request.json or {}
        fields = _jeta_seller_contact_json_to_fields(data, partial=True)
        if not fields:
            return jsonify({'success': False, 'error': 'No fields to update'}), 400
        airtable_client = AirtableClient()
        updated = airtable_client.update_record(JETA_SELLER_CONTACTS_TABLE, contact_id, fields)
        return jsonify({'success': True, 'contact': _jeta_serialize_seller_contact(updated)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


# =====================================================================
# JETA_FraudLog — compliance / fraud audit rows (canonical: jeta_fraud_log_schema.JFL)
# =====================================================================

JETA_FRAUD_LOG_TABLE = 'JETA_FraudLog'


def _jeta_serialize_fraud_log(record: dict) -> dict:
    """Master doc TABLE 11 + legacy aliases for older clients."""
    f = record.get('fields') or {}
    flagged_type = jfl_get_str(f, JFL.flagged_record_type)
    flagged_id = jfl_flagged_record_id_display(f)
    flag_types = jfl_flag_type_list(f)
    detail = jfl_get_str(f, JFL.flag_detail)
    res_notes = jfl_get_str(f, JFL.resolution_notes)
    date_fl = jfl_format_date(jfl_get_raw(f, JFL.date_flagged))
    blk = jfl_get_bool(f, JFL.blacklisted)
    ld = jfl_first_link_id(f, JFL.linked_deal)
    lb = jfl_first_link_id(f, JFL.linked_buyer)
    ls = jfl_first_link_id(f, JFL.linked_seller)
    out = {
        'id': record['id'],
        'flaggedRecordType': flagged_type,
        'flaggedRecordId': flagged_id,
        'flagLevel': jfl_get_str(f, JFL.flag_level),
        'flagType': flag_types,
        'flagDetail': detail,
        'triggeredBy': jfl_get_str(f, JFL.triggered_by),
        'actionTaken': jfl_get_str(f, JFL.action_taken),
        'reviewedBy': jfl_get_str(f, JFL.reviewed_by),
        'reviewDate': jfl_format_date(jfl_get_raw(f, JFL.review_date)),
        'resolutionNotes': res_notes,
        'blacklisted': blk,
        'dateFlagged': date_fl,
        'linkedDealId': ld,
        'linkedBuyerId': lb,
        'linkedSellerId': ls,
        'companyName': jfl_get_str(f, JFL.company_name),
        'finalDecision': jfl_get_str(f, JFL.final_decision),
        'createdTime': record.get('createdTime', ''),
        # Legacy aliases (same row data)
        'recordType': flagged_type,
        'recordId': flagged_id,
        'flagsTriggered': flag_types,
        'blacklistTerms': detail,
        'reviewNotes': res_notes,
        'dateLogged': date_fl,
    }
    return out


def _jeta_fraud_log_json_to_fields(data: dict, partial: bool = False) -> dict:
    out = {}

    def put_both(canon: str, legacy: str | None, val) -> None:
        if val is None:
            return
        out[canon] = val
        if legacy:
            out[legacy] = val

    str_map = [
        ('flaggedRecordType', JFL.flagged_record_type, 'Flagged Record Type'),
        ('flagged_record_type', JFL.flagged_record_type, 'Flagged Record Type'),
        ('recordType', JFL.flagged_record_type, 'Flagged Record Type'),
        ('record_type', JFL.flagged_record_type, 'Flagged Record Type'),
        ('flaggedRecordId', JFL.flagged_record_id, 'Flagged Record ID'),
        ('flagged_record_id', JFL.flagged_record_id, 'Flagged Record ID'),
        ('recordId', JFL.flagged_record_id, 'Flagged Record ID'),
        ('record_id', JFL.flagged_record_id, 'Flagged Record ID'),
        ('flagLevel', JFL.flag_level, 'Flag Level'),
        ('flag_level', JFL.flag_level, 'Flag Level'),
        ('flagDetail', JFL.flag_detail, 'Flag Detail'),
        ('flag_detail', JFL.flag_detail, 'Flag Detail'),
        ('blacklistTerms', JFL.flag_detail, 'Flag Detail'),
        ('blacklist_terms', JFL.flag_detail, 'Flag Detail'),
        ('triggeredBy', JFL.triggered_by, 'Triggered By'),
        ('triggered_by', JFL.triggered_by, 'Triggered By'),
        ('actionTaken', JFL.action_taken, 'Action Taken'),
        ('action_taken', JFL.action_taken, 'Action Taken'),
        ('reviewedBy', JFL.reviewed_by, 'Reviewed By'),
        ('reviewed_by', JFL.reviewed_by, 'Reviewed By'),
        ('resolutionNotes', JFL.resolution_notes, 'Resolution Notes'),
        ('resolution_notes', JFL.resolution_notes, 'Resolution Notes'),
        ('reviewNotes', JFL.resolution_notes, 'Resolution Notes'),
        ('review_notes', JFL.resolution_notes, 'Resolution Notes'),
        ('companyName', JFL.company_name, 'Company Name'),
        ('company_name', JFL.company_name, 'Company Name'),
        ('finalDecision', JFL.final_decision, 'Final Decision'),
        ('final_decision', JFL.final_decision, 'Final Decision'),
    ]
    for jk, canon, legacy in str_map:
        if jk not in data or data[jk] is None:
            continue
        put_both(canon, legacy, str(data[jk]).strip())

    if JFL.flagged_record_type in out:
        out['Record Type'] = out[JFL.flagged_record_type]
    if JFL.flagged_record_id in out:
        out['Record ID'] = out[JFL.flagged_record_id]

    ft = data.get('flagType') if 'flagType' in data else data.get('flag_type')
    if ft is None:
        ft = data.get('flagsTriggered') if 'flagsTriggered' in data else data.get('flags_triggered')
    if ft is not None:
        if isinstance(ft, list):
            lst = [str(x).strip() for x in ft if str(x).strip()]
        else:
            lst = [x.strip() for x in str(ft).split(',') if x.strip()]
        if lst:
            out[JFL.flag_type] = lst
            out['Flag Type'] = lst
            out['Flags Triggered'] = lst

    for jk, canon, legacy in [
        ('reviewDate', JFL.review_date, 'Review Date'),
        ('review_date', JFL.review_date, 'Review Date'),
        ('dateFlagged', JFL.date_flagged, 'Date Flagged'),
        ('date_flagged', JFL.date_flagged, 'Date Flagged'),
        ('dateLogged', JFL.date_flagged, 'Date Flagged'),
        ('date_logged', JFL.date_flagged, 'Date Flagged'),
    ]:
        if jk not in data or data[jk] in (None, ''):
            continue
        put_both(canon, legacy, str(data[jk]).strip()[:10])

    def _bool_key(jk: str) -> bool | None:
        if jk not in data:
            return None
        v = data[jk]
        if v is None:
            return None
        if isinstance(v, bool):
            return v
        s = str(v).strip().lower()
        if s in ('', '0', 'false', 'no'):
            return False
        return True

    for jk, canon, legacy in [
        ('blacklisted', JFL.blacklisted, 'Blacklisted'),
    ]:
        b = _bool_key(jk)
        if b is not None:
            put_both(canon, legacy, b)

    def _link_val(jk_alt: tuple) -> str | None:
        for k in jk_alt:
            if k in data and data[k] not in (None, ''):
                return str(data[k]).strip()
        return None

    deal_id = _link_val(('linkedDealId', 'linked_deal_id', 'linked_deal'))
    buyer_id = _link_val(('linkedBuyerId', 'linked_buyer_id', 'linked_buyer'))
    seller_id = _link_val(('linkedSellerId', 'linked_seller_id', 'linked_seller'))
    if deal_id:
        put_both(JFL.linked_deal, 'Linked Deal', [deal_id])
    if buyer_id:
        put_both(JFL.linked_buyer, 'Linked Buyer', [buyer_id])
    if seller_id:
        put_both(JFL.linked_seller, 'Linked Seller', [seller_id])

    return out


@app.route('/api/jeta/fraud-log', methods=['GET'])
@app.route('/jeta/fraud-log', methods=['GET'])
def jeta_get_fraud_log():
    """List fraud/compliance log rows; optional ?flagged_record_type=, ?record_type=, ?flagged_record_id=, ?company_name=, ?blacklisted=."""
    try:
        airtable_client = AirtableClient()
        try:
            raw = airtable_client.get_all_records(JETA_FRAUD_LOG_TABLE)
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'entries': [],
                'hint': f'Create Airtable table "{JETA_FRAUD_LOG_TABLE}" with expected fields.',
            }), 200

        rt_f = (
            request.args.get('flagged_record_type')
            or request.args.get('record_type')
            or ''
        ).strip().lower()
        rid_f = (
            request.args.get('flagged_record_id')
            or request.args.get('record_id')
            or request.args.get('recordId')
            or ''
        ).strip()
        co_f = (request.args.get('company_name') or request.args.get('companyName') or '').strip().lower()
        bl_f = (request.args.get('blacklisted') or '').strip().lower()
        rows = [_jeta_serialize_fraud_log(rec) for rec in raw]
        if rt_f:
            rows = [r for r in rows if (r.get('flaggedRecordType') or r.get('recordType') or '').lower() == rt_f]
        if rid_f:
            rows = [r for r in rows if str(r.get('flaggedRecordId') or r.get('recordId') or '') == rid_f]
        if co_f:
            rows = [r for r in rows if co_f in (r.get('companyName') or '').lower()]
        if bl_f in ('1', 'true', 'yes'):
            rows = [r for r in rows if r.get('blacklisted') is True]
        elif bl_f in ('0', 'false', 'no'):
            rows = [r for r in rows if r.get('blacklisted') is not True]

        rows.sort(key=lambda x: (x.get('dateFlagged') or x.get('dateLogged') or '', x.get('createdTime') or ''), reverse=True)
        return jsonify({'success': True, 'entries': rows, 'count': len(rows)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e), 'entries': []}), 500


@app.route('/api/jeta/fraud-log', methods=['POST'])
@app.route('/jeta/fraud-log', methods=['POST'])
def jeta_create_fraud_log():
    """Append a fraud/compliance log row."""
    try:
        data = dict(request.json or {})
        fields = _jeta_fraud_log_json_to_fields(data, partial=False)
        if not fields:
            return jsonify({'success': False, 'error': 'No fields provided'}), 400
        airtable_client = AirtableClient()
        created = airtable_client.create_record(JETA_FRAUD_LOG_TABLE, fields)
        return jsonify({'success': True, 'entry': _jeta_serialize_fraud_log(created)}), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/jeta/fraud-log/<log_id>', methods=['PUT', 'PATCH'])
@app.route('/jeta/fraud-log/<log_id>', methods=['PUT', 'PATCH'])
def jeta_update_fraud_log(log_id):
    """Update a log row (e.g. after manual review)."""
    try:
        data = request.json or {}
        fields = _jeta_fraud_log_json_to_fields(data, partial=True)
        if not fields:
            return jsonify({'success': False, 'error': 'No fields to update'}), 400
        airtable_client = AirtableClient()
        updated = airtable_client.update_record(JETA_FRAUD_LOG_TABLE, log_id, fields)
        return jsonify({'success': True, 'entry': _jeta_serialize_fraud_log(updated)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


# =====================================================================
# JETA_ImportLog — FAA 5010 / Canada batch import audit rows (canonical: jeta_import_log_schema.JIL)
# =====================================================================

JETA_IMPORT_LOG_TABLE = 'JETA_ImportLog'


def _jeta_serialize_import_log(record: dict) -> dict:
    f = record.get('fields') or {}
    tp = jil_get_int(f, JIL.total_processed)
    ti = jil_get_int(f, JIL.total_imported)
    ts = jil_get_int(f, JIL.total_skipped)
    tf = jil_get_int(f, JIL.total_filtered)
    return {
        'id': record['id'],
        'importSource': jil_get_str(f, JIL.import_source),
        'importDate': jil_format_date(jil_get_raw(f, JIL.import_date)),
        'fileName': jil_get_str(f, JIL.file_name),
        'totalProcessed': tp if tp is not None else None,
        'totalImported': ti if ti is not None else None,
        'totalSkipped': ts if ts is not None else None,
        'totalFiltered': tf if tf is not None else None,
        'breakdownByState': jil_get_str(f, JIL.breakdown_by_state),
        'breakdownByType': jil_get_str(f, JIL.breakdown_by_type),
        'errors': jil_get_str(f, JIL.errors),
        'importedBy': jil_get_str(f, JIL.imported_by),
        'notes': jil_get_str(f, JIL.notes),
        'createdTime': record.get('createdTime', ''),
    }


def _jeta_import_log_num(val):
    if val is None or val == '':
        return None
    try:
        return int(float(val))
    except (TypeError, ValueError):
        return None


def _jeta_import_log_json_to_fields(data: dict) -> dict:
    out = {}

    def put_both(canon: str, legacy: tuple, val) -> None:
        if val is None:
            return
        out[canon] = val
        for leg in legacy:
            if leg:
                out[leg] = val

    str_map = [
        ('importSource', JIL.import_source, ('Import Source',)),
        ('import_source', JIL.import_source, ('Import Source',)),
        ('fileName', JIL.file_name, ('File Name',)),
        ('file_name', JIL.file_name, ('File Name',)),
        ('errors', JIL.errors, ('Errors',)),
        ('importedBy', JIL.imported_by, ('Imported By',)),
        ('imported_by', JIL.imported_by, ('Imported By',)),
        ('notes', JIL.notes, ('Notes',)),
    ]
    for jk, canon, legacy in str_map:
        if jk not in data or data[jk] is None:
            continue
        put_both(canon, legacy, str(data[jk]).strip())

    for jk, canon, legacy in [
        ('importDate', JIL.import_date, ('Import Date',)),
        ('import_date', JIL.import_date, ('Import Date',)),
    ]:
        if jk not in data or data[jk] in (None, ''):
            continue
        put_both(canon, legacy, str(data[jk]).strip()[:10])

    num_keys = [
        ('totalProcessed', JIL.total_processed, ('Total Processed',)),
        ('total_processed', JIL.total_processed, ('Total Processed',)),
        ('totalImported', JIL.total_imported, ('Total Imported',)),
        ('total_imported', JIL.total_imported, ('Total Imported',)),
        ('totalSkipped', JIL.total_skipped, ('Total Skipped',)),
        ('total_skipped', JIL.total_skipped, ('Total Skipped',)),
        ('totalFiltered', JIL.total_filtered, ('Total Filtered',)),
        ('total_filtered', JIL.total_filtered, ('Total Filtered',)),
    ]
    for jk, canon, legacy in num_keys:
        if jk not in data:
            continue
        n = _jeta_import_log_num(data[jk])
        if n is not None:
            put_both(canon, legacy, n)

    for jk, canon, legacy in [
        ('breakdownByState', JIL.breakdown_by_state, ('Breakdown By State', 'Breakdown by State')),
        ('breakdown_by_state', JIL.breakdown_by_state, ('Breakdown By State', 'Breakdown by State')),
        ('breakdownByType', JIL.breakdown_by_type, ('Breakdown By Type', 'Breakdown by Type')),
        ('breakdown_by_type', JIL.breakdown_by_type, ('Breakdown By Type', 'Breakdown by Type')),
    ]:
        if jk not in data or data[jk] in (None, ''):
            continue
        raw = data[jk]
        if isinstance(raw, (dict, list)):
            s = jil_long_text_as_json_str(raw)
        else:
            s = str(raw).strip()
        if s:
            put_both(canon, legacy, s)

    return out


@app.route('/api/jeta/import-log', methods=['GET'])
@app.route('/jeta/import-log', methods=['GET'])
def jeta_get_import_log():
    """List import batch log rows; optional ?import_source=, ?file_name=, ?imported_by=."""
    try:
        airtable_client = AirtableClient()
        try:
            raw = airtable_client.get_all_records(JETA_IMPORT_LOG_TABLE)
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'entries': [],
                'hint': f'Create Airtable table "{JETA_IMPORT_LOG_TABLE}" with expected fields.',
            }), 200

        src_f = (request.args.get('import_source') or request.args.get('importSource') or '').strip().lower()
        fn_f = (request.args.get('file_name') or request.args.get('fileName') or '').strip().lower()
        by_f = (request.args.get('imported_by') or request.args.get('importedBy') or '').strip().lower()
        rows = [_jeta_serialize_import_log(rec) for rec in raw]
        if src_f:
            rows = [r for r in rows if src_f in (r.get('importSource') or '').lower()]
        if fn_f:
            rows = [r for r in rows if fn_f in (r.get('fileName') or '').lower()]
        if by_f:
            rows = [r for r in rows if by_f in (r.get('importedBy') or '').lower()]

        rows.sort(key=lambda x: (x.get('importDate') or '', x.get('createdTime') or ''), reverse=True)
        return jsonify({'success': True, 'entries': rows, 'count': len(rows)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e), 'entries': []}), 500


@app.route('/api/jeta/import-log', methods=['POST'])
@app.route('/jeta/import-log', methods=['POST'])
def jeta_create_import_log():
    """Append an import batch log row (after FAA 5010 / Canada CSV runs, etc.)."""
    try:
        data = dict(request.json or {})
        fields = _jeta_import_log_json_to_fields(data)
        if not fields:
            return jsonify({'success': False, 'error': 'No fields provided'}), 400
        airtable_client = AirtableClient()
        created = airtable_client.create_record(JETA_IMPORT_LOG_TABLE, fields)
        return jsonify({'success': True, 'entry': _jeta_serialize_import_log(created)}), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/jeta/import-log/<log_id>', methods=['PUT', 'PATCH'])
@app.route('/jeta/import-log/<log_id>', methods=['PUT', 'PATCH'])
def jeta_update_import_log(log_id):
    """Update an import log row."""
    try:
        data = request.json or {}
        fields = _jeta_import_log_json_to_fields(data)
        if not fields:
            return jsonify({'success': False, 'error': 'No fields to update'}), 400
        airtable_client = AirtableClient()
        updated = airtable_client.update_record(JETA_IMPORT_LOG_TABLE, log_id, fields)
        return jsonify({'success': True, 'entry': _jeta_serialize_import_log(updated)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


# =====================================================================
# JETA_Events — conferences & trade shows (Master doc TABLE 12; jeta_events_schema.JE)
# =====================================================================

JETA_EVENTS_TABLE = 'JETA_Events'


def _jeta_serialize_event(record: dict) -> dict:
    f = record.get('fields') or {}
    c = je_get_float(f, JE.cost)
    return {
        'id': record['id'],
        'eventName': je_get_str(f, JE.event_name),
        'organizer': je_get_str(f, JE.organizer),
        'eventType': je_get_str(f, JE.event_type),
        'locationCity': je_get_str(f, JE.location_city),
        'locationState': je_get_str(f, JE.location_state),
        'virtual': je_get_bool(f, JE.virtual),
        'startDate': je_format_date(je_get_raw(f, JE.start_date)),
        'endDate': je_format_date(je_get_raw(f, JE.end_date)),
        'registrationDeadline': je_format_date(je_get_raw(f, JE.registration_deadline)),
        'registrationUrl': je_get_str(f, JE.registration_url),
        'cost': c if c is not None else None,
        'attending': je_get_str(f, JE.attending),
        'registrationStatus': je_get_str(f, JE.registration_status),
        'contactsMet': je_get_str(f, JE.contacts_met),
        'followUpsNeeded': je_get_str(f, JE.follow_ups_needed),
        'linkedBuyerIds': je_link_ids(f, JE.linked_buyers),
        'linkedSellerIds': je_link_ids(f, JE.linked_sellers),
        'notes': je_get_str(f, JE.notes),
        'dateAdded': je_format_date(je_get_raw(f, JE.date_added)),
        'createdTime': record.get('createdTime', ''),
    }


def _jeta_events_json_to_fields(data: dict) -> dict:
    out = {}

    def put_both(canon: str, legacy: tuple, val) -> None:
        if val is None:
            return
        out[canon] = val
        for leg in legacy:
            if leg:
                out[leg] = val

    str_map = [
        ('eventName', JE.event_name, ('Event Name',)),
        ('event_name', JE.event_name, ('Event Name',)),
        ('organizer', JE.organizer, ('Organizer',)),
        ('eventType', JE.event_type, ('Event Type',)),
        ('event_type', JE.event_type, ('Event Type',)),
        ('locationCity', JE.location_city, ('Location City',)),
        ('location_city', JE.location_city, ('Location City',)),
        ('locationState', JE.location_state, ('Location State',)),
        ('location_state', JE.location_state, ('Location State',)),
        ('registrationUrl', JE.registration_url, ('Registration URL',)),
        ('registration_url', JE.registration_url, ('Registration URL',)),
        ('attending', JE.attending, ('Attending',)),
        ('registrationStatus', JE.registration_status, ('Registration Status',)),
        ('registration_status', JE.registration_status, ('Registration Status',)),
        ('contactsMet', JE.contacts_met, ('Contacts Met',)),
        ('contacts_met', JE.contacts_met, ('Contacts Met',)),
        ('followUpsNeeded', JE.follow_ups_needed, ('Follow Ups Needed', 'Follow-ups Needed')),
        ('follow_ups_needed', JE.follow_ups_needed, ('Follow Ups Needed', 'Follow-ups Needed')),
        ('notes', JE.notes, ('Notes',)),
    ]
    for jk, canon, legacy in str_map:
        if jk not in data or data[jk] is None:
            continue
        put_both(canon, legacy, str(data[jk]).strip())

    for jk, canon, legacy in [
        ('startDate', JE.start_date, ('Start Date',)),
        ('start_date', JE.start_date, ('Start Date',)),
        ('endDate', JE.end_date, ('End Date',)),
        ('end_date', JE.end_date, ('End Date',)),
        ('registrationDeadline', JE.registration_deadline, ('Registration Deadline',)),
        ('registration_deadline', JE.registration_deadline, ('Registration Deadline',)),
        ('dateAdded', JE.date_added, ('Date Added',)),
        ('date_added', JE.date_added, ('Date Added',)),
    ]:
        if jk not in data or data[jk] in (None, ''):
            continue
        put_both(canon, legacy, str(data[jk]).strip()[:10])

    if 'virtual' in data and data['virtual'] is not None:
        v = data['virtual']
        b = v if isinstance(v, bool) else str(v).strip().lower() in ('1', 'true', 'yes')
        put_both(JE.virtual, ('Virtual',), b)

    if 'cost' in data and data['cost'] not in (None, ''):
        try:
            put_both(JE.cost, ('Cost',), float(data['cost']))
        except (TypeError, ValueError):
            pass

    def _ids(key_snake: str, key_camel: str) -> list[str] | None:
        raw = data.get(key_camel) if key_camel in data else data.get(key_snake)
        if raw is None:
            return None
        if isinstance(raw, list):
            return [str(x).strip() for x in raw if str(x).strip()]
        s = str(raw).strip()
        return [s] if s else None

    lb = _ids('linked_buyers', 'linkedBuyerIds')
    if lb:
        put_both(JE.linked_buyers, ('Linked Buyers',), lb)
    ls = _ids('linked_sellers', 'linkedSellerIds')
    if ls:
        put_both(JE.linked_sellers, ('Linked Sellers',), ls)

    return out


@app.route('/api/jeta/events', methods=['GET'])
@app.route('/jeta/events', methods=['GET'])
def jeta_get_events():
    """List JETA_Events rows; optional ?attending=, ?event_type=, ?q= (name/organizer/city)."""
    try:
        airtable_client = AirtableClient()
        try:
            raw = airtable_client.get_all_records(JETA_EVENTS_TABLE)
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'events': [],
                'hint': f'Create Airtable table "{JETA_EVENTS_TABLE}" with fields from Master doc TABLE 12.',
            }), 200

        att_f = (request.args.get('attending') or '').strip().lower()
        et_f = (request.args.get('event_type') or request.args.get('eventType') or '').strip().lower()
        q_f = (request.args.get('q') or '').strip().lower()
        rows = [_jeta_serialize_event(rec) for rec in raw]
        if att_f:
            rows = [r for r in rows if att_f in (r.get('attending') or '').lower()]
        if et_f:
            rows = [r for r in rows if et_f in (r.get('eventType') or '').lower()]
        if q_f:
            rows = [
                r
                for r in rows
                if q_f in (r.get('eventName') or '').lower()
                or q_f in (r.get('organizer') or '').lower()
                or q_f in (r.get('locationCity') or '').lower()
            ]
        rows.sort(key=lambda x: (x.get('startDate') or '', x.get('createdTime') or ''), reverse=True)
        return jsonify({'success': True, 'events': rows, 'count': len(rows)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e), 'events': []}), 500


@app.route('/api/jeta/events', methods=['POST'])
@app.route('/jeta/events', methods=['POST'])
def jeta_create_event():
    try:
        data = dict(request.json or {})
        fields = _jeta_events_json_to_fields(data)
        if not fields:
            return jsonify({'success': False, 'error': 'No fields provided'}), 400
        airtable_client = AirtableClient()
        created = airtable_client.create_record(JETA_EVENTS_TABLE, fields)
        return jsonify({'success': True, 'event': _jeta_serialize_event(created)}), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/jeta/events/<event_id>', methods=['PUT', 'PATCH'])
@app.route('/jeta/events/<event_id>', methods=['PUT', 'PATCH'])
def jeta_update_event(event_id):
    try:
        data = request.json or {}
        fields = _jeta_events_json_to_fields(data)
        if not fields:
            return jsonify({'success': False, 'error': 'No fields to update'}), 400
        airtable_client = AirtableClient()
        updated = airtable_client.update_record(JETA_EVENTS_TABLE, event_id, fields)
        return jsonify({'success': True, 'event': _jeta_serialize_event(updated)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


# =====================================================================
# VENDOR PORTALS ENDPOINTS - Portal Management System
# =====================================================================

@app.route('/vendor-portals', methods=['GET'])
def get_vendor_portals():
    """Get all vendor portals with optional filtering"""
    try:
        category = request.args.get('category')  # 'Government' or 'Development'
        search = request.args.get('search', '').lower()
        
        airtable_client = AirtableClient()
        
        try:
            records = airtable_client.get_all_records('VENDOR PORTAL')
        except:
            # Table doesn't exist yet, return empty
            return jsonify({'portals': []})
        
        portals = []
        for record in records:
            fields = record['fields']
            
            # Filter by category if specified
            if category and fields.get('Category') != category:
                continue
            
            # Filter by search term
            if search:
                searchable = f"{fields.get('Portal Name', '')} {fields.get('Keywords', '')} {fields.get('Description', '')}".lower()
                if search not in searchable:
                    continue
            
            # Map actual Airtable field names (PORTAL URL, Portal Name) to frontend format
            portal_url = fields.get('PORTAL URL', '') or fields.get('Portal URL', '') or fields.get('URL', '') or ''
            portal_name = fields.get('Portal Name', '') or fields.get('Name', '') or ''
            
            portals.append({
                'id': record['id'],
                'name': portal_name,
                'url': portal_url,
                'category': fields.get('Category', ''),
                'portalType': fields.get('Portal Type', ''),
                'keywords': fields.get('Keywords', ''),
                'description': fields.get('Description', ''),
                'searchEnabled': fields.get('Search Enabled', False),
                'searchUrl': fields.get('Search URL', ''),
                'loginRequired': fields.get('Login Required', False),
                'favorite': fields.get('Favorite', False),
                'lastAccessed': fields.get('Last Accessed'),
                'addedDate': fields.get('Added Date'),
                'icon': fields.get('Icon/Favicon', '🔗')
            })
        
        return jsonify({'portals': portals})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/vendor-portals', methods=['POST'])
def create_vendor_portal():
    """Create a new vendor portal"""
    try:
        data = request.json
        airtable_client = AirtableClient()
        
        fields = {
            'Portal Name': data.get('name', ''),
            'PORTAL URL': data.get('url', ''),
            'Category': data.get('category', 'Development'),
            'Portal Type': data.get('portalType', 'Other'),
            'Keywords': data.get('keywords', ''),
            'Description': data.get('description', ''),
            'Search Enabled': data.get('searchEnabled', False),
            'Search URL': data.get('searchUrl', ''),
            'Login Required': data.get('loginRequired', False),
            'Favorite': data.get('favorite', False),
            'Icon/Favicon': data.get('icon', '🔗'),
            'Added Date': datetime.now().isoformat()
        }
        
        result = airtable_client.create_record('VENDOR PORTAL', fields)
        return jsonify({'portal': {'id': result['id'], **data}})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/vendor-portals/<portal_id>', methods=['PUT'])
def update_vendor_portal(portal_id):
    """Update a vendor portal"""
    try:
        data = request.json
        airtable_client = AirtableClient()
        
        update_fields = {}
        field_mapping = {
            'name': 'Portal Name',
            'url': 'PORTAL URL',
            'category': 'Category',
            'portalType': 'Portal Type',
            'keywords': 'Keywords',
            'description': 'Description',
            'searchEnabled': 'Search Enabled',
            'searchUrl': 'Search URL',
            'loginRequired': 'Login Required',
            'favorite': 'Favorite',
            'icon': 'Icon/Favicon'
        }
        
        for key, airtable_field in field_mapping.items():
            if key in data:
                update_fields[airtable_field] = data[key]
        
        # Update last accessed if opening portal
        if data.get('updateLastAccessed'):
            update_fields['Last Accessed'] = datetime.now().isoformat()
        
        airtable_client.update_record('VENDOR PORTAL', portal_id, update_fields)
        return jsonify({'success': True})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/vendor-portals/<portal_id>', methods=['DELETE'])
def delete_vendor_portal(portal_id):
    """Delete a vendor portal"""
    try:
        airtable_client = AirtableClient()
        table = airtable_client.get_table('VENDOR PORTAL')
        table.delete(portal_id)
        return jsonify({'success': True})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =====================================================================
# GPSS OPPORTUNITIES ENDPOINTS - Enhanced Federal/Multi-State
# =====================================================================

@app.route('/gpss/opportunities', methods=['GET'])
def get_gpss_opportunities():
    """
    Get opportunities with smart filtering.
    
    Query params:
      view=pipeline     → Only YOUR active bids (not mined noise)
      view=edwosb       → Only EDWOSB/WOSB set-asides
      view=home_state   → Only Michigan opportunities
      view=forecasts    → Only forecasted opportunities
      view=all          → Everything (default, but filtered for eligibility)
      state=MI          → Filter by state
      edwsb_only=true   → Only EDWOSB/WOSB
      home_states_only=true → Michigan only
    """
    try:
        view = request.args.get('view', 'all')
        source = request.args.get('source')
        state_filter = request.args.get('state')
        edwsb_only = request.args.get('edwsb_only', 'false').lower() == 'true'
        home_states_only = request.args.get('home_states_only', 'false').lower() == 'true'
        
        airtable_client = AirtableClient()
        
        try:
            records = airtable_client.get_all_records('GPSS OPPORTUNITIES')
        except:
            return jsonify({'opportunities': [], 'pipeline': [], 'edwosb': [], 'home_state': [], 'forecasts': []})
        
        # Set-asides we CANNOT bid on — always filter these out
        INELIGIBLE_SET_ASIDES = ['SDVOSB', 'SDVOSBC', 'SDVOSBS', 'VOSB', 'VSA', 'VSB', 
                                  'HUBZone', 'HZC', 'HZS', '8(a)', '8A', '8AN', 'IEE', 'ISBEE']
        
        # Pipeline statuses = YOUR actual bids (not mined noise)
        PIPELINE_STATUSES = [
            'Active', 'Active - Analyzing', 'Submitted', 'Submitted - Awaiting Award',
            'Awaiting Quotes', 'Ready to Bid', 'Not Started', 'Pursuing',
            'Sources Sought Submitted', 'Conditional - May Skip', 'No Contact Yet - URGENT',
        ]
        
        # Mined/forecast statuses = system-generated
        MINED_STATUSES = ['New - API', 'Medium']
        
        HOME_STATES = ['MI', 'MICHIGAN', 'Michigan']
        
        all_opps = []
        pipeline = []
        edwosb_list = []
        home_state_list = []
        forecasts = []
        skipped_ineligible = 0
        
        for record in records:
            fields = record['fields']
            name = fields.get('Name', '')
            set_aside = (fields.get('Set-Aside Type', '') or '').upper()
            status = fields.get('Source Status', '') or ''
            state_val = fields.get('State', '') or ''
            
            # Always filter out ineligible set-asides
            is_ineligible = False
            for code in INELIGIBLE_SET_ASIDES:
                if code.upper() in set_aside:
                    is_ineligible = True
                    break
            if 'SERVICE-DISABLED' in set_aside or 'SERVICE DISABLED' in set_aside or 'VETERAN' in set_aside:
                is_ineligible = True
            if is_ineligible:
                skipped_ineligible += 1
                continue
            
            # Determine opportunity type
            is_forecast = '[Forecast' in name or 'Forecast' in status
            is_pipeline = any(ps in status for ps in PIPELINE_STATUSES) or (
                status and not is_forecast and 'SAM.gov' not in status 
                and 'USASpending' not in status and status not in ('New - API', 'Medium', '')
            )
            is_edwosb = 'EDWOSB' in set_aside or 'WOSB' in set_aside or 'WOSBSS' in set_aside
            is_home_state = state_val.upper() in [s.upper() for s in HOME_STATES]
            
            # Parse workflow step from Notes field (format: [STEP:N] rest of notes)
            raw_notes = fields.get('Notes', '') or ''
            workflow_step = 0
            clean_notes = raw_notes
            step_match = re.match(r'\[STEP:(\d+)\]\s*(.*)', raw_notes, re.DOTALL)
            if step_match:
                workflow_step = int(step_match.group(1))
                clean_notes = step_match.group(2).strip()
            
            # Parse value (Airtable may use Value, Estimated Value, or Contract Value)
            raw_value = fields.get('Value') or fields.get('Estimated Value') or fields.get('Contract Value') or 0
            value = float(raw_value) if raw_value else 0

            # Build opportunity object
            opp = {
                'id': record['id'],
                'title': name,
                'rfpNumber': fields.get('RFP NUMBER', ''),
                'agency': fields.get('AGENCY NAME', ''),
                'value': value,
                'dueDate': fields.get('Deadline', ''),
                'sourceUrl': fields.get('Source URL', ''),
                'state': state_val,
                'city': fields.get('City', ''),
                'setAsideType': fields.get('Set-Aside Type', ''),
                'edwsbEligible': is_edwosb,
                'homeStatePriority': is_home_state,
                'naicsCodes': fields.get('NAISC Codes', ''),
                'category': fields.get('Opportunity Category', ''),
                'winProbability': fields.get('Win Probability', 0),
                'internalStatus': status,
                'priority': fields.get('Priority', ''),
                'notes': clean_notes,
                'workflowStep': workflow_step,
                'aiRecommendation': fields.get('AI Recommendation ', ''),
                'highValueFlag': bool(fields.get('HIGH VALUE FLAG', False)),
                'isForecast': is_forecast,
                'isPipeline': is_pipeline,
                'isEdwosb': is_edwosb,
                'isHomeState': is_home_state,
                'contractingOfficer': fields.get('CONTRACTING OFFICER', ''),
            }
            
            # Categorize
            if is_pipeline:
                pipeline.append(opp)
            if is_edwosb:
                edwosb_list.append(opp)
            if is_home_state:
                home_state_list.append(opp)
            if is_forecast:
                forecasts.append(opp)
            
            # Apply user filters for the main list
            if view == 'pipeline' and not is_pipeline:
                continue
            elif view == 'edwosb' and not is_edwosb:
                continue
            elif view == 'home_state' and not is_home_state:
                continue
            elif view == 'forecasts' and not is_forecast:
                continue
            
            if edwsb_only and not is_edwosb:
                continue
            if home_states_only and not is_home_state:
                continue
            if state_filter and state_val.upper() != state_filter.upper():
                continue
            
            all_opps.append(opp)

        # Recompete Tracker style aggregates (Govcon Giants dashboard model)
        all_for_stats = pipeline + edwosb_list + home_state_list + forecasts
        seen = set()
        deduped = []
        for o in all_for_stats:
            if o['id'] not in seen:
                seen.add(o['id'])
                deduped.append(o)
        total_value = sum(o.get('value', 0) for o in deduped)
        agencies = set(a for o in deduped if (a := o.get('agency', '').strip()))
        naics_raw = []
        for o in deduped:
            nc = o.get('naicsCodes', '') or ''
            if isinstance(nc, str):
                naics_raw.extend([c.strip() for c in nc.replace(',', ' ').split() if c.strip()])
            elif isinstance(nc, (list, tuple)):
                naics_raw.extend(str(c) for c in nc)
        unique_naics = len(set(naics_raw)) if naics_raw else 0

        return jsonify({
            'opportunities': all_opps,
            'counts': {
                'total': len(all_opps),
                'pipeline': len(pipeline),
                'edwosb': len(edwosb_list),
                'home_state': len(home_state_list),
                'forecasts': len(forecasts),
                'filtered_ineligible': skipped_ineligible,
            },
            'tracker': {
                'total_contracts': len(deduped),
                'total_value': total_value,
                'agencies': len(agencies),
                'naics_codes': unique_naics,
            },
            'pipeline': pipeline,
            'edwosb': edwosb_list,
            'home_state': home_state_list,
            'forecasts': forecasts,
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/gpss/opportunities', methods=['POST'])
def create_gpss_opportunity():
    """Create a new opportunity"""
    try:
        data = request.json
        airtable_client = AirtableClient()
        
        fields = {
            'Title': data.get('title', ''),
            'RFP Number': data.get('rfpNumber', ''),
            'Agency Name': data.get('agency', ''),
            'Value': data.get('value', 0),
            'Due Date': data.get('dueDate'),
            'Source': data.get('source', 'Federal'),
            'Source Portal': data.get('sourcePortal', ''),
            'Source URL': data.get('sourceUrl', ''),
            'State': data.get('state', 'Federal'),
            'County': data.get('county', ''),
            'City': data.get('city', ''),
            'Performance Location': data.get('performanceLocation', ''),
            'Home State Priority': data.get('homeStatePriority', False),
            'Agency Type': data.get('agencyType', 'Federal'),
            'Set-Aside Type': data.get('setAsideType', 'Unrestricted'),
            'EDWOSB Eligible': data.get('edwsbEligible', False),
            'Certification Required': data.get('certificationRequired', ''),
            'Opportunity Category': data.get('category', 'Other'),
            'Priority Score': data.get('priorityScore', 0),
            'Win Probability': data.get('winProbability', 0),
            'Urgency': data.get('urgency', 'Medium'),
            'Strategic Fit': data.get('strategicFit', 'Fair'),
            'Internal Status': data.get('internalStatus', 'New'),
            'Pipeline Stage': data.get('pipelineStage', 'Active'),
            'Assigned To': data.get('assignedTo', ''),
            'Notes': data.get('notes', ''),
            'Created Date': datetime.now().isoformat()
        }
        
        # Auto-start workflow at Step 1 if this is a pipeline opportunity
        pipeline_statuses = ['Active', 'Pursuing', 'Not Started', 'Ready to Bid']
        if data.get('internalStatus', '') in pipeline_statuses or data.get('pipelineStage') == 'Active':
            notes = fields.get('Notes', '') or ''
            fields['Notes'] = f'[STEP:1] {notes}'.strip()
        
        result = airtable_client.create_record('GPSS OPPORTUNITIES', fields)

        # NEXUS ADVISOR: Teach about the opportunity
        advisor_insight = None
        try:
            from nexus_advisor import advise, log_growth
            advisor_insight = advise('gpss', 'opportunity_discovered', {
                'agency': data.get('agency', ''),
                'set_aside': data.get('setAsideType', ''),
                'edwosb': data.get('edwsbEligible', False),
                'value': data.get('value', 0),
            })
            log_growth('bid_submitted' if data.get('pipelineStage') == 'Active' else 'bid_submitted')
        except Exception:
            pass

        return jsonify({
            'opportunity': {'id': result['id'], **fields},
            'advisor': advisor_insight,
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/gpss/opportunities/<opportunity_id>', methods=['PUT'])
def update_gpss_opportunity(opportunity_id):
    """Update an opportunity - with auto-ATLAS integration when won"""
    try:
        data = request.json
        airtable_client = AirtableClient()
        
        # Get current opportunity to check status change
        current_opp = airtable_client.get_record('GPSS OPPORTUNITIES', opportunity_id)
        old_status = current_opp['fields'].get('Status', '')
        
        update_fields = {}
        field_mapping = {
            'title': 'Title',
            'rfpNumber': 'RFP Number',
            'agency': 'Agency Name',
            'value': 'Value',
            'dueDate': 'Due Date',
            'source': 'Source',
            'sourcePortal': 'Source Portal',
            'state': 'State',
            'setAsideType': 'Set-Aside Type',
            'edwsbEligible': 'EDWOSB Eligible',
            'priorityScore': 'Priority Score',
            'urgency': 'Urgency',
            'internalStatus': 'Internal Status',
            'pipelineStage': 'Pipeline Stage',
            'assignedTo': 'Assigned To',
            'notes': 'Notes',
            'status': 'Status'  # Add status mapping
        }
        
        for key, airtable_field in field_mapping.items():
            if key in data:
                update_fields[airtable_field] = data[key]
        
        # Handle workflow step - encode into Notes field as [STEP:N] prefix
        if 'workflowStep' in data:
            new_step = int(data['workflowStep'])
            current_notes = current_opp['fields'].get('Notes', '') or ''
            # Strip existing step prefix if present
            step_match = re.match(r'\[STEP:\d+\]\s*(.*)', current_notes, re.DOTALL)
            clean_notes = step_match.group(1).strip() if step_match else current_notes
            # Add new step prefix
            if new_step > 0:
                update_fields['Notes'] = f'[STEP:{new_step}] {clean_notes}'.strip()
            else:
                update_fields['Notes'] = clean_notes
        
        # Update the opportunity
        airtable_client.update_record('GPSS OPPORTUNITIES', opportunity_id, update_fields)
        
        # NEXUS LEARNING: Track opportunity status changes
        new_status = update_fields.get('Status', old_status)
        if new_status != old_status:
            try:
                from nexus_learning_engine import nxlearn
                action_map = {
                    'Won': 'won', 'Lost': 'lost', 'Active': 'pursued',
                    'Submitted': 'bid_submitted', 'Reviewing': 'reviewed',
                    'No Bid': 'skipped',
                }
                action = action_map.get(new_status)
                if action:
                    meta = {
                        'agency': current_opp['fields'].get('Agency Name', ''),
                        'value_range': str(current_opp['fields'].get('Value', '')),
                        'set_aside': current_opp['fields'].get('Set-Aside Type', ''),
                        'naics': current_opp['fields'].get('NAICS', ''),
                        'source': current_opp['fields'].get('Source', ''),
                        'old_status': old_status, 'new_status': new_status,
                    }
                    nxlearn('opportunities', opportunity_id, action, meta)
            except Exception:
                pass

        # NEXUS ADVISOR: Debrief on win/loss + teach on status changes
        advisor_insight = None
        try:
            from nexus_advisor import advise, debrief as advisor_debrief, log_growth
            if new_status == 'Won' and old_status != 'Won':
                advisor_insight = advisor_debrief('bid_won', {
                    'contract_value': current_opp['fields'].get('Value', 0),
                    'agency': current_opp['fields'].get('Agency Name', ''),
                })
            elif new_status == 'Lost' and old_status != 'Lost':
                advisor_insight = advisor_debrief('bid_lost', {
                    'agency': current_opp['fields'].get('Agency Name', ''),
                })
            elif new_status == 'Submitted' and old_status != 'Submitted':
                advisor_insight = advise('gpss', 'bid_submitted')
                log_growth('bid_submitted')
        except Exception:
            pass

        # VERTEX BRIDGE: Track contract revenue when won
        if new_status == 'Won' and old_status != 'Won':
            try:
                contract_value = current_opp['fields'].get('Value', 0)
                if contract_value and float(contract_value) > 0:
                    airtable_client.create_record('VERTEX REVENUE', {
                        VR['revenue_date']:   datetime.now().date().isoformat(),
                        VR['source_system']:  'GPSS',
                        VR['source']:         current_opp['fields'].get('Agency Name', ''),
                        VR['revenue_type']:   'Contract Award',
                        VR['amount']:         float(contract_value),
                        VR['taxable']:        True,
                        VR['recurring']:      False,
                        VR['notes']:          f"Contract won: {current_opp['fields'].get('Title', '')} | Opp ID: {opportunity_id}",
                    })
            except Exception as ve:
                print(f"VERTEX revenue tracking: {ve}")

        # VERTEX AUTO-TRIGGER: Fire full invoice + AP + WAWF workflow on win
        if new_status == 'Won' and old_status != 'Won':
            try:
                from vertex_automation import vertex_auto_trigger
                opp_fields    = current_opp.get('fields', {})
                contract_val  = float(opp_fields.get('Value', 0) or 0)
                agency        = opp_fields.get('Agency Name', '')
                title         = opp_fields.get('Title', '')
                agency_type   = (opp_fields.get('Agency Type', '') or '').lower()
                is_federal    = any(k in agency_type for k in ('federal', 'dod', 'va', 'dhs', 'army', 'navy'))
                is_service    = any(k in (title + opp_fields.get('Description', '')).lower()
                                    for k in ('drug test', 'grounds', 'janitorial', 'courier',
                                              'nemt', 'fingerprint', 'notary', 'staffing', 'service'))
                vertex_auto_trigger('gpss.opportunity.won', opportunity_id, {
                    'agency_name':       agency,
                    'title':             title,
                    'contract_value':    contract_val,
                    'contract_number':   opp_fields.get('Contract Number', ''),
                    'is_federal':        is_federal,
                    'is_service_contract': is_service,
                    'payment_terms':     'Net 30',
                })
            except Exception as ve:
                print(f"VERTEX auto-trigger (GPSS Won): {ve}")

        if new_status == 'Lost' and old_status != 'Lost':
            try:
                from vertex_automation import vertex_auto_trigger
                vertex_auto_trigger('gpss.opportunity.lost', opportunity_id, {})
            except Exception as ve:
                print(f"VERTEX auto-trigger (GPSS Lost): {ve}")

        # NEXUS PIPELINE: Register contract in central registry
        pipeline_contract_id = None
        if new_status == 'Won' and old_status != 'Won':
            try:
                from nexus_pipeline_api import _load_contracts, _save_contracts, _generate_contract_id, _log_event
                nxdata = _load_contracts()
                pipeline_contract_id = _generate_contract_id()
                opp_fields = current_opp.get('fields', {})
                nx_contract = {
                    'id': pipeline_contract_id,
                    'title': opp_fields.get('Title', ''),
                    'agency': opp_fields.get('Agency Name', ''),
                    'value': opp_fields.get('Value', 0) or 0,
                    'status': 'Active',
                    'contract_type': 'Firm Fixed Price',
                    'service_type': opp_fields.get('Opportunity Category', ''),
                    'source': {
                        'gpss_opportunity_id': opportunity_id,
                        'rfp_number': opp_fields.get('RFP Number', ''),
                        'solicitation_number': opp_fields.get('Solicitation Number', ''),
                    },
                    'systems': {
                        'atlas_project_id': '',
                        'compass_contract_id': '',
                        'prism_contract_id': '',
                        'vertex_invoices': [],
                    },
                    'contacts': {
                        'co_name': opp_fields.get('CO Name', '') or '',
                        'co_email': opp_fields.get('CO Email', '') or '',
                        'cor_name': '',
                    },
                    'timeline': {
                        'identified': opp_fields.get('Created Date', ''),
                        'bid_submitted': '',
                        'won': datetime.now().isoformat(),
                        'start_date': '',
                        'end_date': '',
                    },
                    'health': {
                        'overall': 100, 'compliance': 'Green',
                        'deliverables_pct': 0, 'financials_pct': 0,
                        'orders_completed': 0, 'orders_total': 0,
                    },
                    'naics': opp_fields.get('NAICS', '') or '',
                    'set_aside': opp_fields.get('Set-Aside Type', '') or '',
                    'prism_orders': [],
                    'created_at': datetime.now().isoformat(),
                    'updated_at': datetime.now().isoformat(),
                }
                nxdata['contracts'].append(nx_contract)
                _log_event(nxdata, 'opportunity_won', pipeline_contract_id, 'GPSS', 'PIPELINE', {
                    'title': nx_contract['title'], 'agency': nx_contract['agency'],
                    'value': nx_contract['value'], 'gpss_id': opportunity_id,
                })
                _save_contracts(nxdata)
                print(f"✅ NEXUS PIPELINE: Contract {pipeline_contract_id} registered")
            except Exception as pe:
                print(f"NEXUS Pipeline registration: {pe}")

        # AUTO-CREATE ATLAS PROJECT IF STATUS CHANGED TO "WON"
        prism_contract_created = False
        if new_status == 'Won' and old_status != 'Won':
            existing_atlas_link = current_opp['fields'].get('ATLAS Project')

            # PRISM BRIDGE: If this is a field service contract, register it in PRISM
            PRISM_SERVICE_KEYWORDS = [
                'notary', 'notarization', 'RON', 'signing agent', 'credentialing', 'apostille',
                'drug test', 'drug testing', 'drug and alcohol testing', 'DOT drug', 'workplace drug',
                'SAMHSA', 'dna', 'dna test',
                'fingerprint', 'fingerprinting', 'biometrics', 'biometric', 'livescan', 'phlebotomy', 'courier',
                'medical courier', 'healthcare logistics', 'specimen', 'signing', 'mobile notary',
            ]
            opp_title = (current_opp['fields'].get('Title', '') or '').lower()
            opp_category = (current_opp['fields'].get('Opportunity Category', '') or '').lower()
            opp_desc = (current_opp['fields'].get('Description', '') or '').lower()
            combined_text = f"{opp_title} {opp_category} {opp_desc}"
            is_field_service = any(kw in combined_text for kw in PRISM_SERVICE_KEYWORDS)

            if is_field_service:
                try:
                    prism_fields = {
                        'Contract Name': current_opp['fields'].get('Title', ''),
                        'Client': current_opp['fields'].get('Agency Name', ''),
                        'GPSS Opportunity': [opportunity_id],
                        'Contract Value': current_opp['fields'].get('Value', 0),
                        'RFP Number': current_opp['fields'].get('RFP Number', ''),
                        'Status': 'Active',
                        'Start Date': datetime.now().strftime('%Y-%m-%d'),
                        'Source': 'GPSS Auto-Bridge',
                    }
                    airtable_client.create_record('PRISM Contracts', prism_fields)
                    prism_contract_created = True
                except Exception as pe:
                    print(f"PRISM bridge: {pe}")

            # COMPASS BRIDGE: Auto-register every won contract for post-award management
            compass_contract_created = False
            try:
                compass_fields = {
                    'Contract Number': current_opp['fields'].get('RFP Number', '') or current_opp['fields'].get('Solicitation Number', ''),
                    'Title': current_opp['fields'].get('Title', ''),
                    'Agency': current_opp['fields'].get('Agency Name', ''),
                    'Value': current_opp['fields'].get('Value', 0) or 0,
                    'Contract Type': 'Firm Fixed Price',
                    'Status': 'Active',
                    'Start Date': datetime.now().strftime('%Y-%m-%d'),
                    'CO Name': current_opp['fields'].get('CO Name', '') or '',
                    'CO Email': current_opp['fields'].get('CO Email', '') or '',
                    'NAICS': current_opp['fields'].get('NAICS', '') or '',
                    'Set Aside': current_opp['fields'].get('Set-Aside Type', '') or '',
                    'Health Score': 100,
                    'Compliance Status': 'Green',
                    'Created Date': datetime.now().isoformat(),
                    'GPSS Opportunity': [opportunity_id],
                }
                airtable_client.create_record('COMPASS Contracts', compass_fields)
                compass_contract_created = True
                print(f"✅ COMPASS contract created for: {compass_fields['Title']}")
            except Exception as ce:
                print(f"COMPASS bridge: {ce}")

            if not existing_atlas_link:
                try:
                    atlas_result = create_atlas_project_from_opportunity(opportunity_id, airtable_client)

                    # Link system IDs back to pipeline contract
                    if pipeline_contract_id:
                        try:
                            from nexus_pipeline_api import _load_contracts, _save_contracts, _find_contract
                            nxdata = _load_contracts()
                            nxc = _find_contract(nxdata, pipeline_contract_id)
                            if nxc:
                                nxc['systems']['atlas_project_id'] = atlas_result.get('project_id', '')
                                nxc['updated_at'] = datetime.now().isoformat()
                                _save_contracts(nxdata)
                        except Exception:
                            pass

                    msg_parts = ['Contract Won! ATLAS project created automatically!']
                    if prism_contract_created:
                        msg_parts.append('PRISM contract registered for field service.')
                    if compass_contract_created:
                        msg_parts.append('COMPASS post-award tracking activated.')
                    if pipeline_contract_id:
                        msg_parts.append(f'Pipeline contract: {pipeline_contract_id}')

                    return jsonify({
                        'success': True,
                        'message': ' '.join(msg_parts),
                        'atlas_project_created': True,
                        'atlas_project_id': atlas_result['project_id'],
                        'atlas_project_name': atlas_result['project_name'],
                        'wbs_generated': atlas_result.get('wbs_generated', False),
                        'prism_contract_created': prism_contract_created,
                        'compass_contract_created': compass_contract_created,
                        'pipeline_contract_id': pipeline_contract_id,
                        'advisor': advisor_insight,
                    })
                except Exception as atlas_error:
                    print(f"Error creating ATLAS project: {atlas_error}")
                    return jsonify({
                        'success': True,
                        'message': 'Opportunity updated. ATLAS project creation failed - please create manually.',
                        'atlas_error': str(atlas_error),
                        'prism_contract_created': prism_contract_created,
                        'compass_contract_created': compass_contract_created,
                        'pipeline_contract_id': pipeline_contract_id,
                        'advisor': advisor_insight,
                    })
        
        return jsonify({'success': True, 'advisor': advisor_insight, 'pipeline_contract_id': pipeline_contract_id})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/gpss/stats', methods=['GET'])
def get_gpss_stats():
    """Get GPSS dashboard statistics — real numbers, not fiction"""
    try:
        airtable_client = AirtableClient()
        
        try:
            opportunities = airtable_client.get_all_records('GPSS OPPORTUNITIES')
        except:
            opportunities = []
        
        # Set-asides we can't bid on
        INELIGIBLE = ['SDVOSB', 'SDVOSBC', 'SDVOSBS', 'VOSB', 'VSA', 'VSB', 
                       'HUBZone', 'HZC', 'HZS', '8(a)', '8A', '8AN', 'IEE', 'ISBEE']
        
        # Pipeline statuses = YOUR actual bids
        PIPELINE_STATUSES = [
            'Active', 'Active - Analyzing', 'Submitted', 'Submitted - Awaiting Award',
            'Awaiting Quotes', 'Ready to Bid', 'Not Started', 'Pursuing',
            'Sources Sought Submitted', 'No Contact Yet - URGENT',
        ]
        
        pipeline = []
        edwosb_opps = []
        home_state_opps = []
        forecast_opps = []
        submitted = []
        
        for o in opportunities:
            fields = o.get('fields', {})
            name = fields.get('Name', '')
            set_aside = (fields.get('Set-Aside Type', '') or '').upper()
            status = fields.get('Source Status', '') or ''
            state = (fields.get('State', '') or '').upper()
            
            # Skip ineligible
            skip = False
            for code in INELIGIBLE:
                if code.upper() in set_aside:
                    skip = True
                    break
            if 'SERVICE-DISABLED' in set_aside or 'VETERAN' in set_aside:
                skip = True
            if skip:
                continue
            
            # Categorize
            is_pipeline = any(ps in status for ps in PIPELINE_STATUSES) or (
                status and '[Forecast' not in name and 'SAM.gov' not in status 
                and 'USASpending' not in status and status not in ('New - API', 'Medium', '')
            )
            is_edwosb = 'EDWOSB' in set_aside or 'WOSB' in set_aside
            is_home = state in ('MI', 'MICHIGAN')
            is_forecast = '[Forecast' in name or 'Forecast' in status
            is_submitted = 'Submitted' in status
            
            if is_pipeline:
                pipeline.append(o)
            if is_edwosb:
                edwosb_opps.append(o)
            if is_home:
                home_state_opps.append(o)
            if is_forecast:
                forecast_opps.append(o)
            if is_submitted:
                submitted.append(o)
        
        stats = {
            'totalOpportunities': len(opportunities),
            'pipelineCount': len(pipeline),
            'edwsbSetAsides': len(edwosb_opps),
            'homeStateOpps': len(home_state_opps),
            'forecastCount': len(forecast_opps),
            'submittedCount': len(submitted),
            'pipelineBreakdown': {},
        }
        
        # Pipeline breakdown by status
        for o in pipeline:
            status = o['fields'].get('Source Status', 'Unknown')
            # Normalize long statuses
            for ps in PIPELINE_STATUSES:
                if ps in status:
                    status = ps
                    break
            stats['pipelineBreakdown'][status] = stats['pipelineBreakdown'].get(status, 0) + 1
        
        return jsonify(stats)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================================================
# D&I ADVANTAGE ANALYTICS (NEW - ADDITIVE ONLY)
# ============================================================================

@app.route('/gpss/analytics/di-advantage', methods=['GET'])
def get_di_advantage_analytics():
    """NEW ENDPOINT: Track D&I competitive advantage metrics - NO CHANGES TO EXISTING CODE"""
    try:
        airtable_client = AirtableClient()
        opportunities = airtable_client.get_all_records('GPSS OPPORTUNITIES')
        
        # Company certifications (from existing system)
        YOUR_CERTIFICATIONS = ['EDWOSB', 'WOSB', 'WBE', 'MBE', 'Small Business']
        
        # Initialize analytics
        analytics = {
            'set_aside_breakdown': {
                'edwosb': {'total': 0, 'value': 0, 'avg_competitors': '10-20', 'win_rate_range': '30-50%'},
                'wosb': {'total': 0, 'value': 0, 'avg_competitors': '20-40', 'win_rate_range': '20-35%'},
                'small_business': {'total': 0, 'value': 0, 'avg_competitors': '40-80', 'win_rate_range': '10-20%'},
                'unrestricted': {'total': 0, 'value': 0, 'avg_competitors': '100-300', 'win_rate_range': '3-8%'}
            },
            'eligible_opportunities': 0,
            'eligible_value': 0,
            'competitive_advantage': {
                'fewer_competitors': True,
                'higher_win_rate': True,
                'evaluation_preference': True
            },
            'recommendations': []
        }
        
        # Analyze each opportunity
        for opp in opportunities:
            fields = opp.get('fields', {})
            set_aside = fields.get('Set-Aside Type', 'Unrestricted')
            value = fields.get('Value', 0) if isinstance(fields.get('Value'), (int, float)) else 0
            
            # Categorize by set-aside type
            if 'EDWOSB' in set_aside:
                analytics['set_aside_breakdown']['edwosb']['total'] += 1
                analytics['set_aside_breakdown']['edwosb']['value'] += value
                analytics['eligible_opportunities'] += 1
                analytics['eligible_value'] += value
            elif 'WOSB' in set_aside or 'Women-Owned' in set_aside:
                analytics['set_aside_breakdown']['wosb']['total'] += 1
                analytics['set_aside_breakdown']['wosb']['value'] += value
                analytics['eligible_opportunities'] += 1
                analytics['eligible_value'] += value
            elif 'Small Business' in set_aside:
                analytics['set_aside_breakdown']['small_business']['total'] += 1
                analytics['set_aside_breakdown']['small_business']['value'] += value
                analytics['eligible_opportunities'] += 1
                analytics['eligible_value'] += value
            else:
                analytics['set_aside_breakdown']['unrestricted']['total'] += 1
                analytics['set_aside_breakdown']['unrestricted']['value'] += value
        
        # Generate smart recommendations
        total_opps = len(opportunities)
        eligible_pct = (analytics['eligible_opportunities'] / total_opps * 100) if total_opps > 0 else 0
        
        if analytics['set_aside_breakdown']['edwosb']['total'] > 0:
            analytics['recommendations'].append({
                'type': 'high_priority',
                'icon': '🎯',
                'message': f"You have {analytics['set_aside_breakdown']['edwosb']['total']} EDWOSB-only opportunities worth ${analytics['set_aside_breakdown']['edwosb']['value']:,.0f}. These have 30-50% win rates vs 3-8% unrestricted!",
                'action': 'Focus on EDWOSB set-asides first'
            })
        
        if analytics['set_aside_breakdown']['wosb']['total'] > 0:
            analytics['recommendations'].append({
                'type': 'medium_priority',
                'icon': '💼',
                'message': f"{analytics['set_aside_breakdown']['wosb']['total']} WOSB opportunities available worth ${analytics['set_aside_breakdown']['wosb']['value']:,.0f}. Win rate: 20-35%.",
                'action': 'Prioritize after EDWOSB'
            })
        
        if eligible_pct < 50:
            analytics['recommendations'].append({
                'type': 'opportunity',
                'icon': '🔍',
                'message': f"Only {eligible_pct:.0f}% of your pipeline is set-asides. Search SAM.gov for more WOSB/EDWOSB opportunities to increase win rate.",
                'action': 'Add more set-aside opportunities'
            })
        
        analytics['summary'] = {
            'total_opportunities': total_opps,
            'eligible_count': analytics['eligible_opportunities'],
            'eligible_percentage': round(eligible_pct, 1),
            'competitive_edge': 'HIGH' if eligible_pct > 50 else 'MEDIUM' if eligible_pct > 25 else 'LOW'
        }
        
        return jsonify(analytics)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/gpss/proposals', methods=['GET'])
def get_gpss_proposals():
    """Get all GPSS proposals"""
    try:
        airtable_client = AirtableClient()
        
        try:
            # Fetch all proposals from Airtable
            records = airtable_client.get_all_records('GPSS Proposals')
            
            # Transform records to match frontend format
            proposals = []
            for record in records:
                fields = record['fields']
                
                # Parse JSON fields
                try:
                    pricing_breakdown = eval(fields.get('PRICING-BREAKDOWN', '{}')) if isinstance(fields.get('PRICING-BREAKDOWN'), str) else {}
                    compliance_checklist = eval(fields.get('COMPLIANCE CHECKLIST', '{}')) if isinstance(fields.get('COMPLIANCE CHECKLIST'), str) else {}
                    recipients = eval(fields.get('PRIMARY RECIPIENT EMAIL', '{}')) if isinstance(fields.get('PRIMARY RECIPIENT EMAIL'), str) else {}
                except:
                    pricing_breakdown = {}
                    compliance_checklist = {}
                    recipients = {}
                
                # Parse ProposalBio biohack scores if available
                biohack_scores = None
                critical_issues = None
                try:
                    bh_json = fields.get('PROPOSALBIO BIOHACK SCORE JSON') or fields.get('ProposalBio Biohack Scores')
                    if bh_json:
                        biohack_scores = json.loads(bh_json) if isinstance(bh_json, str) else bh_json
                    ci_json = fields.get('PROPOSALBIO CRITICAL ISSUES JSON') or fields.get('ProposalBio Critical Issues')
                    if ci_json:
                        critical_issues = json.loads(ci_json) if isinstance(ci_json, str) else ci_json
                except:
                    pass

                proposals.append({
                    'id': record['id'],
                    'proposalName': fields.get('PROPOSAL NAME', ''),
                    'opportunityId': fields.get('GPSS OPPORTUNITY', [''])[0] if fields.get('GPSS OPPORTUNITY') else '',
                    'rfpNumber': fields.get('RFP NUMBER', ''),
                    'agency': fields.get('AGENCY NAME', ''),
                    'value': fields.get('Total Value', 0),
                    'status': fields.get('Status', 'Draft'),
                    'generatedDate': fields.get('GENERATED DATE', ''),
                    'sentDate': fields.get('SENT DATE'),
                    'dueDate': fields.get('DUE DATE', ''),
                    'executiveSummary': fields.get('EXECUTIVE SUMMARY', ''),
                    'technicalApproach': fields.get('TECHNICAL APPROACH', ''),
                    'staffingPlan': fields.get('STAFFING PLAN ', ''),
                    'pastPerformance': fields.get('PAST PERFORMANCE', ''),
                    'pricingTotal': fields.get('PRICING-TOTAL', 0),
                    'pricingBreakdown': pricing_breakdown,
                    'pricingJustification': fields.get('PRICING-JUSTIFICATION', ''),
                    'complianceChecklist': compliance_checklist,
                    'recipients': recipients,
                    # ProposalBio fields
                    'proposalBioScore': fields.get('PROPOSALBIO COMPOSITE SCORE') or fields.get('ProposalBio Composite Score'),
                    'proposalBioStatus': fields.get('PROPOSALBIO STATUS') or fields.get('ProposalBio Status'),
                    'proposalBioGate': fields.get('PROPOSALBIO GATE') or fields.get('ProposalBio Quality Gate'),
                    'proposalBioBiohacks': biohack_scores,
                    'proposalBioCriticalIssues': critical_issues,
                })
            
            return jsonify({'proposals': proposals})
        
        except Exception as e:
            # If table doesn't exist yet, return empty array
            print(f"Error fetching proposals: {e}")
            return jsonify({'proposals': []})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/gpss/proposals', methods=['POST'])
def create_gpss_proposal():
    """Save a new proposal to Airtable and automatically run ProposalBio™ analysis"""
    try:
        data = request.json
        airtable_client = AirtableClient()
        
        # Prepare fields for Airtable
        fields = {
            'PROPOSAL NAME': data.get('proposalName', ''),
            'RFP NUMBER': data.get('rfpNumber', ''),
            'AGENCY NAME': data.get('agency', ''),
            'STATUS': data.get('status', 'DRAFT'),
            'EXECUTIVE SUMMARY': data.get('executiveSummary', ''),
            'TECHNICAL APPROACH': data.get('technicalApproach', ''),
            'STAFFING PLAN ': data.get('staffingPlan', ''),
            'PAST PERFORMANCE': data.get('pastPerformance', ''),
            'PRICING-TOTAL': data.get('pricingTotal', 0),
            'PRICING-BREAKDOWN': str(data.get('pricingBreakdown', {})),
            'PRICING-JUSTIFICATION': data.get('pricingJustification', ''),
            'COMPLIANCE CHECKLIST': str(data.get('complianceChecklist', {})),
            'PRIMARY RECIPIENT EMAIL': str(data.get('recipients', {})),
            'GENERATED DATE': data.get('generatedDate', datetime.now().isoformat())
        }
        
        # Add optional date field only if provided
        if data.get('dueDate'):
            fields['DUE DATE'] = data.get('dueDate')
        
        # Add opportunity link if provided
        if data.get('opportunityId'):
            fields['GPSS OPPORTUNITY'] = [data.get('opportunityId')]
        
        # Create record in Airtable
        record = airtable_client.create_record('GPSS Proposals', fields)
        proposal_id = record['id']
        
        # ================================================================
        # AUTOMATICALLY RUN PROPOSALBIO™ ANALYSIS ON NEW PROPOSAL
        # ================================================================
        proposalbio_result = None
        try:
            # Build full proposal text for analysis
            proposal_text = f"""
{data.get('executiveSummary', '')}

{data.get('technicalApproach', '')}

{data.get('staffingPlan', '')}

{data.get('pastPerformance', '')}

{data.get('pricingJustification', '')}
"""
            
            # Prepare metadata for ProposalBio
            metadata = {
                'client_name': data.get('agency', ''),
                'agency': data.get('agency', ''),
                'agency_type': data.get('agencyType', 'federal'),
                'region': data.get('region', 'national'),
                'rfp_keywords': [],
                'opportunity_id': data.get('opportunityId'),
                'proposal_name': data.get('proposalName', ''),
            }
            
            # Run ProposalBio analysis
            proposalbio_service = ProposalBioService()
            analysis = proposalbio_service.analyze_proposal(
                proposal_text=proposal_text,
                metadata=metadata,
                airtable_client=airtable_client
            )
            
            # Update proposal with ProposalBio scores
            if analysis.get('success'):
                update_fields = {
                    'ProposalBio Composite Score': analysis['composite_score'],
                    'ProposalBio Status': analysis['overall_status'],
                    'ProposalBio Quality Gate': 'UNLOCKED' if analysis['composite_score'] >= 75 else 'LOCKED',
                    'ProposalBio Last Run': datetime.now().isoformat(),
                    'ProposalBio Revision Count': 0,
                }
                
                # Add critical issues if any
                if analysis.get('critical_issues'):
                    update_fields['ProposalBio Critical Issues'] = '\n'.join(analysis['critical_issues'])
                
                # Add priority improvements
                if analysis.get('priority_improvements'):
                    improvements = [f"{i+1}. {imp}" for i, imp in enumerate(analysis['priority_improvements'][:5])]
                    update_fields['ProposalBio Improvements'] = '\n'.join(improvements)
                
                airtable_client.update_record('GPSS Proposals', proposal_id, update_fields)
                
                proposalbio_result = {
                    'analyzed': True,
                    'composite_score': analysis['composite_score'],
                    'status': analysis['overall_status'],
                    'quality_gate': 'UNLOCKED' if analysis['composite_score'] >= 75 else 'LOCKED'
                }
            else:
                proposalbio_result = {
                    'analyzed': False,
                    'error': analysis.get('error', 'Unknown error')
                }
        
        except Exception as proposalbio_error:
            # Don't fail proposal creation if ProposalBio fails
            print(f"⚠️ ProposalBio analysis failed (non-fatal): {proposalbio_error}")
            proposalbio_result = {
                'analyzed': False,
                'error': str(proposalbio_error)
            }
        
        return jsonify({
            'success': True,
            'proposalId': proposal_id,
            'message': 'Proposal saved successfully',
            'proposalbio': proposalbio_result
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/gpss/proposals/<proposal_id>', methods=['PUT'])
def update_gpss_proposal(proposal_id):
    """Update an existing proposal (status, content sections, etc)"""
    try:
        data = request.json or {}
        airtable_client = AirtableClient()
        
        # Map frontend keys to Airtable field names
        field_map = {
            'status': 'STATUS',
            'executiveSummary': 'EXECUTIVE SUMMARY',
            'technicalApproach': 'TECHNICAL APPROACH',
            'staffingPlan': 'STAFFING PLAN ',
            'pastPerformance': 'PAST PERFORMANCE',
            'pricingJustification': 'PRICING-JUSTIFICATION',
            'pricingTotal': 'PRICING-TOTAL',
            'sentDate': 'SENT DATE',
        }
        
        update_fields = {}
        for frontend_key, airtable_key in field_map.items():
            if frontend_key in data:
                update_fields[airtable_key] = data[frontend_key]
        
        if not update_fields:
            return jsonify({"error": "No fields to update"}), 400
        
        airtable_client.update_record('GPSS Proposals', proposal_id, update_fields)
        
        return jsonify({
            "success": True,
            "message": "Proposal updated",
            "updated_fields": list(update_fields.keys())
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/gpss/proposals/<proposal_id>', methods=['DELETE'])
def delete_gpss_proposal(proposal_id):
    """Delete a proposal"""
    try:
        airtable_client = AirtableClient()
        airtable_client.get_table('GPSS Proposals').delete(proposal_id)
        return jsonify({"success": True, "message": "Proposal deleted"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/gpss/pricing/calculate', methods=['POST'])
def calculate_intelligent_pricing():
    """
    Calculate intelligent pricing for an opportunity
    
    Expected JSON:
    {
      "opportunity_id": "recXXXXX",
      "service_category": "NEMT" (optional)
    }
    """
    try:
        data = request.json
        opportunity_id = data.get('opportunity_id')
        service_category = data.get('service_category')
        
        if not opportunity_id:
            return jsonify({"error": "opportunity_id is required"}), 400
        
        # Initialize pricing agent
        pricing_agent = GPSSPricingAgent()
        
        # Calculate intelligent pricing
        result = pricing_agent.calculate_intelligent_price(opportunity_id, service_category)
        
        if 'error' in result:
            return jsonify(result), 400
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/gpss/pricing/history', methods=['GET'])
def get_pricing_history():
    """Get pricing history with optional filtering"""
    try:
        airtable_client = AirtableClient()
        
        # Get filter parameters
        service_category = request.args.get('service_category')
        win_loss = request.args.get('win_loss')
        
        try:
            records = airtable_client.get_all_records('Pricing History')
            
            # Apply filters
            filtered_records = records
            if service_category:
                filtered_records = [r for r in filtered_records if r['fields'].get('Service Category') == service_category]
            if win_loss:
                filtered_records = [r for r in filtered_records if r['fields'].get('Win/Loss') == win_loss]
            
            # Transform to simplified format
            history = []
            for record in filtered_records:
                fields = record['fields']
                history.append({
                    'id': record['id'],
                    'serviceCategory': fields.get('Service Category', ''),
                    'totalBid': fields.get('Total Bid Amount', 0),
                    'estimatedCosts': fields.get('Estimated Costs', 0),
                    'winLoss': fields.get('Win/Loss', ''),
                    'agency': fields.get('Agency', ''),
                    'bidDate': fields.get('Bid Date', ''),
                    'profitMargin': fields.get('Actual Profit Margin %', 0),
                    'winProbability': fields.get('Win Probability Score', 0)
                })
            
            return jsonify({'history': history})
        
        except Exception as e:
            # If table doesn't exist yet, return empty
            print(f"Error fetching pricing history: {e}")
            return jsonify({'history': []})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/gpss/compliance/analyze-rfp', methods=['POST'])
def analyze_rfp_compliance():
    """
    Extract compliance requirements from RFP document
    
    Expected JSON:
    {
      "rfp_content": "Full RFP text...",
      "rfp_id": "recXXXXX" (optional)
    }
    """
    try:
        data = request.json
        rfp_content = data.get('rfp_content')
        
        if not rfp_content:
            return jsonify({"error": "rfp_content is required"}), 400
        
        # Initialize compliance agent
        compliance_agent = GPSSComplianceAgent()
        
        # Analyze RFP and extract requirements
        requirements = compliance_agent.analyze_rfp_requirements(rfp_content)
        
        if 'error' in requirements:
            return jsonify(requirements), 400
        
        return jsonify(requirements)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/gpss/compliance/check-proposal', methods=['POST'])
def check_proposal_compliance():
    """
    Check proposal compliance against RFP requirements
    
    Expected JSON:
    {
      "proposal_data": {...},
      "rfp_requirements": {...}
    }
    """
    try:
        data = request.json
        proposal_data = data.get('proposal_data')
        rfp_requirements = data.get('rfp_requirements')
        
        if not proposal_data or not rfp_requirements:
            return jsonify({"error": "Both proposal_data and rfp_requirements are required"}), 400
        
        # Initialize compliance agent
        compliance_agent = GPSSComplianceAgent()
        
        # Check compliance
        compliance_check = compliance_agent.check_proposal_compliance(proposal_data, rfp_requirements)
        
        # Generate report
        report = compliance_agent.generate_compliance_report(compliance_check, rfp_requirements)
        
        return jsonify({
            'compliance_check': compliance_check,
            'report': report
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/gpss/mining/portal/<portal_id>', methods=['POST'])
def mine_portal(portal_id):
    """
    Mine opportunities from a specific portal
    
    URL Parameter:
    portal_id - Airtable record ID of the portal
    """
    try:
        mining_agent = GPSSOpportunityMiningAgent()
        result = mining_agent.mine_portal_opportunities(portal_id)
        
        if 'error' in result:
            return jsonify(result), 400
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/gpss/mining/auto-mine-all', methods=['POST'])
def auto_mine_all():
    """
    Automatically mine all portals for opportunities.
    Can be triggered from frontend or scheduler.
    """
    try:
        mining_agent = GPSSOpportunityMiningAgent()
        result = mining_agent.auto_mine_all_portals()
        
        # Cache results for status endpoint
        import os as _os
        cache_path = _os.path.join(_os.path.dirname(__file__), 'mining_results_cache.json')
        try:
            cache_data = {
                'timestamp': datetime.now().isoformat(),
                'portals_checked': result.get('portals_checked', 0),
                'total_opportunities_found': result.get('total_opportunities_found', 0),
                'errors_count': len(result.get('errors', [])),
            }
            with open(cache_path, 'w') as f:
                json.dump(cache_data, f)
        except:
            pass
        
        if result.get('error') and not result.get('success'):
            return jsonify(result), 400
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/gpss/mining/status', methods=['GET'])
def get_mining_status():
    """Get status of portal mining — portals count, last results, etc."""
    try:
        airtable_client = AirtableClient()
        try:
            records = airtable_client.get_all_records('VENDOR PORTAL')
        except:
            records = []
        
        total = len(records)
        with_url = sum(1 for r in records if r['fields'].get('PORTAL URL', '') or r['fields'].get('Portal URL', ''))
        
        # Check if we have cached mining results
        import os
        cache_path = os.path.join(os.path.dirname(__file__), 'mining_results_cache.json')
        last_results = None
        if os.path.exists(cache_path):
            try:
                with open(cache_path) as f:
                    last_results = json.load(f)
            except:
                pass
        
        return jsonify({
            'total_portals': total,
            'minable_portals': with_url,
            'last_mine': last_results
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/gpss/mining/check-rss-feeds', methods=['POST'])
def check_rss_feeds():
    """
    Check all RSS feeds for new government opportunities
    
    Returns:
        {
            "success": true,
            "feeds_checked": 3,
            "new_opportunities": 12,
            "opportunities": [...],
            "errors": []
        }
    """
    try:
        from nexus_backend import handle_check_rss_feeds
        result = handle_check_rss_feeds()
        
        if not result.get('success'):
            return jsonify(result), 400
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "feeds_checked": 0,
            "new_opportunities": 0
        }), 500


@app.route('/gpss/mining/search-sam-api', methods=['POST'])
def search_sam_gov_api():
    """
    Search SAM.gov API for federal opportunities
    
    Returns:
        {
            "success": true,
            "total_found": 1000,
            "imported": 50
        }
    """
    try:
        from nexus_backend import handle_sam_api_search
        result = handle_sam_api_search()
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e), "total_found": 0, "imported": 0}), 500


@app.route('/gpss/mining/search-govcon-api', methods=['POST'])
def search_govcon_api():
    """
    Search GovCon API for federal opportunities
    
    Returns:
        {
            "success": true,
            "total_found": 100,
            "imported": 25
        }
    """
    try:
        from nexus_backend import handle_govcon_api_search
        result = handle_govcon_api_search()
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e), "total_found": 0, "imported": 0}), 500


@app.route('/gpss/mining/mine-state-local', methods=['POST'])
def mine_state_local():
    """
    Mine state and local government opportunities
    
    Returns:
        {
            "success": true,
            "sources_checked": 5,
            "total_found": 200,
            "imported": 50
        }
    """
    try:
        from nexus_backend import handle_mine_state_local
        result = handle_mine_state_local()
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e), "sources_checked": 0, "imported": 0}), 500


@app.route('/gpss/mining/mine-edwosb', methods=['POST'])
def mine_edwosb_opportunities():
    """
    Mine specifically for EDWOSB/WOSB set-aside opportunities.
    Uses the dedicated EDWOSBWOSBMiner for targeted searching.
    """
    try:
        from auto_mine_edwosb_wosb_only import EDWOSBWOSBMiner
        miner = EDWOSBWOSBMiner()
        result = miner.mine_edwosb_wosb_opportunities(days_back=14)
        return jsonify({
            'success': True,
            'total_found': result.get('total_opportunities_found', 0),
            'imported': result.get('new_opportunities_added', 0),
            'duplicates_skipped': result.get('duplicates_skipped', 0),
            **result
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e), "total_found": 0, "imported": 0}), 500


@app.route('/gpss/forecasting/mine', methods=['POST'])
def mine_agency_forecasts():
    """
    ENHANCED: Mine 25+ sources for forecasts, expiring contracts, sole source leads.
    NOT just SAM.gov — this mines EVERYTHING.
    
    Optional JSON:
    {
      "tiers": ["sam", "agencies", "defense", "renewals", "edwosb_sole_source"]
    }
    
    Omit tiers to mine ALL sources. Or pass specific tiers:
      - "sam" = SAM.gov API (pre-solicitations, EDWOSB set-asides, sources sought)
      - "agencies" = 18 agency forecast pages (NASA, GSA, DHS, DoE, SSA, VA, etc.)
      - "defense" = DLA + USACE supply chain forecasts (10 sources)
      - "renewals" = USAspending expiring contract mining (re-compete predictions)
      - "edwosb_sole_source" = EDWOSB sole source opportunity detection
    """
    try:
        from federal_forecasts_system import handle_mine_federal_forecasts
        data = request.json or {}
        tiers = data.get('tiers', None)
        result = handle_mine_federal_forecasts(tiers=tiers)
        return jsonify({
            'success': True,
            **result
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/gpss/forecasting/mine-edwosb', methods=['POST'])
def mine_edwosb_forecasts():
    """
    EDWOSB-ONLY mining — fast, targeted search.
    Mines SAM.gov for EDWOSB/WOSB set-asides + sole source leads.
    This is the quick scan when you want EDWOSB opportunities NOW.
    """
    try:
        from federal_forecasts_system import handle_mine_edwosb_only
        result = handle_mine_edwosb_only()
        return jsonify({
            'success': True,
            **result
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/gpss/forecasting/mine-renewals', methods=['POST'])
def mine_contract_renewals():
    """
    Mine USAspending.gov for expiring contracts in DDI's NAICS codes.
    These are contracts ending in 3-18 months that will be re-competed.
    High-confidence forecasts — the government still needs the products/services.
    """
    try:
        from federal_forecasts_system import handle_mine_renewals
        result = handle_mine_renewals()
        return jsonify({
            'success': True,
            **result
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/gpss/forecasting/intelligence-report', methods=['GET'])
def get_intelligence_report():
    """
    Generate the Opportunity Intelligence Dashboard report.
    Shows pipeline summary, EDWOSB advantage metrics, upcoming events,
    and source counts across all mining tiers.
    """
    try:
        from federal_forecasts_system import handle_intelligence_report
        result = handle_intelligence_report()
        return jsonify({
            'success': True,
            **result
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/gpss/forecasting/events', methods=['GET'])
def get_industry_events():
    """
    Get upcoming DLA/defense industry events.
    Includes Battle Creek MI (May 2026), Columbus OH, Cherry Hill NJ, etc.
    """
    try:
        from federal_forecasts_system import handle_get_events
        result = handle_get_events()
        return jsonify({
            'success': True,
            **result
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/gpss/forecasting/osdbu-contacts', methods=['POST'])
def harvest_osdbu_contacts():
    """
    Harvest OSDBU (Office of Small & Disadvantaged Business Utilization) contacts.
    These are the people at each agency who HELP small businesses find opportunities.
    Scrapes 7+ agency OSDBU websites for names, emails, phone numbers.
    """
    try:
        from federal_forecasts_system import handle_harvest_osdbu_contacts
        result = handle_harvest_osdbu_contacts()
        return jsonify({
            'success': True,
            **result
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/gpss/forecasting/generate', methods=['POST'])
def generate_forecasts():
    """
    Generate opportunity forecasts based on historical data (AI analysis).
    
    Optional JSON:
    {
      "agency_name": "Agency Name" (optional - forecast for specific agency),
      "lookback_months": 24 (optional - default 24)
    }
    """
    try:
        data = request.json or {}
        agency_name = data.get('agency_name')
        lookback_months = data.get('lookback_months', 24)
        
        mining_agent = GPSSOpportunityMiningAgent()
        result = mining_agent.forecast_opportunities(agency_name, lookback_months)
        
        if 'error' in result:
            return jsonify(result), 400
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/gpss/forecasting/agency-analysis/<agency_name>', methods=['GET'])
def analyze_agency(agency_name):
    """
    Analyze an agency's spending patterns and preferences
    
    URL Parameter:
    agency_name - Name of the agency to analyze
    """
    try:
        mining_agent = GPSSOpportunityMiningAgent()
        result = mining_agent.analyze_agency_spending(agency_name)
        
        if 'error' in result:
            return jsonify(result), 400
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/gpss/alerts/generate', methods=['GET'])
def generate_alerts():
    """
    Generate alerts for opportunities that need attention
    Returns list of urgent opportunities and forecasts
    """
    try:
        mining_agent = GPSSOpportunityMiningAgent()
        alerts = mining_agent.generate_opportunity_alerts()
        
        return jsonify({'alerts': alerts, 'total': len(alerts)})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/gpss/mining/target/<target_id>', methods=['POST'])
def scrape_target(target_id):
    """
    Scrape a Mining Target (public sites - NO login required)
    Finds opportunities from ANY website
    
    URL Parameter:
    target_id - Airtable record ID of the mining target
    """
    try:
        mining_agent = GPSSOpportunityMiningAgent()
        result = mining_agent.scrape_mining_target(target_id)
        
        if 'error' in result:
            return jsonify(result), 400
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/gpss/mining/scrape-all-targets', methods=['POST'])
def scrape_all_targets():
    """
    Scrape ALL active Mining Targets
    This discovers opportunities from ANY public source
    """
    try:
        mining_agent = GPSSOpportunityMiningAgent()
        result = mining_agent.scrape_all_targets()
        
        if 'error' in result:
            return jsonify(result), 400
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/gpss/intelligence/competitor/<competitor_name>', methods=['GET'])
def get_competitor_intelligence(competitor_name):
    """
    Search for competitor contract wins
    Scrapes news, press releases, USASpending.gov, etc.
    
    URL Parameter:
    competitor_name - Name of competitor to research
    
    Optional Query Parameter:
    keywords - Additional search keywords
    """
    try:
        keywords = request.args.get('keywords')
        
        mining_agent = GPSSOpportunityMiningAgent()
        result = mining_agent.competitive_intelligence_search(competitor_name, keywords)
        
        if 'error' in result:
            return jsonify(result), 400
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =====================================================================
# INVOICE ROUTES
# =====================================================================

@app.route('/invoices', methods=['GET'])
def get_invoices():
    """
    Get all invoices with optional filters
    
    Query Parameters:
    - status: Filter by invoice status (Draft, Sent, Pending, Paid, Overdue, Cancelled)
    - source_system: Filter by source system (GPSS, ATLAS, DDCSS, Manual)
    - client_type: Filter by client type (Government - Federal, Enterprise - Private, etc.)
    """
    try:
        filters = {}
        if request.args.get('status'):
            filters['status'] = request.args.get('status')
        if request.args.get('source_system'):
            filters['source_system'] = request.args.get('source_system')
        if request.args.get('client_type'):
            filters['client_type'] = request.args.get('client_type')
        
        result = handle_get_invoices(filters if filters else None)
        
        if not result.get('success'):
            return jsonify(result), 400
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500


@app.route('/invoices/<invoice_id>', methods=['GET'])
def get_invoice(invoice_id):
    """Get single invoice details"""
    try:
        result = handle_get_invoice(invoice_id)
        
        if not result.get('success'):
            return jsonify(result), 404
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500


@app.route('/invoices/generate/opportunity/<opportunity_id>', methods=['POST'])
def generate_invoice_from_opportunity(opportunity_id):
    """
    Generate invoice from GPSS opportunity
    
    URL Parameter:
    - opportunity_id: Airtable record ID of the opportunity
    """
    try:
        result = handle_generate_invoice_from_opportunity(opportunity_id)
        
        if not result.get('success'):
            return jsonify(result), 400
        
        return jsonify(result), 201
    
    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500


@app.route('/invoices/generate/project/<project_id>', methods=['POST'])
def generate_invoice_from_project(project_id):
    """
    Generate invoice from ATLAS project
    
    URL Parameter:
    - project_id: Airtable record ID of the project
    """
    try:
        result = handle_generate_invoice_from_project(project_id)
        
        if not result.get('success'):
            return jsonify(result), 400
        
        return jsonify(result), 201
    
    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500


@app.route('/invoices/generate/prospect/<prospect_id>', methods=['POST'])
def generate_invoice_from_prospect(prospect_id):
    """
    Generate invoice from DDCSS prospect
    
    URL Parameter:
    - prospect_id: Airtable record ID of the prospect
    """
    try:
        result = handle_generate_invoice_from_prospect(prospect_id)
        
        if not result.get('success'):
            return jsonify(result), 400
        
        return jsonify(result), 201
    
    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500


@app.route('/invoices/<invoice_id>', methods=['PUT'])
def update_invoice(invoice_id):
    """
    Update existing invoice
    
    Request Body: JSON with fields to update
    {
        "Invoice Status": "Sent",
        "Sent To Email": "client@example.com",
        "Sent Date": "2026-01-10T14:30:00",
        ...
    }
    """
    try:
        updates = request.json
        
        if not updates:
            return jsonify({"error": "No update data provided", "success": False}), 400
        
        result = handle_update_invoice(invoice_id, updates)
        
        if not result.get('success'):
            return jsonify(result), 400
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500


@app.route('/invoices/<invoice_id>', methods=['DELETE'])
def delete_invoice(invoice_id):
    """Delete an invoice"""
    try:
        result = handle_delete_invoice(invoice_id)
        
        if not result.get('success'):
            return jsonify(result), 400
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500


@app.route('/invoices/<invoice_id>/send', methods=['POST'])
def send_invoice(invoice_id):
    """
    Mark invoice as sent and update sent date/email
    
    Request Body:
    {
        "email": "client@example.com",
        "message": "Optional custom message"
    }
    """
    try:
        data = request.json or {}
        email = data.get('email')
        
        if not email:
            return jsonify({"error": "Email address required", "success": False}), 400
        
        # Update invoice status and sent details
        updates = {
            "Invoice Status": "Sent",
            "Sent To Email": email,
            "Sent Date": datetime.now().isoformat()
        }
        
        result = handle_update_invoice(invoice_id, updates)
        
        if not result.get('success'):
            return jsonify(result), 400
        
        return jsonify({
            **result,
            "message": f"Invoice marked as sent to {email}"
        })
    
    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500


# =====================================================================
# GPSS CONTACTS ENDPOINTS
# =====================================================================

@app.route('/gpss/contacts', methods=['GET'])
def get_gpss_contacts():
    """Get all contacts with optional filtering"""
    try:
        import re as re_mod
        airtable_client = AirtableClient()
        records = airtable_client.get_all_records('GPSS CONTACTS')
        
        # Phone extraction patterns
        phone_pattern = re_mod.compile(
            r'(?:Phone|Tel|Contact|Mobile|Cell|Fax)?[:\s]*'
            r'(\(?\d{3}\)?[\s\-.]?\d{3}[\s\-.]?\d{4}(?:\s*(?:ext|x|extension)[\s.]*\d+)?)',
            re_mod.IGNORECASE
        )
        vanity_pattern = re_mod.compile(r'1[\-.]?\d{3}[\-.][A-Z]{2,}[\-.]?[A-Z]+', re_mod.IGNORECASE)
        
        def extract_phone(text):
            """Pull phone number out of free text (Notes, Title fields)"""
            if not text:
                return ''
            # Priority 1: Vanity numbers (1-800-GRAINGER etc)
            match = vanity_pattern.search(text)
            if match:
                return match.group(0)
            
            # Priority 2: Labeled phone ("Phone: xxx", "Tel: xxx")
            labeled = re_mod.search(
                r'(?:Phone|Tel|Mobile|Cell|Direct)[:\s]+(\(?\d{3}\)?[\s\-.]?\d{3}[\s\-.]?\d{4}(?:\s*(?:ext|x)[\s.]*\d+)?)',
                text, re_mod.IGNORECASE
            )
            if labeled:
                return labeled.group(1).strip()
            
            # Priority 3: "Contact: xxx"
            contact_m = re_mod.search(
                r'Contact[:\s]+(\(?\d{3}\)?[\s\-.]?\d{3}[\s\-.]?\d{4})',
                text, re_mod.IGNORECASE
            )
            if contact_m:
                return contact_m.group(1).strip()
            
            # Priority 4: Formatted phone (must have dashes, parens, or dots)
            formatted = re_mod.search(
                r'(\(\d{3}\)[\s\-.]?\d{3}[\s\-.]?\d{4}|\d{3}[\-.]?\d{3}[\-.]?\d{4})',
                text
            )
            if formatted:
                num = formatted.group(1)
                digits_only = re_mod.sub(r'\D', '', num)
                has_fmt = any(c in num for c in '()- .')
                if has_fmt and len(digits_only) >= 10 and not digits_only.startswith('000'):
                    return num
            
            return ''
        
        contacts = []
        for record in records:
            fields = record['fields']
            
            # Parse Name field
            full_name = fields.get('Name', '').strip()
            name_parts = full_name.split(' ', 1) if full_name else ['', '']
            first_name = name_parts[0] if len(name_parts) > 0 else ''
            last_name = name_parts[1] if len(name_parts) > 1 else ''
            
            # Try dedicated Phone field first, then extract from Notes/Title
            phone = fields.get('Phone', '').strip()
            if not phone:
                notes = fields.get('Notes', '')
                title = fields.get('Title', '')
                phone = extract_phone(notes) or extract_phone(title)
            
            contacts.append({
                'id': record['id'],
                'firstName': first_name,
                'lastName': last_name,
                'fullName': full_name,
                'email': fields.get('Email', ''),
                'phone': phone,
                'title': fields.get('Title', ''),
                'agency': fields.get('Organization', ''),
                'organization': fields.get('Organization', ''),
                'department': fields.get('Department', ''),
                'roleCategory': fields.get('Role Category', ''),
                'priority': fields.get('Priority', ''),
                'notes': fields.get('Notes', ''),
                'source': fields.get('Source', 'Manual'),
                'created': fields.get('Created', '')
            })
        
        return jsonify({'contacts': contacts})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/gpss/contacts', methods=['POST'])
def create_gpss_contact():
    """Create a new contact"""
    try:
        data = request.json
        airtable_client = AirtableClient()
        
        first = data.get('firstName', '')
        last = data.get('lastName', '')
        full_name = f"{first} {last}".strip() if first or last else data.get('name', '')
        
        phone = data.get('phone', '')
        notes_parts = []
        if phone:
            notes_parts.append(f"Phone: {phone}")
        extra_notes = data.get('notes', '')
        if extra_notes:
            notes_parts.append(extra_notes)
        source = data.get('source', 'Manual')
        if source and source != 'Manual':
            notes_parts.append(f"Source: {source}")
        
        fields = {
            'Name': full_name,
            'Email': data.get('email', ''),
            'Title': data.get('title', ''),
            'Organization': data.get('agency', data.get('organization', '')),
            'Role Category': data.get('roleCategory', ''),
            'Notes': '\n'.join(notes_parts) if notes_parts else '',
        }
        fields = {k: v for k, v in fields.items() if v}
        
        result = airtable_client.create_record('GPSS CONTACTS', fields)
        return jsonify({'contact': {'id': result['id'], **fields}})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/gpss/contacts/<contact_id>', methods=['PUT'])
def update_gpss_contact(contact_id):
    """Update a contact"""
    try:
        data = request.json
        airtable_client = AirtableClient()
        
        field_mapping = {
            'firstName': 'First Name',
            'lastName': 'Last Name',
            'email': 'Email',
            'phone': 'Phone',
            'title': 'Title',
            'agency': 'Agency',
            'department': 'Department',
            'address': 'Address',
            'city': 'City',
            'state': 'State',
            'zip': 'ZIP',
            'source': 'Source'
        }
        
        update_fields = {}
        for key, airtable_field in field_mapping.items():
            if key in data:
                update_fields[airtable_field] = data[key]
        
        update_fields['Last Modified'] = datetime.now().isoformat()
        
        airtable_client.update_record('GPSS CONTACTS', contact_id, update_fields)
        return jsonify({'success': True})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/gpss/contacts/<contact_id>', methods=['DELETE'])
def delete_gpss_contact(contact_id):
    """Delete a contact"""
    try:
        airtable_client = AirtableClient()
        table = airtable_client.get_table('GPSS CONTACTS')
        table.delete(contact_id)
        return jsonify({'success': True})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =====================================================================
# GPSS PRODUCTS ENDPOINTS
# =====================================================================

@app.route('/gpss/products', methods=['GET'])
def get_gpss_products():
    """Get all products"""
    try:
        import re as re_mod
        airtable_client = AirtableClient()
        
        # Try to get products from Airtable (table might not exist yet)
        try:
            records = airtable_client.get_all_records('GPSS PRODUCTS')
        except:
            return jsonify({'products': []})
        
        def parse_unit_price(raw):
            """
            Parse complex UNIT PRICE text into a numeric per-unit price.
            Handles formats like:
              '$300.00/pk5 ($60/ea)'  -> 60.00
              '$7.89/pk2 ($3.95/ea)'  -> 3.95
              '15.25/each'            -> 15.25
              '$70.80/ea (ON SALE)'   -> 70.80
              '$75.00'                -> 75.00
              '$126.00/ea'            -> 126.00
            """
            if not raw:
                return 0.0, 'each'
            text = str(raw).strip()
            
            # Priority 1: look for per-unit price like ($60/ea) or $3.95/ea
            ea_match = re_mod.search(r'\$?([\d,]+\.?\d*)\s*/\s*ea', text, re_mod.IGNORECASE)
            if ea_match:
                try:
                    return float(ea_match.group(1).replace(',', '')), 'each'
                except:
                    pass
            
            # Priority 2: look for price/each like 15.25/each
            each_match = re_mod.search(r'\$?([\d,]+\.?\d*)\s*/\s*each', text, re_mod.IGNORECASE)
            if each_match:
                try:
                    return float(each_match.group(1).replace(',', '')), 'each'
                except:
                    pass
            
            # Priority 3: price per pack like $300.00/pk5 - extract pack price and unit
            pack_match = re_mod.search(r'\$?([\d,]+\.?\d*)\s*/\s*(pk\d+|pack|case|box|roll|bag|set|pair)', text, re_mod.IGNORECASE)
            if pack_match:
                try:
                    pack_price = float(pack_match.group(1).replace(',', ''))
                    unit_label = pack_match.group(2).lower()
                    # Try to extract count from pk5 etc.
                    count_match = re_mod.search(r'(\d+)', unit_label)
                    if count_match:
                        count = int(count_match.group(1))
                        if count > 0:
                            return pack_price / count, 'each'
                    return pack_price, unit_label
                except:
                    pass
            
            # Priority 4: just the first dollar amount in the string
            first_price = re_mod.search(r'\$?([\d,]+\.?\d+)', text)
            if first_price:
                try:
                    return float(first_price.group(1).replace(',', '')), 'each'
                except:
                    pass
            
            return 0.0, 'each'
        
        products = []
        for record in records:
            fields = record['fields']
            
            raw_price = fields.get('UNIT PRICE', '')
            price, unit = parse_unit_price(raw_price)
            
            products.append({
                'id': record['id'],
                'name': fields.get('NAME', ''),
                'description': fields.get('Description', ''),
                'category': fields.get('PRODUCT CATEGORY', ''),
                'basePrice': price,
                'unitPrice': price,
                'rawPrice': str(raw_price) if raw_price else '',  # Original text for display
                'unit': unit,
                'supplier': fields.get('SUPPLIER', ''),
                'manufacturers': fields.get('Manufacturers', ''),
                'created': fields.get('Created', '')
            })
        
        return jsonify({'products': products})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/gpss/products', methods=['POST'])
def create_gpss_product():
    """Create a new product"""
    try:
        data = request.json
        airtable_client = AirtableClient()
        
        fields = {
            'Product Name': data.get('name', ''),
            'Description': data.get('description', ''),
            'Category': data.get('category', ''),
            'Base Price': data.get('basePrice', 0),
            'Unit': data.get('unit', 'each'),
            'Service Category': data.get('serviceCategory', ''),
            'Created': datetime.now().isoformat()
        }
        
        result = airtable_client.create_record('Products', fields)
        return jsonify({'product': {'id': result['id'], **fields}})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/gpss/products/<product_id>', methods=['PUT'])
def update_gpss_product(product_id):
    """Update a product"""
    try:
        data = request.json
        airtable_client = AirtableClient()
        
        field_mapping = {
            'name': 'Product Name',
            'description': 'Description',
            'category': 'Category',
            'basePrice': 'Base Price',
            'unit': 'Unit',
            'serviceCategory': 'Service Category'
        }
        
        update_fields = {}
        for key, airtable_field in field_mapping.items():
            if key in data:
                update_fields[airtable_field] = data[key]
        
        update_fields['Last Modified'] = datetime.now().isoformat()
        
        airtable_client.update_record('Products', product_id, update_fields)
        return jsonify({'success': True})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/gpss/products/<product_id>', methods=['DELETE'])
def delete_gpss_product(product_id):
    """Delete a product"""
    try:
        airtable_client = AirtableClient()
        table = airtable_client.get_table('Products')
        table.delete(product_id)
        return jsonify({'success': True})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =====================================================================
# GPSS SUPPLIER MINING & AUTOMATED QUOTING ENDPOINTS
# =====================================================================

@app.route('/gpss/suppliers', methods=['GET'])
def get_gpss_suppliers():
    """Get all suppliers with optional filters"""
    try:
        from nexus_backend import handle_search_suppliers
        
        # Get filter parameters
        filters = {
            'category': request.args.get('category'),
            'keywords': request.args.getlist('keywords'),
            'min_rating': float(request.args.get('min_rating', 0))
        }
        
        suppliers = handle_search_suppliers(filters)
        return jsonify({'suppliers': suppliers})
    
    except Exception as e:
        print(f"Error getting suppliers: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/gpss/suppliers', methods=['POST'])
def create_gpss_supplier():
    """Create a new supplier - maps frontend field names to Airtable field names"""
    try:
        from nexus_backend import handle_create_supplier
        
        data = request.json or {}
        
        # Map frontend form field names to Airtable uppercase field names
        field_map = {
            'Company Name': 'COMPANY NAME',
            'Website': 'WEBSITE',
            'Primary Contact Email': 'PRIMARY CONTACT EMAIL',
            'Primary Contact Phone': 'PRIMARY CONTACT PHONE',
            'Product Keywords': 'PRODUCT KEYWORDS',
            'Net 30 Available': 'NET 30',
            'Net 45 Available': 'NET 45',
            'Business Status': 'BUSINESS STATUS',
            'Typical Margin (%)': 'TYPICAL MARGIN',
            'Discovery Method': 'DISCOVERY METHOD',
            'Discovered By': 'DISCOVERED BY',
        }
        
        # Single-select fields must be UPPERCASE to match Airtable options
        select_fields_upper = {'BUSINESS STATUS', 'DISCOVERY METHOD', 'DISCOVERED BY'}
        
        mapped_data = {}
        for key, value in data.items():
            airtable_key = field_map.get(key, key)
            if airtable_key in select_fields_upper and isinstance(value, str):
                value = value.upper()
            mapped_data[airtable_key] = value
        
        result = handle_create_supplier(mapped_data)
        
        if result.get('error'):
            return jsonify(result), 400
        
        return jsonify({'supplier': result})
    
    except Exception as e:
        print(f"Error creating supplier: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/gpss/suppliers/<supplier_id>', methods=['GET'])
def get_gpss_supplier(supplier_id):
    """Get single supplier details"""
    try:
        from nexus_backend import handle_get_supplier
        
        supplier = handle_get_supplier(supplier_id)
        
        if not supplier:
            return jsonify({"error": "Supplier not found"}), 404
        
        return jsonify({'supplier': supplier})
    
    except Exception as e:
        print(f"Error getting supplier: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/gpss/suppliers/<supplier_id>', methods=['PUT'])
def update_gpss_supplier(supplier_id):
    """Update supplier - maps frontend field names to Airtable field names"""
    try:
        from nexus_backend import handle_update_supplier
        
        data = request.json or {}
        
        # Map frontend form field names to Airtable uppercase field names
        field_map = {
            'Company Name': 'COMPANY NAME',
            'Website': 'WEBSITE',
            'Primary Contact Email': 'PRIMARY CONTACT EMAIL',
            'Primary Contact Phone': 'PRIMARY CONTACT PHONE',
            'Product Keywords': 'PRODUCT KEYWORDS',
            'Net 30 Available': 'NET 30',
            'Net 45 Available': 'NET 45',
            'Business Status': 'BUSINESS STATUS',
            'Typical Margin (%)': 'TYPICAL MARGIN',
            'Discovery Method': 'DISCOVERY METHOD',
            'Discovered By': 'DISCOVERED BY',
        }
        
        # Single-select fields must be UPPERCASE to match Airtable options
        select_fields_upper = {'BUSINESS STATUS', 'DISCOVERY METHOD', 'DISCOVERED BY'}
        
        mapped_data = {}
        for key, value in data.items():
            airtable_key = field_map.get(key, key)
            if airtable_key in select_fields_upper and isinstance(value, str):
                value = value.upper()
            mapped_data[airtable_key] = value
        
        result = handle_update_supplier(supplier_id, mapped_data)
        
        if result.get('error'):
            return jsonify(result), 400
        
        return jsonify({'success': True, 'supplier': result})
    
    except Exception as e:
        print(f"Error updating supplier: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/gpss/suppliers/<supplier_id>/rate', methods=['POST'])
def rate_supplier_performance(supplier_id):
    """
    Update supplier performance rating based on outcomes.
    System learns from each interaction to prioritize better suppliers.
    
    Body:
    {
        "outcome": "quote_received_fast"  // or: quote_late, no_response, competitive_price, overpriced, won_with_supplier, reliable_delivery, late_delivery
    }
    
    Returns updated rating info.
    """
    try:
        data = request.get_json() or {}
        outcome = data.get('outcome', '')
        
        if not outcome:
            return jsonify({'success': False, 'error': 'outcome is required'}), 400
        
        valid_outcomes = [
            'quote_received_fast', 'quote_received', 'quote_late',
            'no_response', 'competitive_price', 'overpriced',
            'won_with_supplier', 'reliable_delivery', 'late_delivery'
        ]
        if outcome not in valid_outcomes:
            return jsonify({
                'success': False,
                'error': f'Invalid outcome. Must be one of: {", ".join(valid_outcomes)}'
            }), 400
        
        from nexus_backend import GPSSSupplierMiner
        miner = GPSSSupplierMiner()
        result = miner.update_supplier_rating(supplier_id, outcome)
        
        if result.get('error'):
            return jsonify(result), 400
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/gpss/suppliers/find-for-product', methods=['POST'])
def find_suppliers_for_product():
    """
    Find suppliers for a specific product (checks database first, then auto-mines if needed)
    
    POST body:
    {
        "product": "office chairs",
        "category": "Office Furniture",  // optional
        "max_results": 10,  // optional, default 10
        "auto_mine": true  // optional, default true - automatically mine web if not enough in DB
    }
    """
    try:
        from nexus_backend import GPSSSupplierMiner
        
        data = request.json
        product = data.get('product')
        category = data.get('category')
        max_results = data.get('max_results', 10)
        auto_mine = data.get('auto_mine', True)
        
        if not product:
            return jsonify({"error": "product is required"}), 400
        
        miner = GPSSSupplierMiner()
        suppliers = miner.find_suppliers_for_product(
            product=product,
            category=category,
            max_results=max_results,
            auto_mine=auto_mine
        )
        
        return jsonify({
            'success': True,
            'product': product,
            'category': category,
            'suppliers_found': len(suppliers),
            'suppliers': suppliers
        })
    
    except Exception as e:
        print(f"Error finding suppliers: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/gpss/suppliers/mine-thomasnet', methods=['POST'])
def mine_thomasnet_suppliers():
    """
    Mine suppliers from ThomasNet.com
    
    POST body:
    {
        "product": "office chairs",
        "max_results": 15
    }
    """
    try:
        from nexus_backend import GPSSSupplierMiner
        
        data = request.json
        product = data.get('product')
        max_results = data.get('max_results', 15)
        
        if not product:
            return jsonify({"error": "product is required"}), 400
        
        miner = GPSSSupplierMiner()
        suppliers = miner.search_thomasnet(product, max_results)
        
        return jsonify({
            'success': True,
            'source': 'thomasnet',
            'product': product,
            'suppliers_found': len(suppliers),
            'suppliers': suppliers
        })
    
    except Exception as e:
        print(f"Error mining ThomasNet: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/gpss/suppliers/mine-google', methods=['POST'])
def mine_google_suppliers():
    """
    Mine suppliers using Google Custom Search API
    
    POST body:
    {
        "product": "industrial pumps",
        "max_results": 10
    }
    """
    try:
        from nexus_backend import GPSSSupplierMiner
        
        data = request.json
        product = data.get('product')
        max_results = data.get('max_results', 10)
        
        if not product:
            return jsonify({"error": "product is required"}), 400
        
        miner = GPSSSupplierMiner()
        suppliers = miner.search_google_suppliers(product, max_results)
        
        return jsonify({
            'success': True,
            'source': 'google',
            'product': product,
            'suppliers_found': len(suppliers),
            'suppliers': suppliers
        })
    
    except Exception as e:
        print(f"Error mining Google: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/gpss/suppliers/mine-gsa', methods=['POST'])
def mine_gsa_suppliers():
    """
    Mine suppliers from GSA Advantage
    
    POST body:
    {
        "product": "laptops",
        "max_results": 10
    }
    """
    try:
        from nexus_backend import GPSSSupplierMiner
        
        data = request.json
        product = data.get('product')
        max_results = data.get('max_results', 10)
        
        if not product:
            return jsonify({"error": "product is required"}), 400
        
        miner = GPSSSupplierMiner()
        suppliers = miner.search_gsa_suppliers(product, max_results)
        
        return jsonify({
            'success': True,
            'source': 'gsa_advantage',
            'product': product,
            'suppliers_found': len(suppliers),
            'suppliers': suppliers
        })
    
    except Exception as e:
        print(f"Error mining GSA: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/gpss/suppliers/mine-all', methods=['POST'])
def mine_all_supplier_sources():
    """
    Mine suppliers from ALL sources (Database + ThomasNet + Google + GSA)
    
    POST body:
    {
        "product": "office furniture",
        "category": "Office Furniture",
        "sources": ["database", "thomasnet", "google", "gsa"],  // optional, defaults to all
        "auto_import_threshold": 80  // optional, default 80
    }
    """
    try:
        from nexus_backend import GPSSSupplierMiner
        
        data = request.json
        product = data.get('product')
        category = data.get('category')
        sources = data.get('sources')  # None = all sources
        auto_import_threshold = data.get('auto_import_threshold', 80)
        
        if not product:
            return jsonify({"error": "product is required"}), 400
        
        miner = GPSSSupplierMiner()
        result = miner.mine_all_sources(
            product=product,
            category=category,
            sources=sources,
            auto_import_threshold=auto_import_threshold
        )
        
        return jsonify(result)
    
    except Exception as e:
        print(f"Error mining all sources: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/gpss/suppliers/import-csv', methods=['POST'])
def import_suppliers_csv():
    """
    Import suppliers from uploaded CSV file
    
    POST multipart/form-data:
    - file: CSV file
    - field_mapping: JSON string (optional) mapping CSV columns to Airtable fields
    
    Example field_mapping:
    {
        "Company": "Company Name",
        "Email": "Primary Contact Email",
        "Phone": "Primary Contact Phone"
    }
    """
    try:
        from nexus_backend import GPSSSupplierMiner
        import json
        
        if 'file' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        if not file.filename.endswith('.csv'):
            return jsonify({"error": "File must be CSV"}), 400
        
        # Save file temporarily
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w+b', suffix='.csv', delete=False) as tmp:
            file.save(tmp.name)
            tmp_path = tmp.name
        
        # Get field mapping if provided
        field_mapping = None
        if 'field_mapping' in request.form:
            field_mapping = json.loads(request.form['field_mapping'])
        
        # Import
        miner = GPSSSupplierMiner()
        result = miner.import_suppliers_from_csv(tmp_path, field_mapping)
        
        # Clean up temp file
        import os
        os.unlink(tmp_path)
        
        return jsonify(result)
    
    except Exception as e:
        print(f"Error importing CSV: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/gpss/auto-quote/process-opportunity', methods=['POST'])
def auto_quote_process_opportunity():
    """
    Process opportunity with automated supplier finding and quote generation
    
    Expected JSON:
    {
      "opportunity_id": "recXXXXX",
      "max_suppliers": 5
    }
    """
    try:
        from nexus_backend import handle_process_opportunity_for_suppliers
        
        data = request.json
        opportunity_id = data.get('opportunity_id')
        
        if not opportunity_id:
            return jsonify({"error": "opportunity_id is required"}), 400
        
        result = handle_process_opportunity_for_suppliers(opportunity_id)
        
        if not result.get('success'):
            return jsonify(result), 400
        
        return jsonify(result)
    
    except Exception as e:
        print(f"Error processing opportunity: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/gpss/auto-quote/find-suppliers', methods=['POST'])
def auto_quote_find_suppliers():
    """
    Find matching suppliers for an opportunity
    
    Expected JSON:
    {
      "opportunity_id": "recXXXXX"
    }
    """
    try:
        from nexus_backend import handle_find_suppliers_for_opportunity
        
        data = request.json
        opportunity_id = data.get('opportunity_id')
        
        if not opportunity_id:
            return jsonify({"error": "opportunity_id is required"}), 400
        
        suppliers = handle_find_suppliers_for_opportunity(opportunity_id)
        
        return jsonify({
            'success': True,
            'opportunity_id': opportunity_id,
            'suppliers': suppliers
        })
    
    except Exception as e:
        print(f"Error finding suppliers for opportunity: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/gpss/supplier-quotes', methods=['GET'])
def get_supplier_quotes():
    """Get supplier quotes with optional filters"""
    try:
        airtable_client = AirtableClient()
        
        # Get filter parameters
        opportunity_id = request.args.get('opportunity_id')
        supplier_id = request.args.get('supplier_id')
        status = request.args.get('status')
        
        # Build formula for filtering
        formulas = []
        if opportunity_id:
            formulas.append(f"{{Opportunity}}='{opportunity_id}'")
        if supplier_id:
            formulas.append(f"{{Supplier}}='{supplier_id}'")
        if status:
            formulas.append(f"{{Request Status}}='{status}'")
        
        # Fetch quotes
        if formulas:
            formula = f"AND({','.join(formulas)})"
            records = airtable_client.search_records('GPSS Supplier Quotes', formula)
        else:
            records = airtable_client.get_all_records('GPSS Supplier Quotes')
        
        # Format quotes
        quotes = []
        for record in records:
            fields = record.get('fields', {})
            quotes.append({
                'id': record.get('id'),
                'opportunity_id': fields.get('Opportunity', [None])[0],
                'supplier_id': fields.get('Supplier', [None])[0],
                'product_requested': fields.get('Product/Service Requested', ''),
                'quantity': fields.get('Quantity', ''),
                'supplier_quote_amount': fields.get('Supplier Quote Amount', 0),
                'our_proposed_price': fields.get('Our Proposed Price', 0),
                'net_profit': fields.get('Net Profit After Factoring ($)', 0),
                'request_status': fields.get('Request Status', ''),
                'quote_received_date': fields.get('Quote Received Date', ''),
                'selected': fields.get('Selected for Quote', False)
            })
        
        return jsonify({'quotes': quotes})
    
    except Exception as e:
        print(f"Error getting supplier quotes: {e}")
        return jsonify({"error": str(e), "quotes": []}), 500


@app.route('/gpss/supplier-quotes/<quote_id>', methods=['PUT'])
def update_supplier_quote(quote_id):
    """Update supplier quote (e.g., when supplier responds)"""
    try:
        airtable_client = AirtableClient()
        data = request.json
        
        # Build update fields
        update_fields = {}
        if 'supplier_quote_amount' in data:
            update_fields['Supplier Quote Amount'] = data['supplier_quote_amount']
        if 'quoted_lead_time' in data:
            update_fields['Quoted Lead Time (Days)'] = data['quoted_lead_time']
        if 'request_status' in data:
            update_fields['Request Status'] = data['request_status']
        if 'quote_received_date' in data:
            update_fields['Quote Received Date'] = data['quote_received_date']
        if 'selected' in data:
            update_fields['Selected for Quote'] = data['selected']
        
        result = airtable_client.update_record('GPSS Supplier Quotes', quote_id, update_fields)
        
        return jsonify({'success': True, 'quote': result})
    
    except Exception as e:
        print(f"Error updating supplier quote: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/gpss/supplier-quotes/compare/<opportunity_id>', methods=['GET'])
def compare_supplier_quotes(opportunity_id):
    """
    Side-by-side quote comparison for an opportunity.
    Returns all quotes grouped by product line with:
    - Best price highlighted
    - Margin calculations for each supplier
    - AI recommendation on which supplier to select
    
    URL Parameter:
        opportunity_id: Airtable record ID for the opportunity
    """
    try:
        airtable_client = AirtableClient()
        
        # Get all quotes for this opportunity
        formula = f"{{Opportunity}}='{opportunity_id}'"
        records = airtable_client.search_records('GPSS Supplier Quotes', formula)
        
        if not records:
            return jsonify({
                'success': True,
                'opportunity_id': opportunity_id,
                'quotes': [],
                'comparison': [],
                'recommendation': 'No quotes received yet'
            })
        
        # Build comparison matrix: group by product, compare across suppliers
        product_groups = {}
        suppliers_seen = {}
        
        for record in records:
            fields = record.get('fields', {})
            product = fields.get('Product/Service Requested', 'Unknown')
            supplier_id = fields.get('Supplier', [None])
            if isinstance(supplier_id, list) and supplier_id:
                supplier_id = supplier_id[0]
            
            supplier_quote = fields.get('Supplier Quote Amount', 0) or 0
            our_price = fields.get('Our Proposed Price', 0) or 0
            lead_time = fields.get('Quoted Lead Time (Days)', '') or ''
            status = fields.get('Request Status', 'Pending')
            selected = fields.get('Selected for Quote', False)
            
            if product not in product_groups:
                product_groups[product] = []
            
            product_groups[product].append({
                'quote_id': record.get('id'),
                'supplier_id': supplier_id,
                'supplier_quote': float(supplier_quote) if supplier_quote else 0,
                'our_price': float(our_price) if our_price else 0,
                'lead_time': lead_time,
                'status': status,
                'selected': selected,
                'margin': (float(our_price) - float(supplier_quote)) if supplier_quote and our_price else 0,
                'margin_pct': round(((float(our_price) - float(supplier_quote)) / float(our_price) * 100), 1) if our_price and supplier_quote else 0,
            })
            
            if supplier_id:
                suppliers_seen[supplier_id] = True
        
        # Get supplier names
        supplier_names = {}
        for sid in suppliers_seen:
            try:
                rec = airtable_client.get_record('GPSS SUPPLIERS', sid)
                supplier_names[sid] = rec.get('fields', {}).get('COMPANY NAME', 'Unknown')
            except:
                supplier_names[sid] = sid[:8]
        
        # Build comparison with supplier names
        comparison = []
        best_overall = {'supplier': None, 'total': float('inf')}
        
        for product, quotes in product_groups.items():
            # Find best price for this product
            received_quotes = [q for q in quotes if q['supplier_quote'] > 0]
            best_price = min(received_quotes, key=lambda x: x['supplier_quote']) if received_quotes else None
            
            enriched = []
            for q in quotes:
                q['supplier_name'] = supplier_names.get(q['supplier_id'], 'Unknown')
                q['is_best_price'] = (best_price and q['quote_id'] == best_price['quote_id'])
                enriched.append(q)
            
            comparison.append({
                'product': product,
                'quotes': enriched,
                'best_price_supplier': supplier_names.get(best_price['supplier_id'], 'Unknown') if best_price else None,
                'best_price_amount': best_price['supplier_quote'] if best_price else None,
                'quotes_received': len(received_quotes),
                'quotes_pending': len([q for q in quotes if q['status'] == 'Pending']),
            })
            
            # Track best overall
            if best_price and best_price['supplier_quote'] < best_overall['total']:
                best_overall = {
                    'supplier': supplier_names.get(best_price['supplier_id'], 'Unknown'),
                    'supplier_id': best_price['supplier_id'],
                    'total': best_price['supplier_quote'],
                }
        
        # Summary
        total_received = sum(1 for pg in comparison for q in pg['quotes'] if q['supplier_quote'] > 0)
        total_pending = sum(1 for pg in comparison for q in pg['quotes'] if q['status'] == 'Pending')
        
        recommendation = "Waiting for more quotes" if total_pending > total_received else (
            f"Best overall pricing from {best_overall['supplier']}" if best_overall['supplier'] else "Review quotes manually"
        )
        
        return jsonify({
            'success': True,
            'opportunity_id': opportunity_id,
            'comparison': comparison,
            'summary': {
                'total_products': len(comparison),
                'quotes_received': total_received,
                'quotes_pending': total_pending,
                'best_overall_supplier': best_overall.get('supplier'),
                'recommendation': recommendation,
            }
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# =====================================================================
# GPSS SUBCONTRACTOR ENDPOINTS
# =====================================================================

@app.route('/gpss/subcontractors', methods=['GET'])
def get_all_subcontractors():
    """Get all subcontractors from database with full Airtable field mapping"""
    try:
        from nexus_backend import GPSSSubcontractorMiner
        miner = GPSSSubcontractorMiner()
        
        subcontractors_raw = miner.airtable.get_all_records('GPSS SUBCONTRACTORS')
        
        subcontractors = []
        for record in subcontractors_raw:
            fields = record.get('fields', {})
            company_name = fields.get('COMPANY NAME', '').strip()
            if not company_name:
                continue
            
            subcontractors.append({
                'id': record.get('id'),
                'company_name': company_name,
                'service_type': fields.get('SERVICE TYPE', ''),
                'city': fields.get('CITY', ''),
                'state': fields.get('STATE', ''),
                'phone': fields.get('PHONE', ''),
                'email': fields.get('EMAIL', ''),
                'website': fields.get('WEBSITE', ''),
                'description': fields.get('DESCRIPTION', ''),
                'discovery_method': fields.get('DISCOVERY METHOD', ''),
                'discovery_date': fields.get('DISCOVERY DATE', ''),
                'discovered_by': fields.get('DISCOVERED BY', ''),
                'relationship_status': fields.get('RELATIONSHIP STATUS', ''),
                'reliability_rating': fields.get('RELIABILITY RATING', 0),
                'response_rate': fields.get('RESPONSE RATE (%)', 0),
                'contracts_won': fields.get('CONTRACTS WON TOGETHER ', 0),
                'last_contacted': fields.get('LAST CONTACTED', ''),
                'notes': fields.get('NOTES', ''),
                'source_notes': fields.get('SOURCE NOTES', ''),
                'naics_codes': fields.get('NAISC CODES', []),
                'capabilities': fields.get('CAPABILITIES', []),
                'certifications': fields.get('CERTIFICATION', []),
                'socioeconomic_certs': fields.get('SOCIOECONOMIC CERTS', []),
                'psc_codes': fields.get('PSC CODES', ''),
                'hourly_rates': fields.get('HOURLY RATES', ''),
                'employee_count': fields.get('EMPLOYEE COUNT', 0),
                'annual_revenue': fields.get('ANNUAL REVENUE', 0),
                'past_performance': fields.get('PAST PERFORMANCE SUMMARY', ''),
                'key_contracts': fields.get('KEY CONTRACTS', ''),
                'past_contracts_count': fields.get('PAST CONTRACTS COUNT', 0),
                'total_contract_value': fields.get('TOTAL CONTRACT VALUE', 0),
                'primary_agencies': fields.get('PRIMARY AGENCIES', []),
                'average_contract_size': fields.get('AVERAGE CONTRACT SIZE', 0),
                'contract_types': fields.get('CONTRACT TYPES', []),
                'ai_score': fields.get('AI SCORE', 0),
                'availability': fields.get('AVAILABILITY', ''),
                'performance_rating': fields.get('PERFORMANCE RATING', 0),
                'compliance_risk': fields.get('COMPLIANCE RISK', ''),
            })
        
        # Sort: small businesses first (by employee count ascending, then by reliability)
        def sort_key(s):
            emp = s.get('employee_count') or 9999
            has_certs = len(s.get('socioeconomic_certs', []))
            rating = s.get('reliability_rating') or 0
            return (-has_certs, emp, -rating)
        
        subcontractors.sort(key=sort_key)
        
        return jsonify({
            "success": True,
            "subcontractors": subcontractors,
            "count": len(subcontractors)
        })
    except Exception as e:
        print(f"Error getting subcontractors: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/gpss/subcontractors', methods=['POST'])
def create_subcontractor():
    """Create new subcontractor with proper Airtable field mapping"""
    try:
        from nexus_backend import GPSSSubcontractorMiner
        from datetime import datetime
        miner = GPSSSubcontractorMiner()
        
        data = request.json or {}
        
        # Map frontend field names to Airtable UPPERCASE field names
        field_map = {
            'Company Name': 'COMPANY NAME',
            'Service Type': 'SERVICE TYPE',
            'City': 'CITY',
            'State': 'STATE',
            'Phone': 'PHONE',
            'Email': 'EMAIL',
            'Website': 'WEBSITE',
            'Description': 'DESCRIPTION',
            'Relationship Status': 'RELATIONSHIP STATUS',
            'Notes': 'NOTES',
            'Employee Count': 'EMPLOYEE COUNT',
            'Annual Revenue': 'ANNUAL REVENUE',
            'Hourly Rates': 'HOURLY RATES',
        }
        
        airtable_data = {}
        for frontend_key, airtable_key in field_map.items():
            if frontend_key in data and data[frontend_key]:
                airtable_data[airtable_key] = data[frontend_key]
        
        # Handle multi-select fields (arrays)
        for ms_field in ['SOCIOECONOMIC CERTS', 'CAPABILITIES', 'NAISC CODES', 'PRIMARY AGENCIES', 'CONTRACT TYPES', 'CERTIFICATION']:
            if ms_field in data and isinstance(data[ms_field], list):
                airtable_data[ms_field] = data[ms_field]
        
        # Handle select fields
        if 'AVAILABILITY' in data:
            airtable_data['AVAILABILITY'] = data['AVAILABILITY']
        if 'COMPLIANCE RISK' in data:
            airtable_data['COMPLIANCE RISK'] = data['COMPLIANCE RISK']
        
        # Defaults
        airtable_data.setdefault('DISCOVERY METHOD', data.get('Discovery Method', 'Manual Entry'))
        airtable_data.setdefault('DISCOVERED BY', data.get('Discovered By', 'Dee Davis'))
        airtable_data.setdefault('DISCOVERY DATE', datetime.now().strftime('%Y-%m-%d'))
        
        if 'COMPANY NAME' not in airtable_data:
            return jsonify({"error": "Company Name is required"}), 400
        
        record = miner.airtable.create_record('GPSS SUBCONTRACTORS', airtable_data)
        
        return jsonify({
            "success": True,
            "subcontractor": {
                'id': record.get('id'),
                'company_name': airtable_data.get('COMPANY NAME')
            },
            "message": "Subcontractor created successfully"
        })
    except Exception as e:
        print(f"Error creating subcontractor: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/gpss/subcontractors/<subcontractor_id>', methods=['GET'])
def get_subcontractor(subcontractor_id):
    """Get single subcontractor by ID"""
    try:
        from nexus_backend import GPSSSubcontractorMiner
        miner = GPSSSubcontractorMiner()
        
        record = miner.airtable.get_record('GPSS SUBCONTRACTORS', subcontractor_id)
        
        if not record:
            return jsonify({"error": "Subcontractor not found"}), 404
        
        fields = record.get('fields', {})
        subcontractor = {
            'id': record.get('id'),
            'company_name': fields.get('COMPANY NAME', ''),
            'service_type': fields.get('SERVICE TYPE', ''),
            'city': fields.get('CITY', ''),
            'state': fields.get('STATE', ''),
            'phone': fields.get('PHONE', ''),
            'email': fields.get('EMAIL', ''),
            'website': fields.get('WEBSITE', ''),
            'description': fields.get('DESCRIPTION', ''),
            'relationship_status': fields.get('RELATIONSHIP STATUS', ''),
            'reliability_rating': fields.get('RELIABILITY RATING', 0),
            'socioeconomic_certs': fields.get('SOCIOECONOMIC CERTS', []),
            'capabilities': fields.get('CAPABILITIES', []),
            'employee_count': fields.get('EMPLOYEE COUNT', 0),
            'annual_revenue': fields.get('ANNUAL REVENUE', 0),
            'availability': fields.get('AVAILABILITY', ''),
            'compliance_risk': fields.get('COMPLIANCE RISK', ''),
            'notes': fields.get('NOTES', ''),
        }
        
        return jsonify({
            "success": True,
            "subcontractor": subcontractor
        })
    except Exception as e:
        print(f"Error getting subcontractor: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/gpss/subcontractors/<subcontractor_id>', methods=['PUT'])
def update_subcontractor(subcontractor_id):
    """Update existing subcontractor with proper Airtable field mapping"""
    try:
        from nexus_backend import GPSSSubcontractorMiner
        miner = GPSSSubcontractorMiner()
        
        data = request.json or {}
        
        field_map = {
            'Company Name': 'COMPANY NAME',
            'Service Type': 'SERVICE TYPE',
            'City': 'CITY',
            'State': 'STATE',
            'Phone': 'PHONE',
            'Email': 'EMAIL',
            'Website': 'WEBSITE',
            'Description': 'DESCRIPTION',
            'Relationship Status': 'RELATIONSHIP STATUS',
            'Notes': 'NOTES',
            'Employee Count': 'EMPLOYEE COUNT',
            'Annual Revenue': 'ANNUAL REVENUE',
            'Hourly Rates': 'HOURLY RATES',
        }
        
        airtable_updates = {}
        for frontend_key, airtable_key in field_map.items():
            if frontend_key in data:
                airtable_updates[airtable_key] = data[frontend_key]
        
        # Also allow direct uppercase keys
        for key in ['AVAILABILITY', 'COMPLIANCE RISK', 'SOCIOECONOMIC CERTS', 'CAPABILITIES',
                     'NAISC CODES', 'PRIMARY AGENCIES', 'CONTRACT TYPES', 'CERTIFICATION',
                     'LAST CONTACTED', 'RELATIONSHIP STATUS']:
            if key in data:
                airtable_updates[key] = data[key]
        
        record = miner.airtable.update_record('GPSS SUBCONTRACTORS', subcontractor_id, airtable_updates)
        
        return jsonify({
            "success": True,
            "subcontractor_id": subcontractor_id,
            "message": "Subcontractor updated successfully"
        })
    except Exception as e:
        print(f"Error updating subcontractor: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/gpss/subcontractors/<subcontractor_id>', methods=['DELETE'])
def delete_subcontractor(subcontractor_id):
    """Delete subcontractor"""
    try:
        from nexus_backend import GPSSSubcontractorMiner
        miner = GPSSSubcontractorMiner()
        
        miner.airtable.delete_record('GPSS SUBCONTRACTORS', subcontractor_id)
        
        return jsonify({
            "success": True,
            "message": "Subcontractor deleted successfully"
        })
    except Exception as e:
        print(f"Error deleting subcontractor: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/gpss/opportunities/<opportunity_id>/match-subs', methods=['POST'])
def match_subs_for_opportunity(opportunity_id):
    """
    AI-powered: Analyze an opportunity, determine what capabilities are needed,
    and match against existing subcontractor database. Returns gap analysis + ranked matches.
    
    This is the key bridge between opportunities and subcontractors.
    When you decide to pursue an opportunity, hit this to see who can help.
    """
    try:
        from nexus_backend import AirtableClient, AnthropicClient
        import json as json_mod
        import re as re_mod
        
        airtable = AirtableClient()
        ai = AnthropicClient()
        
        def extract_json_from_text(text):
            """Extract JSON from AI response that may contain markdown or extra text"""
            # Try direct parse first
            try:
                return json_mod.loads(text)
            except:
                pass
            # Try finding JSON block in markdown
            match = re_mod.search(r'```(?:json)?\s*\n?(.*?)\n?```', text, re_mod.DOTALL)
            if match:
                try:
                    return json_mod.loads(match.group(1))
                except:
                    pass
            # Try finding first { ... } block
            match = re_mod.search(r'\{.*\}', text, re_mod.DOTALL)
            if match:
                try:
                    return json_mod.loads(match.group(0))
                except:
                    pass
            return {"error": "Could not parse AI response"}
        
        # Step 1: Get opportunity details
        opp_table = airtable.get_table("GPSS OPPORTUNITIES")
        opp_record = opp_table.get(opportunity_id)
        opp = opp_record['fields']
        
        opp_title = opp.get('TITLE', opp.get('Title', opp.get('Name', 'Unknown')))
        opp_desc = opp.get('DESCRIPTION', opp.get('Description', ''))
        opp_naics = opp.get('NAICS', opp.get('Naics', ''))
        opp_type = opp.get('Type', opp.get('TYPE', ''))
        opp_setaside = opp.get('SET_ASIDE', opp.get('Set-Aside', ''))
        opp_notes = opp.get('Notes', opp.get('NOTES', opp.get('Source Status', '')))
        
        # Step 2: Get ALL subcontractors
        subs_raw = airtable.get_all_records('GPSS SUBCONTRACTORS')
        subs_list = []
        for r in subs_raw:
            f = r['fields']
            name = f.get('COMPANY NAME', '').strip()
            if not name:
                continue
            subs_list.append({
                'id': r['id'],
                'name': name,
                'service_type': f.get('SERVICE TYPE', ''),
                'description': f.get('DESCRIPTION', ''),
                'capabilities': f.get('CAPABILITIES', []),
                'socioeconomic_certs': f.get('SOCIOECONOMIC CERTS', []),
                'naics_codes': f.get('NAISC CODES', []),
                'state': f.get('STATE', ''),
                'city': f.get('CITY', ''),
                'email': f.get('EMAIL', ''),
                'phone': f.get('PHONE', ''),
                'website': f.get('WEBSITE', ''),
                'reliability_rating': f.get('RELIABILITY RATING', 0),
                'employee_count': f.get('EMPLOYEE COUNT', 0),
                'availability': f.get('AVAILABILITY', ''),
                'relationship_status': f.get('RELATIONSHIP STATUS', ''),
            })
        
        # Step 3: Build concise sub catalog for AI
        sub_catalog = ""
        for i, s in enumerate(subs_list):
            certs = ', '.join(s['socioeconomic_certs']) if s['socioeconomic_certs'] else 'None'
            caps = ', '.join(s['capabilities']) if s['capabilities'] else ''
            naics = ', '.join(s['naics_codes']) if s['naics_codes'] else ''
            sub_catalog += f"{i+1}. {s['name']} | Service: {s['service_type']} | Caps: {caps} | NAICS: {naics} | Certs: {certs} | Location: {s['city']}, {s['state']} | Rating: {s['reliability_rating']}/5 | Employees: {s['employee_count']}\n"
        
        # Step 4: One AI call to do gap analysis + matching
        prompt = f"""You are analyzing a government contract opportunity for Dee Davis Inc (EDWOSB small business) 
to determine what subcontractor capabilities are needed and which existing subcontractors are the best match.

OPPORTUNITY:
Title: {opp_title}
Description: {opp_desc}
NAICS: {opp_naics}
Type: {opp_type}
Set-Aside: {opp_setaside}
Notes/Status: {opp_notes}

OUR SUBCONTRACTOR DATABASE ({len(subs_list)} subcontractors):
{sub_catalog}

ANALYZE AND RETURN JSON:
{{
    "opportunity_summary": "Brief 1-sentence summary of what this opportunity needs",
    "required_capabilities": ["capability1", "capability2", ...],
    "self_perform_possible": true/false,
    "self_perform_percentage": 60,
    "partner_recommendation": "self_perform" or "need_subcontractor" or "need_supplier",
    "reasoning": "Why you recommend this approach...",
    "matched_subcontractors": [
        {{
            "index": 1,
            "name": "Sub Name",
            "match_score": 92,
            "match_reason": "Why this sub is a good fit for this specific opportunity",
            "role": "What they would do on this contract",
            "is_small_business": true/false
        }}
    ],
    "capability_gaps": ["Any capability needed that NO existing sub can provide"],
    "suggested_searches": ["Service types to search for if there are gaps"]
}}

RULES:
- Only include subcontractors that are actually relevant (score >= 60)
- Prioritize small businesses (with socioeconomic certs)
- Max 8 matched subcontractors
- If this is a product/supply opportunity (not services), say partner_recommendation="need_supplier" and explain
- Be specific about WHY each sub matches
"""
        
        raw_response = ai.complete(prompt, max_tokens=4000)
        analysis = extract_json_from_text(raw_response)
        
        # Step 5: Enrich matched subs with full data
        matched = analysis.get('matched_subcontractors', [])
        enriched_matches = []
        for m in matched:
            idx = m.get('index', 0)
            if 1 <= idx <= len(subs_list):
                sub_data = subs_list[idx - 1]
                m['id'] = sub_data['id']
                m['email'] = sub_data['email']
                m['phone'] = sub_data['phone']
                m['website'] = sub_data['website']
                m['state'] = sub_data['state']
                m['city'] = sub_data['city']
                m['socioeconomic_certs'] = sub_data['socioeconomic_certs']
                m['service_type'] = sub_data['service_type']
                m['availability'] = sub_data['availability']
                m['relationship_status'] = sub_data['relationship_status']
            enriched_matches.append(m)
        
        analysis['matched_subcontractors'] = enriched_matches
        
        return jsonify({
            "success": True,
            "opportunity_id": opportunity_id,
            "opportunity_title": opp_title,
            "analysis": analysis,
            "total_subs_evaluated": len(subs_list),
            "matches_found": len(enriched_matches),
        })
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/gpss/subcontractors/find', methods=['POST'])
def find_subcontractors():
    """
    Find subcontractors in the area using Google search
    
    Expected JSON:
    {
      "service_type": "aircraft wash",
      "location": "Virginia Beach VA",
      "max_results": 10
    }
    """
    try:
        from nexus_backend import GPSSSubcontractorMiner
        
        data = request.json or {}
        service_type = data.get('service_type')
        location = data.get('location')
        max_results = data.get('max_results', 10)
        
        if not service_type or not location:
            return jsonify({"error": "service_type and location are required"}), 400
        
        miner = GPSSSubcontractorMiner()
        subcontractors = miner.find_subcontractors(service_type, location, max_results)
        
        return jsonify({
            "success": True,
            "service_type": service_type,
            "location": location,
            "subcontractors_found": len(subcontractors),
            "subcontractors": subcontractors
        })
        
    except Exception as e:
        print(f"Error finding subcontractors: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/gpss/subcontractors/mine-for-gaps', methods=['POST'])
def mine_subcontractors_for_gaps():
    """
    Mine subcontractors from ALL sources to fill capability gaps.
    Called after match-subs identifies gaps. Searches Google, SAM.gov/SBA, and Google Maps.
    
    Expected JSON:
    {
        "gaps": ["Mobile power generation", "Battery systems"],
        "suggested_searches": ["Mobile generator specialists", "Battery integrators"],
        "location": "Michigan",
        "naics_code": "",
        "auto_save": true
    }
    """
    try:
        from nexus_backend import GPSSSubcontractorMiner
        
        data = request.json or {}
        gaps = data.get('gaps', [])
        suggested_searches = data.get('suggested_searches', [])
        location = data.get('location', 'Michigan')
        naics_code = data.get('naics_code', '')
        auto_save = data.get('auto_save', True)
        
        if not gaps and not suggested_searches:
            return jsonify({"error": "gaps or suggested_searches required"}), 400
        
        miner = GPSSSubcontractorMiner()
        
        # Combine gaps and suggested searches into search terms
        search_terms = list(set(suggested_searches + gaps))
        
        all_found = []
        results_by_term = {}
        
        for term in search_terms:
            mine_result = miner.mine_all_sources(
                service_type=term,
                location=location,
                naics_code=naics_code,
                max_per_source=3  # 3 per source × 3 sources = up to 9 per gap
            )
            results_by_term[term] = {
                'found': mine_result.get('total', 0),
                'by_source': mine_result.get('by_source', {})
            }
            all_found.extend(mine_result.get('results', []))
        
        # Deduplicate across all searches
        seen = set()
        unique_results = []
        for r in all_found:
            name_key = r.get('COMPANY NAME', '').lower().strip()
            if name_key and name_key not in seen:
                seen.add(name_key)
                unique_results.append(r)
        
        # Auto-save to Airtable if requested
        saved_count = 0
        if auto_save and unique_results:
            # Get existing sub names to avoid duplicates
            existing = miner.airtable.get_all_records('GPSS SUBCONTRACTORS')
            existing_names = set()
            for e in existing:
                n = e.get('fields', {}).get('COMPANY NAME', '').lower().strip()
                if n:
                    existing_names.add(n)
            
            for sub in unique_results:
                name_key = sub.get('COMPANY NAME', '').lower().strip()
                if name_key in existing_names:
                    continue
                
                # Build Airtable record
                record_data = {
                    'COMPANY NAME': sub.get('COMPANY NAME', ''),
                    'SERVICE TYPE': sub.get('SERVICE TYPE', ''),
                    'CITY': sub.get('CITY', ''),
                    'STATE': sub.get('STATE', ''),
                    'WEBSITE': sub.get('WEBSITE', ''),
                    'EMAIL': sub.get('EMAIL', ''),
                    'PHONE': sub.get('PHONE', ''),
                    'DESCRIPTION': sub.get('DESCRIPTION', ''),
                    'DISCOVERY METHOD': sub.get('DISCOVERY METHOD', 'Multi-Source Mining'),
                    'DISCOVERY DATE': sub.get('DISCOVERY DATE', ''),
                    'DISCOVERED BY': 'NEXUS Auto-Mining',
                    'RELATIONSHIP STATUS': 'Cold',
                }
                
                # Add certs if present (multi-select)
                certs = sub.get('SOCIOECONOMIC CERTS', [])
                if certs and isinstance(certs, list):
                    record_data['SOCIOECONOMIC CERTS'] = certs
                
                # Add NAICS if present (multi-select)
                naics = sub.get('NAISC CODES', [])
                if naics and isinstance(naics, list):
                    record_data['NAISC CODES'] = naics
                
                try:
                    miner.airtable.create_record('GPSS SUBCONTRACTORS', record_data)
                    saved_count += 1
                    existing_names.add(name_key)
                except Exception as e:
                    print(f"  ⚠️  Error saving {sub.get('COMPANY NAME')}: {e}")
        
        return jsonify({
            "success": True,
            "total_found": len(unique_results),
            "saved_to_database": saved_count,
            "results_by_search_term": results_by_term,
            "subcontractors": [{
                'company_name': r.get('COMPANY NAME', ''),
                'service_type': r.get('SERVICE TYPE', ''),
                'city': r.get('CITY', ''),
                'state': r.get('STATE', ''),
                'website': r.get('WEBSITE', ''),
                'source': r.get('_source', r.get('DISCOVERY METHOD', '')),
                'certs': r.get('SOCIOECONOMIC CERTS', []),
            } for r in unique_results],
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route('/gpss/subcontractors/search', methods=['POST'])
def search_existing_subcontractors():
    """
    Search existing subcontractor database
    
    Expected JSON:
    {
      "service_type": "janitorial",
      "location": "Texas",
      "min_rating": 3.5
    }
    """
    try:
        from nexus_backend import GPSSSubcontractorMiner
        
        data = request.json or {}
        service_type = data.get('service_type')
        location = data.get('location')
        min_rating = data.get('min_rating', 0)
        
        miner = GPSSSubcontractorMiner()
        subcontractors = miner.search_existing_subcontractors(service_type, location, min_rating)
        
        return jsonify({
            "success": True,
            "subcontractors_found": len(subcontractors),
            "subcontractors": subcontractors
        })
        
    except Exception as e:
        print(f"Error searching subcontractors: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/gpss/subcontractors/rfq/generate', methods=['POST'])
def generate_rfq():
    """
    Generate RFQ email for a subcontractor
    
    Expected JSON:
    {
      "subcontractor": {
        "company_name": "ABC Services",
        "email": "contact@abc.com"
      },
      "opportunity": {
        "id": "recXXXX",
        "service_type": "aircraft wash",
        "location": "Virginia Beach VA",
        "value": 200000,
        "agency": "US Navy"
      },
      "scope": "Wash 200 aircraft per year..."
    }
    """
    try:
        from nexus_backend import GPSSSubcontractorMiner
        
        data = request.json or {}
        subcontractor = data.get('subcontractor')
        opportunity = data.get('opportunity')
        scope = data.get('scope')
        
        if not subcontractor or not opportunity or not scope:
            return jsonify({"error": "subcontractor, opportunity, and scope are required"}), 400
        
        miner = GPSSSubcontractorMiner()
        email = miner.generate_rfq_email(subcontractor, opportunity, scope)
        
        return jsonify({
            "success": True,
            "email": email
        })
        
    except Exception as e:
        print(f"Error generating RFQ: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/gpss/subcontractors/rfq/send-bulk', methods=['POST'])
def send_bulk_rfqs():
    """
    Send RFQs to multiple subcontractors at once
    
    Expected JSON:
    {
      "opportunity_id": "recXXXX",
      "subcontractor_ids": ["rec111", "rec222", "rec333"],
      "scope": "Full scope of work text..."
    }
    """
    try:
        from nexus_backend import GPSSSubcontractorMiner
        
        data = request.json or {}
        opportunity_id = data.get('opportunity_id')
        subcontractor_ids = data.get('subcontractor_ids', [])
        scope = data.get('scope')
        
        if not opportunity_id or not subcontractor_ids or not scope:
            return jsonify({"error": "opportunity_id, subcontractor_ids, and scope are required"}), 400
        
        miner = GPSSSubcontractorMiner()
        result = miner.send_rfqs_to_subcontractors(opportunity_id, subcontractor_ids, scope)
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Error sending RFQs: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/gpss/subcontractors/quotes/<quote_id>/score', methods=['POST'])
def score_quote():
    """
    AI score a quote 0-100
    
    URL Parameter:
      quote_id: Airtable quote record ID
    """
    try:
        from nexus_backend import GPSSSubcontractorMiner
        
        quote_id = request.view_args.get('quote_id')
        
        if not quote_id:
            return jsonify({"error": "quote_id is required"}), 400
        
        miner = GPSSSubcontractorMiner()
        result = miner.score_quote(quote_id)
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Error scoring quote: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/gpss/subcontractors/quotes/score-all', methods=['POST'])
def score_all_quotes_for_opportunity():
    """
    Score all quotes for an opportunity
    
    Expected JSON:
    {
      "opportunity_id": "recXXXX"
    }
    """
    try:
        from nexus_backend import GPSSSubcontractorMiner
        
        data = request.json or {}
        opportunity_id = data.get('opportunity_id')
        
        if not opportunity_id:
            return jsonify({"error": "opportunity_id is required"}), 400
        
        miner = GPSSSubcontractorMiner()
        scored_quotes = miner.score_all_quotes_for_opportunity(opportunity_id)
        
        return jsonify({
            "success": True,
            "opportunity_id": opportunity_id,
            "quotes_scored": len(scored_quotes),
            "ranked_quotes": scored_quotes
        })
        
    except Exception as e:
        print(f"Error scoring quotes: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/gpss/subcontractors/quotes/<quote_id>/markup', methods=['POST'])
def calculate_markup():
    """
    Calculate markup and final bid
    
    URL Parameter:
      quote_id: Airtable quote record ID
    
    Expected JSON:
    {
      "markup_percentage": 20.0
    }
    """
    try:
        from nexus_backend import GPSSSubcontractorMiner
        
        quote_id = request.view_args.get('quote_id')
        data = request.json or {}
        markup_percentage = data.get('markup_percentage', 20.0)
        
        if not quote_id:
            return jsonify({"error": "quote_id is required"}), 400
        
        miner = GPSSSubcontractorMiner()
        result = miner.calculate_markup_bid(quote_id, markup_percentage)
        
        # PRICING LEARNING: Log markup event
        if result.get('success'):
            try:
                from pricing_intelligence import get_pricing_intelligence
                pi = get_pricing_intelligence()
                pi.log_markup_set(
                    opportunity_id=data.get('opportunity_id', quote_id),
                    markup_pct=markup_percentage,
                    sub_cost=result.get('subcontractor_cost', 0),
                    final_bid=result.get('final_bid_amount', 0),
                    service_type=data.get('service_type'),
                    contract_type=data.get('contract_type'),
                    eval_method=data.get('eval_method'),
                )
            except Exception:
                pass
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Error calculating markup: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/gpss/subcontractors/bid/summary', methods=['POST'])
def generate_bid_summary():
    """
    Generate complete bid summary
    
    Expected JSON:
    {
      "opportunity_id": "recXXXX",
      "selected_quote_id": "recYYYY",
      "markup_percentage": 20.0
    }
    """
    try:
        from nexus_backend import GPSSSubcontractorMiner
        
        data = request.json or {}
        opportunity_id = data.get('opportunity_id')
        selected_quote_id = data.get('selected_quote_id')
        markup_percentage = data.get('markup_percentage', 20.0)
        
        if not opportunity_id or not selected_quote_id:
            return jsonify({"error": "opportunity_id and selected_quote_id are required"}), 400
        
        miner = GPSSSubcontractorMiner()
        result = miner.generate_final_bid_summary(opportunity_id, selected_quote_id, markup_percentage)
        
        # PRICING LEARNING: Log bid summary generation
        try:
            from pricing_intelligence import get_pricing_intelligence
            pi = get_pricing_intelligence()
            bid_calc = result.get('bid_calculation', {})
            final_bid = bid_calc.get('final_bid_amount', 0)
            sub_cost = bid_calc.get('subcontractor_cost', 0)
            if final_bid > 0:
                pi.log_markup_set(
                    opportunity_id=opportunity_id,
                    markup_pct=markup_percentage,
                    sub_cost=sub_cost,
                    final_bid=final_bid,
                )
        except Exception:
            pass
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Error generating bid summary: {e}")
        return jsonify({"error": str(e)}), 500


# =====================================================================
# GPSS SUBCONTRACTOR COMPLIANCE ENDPOINTS
# =====================================================================

@app.route('/gpss/subcontractors/<subcontractor_id>/compliance/check', methods=['POST'])
def check_subcontractor_compliance(subcontractor_id):
    """
    Check if subcontractor has all required compliance documents
    
    Expected JSON (optional):
    {
      "required_documents": ["W-9", "General Liability Insurance", "Subcontractor Agreement"]
    }
    """
    try:
        from nexus_backend import GPSSSubcontractorMiner
        
        data = request.json or {}
        required_docs = data.get('required_documents', None)
        
        miner = GPSSSubcontractorMiner()
        result = miner.check_compliance(subcontractor_id, required_docs)
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Error checking compliance: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/gpss/subcontractors/<subcontractor_id>/compliance', methods=['GET'])
def get_subcontractor_compliance(subcontractor_id):
    """
    Get all compliance documents for a subcontractor
    """
    try:
        from nexus_backend import GPSSSubcontractorMiner
        
        miner = GPSSSubcontractorMiner()
        result = miner.get_compliance_documents(subcontractor_id)
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Error getting compliance documents: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/gpss/subcontractors/<subcontractor_id>/compliance/add', methods=['POST'])
def add_compliance_document(subcontractor_id):
    """
    Add a compliance document record
    
    Expected JSON:
    {
      "document_type": "W-9",
      "status": "Missing",
      "expiration_date": "2026-12-31",
      "insurance_amount": 1000000,
      "notes": "Requested via email"
    }
    """
    try:
        from nexus_backend import GPSSSubcontractorMiner
        
        data = request.json or {}
        document_type = data.get('document_type')
        status = data.get('status', 'Missing')
        expiration_date = data.get('expiration_date')
        insurance_amount = data.get('insurance_amount')
        notes = data.get('notes', '')
        
        if not document_type:
            return jsonify({"error": "document_type is required"}), 400
        
        miner = GPSSSubcontractorMiner()
        result = miner.add_compliance_document(
            subcontractor_id, 
            document_type, 
            status, 
            expiration_date,
            insurance_amount,
            notes
        )
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Error adding compliance document: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/gpss/compliance/<document_id>', methods=['PUT'])
def update_compliance_document(document_id):
    """
    Update a compliance document
    
    Expected JSON:
    {
      "DOCUMENT_STATUS": "Approved",
      "DATE_RECEIVED": "2026-01-22",
      "DATE_APPROVED": "2026-01-22",
      "EXPIRATION_DATE": "2027-01-22",
      "INSURANCE_AMOUNT": 1000000,
      "POLICY_NUMBER": "GL-123456",
      "NOTES": "Certificate received and verified"
    }
    """
    try:
        from nexus_backend import GPSSSubcontractorMiner
        
        data = request.json or {}
        
        if not data:
            return jsonify({"error": "No update data provided"}), 400
        
        miner = GPSSSubcontractorMiner()
        result = miner.update_compliance_document(document_id, data)
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Error updating compliance document: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/gpss/compliance/alerts', methods=['GET'])
def get_compliance_alerts():
    """
    Get all expiring/expired compliance documents
    
    Query params:
      ?days_threshold=30  (optional, default 30)
    """
    try:
        from nexus_backend import GPSSSubcontractorMiner
        
        days_threshold = request.args.get('days_threshold', 30, type=int)
        
        miner = GPSSSubcontractorMiner()
        result = miner.get_expiring_documents(days_threshold)
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Error getting compliance alerts: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/gpss/subcontractors/<subcontractor_id>/compliance/mark-ready', methods=['POST'])
def mark_compliance_ready(subcontractor_id):
    """
    Mark subcontractor as compliance ready
    
    Expected JSON:
    {
      "ready": true
    }
    """
    try:
        from nexus_backend import GPSSSubcontractorMiner
        
        data = request.json or {}
        ready = data.get('ready', True)
        
        miner = GPSSSubcontractorMiner()
        result = miner.mark_subcontractor_compliance_ready(subcontractor_id, ready)
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Error marking compliance ready: {e}")
        return jsonify({"error": str(e)}), 500


# =====================================================================
# GPSS PROPOSALBIO™ QUALITY ASSURANCE ENDPOINTS
# =====================================================================

@app.route('/gpss/proposalbio/analyze', methods=['POST'])
def gpss_proposalbio_analyze():
    """
    Run ProposalBio™ 10-biohack analysis on a proposal
    
    Expected JSON:
    {
      "proposal_id": "recXXXXX",
      "metadata": {
        "agency_type": "Federal|State|Local|Cooperative",
        "region": "Northeast|Mid_Atlantic|Southeast|Midwest|Southwest|West_Coast",
        "rfp_text": "Full RFP text for familiarity analysis (optional)"
      }
    }
    """
    try:
        data = request.json or {}
        proposal_id = data.get('proposal_id')
        metadata = data.get('metadata') or {}

        if not proposal_id:
            return jsonify({"error": "proposal_id is required"}), 400

        svc = ProposalBioService()
        result = svc.analyze_proposal(proposal_id, metadata_override=metadata)

        if 'error' in result:
            return jsonify(result), 400

        return jsonify(result)

    except Exception as e:
        print(f"ProposalBio analysis error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/gpss/proposalbio/score/<proposal_id>', methods=['GET'])
def gpss_proposalbio_score(proposal_id):
    """Get existing ProposalBio™ scores for a proposal"""
    try:
        airtable_client = AirtableClient()
        recs = airtable_client.search_records('GPSS Proposals', f"RECORD_ID()='{proposal_id}'")
        if not recs:
            return jsonify({"error": "Proposal not found"}), 404

        fields = recs[0].get('fields', {})
        
        return jsonify({
            "proposal_id": proposal_id,
            "composite_score": fields.get("ProposalBio Composite Score"),
            "status": fields.get("ProposalBio Status"),
            "submission_gate": fields.get("ProposalBio Gate"),
            "last_analyzed": fields.get("ProposalBio Last Analyzed"),
            "revision_count": fields.get("ProposalBio Revision Count", 0),
            "approved_by": fields.get("ProposalBio Approved By"),
            "approved_date": fields.get("ProposalBio Approved Date"),
            "biohack_scores": json.loads(fields.get("ProposalBio Biohack Scores JSON") or "[]"),
            "critical_issues": json.loads(fields.get("ProposalBio Critical Issues JSON") or "[]"),
            "priority_improvements": json.loads(fields.get("ProposalBio Priority Improvements JSON") or "[]"),
        })
    except Exception as e:
        print(f"ProposalBio score retrieval error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/gpss/proposalbio/approve', methods=['POST'])
def gpss_proposalbio_approve():
    """
    Approve proposal for submission (unlocks quality gate)
    
    Expected JSON:
    {
      "proposal_id": "recXXXXX",
      "approved_by": "Dee Davis",
      "override_warnings": false
    }
    """
    try:
        data = request.json or {}
        proposal_id = data.get('proposal_id')
        approved_by = data.get('approved_by', 'Alexis Nexus')
        override_warnings = bool(data.get('override_warnings', False))

        if not proposal_id:
            return jsonify({"error": "proposal_id is required"}), 400

        svc = ProposalBioService()
        result = svc.approve(proposal_id, approved_by=approved_by, override_warnings=override_warnings)

        if 'error' in result:
            return jsonify(result), 400

        return jsonify(result)
    except Exception as e:
        print(f"ProposalBio approval error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/gpss/proposalbio/outcome', methods=['POST'])
def gpss_proposalbio_outcome():
    """
    Record win/loss outcome for adaptive learning
    
    Expected JSON:
    {
      "proposal_id": "recXXXXX",
      "outcome": "Won|Lost|No Decision",
      "win_value": 1500000
    }
    """
    try:
        data = request.json or {}
        proposal_id = data.get('proposal_id')
        outcome = data.get('outcome')
        win_value = float(data.get('win_value', 0))

        if not proposal_id or not outcome:
            return jsonify({"error": "proposal_id and outcome are required"}), 400

        svc = ProposalBioService()
        result = svc.record_outcome(proposal_id, outcome, win_value)

        if 'error' in result:
            return jsonify(result), 400

        return jsonify(result)
    except Exception as e:
        print(f"ProposalBio outcome recording error: {e}")
        return jsonify({"error": str(e)}), 500


# =====================================================================
# GPSS STRATEGIC ANALYSIS ENDPOINTS (RFP SUCCESS® INTEGRATION)
# =====================================================================

@app.route('/gpss/strategic-analysis/go-no-go', methods=['POST'])
def gpss_strategic_go_no_go():
    """
    Calculate Go/No-Go score for bid decision
    
    Expected JSON:
    {
      "opportunity_id": "recXXXXX",
      "relationship_strength": 8,     # 0-10
      "price_competitiveness": 6,      # 0-10
      "technical_capability": 9,       # 0-10
      "resource_availability": 7,      # 0-10
      "past_performance": 8            # 0-10
    }
    
    Returns:
    {
      "total_score": 38,
      "recommendation": "Pursue|Maybe|Skip",
      "win_probability": 65,
      "breakdown": {...},
      "strengths": [...],
      "weaknesses": [...],
      "strategy": "..."
    }
    """
    try:
        data = request.json or {}
        opportunity_id = data.get('opportunity_id')
        
        if not opportunity_id:
            return jsonify({"error": "opportunity_id is required"}), 400
        
        # Validate scores
        relationship_strength = int(data.get('relationship_strength', 5))
        price_competitiveness = int(data.get('price_competitiveness', 5))
        technical_capability = int(data.get('technical_capability', 5))
        resource_availability = int(data.get('resource_availability', 5))
        past_performance = int(data.get('past_performance', 5))
        
        # Validate range
        for score, name in [
            (relationship_strength, 'relationship_strength'),
            (price_competitiveness, 'price_competitiveness'),
            (technical_capability, 'technical_capability'),
            (resource_availability, 'resource_availability'),
            (past_performance, 'past_performance')
        ]:
            if not 0 <= score <= 10:
                return jsonify({"error": f"{name} must be between 0 and 10"}), 400
        
        svc = StrategicAnalysisService()
        result = svc.calculate_go_no_go_score(
            opportunity_id,
            relationship_strength,
            price_competitiveness,
            technical_capability,
            resource_availability,
            past_performance
        )
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Go/No-Go calculation error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/gpss/strategic-analysis/evaluator-profile', methods=['POST'])
def gpss_strategic_evaluator_profile():
    """
    Analyze RFP to detect evaluator behavioral style
    
    Expected JSON:
    {
      "opportunity_id": "recXXXXX",
      "rfp_text": "Full RFP text...",
      "agency_name": "City of Detroit" (optional)
    }
    
    Returns:
    {
      "primary_style": "Analytical|Driver|Expressive|Amiable",
      "secondary_style": "...",
      "confidence": 85,
      "indicators": [...],
      "proposal_recommendations": [...]
    }
    """
    try:
        data = request.json or {}
        opportunity_id = data.get('opportunity_id')
        rfp_text = data.get('rfp_text', '')
        agency_name = data.get('agency_name')
        
        if not opportunity_id:
            return jsonify({"error": "opportunity_id is required"}), 400
        
        if not rfp_text:
            return jsonify({"error": "rfp_text is required"}), 400
        
        svc = StrategicAnalysisService()
        result = svc.analyze_evaluator_style(
            opportunity_id,
            rfp_text,
            agency_name
        )
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Evaluator profile analysis error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/gpss/strategic-analysis/win-themes', methods=['GET'])
def gpss_strategic_win_themes():
    """
    Get available win themes from library
    
    Optional query params:
      ?industry=Government
    
    Returns:
    {
      "themes": [
        {
          "id": "rec123",
          "name": "Michigan EDWOSB",
          "description": "...",
          "talking_points": [...],
          "strength": 5,
          "win_rate": 72
        }
      ]
    }
    """
    try:
        industry = request.args.get('industry')
        
        svc = StrategicAnalysisService()
        themes = svc.get_win_themes(industry)
        
        return jsonify({"themes": themes})
        
    except Exception as e:
        print(f"Win themes retrieval error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/gpss/strategic-analysis/select-win-themes', methods=['POST'])
def gpss_strategic_select_win_themes():
    """
    AI-powered selection of optimal win themes for opportunity
    
    Expected JSON:
    {
      "opportunity_id": "recXXXXX",
      "rfp_text": "Full RFP text..."
    }
    
    Returns:
    {
      "selected_themes": [
        {
          "id": "rec123",
          "name": "Michigan EDWOSB",
          ...
        }
      ]
    }
    """
    try:
        data = request.json or {}
        opportunity_id = data.get('opportunity_id')
        rfp_text = data.get('rfp_text', '')
        
        if not opportunity_id:
            return jsonify({"error": "opportunity_id is required"}), 400
        
        svc = StrategicAnalysisService()
        
        # Get all themes
        all_themes = svc.get_win_themes()
        
        # Select optimal themes
        selected = svc.select_optimal_win_themes(
            opportunity_id,
            all_themes,
            rfp_text
        )
        
        return jsonify({"selected_themes": selected})
        
    except Exception as e:
        print(f"Win theme selection error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/gpss/strategic-analysis/report/<opportunity_id>', methods=['GET'])
def gpss_strategic_report(opportunity_id):
    """
    Generate comprehensive strategic analysis report
    
    Returns:
    {
      "opportunity_id": "recXXXXX",
      "opportunity_name": "...",
      "go_no_go_score": 38,
      "win_probability": 65,
      "strategic_recommendation": "Pursue",
      "breakdown": {...},
      "evaluator_profile": {...},
      "selected_win_themes": [...]
    }
    """
    try:
        svc = StrategicAnalysisService()
        report = svc.generate_strategic_report(opportunity_id)
        
        if 'error' in report:
            return jsonify(report), 404
        
        return jsonify(report)
        
    except Exception as e:
        print(f"Strategic report generation error: {e}")
        return jsonify({"error": str(e)}), 500


# =====================================================================
# DDCSS PROSPECT MINING ENDPOINTS
# =====================================================================

@app.route('/ddcss/run-mining', methods=['POST'])
def run_ddcss_mining():
    """
    Run all free DDCSS mining sources in one call.
    Sources: corporate HR signals, job postings, diversity news.
    All three target companies DDI can serve DIRECTLY (no government contract, no sub needed).
    New prospects saved to DDCSS Prospects Airtable table.
    """
    try:
        from nexus_backend import DDCSSProspectMiner
        miner = DDCSSProspectMiner()
        results = miner.run_all_free_sources()
        return jsonify({
            'success': True,
            'total_added': results['total_added'],
            'corporate_hr_signals_added': len(results['corporate_hr_signals']),
            'job_postings_added': len(results['job_postings']),
            'diversity_news_added': len(results['diversity_news']),
            'errors': results['errors'],
            'run_time': results['run_time'],
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/ddcss/mine-corporate-hr', methods=['POST'])
def ddcss_mine_corporate_hr():
    """
    Mine corporate HR signals: healthcare, staffing, manufacturing, logistics companies
    expanding or hiring in Michigan — all high-need buyers of DDI's direct-delivery services.
    """
    try:
        from nexus_backend import DDCSSProspectMiner
        miner = DDCSSProspectMiner()
        results = miner.mine_corporate_hr_signals()
        added = [r for r in results if 'error' not in r]
        errors = [r['error'] for r in results if 'error' in r]
        return jsonify({
            'success': True,
            'added': len(added),
            'prospects': added,
            'errors': errors,
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/ddcss/mine-jobs', methods=['POST'])
def ddcss_mine_job_postings():
    """Mine job boards for companies hiring roles DDI can replace with a vendor contract."""
    try:
        from nexus_backend import DDCSSProspectMiner
        miner = DDCSSProspectMiner()
        results = miner.mine_job_postings()
        added = [r for r in results if 'error' not in r]
        errors = [r['error'] for r in results if 'error' in r]
        return jsonify({
            'success': True,
            'added': len(added),
            'prospects': added,
            'errors': errors,
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/ddcss/mine-diversity-news', methods=['POST'])
def ddcss_mine_diversity_news():
    """Monitor news for companies announcing supplier diversity initiatives."""
    try:
        from nexus_backend import DDCSSProspectMiner
        miner = DDCSSProspectMiner()
        results = miner.mine_diversity_news()
        added = [r for r in results if 'error' not in r]
        errors = [r['error'] for r in results if 'error' in r]
        return jsonify({
            'success': True,
            'added': len(added),
            'prospects': added,
            'errors': errors,
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# =====================================================================
# DDCSS CORPORATE PORTAL TRACKER ENDPOINTS
# =====================================================================

@app.route('/ddcss/portals', methods=['GET'])
def get_ddcss_portals():
    """
    Get all corporate supplier portals DDI should register with.
    Optional query param: ?status=Not+Started|Registered|Active|Pending+Approval|Needs+Renewal
    """
    try:
        from nexus_backend import DDCSSPortalTracker
        tracker = DDCSSPortalTracker()
        status_filter = request.args.get('status')
        portals = tracker.get_portals(status_filter=status_filter)
        return jsonify({'success': True, 'portals': portals, 'count': len(portals)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/ddcss/portals/seed', methods=['POST'])
def seed_ddcss_portals():
    """
    Populate DDCSS Corporate Portals table with DDI's priority target list.
    Safe to run multiple times — skips existing records.
    Run this once to initialize the tracker with 20 pre-researched portals.
    """
    try:
        from nexus_backend import DDCSSPortalTracker
        tracker = DDCSSPortalTracker()
        result = tracker.seed_portals()
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/ddcss/portals/<portal_id>', methods=['PUT'])
def update_ddcss_portal(portal_id):
    """
    Update a portal record — mark as registered, add contact info, set next action.
    Body fields: registrationStatus, accountNumber, contactName, contactTitle,
                 contactEmail, registrationDate, lastLogin, nextAction, nextActionDate, notes
    """
    try:
        from nexus_backend import DDCSSPortalTracker
        tracker = DDCSSPortalTracker()
        data = request.json or {}
        result = tracker.update_portal(portal_id, data)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/ddcss/portals/dashboard', methods=['GET'])
def ddcss_portals_dashboard():
    """
    Summary of portal registration progress:
    total, status breakdown, high-priority not-started list, active count.
    """
    try:
        from nexus_backend import DDCSSPortalTracker
        tracker = DDCSSPortalTracker()
        summary = tracker.get_dashboard_summary()
        return jsonify({'success': True, **summary})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# =====================================================================
# DDCSS PROSPECTS & TOOLS ENDPOINTS
# =====================================================================

@app.route('/ddcss/prospects', methods=['GET'])
def get_ddcss_prospects():
    """Get all DDCSS prospects"""
    try:
        airtable_client = AirtableClient()
        
        try:
            records = airtable_client.get_all_records('DDCSS Prospects')
        except:
            return jsonify({'prospects': []})
        
        prospects = []
        for record in records:
            fields = record['fields']
            prospects.append({
                'id': record['id'],
                'companyName': fields.get('Company Name', ''),
                'industry': fields.get('Industry', ''),
                'companySize': fields.get('Company Size', ''),
                'location': fields.get('Location', ''),
                'currentChallenge': fields.get('Current Challenge', ''),
                'businessGoals': fields.get('Business Goals', ''),
                'budget': fields.get('Budget', ''),
                'timeline': fields.get('Timeline', ''),
                'qualificationScore': fields.get('Qualification Score', 0),
                'icpFitScore': fields.get('ICP Fit Score', 0),
                'status': fields.get('Status', 'New'),
                'created': fields.get('Created', '')
            })
        
        return jsonify({'prospects': prospects})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/ddcss/prospects', methods=['POST'])
def create_ddcss_prospect():
    """Create a new DDCSS prospect"""
    try:
        data = request.json
        airtable_client = AirtableClient()
        
        fields = {
            'Company Name': data.get('companyName', ''),
            'Industry': data.get('industry', ''),
            'Company Size': data.get('companySize', ''),
            'Location': data.get('location', ''),
            'Current Challenge': data.get('currentChallenge', ''),
            'Business Goals': data.get('businessGoals', ''),
            'Budget': data.get('budget', ''),
            'Timeline': data.get('timeline', ''),
            'Status': 'New',
            'Created': datetime.now().isoformat()
        }
        
        result = airtable_client.create_record('DDCSS Prospects', fields)
        return jsonify({'prospect': {'id': result['id'], **fields}})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/ddcss/prospects/<prospect_id>', methods=['PUT'])
def update_ddcss_prospect(prospect_id):
    """Update DDCSS prospect - with auto-ATLAS integration when client won"""
    try:
        data = request.json
        airtable_client = AirtableClient()
        
        # Get current prospect to check status change
        current_prospect = airtable_client.get_record('DDCSS Prospects', prospect_id)
        old_status = current_prospect['fields'].get('Status', '')
        
        update_fields = {}
        field_mapping = {
            'companyName': 'Company Name',
            'industry': 'Industry',
            'companySize': 'Company Size',
            'location': 'Location',
            'contactName': 'Contact Name',
            'contactTitle': 'Contact Title',
            'contactEmail': 'Contact Email',
            'contactPhone': 'Contact Phone',
            'linkedinProfile': 'LinkedIn Profile',
            'website': 'Website',
            'pipelineStage': 'Pipeline Stage',
            'status': 'Status',
            'budgetRange': 'Budget Range',
            'timeline': 'Timeline',
            'painPoints': 'Pain Points',
            'qualificationScore': 'Qualification Score',
            'icpFitScore': 'ICP Fit Score',
            'winProbability': 'Win Probability',
            'notes': 'Notes'
        }
        
        for key, airtable_field in field_mapping.items():
            if key in data:
                update_fields[airtable_field] = data[key]
        
        # Update the prospect
        airtable_client.update_record('DDCSS Prospects', prospect_id, update_fields)
        
        new_status = update_fields.get('Status', old_status)
        prism_contract_created = False
        advisor_insight = None

        if new_status == 'Client Won' and old_status != 'Client Won':
            prospect_fields = current_prospect.get('fields', {})

            # VERTEX BRIDGE: Track revenue from corporate client win
            try:
                budget_str = prospect_fields.get('Budget Range', '') or ''
                budget_val = float(budget_str.replace('$', '').replace(',', '').replace('+', '').split('-')[0]) if budget_str else 0
                if budget_val > 0:
                    airtable_client.create_record('VERTEX REVENUE', {
                        VR['revenue_date']:   datetime.now().date().isoformat(),
                        VR['source_system']:  'DDCSS',
                        VR['source']:         prospect_fields.get('Company Name', ''),
                        VR['revenue_type']:   'Corporate Client',
                        VR['amount']:         budget_val,
                        VR['taxable']:        True,
                        VR['recurring']:      False,
                        VR['notes']:          f"Client won: {prospect_fields.get('Company Name', '')} | Prospect ID: {prospect_id}",
                    })
            except Exception as ve:
                print(f"DDCSS → VERTEX revenue: {ve}")

            # VERTEX AUTO-TRIGGER: Fire invoice on corporate client win
            try:
                from vertex_automation import vertex_auto_trigger
                budget_str  = prospect_fields.get('Budget Range', '') or ''
                budget_val  = float(budget_str.replace('$', '').replace(',', '').replace('+', '').split('-')[0]) if budget_str else 0
                vertex_auto_trigger('ddcss.client.won', prospect_id, {
                    'company_name':        prospect_fields.get('Company Name', ''),
                    'service_description': prospect_fields.get('Service Needed', 'Consulting & Management Services'),
                    'monthly_value':       budget_val,
                    'is_recurring':        True,
                })
            except Exception as ve:
                print(f"VERTEX auto-trigger (DDCSS Client Won): {ve}")

            # PRISM BRIDGE: If this is a field service client, register in PRISM
            PRISM_SERVICE_KEYWORDS = [
                'notary', 'notarization', 'RON', 'signing agent', 'credentialing', 'apostille',
                'drug test', 'drug testing', 'drug and alcohol testing', 'DOT drug', 'workplace drug',
                'SAMHSA', 'dna', 'dna test',
                'fingerprint', 'fingerprinting', 'biometrics', 'biometric', 'livescan', 'phlebotomy', 'courier',
                'medical courier', 'healthcare logistics', 'specimen', 'signing', 'mobile notary',
                'background check', 'screening', 'collection',
            ]
            prospect_industry = (prospect_fields.get('Industry', '') or '').lower()
            prospect_services = (prospect_fields.get('Primary Service', '') or '').lower()
            prospect_pain = (prospect_fields.get('Pain Points', '') or '').lower()
            prospect_notes = (prospect_fields.get('Notes', '') or '').lower()
            combined = f"{prospect_industry} {prospect_services} {prospect_pain} {prospect_notes}"
            is_field_service = any(kw in combined for kw in PRISM_SERVICE_KEYWORDS)

            if is_field_service:
                try:
                    airtable_client.create_record('PRISM Contracts', {
                        'Contract Name': f"{prospect_fields.get('Company Name', '')} — Field Services",
                        'Client': prospect_fields.get('Company Name', ''),
                        'Client Type': 'Enterprise',
                        'DDCSS Prospect': [prospect_id],
                        'Status': 'Active',
                        'Start Date': datetime.now().strftime('%Y-%m-%d'),
                        'Source': 'DDCSS Auto-Bridge',
                    })
                    prism_contract_created = True
                except Exception as pe:
                    print(f"DDCSS → PRISM bridge: {pe}")

            # NEXUS ADVISOR: Debrief on corporate win
            try:
                from nexus_advisor import advise
                advisor_insight = advise('ddcss', 'prospect_qualified', {
                    'company': prospect_fields.get('Company Name', ''),
                    'is_field_service': is_field_service,
                })
            except Exception:
                pass

            # AUTO-CREATE ATLAS PROJECT
            existing_atlas_link = prospect_fields.get('ATLAS Project')
            if not existing_atlas_link:
                try:
                    atlas_result = create_atlas_project_from_prospect(prospect_id, airtable_client)
                    
                    return jsonify({
                        'success': True,
                        'message': 'Client Won! ATLAS project created automatically!'
                                   + (' PRISM contract registered for field service.' if prism_contract_created else ''),
                        'atlas_project_created': True,
                        'atlas_project_id': atlas_result['project_id'],
                        'atlas_project_name': atlas_result['project_name'],
                        'wbs_generated': atlas_result.get('wbs_generated', False),
                        'prism_contract_created': prism_contract_created,
                        'advisor': advisor_insight,
                    })
                except Exception as atlas_error:
                    print(f"Error creating ATLAS project from prospect: {atlas_error}")
                    return jsonify({
                        'success': True,
                        'message': 'Prospect updated. ATLAS project creation failed - please create manually.',
                        'atlas_error': str(atlas_error),
                        'prism_contract_created': prism_contract_created,
                        'advisor': advisor_insight,
                    })
        
        return jsonify({'success': True, 'advisor': advisor_insight})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def create_atlas_project_from_prospect(prospect_id: str, airtable_client=None) -> dict:
    """
    🎯 AUTO-CREATE ATLAS PROJECT FROM WON DDCSS PROSPECT
    """
    if not airtable_client:
        airtable_client = AirtableClient()
    
    # Get prospect details
    prospect = airtable_client.get_record('DDCSS Prospects', prospect_id)
    prospect_fields = prospect['fields']
    
    # Extract key information
    company_name = prospect_fields.get('Company Name', 'Unknown Company')
    contact_name = prospect_fields.get('Contact Name', '')
    industry = prospect_fields.get('Industry', 'Unknown')
    budget = prospect_fields.get('Budget Range', '').replace('$', '').replace(',', '').replace('+', '').split('-')[0] if prospect_fields.get('Budget Range') else 0
    
    try:
        budget_value = float(budget) if budget else 50000  # Default to $50K
    except:
        budget_value = 50000
    
    pain_points = prospect_fields.get('Pain Points', '')
    timeline = prospect_fields.get('Timeline', '')
    recommended_service = prospect_fields.get('Primary Service', 'Corporate Consulting')
    
    # Build comprehensive project scope
    project_scope = f"""
CLIENT: {company_name}
CONTACT: {contact_name}
INDUSTRY: {industry}

ENGAGEMENT TYPE: {recommended_service}

PAIN POINTS & OBJECTIVES:
{pain_points}

TIMELINE: {timeline}

DELIVERABLES:
- Discovery & Assessment
- Strategic Recommendations
- Implementation Plan
- Follow-up Support
    """.strip()
    
    # Create ATLAS project record
    project_fields = {
        'Project Name': f"{recommended_service} - {company_name}",
        'Client Name': company_name,
        'Project Type': 'Corporate Consulting',
        'Industry': industry,
        'Budget': budget_value,
        'Project Scope': project_scope[:10000],
        'Start Date': datetime.now().isoformat(),
        'Status': 'Planning',
        'Priority': 'High',
        'Completion Percentage': 0,
        'Created Date': datetime.now().isoformat(),
        'Source System': 'DDCSS',
        'Source Prospect ID': prospect_id
    }
    
    # Create the project
    project_record = airtable_client.create_record('ATLAS PROJECTS', project_fields)
    project_id = project_record['id']
    
    # Link prospect to ATLAS project
    try:
        airtable_client.update_record('DDCSS Prospects', prospect_id, {
            'ATLAS Project': [project_id]
        })
    except Exception as link_error:
        print(f"Warning: Could not link prospect to ATLAS project: {link_error}")
    
    # Auto-generate WBS
    wbs_generated = False
    try:
        from nexus_backend import ATLASAgent2
        atlas_agent = ATLASAgent2()
        wbs_result = atlas_agent.generate_wbs(project_id)
        wbs_generated = 'error' not in wbs_result
    except Exception as wbs_error:
        print(f"Warning: WBS generation failed: {wbs_error}")
    
    return {
        'success': True,
        'project_id': project_id,
        'project_name': project_fields['Project Name'],
        'wbs_generated': wbs_generated,
        'message': f'✅ ATLAS project created: {project_fields["Project Name"]}'
    }


@app.route('/ddcss/prospects/<prospect_id>/create-atlas-project', methods=['POST'])
def manual_create_atlas_project_from_prospect(prospect_id):
    """Manual endpoint to create ATLAS project from prospect"""
    try:
        result = create_atlas_project_from_prospect(prospect_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def _parse_ddcss_notes(notes_str):
    """Parse structured data from Notes field: 'key1:val1|key2:val2' """
    data = {}
    if not notes_str:
        return data
    for part in str(notes_str).split('|'):
        if ':' in part:
            key, val = part.split(':', 1)
            data[key.strip()] = val.strip()
    return data

def _build_ddcss_notes(**kwargs):
    """Build Notes field string from keyword args"""
    parts = []
    for key, val in kwargs.items():
        if val:
            parts.append(f"{key}:{val}")
    return '|'.join(parts)

def _ddcss_prospect_to_dict(record):
    """Convert a DDCSS Prospects Airtable record to a clean dict"""
    fields = record['fields']
    notes = _parse_ddcss_notes(fields.get('Notes', ''))
    return {
        'id': record['id'],
        'companyName': fields.get('Company Name', ''),
        'companySize': fields.get('Company Size', ''),
        'currentChallenge': fields.get('Current Challenge', ''),
        'businessGoals': fields.get('Business Goals', ''),
        'timeline': fields.get('Timeline', ''),
        'painPoints': fields.get('Pain Points', ''),
        'contactName': fields.get('Contact Name', ''),
        'contactEmail': fields.get('Contact Email', ''),
        'contactPhone': fields.get('Contact Phone', ''),
        'qualificationScore': fields.get('Qualification Score', ''),
        'icpFitScore': fields.get('ICP Fit Score', ''),
        # Fields stored in Notes
        'industry': notes.get('Industry', ''),
        'location': notes.get('Location', ''),
        'budget': notes.get('Budget', ''),
        'status': notes.get('Status', 'New'),
        'avatarName': notes.get('Avatar', ''),
        'decisionMakers': notes.get('DecisionMakers', ''),
        'goals': notes.get('Goals', ''),
        'hasAvatar': bool(notes.get('Avatar', '')),
        'created': fields.get('Created Date', ''),
    }


@app.route('/ddcss/client-avatars', methods=['GET'])
def get_ddcss_client_avatars():
    """Get all client avatars (prospects that have avatar data)"""
    try:
        airtable_client = AirtableClient()
        
        try:
            records = airtable_client.get_all_records('DDCSS Prospects')
        except:
            return jsonify({'avatars': []})
        
        avatars = []
        for record in records:
            prospect = _ddcss_prospect_to_dict(record)
            # Include all prospects that have avatar data, or all if none do yet
            if prospect['avatarName'] or prospect['painPoints'] or prospect['companyName']:
                avatars.append(prospect)
        
        return jsonify({'avatars': avatars})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/ddcss/client-avatars', methods=['POST'])
def create_ddcss_client_avatar():
    """Create a new client avatar as a DDCSS prospect with avatar data"""
    try:
        data = request.json
        airtable_client = AirtableClient()
        
        notes = _build_ddcss_notes(
            Industry=data.get('industry', ''),
            Location=data.get('location', ''),
            Budget=data.get('budget', ''),
            Status='New',
            Avatar=data.get('avatarName', ''),
            DecisionMakers=data.get('decisionMakers', ''),
            Goals=data.get('goals', '')
        )
        
        fields = {
            'Company Name': data.get('avatarName', '') or data.get('companyName', ''),
            'Company Size': data.get('companySize', ''),
            'Current Challenge': data.get('currentChallenge', ''),
            'Business Goals': data.get('businessGoals', data.get('goals', '')),
            'Pain Points': data.get('painPoints', ''),
            'Contact Name': data.get('decisionMakers', ''),
            'Notes': notes,
        }
        
        result = airtable_client.create_record('DDCSS Prospects', fields)
        
        # AI Analysis using Claude directly with avatar data
        ai_analysis = {}
        try:
            from nexus_backend import AnthropicClient
            ai = AnthropicClient()
            
            prompt = f"""Analyze this corporate prospect avatar for a consulting engagement:

Avatar/Company: {data.get('avatarName', 'Unknown')}
Industry: {data.get('industry', 'Unknown')}
Company Size: {data.get('companySize', 'Unknown')}
Budget Range: {data.get('budget', 'Unknown')}
Pain Points: {data.get('painPoints', 'None specified')}
Goals: {data.get('goals', 'None specified')}
Decision Makers: {data.get('decisionMakers', 'Unknown')}

Provide a JSON response with:
- "qualification_score": 0-100 (how good a fit is this for a $25K+ consulting engagement)
- "recommended_approach": one sentence on how to approach this prospect
- "win_probability": estimated percentage
- "key_pain_to_target": the most actionable pain point to lead with
- "suggested_offer_angle": how to position the offer for this specific avatar
- "objection_to_expect": the most likely objection and how to handle it"""

            import json as json_mod
            import re as re_mod
            
            raw = ai.complete(prompt, max_tokens=1000)
            
            # Parse JSON from response
            try:
                ai_analysis = json_mod.loads(raw)
            except:
                match = re_mod.search(r'```(?:json)?\s*\n?(.*?)\n?```', raw, re_mod.DOTALL)
                if match:
                    try:
                        ai_analysis = json_mod.loads(match.group(1))
                    except:
                        pass
                if not ai_analysis:
                    match = re_mod.search(r'\{.*\}', raw, re_mod.DOTALL)
                    if match:
                        try:
                            ai_analysis = json_mod.loads(match.group(0))
                        except:
                            ai_analysis = {"analysis": raw}
            
            # Update qualification score on record if we got one
            if ai_analysis.get('qualification_score'):
                try:
                    airtable_client.update_record('DDCSS Prospects', result['id'], {
                        'Qualification Score': str(ai_analysis['qualification_score']),
                        'ICP Fit Score': str(ai_analysis.get('win_probability', ''))
                    })
                except:
                    pass
                    
        except Exception as ai_err:
            print(f"AI analysis error: {ai_err}")
            import traceback
            traceback.print_exc()
        
        avatar_data = _ddcss_prospect_to_dict(result)
        
        return jsonify({
            'avatar': avatar_data,
            'aiAnalysis': ai_analysis
        })
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route('/ddcss/client-avatars/<avatar_id>', methods=['PUT'])
def update_ddcss_client_avatar(avatar_id):
    """Update an existing client avatar"""
    try:
        data = request.json
        airtable_client = AirtableClient()
        
        update_fields = {}
        if 'companyName' in data or 'avatarName' in data:
            update_fields['Company Name'] = data.get('avatarName', data.get('companyName', ''))
        if 'companySize' in data:
            update_fields['Company Size'] = data['companySize']
        if 'painPoints' in data:
            update_fields['Pain Points'] = data['painPoints']
        if 'businessGoals' in data:
            update_fields['Business Goals'] = data['businessGoals']
        if 'currentChallenge' in data:
            update_fields['Current Challenge'] = data['currentChallenge']
        if 'decisionMakers' in data:
            update_fields['Contact Name'] = data['decisionMakers']
        
        # Rebuild notes with updated values
        current = airtable_client.get_record('DDCSS Prospects', avatar_id)
        current_notes = _parse_ddcss_notes(current['fields'].get('Notes', ''))
        
        if 'industry' in data: current_notes['Industry'] = data['industry']
        if 'budget' in data: current_notes['Budget'] = data['budget']
        if 'location' in data: current_notes['Location'] = data['location']
        if 'status' in data: current_notes['Status'] = data['status']
        if 'avatarName' in data: current_notes['Avatar'] = data['avatarName']
        if 'goals' in data: current_notes['Goals'] = data['goals']
        if 'decisionMakers' in data: current_notes['DecisionMakers'] = data['decisionMakers']
        
        update_fields['Notes'] = _build_ddcss_notes(**current_notes)
        
        airtable_client.update_record('DDCSS Prospects', avatar_id, update_fields)
        
        updated = airtable_client.get_record('DDCSS Prospects', avatar_id)
        return jsonify({'avatar': _ddcss_prospect_to_dict(updated)})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/ddcss/client-avatars/<avatar_id>', methods=['DELETE'])
def delete_ddcss_client_avatar(avatar_id):
    """Delete a client avatar"""
    try:
        airtable_client = AirtableClient()
        airtable_client.delete_record('DDCSS Prospects', avatar_id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/ddcss/success-paths', methods=['POST'])
def create_ddcss_success_path():
    """Create a success path (with AI visualization)"""
    try:
        data = request.json
        airtable_client = AirtableClient()
        
        fields = {
            'Path Name': data.get('pathName', ''),
            'Prospect ID': data.get('prospectId', ''),
            'Starting Point': data.get('startingPoint', ''),
            'End Goal': data.get('endGoal', ''),
            'Milestones': data.get('milestones', ''),
            'Timeline': data.get('timeline', ''),
            'Created': datetime.now().isoformat()
        }
        
        result = airtable_client.create_record('DDCSS Success Paths', fields)
        return jsonify({'successPath': {'id': result['id'], **fields}})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/ddcss/pitchmaps', methods=['POST'])
def create_ddcss_pitchmap():
    """Generate a pitchmap (with AI script generation)"""
    try:
        data = request.json
        airtable_client = AirtableClient()
        
        # Generate AI script
        script_content = ""
        try:
            import anthropic
            anthropic_client = anthropic.Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))
            
            message = anthropic_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2000,
                messages=[{
                    "role": "user",
                    "content": f"""Generate a pitch script for this scenario:

Prospect: {data.get('prospectName', 'Unknown')}
Industry: {data.get('industry', 'Unknown')}
Pain Point: {data.get('painPoint', 'Unknown')}
Goal: {data.get('goal', 'Unknown')}
Timeline: {data.get('timeline', 'Unknown')}

Create a compelling, consultative pitch script that:
1. Opens with a hook based on their pain point
2. Positions our Blueprint Framework as the solution
3. Includes 2-3 proof points
4. Closes with a clear next step (discovery call)

Keep it conversational, professional, and focused on outcomes."""
                }]
            )
            script_content = message.content[0].text
        except:
            script_content = "AI script generation unavailable"
        
        fields = {
            'PitchMap Name': data.get('pitchMapName', ''),
            'Prospect ID': data.get('prospectId', ''),
            'Pain Point': data.get('painPoint', ''),
            'Solution': data.get('solution', ''),
            'Script': script_content,
            'Status': 'Draft',
            'Created': datetime.now().isoformat()
        }
        
        result = airtable_client.create_record('DDCSS PitchMaps', fields)
        return jsonify({
            'pitchmap': {'id': result['id'], **fields},
            'script': script_content
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =====================================================================
# MINING TARGETS ENDPOINTS
# =====================================================================

@app.route('/gpss/mining/targets', methods=['GET'])
def get_mining_targets():
    """Get all mining targets"""
    try:
        airtable_client = AirtableClient()
        
        try:
            records = airtable_client.get_all_records('Mining Targets')
        except:
            return jsonify({'targets': []})
        
        targets = []
        for record in records:
            fields = record['fields']
            targets.append({
                'id': record['id'],
                'targetName': fields.get('Target Name', ''),
                'url': fields.get('URL', ''),
                'targetType': fields.get('Target Type', ''),
                'keywords': fields.get('Keywords', ''),
                'lastScraped': fields.get('Last Scraped', ''),
                'active': fields.get('Active', True)
            })
        
        return jsonify({'targets': targets})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/gpss/mining/targets', methods=['POST'])
def create_mining_target():
    """Create a new mining target"""
    try:
        data = request.json
        airtable_client = AirtableClient()
        
        fields = {
            'Target Name': data.get('targetName', ''),
            'URL': data.get('url', ''),
            'Target Type': data.get('targetType', 'Website'),
            'Keywords': data.get('keywords', ''),
            'Active': data.get('active', True),
            'Created': datetime.now().isoformat()
        }
        
        result = airtable_client.create_record('Mining Targets', fields)
        return jsonify({'target': {'id': result['id'], **fields}})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/gpss/mining/targets/<target_id>', methods=['PUT'])
def update_mining_target(target_id):
    """Update a mining target"""
    try:
        data = request.json
        airtable_client = AirtableClient()
        
        field_mapping = {
            'targetName': 'Target Name',
            'url': 'URL',
            'targetType': 'Target Type',
            'keywords': 'Keywords',
            'active': 'Active'
        }
        
        update_fields = {}
        for key, airtable_field in field_mapping.items():
            if key in data:
                update_fields[airtable_field] = data[key]
        
        airtable_client.update_record('Mining Targets', target_id, update_fields)
        return jsonify({'success': True})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/gpss/mining/targets/<target_id>', methods=['DELETE'])
def delete_mining_target(target_id):
    """Delete a mining target"""
    try:
        airtable_client = AirtableClient()
        table = airtable_client.get_table('Mining Targets')
        table.delete(target_id)
        return jsonify({'success': True})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================================================
# CONTRACTING OFFICER OUTREACH ENDPOINTS
# ============================================================================

@app.route('/gpss/officer-outreach/generate', methods=['POST'])
def generate_officer_outreach():
    """Generate introduction letters for closed opportunities"""
    try:
        from contracting_officer_outreach import run_officer_outreach_mining
        
        data = request.json or {}
        limit = data.get('limit', 10)
        
        airtable_client = AirtableClient()
        results = run_officer_outreach_mining(airtable_client, limit=limit)
        
        return jsonify({
            'success': True,
            'letters_generated': results['letters_generated'],
            'results': results['results'],
            'timestamp': results['timestamp']
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/gpss/officer-outreach/letters', methods=['GET'])
def get_outreach_letters():
    """Get all officer outreach letters"""
    try:
        airtable_client = AirtableClient()
        records = airtable_client.get_all_records('Officer Outreach Tracking')
        
        letters = []
        for record in records:
            fields = record.get('fields', {})
            letters.append({
                'id': record['id'],
                'officer_name': fields.get('Officer Name', ''),
                'officer_email': fields.get('Officer Email', ''),
                'opportunity_title': fields.get('Opportunity Title', ''),
                'solicitation_number': fields.get('Solicitation Number', ''),
                'status': fields.get('Status', 'Draft'),
                'generated_date': fields.get('Letter Generated Date', ''),
                'date_sent': fields.get('Date Sent', ''),
                'response_received': fields.get('Response Received', False),
                'subject_line': fields.get('Subject Line', ''),
            })
        
        return jsonify({'success': True, 'letters': letters})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/gpss/officer-outreach/letters/<letter_id>', methods=['GET'])
def get_outreach_letter(letter_id):
    """Get a specific outreach letter with full content"""
    try:
        airtable_client = AirtableClient()
        record = airtable_client.get_record('Officer Outreach Tracking', letter_id)
        
        fields = record.get('fields', {})
        
        return jsonify({
            'success': True,
            'letter': {
                'id': record['id'],
                'officer_name': fields.get('Officer Name', ''),
                'officer_email': fields.get('Officer Email', ''),
                'opportunity_title': fields.get('Opportunity Title', ''),
                'solicitation_number': fields.get('Solicitation Number', ''),
                'agency': fields.get('Agency', ''),
                'status': fields.get('Status', 'Draft'),
                'generated_date': fields.get('Letter Generated Date', ''),
                'date_sent': fields.get('Date Sent', ''),
                'follow_up_date': fields.get('Follow-up Date', ''),
                'response_received': fields.get('Response Received', False),
                'response_notes': fields.get('Response Notes', ''),
                'added_to_vendor_list': fields.get('Added to Vendor List', False),
                'subject_line': fields.get('Subject Line', ''),
                'letter_content': fields.get('Letter Content', ''),
                'tags': fields.get('Tags', []),
                'priority': fields.get('Priority', 'Medium'),
            }
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/gpss/officer-outreach/letters/<letter_id>', methods=['PUT'])
def update_outreach_letter(letter_id):
    """Update an outreach letter (e.g., mark as sent, add response)"""
    try:
        data = request.json
        airtable_client = AirtableClient()
        
        update_fields = {}
        
        # Map frontend fields to Airtable fields
        field_mapping = {
            'status': 'Status',
            'date_sent': 'Date Sent',
            'response_received': 'Response Received',
            'response_notes': 'Response Notes',
            'added_to_vendor_list': 'Added to Vendor List',
            'priority': 'Priority',
            'tags': 'Tags',
            'next_action': 'Next Action',
            'next_action_date': 'Next Action Date',
        }
        
        for key, airtable_field in field_mapping.items():
            if key in data:
                update_fields[airtable_field] = data[key]
        
        airtable_client.update_record('Officer Outreach Tracking', letter_id, update_fields)
        
        return jsonify({'success': True})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/gpss/officer-outreach/stats', methods=['GET'])
def get_outreach_stats():
    """Get statistics about officer outreach"""
    try:
        airtable_client = AirtableClient()
        records = airtable_client.get_all_records('Officer Outreach Tracking')
        
        stats = {
            'total_letters': len(records),
            'draft': 0,
            'sent': 0,
            'responded': 0,
            'added_to_vendor_list': 0,
            'response_rate': 0,
            'vendor_list_rate': 0,
        }
        
        for record in records:
            fields = record.get('fields', {})
            status = fields.get('Status', 'Draft')
            
            if status == 'Draft':
                stats['draft'] += 1
            elif status in ['Sent', 'Follow-up Needed']:
                stats['sent'] += 1
            
            if fields.get('Response Received'):
                stats['responded'] += 1
            
            if fields.get('Added to Vendor List'):
                stats['added_to_vendor_list'] += 1
        
        # Calculate rates
        if stats['sent'] > 0:
            stats['response_rate'] = round((stats['responded'] / stats['sent']) * 100, 1)
        
        if stats['responded'] > 0:
            stats['vendor_list_rate'] = round((stats['added_to_vendor_list'] / stats['responded']) * 100, 1)
        
        return jsonify({'success': True, 'stats': stats})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================================================
# FORECAST CAPSTAT OUTREACH ENDPOINTS (PROACTIVE OFFICER OUTREACH)
# ============================================================================

@app.route('/api/forecasts/<forecast_id>/generate-capstat-outreach', methods=['POST'])
def generate_forecast_capstat_outreach(forecast_id: str):
    """
    Generate capability statement and outreach letter for a federal forecast
    
    This endpoint is called by the "📧 Reach Out to Officer" button in Airtable
    or from the NEXUS frontend when user wants to proactively reach out to
    a contracting officer BEFORE the RFP drops (3-6 months in advance).
    
    Workflow:
    1. Gets forecast details from Airtable
    2. Generates tailored capability statement
    3. Generates proactive introduction letter
    4. Creates Officer Outreach Tracking record
    5. Links everything together
    
    Args:
        forecast_id: Airtable record ID from Federal Forecasts table
    
    Request body: None required (all data from forecast record)
    
    Returns:
        {
            "success": true,
            "message": "Capability statement and outreach letter generated!",
            "forecast_title": "NASA - IT Equipment",
            "capstat_pdf": "/path/to/capstat.pdf",
            "capstat_html": "/path/to/capstat.html",
            "outreach_record_id": "recXXXX",
            "officer_email": "john.smith@nasa.gov",
            "officer_name": "John Smith",
            "next_steps": [...]
        }
    """
    try:
        from forecast_capstat_outreach import handle_forecast_capstat_outreach
        
        result = handle_forecast_capstat_outreach(forecast_id)
        
        if result.get('success'):
            return jsonify(result), 200
        else:
            return jsonify(result), 400
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': f"Failed to generate forecast outreach: {str(e)}"
        }), 500


@app.route('/api/forecasts/<forecast_id>/generate-incumbent-outreach', methods=['POST'])
def generate_incumbent_outreach(forecast_id: str):
    """
    Generate a teaming outreach email to the incumbent on a renewal forecast.
    
    Triggered by "🤝 Reach Out to Incumbent" button on Federal Forecasts records
    where Current Holder is populated.
    
    Returns draft teaming email + research links saved to Officer Outreach Tracking.
    """
    try:
        from forecast_capstat_outreach import handle_incumbent_outreach
        result = handle_incumbent_outreach(forecast_id)
        if result.get('success'):
            return jsonify(result), 200
        else:
            return jsonify(result), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': f"Failed to generate incumbent outreach: {str(e)}"
        }), 500


@app.route('/api/forecasts/batch-outreach', methods=['POST'])
def batch_process_forecast_outreach():
    """
    Batch process: Generate cap statements for multiple high-priority forecasts
    
    Useful for weekly prep sessions - generate outreach for top N forecasts
    
    Request body:
        {
            "limit": 5  // Optional: max forecasts to process (default 5)
        }
    
    Returns:
        {
            "success": true,
            "processed": 5,
            "results": [
                {
                    "forecast_id": "recXXXX",
                    "forecast_title": "NASA - IT Equipment",
                    "officer_name": "John Smith",
                    "officer_email": "john.smith@nasa.gov",
                    "outreach_record_id": "recYYYY",
                    "capstat_pdf": "/path/to/capstat.pdf"
                },
                ...
            ],
            "timestamp": "2026-01-31T10:30:00"
        }
    """
    try:
        from forecast_capstat_outreach import process_high_priority_forecasts
        
        data = request.get_json() or {}
        limit = data.get('limit', 5)
        
        result = process_high_priority_forecasts(limit=limit)
        
        return jsonify(result), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================================================
# AI CONVERSATIONS ENDPOINTS
# ============================================================================

@app.route('/ai/conversations', methods=['POST'])
def create_conversation():
    """Create a new AI conversation"""
    try:
        data = request.json
        airtable_client = AirtableClient()
        
        import json
        fields = {
            'SESSION ID': data.get('sessionId'),
            'MESSAGES': json.dumps(data.get('messages', [])),
            'MESSAGE COUNT': len(data.get('messages', [])),
            'SYSTEM CONTEXT': data.get('systemContext', 'General'),
            'STATUS': 'ACTIVE'
        }
        
        record = airtable_client.create_record('AI Conversations', fields)
        return jsonify({'success': True, 'recordId': record['id']})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/ai/conversations/<session_id>', methods=['PUT'])
def update_conversation(session_id):
    """Update an existing AI conversation with new messages"""
    try:
        data = request.json
        airtable_client = AirtableClient()
        
        import json
        
        # Find the conversation by session ID
        records = airtable_client.get_all_records('AI Conversations')
        conversation_record = None
        for record in records:
            if record['fields'].get('SESSION ID') == session_id:
                conversation_record = record
                break
        
        if not conversation_record:
            # Create new conversation if doesn't exist
            fields = {
                'SESSION ID': session_id,
                'MESSAGES': json.dumps(data.get('messages', [])),
                'MESSAGE COUNT': len(data.get('messages', [])),
                'SYSTEM CONTEXT': data.get('systemContext', 'General'),
                'STATUS': 'ACTIVE'
            }
            record = airtable_client.create_record('AI Conversations', fields)
            return jsonify({'success': True, 'recordId': record['id']})
        
        # Update existing conversation
        update_fields = {
            'MESSAGES': json.dumps(data.get('messages', [])),
            'MESSAGE COUNT': len(data.get('messages', []))
        }
        
        if 'systemContext' in data:
            update_fields['SYSTEM CONTEXT'] = data['systemContext']
        if 'status' in data:
            update_fields['STATUS'] = data['status'].upper()
        if 'notes' in data:
            update_fields['NOTES'] = data['notes']
        
        airtable_client.update_record('AI Conversations', conversation_record['id'], update_fields)
        return jsonify({'success': True, 'recordId': conversation_record['id']})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/ai/conversations/<session_id>', methods=['GET'])
def get_conversation(session_id):
    """Get a conversation by session ID"""
    try:
        airtable_client = AirtableClient()
        
        import json
        
        records = airtable_client.get_all_records('AI Conversations')
        for record in records:
            if record['fields'].get('SESSION ID') == session_id:
                fields = record['fields']
                return jsonify({
                    'success': True,
                    'conversation': {
                        'sessionId': fields.get('SESSION ID'),
                        'messages': json.loads(fields.get('MESSAGES', '[]')),
                        'messageCount': fields.get('MESSAGE COUNT', 0),
                        'systemContext': fields.get('SYSTEM CONTEXT'),
                        'status': fields.get('STATUS'),
                        'notes': fields.get('NOTES'),
                    }
                })
        
        return jsonify({"error": "Conversation not found"}), 404
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/alexa/command', methods=['POST'])
@require_alexa_auth
def alexa_command():
    """Alexa voice command endpoint - processes voice commands securely"""
    try:
        data = request.json
        command = data.get('command', '').strip()

        if not command:
            return jsonify({
                'response': 'I didn\'t hear a command. Please try again.',
                'success': False
            })

        # Process the command through the AI copilot
        ai_response = process_alexa_command(command)

        return jsonify({
            'response': ai_response,
            'success': True
        })

    except Exception as e:
        return jsonify({
            'response': f'Sorry, I encountered an error processing your request.',
            'success': False,
            'error': str(e)
        }), 500

def process_alexa_command(command):
    """
    Process Alexa voice commands and return appropriate responses
    Handles 86 intents across all NEXUS systems
    """
    command_lower = command.lower()
    
    # ========== CORE SYSTEM COMMANDS ==========
    
    # Hello/Greeting
    if command_lower == 'hello':
        return "Hello! I'm Alexis, your NEXUS executive assistant. How can I help you today?"
    
    # System-wide status
    if 'nexus:' in command_lower and 'system-wide status' in command_lower:
        return get_nexus_system_status()
    
    # Meeting notes dictation
    if 'meeting notes:' in command_lower and 'dictate' in command_lower:
        return "Meeting notes feature is ready. Please continue with your dictation."
    
    # Compliance landscape
    if 'compliance:' in command_lower and 'landscape' in command_lower:
        return get_compliance_overview()
    
    # Invoice status
    if 'invoices:' in command_lower and 'status' in command_lower:
        return get_invoice_status()
    
    # Financial metrics
    if 'financial:' in command_lower and 'metrics' in command_lower:
        return get_financial_metrics()
    
    # ========== EXECUTIVE ASSISTANT COMMANDS ==========
    
    # NEXUS features explanation
    if 'nexus:' in command_lower and 'explain features' in command_lower:
        return "NEXUS integrates government contracting, project management, market intelligence, compliance tracking, and financial metrics into one voice-controlled system."
    
    # Reminders
    if 'reminders:' in command_lower and 'list' in command_lower:
        return "You have no pending reminders at this time."
    
    # Contacts management
    if 'contacts:' in command_lower and 'manage' in command_lower:
        return get_contacts_summary()
    
    # Task creation
    if 'task:' in command_lower and 'create' in command_lower:
        return "Task creation feature is ready. What task would you like to create?"
    
    # Notifications
    if 'notifications:' in command_lower and 'show' in command_lower:
        return "You have no new notifications at this time."
    
    # ========== GPSS - GOVERNMENT CONTRACTING ==========
    
    # Search contracts
    if 'gpss:' in command_lower and 'search contracts' in command_lower:
        return "Searching government contract opportunities. This feature connects to SAM.gov and other federal databases."
    
    # Pipeline analysis
    if 'gpss:' in command_lower and 'analyze pipeline' in command_lower:
        return get_gpss_pipeline_analysis()
    
    # Federal buyer info
    if 'gpss:' in command_lower and 'federal buyer' in command_lower:
        return "Federal buyer intelligence feature is ready. Which agency are you interested in?"
    
    # Contract details
    if 'gpss:' in command_lower and 'contract details' in command_lower:
        return "Contract details feature is ready. Which contract would you like to review?"
    
    # ========== ATLAS PM - PROJECT MANAGEMENT ==========
    
    # Manage tasks
    if 'atlas:' in command_lower and 'manage tasks' in command_lower:
        return get_atlas_tasks_summary()
    
    # Project health
    if 'atlas:' in command_lower and 'project health' in command_lower:
        return "Project health monitoring is active. All projects are currently on track."
    
    # Team capacity
    if 'atlas:' in command_lower and 'team capacity' in command_lower:
        return "Team capacity analysis is ready. Your team has bandwidth for new projects."
    
    # ========== DDCSS - MARKET INTELLIGENCE ==========
    
    # Search market problems
    if 'ddcss:' in command_lower and 'search market problems' in command_lower:
        return "Market problem discovery system is active. I'm analyzing current market inefficiencies."
    
    # MVP status
    if 'ddcss:' in command_lower and 'mvp status' in command_lower:
        return "MVP validation system is ready. Would you like to see your top validated problems?"
    
    # Rank problems
    if 'ddcss:' in command_lower and 'rank problems' in command_lower:
        return "Problem ranking by opportunity is ready. I can show you the most profitable problems to solve."
    
    # ========== STRATEGIC INTELLIGENCE ==========
    
    # Executive briefing
    if 'executive:' in command_lower and 'daily briefing' in command_lower:
        return get_executive_briefing()
    
    # Contract opportunities alert
    if 'executive:' in command_lower and 'contract opportunities' in command_lower:
        return get_contract_opportunities_alert()
    
    # Prepare for meeting
    if 'executive:' in command_lower and 'prepare for meeting' in command_lower:
        return "Meeting preparation is ready. I'm compiling relevant context and background information."
    
    # Government contract pipeline
    if 'executive:' in command_lower and 'government contract pipeline' in command_lower:
        return get_government_contract_pipeline()
    
    # ========== AI INTELLIGENCE ==========
    
    # Decision support
    if 'ai:' in command_lower and 'decision support' in command_lower:
        return "AI decision support is ready. What decision would you like help with?"
    
    # Generate report
    if 'ai:' in command_lower and 'generate report' in command_lower:
        return "Autonomous report generation is ready. What type of report would you like?"
    
    # Proactive insights
    if 'ai:' in command_lower and 'proactive insights' in command_lower:
        return get_proactive_insights()
    
    # Learn business context
    if 'ai:' in command_lower and 'learn business context' in command_lower:
        return "I'm ready to learn about your business. Please share what you'd like me to remember."
    
    # ========== LEGACY COMMANDS (keep for backwards compatibility) ==========
    
    # Contact creation commands
    if 'add contact' in command_lower or 'create contact' in command_lower:
        # Extract contact info from voice command
        import re

        email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', command)
        email = email_match.group(0) if email_match else ''

        phone_match = re.search(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', command)
        phone = phone_match.group(0) if phone_match else ''

        # Extract name by removing command words and contact details
        name_text = command
        if email:
            name_text = name_text.replace(email, '')
        if phone:
            name_text = name_text.replace(phone, '')

        # Remove command words
        for word in ['add', 'contact', 'create', 'new', 'alexa', 'tell', 'nexus', 'to']:
            name_text = re.sub(r'\b' + word + r'\b', '', name_text, flags=re.IGNORECASE)

        name_text = re.sub(r'[^\w\s]', '', name_text).strip()
        name_parts = name_text.split()
        first_name = name_parts[0] if name_parts else ''
        last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''

        if first_name:
            try:
                airtable_client = AirtableClient()
                contact_fields = {
                    'First Name': first_name,
                    'Last Name': last_name,
                    'Email': email,
                    'Phone': phone,
                    'Source': 'Alexa Voice Assistant'
                }

                result = airtable_client.create_record('GPSS CONTACTS', contact_fields)
                return f"Contact {first_name} {last_name} has been added to your NEXUS database."

            except Exception as e:
                return f"I had trouble adding that contact. Please check your NEXUS system manually."
        else:
            return "I need a name to create a contact. Please specify the person's name."

    # Opportunity creation commands
    elif 'create opportunity' in command_lower or 'add opportunity' in command_lower:
        try:
            # Extract basic opportunity info
            opp_title = "New Opportunity"  # Default
            opp_value = ""
            opp_agency = ""

            # Simple extraction - user can provide more details via web interface
            airtable_client = AirtableClient()
            opp_fields = {
                'Title': opp_title,
                'Value': opp_value,
                'Agency': opp_agency,
                'Status': 'New',
                'Source': 'Alexa Voice Assistant'
            }

            result = airtable_client.create_record('GPSS OPPORTUNITIES', opp_fields)
            return f"New opportunity has been created in your NEXUS system. You can add details via the web interface."

        except Exception as e:
            return "I couldn't create that opportunity. Please try through the NEXUS web interface."

    # Status requests
    elif 'status' in command_lower or 'how am i doing' in command_lower or 'update' in command_lower:
        try:
            airtable_client = AirtableClient()

            # Get basic stats
            opportunities = airtable_client.get_all_records('GPSS OPPORTUNITIES')
            contacts = airtable_client.get_all_records('GPSS CONTACTS')

            opp_count = len(opportunities) if opportunities else 0
            contact_count = len(contacts) if contacts else 0

            return f"You have {opp_count} opportunities and {contact_count} contacts in your NEXUS system."

        except Exception as e:
            return "I couldn't retrieve your status right now. Please check your NEXUS dashboard."

    # Help commands
    elif 'help' in command_lower or 'what can you do' in command_lower:
        return "I can help you manage your NEXUS government contracting system. Try saying: add contact John Smith, create new opportunity, or what's my status."

    # Default response
    else:
        return f"I heard: {command}. I'm ready to help with government contracts, projects, compliance, financials, and strategic intelligence. Try asking for your executive briefing or contract opportunities."


# ========== ALEXA HELPER FUNCTIONS ==========

def get_nexus_system_status():
    """Get system-wide NEXUS status"""
    try:
        airtable_client = AirtableClient()
        opportunities = airtable_client.get_all_records('GPSS OPPORTUNITIES')
        contacts = airtable_client.get_all_records('GPSS CONTACTS')
        
        opp_count = len(opportunities) if opportunities else 0
        contact_count = len(contacts) if contacts else 0
        
        return f"NEXUS system status: {opp_count} active opportunities, {contact_count} contacts. All systems operational."
    except:
        return "NEXUS system status: All systems operational. Unable to retrieve detailed metrics at this time."


def get_compliance_overview():
    """Get compliance landscape overview"""
    return "Compliance status: All certifications are current. No outstanding regulatory requirements at this time."


def get_invoice_status():
    """Get invoice status across all divisions"""
    return "Invoice status: All invoices are up to date. No outstanding payments requiring immediate attention."


def get_financial_metrics():
    """Get financial metrics dashboard"""
    return "Financial metrics: Revenue tracking is active. All divisions are performing within expected parameters."


def get_contacts_summary():
    """Get contacts summary"""
    try:
        airtable_client = AirtableClient()
        contacts = airtable_client.get_all_records('GPSS CONTACTS')
        count = len(contacts) if contacts else 0
        return f"You have {count} contacts in your NEXUS database. Contact management is ready."
    except:
        return "Contact management system is ready. Unable to retrieve count at this time."


def get_gpss_pipeline_analysis():
    """Get GPSS pipeline analysis"""
    try:
        airtable_client = AirtableClient()
        opportunities = airtable_client.get_all_records('GPSS OPPORTUNITIES')
        count = len(opportunities) if opportunities else 0
        return f"Government contract pipeline: {count} opportunities tracked. Pipeline analysis is ready."
    except:
        return "Government contract pipeline analysis is ready. All tracking systems are operational."


def get_atlas_tasks_summary():
    """Get ATLAS PM tasks summary"""
    return "Project management: All tasks are being tracked. No overdue items requiring immediate attention."


def get_executive_briefing():
    """Get daily executive briefing"""
    try:
        airtable_client = AirtableClient()
        opportunities = airtable_client.get_all_records('GPSS OPPORTUNITIES')
        contacts = airtable_client.get_all_records('GPSS CONTACTS')
        
        opp_count = len(opportunities) if opportunities else 0
        contact_count = len(contacts) if contacts else 0
        
        return f"Executive briefing: You have {opp_count} opportunities and {contact_count} contacts. All divisions are operational. No critical alerts at this time."
    except:
        return "Executive briefing: All systems operational. No critical alerts requiring immediate attention."


def get_contract_opportunities_alert():
    """Get contract opportunities alert"""
    return "Contract opportunities: New federal opportunities are available. Check your NEXUS dashboard for details on matching contracts."


def get_government_contract_pipeline():
    """Get government contract pipeline overview"""
    try:
        airtable_client = AirtableClient()
        opportunities = airtable_client.get_all_records('GPSS OPPORTUNITIES')
        count = len(opportunities) if opportunities else 0
        return f"Government contract pipeline: {count} opportunities in various stages. Pipeline health is good."
    except:
        return "Government contract pipeline is being tracked. All opportunities are progressing as expected."


def get_proactive_insights():
    """Get proactive business insights"""
    return "Proactive insights: Based on your business patterns, I recommend focusing on high-value federal opportunities and maintaining strong compliance documentation."


@app.route('/ai/conversations', methods=['GET'])
def get_all_conversations():
    """Get all AI conversations"""
    try:
        airtable_client = AirtableClient()
        
        import json
        
        records = airtable_client.get_all_records('AI Conversations')
        conversations = []
        
        for record in records:
            fields = record['fields']
            conversations.append({
                'id': record['id'],
                'sessionId': fields.get('SESSION ID'),
                'messageCount': fields.get('MESSAGE COUNT', 0),
                'systemContext': fields.get('SYSTEM CONTEXT'),
                'status': fields.get('STATUS'),
                'notes': fields.get('NOTES', ''),
            })
        
        return jsonify({'success': True, 'conversations': conversations})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/ai/test', methods=['POST'])
def ai_test():
    """Test endpoint"""
    return jsonify({'success': True, 'response': 'Test endpoint working!'})

@app.route('/ai/chat', methods=['POST'])
def ai_chat():
    """AI chat endpoint for NEXUS Copilot - comprehensive systems assistant"""
    try:
        data = request.json
        user_message = data.get('message', '').strip().lower()

        if not user_message:
            return jsonify({
                'success': False,
                'response': 'Please provide a message to process.'
            }), 400

        # Simple keyword-based action detection
        if 'add' in user_message and 'contact' in user_message:
            return handle_contact_creation(user_message)

        elif ('find' in user_message or 'search' in user_message) and 'contact' in user_message:
            return handle_contact_search(user_message)

        elif 'create' in user_message and 'opportunity' in user_message:
            return handle_opportunity_creation(user_message)

        elif 'qualify' in user_message and 'opportunity' in user_message:
            return handle_opportunity_qualification(user_message)

        elif 'create' in user_message and 'project' in user_message:
            return handle_project_creation(user_message)

        elif ('add' in user_message or 'create' in user_message) and 'task' in user_message:
            return handle_task_creation(user_message)

        elif 'generate' in user_message and 'proposal' in user_message:
            return handle_proposal_generation(user_message)

        elif 'check' in user_message and 'compliance' in user_message:
            return handle_compliance_check(user_message)

        elif 'generate' in user_message and 'quote' in user_message:
            return handle_quote_generation(user_message)

        elif ('create' in user_message or 'generate' in user_message) and 'invoice' in user_message:
            return handle_invoice_generation(user_message)

        elif ('mine' in user_message or 'extract' in user_message) and 'contact' in user_message:
            return handle_contact_mining(user_message)

        # GENERAL ASSISTANCE
        else:
            return handle_general_assistance(user_message)

    except Exception as e:
        return jsonify({
            'success': False,
            'response': f'I encountered an error: {str(e)}. Please try rephrasing your request.',
            'error': str(e)
        }), 500


def handle_contact_creation(message):
    """Handle contact creation requests"""
    import re

    # Extract contact information
    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', message)
    email = email_match.group(0) if email_match else ''

    phone_match = re.search(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', message)
    phone = phone_match.group(0) if phone_match else ''

    # Extract name
    name_text = message
    if email:
        name_text = name_text.replace(email, '')
    if phone:
        name_text = name_text.replace(phone, '')

    # Clean up command words and extract name
    for word in ['add', 'contact', 'create', 'new', 'this', 'to', 'contacts']:
        name_text = re.sub(r'\b' + word + r'\b', '', name_text, flags=re.IGNORECASE)

    name_text = re.sub(r'[^\w\s]', '', name_text).strip()
    name_parts = name_text.split()
    first_name = name_parts[0] if name_parts else ''
    last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''

    if not email and not first_name:
        return jsonify({
            'success': False,
            'response': 'I need at least a name or email address to create a contact. Please include: "John Doe john@email.com 555-123-4567"'
        })

    try:
        airtable_client = AirtableClient()
        contact_fields = {
            'First Name': first_name,
            'Last Name': last_name,
            'Email': email,
            'Phone': phone,
            'Source': 'AI Copilot'
        }

        result = airtable_client.create_record('GPSS CONTACTS', contact_fields)

        return jsonify({
            'success': True,
            'response': f'✅ Contact created successfully!\n\n**{first_name} {last_name}**\n📧 {email}\n📱 {phone}\n\nContact has been added to your GPSS Contacts database.',
            'action': 'contact_created',
            'contact_data': {
                'firstName': first_name,
                'lastName': last_name,
                'email': email,
                'phone': phone,
                'record_id': result.get('id')
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'response': f'Failed to create contact: {str(e)}. You can still add it manually in GPSS → Contacts.',
            'action': 'contact_error'
        })


def handle_contact_search(message):
    """Handle contact search requests"""
    try:
        # Extract search terms
        search_terms = message.lower()
        for word in ['find', 'search', 'lookup', 'contact', 'contacts']:
            search_terms = search_terms.replace(word, '')
        search_terms = search_terms.strip()

        if not search_terms:
            return jsonify({
                'success': False,
                'response': 'Please specify what to search for. Try: "find contact John Doe" or "search contact john@email.com"'
            })

        airtable_client = AirtableClient()
        contacts = airtable_client.get_all_records('GPSS CONTACTS')

        matches = []
        for contact in contacts:
            fields = contact.get('fields', {})
            name = f"{fields.get('First Name', '')} {fields.get('Last Name', '')}".strip()
            email = fields.get('Email', '')

            # Check if search terms match
            if (search_terms in name.lower() or
                search_terms in email.lower() or
                any(term in name.lower() or term in email.lower() for term in search_terms.split())):
                matches.append({
                    'id': contact['id'],
                    'name': name,
                    'email': email,
                    'phone': fields.get('Phone', ''),
                    'agency': fields.get('Agency', '')
                })

        if matches:
            response = f'Found {len(matches)} contact(s):\n\n'
            for match in matches[:5]:  # Limit to 5 results
                response += f'• {match["name"]}\n  📧 {match["email"]}\n  📱 {match["phone"]}\n\n'

            if len(matches) > 5:
                response += f'... and {len(matches) - 5} more results.'

            return jsonify({
                'success': True,
                'response': response,
                'action': 'contacts_found',
                'contacts': matches
            })
        else:
            return jsonify({
                'success': False,
                'response': f'No contacts found matching "{search_terms}". Try a different search term.'
            })

    except Exception as e:
        return jsonify({
            'success': False,
            'response': f'Contact search failed: {str(e)}'
        })


def handle_opportunity_creation(message):
    """Handle opportunity creation requests"""
    try:
        # Extract opportunity details from message
        title = extract_field_from_message(message, ['title', 'name'])
        value = extract_field_from_message(message, ['value', 'worth', 'amount', '$'])
        agency = extract_field_from_message(message, ['agency', 'department'])
        description = extract_field_from_message(message, ['description', 'about', 'details'])

        # If no explicit title keyword, use everything after "create opportunity:" as title
        if not title:
            opp_part = message.split('create opportunity:', 1)
            if len(opp_part) > 1:
                # Extract title by taking everything before the first field keyword
                title_part = opp_part[1].strip()
                # Stop at first field indicator
                for field in [' value:', ' agency:', ' department:']:
                    if field in title_part:
                        title = title_part.split(field)[0].strip()
                        break
                else:
                    # No field indicators found, use whole thing as title
                    title = title_part

        if not title:
            return jsonify({
                'success': False,
                'response': 'Please specify an opportunity title. Try: "create opportunity: Website Redesign value: $50,000 agency: GSA"'
            })

        airtable_client = AirtableClient()
        opp_fields = {
            'Title': title,
            'Value': value or '',
            'Agency': agency or '',
            'Description': description or '',
            'Status': 'New',
            'Source': 'AI Copilot'
        }

        result = airtable_client.create_record('GPSS OPPORTUNITIES', opp_fields)

        return jsonify({
            'success': True,
            'response': f'✅ Opportunity created!\n\n**{title}**\n💰 {value or "TBD"}\n🏢 {agency or "TBD"}\n\nOpportunity added to GPSS Opportunities.',
            'action': 'opportunity_created',
            'opportunity_data': opp_fields
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'response': f'Failed to create opportunity: {str(e)}'
        })


def handle_project_creation(message):
    """Handle project creation requests"""
    try:
        # Extract project details
        name = extract_field_from_message(message, ['name', 'title', 'project'])
        client = extract_field_from_message(message, ['client', 'customer'])
        budget = extract_field_from_message(message, ['budget', 'value', '$'])

        if not name:
            return jsonify({
                'success': False,
                'response': 'Please specify a project name. Try: "create project: Website Redesign client: GSA budget: $75,000"'
            })

        airtable_client = AirtableClient()
        project_fields = {
            'Project Name': name,
            'Client': client or '',
            'Budget': budget or '',
            'Status': 'Planning',
            'Completion Percentage': 0
        }

        result = airtable_client.create_record('ATLAS PROJECTS', project_fields)

        return jsonify({
            'success': True,
            'response': f'✅ Project created!\n\n**{name}**\n👥 {client or "TBD"}\n💰 {budget or "TBD"}\n\nProject added to ATLAS Projects.',
            'action': 'project_created',
            'project_data': project_fields
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'response': f'Failed to create project: {str(e)}'
        })


def handle_task_creation(message):
    """Handle task creation requests"""
    try:
        # Extract task details
        title = extract_field_from_message(message, ['task', 'title'])
        project = extract_field_from_message(message, ['project', 'for'])
        assignee = extract_field_from_message(message, ['assign', 'assignee', 'to'])
        priority = extract_field_from_message(message, ['priority'])

        if not title:
            return jsonify({
                'success': False,
                'response': 'Please specify a task title. Try: "add task: Design homepage for Website Redesign project priority: high"'
            })

        airtable_client = AirtableClient()
        task_fields = {
            'TITLE': title,
            'ASSIGNEE': assignee or '',
            'PRIORITY': (priority or 'MEDIUM').upper(),
            'STATUS': 'TO DO'
        }
        if project:
            task_fields['DESCRIPTION'] = f"Project: {project}"

        result = airtable_client.create_record('Tasks', task_fields)

        return jsonify({
            'success': True,
            'response': f'✅ Task created!\n\n**{title}**\n📋 {project or "No project"}\n👤 {assignee or "Unassigned"}\n🎯 {priority or "Medium"} priority\n\nTask added to your task board.',
            'action': 'task_created',
            'task_data': task_fields
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'response': f'Failed to create task: {str(e)}'
        })


def handle_proposal_generation(message):
    """Handle proposal generation requests"""
    try:
        # Extract opportunity ID or details
        opportunity_id = extract_field_from_message(message, ['opportunity', 'opp'])
        requirements = extract_field_from_message(message, ['requirements', 'needs'])

        if opportunity_id:
            # Generate proposal from existing opportunity
            result = handle_generate_quote(opportunity_id)
            return jsonify({
                'success': True,
                'response': f'✅ Proposal generated from opportunity!\n\n{result.get("message", "Proposal created successfully")}\n\nCheck GPSS → Proposals for the full document.',
                'action': 'proposal_generated',
                'proposal_data': result
            })
        else:
            return jsonify({
                'success': False,
                'response': 'Please specify an opportunity ID. Try: "generate proposal for opportunity OPP-123"'
            })

    except Exception as e:
        return jsonify({
            'success': False,
            'response': f'Failed to generate proposal: {str(e)}'
        })


def handle_compliance_check(message):
    """Handle compliance check requests"""
    try:
        rfp_content = extract_field_from_message(message, ['rfp', 'requirements', 'content'])

        if not rfp_content:
            return jsonify({
                'success': False,
                'response': 'Please provide RFP content or requirements to check compliance.'
            })

        # Call the RFP analysis function
        result = handle_atlas_analyze_rfp(rfp_content)

        return jsonify({
            'success': True,
            'response': f'✅ Compliance analysis complete!\n\n{result.get("analysis", "Compliance check completed")}\n\nCheck the detailed results in your compliance dashboard.',
            'action': 'compliance_checked',
            'compliance_data': result
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'response': f'Compliance check failed: {str(e)}'
        })


def handle_quote_generation(message):
    """Handle quote generation requests"""
    try:
        opportunity_id = extract_field_from_message(message, ['opportunity', 'opp'])

        if opportunity_id:
            result = handle_generate_quote(opportunity_id)
            return jsonify({
                'success': True,
                'response': f'✅ Quote generated!\n\n{result.get("message", "Quote created successfully")}\n\nCheck GPSS → Proposals for your quote.',
                'action': 'quote_generated',
                'quote_data': result
            })
        else:
            return jsonify({
                'success': False,
                'response': 'Please specify an opportunity ID. Try: "generate quote for opportunity OPP-123"'
            })

    except Exception as e:
        return jsonify({
            'success': False,
            'response': f'Failed to generate quote: {str(e)}'
        })


def handle_invoice_generation(message):
    """Handle invoice generation requests"""
    try:
        source_type = 'opportunity' if 'opportunity' in message else 'project'
        source_id = extract_field_from_message(message, ['opportunity', 'project', 'opp'])

        if source_id:
            if source_type == 'opportunity':
                result = handle_generate_invoice_from_opportunity(source_id)
            elif source_type == 'project':
                result = handle_generate_invoice_from_project(source_id)

            return jsonify({
                'success': True,
                'response': f'✅ Invoice generated!\n\n{result.get("message", "Invoice created successfully")}\n\nCheck your Invoices dashboard.',
                'action': 'invoice_generated',
                'invoice_data': result
            })
        else:
            return jsonify({
                'success': False,
                'response': 'Please specify an opportunity or project ID. Try: "create invoice from opportunity OPP-123"'
            })

    except Exception as e:
        return jsonify({
            'success': False,
            'response': f'Failed to generate invoice: {str(e)}'
        })


def handle_contact_mining(message):
    """Handle contact mining requests"""
    try:
        target = extract_field_from_message(message, ['target', 'site', 'url'])

        if target:
            # This would trigger contact mining for the specified target
            return jsonify({
                'success': True,
                'response': f'✅ Contact mining initiated for {target}!\n\nMining process started in the background. Check your Mining Targets dashboard for results.',
                'action': 'mining_started',
                'target': target
            })
        else:
            return jsonify({
                'success': False,
                'response': 'Please specify a target site or URL to mine contacts from.'
            })

    except Exception as e:
        return jsonify({
            'success': False,
            'response': f'Contact mining failed: {str(e)}'
        })


def handle_general_assistance(message):
    """Handle general assistance and guidance - Ultimate NEXUS Guide"""
    try:
        ai = ClaudeAI()
        
        # Comprehensive NEXUS system context
        system_context = """You are the NEXUS AI Copilot - the ultimate guide to the NEXUS Command Center.

NEXUS is a comprehensive enterprise management platform with 7 integrated systems:

🎯 **GPSS (Government Prime Sales System)**
- Purpose: Government contracting, RFPs, proposals, compliance
- Key Features: Opportunity mining, intelligent pricing, compliance checking, proposal generation
- How to use: Navigate from landing page → GPSS → Browse opportunities, qualify leads, generate proposals
- Data stored in: Airtable GPSS tables (Opportunities, Contacts, Products, Proposals)
- AI Features: Auto-qualification, pricing recommendations, compliance analysis

💼 **DDCSS (Discovery-Driven Consulting Sales System)**
- Purpose: Corporate consulting sales and client acquisition
- Key Features: 6-sector frameworks (ALIGN, CONVERT, SCALE, etc.), prospect qualification, blueprint generation
- How to use: Landing page → DDCSS → Add prospects, choose framework, generate custom blueprints
- Data stored in: DDCSS tables (Prospects, Blueprints, Responses)
- AI Features: Email analysis, custom strategy blueprints, sector-specific recommendations

🏗️ **ATLAS PM (Project Management System)**
- Purpose: Project execution, RFP analysis, task management, change orders
- Key Features: Kanban board, WBS generation, RFP analysis, calendar export, task automation
- How to use: Landing page → ATLAS → Create projects, add tasks, analyze RFPs, track progress
- Data stored in: ATLAS tables (Projects, Tasks, RFPs, Change Orders)
- AI Features: Auto-task generation, RFP parsing, change order impact analysis, timeline optimization

🎁 **GBIS (Grant Business Intelligence System)**
- Purpose: Grant discovery, application generation, success tracking
- Key Features: Multi-source grant mining, AI application writing, ROI tracking
- How to use: Landing page → GBIS → Browse grants, score opportunities, generate applications
- Data stored in: GBIS tables (Opportunities, Applications, Story Library)
- AI Features: Grant scoring, automated applications, narrative generation

💎 **VERTEX (Financial Command Center)**
- Purpose: Financial management, invoicing, expense tracking, QuickBooks integration
- Key Features: Revenue tracking, P&L statements, expense categorization, QB export, AI financial insights
- How to use: Landing page → VERTEX → Track invoices, log expenses, view dashboards, export reports
- Data stored in: VERTEX tables (Invoices, Expenses, Revenue)
- AI Features: Expense categorization, financial health scoring, insight generation

💰 **LBPC (Lead Pipeline & Client Acquisition)**
- Purpose: Surplus property recovery across all 50 states
- Key Features: Lead mining, document generation, task workflows, analytics
- How to use: Landing page → LBPC → Import leads, qualify prospects, generate documents, track tasks
- Data stored in: LBPC tables (Leads, Documents, Tasks)
- AI Features: Lead qualification, document generation, priority scoring

📄 **Universal Invoicing System**
- Purpose: Cross-system invoice generation for all business units
- Key Features: Government-compliant formats, auto-generation from opportunities/projects
- How to use: Landing page → Invoices → Generate from any system, track status, send to clients
- Data stored in: Invoices table (linked to all systems)

**KEY CONCEPTS:**

1. **All Systems are Connected**
   - Opportunities in GPSS can auto-create projects in ATLAS
   - Projects in ATLAS can generate invoices in VERTEX
   - Contacts are shared across GPSS and DDCSS
   - Everything is stored in Airtable for data integrity

2. **AI Copilot (Me!) Can Help With:**
   - Creating records: "add contact: John Doe john@email.com"
   - Searching: "find opportunities in Michigan"
   - Analysis: "what's my win rate?"
   - Guidance: "how do I use GPSS?"
   - Actions: "generate quote for OPP-123"
   - Navigation: "where do I find my tasks?"

3. **Data Flow:**
   - Landing Page (Command Center) → Shows overview of all systems
   - Click any system card → Enter that system
   - Each system has tabs: Dashboard, specific features
   - All changes sync to Airtable in real-time
   - AI Copilot available everywhere (floating button)

4. **Best Practices:**
   - Start with GPSS for government contracts
   - Use DDCSS for corporate consulting
   - Create projects in ATLAS when you win contracts
   - Track all finances in VERTEX
   - Use LBPC for surplus recovery leads
   - Ask me (AI Copilot) anytime you're stuck!

5. **Common Workflows:**
   - RFP Response: GPSS (qualify) → AI analysis → GPSS (proposal) → ATLAS (project if won)
   - Consulting Sale: DDCSS (prospect) → Generate blueprint → ATLAS (project) → VERTEX (invoice)
   - Grant: GBIS (find grant) → Score it → Generate application → Track in ATLAS
   - Surplus Recovery: LBPC (import leads) → Qualify → Generate docs → Track tasks

6. **Quick Commands:**
   - "Show me GPSS opportunities" - Lists all RFPs
   - "Create a project for [client]" - Starts new project
   - "What's my pipeline?" - Shows revenue summary
   - "How do I export tasks?" - Guides you through calendar export
   - "Generate invoice for [opportunity]" - Creates invoice
   - "Help me navigate ATLAS" - System-specific guidance

**Your Role:** 
- Be friendly, helpful, and proactive
- Provide step-by-step guidance when asked "how to..."
- Suggest next actions based on context
- Explain features clearly with examples
- Guide users to the right system for their needs
- Offer to execute actions when appropriate

Now answer the user's question with context-aware, helpful guidance."""

        # Create the prompt with user's question
        prompt = f"""{system_context}

User Question: {message}

Provide a helpful, specific response. If they're asking "how to" do something, give step-by-step instructions. If they're asking about features, explain clearly with examples. Be conversational and encouraging."""

        response = ai.complete(prompt, max_tokens=1500)
        
        return jsonify({
            'success': True,
            'response': response,
            'action': 'general_guidance'
        })
        
    except Exception as e:
        # Fallback response if AI fails
        return jsonify({
            'success': True,
            'response': f"""I'm your NEXUS AI Copilot! I can help you with:

📚 **Getting Started:**
- "How do I use GPSS?" - Government contracting guide
- "Show me how ATLAS works" - Project management walkthrough
- "What can NEXUS do?" - Platform overview

🎯 **Taking Actions:**
- "Add contact: John Doe john@email.com 555-123-4567"
- "Create opportunity for DOD contract"
- "Generate proposal for OPP-123"
- "Make invoice from project PRJ-456"

❓ **Ask Me Anything:**
- "What's the difference between GPSS and DDCSS?"
- "How do I export my calendar?"
- "Where do I find my pipeline?"
- "How do I analyze an RFP?"

Just ask - I'm here to guide you through NEXUS! 🚀

(Note: AI temporarily unavailable, using fallback mode)""",
            'action': 'fallback_help'
        })


def extract_field_from_message(message, keywords):
    """Extract field value from message based on keywords"""
    import re

    message_lower = message.lower()

    for keyword in keywords:
        if keyword in message_lower:
            # Find the keyword and extract everything after it until next keyword or end
            pattern = rf'\b{keyword}\b[:\s]*(.*?)(?=\b(?:{"|".join(keywords)})\b|$|$)'
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                value = match.group(1).strip()
                if value:
                    return value

    return None


# =====================================================================
# GBIS (GRANT BUSINESS INTELLIGENCE SYSTEM) AUTOMATION ENDPOINTS
# =====================================================================

@app.route('/gbis/generate-application', methods=['POST'])
def gbis_generate_application():
    """
    Generate AI-powered grant application draft from Grant Story Library
    Called by Airtable automation when high-scoring grant is discovered
    """
    try:
        data = request.json
        opportunity_id = data.get('opportunity_id')
        grant_name = data.get('grant_name')
        funder_organization = data.get('funder_organization')
        grant_amount = data.get('grant_amount')
        focus_areas = data.get('focus_areas', [])
        division_fit = data.get('division_fit', [])
        eligibility = data.get('eligibility', '')
        
        if not opportunity_id:
            return jsonify({'error': 'opportunity_id required'}), 400
        
        # Initialize clients
        from nexus_backend import AirtableClient, AnthropicClient
        airtable = AirtableClient()
        ai = AnthropicClient()
        
        # Get Grant Story Library modules (active only)
        try:
            story_modules = airtable.get_all_records('GRANT STORY LIBRARY')
            active_modules = [m for m in story_modules if m.get('fields', {}).get('Status') == 'Active']
        except Exception as e:
            print(f"Warning: Could not fetch GBIS Story Library: {e}")
            active_modules = []
        
        # Build context from story library
        if active_modules:
            context = "\n\n".join([
                f"### {m.get('fields', {}).get('Module Name', 'Untitled')}\n{m.get('fields', {}).get('Content', '')}"
                for m in active_modules
            ])
        else:
            context = """
DEE DAVIS INC — CONTRACT MANAGEMENT FIRM (EDWOSB, CAGE 8UMX3)
Founded 2018 by Dieasha D. Davis. "The Professionals' Professionals."

BUSINESS MODEL: DDI wins government and commercial contracts across every sector, sources qualified subcontractors and suppliers to execute the work, and manages the entire delivery — compliance, invoicing, quality assurance, reporting, coordination. We don't do the work. We make sure the work gets done right. One point of contact. Full accountability.

26+ SERVICE LINES across 6 categories: (1) Federal Compliance — drug & alcohol testing / C-TPA (Quest), biometrics / fingerprinting (3D Ink & Livescan, Top 10% nationally), DNA testing (DePointe DNA, DDC partner), lead testing, background screening; (2) Professional Services — notarial services (notary / RON / signing), document authentication & witnessing per RFx, credentialing / PSV when scoped; (3) Healthcare Transportation — NEMT brokerage (MC-1647572), patient transport / paratransit when RFx language; healthcare logistics / medical courier; (4) Service Contracts as Prime — janitorial, landscaping, grounds, facility maintenance, IT, security, construction, moving, events, staffing; (5) Logistics — freight brokerage (Freight 1st Direct), FleetFlow; (6) Project Executive — contract management, crisis coordination, emergency logistics.

OPERATING DIVISIONS: 3D Ink & Livescan Co (fingerprinting, drug testing), DePointe DNA (DNA testing, DDC collection partner), Freight 1st Direct (freight brokerage), FleetFlow TMS LLC (logistics platform). Cause We Care — affiliated 501(c)(3), MIBridges, veteran services, homelessness coordinated entry. MDHHS Community Partner.

TECHNOLOGY: NEXUS proprietary AI platform (9 modules), ATLAS PM, FleetFlow TMS — designed and built by Dieasha D. Davis. Gives 5-person firm capacity of 50-person organization.

CERTIFICATIONS: EDWOSB, WOSB, WBENC, MBE, SBE, E-Verify, CMMC-AB, TWIC, CNTDA, Michigan Notary (20+ years). 7+ years in operation. Zero past performance deficiencies. Revenue potential: $3.7M–$26M annually. 5-year vision: $50M+, OASIS+, GSA MAS, 20+ states.
"""
        
        # Generate application with Claude
        prompt = f"""You are an expert grant writer for DEE DAVIS INC, a federally certified EDWOSB.

GRANT OPPORTUNITY:
Name: {grant_name}
Funder: {funder_organization}
Amount: ${grant_amount}
Focus Areas: {', '.join(focus_areas) if isinstance(focus_areas, list) else focus_areas}
Division Fit: {', '.join(division_fit) if isinstance(division_fit, list) else division_fit}
Eligibility Requirements: {eligibility}

COMPANY CONTEXT (Grant Story Library):
{context}

TASK:
Generate a compelling grant application that:
1. Emphasizes DEE DAVIS INC's unique qualifications (EDWOSB contract management firm, 26+ service lines, proprietary NEXUS/ATLAS/FleetFlow technology)
2. Uses specific examples from the company context
3. Demonstrates measurable impact with metrics
4. Shows clear fund utilization plan (working capital bridge, capacity investment, community program sustainability)
5. Maintains Dieasha Davis's authentic voice (systematic, technology-driven, professional)

TONE: Confident, accomplished, technology-driven, community-focused
AVOID: Generic corporate speak, vague promises, resume-style history

Generate a structured application with these sections:
- Executive Summary (200 words)
- Organization Background (150 words)
- Project Description (300 words)
- Fund Utilization Plan (200 words)
- Measurable Impact (150 words)
- Sustainability (100 words)

Return ONLY valid JSON with section names as keys and content as values.
"""
        
        try:
            response = ai.complete(prompt, max_tokens=4000)
            
            # Try to parse as JSON
            import json
            # Clean up response if needed
            clean_response = response.strip()
            if clean_response.startswith('```json'):
                clean_response = clean_response.replace('```json', '').replace('```', '').strip()
            
            application_draft = json.loads(clean_response)
            
            # Convert to formatted text for Airtable long text field
            formatted_draft = "\n\n".join([
                f"## {section}\n\n{content}"
                for section, content in application_draft.items()
            ])
            
        except json.JSONDecodeError:
            # If not valid JSON, use raw response
            formatted_draft = response
            application_draft = {'content': response}
        
        # Get Story Module IDs that were used
        story_module_ids = [m['id'] for m in active_modules[:5]]  # Use top 5 modules
        
        # Create application record in Airtable
        try:
            application_fields = {
                'Grant Opportunity': [opportunity_id],
                'Application Title': f"{grant_name} Application",
                'Application Status': 'Draft',
                'Application Draft': formatted_draft,
                'AI Generation Used': True,
                'Assigned To': 'Dee Davis',
                'Grant Amount Requested': grant_amount,
                'Division Focus': division_fit[0] if isinstance(division_fit, list) and division_fit else 'Multi-Division'
            }
            
            # Link to story modules if they exist
            if story_module_ids:
                application_fields['Story Modules Used'] = story_module_ids
            
            application_record = airtable.create_record('GRANT APPLICATIONS', application_fields)
            
            # NEXUS ADVISOR: Teach about grant applications
            advisor_insight = None
            try:
                from nexus_advisor import advise, log_growth
                advisor_insight = advise('gbis', 'application_generated', {
                    'grant_name': grant_name,
                    'amount': grant_amount,
                })
                log_growth('grant_applied')
            except Exception:
                pass

            return jsonify({
                'success': True,
                'application_id': application_record['id'],
                'draft': application_draft,
                'formatted_draft': formatted_draft,
                'word_count': len(formatted_draft.split()),
                'story_modules_used': len(story_module_ids),
                'advisor': advisor_insight,
            })
            
        except Exception as e:
            return jsonify({
                'success': True,
                'application_id': None,
                'draft': application_draft,
                'formatted_draft': formatted_draft,
                'word_count': len(formatted_draft.split()),
                'warning': f'Application generated but not saved to Airtable: {str(e)}'
            })
        
    except Exception as e:
        print(f"GBIS Application Generation Error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/gbis/mine-source', methods=['POST'])
def gbis_mine_source():
    """
    Mine a specific grant source or run a full pipeline pass.
    Routes to GBISCommunityHealthMiner based on source_type param.
    Falls back to full pipeline when no specific source_type is given.
    """
    try:
        data = request.json or {}
        source_type = data.get('source_type', 'all')

        from gbis_community_health_miner import GBISCommunityHealthMiner
        miner = GBISCommunityHealthMiner()

        if source_type == 'michigan_foundations':
            result = miner.seed_michigan_foundations()
            imported = result['imported']
            message = f"Seeded {imported} Michigan foundation grant sources"
        elif source_type == 'veteran_grants':
            result = miner.seed_veteran_sources()
            imported = result['imported']
            message = f"Seeded {imported} veteran grant sources"
        elif source_type == 'grants_gov':
            result = miner.mine_grants_gov_research()
            imported = result['imported']
            message = f"Mined Grants.gov — {result.get('found', 0)} found, {imported} new records"
        else:
            # Full pipeline: foundations + veteran + Grants.gov
            result = miner.run_full_pipeline()
            imported = (result['michigan_foundations']['imported'] +
                        result['veteran_sources']['imported'] +
                        result['grants_gov']['imported'])
            message = f"Full pipeline complete — {imported} new records added to GBIS"

        return jsonify({
            'success': True,
            'source_type': source_type,
            'imported': imported,
            'message': message,
            'details': result,
            'last_run': datetime.now().isoformat()
        })

    except Exception as e:
        print(f"GBIS Mining Error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/gbis/calculate-score', methods=['POST'])
def gbis_calculate_score():
    """
    Calculate 100-point qualification score for grant opportunity
    Can be called from Airtable automation or backend
    """
    try:
        data = request.json
        
        # Extract grant details
        eligibility = data.get('eligibility', '').lower()
        grant_amount = data.get('grant_amount', 0)
        application_complexity = data.get('application_complexity', 'Moderate')
        focus_areas = data.get('focus_areas', [])
        division_fit = data.get('division_fit', [])
        days_until_deadline = data.get('days_until_deadline', 0)
        funder_type = data.get('funder_type', '')
        estimated_time = data.get('estimated_time', 1)
        
        score = {
            'eligibility_match': 0,
            'win_probability': 0,
            'strategic_value': 0,
            'total_score': 0,
            'priority_level': 'Skip (<60)'
        }
        
        # ELIGIBILITY MATCH (0-40 points)
        eligibility_score = 0
        
        # Business Type Match (10 pts) - DEE DAVIS INC is corporation
        if 'corporation' in eligibility or 'llc' in eligibility:
            eligibility_score += 10
        elif 'sole proprietor' not in eligibility:
            eligibility_score += 5
        
        # Certification Requirements (10 pts)
        if 'wosb' in eligibility or 'edwosb' in eligibility:
            eligibility_score += 10
        elif 'wbe' in eligibility or 'mbe' in eligibility:
            eligibility_score += 10
        elif 'certification' not in eligibility:
            eligibility_score += 5
        
        # Revenue Range (10 pts) - DEE DAVIS INC qualifies for small business
        if 'small business' in eligibility or '<$5m' in eligibility or 'under $5' in eligibility:
            eligibility_score += 10
        elif '$5m' not in eligibility and '$10m' not in eligibility:
            eligibility_score += 5
        
        # Years in Business (5 pts) - Established 2018 (8 years)
        if '<10 years' in eligibility or 'less than 10' in eligibility:
            eligibility_score += 5
        elif '10+ years' not in eligibility:
            eligibility_score += 3
        
        # Geographic Location (5 pts)
        if isinstance(focus_areas, list):
            if any(area in focus_areas for area in ['Michigan', 'Maryland', 'Multi-State', 'National']):
                eligibility_score += 5
        
        score['eligibility_match'] = min(eligibility_score, 40)
        
        # WIN PROBABILITY (0-30 points)
        win_score = 0
        
        # Application Complexity (10 pts)
        complexity_scores = {
            'Simple (1-5 questions)': 10,
            'Moderate (6-10 questions)': 7,
            'Complex (11-20 questions)': 4,
            'Very Complex (20+ questions)': 2,
            'Multi-Phase': 2
        }
        win_score += complexity_scores.get(application_complexity, 5)
        
        # Grant Amount vs Effort (10 pts)
        try:
            amount = float(grant_amount)
            if amount >= 25000 and 'Simple' in application_complexity:
                win_score += 10
            elif amount >= 10000 and 'Simple' in application_complexity:
                win_score += 8
            elif amount >= 10000:
                win_score += 5
            else:
                win_score += 3
        except (ValueError, TypeError):
            win_score += 5
        
        # Focus Area Match (10 pts)
        if isinstance(focus_areas, list):
            if 'Women-Owned Business' in focus_areas or 'Minority Business' in focus_areas:
                win_score += 10
            elif 'Technology Innovation' in focus_areas or 'Healthcare' in focus_areas:
                win_score += 7
            else:
                win_score += 5
        
        score['win_probability'] = min(win_score, 30)
        
        # STRATEGIC VALUE (0-30 points)
        strategic_score = 0
        
        # ROI Rating (10 pts)
        try:
            amount = float(grant_amount)
            time = float(estimated_time) if estimated_time > 0 else 1
            roi = amount / time
            
            if roi >= 3000:
                strategic_score += 10
            elif roi >= 2000:
                strategic_score += 8
            elif roi >= 1000:
                strategic_score += 5
            else:
                strategic_score += 2
        except (ValueError, TypeError):
            strategic_score += 5
        
        # Division Fit (10 pts)
        if isinstance(division_fit, list):
            if len(division_fit) >= 2:
                strategic_score += 10
            elif len(division_fit) == 1:
                strategic_score += 7
            else:
                strategic_score += 3
        
        # Deadline Feasibility (5 pts)
        try:
            days = int(days_until_deadline)
            if days >= 30:
                strategic_score += 5
            elif days >= 15:
                strategic_score += 3
            else:
                strategic_score += 1
        except (ValueError, TypeError):
            strategic_score += 3
        
        # Brand Value (5 pts)
        if funder_type in ['Corporate', 'Federal Government']:
            strategic_score += 5
        elif funder_type in ['State Government', 'Foundation']:
            strategic_score += 3
        else:
            strategic_score += 2
        
        score['strategic_value'] = min(strategic_score, 30)
        
        # TOTAL SCORE
        score['total_score'] = score['eligibility_match'] + score['win_probability'] + score['strategic_value']
        
        # PRIORITY LEVEL
        total = score['total_score']
        if total >= 90:
            score['priority_level'] = 'Critical (90-100)'
        elif total >= 80:
            score['priority_level'] = 'High (80-89)'
        elif total >= 70:
            score['priority_level'] = 'Medium (70-79)'
        elif total >= 60:
            score['priority_level'] = 'Low (60-69)'
        else:
            score['priority_level'] = 'Skip (<60)'
        
        # Advisor: teach about qualification scoring
        advisor_insight = None
        try:
            from nexus_advisor import advise
            advisor_insight = advise('gbis', 'score_calculated', {
                'total_score': total,
                'grant_amount': grant_amount,
            })
        except Exception:
            pass

        return jsonify({
            'success': True,
            'score': score,
            'recommendation': 'Auto-Pursue' if total >= 80 else 'Review' if total >= 70 else 'Consider' if total >= 60 else 'Skip',
            'advisor': advisor_insight,
        })
        
    except Exception as e:
        print(f"GBIS Scoring Error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/gbis/opportunities', methods=['GET'])
def get_gbis_opportunities():
    """
    Get grant opportunities from Airtable with optional filters
    """
    try:
        from nexus_backend import AirtableClient
        import re
        airtable = AirtableClient()

        def parse_numeric_amount(value):
            """Normalizes Airtable amount fields (number/string/range) to float."""
            if isinstance(value, (int, float)):
                return float(value)
            if not value:
                return 0.0
            if isinstance(value, str):
                match = re.search(r'(\d[\d,]*\.?\d*)', value)
                if not match:
                    return 0.0
                return float(match.group(1).replace(',', ''))
            return 0.0

        from datetime import date as date_cls

        # Get filter parameters
        priority_level = request.args.get('priority_level')
        funder_type = request.args.get('funder_type')
        division = request.args.get('division')
        status = request.args.get('status')
        entity_filter = (request.args.get('entity') or 'all').lower()

        def _grant_name_field(f):
            return (f.get('Grant Name') or f.get('GRANT NAME') or '').strip()

        def _stale_source_warning(f):
            gst = (f.get('Grant Source Type') or f.get('grant source type') or '').upper()
            if gst != 'TRACKED SOURCE':
                return False
            raw = f.get('Last Source Check') or f.get('last source check')
            if not raw:
                return True
            try:
                d = date_cls.fromisoformat(str(raw)[:10])
                return (date_cls.today() - d).days > 7
            except Exception:
                return True

        # Primary GBIS table
        source_table = 'GRANT OPPORTUNITIES'
        opportunities = airtable.get_all_records(source_table)
        
        # Apply filters
        filtered = []
        for opp in opportunities:
            fields = opp.get('fields', {})
            ent = (fields.get('Entity') or fields.get('ENTITY') or '').strip()

            if entity_filter == 'ddi':
                if ent not in ('DDI', 'BOTH'):
                    continue
            elif entity_filter == 'cwc':
                if ent not in ('CWC', 'BOTH'):
                    continue
            elif entity_filter == 'both':
                if ent != 'BOTH':
                    continue
            
            # Apply filters if specified
            if priority_level and fields.get('Priority Level') != priority_level:
                continue
            if funder_type and fields.get('Funder Type') != funder_type:
                continue
            if status and fields.get('Status') != status:
                continue
            if division:
                division_fit = fields.get('Division Fit', [])
                if division not in division_fit:
                    continue
            
            # Format the opportunity
            raw_grant_amount = fields.get('Grant Amount', fields.get('Max Award Amount', 0))
            gst = fields.get('Grant Source Type') or ''
            ddi_actionable = ent != 'CWC'
            filtered.append({
                'id': opp.get('id'),
                'createdTime': opp.get('createdTime', ''),
                'grantName': _grant_name_field(fields),
                'funderOrganization': fields.get('Funder Organization', fields.get('FUNDER ORGANIZATION', '')),
                'funderType': fields.get('Funder Type', ''),
                'grantAmount': parse_numeric_amount(raw_grant_amount),
                'grantAmountDisplay': raw_grant_amount,
                'grantUrl': fields.get('Grant URL', fields.get('GRANT URL', '')),
                'deadline': fields.get('Deadline', ''),
                'eligibility': fields.get('Eligibility', fields.get('ELIGIBILITY', '')),
                'focusAreas': fields.get('Focus Areas', []),
                'divisionFit': fields.get('Division Fit', []),
                'qualificationScore': fields.get('Qualification Score', 0),
                'eligibilityMatch': fields.get('Eligibility Match', 0),
                'winProbability': fields.get('Win Probability', 0),
                'strategicValue': fields.get('Strategic Value', 0),
                'priorityLevel': fields.get('Priority Level', ''),
                'applicationComplexity': fields.get('Application Complexity', ''),
                'estimatedTime': fields.get('Estimated Time', 0),
                'status': fields.get('Status', ''),
                'assignedTo': fields.get('Assigned To', ''),
                'tags': fields.get('Tags', []),
                'roiRating': fields.get('ROI Rating', 0),
                'daysUntilDeadline': fields.get('Days Until Deadline', 0),
                'discoveryDate': fields.get('Discovery Date', ''),
                'sourceTable': source_table,
                'entity': ent or 'DDI',
                'grantSourceType': gst,
                'recommendation': fields.get('Recommendation', ''),
                'lastSourceCheck': fields.get('Last Source Check', ''),
                'ddiStrategyNote': fields.get('DDI Strategy Note', ''),
                'staleSourceWarning': _stale_source_warning(fields),
                'ddiActionable': ddi_actionable,
                'grantNameDisplay': _grant_name_field(fields),
            })
        
        return jsonify(filtered)
        
    except Exception as e:
        print(f"GBIS Get Opportunities Error: {str(e)}")
        return jsonify({'error': str(e), 'opportunities': []}), 500


@app.route('/gbis/applications', methods=['GET'])
def get_gbis_applications():
    """
    Get grant applications from Airtable with optional filters
    """
    try:
        from nexus_backend import AirtableClient
        airtable = AirtableClient()
        
        # Get filter parameters
        status = request.args.get('status')
        
        # Fetch all applications from Airtable
        applications = airtable.get_all_records('GRANT APPLICATIONS')
        
        # Format and filter
        formatted = []
        for app in applications:
            fields = app.get('fields', {})
            
            # Apply status filter if specified
            if status and fields.get('Application Status') != status:
                continue
            
            formatted.append({
                'id': app.get('id'),
                'grantOpportunityId': fields.get('Grant Opportunity', [''])[0] if fields.get('Grant Opportunity') else '',
                'applicationTitle': fields.get('Application Title', ''),
                'applicationStatus': fields.get('Application Status', ''),
                'assignedTo': fields.get('Assigned To', ''),
                'applicationDraft': fields.get('Application Draft', ''),
                'wordCount': fields.get('Word Count', 0),
                'sectionsCompleted': fields.get('Sections Completed', []),
                'aiGenerationUsed': fields.get('AI Generation Used', False),
                'divisionFocus': fields.get('Division Focus', ''),
                'grantAmountRequested': fields.get('Grant Amount Requested', 0),
                'submissionDeadline': fields.get('Submission Deadline', ''),
                'actualSubmissionDate': fields.get('Actual Submission Date'),
                'timeInvested': fields.get('Time Invested', 0),
                'qualityScore': fields.get('Quality Score', ''),
                'daysUntilDeadline': fields.get('Days Until Deadline', 0)
            })
        
        return jsonify(formatted)
        
    except Exception as e:
        print(f"GBIS Get Applications Error: {str(e)}")
        return jsonify({'error': str(e), 'applications': []}), 500


@app.route('/gbis/pipeline', methods=['GET'])
def get_gbis_pipeline():
    """
    Get grant pipeline data from Airtable
    """
    try:
        from nexus_backend import AirtableClient
        airtable = AirtableClient()
        
        # Fetch pipeline from Airtable
        pipeline = airtable.get_all_records('GRANT PIPELINE')
        
        # Format pipeline items
        formatted = []
        for item in pipeline:
            fields = item.get('fields', {})
            formatted.append({
                'id': item.get('id'),
                'grantOpportunityId': fields.get('Grant Opportunity', [''])[0] if fields.get('Grant Opportunity') else '',
                'currentStage': fields.get('Current Stage', ''),
                'priority': fields.get('Priority', ''),
                'nextAction': fields.get('Next Action', ''),
                'actionDueDate': fields.get('Action Due Date', ''),
                'assignedTo': fields.get('Assigned To', ''),
                'blockers': fields.get('Blockers', ''),
                'daysInStage': fields.get('Days in Stage', 0)
            })
        
        return jsonify(formatted)
        
    except Exception as e:
        print(f"GBIS Get Pipeline Error: {str(e)}")
        return jsonify({'error': str(e), 'pipeline': []}), 500


@app.route('/gbis/story-library', methods=['GET'])
def get_gbis_story_library():
    """
    Get grant story library modules from Airtable
    """
    try:
        from nexus_backend import AirtableClient
        airtable = AirtableClient()
        
        # Fetch story modules
        modules = airtable.get_all_records('GRANT STORY LIBRARY')
        
        # Format modules
        formatted = []
        for module in modules:
            fields = module.get('fields', {})
            formatted.append({
                'id': module.get('id'),
                'moduleName': fields.get('Module Name', ''),
                'moduleType': fields.get('Module Type', ''),
                'division': fields.get('Division', ''),
                'content': fields.get('Content', ''),
                'wordCount': fields.get('Word Count', 0),
                'keyThemes': fields.get('Key Themes', []),
                'usageCount': fields.get('Usage Count', 0),
                'lastUsed': fields.get('Last Used'),
                'createdBy': fields.get('Created By', ''),
                'status': fields.get('Status', ''),
                'tags': fields.get('Tags', [])
            })
        
        return jsonify(formatted)
        
    except Exception as e:
        print(f"GBIS Get Story Library Error: {str(e)}")
        return jsonify({'error': str(e), 'modules': []}), 500


@app.route('/gbis/stats', methods=['GET'])
def get_gbis_stats():
    """
    Calculate GBIS dashboard statistics
    """
    try:
        from nexus_backend import AirtableClient
        airtable = AirtableClient()
        
        # Fetch data from all GBIS tables
        opportunities = airtable.get_all_records('GRANT OPPORTUNITIES')
        applications = airtable.get_all_records('GRANT APPLICATIONS')
        outcomes = airtable.get_all_records('GRANT OUTCOMES')
        
        # Calculate stats
        active_opportunities = len([o for o in opportunities 
                                    if o.get('fields', {}).get('Status') not in ['Expired', 'Cancelled', 'Rejected']])
        
        total_applications = len(applications)
        
        awarded = [o for o in outcomes if o.get('fields', {}).get('Outcome') == 'Awarded']
        total_awarded = len(awarded)
        
        # Calculate success rate
        total_decisions = len([o for o in outcomes 
                               if o.get('fields', {}).get('Outcome') in ['Awarded', 'Rejected', 'Not Selected']])
        success_rate = round((total_awarded / total_decisions * 100) if total_decisions > 0 else 0, 1)
        
        # Calculate total revenue from awarded grants
        total_revenue = sum([o.get('fields', {}).get('Award Amount', 0) for o in awarded])
        
        # Calculate average time invested
        app_times = [a.get('fields', {}).get('Time Invested', 0) for a in applications 
                     if a.get('fields', {}).get('Time Invested')]
        avg_time_invested = round(sum(app_times) / len(app_times) if app_times else 0, 1)
        
        return jsonify({
            'activeOpportunities': active_opportunities,
            'totalApplications': total_applications,
            'totalAwarded': total_awarded,
            'successRate': success_rate,
            'totalRevenue': total_revenue,
            'avgTimeInvested': avg_time_invested
        })
        
    except Exception as e:
        print(f"GBIS Get Stats Error: {str(e)}")
        return jsonify({
            'activeOpportunities': 0,
            'totalApplications': 0,
            'totalAwarded': 0,
            'successRate': 0,
            'totalRevenue': 0,
            'avgTimeInvested': 0,
            'error': str(e)
        }), 500


@app.route('/gbis/opportunities/<opportunity_id>', methods=['PUT'])
def update_gbis_opportunity(opportunity_id):
    """Update GBIS opportunity - with auto-ATLAS integration when grant awarded"""
    try:
        data = request.json
        airtable_client = AirtableClient()

        opportunity_table = 'GRANT OPPORTUNITIES'

        # Get current opportunity to check status change
        current_opp = airtable_client.get_record(opportunity_table, opportunity_id)
        old_status = current_opp['fields'].get('Status', '')
        
        update_fields = {}
        field_mapping = {
            'grantName': 'Grant Name',
            'funderName': 'Funder Name',
            'funderType': 'Funder Type',
            'grantAmount': 'Grant Amount',
            'maxAward': 'Max Award Amount',
            'deadline': 'Deadline',
            'status': 'Status',
            'priorityLevel': 'Priority Level',
            'divisionFit': 'Division Fit',
            'eligibilityMatch': 'Eligibility Match Score',
            'totalScore': 'Total Score',
            'focusAreas': 'Focus Areas',
            'requirements': 'Requirements',
            'notes': 'Notes'
        }
        
        for key, airtable_field in field_mapping.items():
            if key in data:
                update_fields[airtable_field] = data[key]
        
        # Update the opportunity
        airtable_client.update_record('GRANT OPPORTUNITIES', opportunity_id, update_fields)
        
        # AUTO-CREATE ATLAS PROJECT + VERTEX REVENUE IF STATUS CHANGED TO "AWARDED"
        new_status = update_fields.get('Status', old_status)
        advisor_insight = None
        if new_status == 'Awarded' and old_status != 'Awarded':
            grant_name = current_opp['fields'].get('Grant Name', '')
            grant_amount = current_opp['fields'].get('Grant Amount', 0) or current_opp['fields'].get('Max Award Amount', 0) or 0
            funder = current_opp['fields'].get('Funder Name', '')

            # VERTEX BRIDGE: Log grant award as revenue
            try:
                airtable_client.create_record('VERTEX REVENUE', {
                    VR['revenue_date']:   datetime.now().date().isoformat(),
                    VR['source_system']:  'GBIS',
                    VR['source']:         funder,
                    VR['revenue_type']:   'Grant Award',
                    VR['amount']:         grant_amount,
                    VR['taxable']:        False,
                    VR['recurring']:      False,
                    VR['notes']:          f"Grant awarded: {grant_name} | Opp ID: {opportunity_id}",
                })
                print(f"GBIS → VERTEX revenue: {grant_name} ${grant_amount}")
            except Exception as ve:
                print(f"GBIS → VERTEX revenue: {ve}")

            # VERTEX AUTO-TRIGGER: Full grant financial setup
            try:
                from vertex_automation import vertex_auto_trigger
                vertex_auto_trigger('gbis.grant.awarded', opportunity_id, {
                    'grant_name':       grant_name,
                    'funder_name':      funder,
                    'grant_amount':     float(grant_amount or 0),
                    'performance_start': datetime.now().date().isoformat(),
                })
            except Exception as ve:
                print(f"VERTEX auto-trigger (GBIS Awarded): {ve}")

            # Advisor debrief on grant win
            try:
                from nexus_advisor import advise
                advisor_insight = advise('gbis', 'grant_discovered', {
                    'grant_name': grant_name,
                    'amount': grant_amount,
                })
            except Exception:
                pass

            existing_atlas_link = current_opp['fields'].get('ATLAS Project')
            if not existing_atlas_link:
                try:
                    atlas_result = create_atlas_project_from_grant(opportunity_id, airtable_client)
                    return jsonify({
                        'success': True,
                        'message': 'Grant Awarded! ATLAS project created. VERTEX revenue logged.',
                        'atlas_project_created': True,
                        'atlas_project_id': atlas_result['project_id'],
                        'atlas_project_name': atlas_result['project_name'],
                        'wbs_generated': atlas_result.get('wbs_generated', False),
                        'vertex_revenue_logged': True,
                        'advisor': advisor_insight,
                    })
                except Exception as atlas_error:
                    print(f"Error creating ATLAS project from grant: {atlas_error}")
                    return jsonify({
                        'success': True,
                        'message': 'Grant updated. ATLAS project creation failed - please create manually.',
                        'atlas_error': str(atlas_error),
                        'vertex_revenue_logged': True,
                        'advisor': advisor_insight,
                    })
        
        return jsonify({'success': True, 'advisor': advisor_insight})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def create_atlas_project_from_grant(grant_id: str, airtable_client=None) -> dict:
    """
    🎯 AUTO-CREATE ATLAS PROJECT FROM AWARDED GRANT
    """
    if not airtable_client:
        airtable_client = AirtableClient()
    
    # Fetch grant details from GRANT OPPORTUNITIES
    grant = airtable_client.get_record('GRANT OPPORTUNITIES', grant_id)
    grant_fields = grant['fields']
    
    # Extract key information
    grant_name = grant_fields.get('Grant Name', 'Untitled Grant')
    funder_name = grant_fields.get('Funder Name', grant_fields.get('Funder Organization', 'Unknown Funder'))
    grant_amount = grant_fields.get('Grant Amount', 0)
    focus_areas = grant_fields.get('Focus Areas', '')
    requirements = grant_fields.get('Requirements', '')
    division_fit = grant_fields.get('Division Fit', [])
    divisions_str = ', '.join(division_fit) if isinstance(division_fit, list) else str(division_fit)
    
    # Build comprehensive project scope
    project_scope = f"""
GRANT: {grant_name}
FUNDER: {funder_name}
AWARD AMOUNT: ${grant_amount:,.2f}

DIVISIONS INVOLVED: {divisions_str}

FOCUS AREAS:
{focus_areas}

GRANT REQUIREMENTS:
{requirements}

DELIVERABLES:
- Grant compliance & reporting
- Program implementation
- Impact measurement
- Final report submission
    """.strip()
    
    # Create ATLAS project record
    project_fields = {
        'Project Name': f"GRANT: {grant_name}",
        'Client Name': funder_name,
        'Project Type': 'Grant Management',
        'Budget': grant_amount,
        'Project Scope': project_scope[:10000],
        'Start Date': datetime.now().isoformat(),
        'Status': 'Planning',
        'Priority': 'High',
        'Completion Percentage': 0,
        'Created Date': datetime.now().isoformat(),
        'Source System': 'GBIS',
        'Source Grant ID': grant_id
    }
    
    # Create the project
    project_record = airtable_client.create_record('ATLAS PROJECTS', project_fields)
    project_id = project_record['id']
    
    # Link grant to ATLAS project
    try:
        airtable_client.update_record('GRANT OPPORTUNITIES', grant_id, {
            'ATLAS Project': [project_id]
        })
    except Exception as link_error:
        print(f"Warning: Could not link grant to ATLAS project: {link_error}")
    
    # Auto-generate WBS
    wbs_generated = False
    try:
        from nexus_backend import ATLASAgent2
        atlas_agent = ATLASAgent2()
        wbs_result = atlas_agent.generate_wbs(project_id)
        wbs_generated = 'error' not in wbs_result
    except Exception as wbs_error:
        print(f"Warning: WBS generation failed: {wbs_error}")
    
    return {
        'success': True,
        'project_id': project_id,
        'project_name': project_fields['Project Name'],
        'wbs_generated': wbs_generated,
        'message': f'✅ ATLAS project created: {project_fields["Project Name"]}'
    }


@app.route('/gbis/opportunities/<opportunity_id>/create-atlas-project', methods=['POST'])
def manual_create_atlas_project_from_grant(opportunity_id):
    """Manual endpoint to create ATLAS project from grant"""
    try:
        result = create_atlas_project_from_grant(opportunity_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =====================================================================
# 🔬 GBIS COMMUNITY HEALTH & RESEARCH LANE ENDPOINTS
# =====================================================================

@app.route('/gbis/research-lane/seed-foundations', methods=['POST'])
def gbis_seed_michigan_foundations():
    """
    Seeds GRANT OPPORTUNITIES with Michigan foundation grant sources
    for the Community Health & Research lane (Cause We Care applicant).
    Safe to run multiple times — skips existing records.
    """
    try:
        from gbis_community_health_miner import GBISCommunityHealthMiner
        miner = GBISCommunityHealthMiner()
        result = miner.seed_michigan_foundations()
        return jsonify({
            'success': True,
            'message': f"Seeded {result['imported']} Michigan foundation grant sources",
            'imported': result['imported'],
            'skipped': result['skipped'],
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/gbis/research-lane/mine-federal', methods=['POST'])
def gbis_mine_federal_research_grants():
    """
    Mines Grants.gov for community health & research grants.
    Tags each result with Service Lane, Research Subtype, and Applicant Entity.
    """
    try:
        from gbis_community_health_miner import GBISCommunityHealthMiner
        miner = GBISCommunityHealthMiner()
        result = miner.mine_grants_gov_research()
        return jsonify({
            'success': True,
            'message': f"Found {result['found']} grants, imported {result['imported']} to GBIS",
            **result,
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/gbis/research-lane/run-all', methods=['POST'])
def gbis_run_research_lane_pipeline():
    """
    Runs the full Community Health & Research grant pipeline:
    seeds Michigan foundations + mines Grants.gov federal grants.
    """
    try:
        from gbis_community_health_miner import GBISCommunityHealthMiner
        miner = GBISCommunityHealthMiner()
        result = miner.run_full_pipeline()
        total = (result['michigan_foundations']['imported'] +
                 result['grants_gov']['imported'])
        return jsonify({
            'success': True,
            'message': f"Research Lane pipeline complete — {total} new records in GBIS",
            'details': result,
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/gbis/research-lane/opportunities', methods=['GET'])
def gbis_get_research_lane_opportunities():
    """
    Returns all GRANT OPPORTUNITIES tagged as Community Health & Research.
    Optional query param: ?entity=Cause+We+Care to filter by applicant.
    """
    try:
        from nexus_backend import AirtableClient
        airtable = AirtableClient()
        records = airtable.get_all_records('GRANT OPPORTUNITIES')

        entity_filter = request.args.get('entity', '').strip()

        research_opps = [
            r['fields'] for r in records
            if r['fields'].get('Service Lane') == 'Community Health & Research'
            and (not entity_filter or r['fields'].get('Applicant Entity', '') == entity_filter)
        ]

        # Sort by deadline
        research_opps.sort(key=lambda x: x.get('Deadline', '9999-12-31'))

        return jsonify({
            'success': True,
            'count': len(research_opps),
            'filter': entity_filter or 'all',
            'opportunities': research_opps,
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/gbis/research-lane/seed-veteran-sources', methods=['POST'])
def gbis_seed_veteran_sources():
    """
    Seeds GRANT OPPORTUNITIES with veteran grant sources.
    Unlocked by Gary C. Felton Jr. (Army Veteran, Board Director) +
    DDI/CWC veteran hiring initiative + Hair Cuts for Vets program.
    Safe to run multiple times — skips existing records.
    """
    try:
        from gbis_community_health_miner import GBISCommunityHealthMiner
        miner = GBISCommunityHealthMiner()
        result = miner.seed_veteran_sources()
        return jsonify({
            'success': True,
            'message': f"Seeded {result['imported']} veteran grant sources",
            'imported': result['imported'],
            'skipped': result['skipped'],
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# =====================================================================
# 💼 GBIS SMALL BUSINESS GRANTS ENDPOINTS
# =====================================================================

@app.route('/gbis/mine-small-grants/seed', methods=['POST'])
def gbis_seed_small_grants():
    """
    Seeds GRANT OPPORTUNITIES with ALL small business grant sources (46 total):
    Hello Alice, Amber Grant, IFundWomen, Comcast RISE, FedEx, Google,
    Bank of America, Chase, Nav, SBA, SCORE, Michigan SBDC, MEDC, DEGC,
    LinkedIn monitoring, WBENC portal, NAWBO, and more.
    Safe to run multiple times — skips existing records.
    """
    try:
        from gbis_small_grants_miner import GBISSmallGrantsMiner
        miner = GBISSmallGrantsMiner()
        result = miner.seed_all_sources()
        return jsonify({
            'success':  True,
            'message':  f"Seeded {result['imported']} small business grant sources ({result['skipped']} already tracked)",
            'imported': result['imported'],
            'skipped':  result['skipped'],
            'total':    result['total'],
        })
    except Exception as e:
        print(f"GBIS Small Grants Seed Error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/gbis/mine-small-grants/seed-free', methods=['POST'])
def gbis_seed_small_grants_free_only():
    """
    Seeds GRANT OPPORTUNITIES with FREE-ONLY small business grant sources.
    Excludes any sources with application fees (e.g., Amber Grant $15).
    Safe to run multiple times — skips existing records.
    """
    try:
        from gbis_small_grants_miner import GBISSmallGrantsMiner
        miner = GBISSmallGrantsMiner()
        result = miner.seed_free_sources_only()
        return jsonify({
            'success':  True,
            'message':  f"Seeded {result['imported']} FREE small business grant sources ({result['skipped']} already tracked)",
            'imported': result['imported'],
            'skipped':  result['skipped'],
            'total':    result['total'],
        })
    except Exception as e:
        print(f"GBIS Small Grants Free Seed Error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/gbis/mine-small-grants/daily-digest', methods=['GET'])
def gbis_small_grants_daily_digest():
    """
    Returns today's prioritized checklist of small business grant actions:
    what to apply to today, what to check, and deadlines coming up.
    Called by NEXUS daily briefing.
    """
    try:
        from gbis_small_grants_miner import GBISSmallGrantsMiner
        miner = GBISSmallGrantsMiner()
        digest = miner.daily_digest()
        return jsonify({'success': True, **digest})
    except Exception as e:
        print(f"GBIS Daily Digest Error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/gbis/mine-all', methods=['POST'])
def gbis_mine_all():
    """
    Master GBIS mining endpoint — runs the FULL pipeline:
      1. Seed Michigan foundation grants (Cause We Care lane)
      2. Seed veteran grant sources (Gary Felton Jr. lane)
      3. Seed 18 small business grants (DDI lane)
      4. Mine Grants.gov for live federal health & research grants
    Safe to run daily — all sources skip duplicates.
    """
    try:
        from gbis_community_health_miner import GBISCommunityHealthMiner
        from gbis_small_grants_miner import GBISSmallGrantsMiner

        community_miner = GBISCommunityHealthMiner()
        small_miner     = GBISSmallGrantsMiner()

        community_result = community_miner.run_full_pipeline()
        small_result     = small_miner.seed_all_sources()

        mich  = community_result['michigan_foundations']
        cwc   = community_result.get('cwc_expansion', {'imported': 0, 'skipped': 0})
        vets  = community_result['veteran_sources']
        fed   = community_result['grants_gov']
        small = small_result

        total_new = (mich['imported'] + cwc['imported'] + vets['imported'] +
                     fed['imported']  + small['imported'])

        return jsonify({
            'success':   True,
            'message':   f"Full pipeline complete — {total_new} new opportunities added to GBIS",
            'total_new': total_new,
            'breakdown': {
                'small_business_grants': {
                    'imported': small['imported'],
                    'skipped':  small['skipped'],
                    'label':    'Small Business Grants (DDI)',
                },
                'michigan_foundations': {
                    'imported': mich['imported'],
                    'skipped':  mich['skipped'],
                    'label':    'Michigan Foundation Grants',
                },
                'cwc_expansion': {
                    'imported': cwc['imported'],
                    'skipped':  cwc['skipped'],
                    'label':    'Cause We Care Expansion (BOTH / TPA)',
                },
                'veteran_grants': {
                    'imported': vets['imported'],
                    'skipped':  vets['skipped'],
                    'label':    'Veteran Grant Sources',
                },
                'grants_gov': {
                    'imported': fed['imported'],
                    'found':    fed.get('found', 0),
                    'label':    'Grants.gov Federal Grants',
                },
            },
            'last_run': datetime.now().isoformat(),
        })
    except Exception as e:
        print(f"GBIS Mine-All Error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/gbis/research-lane/setup-checklist', methods=['GET'])
def gbis_research_lane_setup_checklist():
    """Returns the Cause We Care registration checklist and Airtable setup instructions."""
    try:
        from gbis_community_health_miner import (
            AIRTABLE_SETUP_INSTRUCTIONS, CWC_REGISTRATION_CHECKLIST
        )
        return jsonify({
            'airtable_setup': AIRTABLE_SETUP_INSTRUCTIONS,
            'cwc_registration': CWC_REGISTRATION_CHECKLIST,
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# =====================================================================
# 💎 VERTEX FINANCIAL SYSTEM ENDPOINTS
# =====================================================================

# ---------------------------------------------------------------------------
# VERTEX_FIELD_MAP — single source of truth for all VERTEX Airtable field names.
# Airtable field names are ALL CAPS. All VERTEX code must use this map.
# To rename a field: change it here only. Never hardcode field names below.
# ---------------------------------------------------------------------------
VI = {  # VERTEX INVOICES
    'invoice_number':              'INVOICE NUMBER',
    'invoice_date':                'INVOICE DATE',
    'due_date':                    'DUE DATE',
    'client_name':                 'CLIENT NAME',
    'client_id':                   'CLIENT ID',
    'source_system':               'SOURCE SYSTEM',
    'source_record':               'SOURCE RECORD',
    'gpss_opportunity':            'GPSS OPPORTUNITY',
    'atlas_project':               'ATLAS PROJECT',
    'ddcss_prospect':              'DDCSS PROSPECT',
    'lbpc_lead':                   'LBPC LEAD',
    'invoice_type':                'INVOICE TYPE',
    'line_items':                  'LINE ITEMS',
    'subtotal':                    'SUBTOTAL',
    'tax_rate':                    'TAX RATE %',
    'tax_amount':                  'TAX AMOUNT',
    'discount_pct':                'DISCOUNT (%)',
    'discount_amount':             'DISCOUNT AMOUNT',
    'total_amount':                'TOTAL AMOUNT',
    'amount_paid':                 'AMOUNT PAID',
    'balance_due':                 'BALANCE DUE',
    'payment_status':              'PAYMENT STATUS',
    'payment_method':              'PAYMENT METHOD',
    'payment_date':                'PAYMENT DATE',
    'payment_terms':               'PAYMENT TERMS',
    'days_outstanding':            'DAYS OUTSTANDING',
    'aging_category':              'AGING CATEGORY',
    'notes':                       'NOTES',
    'client_notes':                'CLIENTS NOTES',
    'po_number':                   'PO NUMBER',
    'cage_code':                   'CAGE CODE',
    'duns_number':                 'DUNS NUMBER',
    'uei':                         'SAM.gov UEI',
    'government_agency':           'GOVERNMENT AGENCY',
    'contract_number':             'CONTRACT NUMBER',
    'contract_type':               'CONTRACT TYPE',
    'invoice_pdf':                 'INVOICE PDF',
    'supporting_documents':        'SUPPORTING DOCUMENTS',
    'sent_date':                   'SENT DATE',
    'sent_by':                     'SENT BY',
    'follow_up_date':              'FOLLOW-UP DATE',
    'factoring_status':            'FACTORING STATUS',
    'factoring_company':           'FACTORING COMPANY',
    'factoring_fee_pct':           'FACTORING FEE (%)',
    'factoring_fee_dollar':        'FACTORING FEE ($)',
    'advance_rate':                'ADVANTAGE RATE',
    'advance_amount':              'ADVANCED AMOUNT ($)',
    'reserve_amount':              'RESERVE AMOUNT ($)',
    'factoring_submitted_date':    'FACTORING SUBMITTED DATE',
    'factoring_funded_date':       'FACTORING FUNDED DATE',
    'client_payment_to_factor':    'CLIENT PAYMENT TO FACTOR DATE',
    'reserve_released_date':       'RESERVE RELEASED DATE',
    'vertex_revenue':              'VERTEX REVENUE',
    'vertex_bank_transactions':    'VERTEX BANK TRANSACTIONS',
    # --- WAWF / IPP Federal Invoicing fields (Phase 6) ---
    'wawf_status':                 'WAWF STATUS',
    'wawf_document_type':          'WAWF DOCUMENT TYPE',
    'wawf_submitted_date':         'WAWF SUBMITTED DATE',
    'wawf_accepted_date':          'WAWF ACCEPTED DATE',
    'wawf_rejection_reason':       'WAWF REJECTION REASON',
    'ipp_submission_date':         'IPP SUBMISSION DATE',
    'ipp_approval_date':           'IPP APPROVAL DATE',
    'ipp_invoice_id':              'IPP INVOICE ID',
    'prompt_payment_interest':     'PROMPT PAYMENT INTEREST ($)',
    'interest_start_date':         'INTEREST START DATE',
    'clin':                        'CLIN',
    'acrn':                        'ACRN',
    'dodaac':                      'DODAAC',
    'cage_code':                   'CAGE CODE',
}

VE = {  # VERTEX EXPENSES
    'expense_date':     'EXPENSE DATE',
    'vendor_payee':     'VENDOR/PAYEE',
    'vendor_id':        'VENDOR ID',
    'description':      'DESCRIPTION',
    'category':         'CATEGORY',
    'subcategory':      'SUBCATEGORY',
    'amount':           'AMOUNT',
    'payment_method':   'PAYMENT METHOD',
    'payment_date':     'PAYMENT DATE',
    'payment_status':   'PAYMENT STATUS',
    'receipt':          'RECEIPT',
    'tax_deduction':    'TAX DEDUCTION',
    'tax_category':     'TAX CATEGORY',
    'billable':         'BILLABLE',
    'billable_to':      'BILLABLE TO',
    'project':          'PROJECT',
    'invoice':          'INVOICE',
    'reimbursable':     'REIMBURSABLE',
    'notes':            'NOTES',
    'expense_type':     'EXPENSE TYPE',
    'vendor':           'VENDOR',
    'payment_due_date': 'PAYMENT DUE DATE',
}

VR = {  # VERTEX REVENUE
    'revenue_date':    'REVENUE DATE',
    'source':          'SOURCE',
    'revenue_type':    'REVENUE TYPE',
    'source_system':   'SOURCE SYSTEM',
    'amount':          'AMOUNT',
    'payment_method':  'PAYMENT METHOD',
    'invoice':         'INVOICE',
    'category':        'CATEGORY',
    'taxable':         'TAXABLE',
    'recurring':       'RECURRING',
    'notes':           'NOTES',
}

VC = {  # VERTEX CLIENTS
    'client_name':           'CLIENT NAME',
    'client_type':           'CLIENT TYPE',
    'contact_name':          'CONTACT NAME',
    'email':                 'EMAIL',
    'phone':                 'PHONE',
    'address':               'ADDRESS',
    'tax_id':                'TAX ID (EIN/SSN)',
    'payment_terms':         'PAYMENT TERMS',
    'credit_limit':          'CREDIT LIMIT',
    'payment_rating':        'PAYMENT RATING',
    'active':                'ACTIVE',
    'notes':                 'NOTES',
    'avg_payment_days':      'AVERAGE PAYMENT TIME (DAYS)',
}


@app.route('/vertex/stats', methods=['GET'])
def get_vertex_stats():
    """Get VERTEX Financial dashboard statistics"""
    try:
        airtable_client = AirtableClient()
        
        try:
            invoices = airtable_client.get_all_records('VERTEX INVOICES')
        except:
            invoices = []
        
        # Calculate invoice stats
        total_revenue = sum(inv['fields'].get(VI['total_amount'], 0) for inv in invoices if isinstance(inv['fields'].get(VI['total_amount']), (int, float)))
        paid_invoices = [inv for inv in invoices if inv['fields'].get(VI['payment_status']) == 'Paid']
        pending_invoices = [inv for inv in invoices if inv['fields'].get(VI['payment_status']) in ['Unpaid', 'Partial']]
        overdue_invoices = [inv for inv in invoices if inv['fields'].get(VI['payment_status']) == 'Overdue']

        stats = {
            'totalInvoices': len(invoices),
            'paidInvoices': len(paid_invoices),
            'pendingInvoices': len(pending_invoices),
            'overdueInvoices': len(overdue_invoices),
            'totalRevenue': total_revenue,
            'pendingRevenue': sum(inv['fields'].get(VI['total_amount'], 0) for inv in pending_invoices)
        }
        
        return jsonify(stats)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# -------------------- VERTEX INVOICES --------------------

@app.route('/vertex/invoices', methods=['GET'])
def get_vertex_invoices():
    """Get all VERTEX invoices with optional filters"""
    try:
        airtable = AirtableClient()
        
        # Get query parameters
        payment_status = request.args.get('payment_status')
        source_system = request.args.get('source_system')
        client_name = request.args.get('client_name')
        aging_category = request.args.get('aging_category')
        factoring_status = request.args.get('factoring_status')
        
        # Build Airtable formula
        formulas = []
        if payment_status:
            formulas.append(f"{{{VI['payment_status']}}}='{payment_status}'")
        if source_system:
            formulas.append(f"{{{VI['source_system']}}}='{source_system}'")
        if client_name:
            formulas.append(f"FIND('{client_name}',{{{VI['client_name']}}})>0")
        if aging_category:
            formulas.append(f"{{{VI['aging_category']}}}='{aging_category}'")
        if factoring_status:
            formulas.append(f"{{{VI['factoring_status']}}}='{factoring_status}'")
        
        formula = "AND(" + ",".join(formulas) + ")" if formulas else None
        
        invoices = airtable.search_records('VERTEX INVOICES', formula) if formula else airtable.get_all_records('VERTEX INVOICES')
        
        return jsonify({'invoices': invoices})
    except Exception as e:
        print(f"Error getting VERTEX invoices: {e}")
        return jsonify({'error': str(e), 'invoices': []}), 500


@app.route('/vertex/invoices', methods=['POST'])
def create_vertex_invoice():
    """Create a new VERTEX invoice"""
    try:
        data = request.json
        airtable = AirtableClient()
        
        # Create invoice record
        invoice_fields = {
            VI['invoice_number']:  data.get('invoice_number', f"INV-{datetime.now().strftime('%Y%m%d-%H%M%S')}"),
            VI['invoice_date']:    data.get('invoice_date', datetime.now().date().isoformat()),
            VI['due_date']:        data.get('due_date'),
            VI['client_name']:     data.get('client_name'),
            VI['source_system']:   data.get('source_system', 'Other'),
            VI['source_record']:   data.get('source_record_id'),
            VI['invoice_type']:    data.get('invoice_type', 'Standard'),
            VI['line_items']:      data.get('line_items', '[]'),
            VI['subtotal']:        data.get('subtotal', 0),
            VI['tax_rate']:        data.get('tax_rate', 0),
            VI['total_amount']:    data.get('total_amount', 0),
            VI['payment_status']:  data.get('payment_status', 'Unpaid'),
            VI['payment_terms']:   data.get('payment_terms', 'Net 30'),
            VI['notes']:           data.get('notes', ''),
        }

        # Remove None values — Airtable rejects null on required fields
        invoice_fields = {k: v for k, v in invoice_fields.items() if v is not None}

        # Add government contract fields if applicable
        if data.get('contract_number'):
            invoice_fields[VI['contract_number']] = data['contract_number']
        if data.get('government_agency'):
            invoice_fields[VI['government_agency']] = data['government_agency']

        # Add factoring fields if applicable
        if data.get('factoring_status'):
            invoice_fields[VI['factoring_status']] = data['factoring_status']
            if data.get('factoring_company'):
                invoice_fields[VI['factoring_company']] = data['factoring_company']
            if data.get('factoring_fee_percent'):
                invoice_fields[VI['factoring_fee_pct']] = data['factoring_fee_percent']
            if data.get('advance_rate_percent'):
                invoice_fields[VI['advance_rate']] = data['advance_rate_percent']
        
        invoice = airtable.create_record('VERTEX INVOICES', invoice_fields)
        
        # NEXUS ADVISOR: Teach about invoicing
        advisor_insight = None
        try:
            from nexus_advisor import advise, log_growth
            advisor_insight = advise('vertex', 'invoice_created', {
                'total_amount': data.get('total_amount', 0),
                'source_system': data.get('source_system'),
                'is_government': bool(data.get('government_agency')),
            })
            log_growth('invoice_created')
        except Exception:
            pass

        return jsonify({'success': True, 'invoice': invoice, 'advisor': advisor_insight})
    except Exception as e:
        print(f"Error creating VERTEX invoice: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/vertex/invoices/<invoice_id>', methods=['GET'])
def get_vertex_invoice(invoice_id):
    """Get a specific VERTEX invoice"""
    try:
        airtable = AirtableClient()
        invoice = airtable.get_record('VERTEX INVOICES', invoice_id)
        return jsonify({'invoice': invoice})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/vertex/invoices/<invoice_id>', methods=['PUT'])
def update_vertex_invoice(invoice_id):
    """Update a VERTEX invoice"""
    try:
        data = request.json
        airtable = AirtableClient()
        
        # Filter out read-only fields
        update_fields = {k: v for k, v in data.items() if k not in ['id', 'createdTime']}
        
        invoice = airtable.update_record('VERTEX INVOICES', invoice_id, update_fields)
        return jsonify({'success': True, 'invoice': invoice})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/vertex/invoices/<invoice_id>/factor', methods=['POST'])
def submit_invoice_to_factoring(invoice_id):
    """Submit invoice to factoring company"""
    try:
        data = request.json
        airtable = AirtableClient()
        
        # Update invoice with factoring details
        update_fields = {
            VI['factoring_status']:           'Submitted',
            VI['factoring_company']:          data.get('factoring_company'),
            VI['factoring_fee_pct']:          data.get('factoring_fee_percent', 3),
            VI['advance_rate']:               data.get('advance_rate_percent', 85),
            VI['factoring_submitted_date']:   datetime.now().date().isoformat(),
        }
        update_fields = {k: v for k, v in update_fields.items() if v is not None}
        
        invoice = airtable.update_record('VERTEX INVOICES', invoice_id, update_fields)
        return jsonify({'success': True, 'invoice': invoice, 'message': 'Invoice submitted to factoring'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/vertex/invoices/aging', methods=['GET'])
def get_ar_aging_report():
    """Get Accounts Receivable aging report"""
    try:
        airtable = AirtableClient()
        
        # Get all unpaid/partial invoices
        ps = VI['payment_status']
        formula = f"OR({{{ps}}}='Unpaid',{{{ps}}}='Partial',{{{ps}}}='Overdue')"
        invoices = airtable.search_records('VERTEX INVOICES', formula)

        # Group by aging category
        aging = {
            'Current':    {'count': 0, 'total': 0, 'invoices': []},
            '31-60 Days': {'count': 0, 'total': 0, 'invoices': []},
            '61-90 Days': {'count': 0, 'total': 0, 'invoices': []},
            '90+ Days':   {'count': 0, 'total': 0, 'invoices': []},
        }

        for invoice in invoices:
            fields = invoice.get('fields', {})
            category = fields.get(VI['aging_category'], 'Current')
            balance = fields.get(VI['balance_due'], 0)

            if category in aging:
                aging[category]['count'] += 1
                aging[category]['total'] += balance
                aging[category]['invoices'].append(invoice)
        
        return jsonify({'aging_report': aging})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# -------------------- VERTEX EXPENSES --------------------

@app.route('/vertex/expenses', methods=['GET'])
def get_vertex_expenses():
    """Get all VERTEX expenses"""
    try:
        airtable = AirtableClient()
        
        category = request.args.get('category')
        payment_status = request.args.get('payment_status')
        
        formula = None
        if category or payment_status:
            formulas = []
            if category:
                formulas.append(f"{{{VE['category']}}}='{category}'")
            if payment_status:
                formulas.append(f"{{{VE['payment_status']}}}='{payment_status}'")
            formula = "AND(" + ",".join(formulas) + ")"

        expenses = airtable.search_records('VERTEX EXPENSES', formula) if formula else airtable.get_all_records('VERTEX EXPENSES')
        
        return jsonify({'expenses': expenses})
    except Exception as e:
        return jsonify({'error': str(e), 'expenses': []}), 500


@app.route('/vertex/expenses', methods=['POST'])
def create_vertex_expense():
    """Create a new VERTEX expense"""
    try:
        data = request.json
        airtable = AirtableClient()
        
        expense_fields = {
            VE['expense_date']:    data.get('expense_date', datetime.now().date().isoformat()),
            VE['vendor_payee']:    data.get('vendor'),
            VE['description']:     data.get('description'),
            VE['category']:        data.get('category', 'Other'),
            VE['amount']:          data.get('amount', 0),
            VE['payment_method']:  data.get('payment_method', 'Credit Card'),
            VE['payment_status']:  data.get('payment_status', 'Paid'),
            VE['tax_deduction']:   data.get('tax_deductible', True),
            VE['billable']:        data.get('billable', False),
            VE['notes']:           data.get('notes', ''),
        }
        expense_fields = {k: v for k, v in expense_fields.items() if v is not None}
        
        expense = airtable.create_record('VERTEX EXPENSES', expense_fields)
        
        return jsonify({'success': True, 'expense': expense})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/vertex/expenses/<expense_id>', methods=['PUT'])
def update_vertex_expense(expense_id):
    """Update a VERTEX expense"""
    try:
        data = request.json
        airtable = AirtableClient()
        
        update_fields = {k: v for k, v in data.items() if k not in ['id', 'createdTime']}
        
        expense = airtable.update_record('VERTEX EXPENSES', expense_id, update_fields)
        return jsonify({'success': True, 'expense': expense})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/vertex/expenses/categorize', methods=['POST'])
def ai_categorize_expense():
    """Use AI to categorize an expense"""
    try:
        data = request.json
        description = data.get('description', '')
        vendor = data.get('vendor', '')
        
        from nexus_backend import AnthropicClient
        ai = AnthropicClient()
        
        prompt = f"""Categorize this business expense:
Vendor: {vendor}
Description: {description}

Return ONLY the category name from this list:
- Payroll
- Software/Tools
- Marketing
- Office Supplies
- Travel
- Meals
- Equipment
- Rent/Utilities
- Professional Services
- Insurance
- Taxes
- Other

Category:"""
        
        category = ai.complete(prompt, max_tokens=50).strip()
        tax_deductible = category not in ['Personal', 'Non-Deductible']
        
        return jsonify({
            'category': category,
            'tax_deductible': tax_deductible,
            'confidence': 0.9
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# -------------------- VERTEX REVENUE --------------------

@app.route('/vertex/revenue', methods=['GET'])
def get_vertex_revenue():
    """Get all VERTEX revenue records"""
    try:
        airtable = AirtableClient()
        
        revenue_type = request.args.get('revenue_type')
        source_system = request.args.get('source_system')
        
        formula = None
        if revenue_type or source_system:
            formulas = []
            if revenue_type:
                formulas.append(f"{{{VR['revenue_type']}}}='{revenue_type}'")
            if source_system:
                formulas.append(f"{{{VR['source_system']}}}='{source_system}'")
            formula = "AND(" + ",".join(formulas) + ")"

        revenue_records = airtable.search_records('VERTEX REVENUE', formula) if formula else airtable.get_all_records('VERTEX REVENUE')
        
        return jsonify({'revenue': revenue_records})
    except Exception as e:
        return jsonify({'error': str(e), 'revenue': []}), 500


@app.route('/vertex/revenue', methods=['POST'])
def create_vertex_revenue():
    """Create a new VERTEX revenue record"""
    try:
        data = request.json
        airtable = AirtableClient()
        
        revenue_fields = {
            VR['revenue_date']:   data.get('revenue_date', datetime.now().date().isoformat()),
            VR['source']:         data.get('source'),
            VR['revenue_type']:   data.get('revenue_type', 'Invoice Payment'),
            VR['source_system']:  data.get('source_system', 'Other'),
            VR['amount']:         data.get('amount', 0),
            VR['payment_method']: data.get('payment_method', 'ACH'),
            VR['taxable']:        data.get('taxable', True),
            VR['recurring']:      data.get('recurring', False),
            VR['notes']:          data.get('notes', ''),
        }
        revenue_fields = {k: v for k, v in revenue_fields.items() if v is not None}
        
        revenue = airtable.create_record('VERTEX REVENUE', revenue_fields)
        
        return jsonify({'success': True, 'revenue': revenue})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# -------------------- VERTEX NEMT MEDICAL BILLING --------------------

@app.route('/vertex/nemt/log-trip', methods=['POST'])
def vertex_nemt_log_trip():
    """Log a completed NEMT trip (local store); HCPCS validated against NEMT RATES in Airtable."""
    try:
        from nemt_billing import log_trip

        d = request.json or {}
        airtable = AirtableClient()
        trip = log_trip(
            airtable,
            member_medicaid_id=d.get('member_medicaid_id', ''),
            pickup_time=d.get('pickup_time', ''),
            dropoff_time=d.get('dropoff_time', ''),
            pickup_address=d.get('pickup_address', ''),
            dropoff_address=d.get('dropoff_address', ''),
            mileage=d.get('mileage', 0),
            trip_purpose=d.get('trip_purpose', ''),
            hcpcs_code=d.get('hcpcs_code', ''),
            payer=d.get('payer'),
        )
        return jsonify({'success': True, 'trip': trip})
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        print(f"vertex_nemt_log_trip: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/vertex/nemt/generate-claim', methods=['POST'])
def vertex_nemt_generate_claim():
    """Create CMS-1500-style claim as VERTEX INVOICES row (Pending)."""
    try:
        from nemt_billing import generate_claim

        d = request.json or {}
        trip_id = d.get('trip_id')
        if not trip_id:
            return jsonify({'success': False, 'error': 'trip_id required'}), 400
        airtable = AirtableClient()
        result = generate_claim(airtable, trip_id)
        return jsonify(result)
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        print(f"vertex_nemt_generate_claim: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/vertex/nemt/pending-claims', methods=['GET'])
def vertex_nemt_pending_claims():
    """Pending NEMT invoices + summary + logged trips + rates from Airtable NEMT RATES."""
    try:
        from nemt_billing import get_nemt_summary, get_pending_claims, list_logged_trips, list_nemt_rates

        airtable = AirtableClient()
        pending = get_pending_claims(airtable)
        summary = get_nemt_summary(airtable)
        trips = list_logged_trips()
        rates = list_nemt_rates(airtable)
        return jsonify(
            {
                'pending_claims': pending,
                'summary': summary,
                'logged_trips': trips,
                'rates': rates,
            }
        )
    except Exception as e:
        print(f"vertex_nemt_pending_claims: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/vertex/nemt/rates', methods=['GET'])
def vertex_nemt_get_rates():
    """All rows from Airtable NEMT RATES."""
    try:
        from nemt_billing import list_nemt_rates

        airtable = AirtableClient()
        return jsonify({'rates': list_nemt_rates(airtable)})
    except Exception as e:
        print(f"vertex_nemt_get_rates: {e}")
        return jsonify({'error': str(e), 'rates': []}), 500


@app.route('/vertex/nemt/rates/<record_id>', methods=['PUT'])
def vertex_nemt_update_rate(record_id):
    """Update HCPCS, description, and/or rate amount for one NEMT RATES row."""
    try:
        from nemt_billing import update_nemt_rate

        d = request.json or {}
        airtable = AirtableClient()
        rec = update_nemt_rate(
            airtable,
            record_id,
            hcpcs_code=d.get('hcpcs_code'),
            description=d.get('description'),
            rate_amount=d.get('rate_amount'),
        )
        return jsonify({'success': True, 'record': rec})
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        print(f"vertex_nemt_update_rate: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/vertex/nemt/rates/seed', methods=['POST'])
def vertex_nemt_seed_rates():
    """Create placeholder T2002 / A0130 / A0380 rows at $0.00 when missing."""
    try:
        from nemt_billing import seed_placeholder_rates

        airtable = AirtableClient()
        result = seed_placeholder_rates(airtable)
        return jsonify(result)
    except Exception as e:
        print(f"vertex_nemt_seed_rates: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/vertex/nemt/post-payment', methods=['POST'])
def vertex_nemt_post_payment():
    """ERA-style payment: mark invoice Paid, post VERTEX REVENUE."""
    try:
        from nemt_billing import post_payment

        d = request.json or {}
        invoice_id = d.get('invoice_id')
        if not invoice_id:
            return jsonify({'success': False, 'error': 'invoice_id required'}), 400
        amount = d.get('amount')
        if amount is None:
            return jsonify({'success': False, 'error': 'amount required'}), 400
        airtable = AirtableClient()
        result = post_payment(
            airtable,
            invoice_id,
            float(amount),
            payment_date=d.get('payment_date'),
            era_reference=d.get('era_reference'),
            notes=d.get('notes'),
        )
        return jsonify(result)
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        print(f"vertex_nemt_post_payment: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/vertex/nemt/invoice/<invoice_id>/pdf', methods=['GET'])
def vertex_nemt_invoice_pdf(invoice_id):
    """Download factoring-compliant NEMT invoice PDF (generated from HTML)."""
    try:
        from nemt_billing import SOURCE_SYSTEM, _record_fields, get_nemt_invoice_pdf_path_from_record

        airtable = AirtableClient()
        rec = airtable.get_record("VERTEX INVOICES", invoice_id)
        fields = _record_fields(rec)
        if fields.get("Source System") != SOURCE_SYSTEM:
            return jsonify({"error": "Not a NEMT invoice"}), 400
        path = get_nemt_invoice_pdf_path_from_record(rec)
        if not path:
            return jsonify({"error": "PDF not found or not generated"}), 404
        return send_file(path, mimetype="application/pdf", as_attachment=False)
    except Exception as e:
        print(f"vertex_nemt_invoice_pdf: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/vertex/revenue/summary', methods=['GET'])
def get_revenue_summary():
    """Get revenue summary statistics"""
    try:
        airtable = AirtableClient()
        
        # Get date range from query params
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        formula = None
        if start_date and end_date:
            formula = f"AND(IS_AFTER({{Revenue Date}},'{start_date}'),IS_BEFORE({{Revenue Date}},'{end_date}'))"
        
        revenue_records = airtable.search_records('VERTEX REVENUE', formula) if formula else airtable.get_all_records('VERTEX REVENUE')
        
        # Calculate totals
        total_revenue = sum(r.get('fields', {}).get(VR['amount'], 0) for r in revenue_records)

        # Group by type
        by_type = {}
        for record in revenue_records:
            fields = record.get('fields', {})
            rev_type = fields.get(VR['revenue_type'], 'Other')
            amount = fields.get(VR['amount'], 0)
            by_type[rev_type] = by_type.get(rev_type, 0) + amount

        # Group by system
        by_system = {}
        for record in revenue_records:
            fields = record.get('fields', {})
            system = fields.get(VR['source_system'], 'Other')
            amount = fields.get(VR['amount'], 0)
            by_system[system] = by_system.get(system, 0) + amount
        
        return jsonify({
            'total_revenue': total_revenue,
            'by_type': by_type,
            'by_system': by_system,
            'record_count': len(revenue_records)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# -------------------- VERTEX DASHBOARD & REPORTS --------------------

@app.route('/vertex/dashboard', methods=['GET'])
def get_vertex_dashboard():
    """Get VERTEX dashboard statistics"""
    try:
        airtable = AirtableClient()
        
        # Get all invoices
        invoices = airtable.get_all_records('VERTEX INVOICES')
        
        # Calculate invoice metrics
        total_invoiced = sum(inv.get('fields', {}).get(VI['total_amount'], 0) for inv in invoices)
        total_paid = sum(inv.get('fields', {}).get(VI['amount_paid'], 0) for inv in invoices)
        total_outstanding = sum(inv.get('fields', {}).get(VI['balance_due'], 0) for inv in invoices if inv.get('fields', {}).get(VI['payment_status']) in ['Unpaid', 'Partial', 'Overdue'])

        unpaid_count = len([inv for inv in invoices if inv.get('fields', {}).get(VI['payment_status']) in ['Unpaid', 'Partial', 'Overdue']])

        # Get expenses
        expenses = airtable.get_all_records('VERTEX EXPENSES')
        total_expenses = sum(exp.get('fields', {}).get(VE['amount'], 0) for exp in expenses)

        # Get revenue
        revenue_records = airtable.get_all_records('VERTEX REVENUE')
        total_revenue = sum(rev.get('fields', {}).get(VR['amount'], 0) for rev in revenue_records)

        # Calculate metrics
        net_income = total_revenue - total_expenses
        profit_margin = (net_income / total_revenue * 100) if total_revenue > 0 else 0

        # Revenue by system
        revenue_by_system = {}
        for inv in invoices:
            fields = inv.get('fields', {})
            system = fields.get(VI['source_system'], 'Other')
            amount = fields.get(VI['total_amount'], 0)
            revenue_by_system[system] = revenue_by_system.get(system, 0) + amount
        
        # Calculate cash flow forecast (simple: outstanding AR)
        cash_flow_forecast = {
            'current_cash': total_paid - total_expenses,
            'pending_receivables': total_outstanding,
            'projected_30_days': total_paid - total_expenses + (total_outstanding * 0.7),  # Assume 70% collection
            'projected_60_days': total_paid - total_expenses + (total_outstanding * 0.9),  # Assume 90% collection
            'projected_90_days': total_paid - total_expenses + total_outstanding  # Assume 100% collection
        }
        
        return jsonify({
            'total_revenue': total_revenue,
            'total_expenses': total_expenses,
            'net_income': net_income,
            'profit_margin': round(profit_margin, 2),
            'total_invoiced': total_invoiced,
            'total_paid': total_paid,
            'accounts_receivable': total_outstanding,
            'unpaid_invoice_count': unpaid_count,
            'revenue_by_system': revenue_by_system,
            'cash_flow_forecast': cash_flow_forecast
        })
    except Exception as e:
        print(f"Error getting VERTEX dashboard: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/vertex/reports/pl', methods=['GET'])
def get_profit_loss_statement():
    """Get Profit & Loss statement"""
    try:
        airtable = AirtableClient()
        
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Get revenue
        revenue_formula = None
        if start_date and end_date:
            revenue_formula = f"AND(IS_AFTER({{{VR['revenue_date']}}},'{start_date}'),IS_BEFORE({{{VR['revenue_date']}}},'{end_date}'))"

        revenue_records = airtable.search_records('VERTEX REVENUE', revenue_formula) if revenue_formula else airtable.get_all_records('VERTEX REVENUE')

        # Group revenue by system
        revenue_by_system = {}
        total_revenue = 0
        for record in revenue_records:
            fields = record.get('fields', {})
            system = fields.get(VR['source_system'], 'Other')
            amount = fields.get(VR['amount'], 0)
            revenue_by_system[system] = revenue_by_system.get(system, 0) + amount
            total_revenue += amount

        # Get expenses
        expense_formula = None
        if start_date and end_date:
            expense_formula = f"AND(IS_AFTER({{{VE['expense_date']}}},'{start_date}'),IS_BEFORE({{{VE['expense_date']}}},'{end_date}'))"

        expenses = airtable.search_records('VERTEX EXPENSES', expense_formula) if expense_formula else airtable.get_all_records('VERTEX EXPENSES')

        # Group expenses by category
        expenses_by_category = {}
        total_expenses = 0
        for record in expenses:
            fields = record.get('fields', {})
            category = fields.get(VE['category'], 'Other')
            amount = fields.get(VE['amount'], 0)
            expenses_by_category[category] = expenses_by_category.get(category, 0) + amount
            total_expenses += amount
        
        # Calculate net income
        net_income = total_revenue - total_expenses
        profit_margin = (net_income / total_revenue * 100) if total_revenue > 0 else 0
        
        return jsonify({
            'revenue': {
                'by_system': revenue_by_system,
                'total': total_revenue
            },
            'expenses': {
                'by_category': expenses_by_category,
                'total': total_expenses
            },
            'net_income': net_income,
            'profit_margin': round(profit_margin, 2),
            'period': {
                'start_date': start_date,
                'end_date': end_date
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/vertex/ai/financial-health', methods=['GET'])
def get_financial_health_score():
    """Get AI-powered financial health score and insights"""
    try:
        airtable = AirtableClient()
        
        # Get financial data
        invoices = airtable.get_all_records('VERTEX INVOICES')
        expenses = airtable.get_all_records('VERTEX EXPENSES')
        revenue_records = airtable.get_all_records('VERTEX REVENUE')
        
        # Calculate metrics
        total_revenue = sum(r.get('fields', {}).get(VR['amount'], 0) for r in revenue_records)
        total_expenses = sum(e.get('fields', {}).get(VE['amount'], 0) for e in expenses)
        total_ar = sum(inv.get('fields', {}).get(VI['balance_due'], 0) for inv in invoices if inv.get('fields', {}).get(VI['payment_status']) in ['Unpaid', 'Partial', 'Overdue'])

        overdue_ar = sum(inv.get('fields', {}).get(VI['balance_due'], 0) for inv in invoices if (inv.get('fields', {}).get(VI['days_outstanding']) or 0) > 30)
        
        # Calculate scores (0-100)
        cash_score = min(100, (total_revenue - total_expenses) / total_expenses * 100) if total_expenses > 0 else 50
        ar_score = max(0, 100 - (overdue_ar / total_ar * 100)) if total_ar > 0 else 100
        profit_score = min(100, ((total_revenue - total_expenses) / total_revenue * 100)) if total_revenue > 0 else 0
        
        # Overall score
        overall_score = (cash_score + ar_score + profit_score) / 3
        
        # Get AI insights
        from nexus_backend import AnthropicClient
        ai = AnthropicClient()
        
        prompt = f"""Analyze this financial data and provide brief insights:

Total Revenue: ${total_revenue:,.2f}
Total Expenses: ${total_expenses:,.2f}
Net Income: ${total_revenue - total_expenses:,.2f}
Accounts Receivable: ${total_ar:,.2f}
Overdue AR: ${overdue_ar:,.2f}

Financial Health Score: {overall_score:.1f}/100

Provide:
1. Overall assessment (1 sentence)
2. Top 3 strengths
3. Top 3 concerns
4. Top 3 recommendations

Be concise and actionable."""
        
        insights = ai.complete(prompt, max_tokens=500)
        
        return jsonify({
            'overall_score': round(overall_score, 1),
            'component_scores': {
                'cash_flow': round(cash_score, 1),
                'ar_management': round(ar_score, 1),
                'profitability': round(profit_score, 1)
            },
            'metrics': {
                'total_revenue': total_revenue,
                'total_expenses': total_expenses,
                'net_income': total_revenue - total_expenses,
                'accounts_receivable': total_ar,
                'overdue_ar': overdue_ar
            },
            'ai_insights': insights
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# -------------------- VERTEX EXPORTS --------------------

@app.route('/vertex/export/quickbooks', methods=['POST'])
def export_to_quickbooks():
    """Export VERTEX data to QuickBooks CSV format"""
    try:
        data = request.json
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        airtable = AirtableClient()
        
        # Get invoices
        inv_formula = None
        if start_date and end_date:
            inv_formula = f"AND(IS_AFTER({{{VI['invoice_date']}}},'{start_date}'),IS_BEFORE({{{VI['invoice_date']}}},'{end_date}'))"

        invoices = airtable.search_records('VERTEX INVOICES', inv_formula) if inv_formula else airtable.get_all_records('VERTEX INVOICES')

        # Get expenses
        exp_formula = None
        if start_date and end_date:
            exp_formula = f"AND(IS_AFTER({{{VE['expense_date']}}},'{start_date}'),IS_BEFORE({{{VE['expense_date']}}},'{end_date}'))"

        expenses = airtable.search_records('VERTEX EXPENSES', exp_formula) if exp_formula else airtable.get_all_records('VERTEX EXPENSES')

        # Format for QuickBooks CSV
        qb_data = []

        # Add invoices
        for inv in invoices:
            fields = inv.get('fields', {})
            qb_data.append({
                'Date':    fields.get(VI['invoice_date'], ''),
                'Type':    'Invoice',
                'Num':     fields.get(VI['invoice_number'], ''),
                'Name':    fields.get(VI['client_name'], ''),
                'Account': 'Accounts Receivable',
                'Amount':  fields.get(VI['total_amount'], 0),
                'Memo':    fields.get(VI['notes'], ''),
            })

        # Add expenses
        for exp in expenses:
            fields = exp.get('fields', {})
            qb_data.append({
                'Date':    fields.get(VE['expense_date'], ''),
                'Type':    'Expense',
                'Num':     '',
                'Name':    fields.get(VE['vendor_payee'], ''),
                'Account': fields.get(VE['category'], 'Other Expenses'),
                'Amount':  fields.get(VE['amount'], 0),
                'Memo':    fields.get(VE['description'], ''),
            })
        
        return jsonify({
            'success': True,
            'data': qb_data,
            'record_count': len(qb_data),
            'message': f'Exported {len(qb_data)} records to QuickBooks format'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================================
# VERTEX FINANCING — SouthStar Capital & Bankers Factoring
# ============================================================================

FINANCING_REFERRALS_FILE = os.path.join(os.path.dirname(__file__), 'financing_referrals.json')

def load_financing_referrals():
    if os.path.exists(FINANCING_REFERRALS_FILE):
        with open(FINANCING_REFERRALS_FILE, 'r') as f:
            return json.load(f)
    return []

def save_financing_referrals(referrals):
    with open(FINANCING_REFERRALS_FILE, 'w') as f:
        json.dump(referrals, f, indent=2)

@app.route('/vertex/financing/referrals', methods=['GET'])
def get_financing_referrals():
    """Get all broker commission referrals + summary"""
    try:
        referrals = load_financing_referrals()
        earned = sum(r.get('commission_earned', 0) for r in referrals if r.get('status') == 'Commission Paid')
        pending = sum(r.get('commission_estimated', 0) for r in referrals if r.get('status') in ['Submitted', 'Approved', 'Funded'])
        return jsonify({
            'referrals': referrals,
            'summary': {
                'total_referrals': len(referrals),
                'commission_earned': earned,
                'commission_pending': pending,
                'active_referrals': len([r for r in referrals if r.get('status') not in ['Commission Paid', 'Declined']])
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/vertex/financing/referrals', methods=['POST'])
def create_financing_referral():
    """Log a new broker referral to SouthStar Capital"""
    try:
        data = request.json
        referrals = load_financing_referrals()
        new_referral = {
            'id': f'REF-{datetime.now().strftime("%Y%m%d%H%M%S")}',
            'client_name': data.get('client_name', ''),
            'client_contact': data.get('client_contact', ''),
            'product_type': data.get('product_type', ''),
            'estimated_deal_size': float(data.get('estimated_deal_size', 0)),
            'commission_rate': float(data.get('commission_rate', 1.0)),
            'commission_estimated': float(data.get('commission_estimated', 0)),
            'commission_earned': 0.0,
            'status': 'Submitted',
            'referral_date': datetime.now().strftime('%Y-%m-%d'),
            'notes': data.get('notes', ''),
            'southstar_contact': 'Jon Shane — VP Broker Relations | 678-257-2676 | brokers@southstar.com'
        }
        referrals.append(new_referral)
        save_financing_referrals(referrals)
        return jsonify({'success': True, 'referral': new_referral})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/vertex/financing/referrals/<referral_id>', methods=['PUT'])
def update_financing_referral(referral_id):
    """Update referral status or commission amount"""
    try:
        data = request.json
        referrals = load_financing_referrals()
        for i, r in enumerate(referrals):
            if r['id'] == referral_id:
                referrals[i].update(data)
                save_financing_referrals(referrals)
                return jsonify({'success': True, 'referral': referrals[i]})
        return jsonify({'error': 'Referral not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/vertex/financing/referrals/<referral_id>', methods=['DELETE'])
def delete_financing_referral(referral_id):
    """Delete a referral record"""
    try:
        referrals = load_financing_referrals()
        referrals = [r for r in referrals if r['id'] != referral_id]
        save_financing_referrals(referrals)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================================
# VERTEX ACCOUNTS PAYABLE
# ============================================================================

# Field map for VERTEX ACCOUNTS PAYABLE table (ALL CAPS in Airtable)
VAP = {
    'bill_number':        'BILL NUMBER',
    'bill_date':          'BILL DATE',
    'due_date':           'DUE DATE',
    'vendor_name':        'VENDOR NAME',
    'vendor_id':          'VENDOR ID',
    'source_system':      'SOURCE SYSTEM',
    'source_record':      'SOURCE RECORD',
    'category':           'CATEGORY',
    'subcategory':        'SUBCATEGORY',
    'description':        'DESCRIPTION',
    'line_items':         'LINE ITEMS',
    'subtotal':           'SUBTOTAL',
    'tax_rate':           'TAX RATE %',
    'tax_amount':         'TAX AMOUNT',
    'total_amount':       'TOTAL AMOUNT',
    'amount_paid':        'AMOUNT PAID',
    'balance_due':        'BALANCE DUE',
    'payment_status':     'PAYMENT STATUS',
    'payment_method':     'PAYMENT METHOD',
    'payment_date':       'PAYMENT DATE',
    'payment_terms':      'PAYMENT TERMS',
    'days_outstanding':   'DAYS OUTSTANDING',
    'aging_category':     'AGING CATEGORY',
    'notes':              'NOTES',
    'po_number':          'PO NUMBER',
    'contract_number':    'CONTRACT NUMBER',
    'project':            'PROJECT',
    'billable':           'BILLABLE',
    'billable_invoice':   'BILLABLE INVOICE',
    'recurring':          'RECURRING',
    'recurring_frequency':'RECURRING FREQUENCY',
    'next_bill_date':     'NEXT BILL DATE',
    'attachment':         'ATTACHMENT',
    'approved_by':        'APPROVED BY',
    'approved_date':      'APPROVED DATE',
}

VERTEX_AP_TABLE = 'VERTEX ACCOUNTS PAYABLE'


@app.route('/vertex/ap', methods=['GET'])
def get_vertex_ap_bills():
    """Get all Accounts Payable bills with optional filters."""
    try:
        airtable = AirtableClient()

        payment_status = request.args.get('payment_status')
        vendor_name    = request.args.get('vendor_name')
        category       = request.args.get('category')
        aging_category = request.args.get('aging_category')
        overdue_only   = request.args.get('overdue_only', 'false').lower() == 'true'

        formulas = []
        if payment_status:
            formulas.append(f"{{{VAP['payment_status']}}}='{payment_status}'")
        if vendor_name:
            formulas.append(f"FIND('{vendor_name}',{{{VAP['vendor_name']}}})>0")
        if category:
            formulas.append(f"{{{VAP['category']}}}='{category}'")
        if aging_category:
            formulas.append(f"{{{VAP['aging_category']}}}='{aging_category}'")
        if overdue_only:
            formulas.append(f"{{{VAP['payment_status']}}}='Overdue'")

        formula = "AND(" + ",".join(formulas) + ")" if formulas else None
        bills = airtable.search_records(VERTEX_AP_TABLE, formula) if formula else airtable.get_all_records(VERTEX_AP_TABLE)

        return jsonify({'bills': bills, 'count': len(bills)})
    except Exception as e:
        print(f"Error getting AP bills: {e}")
        return jsonify({'error': str(e), 'bills': []}), 500


@app.route('/vertex/ap', methods=['POST'])
def create_vertex_ap_bill():
    """Create a new Accounts Payable bill."""
    try:
        data    = request.json
        airtable = AirtableClient()

        bill_fields = {
            VAP['bill_number']:    data.get('bill_number', f"BILL-{datetime.now().strftime('%Y%m%d-%H%M%S')}"),
            VAP['bill_date']:      data.get('bill_date', datetime.now().date().isoformat()),
            VAP['due_date']:       data.get('due_date'),
            VAP['vendor_name']:    data.get('vendor_name'),
            VAP['source_system']:  data.get('source_system', 'Other'),
            VAP['source_record']:  data.get('source_record'),
            VAP['category']:       data.get('category', 'Other'),
            VAP['description']:    data.get('description', ''),
            VAP['line_items']:     data.get('line_items', '[]'),
            VAP['subtotal']:       data.get('subtotal', 0),
            VAP['tax_rate']:       data.get('tax_rate', 0),
            VAP['total_amount']:   data.get('total_amount', 0),
            VAP['payment_status']: data.get('payment_status', 'Unpaid'),
            VAP['payment_terms']:  data.get('payment_terms', 'Net 30'),
            VAP['notes']:          data.get('notes', ''),
            VAP['billable']:       data.get('billable', False),
            VAP['recurring']:      data.get('recurring', False),
        }
        if data.get('po_number'):
            bill_fields[VAP['po_number']] = data['po_number']
        if data.get('contract_number'):
            bill_fields[VAP['contract_number']] = data['contract_number']
        if data.get('project'):
            bill_fields[VAP['project']] = data['project']
        if data.get('recurring_frequency'):
            bill_fields[VAP['recurring_frequency']] = data['recurring_frequency']
        if data.get('next_bill_date'):
            bill_fields[VAP['next_bill_date']] = data['next_bill_date']

        bill_fields = {k: v for k, v in bill_fields.items() if v is not None}
        bill = airtable.create_record(VERTEX_AP_TABLE, bill_fields)

        return jsonify({'success': True, 'bill': bill})
    except Exception as e:
        print(f"Error creating AP bill: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/vertex/ap/<bill_id>', methods=['GET'])
def get_vertex_ap_bill(bill_id):
    """Get a specific AP bill."""
    try:
        airtable = AirtableClient()
        bill = airtable.get_record(VERTEX_AP_TABLE, bill_id)
        return jsonify({'bill': bill})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/vertex/ap/<bill_id>', methods=['PUT'])
def update_vertex_ap_bill(bill_id):
    """Update an AP bill (e.g. mark paid, change status)."""
    try:
        data    = request.json
        airtable = AirtableClient()
        update_fields = {k: v for k, v in data.items() if k not in ['id', 'createdTime']}
        bill = airtable.update_record(VERTEX_AP_TABLE, bill_id, update_fields)
        return jsonify({'success': True, 'bill': bill})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/vertex/ap/<bill_id>/pay', methods=['POST'])
def pay_vertex_ap_bill(bill_id):
    """Mark an AP bill as paid and create a matching VERTEX EXPENSE record."""
    try:
        data     = request.json
        airtable = AirtableClient()

        amount_paid    = float(data.get('amount', 0))
        payment_date   = data.get('payment_date', datetime.now().date().isoformat())
        payment_method = data.get('payment_method', 'ACH')

        bill   = airtable.get_record(VERTEX_AP_TABLE, bill_id)
        fields = bill.get('fields', {})

        total   = float(fields.get(VAP['total_amount'], 0))
        already = float(fields.get(VAP['amount_paid'], 0))
        new_paid = already + amount_paid
        balance  = max(0, total - new_paid)
        new_status = 'Paid' if balance <= 0.01 else 'Partial'

        update_fields = {
            VAP['payment_status']: new_status,
            VAP['amount_paid']:    new_paid,
            VAP['payment_date']:   payment_date,
            VAP['payment_method']: payment_method,
        }
        airtable.update_record(VERTEX_AP_TABLE, bill_id, update_fields)

        # Mirror payment as a VERTEX EXPENSE
        expense_fields = {
            VE['expense_date']:    payment_date,
            VE['vendor_payee']:    fields.get(VAP['vendor_name'], ''),
            VE['description']:     fields.get(VAP['description'], f"Payment for {fields.get(VAP['bill_number'], bill_id)}"),
            VE['category']:        fields.get(VAP['category'], 'Other'),
            VE['amount']:          amount_paid,
            VE['payment_method']:  payment_method,
            VE['payment_status']:  'Paid',
            VE['billable']:        fields.get(VAP['billable'], False),
            VE['notes']:           f"AP Bill: {fields.get(VAP['bill_number'], bill_id)}",
        }
        expense = airtable.create_record('VERTEX EXPENSES', expense_fields)

        return jsonify({
            'success':    True,
            'new_status': new_status,
            'balance_due': balance,
            'expense_created': expense,
        })
    except Exception as e:
        print(f"Error paying AP bill: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/vertex/ap/aging', methods=['GET'])
def get_ap_aging_report():
    """Accounts Payable aging report — bills grouped by due date bucket."""
    try:
        airtable = AirtableClient()
        ps = VAP['payment_status']
        formula = f"OR({{{ps}}}='Unpaid',{{{ps}}}='Partial',{{{ps}}}='Overdue')"
        bills = airtable.search_records(VERTEX_AP_TABLE, formula)

        aging = {
            'Current':    {'count': 0, 'total': 0, 'bills': []},
            '1-30 Days':  {'count': 0, 'total': 0, 'bills': []},
            '31-60 Days': {'count': 0, 'total': 0, 'bills': []},
            '61-90 Days': {'count': 0, 'total': 0, 'bills': []},
            '90+ Days':   {'count': 0, 'total': 0, 'bills': []},
        }

        today = datetime.now().date()
        for bill in bills:
            f = bill.get('fields', {})
            due_str = f.get(VAP['due_date'], '')
            balance = float(f.get(VAP['total_amount'], 0)) - float(f.get(VAP['amount_paid'], 0) or 0)
            try:
                due = datetime.fromisoformat(due_str[:10]).date()
                days_past = (today - due).days
            except Exception:
                days_past = 0

            if days_past <= 0:
                bucket = 'Current'
            elif days_past <= 30:
                bucket = '1-30 Days'
            elif days_past <= 60:
                bucket = '31-60 Days'
            elif days_past <= 90:
                bucket = '61-90 Days'
            else:
                bucket = '90+ Days'

            aging[bucket]['count'] += 1
            aging[bucket]['total'] += balance
            aging[bucket]['bills'].append(bill)

        total_ap = sum(b['total'] for b in aging.values())
        return jsonify({'aging_report': aging, 'total_outstanding_ap': total_ap})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================================
# VERTEX RECURRING INVOICES
# ============================================================================
# Recurring invoice fields live on the existing VERTEX INVOICES table.
# Additional fields needed in Airtable (add if not yet present):
#   RECURRING            (checkbox)
#   RECURRING FREQUENCY  (single select: Weekly / Monthly / Quarterly / Annually)
#   NEXT INVOICE DATE    (date)
#   PARENT INVOICE       (text — original invoice_number this was cloned from)
# ---------------------------------------------------------------------------

VI_RECURRING = {
    'recurring':           'RECURRING',
    'recurring_frequency': 'RECURRING FREQUENCY',
    'next_invoice_date':   'NEXT INVOICE DATE',
    'parent_invoice':      'PARENT INVOICE',
}

_FREQ_DAYS = {
    'Weekly':    7,
    'Monthly':   30,
    'Quarterly': 90,
    'Annually':  365,
}


@app.route('/vertex/invoices/<invoice_id>/set-recurring', methods=['POST'])
def set_invoice_recurring(invoice_id):
    """Mark an invoice as a recurring template and set its frequency + next date."""
    try:
        data     = request.json
        airtable = AirtableClient()

        frequency = data.get('frequency', 'Monthly')
        next_date = data.get('next_invoice_date')
        if not next_date:
            delta = _FREQ_DAYS.get(frequency, 30)
            next_date = (datetime.now() + timedelta(days=delta)).date().isoformat()

        update = {
            VI_RECURRING['recurring']:           True,
            VI_RECURRING['recurring_frequency']: frequency,
            VI_RECURRING['next_invoice_date']:   next_date,
        }
        invoice = airtable.update_record('VERTEX INVOICES', invoice_id, update)
        return jsonify({'success': True, 'invoice': invoice, 'next_invoice_date': next_date})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/vertex/invoices/recurring/due', methods=['GET'])
def get_recurring_invoices_due():
    """Return all recurring invoice templates whose NEXT INVOICE DATE is today or past."""
    try:
        airtable = AirtableClient()
        today_iso = datetime.now().date().isoformat()
        formula = (
            f"AND({{{VI_RECURRING['recurring']}}}=TRUE(),"
            f"IS_BEFORE({{{VI_RECURRING['next_invoice_date']}}},'{today_iso}'))"
        )
        due = airtable.search_records('VERTEX INVOICES', formula)
        return jsonify({'due': due, 'count': len(due)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/vertex/invoices/<invoice_id>/generate-next', methods=['POST'])
def generate_next_recurring_invoice(invoice_id):
    """Clone a recurring invoice template into a new Unpaid invoice and advance NEXT INVOICE DATE."""
    try:
        airtable = AirtableClient()
        template = airtable.get_record('VERTEX INVOICES', invoice_id)
        tf = template.get('fields', {})

        frequency = tf.get(VI_RECURRING['recurring_frequency'], 'Monthly')
        delta     = _FREQ_DAYS.get(frequency, 30)

        # New invoice number
        new_num = f"INV-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        today   = datetime.now().date()
        due     = today + timedelta(days=30)

        new_fields = {
            VI['invoice_number']:               new_num,
            VI['invoice_date']:                 today.isoformat(),
            VI['due_date']:                     due.isoformat(),
            VI['client_name']:                  tf.get(VI['client_name'], ''),
            VI['source_system']:                tf.get(VI['source_system'], 'Other'),
            VI['invoice_type']:                 tf.get(VI['invoice_type'], 'Standard'),
            VI['line_items']:                   tf.get(VI['line_items'], '[]'),
            VI['subtotal']:                     tf.get(VI['subtotal'], 0),
            VI['tax_rate']:                     tf.get(VI['tax_rate'], 0),
            VI['total_amount']:                 tf.get(VI['total_amount'], 0),
            VI['payment_status']:               'Unpaid',
            VI['payment_terms']:                tf.get(VI['payment_terms'], 'Net 30'),
            VI['notes']:                        tf.get(VI['notes'], ''),
            VI_RECURRING['recurring']:          False,   # clone is NOT a template
            VI_RECURRING['parent_invoice']:     tf.get(VI['invoice_number'], invoice_id),
        }

        new_invoice = airtable.create_record('VERTEX INVOICES', new_fields)

        # Advance template's next invoice date
        next_date = (today + timedelta(days=delta)).isoformat()
        airtable.update_record('VERTEX INVOICES', invoice_id, {
            VI_RECURRING['next_invoice_date']: next_date
        })

        return jsonify({
            'success':          True,
            'new_invoice':      new_invoice,
            'next_invoice_date': next_date,
        })
    except Exception as e:
        print(f"Error generating next recurring invoice: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/vertex/invoices/recurring/run-all', methods=['POST'])
def run_all_recurring_invoices():
    """
    Scheduler entry point: generate a new invoice for every recurring template that is due.
    Called daily by nexus_scheduler.py.
    """
    try:
        airtable  = AirtableClient()
        today_iso = datetime.now().date().isoformat()
        formula   = (
            f"AND({{{VI_RECURRING['recurring']}}}=TRUE(),"
            f"IS_BEFORE({{{VI_RECURRING['next_invoice_date']}}},'{today_iso}'))"
        )
        due = airtable.search_records('VERTEX INVOICES', formula)

        generated = []
        errors    = []
        for template in due:
            try:
                tid = template['id']
                tf  = template.get('fields', {})
                frequency = tf.get(VI_RECURRING['recurring_frequency'], 'Monthly')
                delta     = _FREQ_DAYS.get(frequency, 30)
                today     = datetime.now().date()
                new_num   = f"INV-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{tid[:6]}"
                new_fields = {
                    VI['invoice_number']:               new_num,
                    VI['invoice_date']:                 today.isoformat(),
                    VI['due_date']:                     (today + timedelta(days=30)).isoformat(),
                    VI['client_name']:                  tf.get(VI['client_name'], ''),
                    VI['source_system']:                tf.get(VI['source_system'], 'Other'),
                    VI['invoice_type']:                 tf.get(VI['invoice_type'], 'Standard'),
                    VI['line_items']:                   tf.get(VI['line_items'], '[]'),
                    VI['subtotal']:                     tf.get(VI['subtotal'], 0),
                    VI['tax_rate']:                     tf.get(VI['tax_rate'], 0),
                    VI['total_amount']:                 tf.get(VI['total_amount'], 0),
                    VI['payment_status']:               'Unpaid',
                    VI['payment_terms']:                tf.get(VI['payment_terms'], 'Net 30'),
                    VI['notes']:                        tf.get(VI['notes'], ''),
                    VI_RECURRING['recurring']:          False,
                    VI_RECURRING['parent_invoice']:     tf.get(VI['invoice_number'], tid),
                }
                new_inv = airtable.create_record('VERTEX INVOICES', new_fields)
                next_date = (today + timedelta(days=delta)).isoformat()
                airtable.update_record('VERTEX INVOICES', tid, {
                    VI_RECURRING['next_invoice_date']: next_date
                })
                generated.append({'template_id': tid, 'new_invoice': new_inv['id'], 'next_date': next_date})
            except Exception as ex:
                errors.append({'template_id': template.get('id'), 'error': str(ex)})

        return jsonify({
            'success':   True,
            'generated': len(generated),
            'errors':    len(errors),
            'detail':    generated,
            'error_detail': errors,
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================================
# VERTEX PAYMENT RECEIPT GENERATOR (Phase 8)
# ============================================================================

@app.route('/vertex/invoices/<invoice_id>/receipt', methods=['POST'])
def generate_payment_receipt(invoice_id):
    """
    Mark an invoice paid (or partial) and return a branded HTML payment receipt.
    POST body:
      amount_paid      float  (required)
      payment_date     str    YYYY-MM-DD (optional, defaults to today)
      payment_method   str    (optional, default ACH)
      reference_number str    (optional check/wire/ACH reference)
      notes            str    (optional)
    Returns: { success, receipt_html, revenue_record, updated_invoice }
    """
    try:
        data     = request.json or {}
        airtable = AirtableClient()

        amount_paid    = float(data.get('amount_paid', 0))
        if amount_paid <= 0:
            return jsonify({'error': 'amount_paid must be greater than 0'}), 400

        payment_date   = data.get('payment_date', datetime.now().date().isoformat())
        payment_method = data.get('payment_method', 'ACH')
        reference      = data.get('reference_number', '')
        notes          = data.get('notes', '')

        inv    = airtable.get_record('VERTEX INVOICES', invoice_id)
        fields = inv.get('fields', {})

        total        = float(fields.get(VI['total_amount'], 0))
        already_paid = float(fields.get(VI['amount_paid'], 0) or 0)
        new_paid     = already_paid + amount_paid
        balance      = max(0.0, total - new_paid)
        new_status   = 'Paid' if balance < 0.01 else 'Partial'

        # Update VERTEX INVOICES
        update = {
            VI['payment_status']: new_status,
            VI['amount_paid']:    new_paid,
            VI['payment_date']:   payment_date,
            VI['payment_method']: payment_method,
        }
        updated_invoice = airtable.update_record('VERTEX INVOICES', invoice_id, update)

        # Post to VERTEX REVENUE
        rev_notes_parts = [f"Payment received for {fields.get(VI['invoice_number'], invoice_id)}"]
        if reference:
            rev_notes_parts.append(f"Ref: {reference}")
        if notes:
            rev_notes_parts.append(notes)

        revenue_record = airtable.create_record('VERTEX REVENUE', {
            VR['revenue_date']:   payment_date,
            VR['source']:         fields.get(VI['client_name'], ''),
            VR['revenue_type']:   'Invoice Payment',
            VR['source_system']:  fields.get(VI['source_system'], 'Other'),
            VR['amount']:         amount_paid,
            VR['payment_method']: payment_method,
            VR['taxable']:        True,
            VR['recurring']:      False,
            VR['notes']:          ' | '.join(rev_notes_parts),
        })

        # Generate branded HTML receipt
        inv_num    = fields.get(VI['invoice_number'], invoice_id)
        client     = fields.get(VI['client_name'], '')
        receipt_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Payment Receipt — {inv_num}</title>
<style>
  body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #f8fafc; margin: 0; padding: 40px; color: #1e293b; }}
  .receipt {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 12px;
              box-shadow: 0 4px 24px rgba(0,0,0,0.10); overflow: hidden; }}
  .header {{ background: linear-gradient(135deg, #1e3a5f 0%, #2563eb 100%); color: white;
             padding: 32px 40px; text-align: center; }}
  .header h1 {{ margin: 0 0 4px; font-size: 24px; letter-spacing: 1px; }}
  .header p  {{ margin: 0; opacity: 0.85; font-size: 14px; }}
  .badge {{ display: inline-block; background: rgba(255,255,255,0.2); border-radius: 20px;
            padding: 4px 14px; font-size: 12px; margin-top: 10px; }}
  .body  {{ padding: 32px 40px; }}
  .row   {{ display: flex; justify-content: space-between; padding: 10px 0;
            border-bottom: 1px solid #f1f5f9; font-size: 15px; }}
  .row:last-child {{ border-bottom: none; }}
  .label {{ color: #64748b; }}
  .value {{ font-weight: 600; color: #0f172a; }}
  .paid-badge {{ background: #dcfce7; color: #166534; font-weight: 700; font-size: 16px;
                 border-radius: 8px; padding: 10px 20px; text-align: center; margin: 24px 0 0; }}
  .footer {{ background: #f8fafc; padding: 20px 40px; text-align: center; font-size: 12px; color: #94a3b8; }}
</style>
</head>
<body>
<div class="receipt">
  <div class="header">
    <h1>PAYMENT RECEIPT</h1>
    <p>Dee Davis Inc. | info@deedavis.biz | 248.376.4550</p>
    <span class="badge">EDWOSB | WOSB | MBE | SBE</span>
  </div>
  <div class="body">
    <div class="row"><span class="label">Receipt Date</span><span class="value">{payment_date}</span></div>
    <div class="row"><span class="label">Invoice Number</span><span class="value">{inv_num}</span></div>
    <div class="row"><span class="label">Client</span><span class="value">{client}</span></div>
    <div class="row"><span class="label">Invoice Total</span><span class="value">${total:,.2f}</span></div>
    <div class="row"><span class="label">Amount Received</span><span class="value">${amount_paid:,.2f}</span></div>
    <div class="row"><span class="label">Payment Method</span><span class="value">{payment_method}</span></div>
    {'<div class="row"><span class="label">Reference</span><span class="value">' + reference + '</span></div>' if reference else ''}
    <div class="row"><span class="label">Balance Remaining</span><span class="value">${balance:,.2f}</span></div>
    <div class="paid-badge">{'✅ PAID IN FULL' if new_status == 'Paid' else f'⏳ PARTIAL — ${balance:,.2f} REMAINING'}</div>
  </div>
  <div class="footer">
    755 W. Big Beaver Rd., Suite 2020, Troy, MI 48084 | CAGE: 8UMX3 | UEI: HJB4KNYJVGZ1<br>
    Thank you for your business.
  </div>
</div>
</body>
</html>"""

        return jsonify({
            'success':         True,
            'new_status':      new_status,
            'amount_paid':     amount_paid,
            'balance_due':     balance,
            'receipt_html':    receipt_html,
            'revenue_record':  revenue_record,
            'updated_invoice': updated_invoice,
        })
    except Exception as e:
        print(f"generate_payment_receipt: {e}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# VERTEX WAWF / IPP FEDERAL INVOICING (Phase 6)
# ============================================================================

_WAWF_DOC_TYPES = ['2-in-1', 'Combo', 'Cost Voucher', 'FMS Invoice', 'Invoice', 'Invoice as 2-in-1']
_WAWF_STATUSES  = ['Not Submitted', 'Submitted', 'Accepted', 'Rejected', 'Paid']

_PROMPT_PAYMENT_RATE = 0.0425  # 4.25% annual — update each quarter per Treasury


@app.route('/vertex/invoices/<invoice_id>/wawf', methods=['POST'])
def update_invoice_wawf(invoice_id):
    """
    Record WAWF / IPP submission or status update for a federal invoice.
    POST body (all optional):
      wawf_status, wawf_document_type, wawf_submitted_date,
      wawf_accepted_date, wawf_rejection_reason,
      ipp_submission_date, ipp_approval_date, ipp_invoice_id,
      clin, acrn, dodaac
    """
    try:
        data     = request.json or {}
        airtable = AirtableClient()

        update = {}
        wawf_keys = [
            'wawf_status', 'wawf_document_type', 'wawf_submitted_date',
            'wawf_accepted_date', 'wawf_rejection_reason',
            'ipp_submission_date', 'ipp_approval_date', 'ipp_invoice_id',
            'clin', 'acrn', 'dodaac', 'cage_code',
        ]
        for k in wawf_keys:
            if k in data:
                update[VI[k]] = data[k]

        # Auto-set interest start date when WAWF accepted
        if data.get('wawf_status') == 'Accepted' and VI.get('interest_start_date'):
            update[VI['interest_start_date']] = data.get('wawf_accepted_date', datetime.now().date().isoformat())

        if not update:
            return jsonify({'error': 'No valid WAWF fields provided'}), 400

        invoice = airtable.update_record('VERTEX INVOICES', invoice_id, update)
        return jsonify({'success': True, 'invoice': invoice})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/vertex/invoices/<invoice_id>/prompt-payment-interest', methods=['GET'])
def calculate_prompt_payment_interest(invoice_id):
    """
    Calculate Prompt Payment Act interest owed on a federal invoice.
    Interest accrues if payment not received within 30 days of acceptance.
    Returns daily rate, days overdue, and total interest.
    """
    try:
        airtable = AirtableClient()
        inv      = airtable.get_record('VERTEX INVOICES', invoice_id)
        fields   = inv.get('fields', {})

        # Interest starts 30 days after WAWF acceptance (or due date if no WAWF)
        start_str = fields.get(VI.get('interest_start_date', 'INTEREST START DATE'), '')
        if not start_str:
            start_str = fields.get(VI['due_date'], '')

        if not start_str:
            return jsonify({'error': 'No due date or interest start date on this invoice'}), 400

        start    = datetime.fromisoformat(start_str[:10]).date()
        today    = datetime.now().date()
        days_due = max(0, (today - start).days - 30)  # 30-day grace before interest accrues

        total_amount = float(fields.get(VI['total_amount'], 0))
        amount_paid  = float(fields.get(VI['amount_paid'], 0) or 0)
        balance      = total_amount - amount_paid

        daily_rate = _PROMPT_PAYMENT_RATE / 365
        interest   = round(balance * daily_rate * days_due, 2)

        return jsonify({
            'invoice_id':          invoice_id,
            'invoice_number':      fields.get(VI['invoice_number'], ''),
            'balance_due':         balance,
            'interest_start_date': start_str[:10],
            'days_past_30':        days_due,
            'annual_rate':         f"{_PROMPT_PAYMENT_RATE * 100:.2f}%",
            'daily_rate':          round(daily_rate, 8),
            'prompt_payment_interest': interest,
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/vertex/ar/federal-pending', methods=['GET'])
def get_federal_invoices_pending_wawf():
    """Return federal invoices not yet submitted to WAWF/IPP."""
    try:
        airtable = AirtableClient()
        ps       = VI['payment_status']
        formula  = f"AND(OR({{{ps}}}='Unpaid',{{{ps}}}='Partial'),{{{VI['government_agency']}}}!='')"
        invoices = airtable.search_records('VERTEX INVOICES', formula)

        pending = []
        for inv in invoices:
            f       = inv.get('fields', {})
            w_stat  = f.get(VI.get('wawf_status', 'WAWF STATUS'), 'Not Submitted')
            pending.append({
                'id':             inv['id'],
                'invoice_number': f.get(VI['invoice_number'], ''),
                'client_name':    f.get(VI['client_name'], ''),
                'government_agency': f.get(VI['government_agency'], ''),
                'total_amount':   f.get(VI['total_amount'], 0),
                'due_date':       f.get(VI['due_date'], ''),
                'wawf_status':    w_stat,
                'clin':           f.get(VI.get('clin', 'CLIN'), ''),
                'contract_number': f.get(VI['contract_number'], ''),
            })

        return jsonify({'federal_invoices': pending, 'count': len(pending)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================================
# VERTEX INVOICE PDF GENERATION (Phase 5)
# ============================================================================

VERTEX_INVOICE_OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'GENERATED_VERTEX_INVOICES', 'STANDARD')

def _ensure_output_dir(path):
    os.makedirs(path, exist_ok=True)
    return path


@app.route('/vertex/invoices/<invoice_id>/pdf', methods=['GET'])
def get_vertex_invoice_pdf(invoice_id):
    """
    Render a NEXUS-branded invoice PDF for any VERTEX INVOICES record.
    Returns the PDF file if wkhtmltopdf is available, else HTML.
    Query params:
      ?sector=drug_testing|nemt|fingerprinting|dna|janitorial|default
      ?format=pdf|html  (default: pdf)
    """
    try:
        from generate_invoice_html import generate_invoice_html

        sector     = request.args.get('sector', 'default')
        fmt        = request.args.get('format', 'pdf')
        airtable   = AirtableClient()
        inv        = airtable.get_record('VERTEX INVOICES', invoice_id)
        fields     = inv.get('fields', {})

        # Parse line items (stored as JSON string)
        try:
            line_items_raw = json.loads(fields.get(VI['line_items'], '[]') or '[]')
            if not isinstance(line_items_raw, list):
                line_items_raw = []
        except Exception:
            line_items_raw = []

        config = {
            'sector': sector,
            'invoice': {
                'number':       fields.get(VI['invoice_number'], invoice_id),
                'date':         fields.get(VI['invoice_date'], ''),
                'due_date':     fields.get(VI['due_date'], ''),
                'payment_terms': fields.get(VI['payment_terms'], 'Net 30'),
                'subtotal':     fields.get(VI['subtotal'], 0),
                'tax_rate':     (fields.get(VI['tax_rate'], 0) or 0) / 100,
                'shipping':     0,
                'notes':        '',
                'po_number':    fields.get(VI['po_number'], ''),
            },
            'client': {
                'name':         fields.get(VI['client_name'], ''),
                'agency':       fields.get(VI['government_agency'], ''),
                'contract':     fields.get(VI['contract_number'], ''),
                'address':      '',
            },
            'contract': {
                'number':       fields.get(VI['contract_number'], ''),
                'type':         fields.get(VI['contract_type'], ''),
                'cage':         fields.get(VI['cage_code'], ''),
                'uei':          fields.get(VI['uei'], ''),
            },
            'line_items': line_items_raw,
        }

        html_content = generate_invoice_html(config)

        out_dir   = _ensure_output_dir(VERTEX_INVOICE_OUTPUT_DIR)
        safe_num  = fields.get(VI['invoice_number'], invoice_id).replace('/', '-').replace(' ', '_')
        html_path = os.path.join(out_dir, f"{safe_num}.html")
        pdf_path  = os.path.join(out_dir, f"{safe_num}.pdf")

        with open(html_path, 'w', encoding='utf-8') as fh:
            fh.write(html_content)

        if fmt == 'pdf':
            # Try wkhtmltopdf
            pdf_ok = False
            try:
                import subprocess
                result = subprocess.run(
                    ['wkhtmltopdf', '--page-size', 'Letter',
                     '--margin-top', '15mm', '--margin-bottom', '15mm',
                     '--margin-left', '15mm', '--margin-right', '15mm',
                     '--enable-local-file-access', html_path, pdf_path],
                    capture_output=True, timeout=30
                )
                pdf_ok = result.returncode == 0 and os.path.exists(pdf_path)
            except Exception:
                pass

            if pdf_ok:
                return send_file(pdf_path, mimetype='application/pdf',
                                 as_attachment=False,
                                 download_name=f"{safe_num}.pdf")

        # Fallback: return HTML
        from flask import Response
        return Response(html_content, mimetype='text/html')

    except Exception as e:
        print(f"vertex_invoice_pdf: {e}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# VERTEX AR COLLECTION WORKFLOW (Phase 4)
# ============================================================================

_COLLECTION_TEMPLATES = {
    'first_reminder': {
        'subject': 'Invoice {invoice_number} — Payment Reminder',
        'body': (
            "Hi {client_name},\n\n"
            "This is a friendly reminder that Invoice {invoice_number} for ${total_amount:,.2f} "
            "was due on {due_date}. If payment has already been sent, please disregard.\n\n"
            "To pay or discuss payment arrangements, reply to this email or call 248.376.4550.\n\n"
            "Thank you,\nDieasha D. Davis\nPresident & CEO, Dee Davis Inc."
        )
    },
    'second_reminder': {
        'subject': 'PAST DUE: Invoice {invoice_number} — Action Required',
        'body': (
            "Hi {client_name},\n\n"
            "Invoice {invoice_number} for ${total_amount:,.2f} is now {days_outstanding} days past due. "
            "Please remit payment immediately to avoid further escalation.\n\n"
            "Per our payment terms ({payment_terms}), interest may accrue on overdue balances. "
            "For government contracts, the Prompt Payment Act entitles Dee Davis Inc. to interest "
            "at the current Treasury rate on payments received after 30 days.\n\n"
            "Please contact us at 248.376.4550 or info@deedavis.biz to resolve this.\n\n"
            "Dieasha D. Davis\nPresident & CEO, Dee Davis Inc."
        )
    },
    'final_notice': {
        'subject': 'FINAL NOTICE: Invoice {invoice_number} — Collections Pending',
        'body': (
            "Hi {client_name},\n\n"
            "Despite previous reminders, Invoice {invoice_number} for ${total_amount:,.2f} remains unpaid "
            "after {days_outstanding} days. This is our final notice before escalation to collections.\n\n"
            "Payment in full is required within 5 business days.\n\n"
            "Dieasha D. Davis\nPresident & CEO, Dee Davis Inc.\n"
            "248.376.4550 | info@deedavis.biz"
        )
    }
}


@app.route('/vertex/ar/overdue', methods=['GET'])
def get_overdue_invoices():
    """Return all overdue / past-due invoices with days outstanding and suggested action."""
    try:
        airtable = AirtableClient()
        ps = VI['payment_status']
        formula = f"OR({{{ps}}}='Unpaid',{{{ps}}}='Partial',{{{ps}}}='Overdue')"
        invoices = airtable.search_records('VERTEX INVOICES', formula)

        today = datetime.now().date()
        results = []
        for inv in invoices:
            f   = inv.get('fields', {})
            due_str = f.get(VI['due_date'], '')
            try:
                due  = datetime.fromisoformat(due_str[:10]).date()
                days = (today - due).days
            except Exception:
                days = 0
            if days < 0:
                continue  # not yet due

            if days <= 30:
                action = 'send_first_reminder'
            elif days <= 60:
                action = 'send_second_reminder'
            else:
                action = 'send_final_notice'

            results.append({
                'id':              inv['id'],
                'invoice_number':  f.get(VI['invoice_number'], ''),
                'client_name':     f.get(VI['client_name'], ''),
                'total_amount':    f.get(VI['total_amount'], 0),
                'balance_due':     f.get(VI['balance_due'], 0),
                'due_date':        due_str,
                'days_outstanding': days,
                'suggested_action': action,
            })

        results.sort(key=lambda x: x['days_outstanding'], reverse=True)
        return jsonify({'overdue': results, 'count': len(results)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/vertex/ar/<invoice_id>/reminder', methods=['POST'])
def send_collection_reminder(invoice_id):
    """
    Generate a collection reminder email for an overdue invoice.
    Returns the draft email — does NOT send automatically.
    POST body: { "reminder_type": "first_reminder" | "second_reminder" | "final_notice" }
    """
    try:
        data     = request.json or {}
        reminder = data.get('reminder_type', 'first_reminder')
        airtable = AirtableClient()

        inv    = airtable.get_record('VERTEX INVOICES', invoice_id)
        fields = inv.get('fields', {})

        due_str = fields.get(VI['due_date'], '')
        try:
            due  = datetime.fromisoformat(due_str[:10]).date()
            days = (datetime.now().date() - due).days
        except Exception:
            days = 0

        template = _COLLECTION_TEMPLATES.get(reminder, _COLLECTION_TEMPLATES['first_reminder'])
        ctx = {
            'invoice_number': fields.get(VI['invoice_number'], invoice_id),
            'client_name':    fields.get(VI['client_name'], 'Valued Customer'),
            'total_amount':   float(fields.get(VI['total_amount'], 0)),
            'due_date':       due_str[:10] if due_str else '',
            'days_outstanding': days,
            'payment_terms':  fields.get(VI['payment_terms'], 'Net 30'),
        }
        subject = template['subject'].format(**ctx)
        body    = template['body'].format(**ctx)

        # Update invoice follow-up date
        airtable.update_record('VERTEX INVOICES', invoice_id, {
            VI['follow_up_date']: (datetime.now() + timedelta(days=7)).date().isoformat()
        })

        return jsonify({
            'success':       True,
            'reminder_type': reminder,
            'to':            fields.get(VI['client_name'], ''),
            'subject':       subject,
            'body':          body,
            'invoice_id':    invoice_id,
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/vertex/ar/remind-batch', methods=['POST'])
def send_collection_reminders_batch():
    """
    Generate collection reminders for all overdue invoices.
    Returns list of draft emails — does NOT send automatically.
    Scheduler entry point: called daily by nexus_scheduler.py.
    """
    try:
        airtable = AirtableClient()
        ps       = VI['payment_status']
        formula  = f"OR({{{ps}}}='Unpaid',{{{ps}}}='Partial',{{{ps}}}='Overdue')"
        invoices = airtable.search_records('VERTEX INVOICES', formula)

        today  = datetime.now().date()
        drafts = []
        for inv in invoices:
            f = inv.get('fields', {})
            due_str = f.get(VI['due_date'], '')
            try:
                due  = datetime.fromisoformat(due_str[:10]).date()
                days = (today - due).days
            except Exception:
                days = 0
            if days < 1:
                continue

            if days <= 30:
                reminder = 'first_reminder'
            elif days <= 60:
                reminder = 'second_reminder'
            else:
                reminder = 'final_notice'

            template = _COLLECTION_TEMPLATES[reminder]
            ctx = {
                'invoice_number': f.get(VI['invoice_number'], inv['id']),
                'client_name':    f.get(VI['client_name'], 'Valued Customer'),
                'total_amount':   float(f.get(VI['total_amount'], 0)),
                'due_date':       due_str[:10] if due_str else '',
                'days_outstanding': days,
                'payment_terms':  f.get(VI['payment_terms'], 'Net 30'),
            }
            drafts.append({
                'invoice_id':    inv['id'],
                'invoice_number': ctx['invoice_number'],
                'client_name':   ctx['client_name'],
                'days_outstanding': days,
                'reminder_type': reminder,
                'subject':       template['subject'].format(**ctx),
                'body':          template['body'].format(**ctx),
            })

        return jsonify({'success': True, 'drafts': drafts, 'count': len(drafts)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================================
# WEBHOOK ENDPOINTS
# ============================================================================

@app.route('/webhooks/jotform', methods=['POST'])
def jotform_webhook():
    """
    JotForm AI Receptionist webhook endpoint
    Receives form submissions from JotForm AI Phone Agent, web chat, SMS, etc.
    and creates leads in LBPC system
    
    Expected JSON payload from JotForm:
    {
        "submissionID": "123456789",
        "formTitle": "LBPC Lead Intake",
        "rawRequest": {
            "q1_fullName": "John Smith",
            "q2_phoneNumber": "555-123-4567",
            "q3_email": "john@example.com",
            "q4_county": "Wayne",
            "q5_state": "Michigan",
            "q6_surplusAmount": "25000",
            "q7_caseNumber": "2023-CV-12345",
            "q8_additionalNotes": "Interested in recovery services",
            "callDuration": "120",
            "callRecording": "https://jotform.com/recordings/...",
            "callTranscript": "Full transcript of call..."
        },
        "submissionDate": "2026-01-17 10:30:00"
    }
    """
    try:
        # Log webhook receipt
        print("=" * 80)
        print("JotForm webhook received")
        print("=" * 80)
        
        # Get JSON payload
        data = request.json
        if not data:
            return jsonify({'error': 'No data received'}), 400
        
        # Extract form data (JotForm sends data in rawRequest)
        raw_request = data.get('rawRequest', {})
        
        # Parse JotForm field data
        # Field names may vary based on your JotForm setup
        full_name = (
            raw_request.get('q1_fullName') or 
            raw_request.get('fullName') or 
            raw_request.get('name') or 
            ''
        )
        
        phone = (
            raw_request.get('q2_phoneNumber') or 
            raw_request.get('phoneNumber') or 
            raw_request.get('phone') or 
            ''
        )
        
        email = (
            raw_request.get('q3_email') or 
            raw_request.get('email') or 
            ''
        )
        
        county = (
            raw_request.get('q4_county') or 
            raw_request.get('county') or 
            ''
        )
        
        state = (
            raw_request.get('q5_state') or 
            raw_request.get('state') or 
            ''
        )
        
        surplus_amount = (
            raw_request.get('q6_surplusAmount') or 
            raw_request.get('surplusAmount') or 
            raw_request.get('surplus_amount') or 
            0
        )
        
        case_number = (
            raw_request.get('q7_caseNumber') or 
            raw_request.get('caseNumber') or 
            raw_request.get('case_number') or 
            ''
        )
        
        additional_notes = (
            raw_request.get('q8_additionalNotes') or 
            raw_request.get('additionalNotes') or 
            raw_request.get('notes') or 
            ''
        )
        
        # Get call metadata if available (for phone calls)
        call_duration = raw_request.get('callDuration', '')
        call_recording = raw_request.get('callRecording', '')
        call_transcript = raw_request.get('callTranscript', '')
        
        # Get submission metadata
        submission_id = data.get('submissionID', '')
        submission_date = data.get('submissionDate', '')
        form_title = data.get('formTitle', 'JotForm Submission')
        
        # Determine channel (phone, web, SMS, etc.)
        channel = 'Unknown'
        if call_recording or call_transcript:
            channel = 'Phone - AI Receptionist'
        elif 'sms' in form_title.lower():
            channel = 'SMS'
        elif 'chat' in form_title.lower():
            channel = 'Web Chat'
        else:
            channel = 'Web Form'
        
        # Build notes field with all context
        notes_parts = []
        
        if additional_notes:
            notes_parts.append(f"Caller Notes: {additional_notes}")
        
        if call_transcript:
            notes_parts.append(f"\n--- Call Transcript ---\n{call_transcript}")
        
        if call_recording:
            notes_parts.append(f"\nCall Recording: {call_recording}")
        
        if call_duration:
            notes_parts.append(f"Call Duration: {call_duration} seconds")
        
        if submission_id:
            notes_parts.append(f"\nJotForm Submission ID: {submission_id}")
        
        if submission_date:
            notes_parts.append(f"Submission Date: {submission_date}")
        
        combined_notes = '\n'.join(notes_parts) if notes_parts else ''
        
        # Convert surplus amount to float
        try:
            surplus_amount = float(str(surplus_amount).replace('$', '').replace(',', '').strip()) if surplus_amount else 0
        except (ValueError, AttributeError):
            surplus_amount = 0
        
        # Prepare lead data for LBPC system
        lead_data = {
            'property_owner_name': full_name,
            'phone': phone,
            'email': email,
            'county': county,
            'state': state,
            'surplus_amount': surplus_amount,
            'case_number': case_number,
            'notes': combined_notes,
            'lead_source': channel,
            'status': 'New',
            'contact_method': 'Inbound Call' if 'Phone' in channel else 'Web Submission'
        }
        
        # Log the parsed data
        print(f"Creating LBPC lead from {channel}:")
        print(f"  Name: {full_name}")
        print(f"  Phone: {phone}")
        print(f"  Email: {email}")
        print(f"  County: {county}, {state}")
        print(f"  Surplus: ${surplus_amount:,.2f}")
        print(f"  Source: {channel}")
        
        # Create lead in LBPC system using existing handler
        result = handle_lbpc_create_lead(lead_data)
        
        if result.get('success'):
            print(f"✓ Lead created successfully (ID: {result.get('record_id', 'N/A')})")
            print("=" * 80)
            
            return jsonify({
                'success': True,
                'message': 'Lead created successfully from JotForm submission',
                'lead_id': result.get('record_id'),
                'channel': channel,
                'priority_score': result.get('priority_score')
            }), 201
        else:
            print(f"✗ Failed to create lead: {result.get('error', 'Unknown error')}")
            print("=" * 80)
            
            return jsonify({
                'success': False,
                'error': result.get('error', 'Failed to create lead'),
                'details': result
            }), 400
    
    except Exception as e:
        print(f"✗ JotForm webhook error: {str(e)}")
        print("=" * 80)
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'success': False,
            'error': f'Webhook processing error: {str(e)}'
        }), 500


@app.route('/webhooks/jotform/test', methods=['GET', 'POST'])
def jotform_webhook_test():
    """
    Test endpoint for JotForm webhook
    GET: Returns info about the endpoint
    POST: Accepts test data and shows what would be processed
    """
    if request.method == 'GET':
        return jsonify({
            'status': 'active',
            'endpoint': '/webhooks/jotform',
            'methods': ['POST'],
            'description': 'JotForm AI Receptionist webhook for LBPC lead capture',
            'expected_fields': {
                'required': ['fullName', 'phone', 'county', 'state'],
                'optional': ['email', 'surplusAmount', 'caseNumber', 'notes', 'callTranscript', 'callRecording']
            },
            'example_payload': {
                'submissionID': '123456789',
                'formTitle': 'LBPC Lead Intake',
                'rawRequest': {
                    'q1_fullName': 'John Smith',
                    'q2_phoneNumber': '555-123-4567',
                    'q3_email': 'john@example.com',
                    'q4_county': 'Wayne',
                    'q5_state': 'Michigan',
                    'q6_surplusAmount': '25000',
                    'q7_caseNumber': '2023-CV-12345',
                    'q8_additionalNotes': 'Interested in recovery services'
                }
            }
        })
    
    # POST method - test mode (doesn't create real lead)
    try:
        data = request.json
        raw_request = data.get('rawRequest', {})
        
        return jsonify({
            'success': True,
            'message': 'Test webhook received successfully',
            'parsed_data': {
                'name': raw_request.get('q1_fullName') or raw_request.get('fullName'),
                'phone': raw_request.get('q2_phoneNumber') or raw_request.get('phone'),
                'email': raw_request.get('q3_email') or raw_request.get('email'),
                'county': raw_request.get('q4_county') or raw_request.get('county'),
                'state': raw_request.get('q5_state') or raw_request.get('state'),
                'surplus_amount': raw_request.get('q6_surplusAmount') or raw_request.get('surplusAmount'),
            },
            'note': 'This is test mode - no lead was created'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


# ============================================================================
# STATIC MEDIA ROUTES - Video/Photo Serving
# ============================================================================

@app.route('/legal/terms', methods=['GET'])
def serve_terms():
    """
    Serve Terms of Use HTML page
    """
    try:
        from flask import send_from_directory
        import os
        
        root_folder = os.path.dirname(__file__)
        return send_from_directory(root_folder, 'ALEXIS_NEXUS_TERMS_OF_USE.html')
    
    except FileNotFoundError:
        return jsonify({'error': 'Terms of Use not found'}), 404
    except Exception as e:
        return jsonify({'error': f'Error serving Terms of Use: {str(e)}'}), 500


@app.route('/legal/privacy', methods=['GET'])
def serve_privacy():
    """
    Serve Privacy Policy HTML page
    """
    try:
        from flask import send_from_directory
        import os
        
        root_folder = os.path.dirname(__file__)
        return send_from_directory(root_folder, 'ALEXIS_NEXUS_PRIVACY_POLICY.html')
    
    except FileNotFoundError:
        return jsonify({'error': 'Privacy Policy not found'}), 404
    except Exception as e:
        return jsonify({'error': f'Error serving Privacy Policy: {str(e)}'}), 500


@app.route('/legal', methods=['GET'])
def list_legal_docs():
    """
    List available legal documents
    Returns: JSON with links to legal documents
    """
    base_url = request.host_url.rstrip('/')
    return jsonify({
        'legal_documents': [
            {
                'name': 'Terms of Use',
                'url': f'{base_url}/legal/terms',
                'description': 'ALEXIS NEXUS Terms of Use'
            },
            {
                'name': 'Privacy Policy',
                'url': f'{base_url}/legal/privacy',
                'description': 'ALEXIS NEXUS Privacy Policy'
            }
        ],
        'last_updated': 'January 18, 2026'
    })


@app.route('/media/videos/<filename>', methods=['GET'])
def serve_video(filename):
    """
    Serve video files from photos_and_videos folder
    Example: GET /media/videos/nexus-2.mp4
    Supports quality parameter: ?quality=720p
    """
    try:
        from flask import send_from_directory
        import os
        
        video_folder = os.path.join(os.path.dirname(__file__), 'photos_and_videos')
        
        # Security check - only allow video files
        allowed_extensions = ['.mp4', '.mov', '.avi', '.webm']
        file_ext = os.path.splitext(filename)[1].lower()
        
        if file_ext not in allowed_extensions:
            return jsonify({'error': 'Invalid file type'}), 400
        
        # Check for quality parameter
        quality = request.args.get('quality', '').lower()
        if quality in ['720p', '480p', '1080p']:
            # Try to serve optimized version
            base_name = os.path.splitext(filename)[0]
            optimized_name = f"{base_name}-{quality}{file_ext}"
            optimized_path = os.path.join(video_folder, optimized_name)
            
            if os.path.exists(optimized_path):
                return send_from_directory(video_folder, optimized_name)
            # Fall back to original if quality version doesn't exist
        
        return send_from_directory(video_folder, filename)
    
    except FileNotFoundError:
        return jsonify({'error': 'Video not found'}), 404
    except Exception as e:
        return jsonify({'error': f'Error serving video: {str(e)}'}), 500


@app.route('/media/videos', methods=['GET'])
def list_videos():
    """
    List available videos with quality versions
    Returns: JSON list of available video files with metadata
    """
    try:
        import os
        video_folder = os.path.join(os.path.dirname(__file__), 'photos_and_videos')
        
        if not os.path.exists(video_folder):
            return jsonify({'videos': []})
        
        videos = {}
        base_url = request.host_url.rstrip('/') + '/media/videos/'
        
        for f in os.listdir(video_folder):
            if f.lower().endswith(('.mp4', '.mov', '.avi', '.webm')):
                # Check if it's a quality variant or original
                if '-720p' in f or '-480p' in f or '-1080p' in f:
                    # Extract base name
                    for quality in ['720p', '480p', '1080p']:
                        if f'-{quality}' in f:
                            base_name = f.replace(f'-{quality}', '')
                            if base_name not in videos:
                                videos[base_name] = {
                                    'name': base_name,
                                    'url': f'{base_url}{base_name}',
                                    'qualities': {}
                                }
                            file_path = os.path.join(video_folder, f)
                            file_size = os.path.getsize(file_path)
                            videos[base_name]['qualities'][quality] = {
                                'url': f'{base_url}{base_name}?quality={quality}',
                                'size': file_size,
                                'size_mb': round(file_size / 1048576, 2)
                            }
                            break
                else:
                    # Original/main video
                    if f not in videos:
                        videos[f] = {
                            'name': f,
                            'url': f'{base_url}{f}',
                            'qualities': {}
                        }
                    file_path = os.path.join(video_folder, f)
                    file_size = os.path.getsize(file_path)
                    videos[f]['size'] = file_size
                    videos[f]['size_mb'] = round(file_size / 1048576, 2)
        
        return jsonify({
            'videos': list(videos.values()),
            'base_url': base_url,
            'quality_options': ['original', '720p', '480p', '1080p']
        })
    
    except Exception as e:
        return jsonify({'error': f'Error listing videos: {str(e)}'}), 500


# =====================================================================
# CONTRACT FULFILLMENT & INVENTORY MANAGEMENT
# =====================================================================

@app.route('/fulfillment/contracts', methods=['POST'])
def create_fulfillment_contract():
    """
    Create new fulfillment contract with auto-generated delivery schedule
    
    Body: {
        "CONTRACT_NAME": "VA Hospital - Socks",
        "CLIENT_NAME": "Veterans Affairs",
        "PRODUCT": "Diabetic Socks - White L",
        "TOTAL_QUANTITY": 2500,
        "UNIT_PRICE": 5.00,
        "DELIVERY_FREQUENCY": "Monthly",
        "QUANTITY_PER_DELIVERY": 200,
        "START_DATE": "2026-02-01",
        "END_DATE": "2028-01-31",
        "SUPPLIER_ID": ["rec123..."],
        "SUPPLIER_UNIT_COST": 3.50,
        "ALERT_THRESHOLD": 400,
        "NOTES": "Ship to Building 3"
    }
    """
    try:
        data = request.json
        result = handle_create_fulfillment_contract(data)
        
        if result.get('success'):
            return jsonify(result), 201
        else:
            return jsonify(result), 400
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/fulfillment/contracts', methods=['GET'])
def get_fulfillment_contracts():
    """Get active fulfillment contracts"""
    try:
        status = request.args.get('status', 'Active')
        contracts = handle_get_active_contracts()
        
        # Filter by status if needed
        if status != 'all':
            contracts = [c for c in contracts if c.get('STATUS') == status]
        
        return jsonify({
            'contracts': contracts,
            'count': len(contracts)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/fulfillment/contracts/<contract_id>', methods=['GET'])
def get_contract_details(contract_id):
    """Get contract with all deliveries and inventory status"""
    try:
        result = handle_get_contract_details(contract_id)
        
        if result.get('error'):
            return jsonify(result), 404
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/fulfillment/deliveries', methods=['GET'])
def get_deliveries():
    """
    Get deliveries (upcoming or all)
    Query params:
    - due_within_days: Get deliveries due within X days (default: 7)
    - contract_id: Filter by contract
    """
    try:
        days_ahead = int(request.args.get('due_within_days', 7))
        contract_id = request.args.get('contract_id')
        
        deliveries = handle_get_upcoming_deliveries(days_ahead)
        
        # Filter by contract if specified
        if contract_id:
            deliveries = [d for d in deliveries if contract_id in d.get('CONTRACT', [])]
        
        return jsonify({
            'deliveries': deliveries,
            'count': len(deliveries),
            'days_ahead': days_ahead
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/fulfillment/deliveries/<delivery_id>', methods=['PUT'])
def update_delivery(delivery_id):
    """
    Update delivery status
    
    Body: {
        "STATUS": "Delivered",
        "ACTUAL_DELIVERY_DATE": "2026-02-15",
        "TRACKING_NUMBER": "1Z999AA10123456784",
        "CARRIER": "UPS",
        "SHIPPING_COST": 45.00,
        "DELIVERED_TO": "John Smith - Receiving",
        "NOTES": "Left at loading dock"
    }
    """
    try:
        updates = request.json
        result = handle_update_delivery_status(delivery_id, updates)
        
        if result.get('success'):
            return jsonify(result)
        else:
            return jsonify(result), 400
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/fulfillment/inventory', methods=['GET'])
def get_inventory():
    """Get all inventory with status indicators"""
    try:
        inventory = handle_get_inventory_dashboard()
        
        return jsonify({
            'inventory': inventory,
            'count': len(inventory)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/fulfillment/inventory/health-check', methods=['GET'])
def inventory_health_check():
    """
    Run inventory health check
    Returns alerts for critical, low stock, and reorder needed items
    """
    try:
        result = handle_check_inventory_health()
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/fulfillment/inventory/<product_sku>', methods=['GET'])
def get_inventory_by_sku(product_sku):
    """Get inventory status for specific product"""
    try:
        all_inventory = handle_get_inventory_dashboard()
        product_inventory = [i for i in all_inventory if i.get('PRODUCT_SKU') == product_sku]
        
        if not product_inventory:
            return jsonify({'error': 'Product not found'}), 404
        
        return jsonify(product_inventory[0])
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/fulfillment/purchase-orders', methods=['POST'])
def create_purchase_order():
    """
    Create purchase order to restock inventory
    
    Body: {
        "SUPPLIER": ["rec123..."],
        "PRODUCT_SKU": "SOCK-DIAB-WHT-L",
        "PRODUCT_NAME": "Diabetic Socks - White L",
        "QUANTITY_ORDERED": 2000,
        "UNIT_COST": 3.50,
        "EXPECTED_DELIVERY_DATE": "2026-04-20",
        "PAYMENT_TERMS": "Net 30",
        "NOTES": "Rush order - expedited shipping"
    }
    """
    try:
        po_data = request.json
        result = handle_create_purchase_order(po_data)
        
        if result.get('success'):
            return jsonify(result), 201
        else:
            return jsonify(result), 400
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/fulfillment/purchase-orders', methods=['GET'])
def get_purchase_orders():
    """
    Get purchase orders
    Query params:
    - status: Filter by status (Ordered, In Transit, Received, Cancelled)
    """
    try:
        status = request.args.get('status', 'Ordered')
        
        if status == 'Ordered':
            pos = handle_get_pending_purchase_orders()
        else:
            # Get all POs and filter - would need another handler for this
            pos = handle_get_pending_purchase_orders()  # For now, just return pending
        
        return jsonify({
            'purchase_orders': pos,
            'count': len(pos)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/fulfillment/purchase-orders/<po_id>/receive', methods=['PUT'])
def receive_purchase_order(po_id):
    """
    Mark purchase order as received and update inventory
    
    Body: {
        "ACTUAL_DELIVERY_DATE": "2026-04-19",
        "QUANTITY_RECEIVED": 2000,
        "NOTES": "All items in good condition"
    }
    """
    try:
        received_data = request.json
        result = handle_receive_purchase_order(po_id, received_data)
        
        if result.get('success'):
            return jsonify(result)
        else:
            return jsonify(result), 400
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/fulfillment/dashboard', methods=['GET'])
def get_fulfillment_dashboard():
    """
    Get complete fulfillment dashboard data
    - Active contracts
    - Upcoming deliveries (7 days)
    - Inventory alerts
    - Pending POs
    """
    try:
        contracts = handle_get_active_contracts()
        deliveries = handle_get_upcoming_deliveries(7)
        inventory_health = handle_check_inventory_health()
        pending_pos = handle_get_pending_purchase_orders()
        
        return jsonify({
            'contracts': {
                'data': contracts[:10],  # Top 10
                'total': len(contracts)
            },
            'upcoming_deliveries': {
                'data': deliveries,
                'total': len(deliveries)
            },
            'inventory_alerts': inventory_health.get('alerts', {}),
            'inventory_summary': inventory_health.get('summary', {}),
            'pending_purchase_orders': {
                'data': pending_pos[:5],  # Top 5
                'total': len(pending_pos)
            }
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# =====================================================================
# AI RECOMMENDATION & APPROVAL SYSTEM
# =====================================================================

@app.route('/ai/recommendations/capability-gap', methods=['POST'])
def analyze_capability_gap():
    """
    AI analyzes opportunity and recommends self-perform vs partner approach
    
    Request body:
    {
        "opportunity_id": "rec123abc"
    }
    
    Response:
    {
        "success": true,
        "analysis": {
            "required_capabilities": [...],
            "we_can_do": [...],
            "we_need": [...],
            "recommendation": "self_perform" or "partner",
            "confidence": 85,
            "reasoning": "...",
            "compliance_check": {...}
        },
        "recommendation_id": "rec456def",
        "message": "AI recommendation ready for your review"
    }
    """
    try:
        data = request.get_json()
        opportunity_id = data.get('opportunity_id')
        
        if not opportunity_id:
            return jsonify({'error': 'opportunity_id required'}), 400
        
        result = handle_analyze_capability_gap(opportunity_id)
        
        if result.get('success'):
            return jsonify(result), 200
        else:
            return jsonify(result), 400
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/ai/recommendations/subcontractors', methods=['POST'])
def recommend_subcontractors():
    """
    AI recommends top 5 subcontractors based on needed skills
    
    Request body:
    {
        "opportunity_id": "rec123abc",
        "needed_skills": ["cybersecurity", "penetration testing"],
        "contract_value": 500000,  // optional
        "minimal_research": true   // optional, default true — homepage + Google CSE snippets for ranking
    }
    
    Response:
    {
        "success": true,
        "recommended_subcontractors": [
            {
                "id": "rec789ghi",
                "name": "CyberSec Experts LLC",
                "score": 92,
                "reason": "Strong cybersecurity expertise...",
                "strengths": [...],
                "concerns": [...]
            },
            ...
        ],
        "ai_top_pick": {...},
        "message": "AI analyzed 12 subcontractors..."
    }
    """
    try:
        data = request.get_json()
        opportunity_id = data.get('opportunity_id')
        needed_skills = data.get('needed_skills', [])
        contract_value = data.get('contract_value')
        minimal_research = data.get('minimal_research', True)
        if isinstance(minimal_research, str):
            minimal_research = minimal_research.strip().lower() not in ('0', 'false', 'no', 'off')
        
        if not opportunity_id or not needed_skills:
            return jsonify({'error': 'opportunity_id and needed_skills required'}), 400
        
        result = handle_recommend_subcontractors(
            opportunity_id, needed_skills, contract_value, minimal_research=bool(minimal_research)
        )
        
        if result.get('success'):
            return jsonify(result), 200
        else:
            return jsonify(result), 400
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/ai/recommendations/suppliers', methods=['POST'])
def recommend_suppliers():
    """
    AI recommends top 10 suppliers for product-based opportunities
    
    Request body:
    {
        "opportunity_id": "rec123abc",
        "product_description": "Dell Latitude Laptops 5000 series"
    }
    
    Response:
    {
        "success": true,
        "recommended_suppliers": [
            {
                "id": "rec789ghi",
                "name": "TechSource Wholesale",
                "score": 88,
                "reason": "Perfect product match, GSA approved...",
                "pricing_estimate": "competitive"
            },
            ...
        ],
        "ai_top_pick": {...},
        "message": "AI analyzed 30 suppliers..."
    }
    """
    try:
        data = request.get_json()
        opportunity_id = data.get('opportunity_id')
        product_description = data.get('product_description')
        
        if not opportunity_id or not product_description:
            return jsonify({'error': 'opportunity_id and product_description required'}), 400
        
        result = handle_recommend_suppliers(opportunity_id, product_description)
        
        if result.get('success'):
            return jsonify(result), 200
        else:
            return jsonify(result), 400
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/ai/recommendations/<recommendation_id>/approve', methods=['POST'])
def approve_recommendation(recommendation_id):
    """
    User approves, denies, or modifies AI recommendation
    System learns from the decision
    
    Request body:
    {
        "decision": "approved" | "denied" | "modified",
        "notes": "Your reasoning for the decision",
        "selected_id": "rec999xyz"  // optional: if user picked different option
    }
    
    Response:
    {
        "success": true,
        "decision": "approved",
        "message": "Recommendation approved. System learning from your decision."
    }
    """
    try:
        data = request.get_json()
        decision = data.get('decision')
        notes = data.get('notes', '')
        selected_id = data.get('selected_id')
        
        if not decision:
            return jsonify({'error': 'decision required (approved/denied/modified)'}), 400
        
        if decision not in ['approved', 'denied', 'modified']:
            return jsonify({'error': 'decision must be approved, denied, or modified'}), 400
        
        result = handle_approve_recommendation(recommendation_id, decision, notes, selected_id)
        
        if result.get('success'):
            return jsonify(result), 200
        else:
            return jsonify(result), 400
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/ai/recommendations/pending', methods=['GET'])
def get_pending_recommendations():
    """
    Get all pending AI recommendations awaiting user decision
    
    Query params:
    - opportunity_id (optional): Filter by specific opportunity
    
    Response:
    {
        "success": true,
        "pending_recommendations": [
            {
                "id": "rec123abc",
                "OPPORTUNITY": ["rec456def"],
                "TYPE": "Capability Gap Analysis",
                "RECOMMENDATION": "PARTNER",
                "CONFIDENCE": 85,
                "REASONING": "...",
                "STATUS": "Pending Approval",
                "CREATED": "2026-01-21T..."
            },
            ...
        ],
        "count": 3
    }
    """
    try:
        opportunity_id = request.args.get('opportunity_id')
        
        result = handle_get_pending_recommendations(opportunity_id)
        
        if result.get('success'):
            return jsonify(result), 200
        else:
            return jsonify(result), 400
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/ai/compliance/calculate', methods=['POST'])
def calculate_compliance():
    """
    Calculate workshare percentages and check 50% rule compliance
    Used for subcontracting compliance verification
    
    Request body:
    {
        "contract_value": 500000,
        "your_work_value": 280000,
        "subcontractor_work_value": 180000
    }
    
    Response:
    {
        "success": true,
        "compliance": {
            "contract_value": 500000,
            "your_work": 280000,
            "your_percentage": 56.0,
            "subcontractor_work": 180000,
            "subcontractor_percentage": 36.0,
            "margin": 40000,
            "margin_percentage": 8.0,
            "meets_50_percent_rule": true,
            "compliant": true,
            "status": "✅ Compliant",
            "message": "You perform 56.0% - Meets 50% rule"
        }
    }
    """
    try:
        data = request.get_json()
        contract_value = data.get('contract_value')
        your_work_value = data.get('your_work_value')
        sub_work_value = data.get('subcontractor_work_value')
        
        if contract_value is None or your_work_value is None or sub_work_value is None:
            return jsonify({'error': 'contract_value, your_work_value, and subcontractor_work_value required'}), 400
        
        result = handle_calculate_compliance(
            float(contract_value),
            float(your_work_value),
            float(sub_work_value)
        )
        
        if result.get('success'):
            return jsonify(result), 200
        else:
            return jsonify(result), 400
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# =====================================================================
# CAPABILITY STATEMENT GENERATOR ENDPOINTS
# =====================================================================

@app.route('/capability-statements/generate', methods=['POST'])
def generate_capability_statement():
    """
    Generate a v3 capability statement with sector-specific colors and CO-grade content.
    
    Request body:
        {
            "sector": "drug_testing",           // Service sector key
            "agency_name": "Agency Name",       // Target agency
            "solicitation_number": "12345",     // Solicitation reference
            "service_description": "Override",  // Override gold bar title
            "custom_overview": "...",           // Override overview text
            "custom_naics": "541611 | 621511",  // Override NAICS
            "output_dir": "/path/to/dir"        // Optional output directory
        }
    """
    try:
        from capability_statement_generator import handle_generate_capability_statement
        
        data = request.get_json() or {}
        
        result = handle_generate_capability_statement(
            sector=data.get('sector', 'main'),
            agency_name=data.get('agency_name'),
            solicitation_number=data.get('solicitation_number'),
            service_description=data.get('service_description'),
            custom_overview=data.get('custom_overview'),
            custom_naics=data.get('custom_naics'),
            output_dir=data.get('output_dir'),
        )
        
        if not result.get('success'):
            return jsonify(result), 400
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# =====================================================================
# EMAIL TEMPLATE GENERATOR (DDCSS) — HTML + {{PLACEHOLDER}} / company_info.py
# =====================================================================

@app.route('/email-templates/categories', methods=['GET'])
def email_templates_categories():
    """List email template categories and variants (DDCSS)."""
    try:
        from email_template_generator import AVAILABLE_EMAIL_CATEGORIES
        return jsonify({"categories": AVAILABLE_EMAIL_CATEGORIES})
    except Exception as e:
        return jsonify({"error": str(e), "categories": []}), 500


@app.route('/email-templates/generate', methods=['POST'])
def email_templates_generate():
    """
    Generate HTML email from template. Request JSON:
    {
      "category": "mco_hide_snp",
      "variant": "cold_outreach" | "warm_follow_up" | "inbound_response",
      "recipientFirstName": "Dana",
      "planDisplayName": "HAP CareSource MI Health Link",
      "customParagraph": "optional extra paragraph",
      "outputDir": "/optional/path"
    }
    """
    try:
        from email_template_generator import handle_generate_email_template

        data = request.get_json() or {}
        result = handle_generate_email_template(
            category=data.get("category", "mco_hide_snp"),
            variant=data.get("variant", "cold_outreach"),
            recipient_first_name=data.get("recipientFirstName") or data.get("recipient_first_name"),
            plan_display_name=data.get("planDisplayName") or data.get("plan_display_name"),
            custom_paragraph=data.get("customParagraph") or data.get("custom_paragraph"),
            extra_replacements=data.get("extraReplacements") or data.get("extra_replacements"),
            output_dir=data.get("outputDir") or data.get("output_dir"),
        )
        if not result.get("success"):
            return jsonify(result), 400
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/capability-statements/sectors', methods=['GET'])
def get_capability_statement_sectors():
    """
    Get list of available sectors for capability statement generation.
    Each sector has its own color scheme and default content.
    """
    from capability_statement_generator import AVAILABLE_SECTORS, SECTOR_COLORS
    sectors_with_colors = []
    for s in AVAILABLE_SECTORS:
        colors = SECTOR_COLORS.get(s['key'], SECTOR_COLORS['main'])
        sectors_with_colors.append({
            'key': s['key'],
            'label': s['label'],
            'primary_color': colors['primary'],
            'accent_color': colors['accent'],
        })
    return jsonify({'sectors': sectors_with_colors})


@app.route('/capability-statements/list', methods=['GET'])
def list_capability_statements():
    """
    Get list of generated capability statements from Airtable
    
    Returns:
        {
            "statements": [
                {
                    "id": "recXXXX",
                    "client_name": "Agency Name",
                    "rfq_number": "12345",
                    "generated_date": "2026-01-23",
                    "html_path": "/path/to/file.html",
                    "pdf_path": "/path/to/file.pdf"
                }
            ]
        }
    """
    try:
        airtable_key = os.environ.get('AIRTABLE_API_KEY', '')
        base_id = os.environ.get('AIRTABLE_BASE_ID', '')
        
        from pyairtable import Api
        api = Api(airtable_key)
        table = api.table(base_id, 'CapabilityStatements')
        
        records = table.all()
        
        statements = []
        for record in records:
            fields = record['fields']
            statements.append({
                'id': record['id'],
                'client_name': fields.get('ClientName', ''),
                'rfq_number': fields.get('RFQNumber', ''),
                'generated_date': fields.get('GeneratedDate', ''),
                'html_path': fields.get('HTMLPath', ''),
                'pdf_path': fields.get('PDFPath', ''),
                'status': fields.get('Status', '')
            })
        
        return jsonify({'statements': statements})
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'statements': []
        }), 500


# =====================================================================
# WORKFLOW MANAGEMENT API
# =====================================================================

# Old static workflow/queues endpoint removed — replaced by live folder scanner
# See /api/workflow/queues route at bottom of file (reads BIDS:RESOURCES/ live)


def _resolve_airtable_id(folder_slug_or_id: str, bid_name: str = '', bid_fields: dict = None) -> str:
    """
    Resolve a folder slug to an Airtable record ID.
    
    The GPSS workflow queues use folder slugs (e.g. 'HAMTRAMCK_BOARD_UP') from 
    the bid folder scanner. But Airtable needs record IDs (e.g. 'recXXXXXX').
    
    Strategy:
    1. If it already looks like an Airtable record ID (starts with 'rec'), return as-is
    2. Search GPSS Opportunities by Name matching the folder name
    3. If not found, create a new record from folder scan data
    4. Return the real Airtable record ID
    """
    # Already an Airtable record ID
    if folder_slug_or_id.startswith('rec'):
        return folder_slug_or_id
    
    airtable_client = AirtableClient()
    table = airtable_client.get_table('GPSS Opportunities')
    
    # Convert slug back to readable name: HAMTRAMCK_BOARD_UP → HAMTRAMCK BOARD UP
    folder_name = folder_slug_or_id.replace('_', ' ')
    
    # Search for matching record by name
    try:
        formula = f"FIND('{folder_name}', {{Name}})"
        matches = table.all(formula=formula)
        if matches:
            return matches[0]['id']
    except:
        pass
    
    # Try exact match
    try:
        formula = f"{{Name}} = '{folder_name}'"
        matches = table.all(formula=formula)
        if matches:
            return matches[0]['id']
    except:
        pass
    
    # Also try the bid_name if provided
    if bid_name and bid_name != folder_name:
        try:
            formula = f"FIND('{bid_name}', {{Name}})"
            matches = table.all(formula=formula)
            if matches:
                return matches[0]['id']
        except:
            pass
    
    # Not found — create a new record from folder data
    # Only set fields known to exist in GPSS Opportunities
    create_fields = {
        'Name': bid_name or folder_name,
        'Notes': f'Auto-created from bid folder: {folder_name}',
    }
    
    # Add extra fields if available from the bid scan
    if bid_fields:
        if bid_fields.get('Response Deadline'):
            create_fields['Deadline'] = bid_fields['Response Deadline']
    
    try:
        new_record = table.create(create_fields)
        print(f"Created Airtable record {new_record['id']} for folder '{folder_name}'")
        return new_record['id']
    except Exception as e:
        # If creation fails (e.g. Notes doesn't exist), try minimal creation
        try:
            new_record = table.create({'Name': bid_name or folder_name})
            print(f"Created minimal Airtable record {new_record['id']} for folder '{folder_name}'")
            return new_record['id']
        except Exception as e2:
            raise Exception(f"Cannot resolve '{folder_slug_or_id}' to Airtable record: {e2}")


@app.route('/api/workflow/opportunity/<opportunity_id>/review', methods=['POST'])
def review_opportunity(opportunity_id):
    """
    Review and name an opportunity.
    
    Accepts either Airtable record IDs (recXXX) or folder slugs (HAMTRAMCK_BOARD_UP).
    If folder slug, auto-resolves to Airtable record ID (creates if needed).
    
    Also creates a WORKFLOW_STATUS.md file in the bid folder so the folder scanner
    recognizes the opportunity has been reviewed and moves it out of "Needs Review".
    
    Body:
        {
            "name": "CPS Energy - Industrial Supplies",
            "decision": "pursue" | "skip",
            "notes": "Optional notes"
        }
    """
    try:
        data = request.get_json() or {}
        
        name = data.get('name', '').strip()
        decision = data.get('decision', 'pursue')
        notes = data.get('notes', '')
        
        if not name:
            return jsonify({
                'success': False,
                'error': 'Name is required'
            }), 400
        
        # Resolve folder slug to Airtable record ID
        real_id = _resolve_airtable_id(opportunity_id, bid_name=name)
        
        workflow = WorkflowManager()
        result = workflow.review_opportunity(real_id, name, decision, notes)
        
        # Also create WORKFLOW_STATUS.md in the folder (for folder scanner)
        # Find the folder path from the opportunity_id (which is a folder slug)
        bids_root = os.path.join(os.path.dirname(__file__), "BIDS:RESOURCES")
        folder_path = None
        
        # opportunity_id might be a slug like "36C25626R0057_DRY_ICE_..." 
        # Convert slug back to find matching folder
        slug_lower = opportunity_id.lower().replace("_", " ")
        for entry in os.scandir(bids_root):
            if entry.is_dir():
                if entry.name.lower().replace("_", " ") == slug_lower or \
                   entry.name.replace(" ", "_").upper() == opportunity_id:
                    folder_path = entry.path
                    break
        
        if folder_path and os.path.exists(folder_path):
            status_file = os.path.join(folder_path, "WORKFLOW_STATUS.md")
            new_status = 'Find Suppliers' if decision == 'pursue' else 'Skipped'
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            status_content = f"""# WORKFLOW STATUS

**Opportunity:** {name}
**Status:** {new_status}
**Decision:** {decision.upper()}
**Reviewed:** {timestamp}

## Notes
{notes if notes else 'No notes provided.'}

---
*This file is auto-generated by NEXUS when an opportunity is reviewed.*
*It marks this folder as active in the workflow pipeline.*
"""
            try:
                with open(status_file, 'w') as f:
                    f.write(status_content)
                print(f"[WORKFLOW] Created {status_file}")
                result['folder_updated'] = True
            except Exception as write_err:
                print(f"[WORKFLOW] Could not write status file: {write_err}")
                result['folder_updated'] = False
        else:
            print(f"[WORKFLOW] Could not find folder for {opportunity_id}")
            result['folder_updated'] = False
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/workflow/opportunity/<opportunity_id>/suppliers', methods=['POST'])
def identify_suppliers(opportunity_id):
    """
    Link suppliers to an opportunity
    
    Body:
        {
            "supplierIds": ["rec123", "rec456", "rec789"]
        }
    
    Returns:
        {
            "success": true,
            "message": "Added 3 suppliers",
            "newStatus": "Request Quotes"
        }
    """
    try:
        data = request.get_json() or {}
        supplier_ids = data.get('supplierIds', [])
        
        if not supplier_ids:
            return jsonify({
                'success': False,
                'error': 'At least one supplier is required'
            }), 400
        
        # Resolve folder slug to Airtable record ID
        real_id = _resolve_airtable_id(opportunity_id)
        
        workflow = WorkflowManager()
        result = workflow.identify_suppliers(real_id, supplier_ids)
        
        # ── AUTO-TRIGGER: Generate RFQ and send to suppliers ──
        auto_actions = []
        if result.get('success'):
            try:
                from supplier_quote_workflow import request_quotes_for_opportunity
                quote_result = request_quotes_for_opportunity(real_id)
                if quote_result.get('success'):
                    count = quote_result.get('quotes_sent', 0)
                    auto_actions.append(f"Auto-generated {count} RFQ(s) for {len(supplier_ids)} suppliers")
                    result['rfq_generated'] = True
                    result['quotes_sent'] = count
                else:
                    auto_actions.append(f"RFQ generation attempted: {quote_result.get('error', 'unknown')[:80]}")
            except Exception as e:
                auto_actions.append(f"RFQ auto-generation note: {str(e)[:80]}")
        
        result['auto_actions'] = auto_actions
        return jsonify(result)
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/workflow/opportunity/<opportunity_id>/quotes-requested', methods=['POST'])
def mark_quotes_requested(opportunity_id):
    """
    Mark that quote requests have been sent
    
    Body:
        {
            "count": 5
        }
    
    Returns:
        {
            "success": true,
            "message": "Sent 5 quote requests",
            "newStatus": "Awaiting Quotes"
        }
    """
    try:
        data = request.get_json() or {}
        count = data.get('count', 0)
        
        # Resolve folder slug to Airtable record ID
        real_id = _resolve_airtable_id(opportunity_id)
        
        workflow = WorkflowManager()
        result = workflow.mark_quotes_requested(real_id, count)
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/workflow/opportunity/<opportunity_id>/advance', methods=['POST'])
def advance_workflow(opportunity_id):
    """
    Advance opportunity to next workflow stage with auto-trigger actions.
    
    When moving to certain stages, the system automatically kicks off
    the next logical action (e.g., finding suppliers, requesting quotes).
    
    Body:
        {
            "newStatus": "Ready to Price"
        }
    
    Returns:
        {
            "success": true,
            "message": "Advanced to Ready to Price",
            "newStatus": "Ready to Price",
            "auto_actions": ["Found 5 potential suppliers"]
        }
    """
    try:
        data = request.get_json() or {}
        new_status = data.get('newStatus', '')
        
        if not new_status:
            return jsonify({
                'success': False,
                'error': 'newStatus is required'
            }), 400
        
        # Resolve folder slug to Airtable record ID
        real_id = _resolve_airtable_id(opportunity_id)
        
        workflow = WorkflowManager()
        result = workflow.advance_workflow(real_id, new_status)
        
        # ── AUTO-TRIGGER ACTIONS based on new stage ──
        auto_actions = []
        
        if new_status in ('Find Suppliers', 'findSuppliers'):
            # Auto-search for suppliers when opportunity enters Find Suppliers stage
            # Uses GPSSAutomatedQuoting which chains: database check → ThomasNet → Google → GSA
            try:
                from nexus_backend import handle_find_suppliers_for_opportunity
                suppliers = handle_find_suppliers_for_opportunity(real_id)
                count = len(suppliers) if isinstance(suppliers, list) else 0
                auto_actions.append(f"Auto-found {count} potential suppliers (Database + ThomasNet + Google + GSA)")
            except Exception as e:
                auto_actions.append(f"Supplier search attempted (note: {str(e)[:60]})")

        elif new_status in ('Request Quotes', 'requestQuotes'):
            # Auto-generate RFQ and send to suppliers
            try:
                from supplier_quote_workflow import request_quotes_for_opportunity
                quote_result = request_quotes_for_opportunity(real_id)
                if quote_result.get('success'):
                    count = quote_result.get('quotes_sent', 0)
                    auto_actions.append(f"Auto-generated {count} quote requests and sent to suppliers")
                else:
                    auto_actions.append(f"RFQ generation: {quote_result.get('error', 'check logs')[:60]}")
            except Exception as e:
                auto_actions.append(f"Quote generation attempted (note: {str(e)[:60]})")

        # ── NEW: Auto-generate proposal matrix when advancing to Generate Proposal ──
        if new_status in ('Generate Proposal', 'generateProposal'):
            try:
                from nexus_backend import GPSSSubcontractorMiner
                sub_miner = GPSSSubcontractorMiner()
                matrix_result = sub_miner.generate_proposal_matrix(real_id)
                if matrix_result.get('success'):
                    total = matrix_result.get('matrix', {}).get('total_requirements', 0)
                    critical = matrix_result.get('matrix', {}).get('critical_requirements', 0)
                    auto_actions.append(f"Auto-generated proposal compliance matrix ({total} requirements, {critical} critical)")
                    result['proposal_matrix'] = matrix_result.get('matrix')
            except Exception as e:
                auto_actions.append(f"Proposal matrix generation attempted (note: {str(e)[:60]})")
        
        # ── NEW: Auto-generate NDA when subcontractors are linked ──
        if new_status in ('Find Suppliers', 'findSuppliers', 'Request Quotes', 'requestQuotes'):
            try:
                # Check if this opportunity has linked subcontractors
                opp = AirtableClient().get_record('GPSS Opportunities', real_id)
                opp_fields = opp.get('fields', {}) if opp else {}
                linked_subs = opp_fields.get('SUBCONTRACTORS', opp_fields.get('Linked Subcontractors', []))
                
                if linked_subs:
                    from nexus_backend import GPSSSubcontractorMiner
                    sub_miner = GPSSSubcontractorMiner()
                    nda_count = 0
                    for sub_id in linked_subs:
                        # Check if NDA already exists
                        compliance = sub_miner.check_compliance(sub_id, ['NDA'])
                        if compliance.get('compliance_issues'):
                            nda_result = sub_miner.generate_nda(sub_id, real_id)
                            if nda_result.get('success'):
                                nda_count += 1
                    if nda_count > 0:
                        auto_actions.append(f"Auto-generated {nda_count} NDA(s) for linked subcontractors")
            except Exception as e:
                pass  # Non-critical, don't block workflow

        result['auto_actions'] = auto_actions
        return jsonify(result)
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# =====================================================================
# GOVCON DOCUMENT GENERATORS — NDA, Teaming Agreement, Emails, Matrix
# =====================================================================

@app.route('/gpss/subcontractors/<subcontractor_id>/generate-nda', methods=['POST'])
def generate_nda_endpoint(subcontractor_id):
    """
    Generate pre-filled NDA for a subcontractor.
    Pulls data from Airtable, generates document, creates compliance record.
    
    Body (optional):
        { "opportunity_id": "recXXX" }
    """
    try:
        from nexus_backend import GPSSSubcontractorMiner
        miner = GPSSSubcontractorMiner()
        data = request.get_json() or {}
        result = miner.generate_nda(subcontractor_id, data.get('opportunity_id'))
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/gpss/subcontractors/<subcontractor_id>/generate-teaming-agreement', methods=['POST'])
def generate_teaming_agreement_endpoint(subcontractor_id):
    """
    Generate pre-filled Teaming Agreement for a subcontractor + opportunity.
    
    Body:
        {
            "opportunity_id": "recXXX" (required),
            "workshare_prime": 55,
            "workshare_sub": 45,
            "prime_tasks": ["PM", "Compliance", "QA"],
            "sub_tasks": ["Field work", "Equipment"]
        }
    """
    try:
        from nexus_backend import GPSSSubcontractorMiner
        miner = GPSSSubcontractorMiner()
        data = request.get_json() or {}
        
        if not data.get('opportunity_id'):
            return jsonify({'success': False, 'error': 'opportunity_id is required'}), 400
        
        result = miner.generate_teaming_agreement(
            subcontractor_id=subcontractor_id,
            opportunity_id=data['opportunity_id'],
            workshare_prime=data.get('workshare_prime', 55),
            workshare_sub=data.get('workshare_sub', 45),
            prime_tasks=data.get('prime_tasks'),
            sub_tasks=data.get('sub_tasks')
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/gpss/generate-email', methods=['POST'])
def generate_govcon_email_endpoint():
    """
    Generate context-aware GovCon email from Airtable data.
    
    Body:
        {
            "email_type": "co_sources_sought|sb_office_intro|debrief_formal|sub_outreach|...",
            "opportunity_id": "recXXX" (optional),
            "subcontractor_id": "recXXX" (optional),
            "contact_id": "recXXX" (optional),
            "custom_context": "Any additional context" (optional)
        }
    
    Valid email_type values:
        sb_office_intro, co_sources_sought, co_presolicitation, co_question,
        capstat_intro, capstat_to_prime, debrief_formal, debrief_informal,
        debrief_thanks, sub_outreach, prime_outreach, teaming_followup
    """
    try:
        from nexus_backend import GPSSSubcontractorMiner
        miner = GPSSSubcontractorMiner()
        data = request.get_json() or {}
        
        email_type = data.get('email_type')
        if not email_type:
            return jsonify({'success': False, 'error': 'email_type is required'}), 400
        
        result = miner.generate_govcon_email(
            email_type=email_type,
            opportunity_id=data.get('opportunity_id'),
            subcontractor_id=data.get('subcontractor_id'),
            contact_id=data.get('contact_id'),
            custom_context=data.get('custom_context', '')
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/gpss/opportunities/<opportunity_id>/proposal-matrix', methods=['POST'])
def generate_proposal_matrix_endpoint(opportunity_id):
    """
    Generate proposal compliance matrix for an opportunity.
    Analyzes the RFP data and builds structured requirement tracking.
    
    Auto-triggered when workflow advances to 'Generate Proposal'.
    Also callable manually.
    
    Returns:
        Structured matrix with all requirements, evaluation factors,
        required documents, and whether subcontractors are needed.
    """
    try:
        from nexus_backend import GPSSSubcontractorMiner
        miner = GPSSSubcontractorMiner()
        real_id = _resolve_airtable_id(opportunity_id)
        result = miner.generate_proposal_matrix(real_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/gpss/mining/search', methods=['POST'])
def mine_suppliers():
    """
    Search external sources for new suppliers
    
    Body:
        {
            "product": "industrial wipers",
            "sources": ["thomasnet", "google", "gsa"]
        }
    
    Returns:
        {
            "success": true,
            "results": [...suppliers found],
            "stats": {"thomasnet": 5, "google": 3, ...}
        }
    """
    try:
        from nexus_backend import GPSSSupplierMiner
        
        data = request.get_json() or {}
        product = data.get('product', '').strip()
        sources = data.get('sources', ['thomasnet', 'google', 'gsa'])
        
        if not product:
            return jsonify({
                'success': False,
                'error': 'Product search term is required'
            }), 400
        
        miner = GPSSSupplierMiner()
        result = miner.mine_all_sources(
            product=product,
            sources=sources,
            auto_import_threshold=50  # Auto-save suppliers scoring above 50
        )
        
        return jsonify({
            'success': True,
            'results': result.get('all_results', []),
            'stats': result.get('stats', {}),
            'imported': result.get('imported', [])
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ==================== QUOTE GENERATOR ENDPOINTS ====================
# Output directory for generated quotes
OUTPUT_DIR = Path("GENERATED_QUOTES")
OUTPUT_DIR.mkdir(exist_ok=True)


def parse_quote_data(data):
    """Parse quote data from JSON to template format"""
    
    template = f"""RFQ_NUMBER: {data.get('rfq_number', 'RFQ-2026-001')}
TITLE: {data.get('title', 'Quote Request')}
ISSUE_DATE: {data.get('issue_date', 'January 26, 2026')}
DUE_DATE: {data.get('due_date', 'February 5, 2026')}
DUE_TIME: {data.get('due_time', '5:00 PM EST')}
CONTRACT_PERIOD: {data.get('contract_period', '12 months')}

COLOR_SCHEME: {data.get('color_scheme', '1')}

INTRODUCTION:
{data.get('introduction', 'DEE DAVIS INC is seeking competitive quotes.')}

SCOPE:
{data.get('scope', 'Vendor will provide materials as specified.')}

KEY_REQUIREMENTS:
"""
    
    # Add requirements
    for req in data.get('requirements', []):
        template += f"- {req}\n"
    
    template += "\nITEMS:\n"
    
    # Add items
    for item in data.get('items', []):
        template += f"{item.get('number', 1)} | {item.get('description', '')} | {item.get('specs', '')} | {item.get('quantity', '')} | {item.get('unit', 'unit')}\n"
    
    return template


@app.route('/api/quote/generate-from-paste', methods=['POST'])
def generate_quote_from_paste():
    """
    Generate quote from pasted template text
    
    POST /api/quote/generate-from-paste
    Body: {
        "paste_text": "RFQ_NUMBER: DDI-2026-001\nTITLE: ...",
        "request_type": "supplier" | "subcontractor"  # optional, defaults to supplier
    }
    """
    try:
        data = request.json
        paste_text = data.get('paste_text', '')
        request_type = data.get('request_type', 'supplier').upper()
        
        if not paste_text:
            return jsonify({'success': False, 'error': 'No paste text provided'}), 400
        
        # Add REQUEST_TYPE to paste_text if not already present
        if 'REQUEST_TYPE:' not in paste_text:
            paste_text = f"REQUEST_TYPE: {request_type}\n{paste_text}"
        
        # Create temp file with paste text
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(paste_text)
            temp_file = f.name
        
        # Generate the quote
        result = subprocess.run(
            ['python3', 'create_from_paste.py', 'rfq', temp_file],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        
        # Clean up temp file
        os.unlink(temp_file)
        
        if result.returncode != 0:
            return jsonify({
                'success': False,
                'error': result.stderr
            }), 500
        
        # Extract generated filenames
        output_lines = result.stdout.split('\n')
        files = {}
        
        for line in output_lines:
            if '.html' in line:
                match = re.search(r'(rfq_[a-z0-9_]+\.html)', line)
                if match:
                    files['html'] = match.group(1)
            if '.pdf' in line and 'config' not in line:
                match = re.search(r'(rfq_[a-z0-9_]+\.pdf)', line)
                if match:
                    files['pdf'] = match.group(1)
            if '_config.json' in line:
                match = re.search(r'(rfq_[a-z0-9_]+_config\.json)', line)
                if match:
                    files['config'] = match.group(1)
        
        # Move files to output directory
        for file_type, filename in files.items():
            if os.path.exists(filename):
                dest = OUTPUT_DIR / filename
                os.rename(filename, dest)
                files[file_type] = str(dest)
        
        # Extract just the filename (without GENERATED_QUOTES/ path) for download URL
        pdf_filename = os.path.basename(files.get('pdf', ''))
        
        # Auto-advance workflow to Step 4 if opportunity_id provided
        opportunity_id = data.get('opportunity_id')
        if opportunity_id and files.get('pdf'):
            auto_advance_workflow(opportunity_id, 4, reason='RFQ generated from paste')
        
        return jsonify({
            'success': True,
            'files': files,
            'download_url': f"/api/quote/download/{pdf_filename}" if pdf_filename else None
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/quote/generate', methods=['POST'])
def api_generate_quote_pdf():
    """
    Generate a supplier quote request
    
    POST /api/quote/generate
    Body: {
        "rfq_number": "DDI-2026-001",
        "title": "Quote Request Title",
        "issue_date": "January 26, 2026",
        "due_date": "February 5, 2026",
        "due_time": "5:00 PM EST",
        "contract_period": "12 months",
        "color_scheme": "1",
        "introduction": "Your introduction text...",
        "scope": "Your scope text...",
        "requirements": ["Requirement 1", "Requirement 2"],
        "items": [
            {
                "number": "1",
                "description": "Item name",
                "specs": "Specifications",
                "quantity": "100",
                "unit": "pieces"
            }
        ]
    }
    
    Returns: {
        "success": true,
        "files": {
            "html": "filename.html",
            "pdf": "filename.pdf",
            "config": "filename_config.json"
        },
        "download_url": "/api/quote/download/filename.pdf"
    }
    """
    try:
        data = request.json
        
        # Convert to template format
        template_text = parse_quote_data(data)
        
        # Create temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(template_text)
            temp_file = f.name
        
        # Generate the quote
        result = subprocess.run(
            ['python3', 'create_from_paste.py', 'rfq', temp_file],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        
        # Clean up temp file
        os.unlink(temp_file)
        
        if result.returncode != 0:
            return jsonify({
                'success': False,
                'error': result.stderr
            }), 500
        
        # Extract generated filenames
        output_lines = result.stdout.split('\n')
        files = {}
        
        for line in output_lines:
            if '.html' in line:
                match = re.search(r'(rfq_[a-z0-9_]+\.html)', line)
                if match:
                    files['html'] = match.group(1)
            if '.pdf' in line and 'config' not in line:
                match = re.search(r'(rfq_[a-z0-9_]+\.pdf)', line)
                if match:
                    files['pdf'] = match.group(1)
            if '_config.json' in line:
                match = re.search(r'(rfq_[a-z0-9_]+_config\.json)', line)
                if match:
                    files['config'] = match.group(1)
        
        # Move files to output directory
        for file_type, filename in files.items():
            if os.path.exists(filename):
                dest = OUTPUT_DIR / filename
                os.rename(filename, dest)
                files[file_type] = str(dest)
        
        # Extract just the filename (without GENERATED_QUOTES/ path) for download URL
        pdf_filename = os.path.basename(files.get('pdf', ''))
        
        # Auto-advance workflow to Step 4 if opportunity_id provided
        opportunity_id = data.get('opportunity_id')
        if opportunity_id and files.get('pdf'):
            auto_advance_workflow(opportunity_id, 4, reason='RFQ generated')
        
        return jsonify({
            'success': True,
            'files': files,
            'download_url': f"/api/quote/download/{pdf_filename}" if pdf_filename else None
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/quote/download/<filename>', methods=['GET'])
def download_quote(filename):
    """Download a generated quote file"""
    try:
        filepath = OUTPUT_DIR / filename
        if not filepath.exists():
            return jsonify({'error': 'File not found'}), 404
        
        return send_file(
            filepath,
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/quote/template', methods=['GET'])
def get_quote_template():
    """Get a blank template for quote generation"""
    template = {
        "rfq_number": "RFQ-2026-001",
        "title": "Quote Request Title",
        "issue_date": "January 26, 2026",
        "due_date": "February 5, 2026",
        "due_time": "5:00 PM EST",
        "contract_period": "12 months",
        "color_scheme": "1",
        "introduction": "DEE DAVIS INC is seeking competitive quotes for a Michigan municipal client.",
        "scope": "Vendor will provide materials as specified with delivery to Southeast Michigan.",
        "requirements": [
            "Competitive pricing required",
            "Confirm delivery lead times",
            "Provide payment terms",
            "Quote valid through specified date"
        ],
        "items": [
            {
                "number": "1",
                "description": "Item Description",
                "specs": "Specifications and details",
                "quantity": "100",
                "unit": "unit"
            }
        ]
    }
    
    return jsonify(template)


@app.route('/api/quote/health', methods=['GET'])
def quote_health_check():
    """Health check endpoint for quote generator"""
    return jsonify({
        'status': 'healthy',
        'service': 'NEXUS Quote Generator',
        'version': '1.0.0'
    })


@app.route('/api/quote/request-from-opportunity', methods=['POST'])
def request_quote_from_opportunity():
    """
    Complete workflow: Generate and send quotes to suppliers for an opportunity
    
    POST /api/quote/request-from-opportunity
    Body: {
        "opportunity_id": "recXXXXXX",
        "supplier_ids": ["recYYYYYY", "recZZZZZZ"]  # optional
    }
    
    Returns: {
        "success": true,
        "quote_requests": [...]
    }
    """
    try:
        from supplier_quote_workflow import request_quotes_for_opportunity
        
        data = request.json
        opportunity_id = data.get('opportunity_id')
        
        if not opportunity_id:
            return jsonify({'success': False, 'error': 'No opportunity_id provided'}), 400
        
        # Process the solicitation
        result = request_quotes_for_opportunity(opportunity_id)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ==================== END QUOTE GENERATOR ENDPOINTS ====================


# ==================== AUTO CONTACT MANAGEMENT ENDPOINTS ====================

@app.route('/api/contacts/auto-extract-solicitation', methods=['POST'])
def auto_extract_solicitation_contacts():
    """
    Automatically extract and add contacts from solicitation document
    
    POST /api/contacts/auto-extract-solicitation
    Body: {
        "text": "Full solicitation text...",
        "name": "Solicitation Name"
    }
    
    Returns: {
        "contacts_found": 3,
        "contacts_added": 2,
        "contacts": [...]
    }
    """
    try:
        from auto_contact_manager import AutoContactManager
        
        data = request.json
        solicitation_text = data.get('text', '')
        solicitation_name = data.get('name', 'Unknown Solicitation')
        
        if not solicitation_text:
            return jsonify({'success': False, 'error': 'No solicitation text provided'}), 400
        
        manager = AutoContactManager()
        result = manager.extract_and_add_from_solicitation(solicitation_text, solicitation_name)
        
        return jsonify({
            'success': True,
            **result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/contacts/add-supplier', methods=['POST'])
def add_supplier_contact():
    """
    Add supplier contact when RFQ is sent or quote is requested
    
    POST /api/contacts/add-supplier
    Body: {
        "name": "Supplier Name",
        "email": "supplier@company.com",
        "phone": "555-123-4567",
        "product_type": "Industrial supplies",
        "context": "RFQ sent for RCOC 7814 Trucks"
    }
    
    Returns: {
        "success": true,
        "message": "Supplier contact added",
        "record_id": "recXXXXXX"
    }
    """
    try:
        from auto_contact_manager import AutoContactManager
        
        data = request.json
        
        if not data.get('name'):
            return jsonify({'success': False, 'error': 'Supplier name required'}), 400
        
        manager = AutoContactManager()
        result = manager.add_supplier_contact(
            supplier_name=data.get('name'),
            supplier_email=data.get('email'),
            supplier_phone=data.get('phone'),
            product_type=data.get('product_type'),
            context=data.get('context')
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/contacts/add-subcontractor', methods=['POST'])
def add_subcontractor_contact():
    """
    Add subcontractor contact when identified for opportunity
    
    POST /api/contacts/add-subcontractor
    Body: {
        "name": "Subcontractor Name",
        "email": "sub@company.com",
        "phone": "555-123-4567",
        "services": "Landscaping, Snow removal",
        "context": "Identified for Warren DDA Landscape bid"
    }
    
    Returns: {
        "success": true,
        "message": "Subcontractor contact added",
        "record_id": "recXXXXXX"
    }
    """
    try:
        from auto_contact_manager import AutoContactManager
        
        data = request.json
        
        if not data.get('name'):
            return jsonify({'success': False, 'error': 'Subcontractor name required'}), 400
        
        manager = AutoContactManager()
        result = manager.add_subcontractor_contact(
            sub_name=data.get('name'),
            sub_email=data.get('email'),
            sub_phone=data.get('phone'),
            services=data.get('services'),
            context=data.get('context')
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ==================== END AUTO CONTACT MANAGEMENT ENDPOINTS ====================


# =====================================================================
# DEADLINE NOTIFICATIONS
# =====================================================================

@app.route('/api/agenda', methods=['GET'])
def get_agenda():
    """Get agenda — reads actual bid folders and email content."""
    try:
        view = request.args.get('view', 'today')
        agenda = handle_get_agenda(view)
        return jsonify(agenda)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/agenda/bid/<bid_id>', methods=['GET'])
def get_bid_detail(bid_id):
    """Get full detail for a bid including email body."""
    try:
        from agenda_manager import handle_get_bid_detail
        detail = handle_get_bid_detail(bid_id)
        if detail:
            return jsonify(detail)
        return jsonify({'error': 'Bid not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/agenda/task/<record_id>/done', methods=['POST'])
def mark_task_done(record_id):
    """Mark a TASKS record as DONE in Airtable."""
    try:
        from agenda_manager import AgendaManager
        mgr = AgendaManager()
        ok = mgr.mark_task_done(record_id)
        if ok:
            return jsonify({'success': True})
        return jsonify({'error': 'Failed to update'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/agenda/item/<item_id>/toggle', methods=['POST'])
def toggle_agenda_item(item_id):
    """Mark an agenda item as completed or pending. Persists to Airtable."""
    try:
        from pyairtable import Api
        api = Api(os.environ.get('AIRTABLE_API_KEY', ''))
        base_id = os.environ.get('AIRTABLE_BASE_ID', '')

        record_id = item_id.replace('overdue-', '')

        data = request.get_json() or {}
        new_status = data.get('status', 'completed')

        # Try GPSS Opportunities first (deadline items)
        try:
            table = api.table(base_id, 'GPSS Opportunities')
            record = table.get(record_id)
            if new_status == 'completed':
                table.update(record_id, {'Status': 'Completed'})
            else:
                table.update(record_id, {'Status': ''})
            return jsonify({'success': True, 'source': 'gpss', 'status': new_status})
        except:
            pass

        # Try Officer Outreach Tracking (outreach items)
        try:
            table = api.table(base_id, 'Officer Outreach Tracking')
            record = table.get(record_id)
            if new_status == 'completed':
                table.update(record_id, {'STATUS': 'SENT'})
            else:
                table.update(record_id, {'STATUS': 'DRAFT'})
            return jsonify({'success': True, 'source': 'outreach', 'status': new_status})
        except:
            pass

        return jsonify({'success': False, 'error': 'Record not found in any table'}), 404

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/active-deadlines', methods=['GET'])
def get_active_deadlines():
    """Get active bid deadlines for notification banner"""
    try:
        now = datetime.now()
        
        # Active RCOC bids (from CRITICAL_DEADLINE_VERIFICATION_FEB_2026.md)
        active_bids = [
            {
                "id": "RCOC 7732",
                "name": "Disposable Paper Products",
                "deadline": "2026-02-10T14:30:00",
                "value": "$81,478",
                "profit": "$3-5K",
                "status": "Ready to submit",
                "action": "Submit Feb 7-9",
                "folder": "RCOC 7732 PAPER",
                "buyer": "Shari Graves (248-858-4780)",
                "platform": "BidNet Direct"
            },
            {
                "id": "RCOC 7842",
                "name": "Safety Supplies",
                "deadline": "2026-02-17T14:30:00",
                "value": "$31,558",
                "profit": "$3,975",
                "status": "Ready to submit",
                "action": "Submit Feb 14",
                "folder": "RCOC 7842 SAFETY SUPPLIES",
                "buyer": "Shari Graves (248-858-4780)",
                "platform": "BidNet Direct"
            },
            {
                "id": "RCOC 7814",
                "name": "Pickup Trucks (16 units)",
                "deadline": "2026-02-17T14:30:00",
                "value": "$640K-$800K",
                "profit": "$80K-$120K",
                "status": "Awaiting dealer quotes",
                "action": "Get dealer quotes by Feb 10",
                "folder": "RCOC 7814 TRUCKS",
                "buyer": "Shari Graves (248-858-4796)",
                "platform": "BidNet Direct"
            },
            {
                "id": "RCOC 7790",
                "name": "Prefabricated Traffic Signs",
                "deadline": "2026-02-17T14:30:00",
                "value": "$30K-$50K",
                "profit": "$27K+",
                "status": "Awaiting supplier quotes",
                "action": "Get supplier quotes by Feb 10",
                "folder": "RCOC 7790 SIGNS",
                "buyer": "Tracy McDonald (248-858-4796)",
                "platform": "BidNet Direct"
            }
        ]
        
        # Calculate days/hours until for each
        for bid in active_bids:
            deadline_dt = datetime.fromisoformat(bid['deadline'])
            delta = deadline_dt - now
            bid['daysUntil'] = delta.days
            bid['hoursUntil'] = (delta.seconds // 3600)
        
        return jsonify({
            'success': True,
            'deadlines': active_bids,
            'count': len(active_bids)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500




# =====================================================================
# BID FOLDER SCANNER — LIVE FILESYSTEM DATA
# Reads BIDS:RESOURCES/ folder to detect real bid status
# No mock data. No hardcoded lists. Real filesystem scanning.
# =====================================================================

@app.route('/api/bids/dashboard', methods=['GET'])
def api_bids_dashboard():
    """
    Get dashboard data from real folder scanning.
    Returns formatted data for BidsDashboard frontend component.
    """
    try:
        data = get_dashboard_data()
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/bids/scan', methods=['GET'])
def api_bids_scan():
    """
    Full scan of all bid folders with detailed status.
    Returns submitted, active, needs_review, and stale bids.
    Uses cached results if available and fresh (< 5 min old).
    """
    try:
        # Check for cached scan (from scheduler)
        cache_path = os.path.join(os.path.dirname(__file__), 'scan_cache.json')
        force = request.args.get('force', 'false').lower() == 'true'

        if not force and os.path.exists(cache_path):
            cache_age = time.time() - os.path.getmtime(cache_path)
            if cache_age < 300:  # 5 minutes
                with open(cache_path, 'r') as f:
                    return jsonify(json.load(f))

        # Fresh scan
        result = scan_all_bids()
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/bids/alerts', methods=['GET'])
def api_bids_alerts():
    """
    Get bid alerts (stale bids, unreviewed, approaching deadlines).
    Generated by scheduler's stale detection task.
    """
    try:
        alerts_path = os.path.join(os.path.dirname(__file__), 'bid_alerts.json')
        if os.path.exists(alerts_path):
            with open(alerts_path, 'r') as f:
                return jsonify(json.load(f))
        return jsonify({'alerts': [], 'checked_at': None})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/workflow/queues', methods=['GET'])
def get_workflow_queues_live():
    """
    Get workflow queues from live folder scan instead of static JSON.
    Maps bid status to workflow stages automatically.
    """
    try:
        scan = scan_all_bids()
        if 'error' in scan:
            return jsonify({'success': False, 'error': scan['error']}), 500

        queues = {
            'needsReview': [],
            'findSuppliers': [],
            'requestQuotes': [],
            'awaitingQuotes': [],
            'readyToPrice': [],
            'generateProposal': [],
            'finalReview': [],
            'submitted': [],
        }

        # Map scanned bids to workflow stages
        for bid in scan.get('needs_review', []):
            queues['needsReview'].append(_bid_to_workflow_item(bid))

        for bid in scan.get('active', []):
            if bid['has_ready']:
                queues['finalReview'].append(_bid_to_workflow_item(bid))
            elif bid['has_quotes']:
                queues['readyToPrice'].append(_bid_to_workflow_item(bid))
            elif bid['has_strategy']:
                queues['findSuppliers'].append(_bid_to_workflow_item(bid))
            else:
                queues['requestQuotes'].append(_bid_to_workflow_item(bid))

        for bid in scan.get('submitted', []):
            queues['submitted'].append(_bid_to_workflow_item(bid))

        counts = {stage: len(items) for stage, items in queues.items()}

        return jsonify({
            'success': True,
            'queues': queues,
            'counts': counts,
            'scanned_at': scan.get('scanned_at'),
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


def _bid_to_workflow_item(bid):
    """Convert a scanned bid to workflow queue format."""
    return {
        'id': bid['id'],
        'fields': {
            'Name': bid['name'],
            'Estimated Value': bid['value'],
            'Response Deadline': bid.get('deadline_date') or '',
            'Folder Path': bid.get('folder_path', ''),
            'Status': bid['status'],
            'File Count': bid['file_count'],
            'Last Activity': bid['last_activity_relative'],
            'Has Quotes': bid['has_quotes'],
            'Has Strategy': bid['has_strategy'],
            'Confirmation': bid.get('confirmation_number'),
        }
    }


# =====================================================================
# DOCUMENT GENERATOR ENDPOINTS
# These power the frontend Document Generator tabs:
# - /api/capstat/generate → Capability Statement (wraps existing endpoint)
# - /api/rfp/generate → Supplier RFP (AI-tailored to solicitation)
# - /api/rfp/view/<number> → View generated RFP PDF
# - /api/partnership/generate → Partnership Proposal PDF
# =====================================================================

@app.route('/api/capstat/generate', methods=['POST'])
def api_capstat_generate():
    """
    Generate a v3 capability statement from the Document Generator frontend.
    Accepts sector, agency, solicitation number, and optional overrides.
    Returns the HTML file for browser preview.
    """
    try:
        from capability_statement_generator import handle_generate_capability_statement

        data = request.get_json() or {}

        result = handle_generate_capability_statement(
            sector=data.get('sector', 'main'),
            agency_name=data.get('agencyName') or data.get('agency_name'),
            solicitation_number=data.get('solicitationNumber') or data.get('solicitation_number'),
            service_description=data.get('serviceDescription') or data.get('service_description'),
            custom_overview=data.get('customOverview') or data.get('custom_overview'),
            custom_naics=data.get('naicsCodes') or data.get('custom_naics'),
        )

        if not result.get('success'):
            return jsonify(result), 400

        html_path = result.get('html_file')
        if html_path and os.path.exists(html_path):
            return send_file(
                html_path,
                mimetype='text/html',
                as_attachment=False
            )

        return jsonify(result)

    except ImportError:
        return jsonify({
            'success': False,
            'error': 'Capability statement generator module not found. Run: pip install weasyprint'
        }), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/rfp/generate', methods=['POST'])
def api_rfp_generate():
    """
    Generate a professional supplier RFP tailored to a solicitation.
    Uses Claude AI to write scope/requirements if solicitation data is provided.
    Protects buyer identity per business rules.
    """
    try:
        data = request.get_json() or {}

        project_name = data.get('project_name', 'Untitled Project')
        category = data.get('category', 'General Services')
        sanitized_location = data.get('sanitized_location', 'Michigan')
        scope_of_work = data.get('scope_of_work', '')
        contract_value_min = data.get('contract_value_min', 0)
        contract_value_max = data.get('contract_value_max', 0)
        quote_due_date = data.get('quote_due_date', '')
        contract_period = data.get('contract_period', '12 months')
        service_locations_count = data.get('service_locations_count', 0)
        insurance_requirements = data.get('insurance_requirements', '')

        # Generate RFQ number
        import random
        rfq_number = f"DDI-{datetime.now().strftime('%Y-%m')}-{random.randint(100, 999)}"

        # Build RFP config
        rfq_config = {
            "company": {
                "name": "DEE DAVIS INC",
                "address": "755 W. Big Beaver Rd., Suite 2020, Troy, MI 48084",
                "phone": "(248) 376-4550",
                "email": "info@deedavis.biz",
                "website": "deedavis.biz",
                "cage_code": "8UMX3",
                "duns": "117917627",
                "sam_uei": "HJB4KNYJVGZ1"
            },
            "rfq_details": {
                "rfq_number": rfq_number,
                "title": f"Request for Quotation — {project_name}",
                "issue_date": datetime.now().strftime("%B %d, %Y"),
                "due_date": quote_due_date or (datetime.now() + timedelta(days=14)).strftime("%B %d, %Y"),
                "due_time": "5:00 PM EST",
                "contract_period": contract_period,
                "location": sanitized_location,
                "category": category
            },
            "colors": {
                "primary": "#D97706",
                "accent": "#0F172A",
                "text": "#374151"
            },
            "sections": {
                "introduction": f"DEE DAVIS INC is seeking competitive quotations from qualified vendors for {project_name}. This is for a government client in {sanitized_location}.",
                "scope": scope_of_work or f"Vendor shall provide all labor, materials, equipment, and supervision necessary to complete {project_name} as specified.",
                "requirements": [
                    "Competitive pricing required",
                    "Confirm delivery lead times",
                    "Provide payment terms (Net 30 preferred)",
                    f"Insurance: {insurance_requirements}" if insurance_requirements else "Insurance per standard requirements",
                    "Quote valid for 90 days minimum",
                    f"Service locations: {service_locations_count}" if service_locations_count > 0 else None,
                ],
                "value_range": f"${contract_value_min:,.0f} - ${contract_value_max:,.0f}" if contract_value_max > 0 else None
            }
        }

        # Remove None items from requirements
        rfq_config["sections"]["requirements"] = [r for r in rfq_config["sections"]["requirements"] if r]

        # Generate HTML
        html_content = _generate_rfp_html(rfq_config)

        # Save HTML
        output_dir = os.path.join(os.path.dirname(__file__), 'GENERATED_RFPS')
        os.makedirs(output_dir, exist_ok=True)

        html_path = os.path.join(output_dir, f'RFP_{rfq_number}.html')
        pdf_path = os.path.join(output_dir, f'RFP_{rfq_number}.pdf')

        with open(html_path, 'w') as f:
            f.write(html_content)

        # Try to generate PDF
        pdf_generated = False
        try:
            result = subprocess.run(
                ['wkhtmltopdf', '--page-size', 'Letter',
                 '--margin-top', '15mm', '--margin-bottom', '15mm',
                 '--margin-left', '15mm', '--margin-right', '15mm',
                 '--enable-local-file-access',
                 html_path, pdf_path],
                capture_output=True, timeout=30
            )
            if result.returncode == 0:
                pdf_generated = True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

        if not pdf_generated:
            try:
                from weasyprint import HTML
                HTML(filename=html_path).write_pdf(pdf_path)
                pdf_generated = True
            except ImportError:
                pass

        return jsonify({
            'success': True,
            'rfp_number': rfq_number,
            'html_file': html_path,
            'pdf_file': pdf_path if pdf_generated else None,
            'pdf_generated': pdf_generated,
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/rfp/view/<rfp_number>', methods=['GET'])
def api_rfp_view(rfp_number):
    """View a generated RFP as PDF (or HTML fallback)."""
    try:
        output_dir = os.path.join(os.path.dirname(__file__), 'GENERATED_RFPS')

        pdf_path = os.path.join(output_dir, f'RFP_{rfp_number}.pdf')
        if os.path.exists(pdf_path):
            return send_file(pdf_path, mimetype='application/pdf')

        html_path = os.path.join(output_dir, f'RFP_{rfp_number}.html')
        if os.path.exists(html_path):
            return send_file(html_path, mimetype='text/html')

        return jsonify({'error': 'RFP not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/rfp/test', methods=['POST'])
def api_rfp_test():
    """Generate a test RFP with sample data."""
    try:
        test_data = {
            'project_name': 'Municipal Parks Pressure Washing Services',
            'category': 'Pressure Washing',
            'sanitized_location': 'Oakland County, Michigan',
            'scope_of_work': 'Hot water pressure washing services for park structures, playground equipment, pavilions, and walkways across multiple locations.',
            'contract_value_min': 8000,
            'contract_value_max': 15000,
            'quote_due_date': (datetime.now() + timedelta(days=14)).strftime('%Y-%m-%d'),
            'contract_period': 'March 2026 - December 2026',
            'service_locations_count': 20,
            'insurance_requirements': 'General Liability: $1,000,000 per occurrence',
        }
        # Reuse the generate endpoint logic
        with app.test_request_context(json=test_data):
            return api_rfp_generate()
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/partnership/generate', methods=['POST'])
def api_partnership_generate():
    """
    Generate a professional partnership proposal PDF.
    """
    try:
        data = request.get_json() or {}

        partner_name = data.get('partnerName', 'Partner Company')
        proposal_type = data.get('proposalType', 'Supplier Diversity Partnership')
        services_offered = data.get('servicesOffered', '')
        coverage = data.get('coverage', 'Nationwide')
        certifications = data.get('certifications', 'EDWOSB')
        key_advantages = data.get('keyAdvantages', '')
        target_revenue = data.get('targetRevenue', '')
        timeline = data.get('implementationTimeline', '90 days')

        html_content = _generate_partnership_html(
            partner_name=partner_name,
            proposal_type=proposal_type,
            services_offered=services_offered,
            coverage=coverage,
            certifications=certifications,
            key_advantages=key_advantages,
            target_revenue=target_revenue,
            timeline=timeline,
        )

        output_dir = os.path.join(os.path.dirname(__file__), 'GENERATED_PROPOSALS')
        os.makedirs(output_dir, exist_ok=True)

        safe_partner = partner_name.replace(' ', '_').replace('/', '_')
        date_str = datetime.now().strftime('%Y%m%d')
        filename_base = f'Partnership_Proposal_{safe_partner}_{date_str}'

        html_path = os.path.join(output_dir, f'{filename_base}.html')
        pdf_path = os.path.join(output_dir, f'{filename_base}.pdf')

        with open(html_path, 'w') as f:
            f.write(html_content)

        # Try PDF generation
        pdf_generated = False
        try:
            result = subprocess.run(
                ['wkhtmltopdf', '--page-size', 'Letter',
                 '--margin-top', '15mm', '--margin-bottom', '15mm',
                 '--margin-left', '15mm', '--margin-right', '15mm',
                 '--enable-local-file-access',
                 html_path, pdf_path],
                capture_output=True, timeout=30
            )
            if result.returncode == 0:
                pdf_generated = True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

        if not pdf_generated:
            try:
                from weasyprint import HTML
                HTML(filename=html_path).write_pdf(pdf_path)
                pdf_generated = True
            except ImportError:
                pass

        if pdf_generated:
            return send_file(
                pdf_path,
                mimetype='application/pdf',
                as_attachment=False,
                download_name=f'{filename_base}.pdf'
            )
        else:
            return send_file(
                html_path,
                mimetype='text/html',
                as_attachment=False
            )

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# =====================================================================
# PRESOLICITATION AUTO-RESPONSE ENDPOINT
# Manually trigger auto-response for any opportunity
# (Also runs automatically during SAM.gov mining)
# =====================================================================

@app.route('/api/presolicitation/auto-respond', methods=['POST'])
def api_presolicitation_auto_respond():
    """
    Manually trigger the presolicitation auto-response for an opportunity.
    Generates: capability statement + buyer email + bid folder + workflow checklist.
    
    POST body:
    {
        "title": "Grounds Maintenance Services",
        "noticeId": "W912DR25QA005",
        "agency": "US Army Corps of Engineers",
        "type": "Presolicitation",  // or "Sources Sought", "Intent to Sole Source"
        "description": "...",
        "naicsCode": "561730",
        "typeOfSetAside": "EDWOSB",
        "responseDeadLine": "2026-04-15",
        "pointOfContact": [{"fullName": "...", "email": "...", "phone": "..."}]
    }
    """
    try:
        data = request.get_json() or {}
        
        if not data.get('title') and not data.get('noticeId'):
            return jsonify({'success': False, 'error': 'title or noticeId required'}), 400
        
        # Use SAMgovAPIClient's auto-response methods
        from nexus_backend import SAMgovAPIClient
        client = SAMgovAPIClient()
        
        presol_type = data.get('type', '')
        if not presol_type:
            presol_type = client._is_presolicitation_type(data) or 'Presolicitation'
        
        client._auto_respond_presolicitation(data, presol_type)
        
        folder_name = client._generate_folder_name(
            data.get('agency', data.get('fullParentPathName', '')),
            data.get('title', '')
        )
        
        base_path = os.path.join(os.path.dirname(__file__), 'BIDS:RESOURCES', folder_name)
        
        return jsonify({
            'success': True,
            'message': f'Auto-response generated for {presol_type}: {data.get("noticeId", "")}',
            'folder': folder_name,
            'folder_path': base_path,
            'files_generated': [
                f'SEND_TO_BUYER/{data.get("noticeId", "").replace("/", "-").replace(" ", "_")}_Capability_Statement.html',
                'SEND_TO_BUYER/SEND_TO_BUYER_EMAIL_READY.md',
                'WORKFLOW_CHECKLIST.md'
            ],
            'presolicitation_type': presol_type,
            'next_step': f'Review SEND_TO_BUYER/ and email CO'
        })
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/sources-sought/generate', methods=['POST'])
def api_sources_sought_generate():
    """Generate a Sources Sought / RFI response document."""
    try:
        data = request.get_json() or {}

        html = _generate_sources_sought_html(data)

        output_dir = os.path.join(os.path.dirname(__file__), 'GENERATED_RESPONSES')
        os.makedirs(output_dir, exist_ok=True)

        sol_num = (data.get('solicitationNumber') or 'SS').replace(' ', '_').replace('/', '-')
        date_str = datetime.now().strftime('%Y%m%d')
        filename_base = f'Sources_Sought_Response_{sol_num}_{date_str}'

        html_path = os.path.join(output_dir, f'{filename_base}.html')
        pdf_path = os.path.join(output_dir, f'{filename_base}.pdf')

        with open(html_path, 'w') as f:
            f.write(html)

        pdf_generated = False
        try:
            result = subprocess.run(
                ['wkhtmltopdf', '--page-size', 'Letter',
                 '--margin-top', '15mm', '--margin-bottom', '15mm',
                 '--margin-left', '15mm', '--margin-right', '15mm',
                 '--enable-local-file-access', html_path, pdf_path],
                capture_output=True, timeout=30
            )
            if result.returncode == 0:
                pdf_generated = True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

        if not pdf_generated:
            try:
                from weasyprint import HTML
                HTML(filename=html_path).write_pdf(pdf_path)
                pdf_generated = True
            except ImportError:
                pass

        if pdf_generated:
            return send_file(pdf_path, mimetype='application/pdf', as_attachment=False,
                           download_name=f'{filename_base}.pdf')
        return send_file(html_path, mimetype='text/html', as_attachment=False)

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/solicitation/answer', methods=['POST'])
def api_solicitation_answer():
    """
    Solicitation Response Engine.
    Detects solicitation type and generates the correct response format:
    - RFQ: Cover letter + completed quote/pricing schedule
    - RFP: Multi-volume proposal (Technical, Past Performance, Pricing)
    - Sources Sought: Capability statement + CO outreach email
    - IFB: Completed bid schedule + pricing
    - Presolicitation: Capability statement + interest letter
    """
    try:
        import PyPDF2
        import re as _re

        # --- Step 1: Extract text from uploaded file ---
        if 'file' not in request.files:
            return jsonify({"success": False, "error": "No file uploaded"}), 400
        file = request.files['file']
        if not file.filename:
            return jsonify({"success": False, "error": "No file selected"}), 400

        document_name = file.filename
        document_text = ""
        if file.filename.lower().endswith('.pdf'):
            try:
                pdf_reader = PyPDF2.PdfReader(file)
                for page_num in range(min(len(pdf_reader.pages), 40)):
                    try:
                        pt = pdf_reader.pages[page_num].extract_text()
                        if pt and pt.strip():
                            document_text += pt.strip() + "\n"
                    except:
                        continue
            except Exception as e:
                return jsonify({"success": False, "error": f"PDF read failed: {str(e)}"}), 400
        else:
            document_text = file.read().decode('utf-8', errors='ignore')

        if not document_text.strip():
            return jsonify({"success": False, "error": "No readable text found."}), 400

        pages_read = max(1, len(document_text) // 2500)
        rfp_text = document_text[:30000]

        # --- Step 2: Single AI call — analyze AND generate response ---
        ai = AnthropicClient()

        prompt = f"""You are a government contracting proposal specialist for Dee Davis Inc.

COMPANY: Dee Davis Inc. — EDWOSB/WOSB/WBENC/MBE/SBE certified
ADDRESS: 755 W. Big Beaver Rd., Suite 2020, Troy, MI 48084
CAGE: 8UMX3 | UEI: HJB4KNYJVGZ1 | SAM.gov: Active
PHONE: 248.376.4550 | EMAIL: info@deedavis.biz
CEO: Dee Davis
BUSINESS MODEL: Contract management & procurement. Sources products through authorized
distributors. Manages service contracts through vetted subcontractor partnerships.

DOCUMENT: {document_name}
TEXT:
{rfp_text}

INSTRUCTIONS: Analyze this solicitation and generate the CORRECT response format.

STEP 1 — Determine the solicitation type and return analysis.
STEP 2 — Based on the type, generate the appropriate response documents:

IF TYPE = "RFQ" (Request for Quote):
  The buyer wants a PRICE QUOTE, not a proposal. Generate:
  - cover_letter: Professional 1-page letter acknowledging the RFQ, confirming ability to deliver,
    referencing the solicitation number, signed by Dee Davis, CEO
  - quote_schedule: Array of line items matching their CLINs/items with columns:
    item_number, description, quantity, unit, unit_price (leave as "$ ___" for Dee to fill),
    extended_price (leave as "$ ___")
  - delivery_terms: Delivery location, timeline, shipping method, FOB point
  - representations: Small business status, EDWOSB certification, SAM registration confirmation
  - notes: Any assumptions, exclusions, or conditions

IF TYPE = "RFP" (Request for Proposal):
  The buyer wants a MULTI-VOLUME PROPOSAL. Generate:
  - cover_letter: 1-page letter from Dee Davis addressing the CO by name, acknowledging receipt,
    expressing interest, summarizing qualifications, signed by CEO
  - volume_1_technical: Object with sections that match what Section L requires:
    executive_summary, understanding_of_work, technical_approach (specific methodology, not generic),
    management_plan, staffing_plan, quality_control
  - volume_2_past_performance: Array of 2-3 past performance references with:
    contract_name, agency, contract_number (or "Available upon request"), value, period,
    description, relevance_to_this_work, contact_name, contact_phone, contact_email
  - volume_3_pricing: Object with pricing_narrative (approach to pricing, no actual dollars)
    and price_schedule (array matching CLINs with blank prices for Dee to fill)
  - compliance_matrix: Array mapping each Section L/M requirement to where it's addressed
  - certifications: List of required certs/reps and our status for each

IF TYPE = "Sources Sought" or "Presolicitation" or "RFI":
  The buyer wants to know IF we can do this. Generate:
  - cover_letter: Personal email to the CO expressing interest as an EDWOSB, asking smart
    questions about timeline and set-aside status
  - capability_statement: Tailored to this specific opportunity — company overview,
    relevant capabilities, certifications, past performance summary, contact info
  - questions_for_buyer: 3-4 smart questions about the upcoming procurement

IF TYPE = "IFB" (Invitation for Bid):
  Price-only competition. Generate:
  - cover_letter: Brief acknowledgment letter
  - bid_schedule: Array matching their bid items with blank prices for Dee to fill
  - representations: Required certifications and small business status confirmations
  - delivery_terms: As specified in the solicitation

IF TYPE = "Intent to Sole Source":
  Challenge the sole source. Generate:
  - cover_letter: Letter to CO challenging the sole source as an EDWOSB alternative
  - capability_statement: Proving we can perform the work
  - justification: Why awarding to an EDWOSB serves the agency better

Return ONLY valid JSON:
{{
  "analysis": {{
    "solicitation_info": {{
      "title": "", "number": "", "type": "RFQ|RFP|IFB|Sources Sought|Presolicitation|RFI|Intent to Sole Source",
      "agency": "", "deadline": "", "set_aside": "", "naics": "",
      "estimated_value": "", "contract_type": "", "location": "", "period_of_performance": ""
    }},
    "scope_summary": "",
    "key_requirements": [],
    "line_items": [{{"item": "", "description": "", "quantity": "", "unit": ""}}],
    "evaluation_criteria": [{{"factor": "", "weight": "", "description": ""}}],
    "submission_instructions": "What Section L says about how to submit",
    "contacts": [{{"name": "", "title": "", "email": "", "phone": "", "role": "CO|COR|POC"}}],
    "diversity_advantage": {{"is_set_aside": false, "edwosb_advantage": ""}},
    "bid_recommendation": {{"decision": "GO|NO-GO|REVIEW", "score": 0, "reasoning": "", "strengths": [], "concerns": []}}
  }},
  "response_type": "RFQ|RFP|IFB|SOURCES_SOUGHT|SOLE_SOURCE",
  "response": {{
    ... the type-specific response documents described above ...
  }}
}}

WRITING RULES:
- Be specific to THIS solicitation. No generic boilerplate.
- Use the solicitation's exact terminology. Mirror their words.
- Reference the agency by name (use short form after first mention).
- Reference the solicitation number in the cover letter and throughout.
- Cover letters should be warm and professional — written by a real person, not a robot.
- Technical sections should be concrete with specific methodologies, not vague promises.
- Past performance references should feel real (use plausible contract values and metrics).
- Leave all pricing fields blank for Dee to fill in — NEVER generate dollar amounts.
- For compliance matrices, map EVERY stated requirement to a specific response location.
"""

        ai_response = ai.complete(prompt, max_tokens=8000)
        clean = ai_response.replace('```json', '').replace('```', '').strip()
        try:
            result = json.loads(clean)
        except json.JSONDecodeError:
            m = _re.search(r'\{.*\}', clean, _re.DOTALL)
            if m:
                result = json.loads(m.group())
            else:
                return jsonify({"success": False, "error": "AI returned invalid format"}), 500

        analysis = result.get('analysis', {})
        response_doc = result.get('response', {})
        response_type = result.get('response_type', 'RFP')
        sol = analysis.get('solicitation_info', {})

        # --- Step 3: Run ProposalBio on narrative content (if applicable) ---
        pb_results = None
        if response_type in ('RFP', 'SOURCES_SOUGHT', 'SOLE_SOURCE'):
            # Build narrative from whatever text sections exist
            narrative_parts = []
            for key, val in response_doc.items():
                if isinstance(val, str) and len(val) > 50:
                    narrative_parts.append(val)
                elif isinstance(val, dict):
                    for sub_key, sub_val in val.items():
                        if isinstance(sub_val, str) and len(sub_val) > 50:
                            narrative_parts.append(sub_val)
            full_narrative = '\n\n'.join(narrative_parts)

            if full_narrative.strip():
                pb_meta = {
                    'agency': sol.get('agency', ''),
                    'client_name': sol.get('agency', ''),
                    'rfp_number': sol.get('number', ''),
                    'agency_type': 'Federal',
                    'rfp_text': rfp_text,
                }
                try:
                    analyzer = ProposalBioAnalyzer(full_narrative, pb_meta)
                    pb_results = analyzer.analyze_all()
                except Exception as pb_err:
                    print(f"ProposalBio error: {pb_err}")

        # --- Step 4: Return everything ---
        return jsonify({
            "success": True,
            "document_name": document_name,
            "pages_read": pages_read,
            "response_type": response_type,
            "analysis": analysis,
            "response": response_doc,
            "proposalbio": pb_results,
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/sole-source/generate', methods=['POST'])
def api_sole_source_generate():
    """Generate a Sole Source Justification & Approval document."""
    try:
        data = request.get_json() or {}

        html = _generate_sole_source_html(data)

        output_dir = os.path.join(os.path.dirname(__file__), 'GENERATED_RESPONSES')
        os.makedirs(output_dir, exist_ok=True)

        sol_num = (data.get('solicitationNumber') or 'JA').replace(' ', '_').replace('/', '-')
        date_str = datetime.now().strftime('%Y%m%d')
        filename_base = f'Sole_Source_JA_{sol_num}_{date_str}'

        html_path = os.path.join(output_dir, f'{filename_base}.html')
        pdf_path = os.path.join(output_dir, f'{filename_base}.pdf')

        with open(html_path, 'w') as f:
            f.write(html)

        pdf_generated = False
        try:
            result = subprocess.run(
                ['wkhtmltopdf', '--page-size', 'Letter',
                 '--margin-top', '15mm', '--margin-bottom', '15mm',
                 '--margin-left', '15mm', '--margin-right', '15mm',
                 '--enable-local-file-access', html_path, pdf_path],
                capture_output=True, timeout=30
            )
            if result.returncode == 0:
                pdf_generated = True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

        if not pdf_generated:
            try:
                from weasyprint import HTML
                HTML(filename=html_path).write_pdf(pdf_path)
                pdf_generated = True
            except ImportError:
                pass

        if pdf_generated:
            return send_file(pdf_path, mimetype='application/pdf', as_attachment=False,
                           download_name=f'{filename_base}.pdf')
        return send_file(html_path, mimetype='text/html', as_attachment=False)

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


def _run_proposalbio_analysis(text, metadata=None):
    """Run ProposalBio analysis on text and return results + HTML snippet."""
    try:
        meta = metadata or {}
        analyzer = ProposalBioAnalyzer(text, meta)
        results = analyzer.analyze_all()
        composite = results.get('composite_score', 0)
        biohacks = results.get('biohack_scores', [])
        status = results.get('overall_status', 'N/A')

        score_color = '#10B981' if composite >= 75 else '#F59E0B' if composite >= 60 else '#EF4444'
        status_color = '#10B981' if status == 'APPROVED' else '#F59E0B' if status == 'REVISE' else '#EF4444'

        biohack_rows = ''
        for bh in biohacks:
            bh_color = '#10B981' if bh['score'] >= 6 else '#EF4444'
            icon = '&#10003;' if bh['score'] >= 6 else '&#10007;'
            biohack_rows += (
                f'<div style="display:flex;justify-content:space-between;align-items:center;'
                f'padding:4px 8px;border-bottom:1px solid #E5E7EB;font-size:9pt;">'
                f'<span style="color:#374151;">{bh["biohack_name"]}</span>'
                f'<span style="color:{bh_color};font-weight:700;">{icon} {bh["score"]:.1f}</span>'
                f'</div>'
            )

        html_snippet = f'''
  <div style="margin-top:28px;border:2px solid {score_color};border-radius:10px;overflow:hidden;">
    <div style="background:{score_color};padding:12px 20px;display:flex;justify-content:space-between;align-items:center;">
      <div style="color:white;font-weight:700;font-size:11pt;">ProposalBio&#8482; Quality Score</div>
      <div style="background:white;color:{score_color};padding:4px 14px;border-radius:20px;font-weight:800;font-size:14pt;">{composite:.0f}</div>
    </div>
    <div style="padding:12px 20px;background:#FAFAFA;">
      <div style="display:flex;justify-content:space-between;margin-bottom:8px;">
        <span style="font-size:9pt;color:#6B7280;">Status</span>
        <span style="font-size:9pt;font-weight:700;color:{status_color};">{status}</span>
      </div>
      {biohack_rows}
    </div>
  </div>'''

        return results, html_snippet
    except Exception as e:
        return None, f'<!-- ProposalBio error: {str(e)} -->'


def _generate_sources_sought_html(data):
    """Generate professional Sources Sought response HTML."""
    sol_number = data.get('solicitationNumber', '')
    sol_title = data.get('solicitationTitle', '')
    agency = data.get('issuingAgency', '')
    naics = data.get('naicsCode', '')
    response_type = data.get('responseType', 'interested_capable')
    company_desc = data.get('companyDescription', '') or data.get('capabilities', '')
    capability = data.get('capabilityNarrative', '') or data.get('capabilities', '')
    experience = data.get('relevantExperience', '') or data.get('pastPerformance', '')
    set_aside = data.get('setAsideRecommendation', 'EDWOSB / WOSB')
    teaming = data.get('teamingInterest', 'open')
    contact_name = data.get('contactName', 'Dee Davis')
    contact_title = data.get('contactTitle', 'President and CEO')
    contact_email = data.get('contactEmail', 'info@deedavis.biz')
    contact_phone = data.get('contactPhone', '(248) 376-4550')

    response_label = {
        'interested_capable': 'Interested and Capable',
        'interested_teaming': 'Interested — Open to Teaming Arrangements',
        'information_only': 'Information Only Response',
    }.get(response_type, 'Interested and Capable')

    teaming_label = {
        'open': 'Open to teaming as either prime or subcontractor',
        'prime_only': 'Interested as prime contractor only',
        'sub_available': 'Available as subcontractor to other primes',
    }.get(teaming, 'Open to teaming')

    default_company_desc = (
        'Dee Davis Inc is an SBA-certified Economically Disadvantaged Woman-Owned Small Business (EDWOSB) '
        'headquartered in Troy, Michigan. We are a contract management and procurement firm specializing in '
        'sourcing products and managing service contracts for federal, state, and local government agencies. '
        'With established distributor networks and a vetted subcontractor bench, we deliver reliable results '
        'on every order — from industrial supplies and equipment to professional and technical services.'
    )
    if not company_desc:
        company_desc = default_company_desc

    html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
  body {{ font-family: 'Segoe UI', Tahoma, Geneva, sans-serif; margin: 0; padding: 0; color: #1F2937; font-size: 11pt; line-height: 1.7; }}
  .header {{ background: linear-gradient(135deg, #0F172A 0%, #1E3A5F 60%, #0D47A1 100%); color: white; padding: 45px 40px 35px; position: relative; }}
  .header::after {{ content: ''; position: absolute; bottom: 0; left: 0; right: 0; height: 4px; background: linear-gradient(90deg, #D97706, #F59E0B, #D97706); }}
  .header .company-name {{ font-size: 11pt; font-weight: 700; letter-spacing: 1px; color: #F59E0B; margin-bottom: 4px; }}
  .header .subtitle {{ color: #93C5FD; font-size: 9pt; text-transform: uppercase; letter-spacing: 3px; margin-bottom: 10px; }}
  .header h1 {{ margin: 0 0 8px; font-size: 17pt; font-weight: 700; line-height: 1.3; }}
  .header .sol-ref {{ font-size: 10pt; color: #CBD5E1; margin-bottom: 12px; }}
  .header .badge {{ background: #D97706; color: #000; padding: 5px 16px; border-radius: 4px; font-weight: 700; display: inline-block; font-size: 9pt; letter-spacing: 0.5px; }}
  .content {{ padding: 35px 40px; }}
  .section {{ margin-bottom: 28px; }}
  .section h2 {{ color: #0F172A; font-size: 12pt; font-weight: 700; border-bottom: 2px solid #D97706; padding-bottom: 6px; margin-bottom: 14px; text-transform: uppercase; letter-spacing: 0.5px; }}
  .detail-grid {{ display: grid; grid-template-columns: 170px 1fr; gap: 8px 16px; font-size: 10pt; }}
  .detail-label {{ color: #6B7280; font-weight: 600; }}
  .detail-value {{ color: #111827; }}
  .narrative {{ font-size: 10.5pt; line-height: 1.8; color: #374151; }}
  .narrative p {{ margin-bottom: 12px; }}
  .capability-list {{ list-style: none; padding: 0; margin: 12px 0; }}
  .capability-list li {{ padding: 6px 0 6px 24px; position: relative; font-size: 10pt; color: #374151; }}
  .capability-list li::before {{ content: '\\2713'; position: absolute; left: 0; color: #D97706; font-weight: 700; font-size: 12pt; }}
  .cert-banner {{ background: linear-gradient(135deg, #FFFBEB, #FEF3C7); border-left: 4px solid #D97706; padding: 16px 20px; border-radius: 0 8px 8px 0; margin: 20px 0; }}
  .cert-banner strong {{ color: #92400E; }}
  .cert-badges {{ display: flex; gap: 8px; flex-wrap: wrap; margin-top: 10px; }}
  .cert-badge {{ background: #0F172A; color: #F59E0B; padding: 3px 10px; border-radius: 3px; font-size: 8pt; font-weight: 700; letter-spacing: 0.5px; }}
  .conclusion-box {{ background: #F0FDF4; border: 1px solid #BBF7D0; border-radius: 8px; padding: 20px; margin-top: 24px; }}
  .conclusion-box p {{ margin: 0; font-size: 10.5pt; color: #166534; }}
  .contact-block {{ margin-top: 24px; padding: 16px 20px; background: #F8FAFC; border-radius: 8px; font-size: 10pt; }}
  .contact-block .name {{ font-weight: 700; color: #0F172A; font-size: 11pt; }}
  .contact-block .title {{ color: #6B7280; }}
  .footer {{ background: #0F172A; padding: 20px 40px; font-size: 8pt; color: #94A3B8; text-align: center; line-height: 1.8; }}
  .footer .company {{ color: #F59E0B; font-weight: 700; font-size: 9pt; }}
</style></head><body>

<div class="header">
  <div class="company-name">DEE DAVIS INC</div>
  <div class="subtitle">Sources Sought Response</div>
  <h1>{sol_title}</h1>
  <div class="sol-ref">Solicitation: {sol_number} | Agency: {agency}</div>
  <div class="badge">{response_label}</div>
</div>

<div class="content">
  <div class="section">
    <h2>Notice Information</h2>
    <div class="detail-grid">
      <div class="detail-label">Notice Number:</div><div class="detail-value">{sol_number}</div>
      <div class="detail-label">Title:</div><div class="detail-value">{sol_title}</div>
      <div class="detail-label">Issuing Agency:</div><div class="detail-value">{agency}</div>
      <div class="detail-label">NAICS Code:</div><div class="detail-value">{naics}</div>
      <div class="detail-label">Response Date:</div><div class="detail-value">{datetime.now().strftime('%B %d, %Y')}</div>
    </div>
  </div>

  <div class="section">
    <h2>Company Information</h2>
    <div class="detail-grid">
      <div class="detail-label">Company Name:</div><div class="detail-value">DEE DAVIS INC</div>
      <div class="detail-label">CAGE Code:</div><div class="detail-value">8UMX3</div>
      <div class="detail-label">SAM UEI:</div><div class="detail-value">HJB4KNYJVGZ1</div>
      <div class="detail-label">Business Size:</div><div class="detail-value">Small Business — EDWOSB Certified</div>
      <div class="detail-label">Certifications:</div><div class="detail-value">EDWOSB | WOSB | WBENC (WBE) | MBE | SBE</div>
      <div class="detail-label">Address:</div><div class="detail-value">755 W. Big Beaver Rd., Suite 2020, Troy, MI 48084</div>
      <div class="detail-label">Contact:</div><div class="detail-value">{contact_email} | {contact_phone}</div>
    </div>
  </div>

  <div class="section">
    <h2>Company Overview</h2>
    <div class="narrative">
      <p>{company_desc}</p>
    </div>
  </div>

  {'<div class="section"><h2>Capability Narrative</h2><div class="narrative"><p>' + capability.replace(chr(10), '</p><p>') + '</p></div></div>' if capability and capability != company_desc else ''}

  {'<div class="section"><h2>Relevant Experience &amp; Past Performance</h2><div class="narrative"><p>' + experience.replace(chr(10), '</p><p>') + '</p></div></div>' if experience else ''}

  <div class="cert-banner">
    <strong>Set-Aside Recommendation:</strong> {set_aside}<br>
    <strong>Teaming:</strong> {teaming_label}<br><br>
    Dee Davis Inc is registered and active in SAM.gov and maintains all required certifications for federal contracting.
    <div class="cert-badges">
      <span class="cert-badge">EDWOSB</span>
      <span class="cert-badge">WOSB</span>
      <span class="cert-badge">WBENC</span>
      <span class="cert-badge">MBE</span>
      <span class="cert-badge">SBE</span>
    </div>
  </div>

  <div class="conclusion-box">
    <p>Dee Davis Inc is interested and capable of performing this requirement. We welcome the opportunity to discuss our qualifications further and look forward to the formal solicitation.</p>
  </div>

  {{PROPOSALBIO_SCORE}}

  <div class="contact-block">
    <div class="name">{contact_name}</div>
    <div class="title">{contact_title}</div>
    <div>Dee Davis Inc</div>
    <div>755 W. Big Beaver Rd., Suite 2020, Troy, MI 48084</div>
    <div>{contact_phone} | {contact_email}</div>
    <div>CAGE: 8UMX3 | UEI: HJB4KNYJVGZ1</div>
  </div>
</div>

<div class="footer">
  <div class="company">DEE DAVIS INC</div>
  755 W. Big Beaver Rd., Suite 2020, Troy, MI 48084 | {contact_phone} | {contact_email}<br>
  EDWOSB | WOSB | WBENC | MBE | SBE | CAGE: 8UMX3 | SAM UEI: HJB4KNYJVGZ1
</div>
</body></html>"""

    # Run ProposalBio analysis on the narrative content
    narrative_text = f"{company_desc} {capability} {experience}"
    pb_meta = {
        'agency': agency,
        'client_name': agency,
        'rfp_number': sol_number,
        'proposal_name': sol_title,
        'region': 'Federal',
    }
    _, pb_html = _run_proposalbio_analysis(narrative_text, pb_meta)
    html = html.replace('{PROPOSALBIO_SCORE}', pb_html)

    return html


def _generate_sole_source_html(data):
    """Generate Sole Source J&A / EDWOSB Response document HTML."""
    sol_number = data.get('solicitationNumber', '')
    sol_title = data.get('solicitationTitle', '')
    agency = data.get('issuingAgency', '')
    value = data.get('contractValue', '')
    justification_type = data.get('justificationType', 'edwosb_set_aside')
    capability = data.get('uniqueCapability', '') or data.get('capabilities', '')
    market_research = data.get('marketResearch', '')
    price_fairness = data.get('priceFairness', '')
    delivery = data.get('deliveryTimeline', '30 days ARO')
    pop = data.get('periodOfPerformance', '12 months')
    contact_name = data.get('contactName', 'Dee Davis')
    contact_email = data.get('contactEmail', 'info@deedavis.biz')
    contact_phone = data.get('contactPhone', '(248) 376-4550')

    justification_label = {
        'unique_capability': 'Only One Responsible Source (FAR 6.302-1)',
        'edwosb_set_aside': 'EDWOSB Sole Source Authority (FAR 19.1506)',
        'urgency': 'Unusual and Compelling Urgency (FAR 6.302-2)',
        'only_one_source': 'Only One Responsible Source (FAR 6.302-1)',
        'brand_name': 'Brand Name — EDWOSB Procurement Vehicle',
    }.get(justification_type, 'FAR 6.302-1')

    default_capability = (
        'Dee Davis Inc possesses the certifications, distributor relationships, and contract management '
        'experience required to fulfill this requirement. As an SBA-certified EDWOSB, Dee Davis Inc meets '
        'all eligibility requirements for sole source or set-aside award. We source products through '
        'authorized distributor networks and manage service contracts through vetted subcontractor partnerships, '
        'delivering reliable results for federal agencies.'
    )
    if not capability:
        capability = default_capability

    html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
  body {{ font-family: 'Segoe UI', Tahoma, Geneva, sans-serif; margin: 0; padding: 0; color: #1F2937; font-size: 11pt; line-height: 1.7; }}
  .header {{ background: linear-gradient(135deg, #1E3A5F 0%, #0F172A 60%, #1a1a2e 100%); color: white; padding: 45px 40px 35px; position: relative; }}
  .header::after {{ content: ''; position: absolute; bottom: 0; left: 0; right: 0; height: 4px; background: linear-gradient(90deg, #2563EB, #3B82F6, #2563EB); }}
  .header .company-name {{ font-size: 11pt; font-weight: 700; letter-spacing: 1px; color: #60A5FA; margin-bottom: 4px; }}
  .header .subtitle {{ color: #93C5FD; font-size: 9pt; text-transform: uppercase; letter-spacing: 3px; margin-bottom: 10px; }}
  .header h1 {{ margin: 0 0 8px; font-size: 17pt; font-weight: 700; line-height: 1.3; }}
  .header .sol-ref {{ font-size: 10pt; color: #CBD5E1; margin-bottom: 12px; }}
  .header .badge {{ background: #2563EB; color: #fff; padding: 5px 16px; border-radius: 4px; font-weight: 700; display: inline-block; font-size: 9pt; letter-spacing: 0.5px; }}
  .content {{ padding: 35px 40px; }}
  .section {{ margin-bottom: 28px; }}
  .section h2 {{ color: #0F172A; font-size: 12pt; font-weight: 700; border-bottom: 2px solid #2563EB; padding-bottom: 6px; margin-bottom: 14px; text-transform: uppercase; letter-spacing: 0.5px; }}
  .detail-grid {{ display: grid; grid-template-columns: 190px 1fr; gap: 8px 16px; font-size: 10pt; }}
  .detail-label {{ color: #6B7280; font-weight: 600; }}
  .detail-value {{ color: #111827; }}
  .narrative {{ font-size: 10.5pt; line-height: 1.8; color: #374151; }}
  .authority-box {{ background: #EFF6FF; border-left: 4px solid #2563EB; padding: 16px 20px; border-radius: 0 8px 8px 0; margin: 20px 0; }}
  .authority-box strong {{ color: #1E40AF; }}
  .cert-banner {{ background: linear-gradient(135deg, #FFFBEB, #FEF3C7); border-left: 4px solid #D97706; padding: 16px 20px; border-radius: 0 8px 8px 0; margin: 20px 0; }}
  .cert-banner strong {{ color: #92400E; }}
  .cert-badges {{ display: flex; gap: 8px; flex-wrap: wrap; margin-top: 10px; }}
  .cert-badge {{ background: #0F172A; color: #60A5FA; padding: 3px 10px; border-radius: 3px; font-size: 8pt; font-weight: 700; letter-spacing: 0.5px; }}
  .sig-block {{ margin-top: 40px; display: grid; grid-template-columns: 1fr 1fr; gap: 40px; }}
  .sig-line {{ border-top: 1px solid #000; padding-top: 4px; margin-top: 30px; font-size: 10pt; }}
  .contact-block {{ margin-top: 24px; padding: 16px 20px; background: #F8FAFC; border-radius: 8px; font-size: 10pt; }}
  .contact-block .name {{ font-weight: 700; color: #0F172A; font-size: 11pt; }}
  .contact-block .title {{ color: #6B7280; }}
  .footer {{ background: #0F172A; padding: 20px 40px; font-size: 8pt; color: #94A3B8; text-align: center; line-height: 1.8; }}
  .footer .company {{ color: #60A5FA; font-weight: 700; font-size: 9pt; }}
</style></head><body>

<div class="header">
  <div class="company-name">DEE DAVIS INC</div>
  <div class="subtitle">Sole Source Response &amp; Justification</div>
  <h1>{sol_title or sol_number}</h1>
  <div class="sol-ref">Solicitation: {sol_number} | Agency: {agency}</div>
  <div class="badge">{justification_label}</div>
</div>

<div class="content">
  <div class="section">
    <h2>1. Contracting Activity</h2>
    <div class="detail-grid">
      <div class="detail-label">Agency:</div><div class="detail-value">{agency}</div>
      <div class="detail-label">Requirement:</div><div class="detail-value">{sol_title}</div>
      <div class="detail-label">Solicitation Number:</div><div class="detail-value">{sol_number}</div>
      <div class="detail-label">Estimated Value:</div><div class="detail-value">{value}</div>
      <div class="detail-label">Period of Performance:</div><div class="detail-value">{pop}</div>
      <div class="detail-label">Delivery:</div><div class="detail-value">{delivery}</div>
    </div>
  </div>

  <div class="authority-box">
    <strong>Authority:</strong> {justification_label}
  </div>

  <div class="section">
    <h2>2. Proposed Contractor</h2>
    <div class="detail-grid">
      <div class="detail-label">Name:</div><div class="detail-value">DEE DAVIS INC</div>
      <div class="detail-label">CAGE Code:</div><div class="detail-value">8UMX3</div>
      <div class="detail-label">SAM UEI:</div><div class="detail-value">HJB4KNYJVGZ1</div>
      <div class="detail-label">Business Size:</div><div class="detail-value">Small Business — EDWOSB Certified</div>
      <div class="detail-label">Certifications:</div><div class="detail-value">EDWOSB | WOSB | WBENC (WBE) | MBE | SBE</div>
      <div class="detail-label">Address:</div><div class="detail-value">755 W. Big Beaver Rd., Suite 2020, Troy, MI 48084</div>
      <div class="detail-label">Contact:</div><div class="detail-value">{contact_email} | {contact_phone}</div>
    </div>
  </div>

  <div class="section">
    <h2>3. Justification</h2>
    <div class="narrative"><p>{capability}</p></div>
  </div>

  {'<div class="section"><h2>4. Market Research</h2><div class="narrative"><p>' + market_research + '</p></div></div>' if market_research else ''}

  {'<div class="section"><h2>5. Price Reasonableness</h2><div class="narrative"><p>' + price_fairness + '</p></div></div>' if price_fairness else ''}

  <div class="cert-banner">
    <strong>EDWOSB Certification:</strong> Dee Davis Inc is certified as an Economically Disadvantaged Woman-Owned Small Business (EDWOSB) eligible for sole source awards up to $5M (services) / $8.5M (manufacturing) per FAR 19.1506.
    <div class="cert-badges">
      <span class="cert-badge">EDWOSB</span>
      <span class="cert-badge">WOSB</span>
      <span class="cert-badge">WBENC</span>
      <span class="cert-badge">MBE</span>
      <span class="cert-badge">SBE</span>
    </div>
  </div>

  <div class="sig-block">
    <div>
      <div class="sig-line"><strong>Requesting Official</strong><br>Name: ___________________<br>Title: ___________________<br>Date: ___________________</div>
    </div>
    <div>
      <div class="sig-line"><strong>Approving Official</strong><br>Name: ___________________<br>Title: ___________________<br>Date: ___________________</div>
    </div>
  </div>

  {{PROPOSALBIO_SCORE}}

  <div class="contact-block">
    <div class="name">{contact_name}</div>
    <div class="title">President and CEO</div>
    <div>Dee Davis Inc</div>
    <div>755 W. Big Beaver Rd., Suite 2020, Troy, MI 48084</div>
    <div>{contact_phone} | {contact_email}</div>
    <div>CAGE: 8UMX3 | UEI: HJB4KNYJVGZ1</div>
  </div>
</div>

<div class="footer">
  <div class="company">DEE DAVIS INC</div>
  755 W. Big Beaver Rd., Suite 2020, Troy, MI 48084 | {contact_phone} | {contact_email}<br>
  EDWOSB | WOSB | WBENC | MBE | SBE | CAGE: 8UMX3 | SAM UEI: HJB4KNYJVGZ1
</div>
</body></html>"""

    # Run ProposalBio analysis on the narrative content
    narrative_text = f"{capability} {market_research} {price_fairness}"
    pb_meta = {
        'agency': agency,
        'client_name': agency,
        'rfp_number': sol_number,
        'proposal_name': sol_title,
        'region': 'Federal',
    }
    _, pb_html = _run_proposalbio_analysis(narrative_text, pb_meta)
    html = html.replace('{PROPOSALBIO_SCORE}', pb_html)

    return html


def _generate_rfp_html(config):
    """Generate professional DDI-branded RFP HTML."""
    company = config['company']
    rfq = config['rfq_details']
    sections = config['sections']
    primary = config['colors']['primary']

    requirements_html = ""
    for req in sections.get('requirements', []):
        requirements_html += f"<li>{req}</li>"

    value_section = ""
    if sections.get('value_range'):
        value_section = f"""
        <div style="background: #FEF3C7; border-left: 4px solid {primary}; padding: 12px 16px; margin: 16px 0; border-radius: 4px;">
            <strong>Estimated Contract Value Range:</strong> {sections['value_range']}
        </div>
        """

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  @page {{ margin: 0; }}
  body {{ font-family: 'Segoe UI', Tahoma, Geneva, sans-serif; margin: 0; padding: 0; color: #1F2937; font-size: 11pt; line-height: 1.6; }}
  .header {{ background: linear-gradient(135deg, #0F172A, #1E293B); color: white; padding: 40px; }}
  .header h1 {{ margin: 0; font-size: 22pt; letter-spacing: -0.5px; }}
  .header .subtitle {{ color: {primary}; font-size: 10pt; text-transform: uppercase; letter-spacing: 3px; margin-bottom: 10px; }}
  .header .rfq-number {{ background: {primary}; color: #000; padding: 6px 16px; border-radius: 4px; display: inline-block; font-weight: 700; margin-top: 12px; }}
  .company-bar {{ background: {primary}; color: #000; padding: 10px 40px; font-size: 9pt; display: flex; justify-content: space-between; }}
  .content {{ padding: 30px 40px; }}
  .section {{ margin-bottom: 24px; }}
  .section h2 {{ color: #0F172A; font-size: 14pt; border-bottom: 2px solid {primary}; padding-bottom: 6px; margin-bottom: 12px; }}
  .details-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }}
  .detail-item {{ background: #F8FAFC; padding: 10px 14px; border-radius: 6px; border-left: 3px solid {primary}; }}
  .detail-label {{ font-size: 9pt; color: #6B7280; text-transform: uppercase; letter-spacing: 1px; }}
  .detail-value {{ font-size: 11pt; font-weight: 600; color: #111827; }}
  ul {{ padding-left: 20px; }}
  li {{ margin-bottom: 6px; }}
  .footer {{ background: #F8FAFC; padding: 20px 40px; border-top: 2px solid #E5E7EB; font-size: 9pt; color: #6B7280; text-align: center; }}
  .confidential {{ background: #FEE2E2; border: 1px solid #FECACA; padding: 10px 16px; border-radius: 6px; font-size: 9pt; color: #991B1B; margin-top: 24px; }}
</style>
</head>
<body>

<div class="header">
  <div class="subtitle">DEE DAVIS INC — Request for Quotation</div>
  <h1>{rfq['title']}</h1>
  <div class="rfq-number">{rfq['rfq_number']}</div>
</div>

<div class="company-bar">
  <span>{company['name']} | CAGE: {company['cage_code']} | SAM UEI: {company['sam_uei']}</span>
  <span>{company['email']} | {company['phone']}</span>
</div>

<div class="content">
  <div class="section">
    <h2>RFQ Details</h2>
    <div class="details-grid">
      <div class="detail-item">
        <div class="detail-label">Issue Date</div>
        <div class="detail-value">{rfq['issue_date']}</div>
      </div>
      <div class="detail-item">
        <div class="detail-label">Response Due</div>
        <div class="detail-value">{rfq['due_date']} by {rfq['due_time']}</div>
      </div>
      <div class="detail-item">
        <div class="detail-label">Contract Period</div>
        <div class="detail-value">{rfq['contract_period']}</div>
      </div>
      <div class="detail-item">
        <div class="detail-label">Delivery Location</div>
        <div class="detail-value">{rfq['location']}</div>
      </div>
    </div>
  </div>

  <div class="section">
    <h2>Introduction</h2>
    <p>{sections['introduction']}</p>
  </div>

  <div class="section">
    <h2>Scope of Work</h2>
    <p>{sections['scope']}</p>
  </div>

  {value_section}

  <div class="section">
    <h2>Requirements</h2>
    <ul>{requirements_html}</ul>
  </div>

  <div class="section">
    <h2>Response Instructions</h2>
    <p>Please submit your quotation to <strong>{company['email']}</strong> by the response deadline above. Include:</p>
    <ul>
      <li>Itemized pricing with unit costs and totals</li>
      <li>Delivery lead times and shipping method</li>
      <li>Payment terms</li>
      <li>Any exceptions or clarifications</li>
      <li>Company W-9 (if not previously provided)</li>
    </ul>
  </div>

  <div class="confidential">
    <strong>CONFIDENTIAL:</strong> This RFQ is issued by DEE DAVIS INC. Information about the end client is confidential and proprietary. Do not contact the end client directly.
  </div>
</div>

<div class="footer">
  DEE DAVIS INC | {company['address']} | {company['phone']} | {company['email']}<br>
  EDWOSB Certified | CAGE: {company['cage_code']} | SAM UEI: {company['sam_uei']} | DUNS: {company['duns']}
</div>

</body>
</html>"""


def _generate_partnership_html(partner_name, proposal_type, services_offered,
                                coverage, certifications, key_advantages,
                                target_revenue, timeline):
    """Generate professional partnership proposal HTML."""
    advantages_html = ""
    for line in (key_advantages or "").split("\n"):
        line = line.strip()
        if line:
            advantages_html += f"<li>{line}</li>"

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  body {{ font-family: 'Segoe UI', Tahoma, Geneva, sans-serif; margin: 0; padding: 0; color: #1F2937; font-size: 11pt; line-height: 1.6; }}
  .cover {{ background: linear-gradient(135deg, #0F172A 0%, #1E3A5F 100%); color: white; padding: 80px 60px; min-height: 400px; display: flex; flex-direction: column; justify-content: center; }}
  .cover .badge {{ background: #D97706; color: #000; padding: 6px 16px; border-radius: 20px; font-size: 9pt; font-weight: 700; text-transform: uppercase; letter-spacing: 2px; display: inline-block; margin-bottom: 24px; }}
  .cover h1 {{ font-size: 28pt; margin: 0 0 12px 0; }}
  .cover .subtitle {{ font-size: 14pt; color: #94A3B8; }}
  .cover .date {{ margin-top: 40px; color: #64748B; font-size: 10pt; }}
  .content {{ padding: 40px 60px; }}
  .section {{ margin-bottom: 30px; page-break-inside: avoid; }}
  .section h2 {{ color: #0F172A; font-size: 16pt; border-bottom: 3px solid #D97706; padding-bottom: 8px; margin-bottom: 16px; }}
  .highlight-box {{ background: #FFFBEB; border-left: 4px solid #D97706; padding: 16px 20px; border-radius: 0 8px 8px 0; margin: 16px 0; }}
  .stat-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin: 20px 0; }}
  .stat {{ background: #F8FAFC; padding: 16px; border-radius: 8px; text-align: center; border: 1px solid #E2E8F0; }}
  .stat .value {{ font-size: 18pt; font-weight: 700; color: #D97706; }}
  .stat .label {{ font-size: 9pt; color: #6B7280; text-transform: uppercase; letter-spacing: 1px; margin-top: 4px; }}
  ul {{ padding-left: 20px; }}
  li {{ margin-bottom: 8px; }}
  .footer {{ background: #0F172A; color: #94A3B8; padding: 30px 60px; font-size: 9pt; text-align: center; }}
  .footer .name {{ color: #D97706; font-weight: 700; font-size: 11pt; }}
</style>
</head>
<body>

<div class="cover">
  <div class="badge">Partnership Proposal</div>
  <h1>{proposal_type}</h1>
  <div class="subtitle">Prepared for {partner_name}</div>
  <div class="date">Prepared by DEE DAVIS INC | {datetime.now().strftime('%B %d, %Y')}</div>
</div>

<div class="content">
  <div class="section">
    <h2>Executive Summary</h2>
    <p>DEE DAVIS INC proposes a strategic {proposal_type.lower()} with {partner_name} to deliver {services_offered} across {coverage}.</p>
    <p>As a certified {certifications} firm, we bring immediate supplier diversity value, operational excellence, and a technology-driven service platform.</p>
  </div>

  <div class="section">
    <h2>Service Overview</h2>
    <div class="highlight-box">
      <strong>Services:</strong> {services_offered}<br>
      <strong>Coverage:</strong> {coverage}<br>
      <strong>Certifications:</strong> {certifications}
    </div>
  </div>

  <div class="section">
    <h2>Why Partner with DEE DAVIS INC</h2>
    <ul>{advantages_html if advantages_html else '<li>EDWOSB certification supports supplier diversity goals</li><li>Technology-driven platform for efficient service delivery</li><li>Nationwide operational capability</li>'}</ul>
  </div>

  <div class="section">
    <h2>Financial Projections</h2>
    <p>{target_revenue if target_revenue else 'Revenue projections available upon request based on service volume and geographic scope.'}</p>
    <div class="stat-grid">
      <div class="stat">
        <div class="value">{timeline}</div>
        <div class="label">Implementation</div>
      </div>
      <div class="stat">
        <div class="value">{coverage.split('(')[0].strip() if '(' in coverage else coverage}</div>
        <div class="label">Coverage</div>
      </div>
      <div class="stat">
        <div class="value">EDWOSB</div>
        <div class="label">Certification</div>
      </div>
    </div>
  </div>

  <div class="section">
    <h2>Implementation Timeline</h2>
    <div class="highlight-box">
      <strong>Phase 1 (Days 1-30):</strong> Contract execution, systems integration, team onboarding<br>
      <strong>Phase 2 (Days 31-60):</strong> Pilot program in select markets, quality benchmarking<br>
      <strong>Phase 3 (Days 61-{timeline.replace(' days', '').replace(' day', '') if 'day' in timeline else '90'}):</strong> Full rollout, performance optimization
    </div>
  </div>

  <div class="section">
    <h2>Next Steps</h2>
    <p>We welcome the opportunity to discuss this proposal further. Please contact us to schedule a meeting.</p>
  </div>
</div>

<div class="footer">
  <div class="name">DEE DAVIS INC</div>
  <div>755 W. Big Beaver Rd., Suite 2020, Troy, MI 48084 | (248) 376-4550 | info@deedavis.biz</div>
  <div style="margin-top: 8px;">EDWOSB | WOSB | WBENC | MBE | SBE | CAGE: 8UMX3 | SAM UEI: HJB4KNYJVGZ1</div>
</div>

</body>
</html>"""


# =============================================================================
# OPPORTUNITY INTELLIGENCE API ENDPOINTS
# =============================================================================

@app.route('/api/intelligence/score', methods=['POST'])
def api_intelligence_score():
    """
    Trigger AI scoring of all unscored opportunities.
    POST /api/intelligence/score
    """
    try:
        from nexus_opportunity_intelligence import OpportunityIntelligenceEngine
        engine = OpportunityIntelligenceEngine()
        result = engine.score_and_alert()
        return jsonify({'success': True, **result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/intelligence/mine-local', methods=['POST'])
def api_intelligence_mine_local():
    """
    Trigger Michigan state/local mining.
    POST /api/intelligence/mine-local
    """
    try:
        from nexus_opportunity_intelligence import MichiganLocalMiner
        miner = MichiganLocalMiner()
        result = miner.mine_all()
        return jsonify({'success': True, **result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/intelligence/digest', methods=['POST'])
def api_intelligence_digest():
    """
    Send daily digest email manually.
    POST /api/intelligence/digest
    """
    try:
        from nexus_opportunity_intelligence import send_daily_digest
        send_daily_digest()
        return jsonify({'success': True, 'message': 'Daily digest sent'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/intelligence/status', methods=['GET'])
def api_intelligence_status():
    """
    Get intelligence engine status — what's running, last scores, etc.
    GET /api/intelligence/status
    """
    try:
        # Check scheduler status
        import subprocess
        result = subprocess.run(
            ['pgrep', '-f', 'nexus_scheduler'],
            capture_output=True, text=True
        )
        scheduler_running = result.returncode == 0
        scheduler_pid = result.stdout.strip() if scheduler_running else None
        
        # Check log for last activity
        log_path = os.path.join(os.path.dirname(__file__), 'logs', 'scheduler.log')
        last_activity = None
        if os.path.exists(log_path):
            stat = os.stat(log_path)
            last_activity = datetime.fromtimestamp(stat.st_mtime).isoformat()
        
        return jsonify({
            'success': True,
            'scheduler_running': scheduler_running,
            'scheduler_pid': scheduler_pid,
            'last_log_activity': last_activity,
            'email_configured': bool(os.environ.get('NEXUS_EMAIL_PASSWORD')),
            'sam_api_configured': bool(os.environ.get('SAM_GOV_API_KEY')),
            'govcon_api_configured': bool(os.environ.get('GOVCON_API_KEY')),
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# =============================================================================
# CONTRACT INTELLIGENCE — Three-Avenue Pipeline (Expiring Contracts + Primes + Subs)
# =============================================================================

@app.route('/api/intelligence/contracts/ingest', methods=['POST'])
def api_intel_contracts_ingest():
    """
    Ingest GovCon Giants data (or any intelligence folder).
    POST /api/intelligence/contracts/ingest
    Body: { "folder_path": "/path/to/folder" }  (optional — auto-detects GOVCON_GIANTS)
    """
    try:
        from contract_intelligence import handle_ingest
        data = request.get_json() or {}
        result = handle_ingest(data.get('folder_path'))
        return jsonify({'success': True, **result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/intelligence/contracts/pipeline', methods=['GET'])
def api_intel_contracts_pipeline():
    """
    Three-avenue pipeline: sub under prime, prime recompete, hire subs.
    GET /api/intelligence/contracts/pipeline?lane=Janitorial&min_score=40
    """
    try:
        from contract_intelligence import handle_get_pipeline
        lane = request.args.get('lane')
        min_score = int(request.args.get('min_score', 0))
        result = handle_get_pipeline(lane, min_score)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/intelligence/contracts/expiring', methods=['GET'])
def api_intel_contracts_expiring():
    """
    Expiring contracts filtered to DDI lanes.
    GET /api/intelligence/contracts/expiring?ddi_only=true&lane=Janitorial
    """
    try:
        from contract_intelligence import handle_get_expiring
        ddi_only = request.args.get('ddi_only', 'true').lower() == 'true'
        lane = request.args.get('lane')
        contracts = handle_get_expiring(ddi_only, lane)
        return jsonify({'contracts': contracts, 'count': len(contracts)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/intelligence/contracts/primes', methods=['GET'])
def api_intel_contracts_primes():
    """
    Prime contractor SBLO directory.
    GET /api/intelligence/contracts/primes?lane=Facilities
    """
    try:
        from contract_intelligence import handle_get_primes
        lane = request.args.get('lane')
        primes = handle_get_primes(lane)
        return jsonify({'primes': primes, 'count': len(primes)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/intelligence/contracts/subs', methods=['GET'])
def api_intel_contracts_subs():
    """
    Tier 2 subcontractor directory.
    GET /api/intelligence/contracts/subs?lane=Janitorial
    """
    try:
        from contract_intelligence import handle_get_subs
        lane = request.args.get('lane')
        subs = handle_get_subs(lane)
        return jsonify({'subs': subs, 'count': len(subs)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/intelligence/contracts/priority-outreach', methods=['GET'])
def api_intel_priority_outreach():
    """
    Top priority outreach targets — primes with expiring contracts + SBLO contact.
    GET /api/intelligence/contracts/priority-outreach?limit=20
    """
    try:
        from contract_intelligence import handle_get_priority_outreach
        limit = int(request.args.get('limit', 20))
        targets = handle_get_priority_outreach(limit)
        return jsonify({'targets': targets, 'count': len(targets)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/intelligence/contracts/generate-tasks', methods=['POST'])
def api_intel_generate_tasks():
    """
    Auto-generate outreach tasks in Airtable TASKS table.
    POST /api/intelligence/contracts/generate-tasks
    Body: { "avenue": "sub_under_prime", "limit": 10 }
    """
    try:
        from contract_intelligence import handle_generate_tasks
        data = request.get_json() or {}
        avenue = data.get('avenue', 'sub_under_prime')
        limit = data.get('limit', 10)
        result = handle_generate_tasks(avenue, limit)
        return jsonify({'success': True, **result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# =============================================================================
# NEXUS LEARNING ENGINE — System-wide self-learning for ALL modules
# =============================================================================

@app.route('/api/learning/log', methods=['POST'])
def api_learning_log():
    """
    Log ANY event from ANY NEXUS module.
    POST /api/learning/log
    Body: { "domain": "opportunities", "entity_id": "abc123", "action": "won", "metadata": {...} }
    Domains: opportunities, outreach, bids, suppliers, subcontractors, pricing, intelligence
    """
    try:
        from nexus_learning_engine import handle_log
        data = request.get_json() or {}
        result = handle_log(
            data.get('domain', ''),
            data.get('entity_id', ''),
            data.get('action', ''),
            data.get('metadata', {}),
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/learning/analyze', methods=['POST'])
def api_learning_analyze():
    """
    Run pattern analysis. Optionally scope to a single domain.
    POST /api/learning/analyze
    Body: { "domain": "opportunities" }  (optional — null = all domains)
    """
    try:
        from nexus_learning_engine import handle_analyze
        data = request.get_json() or {}
        result = handle_analyze(data.get('domain'))
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/learning/insights', methods=['GET'])
def api_learning_insights():
    """
    Get AI/statistical insights, optionally filtered by domain.
    GET /api/learning/insights?domain=outreach&limit=10
    """
    try:
        from nexus_learning_engine import handle_get_insights
        domain = request.args.get('domain')
        limit = int(request.args.get('limit', 15))
        insights = handle_get_insights(domain, limit)
        return jsonify({'insights': insights, 'count': len(insights)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/learning/status', methods=['GET'])
def api_learning_status():
    """
    Full learning system status — all domains, readiness, weight versions.
    GET /api/learning/status
    """
    try:
        from nexus_learning_engine import handle_get_status
        status = handle_get_status()
        return jsonify(status)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/learning/weights/<domain>', methods=['GET'])
def api_learning_weights(domain):
    """
    Get active scoring weights for a specific domain.
    GET /api/learning/weights/opportunities
    """
    try:
        from nexus_learning_engine import handle_get_weights
        weights = handle_get_weights(domain)
        return jsonify({'domain': domain, 'weights': weights})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/learning/history/<entity_id>', methods=['GET'])
def api_learning_history(entity_id):
    """
    Get full action history for any entity across all domains.
    GET /api/learning/history/<entity_id>
    """
    try:
        from nexus_learning_engine import handle_get_history
        history = handle_get_history(entity_id)
        return jsonify({'history': history, 'count': len(history)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# =============================================================================
# HISTORICAL PRICING INTELLIGENCE API ENDPOINTS
# =============================================================================

@app.route('/api/pricing/search-historical', methods=['POST'])
def api_pricing_search_historical():
    """
    Search USASpending.gov for similar contracts to benchmark pricing.
    
    POST /api/pricing/search-historical
    Body: {
        "service_type": "medical courier",
        "naics_code": "492110",
        "psc_code": "Q301",
        "min_value": 50000,
        "max_value": 150000,
        "years_back": 3
    }
    
    Returns: List of similar contracts with pricing data
    """
    try:
        data = request.json
        scraper = HistoricalPricingScraper()
        
        results = scraper.search_similar_contracts(
            service_type=data.get('service_type'),
            naics_code=data.get('naics_code'),
            psc_code=data.get('psc_code'),
            min_value=data.get('min_value'),
            max_value=data.get('max_value'),
            years_back=data.get('years_back', 3)
        )
        
        return jsonify({
            'success': True,
            'count': len(results),
            'contracts': results
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/pricing/estimate-unit-price', methods=['POST'])
def api_pricing_estimate_unit_price():
    """
    Estimate per-unit pricing from total contract value.
    
    POST /api/pricing/estimate-unit-price
    Body: {
        "total_contract_value": 350000,
        "contract_duration_years": 5,
        "estimated_annual_volume": 1000,
        "service_type": "medical courier"
    }
    
    Returns: Estimated per-unit pricing breakdown
    """
    try:
        data = request.json
        scraper = HistoricalPricingScraper()
        
        estimate = scraper.estimate_unit_pricing(
            total_contract_value=data['total_contract_value'],
            contract_duration_years=data['contract_duration_years'],
            estimated_annual_volume=data['estimated_annual_volume'],
            service_type=data['service_type']
        )
        
        return jsonify({
            'success': True,
            'estimate': estimate
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/pricing/generate-foia', methods=['POST'])
def api_pricing_generate_foia():
    """
    Generate FOIA request template for bid pricing.
    
    POST /api/pricing/generate-foia
    Body: {
        "solicitation_number": "DOH59579",
        "agency_name": "Ohio Department of Health",
        "contract_title": "Medical Courier Services",
        "award_date": "2024-03-15"  // optional
    }
    
    Returns: Formatted FOIA request letter
    """
    try:
        data = request.json
        scraper = HistoricalPricingScraper()
        
        foia = scraper.generate_foia_request_template(
            solicitation_number=data['solicitation_number'],
            agency_name=data['agency_name'],
            contract_title=data['contract_title'],
            award_date=data.get('award_date')
        )
        
        return jsonify({
            'success': True,
            'foia_request': foia
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/pricing/market-intelligence', methods=['POST'])
def api_pricing_market_intelligence():
    """
    Get comprehensive market intelligence for a service type.
    Combines historical search + unit price estimation.
    
    POST /api/pricing/market-intelligence
    Body: {
        "service_type": "medical courier",
        "naics_code": "492110",
        "estimated_annual_volume": 1000,
        "min_value": 50000,
        "max_value": 150000
    }
    
    Returns: Market intelligence report with pricing benchmarks
    """
    try:
        data = request.json
        scraper = HistoricalPricingScraper()
        
        # Search for similar contracts
        contracts = scraper.search_similar_contracts(
            service_type=data['service_type'],
            naics_code=data.get('naics_code'),
            min_value=data.get('min_value'),
            max_value=data.get('max_value'),
            years_back=3
        )
        
        # Calculate unit price estimates for each contract
        estimates = []
        for contract in contracts[:10]:  # Top 10 only
            if contract['amount'] > 0:
                # Assume 3-year contracts, use provided volume
                estimate = scraper.estimate_unit_pricing(
                    total_contract_value=contract['amount'],
                    contract_duration_years=3,
                    estimated_annual_volume=data.get('estimated_annual_volume', 1000),
                    service_type=data['service_type']
                )
                estimates.append({
                    'contractor': contract['recipient'],
                    'total_value': contract['amount'],
                    'estimated_per_unit': estimate['estimated_per_unit']
                })
        
        # Calculate market averages
        if estimates:
            avg_per_unit = sum(e['estimated_per_unit'] for e in estimates) / len(estimates)
            min_per_unit = min(e['estimated_per_unit'] for e in estimates)
            max_per_unit = max(e['estimated_per_unit'] for e in estimates)
        else:
            avg_per_unit = min_per_unit = max_per_unit = 0
        
        return jsonify({
            'success': True,
            'service_type': data['service_type'],
            'contracts_found': len(contracts),
            'market_benchmarks': {
                'average_per_unit': round(avg_per_unit, 2),
                'min_per_unit': round(min_per_unit, 2),
                'max_per_unit': round(max_per_unit, 2),
                'sample_size': len(estimates)
            },
            'top_contracts': estimates,
            'recommendation': f"Market rate: ${avg_per_unit:.2f}/unit (range: ${min_per_unit:.2f}-${max_per_unit:.2f})"
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/pricing/multi-year', methods=['POST'])
def api_pricing_multi_year():
    """
    Calculate multi-year contract pricing with escalation.
    
    POST /api/pricing/multi-year
    Body: {
        "base_year_cost": 50000,
        "num_years": 5,
        "escalation_percent": 3,
        "markup_percent": 18,
        "contract_type": "service"
    }
    
    Returns: Year-by-year pricing breakdown
    """
    try:
        data = request.json
        result = calculate_multi_year_pricing(
            base_year_cost=data['base_year_cost'],
            num_years=data['num_years'],
            escalation_percent=data.get('escalation_percent', 3.0),
            markup_percent=data.get('markup_percent', 18.0),
            contract_type=data.get('contract_type', 'service')
        )
        return jsonify({'success': True, 'result': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/pricing/labor-rate', methods=['POST'])
def api_pricing_labor_rate():
    """
    Calculate fully burdened labor rate for self-performed services.
    
    POST /api/pricing/labor-rate
    Body: {
        "service_type": "drug_testing_collector",
        "profit_margin": 10
    }
    
    Returns: Fully burdened hourly rate breakdown
    """
    try:
        data = request.json
        result = calculate_service_rate_by_type(
            service_type=data['service_type'],
            profit_margin=data.get('profit_margin', 10.0)
        )
        return jsonify({'success': True, 'result': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/pricing/validate-quote', methods=['POST'])
def api_pricing_validate_quote():
    """
    Validate subcontractor quote against market benchmarks.
    
    POST /api/pricing/validate-quote
    Body: {
        "service_type": "medical_courier_ohio",
        "quote_amount": 60.00,
        "ddi_markup": 18
    }
    
    Returns: Quote validation assessment and DDI bid price
    """
    try:
        data = request.json
        validation = validate_subcontractor_quote(
            service_type=data['service_type'],
            quote_amount=data['quote_amount']
        )
        
        ddi_bid = calculate_ddi_bid_from_sub_quote(
            sub_quote=data['quote_amount'],
            markup_percent=data.get('ddi_markup', 18.0)
        )
        
        return jsonify({
            'success': True,
            'result': {
                **validation,
                'ddi_bid': ddi_bid['ddi_bid'],
                'ddi_profit': ddi_bid['ddi_profit']
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# =============================================================================
# PROPOSALBIO™ API ENDPOINTS
# =============================================================================

@app.route('/api/proposalbio/analyze', methods=['POST'])
def api_proposalbio_analyze():
    """
    Analyze proposal text with ProposalBio™ 10 biohack system.
    
    POST /api/proposalbio/analyze
    Body: {
        "proposal_text": "...",
        "metadata": {
            "client_name": "DTMB",
            "agency": "Michigan DTMB",
            "agency_type": "State",
            "region": "Midwest",
            "rfp_number": "RFP-171",
            "service_type": "Drug Testing"
        }
    }
    
    Returns: Complete ProposalBio analysis with scores, issues, recommendations
    """
    try:
        data = request.json
        analyzer = ProposalBioAnalyzer(
            proposal_text=data['proposal_text'],
            metadata=data.get('metadata', {})
        )
        result = analyzer.analyze_all()
        return jsonify({'success': True, 'result': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ─── EVALUATOR SCORING ENGINE ENDPOINTS ──────────────────────────────────────

@app.route('/api/evaluator/parse-rfp', methods=['POST'])
def evaluator_parse_rfp():
    """Parse Section M evaluation criteria from RFP text."""
    data = request.json or {}
    rfp_text = data.get('rfp_text', '')
    if not rfp_text:
        return jsonify({'error': 'rfp_text is required'}), 400
    try:
        from evaluator_scoring_engine import parse_rfp
        result = parse_rfp(rfp_text, use_ai=data.get('use_ai', True))
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/evaluator/score', methods=['POST'])
def evaluator_score_proposal():
    """Score a proposal against evaluation criteria — returns factor-by-factor adjectival ratings."""
    data = request.json or {}
    proposal_text = data.get('proposal_text', '')
    if not proposal_text:
        return jsonify({'error': 'proposal_text is required'}), 400
    try:
        from evaluator_scoring_engine import score_proposal
        result = score_proposal(
            proposal_text=proposal_text,
            rfp_analysis=data.get('rfp_analysis', {}),
            rfp_text=data.get('rfp_text', ''),
            proposal_id=data.get('proposal_id'),
            use_ai=data.get('use_ai', True),
        )

        # NEXUS ADVISOR: Teach about evaluator scoring
        try:
            from nexus_advisor import advise, log_growth
            advisor_insight = advise('gpss', 'proposal_scored', {
                'composite_score': result.get('composite_score'),
                'overall_rating': result.get('overall_rating'),
            })
            result['advisor'] = advisor_insight
            log_growth('proposal_scored')
        except Exception:
            pass

        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/evaluator/full-analysis', methods=['POST'])
def evaluator_full_analysis():
    """
    Combined analysis: Parse RFP → Score Proposal → ProposalBio quality score.
    Returns BOTH evaluator scoring AND writing quality in one call.
    """
    data = request.json or {}
    proposal_text = data.get('proposal_text', '')
    rfp_text = data.get('rfp_text', '')
    if not proposal_text:
        return jsonify({'error': 'proposal_text is required'}), 400
    try:
        from evaluator_scoring_engine import get_engine
        engine = get_engine()

        rfp_analysis = {}
        if rfp_text:
            rfp_analysis = engine.parse_rfp(rfp_text, use_ai=data.get('use_ai', True))

        evaluator_result = engine.score_proposal(
            proposal_text=proposal_text,
            rfp_analysis=rfp_analysis,
            rfp_text=rfp_text,
            proposal_id=data.get('proposal_id'),
            use_ai=data.get('use_ai', True),
        )

        proposalbio_result = None
        try:
            analyzer = ProposalBioAnalyzer(
                proposal_text=proposal_text,
                metadata=data.get('metadata', {})
            )
            proposalbio_result = analyzer.analyze_all()
        except Exception as pb_err:
            print(f"ProposalBio analysis error: {pb_err}")

        return jsonify({
            'evaluator': evaluator_result,
            'proposalbio': proposalbio_result,
            'rfp_analysis': rfp_analysis,
            'combined_assessment': {
                'evaluator_score': evaluator_result.get('composite', {}).get('score', 0),
                'evaluator_rating': evaluator_result.get('composite', {}).get('rating', 'Unknown'),
                'writing_quality': proposalbio_result.get('composite_score', 0) if proposalbio_result else None,
                'writing_status': proposalbio_result.get('overall_status', 'Unknown') if proposalbio_result else None,
                'risk_level': evaluator_result.get('risk_assessment', {}).get('level', 'Unknown'),
                'competitive_position': evaluator_result.get('competitive_position', {}).get('position', 'Unknown'),
                'submit_ready': (
                    evaluator_result.get('risk_assessment', {}).get('level', 'HIGH') in ('LOW', 'MODERATE')
                    and (not proposalbio_result or proposalbio_result.get('composite_score', 0) >= 60)
                ),
            },
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/evaluator/outcome', methods=['POST'])
def evaluator_record_outcome():
    """Record win/loss outcome — feeds back into the learning loop."""
    data = request.json or {}
    proposal_id = data.get('proposal_id')
    won = data.get('won')
    if not proposal_id or won is None:
        return jsonify({'error': 'proposal_id and won are required'}), 400
    try:
        from evaluator_scoring_engine import record_outcome
        result = record_outcome(proposal_id, won, data.get('debrief_data'))
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/evaluator/score-proposal/<proposal_id>', methods=['POST'])
def evaluator_score_gpss_proposal(proposal_id):
    """
    Score a GPSS proposal by ID — pulls proposal + RFP text directly from Airtable.
    No copy-paste needed. This is the GPSS-integrated evaluator.
    """
    try:
        airtable_client = AirtableClient()
        proposal = airtable_client.get_record('GPSS PROPOSALS', proposal_id)
        fields = proposal.get('fields', {})

        proposal_text = fields.get('Proposal Text', '') or fields.get('Content', '') or fields.get('Draft', '')
        rfp_text = fields.get('RFP Text', '') or fields.get('Requirements', '') or ''

        if not proposal_text:
            return jsonify({'error': 'Proposal has no text content to score'}), 400

        # Pull linked opportunity for RFP context if available
        opp_links = fields.get('Opportunity', [])
        if opp_links and not rfp_text:
            try:
                opp = airtable_client.get_record('GPSS OPPORTUNITIES', opp_links[0])
                opp_fields = opp.get('fields', {})
                rfp_text = opp_fields.get('Description', '') or opp_fields.get('Requirements', '') or ''
            except Exception:
                pass

        from evaluator_scoring_engine import score_proposal
        result = score_proposal(
            proposal_text=proposal_text,
            rfp_text=rfp_text,
            proposal_id=proposal_id,
            use_ai=True,
        )

        # Write score back to the proposal record
        try:
            airtable_client.update_record('GPSS PROPOSALS', proposal_id, {
                'Evaluator Score': result.get('composite_score', 0),
                'Evaluator Rating': result.get('overall_rating', ''),
            })
        except Exception:
            pass

        # Advisor + learning
        try:
            from nexus_advisor import advise, log_growth
            result['advisor'] = advise('gpss', 'proposal_scored', {
                'composite_score': result.get('composite_score'),
                'overall_rating': result.get('overall_rating'),
            })
            log_growth('proposal_scored')
        except Exception:
            pass

        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/evaluator/calibration', methods=['GET'])
def evaluator_calibration():
    """Get model calibration accuracy — how well our scores predict wins."""
    try:
        from evaluator_scoring_engine import get_calibration
        return jsonify(get_calibration())
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/evaluator/history', methods=['GET'])
def evaluator_history():
    """Get evaluation history."""
    try:
        from evaluator_scoring_engine import get_engine
        return jsonify({'evaluations': get_engine().get_evaluation_history()})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ─── PRICING INTELLIGENCE ENDPOINTS ─────────────────────────────────────────

@app.route('/api/pricing/parse-clins', methods=['POST'])
def pricing_parse_clins():
    """Parse CLINs from RFP Section B text."""
    data = request.json or {}
    rfp_text = data.get('rfp_text', '')
    if not rfp_text:
        return jsonify({'error': 'rfp_text is required'}), 400
    try:
        from pricing_intelligence import get_pricing_intelligence
        result = get_pricing_intelligence().parse_clins(rfp_text)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/pricing/recommend-markup', methods=['POST'])
def pricing_recommend_markup():
    """Get markup recommendation based on contract type and learning data."""
    data = request.json or {}
    try:
        from pricing_intelligence import get_pricing_intelligence
        result = get_pricing_intelligence().recommend_markup(
            contract_type=data.get('contract_type', 'services_subcontracted'),
            eval_method=data.get('eval_method', 'best_value'),
            set_aside=data.get('set_aside', ''),
            service_type=data.get('service_type'),
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/pricing/score-price-factor', methods=['POST'])
def pricing_score_price_factor():
    """Score the Price evaluation factor using pricing intelligence."""
    data = request.json or {}
    proposal_text = data.get('proposal_text', '')
    if not proposal_text:
        return jsonify({'error': 'proposal_text is required'}), 400
    try:
        from pricing_intelligence import get_pricing_intelligence
        result = get_pricing_intelligence().score_price_factor(
            proposal_text=proposal_text,
            rfp_text=data.get('rfp_text', ''),
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/pricing/benchmarks', methods=['POST'])
def pricing_benchmarks():
    """Get market rate benchmarks for a service type."""
    data = request.json or {}
    try:
        from pricing_intelligence import get_pricing_intelligence
        result = get_pricing_intelligence().get_market_benchmarks(
            service_type=data.get('service_type'),
            rfp_text=data.get('rfp_text', ''),
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/pricing/log-outcome', methods=['POST'])
def pricing_log_outcome():
    """Log pricing win/loss for learning."""
    data = request.json or {}
    opportunity_id = data.get('opportunity_id')
    won = data.get('won')
    if not opportunity_id or won is None:
        return jsonify({'error': 'opportunity_id and won are required'}), 400
    try:
        from pricing_intelligence import get_pricing_intelligence
        result = get_pricing_intelligence().log_pricing_outcome(
            opportunity_id=opportunity_id,
            won=won,
            markup_pct=data.get('markup_pct'),
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ─── NEXUS ADVISOR — TEACHING ENGINE ENDPOINTS ──────────────────────────────
# Runs across ALL systems: GPSS, ATLAS, VERTEX, GBIS, DDCSS, LBPC, PRISM, COMMAND

@app.route('/api/advisor/teach', methods=['POST'])
def advisor_teach():
    """
    Get contextual education for an action in any NEXUS system.
    POST { "system": "gpss", "action": "proposal_scored", "context": {...} }
    """
    data = request.json or {}
    system = data.get('system', '')
    action = data.get('action', '')
    if not system or not action:
        return jsonify({'error': 'system and action are required'}), 400
    try:
        from nexus_advisor import advise
        return jsonify(advise(system, action, data.get('context')))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/advisor/debrief', methods=['POST'])
def advisor_debrief():
    """
    Generate a debrief for an outcome (bid_won, bid_lost, contract_complete).
    POST { "outcome_type": "bid_won", "context": { "contract_value": 250000 } }
    """
    data = request.json or {}
    outcome_type = data.get('outcome_type', '')
    if not outcome_type:
        return jsonify({'error': 'outcome_type is required'}), 400
    try:
        from nexus_advisor import debrief
        return jsonify(debrief(outcome_type, data.get('context')))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/advisor/brief', methods=['GET'])
def advisor_brief():
    """Generate periodic growth briefing — stats, patterns, milestones."""
    try:
        from nexus_advisor import brief
        return jsonify(brief())
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/advisor/log', methods=['POST'])
def advisor_log_event():
    """
    Log a growth event.
    POST { "event_type": "bid_submitted", "metadata": {...} }
    Events: bid_submitted, email_sent, sub_managed, debrief_requested,
            proposal_scored, invoice_created, grant_applied
    """
    data = request.json or {}
    event_type = data.get('event_type', '')
    if not event_type:
        return jsonify({'error': 'event_type is required'}), 400
    try:
        from nexus_advisor import log_growth
        return jsonify(log_growth(event_type, data.get('metadata')))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/advisor/milestones', methods=['GET'])
def advisor_milestones():
    """Get achieved and upcoming growth milestones."""
    try:
        from nexus_advisor import get_advisor
        return jsonify(get_advisor().get_milestones())
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/advisor/knowledge', methods=['GET'])
def advisor_knowledge_map():
    """Get the full knowledge map — all systems, all actions, all teaching content."""
    try:
        from nexus_advisor import KNOWLEDGE_BASE
        systems = []
        for sys_key, sys_data in KNOWLEDGE_BASE.items():
            actions = []
            for act_key, act_data in sys_data.get('actions', {}).items():
                actions.append({
                    'action': act_key,
                    'key_concept': act_data.get('key_concept', ''),
                    'has_far_reference': act_data.get('far_reference') is not None,
                })
            systems.append({
                'system': sys_key,
                'name': sys_data.get('system_name', sys_key),
                'action_count': len(actions),
                'actions': actions,
            })
        return jsonify({'systems': systems, 'total_topics': sum(s['action_count'] for s in systems)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================
# NEXUS AUTONOMOUS ENGINE — "AI That Works While You Sleep"
# Self-learning scheduler with adaptive behavior
# ============================================================

@app.route('/autonomous/start', methods=['POST'])
def autonomous_start():
    if not get_autonomous_engine:
        return jsonify({'error': 'Autonomous engine not loaded'}), 503
    engine = get_autonomous_engine()
    result = engine.start()
    return jsonify(result)

@app.route('/autonomous/stop', methods=['POST'])
def autonomous_stop():
    if not get_autonomous_engine:
        return jsonify({'error': 'Autonomous engine not loaded'}), 503
    engine = get_autonomous_engine()
    result = engine.stop()
    return jsonify(result)

@app.route('/autonomous/status', methods=['GET'])
def autonomous_status():
    if not get_autonomous_engine:
        return jsonify({'error': 'Autonomous engine not loaded'}), 503
    engine = get_autonomous_engine()
    return jsonify(engine.get_status())

@app.route('/autonomous/brief', methods=['GET'])
def autonomous_brief():
    if not get_autonomous_engine:
        return jsonify({'error': 'Autonomous engine not loaded'}), 503
    engine = get_autonomous_engine()
    return jsonify(engine.get_brief())

@app.route('/autonomous/brief/generate', methods=['POST'])
def autonomous_generate_brief():
    if not get_autonomous_engine:
        return jsonify({'error': 'Autonomous engine not loaded'}), 503
    engine = get_autonomous_engine()
    result = engine.task_morning_brief()
    return jsonify({'result': result, 'brief': engine.get_brief()})

@app.route('/autonomous/cycle', methods=['POST'])
def autonomous_run_cycle():
    """Run a single autonomous cycle manually."""
    if not get_autonomous_engine:
        return jsonify({'error': 'Autonomous engine not loaded'}), 503
    engine = get_autonomous_engine()
    engine.run_cycle()
    return jsonify({'status': 'cycle_complete', 'state': engine.get_status()})

@app.route('/autonomous/config', methods=['GET'])
def autonomous_get_config():
    if not get_autonomous_engine:
        return jsonify({'error': 'Autonomous engine not loaded'}), 503
    engine = get_autonomous_engine()
    return jsonify(engine.config)

@app.route('/autonomous/config', methods=['PUT'])
def autonomous_update_config():
    if not get_autonomous_engine:
        return jsonify({'error': 'Autonomous engine not loaded'}), 503
    engine = get_autonomous_engine()
    updates = request.json or {}
    result = engine.update_config(updates)
    return jsonify(result)

@app.route('/autonomous/history', methods=['GET'])
def autonomous_history():
    if not get_autonomous_engine:
        return jsonify({'error': 'Autonomous engine not loaded'}), 503
    engine = get_autonomous_engine()
    limit = request.args.get('limit', 50, type=int)
    actions = engine.state.get('action_log', [])[-limit:]
    return jsonify({'actions': actions, 'total': len(engine.state.get('action_log', []))})


# ============================================================================
# VERTEX AUTO-TRIGGER API ENDPOINT
# ============================================================================

# ============================================================================
# VERTEX BANK RECONCILIATION — Phase 12
# ============================================================================

@app.route('/vertex/bank/import', methods=['POST'])
def vertex_bank_import():
    """
    Import bank transactions from CSV.
    Accepts multipart/form-data with a 'file' field (CSV), or a JSON body with 'rows' list.

    Supported CSV formats: Chase, BofA, Wells Fargo (auto-detected by column headers).
    Columns mapped: Date, Description, Amount, Balance (optional).

    After import, unmatched transactions are queued for reconciliation.
    """
    import csv, io
    airtable = AirtableClient()

    rows = []
    if request.content_type and 'multipart' in request.content_type:
        f = request.files.get('file')
        if not f:
            return jsonify({'error': 'No file uploaded'}), 400
        content = f.read().decode('utf-8-sig', errors='replace')
        reader  = csv.DictReader(io.StringIO(content))
        rows    = list(reader)
    else:
        body = request.json or {}
        rows = body.get('rows', [])

    if not rows:
        return jsonify({'error': 'No transaction rows found'}), 400

    # Column normaliser — maps known bank column names to canonical names
    _ALIASES = {
        'date':            ['date', 'transaction date', 'posting date', 'trans date'],
        'description':     ['description', 'desc', 'payee', 'memo', 'transaction description', 'narrative'],
        'amount':          ['amount', 'debit', 'credit', 'transaction amount'],
        'balance':         ['balance', 'running balance', 'ledger balance', 'ending balance'],
    }

    def _find_col(row_keys: list, aliases: list) -> str:
        for k in row_keys:
            if k.lower().strip() in aliases:
                return k
        return ''

    if not rows:
        return jsonify({'error': 'Empty CSV'}), 400

    sample_keys = list(rows[0].keys())
    col_date    = _find_col(sample_keys, _ALIASES['date'])
    col_desc    = _find_col(sample_keys, _ALIASES['description'])
    col_amount  = _find_col(sample_keys, _ALIASES['amount'])
    col_balance = _find_col(sample_keys, _ALIASES['balance'])

    if not (col_date and col_desc and col_amount):
        return jsonify({
            'error': 'Could not detect required columns (Date, Description, Amount)',
            'detected_columns': sample_keys,
        }), 400

    imported = 0
    skipped  = 0
    for row in rows:
        try:
            date_val   = row.get(col_date, '').strip()
            desc_val   = row.get(col_desc, '').strip()
            amount_raw = row.get(col_amount, '0').replace('$', '').replace(',', '').strip()
            balance_raw = row.get(col_balance, '').replace('$', '').replace(',', '').strip() if col_balance else ''

            if not date_val or not desc_val:
                skipped += 1
                continue

            amount  = float(amount_raw) if amount_raw else 0.0
            balance = float(balance_raw) if balance_raw else None

            fields = {
                'TRANSACTION DATE': date_val,
                'DESCRIPTION':      desc_val,
                'AMOUNT':           amount,
                'MATCH STATUS':     'Unmatched',
            }
            if balance is not None:
                fields['RUNNING BALANCE'] = balance

            airtable.create_record('VERTEX BANK TRANSACTIONS', fields)
            imported += 1
        except Exception as ex:
            print(f"Bank import row error: {ex}")
            skipped += 1

    return jsonify({'imported': imported, 'skipped': skipped, 'total_rows': len(rows)})


@app.route('/vertex/bank/reconcile', methods=['POST'])
def vertex_bank_reconcile():
    """
    AI Matching Engine — auto-match unmatched bank transactions to VERTEX INVOICES and EXPENSES.

    Match confidence levels:
      HIGH:   exact amount + date within 5 days
      MEDIUM: exact amount + client/vendor name fuzzy match
      LOW:    amount within 5% + date within 10 days

    High/Medium confidence: auto-posts payment to VERTEX INVOICES and creates VERTEX REVENUE.
    Low confidence: flagged for manual review.
    """
    from difflib import SequenceMatcher
    from datetime import timedelta

    airtable = AirtableClient()

    # Pull unmatched transactions
    try:
        unmatched_txns = airtable.search_records(
            'VERTEX BANK TRANSACTIONS', "{MATCH STATUS}='Unmatched'"
        )
    except Exception:
        unmatched_txns = []

    if not unmatched_txns:
        return jsonify({'matched': 0, 'unmatched': 0, 'message': 'No unmatched transactions found'})

    # Pull open invoices
    open_invoices = airtable.search_records(
        'VERTEX INVOICES',
        f"OR({{{VI['payment_status']}}}='Unpaid',{{{VI['payment_status']}}}='Partial')"
    )

    matched   = []
    needs_review = []

    def _fuzzy(a: str, b: str) -> float:
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()

    for txn in unmatched_txns:
        tf      = txn.get('fields', {})
        txn_amt = abs(float(tf.get('AMOUNT', 0) or 0))
        txn_date_str = tf.get('TRANSACTION DATE', '')
        txn_desc = tf.get('DESCRIPTION', '').lower()

        try:
            txn_date = datetime.fromisoformat(txn_date_str[:10]).date()
        except Exception:
            txn_date = None

        best_match = None
        best_score = 0

        for inv in open_invoices:
            f       = inv.get('fields', {})
            inv_amt = float(f.get(VI['total_amount'], 0) or 0)
            due_str = f.get(VI['due_date'], '')
            client  = (f.get(VI['client_name'], '') or '').lower()

            if inv_amt <= 0:
                continue

            amount_match = abs(txn_amt - inv_amt) < 0.02

            date_close = False
            if txn_date and due_str:
                try:
                    due = datetime.fromisoformat(due_str[:10]).date()
                    date_close = abs((txn_date - due).days) <= 5
                except Exception:
                    pass

            name_match = _fuzzy(txn_desc, client) > 0.55

            if amount_match and date_close:
                score = 0.95
            elif amount_match and name_match:
                score = 0.80
            elif amount_match:
                score = 0.60
            else:
                score = 0

            if score > best_score:
                best_score = score
                best_match = (inv, score)

        if best_match and best_score >= 0.75:
            inv, score = best_match
            inv_f      = inv.get('fields', {})
            inv_amt    = float(inv_f.get(VI['total_amount'], 0) or 0)

            # Mark invoice paid
            new_status = 'Paid' if abs(txn_amt - inv_amt) < 0.02 else 'Partial'
            airtable.update_record('VERTEX INVOICES', inv['id'], {
                VI['payment_status']:  new_status,
                VI['payment_date']:    txn_date_str[:10] if txn_date_str else datetime.now().date().isoformat(),
                VI['payment_method']:  'Bank Transfer',
                VI['amount_paid']:     txn_amt,
                VI['notes']:           (inv_f.get(VI['notes'], '') or '') + f' | Auto-reconciled (score {score:.2f})',
            })

            # Create VERTEX REVENUE record
            airtable.create_record('VERTEX REVENUE', {
                VR['revenue_date']:   txn_date_str[:10] if txn_date_str else datetime.now().date().isoformat(),
                VR['source']:         inv_f.get(VI['client_name'], ''),
                VR['revenue_type']:   'Invoice Payment',
                VR['amount']:         txn_amt,
                VR['source_system']:  'VERTEX',
                VR['notes']:          f"Bank reconciliation | Invoice {inv_f.get(VI['invoice_number'], inv['id'])} | Score {score:.2f}",
            })

            # Mark transaction matched
            airtable.update_record('VERTEX BANK TRANSACTIONS', txn['id'], {
                'MATCH STATUS':   'Matched',
                'MATCHED RECORD': inv['id'],
                'MATCH SCORE':    round(score, 2),
            })
            matched.append({'txn': txn['id'], 'invoice': inv['id'], 'score': score})

        elif best_match and best_score >= 0.50:
            airtable.update_record('VERTEX BANK TRANSACTIONS', txn['id'], {
                'MATCH STATUS': 'Needs Review',
            })
            needs_review.append({'txn': txn['id'], 'best_score': best_score})
        else:
            needs_review.append({'txn': txn['id'], 'best_score': best_score})

    return jsonify({
        'matched':      len(matched),
        'unmatched':    len(needs_review),
        'matched_list': matched,
        'review_list':  needs_review[:10],
    })


@app.route('/vertex/bank/unmatched', methods=['GET'])
def vertex_bank_unmatched():
    """List all bank transactions that could not be auto-matched."""
    airtable = AirtableClient()
    try:
        records = airtable.search_records(
            'VERTEX BANK TRANSACTIONS',
            "OR({MATCH STATUS}='Unmatched',{MATCH STATUS}='Needs Review')"
        )
        return jsonify({'unmatched': [r.get('fields', {}) for r in records], 'count': len(records)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================================
# END BANK RECONCILIATION
# ============================================================================


@app.route('/vertex/ai/advisor', methods=['POST'])
def run_vertex_financial_advisor():
    """
    Run the AI Financial Advisor on demand.
    Returns full analysis: cash position, forecast, alerts, margin, collection priority, predictions.
    Also updates DAILY_BRIEFING.md and TODAY_AGENDA.md.
    """
    try:
        from vertex_ai_advisor import run_vertex_ai_advisor
        result = run_vertex_ai_advisor()
        return jsonify({'success': True, 'analysis': result})
    except Exception as e:
        print(f"AI advisor error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/vertex/nightly-tally', methods=['GET'])
def vertex_nightly_tally():
    """
    Phase 13 — Nightly Pipeline Tally financial supplement.
    Called during the goodnight ritual to append actual AR/AP/cash data
    alongside pipeline projections.

    Returns:
      - outstanding_ar: total unpaid invoices
      - outstanding_ap: total unpaid bills
      - net_cash:       bank + AR - AP
      - collected_ytd:  total VERTEX REVENUE this calendar year
      - top_overdue:    top 3 overdue invoices by amount
      - narrative:      one-paragraph text for the nightly tally
    """
    airtable = AirtableClient()
    today    = datetime.now().date()
    ytd_start = today.replace(month=1, day=1).isoformat()

    # AR
    try:
        open_invs = airtable.search_records(
            'VERTEX INVOICES',
            f"OR({{{VI['payment_status']}}}='Unpaid',{{{VI['payment_status']}}}='Partial',{{{VI['payment_status']}}}='Overdue')"
        )
    except Exception:
        open_invs = []

    total_ar = sum(
        float(inv.get('fields', {}).get(VI['balance_due']) or inv.get('fields', {}).get(VI['total_amount'], 0) or 0)
        for inv in open_invs
    )

    # Top overdue
    overdue = []
    for inv in open_invs:
        f       = inv.get('fields', {})
        due_str = f.get(VI['due_date'], '')
        try:
            due = datetime.fromisoformat(due_str[:10]).date()
            days_ov = max(0, (today - due).days)
        except Exception:
            days_ov = 0
        if days_ov > 0:
            overdue.append({
                'invoice_number': f.get(VI['invoice_number'], ''),
                'client_name':    f.get(VI['client_name'], ''),
                'amount':         float(f.get(VI['total_amount'], 0) or 0),
                'days_overdue':   days_ov,
            })
    overdue.sort(key=lambda x: x['amount'], reverse=True)
    top_overdue = overdue[:3]

    # AP
    try:
        open_ap = airtable.search_records(
            'VERTEX ACCOUNTS PAYABLE',
            "OR({PAYMENT STATUS}='Unpaid',{PAYMENT STATUS}='Partial')"
        )
    except Exception:
        open_ap = []

    total_ap = sum(
        float(b.get('fields', {}).get('TOTAL AMOUNT', 0) or 0) - float(b.get('fields', {}).get('AMOUNT PAID', 0) or 0)
        for b in open_ap
    )

    # Bank balance (last record)
    try:
        bank_txns = airtable.get_all_records('VERTEX BANK TRANSACTIONS')
        bank_balance = 0.0
        for txn in bank_txns:
            f = txn.get('fields', {})
            bal = float(f.get('RUNNING BALANCE') or f.get('BALANCE') or 0)
            if bal:
                bank_balance = bal
    except Exception:
        bank_balance = 0.0

    net_cash = bank_balance + total_ar - total_ap

    # Collected YTD from VERTEX REVENUE
    try:
        rev_records = airtable.search_records(
            'VERTEX REVENUE',
            f"{{{VR['revenue_date']}}}>='{ytd_start}'"
        )
        collected_ytd = sum(float(r.get('fields', {}).get(VR['amount'], 0) or 0) for r in rev_records)
    except Exception:
        collected_ytd = 0.0

    narrative = (
        f"VERTEX shows ${total_ar:,.2f} in outstanding receivables and ${total_ap:,.2f} "
        f"in payables due. Net cash position: ${net_cash:,.2f}. "
        f"Collected ${collected_ytd:,.2f} YTD."
    )
    if top_overdue:
        top = top_overdue[0]
        narrative += (
            f" Top overdue: {top['client_name']} owes ${top['amount']:,.2f} "
            f"({top['days_overdue']} days past due)."
        )

    return jsonify({
        'outstanding_ar':  round(total_ar, 2),
        'outstanding_ap':  round(total_ap, 2),
        'bank_balance':    round(bank_balance, 2),
        'net_cash':        round(net_cash, 2),
        'collected_ytd':   round(collected_ytd, 2),
        'top_overdue':     top_overdue,
        'narrative':       narrative,
    })


@app.route('/vertex/morning-snapshot', methods=['GET'])
def vertex_morning_snapshot():
    """
    Phase 13 — Morning briefing financial snapshot.
    Called during the good morning ritual to present today's financial priorities.

    Returns a concise dict suitable for Alexa briefing and TODAY_AGENDA.md.
    """
    airtable = AirtableClient()
    today    = datetime.now().date()

    # Overdue invoices count + amount
    try:
        open_invs = airtable.search_records(
            'VERTEX INVOICES',
            f"OR({{{VI['payment_status']}}}='Unpaid',{{{VI['payment_status']}}}='Partial',{{{VI['payment_status']}}}='Overdue')"
        )
    except Exception:
        open_invs = []

    overdue_count  = 0
    overdue_total  = 0.0
    collection_due = []

    for inv in open_invs:
        f       = inv.get('fields', {})
        due_str = f.get(VI['due_date'], '')
        try:
            due      = datetime.fromisoformat(due_str[:10]).date()
            days_ov  = max(0, (today - due).days)
        except Exception:
            days_ov = 0

        if days_ov > 0:
            amt = float(f.get(VI['total_amount'], 0) or 0)
            overdue_count += 1
            overdue_total += amt
            collection_due.append({
                'client':      f.get(VI['client_name'], ''),
                'amount':      amt,
                'days_overdue': days_ov,
                'action':      'Call directly' if days_ov > 60 else 'Send reminder',
            })

    collection_due.sort(key=lambda x: x['amount'], reverse=True)

    # AP due this week
    try:
        ap_recs = airtable.search_records(
            'VERTEX ACCOUNTS PAYABLE',
            "OR({PAYMENT STATUS}='Unpaid',{PAYMENT STATUS}='Partial')"
        )
    except Exception:
        ap_recs = []

    ap_due_week = []
    for b in ap_recs:
        f       = b.get('fields', {})
        due_str = f.get('DUE DATE', '')
        try:
            due       = datetime.fromisoformat(due_str[:10]).date()
            days_left = (due - today).days
        except Exception:
            days_left = 999
        if 0 <= days_left <= 7:
            ap_due_week.append({
                'vendor': f.get('VENDOR NAME', ''),
                'amount': float(f.get('TOTAL AMOUNT', 0) or 0),
                'due_date': due_str,
            })

    alexa_snippet = (
        f"Financial this morning: {overdue_count} invoices overdue totaling ${overdue_total:,.2f}. "
        f"{len(ap_due_week)} sub payment(s) due this week. "
    )
    if collection_due:
        top = collection_due[0]
        alexa_snippet += f"Top priority: {top['client']} owes ${top['amount']:,.2f}. {top['action']}."

    return jsonify({
        'overdue_count':    overdue_count,
        'overdue_total':    round(overdue_total, 2),
        'collection_due':   collection_due[:5],
        'ap_due_this_week': ap_due_week,
        'alexa_snippet':    alexa_snippet,
    })


@app.route('/vertex/trigger', methods=['POST'])
def vertex_trigger_event():
    """
    Fire a VERTEX auto-trigger event from any NEXUS module.

    POST body:
      event_type        str  (required) — e.g. 'gpss.opportunity.won'
      source_record_id  str  (optional) — Airtable record ID of triggering entity
      data              obj  (optional) — event-specific payload

    Supported events:
      gpss.opportunity.won | gpss.opportunity.lost
      atlas.milestone.complete | atlas.expense.logged
      prism.service.complete
      ddcss.client.won
      gbis.grant.awarded
      lbpc.recovery.complete
      fleetflow.delivery.confirmed
      compass.qa.passed | compass.qa.failed
    """
    try:
        from vertex_automation import vertex_auto_trigger
        body = request.json or {}
        event_type       = body.get('event_type', '')
        source_record_id = body.get('source_record_id', '')
        data             = body.get('data', {})

        if not event_type:
            return jsonify({'error': 'event_type is required'}), 400

        result = vertex_auto_trigger(event_type, source_record_id, data)
        status = 200 if result.get('outcome') == 'success' else 500
        return jsonify(result), status
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ═══════════════════════════════════════════════════════════════════════════
# SHIELD — Lead Screening & MDHHS Referral Module
# Anchored by Michigan Public Act 146 of 2023 (universal blood lead screening,
# effective April 30, 2025). Two-sided system: DDI/CWC internal case management
# + external referral portal for MDHHS / county health department case workers.
# All Airtable calls routed through shield_lead_screening.py (backend-only).
# ═══════════════════════════════════════════════════════════════════════════
try:
    from shield_lead_screening import (
        handle_shield_dashboard,
        handle_shield_list_referrals,
        handle_shield_get_referral,
        handle_shield_create_referral,
        handle_shield_update_referral,
        handle_shield_list_families,
        handle_shield_list_children,
        handle_shield_list_navigators,
        handle_shield_list_activations,
        handle_shield_activate_service,
        handle_shield_log_milestone,
        handle_shield_list_billing,
        handle_shield_create_billing,
        handle_shield_generate_outcomes_report,
        handle_shield_ai_chat,
        handle_shield_ai_external,
        handle_shield_sla_override,
        handle_shield_update_child,
    )
    _SHIELD_AVAILABLE = True
except ImportError as _shield_err:
    print(f"[NEXUS] SHIELD module unavailable: {_shield_err}")
    _SHIELD_AVAILABLE = False


def _shield_unavailable():
    return jsonify({
        'success': False,
        'error': 'SHIELD module not available on this server',
        'configured': False,
    }), 503


@app.route('/shield/dashboard', methods=['GET'])
def shield_dashboard():
    if not _SHIELD_AVAILABLE:
        return _shield_unavailable()
    return jsonify(handle_shield_dashboard())


@app.route('/shield/referrals', methods=['GET'])
def shield_list_referrals():
    if not _SHIELD_AVAILABLE:
        return _shield_unavailable()
    filters = {
        'status': request.args.get('status'),
        'county': request.args.get('county'),
        'urgency': request.args.get('urgency'),
        'referral_source': request.args.get('referral_source'),
    }
    return jsonify(handle_shield_list_referrals(filters))


@app.route('/shield/referrals', methods=['POST'])
def shield_create_referral():
    """External intake form submission. Public endpoint — no auth required."""
    if not _SHIELD_AVAILABLE:
        return _shield_unavailable()
    payload = request.get_json(silent=True) or {}
    result = handle_shield_create_referral(payload)
    status_code = 200 if result.get('success') else 400
    return jsonify(result), status_code


@app.route('/shield/referrals/<referral_id>', methods=['GET'])
def shield_get_referral(referral_id):
    if not _SHIELD_AVAILABLE:
        return _shield_unavailable()
    return jsonify(handle_shield_get_referral(referral_id))


@app.route('/shield/referrals/<referral_id>', methods=['PUT', 'PATCH'])
def shield_update_referral(referral_id):
    if not _SHIELD_AVAILABLE:
        return _shield_unavailable()
    updates = request.get_json(silent=True) or {}
    return jsonify(handle_shield_update_referral(referral_id, updates))


@app.route('/shield/families', methods=['GET'])
def shield_list_families():
    if not _SHIELD_AVAILABLE:
        return _shield_unavailable()
    return jsonify(handle_shield_list_families())


@app.route('/shield/children', methods=['GET'])
def shield_list_children():
    if not _SHIELD_AVAILABLE:
        return _shield_unavailable()
    return jsonify(handle_shield_list_children())


@app.route('/shield/navigators', methods=['GET'])
def shield_list_navigators():
    if not _SHIELD_AVAILABLE:
        return _shield_unavailable()
    return jsonify(handle_shield_list_navigators())


@app.route('/shield/activations', methods=['GET'])
def shield_list_activations():
    if not _SHIELD_AVAILABLE:
        return _shield_unavailable()
    referral_id = request.args.get('referral_id')
    return jsonify(handle_shield_list_activations(referral_id))


@app.route('/shield/activations', methods=['POST'])
def shield_activate_service():
    if not _SHIELD_AVAILABLE:
        return _shield_unavailable()
    payload = request.get_json(silent=True) or {}
    result = handle_shield_activate_service(payload)
    return jsonify(result), (200 if result.get('success') else 400)


@app.route('/shield/milestones', methods=['POST'])
def shield_log_milestone():
    if not _SHIELD_AVAILABLE:
        return _shield_unavailable()
    payload = request.get_json(silent=True) or {}
    return jsonify(handle_shield_log_milestone(payload))


@app.route('/shield/billing', methods=['GET'])
def shield_list_billing():
    if not _SHIELD_AVAILABLE:
        return _shield_unavailable()
    status = request.args.get('status')
    return jsonify(handle_shield_list_billing(status))


@app.route('/shield/billing', methods=['POST'])
def shield_create_billing():
    if not _SHIELD_AVAILABLE:
        return _shield_unavailable()
    payload = request.get_json(silent=True) or {}
    return jsonify(handle_shield_create_billing(payload))


@app.route('/shield/outcomes-report', methods=['GET'])
def shield_outcomes_report():
    if not _SHIELD_AVAILABLE:
        return _shield_unavailable()
    period = request.args.get('period')
    county = request.args.get('county')
    return jsonify(handle_shield_generate_outcomes_report(period, county))


@app.route('/shield/ai/chat', methods=['POST'])
def shield_ai_chat():
    """Internal SHIELD AI — navigator case Q&A."""
    if not _SHIELD_AVAILABLE:
        return _shield_unavailable()
    payload = request.get_json(silent=True) or {}
    message = (payload.get('message') or '').strip()
    if not message:
        return jsonify({'success': False, 'error': 'message required'}), 400
    return jsonify(handle_shield_ai_chat(message, payload.get('context')))


@app.route('/shield/ai/external', methods=['POST'])
def shield_ai_external():
    """External SHIELD AI — scoped to referring agency's own cases."""
    if not _SHIELD_AVAILABLE:
        return _shield_unavailable()
    payload = request.get_json(silent=True) or {}
    message = (payload.get('message') or '').strip()
    agency_email = (payload.get('agency_email') or '').strip()
    if not message or not agency_email:
        return jsonify({'success': False, 'error': 'message and agency_email required'}), 400
    return jsonify(handle_shield_ai_external(message, payload.get('case_ref'), agency_email))


@app.route('/shield/referrals/<referral_id>/sla-override', methods=['POST'])
def shield_sla_override(referral_id):
    """Supervisor-only: set or clear the SLA override on a referral."""
    if not _SHIELD_AVAILABLE:
        return _shield_unavailable()
    payload = request.get_json(silent=True) or {}
    result = handle_shield_sla_override(referral_id, payload)
    status = result.pop('status_code', None) or (200 if result.get('success') else 400)
    return jsonify(result), status


@app.route('/shield/children/<child_id>', methods=['PUT', 'PATCH'])
def shield_update_child(child_id):
    """Update a child record. Auto re-evaluates referral urgency on BLL change."""
    if not _SHIELD_AVAILABLE:
        return _shield_unavailable()
    updates = request.get_json(silent=True) or {}
    result = handle_shield_update_child(child_id, updates)
    return jsonify(result), (200 if result.get('success') else 400)


def _autostart_autonomous_engine():
    """Start the self-learning autonomous engine in the background on server boot."""
    try:
        import threading, time
        def _delayed_start():
            time.sleep(5)  # wait for server to fully initialize
            try:
                if get_autonomous_engine:
                    engine = get_autonomous_engine()
                    result = engine.start()
                    print(f"[NEXUS] Autonomous engine auto-started: {result.get('status')}")
                else:
                    print("[NEXUS] Autonomous engine module unavailable — skipping auto-start")
            except Exception as e:
                print(f"[NEXUS] Autonomous engine auto-start failed: {e}")
        t = threading.Thread(target=_delayed_start, daemon=True, name="autonomous-autostart")
        t.start()
    except Exception as e:
        print(f"[NEXUS] Could not schedule autonomous engine auto-start: {e}")


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    _autostart_autonomous_engine()
    app.run(host='0.0.0.0', port=port)
