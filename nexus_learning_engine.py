#!/usr/bin/env python3
"""
NEXUS LEARNING ENGINE — THE BRAIN
====================================
System-wide self-learning backbone for ALL NEXUS modules. Every action Dee takes,
every outcome recorded, every pattern discovered — it all flows through here.

DOMAINS (one per NEXUS module):
  1. OPPORTUNITIES  — Mining → Scoring → Pursue/Skip → Bid → Win/Lose
  2. OUTREACH       — Email sent → Opened → Responded → Relationship built
  3. BIDS           — Go/No-Go → Prepared → Submitted → Won/Lost → Margin
  4. SUPPLIERS       — Quoted → Price competitiveness → Delivery → Quality
  5. SUBCONTRACTORS — Vetted → Hired → Performance → Retained/Replaced
  6. PRICING        — Markup set → Won/Lost → Actual margin → Market position
  7. INTELLIGENCE   — Prime contacted → Responded → Sub-under → Recompete

LEARNING LOOP (applies to every domain):
  Event happens → Logged with metadata → Patterns analyzed → Weights adjusted → Better decisions

This module replaces intelligence_learning.py as the central learning store.
"""

import os
import json
import copy
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from collections import defaultdict
from dotenv import load_dotenv

load_dotenv()

LEARNING_DB_PATH = Path(os.environ.get(
    'NEXUS_LEARNING_DB',
    '/Users/deedavis/NEXUS BACKEND/nexus_learning_db.json'
))

# ─── DOMAIN DEFINITIONS ─────────────────────────────────────────────────────

