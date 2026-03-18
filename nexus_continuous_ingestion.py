#!/usr/bin/env python3
"""
NEXUS CONTINUOUS DATA INGESTION ENGINE
======================================
Automatically mines opportunities from multiple sources 24/7.
Updates Airtable in real-time. Triggers alerts for high-value matches.

Sources:
- SAM.gov API (federal opportunities - every 15 minutes)
- USASpending.gov (agency spending intelligence - daily)
- State procurement portals (Michigan, etc. - daily)
- Local/municipal sites (as configured - weekly)
- Presolicitation notices (SAM.gov special notices - hourly)
"""

import os
import sys
import time
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import schedule

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[
        logging.FileHandler('nexus_ingestion.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('NexusIngestion')


@dataclass
class Opportunity:
    """Standardized opportunity format across all sources"""
    source: str  # 'sam_gov', 'usaspending', 'state_mi', etc.
    notice_id: str
    solicitation_number: str
    title: str
    agency: str
    sub_agency: str
    naics_code: str
    psc_code: str
    notice_type: str  # 'Presolicitation', 'Solicitation', 'Award', etc.
    set_aside: str  # 'EDWOSB', 'WOSB', 'SB', 'None'
    estimated_value: Optional[float]
    posted_date: datetime
    response_deadline: Optional[datetime]
    description: str
    place_of_performance: str
    contact_info: Dict
    url: str
    raw_data: Dict  # Original source data
    
    # Scoring fields (populated by AI)
    ddi_match_score: int = 0
    ddi_tier: str = 'unknown'
    bid_recommendation: str = 'pending'


class DataIngestionEngine:
    """
    Continuous data ingestion engine for NEXUS.
    Runs background jobs to keep Airtable synced with live sources.
    
    CRITICAL BUSINESS RULE: Find 3 NEW opportunities every day minimum
    This ensures DDI can bid on 12+ opportunities per month to hit win targets.
    """
    
    # CRITICAL: Daily opportunity target
    DAILY_OPPORTUNITY_TARGET = 3  # Minimum new opportunities to find per day
    MONTHLY_BID_TARGET = 12  # Derived: 3/day × 4 weeks = 12 bids/month minimum
    
    def __init__(self):
        self.airtable_api_key = os.environ.get('AIRTABLE_API_KEY')
        self.airtable_base_id = os.environ.get('AIRTABLE_BASE_ID')
        self.sam_api_key = os.environ.get('SAM_GOV_API_KEY')
        
        self.last_ingestion = {
            'sam_gov': None,
            'usaspending': None,
            'state_mi': None
        }
        
        # Daily tracking for the 3-opportunity rule
        self.daily_stats = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'new_opportunities_found': 0,
            'target_met': False,
            'urgent_mode': False  # Triggered if we're behind on daily target
        }
        
        self.stats = {
            'total_ingested': 0,
            'duplicates_skipped': 0,
            'new_opportunities': 0,
            'high_score_alerts': 0,
            'daily_targets_met': 0,
            'daily_targets_missed': 0
        }
        
        # Track seen notice IDs to avoid duplicates
        self.seen_notice_ids: Set[str] = self._load_seen_ids()
        
        # Load daily progress
        self._load_daily_stats()
        
    def _load_seen_ids(self) -> Set[str]:
        """Load previously seen notice IDs from tracking file"""
        try:
            if os.path.exists('seen_notice_ids.json'):
                with open('seen_notice_ids.json', 'r') as f:
                    return set(json.load(f))
        except Exception as e:
            logger.error(f"Error loading seen IDs: {e}")
        return set()

    def _save_seen_ids(self):
        """Save seen notice IDs to tracking file"""
        try:
            with open('seen_notice_ids.json', 'w') as f:
                json.dump(list(self.seen_notice_ids), f)
        except Exception as e:
            logger.error(f"Error saving seen IDs: {e}")

    def _load_daily_stats(self):
        """Load daily opportunity finding progress"""
        try:
            if os.path.exists('daily_stats.json'):
                with open('daily_stats.json', 'r') as f:
                    saved = json.load(f)
                    today = datetime.now().strftime('%Y-%m-%d')
                    if saved.get('date') == today:
                        self.daily_stats = saved
                        logger.info(f"[DAILY TARGET] Loaded progress: {self.daily_stats['new_opportunities_found']}/{self.DAILY_OPPORTUNITY_TARGET} opportunities found today")
                    else:
                        # New day - reset stats but track if yesterday hit target
                        if not saved.get('target_met', False):
                            self.stats['daily_targets_missed'] += 1
                            logger.warning(f"[DAILY TARGET] MISSED yesterday's target! Only found {saved.get('new_opportunities_found', 0)}/{self.DAILY_OPPORTUNITY_TARGET}")
                        else:
                            self.stats['daily_targets_met'] += 1
                        self._reset_daily_stats()
        except Exception as e:
            logger.error(f"Error loading daily stats: {e}")
            self._reset_daily_stats()

    def _reset_daily_stats(self):
        """Reset daily stats for new day"""
        self.daily_stats = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'new_opportunities_found': 0,
            'target_met': False,
            'urgent_mode': False
        }
        self._save_daily_stats()
        logger.info(f"[DAILY TARGET] New day started. Target: {self.DAILY_OPPORTUNITY_TARGET} opportunities to enable {self.MONTHLY_BID_TARGET}+ bids/month")

    def _save_daily_stats(self):
        """Save daily progress"""
        try:
            with open('daily_stats.json', 'w') as f:
                json.dump(self.daily_stats, f)
        except Exception as e:
            logger.error(f"Error saving daily stats: {e}")

    def _check_daily_target(self) -> bool:
        """
        Check if daily opportunity target is met.
        Returns True if we need to find more opportunities urgently.
        """
        current_count = self.daily_stats['new_opportunities_found']
        target = self.DAILY_OPPORTUNITY_TARGET
        
        if current_count >= target:
            if not self.daily_stats['target_met']:
                self.daily_stats['target_met'] = True
                self.daily_stats['urgent_mode'] = False
                self._save_daily_stats()
                logger.info(f"🎯 [DAILY TARGET] ACHIEVED! Found {current_count}/{target} opportunities today. On track for {self.MONTHLY_BID_TARGET}+ bids this month.")
            return False  # Target met, no urgency
        
        # Calculate urgency based on time of day
        now = datetime.now()
        hour = now.hour
        
        if hour >= 20 and current_count < target:  # After 8 PM
            self.daily_stats['urgent_mode'] = True
            self._save_daily_stats()
            logger.warning(f"🚨 [DAILY TARGET] URGENT: Only {current_count}/{target} opportunities found and it's {hour}:00! Need {target - current_count} more TODAY to hit monthly bid target.")
            return True  # Urgent - need to find more
        elif current_count < target:
            remaining = target - current_count
            logger.info(f"[DAILY TARGET] Progress: {current_count}/{target} ({remaining} more needed today)")
            return False  # Still have time, not urgent yet
        
        return False

    def _increment_daily_opportunity_count(self, count: int = 1):
        """Track newly found opportunities toward daily target"""
        self.daily_stats['new_opportunities_found'] += count
        self._save_daily_stats()
        
        # Check if we just hit the target
        if self.daily_stats['new_opportunities_found'] >= self.DAILY_OPPORTUNITY_TARGET:
            self._check_daily_target()
    
    def _get_airtable_table(self, table_name: str):
        """Get Airtable table reference"""
        try:
            from pyairtable import Api
            api = Api(self.airtable_api_key)
            return api.table(self.airtable_base_id, table_name)
        except Exception as e:
            logger.error(f"Airtable connection failed: {e}")
            return None
    
    # ==================== SAM.GOV INGESTION ====================
    
    def ingest_sam_gov(self, hours_back: int = 1, expand_search: bool = False) -> List[Opportunity]:
        """
        Ingest latest opportunities from SAM.gov API
        Default: last 1 hour (for 15-minute polling)
        
        Args:
            hours_back: How many hours to look back
            expand_search: If True, search more NAICS codes and go back further (urgent mode)
        """
        if not self.sam_api_key:
            logger.error("SAM_GOV_API_KEY not configured")
            return []

        logger.info(f"[SAM.GOV] Ingesting opportunities from last {hours_back} hours...")
        
        # In expand mode, we're desperate to find opportunities - go back further
        if expand_search:
            hours_back = max(hours_back, 72)  # At least 3 days back
            logger.info(f"[SAM.GOV] URGENT MODE: Expanding search to {hours_back} hours back")

        try:
            import requests

            # DDI's target NAICS codes
            target_naics = [
                '621511',  # Medical laboratories
                '561730',  # Landscaping
                '561611',  # Admin support
                '561612',  # Security guards
                '561720',  # Janitorial
                '561210',  # Facilities support
                '492110',  # Courier
                '492210',  # Local trucking
                '485999',  # Special needs transit
                '423450',  # Medical equipment merchant
                '561990',  # All other support
                '541614',  # Process improvement
                '611430',  # Professional development
            ]
            
            # Calculate date range
            posted_from = (datetime.now() - timedelta(hours=hours_back)).strftime('%m/%d/%Y')
            posted_to = datetime.now().strftime('%m/%d/%Y')
            
            all_opportunities = []
            
            for naics in target_naics:
                try:
                    params = {
                        'api_key': self.sam_api_key,
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
                        
                        for opp_data in data.get('opportunitiesData', []):
                            notice_id = opp_data.get('noticeId', '')
                            
                            # Skip if already seen
                            if notice_id in self.seen_notice_ids:
                                self.stats['duplicates_skipped'] += 1
                                continue
                            
                            # Parse dates
                            posted_date = self._parse_date(opp_data.get('postedDate', ''))
                            deadline = self._parse_date(opp_data.get('responseDeadLine', ''))
                            
                            # Determine set-aside
                            set_aside = opp_data.get('setAside', 'None')
                            if not set_aside or set_aside == 'NONE':
                                set_aside = 'None'
                            
                            opportunity = Opportunity(
                                source='sam_gov',
                                notice_id=notice_id,
                                solicitation_number=opp_data.get('solicitationNumber', ''),
                                title=opp_data.get('title', 'Untitled'),
                                agency=opp_data.get('agency', 'Unknown'),
                                sub_agency=opp_data.get('office', ''),
                                naics_code=naics,
                                psc_code=opp_data.get('classificationCode', ''),
                                notice_type=opp_data.get('type', 'Unknown'),
                                set_aside=set_aside,
                                estimated_value=self._parse_value(opp_data.get('award', {})),
                                posted_date=posted_date or datetime.now(),
                                response_deadline=deadline,
                                description=opp_data.get('description', '')[:500],
                                place_of_performance=opp_data.get('placeOfPerformance', ''),
                                contact_info={
                                    'name': opp_data.get('pointOfContact', [{}])[0].get('fullName', ''),
                                    'email': opp_data.get('pointOfContact', [{}])[0].get('email', ''),
                                    'phone': opp_data.get('pointOfContact', [{}])[0].get('phone', '')
                                },
                                url=f"https://sam.gov/opp/{notice_id}/view",
                                raw_data=opp_data
                            )
                            
                            all_opportunities.append(opportunity)
                            self.seen_notice_ids.add(notice_id)
                            
                    elif response.status_code == 429:
                        logger.warning("[SAM.GOV] Rate limited - backing off")
                        time.sleep(60)
                    else:
                        logger.error(f"[SAM.GOV] API error: {response.status_code}")
                        
                except Exception as e:
                    logger.error(f"[SAM.GOV] Error querying NAICS {naics}: {e}")
                    continue
            
            logger.info(f"[SAM.GOV] Found {len(all_opportunities)} new opportunities")
            return all_opportunities
            
        except Exception as e:
            logger.error(f"[SAM.GOV] Ingestion failed: {e}")
            return []
    
    def ingest_sam_gov_presolicitations(self, days_back: int = 7) -> List[Opportunity]:
        """
        Specifically hunt for presolicitations and RFIs
        These are GOLD for relationship building
        """
        logger.info(f"[SAM.GOV] Hunting presolicitations from last {days_back} days...")
        
        # Same implementation but filtering for special notices/presols
        # This would query with specific filters
        return []
    
    # ==================== USASPENDING INGESTION ====================
    
    def ingest_usaspending_agencies(self) -> Dict:
        """
        Ingest agency spending intelligence from USASpending
        Run daily to identify high-spending agencies in DDI's lanes
        """
        logger.info("[USASPENDING] Ingesting agency spending intelligence...")
        
        try:
            import requests
            
            target_naics = ['621511', '561730', '561611', '561612', '561720', '492110']
            agency_spending = {}
            
            for naics in target_naics:
                url = "https://api.usaspending.gov/api/v2/search/spending_by_award/"
                
                payload = {
                    "filters": {
                        "naics_codes": {"require": [naics]},
                        "award_type_codes": ["A", "B", "C", "D"],
                        "time_period": [
                            {"start_date": "2024-01-01", "end_date": "2024-12-31"}
                        ]
                    },
                    "fields": ["Award ID", "Award Amount", "Recipient Name", "Agency"],
                    "limit": 500
                }
                
                response = requests.post(url, json=payload, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    for result in data.get('results', []):
                        agency = result.get('Agency', 'Unknown')
                        amount = result.get('Award Amount', 0) or 0
                        
                        if agency not in agency_spending:
                            agency_spending[agency] = {
                                'total_spending': 0,
                                'by_naics': {},
                                'top_contractors': []
                            }
                        
                        agency_spending[agency]['total_spending'] += amount
                        
                        if naics not in agency_spending[agency]['by_naics']:
                            agency_spending[agency]['by_naics'][naics] = 0
                        agency_spending[agency]['by_naics'][naics] += amount
            
            # Store in Airtable AGENCY INTELLIGENCE table
            self._update_agency_intelligence(agency_spending)
            
            logger.info(f"[USASPENDING] Processed {len(agency_spending)} agencies")
            return agency_spending
            
        except Exception as e:
            logger.error(f"[USASPENDING] Ingestion failed: {e}")
            return {}
    
    def ingest_usaspending_incumbents(self, agency_name: str) -> List[Dict]:
        """
        Ingest incumbent contractor data for a specific agency
        Critical for competitive intelligence
        """
        logger.info(f"[USASPENDING] Researching incumbents for {agency_name}...")
        
        try:
            import requests
            
            url = "https://api.usaspending.gov/api/v2/search/spending_by_award/"
            
            payload = {
                "filters": {
                    "agencies": [{"type": "awarding", "tier": "toptier", "name": agency_name}],
                    "award_type_codes": ["A", "B", "C", "D"],
                    "time_period": [
                        {"start_date": "2022-01-01", "end_date": "2025-12-31"}
                    ]
                },
                "fields": ["Award ID", "Award Amount", "Recipient Name", "Description", "Start Date", "End Date"],
                "limit": 100
            }
            
            response = requests.post(url, json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                incumbents = []
                
                for result in data.get('results', []):
                    incumbents.append({
                        'contractor': result.get('Recipient Name', 'Unknown'),
                        'award_id': result.get('Award ID', ''),
                        'amount': result.get('Award Amount', 0),
                        'description': result.get('Description', ''),
                        'period': f"{result.get('Start Date', '')} to {result.get('End Date', '')}"
                    })
                
                return incumbents
                
        except Exception as e:
            logger.error(f"[USASPENDING] Incumbent search failed: {e}")
        
        return []
    
    # ==================== STATE/LOCAL INGESTION ====================
    
    def ingest_michigan_procurement(self) -> List[Opportunity]:
        """
        Ingest from Michigan's DTMB procurement portal
        """
        logger.info("[STATE/MI] Ingesting Michigan procurement opportunities...")
        
        # This would use web scraping or DTMB API
        # Placeholder for implementation
        return []
    
    # ==================== AI SCORING ====================
    
    def score_opportunity(self, opp: Opportunity) -> Opportunity:
        """
        Score an opportunity using DDI's criteria
        """
        score = 0
        reasons = []
        
        # EDWOSB set-aside (highest value)
        if opp.set_aside == 'EDWOSB':
            score += 35
            reasons.append("EDWOSB set-aside - perfect match")
        elif opp.set_aside == 'WOSB':
            score += 30
            reasons.append("WOSB set-aside - excellent match")
        elif opp.set_aside == 'SB':
            score += 20
            reasons.append("Small business set-aside")
        
        # NAICS match
        if opp.naics_code in ['621511', '561611', '561730']:
            score += 15
            reasons.append("Core DDI service lane")
        elif opp.naics_code in ['561612', '561720', '492110']:
            score += 10
            reasons.append("Secondary service lane")
        
        # Value range
        if opp.estimated_value:
            if opp.estimated_value > 5000000:
                score += 15
                reasons.append("High-value opportunity")
            elif opp.estimated_value > 1000000:
                score += 10
                reasons.append("Mid-value opportunity")
        
        # Recency (newly posted)
        days_since_posted = (datetime.now() - opp.posted_date).days
        if days_since_posted <= 1:
            score += 10
            reasons.append("Freshly posted - early mover advantage")
        
        # Deadline urgency
        if opp.response_deadline:
            days_until = (opp.response_deadline - datetime.now()).days
            if 7 < days_until <= 14:
                score += 5
                reasons.append("Approaching deadline - act soon")
        
        opp.ddi_match_score = min(score, 100)
        
        # Determine tier
        if opp.ddi_match_score >= 85:
            opp.ddi_tier = 'excellent'
            opp.bid_recommendation = 'BID_NOW'
        elif opp.ddi_match_score >= 70:
            opp.ddi_tier = 'good'
            opp.bid_recommendation = 'STRONG_CONSIDER'
        elif opp.ddi_match_score >= 55:
            opp.ddi_tier = 'moderate'
            opp.bid_recommendation = 'EVALUATE'
        else:
            opp.ddi_tier = 'develop'
            opp.bid_recommendation = 'MONITOR'
        
        return opp
    
    # ==================== AIRTABLE SYNC ====================
    
    def sync_to_airtable(self, opportunities: List[Opportunity]):
        """
        Sync scored opportunities to Airtable GPSS OPPORTUNITIES table
        """
        logger.info(f"[AIRTABLE] Syncing {len(opportunities)} opportunities...")
        
        table = self._get_airtable_table('GPSS OPPORTUNITIES')
        if not table:
            logger.error("[AIRTABLE] Cannot connect - skipping sync")
            return
        
        for opp in opportunities:
            try:
                # Score before syncing
                scored_opp = self.score_opportunity(opp)
                
                # Check if already exists
                existing = table.all(formula=f"{{RFP NUMBER}} = '{opp.solicitation_number}'")
                
                record_data = {
                    'Name': scored_opp.title,
                    'AGENCY NAME': scored_opp.agency,
                    'RFP NUMBER': scored_opp.solicitation_number,
                    'NAICS Code': scored_opp.naics_code,
                    'Notice Type': scored_opp.notice_type,
                    'Set-Aside Type': scored_opp.set_aside,
                    'VALUE': scored_opp.estimated_value,
                    'Deadline': scored_opp.response_deadline.isoformat() if scored_opp.response_deadline else None,
                    'Posted Date': scored_opp.posted_date.isoformat(),
                    'Status': 'New' if not existing else 'Updated',
                    'NEXUS Score': scored_opp.ddi_match_score,
                    'Bid Recommendation': scored_opp.bid_recommendation,
                    'Data Source': scored_opp.source,
                    'SAM URL': scored_opp.url,
                    'Description': scored_opp.description,
                    'Contact Name': scored_opp.contact_info.get('name', ''),
                    'Contact Email': scored_opp.contact_info.get('email', ''),
                    'Place of Performance': scored_opp.place_of_performance
                }
                
                if existing:
                    # Update existing
                    table.update(existing[0]['id'], record_data)
                    logger.debug(f"[AIRTABLE] Updated {opp.solicitation_number}")
                else:
                    # Create new
                    table.create(record_data)
                    self.stats['new_opportunities'] += 1
                    logger.info(f"[AIRTABLE] Created new: {opp.title[:50]}...")
                    
                    # Trigger alert if high score
                    if scored_opp.ddi_match_score >= 85:
                        self._trigger_high_score_alert(scored_opp)
                        
            except Exception as e:
                logger.error(f"[AIRTABLE] Sync error for {opp.notice_id}: {e}")
        
        self.stats['total_ingested'] += len(opportunities)
    
    def _update_agency_intelligence(self, agency_spending: Dict):
        """Update AGENCY INTELLIGENCE table with spending data"""
        table = self._get_airtable_table('GPSS - AGENCY INTELLIGENCE')
        if not table:
            return
        
        for agency, data in agency_spending.items():
            try:
                existing = table.all(formula=f"{{Agency Name}} = '{agency}'")
                
                record = {
                    'Agency Name': agency,
                    'Total Annual Spending': data['total_spending'],
                    'Spending by NAICS': json.dumps(data['by_naics']),
                    'Last Updated': datetime.now().isoformat()
                }
                
                if existing:
                    table.update(existing[0]['id'], record)
                else:
                    table.create(record)
                    
            except Exception as e:
                logger.error(f"[AIRTABLE] Agency update error: {e}")
    
    def _trigger_high_score_alert(self, opp: Opportunity):
        """Trigger alert for high-scoring opportunity"""
        self.stats['high_score_alerts'] += 1
        logger.info(f"🚨 HIGH SCORE ALERT: {opp.title} ({opp.ddi_match_score}/100)")
        
        # This could:
        # - Send email to Dee
        # - Post to Slack/Teams
        # - Create calendar reminder
        # - Auto-generate capability statement
        
        alert_data = {
            'alert_type': 'HIGH_SCORE_OPPORTUNITY',
            'timestamp': datetime.now().isoformat(),
            'opportunity': {
                'title': opp.title,
                'agency': opp.agency,
                'solicitation': opp.solicitation_number,
                'score': opp.ddi_match_score,
                'value': opp.estimated_value,
                'deadline': opp.response_deadline.isoformat() if opp.response_deadline else None,
                'url': opp.url
            }
        }
        
        # Save alert for retrieval
        with open('high_score_alerts.jsonl', 'a') as f:
            f.write(json.dumps(alert_data) + '\n')
    
    # ==================== SCHEDULED JOBS ====================
    
    def job_sam_gov_poll(self):
        """Poll SAM.gov every 15 minutes - TRACKS toward daily 3-opportunity target"""
        logger.info("[JOB] Starting SAM.gov poll...")
        
        # Check daily target status first
        urgent = self._check_daily_target()
        if urgent:
            logger.warning("🚨 [URGENT MODE] Behind on daily target - expanding search parameters!")
            # In urgent mode, search back further to find more opportunities
            opportunities = self.ingest_sam_gov(hours_back=24, expand_search=True)
        else:
            opportunities = self.ingest_sam_gov(hours_back=1)
        
        if opportunities:
            new_count = len([o for o in opportunities if o.notice_id not in self.seen_notice_ids])
            self.sync_to_airtable(opportunities)
            self._save_seen_ids()
            
            # Track toward daily target
            if new_count > 0:
                self._increment_daily_opportunity_count(new_count)
                logger.info(f"🎯 [DAILY TARGET] +{new_count} opportunities found today (Total: {self.daily_stats['new_opportunities_found']}/{self.DAILY_OPPORTUNITY_TARGET})")
        
        self.last_ingestion['sam_gov'] = datetime.now()

    def job_usaspending_daily(self):
        """Daily USASpending ingestion"""
        logger.info("[JOB] Starting USASpending daily sync...")
        self.ingest_usaspending_agencies()
        self.last_ingestion['usaspending'] = datetime.now()

    def job_presolicitation_hunt(self):
        """Hunt for presolicitations hourly - These count toward daily target!"""
        logger.info("[JOB] Hunting presolicitations...")
        presols = self.ingest_sam_gov_presolicitations(days_back=1)
        if presols:
            new_count = len([o for o in presols if o.notice_id not in self.seen_notice_ids])
            # Presols get extra attention - auto-generate emails
            logger.info(f"[JOB] Found {len(presols)} presolicitations - auto-processing...")
            self.sync_to_airtable(presols)
            
            # Track toward daily target
            if new_count > 0:
                self._increment_daily_opportunity_count(new_count)
                logger.info(f"🎯 [DAILY TARGET] +{new_count} presolicitations found today (Total: {self.daily_stats['new_opportunities_found']}/{self.DAILY_OPPORTUNITY_TARGET})")
        
        # After presol hunt, check if we need to get aggressive about finding opportunities
        self._check_daily_target()
    
    # ==================== MAIN LOOP ====================
    
    def job_daily_end_of_day_summary(self):
        """
        End-of-day summary and alert if daily target not met.
        This runs at 11:45 PM to give final warning if needed.
        """
        now = datetime.now()
        current_count = self.daily_stats['new_opportunities_found']
        target = self.DAILY_OPPORTUNITY_TARGET
        
        logger.info("=" * 60)
        logger.info("📊 [END OF DAY SUMMARY]")
        logger.info("=" * 60)
        
        if current_count >= target:
            logger.info(f"✅ SUCCESS! Found {current_count}/{target} opportunities today")
            logger.info(f"   On track for {self.MONTHLY_BID_TARGET}+ bids this month")
            self.daily_stats['target_met'] = True
            self.stats['daily_targets_met'] += 1
        else:
            shortfall = target - current_count
            logger.error(f"🚨 DAILY TARGET MISSED! Only found {current_count}/{target} opportunities")
            logger.error(f"   Shortfall: {shortfall} opportunities")
            logger.error(f"   This puts monthly bid target ({self.MONTHLY_BID_TARGET}+) at RISK")
            self.daily_stats['target_met'] = False
            self.stats['daily_targets_missed'] += 1
            
            # Generate high-priority alert
            self._trigger_daily_target_missed_alert(current_count, target)
        
        # Monthly progress calculation
        days_in_month = 30  # Approximate
        days_remaining = days_in_month - now.day
        current_month_total = (self.stats['daily_targets_met'] * self.DAILY_OPPORTUNITY_TARGET) + current_count
        projected_monthly = current_month_total + (days_remaining * self.DAILY_OPPORTUNITY_TARGET)
        
        logger.info(f"📈 Monthly Progress: ~{current_month_total} opportunities found so far")
        logger.info(f"   Projected monthly total: ~{projected_monthly}")
        logger.info(f"   Target: {self.MONTHLY_BID_TARGET}+ bids")
        logger.info("=" * 60)
        
        self._save_daily_stats()

    def _trigger_daily_target_missed_alert(self, found: int, target: int):
        """Generate critical alert when daily target is missed"""
        alert_data = {
            'alert_type': 'DAILY_TARGET_MISSED',
            'severity': 'CRITICAL',
            'timestamp': datetime.now().isoformat(),
            'message': f'URGENT: Only found {found}/{target} opportunities today. Monthly bid target at risk!',
            'shortfall': target - found,
            'action_required': 'Review search criteria, expand NAICS codes, or manually search SAM.gov'
        }
        
        # Save alert
        with open('critical_alerts.jsonl', 'a') as f:
            f.write(json.dumps(alert_data) + '\n')
        
        # Also could: send email, Slack notification, SMS, etc.
        logger.critical(f"🚨 CRITICAL ALERT: {alert_data['message']}")

    def run_scheduler(self):
        """Run the continuous ingestion scheduler with DAILY 3-OPPORTUNITY TARGET"""
        logger.info("=" * 60)
        logger.info("NEXUS CONTINUOUS INGESTION ENGINE STARTED")
        logger.info("=" * 60)
        logger.info("🎯 CRITICAL BUSINESS RULE: Find 3 NEW opportunities EVERY DAY")
        logger.info("   This ensures 12+ opportunities per month to hit win targets")
        logger.info("=" * 60)
        logger.info("Schedule:")
        logger.info("  - SAM.gov poll: Every 15 minutes (tracks toward daily target)")
        logger.info("  - Presolicitation hunt: Every hour (counts toward daily target)")
        logger.info("  - USASpending sync: Daily at 6:00 AM")
        logger.info("  - End-of-day summary: 11:45 PM (alerts if target missed)")
        logger.info("=" * 60)

        # Schedule jobs
        schedule.every(15).minutes.do(self.job_sam_gov_poll)
        schedule.every().hour.do(self.job_presolicitation_hunt)
        schedule.every().day.at("06:00").do(self.job_usaspending_daily)
        schedule.every().day.at("23:45").do(self.job_daily_end_of_day_summary)

        # Run initial ingestion
        self.job_sam_gov_poll()

        # Main loop
        while True:
            try:
                schedule.run_pending()
                
                # Check daily target every 15 minutes and log progress
                if datetime.now().minute % 15 == 0:
                    self._check_daily_target()
                
                time.sleep(60)  # Check every minute
            except KeyboardInterrupt:
                logger.info("[SHUTDOWN] Ingestion engine stopped by user")
                self._save_seen_ids()
                self._save_daily_stats()
                break
            except Exception as e:
                logger.error(f"[ERROR] Scheduler error: {e}")
                time.sleep(300)  # Wait 5 minutes on error
    
    def run_once(self):
        """Run all ingestion jobs once (for testing/manual execution)"""
        logger.info("[MANUAL] Running one-time full ingestion...")
        logger.info(f"🎯 Daily target: {self.DAILY_OPPORTUNITY_TARGET} opportunities to enable {self.MONTHLY_BID_TARGET}+ bids/month")

        self.job_sam_gov_poll()
        self.job_usaspending_daily()

        logger.info("=" * 60)
        logger.info("INGESTION COMPLETE")
        logger.info(f"  Total opportunities: {self.stats['total_ingested']}")
        logger.info(f"  New opportunities today: {self.daily_stats['new_opportunities_found']}/{self.DAILY_OPPORTUNITY_TARGET}")
        logger.info(f"  Duplicates skipped: {self.stats['duplicates_skipped']}")
        logger.info(f"  High score alerts: {self.stats['high_score_alerts']}")
        
        # Daily target status
        if self.daily_stats['new_opportunities_found'] >= self.DAILY_OPPORTUNITY_TARGET:
            logger.info(f"  ✅ Daily target MET: {self.daily_stats['new_opportunities_found']}/{self.DAILY_OPPORTUNITY_TARGET}")
        else:
            remaining = self.DAILY_OPPORTUNITY_TARGET - self.daily_stats['new_opportunities_found']
            logger.warning(f"  ⚠️ Daily target NOT MET: Need {remaining} more opportunities today")
        
        logger.info("=" * 60)
    
    # ==================== UTILITIES ====================
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse various date formats"""
        if not date_str:
            return None
        
        formats = [
            '%Y-%m-%dT%H:%M:%S.%f',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%d',
            '%m/%d/%Y'
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str[:len(fmt)], fmt)
            except:
                continue
        
        return None
    
    def _parse_value(self, award_data: Dict) -> Optional[float]:
        """Parse award value from SAM data"""
        if not award_data:
            return None
        
        try:
            value = award_data.get('amount', 0)
            if value:
                return float(value)
        except:
            pass
        
        return None


# ==================== CLI INTERFACE ====================

def main():
    """CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='NEXUS Continuous Data Ingestion Engine')
    parser.add_argument('--run-once', action='store_true', help='Run all jobs once and exit')
    parser.add_argument('--sam-only', action='store_true', help='Only run SAM.gov ingestion')
    parser.add_argument('--daemon', action='store_true', help='Run as continuous daemon')
    
    args = parser.parse_args()
    
    engine = DataIngestionEngine()
    
    if args.run_once:
        engine.run_once()
    elif args.sam_only:
        opportunities = engine.ingest_sam_gov(hours_back=24)
        engine.sync_to_airtable(opportunities)
    elif args.daemon:
        engine.run_scheduler()
    else:
        # Default: run once with summary
        engine.run_once()


if __name__ == '__main__':
    main()
