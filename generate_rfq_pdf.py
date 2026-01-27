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
    
    # Check for logo file (prefer watermark version)
    logo_path = None
    possible_logos = [
        'logo_watermark.png',  # Pre-lightened watermark version (preferred)
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
            # CRITICAL: Draw watermark FIRST, before page content
            self.saveState()
            
            if self._logo_path and os.path.exists(self._logo_path):
                # Draw logo as watermark
                try:
                    # Center and rotate logo
                    self.translate(4.25*inch, 5.5*inch)  # Center of page
                    self.rotate(45)  # Diagonal
                    
                    # Draw image - size 4x4 inches (watermark version already has opacity)
                    # mask='auto' makes white backgrounds transparent
                    self.drawImage(self._logo_path, -2*inch, -2*inch, 
                                  width=4*inch, height=4*inch, 
                                  mask='auto', preserveAspectRatio=True)
                    
                except Exception as e:
                    # If logo fails, fall back to text
                    import traceback
                    print(f"Logo watermark error: {e}")
                    traceback.print_exc()
                    self.setFillGray(0.65)
                    self.setFont(self._watermark_font, 60)
                    text_width = self.stringWidth(self._watermark_text, self._watermark_font, 60)
                    self.drawString(-text_width/2, 0, self._watermark_text)
            else:
                # Fall back to text watermark if no logo
                print(f"Logo not found at: {self._logo_path}, using text watermark")
                self.setFillGray(0.65)  # Medium gray
                self.setFont(self._watermark_font, 60)
                self.translate(4.25*inch, 5.5*inch)
                self.rotate(45)
                text_width = self.stringWidth(self._watermark_text, self._watermark_font, 60)
                self.drawString(-text_width/2, 0, self._watermark_text)
            
            self.restoreState()
            
            # THEN show the page (this renders content on top)
            canvas.Canvas.showPage(self)
    
    # Create a function to draw watermark on first page callback
    def add_watermark(canvas_obj, doc_obj):
        """Add watermark to each page"""
        canvas_obj.saveState()
        
        if logo_path and os.path.exists(logo_path):
            try:
                # Draw logo near top of page
                # Position: centered horizontally, near top (letter = 11" tall)
                canvas_obj.drawImage(logo_path, 2.25*inch, 6.5*inch, 
                                   width=4*inch, height=4*inch, 
                                   mask='auto', preserveAspectRatio=True)
                
                # Draw logo near bottom of page
                # Position: centered horizontally, near bottom
                canvas_obj.drawImage(logo_path, 2.25*inch, 1*inch, 
                                   width=4*inch, height=4*inch, 
                                   mask='auto', preserveAspectRatio=True)
            except Exception as e:
                print(f"Watermark error: {e}")
        
        canvas_obj.restoreState()
    
    doc = SimpleDocTemplate(output_file, pagesize=letter)
    doc.canvasmaker = WatermarkedCanvas  # Still set it but also use onFirstPage
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
    
    items_data = [['#', 'Description', 'Specifications', 'Qty', 'Unit', 'Price/Unit', 'Total Price']]
    for item in config['items']:
        items_data.append([
            item['item_number'],
            item['description'],
            item['specifications'],
            item['estimated_quantity'],
            item.get('unit', 'unit'),
            '',  # Blank for supplier to fill in
            ''   # Blank for supplier to fill in
        ])
    
    # Adjusted column widths - made Specifications wider (2 inches instead of 1.5)
    items_table = Table(items_data, colWidths=[0.3*inch, 1.3*inch, 2*inch, 0.5*inch, 0.7*inch, 0.7*inch, 0.9*inch])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a8a')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),  # Center item numbers
        ('ALIGN', (3, 0), (3, -1), 'CENTER'),  # Center quantities
        ('ALIGN', (4, 0), (4, -1), 'CENTER'),  # Center units
        ('ALIGN', (5, 0), (-1, -1), 'RIGHT'),  # Right-align price columns
        ('ALIGN', (1, 0), (2, -1), 'LEFT'),    # Left-align descriptions and specs
        ('FONTNAME', (0, 0), (-1, 0), font_bold),
        ('FONTNAME', (0, 1), (-1, -1), font_name),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')]),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(items_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Quote Submission Requirements
    story.append(Paragraph("QUOTE SUBMISSION REQUIREMENTS", heading_style))
    
    requirements_text = f"""
    <b>Quote Deadline:</b> {rfq['due_date']} at {rfq['due_time']}<br/>
    <br/>
    <b>Delivery Location:</b> Southeast Michigan (specific address provided upon award)<br/>
    <br/>
    <b>Delivery Terms:</b> Prices must include delivery to specified location. Within 2 business days of order required.<br/>
    <br/>
    <b>Payment Terms:</b> Net 30 days preferred (specify your standard terms)<br/>
    <br/>
    <b>Quote Validity:</b> Quote must remain valid through February 4, 2026<br/>
    <br/>
    <b>Required Information in Your Quote:</b><br/>
    • Price per unit for each item (delivered)<br/>
    • Total estimated annual cost<br/>
    • Delivery lead time<br/>
    • Payment terms<br/>
    • Minimum order quantities (if applicable)<br/>
    • Any volume discounts available<br/>
    <br/>
    <b>Submit Quote To:</b><br/>
    Email: {c['email']}<br/>
    Phone: {c['phone']}<br/>
    <br/>
    <b>Questions?</b> Contact {c['contact_person']} at {c['phone']} or {c['email']}
    """
    
    requirements_style = ParagraphStyle(
        'Requirements',
        parent=normal_style,
        fontSize=9,
        leading=12,
        spaceAfter=6
    )
    
    story.append(Paragraph(requirements_text, requirements_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Footer note
    footer_style = ParagraphStyle(
        'Footer',
        parent=normal_style,
        fontSize=8,
        textColor=colors.HexColor('#6b7280'),
        alignment=TA_CENTER
    )
    
    story.append(Paragraph(
        f"<b>{c['name']}</b> • {c['address']} • {c['phone']} • {c['email']} • {c['website']}", 
        footer_style
    ))
    
    # Build with watermark on all pages
    doc.build(story, onFirstPage=add_watermark, onLaterPages=add_watermark)
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
