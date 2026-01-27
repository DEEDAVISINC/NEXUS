#!/usr/bin/env python3
"""
Quick template creator - for power users who want to edit JSON directly
Creates base templates that you can copy and customize
"""

import json
import sys


def create_capability_template():
    """Create capability statement template"""
    
    config = {
        "company": {
            "name": "DEE DAVIS INC",
            "address": "755 W Big Beaver Rd, Suite 2020, Troy, MI 48084",
            "phone": "248-376-4550",
            "email": "info@deedavis.biz",
            "website": "www.deedavis.biz",
            "cage_code": "8UMX3",
            "uei": "HJB4KNYJVGZ1",
            "duns": "002636755",
            "tax_id": "84-4114181"
        },
        "rfq_details": {
            "client_name": "CLIENT_NAME_HERE",
            "rfq_number": "RFQ_NUMBER_HERE",
            "date": "January 2026"
        },
        "colors": {
            "primary": "#1e3a8a",
            "accent": "#d97706",
            "text": "#374151"
        },
        "company_overview": "PASTE_YOUR_COMPANY_OVERVIEW_HERE - Describe your company, what you do, who you serve, and your value proposition.",
        "core_competencies": [
            "Supply Chain Management",
            "Logistics & Distribution",
            "Vendor Management",
            "Quality Assurance"
        ],
        "differentiators": [
            "EDWOSB Certified - Enhanced contracting opportunities",
            "Michigan-based with nationwide reach",
            "24/7 customer support and rapid response times",
            "Proven track record with government agencies"
        ],
        "certifications": [
            {"name": "EDWOSB", "description": "Economically Disadvantaged Woman-Owned Small Business"},
            {"name": "WOSB", "description": "Woman-Owned Small Business"},
            {"name": "SBE", "description": "Small Business Enterprise"}
        ],
        "highlights": [
            {"type": "naics", "content": "423850 - Industrial Supplies"},
            {"type": "partners", "content": "Partner 1 | Partner 2 | Partner 3"},
            {"type": "custom", "title": "Contract Range", "content": "$50K - $500K Successfully Delivered"}
        ],
        "logo_path": "dee_davis_logo.png"
    }
    
    return config


def create_rfq_template():
    """Create RFQ template"""
    
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
            "rfq_number": "RFQ_NUMBER_HERE",
            "title": "RFQ_TITLE_HERE",
            "issue_date": "January 26, 2026",
            "due_date": "February 15, 2026",
            "due_time": "3:00 PM EST",
            "project_name": "PROJECT_NAME_HERE",
            "contract_period": "12 months"
        },
        "colors": {
            "primary": "#0f172a",
            "accent": "#d97706",
            "text": "#374151"
        },
        "introduction": "PASTE_YOUR_INTRODUCTION_HERE - Explain the purpose of this RFQ and what you're seeking.",
        "scope_of_work": {
            "title": "SCOPE OF WORK",
            "description": "PASTE_SCOPE_DESCRIPTION_HERE - Detail what the vendor will need to provide.",
            "key_requirements": [
                "Requirement 1 - Edit or add more",
                "Requirement 2",
                "Requirement 3"
            ]
        },
        "items": [
            {
                "item_number": "1",
                "description": "ITEM_DESCRIPTION_HERE",
                "specifications": "SPECIFICATIONS_HERE",
                "estimated_quantity": "QUANTITY_HERE",
                "unit": "unit"
            },
            {
                "item_number": "2",
                "description": "ITEM_DESCRIPTION_HERE",
                "specifications": "SPECIFICATIONS_HERE",
                "estimated_quantity": "QUANTITY_HERE",
                "unit": "unit"
            }
        ],
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
    
    return config


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 create_template.py capability")
        print("  python3 create_template.py rfq")
        print("\nCreates a base template JSON file that you can copy and edit.")
        sys.exit(1)
    
    doc_type = sys.argv[1].lower()
    
    if doc_type == 'capability':
        config = create_capability_template()
        output_file = "template_capability_statement.json"
        doc_name = "Capability Statement"
    elif doc_type == 'rfq':
        config = create_rfq_template()
        output_file = "template_rfq.json"
        doc_name = "RFQ"
    else:
        print(f"❌ Error: Unknown type '{doc_type}'")
        print("   Use 'capability' or 'rfq'")
        sys.exit(1)
    
    # Save template
    with open(output_file, 'w') as f:
        json.dump(config, f, indent=4)
    
    print("\n" + "="*60)
    print(f"✅ {doc_name} Template Created!")
    print("="*60)
    
    print(f"\n📄 Template saved: {output_file}")
    
    print(f"\n🎯 How to use:")
    print(f"   1. Copy the template:")
    print(f"      cp {output_file} my_new_doc.json")
    
    print(f"\n   2. Edit your copy:")
    print(f"      nano my_new_doc.json")
    print(f"      (Search for UPPERCASE text and replace with your info)")
    
    print(f"\n   3. Generate documents:")
    if doc_type == 'capability':
        print(f"      python3 generate_html_with_highlights.py my_new_doc.json")
        print(f"      python3 generate_enhanced_pdf.py my_new_doc.json")
    else:
        print(f"      python3 generate_rfq_html.py my_new_doc.json")
        print(f"      python3 generate_rfq_pdf.py my_new_doc.json")
    
    print("\n💡 Power User Tips:")
    print("   • Keep this template - use it for all future docs")
    print("   • Edit only what changes (client, RFQ number, dates)")
    print("   • Use find/replace for bulk edits")
    print("   • Create industry-specific templates")
    
    print("\n📋 What to edit in the template:")
    if doc_type == 'capability':
        print("   • client_name: Your client's name")
        print("   • rfq_number: The RFQ you're responding to")
        print("   • company_overview: Your pitch (PASTE_YOUR_COMPANY_OVERVIEW_HERE)")
        print("   • highlights: Add your specific NAICS, partners, achievements")
        print("   • colors: primary & accent (hex codes)")
    else:
        print("   • rfq_number: Your RFQ identifier")
        print("   • title: What you're buying")
        print("   • introduction: Why you're issuing this RFQ")
        print("   • items: Add/remove items, edit specs & quantities")
        print("   • dates: Issue date and due date")
        print("   • colors: primary & accent (hex codes)")
    
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
