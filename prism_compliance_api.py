#!/usr/bin/env python3
"""
PRISM Compliance & Document API
Handles:
1. Agent document uploads → Airtable attachments
2. DDI document generation (NDA, IC Agreement, W-9 request)
3. Compliance status tracking
"""

import os
import json
import tempfile
import base64
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, send_file
from io import BytesIO

# ─── Blueprint ────────────────────────────────────────────────────
prism_compliance = Blueprint('prism_compliance', __name__)

# ─── Airtable Config ─────────────────────────────────────────────
def get_airtable():
    """Get Airtable API connection"""
    try:
        from pyairtable import Api
        api_key = os.environ.get('AIRTABLE_API_KEY', '')
        base_id = os.environ.get('AIRTABLE_BASE_ID', '')
        if not api_key or not base_id:
            return None, None
        api = Api(api_key)
        return api, base_id
    except ImportError:
        return None, None

COMPLIANCE_TABLE = 'NEXUS COMPLIANCE DOCUMENTS'
FIELD_AGENTS_TABLE = 'PRISM FIELD AGENTS'


# ═══════════════════════════════════════════════════════════════════
# 1. DOCUMENT UPLOAD API
# ═══════════════════════════════════════════════════════════════════

@prism_compliance.route('/prism/compliance/upload', methods=['POST'])
def upload_compliance_document():
    """
    Upload a document file and attach it to a compliance record in Airtable.
    
    Expects multipart form data:
    - file: The document file (PDF, JPEG, PNG)
    - compliance_id: The Airtable record ID of the compliance document
    - person_type: 'Field Agent', 'Subcontractor', or 'Supplier'
    - document_type: Type of document being uploaded
    """
    try:
        # Validate file
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Validate file type
        allowed_extensions = {'.pdf', '.jpg', '.jpeg', '.png'}
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in allowed_extensions:
            return jsonify({'error': f'File type {ext} not allowed. Use PDF, JPEG, or PNG.'}), 400
        
        # Validate file size (50MB max)
        file.seek(0, 2)
        size = file.tell()
        file.seek(0)
        if size > 50 * 1024 * 1024:
            return jsonify({'error': 'File too large. Maximum 50MB.'}), 400
        
        compliance_id = request.form.get('compliance_id', '')
        person_type = request.form.get('person_type', 'Field Agent')
        document_type = request.form.get('document_type', '')
        
        api, base_id = get_airtable()
        
        if api and base_id and compliance_id:
            # Upload to Airtable
            table = api.table(base_id, COMPLIANCE_TABLE)
            
            # Save file temporarily for Airtable upload
            with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
                file.save(tmp.name)
                tmp_path = tmp.name
            
            try:
                # Update the compliance record with the file attachment and status
                table.update(compliance_id, {
                    'DOCUMENT_FILE': [{'url': f'file://{tmp_path}'}],  # Airtable handles the upload
                    'DOCUMENT_STATUS': 'Submitted',
                    'DATE_RECEIVED': datetime.now().strftime('%Y-%m-%d'),
                    'UPLOADED_BY': 'Portal Upload',
                })
                
                return jsonify({
                    'success': True,
                    'message': f'{document_type} uploaded successfully. Status changed to Submitted.',
                    'record_id': compliance_id,
                    'status': 'Submitted',
                })
            finally:
                # Clean up temp file
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
        else:
            # No Airtable connection — save locally for now
            upload_dir = os.path.join(os.path.dirname(__file__), 'uploads', 'compliance')
            os.makedirs(upload_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            safe_name = f"{document_type.replace(' ', '_').replace('/', '_')}_{timestamp}{ext}"
            filepath = os.path.join(upload_dir, safe_name)
            file.save(filepath)
            
            return jsonify({
                'success': True,
                'message': f'{document_type} uploaded successfully (saved locally — Airtable not connected).',
                'filepath': filepath,
                'status': 'Submitted',
            })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@prism_compliance.route('/prism/scanback/upload', methods=['POST'])
def upload_scanback():
    """
    Upload scanback files for a PRISM order.
    
    Expects multipart form data:
    - files: One or more scanback files
    - order_id: The PRISM order number (e.g., PRISM-2026-0001)
    """
    try:
        if 'files' not in request.files:
            # Try single file
            if 'file' not in request.files:
                return jsonify({'error': 'No files provided'}), 400
            files = [request.files['file']]
        else:
            files = request.files.getlist('files')
        
        order_id = request.form.get('order_id', '')
        if not order_id:
            return jsonify({'error': 'No order_id provided'}), 400
        
        uploaded = []
        upload_dir = os.path.join(os.path.dirname(__file__), 'uploads', 'scanbacks', order_id)
        os.makedirs(upload_dir, exist_ok=True)
        
        for file in files:
            if file.filename == '':
                continue
            
            ext = os.path.splitext(file.filename)[1].lower()
            if ext not in {'.pdf', '.jpg', '.jpeg', '.png'}:
                continue
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            safe_name = f"scanback_{timestamp}_{file.filename}"
            filepath = os.path.join(upload_dir, safe_name)
            file.save(filepath)
            uploaded.append({
                'filename': file.filename,
                'saved_as': safe_name,
                'size': os.path.getsize(filepath),
            })
        
        # If Airtable connected, also update the order record
        api, base_id = get_airtable()
        if api and base_id:
            try:
                orders_table = api.table(base_id, 'PRISM Orders')
                # Find the order by order number
                records = orders_table.all(formula=f"{{Order Number}} = '{order_id}'")
                if records:
                    orders_table.update(records[0]['id'], {
                        'Status': 'Scanned Back',
                        'Scanback Upload Date': datetime.now().strftime('%Y-%m-%d'),
                    })
            except Exception:
                pass  # Don't fail if Airtable update fails
        
        # NEXUS ADVISOR: Teach about scanback inspection
        advisor_insight = None
        try:
            from nexus_advisor import advise
            advisor_insight = advise('prism', 'scanback_inspected', {
                'order_id': order_id,
                'file_count': len(uploaded),
            })
        except Exception:
            pass

        return jsonify({
            'success': True,
            'message': f'{len(uploaded)} file(s) uploaded for {order_id}. Submitted for inspection.',
            'files': uploaded,
            'order_id': order_id,
            'advisor': advisor_insight,
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ═══════════════════════════════════════════════════════════════════
# 2. COMPLIANCE STATUS API
# ═══════════════════════════════════════════════════════════════════

@prism_compliance.route('/prism/compliance/<person_type>/<person_id>', methods=['GET'])
def get_compliance_docs(person_type, person_id):
    """Get all compliance documents for a person"""
    api, base_id = get_airtable()
    
    if not api or not base_id:
        return jsonify({'error': 'Airtable not configured'}), 503
    
    try:
        table = api.table(base_id, COMPLIANCE_TABLE)
        
        # Map person type to field name
        link_field = {
            'field-agent': 'FIELD_AGENT',
            'subcontractor': 'SUBCONTRACTOR',
            'supplier': 'SUPPLIER',
        }.get(person_type.lower(), 'FIELD_AGENT')
        
        records = table.all(formula=f"{{{link_field}}} = '{person_id}'")
        
        docs = []
        for r in records:
            fields = r['fields']
            docs.append({
                'id': r['id'],
                'type': fields.get('DOCUMENT_TYPE', ''),
                'status': fields.get('DOCUMENT_STATUS', 'Missing'),
                'date_received': fields.get('DATE_RECEIVED', ''),
                'date_approved': fields.get('DATE_APPROVED', ''),
                'expiration_date': fields.get('EXPIRATION_DATE', ''),
                'alert_status': fields.get('ALERT_STATUS', ''),
                'has_file': bool(fields.get('DOCUMENT_FILE')),
                'policy_number': fields.get('POLICY_NUMBER', ''),
                'commission_number': fields.get('COMMISSION_NUMBER', ''),
                'notes': fields.get('NOTES', ''),
            })
        
        return jsonify({
            'success': True,
            'person_type': person_type,
            'person_id': person_id,
            'documents': docs,
            'total': len(docs),
            'approved': sum(1 for d in docs if d['status'] == 'Approved'),
            'missing': sum(1 for d in docs if d['status'] == 'Missing'),
            'expired': sum(1 for d in docs if d['status'] == 'Expired'),
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@prism_compliance.route('/prism/compliance/<person_type>/<person_id>/can-work', methods=['GET'])
def can_person_work(person_type, person_id):
    """Check if a person is cleared to receive work"""
    api, base_id = get_airtable()
    
    if not api or not base_id:
        return jsonify({'can_work': False, 'reason': 'Airtable not configured'}), 503
    
    try:
        # Check person's onboarding status
        table_name = {
            'field-agent': FIELD_AGENTS_TABLE,
            'subcontractor': 'GPSS SUBCONTRACTORS',
            'supplier': 'GPSS SUPPLIERS',
        }.get(person_type.lower())
        
        if not table_name:
            return jsonify({'can_work': False, 'reason': 'Invalid person type'}), 400
        
        table = api.table(base_id, table_name)
        record = table.get(person_id)
        
        if not record:
            return jsonify({'can_work': False, 'reason': 'Person not found'}), 404
        
        fields = record['fields']
        status = fields.get('ONBOARDING_STATUS', '')
        compliance_ready = fields.get('COMPLIANCE_READY', False)
        
        if status != 'Active':
            return jsonify({'can_work': False, 'reason': f'Onboarding status is {status}, not Active'})
        
        if not compliance_ready:
            return jsonify({'can_work': False, 'reason': 'Compliance documents not complete'})
        
        return jsonify({'can_work': True, 'status': status})
    
    except Exception as e:
        return jsonify({'can_work': False, 'reason': str(e)}), 500


# ═══════════════════════════════════════════════════════════════════
# 3. DOCUMENT GENERATOR — DDI Agreements & Forms
# ═══════════════════════════════════════════════════════════════════

def _generate_pdf_document(title, subtitle, body_sections, filename):
    """
    Generate a professional DDI-branded PDF document using reportlab.
    
    Returns a BytesIO buffer with the PDF.
    """
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
    except ImportError:
        return None
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
    )
    
    # DDI Brand Colors
    ddi_deep_blue = colors.HexColor('#1B2A4A')
    ddi_teal = colors.HexColor('#2DD4BF')
    ddi_pink = colors.HexColor('#EC4899')
    ddi_gold = colors.HexColor('#F59E0B')
    ddi_dark = colors.HexColor('#0F1A2E')
    
    styles = getSampleStyleSheet()
    
    # Custom styles
    styles.add(ParagraphStyle(
        'DDITitle',
        parent=styles['Title'],
        fontSize=22,
        textColor=ddi_deep_blue,
        spaceAfter=6,
        fontName='Helvetica-Bold',
    ))
    styles.add(ParagraphStyle(
        'DDISubtitle',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#64748B'),
        spaceAfter=20,
        alignment=TA_CENTER,
    ))
    styles.add(ParagraphStyle(
        'DDIHeading',
        parent=styles['Heading2'],
        fontSize=13,
        textColor=ddi_deep_blue,
        spaceBefore=16,
        spaceAfter=8,
        fontName='Helvetica-Bold',
    ))
    styles.add(ParagraphStyle(
        'DDIBody',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#1E293B'),
        spaceAfter=8,
        leading=14,
        alignment=TA_JUSTIFY,
    ))
    styles.add(ParagraphStyle(
        'DDISmall',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.HexColor('#94A3B8'),
        spaceAfter=4,
    ))
    styles.add(ParagraphStyle(
        'DDISignature',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#1E293B'),
        spaceBefore=30,
        spaceAfter=4,
    ))
    
    story = []
    
    # ── Header ──
    header_data = [
        [
            Paragraph('<b>DEE DAVIS INC.</b>', ParagraphStyle('hdr', parent=styles['Normal'], fontSize=16, textColor=ddi_deep_blue, fontName='Helvetica-Bold')),
            Paragraph('755 W. Big Beaver Rd, Suite 2020<br/>Troy, MI 48084<br/>(248) 376-4550 | info@deedavis.biz', ParagraphStyle('hdr2', parent=styles['Normal'], fontSize=8, textColor=colors.HexColor('#64748B'), alignment=2)),
        ]
    ]
    header_table = Table(header_data, colWidths=[3.5 * inch, 3.5 * inch])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LINEBELOW', (0, 0), (-1, 0), 2, ddi_pink),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 20))
    
    # ── Title ──
    story.append(Paragraph(title, styles['DDITitle']))
    story.append(Paragraph(subtitle, styles['DDISubtitle']))
    
    # ── Body Sections ──
    for section in body_sections:
        if section.get('heading'):
            story.append(Paragraph(section['heading'], styles['DDIHeading']))
        if section.get('body'):
            for para in section['body']:
                story.append(Paragraph(para, styles['DDIBody']))
        if section.get('signature_block'):
            story.append(Spacer(1, 20))
            for line in section['signature_block']:
                story.append(Paragraph(line, styles['DDISignature']))
    
    # ── Footer ──
    story.append(Spacer(1, 30))
    story.append(Paragraph(
        'EDWOSB / WOSB / WBE / MBE / SBE Certified | CAGE: 8UMX3 | UEI: HJB4KNYJVGZ1',
        ParagraphStyle('footer', parent=styles['Normal'], fontSize=7, textColor=colors.HexColor('#94A3B8'), alignment=TA_CENTER)
    ))
    story.append(Paragraph(
        f'Generated {datetime.now().strftime("%B %d, %Y")} | Dee Davis Inc. Confidential',
        ParagraphStyle('footer2', parent=styles['Normal'], fontSize=7, textColor=colors.HexColor('#CBD5E1'), alignment=TA_CENTER)
    ))
    
    doc.build(story)
    buffer.seek(0)
    return buffer


@prism_compliance.route('/prism/documents/generate/nda', methods=['POST'])
def generate_nda():
    """Generate an NDA / Confidentiality Agreement for an agent or subcontractor"""
    data = request.json or {}
    person_name = data.get('person_name', '[CONTRACTOR NAME]')
    person_type = data.get('person_type', 'Field Agent')
    effective_date = data.get('effective_date', datetime.now().strftime('%B %d, %Y'))
    
    sections = [
        {
            'heading': '1. DEFINITION OF CONFIDENTIAL INFORMATION',
            'body': [
                f'For purposes of this Agreement, "Confidential Information" means any and all non-public information disclosed by Dee Davis Inc. ("DDI") to {person_name} ("Contractor"), including but not limited to:',
                '• Client names, contact information, and account details<br/>'
                '• Signer/subject personal information, documents, and records<br/>'
                '• Business strategies, pricing, margins, and fee structures<br/>'
                '• Proprietary systems, software, and technology (including NEXUS, PRISM, ATLAS PM, FleetFlow)<br/>'
                '• Vendor relationships, supplier lists, and subcontractor networks<br/>'
                '• Government contract details, solicitation numbers, and bid strategies<br/>'
                '• Any information marked or reasonably understood to be confidential',
            ]
        },
        {
            'heading': '2. OBLIGATIONS OF CONTRACTOR',
            'body': [
                f'{person_name} agrees to:',
                '(a) Hold all Confidential Information in strict confidence and not disclose it to any third party without prior written consent from DDI.<br/><br/>'
                '(b) Use Confidential Information solely for the purpose of performing services for DDI.<br/><br/>'
                '(c) Not copy, reproduce, or distribute Confidential Information except as necessary to perform assigned duties.<br/><br/>'
                '(d) Return or destroy all Confidential Information upon termination of the working relationship.<br/><br/>'
                '(e) Immediately notify DDI of any unauthorized disclosure or use of Confidential Information.',
            ]
        },
        {
            'heading': '3. SPECIFIC PROHIBITIONS',
            'body': [
                'Contractor specifically agrees NOT to:',
                '• Contact DDI clients, signers, or subjects directly for personal business purposes<br/>'
                '• Share client information with competing companies or individuals<br/>'
                '• Photograph, screenshot, or copy client documents beyond what is required for assigned tasks<br/>'
                '• Discuss DDI pricing, margins, or business strategies with anyone outside of DDI<br/>'
                '• Solicit DDI clients, vendors, or other contractors for competing services',
            ]
        },
        {
            'heading': '4. DURATION',
            'body': [
                'This Agreement shall remain in effect for the duration of the working relationship between DDI and Contractor, and for a period of two (2) years following its termination, regardless of the reason for termination.',
            ]
        },
        {
            'heading': '5. REMEDIES',
            'body': [
                'Contractor acknowledges that a breach of this Agreement may cause irreparable harm to DDI. In the event of a breach, DDI shall be entitled to seek injunctive relief and any other remedies available at law or in equity, including monetary damages.',
            ]
        },
        {
            'heading': '6. GOVERNING LAW',
            'body': [
                'This Agreement shall be governed by and construed in accordance with the laws of the State of Michigan.',
            ]
        },
        {
            'signature_block': [
                f'<b>Effective Date:</b> {effective_date}',
                '',
                '<b>DEE DAVIS INC.</b>',
                '_____________________________________________',
                'Dieasha Davis, President &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Date: _______________',
                '',
                f'<b>CONTRACTOR: {person_name.upper()}</b>',
                '_____________________________________________',
                f'{person_name} &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Date: _______________',
                '',
                'Address: _____________________________________________',
                '',
                'Email: _______________________________________________',
            ]
        },
    ]
    
    buffer = _generate_pdf_document(
        title='NON-DISCLOSURE AGREEMENT',
        subtitle=f'Confidentiality Agreement — {person_type}',
        body_sections=sections,
        filename='NDA',
    )
    
    if buffer is None:
        return jsonify({'error': 'reportlab not installed. Run: pip install reportlab'}), 500
    
    filename = f"DDI_NDA_{person_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf"
    return send_file(buffer, mimetype='application/pdf', as_attachment=True, download_name=filename)


@prism_compliance.route('/prism/documents/generate/ic-agreement', methods=['POST'])
def generate_ic_agreement():
    """Generate an Independent Contractor Agreement"""
    data = request.json or {}
    person_name = data.get('person_name', '[CONTRACTOR NAME]')
    specialties = data.get('specialties', ['Field Services'])
    effective_date = data.get('effective_date', datetime.now().strftime('%B %d, %Y'))
    
    specialties_str = ', '.join(specialties)
    
    sections = [
        {
            'heading': '1. ENGAGEMENT',
            'body': [
                f'Dee Davis Inc. ("DDI"), a Michigan corporation, engages {person_name} ("Contractor") as an independent contractor to perform the following services: <b>{specialties_str}</b>.',
                'Contractor shall perform services as assigned through DDI\'s PRISM Field Service Management system. Assignments are offered on a per-order basis; Contractor is free to accept or decline any assignment.',
            ]
        },
        {
            'heading': '2. INDEPENDENT CONTRACTOR STATUS',
            'body': [
                f'{person_name} acknowledges and agrees that:',
                '(a) Contractor is an independent contractor, NOT an employee of DDI.<br/><br/>'
                '(b) Contractor is responsible for their own federal, state, and local taxes, including self-employment tax.<br/><br/>'
                '(c) Contractor is not entitled to employee benefits including health insurance, retirement plans, paid time off, or workers\' compensation.<br/><br/>'
                '(d) Contractor controls the manner and means of performing services, subject to DDI\'s quality standards and client requirements.<br/><br/>'
                '(e) Contractor may perform services for other companies, provided it does not conflict with DDI assignments or violate the NDA.',
            ]
        },
        {
            'heading': '3. COMPENSATION',
            'body': [
                'Contractor shall be compensated on a per-assignment basis at rates agreed upon at the time of assignment acceptance. Rates include:',
                '• <b>Base Fee:</b> Per-service fee as listed in the assignment<br/>'
                '• <b>Travel Fee:</b> Mileage/travel compensation when applicable<br/>'
                '• <b>Surcharges:</b> Rush, after-hours, or complexity surcharges as specified',
                'Payment is issued after the assignment is completed AND all required documentation (scanbacks, certifications) has been verified by DDI. Payment terms are Net 14 from verification date.',
            ]
        },
        {
            'heading': '4. REQUIRED DOCUMENTATION',
            'body': [
                'Contractor must maintain current and valid:',
                '• W-9 form on file with DDI<br/>'
                '• Signed NDA/Confidentiality Agreement<br/>'
                '• Background check clearance (updated annually)<br/>'
                '• All certifications and licenses required for assigned specialties<br/>'
                '• Proof of insurance (E&O, vehicle) as applicable',
                'Failure to maintain required documentation will result in suspension of new assignments until compliance is restored.',
            ]
        },
        {
            'heading': '5. QUALITY STANDARDS',
            'body': [
                'Contractor agrees to:',
                '(a) Perform all services professionally and in accordance with industry standards.<br/><br/>'
                '(b) Follow all client-specific rules and instructions provided with each assignment.<br/><br/>'
                '(c) Upload complete and legible scanbacks within the timeframe specified per assignment.<br/><br/>'
                '(d) Respond to correction requests within 24 hours.<br/><br/>'
                '(e) Maintain a professional appearance and demeanor at all appointments.',
            ]
        },
        {
            'heading': '6. TERMINATION',
            'body': [
                'Either party may terminate this Agreement at any time with written notice. Contractor will be compensated for all completed assignments through the termination date. Upon termination, Contractor must return all DDI materials and comply with NDA obligations.',
            ]
        },
        {
            'heading': '7. GOVERNING LAW',
            'body': [
                'This Agreement shall be governed by the laws of the State of Michigan. Any disputes shall be resolved in Oakland County, Michigan.',
            ]
        },
        {
            'signature_block': [
                f'<b>Effective Date:</b> {effective_date}',
                '',
                '<b>DEE DAVIS INC.</b>',
                '_____________________________________________',
                'Dieasha Davis, President &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Date: _______________',
                '',
                f'<b>CONTRACTOR: {person_name.upper()}</b>',
                '_____________________________________________',
                f'{person_name} &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Date: _______________',
                '',
                'SSN/EIN: ____________________________________________',
                '',
                'Address: _____________________________________________',
            ]
        },
    ]
    
    buffer = _generate_pdf_document(
        title='INDEPENDENT CONTRACTOR AGREEMENT',
        subtitle=f'Field Agent Services Agreement — {specialties_str}',
        body_sections=sections,
        filename='IC_Agreement',
    )
    
    if buffer is None:
        return jsonify({'error': 'reportlab not installed. Run: pip install reportlab'}), 500
    
    filename = f"DDI_IC_Agreement_{person_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf"
    return send_file(buffer, mimetype='application/pdf', as_attachment=True, download_name=filename)


@prism_compliance.route('/prism/documents/generate/w9-request', methods=['POST'])
def generate_w9_request():
    """Generate a W-9 request letter for an agent or subcontractor"""
    data = request.json or {}
    person_name = data.get('person_name', '[CONTRACTOR NAME]')
    person_email = data.get('person_email', '')
    person_type = data.get('person_type', 'Field Agent')
    
    sections = [
        {
            'body': [
                f'Dear {person_name},',
                f'Thank you for joining the Dee Davis Inc. {person_type.lower()} network. Before we can process any payments for your services, we are required by the IRS to have a completed W-9 form on file.',
            ]
        },
        {
            'heading': 'What We Need',
            'body': [
                'Please complete and return a <b>Form W-9 (Request for Taxpayer Identification Number and Certification)</b>. You can download the current form from the IRS website at: <b>https://www.irs.gov/forms-pubs/about-form-w-9</b>',
            ]
        },
        {
            'heading': 'How to Submit',
            'body': [
                'You can submit your completed W-9 through any of the following methods:',
                '1. <b>Upload via Portal:</b> Log into your DDI Field Agent Portal and upload under Documents<br/>'
                '2. <b>Email:</b> Send to compliance@deedavis.biz (encrypted/password-protected preferred)<br/>'
                '3. <b>Fax:</b> (248) 376-4551',
            ]
        },
        {
            'heading': 'Important Notes',
            'body': [
                '• The name on your W-9 must match the name on your DDI contractor agreement.<br/>'
                '• If you operate under a business name (LLC, sole proprietorship), include both your legal name and business name.<br/>'
                '• Payment cannot be issued until a valid W-9 is on file.<br/>'
                '• Your W-9 information is handled confidentially and used solely for tax reporting purposes.',
            ]
        },
        {
            'body': [
                'If you have any questions, please don\'t hesitate to reach out at (248) 376-4550 or compliance@deedavis.biz.',
                'We look forward to working with you!',
                '',
                'Warm regards,',
            ]
        },
        {
            'signature_block': [
                '<b>Dee Davis</b>',
                'President, Dee Davis Inc.',
                '(248) 376-4550 | info@deedavis.biz',
            ]
        },
    ]
    
    buffer = _generate_pdf_document(
        title='W-9 REQUEST',
        subtitle=f'Taxpayer Information Required — {person_type}',
        body_sections=sections,
        filename='W9_Request',
    )
    
    if buffer is None:
        return jsonify({'error': 'reportlab not installed. Run: pip install reportlab'}), 500
    
    filename = f"DDI_W9_Request_{person_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf"
    return send_file(buffer, mimetype='application/pdf', as_attachment=True, download_name=filename)


@prism_compliance.route('/prism/documents/generate/subcontractor-agreement', methods=['POST'])
def generate_sub_agreement():
    """Generate a Subcontractor Agreement"""
    data = request.json or {}
    company_name = data.get('company_name', '[SUBCONTRACTOR COMPANY]')
    contact_name = data.get('contact_name', '[CONTACT NAME]')
    service_type = data.get('service_type', '[SERVICE TYPE]')
    effective_date = data.get('effective_date', datetime.now().strftime('%B %d, %Y'))
    
    sections = [
        {
            'heading': '1. SCOPE OF WORK',
            'body': [
                f'Dee Davis Inc. ("DDI") engages {company_name} ("Subcontractor") to provide <b>{service_type}</b> services as described in individual work orders issued under this Agreement.',
                'Each work order will specify the scope, location, timeline, deliverables, and compensation for that specific engagement.',
            ]
        },
        {
            'heading': '2. RELATIONSHIP',
            'body': [
                'Subcontractor is an independent entity and not an employee, partner, or agent of DDI. Subcontractor is responsible for their own employees, taxes, insurance, and compliance with all applicable laws.',
            ]
        },
        {
            'heading': '3. COMPENSATION & PAYMENT',
            'body': [
                'Compensation will be specified in each work order. Standard payment terms are Net 30 from DDI\'s receipt of payment from the end client. DDI reserves the right to adjust payment terms for specific projects.',
            ]
        },
        {
            'heading': '4. INSURANCE REQUIREMENTS',
            'body': [
                'Subcontractor must maintain:<br/>'
                '• General Liability Insurance: $1,000,000 per occurrence / $2,000,000 aggregate<br/>'
                '• Workers Compensation Insurance: Statutory limits (if Subcontractor has employees)<br/>'
                '• Professional Liability Insurance: $1,000,000 (if providing professional services)<br/>'
                '• Dee Davis Inc. must be listed as an Additional Insured on all policies.',
            ]
        },
        {
            'heading': '5. CONFIDENTIALITY',
            'body': [
                'Subcontractor agrees to maintain confidentiality of all DDI client information, project details, pricing, and business practices. A separate NDA may be required for specific projects.',
            ]
        },
        {
            'heading': '6. NON-SOLICITATION',
            'body': [
                'For a period of two (2) years following termination, Subcontractor shall not directly solicit or perform services for any DDI client that Subcontractor was introduced to through DDI, without DDI\'s prior written consent.',
            ]
        },
        {
            'heading': '7. TERMINATION',
            'body': [
                'Either party may terminate this Agreement with 30 days written notice. Outstanding work orders will be completed and compensated per their terms.',
            ]
        },
        {
            'signature_block': [
                f'<b>Effective Date:</b> {effective_date}',
                '',
                '<b>DEE DAVIS INC.</b>',
                '_____________________________________________',
                'Dieasha Davis, President &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Date: _______________',
                '',
                f'<b>{company_name.upper()}</b>',
                '_____________________________________________',
                f'{contact_name} &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Date: _______________',
                '',
                'Title: _______________________________________________',
                '',
                'EIN: ________________________________________________',
            ]
        },
    ]
    
    buffer = _generate_pdf_document(
        title='SUBCONTRACTOR AGREEMENT',
        subtitle=f'Master Service Agreement — {service_type}',
        body_sections=sections,
        filename='Sub_Agreement',
    )
    
    if buffer is None:
        return jsonify({'error': 'reportlab not installed. Run: pip install reportlab'}), 500
    
    filename = f"DDI_Sub_Agreement_{company_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf"
    return send_file(buffer, mimetype='application/pdf', as_attachment=True, download_name=filename)


# ═══════════════════════════════════════════════════════════════════
# 4. LIST AVAILABLE DOCUMENT TEMPLATES
# ═══════════════════════════════════════════════════════════════════

@prism_compliance.route('/prism/documents/templates', methods=['GET'])
def list_document_templates():
    """List all available document templates that DDI can generate"""
    return jsonify({
        'templates': [
            {
                'id': 'nda',
                'name': 'NDA / Confidentiality Agreement',
                'description': 'Non-disclosure agreement for contractors and subcontractors',
                'endpoint': '/prism/documents/generate/nda',
                'required_fields': ['person_name'],
                'optional_fields': ['person_type', 'effective_date'],
                'for': ['Field Agent', 'Subcontractor'],
            },
            {
                'id': 'ic-agreement',
                'name': 'Independent Contractor Agreement',
                'description': 'IC agreement for field agents with specialty-specific terms',
                'endpoint': '/prism/documents/generate/ic-agreement',
                'required_fields': ['person_name'],
                'optional_fields': ['specialties', 'effective_date'],
                'for': ['Field Agent'],
            },
            {
                'id': 'w9-request',
                'name': 'W-9 Request Letter',
                'description': 'Letter requesting W-9 form from contractor',
                'endpoint': '/prism/documents/generate/w9-request',
                'required_fields': ['person_name'],
                'optional_fields': ['person_email', 'person_type'],
                'for': ['Field Agent', 'Subcontractor', 'Supplier'],
            },
            {
                'id': 'sub-agreement',
                'name': 'Subcontractor Agreement',
                'description': 'Master service agreement for subcontractors',
                'endpoint': '/prism/documents/generate/subcontractor-agreement',
                'required_fields': ['company_name', 'contact_name', 'service_type'],
                'optional_fields': ['effective_date'],
                'for': ['Subcontractor'],
            },
        ]
    })


# ═══════════════════════════════════════════════════════════════════
# 5. QC REVIEW API — Admin reviews scanbacks
# ═══════════════════════════════════════════════════════════════════

QC_CHECKLIST = [
    {'id': 1, 'check': 'Every required signature present?'},
    {'id': 2, 'check': 'Every required initial present?'},
    {'id': 3, 'check': 'Every required date filled in?'},
    {'id': 4, 'check': 'Notary seal/stamp present where required?'},
    {'id': 5, 'check': 'All required pages/forms included?'},
    {'id': 6, 'check': 'ID copy included (when required)?'},
    {'id': 7, 'check': 'No stray markings where there shouldn\'t be?'},
]


@prism_compliance.route('/prism/qc/review', methods=['POST'])
def qc_review_scanback():
    """
    Admin submits QC review result for a scanback.

    Expects JSON:
    - order_id: PRISM order ID
    - result: 'clean' or 'errors'
    - checklist: list of {id, passed: bool}
    - errors: list of {severity, page, description} (only if result='errors')
    - reviewer: who reviewed
    """
    data = request.json or {}
    order_id = data.get('order_id', '')
    result = data.get('result', '')  # 'clean' or 'errors'
    checklist = data.get('checklist', [])
    errors = data.get('errors', [])
    reviewer = data.get('reviewer', 'DDI Admin')

    if not order_id or result not in ('clean', 'errors'):
        return jsonify({'error': 'order_id and result (clean|errors) required'}), 400

    new_status = 'Verified' if result == 'clean' else 'Correction Requested'

    # Try to update Airtable
    api, base_id = get_airtable()
    if api and base_id:
        try:
            orders_table = api.table(base_id, 'PRISM Orders')
            records = orders_table.all(formula=f"{{Order Number}} = '{order_id}'")
            if records:
                update_fields = {
                    'Status': new_status,
                    'QC Reviewed By': reviewer,
                    'QC Review Date': datetime.now().strftime('%Y-%m-%d'),
                    'QC Result': result.capitalize(),
                }
                if result == 'errors':
                    update_fields['QC Errors'] = json.dumps(errors)
                orders_table.update(records[0]['id'], update_fields)
        except Exception as e:
            # Don't fail if Airtable update fails
            print(f"Airtable QC update failed: {e}")

    # Save QC report locally
    qc_dir = os.path.join(os.path.dirname(__file__), 'uploads', 'qc_reports')
    os.makedirs(qc_dir, exist_ok=True)
    report = {
        'order_id': order_id,
        'result': result,
        'new_status': new_status,
        'checklist': checklist,
        'errors': errors,
        'reviewer': reviewer,
        'timestamp': datetime.now().isoformat(),
    }
    report_path = os.path.join(qc_dir, f"{order_id}_qc_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)

    # VERTEX BRIDGE: Auto-create invoice when order passes QC
    vertex_invoice_id = None
    if result == 'clean':
        try:
            if api and base_id and records:
                order_fields = records[0].get('fields', {})
                order_amount = order_fields.get('Amount', 0) or order_fields.get('Total', 0) or order_fields.get('Price', 0)
                client_name = order_fields.get('Client', '') or order_fields.get('Client Name', '') or 'PRISM Client'
                if order_amount:
                    vertex_table = api.table(base_id, 'VERTEX INVOICES')
                    vertex_record = vertex_table.create({
                        'Invoice Number': f"PRISM-INV-{order_id}",
                        'Invoice Date': datetime.now().strftime('%Y-%m-%d'),
                        'Due Date': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
                        'Client Name': client_name,
                        'Source System': 'PRISM',
                        'Source Record ID': records[0]['id'],
                        'Invoice Type': 'Standard',
                        'Total Amount': float(order_amount),
                        'Payment Status': 'Unpaid',
                        'Payment Terms': 'Net 30',
                        'Notes': f"Auto-generated from PRISM order {order_id} (QC Verified)",
                    })
                    vertex_invoice_id = vertex_record.get('id')
        except Exception as ve:
            print(f"PRISM → VERTEX invoice creation: {ve}")

    # COMPASS BRIDGE: Log completed service as deliverable against the contract
    compass_logged = False
    if result == 'clean' and api and base_id and records:
        try:
            order_fields = records[0].get('fields', {})
            contract_links = order_fields.get('Contract', []) or order_fields.get('PRISM Contract', [])
            if contract_links:
                compass_table = api.table(base_id, 'COMPASS Deliverables')
                compass_table.create({
                    'Title': f"PRISM Order {order_id} — {order_fields.get('Service Type', 'Field Service')}",
                    'Type': 'Service',
                    'Status': 'Completed',
                    'Due Date': datetime.now().strftime('%Y-%m-%d'),
                    'Completed Date': datetime.now().strftime('%Y-%m-%d'),
                    'Description': f"QC-verified field service order from PRISM. Agent: {order_fields.get('Agent', 'N/A')}",
                })
                compass_logged = True
        except Exception as cpe:
            print(f"PRISM → COMPASS deliverable: {cpe}")

    return jsonify({
        'success': True,
        'order_id': order_id,
        'result': result,
        'new_status': new_status,
        'message': f"Order {order_id} marked as {new_status}. "
                   + ("Agent will be notified of corrections." if result == 'errors' else "Payment can now process."),
        'errors_count': len(errors),
        'vertex_invoice_created': vertex_invoice_id is not None,
        'compass_deliverable_logged': compass_logged,
    })


@prism_compliance.route('/prism/qc/queue', methods=['GET'])
def qc_queue():
    """
    Get all orders awaiting QC review (status = Scanned Back).
    """
    api, base_id = get_airtable()

    if not api or not base_id:
        return jsonify({'error': 'Airtable not configured', 'queue': []}), 503

    try:
        table = api.table(base_id, 'PRISM Orders')
        records = table.all(formula="{Status} = 'Scanned Back'")

        queue = []
        for r in records:
            f = r['fields']
            queue.append({
                'record_id': r['id'],
                'order_id': f.get('Order Number', ''),
                'agent': f.get('Agent', ''),
                'client': f.get('Client', ''),
                'service_type': f.get('Service Type', ''),
                'signer': f.get('Signer Name', ''),
                'upload_date': f.get('Scanback Upload Date', ''),
                'has_files': bool(f.get('Scanback Files')),
            })

        return jsonify({
            'success': True,
            'queue': queue,
            'total': len(queue),
        })
    except Exception as e:
        return jsonify({'error': str(e), 'queue': []}), 500


@prism_compliance.route('/prism/qc/checklist', methods=['GET'])
def get_qc_checklist():
    """Return the 7-point QC inspection checklist"""
    return jsonify({'checklist': QC_CHECKLIST})
