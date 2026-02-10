#!/usr/bin/env python3
"""
Partnership Proposal Generator API
Generates professional partnership proposals for supplier diversity programs
Port: 5004
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
import os
import io

app = Flask(__name__)
CORS(app)

# Create output directory if it doesn't exist
os.makedirs('generated_partnerships', exist_ok=True)

def generate_partnership_proposal_pdf(data):
    """Generate a professional partnership proposal PDF"""
    
    # Extract form data
    partner_name = data.get('partnerName', 'Partner Company')
    proposal_type = data.get('proposalType', 'Supplier Diversity Partnership')
    services = data.get('servicesOffered', 'Mobile Notary Services, Courier Services')
    coverage = data.get('coverage', 'Nationwide (All 50 States)')
    certifications = data.get('certifications', 'EDWOSB')
    key_advantages = data.get('keyAdvantages', '')
    target_revenue = data.get('targetRevenue', '')
    timeline = data.get('implementationTimeline', '90 days')
    contact_email = data.get('contactEmail', '')
    contact_phone = data.get('contactPhone', '')
    
    # Generate filename
    date_str = datetime.now().strftime('%Y-%m-%d')
    filename = f"Partnership_Proposal_{partner_name.replace(' ', '_')}_{date_str}.pdf"
    filepath = os.path.join('generated_partnerships', filename)
    
    # Create PDF
    doc = SimpleDocTemplate(filepath, pagesize=letter,
                           rightMargin=72, leftMargin=72,
                           topMargin=72, bottomMargin=18)
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1a472a'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=14,
        textColor=colors.HexColor('#2d6a4f'),
        spaceAfter=20,
        alignment=TA_CENTER,
        fontName='Helvetica'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#1a472a'),
        spaceAfter=12,
        spaceBefore=16,
        fontName='Helvetica-Bold'
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=12,
        leading=16,
        fontName='Helvetica'
    )
    
    # Header
    elements.append(Paragraph("SUPPLIER DIVERSITY", subtitle_style))
    elements.append(Paragraph(f"{proposal_type}", title_style))
    elements.append(Paragraph(f"Dee Davis Inc. → {partner_name}", subtitle_style))
    elements.append(Spacer(1, 0.2 * inch))
    
    # Date and Company Info
    date_text = f"<b>Date:</b> {datetime.now().strftime('%B %d, %Y')}"
    company_text = "<b>Company:</b> Dee Davis Inc.<br/><b>Certification:</b> " + certifications
    elements.append(Paragraph(date_text, body_style))
    elements.append(Paragraph(company_text, body_style))
    elements.append(Spacer(1, 0.3 * inch))
    
    # Horizontal line
    line_table = Table([['_' * 100]], colWidths=[6.5 * inch])
    line_table.setStyle(TableStyle([
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.grey),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
    ]))
    elements.append(line_table)
    elements.append(Spacer(1, 0.2 * inch))
    
    # Executive Summary
    elements.append(Paragraph("Executive Summary", heading_style))
    summary_text = f"""
    Dee Davis Inc. is a certified {certifications} providing professional {services} to support 
    {partner_name}'s business operations and supplier diversity initiatives. We offer scalable, 
    technology-enabled solutions with {coverage.lower()} through our automated dispatch platform.
    """
    elements.append(Paragraph(summary_text, body_style))
    elements.append(Spacer(1, 0.2 * inch))
    
    # Why Partner with Dee Davis Inc.
    elements.append(Paragraph("Why Partner with Dee Davis Inc.?", heading_style))
    
    why_partner = [
        f"<b>✓ Certified {certifications}</b><br/>Supports your supplier diversity goals and demonstrates commitment to women-owned business support",
        f"<b>✓ {coverage}</b><br/>Not limited to single location - can handle volume fluctuations with consistent service quality",
        "<b>✓ Technology-Enabled Operations</b><br/>Automated dispatch platform (Snapdocs), real-time tracking, digital invoicing, 99.5%+ uptime",
        f"<b>✓ Dual Service Offering</b><br/>{services} in one vendor - streamlined procurement and single point of contact",
        "<b>✓ Quality Assurance</b><br/>All contractors background-checked, $1M+ E&O insurance, customer satisfaction monitoring",
        "<b>✓ Flexible Partnership Models</b><br/>Revenue-sharing, white-label, preferred vendor, or pilot program options"
    ]
    
    for item in why_partner:
        elements.append(Paragraph(item, body_style))
        elements.append(Spacer(1, 0.1 * inch))
    
    elements.append(Spacer(1, 0.2 * inch))
    
    # Key Advantages (specific to this partner)
    if key_advantages:
        elements.append(Paragraph(f"How This Benefits {partner_name}", heading_style))
        advantages_list = key_advantages.split('\n')
        for advantage in advantages_list:
            if advantage.strip():
                elements.append(Paragraph(f"<b>✓</b> {advantage.strip()}", body_style))
        elements.append(Spacer(1, 0.2 * inch))
    
    # Page break
    elements.append(PageBreak())
    
    # Service Overview
    elements.append(Paragraph("Service Overview", heading_style))
    
    services_text = """
    <b>Mobile Notary Services:</b><br/>
    General notarizations (acknowledgments, jurats, affidavits), loan signing services, 
    real estate transactions, corporate documents, power of attorney, healthcare directives, 
    apostille coordination, and witness services.<br/><br/>
    
    <b>Courier Services:</b><br/>
    Same-day delivery, rush services (1-3 hours), legal document filing, medical records 
    transport (HIPAA compliant), court document delivery, business-to-business deliveries, 
    and secure chain-of-custody handling.<br/><br/>
    
    <b>Coverage:</b> {coverage}<br/>
    <b>Response Time:</b> Under 2 hours (metro areas)<br/>
    <b>Availability:</b> Same-day, after-hours, and weekend service available
    """.format(coverage=coverage)
    
    elements.append(Paragraph(services_text, body_style))
    elements.append(Spacer(1, 0.3 * inch))
    
    # Partnership Models
    elements.append(Paragraph("Partnership Models", heading_style))
    
    models = [
        ("<b>Model 1: Referral Partnership</b>", 
         f"{partner_name} refers customers → Dee Davis Inc. provides service → Revenue share (70/30 split) → No infrastructure investment"),
        ("<b>Model 2: White-Label Service</b>", 
         f"Branded as '{partner_name} Mobile Notary' → We provide all operations → You market to customers → Negotiable revenue split"),
        ("<b>Model 3: Preferred Vendor</b>", 
         "Listed as approved vendor → Direct contracts with business customers → Volume pricing → Streamlined invoicing"),
        ("<b>Model 4: Pilot Program</b>", 
         "Test at 10-25 locations → 90-day trial → Measure ROI and satisfaction → Scale based on results")
    ]
    
    for model_title, model_desc in models:
        elements.append(Paragraph(model_title, body_style))
        elements.append(Paragraph(model_desc, body_style))
        elements.append(Spacer(1, 0.1 * inch))
    
    elements.append(Spacer(1, 0.2 * inch))
    
    # Implementation Timeline
    elements.append(Paragraph("Implementation Timeline", heading_style))
    timeline_text = f"""
    <b>Target Timeline:</b> {timeline}<br/><br/>
    
    <b>Phase 1 (Weeks 1-2):</b> Registration & Setup<br/>
    • Complete supplier diversity registration<br/>
    • Submit certification documentation<br/>
    • Complete vendor onboarding<br/><br/>
    
    <b>Phase 2 (Months 1-3):</b> Pilot Program<br/>
    • Launch at 10-25 pilot locations<br/>
    • Train location staff on referral process<br/>
    • Set up tracking and reporting<br/><br/>
    
    <b>Phase 3 (Month 4):</b> Evaluation<br/>
    • Review customer satisfaction metrics<br/>
    • Analyze transaction volume and revenue<br/>
    • Refine processes based on feedback<br/><br/>
    
    <b>Phase 4 (Months 5-12):</b> Expansion<br/>
    • Roll out to additional locations<br/>
    • Scale marketing efforts<br/>
    • Implement volume pricing
    """
    elements.append(Paragraph(timeline_text, body_style))
    elements.append(Spacer(1, 0.2 * inch))
    
    # Page break
    elements.append(PageBreak())
    
    # Financial Projections
    if target_revenue:
        elements.append(Paragraph("Financial Projections", heading_style))
        elements.append(Paragraph(target_revenue, body_style))
        elements.append(Spacer(1, 0.2 * inch))
    
    # Projected Revenue Table
    elements.append(Paragraph("Revenue Scenarios", heading_style))
    
    revenue_data = [
        ['Scenario', 'Locations', 'Transactions/Week', 'Monthly Revenue'],
        ['Conservative', '10', '50', '$8,000'],
        ['Moderate', '50', '250', '$40,000'],
        ['Optimistic', '200', '1,000', '$160,000']
    ]
    
    revenue_table = Table(revenue_data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
    revenue_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a472a')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey)
    ]))
    elements.append(revenue_table)
    elements.append(Spacer(1, 0.3 * inch))
    
    # Quality Assurance
    elements.append(Paragraph("Quality Assurance & Compliance", heading_style))
    qa_text = """
    <b>✓ Quality Commitments</b><br/>
    • 99%+ successful completion rate<br/>
    • Average response time under 2 hours (metro areas)<br/>
    • Customer satisfaction target: 4.5+ out of 5<br/>
    • All notaries background-checked and vetted<br/>
    • $1M+ E&O insurance coverage<br/><br/>
    
    <b>✓ Compliance Standards</b><br/>
    • State-specific notary law compliance<br/>
    • HIPAA compliance for medical documents<br/>
    • Secure document handling protocols<br/>
    • Data security and privacy protection<br/>
    • Regular audits and quality checks
    """
    elements.append(Paragraph(qa_text, body_style))
    elements.append(Spacer(1, 0.3 * inch))
    
    # Next Steps
    elements.append(Paragraph("Next Steps", heading_style))
    next_steps_text = f"""
    <b>1.</b> Review this proposal and assess strategic fit<br/>
    <b>2.</b> Schedule meeting with Dee Davis Inc. team<br/>
    <b>3.</b> Discuss partnership model and pilot program scope<br/>
    <b>4.</b> Negotiate terms and select pilot locations<br/>
    <b>5.</b> Execute agreement and launch pilot within {timeline}
    """
    elements.append(Paragraph(next_steps_text, body_style))
    elements.append(Spacer(1, 0.3 * inch))
    
    # Contact Information
    elements.append(Paragraph("Contact Information", heading_style))
    contact_text = f"""
    <b>Dee Davis Inc.</b><br/>
    <b>Owner:</b> Dee Davis<br/>
    """
    
    if contact_email:
        contact_text += f"<b>Email:</b> {contact_email}<br/>"
    if contact_phone:
        contact_text += f"<b>Phone:</b> {contact_phone}<br/>"
    
    contact_text += f"""<br/>
    <b>Service Coverage:</b> {coverage}<br/>
    <b>Certifications:</b> {certifications}<br/>
    <b>Dispatch Platform:</b> Snapdocs (Automated)<br/>
    <b>Response Time:</b> Under 2 hours average
    """
    
    elements.append(Paragraph(contact_text, body_style))
    elements.append(Spacer(1, 0.5 * inch))
    
    # Footer
    footer_text = f"""
    <i>This proposal is confidential and intended solely for {partner_name} supplier diversity evaluation. 
    Dee Davis Inc. reserves all rights to the services, methods, and business model described herein.</i>
    """
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.grey,
        alignment=TA_CENTER,
        fontName='Helvetica-Oblique'
    )
    elements.append(Paragraph(footer_text, footer_style))
    
    # Build PDF
    doc.build(elements)
    
    return filepath, filename

@app.route('/api/partnership/generate', methods=['POST'])
def generate_partnership():
    """Generate partnership proposal PDF"""
    try:
        data = request.json
        
        if not data.get('partnerName'):
            return jsonify({
                'success': False,
                'error': 'Partner name is required'
            }), 400
        
        filepath, filename = generate_partnership_proposal_pdf(data)
        
        return send_file(
            filepath,
            mimetype='application/pdf',
            as_attachment=False,
            download_name=filename
        )
        
    except Exception as e:
        print(f"Error generating partnership proposal: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/partnership/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Partnership Proposal Generator',
        'port': 5004
    })

if __name__ == '__main__':
    print("=" * 60)
    print("Partnership Proposal Generator API")
    print("=" * 60)
    print("🚀 Server starting on http://localhost:5004")
    print("📄 Endpoint: POST /api/partnership/generate")
    print("❤️  Health: GET /api/partnership/health")
    print("📁 Output: generated_partnerships/")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5004, debug=True)
