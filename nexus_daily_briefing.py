#!/usr/bin/env python3
"""
NEXUS DAILY BRIEFING GENERATOR
Creates a daily report of everything ready to send, everything waiting for response,
and everything that needs attention.

This is the VISIBILITY LAYER — Dee needs to know what NEXUS has prepared.

Output: DAILY_BRIEFING.md in workspace root (open this every morning)
"""

import os
import json
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

# Paths
WORKSPACE = "/Users/deedavis/NEXUS BACKEND"
BIDS_ROOT = os.path.join(WORKSPACE, "BIDS:RESOURCES")
OUTPUT_FILE = os.path.join(WORKSPACE, "DAILY_BRIEFING.md")


def scan_ready_to_send():
    """Find all SEND_TO_BUYER folders with emails ready to send."""
    ready = []
    
    for folder in os.listdir(BIDS_ROOT):
        folder_path = os.path.join(BIDS_ROOT, folder)
        if not os.path.isdir(folder_path):
            continue
            
        send_to_buyer = os.path.join(folder_path, "SEND_TO_BUYER")
        if not os.path.exists(send_to_buyer):
            continue
            
        # Check for email file
        email_file = os.path.join(send_to_buyer, "SEND_TO_BUYER_EMAIL_READY.md")
        if not os.path.exists(email_file):
            continue
            
        # Check if already sent (look for "SENT" in file)
        with open(email_file, 'r') as f:
            content = f.read()
            
        already_sent = "✅ SENT" in content or "STATUS:** ✅ SENT" in content
        
        # Get cap statement if exists
        cap_statements = [f for f in os.listdir(send_to_buyer) 
                         if f.endswith('.html') and 'Capability' in f]
        
        # Get modification time
        mtime = os.path.getmtime(email_file)
        days_old = (datetime.now() - datetime.fromtimestamp(mtime)).days
        
        ready.append({
            'folder': folder,
            'email_file': email_file,
            'cap_statements': cap_statements,
            'already_sent': already_sent,
            'days_old': days_old,
            'path': send_to_buyer
        })
    
    return ready


def scan_workflow_status():
    """Check WORKFLOW_CHECKLIST.md files for status."""
    statuses = {
        'ready_to_send': [],      # Step 5 not done
        'waiting_response': [],    # Sent, no response
        'needs_action': [],        # Stuck somewhere
        'complete': []             # Submitted or won
    }
    
    for folder in os.listdir(BIDS_ROOT):
        folder_path = os.path.join(BIDS_ROOT, folder)
        if not os.path.isdir(folder_path):
            continue
            
        workflow_file = os.path.join(folder_path, "WORKFLOW_CHECKLIST.md")
        if not os.path.exists(workflow_file):
            continue
            
        with open(workflow_file, 'r') as f:
            content = f.read()
        
        # Analyze workflow status
        if "NO BID" in content or "LOST" in content or "CANCELLED" in content:
            continue  # Skip closed bids
            
        if "WON" in content or "AWARDED" in content:
            statuses['complete'].append(folder)
            continue
            
        # Check if email was sent
        if "Record date sent: ___" in content or "SEND TO BUYER ⬜" in content:
            # Has SEND_TO_BUYER folder with content?
            send_to_buyer = os.path.join(folder_path, "SEND_TO_BUYER")
            if os.path.exists(send_to_buyer):
                files = os.listdir(send_to_buyer)
                if any('EMAIL_READY' in f for f in files):
                    statuses['ready_to_send'].append(folder)
                    continue
        
        # Check if sent but no response
        if "✅ SENT" in content or "email sent" in content.lower():
            if "response" not in content.lower() or "no response" in content.lower():
                statuses['waiting_response'].append(folder)
                continue
        
        # Everything else needs attention
        statuses['needs_action'].append(folder)
    
    return statuses


