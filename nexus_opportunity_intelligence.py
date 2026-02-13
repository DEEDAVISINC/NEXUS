#!/usr/bin/env python3
"""
NEXUS OPPORTUNITY INTELLIGENCE ENGINE
======================================
The AI brain that scores every opportunity and alerts Dee when something is worth bidding.

Components:
1. OpportunityIntelligenceEngine — AI scorer + email alerts
2. MichiganLocalMiner — MITN, Detroit, Oakland County, Michigan portals

This module is called by nexus_scheduler.py every 2 hours (scoring) and every 6 hours (local mining).
"""

import os
import json
import smtplib
import requests
import anthropic
import re
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()

# ============================================================================
# DEE DAVIS INC — COMPANY PROFILE
# ============================================================================
DDI_PROFILE = {
    'company': 'Dee Davis Inc.',
    'certifications': ['EDWOSB', 'WOSB', 'WBE', 'MBE', 'SBE'],
    'naics_codes': [
        '423840', '423850', '423990', '424120', '424690', '424910',
        '444190', '561730', '423510', '423720', '423610', '423490', '339999',
    ],
    'products': [
        'office supplies', 'industrial supplies', 'janitorial supplies',
        'safety supplies', 'PPE', 'cleaning chemicals', 'paper products',
        'landscaping materials', 'topsoil', 'grass seed', 'mulch',
        'aggregate materials', 'water infrastructure parts', 'valves',
        'pipes', 'fittings', 'electrical supplies', 'power cables',
        'signs', 'traffic safety', 'wood poles', 'chlorine',
        'trucks', 'vehicles', 'fleet', 'salt', 'sand', 'gravel',
        'tools', 'hardware', 'fasteners', 'paint', 'coatings',
    ],
    'services': [
        'product distribution', 'supply chain management', 'freight brokerage',
        'grounds maintenance', 'landscaping', 'janitorial services',
        'courier services', 'logistics coordination', 'subcontractor management',
    ],
    # Dee Davis Inc. can work in ANY state — freight brokerage + subcontractor coordination
    # Home base gives slight edge but NOT a requirement
    'home_states': ['MI', 'OH', 'IN', 'IL', 'WI'],  # Slight bonus, NOT a filter
    'sweet_spot_min': 10000,
    'sweet_spot_max': 500000,
    'max_contract': 2000000,
}

# Email configuration
SMTP_SERVER = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = 587
EMAIL_FROM = os.environ.get('NEXUS_EMAIL', 'bids.deedavisinc@gmail.com')
EMAIL_PASSWORD = os.environ.get('NEXUS_EMAIL_PASSWORD', '')
EMAIL_TO = os.environ.get('USER_EMAIL', 'bids.deedavisinc@gmail.com')
NOTIFICATION_EMAIL = os.environ.get('NOTIFICATION_EMAIL', 'bids.deedavisinc@gmail.com')


# ============================================================================
# OPPORTUNITY INTELLIGENCE ENGINE — AI SCORING + EMAIL ALERTS
# ============================================================================

