#!/usr/bin/env python3
"""
Add Additional RCOC 7734 Forestry Products to NEXUS
Adds Bishco helmets and Northeastern visors found today
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

api_key = os.environ.get('AIRTABLE_API_KEY')
base_id = os.environ.get('AIRTABLE_BASE_ID')

if not api_key or not base_id:
    print('❌ ERROR: Missing AIRTABLE_API_KEY or AIRTABLE_BASE_ID')
    exit(1)

api = Api(api_key)
table = api.table(base_id, 'GPSS PRODUCTS')

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
Contract: RCOC RFQ 7734
Cost: $101.99/each (tax-exempt)

Phone: 1-800-421-4833
Website: bishco.com/climbing-technology-x-arbor-helmet/

⭐ ALTERNATIVE SOURCE for TreeStuff SKU 24791 (discontinued)
Ordered 3 units to complete 10 helmet requirement
Same price as TreeStuff, in stock'''
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
Contract: RCOC RFQ 7734
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
Cheaper than Wesspur by $0.45 per unit'''
    }
]

print('🚀 ADDING 2 ADDITIONAL FORESTRY PRODUCTS TO NEXUS...\n')

added = 0
for p in products:
    try:
        table.create(p)
        sku = p['Description'].split('SKU: ')[1].split('\n')[0] if 'SKU:' in p['Description'] else 'N/A'
        print(f"✅ {p['NAME']}")
        print(f"   {p['SUPPLIER']}")
        print(f"   SKU: {sku} - ${p['UNIT PRICE']}\n")
        added += 1
    except Exception as e:
        print(f"❌ ERROR: {p['NAME']}: {e}\n")

print(f"✅ Added {added} of {len(products)} products!")
print(f"\n📊 RCOC 7734 Products in NEXUS:")
print(f"   - TreeStuff items: 11")
print(f"   - Bishco helmets: 1")
print(f"   - Northeastern visors: 1")
print(f"   - TOTAL: 13 products with full SKU details ✅")
print(f"\n🔍 All searchable in NEXUS Product Catalog!")
