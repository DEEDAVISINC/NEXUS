"""
Generate Beautiful VA Courier Capability Statement
Uses professional HTML template to create vibrant PDF
"""

import subprocess
import os
from pathlib import Path
from datetime import datetime

def generate_va_courier_capability_statement():
    """Generate professional VA courier capability statement PDF"""
    
    print("🚑 Generating VA Medical Courier Capability Statement...")
    print("=" * 60)
    
    # Paths
    template_path = Path(__file__).parent / 'templates' / 'va_courier_capability_statement.html'
    output_dir = Path(__file__).parent / 'photos_and_videos' / 'SOURCES SOUGHT NOTICEGENERAL BID'
    output_html = output_dir / 'VA_Courier_Capability_Statement_FORMATTED.html'
    output_pdf = output_dir / 'Dee_Davis_Inc_VA_Courier_Capability_Statement.pdf'
    
    # Read template
    with open(template_path, 'r') as f:
        html_content = f.read()
    
    # Save formatted HTML
    with open(output_html, 'w') as f:
        f.write(html_content)
    
    print(f"✅ HTML created: {output_html.name}")
    
    # Generate PDF using wkhtmltopdf
    try:
        print("\n📄 Converting to PDF...")
        
        cmd = [
            'wkhtmltopdf',
            '--enable-local-file-access',
            '--page-size', 'Letter',
            '--margin-top', '0',
            '--margin-bottom', '0',
            '--margin-left', '0',
            '--margin-right', '0',
            '--print-media-type',
            str(output_html),
            str(output_pdf)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ PDF created: {output_pdf.name}")
            print(f"\n📂 Location: {output_pdf}")
            print(f"📏 Size: {output_pdf.stat().st_size / 1024:.1f} KB")
            print("\n🎨 BEAUTIFUL, PROFESSIONAL PDF READY!")
            print("\n✅ READY TO ATTACH TO EMAIL TO VA!")
            return str(output_pdf)
        else:
            print("⚠️ PDF generation failed. Using HTML version instead.")
            print(f"Error: {result.stderr}")
            print(f"\n✅ You can still use the HTML file: {output_html}")
            print("   (Open in browser and Print to PDF)")
            return str(output_html)
            
    except FileNotFoundError:
        print("\n⚠️ wkhtmltopdf not installed.")
        print("\n📋 TWO OPTIONS:")
        print("1. Open HTML in browser and Print to PDF")
        print(f"   File: {output_html}")
        print("\n2. Install wkhtmltopdf:")
        print("   Mac: brew install wkhtmltopdf")
        print("   Then run this script again")
        print("\n✅ HTML version is ready to use!")
        return str(output_html)

if __name__ == '__main__':
    print("\n" + "="*60)
    print("  VA MEDICAL COURIER CAPABILITY STATEMENT GENERATOR")
    print("  Dee Davis Inc. / Freight 1st Direct")
    print("="*60 + "\n")
    
    output_file = generate_va_courier_capability_statement()
    
    print("\n" + "="*60)
    print("  NEXT STEPS:")
    print("="*60)
    print("1. Review the generated document")
    print("2. Attach to email to eileen.meyer@va.gov")
    print("3. Include WOSB certification")
    print("4. Include insurance certificates")
    print("5. Send by Monday, February 10, 2026")
    print("\n🚀 READY TO SUBMIT!")
    print("="*60 + "\n")
