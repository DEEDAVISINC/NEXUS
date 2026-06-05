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


@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'NEXUS PRISM API',
        'version': '1.0.0',
        'mode': 'pa-minimal',
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
