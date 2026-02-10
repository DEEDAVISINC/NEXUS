#!/usr/bin/env python3
"""
AUTOMATED BID MANAGER
Runs daily (or on-demand) to:
1. Generate calendar events for all deadlines
2. Create daily/weekly agenda
3. Ask status questions
4. Clean up old/abandoned bids
5. Send notifications

NO HUNTING - System tells YOU what to do!
"""

import os
import json
from datetime import datetime, timedelta
from pathlib import Path

BIDS_PATH = "/Users/deedavis/NEXUS BACKEND/BIDS:RESOURCES"
CALENDAR_PATH = "/Users/deedavis/NEXUS BACKEND/calendars"

# Known active bids with deadlines
ACTIVE_BIDS = {
    'CPS ENERGY': {'deadline': 'February 11, 2026', 'value': 25000, 'type': 'product'},
    'HENRY FORD BATTERY CABINETS': {'deadline': 'February 11, 2026', 'value': 15000, 'type': 'product'},
    'OAKLAND COUNTY FLOW METERS': {'deadline': 'February 12, 2026', 'value': 8000, 'type': 'product'},
    'OAKLAND COUNTY TREATED SALT': {'deadline': 'February 12, 2026', 'value': 50000, 'type': 'product'},
    'PORT HURON CHEMICALS': {'deadline': 'February 12, 2026', 'value': 12000, 'type': 'product'},
    'CPS ENERGY PADLOCKS': {'deadline': 'February 13, 2026', 'value': 32000, 'type': 'product'},
    'AUBURN HILLS PRESSURE WASHING': {'deadline': 'February 13, 2026', 'value': 5000, 'type': 'service'},
    'SHELBY TOWNSHIP POWER CABLES': {'deadline': 'February 13, 2026', 'value': 75000, 'type': 'product'},
    'OAKLAND COUNTY EXAM STOOLS': {'deadline': 'February 16, 2026', 'value': 3000, 'type': 'product'},
    'OAKLAND COUNTY TRUCK EQUIPMENT': {'deadline': 'February 17, 2026', 'value': 20000, 'type': 'product'},
    'RCOC 7790 SIGNS': {'deadline': 'February 17, 2026', 'value': 10000, 'type': 'product'},
    'RCOC 7842 SAFETY SUPPLIES': {'deadline': 'February 17, 2026', 'value': 8000, 'type': 'product'},
    'GENESEE WOOD POLES': {'deadline': 'February 18, 2026', 'value': 45000, 'type': 'product'},
    'HCMA CHLORINE': {'deadline': 'February 18, 2026', 'value': 30000, 'type': 'product'},
    'LIVONIA MATERIALS': {'deadline': 'February 23, 2026', 'value': 15000, 'type': 'product'},
    'HCMA UTILITY VEHICLES': {'deadline': 'February 25, 2026', 'value': 120000, 'type': 'product'},
    'ALASKA STEEL CONTAINERS': {'deadline': 'March 2, 2026', 'value': 85000, 'type': 'product'},
}

def parse_deadline(date_str):
    """Parse deadline string"""
    for fmt in ['%B %d, %Y', '%b %d, %Y']:
        try:
            return datetime.strptime(date_str, fmt)
        except:
            continue
    return None

def create_calendar_event(bid_name, deadline, description=""):
    """Create ICS calendar file for bid deadline"""
    # ICS format
    deadline_dt = parse_deadline(deadline)
    if not deadline_dt:
        return None
    
    # Set to 2 PM on deadline day
    deadline_dt = deadline_dt.replace(hour=14, minute=0)
    
    # Format for ICS
    dt_format = "%Y%m%dT%H%M%S"
    deadline_str = deadline_dt.strftime(dt_format)
    
    # Create reminders (3 days before, 1 day before, day of)
    remind_3days = (deadline_dt - timedelta(days=3)).strftime(dt_format)
    remind_1day = (deadline_dt - timedelta(days=1)).strftime(dt_format)
    
    event_id = bid_name.replace(' ', '_').replace('/', '_')
    
    ics_content = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Dee Davis Inc//NEXUS Bid Tracker//EN
CALSCALE:GREGORIAN
METHOD:PUBLISH
X-WR-CALNAME:NEXUS Bids
X-WR-TIMEZONE:America/Detroit
X-WR-CALDESC:Bid Deadlines from NEXUS

