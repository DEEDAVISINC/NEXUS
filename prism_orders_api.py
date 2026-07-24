#!/usr/bin/env python3
"""
PRISM Orders & Intake API
=========================
Handles:
1.  POST  /prism/intake — receive submissions from the client intake form
    (optional `channel`: `law_firm` or `service_key`: `notary-law-firm` — see
    `prism_law_firm_notary_channel.py` / GET `/prism/law-firm-channel/intake-schema`)
2.  GET   /prism/orders — list all orders (with optional filters)
3.  GET   /prism/orders/<id> — single order detail
4.  PATCH /prism/orders/<id> — update order status / assign agent
5.  PATCH /prism/orders/<id>/qc — check off individual QC items (mandatory)
6.  PATCH /prism/orders/<id>/gate — clear manual workflow gates
7.  GET   /prism/scanbacks — list orders that have scanback data
8.  POST  /prism/orders/<id>/scanback — agent submits document upload
9.  PATCH /prism/orders/<id>/scanback/review — admin marks clean/errors
10. GET   /prism/agents — list field agents
11. GET   /prism/clients — list clients

QC ENFORCEMENT: Every order auto-receives a service-specific compliance
checklist at creation. FATAL items must be checked before order can be
marked Complete. No exceptions.

AUTOMATED QC (Tier 1):
- Fatal flaw / DNA error detection auto-runs on scanback upload
- Workflow gates auto-evaluate from real data (page count, scanback, QC)
- Page-count enforcement flags under-count uploads
- Temporal compliance cross-checks (4-min temp, post-accident windows, shy bladder, cert expiry)
"""

import os
import json
import uuid
import re
import smtplib
import threading
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta as _timedelta
from typing import Optional
from flask import Blueprint, request, jsonify
from dotenv import load_dotenv

load_dotenv()

from company_info import BRAND_NAME, member_care_phone_display, ops_alert_phone_e164

prism_orders = Blueprint('prism_orders', __name__)

DATA_DIR = os.path.join(os.path.dirname(__file__), 'uploads', 'prism')
NEXUS_CONTRACTS_FILE = os.path.join(os.path.dirname(__file__), 'uploads', 'nexus', 'contracts.json')
os.makedirs(DATA_DIR, exist_ok=True)

ORDERS_FILE = os.path.join(DATA_DIR, 'orders.json')
AGENTS_FILE = os.path.join(DATA_DIR, 'agents.json')
CLIENTS_FILE = os.path.join(DATA_DIR, 'clients.json')

INTAKE_SERVICE_MAP = {
    'testing-drug': 'dot',
    'testing-occhealth': 'phlebotomy',
    'testing-lead': 'phlebotomy',
    'fingerprint': 'fingerprint',
    'background': 'background',
    'dna': 'dna',
    'nemt': 'nemt',
    'transport': 'nemt',
    'community-transition': 'community_transition',
    'cts': 'community_transition',
    'notary': 'notary',
    'notary-law-firm': 'notary',
    'apostille': 'apostille',
    'process': 'process',
    'courier': 'medical_courier',
    'credentialing': 'credentialing',
    'workforce': 'workforce',
}

URGENCY_TO_PRIORITY = {
    'stat': 'STAT',
    'emergency': 'STAT',
    'same-day': 'Same Day',
    'priority': 'Same Day',
    'scheduled': 'Standard',
    'routine': 'Standard',
}

TIER_FEE_BASE = {
    1: 150,   # Mobile Collector
    2: 85,    # Coordinated Ride
    3: 250,   # On-Site Group Event
}

# Event programs quoted per engagement — no fee at intake
SCOPED_PRICING_SERVICE_KEYS = frozenset({'arena', 'event-mobility'})

SERVICE_ROUTING_EMAILS = {
    'testing-drug': 'testing@deedavis.biz',
    'testing-occhealth': 'testing@deedavis.biz',
    'testing-lead': 'testing@deedavis.biz',
    'fingerprint': 'screening@deedavis.biz',
    'background': 'screening@deedavis.biz',
    'dna': 'dna@deedavis.biz',
    'nemt': 'nemt@deedavis.biz',
    'nemt-medicaid': 'nemt@deedavis.biz',
    'community_transition': 'cts@deedavis.biz',
    'arena': 'rides@deedavis.biz',
    'event-mobility': 'rides@deedavis.biz',
    'nemt-mobility': 'nemt@deedavis.biz',
    'transport': 'rides@deedavis.biz',
    'notary': 'notary@deedavis.biz',
    'apostille': 'notary@deedavis.biz',
    'process': 'notary@deedavis.biz',
    'courier': 'courier@deedavis.biz',
    'courier-legal': 'notary@deedavis.biz',
    'courier-medical': 'courier@deedavis.biz',
    'credentialing': 'credentialing@deedavis.biz',
    'workforce': 'compliance@deedavis.biz',
}

# ═══════════════════════════════════════════════════════════════════
# QC CHECKLISTS — auto-attached to every order by service type
# severity FATAL = hard gate (blocks order completion)
# severity CRITICAL = flagged but does not block
# severity STANDARD = advisory
# ═══════════════════════════════════════════════════════════════════

SERVICE_QC_CHECKLISTS = {
    'dot': [
        {'id': 'DOT-1', 'check': 'Collector holds valid CTPA certification?', 'severity': 'FATAL'},
        {'id': 'DOT-2', 'check': 'Federal CCF form used (not non-DOT)?', 'severity': 'FATAL'},
        {'id': 'DOT-3', 'check': 'Donor identity verified with photo ID?', 'severity': 'FATAL'},
        {'id': 'DOT-4', 'check': 'Specimen temperature 90-100°F within 4 minutes?', 'severity': 'FATAL'},
        {'id': 'DOT-5', 'check': 'Chain of custody unbroken and documented?', 'severity': 'FATAL'},
        {'id': 'DOT-6', 'check': 'Donor signed Step 5 of CCF?', 'severity': 'FATAL'},
        {'id': 'DOT-7', 'check': 'Specimen sealed with tamper-evident tape?', 'severity': 'CRITICAL'},
        {'id': 'DOT-8', 'check': 'Split specimen collected and sealed?', 'severity': 'CRITICAL'},
        {'id': 'DOT-9', 'check': 'Shy bladder protocol followed (if applicable)?', 'severity': 'CRITICAL'},
        {'id': 'DOT-10', 'check': 'Specimen shipped to lab within 24 hours?', 'severity': 'CRITICAL'},
    ],
    'non-dot': [
        {'id': 'NDOT-1', 'check': 'Collector holds valid CTPA certification?', 'severity': 'FATAL'},
        {'id': 'NDOT-2', 'check': 'Correct non-DOT CCF/requisition form used?', 'severity': 'FATAL'},
        {'id': 'NDOT-3', 'check': 'Donor identity verified?', 'severity': 'FATAL'},
        {'id': 'NDOT-4', 'check': 'Specimen temperature within acceptable range?', 'severity': 'FATAL'},
        {'id': 'NDOT-5', 'check': 'Chain of custody documented?', 'severity': 'CRITICAL'},
        {'id': 'NDOT-6', 'check': 'Client-specific panel type confirmed?', 'severity': 'CRITICAL'},
        {'id': 'NDOT-7', 'check': 'Specimen sealed and labeled?', 'severity': 'CRITICAL'},
        {'id': 'NDOT-8', 'check': 'Specimen shipped to correct lab?', 'severity': 'CRITICAL'},
    ],
    'dna': [
        {'id': 'DNA-1', 'check': 'Collector certified for legal DNA collections?', 'severity': 'FATAL'},
        {'id': 'DNA-2', 'check': 'All participants photo-ID verified?', 'severity': 'FATAL'},
        {'id': 'DNA-3', 'check': 'Chain of custody form completed and signed?', 'severity': 'FATAL'},
        {'id': 'DNA-4', 'check': 'Buccal swabs collected per protocol (no food/drink 30min)?', 'severity': 'FATAL'},
        {'id': 'DNA-5', 'check': 'Photographs taken of all participants with ID?', 'severity': 'FATAL'},
        {'id': 'DNA-6', 'check': 'Specimens sealed with tamper-evident packaging?', 'severity': 'CRITICAL'},
        {'id': 'DNA-7', 'check': 'Consent/authorization forms signed?', 'severity': 'CRITICAL'},
        {'id': 'DNA-8', 'check': 'Specimens shipped to AABB-accredited lab?', 'severity': 'CRITICAL'},
    ],
    'fingerprint': [
        {'id': 'FP-1', 'check': 'Technician trained on Live Scan / ink card procedures?', 'severity': 'FATAL'},
        {'id': 'FP-2', 'check': 'Subject identity verified with government photo ID?', 'severity': 'FATAL'},
        {'id': 'FP-3', 'check': 'Correct ORI number entered?', 'severity': 'FATAL'},
        {'id': 'FP-4', 'check': 'All 10 fingerprints captured with acceptable quality?', 'severity': 'FATAL'},
        {'id': 'FP-5', 'check': 'Rejection/quality check passed before submission?', 'severity': 'CRITICAL'},
        {'id': 'FP-6', 'check': 'Applicant signed fingerprint card/authorization?', 'severity': 'CRITICAL'},
        {'id': 'FP-7', 'check': 'Submission transmitted to FBI/state agency?', 'severity': 'CRITICAL'},
    ],
    'background': [
        {'id': 'BG-1', 'check': 'Written applicant consent/authorization obtained?', 'severity': 'FATAL'},
        {'id': 'BG-2', 'check': 'FCRA-compliant disclosure provided (standalone doc)?', 'severity': 'FATAL'},
        {'id': 'BG-3', 'check': 'Applicant identity verified with government photo ID?', 'severity': 'FATAL'},
        {'id': 'BG-4', 'check': 'SSN trace completed for address history?', 'severity': 'CRITICAL'},
        {'id': 'BG-5', 'check': 'County criminal search covers all relevant jurisdictions?', 'severity': 'CRITICAL'},
        {'id': 'BG-6', 'check': 'National sex offender registry checked?', 'severity': 'CRITICAL'},
        {'id': 'BG-7', 'check': 'Pre-adverse action notice sent before denial (FCRA §604)?', 'severity': 'FATAL'},
        {'id': 'BG-8', 'check': 'Applicant given copy of report + Summary of Rights?', 'severity': 'FATAL'},
        {'id': 'BG-9', 'check': 'Adverse action notice sent with dispute instructions?', 'severity': 'FATAL'},
        {'id': 'BG-10', 'check': 'State ban-the-box laws followed (if applicable)?', 'severity': 'CRITICAL'},
    ],
    'notary': [
        {'id': 'NOT-1', 'check': 'Active notary commission for this state?', 'severity': 'FATAL'},
        {'id': 'NOT-2', 'check': 'Signer identity verified with acceptable ID?', 'severity': 'FATAL'},
        {'id': 'NOT-3', 'check': 'Signer appeared willingly (no duress)?', 'severity': 'FATAL'},
        {'id': 'NOT-4', 'check': 'Correct notarial act performed (acknowledgment vs jurat)?', 'severity': 'FATAL'},
        {'id': 'NOT-5', 'check': 'Journal entry completed with all required fields?', 'severity': 'CRITICAL'},
        {'id': 'NOT-6', 'check': 'Seal/stamp affixed clearly and completely?', 'severity': 'CRITICAL'},
        {'id': 'NOT-7', 'check': 'Certificate wording matches state requirements?', 'severity': 'CRITICAL'},
    ],
    'ron': [
        {'id': 'RON-1', 'check': 'Agent holds active RON certification for this state?', 'severity': 'FATAL'},
        {'id': 'RON-2', 'check': 'KBA (knowledge-based authentication) passed by signer?', 'severity': 'FATAL'},
        {'id': 'RON-3', 'check': 'Credential analysis of signer ID passed?', 'severity': 'FATAL'},
        {'id': 'RON-4', 'check': 'Audio/video recording started before notarial act?', 'severity': 'FATAL'},
        {'id': 'RON-5', 'check': 'Signer identity confirmed on video?', 'severity': 'FATAL'},
        {'id': 'RON-6', 'check': 'Session recording stored per retention requirements?', 'severity': 'CRITICAL'},
        {'id': 'RON-7', 'check': 'Tamper-sealed digital certificate applied?', 'severity': 'CRITICAL'},
    ],
    'phlebotomy': [
        {'id': 'PH-1', 'check': 'Phlebotomist holds valid certification (CPT/PBT)?', 'severity': 'FATAL'},
        {'id': 'PH-2', 'check': 'Patient identity verified with two identifiers?', 'severity': 'FATAL'},
        {'id': 'PH-3', 'check': 'Correct tubes drawn for ordered tests?', 'severity': 'FATAL'},
        {'id': 'PH-4', 'check': 'Specimens labeled at bedside/draw station?', 'severity': 'FATAL'},
        {'id': 'PH-5', 'check': 'Order of draw followed?', 'severity': 'CRITICAL'},
        {'id': 'PH-6', 'check': 'Venipuncture site properly cleaned?', 'severity': 'CRITICAL'},
        {'id': 'PH-7', 'check': 'Sharps disposed in biohazard container?', 'severity': 'CRITICAL'},
        {'id': 'PH-8', 'check': 'Specimens stored at correct temperature?', 'severity': 'CRITICAL'},
    ],
    'nemt': [
        {'id': 'NEMT-1', 'check': 'Driver license current and matches state requirements?', 'severity': 'FATAL'},
        {'id': 'NEMT-2', 'check': 'Vehicle insurance current with required minimums ($1M+)?', 'severity': 'FATAL'},
        {'id': 'NEMT-3', 'check': 'Vehicle inspection current (daily pre-trip completed)?', 'severity': 'CRITICAL'},
        {'id': 'NEMT-4', 'check': 'Passenger identity verified before transport?', 'severity': 'CRITICAL'},
        {'id': 'NEMT-5', 'check': 'Pick-up and drop-off times documented?', 'severity': 'CRITICAL'},
        {'id': 'NEMT-6', 'check': 'Passenger signature obtained on trip log?', 'severity': 'CRITICAL'},
        {'id': 'NEMT-7', 'check': 'ADA accessibility requirements met (if applicable)?', 'severity': 'FATAL'},
        {'id': 'NEMT-8', 'check': 'No-show documented with timestamp?', 'severity': 'CRITICAL'},
        {'id': 'NEMT-9', 'check': 'HIPAA — passenger medical info protected?', 'severity': 'FATAL'},
    ],
    'community_transition': [
        {'id': 'CTS-1', 'check': 'If payer = Molina: LTSS Orientation Attestation on file? (Onboard equivalent gate before authorizing any other MCO\'s CTS.)', 'severity': 'FATAL'},
        {'id': 'CTS-2', 'check': 'If payer = Molina: Availity portal active with NPI 1538939111 confirmed? (Onboard equivalent gate before authorizing any other MCO\'s CTS.)', 'severity': 'FATAL'},
        {'id': 'CTS-3', 'check': 'Referral source (discharge planner / facility / Care Coordinator) and referral date recorded?', 'severity': 'FATAL'},
        {'id': 'CTS-4', 'check': 'PCSP Confirmation completed — CTS is an approved service on the member\'s PCSP?', 'severity': 'FATAL'},
        {'id': 'CTS-5', 'check': 'Requested expense category is Security Deposit or Utility Set-up (Furnishings/Moving Costs blocked — Article 2.9 disclosure not filed)?', 'severity': 'FATAL'},
        {'id': 'CTS-6', 'check': 'Supporting document (actual invoice/quote) uploaded for every expense item — no verbal estimates?', 'severity': 'FATAL'},
        {'id': 'CTS-7', 'check': 'Home Assessment requirement determined (Y/N), and if Yes, completed with a result before Authorization Sign-Off?', 'severity': 'CRITICAL'},
        {'id': 'CTS-8', 'check': 'Authorization Sign-Off completed with Amount Authorized and Payee recorded before billing T2038?', 'severity': 'FATAL'},
        {'id': 'CTS-9', 'check': 'Case documented for audit (full record retained) before closure?', 'severity': 'CRITICAL'},
    ],
    'medical_courier': [
        {'id': 'MC-1', 'check': 'Courier trained in specimen handling and biohazard transport?', 'severity': 'FATAL'},
        {'id': 'MC-2', 'check': 'Specimen packaging meets DOT/IATA standards?', 'severity': 'FATAL'},
        {'id': 'MC-3', 'check': 'Temperature requirements maintained during transport?', 'severity': 'FATAL'},
        {'id': 'MC-4', 'check': 'Chain of custody form accompanies specimen?', 'severity': 'FATAL'},
        {'id': 'MC-5', 'check': 'Pickup and delivery timestamps documented?', 'severity': 'CRITICAL'},
        {'id': 'MC-6', 'check': 'Recipient signature obtained at delivery?', 'severity': 'CRITICAL'},
        {'id': 'MC-7', 'check': 'Spill kit available in transport vehicle?', 'severity': 'CRITICAL'},
    ],
    'courier': [
        {'id': 'CR-1', 'check': 'Package picked up within scheduled window?', 'severity': 'CRITICAL'},
        {'id': 'CR-2', 'check': 'Delivery receipt signed at destination?', 'severity': 'CRITICAL'},
        {'id': 'CR-3', 'check': 'Package condition verified at pickup and delivery?', 'severity': 'STANDARD'},
        {'id': 'CR-4', 'check': 'Photo documentation of delivery?', 'severity': 'STANDARD'},
        {'id': 'CR-5', 'check': 'Chain of custody maintained (if applicable)?', 'severity': 'CRITICAL'},
    ],
    'apostille': [
        {'id': 'APO-1', 'check': 'Document is eligible for apostille (public document)?', 'severity': 'FATAL'},
        {'id': 'APO-2', 'check': 'Notarization on document is current and valid?', 'severity': 'FATAL'},
        {'id': 'APO-3', 'check': 'Destination country is Hague Convention member?', 'severity': 'FATAL'},
        {'id': 'APO-4', 'check': 'Original document submitted (not photocopy)?', 'severity': 'CRITICAL'},
        {'id': 'APO-5', 'check': 'Correct Secretary of State office identified?', 'severity': 'CRITICAL'},
        {'id': 'APO-6', 'check': 'Apostille certificate attached to correct document?', 'severity': 'FATAL'},
    ],
    'process': [
        {'id': 'PS-1', 'check': 'Correct individual/entity identified for service?', 'severity': 'FATAL'},
        {'id': 'PS-2', 'check': 'Service method compliant with jurisdiction rules?', 'severity': 'FATAL'},
        {'id': 'PS-3', 'check': 'Documents served within statute of limitations?', 'severity': 'FATAL'},
        {'id': 'PS-4', 'check': 'Proof of service / affidavit completed accurately?', 'severity': 'FATAL'},
        {'id': 'PS-5', 'check': 'Date, time, and location of service documented?', 'severity': 'CRITICAL'},
        {'id': 'PS-6', 'check': 'Proof of service filed with court within deadline?', 'severity': 'FATAL'},
    ],
}


