#!/usr/bin/env python3
"""
Add RCOC 7797 Small Automotive Tools to NEXUS
9 items from Zoro, Fastenal, Grainger, and NAPA
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

AIRTABLE_API_KEY = os.getenv('AIRTABLE_API_KEY')
BASE_ID = os.getenv('AIRTABLE_BASE_ID')

if not AIRTABLE_API_KEY or not BASE_ID:
    print('❌ ERROR: Missing AIRTABLE_API_KEY or AIRTABLE_BASE_ID')
    exit(1)

api = Api(AIRTABLE_API_KEY)
table = api.table(BASE_ID, 'GPSS PRODUCTS')

products = [
    {
        'NAME': 'Justrite Safety Gas Can - 5 Gallon Type II Red',
        'PRODUCT CATEGORY': 'Automotive Tools & Supplies',
        'SUPPLIER': 'Fastenal',
        'UNIT PRICE': '220.73/each',
        'Description': '''Fastenal Item: 4119956
Manufacturer: Justrite
Model: 7250120
Capacity: 5 gallon
Type: Type II Safety Can
Color: Red
Material: Steel
Spout: Flexible spout included
Features: UL/FM listed, vapor control, self-venting
Contract: RCOC RFQ 7797 - Item 1
Cost: $220.73/each (tax-exempt)

Quantity needed: 10 cans
Total: $2,207.30 (10 × $220.73)
Ships: ~5 business days

Sourced: January 29, 2026
⭐ EXACT part match for RFQ specification'''
    },
    {
        'NAME': 'Justrite Safety Gas Can - 2 Gallon Type II Red',
        'PRODUCT CATEGORY': 'Automotive Tools & Supplies',
        'SUPPLIER': 'Grainger',
        'UNIT PRICE': '175.62/each',
        'Description': '''Grainger Item: 26XP95
Manufacturer: Justrite
Model: 7220120
Capacity: 2 gallon
Type: Type II Safety Can
Color: Red
Material: Galvanized steel
Spout: Flexible spout
Features: UL/FM listed
Contract: RCOC RFQ 7797 - Item 2
Cost: $175.62/each (tax-exempt)

Quantity needed: 5 cans
Total: $878.10 (5 × $175.62)

Sourced: January 29, 2026
Note: RFQ specified "10568" but this is equivalent Type II 2-gal can'''
    },
    {
        'NAME': 'Goldline Bungee Strap - 18" with Hooks',
        'PRODUCT CATEGORY': 'Automotive Tools & Supplies',
        'SUPPLIER': 'Zoro',
        'UNIT PRICE': '2.32/each',
        'Description': '''Zoro SKU: G3016899
Manufacturer: Goldline
Model: 16899GLN
Length: 18 inches (unstretched)
Cord Diameter: 3/8 inch
Hooks: Steel hooks on both ends
Color: Black
Pack: 10 straps per pack
Contract: RCOC RFQ 7797 - Item 3
Cost: $23.19/pk10 ($2.32/ea)

Quantity needed: 50 straps (5 packs)
Total: $115.95 (5 packs × $23.19)

Sourced: January 29, 2026
Note: RFQ specified "Arnold or equiv" - Goldline acceptable equivalent'''
    },
    {
        'NAME': 'Forney Resin Fiber Disc - 4-1/2" 36 Grit (PK5)',
        'PRODUCT CATEGORY': 'Automotive Tools & Supplies',
        'SUPPLIER': 'Zoro',
        'UNIT PRICE': '7.89/pack',
        'Description': '''Zoro SKU: G3011846
Manufacturer: Forney
Model: 71846
Size: 4-1/2 inch diameter
Grit: 36 (coarse)
Type: Resin fiber backing
Arbor: 7/8 inch
Pack: 5 discs per pack
Use: Angle grinder, metal grinding
Contract: RCOC RFQ 7797 - Item 4
Cost: $7.89/pk5

Quantity needed: 6 packs (30 discs, RFQ asks for 5 but pack is 5)
Total: $47.34 (6 packs × $7.89)

Sourced: January 29, 2026
Note: RFQ specified "Norton or equiv" - Forney acceptable equivalent'''
    },
    {
        'NAME': 'NAPA Safety Blow Gun with MNPT Threads',
        'PRODUCT CATEGORY': 'Automotive Tools & Supplies',
        'SUPPLIER': 'NAPA Auto Parts',
        'UNIT PRICE': '26.99/each',
        'Description': '''NAPA Part #: 90-489
Manufacturer: NAPA
Type: Safety blow gun
Inlet: 1/4" MNPT (male pipe threads)
Features: Meets OSHA requirements
Contract: RCOC RFQ 7797 - Item 5
Cost: $26.99/each (tax-exempt)

Quantity needed: 5 guns
Total: $134.95 (5 × $26.99)

Sourced: January 29, 2026
⭐ EXACT part match - MNPT inlet as specified'''
    },
    {
        'NAME': 'Plews Pistol Oiler - 8oz Flex Spout',
        'PRODUCT CATEGORY': 'Automotive Tools & Supplies',
        'SUPPLIER': 'Zoro',
        'UNIT PRICE': '15.25/each',
        'Description': '''Zoro SKU: G0469421
Manufacturer: Plews Edelmann
Model: 50-595
Capacity: 8 oz (237ml)
Spout: Flexible metal spout
Material: Metal can with pump action
Use: Precision oiling
Contract: RCOC RFQ 7797 - Item 6
Cost: $15.25/each

Quantity needed: 10 oilers
Total: $152.50 (10 × $15.25)

Sourced: January 29, 2026
⭐ EXACT part match per RFQ specification'''
    },
    {
        'NAME': 'ARC Abrasives Emery Cloth Roll - 1-1/2" x 10yd',
        'PRODUCT CATEGORY': 'Automotive Tools & Supplies',
        'SUPPLIER': 'Fastenal',
        'UNIT PRICE': '28.23/each',
        'Description': '''Fastenal Item: 0191735
Manufacturer: ARC Abrasives
Model: 73138
Width: 1-1/2 inches
Length: 10 yards per roll
Grit: 120 (medium)
Backing: Cloth (J-weight)
Type: Aluminum oxide abrasive
Use: Hand sanding metal
Contract: RCOC RFQ 7797 - Item 7
Cost: $28.23/each

Quantity needed: 5 rolls
Total: $141.15 (5 × $28.23)

Sourced: January 29, 2026
⭐ EXACT part match per RFQ specification'''
    },
    {
        'NAME': 'Justrite Flex Spout with Gasket for Type II Cans',
        'PRODUCT CATEGORY': 'Automotive Tools & Supplies',
        'SUPPLIER': 'Zoro',
        'UNIT PRICE': '50.38/set',
        'Description': '''Zoro SKUs: G0471815 + G2531598
Manufacturer: Justrite
Parts: 11078 (spout) + 11073 (gasket)
Spout: Flexible brass pour spout
Gasket: Neoprene gasket for leak-free seal
Thread: 2" NPT
Compatibility: Type II safety cans
Contract: RCOC RFQ 7797 - Item 8
Cost: $50.38/set (spout $41.49 + gasket $8.89)

Quantity needed: 5 sets
Total: $251.90 (5 sets × $50.38)

Sourced: January 29, 2026
Note: Spout and gasket sold separately, both required per RFQ'''
    },
    {
        'NAME': 'Velvac Stove Wire - 19 Gauge Galvanized',
        'PRODUCT CATEGORY': 'Automotive Tools & Supplies',
        'SUPPLIER': 'Zoro',
        'UNIT PRICE': '28.15/each',
        'Description': '''Zoro SKU: G8990388
Manufacturer: Velvac
Gauge: 19 AWG
Material: Galvanized steel wire
Length: 50 ft per roll
Use: General purpose binding wire
Contract: RCOC RFQ 7797 - Item 9
Cost: $28.15/each

Quantity needed: 2 rolls
Total: $56.30 (2 × $28.15)

Sourced: January 29, 2026
Note: RFQ did not specify brand, Velvac is quality supplier'''
    }
]

print('🚀 ADDING 9 RCOC 7797 AUTOMOTIVE TOOLS TO NEXUS...\n')
print(f'API Status: Connected to Base {BASE_ID}')
print(f'Table: GPSS PRODUCTS\n')

added = 0
for p in products:
    try:
        record = table.create(p)
        print(f"✅ {p['NAME']}")
        print(f"   {p['SUPPLIER']} - ${p['UNIT PRICE']}")
        print(f"   Record ID: {record['id']}")
        print()
        added += 1
    except Exception as e:
        print(f"❌ ERROR: {p['NAME']}: {e}\n")

print('='*60)
print(f'✅ SUCCESSFULLY ADDED: {added} of {len(products)} products')
print('='*60)

print('\n📊 RCOC 7797 SMALL AUTOMOTIVE TOOLS IN NEXUS:')
print('   ✅ Fastenal - 5 Gal Gas Cans (10 @ $220.73 = $2,207.30)')
print('   ✅ Grainger - 2 Gal Gas Cans (5 @ $175.62 = $878.10)')
print('   ✅ Zoro - Bungee Straps (50 @ $2.32 = $115.95)')
print('   ✅ Zoro - Resin Discs (6 packs @ $7.89 = $47.34)')
print('   ✅ NAPA - Safety Blow Guns (5 @ $26.99 = $134.95)')
print('   ✅ Zoro - Pistol Oilers (10 @ $15.25 = $152.50)')
print('   ✅ Fastenal - Emery Cloth (5 @ $28.23 = $141.15)')
print('   ✅ Zoro - Flex Spout+Gasket (5 @ $50.38 = $251.90)')
print('   ✅ Zoro - Stove Wire (2 @ $28.15 = $56.30)')
print('\n   TOTAL COST: $3,985.49')
print('   BID AMOUNT: $4,463.75 (12% markup)')
print('   PROFIT: $478.26')
print('\n🔍 All products searchable in NEXUS with full SKU details!')
