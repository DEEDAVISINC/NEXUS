#!/usr/bin/env python3
"""
Add RCOC 7732 Submission to Airtable
February 7, 2026
"""

import os
from datetime import datetime
from dotenv import load_dotenv
from pyairtable import Api

# Load environment variables
load_dotenv()

# Airtable configuration
AIRTABLE_API_KEY = os.getenv('AIRTABLE_API_KEY')
BASE_ID = os.getenv('AIRTABLE_BASE_ID')

print(f"DEBUG: API Key loaded: {'Yes' if AIRTABLE_API_KEY else 'No'}")
print(f"DEBUG: Base ID: {BASE_ID}")

# Initialize Airtable
api = Api(AIRTABLE_API_KEY)

def add_rcoc_7732():
    """Add RCOC 7732 submission to Contracts table"""
    
    table = api.table(BASE_ID, 'Contracts')
    
    opportunity_data = {
        'Opportunity_ID': 'RCOC-7732-2026',
        'Title': 'RCOC 7732 - Disposable Paper Products',
        'Client': 'Road Commission for Oakland County (RCOC)',
        'Contact_Name': 'Shari Graves',
        'Contact_Email': 'sgraves@rcoc.org',
        'Contact_Phone': '248-858-4780',
        'Source': 'BidNet Michigan (MITN)',
        'Solicitation_Number': '7732',
        'Type': 'IFB',
        'Status': 'Submitted',
        'Submission_Date': '2026-02-07',
        'Due_Date': '2026-02-10',
        'Bid_Opening_Date': '2026-02-10',
        'Contract_Start': '2026-03-01',
        'Contract_End': '2027-01-31',
        'Bid_Amount': 80436.52,
        'Estimated_Cost': 70850.00,
        'Estimated_Profit': 9586.52,
        'Profit_Margin': 13.5,
        'Confidence_Level': 'Medium-High (50-60%)',
        'Location': 'Beverly Hills, MI',
        'Delivery_Address': '31001 Lahser Rd, Beverly Hills, MI 48025',
        'Description': 'Annual supply of disposable paper products: napkins (2.25M), hot cups, toilet paper, cloth rags, facial tissue. 11-month blanket order.',
        'Key_Requirements': '5 line items: Empress napkins (9,000 packs), Dixie hot cups (500 tubes), Kimberly-Clark toilet paper (7,040 each), Absorbents cloth rags (90 boxes), Kimberly-Clark facial tissue (288 boxes). All tax-exempt, freight included.',
        'Submission_Method': 'BidNet online portal',
        'Confirmation_Number': '0000378881',
        'Submitted_By': 'Dee Davis',
        'Notes': 'Submitted Feb 7 @ 7:26 PM EST. Confirmation #0000378881. Napkin quantity clarified by Shari Graves (Jan 29). Mixed sourcing: Grainger (napkins $52,500) + Zoro (other items $18,305). Can modify until deadline. 6th bid with Shari Graves.',
        'Suppliers': 'Grainger, Zoro',
        'Certifications_Used': 'EDWOSB, WOSB',
        'Tags': 'RCOC, Paper Products, Submitted, Shari Graves, BidNet',
    }
    
    try:
        record = table.create(opportunity_data)
        print(f"✅ Added RCOC 7732 to Airtable")
        print(f"   Record ID: {record['id']}")
        print(f"   Bid Amount: ${opportunity_data['Bid_Amount']:,.2f}")
        print(f"   Profit: ${opportunity_data['Estimated_Profit']:,.2f}")
        print(f"   Confirmation: {opportunity_data['Confirmation_Number']}")
        return record
    except Exception as e:
        print(f"❌ Error adding to Airtable: {e}")
        return None