def _build_qc_checklist(service_type):
    """Generate a fresh QC checklist for an order based on service type.
    Each item starts unchecked. FATAL items must all be checked before
    the order can move to Complete status."""
    template = SERVICE_QC_CHECKLISTS.get(service_type, [])
    return [
        {
            'id': item['id'],
            'check': item['check'],
            'severity': item['severity'],
            'completed': False,
            'completed_by': None,
            'completed_at': None,
        }
        for item in template
    ]


def _qc_gate_passed(order):
    """Returns True if all FATAL QC items are checked. If no checklist
    exists (legacy order), returns True to avoid blocking old data."""
    checklist = order.get('qc_checklist', [])
    if not checklist:
        return True
    fatal_items = [item for item in checklist if item['severity'] == 'FATAL']
    return all(item['completed'] for item in fatal_items)


# ═══════════════════════════════════════════════════════════════════
# AUTOMATED QC ENGINE — Tier 1 deterministic checks
# Runs on scanback upload, status change, and review.
# ═══════════════════════════════════════════════════════════════════

def _auto_run_compliance_checks(order):
    """Run service-specific compliance rule engines against order data.
    Populates order['auto_qc'] with results. Does NOT block — advisory
    layer that feeds the inspection engine and human reviewer."""
    svc_type = order.get('type', '')
    scanback = order.get('scanback', {})
    details = order.get('details', {})
    auto_qc = {
        'ran_at': datetime.now().isoformat(),
        'service_type': svc_type,
        'checks': [],
        'fatal_flags': [],
        'warnings': [],
        'page_count_ok': None,
        'temporal_ok': None,
    }

    # --- DOT fatal flaw check ---
    if svc_type in ('dot', 'non-dot'):
        try:
            from prism_dot_compliance import detect_fatal_flaws
            scanback_fields = details.get('scanback_fields', {})
            if scanback_fields:
                result = detect_fatal_flaws(scanback_fields)
                auto_qc['checks'].append({
                    'engine': 'DOT Fatal Flaw Detection',
                    'result': result.get('result', 'UNKNOWN'),
                    'message': result.get('message', ''),
                    'fatal_flaws': result.get('fatal_flaws', []),
                    'correctable_flaws': result.get('correctable_flaws', []),
                })
                for ff in result.get('fatal_flaws', []):
                    auto_qc['fatal_flags'].append(ff.get('notes', ff.get('name', 'DOT fatal flaw')))
        except ImportError:
            pass

    # --- DNA collection error check ---
    if svc_type == 'dna':
        try:
            from prism_dna_compliance import detect_dna_collection_errors
            collection_fields = details.get('collection_fields', {})
            if collection_fields:
                result = detect_dna_collection_errors(collection_fields)
                auto_qc['checks'].append({
                    'engine': 'DNA Collection Error Detection',
                    'collection_valid': result.get('collection_valid', True),
                    'recommendation': result.get('recommendation', ''),
                    'fatal_flaws': result.get('fatal_flaws', []),
                })
                for ff in result.get('fatal_flaws', []):
                    auto_qc['fatal_flags'].append(ff.get('description', 'DNA fatal flaw'))
        except ImportError:
            pass

    # --- Page count enforcement ---
    expected_info = SERVICE_EXPECTED_DOCS.get(svc_type, {})
    expected_pages = expected_info.get('pages', 0)
    uploads = scanback.get('uploads', [])
    if uploads:
        actual_pages = uploads[-1].get('pages', 0)
        auto_qc['page_count_ok'] = actual_pages >= expected_pages
        if actual_pages < expected_pages:
            auto_qc['warnings'].append(
                f'Page count under minimum: {actual_pages} uploaded vs {expected_pages} expected for {svc_type}'
            )
            if uploads[-1].get('errors') is None:
                uploads[-1]['errors'] = []
            uploads[-1]['errors'].append({
                'severity': 'WARNING',
                'page': 0,
                'description': f'Automated QC: {actual_pages} page(s) uploaded, {expected_pages} expected',
                'source': 'PRISM_AUTO_QC',
            })

    # --- Temporal compliance ---
    temporal_issues = _check_temporal_compliance(order)
    if temporal_issues:
        auto_qc['temporal_ok'] = False
        auto_qc['warnings'].extend(temporal_issues)
    else:
        auto_qc['temporal_ok'] = True

    # --- Tier 3: Risk scoring (if learning module available) ---
    try:
        from prism_qc_learning import compute_risk_score, load_agent_profiles
        agent_name = order.get('agent', '')
        agent_profile = None
        if agent_name:
            profiles = load_agent_profiles()
            agent_profile = profiles.get(agent_name)
        risk = compute_risk_score(order, agent_profile)
        auto_qc['risk_score'] = risk.get('risk_score', None)
        auto_qc['risk_routing'] = risk.get('routing', 'standard_review')
    except ImportError:
        auto_qc['risk_score'] = None
        auto_qc['risk_routing'] = 'standard_review'

    order['auto_qc'] = auto_qc
    return auto_qc


def _check_temporal_compliance(order):
    """Cross-check timestamps for regulatory windows. Returns list of issues."""
    issues = []
    svc_type = order.get('type', '')
    details = order.get('details', {})

    if svc_type == 'dot':
        collection_time_str = details.get('collection_time')
        temp_recorded_str = details.get('temp_recorded_time')
        if collection_time_str and temp_recorded_str:
            try:
                ct = datetime.fromisoformat(collection_time_str)
                tr = datetime.fromisoformat(temp_recorded_str)
                diff = (tr - ct).total_seconds()
                if diff > 240:
                    issues.append(
                        f'Temperature recorded {int(diff)}s after collection — exceeds 4-minute (240s) rule per 49 CFR Part 40'
                    )
            except (ValueError, TypeError):
                pass

        if details.get('test_reason') == 'post_accident':
            accident_time_str = details.get('accident_time')
            if accident_time_str and collection_time_str:
                try:
                    at = datetime.fromisoformat(accident_time_str)
                    ct = datetime.fromisoformat(collection_time_str)
                    drug_hrs = (ct - at).total_seconds() / 3600
                    if drug_hrs > 32:
                        issues.append(
                            f'Post-accident drug test collected {drug_hrs:.1f}h after accident — exceeds 32-hour window'
                        )
                    alcohol_time_str = details.get('alcohol_collection_time')
                    if alcohol_time_str:
                        act = datetime.fromisoformat(alcohol_time_str)
                        alc_hrs = (act - at).total_seconds() / 3600
                        if alc_hrs > 8:
                            issues.append(
                                f'Post-accident alcohol test {alc_hrs:.1f}h after accident — exceeds 8-hour window'
                            )
                except (ValueError, TypeError):
                    pass

        shy_bladder_start = details.get('shy_bladder_start')
        shy_bladder_end = details.get('shy_bladder_end')
        if shy_bladder_start and shy_bladder_end:
            try:
                sbs = datetime.fromisoformat(shy_bladder_start)
                sbe = datetime.fromisoformat(shy_bladder_end)
                window_hrs = (sbe - sbs).total_seconds() / 3600
                if window_hrs > 3:
                    issues.append(
                        f'Shy bladder window {window_hrs:.1f}h — exceeds 3-hour maximum per 49 CFR Part 40'
                    )
            except (ValueError, TypeError):
                pass

    return issues


def _check_scanback_received(order):
    """Returns True if at least one scanback upload exists with sufficient pages."""
    sb = order.get('scanback', {})
    uploads = sb.get('uploads', [])
    if not uploads:
        return False
    svc = order.get('type', '')
    expected = SERVICE_EXPECTED_DOCS.get(svc, {}).get('pages', 1)
    return uploads[-1].get('pages', 0) >= expected


# ═══════════════════════════════════════════════════════════════════
# ORDER WORKFLOW ENGINE
# Each order follows a sequential pipeline. You cannot advance
# to the next stage unless every gate condition on the current
# stage is satisfied. Service-specific stages override where needed.
# ═══════════════════════════════════════════════════════════════════

WORKFLOW_COMMON = [
    {
        'stage': 'received',
        'label': 'Order Received',
        'auto': True,
        'gates': [
            {'id': 'G-RCV-1', 'check': 'Client company name provided', 'field': 'client', 'rule': 'not_empty'},
            {'id': 'G-RCV-2', 'check': 'Subject / donor name provided', 'field': 'signer', 'rule': 'not_empty'},
            {'id': 'G-RCV-3', 'check': 'Service type confirmed', 'field': 'type', 'rule': 'not_empty'},
        ],
    },
    {
        'stage': 'validated',
        'label': 'Order Validated',
        'auto': True,
        'gates': [
            {'id': 'G-VAL-1', 'check': 'Scheduling date set', 'field': 'date', 'rule': 'not_empty'},
            {'id': 'G-VAL-2', 'check': 'Service location / address confirmed', 'field': 'address', 'rule': 'not_empty'},
            {'id': 'G-VAL-3', 'check': 'Client contact info on file', 'field': 'client_email', 'rule': 'not_empty'},
        ],
    },
    {
        'stage': 'assigned',
        'label': 'Agent Assigned',
        'auto': False,
        'gates': [
            {'id': 'G-ASN-1', 'check': 'Field agent assigned', 'field': 'agent', 'rule': 'not_empty'},
        ],
    },
    {
        'stage': 'en_route',
        'label': 'En Route / Scheduled',
        'auto': False,
        'gates': [
            {'id': 'G-ENR-1', 'check': 'Agent confirmed appointment', 'field': None, 'rule': 'manual'},
        ],
    },
    {
        'stage': 'in_progress',
        'label': 'Service In Progress',
        'auto': False,
        'gates': [
            {'id': 'G-SVC-1', 'check': 'Service being performed on-site', 'field': None, 'rule': 'manual'},
        ],
    },
    {
        'stage': 'qc_review',
        'label': 'QC Review',
        'auto': False,
        'gates': [
            {'id': 'G-QC-1', 'check': 'All FATAL QC items passed', 'field': None, 'rule': 'qc_fatal_pass'},
        ],
    },
    {
        'stage': 'documentation',
        'label': 'Documentation',
        'auto': True,
        'gates': [
            {'id': 'G-DOC-1', 'check': 'Scanback uploaded with sufficient pages', 'field': None, 'rule': 'scanback_received'},
            {'id': 'G-DOC-2', 'check': 'Automated QC passed (no fatal flags)', 'field': None, 'rule': 'auto_qc_clean'},
        ],
    },
    {
        'stage': 'delivered',
        'label': 'Results Delivered',
        'auto': False,
        'gates': [
            {'id': 'G-DLV-1', 'check': 'Results / documents sent to client', 'field': None, 'rule': 'manual'},
        ],
    },
    {
        'stage': 'billed',
        'label': 'Billed',
        'auto': False,
        'gates': [
            {'id': 'G-BIL-1', 'check': 'Invoice generated and sent', 'field': None, 'rule': 'manual'},
        ],
    },
    {
        'stage': 'complete',
        'label': 'Complete',
        'auto': True,
        'gates': [],
    },
]

