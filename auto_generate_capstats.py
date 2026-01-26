#!/usr/bin/env python3
"""
Auto-Generate Capability Statements for Qualified Opportunities
Run this script to automatically generate capability statements for all opportunities
that are ready to bid but don't have a capability statement yet.

Usage:
    python3 auto_generate_capstats.py                    # Generate for all qualified
    python3 auto_generate_capstats.py --opportunity-id recXXX  # Generate for specific opportunity
    python3 auto_generate_capstats.py --dry-run          # Preview what would be generated
"""

import os
import sys
import argparse
from datetime import datetime
from typing import List, Dict
from pyairtable import Api
from capability_statement_generator import handle_generate_capability_statement


def get_qualified_opportunities() -> List[Dict]:
    """Get all opportunities that need capability statements"""
    
    airtable_key = os.environ.get('AIRTABLE_API_KEY')
    base_id = os.environ.get('AIRTABLE_BASE_ID')
    
    if not airtable_key or not base_id:
        print("❌ Error: AIRTABLE_API_KEY and AIRTABLE_BASE_ID environment variables required")
        sys.exit(1)
    
    api = Api(airtable_key)
    opportunities = api.table(base_id, 'Opportunities')
    
    # Find opportunities that need capability statements
    formula = "AND(OR({Status}='Ready to Bid', {Status}='Bidding'), {CapabilityStatementID}=BLANK())"
    
    try:
        records = opportunities.all(formula=formula)
        return records
    except Exception as e:
        print(f"❌ Error fetching opportunities: {e}")
        return []


def generate_for_opportunity(opportunity_id: str, dry_run: bool = False) -> Dict:
    """Generate capability statement for a specific opportunity"""
    
    if dry_run:
        return {
            'success': True,
            'dry_run': True,
            'message': f'Would generate for {opportunity_id}'
        }
    
    try:
        result = handle_generate_capability_statement(
            opportunity_id=opportunity_id,
            template='auto'  # Let system choose best template
        )
        return result
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'opportunity_id': opportunity_id
        }


def main():
    """Main function"""
    
    parser = argparse.ArgumentParser(description='Auto-generate capability statements')
    parser.add_argument('--opportunity-id', help='Generate for specific opportunity')
    parser.add_argument('--dry-run', action='store_true', help='Preview without generating')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🚀 NEXUS CAPABILITY STATEMENT AUTO-GENERATOR")
    print("=" * 60)
    print()
    
    if args.dry_run:
        print("🔍 DRY RUN MODE - No files will be generated")
        print()
    
    # Generate for specific opportunity
    if args.opportunity_id:
        print(f"📝 Generating for opportunity: {args.opportunity_id}")
        print()
        
        result = generate_for_opportunity(args.opportunity_id, args.dry_run)
        
        if result['success']:
            if args.dry_run:
                print(f"✓ Would generate capability statement")
            else:
                print(f"✓ Generated successfully!")
                print(f"  HTML: {result.get('html_file', 'N/A')}")
                print(f"  PDF: {result.get('pdf_file', 'N/A')}")
                print(f"  Airtable ID: {result.get('airtable_record_id', 'N/A')}")
        else:
            print(f"❌ Error: {result.get('error', 'Unknown error')}")
        
        return
    
    # Generate for all qualified opportunities
    print("🔍 Finding qualified opportunities...")
    opportunities = get_qualified_opportunities()
    
    if not opportunities:
        print("✓ No opportunities need capability statements")
        print("  All qualified opportunities already have statements!")
        return
    
    print(f"📋 Found {len(opportunities)} opportunities needing capability statements")
    print()
    
    # Show what will be generated
    for opp in opportunities:
        fields = opp['fields']
        client = fields.get('ClientName', 'Unknown')
        rfq = fields.get('OpportunityNumber', 'Unknown')
        status = fields.get('Status', 'Unknown')
        
        print(f"  • {client} - {rfq} ({status})")
    
    print()
    
    if args.dry_run:
        print("✓ Dry run complete. Run without --dry-run to generate.")
        return
    
    # Confirm before generating
    response = input("Generate capability statements for these opportunities? (y/n): ")
    
    if response.lower() != 'y':
        print("❌ Cancelled")
        return
    
    print()
    print("=" * 60)
    print("🎯 GENERATING CAPABILITY STATEMENTS")
    print("=" * 60)
    print()
    
    # Generate for each
    results = {
        'success': [],
        'failed': [],
        'total': len(opportunities)
    }
    
    for i, opp in enumerate(opportunities, 1):
        fields = opp['fields']
        client = fields.get('ClientName', 'Unknown')
        rfq = fields.get('OpportunityNumber', 'Unknown')
        
        print(f"[{i}/{len(opportunities)}] Generating for {client} - {rfq}...")
        
        result = generate_for_opportunity(opp['id'])
        
        if result['success']:
            print(f"  ✓ Success! PDF: {result.get('pdf_file', 'N/A')}")
            results['success'].append({
                'client': client,
                'rfq': rfq,
                'files': result
            })
        else:
            print(f"  ❌ Failed: {result.get('error', 'Unknown')}")
            results['failed'].append({
                'client': client,
                'rfq': rfq,
                'error': result.get('error')
            })
        
        print()
    
    # Summary
    print("=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    print(f"Total: {results['total']}")
    print(f"Success: {len(results['success'])} ✓")
    print(f"Failed: {len(results['failed'])} ❌")
    print()
    
    if results['success']:
        print("✅ Successfully Generated:")
        for item in results['success']:
            print(f"  • {item['client']} - {item['rfq']}")
        print()
    
    if results['failed']:
        print("❌ Failed:")
        for item in results['failed']:
            print(f"  • {item['client']} - {item['rfq']}")
            print(f"    Error: {item['error']}")
        print()
    
    print("✓ Auto-generation complete!")


if __name__ == '__main__':
    main()