class OpportunityIntelligenceEngine:
    """
    Scores every new opportunity against Dee Davis Inc.'s profile and capabilities.
    
    Scoring tiers:
      85-100: BID NOW — Drop everything, this is a match
      65-84:  WORTH A LOOK — Good potential, review when you can
      40-64:  MAYBE — Stretch, but possible with right subcontractor
      0-39:   SKIP — Not a fit
    
    For BID NOW opportunities:
      - Sends immediate email alert to Dee
      - Updates Airtable with score and recommendation
      - Highlights WHY it's a match (set-aside, NAICS, location, value)
    """
    
    def __init__(self):
        from pyairtable import Api
        self.airtable_api = Api(os.environ.get('AIRTABLE_API_KEY', ''))
        self.base_id = os.environ.get('AIRTABLE_BASE_ID', '')
        self.anthropic_client = anthropic.Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY', ''))
    
    def _get_table(self, table_name: str):
        return self.airtable_api.table(self.base_id, table_name)
    
    def score_and_alert(self) -> Dict:
        """
        Main entry point. Called by scheduler every 2 hours.
        1. Fetch all unscored opportunities from Airtable
        2. Score each one
        3. Update Airtable with scores
        4. Email alerts for BID NOW opportunities
        """
        print("🧠 NEXUS Intelligence Engine — Scoring new opportunities...")
        
        results = {
            'bid_now': 0,
            'worth_a_look': 0,
            'maybe': 0,
            'skip': 0,
            'errors': 0,
            'emails_sent': 0,
            'scored': [],
        }
        
        try:
            table = self._get_table('GPSS OPPORTUNITIES')
            all_records = table.all()
        except Exception as e:
            print(f"   ❌ Failed to fetch Airtable records: {e}")
            return results
        
        # Find unscored opportunities
        # Airtable field is "Source Status" (not "Status")
        # "AI Recommendation " field (note trailing space) is used for score tracking
        unscored = []
        for record in all_records:
            fields = record.get('fields', {})
            source_status = (fields.get('Source Status') or '').strip()
            ai_rec = (fields.get('AI Recommendation ') or '').strip()
            
            # Skip already scored by AI
            if ai_rec and ('BID NOW' in ai_rec or 'SKIP' in ai_rec or 'Worth' in ai_rec or 'Maybe' in ai_rec):
                continue
            
            # Score records that are:
            # 1. "New - API" (freshly mined from SAM.gov/GovCon)
            # 2. Empty status (imported but not categorized)
            # 3. Forecast records (to identify the diamonds)
            # 4. Presolicitation/Sources Sought types
            # Skip records that are already being actively worked by Dee
            active_statuses = ['active', 'submitted', 'awaiting quotes', 'ready to bid',
                               'missed', 'not started', 'conditional', 'bid now']
            is_active = any(s in source_status.lower() for s in active_statuses)
            if is_active:
                continue
            
            # Skip records already categorized as "Worth A Look" by AI
            if 'worth a look' in source_status.lower():
                continue
            
            unscored.append(record)
        
        if not unscored:
            print("   ✓ No new opportunities to score")
            return results
        
        # Cap at 200 per run to avoid Airtable rate limits (5 requests/sec)
        # Prioritize: New-API first, then empty status, then forecasts
        def priority_sort(record):
            ss = (record.get('fields', {}).get('Source Status') or '').lower()
            if 'new - api' in ss:
                return 0
            elif ss == '' or ss == '(empty)':
                return 1
            else:
                return 2
        
        unscored.sort(key=priority_sort)
        batch = unscored[:200]
        
        print(f"   📊 Scoring {len(batch)} opportunities (of {len(unscored)} total unscored)...")
        
        bid_now_opps = []
        
        for idx, record in enumerate(batch):
            try:
                fields = record.get('fields', {})
                score_result = self._score_opportunity(fields)
                
                tier = score_result['tier']
                score = score_result['score']
                reasoning = score_result['reasoning']
                
                # Update Airtable with score
                # Field: "AI Recommendation " (note trailing space — matches existing Airtable schema)
                # Field: "Source Status" for status updates
                # Field: "Notes" for reasoning
                try:
                    update_fields = {
                        'AI Recommendation ': f'{tier} ({score}/100)',
                    }
                    
                    # Update source status for high-value items
                    if tier == 'BID NOW':
                        update_fields['Source Status'] = f'🔴 BID NOW — AI Score {score}/100'
                        update_fields['Priority'] = 'High'
                        results['bid_now'] += 1
                        bid_now_opps.append({
                            'record': record,
                            'score': score,
                            'reasoning': reasoning,
                            'fields': fields,
                        })
                    elif tier == 'WORTH A LOOK':
                        update_fields['Source Status'] = f'🟡 Worth A Look — AI Score {score}/100'
                        results['worth_a_look'] += 1
                    elif tier == 'MAYBE':
                        results['maybe'] += 1
                        # Don't update Source Status for maybes — leave original
                    else:
                        results['skip'] += 1
                        # Don't update Source Status for skips — leave original
                    
                    # Append reasoning to Notes (only for BID NOW and WORTH A LOOK)
                    if tier in ('BID NOW', 'WORTH A LOOK'):
                        existing_notes = fields.get('Notes', '') or ''
                        score_note = f"\n\n--- AI SCORE: {score}/100 ({tier}) ---\n{reasoning}\nScored: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                        update_fields['Notes'] = (existing_notes + score_note)[:2000]
                    
                    table.update(record['id'], update_fields)
                    
                    # Rate limit: Airtable allows 5 req/sec
                    import time
                    time.sleep(0.25)
                    
                except Exception as e:
                    print(f"   ⚠️  Failed to update Airtable for {fields.get('Name', '?')[:30]}: {e}")
                
                results['scored'].append({
                    'name': fields.get('Name', 'Unknown')[:50],
                    'score': score,
                    'tier': tier,
                })
                
            except Exception as e:
                results['errors'] += 1
                print(f"   ❌ Scoring error: {e}")
        
        # Send email alerts for BID NOW opportunities
        if bid_now_opps:
            try:
                emails_sent = self._send_bid_now_alerts(bid_now_opps)
                results['emails_sent'] = emails_sent
            except Exception as e:
                print(f"   ❌ Email alert failed: {e}")
        
        # Print summary
        print(f"\n   ✅ SCORING COMPLETE:")
        print(f"   🔴 BID NOW: {results['bid_now']}")
        print(f"   🟡 WORTH A LOOK: {results['worth_a_look']}")
        print(f"   🔵 MAYBE: {results['maybe']}")
        print(f"   ⚪ SKIP: {results['skip']}")
        if results['emails_sent']:
            print(f"   📧 Alert emails sent: {results['emails_sent']}")
        
        return results
    
    def _score_opportunity(self, fields: Dict) -> Dict:
        """
        Score an opportunity against DDI profile.
        Uses a hybrid approach: rule-based scoring + AI enhancement.
        
        Returns: {'score': 0-100, 'tier': 'BID NOW'|'WORTH A LOOK'|'MAYBE'|'SKIP', 'reasoning': str}
        """
        name = (fields.get('Name') or '').lower()
        status = (fields.get('Source Status') or '').lower()
        set_aside = (fields.get('Set-Aside Type') or '').lower()
        naics = (fields.get('NAISC Codes') or fields.get('NAICS Codes') or '')
        state = (fields.get('State') or '').upper()
        notes = (fields.get('Notes') or '').lower()
        source_url = fields.get('Source URL', '')
        deadline_str = fields.get('Deadline', '')
        agency = (fields.get('AGENCY NAME') or fields.get('AGENCY') or '').lower()
        
        combined_text = f"{name} {notes} {agency}"
        
        score = 0
        reasons = []
        
        # === SET-ASIDE SCORING (0-30 points) ===
        if 'edwosb' in set_aside:
            score += 30
            reasons.append("EDWOSB set-aside — maximum advantage")
        elif 'wosb' in set_aside or 'women' in set_aside:
            score += 25
            reasons.append("WOSB set-aside — strong advantage")
        elif 'small business' in set_aside or 'sba' in set_aside:
            score += 15
            reasons.append("Small business set-aside — eligible")
        elif set_aside == '' or 'total' in set_aside:
            score += 5
            reasons.append("Open/unrestricted — more competition")
        
        # === NAICS CODE MATCH (0-20 points) ===
        if naics:
            naics_list = [n.strip() for n in naics.replace(',', ' ').split()]
            matching_naics = [n for n in naics_list if n in DDI_PROFILE['naics_codes']]
            if matching_naics:
                score += 20
                reasons.append(f"NAICS match: {', '.join(matching_naics)}")
            else:
                score += 3
                reasons.append(f"NAICS {naics} not in primary codes — may need subcontractor")
        
        # === PRODUCT/SERVICE KEYWORD MATCH (0-20 points) ===
        product_matches = []
        for product in DDI_PROFILE['products']:
            if product in combined_text:
                product_matches.append(product)
        for service in DDI_PROFILE['services']:
            if service in combined_text:
                product_matches.append(service)
        
        if len(product_matches) >= 3:
            score += 20
            reasons.append(f"Strong product/service match: {', '.join(product_matches[:5])}")
        elif len(product_matches) >= 1:
            score += 12
            reasons.append(f"Partial product match: {', '.join(product_matches[:3])}")
        else:
            # Check for general categories
            general_keywords = ['supply', 'supplies', 'equipment', 'material', 'products',
                                'maintenance', 'service', 'distribution', 'delivery']
            gen_matches = [kw for kw in general_keywords if kw in combined_text]
            if gen_matches:
                score += 5
                reasons.append(f"General category match: {', '.join(gen_matches[:3])}")
        
        # === LOCATION SCORING (0-15 points) ===
        # WE CAN WORK IN ANY STATE — freight brokerage + subcontractor model
        # Home base gets a small bonus, but everywhere else is still fully eligible
        if state in DDI_PROFILE['home_states']:
            score += 15
            reasons.append(f"Home turf: {state} — local advantage")
        elif state:
            score += 10
            reasons.append(f"Location: {state} — we serve all 50 states")
        else:
            score += 10
            reasons.append("No state specified — we serve nationwide")
        
        # === PRESOLICITATION / SOURCES SOUGHT BONUS (0-15 points) ===
        if 'sources sought' in status or 'sources sought' in name:
            score += 15
            reasons.append("Sources Sought — ALWAYS RESPOND, early mover advantage")
        elif 'presolicitation' in status or 'presolicitation' in name:
            score += 12
            reasons.append("Presolicitation — get on buyer's radar early")
        elif 'sole source' in status or 'sole source' in name or 'intent to' in name:
            score += 15
            reasons.append("Sole source/Intent — EDWOSB alternative opportunity, ALWAYS RESPOND")
        
        # === EDWOSB + PRODUCT MATCH COMBO BONUS (0-10 points) ===
        # If EDWOSB/WOSB set-aside AND we have product matches, this is a strong combo
        if ('edwosb' in set_aside or 'wosb' in set_aside) and product_matches:
            score += 10
            reasons.append("EDWOSB/WOSB + product match = strong competitive position")
        
        # === DEADLINE URGENCY (0-5 points) ===
        if deadline_str:
            try:
                from dateutil import parser as date_parser
                deadline = date_parser.parse(deadline_str)
                days_left = (deadline - datetime.now()).days
                if 3 <= days_left <= 14:
                    score += 5
                    reasons.append(f"Deadline in {days_left} days — actionable window")
                elif days_left < 3:
                    score -= 5
                    reasons.append(f"⚠️ Only {days_left} days left — tight deadline")
                elif days_left > 30:
                    score += 2
                    reasons.append(f"Deadline in {days_left} days — plenty of time")
            except:
                pass
        
        # === NEGATIVE SIGNALS (-points) ===
        negative_keywords = [
            'construction bond', 'performance bond required', 'top secret clearance',
            'ts/sci', 'software development', 'programming', 'web development',
            'aircraft', 'submarine', 'nuclear', 'classified', 'secret clearance',
        ]
        for neg in negative_keywords:
            if neg in combined_text:
                score -= 10
                reasons.append(f"⚠️ Negative signal: '{neg}' — may not be a fit")
                break
        
        # Clamp score
        score = max(0, min(100, score))
        
        # Determine tier
        if score >= 75:
            tier = 'BID NOW'
        elif score >= 55:
            tier = 'WORTH A LOOK'
        elif score >= 35:
            tier = 'MAYBE'
        else:
            tier = 'SKIP'
        
        return {
            'score': score,
            'tier': tier,
            'reasoning': '\n'.join(f"• {r}" for r in reasons),
        }
    
    def _send_bid_now_alerts(self, bid_now_opps: List[Dict]) -> int:
        """Send email alerts for BID NOW opportunities."""
        if not EMAIL_PASSWORD:
            print("   ⚠️  No email password configured — skipping email alerts")
            return 0
        
        # Build email body with all BID NOW opportunities
        opp_sections = []
        for item in bid_now_opps:
            fields = item['fields']
            name = fields.get('Name', 'Untitled')
            rfp = fields.get('RFP NUMBER', 'N/A')
            agency = fields.get('AGENCY', 'Unknown')
            set_aside = fields.get('Set-Aside Type', 'N/A')
            deadline = fields.get('Deadline', 'N/A')
            state = fields.get('State', 'N/A')
            score = item['score']
            reasoning = item['reasoning']
            source_url = fields.get('Source URL', '')
            
            section = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔴 BID NOW — Score: {score}/100
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 {name}
📌 RFP: {rfp}
🏛️  Agency: {agency}
🏷️  Set-Aside: {set_aside}
📍 State: {state}
⏰ Deadline: {deadline}
🔗 {source_url}

