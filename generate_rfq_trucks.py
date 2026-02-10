#!/usr/bin/env python3
"""
FAST RFQ Generator for Trucks
Auto-extracts from solicitation and generates supplier RFQ

⚠️ CRITICAL BUYER PROTECTION RULES ⚠️
BEFORE generating RFQ, verify:
1. NO buyer/client names (RCOC, Genesee, Canton, etc.)
2. NO specific cities (Flint, Detroit, etc.)
3. NO specific addresses with street names
4. NO solicitation numbers from original RFP
5. USE generic terms only: "Municipal client", "Southeast Michigan"
6. RFQ numbers: DDI-YYYY-### (simple sequential, no buyer info)

See: .cursor/rules/rfq-buyer-protection-checklist.mdc
"""

import sys
import os
from pathlib import Path
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PyPDF2 import PdfReader, PdfWriter

# Output directory
OUTPUT_DIR = Path("GENERATED_QUOTES")
OUTPUT_DIR.mkdir(exist_ok=True)

# ============================================================================
# FONT REGISTRATION (AVENIR)
# ============================================================================

FONT_NAME = "Helvetica"  # Default fallback
FONT_BOLD = "Helvetica-Bold"

try:
    # Common Avenir locations on macOS
    avenir_paths = [
        "/System/Library/Fonts/Avenir.ttc",
        "/System/Library/Fonts/Avenir Next.ttc",
        "/Library/Fonts/Avenir.ttc"
    ]
    
    for path in avenir_paths:
        if os.path.exists(path):
            # Register Avenir fonts
            pdfmetrics.registerFont(TTFont('Avenir', path, subfontIndex=0))
            pdfmetrics.registerFont(TTFont('Avenir-Bold', path, subfontIndex=1))
            FONT_NAME = "Avenir"
            FONT_BOLD = "Avenir-Bold"
            print(f"✓ Registered Avenir font from {path}")
            break
except Exception as e:
    # If Avenir fails, just use Helvetica
    print(f"⚠ Could not register Avenir font, using Helvetica: {e}")
    FONT_NAME = "Helvetica"
    FONT_BOLD = "Helvetica-Bold"


# ============================================================================
# WATERMARK FUNCTIONS
# ============================================================================

def create_watermark_pdf():
    """Create a PDF with DDI logo watermark"""
    watermark_path = 'watermark_temp.pdf'
    logo_path = 'logo_watermark.png'  # Use pre-created watermark logo
    
    # Check if watermark logo exists, fallback to regular logo
    if not os.path.exists(logo_path):
        logo_path = 'logo.png'
    
    if not os.path.exists(logo_path):
        # If no logo found, create text watermark as fallback
        c = canvas.Canvas(watermark_path, pagesize=letter)
        width, height = letter
        c.saveState()
        c.translate(width/2, height/2)
        c.rotate(45)
        c.setFillColorRGB(0.9, 0.9, 0.9)
        c.setFont(FONT_BOLD, 60)
        c.drawCentredString(0, 0, "DEE DAVIS INC")
        c.restoreState()
        c.save()
        return watermark_path
    
    c = canvas.Canvas(watermark_path, pagesize=letter)
    width, height = letter
    
    # Draw logo watermark (straight, not rotated)
    c.saveState()
    
    # Draw logo at reduced opacity (watermark logo already has reduced opacity)
    logo_width = 3 * inch
    logo_height = 3 * inch
    
    # Position in lower portion of page (moved down to avoid title text)
    x = (width - logo_width) / 2
    y = 2 * inch  # Positioned near bottom instead of center
    
    c.drawImage(logo_path, x, y, 
                width=logo_width, height=logo_height, 
                mask='auto', preserveAspectRatio=True)
    
    c.restoreState()
    c.save()
    
    return watermark_path


def add_watermark_to_pdf(input_pdf_path, output_pdf_path):
    """Add watermark to existing PDF"""
    try:
        # Create watermark
        watermark_path = create_watermark_pdf()
        
        # Read input PDF and watermark
        input_pdf = PdfReader(input_pdf_path)
        watermark_pdf = PdfReader(watermark_path)
        watermark_page = watermark_pdf.pages[0]
        
        output = PdfWriter()
        
        # Add watermark to each page
        for page in input_pdf.pages:
            page.merge_page(watermark_page)
            output.add_page(page)
        
        # Write output
        with open(output_pdf_path, 'wb') as f:
            output.write(f)
        
        # Clean up temp watermark
        if os.path.exists(watermark_path):
            os.remove(watermark_path)
        
        return True
    except Exception as e:
        print(f"Watermark error: {e}")
        # If watermark fails, just copy original
        import shutil
        shutil.copy(input_pdf_path, output_pdf_path)
        return False

