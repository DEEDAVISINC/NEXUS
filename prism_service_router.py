#!/usr/bin/env python3
"""
PRISM SERVICE ROUTER — DDI DUAL-LAYER FULFILLMENT ENGINE
=========================================================
The operational brain of DDI's business model:

  LAYER 1: DDI manages the program (C/TPA, prime contractor, brokerage)
  LAYER 2: DDI operates what it can reach → partners fill the rest

For every incoming order, the router decides:
  → DDI_DIRECT:  DDI performs the service (100% revenue, no sub cost)
  → PARTNER:     Route to a named partner (DDI keeps management margin)

DDI's partner network by service line:
  Drug Testing:     Quest Diagnostics, eScreen, Concentra
  DNA Testing:      DDC Laboratories (AABB-accredited)
  Fingerprinting:   Lakota, IdentoGO (overflow/out-of-area)
  Medical Courier:  Freight 1st Direct (DDI-controlled), courier subs
  NEMT:             Uber Health, Lyft Healthcare, local NEMT operators
  Occupational Hlth: Concentra, local occupational health clinics
  Lab Analysis:     Quest, CRL, Labcorp (ALWAYS — DDI never runs a lab)

DDI_DIRECT service area: Metro Detroit / Southeast Michigan (default).
Geography can be overridden per order or at the account level.

Reference: DDI_BUSINESS_MODEL.md, DEE_DAVIS_INC_COMPLETE_SERVICE_CATALOG.md
"""

import os
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from flask import Blueprint, request, jsonify

prism_router = Blueprint('prism_router', __name__)

# ═══════════════════════════════════════════════════════════════════
# DDI SERVICE AREA (geographic coverage for DDI_DIRECT operations)
# ═══════════════════════════════════════════════════════════════════

DDI_DIRECT_COUNTIES = [
    'Wayne', 'Oakland', 'Macomb', 'Washtenaw', 'Livingston',
    'Monroe', 'St. Clair', 'Lapeer', 'Genesee',
]

DDI_DIRECT_STATES = ['MI']  # expand as DDI grows mobile ops

DDI_DIRECT_METRO = 'Metro Detroit / Southeast Michigan'

# ═══════════════════════════════════════════════════════════════════
# SERVICE LINE DEFINITIONS
# ═══════════════════════════════════════════════════════════════════

# For each service type:
#   ddi_capable:   Can DDI perform this directly (with collector cert / mobile unit)?
#   lab_required:  Does this need a third-party lab regardless?
#   partners:      Ordered list of preferred partners (first = primary)
#   ddi_rate:      What DDI charges the client (agency rate)
#   sub_cost_low:  DDI's cost when using a partner (low estimate)
#   sub_cost_high: DDI's cost when using a partner (high estimate)
#   ddi_direct_cost: DDI's cost when operating directly (supplies/mileage only)
#   notes:         Routing guidance

