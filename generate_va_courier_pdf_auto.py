#!/usr/bin/env python3
"""
Automated PDF Generator for VA Courier Capability Statement
Uses macOS built-in tools for conversion
"""

import os
import subprocess
import sys
from pathlib import Path

def generate_pdf_automated():
    """Generate PDF using macOS built-in tools"""
    
    print("\n" + "="*60)
    print("  VA COURIER CAPABILITY STATEMENT - AUTO PDF GENERATOR")
    print("  Dee Davis Inc. / Freight 1st Direct")
    print("="*60 + "\n")
    
    # Paths
    base_dir = Path("/Users/deedavis/NEXUS BACKEND")
    template_path = base_dir / "templates/va_courier_capability_statement.html"
    output_dir = base_dir / "photos_and_videos/SOURCES SOUGHT NOTICEGENERAL BID"
    logo_path = base_dir / "photos_and_videos/dee davis inc logo.png"
    
    output_html = output_dir / "VA_Courier_Capability_Statement_FORMATTED.html"
    output_pdf = output_dir / "VA_Courier_Capability_Statement_FINAL.pdf"
    
    print("🚑 Generating VA Medical Courier Capability Statement...")
    print("="*60)
    
    # Step 1: Copy logo to output directory
    logo_dest = output_dir / "dee_davis_inc_logo.png"
    if logo_path.exists():
        subprocess.run(["cp", str(logo_path), str(logo_dest)], check=True)
        print(f"✅ Logo copied to: {logo_dest.name}")
    
    # Step 2: Copy HTML to output directory
    if template_path.exists():
        subprocess.run(["cp", str(template_path), str(output_html)], check=True)
        print(f"✅ HTML created: {output_html.name}")
    
    # Step 3: Convert to PDF using cupsfilter (macOS built-in)
    print(f"\n📄 Converting to PDF using macOS built-in tools...")
    
    try:
        # Use cupsfilter to convert HTML to PDF
        result = subprocess.run(
            ["cupsfilter", str(output_html)],
            capture_output=True,
            check=True
        )
        
        # Write PDF output
        with open(output_pdf, 'wb') as f:
            f.write(result.stdout)
        
        if output_pdf.exists() and output_pdf.stat().st_size > 0:
            print(f"✅ PDF created: {output_pdf.name}")
            print(f"\n📂 Location: {output_pdf}")
            print("\n" + "="*60)
            print("  ✅ PDF READY TO SEND TO VA!")
            print("="*60)
            
            # Open the PDF
            subprocess.run(["open", str(output_pdf)])
            
            print("\n✅ PDF opened! Review it and you're ready to email!")
            return True
    except Exception as e:
        print(f"⚠️  Built-in conversion had issues: {e}")
        pass
    
    # Fallback: Manual instructions
    print("\n⚠️  Automated conversion requires manual step.")
    print("\n📋 QUICK MANUAL CONVERSION (30 seconds):")
    print(f"1. Opening HTML in browser now...")
    
    # Open in default browser
    subprocess.run(["open", str(output_html)])
    
    print(f"\n2. In your browser window:")
    print("   • Press Command+P (or File → Print)")
    print("   • Select 'Save as PDF'")
    print("   • Name it: VA_Courier_Capability_Statement_FINAL.pdf")
    print(f"   • Save to: {output_dir}")
    print("   • Click Save")
    print("\n✅ Done! You'll have your PDF ready to email!")
    
    print("\n" + "="*60)
    print("  NEXT STEPS:")
    print("="*60)
    print("1. Save the PDF (see instructions above)")
    print("2. Email to: eileen.meyer@va.gov")
    print("3. Subject: Response to Sources Sought 36C25226Q0235")
    print("4. Attach: Your PDF capability statement")
    print("5. Send by: February 12, 2026 at 10:00 AM Central")
    print("\n🚀 READY TO SUBMIT!")
    print("="*60 + "\n")
    
    return False

if __name__ == "__main__":
    try:
        generate_pdf_automated()
    except KeyboardInterrupt:
        print("\n\n⚠️  Generation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nPlease use manual method:")
        print("1. Open the HTML file in your browser")
        print("2. Press Command+P")
        print("3. Select 'Save as PDF'")
        sys.exit(1)
