#!/usr/bin/env python3
"""
NEXUS OPPORTUNITY HUNTER API
============================
New API endpoints to power the Opportunity Hunter interface.
Connects to existing SAM.gov, USASpending, and Airtable integrations.
"""

from flask import Blueprint, jsonify, request
import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List

# Configure logging
logger = logging.getLogger('OpportunityHunter')

# Create blueprint
opportunity_hunter = Blueprint('opportunity_hunter', __name__)

# DDI Profile (constant)
DDI_PROFILE = {
    'certifications': ['EDWOSB', 'WOSB', 'WBE', 'MBE', 'SBE', 'E-Verify'],
    'naics_codes': [
        # Healthcare, Testing & Compliance
        '621511', '621999', '621910', '541620', '541380',
        # Fingerprinting, Background & Security
        '561611', '561612',
        # Professional & Legal
        '541199', '541990', '561110', '561492', '541930',
        # Management Consulting
        '541611', '541614', '541618', '541690', '541612',
        # Staffing
        '561320', '561311',
        # IT & Technology
        '541512', '541519', '541511', '518210',
        # Transportation, Courier & Logistics
        '485991', '485999', '492110', '492210', '488510', '488190', '484210',
        # Facilities, Construction & Grounds
        '561720', '561730', '561210', '561790', '561990',
        '236220', '238990', '238160', '238330',
        # Events & Security
        '561920', '561621',
        # Medical & Industrial Products
        '423450', '339113', '339112', '424210', '423850',
        '423840', '424120', '424490',
        # Environmental & Emergency
        '562910', '562119', '562112',
        # Document & Records
        '561410',
        # Market Research & Community Health
        '541910', '541720', '624190', '624230', '624221',
    ],
    'services': [
        'Drug Testing/TPA',
        'Fingerprinting / Credentialing',
        'Medical Courier',
        'NEMT',
        'Grounds Maintenance',
        'Janitorial Services',
        'Security Guards',
        'Product Reselling',
        'DNA/Paternity Testing',
        'Notary & Title Services',
        'Construction & Facilities',
        'IT Services',
        'Staffing & Workforce',
        'Management Consulting',
        'Environmental Services',
        'Emergency & Disaster Response',
        'Freight & Logistics Brokerage',
        'AOG Courier (time-critical / aircraft-on-ground — Freight 1st Direct)',
        'Jet Fuel — JETA (brokerage / into-plane; separate from AOG courier)',
        'Jet fuel broker + delivery (single solicitation — when buyer bundles)',
    ],
    'location': 'Michigan',
    'nationwide': True,
    # All searchable set-aside types
    'business_types': [
        {'code': 'EDWOSB', 'label': 'EDWOSB', 'description': 'Economically Disadvantaged Women-Owned', 'ddi_has': True, 'competition_level': 'very_low'},
        {'code': 'WOSB', 'label': 'WOSB', 'description': 'Women-Owned Small Business', 'ddi_has': True, 'competition_level': 'low'},
        {'code': '8A', 'label': '8(a)', 'description': 'SBA 8(a) Business Development', 'ddi_has': False, 'competition_level': 'very_low'},
        {'code': 'HUBZONE', 'label': 'HUBZone', 'description': 'Historically Underutilized Zone', 'ddi_has': False, 'competition_level': 'low'},
        {'code': 'SDVOSB', 'label': 'SDVOSB', 'description': 'Service-Disabled Veteran-Owned', 'ddi_has': False, 'competition_level': 'low'},
        {'code': 'VOSB', 'label': 'VOSB', 'description': 'Veteran-Owned Small Business', 'ddi_has': False, 'competition_level': 'moderate'},
        {'code': 'SDB', 'label': 'SDB', 'description': 'Small Disadvantaged Business', 'ddi_has': False, 'competition_level': 'moderate'},
        {'code': 'SMALL_BUSINESS', 'label': 'Small Business', 'description': 'Small Business Set-Aside', 'ddi_has': True, 'competition_level': 'moderate'},
        {'code': 'NONE', 'label': 'Open Competition', 'description': 'Full & Open / Unrestricted', 'ddi_has': True, 'competition_level': 'high'}
    ],
    # Low hanging fruit criteria
    # NOTE: Low hanging fruit is about COMPETITION LEVEL, not contract size
    # A $5M EDWOSB set-aside can be "low hanging" if very few bidders qualify
    'low_hanging_fruit_criteria': {
        'contract_value_sweet_spot': 100000,  # Sweet spot: $50K-$250K
        'set_aside_score_boost': {
            'EDWOSB': 35,  # Fewest qualified bidders
            '8A': 35,      # Very limited pool
            'WOSB': 25,
            'HUBZONE': 25,
            'SDVOSB': 25,
            'SMALL_BUSINESS': 15,
            'NONE': 0      # Open competition = high competition
        },
        'days_posted_max': 7,  # Recently posted = fewer have seen it
        'days_until_deadline_min': 14,  # Enough time to prepare
        'naics_rarity_boost': 10,  # Niche NAICS codes
        'new_contract_bonus': 20,  # No incumbent = lower competition
        'presolicitation_bonus': 15  # Early engagement advantage
    },
    # Contract size terminology and thresholds
    'contract_size_categories': {
        'micro_purchase': {'max': 10000, 'label': 'Micro-Purchase', 'method': 'Purchase card / No competition', 'past_perf_required': False},
        'simplified_acquisition': {'min': 10000, 'max': 250000, 'label': 'Simplified Acquisition', 'method': 'SAP / Limited competition', 'past_perf_required': False},
        'sat_threshold': {'min': 250000, 'max': 350000, 'label': 'Under SAT (legacy $250K)', 'method': 'No past perf required (legacy)', 'past_perf_required': False},
        'sb_setaside': {'min': 350000, 'max': 500000, 'label': 'Small Business Set-Aside', 'method': 'Restricted competition', 'past_perf_required': True},
        'under_500k': {'min': 0, 'max': 500000, 'label': 'Under $500K', 'method': 'Best for new contractors', 'past_perf_required': None},
        'under_350k': {'min': 0, 'max': 350000, 'label': 'Under $350K (No Past Perf)', 'method': 'Simplified Acquisition Threshold', 'past_perf_required': False},
        'large_setaside': {'min': 500000, 'max': 7000000, 'label': 'Large Set-Aside ($500K-$7M)', 'method': 'EDWOSB sole-source up to $7M / WOSB set-aside', 'past_perf_required': True},
        'large_open': {'min': 500000, 'max': 25000000, 'label': 'Large Contract ($500K-$25M)', 'method': 'Full & open or partial set-aside with diversity scoring', 'past_perf_required': True},
        'major': {'min': 25000000, 'label': 'Major ($25M+)', 'method': 'Full & open — prime or sub strategy required', 'past_perf_required': True},
    },
    # EDWOSB sole-source authority
    'edwosb_sole_source_ceiling': 7000000,
    'edwosb_sole_source_note': 'EDWOSB sole-source contracts up to $7M require NO competition — CO can award directly to DDI',
    # Past performance threshold (as of Oct 1, 2025)
    'past_performance_threshold': 350000,
    'past_performance_note': 'Contracts under $350K (Simplified Acquisition Threshold) do not require past performance evaluations per FAR 42.1502(b)',
    'past_performance_clarification': 'IMPORTANT: EDWOSB set-aside status does NOT exempt from past performance requirements. The $350K threshold applies to ALL contracts regardless of set-aside type.',
    # Large contract bid/no-bid criteria
    'large_contract_criteria': {
        'minimum_margin_pct': 15,
        'minimum_roi_on_bid_prep': 5,
        'require_sub_identified': True,
        'require_bonding_check': True,
        'require_factoring_plan': True,
        'preferred_lanes': [
            'Drug Testing/TPA',
            'Fingerprinting / Credentialing',
            'NEMT',
            'Janitorial Services',
            'Grounds Maintenance',
            'Medical Courier',
            'Staffing & Workforce',
            'DNA/Paternity Testing',
        ],
        'past_performance_strategy': 'Package Gideon Logistics, NEMT brokerage, fingerprinting/credentialing work, and State of Michigan ICA contract as formal past performance references',
    }
}


@opportunity_hunter.route('/api/hunter/profile', methods=['GET'])
def get_hunter_profile():
    """
    Get DDI profile + data freshness indicators + daily target progress
    GET /api/hunter/profile
    """
    # Get data freshness
    data_freshness = get_data_freshness()
    
    # Get daily target progress from ingestion engine
    daily_target = get_daily_target_progress()
    
    return jsonify({
        'success': True,
        'profile': DDI_PROFILE,
        'data_freshness': data_freshness,
        'daily_target': daily_target,
        'search_modes': [
            {'id': 'internal', 'label': 'Internal Database', 'description': 'Search your Airtable opportunities'},
            {'id': 'live', 'label': 'Live Federal Search', 'description': 'Query SAM.gov in real-time'},
            {'id': 'combined', 'label': 'Full Opportunity Hunt', 'description': 'Internal + Live SAM.gov + USASpending'},
            {'id': 'low-hanging', 'label': 'Quick Wins Only', 'description': 'Easy/fast bids: EDWOSB, under $350K, low competition'},
            {'id': 'strategic', 'label': 'Strategic Large Contracts', 'description': 'EDWOSB/WOSB set-asides $500K-$7M + large full & open with diversity scoring'},
        ]
    })