SERVICE_STAGE_OVERRIDES = {
    'dot': {
        'in_progress': {
            'label': 'Collection In Progress',
            'gates': [
                {'id': 'G-DOT-1', 'check': 'Donor identity verified with photo ID', 'field': None, 'rule': 'manual'},
                {'id': 'G-DOT-2', 'check': 'Federal CCF form used (not non-DOT)', 'field': None, 'rule': 'manual'},
                {'id': 'G-DOT-3', 'check': 'Specimen temperature 90-100°F verified', 'field': None, 'rule': 'manual'},
            ],
        },
        'documentation': {
            'label': 'Specimen Shipped to Lab',
            'gates': [
                {'id': 'G-DOT-4', 'check': 'Specimen sealed with tamper-evident tape', 'field': None, 'rule': 'manual'},
                {'id': 'G-DOT-5', 'check': 'Specimen shipped via approved carrier', 'field': None, 'rule': 'manual'},
                {'id': 'G-DOT-6', 'check': 'Lab tracking number recorded', 'field': None, 'rule': 'manual'},
            ],
        },
    },
    'non-dot': {
        'in_progress': {
            'label': 'Collection In Progress',
            'gates': [
                {'id': 'G-ND-1', 'check': 'Donor identity verified', 'field': None, 'rule': 'manual'},
                {'id': 'G-ND-2', 'check': 'Correct panel / requisition form used', 'field': None, 'rule': 'manual'},
                {'id': 'G-ND-3', 'check': 'Specimen temperature acceptable', 'field': None, 'rule': 'manual'},
            ],
        },
    },
    'dna': {
        'in_progress': {
            'label': 'DNA Collection',
            'gates': [
                {'id': 'G-DNA-1', 'check': 'All participants present and photo-ID verified', 'field': None, 'rule': 'manual'},
                {'id': 'G-DNA-2', 'check': 'No food/drink/tobacco 30 min prior confirmed', 'field': None, 'rule': 'manual'},
                {'id': 'G-DNA-3', 'check': 'Buccal swabs collected per protocol', 'field': None, 'rule': 'manual'},
                {'id': 'G-DNA-4', 'check': 'Photographs taken of all participants with ID', 'field': None, 'rule': 'manual'},
            ],
        },
        'documentation': {
            'label': 'Specimen Shipped to AABB Lab',
            'gates': [
                {'id': 'G-DNA-5', 'check': 'Chain of custody sealed and signed', 'field': None, 'rule': 'manual'},
                {'id': 'G-DNA-6', 'check': 'Shipped to AABB-accredited laboratory', 'field': None, 'rule': 'manual'},
            ],
        },
    },
    'fingerprint': {
        'in_progress': {
            'label': 'Fingerprinting',
            'gates': [
                {'id': 'G-FP-1', 'check': 'Subject identity verified with government photo ID', 'field': None, 'rule': 'manual'},
                {'id': 'G-FP-2', 'check': 'Correct ORI number entered', 'field': None, 'rule': 'manual'},
                {'id': 'G-FP-3', 'check': 'All 10 fingerprints captured with acceptable quality', 'field': None, 'rule': 'manual'},
            ],
        },
        'documentation': {
            'label': 'Submission Transmitted',
            'gates': [
                {'id': 'G-FP-4', 'check': 'Prints submitted to FBI/state agency', 'field': None, 'rule': 'manual'},
                {'id': 'G-FP-5', 'check': 'Confirmation receipt saved', 'field': None, 'rule': 'manual'},
            ],
        },
    },
    'background': {
        'in_progress': {
            'label': 'Background Search Initiated',
            'gates': [
                {'id': 'G-BG-1', 'check': 'Written FCRA consent obtained (standalone)', 'field': None, 'rule': 'manual'},
                {'id': 'G-BG-2', 'check': 'FCRA disclosure provided', 'field': None, 'rule': 'manual'},
                {'id': 'G-BG-3', 'check': 'Applicant identity verified', 'field': None, 'rule': 'manual'},
                {'id': 'G-BG-4', 'check': 'SSN trace + county criminal search initiated', 'field': None, 'rule': 'manual'},
            ],
        },
        'documentation': {
            'label': 'Results Received from CRA',
            'gates': [
                {'id': 'G-BG-5', 'check': 'Background report received from CRA', 'field': None, 'rule': 'manual'},
                {'id': 'G-BG-6', 'check': 'Report reviewed for accuracy', 'field': None, 'rule': 'manual'},
            ],
        },
        'delivered': {
            'label': 'Report Delivered / Adverse Action',
            'gates': [
                {'id': 'G-BG-7', 'check': 'Report delivered to client', 'field': None, 'rule': 'manual'},
                {'id': 'G-BG-8', 'check': 'Pre-adverse action notice sent (if applicable)', 'field': None, 'rule': 'manual'},
                {'id': 'G-BG-9', 'check': 'Applicant given copy of report + Summary of Rights', 'field': None, 'rule': 'manual'},
            ],
        },
    },
    'notary': {
        'in_progress': {
            'label': 'Notarization',
            'gates': [
                {'id': 'G-NOT-1', 'check': 'Signer identity verified with acceptable ID', 'field': None, 'rule': 'manual'},
                {'id': 'G-NOT-2', 'check': 'Signer appeared willingly (no duress)', 'field': None, 'rule': 'manual'},
                {'id': 'G-NOT-3', 'check': 'Correct notarial act performed', 'field': None, 'rule': 'manual'},
            ],
        },
        'documentation': {
            'label': 'Journal + Seal',
            'gates': [
                {'id': 'G-NOT-4', 'check': 'Journal entry completed', 'field': None, 'rule': 'manual'},
                {'id': 'G-NOT-5', 'check': 'Seal/stamp affixed clearly', 'field': None, 'rule': 'manual'},
                {'id': 'G-NOT-6', 'check': 'Document scanned and uploaded', 'field': None, 'rule': 'manual'},
            ],
        },
    },
    'ron': {
        'in_progress': {
            'label': 'Remote Online Notarization',
            'gates': [
                {'id': 'G-RON-1', 'check': 'KBA (knowledge-based auth) passed by signer', 'field': None, 'rule': 'manual'},
                {'id': 'G-RON-2', 'check': 'Credential analysis of signer ID passed', 'field': None, 'rule': 'manual'},
                {'id': 'G-RON-3', 'check': 'Audio/video recording active', 'field': None, 'rule': 'manual'},
            ],
        },
        'documentation': {
            'label': 'Recording + Certificate',
            'gates': [
                {'id': 'G-RON-4', 'check': 'Session recording stored per retention rules', 'field': None, 'rule': 'manual'},
                {'id': 'G-RON-5', 'check': 'Tamper-sealed digital certificate applied', 'field': None, 'rule': 'manual'},
            ],
        },
    },
    'phlebotomy': {
        'in_progress': {
            'label': 'Specimen Collection',
            'gates': [
                {'id': 'G-PH-1', 'check': 'Patient identity verified with two identifiers', 'field': None, 'rule': 'manual'},
                {'id': 'G-PH-2', 'check': 'Correct tubes drawn for ordered tests', 'field': None, 'rule': 'manual'},
                {'id': 'G-PH-3', 'check': 'Specimens labeled at draw station', 'field': None, 'rule': 'manual'},
            ],
        },
    },
    'nemt': {
        'assigned': {
            'label': 'Driver Assigned',
            'gates': [
                {'id': 'G-NE-0', 'check': 'Driver confirmed and assigned to trip', 'field': None, 'rule': 'manual'},
            ],
        },
        'en_route': {
            'label': 'Driver En Route to Pickup',
            'gates': [
                {'id': 'G-NE-1', 'check': 'Driver confirmed and dispatched', 'field': None, 'rule': 'manual'},
                {'id': 'G-NE-2', 'check': 'Vehicle pre-trip inspection completed', 'field': None, 'rule': 'manual'},
            ],
        },
        'in_progress': {
            'label': 'Passenger Transport',
            'gates': [
                {'id': 'G-NE-3', 'check': 'Passenger identity verified', 'field': None, 'rule': 'manual'},
                {'id': 'G-NE-4', 'check': 'Passenger picked up — timestamp logged', 'field': None, 'rule': 'manual'},
                {'id': 'G-NE-5', 'check': 'Passenger delivered — timestamp logged', 'field': None, 'rule': 'manual'},
            ],
        },
        'documentation': {
            'label': 'Trip Documentation',
            'gates': [
                {'id': 'G-NE-6', 'check': 'Trip log signed by passenger', 'field': None, 'rule': 'manual'},
                {'id': 'G-NE-7', 'check': 'Mileage and times recorded', 'field': None, 'rule': 'manual'},
            ],
        },
    },
    'community_transition': {
        'in_progress': {
            'label': 'Eligibility/PCSP Verification & Documentation',
            'gates': [
                {'id': 'G-CTS-1', 'check': 'Referral source and date recorded', 'field': None, 'rule': 'manual'},
                {'id': 'G-CTS-2', 'check': 'PCSP Confirmation completed — CTS approved on member\'s PCSP', 'field': None, 'rule': 'manual'},
                {'id': 'G-CTS-3', 'check': 'Expense category is Security Deposit or Utility Set-up with supporting invoice/quote', 'field': None, 'rule': 'manual'},
            ],
        },
        'documentation': {
            'label': 'Home Assessment & Authorization Sign-Off',
            'gates': [
                {'id': 'G-CTS-4', 'check': 'Home Assessment requirement determined, and completed if required (T1028)', 'field': None, 'rule': 'manual'},
                {'id': 'G-CTS-5', 'check': 'Authorization Sign-Off completed — Amount Authorized and Payee recorded (T2038)', 'field': None, 'rule': 'manual'},
                {'id': 'G-CTS-6', 'check': 'Case documented for audit before closure', 'field': None, 'rule': 'manual'},
            ],
        },
    },
    'medical_courier': {
        'in_progress': {
            'label': 'Specimen Pickup & Transport',
            'gates': [
                {'id': 'G-MC-1', 'check': 'Specimen packaging meets DOT/IATA standards', 'field': None, 'rule': 'manual'},
                {'id': 'G-MC-2', 'check': 'Temperature requirements maintained', 'field': None, 'rule': 'manual'},
                {'id': 'G-MC-3', 'check': 'Chain of custody form with specimen', 'field': None, 'rule': 'manual'},
            ],
        },
        'documentation': {
            'label': 'Delivery Confirmed',
            'gates': [
                {'id': 'G-MC-4', 'check': 'Recipient signature obtained at lab', 'field': None, 'rule': 'manual'},
                {'id': 'G-MC-5', 'check': 'Pickup/delivery timestamps documented', 'field': None, 'rule': 'manual'},
            ],
        },
    },
    'apostille': {
        'in_progress': {
            'label': 'Document Processing',
            'gates': [
                {'id': 'G-APO-1', 'check': 'Document is public and eligible for apostille', 'field': None, 'rule': 'manual'},
                {'id': 'G-APO-2', 'check': 'Destination country is Hague Convention member', 'field': None, 'rule': 'manual'},
                {'id': 'G-APO-3', 'check': 'Submitted to correct Secretary of State', 'field': None, 'rule': 'manual'},
            ],
        },
        'documentation': {
            'label': 'Apostille Certificate Received',
            'gates': [
                {'id': 'G-APO-4', 'check': 'Apostille attached to correct document', 'field': None, 'rule': 'manual'},
            ],
        },
    },
    'process': {
        'in_progress': {
            'label': 'Attempting Service',
            'gates': [
                {'id': 'G-PS-1', 'check': 'Correct individual/entity located', 'field': None, 'rule': 'manual'},
                {'id': 'G-PS-2', 'check': 'Service method compliant with jurisdiction', 'field': None, 'rule': 'manual'},
            ],
        },
        'documentation': {
            'label': 'Proof of Service Filed',
            'gates': [
                {'id': 'G-PS-3', 'check': 'Affidavit / proof of service completed', 'field': None, 'rule': 'manual'},
                {'id': 'G-PS-4', 'check': 'Filed with court within deadline', 'field': None, 'rule': 'manual'},
            ],
        },
    },
}


def _build_workflow(service_type):
    """Build the full workflow for an order based on service type.
    Starts at stage 0 (received) with all gates unchecked."""
    import copy
    overrides = SERVICE_STAGE_OVERRIDES.get(service_type, {})
    stages = []
    for base in WORKFLOW_COMMON:
        stage = copy.deepcopy(base)
        if stage['stage'] in overrides:
            ovr = overrides[stage['stage']]
            if 'label' in ovr:
                stage['label'] = ovr['label']
            if 'gates' in ovr:
                stage['gates'] = copy.deepcopy(ovr['gates'])
        for g in stage['gates']:
            g['passed'] = False
            g['passed_by'] = None
            g['passed_at'] = None
        stages.append(stage)
    return stages


def _evaluate_auto_gates(order):
    """Auto-evaluate gates that check order fields (not manual).
    Also handles scanback_received and auto-QC fatal checks."""
    now_iso = datetime.now().isoformat()
    workflow = order.get('workflow', [])
    for stage in workflow:
        for gate in stage.get('gates', []):
            if gate.get('passed'):
                continue
            rule = gate.get('rule', 'manual')
            if rule == 'not_empty':
                field = gate.get('field', '')
                val = order.get(field, '')
                if val and str(val).strip():
                    gate['passed'] = True
                    gate['passed_by'] = 'System'
                    gate['passed_at'] = now_iso
            elif rule == 'qc_fatal_pass':
                if _qc_gate_passed(order):
                    gate['passed'] = True
                    gate['passed_by'] = 'System (QC Engine)'
                    gate['passed_at'] = now_iso
            elif rule == 'scanback_received':
                if _check_scanback_received(order):
                    gate['passed'] = True
                    gate['passed_by'] = 'System (Scanback Auto-Gate)'
                    gate['passed_at'] = now_iso
            elif rule == 'auto_qc_clean':
                aqc = order.get('auto_qc', {})
                if aqc and not aqc.get('fatal_flags') and aqc.get('page_count_ok') and aqc.get('temporal_ok'):
                    gate['passed'] = True
                    gate['passed_by'] = 'System (Auto QC — no fatal flags)'
                    gate['passed_at'] = now_iso
    order['workflow'] = workflow
    _update_workflow_position(order)
    return order


def _update_workflow_position(order):
    """Advance current_stage to the furthest stage where all prior
    stages have all gates passed."""
    raw_status = (order.get('status') or '').strip().lower()
    if raw_status in _portal_hidden_statuses():
        order['workflow_stage_label'] = 'Cancelled'
        return
    workflow = order.get('workflow', [])
    current = 0
    for i, stage in enumerate(workflow):
        all_passed = all(g['passed'] for g in stage.get('gates', []))
        if all_passed:
            current = i + 1
        else:
            break
    order['workflow_stage'] = min(current, len(workflow) - 1)
    stage_obj = workflow[order['workflow_stage']] if workflow else {}
    order['workflow_stage_label'] = stage_obj.get('label', 'Unknown')
    order['status'] = stage_obj.get('label', order.get('status', 'New'))
    if current >= len(workflow):
        order['status'] = 'Complete'


SMTP_SERVER = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = 587
EMAIL_FROM = os.environ.get('NEXUS_EMAIL', 'bids.deedavisinc@gmail.com')
EMAIL_PASSWORD = os.environ.get('NEXUS_EMAIL_PASSWORD')
ADMIN_EMAIL = os.environ.get('USER_EMAIL', 'info@deedavis.biz')


def _load(filepath, default=None):
    if default is None:
        default = []
    try:
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                return json.load(f)
    except (json.JSONDecodeError, IOError):
        pass
    return default


def _save(filepath, data):
    directory = os.path.dirname(filepath)
    if directory:
        os.makedirs(directory, exist_ok=True)
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2, default=str)


def _fire_notification(order):
    """Push a notification into the PRISM notification feed."""
    notif_file = os.path.join(os.path.dirname(__file__), 'uploads', 'notifications', 'notifications.json')
    try:
        details = order.get('details') or {}
        intake_channel = details.get('intake_channel') or order.get('intake_channel')
        is_voice = intake_channel == 'voice_ai'
        notif_type = 'voice_intake' if is_voice else 'new_order'
        priority = order.get('priority', 'Standard')
        severity = 'warning' if priority == 'STAT' else 'info'
        if priority == 'Same Day':
            severity = 'medium'

        notifs = _load(notif_file, [])
        notifs.insert(0, {
            'id': f"NOTIF-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:4]}",
            'type': notif_type,
            'icon': '📞' if is_voice else '📋',
            'severity': severity,
            'title': (
                'Voice Intake — NEMT Trip Booked'
                if is_voice
                else f"New {order.get('service_label', 'Service')} Request"
            ),
            'message': f"{order.get('client', '')} — {order.get('signer', '')} — {priority}",
            'target': 'admin',
            'order_id': order['id'],
            'created_at': datetime.utcnow().isoformat() + 'Z',
            'read': False,
            'metadata': {
                'service_key': order.get('service_key'),
                'intake_channel': intake_channel,
                'routing_email': order.get('routing_email'),
            },
        })
        if len(notifs) > 500:
            notifs = notifs[:500]
        _save(notif_file, notifs)
    except Exception:
        pass