SERVICE_CATALOG = {

    # ─── DRUG TESTING ───────────────────────────────────────────────
    'dot_drug_test': {
        'label':            'DOT 5-Panel Urine Drug Test',
        'service_line':     'Drug Testing',
        'ddi_capable':      True,
        'lab_required':     True,
        'lab_partners':     ['Quest Diagnostics', 'eScreen', 'CRL', 'Labcorp'],
        'collection_partners': ['Concentra', 'eScreen Network', 'Quest PSC Network'],
        'ddi_rate':         125,
        'sub_cost_low':     55,
        'sub_cost_high':    75,
        'ddi_direct_cost':  20,   # supplies + mileage when DDI collects
        'lab_cost':         30,   # lab analysis — always a cost even when DDI collects
        'notes':            'DDI can collect locally. Lab analysis always routes to Quest/eScreen. MRO required for positives.',
    },
    'non_dot_drug_test': {
        'label':            'Non-DOT Drug Test (5-Panel)',
        'service_line':     'Drug Testing',
        'ddi_capable':      True,
        'lab_required':     True,
        'lab_partners':     ['Quest Diagnostics', 'eScreen', 'Labcorp'],
        'collection_partners': ['Concentra', 'Quest PSC Network'],
        'ddi_rate':         85,
        'sub_cost_low':     40,
        'sub_cost_high':    55,
        'ddi_direct_cost':  15,
        'lab_cost':         25,
        'notes':            'DDI can collect locally. No MRO required for negatives.',
    },
    'non_dot_drug_test_10panel': {
        'label':            'Non-DOT Drug Test (10-Panel)',
        'service_line':     'Drug Testing',
        'ddi_capable':      True,
        'lab_required':     True,
        'lab_partners':     ['Quest Diagnostics', 'eScreen', 'Labcorp'],
        'collection_partners': ['Concentra', 'Quest PSC Network'],
        'ddi_rate':         125,
        'sub_cost_low':     55,
        'sub_cost_high':    70,
        'ddi_direct_cost':  15,
        'lab_cost':         35,
        'notes':            '10-panel expanded screening.',
    },
    'dot_alcohol_test': {
        'label':            'DOT Breath Alcohol Test (BAT)',
        'service_line':     'Drug Testing',
        'ddi_capable':      True,
        'lab_required':     False,
        'lab_partners':     [],
        'collection_partners': ['Concentra', 'Quest PSC Network'],
        'ddi_rate':         85,
        'sub_cost_low':     40,
        'sub_cost_high':    55,
        'ddi_direct_cost':  10,   # evidentiary breath device amortized
        'lab_cost':         0,
        'notes':            'Requires certified BAT device. DDI can operate locally with proper equipment.',
    },
    'post_accident_drug': {
        'label':            'Post-Accident Drug Test (DOT)',
        'service_line':     'Drug Testing',
        'ddi_capable':      True,
        'lab_required':     True,
        'lab_partners':     ['Quest Diagnostics', 'eScreen'],
        'collection_partners': ['Concentra', 'Quest PSC Network'],
        'ddi_rate':         150,
        'sub_cost_low':     70,
        'sub_cost_high':    85,
        'ddi_direct_cost':  20,
        'lab_cost':         30,
        'urgent':           True,
        'notes':            'URGENT — must complete within 32 hours of accident. Route to fastest available collector.',
    },
    'return_to_duty_test': {
        'label':            'Return-to-Duty Drug Test',
        'service_line':     'Drug Testing',
        'ddi_capable':      True,
        'lab_required':     True,
        'lab_partners':     ['Quest Diagnostics', 'eScreen'],
        'collection_partners': ['Concentra', 'Quest PSC Network'],
        'ddi_rate':         150,
        'sub_cost_low':     70,
        'sub_cost_high':    85,
        'ddi_direct_cost':  20,
        'lab_cost':         30,
        'clearinghouse_required': True,
        'notes':            'Must report negative result to FMCSA Clearinghouse. Triggers follow-up testing plan.',
    },
    'non_dot_drug_test_12panel_rapid': {
        'label':            'Non-DOT 12-Panel Rapid POCT (Instant Cup)',
        'service_line':     'Drug Testing',
        'ddi_capable':      True,
        'lab_required':     False,   # POCT = instant result, no lab unless confirmation needed
        'lab_partners':     ['Quest Diagnostics', 'eScreen'],   # for positive confirmations
        'collection_partners': [],
        'ddi_rate':         70,
        'sub_cost_low':     17,
        'sub_cost_high':    22,
        'ddi_direct_cost':  20,      # $2.09 cup (12PanelNow) + admin supplies
        'lab_cost':         0,       # no lab unless positive — then confirmation adds cost
        'supplier':         '12PanelNow',
        'supplier_cost_per_cup': 2.09,
        'notes':            'Rapid POCT cup from 12PanelNow ($2.09/cup). Instant result on-site. Positive results should be confirmed by lab. Ideal for courts, probation, social services.',
    },
    'non_dot_drug_test_12panel_lab': {
        'label':            'Non-DOT 12-Panel Lab-Confirmed',
        'service_line':     'Drug Testing',
        'ddi_capable':      True,
        'lab_required':     True,
        'lab_partners':     ['Quest Diagnostics', 'eScreen', 'Labcorp'],
        'collection_partners': ['Concentra', 'Quest PSC Network'],
        'ddi_rate':         150,
        'sub_cost_low':     65,
        'sub_cost_high':    85,
        'ddi_direct_cost':  20,
        'lab_cost':         45,
        'notes':            'Full lab confirmation. 12 substances including expanded opioids and buprenorphine. Court-admissible results.',
    },
    'non_dot_drug_test_12panel_oral': {
        'label':            'Non-DOT 12-Panel Oral Fluid',
        'service_line':     'Drug Testing',
        'ddi_capable':      True,
        'lab_required':     True,
        'lab_partners':     ['Quest Diagnostics', 'Psychemedics'],
        'collection_partners': [],
        'ddi_rate':         135,
        'sub_cost_low':     50,
        'sub_cost_high':    70,
        'ddi_direct_cost':  15,
        'lab_cost':         45,
        'notes':            'Oral fluid (saliva) collection. Detects recent use (1-3 days). Good for reasonable suspicion and post-accident.',
    },
    'hair_follicle_12panel': {
        'label':            'Hair Follicle 12-Panel Drug Test',
        'service_line':     'Drug Testing',
        'ddi_capable':      False,
        'lab_required':     True,
        'lab_partners':     ['Quest Diagnostics', 'Psychemedics'],
        'collection_partners': ['Concentra', 'Quest PSC Network'],
        'ddi_rate':         310,
        'sub_cost_low':     175,
        'sub_cost_high':    220,
        'ddi_direct_cost':  None,
        'lab_cost':         None,
        'notes':            '90-day detection window. 12-substance panel. Always route to Concentra or Quest PSC for collection.',
    },
    'hair_follicle_test': {
        'label':            'Hair Follicle Drug Test (5-Panel)',
        'service_line':     'Drug Testing',
        'ddi_capable':      False,   # requires specialized training
        'lab_required':     True,
        'lab_partners':     ['Quest Diagnostics', 'Psychemedics'],
        'collection_partners': ['Concentra', 'Quest PSC Network'],
        'ddi_rate':         275,
        'sub_cost_low':     150,
        'sub_cost_high':    200,
        'ddi_direct_cost':  None,
        'lab_cost':         None,
        'notes':            'Specialized collection — always route to Concentra or Quest PSC.',
    },
    'poct_confirmation_lab': {
        'label':            'POCT Positive Confirmation (Lab Send-Out)',
        'service_line':     'Drug Testing',
        'ddi_capable':      True,
        'lab_required':     True,
        'lab_partners':     ['Quest Diagnostics', 'eScreen', 'Labcorp'],
        'collection_partners': [],
        'ddi_rate':         85,
        'sub_cost_low':     35,
        'sub_cost_high':    55,
        'ddi_direct_cost':  10,
        'lab_cost':         40,
        'notes':            'Add-on when POCT rapid screen returns non-negative. Send split specimen to lab for GC/MS confirmation. Required before adverse action.',
    },

    # ─── DNA TESTING ────────────────────────────────────────────────
    'dna_legal_paternity': {
        'label':            'Legal Paternity DNA Test (Chain of Custody)',
        'service_line':     'DNA Testing',
        'ddi_capable':      True,
        'lab_required':     True,
        'lab_partners':     ['DDC Laboratories', 'AABB-accredited lab'],
        'collection_partners': [],
        'ddi_rate':         375,
        'sub_cost_low':     200,
        'sub_cost_high':    280,
        'ddi_direct_cost':  15,   # collection kit + chain of custody docs
        'lab_cost':         220,
        'notes':            'DePointe DNA. DDI collects cheek swabs. DDC handles lab. Chain of custody required.',
    },
    'dna_immigration': {
        'label':            'Immigration DNA Test (USCIS)',
        'service_line':     'DNA Testing',
        'ddi_capable':      True,
        'lab_required':     True,
        'lab_partners':     ['DDC Laboratories', 'AABB-accredited lab'],
        'collection_partners': [],
        'ddi_rate':         500,
        'sub_cost_low':     250,
        'sub_cost_high':    350,
        'ddi_direct_cost':  15,
        'lab_cost':         280,
        'notes':            'DePointe DNA. High-value. Immigration attorneys are referral sources. AABB-accredited lab required.',
    },
    'dna_informational': {
        'label':            'Informational DNA Test (Non-Legal)',
        'service_line':     'DNA Testing',
        'ddi_capable':      True,
        'lab_required':     True,
        'lab_partners':     ['DDC Laboratories', 'Identigene'],
        'collection_partners': [],
        'ddi_rate':         175,
        'sub_cost_low':     80,
        'sub_cost_high':    120,
        'ddi_direct_cost':  10,
        'lab_cost':         90,
        'notes':            'No chain of custody required. Home kit or mobile collection.',
    },
    'dna_siblingship': {
        'label':            'Siblingship / Grandparentage DNA Test',
        'service_line':     'DNA Testing',
        'ddi_capable':      True,
        'lab_required':     True,
        'lab_partners':     ['DDC Laboratories'],
        'collection_partners': [],
        'ddi_rate':         450,
        'sub_cost_low':     250,
        'sub_cost_high':    320,
        'ddi_direct_cost':  15,
        'lab_cost':         280,
        'notes':            'Complex relationship testing. DDC is the only lab.',
    },

    # ─── FINGERPRINTING ─────────────────────────────────────────────
    'fingerprint_livescan': {
        'label':            'Livescan Electronic Fingerprinting',
        'service_line':     'Fingerprinting',
        'ddi_capable':      True,
        'lab_required':     False,
        'lab_partners':     [],
        'collection_partners': ['Lakota', 'IdentoGO'],
        'ddi_rate':         150,
        'sub_cost_low':     60,
        'sub_cost_high':    90,
        'ddi_direct_cost':  5,    # 3D Ink & Livescan Co equipment amortized
        'lab_cost':         0,
        'notes':            '3D Ink & Livescan Co. DDI is SWFT-authorized. Mobile to employer sites.',
    },
    'fingerprint_ink_card': {
        'label':            'Ink Card Fingerprinting (FD-258)',
        'service_line':     'Fingerprinting',
        'ddi_capable':      True,
        'lab_required':     False,
        'lab_partners':     [],
        'collection_partners': ['Lakota'],
        'ddi_rate':         100,
        'sub_cost_low':     40,
        'sub_cost_high':    60,
        'ddi_direct_cost':  5,
        'lab_cost':         0,
        'notes':            'FBI FD-258 ink cards. DDI prints and submits via SWFT.',
    },
    'fingerprint_swft_submission': {
        'label':            'SWFT Electronic Submission to FBI',
        'service_line':     'Fingerprinting',
        'ddi_capable':      True,
        'lab_required':     False,
        'lab_partners':     [],
        'collection_partners': [],
        'ddi_rate':         50,
        'sub_cost_low':     0,
        'sub_cost_high':    0,
        'ddi_direct_cost':  0,
        'lab_cost':         0,
        'notes':            'Add-on to any print service. DDI submits directly — 100% margin.',
    },
    'fingerprint_background_check': {
        'label':            'Background Check + Fingerprinting Bundle',
        'service_line':     'Fingerprinting',
        'ddi_capable':      True,
        'lab_required':     False,
        'lab_partners':     [],
        'collection_partners': ['Lakota', 'IdentoGO'],
        'ddi_rate':         200,
        'sub_cost_low':     80,
        'sub_cost_high':    120,
        'ddi_direct_cost':  10,
        'lab_cost':         0,
        'notes':            'Bundled: print + SWFT + background check coordination.',
    },

    # ─── MEDICAL COURIER ────────────────────────────────────────────
    'medical_courier_specimen': {
        'label':            'Medical Specimen Courier',
        'service_line':     'Medical Courier',
        'ddi_capable':      True,
        'lab_required':     False,
        'lab_partners':     [],
        'collection_partners': [],
        'ddi_rate':         95,   # per run
        'sub_cost_low':     45,
        'sub_cost_high':    65,
        'ddi_direct_cost':  20,   # mileage + supplies
        'lab_cost':         0,
        'notes':            'DDI van handles local Metro Detroit runs. Freight 1st for out-of-area.',
    },
    'medical_courier_route': {
        'label':            'Medical Courier Scheduled Route',
        'service_line':     'Medical Courier',
        'ddi_capable':      True,
        'lab_required':     False,
        'lab_partners':     [],
        'collection_partners': ['Freight 1st Direct'],
        'ddi_rate':         75,   # per stop on scheduled route
        'sub_cost_low':     35,
        'sub_cost_high':    50,
        'ddi_direct_cost':  15,
        'lab_cost':         0,
        'notes':            'Scheduled daily/weekly routes. DDI driver preferred for local. Freight 1st for extended routes.',
    },
    'medical_courier_stat': {
        'label':            'STAT Medical Courier (Urgent)',
        'service_line':     'Medical Courier',
        'ddi_capable':      True,
        'lab_required':     False,
        'lab_partners':     [],
        'collection_partners': ['Freight 1st Direct'],
        'ddi_rate':         175,
        'sub_cost_low':     75,
        'sub_cost_high':    100,
        'ddi_direct_cost':  25,
        'lab_cost':         0,
        'urgent':           True,
        'notes':            'Premium pricing for STAT runs. DDI handles locally when possible.',
    },

    # ─── NEMT ────────────────────────────────────────────────────────
    'nemt_scheduled': {
        'label':            'NEMT Scheduled Trip',
        'service_line':     'NEMT',
        'ddi_capable':      True,
        'lab_required':     False,
        'lab_partners':     [],
        'collection_partners': ['Uber Health', 'Lyft Healthcare', 'Local NEMT operators'],
        'ddi_rate':         65,   # per one-way trip (Medicaid rate varies by state)
        'sub_cost_low':     28,
        'sub_cost_high':    45,
        'ddi_direct_cost':  20,   # DDI vehicle mileage + driver
        'lab_cost':         0,
        'notes':            'DDI vehicle for local trips. Uber Health / Lyft for overflow or out-of-area.',
    },
    'nemt_wheelchair': {
        'label':            'NEMT Wheelchair Van Trip',
        'service_line':     'NEMT',
        'ddi_capable':      False,   # requires WAV-certified vehicle
        'lab_required':     False,
        'lab_partners':     [],
        'collection_partners': ['Local wheelchair van operators', 'MedTrans'],
        'ddi_rate':         125,
        'sub_cost_low':     70,
        'sub_cost_high':    95,
        'ddi_direct_cost':  None,
        'lab_cost':         0,
        'notes':            'Wheelchair accessible vehicle required. Always route to WAV-certified sub.',
    },
    'nemt_stretcher': {
        'label':            'NEMT Stretcher Transport',
        'service_line':     'NEMT',
        'ddi_capable':      False,
        'lab_required':     False,
        'lab_partners':     [],
        'collection_partners': ['Local ambulance companies', 'MedTrans'],
        'ddi_rate':         250,
        'sub_cost_low':     150,
        'sub_cost_high':    200,
        'ddi_direct_cost':  None,
        'lab_cost':         0,
        'notes':            'Always requires licensed stretcher transport sub.',
    },
    'nemt_brokerage_program': {
        'label':            'NEMT Brokerage Program Management',
        'service_line':     'NEMT',
        'ddi_capable':      True,
        'lab_required':     False,
        'lab_partners':     [],
        'collection_partners': ['Uber Health', 'Lyft Healthcare', 'Full NEMT network'],
        'ddi_rate':         None,   # per contract (Medicaid brokerage fee or per-trip rate)
        'sub_cost_low':     None,
        'sub_cost_high':    None,
        'ddi_direct_cost':  0,
        'lab_cost':         0,
        'notes':            'DDI is the broker. All trips dispatched through network. DDI keeps broker margin.',
    },

    # ─── OCCUPATIONAL HEALTH ─────────────────────────────────────────
    'dot_physical': {
        'label':            'DOT Physical Examination (FMCSA)',
        'service_line':     'Occupational Health',
        'ddi_capable':      False,   # requires licensed Medical Examiner on FMCSA registry
        'lab_required':     False,
        'lab_partners':     [],
        'collection_partners': ['Concentra', 'Local certified Medical Examiners'],
        'ddi_rate':         175,
        'sub_cost_low':     100,
        'sub_cost_high':    130,
        'ddi_direct_cost':  None,
        'lab_cost':         0,
        'notes':            'FMCSA-registered Medical Examiner required. Always route to Concentra or local ME. DDI coordinates and tracks.',
    },
    'non_dot_physical': {
        'label':            'Non-DOT Physical Examination',
        'service_line':     'Occupational Health',
        'ddi_capable':      False,   # requires licensed examiner
        'lab_required':     False,
        'lab_partners':     [],
        'collection_partners': ['Concentra', 'Local occupational health clinics'],
        'ddi_rate':         135,
        'sub_cost_low':     75,
        'sub_cost_high':    95,
        'ddi_direct_cost':  None,
        'lab_cost':         0,
        'notes':            'Non-DOT physical. Route to Concentra or local clinic. DDI coordinates and bills.',
    },
    'phlebotomy_blood_draw': {
        'label':            'Mobile Phlebotomy / Blood Draw',
        'service_line':     'Occupational Health',
        'ddi_capable':      True,   # with certified phlebotomist sub or hire
        'lab_required':     True,
        'lab_partners':     ['Quest Diagnostics', 'Labcorp'],
        'collection_partners': ['Mobile phlebotomy subs'],
        'ddi_rate':         120,
        'sub_cost_low':     50,
        'sub_cost_high':    75,
        'ddi_direct_cost':  25,
        'lab_cost':         30,
        'notes':            'DDI can do locally with certified phlebotomist. Lab analysis routes to Quest.',
    },
    'respirator_fit_test': {
        'label':            'Respirator Fit Test (OSHA)',
        'service_line':     'Occupational Health',
        'ddi_capable':      False,
        'lab_required':     False,
        'lab_partners':     [],
        'collection_partners': ['Concentra', 'Local industrial health clinics'],
        'ddi_rate':         150,
        'sub_cost_low':     80,
        'sub_cost_high':    110,
        'ddi_direct_cost':  None,
        'lab_cost':         0,
        'notes':            '29 CFR 1910.134. Route to Concentra or OSHA-certified provider.',
    },

    # ─── NOTARY ──────────────────────────────────────────────────────
    'notary_standard': {
        'label':            'Standard Notarization (§3 MiLONA)',
        'service_line':     'Notary',
        'ddi_capable':      True,
        'lab_required':     False,
        'lab_partners':     [],
        'collection_partners': ['Mobile notary subs'],
        'ddi_rate':         35,   # per notarial act (state max or market)
        'sub_cost_low':     15,
        'sub_cost_high':    25,
        'ddi_direct_cost':  0,   # Dee is a notary
        'lab_cost':         0,
        'notes':            'General acknowledgments/jurats. Dee performs locally. Mobile notary subs for out-of-area. Distinct from CNTDA packages and loan signings.',
    },
    'notary_cntda_estate': {
        'label':            'CNTDA — Trust & Estate Packages (§4)',
        'service_line':     'Notary',
        'ddi_capable':      True,
        'lab_required':     False,
        'lab_partners':     [],
        'collection_partners': ['Mobile notary subs (CNTDA-capable)'],
        'ddi_rate':         200,   # anchor: living trust / estate package band $150–250 in price book
        'sub_cost_low':     80,
        'sub_cost_high':    140,
        'ddi_direct_cost':  0,
        'lab_cost':         0,
        'notes':            'Trust signings, POA/AHD sets, estate delivery — document-agent role; UPL boundaries. POA/AHD lines often $75–125 per set in DDI_PROFESSIONAL_SERVICES_PRICING §4.',
    },
    'notary_loan_signing': {
        'label':            'Loan Signing (NSA)',
        'service_line':     'Notary',
        'ddi_capable':      True,
        'lab_required':     False,
        'lab_partners':     [],
        'collection_partners': ['Mobile notary subs', 'SigningAgent.com network'],
        'ddi_rate':         175,
        'sub_cost_low':     75,
        'sub_cost_high':    125,
        'ddi_direct_cost':  0,
        'lab_cost':         0,
        'notes':            'High margin. Dee performs locally. Subs for out-of-area or overflow.',
    },
    'notary_ron': {
        'label':            'Remote Online Notarization (RON)',
        'service_line':     'Notary',
        'ddi_capable':      True,
        'lab_required':     False,
        'lab_partners':     [],
        'collection_partners': ['Notarize.com', 'Proof.com'],
        'ddi_rate':         75,
        'sub_cost_low':     0,
        'sub_cost_high':    15,
        'ddi_direct_cost':  0,
        'lab_cost':         0,
        'notes':            'RON platform cost only. High margin. Geographic unlimited.',
    },
    'notary_apostille': {
        'label':            'Apostille Coordination',
        'service_line':     'Notary',
        'ddi_capable':      True,
        'lab_required':     False,
        'lab_partners':     [],
        'collection_partners': [],
        'ddi_rate':         150,
        'sub_cost_low':     30,
        'sub_cost_high':    50,
        'ddi_direct_cost':  30,   # state filing fees
        'lab_cost':         0,
        'notes':            'DDI manages the apostille process. State fees are pass-through.',
    },
    'legal_courier_filing': {
        'label':            'Legal Courier & Court / SOS Filing (§6)',
        'service_line':     'Legal Courier',
        'ddi_capable':      True,
        'lab_required':     False,
        'lab_partners':     [],
        'collection_partners': ['Freight 1st Direct', 'Local runner subs'],
        'ddi_rate':         65,   # typical regional filing/runner; court rush $75+ in price book
        'sub_cost_low':     25,
        'sub_cost_high':    45,
        'ddi_direct_cost':  15,   # mileage/parking when DDI runs
        'lab_cost':         0,
        'notes':            'Filings, retrievals, SOS — not the same SKU as medical courier or §3 notary-only. Filing fees pass-through where applicable.',
    },
    'permit_runner_npr': {
        'label':            'Permit Runner / NPR (§6A)',
        'service_line':     'Permit Runner',
        'ddi_capable':      True,
        'lab_required':     False,
        'lab_partners':     [],
        'collection_partners': ['Local NPR subs', 'LARA/building counter runners'],
        'ddi_rate':         75,   # base pull + permit fees pass-through per price book
        'sub_cost_low':     35,
        'sub_cost_high':    55,
        'ddi_direct_cost':  20,
        'lab_cost':         0,
        'notes':            'Building/LARA permit pulls — may involve notarized forms but billed as permit-runner service, not generic notary.',
    },
}