def get_daily_target_progress() -> Dict:
    """Get daily opportunity target progress from ingestion engine stats"""
    try:
        # Try to load from daily_stats.json
        if os.path.exists('daily_stats.json'):
            with open('daily_stats.json', 'r') as f:
                saved = json.load(f)
                today = datetime.now().strftime('%Y-%m-%d')
                if saved.get('date') == today:
                    found = saved.get('new_opportunities_found', 0)
                    target = 3  # DAILY_OPPORTUNITY_TARGET
                    return {
                        'found': found,
                        'target': target,
                        'percentage': min((found / target) * 100, 100),
                        'target_met': found >= target,
                        'remaining': max(target - found, 0),
                        'monthly_projection': int((found / target) * 12) if target > 0 else 0,
                        'urgent': saved.get('urgent_mode', False)
                    }
    except Exception as e:
        logger.error(f"Error loading daily target: {e}")
    
    # Default if can't load
    return {
        'found': 0,
        'target': 3,
        'percentage': 0,
        'target_met': False,
        'remaining': 3,
        'monthly_projection': 0,
        'urgent': False
    }


def get_data_freshness() -> Dict:
    """Check freshness of data sources"""
    freshness = {
        'airtable': {'status': 'unknown', 'last_update': None, 'record_count': 0},
        'sam_gov': {'status': 'unknown', 'last_update': None},
        'usaspending': {'status': 'unknown', 'last_update': None}
    }
    
    # Check Airtable
    try:
        from pyairtable import Api
        api = Api(os.environ.get('AIRTABLE_API_KEY'))
        table = api.table(os.environ.get('AIRTABLE_BASE_ID'), 'GPSS OPPORTUNITIES')
        
        # Get recent records
        recent = table.all(
            formula='DATETIME_DIFF(NOW(), {Posted Date}, "hours") < 24',
            max_records=1
        )
        
        freshness['airtable']['record_count'] = len(table.all(max_records=1))
        
        if recent:
            freshness['airtable']['status'] = 'fresh'
            freshness['airtable']['last_update'] = recent[0]['fields'].get('Posted Date', 'Unknown')
        else:
            freshness['airtable']['status'] = 'stale'
            
    except Exception as e:
        freshness['airtable']['status'] = 'error'
        freshness['airtable']['error'] = str(e)
    
    # Check ingestion log
    try:
        if os.path.exists('nexus_ingestion.log'):
            import subprocess
            result = subprocess.run(
                ['tail', '-n', '50', 'nexus_ingestion.log'],
                capture_output=True,
                text=True
            )
            
            # Parse last SAM.gov update
            for line in reversed(result.stdout.split('\n')):
                if '[SAM.GOV]' in line and 'Found' in line:
                    freshness['sam_gov']['status'] = 'fresh'
                    freshness['sam_gov']['last_update'] = line.split('|')[0].strip()
                    break
                    
            # Parse last USASpending update
            for line in reversed(result.stdout.split('\n')):
                if '[USASPENDING]' in line and 'Processed' in line:
                    freshness['usaspending']['status'] = 'fresh'
                    freshness['usaspending']['last_update'] = line.split('|')[0].strip()
                    break
                    
    except Exception as e:
        pass
    
    return freshness


@opportunity_hunter.route('/api/hunter/agencies', methods=['POST'])
def hunt_agencies():
    """
    Main hunting endpoint - searches and scores agencies
    Queries BOTH internal Airtable data AND live SAM.gov/USASpending APIs
    
    POST /api/hunter/agencies
    
    Body:
    {
        "certifications": ["EDWOSB", "WOSB"],
        "naics_codes": ["621511", "561730"],
        "location": "nationwide",
        "value_range": "all",
        "specific_agency": null,
        "search_live": true  // Set to false to only search internal data
    }
    
    Returns:
    {
        "success": true,
        "agencies": [...],
        "live_results": true,
        "sources": ["airtable", "sam_gov", "usaspending"],
        "business_types_searched": ["EDWOSB", "WOSB", "SMALL_BUSINESS"]
    }
    """
    try:
        data = request.json or {}
        
        # Get search criteria
        certifications = data.get('certifications', DDI_PROFILE['certifications'])
        business_types = data.get('business_types', ['EDWOSB', 'WOSB', 'SMALL_BUSINESS'])
        naics_codes = data.get('naics_codes', DDI_PROFILE['naics_codes'])
        location = data.get('location', 'nationwide')
        value_range = data.get('value_range', 'all')
        specific_agency = data.get('specific_agency')
        search_live = data.get('search_live', True)
        
        logger.info(f"[HUNTER] Starting hunt for {len(business_types)} business types: {business_types}")
        
        # Past performance warning for user
        past_perf_warning = None
        
        agencies_combined = {}
        sources_used = []
        
        # 1. Query INTERNAL Airtable data (for ALL selected business types)
        print("[HUNTER] Querying internal Airtable database...")
        agencies_data = query_agencies_from_airtable(
            certifications=certifications,
            business_types=business_types,
            naics_codes=naics_codes,
            specific_agency=specific_agency
        )
        
        # Add to combined results
        for agency in agencies_data:
            agencies_combined[agency['name']] = {
                'internal_data': agency,
                'opportunities': agency.get('opportunities', []),
                'source': 'internal'
            }
        sources_used.append('airtable')
        
        # 2. Query LIVE SAM.gov API for new opportunities (for ALL selected business types)
        if search_live:
            print(f"[HUNTER] Querying live SAM.gov API for {len(business_types)} business types...")
            sam_opportunities = query_sam_gov_live(
                naics_codes=naics_codes,
                business_types=business_types,
                specific_agency=specific_agency
            )
            
            # Merge SAM.gov results
            for opp in sam_opportunities:
                agency_name = opp.get('agency', 'Unknown')
                if agency_name not in agencies_combined:
                    agencies_combined[agency_name] = {
                        'opportunities': [],
                        'source': 'sam_gov'
                    }
                agencies_combined[agency_name]['opportunities'].append(opp)
                agencies_combined[agency_name]['source'] = 'mixed' if agencies_combined[agency_name].get('internal_data') else 'sam_gov'
            
            sources_used.append('sam_gov')
        
        # 3. Query USASpending for ALL agencies spending in these NAICS
        print("[HUNTER] Querying USASpending for agency spending...")
        spending_data = query_usaspending_by_agency(naics_codes)
        
        # Add agencies that spend in these NAICS but have no active opportunities
        for agency_name, spending in spending_data.items():
            if agency_name not in agencies_combined and spending.get('total_spending', 0) > 10000000:  # $10M+ threshold
                agencies_combined[agency_name] = {
                    'opportunities': [],
                    'source': 'usaspending_only'
                }
        
        sources_used.append('usaspending')
        
        # 4. Build final scorecards
        agencies = build_agency_scorecards_from_combined(
            agencies_combined=agencies_combined,
            spending_data=spending_data,
            criteria={'certifications': certifications, 'naics_codes': naics_codes}
        )
        
        # 5. Sort by match score
        agencies.sort(key=lambda x: x['match_score'], reverse=True)
        
        # Add past performance warning for any opportunity over $350K
        warning = None
        for agency in agencies:
            for opp in agency.get('active_opportunities', []):
                opp_value = opp.get('value', 0)
                if isinstance(opp_value, (int, float)) and opp_value > 350000:
                    warning = "⚠️ Some opportunities over $350K require past performance evaluations (FAR 42.1502). EDWOSB set-aside does NOT exempt from this requirement."
                    break
            if warning:
                break
        
        return jsonify({
            'success': True,
            'agencies': agencies,
            'total_found': len(agencies),
            'live_results': search_live,
            'sources': sources_used,
            'business_types_searched': business_types,
            'past_perf_warning': warning,
            'past_perf_threshold': 350000,
            'past_perf_rule': 'Contracts $350K+ require past performance evaluations per FAR 42.1502 (applies to ALL contracts including EDWOSB set-asides)',
            'search_criteria': {
                'certifications': certifications,
                'business_types': business_types,
                'naics_codes': naics_codes,
                'location': location
            }
        })
        
    except Exception as e:
        import traceback
        print(f"[HUNTER ERROR] {str(e)}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e),
            'agencies': []
        }), 500


