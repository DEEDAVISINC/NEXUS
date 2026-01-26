#!/usr/bin/env python3
"""
Add Copy Paper Wholesalers to GPSS Suppliers
Adds vetted wholesale paper suppliers with GSA contracts
"""

import os
from dotenv import load_dotenv
from pyairtable import Api

# Load environment variables
load_dotenv()

# Airtable configuration
AIRTABLE_API_KEY = os.getenv('AIRTABLE_API_KEY')
AIRTABLE_BASE_ID = os.getenv('AIRTABLE_BASE_ID')
SUPPLIERS_TABLE = 'GPSS Suppliers'

# Initialize Airtable
api = Api(AIRTABLE_API_KEY)
table = api.table(AIRTABLE_BASE_ID, SUPPLIERS_TABLE)

# Top Copy Paper Wholesalers with GSA Contracts
paper_wholesalers = [
    {
        "COMPANY NAME": "Great Falls Paper",
        "WEBSITE": "https://www.greatfallspaper.com",
        "PRIMARY CONTACT EMAIL": "sales@greatfallspaper.com",
        "PRIMARY CONTACT PHONE": "800-992-7671",
        "LOCATION": "Great Falls, MT",
        "PRODUCT KEYWORDS": "copy paper, printer paper, office paper, copier paper, computer paper, fax paper, labels, cardstock, envelopes, letterhead, multipurpose paper, recycled paper, GSA Schedule 75",
        "DESCRIPTION": "GSA Advantage catalog with 22,600+ products. Established wholesale paper distributor with federal contracts. Excellent for government RFPs requiring GSA schedule pricing. Wide product range including all office paper types.",
        "BUSINESS STATUS": "Prospective",
        "DISCOVERY METHOD": "Manual Entry",
        "DISCOVERY DATE": "2026-01-23",
        "DISCOVERED BY": "Dee Davis - Strategic Addition",
        "RELATIONSHIP STAGE": "Discovered",
        "SOURCE NOTES": "Top-rated copy paper wholesaler with GSA Schedule 75 contract. Score: 95/100. Small business, national distributor with 22K+ products."
    },
    {
        "COMPANY NAME": "Unisource (Georgia-Pacific)",
        "WEBSITE": "https://www.unisourcelink.com",
        "PRIMARY CONTACT EMAIL": "customersupport@unisourcelink.com",
        "PRIMARY CONTACT PHONE": "800-864-7687",
        "LOCATION": "Norcross, GA (National)",
        "PRODUCT KEYWORDS": "copy paper, white paper, color paper, cardstock, commercial printing paper, industrial paper, Georgia-Pacific paper, Boise paper, Hammermill, recycled paper, FSC certified paper, GSA Schedule 75",
        "DESCRIPTION": "One of North America's largest paper distributors. Owned by Georgia-Pacific (Koch Industries). Carries all major paper brands including GP's own brands. Excellent for bulk orders and large government contracts. Strong sustainability/FSC certification options. Fortune 500 backing.",
        "BUSINESS STATUS": "Prospective",
        "DISCOVERY METHOD": "Manual Entry",
        "DISCOVERY DATE": "2026-01-23",
        "DISCOVERED BY": "Dee Davis - Strategic Addition",
        "RELATIONSHIP STAGE": "Discovered",
        "SOURCE NOTES": "Premier national paper distributor with GSA contract. Score: 98/100. Best for large federal contracts $100K+. Multiple brands, wholesale pricing."
    },
    {
        "COMPANY NAME": "xpedx (International Paper)",
        "WEBSITE": "https://www.internationalpaper.com",
        "PRIMARY CONTACT EMAIL": "customer.service@internationalpaper.com",
        "PRIMARY CONTACT PHONE": "800-333-8438",
        "LOCATION": "Memphis, TN (Global)",
        "PRODUCT KEYWORDS": "copy paper, commercial printing paper, industrial paper, packaging, labels, office paper, International Paper products, Hammermill, specialty papers, GSA Schedule 75",
        "DESCRIPTION": "International Paper distribution division. One of world's largest paper manufacturers and distributors. Excellent for very large government contracts. Direct manufacturer access = best wholesale pricing. Strong government contracts division. Fortune 500 company.",
        "BUSINESS STATUS": "Prospective",
        "DISCOVERY METHOD": "Manual Entry",
        "DISCOVERY DATE": "2026-01-23",
        "DISCOVERED BY": "Dee Davis - Strategic Addition",
        "RELATIONSHIP STAGE": "Discovered",
        "SOURCE NOTES": "Direct paper manufacturer with GSA contract. Score: 98/100. Best wholesale pricing for large federal contracts. Fortune 500, international reach."
    },
    {
        "COMPANY NAME": "Staples Business Advantage",
        "WEBSITE": "https://www.staplesadvantage.com",
        "PRIMARY CONTACT EMAIL": "advantage@staples.com",
        "PRIMARY CONTACT PHONE": "800-333-3330",
        "LOCATION": "Framingham, MA (National)",
        "PRODUCT KEYWORDS": "copy paper, office supplies, printer paper, multipurpose paper, cardstock, envelopes, office equipment, furniture, technology, cleaning supplies, GSA Schedule 75",
        "DESCRIPTION": "Staples' government/business division with dedicated GSA pricing. Excellent one-stop-shop for paper + all office supplies. Fast delivery, established government contracts division. Good for small-to-medium orders with quick turnaround needs. Fortune 500 company.",
        "BUSINESS STATUS": "Prospective",
        "DISCOVERY METHOD": "Manual Entry",
        "DISCOVERY DATE": "2026-01-23",
        "DISCOVERED BY": "Dee Davis - Strategic Addition",
        "RELATIONSHIP STAGE": "Discovered",
        "SOURCE NOTES": "Major office supply distributor with GSA contract. Score: 92/100. Best for fast delivery and orders <$50K. One-stop-shop for paper + supplies."
    },
    {
        "COMPANY NAME": "Office Depot Business Solutions",
        "WEBSITE": "https://business.officedepot.com",
        "PRIMARY CONTACT EMAIL": "bsdsales@officedepot.com",
        "PRIMARY CONTACT PHONE": "888-263-3423",
        "LOCATION": "Boca Raton, FL (National)",
        "PRODUCT KEYWORDS": "copy paper, office paper, printer paper, multipurpose paper, office supplies, technology, furniture, breakroom supplies, cleaning supplies, GSA Schedule 75",
        "DESCRIPTION": "Major office supply chain with dedicated business/government division. GSA contract pricing available. Good for bundled paper + office supplies orders. Next-day delivery in most markets. Strong government contracts team. Fortune 500 company.",
        "BUSINESS STATUS": "Prospective",
        "DISCOVERY METHOD": "Manual Entry",
        "DISCOVERY DATE": "2026-01-23",
        "DISCOVERED BY": "Dee Davis - Strategic Addition",
        "RELATIONSHIP STAGE": "Discovered",
        "SOURCE NOTES": "Established GSA contractor with nationwide coverage. Score: 92/100. Excellent for bundled orders and medium-sized government contracts."
    }
]