def _send_order_email(order):
    """Send email notification to the service routing address + admin."""
    if not EMAIL_PASSWORD:
        print("PRISM email: No NEXUS_EMAIL_PASSWORD set, skipping email")
        return

    routing = order.get('routing_email') or SERVICE_ROUTING_EMAILS.get(order.get('service_key', ''), ADMIN_EMAIL)
    recipients = list({routing, ADMIN_EMAIL})

    priority_icon = {'STAT': '🚨', 'Same Day': '⚡'}.get(order.get('priority', ''), '📋')
    subject = f"{priority_icon} PRISM Order — {order['id']} — {order.get('service_label', 'Service Request')}"

    body = f"""PRISM SERVICE REQUEST — DEE DAVIS INC.
========================================
Confirmation:  {order['id']}
Created:       {order.get('created_at', '')}
Priority:      {order.get('priority', 'Standard')}
Service:       {order.get('service_label', '')}
Tier:          {order.get('tier', 1)}
Fee:           {('Dynamic — proposal after consultation (no flat rates)' if (order.get('billing') or {}).get('pricing_model') == 'scoped_per_event' or order.get('service_key') in SCOPED_PRICING_SERVICE_KEYS else f"${order.get('fee', 0)}")}
========================================

CLIENT
Company:       {order.get('client', '')}
Contact:       {order.get('client_contact', '')}
Phone:         {order.get('client_phone', '')}
Email:         {order.get('client_email', '')}
PO / Account:  {order.get('client_po', '')}
Address:       {order.get('client_address', '')}

SUBJECT
Name:          {order.get('signer', '')}
DOB:           {order.get('subject_dob', '')}
Phone:         {order.get('subject_phone', '')}
Email:         {order.get('subject_email', '')}
ID:            {order.get('subject_id', '')}
Location:      {order.get('address', '')}

SCHEDULING
Date:          {order.get('date', '')}
Time:          {order.get('time', '')} {order.get('timezone', '')}
Site:          {order.get('collection_site', '')}

Notes:         {order.get('notes', '')}
"""
    details = order.get('details') or {}
    if details:
        body += "\nSERVICE DETAILS\n"
        for key, value in details.items():
            if value and str(value).strip() not in ('', '—'):
                label = key.replace('_', ' ').title()
                body += f"{label + ':':14} {value}\n"
    body += """========================================
View in PRISM Dashboard: NEXUS → PRISM → Orders
"""

    try:
        msg = MIMEMultipart()
        msg['From'] = f"PRISM Dispatch <{EMAIL_FROM}>"
        msg['To'] = ', '.join(recipients)
        msg['Subject'] = subject
        if order.get('priority') == 'STAT':
            msg['X-Priority'] = '1'
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_FROM, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        print(f"PRISM email: Sent to {recipients} for order {order['id']}")
    except Exception as e:
        print(f"PRISM email: Failed — {e}")


def _send_order_email_async(order):
    """Fire-and-forget email in background thread so API response isn't delayed."""
    threading.Thread(target=_send_order_email, args=(order,), daemon=True).start()


# ── Status-driven notification messages ──────────────────────────────────────
# Fires automatically when order status changes. Skips NEMT (handled by
# Uber Health / Lyft Healthcare API webhooks when credentials are active).

# NEMT ride-tracking statuses (En Route, Arrived, Departed) are owned by
# Uber Health / Lyft Healthcare webhooks once API credentials are active.
# We still fire initial confirmation, day-of reminder, and completion for NEMT —
# just not the mid-ride position updates.
_NEMT_RIDE_TRACKING_STATUSES = {'En Route', 'Arrived', 'Departed', 'Driver Assigned'}
_SKIP_STATUS_NOTIFY_SERVICES = set()  # No service fully skipped — NEMT handled below

def _status_sms_templates() -> dict:
    """Member-facing status SMS — always use care line, never CEO personal."""
    care = member_care_phone_display()
    return {
        'Confirmed': (
            "✅ Confirmed: your {what} with {BRAND_NAME}\n\n"
            "Eligibility verified — we're preparing dispatch for your scheduled trip.\n\n"
            "📅 {dt_str}\n📍 {location}\nRef: {ref}\n\n"
            f"Questions? Call/text {care}"
        ),
        'Agent Assigned': (
            "📋 Update on your {what} with {BRAND_NAME}\n\n"
            "A collector has been assigned to your order and will contact you "
            "before heading your way.\n\n"
            "📅 {dt_str}\n📍 {location}\nRef: {ref}\n\n"
            f"Questions? Call/text {care}"
        ),
        'En Route': (
            "🚗 Your collector is on the way!\n\n"
            "📋 {what}\n"
            "📍 Heading to: {location}\n"
            "📅 Scheduled: {dt_str}\n\n"
            "Please be ready at your location.\n"
            f"Ref: {{ref}} · Questions? {care}"
        ),
        'Arrived': (
            "✅ Your collector has arrived!\n\n"
            "📋 {what}\n"
            "📍 {location}\n\n"
            "Please come to the door / front desk now.\n"
            f"Ref: {{ref}} · Questions? {care}"
        ),
        'In Progress': (
            "🔬 Your {what} is now in progress.\n\n"
            "📍 {location}\n"
            f"Ref: {{ref}}\n\n"
            f"{BRAND_NAME} · {care}"
        ),
        'Complete': (
            "✅ Your {what} is complete!\n\n"
            "Results will be processed and delivered per standard protocol.\n"
            f"If you have questions, contact {BRAND_NAME} at {care}.\n\n"
            "Ref: {ref}"
        ),
        'No Show': (
            "⚠️ We attempted to complete your {what} but were unable to reach you "
            "at {location}.\n\n"
            f"Please call {BRAND_NAME} at {care} to reschedule.\n"
            "Ref: {ref}"
        ),
        'Cancelled': (
            "Your {what} (Ref: {ref}) has been cancelled.\n\n"
            f"To reschedule, call {BRAND_NAME} at {care} or reply to this message."
        ),
    }

_SVC_LABELS_SHORT = {
    'dot':             'drug screen',
    'phlebotomy':      'occupational health appointment',
    'fingerprint':     'fingerprinting appointment',
    'dna':             'DNA collection',
    'notary':          'notary signing',
    'apostille':       'notary / apostille service',
    'medical_courier': 'courier pickup',
    'background':      'background check appointment',
    'process':         'process service appointment',
}

_COMPLETION_TIMEFRAMES = {
    'dot':        '24–48 hours via your MRO',
    'phlebotomy': '3–5 business days',
    'fingerprint':'3–5 business days via the submitting agency',
    'dna':        '3–5 business days from the lab',
    'background': '1–3 business days',
    'notary':     'immediately — your documents are complete',
}


def _fire_status_notification(order: dict, new_status: str) -> None:
    """
    Fire an SMS (and optionally email) to the subject/client when order status
    changes to a meaningful milestone. Non-blocking daemon thread.
    For NEMT: skips ride-tracking statuses (En Route, Arrived, Departed) —
    those come from Uber Health / Lyft Healthcare webhooks once APIs are active.
    Initial confirmation, day-of reminder, and completion fire for all services.
    """
    svc = order.get('service_key', '')
    # NEMT ride-tracking = Uber/Lyft's job, not ours
    if svc in ('nemt', 'transport') and new_status in _NEMT_RIDE_TRACKING_STATUSES:
        return

    template = _status_sms_templates().get(new_status)
    if not template:
        return

    phone = order.get('subject_phone') or order.get('client_phone', '')
    email = (order.get('client_email') or order.get('subject_email') or '').strip()
    name  = order.get('signer') or order.get('client_contact') or order.get('client', '')

    if not phone and not email:
        return

    what_str  = _SVC_LABELS_SHORT.get(svc, order.get('service_label', 'appointment'))
    dt_str    = f"{order.get('date', '')} at {order.get('time', '')} {order.get('timezone', 'ET')}".strip()
    location  = order.get('address') or order.get('collection_site') or 'your location'
    ref       = order.get('id', '')

    # For completion, swap in the timeframe line
    care = member_care_phone_display()
    if new_status == 'Complete':
        if svc in ('nemt', 'transport'):
            body = (
                f"✅ Your {what_str} with {BRAND_NAME} is complete.\n\n"
                f"You have arrived at your destination.\n"
                f"Need a ride home? Open portal.deedavis.biz → tap Return home on this trip.\n"
                f"Questions? Call {care}.\n\n"
                f"Ref: {ref}"
            )
        else:
            timeframe = _COMPLETION_TIMEFRAMES.get(svc, 'per standard protocol')
            body = (
                f"✅ Your {what_str} is complete!\n\n"
                f"Results: {timeframe}.\n"
                f"Questions? Call {BRAND_NAME} at {care}.\n\n"
                f"Ref: {ref}"
            )
    else:
        body = template.format(
            what=what_str, dt_str=dt_str,
            location=location, ref=ref, name=name or 'there'
        )

    # Internal alert on No Show — ops mobile, not CEO personal
    dee_alert = new_status == 'No Show'

    def _do() -> None:
        try:
            from nexus_confirmation_engine import _send_sms_raw, _send_email_raw
            if phone:
                _send_sms_raw(phone, body)
            # Email on completion and no-show only (not every status ping)
            if email and new_status in ('Complete', 'No Show', 'Cancelled'):
                subj = f"{'✅' if new_status == 'Complete' else '⚠️'} {what_str.capitalize()} — {new_status} · Ref {ref}"
                html = f"<p>Hi {name or 'there'},</p><p>{body.replace(chr(10), '<br/>')}</p>"
                _send_email_raw(email, subj, html, cc='info@deedavis.biz')
            if dee_alert:
                dee_phone = ops_alert_phone_e164()
                if dee_phone:
                    _send_sms_raw(
                        dee_phone,
                        f"⚠️ NO SHOW: {name or 'Subject'} was not present for {what_str} "
                        f"at {location}. Ref: {ref}"
                    )
        except Exception as exc:
            import logging
            logging.getLogger('prism.orders').warning('Status notification error: %s', exc)

    threading.Thread(target=_do, daemon=True).start()


def _fire_dayon_reminder(order: dict) -> None:
    """
    Schedule a day-of reminder SMS at 7 AM on the appointment date.
    Called when an order is created or rescheduled with a future date.
    Fires for ALL services including NEMT.
    """
    import time as _time

    svc = order.get('service_key', '')

    phone = order.get('subject_phone') or order.get('client_phone', '')
    if not phone:
        return

    date_str = order.get('date', '')
    time_str = order.get('time', '')
    if not date_str:
        return

    what_str = _SVC_LABELS_SHORT.get(svc, order.get('service_label', 'appointment'))
    location = order.get('address') or order.get('collection_site') or 'your scheduled location'
    ref      = order.get('id', '')
    name     = order.get('signer') or order.get('client_contact') or order.get('client', 'there')
    tz_str   = order.get('timezone', 'ET')
    bring    = ''
    if svc in ('dot', 'phlebotomy'):
        bring = "Bring a valid photo ID. Do not use the restroom immediately before."
    elif svc == 'fingerprint':
        bring = "Bring a valid photo ID. Clean, dry hands required."
    elif svc == 'dna':
        bring = "Bring a valid photo ID. No eating or drinking 30 minutes before."
    elif svc in ('notary', 'apostille'):
        bring = "Bring all documents to be notarized and a valid photo ID."

    def _schedule() -> None:
        try:
            from datetime import datetime as _dt
            from zoneinfo import ZoneInfo
            eastern = ZoneInfo('America/Detroit')

            # Parse appointment date
            for fmt in ('%m/%d/%Y', '%Y-%m-%d', '%B %d, %Y'):
                try:
                    appt_date = _dt.strptime(date_str.strip(), fmt).date()
                    break
                except ValueError:
                    continue
            else:
                return  # Unparseable date

            # Target: 7 AM ET on appointment day
            target = _dt(appt_date.year, appt_date.month, appt_date.day,
                         7, 0, 0, tzinfo=eastern)
            now    = _dt.now(eastern)
            delay  = (target - now).total_seconds()

            if delay < 0:
                return  # Appointment already passed or same-day past 7 AM

            _time.sleep(delay)

            body = (
                f"⏰ Reminder — your {what_str} is TODAY!\n\n"
                f"📅 {date_str} at {time_str} {tz_str}\n"
                f"📍 {location}\n"
            )
            if bring:
                body += f"\n🎒 {bring}\n"
            body += (
                f"\nRef: {ref}\n"
                f"Questions? Call/text {BRAND_NAME} at {member_care_phone_display()}"
            )

            from nexus_confirmation_engine import _send_sms_raw
            _send_sms_raw(phone, body)

        except Exception as exc:
            import logging
            logging.getLogger('prism.orders').warning('Day-of reminder error: %s', exc)

    threading.Thread(target=_schedule, daemon=True).start()


def _send_confirmation_async(order):
    """
    Fire confirmation requests to the requester AND the member/rider when scheduled.
    Uses the NEXUS Confirmation Engine — non-blocking, daemon thread.
    """
    if not order.get('date') or not order.get('time'):
        return

    requester_email = (order.get('client_email') or '').strip()
    requester_phone = order.get('client_phone', '')
    requester_name = order.get('client_contact') or order.get('client', 'there')

    rider_email = (order.get('subject_email') or '').strip()
    rider_phone = order.get('subject_phone', '')
    rider_name = order.get('signer') or 'Member'

    if not (requester_email or requester_phone or rider_email or rider_phone):
        return

    svc_map = {
        'dot':             'drug_test',
        'phlebotomy':      'occ_health',
        'fingerprint':     'fingerprint',
        'dna':             'dna_collection',
        'nemt':            'nemt_ride',
        'notary':          'notary_signing',
        'apostille':       'notary_signing',
        'medical_courier': 'prism_appointment',
    }
    event_type = svc_map.get(order.get('service_key', ''), 'prism_appointment')

    dt_str   = f"{order['date']} at {order['time']} {order.get('timezone', 'ET')}"
    location = order.get('address') or order.get('collection_site') or 'TBD — details to follow'

    svc_labels = {
        'dot':             'DOT urine drug screen (5-panel)',
        'phlebotomy':      'Occupational health / blood draw',
        'fingerprint':     'Electronic fingerprinting (LiveScan)',
        'dna':             'DNA collection (chain of custody)',
        'nemt':            'Non-emergency medical transport pickup',
        'notary':          'Notary signing service',
        'apostille':       'Apostille / notary service',
        'medical_courier': 'Medical courier pickup',
    }
    what_str = svc_labels.get(order.get('service_key', ''), order.get('service_label', '') or 'Service appointment')
    who_str  = '{BRAND_NAME} — your assigned provider will contact you before arrival'
    bring_str = ''
    svc = order.get('service_key', '')
    if svc in ('dot', 'phlebotomy'):
        bring_str = 'Government-issued photo ID required. Do not use the restroom immediately before your appointment.'
    elif svc == 'fingerprint':
        bring_str = 'Government-issued photo ID required. Clean, dry hands.'
    elif svc == 'dna':
        bring_str = 'Government-issued photo ID required. Do not eat or drink 30 minutes before.'
    elif svc == 'notary':
        bring_str = 'Bring all documents to be notarized and a valid government-issued photo ID.'

    def _do():
        try:
            from nexus_calendar_service import create_calendar_event
            svc_title = {
                'dot': 'DOT Drug Screen', 'phlebotomy': 'Occ Health Appointment',
                'fingerprint': 'Fingerprinting', 'dna': 'DNA Collection',
                'notary': 'Notary Signing', 'apostille': 'Apostille/Notary',
                'medical_courier': 'Medical Courier Pickup', 'background': 'Background Check',
            }.get(svc, order.get('service_label', 'PRISM Appointment'))
            create_calendar_event(
                title=f"{svc_title} — {rider_name or order.get('client', '')}",
                start_iso=order.get('date', '') + 'T' + (order.get('time', '09:00').replace(' ', '') or '09:00') + ':00',
                location=location,
                description=order.get('notes', ''),
                system='PRISM',
                event_type='appointment',
                internal_id=order.get('id', ''),
                party_name=rider_name,
                party_email=rider_email or requester_email,
                party_phone=rider_phone or requester_phone,
            )
        except Exception:
            pass
        try:
            from nexus_confirmation_engine import send_confirmation_request

            # Requester — booking confirmation (email preferred; SMS if no email)
            if requester_email or requester_phone:
                send_confirmation_request(
                    event_type=event_type,
                    party_name=requester_name,
                    party_email=requester_email,
                    party_phone=requester_phone if not requester_email else '',
                    datetime_str=dt_str,
                    location=location,
                    internal_id=order.get('id', ''),
                    notes=order.get('notes', ''),
                    who=who_str,
                    what=what_str,
                    why=f"Request submitted for {rider_name}",
                    bring=bring_str,
                )

            # Member/rider — skip duplicate if same email/phone as requester
            rider_email_norm = rider_email.lower()
            requester_email_norm = requester_email.lower()
            same_email = rider_email_norm and rider_email_norm == requester_email_norm
            same_phone = rider_phone and requester_phone and rider_phone == requester_phone

            if (rider_email or rider_phone) and not (same_email or (not rider_email and same_phone)):
                send_confirmation_request(
                    event_type=event_type,
                    party_name=rider_name,
                    party_email=rider_email if not same_email else '',
                    party_phone=rider_phone if not same_phone else '',
                    datetime_str=dt_str,
                    location=location,
                    internal_id=order.get('id', ''),
                    notes=order.get('notes', ''),
                    who=who_str,
                    what=what_str,
                    why=order.get('notes', '') or 'Your scheduled service with {BRAND_NAME}',
                    bring=bring_str,
                )
        except Exception as exc:
            import logging
            logging.getLogger('prism.orders').warning('Confirmation engine error: %s', exc)

    threading.Thread(target=_do, daemon=True).start()


