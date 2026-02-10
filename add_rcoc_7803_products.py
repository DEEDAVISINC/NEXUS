#!/usr/bin/env python3
"""
Add RCOC 7803 Products to NEXUS
Adds all 6 products from RCOC 7803 (Hammers, Tape Measures, Levels) to GPSS PRODUCTS table
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

# Define all 6 RCOC 7803 products with complete details
products = [
    {
        'NAME': '8 oz Ball Pein Hammer, 11" Fiberglass Handle',
        'PRODUCT CATEGORY': 'Hand Tools - Hammers',
        'SUPPLIER': 'Zoro',
        'UNIT PRICE': '$12.99',
        'Description': '''STAR ASIA 8 oz Ball Pein Hammer
Manufacturer Part #: 63308
Zoro SKU: G6897318
UOM: Each
Supplier Cost: $12.99
Bid Price: $17.29 (33% markup)

Specs: 8 oz head weight, 11" overall length, fiberglass handle
Contract: RCOC 7803 - Hammers, Tape Measures, Levels
Quantity Bid: 10 units
Extended Supplier Cost: $129.90
Extended Bid Price: $172.90
Delivery: February 5, 2026
Stock Status: In Stock

Date: January 31, 2026'''
    },
    {
        'NAME': '16 oz Ball Pein Hammer, 12" Fiberglass Handle',
        'PRODUCT CATEGORY': 'Hand Tools - Hammers',
        'SUPPLIER': 'Zoro',
        'UNIT PRICE': '$13.15',
        'Description': '''PERFORMANCE TOOL 16 oz Ball Pein Hammer
Manufacturer Part #: M7032B
Zoro SKU: G500550149
UOM: Each
Supplier Cost: $13.15
Bid Price: $17.76 (35% markup)

Specs: 16 oz head weight, 12" overall length, fiberglass handle
Contract: RCOC 7803 - Hammers, Tape Measures, Levels
Quantity Bid: 3 units
Extended Supplier Cost: $39.45
Extended Bid Price: $53.25
Delivery: February 5, 2026
Stock Status: In Stock

Date: January 31, 2026'''
    },
    {
        'NAME': '3 lb Blacksmith Hammer, 10" Fiberglass Handle',
        'PRODUCT CATEGORY': 'Hand Tools - Hammers',
        'SUPPLIER': 'Zoro',
        'UNIT PRICE': '$17.65',
        'Description': '''WESTWARD 3 lb Hand Drilling Hammer
Manufacturer Part #: 2DBU5
Zoro SKU: G1958451
UOM: Each
Supplier Cost: $17.65
Bid Price: $22.95 (30% markup - bulk item)

Specs: 3 lb steel head, 10" overall length, fiberglass handle, polished face
Contract: RCOC 7803 - Hammers, Tape Measures, Levels
Quantity Bid: 50 units (BULK ORDER - largest quantity)
Extended Supplier Cost: $882.50
Extended Bid Price: $1,147.50
Delivery: February 4, 2026 (fastest delivery)
Stock Status: In Stock

⚡ BULK ITEM: 50 units = 41% of total contract value
Competitive 30% markup for bulk pricing

Date: January 31, 2026'''
    },
    {
        'NAME': '6 ft Folding Wood Ruler, Red End, Inches (Lufkin 066)',
        'PRODUCT CATEGORY': 'Hand Tools - Measuring Tools',
        'SUPPLIER': 'Zoro',
        'UNIT PRICE': '$20.49',
        'Description': '''CRESCENT LUFKIN 066FN 6' Folding Wood Rule
Manufacturer Part #: 066FN
Zoro SKU: G7867242
UOM: Each
Supplier Cost: $20.49
Bid Price: $27.66 (35% markup)

Specs: 6 feet (72 inches), folding wood ruler, red end, flat reading, inch scale
Model: Lufkin 066 series (exact reference model specified in RFQ)
Contract: RCOC 7803 - Hammers, Tape Measures, Levels
Quantity Bid: 5 units
Extended Supplier Cost: $102.45
Extended Bid Price: $138.30
Delivery: February 3, 2026 (fastest delivery)
Stock Status: In Stock

✅ EXACT MODEL MATCH: 066FN is the Lufkin 066 series specified

Date: January 31, 2026'''
    },
    {
        'NAME': '25 ft Tape Measure, 1-1/4" Blade, Stanley FATMAX',
        'PRODUCT CATEGORY': 'Hand Tools - Measuring Tools',
        'SUPPLIER': 'Zoro',
        'UNIT PRICE': '$19.70',
        'Description': '''STANLEY FATMAX 25 ft Tape Measure
Manufacturer Part #: 33-725
Zoro SKU: G1202564
UOM: Each
Supplier Cost: $19.70 (20% OFF - was $24.79!)
Bid Price: $25.61 (30% markup - bulk item)

Specs: 25 feet length, 1-1/4" blade width (wider than 1" spec = premium), 
SAE measurements, 1/16" graduation, ABS plastic case with rubber grip
Series: FATMAX (Stanley's premium line)
Rating: 4.58 stars (357 reviews) - highly rated!
Contract: RCOC 7803 - Hammers, Tape Measures, Levels
Quantity Bid: 35 units (BULK ORDER - second largest quantity)
Extended Supplier Cost: $689.50
Extended Bid Price: $896.35
Delivery: February 4, 2026
Stock Status: In Stock

⚡ BULK ITEM: 35 units = 34% of total contract value
🎯 PREMIUM PRODUCT: Stanley FATMAX on sale (20% discount)
✅ EXCEEDS SPEC: 1-1/4" blade (better than required 1")

Date: January 31, 2026'''
    },
    {
        'NAME': 'Nylon Twine #18 x 250 ft, Orange (Yellow substitute)',
        'PRODUCT CATEGORY': 'Hardware - Cordage & Rope',
        'SUPPLIER': 'Zoro',
        'UNIT PRICE': '$8.75',
        'Description': '''ZORO SELECT Nylon Twine #18
Manufacturer Part #: 89O-WA
Zoro SKU: 89O-WA (Color: Orange)
UOM: Each (250 ft spool)
Supplier Cost: $8.75
Bid Price: $11.64 (33% markup)

Specs: Nylon material, #18 size, 250 feet per spool, Orange color
NOTE: Orange substituted for yellow (yellow not available)
Justification: "All brands acceptable" + exact material/size specs met
Contract: RCOC 7803 - Hammers, Tape Measures, Levels
Quantity Bid: 20 units
Extended Supplier Cost: $175.00
Extended Bid Price: $232.80
Delivery: February 4, 2026
Stock Status: Available

⚠️ COLOR SUBSTITUTION: Orange for yellow (functionally equivalent for visibility)
✅ SPECS MATCH: Nylon, #18, 250 ft all correct

Date: January 31, 2026'''
    },
]

print(f'📦 Adding {len(products)} RCOC 7803 products to NEXUS...\n')

added = 0
for product in products:
    try:
        # Create the record
        result = table.create(product)
        print(f'✅ Added: {product["NAME"]}')
        print(f'   Supplier: {product["SUPPLIER"]} | Price: {product["UNIT PRICE"]}')
        added += 1
    except Exception as e:
        print(f'❌ Error adding {product["NAME"]}: {str(e)}')

print(f'\n🎉 Successfully added {added}/{len(products)} products to NEXUS!')
print('\n📊 RCOC 7803 Summary:')
print('   Contract: RCOC 7803 - Hammers, Tape Measures, and Levels')
print('   Bid Due: February 6, 2026')
print('   Total Items: 123 units across 6 products')
print('   Supplier Cost: $2,018.80')
print('   Bid Amount: $2,641.10')
print('   Profit Margin: 30.8% ($622.30)')
print('   All Supplier: Zoro (single source)')
print('')
print('✅ Products now searchable in NEXUS Product Catalog!')