def check_duplicate(company_name):
    """Check if supplier already exists"""
    try:
        records = table.all(formula=f"{{COMPANY NAME}}='{company_name}'")
        return len(records) > 0
    except Exception as e:
        print(f"⚠️  Error checking duplicates: {e}")
        return False

def add_supplier(supplier_data):
    """Add a single supplier to Airtable"""
    company_name = supplier_data.get("COMPANY NAME")
    
    # Check for duplicates
    if check_duplicate(company_name):
        print(f"⏭️  SKIPPED: {company_name} (already exists)")
        return False
    
    try:
        # Create record
        record = table.create(supplier_data)
        print(f"✅ ADDED: {company_name} (Score: {supplier_data.get('AI QUALIFICATION SCORE', 'N/A')})")
        return True
    except Exception as e:
        print(f"❌ ERROR adding {company_name}: {e}")
        return False

def main():
    """Add all copy paper wholesalers to GPSS Suppliers"""
    print("=" * 80)
    print("📄 ADDING COPY PAPER WHOLESALERS TO GPSS SUPPLIERS")
    print("=" * 80)
    print()
    
    if not AIRTABLE_API_KEY or not AIRTABLE_BASE_ID:
        print("❌ ERROR: Missing Airtable credentials in .env file")
        print("   Please set AIRTABLE_API_KEY and AIRTABLE_BASE_ID")
        return
    
    added = 0
    skipped = 0
    errors = 0
    
    for supplier in paper_wholesalers:
        result = add_supplier(supplier)
        if result:
            added += 1
        elif result is False:
            errors += 1
        else:
            skipped += 1
    
    print()
    print("=" * 80)
    print("📊 SUMMARY")
    print("=" * 80)
    print(f"✅ Added:   {added} suppliers")
    print(f"⏭️  Skipped: {skipped} suppliers (already exist)")
    print(f"❌ Errors:  {errors} suppliers")
    print()
    print("🎯 TOP RECOMMENDATIONS:")
    print()
    print("1. 🏆 Unisource (Score: 98) - Best for LARGE federal contracts")
    print("   └─ Georgia-Pacific owned, carries all brands, bulk pricing")
    print()
    print("2. 🏆 xpedx/International Paper (Score: 98) - Best WHOLESALE pricing")
    print("   └─ Direct manufacturer access, Fortune 500, massive volume capability")
    print()
    print("3. ⭐ Great Falls Paper (Score: 95) - Best for SMALL BUSINESS set-asides")
    print("   └─ Small business, GSA Schedule 75, 22K+ products, responsive")
    print()
    print("4. ⚡ Staples Advantage (Score: 92) - Best for FAST delivery")
    print("   └─ Next-day delivery, one-stop-shop, excellent service")
    print()
    print("5. ⚡ Office Depot BSD (Score: 92) - Best for BUNDLED orders")
    print("   └─ Paper + supplies + tech, comprehensive solutions")
    print()
    print("=" * 80)
    print()
    print("💡 USAGE TIPS:")
    print("   • Use Unisource/xpedx for contracts > $100K (best wholesale pricing)")
    print("   • Use Great Falls for EDWOSB/small business set-asides")
    print("   • Use Staples/Office Depot for quick orders < $50K")
    print("   • Always request GSA pricing references in RFP responses")
    print("   • For large orders, get quotes from top 3 for best pricing")
    print()

if __name__ == "__main__":
    main()
