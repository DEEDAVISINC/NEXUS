#!/usr/bin/env python3
"""
Search SAM.gov for EDWOSB and WOSB Set-Aside Opportunities
Filters for product opportunities and adds to NEXUS
"""

import requests
import json
from datetime import datetime, timedelta
import os

# SAM.gov API endpoint
SAM_API_BASE = "https://api.sam.gov/opportunities/v2/search"
SAM_API_KEY = os.environ.get('SAM_GOV_API_KEY', '')  # Get from environment if available

def search_edwosb_wosb_opportunities():
    """Search for EDWOSB and WOSB opportunities"""
    
    print("🔍 Searching SAM.gov for EDWOSB/WOSB Opportunities...")
    print("=" * 60)
    
    # Date range: Posted in last 7 days
    today = datetime.now()
    week_ago = today - timedelta(days=7)
    
    # Search parameters
    params = {
        'api_key': SAM_API_KEY,
        'postedFrom': week_ago.strftime('%m/%d/%Y'),
        'postedTo': today.strftime('%m/%d/%Y'),
        'ptype': 'o',  # Opportunities (not awards)
        'limit': 100,
    }
    
    all_opportunities = []
    
    # Search for EDWOSB
    print("\n📋 Searching for EDWOSB opportunities...")
    params['typeOfSetAside'] = 'EDWOSB'
    
    try:
        response = requests.get(SAM_API_BASE, params=params)
        if response.status_code == 200:
            data = response.json()
            opportunities = data.get('opportunitiesData', [])
            print(f"   Found {len(opportunities)} EDWOSB opportunities")
            all_opportunities.extend(opportunities)
        else:
            print(f"   ⚠️ Error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Search for WOSB
    print("\n📋 Searching for WOSB opportunities...")
    params['typeOfSetAside'] = 'WOSB'
    
    try:
        response = requests.get(SAM_API_BASE, params=params)
        if response.status_code == 200:
            data = response.json()
            opportunities = data.get('opportunitiesData', [])
            print(f"   Found {len(opportunities)} WOSB opportunities")
            all_opportunities.extend(opportunities)
        else:
            print(f"   ⚠️ Error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print(f"\n✅ Total opportunities found: {len(all_opportunities)}")
    print("=" * 60)
    
    # Filter and display results
    if all_opportunities:
        print("\n🎯 EDWOSB/WOSB OPPORTUNITIES:\n")
        
        for i, opp in enumerate(all_opportunities, 1):
            title = opp.get('title', 'Untitled')
            notice_id = opp.get('noticeId', 'N/A')
            sol_number = opp.get('solicitationNumber', 'N/A')
            type_of_set_aside = opp.get('typeOfSetAside', 'N/A')
            response_deadline = opp.get('responseDeadLine', 'N/A')
            office_address = opp.get('officeAddress', {})
            state = office_address.get('state', 'N/A')
            
            # Extract category
            naics = opp.get('naicsCode', '')
            description = opp.get('description', '')
            
            # Determine if product or service (basic heuristic)
            product_keywords = ['supply', 'supplies', 'equipment', 'materials', 'product', 
                              'goods', 'items', 'parts', 'components', 'hardware']
            is_product = any(keyword in title.lower() or keyword in description.lower() 
                           for keyword in product_keywords)
            
            category = "🔧 PRODUCT" if is_product else "🛠️ SERVICE"
            
            print(f"{i}. {category} | {type_of_set_aside}")
            print(f"   Title: {title}")
            print(f"   Solicitation: {sol_number}")
            print(f"   Deadline: {response_deadline}")
            print(f"   Location: {state}")
            print(f"   URL: https://sam.gov/opp/{notice_id}/view")
            print()
    
    else:
        print("\n❌ No EDWOSB/WOSB opportunities found in the last 7 days.")
        print("💡 Try searching on SAM.gov directly for more options.")
    
    return all_opportunities

def main():
    """Main execution"""
    if not SAM_API_KEY:
        print("⚠️  No SAM.gov API key found in environment")
        print("💡 Searching without API key (limited results)...\n")
    
    opportunities = search_edwosb_wosb_opportunities()
    
    print("\n" + "=" * 60)
    print("🎯 NEXT STEPS:")
    print("=" * 60)
    print("1. Review opportunities above")
    print("2. Visit SAM.gov URLs for full details")
    print("3. Identify product opportunities (🔧)")
    print("4. Add promising opportunities to NEXUS")
    print("\n💡 Focus on products you can source as VAR!")
    print()

if __name__ == "__main__":
    main()
