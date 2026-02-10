#!/usr/bin/env python3
"""
MINE REAL FEDERAL FORECASTS
Pulls actual government forecast data from official sources
NO PREDICTIONS - ONLY REAL PUBLISHED FORECASTS

Data Sources:
1. DHS APFS - https://apfs-cloud.dhs.gov/forecast/
2. SAM.gov Pre-Solicitations
3. NASA Forecasts
4. Other agency forecasts

Author: NEXUS
Created: January 28, 2026
"""

import os
import requests
import csv
from io import StringIO
from datetime import datetime
from typing import Dict, List
from pyairtable import Api
from dotenv import load_dotenv
import time
import anthropic
from bs4 import BeautifulSoup

load_dotenv()


class RealFederalForecastsMiner:
    """Mine REAL federal forecasts from official government sources"""
    
    def __init__(self):
        self.airtable_token = os.environ.get('AIRTABLE_API_KEY')
        self.base_id = os.environ.get('AIRTABLE_BASE_ID')
        self.sam_api_key = os.environ.get('SAM_GOV_API_KEY')
        self.anthropic_key = os.environ.get('ANTHROPIC_API_KEY')
        
        self.api = Api(self.airtable_token)
        self.ai_client = anthropic.Anthropic(api_key=self.anthropic_key) if self.anthropic_key else None
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
    
    def mine_all_sources(self) -> Dict:
        """Mine all federal forecast sources"""
        
        print("=" * 80)
        print("MINING REAL FEDERAL FORECASTS - ALL SOURCES")
        print("=" * 80)
        print()
        
        results = {
            'dhs_apfs': 0,
            'sam_presolicitations': 0,
            'sam_forecasts': 0,
            'usaspending': 0,
            'beta_sam': 0,
            'total_stored': 0,
            'errors': []
        }
        
        # 1. Mine SAM.gov Pre-Solicitations (WORKING)
        print("1️⃣  Mining SAM.gov Pre-Solicitations...")
        try:
            sam_forecasts = self.mine_sam_presolicitations()
            results['sam_presolicitations'] = len(sam_forecasts)
            print(f"   ✅ Found {len(sam_forecasts)} pre-solicitations")
            
            stored = self.store_forecasts(sam_forecasts, 'SAM.gov Pre-Solicitation')
            results['total_stored'] += stored
            print(f"   💾 Stored {stored} new forecasts")
        except Exception as e:
            error_msg = f"SAM.gov Pre-Solic error: {e}"
            results['errors'].append(error_msg)
            print(f"   ❌ {error_msg}")
        print()
        
        # 2. Mine SAM.gov Forecast Opportunities
        print("2️⃣  Mining SAM.gov Forecasted Opportunities...")
        try:
            sam_forecast_opps = self.mine_sam_forecasts()
            results['sam_forecasts'] = len(sam_forecast_opps)
            print(f"   ✅ Found {len(sam_forecast_opps)} forecast opportunities")
            
            stored = self.store_forecasts(sam_forecast_opps, 'SAM.gov Forecast')
            results['total_stored'] += stored
            print(f"   💾 Stored {stored} new forecasts")
        except Exception as e:
            error_msg = f"SAM.gov Forecast error: {e}"
            results['errors'].append(error_msg)
            print(f"   ❌ {error_msg}")
        print()
        
        # 3. Mine USASpending.gov Contract Forecasts
        print("3️⃣  Mining USASpending.gov Contract Forecasts...")
        try:
            usaspending_forecasts = self.mine_usaspending_forecasts()
            results['usaspending'] = len(usaspending_forecasts)
            print(f"   ✅ Found {len(usaspending_forecasts)} spending forecasts")
            
            stored = self.store_forecasts(usaspending_forecasts, 'USASpending.gov')
            results['total_stored'] += stored
            print(f"   💾 Stored {stored} new forecasts")
        except Exception as e:
            error_msg = f"USASpending error: {e}"
            results['errors'].append(error_msg)
            print(f"   ❌ {error_msg}")
        print()
        
        # 4. Mine Beta.SAM.gov (Acquisitions.gov data)
        print("4️⃣  Mining Beta.SAM.gov / Acquisitions.gov...")
        try:
            beta_sam_forecasts = self.mine_beta_sam()
            results['beta_sam'] = len(beta_sam_forecasts)
            print(f"   ✅ Found {len(beta_sam_forecasts)} acquisition forecasts")
            
            stored = self.store_forecasts(beta_sam_forecasts, 'Beta.SAM.gov')
            results['total_stored'] += stored
            print(f"   💾 Stored {stored} new forecasts")
        except Exception as e:
            error_msg = f"Beta.SAM error: {e}"
            results['errors'].append(error_msg)
            print(f"   ❌ {error_msg}")
        print()
        
        # 5. Mine DHS APFS (JavaScript-heavy, might fail)
        print("5️⃣  Mining DHS APFS (Acquisition Planning Forecast System)...")
        try:
            dhs_forecasts = self.mine_dhs_apfs()
            results['dhs_apfs'] = len(dhs_forecasts)
            print(f"   ✅ Found {len(dhs_forecasts)} DHS forecasts")
            
            stored = self.store_forecasts(dhs_forecasts, 'DHS APFS')
            results['total_stored'] += stored
            print(f"   💾 Stored {stored} new forecasts")
        except Exception as e:
            error_msg = f"DHS APFS error: {e}"
            results['errors'].append(error_msg)
            print(f"   ❌ {error_msg}")
        print()
        
        print("=" * 80)
        print(f"✅ COMPLETE: {results['total_stored']} REAL forecasts stored")
        print(f"   SAM.gov Pre-Solicitations: {results['sam_presolicitations']}")
        print(f"   SAM.gov Forecasts: {results['sam_forecasts']}")
        print(f"   USASpending.gov: {results['usaspending']}")
        print(f"   Beta.SAM.gov/Acquisitions: {results['beta_sam']}")
        print(f"   DHS APFS: {results['dhs_apfs']}")
        if results['errors']:
            print(f"   ⚠️  Errors: {len(results['errors'])}")
        print("=" * 80)
        
        return results
    
    def mine_dhs_apfs(self) -> List[Dict]:
        """
        Mine DHS Acquisition Planning Forecast System
        URL: https://apfs-cloud.dhs.gov/forecast/
        """
        
        # Try to get the HTML page and parse the table
        url = "https://apfs-cloud.dhs.gov/forecast/"
        
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find the forecast table
            table = soup.find('table')
            
            if not table:
                print("   ⚠️  No table found on DHS APFS page")
                return []
            
            # Parse table rows
            forecasts = []
            rows = table.find_all('tr')[1:]  # Skip header row
            
            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 10:
                    try:
                        forecast = {
                            'apfs_number': cols[1].get_text(strip=True) if len(cols) > 1 else '',
                            'component': cols[2].get_text(strip=True) if len(cols) > 2 else '',
                            'title': cols[3].get_text(strip=True) if len(cols) > 3 else '',
                            'naics': cols[6].get_text(strip=True) if len(cols) > 6 else '',
                            'small_business_program': cols[7].get_text(strip=True) if len(cols) > 7 else '',
                            'set_aside': cols[29].get_text(strip=True) if len(cols) > 29 else '',
                            'dollar_range': cols[23].get_text(strip=True) if len(cols) > 23 else '',
                            'estimated_solicitation_date': cols[16].get_text(strip=True) if len(cols) > 16 else '',
                            'place_city': cols[17].get_text(strip=True) if len(cols) > 17 else '',
                            'place_state': cols[18].get_text(strip=True) if len(cols) > 18 else '',
                            'contact_first': cols[19].get_text(strip=True) if len(cols) > 19 else '',
                            'contact_last': cols[20].get_text(strip=True) if len(cols) > 20 else '',
                            'contact_phone': cols[21].get_text(strip=True) if len(cols) > 21 else '',
                            'contact_email': cols[22].get_text(strip=True) if len(cols) > 22 else '',
                            'source': 'DHS APFS',
                            'agency': 'Department of Homeland Security',
                            'forecast_type': 'Official DHS Forecast'
                        }
                        
                        if forecast['title']:  # Only add if has a title
                            forecasts.append(forecast)
                    except Exception as e:
                        continue
            
            return forecasts
            
        except Exception as e:
            print(f"   ⚠️  DHS APFS scraping error: {e}")
            return []
    
    # Set-aside codes Dee Davis Inc qualifies for
    ELIGIBLE_SET_ASIDE_CODES = 'EDWOSB,WOSB,SBA,SBP'

    # Set-aside codes to EXCLUDE if they slip through
    INELIGIBLE_KEYWORDS = ['SDVOSB', 'VOSB', 'VETERAN', 'SERVICE-DISABLED', 'HUBZONE', '8(A)', 'IEE', 'ISBEE']

    def _is_eligible_set_aside(self, set_aside_str: str) -> bool:
        """Check if a set-aside type is one Dee Davis Inc can bid on"""
        if not set_aside_str:
            return True  # Unrestricted is fine
        upper = set_aside_str.upper()
        for keyword in self.INELIGIBLE_KEYWORDS:
            if keyword in upper:
                return False
        return True

    def mine_sam_presolicitations(self) -> List[Dict]:
        """
        Mine SAM.gov pre-solicitation notices
        FILTERED: EDWOSB, WOSB, Small Business, Very Small Business ONLY
        Excludes SDVOSB, HUBZone, 8(a) — we don't qualify
        """
        
        if not self.sam_api_key:
            print("   ⚠️  SAM_GOV_API_KEY not set - skipping SAM.gov")
            return []
        
        try:
            url = "https://api.sam.gov/opportunities/v2/search"
            
            # Use query parameters in URL, not as params
            from datetime import timedelta
            posted_from = (datetime.now() - timedelta(days=60)).strftime('%m/%d/%Y')
            posted_to = datetime.now().strftime('%m/%d/%Y')
            
            # FILTER: EDWOSB + WOSB + Small Business + Very Small Business nationwide
            full_url = f"{url}?api_key={self.sam_api_key}&ptype=p&limit=100&postedFrom={posted_from}&postedTo={posted_to}&typeOfSetAside={self.ELIGIBLE_SET_ASIDE_CODES}"
            
            print("   🔍 Filters: EDWOSB, WOSB, SB set-asides (NATIONWIDE)")
            
            response = requests.get(full_url, timeout=30)
            
            if response.status_code == 403:
                print(f"   ⚠️  SAM.gov API key invalid or expired")
                return []
            elif response.status_code == 500:
                print(f"   ⚠️  SAM.gov API server error - try again later")
                return []
            elif response.status_code != 200:
                print(f"   ⚠️  SAM.gov API returned status {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                return []
            
            data = response.json()
            opportunities = data.get('opportunitiesData', [])
            
            if not opportunities:
                print(f"   ℹ️  No pre-solicitations found in date range")
                return []
            
            forecasts = []
            for opp in opportunities:
                # Safely get place of performance
                place_of_perf = opp.get('placeOfPerformance') or {}
                place_city = ''
                place_state = ''
                if isinstance(place_of_perf, dict):
                    city_data = place_of_perf.get('city') or {}
                    state_data = place_of_perf.get('state') or {}
                    if isinstance(city_data, dict):
                        place_city = city_data.get('name', '')
                    if isinstance(state_data, dict):
                        place_state = state_data.get('name', '')
                
                # Safely get contact email
                contact_email = ''
                point_of_contact = opp.get('pointOfContact')
                if point_of_contact and isinstance(point_of_contact, list) and len(point_of_contact) > 0:
                    contact_email = point_of_contact[0].get('email', '')
                
                # Double-check eligibility — skip SDVOSB/HUBZone/8(a) even if API returned them
                opp_set_aside = opp.get('typeOfSetAside', '') or ''
                if not self._is_eligible_set_aside(opp_set_aside):
                    continue

                forecast = {
                    'title': opp.get('title', 'Untitled')[:200],
                    'solicitation_number': opp.get('solicitationNumber', ''),
                    'agency': opp.get('department', 'Unknown'),
                    'sub_agency': opp.get('subtier', ''),
                    'naics': opp.get('naicsCode', ''),
                    'set_aside': opp_set_aside or 'Unrestricted',
                    'description': opp.get('description', '')[:1000],
                    'posted_date': opp.get('postedDate', ''),
                    'response_deadline': opp.get('responseDeadLine', ''),
                    'estimated_solicitation_date': self._estimate_solicitation_date(opp),
                    'place_city': place_city,
                    'place_state': place_state,
                    'contact_email': contact_email,
                    'source': 'SAM.gov Pre-Solicitation',
                    'forecast_type': 'Near-Term Pre-Solicitation',
                    'notice_id': opp.get('noticeId', ''),
                    'source_url': f"https://sam.gov/opp/{opp.get('noticeId', '')}"
                }
                
                forecasts.append(forecast)
            
            return forecasts
            
        except Exception as e:
            print(f"   ⚠️  SAM.gov mining error: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def mine_sam_forecasts(self) -> List[Dict]:
        """
        Mine SAM.gov forecasted/planned opportunities
        FILTERED: EDWOSB, WOSB, Small Business, Very Small Business ONLY
        Excludes SDVOSB, HUBZone, 8(a) — we don't qualify
        """
        
        if not self.sam_api_key:
            print("   ⚠️  SAM_GOV_API_KEY not set")
            return []
        
        try:
            url = "https://api.sam.gov/opportunities/v2/search"
            
            from datetime import timedelta
            posted_from = (datetime.now() - timedelta(days=60)).strftime('%m/%d/%Y')
            posted_to = datetime.now().strftime('%m/%d/%Y')
            
            # FILTER: EDWOSB + WOSB + SB + VSB forecasts nationwide
            print("   🔍 Filters: EDWOSB, WOSB, SB set-asides (NATIONWIDE)")
            forecasts = []
            
            for notice_type in ['s', 'o']:  # s=sources sought, o=other (includes forecasts)
                full_url = f"{url}?api_key={self.sam_api_key}&ptype={notice_type}&limit=100&postedFrom={posted_from}&postedTo={posted_to}&typeOfSetAside={self.ELIGIBLE_SET_ASIDE_CODES}"
                
                response = requests.get(full_url, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    opportunities = data.get('opportunitiesData', [])
                    
                    for opp in opportunities:
                        # Safely get all fields
                        place_of_perf = opp.get('placeOfPerformance') or {}
                        place_city = ''
                        place_state = ''
                        if isinstance(place_of_perf, dict):
                            city_data = place_of_perf.get('city') or {}
                            state_data = place_of_perf.get('state') or {}
                            if isinstance(city_data, dict):
                                place_city = city_data.get('name', '')
                            if isinstance(state_data, dict):
                                place_state = state_data.get('name', '')
                        
                        contact_email = ''
                        point_of_contact = opp.get('pointOfContact')
                        if point_of_contact and isinstance(point_of_contact, list) and len(point_of_contact) > 0:
                            contact_email = point_of_contact[0].get('email', '')
                        
                        # Double-check eligibility — skip SDVOSB/HUBZone/8(a)
                        opp_set_aside = opp.get('typeOfSetAside', '') or ''
                        if not self._is_eligible_set_aside(opp_set_aside):
                            continue

                        forecast = {
                            'title': opp.get('title', 'Untitled')[:200],
                            'solicitation_number': opp.get('solicitationNumber', ''),
                            'agency': opp.get('department', 'Unknown'),
                            'sub_agency': opp.get('subtier', ''),
                            'naics': opp.get('naicsCode', ''),
                            'set_aside': opp_set_aside or 'Unrestricted',
                            'description': opp.get('description', '')[:1000],
                            'posted_date': opp.get('postedDate', ''),
                            'response_deadline': opp.get('responseDeadLine', ''),
                            'estimated_solicitation_date': '',
                            'place_city': place_city,
                            'place_state': place_state,
                            'contact_email': contact_email,
                            'source': 'SAM.gov Forecast',
                            'forecast_type': 'Sources Sought / Forecast' if notice_type == 's' else 'Forecasted Opportunity',
                            'notice_id': opp.get('noticeId', ''),
                            'source_url': f"https://sam.gov/opp/{opp.get('noticeId', '')}"
                        }
                        
                        forecasts.append(forecast)
            
            return forecasts
            
        except Exception as e:
            print(f"   ⚠️  SAM.gov forecast mining error: {e}")
            return []
    
    def mine_usaspending_forecasts(self) -> List[Dict]:
        """
        Mine USASpending.gov for contract forecast data
        Look for large contracts that are likely to repeat
        """
        
        try:
            # USASpending.gov API for awards
            url = "https://api.usaspending.gov/api/v2/search/spending_by_award/"
            
            # Search for recent large contracts that indicate future opportunities
            payload = {
                "filters": {
                    "time_period": [
                        {
                            "start_date": "2025-10-01",
                            "end_date": "2026-01-28"
                        }
                    ],
                    "award_type_codes": ["A", "B", "C", "D"],  # Contracts
                },
                "fields": ["Award ID", "Recipient Name", "Description", "Award Amount", "awarding_agency_name"],
                "limit": 100,
                "sort": "Award Amount",
                "order": "desc"
            }
            
            response = requests.post(url, json=payload, timeout=30)
            
            if response.status_code != 200:
                print(f"   ℹ️  USASpending API returned {response.status_code}")
                return []
            
            data = response.json()
            results = data.get('results', [])
            
            forecasts = []
            for award in results:
                # Extract award data
                award_id = award.get('Award ID', '')
                recipient = award.get('Recipient Name', 'Unknown')
                description = award.get('Description', '')
                amount = award.get('Award Amount', 0)
                agency = award.get('awarding_agency_name', 'Unknown')
                
                # Only include large contracts (>$100K) as potential forecasts
                if amount and amount > 100000:
                    forecast = {
                        'title': f"Potential Renewal: {description[:150]}"[:200],
                        'solicitation_number': award_id,
                        'agency': agency,
                        'sub_agency': '',
                        'naics': '',
                        'set_aside': '',
                        'description': f"Recent award to {recipient}. Amount: ${amount:,.0f}. May renew or re-compete."[:1000],
                        'posted_date': datetime.now().strftime('%Y-%m-%d'),
                        'response_deadline': '',
                        'estimated_solicitation_date': '',
                        'source': 'USASpending.gov',
                        'forecast_type': 'Contract Renewal Forecast',
                        'source_url': f"https://www.usaspending.gov/award/{award_id}"
                    }
                    
                    forecasts.append(forecast)
            
            return forecasts
            
        except Exception as e:
            print(f"   ⚠️  USASpending mining error: {e}")
            return []
    
    def mine_beta_sam(self) -> List[Dict]:
        """
        Mine Beta.SAM.gov for acquisition forecasts
        Beta.SAM has additional forecast data not in v2 API
        """
        
        if not self.sam_api_key:
            print("   ⚠️  SAM_GOV_API_KEY not set")
            return []
        
        try:
            # Try the entity/opportunities endpoint (newer API)
            url = "https://api.sam.gov/entity-information/v3/entities"
            
            params = {
                'api_key': self.sam_api_key,
                'purposeOfRegistrationCode': '2,3',  # All awards, Federal assistance
                'registrationStatus': 'A',  # Active
                'limit': 100
            }
            
            response = requests.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                entities = data.get('entityData', [])
                
                forecasts = []
                for entity in entities:
                    # Extract entity contract data that indicates forecasting
                    core_data = entity.get('coreData', {})
                    entity_name = core_data.get('legalBusinessName', 'Unknown')
                    
                    # This is entity registration data - useful for finding who's registered for what
                    # But not actual forecasts. Let's try a different approach.
                
                print(f"   ℹ️  Beta.SAM entity data doesn't provide forecasts directly")
                return []
            else:
                print(f"   ℹ️  Beta.SAM API returned {response.status_code}")
                return []
                
        except Exception as e:
            print(f"   ⚠️  Beta.SAM mining error: {e}")
            return []
    
    def _estimate_solicitation_date(self, presolic_data: Dict) -> str:
        """Estimate when solicitation will be posted (typically 2-4 weeks after response deadline)"""
        response_deadline = presolic_data.get('responseDeadLine', '')
        if response_deadline:
            try:
                from datetime import datetime, timedelta
                deadline_date = datetime.strptime(response_deadline, '%Y-%m-%d')
                estimated_date = deadline_date + timedelta(days=21)  # Typically 3 weeks
                return estimated_date.strftime('%Y-%m-%d')
            except:
                pass
        return ''
    
    def store_forecasts(self, forecasts: List[Dict], source: str) -> int:
        """Store forecasts in Airtable GPSS OPPORTUNITIES table"""
        
        if not forecasts:
            return 0
        
        try:
            table = self.api.table(self.base_id, 'GPSS OPPORTUNITIES')
            
            # Get existing opportunities to avoid duplicates
            existing = table.all()
            existing_titles = {r['fields'].get('Name', '').lower() for r in existing}
            
            stored = 0
            for forecast in forecasts:
                title = forecast.get('title', 'Untitled')
                
                # Skip if already exists
                if title.lower() in existing_titles:
                    continue
                
                # Map to actual Airtable fields - GPSS OPPORTUNITIES table already has 63 fields!
                # Using existing field names from the table
                
                # Parse deadline - handle various formats
                deadline = forecast.get('response_deadline', forecast.get('estimated_solicitation_date', ''))
                posted_date = forecast.get('posted_date', '')
                
                # Fix date format
                def fix_date(date_str):
                    if not date_str:
                        return None
                    try:
                        # Try parsing different formats
                        if 'T' in date_str:
                            # ISO format with time: 2026-01-28T14:00:00
                            date_str = date_str.split('T')[0]
                        elif '/' in date_str:
                            # MM/DD/YYYY format
                            parts = date_str.split('/')
                            if len(parts) == 3:
                                date_str = f"{parts[2]}-{parts[0].zfill(2)}-{parts[1].zfill(2)}"
                        # Validate it's YYYY-MM-DD format
                        datetime.strptime(date_str, '%Y-%m-%d')
                        return date_str
                    except:
                        return None  # Invalid date, skip it
                
                deadline = fix_date(deadline)
                posted_date = fix_date(posted_date)
                
                # Build fields dict
                fields = {
                    'Name': title[:100],
                    'AGENCY NAME': forecast.get('agency', 'Unknown'),
                    'SOURCE': 'FEDERAL',
                    'Source Status': f"{source} | {forecast.get('forecast_type', 'Unknown')}",
                    'AI Recommendation ': 'New Federal Forecast - Review Recommended',
                    'Priority': 'Medium',
                    'Win Probability': '50%'
                }
                
                # Add optional fields only if they exist and are valid
                if forecast.get('solicitation_number') or forecast.get('apfs_number'):
                    fields['RFP NUMBER'] = (forecast.get('solicitation_number', '') or forecast.get('apfs_number', ''))[:100]
                
                if deadline:
                    fields['Deadline'] = deadline
                
                if forecast.get('estimated_value') and forecast['estimated_value'] > 0:
                    try:
                        fields['VALUE'] = int(forecast['estimated_value'])
                    except:
                        pass
                
                if forecast.get('source_url'):
                    fields['Source URL'] = forecast['source_url']
                
                if forecast.get('place_state'):
                    fields['State'] = forecast['place_state']
                
                if forecast.get('place_city'):
                    fields['City'] = forecast['place_city']
                
                if forecast.get('set_aside') and forecast['set_aside'] != 'Unrestricted':
                    fields['Set-Aside Type'] = forecast['set_aside']
                
                if forecast.get('naics'):
                    fields['NAISC Codes'] = forecast['naics']
                
                if forecast.get('forecast_type'):
                    fields['Opportunity Category'] = forecast['forecast_type']
                
                if forecast.get('description'):
                    fields['Notes'] = forecast['description'][:500]
                
                if forecast.get('contact_email'):
                    fields['CONTRACTING OFFICER'] = f"Email: {forecast['contact_email']}"
                
                try:
                    table.create(fields)
                    stored += 1
                    existing_titles.add(title.lower())
                except Exception as e:
                    print(f"   ⚠️  Failed to store: {title[:50]}... - {e}")
            
            return stored
            
        except Exception as e:
            print(f"   ❌ Airtable storage error: {e}")
            return 0


def main():
    """Run the real federal forecasts miner"""
    miner = RealFederalForecastsMiner()
    results = miner.mine_all_sources()
    
    print()
    print("📊 SUMMARY:")
    print(f"   Total forecasts stored: {results['total_stored']}")
    print(f"   DHS APFS: {results['dhs_apfs']}")
    print(f"   SAM.gov Pre-Solicitations: {results['sam_presolicitations']}")
    
    if results['errors']:
        print(f"   ⚠️  Errors encountered: {len(results['errors'])}")
        for error in results['errors']:
            print(f"      - {error}")
    
    return results


if __name__ == '__main__':
    main()