WHY THIS IS A MATCH:
{reasoning}
"""
            opp_sections.append(section)
        
        subject = f"🔴 NEXUS ALERT: {len(bid_now_opps)} BID NOW Opportunit{'y' if len(bid_now_opps) == 1 else 'ies'} Found"
        
        body = f"""
NEXUS OPPORTUNITY INTELLIGENCE
{'=' * 50}

{len(bid_now_opps)} HIGH-MATCH OPPORTUNIT{'Y' if len(bid_now_opps) == 1 else 'IES'} DETECTED
Scored at 85+ against your company profile.
These are strong matches — review and act ASAP.

{''.join(opp_sections)}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
NEXT STEPS:
1. Log into NEXUS dashboard to review details
2. Check the GPSS Opportunities table for full info
3. Create bid folder and start pursuing

This alert was generated automatically by NEXUS Intelligence Engine.
Scanned at: {datetime.now().strftime('%Y-%m-%d %I:%M %p')}
"""
        
        try:
            msg = MIMEMultipart()
            msg['From'] = EMAIL_FROM
            msg['To'] = NOTIFICATION_EMAIL
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))
            
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(EMAIL_FROM, EMAIL_PASSWORD)
                server.send_message(msg)
            
            print(f"   📧 BID NOW alert email sent to {NOTIFICATION_EMAIL}")
            return 1
            
        except Exception as e:
            print(f"   ❌ Email send failed: {e}")
            return 0


# ============================================================================
# MICHIGAN LOCAL MINER — MITN, Detroit, Oakland County, etc.
# ============================================================================

class MichiganLocalMiner:
    """
    Mines Michigan state and local government portals for bid opportunities.
    
    Sources:
    1. MITN (Michigan Inter-governmental Trade Network) via BidNet Direct
    2. Oakland County purchasing
    3. City of Detroit procurement
    4. Wayne County procurement
    5. Macomb County procurement
    6. MDOT (Michigan DOT)
    """
    
    # Michigan portal configurations
    SOURCES = {
        'MITN_BidNet': {
            'name': 'MITN / BidNet Direct',
            'search_url': 'https://www.bidnetdirect.com/michigan/mitn',
            'rss_url': 'https://www.bidnetdirect.com/michigan/mitn/rss',
            'enabled': True,
        },
        'Oakland_County': {
            'name': 'Oakland County Purchasing',
            'url': 'https://www.oakgov.com/purchasing/',
            'search_url': 'https://www.oakgov.com/purchasing/bids-contracts/',
            'enabled': True,
        },
        'Detroit': {
            'name': 'City of Detroit Procurement',
            'url': 'https://detroitmi.gov/departments/office-chief-financial-officer/ocfo-divisions/office-contracting-and-procurement',
            'enabled': True,
        },
        'Wayne_County': {
            'name': 'Wayne County Procurement',
            'url': 'https://www.waynecounty.com/departments/management-budget/procurement-services.aspx',
            'enabled': True,
        },
        'Macomb_County': {
            'name': 'Macomb County Purchasing',
            'url': 'https://purchasing.macombgov.org/',
            'enabled': True,
        },
        'MDOT': {
            'name': 'Michigan DOT',
            'url': 'https://www.michigan.gov/mdot',
            'enabled': True,
        },
    }
    
    # Keywords to search for on these portals
    SEARCH_KEYWORDS = [
        'supplies', 'janitorial', 'cleaning', 'office', 'safety',
        'PPE', 'landscaping', 'grounds maintenance', 'mowing',
        'sand', 'salt', 'gravel', 'aggregate', 'signs', 'traffic',
        'pipes', 'valves', 'water', 'tools', 'hardware',
        'trucks', 'vehicles', 'fleet', 'equipment', 'chemicals',
        'paper', 'products', 'materials', 'delivery', 'distribution',
    ]
    
    def __init__(self):
        from pyairtable import Api
        self.airtable_api = Api(os.environ.get('AIRTABLE_API_KEY', ''))
        self.base_id = os.environ.get('AIRTABLE_BASE_ID', '')
    
    def _get_table(self, table_name: str):
        return self.airtable_api.table(self.base_id, table_name)
    
    def mine_all(self) -> Dict:
        """Mine all enabled Michigan sources."""
        results = {
            'total_found': 0,
            'imported': 0,
            'sources_checked': 0,
            'errors': [],
        }
        
        print("🏛️  Mining Michigan State & Local Portals...")
        
        # 1. MITN via BidNet Direct (best source — most Michigan municipalities use this)
        try:
            mitn_result = self._mine_mitn_bidnet()
            results['sources_checked'] += 1
            results['total_found'] += mitn_result.get('found', 0)
            results['imported'] += mitn_result.get('imported', 0)
        except Exception as e:
            results['errors'].append(f"MITN/BidNet: {str(e)}")
            print(f"   ❌ MITN/BidNet error: {e}")
        
        # 2. Oakland County (direct scrape)
        try:
            oak_result = self._mine_oakland_county()
            results['sources_checked'] += 1
            results['total_found'] += oak_result.get('found', 0)
            results['imported'] += oak_result.get('imported', 0)
        except Exception as e:
            results['errors'].append(f"Oakland County: {str(e)}")
            print(f"   ❌ Oakland County error: {e}")
        
        # 3. City of Detroit
        try:
            det_result = self._mine_detroit()
            results['sources_checked'] += 1
            results['total_found'] += det_result.get('found', 0)
            results['imported'] += det_result.get('imported', 0)
        except Exception as e:
            results['errors'].append(f"Detroit: {str(e)}")
            print(f"   ❌ Detroit error: {e}")
        
        # 4. SAM.gov Michigan-specific search (guaranteed to work)
        try:
            sam_mi_result = self._mine_sam_michigan()
            results['sources_checked'] += 1
            results['total_found'] += sam_mi_result.get('found', 0)
            results['imported'] += sam_mi_result.get('imported', 0)
        except Exception as e:
            results['errors'].append(f"SAM.gov Michigan: {str(e)}")
            print(f"   ❌ SAM.gov Michigan error: {e}")
        
        print(f"\n   ✅ Michigan mining complete: {results['total_found']} found, {results['imported']} imported")
        if results['errors']:
            print(f"   ⚠️  {len(results['errors'])} source errors (non-fatal)")
        
        return results
    
    def _mine_mitn_bidnet(self) -> Dict:
        """
        Mine MITN opportunities via BidNet Direct.
        BidNet Direct hosts MITN bids — this is where Oakland County, 
        Macomb County, and hundreds of Michigan municipalities post bids.
        """
        print("   🔍 Mining MITN / BidNet Direct...")
        found = 0
        imported = 0
        
        try:
            # BidNet Direct / MITN — try multiple URL patterns
            search_urls = [
                "https://www.bidnetdirect.com/michigan/mitn",
                "https://www.bidnetdirect.com/michigan",
                "https://www.mitn.info",
            ]
            search_url = None
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
            
            response = None
            for try_url in search_urls:
                try:
                    response = requests.get(try_url, headers=headers, timeout=15)
                    if response.status_code == 200:
                        search_url = try_url
                        break
                except:
                    continue
            
            if not search_url or not response or response.status_code != 200:
                print(f"      ⚠️  BidNet/MITN URLs all failed")
                return {'found': 0, 'imported': 0}
            
            if response.status_code == 200:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for bid listings — BidNet uses specific CSS classes
                bid_items = soup.select('.bid-item, .search-result, .listing-item, tr.bid-row, .opportunity-item')
                
                if not bid_items:
                    # Try alternate selectors
                    bid_items = soup.find_all('div', class_=re.compile(r'bid|listing|opportunity', re.I))
                
                if not bid_items:
                    # Fallback: look for links with bid-like text
                    all_links = soup.find_all('a', href=True)
                    bid_items = [
                        link for link in all_links
                        if any(kw in (link.get_text() or '').lower() for kw in self.SEARCH_KEYWORDS)
                        and len(link.get_text().strip()) > 10
                    ]
                
                for item in bid_items[:30]:  # Process up to 30 results
                    try:
                        # Extract title
                        title = ''
                        if hasattr(item, 'select_one'):
                            title_el = item.select_one('h3, h4, .title, .bid-title, a')
                            if title_el:
                                title = title_el.get_text(strip=True)
                        if not title:
                            title = item.get_text(strip=True)[:200]
                        
                        if not title or len(title) < 5:
                            continue
                        
                        # Check if relevant to our keywords
                        title_lower = title.lower()
                        is_relevant = any(kw in title_lower for kw in self.SEARCH_KEYWORDS)
                        if not is_relevant:
                            continue
                        
                        # Check for duplicates
                        if self._is_duplicate(title):
                            continue
                        
                        # Extract URL
                        url = ''
                        if item.name == 'a':
                            url = item.get('href', '')
                        else:
                            link = item.find('a', href=True)
                            if link:
                                url = link.get('href', '')
                        if url and not url.startswith('http'):
                            url = f"https://www.bidnetdirect.com{url}"
                        
                        # Import to Airtable
                        self._import_opportunity({
                            'title': title[:255],
                            'source': 'BidNet Direct / MITN',
                            'state': 'MI',
                            'url': url,
                        })
                        
                        found += 1
                        imported += 1
                        
                    except Exception:
                        continue
                
                print(f"      ✓ MITN/BidNet: {found} relevant found, {imported} imported")
            else:
                print(f"      ⚠️  BidNet returned {response.status_code}")
                
        except Exception as e:
            print(f"      ❌ MITN/BidNet scrape error: {e}")
        
        return {'found': found, 'imported': imported}
    
    def _mine_oakland_county(self) -> Dict:
        """Mine Oakland County purchasing portal."""
        print("   🔍 Mining Oakland County Purchasing...")
        found = 0
        imported = 0
        
        try:
            # Try multiple URLs — Oakland County has reorganized their site
            urls_to_try = [
                "https://www.oakgov.com/government/purchasing/open-bids",
                "https://www.oakgov.com/purchasing/bids-contracts/",
                "https://www.oakgov.com/government/departments-agencies/management-and-budget/purchasing",
            ]
            url = None
            response = None
            for try_url in urls_to_try:
                try:
                    response = requests.get(try_url, headers=headers, timeout=15)
                    if response.status_code == 200:
                        url = try_url
                        break
                except:
                    continue
            
            if not url or not response or response.status_code != 200:
                print(f"      ⚠️  Oakland County URLs all failed")
                return {'found': 0, 'imported': 0}
            
            if response.status_code == 200:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Oakland County lists bids in tables or list items
                rows = soup.select('table tr, .bid-listing li, .content-area li, .field-content')
                
                for row in rows[:20]:
                    try:
                        text = row.get_text(strip=True)
                        if len(text) < 10:
                            continue
                        
                        text_lower = text.lower()
                        is_relevant = any(kw in text_lower for kw in self.SEARCH_KEYWORDS)
                        if not is_relevant:
                            continue
                        
                        if self._is_duplicate(text[:100]):
                            continue
                        
                        link = row.find('a', href=True)
                        url = ''
                        if link:
                            url = link.get('href', '')
                            if url and not url.startswith('http'):
                                url = f"https://www.oakgov.com{url}"
                        
                        self._import_opportunity({
                            'title': text[:255],
                            'source': 'Oakland County Purchasing',
                            'state': 'MI',
                            'url': url,
                        })
                        
                        found += 1
                        imported += 1
                        
                    except Exception:
                        continue
                
                print(f"      ✓ Oakland County: {found} relevant found")
            else:
                print(f"      ⚠️  Oakland County returned {response.status_code}")
                
        except Exception as e:
            print(f"      ❌ Oakland County error: {e}")
        
        return {'found': found, 'imported': imported}
    
    def _mine_detroit(self) -> Dict:
        """Mine City of Detroit procurement portal."""
        print("   🔍 Mining City of Detroit Procurement...")
        found = 0
        imported = 0
        
        try:
            # Detroit has multiple possible procurement pages
            urls_to_try = [
                "https://detroitmi.gov/departments/office-chief-financial-officer/ocfo-divisions/office-contracting-and-procurement/current-bids-and-requests-proposals",
                "https://detroitmi.gov/government/office-chief-financial-officer/office-contracting-and-procurement",
                "https://detroitmi.gov/departments/office-contracting-and-procurement",
            ]
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
            
            response = None
            for try_url in urls_to_try:
                try:
                    response = requests.get(try_url, headers=headers, timeout=15)
                    if response.status_code == 200:
                        break
                except:
                    continue
            
            if not response or response.status_code != 200:
                print(f"      ⚠️  Detroit procurement URLs all returned non-200")
                return {'found': 0, 'imported': 0}
            
            if response.status_code == 200:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Detroit lists bids in content area
                items = soup.select('.view-content .views-row, .field-content, table tr, li')
                
                for item in items[:30]:
                    try:
                        text = item.get_text(strip=True)
                        if len(text) < 10:
                            continue
                        
                        text_lower = text.lower()
                        # Check for bid indicators
                        has_bid_indicator = any(kw in text_lower for kw in ['rfp', 'rfq', 'itb', 'bid', 'proposal', 'solicitation'])
                        is_relevant = any(kw in text_lower for kw in self.SEARCH_KEYWORDS)
                        
                        if not (has_bid_indicator or is_relevant):
                            continue
                        
                        if self._is_duplicate(text[:100]):
                            continue
                        
                        link = item.find('a', href=True)
                        link_url = ''
                        if link:
                            link_url = link.get('href', '')
                            if link_url and not link_url.startswith('http'):
                                link_url = f"https://detroitmi.gov{link_url}"
                        
                        self._import_opportunity({
                            'title': text[:255],
                            'source': 'City of Detroit',
                            'state': 'MI',
                            'url': link_url,
                        })
                        
                        found += 1
                        imported += 1
                        
                    except Exception:
                        continue
                
                print(f"      ✓ Detroit: {found} relevant found")
            else:
                print(f"      ⚠️  Detroit returned {response.status_code}")
                
        except Exception as e:
            print(f"      ❌ Detroit error: {e}")
        
        return {'found': found, 'imported': imported}
    
    def _mine_sam_michigan(self) -> Dict:
        """
        Mine SAM.gov specifically for Michigan opportunities.
        This is the most RELIABLE source — always works.
        Searches for our NAICS codes + Michigan performance location.
        """
        print("   🔍 Mining SAM.gov for Michigan-specific opportunities...")
        found = 0
        imported = 0
        
        api_key = os.environ.get('SAM_GOV_API_KEY', '')
        if not api_key:
            print("      ⚠️  No SAM.gov API key")
            return {'found': 0, 'imported': 0}
        
        try:
            base_url = "https://api.sam.gov/opportunities/v2/search"
            
            params = {
                'api_key': api_key,
                'limit': 50,
                'postedFrom': (datetime.now() - timedelta(days=14)).strftime('%m/%d/%Y'),
                'postedTo': datetime.now().strftime('%m/%d/%Y'),
                'state': 'MI',  # Michigan only
                'ntype': 'o,k,p,r',  # Solicitation, Combined, Presolicitation, Sources Sought
            }
            
            response = requests.get(base_url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                opps = data.get('opportunitiesData', [])
                
                for opp in opps:
                    try:
                        notice_id = opp.get('noticeId', '')
                        title = opp.get('title', '')
                        
                        if self._is_duplicate(notice_id) or self._is_duplicate(title[:100]):
                            continue
                        
                        # Check set-aside eligibility
                        set_aside = (opp.get('typeOfSetAside') or '').upper()
                        ineligible = ['SDVOSB', 'VOSB', 'HZC', 'HZS', '8A', '8AN']
                        if any(code in set_aside for code in ineligible):
                            continue
                        
                        deadline = ''
                        try:
                            if opp.get('responseDeadLine'):
                                from dateutil import parser as date_parser
                                deadline = date_parser.parse(opp['responseDeadLine']).strftime('%Y-%m-%d')
                        except:
                            pass
                        
                        self._import_opportunity({
                            'title': title[:255],
                            'rfp_number': notice_id,
                            'source': 'SAM.gov (Michigan)',
                            'state': 'MI',
                            'set_aside': opp.get('typeOfSetAsideDescription', ''),
                            'naics': opp.get('naicsCode', ''),
                            'agency': (opp.get('fullParentPathName') or '')[:255],
                            'deadline': deadline,
                            'url': f"https://sam.gov/opp/{notice_id}/view" if notice_id else '',
                        })
                        
                        found += 1
                        imported += 1
                        
                    except Exception:
                        continue
                
                print(f"      ✓ SAM.gov Michigan: {found} opportunities imported")
            else:
                print(f"      ⚠️  SAM.gov returned {response.status_code}")
        
        except Exception as e:
            print(f"      ❌ SAM.gov Michigan error: {e}")
        
        return {'found': found, 'imported': imported}
    
    def _is_duplicate(self, identifier: str) -> bool:
        """Check if an opportunity already exists in Airtable."""
        if not identifier:
            return False
        try:
            table = self._get_table('GPSS OPPORTUNITIES')
            records = table.all()
            identifier_clean = identifier.strip().lower()
            for r in records:
                fields = r.get('fields', {})
                name = (fields.get('Name') or '').lower()
                rfp = (fields.get('RFP NUMBER') or '').lower()
                if identifier_clean in name or identifier_clean == rfp:
                    return True
            return False
        except:
            return False
    
    def _import_opportunity(self, opp: Dict):
        """Import a local opportunity to Airtable."""
        try:
            table = self._get_table('GPSS OPPORTUNITIES')
            
            fields = {
                'Name': opp.get('title', 'Untitled')[:255],
                'Source Status': 'New - Local',
                'SOURCE': opp.get('source', 'Michigan Local'),
            }
            
            if opp.get('rfp_number'):
                fields['RFP NUMBER'] = opp['rfp_number']
            if opp.get('state'):
                fields['State'] = opp['state']
            if opp.get('url'):
                fields['Source URL'] = opp['url'][:500]
            if opp.get('set_aside'):
                fields['Set-Aside Type'] = opp['set_aside'][:100]
            if opp.get('naics'):
                fields['NAISC Codes'] = opp['naics'][:100]
            if opp.get('agency'):
                fields['AGENCY'] = opp['agency'][:255]
            if opp.get('deadline'):
                fields['Deadline'] = opp['deadline']
            
            notes_parts = []
            if opp.get('agency'):
                notes_parts.append(f"Agency: {opp['agency']}")
            if opp.get('set_aside'):
                notes_parts.append(f"Set-Aside: {opp['set_aside']}")
            if opp.get('url'):
                notes_parts.append(f"URL: {opp['url']}")
            if notes_parts:
                fields['Notes'] = ' | '.join(notes_parts)[:2000]
            
            table.create(fields)
            
        except Exception as e:
            print(f"      ⚠️  Import failed: {e}")


# ============================================================================
# DAILY DIGEST EMAIL
# ============================================================================

def send_daily_digest():
    """
    Send a daily digest email summarizing:
    - New opportunities found today
    - BID NOW recommendations
    - Upcoming deadlines
    - Stale bids needing attention
    
    Called by scheduler once per day (or manually).
    """
    print("📧 Generating daily digest...")
    
    if not EMAIL_PASSWORD:
        print("   ⚠️  No email password — skipping digest")
        return
    
    try:
        from pyairtable import Api
        airtable = Api(os.environ.get('AIRTABLE_API_KEY', ''))
        base_id = os.environ.get('AIRTABLE_BASE_ID', '')
        table = airtable.table(base_id, 'GPSS OPPORTUNITIES')
        records = table.all()
    except Exception as e:
        print(f"   ❌ Failed to fetch records: {e}")
        return
    
    now = datetime.now()
    today = now.strftime('%Y-%m-%d')
    
    # Categorize
    bid_now = []
    worth_look = []
    upcoming_deadlines = []
    new_today = []
    
    for r in records:
        f = r.get('fields', {})
        source_status = f.get('Source Status', '')
        ai_rec = f.get('AI Recommendation ', '')
        name = f.get('Name', 'Untitled')
        deadline = f.get('Deadline', '')
        
        if 'BID NOW' in source_status or 'BID NOW' in ai_rec:
            bid_now.append(f)
        elif 'Worth A Look' in source_status or 'WORTH A LOOK' in ai_rec:
            worth_look.append(f)
        
        if deadline:
            try:
                from dateutil import parser as dp
                dl = dp.parse(deadline)
                days_left = (dl - now).days
                if 0 <= days_left <= 7:
                    upcoming_deadlines.append({**f, '_days_left': days_left})
            except:
                pass
    
    # Build digest
    subject = f"📋 NEXUS Daily Digest — {now.strftime('%B %d, %Y')}"
    
    body = f"""
