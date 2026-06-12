#!/usr/bin/env python3
"""
Minimal NEXUS PRISM API — PythonAnywhere / slim deploy.

Loads only PRISM order intake + ops queue routes. Avoids importing the full
api_server stack (GPSS, JETA, bid scanners, etc.) which can fail on PA free tier.
"""

import os

from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

app = Flask(__name__)
CORS(app)

_nemt_loaded = False
_member_survey_loaded = False
_member_survey_error = None
_qc_loaded = False
_qc_error = None


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
        'version': '1.0.3',
        'mode': 'pa-minimal',
        'modules': {
            'nemt': _nemt_loaded,
            'member_survey': _member_survey_loaded,
            'nexus_qc': _qc_loaded,
        },
        'member_survey_error': _member_survey_error,
        'nexus_qc_error': _qc_error,
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

try:
    from prism_notifications_api import prism_notifications

    app.register_blueprint(prism_notifications)
except ImportError as exc:
    logger_msg_notif = f'PRISM Notifications API not loaded: {exc}'

    @app.route('/prism/notifications', methods=['GET'])
    @app.route('/prism/notifications/read', methods=['POST'])
    def prism_notifications_unavailable():
        return jsonify({'error': logger_msg_notif, 'notifications': [], 'unread': 0}), 503


try:
    from prism_voice_intake import prism_voice

    app.register_blueprint(prism_voice)
except ImportError as exc:
    logger_msg = f'PRISM Voice Intake not loaded: {exc}'

    @app.route('/prism/voice/<path:_path>', methods=['GET', 'POST'])
    def prism_voice_unavailable(_path):
        return jsonify({'error': logger_msg}), 503

try:
    from prism_nemt import prism_nemt

    app.register_blueprint(prism_nemt)
    _nemt_loaded = True
except ImportError as exc:
    _nemt_loaded = False
    _nemt_err = f'PRISM NEMT API not loaded: {exc}'

    @app.route('/prism/nemt/<path:_path>', methods=['GET', 'POST'])
    def prism_nemt_unavailable(_path):
        return jsonify({'error': _nemt_err}), 503


@app.route('/shield/webhook/twilio-inbound', methods=['POST'])
def shield_twilio_inbound():
    """Twilio inbound SMS — CONFIRM/CANCEL for NEXUS confirmation engine."""
    from_number = request.form.get('From', '')
    body = request.form.get('Body', '').strip()
    keyword = body.upper().split()[0] if body else ''

    nexus_reply = None
    if keyword in ('CONFIRM', 'CANCEL', 'YES', 'NO'):
        try:
            from nexus_confirmation_engine import (
                _load_log, _clean_phone, mark_confirmed, mark_cancelled,
            )
            from company_info import BRAND_NAME, member_care_phone_display

            member_care = member_care_phone_display()
            clean_from = _clean_phone(from_number)
            pending = [
                r for r in _load_log()
                if _clean_phone(r.get('party_phone', '')) == clean_from
                and r.get('status') == 'pending'
            ]
            if pending:
                rec = pending[0]
                if keyword in ('CONFIRM', 'YES'):
                    mark_confirmed(rec['token'], channel='sms')
                    nexus_reply = (
                        "✅ Confirmed! We have your appointment on file. "
                        f"See you then. Questions? Call {member_care}"
                    )
                elif keyword in ('CANCEL', 'NO'):
                    mark_cancelled(rec['token'], channel='sms')
                    nexus_reply = (
                        "We've noted your cancellation. "
                        f"Call {BRAND_NAME} at {member_care} to reschedule."
                    )
        except Exception:
            pass

    if nexus_reply:
        twiml = (
            '<?xml version="1.0" encoding="UTF-8"?><Response>'
            f'<Message>{nexus_reply}</Message>'
            '</Response>'
        )
        return twiml, 200, {'Content-Type': 'text/xml'}

    # Advanced Opt-Out handles HELP/STOP on the Messaging Service; empty TwiML OK.
    return '<?xml version="1.0" encoding="UTF-8"?><Response></Response>', 200, {
        'Content-Type': 'text/xml',
    }


try:
    from member_satisfaction_survey import member_survey

    app.register_blueprint(member_survey)
    _member_survey_loaded = True
except ImportError as exc:
    _member_survey_error = str(exc)
    logger_msg_survey = f'Member satisfaction survey not loaded: {exc}'

    @app.route('/member/survey/<path:_path>', methods=['GET', 'POST'])
    @app.route('/prism/nemt/satisfaction/<path:_path>', methods=['GET', 'POST'])
    def member_survey_unavailable(_path):
        return jsonify({
            'error': logger_msg_survey,
            'hint': 'Pull member_satisfaction_survey.py + member_trip_grade_audit_report.py and reload web app.',
        }), 503

_qc_loaded = False
_qc_error = None
try:
    from nexus_qc_api import nexus_qc

    app.register_blueprint(nexus_qc)
    _qc_loaded = True
except ImportError as exc:
    _qc_error = str(exc)


# PythonAnywhere WSGI entry point
application = app