def scan_stale_bids():
    """Find bids with no recent activity."""
    stale = []
    now = datetime.now()
    
    for folder in os.listdir(BIDS_ROOT):
        folder_path = os.path.join(BIDS_ROOT, folder)
        if not os.path.isdir(folder_path):
            continue
            
        # Get most recent file modification
        latest_mtime = 0
        for root, dirs, files in os.walk(folder_path):
            for f in files:
                fpath = os.path.join(root, f)
                try:
                    mtime = os.path.getmtime(fpath)
                    if mtime > latest_mtime:
                        latest_mtime = mtime
                except:
                    pass
        
        if latest_mtime > 0:
            days_since = (now - datetime.fromtimestamp(latest_mtime)).days
            if days_since >= 7:
                stale.append({
                    'folder': folder,
                    'days_since': days_since
                })
    
    return sorted(stale, key=lambda x: x['days_since'], reverse=True)


def get_upcoming_deadlines():
    """Extract deadlines from workflow files."""
    deadlines = []
    
    for folder in os.listdir(BIDS_ROOT):
        folder_path = os.path.join(BIDS_ROOT, folder)
        workflow_file = os.path.join(folder_path, "WORKFLOW_CHECKLIST.md")
        
        if not os.path.exists(workflow_file):
            continue
            
        with open(workflow_file, 'r') as f:
            content = f.read()
        
        # Look for deadline patterns
        import re
        patterns = [
            r'\*\*(?:Due|Deadline|Closes|PROPOSALS DUE)\*\*[:\s]*(\w+\s+\d+,?\s*\d{4})',
            r'Due[:\s]+(\w+\s+\d+,?\s*\d{4})',
            r'(\d{2}/\d{2}/\d{4})',
            r'(\d{4}-\d{2}-\d{2})'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                try:
                    # Try to parse the date
                    for fmt in ['%B %d, %Y', '%B %d %Y', '%m/%d/%Y', '%Y-%m-%d']:
                        try:
                            deadline = datetime.strptime(match, fmt)
                            if deadline > datetime.now():
                                deadlines.append({
                                    'folder': folder,
                                    'deadline': deadline,
                                    'days_until': (deadline - datetime.now()).days
                                })
                            break
                        except:
                            continue
                except:
                    pass
    
    return sorted(deadlines, key=lambda x: x['deadline'])[:10]


def generate_briefing():
    """Generate the daily briefing markdown file."""
    
    ready = scan_ready_to_send()
    statuses = scan_workflow_status()
    stale = scan_stale_bids()
    deadlines = get_upcoming_deadlines()
    
    # Separate ready to send into sent vs not sent
    not_sent = [r for r in ready if not r['already_sent']]
    sent_waiting = [r for r in ready if r['already_sent']]
    
    # Generate markdown
    lines = []
    lines.append(f"# 📋 NEXUS DAILY BRIEFING")
    lines.append(f"**Generated:** {datetime.now().strftime('%A, %B %d, %Y at %I:%M %p')}")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # SECTION 1: READY TO SEND (NOT YET SENT)
    lines.append("## 🚀 READY TO SEND — ACTION REQUIRED")
    lines.append("")
    if not_sent:
        lines.append(f"**{len(not_sent)} emails ready to send:**")
        lines.append("")
        lines.append("| Opportunity | Cap Statement | Folder | Days Waiting |")
        lines.append("|---|---|---|---|")
        for item in sorted(not_sent, key=lambda x: x['days_old'], reverse=True):
            caps = ", ".join(item['cap_statements'][:1]) if item['cap_statements'] else "None"
            lines.append(f"| {item['folder']} | {caps} | [Open]({item['path']}) | {item['days_old']} days |")
        lines.append("")
        lines.append("**To send:** Open folder → Open HTML in Chrome → Cmd+P → Save as PDF → Copy email → Send")
        lines.append("")
    else:
        lines.append("✅ No emails waiting to be sent!")
        lines.append("")
    
    # SECTION 2: SENT, WAITING FOR RESPONSE
    lines.append("## ⏳ SENT — WAITING FOR RESPONSE")
    lines.append("")
    if statuses['waiting_response']:
        lines.append(f"**{len(statuses['waiting_response'])} outreach emails sent, no response yet:**")
        lines.append("")
        for folder in statuses['waiting_response'][:10]:
            lines.append(f"- {folder}")
        if len(statuses['waiting_response']) > 10:
            lines.append(f"- ... and {len(statuses['waiting_response']) - 10} more")
        lines.append("")
        lines.append("**Action:** Follow up on any sent 7+ days ago")
        lines.append("")
    else:
        lines.append("No outreach waiting for response.")
        lines.append("")
    
    # SECTION 3: UPCOMING DEADLINES
    lines.append("## 📅 UPCOMING DEADLINES")
    lines.append("")
    if deadlines:
        lines.append("| Opportunity | Deadline | Days Until |")
        lines.append("|---|---|---|")
        for d in deadlines:
            urgency = "🔴" if d['days_until'] <= 7 else "🟡" if d['days_until'] <= 14 else ""
            lines.append(f"| {urgency} {d['folder']} | {d['deadline'].strftime('%B %d, %Y')} | {d['days_until']} days |")
        lines.append("")
    else:
        lines.append("No upcoming deadlines found.")
        lines.append("")
    
    # SECTION 4: STALE BIDS
    lines.append("## ⚠️ STALE BIDS — NO ACTIVITY")
    lines.append("")
    stale_14_plus = [s for s in stale if s['days_since'] >= 14]
    if stale_14_plus:
        lines.append(f"**{len(stale_14_plus)} bids with no activity in 14+ days:**")
        lines.append("")
        for s in stale_14_plus[:15]:
            lines.append(f"- {s['folder']} ({s['days_since']} days)")
        if len(stale_14_plus) > 15:
            lines.append(f"- ... and {len(stale_14_plus) - 15} more")
        lines.append("")
        lines.append("**Action:** Review each — send outreach, close out, or delete")
        lines.append("")
    else:
        lines.append("✅ All bids have recent activity!")
        lines.append("")
    
    # SECTION 5: SUMMARY STATS
    lines.append("## 📊 PIPELINE SUMMARY")
    lines.append("")
    lines.append(f"| Status | Count |")
    lines.append(f"|---|---|")
    lines.append(f"| Ready to Send | {len(not_sent)} |")
    lines.append(f"| Sent, Waiting | {len(statuses['waiting_response'])} |")
    lines.append(f"| Needs Action | {len(statuses['needs_action'])} |")
    lines.append(f"| Stale (14+ days) | {len(stale_14_plus)} |")
    lines.append(f"| Upcoming Deadlines | {len(deadlines)} |")
    lines.append("")
    
    # SECTION 6: TODAY'S TOP 5 ACTIONS
    lines.append("## ✅ TODAY'S TOP 5 ACTIONS")
    lines.append("")
    actions = []
    
    # Urgent deadlines
    for d in deadlines[:2]:
        if d['days_until'] <= 14:
            actions.append(f"📅 **{d['folder']}** — Due in {d['days_until']} days, prepare bid")
    
    # Ready to send
    for item in not_sent[:3]:
        actions.append(f"📧 **{item['folder']}** — Email ready, SEND IT")
    
    # Fill with follow-ups if needed
    if len(actions) < 5:
        for folder in statuses['waiting_response'][:5-len(actions)]:
            actions.append(f"📞 **{folder}** — Sent, needs follow-up")
    
    for i, action in enumerate(actions[:5], 1):
        lines.append(f"{i}. {action}")
    
    if not actions:
        lines.append("No urgent actions today!")
    
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append(f"*Next briefing will regenerate automatically. Check `DAILY_BRIEFING.md` each morning.*")
    
    # Write file
    with open(OUTPUT_FILE, 'w') as f:
        f.write('\n'.join(lines))
    
    print(f"✅ Daily briefing generated: {OUTPUT_FILE}")
    print(f"   Ready to send: {len(not_sent)}")
    print(f"   Waiting response: {len(statuses['waiting_response'])}")
    print(f"   Upcoming deadlines: {len(deadlines)}")
    print(f"   Stale bids: {len(stale_14_plus)}")
    
    return {
        'ready_to_send': len(not_sent),
        'waiting_response': len(statuses['waiting_response']),
        'deadlines': len(deadlines),
        'stale': len(stale_14_plus)
    }


if __name__ == "__main__":
    generate_briefing()
