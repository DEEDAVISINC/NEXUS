#!/usr/bin/env python3
"""
COMPLETE BID TRACKING DASHBOARD
Shows EVERYTHING about each bid at a glance:
- Due date & days left
- Current status (sourcing, waiting, ready, submitted)
- Quote status
- Documents status
- Priority level
"""

import os
import json
from datetime import datetime, timedelta
from pathlib import Path

BIDS_PATH = "/Users/deedavis/NEXUS BACKEND/BIDS:RESOURCES"

def scan_bid_folder(folder_path):
    """Analyze bid folder to determine status"""
    status = {
        'has_solicitation': False,
        'has_analysis': False,
        'has_quotes': False,
        'has_submission': False,
        'quote_files': [],
        'analysis_files': [],
        'submission_files': [],
        'deadline': None,
        'deadline_str': '',
        'days_left': None
    }
    
    # Check for files
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_lower = file.lower()
            
            # Solicitation PDF
            if file.endswith('.pdf') and any(x in file_lower for x in ['rfq', 'rfp', 'itb', 'solicitation', 'bid']):
                status['has_solicitation'] = True
            
            # Analysis documents
            if file.endswith('.md') and any(x in file_lower for x in ['analysis', 'strategy', 'quick', 'guide', 'review']):
                status['has_analysis'] = True
                status['analysis_files'].append(file)
                
                # Try to extract deadline
                if not status['deadline']:
                    file_path = os.path.join(root, file)
                    deadline = extract_deadline_from_file(file_path)
                    if deadline:
                        status['deadline'] = deadline
                        status['deadline_str'] = deadline.strftime('%a, %b %d')
                        status['days_left'] = (deadline - datetime.now()).days
            
            # Quote files
            if file.endswith('.pdf') and any(x in file_lower for x in ['quote', 'quotation', 'pricing', 'grainger']):
                status['has_quotes'] = True
                status['quote_files'].append(file)
            
            # Submission files
            if any(x in file_lower for x in ['submit', 'signed', 'complete', 'final']):
                status['has_submission'] = True
                status['submission_files'].append(file)
    
    return status