# ═══════════════════════════════════════════════════════════════════
# PARTNER DIRECTORY
# ═══════════════════════════════════════════════════════════════════

PARTNER_DIRECTORY = {
    'Quest Diagnostics': {
        'role':         'Lab + Collection Network',
        'services':     ['Drug Testing', 'Occupational Health', 'Blood Draw'],
        'coverage':     'Nationwide',
        'contact_key':  'quest_account',
        'notes':        'Primary lab for drug testing. PSC collection sites nationwide.',
    },
    'eScreen': {
        'role':         'Electronic Drug Testing Network',
        'services':     ['Drug Testing'],
        'coverage':     'Nationwide',
        'contact_key':  'escreen_account',
        'notes':        'PRISM network primary for electronic orders.',
    },
    'Concentra': {
        'role':         'Occupational Health Clinic Network',
        'services':     ['Drug Testing', 'Occupational Health', 'DOT Physicals'],
        'coverage':     'Nationwide (700+ locations)',
        'contact_key':  'concentra_account',
        'notes':        'Preferred for DOT physicals and non-DOT physicals. Collection overflow.',
    },
    'DDC Laboratories': {
        'role':         'DNA Testing Lab (AABB-Accredited)',
        'services':     ['DNA Testing'],
        'coverage':     'Nationwide (lab analysis)',
        'contact_key':  'ddc_account',
        'notes':        'Primary lab for all DePointe DNA testing. AABB-accredited. Immigration and legal.',
    },
    'Lakota': {
        'role':         'Fingerprinting Partner',
        'services':     ['Fingerprinting', 'Background Checks'],
        'coverage':     'Michigan + Regional',
        'contact_key':  'lakota_account',
        'notes':        'EFT file creation partnership. Overflow and out-of-area fingerprinting.',
    },
    'IdentoGO': {
        'role':         'Fingerprinting Network',
        'services':     ['Fingerprinting'],
        'coverage':     'Nationwide',
        'contact_key':  'identogo_account',
        'notes':        'Overflow for cross-state fingerprinting needs.',
    },
    'Uber Health': {
        'role':         'NEMT Ride Network',
        'services':     ['NEMT'],
        'coverage':     'Nationwide',
        'contact_key':  'uber_health_account',
        'notes':        'Primary NEMT overflow partner. API integration available (prism_uber_health.py).',
    },
    'Lyft Healthcare': {
        'role':         'NEMT Ride Network',
        'services':     ['NEMT'],
        'coverage':     'Nationwide',
        'contact_key':  'lyft_healthcare_account',
        'notes':        'Secondary NEMT partner.',
    },
    'Freight 1st Direct': {
        'role':         'Medical Courier / Freight',
        'services':     ['Medical Courier', 'Freight/Logistics'],
        'coverage':     'Regional + National',
        'contact_key':  'freight1st_account',
        'notes':        "DDI's own freight brokerage (MC-1647572, DOT-4250594). Courier overflow and long-haul.",
    },
}


