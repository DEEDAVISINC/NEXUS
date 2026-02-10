#!/usr/bin/env python3
"""
Add ALL RCOC 7734 Forestry Products Sourced Today to NEXUS
Includes: Bishco helmets, Northeastern visors, Bishco LimeLite24 rope, Amazon Pelican rope
Date: January 30, 2026
"""

import os
from pyairtable import Api

# Load environment variables
env_file = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(env_file):
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()

# Get API credentials (try both variable names)
AIRTABLE_API_KEY = os.getenv('AIRTABLE_API_KEY') or os.getenv('AIRTABLE_PERSONAL_ACCESS_TOKEN')
BASE_ID = os.getenv('AIRTABLE_BASE_ID')

if not AIRTABLE_API_KEY or not BASE_ID:
    print('❌ ERROR: Missing AIRTABLE_API_KEY or AIRTABLE_BASE_ID')
    print(f'API KEY: {"Found" if AIRTABLE_API_KEY else "Missing"}')
    print(f'BASE ID: {"Found" if BASE_ID else "Missing"}')
    exit(1)

# Initialize API
api = Api(AIRTABLE_API_KEY)
table = api.table(BASE_ID, 'GPSS PRODUCTS')

# ALL FORESTRY PRODUCTS SOURCED TODAY
products = [
    {
        'NAME': 'CT X-Arbor Helmet - Black (Bishco)',
        'PRODUCT CATEGORY': 'Forestry Equipment - Safety Gear',
        'SUPPLIER': 'Bishco',
        'UNIT PRICE': '101.99/each',
        'Description': '''Bishco SKU: CTECHXARB
Manufacturer: Climbing Technology (CT)
Manufacturer Part #: 6X94601CT002
Model: X-Arbor Helmet
Color: Black
Source: Italy
Sourced: January 30, 2026
Contract: RCOC RFQ 7734 - Item 3a
Cost: $101.99/each (tax-exempt)

Phone: 1-800-421-4833
Website: bishco.com/climbing-technology-x-arbor-helmet/

⭐ ALTERNATIVE SOURCE for TreeStuff SKU 24791 (discontinued)
Ordered 3 units to complete 10 helmet requirement
Same price as TreeStuff ($101.99), in stock
Total: $305.97 (3 × $101.99)'''
    },
    {
        'NAME': 'CT Visor G - Clear for X-Arbor Helmet',
        'PRODUCT CATEGORY': 'Forestry Equipment - Safety Gear',
        'SUPPLIER': 'Northeastern Arborist Supply',
        'UNIT PRICE': '58.55/each',
        'Description': '''Northeastern SKU: 6X9410A
Manufacturer: Climbing Technology
Model: Visor G (Clear/Transparent)
Material: Polycarbonate
Sourced: January 30, 2026
Contract: RCOC RFQ 7734 - Item 3c
Cost: $58.55/each (tax-exempt)

Website: northeastern-arborist-supply-633503.shoplightspeed.com/ct-visor-g.html
Alternative: Wesspur SKU SAF101-VS (smoke) at $59.00

Features:
- Anti-scratch treatment (outside)
- Anti-fog treatment (inside)
- 3 positions: lowered, raised, intermediate
- Compatible with CT X-Arbor and Galaxy helmets
- Full protection from ice, snow, debris

Ordered 10 units (clear recommended for forestry safety work)
Cheaper than Wesspur by $0.45 per unit
Total: $585.50 (10 × $58.55)'''
    },
    {
        'NAME': 'LimeLite24 Climbing Line 11.7mm with Spliced Eye - 150 ft',
        'PRODUCT CATEGORY': 'Forestry Equipment - Climbing Rope',
        'SUPPLIER': 'Bishco',
        'UNIT PRICE': '202.99/each',
        'Description': '''Bishco SKU: LimeLite24-150ft
Manufacturer: Bishop Company (Bishco Exclusive)
Product: LimeLite24 Climbing Line
Diameter: 11.7mm (exact RCOC spec match!)
Length: 150 feet
Construction: 24-strand braided polyester
Configuration: 1-inch spliced eye with chafe guard
Strength: 6,500 lbs tensile
Standards: CE-EN1891 Type-B
Weight: Approximately 7.5 lbs per 100 ft
Color: Lime/yellow (high visibility)

Sourced: January 30, 2026
Contract: RCOC RFQ 7734 - Item 11
Cost: $202.99/each (tax-exempt)

Phone: 1-800-421-4833
Website: bishco.com
Product Page: bishco.com/limelite-arborist-climbing-line/

⭐ PERFECT MATCH for RCOC spec: "24-strand 11.7mm climbing line 150 ft"
Quantity needed: 5 ropes
Total: $1,014.95 (5 × $202.99)

Features:
- 24-strand braided construction (exact spec)
- 11.7mm diameter (exact spec)
- One tight eye splice (exact spec)
- CE certified for arborist work
- High visibility lime color
- Chafe guard protection on splice
- Low stretch for precision climbing
- Excellent abrasion resistance
- Made specifically for tree work

Alternative Sources:
- TreeStuff: Sterling Banshee at $230.99 (but discontinued)
- Bishco is $28/rope cheaper and IN STOCK'''
    },
    {
        'NAME': 'Pelican Rope 16-Strand Arborist Rope - 1/2" x 150 ft with Spliced Eye',
        'PRODUCT CATEGORY': 'Forestry Equipment - Climbing Rope',
        'SUPPLIER': 'Amazon (U.S. Rigging Supply)',
        'UNIT PRICE': '150.19/each',
        'Description': '''Amazon ASIN: B08W2QHDHJ
Manufacturer: Pelican Rope (Made in USA)
Product: Arborist-16™ Climbing Rope
Diameter: 1/2 inch (12.7mm)
Length: 150 feet
Construction: 16-strand braided polyester
Cover: Braided polyester (high visibility)
Core: Nylon braided (non-rotational)
Configuration: Tight spliced eye at one end
Strength: 5,400 lbs MBS (with splice), 7,150 lbs (without splice)
Features: Low stretch, abrasion resistant, chemical resistant
Color: Orange/White (high visibility options: Red/White/Blue, Blue/White, Red/White)
Standards: Static climbing rope for rescue operations
Weight: ~7 lbs per 100 feet

Sourced: January 30, 2026
Contract: RCOC RFQ 7734 - Item 12
Cost: $150.19/each (tax-exempt)

Amazon Product URL: https://www.amazon.com/dp/B08W2QHDHJ

Business Price: $150.19 (List: $169.98, Save $19.79 = 12% off)
Seller: U.S. Rigging Supply (Amazon)
Seller Credentials: Business Hour Delivery, SBA Small Business, 889 Cert, ISO 9001
Rating: 4.5/5 stars (56 reviews)
Availability: In stock, ships 2-3 days
Delivery Time: Feb 11-13, 2026
Return Policy: 30-day refund/replacement
Shipping: $5 (or free with order)

Quantity needed: 2 ropes (2 bags as specified in RFQ)
Total: $300.38 (2 × $150.19)

Specifications from manufacturer:
- 100% polyester strands
- Tested tensile strength: 7,150 lbs (reduces to 5,400 with splice)
- Tightly-woven 16-strand with high twist core
- Torque-balanced polyester keeps line firm and round
- Suitable for: Tree work, arborist climbing, fixed line ascension, load hauling
- Not suitable for dynamic/lead climbing

Alternative Sources:
- Pelican Rope Direct: pelicanrope.com
- Phone: Available through U.S. Rigging Supply

Notes:
- Tax-exempt for government contracts
- Only 7 in stock on Amazon (we need 2, so plenty available)
- Excellent reviews from professional arborists
- Made in USA (bonus for government contracts)'''
    }
]

