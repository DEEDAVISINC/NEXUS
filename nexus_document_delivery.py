#!/usr/bin/env python3
"""
NEXUS Document Delivery System
==============================
Central document delivery infrastructure for all NEXUS modules.

Provides:
- Email delivery via SendGrid
- PDF generation from HTML
- Document tracking and logging
- Template management
- Signature tracking (future: e-signature integration)

Each NEXUS module connects to this system for document delivery:
- HAVEN → Partner agreements, onboarding docs
- PRISM → Field agent contracts, NDAs, W9 requests
- GPSS → Buyer capability statements, proposals, RFQ responses
- DDCSS → Client proposals, pricing packages
- ATLAS → Dispatch confirmations, driver contracts
- SHIELD → Case documents, referral letters
"""

import os
import json
import base64
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict, field
from enum import Enum
import subprocess
import threading
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("nexus_document_delivery")

# Base paths
NEXUS_BASE = Path("/Users/deedavis/NEXUS BACKEND")
DELIVERY_LOG = NEXUS_BASE / "DOCUMENT_DELIVERY_LOG.json"


class DeliveryChannel(Enum):
    EMAIL = "email"
    STAGED = "staged"  # Saved to SEND_TO folder for manual send
    API = "api"  # Returned via API for frontend handling


class DeliveryStatus(Enum):
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    OPENED = "opened"
    SIGNED = "signed"
    FAILED = "failed"
    BOUNCED = "bounced"


class DocumentType(Enum):
    # HAVEN
    HAVEN_NDA = "haven_nda"
    HAVEN_SERVICE_AGREEMENT = "haven_service_agreement"
    HAVEN_BAA = "haven_baa"
    HAVEN_COI_REQUEST = "haven_coi_request"
    
    # PRISM
    PRISM_NDA = "prism_nda"
    PRISM_IC_AGREEMENT = "prism_ic_agreement"
    PRISM_W9_REQUEST = "prism_w9_request"
    PRISM_SUBCONTRACTOR_AGREEMENT = "prism_subcontractor_agreement"
    
    # GPSS
    GPSS_CAPABILITY_STATEMENT = "gpss_capability_statement"
    GPSS_QUOTE_RESPONSE = "gpss_quote_response"
    GPSS_PROPOSAL = "gpss_proposal"
    GPSS_BUYER_EMAIL = "gpss_buyer_email"
    
    # DDCSS
    DDCSS_PROPOSAL = "ddcss_proposal"
    DDCSS_PRICING = "ddcss_pricing"
    
    # ATLAS
    ATLAS_DISPATCH_CONFIRMATION = "atlas_dispatch_confirmation"
    ATLAS_DRIVER_CONTRACT = "atlas_driver_contract"
    
    # SHIELD
    SHIELD_REFERRAL = "shield_referral"
    SHIELD_CASE_DOCUMENT = "shield_case_document"


@dataclass
class DeliveryRecord:
    """Record of a document delivery"""
    delivery_id: str
    document_type: str
    recipient_email: str
    recipient_name: str
    subject: str
    channel: str
    status: str
    source_module: str  # haven, prism, gpss, etc.
    source_record_id: Optional[str] = None
    file_paths: List[str] = field(default_factory=list)
    sent_at: Optional[str] = None
    delivered_at: Optional[str] = None
    opened_at: Optional[str] = None
    signed_at: Optional[str] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = ""
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()


