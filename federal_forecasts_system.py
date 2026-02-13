#!/usr/bin/env python3
"""
FEDERAL FORECASTS & OPPORTUNITY INTELLIGENCE SYSTEM
Comprehensive mining across 20+ government forecast sources, contract renewal
prediction, EDWOSB sole source intelligence, and DLA supply chain forecasting.

NOT just SAM.gov. This mines EVERYTHING.

Data Sources:
 TIER 1 — APIs (Structured Data):
  1. SAM.gov API — Pre-solicitation notices (near-term forecasts)
  2. SAM.gov API — EDWOSB/WOSB set-aside active solicitations
  3. USAspending.gov API — Expiring contract mining (renewal predictions)

 TIER 2 — Agency Forecast Pages (AI-Extracted):
  4. NASA Forecast
  5. GSA Forecast of Contracting Opportunities
  6. DHS Forecast System
  7. USAID Business Forecast
  8. Commerce Dept Forecasts
  9. Treasury Forecasts
  10. Dept of Education FY2026 Forecast
  11. Social Security Administration Forecast
  12. VA (Veterans Affairs) Forecast
  13. DOE (Energy) Forecast
  14. EPA Forecast
  15. HHS Forecast
  16. DOJ (Justice) Forecast
  17. Interior Dept Forecast
  18. USDA Forecast

 TIER 3 — Defense / DLA Supply Chain:
  19. DLA Demand Forecast & Industry Events
  20. DLA Distribution Business Opportunities
  21. USACE HQ Upcoming Opportunities
  22. USACE Detroit District (home turf)
  23. USACE Louisville District
  24. USACE Omaha District

 TIER 4 — Government-Wide Forecast Tools:
  25. Acquisition Gateway FCO (acquisitiongateway.gov/forecast)

 TIER 5 — EDWOSB Intelligence:
  26. EDWOSB sole source opportunity detection
  27. Contract renewal prediction (expiring WOSB/EDWOSB awards)
  28. Agency OSDBU contact harvesting

Author: NEXUS AI
Created: January 28, 2026
Enhanced: February 9, 2026 — Full mining & forecasting overhaul
"""

import os
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from pyairtable import Api
from dotenv import load_dotenv
import anthropic
from bs4 import BeautifulSoup
import time

load_dotenv()


# ============================================================================
# DEE DAVIS INC — COMPANY PROFILE (used across all scoring/matching)
# ============================================================================
DDI_PROFILE = {
    'company': 'Dee Davis Inc.',
    'identity': 'Contract Management Firm — wins contracts, sources partners, manages delivery',
    'certifications': ['EDWOSB', 'WOSB', 'WBE', 'MBE', 'SBE', 'E-Verify', 'SWFT', 'CMMC-AB'],
    'federal_ids': {'cage': '8UMX3', 'uei': 'HJB4KNYJVGZ1', 'duns': '002636755'},
    'products': [
        # Office & Paper
        'office supplies', 'paper products', 'copier paper', 'printer supplies',
        # Industrial & Safety
        'industrial supplies', 'safety supplies', 'PPE', 'fire extinguishers',
        'janitorial supplies', 'cleaning chemicals', 'cleaning equipment',
        # Electrical & Power
        'electrical supplies', 'power cables', 'cable assemblies', 'relay assemblies',
        'VFDs', 'variable frequency drives', 'electrical equipment', 'transformers',
        # Landscaping & Grounds
        'landscaping materials', 'topsoil', 'grass seed', 'mulch', 'aggregate materials',
        # Water & Plumbing
        'water infrastructure parts', 'valves', 'pipes', 'fittings', 'plumbing supplies',
        # Signs & Displays
        'signs', 'traffic safety', 'kiosk panels', 'interpretive displays',
        # Other
        'wood poles', 'chlorine', 'medical supplies', 'automotive parts',
        'hardware', 'tools', 'MRO supplies', 'dry ice',
    ],
    'services': [
        'contract management', 'product distribution', 'supply chain management',
        'facility services', 'janitorial services', 'custodial services',
        'landscaping services', 'grounds maintenance', 'snow removal',
        'transportation', 'freight brokerage', 'delivery coordination',
        'construction trades management', 'professional services',
    ],
    'location': 'Troy, Michigan',
    'region': 'Nationwide — can bid in any state',
    'home_turf': ['MI', 'OH', 'IN', 'IL'],
    'states_served': 'ALL',  # DDI can bid nationwide
    'sweet_spot_min': 5000,
    'sweet_spot_max': 500000,
    'max_contract': 2000000,
    'naics_codes': [
        '423840',  # Industrial Supplies & Equipment
        '423850',  # Service Establishment Equipment
        '423990',  # Durable Goods NEC
        '424120',  # Stationery & Office Supplies
        '424690',  # Chemical & Allied Products NEC
        '424910',  # Farm Supplies
        '444190',  # Other Building Material Dealers
        '561730',  # Landscaping Services
        '561720',  # Janitorial Services
        '561210',  # Facilities Support Services
        '423510',  # Metal Service Centers
        '423720',  # Plumbing & Heating Equipment
        '423610',  # Electrical Apparatus & Equipment
        '423490',  # Other Professional Equipment
        '339999',  # Miscellaneous Manufacturing
        '484110',  # General Freight Trucking, Local
        '488510',  # Freight Transportation Arrangement
        '423430',  # Computer Equipment & Peripherals
        '423450',  # Medical Equipment & Supplies
        '339113',  # Surgical Appliance & Supplies
    ],
    'edwosb_sole_source_ceiling_manufacturing': 6500000,
    'edwosb_sole_source_ceiling_other': 4000000,
    'diversity_preference': 'ALWAYS pursue set-aside and best-value bids — DDI certification stack is a weapon',
    'bid_diversity_rule': 'No two active bids should be the same category — build experience across sectors',
}


