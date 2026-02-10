#!/usr/bin/env python3
"""
Simple scan: List ALL bid folders and look for deadline mentions
No complex parsing - just show what we find
"""

import os
import re
from datetime import datetime
from pathlib import Path

BIDS_PATH = "/Users/deedavis/NEXUS BACKEND/BIDS:RESOURCES"

def find_deadline_in_folder(folder_path, folder_name):
    """Find any deadline mention in folder"""
    deadlines_found = []
    
    for file in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file)
        
        # Recurse into subfolders
        if os.path.isdir(file_path) and not file.startswith('.'):
            sub_deadlines = find_deadline_in_folder(file_path, folder_name)
            deadlines_found.extend(sub_deadlines)
            continue
        
        # Check markdown files
        if not file.endswith('.md'):
            continue
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line_num, line in enumerate(f, 1):
                    # Look for lines with "Deadline:" or "Due:"
                    if 'deadline' in line.lower() or ('due' in line.lower() and 'feb' in line.lower()):
                        # Extract any February/March dates
                        date_matches = re.findall(r'(February|March)\s+(\d{1,2}),?\s+(2026)?', line, re.IGNORECASE)
                        for match in date_matches:
                            month, day, year = match
                            deadlines_found.append({
                                'month': month,
                                'day': day,
                                'line': line.strip(),
                                'file': file
                            })
        except:
            pass
    
    return deadlines_found

def scan_folders():
    """Scan all folders"""
    print("🔍 Scanning all bid folders for deadlines...\n")
    
    if not os.path.exists(BIDS_PATH):
        print(f"❌ Path not found: {BIDS_PATH}")
        return
    
    all_bids = []
    
    for folder in sorted(os.listdir(BIDS_PATH)):
        folder_path = os.path.join(BIDS_PATH, folder)
        
        if folder.startswith('.') or not os.path.isdir(folder_path):
            continue
        
        # Skip reference folders
        if any(x in folder.upper() for x in ['MASTER FILES', 'REFERENCE', 'GUIDE', 'SCORECARD', 'LEGAL']):
            continue
        
        deadlines = find_deadline_in_folder(folder_path, folder)
        
        all_bids.append({
            'folder': folder,
            'deadlines': deadlines
        })
    
    # Generate markdown
    output_path = "ALL_BIDS_WITH_DEADLINES.md"
    
    with open(output_path, 'w') as f:
        f.write(f"# 📊 ALL BID FOLDERS - DEADLINE SCAN\n")
        f.write(f"**Generated:** {datetime.now().strftime('%A, %B %d, %Y at %I:%M %p')}\n")
        f.write(f"**Total Folders:** {len(all_bids)}\n\n")
        f.write("---\n\n")
        
        # Group by whether deadline found
        with_deadlines = [b for b in all_bids if b['deadlines']]
        without_deadlines = [b for b in all_bids if not b['deadlines']]
        
        f.write(f"## ✅ BIDS WITH DEADLINES FOUND ({len(with_deadlines)})\n\n")
        
        for bid in with_deadlines:
            f.write(f"### {bid['folder']}\n")
            
            # Get unique dates
            dates_found = set()
            for d in bid['deadlines']:
                dates_found.add(f"{d['month']} {d['day']}")
            
            if dates_found:
                f.write(f"- **Deadline(s) Found:** {', '.join(sorted(dates_found))}\n")
                
                # Show first line that mentioned deadline
                first = bid['deadlines'][0]
                f.write(f"- **From File:** {first['file']}\n")
                f.write(f"- **Line:** _{first['line'][:80]}_\n")
            
            f.write(f"- **Folder:** `BIDS:RESOURCES/{bid['folder']}/`\n\n")
        
        f.write("---\n\n")
        f.write(f"## ❓ BIDS WITHOUT CLEAR DEADLINES ({len(without_deadlines)})\n\n")
        f.write("These folders exist but no deadline found in markdown files:\n\n")
        
        for bid in without_deadlines[:20]:  # Limit to 20
            f.write(f"- {bid['folder']}\n")
        
        if len(without_deadlines) > 20:
            f.write(f"\n...and {len(without_deadlines) - 20} more\n")
    
    print(f"✅ Scan complete: {output_path}")
    print(f"\n📊 Results:")
    print(f"   - With deadlines: {len(with_deadlines)}")
    print(f"   - Without deadlines: {len(without_deadlines)}")
    print(f"\n🎯 Open ALL_BIDS_WITH_DEADLINES.md to review!")

if __name__ == "__main__":
    scan_folders()
