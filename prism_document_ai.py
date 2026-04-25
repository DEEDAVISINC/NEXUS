#!/usr/bin/env python3
"""
PRISM Document AI Module
=========================
Tier 2 automated QC: processes uploaded files (images / PDFs) with AI.

Capabilities:
1. Signature detection — vision model checks for handwritten signatures
2. Form field extraction — OCR + structured output from CCF, ATF, notarial certs, FD-258, trip logs
3. Page classification — identify document types in multi-page uploads
4. Seal / stamp detection — notary seal, embossed stamp, official letterhead
5. Photo quality scoring — REO property photo blur/darkness/framing checks
6. Signature Reference Map — analyze a reference document from escrow/title to identify WHERE
   every signer (client, title agent, escrow, notary, witness, lender, co-buyer) must sign,
   initial, date, or stamp. Stored per order. Scanbacks are verified against this map so
   any missing signature, initial, or notary stamp generates an automatic error.

Architecture:
  Reference doc (from escrow/title) → Signature Map → stored per order
  Agent upload (scanback) → Verify against map → errors flagged automatically

Vision backend: Pluggable — supports Claude (Anthropic), GPT-4o (OpenAI),
or a lightweight OCR fallback (Tesseract / Textract stub). Configured via
PRISM_VISION_PROVIDER env var.

Reference: prism_ai_qc_methods plan — Tier 2
"""

import os
import json
import base64
import hashlib
from datetime import datetime
from typing import Dict, List, Optional
from flask import Blueprint, request, jsonify

prism_doc_ai = Blueprint('prism_doc_ai', __name__)

VISION_PROVIDER = os.environ.get('PRISM_VISION_PROVIDER', 'claude')
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY', '')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), 'uploads', 'prism', 'scanback_files')
RESULTS_DIR = os.path.join(os.path.dirname(__file__), 'uploads', 'prism', 'doc_ai_results')
SIG_MAPS_DIR = os.path.join(os.path.dirname(__file__), 'uploads', 'prism', 'signature_maps')
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)
os.makedirs(SIG_MAPS_DIR, exist_ok=True)


# ═══════════════════════════════════════════════════════════════════
# 1. SIGNATURE DETECTION
# ═══════════════════════════════════════════════════════════════════

SIGNATURE_FIELD_MAP = {
    'dot': [
        {'field': 'collector_signature', 'label': 'Collector signature (Step 4)', 'page_hint': 1, 'fatal': True},
        {'field': 'donor_signature', 'label': 'Donor signature (Step 5)', 'page_hint': 1, 'fatal': True},
    ],
    'non-dot': [
        {'field': 'collector_signature', 'label': 'Collector signature', 'page_hint': 1, 'fatal': True},
        {'field': 'donor_signature', 'label': 'Donor signature', 'page_hint': 1, 'fatal': True},
    ],
    'dna': [
        {'field': 'collector_signature', 'label': 'Collector signature on COC', 'page_hint': 1, 'fatal': True},
        {'field': 'participant_signature', 'label': 'Participant signature on consent', 'page_hint': 2, 'fatal': True},
    ],
    'notary': [
        {'field': 'notary_signature', 'label': 'Notary signature on certificate', 'page_hint': 1, 'fatal': True},
        {'field': 'signer_signature', 'label': 'Signer signature', 'page_hint': 1, 'fatal': True},
    ],
    'ron': [
        {'field': 'notary_signature', 'label': 'Digital notary signature', 'page_hint': 1, 'fatal': True},
        {'field': 'signer_signature', 'label': 'Signer e-signature', 'page_hint': 1, 'fatal': True},
    ],
    'fingerprint': [
        {'field': 'applicant_signature', 'label': 'Applicant signature on FD-258', 'page_hint': 1, 'fatal': True},
    ],
    'nemt': [
        {'field': 'passenger_signature', 'label': 'Passenger signature on trip log', 'page_hint': 1, 'fatal': False},
        {'field': 'driver_signature', 'label': 'Driver signature', 'page_hint': 1, 'fatal': False},
    ],
    'process': [
        {'field': 'server_signature', 'label': 'Process server signature on affidavit', 'page_hint': 1, 'fatal': True},
    ],
    'medical_courier': [
        {'field': 'recipient_signature', 'label': 'Recipient signature on delivery', 'page_hint': 1, 'fatal': False},
    ],
}


def _build_signature_prompt(service_type: str, fields: list) -> str:
    """Build a structured prompt for the vision model to detect signatures."""
    field_desc = '\n'.join(
        f'  - "{f["label"]}" (field: {f["field"]}, FATAL={f["fatal"]})'
        for f in fields
    )
    return (
        f'You are a document QC reviewer for a {service_type} order.\n'
        f'Analyze this form image and determine whether the following signature fields '
        f'contain a valid handwritten or digital signature:\n{field_desc}\n\n'
        f'For each field, respond with JSON:\n'
        f'{{"signatures": [{{"field": "<field_name>", "present": true/false, '
        f'"confidence": 0.0-1.0, "notes": "brief observation"}}]}}\n'
        f'Only return valid JSON, no other text.'
    )


def detect_signatures(image_b64: str, service_type: str) -> dict:
    """Run signature detection on a base64-encoded image.
    Returns per-field presence, confidence, and fatality classification."""
    fields = SIGNATURE_FIELD_MAP.get(service_type, [])
    if not fields:
        return {
            'service_type': service_type,
            'signatures': [],
            'note': 'No signature fields defined for this service type',
        }

    prompt = _build_signature_prompt(service_type, fields)
    raw = _call_vision_model(prompt, image_b64)
    parsed = _parse_json_response(raw)

    sigs = parsed.get('signatures', [])
    fatal_missing = [
        s for s in sigs
        if not s.get('present', False)
        and any(f['field'] == s.get('field') and f['fatal'] for f in fields)
    ]
    low_confidence = [s for s in sigs if s.get('confidence', 1.0) < 0.7]

    return {
        'service_type': service_type,
        'signatures': sigs,
        'fatal_missing': [s['field'] for s in fatal_missing],
        'low_confidence': [s['field'] for s in low_confidence],
        'all_present': len(fatal_missing) == 0,
        'needs_human_review': len(low_confidence) > 0,
        'analyzed_at': datetime.now().isoformat(),
    }