def _fire_pipeline_event(event_type, order, extra=None):
    """Fire a cross-system event to the NEXUS pipeline (non-blocking)."""
    def _do_fire():
        try:
            nexus_data_path = NEXUS_CONTRACTS_FILE
            if not os.path.exists(nexus_data_path):
                return

            with open(nexus_data_path, 'r') as f:
                nxdata = json.load(f)

            contract_id = order.get('contract_id', '')
            event = {
                'id': f"EVT-{datetime.now().strftime('%Y%m%d%H%M%S')}-{len(nxdata.get('events', []))+1:04d}",
                'type': event_type,
                'contract_id': contract_id,
                'source': 'PRISM',
                'target': 'PIPELINE',
                'details': {
                    'order_id': order.get('id', ''),
                    'service_type': order.get('type', '') or order.get('service_type', ''),
                    'client_name': order.get('client', '') or order.get('client_name', ''),
                    'status': order.get('status', ''),
                    'total_amount': order.get('fee', 0) or order.get('total_amount', 0),
                    **(extra or {}),
                },
                'timestamp': datetime.now().isoformat(),
            }

            nxdata.setdefault('events', []).append(event)
            if len(nxdata['events']) > 500:
                nxdata['events'] = nxdata['events'][-500:]

            if contract_id and event_type == 'order_completed':
                for c in nxdata.get('contracts', []):
                    if c['id'] == contract_id:
                        c['health']['orders_completed'] = c['health'].get('orders_completed', 0) + 1
                        total = c['health'].get('orders_total', 1) or 1
                        completed = c['health']['orders_completed']
                        c['health']['deliverables_pct'] = round((completed / total) * 100)
                        c['updated_at'] = datetime.now().isoformat()
                        break

            if contract_id and event_type == 'order_created':
                for c in nxdata.get('contracts', []):
                    if c['id'] == contract_id:
                        oid = order.get('id', '')
                        if oid and oid not in c.get('prism_orders', []):
                            c.setdefault('prism_orders', []).append(oid)
                        c['health']['orders_total'] = c['health'].get('orders_total', 0) + 1
                        c['updated_at'] = datetime.now().isoformat()
                        break

            with open(nexus_data_path, 'w') as f:
                json.dump(nxdata, f, indent=2, default=str)

            if event_type == 'order_completed':
                _propagate_prism_to_vertex(order, contract_id, nxdata)

        except Exception as e:
            print(f"Pipeline event fire error: {e}")

    threading.Thread(target=_do_fire, daemon=True).start()


def _propagate_prism_to_vertex(order, contract_id, nxdata):
    """When a PRISM order completes, auto-create VERTEX invoice line item."""
    try:
        from nexus_backend import AirtableClient
        client = AirtableClient()

        order_id = order.get('id', '')
        amount = order.get('fee', 0) or order.get('total_amount', 0)
        svc = order.get('type', '') or order.get('service_type', '')
        client_name = order.get('client', '') or order.get('client_name', '')

        contract_title = ''
        for c in nxdata.get('contracts', []):
            if c['id'] == contract_id:
                client_name = client_name or c.get('agency', '')
                contract_title = c.get('title', '')
                break

        inv_number = f"INV-{datetime.now().strftime('%Y%m')}-{order_id[-6:]}"
        desc = f"Service: {svc} | Order: {order_id}"
        if contract_title:
            desc += f" | Contract: {contract_title}"

        vertex_fields = {
            'Invoice Number': inv_number,
            'Invoice Date': datetime.now().isoformat(),
            'Due Date': (datetime.now() + _timedelta(days=30)).isoformat(),
            'Client Name': client_name,
            'Source System': 'PRISM',
            'Source Record ID': order_id,
            'Invoice Type': 'Service',
            'Total Amount': amount,
            'Payment Status': 'Unpaid',
            'Payment Terms': 'Net 30',
            'Notes': desc,
        }
        client.create_record('VERTEX INVOICES', vertex_fields)
        print(f"✅ PRISM→VERTEX: Invoice {inv_number} created for ${amount:,.2f}")
    except Exception as e:
        print(f"PRISM→VERTEX propagation skipped: {e}")


# ═══════════════════════════════════════════════════════════════════
# POST /prism/intake  —  Client intake form submission
# ═══════════════════════════════════════════════════════════════════

@prism_orders.route('/prism/intake', methods=['POST'])
def create_intake_order():
    try:
        return _create_intake_order_impl()
    except OSError as e:
        return jsonify({
            'error': f'Could not save order (disk/path): {e}',
            'hint': 'Run: mkdir -p uploads/prism && check PythonAnywhere disk quota',
        }), 507
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e), 'type': type(e).__name__}), 500


def _create_intake_order_impl():
    data = request.get_json(silent=True) or {}

    svc_key = data.get('service_key', 'notary')
    service_type = INTAKE_SERVICE_MAP.get(svc_key, 'notary')
    urgency_raw = data.get('urgency', 'scheduled').lower()
    priority = URGENCY_TO_PRIORITY.get(urgency_raw, 'Standard')
    tier = int(data.get('tier', 1))
    fee = TIER_FEE_BASE.get(tier, 150)

    details = dict(data.get('details') or {})
    if data.get('rebook_source_id'):
        details['rebook_source_id'] = data.get('rebook_source_id')
        details['rebook_mode'] = data.get('rebook_mode') or ''
    is_scoped_pricing = (
        svc_key in SCOPED_PRICING_SERVICE_KEYS
        or details.get('pricing_model') == 'scoped_per_event'
        or data.get('pricing_model') == 'scoped_per_event'
    )
    if is_scoped_pricing:
        fee = 0
        details['pricing_model'] = 'scoped_per_event'

    if priority == 'STAT':
        fee = int(fee * 1.5)
    elif priority == 'Same Day':
        fee = int(fee * 1.25)

    now = datetime.now()
    from prism_confirmation_ids import channel_code, confirmation_display_meta, generate_confirmation_id

    channel = (data.get('channel') or '').strip().lower()
    incoming_conf = (data.get('confirmation') or '').strip()
    if incoming_conf:
        conf = incoming_conf
    else:
        conf = generate_confirmation_id(
            svc_key,
            channel or 'web',
            details=details,
            payer_name=data.get('payer') or details.get('payer'),
            client_company=data.get('client_company', '') or data.get('client_name', ''),
            contract_payer_id=details.get('contract_payer_id'),
        )

    sub_phone = re.sub(r'\D', '', data.get('subject_phone', '') or data.get('client_phone', '') or '')
    if sub_phone and not details.get('confirmation_phone_last4'):
        details['confirmation_phone_last4'] = sub_phone[-4:]

    routing_email = data.get('routing_email', SERVICE_ROUTING_EMAILS.get(svc_key, ADMIN_EMAIL))

    if channel == 'law_firm' or svc_key == 'notary-law-firm':
        try:
            from prism_law_firm_notary_channel import extract_law_firm_account_payload
            lf_payload = extract_law_firm_account_payload(data)
            if lf_payload:
                details['law_firm_account'] = lf_payload
        except ImportError:
            pass

    order = {
        'id': conf,
        'confirmation_ref': conf,
        'confirmation_meta': confirmation_display_meta(conf, channel=channel_code(channel or 'web')),
        'type': service_type,
        'service_key': svc_key,
        'channel': channel or None,
        'service_label': data.get('service_label', ''),
        'status': 'New',
        'agent': '',
        'client': data.get('client_company', '') or data.get('client_name', ''),
        'client_contact': data.get('client_contact', ''),
        'client_phone': data.get('client_phone', ''),
        'client_email': data.get('client_email', ''),
        'client_po': data.get('client_po', ''),
        'client_address': data.get('client_address', ''),
        'signer': f"{data.get('subject_first', '')} {data.get('subject_last', '')}".strip(),
        'subject_dob': data.get('subject_dob', ''),
        'subject_phone': data.get('subject_phone', ''),
        'subject_email': data.get('subject_email', ''),
        'subject_id': data.get('subject_id', ''),
        'address': data.get('subject_location', ''),
        'date': data.get('sched_date', now.strftime('%m/%d/%Y')),
        'time': data.get('sched_time', ''),
        'timezone': data.get('sched_tz', 'EST'),
        'collection_site': data.get('collection_site', ''),
        'fee': fee,
        'priority': priority,
        'tier': tier,
        'notes': data.get('notes', ''),
        'routing_email': routing_email,
        'details': details,
        'qc_checklist': _build_qc_checklist(service_type),
        'qc_status': 'pending',
        'workflow': _build_workflow(service_type),
        'workflow_stage': 0,
        'workflow_stage_label': 'Scoping Request' if is_scoped_pricing else 'Order Received',
        'created_at': now.isoformat(),
        'updated_at': now.isoformat(),
    }

    if service_type == 'community_transition':
        order['workflow_stage_label'] = 'CTS Referral Received'

    _evaluate_auto_gates(order)

    orders = _load(ORDERS_FILE, [])
    orders.insert(0, order)
    _save(ORDERS_FILE, orders)

    # Sync to Airtable PRISM Orders (system of record for portal calendar)
    try:
        from prism_airtable_intake import sync_intake_order_to_airtable
        airtable_id = sync_intake_order_to_airtable(order, data)
        if airtable_id:
            order['airtable_record_id'] = airtable_id
            orders[0] = order
            _save(ORDERS_FILE, orders)
    except Exception as e:
        print(f'PRISM Airtable intake sync skipped: {e}')

    nemt_order_id = None
    try:
        from prism_nemt import create_nemt_from_prism_intake

        nemt_order_id = create_nemt_from_prism_intake(order, data)
        if nemt_order_id:
            order.setdefault('details', {})['nemt_order_id'] = nemt_order_id
            orders[0] = order
            _save(ORDERS_FILE, orders)
    except Exception as e:
        print(f'PRISM NEMT auto-link skipped: {e}')

    cts_id = None
    try:
        from prism_nemt import create_cts_from_prism_intake

        cts_id = create_cts_from_prism_intake(order, data)
        if cts_id:
            order.setdefault('details', {})['cts_id'] = cts_id
            orders[0] = order
            _save(ORDERS_FILE, orders)
    except Exception as e:
        print(f'PRISM CTS (Community Transition) auto-link skipped: {e}')

    # Billing data from intake form
    billing_tier = data.get('billing_tier', 'pay_at_booking')
    payment_method = data.get('payment_method', '')
    override_code = data.get('override_code', '')
    if is_scoped_pricing:
        order_total = 0.0
        if not payment_method:
            payment_method = 'proposal'
    else:
        order_total = float(data.get('order_total', fee) or fee)
    order['billing'] = {
        'tier': billing_tier,
        'payment_method': payment_method,
        'override_code': override_code,
        'order_total': order_total,
        'pricing_model': 'scoped_per_event' if is_scoped_pricing else details.get('pricing_model', ''),
    }
    if is_scoped_pricing:
        order['fee'] = 0

    _fire_notification(order)
    _send_order_email_async(order)
    _fire_pipeline_event('order_created', order)
    _send_confirmation_async(order)
    _fire_dayon_reminder(order)

    # Fire VERTEX invoice creation async
    def _vertex_invoice():
        if is_scoped_pricing or order_total <= 0:
            return
        try:
            from vertex_automation import vertex_auto_trigger
            vertex_auto_trigger(
                'prism.service.complete',
                source_record_id=order['id'],
                data={
                    'client_name': order.get('client', ''),
                    'client_email': order.get('client_email', ''),
                    'service_type': order.get('service_label', order.get('type', '')),
                    'amount': order_total,
                    'payment_method': payment_method,
                    'billing_tier': billing_tier,
                    'override_code': override_code,
                },
            )
        except Exception as e:
            import logging
            logging.getLogger("prism_billing").warning(f"VERTEX auto-trigger failed: {e}")

    threading.Thread(target=_vertex_invoice, daemon=True).start()

    payload = {'success': True, 'order': order}
    if nemt_order_id:
        payload['nemt_order_id'] = nemt_order_id
        payload['nemt_linked'] = True
    return jsonify(payload), 201


def _portal_hidden_statuses():
    return {'cancelled', 'canceled', 'deleted', 'void', 'voided'}


def _portal_order_hidden(order: dict) -> bool:
    s = (order.get('status') or '').lower().replace(' ', '_')
    return s in _portal_hidden_statuses()


def _portal_order_status(status):
    """Map PRISM ops status → client portal bucket."""
    s = (status or 'New').lower().replace(' ', '_')
    if s in _portal_hidden_statuses():
        return 'cancelled'
    if s in ('complete', 'completed', 'closed', 'verified', 'documentation'):
        return 'completed'
    if s in ('in_progress', 'assigned', 'dispatched', 'driver_assigned',
             'agent_assigned', 'en_route', 'arrived', 'departed'):
        return 'in_progress'
    if s in ('confirmed', 'scheduled', 'order_validated', 'validated'):
        return 'scheduled'
    return 'pending'


def _order_portal_emails(order: dict) -> set:
    """Emails that may log into portal.deedavis.biz for this order."""
    out = set()
    for key in ('client_email', 'subject_email'):
        e = (order.get(key) or '').strip().lower()
        if e and '@' in e:
            out.add(e)
    return out


def sync_prism_order_status(
    prism_order_id: str,
    status: str,
    *,
    notify: bool = True,
    details_patch: Optional[dict] = None,
) -> bool:
    """
    Push ops milestone to PRISM orders.json so portal.deedavis.biz dashboard
    and SMS/email notifications stay in sync with NEMT dispatch workflow.
    Bypasses PATCH QC gate for automated NEMT completion paths.
    """
    pid = (prism_order_id or '').strip()
    if not pid or not status:
        return False
    try:
        orders = _load(ORDERS_FILE, [])
        for i, o in enumerate(orders):
            if o.get('id') != pid:
                continue
            orders[i]['status'] = status
            orders[i]['updated_at'] = datetime.now().isoformat()
            if details_patch:
                details = dict(orders[i].get('details') or {})
                details.update(details_patch)
                orders[i]['details'] = details
            _save(ORDERS_FILE, orders)
            if notify:
                _fire_status_notification(orders[i], status)
            return True
        return False
    except Exception as exc:
        print(f'PRISM order status sync skipped: {exc}')
        return False


def _nemt_ride_tracking_for_prism_order(prism_order_id: str, details: dict) -> dict:
    """Resolve guest ride tracking URL from PRISM details or linked NEMT ops order."""
    url = (details.get('ride_tracking_url') or '').strip()
    platform = (details.get('ride_tracking_platform') or '').strip()
    if url:
        return {'ride_tracking_url': url, 'ride_tracking_platform': platform}
    pid = (prism_order_id or '').strip()
    if not pid:
        return {}
    try:
        from prism_nemt import find_nemt_order_by_prism_id

        nemt = find_nemt_order_by_prism_id(pid)
        if not nemt:
            return {}
        url = (nemt.get('rider_tracking_url') or '').strip()
        if not url:
            return {}
        return {
            'ride_tracking_url': url,
            'ride_tracking_platform': (
                nemt.get('fulfillment_platform') or platform
            ),
        }
    except Exception:
        return {}


