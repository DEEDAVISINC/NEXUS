#!/usr/bin/env python3
"""
Interactive RFQ Creator
Just answer questions and paste info - we'll handle the rest!
"""

import json
import subprocess


def get_input(prompt, default=""):
    """Get input with optional default"""
    if default:
        user_input = input(f"{prompt} [{default}]: ").strip()
        return user_input if user_input else default
    else:
        return input(f"{prompt}: ").strip()


def get_multiline_input(prompt):
    """Get multi-line input (ends with empty line)"""
    print(f"\n{prompt}")
    print("(Press Enter twice when done)")
    lines = []
    while True:
        line = input()
        if not line:
            break
        lines.append(line)
    return " ".join(lines)


def choose_colors():
    """Choose color scheme"""
    print("\n" + "="*60)
    print("CHOOSE COLOR SCHEME")
    print("="*60)
    
    color_schemes = {
        "1": {"name": "Industrial Navy & Gold", "primary": "#0f172a", "accent": "#d97706"},
        "2": {"name": "Transportation Brown & Orange", "primary": "#7c2d12", "accent": "#f97316"},
        "3": {"name": "Technology Purple & Violet", "primary": "#4c1d95", "accent": "#8b5cf6"},
        "4": {"name": "Healthcare Blue & Teal", "primary": "#0c4a6e", "accent": "#0891b2"},
        "5": {"name": "Construction Dark Brown", "primary": "#713f12", "accent": "#f97316"},
    }
    
    for key, scheme in color_schemes.items():
        print(f"{key}. {scheme['name']}")
    
    choice = get_input("\nEnter number (1-5)", "1")
    
    if choice in color_schemes:
        return color_schemes[choice]
    else:
        return color_schemes["1"]


def add_items():
    """Add items/services to RFQ"""
    print("\n" + "="*60)
    print("ADD ITEMS/SERVICES")
    print("="*60)
    print("Add the products or services you need quotes for.")
    print()
    
    items = []
    item_num = 1
    
    while True:
        print(f"\n--- Item #{item_num} ---")
        
        description = get_input("Description (or 'done' to finish)")
        if description.lower() == 'done':
            break
        
        specifications = get_input("Specifications/Details")
        quantity = get_input("Estimated Quantity (e.g., '100 units')", "TBD")
        unit = get_input("Unit (e.g., 'unit', 'box', 'gallon')", "unit")
        
        items.append({
            "item_number": str(item_num),
            "description": description,
            "specifications": specifications,
            "estimated_quantity": quantity,
            "unit": unit
        })
        
        item_num += 1
        
        if len(items) >= 3:
            more = get_input("Add another item? (y/n)", "n").lower()
            if more != 'y':
                break
    
    return items


def create_rfq():
    """Interactive RFQ creator"""
    
    print("\n" + "="*60)
    print("RFQ CREATOR")
    print("="*60)
    print("Let's create your Request for Quote!")
    print("Just answer the questions below.")
    print("="*60)
    
    # RFQ Details
    print("\n--- RFQ DETAILS ---")
    rfq_number = get_input("RFQ Number (e.g., 'RFQ-2026-001')")
    title = get_input("RFQ Title (e.g., 'Industrial Cleaning Supplies')")
    issue_date = get_input("Issue Date", "January 26, 2026")
    due_date = get_input("Due Date", "February 15, 2026")
    due_time = get_input("Due Time", "3:00 PM EST")
    contract_period = get_input("Contract Period", "12 months")
    
    # Choose colors
    color_scheme = choose_colors()
    
    # Introduction
    print("\n--- INTRODUCTION ---")
    introduction = get_multiline_input("Paste or type your RFQ introduction:")
    
    # Scope of Work
    print("\n--- SCOPE OF WORK ---")
    scope_description = get_multiline_input("Describe the scope of work:")
    
    print("\nKey requirements (one per line, type 'done' when finished):")
    key_requirements = []
    while True:
        req = input("  Requirement: ").strip()
        if req.lower() == 'done' or not req:
            break
        key_requirements.append(req)
    
    # Items
    items = add_items()
    
    if not items:
        print("\n⚠️  No items added. Adding a default item.")
        items = [{
            "item_number": "1",
            "description": "Product/Service",
            "specifications": "To be specified",
            "estimated_quantity": "TBD",
            "unit": "unit"
        }]
    
    # Build config
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
            "rfq_number": rfq_number,
            "title": title,
            "issue_date": issue_date,
            "due_date": due_date,
            "due_time": due_time,
            "project_name": title,
            "contract_period": contract_period
        },
        "colors": {
            "primary": color_scheme["primary"],
            "accent": color_scheme["accent"],
            "text": "#374151"
        },
        "introduction": introduction,
        "scope_of_work": {
            "title": "SCOPE OF WORK",
            "description": scope_description,
            "key_requirements": key_requirements if key_requirements else [
                "Meet quality standards",
                "Provide timely delivery",
                "Maintain competitive pricing"
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
                {"title": "Contract Period", "description": f"{contract_period} with option to extend"},
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
                f"Questions must be submitted in writing by {issue_date}",
                "DEE DAVIS INC reserves the right to accept or reject any or all quotes",
                "Late submissions will not be considered",
                f"Award notification expected within 10 business days of {due_date}"
            ]
        },
        "logo_path": "dee_davis_logo.png"
    }
    
    # Save config
    filename = f"rfq_{rfq_number.replace('-', '_').lower()}_config.json"
    with open(filename, 'w') as f:
        json.dump(config, f, indent=4)
    
    print("\n" + "="*60)
    print(f"✓ Configuration saved: {filename}")
    print("="*60)
    
    # Generate files
    print("\n🎨 Generating HTML and PDF...")
    
    try:
        subprocess.run(['python3', 'generate_rfq_html.py', filename], check=True)
        subprocess.run(['python3', 'generate_rfq_pdf.py', filename], check=True)
        
        print("\n" + "="*60)
        print("✅ SUCCESS! Your RFQ is ready!")
        print("="*60)
        
        base = filename.replace('_config.json', '')
        print(f"\n📄 Your files:")
        print(f"   • {base}.html")
        print(f"   • {base}.pdf")
        print(f"   • {filename} (config - save this for future edits)")
        print("\n🎯 Next steps:")
        print(f"   1. Open {base}.html in browser to preview")
        print(f"   2. Send {base}.pdf to vendors")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error generating files: {e}")
        print(f"But your config is saved: {filename}")


if __name__ == "__main__":
    create_rfq()