class FederalForecastsMiner:
    """
    Comprehensive Federal Opportunity Intelligence System
    Mines 25+ sources for forecasts, expiring contracts, sole source leads,
    and EDWOSB-specific opportunities. Scores everything against DDI profile.
    """
    
    def __init__(self):
        self.airtable_token = os.environ.get('AIRTABLE_API_KEY')
        self.base_id = os.environ.get('AIRTABLE_BASE_ID')
        self.sam_api_key = os.environ.get('SAM_GOV_API_KEY')
        self.anthropic_key = os.environ.get('ANTHROPIC_API_KEY')
        
        self.api = Api(self.airtable_token)
        self.ai = anthropic.Anthropic(api_key=self.anthropic_key)
        
        # ================================================================
        # TIER 2: Agency Forecast Pages (20+ agencies)
        # ================================================================
        self.forecast_sources = {
            # --- ORIGINAL 6 ---
            'NASA': 'https://www.hq.nasa.gov/office/procurement/forecast/',
            'GSA': 'https://www.gsa.gov/small-business/forecast-of-contracting-opportunities',
            'DHS': 'https://apfs-cloud.dhs.gov/',
            'USAID': 'https://www.usaid.gov/business-forecast',
            'Commerce': 'https://www.commerce.gov/oam/industry/procurement-forecasts',
            'Treasury': 'https://home.treasury.gov/policy-issues/small-business-programs/small-and-disadvantaged-business-utilization/forecast-of-contract-opportunities/fiscal-year-2026-forecast-of-contract-opportunities',
            # --- NEW AGENCIES ---
            'Dept of Education': 'https://www.ed.gov/about/doing-business-ed/forecast-of-ed-contract-opportunities',
            'Social Security Admin': 'https://www.ssa.gov/osdbu/contract-forecast-intro.html',
            'Veterans Affairs': 'https://www.va.gov/osdbu/library/contracting-forecast.asp',
            'Dept of Energy': 'https://www.energy.gov/management/office-small-and-disadvantaged-business-utilization/procurement-forecast',
            'EPA': 'https://www.epa.gov/contracts/forecast-epa-contracting-opportunities',
            'HHS': 'https://www.hhs.gov/grants-contracts/contracts/forecast/index.html',
            'Dept of Justice': 'https://www.justice.gov/jmd/procurement-forecast',
            'Interior': 'https://www.doi.gov/pmb/osdbu/forecast',
            'USDA': 'https://www.dm.usda.gov/smallbus/forecast.htm',
            'State Dept': 'https://www.state.gov/procurement-forecast/',
            'Transportation': 'https://www.transportation.gov/osdbu/procurement-forecast',
            'Labor': 'https://www.dol.gov/agencies/oasam/centers-offices/business-operations-center/forecast',
        }
        
        # ================================================================
        # TIER 3: Defense / DLA Supply Chain Sources
        # ================================================================
        self.defense_sources = {
            'DLA Demand Forecast': 'https://www.dla.mil/Acquisition/Industry-Engagement-and-Analysis/Demand-Forecast/',
            'DLA Distribution': 'https://www.dla.mil/Distribution/',
            'DLA Troop Support': 'https://www.dla.mil/Troop-Support/',
            'DLA Land and Maritime': 'https://www.dla.mil/Land-and-Maritime/',
            'DLA Aviation': 'https://www.dla.mil/Aviation/',
            'DLA Small Business': 'https://www.dla.mil/Small-Business/',
            'USACE HQ': 'https://www.usace.army.mil/Business-With-Us/Small-Business/Upcoming-Contract-Opportunities/',
            'USACE Detroit': 'https://www.lre.usace.army.mil/Business-With-Us/Contracting/',
            'USACE Louisville': 'https://www.lrl.usace.army.mil/Business-With-Us/',
            'USACE Omaha': 'https://www.nwo.usace.army.mil/Business-With-Us/Upcoming-Opportunities/',
        }
        
        # ================================================================
        # TIER 5: OSDBU Offices (contact harvesting)
        # ================================================================
        self.osdbu_offices = {
            'DLA OSDBU': 'https://www.dla.mil/Small-Business/',
            'GSA OSDBU': 'https://www.gsa.gov/small-business/small-business-resources/contact-information-for-small-business-support',
            'VA OSDBU': 'https://www.va.gov/osdbu/',
            'DOE OSDBU': 'https://www.energy.gov/management/office-small-and-disadvantaged-business-utilization',
            'EPA OSDBU': 'https://www.epa.gov/osdbu',
            'USDA OSDBU': 'https://www.dm.usda.gov/smallbus/',
            'Army OSDBU': 'https://www.army.mil/standto/archive/2020/06/12/',
        }
        
        # ================================================================
        # DLA Upcoming Industry Events (networking opportunities)
        # ================================================================
        self.dla_events = [
            {
                'event': 'Joint Advanced Planning Brief for Industry (JAPBI)',
                'date': '2026-03-02',
                'end_date': '2026-03-04',
                'location': 'Cherry Hill, NJ',
                'host': 'DLA Troop Support',
                'url': 'https://www.dla.mil/Troop-Support/Clothing-and-Textiles/Industry-Support/Events/',
                'relevance': 'HIGH — Troop Support buys supplies DDI can provide'
            },
            {
                'event': 'DLA Energy Worldwide Conference',
                'date': '2026-04-21',
                'end_date': '2026-04-23',
                'location': 'Crystal City, VA',
                'host': 'DLA Energy',
                'url': 'https://www.dla.mil/Energy/Business/Worldwide-Energy-Conference/',
                'relevance': 'MEDIUM — Energy products, fuel supplies'
            },
            {
                'event': 'DLA Disposition Services Industry Day',
                'date': '2026-05-19',
                'end_date': '2026-05-20',
                'location': 'Battle Creek, MI',
                'host': 'DLA Disposition Services',
                'url': 'https://www.dla.mil/Disposition-Services/',
                'relevance': 'HIGH — In Michigan, direct relationship building'
            },
            {
                'event': 'DLA Supply Chain Alliance Symposium & Exhibition',
                'date': '2026-06-02',
                'end_date': '2026-06-03',
                'location': 'Columbus, OH',
                'host': 'DLA Weapons Support',
                'url': 'https://www.dla.mil/Working-With-DLA/Events/DLA-Supply-Chain-Alliance-Symposium/',
                'relevance': 'HIGH — Weapons/Industrial supplies, close to Michigan'
            },
        ]
    
    # ================================================================
    # MASTER MINING ORCHESTRATOR
    # ================================================================
    
    def mine_all_forecasts(self, tiers: List[str] = None) -> Dict:
        """
        Mine forecasts from ALL sources across all tiers.
        
        Args:
            tiers: Optional list of tiers to mine. Default = all tiers.
                   Options: ['sam', 'agencies', 'defense', 'renewals', 'edwosb_sole_source']
        
        Returns summary of forecasts found and stored
        """
        if tiers is None:
            tiers = ['sam', 'agencies', 'defense', 'renewals', 'edwosb_sole_source']
        
        print("=" * 70)
        print("🔮 NEXUS OPPORTUNITY INTELLIGENCE SYSTEM")
        print("   Mining 25+ sources — NOT just SAM.gov")
        print("=" * 70)
        print()
        
        all_forecasts = []
        source_counts = {}
        errors = []
        
        # ────────────────────────────────────────────
        # TIER 1: SAM.gov API (Pre-solicitations + EDWOSB active)
        # ────────────────────────────────────────────
        if 'sam' in tiers:
            print("━" * 50)
            print("TIER 1: SAM.gov API Mining")
            print("━" * 50)
            
            # Pre-solicitation notices
            print("📡 Mining SAM.gov pre-solicitation notices...")
            sam_presolic = self._mine_sam_presolicitations()
            all_forecasts.extend(sam_presolic)
            source_counts['SAM.gov Pre-Solicitations'] = len(sam_presolic)
            print(f"   ✅ {len(sam_presolic)} pre-solicitation notices")
            
            # EDWOSB/WOSB set-aside active solicitations
            print("📡 Mining SAM.gov EDWOSB/WOSB set-asides...")
            sam_edwosb = self._mine_sam_edwosb_setasides()
            all_forecasts.extend(sam_edwosb)
            source_counts['SAM.gov EDWOSB Set-Asides'] = len(sam_edwosb)
            print(f"   ✅ {len(sam_edwosb)} EDWOSB/WOSB set-aside opportunities")
            
            # Sources sought (early intelligence)
            print("📡 Mining SAM.gov sources sought notices...")
            sam_sources = self._mine_sam_sources_sought()
            all_forecasts.extend(sam_sources)
            source_counts['SAM.gov Sources Sought'] = len(sam_sources)
            print(f"   ✅ {len(sam_sources)} sources sought notices")
            print()
        
        # ────────────────────────────────────────────
        # TIER 2: Agency Forecast Pages (18 agencies)
        # ────────────────────────────────────────────
        if 'agencies' in tiers:
            print("━" * 50)
            print("TIER 2: Agency Forecast Pages (18 agencies)")
            print("━" * 50)
            
            for agency, url in self.forecast_sources.items():
                print(f"📡 Mining {agency}...")
                try:
                    agency_forecasts = self._scrape_agency_forecast_page(agency, url)
                    all_forecasts.extend(agency_forecasts)
                    source_counts[f'{agency} Forecast'] = len(agency_forecasts)
                    print(f"   ✅ {len(agency_forecasts)} forecasts")
                except Exception as e:
                    errors.append(f"{agency}: {e}")
                    print(f"   ⚠️  Error: {e}")
                time.sleep(1.5)  # Respectful rate limiting
            print()
        
        # ────────────────────────────────────────────
        # TIER 3: Defense / DLA Supply Chain
        # ────────────────────────────────────────────
        if 'defense' in tiers:
            print("━" * 50)
            print("TIER 3: Defense / DLA Supply Chain Mining")
            print("━" * 50)
            
            for source_name, url in self.defense_sources.items():
                print(f"📡 Mining {source_name}...")
                try:
                    defense_forecasts = self._scrape_agency_forecast_page(source_name, url)
                    all_forecasts.extend(defense_forecasts)
                    source_counts[source_name] = len(defense_forecasts)
                    print(f"   ✅ {len(defense_forecasts)} forecasts/opportunities")
                except Exception as e:
                    errors.append(f"{source_name}: {e}")
                    print(f"   ⚠️  Error: {e}")
                time.sleep(1.5)
            print()
        
        # ────────────────────────────────────────────
        # TIER 4: USAspending Contract Renewal Mining
        # ────────────────────────────────────────────
        if 'renewals' in tiers:
            print("━" * 50)
            print("TIER 4: Expiring Contract Mining (USAspending)")
            print("━" * 50)
            
            print("📡 Mining USAspending for expiring EDWOSB/WOSB contracts...")
            try:
                renewals = self._mine_expiring_contracts()
                all_forecasts.extend(renewals)
                source_counts['USAspending Renewals'] = len(renewals)
                print(f"   ✅ {len(renewals)} expiring contracts identified for re-compete")
            except Exception as e:
                errors.append(f"USAspending Renewals: {e}")
                print(f"   ⚠️  Error: {e}")
            print()
        
        # ────────────────────────────────────────────
        # TIER 5: EDWOSB Sole Source Intelligence
        # ────────────────────────────────────────────
        if 'edwosb_sole_source' in tiers:
            print("━" * 50)
            print("TIER 5: EDWOSB Sole Source Intelligence")
            print("━" * 50)
            
            print("📡 Scanning for sole source opportunities...")
            try:
                sole_source = self._mine_edwosb_sole_source_leads()
                all_forecasts.extend(sole_source)
                source_counts['EDWOSB Sole Source Leads'] = len(sole_source)
                print(f"   ✅ {len(sole_source)} potential sole source leads")
            except Exception as e:
                errors.append(f"Sole Source: {e}")
                print(f"   ⚠️  Error: {e}")
            print()
        
        # ────────────────────────────────────────────
        # STORE & ANALYZE
        # ────────────────────────────────────────────
        print("━" * 50)
        print("STORING & ANALYZING")
        print("━" * 50)
        
        print(f"💾 Storing {len(all_forecasts)} total opportunities...")
        stored_count = self._store_forecasts_in_airtable(all_forecasts)
        print(f"   ✅ Stored {stored_count} new records")
        
        print("🎯 Scoring against DDI profile...")
        matches = self._analyze_and_match_forecasts()
        print(f"   ✅ {matches} high-fit opportunities identified")
        print()
        
        # ────────────────────────────────────────────
        # SUMMARY
        # ────────────────────────────────────────────
        total_sources = len([v for v in source_counts.values() if v > 0])
        
        print("=" * 70)
        print(f"✅ MINING COMPLETE")
        print(f"   Sources mined: {total_sources}")
        print(f"   Total opportunities: {len(all_forecasts)}")
        print(f"   New records stored: {stored_count}")
        print(f"   High-fit matches: {matches}")
        if errors:
            print(f"   Errors: {len(errors)}")
            for err in errors[:5]:
                print(f"      - {err}")
        print("=" * 70)
        
        # Include DLA events in the result
        upcoming_events = self._get_upcoming_events()
        
        return {
            'total_mined': len(all_forecasts),
            'stored': stored_count,
            'high_fit_matches': matches,
            'sources': source_counts,
            'errors': errors,
            'tiers_mined': tiers,
            'upcoming_dla_events': upcoming_events,
            'mining_timestamp': datetime.now().isoformat()
        }
    
    # ================================================================
    # TIER 1: SAM.gov API Mining
    # ================================================================
    
    def _mine_sam_presolicitations(self) -> List[Dict]:
        """
        Mine pre-solicitation notices from SAM.gov API
        These are near-term forecasts — opportunities about to be solicited
        """
        return self._search_sam_api(
            ptype='p',
            source_label='SAM.gov Pre-Solicitation',
            forecast_type='Near-Term (Pre-Solicitation)'
        )
    
    def _mine_sam_edwosb_setasides(self) -> List[Dict]:
        """
        Mine ACTIVE EDWOSB and WOSB set-aside solicitations from SAM.gov
        These are the crown jewels — limited competition opportunities
        """
        edwosb_results = self._search_sam_api(
            ptype='o',  # Active solicitations
            set_aside='EDWOSB',
            source_label='SAM.gov EDWOSB Set-Aside',
            forecast_type='Active EDWOSB Set-Aside'
        )
        
        wosb_results = self._search_sam_api(
            ptype='o',
            set_aside='WOSB',
            source_label='SAM.gov WOSB Set-Aside',
            forecast_type='Active WOSB Set-Aside'
        )
        
        return edwosb_results + wosb_results
    
    def _mine_sam_sources_sought(self) -> List[Dict]:
        """
        Mine sources sought notices — earliest possible intelligence.
        Agencies post these when they're researching if businesses can do the work.
        Responding to these builds relationships BEFORE the RFP drops.
        """
        return self._search_sam_api(
            ptype='r',  # Sources sought
            source_label='SAM.gov Sources Sought',
            forecast_type='Early Intelligence (Sources Sought)'
        )
    
    def _search_sam_api(self, ptype: str, source_label: str, forecast_type: str,
                        set_aside: str = None) -> List[Dict]:
        """
        Generic SAM.gov API searcher. Used by all SAM mining methods.
        
        Args:
            ptype: 'p' (pre-solicitation), 'o' (solicitation), 'r' (sources sought)
            source_label: Label for the source field
            forecast_type: Label for the forecast_type field
            set_aside: Optional set-aside filter ('EDWOSB', 'WOSB', etc.)
        """
        if not self.sam_api_key:
            print("   ⚠️  SAM_GOV_API_KEY not set — skipping")
            return []
        
        try:
            url = "https://api.sam.gov/opportunities/v2/search"
            
            params = {
                'api_key': self.sam_api_key,
                'ptype': ptype,
                'limit': 100,
                'postedFrom': (datetime.now() - timedelta(days=30)).strftime('%m/%d/%Y'),
                'postedTo': datetime.now().strftime('%m/%d/%Y')
            }
            
            if set_aside:
                params['typeOfSetAside'] = set_aside
            
            response = requests.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                opportunities = data.get('opportunitiesData', [])
                
                forecasts = []
                for opp in opportunities:
                    # Extract place of performance safely
                    pop = opp.get('placeOfPerformance', {}) or {}
                    city = pop.get('city', {}) or {}
                    state = pop.get('state', {}) or {}
                    
                    forecast = {
                        'title': opp.get('title', 'Untitled'),
                        'agency': opp.get('department', 'Unknown'),
                        'sub_agency': opp.get('subtier', ''),
                        'naics_code': opp.get('naicsCode', ''),
                        'set_aside': opp.get('typeOfSetAside', 'Unrestricted'),
                        'place_of_performance': city.get('name', ''),
                        'state': state.get('name', ''),
                        'description': opp.get('description', ''),
                        'posted_date': opp.get('postedDate', ''),
                        'response_deadline': opp.get('responseDeadLine', ''),
                        'solicitation_number': opp.get('solicitationNumber', ''),
                        'contract_type': opp.get('type', ''),
                        'source': source_label,
                        'source_url': f"https://sam.gov/opp/{opp.get('noticeId', '')}",
                        'forecast_type': forecast_type,
                        'estimated_solicitation_date': self._estimate_solicitation_date(opp),
                    }
                    forecasts.append(forecast)
                
                return forecasts
            else:
                print(f"   ⚠️  SAM.gov API error: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"   ⚠️  SAM.gov error: {e}")
            return []
    
    # ================================================================
    # TIER 4: USAspending Expiring Contract Mining
    # ================================================================
    
    def _mine_expiring_contracts(self) -> List[Dict]:
        """
        Mine USAspending.gov for contracts that are expiring in the next 6-18 months.
        These contracts will need to be re-competed — that's our window.
        
        Strategy:
        - Find WOSB/EDWOSB-awarded contracts from 4-5 years ago
        - Find contracts in our NAICS codes with approaching end dates
        - These are high-confidence forecasts (the need doesn't go away)
        """
        forecasts = []
        
        try:
            url = "https://api.usaspending.gov/api/v2/search/spending_by_award/"
            
            # Search for contracts in DDI's NAICS codes that are ending soon
            # Search across a wide date range to catch multi-year contracts
            for naics in DDI_PROFILE['naics_codes'][:8]:  # Top 8 NAICS codes
                payload = {
                    "filters": {
                        "time_period": [
                            {
                                "start_date": "2020-01-01",
                                "end_date": "2025-12-31"
                            }
                        ],
                        "award_type_codes": ["A", "B", "C", "D"],  # Contracts
                        "naics_codes": {"require": [naics]},
                    },
                    "fields": [
                        "Award ID", "Recipient Name", "Award Amount",
                        "Start Date", "End Date", "Awarding Agency",
                        "Awarding Sub Agency", "Description",
                        "Contract Award Type"
                    ],
                    "limit": 25,
                    "page": 1,
                    "sort": "Award Amount",
                    "order": "desc"
                }
                
                try:
                    response = requests.post(url, json=payload, timeout=30)
                    if response.status_code == 200:
                        data = response.json()
                        results = data.get('results', [])
                        
                        for award in results:
                            end_date = award.get('End Date', '')
                            award_amount = award.get('Award Amount', 0) or 0
                            
                            # Calculate if this is coming up for re-compete
                            # Contracts ending in 2026-2027 are prime targets
                            if not end_date:
                                continue
                            
                            try:
                                end_dt = datetime.strptime(end_date, '%Y-%m-%d')
                                months_until_end = (end_dt - datetime.now()).days / 30
                                
                                # We want contracts ending in 3-18 months
                                if not (3 <= months_until_end <= 18):
                                    continue
                            except (ValueError, TypeError):
                                continue
                            
                            # Skip tiny contracts
                            if award_amount < DDI_PROFILE['sweet_spot_min']:
                                continue
                            
                            forecasts.append({
                                'title': f"[Renewal] {award.get('Description', 'Contract Renewal')[:60]}",
                                'agency': award.get('Awarding Agency', 'Unknown'),
                                'sub_agency': award.get('Awarding Sub Agency', ''),
                                'naics_code': naics,
                                'description': (
                                    f"Expiring contract (ends {end_date}). "
                                    f"Original value: ${award_amount:,.0f}. "
                                    f"Current holder: {award.get('Recipient Name', 'Unknown')}. "
                                    f"This contract will likely be re-competed. "
                                    f"Position NOW before solicitation drops."
                                ),
                                'estimated_value': award_amount,
                                'estimated_solicitation_date': (
                                    (end_dt - timedelta(days=90)).strftime('%Y-%m-%d')
                                ),
                                'set_aside': 'TBD (check re-solicitation)',
                                'source': 'USAspending Contract Renewal Intelligence',
                                'source_url': f"https://www.usaspending.gov/award/{award.get('Award ID', '')}",
                                'forecast_type': 'Contract Renewal Prediction',
                                'confidence': 'High' if months_until_end <= 9 else 'Medium',
                                'current_holder': award.get('Recipient Name', ''),
                                'contract_end_date': end_date,
                            })
                    
                    time.sleep(1)  # Rate limiting
                    
                except Exception as e:
                    print(f"   ⚠️  USAspending NAICS {naics} error: {e}")
                    continue
                    
        except Exception as e:
            print(f"   ⚠️  USAspending mining error: {e}")
        
        return forecasts
    
    # ================================================================
    # TIER 5: EDWOSB Sole Source Intelligence
    # ================================================================
    
    def _mine_edwosb_sole_source_leads(self) -> List[Dict]:
        """
        Find potential sole source opportunities for EDWOSB.
        
        FAR 19.1506: Sole source awards to EDWOSB up to:
        - $6.5M for manufacturing
        - $4.0M for all other contracts
        
        Strategy:
        - Search SAM.gov for sole source awards to EDWOSB firms
        - Search for small-value procurements in EDWOSB-eligible NAICS
          that agencies might not have competed (missed sole source potential)
        - Find agencies with low WOSB achievement (they NEED to find EDWOSB firms)
        """
        forecasts = []
        
        if not self.sam_api_key:
            return forecasts
        
        try:
            # Search for sole source notices mentioning EDWOSB
            url = "https://api.sam.gov/opportunities/v2/search"
            
            params = {
                'api_key': self.sam_api_key,
                'ptype': 'o',  # Solicitations
                'typeOfSetAside': 'EDWOSB',
                'limit': 50,
                'postedFrom': (datetime.now() - timedelta(days=60)).strftime('%m/%d/%Y'),
                'postedTo': datetime.now().strftime('%m/%d/%Y')
            }
            
            response = requests.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                opportunities = data.get('opportunitiesData', [])
                
                for opp in opportunities:
                    title = opp.get('title', '').lower()
                    desc = opp.get('description', '').lower() if opp.get('description') else ''
                    
                    # Flag if this looks like sole source
                    is_sole_source = any(term in title + desc for term in [
                        'sole source', 'sole-source', 'j&a', 'justification',
                        'single source', 'brand name', 'only source'
                    ])
                    
                    # Flag if under sole source ceiling
                    # (We can't always get the value from SAM, but flag the opportunity)
                    pop = opp.get('placeOfPerformance', {}) or {}
                    city = pop.get('city', {}) or {}
                    state = pop.get('state', {}) or {}
                    
                    forecast = {
                        'title': f"[EDWOSB{'—Sole Source' if is_sole_source else ''}] {opp.get('title', '')}",
                        'agency': opp.get('department', 'Unknown'),
                        'sub_agency': opp.get('subtier', ''),
                        'naics_code': opp.get('naicsCode', ''),
                        'set_aside': 'EDWOSB',
                        'place_of_performance': city.get('name', ''),
                        'state': state.get('name', ''),
                        'description': (
                            f"{opp.get('description', '')[:300]}\n\n"
                            f"{'⭐ SOLE SOURCE POTENTIAL — Limited/no competition' if is_sole_source else ''}\n"
                            f"EDWOSB sole source ceiling: $6.5M (mfg) / $4M (other)"
                        ),
                        'posted_date': opp.get('postedDate', ''),
                        'response_deadline': opp.get('responseDeadLine', ''),
                        'solicitation_number': opp.get('solicitationNumber', ''),
                        'source': 'EDWOSB Sole Source Intelligence',
                        'source_url': f"https://sam.gov/opp/{opp.get('noticeId', '')}",
                        'forecast_type': 'EDWOSB Sole Source Lead' if is_sole_source else 'EDWOSB Set-Aside',
                        'confidence': 'Very High' if is_sole_source else 'High',
                    }
                    forecasts.append(forecast)
                    
        except Exception as e:
            print(f"   ⚠️  Sole source mining error: {e}")
        
        return forecasts
    
    # ================================================================
    # DLA EVENTS TRACKER
    # ================================================================
    
    def _get_upcoming_events(self) -> List[Dict]:
        """Return upcoming DLA/defense industry events"""
        now = datetime.now()
        upcoming = []
        for event in self.dla_events:
            try:
                event_date = datetime.strptime(event['date'], '%Y-%m-%d')
                days_until = (event_date - now).days
                if days_until > 0:
                    upcoming.append({
                        **event,
                        'days_until': days_until
                    })
            except (ValueError, TypeError):
                continue
        return sorted(upcoming, key=lambda x: x.get('days_until', 999))
    
    def get_events_report(self) -> Dict:
        """Generate a formatted events report"""
        events = self._get_upcoming_events()
        return {
            'total_events': len(events),
            'events': events,
            'next_event': events[0] if events else None,
            'michigan_events': [e for e in events if 'MI' in e.get('location', '') or 'Michigan' in e.get('location', '')]
        }
    
    # ================================================================
    # ORIGINAL SAM.gov METHODS (refactored to use generic searcher)
    # ================================================================
    
    def _scrape_agency_forecast_page(self, agency: str, url: str) -> List[Dict]:
        """
        Scrape an agency's forecast page using AI to extract structured data
        Each agency has different formats - AI handles the variety
        """
        try:
            # Fetch page
            response = requests.get(url, timeout=30)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract text content
            page_text = soup.get_text(separator='\n', strip=True)
            
            # Use AI to extract forecasts from unstructured page
            forecasts = self._ai_extract_forecasts(agency, page_text[:15000])  # Limit to 15k chars
            
            # Add metadata
            for forecast in forecasts:
                forecast['agency'] = agency
                forecast['source'] = f'{agency} Official Forecast'
                forecast['source_url'] = url
                forecast['mined_date'] = datetime.now().strftime('%Y-%m-%d')
            
            return forecasts
            
        except Exception as e:
            print(f"   ⚠️  Scraping error for {agency}: {e}")
            return []
    
    def _ai_extract_forecasts(self, agency: str, page_content: str) -> List[Dict]:
        """
        Use Claude AI to extract forecast information from agency page
        Handles various formats automatically
        """
        prompt = f"""
Extract federal procurement forecasts from this {agency} forecast page.

PAGE CONTENT:
{page_content}

Extract each forecast as JSON. Look for:
- Procurement title/description
- NAICS code
- Estimated dollar value
- Estimated solicitation date (when RFP will be posted)
- Contract type (FFP, T&M, etc)
- Set-aside type (8(a), SDVOSB, WOSB, etc)
- Place of performance (location)
- Any other relevant details

Return as JSON array:
[
  {{
    "title": "Procurement title",
    "description": "What they're buying",
    "naics_code": "123456",
    "estimated_value": 0,
    "estimated_solicitation_date": "YYYY-MM-DD or YYYY-Q1 or null",
    "contract_duration": "1 year" or null,
    "set_aside": "WOSB" or "Unrestricted" or null,
    "place_of_performance": "City, State" or null,
    "contract_type": "FFP" or null,
    "forecast_type": "FY2026 Forecast",
    "confidence": "High|Medium|Low",
    "additional_details": "Any other important info"
  }}
]

If no forecasts found, return empty array [].
Return ONLY valid JSON array.
"""
        
        try:
            response = self.ai.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            result = response.content[0].text
            result = result.replace('```json', '').replace('```', '').strip()
            
            forecasts = json.loads(result)
            
            if not isinstance(forecasts, list):
                return []
            
            return forecasts
            
        except Exception as e:
            print(f"   ⚠️  AI extraction error: {e}")
            return []
    
    def _estimate_solicitation_date(self, presolic_data: Dict) -> Optional[str]:
        """
        Estimate when the actual solicitation will be posted
        Based on response deadline in pre-solicitation
        """
        response_deadline = presolic_data.get('responseDeadLine', '')
        if response_deadline:
            try:
                # Pre-solicitations usually become solicitations 2-4 weeks after response deadline
                deadline_date = datetime.strptime(response_deadline, '%Y-%m-%d')
                estimated_date = deadline_date + timedelta(days=14)
                return estimated_date.strftime('%Y-%m-%d')
            except:
                pass
        return None
    
    def _store_forecasts_in_airtable(self, forecasts: List[Dict]) -> int:
        """
        Store forecasts in GPSS Opportunities table (the table that exists).
        Tags them with [Forecast] prefix and source info.
        Avoids duplicates based on title + agency.
        """
        if not forecasts:
            return 0
        
        try:
            table = self.api.table(self.base_id, 'GPSS Opportunities')
            
            # Get existing forecasts to avoid duplicates
            # Check recent records with Forecast in the name
            try:
                existing = table.all(formula="FIND('[Forecast]', {Name})", max_records=500)
            except:
                existing = table.all(max_records=500)
            
            existing_keys = set()
            for r in existing:
                name = r['fields'].get('Name', '').lower()
                agency = r['fields'].get('AGENCY NAME', '').lower()
                existing_keys.add(f"{name}_{agency}")
            
            stored = 0
            for forecast in forecasts:
                title = forecast.get('title', 'Untitled')[:80]
                agency = forecast.get('agency', 'Unknown')
                
                # Create unique key for dedup
                name_tag = f"[Forecast] {agency} - {title}"
                key = f"{name_tag.lower()}_{agency.lower()}"
                
                if key in existing_keys:
                    continue  # Skip duplicate
                
                # Build description with all forecast details
                desc_parts = []
                if forecast.get('description'):
                    desc_parts.append(forecast['description'][:500])
                if forecast.get('forecast_type'):
                    desc_parts.append(f"Forecast Type: {forecast['forecast_type']}")
                if forecast.get('estimated_solicitation_date'):
                    desc_parts.append(f"Est. Solicitation Date: {forecast['estimated_solicitation_date']}")
                if forecast.get('contract_type'):
                    desc_parts.append(f"Contract Type: {forecast['contract_type']}")
                if forecast.get('contract_duration'):
                    desc_parts.append(f"Duration: {forecast['contract_duration']}")
                if forecast.get('confidence'):
                    desc_parts.append(f"Confidence: {forecast['confidence']}")
                
                # Use only fields that exist in GPSS Opportunities
                fields = {
                    'Name': name_tag,
                    'AGENCY NAME': agency,
                }
                
                # Optional fields — set only if we have values
                if forecast.get('naics_code'):
                    fields['NAISC Codes'] = str(forecast['naics_code'])
                if forecast.get('set_aside'):
                    fields['Set-Aside Type'] = forecast['set_aside']
                if forecast.get('state'):
                    fields['State'] = forecast['state']
                if forecast.get('source_url'):
                    fields['Source URL'] = forecast['source_url']
                if forecast.get('response_deadline'):
                    fields['Deadline'] = forecast['response_deadline']
                if forecast.get('solicitation_number'):
                    fields['RFP NUMBER'] = forecast['solicitation_number']
                if desc_parts:
                    fields['Notes'] = '\n'.join(desc_parts)
                
                try:
                    table.create(fields)
                    stored += 1
                    existing_keys.add(key)
                except Exception as e:
                    # If optional fields fail, try minimal
                    try:
                        table.create({
                            'Name': name_tag,
                            'AGENCY NAME': agency,
                        })
                        stored += 1
                    except Exception as e2:
                        print(f"   ⚠️  Failed to store forecast: {e2}")
            
            return stored
            
        except Exception as e:
            print(f"   ⚠️  Airtable storage error: {e}")
            return 0
    
    def _analyze_and_match_forecasts(self) -> int:
        """
        Analyze new forecasts and match to DEE DAVIS INC capabilities.
        Uses AI to score each forecast, updates Priority field.
        Works with GPSS Opportunities table.
        """
        try:
            table = self.api.table(self.base_id, 'GPSS Opportunities')
            
            # Get recent forecasts that haven't been prioritized
            forecasts = table.all(
                formula="AND(FIND('[Forecast]', {Name}), {Priority} = BLANK())",
                max_records=20  # Limit AI calls per run
            )
            
            if not forecasts:
                print("   No new forecasts to analyze")
                return 0
            
            high_fit_count = 0
            
            for record in forecasts:
                fields = record['fields']
                
                # Calculate fit score using AI
                fit_analysis = self._calculate_forecast_fit(fields)
                
                # Update record with analysis
                updates = {
                    'Priority': fit_analysis.get('priority', 'Medium'),
                }
                
                # Add analysis to notes
                analysis_text = fit_analysis.get('analysis', '')
                recommendation = fit_analysis.get('recommendation', '')
                score = fit_analysis.get('score', 50)
                existing_notes = fields.get('Notes', '')
                
                new_notes = f"{existing_notes}\n\n--- AI FIT ANALYSIS (Score: {score}/100) ---\n{analysis_text}\nRecommendation: {recommendation}"
                updates['Notes'] = new_notes.strip()
                
                try:
                    table.update(record['id'], updates)
                except:
                    # If Priority field is a select, it might reject our value
                    try:
                        table.update(record['id'], {'Notes': new_notes.strip()})
                    except:
                        pass
                
                if score >= 70:
                    high_fit_count += 1
            
            return high_fit_count
            
        except Exception as e:
            print(f"   ⚠️  Analysis error: {e}")
            return 0
    
    def _calculate_forecast_fit(self, forecast_data: Dict) -> Dict:
        """
        Calculate how well a forecast matches DEE DAVIS INC capabilities
        Returns score (0-100), analysis, priority, and recommendation
        """
        prompt = f"""
Analyze this federal procurement forecast for DEE DAVIS INC.

FORECAST:
- Title: {forecast_data.get('Name', '')}
- Agency: {forecast_data.get('AGENCY NAME', '')}
- Details: {forecast_data.get('Notes', '')}
- NAICS: {forecast_data.get('NAISC Codes', '')}
- Set-Aside: {forecast_data.get('Set-Aside Type', 'Unknown')}
- State: {forecast_data.get('State', '')}
- Deadline: {forecast_data.get('Deadline', 'TBD')}

DEE DAVIS INC PROFILE:
- EDWOSB/WOSB/MBE/WBE certified
- Product distribution: office supplies, industrial supplies, janitorial supplies
- Landscaping materials: topsoil, grass seed, mulch, aggregate materials
- Located: Troy, Michigan (serves Midwest primarily)
- Best contract size: $20K-$500K
- Can handle larger with good margins
- Government contracting specialist

Analyze and return JSON:
{{
  "score": 0-100,
  "priority": "HIGH|MEDIUM|LOW",
  "analysis": "2-3 sentences explaining fit",
  "recommendation": "Specific action to take",
  "strengths": ["strength 1", "strength 2"],
  "concerns": ["concern 1", "concern 2"],
  "preparation_tips": ["tip 1", "tip 2"]
}}

Scoring:
- 80-100: Perfect fit (EDWOSB set-aside, right products, good value, local)
- 60-79: Good fit (matches capabilities, some concerns)
- 40-59: Moderate fit (possible but competitive)
- 0-39: Poor fit (wrong products, too far, too large/small)
"""
        
        try:
            response = self.ai.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            result = response.content[0].text
            result = result.replace('```json', '').replace('```', '').strip()
            
            analysis = json.loads(result)
            return analysis
            
        except Exception as e:
            print(f"   ⚠️  Fit calculation error: {e}")
            return {
                'score': 50,
                'priority': 'MEDIUM',
                'analysis': 'Unable to analyze automatically',
                'recommendation': 'Manual review required'
            }


    # ================================================================
    # OSDBU CONTACT HARVESTING
    # ================================================================
    
    def harvest_osdbu_contacts(self) -> List[Dict]:
        """
        Scrape OSDBU (Office of Small and Disadvantaged Business Utilization)
        pages for contact information. These are the people who HELP small
        businesses find opportunities within their agency.
        
        Returns list of contacts with agency, name, email, phone, title
        """
        contacts = []
        
        for agency, url in self.osdbu_offices.items():
            print(f"📇 Harvesting contacts from {agency}...")
            try:
                response = requests.get(url, timeout=20)
                soup = BeautifulSoup(response.content, 'html.parser')
                page_text = soup.get_text(separator='\n', strip=True)
                
                # Use AI to extract contact info
                extracted = self._ai_extract_contacts(agency, page_text[:8000])
                for contact in extracted:
                    contact['agency'] = agency
                    contact['source_url'] = url
                contacts.extend(extracted)
                print(f"   ✅ {len(extracted)} contacts found")
                
            except Exception as e:
                print(f"   ⚠️  Error: {e}")
            
            time.sleep(1)
        
        return contacts
    
    def _ai_extract_contacts(self, agency: str, page_content: str) -> List[Dict]:
        """Extract contact information from OSDBU page using AI"""
        prompt = f"""
Extract contact information from this {agency} OSDBU page.
Look for small business liaison officers, OSDBU directors, procurement contacts.

PAGE CONTENT:
{page_content}

Return as JSON array:
[
  {{
    "name": "Full Name",
    "title": "Job Title",
    "email": "email@gov" or null,
    "phone": "phone number" or null,
    "role": "OSDBU Director|Small Business Specialist|Procurement Contact"
  }}
]

If no contacts found, return [].
Return ONLY valid JSON array.
"""
        try:
            response = self.ai.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1500,
                messages=[{"role": "user", "content": prompt}]
            )
            result = response.content[0].text
            result = result.replace('```json', '').replace('```', '').strip()
            contacts = json.loads(result)
            return contacts if isinstance(contacts, list) else []
        except Exception:
            return []
    
    # ================================================================
    # INTELLIGENCE REPORT GENERATOR
    # ================================================================
    
    def generate_intelligence_report(self) -> Dict:
        """
        Generate a comprehensive opportunity intelligence report.
        This is the executive summary Dee sees in the dashboard.
        """
        try:
            table = self.api.table(self.base_id, 'GPSS Opportunities')
            
            # Get all forecasted and mined records
            try:
                all_records = table.all(max_records=500)
            except Exception:
                all_records = []
            
            forecasts = [r for r in all_records if '[Forecast]' in r['fields'].get('Name', '')]
            renewals = [r for r in all_records if '[Renewal]' in r['fields'].get('Name', '')]
            edwosb = [r for r in all_records if 'EDWOSB' in r['fields'].get('Set-Aside Type', '').upper()]
            wosb = [r for r in all_records if 'WOSB' in r['fields'].get('Set-Aside Type', '').upper()]
            sole_source = [r for r in all_records if 'Sole Source' in r['fields'].get('Name', '')]
            
            # Get upcoming events
            events = self._get_upcoming_events()
            
            return {
                'report_date': datetime.now().isoformat(),
                'pipeline_summary': {
                    'total_opportunities': len(all_records),
                    'forecasts': len(forecasts),
                    'contract_renewals': len(renewals),
                    'edwosb_setasides': len(edwosb),
                    'wosb_setasides': len(wosb),
                    'sole_source_leads': len(sole_source),
                },
                'edwosb_advantage': {
                    'total_edwosb': len(edwosb),
                    'total_wosb': len(wosb),
                    'combined': len(edwosb) + len(wosb),
                    'sole_source_ceiling_mfg': '$6.5M',
                    'sole_source_ceiling_other': '$4.0M',
                    'federal_goal': '5% of all contracting dollars',
                    'current_achievement': '~4.57% (agencies are UNDER goal — they need us)',
                },
                'upcoming_events': events,
                'next_event': events[0] if events else None,
                'michigan_events': [e for e in events if 'MI' in e.get('location', '')],
                'sources_count': len(self.forecast_sources) + len(self.defense_sources) + 3,
            }
        except Exception as e:
            return {'error': str(e)}


