#!/usr/bin/env python3
"""
NEXUS Email Automation System
Monitors inbox, extracts solicitations, sends diversity inquiries, tracks responses

Author: NEXUS AI
Created: January 25, 2026
"""

import os
import imaplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import anthropic
import json
from datetime import datetime
from pyairtable import Api
import time
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# =====================================================================
# CONFIGURATION
# =====================================================================

# Email Settings
EMAIL_ADDRESS = os.environ.get('NEXUS_EMAIL', 'bids@deedavisinc.com')
EMAIL_PASSWORD = os.environ.get('NEXUS_EMAIL_PASSWORD')
IMAP_SERVER = os.environ.get('IMAP_SERVER', 'imap.gmail.com')
SMTP_SERVER = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = 587

# Airtable Settings
AIRTABLE_API_KEY = os.environ.get('AIRTABLE_API_KEY')
AIRTABLE_BASE_ID = os.environ.get('AIRTABLE_BASE_ID')
OPPORTUNITIES_TABLE = 'GPSS OPPORTUNITIES'  # Using existing opportunities table

# Anthropic Settings
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')

# Company Info
COMPANY_NAME = "DEE DAVIS INC"
COMPANY_LOCATION = "Troy, MI 48083"
COMPANY_PHONE = "248-376-4550"
COMPANY_EMAIL = "info@deedavis.biz"
CAGE_CODE = os.environ.get('CAGE_CODE', '[YOUR CAGE CODE]')

# Thresholds for auto-inquiry
MIN_FIT_SCORE = 70  # Only send inquiry if fit score >= 70
MIN_CONTRACT_VALUE = 20000  # Only send inquiry if value >= $20K

# =====================================================================
# EMAIL MONITORING
# =====================================================================

class EmailMonitor:
    """Monitor inbox for new solicitations"""
    
    def __init__(self):
        self.imap = None
        self.connect()
        
    def connect(self):
        """Connect to email server"""
        try:
            self.imap = imaplib.IMAP4_SSL(IMAP_SERVER)
            self.imap.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            print(f"✓ Connected to {EMAIL_ADDRESS}")
        except Exception as e:
            print(f"✗ Failed to connect to email: {e}")
            raise
        
    def check_for_new_solicitations(self):
        """Check inbox for unread emails with solicitation keywords"""
        try:
            self.imap.select('INBOX')
            
            # Search for unread emails
            status, messages = self.imap.search(None, 'UNSEEN')
            email_ids = messages[0].split()
            
            print(f"Found {len(email_ids)} unread emails")
            
            solicitations = []
            
            for email_id in email_ids:
                # Fetch email
                status, msg_data = self.imap.fetch(email_id, '(RFC822)')
                email_body = msg_data[0][1]
                email_message = email.message_from_bytes(email_body)
                
                # Check if it's a solicitation
                if self.is_solicitation(email_message):
                    solicitations.append({
                        'id': email_id,
                        'message': email_message
                    })
                    print(f"  ✓ Solicitation: {email_message['subject']}")
                else:
                    # Mark as read (not a solicitation)
                    self.imap.store(email_id, '+FLAGS', '\\Seen')
                    
            return solicitations
            
        except Exception as e:
            print(f"✗ Error checking emails: {e}")
            return []
    
    def is_solicitation(self, email_message):
        """Determine if email is a bid solicitation"""
        subject = str(email_message['subject']).lower()
        body = self.get_email_body(email_message).lower()
        
        # Keywords that indicate solicitation
        keywords = [
            'rfp', 'rfq', 'rfb', 'rfi',
            'request for proposal',
            'request for quote',
            'request for bid',
            'bid opportunity',
            'solicitation',
            'invitation to bid', 'itb',
            'proposal due', 'bid due',
            'procurement',
            'notice of contract opportunity',
            'bidnet', 'sam.gov',
            'public purchasing'
        ]
        
        # Check if any keyword appears
        text_to_check = subject + " " + body[:500]  # Check subject + first 500 chars
        for keyword in keywords:
            if keyword in text_to_check:
                return True
                
        return False
    
    def get_email_body(self, email_message):
        """Extract plain text body from email"""
        try:
            if email_message.is_multipart():
                for part in email_message.walk():
                    if part.get_content_type() == "text/plain":
                        payload = part.get_payload(decode=True)
                        if payload:
                            return payload.decode(errors='ignore')
            else:
                payload = email_message.get_payload(decode=True)
                if payload:
                    return payload.decode(errors='ignore')
        except Exception as e:
            print(f"  ⚠ Warning: Could not extract email body: {e}")
            
        return ""
    
    def mark_as_processed(self, email_id):
        """Mark email as read/processed"""
        try:
            self.imap.store(email_id, '+FLAGS', '\\Seen')
        except Exception as e:
            print(f"  ⚠ Warning: Could not mark email as read: {e}")

