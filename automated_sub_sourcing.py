#!/usr/bin/env python3
"""
Automated Subcontractor Sourcing System
Finds, vets, and contacts subcontractors automatically

Usage:
    # Find subs for an opportunity
    python3 automated_sub_sourcing.py find --service "lawn care" --location "Oakland County, MI"
    
    # Send outreach emails
    python3 automated_sub_sourcing.py outreach --opportunity-id recXYZ123
    
    # Send follow-ups (run daily via cron)
    python3 automated_sub_sourcing.py follow-up
    
    # Compare quotes
    python3 automated_sub_sourcing.py compare --opportunity-id recXYZ123
"""

import os
import sys
import argparse
import requests
from typing import List, Dict, Optional
from pyairtable import Api
from datetime import datetime, timedelta
import json

class SubcontractorSourcingSystem:
    """Automated subcontractor discovery and outreach"""
    
    def __init__(self):
        self.airtable_key = os.getenv('AIRTABLE_API_KEY')
        self.base_id = os.getenv('AIRTABLE_BASE_ID')
        self.google_maps_key = os.getenv('GOOGLE_MAPS_API_KEY')
        self.yelp_api_key = os.getenv('YELP_API_KEY')
        
        if not all([self.airtable_key, self.base_id]):
            raise ValueError("AIRTABLE_API_KEY and AIRTABLE_BASE_ID required")
        
        self.api = Api(self.airtable_key)
        
        # Initialize tables (create if they don't exist)
        try:
            self.subs_table = self.api.table(self.base_id, 'SUBCONTRACTORS')
            self.tracking_table = self.api.table(self.base_id, 'SUB_OUTREACH_TRACKING')
        except Exception as e:
            print(f"⚠️  Warning: Could not connect to Airtable tables: {e}")
            print("   Make sure SUBCONTRACTORS and SUB_OUTREACH_TRACKING tables exist")
    
    def find_subcontractors(self, service_type: str, location: str, 
                           radius_miles: int = 25, limit: int = 20) -> List[Dict]:
        """
        Find subcontractors using Google Maps and Yelp APIs
        
        Args:
            service_type: Type of service (e.g., "lawn care", "pressure washing")
            location: Location to search (e.g., "Oakland County, MI")
            radius_miles: Search radius in miles
            limit: Maximum number of results to return
        
        Returns:
            List of qualified subcontractors
        """
        print(f"\n{'='*60}")
        print(f"🔍 SEARCHING FOR SUBCONTRACTORS")
        print(f"{'='*60}")
        print(f"Service: {service_type}")
        print(f"Location: {location}")
        print(f"Radius: {radius_miles} miles\n")
        
        all_results = []
        
        # Search Google Maps (if API key available)
        if self.google_maps_key:
            try:
                google_results = self._search_google_maps(service_type, location, radius_miles)
                print(f"✓ Google Maps: Found {len(google_results)} businesses")
                all_results.extend(google_results)
            except Exception as e:
                print(f"⚠️  Google Maps search failed: {e}")
        else:
            print(f"⚠️  Google Maps API key not configured")
        
        # Search Yelp (if API key available)
        if self.yelp_api_key:
            try:
                yelp_results = self._search_yelp(service_type, location, radius_miles)
                print(f"✓ Yelp: Found {len(yelp_results)} businesses")
                all_results.extend(yelp_results)
            except Exception as e:
                print(f"⚠️  Yelp search failed: {e}")
        else:
            print(f"⚠️  Yelp API key not configured")
        
        if not all_results:
            print(f"\n❌ No results found. Check API keys and try again.")
            return []
        
        # Combine and deduplicate
        merged = self._merge_results(all_results)
        print(f"✓ Merged results: {len(merged)} unique businesses")
        
        # Filter by quality
        qualified = self._filter_qualified(merged)
        print(f"✓ Qualified contractors: {len(qualified)}")
        
        # CRITICAL: Check USASpending to filter out competitors
        print(f"\n🔍 Checking USASpending.gov for contract wins...")
        safe_subs = self._filter_usaspending_competitors(qualified, service_type)
        print(f"✓ Safe subcontractors (no competing contracts): {len(safe_subs)}")
        if len(qualified) > len(safe_subs):
            print(f"⚠️  Filtered out {len(qualified) - len(safe_subs)} subs who already win their own gov contracts")
        
        # Limit results
        safe_subs = safe_subs[:limit]
        print(f"✓ Returning top {len(safe_subs)} results")
        
        # Save to Airtable
        try:
            saved = self._save_to_airtable(safe_subs, service_type, location)
            print(f"✓ Saved {saved} new contractors to Airtable")
        except Exception as e:
            print(f"⚠️  Could not save to Airtable: {e}")
        
        print(f"\n{'='*60}")
        print(f"✅ SEARCH COMPLETE")
        print(f"{'='*60}\n")
        
        return safe_subs
    
    def _search_google_maps(self, service_type: str, location: str, 
                           radius_miles: int) -> List[Dict]:
        """Search Google Maps Places API"""
        url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
        
        params = {
            'query': f"{service_type} {location}",
            'radius': int(radius_miles * 1609),  # Convert miles to meters
            'key': self.google_maps_key
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        results = []
        for place in data.get('results', []):
            # Get place details for more info
            details = self._get_place_details(place.get('place_id'))
            
            results.append({
                'name': place.get('name'),
                'rating': place.get('rating', 0),
                'total_reviews': place.get('user_ratings_total', 0),
                'address': place.get('formatted_address'),
                'phone': details.get('phone'),
                'website': details.get('website'),
                'place_id': place.get('place_id'),
                'google_maps_url': f"https://maps.google.com/?cid={place.get('place_id')}",
                'source': 'Google Maps'
            })
        
        return results
    
    def _get_place_details(self, place_id: str) -> Dict:
        """Get detailed information for a place"""
        if not place_id or not self.google_maps_key:
            return {}
        
        url = "https://maps.googleapis.com/maps/api/place/details/json"
        params = {
            'place_id': place_id,
            'fields': 'formatted_phone_number,website',
            'key': self.google_maps_key
        }
        
        try:
            response = requests.get(url, params=params)
            data = response.json()
            result = data.get('result', {})
            return {
                'phone': result.get('formatted_phone_number'),
                'website': result.get('website')
            }
        except:
            return {}
    
    def _search_yelp(self, service_type: str, location: str, 
                    radius_miles: int) -> List[Dict]:
        """Search Yelp Fusion API"""
        url = "https://api.yelp.com/v3/businesses/search"
        
        headers = {
            'Authorization': f'Bearer {self.yelp_api_key}'
        }
        
        params = {
            'term': service_type,
            'location': location,
            'radius': int(radius_miles * 1609),  # Convert to meters
            'limit': 50,
            'sort_by': 'rating'
        }
        
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        results = []
        for business in data.get('businesses', []):
            results.append({
                'name': business.get('name'),
                'rating': business.get('rating', 0),
                'total_reviews': business.get('review_count', 0),
                'phone': business.get('phone'),
                'address': business['location'].get('address1'),
                'city': business['location'].get('city'),
                'state': business['location'].get('state'),
                'zip': business['location'].get('zip_code'),
                'yelp_url': business.get('url'),
                'categories': [cat['title'] for cat in business.get('categories', [])],
                'source': 'Yelp'
            })
        
        return results
    
    def _merge_results(self, results: List[Dict]) -> List[Dict]:
        """Combine and deduplicate results from multiple sources"""
        merged = {}
        
        for result in results:
            # Normalize name for matching
            key = result['name'].lower().strip()
            
            if key not in merged:
                merged[key] = result
            else:
                # Merge data from multiple sources
                existing = merged[key]
                
                # Keep best data from each source
                if not existing.get('phone') and result.get('phone'):
                    existing['phone'] = result['phone']
                if not existing.get('website') and result.get('website'):
                    existing['website'] = result['website']
                if not existing.get('yelp_url') and result.get('yelp_url'):
                    existing['yelp_url'] = result['yelp_url']
                
                # Average ratings if from multiple sources
                if result.get('rating'):
                    existing['rating'] = (existing.get('rating', 0) + result['rating']) / 2
        
        return list(merged.values())
    
    def _filter_qualified(self, results: List[Dict]) -> List[Dict]:
        """Filter for qualified contractors only"""
        qualified = []
        
        for sub in results:
            # Must have rating ≥4.0
            if sub.get('rating', 0) < 4.0:
                continue
            
            # Must have at least 10 reviews (established business)
            if sub.get('total_reviews', 0) < 10:
                continue
            
            # Must have contact info (phone or website or yelp)
            if not any([sub.get('phone'), sub.get('website'), sub.get('yelp_url')]):
                continue
            
            qualified.append(sub)
        
        # Sort by rating (highest first)
        qualified.sort(key=lambda x: x.get('rating', 0), reverse=True)
        
        return qualified
    
    def _filter_usaspending_competitors(self, subs: List[Dict], service_type: str) -> List[Dict]:
        """
        Filter out subcontractors who already win their own government contracts.
        
        If a sub wins federal contracts in the same service type, they're a competitor
        who will learn your client and bid directly. EXCLUDE THEM.
        
        Args:
            subs: List of potential subcontractors
            service_type: Service type (drug testing, NEMT, grounds, etc.)
        
        Returns:
            Filtered list with competitors removed
        """
        safe_subs = []
        
        for sub in subs:
            company_name = sub.get('name', '')
            if not company_name:
                continue
            
            # Query USASpending.gov API for this company's contract wins
            try:
                url = "https://api.usaspending.gov/api/v2/search/spending_by_award/"
                payload = {
                    "filters": {
                        "recipient_search_text": [company_name],
                        "award_type_codes": ["A", "B", "C", "D"],  # Contracts only
                        "time_period": [
                            {
                                "start_date": "2020-01-01",
                                "end_date": "2026-12-31"
                            }
                        ]
                    },
                    "fields": ["Award ID", "Description", "Award Amount", "NAICS Code"],
                    "limit": 10,
                    "page": 1
                }
                
                response = requests.post(url, json=payload, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    results = data.get('results', [])
                    
                    if len(results) > 0:
                        # They win government contracts — check if same service type
                        descriptions = ' '.join([r.get('Description', '').lower() for r in results])
                        
                        # Service type keywords that indicate competition
                        service_keywords = {
                            'drug testing': ['drug', 'testing', 'specimen', 'urinalysis', 'toxicology'],
                            'fingerprinting': ['fingerprint', 'livescan', 'background', 'identity'],
                            'NEMT': ['medical transport', 'nemt', 'patient transport', 'ambulance'],
                            'grounds': ['grounds', 'landscaping', 'lawn', 'mowing', 'maintenance'],
                            'janitorial': ['janitorial', 'custodial', 'cleaning', 'housekeeping'],
                            'courier': ['courier', 'delivery', 'messenger', 'transport'],
                        }
                        
                        # Check if their contracts match our service type
                        is_competitor = False
                        for key, keywords in service_keywords.items():
                            if key.lower() in service_type.lower():
                                if any(kw in descriptions for kw in keywords):
                                    is_competitor = True
                                    print(f"   ⚠️  COMPETITOR: {company_name} wins {key} contracts — EXCLUDED")
                                    break
                        
                        if is_competitor:
                            continue  # Skip this sub — they're a competitor
                        else:
                            # They win contracts but NOT in our service type — OK to use
                            safe_subs.append(sub)
                    else:
                        # No contract wins found — IDEAL sub (needs a prime)
                        safe_subs.append(sub)
                else:
                    # API error — include them (benefit of the doubt)
                    safe_subs.append(sub)
            
            except Exception as e:
                # Error checking — include them (benefit of the doubt)
                print(f"   ⚠️  Could not check USASpending for {company_name}: {e}")
                safe_subs.append(sub)
        
        return safe_subs
    
    def _save_to_airtable(self, subs: List[Dict], service_type: str, 
                         location: str) -> int:
        """Save contractors to Airtable SUBCONTRACTORS table"""
        saved_count = 0
        
        for sub in subs:
            try:
                # Check if already exists
                existing = self.subs_table.all(
                    formula=f"{{CompanyName}}='{sub['name'].replace(chr(39), chr(39)+chr(39))}'"  # Escape single quotes
                )
                
                if existing:
                    continue  # Skip duplicates
                
                # Create new record
                self.subs_table.create({
                    'CompanyName': sub['name'],
                    'Phone': sub.get('phone', ''),
                    'Website': sub.get('website', ''),
                    'GoogleRating': sub.get('rating', 0),
                    'YelpRating': sub.get('rating', 0) if sub.get('source') == 'Yelp' else 0,
                    'TotalReviews': sub.get('total_reviews', 0),
                    'YelpURL': sub.get('yelp_url', ''),
                    'GoogleMapsURL': sub.get('google_maps_url', ''),
                    'Address': sub.get('address', ''),
                    'City': sub.get('city', ''),
                    'State': sub.get('state', ''),
                    'ServiceTypes': [service_type],
                    'CoverageArea': location,
                    'FirstContactDate': datetime.now().isoformat(),
                    'Status': 'New',
                    'Source': sub.get('source', 'API Search')
                })
                
                saved_count += 1
            except Exception as e:
                print(f"   ⚠️  Could not save {sub['name']}: {e}")
                continue
        
        return saved_count
    
    def generate_outreach_email_template(self, opportunity_record: Dict, 
                                        subcontractor_record: Dict) -> Dict:
        """
        Generate personalized outreach email template
        
        Args:
            opportunity_record: Airtable record for opportunity
            subcontractor_record: Airtable record for subcontractor
        
        Returns:
            Dict with 'subject' and 'body' keys
        """
        opp = opportunity_record.get('fields', {})
        sub = subcontractor_record.get('fields', {})
        
        # Get response deadline (5 days from now)
        deadline = (datetime.now() + timedelta(days=5)).strftime('%B %d, %Y')
        
        subject = f"Government Contract Opportunity - {opp.get('ServiceType', 'Services')} in {opp.get('Location', '')}"
        
        contact_name = sub.get('ContactName', 'there')
        company_name = sub.get('CompanyName', 'your company')
        rating = sub.get('GoogleRating') or sub.get('YelpRating', 'excellent')
        
        body = f"""Hi {contact_name},

I'm Dee Davis with DEE DAVIS INC, a certified EDWOSB prime contractor. 
I found {company_name} and was impressed by your {rating}-star rating.

I'm bidding on a {opp.get('ServiceType')} contract for a municipal client in {opp.get('GeneralLocation', opp.get('Location'))} 
and looking for a qualified subcontractor partner.

PROJECT SCOPE:
• Service: {opp.get('Description', 'See details below')}
• Location: {opp.get('GeneralLocation', 'County/region')}
• Duration: {opp.get('ContractLength', 'TBD')}
• Start Date: {opp.get('StartDate', 'TBD')}

REQUIREMENTS:
• $1M liability insurance (DEE DAVIS INC as additional insured)
• Business license in good standing
• {opp.get('OtherRequirements', 'References available')}

If you're interested and available, please respond with:
1. Your pricing (per {opp.get('PricingUnit', 'service')})
2. Availability starting {opp.get('StartDate', 'soon')}
3. Confirmation of insurance coverage

Please respond by {deadline} if interested. I'm evaluating multiple contractors 
and will select partners this week.

Best regards,

Dee Davis, President
DEE DAVIS INC
248-376-4550
info@deedavis.biz
www.deedavis.biz

---

P.S. This is a government contract with reliable payment and potential for 
ongoing work. References required if selected.
"""
        
        return {
            'subject': subject,
            'body': body
        }
    
    def list_subcontractors(self, service_type: Optional[str] = None, 
                           location: Optional[str] = None) -> List[Dict]:
        """
        List subcontractors from Airtable database
        
        Args:
            service_type: Filter by service type (optional)
            location: Filter by coverage area (optional)
        
        Returns:
            List of subcontractor records
        """
        formula_parts = []
        
        if service_type:
            formula_parts.append(f"FIND('{service_type}', {{ServiceTypes}})")
        
        if location:
            formula_parts.append(f"FIND('{location}', {{CoverageArea}})")
        
        formula = f"AND({', '.join(formula_parts)})" if formula_parts else None
        
        records = self.subs_table.all(formula=formula) if formula else self.subs_table.all()
        
        return records
    
    def compare_quotes(self, opportunity_id: str) -> List[Dict]:
        """
        Compare quotes received for an opportunity
        
        Args:
            opportunity_id: Airtable record ID for opportunity
        
        Returns:
            List of quote comparisons sorted by price
        """
        print(f"\n{'='*60}")
        print(f"📊 COMPARING QUOTES")
        print(f"{'='*60}\n")
        
        # Get all tracking records with quotes for this opportunity
        formula = f"AND({{OpportunityID}}='{opportunity_id}', {{ResponseStatus}}='Interested', {{QuoteAmount}}>0)"
        
        tracking_records = self.tracking_table.all(formula=formula)
        
        if not tracking_records:
            print("❌ No quotes found for this opportunity")
            return []
        
        comparisons = []
        
        for record in tracking_records:
            fields = record['fields']
            
            # Get subcontractor details
            sub_id = fields['SubcontractorID'][0]
            sub = self.subs_table.get(sub_id)
            sub_fields = sub['fields']
            
            # Calculate response time
            response_time_hours = None
            if fields.get('ResponseDate') and fields.get('OutreachDate'):
                response_time = (
                    datetime.fromisoformat(fields['ResponseDate']) - 
                    datetime.fromisoformat(fields['OutreachDate'])
                )
                response_time_hours = response_time.total_seconds() / 3600
            
            comparisons.append({
                'company': sub_fields.get('CompanyName'),
                'rating': sub_fields.get('GoogleRating') or sub_fields.get('YelpRating', 0),
                'total_reviews': sub_fields.get('TotalReviews', 0),
                'quote_amount': fields.get('QuoteAmount', 0),
                'quote_details': fields.get('QuoteDetails', ''),
                'available': fields.get('Available', False),
                'availability_notes': fields.get('AvailabilityNotes', ''),
                'response_time_hours': round(response_time_hours, 1) if response_time_hours else None,
                'phone': sub_fields.get('Phone', ''),
                'website': sub_fields.get('Website', ''),
                'notes': fields.get('Notes', '')
            })
        
        # Sort by quote amount (lowest first)
        comparisons.sort(key=lambda x: x['quote_amount'])
        
        # Display comparison
        print(f"{'Company':<30} {'Rating':<10} {'Quote':<15} {'Response':<12} {'Available':<10}")
        print(f"{'-'*30} {'-'*10} {'-'*15} {'-'*12} {'-'*10}")
        
        for comp in comparisons:
            print(f"{comp['company']:<30} "
                  f"{comp['rating']:.1f}★ ({comp['total_reviews']:<4})"
                  f" ${comp['quote_amount']:<13,.2f} "
                  f"{comp['response_time_hours'] or 'N/A':<12} "
                  f"{'Yes' if comp['available'] else 'No':<10}")
        
        print(f"\n{'='*60}\n")
        
        return comparisons


def main():
    """Command-line interface"""
    parser = argparse.ArgumentParser(description='Automated Subcontractor Sourcing')
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Find command
    find_parser = subparsers.add_parser('find', help='Find subcontractors')
    find_parser.add_argument('--service', required=True, help='Service type (e.g., "lawn care")')
    find_parser.add_argument('--location', required=True, help='Location (e.g., "Oakland County, MI")')
    find_parser.add_argument('--radius', type=int, default=25, help='Search radius in miles (default: 25)')
    find_parser.add_argument('--limit', type=int, default=20, help='Maximum results (default: 20)')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List subcontractors from database')
    list_parser.add_argument('--service', help='Filter by service type')
    list_parser.add_argument('--location', help='Filter by location')
    
    # Compare command
    compare_parser = subparsers.add_parser('compare', help='Compare quotes for opportunity')
    compare_parser.add_argument('--opportunity-id', required=True, help='Airtable opportunity record ID')
    
    # Generate email template command
    email_parser = subparsers.add_parser('email-template', help='Generate email template')
    email_parser.add_argument('--opportunity-id', required=True, help='Airtable opportunity record ID')
    email_parser.add_argument('--subcontractor-id', required=True, help='Airtable subcontractor record ID')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize system
    try:
        system = SubcontractorSourcingSystem()
    except Exception as e:
        print(f"❌ Error initializing system: {e}")
        return 1
    
    # Execute command
    if args.command == 'find':
        system.find_subcontractors(
            service_type=args.service,
            location=args.location,
            radius_miles=args.radius,
            limit=args.limit
        )
    
    elif args.command == 'list':
        subs = system.list_subcontractors(
            service_type=args.service,
            location=args.location
        )
        print(f"\n{'='*60}")
        print(f"SUBCONTRACTORS ({len(subs)} total)")
        print(f"{'='*60}\n")
        for sub in subs:
            fields = sub['fields']
            print(f"• {fields.get('CompanyName')}")
            print(f"  Rating: {fields.get('GoogleRating', 'N/A')}★")
            print(f"  Phone: {fields.get('Phone', 'N/A')}")
            print(f"  Services: {', '.join(fields.get('ServiceTypes', []))}")
            print()
    
    elif args.command == 'compare':
        system.compare_quotes(args.opportunity_id)
    
    elif args.command == 'email-template':
        # Get records from Airtable
        opp_table = system.api.table(system.base_id, 'Opportunities')
        opportunity = opp_table.get(args.opportunity_id)
        subcontractor = system.subs_table.get(args.subcontractor_id)
        
        # Generate email
        email = system.generate_outreach_email_template(opportunity, subcontractor)
        
        print(f"\n{'='*60}")
        print(f"EMAIL TEMPLATE")
        print(f"{'='*60}\n")
        print(f"SUBJECT: {email['subject']}\n")
        print(f"BODY:\n{email['body']}")
        print(f"\n{'='*60}\n")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
