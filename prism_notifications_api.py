#!/usr/bin/env python3
"""
PRISM Notification & Receipt Tracking API
==========================================
Handles:
1. Real-time notification feed for admin + agents
2. Receipt upload with automatic tracking number extraction
3. Shipping status tracking per order
"""

import os
import re
import json
from datetime import datetime
from flask import Blueprint, request, jsonify

prism_notifications = Blueprint('prism_notifications', __name__)

NOTIFICATIONS_DIR = os.path.join(os.path.dirname(__file__), 'uploads', 'notifications')
RECEIPTS_DIR = os.path.join(os.path.dirname(__file__), 'uploads', 'receipts')
os.makedirs(NOTIFICATIONS_DIR, exist_ok=True)
os.makedirs(RECEIPTS_DIR, exist_ok=True)

NOTIFICATIONS_FILE = os.path.join(NOTIFICATIONS_DIR, 'notifications.json')
TRACKING_FILE = os.path.join(NOTIFICATIONS_DIR, 'tracking.json')


def _load_json(filepath, default=None):
    if default is None:
        default = []
    try:
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                return json.load(f)
    except (json.JSONDecodeError, IOError):
        pass
    return default


def _save_json(filepath, data):
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2, default=str)


# ═══════════════════════════════════════════════════════════════════
# 1. NOTIFICATION ENGINE
# ═══════════════════════════════════════════════════════════════════

NOTIFICATION_TYPES = {
    'scanback_uploaded': {
        'icon': '📸',
        'title': 'Scanback Uploaded',
        'severity': 'info',
        'target': 'admin',
    },
    'compliance_uploaded': {
        'icon': '📄',
        'title': 'Compliance Document Uploaded',
        'severity': 'info',
        'target': 'admin',
    },
    'receipt_uploaded': {
        'icon': '🧾',
        'title': 'Shipping Receipt Uploaded',
        'severity': 'info',
        'target': 'admin',
    },
    'tracking_extracted': {
        'icon': '📦',
        'title': 'Tracking Number Detected',
        'severity': 'success',
        'target': 'admin',
    },
    'qc_clean': {
        'icon': '✅',
        'title': 'QC Passed — Clean',
        'severity': 'success',
        'target': 'agent',
    },
    'qc_errors': {
        'icon': '🚨',
        'title': 'QC Failed — Corrections Needed',
        'severity': 'error',
        'target': 'agent',
    },
    'order_assigned': {
        'icon': '🚀',
        'title': 'New Order Assigned',
        'severity': 'info',
        'target': 'agent',
    },
    'correction_requested': {
        'icon': '⚠️',
        'title': 'Correction Requested',
        'severity': 'warning',
        'target': 'agent',
    },
    'payment_processed': {
        'icon': '💰',
        'title': 'Payment Processed',
        'severity': 'success',
        'target': 'agent',
    },
    'compliance_expiring': {
        'icon': '⏰',
        'title': 'Document Expiring Soon',
        'severity': 'warning',
        'target': 'agent',
    },
}


def create_notification(notif_type: str, message: str, order_id: str = '',
                        agent_id: str = '', agent_name: str = '',
                        metadata: dict = None) -> dict:
    """Create and persist a notification. Called by other PRISM modules."""
    type_info = NOTIFICATION_TYPES.get(notif_type, {
        'icon': '🔔', 'title': notif_type, 'severity': 'info', 'target': 'admin'
    })

    notification = {
        'id': f"NOTIF-{datetime.now().strftime('%Y%m%d%H%M%S')}-{len(_load_json(NOTIFICATIONS_FILE)) + 1}",
        'type': notif_type,
        'icon': type_info['icon'],
        'title': type_info['title'],
        'message': message,
        'severity': type_info['severity'],
        'target': type_info['target'],
        'order_id': order_id,
        'agent_id': agent_id,
        'agent_name': agent_name,
        'metadata': metadata or {},
        'read': False,
        'created_at': datetime.now().isoformat(),
    }

    notifications = _load_json(NOTIFICATIONS_FILE)
    notifications.insert(0, notification)

    if len(notifications) > 500:
        notifications = notifications[:500]

    _save_json(NOTIFICATIONS_FILE, notifications)
    return notification


