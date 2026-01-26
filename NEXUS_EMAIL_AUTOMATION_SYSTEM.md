# NEXUS EMAIL AUTOMATION SYSTEM
**Automated Bid Intelligence: Receive, Extract, Inquire, Track**

**Last Updated:** January 25, 2026

---

## 🎯 THE VISION

**NEXUS should automatically:**

1. ✅ **RECEIVE** - Monitor dedicated email inbox for new solicitations
2. ✅ **EXTRACT** - Pull key info (RFP #, deadline, buyer, value, location)
3. ✅ **ANALYZE** - AI determines if opportunity fits your profile
4. ✅ **INQUIRE** - Auto-send diversity inquiry emails to buyers
5. ✅ **TRACK** - Log responses, update Airtable, alert you to high-value opportunities
6. ✅ **RECOMMEND** - Score opportunities based on diversity preference + fit

**Result:** Wake up to a curated list of pre-qualified opportunities with diversity intel!

---

## 📧 THE EMAIL AUTOMATION WORKFLOW

```
┌─────────────────────────────────────────────────────────────┐
│ STEP 1: SOLICITATION RECEIVED                                │
│ bids@deedavisinc.com receives RFP/RFQ notification           │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 2: NEXUS MONITORS INBOX (Every 30 minutes)              │
│ - Checks for new emails                                      │
│ - Identifies solicitation emails (keywords, sources)         │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 3: AI EXTRACTS KEY INFORMATION                          │
│ - Solicitation number                                        │
│ - Organization name                                          │
│ - Deadline date/time                                         │
│ - Product/service description                                │
│ - Contract value (if mentioned)                              │
│ - Buyer contact (name, email, phone)                         │
│ - Location                                                   │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 4: AI ANALYZES FIT                                      │
│ - Matches against your capabilities                          │
│ - Calculates fit score (0-100)                               │
│ - Estimates contract value                                   │
│ - Determines priority level                                  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 5: CREATES AIRTABLE RECORD                              │
│ Table: "BID OPPORTUNITIES"                                   │
│ - All extracted fields populated                             │
│ - Status: "NEW - PENDING DIVERSITY INQUIRY"                  │
│ - AI Fit Score: 0-100                                        │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 6: AUTO-SEND DIVERSITY INQUIRY (If high-value)          │
│ - Generates personalized email to buyer                      │
│ - Sends from bids@deedavisinc.com                            │
│ - Asks about diversity preferences                           │
│ - Logs sent inquiry in Airtable                              │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 7: MONITORS FOR RESPONSES                               │
│ - Watches for buyer reply                                    │
│ - AI extracts diversity preference (YES/NO/MAYBE)            │
│ - Updates Airtable with diversity status                     │
│ - Calculates revised win probability                         │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 8: ALERTS YOU TO HIGH-PRIORITY OPPORTUNITIES            │
│ - Slack notification: "NEW: $500K contract, 75% fit"         │
│ - Email digest: Daily summary of new opportunities           │
│ - Dashboard: Sortable list of qualified opportunities        │
└─────────────────────────────────────────────────────────────┘
```

---

## 📋 AIRTABLE SCHEMA: "BID OPPORTUNITIES" TABLE

### **Fields to Add/Modify:**

```javascript
{
  // BASIC INFORMATION
  "Solicitation Number": "Text",
  "Title": "Long Text",
  "Organization": "Text",
  "Buyer Name": "Text",
  "Buyer Email": "Email",
  "Buyer Phone": "Phone",
  "Deadline": "Date/Time",
  "Publication Date": "Date",
  
  // OPPORTUNITY DETAILS
  "Description": "Long Text",
  "Estimated Value": "Currency",
  "Contract Duration": "Text",
  "Location": "Text",
  "Product/Service Category": "Single Select",
  
  // AI ANALYSIS
  "AI Fit Score": "Number (0-100)",
  "Fit Analysis": "Long Text",
  "Estimated Win Probability": "Percent",
  "Priority Level": "Single Select (High/Medium/Low)",
  
  // DIVERSITY INTELLIGENCE
  "Diversity Inquiry Status": "Single Select",
  //   Options: "Not Sent", "Sent - Awaiting Response", 
  //            "YES - Diversity Valued", "NO - Price Only",
  //            "MAYBE - Other Factors", "No Response"
  
  "Diversity Inquiry Sent Date": "Date",
  "Diversity Response Received Date": "Date",
  "Diversity Response": "Long Text",
  "Revised Win Probability": "Percent (after diversity intel)",
  
  // BID TRACKING
  "Bid Status": "Single Select",
  //   Options: "NEW - Not Reviewed", "REVIEWING",
  //            "DIVERSITY INQUIRY SENT", "QUALIFIED - BID",
  //            "DISQUALIFIED - SKIP", "BID SUBMITTED",
  //            "WON", "LOST"
  
  "Source": "Single Select (Email, SAM.gov, BidNet, etc.)",
  "Email Thread": "URL (link to email)",
  "Documents": "Attachments",
  
  // DECISION TRACKING
  "Decision": "Single Select (BID / SKIP / PENDING)",
  "Decision Reason": "Long Text",
  "Decision Date": "Date",
  
  // AUTOMATION TRACKING
  "Auto-Extracted": "Checkbox",
  "Auto-Inquiry-Sent": "Checkbox",
  "Created By": "Single Select (NEXUS AI / Manual)",
  "Last Updated": "Date"
}
```

---

## 🤖 THE EMAIL MONITORING SYSTEM

### **Option 1: Gmail API (RECOMMENDED)** ⭐

**Setup:**
1. Create Gmail: `bids@deedavisinc.com`
2. Enable Gmail API in Google Cloud Console
3. Python script checks inbox every 30 minutes
4. Reads unread emails with solicitation keywords

**Pros:**
- ✅ Free
- ✅ Powerful API
- ✅ Can mark emails as read after processing
- ✅ Can create labels/folders
- ✅ Can send replies automatically

**Cons:**
- ⚠️ Requires Google Cloud setup (one-time)

---

### **Option 2: Microsoft 365 / Outlook API**

**Setup:**
1. Create Outlook: `bids@deedavisinc.com`
2. Use Microsoft Graph API
3. Similar to Gmail API

**Pros:**
- ✅ Professional email domain
- ✅ Can use custom domain (deedavisinc.com)
- ✅ Better for business

**Cons:**
- ⚠️ May require paid Microsoft 365 plan

---

### **Option 3: IMAP Monitoring (Simplest)**

**Setup:**
1. Any email provider with IMAP support
2. Python script connects via IMAP
3. Checks for new emails periodically

**Pros:**
- ✅ Works with any email provider
- ✅ Simple to set up
- ✅ No API credentials needed

**Cons:**
- ⚠️ Slower than API
- ⚠️ Less reliable

---

## 🧠 AI EXTRACTION WORKFLOW

### **What NEXUS Extracts from Solicitation Emails:**

```python
# Example Email Body:
"""
Subject: New Bid Opportunity - RFQ 2026-12345 - Office Supplies

The City of Detroit announces RFQ 2026-12345 for office supplies.

Deadline: February 15, 2026 at 2:00 PM EST
Contact: John Smith, Procurement Officer
Email: jsmith@detroitmi.gov
Phone: (313) 555-1234

Estimated annual value: $150,000

Please submit bids electronically to the email above.
"""

# NEXUS AI Extracts:
{
  "solicitation_number": "RFQ 2026-12345",
  "title": "Office Supplies",
  "organization": "City of Detroit",
  "buyer_name": "John Smith",
  "buyer_title": "Procurement Officer",
  "buyer_email": "jsmith@detroitmi.gov",
  "buyer_phone": "(313) 555-1234",
  "deadline": "2026-02-15T14:00:00-05:00",
  "estimated_value": 150000,
  "location": "Detroit, MI",
  "category": "Office Supplies",
  "submission_method": "Email"
}
```

### **AI Fit Analysis:**

```python
# NEXUS analyzes against your capabilities:
{
  "fit_score": 85,  # Out of 100
  "fit_analysis": "GOOD FIT - Office supplies matches your 
                   distribution capabilities. Detroit is local 
                   (30 min from Troy). Contract size ($150K) is 
                   ideal for your capacity.",
  
  "priority_level": "HIGH",
  
  "strengths": [
    "Local (30 min from Troy)",
    "Contract size matches your capacity",
    "Product category matches capabilities",
    "City procurement (likely values diversity)"
  ],
  
  "concerns": [
    "Competitive category (many suppliers)",
    "Deadline is tight (3 weeks)"
  ],
  
  "estimated_win_probability": 40,  # Before diversity intel
  
  "recommendation": "SEND DIVERSITY INQUIRY - This is a good 
                     opportunity. Local government likely values 
                     EDWOSB/WBE certifications. Send inquiry to 
                     determine if diversity affects evaluation."
}
```

---

## 📧 AUTO-GENERATED DIVERSITY INQUIRY EMAIL

### **NEXUS Automatically Sends:**

```python
# If opportunity fit_score > 70 and estimated_value > $20,000:

To: jsmith@detroitmi.gov
From: bids@deedavisinc.com
Subject: Question About RFQ 2026-12345 - Diversity Preferences

Good morning John,

I'm Dee Davis with DEE DAVIS INC, and I'm preparing a bid for 
RFQ 2026-12345 - Office Supplies. I have a question about the 
City of Detroit's evaluation process.

Does this procurement include diversity goals or preferences for 
certified small businesses?

DEE DAVIS INC is a certified EDWOSB/WOSB/MBE/WBE contractor 
based in Troy, Michigan. If the City of Detroit values diverse 
supplier participation, I want to ensure we properly highlight 
our certifications in our bid submission.

Could you clarify whether diversity certifications are considered 
in the award decision, or if the award is based solely on price?

Thank you for your guidance!

Dee Davis
DEE DAVIS INC
Troy, MI 48083
248-376-4550
info@deedavis.biz

EDWOSB/WOSB/MBE/WBE Certified
CAGE Code: [YOUR CAGE CODE]

---
This email was sent by NEXUS, DEE DAVIS INC's automated bid 
intelligence system. For questions, please reply to this email.
```

---

## 🎯 AI RESPONSE CLASSIFICATION

### **When Buyer Replies, NEXUS Extracts:**

```python
# Example Response 1:
"""
Hi Dee,

Yes, the City of Detroit does consider diversity certifications 
in our evaluation. We award up to 5 points for EDWOSB/WBE 
certification.

Best regards,
John Smith
"""

# NEXUS Classifies:
{
  "diversity_status": "YES - Diversity Valued",
  "diversity_details": "5 evaluation points for EDWOSB/WBE",
  "revised_win_probability": 55,  # Up from 40%
  "confidence": "HIGH",
  "priority_update": "HIGH → VERY HIGH"
}

# NEXUS Actions:
# 1. Updates Airtable record
# 2. Sends you Slack/email: "⭐ HIGH PRIORITY: RFQ 2026-12345 
#    values diversity! Win probability: 55%"
# 3. Marks as "QUALIFIED - BID"
```

```python
# Example Response 2:
"""
Hi Dee,

This is a low-bid procurement. Award will be made to the lowest 
responsible bidder.

John Smith
"""

# NEXUS Classifies:
{
  "diversity_status": "NO - Price Only",
  "diversity_details": "Lowest responsible bidder",
  "revised_win_probability": 20,  # Down from 40%
  "confidence": "HIGH",
  "priority_update": "HIGH → LOW"
}

# NEXUS Actions:
# 1. Updates Airtable record
# 2. Sends you note: "⚠️ RFQ 2026-12345 is price-only. 
#    Consider skipping unless you have strong pricing."
# 3. Marks as "UNDER REVIEW"
```

---

## 📊 YOUR DAILY DIGEST

### **NEXUS Sends You (Every Morning at 8 AM):**

```
Subject: NEXUS Daily Digest - 3 New Opportunities, 2 Responses

Good morning Dee! Here's your bid intelligence update:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔥 HIGH PRIORITY OPPORTUNITIES (Diversity Valued)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. ⭐ City of Detroit - Office Supplies (RFQ 2026-12345)
   - Value: $150K/year
   - Deadline: Feb 15, 2026
   - Diversity: YES (5 points for EDWOSB/WBE)
   - Win Probability: 55%
   - Fit Score: 85/100
   - Distance: 30 min from Troy
   
   ACTION: Review and decide by Feb 5
   [View in NEXUS Dashboard →]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ MODERATE PRIORITY (Under Review)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

2. Oakland County - Janitorial Services (BID 2026-999)
   - Value: $200K/year
   - Deadline: March 1, 2026
   - Diversity: AWAITING RESPONSE (inquiry sent Jan 24)
   - Win Probability: 45% (pending diversity intel)
   - Fit Score: 70/100
   
   ACTION: Follow up on diversity inquiry by Jan 29
   [View in NEXUS Dashboard →]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
❌ LOW PRIORITY (Price Only)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

3. State of Michigan - Aggregate Materials (Contract 2026-ABC)
   - Value: $2.5M
   - Deadline: Feb 20, 2026
   - Diversity: NO (lowest price wins)
   - Win Probability: 10%
   - Fit Score: 45/100
   
   RECOMMENDATION: SKIP - Commodity pricing war, low win probability
   [View in NEXUS Dashboard →]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📈 PORTFOLIO SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Active Opportunities: 12
High Priority: 4 (diversity valued)
Awaiting Diversity Responses: 3
Bids In Progress: 5
Expected Value (All Opportunities): $87,500

[Open NEXUS Dashboard →]
```

---

## 🛠️ TECHNICAL IMPLEMENTATION

### **File: `nexus_email_automation.py`**

```python
#!/usr/bin/env python3
"""
NEXUS Email Automation System
Monitors inbox, extracts solicitations, sends diversity inquiries
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

# =====================================================================
# CONFIGURATION
# =====================================================================

EMAIL_ADDRESS = "bids@deedavisinc.com"
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')
IMAP_SERVER = "imap.gmail.com"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

AIRTABLE_API_KEY = os.environ.get('AIRTABLE_API_KEY')
AIRTABLE_BASE_ID = "YOUR_BASE_ID"
AIRTABLE_TABLE = "BID OPPORTUNITIES"

ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')

# =====================================================================
# EMAIL MONITORING
# =====================================================================

class EmailMonitor:
    """Monitor inbox for new solicitations"""
    
    def __init__(self):
        self.imap = imaplib.IMAP4_SSL(IMAP_SERVER)
        self.imap.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        
    def check_for_new_solicitations(self):
        """Check inbox for unread emails with solicitation keywords"""
        self.imap.select('INBOX')
        
        # Search for unread emails
        status, messages = self.imap.search(None, 'UNSEEN')
        email_ids = messages[0].split()
        
        solicitations = []
        
        for email_id in email_ids:
            # Fetch email
            status, msg_data = self.imap.fetch(email_id, '(RFC822)')
            email_body = msg_data[0][1]
            email_message = email.message_from_bytes(email_body)
            
            # Check if it's a solicitation
            if self.is_solicitation(email_message):
                solicitations.append(email_message)
                
        return solicitations
    
    def is_solicitation(self, email_message):
        """Determine if email is a bid solicitation"""
        subject = email_message['subject'].lower()
        body = self.get_email_body(email_message).lower()
        
        # Keywords that indicate solicitation
        keywords = [
            'rfp', 'rfq', 'rfb', 'request for proposal',
            'request for quote', 'bid opportunity',
            'solicitation', 'invitation to bid', 'itb',
            'proposal due', 'bid due', 'procurement'
        ]
        
        # Check if any keyword appears
        for keyword in keywords:
            if keyword in subject or keyword in body:
                return True
                
        return False
    
    def get_email_body(self, email_message):
        """Extract plain text body from email"""
        if email_message.is_multipart():
            for part in email_message.walk():
                if part.get_content_type() == "text/plain":
                    return part.get_payload(decode=True).decode()
        else:
            return email_message.get_payload(decode=True).decode()
        
        return ""

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
        
        prompt = f"""
Extract key information from this bid solicitation email and return as JSON.

EMAIL SUBJECT: {subject}

EMAIL FROM: {from_address}

EMAIL BODY:
{body}

Extract the following information (use null if not found):
- solicitation_number: The RFP/RFQ/RFB number
- title: Brief title of what's being procured
- organization: Organization/agency name
- buyer_name: Procurement officer name
- buyer_email: Buyer's email address
- buyer_phone: Buyer's phone number
- deadline: Bid deadline (ISO format: YYYY-MM-DDTHH:MM:SS)
- estimated_value: Contract value in dollars (number only)
- contract_duration: Duration (e.g., "1 year", "3 years")
- location: City, State
- description: Brief description of what's needed
- product_category: Category (e.g., "Office Supplies", "Landscaping")
- submission_method: How to submit (e.g., "Email", "Portal")

Also provide:
- fit_score: How well this matches DEE DAVIS INC capabilities (0-100)
- fit_analysis: Brief explanation of fit
- priority_level: HIGH/MEDIUM/LOW
- should_send_diversity_inquiry: true/false

DEE DAVIS INC CAPABILITIES:
- Product distribution/resale (office supplies, industrial goods)
- Landscaping materials (topsoil, grass seed, mulch)
- Janitorial supplies
- Government contracting
- EDWOSB/WOSB/MBE/WBE certified
- Located in Troy, Michigan
- Best for contracts $20K-$500K

Return ONLY valid JSON, no explanation.
"""
        
        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        result = response.content[0].text
        result = result.replace('```json', '').replace('```', '').strip()
        
        return json.loads(result)
    
    def get_email_body(self, email_message):
        """Extract plain text body from email"""
        if email_message.is_multipart():
            for part in email_message.walk():
                if part.get_content_type() == "text/plain":
                    return part.get_payload(decode=True).decode()
        else:
            return email_message.get_payload(decode=True).decode()
        return ""

# =====================================================================
# AIRTABLE INTEGRATION
# =====================================================================

class AirtableManager:
    """Manage bid opportunities in Airtable"""
    
    def __init__(self):
        self.api = Api(AIRTABLE_API_KEY)
        self.table = self.api.table(AIRTABLE_BASE_ID, AIRTABLE_TABLE)
        
    def create_opportunity(self, extracted_info):
        """Create new opportunity record"""
        fields = {
            'Solicitation Number': extracted_info.get('solicitation_number'),
            'Title': extracted_info.get('title'),
            'Organization': extracted_info.get('organization'),
            'Buyer Name': extracted_info.get('buyer_name'),
            'Buyer Email': extracted_info.get('buyer_email'),
            'Buyer Phone': extracted_info.get('buyer_phone'),
            'Deadline': extracted_info.get('deadline'),
            'Estimated Value': extracted_info.get('estimated_value'),
            'Contract Duration': extracted_info.get('contract_duration'),
            'Location': extracted_info.get('location'),
            'Description': extracted_info.get('description'),
            'Product/Service Category': extracted_info.get('product_category'),
            'AI Fit Score': extracted_info.get('fit_score'),
            'Fit Analysis': extracted_info.get('fit_analysis'),
            'Priority Level': extracted_info.get('priority_level'),
            'Bid Status': 'NEW - Not Reviewed',
            'Diversity Inquiry Status': 'Not Sent',
            'Auto-Extracted': True,
            'Created By': 'NEXUS AI',
            'Source': 'Email'
        }
        
        # Remove None values
        fields = {k: v for k, v in fields.items() if v is not None}
        
        record = self.table.create(fields)
        return record
    
    def update_diversity_status(self, record_id, status, response_text):
        """Update diversity inquiry status"""
        fields = {
            'Diversity Inquiry Status': status,
            'Diversity Response': response_text,
            'Diversity Response Received Date': datetime.now().isoformat()
        }
        
        return self.table.update(record_id, fields)

# =====================================================================
# DIVERSITY INQUIRY SENDER
# =====================================================================

class DiversityInquirySender:
    """Automatically send diversity inquiry emails"""
    
    def __init__(self):
        self.smtp = None
        
    def send_inquiry(self, buyer_email, buyer_name, solicitation_number, 
                     solicitation_title, organization):
        """Send diversity preference inquiry"""
        
        # Connect to SMTP
        self.smtp = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        self.smtp.starttls()
        self.smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        
        # Create email
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = buyer_email
        msg['Subject'] = f"Question About {solicitation_number} - Diversity Preferences"
        
        body = f"""Good morning {buyer_name},

I'm Dee Davis with DEE DAVIS INC, and I'm preparing a bid for {solicitation_number} - {solicitation_title}. I have a question about {organization}'s evaluation process.

Does this procurement include diversity goals or preferences for certified small businesses?

DEE DAVIS INC is a certified EDWOSB/WOSB/MBE/WBE contractor based in Troy, Michigan. If {organization} values diverse supplier participation, I want to ensure we properly highlight our certifications in our bid submission.

Could you clarify whether diversity certifications are considered in the award decision, or if the award is based solely on price?

Thank you for your guidance!

Dee Davis
DEE DAVIS INC
Troy, MI 48083
248-376-4550
info@deedavis.biz

EDWOSB/WOSB/MBE/WBE Certified
CAGE Code: [YOUR CAGE CODE]

---
This email was sent by NEXUS, DEE DAVIS INC's automated bid intelligence system.
"""
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Send
        self.smtp.send_message(msg)
        self.smtp.quit()
        
        return True

# =====================================================================
# MAIN AUTOMATION LOOP
# =====================================================================

def main():
    """Main automation loop"""
    print("NEXUS Email Automation System Starting...")
    
    # Initialize components
    monitor = EmailMonitor()
    extractor = SolicitationExtractor()
    airtable = AirtableManager()
    inquiry_sender = DiversityInquirySender()
    
    # Check for new solicitations
    print("Checking inbox for new solicitations...")
    solicitations = monitor.check_for_new_solicitations()
    
    print(f"Found {len(solicitations)} new solicitations")
    
    for email_msg in solicitations:
        print(f"\nProcessing: {email_msg['subject']}")
        
        # Extract information
        info = extractor.extract_info(email_msg)
        print(f"Extracted: {info.get('title')}")
        print(f"Fit Score: {info.get('fit_score')}/100")
        print(f"Priority: {info.get('priority_level')}")
        
        # Create Airtable record
        record = airtable.create_opportunity(info)
        print(f"Created Airtable record: {record['id']}")
        
        # Send diversity inquiry if recommended
        if info.get('should_send_diversity_inquiry') and info.get('buyer_email'):
            print(f"Sending diversity inquiry to {info.get('buyer_email')}")
            
            inquiry_sender.send_inquiry(
                buyer_email=info['buyer_email'],
                buyer_name=info.get('buyer_name', 'Sir/Madam'),
                solicitation_number=info['solicitation_number'],
                solicitation_title=info['title'],
                organization=info['organization']
            )
            
            # Update Airtable
            airtable.table.update(record['id'], {
                'Diversity Inquiry Status': 'Sent - Awaiting Response',
                'Diversity Inquiry Sent Date': datetime.now().isoformat(),
                'Auto-Inquiry-Sent': True
            })
            
            print("✓ Diversity inquiry sent and logged")
    
    print("\nNEXUS Email Automation Complete!")

if __name__ == "__main__":
    main()
```

---

## ⚙️ SETUP INSTRUCTIONS

### **Step 1: Create Dedicated Email**

1. Go to Gmail.com
2. Create new account: `bids@deedavisinc.com` (or use your domain)
3. Enable "Less secure app access" (or use App Password)
4. Save credentials securely

---

### **Step 2: Set Environment Variables**

```bash
export EMAIL_PASSWORD="your_email_password"
export AIRTABLE_API_KEY="your_airtable_key"
export ANTHROPIC_API_KEY="your_anthropic_key"
```

---

### **Step 3: Install Dependencies**

```bash
pip install anthropic pyairtable
```

---

### **Step 4: Update Airtable Schema**

Add fields to "BID OPPORTUNITIES" table (see schema above)

---

### **Step 5: Test Manually**

```bash
python nexus_email_automation.py
```

---

### **Step 6: Schedule Automation**

**Option A: Cron (Linux/Mac)**
```bash
# Run every 30 minutes
*/30 * * * * cd /path/to/nexus && python nexus_email_automation.py
```

**Option B: PythonAnywhere Scheduled Task**
- Add as daily/hourly task in PythonAnywhere dashboard

**Option C: GitHub Actions (Free)**
- Runs on GitHub's servers every 30 minutes

---

## 🎯 EXPECTED RESULTS

### **After 30 Days:**

**Automation Performance:**
- 50-100 new opportunities detected
- 30-50 opportunities auto-analyzed (fit score >60)
- 15-25 diversity inquiries auto-sent
- 10-15 diversity responses received
- 5-10 high-priority opportunities flagged

**Your Time Saved:**
- Email monitoring: 2-3 hours/week → 0 minutes (100% automated)
- Data entry: 1-2 hours/week → 0 minutes (100% automated)
- Diversity inquiries: 1 hour/week → 0 minutes (100% automated)
- **Total saved: 4-6 hours/week = 16-24 hours/month**

**Better Decisions:**
- More opportunities reviewed (100 vs. 20 manual)
- Better pre-qualification (diversity intel on 50%+ of opportunities)
- Higher win rate (focus on diversity-valued opportunities)
- Data-driven portfolio (track win rates by category, organization)

---

## 💰 ROI CALCULATION

### **Cost:**
- Email account: $0 (Gmail free) or $6/month (Google Workspace)
- Anthropic API: ~$5-10/month (based on volume)
- PythonAnywhere: $5/month (already using)
- **Total: $10-16/month**

### **Value:**
- Time saved: 4-6 hours/week × $100/hour = $400-600/week
- Better opportunities: 2-3 extra high-probability bids/month
- Higher win rate: 10-15% increase due to diversity targeting
- **Value: $1,600-2,400/month**

### **ROI: 10,000%+** 🚀

---

## ✅ NEXT STEPS

### **Phase 1: MVP (This Week)**
- [ ] Create `bids@deedavisinc.com` email
- [ ] Add "BID OPPORTUNITIES" fields to Airtable
- [ ] Create `nexus_email_automation.py` script
- [ ] Test with manual run
- [ ] Verify extraction works
- [ ] Test diversity inquiry sending

### **Phase 2: Schedule (Next Week)**
- [ ] Set up automated scheduling (cron or PythonAnywhere)
- [ ] Test for 3-5 days
- [ ] Monitor results
- [ ] Adjust AI prompts as needed

### **Phase 3: Enhance (Month 2)**
- [ ] Add daily digest email
- [ ] Add Slack notifications
- [ ] Create NEXUS dashboard
- [ ] Track win rate by diversity status
- [ ] Optimize AI analysis prompts

---

**This is NOT asking too much - this is EXACTLY what NEXUS should do!** 🤖✅

Would you like me to start building this email automation system?

---

*Created: January 25, 2026*
*Implementation Time: 2-4 hours*
*Expected ROI: 10,000%+*
