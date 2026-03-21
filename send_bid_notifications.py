#!/usr/bin/env python3
"""
NEXUS BID NOTIFICATION SYSTEM
Sends targeted email notifications for active bids

Created: February 5, 2026
Purpose: Send daily reminders for active RCOC bids
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

# Email configuration
SMTP_SERVER = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = 587
EMAIL_FROM = os.environ.get('NEXUS_EMAIL', 'bids.deedavisinc@gmail.com')
EMAIL_PASSWORD = os.environ.get('NEXUS_EMAIL_PASSWORD')
EMAIL_TO = os.environ.get('USER_EMAIL', 'info@deedavis.biz')

# Active bids — dynamically loaded, expired bids automatically skipped
# Add new bids here. Expired deadlines are filtered out at runtime.
ACTIVE_BIDS = [
    {
        "id": "VA SHREDDING",
        "name": "Document Shredding Services",
        "deadline": datetime(2026, 3, 31, 17, 0),
        "value": "TBD",
        "profit": "TBD",
        "status": "Need to pull solicitation",
        "platform": "SAM.gov",
        "buyer": "Tiffany Garfield (VA VBAVACO)",
        "action": "Pull solicitation 36C10D26Q0034 from SAM.gov, review, bid",
        "folder": "BIDS:RESOURCES/VA DOCUMENT SHREDDING/"
    },
]


def _filter_expired_bids(bids):
    """Remove bids whose deadlines have already passed."""
    now = datetime.now()
    active = []
    for bid in bids:
        if bid['deadline'] > now:
            active.append(bid)
    return active


def calculate_days_until(deadline):
    """Calculate days until deadline"""
    now = datetime.now()
    delta = deadline - now
    days = delta.days
    hours = delta.seconds // 3600
    return days, hours


def get_urgency_emoji(days_until):
    """Get emoji based on urgency"""
    if days_until <= 2:
        return "🔴"
    elif days_until <= 5:
        return "🟡"
    else:
        return "🟢"


def send_notification_email(subject, body):
    """Send email notification"""
    try:
        msg = MIMEMultipart()
        msg['From'] = f"NEXUS Notifications <{EMAIL_FROM}>"
        msg['To'] = EMAIL_TO
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_FROM, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        print(f"✅ Sent notification: {subject}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send notification: {e}")
        return False


def send_daily_bid_reminder():
    """Send daily reminder for active (non-expired) bids only."""
    today = datetime.now()
    live_bids = _filter_expired_bids(ACTIVE_BIDS)
    
    if not live_bids:
        print("✅ No active bids with upcoming deadlines — no reminder sent.")
        return
    
    # Categorize bids by urgency
    urgent = []  # <= 3 days
    coming_soon = []  # 4-7 days
    upcoming = []  # 8+ days
    
    for bid in live_bids:
        days_until, hours_until = calculate_days_until(bid['deadline'])
        
        bid_info = bid.copy()
        bid_info['days_until'] = days_until
        bid_info['hours_until'] = hours_until
        
        if days_until <= 3:
            urgent.append(bid_info)
        elif days_until <= 7:
            coming_soon.append(bid_info)
        else:
            upcoming.append(bid_info)
    
    # Build email body
    body = f"""🚨 NEXUS BID REMINDER
{today.strftime('%A, %B %d, %Y @ %I:%M %p')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
    
    if urgent:
        body += "🔴 URGENT - NEXT 3 DAYS:\n\n"
        for bid in urgent:
            body += f"{bid['id']}: {bid['name']}\n"
            body += f"  💰 Value: {bid['value']} | Profit: {bid['profit']}\n"
            body += f"  ⏰ Deadline: {bid['deadline'].strftime('%A, %B %d @ %I:%M %p EST')}\n"
            body += f"  📅 Due in: {bid['days_until']} days, {bid['hours_until']} hours\n"
            body += f"  📋 Status: {bid['status']}\n"
            body += f"  🎯 Action: {bid['action']}\n"
            body += f"  📁 Folder: {bid['folder']}\n\n"
    
    if coming_soon:
        body += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        body += "🟡 THIS WEEK (4-7 DAYS):\n\n"
        for bid in coming_soon:
            body += f"{bid['id']}: {bid['name']}\n"
            body += f"  💰 Value: {bid['value']} | Profit: {bid['profit']}\n"
            body += f"  ⏰ Deadline: {bid['deadline'].strftime('%A, %B %d @ %I:%M %p EST')}\n"
            body += f"  📅 Due in: {bid['days_until']} days\n"
            body += f"  📋 Status: {bid['status']}\n"
            body += f"  🎯 Action: {bid['action']}\n\n"
    
    if upcoming:
        body += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        body += "🟢 UPCOMING (8+ DAYS):\n\n"
        for bid in upcoming:
            body += f"{bid['id']}: {bid['name']}\n"
            body += f"  💰 Value: {bid['value']} | Deadline: {bid['deadline'].strftime('%B %d')}\n"
            body += f"  📅 Due in: {bid['days_until']} days\n\n"
    
    body += """━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 TODAY'S PRIORITIES:

"""
    
    # Generate today's action items
    if urgent:
        for bid in urgent:
            if bid['days_until'] <= 1:
                body += f"  🔴 SUBMIT {bid['id']} TODAY!\n"
            elif bid['days_until'] <= 2:
                body += f"  🟡 Final review for {bid['id']}\n"
            else:
                body += f"  🟢 Start final prep for {bid['id']}\n"
    
    if coming_soon:
        for bid in coming_soon:
            if "quotes" in bid['action'].lower():
                body += f"  📞 Request quotes for {bid['id']}\n"
    
    body += """

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📞 KEY CONTACTS:
  • Grainger Quotes: quotes@grainger.com | 1-800-472-4643
  • Shari Graves (RCOC): 248-858-4780 | purchasing@rcoc.org
  • Tracy McDonald (RCOC): 248-858-4796 | purchasing@rcoc.org

📁 All bid documents: /Users/deedavis/NEXUS BACKEND/photos_and_videos/

⚠️  REMEMBER: RCOC bids close at 2:30 PM EST (not 5 PM!)
Submit 3 days early for safety margin.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

NEXUS Bid Notification System
Never miss another deadline.

To stop these notifications, reply "STOP NOTIFICATIONS"
To adjust notification timing, reply with your preferences
"""
    
    # Determine subject based on urgency
    if urgent:
        subject = f"🔴 URGENT: {len(urgent)} Bid(s) Due in Next 3 Days!"
    elif coming_soon:
        subject = f"🟡 Reminder: {len(coming_soon)} Bid(s) Due This Week"
    else:
        subject = f"🟢 Weekly Bid Update: {len(ACTIVE_BIDS)} Active Bids"
    
    # Send email
    send_notification_email(subject, body)


def send_urgent_alert(bid):
    """Send urgent alert for specific bid (≤ 3 days until deadline)"""
    days_until, hours_until = calculate_days_until(bid['deadline'])
    
    # Determine urgency level
    if days_until == 0:
        urgency = "🔴 CRITICAL"
        subject = f"🔴 CRITICAL: {bid['id']} DUE TODAY at 2:30 PM!"
    elif days_until == 1:
        urgency = "🔴 URGENT"
        subject = f"🔴 URGENT: {bid['id']} Due TOMORROW!"
    elif days_until == 2:
        urgency = "🟡 URGENT"
        subject = f"🟡 URGENT: {bid['id']} Due in 2 Days!"
    else:
        urgency = "🟡 ALERT"
        subject = f"🟡 ALERT: {bid['id']} Due in {days_until} Days"
    
    body = f"""{urgency}: BID DEADLINE APPROACHING

{bid['id']}: {bid['name']}

⏰ DEADLINE: {bid['deadline'].strftime('%A, %B %d, %Y @ %I:%M %p EST')}
📅 TIME REMAINING: {days_until} days, {hours_until} hours

💰 CONTRACT VALUE: {bid['value']}
💵 ESTIMATED PROFIT: {bid['profit']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️  IMMEDIATE ACTION REQUIRED:

"""
    
    if days_until == 0:
        body += f"""  🔴 SUBMIT NOW!
  
  The deadline is TODAY at 2:30 PM EST.
  You have approximately {hours_until} hours remaining.
  
  SUBMIT IMMEDIATELY via {bid['platform']}
"""
    elif days_until == 1:
        body += f"""  🔴 FINAL REVIEW & SUBMIT TOMORROW MORNING!
  
  Deadline: TOMORROW at 2:30 PM EST
  
  TODAY:
  - Final review of all pricing
  - Verify all documents complete
  - Test upload to {bid['platform']}
  
  TOMORROW:
  - Submit by 10 AM (4.5 hours early for safety)
"""
    elif days_until == 2:
        body += f"""  🟡 COMPLETE BID FORM TODAY!
  
  Deadline: {bid['deadline'].strftime('%A')} at 2:30 PM EST (2 days)
  
  TODAY:
  - Complete all bid forms
  - Upload to {bid['platform']}
  - Review for accuracy
  
  TOMORROW:
  - Final review and submit
"""
    else:
        body += f"""  🟢 PREPARE FOR SUBMISSION
  
  Deadline: {bid['deadline'].strftime('%A, %B %d')} at 2:30 PM EST
  
  ACTION: {bid['action']}
"""
    
    body += f"""

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 BID DETAILS:

Status: {bid['status']}
Buyer: {bid['buyer']}
Platform: {bid['platform']}
Folder: {bid['folder']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️  REMEMBER:
- RCOC bids close at 2:30 PM EST (not 5 PM!)
- Submit 3-4 hours early for technical issues
- Test upload BEFORE deadline day

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

NEXUS Urgent Alert System
You're receiving this because the deadline is within 3 days.

Frontend Dashboard: http://localhost:3000
All active bids visible in NEXUS notification banner.
"""
    
    send_notification_email(subject, body)


def check_and_send_alerts():
    """Check active (non-expired) bids and send ONLY urgent/critical alerts (≤ 3 days)"""
    print("=" * 70)
    print("🚨 NEXUS URGENT NOTIFICATION SYSTEM")
    print(f"Running: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print()
    
    live_bids = _filter_expired_bids(ACTIVE_BIDS)
    if not live_bids:
        print("✅ No active bids — all deadlines have passed or no bids configured.")
        return
    
    # Check for urgent alerts ONLY (≤ 3 days)
    urgent_bids = []
    for bid in live_bids:
        days_until, _ = calculate_days_until(bid['deadline'])
        if days_until <= 3:
            urgent_bids.append(bid)
    
    if urgent_bids:
        print(f"🔴 Found {len(urgent_bids)} URGENT bid(s) - sending alerts...")
        for bid in urgent_bids:
            days_until, hours_until = calculate_days_until(bid['deadline'])
            print(f"   • {bid['id']}: {days_until} days, {hours_until} hours remaining")
            send_urgent_alert(bid)
        print()
    else:
        print("✅ No urgent bids (all deadlines > 3 days away)")
        print("   Frontend notification banner shows all active bids.")
        print()
    
    print("=" * 70)
    print("✅ Notification check complete")
    print(f"   Emails sent: {len(urgent_bids)}")
    print("=" * 70)


if __name__ == "__main__":
    check_and_send_alerts()