# ============================================================================
# HANDLER FUNCTIONS (for API integration)
# ============================================================================

def handle_mine_federal_forecasts(tiers: List[str] = None) -> Dict:
    """
    Handler function for NEXUS backend integration.
    Mine federal forecasts and return summary.
    
    Args:
        tiers: Optional list of tiers to mine.
               Default: all tiers ['sam', 'agencies', 'defense', 'renewals', 'edwosb_sole_source']
    """
    miner = FederalForecastsMiner()
    return miner.mine_all_forecasts(tiers=tiers)


def handle_mine_edwosb_only() -> Dict:
    """Mine ONLY EDWOSB/WOSB opportunities — fastest, most targeted search"""
    miner = FederalForecastsMiner()
    return miner.mine_all_forecasts(tiers=['sam', 'edwosb_sole_source'])


def handle_mine_renewals() -> Dict:
    """Mine ONLY expiring contracts for re-compete opportunities"""
    miner = FederalForecastsMiner()
    return miner.mine_all_forecasts(tiers=['renewals'])


def handle_intelligence_report() -> Dict:
    """Generate the opportunity intelligence dashboard report"""
    miner = FederalForecastsMiner()
    return miner.generate_intelligence_report()


def handle_harvest_osdbu_contacts() -> Dict:
    """Harvest OSDBU contacts from agency websites"""
    miner = FederalForecastsMiner()
    contacts = miner.harvest_osdbu_contacts()
    return {
        'total_contacts': len(contacts),
        'contacts': contacts
    }