@prism_notifications.route('/prism/notifications', methods=['GET'])
def get_notifications():
    """
    Get notifications feed.
    Query params:
    - target: 'admin' or 'agent' (default: all)
    - agent_id: filter by agent (for agent portal)
    - unread_only: 'true' to show unread only
    - limit: max results (default 50)
    """
    target = request.args.get('target', '')
    agent_id = request.args.get('agent_id', '')
    unread_only = request.args.get('unread_only', '').lower() == 'true'
    limit = int(request.args.get('limit', 50))

    notifications = _load_json(NOTIFICATIONS_FILE)

    if target:
        notifications = [n for n in notifications if n.get('target') == target]
    if agent_id:
        notifications = [n for n in notifications
                         if n.get('agent_id') == agent_id or n.get('target') == 'agent']
    if unread_only:
        notifications = [n for n in notifications if not n.get('read')]

    total_unread = sum(1 for n in _load_json(NOTIFICATIONS_FILE)
                       if not n.get('read') and (not target or n.get('target') == target))

    return jsonify({
        'success': True,
        'notifications': notifications[:limit],
        'total': len(notifications),
        'unread': total_unread,
    })


@prism_notifications.route('/prism/notifications/read', methods=['POST'])
def mark_notifications_read():
    """
    Mark notifications as read.
    JSON body: { notification_ids: ['NOTIF-...', ...'] } or { mark_all: true }
    """
    data = request.json or {}
    mark_all = data.get('mark_all', False)
    notification_ids = data.get('notification_ids', [])

    notifications = _load_json(NOTIFICATIONS_FILE)
    marked = 0

    for n in notifications:
        if mark_all or n['id'] in notification_ids:
            if not n.get('read'):
                n['read'] = True
                n['read_at'] = datetime.now().isoformat()
                marked += 1

    _save_json(NOTIFICATIONS_FILE, notifications)

    return jsonify({
        'success': True,
        'marked_read': marked,
    })


# ═══════════════════════════════════════════════════════════════════
# 2. RECEIPT UPLOAD & TRACKING NUMBER EXTRACTION
# ═══════════════════════════════════════════════════════════════════

TRACKING_PATTERNS = [
    {
        'carrier': 'UPS',
        'patterns': [
            r'\b(1Z[0-9A-Z]{16})\b',
            r'\b(T\d{10})\b',
            r'\b(\d{26})\b',  # UPS Mail Innovations
        ],
        'prefix_hints': ['ups', 'united parcel'],
    },
    {
        'carrier': 'USPS',
        'patterns': [
            r'\b(9[2-5]\d{18,22})\b',
            r'\b(94\d{18,22})\b',  # Certified Mail
            r'\b(70\d{18,22})\b',  # Priority Mail
            r'\b(EC\d{9}US)\b',    # Express Mail International
        ],
        'prefix_hints': ['usps', 'united states postal', 'post office'],
    },
    {
        'carrier': 'FedEx',
        'patterns': [
            r'\b(96\d{20})\b',  # FedEx Ground / SmartPost
            r'\b(61\d{18})\b',  # FedEx Express
            r'\b(\d{12,15})\b',
            r'\b(\d{20,22})\b',
        ],
        'prefix_hints': ['fedex', 'fed ex', 'fdx'],
    },
]


def extract_tracking_number(text: str) -> dict:
    """
    Extract tracking number and carrier from receipt text.
    Returns { carrier, tracking_number, confidence } or None.
    """
    if not text:
        return None

    text_lower = text.lower()

    for carrier_info in TRACKING_PATTERNS:
        carrier = carrier_info['carrier']
        has_hint = any(hint in text_lower for hint in carrier_info['prefix_hints'])

        for pattern in carrier_info['patterns']:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                tracking = matches[0]
                confidence = 'high' if has_hint else 'medium'
                return {
                    'carrier': carrier,
                    'tracking_number': tracking,
                    'confidence': confidence,
                }

    return None


