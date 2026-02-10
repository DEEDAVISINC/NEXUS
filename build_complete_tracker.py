#!/usr/bin/env python3
"""
ULTIMATE BID TRACKER - Combines deadline scan with status tracking
Shows EVERYTHING at a glance
"""

import os
import re
from datetime import datetime
from pathlib import Path

BIDS_PATH = "/Users/deedavis/NEXUS BACKEND/BIDS:RESOURCES"

# Manual deadline data from bids we know about
KNOWN_DEADLINES = {
    'OAKLAND COUNTY FLOW METERS': 'February 12, 2026',
    'OAKLAND COUNTY TREATED SALT': 'February 12, 2026',
    'PORT HURON CHEMICALS': 'February 12, 2026',
    'CPS ENERGY': 'February 11, 2026',
    'CPS ENERGY PADLOCKS': 'February 13, 2026',  # Guardrails subfolder
    'HENRY FORD BATTERY CABINETS': 'February 11, 2026',
    'AUBURN HILLS PRESSURE WASHING': 'February 13, 2026',
    'SHELBY TOWNSHIP POWER CABLES': 'February 13, 2026',
    'OAKLAND COUNTY EXAM STOOLS': 'February 16, 2026',
    'OAKLAND COUNTY TRUCK EQUIPMENT': 'February 17, 2026',
    'RCOC 7790 SIGNS': 'February 17, 2026',
    'RCOC 7842 SAFETY SUPPLIES': 'February 17, 2026',
    'GENESEE WOOD POLES': 'February 18, 2026',
    'HCMA CHLORINE': 'February 18, 2026',
    'LIVONIA MATERIALS': 'February 23, 2026',
    'HCMA UTILITY VEHICLES': 'February 25, 2026',
    'ALASKA STEEL CONTAINERS': 'March 2, 2026',
}

def parse_deadline(date_str):
    """Parse deadline string to datetime"""
    for fmt in ['%B %d, %Y', '%b %d, %Y']:
        try:
            return datetime.strptime(date_str, fmt)
        except:
            continue
    return None

def scan_bid_status(folder_path):
    """Quick scan of folder status"""
    status = {
        'has_pdf': False,
        'has_analysis': False,
        'has_quotes': False,
        'quote_count': 0,
        'has_submission': False
    }
    
    try:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                f_lower = file.lower()
                
                if file.endswith('.pdf'):
                    if any(x in f_lower for x in ['rfq', 'rfp', 'itb', 'solicitation']):
                        status['has_pdf'] = True
                    if any(x in f_lower for x in ['quote', 'quotation', 'pricing']):
                        status['has_quotes'] = True
                        status['quote_count'] += 1
                
                if file.endswith('.md'):
                    if any(x in f_lower for x in ['analysis', 'strategy', 'review', 'quick']):
                        status['has_analysis'] = True
                    if any(x in f_lower for x in ['submit', 'complete', 'signed', 'final']):
                        status['has_submission'] = True
    except:
        pass
    
    return status

def determine_status(bid_status, days_left):
    """Determine bid status"""
    if bid_status['has_submission']:
        return "✅ SUBMITTED"
    if bid_status['has_quotes'] and days_left <= 3:
        return "🎯 READY"
    if bid_status['has_quotes']:
        return "📝 HAS QUOTES"
    if bid_status['has_analysis'] and days_left <= 2:
        return "🔥 URGENT!"
    if bid_status['has_analysis']:
        return "⏳ SOURCING"
    if bid_status['has_pdf']:
        return "📥 NEW"
    return "❓ UNKNOWN"