BEGIN:VEVENT
UID:{event_id}@deedavis.biz
DTSTAMP:{datetime.now().strftime(dt_format)}
DTSTART:{deadline_str}
DTEND:{deadline_str}
SUMMARY:🔥 BID DUE: {bid_name}
DESCRIPTION:{description}\\n\\nFolder: BIDS:RESOURCES/{bid_name}/
LOCATION:Submit via portal/email
STATUS:CONFIRMED
SEQUENCE:0
BEGIN:VALARM
TRIGGER:-P3D
DESCRIPTION:Bid due in 3 days: {bid_name}
ACTION:DISPLAY
END:VALARM
BEGIN:VALARM
TRIGGER:-P1D
DESCRIPTION:Bid due TOMORROW: {bid_name}
ACTION:DISPLAY
END:VALARM
BEGIN:VALARM
TRIGGER:-PT2H
DESCRIPTION:Bid due in 2 hours: {bid_name}
ACTION:DISPLAY
END:VALARM
END:VEVENT
END:VCALENDAR
"""
    
    return ics_content

def generate_all_calendars():
    """Generate calendar files for all active bids"""
    print("📅 Generating calendar events...\n")
    
    # Create calendars directory if needed
    os.makedirs(CALENDAR_PATH, exist_ok=True)
    
    # Clean old calendar files
    for file in os.listdir(CALENDAR_PATH):
        if file.endswith('.ics'):
            os.remove(os.path.join(CALENDAR_PATH, file))
    
    created = 0
    today = datetime.now()
    
    for bid_name, info in ACTIVE_BIDS.items():
        deadline = parse_deadline(info['deadline'])
        if not deadline:
            continue
        
        days_left = (deadline - today).days
        
        # Only create calendar for future deadlines
        if days_left >= 0:
            description = f"Value: ${info['value']:,}\\nType: {info['type'].title()}"
            ics = create_calendar_event(bid_name, info['deadline'], description)
            
            if ics:
                filename = f"{bid_name.replace(' ', '_').replace('/', '_')}.ics"
                filepath = os.path.join(CALENDAR_PATH, filename)
                
                with open(filepath, 'w') as f:
                    f.write(ics)
                
                created += 1
                print(f"  ✅ {bid_name} - {info['deadline']}")
    
    print(f"\n✅ Created {created} calendar events in {CALENDAR_PATH}/")
    print(f"   📲 Import these to your calendar app!\n")
    
    return created

def generate_daily_agenda():
    """Generate TODAY's agenda - what to work on"""
    print("📋 Generating today's agenda...\n")
    
    today = datetime.now()
    
    # Categorize bids
    urgent = []  # ≤2 days
    today_list = []  # Need action today
    this_week = []  # 3-7 days
    
    for bid_name, info in ACTIVE_BIDS.items():
        deadline = parse_deadline(info['deadline'])
        if not deadline:
            continue
        
        days_left = (deadline - today).days
        
        if days_left < 0:
            continue  # Past deadline
        
        folder_path = os.path.join(BIDS_PATH, bid_name)
        if not os.path.exists(folder_path):
            continue
        
        bid_info = {
            'name': bid_name,
            'deadline': deadline,
            'days_left': days_left,
            'value': info['value'],
            'type': info['type']
        }
        
        if days_left <= 2:
            urgent.append(bid_info)
        elif days_left <= 7:
            this_week.append(bid_info)
    
    # Generate agenda
    output_path = "TODAY_AGENDA.md"
    
    with open(output_path, 'w') as f:
        f.write(f"# 📅 YOUR AGENDA - {today.strftime('%A, %B %d, %Y')}\n\n")
        f.write("**This is what you need to work on TODAY.**\n\n")
        f.write("---\n\n")
        
        if urgent:
            f.write(f"## 🔥 URGENT - DROP EVERYTHING ({len(urgent)} bids)\n\n")
            f.write("**These need IMMEDIATE action:**\n\n")
            
            for i, bid in enumerate(urgent, 1):
                days_emoji = "🔴" if bid['days_left'] <= 1 else "⚠️"
                f.write(f"### {i}. {days_emoji} {bid['name']}\n")
                f.write(f"- **Deadline:** {bid['deadline'].strftime('%A, %B %d')} ({bid['days_left']} days!)\n")
                f.write(f"- **Value:** ${bid['value']:,}\n")
                f.write(f"- **Type:** {bid['type'].title()}\n")
                f.write(f"- **Folder:** `BIDS:RESOURCES/{bid['name']}/`\n\n")
                f.write("**TODAY'S TASKS:**\n")
                f.write("- [ ] Check folder for analysis\n")
                f.write("- [ ] Find suppliers/subcontractors\n")
                f.write("- [ ] Request quotes\n")
                f.write("- [ ] Follow up on quotes\n")
                f.write("- [ ] Review and submit\n\n")
        
        if this_week:
            f.write(f"## 📅 THIS WEEK - Start Working ({len(this_week)} bids)\n\n")
            
            for bid in this_week:
                f.write(f"- **{bid['name']}** - {bid['deadline'].strftime('%b %d')} ({bid['days_left']}d) - ${bid['value']:,}\n")
            
            f.write("\n")
        
        f.write("---\n\n")
        f.write("## ✅ DAILY CHECKLIST\n\n")
        f.write("- [ ] Review urgent bids above\n")
        f.write("- [ ] Follow up on pending quotes\n")
        f.write("- [ ] Check email for new solicitations\n")
        f.write("- [ ] Update bid status in folders\n")
        f.write("- [ ] Submit any ready bids\n\n")
        
        f.write("---\n\n")
        f.write(f"*Generated automatically. Run `python3 auto_bid_manager.py` to refresh.*\n")
    
    print(f"✅ Today's agenda saved: {output_path}\n")
    
    return len(urgent), len(this_week)