def _order_to_portal_view(order):
    """Shape stored order for PRISM client intake dashboard / calendar."""
    raw_status = order.get('status', '')
    details = order.get('details') or {}
    signer = (order.get('signer') or '').strip()
    parts = signer.split(None, 1) if signer else []
    first = parts[0] if parts else ''
    last = parts[1] if len(parts) > 1 else ''
    pickup = (
        details.get('pickup_address')
        or order.get('address', '')
        or ''
    ).strip()
    dropoff = (
        details.get('dropoff_address')
        or order.get('collection_site', '')
        or ''
    ).strip()
    svc_key = (order.get('service_key') or order.get('type') or '').lower()
    tracking = _nemt_ride_tracking_for_prism_order(order.get('id', ''), details)
    ride_tracking_url = tracking.get('ride_tracking_url', '')
    ride_tracking_platform = tracking.get('ride_tracking_platform', '')
    portal_status = _portal_order_status(raw_status)
    return {
        'id': order.get('id', ''),
        'type': order.get('type') or order.get('service_key', ''),
        'service_key': order.get('service_key', ''),
        'service_label': order.get('service_label', ''),
        'subject': signer or '—',
        'subject_first': first,
        'subject_last': last,
        'subject_dob': order.get('subject_dob', ''),
        'subject_phone': order.get('subject_phone', ''),
        'subject_email': order.get('subject_email', ''),
        'subject_id': order.get('subject_id', '') or details.get('member_id', ''),
        'pickup_address': pickup,
        'dropoff_address': dropoff,
        'nemt_program': details.get('program_type') or details.get('mobility_lane') or '',
        'nemt_trip_type': details.get('trip_type', ''),
        'nemt_purpose': details.get('appointment_purpose', ''),
        'nemt_leg_type': details.get('leg_type', ''),
        'client_company': order.get('client', ''),
        'client_contact': order.get('client_contact', ''),
        'client_phone': order.get('client_phone', ''),
        'date': order.get('date', ''),
        'time': order.get('time', ''),
        'timezone': order.get('timezone', ''),
        'location': dropoff or pickup or order.get('collection_site') or order.get('address', ''),
        'status': portal_status,
        'ops_status': raw_status,
        'priority': order.get('priority', 'Standard'),
        'result': order.get('result', ''),
        'created_at': order.get('created_at', ''),
        'updated_at': order.get('updated_at', ''),
        'rebook_eligible': svc_key in ('nemt', 'transport'),
        'rebook_source_id': details.get('rebook_source_id', ''),
        'rebook_mode': details.get('rebook_mode', ''),
        'nemt_order_id': details.get('nemt_order_id', ''),
        'ride_tracking_url': ride_tracking_url,
        'ride_tracking_platform': ride_tracking_platform,
        'ride_tracking_active': bool(
            ride_tracking_url
            and portal_status in ('scheduled', 'pending', 'in_progress')
        ),
    }


# ═══════════════════════════════════════════════════════════════════
# GET /prism/orders/my  —  Orders for logged-in client (by email)
# ═══════════════════════════════════════════════════════════════════

@prism_orders.route('/prism/orders/my', methods=['GET'])
def my_orders():
    email = (request.args.get('email') or '').strip().lower()
    if not email or '@' not in email:
        return jsonify({'error': 'Valid email required'}), 400

    json_orders = _load(ORDERS_FILE, [])
    mine_json = [
        o for o in json_orders
        if email in _order_portal_emails(o) and not _portal_order_hidden(o)
    ]
    portal_json = [_order_to_portal_view(o) for o in mine_json]

    portal_airtable = []
    try:
        from prism_airtable_intake import fetch_portal_orders_by_email, merge_portal_orders
        portal_airtable = fetch_portal_orders_by_email(email)
        portal = merge_portal_orders(portal_airtable, portal_json)
    except Exception as e:
        print(f'PRISM Airtable my_orders fallback to JSON: {e}')
        portal = portal_json

    portal.sort(key=lambda x: str(x.get('created_at', '')), reverse=True)
    return jsonify({
        'orders': portal,
        'total': len(portal),
        'email': email,
        'sources': {
            'airtable': len(portal_airtable),
            'json': len(portal_json),
        },
    })


# ═══════════════════════════════════════════════════════════════════
# GET /prism/orders  —  List all orders
# ═══════════════════════════════════════════════════════════════════

@prism_orders.route('/prism/orders', methods=['GET'])
def list_orders():
    orders = _load(ORDERS_FILE, [])

    status = request.args.get('status')
    if status:
        orders = [o for o in orders if o.get('status', '').lower() == status.lower()]

    svc = request.args.get('type')
    if svc:
        orders = [o for o in orders if o.get('type', '').lower() == svc.lower()]

    return jsonify({'orders': orders, 'total': len(orders)})


# ═══════════════════════════════════════════════════════════════════
# GET /prism/orders/<id>  —  Single order detail
# ═══════════════════════════════════════════════════════════════════

@prism_orders.route('/prism/orders/<order_id>', methods=['GET'])
def get_order(order_id):
    orders = _load(ORDERS_FILE, [])
    order = next((o for o in orders if o['id'] == order_id), None)
    if not order:
        return jsonify({'error': 'Order not found'}), 404
    return jsonify({'order': order})


# ═══════════════════════════════════════════════════════════════════
# PATCH /prism/orders/<id>  —  Update status, assign agent, etc.
# ═══════════════════════════════════════════════════════════════════

@prism_orders.route('/prism/orders/<order_id>', methods=['DELETE'])
def delete_order(order_id):
    """Remove PRISM intake order and cancel linked NEMT trip (ops cleanup)."""
    orders = _load(ORDERS_FILE, [])
    idx = next((i for i, o in enumerate(orders) if o['id'] == order_id), None)
    if idx is None:
        return jsonify({'error': 'Order not found'}), 404

    order = orders[idx]
    nemt_cancelled = False
    nemt_order_id = (order.get('details') or {}).get('nemt_order_id')
    try:
        from prism_nemt import cancel_nemt_order_for_prism

        nemt_cancelled = cancel_nemt_order_for_prism(order_id)
    except Exception as exc:
        print(f'NEMT cancel on delete skipped: {exc}')

    removed = orders.pop(idx)
    _save(ORDERS_FILE, orders)

    return jsonify({
        'success': True,
        'deleted': order_id,
        'nemt_cancelled': nemt_cancelled,
        'nemt_order_id': nemt_order_id,
        'order': removed,
    })


@prism_orders.route('/prism/orders/<order_id>', methods=['PATCH'])
def update_order(order_id):
    orders = _load(ORDERS_FILE, [])
    idx = next((i for i, o in enumerate(orders) if o['id'] == order_id), None)
    if idx is None:
        return jsonify({'error': 'Order not found'}), 404

    data = request.get_json(silent=True) or {}

    new_status = data.get('status', '').strip()
    if new_status.lower() in ('complete', 'completed'):
        if not _qc_gate_passed(orders[idx]):
            fatal_open = [
                item['id'] for item in orders[idx].get('qc_checklist', [])
                if item['severity'] == 'FATAL' and not item['completed']
            ]
            return jsonify({
                'error': 'QC GATE BLOCKED — FATAL checklist items not completed',
                'fatal_items_open': fatal_open,
                'message': f'{len(fatal_open)} mandatory QC item(s) must be checked before completing this order',
            }), 422

    allowed = ['status', 'agent', 'fee', 'notes', 'date', 'time', 'priority', 'address', 'collection_site']
    for key in allowed:
        if key in data:
            orders[idx][key] = data[key]

    checklist = orders[idx].get('qc_checklist', [])
    if checklist:
        total = len(checklist)
        done = sum(1 for c in checklist if c['completed'])
        fatal_total = sum(1 for c in checklist if c['severity'] == 'FATAL')
        fatal_done = sum(1 for c in checklist if c['severity'] == 'FATAL' and c['completed'])
        orders[idx]['qc_status'] = 'passed' if fatal_done == fatal_total else ('in_progress' if done > 0 else 'pending')
        orders[idx]['qc_progress'] = round(done / total * 100) if total else 0

    _evaluate_auto_gates(orders[idx])
    orders[idx]['updated_at'] = datetime.now().isoformat()
    _save(ORDERS_FILE, orders)

    if new_status and new_status.lower() in ('complete', 'completed'):
        _fire_pipeline_event('order_completed', orders[idx])
        _fire_status_notification(orders[idx], 'Complete')
    elif new_status:
        _fire_pipeline_event('order_status_changed', orders[idx], {'new_status': new_status})
        _fire_status_notification(orders[idx], new_status)

    # Re-schedule day-of reminder if date/time was updated
    if 'date' in data or 'time' in data:
        _fire_dayon_reminder(orders[idx])
        # Re-send reschedule confirmation to subject
        _send_confirmation_async(orders[idx])

    return jsonify({'success': True, 'order': orders[idx]})


# ═══════════════════════════════════════════════════════════════════
# PATCH /prism/orders/<id>/gate  —  Clear a workflow gate
# ═══════════════════════════════════════════════════════════════════

@prism_orders.route('/prism/orders/<order_id>/gate', methods=['PATCH'])
def clear_gate(order_id):
    """
    Body: { "gate_id": "G-DOT-1", "agent": "Dee Davis" }
    Or batch: { "gates": ["G-DOT-1", "G-DOT-2"], "agent": "Dee Davis" }
    Clears manual gates so the order can advance.
    """
    orders = _load(ORDERS_FILE, [])
    idx = next((i for i, o in enumerate(orders) if o['id'] == order_id), None)
    if idx is None:
        return jsonify({'error': 'Order not found'}), 404

    data = request.get_json(silent=True) or {}
    agent_name = data.get('agent', 'System')
    now_iso = datetime.now().isoformat()

    gate_ids = data.get('gates', [])
    if not gate_ids and 'gate_id' in data:
        gate_ids = [data['gate_id']]

    cleared = []
    workflow = orders[idx].get('workflow', [])
    for stage in workflow:
        for gate in stage.get('gates', []):
            if gate['id'] in gate_ids:
                gate['passed'] = True
                gate['passed_by'] = agent_name
                gate['passed_at'] = now_iso
                cleared.append(gate['id'])

    orders[idx]['workflow'] = workflow
    _evaluate_auto_gates(orders[idx])
    orders[idx]['updated_at'] = now_iso
    _save(ORDERS_FILE, orders)

    return jsonify({
        'success': True,
        'cleared': cleared,
        'workflow_stage': orders[idx]['workflow_stage'],
        'workflow_stage_label': orders[idx]['workflow_stage_label'],
        'status': orders[idx]['status'],
        'order': orders[idx],
    })


# ═══════════════════════════════════════════════════════════════════
# PATCH /prism/orders/<id>/qc  —  Check off / uncheck QC items
# ═══════════════════════════════════════════════════════════════════

@prism_orders.route('/prism/orders/<order_id>/qc', methods=['PATCH'])
def update_qc_checklist(order_id):
    """
    Body: { "item_id": "DOT-1", "completed": true, "agent": "Dee Davis" }
    Or batch: { "items": [{ "item_id": "DOT-1", "completed": true }, ...], "agent": "Dee Davis" }
    """
    orders = _load(ORDERS_FILE, [])
    idx = next((i for i, o in enumerate(orders) if o['id'] == order_id), None)
    if idx is None:
        return jsonify({'error': 'Order not found'}), 404

    data = request.get_json(silent=True) or {}
    agent_name = data.get('agent', 'System')
    now_iso = datetime.now().isoformat()

    items_to_update = data.get('items', [])
    if not items_to_update and 'item_id' in data:
        items_to_update = [{'item_id': data['item_id'], 'completed': data.get('completed', True)}]

    checklist = orders[idx].get('qc_checklist', [])
    if not checklist:
        checklist = _build_qc_checklist(orders[idx].get('type', 'notary'))
        orders[idx]['qc_checklist'] = checklist

    updated_ids = []
    for update in items_to_update:
        item_id = update.get('item_id')
        completed = update.get('completed', True)
        for item in checklist:
            if item['id'] == item_id:
                item['completed'] = completed
                item['completed_by'] = agent_name if completed else None
                item['completed_at'] = now_iso if completed else None
                updated_ids.append(item_id)
                break

    total = len(checklist)
    done = sum(1 for c in checklist if c['completed'])
    fatal_total = sum(1 for c in checklist if c['severity'] == 'FATAL')
    fatal_done = sum(1 for c in checklist if c['severity'] == 'FATAL' and c['completed'])

    orders[idx]['qc_checklist'] = checklist
    orders[idx]['qc_status'] = 'passed' if fatal_done == fatal_total else ('in_progress' if done > 0 else 'pending')
    orders[idx]['qc_progress'] = round(done / total * 100) if total else 0

    _evaluate_auto_gates(orders[idx])
    orders[idx]['updated_at'] = now_iso
    _save(ORDERS_FILE, orders)

    return jsonify({
        'success': True,
        'updated': updated_ids,
        'qc_progress': orders[idx]['qc_progress'],
        'qc_status': orders[idx]['qc_status'],
        'fatal_complete': fatal_done == fatal_total,
        'fatal_remaining': fatal_total - fatal_done,
        'workflow_stage': orders[idx].get('workflow_stage', 0),
        'workflow_stage_label': orders[idx].get('workflow_stage_label', ''),
        'order': orders[idx],
    })


# ═══════════════════════════════════════════════════════════════════
# SCANBACK — Document Verification System
# ═══════════════════════════════════════════════════════════════════

SERVICE_EXPECTED_DOCS = {
    'dot':             {'pages': 3, 'docs': ['CCF (Copy 1 – Lab)', 'CCF (Copy 4 – Employer)', 'Photo ID Verification']},
    'non-dot':         {'pages': 2, 'docs': ['Chain of Custody Form', 'Photo ID Verification']},
    'dna':             {'pages': 3, 'docs': ['DNA Collection Form', 'Chain of Custody', 'Consent Form']},
    'fingerprint':     {'pages': 2, 'docs': ['Fingerprint Capture Confirmation', 'Photo ID Verification']},
    'background':      {'pages': 2, 'docs': ['Signed Authorization/Consent', 'Photo ID Verification']},
    'notary':          {'pages': 2, 'docs': ['Notarized Document Scan', 'Notary Journal Entry']},
    'ron':             {'pages': 3, 'docs': ['Notarized Document Scan', 'Recording Confirmation', 'ID Verification Screenshot']},
    'apostille':       {'pages': 2, 'docs': ['Apostille Certificate Scan', 'Original Document Scan']},
    'process':         {'pages': 2, 'docs': ['Proof of Service / Affidavit', 'Photo Evidence']},
    'nemt':            {'pages': 2, 'docs': ['Trip Log / Manifest', 'Passenger Signature Form']},
    'community_transition': {'pages': 5, 'docs': ['Referral Documentation', 'PCSP Confirmation', 'Supporting Invoice/Quote per Expense Item', 'Home Assessment Report (if required)', 'Authorization Sign-Off Record']},
    'medical_courier': {'pages': 2, 'docs': ['Chain of Custody / Manifest', 'Delivery Confirmation']},
    'courier':         {'pages': 1, 'docs': ['Delivery Confirmation / POD']},
    'phlebotomy':      {'pages': 2, 'docs': ['Collection Form', 'Photo ID Verification']},
}


@prism_orders.route('/prism/scanbacks', methods=['GET'])
def list_scanbacks():
    """Return all orders that have reached documentation stage or have scanback data."""
    orders = _load(ORDERS_FILE, [])
    scanbacks = []
    for o in orders:
        sb = o.get('scanback')
        stage = o.get('workflow_stage', 0)
        if sb or stage >= 6:
            svc = o.get('type', 'notary')
            expected = SERVICE_EXPECTED_DOCS.get(svc, {'pages': 1, 'docs': []})
            uploads = sb.get('uploads', []) if sb else []
            latest = uploads[-1] if uploads else None
            scanbacks.append({
                'id': f"SB-{o['id']}",
                'orderId': o['id'],
                'type': svc,
                'agent': o.get('agent', 'Unassigned'),
                'client': o.get('client', ''),
                'signer': o.get('signer', ''),
                'status': sb.get('status', 'Awaiting Upload') if sb else 'Awaiting Upload',
                'pages': latest.get('pages', 0) if latest else 0,
                'expected': expected['pages'],
                'expectedDocs': expected['docs'],
                'uploadDate': latest.get('uploaded_at', '') if latest else '',
                'attempt': len(uploads),
                'errors': latest.get('errors', []) if latest else [],
                'reviewed_by': sb.get('reviewed_by') if sb else None,
                'reviewed_at': sb.get('reviewed_at') if sb else None,
            })
    return jsonify({'scanbacks': scanbacks, 'total': len(scanbacks)})