def generate_tracker():
    """Generate complete tracker"""
    print("🔍 Building complete bid tracker...\n")
    
    all_bids = []
    today = datetime.now()
    
    # Process known deadlines
    for folder_name, deadline_str in KNOWN_DEADLINES.items():
        folder_path = os.path.join(BIDS_PATH, folder_name)
        
        if not os.path.exists(folder_path):
            continue
        
        deadline = parse_deadline(deadline_str)
        if not deadline:
            continue
        
        days_left = (deadline - today).days
        
        # Only include next 30 days
        if 0 <= days_left <= 30:
            bid_status = scan_bid_status(folder_path)
            status_text = determine_status(bid_status, days_left)
            
            all_bids.append({
                'folder': folder_name,
                'deadline': deadline,
                'deadline_str': deadline.strftime('%a, %b %d'),
                'days_left': days_left,
                'status': status_text,
                **bid_status
            })
    
    # Sort by days left
    all_bids.sort(key=lambda x: x['days_left'])
    
    # Generate markdown
    output = "BID_TRACKER_COMPLETE.md"
    
    with open(output, 'w') as f:
        f.write("# 📊 COMPLETE BID TRACKER - ALL STATUS AT A GLANCE\n")
        f.write(f"**Updated:** {today.strftime('%A, %B %d, %Y at %I:%M %p')}\n")
        f.write(f"**Active Bids (Next 30 Days):** {len(all_bids)}\n\n")
        f.write("---\n\n")
        
        f.write("## 📋 STATUS LEGEND\n\n")
        f.write("| Symbol | Meaning |\n")
        f.write("|--------|----------|\n")
        f.write("| ✅ SUBMITTED | Bid already submitted |\n")
        f.write("| 🎯 READY | Have quotes, ready to submit |\n")
        f.write("| 📝 HAS QUOTES | Quotes received, need review |\n")
        f.write("| ⏳ SOURCING | Looking for suppliers/quotes |\n")
        f.write("| 🔥 URGENT! | Deadline ≤2 days, NO quotes! |\n")
        f.write("| 📥 NEW | Just added, needs analysis |\n")
        f.write("| ❓ UNKNOWN | Status unclear |\n\n")
        
        f.write("**File Status:**\n")
        f.write("- 📄 = Solicitation PDF | 📊 = Analysis Doc | 💰 = Supplier Quotes | ✅ = Submitted\n\n")
        
        f.write("---\n\n")
        
        # Group by urgency
        urgent = [b for b in all_bids if b['days_left'] <= 3]
        this_week = [b for b in all_bids if 3 < b['days_left'] <= 7]
        next_week = [b for b in all_bids if 7 < b['days_left'] <= 14]
        later = [b for b in all_bids if b['days_left'] > 14]
        
        f.write("## 📈 QUICK STATS\n\n")
        f.write(f"| Timeframe | Count | Action |\n")
        f.write(f"|-----------|-------|--------|\n")
        f.write(f"| 🔥 URGENT (≤3 days) | **{len(urgent)}** | **DROP EVERYTHING** |\n")
        f.write(f"| 📅 This Week (4-7 days) | {len(this_week)} | Get quotes ASAP |\n")
        f.write(f"| 📆 Next Week (8-14 days) | {len(next_week)} | Start prep |\n")
        f.write(f"| 📋 Later (15-30 days) | {len(later)} | Monitor |\n\n")
        
        f.write("---\n\n")
        
        # URGENT TABLE
        if urgent:
            f.write(f"## 🔥 URGENT - NEXT 3 DAYS ({len(urgent)})\n\n")
            f.write("| # | Bid Name | Due | Days | Status | 📄 | 📊 | 💰 | ✅ | Action |\n")
            f.write("|---|----------|-----|------|--------|---|---|---|---|--------|\n")
            
            for i, bid in enumerate(urgent, 1):
                pdf = "✅" if bid['has_pdf'] else "❌"
                analysis = "✅" if bid['has_analysis'] else "❌"
                quotes = f"{bid['quote_count']}✅" if bid['has_quotes'] else "❌"
                submit = "✅" if bid['has_submission'] else "❌"
                
                action = ""
                if bid['has_submission']:
                    action = "Done!"
                elif bid['has_quotes']:
                    action = "Review & Submit"
                else:
                    action = "**GET QUOTES NOW**"
                
                f.write(f"| {i} | **{bid['folder']}** | {bid['deadline_str']} | 🔴**{bid['days_left']}** | {bid['status']} | {pdf} | {analysis} | {quotes} | {submit} | {action} |\n")
            
            f.write("\n")
        
        # THIS WEEK
        if this_week:
            f.write(f"## 📅 THIS WEEK - 4-7 DAYS ({len(this_week)})\n\n")
            f.write("| # | Bid Name | Due | Days | Status | 📄 | 📊 | 💰 | Action |\n")
            f.write("|---|----------|-----|------|--------|---|---|---|--------|\n")
            
            for i, bid in enumerate(this_week, 1):
                pdf = "✅" if bid['has_pdf'] else "❌"
                analysis = "✅" if bid['has_analysis'] else "❌"
                quotes = f"{bid['quote_count']}✅" if bid['has_quotes'] else "❌"
                
                action = ""
                if bid['has_submission']:
                    action = "✅ Done"
                elif bid['has_quotes']:
                    action = "Review quotes"
                elif bid['has_analysis']:
                    action = "Get quotes"
                else:
                    action = "Analyze bid"
                
                f.write(f"| {i} | {bid['folder']} | {bid['deadline_str']} | {bid['days_left']}d | {bid['status']} | {pdf} | {analysis} | {quotes} | {action} |\n")
            
            f.write("\n")
        
        # NEXT WEEK (simpler)
        if next_week:
            f.write(f"## 📆 NEXT WEEK - 8-14 DAYS ({len(next_week)})\n\n")
            for bid in next_week:
                icon = "✅" if bid['has_submission'] else "📝" if bid['has_quotes'] else "⏳"
                f.write(f"{icon} **{bid['folder']}** - {bid['deadline_str']} ({bid['days_left']}d) - {bid['status']}\n")
            f.write("\n")
        
        # LATER (compact)
        if later:
            f.write(f"## 📋 LATER - 15-30 DAYS ({len(later)})\n\n")
            for bid in later:
                icon = "✅" if bid['has_submission'] else "📝" if bid['has_quotes'] else "⏳"
                f.write(f"{icon} {bid['folder']} - {bid['deadline_str']}\n")
            f.write("\n")
        
        f.write("---\n\n")
        f.write("## 🎯 IMMEDIATE PRIORITIES\n\n")
        
        # What needs immediate action
        need_quotes_urgent = [b for b in urgent if not b['has_quotes'] and not b['has_submission']]
        need_submit_urgent = [b for b in urgent if b['has_quotes'] and not b['has_submission']]
        
        if need_quotes_urgent:
            f.write(f"### 🚨 GET QUOTES NOW ({len(need_quotes_urgent)} bids)\n\n")
            for bid in need_quotes_urgent:
                f.write(f"**{bid['folder']}** - {bid['days_left']} days left!\n")
                f.write(f"- [ ] Find suppliers/subs\n")
                f.write(f"- [ ] Request quotes\n")
                f.write(f"- [ ] Folder: `BIDS:RESOURCES/{bid['folder']}/`\n\n")
        
        if need_submit_urgent:
            f.write(f"### 📝 REVIEW & SUBMIT ({len(need_submit_urgent)} bids)\n\n")
            for bid in need_submit_urgent:
                f.write(f"**{bid['folder']}** - {bid['quote_count']} quote(s) ready\n")
                f.write(f"- [ ] Review quotes\n")
                f.write(f"- [ ] Complete bid forms\n")
                f.write(f"- [ ] Submit by {bid['deadline_str']}\n\n")
        
        f.write("---\n\n")
        f.write("## 💡 HOW TO UPDATE\n\n")
        f.write("```bash\n")
        f.write("# Refresh this dashboard\n")
        f.write("python3 build_complete_tracker.py\n")
        f.write("```\n\n")
        f.write("**To add more bids:** Edit `KNOWN_DEADLINES` dict in `build_complete_tracker.py`\n\n")
        f.write("---\n\n")
        f.write(f"*This is YOUR mission control. Review daily!*\n")
    
    print(f"✅ Complete tracker generated: {output}")
    print(f"\n📊 Breakdown:")
    print(f"   🔥 URGENT (≤3 days): {len(urgent)}")
    print(f"   📅 This Week (4-7 days): {len(this_week)}")
    print(f"   📆 Next Week (8-14 days): {len(next_week)}")
    print(f"   📋 Later (15-30 days): {len(later)}")
    
    if need_quotes_urgent:
        print(f"\n🚨 CRITICAL: {len(need_quotes_urgent)} bids need quotes IMMEDIATELY!")
        for bid in need_quotes_urgent:
            print(f"   - {bid['folder']} ({bid['days_left']} days)")

if __name__ == "__main__":
    generate_tracker()