DOMAINS = {
    # ─── GPSS: Government Pipeline & Sourcing ─────────────────────────────────
    'opportunities': {
        'name': 'Opportunity Mining',
        'actions': [
            'discovered', 'scored', 'reviewed', 'pursued', 'skipped',
            'bid_submitted', 'won', 'lost', 'expired',
        ],
        'positive': {'pursued', 'bid_submitted', 'won'},
        'negative': {'skipped', 'lost', 'expired'},
        'terminal': {'won', 'lost', 'skipped', 'expired'},
        'key_fields': ['naics', 'set_aside', 'agency', 'value_range', 'source', 'state'],
    },
    'outreach': {
        'name': 'Email & Outreach',
        'actions': [
            'email_drafted', 'email_sent', 'email_opened', 'email_responded',
            'meeting_scheduled', 'relationship_built', 'no_response',
        ],
        'positive': {'email_responded', 'meeting_scheduled', 'relationship_built'},
        'negative': {'no_response'},
        'terminal': {'relationship_built', 'no_response'},
        'key_fields': ['recipient_type', 'agency', 'subject_pattern', 'has_cap_statement', 'biohack_score'],
    },
    'bids': {
        'name': 'Bid Workflow',
        'actions': [
            'identified', 'go_decision', 'nogo_decision', 'rfq_sent',
            'quotes_received', 'bid_prepared', 'bid_submitted', 'won', 'lost',
            'debriefed',
        ],
        'positive': {'go_decision', 'bid_submitted', 'won'},
        'negative': {'nogo_decision', 'lost'},
        'terminal': {'won', 'lost', 'nogo_decision'},
        'key_fields': ['contract_type', 'set_aside', 'agency', 'value_range', 'competition_level', 'naics'],
    },
    'suppliers': {
        'name': 'Supplier Management',
        'actions': [
            'rfq_sent', 'quote_received', 'quote_competitive', 'quote_expensive',
            'selected', 'delivered_on_time', 'delivered_late', 'quality_good',
            'quality_poor', 'will_reuse', 'will_not_reuse',
        ],
        'positive': {'quote_competitive', 'delivered_on_time', 'quality_good', 'will_reuse'},
        'negative': {'quote_expensive', 'delivered_late', 'quality_poor', 'will_not_reuse'},
        'terminal': {'will_reuse', 'will_not_reuse'},
        'key_fields': ['supplier_name', 'product_type', 'response_days', 'price_vs_market'],
    },
    'subcontractors': {
        'name': 'Subcontractor Management',
        'actions': [
            'identified', 'vetted', 'nda_signed', 'coi_received', 'hired',
            'performing_well', 'performing_poorly', 'retained', 'replaced',
        ],
        'positive': {'nda_signed', 'coi_received', 'hired', 'performing_well', 'retained'},
        'negative': {'performing_poorly', 'replaced'},
        'terminal': {'retained', 'replaced'},
        'key_fields': ['service_type', 'region', 'certifications', 'contract_value'],
    },
    'pricing': {
        'name': 'Pricing Strategy',
        'actions': [
            'markup_set', 'price_submitted', 'price_won', 'price_lost',
            'price_too_high', 'price_too_low', 'margin_achieved',
        ],
        'positive': {'price_won', 'margin_achieved'},
        'negative': {'price_lost', 'price_too_high', 'price_too_low'},
        'terminal': {'price_won', 'price_lost'},
        'key_fields': ['markup_pct', 'contract_type', 'value_range', 'competition_level'],
    },
    'intelligence': {
        'name': 'Contract Intelligence',
        'actions': [
            'discovered', 'reviewed', 'contacted', 'responded', 'meeting',
            'pursuing', 'bid_submitted', 'won', 'lost', 'skipped', 'no_response',
        ],
        'positive': {'responded', 'meeting', 'pursuing', 'bid_submitted', 'won'},
        'negative': {'no_response', 'lost', 'skipped'},
        'terminal': {'won', 'lost', 'skipped', 'no_response'},
        'key_fields': ['lane', 'agency', 'avenue', 'value_range', 'prime_company'],
    },

    # ─── PRISM: Service Delivery & QC ─────────────────────────────────────────
    'service_orders': {
        'name': 'PRISM Service Orders',
        'actions': [
            'order_created', 'order_routed', 'agent_assigned', 'in_progress',
            'completed', 'failed', 'cancelled', 'rescheduled',
            'scanback_received', 'qc_passed', 'qc_failed', 'qc_rework',
            'invoiced', 'paid',
        ],
        'positive': {'completed', 'qc_passed', 'paid'},
        'negative': {'failed', 'cancelled', 'qc_failed'},
        'terminal': {'completed', 'failed', 'cancelled', 'paid'},
        'key_fields': ['service_type', 'division', 'agent_id', 'region', 'client_id', 'turnaround_hours'],
    },
    'agent_performance': {
        'name': 'PRISM Agent Performance',
        'actions': [
            'order_assigned', 'order_completed', 'order_failed',
            'qc_passed', 'qc_failed', 'client_complaint', 'client_praise',
            'certified', 'decertified', 'training_completed',
        ],
        'positive': {'order_completed', 'qc_passed', 'client_praise', 'certified', 'training_completed'},
        'negative': {'order_failed', 'qc_failed', 'client_complaint', 'decertified'},
        'terminal': {'decertified'},
        'key_fields': ['agent_id', 'service_type', 'division', 'region', 'certification_level'],
    },

    # ─── VERTEX: Billing & Revenue ────────────────────────────────────────────
    'billing': {
        'name': 'VERTEX Billing',
        'actions': [
            'invoice_created', 'invoice_sent', 'payment_received', 'payment_late',
            'claim_submitted', 'claim_approved', 'claim_denied', 'claim_appealed',
            'write_off', 'collection_started',
        ],
        'positive': {'payment_received', 'claim_approved'},
        'negative': {'payment_late', 'claim_denied', 'write_off'},
        'terminal': {'payment_received', 'write_off'},
        'key_fields': ['client_id', 'service_type', 'invoice_amount', 'days_to_pay', 'payer_type'],
    },

    # ─── COMPASS: Relationships & CRM ─────────────────────────────────────────
    'relationships': {
        'name': 'COMPASS Relationships',
        'actions': [
            'contact_added', 'contact_updated', 'touchpoint_logged',
            'meeting_held', 'proposal_sent', 'contract_signed',
            'relationship_cold', 'relationship_warm', 'relationship_hot',
            'referral_received', 'referral_given',
        ],
        'positive': {'meeting_held', 'contract_signed', 'relationship_hot', 'referral_received'},
        'negative': {'relationship_cold'},
        'terminal': {'contract_signed'},
        'key_fields': ['contact_type', 'organization', 'industry', 'relationship_stage', 'last_touchpoint_days'],
    },

    # ─── ATLAS: Partner Onboarding ────────────────────────────────────────────
    'partner_onboarding': {
        'name': 'ATLAS Partner Onboarding',
        'actions': [
            'lead_identified', 'outreach_sent', 'interest_confirmed',
            'nda_sent', 'nda_signed', 'credentials_verified',
            'training_assigned', 'training_completed', 'activated',
            'first_order_completed', 'churned',
        ],
        'positive': {'interest_confirmed', 'nda_signed', 'activated', 'first_order_completed'},
        'negative': {'churned'},
        'terminal': {'activated', 'churned'},
        'key_fields': ['partner_type', 'service_types', 'region', 'onboarding_days', 'source'],
    },

    # ─── TRANSPORT: NEMT & Courier ────────────────────────────────────────────
    'transport': {
        'name': 'Transport & Courier',
        'actions': [
            'trip_requested', 'trip_scheduled', 'driver_assigned',
            'trip_started', 'trip_completed', 'trip_cancelled', 'trip_no_show',
            'delivery_completed', 'delivery_failed', 'delivery_rescheduled',
            'client_satisfied', 'client_complaint',
        ],
        'positive': {'trip_completed', 'delivery_completed', 'client_satisfied'},
        'negative': {'trip_cancelled', 'trip_no_show', 'delivery_failed', 'client_complaint'},
        'terminal': {'trip_completed', 'trip_cancelled', 'trip_no_show', 'delivery_completed', 'delivery_failed'},
        'key_fields': ['transport_type', 'region', 'driver_id', 'mco_id', 'trip_distance', 'fulfillment_partner'],
    },

    # ─── DDCSS: Corporate Sales System ─────────────────────────────────────────
    'ddcss_prospects': {
        'name': 'DDCSS Corporate Prospects',
        'actions': [
            'lead_identified', 'lead_qualified', 'avatar_built', 'pitch_generated',
            'outreach_sent', 'responded', 'meeting_scheduled', 'proposal_sent',
            'contract_signed', 'lost', 'nurturing', 'disqualified',
        ],
        'positive': {'lead_qualified', 'responded', 'meeting_scheduled', 'proposal_sent', 'contract_signed'},
        'negative': {'lost', 'disqualified'},
        'terminal': {'contract_signed', 'lost', 'disqualified'},
        'key_fields': ['sector', 'company_size', 'industry', 'source', 'deal_value', 'sales_cycle_days'],
    },
    'ddcss_pipeline': {
        'name': 'DDCSS Sales Pipeline',
        'actions': [
            'stage_discovery', 'stage_qualification', 'stage_proposal',
            'stage_negotiation', 'stage_closed_won', 'stage_closed_lost',
            'deal_stalled', 'deal_reactivated',
        ],
        'positive': {'stage_proposal', 'stage_negotiation', 'stage_closed_won'},
        'negative': {'stage_closed_lost', 'deal_stalled'},
        'terminal': {'stage_closed_won', 'stage_closed_lost'},
        'key_fields': ['sector', 'deal_value', 'probability', 'days_in_stage', 'competitor'],
    },

    # ─── JETA: Jet Fuel Trading & Fraud Detection ──────────────────────────────
    'jeta_deals': {
        'name': 'JETA Trading Deals',
        'actions': [
            'deal_created', 'counterparty_scored', 'kyc_started', 'kyc_passed', 'kyc_failed',
            'deal_approved', 'deal_blocked', 'contract_drafted', 'contract_signed',
            'shipment_started', 'shipment_completed', 'payment_received',
            'fraud_flagged', 'deal_cancelled',
        ],
        'positive': {'kyc_passed', 'deal_approved', 'contract_signed', 'shipment_completed', 'payment_received'},
        'negative': {'kyc_failed', 'deal_blocked', 'fraud_flagged', 'deal_cancelled'},
        'terminal': {'payment_received', 'deal_blocked', 'deal_cancelled'},
        'key_fields': ['product_type', 'counterparty_type', 'deal_value', 'fraud_score', 'region'],
    },
    'jeta_fraud': {
        'name': 'JETA Fraud Detection',
        'actions': [
            'term_flagged', 'pattern_detected', 'manual_review', 'cleared',
            'blocked', 'reported', 'false_positive',
        ],
        'positive': {'cleared', 'false_positive'},
        'negative': {'blocked', 'reported'},
        'terminal': {'cleared', 'blocked', 'reported'},
        'key_fields': ['flag_type', 'severity', 'counterparty', 'product_type'],
    },

    # ─── SHIELD: Service Verification (Cause We Care) ──────────────────────────
    'shield_referrals': {
        'name': 'SHIELD Referrals',
        'actions': [
            'referral_received', 'screened', 'qualified', 'disqualified',
            'family_enrolled', 'services_assigned', 'services_started',
            'services_completed', 'billing_submitted', 'payment_received',
            'case_closed', 'case_escalated',
        ],
        'positive': {'qualified', 'family_enrolled', 'services_completed', 'payment_received'},
        'negative': {'disqualified', 'case_escalated'},
        'terminal': {'case_closed', 'disqualified'},
        'key_fields': ['referral_source', 'service_type', 'county', 'payer', 'family_size'],
    },
    'shield_verification': {
        'name': 'SHIELD Service Verification',
        'actions': [
            'verification_started', 'sms_sent', 'sms_response_received',
            'step_completed', 'step_failed', 'all_steps_complete',
            'verification_passed', 'verification_failed', 'escalated',
        ],
        'positive': {'sms_response_received', 'step_completed', 'all_steps_complete', 'verification_passed'},
        'negative': {'step_failed', 'verification_failed', 'escalated'},
        'terminal': {'verification_passed', 'verification_failed'},
        'key_fields': ['service_type', 'contractor_id', 'response_time_hours', 'steps_completed'],
    },

    # ─── LBPC: Surplus Recovery ────────────────────────────────────────────────
    'lbpc_leads': {
        'name': 'LBPC Surplus Recovery Leads',
        'actions': [
            'lead_mined', 'lead_scored', 'initial_notice_sent', 'response_received',
            'claim_filed', 'documentation_submitted', 'claim_approved', 'claim_denied',
            'payment_received', 'lead_expired', 'lead_disqualified',
        ],
        'positive': {'response_received', 'claim_filed', 'claim_approved', 'payment_received'},
        'negative': {'claim_denied', 'lead_expired', 'lead_disqualified'},
        'terminal': {'payment_received', 'claim_denied', 'lead_expired', 'lead_disqualified'},
        'key_fields': ['county', 'property_type', 'estimated_value', 'source', 'claim_type'],
    },

    # ─── GBIS: Grants Intelligence System ──────────────────────────────────────
    'gbis_grants': {
        'name': 'GBIS Grant Opportunities',
        'actions': [
            'grant_discovered', 'grant_scored', 'eligibility_checked', 'eligible', 'ineligible',
            'application_started', 'application_submitted', 'awarded', 'not_awarded',
            'reporting_completed', 'grant_closed',
        ],
        'positive': {'eligible', 'application_submitted', 'awarded', 'reporting_completed'},
        'negative': {'ineligible', 'not_awarded'},
        'terminal': {'awarded', 'not_awarded', 'ineligible', 'grant_closed'},
        'key_fields': ['funding_agency', 'grant_type', 'applicant_entity', 'award_amount', 'research_subtype'],
    },

    # ─── ATLAS PM: Project Management ──────────────────────────────────────────
    'atlas_projects': {
        'name': 'ATLAS Project Management',
        'actions': [
            'project_created', 'rfp_analyzed', 'wbs_generated', 'tasks_assigned',
            'milestone_reached', 'milestone_missed', 'change_order_submitted',
            'change_order_approved', 'change_order_denied',
            'project_completed', 'project_cancelled', 'project_on_hold',
        ],
        'positive': {'rfp_analyzed', 'milestone_reached', 'change_order_approved', 'project_completed'},
        'negative': {'milestone_missed', 'change_order_denied', 'project_cancelled'},
        'terminal': {'project_completed', 'project_cancelled'},
        'key_fields': ['project_type', 'client_id', 'budget', 'duration_days', 'team_size'],
    },
}