# ═══════════════════════════════════════════════════════════════════
# 2. FORM FIELD EXTRACTION (OCR + Structured Output)
# ═══════════════════════════════════════════════════════════════════

EXTRACTION_SCHEMAS = {
    'ccf': {
        'form_name': 'Federal Custody and Control Form (CCF)',
        'fields': [
            {'key': 'specimen_id', 'label': 'Specimen ID number', 'required': True},
            {'key': 'donor_name', 'label': 'Donor / Employee name', 'required': True},
            {'key': 'donor_ssn_last4', 'label': 'Donor SSN last 4 (if visible)', 'required': False},
            {'key': 'collection_date', 'label': 'Date of collection', 'required': True},
            {'key': 'collection_time', 'label': 'Time of collection', 'required': True},
            {'key': 'temperature', 'label': 'Specimen temperature (°F)', 'required': True},
            {'key': 'temp_in_range', 'label': 'Temperature 90-100°F checkbox', 'required': True},
            {'key': 'test_reason', 'label': 'Reason for test (pre-employment, random, post-accident, etc.)', 'required': True},
            {'key': 'collector_name', 'label': 'Collector name', 'required': True},
            {'key': 'employer_name', 'label': 'Employer / Company name', 'required': False},
            {'key': 'split_specimen', 'label': 'Split specimen collected (yes/no)', 'required': False},
            {'key': 'volume_ml', 'label': 'Specimen volume (mL) if indicated', 'required': False},
        ],
    },
    'atf': {
        'form_name': 'Alcohol Testing Form (ATF)',
        'fields': [
            {'key': 'employee_name', 'label': 'Employee name', 'required': True},
            {'key': 'screening_result', 'label': 'Screening test BrAC result', 'required': True},
            {'key': 'screening_time', 'label': 'Screening test time', 'required': True},
            {'key': 'confirm_result', 'label': 'Confirmation test BrAC result', 'required': False},
            {'key': 'confirm_time', 'label': 'Confirmation test time', 'required': False},
            {'key': 'ebt_serial', 'label': 'EBT device serial number', 'required': True},
            {'key': 'bat_name', 'label': 'BAT / STT name', 'required': True},
            {'key': 'test_reason', 'label': 'Reason for test', 'required': True},
        ],
    },
    'notarial_cert': {
        'form_name': 'Notarial Certificate',
        'fields': [
            {'key': 'notary_name', 'label': 'Notary name', 'required': True},
            {'key': 'commission_number', 'label': 'Commission / appointment number', 'required': True},
            {'key': 'commission_expiry', 'label': 'Commission expiration date', 'required': True},
            {'key': 'county_venue', 'label': 'County / venue', 'required': True},
            {'key': 'state', 'label': 'State', 'required': True},
            {'key': 'act_type', 'label': 'Notarial act type (acknowledgment / jurat / oath)', 'required': True},
            {'key': 'signer_name', 'label': 'Signer name', 'required': True},
            {'key': 'notarization_date', 'label': 'Date of notarization', 'required': True},
            {'key': 'seal_present', 'label': 'Seal / stamp visible (yes/no)', 'required': True},
        ],
    },
    'fd258': {
        'form_name': 'FBI FD-258 Fingerprint Card',
        'fields': [
            {'key': 'name', 'label': 'Name (last, first, middle)', 'required': True},
            {'key': 'date_of_birth', 'label': 'Date of birth', 'required': True},
            {'key': 'ori', 'label': 'ORI number', 'required': True},
            {'key': 'agency', 'label': 'Contributing agency', 'required': True},
            {'key': 'date_printed', 'label': 'Date fingerprints taken', 'required': True},
            {'key': 'reason', 'label': 'Reason fingerprinted', 'required': False},
        ],
    },
    'trip_log': {
        'form_name': 'NEMT Trip Log / Manifest',
        'fields': [
            {'key': 'passenger_name', 'label': 'Passenger name', 'required': True},
            {'key': 'pickup_time', 'label': 'Pickup time', 'required': True},
            {'key': 'pickup_address', 'label': 'Pickup address', 'required': True},
            {'key': 'dropoff_time', 'label': 'Drop-off time', 'required': True},
            {'key': 'dropoff_address', 'label': 'Drop-off address', 'required': True},
            {'key': 'mileage', 'label': 'Trip mileage', 'required': False},
            {'key': 'passenger_signature', 'label': 'Passenger signature present (yes/no)', 'required': True},
            {'key': 'driver_name', 'label': 'Driver name', 'required': True},
        ],
    },
}

SERVICE_TO_FORM_TYPE = {
    'dot':          'ccf',
    'non-dot':      'ccf',
    'notary':       'notarial_cert',
    'ron':          'notarial_cert',
    'fingerprint':  'fd258',
    'nemt':         'trip_log',
}


def _build_extraction_prompt(form_type: str) -> str:
    """Build a structured prompt for field extraction."""
    schema = EXTRACTION_SCHEMAS.get(form_type)
    if not schema:
        return ''
    fields_desc = '\n'.join(
        f'  - {f["key"]}: {f["label"]} ({"required" if f["required"] else "optional"})'
        for f in schema['fields']
    )
    return (
        f'You are a document processor for a {schema["form_name"]}.\n'
        f'Extract the following fields from this form image. '
        f'If a field is not visible or illegible, set its value to null.\n\n'
        f'Fields:\n{fields_desc}\n\n'
        f'Respond with JSON:\n'
        f'{{"form_type": "{form_type}", "fields": {{"field_key": "extracted_value", ...}}, '
        f'"confidence": 0.0-1.0, "notes": "any issues"}}\n'
        f'Only return valid JSON, no other text.'
    )