def scan_bid_status(folder_path):
    """Quick scan to check bid status"""
    has_quotes = False
    has_submission = False
    
    try:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                f_lower = file.lower()
                if 'quote' in f_lower or 'quotation' in f_lower:
                    has_quotes = True
                if 'submit' in f_lower or 'signed' in f_lower or 'complete' in f_lower:
                    has_submission = True
    except:
        pass
    
    return has_quotes, has_submission

def interactive_status_check():
    """Ask about each bid - still pursuing?"""
    print("🤔 Let's check status of each bid...\n")
    print("(This would normally be interactive, but showing what it would ask)\n")
    
    questions = []
    today = datetime.now()
    
    for bid_name, info in ACTIVE_BIDS.items():
        deadline = parse_deadline(info['deadline'])
        if not deadline:
            continue
        
        days_left = (deadline - today).days
        
        if days_left < 0:
            questions.append({
                'bid': bid_name,
                'question': f"❌ {bid_name} deadline passed. Remove from tracking?",
                'action': 'remove'
            })
        elif days_left <= 7:
            folder_path = os.path.join(BIDS_PATH, bid_name)
            has_quotes, has_submission = scan_bid_status(folder_path)
            
            if has_submission:
                questions.append({
                    'bid': bid_name,
                    'question': f"✅ {bid_name} appears submitted. Mark as complete?",
                    'action': 'complete'
                })
            elif not has_quotes and days_left <= 2:
                questions.append({
                    'bid': bid_name,
                    'question': f"⚠️ {bid_name} due in {days_left} days, no quotes. Still pursuing?",
                    'action': 'pursue_check'
                })
    
    # Save questions to file
    output_path = "BID_STATUS_QUESTIONS.md"
    
    with open(output_path, 'w') as f:
        f.write(f"# 🤔 BID STATUS QUESTIONS\n")
        f.write(f"**Generated:** {today.strftime('%A, %B %d, %Y')}\n\n")
        f.write("**Answer these questions to keep your bid list clean:**\n\n")
        f.write("---\n\n")
        
        for i, q in enumerate(questions, 1):
            f.write(f"## {i}. {q['question']}\n\n")
            f.write(f"**Bid:** {q['bid']}\n")
            f.write(f"**Folder:** `BIDS:RESOURCES/{q['bid']}/`\n\n")
            f.write("**Your Answer:**\n")
            f.write("- [ ] Yes\n")
            f.write("- [ ] No\n")
            f.write("- [ ] Need to check\n\n")
            f.write("---\n\n")
    
    print(f"✅ Status questions saved: {output_path}")
    print(f"   {len(questions)} questions to answer\n")
    
    return len(questions)

def send_notification(urgent_count, this_week_count, calendar_count):
    """Send macOS notification"""
    title = "NEXUS Bid Manager"
    message = f"🔥 {urgent_count} urgent bids\\n📅 {this_week_count} this week\\n📆 {calendar_count} calendar events"
    
    cmd = f'''osascript -e 'display notification "{message}" with title "{title}" sound name "Frog"' '''
    os.system(cmd)

def main():
    """Run complete automated workflow"""
    print("="*80)
    print("🤖 NEXUS AUTOMATED BID MANAGER")
    print("="*80)
    print("\n")
    
    # 1. Generate calendars
    calendar_count = generate_all_calendars()
    
    # 2. Generate daily agenda
    urgent_count, this_week_count = generate_daily_agenda()
    
    # 3. Generate status questions
    questions_count = interactive_status_check()
    
    print("="*80)
    print("✅ AUTOMATION COMPLETE")
    print("="*80)
    print(f"\n📊 Summary:")
    print(f"   - 📅 Calendar events: {calendar_count}")
    print(f"   - 🔥 Urgent bids: {urgent_count}")
    print(f"   - 📅 This week: {this_week_count}")
    print(f"   - 🤔 Status questions: {questions_count}")
    
    print(f"\n📂 Files Generated:")
    print(f"   - TODAY_AGENDA.md (your daily todo list)")
    print(f"   - BID_STATUS_QUESTIONS.md (answer these)")
    print(f"   - calendars/*.ics ({calendar_count} files to import)")
    
    print(f"\n🎯 Next Steps:")
    print(f"   1. Open TODAY_AGENDA.md - work on urgent bids")
    print(f"   2. Import calendar/*.ics files to your calendar")
    print(f"   3. Answer questions in BID_STATUS_QUESTIONS.md")
    
    # Send notification
    send_notification(urgent_count, this_week_count, calendar_count)
    
    print(f"\n💡 To run automatically every morning:")
    print(f"   Add to crontab: 0 7 * * * cd '{os.getcwd()}' && python3 auto_bid_manager.py")
    print("\n")

if __name__ == "__main__":
    main()
