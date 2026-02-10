#!/usr/bin/env python3
"""
Scan ALL bid folders and extract deadlines/status
Creates comprehensive dashboard of ALL active bids
"""

import os
import re
from datetime import datetime
from pathlib import Path

BIDS_PATH = "/Users/deedavis/NEXUS BACKEND/BIDS:RESOURCES"

def extract_deadline_from_folder(folder_path):
    """Extract deadline from any analysis/readme files in folder (including subfolders)"""
    # Check main folder
    for file in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file)
        
        # Check subfolders
        if os.path.isdir(file_path) and not file.startswith('.'):
            deadline = extract_deadline_from_folder(file_path)
            if deadline:
                return deadline
        
        # Check markdown files
        if file.endswith('.md') and any(x in file.upper() for x in ['ANALYSIS', 'README', 'QUICK', 'STRATEGY', 'CALL', 'ACTION']):
            file_path = os.path.join(folder_path, file)
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                    
                    # Look for deadline patterns (prioritize "Deadline:" over other dates)
                    patterns = [
                        (r'\*\*Deadline:\*\*\s+([A-Za-z]+,?\s+[A-Za-z]+\s+\d{1,2},?\s+\d{4})', 100),  # Highest priority
                        (r'Deadline[:\s]+([A-Za-z]+,?\s+[A-Za-z]+\s+\d{1,2},?\s+\d{4})', 90),
                        (r'Due Date[:\s]+([A-Za-z]+,?\s+[A-Za-z]+\s+\d{1,2},?\s+\d{4})', 80),
                        (r'Closing[:\s]+([A-Za-z]+,?\s+[A-Za-z]+\s+\d{1,2},?\s+\d{4})', 70),
                        (r'Submit by[:\s]+([A-Za-z]+,?\s+[A-Za-z]+\s+\d{1,2})', 60),
                    ]
                    
                    best_deadline = None
                    best_priority = 0
                    
                    for pattern, priority in patterns:
                        matches = re.findall(pattern, content, re.IGNORECASE)
                        if matches:
                            for match in matches:
                                if isinstance(match, tuple):
                                    date_str = ' '.join(match)
                                else:
                                    date_str = match
                                
                                # Add year if missing
                                if '2026' not in date_str and '2027' not in date_str:
                                    # Try to add year
                                    if 'Feb' in date_str or 'Mar' in date_str:
                                        date_str = date_str + ', 2026'
                                    elif re.match(r'^\d{1,2}$', date_str.strip()):
                                        # Just a number like "12"
                                        date_str = f'February {date_str}, 2026'
                                
                                # Try to parse
                                formats = [
                                    '%A, %B %d, %Y',
                                    '%B %d, %Y',
                                    '%m/%d/%Y',
                                    '%B %d %Y',
                                    '%b %d, %Y'
                                ]
                                for fmt in formats:
                                    try:
                                        deadline = datetime.strptime(date_str, fmt)
                                        if priority > best_priority:
                                            best_deadline = deadline
                                            best_priority = priority
                                    except:
                                        continue
                    
                    if best_deadline:
                        return best_deadline
            except:
                pass
    return None

