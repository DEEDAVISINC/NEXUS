#!/usr/bin/env python3
"""
PRISM DOT COMPLIANCE MODULE
============================
Enhanced DOT drug and alcohol testing compliance for PRISM.

Includes:
- Collection Type Workflows (step-by-step procedures)
- Fatal Flaw Detection Engine
- Post-Accident Decision Logic
- Collector Certification Tracking
- Shy Bladder Protocol
- Temperature Out of Range Handler
- Random Selection System
- Collector due diligence: operational basics (autopilot / audit risk)

Reference: 49 CFR Part 40, FMCSA Part 382
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from flask import Blueprint, request, jsonify

prism_dot = Blueprint('prism_dot', __name__)


# ═══════════════════════════════════════════════════════════════════
# DOT COLLECTION WORKFLOWS — Step-by-step procedures
# ═══════════════════════════════════════════════════════════════════

DOT_URINE_COLLECTION_WORKFLOW = {
    'id': 'DOT_URINE',
    'name': 'DOT Urine Specimen Collection',
    'reference': '49 CFR Part 40 Subpart C-E',
    'steps': [
        {
            'step': 1,
            'name': 'Verify Donor Identity',
            'instruction': 'Request government-issued photo ID. Verify name matches authorization.',
            'critical': True,
            'fatal_if_skipped': False,
            'documentation': 'Record ID type and number on CCF',
        },
        {
            'step': 2,
            'name': 'Explain Collection Process',
            'instruction': 'Explain the collection process to the donor. Answer questions.',
            'critical': False,
            'fatal_if_skipped': False,
            'documentation': None,
        },
        {
            'step': 3,
            'name': 'Remove Outer Garments',
            'instruction': 'Ask donor to remove coat, hat, purse, bag. Store securely.',
            'critical': False,
            'fatal_if_skipped': False,
            'documentation': None,
        },
        {
            'step': 4,
            'name': 'Empty Pockets',
            'instruction': 'Ask donor to empty pockets. Display items. Leave with belongings.',
            'critical': False,
            'fatal_if_skipped': False,
            'documentation': None,
        },
        {
            'step': 5,
            'name': 'Donor Washes Hands',
            'instruction': 'Direct donor to wash and dry hands before providing specimen.',
            'critical': True,
            'fatal_if_skipped': False,
            'documentation': None,
        },
        {
            'step': 6,
            'name': 'Provide Collection Container',
            'instruction': 'Open sealed collection container in donor\'s presence. Verify seal intact.',
            'critical': True,
            'fatal_if_skipped': True,
            'documentation': 'Container must be sealed until opened in donor\'s presence',
        },
        {
            'step': 7,
            'name': 'Donor Provides Specimen',
            'instruction': 'Donor enters restroom. Provides specimen in private (unless observed).',
            'critical': True,
            'fatal_if_skipped': True,
            'documentation': 'Note if observed collection was required',
        },
        {
            'step': 8,
            'name': 'Check Temperature',
            'instruction': 'Check temperature WITHIN 4 MINUTES. Must be 90-100°F (32-38°C).',
            'critical': True,
            'fatal_if_skipped': True,
            'documentation': 'Record actual temperature on CCF. If out of range, proceed to observed collection.',
            'decision_point': 'temperature_check',
        },
        {
            'step': 9,
            'name': 'Check Volume',
            'instruction': 'Verify at least 45mL of urine. If insufficient, start shy bladder protocol.',
            'critical': True,
            'fatal_if_skipped': True,
            'documentation': 'If <45mL, invoke shy bladder protocol',
            'decision_point': 'volume_check',
        },
        {
            'step': 10,
            'name': 'Split Specimen',
            'instruction': 'Pour 30mL into primary bottle (Bottle A). Pour 15mL into split bottle (Bottle B).',
            'critical': True,
            'fatal_if_skipped': True,
            'documentation': 'Both bottles must meet minimum volumes',
        },
        {
            'step': 11,
            'name': 'Seal Bottles',
            'instruction': 'Apply tamper-evident seals in donor\'s presence. Seals go across cap/bottle seam.',
            'critical': True,
            'fatal_if_skipped': True,
            'documentation': 'Donor must witness sealing',
        },
        {
            'step': 12,
            'name': 'Donor Initials Seals',
            'instruction': 'Have donor initial and date both seals.',
            'critical': True,
            'fatal_if_skipped': True,
            'documentation': 'Donor initials required on both bottle seals',
        },
        {
            'step': 13,
            'name': 'Complete CCF',
            'instruction': 'Complete ALL fields on CCF. No blanks. Include specimen ID, collection time, date.',
            'critical': True,
            'fatal_if_skipped': True,
            'documentation': 'All CCF fields must be completed',
        },
        {
            'step': 14,
            'name': 'Collector Signs CCF',
            'instruction': 'Print your name AND sign the CCF. Both required.',
            'critical': True,
            'fatal_if_skipped': True,
            'documentation': 'FATAL FLAW if collector signature missing',
        },
        {
            'step': 15,
            'name': 'Donor Signs CCF',
            'instruction': 'Have donor sign and date Step 1 of CCF.',
            'critical': True,
            'fatal_if_skipped': True,
            'documentation': 'FATAL FLAW if donor signature missing (unless documented refusal)',
        },
        {
            'step': 16,
            'name': 'Give Donor Copy',
            'instruction': 'Give donor Copy 5 of the CCF.',
            'critical': True,
            'fatal_if_skipped': False,
            'documentation': 'Donor must receive their copy',
        },
        {
            'step': 17,
            'name': 'Package for Shipping',
            'instruction': 'Place sealed bottles and Copy 1 in shipping bag. Seal bag.',
            'critical': True,
            'fatal_if_skipped': False,
            'documentation': 'Maintain chain of custody to lab',
        },
        {
            'step': 18,
            'name': 'Ship to Laboratory',
            'instruction': 'Ship to SAMHSA-certified laboratory same day if possible.',
            'critical': True,
            'fatal_if_skipped': False,
            'documentation': 'Track shipment. Lab must be SAMHSA-certified.',
        },
    ],
}

DOT_ALCOHOL_SCREENING_WORKFLOW = {
    'id': 'DOT_ALCOHOL_SCREEN',
    'name': 'DOT Alcohol Screening Test',
    'reference': '49 CFR Part 40 Subpart L',
    'steps': [
        {
            'step': 1,
            'name': 'Verify Employee Identity',
            'instruction': 'Request government-issued photo ID. Verify name matches authorization.',
            'critical': True,
            'fatal_if_skipped': False,
        },
        {
            'step': 2,
            'name': 'Complete ATF Step 1',
            'instruction': 'Complete Step 1 of Alcohol Testing Form (ATF).',
            'critical': True,
            'fatal_if_skipped': True,
        },
        {
            'step': 3,
            'name': 'Open Testing Device',
            'instruction': 'Open ASD or EBT device in employee\'s presence. Verify seal intact.',
            'critical': True,
            'fatal_if_skipped': True,
        },
        {
            'step': 4,
            'name': 'Perform Screening Test',
            'instruction': 'Conduct screening test per device instructions.',
            'critical': True,
            'fatal_if_skipped': True,
        },
        {
            'step': 5,
            'name': 'Read Result',
            'instruction': 'Read and record screening test result.',
            'critical': True,
            'fatal_if_skipped': True,
            'decision_point': 'alcohol_screening_result',
        },
        {
            'step': 6,
            'name': 'Show Result to Employee',
            'instruction': 'Show result to employee.',
            'critical': True,
            'fatal_if_skipped': False,
        },
        {
            'step': 7,
            'name': 'Record on ATF',
            'instruction': 'Record result on ATF. Both BAT/STT and employee sign.',
            'critical': True,
            'fatal_if_skipped': True,
        },
    ],
}

DOT_ALCOHOL_CONFIRMATION_WORKFLOW = {
    'id': 'DOT_ALCOHOL_CONFIRM',
    'name': 'DOT Alcohol Confirmation Test',
    'reference': '49 CFR Part 40 Subpart M',
    'prerequisite': 'Screening result >= 0.02 BAC',
    'steps': [
        {
            'step': 1,
            'name': 'Wait 15 Minutes',
            'instruction': 'MUST wait at least 15 minutes after screening test. Employee cannot eat, drink, smoke.',
            'critical': True,
            'fatal_if_skipped': True,
            'timing': '15-30 minutes',
        },
        {
            'step': 2,
            'name': 'Confirm No Ingestion',
            'instruction': 'Confirm employee has not eaten, drunk, smoked, or put anything in mouth.',
            'critical': True,
            'fatal_if_skipped': False,
        },
        {
            'step': 3,
            'name': 'Prepare EBT',
            'instruction': 'EBT only for confirmation (ASD not permitted). Run air blank - must read 0.00.',
            'critical': True,
            'fatal_if_skipped': True,
        },
        {
            'step': 4,
            'name': 'Install New Mouthpiece',
            'instruction': 'Open new mouthpiece in employee\'s presence. Install on EBT.',
            'critical': True,
            'fatal_if_skipped': True,
        },
        {
            'step': 5,
            'name': 'Conduct Confirmation Test',
            'instruction': 'Employee blows into EBT. Device prints result.',
            'critical': True,
            'fatal_if_skipped': True,
        },
        {
            'step': 6,
            'name': 'Record Result',
            'instruction': 'Record confirmation result on ATF.',
            'critical': True,
            'fatal_if_skipped': True,
            'decision_point': 'alcohol_confirmation_result',
        },
        {
            'step': 7,
            'name': 'Attach Printout',
            'instruction': 'Attach EBT printout to ATF.',
            'critical': True,
            'fatal_if_skipped': True,
        },
        {
            'step': 8,
            'name': 'Sign ATF',
            'instruction': 'Both BAT and employee sign the ATF and printout.',
            'critical': True,
            'fatal_if_skipped': True,
        },
        {
            'step': 9,
            'name': 'Report Result',
            'instruction': 'Report result to employer immediately if >= 0.02.',
            'critical': True,
            'fatal_if_skipped': False,
        },
    ],
}


# ═══════════════════════════════════════════════════════════════════
# FATAL FLAW DETECTION ENGINE
# ═══════════════════════════════════════════════════════════════════

FATAL_FLAWS = [
    {
        'id': 'FF-001',
        'name': 'No Collector Signature',
        'check': 'Collector signature present on CCF',
        'reference': '49 CFR §40.199(a)',
        'correctable': False,
        'action': 'CANCEL TEST',
    },
    {
        'id': 'FF-002',
        'name': 'No Donor Signature',
        'check': 'Donor signature present on CCF (or documented refusal)',
        'reference': '49 CFR §40.199(a)',
        'correctable': 'Only if collector documented attempt per §40.73',
        'action': 'CANCEL TEST (unless corrected per §40.73)',
    },
    {
        'id': 'FF-003',
        'name': 'Specimen ID Mismatch',
        'check': 'Specimen ID on bottle matches CCF exactly',
        'reference': '49 CFR §40.199(a)',
        'correctable': False,
        'action': 'CANCEL TEST',
    },
    {
        'id': 'FF-004',
        'name': 'Broken Seal',
        'check': 'Specimen bottle seal intact (no tears, no tampering)',
        'reference': '49 CFR §40.199(a)',
        'correctable': False,
        'action': 'CANCEL TEST',
    },
    {
        'id': 'FF-005',
        'name': 'Insufficient Volume',
        'check': 'Sufficient specimen volume for testing',
        'reference': '49 CFR §40.199(a)',
        'correctable': False,
        'action': 'CANCEL TEST',
    },
    {
        'id': 'FF-006',
        'name': 'No Printed Collector Name',
        'check': 'Collector name printed on CCF (and identifiable)',
        'reference': '49 CFR §40.199(a)',
        'correctable': 'Only if collector can be identified',
        'action': 'CANCEL TEST (if unidentifiable)',
    },
]

CORRECTABLE_FLAWS = [
    {
        'id': 'CF-001',
        'name': 'Missing Employer Phone',
        'check': 'Employer phone number on CCF',
        'reference': '49 CFR §40.203',
        'who_corrects': 'MRO',
        'deadline': '5 business days',
    },
    {
        'id': 'CF-002',
        'name': 'Missing Employer Address',
        'check': 'Employer address on CCF',
        'reference': '49 CFR §40.203',
        'who_corrects': 'MRO',
        'deadline': '5 business days',
    },
    {
        'id': 'CF-003',
        'name': 'Transposed Numbers',
        'check': 'Specimen ID numbers correct (not transposed)',
        'reference': '49 CFR §40.203',
        'who_corrects': 'MRO verifies with lab/collector',
        'deadline': '5 business days',
    },
    {
        'id': 'CF-004',
        'name': 'Missing Temperature',
        'check': 'Specimen temperature recorded on CCF',
        'reference': '49 CFR §40.208',
        'who_corrects': 'MRO contacts collector',
        'deadline': '5 business days',
    },
]

# Due diligence: experienced-collector "basics" that drive audit findings
DOT_COLLECTOR_DUE_DILIGENCE = {
    'id': 'DOT_COLLECTOR_BASICS_DD',
    'title': "DOT Collectors — Don't Let the Basics Slip",
    'category': 'due_diligence',
    'audience': ['DOT collectors', 'C/TPA QA', 'PRISM field ops'],
    'reference': '49 CFR Part 40',
    'version': '1.0',
    'summary': (
        "Most DOT collection errors are not from ignorance of the process — they come from "
        "relaxing small compliance steps over time. This brief is for QA, onboarding refreshers, "
        "and PRISM due-diligence checks."
    ),
    'reminders': [
        {
            'order': 1,
            'title': 'ID verification must be intentional',
            'body': (
                "A quick glance is not enough. Always confirm the donor's identity using acceptable "
                "documentation. No assumptions. No shortcuts."
            ),
            'prism_workflow_ref': 'DOT_URINE step 1',
        },
        {
            'order': 2,
            'title': 'Temperature check is not optional',
            'body': (
                "The 4-minute window after collection matters. If temperature is not documented "
                "correctly, the collection can be invalidated even when everything else was done "
                "correctly. Follow the CCF and Part 40 timing rules."
            ),
            'prism_workflow_ref': 'DOT_URINE step 8',
            'reference': '49 CFR Part 40 Subpart C (collection procedures)',
        },
        {
            'order': 3,
            'title': 'CCF accuracy is everything',
            'body': (
                "Wrong test reason, missing signatures, incorrect dates, and step omissions can "
                "constitute fatal flaws or uncorrectable problems in some situations. Treat the CCF "
                "as a legal document every time."
            ),
            'reference': '49 CFR §40.199 (fatal flaws)',
        },
        {
            'order': 4,
            'title': 'Direct observation rules are strict',
            'body': (
                "Observed collection is not based on preference — it is based on regulatory triggers "
                "(e.g., temperature out of range, suspected tampering, return-to-duty / follow-up as "
                "applicable). Know when observation is required to protect the donor, the employer, and "
                "the defensibility of the test."
            ),
        },
        {
            'order': 5,
            'title': 'Shy bladder timing still applies',
            'body': (
                "Collectors may rush or improvise. The 3-hour window and required documentation for "
                "insufficient volume / shy bladder must be followed as outlined in 49 CFR Part 40. Do "
                "not shortcut the stated sequence."
            ),
            'reference': '49 CFR Part 40 (shy bladder / insufficient volume)',
        },
        {
            'order': 6,
            'title': 'Specimen security never changes',
            'body': (
                "From sealing bottles to package and shipping procedures, chain of custody and "
                "integrity are what make a test legally defensible."
            ),
            'prism_workflow_ref': 'DOT_URINE steps 11-18',
        },
    ],
    'mindset': (
        "The difference between a collector and a compliance professional is attention to detail. "
        "Employers are not only paying for a sample — they are paying for protection from violations, "
        "penalties, and audit findings. When that is understood, the role in the industry shifts."
    ),
    'closing': 'Stay sharp. Stay compliant. Stay valuable.',
}


def detect_fatal_flaws(scanback_data: dict) -> dict:
    """
    Analyze scanback data for fatal flaws.
    
    scanback_data should include:
    - collector_signature: bool
    - donor_signature: bool
    - donor_signature_refusal_documented: bool
    - specimen_id_bottle: str
    - specimen_id_ccf: str
    - seal_intact: bool
    - volume_sufficient: bool
    - collector_name_printed: bool
    - collector_identifiable: bool
    - temperature_recorded: bool
    - temperature_value: float (or None)
    - employer_phone: bool
    - employer_address: bool
    """
    fatal_flaws_found = []
    correctable_flaws_found = []
    
    # Check each fatal flaw
    if not scanback_data.get('collector_signature', False):
        fatal_flaws_found.append({
            **FATAL_FLAWS[0],
            'status': 'FAILED',
            'notes': 'No collector signature on CCF',
        })
    
    if not scanback_data.get('donor_signature', False):
        if not scanback_data.get('donor_signature_refusal_documented', False):
            fatal_flaws_found.append({
                **FATAL_FLAWS[1],
                'status': 'FAILED',
                'notes': 'No donor signature and no documented refusal',
            })
    
    specimen_id_bottle = scanback_data.get('specimen_id_bottle', '')
    specimen_id_ccf = scanback_data.get('specimen_id_ccf', '')
    if specimen_id_bottle and specimen_id_ccf and specimen_id_bottle != specimen_id_ccf:
        fatal_flaws_found.append({
            **FATAL_FLAWS[2],
            'status': 'FAILED',
            'notes': f'Bottle ID: {specimen_id_bottle}, CCF ID: {specimen_id_ccf}',
        })
    
    if not scanback_data.get('seal_intact', True):
        fatal_flaws_found.append({
            **FATAL_FLAWS[3],
            'status': 'FAILED',
            'notes': 'Specimen seal broken or shows tampering',
        })
    
    if not scanback_data.get('volume_sufficient', True):
        fatal_flaws_found.append({
            **FATAL_FLAWS[4],
            'status': 'FAILED',
            'notes': 'Insufficient specimen volume',
        })
    
    if not scanback_data.get('collector_name_printed', False):
        if not scanback_data.get('collector_identifiable', False):
            fatal_flaws_found.append({
                **FATAL_FLAWS[5],
                'status': 'FAILED',
                'notes': 'No printed collector name and collector unidentifiable',
            })
    
    # Check correctable flaws
    if not scanback_data.get('employer_phone', True):
        correctable_flaws_found.append({
            **CORRECTABLE_FLAWS[0],
            'status': 'NEEDS_CORRECTION',
        })
    
    if not scanback_data.get('employer_address', True):
        correctable_flaws_found.append({
            **CORRECTABLE_FLAWS[1],
            'status': 'NEEDS_CORRECTION',
        })
    
    if not scanback_data.get('temperature_recorded', True):
        correctable_flaws_found.append({
            **CORRECTABLE_FLAWS[3],
            'status': 'NEEDS_CORRECTION',
        })
    
    # Determine result
    if fatal_flaws_found:
        result = 'CANCEL_TEST'
        message = f'FATAL FLAW DETECTED — {len(fatal_flaws_found)} fatal flaw(s). Test must be cancelled.'
    elif correctable_flaws_found:
        result = 'NEEDS_CORRECTION'
        message = f'{len(correctable_flaws_found)} correctable flaw(s). MRO to correct within 5 business days.'
    else:
        result = 'PASS'
        message = 'No fatal or correctable flaws detected.'
    
    return {
        'result': result,
        'message': message,
        'fatal_flaws': fatal_flaws_found,
        'correctable_flaws': correctable_flaws_found,
        'timestamp': datetime.now().isoformat(),
    }


# ═══════════════════════════════════════════════════════════════════
# POST-ACCIDENT DECISION ENGINE
# ═══════════════════════════════════════════════════════════════════

def post_accident_testing_required(
    fatality: bool,
    citation_issued: bool,
    bodily_injury: bool,
    vehicle_towed: bool,
) -> dict:
    """
    Determine if post-accident testing is required per FMCSA 49 CFR 382.303.
    
    Args:
        fatality: Was there a fatality?
        citation_issued: Was a citation issued to the DOT-regulated driver?
        bodily_injury: Was there bodily injury requiring immediate medical treatment away from scene?
        vehicle_towed: Was any vehicle towed from scene due to disabling damage?
    
    Returns:
        Decision with testing requirements and timeframes.
    """
    testing_required = False
    reason = ''
    
    # Decision tree per 49 CFR 382.303
    if fatality:
        testing_required = True
        reason = 'Fatality occurred — testing ALWAYS required'
    elif citation_issued:
        if bodily_injury:
            testing_required = True
            reason = 'Citation issued AND bodily injury requiring off-site medical treatment'
        elif vehicle_towed:
            testing_required = True
            reason = 'Citation issued AND vehicle towed due to disabling damage'
        else:
            testing_required = False
            reason = 'Citation issued but no bodily injury or tow — testing NOT required'
    else:
        testing_required = False
        reason = 'No citation issued — testing NOT required'
    
    result = {
        'testing_required': testing_required,
        'reason': reason,
        'inputs': {
            'fatality': fatality,
            'citation_issued': citation_issued,
            'bodily_injury': bodily_injury,
            'vehicle_towed': vehicle_towed,
        },
    }
    
    if testing_required:
        result['tests_required'] = ['drug', 'alcohol']
        result['timeframes'] = {
            'alcohol': {
                'deadline': '8 hours from accident',
                'preferred': '2 hours from accident',
                'if_missed': 'Document why test was not performed. DO NOT TEST.',
            },
            'drug': {
                'deadline': '32 hours from accident',
                'preferred': 'As soon as possible',
                'if_missed': 'Document why test was not performed. DO NOT TEST.',
            },
        }
        result['driver_requirements'] = [
            'Remain available for testing',
            'Do NOT consume alcohol for 8 hours following accident',
            'Refusal to test = treated as positive result',
        ]
    
    result['timestamp'] = datetime.now().isoformat()
    return result


# ═══════════════════════════════════════════════════════════════════
# SHY BLADDER PROTOCOL
# ═══════════════════════════════════════════════════════════════════

def start_shy_bladder_protocol(order_id: str, start_time: datetime = None) -> dict:
    """
    Initialize shy bladder protocol per 49 CFR §40.193.
    
    When donor cannot provide 45mL of urine.
    """
    if start_time is None:
        start_time = datetime.now()
    
    end_time = start_time + timedelta(hours=3)
    
    return {
        'order_id': order_id,
        'protocol': 'SHY_BLADDER',
        'reference': '49 CFR §40.193',
        'start_time': start_time.isoformat(),
        'end_time': end_time.isoformat(),
        'max_fluid': '40 oz',
        'instructions': [
            'Discard the insufficient specimen',
            'Document start time of 3-hour window',
            'Offer donor up to 40 oz of fluid over 3 hours',
            'Donor may attempt to provide specimen at any time',
            'Donor must remain at collection site',
            'If still insufficient after 3 hours — stop and notify employer',
            'Employer refers donor for medical evaluation',
            'If no legitimate medical explanation — REFUSAL TO TEST',
        ],
        'do_not': [
            'Do NOT allow donor to leave collection site',
            'Do NOT combine specimens from multiple attempts',
            'Do NOT use observed collection as substitute for shy bladder',
        ],
        'status': 'IN_PROGRESS',
        'timestamp': datetime.now().isoformat(),
    }


def check_shy_bladder_status(start_time: datetime, current_time: datetime = None) -> dict:
    """Check if shy bladder window has expired."""
    if current_time is None:
        current_time = datetime.now()
    
    end_time = start_time + timedelta(hours=3)
    time_remaining = end_time - current_time
    
    if current_time >= end_time:
        return {
            'status': 'EXPIRED',
            'message': '3-hour window has expired. Notify employer for medical evaluation.',
            'action': 'REFER_FOR_MEDICAL_EVALUATION',
        }
    else:
        minutes_remaining = int(time_remaining.total_seconds() / 60)
        return {
            'status': 'IN_PROGRESS',
            'message': f'{minutes_remaining} minutes remaining in 3-hour window.',
            'time_remaining_minutes': minutes_remaining,
        }


# ═══════════════════════════════════════════════════════════════════
# TEMPERATURE OUT OF RANGE HANDLER
# ═══════════════════════════════════════════════════════════════════

def handle_temperature_out_of_range(
    actual_temperature: float,
    donor_explanation: str = None,
) -> dict:
    """
    Handle specimen with temperature outside 90-100°F range.
    
    Per 49 CFR §40.65, if temperature is out of range:
    1. Document actual temperature
    2. Ask donor for explanation
    3. Conduct immediate observed collection
    4. Send both specimens to lab
    """
    in_range = 90.0 <= actual_temperature <= 100.0
    
    if in_range:
        return {
            'status': 'IN_RANGE',
            'temperature': actual_temperature,
            'message': 'Temperature within acceptable range.',
            'action': 'CONTINUE_NORMAL_COLLECTION',
        }
    
    return {
        'status': 'OUT_OF_RANGE',
        'temperature': actual_temperature,
        'acceptable_range': '90-100°F (32-38°C)',
        'message': 'Temperature out of range — immediate observed collection required.',
        'reference': '49 CFR §40.65',
        'donor_explanation': donor_explanation,
        'required_actions': [
            'Document actual temperature on CCF',
            'Document donor explanation (if any)',
            'Immediately conduct second collection under DIRECT OBSERVATION',
            'Use NEW CCF for observed collection',
            'Send BOTH specimens to laboratory',
            'Lab tests both specimens independently',
        ],
        'likely_cause': 'Too cold (<90°F) = possible substitution. Too hot (>100°F) = specimen was heated.',
    }


# ═══════════════════════════════════════════════════════════════════
# COLLECTOR CERTIFICATION TRACKING
# ═══════════════════════════════════════════════════════════════════

COLLECTOR_CERT_REQUIREMENTS = {
    'initial_training': {
        'name': 'Initial Collector Training',
        'reference': '49 CFR §40.33',
        'description': 'All Part 40 collection procedures',
        'required': True,
    },
    'qualification_training': {
        'name': 'Qualification Training',
        'reference': '49 CFR §40.33',
        'description': '5 consecutive error-free mock collections',
        'required': True,
    },
    'proficiency_demonstration': {
        'name': 'Proficiency Demonstration',
        'reference': '49 CFR §40.31',
        'description': 'Demonstrated proficiency in collection procedures',
        'required': True,
    },
    'refresher_training': {
        'name': 'Refresher Training',
        'reference': '49 CFR §40.33',
        'description': 'Required every 5 years from initial training date',
        'required': True,
        'renewal_period_years': 5,
    },
    'error_correction_training': {
        'name': 'Error Correction Training',
        'reference': '49 CFR §40.33',
        'description': 'Required after any collection error',
        'required': False,
        'triggered_by': 'Collection error',
    },
}


def check_collector_certification(collector_data: dict) -> dict:
    """
    Check if a collector meets all certification requirements.
    
    collector_data should include:
    - initial_training_date: date (or None)
    - qualification_training_date: date (or None)
    - proficiency_demonstration_date: date (or None)
    - last_refresher_date: date (or None)
    - last_error_date: date (or None)
    - error_correction_training_date: date (or None)
    """
    issues = []
    warnings = []
    
    today = datetime.now().date()
    
    # Check initial training
    initial_date = collector_data.get('initial_training_date')
    if not initial_date:
        issues.append('Missing initial collector training')
    
    # Check qualification training
    qual_date = collector_data.get('qualification_training_date')
    if not qual_date:
        issues.append('Missing qualification training (5 mock collections)')
    
    # Check proficiency demonstration
    prof_date = collector_data.get('proficiency_demonstration_date')
    if not prof_date:
        issues.append('Missing proficiency demonstration')
    
    # Check refresher training (every 5 years)
    if initial_date:
        if isinstance(initial_date, str):
            initial_date = datetime.fromisoformat(initial_date).date()
        
        refresher_date = collector_data.get('last_refresher_date')
        if refresher_date and isinstance(refresher_date, str):
            refresher_date = datetime.fromisoformat(refresher_date).date()
        
        # Use the more recent of initial or last refresher
        base_date = refresher_date if refresher_date else initial_date
        years_since = (today - base_date).days / 365.25
        
        if years_since >= 5:
            issues.append(f'Refresher training overdue (last: {base_date}, {years_since:.1f} years ago)')
        elif years_since >= 4.5:
            warnings.append(f'Refresher training due soon (expires in {(5 - years_since) * 12:.0f} months)')
    
    # Check error correction training
    last_error = collector_data.get('last_error_date')
    error_correction = collector_data.get('error_correction_training_date')
    
    if last_error:
        if isinstance(last_error, str):
            last_error = datetime.fromisoformat(last_error).date()
        
        if error_correction:
            if isinstance(error_correction, str):
                error_correction = datetime.fromisoformat(error_correction).date()
            
            if error_correction < last_error:
                issues.append('Error correction training required (error occurred after last training)')
        else:
            issues.append('Error correction training required (error on record, no correction training)')
    
    # Determine status
    if issues:
        status = 'NOT_QUALIFIED'
        message = 'Collector does NOT meet DOT requirements'
    elif warnings:
        status = 'QUALIFIED_WITH_WARNINGS'
        message = 'Collector is qualified but has upcoming requirements'
    else:
        status = 'QUALIFIED'
        message = 'Collector meets all DOT requirements'
    
    return {
        'status': status,
        'message': message,
        'issues': issues,
        'warnings': warnings,
        'timestamp': datetime.now().isoformat(),
    }


# ═══════════════════════════════════════════════════════════════════
# RANDOM SELECTION SYSTEM
# ═══════════════════════════════════════════════════════════════════

import random
import hashlib


def random_selection(
    driver_pool: List[dict],
    selection_rate: float = 0.50,
    selection_date: datetime = None,
    seed: str = None,
) -> dict:
    """
    Perform scientifically valid random selection for DOT random testing.
    
    Per DOT requirements:
    - Each employee must have equal chance of selection
    - Selection must be unannounced
    - Selection must be spread throughout the year
    
    Args:
        driver_pool: List of driver dicts with 'id' and 'name'
        selection_rate: Annual selection rate (0.50 = 50% for FMCSA drug)
        selection_date: Date of selection (defaults to today)
        seed: Optional seed for reproducibility (use date-based for auditing)
    
    Returns:
        Selection results with selected drivers.
    """
    if selection_date is None:
        selection_date = datetime.now()
    
    # Create seed from date if not provided (for audit reproducibility)
    if seed is None:
        seed = f"DOT_RANDOM_{selection_date.strftime('%Y%m%d')}"
    
    # Use seed for reproducible randomness
    seed_hash = int(hashlib.sha256(seed.encode()).hexdigest(), 16) % (2**32)
    random.seed(seed_hash)
    
    pool_size = len(driver_pool)
    if pool_size == 0:
        return {
            'error': 'Empty driver pool',
            'selected': [],
        }
    
    # Calculate number to select this period
    # For monthly selection with 50% annual rate: ~4.17% per month
    # But we select based on the period rate provided
    num_to_select = max(1, int(pool_size * selection_rate / 12))  # Monthly selection
    
    # Ensure we don't select more than pool
    num_to_select = min(num_to_select, pool_size)
    
    # Random selection
    selected = random.sample(driver_pool, num_to_select)
    
    return {
        'selection_date': selection_date.isoformat(),
        'pool_size': pool_size,
        'selection_rate': selection_rate,
        'num_selected': len(selected),
        'selected': selected,
        'seed': seed,
        'next_selection': (selection_date + timedelta(days=30)).isoformat(),
        'notes': [
            'Selection was scientifically random (equal probability)',
            'Notify selected drivers immediately',
            'Testing must be unannounced',
            'Document any no-shows as refusals',
        ],
    }


# ═══════════════════════════════════════════════════════════════════
# API ENDPOINTS
# ═══════════════════════════════════════════════════════════════════

@prism_dot.route('/prism/dot/workflow/<workflow_id>', methods=['GET'])
def api_get_workflow(workflow_id):
    """Get a DOT collection workflow by ID."""
    workflows = {
        'DOT_URINE': DOT_URINE_COLLECTION_WORKFLOW,
        'DOT_ALCOHOL_SCREEN': DOT_ALCOHOL_SCREENING_WORKFLOW,
        'DOT_ALCOHOL_CONFIRM': DOT_ALCOHOL_CONFIRMATION_WORKFLOW,
    }
    
    workflow = workflows.get(workflow_id.upper())
    if not workflow:
        return jsonify({'error': f'Unknown workflow: {workflow_id}'}), 404
    
    return jsonify(workflow)


@prism_dot.route('/prism/dot/fatal-flaw-check', methods=['POST'])
def api_fatal_flaw_check():
    """Run fatal flaw detection on scanback data."""
    data = request.json or {}
    result = detect_fatal_flaws(data)
    return jsonify(result)


@prism_dot.route('/prism/dot/post-accident-decision', methods=['POST'])
def api_post_accident_decision():
    """Determine if post-accident testing is required."""
    data = request.json or {}
    result = post_accident_testing_required(
        fatality=data.get('fatality', False),
        citation_issued=data.get('citation_issued', False),
        bodily_injury=data.get('bodily_injury', False),
        vehicle_towed=data.get('vehicle_towed', False),
    )
    return jsonify(result)


@prism_dot.route('/prism/dot/shy-bladder/start', methods=['POST'])
def api_start_shy_bladder():
    """Start shy bladder protocol for an order."""
    data = request.json or {}
    order_id = data.get('order_id')
    if not order_id:
        return jsonify({'error': 'order_id required'}), 400
    
    result = start_shy_bladder_protocol(order_id)
    return jsonify(result)


@prism_dot.route('/prism/dot/temperature-check', methods=['POST'])
def api_temperature_check():
    """Check if specimen temperature is in range."""
    data = request.json or {}
    temperature = data.get('temperature')
    if temperature is None:
        return jsonify({'error': 'temperature required'}), 400
    
    result = handle_temperature_out_of_range(
        actual_temperature=float(temperature),
        donor_explanation=data.get('donor_explanation'),
    )
    return jsonify(result)


@prism_dot.route('/prism/dot/collector-cert-check', methods=['POST'])
def api_collector_cert_check():
    """Check if a collector meets certification requirements."""
    data = request.json or {}
    result = check_collector_certification(data)
    return jsonify(result)


@prism_dot.route('/prism/dot/random-selection', methods=['POST'])
def api_random_selection():
    """Perform random selection from driver pool."""
    data = request.json or {}
    driver_pool = data.get('driver_pool', [])
    selection_rate = data.get('selection_rate', 0.50)
    
    if not driver_pool:
        return jsonify({'error': 'driver_pool required'}), 400
    
    result = random_selection(
        driver_pool=driver_pool,
        selection_rate=selection_rate,
    )
    return jsonify(result)


@prism_dot.route('/prism/dot/fatal-flaws', methods=['GET'])
def api_get_fatal_flaws():
    """Get list of all fatal flaws."""
    return jsonify({
        'fatal_flaws': FATAL_FLAWS,
        'correctable_flaws': CORRECTABLE_FLAWS,
    })


@prism_dot.route('/prism/dot/collector-requirements', methods=['GET'])
def api_get_collector_requirements():
    """Get collector certification requirements."""
    return jsonify(COLLECTOR_CERT_REQUIREMENTS)


@prism_dot.route('/prism/dot/collector-due-diligence', methods=['GET'])
def api_get_collector_due_diligence():
    """
    PRISM / QA: DOT collector due-diligence brief — 'basics' that slip under autopilot
    (ID, temperature, CCF, observation, shy bladder, custody). Not a substitute for 49 CFR.
    """
    return jsonify(DOT_COLLECTOR_DUE_DILIGENCE)
