#!/usr/bin/env python3
"""
Add RCOC Products to NEXUS
Adds all 9 products from RCOC bids (7732, 7731, 7798) to GPSS PRODUCTS table
"""

import os
from pyairtable import Api

# Load environment variables manually
env_file = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(env_file):
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()

# Get API credentials
api_key = os.environ.get('AIRTABLE_API_KEY')
base_id = os.environ.get('AIRTABLE_BASE_ID')

if not api_key or not base_id:
    print('❌ ERROR: Missing AIRTABLE_API_KEY or AIRTABLE_BASE_ID in .env file')
    exit(1)

api = Api(api_key)
table = api.table(base_id, 'GPSS PRODUCTS')

# Define all 9 RCOC products with complete details
# Using actual GPSS PRODUCTS table fields: NAME, PRODUCT CATEGORY, SUPPLIER, UNIT PRICE, Description
products = [
    {
        'NAME': 'Dinner Napkins - White, 1/8 Fold, 2-Ply (PK3000)',
        'PRODUCT CATEGORY': 'Janitorial Supplies - Paper Products',
        'SUPPLIER': 'Grainger',
        'UNIT PRICE': '70.00/pack',
        'Description': '''Empress DN 281517B
Grainger SKU: 846N89
UOM: Pack of 3,000 napkins
Cost: $70.00/pack

Alternative: Zoro (more expensive)
Contract: RCOC IFB 7732
Date: 2026-01-29

NOTE: Grainger is cheaper than Zoro on this item. Use Grainger Quote #2063445243. Tax-exempt for government contracts.'''
    },
    {
        'NAME': 'Disposable Hot Cups 8oz - White (PK1000)',
        'PRODUCT CATEGORY': 'Janitorial Supplies - Paper Products',
        'SUPPLIER': 'Zoro',
        'UNIT PRICE': '123.99/pack',
        'Description': '''Dixie 5338CD
Zoro SKU: TBD
UOM: Pack of 1,000 cups
Cost: $123.99/pack

Alternative: Grainger - $180.00/pack
💰 SAVES 31%! ($56/pack savings)
Contract: RCOC IFB 7732
Date: 2026-01-29

31% SAVINGS vs Grainger! Coffee Haze pattern, polyethylene lined, microwave safe. ALWAYS check Zoro first!'''
    },
    {
        'NAME': 'Toilet Paper - Scott Essential, 2-Ply, 550 Sheets (PK80)',
        'PRODUCT CATEGORY': 'Janitorial Supplies - Paper Products',
        'SUPPLIER': 'Zoro',
        'UNIT PRICE': '96.29/pack',
        'Description': '''Kimberly-Clark Professional 04460 (Scott Essential)
Zoro SKU: G4519551
UOM: Pack of 80 rolls
Cost: $96.29/pack

Alternative: Grainger - $111.02/pack
💰 SAVES 13%! ($14.73/pack)
Contract: RCOC IFB 7732
Date: 2026-01-29

550 sheets/roll, 183ft length, FSC certified, 4" x 4.1" sheet size.'''
    },
    {
        'NAME': 'Cloth Rags - Reclaimed White Cotton (25lb Box)',
        'PRODUCT CATEGORY': 'Janitorial Supplies - Cleaning',
        'SUPPLIER': 'Zoro',
        'UNIT PRICE': '48.39/each',
        'Description': '''Absorbents Midwest 30-450-B
Zoro SKU: G614665951
UOM: Each (25lb box)
Cost: $48.39/each

Alternative: Grainger (G440025PC) - $50.00/each
💰 SAVES 3% ($1.61/each)
Contract: RCOC IFB 7732
Date: 2026-01-29

White cotton sheeting, reclaimed material.'''
    },
    {
        'NAME': 'Facial Tissue - Comfort Touch, 2-Ply (PK36)',
        'PRODUCT CATEGORY': 'Janitorial Supplies - Paper Products',
        'SUPPLIER': 'Zoro',
        'UNIT PRICE': '76.25/pack',
        'Description': '''Kimberly-Clark Professional 21270 (Comfort Touch)
Zoro SKU: G306113302
UOM: Pack of 36 boxes
Cost: $76.25/pack

Alternative: Grainger - $95.00/pack
💰 SAVES 20%! ($18.75/pack)
Contract: RCOC IFB 7732
Date: 2026-01-29

90 sheets per box, 2-ply. Check Zoro first!'''
    },
    {
        'NAME': 'Industrial Wipers - WYPALL X60 Blue HydroKnit (CTN/6)',
        'PRODUCT CATEGORY': 'Industrial Supplies - Wipers',
        'SUPPLIER': 'Zoro',
        'UNIT PRICE': '166.99/carton',
        'Description': '''Kimberly-Clark Professional 35431 (WYPALL X60)
Zoro SKU: G2856357
UOM: Carton of 6 rolls
Cost: $166.99/carton

Alternative: Grainger - $234.78/carton
🏆 SAVES 29%!! ($67.79/carton = $22,575 total savings!)
Contract: RCOC RFQ 7731
Date: 2026-01-29

HydroKnit technology, 130 sheets/roll, 19.5"x13.5", blue, reinforced. Grainger Quote #2063475035. ALWAYS use Zoro!'''
    },
    {
        'NAME': 'Windshield Wiper Blade - 18 inch',
        'PRODUCT CATEGORY': 'Automotive - Maintenance',
        'SUPPLIER': 'Zoro',
        'UNIT PRICE': '7.99/each',
        'Description': '''Prime Vision PRIMPBB18
Zoro SKU: G006888180
UOM: Each
Cost: $7.99/each
Contract: RCOC RFQ 7798
Date: 2026-01-29

Fast delivery (by Feb 5), in stock at Zoro.'''
    },
    {
        'NAME': 'Windshield Wiper Blade - 22 inch',
        'PRODUCT CATEGORY': 'Automotive - Maintenance',
        'SUPPLIER': 'Zoro',
        'UNIT PRICE': '7.89/each',
        'Description': '''Prime Vision PRIMPBB22
Zoro SKU: G806888205
UOM: Each
Cost: $7.89/each
Contract: RCOC RFQ 7798
Date: 2026-01-29

Fast delivery (by Feb 3), in stock at Zoro.'''
    },
    {
        'NAME': 'Windshield Wiper Blade - 20 inch',
        'PRODUCT CATEGORY': 'Automotive - Maintenance',
        'SUPPLIER': 'Zoro',
        'UNIT PRICE': '7.89/each',
        'Description': '''Prime Vision PRIMPBB20
Zoro SKU: G306888170
UOM: Each
Cost: $7.89/each
Contract: RCOC RFQ 7798
Date: 2026-01-29

Fast delivery (by Feb 2), in stock at Zoro.'''
    }
]

print('🚀 ADDING 9 RCOC PRODUCTS TO NEXUS GPSS PRODUCTS TABLE...\n')

added_count = 0
for product in products:
    try:
        result = table.create(product)
        print(f"✅ Added: {product['NAME']}")
        print(f"   Supplier: {product['SUPPLIER']} - Price: ${product['UNIT PRICE']}")
        print()
        added_count += 1
    except Exception as e:
        print(f"❌ ERROR adding {product['NAME']}: {e}\n")

print(f"\n✅ SUCCESS! Added {added_count} of 9 products to NEXUS Product Catalog!")
print(f"\n📊 Total Contract Value: $126,895")
print(f"💰 Total Zoro Savings: $25,699 vs all-Grainger pricing")
print(f"\n🔍 You can now search these products in NEXUS for future quotes!")
