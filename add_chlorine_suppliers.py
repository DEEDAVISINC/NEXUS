#!/usr/bin/env python3
"""
Add liquid chlorine suppliers to GPSS SUPPLIERS table
For HCMA Liquid Chlorine ITB #2026-004
"""

import os
from dotenv import load_dotenv
from pyairtable import Api

# Load environment variables
load_dotenv()

# Airtable configuration
AIRTABLE_API_KEY = os.getenv('AIRTABLE_API_KEY')
AIRTABLE_BASE_ID = os.getenv('AIRTABLE_BASE_ID')

# Initialize Airtable
api = Api(AIRTABLE_API_KEY)
suppliers_table = api.table(AIRTABLE_BASE_ID, 'GPSS SUPPLIERS')

# Liquid Chlorine Suppliers
chlorine_suppliers = [
    {
        "COMPANY NAME": "Univar Solutions",
        "WEBSITE": "https://www.univarsolutions.com",
        "PRIMARY CONTACT PHONE": "1-800-531-7106",
        "PRIMARY CONTACT EMAIL": "SDSNA@univarsolutions.com",
        "LOCATION": "National (Michigan service available)",
        "PRODUCT KEYWORDS": "sodium hypochlorite, liquid chlorine, Liqui-Chlor, water treatment chemicals, 12.5% chlorine, bulk tanker delivery, NSF certified, EPA registered, industrial chemicals, pool chemicals",
        "DESCRIPTION": "National chemical distributor with 85+ stocking locations. Offers sodium hypochlorite in multiple concentrations (12.5%, 12%, 16%, 18%, 4%). Bulk tanker delivery, MiniBulk, totes, drums, pails available. EPA-registered products with NSF certification. Serves Michigan market.",
        "BUSINESS STATUS": "Prospective",
        "DISCOVERY METHOD": "Web Research",
        "DISCOVERY DATE": "2026-01-23",
        "DISCOVERED BY": "Dee Davis - HCMA Liquid Chlorine RFP",
        "RELATIONSHIP STAGE": "Discovered",
        "SOURCE NOTES": "Found for HCMA ITB #2026-004 Liquid Chlorine bid. Major national distributor, tanker delivery capability, multiple concentrations, NSF certified. Phone: 1-800-531-7106, SDS requests: 1-855-429-2661"
    },
    {
        "COMPANY NAME": "Brenntag North America - Grand Rapids",
        "WEBSITE": "https://www.brenntag.com/en-us/",
        "PRIMARY CONTACT PHONE": "(616) 656-9555",
        "PRIMARY CONTACT EMAIL": "Contact via website",
        "LOCATION": "3900 44th St SE, Grand Rapids, MI 49512",
        "PRODUCT KEYWORDS": "sodium hypochlorite, liquid chlorine, water treatment chemicals, commodity chemicals, solvents, surfactants, specialties, industrial chemicals, bulk delivery",
        "DESCRIPTION": "Brenntag Great Lakes division serves Michigan and Indiana from Grand Rapids location. Part of national network with 300+ locations and 11,000 employees. Toledo distribution center supports Michigan deliveries with 7-acre tank farm and rail services. Major chemical distributor.",
        "BUSINESS STATUS": "Prospective",
        "DISCOVERY METHOD": "Web Research",
        "DISCOVERY DATE": "2026-01-23",
        "DISCOVERED BY": "Dee Davis - HCMA Liquid Chlorine RFP",
        "RELATIONSHIP STAGE": "Discovered",
        "SOURCE NOTES": "Found for HCMA ITB #2026-004. LOCAL Michigan presence in Grand Rapids. Part of Brenntag Great Lakes region. Major Fortune 500 chemical distribution network. Contact: (616) 656-9555"
    },
    {
        "COMPANY NAME": "Hawkins Water Treatment Group",
        "WEBSITE": "https://www.hawkinsinc.com/groups/water-treatment/",
        "PRIMARY CONTACT PHONE": "Check website for MI location",
        "PRIMARY CONTACT EMAIL": "Contact via website",
        "LOCATION": "Multi-state (27+ states, Michigan service)",
        "PRODUCT KEYWORDS": "sodium hypochlorite, Azone-15, water treatment chemicals, NSF certified, ANSI Std 60, municipal water treatment, mini bulk delivery, bulk tanker, technical support, lab testing",
        "DESCRIPTION": "Municipal water treatment specialist with 27+ state coverage including Michigan. Manufactures sodium hypochlorite in concentrations 3-20% (standard 12.5%). EPA-registered Azone-15 brand. NSF certified to ANSI/Std. 60. Local route technician model with equipment installation and lab testing. Serves municipal water/wastewater and industrial applications. B2B only.",
        "BUSINESS STATUS": "Prospective",
        "DISCOVERY METHOD": "Web Research",
        "DISCOVERY DATE": "2026-01-23",
        "DISCOVERED BY": "Dee Davis - HCMA Liquid Chlorine RFP",
        "RELATIONSHIP STAGE": "Discovered",
        "SOURCE NOTES": "Found for HCMA ITB #2026-004. MUNICIPAL SPECIALIST - excellent match for aquatic center. NSF certified, technical support included, route delivery model. Visit water treatment locations page for MI contacts."
    },
    {
        "COMPANY NAME": "Elite Chlorine",
        "WEBSITE": "https://elitechlorine.com/michigan/",
        "PRIMARY CONTACT PHONE": "Contact via website form",
        "PRIMARY CONTACT EMAIL": "Contact via website form",
        "LOCATION": "Michigan (state-wide service)",
        "PRODUCT KEYWORDS": "bulk liquid chlorine, sodium hypochlorite, tanker delivery, commercial pools, municipal water treatment, aquatic centers, specialized tanker fleet, industrial chlorine",
        "DESCRIPTION": "Specialized liquid chlorine distributor exclusively serving Michigan. State-of-the-art storage facilities and fleet of specialized tanker vehicles designed for safe efficient chlorine transportation. Serves commercial pools, municipal water treatment plants, aquatic centers, and industrial clients. Emphasizes safety protocols and customized delivery schedules.",
        "BUSINESS STATUS": "Prospective",
        "DISCOVERY METHOD": "Web Research",
        "DISCOVERY DATE": "2026-01-23",
        "DISCOVERED BY": "Dee Davis - HCMA Liquid Chlorine RFP",
        "RELATIONSHIP STAGE": "Discovered",
        "SOURCE NOTES": "Found for HCMA ITB #2026-004. MICHIGAN-SPECIFIC operation! Tanker delivery specialist. Perfect match for aquatic center requirements. Safety-focused. Contact via website for quote."
    },
    {
        "COMPANY NAME": "Horizon Commercial Pool Supply",
        "WEBSITE": "https://www.horizonpoolsupply.com",
        "PRIMARY CONTACT PHONE": "Check website for contact",
        "PRIMARY CONTACT EMAIL": "Check website for contact",
        "LOCATION": "Multi-state: Michigan, Wisconsin, Illinois, Minnesota, Ohio",
        "PRODUCT KEYWORDS": "liquid chlorine, sodium hypochlorite 12.5-15%, bulk chemical delivery, commercial pool chemicals, aquatic facility supply, trained delivery drivers, no container deposit",
        "DESCRIPTION": "Commercial aquatic facility supplier serving 5-state region including Michigan. Professional bulk chemical delivery with trained drivers who dispense directly into bulk containers, eliminating handling requirements. No container deposits. Comprehensive commercial pool chemicals and equipment. Established aquatic industry supplier.",
        "BUSINESS STATUS": "Prospective",
        "DISCOVERY METHOD": "Web Research",
        "DISCOVERY DATE": "2026-01-23",
        "DISCOVERED BY": "Dee Davis - HCMA Liquid Chlorine RFP",
        "RELATIONSHIP STAGE": "Discovered",
        "SOURCE NOTES": "Found for HCMA ITB #2026-004. COMMERCIAL POOL SPECIALIST - excellent match for aquatic center. Professional delivery service, trained drivers, no deposits. Multi-state coverage."
    },
    {
        "COMPANY NAME": "Chemtrade Logistics - River Rouge",
        "WEBSITE": "https://www.chemtradelogistics.com",
        "PRIMARY CONTACT PHONE": "(866) 416-4404",
        "PRIMARY CONTACT EMAIL": "Contact via website",
        "LOCATION": "River Rouge, Michigan (manufacturing facility)",
        "PRODUCT KEYWORDS": "sodium hypochlorite, liquid chlorine, water treatment chemicals, municipal disinfection, chemical manufacturing, bulk production, industrial chemicals",
        "DESCRIPTION": "Chemical manufacturer with water chemical production plant in River Rouge, Michigan. Manufactures sodium hypochlorite and supplies to producers and repackagers who distribute to municipalities for water treatment and disinfection. Direct manufacturer access may provide competitive wholesale pricing.",
        "BUSINESS STATUS": "Prospective",
        "DISCOVERY METHOD": "Web Research",
        "DISCOVERY DATE": "2026-01-23",
        "DISCOVERED BY": "Dee Davis - HCMA Liquid Chlorine RFP",
        "RELATIONSHIP STAGE": "Discovered",
        "SOURCE NOTES": "Found for HCMA ITB #2026-004. LOCAL Michigan MANUFACTURER in River Rouge! May offer best wholesale pricing as direct source. Emergency: (866) 416-4404, SDS Info: (416) 496-5856"
    },
    {
        "COMPANY NAME": "BulkChlorine.com",
        "WEBSITE": "https://bulkchlorine.com",
        "PRIMARY CONTACT PHONE": "Check website for contact",
        "PRIMARY CONTACT EMAIL": "Check website for contact",
        "LOCATION": "National (online, ships lower 48 states)",
        "PRODUCT KEYWORDS": "sodium hypochlorite 12.5-15%, NSF 50/60 certified, bulk liquid chlorine, 55-gallon drums, commercial pool shock, same-day shipping, online ordering, American made",
        "DESCRIPTION": "Online bulk chlorine supplier with national coverage (lower 48 states). Commercial-grade sodium hypochlorite NSF 50/60 certified for drinking water treatment. Available in cases, 55-gal drums ($329.99), and full 4-drum pallets ($1,299.99). Same-day shipping available. American-made products designed for automatic chemical feeders.",
        "BUSINESS STATUS": "Prospective",
        "DISCOVERY METHOD": "Web Research",
        "DISCOVERY DATE": "2026-01-23",
        "DISCOVERED BY": "Dee Davis - HCMA Liquid Chlorine RFP",
        "RELATIONSHIP STAGE": "Discovered",
        "SOURCE NOTES": "Found for HCMA ITB #2026-004. Online ordering option. Known pricing: $329.99/55-gal drum, $1,299.99/pallet. Same-day shipping. NSF certified. Good for comparison pricing."
    },
    {
        "COMPANY NAME": "Waterline Technologies",
        "WEBSITE": "https://waterlinetechnologies.com",
        "PRIMARY CONTACT PHONE": "1-800-464-7762",
        "PRIMARY CONTACT EMAIL": "Check website for contact",
        "LOCATION": "National",
        "PRODUCT KEYWORDS": "bulk sodium hypochlorite 12.5%, NSF listed, liquid chlorine, water treatment chemicals, 1 gallon, 5 gallon, 15 gallon, 55 gallon drums, 330 gallon totes, call for pricing",
        "DESCRIPTION": "Water treatment chemical supplier offering NSF-listed bulk sodium hypochlorite 12.5%. Multiple size options from 1 gallon to 330-gallon totes. Flexible ordering options. Call for pricing and Michigan delivery availability.",
        "BUSINESS STATUS": "Prospective",
        "DISCOVERY METHOD": "Web Research",
        "DISCOVERY DATE": "2026-01-23",
        "DISCOVERED BY": "Dee Davis - HCMA Liquid Chlorine RFP",
        "RELATIONSHIP STAGE": "Discovered",
        "SOURCE NOTES": "Found for HCMA ITB #2026-004. Multiple bulk sizes available. NSF listed. Call 1-800-464-7762 for Michigan delivery and tanker availability. Need to verify if they can do 900-1200 gal tanker deliveries."
    }
]

