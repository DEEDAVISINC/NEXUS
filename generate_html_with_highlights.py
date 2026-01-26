#!/usr/bin/env python3
"""
Capability Statement HTML Generator with Highlights
Generates professional HTML capability statements for DEE DAVIS INC
"""

import json
import sys
import os
from pathlib import Path


def generate_html(config, output_file):
    """Generate HTML capability statement from config using template"""
    
    company = config['company']
    opportunity = config['opportunity']
    colors = config['colors']
    highlights = config['highlights']
    
    # Load template
    template_path = Path(__file__).parent / 'capability_statement_template.html'
    with open(template_path, 'r', encoding='utf-8') as f:
        html = f.read()
    
    # Build certifications HTML
    certifications_html = ""
    for cert in config['certifications']:
        cert_name = cert.split(' - ')[0] if ' - ' in cert else cert
        cert_desc = cert.split(' - ')[1] if ' - ' in cert else ''
        certifications_html += f"""                        <div class="flex items-start">
                            <i data-lucide="check" class="w-4 h-4 mt-1 mr-2 text-accent flex-shrink-0"></i>
                            <div>
                                <strong class="block text-accent">{cert_name}</strong>
                                <span class="text-xs text-gray-300">{cert_desc}</span>
                            </div>
                        </div>
"""
    
    # Build highlights HTML
    highlights_html = ""
    for item in highlights['items']:
        highlights_html += f"""                        <div class="flex items-start">
                            <span class="text-lg mr-2">{item['icon']}</span>
                            <div class="flex-1">
                                <div class="font-bold text-xs text-gray-500 uppercase">{item['label']}</div>
                                <div class="text-sm font-semibold text-primary">{item['value']}</div>
                            </div>
                        </div>
"""
    
    # Build competencies HTML
    competencies_html = ""
    for comp in config['core_competencies']:
        competencies_html += f"""                        <div class="flex items-start p-3 bg-blue-50 rounded-lg border-l-4" style="border-color: {colors['primary']}">
                            <div class="mr-4 mt-1 bg-white p-2 rounded-full shadow-sm text-primary">
                                <i data-lucide="package-search" class="w-5 h-5"></i>
                            </div>
                            <div>
                                <h4 class="font-bold text-primary">{comp['title']}</h4>
                                <p class="text-xs text-gray-600 mt-1">{comp['description']}</p>
                            </div>
                        </div>
"""
    
    # Build benefits HTML
    benefits_html = ""
    for benefit in config['benefits']:
        benefits_html += f"""                        <div class="bg-gray-50 p-3 rounded hover:bg-yellow-50 transition-colors">
                            <div class="font-bold text-primary text-sm mb-1">{benefit['icon']} {benefit['title']}</div>
                            <p class="text-xs text-gray-600">{benefit['description']}</p>
                        </div>
"""
    
    capabilities = config['contract_capabilities']
    
    # Replace placeholders
    replacements = {
        '{{PRIMARY_COLOR}}': colors['primary'],
        '{{ACCENT_COLOR}}': colors['accent'],
        '{{COMPANY_NAME}}': company['name'],
        '{{CLIENT_NAME}}': opportunity['client_name'],
        '{{RFQ_NUMBER}}': opportunity['rfq_number'],
        '{{DATE}}': opportunity['date'],
        '{{LOGO_PATH}}': 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==',  # Placeholder
        '{{CAGE_CODE}}': company['cage_code'],
        '{{UEI}}': company.get('uei', 'HJB4KNYJVGZ1'),
        '{{DUNS}}': company['duns'],
        '{{TAX_ID}}': company['tax_id'],
        '{{SAM_STATUS}}': company['sam_status'],
        '{{FOUNDED}}': company['founded'],
        '{{CERTIFICATIONS_HTML}}': certifications_html,
        '{{HIGHLIGHTS_HTML}}': highlights_html,
        '{{OVERVIEW}}': config['overview'],
        '{{COMPETENCIES_HTML}}': competencies_html,
        '{{BENEFITS_HTML}}': benefits_html,
        '{{COMMITMENT}}': config['commitment'],
        '{{PRESIDENT}}': company['president'].upper(),
        '{{ADDRESS}}': company['address'],
        '{{CITY}}': company['city'],
        '{{STATE}}': company['state'],
        '{{ZIP}}': company['zip'],
        '{{PHONE}}': company['phone'],
        '{{EMAIL}}': company['email'],
        '{{WEBSITE}}': company['website'],
        '{{PAYMENT_TERMS}}': capabilities['payment_terms'],
        '{{DELIVERY_TIME}}': capabilities['delivery_time'],
        '{{COVERAGE}}': capabilities['coverage'],
        '{{INSURANCE}}': capabilities['insurance']
    }
    
    for placeholder, value in replacements.items():
        html = html.replace(placeholder, str(value))
    
    # Write to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✓ Generated HTML: {output_file}")
    return output_file


def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python3 generate_html_with_highlights.py <config.json>")
        print("Example: python3 generate_html_with_highlights.py default_config.json")
        sys.exit(1)
    
    config_file = sys.argv[1]
    
    # Load config
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except FileNotFoundError:
        print(f"Error: Config file '{config_file}' not found")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in config file: {e}")
        sys.exit(1)
    
    # Generate output filename (remove _config suffix if present)
    config_path = Path(config_file)
    filename = config_path.stem
    if filename.endswith('_config'):
        filename = filename[:-7]  # Remove '_config'
    output_file = filename + '.html'
    
    # Generate HTML
    generate_html(config, output_file)


if __name__ == '__main__':
    main()
