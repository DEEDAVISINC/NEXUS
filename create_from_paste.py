#!/usr/bin/env python3
"""
Create documents from paste templates - fastest way!
Usage: python3 create_from_paste.py capability my_data.txt
       python3 create_from_paste.py rfq rfq_data.txt
"""

import json
import sys
import subprocess
import re


def parse_capability_template(text):
    """Parse capability statement paste template"""
    
    # Extract fields
    client_name = re.search(r'CLIENT_NAME:\s*(.+)', text)
    rfq_number = re.search(r'RFQ_NUMBER:\s*(.+)', text)
    date = re.search(r'DATE:\s*(.+)', text)
    color_scheme = re.search(r'COLOR_SCHEME:\s*(\d+)', text)
    
    # Extract overview (multiline)
    overview_match = re.search(r'OVERVIEW:\s*\n(.+?)(?=\n\n|\nHIGHLIGHTS:)', text, re.DOTALL)
    overview = overview_match.group(1).strip() if overview_match else ""
    
    # Extract highlights
    highlights = []
    highlights_section = re.search(r'HIGHLIGHTS:\s*\n(.+?)(?=\n\n|$)', text, re.DOTALL)
    
    if highlights_section:
        for line in highlights_section.group(1).split('\n'):
            line = line.strip()
            if not line:
                continue
            
            if line.startswith('NAICS:'):
                highlights.append({
                    "type": "naics",
                    "content": line.replace('NAICS:', '').strip()
                })
            elif line.startswith('Partners:'):
                highlights.append({
                    "type": "partners",
                    "content": line.replace('Partners:', '').strip()
                })
            elif 'Contract Range' in line or 'Performance' in line or 'Coverage' in line:
                parts = line.split(':', 1)
                if len(parts) == 2:
                    highlights.append({
                        "type": "custom",
                        "title": parts[0].strip(),
                        "content": parts[1].strip()
                    })
    
    # Color schemes
    color_schemes = {
        "1": {"primary": "#1e3a8a", "accent": "#d97706"},
        "2": {"primary": "#0c4a6e", "accent": "#0891b2"},
        "3": {"primary": "#713f12", "accent": "#f97316"},
        "4": {"primary": "#4c1d95", "accent": "#8b5cf6"},
        "5": {"primary": "#0369a1", "accent": "#0284c7"},
        "6": {"primary": "#14532d", "accent": "#16a34a"}
    }
    
    scheme_num = color_scheme.group(1) if color_scheme else "1"
    colors = color_schemes.get(scheme_num, color_schemes["1"])
    
    # Build config
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
            "client_name": client_name.group(1).strip() if client_name else "Client",
            "rfq_number": rfq_number.group(1).strip() if rfq_number else "RFQ-001",
            "date": date.group(1).strip() if date else "January 2026"
        },
        "colors": {
            "primary": colors["primary"],
            "accent": colors["accent"],
            "text": "#374151"
        },
        "company_overview": overview,
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
        "highlights": highlights,
        "logo_path": "dee_davis_logo.png"
    }
    
    return config


