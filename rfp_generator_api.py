#!/usr/bin/env python3
"""
NEXUS RFP Generator API
Automated Supplier RFP Creation with Buyer Protection

Creates professional, branded supplier RFPs with DDI watermark
Similar to quote_generator but for creating supplier-facing RFPs
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import io
from datetime import datetime, timedelta
from pyairtable import Api
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak,
    Table, TableStyle, KeepTogether, Image
)
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PyPDF2 import PdfReader, PdfWriter
import json

app = Flask(__name__)
CORS(app)

# ============================================================================
# CONFIGURATION
# ============================================================================

# Load environment variables
env_file = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(env_file):
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()

AIRTABLE_API_KEY = os.getenv('AIRTABLE_API_KEY') or os.getenv('AIRTABLE_PERSONAL_ACCESS_TOKEN')
BASE_ID = os.getenv('AIRTABLE_BASE_ID')

# Initialize Airtable
airtable_api = Api(AIRTABLE_API_KEY)

# ============================================================================
# FONT REGISTRATION
# ============================================================================

# Register Avenir font (macOS system font)
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

# Create directories
os.makedirs('generated_rfps', exist_ok=True)

# ============================================================================
# RFP NUMBER GENERATOR
# ============================================================================

def generate_rfp_number(category):
    """Generate unique DDI RFP number"""
    try:
        table = airtable_api.table(BASE_ID, 'SUPPLIER_RFPS')
        records = table.all()
        
        year = datetime.now().year
        count = len([r for r in records if str(year) in r['fields'].get('ddi_rfp_number', '')])
        
        # Category codes
        category_codes = {
            'Pressure Washing': 'PW',
            'Landscaping': 'LS',
            'Janitorial': 'JAN',
            'Construction': 'CON',
            'Supplies': 'SUP',
            'HVAC': 'HVAC',
            'Plumbing': 'PLU',
            'Electrical': 'ELE',
            'General Services': 'GEN',
            'Painting': 'PAINT',
            'Maintenance': 'MAINT',
        }
        
        code = category_codes.get(category, 'GEN')
        number = f"DDI-{year}-{code}-{count + 1:03d}"
        
        return number
    except Exception as e:
        # Fallback if Airtable not available
        return f"DDI-{datetime.now().year}-GEN-001"


# ============================================================================
# PDF WATERMARK CREATOR
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


# ============================================================================
# PDF GENERATOR
# ============================================================================

def create_rfp_pdf(rfp_number, data):
    """Generate professional RFP PDF with DDI branding"""
    
    # File paths
    temp_pdf = f'generated_rfps/temp_{rfp_number}.pdf'
    final_pdf = f'generated_rfps/RFP_{rfp_number}.pdf'
    
    # Create PDF
    doc = SimpleDocTemplate(temp_pdf, pagesize=letter,
                           topMargin=0.75*inch, bottomMargin=0.75*inch,
                           leftMargin=1*inch, rightMargin=1*inch)
    
    # Styles
    styles = getSampleStyleSheet()
    
    # Custom styles with Avenir font
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontName=FONT_BOLD,
        fontSize=24,
        textColor=colors.HexColor('#1e3a8a'),
        spaceAfter=12,
        alignment=TA_CENTER
    )
    
    heading1_style = ParagraphStyle(
        'CustomHeading1',
        parent=styles['Heading1'],
        fontName=FONT_BOLD,
        fontSize=16,
        textColor=colors.HexColor('#1e3a8a'),
        spaceAfter=12,
        spaceBefore=12,
        borderWidth=2,
        borderColor=colors.HexColor('#1e3a8a'),
        borderPadding=8,
    )
    
    heading2_style = ParagraphStyle(
        'CustomHeading2',
        parent=styles['Heading2'],
        fontName=FONT_BOLD,
        fontSize=14,
        textColor=colors.HexColor('#2563eb'),
        spaceAfter=8,
        spaceBefore=8,
        alignment=TA_CENTER
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['BodyText'],
        fontName=FONT_NAME,
        fontSize=10,
        alignment=TA_JUSTIFY,
        spaceAfter=6,
    )
    
    # Story (content)
    story = []
    
    # ========================================================================
    # COVER PAGE
    # ========================================================================
    
    story.append(Spacer(1, 0.5*inch))
    
    # Add company logo
    logo_path = 'logo.png'
    if os.path.exists(logo_path):
        logo = Image(logo_path, width=2*inch, height=2*inch)
        story.append(logo)
        story.append(Spacer(1, 0.3*inch))
    
    # Company name - centered
    story.append(Paragraph("DEE DAVIS INC", title_style))
    
    # Certification line - centered, directly under company name
    cert_style = ParagraphStyle(
        'CertStyle',
        parent=styles['Normal'],
        fontName=FONT_NAME,
        fontSize=12,
        textColor=colors.HexColor('#1e3a8a'),
        alignment=TA_CENTER,
        spaceAfter=6
    )
    story.append(Paragraph("Certified EDWOSB Prime Contractor", cert_style))
    story.append(Spacer(1, 0.5*inch))
    
    # Create centered style for RFQ number and lines
    centered_style = ParagraphStyle(
        'Centered',
        parent=styles['Normal'],
        fontName=FONT_NAME,
        fontSize=10,
        alignment=TA_CENTER
    )
    
    # RFQ Title (all centered) - REQUEST FOR QUOTE comes first
    story.append(Paragraph("REQUEST FOR QUOTE", heading1_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Horizontal line (centered)
    story.append(Paragraph("_" * 80, centered_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Project name and RFQ number below the line
    story.append(Paragraph(data.get('project_name', 'Project'), heading2_style))
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph(f"RFQ Number: {rfp_number}", centered_style))
    
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("_" * 80, centered_style))
    story.append(Spacer(1, 0.5*inch))
    
    # Key dates
    issue_date = datetime.now().strftime('%B %d, %Y')
    quote_due = data.get('quote_due_date', '')
    if quote_due:
        try:
            quote_due_dt = datetime.fromisoformat(quote_due)
            quote_due = quote_due_dt.strftime('%B %d, %Y at %I:%M %p %Z')
        except:
            pass
    
    dates_data = [
        ['RFQ Issue Date:', issue_date],
        ['Questions Due:', data.get('questions_due', '(See RFQ)')],
        ['Quote Due Date:', quote_due or '(See RFQ)'],
        ['Contract Start Date:', data.get('contract_start', '(Upon Award)')],
        ['Contract Period:', data.get('contract_period', '(See RFQ)')],
    ]
    
    dates_table = Table(dates_data, colWidths=[2.5*inch, 3.5*inch])
    dates_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), FONT_BOLD),
        ('FONTNAME', (1, 0), (1, -1), FONT_NAME),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(dates_table)
    
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("_" * 80, centered_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Contact info
    story.append(Paragraph("<b>ISSUED BY:</b>", styles['Normal']))
    story.append(Paragraph("DEE DAVIS INC", styles['Normal']))
    story.append(Paragraph("Troy, Michigan 48084", styles['Normal']))
    story.append(Paragraph("248-376-4550", styles['Normal']))
    story.append(Paragraph("proposals@deedavis.biz", styles['Normal']))
    story.append(Paragraph("www.deedavis.biz", styles['Normal']))
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph("CAGE Code: 8UMX3", styles['Normal']))
    
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("_" * 80, centered_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Confidentiality notice
    conf_style = ParagraphStyle(
        'Confidential',
        parent=styles['Normal'],
        fontSize=9,
        alignment=TA_CENTER,
        textColor=colors.red
    )
    story.append(Paragraph("<b>PROPRIETARY & CONFIDENTIAL</b>", conf_style))
    story.append(Paragraph("This RFQ contains proprietary information of DEE DAVIS INC", conf_style))
    story.append(Paragraph("Not for redistribution without written consent", conf_style))
    
    story.append(PageBreak())
    
    # ========================================================================
    # SECTION 1: INTRODUCTION
    # ========================================================================
    
    story.append(Paragraph("SECTION 1: INTRODUCTION & OVERVIEW", heading1_style))
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("<b>1.1 ABOUT DEE DAVIS INC</b>", heading2_style))
    
    intro_text = """
    DEE DAVIS INC is a federally certified Woman-Owned Small Business (WOSB) and Economically 
    Disadvantaged Woman-Owned Small Business (EDWOSB) prime contractor headquartered in Troy, Michigan.
    <br/><br/>
    <b>Company Overview:</b><br/>
    Founded in 2018, DEE DAVIS INC has established itself as a reliable prime contractor serving 
    federal, state, and local government agencies, as well as commercial clients throughout the 
    United States. Our business model emphasizes strategic partnerships with qualified subcontractors 
    to deliver comprehensive solutions across multiple sectors including construction, professional 
    services, facilities management, and supply chain management.
    <br/><br/>
    <b>Federal Certifications & Registrations:</b><br/>
    • EDWOSB Certified - U.S. Small Business Administration<br/>
    • WOSB Certified - U.S. Small Business Administration<br/>
    • SAM.gov Active Registration - Verified Annually<br/>
    • CAGE Code: 8UMX3<br/>
    • UEI: HJB4KNYJVGZ1<br/>
    <br/>
    <b>NAICS Codes:</b> 236220, 238910, 541330, 561210, 561720, 562910, 811310, and others<br/>
    <br/>
    <b>Core Competencies:</b><br/>
    DEE DAVIS INC specializes in serving as a prime contractor for projects requiring specialized 
    expertise, equipment, or local knowledge. We maintain a national network of pre-qualified 
    subcontractors and vendors, enabling rapid mobilization and competitive pricing while maintaining 
    strict quality standards and compliance requirements.
    """
    story.append(Paragraph(intro_text, body_style))
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("<b>1.2 PURPOSE OF THIS RFQ</b>", heading2_style))
    
    purpose_text = f"""
    DEE DAVIS INC, acting as Prime Contractor, is seeking competitive quotes from qualified 
    subcontractors to <b>PERFORM {data.get('category', 'services')}</b> on a municipal client 
    project in <b>{data.get('sanitized_location', 'the region')}</b>.
    <br/><br/>
    <b>This is a service subcontracting opportunity. We're asking:</b><br/>
    • <b>What do you charge to perform this work?</b><br/>
    • Can you do the work safely, on time, and to specifications?<br/>
    • Do you have proper insurance and licensing?<br/>
    • Have you done similar work before?<br/>
    <br/>
    <b>This RFQ Process:</b><br/>
    • We provide the scope of work and project requirements<br/>
    • You quote your price to perform the service<br/>
    • We verify you meet minimum qualifications and insurance requirements<br/>
    • Lowest qualified bidder typically wins<br/>
    <br/>
    <b>This RFQ defines:</b><br/>
    • Detailed scope of work (what needs to be done)<br/>
    • Minimum contractor qualifications<br/>
    • Required insurance coverage (mandatory)<br/>
    • How to submit your quote<br/>
    • Subcontract terms and payment schedule<br/>
    • Confidentiality requirements<br/>
    <br/>
    <b>Client Confidentiality:</b> The end client identity is confidential per our prime contract. 
    The selected subcontractor will receive complete project details upon subcontract execution 
    and signing of non-disclosure agreement.
    """
    story.append(Paragraph(purpose_text, body_style))
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("<b>1.3 PROJECT OVERVIEW</b>", heading2_style))
    
    # Project details table
    project_data = [
        ['Project Name:', data.get('project_name', 'N/A')],
        ['Project Location:', data.get('sanitized_location', 'N/A')],
        ['Contract Type:', data.get('contract_type', 'As-Needed Services')],
        ['Contract Period:', data.get('contract_period', 'N/A')],
        ['Payment Terms:', 'Net 30 days from invoice'],
    ]
    
    project_table = Table(project_data, colWidths=[2*inch, 4*inch])
    project_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), FONT_BOLD),
        ('FONTNAME', (1, 0), (1, -1), FONT_NAME),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    story.append(project_table)
    story.append(Spacer(1, 0.2*inch))
    
    # Project description
    if data.get('scope_of_work'):
        story.append(Paragraph("<b>Project Description:</b>", body_style))
        story.append(Paragraph(data.get('scope_of_work', ''), body_style))
        story.append(Spacer(1, 0.1*inch))
    
    # Important note
    note_text = """
    <b>Note:</b> End client information is confidential per prime contract requirements. 
    The selected subcontractor will receive specific project details upon contract award.
    """
    story.append(Paragraph(note_text, body_style))
    
    story.append(PageBreak())
    
    # ========================================================================
    # SECTION 2: SCOPE OF WORK
    # ========================================================================
    
    story.append(Paragraph("SECTION 2: SCOPE OF WORK", heading1_style))
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("<b>2.1 GENERAL SCOPE & DELIVERABLES</b>", heading2_style))
    
    if data.get('scope_of_work'):
        story.append(Paragraph(data.get('scope_of_work'), body_style))
    else:
        story.append(Paragraph("Detailed scope of work to be provided.", body_style))
    
    story.append(Spacer(1, 0.2*inch))
    
    # Service locations
    if data.get('service_locations_count'):
        locations_text = f"""
        <b>Service Locations:</b> {data.get('service_locations_count')} separate locations<br/>
        Specific addresses, access instructions, and site-specific requirements will be provided 
        to the selected subcontractor upon contract execution. All locations are within the 
        geographic area specified in Section 1.3.
        """
        story.append(Paragraph(locations_text, body_style))
    
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("<b>2.2 PERFORMANCE STANDARDS & QUALITY CONTROL</b>", heading2_style))
    
    quality_text = """
    The selected subcontractor shall:<br/><br/>
    <b>Performance Requirements:</b><br/>
    • Comply with all applicable federal, state, and local regulations<br/>
    • Maintain industry best practices and safety standards<br/>
    • Provide qualified, trained personnel for all work performed<br/>
    • Utilize equipment and materials meeting or exceeding specifications<br/>
    • Complete work within specified timeframes and to stated quality standards<br/>
    <br/>
    <b>Quality Assurance:</b><br/>
    • Implement documented quality control procedures<br/>
    • Conduct self-inspections prior to final approval<br/>
    • Correct any deficiencies promptly at no additional cost<br/>
    • Maintain detailed records of work performed<br/>
    • Provide photographic documentation when requested<br/>
    <br/>
    <b>Project Management:</b><br/>
    • Designate a single point of contact for all project communications<br/>
    • Respond to inquiries within 24 business hours<br/>
    • Provide advance notice of scheduling and any potential delays<br/>
    • Coordinate with DEE DAVIS INC project management team<br/>
    • Submit progress reports and invoicing documentation as required<br/>
    """
    story.append(Paragraph(quality_text, body_style))
    
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("<b>2.3 COMPLIANCE & REGULATORY REQUIREMENTS</b>", heading2_style))
    
    compliance_text = """
    All work must comply with:<br/>
    • OSHA safety standards and regulations<br/>
    • Environmental Protection Agency (EPA) requirements<br/>
    • State and local building codes, permits, and ordinances<br/>
    • Industry-specific regulations and standards<br/>
    • DEE DAVIS INC safety and compliance policies<br/>
    • End client policies and procedures (as provided)<br/>
    <br/>
    <b>Safety Requirements:</b><br/>
    The subcontractor is solely responsible for workplace safety and must maintain a comprehensive 
    safety program including written safety plans, employee training records, and incident reporting 
    procedures. DEE DAVIS INC reserves the right to suspend work for any safety violations.
    """
    story.append(Paragraph(compliance_text, body_style))
    
    story.append(PageBreak())
    
    # ========================================================================
    # SECTION 3: MINIMUM QUALIFICATIONS & EXPERIENCE
    # ========================================================================
    
    story.append(Paragraph("SECTION 3: MINIMUM QUALIFICATIONS", heading1_style))
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("<b>3.1 MINIMUM REQUIREMENTS</b>", heading2_style))
    
    qualifications_text = """
    Basic requirements for subcontractors. If you meet these, your quote competes on price.<br/><br/>
    
    <b>REQUIREMENT #1: You're a Legitimate Contractor</b><br/>
    • Valid business license for this type of work<br/>
    • Can provide W-9 Form<br/>
    • Not debarred from government contracting<br/>
    • Any required trade-specific licenses or certifications<br/>
    <br/>
    <b>REQUIREMENT #2: You Have Required Insurance (MANDATORY - NON-NEGOTIABLE)</b><br/>
    • <b>Commercial General Liability:</b> $1M per occurrence / $2M aggregate minimum<br/>
    • <b>Workers' Compensation:</b> Required if you have employees<br/>
    • <b>Commercial Auto Liability:</b> Required if using vehicles for this work<br/>
    • <b>Must be able to add DEE DAVIS INC as Additional Insured</b><br/>
    • Provide current Certificate of Insurance with quote<br/>
    <br/>
    <b>REQUIREMENT #3: You Can Perform This Service</b><br/>
    • Have experience performing this type of work<br/>
    • Have necessary equipment, tools, and crew<br/>
    • Can meet the project timeline and requirements<br/>
    • Have capacity to take on this project<br/>
    <br/>
    <b>That's it.</b> Meet these three requirements and you're in the running. 
    Lowest qualified price typically wins.<br/>
    <br/>
    <b>⚠️ INSURANCE IS MANDATORY - No proper insurance = Automatic rejection, no exceptions</b>
    """
    story.append(Paragraph(qualifications_text, body_style))
    
    story.append(PageBreak())
    
    # ========================================================================
    # SECTION 4: EVALUATION CRITERIA & SELECTION PROCESS
    # ========================================================================
    
    story.append(Paragraph("SECTION 4: EVALUATION & AWARD", heading1_style))
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("<b>4.1 EVALUATION METHODOLOGY</b>", heading2_style))
    
    evaluation_text = """
    <b>Evaluation: Price-Driven with Qualification Check</b><br/><br/>
    
    This is primarily a price competition among qualified subcontractors:<br/>
    1. We verify you meet the 3 minimum requirements (Section 3.1)<br/>
    2. Among qualified bidders, <b>lowest price typically wins</b><br/>
    3. Quick reference checks on top 2-3 lowest bidders<br/>
    4. Award to lowest qualified responsive bidder<br/>
    <br/>
    <b>Scoring Methodology:</b><br/><br/>
    
    <b>PRICE COMPETITIVENESS: 60 points</b><br/>
    • Lowest qualified bidder gets 60 points<br/>
    • Other bidders scored proportionally<br/>
    • Price must be complete and reasonable<br/>
    <br/>
    <b>CAPABILITY & EXPERIENCE: 20 points</b><br/>
    • Demonstrated experience with similar work<br/>
    • Proper equipment, tools, and crew<br/>
    • References verify good performance<br/>
    • Can meet project timeline<br/>
    <br/>
    <b>COMPLIANCE & INSURANCE: 20 points</b><br/>
    • Insurance meets all minimum requirements<br/>
    • Can add DEE DAVIS INC as Additional Insured<br/>
    • W-9, business license, and trade licenses complete<br/>
    • No red flags or compliance issues<br/>
    <br/>
    <b>TOTAL: 100 points</b><br/>
    <br/>
    <b>Reality Check:</b> The lowest qualified bidder usually wins. We go to the next lowest if:<br/>
    • Insurance inadequate or missing (automatic rejection)<br/>
    • References reveal serious performance or safety issues<br/>
    • Can't meet timeline or project requirements<br/>
    • Pricing is incomplete or unreasonably low (red flag)<br/>
    • Licensing or business legitimacy concerns<br/>
    <br/>
    <b>Bottom Line: Best price wins among contractors who can safely perform the work with proper insurance.</b>
    """
    story.append(Paragraph(evaluation_text, body_style))
    
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("<b>4.2 SELECTION & AWARD PROCESS</b>", heading2_style))
    
    award_text = """
    <b>STREAMLINED SELECTION PROCESS (3-7 business days typical)</b><br/><br/>
    
    <b>Step 1: Threshold Screening (1-2 business days)</b><br/>
    • Verify insurance documentation meets minimums<br/>
    • Check business license and W-9 included<br/>
    • Confirm minimum experience requirements met<br/>
    • Eliminate non-responsive quotes (missing required docs)<br/>
    <br/>
    <b>Step 2: Price Evaluation & Reference Checks (2-3 business days)</b><br/>
    • Compare pricing from qualified bidders<br/>
    • Conduct quick reference checks on lowest 2-3 bidders<br/>
    • Verify pricing is complete and reasonable<br/>
    • May request pricing clarifications or corrections<br/>
    <br/>
    <b>Step 3: Award Decision (1-2 business days)</b><br/>
    • Select lowest qualified responsive bidder (typical)<br/>
    • OR select higher bidder if significant qualification concerns with lowest<br/>
    • Execute simple subcontract agreement<br/>
    • Issue Notice to Proceed<br/>
    <br/>
    <b>Typical Timeline: Award within 5-7 business days of quote due date</b><br/>
    <br/>
    <b>Important Notes:</b><br/>
    • This is a competitive price-driven RFQ - lowest qualified bidder typically wins<br/>
    • DEE DAVIS INC reserves right to reject any or all quotes<br/>
    • Award decision is final and not subject to protest or appeal<br/>
    • Only the awarded firm will be notified (unsuccessful bidders will not receive notification)<br/>
    • No debriefings, negotiations, or discussions with unsuccessful bidders<br/>
    """
    story.append(Paragraph(award_text, body_style))
    
    story.append(PageBreak())
    
    # ========================================================================
    # SECTION 5: SUBMISSION REQUIREMENTS
    # ========================================================================
    
    story.append(Paragraph("SECTION 5: SUBMISSION REQUIREMENTS", heading1_style))
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("<b>5.1 REQUIRED QUOTE COMPONENTS</b>", heading2_style))
    
    format_text = """
    This is a subcontracting opportunity. We need your best price to PERFORM this service, 
    along with proof you can do the work and have proper insurance.<br/><br/>
    
    <b>PART 1: YOUR SERVICE PRICE QUOTE (REQUIRED)</b><br/>
    What do you charge to perform this work?<br/>
    • <b>Labor pricing</b> (hourly rates, per-unit, or lump sum)<br/>
    • <b>Total project cost</b><br/>
    • Materials included (or list separately if not)<br/>
    • Timeline to complete the work<br/>
    • Price valid for 60 days minimum<br/>
    • Payment terms (if different from Net 30)<br/>
    • Any assumptions or exclusions<br/>
    <br/>
    <b>PART 2: COMPANY INFO & CAPABILITY (REQUIRED - 1-2 pages)</b><br/>
    • Business name, address, phone, email<br/>
    • Primary contact person and title<br/>
    • Years performing this type of work<br/>
    • <b>Brief description of how you'll perform this service</b> (3-5 sentences)<br/>
    • Equipment, tools, and crew you'll use<br/>
    • Relevant licenses, certifications, or trade qualifications<br/>
    • Can you meet the timeline and project requirements?<br/>
    <br/>
    <b>PART 3: INSURANCE & COMPLIANCE (REQUIRED - MANDATORY)</b><br/>
    • <b>Certificate of Insurance</b> (see Section 6.2 for minimum coverage)<br/>
    • <b>W-9 Form</b><br/>
    • <b>Business license</b> (valid for this type of work)<br/>
    • Confirm you can add DEE DAVIS INC as Additional Insured<br/>
    • Any trade-specific licenses or certifications<br/>
    <br/>
    <b>PART 4: EXPERIENCE & REFERENCES (HELPFUL - 1 page)</b><br/>
    Provide 1-2 recent similar projects:<br/>
    • Project description and scope<br/>
    • When completed (month/year)<br/>
    • Client contact (or "Government Client" if confidential)<br/>
    • Reference phone/email<br/>
    <br/>
    <b>WHAT WE'RE ASKING:</b><br/>
    • What do you charge to do this work? (Part 1)<br/>
    • Can you actually do it? (Part 2)<br/>
    • Do you have insurance? (Part 3 - mandatory)<br/>
    • Have you done this before? (Part 4 - helpful)<br/>
    <br/>
    <b>⚠️ QUOTES MISSING PRICING, BASIC CAPABILITY INFO, OR INSURANCE WILL BE REJECTED</b>
    """
    story.append(Paragraph(format_text, body_style))
    
    story.append(PageBreak())
    
    story.append(Paragraph("<b>5.2 SUBMISSION INSTRUCTIONS & DEADLINES</b>", heading2_style))
    
    submit_text = f"""
    <b>DUE DATE:</b> {quote_due or '(See above)'}<br/>
    <b>SUBMIT TO:</b> proposals@deedavis.biz<br/>
    <b>SUBJECT:</b> RFQ Response: {rfp_number} - [YOUR COMPANY NAME]<br/>
    <br/>
    <b>Format Requirements:</b><br/>
    • Submit as PDF (preferred) or Word document<br/>
    • File name: {rfp_number}_[COMPANY-NAME]_Quote.pdf<br/>
    • Maximum file size: 15 MB<br/>
    • Include all required attachments<br/>
    <br/>
    <b>LATE SUBMISSIONS WILL NOT BE ACCEPTED.</b><br/>
    <br/>
    <b>Questions and Clarifications:</b><br/>
    All questions must be submitted in writing to proposals@deedavis.biz<br/>
    Questions Due: {data.get('questions_due', '5 business days before proposal due date')}
    """
    story.append(Paragraph(submit_text, body_style))
    
    story.append(PageBreak())
    
    # ========================================================================
    # SECTION 6: CONTRACT TERMS & CONDITIONS
    # ========================================================================
    
    story.append(Paragraph("SECTION 6: CONTRACT TERMS & CONDITIONS", heading1_style))
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("<b>6.1 CONTRACT TYPE & PAYMENT TERMS</b>", heading2_style))
    
    payment_text = """
    <b>Payment Schedule:</b><br/>
    Payment terms are Net 30 days from DEE DAVIS INC's receipt and approval of properly submitted 
    invoices. All invoices must be submitted within 15 days of work completion and include:<br/>
    • Detailed description of work performed with dates<br/>
    • Supporting documentation (photos, signed completion forms, etc.)<br/>
    • Reference to RFQ number and purchase order number<br/>
    • Proper W-9 information and remittance address<br/>
    <br/>
    <b>Payment Method:</b> Payment will be made via company check or ACH transfer to subcontractor's 
    designated bank account. Subcontractor is responsible for providing accurate banking information.<br/>
    <br/>
    <b>Retainage:</b> DEE DAVIS INC may withhold up to 10% retainage pending final inspection and 
    approval of all work, to be released within 30 days of final acceptance.<br/>
    <br/>
    <b>Disputed Invoices:</b> In the event of invoice disputes, DEE DAVIS INC will pay undisputed 
    portions within the standard payment period and work to resolve disputes within 15 business days.
    """
    story.append(Paragraph(payment_text, body_style))
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("<b>6.2 MANDATORY INSURANCE REQUIREMENTS</b>", heading2_style))
    
    if data.get('insurance_requirements'):
        story.append(Paragraph(data.get('insurance_requirements'), body_style))
    else:
        insurance_text = """
        The selected subcontractor must procure and maintain, at its own expense, insurance coverage 
        meeting or exceeding the following minimum requirements. All insurance must be provided by 
        carriers with an A.M. Best rating of A- VII or better.<br/><br/>
        
        <b>1. Commercial General Liability (CGL) Insurance - REQUIRED</b><br/>
        • Minimum Coverage: $1,000,000 per occurrence / $2,000,000 aggregate<br/>
        • Coverage for bodily injury, property damage, and personal injury<br/>
        • Products/Completed Operations coverage included<br/>
        • Contractual Liability coverage included<br/>
        • <b>DEE DAVIS INC must be named as Additional Insured on primary, non-contributory basis</b><br/>
        • Waiver of subrogation in favor of DEE DAVIS INC required<br/>
        • 30-day notice of cancellation or material change required<br/>
        <br/>
        <b>2. Workers' Compensation & Employer's Liability - REQUIRED (if employees)</b><br/>
        • Statutory Workers' Compensation coverage per state law<br/>
        • Employer's Liability: $1,000,000 each accident / $1,000,000 disease each employee / 
        $1,000,000 disease policy limit<br/>
        • Waiver of subrogation in favor of DEE DAVIS INC required<br/>
        <br/>
        <b>3. Commercial Automobile Liability - REQUIRED (if vehicles used)</b><br/>
        • Minimum Coverage: $1,000,000 combined single limit<br/>
        • Coverage for owned, non-owned, and hired vehicles<br/>
        • DEE DAVIS INC named as Additional Insured<br/>
        <br/>
        <b>4. Umbrella/Excess Liability - RECOMMENDED</b><br/>
        • Recommended minimum: $2,000,000 per occurrence<br/>
        • Must provide excess coverage over primary policies listed above<br/>
        <br/>
        <b>5. Professional Liability/Errors & Omissions - IF APPLICABLE</b><br/>
        • Required for professional services: $1,000,000 per claim / $2,000,000 aggregate<br/>
        <br/>
        <b>6. Pollution Liability - IF APPLICABLE</b><br/>
        • Required if work involves hazardous materials or environmental exposure<br/>
        • Minimum: $1,000,000 per occurrence / $2,000,000 aggregate<br/>
        <br/>
        <b>Insurance Submission Requirements:</b><br/>
        • Certificate of Insurance showing all required coverage must be provided BEFORE contract execution<br/>
        • All policies must be current and remain in force for duration of contract<br/>
        • Renewal certificates must be provided 15 days prior to expiration<br/>
        • Deductibles and self-insured retentions must be disclosed and are subcontractor's sole responsibility<br/>
        • Any gaps in coverage must be disclosed in writing<br/>
        <br/>
        <b>⚠️ WORK MAY NOT COMMENCE UNTIL PROPER INSURANCE DOCUMENTATION IS RECEIVED AND APPROVED</b>
        """
        story.append(Paragraph(insurance_text, body_style))
    
    story.append(PageBreak())
    
    story.append(Paragraph("<b>6.3 INDEMNIFICATION & LIABILITY</b>", heading2_style))
    
    indemnity_text = """
    <b>Hold Harmless and Indemnification:</b><br/>
    To the fullest extent permitted by law, Subcontractor shall indemnify, defend, and hold harmless 
    DEE DAVIS INC, its officers, directors, employees, agents, and the end client from and against 
    any and all claims, damages, losses, liabilities, costs, and expenses (including reasonable 
    attorneys' fees) arising out of or resulting from:<br/>
    • Performance or non-performance of the subcontract work<br/>
    • Acts, errors, omissions, or negligence of Subcontractor or its employees, agents, or sub-subcontractors<br/>
    • Bodily injury, death, or property damage caused by Subcontractor<br/>
    • Violation of laws, regulations, or ordinances by Subcontractor<br/>
    • Claims of third parties relating to Subcontractor's work<br/>
    <br/>
    This indemnification obligation survives termination or completion of the contract.
    """
    story.append(Paragraph(indemnity_text, body_style))
    
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("<b>6.4 CONFIDENTIALITY & NON-CIRCUMVENTION</b>", heading2_style))
    
    confidentiality_text = """
    <b>CONFIDENTIAL INFORMATION & NON-DISCLOSURE:</b><br/><br/>
    Subcontractor acknowledges that during the course of this engagement, it may be provided with or 
    have access to confidential, proprietary, and sensitive information (collectively "Confidential Information") 
    including but not limited to:<br/>
    • End client name, identity, contact information, and organizational details<br/>
    • Project location addresses and site-specific information<br/>
    • DEE DAVIS INC pricing, profit margins, business strategies, and client relationships<br/>
    • Contract terms between DEE DAVIS INC and the end client<br/>
    • Technical specifications, drawings, plans, and proprietary methodologies<br/>
    • Any information marked or identified as confidential<br/>
    <br/>
    <b>Non-Disclosure Obligations - Subcontractor Agrees To:</b><br/>
    1. <b>Maintain Strict Confidentiality:</b> Hold all Confidential Information in the strictest 
    confidence and not disclose, publish, or disseminate such information to any third party without 
    DEE DAVIS INC's prior written consent.<br/>
    <br/>
    2. <b>Limited Use:</b> Use Confidential Information solely for the purpose of performing work 
    under this subcontract and for no other purpose whatsoever.<br/>
    <br/>
    3. <b>No Direct Contact:</b> NOT contact, communicate with, or solicit the end client directly 
    under any circumstances during or after the contract period without express written authorization 
    from DEE DAVIS INC.<br/>
    <br/>
    4. <b>No Marketing/References:</b> NOT use the end client's name, project details, or any 
    Confidential Information in marketing materials, proposals, website, or any public communications 
    without DEE DAVIS INC's prior written approval.<br/>
    <br/>
    5. <b>Protect Information:</b> Implement reasonable safeguards to protect Confidential Information 
    from unauthorized disclosure, including limiting access to employees with need-to-know.<br/>
    <br/>
    6. <b>Return Materials:</b> Upon completion or termination, immediately return or destroy all 
    documents, files, and materials containing Confidential Information.<br/>
    <br/>
    <b>NON-CIRCUMVENTION AGREEMENT:</b><br/>
    Subcontractor specifically agrees that it shall NOT, directly or indirectly:<br/>
    • Attempt to bypass, circumvent, or displace DEE DAVIS INC in any dealings with the end client<br/>
    • Solicit, contact, or accept work directly from the end client for a period of 3 years<br/>
    • Interfere with DEE DAVIS INC's relationship with the end client<br/>
    • Assist any third party in circumventing DEE DAVIS INC's role as prime contractor<br/>
    <br/>
    <b>Duration of Obligations:</b> These confidentiality and non-circumvention obligations survive 
    indefinitely after contract completion or termination.<br/>
    <br/>
    <b>REMEDIES FOR BREACH:</b><br/>
    Subcontractor acknowledges that breach of these obligations will cause irreparable harm to 
    DEE DAVIS INC for which monetary damages are inadequate. Therefore, in addition to any other 
    remedies available at law or equity, DEE DAVIS INC shall be entitled to:<br/>
    <br/>
    1. <b>Immediate Injunctive Relief:</b> Seek immediate injunctive or equitable relief without 
    posting bond to prevent or stop any breach or threatened breach.<br/>
    <br/>
    2. <b>Contract Termination for Cause:</b> Immediately terminate the subcontract without notice 
    and without liability for further payment.<br/>
    <br/>
    3. <b>Withholding of Payment:</b> Withhold and offset any unpaid amounts against damages.<br/>
    <br/>
    4. <b>Monetary Damages:</b> Recover all actual, consequential, and punitive damages resulting 
    from the breach including:<br/>
    • Loss of contract value and profit margins<br/>
    • Loss of client relationship and future business<br/>
    • Costs of investigation and enforcement<br/>
    • Attorneys' fees and litigation costs<br/>
    <br/>
    5. <b>Liquidated Damages:</b> Subcontractor shall pay liquidated damages of $50,000 for each 
    instance of unauthorized client contact or disclosure of Confidential Information, without 
    prejudice to DEE DAVIS INC's right to seek additional damages.<br/>
    <br/>
    6. <b>Disgorgement of Profits:</b> Forfeit and pay over to DEE DAVIS INC any profits, fees, or 
    compensation received as a result of unauthorized dealings with the end client.<br/>
    <br/>
    <b>⚠️ SUBCONTRACTOR ACKNOWLEDGES READING, UNDERSTANDING, AND AGREEING TO BE LEGALLY BOUND BY 
    THESE CONFIDENTIALITY AND NON-CIRCUMVENTION TERMS</b>
    """
    story.append(Paragraph(confidentiality_text, body_style))
    
    story.append(PageBreak())
    
    story.append(Paragraph("<b>6.5 ADDITIONAL CONTRACT TERMS</b>", heading2_style))
    
    additional_terms = """
    <b>Termination:</b> DEE DAVIS INC may terminate this subcontract for convenience with 15 days 
    written notice, or immediately for cause (including poor performance, safety violations, or 
    breach of terms). Subcontractor will be compensated only for work satisfactorily completed 
    prior to termination.<br/>
    <br/>
    <b>Warranties:</b> Subcontractor warrants all work will be performed in a professional, 
    workmanlike manner using qualified personnel and meeting all applicable standards. Subcontractor 
    warrants all materials and equipment will be new, of good quality, and fit for intended purpose. 
    Warranty period minimum 1 year from completion.<br/>
    <br/>
    <b>Independent Contractor:</b> Subcontractor is an independent contractor, not an employee or 
    agent of DEE DAVIS INC. Subcontractor is solely responsible for all taxes, insurance, and 
    employee matters.<br/>
    <br/>
    <b>Compliance with Laws:</b> Subcontractor shall comply with all federal, state, and local laws, 
    regulations, ordinances, and codes applicable to the work.<br/>
    <br/>
    <b>Assignment:</b> Subcontractor may not assign, transfer, or delegate this contract or any 
    rights hereunder without DEE DAVIS INC's prior written consent.<br/>
    <br/>
    <b>Dispute Resolution:</b> Any disputes shall be resolved first through good faith negotiation. 
    If unsuccessful, disputes shall be submitted to binding arbitration in Oakland County, Michigan 
    under AAA Commercial Arbitration Rules.<br/>
    <br/>
    <b>Governing Law:</b> This RFQ and any resulting subcontract shall be governed by the laws of 
    the State of Michigan without regard to conflicts of law principles.<br/>
    <br/>
    <b>Entire Agreement:</b> The executed subcontract, including this RFQ and Subcontractor's 
    quote, constitutes the entire agreement and supersedes all prior negotiations, representations, 
    and agreements.
    """
    story.append(Paragraph(additional_terms, body_style))
    
    story.append(PageBreak())
    
    # ========================================================================
    # FOOTER
    # ========================================================================
    
    footer_text = """
    <br/><br/><br/>
    ________________________________________________________________________<br/>
    DEE DAVIS INC | Troy, MI 48084 | 248-376-4550 | deedavis.biz<br/>
    proposals@deedavis.biz | CAGE Code: 8UMX3<br/>
    Certified EDWOSB/WOSB | PROPRIETARY & CONFIDENTIAL<br/>
    """
    story.append(Paragraph(footer_text, ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, alignment=TA_CENTER)))
    
    # Build PDF
    doc.build(story)
    
    # Add watermark
    add_watermark_to_pdf(temp_pdf, final_pdf)
    
    # Clean up temp file
    if os.path.exists(temp_pdf):
        os.remove(temp_pdf)
    
    return final_pdf


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.route('/api/rfp/generate', methods=['POST'])
def generate_rfp():
    """
    Generate professional DDI-branded supplier RFP as PDF
    
    Expected JSON:
    {
        "project_name": "Municipal Parks Pressure Washing",
        "category": "Pressure Washing",
        "sanitized_location": "Oakland County, Michigan",
        "scope_of_work": "Hot water pressure washing...",
        "contract_value_min": 8000,
        "contract_value_max": 15000,
        "quote_due_date": "2026-02-10T17:00:00",
        "contract_period": "March 2026 - December 2026",
        "service_locations_count": 20,
        "insurance_requirements": "GL $1M...",
        "buyer_name": "City of Auburn Hills" (confidential, not in PDF),
        "buyer_rfp_number": "RFQ-01-30-2026-001" (confidential)
    }
    """
    try:
        data = request.json
        
        # Generate DDI RFP number
        ddi_rfp_number = generate_rfp_number(data.get('category', 'General Services'))
        
        print(f"Generating RFP: {ddi_rfp_number}")
        
        # Save to database (if Airtable available)
        try:
            rfp_record = save_rfp_to_database(ddi_rfp_number, data)
            record_id = rfp_record['id']
        except Exception as e:
            print(f"Airtable save failed: {e}")
            record_id = None
        
        # Generate PDF
        pdf_path = create_rfp_pdf(ddi_rfp_number, data)
        
        return jsonify({
            'success': True,
            'rfp_number': ddi_rfp_number,
            'pdf_path': pdf_path,
            'record_id': record_id,
            'message': f'RFP {ddi_rfp_number} generated successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/rfp/view/<rfp_number>', methods=['GET'])
def view_rfp(rfp_number):
    """View RFP PDF in browser (inline)"""
    try:
        pdf_path = f'generated_rfps/RFP_{rfp_number}.pdf'
        
        if not os.path.exists(pdf_path):
            return jsonify({
                'success': False,
                'error': 'RFP not found'
            }), 404
        
        # Display inline in browser for review
        return send_file(
            pdf_path,
            mimetype='application/pdf',
            as_attachment=False,  # Shows in browser (inline)
            download_name=f'RFP_{rfp_number}.pdf'
        )
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/rfp/download/<rfp_number>', methods=['GET'])
def download_rfp(rfp_number):
    """Download RFP PDF (forces save dialog)"""
    try:
        pdf_path = f'generated_rfps/RFP_{rfp_number}.pdf'
        
        if not os.path.exists(pdf_path):
            return jsonify({
                'success': False,
                'error': 'RFP not found'
            }), 404
        
        # Force download (for when user explicitly wants to save)
        return send_file(
            pdf_path,
            mimetype='application/pdf',
            as_attachment=True,  # Forces download dialog
            download_name=f'RFP_{rfp_number}.pdf'
        )
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/rfp/list', methods=['GET'])
def list_rfps():
    """Get all generated RFPs"""
    try:
        table = airtable_api.table(BASE_ID, 'SUPPLIER_RFPS')
        records = table.all()
        
        rfps = []
        for r in records:
            rfp_data = {
                'id': r['id'],
                **r['fields']
            }
            rfps.append(rfp_data)
        
        return jsonify({
            'success': True,
            'rfps': rfps,
            'count': len(rfps)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/rfp/test', methods=['POST'])
def test_rfp():
    """Test endpoint - generate Auburn Hills pressure washing RFP"""
    
    test_data = {
        "project_name": "Municipal Parks Pressure Washing Services",
        "category": "Pressure Washing",
        "sanitized_location": "Oakland County, Michigan",
        "scope_of_work": """
        DEE DAVIS INC has been contracted to provide hot water pressure washing services 
        for park structures, playground equipment, picnic shelters, restroom facilities, 
        and other municipal assets at 20 locations throughout Oakland County.
        <br/><br/>
        Services will be requested on an as-needed basis. The selected subcontractor must 
        respond within 1 week of service request and provide high-quality hot water pressure 
        washing per specifications.
        <br/><br/>
        <b>Key Requirements:</b><br/>
        • HOT WATER pressure washing REQUIRED (minimum 200°F)<br/>
        • All equipment, water supply, chemicals, and supplies provided by subcontractor<br/>
        • 1-week turnaround from service request to completion<br/>
        • Before and after photos required for each service call<br/>
        • Eco-friendly cleaning products required<br/>
        """,
        "contract_value_min": 8000,
        "contract_value_max": 15000,
        "quote_due_date": "2026-02-10T17:00:00",
        "contract_period": "March 2026 - December 2026 (10 months)",
        "contract_type": "As-Needed Services",
        "contract_start": "March 2026",
        "service_locations_count": 20,
        "questions_due": "February 7, 2026 at 5:00 PM EST",
        "insurance_requirements": """
        <b>1. Commercial General Liability Insurance</b><br/>
        Minimum Coverage: $1,000,000 per occurrence / $2,000,000 aggregate<br/>
        <br/>
        <b>2. Workers Compensation Insurance</b><br/>
        Required if subcontractor has employees (per Michigan law)<br/>
        <br/>
        <b>3. Commercial Automobile Liability</b><br/>
        Minimum Coverage: $1,000,000 combined single limit<br/>
        <br/>
        <b>⚠️ DEE DAVIS INC MUST BE NAMED AS ADDITIONAL INSURED on GL and Auto policies</b>
        """,
        "buyer_name": "City of Auburn Hills",
        "buyer_rfp_number": "RFQ-01-30-2026-001"
    }
    
    return generate_rfp_from_data(test_data)


def generate_rfp_from_data(data):
    """Internal function to generate RFP"""
    try:
        ddi_rfp_number = generate_rfp_number(data.get('category', 'General Services'))
        
        print(f"Generating test RFP: {ddi_rfp_number}")
        
        # Generate PDF
        pdf_path = create_rfp_pdf(ddi_rfp_number, data)
        
        # Save to database (optional, may fail if table doesn't exist)
        try:
            rfp_record = save_rfp_to_database(ddi_rfp_number, data)
            record_id = rfp_record['id']
        except:
            record_id = None
        
        return jsonify({
            'success': True,
            'rfp_number': ddi_rfp_number,
            'pdf_path': pdf_path,
            'record_id': record_id,
            'message': f'Test RFP {ddi_rfp_number} generated successfully!',
            'download_url': f'/api/rfp/download/{ddi_rfp_number}'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


def save_rfp_to_database(ddi_rfp_number, data):
    """Save RFP to Airtable SUPPLIER_RFPS table"""
    table = airtable_api.table(BASE_ID, 'SUPPLIER_RFPS')
    
    record = table.create({
        'ddi_rfp_number': ddi_rfp_number,
        'project_name': data.get('project_name'),
        'category': data.get('category'),
        'sanitized_location': data.get('sanitized_location'),
        'scope_of_work': data.get('scope_of_work'),
        'contract_value_min': data.get('contract_value_min'),
        'contract_value_max': data.get('contract_value_max'),
        'quote_due_date': data.get('quote_due_date'),
        'contract_period': data.get('contract_period'),
        'service_locations_count': data.get('service_locations_count'),
        'insurance_requirements': data.get('insurance_requirements'),
        'status': 'draft',
        'pdf_generated_path': f'generated_rfps/RFP_{ddi_rfp_number}.pdf',
    })
    
    return record


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'service': 'RFP Generator API',
        'version': '1.0.0',
        'airtable_connected': AIRTABLE_API_KEY is not None
    })


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    print("=" * 60)
    print("NEXUS RFP GENERATOR API")
    print("=" * 60)
    print(f"Airtable: {'✅ Connected' if AIRTABLE_API_KEY else '❌ Not configured'}")
    print(f"Output Directory: generated_rfps/")
    print()
    print("Starting server on http://localhost:5002")
    print()
    print("Test the API:")
    print("  curl -X POST http://localhost:5002/api/rfp/test")
    print()
    print("=" * 60)
    
    app.run(debug=True, port=5002, host='0.0.0.0')
