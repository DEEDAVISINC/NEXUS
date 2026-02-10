#!/usr/bin/env python3
"""
Auto-Generate Opportunity-Specific Capability Statements
Pulls opportunity data and creates customized capability statements
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional
from pyairtable import Api
from dotenv import load_dotenv
import subprocess

load_dotenv()

# Initialize Airtable
api = Api(os.getenv('AIRTABLE_API_KEY'))
base_id = os.getenv('AIRTABLE_BASE_ID')


def get_category_naics_and_competencies(opportunity_title: str, description: str = "") -> tuple:
    """
    Determine NAICS codes and competencies based on opportunity category
    
    Returns: (naics_codes, competencies, highlights)
    """
    title_lower = opportunity_title.lower()
    desc_lower = description.lower() if description else ""
    combined = f"{title_lower} {desc_lower}"
    
    # Product Categories
    if any(word in combined for word in ['cable', 'wire', 'assembly', 'electronic']):
        return (
            ["5995 - Cable and Wire Products", "6150 - Electrical Components"],
            [
                {
                    "title": "Cable & Wire Assembly Sourcing",
                    "description": "Strategic partnerships with major cable manufacturers for MIL-SPEC and commercial-grade assemblies"
                },
                {
                    "title": "Electronic Component Procurement",
                    "description": "Nationwide sourcing network for electrical components meeting federal specifications"
                }
            ],
            [
                {"icon": "🎯", "label": "Primary NAICS", "value": "5995 - Cable/Wire Products"},
                {"icon": "🤝", "label": "Key Partners", "value": "Major Cable Manufacturers"}
            ]
        )
    
    elif any(word in combined for word in ['shipping', 'storage', 'logistics', 'warehouse']):
        return (
            ["423850 - Warehouse Equipment", "492110 - Storage Services"],
            [
                {
                    "title": "Logistics & Supply Chain Management",
                    "description": "Comprehensive shipping, storage, and distribution solutions with nationwide coverage"
                },
                {
                    "title": "Warehouse Equipment Procurement",
                    "description": "Complete line of storage and warehouse equipment meeting federal specifications"
                }
            ],
            [
                {"icon": "🎯", "label": "Primary NAICS", "value": "423850 - Warehouse Equipment"},
                {"icon": "📦", "label": "Coverage", "value": "Nationwide Logistics Network"}
            ]
        )
    
    elif any(word in combined for word in ['industrial', 'supplies', 'tools', 'equipment']):
        return (
            ["423840 - Industrial Supplies", "423850 - Service Equipment"],
            [
                {
                    "title": "Industrial Supply Procurement",
                    "description": "Comprehensive sourcing of industrial supplies, tools, and equipment from major distributors"
                },
                {
                    "title": "Multi-Category Fulfillment",
                    "description": "One-stop solution for diverse industrial supply requirements"
                }
            ],
            [
                {"icon": "🎯", "label": "Primary NAICS", "value": "423840 - Industrial Supplies"},
                {"icon": "🤝", "label": "Key Partners", "value": "Grainger | Fastenal | MSC"}
            ]
        )
    
    elif any(word in combined for word in ['medical', 'healthcare', 'hospital', 'supplies']):
        return (
            ["423450 - Medical Equipment", "339112 - Surgical Supplies"],
            [
                {
                    "title": "Medical Equipment & Supplies",
                    "description": "Comprehensive procurement of medical equipment, surgical supplies, and healthcare products"
                },
                {
                    "title": "Healthcare Compliance",
                    "description": "Full compliance with FDA, CDC, and federal healthcare procurement standards"
                }
            ],
            [
                {"icon": "🎯", "label": "Primary NAICS", "value": "423450 - Medical Equipment"},
                {"icon": "🏥", "label": "Compliance", "value": "FDA | CDC Standards"}
            ]
        )
    
    elif any(word in combined for word in ['automotive', 'vehicle', 'truck', 'fleet']):
        return (
            ["441110 - Automobile Dealers", "423120 - Motor Vehicle Supplies"],
            [
                {
                    "title": "Vehicle Procurement & Fleet Services",
                    "description": "Partnership with wholesale dealers for vehicle procurement meeting federal specifications"
                },
                {
                    "title": "Automotive Supplies & Parts",
                    "description": "Comprehensive automotive supply sourcing for fleet maintenance and operations"
                }
            ],
            [
                {"icon": "🎯", "label": "Primary NAICS", "value": "441110 - Vehicle Procurement"},
                {"icon": "🚗", "label": "Capability", "value": "Fleet Vehicles & Supplies"}
            ]
        )
    
    elif any(word in combined for word in ['cleaning', 'janitorial', 'sanitation', 'custodial']):
        return (
            ["561720 - Janitorial Services", "423850 - Cleaning Supplies"],
            [
                {
                    "title": "Cleaning Services & Supplies",
                    "description": "Prime contracting for cleaning services with qualified subcontractor network"
                },
                {
                    "title": "Facility Maintenance",
                    "description": "Comprehensive facility maintenance solutions with EDWOSB certification"
                }
            ],
            [
                {"icon": "🎯", "label": "Primary NAICS", "value": "561720 - Janitorial Services"},
                {"icon": "🧹", "label": "Capability", "value": "Prime/Sub Cleaning Services"}
            ]
        )
    
    # Default/General
    else:
        return (
            ["423840 - Industrial Supplies", "423850 - Service Equipment", "541990 - Professional Services"],
            [
                {
                    "title": "Multi-Category Procurement",
                    "description": "Diverse sourcing capabilities across multiple product and service categories"
                },
                {
                    "title": "Government Contract Fulfillment",
                    "description": "Experienced in federal, state, and local government contract execution"
                }
            ],
            [
                {"icon": "🎯", "label": "Primary NAICS", "value": "423840 - Industrial Supplies"},
                {"icon": "🤝", "label": "Experience", "value": "Federal/State/Local Contracts"}
            ]
        )


def generate_opportunity_specific_capstat(
    opportunity_title: str,
    solicitation_number: str = "",
    agency: str = "",
    set_aside: str = "",
    description: str = "",
    opportunity_id: Optional[str] = None
) -> Dict:
    """
    Generate a capability statement customized for a specific opportunity
    
    Args:
        opportunity_title: Title of the opportunity
        solicitation_number: RFP/RFQ number
        agency: Government agency name
        set_aside: Set-aside type (WOSB, EDWOSB, etc.)
        description: Description of the opportunity
        opportunity_id: Optional Airtable record ID
    
    Returns:
        Dict with file paths and metadata
    """
    
    # Get category-specific content
    naics_codes, competencies, highlights = get_category_naics_and_competencies(
        opportunity_title, description
    )
    
    # Determine colors based on set-aside or agency
    if 'WOSB' in set_aside or 'EDWOSB' in set_aside:
        colors = {
            "primary": "#0f172a",
            "secondary": "#1e293b",
            "accent": "#d97706",  # Amber for WOSB
            "text": "#334155",
            "light": "#f1f5f9"
        }
    elif 'VA' in agency or 'Veterans' in agency:
        colors = {
            "primary": "#1e3a8a",
            "secondary": "#1e40af",
            "accent": "#0066cc",  # Blue for VA
            "text": "#334155",
            "light": "#f1f5f9"
        }
    else:
        colors = {
            "primary": "#0f172a",
            "secondary": "#1e293b",
            "accent": "#f97316",  # Orange default
            "text": "#334155",
            "light": "#f1f5f9"
        }
    
    # Build comprehensive config
    rfq_details_data = {
        "client_name": agency if agency else "Federal Agency",
        "rfq_number": solicitation_number if solicitation_number else "Sources Sought",
        "date": datetime.now().strftime("%B %Y"),
        "title": opportunity_title
    }
    
    config = {
        "company": {
            "name": "DEE DAVIS INC",
            "cage_code": "8UMX3",
            "uei": "HJB4KNYJVGZ1",
            "duns": "002636755",
            "tax_id": "84-4114181",
            "sam_status": "Active",
            "founded": "2018",
            "address": "755 W Big Beaver Rd, Suite 2020",
            "city": "Troy",
            "state": "MI",
            "zip": "48084-4925",
            "phone": "248-376-4550",
            "email": "info@deedavis.biz",
            "website": "www.deedavis.biz",
            "president": "Dee Davis"
        },
        "opportunity": rfq_details_data,
        "rfq_details": rfq_details_data,  # Alias for compatibility with older scripts
        "colors": colors,
        "highlights": {
            "title": "QUICK FACTS",
            "items": highlights
        },
        "overview": f"Dee Davis Inc. is a certified EDWOSB (Economically Disadvantaged Woman-Owned Small Business) specializing in government contract fulfillment. We bring proven expertise in {opportunity_title.lower()} with a strong track record of delivering quality products and services to federal, state, and local agencies.",
        "core_competencies": competencies,
        "benefits": [
            {
                "icon": "✓",
                "title": "EDWOSB Certified",
                "description": "Economically Disadvantaged Woman-Owned Small Business - helps agencies meet socioeconomic goals"
            },
            {
                "icon": "✓",
                "title": "SAM.gov Registered",
                "description": "Active registration with CAGE Code 8UMX3, ready for federal contract awards"
            },
            {
                "icon": "✓",
                "title": "Proven Track Record",
                "description": "Successful government contracts with multiple agencies including RCOC, Michigan municipalities"
            },
            {
                "icon": "✓",
                "title": "Nationwide Capability",
                "description": "Michigan-based with nationwide sourcing and delivery network"
            }
        ],
        "certifications": [
            "EDWOSB - SBA Certified (Economically Disadvantaged Woman-Owned Small Business)",
            "WOSB - Women-Owned Small Business",
            "SAM.gov Registered - CAGE Code: 8UMX3",
            "UEI: HJB4KNYJVGZ1",
            "DUNS: 002636755"
        ],
        "naics_codes": naics_codes,
        "contract_capabilities": {
            "payment_terms": "Net 30 or per contract requirements",
            "delivery_time": "10-30 days ARO (varies by product)",
            "coverage": "Nationwide delivery capability",
            "insurance": "$1M+ General Liability, Workers Comp as required"
        },
        "commitment": f"Dee Davis Inc. is committed to supporting {agency if agency else 'your agency'}'s mission by providing quality {opportunity_title.lower()}, competitive pricing, and excellent service. As a certified EDWOSB, we help agencies meet supplier diversity goals while delivering exceptional performance."
    }
    
    # Generate timestamp for unique filenames
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_title = "".join(c for c in opportunity_title if c.isalnum() or c in (' ', '-', '_')).replace(' ', '_')[:50]
    config_filename = f"capstat_config_{safe_title}_{timestamp}.json"
    
    # Save config
    config_path = Path(config_filename)
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ Config saved: {config_filename}")
    
    # Generate HTML
    html_output = f"capstat_{safe_title}_{timestamp}.html"
    try:
        subprocess.run([
            'python3', 'generate_html_with_highlights.py',
            config_filename
        ], check=True)
        print(f"✅ HTML generated: {html_output}")
    except Exception as e:
        print(f"❌ HTML generation failed: {e}")
        html_output = None
    
    # Generate PDF
    pdf_output = f"capstat_{safe_title}_{timestamp}_enhanced.pdf"
    try:
        subprocess.run([
            'python3', 'generate_enhanced_pdf.py',
            config_filename
        ], check=True)
        print(f"✅ PDF generated: {pdf_output}")
    except Exception as e:
        print(f"❌ PDF generation failed: {e}")
        pdf_output = None
    
    return {
        "config_file": str(config_path),
        "html_file": html_output,
        "pdf_file": pdf_output,
        "opportunity_title": opportunity_title,
        "solicitation_number": solicitation_number,
        "agency": agency,
        "timestamp": timestamp
    }


def generate_from_outreach_record(outreach_record_id: str) -> Dict:
    """
    Generate capability statement from an OFFICER OUTREACH TRACKING record
    
    Args:
        outreach_record_id: Airtable record ID from OFFICER OUTREACH TRACKING
    
    Returns:
        Dict with generated file paths
    """
    # Get outreach record
    outreach_table = api.table(base_id, 'OFFICER OUTREACH TRACKING')
    record = outreach_table.get(outreach_record_id)
    fields = record['fields']
    
    # Extract data
    opportunity_title = fields.get('OPPORTUNITY TITLE', 'Federal Opportunity')
    solicitation_number = fields.get('SOLICITATION NUMBER', '')
    agency = fields.get('AGENCY', '')
    description = fields.get('DESCRIPTION', '')
    
    # Check if it's WOSB set-aside
    tags = fields.get('TAGS', [])
    set_aside = 'WOSB' if 'WOSB' in str(tags) else ''
    
    print(f"\n📄 Generating Capability Statement for:")
    print(f"   Opportunity: {opportunity_title}")
    print(f"   Solicitation: {solicitation_number}")
    print(f"   Agency: {agency}")
    print(f"   Set-Aside: {set_aside}")
    
    # Generate
    result = generate_opportunity_specific_capstat(
        opportunity_title=opportunity_title,
        solicitation_number=solicitation_number,
        agency=agency,
        set_aside=set_aside,
        description=description,
        opportunity_id=outreach_record_id
    )
    
    # Update outreach record
    try:
        outreach_table.update(outreach_record_id, {
            'CAPSTATGENERATED': True,
            'CAPSTAT GENERATED DATE': datetime.now().isoformat()
        })
        print(f"✅ Updated outreach record: CAPSTATGENERATED = True")
    except Exception as e:
        print(f"⚠️  Could not update outreach record: {e}")
    
    return result


def generate_from_opportunity_record(opportunity_record_id: str) -> Dict:
    """
    Generate capability statement from a GPSS OPPORTUNITIES record
    
    Args:
        opportunity_record_id: Airtable record ID from GPSS OPPORTUNITIES
    
    Returns:
        Dict with generated file paths
    """
    # Get opportunity record
    opp_table = api.table(base_id, 'GPSS OPPORTUNITIES')
    record = opp_table.get(opportunity_record_id)
    fields = record['fields']
    
    # Extract data
    opportunity_title = fields.get('Name', 'Federal Opportunity')
    solicitation_number = fields.get('RFP NUMBER', '')
    source = fields.get('SOURCE', '')
    source_status = fields.get('Source Status', '')
    
    # Determine agency from source or title
    agency = ""
    if 'FEDERAL' in source.upper():
        agency = "Federal Agency"
    elif 'RCOC' in opportunity_title.upper():
        agency = "Road Commission for Oakland County"
    
    # Determine set-aside
    set_aside = ""
    if 'WOSB' in source_status or 'WOSB' in opportunity_title:
        set_aside = "WOSB"
    
    print(f"\n📄 Generating Capability Statement for:")
    print(f"   Opportunity: {opportunity_title}")
    print(f"   RFP Number: {solicitation_number}")
    print(f"   Source: {source}")
    
    # Generate
    result = generate_opportunity_specific_capstat(
        opportunity_title=opportunity_title,
        solicitation_number=solicitation_number,
        agency=agency,
        set_aside=set_aside,
        description="",
        opportunity_id=opportunity_record_id
    )
    
    return result


if __name__ == "__main__":
    import sys
    
    print("=" * 80)
    print("OPPORTUNITY-SPECIFIC CAPABILITY STATEMENT GENERATOR")
    print("=" * 80)
    
    if len(sys.argv) < 2:
        print("\n❌ Usage:")
        print("   python3 auto_generate_opportunity_capstat.py <record_id>")
        print("   python3 auto_generate_opportunity_capstat.py --manual")
        print("\nExamples:")
        print("   python3 auto_generate_opportunity_capstat.py recKeusVGeCAeLor8")
        print("   python3 auto_generate_opportunity_capstat.py --manual")
        sys.exit(1)
    
    if sys.argv[1] == "--manual":
        print("\n📝 Manual Mode - Enter Opportunity Details:\n")
        opportunity_title = input("Opportunity Title: ")
        solicitation_number = input("Solicitation Number (optional): ")
        agency = input("Agency Name (optional): ")
        set_aside = input("Set-Aside Type (WOSB/EDWOSB/etc, optional): ")
        
        result = generate_opportunity_specific_capstat(
            opportunity_title=opportunity_title,
            solicitation_number=solicitation_number,
            agency=agency,
            set_aside=set_aside
        )
        
        print("\n" + "=" * 80)
        print("✅ CAPABILITY STATEMENT GENERATED!")
        print("=" * 80)
        print(f"HTML: {result['html_file']}")
        print(f"PDF: {result['pdf_file']}")
        print(f"Config: {result['config_file']}")
    
    else:
        record_id = sys.argv[1]
        
        # Try outreach table first
        try:
            result = generate_from_outreach_record(record_id)
            print("\n" + "=" * 80)
            print("✅ CAPABILITY STATEMENT GENERATED FROM OUTREACH RECORD!")
            print("=" * 80)
            print(f"HTML: {result['html_file']}")
            print(f"PDF: {result['pdf_file']}")
            print(f"Config: {result['config_file']}")
        except Exception as e:
            print(f"⚠️  Not an outreach record, trying opportunities table...")
            try:
                result = generate_from_opportunity_record(record_id)
                print("\n" + "=" * 80)
                print("✅ CAPABILITY STATEMENT GENERATED FROM OPPORTUNITY RECORD!")
                print("=" * 80)
                print(f"HTML: {result['html_file']}")
                print(f"PDF: {result['pdf_file']}")
                print(f"Config: {result['config_file']}")
            except Exception as e2:
                print(f"\n❌ Error: Could not generate from record {record_id}")
                print(f"   Outreach error: {e}")
                print(f"   Opportunity error: {e2}")
                sys.exit(1)
