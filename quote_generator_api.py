"""
NEXUS Quote Generator API
Endpoint for generating supplier quote requests from solicitation data
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import json
import subprocess
import tempfile
import os
from pathlib import Path
import re

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Output directory for generated quotes
OUTPUT_DIR = Path("GENERATED_QUOTES")
OUTPUT_DIR.mkdir(exist_ok=True)


def parse_quote_data(data):
    """Parse quote data from JSON to template format"""
    
    template = f"""RFQ_NUMBER: {data.get('rfq_number', 'RFQ-2026-001')}
TITLE: {data.get('title', 'Quote Request')}
ISSUE_DATE: {data.get('issue_date', 'January 26, 2026')}
DUE_DATE: {data.get('due_date', 'February 5, 2026')}
DUE_TIME: {data.get('due_time', '5:00 PM EST')}
CONTRACT_PERIOD: {data.get('contract_period', '12 months')}

COLOR_SCHEME: {data.get('color_scheme', '1')}

INTRODUCTION:
{data.get('introduction', 'DEE DAVIS INC is seeking competitive quotes.')}

SCOPE:
{data.get('scope', 'Vendor will provide materials as specified.')}

KEY_REQUIREMENTS:
"""
    
    # Add requirements
    for req in data.get('requirements', []):
        template += f"- {req}\n"
    
    template += "\nITEMS:\n"
    
    # Add items
    for item in data.get('items', []):
        template += f"{item.get('number', 1)} | {item.get('description', '')} | {item.get('specs', '')} | {item.get('quantity', '')} | {item.get('unit', 'unit')}\n"
    
    return template


@app.route('/api/quote/generate-from-paste', methods=['POST'])
def generate_quote_from_paste():
    """
    Generate quote from pasted template text
    
    POST /api/quote/generate-from-paste
    Body: {
        "paste_text": "RFQ_NUMBER: DDI-2026-001\nTITLE: ...",
        "request_type": "supplier" | "subcontractor"  # optional, defaults to supplier
    }
    """
    try:
        data = request.json
        paste_text = data.get('paste_text', '')
        request_type = data.get('request_type', 'supplier').upper()
        
        if not paste_text:
            return jsonify({'success': False, 'error': 'No paste text provided'}), 400
        
        # Add REQUEST_TYPE to paste_text if not already present
        if 'REQUEST_TYPE:' not in paste_text:
            paste_text = f"REQUEST_TYPE: {request_type}\n{paste_text}"
        
        # Create temp file with paste text
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(paste_text)
            temp_file = f.name
        
        # Generate the quote
        result = subprocess.run(
            ['python3', 'create_from_paste.py', 'rfq', temp_file],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        
        # Clean up temp file
        os.unlink(temp_file)
        
        if result.returncode != 0:
            return jsonify({
                'success': False,
                'error': result.stderr
            }), 500
        
        # Extract generated filenames
        output_lines = result.stdout.split('\n')
        files = {}
        
        for line in output_lines:
            if '.html' in line:
                match = re.search(r'(rfq_[a-z0-9_]+\.html)', line)
                if match:
                    files['html'] = match.group(1)
            if '.pdf' in line and 'config' not in line:
                match = re.search(r'(rfq_[a-z0-9_]+\.pdf)', line)
                if match:
                    files['pdf'] = match.group(1)
            if '_config.json' in line:
                match = re.search(r'(rfq_[a-z0-9_]+_config\.json)', line)
                if match:
                    files['config'] = match.group(1)
        
        # Move files to output directory
        for file_type, filename in files.items():
            if os.path.exists(filename):
                dest = OUTPUT_DIR / filename
                os.rename(filename, dest)
                files[file_type] = str(dest)
        
        # Extract just the filename (without GENERATED_QUOTES/ path) for download URL
        pdf_filename = os.path.basename(files.get('pdf', ''))
        
        return jsonify({
            'success': True,
            'files': files,
            'download_url': f"/api/quote/download/{pdf_filename}" if pdf_filename else None
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/quote/generate', methods=['POST'])
def generate_quote():
    """
    Generate a supplier quote request
    
    POST /api/quote/generate
    Body: {
        "rfq_number": "DDI-2026-001",
        "title": "Quote Request Title",
        "issue_date": "January 26, 2026",
        "due_date": "February 5, 2026",
        "due_time": "5:00 PM EST",
        "contract_period": "12 months",
        "color_scheme": "1",
        "introduction": "Your introduction text...",
        "scope": "Your scope text...",
        "requirements": ["Requirement 1", "Requirement 2"],
        "items": [
            {
                "number": "1",
                "description": "Item name",
                "specs": "Specifications",
                "quantity": "100",
                "unit": "pieces"
            }
        ]
    }
    
    Returns: {
        "success": true,
        "files": {
            "html": "filename.html",
            "pdf": "filename.pdf",
            "config": "filename_config.json"
        },
        "download_url": "/api/quote/download/filename.pdf"
    }
    """
    try:
        data = request.json
        
        # Convert to template format
        template_text = parse_quote_data(data)
        
        # Create temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(template_text)
            temp_file = f.name
        
        # Generate the quote
        result = subprocess.run(
            ['python3', 'create_from_paste.py', 'rfq', temp_file],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        
        # Clean up temp file
        os.unlink(temp_file)
        
        if result.returncode != 0:
            return jsonify({
                'success': False,
                'error': result.stderr
            }), 500
        
        # Extract generated filenames
        output_lines = result.stdout.split('\n')
        files = {}
        
        for line in output_lines:
            if '.html' in line:
                match = re.search(r'(rfq_[a-z0-9_]+\.html)', line)
                if match:
                    files['html'] = match.group(1)
            if '.pdf' in line and 'config' not in line:
                match = re.search(r'(rfq_[a-z0-9_]+\.pdf)', line)
                if match:
                    files['pdf'] = match.group(1)
            if '_config.json' in line:
                match = re.search(r'(rfq_[a-z0-9_]+_config\.json)', line)
                if match:
                    files['config'] = match.group(1)
        
        # Move files to output directory
        for file_type, filename in files.items():
            if os.path.exists(filename):
                dest = OUTPUT_DIR / filename
                os.rename(filename, dest)
                files[file_type] = str(dest)
        
        # Extract just the filename (without GENERATED_QUOTES/ path) for download URL
        pdf_filename = os.path.basename(files.get('pdf', ''))
        
        return jsonify({
            'success': True,
            'files': files,
            'download_url': f"/api/quote/download/{pdf_filename}" if pdf_filename else None
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/quote/download/<filename>', methods=['GET'])
def download_quote(filename):
    """Download a generated quote file"""
    try:
        filepath = OUTPUT_DIR / filename
        if not filepath.exists():
            return jsonify({'error': 'File not found'}), 404
        
        return send_file(
            filepath,
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/quote/template', methods=['GET'])
def get_template():
    """Get a blank template for quote generation"""
    template = {
        "rfq_number": "RFQ-2026-001",
        "title": "Quote Request Title",
        "issue_date": "January 26, 2026",
        "due_date": "February 5, 2026",
        "due_time": "5:00 PM EST",
        "contract_period": "12 months",
        "color_scheme": "1",
        "introduction": "DEE DAVIS INC is seeking competitive quotes for a Michigan municipal client.",
        "scope": "Vendor will provide materials as specified with delivery to Southeast Michigan.",
        "requirements": [
            "Competitive pricing required",
            "Confirm delivery lead times",
            "Provide payment terms",
            "Quote valid through specified date"
        ],
        "items": [
            {
                "number": "1",
                "description": "Item Description",
                "specs": "Specifications and details",
                "quantity": "100",
                "unit": "unit"
            }
        ]
    }
    
    return jsonify(template)


@app.route('/api/quote/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'NEXUS Quote Generator API',
        'version': '1.0.0'
    })


@app.route('/api/quote/request-from-opportunity', methods=['POST'])
def request_from_opportunity():
    """
    Complete workflow: Generate and send quotes to suppliers for an opportunity
    
    POST /api/quote/request-from-opportunity
    Body: {
        "opportunity_id": "recXXXXXX",
        "supplier_ids": ["recYYYYYY", "recZZZZZZ"]  # optional
    }
    
    Returns: {
        "success": true,
        "quote_requests": [...]
    }
    """
    try:
        from supplier_quote_workflow import request_quotes_for_opportunity
        
        data = request.json
        opportunity_id = data.get('opportunity_id')
        
        if not opportunity_id:
            return jsonify({'success': False, 'error': 'No opportunity_id provided'}), 400
        
        # Process the solicitation
        result = request_quotes_for_opportunity(opportunity_id)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    print("="*60)
    print("🚀 NEXUS Quote Generator API")
    print("="*60)
    print(f"Output directory: {OUTPUT_DIR.absolute()}")
    print(f"API running on: http://localhost:5001")
    print(f"Frontend should connect to: http://localhost:5001/api/quote/")
    print("\n📋 Workflow Integration:")
    print("  • Generate quotes from opportunities")
    print("  • Auto-send to suppliers")
    print("  • Track and follow-up")
    print("="*60 + "\n")
    
    app.run(debug=True, port=5001, host='0.0.0.0')