def extract_form_fields(image_b64: str, form_type: str) -> dict:
    """Extract structured fields from a form image using vision model."""
    schema = EXTRACTION_SCHEMAS.get(form_type)
    if not schema:
        return {
            'form_type': form_type,
            'fields': {},
            'error': f'No extraction schema for form type: {form_type}',
        }

    prompt = _build_extraction_prompt(form_type)
    raw = _call_vision_model(prompt, image_b64)
    parsed = _parse_json_response(raw)

    extracted_fields = parsed.get('fields', {})
    missing_required = [
        f['key'] for f in schema['fields']
        if f['required'] and not extracted_fields.get(f['key'])
    ]

    return {
        'form_type': form_type,
        'form_name': schema['form_name'],
        'fields': extracted_fields,
        'missing_required': missing_required,
        'all_required_present': len(missing_required) == 0,
        'confidence': parsed.get('confidence', 0.0),
        'notes': parsed.get('notes', ''),
        'extracted_at': datetime.now().isoformat(),
    }


# ═══════════════════════════════════════════════════════════════════
# 3. PAGE CLASSIFICATION
# ═══════════════════════════════════════════════════════════════════

PAGE_TYPES = [
    'ccf',
    'atf',
    'chain_of_custody',
    'consent_form',
    'photo_id',
    'notarial_certificate',
    'fd258_fingerprint_card',
    'trip_log',
    'delivery_confirmation',
    'proof_of_service',
    'apostille_certificate',
    'property_photo',
    'inspection_report',
    'dna_collection_form',
    'lab_report',
    'seal_page',
    'unknown',
]


def classify_page(image_b64: str) -> dict:
    """Classify a single page image into a known document type."""
    prompt = (
        'You are a document classifier for a compliance QC system.\n'
        'Identify which document type this page image represents.\n\n'
        f'Possible types: {", ".join(PAGE_TYPES)}\n\n'
        'Respond with JSON:\n'
        '{"page_type": "<type>", "confidence": 0.0-1.0, '
        '"description": "brief description of what you see"}\n'
        'Only return valid JSON, no other text.'
    )
    raw = _call_vision_model(prompt, image_b64)
    parsed = _parse_json_response(raw)

    page_type = parsed.get('page_type', 'unknown')
    if page_type not in PAGE_TYPES:
        page_type = 'unknown'

    return {
        'page_type': page_type,
        'confidence': parsed.get('confidence', 0.0),
        'description': parsed.get('description', ''),
        'classified_at': datetime.now().isoformat(),
    }


def classify_multi_page(images_b64: list) -> dict:
    """Classify each page in a multi-page upload."""
    pages = []
    for i, img in enumerate(images_b64):
        result = classify_page(img)
        result['page_number'] = i + 1
        pages.append(result)
    return {
        'total_pages': len(pages),
        'pages': pages,
        'classified_at': datetime.now().isoformat(),
    }


# ═══════════════════════════════════════════════════════════════════
# 4. SEAL / STAMP DETECTION
# ═══════════════════════════════════════════════════════════════════

def detect_seal_or_stamp(image_b64: str, expected_type: str = 'notary') -> dict:
    """Detect presence of notary seal, embossed stamp, or official letterhead."""
    prompt = (
        f'You are inspecting a document for a {expected_type} order.\n'
        'Check whether a seal, embossed stamp, or official stamp is present on this image.\n\n'
        'Respond with JSON:\n'
        '{"seal_present": true/false, "seal_type": "ink_stamp|embossed|digital|none", '
        '"confidence": 0.0-1.0, "legible": true/false, '
        '"notes": "brief observation about seal quality/completeness"}\n'
        'Only return valid JSON, no other text.'
    )
    raw = _call_vision_model(prompt, image_b64)
    parsed = _parse_json_response(raw)

    return {
        'seal_present': parsed.get('seal_present', False),
        'seal_type': parsed.get('seal_type', 'none'),
        'confidence': parsed.get('confidence', 0.0),
        'legible': parsed.get('legible', False),
        'notes': parsed.get('notes', ''),
        'fatal_if_missing': expected_type in ('notary', 'ron', 'apostille'),
        'analyzed_at': datetime.now().isoformat(),
    }


# ═══════════════════════════════════════════════════════════════════
# 5. PHOTO QUALITY SCORING (Field Ops / REO)
# ═══════════════════════════════════════════════════════════════════

def score_photo_quality(image_b64: str, expected_subject: str = '') -> dict:
    """Score a field operations photo for QC compliance.
    Checks blur, darkness, framing, and subject recognition."""
    subject_hint = f' The expected subject is: {expected_subject}.' if expected_subject else ''
    prompt = (
        f'You are a QC reviewer for field service property photos.{subject_hint}\n'
        'Evaluate this photo for quality and usability:\n'
        '1. Is it blurry? (0-10, 10=crystal clear)\n'
        '2. Is it properly lit? (0-10, 10=perfectly lit)\n'
        '3. Is the framing acceptable? (0-10, 10=perfectly framed)\n'
        '4. Can you identify the subject/room? What is it?\n\n'
        'Respond with JSON:\n'
        '{"sharpness": 0-10, "lighting": 0-10, "framing": 0-10, '
        '"overall_score": 0-10, "subject_identified": "description", '
        '"pass": true/false, "issues": ["list of problems"]}\n'
        'Only return valid JSON, no other text.'
    )
    raw = _call_vision_model(prompt, image_b64)
    parsed = _parse_json_response(raw)

    overall = parsed.get('overall_score', 5)
    return {
        'sharpness': parsed.get('sharpness', 5),
        'lighting': parsed.get('lighting', 5),
        'framing': parsed.get('framing', 5),
        'overall_score': overall,
        'subject_identified': parsed.get('subject_identified', ''),
        'pass': parsed.get('pass', overall >= 5),
        'issues': parsed.get('issues', []),
        'scored_at': datetime.now().isoformat(),
    }