# RCOC 7814 TRUCK DATA (extracted from solicitation)
RCOC_7814_DATA = {
    "rfq_number": "DDI-2026-TRUCKS-001",
    "title": "REQUEST FOR QUOTE - Pickup Trucks (16 Units)",
    "project": "Municipal Fleet Replacement",
    "client": "Michigan municipal government agency (confidential)",
    "location": "Southeast Michigan / Oakland County area",
    "quote_due": "February 10, 2026 by 5:00 PM EST",
    "bid_deadline": "February 17, 2026",
    "delivery": "Spring 2026",
    
    "configurations": [
        {
            "name": "Inspector Trucks",
            "quantity": 7,
            "specs": {
                "Cab": "Extended Cab",
                "Bed": "6.7' Standard Bed",
                "Color": "Red",
                "Body": "Aluminum",
                "Drive": "4x4 with electronically actuated shifting",
                "Differential": "Limited-Slip Rear",
                "Engine": "Turbocharged V6 or V8 (300hp/350ft-lb minimum)",
                "Transmission": "10-speed automatic",
                "Wheels": "17\" Steel with All-Terrain Tires",
                "Towing": "Class 4 Package with receiver hitch",
                "Brake": "Integrated Electronic Brake Controller, 7-pin plug",
                "Spare": "Full Size",
                "Radio": "Android Auto/Apple CarPlay capable",
                "Inverter": "In-cab 120v (400-watt minimum)",
                "Cruise": "Cruise Control",
                "Lights": "Daytime Running, Automatic Headlights",
                "Switches": "Factory Upfitter switches (if available)",
                "Seats": "40/20/40 Vinyl with center storage"
            },
            "upfitting": [
                "Four Amber & Green Combo Class 1 Strobe Lights (2 grill, 2 rear bumper)",
                "Amber & Green Combo Class 1 Beacon",
                "Rubber Floor Mats",
                "LINE-X Style Spray-in Bed Liner",
                "Nerf Bar Style Running Boards",
                "ARE DCU 23\" Truck Cap (Red, painted to match)",
                "Standard Toolboxes with Doors (driver & passenger sides)",
                "ARE 'Style 5' Toolbox Dividers (both sides)",
                "Hinge-up Rear Door with Window",
                "Front Picture Window",
                "Lighting in toolboxes and interior",
                "1500lb CargoGlide Mounted in Bed",
                "TM100 Traffic Advisor at Rear",
                "Truck Office Cargo Deck (replaces rear seats)"
            ]
        },
        {
            "name": "Supervisor Trucks",
            "quantity": 2,
            "specs": {
                "Cab": "Regular Cab",
                "Bed": "6.5' Short Bed",
                "Color": "White",
                "Body": "Aluminum",
                "Drive": "2WD acceptable",
                "Differential": "Limited-Slip Rear",
                "Engine": "Turbocharged V6 or V8 (300hp/350ft-lb minimum)",
                "Transmission": "10-speed automatic",
                "Wheels": "17\" Steel with All-Terrain Tires",
                "Spare": "Full Size",
                "Radio": "Android Auto/Apple CarPlay capable",
                "Cruise": "Cruise Control",
                "Lights": "Daytime Running, Automatic Headlights",
                "Switches": "Factory Upfitter switches (if available)",
                "Seats": "40/20/40 Vinyl with center storage",
                "Floor": "Full Vinyl Covering"
            },
            "upfitting": [
                "Four Amber & Green Combo Class 1 Strobe Lights (2 grill, 2 rear bumper)",
                "Rubber Floor Mats",
                "LINE-X Style Spray-in Bed Liner",
                "Weatherguard Gullwing Toolbox Model 127-52-4 (NO SUBSTITUTIONS)",
                "Nerf Bar Style Running Boards",
                "DOT Reflector Tape (sides and tailgate)"
            ]
        },
        {
            "name": "Crew Trucks",
            "quantity": 7,
            "specs": {
                "Cab": "Regular Cab",
                "Bed": "6.5' Short Bed",
                "Color": "Red",
                "Body": "Aluminum",
                "Drive": "2WD acceptable",
                "Differential": "Limited-Slip Rear",
                "Engine": "Turbocharged V6 or V8 (300hp/350ft-lb minimum)",
                "Transmission": "10-speed automatic",
                "Wheels": "17\" Steel with All-Terrain Tires",
                "Spare": "Full Size",
                "Radio": "Android Auto/Apple CarPlay capable",
                "Cruise": "Cruise Control",
                "Lights": "Daytime Running, Automatic Headlights",
                "Switches": "Factory Upfitter switches (if available)",
                "Seats": "40/20/40 Vinyl with center storage",
                "Floor": "Full Vinyl Covering"
            },
            "upfitting": [
                "Four Amber & Green Combo Class 1 Strobe Lights (2 grill, 2 rear bumper)",
                "Back Rack installed in Bed",
                "Amber & Green Combo Class 1 Mini Light Bar (mounted to back rack)",
                "Two 1600+ lumen work lights (mounted to back rack)",
                "Rubber Floor Mats",
                "LINE-X Style Spray-in Bed Liner"
            ]
        }
    ]
}