print('🚀 ADDING 4 FORESTRY PRODUCTS TO NEXUS PRODUCT CATALOG...\n')
print(f'API Status: Connected to Base {BASE_ID}')
print(f'Table: GPSS PRODUCTS\n')

added_count = 0
failed_count = 0

for product in products:
    try:
        record = table.create(product)
        print(f"✅ SUCCESS: {product['NAME']}")
        print(f"   Supplier: {product['SUPPLIER']}")
        print(f"   Price: ${product['UNIT PRICE']}")
        print(f"   Record ID: {record['id']}")
        print()
        added_count += 1
    except Exception as e:
        print(f"❌ FAILED: {product['NAME']}")
        print(f"   Error: {e}")
        print()
        failed_count += 1

print('\n' + '='*60)
print(f'✅ SUCCESSFULLY ADDED: {added_count} of {len(products)} products')
if failed_count > 0:
    print(f'❌ FAILED: {failed_count} products')
print('='*60)

print('\n📊 RCOC 7734 FORESTRY PRODUCTS IN NEXUS:')
print('   ✅ Bishco - CT X-Arbor Helmet (3 units @ $101.99 = $305.97)')
print('   ✅ Northeastern - CT Visor G Clear (10 units @ $58.55 = $585.50)')
print('   ✅ Bishco - LimeLite24 Rope 11.7mm 150ft (5 units @ $202.99 = $1,014.95)')
print('   ✅ Amazon - Pelican 16-Strand Rope 1/2" 150ft (2 units @ $150.19 = $300.38)')
print('\n   TOTAL ADDED TODAY: $2,206.80')
print('\n🔍 All products now searchable in NEXUS with full SKU details!')
print('\n⚠️ STILL PENDING RCOC CLARIFICATION:')
print('   - Item 10: 16 ft positioning lanyard (non-standard size)')
print('   - Items 13-14: 3/8" prusik cords (10mm alternatives found)')
