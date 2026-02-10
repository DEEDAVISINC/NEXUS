#!/usr/bin/env python3
"""
Create RCOC 7802 Bid Submission PDF
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

# Register Avenir font if available
font_name = "Helvetica"
font_bold = "Helvetica-Bold"

try:
    avenir_path = "/System/Library/Fonts/Avenir.ttc"
    if os.path.exists(avenir_path):
        pdfmetrics.registerFont(TTFont('Avenir', avenir_path, subfontIndex=0))
        pdfmetrics.registerFont(TTFont('Avenir-Bold', avenir_path, subfontIndex=1))
        font_name = "Avenir"
        font_bold = "Avenir-Bold"
except:
    pass

# Create PDF
doc = SimpleDocTemplate(
    "RCOC_7802_BID_SUBMISSION.pdf",
    pagesize=letter,
    rightMargin=0.75*inch,
    leftMargin=0.75*inch,
    topMargin=0.75*inch,
    bottomMargin=0.75*inch
)

story = []
styles = getSampleStyleSheet()

# Title
title_style = ParagraphStyle(
    'Title',
    parent=styles['Heading1'],
    fontName=font_bold,
    fontSize=18,
    textColor=colors.HexColor('#0F172A'),
    alignment=TA_CENTER,
    spaceAfter=12
)

story.append(Paragraph("DEE DAVIS INC", title_style))
story.append(Paragraph("EDWOSB-Certified Woman-Owned Small Business", 
    ParagraphStyle('Subtitle', parent=styles['Normal'], fontSize=10, alignment=TA_CENTER, textColor=colors.HexColor('#6b7280'))))
story.append(Spacer(1, 0.2*inch))

# Bid header
header_style = ParagraphStyle(
    'Header',
    parent=styles['Heading2'],
    fontName=font_bold,
    fontSize=14,
    textColor=colors.HexColor('#D97706'),
    alignment=TA_CENTER,
    spaceAfter=12
)

story.append(Paragraph("BID SUBMISSION", header_style))
story.append(Paragraph("RCOC Solicitation #7802 - Building Tools", 
    ParagraphStyle('SubHeader', parent=styles['Normal'], fontSize=12, alignment=TA_CENTER, fontName=font_bold)))
story.append(Spacer(1, 0.2*inch))

# Company info
info_style = ParagraphStyle('Info', parent=styles['Normal'], fontSize=9, spaceAfter=4)
story.append(Paragraph("<b>Company:</b> DEE DAVIS INC", info_style))
story.append(Paragraph("<b>Address:</b> 755 W Big Beaver Rd, Suite 2020, Troy, MI 48084", info_style))
story.append(Paragraph("<b>Phone:</b> 248-376-4550", info_style))
story.append(Paragraph("<b>Email:</b> info@deedavis.biz", info_style))
story.append(Paragraph("<b>Contact:</b> Dee Davis, President & CEO", info_style))
story.append(Paragraph("<b>Certification:</b> EDWOSB (Economically Disadvantaged Woman-Owned Small Business)", info_style))
story.append(Spacer(1, 0.2*inch))

# Items table
items_data = [
    ['Item', 'Description', 'Mfr', 'Part #', 'Qty', 'Unit Price', 'Total']
]

items = [
    ['1', 'Hole Saw Arbor w/Pilot Drill', 'WESTWARD', '29VX02', '5', '$11.37', '$56.87'],
    ['2', '1"x11-6" Bandsaw Blade', 'SUPERCUT', '203981', '5', '$89.87', '$449.36'],
    ['3', '24" Coarse Garage Broom HD', 'MAGNOLIA', '455-2224LH', '20', '$34.26', '$685.17'],
    ['4', '24" Push Broom Synthetic Fine *', 'WEILER', '77014', '20', '$22.76', '$455.13'],
    ['5', 'Whisk Broom - Mixed Corn *', 'ABCO', '00300-12', '100', '$9.68', '$967.68'],
    ['6', '8" All Purpose Washing Brush', 'DQB', '11670', '10', '$7.58', '$75.79'],
    ['7', 'Threaded Broom Handle *', 'RUBBERMAID', 'FG636400LAC', '50', '$10.61', '$530.61'],
    ['8', '1-1/4" Putty Knife', 'HYDE', '02050', '5', '$6.77', '$33.87'],
    ['9', '2" Stiff Putty Knife', 'HYDE', '02300', '20', '$7.41', '$148.12'],
    ['10', '1/4"x5-1/2" Center Punch', 'GEARWRENCH', '82271', '2', '$8.69', '$17.37'],
    ['11', '1/4" Punch Prick - 6"', 'HARGRAVE', '34104', '2', '$2.59', '$5.18'],
    ['12', '5/8"x50\' Garden Hose', 'GILMOUR', '874501-1002', '5', '$46.45', '$232.24'],
    ['13', 'Padlock No. 1 (Keyed Alike) *', 'MASTER LOCK', '3QCOM', '25', '$10.69', '$267.18'],
    ['14', 'Padlock No. 3 (Keyed Alike) *', 'MASTER LOCK', '3QLF', '25', '$15.58', '$389.54'],
    ['15', 'Padlock Brass 2-1/2" Shackle', 'MASTER LOCK', 'M1KALJSTS', '15', '$37.84', '$567.53'],
    ['16', '2 Gallon Pressurized Sprayer', 'SOLO', '456', '40', '$60.25', '$2,409.94'],
]

for item in items:
    items_data.append(item)

# Add total row
items_data.append(['', '', '', '', '', '<b>TOTAL:</b>', '<b>$6,719.73</b>'])

# Create table
table = Table(items_data, colWidths=[0.5*inch, 2*inch, 1*inch, 0.9*inch, 0.5*inch, 0.8*inch, 0.9*inch])
table.setStyle(TableStyle([
    # Header row
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0F172A')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('FONTNAME', (0, 0), (-1, 0), font_bold),
    ('FONTSIZE', (0, 0), (-1, 0), 9),
    ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
    
    # Data rows
    ('FONTNAME', (0, 1), (-1, -2), font_name),
    ('FONTSIZE', (0, 1), (-1, -2), 8),
    ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # Item numbers
    ('ALIGN', (4, 1), (4, -1), 'CENTER'),  # Quantity
    ('ALIGN', (5, 1), (-1, -1), 'RIGHT'),  # Prices
    
    # Alternating rows
    ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#F9FAFB')]),
    
    # Total row
    ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#FEF3C7')),
    ('FONTNAME', (0, -1), (-1, -1), font_bold),
    ('FONTSIZE', (0, -1), (-1, -1), 10),
    ('ALIGN', (5, -1), (-1, -1), 'RIGHT'),
    
    # Borders
    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E5E7EB')),
    ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#0F172A')),
]))

story.append(table)
story.append(Spacer(1, 0.15*inch))

# Bonus items note
note_style = ParagraphStyle('Note', parent=styles['Normal'], fontSize=8, textColor=colors.HexColor('#6b7280'), leftIndent=10)
story.append(Paragraph("* Items marked with asterisk include bonus units at no additional charge:", note_style))
story.append(Paragraph("  • Item 4: Providing 24 EA (4 bonus units)", note_style))
story.append(Paragraph("  • Item 5: Providing 108 EA (8 bonus units)", note_style))
story.append(Paragraph("  • Item 7: Providing 60 EA (10 bonus units)", note_style))
story.append(Paragraph("  • Item 13: Providing 28 EA (3 bonus units)", note_style))
story.append(Paragraph("  • Item 14: Providing 28 EA (3 bonus units)", note_style))
story.append(Paragraph("  <b>Total: 28 bonus units provided at no charge</b>", ParagraphStyle('BonusNote', parent=note_style, fontName=font_bold)))

story.append(Spacer(1, 0.15*inch))

# Terms
terms_style = ParagraphStyle('Terms', parent=styles['Normal'], fontSize=9, spaceAfter=6)
story.append(Paragraph("<b>TERMS & CONDITIONS:</b>", ParagraphStyle('TermsHeader', parent=terms_style, fontName=font_bold, fontSize=10)))
story.append(Paragraph("• <b>Pricing:</b> FOB Destination, firm for contract period", terms_style))
story.append(Paragraph("• <b>Delivery:</b> 2-4 weeks ARO (after receipt of order)", terms_style))
story.append(Paragraph("• <b>Payment Terms:</b> Net 30 days", terms_style))
story.append(Paragraph("• <b>Contract Period:</b> March 1, 2026 - February 28, 2027", terms_style))
story.append(Paragraph("• <b>Tax:</b> Sales tax exempt (government client)", terms_style))
story.append(Paragraph("• <b>Quality:</b> All items meet or exceed manufacturer specifications", terms_style))
story.append(Paragraph("• <b>Warranty:</b> Full manufacturer warranty on all products", terms_style))

story.append(Spacer(1, 0.15*inch))

# Signature
sig_style = ParagraphStyle('Sig', parent=styles['Normal'], fontSize=10, spaceAfter=4)
story.append(Paragraph("Respectfully submitted,", sig_style))
story.append(Spacer(1, 0.3*inch))
story.append(Paragraph("_________________________________", sig_style))
story.append(Paragraph("<b>Dee Davis</b>", sig_style))
story.append(Paragraph("President & CEO", sig_style))
story.append(Paragraph("DEE DAVIS INC", sig_style))
story.append(Paragraph(f"Date: February 5, 2026", sig_style))

# Build PDF
doc.build(story)
print("✓ Generated: RCOC_7802_BID_SUBMISSION.pdf")
