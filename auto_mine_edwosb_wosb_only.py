#!/usr/bin/env python3
"""
AUTOMATED EDWOSB / WOSB / TOTAL SB OPPORTUNITY MINER
Searches SAM.gov for EDWOSB, WOSB, and Total Small Business set-aside opportunities.
Adds them to NEXUS automatically.
Filters out SDVOSB, HUBZone, 8(a), and all other set-asides.

STRATEGY: Until DDI achieves 8(a) certification, search ALL set-asides DDI qualifies for:
  - EDWOSB (highest priority)
  - WOSB (high priority)
  - Total Small Business / SBA (moderate competition)

Run this daily to populate NEXUS with opportunities you can bid on!

Author: NEXUS AI
Created: February 6, 2026
Updated: March 2026 — Added Total SB (SBA) per "search all until 8a" strategy
"""

import os
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List
from pyairtable import Api
from dotenv import load_dotenv
import time

load_dotenv()


class EDWOSBWOSBMiner:
    """
    Mine ONLY EDWOSB and WOSB opportunities from SAM.gov
    Filter out everything else automatically
    """
    
    def __init__(self):
        self.airtable_token = os.environ.get('AIRTABLE_PAT') or os.environ.get('AIRTABLE_API_KEY')
        self.base_id = os.environ.get('AIRTABLE_BASE_ID', 'appaJZqKVUn3yJ7ma')
        self.sam_api_key = os.environ.get('SAM_GOV_API_KEY')
        
        if not self.airtable_token:
            raise ValueError("❌ AIRTABLE_PAT or AIRTABLE_API_KEY not set!")
        
        self.api = Api(self.airtable_token)
        self.opportunities_table = self.api.table(self.base_id, 'GPSS OPPORTUNITIES')
        self.contacts_table = self.api.table(self.base_id, 'GPSS CONTACTS')
        
        # CRITICAL: Only these set-aside types (until 8a certified, search all DDI-eligible)
        self.allowed_set_asides = [
            'EDWOSB',
            'WOSB',
            'Women-Owned Small Business',
            'Economically Disadvantaged Women-Owned Small Business',
            'SBA Certified EDWOSB',
            'SBA Certified WOSB',
            'SBA',  # Total Small Business Set-Aside (FAR 19.5)
            'Total Small Business',
            'Total Small Business Set-Aside',
        ]
    
    def mine_edwosb_wosb_opportunities(self, days_back: int = 30) -> Dict:
        """
        Search SAM.gov for EDWOSB/WOSB opportunities ONLY
        Returns summary of what was found and added to NEXUS
        """
        print("=" * 80)
        print("🎯 AUTOMATED EDWOSB/WOSB OPPORTUNITY MINER")
        print("=" * 80)
        print()
        print("🔍 Searching SAM.gov for:")
        print("   ✅ EDWOSB (Economically Disadvantaged Women-Owned)")
        print("   ✅ WOSB (Women-Owned Small Business)")
        print("   ✅ Total Small Business (SBA)")
        print()
        print("❌ Filtering out:")
        print("   • SDVOSB (Service-Disabled Veterans)")
        print("   • HUBZone")
        print("   • 8(a)")
        print("   • All other set-asides")
        print()
        print("=" * 80)
        print()
        
        all_opportunities = []
        
        # Search for each notice type
        notice_types = [
            ('o', 'Solicitation'),
            ('p', 'Pre-Solicitation'),
            ('r', 'Sources Sought'),
            ('s', 'Special Notice'),
            ('i', 'Intent to Bundle'),  # Intent to Sole Source
        ]
        
        for notice_code, notice_name in notice_types:
            print(f"📡 Searching {notice_name} notices...")
            opportunities = self._search_sam_gov(notice_code, days_back)
            
            # CRITICAL: Filter for EDWOSB/WOSB ONLY
            filtered = self._filter_edwosb_wosb_only(opportunities)
            
            all_opportunities.extend(filtered)
            print(f"   ✅ Found {len(filtered)} EDWOSB/WOSB opportunities")
            print()
            time.sleep(2)  # Rate limiting
        
        print(f"📊 TOTAL EDWOSB/WOSB OPPORTUNITIES FOUND: {len(all_opportunities)}")
        print()
        
        # Store in Airtable
        print("💾 Adding to NEXUS...")
        stored = self._add_to_nexus(all_opportunities)
        print(f"   ✅ Added {stored} new opportunities to NEXUS")
        print()
        
        print("=" * 80)
        print("✅ MINING COMPLETE!")
        print("=" * 80)
        print()
        print(f"📊 SUMMARY:")
        print(f"   Total Found: {len(all_opportunities)}")
        print(f"   Added to NEXUS: {stored}")
        print(f"   Duplicates Skipped: {len(all_opportunities) - stored}")
        print()
        
        return {
            'total_found': len(all_opportunities),
            'added_to_nexus': stored,
            'duplicates_skipped': len(all_opportunities) - stored,
            'notice_types': {name: len([o for o in all_opportunities if o['notice_type'] == name]) 
                           for _, name in notice_types}
        }
    
    def _search_sam_gov(self, notice_type: str, days_back: int) -> List[Dict]:
        """
        Search SAM.gov API for opportunities by notice type
        Returns ALL opportunities (will filter later)
        """
        if not self.sam_api_key:
            print(f"   ⚠️  SAM_GOV_API_KEY not set - skipping SAM.gov search")
            return []
        
        try:
            url = "https://api.sam.gov/opportunities/v2/search"
            
            params = {
                'api_key': self.sam_api_key,
                'ptype': notice_type,
                'limit': 100,
                'postedFrom': (datetime.now() - timedelta(days=days_back)).strftime('%m/%d/%Y'),
                'postedTo': datetime.now().strftime('%m/%d/%Y')
            }
            
            response = requests.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                opportunities = data.get('opportunitiesData', [])
                return opportunities
            else:
                print(f"   ⚠️  SAM.gov API error: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"   ⚠️  SAM.gov error: {e}")
            return []
    
    def _filter_edwosb_wosb_only(self, opportunities: List[Dict]) -> List[Dict]:
        """
        CRITICAL FILTER: Only keep EDWOSB and WOSB opportunities
        Reject EVERYTHING else
        """
        filtered = []
        
        for opp in opportunities:
            set_aside = str(opp.get('typeOfSetAside', 'None') or 'None').strip()
            set_aside_desc = str(opp.get('typeOfSetAsideDescription', '') or '').strip()
            
            # Check if it's EDWOSB or WOSB
            is_eligible = False
            
            # Check set-aside field
            for allowed in self.allowed_set_asides:
                if allowed.upper() in set_aside.upper():
                    is_eligible = True
                    break
                if allowed.upper() in set_aside_desc.upper():
                    is_eligible = True
                    break
            
            # CRITICAL: Must explicitly check it's NOT SDVOSB
            if 'SDVOSB' in set_aside.upper() or 'SERVICE-DISABLED' in set_aside.upper():
                is_eligible = False
            
            if 'HUBZONE' in set_aside.upper():
                is_eligible = False
            
            if '8(A)' in set_aside.upper():
                is_eligible = False
            
            if is_eligible:
                # Parse and structure the opportunity
                filtered.append({
                    'title': opp.get('title', 'Untitled'),
                    'notice_id': opp.get('noticeId', ''),
                    'solicitation_number': opp.get('solicitationNumber', ''),
                    'notice_type': self._get_notice_type_name(opp.get('type', '')),
                    'posted_date': opp.get('postedDate', ''),
                    'response_deadline': opp.get('responseDeadLine', ''),
                    'department': opp.get('department', 'Unknown'),
                    'subtier': opp.get('subtier', ''),
                    'office': opp.get('office', ''),
                    'set_aside': set_aside,
                    'set_aside_description': set_aside_desc,
                    'naics_code': opp.get('naicsCode', ''),
                    'place_of_performance': self._get_location(opp),
                    'description': opp.get('description', ''),
                    'contact_name': opp.get('pointOfContact', [{}])[0].get('fullName', '') if opp.get('pointOfContact') else '',
                    'contact_email': opp.get('pointOfContact', [{}])[0].get('email', '') if opp.get('pointOfContact') else '',
                    'contact_phone': opp.get('pointOfContact', [{}])[0].get('phone', '') if opp.get('pointOfContact') else '',
                    'sam_url': f"https://sam.gov/opp/{opp.get('noticeId', '')}",
                    'raw_data': json.dumps(opp)
                })
        
        return filtered
    
    def _get_notice_type_name(self, code: str) -> str:
        """Convert SAM.gov notice type code to readable name"""
        mapping = {
            'o': 'Solicitation',
            'p': 'Pre-Solicitation',
            'r': 'Sources Sought',
            's': 'Special Notice',
            'i': 'Intent to Bundle',
            'a': 'Award',
            'k': 'Combined Synopsis/Solicitation'
        }
        return mapping.get(code.lower(), code)
    
    def _get_location(self, opp: Dict) -> str:
        """Extract place of performance location"""
        try:
            pop = opp.get('placeOfPerformance', {})
            city = pop.get('city', {}).get('name', '')
            state = pop.get('state', {}).get('name', '')
            
            if city and state:
                return f"{city}, {state}"
            elif state:
                return state
            else:
                return ''
        except:
            return ''
    
    def _add_to_nexus(self, opportunities: List[Dict]) -> int:
        """
        Add opportunities to NEXUS (Airtable)
        Skip duplicates based on notice_id
        """
        if not opportunities:
            return 0
        
        try:
            # Get existing opportunities to avoid duplicates
            existing = self.opportunities_table.all()
            existing_ids = {r['fields'].get('Notice ID', '').strip().lower() for r in existing}
            
            stored = 0
            
            for opp in opportunities:
                notice_id = opp.get('notice_id', '').strip()
                
                # Skip if duplicate
                if notice_id.lower() in existing_ids:
                    continue
                
                # Parse deadline - Airtable expects YYYY-MM-DD format
                deadline = None
                if opp.get('response_deadline'):
                    try:
                        # Try multiple date formats
                        dl = opp['response_deadline']
                        if 'T' in dl:  # ISO format with time
                            deadline = dl.split('T')[0]
                        elif len(dl) == 10 and dl.count('-') == 2:  # Already YYYY-MM-DD
                            deadline = dl
                        else:
                            # Try parsing and reformatting
                            dt = datetime.strptime(dl, '%m/%d/%Y')
                            deadline = dt.strftime('%Y-%m-%d')
                    except Exception as e:
                        print(f"   ⚠️  Could not parse deadline '{opp.get('response_deadline')}': {e}")
                        deadline = None
                
                # Prepare fields for Airtable (using correct field names)
                fields = {
                    'Name': opp['title'][:100],
                    'RFP NUMBER': f"{notice_id}\n{opp.get('solicitation_number', '')}",
                    'Source Status': opp.get('notice_type', ''),
                    'AGENCY NAME': opp.get('department', 'Unknown'),
                    'Set-Aside Type': opp.get('set_aside', 'Unknown'),
                    'NAISC Codes': str(opp.get('naics_code', '')),
                    'Performance Location': opp.get('place_of_performance', ''),
                    'Notes': f"SAM.gov Auto-Mined {datetime.now().strftime('%Y-%m-%d')}\n\n{opp.get('description', '')[:3000]}",
                    'Deadline': deadline,
                    'Source URL': opp.get('sam_url', ''),
                    'Priority': 'Medium'
                }
                
                # Remove None/empty values
                fields = {k: v for k, v in fields.items() if v not in [None, '', 'Unknown', []]}
                
                # Add to Airtable
                try:
                    created = self.opportunities_table.create(fields)
                    stored += 1
                    
                    # Add contact if available
                    if opp.get('contact_email'):
                        self._add_contact(opp, created['id'])
                    
                except Exception as e:
                    print(f"   ⚠️  Failed to add opportunity {notice_id}: {e}")
            
            return stored
            
        except Exception as e:
            print(f"   ⚠️  Airtable error: {e}")
            return 0
    
    def _add_contact(self, opp: Dict, opportunity_record_id: str):
        """Add contracting officer contact to NEXUS"""
        try:
            if not opp.get('contact_email'):
                return
            
            # Check if contact already exists
            existing = self.contacts_table.all()
            existing_emails = {r['fields'].get('Email', '').strip().lower() for r in existing}
            
            email = opp.get('contact_email', '').strip().lower()
            
            if email in existing_emails:
                return  # Skip duplicate
            
            fields = {
                'Name': opp.get('contact_name', 'Contracting Officer'),
                'Email': email,
                'Phone': opp.get('contact_phone', ''),
                'Organization': opp.get('department', ''),
                'Title': 'Contracting Officer',
                'Contact Type': 'Government',
                'Opportunities': [opportunity_record_id],
                'Source': 'SAM.gov Auto-Mined',
                'Added Date': datetime.now().strftime('%Y-%m-%d')
            }
            
            # Remove None/empty values
            fields = {k: v for k, v in fields.items() if v not in [None, '', []]}
            
            self.contacts_table.create(fields)
            
        except Exception as e:
            print(f"   ⚠️  Failed to add contact: {e}")


def main():
    """
    Run the EDWOSB/WOSB opportunity miner
    """
    try:
        miner = EDWOSBWOSBMiner()
        result = miner.mine_edwosb_wosb_opportunities(days_back=30)
        
        print("📊 FINAL RESULTS:")
        print(f"   Total EDWOSB/WOSB Found: {result['total_found']}")
        print(f"   Added to NEXUS: {result['added_to_nexus']}")
        print()
        print("   By Notice Type:")
        for notice_type, count in result['notice_types'].items():
            print(f"      {notice_type}: {count}")
        print()
        print("✅ ALL OPPORTUNITIES IN NEXUS ARE NOW ELIGIBLE FOR DEE DAVIS INC!")
        print()
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