# =====================================================================
# AI EXTRACTION
# =====================================================================

class SolicitationExtractor:
    """Use Claude to extract key information from solicitations"""
    
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        
    def extract_info(self, email_message):
        """Extract structured information from email"""
        subject = email_message['subject']
        body = self.get_email_body(email_message)
        from_address = email_message['from']
        date = email_message['date']
        
        prompt = f"""
Extract key information from this bid solicitation email and return as JSON.

EMAIL SUBJECT: {subject}
EMAIL FROM: {from_address}
EMAIL DATE: {date}

EMAIL BODY:
{body[:3000]}

Extract the following information (use null if not found):

REQUIRED FIELDS:
- solicitation_number: The RFP/RFQ/RFB number (e.g., "RFQ-2026-12345")
- title: Brief title of what's being procured (e.g., "Office Supplies")
- organization: Organization/agency name (e.g., "City of Detroit")
- deadline: Bid deadline in ISO format YYYY-MM-DDTHH:MM:SS (e.g., "2026-02-15T14:00:00")

OPTIONAL FIELDS:
- buyer_name: Procurement officer name (just first and last name)
- buyer_email: Buyer's email address
- buyer_phone: Buyer's phone number (format: (XXX) XXX-XXXX)
- estimated_value: Contract value in dollars (number only, no $ or commas)
- contract_duration: Duration (e.g., "1 year", "3 years", "2026-2029")
- location: City, State (e.g., "Detroit, MI")
- description: Brief description (1-2 sentences max)
- product_category: Category from this list ONLY: "Office Supplies", "Landscaping Materials", 
  "Janitorial Supplies", "Industrial Supplies", "Construction Materials", "Professional Services", 
  "IT Services", "Other"
- submission_method: "Email", "Portal", "Mail", "Hand Delivery", or "Other"

AI ANALYSIS FIELDS:
- fit_score: Rate 0-100 how well this matches DEE DAVIS INC capabilities
- fit_analysis: 2-3 sentences explaining the fit score
- priority_level: "HIGH", "MEDIUM", or "LOW"
- should_send_diversity_inquiry: true or false

DEE DAVIS INC PROFILE:
- Product distribution/resale (office supplies, industrial goods, janitorial)
- Landscaping materials (topsoil, grass seed, mulch, aggregates)
- Government contracting specialist
- EDWOSB/WOSB/MBE/WBE certified
- Located in Troy, Michigan (serves Michigan, Ohio, Indiana primarily)
- Ideal contract size: $20K-$500K
- Can handle larger contracts with good margins

SCORING GUIDELINES:
- HIGH fit (80-100): Perfect match, good contract size, local, likely diversity-valued
- MEDIUM fit (60-79): Good match, but some concerns (too large, too small, far away, competitive)
- LOW fit (<60): Poor match (wrong product, too far, wrong size)

Send diversity inquiry if:
- Fit score >= 70 AND
- Estimated value >= $20,000 AND
- Government/public sector contract AND
- Buyer email is available

Return ONLY valid JSON with all fields. Use null for missing data.
"""
        
        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            result = response.content[0].text
            result = result.replace('```json', '').replace('```', '').strip()
            
            extracted = json.loads(result)
            
            # Add metadata
            extracted['source_email_from'] = from_address
            extracted['source_email_date'] = date
            extracted['source_email_subject'] = subject
            
            return extracted
            
        except Exception as e:
            print(f"  ✗ AI extraction failed: {e}")
            # Return minimal data
            return {
                'solicitation_number': 'UNKNOWN',
                'title': subject[:100],
                'organization': 'Unknown',
                'fit_score': 0,
                'priority_level': 'LOW',
                'should_send_diversity_inquiry': False,
                'extraction_error': str(e)
            }
    
    def get_email_body(self, email_message):
        """Extract plain text body from email"""
        try:
            if email_message.is_multipart():
                for part in email_message.walk():
                    if part.get_content_type() == "text/plain":
                        payload = part.get_payload(decode=True)
                        if payload:
                            return payload.decode(errors='ignore')
            else:
                payload = email_message.get_payload(decode=True)
                if payload:
                    return payload.decode(errors='ignore')
        except Exception as e:
            print(f"  ⚠ Could not extract email body: {e}")
            
        return ""