def add_products():
    """Add line items to Products/Quotes table"""
    
    # Try Products table, if it doesn't exist, skip
    try:
        table = api.table(BASE_ID, 'Products')
    except:
        print("   ⚠️ Products table not found, skipping line items")
        return
    
    products = [
        {
            'Product_Name': 'Empress Dinner Napkins',
            'Manufacturer': 'Empress',
            'Part_Number': 'DN 281517B',
            'Description': 'Dinner Napkin, White, 2-Ply, Pack of 250',
            'Category': 'Paper Products',
            'UOM': 'Pack',
            'Quantity': 9000,
            'Unit_Price': 6.71,
            'Extended_Total': 60390.00,
            'Supplier': 'Grainger',
            'Supplier_Item': '846N89',
            'Cost_Per_Unit': 5.83,
            'Opportunity_ID': 'RCOC-7732-2026',
            'Status': 'Quoted',
        },
        {
            'Product_Name': 'Dixie Hot Cups',
            'Manufacturer': 'Dixie',
            'Part_Number': '5338CD',
            'Description': 'Disposable Hot Cup, 8 oz, White, Pack of 1,000',
            'Category': 'Paper Products',
            'UOM': 'Tube',
            'Quantity': 500,
            'Unit_Price': 7.13,
            'Extended_Total': 3565.00,
            'Supplier': 'Zoro',
            'Cost_Per_Unit': 6.20,
            'Opportunity_ID': 'RCOC-7732-2026',
            'Status': 'Quoted',
        },
        {
            'Product_Name': 'Kimberly-Clark Toilet Paper',
            'Manufacturer': 'Kimberly-Clark Professional',
            'Part_Number': '04460',
            'Description': 'Toilet Paper Roll, 2-Ply, 550 Sheets, White',
            'Category': 'Paper Products',
            'UOM': 'Each',
            'Quantity': 7040,
            'Unit_Price': 1.53,
            'Extended_Total': 10771.20,
            'Supplier': 'Zoro',
            'Supplier_Item': 'G4519551',
            'Cost_Per_Unit': 1.33,
            'Opportunity_ID': 'RCOC-7732-2026',
            'Status': 'Quoted',
        },
        {
            'Product_Name': 'Absorbents Midwest Cloth Rags',
            'Manufacturer': 'Absorbents Midwest',
            'Part_Number': '30-450-B',
            'Description': 'Cloth Rag, Reclaimed White Cotton, 25lb Box',
            'Category': 'Janitorial Supplies',
            'UOM': 'Box',
            'Quantity': 90,
            'Unit_Price': 55.64,
            'Extended_Total': 5007.60,
            'Supplier': 'Zoro',
            'Supplier_Item': 'G614665951',
            'Cost_Per_Unit': 48.39,
            'Opportunity_ID': 'RCOC-7732-2026',
            'Status': 'Quoted',
        },
        {
            'Product_Name': 'Kimberly-Clark Facial Tissue',
            'Manufacturer': 'Kimberly-Clark Professional',
            'Part_Number': '21270',
            'Description': 'Facial Tissue, 2-Ply, 90 Sheets/Box, Pack of 36',
            'Category': 'Paper Products',
            'UOM': 'Box',
            'Quantity': 288,
            'Unit_Price': 2.44,
            'Extended_Total': 702.72,
            'Supplier': 'Zoro',
            'Supplier_Item': 'G306113302',
            'Cost_Per_Unit': 2.12,
            'Opportunity_ID': 'RCOC-7732-2026',
            'Status': 'Quoted',
        },
    ]
    
    print("\n📦 Adding products to Airtable...")
    for product in products:
        try:
            record = table.create(product)
            print(f"   ✅ {product['Product_Name']} - ${product['Extended_Total']:,.2f}")
        except Exception as e:
            print(f"   ❌ Error adding {product['Product_Name']}: {e}")

if __name__ == '__main__':
    print("🚀 Adding RCOC 7732 submission to Airtable...\n")
    
    # Add opportunity
    opportunity = add_rcoc_7732()
    
    # Add products
    if opportunity:
        add_products()
    
    print("\n✅ RCOC 7732 added to NEXUS Airtable!")
    print("   Confirmation: 0000378881")
    print("   Total Bid: $80,436.52")
    print("   Profit: $9,586.52")