# ═══════════════════════════════════════════════════════════════════
# FULL DOCUMENT AI PIPELINE — orchestrates all checks on a scanback
# ═══════════════════════════════════════════════════════════════════

def run_document_ai_pipeline(
    images_b64: list,
    service_type: str,
    order_id: str = '',
) -> dict:
    """Run the full Tier 2 pipeline on a set of uploaded page images.

    Steps:
    1. Classify each page
    2. Detect signatures on relevant pages
    3. Extract form fields from classified forms
    4. Detect seals on notary/apostille pages
    5. Score photo quality on property photos

    Returns a consolidated result that feeds into the rule engine.
    """
    pipeline_result = {
        'order_id': order_id,
        'service_type': service_type,
        'total_pages': len(images_b64),
        'classification': None,
        'signature_detection': None,
        'field_extraction': None,
        'seal_detection': None,
        'photo_scores': [],
        'fatal_flags': [],
        'warnings': [],
        'ran_at': datetime.now().isoformat(),
    }

    # Step 1: Page classification
    classification = classify_multi_page(images_b64)
    pipeline_result['classification'] = classification

    # Step 2: Signature detection on the first relevant page
    if images_b64:
        sig_result = detect_signatures(images_b64[0], service_type)
        pipeline_result['signature_detection'] = sig_result
        for missing_field in sig_result.get('fatal_missing', []):
            pipeline_result['fatal_flags'].append(f'SIGNATURE MISSING: {missing_field}')
        if sig_result.get('needs_human_review'):
            pipeline_result['warnings'].append('Low-confidence signature detection — route to human review')

    # Step 3: Field extraction from the appropriate form type
    form_type = SERVICE_TO_FORM_TYPE.get(service_type)
    if form_type and images_b64:
        extraction = extract_form_fields(images_b64[0], form_type)
        pipeline_result['field_extraction'] = extraction
        for mf in extraction.get('missing_required', []):
            pipeline_result['warnings'].append(f'FIELD MISSING: {mf} on {form_type}')

    # Step 4: Seal detection for notary / apostille / RON
    if service_type in ('notary', 'ron', 'apostille') and images_b64:
        seal_page_idx = _find_page_by_type(classification, ['notarial_certificate', 'seal_page', 'apostille_certificate'])
        seal_img = images_b64[seal_page_idx] if seal_page_idx < len(images_b64) else images_b64[0]
        seal_result = detect_seal_or_stamp(seal_img, expected_type=service_type)
        pipeline_result['seal_detection'] = seal_result
        if not seal_result.get('seal_present') and seal_result.get('fatal_if_missing'):
            pipeline_result['fatal_flags'].append(f'SEAL/STAMP NOT DETECTED on {service_type} document')

    # Step 5: Photo quality for property/field ops pages
    for i, pg in enumerate(classification.get('pages', [])):
        if pg.get('page_type') == 'property_photo':
            score = score_photo_quality(images_b64[i])
            score['page_number'] = i + 1
            pipeline_result['photo_scores'].append(score)
            if not score.get('pass'):
                pipeline_result['warnings'].append(f'Photo page {i + 1} failed quality check: {", ".join(score.get("issues", []))}')

    # Persist result
    if order_id:
        result_path = os.path.join(RESULTS_DIR, f'{order_id}.json')
        try:
            with open(result_path, 'w') as f:
                json.dump(pipeline_result, f, indent=2, default=str)
        except IOError:
            pass

    return pipeline_result


def _find_page_by_type(classification: dict, target_types: list) -> int:
    """Return index of the first page matching any of the target types."""
    for pg in classification.get('pages', []):
        if pg.get('page_type') in target_types:
            return pg.get('page_number', 1) - 1
    return 0


# ═══════════════════════════════════════════════════════════════════
# 6. SIGNATURE REFERENCE MAP SYSTEM
#
# Phase A — Map: analyze a reference document from escrow / title / lender
#   to discover exactly WHERE and WHO needs to sign, initial, date, or stamp.
#   Produces a structured per-page requirement list stored per order.
#
# Phase B — Verify: when the agent uploads a completed scanback, compare
#   every page against its requirements from the map. Flag any missing
#   signature / initial / notary stamp as an error (fatal or warning).
# ═══════════════════════════════════════════════════════════════════

SIGNER_TYPES = [
    'buyer',
    'co_buyer',
    'seller',
    'co_seller',
    'borrower',
    'co_borrower',
    'title_agent',
    'escrow_officer',
    'notary',
    'witness',
    'lender_representative',
    'attorney',
    'trustee',
    'authorized_signatory',
    'collecting_agent',
    'donor',
    'participant',
    'guardian',
    'other',
]

REQUIREMENT_TYPES = [
    'signature',
    'initials',
    'notary_stamp',
    'notary_signature',
    'date',
    'witness_signature',
    'witness_initials',
    'lender_stamp',
    'title_stamp',
    'acknowledgment',
]

FATAL_REQUIREMENT_TYPES = {
    'signature',
    'notary_stamp',
    'notary_signature',
    'witness_signature',
}

FATAL_SIGNER_TYPES = {
    'buyer',
    'borrower',
    'seller',
    'notary',
    'title_agent',
    'escrow_officer',
    'collecting_agent',
    'donor',
}


