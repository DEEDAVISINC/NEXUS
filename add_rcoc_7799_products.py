#!/usr/bin/env python3
"""
Add RCOC 7799 Products to NEXUS
Adds all 8 products from RCOC 7799 (Grease and Air Couplers) to GPSS PRODUCTS table
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

# Define all 8 RCOC 7799 products with complete details
products = [
    {
        'NAME': 'EATON Aeroquip Hydraulic Quick Connect Coupler Female 5601-8-10S',
        'PRODUCT CATEGORY': 'Hydraulic Fittings - Quick Couplers',
        'SUPPLIER': 'Zoro',
        'UNIT PRICE': '$42.60',
        'Description': '''EATON AEROQUIP 5601-8-10S Hydraulic Quick Connect Coupler
Manufacturer Part #: 5601-8-10S
Zoro SKU: G1343833
UOM: Each
Supplier Cost: $42.60
Bid Price: $53.25 (25% markup)

⚠️ BRAND SPECIFIC - NO SUBSTITUTIONS (Aeroquip/Eaton only)

Specs: Steel body, sleeve lock, 1/2"-14 thread size, 5600 Series
Type: Female coupler for spinner/auger equipment
Contract: RCOC 7799 - Grease and Air Couplers
Quantity Bid: 40 units
Extended Supplier Cost: $1,704.00
Extended Bid Price: $2,130.00
Delivery: February 4, 2026
Stock Status: In Stock

NOTE: This is a premium hydraulic fitting. RCOC specified Aeroquip brand only - no substitutions allowed.

Date: January 31, 2026'''
    },
    {
        'NAME': 'EATON Aeroquip Hydraulic Quick Connect Coupler Male 5602-8-10S',
        'PRODUCT CATEGORY': 'Hydraulic Fittings - Quick Couplers',
        'SUPPLIER': 'Zoro',
        'UNIT PRICE': '$19.86',
        'Description': '''EATON AEROQUIP 5602-8-10S Hydraulic Quick Connect Coupler
Manufacturer Part #: 5602-8-10S
Zoro SKU: G3022984
UOM: Each
Supplier Cost: $19.86
Bid Price: $25.42 (28% markup)

⚠️ BRAND SPECIFIC - NO SUBSTITUTIONS (Aeroquip/Eaton only)

Specs: Steel body, sleeve lock, 1/2"-14 thread size, 5600 Series
Type: Male coupler for spinner/auger equipment
Contract: RCOC 7799 - Grease and Air Couplers
Quantity Bid: 40 units
Extended Supplier Cost: $794.40
Extended Bid Price: $1,016.80
Delivery: February 4, 2026 (estimated)
Stock Status: Available

NOTE: Male coupler is significantly cheaper than female ($19.86 vs $42.60). RCOC specified Aeroquip brand only.

Date: January 31, 2026'''
    },
    {
        'NAME': 'Milton 745 Air Coupler Body 1/4" NPT Female (A-Style Compatible)',
        'PRODUCT CATEGORY': 'Pneumatic Fittings - Air Couplers',
        'SUPPLIER': 'Zoro',
        'UNIT PRICE': '$15.61',
        'Description': '''MILTON 745 Coupler Body 1/4" NPT Female
Manufacturer Part #: 745
Zoro SKU: G702650777
UOM: Each
Supplier Cost: $15.61
Bid Price: $20.84 (33% markup)

Specs: 1/4" NPT female threads, compatible with A, M, or T style plugs
Reference: Milton S-775 or equivalent (all brands acceptable)
Contract: RCOC 7799 - Grease and Air Couplers
Quantity Bid: 30 units
Extended Supplier Cost: $468.30
Extended Bid Price: $625.20
Delivery: February 11, 2026
Stock Status: Limited Stock

NOTE: Milton 745 works with A-style plugs as referenced in RFQ. Contract starts March 1 so Feb 11 delivery is fine.

Date: January 31, 2026'''
    },
    {
        'NAME': 'Milton MI1815S 1/2" NPT Female G-Style Quick Coupler',
        'PRODUCT CATEGORY': 'Pneumatic Fittings - Air Couplers',
        'SUPPLIER': 'Zoro',
        'UNIT PRICE': '$53.15',
        'Description': '''MILTON MI1815S 1/2" Female NPT G-Style Air Coupler
Manufacturer Part #: MI1815S (1815S)
Zoro SKU: G310771697
UOM: Each
Supplier Cost: $53.15
Bid Price: $66.44 (25% markup)

Specs: 1/2" x 1/2" Female NPT, G-Style industrial quick coupler
Reference: Milton 1815 G Style or equivalent (all brands acceptable)
Contract: RCOC 7799 - Grease and Air Couplers
Quantity Bid: 20 units
Extended Supplier Cost: $1,063.00
Extended Bid Price: $1,328.80
Delivery: Standard delivery
Stock Status: In Stock

NOTE: 1/2" industrial couplers are more expensive than 1/4" sizes. G-style is industrial standard.

Date: January 31, 2026'''
    },
    {
        'NAME': 'Milton S-777 1/4" Male Plug A-Style Air Coupling (Pack of 3)',
        'PRODUCT CATEGORY': 'Pneumatic Fittings - Air Couplers',
        'SUPPLIER': 'Zoro',
        'UNIT PRICE': '$5.49',
        'Description': '''MILTON S-777 1/4" Male Plug A-Style
Manufacturer Part #: S-777
Zoro SKU: G502652599
UOM: Each (sold in packs of 3 for $16.47)
Supplier Cost: $5.49 per unit
Bid Price: $7.14 (30% markup - bulk pricing)

Specs: 1/4" male plug, A-style air coupling, 2 per card
Reference: Milton S-777 or equivalent (all brands acceptable)
Contract: RCOC 7799 - Grease and Air Couplers
Quantity Bid: 50 units (BULK ORDER - largest flexible-item quantity)
Packs Needed: 17 packs of 3 = 51 units (1 extra)
Extended Supplier Cost: $279.99 (for 51 units)
Extended Bid Price: $357.00 (for 50 units)
Delivery: February 4, 2026
Stock Status: In Stock

⚡ BULK ITEM: 50 units at excellent price ($5.49 each)
Competitive 30% markup for bulk pricing

Date: January 31, 2026'''
    },
    {
        'NAME': 'Milton 133 Safety Blow Gun with 10" Extension',
        'PRODUCT CATEGORY': 'Pneumatic Tools - Blow Guns',
        'SUPPLIER': 'Zoro',
        'UNIT PRICE': '$24.15',
        'Description': '''MILTON 133 Safety Blow Gun 10" Extension
Manufacturer Part #: 133
Zoro SKU: G5034611
UOM: Each
Supplier Cost: $24.15
Bid Price: $32.15 (33% markup)

Specs: 17 1/4" overall length, 10" extension, with safety relief
Reference: Milton 133 or equivalent (all brands acceptable)
Contract: RCOC 7799 - Grease and Air Couplers
Quantity Bid: 5 units
Extended Supplier Cost: $120.75
Extended Bid Price: $160.75
Delivery: February 10, 2026
Stock Status: In Stock

NOTE: Two options available - selected 17 1/4" option at $24.15 vs 13 1/4" at $47.19 (better value)

Date: January 31, 2026'''
    },
    {
        'NAME': 'LOCKNLUBE 353 Professional Series Grease Gun 7500 PSI',
        'PRODUCT CATEGORY': 'Lubrication Equipment - Grease Guns',
        'SUPPLIER': 'LOCKNLUBE Direct',
        'UNIT PRICE': '$119.99',
        'Description': '''LOCKNLUBE 353 Professional Series Dual-Mode Pistol Grip Grease Gun
Manufacturer Part #: 353 (LNL353)
Source: LOCKNLUBE direct / Amazon
UOM: Each
Supplier Cost: $119.99
Bid Price: $150.00 (25% markup)

⚠️ BRAND SPECIFIC - NO SUBSTITUTIONS (LOCKNLUBE 353 or Dynaflo 58874 only)

Specs: 7500+ PSI rating, dual-mode, pistol grip, leak-free design
Series: Professional Series
Rating: 35 reviews (well-rated product)
Contract: RCOC 7799 - Grease and Air Couplers
Quantity Bid: 3 units
Extended Supplier Cost: $359.97
Extended Bid Price: $450.00
Delivery: Standard shipping
Shipping: FREE

NOTE: Premium specialty grease gun. RCOC specified LOCKNLUBE brand only - no other substitutions. Alternative allowed: Dynaflo 58874.

Date: January 31, 2026'''
    },
    {
        'NAME': 'Milton 1817 G-Style Plug 1/2" MNPT Coupler Nipple (Pack of 5)',
        'PRODUCT CATEGORY': 'Pneumatic Fittings - Coupler Nipples',
        'SUPPLIER': 'Zoro',
        'UNIT PRICE': '$4.48',
        'Description': '''MILTON 1817 G-Style Plug 1/2" MNPT
Manufacturer Part #: 1817
Zoro SKU: G5037061
UOM: Each (sold in packs of 5 for $22.39)
Supplier Cost: $4.48 per unit
Bid Price: $5.98 (33% markup)

Specs: G-Style plug, 1/2" MNPT threads, quick coupler nipple
Reference: Milton 1817 2F G-Style or equivalent (all brands acceptable)
Rating: 5 stars (1 review)
Contract: RCOC 7799 - Grease and Air Couplers
Quantity Bid: 10 units
Packs Needed: 2 packs of 5
Extended Supplier Cost: $44.78 (for 10 units)
Extended Bid Price: $59.80
Delivery: Standard delivery
Stock Status: Available

NOTE: Sold in packs of 5. Need 2 packs for 10 units. Excellent price at $4.48 per unit.

Date: January 31, 2026'''
    },
]

print(f'📦 Adding {len(products)} RCOC 7799 products to NEXUS...\n')

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
print('\n📊 RCOC 7799 Summary:')
print('   Contract: RCOC 7799 - Grease and Air Couplers')
print('   Bid Due: February 6, 2026')
print('   Total Items: 198 units across 8 products')
print('   Supplier Cost: $4,835.19')
print('   Bid Amount: $6,128.35')
print('   Profit Margin: 26.7% ($1,293.16)')
print('   Primary Supplier: Zoro (7 items) + LOCKNLUBE direct (1 item)')
print('   ⚠️ Brand-Specific Items: 3 (Aeroquip couplers + LOCKNLUBE grease gun)')
print('')
print('✅ Products now searchable in NEXUS Product Catalog!')
