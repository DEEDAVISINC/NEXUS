"""
NEXUS API Server
Flask app with webhook endpoints for Make.com integration
"""

from flask import Flask, request, jsonify
import os
from nexus_backend import (
    Config,
    handle_document_upload,
    handle_qualify_opportunity,
    handle_generate_quote
)

app = Flask(__name__)

# Set base ID from environment
Config.AIRTABLE_BASE_ID = os.environ.get('AIRTABLE_BASE_ID', '')

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "NEXUS Backend",
        "version": "1.0.0"
    })

@app.route('/extract-contacts', methods=['POST'])
def extract_contacts():
    """
    Extract contacts from document text
    
    Expected JSON:
    {
        "document_text": "...",
        "document_name": "RFP-12345.pdf"
    }
    """
    try:
        data = request.json
        document_text = data.get('document_text', '')
        document_name = data.get('document_name', 'Unknown Document')
        
        if not document_text:
            return jsonify({"error": "document_text required"}), 400
        
        result = handle_document_upload(document_text, document_name)
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/qualify-opportunity', methods=['POST'])
def qualify_opportunity():
    """
    Qualify a government opportunity
    
    Expected JSON:
    {
        "opportunity_id": "rec..."
    }
    """
    try:
        data = request.json
        opportunity_id = data.get('opportunity_id', '')
        
        if not opportunity_id:
            return jsonify({"error": "opportunity_id required"}), 400
        
        result = handle_qualify_opportunity(opportunity_id)
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/generate-quote', methods=['POST'])
def generate_quote():
    """
    Generate quote for opportunity
    
    Expected JSON:
    {
        "opportunity_id": "rec..."
    }
    """
    try:
        data = request.json
        opportunity_id = data.get('opportunity_id', '')
        
        if not opportunity_id:
            return jsonify({"error": "opportunity_id required"}), 400
        
        result = handle_generate_quote(opportunity_id)
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