@opportunity_hunter.route('/api/hunter/refresh', methods=['POST'])
def force_data_refresh():
    """
    Force immediate data refresh from all sources
    POST /api/hunter/refresh
    
    Triggers the continuous ingestion engine to poll all sources immediately
    """
    try:
        from nexus_continuous_ingestion import DataIngestionEngine
        
        engine = DataIngestionEngine()
        
        # Trigger immediate ingestion
        logger.info("[FORCE REFRESH] Triggering immediate data ingestion...")
        
        # SAM.gov poll
        sam_opps = engine.ingest_sam_gov(hours_back=24)
        engine.sync_to_airtable(sam_opps)
        
        # USASpending sync
        engine.ingest_usaspending_agencies()
        
        return jsonify({
            'success': True,
            'message': 'Data refresh triggered',
            'results': {
                'sam_gov_opportunities': len(sam_opps),
                'new_opportunities': engine.stats['new_opportunities'],
                'high_score_alerts': engine.stats['high_score_alerts']
            }
        })
        
    except Exception as e:
        logger.error(f"[FORCE REFRESH ERROR] {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@opportunity_hunter.route('/api/hunter/agency/<agency_name>/scorecard', methods=['GET'])
def get_agency_scorecard(agency_name):
    """
    Get detailed scorecard for a specific agency
    GET /api/hunter/agency/Veterans%20Health%20Administration/scorecard
    """
    try:
        # 1. Get agency details from Airtable
        opportunities = query_agency_opportunities(agency_name)

        # 2. Get spending data from USASpending
        spending = query_agency_spending(agency_name, DDI_PROFILE['naics_codes'])

        # 3. Get contacts
        contacts = query_agency_contacts(agency_name)

        # 4. Get incumbent data
        incumbents = query_agency_incumbents(agency_name)

        # Build detailed scorecard
        scorecard = {
            'agency_name': agency_name,
            'match_score': calculate_detailed_match_score(agency_name, opportunities, spending),
            'spending_profile': spending,
            'active_opportunities': opportunities,
            'key_contacts': contacts,
            'incumbents': incumbents,
            'why_match': generate_match_reasoning(agency_name, opportunities, spending),
            'recommended_approach': generate_approach_strategy(agency_name, incumbents)
        }

        return jsonify({
            'success': True,
            'scorecard': scorecard
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@opportunity_hunter.route('/api/hunter/low-hanging-fruit', methods=['POST'])
def hunt_low_hanging_fruit():
    """
    Hunt for low competition opportunities - the easy wins
    POST /api/hunter/low-hanging-fruit
    
    Government Contract Size Terminology:
    - Micro-Purchase: Under $10,000 (purchase card, no formal competition)
    - Simplified Acquisition: $10K - $250K (SAP procedures, limited competition)
    - Small Business Set-Aside: $250K - $500K (restricted to small businesses)
    
    IMPORTANT - PAST PERFORMANCE RULES (FAR 42.1502):
    - Contracts UNDER $350,000 (SAT): NO past performance evaluation required
    - Contracts $350,000+: Past performance evaluation IS required
    
    Criteria for low hanging fruit:
    - EDWOSB/8A set-aside (very few qualified bidders)
    - Contract value <$500K (less competition than large contracts)
    - Under $350K = NO past performance required (perfect for new contractors!)
    - Recently posted (< 7 days - fewer have seen it)
    - Sufficient response time (14+ days to prepare)
    - Presolicitation/Sources Sought (early engagement advantage)
    - No incumbent (new contract, not a recompete)
    
    Body:
    {
        "contract_size": "micro",  // "micro" (<$10K), "simplified" (<$250K), "small" (<$500K), "under350k", "any"
        "business_types": ["EDWOSB", "WOSB", "8A"],
        "naics_codes": ["621511", "561730"],
        "days_posted_max": 7,
        "include_presols": true,
        "no_past_perf_required": false  // Set to true to only show opportunities under $350K
    }
    
    Returns:
    {
        "success": true,
        "opportunities": [...],
        "total_found": 15,
        "contract_size_searched": "Simplified Acquisition (<$250K)",
        "past_perf_note": "All opportunities under $350K - NO past performance required",
        "low_hanging_score_avg": 82
    }
    """
    try:
        data = request.json or {}
        
        # Get search criteria with defaults for low hanging fruit
        # Default to 'any' to show ALL contract sizes - user can filter if desired
        contract_size = data.get('contract_size', 'any')  # micro, simplified, small, under350k, any
        no_past_perf_required = data.get('no_past_perf_required', False)
        
        # Map contract size to value thresholds
        size_thresholds = {
            'micro': 10000,
            'simplified': 250000,
            'under350k': 350000,  # Under SAT - NO past performance required!
            'under500k': 500000,
            'small': 500000,
            'mid': 1000000,       # $500K - $1M
            'strategic': 100000000,  # $1M+ (effectively unlimited)
            'any': 100000000      # Any size
        }
        
        # Default to any size unless user specifically filters
        if contract_size == 'any':
            max_value = data.get('max_value', 100000000)  # Effectively unlimited
            logger.info("[LOW HANGING FRUIT] Hunting for ALL contract sizes (strategic + quick wins)")
        elif no_past_perf_required:
            max_value = min(data.get('max_value', 350000), 350000)
            contract_size = 'under350k'
            logger.info("[LOW HANGING FRUIT] Filtering for NO PAST PERFORMANCE REQUIRED (under $350K)")
        else:
            max_value = data.get('max_value', size_thresholds.get(contract_size, 100000000))
        
        business_types = data.get('business_types', ['EDWOSB', 'WOSB', '8A'])
        naics_codes = data.get('naics_codes', DDI_PROFILE['naics_codes'])
        days_posted_max = data.get('days_posted_max', 7)
        include_presols = data.get('include_presols', True)
        
        size_labels = {
            'micro': 'Micro-Purchase (<$10K)',
            'simplified': 'Simplified Acquisition (<$250K)',
            'small': 'Small Business Set-Aside (<$500K)',
            'under350k': 'Under $350K (NO Past Perf Required)',
            'under500k': 'Small Business Set-Asides (<$500K)',
            'mid': 'Mid-Size ($500K - $1M)',
            'strategic': 'Strategic Pursuits ($1M+)',
            'any': 'ALL Contract Sizes'
        }
        
        logger.info(f"[LOW HANGING FRUIT] Hunting for {size_labels.get(contract_size, 'Custom')} opportunities")
        
        # 1. Query internal database
        internal_opps = query_low_hanging_fruit_from_airtable(
            max_value=max_value,
            business_types=business_types,
            naics_codes=naics_codes,
            days_posted_max=days_posted_max
        )
        
        # 2. Query live SAM.gov with strict low-competition filters
        live_opps = query_sam_gov_low_hanging_fruit(
            max_value=max_value,
            business_types=business_types,
            naics_codes=naics_codes,
            days_back=max(days_posted_max, 14),
            include_presols=include_presols
        )
        
        # 3. Combine and score
        all_opps = internal_opps + live_opps
        
        # Calculate low hanging fruit score for each
        scored_opps = []
        for opp in all_opps:
            lh_score, reasons = calculate_low_hanging_fruit_score(opp, max_value)
            opp['low_hanging_score'] = lh_score
            opp['low_hanging_reasons'] = reasons
            opp['is_low_hanging'] = lh_score >= 75
            scored_opps.append(opp)
        
        # Sort by low hanging score
        scored_opps.sort(key=lambda x: x['low_hanging_score'], reverse=True)
        
        # Filter to only high-confidence low hanging fruit
        low_hanging_opps = [o for o in scored_opps if o['is_low_hanging']]
        
        # Determine past performance status
        past_perf_note = None
        if max_value <= 350000:
            past_perf_note = "✅ NO past performance required (under $350K SAT per FAR 42.1502)"
        elif max_value <= 500000:
            past_perf_note = "⚠️ MIXED: Under $350K = no past perf | $350K-$500K = past perf REQUIRED (even for EDWOSB!)"
        else:
            past_perf_note = "⚠️ Past performance evaluations REQUIRED (over $350K) - applies to ALL contracts including EDWOSB set-asides"
        
        return jsonify({
            'success': True,
            'opportunities': low_hanging_opps,
            'total_found': len(low_hanging_opps),
            'all_opportunities_count': len(scored_opps),
            'contract_size_searched': size_labels.get(contract_size, 'Custom'),
            'past_performance_note': past_perf_note,
            'past_perf_threshold': 350000,
            'search_criteria': {
                'contract_size': contract_size,
                'max_value': max_value,
                'no_past_perf_required': no_past_perf_required,
                'business_types': business_types,
                'naics_codes': naics_codes,
                'days_posted_max': days_posted_max
            },
            'avg_low_hanging_score': round(sum(o['low_hanging_score'] for o in low_hanging_opps) / len(low_hanging_opps), 1) if low_hanging_opps else 0
        })
        
    except Exception as e:
        logger.error(f"[LOW HANGING FRUIT ERROR] {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@opportunity_hunter.route('/api/hunter/strategic', methods=['POST'])
def hunt_strategic_contracts():
    """
    Hunt for large, high-value contracts — EDWOSB/WOSB set-asides $500K-$7M,
    large full & open with diversity scoring, IDIQs, BPAs, and multi-year awards.

    POST /api/hunter/strategic
    {
        "min_value": 500000,
        "max_value": 7000000,
        "business_types": ["EDWOSB", "WOSB", "SMALL_BUSINESS", "NONE"],
        "naics_codes": [...],
        "include_idiq": true,
        "include_presols": true
    }
    """
    try:
        data = request.json or {}

        min_value = data.get('min_value', 500000)
        max_value = data.get('max_value', 25000000)
        business_types = data.get('business_types', ['EDWOSB', 'WOSB', 'SMALL_BUSINESS', 'NONE'])
        naics_codes = data.get('naics_codes', DDI_PROFILE['naics_codes'])
        include_presols = data.get('include_presols', True)

        logger.info(f"[STRATEGIC] Hunting large contracts ${min_value:,}-${max_value:,} across {len(business_types)} business types")

        # Query live SAM.gov for ALL business types (including full & open)
        all_opps = query_sam_gov_live(
            naics_codes=naics_codes,
            business_types=business_types,
            days_back=60,
        )

        # Query internal database
        internal_opps = query_low_hanging_fruit_from_airtable(
            max_value=max_value,
            business_types=business_types,
            naics_codes=naics_codes,
            days_posted_max=60,
        )
        all_opps.extend(internal_opps)

        # Score and categorize each opportunity for strategic pursuit
        scored = []
        for opp in all_opps:
            score, reasons, category = _score_strategic_opportunity(opp, min_value)
            if score > 0:
                opp['strategic_score'] = score
                opp['strategic_reasons'] = reasons
                opp['strategic_category'] = category
                scored.append(opp)

        scored.sort(key=lambda x: x['strategic_score'], reverse=True)

        # Categorize results
        sole_source = [o for o in scored if o['strategic_category'] == 'edwosb_sole_source']
        set_aside_large = [o for o in scored if o['strategic_category'] == 'large_set_aside']
        open_with_diversity = [o for o in scored if o['strategic_category'] == 'open_diversity_advantage']
        presol_large = [o for o in scored if o['strategic_category'] == 'presolicitation']

        return jsonify({
            'success': True,
            'opportunities': scored,
            'total_found': len(scored),
            'categories': {
                'edwosb_sole_source': {
                    'count': len(sole_source),
                    'label': 'EDWOSB Sole Source (up to $7M — NO competition)',
                    'opportunities': sole_source[:10],
                },
                'large_set_aside': {
                    'count': len(set_aside_large),
                    'label': 'Large WOSB/SB Set-Asides ($500K+)',
                    'opportunities': set_aside_large[:10],
                },
                'open_diversity_advantage': {
                    'count': len(open_with_diversity),
                    'label': 'Full & Open with Diversity Scoring Advantage',
                    'opportunities': open_with_diversity[:10],
                },
                'presolicitation': {
                    'count': len(presol_large),
                    'label': 'Large Presolicitations (Get on Radar Early)',
                    'opportunities': presol_large[:10],
                },
            },
            'strategy_notes': {
                'edwosb_sole_source': f'EDWOSB sole-source up to ${DDI_PROFILE["edwosb_sole_source_ceiling"]:,} — CO awards directly to DDI, zero competition',
                'past_performance': 'Contracts $350K+ require past performance — package Gideon, NEMT, fingerprinting lanes, State of MI ICA as references',
                'bonding': 'Contracts $500K+ may require performance bond — confirm capacity with SuretyCloud',
                'cash_flow': 'Large contracts have 30-90 day payment cycles — invoice factoring handles the float',
                'sub_strategy': 'DDI primes, subs execute — identify regional partners BEFORE bidding',
            },
            'search_criteria': {
                'min_value': min_value,
                'max_value': max_value,
                'business_types': business_types,
                'naics_count': len(naics_codes),
            }
        })

    except Exception as e:
        logger.error(f"[STRATEGIC ERROR] {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


def _score_strategic_opportunity(opp: Dict, min_value: int) -> tuple:
    """
    Score an opportunity for strategic large-contract pursuit.
    Returns (score, reasons, category).
    """
    score = 0
    reasons = []
    category = 'other'

    set_aside = str(opp.get('set_aside', '')).upper()
    notice_type = opp.get('type', '') or opp.get('notice_type', '')
    value = opp.get('value', 0)

    is_numeric_value = isinstance(value, (int, float)) and value > 0

    # Presolicitations are always interesting for large contracts
    if notice_type in ('Presolicitation', 'Sources Sought', 'Special Notice'):
        score += 30
        reasons.append('Early-stage opportunity — relationship building window')
        category = 'presolicitation'
        if 'EDWOSB' in set_aside:
            score += 25
            reasons.append('EDWOSB presolicitation — get on CO radar before RFP drops')

    # EDWOSB sole-source potential ($7M ceiling, zero competition)
    if 'EDWOSB' in set_aside:
        score += 40
        reasons.append('EDWOSB set-aside — very few qualified bidders')
        if is_numeric_value and value <= DDI_PROFILE['edwosb_sole_source_ceiling']:
            score += 15
            reasons.append(f'Within $7M EDWOSB sole-source ceiling — CO can award directly')
            if category != 'presolicitation':
                category = 'edwosb_sole_source'
        elif is_numeric_value:
            if category != 'presolicitation':
                category = 'large_set_aside'

    # WOSB set-aside
    elif 'WOSB' in set_aside:
        score += 30
        reasons.append('WOSB set-aside — limited competition pool')
        if category != 'presolicitation':
            category = 'large_set_aside'

    # Small business set-aside (DDI qualifies)
    elif 'SB' in set_aside and 'SDVOSB' not in set_aside:
        score += 15
        reasons.append('Small business set-aside — restricted competition')
        if category != 'presolicitation':
            category = 'large_set_aside'

    # Full & open — DDI competes on diversity scoring + best value
    elif set_aside in ('', 'NONE', 'FULL AND OPEN') or not set_aside.strip():
        if is_numeric_value and value >= min_value:
            score += 10
            reasons.append('Full & open — EDWOSB/diversity scoring gives evaluation advantage')
            if category != 'presolicitation':
                category = 'open_diversity_advantage'

    # Value-based scoring
    if is_numeric_value:
        if value >= 1000000:
            score += 20
            reasons.append(f'${value:,.0f} — major contract, high revenue impact')
        elif value >= 500000:
            score += 15
            reasons.append(f'${value:,.0f} — large contract')
        elif value >= 250000:
            score += 10
            reasons.append(f'${value:,.0f} — mid-size contract')

    # DDI NAICS match
    opp_naics = str(opp.get('naics', ''))
    if opp_naics in DDI_PROFILE['naics_codes']:
        score += 10
        reasons.append(f'NAICS {opp_naics} — direct DDI service lane match')

    # Deadline check
    deadline = opp.get('deadline', '') or opp.get('response_deadline', '')
    if deadline and deadline != 'TBD':
        try:
            if isinstance(deadline, str):
                due = datetime.fromisoformat(deadline.replace('Z', '+00:00'))
            else:
                due = deadline
            days_until = (due - datetime.now()).days
            if days_until >= 21:
                score += 5
                reasons.append(f'{days_until} days to prepare — sufficient for complex proposal')
            elif 7 <= days_until < 21:
                score += 2
                reasons.append(f'{days_until} days — tight but feasible with NEXUS speed')
            elif days_until < 7:
                score -= 15
                reasons.append(f'Only {days_until} days — risky for large contract bid prep')
        except (ValueError, TypeError):
            pass

    # Filter out low-value noise
    if is_numeric_value and value < min_value and category != 'presolicitation':
        score = 0

    return max(0, min(100, score)), reasons, category


def query_agencies_from_airtable(certifications: List[str], business_types: List[str] = None, naics_codes: List[str] = None, specific_agency: str = None) -> List[Dict]:
    """Query Airtable for agencies with active opportunities matching business types"""
    try:
        from pyairtable import Api
        
        api = Api(os.environ.get('AIRTABLE_API_KEY'))
        table = api.table(os.environ.get('AIRTABLE_BASE_ID'), 'GPSS OPPORTUNITIES')
        
        # Build filter formula
        filters = ['{Status} = "Active"']
        
        if specific_agency:
            filters.append(f"FIND('{specific_agency}', {{AGENCY NAME}}) > 0")
        
        # Check for set-aside types (now supporting ALL business types)
        business_types = business_types or ['EDWOSB', 'WOSB']
        set_aside_conditions = []
        
        for bt in business_types:
            bt_upper = bt.upper()
            if bt_upper == 'SMALL_BUSINESS':
                # Match multiple small business indicators
                set_aside_conditions.append(f"OR(FIND('SB', {{Set-Aside Type}}) > 0, FIND('Small Business', {{Set-Aside Type}}) > 0)")
            elif bt_upper == 'NONE':
                # Match opportunities with no set-aside
                set_aside_conditions.append("OR({Set-Aside Type} = '', {Set-Aside Type} = 'NONE')")
            else:
                # Match specific set-aside type
                set_aside_conditions.append(f"FIND('{bt}', {{Set-Aside Type}}) > 0")
        
        if set_aside_conditions:
            set_aside_formula = 'OR(' + ', '.join(set_aside_conditions) + ')'
            filters.append(set_aside_formula)
        
        formula = 'AND(' + ', '.join(filters) + ')'
        
        records = table.all(formula=formula)
        
        # Group by agency
        agencies = {}
        for record in records:
            fields = record['fields']
            agency = fields.get('AGENCY NAME', 'Unknown')
            
            if agency not in agencies:
                agencies[agency] = {
                    'name': agency,
                    'opportunities': [],
                    'total_value': 0
                }
            
            agencies[agency]['opportunities'].append({
                'title': fields.get('Name'),
                'solicitation': fields.get('RFP NUMBER'),
                'due_date': fields.get('Deadline'),
                'value': fields.get('VALUE'),
                'set_aside': fields.get('Set-Aside Type'),
                'score': fields.get('Win Probability', 0)
            })
            
            value = fields.get('VALUE', 0) or 0
            if isinstance(value, (int, float)):
                agencies[agency]['total_value'] += value
        
        return list(agencies.values())
        
    except Exception as e:
        print(f"Error querying Airtable: {e}")
        return []


def query_usaspending_by_agency(naics_codes: List[str]) -> Dict:
    """Query USASpending for agency spending by NAICS"""
    try:
        import requests
        
        spending_data = {}
        
        for naics in naics_codes:
            url = "https://api.usaspending.gov/api/v2/search/spending_by_award/"
            
            payload = {
                "filters": {
                    "naics_codes": {"require": [naics]},
                    "award_type_codes": ["A", "B", "C", "D"],
                    "time_period": [{"start_date": "2024-01-01", "end_date": "2024-12-31"}]
                },
                "fields": ["Award ID", "Award Amount", "Recipient Name", "Agency", "Description"],
                "limit": 100
            }
            
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                data = response.json()
                
                # Aggregate by agency
                for result in data.get('results', []):
                    agency = result.get('Agency', 'Unknown')
                    amount = result.get('Award Amount', 0)
                    
                    if agency not in spending_data:
                        spending_data[agency] = {
                            'total_spending': 0,
                            'by_naics': {},
                            'top_contracts': []
                        }
                    
                    spending_data[agency]['total_spending'] += amount
                    
                    if naics not in spending_data[agency]['by_naics']:
                        spending_data[agency]['by_naics'][naics] = 0
                    spending_data[agency]['by_naics'][naics] += amount
        
        return spending_data
        
    except Exception as e:
        print(f"Error querying USASpending: {e}")
        return {}


def query_sam_gov_live(naics_codes: List[str], business_types: List[str] = None, specific_agency: str = None, days_back: int = 30) -> List[Dict]:
    """
    Query live SAM.gov API for active opportunities
    Returns list of opportunity objects from live federal data
    Supports multiple business types (EDWOSB, WOSB, 8A, HUBZone, SDVOSB, etc.)
    """
    try:
        sam_api_key = os.environ.get('SAM_GOV_API_KEY')
        if not sam_api_key:
            print("[HUNTER] SAM_GOV_API_KEY not set - skipping live SAM.gov search")
            return []

        import requests

        opportunities = []
        business_types = business_types or ['EDWOSB', 'WOSB']

        # Calculate date range
        posted_from = (datetime.now() - timedelta(days=days_back)).strftime('%m/%d/%Y')
        posted_to = datetime.now().strftime('%m/%d/%Y')

        print(f"[HUNTER] Querying SAM.gov for {len(naics_codes)} NAICS codes, filtering for {len(business_types)} business types")

        # SAM.gov set-aside code mapping
        set_aside_mapping = {
            'EDWOSB': 'EDWOSB',
            'WOSB': 'WOSB',
            '8A': '8A',
            'HUBZONE': 'HZ',
            'SDVOSB': 'SDVOSB',
            'VOSB': 'VOSB',
            'SDB': 'SDB',
            'SMALL_BUSINESS': 'SB',
            'NONE': 'NONE'
        }

        # Query for each NAICS code
        for naics in naics_codes:
            # First query: Get all opportunities for this NAICS
            try:
                params = {
                    'api_key': sam_api_key,
                    'q': f'"{naics}"',
                    'postedFrom': posted_from,
                    'postedTo': posted_to,
                    'limit': 100,
                    'offset': 0
                }

                response = requests.get(
                    'https://api.sam.gov/prod/opportunities/v1/search',
                    params=params,
                    timeout=30
                )

                if response.status_code == 200:
                    data = response.json()
                    opp_list = data.get('opportunitiesData', [])

                    for opp in opp_list:
                        agency = opp.get('agency', 'Unknown Agency')

                        # Filter by specific agency if requested
                        if specific_agency and specific_agency.lower() not in agency.lower():
                            continue

                        # Get set-aside type and normalize it
                        set_aside = opp.get('setAside', 'None') or 'None'
                        
                        # Check if this opportunity matches ANY of the requested business types
                        # This allows searching multiple set-aside types simultaneously
                        matches_requested = False
                        for bt in business_types:
                            if bt == 'NONE' and (set_aside == 'NONE' or set_aside == '' or not set_aside):
                                matches_requested = True
                                break
                            elif bt in set_aside.upper():
                                matches_requested = True
                                break
                            elif bt == 'SMALL_BUSINESS' and 'SB' in set_aside.upper():
                                matches_requested = True
                                break
                            elif bt == 'SDB' and 'SDB' in set_aside.upper():
                                matches_requested = True
                                break
                        
                        if not matches_requested:
                            continue  # Skip opportunities that don't match selected business types

                        # Map to our format
                        mapped_opp = {
                            'title': opp.get('title', 'Untitled'),
                            'agency': agency,
                            'naics': naics,
                            'notice_id': opp.get('noticeId', ''),
                            'solicitation_number': opp.get('solicitationNumber', ''),
                            'type': opp.get('type', 'Unknown'),
                            'posted_date': opp.get('postedDate', ''),
                            'response_deadline': opp.get('responseDeadLine', ''),
                            'set_aside': set_aside,
                            'value': opp.get('award', {}).get('amount') if opp.get('award') else 'TBD',
                            'source': 'sam_gov_live',
                            'match_score': calculate_live_match_score(opp, naics, business_types)
                        }
                        opportunities.append(mapped_opp)

                elif response.status_code == 403:
                    print("[HUNTER] SAM.gov API access denied - check API key permissions")
                    break
                else:
                    print(f"[HUNTER] SAM.gov API returned {response.status_code}")

            except Exception as e:
                print(f"[HUNTER] Error querying SAM.gov for NAICS {naics}: {e}")
                continue

        print(f"[HUNTER] Found {len(opportunities)} live opportunities matching {business_types}")
        return opportunities

    except Exception as e:
        print(f"[HUNTER] SAM.gov live query failed: {e}")
        return []


def calculate_live_match_score(opp: Dict, naics: str, business_types: List[str]) -> int:
    """
    Calculate match score for live SAM.gov opportunities
    Scores higher for business types that match DDI's certifications
    """
    score = 60  # Base score for live data
    
    # Check if opportunity matches requested business types
    set_aside = str(opp.get('setAside', '')).upper()
    
    # Highest score for EDWOSB (DDI's primary advantage)
    if 'EDWOSB' in set_aside and 'EDWOSB' in business_types:
        score += 30
    # High score for WOSB (DDI's secondary advantage)
    elif 'WOSB' in set_aside and 'WOSB' in business_types:
        score += 25
    # Good score for 8A
    elif '8A' in set_aside and '8A' in business_types:
        score += 20
    # Good score for HUBZone
    elif ('HUBZONE' in set_aside or 'HZ' in set_aside) and 'HUBZONE' in business_types:
        score += 20
    # Good score for SDVOSB
    elif 'SDVOSB' in set_aside and 'SDVOSB' in business_types:
        score += 20
    # Moderate score for general VOSB
    elif 'VOSB' in set_aside and 'VOSB' in business_types:
        score += 15
    # Moderate score for SDB
    elif 'SDB' in set_aside and 'SDB' in business_types:
        score += 15
    # Moderate score for Small Business
    elif ('SB' in set_aside or 'SMALL BUSINESS' in set_aside) and 'SMALL_BUSINESS' in business_types:
        score += 12
    # Base score for open competition (if requested)
    elif 'NONE' in business_types and (set_aside == '' or set_aside == 'NONE'):
        score += 5

    # Boost for recency (if close to deadline)
    deadline = opp.get('responseDeadLine', '')
    if deadline:
        try:
            from datetime import datetime
            deadline_dt = datetime.strptime(deadline[:10], '%Y-%m-%d')
            days_until = (deadline_dt - datetime.now()).days
            if 0 < days_until <= 14:
                score += 5  # Urgent opportunity
        except:
            pass
    
    return min(score, 95)  # Cap at 95 for live data


def build_agency_scorecards_from_combined(agencies_combined: Dict, spending_data: Dict, criteria: Dict) -> List[Dict]:
    """Build scorecards from combined internal + live data"""
    scorecards = []
    
    for agency_name, data in agencies_combined.items():
        spending = spending_data.get(agency_name, {})
        opportunities = data.get('opportunities', [])
        source = data.get('source', 'unknown')
        
        # Calculate match score
        match_score = calculate_match_score_from_combined(opportunities, spending, criteria, source)
        
        # Determine tier
        if match_score >= 85:
            tier = 'excellent'
        elif match_score >= 70:
            tier = 'good'
        elif match_score >= 55:
            tier = 'moderate'
        else:
            tier = 'develop'
        
        # Build why_match reasoning
        why_match = generate_why_match_from_combined(opportunities, spending, criteria, source)
        
        # Get set-aside percentage
        set_aside_pct = estimate_set_aside_percentage(opportunities)
        
        scorecard = {
            'name': agency_name,
            'match_score': match_score,
            'tier': tier,
            'annual_spending': spending.get('by_naics', {}),
            'total_spending': spending.get('total_spending', 0),
            'set_aside_percentage': set_aside_pct,
            'location': 'Nationwide',
            'active_opportunities': opportunities[:5],
            'opportunity_count': len(opportunities),
            'key_contacts': [],
            'why_match': why_match,
            'data_sources': source
        }
        
        scorecards.append(scorecard)
    
    return scorecards


def calculate_match_score_from_combined(opportunities: List[Dict], spending: Dict, criteria: Dict, source: str) -> int:
    """Calculate match score from combined data sources"""
    score = 0
    
    # 1. Has active opportunities (up to 35 points)
    opp_count = len(opportunities)
    score += min(opp_count * 7, 35)
    
    # 2. Spending amount (up to 25 points)
    total_spending = spending.get('total_spending', 0)
    if total_spending > 1000000000:  # $1B+
        score += 25
    elif total_spending > 500000000:  # $500M+
        score += 20
    elif total_spending > 100000000:  # $100M+
        score += 15
    elif total_spending > 50000000:   # $50M+
        score += 10
    else:
        score += 5
    
    # 3. EDWOSB/WOSB set-asides (up to 25 points)
    set_asides = [opp.get('set_aside', '') for opp in opportunities]
    if any('EDWOSB' in str(s) for s in set_asides):
        score += 25
    elif any('WOSB' in str(s) for s in set_asides):
        score += 20
    elif any('SB' in str(s) for s in set_asides):
        score += 15
    
    # 4. Source quality bonus
    if source == 'mixed':
        score += 10  # Both internal and live data
    elif source == 'sam_gov':
        score += 5   # Fresh live data
    
    # 5. High-scoring opportunities
    high_scores = [opp for opp in opportunities if opp.get('match_score', 0) >= 80]
    score += min(len(high_scores) * 3, 10)
    
    return min(score, 100)


def generate_why_match_from_combined(opportunities: List[Dict], spending: Dict, criteria: Dict, source: str) -> List[str]:
    """Generate match reasoning from combined data"""
    reasons = []
    
    opp_count = len(opportunities)
    if opp_count > 0:
        edwosb_count = sum(1 for opp in opportunities if 'EDWOSB' in str(opp.get('set_aside', '')))
        if edwosb_count > 0:
            reasons.append(f"{opp_count} active opportunities ({edwosb_count} EDWOSB set-aside)")
        else:
            reasons.append(f"{opp_count} active opportunities in DDI service lanes")
    
    total_spending = spending.get('total_spending', 0)
    if total_spending > 1000000000:
        reasons.append(f"${total_spending/1e9:.1f}B annual federal spending")
    elif total_spending > 100000000:
        reasons.append(f"${total_spending/1e6:.0f}M annual federal spending")
    
    if source == 'mixed':
        reasons.append("Live SAM.gov + internal tracking data")
    elif source == 'sam_gov':
        reasons.append("Fresh from SAM.gov (not yet in internal database)")
    elif source == 'usaspending_only':
        reasons.append("High spending agency - monitor for opportunities")
    
    # Add recency note if applicable
    live_opps = [opp for opp in opportunities if opp.get('source') == 'sam_gov_live']
    if live_opps:
        recent_count = len([o for o in live_opps if o.get('posted_date', '').startswith('2026')])
        if recent_count > 0:
            reasons.append(f"{recent_count} newly posted opportunities")
    
    return reasons


def build_agency_scorecards(agencies_data: List[Dict], spending_data: Dict, criteria: Dict) -> List[Dict]:
    """Build agency scorecards with match scores (legacy - for backward compatibility)"""
    scorecards = []
    
    for agency in agencies_data:
        agency_name = agency['name']
        spending = spending_data.get(agency_name, {})
        
        match_score = calculate_match_score(agency, spending, criteria)
        
        if match_score >= 85:
            tier = 'excellent'
        elif match_score >= 65:
            tier = 'good'
        else:
            tier = 'moderate'
        
        why_match = generate_why_match(agency, spending, criteria)
        set_aside_pct = estimate_set_aside_percentage(agency['opportunities'])
        
        scorecards.append({
            'name': agency_name,
            'match_score': match_score,
            'tier': tier,
            'annual_spending': spending.get('by_naics', {}),
            'total_spending': spending.get('total_spending', 0),
            'set_aside_percentage': set_aside_pct,
            'location': 'Nationwide',
            'active_opportunities': agency['opportunities'][:5],
            'opportunity_count': len(agency['opportunities']),
            'key_contacts': [],
            'why_match': why_match,
            'data_sources': 'internal'
        })
    
    return scorecards


def calculate_match_score(agency: Dict, spending: Dict, criteria: Dict) -> int:
    """Calculate 0-100 match score for an agency"""
    score = 0
    
    # 1. Has active opportunities (up to 30 points)
    opp_count = len(agency['opportunities'])
    score += min(opp_count * 5, 30)
    
    # 2. Spending amount (up to 25 points)
    total_spending = spending.get('total_spending', 0)
    if total_spending > 1000000000:  # $1B+
        score += 25
    elif total_spending > 500000000:  # $500M+
        score += 20
    elif total_spending > 100000000:  # $100M+
        score += 15
    elif total_spending > 50000000:   # $50M+
        score += 10
    else:
        score += 5
    
    # 3. EDWOSB/WOSB set-asides (up to 25 points)
    set_asides = [opp.get('set_aside', '') for opp in agency['opportunities']]
    if any('EDWOSB' in s for s in set_asides):
        score += 25
    elif any('WOSB' in s for s in set_asides):
        score += 20
    elif any('SB' in s for s in set_asides):
        score += 15
    
    # 4. Opportunity quality (up to 20 points)
    high_scores = [opp for opp in agency['opportunities'] if opp.get('score', 0) >= 75]
    score += min(len(high_scores) * 5, 20)
    
    return min(score, 100)


def generate_why_match(agency: Dict, spending: Dict, criteria: Dict) -> List[str]:
    """Generate reasoning for why this agency is a match"""
    reasons = []
    
    opp_count = len(agency['opportunities'])
    if opp_count > 0:
        reasons.append(f"{opp_count} active opportunities in DDI's service lanes")
    
    total_spending = spending.get('total_spending', 0)
    if total_spending > 1000000000:
        reasons.append(f"${total_spending/1e9:.1f}B annual spending - significant opportunity")
    elif total_spending > 500000000:
        reasons.append(f"${total_spending/1e6:.0f}M annual spending - strong market")
    
    set_asides = [opp.get('set_aside', '') for opp in agency['opportunities']]
    if any('EDWOSB' in s for s in set_asides):
        reasons.append("EDWOSB set-asides - DDI's competitive advantage")
    elif any('WOSB' in s for s in set_asides):
        reasons.append("WOSB set-asides - DDI certification qualifies")
    
    high_score_opps = [opp for opp in agency['opportunities'] if opp.get('score', 0) >= 75]
    if high_score_opps:
        reasons.append(f"{len(high_score_opps)} high-scoring opportunities (75+ AI score)")
    
    return reasons


def estimate_set_aside_percentage(opportunities: List[Dict]) -> int:
    """Estimate set-aside percentage from opportunities"""
    if not opportunities:
        return 25  # Default
    
    set_aside_opps = [opp for opp in opportunities if opp.get('set_aside')]
    return int((len(set_aside_opps) / len(opportunities)) * 100)


def query_low_hanging_fruit_from_airtable(max_value: int, business_types: List[str], naics_codes: List[str], days_posted_max: int) -> List[Dict]:
    """Query Airtable for low competition opportunities"""
    try:
        from pyairtable import Api
        
        api = Api(os.environ.get('AIRTABLE_API_KEY'))
        table = api.table(os.environ.get('AIRTABLE_BASE_ID'), 'GPSS OPPORTUNITIES')
        
        # Build filter for low competition
        filters = [
            '{Status} = "Active"',
            f"{{VALUE}} <= {max_value}"
        ]
        
        # Filter for high-value set-asides
        set_aside_conditions = []
        for bt in business_types:
            if bt == 'SMALL_BUSINESS':
                set_aside_conditions.append(f"OR(FIND('SB', {{Set-Aside Type}}) > 0, FIND('Small Business', {{Set-Aside Type}}) > 0)")
            elif bt != 'NONE':
                set_aside_conditions.append(f"FIND('{bt}', {{Set-Aside Type}}) > 0")
        
        if set_aside_conditions:
            filters.append('OR(' + ', '.join(set_aside_conditions) + ')')
        
        # Posted recently (fresher = fewer bidders have seen it)
        # This would require a Posted Date field comparison
        
        formula = 'AND(' + ', '.join(filters) + ')'
        
        records = table.all(formula=formula, max_records=100)
        
        opportunities = []
        for record in records:
            fields = record['fields']
            
            opp = {
                'title': fields.get('Name', 'Untitled'),
                'solicitation': fields.get('RFP NUMBER', ''),
                'agency': fields.get('AGENCY NAME', 'Unknown'),
                'naics': fields.get('NAICS Code', ''),
                'set_aside': fields.get('Set-Aside Type', 'None'),
                'value': fields.get('VALUE', 0),
                'deadline': fields.get('Deadline', ''),
                'posted_date': fields.get('Posted Date', ''),
                'notice_type': fields.get('Notice Type', 'Solicitation'),
                'source': 'internal',
                'url': fields.get('SAM URL', '')
            }
            opportunities.append(opp)
        
        logger.info(f"[LOW HANGING] Found {len(opportunities)} opportunities from internal DB")
        return opportunities
        
    except Exception as e:
        logger.error(f"[LOW HANGING] Airtable query error: {e}")
        return []


def query_sam_gov_low_hanging_fruit(max_value: int, business_types: List[str], naics_codes: List[str], days_back: int, include_presols: bool) -> List[Dict]:
    """Query SAM.gov specifically for low competition opportunities"""
    # Use the existing query_sam_gov_live but with specific low-hanging filters
    opportunities = query_sam_gov_live(
        naics_codes=naics_codes,
        business_types=business_types,
        specific_agency=None,
        days_back=days_back
    )
    
    # Additional filtering for low value (SAM.gov doesn't always return value, so we do our best)
    filtered = []
    for opp in opportunities:
        # Check if it's a presolicitation (bonus for early engagement)
        if include_presols and opp.get('type') in ['Presolicitation', 'Sources Sought', 'Special Notice']:
            opp['is_presolicitation'] = True
            filtered.append(opp)
        else:
            opp['is_presolicitation'] = False
            
            # Try to filter by value if available
            value = opp.get('value', 'TBD')
            if value != 'TBD' and isinstance(value, (int, float)):
                if value <= max_value:
                    filtered.append(opp)
            else:
                # Include if value unknown (we'll score it based on other factors)
                filtered.append(opp)
    
    logger.info(f"[LOW HANGING] Found {len(filtered)} opportunities from SAM.gov")
    return filtered


def calculate_low_hanging_fruit_score(opp: Dict, max_value: int) -> tuple:
    """
    Calculate low hanging fruit score (0-100)
    Higher = lower competition = easier win
    
    Returns: (score, list_of_reasons)
    """
    score = 50  # Base score
    reasons = []
    
    criteria = DDI_PROFILE['low_hanging_fruit_criteria']
    
    # 1. Set-aside type (highest impact on competition)
    set_aside = str(opp.get('set_aside', '')).upper()
    
    if 'EDWOSB' in set_aside:
        score += criteria['set_aside_score_boost']['EDWOSB']
        reasons.append(f"EDWOSB set-aside (very few qualified bidders)")
    elif '8A' in set_aside:
        score += criteria['set_aside_score_boost']['8A']
        reasons.append(f"8(a) set-aside (very limited pool)")
    elif 'WOSB' in set_aside:
        score += criteria['set_aside_score_boost']['WOSB']
        reasons.append(f"WOSB set-aside (limited competition)")
    elif 'HUBZONE' in set_aside or 'HZ' in set_aside:
        score += criteria['set_aside_score_boost']['HUBZONE']
        reasons.append(f"HUBZone set-aside (limited competition)")
    elif 'SDVOSB' in set_aside:
        score += criteria['set_aside_score_boost']['SDVOSB']
        reasons.append(f"SDVOSB set-aside (limited competition)")
    elif 'SMALL_BUSINESS' in set_aside or 'SB' in set_aside:
        score += criteria['set_aside_score_boost']['SMALL_BUSINESS']
        reasons.append(f"Small business set-aside")
    else:
        # Open competition - still might be low hanging if other factors align
        reasons.append("Open competition (higher competition)")
    
    # 2. Contract value assessment
    value = opp.get('value', 0)
    if isinstance(value, (int, float)) and value > 0:
        if value <= criteria['contract_value_sweet_spot']:
            score += 15
            reasons.append(f"Sweet spot value: ${value:,.0f} (micro contracts have less competition)")
        elif value <= 250000:
            score += 10
            reasons.append(f"Small value: ${value:,.0f}")
        elif value <= 350000:
            score += 12  # Bonus for no past performance required!
            reasons.append(f"Under $350K: NO past performance required (FAR 42.1502) ✓")
        elif value <= 1000000:
            score += 8
            reasons.append(f"Mid-size contract: ${value:,.0f} (growth opportunity)")
        elif value <= 5000000:
            score += 5
            reasons.append(f"Strategic contract: ${value:,.0f} (requires past performance)")
        else:
            score += 3
            reasons.append(f"Major contract: ${value:,.0f} (high stakes, high reward)")
    
    # 3. Recency (recently posted = fewer bidders have seen it)
    posted_date = opp.get('posted_date', '')
    if posted_date:
        try:
            from datetime import datetime
            if isinstance(posted_date, str):
                posted = datetime.fromisoformat(posted_date.replace('Z', '+00:00'))
            else:
                posted = posted_date
            
            days_posted = (datetime.now() - posted).days
            if days_posted <= 1:
                score += 10
                reasons.append("Posted TODAY (early mover advantage!)")
            elif days_posted <= 3:
                score += 8
                reasons.append(f"Posted {days_posted} days ago (fresh)")
            elif days_posted <= 7:
                score += 5
                reasons.append(f"Posted {days_posted} days ago (recent)")
        except:
            pass
    
    # 4. Deadline (sufficient time = better prepared bid)
    deadline = opp.get('deadline', '') or opp.get('response_deadline', '')
    if deadline and deadline != 'TBD':
        try:
            from datetime import datetime
            if isinstance(deadline, str):
                due = datetime.fromisoformat(deadline.replace('Z', '+00:00'))
            else:
                due = deadline
            
            days_until = (due - datetime.now()).days
            if days_until >= 21:
                score += 5
                reasons.append(f"{days_until} days to prepare (ample time)")
            elif 14 <= days_until < 21:
                score += 3
                reasons.append(f"{days_until} days to prepare")
            elif days_until < 7:
                score -= 10  # Penalty for too short
                reasons.append(f"URGENT: Only {days_until} days left!")
        except:
            pass
    
    # 5. Presolicitation/Sources Sought (early engagement)
    notice_type = opp.get('type', '') or opp.get('notice_type', '')
    if notice_type in ['Presolicitation', 'Sources Sought', 'Special Notice']:
        score += criteria['presolicitation_bonus']
        reasons.append("Presolicitation (relationship building opportunity)")
    
    # 6. Source bonus (internal data = higher confidence)
    if opp.get('source') == 'internal':
        score += 5
        reasons.append("In DDI's tracked opportunities (vetted)")
    
    # Cap at 100
    score = min(score, 100)
    
    # Determine tier
    if score >= 85:
        reasons.insert(0, "🎯 EXCELLENT: Very low competition - high win probability")
    elif score >= 70:
        reasons.insert(0, "✅ GOOD: Lower than average competition")
    elif score >= 60:
        reasons.insert(0, "⚠️ MODERATE: Some competition but worth evaluating")
    else:
        reasons.insert(0, "❌ STANDARD: Typical competition level")
    
    return score, reasons


# Placeholder functions for detailed scorecard
def query_agency_opportunities(agency_name: str) -> List[Dict]:
    """Query all opportunities for a specific agency"""
    # Would implement full query
    return []


def query_agency_spending(agency_name: str, naics_codes: List[str]) -> Dict:
    """Query detailed spending for an agency"""
    # Would implement full query
    return {}


def query_agency_contacts(agency_name: str) -> List[Dict]:
    """Query contacts for an agency"""
    # Would query from GPSS CONTACTS
    return []


def query_agency_incumbents(agency_name: str) -> List[Dict]:
    """Query incumbent contractors for an agency"""
    # Would query from USASpending
    return []


def calculate_detailed_match_score(agency_name: str, opportunities: List[Dict], spending: Dict) -> int:
    """Calculate detailed match score for scorecard view"""
    return 85  # Placeholder


def generate_match_reasoning(agency_name: str, opportunities: List[Dict], spending: Dict) -> List[str]:
    """Generate detailed match reasoning"""
    return ["High spending in DDI NAICS codes", "Active EDWOSB set-asides"]


def generate_approach_strategy(agency_name: str, incumbents: List[Dict]) -> str:
    """Generate recommended approach strategy"""
    return "Focus on EDWOSB advantage and competitive pricing"


@opportunity_hunter.route('/api/hunter/add-to-pipeline', methods=['POST'])
def add_to_pipeline():
    """
    Add a NOVA-discovered opportunity directly to GPSS pipeline in Airtable.
    This creates a new opportunity record ready for workflow processing.
    
    POST /api/hunter/add-to-pipeline
    {
        "title": "Contract Title",
        "agency": "Agency Name",
        "solicitation_number": "ABC123",
        "contract_value": 100000,
        "due_date": "2026-03-15",
        "description": "Contract description",
        "set_aside_type": "EDWOSB",
        "naics_codes": ["621511"],
        "url": "https://sam.gov/...",
        "source": "SAM.gov - NOVA Discovery",
        "auto_generate_cap_statement": true
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('title') or not data.get('agency'):
            return jsonify({
                'success': False,
                'error': 'Title and agency are required'
            }), 400
        
        # Import Airtable integration
        try:
            from airtable_integration import airtable_client
        except ImportError:
            return jsonify({
                'success': False,
                'error': 'Airtable integration not available'
            }), 500
        
        # Prepare opportunity record for Airtable GPSS
        opportunity_record = {
            'Name': data['title'],
            'AGENCY': data['agency'],
            'RFP NUMBER': data.get('solicitation_number', 'TBD'),
            'ESTIMATED VALUE': data.get('contract_value', 0),
            'Response Deadline': data.get('due_date'),
            'Description': data.get('description', ''),
            'Set-Aside Type': data.get('set_aside_type', ''),
            'NAICS CODES': ', '.join(data.get('naics_codes', [])) if isinstance(data.get('naics_codes'), list) else data.get('naics_codes', ''),
            'SAM.gov URL': data.get('url', ''),
            'Source': data.get('source', 'NOVA - Federal Search'),
            'Status': 'Pipeline - Needs Review',  # Initial workflow status
            'Date Added': datetime.now().isoformat(),
            'Priority': 'Medium',
            'Pipeline': True,
            'isPipeline': True,
            'internalStatus': 'nova_discovered',
            'discovery_method': 'nova_automated',
            'requires_capability_statement': data.get('auto_generate_cap_statement', True),
            'past_perf_required': data.get('past_perf_required', False),
            'low_hanging_score': data.get('low_hanging_score', 0),
            'match_score': data.get('match_score', 0)
        }
        
        # Create record in Airtable GPSS OPPORTUNITIES table
        try:
            result = airtable_client.create_record('OPPORTUNITIES', opportunity_record)
            record_id = result.get('id', 'unknown')
            
            logger.info(f"✅ NOVA added opportunity to pipeline: {data['title']} (ID: {record_id})")
            
            # Trigger autonomous workflow actions
            autonomous_actions = []
            
            # 1. Queue for capability statement generation if requested
            if data.get('auto_generate_cap_statement'):
                autonomous_actions.append({
                    'action': 'generate_cap_statement',
                    'status': 'queued',
                    'message': 'Capability statement will be auto-generated'
                })
            
            # 2. Check if we have contacts for this agency
            try:
                contacts = airtable_client.get_records('CONTACTS', filter_by_formula=f"{{AGENCY}}='{data['agency']}'")
                if not contacts:
                    autonomous_actions.append({
                        'action': 'find_contacts',
                        'status': 'needed',
                        'message': f'No contacts found for {data["agency"]} - research needed'
                    })
            except:
                pass
            
            # 3. Check for similar past opportunities
            try:
                similar = airtable_client.get_records(
                    'OPPORTUNITIES',
                    filter_by_formula=f"AND({{AGENCY}}='{data['agency']}', {{Status}}='Won')"
                )
                if similar:
                    autonomous_actions.append({
                        'action': 'past_performance_available',
                        'status': 'ready',
                        'message': f'{len(similar)} similar wins with this agency - can reference'
                    })
            except:
                pass
            
            # 4. Check supplier/subcontractor needs based on service type
            service_tags = data.get('service_tags', [])
            if service_tags:
                autonomous_actions.append({
                    'action': 'supplier_search',
                    'status': 'ready',
                    'message': f'Service tags identified: {", ".join(service_tags)} - supplier search available'
                })
            
            # NEXUS PIPELINE: Log discovery event
            try:
                import json as _json
                pipeline_path = os.path.join(os.path.dirname(__file__), 'uploads', 'nexus', 'contracts.json')
                if os.path.exists(pipeline_path):
                    with open(pipeline_path, 'r') as _pf:
                        _pdata = _json.load(_pf)
                    _pdata.setdefault('events', []).append({
                        'id': f"EVT-{datetime.now().strftime('%Y%m%d%H%M%S')}-{len(_pdata.get('events', []))+1:04d}",
                        'type': 'opportunity_added_to_pipeline',
                        'contract_id': '',
                        'source': 'NOVA',
                        'target': 'GPSS',
                        'details': {
                            'title': data['title'],
                            'agency': data['agency'],
                            'gpss_record_id': record_id,
                            'value': data.get('contract_value', 0),
                            'set_aside': data.get('set_aside_type', ''),
                        },
                        'timestamp': datetime.now().isoformat(),
                    })
                    if len(_pdata['events']) > 500:
                        _pdata['events'] = _pdata['events'][-500:]
                    with open(pipeline_path, 'w') as _pf:
                        _json.dump(_pdata, _pf, indent=2, default=str)
            except Exception:
                pass

            return jsonify({
                'success': True,
                'message': f'Opportunity added to GPSS pipeline: {data["title"]}',
                'airtable_id': record_id,
                'next_steps': [
                    'Review opportunity details in GPSS',
                    'Generate capability statement',
                    'Research agency contacts',
                    'Identify suppliers/subcontractors'
                ],
                'autonomous_actions': autonomous_actions,
                'workflow_status': 'Pipeline - Needs Review'
            })
            
        except Exception as airtable_error:
            logger.error(f"❌ Airtable error adding opportunity: {str(airtable_error)}")
            return jsonify({
                'success': False,
                'error': f'Failed to create Airtable record: {str(airtable_error)}'
            }), 500
            
    except Exception as e:
        logger.error(f"❌ Error in add_to_pipeline: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@opportunity_hunter.route('/api/hunter/autonomous-actions', methods=['GET'])
def get_autonomous_actions():
    """
    Get all pending autonomous actions NEXUS recommends for today.
    This is what shows when you first open NEXUS - the "what should I do" view.
    
    GET /api/hunter/autonomous-actions
    """
    try:
        from pyairtable import Api
        api = Api(os.environ.get('AIRTABLE_API_KEY'))
        table = api.table(os.environ.get('AIRTABLE_BASE_ID'), 'GPSS OPPORTUNITIES')
        
        actions = []
        
        # 1. Opportunities that need review (from NOVA or elsewhere)
        try:
            # Get opportunities with Status = 'Pipeline - Needs Review' OR 'Needs Review' OR 'needs_review'
            review_opps = table.all(
                formula="OR({Status}='Pipeline - Needs Review', {Status}='Needs Review', {Status}='needs_review')",
                max_records=5
            )
            for opp in review_opps:
                fields = opp.get('fields', {})
                actions.append({
                    'type': 'review_opportunity',
                    'priority': 'high',
                    'title': fields.get('Name', 'Unnamed Opportunity'),
                    'agency': fields.get('AGENCY', 'Unknown'),
                    'value': fields.get('ESTIMATED VALUE', 0),
                    'deadline': fields.get('Response Deadline'),
                    'airtable_id': opp.get('id'),
                    'action_text': f'Review and approve opportunity from {fields.get("AGENCY", "Unknown")}',
                    'auto_generated': fields.get('discovery_method') == 'nova_automated',
                    'low_hanging_score': fields.get('low_hanging_score', 0)
                })
        except Exception as e:
            logger.warning(f"Could not fetch review opportunities: {e}")
        
        # 2. Opportunities ready for capability statements
        try:
            cap_stat_opps = table.all(
                formula="{requires_capability_statement}=TRUE()",
                max_records=3
            )
            for opp in cap_stat_opps:
                fields = opp.get('fields', {})
                if fields.get('cap_statement_status') != 'generated':
                    actions.append({
                        'type': 'generate_cap_statement',
                        'priority': 'medium',
                        'title': fields.get('Name', 'Unnamed'),
                        'agency': fields.get('AGENCY', 'Unknown'),
                        'airtable_id': opp.get('id'),
                        'action_text': f'Generate capability statement for {fields.get("AGENCY", "Unknown")}',
                        'can_auto': True
                    })
        except Exception as e:
            logger.warning(f"Could not fetch cap statement needs: {e}")
        
        # 3. Daily target check
        daily_target = get_daily_target_progress()
        if not daily_target.get('target_met', False):
            actions.append({
                'type': 'daily_target',
                'priority': 'high' if daily_target.get('urgent_mode') else 'medium',
                'title': 'Find 3 Opportunities Today',
                'progress': f"{daily_target.get('found_today', 0)}/3",
                'action_text': f"Daily target: {daily_target.get('found_today', 0)}/3 opportunities found",
                'cta': 'Open NOVA →',
                'cta_link': '/nova',
                'urgent': daily_target.get('urgent_mode', False)
            })
        
        # 4. NOVA opportunities waiting for decision
        try:
            nova_opps = table.all(
                formula="{discovery_method}='nova_automated'",
                max_records=10
            )
            nova_count = len(nova_opps)
            if nova_count > 0:
                # Count by status - check multiple status formats
                needs_review = sum(1 for o in nova_opps if o.get('fields', {}).get('Status') in ['Pipeline - Needs Review', 'Needs Review', 'needs_review'])
                actions.append({
                    'type': 'nova_summary',
                    'priority': 'info',
                    'title': f'{nova_count} opportunities discovered by NOVA',
                    'needs_review': needs_review,
                    'action_text': f'{needs_review} waiting for your review',
                    'cta': 'Review in GPSS →'
                })
        except Exception as e:
            logger.warning(f"Could not fetch NOVA summary: {e}")
        
        # Sort by priority
        priority_order = {'high': 0, 'medium': 1, 'low': 2, 'info': 3}
        actions.sort(key=lambda x: priority_order.get(x.get('priority', 'low'), 99))
        
        return jsonify({
            'success': True,
            'actions': actions,
            'total_actions': len(actions),
            'high_priority': len([a for a in actions if a.get('priority') == 'high']),
            'timestamp': datetime.now().isoformat(),
            'message': f'NEXUS has {len(actions)} recommended actions for you today'
        })
        
    except Exception as e:
        logger.error(f"❌ Error getting autonomous actions: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'actions': []
        }), 500