def generate_rfq_pdf(supplier_name="SUPPLIER"):
    """Generate RFQ PDF for RCOC 7814 Trucks"""
    
    data = RCOC_7814_DATA
    rfq_num = data['rfq_number']
    
    # Temp file (before watermark)
    temp_file = OUTPUT_DIR / f"temp_{rfq_num}_{supplier_name.replace(' ', '_')}.pdf"
    
    # Final output file
    output_file = OUTPUT_DIR / f"RFQ_{rfq_num}_{supplier_name.replace(' ', '_')}.pdf"
    
    # Create PDF
    doc = SimpleDocTemplate(
        str(temp_file),
        pagesize=letter,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch,
        leftMargin=1*inch,
        rightMargin=1*inch
    )
    
    # Styles (using Avenir font)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Title'],
        fontSize=24,
        textColor=colors.HexColor('#1e3a8a'),
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName=FONT_BOLD
    )
    
    heading_style = ParagraphStyle(
        'Heading',
        fontSize=16,
        textColor=colors.HexColor('#1e3a8a'),
        spaceAfter=8,
        spaceBefore=12,
        fontName=FONT_BOLD
    )
    
    subheading_style = ParagraphStyle(
        'SubHeading',
        fontSize=12,
        textColor=colors.HexColor('#2563eb'),
        spaceAfter=6,
        spaceBefore=8,
        fontName=FONT_BOLD
    )
    
    body_style = ParagraphStyle(
        'Body',
        fontSize=10,
        spaceAfter=6,
        fontName=FONT_NAME
    )
    
    # Content
    story = []
    
    # Header with logo
    story.append(Spacer(1, 0.3*inch))
    
    # Add company logo
    logo_path = 'logo.png'
    if os.path.exists(logo_path):
        logo = Image(logo_path, width=2*inch, height=2*inch)
        story.append(logo)
        story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("DEE DAVIS INC", title_style))
    
    cert_style = ParagraphStyle(
        'CertStyle',
        parent=body_style,
        fontSize=12,
        textColor=colors.HexColor('#1e3a8a'),
        alignment=TA_CENTER,
        spaceAfter=6
    )
    story.append(Paragraph("Certified EDWOSB Prime Contractor", cert_style))
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph("755 W Big Beaver Rd, Suite 2020, Troy, MI 48084", body_style))
    story.append(Paragraph("Phone: 248-376-4550 | Email: info@deedavis.biz", body_style))
    story.append(Paragraph("CAGE Code: 8UMX3", body_style))
    story.append(Spacer(1, 0.3*inch))
    
    story.append(Paragraph("_" * 100, body_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Title
    story.append(Paragraph("REQUEST FOR QUOTE", title_style))
    story.append(Paragraph(data['title'], heading_style))
    story.append(Paragraph(f"RFQ Number: {rfq_num}", body_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Key info
    info_data = [
        ['Issue Date:', datetime.now().strftime('%B %d, %Y')],
        ['Quote Due:', data['quote_due']],
        ['Project:', data['project']],
        ['Location:', data['location']],
        ['Delivery:', data['delivery']],
    ]
    
    info_table = Table(info_data, colWidths=[2*inch, 4*inch])
    info_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), FONT_BOLD),
        ('FONTNAME', (1, 0), (1, -1), FONT_NAME),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Overview
    story.append(Paragraph("PROJECT OVERVIEW", heading_style))
    overview = f"""
    DEE DAVIS INC is seeking competitive quotes for {len(data['configurations'])} configurations 
    of pickup trucks (total {sum(c['quantity'] for c in data['configurations'])} units) for a 
    {data['client']}. All vehicles must be current model year with complete commercial upfitting 
    as specified below.
    """
    story.append(Paragraph(overview, body_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Configurations
    for config in data['configurations']:
        story.append(Paragraph(f"{config['name'].upper()} - {config['quantity']} UNITS", heading_style))
        
        # Base specs
        story.append(Paragraph("<b>Base Vehicle Specifications:</b>", body_style))
        for key, value in config['specs'].items():
            story.append(Paragraph(f"• <b>{key}:</b> {value}", body_style))
        
        story.append(Spacer(1, 0.1*inch))
        
        # Upfitting
        story.append(Paragraph("<b>Commercial Upfitting Required:</b>", body_style))
        for item in config['upfitting']:
            story.append(Paragraph(f"• {item}", body_style))
        
        story.append(Spacer(1, 0.2*inch))
        
        # Pricing table
        story.append(Paragraph("<b>YOUR QUOTE - COMPLETE THIS SECTION:</b>", subheading_style))
        story.append(Spacer(1, 0.1*inch))
        
        pricing_data = [
            ['Item', 'Description', 'Qty', 'Unit Price', 'Extended Total'],
            ['Base Vehicle', f'{config["name"]} Base Truck', str(config['quantity']), '$__________', '$__________'],
            ['Upfitting', f'{config["name"]} Upfitting', str(config['quantity']), '$__________', '$__________'],
            ['', '', '', '', ''],
            ['TOTAL', f'{config["name"].upper()} TURNKEY', str(config['quantity']), '$__________', '$__________'],
        ]
        
        pricing_table = Table(pricing_data, colWidths=[0.9*inch, 2.1*inch, 0.6*inch, 1.2*inch, 1.2*inch])
        pricing_table.setStyle(TableStyle([
            # Header row
            ('FONTNAME', (0, 0), (-1, 0), FONT_BOLD),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a8a')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (1, 0), 'LEFT'),
            ('ALIGN', (2, 0), (-1, 0), 'CENTER'),
            
            # Data rows
            ('FONTNAME', (0, 1), (-1, 2), FONT_NAME),
            ('FONTSIZE', (0, 1), (-1, 2), 9),
            ('ALIGN', (0, 1), (1, 2), 'LEFT'),
            ('ALIGN', (2, 1), (2, 2), 'CENTER'),
            ('ALIGN', (3, 1), (4, 2), 'CENTER'),
            
            # Spacer row
            ('LINEBELOW', (0, 2), (-1, 2), 1, colors.HexColor('#1e3a8a')),
            
            # Total row
            ('FONTNAME', (0, -1), (-1, -1), FONT_BOLD),
            ('FONTSIZE', (0, -1), (-1, -1), 10),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#dbeafe')),
            ('ALIGN', (0, -1), (1, -1), 'LEFT'),
            ('ALIGN', (2, -1), (2, -1), 'CENTER'),
            ('ALIGN', (3, -1), (4, -1), 'CENTER'),
            
            # Grid
            ('GRID', (0, 0), (-1, -2), 0.5, colors.grey),
            ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#1e3a8a')),
            
            # Padding
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(pricing_table)
        story.append(Spacer(1, 0.3*inch))
    
    # Summary
    story.append(Paragraph("TOTAL PROJECT QUOTE SUMMARY", heading_style))
    story.append(Spacer(1, 0.1*inch))
    
    summary_data = [
        ['Configuration', 'Qty', 'Unit Price\n(Turnkey)', 'Extended Total'],
        ['Inspector Trucks', '7', '$__________', '$__________'],
        ['Supervisor Trucks', '2', '$__________', '$__________'],
        ['Crew Trucks', '7', '$__________', '$__________'],
        ['', '', '', ''],
        ['GRAND TOTAL (16 TRUCKS)', '16', '', '$__________'],
    ]
    
    summary_table = Table(summary_data, colWidths=[2*inch, 0.6*inch, 1.7*inch, 1.7*inch])
    summary_table.setStyle(TableStyle([
        # Header row
        ('FONTNAME', (0, 0), (-1, 0), FONT_BOLD),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a8a')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('ALIGN', (1, 0), (-1, 0), 'CENTER'),
        
        # Data rows
        ('FONTNAME', (0, 1), (-1, 3), FONT_NAME),
        ('FONTSIZE', (0, 1), (-1, 3), 10),
        ('ALIGN', (0, 1), (0, 3), 'LEFT'),
        ('ALIGN', (1, 1), (-1, 3), 'CENTER'),
        
        # Spacer row
        ('LINEBELOW', (0, 3), (-1, 3), 2, colors.HexColor('#1e3a8a')),
        
        # Grand total row
        ('FONTNAME', (0, -1), (-1, -1), FONT_BOLD),
        ('FONTSIZE', (0, -1), (-1, -1), 11),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#1e3a8a')),
        ('TEXTCOLOR', (0, -1), (-1, -1), colors.white),
        ('ALIGN', (0, -1), (0, -1), 'LEFT'),
        ('ALIGN', (1, -1), (-1, -1), 'CENTER'),
        
        # Grid
        ('GRID', (0, 0), (-1, -2), 0.5, colors.grey),
        ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#1e3a8a')),
        
        # Padding
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Requirements
    story.append(Paragraph("QUOTE REQUIREMENTS", heading_style))
    requirements = """
    <b>Please provide:</b><br/>
    1. Turnkey pricing (base truck + all upfitting complete)<br/>
    2. Breakdown of base vehicle cost vs. upfitting cost<br/>
    3. Delivery timeline from order to delivery<br/>
    4. Warranty information (vehicle and upfitting)<br/>
    5. Payment terms (Net 30 preferred)<br/>
    6. Quote validity period (must be valid through February 17, 2026)<br/>
    <br/>
    <b>Critical Requirements:</b><br/>
    • All vehicles must be CURRENT MODEL YEAR<br/>
    • All upfitting must be COMPLETE and ready for service<br/>
    • Weatherguard Model 127-52-4 toolbox (NO substitutions on Supervisor trucks)<br/>
    • Professional-grade upfitting meeting municipal standards<br/>
    """
    story.append(Paragraph(requirements, body_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Submission
    story.append(Paragraph("SUBMISSION INSTRUCTIONS", heading_style))
    submission = f"""
    <b>Quote Due:</b> {data['quote_due']}<br/>
    <b>Submit To:</b> info@deedavis.biz<br/>
    <b>Subject:</b> RFQ Response: {rfq_num} - [YOUR COMPANY NAME]<br/>
    <b>Format:</b> PDF preferred<br/>
    <br/>
    <b>Questions?</b> Contact Dee Davis at 248-376-4550<br/>
    """
    story.append(Paragraph(submission, body_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Footer
    story.append(Paragraph("_" * 100, body_style))
    story.append(Spacer(1, 0.1*inch))
    footer = """
    <b>DEE DAVIS INC</b> | Troy, MI 48084 | 248-376-4550 | deedavis.biz<br/>
    CAGE Code: 8UMX3 | EDWOSB Certified | PROPRIETARY & CONFIDENTIAL
    """
    story.append(Paragraph(footer, ParagraphStyle('Footer', fontSize=8, alignment=TA_CENTER)))
    
    # Build PDF (temp file without watermark)
    doc.build(story)
    
    # Add watermark to create final PDF
    print("  Adding watermark...")
    add_watermark_to_pdf(str(temp_file), str(output_file))
    
    # Clean up temp file
    if os.path.exists(str(temp_file)):
        os.remove(str(temp_file))
    
    return output_file


def add_supplier_to_nexus(supplier_name, product_type="Pickup Trucks", context=""):
    """
    Automatically add supplier to NEXUS contacts system
    """
    try:
        from auto_contact_manager import AutoContactManager
        
        manager = AutoContactManager()
        result = manager.add_supplier_contact(
            supplier_name=supplier_name.replace('_', ' ').title(),
            product_type=product_type,
            context=f"RFQ sent for RCOC 7814 Trucks. {context}"
        )
        
        if result.get('success'):
            print(f"  ✓ Supplier contact added to NEXUS: {supplier_name}")
        else:
            print(f"  ℹ {result.get('message', 'Contact already in system')}")
    except Exception as e:
        print(f"  ⚠ Could not add supplier to NEXUS: {e}")


if __name__ == '__main__':
    supplier = sys.argv[1] if len(sys.argv) > 1 else "National_Auto_Fleet_Group"
    
    print("=" * 60)
    print("GENERATING RFQ FOR RCOC 7814 TRUCKS")
    print("=" * 60)
    print(f"Supplier: {supplier}")
    print(f"RFQ Number: {RCOC_7814_DATA['rfq_number']}")
    print()
    
    output = generate_rfq_pdf(supplier)
    
    print(f"✅ RFQ Generated: {output}")
    print()
    
    # Automatically add supplier to NEXUS contacts
    print("Adding supplier to NEXUS contacts system...")
    add_supplier_to_nexus(supplier)
    print()
    
    print("📧 Ready to send to supplier!")
    print("=" * 60)
