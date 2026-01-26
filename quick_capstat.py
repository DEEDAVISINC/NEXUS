#!/usr/bin/env python3
"""
Quick Capability Statement Generator
Interactive CLI tool for rapid capability statement generation

Usage:
    python3 quick_capstat.py
"""

from capability_statement_generator import handle_generate_capability_statement
import sys


def main():
    """Interactive capability statement generator"""
    
    print("=" * 60)
    print("⚡ QUICK CAPABILITY STATEMENT GENERATOR")
    print("=" * 60)
    print()
    
    # Get client info
    print("📋 Client Information:")
    client_name = input("  Client Name: ").strip()
    
    if not client_name:
        print("❌ Client name is required")
        sys.exit(1)
    
    rfq_number = input("  RFQ Number: ").strip()
    
    if not rfq_number:
        print("❌ RFQ number is required")
        sys.exit(1)
    
    rfq_title = input("  RFQ Title (optional): ").strip()
    
    print()
    
    # Select template
    print("🎨 Select Template:")
    print("  1. Default (Industrial Supplies) - Amber")
    print("  2. VA Medical (Healthcare) - Blue")
    print("  3. Construction - Orange")
    print("  4. Auto (Let system choose)")
    print()
    
    template_choice = input("  Choice (1-4): ").strip()
    
    template_map = {
        '1': 'default',
        '2': 'va_medical',
        '3': 'construction',
        '4': 'auto'
    }
    
    template = template_map.get(template_choice, 'default')
    
    print()
    print("=" * 60)
    print("🎯 GENERATING CAPABILITY STATEMENT")
    print("=" * 60)
    print()
    print(f"Client: {client_name}")
    print(f"RFQ: {rfq_number}")
    if rfq_title:
        print(f"Title: {rfq_title}")
    print(f"Template: {template}")
    print()
    
    # Confirm
    response = input("Generate? (y/n): ")
    
    if response.lower() != 'y':
        print("❌ Cancelled")
        sys.exit(0)
    
    print()
    print("⏳ Generating...")
    
    # Generate
    try:
        result = handle_generate_capability_statement(
            client_name=client_name,
            rfq_number=rfq_number,
            rfq_title=rfq_title if rfq_title else None,
            template=template
        )
        
        if result['success']:
            print()
            print("=" * 60)
            print("✅ SUCCESS!")
            print("=" * 60)
            print()
            print(f"HTML File: {result['html_file']}")
            print(f"PDF File: {result['pdf_file']}")
            print(f"Airtable ID: {result['airtable_record_id']}")
            print()
            print("📧 Ready to attach to your RFP response email!")
            print()
            
            # Offer to open
            open_files = input("Open files now? (y/n): ")
            if open_files.lower() == 'y':
                import subprocess
                subprocess.run(['open', result['html_file']])
                subprocess.run(['open', result['pdf_file']])
        else:
            print()
            print(f"❌ Error: {result.get('error', 'Unknown error')}")
            print()
    
    except Exception as e:
        print()
        print(f"❌ Error: {e}")
        print()
        sys.exit(1)


if __name__ == '__main__':
    main()