# ═══════════════════════════════════════════════════════════════════
# ROUTING ENGINE
# ═══════════════════════════════════════════════════════════════════

def route_order(
    service_type: str,
    client_state: str = '',
    client_county: str = '',
    client_city: str = '',
    urgent: bool = False,
    override_fulfillment: str = None,
) -> dict:
    """
    Core routing decision for a service order.

    Returns a routing decision with:
    - fulfillment_mode: 'DDI_DIRECT' or 'PARTNER'
    - assigned_partner: partner name if PARTNER mode
    - rationale: why this decision was made
    - revenue_model: full breakdown of DDI's financials on this order
    - next_steps: what to do right now
    """
    if service_type not in SERVICE_CATALOG:
        return {
            'error': f'Unknown service type: {service_type}',
            'available_services': list(SERVICE_CATALOG.keys()),
        }

    svc = SERVICE_CATALOG[service_type]

    # Manual override
    if override_fulfillment:
        fulfillment_mode = override_fulfillment.upper()
        rationale = f'Manual override: {override_fulfillment}'
        partner = None
    else:
        # Decision logic
        is_local = (
            client_state.upper() in [s.upper() for s in DDI_DIRECT_STATES] and
            any(county.lower() in client_county.lower() for county in DDI_DIRECT_COUNTIES)
        ) if client_state and client_county else False

        if svc['ddi_capable'] and is_local:
            fulfillment_mode = 'DDI_DIRECT'
            partner = None
            rationale = f'DDI can perform this service. Client is in {DDI_DIRECT_METRO} (local service area).'
        elif svc['ddi_capable'] and not is_local and client_state:
            fulfillment_mode = 'PARTNER'
            partner = (svc.get('collection_partners') or ['Network collector'])[0]
            rationale = f'DDI capable but client is outside local service area ({client_state}, {client_county}). Routing to partner.'
        elif not svc['ddi_capable']:
            fulfillment_mode = 'PARTNER'
            partner = (svc.get('collection_partners') or ['Network collector'])[0]
            rationale = f'This service requires a licensed specialist. DDI coordinates and manages — {partner} performs.'
        else:
            # No geography provided — default to DDI_DIRECT with note
            fulfillment_mode = 'DDI_DIRECT'
            partner = None
            rationale = 'No geography provided. Defaulting to DDI_DIRECT. Confirm client location.'

    # Revenue model
    ddi_rate = svc['ddi_rate'] or 0
    if fulfillment_mode == 'DDI_DIRECT':
        direct_cost = (svc['ddi_direct_cost'] or 0) + (svc['lab_cost'] or 0)
        ddi_margin = ddi_rate - direct_cost
        margin_pct = round((ddi_margin / ddi_rate * 100) if ddi_rate else 0, 1)
        revenue_model = {
            'ddi_rate':       ddi_rate,
            'fulfillment_cost': direct_cost,
            'ddi_margin':     ddi_margin,
            'margin_pct':     f'{margin_pct}%',
            'mode':           'DDI_DIRECT — full revenue captured',
        }
    else:
        sub_cost_mid = round(((svc['sub_cost_low'] or 0) + (svc['sub_cost_high'] or 0)) / 2, 2)
        ddi_margin = ddi_rate - sub_cost_mid
        margin_pct = round((ddi_margin / ddi_rate * 100) if ddi_rate else 0, 1)
        revenue_model = {
            'ddi_rate':       ddi_rate,
            'partner_cost_low':  svc['sub_cost_low'],
            'partner_cost_high': svc['sub_cost_high'],
            'partner_cost_mid':  sub_cost_mid,
            'ddi_margin':     ddi_margin,
            'margin_pct':     f'{margin_pct}%',
            'mode':           f'PARTNER — DDI keeps management margin, {partner} performs',
        }

    # Lab routing (if required)
    lab_routing = None
    if svc.get('lab_required') and svc.get('lab_partners'):
        lab_routing = {
            'lab_required': True,
            'primary_lab':  svc['lab_partners'][0],
            'note':         'Lab analysis always routes to third-party lab. DDI never analyzes specimens.',
        }

    # Clearinghouse flag
    clearinghouse_action = None
    if svc.get('clearinghouse_required'):
        clearinghouse_action = {
            'required': True,
            'action':   'Report result to FMCSA Clearinghouse after completion.',
            'endpoint': '/prism/clearinghouse/violations or /prism/clearinghouse/rtd',
        }

    # Urgency
    if urgent or svc.get('urgent'):
        next_steps = [
            f'URGENT ORDER — assign immediately',
            f'Notify {"DDI mobile collector" if fulfillment_mode == "DDI_DIRECT" else partner} now',
            'Track completion within required window',
        ]
    else:
        next_steps = [
            f'{"DDI performs this service" if fulfillment_mode == "DDI_DIRECT" else f"Route to {partner}"}',
            'Create order in PRISM',
            'Notify client of scheduling',
        ]
        if clearinghouse_action:
            next_steps.append('After completion: report to FMCSA Clearinghouse')

    return {
        'service_type':       service_type,
        'service_label':      svc['label'],
        'service_line':       svc['service_line'],
        'fulfillment_mode':   fulfillment_mode,
        'assigned_partner':   partner,
        'rationale':          rationale,
        'revenue_model':      revenue_model,
        'lab_routing':        lab_routing,
        'clearinghouse_action': clearinghouse_action,
        'next_steps':         next_steps,
        'service_notes':      svc['notes'],
        'routed_at':          datetime.now().isoformat(),
    }