# ─── BASELINE WEIGHTS PER DOMAIN ────────────────────────────────────────────

BASELINE_WEIGHTS = {
    'opportunities': {
        'edwosb_set_aside': 30,
        'wosb_set_aside': 25,
        'small_biz_set_aside': 20,
        'naics_match': 25,
        'value_sweet_spot': 20,
        'home_state': 10,
        'past_performance_match': 15,
    },
    'outreach': {
        'has_co_name': 15,
        'has_cap_statement': 20,
        'agency_name_in_subject': 15,
        'edwosb_in_first_para': 10,
        'smart_questions': 10,
        'human_touch_tone': 10,
        'biohack_score_above_70': 20,
    },
    'bids': {
        'set_aside_match': 30,
        'naics_match': 20,
        'value_under_500k': 25,
        'value_under_2m': 15,
        'past_performance': 20,
        'edwosb_advantage': 25,
        'low_competition': 15,
    },
    'suppliers': {
        'response_under_48h': 25,
        'price_within_10pct_market': 20,
        'delivery_on_time': 30,
        'quality_rating': 25,
    },
    'subcontractors': {
        'relevant_experience': 25,
        'proper_insurance': 20,
        'geographic_match': 15,
        'past_performance': 25,
        'certifications': 15,
    },
    'pricing': {
        'markup_15_25_pct': 25,
        'markup_25_35_pct': 15,
        'competitive_intelligence': 20,
        'edwosb_premium': 10,
    },
    'intelligence': {
        'sub_under_prime': {
            'has_contact_info': 40,
            'prime_in_directory': 20,
            'is_priority_lane': 20,
            'value_under_50m': 20,
            'value_under_500m': 10,
            'value_over_500m': 5,
        },
        'prime_recompete': {
            'is_priority_lane': 30,
            'value_under_10m': 30,
            'value_under_50m': 20,
            'value_under_200m': 10,
            'value_over_200m': 5,
            'va_agency': 15,
            'hhs_agency': 10,
        },
        'hire_subs': {
            'priority_lane': 25,
            'value_under_25m': 25,
            'value_under_100m': 15,
            'high_sub_availability': 20,
        },
    },

    # ─── PRISM: Service Delivery ──────────────────────────────────────────────
    'service_orders': {
        'agent_certified': 25,
        'same_day_completion': 20,
        'qc_first_pass': 30,
        'client_repeat': 15,
        'region_match': 10,
    },
    'agent_performance': {
        'completion_rate': 30,
        'qc_pass_rate': 25,
        'client_satisfaction': 25,
        'certifications_current': 10,
        'response_time': 10,
    },

    # ─── VERTEX: Billing ──────────────────────────────────────────────────────
    'billing': {
        'payment_under_30_days': 30,
        'payment_under_60_days': 15,
        'claim_first_submission_approval': 25,
        'no_write_offs': 20,
        'client_payment_history': 10,
    },

    # ─── COMPASS: Relationships ───────────────────────────────────────────────
    'relationships': {
        'recent_touchpoint': 25,
        'multiple_contacts_at_org': 15,
        'past_contract': 30,
        'referral_source': 20,
        'industry_match': 10,
    },

    # ─── ATLAS: Partner Onboarding ────────────────────────────────────────────
    'partner_onboarding': {
        'fast_nda_turnaround': 15,
        'credentials_verified': 25,
        'training_completed': 20,
        'first_order_success': 30,
        'geographic_coverage': 10,
    },

    # ─── TRANSPORT: NEMT & Courier ────────────────────────────────────────────
    'transport': {
        'on_time_arrival': 30,
        'no_cancellations': 20,
        'client_satisfaction': 25,
        'driver_rating': 15,
        'route_efficiency': 10,
    },

    # ─── DDCSS: Corporate Sales ─────────────────────────────────────────────────
    'ddcss_prospects': {
        'qualified_lead': 25,
        'avatar_quality': 15,
        'pitch_personalization': 20,
        'response_rate': 30,
        'deal_value_match': 10,
    },
    'ddcss_pipeline': {
        'stage_velocity': 25,
        'win_rate_by_sector': 30,
        'deal_size_accuracy': 20,
        'competitor_presence': 15,
        'qualification_accuracy': 10,
    },

    # ─── JETA: Jet Fuel Trading ─────────────────────────────────────────────────
    'jeta_deals': {
        'kyc_pass_rate': 30,
        'fraud_score_accuracy': 25,
        'deal_completion_rate': 25,
        'payment_on_time': 15,
        'counterparty_reliability': 5,
    },
    'jeta_fraud': {
        'flag_accuracy': 35,
        'false_positive_rate': 25,
        'detection_speed': 20,
        'pattern_recognition': 15,
        'manual_review_quality': 5,
    },

    # ─── SHIELD: Service Verification ───────────────────────────────────────────
    'shield_referrals': {
        'qualification_accuracy': 25,
        'enrollment_rate': 25,
        'service_completion_rate': 30,
        'billing_accuracy': 15,
        'referral_source_quality': 5,
    },
    'shield_verification': {
        'sms_response_rate': 25,
        'verification_completion_rate': 30,
        'step_pass_rate': 25,
        'escalation_rate': 15,
        'response_time': 5,
    },

    # ─── LBPC: Surplus Recovery ─────────────────────────────────────────────────
    'lbpc_leads': {
        'lead_quality_score': 25,
        'response_rate': 25,
        'claim_approval_rate': 30,
        'payment_success_rate': 15,
        'county_performance': 5,
    },

    # ─── GBIS: Grants Intelligence ──────────────────────────────────────────────
    'gbis_grants': {
        'eligibility_accuracy': 25,
        'application_quality': 25,
        'award_rate': 30,
        'funding_agency_match': 15,
        'applicant_entity_fit': 5,
    },

    # ─── ATLAS PM: Project Management ───────────────────────────────────────────
    'atlas_projects': {
        'on_time_delivery': 30,
        'budget_accuracy': 25,
        'milestone_hit_rate': 25,
        'change_order_approval': 15,
        'client_satisfaction': 5,
    },
}


