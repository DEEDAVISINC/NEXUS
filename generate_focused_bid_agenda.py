#!/usr/bin/env python3
"""
Generate FOCUSED Bid Agenda - Only shows bids you're actively working on
Checks: BIDS:RESOURCES folders + Monday action plan + Recent activity
"""

import os
from datetime import datetime, timedelta
from pyairtable import Api
from dotenv import load_dotenv

load_dotenv()

api = Api(os.getenv('AIRTABLE_API_KEY'))
base_id = os.getenv('AIRTABLE_BASE_ID')
opportunities = api.table(base_id, 'GPSS OPPORTUNITIES')

def get_active_bid_folders():
    """Get list of bids you're actively working on from BIDS:RESOURCES"""
    bids_path = "/Users/deedavis/NEXUS BACKEND/BIDS:RESOURCES"
    if not os.path.exists(bids_path):
        return []
    
    folders = []
    for item in os.listdir(bids_path):
        item_path = os.path.join(bids_path, item)
        if os.path.isdir(item_path) and not item.startswith('.'):
            folders.append(item.upper())
    return folders

def generate_focused_agenda():
    """Generate focused agenda with only active bids"""
    
    print("📊 Generating FOCUSED bid agenda...")
    
    # Get active bid folders
    active_folders = get_active_bid_folders()
    print(f"   Found {len(active_folders)} active bid folders in BIDS:RESOURCES")
    
    # Get all opportunities
    all_opps = opportunities.all()
    
    # Find matching opportunities
    active_bids = []
    today = datetime.now()
    
    for record in all_opps:
        fields = record.get('fields', {})
        name = fields.get('Name', '').upper()
        
        # Check if this bid has a folder (you're actively working on it)
        is_active = False
        for folder in active_folders:
            # Match by folder name
            folder_clean = folder.replace('BIDS:RESOURCES/', '').replace(' ', '').replace('-', '')
            name_clean = name.replace(' ', '').replace('-', '')
            
            if folder_clean in name_clean or name_clean in folder_clean:
                is_active = True
                break
        
        if not is_active:
            # Also check if mentioned in key fields
            rfp = fields.get('RFP NUMBER', '').upper()
            agency = fields.get('AGENCY NAME', '').upper()
            
            for folder in active_folders:
                if rfp and rfp in folder:
                    is_active = True
                    break
                if agency and len(agency) > 5 and agency in folder:
                    is_active = True
                    break
        
        if is_active:
            # Skip if sole source (can't bid)
            if 'SOLE SOURCE' in name.upper():
                continue
            
            # Skip if already submitted
            status = fields.get('STATUS', '').upper()
            if 'SUBMITTED' in status or 'SENT' in status:
                continue
            
            # Get deadline
            deadline_str = fields.get('Deadline')
            if deadline_str:
                try:
                    deadline = datetime.strptime(deadline_str, '%Y-%m-%d')
                    days_left = (deadline - today).days
                    
                    # Only show FUTURE deadlines (not past)
                    if days_left >= 0 and days_left <= 30:
                        active_bids.append({
                            'name': fields.get('Name', 'Unknown'),
                            'rfp': fields.get('RFP NUMBER', ''),
                            'deadline': deadline,
                            'days_left': days_left,
                            'value': fields.get('VALUE', 0) or 0,
                            'status': fields.get('STATUS', ''),
                            'notes': fields.get('Notes', ''),
                            'agency': fields.get('AGENCY NAME', '')
                        })
                except:
                    pass
    
    # Sort by deadline
    active_bids.sort(key=lambda x: x['days_left'])
    
    # Generate markdown
    agenda_path = "BID_STATUS_AGENDA.md"
    
    with open(agenda_path, 'w') as f:
        f.write(f"# 📊 FOCUSED BID DASHBOARD\n")
        f.write(f"**Generated:** {datetime.now().strftime('%A, %B %d, %Y at %I:%M %p')}\n")
        f.write(f"**Showing:** Only bids you're actively working on\n\n")
        f.write("---\n\n")
        
        # Summary
        urgent = [b for b in active_bids if b['days_left'] <= 3]
        this_week = [b for b in active_bids if 3 < b['days_left'] <= 7]
        next_week = [b for b in active_bids if 7 < b['days_left'] <= 14]
        later = [b for b in active_bids if b['days_left'] > 14]
        
        f.write(f"## 📈 OVERVIEW\n\n")
        f.write(f"- **Active Bids (you're working on):** {len(active_bids)}\n")
        f.write(f"- **Urgent (≤3 days):** {len(urgent)}\n")
        f.write(f"- **This Week (4-7 days):** {len(this_week)}\n")
        f.write(f"- **Next Week (8-14 days):** {len(next_week)}\n")
        f.write(f"- **Later (15-30 days):** {len(later)}\n\n")
        f.write("---\n\n")
        
        # Urgent section
        if urgent:
            f.write(f"## 🔥 URGENT - NEXT 3 DAYS ({len(urgent)})\n\n")
            for bid in urgent:
                f.write(f"### {'⚠️' if bid['days_left'] <= 1 else '🔴'} {bid['name']}\n\n")
                f.write(f"- **Deadline:** {bid['deadline'].strftime('%A, %B %d')} ({bid['days_left']} days)\n")
                if bid['agency']:
                    f.write(f"- **Agency:** {bid['agency']}\n")
                if bid['rfp']:
                    f.write(f"- **RFP#:** {bid['rfp']}\n")
                if bid['value'] > 0:
                    f.write(f"- **Value:** ${bid['value']:,.0f}\n")
                if bid['status']:
                    f.write(f"- **Status:** {bid['status']}\n")
                
                f.write(f"\n**Folder:** `BIDS:RESOURCES/[folder matching this bid]`\n\n")
                f.write(f"**Next Action:** Review bid folder and prepare submission\n\n")
            f.write("---\n\n")
        
        # This week
        if this_week:
            f.write(f"## 📅 THIS WEEK ({len(this_week)})\n\n")
            for bid in this_week:
                f.write(f"### {bid['name']}\n\n")
                f.write(f"- **Deadline:** {bid['deadline'].strftime('%A, %B %d')} ({bid['days_left']} days)\n")
                if bid['agency']:
                    f.write(f"- **Agency:** {bid['agency']}\n")
                if bid['value'] > 0:
                    f.write(f"- **Value:** ${bid['value']:,.0f}\n")
                f.write(f"\n")
            f.write("---\n\n")
        
        # Next week
        if next_week:
            f.write(f"## 📆 NEXT WEEK ({len(next_week)})\n\n")
            for bid in next_week:
                f.write(f"- **{bid['name']}** - {bid['deadline'].strftime('%b %d')} ({bid['days_left']} days)\n")
            f.write("\n---\n\n")
        
        # Later
        if later:
            f.write(f"## 📋 LATER (15-30 days) ({len(later)})\n\n")
            for bid in later:
                f.write(f"- {bid['name']} - {bid['deadline'].strftime('%b %d')}\n")
            f.write("\n---\n\n")
        
        # Action list
        f.write(f"## 🎯 TODAY'S PRIORITIES\n\n")
        if urgent:
            f.write(f"1. **URGENT:** Complete {len(urgent)} bid(s) due in next 3 days\n")
        if this_week:
            f.write(f"2. **THIS WEEK:** Prepare {len(this_week)} bid(s) due this week\n")
        if next_week:
            f.write(f"3. **NEXT WEEK:** Start work on {len(next_week)} bid(s) due next week\n")
        
        if not active_bids:
            f.write("✨ No active bids found with upcoming deadlines!\n\n")
            f.write("**Tip:** Drop bid PDFs in `photos_and_videos/` to auto-process them.\n")
        
        f.write("\n---\n\n")
        f.write("*This focused agenda shows only bids in your BIDS:RESOURCES folder.*\n")
        f.write("*Run `python3 generate_focused_bid_agenda.py` to refresh.*\n")
    
    print(f"✅ Focused agenda generated: {agenda_path}")
    print(f"\n📊 Summary:")
    print(f"   - Urgent (≤3 days): {len(urgent)}")
    print(f"   - This Week (4-7 days): {len(this_week)}")
    print(f"   - Next Week (8-14 days): {len(next_week)}")
    print(f"   - Later (15-30 days): {len(later)}")
    print(f"\n🎯 Open BID_STATUS_AGENDA.md to see your focused action list!")

if __name__ == "__main__":
    generate_focused_agenda()