def extract_deadline_from_file(file_path):
    """Extract deadline date from file"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
            # Look for "**Deadline:**" pattern (highest priority)
            import re
            patterns = [
                r'\*\*Deadline:\*\*\s+([A-Za-z]+,?\s+[A-Za-z]+\s+\d{1,2},?\s+\d{4})',
                r'Deadline[:\s]+([A-Za-z]+,?\s+[A-Za-z]+\s+\d{1,2},?\s+\d{4})',
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    date_str = matches[0]
                    
                    for fmt in ['%A, %B %d, %Y', '%B %d, %Y', '%a, %b %d, %Y']:
                        try:
                            return datetime.strptime(date_str, fmt)
                        except:
                            continue
    except:
        pass
    
    return None

def determine_bid_status(folder_status, days_left):
    """Determine overall bid status based on folder contents"""
    
    if folder_status['has_submission']:
        return "✅ SUBMITTED", "green"
    
    if not folder_status['has_solicitation']:
        return "❓ NO SOLICITATION", "gray"
    
    if not folder_status['has_analysis']:
        return "📥 NEW (Need Analysis)", "blue"
    
    if folder_status['has_quotes']:
        if days_left and days_left <= 3:
            return "🎯 READY TO SUBMIT", "yellow"
        return "📝 HAS QUOTES (Review)", "cyan"
    
    if folder_status['has_analysis']:
        if days_left and days_left <= 2:
            return "🔥 URGENT (No Quotes!)", "red"
        return "⏳ SOURCING QUOTES", "orange"
    
    return "❓ UNKNOWN", "gray"

def generate_dashboard():
    """Generate complete bid tracking dashboard"""
    
    print("🔍 Scanning all bid folders for complete status...\n")
    
    if not os.path.exists(BIDS_PATH):
        print(f"❌ Path not found: {BIDS_PATH}")
        return
    
    all_bids = []
    today = datetime.now()
    
    # Scan all folders
    for folder in sorted(os.listdir(BIDS_PATH)):
        folder_path = os.path.join(BIDS_PATH, folder)
        
        if folder.startswith('.') or not os.path.isdir(folder_path):
            continue
        
        # Skip reference folders
        if any(x in folder.upper() for x in ['MASTER FILES', 'REFERENCE', 'GUIDE', 'SCORECARD', 'LEGAL', 'COMPANY FORMS']):
            continue
        
        # Scan folder
        folder_status = scan_bid_folder(folder_path)
        
        # Only include if has deadline in next 30 days
        if folder_status['deadline'] and folder_status['days_left'] is not None:
            if 0 <= folder_status['days_left'] <= 30:
                status_text, status_color = determine_bid_status(folder_status, folder_status['days_left'])
                
                all_bids.append({
                    'folder': folder,
                    'deadline': folder_status['deadline'],
                    'deadline_str': folder_status['deadline_str'],
                    'days_left': folder_status['days_left'],
                    'status': status_text,
                    'status_color': status_color,
                    'has_solicitation': folder_status['has_solicitation'],
                    'has_analysis': folder_status['has_analysis'],
                    'has_quotes': folder_status['has_quotes'],
                    'quote_count': len(folder_status['quote_files']),
                    'has_submission': folder_status['has_submission']
                })
    
    # Sort by days left
    all_bids.sort(key=lambda x: x['days_left'])
    
    # Generate markdown dashboard
    output_path = "BID_TRACKER_DASHBOARD.md"
    
    with open(output_path, 'w') as f:
        f.write("# 📊 BID TRACKER DASHBOARD - COMPLETE STATUS\n")
        f.write(f"**Updated:** {today.strftime('%A, %B %d, %Y at %I:%M %p')}\n")
        f.write(f"**Active Bids:** {len(all_bids)}\n\n")
        f.write("---\n\n")
        
        f.write("## 📋 LEGEND\n\n")
        f.write("**Status:**\n")
        f.write("- ✅ SUBMITTED = Bid already submitted\n")
        f.write("- 🎯 READY TO SUBMIT = Have quotes, ready to finalize\n")
        f.write("- 📝 HAS QUOTES = Quotes received, need to review\n")
        f.write("- ⏳ SOURCING QUOTES = Analysis done, waiting for supplier quotes\n")
        f.write("- 🔥 URGENT = Deadline ≤2 days, no quotes yet!\n")
        f.write("- 📥 NEW = Just added, need analysis\n\n")
        
        f.write("**Columns:**\n")
        f.write("- 📄 = Has solicitation PDF\n")
        f.write("- 📊 = Has analysis/strategy doc\n")
        f.write("- 💰 = Has supplier quotes\n")
        f.write("- ✅ = Submission ready/complete\n\n")
        
        f.write("---\n\n")
        
        # Group by urgency
        urgent = [b for b in all_bids if b['days_left'] <= 3]
        this_week = [b for b in all_bids if 3 < b['days_left'] <= 7]
        next_week = [b for b in all_bids if 7 < b['days_left'] <= 14]
        later = [b for b in all_bids if b['days_left'] > 14]
        
        # Stats
        f.write("## 📈 SUMMARY\n\n")
        f.write(f"| Category | Count | Action Needed |\n")
        f.write(f"|----------|-------|---------------|\n")
        f.write(f"| 🔥 URGENT (≤3 days) | {len(urgent)} | **IMMEDIATE ACTION** |\n")
        f.write(f"| 📅 This Week (4-7 days) | {len(this_week)} | Start sourcing quotes |\n")
        f.write(f"| 📆 Next Week (8-14 days) | {len(next_week)} | Review & analyze |\n")
        f.write(f"| 📋 Later (15-30 days) | {len(later)} | Monitor |\n\n")
        
        f.write("---\n\n")
        
        # Urgent section
        if urgent:
            f.write(f"## 🔥 URGENT - NEXT 3 DAYS ({len(urgent)})\n\n")
            f.write("| Bid | Deadline | Days | Status | 📄 | 📊 | 💰 | ✅ |\n")
            f.write("|-----|----------|------|--------|---|---|---|---|\n")
            
            for bid in urgent:
                emoji_pdf = "✅" if bid['has_solicitation'] else "❌"
                emoji_analysis = "✅" if bid['has_analysis'] else "❌"
                emoji_quotes = f"{bid['quote_count']}✅" if bid['has_quotes'] else "❌"
                emoji_submit = "✅" if bid['has_submission'] else "⏳"
                
                days_emoji = "🔴" if bid['days_left'] <= 1 else "⚠️"
                
                f.write(f"| **{bid['folder']}** | {bid['deadline_str']} | {days_emoji} {bid['days_left']}d | {bid['status']} | {emoji_pdf} | {emoji_analysis} | {emoji_quotes} | {emoji_submit} |\n")
            
            f.write("\n")
        
        # This week
        if this_week:
            f.write(f"## 📅 THIS WEEK - 4-7 DAYS ({len(this_week)})\n\n")
            f.write("| Bid | Deadline | Days | Status | 📄 | 📊 | 💰 | ✅ |\n")
            f.write("|-----|----------|------|--------|---|---|---|---|\n")
            
            for bid in this_week:
                emoji_pdf = "✅" if bid['has_solicitation'] else "❌"
                emoji_analysis = "✅" if bid['has_analysis'] else "❌"
                emoji_quotes = f"{bid['quote_count']}✅" if bid['has_quotes'] else "❌"
                emoji_submit = "✅" if bid['has_submission'] else "⏳"
                
                f.write(f"| {bid['folder']} | {bid['deadline_str']} | {bid['days_left']}d | {bid['status']} | {emoji_pdf} | {emoji_analysis} | {emoji_quotes} | {emoji_submit} |\n")
            
            f.write("\n")
        
        # Next week (compact)
        if next_week:
            f.write(f"## 📆 NEXT WEEK - 8-14 DAYS ({len(next_week)})\n\n")
            
            for bid in next_week:
                status_icon = "✅" if bid['has_submission'] else "📝" if bid['has_quotes'] else "⏳"
                f.write(f"- {status_icon} **{bid['folder']}** - {bid['deadline_str']} ({bid['days_left']}d) - {bid['status']}\n")
            
            f.write("\n")
        
        # Later (compact)
        if later:
            f.write(f"## 📋 LATER - 15-30 DAYS ({len(later)})\n\n")
            
            for bid in later:
                status_icon = "✅" if bid['has_submission'] else "📝" if bid['has_quotes'] else "⏳"
                f.write(f"- {status_icon} {bid['folder']} - {bid['deadline_str']}\n")
            
            f.write("\n")
        
        f.write("---\n\n")
        f.write("## 🎯 NEXT ACTIONS\n\n")
        
        # Identify what needs attention
        need_quotes = [b for b in urgent + this_week if not b['has_quotes'] and not b['has_submission']]
        have_quotes = [b for b in urgent + this_week if b['has_quotes'] and not b['has_submission']]
        
        if need_quotes:
            f.write(f"### 🔥 URGENT: Need Quotes ({len(need_quotes)})\n\n")
            for bid in need_quotes:
                f.write(f"1. **{bid['folder']}** - {bid['days_left']} days left!\n")
                f.write(f"   - [ ] Find suppliers/subcontractors\n")
                f.write(f"   - [ ] Request quotes\n")
                f.write(f"   - [ ] Follow up\n\n")
        
        if have_quotes:
            f.write(f"### 📝 Review & Submit ({len(have_quotes)})\n\n")
            for bid in have_quotes:
                f.write(f"1. **{bid['folder']}** - {bid['quote_count']} quote(s) received\n")
                f.write(f"   - [ ] Review quotes\n")
                f.write(f"   - [ ] Prepare bid package\n")
                f.write(f"   - [ ] Submit before {bid['deadline_str']}\n\n")
        
        f.write("---\n\n")
        f.write(f"*Run `python3 build_bid_tracker_dashboard.py` to refresh this dashboard.*\n")
    
    print(f"✅ Dashboard generated: {output_path}")
    print(f"\n📊 Status Breakdown:")
    print(f"   - 🔥 Urgent (≤3 days): {len(urgent)}")
    print(f"   - 📅 This Week (4-7 days): {len(this_week)}")
    print(f"   - 📆 Next Week (8-14 days): {len(next_week)}")
    print(f"   - 📋 Later (15-30 days): {len(later)}")
    
    # Also save as JSON for programmatic access
    json_output = "bid_tracker_data.json"
    with open(json_output, 'w') as f:
        json.dump({
            'updated': today.isoformat(),
            'total_bids': len(all_bids),
            'bids': [{
                'folder': b['folder'],
                'deadline': b['deadline'].isoformat(),
                'days_left': b['days_left'],
                'status': b['status'],
                'has_solicitation': b['has_solicitation'],
                'has_analysis': b['has_analysis'],
                'has_quotes': b['has_quotes'],
                'quote_count': b['quote_count'],
                'has_submission': b['has_submission']
            } for b in all_bids]
        }, f, indent=2)
    
    print(f"✅ JSON data saved: {json_output}")
    print(f"\n🎯 Open BID_TRACKER_DASHBOARD.md to see complete status!")

if __name__ == "__main__":
    generate_dashboard()