@prism_orders.route('/prism/orders/<order_id>/scanback', methods=['POST'])
def submit_scanback(order_id):
    """Agent submits documents for an order.
    Body: { "pages": 3, "files": ["ccf.pdf", "id.jpg"], "agent": "Dee Davis" }
    """
    orders = _load(ORDERS_FILE, [])
    idx = next((i for i, o in enumerate(orders) if o['id'] == order_id), None)
    if idx is None:
        return jsonify({'error': 'Order not found'}), 404

    data = request.get_json(silent=True) or {}
    now_iso = datetime.now().isoformat()

    if 'scanback' not in orders[idx]:
        orders[idx]['scanback'] = {'status': 'Awaiting Upload', 'uploads': []}

    sb = orders[idx]['scanback']
    upload = {
        'attempt': len(sb['uploads']) + 1,
        'uploaded_at': now_iso,
        'uploaded_by': data.get('agent', 'Unknown'),
        'pages': data.get('pages', 0),
        'files': data.get('files', []),
        'errors': [],
    }
    sb['uploads'].append(upload)
    sb['status'] = 'Needs Review'

    auto_qc = _auto_run_compliance_checks(orders[idx])

    # Auto-verify against signature map if one exists for this order
    sig_verify = None
    images_b64 = data.get('images_b64', [])
    if images_b64:
        try:
            from prism_document_ai import verify_signatures_against_map, load_signature_map
            existing_map = load_signature_map(order_id)
            if existing_map:
                sig_verify = verify_signatures_against_map(
                    images_b64=images_b64,
                    order_id=order_id,
                    sig_map=existing_map,
                )
                orders[idx]['signature_verification'] = {
                    'all_satisfied': sig_verify.get('all_satisfied', False),
                    'has_fatal_errors': sig_verify.get('has_fatal_errors', False),
                    'error_count': len(sig_verify.get('errors', [])),
                    'warning_count': len(sig_verify.get('warnings', [])),
                    'verified_at': sig_verify.get('verified_at', ''),
                }
                # Append signature errors to the upload record
                sig_errors = sig_verify.get('errors', []) + sig_verify.get('warnings', [])
                if sig_errors:
                    if sb['uploads'][-1].get('errors') is None:
                        sb['uploads'][-1]['errors'] = []
                    sb['uploads'][-1]['errors'].extend(sig_errors)
                if sig_verify.get('has_fatal_errors'):
                    auto_qc['fatal_flags'].extend([
                        e['description'] for e in sig_verify.get('errors', []) if e.get('fatal')
                    ])
        except ImportError:
            pass

    _evaluate_auto_gates(orders[idx])
    orders[idx]['updated_at'] = now_iso
    _save(ORDERS_FILE, orders)

    return jsonify({
        'success': True,
        'scanback': sb,
        'auto_qc': auto_qc,
        'signature_verification': sig_verify,
        'order': orders[idx],
    })


@prism_orders.route('/prism/orders/<order_id>/scanback/review', methods=['PATCH'])
def review_scanback(order_id):
    """Admin reviews a scanback: mark clean or flag errors.
    Body: { "action": "clean" | "errors", "errors": [...], "reviewer": "Dee Davis" }
    """
    orders = _load(ORDERS_FILE, [])
    idx = next((i for i, o in enumerate(orders) if o['id'] == order_id), None)
    if idx is None:
        return jsonify({'error': 'Order not found'}), 404

    sb = orders[idx].get('scanback')
    if not sb or not sb.get('uploads'):
        return jsonify({'error': 'No scanback submitted yet'}), 422

    data = request.get_json(silent=True) or {}
    action = data.get('action', 'clean')
    reviewer = data.get('reviewer', 'Admin')
    now_iso = datetime.now().isoformat()

    if action == 'clean':
        sb['status'] = 'Clean'
        sb['reviewed_by'] = reviewer
        sb['reviewed_at'] = now_iso
        if sb['uploads']:
            sb['uploads'][-1]['errors'] = []
    elif action == 'errors':
        sb['status'] = 'Errors Found'
        sb['reviewed_by'] = reviewer
        sb['reviewed_at'] = now_iso
        if sb['uploads']:
            sb['uploads'][-1]['errors'] = data.get('errors', [])

    _evaluate_auto_gates(orders[idx])
    orders[idx]['updated_at'] = now_iso
    _save(ORDERS_FILE, orders)

    if action == 'clean':
        _fire_pipeline_event('scanback_clean', orders[idx])
    else:
        _fire_pipeline_event('scanback_errors', orders[idx], {'error_count': len(data.get('errors', []))})

    # Tier 3: Record QC outcome for agent quality profiling
    agent_name = orders[idx].get('agent', '')
    if agent_name:
        try:
            from prism_qc_learning import record_qc_outcome
            record_qc_outcome(
                agent_name=agent_name,
                order_id=order_id,
                service_type=orders[idx].get('type', ''),
                outcome='clean' if action == 'clean' else 'errors',
                errors=data.get('errors') if action == 'errors' else None,
            )
        except ImportError:
            pass

    return jsonify({'success': True, 'scanback': sb, 'order': orders[idx]})


@prism_orders.route('/prism/orders/<order_id>/signature-map', methods=['POST'])
def create_order_signature_map(order_id):
    """Attach a signature reference map to an order.
    Call when the reference document arrives from escrow / title / lender.

    Body: {
      images_b64: ["<page1_base64>", ...],
      document_type: "Deed of Trust",
      document_context: "Michigan closing, 2 buyers"
    }
    """
    orders = _load(ORDERS_FILE, [])
    idx = next((i for i, o in enumerate(orders) if o['id'] == order_id), None)
    if idx is None:
        return jsonify({'error': 'Order not found'}), 404

    data = request.get_json(silent=True) or {}
    images_b64 = data.get('images_b64', [])
    if not images_b64:
        return jsonify({'error': 'images_b64 is required'}), 400

    try:
        from prism_document_ai import map_document_signatures
        sig_map = map_document_signatures(
            images_b64=images_b64,
            order_id=order_id,
            document_type=data.get('document_type', ''),
            document_context=data.get('document_context', ''),
        )
    except ImportError:
        return jsonify({'error': 'Document AI module not available'}), 503

    orders[idx]['signature_map_attached'] = True
    orders[idx]['signature_map_requirements'] = sig_map.get('total_requirements', 0)
    orders[idx]['signature_map_document_type'] = data.get('document_type', '')
    orders[idx]['updated_at'] = datetime.now().isoformat()
    _save(ORDERS_FILE, orders)

    return jsonify({
        'success': True,
        'order_id': order_id,
        'signature_map': sig_map,
    })


@prism_orders.route('/prism/orders/<order_id>/signature-map', methods=['GET'])
def get_order_signature_map(order_id):
    """Return the stored signature map for an order."""
    try:
        from prism_document_ai import load_signature_map
        sig_map = load_signature_map(order_id)
    except ImportError:
        return jsonify({'error': 'Document AI module not available'}), 503

    if not sig_map:
        return jsonify({'error': 'No signature map found for this order'}), 404
    return jsonify(sig_map)


@prism_orders.route('/prism/orders/<order_id>/auto-qc', methods=['POST'])
def run_auto_qc(order_id):
    """On-demand automated QC check for an order.
    Re-runs fatal flaw detection, page count, and temporal compliance."""
    orders = _load(ORDERS_FILE, [])
    idx = next((i for i, o in enumerate(orders) if o['id'] == order_id), None)
    if idx is None:
        return jsonify({'error': 'Order not found'}), 404

    auto_qc = _auto_run_compliance_checks(orders[idx])
    _evaluate_auto_gates(orders[idx])
    orders[idx]['updated_at'] = datetime.now().isoformat()
    _save(ORDERS_FILE, orders)

    return jsonify({
        'success': True,
        'auto_qc': auto_qc,
        'order': orders[idx],
    })


# ═══════════════════════════════════════════════════════════════════
# FIELD OPS — REO & Mortgage Field Service Work Orders
# ═══════════════════════════════════════════════════════════════════

FIELD_OPS_FILE = os.path.join(DATA_DIR, 'field_ops.json')


@prism_orders.route('/prism/fieldops', methods=['GET'])
def list_field_ops():
    """Return all property work orders with optional status/program filter."""
    wos = _load(FIELD_OPS_FILE, [])
    status = request.args.get('status')
    program = request.args.get('program')
    if status:
        wos = [w for w in wos if w.get('status') == status]
    if program:
        wos = [w for w in wos if w.get('program') == program]
    return jsonify({'work_orders': wos, 'total': len(wos)})


@prism_orders.route('/prism/fieldops', methods=['POST'])
def create_field_op():
    """Create a new property work order."""
    data = request.get_json(silent=True) or {}
    wos = _load(FIELD_OPS_FILE, [])
    now_iso = datetime.now().isoformat()
    seq = len(wos) + 1
    wo = {
        'id': f"FO-2026-{seq:03d}",
        'property_address': data.get('property_address', ''),
        'city': data.get('city', ''),
        'state': data.get('state', 'MI'),
        'zip': data.get('zip', ''),
        'property_type': data.get('property_type', 'single_family'),
        'program': data.get('program', 'hud_fsm'),
        'service_type': data.get('service_type', 'occupancy_check'),
        'status': 'new',
        'priority': data.get('priority', 'standard'),
        'assigned_to': data.get('assigned_to', ''),
        'vendor_source': data.get('vendor_source', 'ddi_direct'),
        'photos_required': data.get('photos_required', 6),
        'photos_submitted': 0,
        'condition_code': '',
        'due_date': data.get('due_date', ''),
        'recurring': data.get('recurring', False),
        'recurring_freq': data.get('recurring_freq', ''),
        'fee': data.get('fee', 0),
        'notes': data.get('notes', ''),
        'created_at': now_iso,
    }
    wos.append(wo)
    _save(FIELD_OPS_FILE, wos)
    return jsonify({'success': True, 'work_order': wo}), 201


@prism_orders.route('/prism/fieldops/<wo_id>', methods=['PATCH'])
def update_field_op(wo_id):
    """Update a property work order (status, photos, assignment, etc.)."""
    wos = _load(FIELD_OPS_FILE, [])
    idx = next((i for i, w in enumerate(wos) if w['id'] == wo_id), None)
    if idx is None:
        return jsonify({'error': 'Work order not found'}), 404
    data = request.get_json(silent=True) or {}
    allowed = ['status', 'assigned_to', 'vendor_source', 'photos_submitted',
               'condition_code', 'priority', 'notes', 'fee', 'due_date']
    for k in allowed:
        if k in data:
            wos[idx][k] = data[k]
    wos[idx]['updated_at'] = datetime.now().isoformat()
    _save(FIELD_OPS_FILE, wos)
    return jsonify({'success': True, 'work_order': wos[idx]})


# ═══════════════════════════════════════════════════════════════════
# GET /prism/agents  —  List field agents
# ═══════════════════════════════════════════════════════════════════

@prism_orders.route('/prism/agents', methods=['GET'])
def list_agents():
    agents = _load(AGENTS_FILE, [])
    if not agents:
        agents = [
            {'id': 'AGT-001', 'name': 'Dee Davis', 'specialties': ['notary', 'ron', 'fingerprint', 'dna', 'dot', 'non-dot'], 'status': 'Active', 'city': 'Troy', 'state': 'MI', 'completionRate': 100, 'onTimeRate': 100, 'errorRate': 0, 'rating': 5.0, 'ordersCompleted': 0, 'activeOrders': 0},
        ]
        _save(AGENTS_FILE, agents)
    return jsonify({'agents': agents})


# ═══════════════════════════════════════════════════════════════════
# GET /prism/clients  —  List clients
# ═══════════════════════════════════════════════════════════════════

@prism_orders.route('/prism/clients', methods=['GET'])
def list_clients():
    clients = _load(CLIENTS_FILE, [])
    if not clients:
        orders = _load(ORDERS_FILE, [])
        client_map = {}
        for o in orders:
            name = o.get('client', '')
            if name and name not in client_map:
                client_map[name] = {
                    'id': f'CLT-{uuid.uuid4().hex[:6].upper()}',
                    'name': name,
                    'type': 'Employer',
                    'services': [o.get('type', '')],
                    'orders': 0,
                    'revenue': 0,
                    'status': 'Active',
                    'retainer': 0,
                }
            if name in client_map:
                client_map[name]['orders'] += 1
                client_map[name]['revenue'] += o.get('fee', 0)
                if o.get('type') not in client_map[name]['services']:
                    client_map[name]['services'].append(o['type'])
        clients = list(client_map.values())
        if clients:
            _save(CLIENTS_FILE, clients)
    return jsonify({'clients': clients})


# ═══════════════════════════════════════════════════════════════════
# PRISM BILLING — VERTEX Integration
# ═══════════════════════════════════════════════════════════════════

BILLING_OVERRIDE_FILE = os.path.join(DATA_DIR, 'billing_overrides.json')

def _get_airtable():
    """Lazy import to avoid circular deps."""
    try:
        from nexus_backend import AirtableClient
        return AirtableClient()
    except Exception:
        return None


def _get_vertex_client_by_email(email):
    """Look up a VERTEX Client record by email. Returns dict or None."""
    at = _get_airtable()
    if not at:
        return None
    try:
        formula = f"LOWER({{EMAIL}})='{email.lower()}'"
        records = at.search_records("VERTEX CLIENTS", formula)
        if records:
            return records[0]
    except Exception as e:
        import logging
        logging.getLogger("prism_billing").warning(f"VERTEX client lookup failed: {e}")
    return None


@prism_orders.route('/prism/billing/lookup', methods=['GET'])
def billing_lookup():
    """
    Look up billing tier for a client email.
    Returns: billing tier (contract / card_on_file / pay_at_booking),
    contract details, card on file status, and open invoices.
    """
    email = (request.args.get('email') or '').strip().lower()
    if not email:
        return jsonify({'error': 'Email required'}), 400

    vc = _get_vertex_client_by_email(email)
    if not vc:
        return jsonify({
            'found': False,
            'billing': {
                'tier': 'pay_at_booking',
                'contract_id': None,
                'contract_name': None,
                'payment_terms': 'Due on Receipt',
                'card_on_file': None,
                'autopay': False,
            }
        })

    fields = vc.get('fields', {})
    payment_terms = fields.get('PAYMENT TERMS', 'Due on Receipt')
    client_name = fields.get('CLIENT NAME', '')
    contact_name = (fields.get('CONTACT NAME') or '').strip()
    contact_phone = (fields.get('PHONE') or '').strip()

    # Determine billing tier from payment terms
    is_contract = payment_terms in ('Net 15', 'Net 30', 'Net 45', 'Net 60')

    # Check for contract linkage
    contract_id = None
    contract_name = None
    try:
        at = _get_airtable()
        if at and is_contract:
            c_formula = f"AND(FIND('{client_name}',{{CLIENT NAME}}),{{STATUS}}='Active')"
            try:
                contracts = at.search_records("NEXUS CONTRACTS", c_formula)
                if contracts:
                    cf = contracts[0].get('fields', {})
                    contract_id = cf.get('CONTRACT NUMBER', cf.get('CONTRACT ID', ''))
                    contract_name = cf.get('TITLE', cf.get('CONTRACT NAME', ''))
            except Exception:
                pass
    except Exception:
        pass

    # Check for card on file (stored in VERTEX CLIENTS NOTES as JSON or dedicated field)
    card_on_file = None
    card_data = fields.get('CARD ON FILE', '') or fields.get('NOTES', '')
    if card_data and 'card_on_file' in str(card_data).lower():
        try:
            parsed = json.loads(card_data) if isinstance(card_data, str) else card_data
            if isinstance(parsed, dict) and parsed.get('card_on_file'):
                card_on_file = parsed['card_on_file']
        except (json.JSONDecodeError, TypeError):
            pass

    autopay = 'autopay' in str(fields.get('NOTES', '')).lower()

    if is_contract:
        tier = 'contract'
    elif card_on_file:
        tier = 'card_on_file'
    else:
        tier = 'pay_at_booking'

    # Pull open invoices from VERTEX
    open_invoices = []
    try:
        at = _get_airtable()
        if at:
            inv_formula = f"AND({{CLIENT NAME}}='{client_name}',OR({{PAYMENT STATUS}}='Unpaid',{{PAYMENT STATUS}}='Partial',{{PAYMENT STATUS}}='Overdue'))"
            invs = at.search_records("VERTEX INVOICES", inv_formula)
            for inv in invs:
                inf = inv.get('fields', {})
                open_invoices.append({
                    'id': inf.get('INVOICE NUMBER', inv.get('id', '')),
                    'amount': inf.get('TOTAL AMOUNT', 0),
                    'status': inf.get('PAYMENT STATUS', 'Unpaid'),
                    'date': inf.get('INVOICE DATE', ''),
                    'due': inf.get('DUE DATE', ''),
                })
    except Exception:
        pass

    return jsonify({
        'found': True,
        'client_name': client_name,
        'contact_name': contact_name,
        'contact_phone': contact_phone,
        'record_id': vc.get('id'),
        'billing': {
            'tier': tier,
            'contract_id': contract_id,
            'contract_name': contract_name,
            'payment_terms': payment_terms,
            'card_on_file': card_on_file,
            'autopay': autopay,
        },
        'open_invoices': open_invoices,
    })