# =====================================================================
# AIRTABLE INTEGRATION
# =====================================================================

class AirtableManager:
    """Manage bid opportunities in Airtable"""
    
    def __init__(self):
        self.api = Api(AIRTABLE_API_KEY)
        self.table = self.api.table(AIRTABLE_BASE_ID, OPPORTUNITIES_TABLE)
        
    def create_opportunity(self, extracted_info):
        """Create new opportunity record - using existing table fields"""
        
        # Build name from organization + title
        org = extracted_info.get('organization', 'Unknown')
        title = extracted_info.get('title', 'Unknown')
        name = f"{org} - {title}"[:100]  # Limit to 100 chars
        
        # Determine high value flag (>= $50K)
        value = extracted_info.get('estimated_value', 0)
        high_value = value >= 50000 if value else False
        
        # Basic fields that exist in GPSS OPPORTUNITIES
        fields = {
            'Name': name,
            'RFP NUMBER': extracted_info.get('solicitation_number', 'Unknown'),
            'Deadline': extracted_info.get('deadline'),
            'Source Status': 'NEW',
            'HIGH VALUE FLAG': high_value
        }
        
        # Remove None values
        fields = {k: v for k, v in fields.items() if v is not None}
        
        try:
            record = self.table.create(fields)
            print(f"  ✓ Created Airtable record: {record['id']}")
            print(f"     Name: {name}")
            print(f"     RFP: {fields.get('RFP NUMBER')}")
            print(f"     Deadline: {fields.get('Deadline', 'Not specified')}")
            print(f"     High Value: {'Yes' if high_value else 'No'}")
            
            # Store extracted info in memory for diversity inquiry
            self._last_extracted = extracted_info
            return record
        except Exception as e:
            print(f"  ✗ Failed to create Airtable record: {e}")
            print(f"     Error details: {str(e)}")
            return None
    
    def update_diversity_inquiry_sent(self, record_id):
        """Mark diversity inquiry as sent"""
        try:
            # Update Source Status to indicate inquiry sent
            fields = {
                'Source Status': 'INQUIRY SENT'
            }
            self.table.update(record_id, fields)
            print(f"  ✓ Updated record {record_id} - diversity inquiry sent")
        except Exception as e:
            print(f"  ✗ Failed to update record: {e}")

# =====================================================================
# DIVERSITY INQUIRY SENDER
# =====================================================================

class DiversityInquirySender:
    """Automatically send diversity inquiry emails"""
    
    def send_inquiry(self, buyer_email, buyer_name, solicitation_number, 
                     solicitation_title, organization):
        """Send diversity preference inquiry"""
        
        try:
            # Connect to SMTP
            smtp = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            smtp.starttls()
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            
            # Determine salutation
            salutation = f"Good morning {buyer_name}," if buyer_name else "Good morning,"
            
            # Create email
            msg = MIMEMultipart()
            msg['From'] = f"{COMPANY_NAME} <{EMAIL_ADDRESS}>"
            msg['To'] = buyer_email
            msg['Subject'] = f"Question About {solicitation_number} - Diversity Preferences"
            
            body = f"""{salutation}

I'm Dee Davis with {COMPANY_NAME}, and I'm preparing a bid for {solicitation_number} - {solicitation_title}. I have a question about {organization}'s evaluation process.

Does this procurement include diversity goals or preferences for certified small businesses?

{COMPANY_NAME} is a certified EDWOSB/WOSB/MBE/WBE contractor based in {COMPANY_LOCATION}. If {organization} values diverse supplier participation, I want to ensure we properly highlight our certifications in our bid submission.

Could you clarify whether diversity certifications are considered in the award decision, or if the award is based solely on price?

Thank you for your guidance!

Dee Davis
{COMPANY_NAME}
{COMPANY_LOCATION}
{COMPANY_PHONE}
{COMPANY_EMAIL}

EDWOSB/WOSB/MBE/WBE Certified
CAGE Code: {CAGE_CODE}

---
This email was sent by NEXUS, {COMPANY_NAME}'s automated bid intelligence system.
For questions, please reply to this email.
"""
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send
            smtp.send_message(msg)
            smtp.quit()
            
            print(f"  ✓ Sent diversity inquiry to {buyer_email}")
            return True
            
        except Exception as e:
            print(f"  ✗ Failed to send inquiry: {e}")
            return False