def route_batch(orders: List[dict]) -> List[dict]:
    """Route multiple orders at once. Each order dict needs: service_type, client_state, client_county."""
    results = []
    for o in orders:
        result = route_order(
            service_type=o.get('service_type', ''),
            client_state=o.get('client_state', ''),
            client_county=o.get('client_county', ''),
            client_city=o.get('client_city', ''),
            urgent=o.get('urgent', False),
            override_fulfillment=o.get('override_fulfillment'),
        )
        result['order_ref'] = o.get('order_ref', '')
        results.append(result)
    return results


def get_revenue_summary(orders: List[dict]) -> dict:
    """
    Given a list of routing decisions, summarize total revenue, costs, and margin.
    Pass the output of route_batch() here.
    """
    total_revenue = 0
    total_cost = 0
    ddi_direct_count = 0
    partner_count = 0

    for o in orders:
        rm = o.get('revenue_model', {})
        total_revenue += rm.get('ddi_rate') or 0
        if o.get('fulfillment_mode') == 'DDI_DIRECT':
            total_cost += rm.get('fulfillment_cost') or 0
            ddi_direct_count += 1
        else:
            total_cost += rm.get('partner_cost_mid') or 0
            partner_count += 1

    total_margin = total_revenue - total_cost
    margin_pct = round((total_margin / total_revenue * 100) if total_revenue else 0, 1)

    return {
        'total_orders':       len(orders),
        'ddi_direct_orders':  ddi_direct_count,
        'partner_orders':     partner_count,
        'total_revenue':      total_revenue,
        'total_cost':         total_cost,
        'total_margin':       total_margin,
        'margin_pct':         f'{margin_pct}%',
        'avg_revenue_per_order': round(total_revenue / len(orders), 2) if orders else 0,
        'avg_margin_per_order':  round(total_margin / len(orders), 2) if orders else 0,
    }