def _build_signature_map_prompt(total_pages: int, document_context: str = '') -> str:
    """Build the prompt that identifies ALL required signature/initial/stamp locations
    in a reference document. Sent page-by-page; total_pages gives global context."""
    ctx = f' Document context: {document_context}.' if document_context else ''
    signer_list = ', '.join(SIGNER_TYPES)
    req_list = ', '.join(REQUIREMENT_TYPES)
    return (
        f'You are a document QC analyst reviewing page {"{PAGE_NUM}"} of {total_pages} '
        f'in a document package.{ctx}\n\n'
        f'Identify every location on this page where a signature, initials, date, notary stamp, '
        f'or other attestation is required (blank lines, signature blocks, "Sign here" tabs, '
        f'"Initial here" boxes, notary blocks, witness blocks, stamp boxes).\n\n'
        f'For each requirement found, output:\n'
        f'  - signer_type: one of [{signer_list}]\n'
        f'  - signer_label: descriptive label (e.g. "Buyer 1", "Settlement Agent")\n'
        f'  - requirement_type: one of [{req_list}]\n'
        f'  - location_description: where on the page (e.g. "bottom-right, above printed \'Buyer\' line")\n'
        f'  - context: surrounding text label (e.g. "Borrower\'s Signature", "Notary Public")\n'
        f'  - required: true if missing would be a defect\n\n'
        f'Respond with JSON:\n'
        f'{{"page": {"{PAGE_NUM}"}, "requirements": ['
        f'{{"signer_type": "...", "signer_label": "...", "requirement_type": "...", '
        f'"location_description": "...", "context": "...", "required": true/false}}]}}\n'
        f'If this page has no signature requirements, return {{"page": {"{PAGE_NUM}"}, "requirements": []}}.\n'
        f'Only return valid JSON, no other text.'
    )


def map_document_signatures(
    images_b64: list,
    order_id: str,
    document_type: str = '',
    document_context: str = '',
) -> dict:
    """Phase A — analyze reference document pages and build a signature requirement map.

    images_b64: list of base64-encoded page images (one per page)
    order_id: PRISM order ID — map will be stored at SIG_MAPS_DIR/<order_id>.json
    document_type: free-text (e.g. "Deed of Trust", "Loan Signing Package")
    document_context: optional context hint for the model (e.g. "Michigan closing package, 2 buyers")

    Returns the full signature map dict and persists it to disk.
    """
    total_pages = len(images_b64)
    all_requirements = []
    req_id_counter = 1

    for page_num, img in enumerate(images_b64, start=1):
        base_prompt = _build_signature_map_prompt(total_pages, document_context)
        prompt = base_prompt.replace('{PAGE_NUM}', str(page_num))
        raw = _call_vision_model(prompt, img)
        parsed = _parse_json_response(raw)
        page_reqs = parsed.get('requirements', [])

        for req in page_reqs:
            signer_type = req.get('signer_type', 'other')
            req_type = req.get('requirement_type', 'signature')
            is_fatal = (
                req.get('required', True)
                and req_type in FATAL_REQUIREMENT_TYPES
                and signer_type in FATAL_SIGNER_TYPES
            )
            all_requirements.append({
                'id': f'SIG-{req_id_counter:03d}',
                'page': page_num,
                'signer_type': signer_type,
                'signer_label': req.get('signer_label', signer_type.replace('_', ' ').title()),
                'requirement_type': req_type,
                'location_description': req.get('location_description', ''),
                'context': req.get('context', ''),
                'required': req.get('required', True),
                'fatal': is_fatal,
            })
            req_id_counter += 1

    sig_map = {
        'order_id': order_id,
        'document_type': document_type,
        'document_context': document_context,
        'total_pages': total_pages,
        'total_requirements': len(all_requirements),
        'requirements': all_requirements,
        'signer_summary': _summarize_signers(all_requirements),
        'mapped_at': datetime.now().isoformat(),
        'map_version': 1,
    }

    _save_signature_map(order_id, sig_map)
    return sig_map


def _summarize_signers(requirements: list) -> dict:
    """Build a summary of how many requirements exist per signer type."""
    summary: dict = {}
    for req in requirements:
        st = req.get('signer_type', 'other')
        if st not in summary:
            summary[st] = {'total': 0, 'fatal': 0, 'by_type': {}}
        summary[st]['total'] += 1
        if req.get('fatal'):
            summary[st]['fatal'] += 1
        rt = req.get('requirement_type', 'signature')
        summary[st]['by_type'][rt] = summary[st]['by_type'].get(rt, 0) + 1
    return summary


def _save_signature_map(order_id: str, sig_map: dict):
    """Persist a signature map to disk."""
    path = os.path.join(SIG_MAPS_DIR, f'{order_id}.json')
    try:
        with open(path, 'w') as f:
            json.dump(sig_map, f, indent=2, default=str)
    except IOError:
        pass


def load_signature_map(order_id: str) -> Optional[dict]:
    """Load a stored signature map for an order. Returns None if not found."""
    path = os.path.join(SIG_MAPS_DIR, f'{order_id}.json')
    if not os.path.exists(path):
        return None
    try:
        with open(path) as f:
            return json.load(f)
    except (IOError, json.JSONDecodeError):
        return None


