#!/usr/bin/env python3
"""
Add Pelican 16-Strand Arborist Rope to NEXUS Product Catalog
RCOC RFQ 7734 - Item 12
Source: Amazon (U.S. Rigging Supply)
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
AIRTABLE_API_KEY = os.getenv('AIRTABLE_PERSONAL_ACCESS_TOKEN')
BASE_ID = 'appwTENYFFLFC6Wwc'
TABLE_NAME = 'GPSS PRODUCTS'

# Initialize API and table
api = Api(AIRTABLE_API_KEY)
table = api.table(BASE_ID, TABLE_NAME)

# Pelican 16-Strand Arborist Rope product data
product = {
    'NAME': 'Pelican 16-Strand Arborist Rope - 1/2" x 150 ft with Spliced Eye',
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
Contract: RCOC RFQ 7734 - Item 12
Quote Date: January 30, 2026
Unit Cost: $150.19 (Business Price, was $169.98)
Seller: U.S. Rigging Supply (Amazon)
Seller Credentials: Business Hour Delivery, SBA Small Business, 889 Cert, ISO 9001
Rating: 4.5/5 stars (56 reviews)
Availability: In stock, ships 2-3 days
Delivery Time: Feb 11-13, 2026
Return Policy: 30-day refund/replacement

Amazon Product URL: https://www.amazon.com/dp/B08W2QHDHJ

Alternative Sources:
- Pelican Rope Direct: pelicanrope.com
- Phone: Available through U.S. Rigging Supply

Specifications from manufacturer:
- 100% polyester strands
- Tested tensile strength: 7,150 lbs (reduces to 5,400 with splice)
- Tightly-woven 16-strand with high twist core
- Torque-balanced polyester keeps line firm and round
- Suitable for: Tree work, arborist climbing, fixed line ascension, load hauling
- Not suitable for dynamic/lead climbing

Notes:
- Tax-exempt for government contracts
- Quantity needed for RCOC: 2 bags (2 ropes)
- Total RCOC cost: $300.38 (2 × $150.19)'''
}

print("Adding Pelican 16-Strand Arborist Rope to NEXUS Product Catalog...")
print(f"Product: {product['NAME']}")
print(f"Supplier: {product['SUPPLIER']}")
print(f"Unit Price: ${product['UNIT PRICE']}")
print()

try:
    record = table.create(product)
    print(f"✅ SUCCESS! Record created with ID: {record['id']}")
    print(f"Product added to GPSS PRODUCTS table")
    print()
    print("Product Details:")
    print(f"  - Amazon ASIN: B08W2QHDHJ")
    print(f"  - Manufacturer: Pelican Rope")
    print(f"  - Diameter: 1/2 inch (12.7mm)")
    print(f"  - Length: 150 ft with spliced eye")
    print(f"  - Construction: 16-strand")
    print(f"  - Strength: 5,400 lbs MBS")
    print(f"  - Price: $150.19 each")
    print(f"  - Contract: RCOC RFQ 7734 Item 12")
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    print("Failed to add product to Airtable")
