#!/usr/bin/env python3
"""
Bids Dashboard API
Serves adaptive dashboard data to NEXUS frontend
"""

from flask import Flask, jsonify
from flask_cors import CORS
import json
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

LEARNING_DATA_FILE = "bid_learning_data.json"

def load_dashboard_data():
    """Load and format dashboard data"""
    # This would integrate with adaptive_bid_system.py
    # For now, return structured data
    
    return {
        "focusBid": {
            "name": "HENRY FORD BATTERY CABINETS",
            "value": 15000,
            "deadline": "February 11, 2026",
            "daysLeft": 2,
            "status": "urgent",
            "activity": {
                "fileCount": 4,
                "lastEdited": "2 days ago"
            },
            "hasQuotes": False,
            "hasSubmission": False
        },
        "urgentBids": [
            {
                "name": "OAKLAND COUNTY TREATED SALT",
                "value": 50000,
                "deadline": "February 12, 2026",
                "daysLeft": 3,
                "status": "urgent",
                "activity": {"fileCount": 0, "lastEdited": "Never"},
                "hasQuotes": False,
                "hasSubmission": False
            },
            {
                "name": "OAKLAND COUNTY FLOW METERS",
                "value": 8000,
                "deadline": "February 12, 2026",
                "daysLeft": 3,
                "status": "urgent",
                "activity": {"fileCount": 0, "lastEdited": "Never"},
                "hasQuotes": False,
                "hasSubmission": False
            }
        ],
        "thisWeekBids": [
            {"name": "CPS ENERGY PADLOCKS", "value": 32000, "deadline": "February 13, 2026", "daysLeft": 4, "status": "active", "activity": {"fileCount": 15, "lastEdited": "1 day ago"}, "hasQuotes": False, "hasSubmission": False},
            {"name": "AUBURN HILLS PRESSURE WASHING", "value": 5000, "deadline": "February 13, 2026", "daysLeft": 4, "status": "active", "activity": {"fileCount": 3, "lastEdited": "3 days ago"}, "hasQuotes": False, "hasSubmission": False},
            {"name": "OAKLAND COUNTY EXAM STOOLS", "value": 3000, "deadline": "February 16, 2026", "daysLeft": 7, "status": "active", "activity": {"fileCount": 2, "lastEdited": "1 day ago"}, "hasQuotes": False, "hasSubmission": False}
        ],
        "completedBids": [
            {"name": "SHELBY TOWNSHIP POWER CABLES", "value": 75000, "status": "completed"},
            {"name": "GENESEE WOOD POLES", "value": 45000, "status": "completed"},
            {"name": "HCMA CHLORINE", "value": 30000, "status": "completed"},
            {"name": "CPS ENERGY", "value": 25000, "status": "completed"},
            {"name": "RCOC 7790 SIGNS", "value": 10000, "status": "completed"},
            {"name": "RCOC 7842 SAFETY SUPPLIES", "value": 8000, "status": "completed"}
        ],
        "totalValue": 353000,
        "completedValue": 193000,
        "autoRemovedCount": 1
    }

@app.route('/api/bids/dashboard', methods=['GET'])
def get_dashboard():
    """Get adaptive dashboard data"""
    try:
        data = load_dashboard_data()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/bids/refresh', methods=['POST'])
def refresh_dashboard():
    """Trigger adaptive system refresh"""
    try:
        # This would call adaptive_bid_system.py
        os.system('python3 adaptive_bid_system.py')
        return jsonify({"success": True, "message": "Dashboard refreshed"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=8001, debug=True)
