#!/usr/bin/env python3
"""
Add RCOC 7777 Welding Supplies Products to NEXUS GPSS PRODUCTS Table
All 17 items with complete supplier information
"""

import os
import requests

# Load environment variables manually
env_path = '/Users/deedavis/NEXUS BACKEND/.env'
with open(env_path, 'r') as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            key, value = line.split('=', 1)
            os.environ[key] = value

AIRTABLE_API_KEY = os.environ.get('AIRTABLE_API_KEY')
AIRTABLE_BASE_ID = os.environ.get('AIRTABLE_BASE_ID')
TABLE_NAME = 'GPSS PRODUCTS'

headers = {
    'Authorization': f'Bearer {AIRTABLE_API_KEY}',
    'Content-Type': 'application/json'
}

# All 17 welding products from RCOC 7777
products = [
    # ITEM 1
    {
        'NAME': 'Jackson Safety 170SB Headgear HDG20 Faceshield',
        'PRODUCT CATEGORY': 'Welding Supplies - Safety Equipment',
        'SUPPLIER': 'Zoro',
        'UNIT PRICE': '$25.55/ea',
        'Description': '''Jackson Safety 138-14940
Zoro SKU: G622449406
Qty: 5 @ $25.55/ea
Total: $127.75

Product: Jackson 170SB Headgear for HDG20 Faceshield
Contract: RCOC RFQ 7777 Welding Supplies
Date: 2026-01-29
Delivery: Feb 3

NOTE: NO SUBSTITUTIONS - Exact Jackson 170SB required per RCOC spec.'''
    },
    
    # ITEM 2
    {
        'NAME': 'Jackson Face Shield 15.5x8 Acetate Clear',
        'PRODUCT CATEGORY': 'Welding Supplies - Safety Equipment',
        'SUPPLIER': 'Zoro',
        'UNIT PRICE': '$11.35/ea',
        'Description': '''Jackson Safety 29052
Zoro SKU: G3036756
Qty: 10 @ $11.35/ea
Total: $113.50

Product: Faceshield, Acetate, Uncoated, Clear, 8" x 15.5"
Fits: Jackson 170SB Headgear
Contract: RCOC RFQ 7777
Date: 2026-01-29
Delivery: Feb 3

NOTE: NO SUBSTITUTIONS - Must fit Jackson 170SB headgear.'''
    },
    
    # ITEM 3
    {
        'NAME': 'Tweco MIG Gun Nozzle WS24A-62 Slip-On 5/8"',
        'PRODUCT CATEGORY': 'Welding Supplies - MIG Gun Parts',
        'SUPPLIER': 'Zoro',
        'UNIT PRICE': '$7.89/pk2 ($3.95/ea)',
        'Description': '''Tweco 12401556
Zoro SKU: G2981587
Qty Needed: 5 each (buy 3 packs = 6 nozzles)
Cost: $23.67

Product: Nozzle, Slip-On, Bore 5/8"
Pack: 2 nozzles per pack
Contract: RCOC RFQ 7777
Date: 2026-01-29

NOTE: Equivalents acceptable per RCOC.'''
    },
    
    # ITEM 4
    {
        'NAME': 'Tweco Contact Tip WS14-35 .035" Wire (PK25)',
        'PRODUCT CATEGORY': 'Welding Supplies - MIG Gun Parts',
        'SUPPLIER': 'Zoro',
        'UNIT PRICE': '$13.99/pk25 (ON SALE - was $15.39)',
        'Description': '''Tweco 11401167
Zoro SKU: G2175214
Qty Needed: 10 tips (buy 1 pack = 25 tips - extras!)
Cost: $13.99
SAVINGS: 9% OFF!

Product: Contact Tip, Tweco WS14-35, Threaded, Copper, .035" wire
Pack: 25 tips per pack
Contract: RCOC RFQ 7777
Date: 2026-01-29

NOTE: Equivalents acceptable. Great price - on sale!'''
    },
    
    # ITEM 5
    {
        'NAME': 'Tweco Wire Conduit Liner Series 44 15ft Max .045',
        'PRODUCT CATEGORY': 'Welding Supplies - MIG Gun Parts',
        'SUPPLIER': 'Zoro',
        'UNIT PRICE': '$17.99/ea',
        'Description': '''Tweco 14401140
Zoro SKU: G2338472
Qty: 3 @ $17.99/ea
Total: $53.97

Product: Conduit Liner, Series 44, 15 ft length, Max 0.045" wire
Contract: RCOC RFQ 7777
Date: 2026-01-29

NOTE: Equivalents acceptable per RCOC.'''
    },
    
    # ITEM 6
    {
        'NAME': 'Powerweld Standard Torch Tip Cleaner Set TC-1',
        'PRODUCT CATEGORY': 'Welding Supplies - Torch Accessories',
        'SUPPLIER': 'Zoro',
        'UNIT PRICE': '$7.80/4pk ($1.95/ea)',
        'Description': '''Powerweld TC-1
Zoro SKU: G104190970
Qty Needed: 5 sets (buy 8 = 2 packs)
Cost: $15.60

Product: Standard Tip Cleaner Set
Sold in multiples of 4
Contract: RCOC RFQ 7777
Date: 2026-01-29
Delivery: Feb 9

NOTE: Any brand acceptable.'''
    },
    
    # ITEM 7
    {
        'NAME': 'Shurlite Three Flint Spark Lighter 4501',
        'PRODUCT CATEGORY': 'Welding Supplies - Torch Accessories',
        'SUPPLIER': 'Zoro',
        'UNIT PRICE': '$43.50/6pk ($7.25/ea)',
        'Description': '''Shurlite 4501
Zoro SKU: G014581783
Qty Needed: 20 lighters (buy 24 = 4 packs)
Cost: $174.00

Product: THREE Flint Spark Lighter (better than single flint!)
Sold in multiples of 6
Contract: RCOC RFQ 7777
Date: 2026-01-29
Delivery: Feb 9
Stock: Limited

NOTE: Equivalents acceptable. Three-flint version better than required single-flint.'''
    },
    
    # ITEM 8
    {
        'NAME': 'Lincoln MIG Wire ER70S-6 .035" 44lb Spool',
        'PRODUCT CATEGORY': 'Welding Supplies - Welding Wire',
        'SUPPLIER': 'Zoro',
        'UNIT PRICE': '$283.99/ea',
        'Description': '''Lincoln Electric ED033704
Zoro SKU: G203501233
Qty: 10 spools @ $283.99/ea
Total: $2,839.90

Product: MIG Welding Wire, ER70S-6, .035" diameter, 44 lb spool
Specification: Meets AWS A5.18 ER70S-6 (REQUIRED)
Total Weight: 440 lbs of wire
Contract: RCOC RFQ 7777
Date: 2026-01-29

NOTE: Equivalents acceptable (any brand meeting AWS A5.18 spec).
⚠️ HIGHEST INDIVIDUAL COST ITEM in this bid!'''
    },
    
    # ITEM 9
    {
        'NAME': 'Victor ST1000FC 21" Cutting Torch VIC0381-1641',
        'PRODUCT CATEGORY': 'Welding Supplies - Torches',
        'SUPPLIER': 'Zoro',
        'UNIT PRICE': '$673.99/ea',
        'Description': '''Victor 0381-1641
Zoro SKU: G511390079
Qty: 5 @ $673.99/ea
Total: $3,369.95

Product: Victor ST1000FC Heavy Duty 21" 90° Cutting Torch
Type: 1-piece acetylene torch
Contract: RCOC RFQ 7777
Date: 2026-01-29

Alternative Pricing Checked:
- Airgas: $729.12/ea (more expensive)
- Zoro saves $55.13 per torch!

NOTE: NO SUBSTITUTIONS - Exact Victor 0381-1641 required.
⚠️ SECOND HIGHEST COST ITEM in this bid!'''
    },
    
    # ITEM 10
    {
        'NAME': 'Victor Acetylene Cutting Tip 1-1-101 Size 1',
        'PRODUCT CATEGORY': 'Welding Supplies - Torch Tips',
        'SUPPLIER': 'Zoro',
        'UNIT PRICE': '$22.85/ea',
        'Description': '''Victor 0330-0005
Zoro SKU: G1559467
Qty: 8 @ $22.85/ea
Total: $182.80

Product: Victor Acetylene Cutting Tip, Size 1 (1-1-101)
Contract: RCOC RFQ 7777
Date: 2026-01-29
Delivery: Feb 3

NOTE: NO SUBSTITUTIONS - Victor or Praxair only.'''
    },
    
    # ITEM 11
    {
        'NAME': 'Miller AccuLock MDX-250 MIG Consumable Kit .035',
        'PRODUCT CATEGORY': 'Welding Supplies - MIG Gun Parts',
        'SUPPLIER': 'BakersGas.com',
        'UNIT PRICE': '$70.80/ea (ON SALE - was $77.80)',
        'Description': '''Miller Electric 1880276
BakersGas SKU: MIL1880276
Qty: 5 kits @ $70.80/ea
Total: $354.00
SAVINGS: $7/kit on sale!

Product: Miller AccuLock MDX-250 MIG Consumable Rebuild Kit, .035" wire
Includes: Contact Tip Adapter, Nozzle, Nozzle Adapter, 10 Contact Tips
For: MDX 250 AccuLock MIG Gun
Contract: RCOC RFQ 7777
Date: 2026-01-29

NOTE: NO SUBSTITUTIONS - Exact Miller 1880276 required.
Found after rejecting wrong kits: SC101 (wrong model), 234611 (M-25 gun not MDX-250).'''
    },
    
    # ITEM 12
    {
        'NAME': 'Victor 8-MFTA Rosebud Heating Tip VIC0330-0528',
        'PRODUCT CATEGORY': 'Welding Supplies - Torch Tips',
        'SUPPLIER': 'Airgas',
        'UNIT PRICE': '$197.00/ea',
        'Description': '''Victor 0330-0528 (341-0330-0528)
Airgas Part: VIC0330-0528
Qty: 10 @ $197.00/ea
Total: $1,970.00

Product: Victor Professional Heating Tip, Type MFTA (Multi-Flame Tip Array), Size 8
Heavy-duty specialized rosebud tip
Contract: RCOC RFQ 7777
Date: 2026-01-29

Alternative Pricing:
- Zoro: $245.99/ea (more expensive!)
- Airgas saves $489.90 total

NOTE: Equivalents acceptable per RCOC, but bidding exact part.
This is a specialized $200 MFTA tip (not standard $25 rosebud).
⚠️ THIRD HIGHEST COST ITEM in this bid!'''
    },
    
    # ITEM 13
    {
        'NAME': 'Victor Acetylene Cutting Tip Size 2',
        'PRODUCT CATEGORY': 'Welding Supplies - Torch Tips',
        'SUPPLIER': 'Zoro',
        'UNIT PRICE': '$21.39/ea',
        'Description': '''Victor 0330-0006
Zoro SKU: G1559467
Qty: 5 @ $21.39/ea
Total: $106.95

Product: Victor Acetylene Cutting Tip, Size 2
Contract: RCOC RFQ 7777
Date: 2026-01-29
Delivery: Feb 3

NOTE: NO SUBSTITUTIONS - Victor or Praxair only.'''
    },
    
    # ITEM 14
    {
        'NAME': 'Victor Acetylene Cutting Tip Size 5',
        'PRODUCT CATEGORY': 'Welding Supplies - Torch Tips',
        'SUPPLIER': 'Zoro',
        'UNIT PRICE': '$22.49/ea',
        'Description': '''Victor 0330-0008
Zoro SKU: G6779446
Qty: 20 @ $22.49/ea (HIGHEST QUANTITY!)
Total: $449.80

Product: Victor Cutting Tip, 1 Piece, Size 5, Acetylene
Contract: RCOC RFQ 7777
Date: 2026-01-29
Delivery: Feb 3

NOTE: NO SUBSTITUTIONS - Victor or Praxair only.
⚠️ This is the highest quantity item in the entire bid!'''
    },
    
    # ITEM 15
    {
        'NAME': 'Hypertherm 65A Fine Cutting Tip 428931 (PK5)',
        'PRODUCT CATEGORY': 'Welding Supplies - Plasma Cutter Parts',
        'SUPPLIER': 'BakersGas.com',
        'UNIT PRICE': '$290.00/pk5 ($58/ea)',
        'Description': '''Hypertherm 428931
BakersGas SKU: HYP428931-5
Qty Needed: 5 tips (buy 1 pack = exactly 5)
Cost: $290.00

Product: Hypertherm 65A SmartSYNC Cartridge for Drag Cutting (Fine Tip)
For: Hypertherm Powermax 65A Plasma Cutter
Pack: 5 tips per pack
Contract: RCOC RFQ 7777
Date: 2026-01-29

NOTE: NO SUBSTITUTIONS - Exact Hypertherm part required.'''
    },
    
    # ITEM 16
    {
        'NAME': 'Hypertherm 45-85A Gouge Tip 428932 (PK5)',
        'PRODUCT CATEGORY': 'Welding Supplies - Plasma Cutter Parts',
        'SUPPLIER': 'BakersGas.com',
        'UNIT PRICE': '$300.00/pk5 ($60/ea)',
        'Description': '''Hypertherm 428932
BakersGas SKU: HYP428932-5
Qty Needed: 5 tips (buy 1 pack = exactly 5)
Cost: $300.00

Product: Hypertherm 45-85A SmartSYNC Cartridge For Max Removal Gouging
For: Hypertherm Powermax 65A Plasma Cutter
Pack: 5 tips per pack
Contract: RCOC RFQ 7777
Date: 2026-01-29

NOTE: NO SUBSTITUTIONS - Exact Hypertherm part required.'''
    },
    
    # ITEM 17
    {
        'NAME': 'Hypertherm Cartridge Adapter Duramax 428951',
        'PRODUCT CATEGORY': 'Welding Supplies - Plasma Cutter Parts',
        'SUPPLIER': 'BakersGas.com',
        'UNIT PRICE': '$126.00/ea',
        'Description': '''Hypertherm 428951
BakersGas SKU: HYP428951
Qty: 5 @ $126.00/ea
Total: $630.00

Product: Hypertherm Cartridge Adapter for Duramax Hand or Mechanized Torches
For: Hypertherm Powermax 65A Plasma Cutter
Contract: RCOC RFQ 7777
Date: 2026-01-29

NOTE: NO SUBSTITUTIONS - Exact Hypertherm part required.'''
    }
]