def _normalize_prism_vertex_invoice(rec: dict) -> dict:
    """Flatten Airtable VERTEX INVOICES row for PRISM payments UI."""
    from api_server import VI

    fields = rec.get('fields') or {}
    record_id = rec.get('id') or ''
    total = float(fields.get(VI['total_amount']) or 0)
    paid = float(fields.get(VI['amount_paid']) or 0)
    balance = fields.get(VI['balance_due'])
    if balance is None or balance == '':
        balance = max(0.0, total - paid)
    else:
        balance = float(balance)

    notes_raw = fields.get(VI['notes']) or ''
    is_nemt = False
    try:
        notes_obj = json.loads(notes_raw) if isinstance(notes_raw, str) and notes_raw.strip().startswith('{') else {}
        is_nemt = notes_obj.get('vertex_module') == 'NEMT'
    except (json.JSONDecodeError, TypeError):
        is_nemt = 'NEMT' in str(fields.get(VI['source_system']) or '')

    return {
        'record_id': record_id,
        'invoice_number': fields.get(VI['invoice_number']) or record_id,
        'client_name': fields.get(VI['client_name']) or '',
        'amount': round(total, 2),
        'amount_paid': round(paid, 2),
        'balance_due': round(balance, 2),
        'status': fields.get(VI['payment_status']) or 'Unpaid',
        'date': fields.get(VI['invoice_date']) or '',
        'due_date': fields.get(VI['due_date']) or '',
        'source_system': fields.get(VI['source_system']) or '',
        'payment_terms': fields.get(VI['payment_terms']) or '',
        'pdf_path': f'/vertex/nemt/invoice/{record_id}/pdf' if is_nemt and record_id else None,
    }


def _summarize_prism_invoices(invoices: list) -> dict:
    collected = pending = overdue = 0.0
    for inv in invoices:
        status = str(inv.get('status') or '').lower()
        amt = float(inv.get('amount') or 0)
        paid = float(inv.get('amount_paid') or 0)
        balance = float(inv.get('balance_due') or 0)
        if status == 'paid':
            collected += paid or amt
        elif status == 'overdue':
            overdue += balance or amt
        else:
            pending += balance or max(0.0, amt - paid)
    return {
        'total_billed': round(sum(float(i.get('amount') or 0) for i in invoices), 2),
        'collected': round(collected, 2),
        'pending': round(pending, 2),
        'overdue': round(overdue, 2),
        'count': len(invoices),
    }


@prism_orders.route('/prism/billing/invoices', methods=['GET', 'POST'])
def list_prism_billing_invoices():
    """
    VERTEX invoice details for PRISM Payments tab.
    GET  ?ids=recA,recB&client_names=Name1|Name2
    POST { "ids": [...], "client_names": [...] }
    """
    if request.method == 'POST':
        data = request.get_json(silent=True) or {}
        ids = [str(x).strip() for x in (data.get('ids') or []) if str(x).strip()]
        client_names = [str(x).strip() for x in (data.get('client_names') or []) if str(x).strip()]
    else:
        ids = [x.strip() for x in (request.args.get('ids') or '').split(',') if x.strip()]
        client_names = [x.strip() for x in (request.args.get('client_names') or '').split('|') if x.strip()]

    if not ids and not client_names:
        return jsonify({'invoices': [], 'summary': _summarize_prism_invoices([])})

    at = _get_airtable()
    if not at:
        return jsonify({'error': 'VERTEX/Airtable unavailable', 'invoices': [], 'summary': _summarize_prism_invoices([])}), 503

    from api_server import VI

    by_id: dict = {}

    for record_id in ids:
        try:
            rec = at.get_record('VERTEX INVOICES', record_id)
            if rec:
                by_id[rec.get('id')] = _normalize_prism_vertex_invoice(rec)
        except Exception:
            continue

    if client_names:
        try:
            formulas = [f"FIND('{name.replace(chr(39), chr(39)+chr(39))}',{{{VI['client_name']}}})>0" for name in client_names]
            formula = f"OR({','.join(formulas)})" if len(formulas) > 1 else formulas[0]
            for rec in at.search_records('VERTEX INVOICES', formula):
                rid = rec.get('id')
                if rid:
                    by_id[rid] = _normalize_prism_vertex_invoice(rec)
        except Exception:
            pass

    invoices = sorted(by_id.values(), key=lambda x: x.get('date') or '', reverse=True)
    return jsonify({'invoices': invoices, 'summary': _summarize_prism_invoices(invoices)})


@prism_orders.route('/prism/billing/validate-override', methods=['POST'])
def validate_override():
    """
    Validate a billing override code against VERTEX.
    Override codes are stored in billing_overrides.json or VERTEX REPORTS.
    """
    data = request.get_json(silent=True) or {}
    code = (data.get('code') or '').strip().upper()
    email = (data.get('email') or '').strip().lower()

    if not code:
        return jsonify({'valid': False, 'message': 'Override code required'}), 400

    # Rotating exemption codes (EX-1-MOB-A-2026Q2-WVR-XXXXXX)
    if code.startswith('EX-'):
        from prism_confirmation_ids import (
            confirmation_display_meta,
            validate_exemption_code,
        )

        contract_payer_id = data.get('contract_payer_id')
        lane = data.get('lane') or data.get('mobility_lane')
        order_id = (data.get('order_id') or data.get('confirmation_ref') or '').strip()
        meta = {}
        if order_id and (contract_payer_id is None or not lane):
            orders = _load(ORDERS_FILE, [])
            order = next(
                (o for o in orders if o.get('id') == order_id or o.get('confirmation_ref') == order_id),
                None,
            )
            if order:
                details = order.get('details') or {}
                meta = confirmation_display_meta(order.get('confirmation_ref') or order_id)
                if contract_payer_id is None:
                    contract_payer_id = details.get('contract_payer_id')
                    if contract_payer_id is None and meta.get('contract_payer_id') is not None:
                        contract_payer_id = meta['contract_payer_id']
                if not lane:
                    lane = details.get('mobility_lane') or meta.get('population_lane')

        ex_result = validate_exemption_code(
            code,
            email=email,
            context='billing_override',
            contract_payer_id=contract_payer_id,
            lane=lane,
            mobility_lane=lane,
        )
        if ex_result.get('valid'):
            return jsonify({
                'valid': True,
                'code': code,
                'type': ex_result.get('type', 'exemption'),
                'exemption_type': ex_result.get('exemption_type'),
                'source': 'rotating_exemption',
                'message': ex_result.get('message', 'Exemption accepted.'),
                'uses_remaining': ex_result.get('uses_remaining'),
            })
        return jsonify(ex_result)

    # Check local override file (legacy static codes)
    overrides = _load(BILLING_OVERRIDE_FILE, {})
    if not overrides:
        overrides = {
            'DDI-EXEMPT-2026': {'type': 'global', 'description': 'DDI internal exempt', 'active': True},
            'GOV-CONTRACT': {'type': 'contract', 'description': 'Government contract billing', 'active': True},
            'DDI-WAIVER': {'type': 'waiver', 'description': 'Fee waiver authorized by management', 'active': True},
            'PRISM-OVERRIDE': {'type': 'system', 'description': 'System-level override', 'active': True},
        }
        _save(BILLING_OVERRIDE_FILE, overrides)

    if code in overrides and overrides[code].get('active'):
        override_info = overrides[code]

        # Log override usage to VERTEX REPORTS
        try:
            at = _get_airtable()
            if at:
                at.create_record("VERTEX REPORTS", {
                    "REPORT DATE": datetime.now().date().isoformat(),
                    "REPORT TYPE": "Billing Override Used",
                    "SOURCE SYSTEM": "PRISM",
                    "EVENT TYPE": f"override.{override_info['type']}",
                    "OUTCOME": "Approved",
                    "DETAILS": json.dumps({
                        'code': code,
                        'type': override_info['type'],
                        'email': email,
                        'timestamp': datetime.now().isoformat(),
                    }),
                    "GENERATED BY": "prism_orders_api.py",
                })
        except Exception:
            pass

        return jsonify({
            'valid': True,
            'code': code,
            'type': override_info['type'],
            'message': f'Override accepted — {override_info["description"]}',
        })

    return jsonify({
        'valid': False,
        'code': code,
        'message': f'Code "{code}" not recognized. Contact DDI at {member_care_phone_display()}.',
    })


@prism_orders.route('/prism/billing/create-service-invoice', methods=['POST'])
def create_service_invoice():
    """
    Create a VERTEX invoice when a PRISM service is booked.
    Fires vertex_auto_trigger('prism.service.complete') to create the invoice.
    """
    data = request.get_json(silent=True) or {}
    order_id = data.get('order_id', '')
    client_name = data.get('client_name', '')
    client_email = data.get('client_email', '')
    service_type = data.get('service_type', 'Field Service')
    amount = float(data.get('amount', 0) or 0)
    payment_method = data.get('payment_method', '')
    billing_tier = data.get('billing_tier', 'pay_at_booking')
    override_code = data.get('override_code', '')
    line_items = data.get('line_items', [])

    if amount <= 0:
        return jsonify({'error': 'Amount must be greater than zero'}), 400

    try:
        from vertex_automation import vertex_auto_trigger

        trigger_data = {
            'client_name': client_name,
            'client_email': client_email,
            'service_type': service_type,
            'amount': amount,
            'payment_method': payment_method,
            'billing_tier': billing_tier,
            'override_code': override_code,
            'line_items': line_items,
        }

        # Adjust payment terms based on billing tier
        if billing_tier == 'contract':
            trigger_data['payment_terms'] = 'Net 30'
        elif billing_tier == 'card_on_file':
            trigger_data['payment_terms'] = 'Due on Receipt'
            trigger_data['auto_charge'] = True
        else:
            trigger_data['payment_terms'] = 'Due on Receipt'

        result = vertex_auto_trigger(
            'prism.service.complete',
            source_record_id=order_id,
            data=trigger_data,
        )

        return jsonify({
            'success': True,
            'invoice': result,
            'message': f'VERTEX invoice created for ${amount:.2f}',
        })

    except Exception as e:
        import logging
        logging.getLogger("prism_billing").error(f"VERTEX invoice creation failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Invoice creation failed — will retry on service completion',
        }), 500


@prism_orders.route('/prism/billing/override-codes', methods=['GET'])
def list_override_codes():
    """Admin endpoint: list all active override codes."""
    overrides = _load(BILLING_OVERRIDE_FILE, {})
    return jsonify({'codes': overrides})


@prism_orders.route('/prism/billing/override-codes', methods=['POST'])
def create_override_code():
    """Admin endpoint: create or update an override code."""
    data = request.get_json(silent=True) or {}
    code = (data.get('code') or '').strip().upper()
    if not code:
        return jsonify({'error': 'Code required'}), 400

    overrides = _load(BILLING_OVERRIDE_FILE, {})
    overrides[code] = {
        'type': data.get('type', 'custom'),
        'description': data.get('description', ''),
        'active': data.get('active', True),
        'created': datetime.now().isoformat(),
        'client_email': data.get('client_email', ''),
    }
    _save(BILLING_OVERRIDE_FILE, overrides)
    return jsonify({'success': True, 'code': code, 'override': overrides[code]})


@prism_orders.route('/prism/confirmations/schema', methods=['GET'])
def confirmations_schema():
    """Public reference for confirmation + exemption ID formats."""
    from prism_confirmation_ids import format_schema_public

    return jsonify(format_schema_public())


@prism_orders.route('/prism/confirmations/lookup/<ref>', methods=['GET'])
def confirmations_lookup(ref):
    """Limited public status lookup. Voice bookings require ?phone_last4=."""
    from prism_confirmation_ids import lookup_confirmation_public

    phone_last4 = (request.args.get('phone_last4') or '').strip()
    orders = _load(ORDERS_FILE, [])
    return jsonify(lookup_confirmation_public(ref, orders, phone_last4=phone_last4 or None))


@prism_orders.route('/prism/exemptions/status', methods=['GET'])
def exemptions_status():
    """Active exemption period metadata (no plaintext codes). Optional ?contract_payer_id=&lane="""
    from prism_confirmation_ids import admin_authorized, exemption_status

    auth = request.headers.get('Authorization', '')
    payer_q = request.args.get('contract_payer_id')
    lane_q = request.args.get('lane') or request.args.get('mobility_lane')
    try:
        payer_id = int(payer_q) if payer_q is not None and str(payer_q).strip() != '' else None
    except (TypeError, ValueError):
        payer_id = None
    payload = exemption_status(contract_payer_id=payer_id, lane=lane_q)
    payload['admin'] = admin_authorized(auth)
    return jsonify(payload)


@prism_orders.route('/prism/exemptions/rotate', methods=['POST'])
def exemptions_rotate():
    """
    Generate new quarterly exemption codes per MCO/program scope.
    Requires Authorization: Bearer <PRISM_EXEMPTION_ADMIN_KEY>.
    Plaintext codes returned once — store in 1Password / internal ops doc.

    Body examples:
      {"setup_defaults": true}  — HAP MOB-A + HAP ALL + DDI enterprise
      {"contract_payer_id": 1, "lane": "MOB-A"}
      {"scopes": [{"contract_payer_id": 1, "lane": "MOB-A"}, {"contract_payer_id": 2, "lane": "MOB-A"}]}
    """
    from prism_confirmation_ids import admin_authorized, rotate_exemption_codes

    if not admin_authorized(request.headers.get('Authorization', '')):
        return jsonify({'error': 'Unauthorized — set PRISM_EXEMPTION_ADMIN_KEY on server'}), 401

    data = request.get_json(silent=True) or {}
    payer_raw = data.get('contract_payer_id')
    try:
        payer_id = int(payer_raw) if payer_raw is not None and str(payer_raw).strip() != '' else None
    except (TypeError, ValueError):
        payer_id = None

    result = rotate_exemption_codes(
        period=(data.get('period') or '').strip().upper() or None,
        types=data.get('types'),
        contract_payer_id=payer_id,
        lane=data.get('lane') or data.get('mobility_lane'),
        scopes=data.get('scopes'),
        setup_defaults=bool(data.get('setup_defaults')),
        deactivate_previous=data.get('deactivate_previous', True),
    )
    if result.get('error'):
        return jsonify(result), 400
    return jsonify(result)


@prism_orders.route('/prism/exemptions/validate', methods=['POST'])
def exemptions_validate():
    """Validate a rotating EX-… exemption code (scoped per MCO + program lane)."""
    from prism_confirmation_ids import validate_exemption_code

    data = request.get_json(silent=True) or {}
    code = (data.get('code') or data.get('override_code') or '').strip()
    email = (data.get('email') or '').strip().lower()
    context = (data.get('context') or 'api').strip()
    payer_raw = data.get('contract_payer_id')
    try:
        payer_id = int(payer_raw) if payer_raw is not None and str(payer_raw).strip() != '' else None
    except (TypeError, ValueError):
        payer_id = None
    lane = data.get('lane') or data.get('mobility_lane')
    return jsonify(
        validate_exemption_code(
            code,
            email=email,
            context=context,
            contract_payer_id=payer_id,
            lane=lane,
            mobility_lane=lane,
        )
    )
