#!/usr/bin/env python3
"""
HAVEN Partner Onboarding System
================================
Document delivery and onboarding workflow for HAVEN disaster response partners.

Sends agreement packages, tracks signatures, auto-reminds, and activates partners.

Uses the central NEXUS document delivery infrastructure (SendGrid + PDF generation).
"""

import os
import json
import base64
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import subprocess

# HAVEN folder paths
HAVEN_BASE = Path("/Users/deedavis/NEXUS BACKEND/HAVEN")
AGREEMENTS_DIR = HAVEN_BASE / "AGREEMENTS"

# Agreement templates
AGREEMENT_TEMPLATES = {
    "nda": AGREEMENTS_DIR / "HAVEN_Partner_NDA.html",
    "service_agreement": AGREEMENTS_DIR / "HAVEN_Partner_Agreement_Comprehensive.html",
    "baa": AGREEMENTS_DIR / "HAVEN_Business_Associate_Agreement.html",
    "coi_request": AGREEMENTS_DIR / "HAVEN_COI_Request.html",
}

# Partner types and their required documents
PARTNER_REQUIREMENTS = {
    "housing": {
        "documents": ["nda", "service_agreement", "baa", "coi_request"],
        "description": "Hotels, vacation rentals, temporary housing providers",
        "coi_requirements": ["general_liability", "property", "workers_comp"],
    },
    "transport": {
        "documents": ["nda", "service_agreement", "baa", "coi_request"],
        "description": "NEMT, rideshare, medical transport providers",
        "coi_requirements": ["general_liability", "auto", "workers_comp", "professional_liability"],
    },
    "medical": {
        "documents": ["nda", "service_agreement", "baa", "coi_request"],
        "description": "DME, pharmacy, home health, medical equipment providers",
        "coi_requirements": ["general_liability", "professional_liability", "product_liability", "workers_comp"],
    },
}


class OnboardingStatus(Enum):
    """Partner onboarding stages"""
    IDENTIFIED = "identified"
    NDA_SENT = "nda_sent"
    NDA_SIGNED = "nda_signed"
    AGREEMENT_SENT = "agreement_sent"
    AGREEMENT_SIGNED = "agreement_signed"
    BAA_SENT = "baa_sent"
    BAA_SIGNED = "baa_signed"
    COI_REQUESTED = "coi_requested"
    COI_RECEIVED = "coi_received"
    CREDENTIALING = "credentialing"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    TERMINATED = "terminated"


@dataclass
class HAVENPartner:
    """HAVEN partner record"""
    partner_id: str
    company_name: str
    contact_name: str
    contact_email: str
    contact_phone: str
    partner_type: str  # housing, transport, medical
    service_areas: List[str]
    status: str = "identified"
    nda_sent_date: Optional[str] = None
    nda_signed_date: Optional[str] = None
    agreement_sent_date: Optional[str] = None
    agreement_signed_date: Optional[str] = None
    baa_sent_date: Optional[str] = None
    baa_signed_date: Optional[str] = None
    coi_requested_date: Optional[str] = None
    coi_received_date: Optional[str] = None
    activation_date: Optional[str] = None
    notes: str = ""
    created_at: str = ""
    updated_at: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()


