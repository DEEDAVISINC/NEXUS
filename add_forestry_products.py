#!/usr/bin/env python3
"""
Add RCOC 7734 Forestry Products to NEXUS
Adds all TreeStuff products with SKU numbers from Quote Q-52998
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

# Get API credentials
api_key = os.environ.get('AIRTABLE_API_KEY')
base_id = os.environ.get('AIRTABLE_BASE_ID')

if not api_key or not base_id:
    print('❌ ERROR: Missing AIRTABLE_API_KEY or AIRTABLE_BASE_ID')
    exit(1)

api = Api(api_key)
table = api.table(base_id, 'GPSS PRODUCTS')

# ALL FORESTRY PRODUCTS FROM TREESTUFF QUOTE Q-52998
products = [
    {
        'NAME': 'DMM Ultra "O" Auto Locking Oval Carabiner',
        'PRODUCT CATEGORY': 'Forestry Equipment - Carabiners',
        'SUPPLIER': 'TreeStuff',
        'UNIT PRICE': '41.99/each',
        'Description': '''TreeStuff SKU: 33166
Manufacturer: DMM
Model: Ultra O Auto Locking
Type: Aluminum oval shaped carabiner
Quote: Q-52998 (Jan 30, 2026)
Contract: RCOC RFQ 7734
Cost: $41.99/each (tax-exempt)

Auto-locking carabiner for tree climbing/arborist work.'''
    },
    {
        'NAME': 'DMM Triple Attachment Pulley 2 - Red',
        'PRODUCT CATEGORY': 'Forestry Equipment - Pulleys',
        'SUPPLIER': 'TreeStuff',
        'UNIT PRICE': '106.99/each',
        'Description': '''TreeStuff SKU: 99863
Manufacturer: DMM
Model: Triple Attachment Pulley 2
Color: Red
Quote: Q-52998 (Jan 30, 2026)
Contract: RCOC RFQ 7734
Cost: $106.99/each (tax-exempt)

Hitch climber pulley for tree climbing.'''
    },
    {
        'NAME': 'CT X-Arbor Helmet - Black',
        'PRODUCT CATEGORY': 'Forestry Equipment - Safety Gear',
        'SUPPLIER': 'TreeStuff',
        'UNIT PRICE': '101.99/each',
        'Description': '''TreeStuff SKU: 24791 (DISCONTINUED - LIMITED STOCK)
Manufacturer: Climbing Technology (CT)
Model: X-Arbor Helmet
Color: Black
Quote: Q-52998 (Jan 30, 2026)
Contract: RCOC RFQ 7734
Cost: $101.99/each (tax-exempt)

⚠️ DISCONTINUED ITEM - TreeStuff only has 7 in stock (need 10 total)
Alternative suppliers: Sherrill Tree, Wesspur
Compatible with 3M PELTOR earmuffs'''
    },
    {
        'NAME': '3M PELTOR Helmet Attached Earmuffs X4P3E',
        'PRODUCT CATEGORY': 'Forestry Equipment - Safety Gear',
        'SUPPLIER': 'TreeStuff',
        'UNIT PRICE': '42.99/each',
        'Description': '''TreeStuff SKU: 100599
Manufacturer: 3M PELTOR
Model: X4P3E
Type: Helmet-attached earmuffs
Quote: Q-52998 (Jan 30, 2026)
Contract: RCOC RFQ 7734
Cost: $42.99/each (tax-exempt)

Compatible with CT X-Arbor helmet (Item 24791)'''
    },
    {
        'NAME': 'Petzl Bucket Rope Bag - Black - 30L',
        'PRODUCT CATEGORY': 'Forestry Equipment - Rope Bags',
        'SUPPLIER': 'TreeStuff',
        'UNIT PRICE': '84.99/each',
        'Description': '''TreeStuff SKU: PRBKT-BK-30L
Manufacturer: Petzl
Model: Bucket Rope Bag
Color: Black
Capacity: 30L
Quote: Q-52998 (Jan 30, 2026)
Contract: RCOC RFQ 7734
Cost: $84.99/each (tax-exempt)'''
    },
    {
        'NAME': 'Notch Acculine Throwline 2.2mm - 180 ft',
        'PRODUCT CATEGORY': 'Forestry Equipment - Throwlines',
        'SUPPLIER': 'TreeStuff',
        'UNIT PRICE': '39.99/each',
        'Description': '''TreeStuff SKU: NTL22-180
Manufacturer: Notch
Model: Acculine
Diameter: 2.2mm
Length: 180 ft
Quote: Q-52998 (Jan 30, 2026)
Contract: RCOC RFQ 7734
Cost: $39.99/each (tax-exempt)'''
    },
    {
        'NAME': 'Notch Pro Folding Cube',
        'PRODUCT CATEGORY': 'Forestry Equipment - Storage',
        'SUPPLIER': 'TreeStuff',
        'UNIT PRICE': '78.99/each',
        'Description': '''TreeStuff SKU: 32443
Manufacturer: Notch
Model: Pro Folding Cube
Quote: Q-52998 (Jan 30, 2026)
Contract: RCOC RFQ 7734
Cost: $78.99/each (tax-exempt)'''
    },
    {
        'NAME': 'Notch Zero Throw Weight 14oz',
        'PRODUCT CATEGORY': 'Forestry Equipment - Throw Weights',
        'SUPPLIER': 'TreeStuff',
        'UNIT PRICE': '27.99/each',
        'Description': '''TreeStuff SKU: NTW2-14
Manufacturer: Notch
Model: ZERO
Weight: 14oz (397g)
Quote: Q-52998 (Jan 30, 2026)
Contract: RCOC RFQ 7734
Cost: $27.99/each (tax-exempt)'''
    },
    {
        'NAME': 'CMI Arborist Block RP145',
        'PRODUCT CATEGORY': 'Forestry Equipment - Rigging Blocks',
        'SUPPLIER': 'TreeStuff',
        'UNIT PRICE': '141.99/each',
        'Description': '''TreeStuff SKU: 12974
Manufacturer: CMI (Climbing Manufacturing Inc)
Model: RP145
Size: 3/4 inch
Type: Zinc-plated arborist rigging block
Quote: Q-52998 (Jan 30, 2026)
Contract: RCOC RFQ 7734
Cost: $141.99/each (tax-exempt)'''
    },
    {
        'NAME': 'DMM Oval Locksafe Steel Carabiner',
        'PRODUCT CATEGORY': 'Forestry Equipment - Carabiners',
        'SUPPLIER': 'TreeStuff',
        'UNIT PRICE': '43.99/each',
        'Description': '''TreeStuff SKU: 13606
Manufacturer: DMM
Model: Oval Locksafe
Material: Steel
Quote: Q-52998 (Jan 30, 2026)
Contract: RCOC RFQ 7734
Cost: $43.99/each (tax-exempt)

Steel construction (vs aluminum Ultra O)'''
    },
    {
        'NAME': 'Sterling Banshee Climbing Line 7/16 x 150 ft',
        'PRODUCT CATEGORY': 'Forestry Equipment - Climbing Ropes',
        'SUPPLIER': 'TreeStuff',
        'UNIT PRICE': '230.99/each',
        'Description': '''TreeStuff SKU: BNSE-150-TS
Manufacturer: Sterling Rope
Model: Banshee
Diameter: 7/16 inch (11.7mm)
Length: 150 ft
Strand: 24-strand (NOT 16-strand as in RFQ)
Splice: One tight eye splice
Quote: Q-52998 (Jan 30, 2026)
Contract: RCOC RFQ 7734
Cost: $230.99/each (tax-exempt)

⚠️ NOTE: RFQ requested 16-strand, TreeStuff quoted 24-strand
May need to verify with Shari Graves if substitution acceptable'''
    }
]

print('🚀 ADDING 11 FORESTRY PRODUCTS TO NEXUS...\n')

added_count = 0
for product in products:
    try:
        result = table.create(product)
        print(f"✅ Added: {product['NAME']}")
        print(f"   SKU: {product['Description'].split('SKU: ')[1].split('\\n')[0] if 'SKU:' in product['Description'] else 'N/A'}")
        print(f"   Price: ${product['UNIT PRICE']}")
        print()
        added_count += 1
    except Exception as e:
        print(f"❌ ERROR adding {product['NAME']}: {e}\n")

print(f"\n✅ SUCCESS! Added {added_count} of 11 products to NEXUS!")
print(f"\n📊 TreeStuff Quote: $4,978.35 (tax-exempt)")
print(f"🔍 All SKU numbers now searchable in NEXUS Product Catalog!")
print(f"\n⚠️ MISSING ITEMS STILL NEEDED:")
print(f"   - 3 more CT X-Arbor helmets (only 7 available)")
print(f"   - 10 face shields/visors")
print(f"   - 5 positioning lanyards (16 ft)")
print(f"   - 2 climbing ropes (16-strand)")
print(f"   - 10 prusik cords (28\" and 30\")")