class NexusLearningEngine:
    """
    The brain of NEXUS. Tracks every event across all domains,
    analyzes patterns, and adjusts scoring weights system-wide.
    """

    def __init__(self):
        self._data = None
        self._anthropic = None

    def _get_anthropic(self):
        if self._anthropic is None:
            import anthropic
            self._anthropic = anthropic.Anthropic(
                api_key=os.environ.get('ANTHROPIC_API_KEY', '')
            )
        return self._anthropic

    # ─── DATA PERSISTENCE ────────────────────────────────────────────────

    def _load_data(self) -> Dict:
        if self._data is not None:
            return self._data
        if LEARNING_DB_PATH.exists():
            with open(LEARNING_DB_PATH, 'r') as f:
                self._data = json.load(f)
        else:
            self._data = {
                'events': [],
                'insights': [],
                'learned_weights': {},
                'weight_history': [],
                'analysis_history': [],
                'stats': {
                    'total_events': 0,
                    'events_by_domain': {},
                    'total_analyses': 0,
                    'last_analysis': None,
                },
            }
        return self._data

    def _save_data(self):
        if self._data:
            with open(LEARNING_DB_PATH, 'w') as f:
                json.dump(self._data, f, indent=2, default=str)

    # ─── LOG — Universal event logging ───────────────────────────────────

    def log(self, domain: str, entity_id: str, action: str, metadata: Dict = None) -> Dict:
        """
        Log ANY event from ANY NEXUS module.
        
        domain:    'opportunities', 'outreach', 'bids', 'suppliers', etc.
        entity_id: Unique ID for the entity (opportunity ID, email ID, bid ID, etc.)
        action:    Domain-specific action (see DOMAINS dict for valid actions)
        metadata:  Any relevant data (agency, value, lane, supplier name, etc.)
        """
        if domain not in DOMAINS:
            return {'error': f'Unknown domain: {domain}. Valid: {list(DOMAINS.keys())}'}

        domain_def = DOMAINS[domain]
        if action not in domain_def['actions']:
            return {'error': f'Invalid action "{action}" for domain "{domain}". Valid: {domain_def["actions"]}'}

        data = self._load_data()

        event = {
            'id': hashlib.md5(
                f"{domain}-{entity_id}-{action}-{datetime.now().isoformat()}".encode()
            ).hexdigest()[:12],
            'domain': domain,
            'entity_id': entity_id,
            'action': action,
            'timestamp': datetime.now().isoformat(),
            'metadata': metadata or {},
            'is_positive': action in domain_def['positive'],
            'is_negative': action in domain_def['negative'],
            'is_terminal': action in domain_def['terminal'],
        }

        data['events'].append(event)
        data['stats']['total_events'] = len(data['events'])
        domain_counts = data['stats'].setdefault('events_by_domain', {})
        domain_counts[domain] = domain_counts.get(domain, 0) + 1
        self._save_data()

        return {'success': True, 'event': event}

    # ─── ANALYZE — Pattern finding across all domains ────────────────────

    def analyze(self, domain: str = None, use_ai: bool = True) -> Dict:
        """
        Run analysis. If domain is specified, analyze that domain only.
        If None, analyze all domains with sufficient data.
        """
        data = self._load_data()
        all_events = data.get('events', [])

        if len(all_events) < 3:
            return {
                'status': 'insufficient_data',
                'message': f'Need at least 3 events. Currently have {len(all_events)}.',
            }

        domains_to_analyze = [domain] if domain else [
            d for d in DOMAINS
            if sum(1 for e in all_events if e['domain'] == d) >= 2
        ]

        all_insights = []
        all_patterns = []
        weights_updated = False

        for d in domains_to_analyze:
            domain_events = [e for e in all_events if e['domain'] == d]
            if len(domain_events) < 2:
                continue

            summary = self._build_domain_summary(d, domain_events)
            result = self._analyze_domain(d, summary, data)

            all_insights.extend(result.get('insights', []))
            all_patterns.extend(result.get('patterns', []))

            if result.get('new_weights'):
                domain_key = d
                old_w = data.get('learned_weights', {}).get(domain_key, {})
                data.setdefault('learned_weights', {})[domain_key] = result['new_weights']
                data.setdefault('weight_history', []).append({
                    'timestamp': datetime.now().isoformat(),
                    'domain': domain_key,
                    'old_weights': old_w,
                    'new_weights': result['new_weights'],
                    'reason': result.get('weight_change_reason', 'Statistical analysis'),
                })
                weights_updated = True

        if all_insights:
            for ins in all_insights:
                ins['generated_at'] = datetime.now().isoformat()
            data['insights'] = all_insights + data.get('insights', [])
            data['insights'] = data['insights'][:100]

        data['stats']['total_analyses'] = len(data.get('analysis_history', [])) + 1
        data['stats']['last_analysis'] = datetime.now().isoformat()
        data.setdefault('analysis_history', []).append({
            'timestamp': datetime.now().isoformat(),
            'domains_analyzed': domains_to_analyze,
            'events_count': len(all_events),
            'insights_generated': len(all_insights),
            'weights_updated': weights_updated,
        })

        if weights_updated:
            data['stats']['last_weight_update'] = datetime.now().isoformat()

        self._save_data()

        return {
            'status': 'complete',
            'domains_analyzed': domains_to_analyze,
            'total_events': len(all_events),
            'insights_generated': len(all_insights),
            'weights_updated': weights_updated,
            'insights': all_insights,
            'patterns': all_patterns,
        }

    def _build_domain_summary(self, domain: str, events: List[Dict]) -> Dict:
        """Build outcome statistics for a single domain."""
        domain_def = DOMAINS[domain]
        by_entity = defaultdict(list)
        for e in events:
            by_entity[e['entity_id']].append(e)

        outcomes = []
        for eid, entity_events in by_entity.items():
            sorted_ev = sorted(entity_events, key=lambda x: x['timestamp'])
            last = sorted_ev[-1]
            merged_meta = {}
            for ev in sorted_ev:
                merged_meta.update(ev.get('metadata', {}))

            outcomes.append({
                'entity_id': eid,
                'actions': [e['action'] for e in sorted_ev],
                'final_action': last['action'],
                'is_positive': last['is_positive'],
                'is_negative': last['is_negative'],
                'is_terminal': last['is_terminal'],
                'metadata': merged_meta,
            })

        by_field = {}
        for field in domain_def.get('key_fields', []):
            field_stats = defaultdict(lambda: {'positive': 0, 'negative': 0, 'total': 0})
            for o in outcomes:
                val = o['metadata'].get(field, 'Unknown')
                field_stats[val]['total'] += 1
                if o['is_positive']:
                    field_stats[val]['positive'] += 1
                if o['is_negative']:
                    field_stats[val]['negative'] += 1
            by_field[field] = dict(field_stats)

        total = len(outcomes)
        positive = sum(1 for o in outcomes if o['is_positive'])
        negative = sum(1 for o in outcomes if o['is_negative'])

        return {
            'domain': domain,
            'total_entities': total,
            'total_events': len(events),
            'positive_count': positive,
            'negative_count': negative,
            'positive_rate': positive / max(total, 1),
            'outcomes': outcomes,
            'by_field': by_field,
        }

    def _analyze_domain(self, domain: str, summary: Dict, data: Dict) -> Dict:
        """Statistical analysis for a single domain. Returns insights + weight adjustments."""
        current_weights = data.get('learned_weights', {}).get(domain, {})
        if not current_weights:
            current_weights = BASELINE_WEIGHTS.get(domain, {})

        new_weights = copy.deepcopy(current_weights)
        insights = []
        patterns = []
        domain_name = DOMAINS[domain]['name']

        # Overall rate
        rate = summary['positive_rate']
        if summary['total_entities'] >= 3:
            if rate >= 0.6:
                insights.append({
                    'title': f'{domain_name}: Strong performance',
                    'body': f'{rate:.0%} positive rate across {summary["total_entities"]} tracked items. Current approach is working.',
                    'impact': 'high',
                    'category': domain,
                    'domain': domain,
                })
            elif rate < 0.25 and summary['negative_count'] > 0:
                insights.append({
                    'title': f'{domain_name}: Needs attention',
                    'body': f'Only {rate:.0%} positive rate. Review strategy for this area.',
                    'impact': 'high',
                    'category': domain,
                    'domain': domain,
                })

        # Per-field analysis
        for field, field_data in summary.get('by_field', {}).items():
            for val, counts in field_data.items():
                if val == 'Unknown' or counts['total'] < 2:
                    continue

                val_rate = counts['positive'] / counts['total']
                field_label = field.replace('_', ' ').title()

                if val_rate >= 0.7 and counts['total'] >= 2:
                    patterns.append({
                        'pattern': f'{field_label}="{val}" has {val_rate:.0%} success in {domain_name}',
                        'confidence': 'high' if counts['total'] >= 4 else 'medium',
                        'evidence': f'{counts["positive"]} positive of {counts["total"]}',
                        'domain': domain,
                    })
                    insights.append({
                        'title': f'{val} is a winner ({domain_name})',
                        'body': f'{val_rate:.0%} positive rate for {field_label}="{val}". Double down on this.',
                        'impact': 'high',
                        'category': domain,
                        'domain': domain,
                    })
                elif val_rate <= 0.2 and counts['negative'] >= 2:
                    patterns.append({
                        'pattern': f'{field_label}="{val}" is underperforming in {domain_name}',
                        'confidence': 'medium',
                        'evidence': f'{counts["negative"]} negative of {counts["total"]}',
                        'domain': domain,
                    })
                    insights.append({
                        'title': f'{val} is not working ({domain_name})',
                        'body': f'Only {val_rate:.0%} positive for {field_label}="{val}". Consider different approach or deprioritize.',
                        'impact': 'medium',
                        'category': domain,
                        'domain': domain,
                    })

        # Domain-specific weight adjustments
        if domain == 'opportunities':
            new_weights = self._adjust_opportunity_weights(summary, new_weights)
        elif domain == 'outreach':
            new_weights = self._adjust_outreach_weights(summary, new_weights)
        elif domain == 'bids':
            new_weights = self._adjust_bid_weights(summary, new_weights)
        elif domain == 'intelligence':
            new_weights = self._adjust_intelligence_weights(summary, new_weights)

        changed = json.dumps(new_weights, sort_keys=True) != json.dumps(current_weights, sort_keys=True)

        return {
            'insights': insights,
            'patterns': patterns,
            'new_weights': new_weights if changed else None,
            'weight_change_reason': f'Statistical analysis of {summary["total_events"]} events in {domain_name}' if changed else None,
        }

    # ─── DOMAIN-SPECIFIC WEIGHT ADJUSTMENTS ──────────────────────────────

    def _adjust_opportunity_weights(self, summary: Dict, weights: Dict) -> Dict:
        """Adjust opportunity scoring weights based on outcomes."""
        sa_data = summary['by_field'].get('set_aside', {})
        for sa_type, counts in sa_data.items():
            if counts['total'] < 2:
                continue
            rate = counts['positive'] / counts['total']
            if 'edwosb' in sa_type.lower() or 'wosb' in sa_type.lower():
                if rate >= 0.5:
                    weights['edwosb_set_aside'] = min(40, weights.get('edwosb_set_aside', 30) + 5)
                elif rate < 0.2:
                    weights['edwosb_set_aside'] = max(15, weights.get('edwosb_set_aside', 30) - 5)

        agency_data = summary['by_field'].get('agency', {})
        for agency, counts in agency_data.items():
            if counts['total'] >= 3 and counts['positive'] / counts['total'] >= 0.6:
                weights[f'agency_bonus_{agency[:20].lower().replace(" ", "_")}'] = 10

        return weights

    def _adjust_outreach_weights(self, summary: Dict, weights: Dict) -> Dict:
        """Adjust outreach weights based on response patterns."""
        recip_data = summary['by_field'].get('recipient_type', {})
        for rtype, counts in recip_data.items():
            if counts['total'] < 2:
                continue
            rate = counts['positive'] / counts['total']
            if rate >= 0.5:
                weights[f'recipient_{rtype.lower()}_bonus'] = min(15, 5 + int(rate * 10))

        biohack_data = summary['by_field'].get('biohack_score', {})
        high_score_positive = sum(
            c['positive'] for k, c in biohack_data.items()
            if k not in ('Unknown', '') and self._safe_float(k) >= 70
        )
        high_score_total = sum(
            c['total'] for k, c in biohack_data.items()
            if k not in ('Unknown', '') and self._safe_float(k) >= 70
        )
        if high_score_total >= 2 and high_score_positive / high_score_total >= 0.5:
            weights['biohack_score_above_70'] = min(30, weights.get('biohack_score_above_70', 20) + 5)

        return weights

    def _adjust_bid_weights(self, summary: Dict, weights: Dict) -> Dict:
        """Adjust bid go/no-go weights based on win/loss patterns."""
        val_data = summary['by_field'].get('value_range', {})
        for vrange, counts in val_data.items():
            if counts['total'] < 2:
                continue
            rate = counts['positive'] / counts['total']
            if 'under' in vrange.lower() and '500k' in vrange.lower() and rate >= 0.5:
                weights['value_under_500k'] = min(35, weights.get('value_under_500k', 25) + 5)

        comp_data = summary['by_field'].get('competition_level', {})
        for level, counts in comp_data.items():
            if counts['total'] >= 2 and counts['positive'] / counts['total'] >= 0.6:
                weights[f'competition_{level.lower()}_bonus'] = 10

        return weights

    def _adjust_intelligence_weights(self, summary: Dict, weights: Dict) -> Dict:
        """Adjust contract intelligence weights. Handles nested structure."""
        if not isinstance(weights, dict):
            return weights

        avenue_data = summary['by_field'].get('avenue', {})
        for avenue, counts in avenue_data.items():
            if counts['total'] < 2 or avenue not in weights:
                continue
            rate = counts['positive'] / counts['total']
            if isinstance(weights.get(avenue), dict):
                for key in weights[avenue]:
                    if rate >= 0.6:
                        weights[avenue][key] = min(50, weights[avenue][key] + 3)
                    elif rate < 0.2:
                        weights[avenue][key] = max(5, weights[avenue][key] - 3)

        return weights

    # ─── QUERY — What modules and the dashboard call ─────────────────────

    def get_weights(self, domain: str) -> Dict:
        """Get active weights for a domain. Learned if available, else baseline."""
        data = self._load_data()
        learned = data.get('learned_weights', {}).get(domain)
        if learned:
            return learned
        return BASELINE_WEIGHTS.get(domain, {})

    def get_insights(self, domain: str = None, limit: int = 15) -> List[Dict]:
        """Get insights, optionally filtered by domain."""
        data = self._load_data()
        insights = data.get('insights', [])
        if domain:
            insights = [i for i in insights if i.get('domain') == domain]
        return insights[:limit]

    def get_entity_history(self, entity_id: str) -> List[Dict]:
        """Get full action history for an entity."""
        data = self._load_data()
        return [e for e in data.get('events', []) if e['entity_id'] == entity_id]

    def get_status(self) -> Dict:
        """Full learning system status for the dashboard."""
        data = self._load_data()
        events = data.get('events', [])

        by_domain = defaultdict(lambda: {
            'total': 0, 'positive': 0, 'negative': 0,
            'entities': set(), 'has_weights': False,
        })
        for e in events:
            d = by_domain[e['domain']]
            d['total'] += 1
            d['entities'].add(e['entity_id'])
            if e.get('is_positive'):
                d['positive'] += 1
            if e.get('is_negative'):
                d['negative'] += 1

        learned = data.get('learned_weights', {})
        domain_status = {}
        for dom in DOMAINS:
            ds = by_domain.get(dom, {'total': 0, 'positive': 0, 'negative': 0, 'entities': set()})
            total = ds['total']
            entities = len(ds['entities']) if isinstance(ds['entities'], set) else ds.get('entities', 0)

            if total == 0:
                level = 'inactive'
            elif total < 5:
                level = 'collecting'
            elif total < 15:
                level = 'learning'
            elif total < 30:
                level = 'growing'
            else:
                level = 'mature'

            domain_status[dom] = {
                'name': DOMAINS[dom]['name'],
                'events': total,
                'entities': entities,
                'positive': ds['positive'],
                'negative': ds['negative'],
                'positive_rate': ds['positive'] / max(total, 1),
                'level': level,
                'has_learned_weights': dom in learned,
                'weights_version': sum(
                    1 for wh in data.get('weight_history', []) if wh.get('domain') == dom
                ),
            }

        return {
            'total_events': len(events),
            'total_domains_active': sum(1 for d in domain_status.values() if d['events'] > 0),
            'total_analyses': data['stats'].get('total_analyses', 0),
            'last_analysis': data['stats'].get('last_analysis'),
            'last_weight_update': data['stats'].get('last_weight_update'),
            'insights_count': len(data.get('insights', [])),
            'domains': domain_status,
            'system_readiness': self._system_readiness(domain_status),
        }

    def _system_readiness(self, domain_status: Dict) -> Dict:
        """Overall system learning health."""
        active = sum(1 for d in domain_status.values() if d['events'] > 0)
        mature = sum(1 for d in domain_status.values() if d['level'] in ('growing', 'mature'))
        total_events = sum(d['events'] for d in domain_status.values())

        if active == 0:
            level = 'dormant'
            msg = 'No events tracked yet. Use NEXUS and the system will start learning.'
        elif active <= 2 and total_events < 10:
            level = 'waking'
            msg = f'{active} domains active. Keep using NEXUS — every action is training data.'
        elif mature == 0:
            level = 'learning'
            msg = f'{active} domains collecting data. Need more outcomes to adjust weights.'
        elif mature < 4:
            level = 'growing'
            msg = f'{mature} domains have enough data for weight adjustments. System getting smarter.'
        else:
            level = 'intelligent'
            msg = f'{mature} domains with learned weights. Scoring is data-driven across the board.'

        return {
            'level': level,
            'message': msg,
            'active_domains': active,
            'mature_domains': mature,
            'total_events': total_events,
        }

    # ─── HELPERS ─────────────────────────────────────────────────────────

    def _safe_float(self, val) -> float:
        try:
            return float(val)
        except (TypeError, ValueError):
            return 0.0


# ─── SINGLETON + CONVENIENCE FUNCTIONS ───────────────────────────────────────

_engine: Optional[NexusLearningEngine] = None

def get_engine() -> NexusLearningEngine:
    global _engine
    if _engine is None:
        _engine = NexusLearningEngine()
    return _engine

def nxlearn(domain: str, entity_id: str, action: str, metadata: Dict = None) -> Dict:
    """Shorthand for logging. Use this from any module: nxlearn('bids', bid_id, 'won', {...})"""
    return get_engine().log(domain, entity_id, action, metadata)

def handle_log(domain: str, entity_id: str, action: str, metadata: Dict = None) -> Dict:
    return get_engine().log(domain, entity_id, action, metadata)

def handle_analyze(domain: str = None) -> Dict:
    return get_engine().analyze(domain)

def handle_get_insights(domain: str = None, limit: int = 15) -> List[Dict]:
    return get_engine().get_insights(domain, limit)

def handle_get_status() -> Dict:
    return get_engine().get_status()

def handle_get_weights(domain: str) -> Dict:
    return get_engine().get_weights(domain)

def handle_get_history(entity_id: str) -> List[Dict]:
    return get_engine().get_entity_history(entity_id)
