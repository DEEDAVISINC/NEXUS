#!/usr/bin/env python3
"""
NEXUS AGENDA MANAGER — Parses actual bid folders and email content.
Shows the real work: who to email, what to send, what's next.
"""

import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv

load_dotenv()

BIDS_ROOT = Path(os.environ.get('BIDS_ROOT', '/Users/deedavis/NEXUS BACKEND/BIDS:RESOURCES'))

SKIP_NAMES = {
    'COMPANY FORMS', 'REFERENCE GUIDES', 'MISCELLANEOUS', 'OUTREACH EMAILS',
    'PERSONAL LEGAL', 'RCOC MASTER FILES', 'SUBCONTRACTING PLAN CHALLENGES',
}


class AgendaManager:

    def __init__(self):
        self._api = None
        self._base_id = os.environ.get('AIRTABLE_BASE_ID', '')

    def _get_api(self):
        if self._api is None:
            from pyairtable import Api
            self._api = Api(os.environ.get('AIRTABLE_API_KEY', ''))
        return self._api

    def get_agenda(self, view: str = 'today') -> Dict:
        all_tasks = self._get_tasks(include_done=True)
        active_tasks = [t for t in all_tasks if t.get('status') != 'DONE']
        done_tasks = [t for t in all_tasks if t.get('status') == 'DONE']
        bids = self._scan_all_folders()

        critical = [t for t in active_tasks if t.get('priority') == 'CRITICAL']
        high = [t for t in active_tasks if t.get('priority') == 'HIGH']
        medium = [t for t in active_tasks if t.get('priority') == 'MEDIUM']
        low = [t for t in active_tasks if t.get('priority') == 'LOW']

        ready = [b for b in bids if b['stage'] == 'ready_to_send']
        supplier = [b for b in bids if b['stage'] == 'supplier_pending']

        return {
            'view': view,
            'date': datetime.now().strftime('%Y-%m-%d'),
            'sections': [
                {
                    'id': 'critical',
                    'title': 'Do Now',
                    'subtitle': 'Critical — handle immediately',
                    'color': 'red',
                    'items': critical,
                    'type': 'tasks',
                },
                {
                    'id': 'high',
                    'title': 'High Priority',
                    'subtitle': 'Lab accounts, follow-ups, key checks',
                    'color': 'orange',
                    'items': high,
                    'type': 'tasks',
                },
                {
                    'id': 'ready_to_send',
                    'title': 'Emails Ready to Send',
                    'subtitle': 'Review, attach cap statement, send to buyer',
                    'color': 'green',
                    'items': ready,
                    'type': 'bids',
                },
                {
                    'id': 'medium',
                    'title': 'This Week',
                    'subtitle': 'Registrations, certifications, pipeline',
                    'color': 'blue',
                    'items': medium,
                    'type': 'tasks',
                },
                {
                    'id': 'supplier_pending',
                    'title': 'Waiting on Suppliers',
                    'subtitle': 'RFQs sent — follow up for quotes',
                    'color': 'yellow',
                    'items': supplier,
                    'type': 'bids',
                },
                {
                    'id': 'low',
                    'title': 'When You Can',
                    'subtitle': 'Lower priority, long-term items',
                    'color': 'gray',
                    'items': low,
                    'type': 'tasks',
                },
                {
                    'id': 'done',
                    'title': 'Already Sent / Completed',
                    'subtitle': 'Emails confirmed sent, tasks completed',
                    'color': 'emerald',
                    'items': done_tasks,
                    'type': 'tasks',
                },
            ],
            'stats': {
                'total_tasks': len(active_tasks),
                'completed': len(done_tasks),
                'critical': len(critical),
                'high': len(high),
                'medium': len(medium),
                'low': len(low),
                'ready_to_send': len(ready),
                'supplier_pending': len(supplier),
            },
        }

    def _get_tasks(self, include_done=False) -> List[Dict]:
        items = []
        try:
            records = self._get_api().table(self._base_id, 'TASKS').all(max_records=200)
            for r in records:
                f = r['fields']
                status = f.get('STATUS', '')
                if status == 'DONE' and not include_done:
                    continue
                desc = f.get('DESCRIPTION', '')
                to_addr = ''
                for part in desc.split('|'):
                    part = part.strip()
                    if part.startswith('TO:'):
                        to_addr = part[3:].strip()
                        break
                items.append({
                    'id': r['id'],
                    'name': f.get('TITLE', 'Untitled'),
                    'stage': 'task',
                    'action': desc,
                    'priority': f.get('PRIORITY', 'MEDIUM'),
                    'status': status,
                    'dueDate': f.get('DUE DATE', ''),
                    'project': f.get('PROJECTS', ''),
                    'folder': '', 'to': to_addr, 'cc': '', 'subject': '',
                    'hasEmail': False, 'hasWorkflow': False,
                    'capStatements': [], 'buyerDocCount': 0,
                    'supplierDocCount': 0, 'checklist': [],
                    'lastModified': '', 'daysAgo': 0,
                    'recordId': r['id'], 'type': 'task',
                })
        except Exception as e:
            print(f"TASKS error: {e}")
        return items

    def mark_task_done(self, record_id: str) -> bool:
        try:
            record = self._get_api().table(self._base_id, 'TASKS').get(record_id)
            self._get_api().table(self._base_id, 'TASKS').update(record_id, {'STATUS': 'DONE'})

            try:
                from nexus_learning_engine import nxlearn
                fields = record.get('fields', {})
                title = fields.get('TITLE', '')
                project = fields.get('PROJECTS', '')
                domain = 'outreach' if 'email' in title.lower() or 'sent' in title.lower() else 'bids'
                action = 'email_sent' if domain == 'outreach' else 'bid_prepared'
                nxlearn(domain, record_id, action, {
                    'title': title,
                    'project': project,
                    'agency': fields.get('DESCRIPTION', '')[:80],
                })
            except Exception:
                pass

            return True
        except Exception as e:
            print(f"Mark done error: {e}")
            return False

    def get_bid_detail(self, bid_id: str) -> Optional[Dict]:
        """Get full detail for a single bid including email content."""
        folder_name = bid_id.replace('-', ' ').upper()
        folder = BIDS_ROOT / folder_name
        if not folder.exists():
            for d in BIDS_ROOT.iterdir():
                if d.is_dir() and d.name.replace(' ', '-').lower() == bid_id:
                    folder = d
                    break

        if not folder.exists():
            return None

        email_file = folder / 'SEND_TO_BUYER' / 'SEND_TO_BUYER_EMAIL_READY.md'
        email_data = self._parse_email_file(email_file) if email_file.exists() else {}

        buyer_docs = []
        send_buyer = folder / 'SEND_TO_BUYER'
        if send_buyer.exists():
            for f in send_buyer.iterdir():
                if f.is_file() and f.name != 'SEND_TO_BUYER_EMAIL_READY.md':
                    buyer_docs.append({
                        'name': f.name,
                        'type': f.suffix.lstrip('.'),
                        'path': str(f),
                    })

        return {
            'id': bid_id,
            'name': folder.name,
            'folder': str(folder),
            'email': email_data,
            'buyerDocs': buyer_docs,
        }

    def _scan_all_folders(self) -> List[Dict]:
        bids = []
        if not BIDS_ROOT.exists():
            return bids

        for folder in sorted(BIDS_ROOT.iterdir()):
            if not folder.is_dir() or folder.name in SKIP_NAMES:
                continue
            if folder.name.startswith('.') or folder.name.endswith('.md') or folder.name.endswith('.pdf'):
                continue

            send_buyer = folder / 'SEND_TO_BUYER'
            send_supplier = folder / 'SEND_TO_SUPPLIER'
            workflow = folder / 'WORKFLOW_CHECKLIST.md'
            email_file = send_buyer / 'SEND_TO_BUYER_EMAIL_READY.md'

            has_email = email_file.exists()
            has_workflow = workflow.exists()

            buyer_files = [f.name for f in send_buyer.iterdir() if f.is_file()] if send_buyer.exists() else []
            supplier_files = [f.name for f in send_supplier.iterdir() if f.is_file()] if send_supplier.exists() else []

            mod_time = self._folder_mod_time(folder)
            days_ago = (datetime.now() - mod_time).days if mod_time else 999

            email_data: Dict = {}
            if has_email:
                email_data = self._parse_email_file(email_file)

            cap_statements = [f for f in buyer_files if f.endswith('.html') or (f.endswith('.pdf') and 'capability' in f.lower())]

            bid_id = folder.name.replace(' ', '-').lower()

            if has_email:
                stage = 'ready_to_send'
                to_addr = email_data.get('to', '')
                subject = email_data.get('subject', '')
                action = f"Send to {to_addr}" if to_addr else 'Review and send email'
            elif supplier_files and not buyer_files:
                stage = 'supplier_pending'
                action = f"{len(supplier_files)} supplier RFQ{'s' if len(supplier_files) != 1 else ''} sent — follow up"
            elif has_workflow or (send_buyer.exists() and not has_email):
                stage = 'in_progress'
                action = 'Continue workflow' if has_workflow else 'Create buyer email and documents'
            elif send_buyer.exists() or send_supplier.exists():
                stage = 'needs_work'
                action = 'Missing documents — needs attention'
            else:
                continue

            bids.append({
                'id': bid_id,
                'name': folder.name,
                'stage': stage,
                'action': action,
                'folder': str(folder),
                'lastModified': mod_time.strftime('%Y-%m-%d') if mod_time else '',
                'daysAgo': days_ago,
                'to': email_data.get('to', ''),
                'cc': email_data.get('cc', ''),
                'subject': email_data.get('subject', ''),
                'hasEmail': has_email,
                'hasWorkflow': has_workflow,
                'capStatements': cap_statements,
                'buyerDocCount': len(buyer_files),
                'supplierDocCount': len(supplier_files),
                'checklist': email_data.get('checklist', []),
            })

        bids.sort(key=lambda b: b.get('daysAgo', 999))
        return bids

    def _parse_email_file(self, path: Path) -> Dict:
        """Extract TO, CC, SUBJECT, body, and checklist from email file."""
        try:
            text = path.read_text(encoding='utf-8')
        except Exception:
            return {}

        result: Dict = {'raw': text}
        lines = text.split('\n')

        for line in lines:
            low = line.lower().strip()
            stripped = line.strip()

            if low.startswith('to:') or low.startswith('**to:**'):
                result['to'] = self._extract_value(stripped)
            elif low.startswith('cc:') or low.startswith('**cc:**'):
                result['cc'] = self._extract_value(stripped)
            elif low.startswith('subject:') or low.startswith('**subject:**'):
                result['subject'] = self._extract_value(stripped)

        body = self._extract_email_body(text)
        if body:
            result['body'] = body

        checklist = []
        in_checklist = False
        for line in lines:
            if '## ACTION CHECKLIST' in line or '## BEFORE SENDING' in line or '## ACTION' in line:
                in_checklist = True
                continue
            if in_checklist:
                if line.startswith('## ') or line.startswith('---'):
                    in_checklist = False
                    continue
                m = re.match(r'\s*-\s*\[[ x]\]\s*(.*)', line)
                if m:
                    checklist.append(m.group(1).strip())
        result['checklist'] = checklist

        return result

    def _extract_email_body(self, text: str) -> str:
        """Pull the copy-ready email body from the file."""
        markers = [
            '## COPY-READY EMAIL', '## EMAIL BODY', '## COPY BELOW',
            '## EMAIL BODY (COPY BELOW)',
        ]
        for marker in markers:
            if marker in text:
                section = text.split(marker, 1)[1]
                parts = section.split('## ', 1)
                body = parts[0].strip()
                body = re.sub(r'^---\s*$', '', body, flags=re.MULTILINE).strip()
                body = re.sub(r'^\*\*To:\*\*.*$', '', body, flags=re.MULTILINE)
                body = re.sub(r'^\*\*CC:\*\*.*$', '', body, flags=re.MULTILINE)
                body = re.sub(r'^\*\*Subject:\*\*.*$', '', body, flags=re.MULTILINE)
                body = body.strip().strip('`').strip()
                return body

        if '```' in text:
            m = re.search(r'```\n?(.*?)```', text, re.DOTALL)
            if m:
                return m.group(1).strip()

        lines = text.split('\n')
        for i, line in enumerate(lines):
            if line.strip() == '---' and i > 2:
                rest = '\n'.join(lines[i+1:]).strip()
                if rest and not rest.startswith('#'):
                    end = rest.find('\n---')
                    if end > 0:
                        return rest[:end].strip()
                    return rest

        return ''

    def _extract_value(self, line: str) -> str:
        """Extract value after TO:/SUBJECT:/etc headers."""
        line = re.sub(r'^\*\*\w+[:\*]*\*?\*?\s*', '', line)
        line = re.sub(r'^(TO|CC|Subject|SUBJECT|to|cc):\s*', '', line, flags=re.IGNORECASE)
        line = line.strip().rstrip('|').strip()
        parts = [p.strip() for p in re.split(r'[/,]', line) if '@' in p or not line.startswith('(')]
        return parts[0] if parts else line

    def _folder_mod_time(self, folder: Path) -> Optional[datetime]:
        latest = None
        try:
            for item in folder.rglob('*'):
                if item.is_file():
                    mtime = datetime.fromtimestamp(item.stat().st_mtime)
                    if latest is None or mtime > latest:
                        latest = mtime
        except Exception:
            pass
        return latest


def handle_get_agenda(view: str = 'today') -> Dict:
    return AgendaManager().get_agenda(view)


def handle_get_bid_detail(bid_id: str) -> Optional[Dict]:
    return AgendaManager().get_bid_detail(bid_id)


if __name__ == '__main__':
    manager = AgendaManager()
    agenda = manager.get_agenda()

    print(f"NEXUS Workbench — {agenda['date']}\n")
    stats = agenda['stats']
    print(f"  {stats['total_bids']} bids | {stats['ready_to_send']} ready | {stats['supplier_pending']} suppliers | {stats['in_progress']} progress | {stats['needs_work']} needs work\n")

    for section in agenda['sections']:
        if not section['items']:
            continue
        print(f"{'='*70}")
        print(f"  {section['title']} ({len(section['items'])})")
        print(f"{'='*70}")
        for item in section['items'][:8]:
            print(f"  {item['name']}")
            if item.get('to'):
                print(f"    TO: {item['to']}")
            if item.get('subject'):
                print(f"    SUBJ: {item['subject'][:65]}")
            if item.get('checklist'):
                print(f"    Steps: {len(item['checklist'])} items")
            if not item.get('to'):
                print(f"    {item['action']}")
            print()