def _build_verification_prompt(requirement: dict, page_num: int) -> str:
    """Build a focused verification prompt for a single requirement on a specific page."""
    signer = requirement.get('signer_label', requirement.get('signer_type', 'signer'))
    req_type = requirement.get('requirement_type', 'signature')
    location = requirement.get('location_description', 'on the page')
    context = requirement.get('context', '')
    context_hint = f' The surrounding label reads: "{context}".' if context else ''

    type_descriptions = {
        'signature': 'a handwritten or electronic full signature',
        'initials': 'handwritten or printed initials (2-3 letters)',
        'notary_stamp': 'an official notary seal, ink stamp, or embossed stamp',
        'notary_signature': 'a handwritten notary signature',
        'date': 'a written or printed date',
        'witness_signature': 'a witness handwritten signature',
        'witness_initials': 'witness initials',
        'lender_stamp': 'an official lender stamp or seal',
        'title_stamp': 'a title company stamp or seal',
        'acknowledgment': 'a written acknowledgment or certification text',
    }
    what = type_descriptions.get(req_type, f'a {req_type}')

    return (
        f'You are a document QC reviewer on page {page_num}.\n'
        f'Check whether {signer} has provided {what} at this location: {location}.{context_hint}\n\n'
        f'Look carefully at that specific area of the page. An empty line, blank box, or '
        f'missing mark is a defect. A faint or partial mark should be flagged as unclear.\n\n'
        f'Respond with JSON:\n'
        f'{{"present": true/false, "status": "present"|"missing"|"unclear", '
        f'"confidence": 0.0-1.0, "notes": "brief observation about what you see there"}}\n'
        f'Only return valid JSON, no other text.'
    )


def verify_signatures_against_map(
    images_b64: list,
    order_id: str,
    sig_map: dict = None,
) -> dict:
    """Phase B — verify a completed scanback document against the stored signature map.

    For each requirement in the map, inspects the corresponding page in images_b64 and
    reports present / missing / unclear. Missing fatal requirements become errors that
    block the scanback from being marked clean.

    images_b64: completed scanback pages (base64), in page order
    order_id: used to load map if sig_map not provided
    sig_map: optionally pass the map directly (skips disk load)
    """
    if sig_map is None:
        sig_map = load_signature_map(order_id)
    if not sig_map:
        return {
            'order_id': order_id,
            'verified': False,
            'error': 'No signature map found for this order. Upload a reference document first.',
        }

    requirements = sig_map.get('requirements', [])
    total_pages_available = len(images_b64)
    verified_items = []
    errors = []
    warnings = []

    for req in requirements:
        page_num = req.get('page', 1)
        page_idx = page_num - 1
        req_id = req.get('id', 'SIG-???')

        if page_idx >= total_pages_available:
            status = 'missing'
            confidence = 0.0
            notes = f'Page {page_num} not present in scanback upload ({total_pages_available} pages received)'
        else:
            prompt = _build_verification_prompt(req, page_num)
            raw = _call_vision_model(prompt, images_b64[page_idx])
            parsed = _parse_json_response(raw)
            status = parsed.get('status', 'missing' if not parsed.get('present', False) else 'present')
            confidence = parsed.get('confidence', 0.0)
            notes = parsed.get('notes', '')

        item = {
            'id': req_id,
            'page': page_num,
            'signer_type': req.get('signer_type', ''),
            'signer_label': req.get('signer_label', ''),
            'requirement_type': req.get('requirement_type', ''),
            'location_description': req.get('location_description', ''),
            'context': req.get('context', ''),
            'fatal': req.get('fatal', False),
            'status': status,
            'confidence': confidence,
            'notes': notes,
        }
        verified_items.append(item)

        if status == 'missing' and req.get('required', True):
            error_entry = {
                'id': req_id,
                'page': page_num,
                'signer_label': req.get('signer_label', req.get('signer_type', '')),
                'requirement_type': req.get('requirement_type', ''),
                'location': req.get('location_description', ''),
                'context': req.get('context', ''),
                'fatal': req.get('fatal', False),
                'severity': 'FATAL' if req.get('fatal') else 'WARNING',
                'description': (
                    f'{req.get("signer_label", "Signer")} — {req.get("requirement_type", "signature")} '
                    f'missing on page {page_num} ({req.get("location_description", "")})'
                ),
                'source': 'PRISM_SIG_VERIFY',
            }
            if req.get('fatal'):
                errors.append(error_entry)
            else:
                warnings.append(error_entry)
        elif status == 'unclear':
            warnings.append({
                'id': req_id,
                'page': page_num,
                'signer_label': req.get('signer_label', ''),
                'requirement_type': req.get('requirement_type', ''),
                'severity': 'REVIEW',
                'description': (
                    f'{req.get("signer_label", "Signer")} — {req.get("requirement_type", "signature")} '
                    f'unclear/illegible on page {page_num} — needs human confirmation'
                ),
                'source': 'PRISM_SIG_VERIFY',
            })

    # Count summaries
    present_count = sum(1 for i in verified_items if i['status'] == 'present')
    missing_count = sum(1 for i in verified_items if i['status'] == 'missing')
    unclear_count = sum(1 for i in verified_items if i['status'] == 'unclear')
    fatal_errors = [e for e in errors if e.get('fatal')]

    result = {
        'order_id': order_id,
        'map_version': sig_map.get('map_version', 1),
        'document_type': sig_map.get('document_type', ''),
        'total_requirements': len(requirements),
        'present': present_count,
        'missing': missing_count,
        'unclear': unclear_count,
        'all_satisfied': missing_count == 0 and len(fatal_errors) == 0,
        'has_fatal_errors': len(fatal_errors) > 0,
        'verified_items': verified_items,
        'errors': errors,
        'warnings': warnings,
        'verified_at': datetime.now().isoformat(),
    }

    # Persist verification result
    verify_path = os.path.join(SIG_MAPS_DIR, f'{order_id}_verify.json')
    try:
        with open(verify_path, 'w') as f:
            json.dump(result, f, indent=2, default=str)
    except IOError:
        pass

    return result


# ═══════════════════════════════════════════════════════════════════
# VISION MODEL INTERFACE — pluggable backend
# ═══════════════════════════════════════════════════════════════════

def _call_vision_model(prompt: str, image_b64: str) -> str:
    """Call the configured vision model with a text prompt and base64 image.
    Returns raw text response. Supports Claude and GPT-4o backends."""
    if VISION_PROVIDER == 'claude' and ANTHROPIC_API_KEY:
        return _call_claude_vision(prompt, image_b64)
    elif VISION_PROVIDER == 'openai' and OPENAI_API_KEY:
        return _call_openai_vision(prompt, image_b64)
    else:
        return _call_fallback(prompt)