# ═══════════════════════════════════════════════════════════════════
# CROSS-MODULE HOOKS
# ═══════════════════════════════════════════════════════════════════

def on_random_draw_completed(draw_result: dict) -> List[dict]:
    """
    Hook called after a random pool draw (from prism_random_pool).
    For each selected driver, creates routing decisions for their drug test
    AND flags Clearinghouse annual query if due.
    Returns list of routed orders for the draw.
    """
    selected = draw_result.get('selected', [])
    pool_type = draw_result.get('pool_type', 'DOT')
    dot_authority = draw_result.get('dot_authority', 'FMCSA')
    employer_id = draw_result.get('client_id', '')

    routed_orders = []
    clearinghouse_flags = []

    for driver in selected:
        # Route the drug test
        test_type = 'dot_drug_test' if pool_type == 'DOT' else 'non_dot_drug_test'
        routing = route_order(
            service_type=test_type,
            client_state='MI',
            client_county='Wayne',  # default — override with driver location if available
        )
        routing['driver_id'] = driver.get('employee_id')
        routing['driver_name'] = driver.get('name')
        routing['employer_id'] = employer_id
        routing['trigger'] = 'RANDOM_DRAW'
        routing['draw_id'] = draw_result.get('draw_id')
        routed_orders.append(routing)

        # Flag for Clearinghouse annual query check
        last_query = driver.get('last_clearinghouse_query')
        if not last_query:
            clearinghouse_flags.append({
                'driver_id':   driver.get('employee_id'),
                'driver_name': driver.get('name'),
                'employer_id': employer_id,
                'flag':        'NO_CLEARINGHOUSE_QUERY_ON_FILE',
                'action':      'Run annual or pre-employment query at clearinghouse.fmcsa.dot.gov',
            })

    return {
        'routed_orders':        routed_orders,
        'clearinghouse_flags':  clearinghouse_flags,
        'total_tests_ordered':  len(routed_orders),
    }


