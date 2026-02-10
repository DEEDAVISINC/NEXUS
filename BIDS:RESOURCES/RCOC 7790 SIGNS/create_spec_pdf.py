#!/usr/bin/env python3
"""Create professional PDF from technical specifications"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

# Try to register Avenir font
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
    "DDI_TECHNICAL_SPECIFICATIONS_TRAFFIC_SIGNS.pdf",
    pagesize=letter,
    rightMargin=inch,
    leftMargin=inch,
    topMargin=inch,
    bottomMargin=inch
)

# Styles
styles = getSampleStyleSheet()

title_style = ParagraphStyle(
    'CustomTitle',
    parent=styles['Heading1'],
    fontName=font_bold,
    fontSize=20,
    textColor=colors.HexColor('#0F172A'),
    spaceAfter=6,
    alignment=TA_CENTER
)

subtitle_style = ParagraphStyle(
    'CustomSubtitle',
    parent=styles['Heading2'],
    fontName=font_name,
    fontSize=14,
    textColor=colors.HexColor('#D97706'),
    spaceAfter=6,
    alignment=TA_CENTER
)

section_style = ParagraphStyle(
    'SectionHeading',
    parent=styles['Heading2'],
    fontName=font_bold,
    fontSize=14,
    textColor=colors.HexColor('#0F172A'),
    spaceAfter=12,
    spaceBefore=18
)

subsection_style = ParagraphStyle(
    'SubsectionHeading',
    parent=styles['Heading3'],
    fontName=font_bold,
    fontSize=12,
    textColor=colors.HexColor('#374151'),
    spaceAfter=6,
    spaceBefore=12
)

body_style = ParagraphStyle(
    'CustomBody',
    parent=styles['Normal'],
    fontName=font_name,
    fontSize=10,
    textColor=colors.black,
    spaceAfter=8,
    alignment=TA_JUSTIFY
)

bullet_style = ParagraphStyle(
    'CustomBullet',
    parent=styles['Normal'],
    fontName=font_name,
    fontSize=10,
    textColor=colors.black,
    spaceAfter=4,
    leftIndent=20,
    bulletIndent=10
)

critical_style = ParagraphStyle(
    'Critical',
    parent=styles['Normal'],
    fontName=font_bold,
    fontSize=11,
    textColor=colors.HexColor('#DC2626'),
    spaceAfter=8,
    spaceBefore=8
)

example_style = ParagraphStyle(
    'Example',
    parent=styles['Code'],
    fontName='Courier',
    fontSize=10,
    textColor=colors.HexColor('#059669'),
    backColor=colors.HexColor('#F3F4F6'),
    spaceAfter=8,
    leftIndent=20
)

# Build document
story = []

# Header
story.append(Paragraph("DEE DAVIS INC", title_style))
story.append(Paragraph("Technical Specifications - Traffic Signs", subtitle_style))
story.append(Paragraph("RFQ #: DDI-2026-007", subtitle_style))
story.append(Spacer(1, 0.3*inch))

# A. General Requirements
story.append(Paragraph("A. General Requirements", section_style))
story.append(Paragraph(
    'All supplied traffic signs shall meet the requirements of the <b>Michigan Department of Transportation (MDOT) 2020 Standard Specifications For Construction, Section 919</b>.',
    body_style
))

story.append(Paragraph("Sign Panel Materials", subsection_style))
story.append(Paragraph(
    'All sign panels shall be either <b>Type III or Type V</b>, except for the following signs which shall be <b>0.063" aluminum sheets</b>:',
    body_style
))
for item in [
    'DEAD END – RIGHT SPECIAL 36"x9" FLUORESCENT YELLOW',
    'DEAD END – LEFT SPECIAL 36"x9" FLUORESCENT YELLOW',
    'NO OUTLET – RIGHT W14-2AR(MOD) 36"X9" FLUORESCENT YELLOW',
    'NO OUTLET – LEFT W14-2AR(MOD) 36"X9" FLUORESCENT YELLOW'
]:
    story.append(Paragraph(f'• {item}', bullet_style))

story.append(Paragraph("Sign Sheeting", subsection_style))
story.append(Paragraph(
    'Sign sheeting shall comply with <b>MDOT Section 919.02B and Table 919-3</b>. Sign reflective sheeting is for highway signs and other traffic control devices to assure optimum day and night visibility when exposed to a light source in dry and wet weather conditions.',
    body_style
))
story.append(Paragraph("<b>Bidders must specify:</b>", body_style))
story.append(Paragraph("• Brand name and manufacturer of sheeting used", bullet_style))
story.append(Paragraph("• Confirmation that materials are listed on <b>MDOT's Qualified Products List (QPL)</b>", bullet_style))

# B. Fabrication
story.append(Paragraph("B. Fabrication", section_style))
story.append(Paragraph("Signs shall be fabricated in accordance with:", body_style))
story.append(Paragraph("• Current <b>MDOT Traffic Safety Standard Highway Signs Manual</b>", bullet_style))
story.append(Paragraph("• <b>MDOT Reflective Sign Sheeting Guidelines</b>", bullet_style))
story.append(Paragraph("• All sheeting materials must be listed on <b>MDOT QPL</b>", bullet_style))

# C. Sign Face Requirements
story.append(Paragraph("C. Sign Face Requirements", section_style))

story.append(Paragraph("⚠️ CRITICAL: Required Markings on ALL Signs", critical_style))
story.append(Paragraph(
    '<b>ALL fabricated signs shall bear the following information in characters not to exceed one half inch in height:</b>',
    body_style
))
for i, item in enumerate([
    'The initials <b>"RCOC"</b> in uppercase letters',
    'The <b>2-digit month/2-digit year of fabrication</b> (e.g., "02/26" for February 2026)',
    'Uppercase initials of the <b>sheeting manufacturer</b> (e.g., "3M" for 3M Company)',
    '<b>Uppercase initials (4-character max)</b> representing the supplier fabricating the sign'
], 1):
    story.append(Paragraph(f'{i}. {item}', bullet_style))

story.append(Paragraph(
    '<b>Location:</b> This information string shall be on or near the sign border at the <b>bottom, lower left portion</b> of the sign face.',
    body_style
))
story.append(Paragraph('<b>Example marking:</b>', body_style))
story.append(Paragraph('RCOC 02/26 3M ABCD', example_style))

story.append(Paragraph("Additional Requirements", subsection_style))
story.append(Paragraph("• No splices shall be in the sign face", bullet_style))
story.append(Paragraph("• Design shall conform to detailed drawings in the current <b>Michigan Manual of Uniform Traffic Control Devices (MMUTCD)</b>", bullet_style))
story.append(Paragraph("• Holes in aluminum as specified", bullet_style))
story.append(Paragraph("• Sign faces must conform to all standards specified herein", bullet_style))

# D. Packaging and Shipping
story.append(Paragraph("D. Packaging and Shipping", section_style))

story.append(Paragraph("Protection Requirements", subsection_style))
story.append(Paragraph("Fabricated signs shall be packaged to ensure:", body_style))
story.append(Paragraph("• Protection from damage in transit", bullet_style))
story.append(Paragraph("• Readiness for use upon delivery", bullet_style))
story.append(Paragraph("• Sheeting, decals, and signs shall <b>NOT become wet in transit</b>", bullet_style))

story.append(Paragraph("Packaging Standards", subsection_style))
story.append(Paragraph("• <b>Packaged cartons:</b> Maximum weight 60 pounds", bullet_style))
story.append(Paragraph("• <b>Plastic banded</b> with each sign face protected", bullet_style))
story.append(Paragraph("• <b>Slip sheet paper (glossy side)</b> against each sign face", bullet_style))
story.append(Paragraph("• <b>Pallet skids:</b> Protected and plastic banded with slip sheet protection", bullet_style))
story.append(Paragraph("• Banding, stacking, or crating in accord with commercially accepted standards", bullet_style))
story.append(Paragraph("• Adequate support and protection to prevent movement and chafing during transit", bullet_style))

story.append(Paragraph("Carton/Pallet Marking", subsection_style))
story.append(Paragraph("Each carton or pallet skid shall be clearly marked with:", body_style))
story.append(Paragraph("• Contents description", bullet_style))
story.append(Paragraph("• Quantity", bullet_style))
story.append(Paragraph("• Item stock code number (as shown on DEE DAVIS INC purchase order)", bullet_style))
story.append(Paragraph("• Any special packaging or handling requirements", bullet_style))

# E. Certification Requirements
story.append(Paragraph("E. Certification Requirements", section_style))
story.append(Paragraph("The supplier shall certify:", body_style))
story.append(Paragraph("• All materials furnished are <b>new or refurbished aluminum like new</b>", bullet_style))
story.append(Paragraph("• All work will be <b>good quality, free from faults and defects</b>", bullet_style))
story.append(Paragraph("• All work conforms to these technical specifications", bullet_style))
story.append(Paragraph("• All materials and work conform to MDOT standards and MMUTCD requirements", bullet_style))
story.append(Paragraph(
    '<b>Samples may be requested to confirm acceptability.</b> All work not conforming to these specifications, including substitutions not approved and authorized, may be considered defective.',
    body_style
))

# F. Quality Assurance
story.append(Paragraph("F. Quality Assurance", section_style))

story.append(Paragraph("MDOT Qualified Products List (QPL)", subsection_style))
story.append(Paragraph("• All sign sheeting materials MUST be listed on MDOT QPL", bullet_style))
story.append(Paragraph("• Supplier must provide documentation/certification of QPL listing", bullet_style))
story.append(Paragraph("• Non-compliant materials will not be accepted", bullet_style))

story.append(Paragraph("MUTCD Compliance", subsection_style))
story.append(Paragraph("• All signs must meet current Michigan Manual of Uniform Traffic Control Devices (MMUTCD) standards", bullet_style))
story.append(Paragraph("• Supplier must provide MUTCD compliance certification with quote", bullet_style))

# G. Delivery Requirements
story.append(Paragraph("G. Delivery Requirements", section_style))
story.append(Paragraph("• Delivery to: <b>Waterford, MI 48328</b> (specific address provided upon award)", bullet_style))
story.append(Paragraph("• Signs must arrive ready for immediate installation", bullet_style))
story.append(Paragraph("• Packaging must protect signs during transit", bullet_style))
story.append(Paragraph("• Delivery coordination required (will be specified in purchase order)", bullet_style))

# Footer
story.append(Spacer(1, 0.4*inch))
story.append(Paragraph("Questions or Clarifications", section_style))
story.append(Paragraph(
    'Contact: <b>Dee Davis</b><br/>DEE DAVIS INC<br/>Phone: 248-376-4550<br/>Email: info@deedavis.biz',
    body_style
))

story.append(Spacer(1, 0.2*inch))
story.append(Paragraph(
    '<b>This specification is part of RFQ #DDI-2026-007</b><br/>All quotes must reference this RFQ number<br/>Quote deadline: February 10, 2026 @ 12:00 PM EST',
    ParagraphStyle('Footer', parent=body_style, alignment=TA_CENTER, textColor=colors.HexColor('#6b7280'))
))

# Build PDF
doc.build(story)
print("✓ Generated: DDI_TECHNICAL_SPECIFICATIONS_TRAFFIC_SIGNS.pdf")