def _call_claude_vision(prompt: str, image_b64: str) -> str:
    """Call Anthropic Claude with vision capability."""
    try:
        import httpx
        resp = httpx.post(
            'https://api.anthropic.com/v1/messages',
            headers={
                'x-api-key': ANTHROPIC_API_KEY,
                'anthropic-version': '2023-06-01',
                'content-type': 'application/json',
            },
            json={
                'model': 'claude-sonnet-4-20250514',
                'max_tokens': 1024,
                'messages': [{
                    'role': 'user',
                    'content': [
                        {
                            'type': 'image',
                            'source': {
                                'type': 'base64',
                                'media_type': 'image/jpeg',
                                'data': image_b64,
                            },
                        },
                        {'type': 'text', 'text': prompt},
                    ],
                }],
            },
            timeout=30.0,
        )
        data = resp.json()
        return data.get('content', [{}])[0].get('text', '')
    except Exception as e:
        return json.dumps({'error': str(e)})


def _call_openai_vision(prompt: str, image_b64: str) -> str:
    """Call OpenAI GPT-4o with vision capability."""
    try:
        import httpx
        resp = httpx.post(
            'https://api.openai.com/v1/chat/completions',
            headers={
                'Authorization': f'Bearer {OPENAI_API_KEY}',
                'Content-Type': 'application/json',
            },
            json={
                'model': 'gpt-4o',
                'max_tokens': 1024,
                'messages': [{
                    'role': 'user',
                    'content': [
                        {
                            'type': 'image_url',
                            'image_url': {
                                'url': f'data:image/jpeg;base64,{image_b64}',
                            },
                        },
                        {'type': 'text', 'text': prompt},
                    ],
                }],
            },
            timeout=30.0,
        )
        data = resp.json()
        return data.get('choices', [{}])[0].get('message', {}).get('content', '')
    except Exception as e:
        return json.dumps({'error': str(e)})


def _call_fallback(prompt: str) -> str:
    """Return a structured placeholder when no vision API key is configured.
    In production, swap for Tesseract / AWS Textract / Google Document AI."""
    return json.dumps({
        'note': 'No vision API key configured — returning placeholder.',
        'signatures': [],
        'fields': {},
        'page_type': 'unknown',
        'confidence': 0.0,
        'seal_present': False,
        'seal_type': 'none',
        'legible': False,
        'sharpness': 5,
        'lighting': 5,
        'framing': 5,
        'overall_score': 5,
        'pass': True,
        'issues': [],
        'subject_identified': '',
    })


def _parse_json_response(raw: str) -> dict:
    """Parse JSON from a model response, handling markdown fences."""
    text = raw.strip()
    if text.startswith('```'):
        lines = text.split('\n')
        lines = [l for l in lines if not l.strip().startswith('```')]
        text = '\n'.join(lines)
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return {}


# ═══════════════════════════════════════════════════════════════════
# API ROUTES
# ═══════════════════════════════════════════════════════════════════

@prism_doc_ai.route('/prism/doc-ai/detect-signatures', methods=['POST'])
def api_detect_signatures():
    """Detect signatures on an uploaded form image.
    Body: { image_b64: "<base64>", service_type: "dot" }"""
    data = request.get_json(silent=True) or {}
    image_b64 = data.get('image_b64', '')
    service_type = data.get('service_type', '')
    if not image_b64 or not service_type:
        return jsonify({'error': 'image_b64 and service_type are required'}), 400
    result = detect_signatures(image_b64, service_type)
    return jsonify(result)


@prism_doc_ai.route('/prism/doc-ai/extract-fields', methods=['POST'])
def api_extract_fields():
    """Extract structured fields from a form image.
    Body: { image_b64: "<base64>", form_type: "ccf" }"""
    data = request.get_json(silent=True) or {}
    image_b64 = data.get('image_b64', '')
    form_type = data.get('form_type', '')
    if not image_b64 or not form_type:
        return jsonify({'error': 'image_b64 and form_type are required'}), 400
    result = extract_form_fields(image_b64, form_type)
    return jsonify(result)


@prism_doc_ai.route('/prism/doc-ai/classify-page', methods=['POST'])
def api_classify_page():
    """Classify a document page image.
    Body: { image_b64: "<base64>" }"""
    data = request.get_json(silent=True) or {}
    image_b64 = data.get('image_b64', '')
    if not image_b64:
        return jsonify({'error': 'image_b64 is required'}), 400
    result = classify_page(image_b64)
    return jsonify(result)


@prism_doc_ai.route('/prism/doc-ai/classify-multi', methods=['POST'])
def api_classify_multi():
    """Classify multiple pages in a multi-page upload.
    Body: { images_b64: ["<base64>", ...] }"""
    data = request.get_json(silent=True) or {}
    images = data.get('images_b64', [])
    if not images:
        return jsonify({'error': 'images_b64 array is required'}), 400
    result = classify_multi_page(images)
    return jsonify(result)


@prism_doc_ai.route('/prism/doc-ai/detect-seal', methods=['POST'])
def api_detect_seal():
    """Detect notary seal / stamp / letterhead.
    Body: { image_b64: "<base64>", expected_type: "notary" }"""
    data = request.get_json(silent=True) or {}
    image_b64 = data.get('image_b64', '')
    expected_type = data.get('expected_type', 'notary')
    if not image_b64:
        return jsonify({'error': 'image_b64 is required'}), 400
    result = detect_seal_or_stamp(image_b64, expected_type)
    return jsonify(result)


