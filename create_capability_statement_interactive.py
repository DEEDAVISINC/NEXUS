#!/usr/bin/env python3
"""
Interactive Capability Statement Creator
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
        "1": {"name": "Professional Navy & Gold", "primary": "#1e3a8a", "accent": "#d97706"},
        "2": {"name": "Healthcare Blue & Teal", "primary": "#0c4a6e", "accent": "#0891b2"},
        "3": {"name": "Construction Brown & Orange", "primary": "#713f12", "accent": "#f97316"},
        "4": {"name": "Technology Purple & Violet", "primary": "#4c1d95", "accent": "#8b5cf6"},
        "5": {"name": "Corporate Blue & Sky", "primary": "#0369a1", "accent": "#0284c7"},
        "6": {"name": "Environmental Green", "primary": "#14532d", "accent": "#16a34a"},
    }
    
    for key, scheme in color_schemes.items():
        print(f"{key}. {scheme['name']}")
    
    choice = get_input("\nEnter number (1-6)", "1")
    
    if choice in color_schemes:
        return color_schemes[choice]
    else:
        return color_schemes["1"]


def add_highlights():
    """Add optional highlights"""
    highlights = []
    
    print("\n" + "="*60)
    print("ADD HIGHLIGHTS (Optional)")
    print("="*60)
    
    # NAICS
    if get_input("Add NAICS code? (y/n)", "y").lower() == 'y':
        naics = get_input("  NAICS code (e.g., '541330 - Engineering Services')")
        if naics:
            highlights.append({"type": "naics", "content": naics})
    
    # Key Partners
    if get_input("Add key partners? (y/n)", "y").lower() == 'y':
        partners = get_input("  Partners (separate with |)")
        if partners:
            highlights.append({"type": "partners", "content": partners})
    
    # Past Performance
    if get_input("Add past performance? (y/n)", "y").lower() == 'y':
        performance = get_input("  Past performance highlight")
        if performance:
            highlights.append({"type": "performance", "content": performance})
    
    # Certifications
    if get_input("Add certifications? (y/n)", "y").lower() == 'y':
        certs = get_input("  Certifications (separate with |)")
        if certs:
            highlights.append({"type": "certifications", "content": certs})
    
    # Service Area
    if get_input("Add service area? (y/n)", "y").lower() == 'y':
        area = get_input("  Service area")
        if area:
            highlights.append({"type": "service_area", "content": area})
    
    # Custom highlight
    if get_input("Add custom highlight? (y/n)", "n").lower() == 'y':
        custom_title = get_input("  Title")
        custom_content = get_input("  Content")
        if custom_title and custom_content:
            highlights.append({"type": "custom", "title": custom_title, "content": custom_content})
    
    return highlights


def create_capability_statement():
    """Interactive capability statement creator"""
    
    print("\n" + "="*60)
    print("CAPABILITY STATEMENT CREATOR")
    print("="*60)
    print("Let's create your capability statement!")
    print("Just answer the questions below.")
    print("="*60)
    
    # Company Info
    print("\n--- COMPANY INFORMATION (press Enter to use defaults) ---")
    company_name = get_input("Company name", "DEE DAVIS INC")
    cage_code = get_input("CAGE Code", "8UMX3")
    uei = get_input("UEI", "HJB4KNYJVGZ1")
    duns = get_input("DUNS", "002636755")
    tax_id = get_input("Tax ID", "84-4114181")
    
    # Client/RFQ Info
    print("\n--- RFQ/CLIENT INFORMATION ---")
    client_name = get_input("Client name (e.g., 'VA Medical Center')")
    rfq_number = get_input("RFQ number (e.g., '789456')")
    date = get_input("Date", "January 2026")
    
    # Choose colors
    color_scheme = choose_colors()
    
    # Company Overview
    print("\n--- COMPANY OVERVIEW ---")
    overview = get_multiline_input("Paste or type your company overview:")
    
    # Core Competencies
    print("\n--- CORE COMPETENCIES ---")
    print("Enter your core competencies (one per line, type 'done' when finished):")
    competencies = []
    while True:
        comp = input("  Competency: ").strip()
        if comp.lower() == 'done' or not comp:
            break
        competencies.append(comp)
    
    if not competencies:
        competencies = [
            "Supply Chain Management",
            "Logistics & Distribution",
            "Vendor Management",
            "Quality Assurance"
        ]
    
    # Differentiators
    print("\n--- DIFFERENTIATORS ---")
    print("What makes you different? (one per line, type 'done' when finished):")
    differentiators = []
    while True:
        diff = input("  Differentiator: ").strip()
        if diff.lower() == 'done' or not diff:
            break
        differentiators.append(diff)
    
    if not differentiators:
        differentiators = [
            "EDWOSB Certified - Enhanced contracting opportunities",
            "Michigan-based with nationwide reach",
            "24/7 customer support and rapid response times",
            "Proven track record with government agencies"
        ]
    
    # Highlights
    highlights = add_highlights()
    
    # Build config
    config = {
        "company": {
            "name": company_name,
            "address": "755 W Big Beaver Rd, Suite 2020, Troy, MI 48084",
            "phone": "248-376-4550",
            "email": "info@deedavis.biz",
            "website": "www.deedavis.biz",
            "cage_code": cage_code,
            "uei": uei,
            "duns": duns,
            "tax_id": tax_id
        },
        "rfq_details": {
            "client_name": client_name,
            "rfq_number": rfq_number,
            "date": date
        },
        "colors": {
            "primary": color_scheme["primary"],
            "accent": color_scheme["accent"],
            "text": "#374151"
        },
        "company_overview": overview,
        "core_competencies": competencies,
        "differentiators": differentiators,
        "certifications": [
            {"name": "EDWOSB", "description": "Economically Disadvantaged Woman-Owned Small Business"},
            {"name": "WOSB", "description": "Woman-Owned Small Business"},
            {"name": "SBE", "description": "Small Business Enterprise"}
        ],
        "highlights": highlights,
        "logo_path": "dee_davis_logo.png"
    }
    
    # Save config
    filename = f"cap_stmt_{client_name.lower().replace(' ', '_')}_config.json"
    with open(filename, 'w') as f:
        json.dump(config, f, indent=4)
    
    print("\n" + "="*60)
    print(f"✓ Configuration saved: {filename}")
    print("="*60)
    
    # Generate files
    print("\n🎨 Generating HTML and PDF...")
    
    try:
        subprocess.run(['python3', 'generate_html_with_highlights.py', filename], check=True)
        subprocess.run(['python3', 'generate_enhanced_pdf.py', filename], check=True)
        
        print("\n" + "="*60)
        print("✅ SUCCESS! Your capability statement is ready!")
        print("="*60)
        
        base = filename.replace('_config.json', '')
        print(f"\n📄 Your files:")
        print(f"   • {base}.html")
        print(f"   • {base}_enhanced.pdf")
        print(f"   • {filename} (config - save this for future edits)")
        print("\n🎯 Next steps:")
        print(f"   1. Open {base}.html in browser to preview")
        print(f"   2. Submit {base}_enhanced.pdf to client")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error generating files: {e}")
        print(f"But your config is saved: {filename}")


if __name__ == "__main__":
    create_capability_statement()