NEXUS DAILY DIGEST — {now.strftime('%A, %B %d, %Y')}
{'=' * 50}

🔴 BID NOW RECOMMENDATIONS: {len(bid_now)}
"""
    
    for opp in bid_now[:10]:
        body += f"  • {opp.get('Name', '?')[:60]} | {opp.get('Set-Aside Type', 'N/A')} | Due: {opp.get('Deadline', 'N/A')}\n"
    
    body += f"""
🟡 WORTH A LOOK: {len(worth_look)}
"""
    for opp in worth_look[:10]:
        body += f"  • {opp.get('Name', '?')[:60]} | Due: {opp.get('Deadline', 'N/A')}\n"
    
    body += f"""
⏰ UPCOMING DEADLINES (Next 7 Days): {len(upcoming_deadlines)}
"""
    for opp in sorted(upcoming_deadlines, key=lambda x: x.get('_days_left', 99)):
        body += f"  • [{opp['_days_left']}d] {opp.get('Name', '?')[:50]} | {opp.get('Status', '')}\n"
    
    body += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total records in pipeline: {len(records)}
Generated: {now.strftime('%I:%M %p')}
"""
    
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_FROM
        msg['To'] = NOTIFICATION_EMAIL
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_FROM, EMAIL_PASSWORD)
            server.send_message(msg)
        
        print(f"   ✅ Daily digest sent to {NOTIFICATION_EMAIL}")
        
    except Exception as e:
        print(f"   ❌ Digest email failed: {e}")


# ============================================================================
# CLI ENTRY POINT
# ============================================================================

if __name__ == '__main__':
    import sys
    
    if '--score' in sys.argv:
        engine = OpportunityIntelligenceEngine()
        result = engine.score_and_alert()
        print(json.dumps(result, indent=2, default=str))
    
    elif '--local' in sys.argv:
        miner = MichiganLocalMiner()
        result = miner.mine_all()
        print(json.dumps(result, indent=2, default=str))
    
    elif '--digest' in sys.argv:
        send_daily_digest()
    
    else:
        print("NEXUS Opportunity Intelligence Engine")
        print("Usage:")
        print("  python3 nexus_opportunity_intelligence.py --score   # Score all new opportunities + send alerts")
        print("  python3 nexus_opportunity_intelligence.py --local   # Mine Michigan local portals")
        print("  python3 nexus_opportunity_intelligence.py --digest  # Send daily digest email")