def on_positive_test_result(order: dict) -> dict:
    """
    Hook called when a drug test returns positive (from prism_orders or MRO notification).
    Returns a violation reporting package for the Clearinghouse module.
    """
    return {
        'action':          'REPORT_TO_CLEARINGHOUSE',
        'deadline':        '3 business days from result received date',
        'endpoint':        'POST /prism/clearinghouse/violations',
        'required_fields': {
            'driver_id':                    order.get('driver_id', ''),
            'employer_id':                  order.get('employer_id', ''),
            'violation_type':               'POSITIVE_DRUG',
            'violation_date':               order.get('collection_date', ''),
            'test_result_received_date':    order.get('result_date', ''),
            'mro_name':                     order.get('mro_name', ''),
            'lab_name':                     order.get('lab_name', ''),
            'substance':                    order.get('substance_detected', ''),
        },
        'next_steps': [
            '1. Report to Clearinghouse within 3 business days',
            '2. Remove driver from safety-sensitive duty immediately',
            '3. Open RTD case: POST /prism/clearinghouse/rtd',
            '4. Refer driver to qualified SAP',
        ],
    }


def on_rtd_negative_result(rtd_case: dict) -> dict:
    """
    Hook called when a Return-to-Duty test comes back negative.
    Routes the Clearinghouse report and follow-up plan creation.
    """
    return {
        'action':     'RTD_CLEARINGHOUSE_REPORT + FOLLOWUP_PLAN',
        'steps': [
            {
                'step': 1,
                'action': 'Report negative RTD result to Clearinghouse',
                'endpoint': 'PATCH /prism/clearinghouse/rtd/<rtd_id>',
                'payload': {
                    'rtd_test_result':          'NEGATIVE',
                    'reported_to_clearinghouse': True,
                    'clearinghouse_reported_date': 'TODAY',
                },
            },
            {
                'step': 2,
                'action': 'Create follow-up testing plan (minimum 6 tests, 12 months)',
                'endpoint': 'POST /prism/clearinghouse/followup',
                'payload': {
                    'driver_id':    rtd_case.get('driver_id'),
                    'employer_id':  rtd_case.get('employer_id'),
                    'rtd_id':       rtd_case.get('id'),
                    'rtd_date':     'TODAY',
                    'num_tests':    6,
                    'plan_months':  12,
                },
            },
            {
                'step': 3,
                'action': 'Driver may return to safety-sensitive duty',
                'note':   'Notify employer DER that driver is cleared',
            },
        ],
    }


