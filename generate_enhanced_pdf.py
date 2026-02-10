#!/usr/bin/env python3
"""
Generate enhanced PDF from capability statement config
Uses wkhtmltopdf for best results, falls back to reportlab
"""

import json
import sys
import subprocess
import os


def generate_pdf_wkhtmltopdf(html_file, output_file):
    """Generate PDF using wkhtmltopdf"""
    try:
        subprocess.run([
            'wkhtmltopdf',
            '--page-size', 'Letter',
            '--margin-top', '0',
            '--margin-bottom', '0',
            '--margin-left', '0',
            '--margin-right', '0',
            '--enable-local-file-access',
            html_file,
            output_file
        ], check=True, capture_output=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def generate_pdf_reportlab(config, output_file):
    """Generate PDF using reportlab as fallback"""
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_CENTER, TA_LEFT
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
    except ImportError:
        print("❌ Neither wkhtmltopdf nor reportlab available")
        print("   Install one of:")
        print("   - brew install wkhtmltopdf")
        print("   - pip install reportlab")
        return False
    
    # Register Avenir font (macOS system font)
    font_name = "Helvetica"  # Default fallback
    font_bold = "Helvetica-Bold"
    
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
                font_name = "Avenir"
                font_bold = "Avenir-Bold"
                print(f"✓ Registered Avenir font from {path}")
                break
    except Exception as e:
        # If Avenir fails, just use Helvetica
        print(f"⚠ Could not register Avenir font, using Helvetica: {e}")
    
    doc = SimpleDocTemplate(output_file, pagesize=letter,
                           topMargin=0.5*inch, bottomMargin=0.5*inch)
    story = []
    styles = getSampleStyleSheet()
    
    # Custom styles with Avenir
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=28,
        textColor=colors.HexColor('#1e3a8a'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName=font_bold
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=18,
        textColor=colors.HexColor('#1e3a8a'),
        spaceAfter=12,
        spaceBefore=20,
        fontName=font_bold,
        borderWidth=0,
        borderColor=colors.HexColor('#d97706'),
        borderPadding=5
    )
    
    # Title
    c = config['company']
    rfq = config['rfq_details']
    
    story.append(Paragraph(c['name'], title_style))
    story.append(Paragraph("Capability Statement", styles['Heading2']))
    story.append(Spacer(1, 0.3*inch))
    
    # Client/RFQ Info
    client_data = [
        ['Client:', rfq['client_name']],
        ['RFQ Number:', rfq['rfq_number']],
        ['Date:', rfq['date']]
    ]
    
    client_table = Table(client_data, colWidths=[1.5*inch, 4*inch])
    client_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), font_bold),
        ('FONTNAME', (1, 0), (1, -1), font_name),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f0f0f0')),
    ]))
    story.append(client_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Company Details
    details_data = [
        ['CAGE Code:', c['cage_code'], 'UEI:', c['uei']],
        ['DUNS:', c['duns'], 'Tax ID:', c['tax_id']]
    ]
    
    details_table = Table(details_data, colWidths=[1.2*inch, 2*inch, 1*inch, 2*inch])
    details_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), font_bold),
        ('FONTNAME', (1, 0), (1, -1), font_name),
        ('FONTNAME', (2, 0), (2, -1), font_bold),
        ('FONTNAME', (3, 0), (3, -1), font_name),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(details_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Company Overview
    story.append(Paragraph("COMPANY OVERVIEW", heading_style))
    story.append(Paragraph(config['company_overview'], styles['Normal']))
    story.append(Spacer(1, 0.2*inch))
    
    # Core Competencies
    story.append(Paragraph("CORE COMPETENCIES", heading_style))
    for comp in config['core_competencies']:
        story.append(Paragraph(f"• {comp}", styles['Normal']))
    story.append(Spacer(1, 0.2*inch))
    
    # Differentiators
    story.append(Paragraph("WHAT SETS US APART", heading_style))
    for diff in config['differentiators']:
        story.append(Paragraph(f"⭐ {diff}", styles['Normal']))
        story.append(Spacer(1, 0.1*inch))
    
    # Certifications
    story.append(Paragraph("CERTIFICATIONS", heading_style))
    for cert in config['certifications']:
        story.append(Paragraph(f"<b>{cert['name']}</b> - {cert['description']}", styles['Normal']))
        story.append(Spacer(1, 0.05*inch))
    
    story.append(Spacer(1, 0.3*inch))
    
    # Contact
    story.append(Paragraph("CONTACT INFORMATION", heading_style))
    contact_text = f"{c['address']}<br/>{c['phone']} | {c['email']}<br/>{c['website']}"
    story.append(Paragraph(contact_text, styles['Normal']))
    
    doc.build(story)
    return True


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 generate_enhanced_pdf.py <config.json>")
        sys.exit(1)
    
    config_file = sys.argv[1]
    
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    html_file = config_file.replace('_config.json', '.html')
    output_file = config_file.replace('_config.json', '_enhanced.pdf')
    
    # Try wkhtmltopdf first (better quality)
    if os.path.exists(html_file):
        if generate_pdf_wkhtmltopdf(html_file, output_file):
            print(f"✓ Generated: {output_file}")
            return
    
    # Fallback to reportlab
    if generate_pdf_reportlab(config, output_file):
        print(f"✓ Generated: {output_file} (using reportlab)")
    else:
        print(f"❌ Could not generate PDF")
        print(f"   HTML available at: {html_file}")


if __name__ == "__main__":
    main()