def extract_text_from_file(filepath: str) -> str:
    """Extract readable text from a file (PDF or image)."""
    ext = os.path.splitext(filepath)[1].lower()
    text = ''

    if ext == '.pdf':
        try:
            import subprocess
            result = subprocess.run(
                ['python3', '-c', f'''
import sys
try:
    from PyPDF2 import PdfReader
    reader = PdfReader("{filepath}")
    for page in reader.pages:
        t = page.extract_text()
        if t:
            print(t)
except Exception as e:
    print(str(e), file=sys.stderr)
'''],
                capture_output=True, text=True, timeout=15
            )
            text = result.stdout
        except Exception:
            pass

    if ext in ('.jpg', '.jpeg', '.png'):
        try:
            import subprocess
            result = subprocess.run(
                ['python3', '-c', f'''
try:
    import pytesseract
    from PIL import Image
    img = Image.open("{filepath}")
    print(pytesseract.image_to_string(img))
except ImportError:
    pass
except Exception:
    pass
'''],
                capture_output=True, text=True, timeout=15
            )
            text = result.stdout
        except Exception:
            pass

    return text


@prism_notifications.route('/prism/receipt/upload', methods=['POST'])
def upload_receipt():
    """
    Upload a shipping receipt (FedEx, UPS, USPS) for a PRISM order.
    Auto-extracts tracking number from the file or from manual entry.

    Multipart form data:
    - file: Receipt image or PDF
    - order_id: PRISM order number
    - carrier: (optional) 'FedEx', 'UPS', 'USPS'
    - tracking_number: (optional) Manual tracking number entry
    - agent_id: (optional) Who uploaded
    - agent_name: (optional) Agent name
    """
    order_id = request.form.get('order_id', '')
    if not order_id:
        return jsonify({'error': 'order_id required'}), 400

    carrier = request.form.get('carrier', '')
    manual_tracking = request.form.get('tracking_number', '')
    agent_id = request.form.get('agent_id', '')
    agent_name = request.form.get('agent_name', '')

    receipt_path = None
    extracted = None

    if 'file' in request.files:
        file = request.files['file']
        if file.filename:
            ext = os.path.splitext(file.filename)[1].lower()
            if ext not in {'.pdf', '.jpg', '.jpeg', '.png'}:
                return jsonify({'error': f'File type {ext} not supported. Use PDF, JPEG, or PNG.'}), 400

            order_receipt_dir = os.path.join(RECEIPTS_DIR, order_id)
            os.makedirs(order_receipt_dir, exist_ok=True)

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            safe_name = f"receipt_{timestamp}{ext}"
            receipt_path = os.path.join(order_receipt_dir, safe_name)
            file.save(receipt_path)

            file_text = extract_text_from_file(receipt_path)
            if file_text:
                extracted = extract_tracking_number(file_text)

    tracking_number = manual_tracking
    detected_carrier = carrier

    if not tracking_number and extracted:
        tracking_number = extracted['tracking_number']
        detected_carrier = extracted['carrier']

    if tracking_number and not detected_carrier:
        probe = extract_tracking_number(tracking_number)
        if probe:
            detected_carrier = probe['carrier']

    tracking_record = {
        'order_id': order_id,
        'tracking_number': tracking_number,
        'carrier': detected_carrier,
        'receipt_file': receipt_path,
        'extraction_method': 'manual' if manual_tracking else ('auto' if extracted else 'none'),
        'confidence': extracted.get('confidence', 'manual') if extracted else ('manual' if manual_tracking else 'none'),
        'uploaded_by': agent_name or agent_id or 'Unknown',
        'uploaded_at': datetime.now().isoformat(),
        'status': 'shipped',
    }

    all_tracking = _load_json(TRACKING_FILE)
    existing_idx = next((i for i, t in enumerate(all_tracking)
                         if t['order_id'] == order_id), None)
    if existing_idx is not None:
        all_tracking[existing_idx] = tracking_record
    else:
        all_tracking.append(tracking_record)
    _save_json(TRACKING_FILE, all_tracking)

    if receipt_path or tracking_number:
        create_notification(
            'receipt_uploaded',
            f"Shipping receipt uploaded for {order_id}" +
            (f" by {agent_name}" if agent_name else ""),
            order_id=order_id,
            agent_id=agent_id,
            agent_name=agent_name,
            metadata={'carrier': detected_carrier, 'has_tracking': bool(tracking_number)},
        )

    if tracking_number:
        create_notification(
            'tracking_extracted',
            f"Tracking #{tracking_number} ({detected_carrier}) detected for {order_id}",
            order_id=order_id,
            agent_id=agent_id,
            agent_name=agent_name,
            metadata={'carrier': detected_carrier, 'tracking_number': tracking_number},
        )

    return jsonify({
        'success': True,
        'order_id': order_id,
        'tracking_number': tracking_number or None,
        'carrier': detected_carrier or None,
        'extraction_method': tracking_record['extraction_method'],
        'confidence': tracking_record['confidence'],
        'receipt_saved': receipt_path is not None,
        'message': (
            f"Tracking #{tracking_number} ({detected_carrier}) captured for {order_id}."
            if tracking_number
            else f"Receipt saved for {order_id}. No tracking number detected — enter manually or upload a clearer image."
        ),
    })


