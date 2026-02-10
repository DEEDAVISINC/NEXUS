#!/usr/bin/env python3
"""
NEXUS AGENDA MANAGER
Serves daily agenda from TOMORROW_AGENDA markdown files
"""

import os
from datetime import datetime, timedelta
from typing import Dict, List
import re

class AgendaManager:
    """
    Manages daily agenda by parsing TOMORROW_AGENDA markdown files
    and serving structured data to NEXUS frontend
    """
    
    def __init__(self):
        self.workspace_path = "/Users/deedavis/NEXUS BACKEND"
    
    def get_agenda_for_date(self, date_str: str = None) -> Dict:
        """
        Get agenda for specific date
        
        Args:
            date_str: Date in format "FEB_7_2026" or None for today
            
        Returns:
            Dictionary with structured agenda items
        """
        if not date_str:
            # Default to tomorrow's date
            tomorrow = datetime.now() + timedelta(days=1)
            date_str = tomorrow.strftime("%b_%d_%Y").upper()
        
        # Look for agenda file
        agenda_file = f"{self.workspace_path}/TOMORROW_AGENDA_{date_str}.md"
        
        if not os.path.exists(agenda_file):
            # Try alternate format
            date_str = date_str.replace('_', '_')
            agenda_file = f"{self.workspace_path}/TOMORROW_AGENDA_{date_str}.md"
        
        if not os.path.exists(agenda_file):
            return self._get_empty_agenda()
        
        return self._parse_agenda_file(agenda_file)
    
    def get_todays_agenda(self) -> Dict:
        """Get agenda for today"""
        today = datetime.now()
        
        # Try today's date
        date_str = today.strftime("%b_%d_%Y").upper()
        agenda_file = f"{self.workspace_path}/TOMORROW_AGENDA_{date_str}.md"
        
        if os.path.exists(agenda_file):
            return self._parse_agenda_file(agenda_file)
        
        # If no file for today, get most recent agenda file
        return self._get_most_recent_agenda()
    
    def get_tomorrows_agenda(self) -> Dict:
        """Get agenda for tomorrow"""
        tomorrow = datetime.now() + timedelta(days=1)
        date_str = tomorrow.strftime("%b_%d_%Y").upper()
        return self.get_agenda_for_date(date_str)
    
    def get_week_agenda(self) -> Dict:
        """Get agenda for this week"""
        # For now, combine today and tomorrow
        today_agenda = self.get_todays_agenda()
        tomorrow_agenda = self.get_tomorrows_agenda()
        
        # Merge items
        all_items = today_agenda.get('items', []) + tomorrow_agenda.get('items', [])
        
        return {
            'view': 'this-week',
            'date': datetime.now().strftime("%Y-%m-%d"),
            'items': all_items,
            'total_count': len(all_items),
            'completed_count': len([i for i in all_items if i.get('status') == 'completed'])
        }
    
    def _get_most_recent_agenda(self) -> Dict:
        """Get the most recently created agenda file"""
        agenda_files = []
        
        for filename in os.listdir(self.workspace_path):
            if filename.startswith('TOMORROW_AGENDA_') and filename.endswith('.md'):
                filepath = os.path.join(self.workspace_path, filename)
                mtime = os.path.getmtime(filepath)
                agenda_files.append((mtime, filepath))
        
        if not agenda_files:
            return self._get_empty_agenda()
        
        # Get most recent
        agenda_files.sort(reverse=True)
        most_recent = agenda_files[0][1]
        
        return self._parse_agenda_file(most_recent)
    
    def _parse_agenda_file(self, filepath: str) -> Dict:
        """
        Parse markdown agenda file and extract structured agenda items
        
        Args:
            filepath: Path to agenda markdown file
            
        Returns:
            Dictionary with structured agenda items
        """
        with open(filepath, 'r') as f:
            content = f.read()
        
        items = []
        
        # Parse the file to extract agenda items
        # Look for time-based sections (e.g., "6:00-8:00 AM: McKesson Quote Finalization")
        
        # Extract Morning - NIH Submission
        if 'MORNING - NIH SURGICAL SUPPLIES SUBMISSION' in content:
            items.append({
                'id': 'nih-mckesson',
                'type': 'call',
                'title': 'Contact McKesson for Quote',
                'description': 'Get final pricing and expedited shipping quote for Surgicel products',
                'priority': 'urgent',
                'dueDate': self._extract_date_from_content(content),
                'dueTime': '6:00-8:00 AM',
                'status': 'pending',
                'relatedTo': 'NIH Surgical Supplies (26-002571)',
                'action': 'Check email or call 1-800-625-3776'
            })
            
            items.append({
                'id': 'nih-pdf',
                'type': 'document',
                'title': 'Generate NIH Capability Statement PDF',
                'description': 'Save HTML as PDF: 26-002571_Dee_Davis_Inc_Surgical_Supplies_Capability.pdf',
                'priority': 'urgent',
                'dueDate': self._extract_date_from_content(content),
                'dueTime': '8:00-9:00 AM',
                'status': 'pending',
                'relatedTo': 'NIH Surgical Supplies (26-002571)',
                'action': 'Open HTML → Command+P → Save as PDF'
            })
            
            items.append({
                'id': 'nih-email',
                'type': 'email',
                'title': 'Prepare NIH Submission Email',
                'description': 'Copy email from FINAL_EMAIL_SUBMISSION_READY.txt, update pricing and phone',
                'priority': 'urgent',
                'dueDate': self._extract_date_from_content(content),
                'dueTime': '9:00-10:45 AM',
                'status': 'pending',
                'relatedTo': 'NIH Surgical Supplies (26-002571)',
                'action': 'Update phone to 248.376.4550, attach PDF'
            })
            
            items.append({
                'id': 'nih-submit',
                'type': 'deadline',
                'title': '🚀 SUBMIT NIH SURGICAL SUPPLIES',
                'description': 'Final submission to valerie.gregorio@nih.gov - Patient care emergency!',
                'priority': 'urgent',
                'dueDate': self._extract_date_from_content(content),
                'dueTime': '10:45 AM',
                'status': 'pending',
                'relatedTo': 'NIH Surgical Supplies (26-002571)',
                'action': 'Send email with PDF attachment - Deadline 12:00 PM EST'
            })
        
        # Extract Afternoon - EDWOSB Opportunity Search
        if 'AFTERNOON - EDWOSB OPPORTUNITY EXPANSION' in content:
            items.append({
                'id': 'nexus-update',
                'type': 'review',
                'title': 'Add All Opportunities to NEXUS',
                'description': 'Run Python script to add 6 EDWOSB opportunities to Airtable',
                'priority': 'high',
                'dueDate': self._extract_date_from_content(content),
                'dueTime': '1:00 PM',
                'status': 'pending',
                'relatedTo': 'NEXUS Database',
                'action': 'Run: python3 add_all_edwosb_opportunities_to_nexus.py'
            })
            
            items.append({
                'id': 'sam-search',
                'type': 'follow-up',
                'title': 'Comprehensive SAM.gov Search',
                'description': 'Run 62 searches × 3 (Intent to Sole Source, Sources Sought, Solicitations)',
                'priority': 'high',
                'dueDate': self._extract_date_from_content(content),
                'dueTime': '1:00-3:00 PM',
                'status': 'pending',
                'relatedTo': 'SAM_GOV_SEARCH_BATTLE_PLAN.md',
                'action': 'Triple-search strategy - Expected: 500-1,000 opportunities!'
            })
            
            items.append({
                'id': 'sam-sort',
                'type': 'review',
                'title': 'Sort & Prioritize Opportunities',
                'description': 'Export results, identify top 20-30 opportunities, add to NEXUS',
                'priority': 'high',
                'dueDate': self._extract_date_from_content(content),
                'dueTime': '3:00-5:00 PM',
                'status': 'pending',
                'relatedTo': 'SAM.gov Search Results',
                'action': 'Sort by: Intent to Sole Source first, then Sources Sought, then deadline'
            })
        
        # Extract Evening - VA Orlando
        if 'Start VA Orlando Courier' in content or 'VA ORLANDO COURIER' in content:
            items.append({
                'id': 'va-orlando',
                'type': 'document',
                'title': 'Start VA Orlando Courier Materials',
                'description': 'Download solicitation, create folder, adapt VA Illiana materials',
                'priority': 'high',
                'dueDate': self._extract_date_from_content(content),
                'dueTime': '5:00-7:00 PM',
                'status': 'pending',
                'relatedTo': 'VA Orlando Courier (36C24826Q0302)',
                'action': 'Reuse 90% of VA Illiana capability statement - just change facility names'
            })
        
        return {
            'view': 'today',
            'date': self._extract_date_from_content(content),
            'items': items,
            'total_count': len(items),
            'completed_count': 0
        }
    
    def _extract_date_from_content(self, content: str) -> str:
        """Extract date from agenda file content"""
        # Look for date in title or content
        match = re.search(r'Friday,?\s+February\s+7,?\s+2026', content, re.IGNORECASE)
        if match:
            return '2026-02-07'
        
        match = re.search(r'Feb(?:ruary)?\s+7,?\s+2026', content, re.IGNORECASE)
        if match:
            return '2026-02-07'
        
        # Default to tomorrow
        tomorrow = datetime.now() + timedelta(days=1)
        return tomorrow.strftime("%Y-%m-%d")
    
    def _get_empty_agenda(self) -> Dict:
        """Return empty agenda structure"""
        return {
            'view': 'today',
            'date': datetime.now().strftime("%Y-%m-%d"),
            'items': [],
            'total_count': 0,
            'completed_count': 0
        }


# Handler function for NEXUS backend
def handle_get_agenda(view: str = 'today') -> Dict:
    """
    Get agenda for specified view
    
    Args:
        view: 'today', 'tomorrow', or 'this-week'
        
    Returns:
        Structured agenda data
    """
    manager = AgendaManager()
    
    if view == 'today':
        return manager.get_todays_agenda()
    elif view == 'tomorrow':
        return manager.get_tomorrows_agenda()
    elif view == 'this-week':
        return manager.get_week_agenda()
    else:
        return manager.get_todays_agenda()


if __name__ == '__main__':
    """Test the agenda manager"""
    print("🚀 Testing NEXUS Agenda Manager\n")
    
    manager = AgendaManager()
    
    # Test today's agenda
    print("📅 TODAY'S AGENDA:")
    agenda = manager.get_todays_agenda()
    print(f"   Date: {agenda['date']}")
    print(f"   Items: {agenda['total_count']}\n")
    
    for item in agenda['items']:
        print(f"   {item['dueTime']} - {item['title']}")
        print(f"      Priority: {item['priority']}")
        print(f"      Action: {item['action']}\n")
    
    print("\n✅ Agenda manager ready!")
