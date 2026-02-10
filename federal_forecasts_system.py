#!/usr/bin/env python3
"""
FEDERAL FORECASTS MINING SYSTEM
Pulls REAL federal procurement forecasts from government sources

Data Sources:
1. SAM.gov API - Pre-solicitation notices (near-term forecasts)
2. NASA Forecast Page - https://www.hq.nasa.gov/office/procurement/forecast/
3. GSA Forecast Page - https://www.gsa.gov/small-business/forecast-of-contracting-opportunities
4. DHS Forecast System - https://apfs-cloud.dhs.gov/
5. USAID Business Forecast - https://www.usaid.gov/business-forecast
6. Commerce Forecasts - https://www.commerce.gov/oam/industry/procurement-forecasts
7. Treasury Forecasts - https://sbecs.treas.gov/Forecast

Author: NEXUS AI
Created: January 28, 2026
"""

import os
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pyairtable import Api
from dotenv import load_dotenv
import anthropic
from bs4 import BeautifulSoup
import time

load_dotenv()


class FederalForecastsMiner:
    """
    Mine REAL federal procurement forecasts from official government sources
    These are actual agency announcements of upcoming procurements
    """
    
    def __init__(self):
        self.airtable_token = os.environ.get('AIRTABLE_API_KEY')
        self.base_id = os.environ.get('AIRTABLE_BASE_ID')
        self.sam_api_key = os.environ.get('SAM_GOV_API_KEY')
        self.anthropic_key = os.environ.get('ANTHROPIC_API_KEY')
        
        self.api = Api(self.airtable_token)
        self.ai = anthropic.Anthropic(api_key=self.anthropic_key)
        
        # Agency forecast URLs
        self.forecast_sources = {
            'NASA': 'https://www.hq.nasa.gov/office/procurement/forecast/',
            'GSA': 'https://www.gsa.gov/small-business/forecast-of-contracting-opportunities',
            'DHS': 'https://apfs-cloud.dhs.gov/',
            'USAID': 'https://www.usaid.gov/business-forecast',
            'Commerce': 'https://www.commerce.gov/oam/industry/procurement-forecasts',
            'Treasury': 'https://sbecs.treas.gov/Forecast'
        }
    
    def mine_all_forecasts(self) -> Dict:
        """
        Mine forecasts from all sources
        Returns summary of forecasts found and stored
        """
        print("🔮 FEDERAL FORECASTS MINING SYSTEM")
        print("=" * 70)
        print()
        
        all_forecasts = []
        
        # 1. Mine SAM.gov pre-solicitation notices (best source)
        print("📡 Mining SAM.gov pre-solicitation notices...")
        sam_forecasts = self._mine_sam_presolicitations()
        all_forecasts.extend(sam_forecasts)
        print(f"   ✅ Found {len(sam_forecasts)} pre-solicitation notices")
        print()
        
        # 2. Mine agency forecast pages
        for agency, url in self.forecast_sources.items():
            print(f"📡 Mining {agency} forecast page...")
            try:
                agency_forecasts = self._scrape_agency_forecast_page(agency, url)
                all_forecasts.extend(agency_forecasts)
                print(f"   ✅ Found {len(agency_forecasts)} forecasts from {agency}")
            except Exception as e:
                print(f"   ⚠️  Error mining {agency}: {e}")
            print()
            time.sleep(2)  # Respectful rate limiting
        
        # 3. Store in Airtable
        print(f"💾 Storing {len(all_forecasts)} forecasts in Airtable...")
        stored_count = self._store_forecasts_in_airtable(all_forecasts)
        print(f"   ✅ Stored {stored_count} new forecasts")
        print()
        
        # 4. Match to capabilities and alert
        print("🎯 Analyzing forecasts for fit...")
        matches = self._analyze_and_match_forecasts()
        print(f"   ✅ Found {matches} high-fit forecasts")
        print()
        
        print("=" * 70)
        print(f"✅ COMPLETE: {len(all_forecasts)} forecasts mined, {stored_count} stored, {matches} matched")
        
        return {
            'total_mined': len(all_forecasts),
            'stored': stored_count,
            'high_fit_matches': matches,
            'sources': {
                'sam_gov': len(sam_forecasts),
                **{agency: len([f for f in all_forecasts if f.get('agency') == agency]) 
                   for agency in self.forecast_sources.keys()}
            }
        }
    
    def _mine_sam_presolicitations(self) -> List[Dict]:
        """
        Mine pre-solicitation notices from SAM.gov API
        These are essentially near-term forecasts (upcoming opportunities)
        """
        if not self.sam_api_key:
            print("   ⚠️  SAM_GOV_API_KEY not set - skipping SAM.gov")
            return []
        
        try:
            url = "https://api.sam.gov/opportunities/v2/search"
            
            # Search for pre-solicitation notices (type: p)
            params = {
                'api_key': self.sam_api_key,
                'ptype': 'p',  # Pre-solicitation
                'limit': 100,
                'postedFrom': (datetime.now() - timedelta(days=30)).strftime('%m/%d/%Y'),
                'postedTo': datetime.now().strftime('%m/%d/%Y')
            }
            
            response = requests.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                opportunities = data.get('opportunitiesData', [])
                
                forecasts = []
                for opp in opportunities:
                    forecast = {
                        'title': opp.get('title', 'Untitled'),
                        'agency': opp.get('department', 'Unknown'),
                        'sub_agency': opp.get('subtier', ''),
                        'naics_code': opp.get('naicsCode', ''),
                        'set_aside': opp.get('typeOfSetAside', 'Unrestricted'),
                        'place_of_performance': opp.get('placeOfPerformance', {}).get('city', {}).get('name', ''),
                        'state': opp.get('placeOfPerformance', {}).get('state', {}).get('name', ''),
                        'description': opp.get('description', ''),
                        'posted_date': opp.get('postedDate', ''),
                        'response_deadline': opp.get('responseDeadLine', ''),
                        'solicitation_number': opp.get('solicitationNumber', ''),
                        'contract_type': opp.get('type', ''),
                        'source': 'SAM.gov Pre-Solicitation',
                        'source_url': f"https://sam.gov/opp/{opp.get('noticeId', '')}",
                        'forecast_type': 'Near-Term (Pre-Solicitation)',
                        'estimated_solicitation_date': self._estimate_solicitation_date(opp),
                        'raw_data': json.dumps(opp)
                    }
                    forecasts.append(forecast)
                
                return forecasts
            else:
                print(f"   ⚠️  SAM.gov API error: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"   ⚠️  SAM.gov error: {e}")
            return []
    
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


def handle_mine_federal_forecasts() -> Dict:
    """
    Handler function for NEXUS backend integration
    Mine federal forecasts and return summary
    """
    miner = FederalForecastsMiner()
    return miner.mine_all_forecasts()


if __name__ == '__main__':
    """
    Test the federal forecasts system
    """
    print("🔮 FEDERAL FORECASTS MINING SYSTEM TEST\n")
    
    miner = FederalForecastsMiner()
    result = miner.mine_all_forecasts()
    
    print("\n📊 FINAL RESULTS:")
    print(f"   Total Forecasts Mined: {result['total_mined']}")
    print(f"   Stored in Airtable: {result['stored']}")
    print(f"   High-Fit Matches: {result['high_fit_matches']}")
    print("\n   Breakdown by Source:")
    for source, count in result['sources'].items():
        print(f"      {source}: {count}")
    
    print("\n✅ Federal Forecasts System Ready!")
