#!/usr/bin/env python3
"""
PRISM Orders & Intake API
=========================
Handles:
1.  POST  /prism/intake — receive submissions from the client intake form
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
"""

import os
import json
import uuid
import smtplib
import threading
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from flask import Blueprint, request, jsonify
from dotenv import load_dotenv

load_dotenv()

prism_orders = Blueprint('prism_orders', __name__)

DATA_DIR = os.path.join(os.path.dirname(__file__), 'uploads', 'prism')
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
    'notary': 'notary',
    'apostille': 'apostille',
    'process': 'process',
    'courier': 'medical_courier',
}

URGENCY_TO_PRIORITY = {
    'stat': 'STAT',
    'same-day': 'Same Day',
    'scheduled': 'Standard',
}

TIER_FEE_BASE = {
    1: 150,   # Mobile Collector
    2: 85,    # Coordinated Ride
    3: 250,   # On-Site Group Event
}

SERVICE_ROUTING_EMAILS = {
    'testing-drug': 'testing@deedavis.biz',
    'testing-occhealth': 'testing@deedavis.biz',
    'testing-lead': 'testing@deedavis.biz',
    'fingerprint': 'screening@deedavis.biz',
    'background': 'screening@deedavis.biz',
    'dna': 'dna@deedavis.biz',
    'nemt': 'rides@deedavis.biz',
    'transport': 'rides@deedavis.biz',
    'notary': 'notary@deedavis.biz',
    'apostille': 'notary@deedavis.biz',
    'process': 'notary@deedavis.biz',
    'courier': 'courier@deedavis.biz',
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
        'auto': False,
        'gates': [
            {'id': 'G-DOC-1', 'check': 'Service documentation uploaded', 'field': None, 'rule': 'manual'},
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
    """Auto-evaluate gates that check order fields (not manual)."""
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
                    gate['passed_at'] = datetime.now().isoformat()
            elif rule == 'qc_fatal_pass':
                if _qc_gate_passed(order):
                    gate['passed'] = True
                    gate['passed_by'] = 'System (QC Engine)'
                    gate['passed_at'] = datetime.now().isoformat()
    order['workflow'] = workflow
    _update_workflow_position(order)
    return order


def _update_workflow_position(order):
    """Advance current_stage to the furthest stage where all prior
    stages have all gates passed."""
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
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2, default=str)


def _fire_notification(order):
    """Push a notification into the PRISM notification feed."""
    notif_file = os.path.join(os.path.dirname(__file__), 'uploads', 'notifications', 'notifications.json')
    try:
        notifs = _load(notif_file, [])
        notifs.insert(0, {
            'id': f'notif-{uuid.uuid4().hex[:8]}',
            'type': 'new_order',
            'severity': 'high' if order.get('priority') == 'STAT' else 'medium',
            'title': f"New {order.get('service_label', 'Service')} Request",
            'message': f"{order['client']} — {order['signer']} — {order['priority']}",
            'order_id': order['id'],
            'timestamp': datetime.utcnow().isoformat(),
            'read': False,
            'recipient': 'admin',
        })
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
Fee:           ${order.get('fee', 0)}
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
ID:            {order.get('subject_id', '')}
Location:      {order.get('address', '')}

SCHEDULING
Date:          {order.get('date', '')}
Time:          {order.get('time', '')} {order.get('timezone', '')}
Site:          {order.get('collection_site', '')}

Notes:         {order.get('notes', '')}
========================================
View in PRISM Dashboard: http://localhost:3000 → PRISM → Orders
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


# ═══════════════════════════════════════════════════════════════════
# POST /prism/intake  —  Client intake form submission
# ═══════════════════════════════════════════════════════════════════

@prism_orders.route('/prism/intake', methods=['POST'])
def create_intake_order():
    data = request.get_json(silent=True) or {}

    svc_key = data.get('service_key', 'notary')
    service_type = INTAKE_SERVICE_MAP.get(svc_key, 'notary')
    urgency_raw = data.get('urgency', 'scheduled').lower()
    priority = URGENCY_TO_PRIORITY.get(urgency_raw, 'Standard')
    tier = int(data.get('tier', 1))
    fee = TIER_FEE_BASE.get(tier, 150)

    if priority == 'STAT':
        fee = int(fee * 1.5)
    elif priority == 'Same Day':
        fee = int(fee * 1.25)

    now = datetime.now()
    conf = data.get('confirmation') or f"PRISM-{now.strftime('%Y%m%d-%H%M')}-{uuid.uuid4().hex[:4].upper()}"

    routing_email = data.get('routing_email', SERVICE_ROUTING_EMAILS.get(svc_key, ADMIN_EMAIL))

    order = {
        'id': conf,
        'type': service_type,
        'service_key': svc_key,
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
        'details': data.get('details', {}),
        'qc_checklist': _build_qc_checklist(service_type),
        'qc_status': 'pending',
        'workflow': _build_workflow(service_type),
        'workflow_stage': 0,
        'workflow_stage_label': 'Order Received',
        'created_at': now.isoformat(),
        'updated_at': now.isoformat(),
    }

    _evaluate_auto_gates(order)

    orders = _load(ORDERS_FILE, [])
    orders.insert(0, order)
    _save(ORDERS_FILE, orders)

    _fire_notification(order)
    _send_order_email_async(order)

    return jsonify({'success': True, 'order': order}), 201


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

    _evaluate_auto_gates(orders[idx])
    orders[idx]['updated_at'] = now_iso
    _save(ORDERS_FILE, orders)

    return jsonify({'success': True, 'scanback': sb, 'order': orders[idx]})


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

    return jsonify({'success': True, 'scanback': sb, 'order': orders[idx]})


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
