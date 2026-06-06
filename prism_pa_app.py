#!/usr/bin/env python3
"""
Minimal NEXUS PRISM API — PythonAnywhere / slim deploy.

Loads only PRISM order intake + ops queue routes. Avoids importing the full
api_server stack (GPSS, JETA, bid scanners, etc.) which can fail on PA free tier.
"""

import os

from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_cors import CORS

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

app = Flask(__name__)
CORS(app)


def _mask_phone(raw: str) -> str:
    """Last 4 digits only — safe for health endpoint."""
    digits = ''.join(c for c in (raw or '') if c.isdigit())
    if len(digits) < 4:
        return ''
    return f"***-***-{digits[-4:]}"


def _notification_config():
    """Non-secret channel readiness for ops / deploy verification."""
    twilio_sid = bool(os.environ.get('TWILIO_ACCOUNT_SID'))
    twilio_token = bool(os.environ.get('TWILIO_AUTH_TOKEN'))
    twilio_from = (os.environ.get('TWILIO_FROM_NUMBER') or '').strip()
    twilio_ok = twilio_sid and twilio_token and bool(twilio_from)

    sendgrid_ok = bool(
        os.environ.get('SENDGRID_API_KEY') and os.environ.get('SENDGRID_FROM_EMAIL')
    )

    smtp_ok = bool(os.environ.get('NEXUS_EMAIL_PASSWORD') and os.environ.get('NEXUS_EMAIL'))

    confirm_url = (os.environ.get('NEXUS_CONFIRM_BASE_URL') or '').strip()

    return {
        'twilio_configured': twilio_ok,
        'twilio_from_masked': _mask_phone(twilio_from) if twilio_from else None,
        'sendgrid_configured': sendgrid_ok,
        'smtp_configured': smtp_ok,
        'confirm_links_configured': bool(confirm_url),
        'channels_ready': {
            'rider_sms': twilio_ok,
            'confirmation_email_sendgrid': sendgrid_ok,
            'ops_email_smtp': smtp_ok,
            'confirm_yes_no_links': bool(confirm_url),
        },
        'missing_for_full_notifications': [
            k
            for k, ok in [
                ('TWILIO_ACCOUNT_SID', twilio_sid),
                ('TWILIO_AUTH_TOKEN', twilio_token),
                ('TWILIO_FROM_NUMBER', bool(twilio_from)),
                ('SENDGRID_API_KEY', bool(os.environ.get('SENDGRID_API_KEY'))),
                ('SENDGRID_FROM_EMAIL', bool(os.environ.get('SENDGRID_FROM_EMAIL'))),
                ('NEXUS_EMAIL_PASSWORD', bool(os.environ.get('NEXUS_EMAIL_PASSWORD'))),
                ('NEXUS_CONFIRM_BASE_URL', bool(confirm_url)),
            ]
            if not ok
        ],
    }


@app.route('/health', methods=['GET'])
def health_check():
    notifications = _notification_config()
    all_channels = all(notifications['channels_ready'].values())
    return jsonify({
        'status': 'healthy',
        'service': 'NEXUS PRISM API',
        'version': '1.0.1',
        'mode': 'pa-minimal',
        'notifications': notifications,
        'notifications_ready': all_channels,
    })


try:
    from prism_orders_api import prism_orders

    app.register_blueprint(prism_orders)
except ImportError as exc:
    @app.route('/prism/<path:_path>', methods=['GET', 'POST', 'PATCH'])
    def prism_unavailable(_path):
        return jsonify({'error': f'PRISM Orders API not loaded: {exc}'}), 503


# PythonAnywhere WSGI entry point
application = app
