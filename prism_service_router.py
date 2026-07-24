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

# ─── NEXUS LEARNING ENGINE INTEGRATION ────────────────────────────────────────
try:
    from nexus_learning_engine import nxlearn
except ImportError:
    def nxlearn(*args, **kwargs):
        pass  # Graceful fallback if learning engine not available

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
        'notes':            '3D Ink & Livescan Co. LiveScan capture; submission per client channel (no DCSA SWFT claim — COMPANY_INFO_MASTER). Mobile to employer sites.',
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
        'notes':            'FBI FD-258 ink cards. DDI prints; submission via mail/state channel or partner per program (no DCSA SWFT claim).',
    },
    'fingerprint_swft_submission': {
        'label':            'Electronic submission add-on (partner/cleared channel)',
        'service_line':     'Fingerprinting',
        'ddi_capable':      True,
        'lab_required':     False,
        'lab_partners':     [],
        'collection_partners': ['Lakota'],
        'ddi_rate':         50,
        'sub_cost_low':     0,
        'sub_cost_high':    0,
        'ddi_direct_cost':  0,
        'lab_cost':         0,
        'notes':            'DCSA SWFT not held by DDI (denied Mar 2026). Coordinate via Lakota/cleared sub when program requires electronic submission.',
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
        'notes':            'Bundled: print + electronic channel (as applicable) + background check coordination.',
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

    # ─── COMMUNITY TRANSITION SERVICES (Molina HIDE SNP LTSS — secondary service) ──
    'community_transition_assessment': {
        'label':            'Community Transition Services — Home/Environment Assessment (T1028)',
        'service_line':     'Community Transition Services',
        'ddi_capable':      True,
        'lab_required':     False,
        'lab_partners':     [],
        'collection_partners': [],   # DDI-direct — case management, not fulfillment
        'ddi_rate':         150,    # Molina fee schedule flat rate (T1028), no discount
        'sub_cost_low':     None,
        'sub_cost_high':    None,
        'ddi_direct_cost':  0,
        'lab_cost':         0,
        'notes':            'Molina HIDE SNP LTSS. One-time assessment of home/physical/family environment for a member transitioning out of a nursing facility. DDI-direct, no sub routing — this is case management, not a trip.',
    },
    'community_transition_services': {
        'label':            'Community Transition Services — Non-Recurring Setup Expenses (T2038)',
        'service_line':     'Community Transition Services',
        'ddi_capable':      True,
        'lab_required':     False,
        'lab_partners':     [],
        'collection_partners': [],   # DDI-direct case management — DDI does not front vendor costs; Molina/MI Medicaid funds release
        'ddi_rate':         None,   # "Manual" on Molina fee schedule — billed at DDI's Amount Authorized from Authorization Sign-Off
        'sub_cost_low':     None,
        'sub_cost_high':    None,
        'ddi_direct_cost':  None,
        'lab_cost':         0,
        'notes':            (
            'Non-recurring setup expenses ONLY for a member moving from a nursing facility into their own '
            'residence. STARTING SCOPE: Security Deposit and Utility Set-up only — Furnishings and Moving Costs '
            'are blocked until subcontractor disclosure is filed under Article 2.9 of the executed Molina HCBS '
            'PSA. Every expense item requires an actual invoice/quote (no verbal estimates). DDI executes its '
            'own Authorization Sign-Off (Amount Authorized) based on documented need — Michigan State Plan '
            'Medicaid is the funding source, DDI does not cut the check. Retain itemized receipts for '
            'scanback/audit — no recurring charges (rent, ongoing utilities) allowed.'
        ),
    },

    # ─── PRESCRIPTION DELIVERY ──────────────────────────────────────
    'rx_delivery_standard': {
        'label':            'Prescription Delivery — Standard (Same-Day)',
        'service_line':     'Prescription Delivery',
        'ddi_capable':      True,
        'lab_required':     False,
        'lab_partners':     [],
        'collection_partners': ['Uber Health', 'Local courier subs'],
        'ddi_rate':         25,
        'sub_cost_low':     12,
        'sub_cost_high':    18,
        'ddi_direct_cost':  8,    # mileage + packaging
        'lab_cost':         0,
        'notes':            'Non-controlled Rx. DDI driver or Uber Health. HIPAA-compliant packaging, ID verification at delivery, photo proof.',
    },
    'rx_delivery_controlled': {
        'label':            'Prescription Delivery — Controlled Substance (Schedule II-V)',
        'service_line':     'Prescription Delivery',
        'ddi_capable':      True,
        'lab_required':     False,
        'lab_partners':     [],
        'collection_partners': [],   # DDI-direct only for controlled substances — chain of custody is critical
        'ddi_rate':         45,
        'sub_cost_low':     None,    # DDI-direct only
        'sub_cost_high':    None,
        'ddi_direct_cost':  12,
        'lab_cost':         0,
        'notes':            'DEA-regulated. Signature required, no leave-at-door. Chain of custody pharmacy→patient. DDI driver only — no sub routing.',
    },
    'rx_delivery_cold_chain': {
        'label':            'Prescription Delivery — Temperature-Sensitive / Cold Chain',
        'service_line':     'Prescription Delivery',
        'ddi_capable':      True,
        'lab_required':     False,
        'lab_partners':     [],
        'collection_partners': ['Specialized cold-chain courier subs'],
        'ddi_rate':         40,
        'sub_cost_low':     18,
        'sub_cost_high':    25,
        'ddi_direct_cost':  15,   # insulated container + temp monitor + mileage
        'lab_cost':         0,
        'notes':            'Insulin, biologics, vaccines. Requires insulated container with temp monitor. Temp log uploaded as scanback. Delivery within 2-hour window.',
    },
    'rx_delivery_bulk_pharmacy': {
        'label':            'Prescription Delivery — Bulk Pharmacy Program',
        'service_line':     'Prescription Delivery',
        'ddi_capable':      True,
        'lab_required':     False,
        'lab_partners':     [],
        'collection_partners': ['Uber Health', 'Local courier subs'],
        'ddi_rate':         None,   # per contract (volume-based pricing)
        'sub_cost_low':     None,
        'sub_cost_high':    None,
        'ddi_direct_cost':  0,
        'lab_cost':         0,
        'notes':            'DDI manages delivery program for pharmacy or MCO. Volume pricing. Daily scheduled routes + on-demand overflow.',
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
    'American Medical Review Officer (AMRO)': {
        'role':         'MRO Services',
        'services':     ['Drug Testing'],
        'coverage':     'Nationwide',
        'contact_key':  'amro_account',
        'notes':        'MRO-only provider (no TPA conflict). Dr. Donald S. Freedman, M.D. Pricing: $4/test DOT/Non-DOT, $30 abnormal-only. Alternative to Quest bundled MRO.',
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
# AGENT CREDENTIAL GATE — runs before dispatch / assignment
# ═══════════════════════════════════════════════════════════════════

SERVICE_REQUIRED_CREDENTIALS = {
    'dot_drug_test':         ['ctpa_collector_cert'],
    'non_dot_drug_test':     ['ctpa_collector_cert'],
    'non_dot_drug_test_10panel': ['ctpa_collector_cert'],
    'non_dot_drug_test_12panel_rapid': ['ctpa_collector_cert'],
    'non_dot_drug_test_12panel_lab': ['ctpa_collector_cert'],
    'non_dot_drug_test_12panel_oral': ['ctpa_collector_cert'],
    'dot_alcohol_test':      ['bat_cert'],
    'post_accident_drug':    ['ctpa_collector_cert'],
    'return_to_duty_test':   ['ctpa_collector_cert'],
    'dna_legal_paternity':   ['dna_collector_cert'],
    'dna_immigration':       ['dna_collector_cert'],
    'dna_siblingship':       ['dna_collector_cert'],
    'fingerprint_livescan':  ['livescan_trained'],
    'fingerprint_ink_card':  ['ink_card_trained'],
    'notary_standard':       ['notary_commission'],
    'notary_loan_signing':   ['notary_commission', 'nsa_certified'],
    'notary_cntda_estate':   ['notary_commission'],
    'notary_ron':            ['ron_cert'],
    'notary_apostille':      ['notary_commission'],
    'phlebotomy_blood_draw': ['phlebotomy_cert'],
    'nemt_scheduled':        ['driver_license', 'vehicle_insurance'],
    'rx_delivery_standard':  ['driver_license', 'hipaa_trained'],
    'rx_delivery_controlled': ['driver_license', 'hipaa_trained', 'background_check_clear'],
    'rx_delivery_cold_chain': ['driver_license', 'hipaa_trained', 'cold_chain_trained'],
    'medical_courier_specimen': ['biohazard_transport_trained'],
}

# Partner list price (approx.) in USD where known; subs still purchase through DDI credentialing.
# ddi_credentialing_fee = what the sub pays DDI (access, assignment, tracking, audit trail, PRISM gate).
CREDENTIAL_TRAINING_SOURCES = {
    'hipaa_trained':            {'provider': 'NALI', 'url': 'https://nalearning.org/partner', 'cost': 15, 'ddi_credentialing_fee': 45, 'note': 'DDI referral partner portal'},
    'bloodborne_pathogens':     {'provider': 'NALI', 'url': 'https://nalearning.org/partner', 'cost': 15, 'ddi_credentialing_fee': 45, 'note': 'OSHA Bloodborne Pathogens'},
    'first_aid':                {'provider': 'NALI', 'url': 'https://nalearning.org/partner', 'cost': 25, 'ddi_credentialing_fee': 50, 'note': 'First Aid certification'},
    'cpr':                      {'provider': 'NALI', 'url': 'https://nalearning.org/partner', 'cost': 25, 'ddi_credentialing_fee': 50, 'note': 'CPR certification'},
    'drug_alcohol_awareness':   {'provider': 'NALI', 'url': 'https://nalearning.org/partner', 'cost': 25, 'ddi_credentialing_fee': 50, 'note': 'Drug & Alcohol Awareness'},
    'fraud_waste_abuse':        {'provider': 'NALI', 'url': 'https://nalearning.org/partner', 'cost': 25, 'ddi_credentialing_fee': 50, 'note': 'Medicaid/Medicare FWA compliance'},
    'sexual_harassment':        {'provider': 'NALI', 'url': 'https://nalearning.org/partner', 'cost': 25, 'ddi_credentialing_fee': 50, 'note': 'Workplace compliance — all agents'},
    'hazcom':                   {'provider': 'NALI', 'url': 'https://nalearning.org/partner', 'cost': 25, 'ddi_credentialing_fee': 50, 'note': 'Hazard Communication — chemical/specimen handling'},
    'human_trafficking':        {'provider': 'NALI', 'url': 'https://nalearning.org/partner', 'cost': 25, 'ddi_credentialing_fee': 50, 'note': 'NEMT driver awareness — federally recommended'},
    'theft_awareness':          {'provider': 'NALI', 'url': 'https://nalearning.org/partner', 'cost': 25, 'ddi_credentialing_fee': 50, 'note': 'Rx delivery / controlled substance handling'},
    'hiv_aids_awareness':       {'provider': 'NALI', 'url': 'https://nalearning.org/partner', 'cost': 15, 'ddi_credentialing_fee': 45, 'note': 'Medical service agent awareness'},
    'diversity_awareness':      {'provider': 'NALI', 'url': 'https://nalearning.org/partner', 'cost': 25, 'ddi_credentialing_fee': 50, 'note': 'Workplace compliance — all agents'},
    'ethics':                   {'provider': 'NALI', 'url': 'https://nalearning.org/partner', 'cost': 25, 'ddi_credentialing_fee': 50, 'note': 'Professional conduct — all agents'},
    'conflict_resolution':      {'provider': 'NALI', 'url': 'https://nalearning.org/partner', 'cost': 15, 'ddi_credentialing_fee': 45, 'note': 'Client-facing de-escalation'},
    'fire_safety':              {'provider': 'NALI', 'url': 'https://nalearning.org/partner', 'cost': 25, 'ddi_credentialing_fee': 50, 'note': 'Field ops / facility services'},
    'workplace_violence':       {'provider': 'NALI', 'url': 'https://nalearning.org/partner', 'cost': 25, 'ddi_credentialing_fee': 50, 'note': 'Workplace safety — all agents'},
    'dot_supervisor_training':  {'provider': 'Quest Employer Solutions', 'url': 'Quest Employer Solutions Online Training Center', 'cost': None, 'ddi_credentialing_fee': 75, 'note': 'DOT Reasonable Suspicion, DOT Drug & Alcohol, FMCSA compliance. Sub pays DDI credentialing fee.'},
    'ctpa_collector_cert':      {'provider': 'Quest Employer Solutions', 'url': 'Quest Employer Solutions Online Training Center', 'cost': None, 'ddi_credentialing_fee': 75, 'note': 'SAMHSA-aligned collector training. Sub pays DDI credentialing fee.'},
    'bat_cert':                 {'provider': 'Quest Employer Solutions', 'url': 'Quest Employer Solutions Online Training Center', 'cost': None, 'ddi_credentialing_fee': 75, 'note': 'Breath Alcohol Technician certification. Sub pays DDI credentialing fee.'},
    'dna_collector_cert':       {'provider': 'DDC Laboratories', 'url': None, 'cost': None, 'ddi_credentialing_fee': None, 'note': 'AABB-accredited DNA collector training — quote per DDC'},
    'livescan_trained':         {'provider': 'DDI / Lakota', 'url': None, 'cost': None, 'ddi_credentialing_fee': None, 'note': 'LiveScan equipment training through DDI or Lakota partnership'},
    'ink_card_trained':         {'provider': 'DDI onboarding', 'url': None, 'cost': None, 'ddi_credentialing_fee': None, 'note': 'FD-258 ink card rolling technique — DDI hands-on training'},
    'notary_commission':        {'provider': 'State of Michigan', 'url': None, 'cost': None, 'ddi_credentialing_fee': None, 'note': 'Michigan notary commission — state-issued'},
    'nsa_certified':            {'provider': 'NNA / LSS', 'url': None, 'cost': None, 'ddi_credentialing_fee': None, 'note': 'Notary Signing Agent certification'},
    'ron_cert':                 {'provider': 'State + ZigSig', 'url': None, 'cost': None, 'ddi_credentialing_fee': None, 'note': 'Remote Online Notarization certification'},
    'cold_chain_trained':       {'provider': 'NALI + DDI onboarding', 'url': 'https://nalearning.org/partner', 'cost': None, 'ddi_credentialing_fee': None, 'note': 'Temperature-controlled transport — use Medical Courier / cold-chain bundle pricing in CREDENTIALING_BUNDLES'},
    'background_check_clear':   {'provider': 'National Crime Search (NCS)', 'url': 'https://deedavisinc.nationalcrimesearch.com', 'cost': None, 'ddi_credentialing_fee': 65, 'note': 'FCRA-compliant background check through DDI NCS portal'},
    'biohazard_transport_trained': {'provider': 'NALI', 'url': 'https://nalearning.org/partner', 'cost': 15, 'ddi_credentialing_fee': 45, 'note': 'Bloodborne pathogens (NALI) + DOT/IATA Category B (DDI onboarding)'},
}

# Bundled credentialing (sub pays DDI bundle fee; aligns with DEE_DAVIS_INC_COMPLETE_SERVICE_CATALOG.md).
CREDENTIALING_BUNDLES = {
    'ddi_agent_baseline': {
        'label': 'DDI Agent Baseline',
        'credential_keys': ['sexual_harassment', 'diversity_awareness', 'ethics', 'conflict_resolution', 'workplace_violence'],
        'platform_cost_estimate': 115,
        'ddi_credentialing_fee': 250,
    },
    'medical_courier_ready': {
        'label': 'Medical Courier Ready',
        'credential_keys': ['hipaa_trained', 'bloodborne_pathogens', 'hazcom'],
        'platform_cost_estimate': 55,
        'ddi_credentialing_fee': 125,
    },
    'rx_delivery_ready': {
        'label': 'Rx Delivery Ready',
        'credential_keys': ['hipaa_trained', 'drug_alcohol_awareness', 'theft_awareness'],
        'platform_cost_estimate': 55,
        'ddi_credentialing_fee': 125,
    },
    'nemt_driver_ready': {
        'label': 'NEMT Driver Ready',
        'credential_keys': ['hipaa_trained', 'first_aid', 'cpr', 'human_trafficking', 'drug_alcohol_awareness'],
        'platform_cost_estimate': 115,
        'ddi_credentialing_fee': 250,
    },
    'drug_testing_collector_ready': {
        'label': 'Drug Testing Collector Ready',
        'credential_keys': ['hipaa_trained', 'bloodborne_pathogens', 'drug_alcohol_awareness', 'ctpa_collector_cert'],
        'platform_cost_estimate': 80,
        'ddi_credentialing_fee': 200,
    },
    'notary_signing_ready': {
        'label': 'Notary / Signing Agent Ready',
        'credential_keys': ['ethics', 'conflict_resolution', 'fraud_waste_abuse'],
        'platform_cost_estimate': 65,
        'ddi_credentialing_fee': 150,
    },
    'field_ops_ready': {
        'label': 'Field Ops Ready',
        'credential_keys': ['first_aid', 'cpr', 'fire_safety'],
        'platform_cost_estimate': 75,
        'ddi_credentialing_fee': 200,
        'note': 'Catalog also references confined-space training where contract requires — add course or adjust fee.',
    },
}

# Full-stack combos (baseline + service bundle) per service catalog — package fees are
# intentionally below the sum of constituent bundles (volume/onboarding incentive).
CREDENTIALING_FULL_PACKAGES = {
    'full_rx_delivery_agent': {
        'bundles': ['ddi_agent_baseline', 'rx_delivery_ready'],
        'sum_of_bundle_fees': 375,
        'ddi_credentialing_fee': 350,
    },
    'full_nemt_driver': {
        'bundles': ['ddi_agent_baseline', 'nemt_driver_ready'],
        'sum_of_bundle_fees': 500,
        'ddi_credentialing_fee': 450,
    },
    'full_drug_testing_collector': {
        'bundles': ['ddi_agent_baseline', 'drug_testing_collector_ready'],
        'sum_of_bundle_fees': 450,
        'ddi_credentialing_fee': 400,
    },
}


def get_credential_training_pricing(credential_key: str) -> dict:
    """Return training source row for a credential, or empty dict."""
    return dict(CREDENTIAL_TRAINING_SOURCES.get(credential_key) or {})


def sum_individual_credentialing_fees(credential_keys: list) -> dict:
    """Sum ddi_credentialing_fee for a list of credential keys (skips None)."""
    total = 0
    breakdown = []
    for k in credential_keys:
        row = CREDENTIAL_TRAINING_SOURCES.get(k) or {}
        fee = row.get('ddi_credentialing_fee')
        if fee is not None:
            total += fee
        breakdown.append({'credential': k, 'ddi_credentialing_fee': fee})
    return {'total_ddi_credentialing_fee': total, 'breakdown': breakdown}


def get_credentialing_pricing_catalog() -> dict:
    """Serializable catalog for GET /prism/router/credentialing-pricing."""
    return {
        'credentials': dict(CREDENTIAL_TRAINING_SOURCES),
        'bundles': {bid: {**meta, 'id': bid} for bid, meta in CREDENTIALING_BUNDLES.items()},
        'full_packages': dict(CREDENTIALING_FULL_PACKAGES),
        'policy': (
            'Subs and independent agents pay DDI credentialing fees (not DDI). '
            'Fees cover partner portal access, assignment, tracking, audit records, and PRISM gate checks.'
        ),
    }


def compute_credentialing_quote(data: dict) -> dict:
    """
    Body keys (one mode):
      - full_package: str (e.g. full_rx_delivery_agent)
      - bundles: [str, ...] bundle ids
      - credentials: [str, ...] à la carte credential keys
    Precedence if multiple sent: full_package > bundles > credentials.
    """
    fp = data.get('full_package')
    if fp:
        if fp not in CREDENTIALING_FULL_PACKAGES:
            return {'error': f'Unknown full_package: {fp}', '_http_status': 400}
        pkg = CREDENTIALING_FULL_PACKAGES[fp]
        bundle_rows = []
        for bid in pkg['bundles']:
            b = CREDENTIALING_BUNDLES.get(bid)
            if not b:
                continue
            bundle_rows.append({'id': bid, 'label': b.get('label'), 'ddi_credentialing_fee': b['ddi_credentialing_fee']})
        savings = None
        if 'sum_of_bundle_fees' in pkg:
            savings = pkg['sum_of_bundle_fees'] - pkg['ddi_credentialing_fee']
        return {
            'mode': 'full_package',
            'package_id': fp,
            'ddi_credentialing_fee_total': pkg['ddi_credentialing_fee'],
            'sum_of_bundle_fees': pkg.get('sum_of_bundle_fees'),
            'package_savings_vs_separate_bundles': savings,
            'bundles_in_package': bundle_rows,
        }

    bundles = data.get('bundles') or data.get('bundle_ids')
    if bundles:
        if not isinstance(bundles, list):
            return {'error': 'bundles must be a list of bundle id strings', '_http_status': 400}
        total = 0
        detail = []
        for bid in bundles:
            b = CREDENTIALING_BUNDLES.get(bid)
            if not b:
                return {'error': f'Unknown bundle id: {bid}', '_http_status': 400}
            fee = b['ddi_credentialing_fee']
            total += fee
            detail.append({
                'id': bid,
                'label': b.get('label'),
                'ddi_credentialing_fee': fee,
                'credential_keys': b.get('credential_keys', []),
            })
        return {
            'mode': 'bundles',
            'ddi_credentialing_fee_total': total,
            'bundles': detail,
        }

    creds = data.get('credentials') or data.get('credential_keys')
    if creds:
        if not isinstance(creds, list):
            return {'error': 'credentials must be a list of credential keys', '_http_status': 400}
        unknown = [c for c in creds if c not in CREDENTIAL_TRAINING_SOURCES]
        if unknown:
            return {'error': f'Unknown credential keys: {unknown}', '_http_status': 400}
        summed = sum_individual_credentialing_fees(creds)
        return {
            'mode': 'credentials',
            'ddi_credentialing_fee_total': summed['total_ddi_credentialing_fee'],
            'breakdown': summed['breakdown'],
        }

    return {'error': 'Provide full_package, bundles, or credentials', '_http_status': 400}


def check_agent_qualified(agent: dict, service_type: str) -> dict:
    """Verify an agent holds every credential required for a service type.
    Returns {qualified: bool, missing: [...], warnings: [...]}."""
    required = SERVICE_REQUIRED_CREDENTIALS.get(service_type, [])
    if not required:
        return {'qualified': True, 'missing': [], 'warnings': []}

    agent_creds = agent.get('credentials', {})
    missing = []
    warnings = []

    for cred_key in required:
        cred = agent_creds.get(cred_key)
        if not cred or not cred.get('active', False):
            missing.append(cred_key)
            continue
        expiry_str = cred.get('expires')
        if expiry_str:
            try:
                expiry = datetime.fromisoformat(expiry_str)
                days_left = (expiry - datetime.now()).days
                if days_left < 0:
                    missing.append(f'{cred_key} (EXPIRED {expiry_str})')
                elif days_left <= 30:
                    warnings.append(f'{cred_key} expires in {days_left} day(s) — schedule renewal')
            except (ValueError, TypeError):
                pass

    return {
        'qualified': len(missing) == 0,
        'missing': missing,
        'warnings': warnings,
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
    agent: dict = None,
) -> dict:
    """
    Core routing decision for a service order.

    Returns a routing decision with:
    - fulfillment_mode: 'DDI_DIRECT' or 'PARTNER'
    - assigned_partner: partner name if PARTNER mode
    - rationale: why this decision was made
    - revenue_model: full breakdown of DDI's financials on this order
    - next_steps: what to do right now
    - credential_check: agent qualification status (if agent provided)
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

    credential_check = None
    if agent:
        credential_check = check_agent_qualified(agent, service_type)
        if not credential_check['qualified']:
            next_steps.insert(0, f'CREDENTIAL BLOCK — agent missing: {", ".join(credential_check["missing"])}')
        elif credential_check.get('warnings'):
            next_steps.insert(0, f'CREDENTIAL WARNING — {"; ".join(credential_check["warnings"])}')

    # ─── LEARNING ENGINE: Log order routing decision ──────────────────────────
    order_id = str(uuid.uuid4())[:12]
    nxlearn('service_orders', order_id, 'order_routed', {
        'service_type': service_type,
        'division': svc['service_line'],
        'region': client_state or 'MI',
        'fulfillment_mode': fulfillment_mode,
        'partner': partner,
        'ddi_rate': ddi_rate,
        'margin_pct': margin_pct,
    })

    return {
        'order_id':           order_id,  # Add order_id to response for tracking
        'service_type':       service_type,
        'service_label':      svc['label'],
        'service_line':       svc['service_line'],
        'fulfillment_mode':   fulfillment_mode,
        'assigned_partner':   partner,
        'rationale':          rationale,
        'revenue_model':      revenue_model,
        'lab_routing':        lab_routing,
        'clearinghouse_action': clearinghouse_action,
        'credential_check':   credential_check,
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
        agent=data.get('agent'),
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


@prism_router.route('/prism/router/credentialing-pricing', methods=['GET'])
def api_credentialing_pricing():
    """Full credentialing fee catalog: per-credential, bundles, full packages (subs pay DDI)."""
    return jsonify(get_credentialing_pricing_catalog())


@prism_router.route('/prism/router/credentialing-quote', methods=['POST'])
def api_credentialing_quote():
    """Quote DDI credentialing fees. Body: { full_package } | { bundles: [] } | { credentials: [] }."""
    data = request.get_json() or {}
    result = compute_credentialing_quote(data)
    code = result.pop('_http_status', 200)
    return jsonify(result), code


@prism_router.route('/prism/router/credential-check', methods=['POST'])
def api_credential_check():
    """Check if an agent is qualified for a service type before dispatch.
    Body: { agent: {credentials: {...}}, service_type: "dot_drug_test" }"""
    data = request.get_json() or {}
    agent = data.get('agent')
    service_type = data.get('service_type')
    if not agent or not service_type:
        return jsonify({'error': 'agent and service_type are required'}), 400
    result = check_agent_qualified(agent, service_type)
    result['service_type'] = service_type
    result['required_credentials'] = SERVICE_REQUIRED_CREDENTIALS.get(service_type, [])
    return jsonify(result)


# ═══════════════════════════════════════════════════════════════════════════════
# CLIENT PORTAL API — CONNECTS CLIENT LINK TO PRISM/NEXUS SYSTEM
# ═══════════════════════════════════════════════════════════════════════════════
#
# The Client Portal is a READ window + order submission into PRISM.
# Data flow:
#   Client submits request → PRISM order queue → DDI routes via service router
#   DDI updates order status → Client sees it instantly in their portal
#   DDI uploads result/scanback → Client can download it from Documents tab
#   DDI generates invoice → Client sees it in Invoices and can pay online
#
# The magic link encodes a client_code that maps to their Airtable client record.
# Every portal read/write authenticates against this code — no passwords.

CLIENT_PORTAL_STORE = {}  # In production: Airtable PRISM_CLIENTS table

PRISM_DATA_DIR = os.path.join(os.path.dirname(__file__), 'uploads', 'prism')
PRISM_CLIENTS_FILE = os.path.join(PRISM_DATA_DIR, 'clients.json')
PRISM_ORDERS_FILE = os.path.join(PRISM_DATA_DIR, 'orders.json')


def _load_prism_json(path: str, default):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return default


def _client_portal_record(raw: dict, code: str) -> dict:
    services = raw.get('services') or []
    if isinstance(services, str):
        services = [services]
    return {
        'id': raw.get('id'),
        'code': code,
        'name': raw.get('name', ''),
        'contact_name': raw.get('contact_name') or raw.get('contactName', ''),
        'contact_email': raw.get('email') or raw.get('contact_email') or raw.get('contactEmail', ''),
        'contact_phone': raw.get('phone') or raw.get('contact_phone') or raw.get('contactPhone', ''),
        'services': services,
        'service_category': raw.get('service_category') or raw.get('type') or 'multi',
        'state': raw.get('state', 'MI'),
        'county': raw.get('county', ''),
    }


def _get_client_by_code(code: str) -> Optional[dict]:
    """Fetch client record by magic link code. Maps to clients.json / portal store."""
    if code in CLIENT_PORTAL_STORE:
        return CLIENT_PORTAL_STORE[code]

    needle = (code or '').strip().upper()
    if not needle:
        return None

    for raw in _load_prism_json(PRISM_CLIENTS_FILE, []):
        portal = str(raw.get('portal_code') or raw.get('code') or '').upper()
        cid = str(raw.get('id') or '').upper()
        if portal == needle or cid == needle:
            return _client_portal_record(raw, code)

    return None


def _orders_for_client(client: dict) -> List[dict]:
    """Return PRISM orders belonging to this client (by id or client name)."""
    orders = _load_prism_json(PRISM_ORDERS_FILE, [])
    cid = client.get('id')
    cname = client.get('name')
    cc = client.get('code')
    matched = []
    for o in orders:
        if cid and o.get('client_id') == cid:
            matched.append(o)
        elif cname and o.get('client') == cname:
            matched.append(o)
        elif cc and o.get('client_code') == cc:
            matched.append(o)
    return matched


@prism_router.route('/prism/client-portal/<client_code>', methods=['GET'])
def api_client_portal_home(client_code):
    """Client portal data — returns everything the frontend needs in one call.
    Connected to PRISM orders, documents, invoices, and calendar."""
    client = _get_client_by_code(client_code)
    if not client:
        return jsonify({'error': 'Invalid or expired link'}), 404

    client_orders = _orders_for_client(client)
    portal_orders = [
        {
            'id': o.get('id'),
            'type': o.get('type') or o.get('service_key'),
            'subject': o.get('signer') or o.get('service_label') or '',
            'status': (o.get('status') or 'pending').lower().replace(' ', '_'),
            'scheduledDate': o.get('date'),
            'scheduledTime': o.get('time'),
            'location': o.get('collection_site') or o.get('address'),
            'notes': o.get('notes') or '',
            'createdAt': (o.get('created_at') or '')[:10],
        }
        for o in client_orders
    ]

    return jsonify({
        'client': client,
        'orders': portal_orders,
        'documents': [],
        'invoices': [],
        'services_available': [
            {
                'type': svc_key,
                'label': svc_val['label'],
                'service_line': svc_val['service_line'],
            }
            for svc_key, svc_val in SERVICE_CATALOG.items()
            if svc_key in client.get('services', [])
        ],
    })


@prism_router.route('/prism/client-portal/<client_code>/orders', methods=['GET'])
def api_client_orders(client_code):
    """List all orders for this client (active + history)."""
    client = _get_client_by_code(client_code)
    if not client:
        return jsonify({'error': 'Invalid link'}), 404
    portal_orders = [
        {
            'id': o.get('id'),
            'type': o.get('type') or o.get('service_key'),
            'subject': o.get('signer') or '',
            'status': (o.get('status') or 'pending').lower().replace(' ', '_'),
            'createdAt': (o.get('created_at') or '')[:10],
        }
        for o in _orders_for_client(client)
    ]
    return jsonify({'orders': portal_orders})


@prism_router.route('/prism/client-portal/<client_code>/orders', methods=['POST'])
def api_client_submit_order(client_code):
    """Client submits a new service request — enters PRISM order queue.
    This triggers the service router to assign fulfillment."""
    client = _get_client_by_code(client_code)
    if not client:
        return jsonify({'error': 'Invalid link'}), 404

    data = request.get_json() or {}
    service_type = data.get('service_type')
    subject_name = data.get('subject_name')
    urgent = data.get('urgent', False)

    if not service_type or not subject_name:
        return jsonify({'error': 'service_type and subject_name required'}), 400

    if service_type not in SERVICE_CATALOG:
        return jsonify({'error': f'Service type not available: {service_type}'}), 400

    # Route through PRISM service router
    routing = route_order(
        service_type=service_type,
        client_state=client.get('state', ''),
        client_county=client.get('county', ''),
        urgent=urgent,
    )

    order_id = f'ORD-{datetime.now().strftime("%Y")}-{str(uuid.uuid4())[:4].upper()}'

    order = {
        'id': order_id,
        'client_id': client['id'],
        'client_code': client_code,
        'service_type': service_type,
        'subject_name': subject_name,
        'subject_phone': data.get('subject_phone', ''),
        'subject_dob': data.get('subject_dob', ''),
        'subject_cdl': data.get('subject_cdl', ''),
        'notes': data.get('notes', ''),
        'urgent': urgent,
        'status': 'pending',
        'created_at': datetime.now().isoformat(),
        'routing': routing,
    }

    # Production: write to Airtable PRISM_ORDERS table
    # airtable.create('PRISM_ORDERS', order)

    # Log to NEXUS learning engine
    nxlearn('client_portal_order', {
        'client_code': client_code,
        'service_type': service_type,
        'routing_mode': routing.get('fulfillment_mode'),
        'margin_pct': routing.get('revenue_model', {}).get('margin_pct'),
    })

    return jsonify({
        'success': True,
        'order': order,
        'message': f'Request received. Your DDI team is on it.',
        'routing_summary': {
            'mode': routing.get('fulfillment_mode'),
            'partner': routing.get('assigned_partner'),
            'estimated_schedule': '1-2 business days' if not urgent else 'Within 8 hours',
        }
    }), 201


@prism_router.route('/prism/client-portal/<client_code>/documents', methods=['GET'])
def api_client_documents(client_code):
    """All documents available to this client (results, scanbacks, reports)."""
    client = _get_client_by_code(client_code)
    if not client:
        return jsonify({'error': 'Invalid link'}), 404
    # Production: query Airtable PRISM_DOCUMENTS where client_id = client['id']
    return jsonify({'documents': []})


@prism_router.route('/prism/client-portal/<client_code>/invoices', methods=['GET'])
def api_client_invoices(client_code):
    """All invoices for this client."""
    client = _get_client_by_code(client_code)
    if not client:
        return jsonify({'error': 'Invalid link'}), 404
    # Production: query Airtable PRISM_INVOICES where client_id = client['id']
    return jsonify({'invoices': []})


@prism_router.route('/prism/client-portal/<client_code>/invoices/<invoice_id>/pay', methods=['POST'])
def api_client_pay_invoice(client_code, invoice_id):
    """Initiate payment for an invoice — creates Stripe checkout session."""
    client = _get_client_by_code(client_code)
    if not client:
        return jsonify({'error': 'Invalid link'}), 404

    # Production: create Stripe checkout session for the invoice amount
    # stripe.checkout.Session.create(...)
    return jsonify({
        'success': True,
        'checkout_url': f'https://checkout.stripe.com/pay/{invoice_id}',
        'message': 'Redirecting to secure payment...',
    })


@prism_router.route('/prism/client-portal/<client_code>/calendar', methods=['GET'])
def api_client_calendar(client_code):
    """Calendar events for this client — derived from scheduled orders."""
    client = _get_client_by_code(client_code)
    if not client:
        return jsonify({'error': 'Invalid link'}), 404
    # Production: query PRISM_ORDERS where client_id = client['id'] AND status IN ('scheduled', 'completed')
    # Transform to calendar events
    return jsonify({'events': []})


@prism_router.route('/prism/client-portal/generate-link', methods=['POST'])
def api_generate_client_link():
    """DDI internal: Generate a new magic link for a client.
    Called from PRISM when onboarding a new client."""
    data = request.get_json() or {}
    client_name = data.get('client_name')
    contact_email = data.get('contact_email')
    services = data.get('services', [])

    if not client_name or not contact_email:
        return jsonify({'error': 'client_name and contact_email required'}), 400

    # Generate unique code
    code = f'{client_name[:3].upper()}-{str(uuid.uuid4())[:5].upper()}'

    client_record = {
        'id': str(uuid.uuid4()),
        'code': code,
        'name': client_name,
        'contact_email': contact_email,
        'services': services,
        'created_at': datetime.now().isoformat(),
    }

    CLIENT_PORTAL_STORE[code] = client_record
    # Production: write to Airtable PRISM_CLIENTS table

    portal_url = f'https://portal.deedavis.biz/client/{code}'

    return jsonify({
        'success': True,
        'client_code': code,
        'portal_url': portal_url,
        'message': f'Portal link generated for {client_name}. Send to {contact_email}.',
    })