def scan_all_bids():
    """Scan all bid folders"""
    print("🔍 Scanning all bid folders...\n")
    
    if not os.path.exists(BIDS_PATH):
        print(f"❌ Path not found: {BIDS_PATH}")
        return
    
    bids = []
    today = datetime.now()
    
    for folder in sorted(os.listdir(BIDS_PATH)):
        folder_path = os.path.join(BIDS_PATH, folder)
        
        # Skip hidden and non-directories
        if folder.startswith('.') or not os.path.isdir(folder_path):
            continue
        
        # Skip reference folders
        if any(x in folder.upper() for x in ['MASTER FILES', 'REFERENCE', 'GUIDES', 'SCORECARDS']):
            continue
        
        # Get deadline
        deadline = extract_deadline_from_folder(folder_path)
        
        if deadline:
            days_left = (deadline - today).days
            
            # Only show future deadlines in next 60 days
            if 0 <= days_left <= 60:
                bids.append({
                    'folder': folder,
                    'deadline': deadline,
                    'days_left': days_left
                })
        else:
            # No deadline found - might be old or reference
            pass
    
    # Sort by deadline
    bids.sort(key=lambda x: x['days_left'])
    
    # Generate markdown
    output_path = "ALL_ACTIVE_BIDS.md"
    
    with open(output_path, 'w') as f:
        f.write(f"# 📊 ALL ACTIVE BIDS - COMPLETE LIST\n")
        f.write(f"**Generated:** {datetime.now().strftime('%A, %B %d, %Y at %I:%M %p')}\n")
        f.write(f"**Total:** {len(bids)} bids with upcoming deadlines\n\n")
        f.write("---\n\n")
        
        # Group by urgency
        urgent = [b for b in bids if b['days_left'] <= 3]
        this_week = [b for b in bids if 3 < b['days_left'] <= 7]
        next_week = [b for b in bids if 7 < b['days_left'] <= 14]
        this_month = [b for b in bids if 14 < b['days_left'] <= 30]
        later = [b for b in bids if b['days_left'] > 30]
        
        f.write(f"## 📈 OVERVIEW\n\n")
        f.write(f"- **Urgent (≤3 days):** {len(urgent)}\n")
        f.write(f"- **This Week (4-7 days):** {len(this_week)}\n")
        f.write(f"- **Next Week (8-14 days):** {len(next_week)}\n")
        f.write(f"- **This Month (15-30 days):** {len(this_month)}\n")
        f.write(f"- **Later (31-60 days):** {len(later)}\n\n")
        f.write("---\n\n")
        
        # Urgent
        if urgent:
            f.write(f"## 🔥 URGENT - NEXT 3 DAYS ({len(urgent)})\n\n")
            for bid in urgent:
                days_emoji = '🔴' if bid['days_left'] <= 1 else '⚠️'
                f.write(f"### {days_emoji} {bid['folder']}\n")
                f.write(f"- **Deadline:** {bid['deadline'].strftime('%A, %B %d, %Y')} ({bid['days_left']} days)\n")
                f.write(f"- **Folder:** `BIDS:RESOURCES/{bid['folder']}/`\n\n")
            f.write("---\n\n")
        
        # This week
        if this_week:
            f.write(f"## 📅 THIS WEEK - 4-7 DAYS ({len(this_week)})\n\n")
            for bid in this_week:
                f.write(f"### {bid['folder']}\n")
                f.write(f"- **Deadline:** {bid['deadline'].strftime('%A, %B %d')} ({bid['days_left']} days)\n")
                f.write(f"- **Folder:** `BIDS:RESOURCES/{bid['folder']}/`\n\n")
            f.write("---\n\n")
        
        # Next week
        if next_week:
            f.write(f"## 📆 NEXT WEEK - 8-14 DAYS ({len(next_week)})\n\n")
            for bid in next_week:
                f.write(f"- **{bid['folder']}** - {bid['deadline'].strftime('%b %d')} ({bid['days_left']} days)\n")
            f.write("\n---\n\n")
        
        # This month
        if this_month:
            f.write(f"## 📋 THIS MONTH - 15-30 DAYS ({len(this_month)})\n\n")
            for bid in this_month:
                f.write(f"- {bid['folder']} - {bid['deadline'].strftime('%b %d')} ({bid['days_left']} days)\n")
            f.write("\n---\n\n")
        
        # Later
        if later:
            f.write(f"## 📅 LATER - 31-60 DAYS ({len(later)})\n\n")
            for bid in later:
                f.write(f"- {bid['folder']} - {bid['deadline'].strftime('%b %d')}\n")
            f.write("\n---\n\n")
        
        # Priority summary
        f.write(f"## 🎯 PRIORITIES\n\n")
        if urgent:
            f.write(f"1. **URGENT:** Complete {len(urgent)} bid(s) in next 3 days\n")
        if this_week:
            f.write(f"2. **THIS WEEK:** Work on {len(this_week)} bid(s)\n")
        if next_week:
            f.write(f"3. **NEXT WEEK:** Prepare {len(next_week)} bid(s)\n")
        
        f.write("\n---\n\n")
        f.write(f"*Run `python3 scan_all_active_bids.py` to refresh this list.*\n")
    
    print(f"✅ Complete list generated: {output_path}")
    print(f"\n📊 Found {len(bids)} bids with upcoming deadlines:")
    print(f"   - Urgent (≤3 days): {len(urgent)}")
    print(f"   - This Week (4-7 days): {len(this_week)}")
    print(f"   - Next Week (8-14 days): {len(next_week)}")
    print(f"   - This Month (15-30 days): {len(this_month)}")
    print(f"   - Later (31-60 days): {len(later)}")

if __name__ == "__main__":
    scan_all_bids()