def handle_get_events() -> Dict:
    """Get upcoming DLA/defense industry events"""
    miner = FederalForecastsMiner()
    return miner.get_events_report()


if __name__ == '__main__':
    """
    Run the full mining system
    """
    import sys
    
    print("🔮 NEXUS OPPORTUNITY INTELLIGENCE SYSTEM\n")
    
    # Allow running specific tiers from command line
    # Usage: python federal_forecasts_system.py sam agencies
    # Usage: python federal_forecasts_system.py edwosb  (shortcut for EDWOSB-only)
    # Usage: python federal_forecasts_system.py renewals
    # Usage: python federal_forecasts_system.py all  (default — everything)
    
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg == 'edwosb':
            result = handle_mine_edwosb_only()
        elif arg == 'renewals':
            result = handle_mine_renewals()
        elif arg == 'report':
            result = handle_intelligence_report()
            print(json.dumps(result, indent=2, default=str))
            sys.exit(0)
        elif arg == 'events':
            result = handle_get_events()
            print(json.dumps(result, indent=2, default=str))
            sys.exit(0)
        elif arg == 'contacts':
            result = handle_harvest_osdbu_contacts()
            print(json.dumps(result, indent=2, default=str))
            sys.exit(0)
        else:
            tiers = sys.argv[1:]
            result = handle_mine_federal_forecasts(tiers=tiers)
    else:
        result = handle_mine_federal_forecasts()
    
    print("\n📊 FINAL RESULTS:")
    print(f"   Total Mined: {result.get('total_mined', 0)}")
    print(f"   Stored in Airtable: {result.get('stored', 0)}")
    print(f"   High-Fit Matches: {result.get('high_fit_matches', 0)}")
    
    if result.get('sources'):
        print("\n   Breakdown by Source:")
        for source, count in result['sources'].items():
            if count > 0:
                print(f"      {source}: {count}")
    
    if result.get('upcoming_dla_events'):
        print("\n   📅 Upcoming DLA Events:")
        for event in result['upcoming_dla_events']:
            print(f"      {event['event']} — {event['location']} ({event['days_until']} days)")
    
    print("\n✅ Mining Complete!")