class HAVENPartnerOnboarding:
    """
    HAVEN Partner Onboarding System
    
    Manages the full partner onboarding lifecycle:
    1. Partner registration
    2. Document generation (personalized from templates)
    3. Document delivery via email
    4. Signature tracking
    5. Automated reminders
    6. Partner activation
    """
    
    def __init__(self, airtable_client=None):
        self.airtable = airtable_client
        self.partners_file = HAVEN_BASE / "PARTNER_REGISTRY.json"
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Ensure all required directories exist"""
        HAVEN_BASE.mkdir(exist_ok=True)
        AGREEMENTS_DIR.mkdir(exist_ok=True)
        (HAVEN_BASE / "GENERATED").mkdir(exist_ok=True)
        (HAVEN_BASE / "SENT").mkdir(exist_ok=True)
    
    def _load_partners(self) -> Dict[str, HAVENPartner]:
        """Load partners from local JSON file"""
        if self.partners_file.exists():
            with open(self.partners_file) as f:
                data = json.load(f)
                return {k: HAVENPartner(**v) for k, v in data.items()}
        return {}
    
    def _save_partners(self, partners: Dict[str, HAVENPartner]):
        """Save partners to local JSON file"""
        with open(self.partners_file, 'w') as f:
            json.dump({k: asdict(v) for k, v in partners.items()}, f, indent=2)
    
    def _generate_partner_id(self, partner_type: str) -> str:
        """Generate unique partner ID"""
        prefix = {"housing": "HP", "transport": "TP", "medical": "MP"}.get(partner_type, "XP")
        timestamp = datetime.now().strftime("%y%m%d%H%M")
        return f"HAVEN-{prefix}-{timestamp}"
    
    # =========================================================================
    # PARTNER REGISTRATION
    # =========================================================================
    
    def register_partner(
        self,
        company_name: str,
        contact_name: str,
        contact_email: str,
        contact_phone: str,
        partner_type: str,
        service_areas: List[str],
        notes: str = ""
    ) -> HAVENPartner:
        """
        Register a new HAVEN partner
        
        Args:
            company_name: Legal company name
            contact_name: Primary contact name
            contact_email: Primary contact email
            contact_phone: Primary contact phone
            partner_type: housing, transport, or medical
            service_areas: List of states/regions covered
            notes: Optional notes
            
        Returns:
            HAVENPartner record
        """
        if partner_type not in PARTNER_REQUIREMENTS:
            raise ValueError(f"Invalid partner type: {partner_type}. Must be one of: {list(PARTNER_REQUIREMENTS.keys())}")
        
        partner_id = self._generate_partner_id(partner_type)
        
        partner = HAVENPartner(
            partner_id=partner_id,
            company_name=company_name,
            contact_name=contact_name,
            contact_email=contact_email,
            contact_phone=contact_phone,
            partner_type=partner_type,
            service_areas=service_areas,
            notes=notes,
        )
        
        # Save to local registry
        partners = self._load_partners()
        partners[partner_id] = partner
        self._save_partners(partners)
        
        # Save to Airtable if available
        if self.airtable:
            try:
                self.airtable.create_record("HAVEN Partners", {
                    "Partner ID": partner_id,
                    "Company Name": company_name,
                    "Contact Name": contact_name,
                    "Contact Email": contact_email,
                    "Contact Phone": contact_phone,
                    "Partner Type": partner_type,
                    "Service Areas": ", ".join(service_areas),
                    "Status": "Identified",
                    "Notes": notes,
                })
            except Exception as e:
                print(f"Warning: Could not save to Airtable: {e}")
        
        return partner
    
    # =========================================================================
    # DOCUMENT GENERATION
    # =========================================================================
    
    def _personalize_document(self, template_path: Path, partner: HAVENPartner) -> str:
        """
        Personalize an HTML template with partner information
        
        Replaces placeholders:
        - {{PARTNER_NAME}} → company name
        - {{CONTACT_NAME}} → contact person
        - {{PARTNER_TYPE}} → partner type description
        - {{EFFECTIVE_DATE}} → today's date
        - {{SERVICE_AREAS}} → service areas list
        """
        with open(template_path) as f:
            html = f.read()
        
        replacements = {
            "{{PARTNER_NAME}}": partner.company_name,
            "{{CONTACT_NAME}}": partner.contact_name,
            "{{PARTNER_TYPE}}": partner.partner_type.title(),
            "{{EFFECTIVE_DATE}}": datetime.now().strftime("%B %d, %Y"),
            "{{SERVICE_AREAS}}": ", ".join(partner.service_areas),
            "{{PARTNER_ID}}": partner.partner_id,
            "{{CONTACT_EMAIL}}": partner.contact_email,
            "{{CONTACT_PHONE}}": partner.contact_phone,
            "[PARTNER NAME]": partner.company_name,
            "[EFFECTIVE DATE]": datetime.now().strftime("%B %d, %Y"),
        }
        
        for placeholder, value in replacements.items():
            html = html.replace(placeholder, value)
        
        return html
    
    def _html_to_pdf(self, html_path: Path, pdf_path: Path) -> bool:
        """Convert HTML to PDF using wkhtmltopdf or Chrome"""
        try:
            # Try wkhtmltopdf first
            result = subprocess.run(
                ["wkhtmltopdf", "--enable-local-file-access", str(html_path), str(pdf_path)],
                capture_output=True,
                timeout=60
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
        
        try:
            # Try Chrome headless
            result = subprocess.run(
                [
                    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                    "--headless",
                    "--disable-gpu",
                    f"--print-to-pdf={pdf_path}",
                    str(html_path)
                ],
                capture_output=True,
                timeout=60
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
        
        return False
    
    def generate_document(
        self,
        partner_id: str,
        document_type: str,
        output_format: str = "both"
    ) -> Dict[str, Any]:
        """
        Generate a personalized document for a partner
        
        Args:
            partner_id: Partner ID
            document_type: nda, service_agreement, baa, or coi_request
            output_format: html, pdf, or both
            
        Returns:
            Dict with file paths and status
        """
        partners = self._load_partners()
        if partner_id not in partners:
            return {"success": False, "error": f"Partner not found: {partner_id}"}
        
        partner = partners[partner_id]
        
        if document_type not in AGREEMENT_TEMPLATES:
            return {"success": False, "error": f"Unknown document type: {document_type}"}
        
        template_path = AGREEMENT_TEMPLATES[document_type]
        if not template_path.exists():
            return {"success": False, "error": f"Template not found: {template_path}"}
        
        # Create output directory for this partner
        partner_dir = HAVEN_BASE / "GENERATED" / partner_id
        partner_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate personalized HTML
        html_content = self._personalize_document(template_path, partner)
        
        doc_names = {
            "nda": "HAVEN_NDA",
            "service_agreement": "HAVEN_Service_Agreement",
            "baa": "HAVEN_BAA",
            "coi_request": "HAVEN_COI_Request",
        }
        doc_name = doc_names[document_type]
        
        html_path = partner_dir / f"{doc_name}_{partner.company_name.replace(' ', '_')}.html"
        pdf_path = partner_dir / f"{doc_name}_{partner.company_name.replace(' ', '_')}.pdf"
        
        result = {
            "success": True,
            "partner_id": partner_id,
            "document_type": document_type,
            "files": {}
        }
        
        # Save HTML
        if output_format in ["html", "both"]:
            with open(html_path, 'w') as f:
                f.write(html_content)
            result["files"]["html"] = str(html_path)
        
        # Generate PDF
        if output_format in ["pdf", "both"]:
            # First save HTML for PDF conversion
            temp_html = partner_dir / f"_temp_{doc_name}.html"
            with open(temp_html, 'w') as f:
                f.write(html_content)
            
            if self._html_to_pdf(temp_html, pdf_path):
                result["files"]["pdf"] = str(pdf_path)
            else:
                result["pdf_warning"] = "PDF generation failed. HTML file available."
            
            # Clean up temp file
            if temp_html.exists():
                temp_html.unlink()
        
        return result
    
    def generate_onboarding_package(self, partner_id: str) -> Dict[str, Any]:
        """
        Generate all required documents for a partner
        
        Returns dict with all generated files organized by document type
        """
        partners = self._load_partners()
        if partner_id not in partners:
            return {"success": False, "error": f"Partner not found: {partner_id}"}
        
        partner = partners[partner_id]
        required_docs = PARTNER_REQUIREMENTS[partner.partner_type]["documents"]
        
        results = {
            "success": True,
            "partner_id": partner_id,
            "partner_name": partner.company_name,
            "partner_type": partner.partner_type,
            "documents": {}
        }
        
        for doc_type in required_docs:
            doc_result = self.generate_document(partner_id, doc_type, "both")
            results["documents"][doc_type] = doc_result
            if not doc_result.get("success"):
                results["success"] = False
        
        return results
    
    # =========================================================================
    # DOCUMENT DELIVERY
    # =========================================================================
    
    def _send_email(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        attachments: List[Dict[str, str]] = None,
        cc: str = None
    ) -> Dict[str, Any]:
        """
        Send email via SendGrid
        
        Attachments format: [{"filename": "doc.pdf", "content_base64": "..."}]
        """
        try:
            import sendgrid
            from sendgrid.helpers.mail import (
                Mail, Email, To, Content, Attachment, 
                FileContent, FileName, FileType, Disposition, Cc
            )
        except ImportError:
            return {"success": False, "error": "sendgrid not installed", "skipped": True}
        
        api_key = os.environ.get("SENDGRID_API_KEY")
        from_email = os.environ.get("SENDGRID_FROM_EMAIL", "info@deedavis.biz")
        
        if not api_key:
            return {"success": False, "error": "SENDGRID_API_KEY not configured", "skipped": True}
        
        try:
            sg = sendgrid.SendGridAPIClient(api_key=api_key)
            
            message = Mail(
                from_email=Email(from_email, "Dee Davis Inc"),
                to_emails=To(to_email),
                subject=subject,
                html_content=Content("text/html", html_body)
            )
            
            if cc:
                message.cc = Cc(cc)
            
            # Add attachments
            if attachments:
                for att in attachments:
                    attachment = Attachment(
                        FileContent(att["content_base64"]),
                        FileName(att["filename"]),
                        FileType(att.get("type", "application/pdf")),
                        Disposition("attachment")
                    )
                    message.add_attachment(attachment)
            
            response = sg.send(message)
            
            return {
                "success": response.status_code in [200, 201, 202],
                "status_code": response.status_code,
                "channel": "email"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e), "channel": "email"}
    
    def _get_email_template(self, document_type: str, partner: HAVENPartner) -> Dict[str, str]:
        """Get email subject and body for each document type"""
        
        templates = {
            "nda": {
                "subject": f"HAVEN Partner NDA — {partner.company_name}",
                "body": f"""
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <h2 style="color: #1e3a5f;">HAVEN Partnership — Non-Disclosure Agreement</h2>
                    
                    <p>Dear {partner.contact_name},</p>
                    
                    <p>Thank you for your interest in joining the HAVEN Disaster Response Network. 
                    As a first step in our partnership process, please review and sign the attached 
                    Non-Disclosure Agreement.</p>
                    
                    <p>This NDA protects both parties and our MCO clients during the partnership 
                    evaluation process.</p>
                    
                    <p><strong>Next Steps:</strong></p>
                    <ol>
                        <li>Review the attached NDA</li>
                        <li>Sign and return to <a href="mailto:info@deedavis.biz">info@deedavis.biz</a></li>
                        <li>Once received, we'll send the full Partner Service Agreement</li>
                    </ol>
                    
                    <p>If you have any questions, please don't hesitate to reach out.</p>
                    
                    <p>Best regards,<br/>
                    <strong>Dieasha D. Davis</strong><br/>
                    President & CEO<br/>
                    Dee Davis Inc.<br/>
                    248.376.4550 | info@deedavis.biz</p>
                </div>
                """
            },
            "service_agreement": {
                "subject": f"HAVEN Partner Service Agreement — {partner.company_name}",
                "body": f"""
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <h2 style="color: #1e3a5f;">HAVEN Partnership — Service Agreement</h2>
                    
                    <p>Dear {partner.contact_name},</p>
                    
                    <p>Thank you for signing the NDA. Attached is the HAVEN Partner Service Agreement 
                    for {partner.company_name}.</p>
                    
                    <p>This comprehensive agreement covers:</p>
                    <ul>
                        <li>Scope of services for {partner.partner_type} partners</li>
                        <li>Service level standards and disaster activation protocols</li>
                        <li>Compensation and payment terms</li>
                        <li>Insurance and compliance requirements</li>
                        <li>Quality assurance and performance metrics</li>
                    </ul>
                    
                    <p><strong>Next Steps:</strong></p>
                    <ol>
                        <li>Review the Service Agreement carefully</li>
                        <li>Sign and return to <a href="mailto:info@deedavis.biz">info@deedavis.biz</a></li>
                        <li>We'll then send the HIPAA Business Associate Agreement</li>
                    </ol>
                    
                    <p>Best regards,<br/>
                    <strong>Dieasha D. Davis</strong><br/>
                    President & CEO<br/>
                    Dee Davis Inc.<br/>
                    248.376.4550 | info@deedavis.biz</p>
                </div>
                """
            },
            "baa": {
                "subject": f"HAVEN HIPAA Business Associate Agreement — {partner.company_name}",
                "body": f"""
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <h2 style="color: #1e3a5f;">HAVEN Partnership — Business Associate Agreement</h2>
                    
                    <p>Dear {partner.contact_name},</p>
                    
                    <p>As a HAVEN partner handling Protected Health Information (PHI), HIPAA requires 
                    a Business Associate Agreement between our organizations.</p>
                    
                    <p>This BAA establishes:</p>
                    <ul>
                        <li>Permitted uses of PHI</li>
                        <li>Required safeguards (administrative, physical, technical)</li>
                        <li>Breach notification procedures</li>
                        <li>Compliance with HIPAA regulations</li>
                    </ul>
                    
                    <p><strong>Next Steps:</strong></p>
                    <ol>
                        <li>Review and sign the attached BAA</li>
                        <li>Return to <a href="mailto:info@deedavis.biz">info@deedavis.biz</a></li>
                        <li>We'll then send the Certificate of Insurance request</li>
                    </ol>
                    
                    <p>Best regards,<br/>
                    <strong>Dieasha D. Davis</strong><br/>
                    President & CEO<br/>
                    Dee Davis Inc.<br/>
                    248.376.4550 | info@deedavis.biz</p>
                </div>
                """
            },
            "coi_request": {
                "subject": f"HAVEN Partner COI Request — {partner.company_name}",
                "body": f"""
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <h2 style="color: #1e3a5f;">HAVEN Partnership — Certificate of Insurance Request</h2>
                    
                    <p>Dear {partner.contact_name},</p>
                    
                    <p>We're almost there! The final step before activating {partner.company_name} 
                    as a HAVEN partner is providing proof of insurance.</p>
                    
                    <p>Please see the attached COI Request form which details:</p>
                    <ul>
                        <li>Required coverage types for {partner.partner_type} partners</li>
                        <li>Minimum coverage limits</li>
                        <li>Additional insured requirements (Dee Davis Inc must be listed)</li>
                    </ul>
                    
                    <p><strong>To Complete:</strong></p>
                    <ol>
                        <li>Forward the attached form to your insurance agent</li>
                        <li>Have them issue a COI naming Dee Davis Inc as Additional Insured</li>
                        <li>Send the COI to <a href="mailto:info@deedavis.biz">info@deedavis.biz</a></li>
                    </ol>
                    
                    <p>Once we receive your COI, we'll complete credentialing and activate your 
                    partnership!</p>
                    
                    <p>Best regards,<br/>
                    <strong>Dieasha D. Davis</strong><br/>
                    President & CEO<br/>
                    Dee Davis Inc.<br/>
                    248.376.4550 | info@deedavis.biz</p>
                </div>
                """
            },
        }
        
        return templates.get(document_type, {
            "subject": f"HAVEN Partnership Document — {partner.company_name}",
            "body": f"<p>Dear {partner.contact_name},</p><p>Please see attached document.</p>"
        })
    
    def send_document(
        self,
        partner_id: str,
        document_type: str,
        cc_dee: bool = True
    ) -> Dict[str, Any]:
        """
        Send a document to a partner via email
        
        Args:
            partner_id: Partner ID
            document_type: nda, service_agreement, baa, or coi_request
            cc_dee: Whether to CC info@deedavis.biz
            
        Returns:
            Delivery result
        """
        partners = self._load_partners()
        if partner_id not in partners:
            return {"success": False, "error": f"Partner not found: {partner_id}"}
        
        partner = partners[partner_id]
        
        # Generate the document first
        gen_result = self.generate_document(partner_id, document_type, "pdf")
        if not gen_result.get("success"):
            return {"success": False, "error": f"Document generation failed: {gen_result}"}
        
        # Get PDF path
        pdf_path = gen_result.get("files", {}).get("pdf")
        if not pdf_path or not Path(pdf_path).exists():
            return {"success": False, "error": "PDF not generated"}
        
        # Read PDF and encode
        with open(pdf_path, "rb") as f:
            pdf_content = base64.b64encode(f.read()).decode()
        
        # Get email template
        email_template = self._get_email_template(document_type, partner)
        
        # Send email
        result = self._send_email(
            to_email=partner.contact_email,
            subject=email_template["subject"],
            html_body=email_template["body"],
            attachments=[{
                "filename": Path(pdf_path).name,
                "content_base64": pdf_content,
                "type": "application/pdf"
            }],
            cc="info@deedavis.biz" if cc_dee else None
        )
        
        # Update partner status
        if result.get("success"):
            status_map = {
                "nda": ("nda_sent", OnboardingStatus.NDA_SENT),
                "service_agreement": ("agreement_sent", OnboardingStatus.AGREEMENT_SENT),
                "baa": ("baa_sent", OnboardingStatus.BAA_SENT),
                "coi_request": ("coi_requested", OnboardingStatus.COI_REQUESTED),
            }
            
            date_field, new_status = status_map.get(document_type, (None, None))
            if date_field:
                setattr(partner, f"{date_field}_date", datetime.now().isoformat())
                partner.status = new_status.value
                partner.updated_at = datetime.now().isoformat()
                partners[partner_id] = partner
                self._save_partners(partners)
                
                # Copy to SENT folder
                sent_dir = HAVEN_BASE / "SENT" / partner_id
                sent_dir.mkdir(parents=True, exist_ok=True)
                import shutil
                shutil.copy2(pdf_path, sent_dir / f"{Path(pdf_path).name}")
        
        result["partner_id"] = partner_id
        result["document_type"] = document_type
        result["sent_to"] = partner.contact_email
        
        return result
    
    def send_onboarding_sequence(self, partner_id: str) -> Dict[str, Any]:
        """
        Start the full onboarding sequence (sends NDA first)
        
        The sequence is:
        1. NDA → wait for signature
        2. Service Agreement → wait for signature  
        3. BAA → wait for signature
        4. COI Request → wait for COI
        5. Credentialing → activation
        
        This sends the NDA. Use advance_onboarding() after each signature.
        """
        return self.send_document(partner_id, "nda")
    
    def advance_onboarding(self, partner_id: str, signed_document: str) -> Dict[str, Any]:
        """
        Mark a document as signed and send the next one
        
        Args:
            partner_id: Partner ID
            signed_document: Which document was signed (nda, service_agreement, baa)
            
        Returns:
            Result of next document send
        """
        partners = self._load_partners()
        if partner_id not in partners:
            return {"success": False, "error": f"Partner not found: {partner_id}"}
        
        partner = partners[partner_id]
        
        # Mark as signed and determine next step
        sequence = {
            "nda": ("nda_signed", "service_agreement"),
            "service_agreement": ("agreement_signed", "baa"),
            "baa": ("baa_signed", "coi_request"),
            "coi_request": ("coi_received", None),  # End of document sequence
        }
        
        if signed_document not in sequence:
            return {"success": False, "error": f"Unknown document: {signed_document}"}
        
        signed_field, next_doc = sequence[signed_document]
        
        # Update signed status
        setattr(partner, f"{signed_field}_date", datetime.now().isoformat())
        
        # Update status enum
        status_after_sign = {
            "nda_signed": OnboardingStatus.NDA_SIGNED,
            "agreement_signed": OnboardingStatus.AGREEMENT_SIGNED,
            "baa_signed": OnboardingStatus.BAA_SIGNED,
            "coi_received": OnboardingStatus.CREDENTIALING,
        }
        partner.status = status_after_sign[signed_field].value
        partner.updated_at = datetime.now().isoformat()
        partners[partner_id] = partner
        self._save_partners(partners)
        
        result = {
            "success": True,
            "partner_id": partner_id,
            "signed": signed_document,
            "status": partner.status,
        }
        
        # Send next document if there is one
        if next_doc:
            send_result = self.send_document(partner_id, next_doc)
            result["next_document"] = next_doc
            result["send_result"] = send_result
        else:
            result["message"] = "All documents complete. Ready for credentialing."
        
        return result
    
    def activate_partner(self, partner_id: str) -> Dict[str, Any]:
        """
        Activate a partner after credentialing is complete
        """
        partners = self._load_partners()
        if partner_id not in partners:
            return {"success": False, "error": f"Partner not found: {partner_id}"}
        
        partner = partners[partner_id]
        
        # Verify all required steps are complete
        required_dates = [
            partner.nda_signed_date,
            partner.agreement_signed_date,
            partner.baa_signed_date,
            partner.coi_received_date,
        ]
        
        if not all(required_dates):
            missing = []
            if not partner.nda_signed_date: missing.append("NDA")
            if not partner.agreement_signed_date: missing.append("Service Agreement")
            if not partner.baa_signed_date: missing.append("BAA")
            if not partner.coi_received_date: missing.append("COI")
            return {
                "success": False,
                "error": f"Cannot activate. Missing: {', '.join(missing)}"
            }
        
        partner.status = OnboardingStatus.ACTIVE.value
        partner.activation_date = datetime.now().isoformat()
        partner.updated_at = datetime.now().isoformat()
        partners[partner_id] = partner
        self._save_partners(partners)
        
        return {
            "success": True,
            "partner_id": partner_id,
            "company_name": partner.company_name,
            "status": "active",
            "activation_date": partner.activation_date,
            "message": f"{partner.company_name} is now an active HAVEN partner!"
        }
    
    # =========================================================================
    # STATUS & REPORTING
    # =========================================================================
    
    def get_partner_status(self, partner_id: str) -> Dict[str, Any]:
        """Get full status of a partner"""
        partners = self._load_partners()
        if partner_id not in partners:
            return {"success": False, "error": f"Partner not found: {partner_id}"}
        
        partner = partners[partner_id]
        return {
            "success": True,
            **asdict(partner)
        }
    
    def get_onboarding_dashboard(self) -> Dict[str, Any]:
        """Get dashboard of all partners by status"""
        partners = self._load_partners()
        
        by_status = {}
        for partner in partners.values():
            status = partner.status
            if status not in by_status:
                by_status[status] = []
            by_status[status].append({
                "partner_id": partner.partner_id,
                "company_name": partner.company_name,
                "partner_type": partner.partner_type,
                "contact_email": partner.contact_email,
                "updated_at": partner.updated_at,
            })
        
        return {
            "total_partners": len(partners),
            "by_status": by_status,
            "status_counts": {k: len(v) for k, v in by_status.items()},
        }
    
    def get_pending_reminders(self, days_threshold: int = 2) -> List[Dict[str, Any]]:
        """Get partners who need follow-up (no response after X days)"""
        partners = self._load_partners()
        threshold = datetime.now() - timedelta(days=days_threshold)
        
        reminders = []
        for partner in partners.values():
            # Check each stage for stale documents
            checks = [
                (partner.nda_sent_date, partner.nda_signed_date, "NDA"),
                (partner.agreement_sent_date, partner.agreement_signed_date, "Service Agreement"),
                (partner.baa_sent_date, partner.baa_signed_date, "BAA"),
                (partner.coi_requested_date, partner.coi_received_date, "COI"),
            ]
            
            for sent_date, signed_date, doc_name in checks:
                if sent_date and not signed_date:
                    sent_dt = datetime.fromisoformat(sent_date)
                    if sent_dt < threshold:
                        days_waiting = (datetime.now() - sent_dt).days
                        reminders.append({
                            "partner_id": partner.partner_id,
                            "company_name": partner.company_name,
                            "contact_email": partner.contact_email,
                            "document": doc_name,
                            "sent_date": sent_date,
                            "days_waiting": days_waiting,
                        })
        
        return reminders


# =============================================================================
# FLASK API ROUTES (add to api_server.py)
# =============================================================================

def create_haven_onboarding_routes(app, airtable_client=None):
    """
    Create Flask routes for HAVEN partner onboarding
    
    Add to api_server.py:
        from haven_partner_onboarding import create_haven_onboarding_routes
        create_haven_onboarding_routes(app, airtable)
    """
    from flask import request, jsonify
    
    onboarding = HAVENPartnerOnboarding(airtable_client)
    
    @app.route('/api/haven/partners', methods=['POST'])
    def haven_register_partner():
        """Register a new HAVEN partner"""
        data = request.json or {}
        try:
            partner = onboarding.register_partner(
                company_name=data.get('company_name', ''),
                contact_name=data.get('contact_name', ''),
                contact_email=data.get('contact_email', ''),
                contact_phone=data.get('contact_phone', ''),
                partner_type=data.get('partner_type', ''),
                service_areas=data.get('service_areas', []),
                notes=data.get('notes', ''),
            )
            return jsonify({"success": True, "partner": asdict(partner)})
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 400
    
    @app.route('/api/haven/partners/<partner_id>', methods=['GET'])
    def haven_get_partner(partner_id):
        """Get partner status"""
        return jsonify(onboarding.get_partner_status(partner_id))
    
    @app.route('/api/haven/partners/<partner_id>/generate', methods=['POST'])
    def haven_generate_docs(partner_id):
        """Generate all onboarding documents"""
        return jsonify(onboarding.generate_onboarding_package(partner_id))
    
    @app.route('/api/haven/partners/<partner_id>/send/<doc_type>', methods=['POST'])
    def haven_send_document(partner_id, doc_type):
        """Send a specific document"""
        return jsonify(onboarding.send_document(partner_id, doc_type))
    
    @app.route('/api/haven/partners/<partner_id>/start-onboarding', methods=['POST'])
    def haven_start_onboarding(partner_id):
        """Start onboarding sequence (sends NDA)"""
        return jsonify(onboarding.send_onboarding_sequence(partner_id))
    
    @app.route('/api/haven/partners/<partner_id>/advance', methods=['POST'])
    def haven_advance_onboarding(partner_id):
        """Mark document signed and send next"""
        data = request.json or {}
        signed_doc = data.get('signed_document', '')
        return jsonify(onboarding.advance_onboarding(partner_id, signed_doc))
    
    @app.route('/api/haven/partners/<partner_id>/activate', methods=['POST'])
    def haven_activate_partner(partner_id):
        """Activate a partner"""
        return jsonify(onboarding.activate_partner(partner_id))
    
    @app.route('/api/haven/dashboard', methods=['GET'])
    def haven_dashboard():
        """Get onboarding dashboard"""
        return jsonify(onboarding.get_onboarding_dashboard())
    
    @app.route('/api/haven/reminders', methods=['GET'])
    def haven_reminders():
        """Get pending follow-up reminders"""
        days = request.args.get('days', 2, type=int)
        return jsonify({"reminders": onboarding.get_pending_reminders(days)})
    
    print("✅ HAVEN Partner Onboarding routes registered")


# =============================================================================
# CLI
# =============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="HAVEN Partner Onboarding System")
    parser.add_argument("command", choices=[
        "register", "status", "generate", "send", "advance", "activate", "dashboard", "reminders"
    ])
    parser.add_argument("--partner-id", "-p", help="Partner ID")
    parser.add_argument("--company", help="Company name (for register)")
    parser.add_argument("--contact", help="Contact name (for register)")
    parser.add_argument("--email", help="Contact email (for register)")
    parser.add_argument("--phone", help="Contact phone (for register)")
    parser.add_argument("--type", choices=["housing", "transport", "medical"], help="Partner type")
    parser.add_argument("--areas", nargs="+", help="Service areas (states)")
    parser.add_argument("--doc", choices=["nda", "service_agreement", "baa", "coi_request"], help="Document type")
    parser.add_argument("--days", type=int, default=2, help="Days threshold for reminders")
    
    args = parser.parse_args()
    onboarding = HAVENPartnerOnboarding()
    
    if args.command == "register":
        partner = onboarding.register_partner(
            company_name=args.company or input("Company name: "),
            contact_name=args.contact or input("Contact name: "),
            contact_email=args.email or input("Contact email: "),
            contact_phone=args.phone or input("Contact phone: "),
            partner_type=args.type or input("Partner type (housing/transport/medical): "),
            service_areas=args.areas or input("Service areas (comma-separated states): ").split(","),
        )
        print(f"\n✅ Registered: {partner.partner_id}")
        print(json.dumps(asdict(partner), indent=2))
    
    elif args.command == "status":
        result = onboarding.get_partner_status(args.partner_id)
        print(json.dumps(result, indent=2))
    
    elif args.command == "generate":
        result = onboarding.generate_onboarding_package(args.partner_id)
        print(json.dumps(result, indent=2))
    
    elif args.command == "send":
        result = onboarding.send_document(args.partner_id, args.doc)
        print(json.dumps(result, indent=2))
    
    elif args.command == "advance":
        result = onboarding.advance_onboarding(args.partner_id, args.doc)
        print(json.dumps(result, indent=2))
    
    elif args.command == "activate":
        result = onboarding.activate_partner(args.partner_id)
        print(json.dumps(result, indent=2))
    
    elif args.command == "dashboard":
        result = onboarding.get_onboarding_dashboard()
        print(json.dumps(result, indent=2))
    
    elif args.command == "reminders":
        reminders = onboarding.get_pending_reminders(args.days)
        print(f"\n📬 Partners waiting {args.days}+ days for response:\n")
        for r in reminders:
            print(f"  • {r['company_name']} — {r['document']} sent {r['days_waiting']} days ago")
        if not reminders:
            print("  No pending reminders!")