class NEXUSDocumentDelivery:
    """
    Central document delivery system for NEXUS
    
    Usage:
        delivery = NEXUSDocumentDelivery()
        
        # Send a document
        result = delivery.send(
            document_type="haven_nda",
            recipient_email="partner@example.com",
            recipient_name="John Doe",
            subject="HAVEN Partner NDA",
            html_body="<html>...</html>",
            attachments=[{"path": "/path/to/doc.pdf", "filename": "NDA.pdf"}],
            source_module="haven",
            source_record_id="HAVEN-TP-2605101234"
        )
        
        # Stage for manual send
        result = delivery.stage(
            folder=Path("/path/to/SEND_TO_BUYER"),
            documents=[{"path": "/path/to/cap.pdf", "filename": "cap.pdf"}],
            email_draft="Ready to send email...",
            source_module="gpss"
        )
    """
    
    def __init__(self):
        self._ensure_log_file()
        self._callbacks: Dict[str, List[Callable]] = {}
    
    def _ensure_log_file(self):
        """Ensure delivery log exists"""
        if not DELIVERY_LOG.exists():
            with open(DELIVERY_LOG, 'w') as f:
                json.dump({"deliveries": []}, f)
    
    def _load_log(self) -> Dict[str, Any]:
        """Load delivery log"""
        with open(DELIVERY_LOG) as f:
            return json.load(f)
    
    def _save_log(self, data: Dict[str, Any]):
        """Save delivery log"""
        with open(DELIVERY_LOG, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _generate_delivery_id(self, source_module: str) -> str:
        """Generate unique delivery ID"""
        prefix = source_module.upper()[:4]
        timestamp = datetime.now().strftime("%y%m%d%H%M%S")
        random_suffix = hashlib.md5(str(datetime.now().timestamp()).encode()).hexdigest()[:4]
        return f"DEL-{prefix}-{timestamp}-{random_suffix}"
    
    def _log_delivery(self, record: DeliveryRecord):
        """Log a delivery record"""
        log = self._load_log()
        log["deliveries"].append(asdict(record))
        # Keep last 1000 records
        if len(log["deliveries"]) > 1000:
            log["deliveries"] = log["deliveries"][-1000:]
        self._save_log(log)
    
    # =========================================================================
    # EMAIL DELIVERY
    # =========================================================================
    
    def _sendgrid_configured(self) -> bool:
        """Check if SendGrid is configured"""
        return bool(
            os.environ.get("SENDGRID_API_KEY") and 
            os.environ.get("SENDGRID_FROM_EMAIL")
        )
    
    def send_email(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        attachments: List[Dict[str, Any]] = None,
        cc: str = None,
        from_name: str = "Dee Davis Inc"
    ) -> Dict[str, Any]:
        """
        Send email via SendGrid
        
        Args:
            to_email: Recipient email
            subject: Email subject
            html_body: HTML email body
            attachments: List of {"path": str, "filename": str} or {"content_base64": str, "filename": str}
            cc: CC email address
            from_name: Sender name
            
        Returns:
            Delivery result dict
        """
        if not self._sendgrid_configured():
            return {
                "success": False,
                "error": "SendGrid not configured",
                "skipped": True,
                "channel": "email"
            }
        
        try:
            import sendgrid
            from sendgrid.helpers.mail import (
                Mail, Email, To, Content, Attachment,
                FileContent, FileName, FileType, Disposition, Cc
            )
        except ImportError:
            return {
                "success": False,
                "error": "sendgrid package not installed",
                "skipped": True,
                "channel": "email"
            }
        
        try:
            api_key = os.environ["SENDGRID_API_KEY"]
            from_email_addr = os.environ["SENDGRID_FROM_EMAIL"]
            
            sg = sendgrid.SendGridAPIClient(api_key=api_key)
            
            message = Mail(
                from_email=Email(from_email_addr, from_name),
                to_emails=To(to_email),
                subject=subject,
                html_content=Content("text/html", html_body)
            )
            
            if cc:
                message.cc = Cc(cc)
            
            # Add attachments
            if attachments:
                for att in attachments:
                    # Get content
                    if "content_base64" in att:
                        content = att["content_base64"]
                    elif "path" in att and Path(att["path"]).exists():
                        with open(att["path"], "rb") as f:
                            content = base64.b64encode(f.read()).decode()
                    else:
                        continue
                    
                    filename = att.get("filename", "document.pdf")
                    file_type = att.get("type", "application/pdf")
                    
                    attachment = Attachment(
                        FileContent(content),
                        FileName(filename),
                        FileType(file_type),
                        Disposition("attachment")
                    )
                    message.add_attachment(attachment)
            
            response = sg.send(message)
            
            success = response.status_code in [200, 201, 202]
            
            return {
                "success": success,
                "status_code": response.status_code,
                "channel": "email",
                "sent_at": datetime.now().isoformat() if success else None
            }
            
        except Exception as e:
            logger.error(f"SendGrid error: {e}")
            return {
                "success": False,
                "error": str(e),
                "channel": "email"
            }
    
    # =========================================================================
    # PDF GENERATION
    # =========================================================================
    
    def html_to_pdf(self, html_path: Path, pdf_path: Path) -> bool:
        """
        Convert HTML to PDF
        
        Tries multiple methods:
        1. wkhtmltopdf
        2. Chrome headless
        3. weasyprint (if installed)
        """
        # Try wkhtmltopdf
        try:
            result = subprocess.run(
                ["wkhtmltopdf", "--enable-local-file-access", 
                 "--page-size", "Letter", str(html_path), str(pdf_path)],
                capture_output=True,
                timeout=60
            )
            if result.returncode == 0:
                return True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
        
        # Try Chrome headless
        chrome_paths = [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/usr/bin/google-chrome",
            "/usr/bin/chromium-browser",
        ]
        
        for chrome in chrome_paths:
            if Path(chrome).exists():
                try:
                    result = subprocess.run(
                        [chrome, "--headless", "--disable-gpu",
                         f"--print-to-pdf={pdf_path}", str(html_path)],
                        capture_output=True,
                        timeout=60
                    )
                    if result.returncode == 0:
                        return True
                except (subprocess.TimeoutExpired, Exception):
                    continue
        
        # Try weasyprint
        try:
            from weasyprint import HTML
            HTML(filename=str(html_path)).write_pdf(str(pdf_path))
            return True
        except ImportError:
            pass
        except Exception as e:
            logger.warning(f"weasyprint failed: {e}")
        
        return False
    
    def generate_pdf_from_html_string(self, html_content: str, output_path: Path) -> bool:
        """Generate PDF from HTML string"""
        temp_html = output_path.with_suffix('.tmp.html')
        try:
            with open(temp_html, 'w') as f:
                f.write(html_content)
            return self.html_to_pdf(temp_html, output_path)
        finally:
            if temp_html.exists():
                temp_html.unlink()
    
    # =========================================================================
    # HIGH-LEVEL DELIVERY METHODS
    # =========================================================================
    
    def send(
        self,
        document_type: str,
        recipient_email: str,
        recipient_name: str,
        subject: str,
        html_body: str,
        attachments: List[Dict[str, Any]] = None,
        source_module: str = "nexus",
        source_record_id: str = None,
        cc: str = None,
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Send a document via email
        
        Args:
            document_type: Type of document (use DocumentType enum values)
            recipient_email: Recipient email address
            recipient_name: Recipient name
            subject: Email subject
            html_body: HTML email body
            attachments: List of attachments
            source_module: Which NEXUS module is sending
            source_record_id: ID of the source record (partner, opportunity, etc.)
            cc: CC email address
            metadata: Additional metadata to store
            
        Returns:
            Delivery result with delivery_id
        """
        delivery_id = self._generate_delivery_id(source_module)
        
        # Create delivery record
        record = DeliveryRecord(
            delivery_id=delivery_id,
            document_type=document_type,
            recipient_email=recipient_email,
            recipient_name=recipient_name,
            subject=subject,
            channel=DeliveryChannel.EMAIL.value,
            status=DeliveryStatus.PENDING.value,
            source_module=source_module,
            source_record_id=source_record_id,
            file_paths=[a.get("path", a.get("filename", "")) for a in (attachments or [])],
            metadata=metadata or {}
        )
        
        # Send email
        result = self.send_email(
            to_email=recipient_email,
            subject=subject,
            html_body=html_body,
            attachments=attachments,
            cc=cc
        )
        
        # Update record
        if result.get("success"):
            record.status = DeliveryStatus.SENT.value
            record.sent_at = result.get("sent_at")
        else:
            record.status = DeliveryStatus.FAILED.value
            record.error_message = result.get("error")
        
        # Log delivery
        self._log_delivery(record)
        
        # Trigger callbacks
        self._trigger_callbacks("on_send", record, result)
        
        return {
            "success": result.get("success", False),
            "delivery_id": delivery_id,
            "status": record.status,
            "error": result.get("error"),
            "channel": "email"
        }
    
    def stage(
        self,
        folder: Path,
        documents: List[Dict[str, Any]],
        email_draft: str = None,
        source_module: str = "nexus",
        source_record_id: str = None,
        recipient_email: str = None,
        recipient_name: str = None,
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Stage documents for manual send (copy to SEND_TO folder)
        
        Args:
            folder: Destination folder (e.g., SEND_TO_BUYER)
            documents: List of {"path": str, "filename": str}
            email_draft: Email draft text to save
            source_module: Which NEXUS module is staging
            source_record_id: ID of the source record
            recipient_email: Intended recipient email
            recipient_name: Intended recipient name
            metadata: Additional metadata
            
        Returns:
            Staging result
        """
        import shutil
        
        delivery_id = self._generate_delivery_id(source_module)
        folder.mkdir(parents=True, exist_ok=True)
        
        copied_files = []
        
        # Copy documents
        for doc in documents:
            src_path = Path(doc["path"])
            if src_path.exists():
                dest_path = folder / doc.get("filename", src_path.name)
                shutil.copy2(src_path, dest_path)
                copied_files.append(str(dest_path))
        
        # Save email draft
        if email_draft:
            email_path = folder / "SEND_TO_BUYER_EMAIL_READY.md"
            with open(email_path, 'w') as f:
                f.write(email_draft)
            copied_files.append(str(email_path))
        
        # Create delivery record
        record = DeliveryRecord(
            delivery_id=delivery_id,
            document_type="staged_package",
            recipient_email=recipient_email or "",
            recipient_name=recipient_name or "",
            subject="Staged for manual send",
            channel=DeliveryChannel.STAGED.value,
            status=DeliveryStatus.PENDING.value,
            source_module=source_module,
            source_record_id=source_record_id,
            file_paths=copied_files,
            metadata=metadata or {}
        )
        
        self._log_delivery(record)
        
        return {
            "success": True,
            "delivery_id": delivery_id,
            "folder": str(folder),
            "files": copied_files,
            "channel": "staged"
        }
    
    # =========================================================================
    # STATUS TRACKING
    # =========================================================================
    
    def update_status(
        self,
        delivery_id: str,
        new_status: str,
        timestamp: str = None
    ) -> Dict[str, Any]:
        """Update delivery status (e.g., mark as signed)"""
        log = self._load_log()
        
        for record in log["deliveries"]:
            if record["delivery_id"] == delivery_id:
                record["status"] = new_status
                
                timestamp = timestamp or datetime.now().isoformat()
                if new_status == DeliveryStatus.DELIVERED.value:
                    record["delivered_at"] = timestamp
                elif new_status == DeliveryStatus.OPENED.value:
                    record["opened_at"] = timestamp
                elif new_status == DeliveryStatus.SIGNED.value:
                    record["signed_at"] = timestamp
                
                self._save_log(log)
                
                # Trigger callbacks
                self._trigger_callbacks(f"on_{new_status}", DeliveryRecord(**record), {})
                
                return {"success": True, "delivery_id": delivery_id, "status": new_status}
        
        return {"success": False, "error": f"Delivery not found: {delivery_id}"}
    
    def get_delivery(self, delivery_id: str) -> Optional[Dict[str, Any]]:
        """Get delivery record by ID"""
        log = self._load_log()
        for record in log["deliveries"]:
            if record["delivery_id"] == delivery_id:
                return record
        return None
    
    def get_deliveries_by_module(
        self,
        source_module: str,
        status: str = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get deliveries for a module"""
        log = self._load_log()
        
        results = [
            r for r in log["deliveries"]
            if r["source_module"] == source_module
            and (status is None or r["status"] == status)
        ]
        
        return results[-limit:]
    
    def get_pending_signatures(self, days_threshold: int = 2) -> List[Dict[str, Any]]:
        """Get deliveries waiting for signature"""
        log = self._load_log()
        threshold = datetime.now() - timedelta(days=days_threshold)
        
        pending = []
        for record in log["deliveries"]:
            if record["status"] == DeliveryStatus.SENT.value:
                sent_at = record.get("sent_at")
                if sent_at:
                    sent_dt = datetime.fromisoformat(sent_at)
                    if sent_dt < threshold:
                        days_waiting = (datetime.now() - sent_dt).days
                        record["days_waiting"] = days_waiting
                        pending.append(record)
        
        return pending
    
    # =========================================================================
    # CALLBACKS
    # =========================================================================
    
    def register_callback(self, event: str, callback: Callable):
        """
        Register a callback for delivery events
        
        Events:
        - on_send: Called after document is sent
        - on_delivered: Called when delivery confirmed
        - on_opened: Called when document is opened
        - on_signed: Called when document is signed
        """
        if event not in self._callbacks:
            self._callbacks[event] = []
        self._callbacks[event].append(callback)
    
    def _trigger_callbacks(self, event: str, record: DeliveryRecord, result: Dict[str, Any]):
        """Trigger callbacks for an event"""
        for callback in self._callbacks.get(event, []):
            try:
                callback(record, result)
            except Exception as e:
                logger.error(f"Callback error for {event}: {e}")
    
    # =========================================================================
    # REPORTING
    # =========================================================================
    
    def get_delivery_stats(self) -> Dict[str, Any]:
        """Get delivery statistics"""
        log = self._load_log()
        
        by_module = {}
        by_status = {}
        by_channel = {}
        
        for record in log["deliveries"]:
            module = record["source_module"]
            status = record["status"]
            channel = record["channel"]
            
            by_module[module] = by_module.get(module, 0) + 1
            by_status[status] = by_status.get(status, 0) + 1
            by_channel[channel] = by_channel.get(channel, 0) + 1
        
        return {
            "total_deliveries": len(log["deliveries"]),
            "by_module": by_module,
            "by_status": by_status,
            "by_channel": by_channel
        }


# =============================================================================
# MODULE INTEGRATIONS
# =============================================================================

class ModuleDeliveryMixin:
    """
    Mixin class for NEXUS modules to integrate with document delivery
    
    Usage:
        class HAVENPartnerOnboarding(ModuleDeliveryMixin):
            MODULE_NAME = "haven"
            
            def send_nda(self, partner):
                return self.deliver_document(
                    document_type="haven_nda",
                    recipient_email=partner.email,
                    ...
                )
    """
    
    MODULE_NAME = "nexus"
    
    def __init__(self):
        self._delivery = NEXUSDocumentDelivery()
    
    def deliver_document(
        self,
        document_type: str,
        recipient_email: str,
        recipient_name: str,
        subject: str,
        html_body: str,
        attachments: List[Dict[str, Any]] = None,
        source_record_id: str = None,
        cc: str = None,
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Send a document through the central delivery system"""
        return self._delivery.send(
            document_type=document_type,
            recipient_email=recipient_email,
            recipient_name=recipient_name,
            subject=subject,
            html_body=html_body,
            attachments=attachments,
            source_module=self.MODULE_NAME,
            source_record_id=source_record_id,
            cc=cc,
            metadata=metadata
        )
    
    def stage_documents(
        self,
        folder: Path,
        documents: List[Dict[str, Any]],
        email_draft: str = None,
        source_record_id: str = None,
        recipient_email: str = None,
        recipient_name: str = None,
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Stage documents for manual send"""
        return self._delivery.stage(
            folder=folder,
            documents=documents,
            email_draft=email_draft,
            source_module=self.MODULE_NAME,
            source_record_id=source_record_id,
            recipient_email=recipient_email,
            recipient_name=recipient_name,
            metadata=metadata
        )
    
    def get_module_deliveries(self, status: str = None, limit: int = 100):
        """Get deliveries for this module"""
        return self._delivery.get_deliveries_by_module(
            self.MODULE_NAME, status, limit
        )


# =============================================================================
# FLASK API ROUTES
# =============================================================================

def create_document_delivery_routes(app):
    """
    Create Flask routes for document delivery
    
    Add to api_server.py:
        from nexus_document_delivery import create_document_delivery_routes
        create_document_delivery_routes(app)
    """
    from flask import request, jsonify
    
    delivery = NEXUSDocumentDelivery()
    
    @app.route('/api/delivery/send', methods=['POST'])
    def delivery_send():
        """Send a document via email"""
        data = request.json or {}
        return jsonify(delivery.send(**data))
    
    @app.route('/api/delivery/<delivery_id>', methods=['GET'])
    def delivery_get(delivery_id):
        """Get delivery record"""
        record = delivery.get_delivery(delivery_id)
        if record:
            return jsonify(record)
        return jsonify({"error": "Not found"}), 404
    
    @app.route('/api/delivery/<delivery_id>/status', methods=['PUT'])
    def delivery_update_status(delivery_id):
        """Update delivery status"""
        data = request.json or {}
        return jsonify(delivery.update_status(
            delivery_id,
            data.get('status'),
            data.get('timestamp')
        ))
    
    @app.route('/api/delivery/module/<module>', methods=['GET'])
    def delivery_by_module(module):
        """Get deliveries by module"""
        status = request.args.get('status')
        limit = request.args.get('limit', 100, type=int)
        return jsonify({
            "deliveries": delivery.get_deliveries_by_module(module, status, limit)
        })
    
    @app.route('/api/delivery/pending-signatures', methods=['GET'])
    def delivery_pending_signatures():
        """Get pending signatures"""
        days = request.args.get('days', 2, type=int)
        return jsonify({
            "pending": delivery.get_pending_signatures(days)
        })
    
    @app.route('/api/delivery/stats', methods=['GET'])
    def delivery_stats():
        """Get delivery statistics"""
        return jsonify(delivery.get_delivery_stats())
    
    print("✅ Document Delivery routes registered")


# =============================================================================
# CLI
# =============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="NEXUS Document Delivery System")
    parser.add_argument("command", choices=["stats", "pending", "get", "modules"])
    parser.add_argument("--delivery-id", "-d", help="Delivery ID")
    parser.add_argument("--days", type=int, default=2, help="Days threshold")
    
    args = parser.parse_args()
    delivery = NEXUSDocumentDelivery()
    
    if args.command == "stats":
        stats = delivery.get_delivery_stats()
        print(json.dumps(stats, indent=2))
    
    elif args.command == "pending":
        pending = delivery.get_pending_signatures(args.days)
        print(f"\n📬 Documents pending signature ({args.days}+ days):\n")
        for p in pending:
            print(f"  • {p['recipient_name']} — {p['document_type']} ({p['days_waiting']} days)")
        if not pending:
            print("  No pending signatures!")
    
    elif args.command == "get":
        record = delivery.get_delivery(args.delivery_id)
        print(json.dumps(record, indent=2) if record else "Not found")
    
    elif args.command == "modules":
        stats = delivery.get_delivery_stats()
        print("\n📊 Deliveries by NEXUS Module:\n")
        for module, count in stats.get("by_module", {}).items():
            print(f"  • {module.upper()}: {count}")