# ═══════════════════════════════════════════════════════════════════
# API ROUTES
# ═══════════════════════════════════════════════════════════════════

@prism_router.route('/prism/router/route', methods=['POST'])
def api_route_order():
    """
    Route a single service order.
    Body: { service_type, client_state, client_county, client_city, urgent, override_fulfillment }
    """
    data = request.get_json() or {}
    if not data.get('service_type'):
        return jsonify({'error': 'service_type is required'}), 400
    result = route_order(
        service_type=data['service_type'],
        client_state=data.get('client_state', ''),
        client_county=data.get('client_county', ''),
        client_city=data.get('client_city', ''),
        urgent=data.get('urgent', False),
        override_fulfillment=data.get('override_fulfillment'),
    )
    return jsonify(result)


@prism_router.route('/prism/router/route-batch', methods=['POST'])
def api_route_batch():
    """Route multiple service orders at once."""
    data = request.get_json() or {}
    orders = data.get('orders', [])
    if not orders:
        return jsonify({'error': 'orders array is required'}), 400
    results = route_batch(orders)
    summary = get_revenue_summary(results)
    return jsonify({'routes': results, 'summary': summary})


@prism_router.route('/prism/router/services', methods=['GET'])
def api_list_services():
    """List all service types DDI can route, with pricing and capability info."""
    service_line = request.args.get('service_line')
    catalog = {}
    for key, svc in SERVICE_CATALOG.items():
        if service_line and svc['service_line'].lower() != service_line.lower():
            continue
        catalog[key] = {
            'label':          svc['label'],
            'service_line':   svc['service_line'],
            'ddi_capable':    svc['ddi_capable'],
            'ddi_rate':       svc['ddi_rate'],
            'sub_cost_range': f"${svc['sub_cost_low']}-${svc['sub_cost_high']}" if svc['sub_cost_low'] else 'Custom',
            'lab_required':   svc['lab_required'],
            'notes':          svc['notes'],
        }
    return jsonify({'services': catalog, 'count': len(catalog)})


@prism_router.route('/prism/router/partners', methods=['GET'])
def api_list_partners():
    """List DDI's full partner network."""
    service_filter = request.args.get('service')
    partners = {}
    for name, p in PARTNER_DIRECTORY.items():
        if service_filter and service_filter not in p['services']:
            continue
        partners[name] = p
    return jsonify({'partners': partners, 'count': len(partners)})


@prism_router.route('/prism/router/service-area', methods=['GET'])
def api_service_area():
    """Return DDI's direct service area."""
    return jsonify({
        'ddi_direct_states':   DDI_DIRECT_STATES,
        'ddi_direct_counties': DDI_DIRECT_COUNTIES,
        'metro_label':         DDI_DIRECT_METRO,
        'outside_area':        'Routes to partner network — DDI retains management margin',
    })


@prism_router.route('/prism/router/hooks/random-draw', methods=['POST'])
def api_hook_random_draw():
    """Called after a random pool draw — creates test orders + Clearinghouse flags."""
    data = request.get_json() or {}
    result = on_random_draw_completed(data)
    return jsonify(result)


@prism_router.route('/prism/router/hooks/positive-test', methods=['POST'])
def api_hook_positive_test():
    """Called when a drug test returns positive — generates Clearinghouse reporting package."""
    data = request.get_json() or {}
    result = on_positive_test_result(data)
    return jsonify(result)


@prism_router.route('/prism/router/hooks/rtd-negative', methods=['POST'])
def api_hook_rtd_negative():
    """Called when RTD test returns negative — generates Clearinghouse report + follow-up plan steps."""
    data = request.get_json() or {}
    result = on_rtd_negative_result(data)
    return jsonify(result)


@prism_router.route('/prism/router/revenue-calculator', methods=['POST'])
def api_revenue_calculator():
    """
    Calculate revenue for a mix of service orders.
    Useful for quoting a client or estimating contract value.
    Body: { orders: [{ service_type, qty, client_state, client_county }] }
    """
    data = request.get_json() or {}
    orders_input = data.get('orders', [])
    if not orders_input:
        return jsonify({'error': 'orders array required'}), 400

    expanded = []
    for item in orders_input:
        qty = item.get('qty', 1)
        for _ in range(qty):
            expanded.append(item)

    results = route_batch(expanded)
    summary = get_revenue_summary(results)

    # Annual projection
    frequency = data.get('frequency', 'one_time')
    if frequency == 'monthly':
        summary['annual_revenue_projection'] = summary['total_revenue'] * 12
        summary['annual_margin_projection'] = summary['total_margin'] * 12
    elif frequency == 'weekly':
        summary['annual_revenue_projection'] = summary['total_revenue'] * 52
        summary['annual_margin_projection'] = summary['total_margin'] * 52

    return jsonify({'summary': summary, 'routes': results})