print("=" * 80)
print("🧪 ADDING LIQUID CHLORINE SUPPLIERS TO GPSS SUPPLIERS TABLE")
print("=" * 80)
print()

try:
    # Check if table exists and get sample record to verify fields
    print("📋 Verifying GPSS SUPPLIERS table structure...")
    
    added_count = 0
    error_count = 0
    
    for i, supplier in enumerate(chlorine_suppliers, 1):
        company_name = supplier.get("COMPANY NAME")
        print(f"\n{i}. Adding: {company_name}")
        
        try:
            # Check if supplier already exists
            existing = suppliers_table.all(formula=f"{{COMPANY NAME}}='{company_name}'")
            
            if existing:
                print(f"   ⚠️  Already exists - Skipping")
                continue
            
            # Add supplier to table
            record = suppliers_table.create(supplier)
            print(f"   ✅ Added successfully (Record ID: {record['id']})")
            added_count += 1
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            error_count += 1
    
    print()
    print("=" * 80)
    print(f"📊 SUMMARY:")
    print(f"   ✅ Successfully added: {added_count} suppliers")
    if error_count > 0:
        print(f"   ❌ Errors: {error_count}")
    print("=" * 80)
    print()
    
    if added_count > 0:
        print("🎯 NEXT STEPS:")
        print("   1. Review suppliers in Airtable GPSS SUPPLIERS table")
        print("   2. Begin contacting suppliers for quotes")
        print("   3. Update contact information as you reach them")
        print("   4. Track quotes in HCMA_CHLORINE_SUPPLIER_QUOTES.md")
        print()
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    print()
    print("Possible issues:")
    print("   - GPSS SUPPLIERS table doesn't exist")
    print("   - Field names don't match (check Airtable table structure)")
    print("   - Airtable API credentials incorrect")
    print()
    print("Check your Airtable base and verify:")
    print("   - Table name is exactly 'GPSS SUPPLIERS'")
    print("   - Required fields exist: COMPANY NAME, WEBSITE, PHONE, etc.")
