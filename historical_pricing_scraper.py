#!/usr/bin/env python3
"""
HISTORICAL PRICING SCRAPER
Find pricing from previous government contracts
"""

import requests
from datetime import datetime, timedelta
import json


class HistoricalPricingScraper:
    """Scrape historical pricing from government sources"""
    
    def __init__(self):
        self.usaspending_base = "https://api.usaspending.gov/api/v2"
    
    def search_similar_contracts(
        self,
        service_type: str,
        naics_code: str = None,
        psc_code: str = None,
        min_value: float = None,
        max_value: float = None,
        years_back: int = 3
    ) -> list:
        """
        Search USASpending for similar contracts to benchmark pricing.
        
        Args:
            service_type: Description of service (e.g., "medical courier")
            naics_code: NAICS code to filter by
            psc_code: PSC code to filter by
            min_value: Minimum contract value
            max_value: Maximum contract value
            years_back: How many years to search back
        
        Returns:
            List of similar contracts with pricing data
        """
        
        # Build search filters
        filters = {
            'time_period': [{
                'start_date': (datetime.now() - timedelta(days=365*years_back)).strftime('%Y-%m-%d'),
                'end_date': datetime.now().strftime('%Y-%m-%d')
            }],
            'award_type_codes': ['A', 'B', 'C', 'D']  # Contract types
        }
        
        if naics_code:
            filters['naics_codes'] = [naics_code]
        
        if psc_code:
            filters['psc_codes'] = [psc_code]
        
        if service_type:
            filters['keywords'] = [service_type]
        
        if min_value or max_value:
            filters['award_amounts'] = []
            if min_value:
                filters['award_amounts'].append({'lower_bound': min_value})
            if max_value:
                filters['award_amounts'].append({'upper_bound': max_value})
        
        # Make API request
        try:
            response = requests.post(
                f"{self.usaspending_base}/search/spending_by_award/",
                json={
                    'filters': filters,
                    'fields': [
                        'Award ID',
                        'Recipient Name',
                        'Award Amount',
                        'Awarding Agency',
                        'Awarding Sub Agency',
                        'Award Type',
                        'Description',
                        'Start Date',
                        'End Date',
                        'Place of Performance State Code',
                        'Contract Award Type'
                    ],
                    'limit': 100,
                    'page': 1,
                    'sort': 'Award Amount',
                    'order': 'desc'
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                results = data.get('results', [])
                
                # Parse and format results
                contracts = []
                for award in results:
                    contracts.append({
                        'recipient': award.get('Recipient Name', 'Unknown'),
                        'amount': award.get('Award Amount', 0),
                        'agency': award.get('Awarding Agency', 'Unknown'),
                        'sub_agency': award.get('Awarding Sub Agency', ''),
                        'description': award.get('Description', 'No description'),
                        'start_date': award.get('Start Date', 'Unknown'),
                        'end_date': award.get('End Date', 'Unknown'),
                        'award_id': award.get('Award ID', 'Unknown'),
                        'state': award.get('Place of Performance State Code', ''),
                        'contract_type': award.get('Contract Award Type', '')
                    })
                
                return contracts
            else:
                print(f"API Error: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"Error searching contracts: {e}")
            return []
    
    def estimate_unit_pricing(
        self,
        total_contract_value: float,
        contract_duration_years: float,
        estimated_annual_volume: int,
        service_type: str
    ) -> dict:
        """
        Estimate per-unit pricing from total contract value.
        
        Args:
            total_contract_value: Total contract award amount
            contract_duration_years: Contract length in years
            estimated_annual_volume: Estimated units per year (shipments, tests, etc.)
            service_type: Type of service
        
        Returns:
            Dict with estimated per-unit pricing
        
        Example:
            >>> estimate_unit_pricing(350000, 5, 1000, 'medical courier')
            {
                'total_value': 350000,
                'annual_value': 70000,
                'annual_volume': 1000,
                'estimated_per_unit': 70.00,
                'notes': 'Estimated from total contract value'
            }
        """
        
        annual_value = total_contract_value / contract_duration_years
        per_unit = annual_value / estimated_annual_volume if estimated_annual_volume > 0 else 0
        
        return {
            'total_value': total_contract_value,
            'duration_years': contract_duration_years,
            'annual_value': round(annual_value, 2),
            'annual_volume': estimated_annual_volume,
            'estimated_per_unit': round(per_unit, 2),
            'service_type': service_type,
            'notes': 'Estimated from total contract value (actual unit pricing not public)'
        }
    
    def generate_foia_request_template(
        self,
        solicitation_number: str,
        agency_name: str,
        contract_title: str,
        award_date: str = None
    ) -> str:
        """
        Generate FOIA request template for bid pricing.
        
        Args:
            solicitation_number: RFP/RFQ/ITB number
            agency_name: Government agency name
            contract_title: Title of the contract
            award_date: Date contract was awarded (if known)
        
        Returns:
            Formatted FOIA request letter
        """
        
        template = f"""
FREEDOM OF INFORMATION ACT (FOIA) REQUEST

To: {agency_name}
    FOIA Officer / Procurement Department

Date: {datetime.now().strftime('%B %d, %Y')}

Subject: FOIA Request for Bid Pricing — Solicitation {solicitation_number}

Dear FOIA Officer,

Pursuant to the Freedom of Information Act (5 U.S.C. § 552) and/or applicable state public records laws, I am requesting copies of the following records:

**Solicitation Number:** {solicitation_number}
**Contract Title:** {contract_title}
"""
        
        if award_date:
            template += f"**Award Date:** {award_date}\n"
        
        template += """
**Records Requested:**

1. All bids/proposals received in response to this solicitation, including:
   - Technical proposals
   - Cost proposals / pricing sheets
   - Line-item pricing for all bidders
   
2. Bid tabulation sheet showing:
   - All bidders
   - Bid amounts
   - Evaluation scores (if applicable)
   
3. Contract award documentation:
   - Award letter
   - Final negotiated pricing
   - Contract terms and conditions

**Purpose:** Market research for competitive pricing analysis.

**Preferred Format:** Electronic (PDF) via email to info@deedavis.biz

**Fee Waiver Request:** As a small business conducting market research, I request a waiver of any fees associated with this request. If fees cannot be waived, please notify me if costs will exceed $50 before processing.

If you have any questions or need clarification, please contact me at:

Dee Davis
Dee Davis Inc.
248.376.4550
info@deedavis.biz

Thank you for your assistance.

Sincerely,

Dee Davis
President & CEO
Dee Davis Inc.
"""
        
        return template


def search_ohio_medical_courier_pricing():
    """Example: Search for Ohio medical courier contract pricing"""
    
    scraper = HistoricalPricingScraper()
    
    print("\n" + "="*80)
    print("SEARCHING USASPENDING FOR OHIO MEDICAL COURIER CONTRACTS")
    print("="*80)
    print("\nSearching for contracts similar to Ohio DOH Medical Courier...")
    print("Filters: NAICS 492110 (Couriers), PSC Q301/R602 (Medical Services/Courier)")
    print("Value range: $50K - $150K")
    print("Years: 2021-2026")
    print()
    
    # Search by NAICS
    results = scraper.search_similar_contracts(
        service_type="medical courier",
        naics_code="492110",
        min_value=50000,
        max_value=150000,
        years_back=5
    )
    
    if results:
        print(f"✅ Found {len(results)} similar contracts\n")
        print("-" * 80)
        
        for i, contract in enumerate(results[:10], 1):
            print(f"\n{i}. {contract['recipient']}")
            print(f"   Agency: {contract['agency']}")
            print(f"   Amount: ${contract['amount']:,.2f}")
            print(f"   Period: {contract['start_date']} to {contract['end_date']}")
            desc = contract.get('description') or 'No description'
            print(f"   Description: {desc[:100]}...")
            
            # Estimate per-shipment cost (assuming 1000 shipments/year, 3-year contract)
            if contract['amount'] > 0:
                estimate = scraper.estimate_unit_pricing(
                    total_contract_value=contract['amount'],
                    contract_duration_years=3,
                    estimated_annual_volume=1000,
                    service_type='medical courier'
                )
                print(f"   Estimated: ${estimate['estimated_per_unit']:.2f} per shipment (if 1000/year)")
        
        print("\n" + "-" * 80)
        print("\n💡 USE THIS DATA TO:")
        print("  - Validate your subcontractor's quote")
        print("  - Understand market pricing")
        print("  - Ensure your bid is competitive")
        
    else:
        print("❌ No contracts found with these filters")
        print("\n💡 TRY:")
        print("  - Broader search (remove value filters)")
        print("  - Different NAICS/PSC codes")
        print("  - FOIA request to Ohio DOH for incumbent pricing")
    
    print("\n" + "="*80)
    
    # Generate FOIA template
    print("\n📄 FOIA REQUEST TEMPLATE FOR OHIO DOH INCUMBENT PRICING")
    print("="*80)
    
    foia = scraper.generate_foia_request_template(
        solicitation_number="SRC0000036969 / DOH59579",
        agency_name="Ohio Department of Health",
        contract_title="Medical Specimen and Specimen Supply Courier Services"
    )
    
    print(foia)
    print("="*80)
    print("\n💡 SAVE THIS AS: FOIA_REQUEST_OHIO_DOH_COURIER.txt")
    print("   Send to: Ohio DOH FOIA Officer (find contact on ODH website)")
    print("="*80 + "\n")


if __name__ == "__main__":
    search_ohio_medical_courier_pricing()