# =====================================================================
# MAIN AUTOMATION
# =====================================================================

def main():
    """Main automation loop"""
    print("=" * 70)
    print("NEXUS EMAIL AUTOMATION SYSTEM")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print()
    
    # Check environment variables
    if not all([EMAIL_PASSWORD, AIRTABLE_API_KEY, ANTHROPIC_API_KEY]):
        print("✗ ERROR: Missing required environment variables!")
        print("  Required: NEXUS_EMAIL_PASSWORD, AIRTABLE_API_KEY, ANTHROPIC_API_KEY")
        return
    
    # Initialize components
    print("Initializing components...")
    try:
        monitor = EmailMonitor()
        extractor = SolicitationExtractor()
        airtable = AirtableManager()
        inquiry_sender = DiversityInquirySender()
    except Exception as e:
        print(f"✗ Initialization failed: {e}")
        return
    
    print()
    
    # Check for new solicitations
    print("Checking inbox for new solicitations...")
    solicitations = monitor.check_for_new_solicitations()
    
    if not solicitations:
        print("✓ No new solicitations found")
        print()
        return
    
    print(f"\n✓ Found {len(solicitations)} new solicitations to process")
    print()
    
    # Process each solicitation
    for idx, sol in enumerate(solicitations, 1):
        email_id = sol['id']
        email_msg = sol['message']
        
        print(f"[{idx}/{len(solicitations)}] Processing: {email_msg['subject'][:60]}...")
        
        # Extract information
        info = extractor.extract_info(email_msg)
        
        print(f"  → Title: {info.get('title', 'Unknown')}")
        print(f"  → Organization: {info.get('organization', 'Unknown')}")
        print(f"  → Fit Score: {info.get('fit_score', 0)}/100")
        print(f"  → Priority: {info.get('priority_level', 'UNKNOWN')}")
        
        # Create Airtable record
        record = airtable.create_opportunity(info)
        
        if not record:
            print(f"  ⚠ Skipping inquiry (failed to create record)")
            monitor.mark_as_processed(email_id)
            print()
            continue
        
        # Send diversity inquiry if recommended
        if info.get('should_send_diversity_inquiry') and info.get('buyer_email'):
            fit_score = info.get('fit_score', 0)
            value = info.get('estimated_value', 0)
            
            # Double-check thresholds
            if fit_score >= MIN_FIT_SCORE and (value is None or value >= MIN_CONTRACT_VALUE):
                print(f"  → Sending diversity inquiry to {info['buyer_email']}")
                
                success = inquiry_sender.send_inquiry(
                    buyer_email=info['buyer_email'],
                    buyer_name=info.get('buyer_name', ''),
                    solicitation_number=info['solicitation_number'],
                    solicitation_title=info['title'],
                    organization=info['organization']
                )
                
                if success:
                    airtable.update_diversity_inquiry_sent(record['id'])
            else:
                print(f"  → Skipping inquiry (fit={fit_score}, value={value})")
        else:
            if not info.get('buyer_email'):
                print(f"  → No buyer email found - cannot send inquiry")
            else:
                print(f"  → Inquiry not recommended by AI")
        
        # Mark email as processed
        monitor.mark_as_processed(email_id)
        print()
    
    print("=" * 70)
    print(f"NEXUS Email Automation Complete!")
    print(f"Processed: {len(solicitations)} solicitations")
    print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

if __name__ == "__main__":
    main()
