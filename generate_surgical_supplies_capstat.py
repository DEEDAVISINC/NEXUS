#!/usr/bin/env python3
"""
SURGICAL SUPPLIES CAPABILITY STATEMENT GENERATOR
Dee Davis Inc. - EDWOSB Alternative Response
"""

import os
import subprocess
from pathlib import Path

def generate():
    print("\n" + "="*60)
    print("  SURGICAL SUPPLIES CAPABILITY STATEMENT GENERATOR")
    print("  Dee Davis Inc. - EDWOSB Alternative")
    print("="*60 + "\n")
    
    # Paths
    base_dir = Path("/Users/deedavis/NEXUS BACKEND")
    template = base_dir / "templates/surgical_supplies_capability_statement.html"
    output_dir = base_dir / "photos_and_videos/SURGICAL SUPPLIES SOLE SOURCE"
    logo = base_dir / "photos_and_videos/dee davis inc logo.png"
    
    output_html = output_dir / "Surgical_Supplies_Capability_Statement.html"
    
    print("🏥 Generating Surgical Supplies Capability Statement...")
    print("="*60)
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy logo
    logo_dest = output_dir / "dee_davis_inc_logo.png"
    if not logo_dest.exists():
        subprocess.run(["cp", str(logo), str(logo_dest)])
    print(f"✅ Logo ready")
    
    # Copy template
    subprocess.run(["cp", str(template), str(output_html)])
    print(f"✅ HTML created: {output_html.name}")
    
    # Open in browser
    subprocess.run(["open", str(output_html)])
    
    print("\n" + "="*60)
    print("  TO SAVE AS PDF:")
    print("="*60)
    print("1. Press Command+P (Print)")
    print("2. Select 'Save as PDF'")
    print("3. Name: Dee_Davis_Inc_Surgical_Supplies_Capability.pdf")
    print("4. Attach to email!")
    
    print("\n" + "="*60)
    print("  NEXT STEPS:")
    print("="*60)
    print("1. Get CO contact from SAM.gov")
    print("2. Send email (template in EMAIL_TO_CONTRACTING_OFFICER.txt)")
    print("3. Attach this PDF")
    print("4. Submit by TOMORROW (Feb 7, 2026)!")
    print("\n🚀 READY TO SUBMIT!")
    print("="*60 + "\n")

if __name__ == "__main__":
    generate()
