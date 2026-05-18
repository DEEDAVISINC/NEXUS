#!/usr/bin/env python3
"""
NEXUS — Daily Opportunity Report Email Sender
Sends healthcare, public portal, and MCO checklist reports to Dee.

Run: python3 send_opportunity_reports.py
     python3 send_opportunity_reports.py --healthcare   # Healthcare only
     python3 send_opportunity_reports.py --public       # Public portals only
     python3 send_opportunity_reports.py --all          # All reports (default)

Scheduled: Add to cron to run after morning scans complete.
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Email configuration
SMTP_SERVER = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = 587
EMAIL_FROM = os.environ.get('NEXUS_EMAIL', 'bids.deedavisinc@gmail.com')
EMAIL_PASSWORD = os.environ.get('NEXUS_EMAIL_PASSWORD')
EMAIL_TO = 'bids.deedavisinc@gmail.com'  # Dee's inbox

# Report files
BASE_DIR = Path(__file__).resolve().parent
HEALTHCARE_REPORT = BASE_DIR / "HEALTHCARE_OPPORTUNITIES_REPORT.md"
PUBLIC_REPORT = BASE_DIR / "DAILY_OPPORTUNITIES_REPORT.md"
MCO_CHECKLIST = BASE_DIR / "MCO_PORTAL_DAILY_CHECKLIST.md"


def read_report(filepath: Path) -> str:
    """Read report file content."""
    if filepath.exists():
        return filepath.read_text()
    return f"Report not found: {filepath.name}"


def send_email(subject: str, body: str) -> bool:
    """Send email via Gmail SMTP."""
    if not EMAIL_PASSWORD:
        print("ERROR: NEXUS_EMAIL_PASSWORD not set in .env")
        print("Email not sent. Report content:")
        print("-" * 60)
        print(body[:2000])
        print("-" * 60)
        return False
    
    try:
        msg = MIMEMultipart('alternative')
        msg['From'] = f"NEXUS Opportunity Scanner <{EMAIL_FROM}>"
        msg['To'] = EMAIL_TO
        msg['Subject'] = subject
        
        # Plain text version
        msg.attach(MIMEText(body, 'plain'))
        
        # Connect and send
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_FROM, EMAIL_PASSWORD)
            server.send_message(msg)
        
        print(f"✅ Email sent to {EMAIL_TO}")
        return True
        
    except Exception as e:
        print(f"❌ Email failed: {e}")
        return False


def send_healthcare_report():
    """Send healthcare & MCO opportunities report."""
    report = read_report(HEALTHCARE_REPORT)
    checklist = read_report(MCO_CHECKLIST)
    
    body = f"""NEXUS Healthcare & MCO Opportunity Report
Generated: {datetime.now().strftime("%B %d, %Y at %I:%M %p ET")}

{'='*60}
HEALTHCARE OPPORTUNITIES (State Medicaid + Hospital RFPs)
{'='*60}

{report}

{'='*60}
MCO VENDOR PORTAL CHECKLIST (Manual Check Required)
{'='*60}

{checklist}

---
This is an automated report from NEXUS.
Run healthcare scan: python3 nexus_scheduler.py --healthcare
"""
    
    subject = f"🏥 NEXUS Healthcare Opportunities — {datetime.now().strftime('%b %d, %Y')}"
    return send_email(subject, body)


def send_public_portal_report():
    """Send public portal scan report."""
    report = read_report(PUBLIC_REPORT)
    
    body = f"""NEXUS Public Portal Opportunity Report
Generated: {datetime.now().strftime("%B %d, %Y at %I:%M %p ET")}

{'='*60}
PUBLIC PROCUREMENT PORTALS (SAM.gov, BidNet, State Sites)
{'='*60}

{report}

---
This is an automated report from NEXUS.
Run public scan: python3 nexus_scheduler.py --public
"""
    
    subject = f"📋 NEXUS Public Opportunities — {datetime.now().strftime('%b %d, %Y')}"
    return send_email(subject, body)


def send_combined_report():
    """Send all reports in one email."""
    healthcare = read_report(HEALTHCARE_REPORT)
    public = read_report(PUBLIC_REPORT)
    checklist = read_report(MCO_CHECKLIST)
    
    body = f"""NEXUS DAILY OPPORTUNITY REPORT
Generated: {datetime.now().strftime("%B %d, %Y at %I:%M %p ET")}

This email contains ALL opportunities from today's scans:
1. Healthcare & MCO Opportunities
2. Public Portal Opportunities (Government)
3. MCO Vendor Portal Checklist (Manual)

{'='*60}
SECTION 1: HEALTHCARE & MCO OPPORTUNITIES
{'='*60}

{healthcare}

{'='*60}
SECTION 2: PUBLIC PORTAL OPPORTUNITIES
{'='*60}

{public}

{'='*60}
SECTION 3: MCO VENDOR PORTAL CHECKLIST
{'='*60}

{checklist}

---
This is an automated report from NEXUS.
To run scans manually:
  python3 nexus_scheduler.py --healthcare
  python3 nexus_scheduler.py --public
"""
    
    subject = f"🎯 NEXUS Daily Opportunities — {datetime.now().strftime('%b %d, %Y')}"
    return send_email(subject, body)


if __name__ == "__main__":
    import sys
    
    args = sys.argv[1:] if len(sys.argv) > 1 else ["--all"]
    
    if "--healthcare" in args:
        print("Sending healthcare report...")
        send_healthcare_report()
    elif "--public" in args:
        print("Sending public portal report...")
        send_public_portal_report()
    else:
        print("Sending combined opportunity report...")
        send_combined_report()
