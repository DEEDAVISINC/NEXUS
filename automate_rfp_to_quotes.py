#!/usr/bin/env python3
"""
NEXUS RFP-to-Quotes Automation
Upload RFP → Find Suppliers → Generate Quote Emails → Track Responses

This is what you SHOULD be doing instead of manual work!
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from nexus_backend import (
    GPSSSupplierMiner,
    GPSSAutomatedQuoting,
    AirtableManager
)

load_dotenv()

class RFPAutomation:
    """Fully automated RFP processing"""
    
    def __init__(self):
        self.supplier_miner = GPSSSupplierMiner()
        self.auto_quote = GPSSAutomatedQuoting()
        self.airtable = AirtableManager()
    
    def process_rfp_end_to_end(
        self,
        product_description: str,
        quantity: str,
        delivery_location: str,
        quote_deadline: str,
        specs: dict = None
    ) -> dict:
        """
        MAIN AUTOMATION METHOD
        
        Takes RFP details → Finds suppliers → Generates emails → Returns ready-to-send quotes
        
        Args:
            product_description: "Sodium Hypochlorite 12.5% (Liquid Chlorine)"
            quantity: "13,000 gallons per year"
            delivery_location: "Southeast Michigan (Wayne County)" 
            quote_deadline: "January 31, 2026"
            specs: Additional specifications dict
            
        Returns:
            {
                'suppliers_found': 8,
                'suppliers': [...],
                'quote_emails': [...],
                'summary': '...'
            }
        """
        
        print("=" * 80)
        print("🤖 NEXUS RFP AUTOMATION - FULL PROCESS")
        print("=" * 80)
        print()
        
        # STEP 1: Search for suppliers
        print("📋 STEP 1: Finding suppliers...")
        print(f"   Product: {product_description}")
        print()
        
        suppliers = self.supplier_miner.find_suppliers_for_product(
            product=product_description,
            max_results=8,
            auto_mine=True  # Auto-searches if not enough in database
        )
        
        print(f"   ✅ Found {len(suppliers)} suppliers")
        for i, s in enumerate(suppliers[:5], 1):
            print(f"      {i}. {s.get('Company Name', 'Unknown')}")
        if len(suppliers) > 5:
            print(f"      ... and {len(suppliers) - 5} more")
        print()
        
        # STEP 2: Generate quote request emails for each
        print("📧 STEP 2: Generating quote request emails...")
        print()
        
        quote_specs = specs or {}
        quote_specs.update({
            'product': product_description,
            'quantity': quantity,
            'delivery_location': delivery_location,
            'quote_deadline': quote_deadline
        })
        
        quote_emails = []
        for supplier in suppliers:
            try:
                email_data = self.auto_quote.generate_quote_request_email(
                    supplier=supplier,
                    specs=quote_specs
                )
                quote_emails.append({
                    'supplier': supplier.get('Company Name'),
                    'email_to': email_data.get('to'),
                    'subject': email_data.get('subject'),
                    'body': email_data.get('body'),
                    'status': 'ready_to_send'
                })
                print(f"   ✅ Generated email for: {supplier.get('Company Name')}")
            except Exception as e:
                print(f"   ⚠️  Error for {supplier.get('Company Name')}: {e}")
        
        print()
        print(f"   📧 Generated {len(quote_emails)} quote request emails")
        print()
        
        # STEP 3: Summary
        print("=" * 80)
        print("✅ AUTOMATION COMPLETE!")
        print("=" * 80)
        print()
        print(f"📊 RESULTS:")
        print(f"   • Suppliers found: {len(suppliers)}")
        print(f"   • Quote emails generated: {len(quote_emails)}")
        print(f"   • Ready to send: {len([e for e in quote_emails if e['status'] == 'ready_to_send'])}")
        print()
        print("🎯 NEXT STEPS:")
        print("   1. Review generated emails (below)")
        print("   2. Send via your email client")
        print("   3. Track responses in Airtable")
        print()
        
        return {
            'suppliers_found': len(suppliers),
            'suppliers': suppliers,
            'quote_emails': quote_emails,
            'summary': f"Found {len(suppliers)} suppliers and generated {len(quote_emails)} quote requests"
        }
    
    def show_generated_email(self, email_data: dict):
        """Display generated email in copyable format"""
        print("=" * 80)
        print(f"📧 TO: {email_data['email_to']}")
        print(f"📋 SUPPLIER: {email_data['supplier']}")
        print("=" * 80)
        print()
        print(f"SUBJECT: {email_data['subject']}")
        print()
        print(email_data['body'])
        print()
        print("=" * 80)
        print()


def demo_hcma_automation():
    """
    Demo: Run automation for HCMA Liquid Chlorine RFP
    This is what should have happened automatically!
    """
    
    automation = RFPAutomation()
    
    # Run full automation
    result = automation.process_rfp_end_to_end(
        product_description="Sodium Hypochlorite 12.5% Liquid Chlorine",
        quantity="13,000 gallons per year (approximately 15 deliveries of 900-1200 gallons each)",
        delivery_location="Southeast Michigan (Wayne County area)",
        quote_deadline="January 31, 2026",
        specs={
            'delivery_method': 'Tanker truck (pumped/metered preferred)',
            'response_time': '24-48 hours from order',
            'contract_term': '2 years with firm pricing',
            'quality_standard': 'NSF/ANSI 60 standards'
        }
    )
    
    # Show first 3 generated emails
    print("\n" + "="*80)
    print("📧 SAMPLE GENERATED EMAILS (First 3):")
    print("="*80 + "\n")
    
    for i, email in enumerate(result['quote_emails'][:3], 1):
        print(f"\n{'='*80}")
        print(f"EMAIL #{i}")
        automation.show_generated_email(email)
    
    return result


if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║                    🤖 NEXUS RFP AUTOMATION SYSTEM                           ║
║                                                                              ║
║  This script demonstrates what NEXUS should be doing automatically:         ║
║                                                                              ║
║    1. Upload RFP → Extract details                                          ║
║    2. Find suppliers automatically (check database + search online)         ║
║    3. Generate personalized quote request emails                            ║
║    4. Track responses and rank quotes                                       ║
║    5. Calculate optimal bid with margin                                     ║
║                                                                              ║
║  Instead of doing this manually, you should just:                           ║
║    • Upload RFP PDF                                                         ║
║    • Click "Automate"                                                       ║
║    • Review & send generated emails                                         ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)
    
    print("\nRunning automation for HCMA Liquid Chlorine RFP...")
    print()
    
    try:
        result = demo_hcma_automation()
        
        print("\n" + "="*80)
        print("✅ AUTOMATION SUCCESSFUL!")
        print("="*80)
        print(f"\nThis should have taken 30 seconds, not hours of manual work!")
        print(f"\nGenerated {result['suppliers_found']} suppliers and {len(result['quote_emails'])} emails automatically.")
        print("\n💡 NEXT: Build UI to make this one-click!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nThis might need API keys configured (Google CSE, SAM.gov)")
        print("But the automation framework is ready!")