@prism_doc_ai.route('/prism/doc-ai/photo-quality', methods=['POST'])
def api_photo_quality():
    """Score a property / field ops photo for quality.
    Body: { image_b64: "<base64>", expected_subject: "kitchen" }"""
    data = request.get_json(silent=True) or {}
    image_b64 = data.get('image_b64', '')
    expected_subject = data.get('expected_subject', '')
    if not image_b64:
        return jsonify({'error': 'image_b64 is required'}), 400
    result = score_photo_quality(image_b64, expected_subject)
    return jsonify(result)


@prism_doc_ai.route('/prism/doc-ai/pipeline', methods=['POST'])
def api_run_pipeline():
    """Run the full document AI pipeline on uploaded scanback images.
    Body: { images_b64: ["<base64>", ...], service_type: "dot", order_id: "ORD-2026-001" }"""
    data = request.get_json(silent=True) or {}
    images = data.get('images_b64', [])
    service_type = data.get('service_type', '')
    order_id = data.get('order_id', '')
    if not images or not service_type:
        return jsonify({'error': 'images_b64 and service_type are required'}), 400
    result = run_document_ai_pipeline(images, service_type, order_id)
    return jsonify(result)


@prism_doc_ai.route('/prism/doc-ai/schemas', methods=['GET'])
def api_list_schemas():
    """List available form extraction schemas."""
    schemas = {k: {'form_name': v['form_name'], 'field_count': len(v['fields'])}
               for k, v in EXTRACTION_SCHEMAS.items()}
    return jsonify({
        'schemas': schemas,
        'page_types': PAGE_TYPES,
        'signature_services': list(SIGNATURE_FIELD_MAP.keys()),
    })


# ─── Signature Reference Map endpoints ─────────────────────────────

@prism_doc_ai.route('/prism/doc-ai/map-signatures', methods=['POST'])
def api_map_signatures():
    """Phase A: Analyze a reference document and build the signature requirement map.

    Call this when the document package arrives from escrow / title / lender,
    BEFORE the agent goes to the signing appointment. The resulting map becomes
    the reference point for scanback verification.

    Body: {
      order_id: "ORD-2026-001",
      images_b64: ["<page1_base64>", "<page2_base64>", ...],
      document_type: "Deed of Trust",          // optional label
      document_context: "Michigan closing, 2 buyers, 1 notary"  // optional hint
    }

    Returns the full signature map with every signer type, page, location, and fatality.
    """
    data = request.get_json(silent=True) or {}
    order_id = data.get('order_id', '')
    images = data.get('images_b64', [])
    document_type = data.get('document_type', '')
    document_context = data.get('document_context', '')

    if not order_id or not images:
        return jsonify({'error': 'order_id and images_b64 are required'}), 400

    sig_map = map_document_signatures(
        images_b64=images,
        order_id=order_id,
        document_type=document_type,
        document_context=document_context,
    )
    return jsonify(sig_map)


@prism_doc_ai.route('/prism/doc-ai/verify-signatures', methods=['POST'])
def api_verify_signatures():
    """Phase B: Verify a completed scanback against the stored signature map.

    Call this when the agent submits the signed document package as a scanback.
    Compares each page against the reference map requirements and flags any
    missing signature, initials, or notary stamp as a FATAL or WARNING error.

    Body: {
      order_id: "ORD-2026-001",
      images_b64: ["<completed_page1_base64>", ...]
    }

    Returns: all_satisfied bool, error list, warning list, per-requirement statuses.
    """
    data = request.get_json(silent=True) or {}
    order_id = data.get('order_id', '')
    images = data.get('images_b64', [])

    if not order_id or not images:
        return jsonify({'error': 'order_id and images_b64 are required'}), 400

    result = verify_signatures_against_map(
        images_b64=images,
        order_id=order_id,
    )
    return jsonify(result)


@prism_doc_ai.route('/prism/doc-ai/signature-map/<order_id>', methods=['GET'])
def api_get_signature_map(order_id):
    """Return the stored signature map for an order."""
    sig_map = load_signature_map(order_id)
    if not sig_map:
        return jsonify({'error': f'No signature map found for order {order_id}'}), 404
    return jsonify(sig_map)


@prism_doc_ai.route('/prism/doc-ai/signature-map/<order_id>', methods=['DELETE'])
def api_delete_signature_map(order_id):
    """Delete the signature map for an order (e.g. when re-mapping with a corrected doc)."""
    path = os.path.join(SIG_MAPS_DIR, f'{order_id}.json')
    verify_path = os.path.join(SIG_MAPS_DIR, f'{order_id}_verify.json')
    deleted = []
    for p in (path, verify_path):
        if os.path.exists(p):
            try:
                os.remove(p)
                deleted.append(p)
            except IOError:
                pass
    return jsonify({'deleted': len(deleted), 'order_id': order_id})


@prism_doc_ai.route('/prism/doc-ai/verification-result/<order_id>', methods=['GET'])
def api_get_verification_result(order_id):
    """Return the most recent verification result for an order's scanback."""
    verify_path = os.path.join(SIG_MAPS_DIR, f'{order_id}_verify.json')
    if not os.path.exists(verify_path):
        return jsonify({'error': f'No verification result found for order {order_id}'}), 404
    try:
        with open(verify_path) as f:
            return jsonify(json.load(f))
    except (IOError, json.JSONDecodeError):
        return jsonify({'error': 'Could not read verification result'}), 500


@prism_doc_ai.route('/prism/doc-ai/signer-types', methods=['GET'])
def api_signer_types():
    """Return all recognized signer types, requirement types, and fatality rules."""
    return jsonify({
        'signer_types': SIGNER_TYPES,
        'requirement_types': REQUIREMENT_TYPES,
        'fatal_requirement_types': list(FATAL_REQUIREMENT_TYPES),
        'fatal_signer_types': list(FATAL_SIGNER_TYPES),
    })
