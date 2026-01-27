"""
NEXUS Supplier Quote Workflow
Complete automation: Solicitation → Supplier → Quote → Follow-up
"""

from pyairtable import Api
import json
import subprocess
import os
from datetime import datetime, timedelta
from pathlib import Path
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication


class SupplierQuoteWorkflow:
    """
    Complete workflow for requesting supplier quotes from solicitations
    
    Workflow:
    1. Solicitation found → Extract items
    2. Match suppliers for items
    3. Generate quote request PDF
    4. Send to suppliers (email/fax)
    5. Log to Airtable with timestamp
    6. Auto-generate follow-up if no response
    """
    
    def __init__(self, airtable_key, base_id):
        self.api = Api(airtable_key)
        self.base_id = base_id
        self.opportunities_table = self.api.table(base_id, 'Opportunities')
        self.suppliers_table = self.api.table(base_id, 'Suppliers')
        self.quote_requests_table = self.api.table(base_id, 'Quote Requests')
        
    
    def process_solicitation(self, opportunity_id):
        """
        Process a solicitation and generate supplier quote requests
        
        Args:
            opportunity_id: Airtable record ID for the opportunity
            
        Returns:
            dict: Status and generated quote request IDs
        """
        # Get opportunity details
        opportunity = self.opportunities_table.get(opportunity_id)
        
        # Extract items from solicitation
        items = self._extract_items(opportunity)
        
        # Find matching suppliers
        suppliers = self._match_suppliers(items)
        
        # Generate quote request for each supplier
        quote_requests = []
        
        for supplier in suppliers:
            # Generate PDF
            pdf_path = self._generate_quote_pdf(opportunity, items, supplier)
            
            # Send to supplier
            sent = self._send_to_supplier(supplier, pdf_path)
            
            # Log to Airtable
            quote_request = self._log_quote_request(
                opportunity_id=opportunity_id,
                supplier_id=supplier['id'],
                pdf_path=pdf_path,
                sent=sent
            )
            
            quote_requests.append(quote_request)
            
            # Schedule follow-up
            self._schedule_followup(quote_request['id'], days=3)
        
        return {
            'success': True,
            'opportunity_id': opportunity_id,
            'quote_requests': quote_requests
        }
    
    
    def _extract_items(self, opportunity):
        """Extract items from opportunity/solicitation"""
        # Parse items from opportunity description or structured fields
        items = []
        
        # If items are already structured
        if 'Items' in opportunity['fields']:
            return opportunity['fields']['Items']
        
        # TODO: Use Claude to extract items from description
        # For now, return empty list
        return items
    
    
    def _match_suppliers(self, items):
        """
        Find matching suppliers for the items
        
        Args:
            items: List of item dicts with categories/descriptions
            
        Returns:
            list: Matching supplier records
        """
        suppliers = []
        
        # Get all active suppliers
        all_suppliers = self.suppliers_table.all()
        
        # TODO: Smart matching based on:
        # - Product categories
        # - Past performance
        # - Geographic location
        # - Pricing history
        
        # For now, return top 3-5 suppliers
        return all_suppliers[:5]
    
    
    def _generate_quote_pdf(self, opportunity, items, supplier):
        """
        Generate quote request PDF
        
        Args:
            opportunity: Airtable opportunity record
            items: List of items to quote
            supplier: Supplier record
            
        Returns:
            str: Path to generated PDF
        """
        # Build quote data
        opp_fields = opportunity['fields']
        
        # Create RFQ number
        rfq_number = f"DDI-{datetime.now().strftime('%Y')}-{opportunity['id'][:6].upper()}"
        
        # Calculate due date (before opportunity deadline)
        opp_deadline = opp_fields.get('Deadline', '')
        # Give suppliers 1 week, or half the time until deadline
        due_date = (datetime.now() + timedelta(days=7)).strftime('%B %d, %Y')
        
        quote_template = f"""RFQ_NUMBER: {rfq_number}
TITLE: {opp_fields.get('Title', 'Quote Request')}
ISSUE_DATE: {datetime.now().strftime('%B %d, %Y')}
DUE_DATE: {due_date}
DUE_TIME: 5:00 PM EST
CONTRACT_PERIOD: {opp_fields.get('Contract Period', '12 months')}

COLOR_SCHEME: 1

INTRODUCTION:
DEE DAVIS INC is preparing a bid for a Michigan municipal client. We need competitive quotes for the items listed below by {due_date}.

SCOPE:
Vendor will provide materials/services as specified. Delivery to Southeast Michigan location. This is a competitive opportunity and we need your best pricing.

KEY_REQUIREMENTS:
- Competitive pricing required
- Confirm availability and lead times
- Provide delivery terms
- Net 30 payment terms preferred

ITEMS:
"""
        
        # Add items
        for idx, item in enumerate(items, 1):
            quote_template += f"{idx} | {item.get('description', '')} | {item.get('specifications', '')} | {item.get('quantity', '')} | {item.get('unit', 'unit')}\n"
        
        # Save template to temp file
        temp_file = f"/tmp/quote_{rfq_number}.txt"
        with open(temp_file, 'w') as f:
            f.write(quote_template)
        
        # Generate PDF
        result = subprocess.run(
            ['python3', 'create_from_paste.py', 'rfq', temp_file],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        
        # Find generated PDF
        output_dir = Path("GENERATED_QUOTES")
        pdf_files = list(output_dir.glob(f"rfq_{rfq_number.lower().replace('-', '_')}*.pdf"))
        
        if pdf_files:
            return str(pdf_files[0])
        
        return None
    
    
    def _send_to_supplier(self, supplier, pdf_path):
        """
        Send quote request to supplier via email or fax
        
        Args:
            supplier: Supplier record
            pdf_path: Path to PDF file
            
        Returns:
            dict: Sent status with timestamp and method
        """
        supplier_fields = supplier['fields']
        
        # Try email first
        email = supplier_fields.get('Email', '')
        if email:
            sent = self._send_email(email, pdf_path, supplier_fields)
            if sent:
                return {
                    'method': 'email',
                    'to': email,
                    'timestamp': datetime.now().isoformat(),
                    'success': True
                }
        
        # Try fax if no email or email failed
        fax = supplier_fields.get('Fax', '')
        if fax:
            sent = self._send_fax(fax, pdf_path)
            if sent:
                return {
                    'method': 'fax',
                    'to': fax,
                    'timestamp': datetime.now().isoformat(),
                    'success': True
                }
        
        return {
            'method': 'none',
            'success': False,
            'timestamp': datetime.now().isoformat()
        }
    
    
    def _send_email(self, to_email, pdf_path, supplier_info):
        """Send quote request via email"""
        try:
            # Email configuration from env
            smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
            smtp_port = int(os.getenv('SMTP_PORT', '587'))
            from_email = os.getenv('EMAIL_USER', 'info@deedavis.biz')
            password = os.getenv('EMAIL_PASSWORD', '')
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = from_email
            msg['To'] = to_email
            msg['Subject'] = 'Quote Request - DEE DAVIS INC'
            
            # Email body
            supplier_name = supplier_info.get('Name', 'Supplier')
            body = f"""Hello {supplier_name},

DEE DAVIS INC is preparing a bid for a Michigan municipal client and needs competitive pricing.

Please see the attached quote request for full details and specifications. We need your response by the date specified in the document.

Please include:
- Unit pricing for all items
- Delivery lead times and terms
- Payment terms
- Quote validity period

If you have any questions, please contact us at 248-376-4550.

Looking forward to your competitive quote!

Best regards,

Dee Davis
President & CEO
DEE DAVIS INC
248-376-4550
info@deedavis.biz
www.deedavis.biz
"""
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Attach PDF
            if pdf_path and os.path.exists(pdf_path):
                with open(pdf_path, 'rb') as f:
                    pdf = MIMEApplication(f.read(), _subtype='pdf')
                    pdf.add_header('Content-Disposition', 'attachment', 
                                 filename=os.path.basename(pdf_path))
                    msg.attach(pdf)
            
            # Send email
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(from_email, password)
            server.send_message(msg)
            server.quit()
            
            return True
            
        except Exception as e:
            print(f"Email error: {e}")
            return False
    
    
    def _send_fax(self, fax_number, pdf_path):
        """Send quote request via fax (integrate with fax service)"""
        # TODO: Integrate with fax service (e.g., eFax, RingCentral, Phaxio)
        # For now, log that fax would be sent
        print(f"Would send fax to {fax_number}: {pdf_path}")
        return False
    
    
    def _log_quote_request(self, opportunity_id, supplier_id, pdf_path, sent):
        """
        Log quote request to Airtable
        
        Creates a record in Quote Requests table with:
        - Link to opportunity
        - Link to supplier
        - Timestamp
        - Delivery method
        - Status
        """
        record = self.quote_requests_table.create({
            'Opportunity': [opportunity_id],
            'Supplier': [supplier_id],
            'Sent Date': datetime.now().isoformat(),
            'Sent Method': sent.get('method', 'unknown'),
            'Sent To': sent.get('to', ''),
            'Status': 'Sent' if sent.get('success') else 'Failed',
            'PDF Path': pdf_path or '',
            'Due Date': (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d'),
            'Follow-up Needed': True
        })
        
        return record
    
    
    def _schedule_followup(self, quote_request_id, days=3):
        """
        Schedule automatic follow-up if no response
        
        Args:
            quote_request_id: Record ID in Quote Requests table
            days: Days to wait before follow-up
        """
        followup_date = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d')
        
        self.quote_requests_table.update(quote_request_id, {
            'Follow-up Date': followup_date,
            'Follow-up Needed': True
        })
    
    
    def check_followups(self):
        """
        Check for quote requests needing follow-up
        
        Returns:
            list: Quote requests that need follow-up
        """
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Get quote requests needing follow-up
        formula = f"AND({{Follow-up Needed}}, {{Follow-up Date}} <= '{today}', {{Status}} = 'Sent')"
        
        records = self.quote_requests_table.all(formula=formula)
        
        return records
    
    
    def send_followup(self, quote_request_id):
        """
        Send follow-up email/fax for quote request
        
        Args:
            quote_request_id: Record ID to follow up on
        """
        record = self.quote_requests_table.get(quote_request_id)
        
        # Get supplier info
        supplier_id = record['fields']['Supplier'][0]
        supplier = self.suppliers_table.get(supplier_id)
        
        # Send follow-up
        email = supplier['fields'].get('Email', '')
        if email:
            self._send_followup_email(email, record, supplier)
        
        # Update record
        self.quote_requests_table.update(quote_request_id, {
            'Last Follow-up': datetime.now().isoformat(),
            'Follow-up Count': record['fields'].get('Follow-up Count', 0) + 1
        })
    
    
    def _send_followup_email(self, email, quote_request, supplier):
        """Send follow-up email for quote"""
        try:
            smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
            smtp_port = int(os.getenv('SMTP_PORT', '587'))
            from_email = os.getenv('EMAIL_USER', 'info@deedavis.biz')
            password = os.getenv('EMAIL_PASSWORD', '')
            
            msg = MIMEMultipart()
            msg['From'] = from_email
            msg['To'] = email
            msg['Subject'] = 'Follow-up: Quote Request - DEE DAVIS INC'
            
            supplier_name = supplier['fields'].get('Name', 'Supplier')
            sent_date = quote_request['fields'].get('Sent Date', '')
            
            body = f"""Hello {supplier_name},

Following up on our quote request sent on {sent_date}.

We need your competitive pricing to finalize our bid. If you haven't received the original request or need additional information, please let us know.

Time is of the essence on this opportunity.

Please contact us at 248-376-4550 or reply to this email.

Thank you,

Dee Davis
DEE DAVIS INC
248-376-4550
info@deedavis.biz
"""
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(from_email, password)
            server.send_message(msg)
            server.quit()
            
            return True
            
        except Exception as e:
            print(f"Follow-up email error: {e}")
            return False


# Quick usage functions
def request_quotes_for_opportunity(opportunity_id):
    """
    Main function: Request quotes from suppliers for an opportunity
    
    Usage:
        request_quotes_for_opportunity('rec123456')
    """
    workflow = SupplierQuoteWorkflow(
        airtable_key=os.getenv('AIRTABLE_API_KEY'),
        base_id=os.getenv('AIRTABLE_BASE_ID')
    )
    
    return workflow.process_solicitation(opportunity_id)


def check_and_send_followups():
    """
    Check for quote requests needing follow-up and send them
    
    Run this daily via cron job
    """
    workflow = SupplierQuoteWorkflow(
        airtable_key=os.getenv('AIRTABLE_API_KEY'),
        base_id=os.getenv('AIRTABLE_BASE_ID')
    )
    
    followups = workflow.check_followups()
    
    for record in followups:
        workflow.send_followup(record['id'])
    
    return {
        'checked': len(followups),
        'sent': len(followups)
    }


if __name__ == '__main__':
    # Test
    print("NEXUS Supplier Quote Workflow")
    print("Usage: request_quotes_for_opportunity('opportunity_id')")