print(f"Adding {len(products)} RCOC 7777 Welding Products to NEXUS...\n")

url = f'https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{TABLE_NAME}'

success_count = 0
for i, product in enumerate(products, 1):
    try:
        response = requests.post(
            url,
            headers=headers,
            json={'fields': product}
        )
        
        if response.status_code == 200:
            success_count += 1
            print(f"✅ {i}. Added: {product['NAME']}")
            print(f"   Supplier: {product['SUPPLIER']} | Price: {product['UNIT PRICE']}")
        else:
            print(f"❌ {i}. FAILED: {product['NAME']}")
            print(f"   Error: {response.text}")
    
    except Exception as e:
        print(f"❌ {i}. ERROR: {product['NAME']}")
        print(f"   Exception: {str(e)}")
    
    print()

print(f"\n{'='*60}")
print(f"COMPLETE: {success_count}/{len(products)} products added to NEXUS!")
print(f"{'='*60}")
print(f"\nRCOC 7777 WELDING SUPPLIES - FULL BID SUMMARY:")
print(f"Total Cost: $11,015.88")
print(f"Your Bid (12%): $12,337.79")
print(f"Your Profit: $1,321.91")
print(f"\nSuppliers Used:")
print(f"  - Zoro: $7,471.68 (12 items)")
print(f"  - BakersGas.com: $1,574.00 (4 items)")
print(f"  - Airgas: $1,970.00 (1 item)")
