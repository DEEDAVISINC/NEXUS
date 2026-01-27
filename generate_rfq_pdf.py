#!/usr/bin/env python3
"""
Generate PDF from RFQ config using wkhtmltopdf
Falls back to simple text PDF if wkhtmltopdf not available
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
    """Generate simple PDF using reportlab as fallback"""
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_CENTER, TA_LEFT
        from reportlab.pdfgen import canvas
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
    except ImportError:
        print("❌ Neither wkhtmltopdf nor reportlab available")
        print("   Install one of:")
        print("   - brew install wkhtmltopdf")
        print("   - pip install reportlab")
        return False
    
    # Try to register Avenir font (macOS system font)
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
                break
    except Exception as e:
        # If Avenir fails, just use Helvetica
        pass
    
    # Get company name and logo for watermark
    company_name = config['company']['name']
    
    # Check for logo file
    logo_path = None
    possible_logos = [
        'logo.png',
        'photos_and_videos/deedavisinclogo.png',
        'photos_and_videos/logo.png'
    ]
    for path in possible_logos:
        if os.path.exists(path):
            logo_path = path
            break
    
    # Custom canvas with watermark
    class WatermarkedCanvas(canvas.Canvas):
        def __init__(self, *args, **kwargs):
            canvas.Canvas.__init__(self, *args, **kwargs)
            self._watermark_text = company_name
            self._watermark_font = font_bold
            self._logo_path = logo_path
        
        def showPage(self):
            # Draw watermark before showing page
            self.saveState()
            
            if self._logo_path:
                # Draw logo as watermark
                try:
                    # Center and rotate logo
                    self.translate(4.25*inch, 5.5*inch)  # Center of page
                    self.rotate(45)  # Diagonal
                    
                    # Draw logo with transparency effect
                    self.setFillAlpha(0.15)  # 15% opacity
                    
                    # Draw image - size 3x3 inches, centered
                    self.drawImage(self._logo_path, -1.5*inch, -1.5*inch, 
                                  width=3*inch, height=3*inch, 
                                  mask='auto', preserveAspectRatio=True)
                except:
                    # If logo fails, fall back to text
                    pass
            else:
                # Fall back to text watermark if no logo
                self.setFillGray(0.65)  # Medium gray
                self.setFont(self._watermark_font, 60)
                self.translate(4.25*inch, 5.5*inch)
                self.rotate(45)
                text_width = self.stringWidth(self._watermark_text, self._watermark_font, 60)
                self.drawString(-text_width/2, 0, self._watermark_text)
            
            self.restoreState()
            
            # Show the page
            canvas.Canvas.showPage(self)
    
    doc = SimpleDocTemplate(output_file, pagesize=letter, canvasmaker=WatermarkedCanvas)
    story = []
    styles = getSampleStyleSheet()
    
    # Custom styles with Avenir font
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontName=font_bold,
        fontSize=24,
        textColor=colors.HexColor('#1e3a8a'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontName=font_bold,
        fontSize=16,
        textColor=colors.HexColor('#1e3a8a'),
        spaceAfter=12,
        spaceBefore=20
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=10
    )
    
    # Title
    c = config['company']
    rfq = config['rfq_details']
    
    story.append(Paragraph(c['name'], title_style))
    subtitle_style = ParagraphStyle('Subtitle', parent=styles['Heading2'], fontName=font_name)
    story.append(Paragraph("Request for Quote", subtitle_style))
    story.append(Spacer(1, 0.3*inch))
    
    # RFQ Details
    story.append(Paragraph(rfq['title'], heading_style))
    
    details_data = [
        ['RFQ Number:', rfq['rfq_number']],
        ['Issue Date:', rfq['issue_date']],
        ['Due Date:', f"{rfq['due_date']} at {rfq['due_time']}"],
        ['Contract Period:', rfq['contract_period']]
    ]
    
    details_table = Table(details_data, colWidths=[2*inch, 4*inch])
    details_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), font_bold),
        ('FONTNAME', (1, 0), (1, -1), font_name),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(details_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Introduction
    story.append(Paragraph("INTRODUCTION", heading_style))
    story.append(Paragraph(config['introduction'], normal_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Items
    story.append(Paragraph("ITEMS REQUESTED", heading_style))
    
    items_data = [['Item', 'Description', 'Specifications', 'Qty']]
    for item in config['items']:
        items_data.append([
            item['item_number'],
            item['description'],
            item['specifications'],
            item['estimated_quantity']
        ])
    
    items_table = Table(items_data, colWidths=[0.5*inch, 2*inch, 2.5*inch, 1*inch])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a8a')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), font_bold),
        ('FONTNAME', (0, 1), (-1, -1), font_name),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')]),
    ]))
    story.append(items_table)
    story.append(Spacer(1, 0.2*inch))
    
    # Contact
    story.append(Paragraph("CONTACT INFORMATION", heading_style))
    contact_text = f"{c['contact_person']}<br/>{c['email']} | {c['phone']}<br/>{c['website']}"
    story.append(Paragraph(contact_text, normal_style))
    
    doc.build(story)
    return True


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 generate_rfq_pdf.py <config.json>")
        sys.exit(1)
    
    config_file = sys.argv[1]
    
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    html_file = config_file.replace('_config.json', '.html')
    output_file = config_file.replace('_config.json', '.pdf')
    
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
