#!/usr/bin/env python3
"""
RFQ Generator for Wood Poles
Generates professional PDFs with branding for suppliers

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
OUTPUT_DIR = Path("photos_and_videos/GENESEE WOOD POLES")
OUTPUT_DIR.mkdir(exist_ok=True)

# ============================================================================
# FONT REGISTRATION (AVENIR)
# ============================================================================

FONT_NAME = "Helvetica"  # Default fallback
FONT_BOLD = "Helvetica-Bold"

try:
    avenir_paths = [
        "/System/Library/Fonts/Avenir.ttc",
        "/System/Library/Fonts/Avenir Next.ttc",
        "/Library/Fonts/Avenir.ttc"
    ]
    
    for path in avenir_paths:
        if os.path.exists(path):
            pdfmetrics.registerFont(TTFont('Avenir', path, subfontIndex=0))
            pdfmetrics.registerFont(TTFont('Avenir-Bold', path, subfontIndex=1))
            FONT_NAME = "Avenir"
            FONT_BOLD = "Avenir-Bold"
            print(f"✓ Registered Avenir font from {path}")
            break
except Exception as e:
    print(f"⚠ Could not register Avenir font, using Helvetica: {e}")
    FONT_NAME = "Helvetica"
    FONT_BOLD = "Helvetica-Bold"


# ============================================================================
# WATERMARK FUNCTIONS
# ============================================================================

def create_watermark_pdf():
    """Create a PDF with DDI logo watermark"""
    watermark_path = 'watermark_temp.pdf'
    logo_path = 'logo_watermark.png'
    
    if not os.path.exists(logo_path):
        logo_path = 'logo.png'
    
    if not os.path.exists(logo_path):
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
    
    c.saveState()
    
    # Set very light opacity for watermark
    c.setFillAlpha(0.08)  # Very subtle watermark (was too dark before)
    
    logo_width = 3 * inch
    logo_height = 3 * inch
    x = (width - logo_width) / 2
    y = 2 * inch
    
    c.drawImage(logo_path, x, y, 
                width=logo_width, height=logo_height, 
                mask='auto', preserveAspectRatio=True)
    
    c.restoreState()
    c.save()
    return watermark_path


def apply_watermark(input_pdf_path, output_pdf_path):
    """Apply watermark to PDF"""
    try:
        watermark_path = create_watermark_pdf()
        
        pdf_reader = PdfReader(input_pdf_path)
        pdf_writer = PdfWriter()
        watermark_reader = PdfReader(watermark_path)
        watermark_page = watermark_reader.pages[0]
        
        for page in pdf_reader.pages:
            page.merge_page(watermark_page)
            pdf_writer.add_page(page)
        
        with open(output_pdf_path, 'wb') as output_file:
            pdf_writer.write(output_file)
        
        if os.path.exists(watermark_path):
            os.remove(watermark_path)
            
        return True
    except Exception as e:
        print(f"⚠ Warning: Could not apply watermark: {e}")
        if os.path.exists(input_pdf_path) and not os.path.exists(output_pdf_path):
            os.rename(input_pdf_path, output_pdf_path)
        return False


# ============================================================================
# SUPPLIER DATA
# ============================================================================

SUPPLIERS = {
    'brooks': {
        'name': 'Brooks Manufacturing Co.',
        'address': '2120 Pacific Street\nBellingham, WA 98229',
        'phone': '360-733-1700',
        'website': 'brooksmfg.com',
        'rfq_number': 'DDI-2026-003',  # Simple sequential - system auto-increments
        'notes': 'Woman Business Enterprise (WBE) Certified'
    },
    'koppers': {
        'name': 'Koppers Inc.',
        'address': '436 Seventh Avenue\nPittsburgh, PA 15219-1800',
        'phone': '+1 412-227-2001',
        'website': 'koppers.com',
        'rfq_number': 'DDI-2026-004',  # Simple sequential - system auto-increments
        'notes': 'Utility & Industrial Products Division'
    }
}


# ============================================================================
# RFQ GENERATOR
# ============================================================================

def generate_rfq_pdf(supplier_key):
    """Generate RFQ PDF for specified supplier"""
    
    supplier = SUPPLIERS[supplier_key]
    
    # Create filename
    filename = f"RFQ_{supplier['name'].replace(' ', '_').replace('.', '').upper()}.pdf"
    temp_pdf = OUTPUT_DIR / f"temp_{filename}"
    final_pdf = OUTPUT_DIR / filename
    
    # Create PDF
    doc = SimpleDocTemplate(str(temp_pdf), pagesize=letter,
                           leftMargin=0.75*inch, rightMargin=0.75*inch,
                           topMargin=0.75*inch, bottomMargin=0.75*inch)
    
    story = []
    styles = getSampleStyleSheet()
    
    # Custom styles using Avenir
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontName=FONT_BOLD,
        fontSize=18,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=6,
        alignment=TA_CENTER
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontName=FONT_NAME,
        fontSize=12,
        textColor=colors.HexColor('#666666'),
        spaceAfter=20,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontName=FONT_BOLD,
        fontSize=14,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=10,
        spaceBefore=12
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['BodyText'],
        fontName=FONT_NAME,
        fontSize=10,
        textColor=colors.HexColor('#333333'),
        spaceAfter=8,
        leading=14
    )
    
    # Header
    story.append(Paragraph("REQUEST FOR QUOTATION", title_style))
    story.append(Paragraph("Utility Wood Poles - Michigan Municipal Client", subtitle_style))
    story.append(Spacer(1, 0.15*inch))
    
    # RFQ Details Table
    rfq_data = [
        ['Date:', 'February 4, 2026', 'RFQ #:', supplier['rfq_number']],
        ['Quote Due:', 'February 12, 2026', 'Project:', 'Municipal Utility Poles']
    ]
    
    rfq_table = Table(rfq_data, colWidths=[1.2*inch, 2*inch, 1*inch, 2.5*inch])
    rfq_table.setStyle(TableStyle([
        ('FONTNAME', (0,0), (0,-1), FONT_BOLD),
        ('FONTNAME', (2,0), (2,-1), FONT_BOLD),
        ('FONTNAME', (1,0), (-1,-1), FONT_NAME),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.HexColor('#333333')),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(rfq_table)
    story.append(Spacer(1, 0.2*inch))
    
    # From/To Section
    from_to_data = [
        [Paragraph('<b>From:</b>', body_style), Paragraph('<b>To:</b>', body_style)],
        [Paragraph('Dee Davis Inc.<br/>EDWOSB Certified<br/>Michigan-Based Supplier', body_style),
         Paragraph(f"{supplier['name']}<br/>{supplier['address']}<br/>Phone: {supplier['phone']}<br/>{supplier['website']}", body_style)]
    ]
    
    from_to_table = Table(from_to_data, colWidths=[3.25*inch, 3.25*inch])
    from_to_table.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), FONT_NAME),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(from_to_table)
    story.append(Spacer(1, 0.2*inch))
    
    # Project Overview
    story.append(Paragraph("PROJECT OVERVIEW", heading_style))
    story.append(Paragraph(
        "Dee Davis Inc. is requesting a quote for <b>Southern Pine utility poles</b> for a <b>Michigan municipal road commission client</b>. "
        "We need competitive pricing for delivery to <b>Southeast Michigan</b>.",
        body_style
    ))
    story.append(Spacer(1, 0.1*inch))
    
    # Project details
    project_data = [
        ['Location:', 'Southeast Michigan'],
        ['Client Type:', 'Municipal Road Commission'],
        ['Project:', 'Utility infrastructure maintenance'],
        ['Delivery:', 'Southeast Michigan'],
        ['Timeline:', 'Quote needed by February 12, 2026']
    ]
    
    project_table = Table(project_data, colWidths=[1.5*inch, 5*inch])
    project_table.setStyle(TableStyle([
        ('FONTNAME', (0,0), (0,-1), FONT_BOLD),
        ('FONTNAME', (1,0), (1,-1), FONT_NAME),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.HexColor('#333333')),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(project_table)
    story.append(Spacer(1, 0.2*inch))
    
    # Items Requested
    story.append(Paragraph("ITEMS REQUESTED", heading_style))
    
    # Item 1
    story.append(Paragraph("<b>Item 1: 35-Foot Southern Pine Utility Poles</b>", body_style))
    story.append(Paragraph("<b>Quantity:</b> 4 each", body_style))
    
    specs_35 = [
        ['Length:', '35 feet'],
        ['Species:', 'Southern Pine (Yellow Pine)'],
        ['Class:', 'Class 1'],
        ['Top Diameter:', '13 inches'],
        ['Treatment:', 'Creosote, .15 DCOI (Depth of Creosote Oil Injection)'],
        ['Branding:', '<b>MDOT Branded</b> (Michigan DOT approved)'],
        ['Compliance:', 'ANSI O5.1 standards']
    ]
    
    specs_table_35 = Table(specs_35, colWidths=[1.5*inch, 4.5*inch])
    specs_table_35.setStyle(TableStyle([
        ('FONTNAME', (0,0), (0,-1), FONT_BOLD),
        ('FONTNAME', (1,0), (1,-1), FONT_NAME),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.HexColor('#333333')),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f9f9f9')),
    ]))
    story.append(specs_table_35)
    story.append(Spacer(1, 0.15*inch))
    
    # Item 2
    story.append(Paragraph("<b>Item 2: 40-Foot Southern Pine Utility Poles</b>", body_style))
    story.append(Paragraph("<b>Quantity:</b> 4 each", body_style))
    
    specs_40 = [
        ['Length:', '40 feet'],
        ['Species:', 'Southern Pine (Yellow Pine)'],
        ['Class:', 'Class 1'],
        ['Top Diameter:', '12 inches'],
        ['Treatment:', 'Creosote, .15 DCOI (Depth of Creosote Oil Injection)'],
        ['Branding:', '<b>MDOT Branded</b> (Michigan DOT approved)'],
        ['Compliance:', 'ANSI O5.1 standards']
    ]
    
    specs_table_40 = Table(specs_40, colWidths=[1.5*inch, 4.5*inch])
    specs_table_40.setStyle(TableStyle([
        ('FONTNAME', (0,0), (0,-1), FONT_BOLD),
        ('FONTNAME', (1,0), (1,-1), FONT_NAME),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.HexColor('#333333')),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f9f9f9')),
    ]))
    story.append(specs_table_40)
    story.append(Spacer(1, 0.2*inch))
    
    # Quote Requirements
    story.append(Paragraph("QUOTE REQUIREMENTS", heading_style))
    story.append(Paragraph("Please provide the following pricing breakdown:", body_style))
    story.append(Spacer(1, 0.1*inch))
    
    # Pricing Table
    pricing_data = [
        ['Item', 'Description', 'Qty', 'Unit Price', 'Total'],
        ['1', "35' Southern Pine Pole\nClass 1, 13\" dia, MDOT branded, .15 DCOI", '4', '', ''],
        ['2', "40' Southern Pine Pole\nClass 1, 12\" dia, MDOT branded, .15 DCOI", '4', '', ''],
        ['', 'Subtotal (Materials)', '', '', ''],
        ['', 'Freight/Delivery to Southeast MI', '', '', ''],
        ['', '<b>TOTAL QUOTE</b>', '', '', '']
    ]
    
    pricing_table = Table(pricing_data, colWidths=[0.5*inch, 3*inch, 0.5*inch, 1*inch, 1*inch])
    pricing_table.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,0), FONT_BOLD),
        ('FONTNAME', (0,1), (-1,-2), FONT_NAME),
        ('FONTNAME', (0,-1), (-1,-1), FONT_BOLD),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#4a90e2')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('TEXTCOLOR', (0,1), (-1,-1), colors.HexColor('#333333')),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('ALIGN', (2,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0,1), (-1,-2), [colors.white, colors.HexColor('#f9f9f9')]),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#e8f4f8')),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(pricing_table)
    story.append(Spacer(1, 0.2*inch))
    
    # Additional Information
    story.append(Paragraph("Additional Information Requested:", body_style))
    
    additional_info = [
        ['Lead Time:', 'How many days from order to delivery?'],
        ['MDOT Branding:', 'Confirm poles will be MDOT branded'],
        ['Payment Terms:', 'Standard payment terms'],
        ['Delivery Method:', 'Truck type, offloading equipment available'],
        ['Warranty:', 'Standard warranty/guarantee']
    ]
    
    info_table = Table(additional_info, colWidths=[1.5*inch, 4.5*inch])
    info_table.setStyle(TableStyle([
        ('FONTNAME', (0,0), (0,-1), FONT_BOLD),
        ('FONTNAME', (1,0), (1,-1), FONT_NAME),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.HexColor('#333333')),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f9f9f9')),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 0.2*inch))
    
    # Submission Instructions
    story.append(Paragraph("SUBMISSION INSTRUCTIONS", heading_style))
    story.append(Paragraph("<b>Please submit your quote by: February 12, 2026</b>", body_style))
    story.append(Paragraph("<b>Submit To:</b> info@deedavis.biz", body_style))
    story.append(Paragraph("<b>Subject Line:</b> \"Quote - Utility Poles for Michigan Municipal Client\"", body_style))
    story.append(Spacer(1, 0.1*inch))
    
    # Footer note
    story.append(Paragraph(
        "<b>Note:</b> This is for a Michigan municipal client. We need competitive pricing to remain competitive "
        "while maintaining quality standards. <b>MDOT branding is non-negotiable.</b>",
        body_style
    ))
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph("<b>CONFIDENTIAL:</b> This RFQ and your quote are confidential. Please do not share project details with third parties.", body_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Bottom description for clarity
    story.append(Paragraph("ABOUT THIS REQUEST", heading_style))
    story.append(Paragraph(
        "Dee Davis Inc. is a Michigan-based EDWOSB certified supplier serving municipal, state, and federal clients. "
        "We are submitting a bid to a Michigan road commission for utility pole supply and need your wholesale pricing to complete our bid package. "
        "This is a straightforward product resale opportunity - we handle all coordination, payment, and delivery logistics with the end client. "
        "Your quote will remain confidential and will only be used for our bid submission.",
        body_style
    ))
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph(
        "<b>What We Need From You:</b> Unit pricing for the specified poles, delivery costs to Flint MI, lead time, and confirmation of MDOT branding capability. "
        "We value long-term supplier relationships and aim for repeat business with reliable partners.",
        body_style
    ))
    
    # Build PDF
    doc.build(story)
    
    # Apply watermark
    apply_watermark(str(temp_pdf), str(final_pdf))
    
    # Clean up temp file
    if temp_pdf.exists():
        temp_pdf.unlink()
    
    return final_pdf


def add_supplier_to_nexus(supplier_name, product_type="Utility Poles", context=""):
    """Automatically add supplier to NEXUS contacts system"""
    try:
        from auto_contact_manager import AutoContactManager
        manager = AutoContactManager()
        result = manager.add_supplier_contact(
            supplier_name=supplier_name,
            product_type=product_type,
            context=f"RFQ sent for Genesee County Wood Poles. {context}"
        )
        if result.get('success'):
            print(f"  ✓ Supplier contact added to NEXUS: {supplier_name}")
        else:
            print(f"  ℹ {result.get('message', 'Contact already in system')}")
    except Exception as e:
        print(f"  ⚠ Could not add supplier to NEXUS: {e}")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    print("\n🌲 GENESEE COUNTY WOOD POLES - RFQ GENERATOR")
    print("=" * 60)
    
    if len(sys.argv) > 1:
        supplier_key = sys.argv[1].lower()
        if supplier_key not in SUPPLIERS:
            print(f"❌ Unknown supplier: {supplier_key}")
            print(f"Available: {', '.join(SUPPLIERS.keys())}")
            sys.exit(1)
        
        suppliers_to_generate = [supplier_key]
    else:
        suppliers_to_generate = list(SUPPLIERS.keys())
    
    for supplier_key in suppliers_to_generate:
        supplier = SUPPLIERS[supplier_key]
        print(f"\n📄 Generating RFQ for {supplier['name']}...")
        
        try:
            output = generate_rfq_pdf(supplier_key)
            print(f"✅ RFQ Generated: {output}")
            print(f"   RFQ #: {supplier['rfq_number']}")
            print(f"   Phone: {supplier['phone']}")
            
            print("\nAdding supplier to NEXUS contacts system...")
            add_supplier_to_nexus(supplier['name'])
            
            print("\n📧 Ready to send to supplier!")
            print(f"   Email: Use contact form at {supplier['website']}")
            print(f"   Phone: {supplier['phone']}")
            
        except Exception as e:
            print(f"❌ Error generating RFQ: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("✅ RFQ generation complete!")
    print(f"📁 Files saved to: {OUTPUT_DIR}")
    print("\n📞 NEXT STEPS:")
    print("1. Call each supplier to introduce yourself")
    print("2. Email the PDF RFQ after the call")
    print("3. Follow up if no response in 2-3 days")
    print("4. Quotes due: February 12, 2026")
