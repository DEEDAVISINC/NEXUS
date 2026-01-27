#!/usr/bin/env python3
"""
Import items from CSV for RFQ generation
Usage: python3 import_from_csv.py items.csv
"""

import csv
import json
import sys


def read_csv_items(filename):
    """Read items from CSV file"""
    items = []
    
    try:
        with open(filename, 'r') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                # Support multiple column name variations
                item_num = (row.get('Item #') or row.get('Item') or 
                           row.get('item_number') or str(len(items) + 1))
                
                description = (row.get('Description') or row.get('description') or 
                             row.get('Item Description') or '')
                
                specs = (row.get('Specifications') or row.get('specifications') or 
                        row.get('Specs') or row.get('Details') or '')
                
                quantity = (row.get('Est. Quantity') or row.get('Quantity') or 
                           row.get('estimated_quantity') or row.get('Qty') or 'TBD')
                
                unit = (row.get('Unit') or row.get('unit') or 
                       row.get('UOM') or 'unit')
                
                if description:  # Only add if we have at least a description
                    items.append({
                        "item_number": str(item_num),
                        "description": description,
                        "specifications": specs,
                        "estimated_quantity": str(quantity),
                        "unit": str(unit)
                    })
        
        return items
        
    except FileNotFoundError:
        print(f"❌ Error: File '{filename}' not found")
        return None
    except Exception as e:
        print(f"❌ Error reading CSV: {e}")
        return None


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 import_from_csv.py <items.csv>")
        print("\nExpected CSV format:")
        print("Item #,Description,Specifications,Est. Quantity,Unit")
        print("1,Paper Towels,11x9 roll case of 30,500 cases,case")
        print("2,Cleaner,1-gallon concentrated,200 gallons,gallon")
        sys.exit(1)
    
    csv_file = sys.argv[1]
    
    print(f"\n📊 Importing items from {csv_file}...")
    
    items = read_csv_items(csv_file)
    
    if items is None:
        sys.exit(1)
    
    if not items:
        print("❌ No items found in CSV file")
        sys.exit(1)
    
    print(f"✓ Imported {len(items)} items")
    
    # Create a basic RFQ config with imported items
    config = {
        "company": {
            "name": "DEE DAVIS INC",
            "address": "755 W Big Beaver Rd, Suite 2020, Troy, MI 48084",
            "phone": "248-376-4550",
            "email": "info@deedavis.biz",
            "website": "www.deedavis.biz",
            "contact_person": "Dee Davis, President & CEO"
        },
        "rfq_details": {
            "rfq_number": "RFQ-2026-001",
            "title": "Request for Quote",
            "issue_date": "January 26, 2026",
            "due_date": "February 15, 2026",
            "due_time": "3:00 PM EST",
            "project_name": "Request for Quote",
            "contract_period": "12 months"
        },
        "colors": {
            "primary": "#0f172a",
            "accent": "#d97706",
            "text": "#374151"
        },
        "introduction": "DEE DAVIS INC is seeking qualified suppliers to provide the items listed below.",
        "scope_of_work": {
            "title": "SCOPE OF WORK",
            "description": "The selected vendor will provide all items as specified with delivery to our designated location.",
            "key_requirements": [
                "Meet all quality specifications",
                "Provide timely delivery as scheduled",
                "Maintain competitive pricing",
                "Ensure product availability"
            ]
        },
        "items": items,
        "submission_requirements": {
            "title": "SUBMISSION REQUIREMENTS",
            "items": [
                "Complete pricing for all items listed",
                "Product specifications and technical data sheets",
                "Company profile and relevant certifications",
                "References from at least 3 similar clients",
                "Delivery schedule and lead times",
                "Payment terms and available discounts"
            ]
        },
        "terms_and_conditions": {
            "title": "TERMS & CONDITIONS",
            "items": [
                {"title": "Payment Terms", "description": "Net 30 days from invoice date"},
                {"title": "Delivery", "description": "FOB Destination, freight prepaid and included"},
                {"title": "Contract Period", "description": "12 months with option to extend"},
                {"title": "Quality Standards", "description": "All products must meet industry standards"},
                {"title": "Insurance", "description": "Vendor must maintain minimum $1M general liability"}
            ]
        },
        "evaluation_criteria": {
            "title": "EVALUATION CRITERIA",
            "description": "Quotes will be evaluated based on the following weighted criteria:",
            "criteria": [
                {"criterion": "Total Cost", "weight": "40%"},
                {"criterion": "Product Quality & Specifications", "weight": "25%"},
                {"criterion": "Delivery Capability & Lead Times", "weight": "20%"},
                {"criterion": "Company Experience & References", "weight": "10%"},
                {"criterion": "Payment Terms & Discounts", "weight": "5%"}
            ]
        },
        "additional_info": {
            "title": "ADDITIONAL INFORMATION",
            "items": [
                "Questions must be submitted in writing by issue date",
                "DEE DAVIS INC reserves the right to accept or reject any or all quotes",
                "Late submissions will not be considered",
                "Award notification expected within 10 business days of due date"
            ]
        },
        "logo_path": "dee_davis_logo.png"
    }
    
    # Save config
    config_file = "rfq_from_csv_config.json"
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=4)
    
    print(f"✓ Configuration saved: {config_file}")
    
    print("\n" + "="*60)
    print("✅ CSV IMPORT COMPLETE!")
    print("="*60)
    
    print(f"\n📋 Imported Items:")
    for item in items:
        print(f"   {item['item_number']}. {item['description']}")
    
    print(f"\n🎯 Next steps:")
    print(f"   1. Edit {config_file} to customize:")
    print(f"      - RFQ number and title")
    print(f"      - Dates and deadlines")
    print(f"      - Introduction and scope")
    print(f"   2. Generate documents:")
    print(f"      python3 generate_rfq_html.py {config_file}")
    print(f"      python3 generate_rfq_pdf.py {config_file}")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