def parse_rfq_template(text):
    """Parse RFQ paste template"""
    
    # Extract fields
    request_type = re.search(r'REQUEST_TYPE:\s*(.+)', text)
    request_type_value = request_type.group(1).strip().upper() if request_type else "SUPPLIER"
    
    rfq_number = re.search(r'RFQ_NUMBER:\s*(.+)', text)
    title = re.search(r'TITLE:\s*(.+)', text)
    issue_date = re.search(r'ISSUE_DATE:\s*(.+)', text)
    due_date = re.search(r'DUE_DATE:\s*(.+)', text)
    due_time = re.search(r'DUE_TIME:\s*(.+)', text)
    contract_period = re.search(r'CONTRACT_PERIOD:\s*(.+)', text)
    color_scheme = re.search(r'COLOR_SCHEME:\s*(\d+)', text)
    
    # Extract introduction
    intro_match = re.search(r'INTRODUCTION:\s*\n(.+?)(?=\n\nSCOPE:)', text, re.DOTALL)
    introduction = intro_match.group(1).strip() if intro_match else ""
    
    # Extract scope
    scope_match = re.search(r'SCOPE:\s*\n(.+?)(?=\n\nKEY_REQUIREMENTS:)', text, re.DOTALL)
    scope = scope_match.group(1).strip() if scope_match else ""
    
    # Extract key requirements
    key_requirements = []
    req_match = re.search(r'KEY_REQUIREMENTS:\s*\n(.+?)(?=\n\nITEMS:)', text, re.DOTALL)
    if req_match:
        for line in req_match.group(1).split('\n'):
            line = line.strip()
            if line.startswith('-'):
                key_requirements.append(line[1:].strip())
    
    # Extract items or services based on request type
    items = []
    
    # Try SERVICES first (for subcontractor), then ITEMS (for supplier)
    items_match = re.search(r'(?:SERVICES|ITEMS):\s*\n(.+?)(?=\n\n|COMPLIANCE_REQUIREMENTS:|$)', text, re.DOTALL)
    if items_match:
        for line in items_match.group(1).split('\n'):
            line = line.strip()
            if not line or line.startswith('('):
                continue
            
            parts = [p.strip() for p in line.split('|')]
            if len(parts) >= 4:
                items.append({
                    "item_number": parts[0],
                    "description": parts[1],
                    "specifications": parts[2],
                    "estimated_quantity": parts[3],
                    "unit": parts[4] if len(parts) >= 5 else "unit"
                })
    
    # Extract compliance requirements (subcontractor only)
    compliance_requirements = []
    compliance_match = re.search(r'COMPLIANCE_REQUIREMENTS:\s*\n(.+?)(?=\n\n|⚠️|$)', text, re.DOTALL)
    if compliance_match:
        for line in compliance_match.group(1).split('\n'):
            line = line.strip()
            if line.startswith('-'):
                compliance_requirements.append(line[1:].strip())
    
    # Color schemes
    color_schemes = {
        "1": {"primary": "#0f172a", "accent": "#d97706"},
        "2": {"primary": "#7c2d12", "accent": "#f97316"},
        "3": {"primary": "#4c1d95", "accent": "#8b5cf6"},
        "4": {"primary": "#0c4a6e", "accent": "#0891b2"},
        "5": {"primary": "#713f12", "accent": "#f97316"}
    }
    
    scheme_num = color_scheme.group(1) if color_scheme else "1"
    colors = color_schemes.get(scheme_num, color_schemes["1"])
    
    # Build config
    config = {
        "request_type": request_type_value,
        "company": {
            "name": "DEE DAVIS INC",
            "address": "755 W Big Beaver Rd, Suite 2020, Troy, MI 48084",
            "phone": "248-376-4550",
            "email": "info@deedavis.biz",
            "website": "www.deedavis.biz",
            "contact_person": "Dee Davis, President & CEO"
        },
        "rfq_details": {
            "rfq_number": rfq_number.group(1).strip() if rfq_number else "RFQ-001",
            "title": title.group(1).strip() if title else "Request for Quote",
            "issue_date": issue_date.group(1).strip() if issue_date else "January 26, 2026",
            "due_date": due_date.group(1).strip() if due_date else "February 15, 2026",
            "due_time": due_time.group(1).strip() if due_time else "3:00 PM EST",
            "project_name": title.group(1).strip() if title else "Request for Quote",
            "contract_period": contract_period.group(1).strip() if contract_period else "12 months"
        },
        "colors": {
            "primary": colors["primary"],
            "accent": colors["accent"],
            "text": "#374151"
        },
        "introduction": introduction,
        "scope_of_work": {
            "title": "SCOPE OF WORK",
            "description": scope,
            "key_requirements": key_requirements if key_requirements else [
                "Meet quality standards",
                "Provide timely delivery",
                "Maintain competitive pricing"
            ]
        },
        "items": items if items else [{
            "item_number": "1",
            "description": "Product/Service",
            "specifications": "To be specified",
            "estimated_quantity": "TBD",
            "unit": "unit"
        }],
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
                {"title": "Contract Period", "description": f"{contract_period.group(1).strip() if contract_period else '12 months'} with option to extend"},
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
                f"Questions must be submitted in writing by {issue_date.group(1).strip() if issue_date else 'issue date'}",
                "DEE DAVIS INC reserves the right to accept or reject any or all quotes",
                "Late submissions will not be considered",
                f"Award notification expected within 10 business days of {due_date.group(1).strip() if due_date else 'due date'}"
            ]
        },
        "logo_path": "dee_davis_logo.png"
    }
    
    # Add compliance requirements if subcontractor request
    if request_type_value == "SUBCONTRACTOR" and compliance_requirements:
        config["compliance_requirements"] = {
            "title": "COMPLIANCE & INSURANCE REQUIREMENTS",
            "items": compliance_requirements
        }
    
    return config


def main():
    if len(sys.argv) < 3:
        print("Usage:")
        print("  python3 create_from_paste.py capability <template_file>")
        print("  python3 create_from_paste.py rfq <template_file>")
        sys.exit(1)
    
    doc_type = sys.argv[1].lower()
    template_file = sys.argv[2]
    
    # Read template
    try:
        with open(template_file, 'r') as f:
            text = f.read()
    except FileNotFoundError:
        print(f"❌ Error: File '{template_file}' not found")
        sys.exit(1)
    
    print(f"\n🎨 Parsing {doc_type} template from {template_file}...")
    
    # Parse based on type
    if doc_type == 'capability':
        config = parse_capability_template(text)
        output_base = f"cap_stmt_{config['rfq_details']['client_name'].lower().replace(' ', '_')}"
        html_generator = 'generate_html_with_highlights.py'
        pdf_generator = 'generate_enhanced_pdf.py'
    elif doc_type == 'rfq':
        config = parse_rfq_template(text)
        output_base = f"rfq_{config['rfq_details']['rfq_number'].lower().replace('-', '_')}"
        html_generator = 'generate_rfq_html.py'
        pdf_generator = 'generate_rfq_pdf.py'
    else:
        print(f"❌ Error: Unknown document type '{doc_type}'")
        print("   Use 'capability' or 'rfq'")
        sys.exit(1)
    
    # Save config
    config_file = f"{output_base}_config.json"
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=4)
    
    print(f"✓ Configuration saved: {config_file}")
    
    # Generate files
    print("\n🎨 Generating HTML and PDF...")
    
    try:
        subprocess.run(['python3', html_generator, config_file], check=True)
        subprocess.run(['python3', pdf_generator, config_file], check=True)
        
        print("\n" + "="*60)
        print("✅ SUCCESS! Your document is ready!")
        print("="*60)
        
        print(f"\n📄 Your files:")
        if doc_type == 'capability':
            print(f"   • {output_base}.html")
            print(f"   • {output_base}_enhanced.pdf")
        else:
            print(f"   • {output_base}.html")
            print(f"   • {output_base}.pdf")
        print(f"   • {config_file} (config)")
        
        print("\n🎯 Next steps:")
        print(f"   1. Open {output_base}.html in browser to preview")
        if doc_type == 'capability':
            print(f"   2. Submit {output_base}_enhanced.pdf to client")
        else:
            print(f"   2. Send {output_base}.pdf to vendors")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error generating files: {e}")
        print(f"But your config is saved: {config_file}")


if __name__ == "__main__":
    main()