@prism_notifications.route('/prism/tracking/<order_id>', methods=['GET'])
def get_tracking(order_id):
    """Get tracking info for a PRISM order."""
    all_tracking = _load_json(TRACKING_FILE)
    record = next((t for t in all_tracking if t['order_id'] == order_id), None)

    if not record:
        return jsonify({'success': True, 'tracking': None, 'message': 'No tracking info for this order.'})

    return jsonify({
        'success': True,
        'tracking': record,
    })


@prism_notifications.route('/prism/tracking', methods=['GET'])
def get_all_tracking():
    """Get all tracking records. Optionally filter by status."""
    status = request.args.get('status', '')
    all_tracking = _load_json(TRACKING_FILE)

    if status:
        all_tracking = [t for t in all_tracking if t.get('status') == status]

    return jsonify({
        'success': True,
        'tracking': all_tracking,
        'total': len(all_tracking),
    })


@prism_notifications.route('/prism/tracking/<order_id>', methods=['PUT'])
def update_tracking(order_id):
    """
    Manually update or add tracking for an order.
    JSON body: { tracking_number, carrier }
    """
    data = request.json or {}
    tracking_number = data.get('tracking_number', '')
    carrier = data.get('carrier', '')

    if not tracking_number:
        return jsonify({'error': 'tracking_number required'}), 400

    if not carrier:
        probe = extract_tracking_number(tracking_number)
        carrier = probe['carrier'] if probe else 'Unknown'

    all_tracking = _load_json(TRACKING_FILE)
    existing_idx = next((i for i, t in enumerate(all_tracking)
                         if t['order_id'] == order_id), None)

    record = {
        'order_id': order_id,
        'tracking_number': tracking_number,
        'carrier': carrier,
        'receipt_file': None,
        'extraction_method': 'manual',
        'confidence': 'manual',
        'uploaded_by': 'Admin',
        'uploaded_at': datetime.now().isoformat(),
        'status': 'shipped',
    }

    if existing_idx is not None:
        record['receipt_file'] = all_tracking[existing_idx].get('receipt_file')
        all_tracking[existing_idx] = record
    else:
        all_tracking.append(record)

    _save_json(TRACKING_FILE, all_tracking)

    create_notification(
        'tracking_extracted',
        f"Tracking #{tracking_number} ({carrier}) manually entered for {order_id}",
        order_id=order_id,
    )

    return jsonify({
        'success': True,
        'tracking': record,
        'message': f"Tracking updated for {order_id}: {tracking_number} ({carrier})",
    })
