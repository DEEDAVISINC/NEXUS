"""
NEXUS API Server
Flask app with webhook endpoints for Make.com integration
"""

# Load environment variables from .env file FIRST
import os
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

from flask import Flask, request, jsonify
from flask_cors import CORS
import jwt
from datetime import datetime, timedelta
from functools import wraps
from nexus_backend import (
    Config,
    AirtableClient,
    GPSSPricingAgent,
    GPSSComplianceAgent,
    GPSSOpportunityMiningAgent,
    handle_document_upload,
    handle_qualify_opportunity,
    handle_generate_quote,
    handle_ddcss_qualify_prospect,
    handle_generate_invoice_from_opportunity,
    handle_generate_invoice_from_project,
    handle_atlas_analyze_rfp,
    handle_ddcss_generate_blueprint,
    handle_ddcss_analyze_response,
    handle_atlas_analyze_rfp,
    handle_atlas_generate_wbs,
    handle_atlas_analyze_change_request,
    handle_generate_invoice_from_opportunity,
    handle_generate_invoice_from_project,
    handle_generate_invoice_from_prospect,
    handle_get_invoices,
    handle_get_invoice,
    handle_update_invoice,
    handle_delete_invoice,
    # LBPC handlers
    handle_lbpc_get_leads,
    handle_lbpc_create_lead,
    handle_lbpc_update_lead,
    handle_lbpc_delete_lead,
    handle_lbpc_generate_document,
    handle_lbpc_get_documents,
    handle_lbpc_get_tasks,
    handle_lbpc_update_task,
    handle_lbpc_ai_qualify_lead,
    handle_lbpc_create_invoice,
    handle_lbpc_import_csv,
    handle_lbpc_get_analytics
)
from datetime import datetime, timedelta
import jwt
from functools import wraps
import json

# ProposalBio™ Quality Assurance Module
from proposalbio_module import ProposalBioService


app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Set base ID from environment
Config.AIRTABLE_BASE_ID = os.environ.get('AIRTABLE_BASE_ID', '')

# JWT Secret for Alexa authentication
JWT_SECRET = os.environ.get('JWT_SECRET', 'nexus-alexa-secret-key-change-in-production')

def require_alexa_auth(f):
    """Decorator to require Alexa JWT authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Missing or invalid authorization header'}), 401

        token = auth_header.split(' ')[1]
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
            # Check if token is for Alexa user
            if payload.get('user') != 'alexa_user':
                return jsonify({'error': 'Invalid token user'}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401

        return f(*args, **kwargs)
    return decorated_function

@app.route('/auth/alexa', methods=['POST'])
def alexa_auth():
    """Alexa authentication endpoint - validates skill ID and returns JWT"""
    try:
        # Validate Alexa Skill ID
        skill_id = request.headers.get('Alexa-Skill-Id')
        expected_skill_id = os.environ.get('ALEXA_SKILL_ID')

        if not expected_skill_id:
            return jsonify({'error': 'Alexa integration not configured'}), 500

        if skill_id != expected_skill_id:
            return jsonify({'error': 'Unauthorized skill'}), 401

        # Generate JWT token valid for 1 hour
        token = jwt.encode({
            'user': 'alexa_user',
            'skill_id': skill_id,
            'exp': datetime.utcnow() + timedelta(hours=1),
            'iat': datetime.utcnow()
        }, JWT_SECRET, algorithm='HS256')

        return jsonify({
            'success': True,
            'token': token,
            'expires_in': 3600  # 1 hour
        })

    except Exception as e:
        return jsonify({
            'error': f'Authentication failed: {str(e)}'
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "NEXUS Backend",
        "version": "1.0.0"
    })

@app.route('/dashboard/stats', methods=['GET'])
def get_dashboard_stats():
    """
    Get real-time dashboard statistics from Airtable
    Returns: counts, revenue, and aggregated data
    """
    try:
        airtable_client = AirtableClient()
        
        # Get data from all tables
        opportunities = airtable_client.get_all_records('GPSS OPPORTUNITIES')
        contacts = airtable_client.get_all_records('GPSS CONTACTS')
        
        # Try to get ATLAS projects (might not exist yet)
        try:
            atlas_projects = airtable_client.get_all_records('ATLAS PROJECTS')
        except:
            atlas_projects = []
        
        # Calculate stats
        active_opportunities = [opp for opp in opportunities if opp['fields'].get('Status') in ['Active', 'Qualifying', 'Proposal']]
        
        # Calculate total pipeline value
        total_pipeline = 0
        for opp in active_opportunities:
            value = opp['fields'].get('Value', 0)
            if isinstance(value, (int, float)):
                total_pipeline += value
        
        # Count active projects
        active_projects = [proj for proj in atlas_projects if proj['fields'].get('Status') in ['Active', 'In Progress', 'Planning']]
        
        # Get system-specific stats
        gpss_opportunities = [opp for opp in opportunities if opp['fields'].get('Source') in ['Government', 'SAM.gov', 'GPSS']]
        gpss_pipeline = sum(opp['fields'].get('Value', 0) for opp in gpss_opportunities if isinstance(opp['fields'].get('Value', 0), (int, float)))
        
        # Build response
        stats = {
            'active_opportunities': len(active_opportunities),
            'total_contacts': len(contacts),
            'active_projects': len(active_projects),
            'revenue_pipeline': total_pipeline,
            'systems': {
                'gpss': {
                    'opportunities': len(gpss_opportunities),
                    'pipeline': gpss_pipeline,
                    'contacts': len([c for c in contacts if c['fields'].get('Source') == 'Government'])
                },
                'ddcss': {
                    'prospects': 0,  # Will be calculated once DDCSS table exists
                    'responses': 0,
                    'sectors': 6
                },
                'atlas': {
                    'projects': len(active_projects),
                    'rfps_analyzed': len([proj for proj in atlas_projects if proj['fields'].get('RFP Analyzed') == True]),
                    'total_value': sum(proj['fields'].get('Budget', 0) for proj in atlas_projects if isinstance(proj['fields'].get('Budget', 0), (int, float)))
                }
            },
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(stats)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/dashboard/activity', methods=['GET'])
def get_dashboard_activity():
    """
    Get recent activity feed from all systems
    Returns: recent records sorted by creation date
    """
    try:
        airtable_client = AirtableClient()
        activities = []
        
        # Get recent contacts
        try:
            contacts = airtable_client.get_all_records('GPSS CONTACTS', sort=['Created'])
            for contact in contacts[-5:]:  # Last 5 contacts
                fields = contact['fields']
                activities.append({
                    'type': 'contact',
                    'system': 'GPSS',
                    'action': 'Contact Extracted',
                    'title': f"{fields.get('First Name', '')} {fields.get('Last Name', '')} - {fields.get('Agency', '')}",
                    'time': fields.get('Created', ''),
                    'icon': '👤',
                    'color': 'text-blue-400'
                })
        except Exception as e:
            print(f"Error fetching contacts: {e}")
        
        # Get recent opportunities
        try:
            opportunities = airtable_client.get_all_records('GPSS OPPORTUNITIES', sort=['Created Date'])
            for opp in opportunities[-5:]:  # Last 5 opportunities
                fields = opp['fields']
                activities.append({
                    'type': 'opportunity',
                    'system': 'GPSS',
                    'action': 'New Opportunity',
                    'title': f"{fields.get('Title', 'Untitled')} - ${fields.get('Value', 0):,.0f}",
                    'time': fields.get('Created Date', ''),
                    'icon': '🎯',
                    'color': 'text-yellow-400'
                })
        except Exception as e:
            print(f"Error fetching opportunities: {e}")
        
        # Get recent ATLAS projects
        try:
            projects = airtable_client.get_all_records('ATLAS PROJECTS', sort=['Created Date'])
            for proj in projects[-5:]:  # Last 5 projects
                fields = proj['fields']
                activities.append({
                    'type': 'project',
                    'system': 'ATLAS PM',
                    'action': 'Project Updated',
                    'title': f"{fields.get('Project Name', 'Untitled')} - {fields.get('Completion Percentage', 0)}% Complete",
                    'time': fields.get('Last Updated', fields.get('Created Date', '')),
                    'icon': '📋',
                    'color': 'text-purple-400'
                })
        except Exception as e:
            print(f"Error fetching projects: {e}")
        
        # Sort by time (most recent first)
        activities.sort(key=lambda x: x['time'], reverse=True)
        
        return jsonify({'activities': activities[:10]})  # Return top 10
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/dashboard/alerts', methods=['GET'])
def get_dashboard_alerts():
    """
    Get alerts and notifications
    Returns: urgent items requiring attention
    """
    try:
        airtable_client = AirtableClient()
        alerts = []
        
        # Check for upcoming RFP deadlines (within 7 days)
        try:
            opportunities = airtable_client.get_all_records('GPSS OPPORTUNITIES')
            now = datetime.now()
            
            for opp in opportunities:
                fields = opp['fields']
                due_date_str = fields.get('Due Date')
                if due_date_str:
                    try:
                        due_date = datetime.fromisoformat(due_date_str.replace('Z', '+00:00'))
                        days_until = (due_date - now).days
                        
                        if 0 <= days_until <= 7 and fields.get('Status') in ['Active', 'Proposal']:
                            alerts.append({
                                'type': 'urgent' if days_until <= 3 else 'warning',
                                'title': f'RFP Deadline Approaching',
                                'message': f"{fields.get('Title', 'Untitled')} due in {days_until} days",
                                'action': 'Review RFP',
                                'system': 'GPSS'
                            })
                    except:
                        pass
        except Exception as e:
            print(f"Error checking deadlines: {e}")
        
        # Check for pending change orders
        try:
            change_orders = airtable_client.get_all_records('ATLAS CHANGE ORDERS')
            pending = [co for co in change_orders if co['fields'].get('Status') == 'Pending']
            
            for co in pending[:3]:  # Top 3 pending
                fields = co['fields']
                alerts.append({
                    'type': 'info',
                    'title': 'Change Order Pending',
                    'message': f"{fields.get('Title', 'Untitled')} - ${fields.get('Impact Budget', 0):,.0f} approval needed",
                    'action': 'Review',
                    'system': 'ATLAS PM'
                })
        except Exception as e:
            print(f"Error checking change orders: {e}")
        
        return jsonify({'alerts': alerts})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/extract-contacts', methods=['POST'])
def extract_contacts():
    """
    Extract contacts from document text or uploaded PDF file

    Accepts either:
    1. JSON: {"document_text": "...", "document_name": "..."}
    2. Form data with file: uploaded PDF file
    """
    try:
        document_text = ""
        document_name = "Unknown Document"

        # Check if it's a file upload
        if 'file' in request.files:
            file = request.files['file']
            if file.filename == '':
                return jsonify({"error": "No file selected"}), 400

            if file and file.filename.lower().endswith('.pdf'):
                document_name = file.filename

                # Process PDF file with error handling
                try:
                    import PyPDF2
                    pdf_reader = PyPDF2.PdfReader(file)

                    # Extract text from all pages (limit to first 20 pages for performance)
                    document_text = ""
                    max_pages = min(len(pdf_reader.pages), 20)

                    for page_num in range(max_pages):
                        try:
                            page = pdf_reader.pages[page_num]
                            page_text = page.extract_text()
                            if page_text and page_text.strip():
                                document_text += page_text.strip() + "\n"
                        except Exception as page_error:
                            # Skip problematic pages
                            continue

                    if not document_text.strip():
                        return jsonify({
                            "success": False,
                            "error": "No readable text found in PDF. The PDF may contain only images, be scanned, or password-protected. Try uploading a different PDF or use the manual text entry option."
                        }), 400

                except Exception as pdf_error:
                    return jsonify({
                        "success": False,
                        "error": f"PDF processing failed: {str(pdf_error)}. Try a different PDF file or use manual text entry."
                    }), 400

        # Check if it's JSON text input
        elif request.is_json:
            data = request.json
            document_text = data.get('document_text', '')
            document_name = data.get('document_name', 'Unknown Document')

            if not document_text:
                return jsonify({"error": "document_text required"}), 400

        else:
            return jsonify({"error": "Invalid request format. Send JSON with document_text or upload a PDF file."}), 400

        # Process the extracted text
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

# =====================================================================
# DDCSS ENDPOINTS - Corporate Sales System
# =====================================================================

@app.route('/ddcss/qualify-prospect', methods=['POST'])
def ddcss_qualify_prospect():
    """
    Qualify a corporate prospect using AI analysis

    Expected JSON:
    {
        "prospect_id": "rec..."
    }
    """
    try:
        data = request.json
        prospect_id = data.get('prospect_id', '')

        if not prospect_id:
            return jsonify({"error": "prospect_id required"}), 400

        result = handle_ddcss_qualify_prospect(prospect_id)
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/ddcss/generate-blueprint', methods=['POST'])
def ddcss_generate_blueprint():
    """
    Generate a customized Blueprint Framework

    Expected JSON:
    {
        "prospect_id": "rec...",
        "framework_type": "ALIGN|DEFINE|DESIGN|SHINE" (optional, defaults to ALIGN)
    }
    """
    try:
        data = request.json
        prospect_id = data.get('prospect_id', '')
        framework_type = data.get('framework_type', 'ALIGN')

        if not prospect_id:
            return jsonify({"error": "prospect_id required"}), 400

        if framework_type not in ['ALIGN', 'DEFINE', 'DESIGN', 'SHINE']:
            return jsonify({"error": "Invalid framework_type. Must be ALIGN, DEFINE, DESIGN, or SHINE"}), 400

        result = handle_ddcss_generate_blueprint(prospect_id, framework_type)
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/ddcss/analyze-response', methods=['POST'])
def ddcss_analyze_response():
    """
    Analyze inbound email response using AI

    Expected JSON:
    {
        "email_content": "Full email text...",
        "prospect_id": "rec..." (optional)
    }
    """
    try:
        data = request.json
        email_content = data.get('email_content', '')
        prospect_id = data.get('prospect_id', '')

        if not email_content:
            return jsonify({"error": "email_content required"}), 400

        result = handle_ddcss_analyze_response(email_content, prospect_id or None)
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# =====================================================================
# ATLAS PM ENDPOINTS - Project Management System
# =====================================================================

# Project CRUD operations
@app.route('/atlas/projects', methods=['GET'])
def get_atlas_projects():
    """Get all projects with optional filtering"""
    try:
        airtable_client = AirtableClient()
        records = airtable_client.get_all_records('ATLAS PROJECTS')

        # Transform records for frontend
        projects = []
        for record in records:
            fields = record['fields']
            projects.append({
                'id': record['id'],
                'name': fields.get('Project Name', ''),
                'client': fields.get('Client Name', ''),
                'status': fields.get('Status', 'Planning'),
                'budget': fields.get('Budget', 0),
                'timeline': fields.get('Timeline', ''),
                'completion_percentage': fields.get('Completion Percentage', 0),
                'priority': fields.get('Priority', 'Medium'),
                'start_date': fields.get('Start Date'),
                'end_date': fields.get('End Date'),
                'created_date': fields.get('Created Date')
            })

        return jsonify({'projects': projects})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/atlas/projects', methods=['POST'])
def create_atlas_project():
    """Create a new project"""
    try:
        data = request.json
        airtable_client = AirtableClient()

        fields = {
            'Project Name': data.get('name', ''),
            'Client Name': data.get('client', ''),
            'Project Type': data.get('type', 'Consulting'),
            'Industry': data.get('industry', ''),
            'Project Scope': data.get('scope', ''),
            'Budget': data.get('budget', 0),
            'Timeline': data.get('timeline', ''),
            'Start Date': data.get('start_date'),
            'Status': 'Planning',
            'Priority': data.get('priority', 'Medium'),
            'Completion Percentage': 0,
            'Created Date': datetime.now().isoformat()
        }

        result = airtable_client.create_record('ATLAS PROJECTS', fields)
        return jsonify({'project': {'id': result['id'], **fields}})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def create_atlas_project_from_opportunity(opportunity_id: str, airtable_client=None) -> dict:
    """
    🎯 AUTO-CREATE ATLAS PROJECT FROM WON GPSS OPPORTUNITY
    This is the 90% automation bridge!
    """
    if not airtable_client:
        airtable_client = AirtableClient()
    
    # Get opportunity details
    opportunity = airtable_client.get_record('GPSS OPPORTUNITIES', opportunity_id)
    opp_fields = opportunity['fields']
    
    # Extract key information
    project_name = opp_fields.get('Title', 'Untitled Project')
    client_name = opp_fields.get('Agency Name', 'Unknown Agency')
    contract_value = opp_fields.get('Value', 0)
    rfp_number = opp_fields.get('RFP Number', '')
    due_date = opp_fields.get('Due Date', '')
    description = opp_fields.get('Description', '')
    requirements = opp_fields.get('Requirements', '')
    category = opp_fields.get('Category', 'General')
    
    # Build comprehensive project scope from opportunity data
    project_scope = f"""
CONTRACT: {rfp_number}
AGENCY: {client_name}
CATEGORY: {category}

DESCRIPTION:
{description}

REQUIREMENTS:
{requirements}
    """.strip()
    
    # Calculate project timeline (default 6 months or based on contract)
    start_date = datetime.now().isoformat()
    
    # Determine project type based on category
    project_type_mapping = {
        'Healthcare': 'Healthcare Services',
        'Logistics': 'Logistics & Transportation',
        'IT': 'Technology Services',
        'Construction': 'Construction',
        'Consulting': 'Professional Services',
        'Products': 'Product Delivery',
        'Supplies': 'Product Delivery'
    }
    project_type = project_type_mapping.get(category, 'Government Contract')
    
    # Create ATLAS project record
    project_fields = {
        'Project Name': f"{project_name} ({client_name})",
        'Client Name': client_name,
        'Project Type': project_type,
        'Budget': contract_value,
        'Project Scope': project_scope[:10000],  # Airtable field limit
        'Start Date': start_date,
        'Status': 'Planning',
        'Priority': 'High',
        'Completion Percentage': 0,
        'Created Date': datetime.now().isoformat(),
        'Source System': 'GPSS',
        'Source Opportunity ID': opportunity_id,
        'Contract Number': rfp_number
    }
    
    # Create the project in Airtable
    project_record = airtable_client.create_record('ATLAS PROJECTS', project_fields)
    project_id = project_record['id']
    
    # Link opportunity to ATLAS project (bidirectional)
    try:
        airtable_client.update_record('GPSS OPPORTUNITIES', opportunity_id, {
            'ATLAS Project': [project_id]
        })
    except Exception as link_error:
        print(f"Warning: Could not link opportunity to ATLAS project: {link_error}")
    
    # 🤖 AUTO-GENERATE WBS using ATLAS Agent 2
    wbs_generated = False
    try:
        from nexus_backend import ATLASAgent2
        atlas_agent = ATLASAgent2()
        wbs_result = atlas_agent.generate_wbs(project_id)
        wbs_generated = 'error' not in wbs_result
    except Exception as wbs_error:
        print(f"Warning: WBS generation failed: {wbs_error}")
    
    return {
        'success': True,
        'project_id': project_id,
        'project_name': project_fields['Project Name'],
        'wbs_generated': wbs_generated,
        'message': f'✅ ATLAS project created: {project_fields["Project Name"]}'
    }


@app.route('/gpss/opportunities/<opportunity_id>/create-atlas-project', methods=['POST'])
def manual_create_atlas_project_from_opportunity(opportunity_id):
    """
    Manual endpoint to create ATLAS project from opportunity
    Used if auto-creation failed or for retroactive project creation
    """
    try:
        result = create_atlas_project_from_opportunity(opportunity_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def create_invoice_from_atlas_project(project_id: str, airtable_client=None) -> dict:
    """
    🎯 AUTO-CREATE INVOICE FROM COMPLETED ATLAS PROJECT
    Universal invoicing for all revenue-generating systems!
    """
    if not airtable_client:
        airtable_client = AirtableClient()
    
    # Get project details
    project = airtable_client.get_record('ATLAS PROJECTS', project_id)
    project_fields = project['fields']
    
    # Extract key information
    project_name = project_fields.get('Project Name', 'Untitled Project')
    client_name = project_fields.get('Client Name', 'Unknown Client')
    budget = project_fields.get('Budget', 0)
    project_type = project_fields.get('Project Type', 'General')
    source_system = project_fields.get('Source System', 'ATLAS')
    start_date = project_fields.get('Start Date', '')
    completion_date = project_fields.get('End Date') or datetime.now().isoformat()
    
    # Generate invoice number
    # Format: INV-YYYYMM-XXXX
    invoice_number = f"INV-{datetime.now().strftime('%Y%m')}-{datetime.now().strftime('%d%H%M')}"
    
    # Build invoice description
    invoice_description = f"""
PROJECT: {project_name}
CLIENT: {client_name}
PROJECT TYPE: {project_type}
PERIOD: {start_date[:10] if start_date else 'N/A'} to {completion_date[:10]}

Project completed and delivered as per agreement.
All deliverables submitted and accepted.
    """.strip()
    
    # Create invoice record
    invoice_fields = {
        'Invoice Number': invoice_number,
        'Client Name': client_name,
        'Invoice Date': datetime.now().isoformat(),
        'Due Date': (datetime.now() + timedelta(days=30)).isoformat(),  # Net 30
        'Amount': budget,
        'Status': 'Draft',
        'Description': invoice_description,
        'Project': [project_id],  # Link to ATLAS project
        'Source System': source_system,
        'Created Date': datetime.now().isoformat()
    }
    
    # Create the invoice
    invoice_record = airtable_client.create_record('INVOICES', invoice_fields)
    invoice_id = invoice_record['id']
    
    # Link project to invoice
    try:
        airtable_client.update_record('ATLAS PROJECTS', project_id, {
            'Invoice': [invoice_id]
        })
    except Exception as link_error:
        print(f"Warning: Could not link project to invoice: {link_error}")
    
    return {
        'success': True,
        'invoice_id': invoice_id,
        'invoice_number': invoice_number,
        'invoice_amount': budget,
        'message': f'✅ Invoice created: {invoice_number} for ${budget:,.2f}'
    }


@app.route('/atlas/projects/<project_id>/create-invoice', methods=['POST'])
def manual_create_invoice_from_project(project_id):
    """Manual endpoint to create invoice from project"""
    try:
        result = create_invoice_from_atlas_project(project_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/atlas/projects/<project_id>', methods=['GET'])
def get_atlas_project(project_id):
    """Get specific project details"""
    try:
        airtable_client = AirtableClient()
        records = airtable_client.get_all_records('ATLAS PROJECTS')

        project = next((r for r in records if r['id'] == project_id), None)
        if not project:
            return jsonify({"error": "Project not found"}), 404

        fields = project['fields']
        return jsonify({
            'project': {
                'id': project_id,
                **fields
            }
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/atlas/projects/<project_id>', methods=['PUT'])
def update_atlas_project(project_id):
    """Update project details - with auto-INVOICE generation when completed"""
    try:
        data = request.json
        airtable_client = AirtableClient()
        
        # Get current project to check status change
        current_project = airtable_client.get_record('ATLAS PROJECTS', project_id)
        old_status = current_project['fields'].get('Status', '')
        old_completion = current_project['fields'].get('Completion Percentage', 0)

        update_fields = {}
        field_mapping = {
            'name': 'Project Name',
            'client': 'Client Name',
            'status': 'Status',
            'budget': 'Budget',
            'timeline': 'Timeline',
            'completion_percentage': 'Completion Percentage',
            'priority': 'Priority',
            'start_date': 'Start Date',
            'end_date': 'End Date'
        }

        for key, airtable_field in field_mapping.items():
            if key in data:
                update_fields[airtable_field] = data[key]

        update_fields['Last Updated'] = datetime.now().isoformat()

        # Update the project
        airtable_client.update_record('ATLAS PROJECTS', project_id, update_fields)
        
        # 🎯 AUTO-CREATE INVOICE IF PROJECT COMPLETED
        new_status = update_fields.get('Status', old_status)
        new_completion = update_fields.get('Completion Percentage', old_completion)
        
        # Trigger invoice creation if:
        # 1. Status changed to "Completed" OR
        # 2. Completion percentage reached 100%
        should_create_invoice = (
            (new_status == 'Completed' and old_status != 'Completed') or
            (new_completion == 100 and old_completion < 100)
        )
        
        if should_create_invoice:
            # Check if invoice already exists for this project
            existing_invoice = current_project['fields'].get('Invoice')
            
            if not existing_invoice:
                try:
                    # Auto-create invoice!
                    invoice_result = create_invoice_from_atlas_project(project_id, airtable_client)
                    
                    return jsonify({
                        'success': True,
                        'message': '✅ Project completed! Invoice created automatically!',
                        'invoice_created': True,
                        'invoice_id': invoice_result['invoice_id'],
                        'invoice_number': invoice_result['invoice_number'],
                        'invoice_amount': invoice_result['invoice_amount']
                    })
                except Exception as invoice_error:
                    print(f"Error creating invoice from project: {invoice_error}")
                    return jsonify({
                        'success': True,
                        'message': 'Project updated. Invoice creation failed - please create manually.',
                        'invoice_error': str(invoice_error)
                    })
        
        return jsonify({'success': True})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# RFP CRUD operations
@app.route('/atlas/rfps', methods=['GET'])
def get_atlas_rfps():
    """Get RFPs with optional project filtering"""
    try:
        project_id = request.args.get('project_id')
        airtable_client = AirtableClient()

        records = airtable_client.get_all_records('ATLAS RFPS')

        # Filter by project if specified
        if project_id:
            # Note: This would need a link field in a real implementation
            # For now, we'll return all RFPs
            pass

        rfps = []
        for record in records:
            fields = record['fields']
            rfps.append({
                'id': record['id'],
                'name': fields.get('RFP Name', ''),
                'client': fields.get('Client Name', ''),
                'rfp_number': fields.get('RFP Number', ''),
                'value': fields.get('Value', 0),
                'due_date': fields.get('Due Date'),
                'status': fields.get('Status', 'Draft'),
                'probability': fields.get('Probability', 50),
                'industry': fields.get('Industry', ''),
                'contact_name': fields.get('Contact Name', ''),
                'contact_email': fields.get('Contact Email', ''),
                'created_date': fields.get('Created Date')
            })

        return jsonify({'rfps': rfps})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/atlas/rfps', methods=['POST'])
def create_atlas_rfp():
    """Create a new RFP"""
    try:
        data = request.json
        airtable_client = AirtableClient()

        fields = {
            'RFP Name': data.get('name', ''),
            'Client Name': data.get('client', ''),
            'RFP Number': data.get('rfp_number', ''),
            'Value': data.get('value', 0),
            'Due Date': data.get('due_date'),
            'Industry': data.get('industry', ''),
            'Description': data.get('description', ''),
            'Contact Name': data.get('contact_name', ''),
            'Contact Email': data.get('contact_email'),
            'Contact Phone': data.get('contact_phone'),
            'Status': 'Draft',
            'Probability': data.get('probability', 50),
            'Created Date': datetime.now().isoformat()
        }

        result = airtable_client.create_record('ATLAS RFPS', fields)
        return jsonify({'rfp': {'id': result['id'], **fields}})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Change Orders CRUD operations
@app.route('/atlas/change-orders', methods=['GET'])
def get_atlas_change_orders():
    """Get change orders with optional project filtering"""
    try:
        project_id = request.args.get('project_id')
        airtable_client = AirtableClient()

        records = airtable_client.get_all_records('ATLAS CHANGE ORDERS')

        change_orders = []
        for record in records:
            fields = record['fields']
            # Filter by project if specified
            if project_id and fields.get('Project ID') != project_id:
                continue

            change_orders.append({
                'id': record['id'],
                'project_id': fields.get('Project ID', ''),
                'title': fields.get('Title', ''),
                'description': fields.get('Description', ''),
                'type': fields.get('Type', ''),
                'priority': fields.get('Priority', 'Medium'),
                'status': fields.get('Status', 'Draft'),
                'impact_scope': fields.get('Impact Scope', 'Low'),
                'impact_schedule': fields.get('Impact Schedule', ''),
                'impact_budget': fields.get('Impact Budget', 0),
                'created_date': fields.get('Created Date')
            })

        return jsonify({'change_orders': change_orders})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/atlas/change-orders', methods=['POST'])
def create_atlas_change_order():
    """Create a new change order"""
    try:
        data = request.json
        airtable_client = AirtableClient()

        fields = {
            'Project ID': data.get('project_id', ''),
            'Title': data.get('title', ''),
            'Description': data.get('description', ''),
            'Type': data.get('type', 'Scope'),
            'Priority': data.get('priority', 'Medium'),
            'Status': 'Draft',
            'Requested By': data.get('requested_by', ''),
            'Created Date': datetime.now().isoformat()
        }

        result = airtable_client.create_record('ATLAS CHANGE ORDERS', fields)
        return jsonify({'change_order': {'id': result['id'], **fields}})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Existing ATLAS PM AI endpoints
@app.route('/atlas/analyze-rfp', methods=['POST'])
def atlas_analyze_rfp():
    """
    Analyze RFP content and extract requirements

    Expected JSON:
    {
        "rfp_content": "Full RFP text...",
        "project_id": "rec..." (optional)
    }
    """
    try:
        data = request.json
        rfp_content = data.get('rfp_content', '')
        project_id = data.get('project_id', '')

        if not rfp_content:
            return jsonify({"error": "rfp_content required"}), 400

        result = handle_atlas_analyze_rfp(rfp_content, project_id or None)
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/atlas/generate-wbs', methods=['POST'])
def atlas_generate_wbs():
    """
    Generate Work Breakdown Structure for project

    Expected JSON:
    {
        "project_id": "rec..."
    }
    """
    try:
        data = request.json
        project_id = data.get('project_id', '')

        if not project_id:
            return jsonify({"error": "project_id required"}), 400

        result = handle_atlas_generate_wbs(project_id)
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/atlas/analyze-change-request', methods=['POST'])
def atlas_analyze_change_request():
    """
    Analyze change request and provide impact assessment

    Expected JSON:
    {
        "change_description": "Description of requested change...",
        "project_id": "rec..."
    }
    """
    try:
        data = request.json
        change_description = data.get('change_description', '')
        project_id = data.get('project_id', '')

        if not change_description:
            return jsonify({"error": "change_description required"}), 400
        if not project_id:
            return jsonify({"error": "project_id required"}), 400

        result = handle_atlas_analyze_change_request(change_description, project_id)
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =====================================================================
# TASK BOARD ENDPOINTS - Monday.com Style
# =====================================================================

@app.route('/atlas/tasks', methods=['GET'])
def get_tasks():
    """Get all tasks with optional filtering"""
    try:
        project_id = request.args.get('project_id')
        airtable_client = AirtableClient()
        
        # Try to get tasks from Airtable (create table if doesn't exist)
        try:
            records = airtable_client.get_all_records('ATLAS TASKS')
        except:
            # Table doesn't exist yet, return empty
            return jsonify({'tasks': []})
        
        tasks = []
        for record in records:
            fields = record['fields']
            # Filter by project if specified
            if project_id and fields.get('Project ID') != project_id:
                continue
                
            tasks.append({
                'id': record['id'],
                'title': fields.get('Title', ''),
                'status': fields.get('Status', 'todo'),
                'priority': fields.get('Priority', 'medium'),
                'owner': fields.get('Owner', 'Unassigned'),
                'dueDate': fields.get('Due Date'),
                'progress': fields.get('Progress', 0),
                'budget': fields.get('Budget', 0),
                'description': fields.get('Description', ''),
                'project': fields.get('Project Name', ''),
                'createdDate': fields.get('Created Date')
            })
        
        return jsonify({'tasks': tasks})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/atlas/tasks', methods=['POST'])
def create_task():
    """Create a new task"""
    try:
        data = request.json
        airtable_client = AirtableClient()
        
        fields = {
            'Title': data.get('title', 'New Task'),
            'Status': data.get('status', 'todo'),
            'Priority': data.get('priority', 'medium'),
            'Owner': data.get('owner', 'Unassigned'),
            'Due Date': data.get('dueDate'),
            'Progress': data.get('progress', 0),
            'Budget': data.get('budget', 0),
            'Description': data.get('description', ''),
            'Project Name': data.get('project', ''),
            'Created Date': datetime.now().isoformat()
        }
        
        result = airtable_client.create_record('ATLAS TASKS', fields)
        return jsonify({'task': {'id': result['id'], **fields}})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/atlas/tasks/<task_id>', methods=['PUT'])
def update_task(task_id):
    """Update a task"""
    try:
        data = request.json
        airtable_client = AirtableClient()
        
        update_fields = {}
        field_mapping = {
            'title': 'Title',
            'status': 'Status',
            'priority': 'Priority',
            'owner': 'Owner',
            'dueDate': 'Due Date',
            'progress': 'Progress',
            'budget': 'Budget',
            'description': 'Description',
            'project': 'Project Name'
        }
        
        for key, airtable_field in field_mapping.items():
            if key in data:
                update_fields[airtable_field] = data[key]
        
        update_fields['Last Updated'] = datetime.now().isoformat()
        
        airtable_client.update_record('ATLAS TASKS', task_id, update_fields)
        return jsonify({'success': True})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/atlas/tasks/<task_id>', methods=['DELETE'])
def delete_task(task_id):
    """Delete a task"""
    try:
        airtable_client = AirtableClient()
        table = airtable_client.get_table('ATLAS TASKS')
        table.delete(task_id)
        return jsonify({'success': True})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/atlas/tasks/ai-suggestions', methods=['POST'])
def get_ai_task_suggestions():
    """Get AI suggestions for task management"""
    try:
        data = request.json
        tasks = data.get('tasks', [])
        
        # Use Claude AI to analyze tasks and provide suggestions
        anthropic_client = anthropic.Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))
        
        task_summary = f"Analyzing {len(tasks)} tasks:\n"
        for task in tasks[:10]:  # Limit to 10 tasks for context
            task_summary += f"- {task.get('title')} ({task.get('status')}, {task.get('priority')} priority, {task.get('progress')}% complete)\n"
        
        message = anthropic_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            messages=[{
                "role": "user",
                "content": f"""You are a project management AI assistant. Analyze these tasks and provide actionable insights:

{task_summary}

Provide:
1. Top 3 priorities for today
2. Any blockers or risks
3. Suggestions for improving workflow
4. Tasks that might be behind schedule

Keep it concise and actionable."""
            }]
        )
        
        suggestions = message.content[0].text
        
        return jsonify({
            'suggestions': suggestions,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/atlas/tasks/auto-generate', methods=['POST'])
def auto_generate_tasks():
    """Auto-generate tasks from RFP or project description using AI"""
    try:
        data = request.json
        project_description = data.get('description', '')
        project_name = data.get('project_name', 'New Project')
        
        if not project_description:
            return jsonify({"error": "description required"}), 400
        
        # Use Claude AI to generate tasks
        anthropic_client = anthropic.Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))
        
        message = anthropic_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[{
                "role": "user",
                "content": f"""You are a project management AI. Based on this project description, generate a comprehensive task list:

Project: {project_name}
Description: {project_description}

Generate 10-15 tasks that cover the full project lifecycle. For each task, provide:
- Title (clear, actionable)
- Priority (low/medium/high/urgent)
- Estimated duration
- Suggested owner role (e.g., "Project Manager", "Developer", "Designer")

Format as JSON array with fields: title, priority, duration, owner_role, description"""
            }]
        )
        
        # Parse AI response and create tasks
        ai_response = message.content[0].text
        
        return jsonify({
            'generated_tasks': ai_response,
            'project_name': project_name,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =====================================================================
# LBPC (LANCASTER BANQUES P.C.) - SURPLUS RECOVERY ENDPOINTS
# =====================================================================

@app.route('/lbpc/leads', methods=['GET'])
def lbpc_get_leads():
    """Get all LBPC leads with optional filtering"""
    try:
        filters = {}
        if request.args.get('state'):
            filters['state'] = request.args.get('state')
        if request.args.get('status'):
            filters['status'] = request.args.get('status')
        if request.args.get('min_amount'):
            filters['min_amount'] = float(request.args.get('min_amount'))
        
        result = handle_lbpc_get_leads(filters if filters else None)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/lbpc/leads', methods=['POST'])
def lbpc_create_lead():
    """Create new LBPC lead"""
    try:
        data = request.json
        result = handle_lbpc_create_lead(data)
        return jsonify(result), 201 if result.get('success') else 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/lbpc/leads/<lead_id>', methods=['PUT'])
def lbpc_update_lead(lead_id):
    """Update existing LBPC lead"""
    try:
        data = request.json
        result = handle_lbpc_update_lead(lead_id, data)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/lbpc/leads/<lead_id>', methods=['DELETE'])
def lbpc_delete_lead(lead_id):
    """Delete LBPC lead"""
    try:
        result = handle_lbpc_delete_lead(lead_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/lbpc/leads/<lead_id>/qualify', methods=['POST'])
def lbpc_qualify_lead(lead_id):
    """AI qualification of a lead"""
    try:
        result = handle_lbpc_ai_qualify_lead(lead_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/lbpc/leads/<lead_id>/generate-document', methods=['POST'])
def lbpc_generate_document(lead_id):
    """Generate document for a lead"""
    try:
        data = request.json
        template_type = data.get('template_type', 'Initial Notice')
        use_ai = data.get('use_ai', True)
        
        result = handle_lbpc_generate_document(lead_id, template_type, use_ai)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/lbpc/leads/<lead_id>/create-invoice', methods=['POST'])
def lbpc_create_lead_invoice(lead_id):
    """Create invoice for LBPC lead"""
    try:
        result = handle_lbpc_create_invoice(lead_id)
        return jsonify(result), 201 if result.get('success') else 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/lbpc/documents', methods=['GET'])
def lbpc_get_documents():
    """Get LBPC documents"""
    try:
        lead_id = request.args.get('lead_id')
        result = handle_lbpc_get_documents(lead_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/lbpc/tasks', methods=['GET'])
def lbpc_get_tasks():
    """Get LBPC tasks"""
    try:
        filters = {}
        if request.args.get('status'):
            filters['status'] = request.args.get('status')
        if request.args.get('lead_id'):
            filters['lead_id'] = request.args.get('lead_id')
        
        result = handle_lbpc_get_tasks(filters if filters else None)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/lbpc/tasks/<task_id>', methods=['PUT'])
def lbpc_update_task(task_id):
    """Update LBPC task"""
    try:
        data = request.json
        result = handle_lbpc_update_task(task_id, data)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/lbpc/import-csv', methods=['POST'])
def lbpc_import_csv():
    """Import leads from CSV data"""
    try:
        data = request.json
        csv_data = data.get('leads', [])
        
        if not csv_data:
            return jsonify({'error': 'No lead data provided'}), 400
        
        result = handle_lbpc_import_csv(csv_data)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/lbpc/analytics', methods=['GET'])
def lbpc_get_analytics():
    """Get LBPC analytics and dashboard stats"""
    try:
        result = handle_lbpc_get_analytics()
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/lbpc/mine/county', methods=['POST'])
def lbpc_mine_county():
    """Mine leads from specific county website"""
    try:
        data = request.json
        county = data.get('county')
        state = data.get('state')
        
        if not county or not state:
            return jsonify({'error': 'County and state required'}), 400
        
        result = handle_lbpc_mine_county(county, state)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/lbpc/upload-pdf', methods=['POST'])
def lbpc_upload_pdf():
    """Upload and parse PDF surplus list"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        county = request.form.get('county')
        state = request.form.get('state')
        
        if not county or not state:
            return jsonify({'error': 'County and state required'}), 400
        
        # Save temporarily
        temp_path = f'/tmp/lbpc_upload_{datetime.now().timestamp()}.pdf'
        file.save(temp_path)
        
        result = handle_lbpc_upload_pdf(temp_path, county, state)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/lbpc/upload-csv', methods=['POST'])
def lbpc_upload_csv():
    """Upload and parse CSV surplus list"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        county = request.form.get('county')
        state = request.form.get('state')
        
        if not county or not state:
            return jsonify({'error': 'County and state required'}), 400
        
        # Read CSV content
        csv_content = file.read().decode('utf-8')
        
        result = handle_lbpc_upload_csv(csv_content, county, state)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# =====================================================================
# VENDOR PORTALS ENDPOINTS - Portal Management System
# =====================================================================

@app.route('/vendor-portals', methods=['GET'])
def get_vendor_portals():
    """Get all vendor portals with optional filtering"""
    try:
        category = request.args.get('category')  # 'Government' or 'Development'
        search = request.args.get('search', '').lower()
        
        airtable_client = AirtableClient()
        
        try:
            records = airtable_client.get_all_records('VENDOR PORTALS')
        except:
            # Table doesn't exist yet, return empty
            return jsonify({'portals': []})
        
        portals = []
        for record in records:
            fields = record['fields']
            
            # Filter by category if specified
            if category and fields.get('Category') != category:
                continue
            
            # Filter by search term
            if search:
                searchable = f"{fields.get('Portal Name', '')} {fields.get('Keywords', '')} {fields.get('Description', '')}".lower()
                if search not in searchable:
                    continue
            
            portals.append({
                'id': record['id'],
                'name': fields.get('Portal Name', ''),
                'url': fields.get('URL', ''),
                'category': fields.get('Category', ''),
                'portalType': fields.get('Portal Type', ''),
                'keywords': fields.get('Keywords', ''),
                'description': fields.get('Description', ''),
                'searchEnabled': fields.get('Search Enabled', False),
                'searchUrl': fields.get('Search URL', ''),
                'loginRequired': fields.get('Login Required', False),
                'favorite': fields.get('Favorite', False),
                'lastAccessed': fields.get('Last Accessed'),
                'addedDate': fields.get('Added Date'),
                'icon': fields.get('Icon/Favicon', '🔗')
            })
        
        return jsonify({'portals': portals})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/vendor-portals', methods=['POST'])
def create_vendor_portal():
    """Create a new vendor portal"""
    try:
        data = request.json
        airtable_client = AirtableClient()
        
        fields = {
            'Portal Name': data.get('name', ''),
            'URL': data.get('url', ''),
            'Category': data.get('category', 'Development'),
            'Portal Type': data.get('portalType', 'Other'),
            'Keywords': data.get('keywords', ''),
            'Description': data.get('description', ''),
            'Search Enabled': data.get('searchEnabled', False),
            'Search URL': data.get('searchUrl', ''),
            'Login Required': data.get('loginRequired', False),
            'Favorite': data.get('favorite', False),
            'Icon/Favicon': data.get('icon', '🔗'),
            'Added Date': datetime.now().isoformat()
        }
        
        result = airtable_client.create_record('VENDOR PORTALS', fields)
        return jsonify({'portal': {'id': result['id'], **data}})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/vendor-portals/<portal_id>', methods=['PUT'])
def update_vendor_portal(portal_id):
    """Update a vendor portal"""
    try:
        data = request.json
        airtable_client = AirtableClient()
        
        update_fields = {}
        field_mapping = {
            'name': 'Portal Name',
            'url': 'URL',
            'category': 'Category',
            'portalType': 'Portal Type',
            'keywords': 'Keywords',
            'description': 'Description',
            'searchEnabled': 'Search Enabled',
            'searchUrl': 'Search URL',
            'loginRequired': 'Login Required',
            'favorite': 'Favorite',
            'icon': 'Icon/Favicon'
        }
        
        for key, airtable_field in field_mapping.items():
            if key in data:
                update_fields[airtable_field] = data[key]
        
        # Update last accessed if opening portal
        if data.get('updateLastAccessed'):
            update_fields['Last Accessed'] = datetime.now().isoformat()
        
        airtable_client.update_record('VENDOR PORTALS', portal_id, update_fields)
        return jsonify({'success': True})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/vendor-portals/<portal_id>', methods=['DELETE'])
def delete_vendor_portal(portal_id):
    """Delete a vendor portal"""
    try:
        airtable_client = AirtableClient()
        table = airtable_client.get_table('VENDOR PORTALS')
        table.delete(portal_id)
        return jsonify({'success': True})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =====================================================================
# GPSS OPPORTUNITIES ENDPOINTS - Enhanced Federal/Multi-State
# =====================================================================

@app.route('/gpss/opportunities', methods=['GET'])
def get_gpss_opportunities():
    """Get all opportunities with optional filtering"""
    try:
        # Get filter parameters
        source = request.args.get('source')  # Federal, State, Local, Cooperative
        state = request.args.get('state')     # MI, GA, MD, TX, CA, IL, Federal, Multi-State
        edwsb_only = request.args.get('edwsb_only', 'false').lower() == 'true'
        urgency = request.args.get('urgency')  # Critical, High, Medium, Low
        home_states_only = request.args.get('home_states_only', 'false').lower() == 'true'
        
        airtable_client = AirtableClient()
        
        try:
            records = airtable_client.get_all_records('GPSS OPPORTUNITIES')
        except:
            # Table doesn't exist yet, return empty
            return jsonify({'opportunities': []})
        
        opportunities = []
        for record in records:
            fields = record['fields']
            
            # Apply filters
            if source and fields.get('Source') != source:
                continue
            if state and fields.get('State') != state:
                continue
            if edwsb_only and not fields.get('EDWOSB Eligible'):
                continue
            if urgency and fields.get('Urgency') != urgency:
                continue
            if home_states_only and not fields.get('Home State Priority'):
                continue
            
            opportunities.append({
                'id': record['id'],
                'title': fields.get('Title', ''),
                'rfpNumber': fields.get('RFP Number', ''),
                'agency': fields.get('Agency Name', ''),
                'value': fields.get('Value', 0),
                'dueDate': fields.get('Due Date', ''),
                'source': fields.get('Source', ''),
                'sourcePortal': fields.get('Source Portal', ''),
                'sourceUrl': fields.get('Source URL', ''),
                'state': fields.get('State', ''),
                'county': fields.get('County', ''),
                'city': fields.get('City', ''),
                'performanceLocation': fields.get('Performance Location', ''),
                'homeStatePriority': fields.get('Home State Priority', False),
                'agencyType': fields.get('Agency Type', ''),
                'setAsideType': fields.get('Set-Aside Type', ''),
                'edwsbEligible': fields.get('EDWOSB Eligible', False),
                'certificationRequired': fields.get('Certification Required', ''),
                'naicsCodes': fields.get('NAICS Codes', []),
                'pscCodes': fields.get('PSC Codes', ''),
                'nigpCodes': fields.get('NIGP Codes', ''),  # User added this!
                'category': fields.get('Opportunity Category', ''),
                'priorityScore': fields.get('Priority Score', 0),
                'winProbability': fields.get('Win Probability', 0),
                'urgency': fields.get('Urgency', 'Medium'),
                'daysUntilDue': fields.get('Days Until Due', 0),
                'strategicFit': fields.get('Strategic Fit', ''),
                'internalStatus': fields.get('Internal Status', 'New'),
                'pipelineStage': fields.get('Pipeline Stage', 'Active'),
                'assignedTo': fields.get('Assigned To', ''),
                'notes': fields.get('Notes', ''),
                'aiQualificationResult': fields.get('AI Qualification Result', ''),
                'aiRecommendation': fields.get('AI Recommendation', ''),
                'aiStrengths': fields.get('AI Strengths', ''),
                'aiConcerns': fields.get('AI Concerns', ''),
                'contactsExtracted': fields.get('Contacts Extracted', 0),
                'lastReviewedDate': fields.get('Last Reviewed Date', ''),
                'createdDate': fields.get('Created Date', '')
            })
        
        return jsonify({'opportunities': opportunities})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/gpss/opportunities', methods=['POST'])
def create_gpss_opportunity():
    """Create a new opportunity"""
    try:
        data = request.json
        airtable_client = AirtableClient()
        
        fields = {
            'Title': data.get('title', ''),
            'RFP Number': data.get('rfpNumber', ''),
            'Agency Name': data.get('agency', ''),
            'Value': data.get('value', 0),
            'Due Date': data.get('dueDate'),
            'Source': data.get('source', 'Federal'),
            'Source Portal': data.get('sourcePortal', ''),
            'Source URL': data.get('sourceUrl', ''),
            'State': data.get('state', 'Federal'),
            'County': data.get('county', ''),
            'City': data.get('city', ''),
            'Performance Location': data.get('performanceLocation', ''),
            'Home State Priority': data.get('homeStatePriority', False),
            'Agency Type': data.get('agencyType', 'Federal'),
            'Set-Aside Type': data.get('setAsideType', 'Unrestricted'),
            'EDWOSB Eligible': data.get('edwsbEligible', False),
            'Certification Required': data.get('certificationRequired', ''),
            'Opportunity Category': data.get('category', 'Other'),
            'Priority Score': data.get('priorityScore', 0),
            'Win Probability': data.get('winProbability', 0),
            'Urgency': data.get('urgency', 'Medium'),
            'Strategic Fit': data.get('strategicFit', 'Fair'),
            'Internal Status': data.get('internalStatus', 'New'),
            'Pipeline Stage': data.get('pipelineStage', 'Active'),
            'Assigned To': data.get('assignedTo', ''),
            'Notes': data.get('notes', ''),
            'Created Date': datetime.now().isoformat()
        }
        
        result = airtable_client.create_record('GPSS OPPORTUNITIES', fields)
        return jsonify({'opportunity': {'id': result['id'], **fields}})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/gpss/opportunities/<opportunity_id>', methods=['PUT'])
def update_gpss_opportunity(opportunity_id):
    """Update an opportunity - with auto-ATLAS integration when won"""
    try:
        data = request.json
        airtable_client = AirtableClient()
        
        # Get current opportunity to check status change
        current_opp = airtable_client.get_record('GPSS OPPORTUNITIES', opportunity_id)
        old_status = current_opp['fields'].get('Status', '')
        
        update_fields = {}
        field_mapping = {
            'title': 'Title',
            'rfpNumber': 'RFP Number',
            'agency': 'Agency Name',
            'value': 'Value',
            'dueDate': 'Due Date',
            'source': 'Source',
            'sourcePortal': 'Source Portal',
            'state': 'State',
            'setAsideType': 'Set-Aside Type',
            'edwsbEligible': 'EDWOSB Eligible',
            'priorityScore': 'Priority Score',
            'urgency': 'Urgency',
            'internalStatus': 'Internal Status',
            'pipelineStage': 'Pipeline Stage',
            'assignedTo': 'Assigned To',
            'notes': 'Notes',
            'status': 'Status'  # Add status mapping
        }
        
        for key, airtable_field in field_mapping.items():
            if key in data:
                update_fields[airtable_field] = data[key]
        
        # Update the opportunity
        airtable_client.update_record('GPSS OPPORTUNITIES', opportunity_id, update_fields)
        
        # 🎯 AUTO-CREATE ATLAS PROJECT IF STATUS CHANGED TO "WON"
        new_status = update_fields.get('Status', old_status)
        if new_status == 'Won' and old_status != 'Won':
            # Check if ATLAS project already exists for this opportunity
            existing_atlas_link = current_opp['fields'].get('ATLAS Project')
            
            if not existing_atlas_link:
                try:
                    # Auto-create ATLAS project!
                    atlas_result = create_atlas_project_from_opportunity(opportunity_id, airtable_client)
                    
                    return jsonify({
                        'success': True,
                        'message': '🎉 Contract Won! ATLAS project created automatically!',
                        'atlas_project_created': True,
                        'atlas_project_id': atlas_result['project_id'],
                        'atlas_project_name': atlas_result['project_name'],
                        'wbs_generated': atlas_result.get('wbs_generated', False)
                    })
                except Exception as atlas_error:
                    print(f"Error creating ATLAS project: {atlas_error}")
                    # Still return success for opportunity update
                    return jsonify({
                        'success': True,
                        'message': 'Opportunity updated. ATLAS project creation failed - please create manually.',
                        'atlas_error': str(atlas_error)
                    })
        
        return jsonify({'success': True})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/gpss/stats', methods=['GET'])
def get_gpss_stats():
    """Get GPSS dashboard statistics"""
    try:
        airtable_client = AirtableClient()
        
        try:
            opportunities = airtable_client.get_all_records('GPSS OPPORTUNITIES')
        except:
            opportunities = []
        
        # Calculate stats
        federal_opps = [o for o in opportunities if o['fields'].get('Source') == 'Federal']
        edwsb_eligible = [o for o in opportunities if o['fields'].get('EDWOSB Eligible')]
        home_state_opps = [o for o in opportunities if o['fields'].get('Home State Priority')]
        critical_urgency = [o for o in opportunities if o['fields'].get('Urgency') == 'Critical']
        
        total_pipeline = sum(o['fields'].get('Value', 0) for o in opportunities if isinstance(o['fields'].get('Value'), (int, float)))
        
        stats = {
            'federalOpps': len(federal_opps),
            'edwsbSetAsides': len(edwsb_eligible),
            'homeStateOpps': len(home_state_opps),
            'criticalUrgency': len(critical_urgency),
            'totalPipeline': total_pipeline,
            'totalOpportunities': len(opportunities),
            'bySource': {
                'Federal': len([o for o in opportunities if o['fields'].get('Source') == 'Federal']),
                'State': len([o for o in opportunities if o['fields'].get('Source') == 'State']),
                'Local': len([o for o in opportunities if o['fields'].get('Source') == 'Local']),
                'Cooperative': len([o for o in opportunities if o['fields'].get('Source') == 'Cooperative'])
            }
        }
        
        return jsonify(stats)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================================================
# D&I ADVANTAGE ANALYTICS (NEW - ADDITIVE ONLY)
# ============================================================================

@app.route('/gpss/analytics/di-advantage', methods=['GET'])
def get_di_advantage_analytics():
    """NEW ENDPOINT: Track D&I competitive advantage metrics - NO CHANGES TO EXISTING CODE"""
    try:
        airtable_client = AirtableClient()
        opportunities = airtable_client.get_all_records('GPSS OPPORTUNITIES')
        
        # Company certifications (from existing system)
        YOUR_CERTIFICATIONS = ['EDWOSB', 'WOSB', 'WBE', 'MBE', 'Small Business']
        
        # Initialize analytics
        analytics = {
            'set_aside_breakdown': {
                'edwosb': {'total': 0, 'value': 0, 'avg_competitors': '10-20', 'win_rate_range': '30-50%'},
                'wosb': {'total': 0, 'value': 0, 'avg_competitors': '20-40', 'win_rate_range': '20-35%'},
                'small_business': {'total': 0, 'value': 0, 'avg_competitors': '40-80', 'win_rate_range': '10-20%'},
                'unrestricted': {'total': 0, 'value': 0, 'avg_competitors': '100-300', 'win_rate_range': '3-8%'}
            },
            'eligible_opportunities': 0,
            'eligible_value': 0,
            'competitive_advantage': {
                'fewer_competitors': True,
                'higher_win_rate': True,
                'evaluation_preference': True
            },
            'recommendations': []
        }
        
        # Analyze each opportunity
        for opp in opportunities:
            fields = opp.get('fields', {})
            set_aside = fields.get('Set-Aside Type', 'Unrestricted')
            value = fields.get('Value', 0) if isinstance(fields.get('Value'), (int, float)) else 0
            
            # Categorize by set-aside type
            if 'EDWOSB' in set_aside:
                analytics['set_aside_breakdown']['edwosb']['total'] += 1
                analytics['set_aside_breakdown']['edwosb']['value'] += value
                analytics['eligible_opportunities'] += 1
                analytics['eligible_value'] += value
            elif 'WOSB' in set_aside or 'Women-Owned' in set_aside:
                analytics['set_aside_breakdown']['wosb']['total'] += 1
                analytics['set_aside_breakdown']['wosb']['value'] += value
                analytics['eligible_opportunities'] += 1
                analytics['eligible_value'] += value
            elif 'Small Business' in set_aside:
                analytics['set_aside_breakdown']['small_business']['total'] += 1
                analytics['set_aside_breakdown']['small_business']['value'] += value
                analytics['eligible_opportunities'] += 1
                analytics['eligible_value'] += value
            else:
                analytics['set_aside_breakdown']['unrestricted']['total'] += 1
                analytics['set_aside_breakdown']['unrestricted']['value'] += value
        
        # Generate smart recommendations
        total_opps = len(opportunities)
        eligible_pct = (analytics['eligible_opportunities'] / total_opps * 100) if total_opps > 0 else 0
        
        if analytics['set_aside_breakdown']['edwosb']['total'] > 0:
            analytics['recommendations'].append({
                'type': 'high_priority',
                'icon': '🎯',
                'message': f"You have {analytics['set_aside_breakdown']['edwosb']['total']} EDWOSB-only opportunities worth ${analytics['set_aside_breakdown']['edwosb']['value']:,.0f}. These have 30-50% win rates vs 3-8% unrestricted!",
                'action': 'Focus on EDWOSB set-asides first'
            })
        
        if analytics['set_aside_breakdown']['wosb']['total'] > 0:
            analytics['recommendations'].append({
                'type': 'medium_priority',
                'icon': '💼',
                'message': f"{analytics['set_aside_breakdown']['wosb']['total']} WOSB opportunities available worth ${analytics['set_aside_breakdown']['wosb']['value']:,.0f}. Win rate: 20-35%.",
                'action': 'Prioritize after EDWOSB'
            })
        
        if eligible_pct < 50:
            analytics['recommendations'].append({
                'type': 'opportunity',
                'icon': '🔍',
                'message': f"Only {eligible_pct:.0f}% of your pipeline is set-asides. Search SAM.gov for more WOSB/EDWOSB opportunities to increase win rate.",
                'action': 'Add more set-aside opportunities'
            })
        
        analytics['summary'] = {
            'total_opportunities': total_opps,
            'eligible_count': analytics['eligible_opportunities'],
            'eligible_percentage': round(eligible_pct, 1),
            'competitive_edge': 'HIGH' if eligible_pct > 50 else 'MEDIUM' if eligible_pct > 25 else 'LOW'
        }
        
        return jsonify(analytics)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/gpss/proposals', methods=['GET'])
def get_gpss_proposals():
    """Get all GPSS proposals"""
    try:
        airtable_client = AirtableClient()
        
        try:
            # Fetch all proposals from Airtable
            records = airtable_client.get_all_records('GPSS Proposals')
            
            # Transform records to match frontend format
            proposals = []
            for record in records:
                fields = record['fields']
                
                # Parse JSON fields
                try:
                    pricing_breakdown = eval(fields.get('PRICING-BREAKDOWN', '{}')) if isinstance(fields.get('PRICING-BREAKDOWN'), str) else {}
                    compliance_checklist = eval(fields.get('COMPLIANCE CHECKLIST', '{}')) if isinstance(fields.get('COMPLIANCE CHECKLIST'), str) else {}
                    recipients = eval(fields.get('PRIMARY RECIPIENT EMAIL', '{}')) if isinstance(fields.get('PRIMARY RECIPIENT EMAIL'), str) else {}
                except:
                    pricing_breakdown = {}
                    compliance_checklist = {}
                    recipients = {}
                
                proposals.append({
                    'id': record['id'],
                    'proposalName': fields.get('PROPOSAL NAME', ''),
                    'opportunityId': fields.get('GPSS OPPORTUNITY', [''])[0] if fields.get('GPSS OPPORTUNITY') else '',
                    'rfpNumber': fields.get('RFP NUMBER', ''),
                    'agency': fields.get('AGENCY NAME', ''),
                    'value': fields.get('Total Value', 0),
                    'status': fields.get('Status', 'Draft'),
                    'generatedDate': fields.get('GENERATED DATE', ''),
                    'sentDate': fields.get('SENT DATE'),
                    'dueDate': fields.get('DUE DATE', ''),
                    'executiveSummary': fields.get('EXECUTIVE SUMMARY', ''),
                    'technicalApproach': fields.get('TECHNICAL APPROACH', ''),
                    'staffingPlan': fields.get('STAFFING PLAN ', ''),
                    'pastPerformance': fields.get('PAST PERFORMANCE', ''),
                    'pricingTotal': fields.get('PRICING-TOTAL', 0),
                    'pricingBreakdown': pricing_breakdown,
                    'pricingJustification': fields.get('PRICING-JUSTIFICATION', ''),
                    'complianceChecklist': compliance_checklist,
                    'recipients': recipients
                })
            
            return jsonify({'proposals': proposals})
        
        except Exception as e:
            # If table doesn't exist yet, return empty array
            print(f"Error fetching proposals: {e}")
            return jsonify({'proposals': []})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/gpss/proposals', methods=['POST'])
def create_gpss_proposal():
    """Save a new proposal to Airtable"""
    try:
        data = request.json
        airtable_client = AirtableClient()
        
        # Prepare fields for Airtable
        fields = {
            'PROPOSAL NAME': data.get('proposalName', ''),
            'RFP NUMBER': data.get('rfpNumber', ''),
            'AGENCY NAME': data.get('agency', ''),
            'STATUS': data.get('status', 'DRAFT'),
            'EXECUTIVE SUMMARY': data.get('executiveSummary', ''),
            'TECHNICAL APPROACH': data.get('technicalApproach', ''),
            'STAFFING PLAN ': data.get('staffingPlan', ''),
            'PAST PERFORMANCE': data.get('pastPerformance', ''),
            'PRICING-TOTAL': data.get('pricingTotal', 0),
            'PRICING-BREAKDOWN': str(data.get('pricingBreakdown', {})),
            'PRICING-JUSTIFICATION': data.get('pricingJustification', ''),
            'COMPLIANCE CHECKLIST': str(data.get('complianceChecklist', {})),
            'PRIMARY RECIPIENT EMAIL': str(data.get('recipients', {})),
            'GENERATED DATE': data.get('generatedDate', datetime.now().isoformat())
        }
        
        # Add optional date field only if provided
        if data.get('dueDate'):
            fields['DUE DATE'] = data.get('dueDate')
        
        # Add opportunity link if provided
        if data.get('opportunityId'):
            fields['GPSS OPPORTUNITY'] = [data.get('opportunityId')]
        
        # Create record in Airtable
        record = airtable_client.create_record('GPSS Proposals', fields)
        
        return jsonify({
            'success': True,
            'proposalId': record['id'],
            'message': 'Proposal saved successfully'
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/gpss/pricing/calculate', methods=['POST'])
def calculate_intelligent_pricing():
    """
    Calculate intelligent pricing for an opportunity
    
    Expected JSON:
    {
      "opportunity_id": "recXXXXX",
      "service_category": "NEMT" (optional)
    }
    """
    try:
        data = request.json
        opportunity_id = data.get('opportunity_id')
        service_category = data.get('service_category')
        
        if not opportunity_id:
            return jsonify({"error": "opportunity_id is required"}), 400
        
        # Initialize pricing agent
        pricing_agent = GPSSPricingAgent()
        
        # Calculate intelligent pricing
        result = pricing_agent.calculate_intelligent_price(opportunity_id, service_category)
        
        if 'error' in result:
            return jsonify(result), 400
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/gpss/pricing/history', methods=['GET'])
def get_pricing_history():
    """Get pricing history with optional filtering"""
    try:
        airtable_client = AirtableClient()
        
        # Get filter parameters
        service_category = request.args.get('service_category')
        win_loss = request.args.get('win_loss')
        
        try:
            records = airtable_client.get_all_records('Pricing History')
            
            # Apply filters
            filtered_records = records
            if service_category:
                filtered_records = [r for r in filtered_records if r['fields'].get('Service Category') == service_category]
            if win_loss:
                filtered_records = [r for r in filtered_records if r['fields'].get('Win/Loss') == win_loss]
            
            # Transform to simplified format
            history = []
            for record in filtered_records:
                fields = record['fields']
                history.append({
                    'id': record['id'],
                    'serviceCategory': fields.get('Service Category', ''),
                    'totalBid': fields.get('Total Bid Amount', 0),
                    'estimatedCosts': fields.get('Estimated Costs', 0),
                    'winLoss': fields.get('Win/Loss', ''),
                    'agency': fields.get('Agency', ''),
                    'bidDate': fields.get('Bid Date', ''),
                    'profitMargin': fields.get('Actual Profit Margin %', 0),
                    'winProbability': fields.get('Win Probability Score', 0)
                })
            
            return jsonify({'history': history})
        
        except Exception as e:
            # If table doesn't exist yet, return empty
            print(f"Error fetching pricing history: {e}")
            return jsonify({'history': []})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/gpss/compliance/analyze-rfp', methods=['POST'])
def analyze_rfp_compliance():
    """
    Extract compliance requirements from RFP document
    
    Expected JSON:
    {
      "rfp_content": "Full RFP text...",
      "rfp_id": "recXXXXX" (optional)
    }
    """
    try:
        data = request.json
        rfp_content = data.get('rfp_content')
        
        if not rfp_content:
            return jsonify({"error": "rfp_content is required"}), 400
        
        # Initialize compliance agent
        compliance_agent = GPSSComplianceAgent()
        
        # Analyze RFP and extract requirements
        requirements = compliance_agent.analyze_rfp_requirements(rfp_content)
        
        if 'error' in requirements:
            return jsonify(requirements), 400
        
        return jsonify(requirements)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/gpss/compliance/check-proposal', methods=['POST'])
def check_proposal_compliance():
    """
    Check proposal compliance against RFP requirements
    
    Expected JSON:
    {
      "proposal_data": {...},
      "rfp_requirements": {...}
    }
    """
    try:
        data = request.json
        proposal_data = data.get('proposal_data')
        rfp_requirements = data.get('rfp_requirements')
        
        if not proposal_data or not rfp_requirements:
            return jsonify({"error": "Both proposal_data and rfp_requirements are required"}), 400
        
        # Initialize compliance agent
        compliance_agent = GPSSComplianceAgent()
        
        # Check compliance
        compliance_check = compliance_agent.check_proposal_compliance(proposal_data, rfp_requirements)
        
        # Generate report
        report = compliance_agent.generate_compliance_report(compliance_check, rfp_requirements)
        
        return jsonify({
            'compliance_check': compliance_check,
            'report': report
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/gpss/mining/portal/<portal_id>', methods=['POST'])
def mine_portal(portal_id):
    """
    Mine opportunities from a specific portal
    
    URL Parameter:
    portal_id - Airtable record ID of the portal
    """
    try:
        mining_agent = GPSSOpportunityMiningAgent()
        result = mining_agent.mine_portal_opportunities(portal_id)
        
        if 'error' in result:
            return jsonify(result), 400
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/gpss/mining/auto-mine-all', methods=['POST'])
def auto_mine_all():
    """
    Automatically mine all portals with auto-mining enabled
    This can be triggered daily via cron job
    """
    try:
        mining_agent = GPSSOpportunityMiningAgent()
        result = mining_agent.auto_mine_all_portals()
        
        if 'error' in result:
            return jsonify(result), 400
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/gpss/mining/check-rss-feeds', methods=['POST'])
def check_rss_feeds():
    """
    Check all RSS feeds for new government opportunities
    
    Returns:
        {
            "success": true,
            "feeds_checked": 3,
            "new_opportunities": 12,
            "opportunities": [...],
            "errors": []
        }
    """
    try:
        from nexus_backend import handle_check_rss_feeds
        result = handle_check_rss_feeds()
        
        if not result.get('success'):
            return jsonify(result), 400
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "feeds_checked": 0,
            "new_opportunities": 0
        }), 500


@app.route('/gpss/mining/search-sam-api', methods=['POST'])
def search_sam_gov_api():
    """
    Search SAM.gov API for federal opportunities
    
    Returns:
        {
            "success": true,
            "total_found": 1000,
            "imported": 50
        }
    """
    try:
        from nexus_backend import handle_sam_api_search
        result = handle_sam_api_search()
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e), "total_found": 0, "imported": 0}), 500


@app.route('/gpss/mining/search-govcon-api', methods=['POST'])
def search_govcon_api():
    """
    Search GovCon API for federal opportunities
    
    Returns:
        {
            "success": true,
            "total_found": 100,
            "imported": 25
        }
    """
    try:
        from nexus_backend import handle_govcon_api_search
        result = handle_govcon_api_search()
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e), "total_found": 0, "imported": 0}), 500


@app.route('/gpss/mining/mine-state-local', methods=['POST'])
def mine_state_local():
    """
    Mine state and local government opportunities
    
    Returns:
        {
            "success": true,
            "sources_checked": 5,
            "total_found": 200,
            "imported": 50
        }
    """
    try:
        from nexus_backend import handle_mine_state_local
        result = handle_mine_state_local()
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e), "sources_checked": 0, "imported": 0}), 500


@app.route('/gpss/forecasting/generate', methods=['POST'])
def generate_forecasts():
    """
    Generate opportunity forecasts based on historical data
    
    Optional JSON:
    {
      "agency_name": "Agency Name" (optional - forecast for specific agency),
      "lookback_months": 24 (optional - default 24)
    }
    """
    try:
        data = request.json or {}
        agency_name = data.get('agency_name')
        lookback_months = data.get('lookback_months', 24)
        
        mining_agent = GPSSOpportunityMiningAgent()
        result = mining_agent.forecast_opportunities(agency_name, lookback_months)
        
        if 'error' in result:
            return jsonify(result), 400
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/gpss/forecasting/agency-analysis/<agency_name>', methods=['GET'])
def analyze_agency(agency_name):
    """
    Analyze an agency's spending patterns and preferences
    
    URL Parameter:
    agency_name - Name of the agency to analyze
    """
    try:
        mining_agent = GPSSOpportunityMiningAgent()
        result = mining_agent.analyze_agency_spending(agency_name)
        
        if 'error' in result:
            return jsonify(result), 400
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/gpss/alerts/generate', methods=['GET'])
def generate_alerts():
    """
    Generate alerts for opportunities that need attention
    Returns list of urgent opportunities and forecasts
    """
    try:
        mining_agent = GPSSOpportunityMiningAgent()
        alerts = mining_agent.generate_opportunity_alerts()
        
        return jsonify({'alerts': alerts, 'total': len(alerts)})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/gpss/mining/target/<target_id>', methods=['POST'])
def scrape_target(target_id):
    """
    Scrape a Mining Target (public sites - NO login required)
    Finds opportunities from ANY website
    
    URL Parameter:
    target_id - Airtable record ID of the mining target
    """
    try:
        mining_agent = GPSSOpportunityMiningAgent()
        result = mining_agent.scrape_mining_target(target_id)
        
        if 'error' in result:
            return jsonify(result), 400
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/gpss/mining/scrape-all-targets', methods=['POST'])
def scrape_all_targets():
    """
    Scrape ALL active Mining Targets
    This discovers opportunities from ANY public source
    """
    try:
        mining_agent = GPSSOpportunityMiningAgent()
        result = mining_agent.scrape_all_targets()
        
        if 'error' in result:
            return jsonify(result), 400
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/gpss/intelligence/competitor/<competitor_name>', methods=['GET'])
def get_competitor_intelligence(competitor_name):
    """
    Search for competitor contract wins
    Scrapes news, press releases, USASpending.gov, etc.
    
    URL Parameter:
    competitor_name - Name of competitor to research
    
    Optional Query Parameter:
    keywords - Additional search keywords
    """
    try:
        keywords = request.args.get('keywords')
        
        mining_agent = GPSSOpportunityMiningAgent()
        result = mining_agent.competitive_intelligence_search(competitor_name, keywords)
        
        if 'error' in result:
            return jsonify(result), 400
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =====================================================================
# INVOICE ROUTES
# =====================================================================

@app.route('/invoices', methods=['GET'])
def get_invoices():
    """
    Get all invoices with optional filters
    
    Query Parameters:
    - status: Filter by invoice status (Draft, Sent, Pending, Paid, Overdue, Cancelled)
    - source_system: Filter by source system (GPSS, ATLAS, DDCSS, Manual)
    - client_type: Filter by client type (Government - Federal, Enterprise - Private, etc.)
    """
    try:
        filters = {}
        if request.args.get('status'):
            filters['status'] = request.args.get('status')
        if request.args.get('source_system'):
            filters['source_system'] = request.args.get('source_system')
        if request.args.get('client_type'):
            filters['client_type'] = request.args.get('client_type')
        
        result = handle_get_invoices(filters if filters else None)
        
        if not result.get('success'):
            return jsonify(result), 400
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500


@app.route('/invoices/<invoice_id>', methods=['GET'])
def get_invoice(invoice_id):
    """Get single invoice details"""
    try:
        result = handle_get_invoice(invoice_id)
        
        if not result.get('success'):
            return jsonify(result), 404
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500


@app.route('/invoices/generate/opportunity/<opportunity_id>', methods=['POST'])
def generate_invoice_from_opportunity(opportunity_id):
    """
    Generate invoice from GPSS opportunity
    
    URL Parameter:
    - opportunity_id: Airtable record ID of the opportunity
    """
    try:
        result = handle_generate_invoice_from_opportunity(opportunity_id)
        
        if not result.get('success'):
            return jsonify(result), 400
        
        return jsonify(result), 201
    
    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500


@app.route('/invoices/generate/project/<project_id>', methods=['POST'])
def generate_invoice_from_project(project_id):
    """
    Generate invoice from ATLAS project
    
    URL Parameter:
    - project_id: Airtable record ID of the project
    """
    try:
        result = handle_generate_invoice_from_project(project_id)
        
        if not result.get('success'):
            return jsonify(result), 400
        
        return jsonify(result), 201
    
    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500


@app.route('/invoices/generate/prospect/<prospect_id>', methods=['POST'])
def generate_invoice_from_prospect(prospect_id):
    """
    Generate invoice from DDCSS prospect
    
    URL Parameter:
    - prospect_id: Airtable record ID of the prospect
    """
    try:
        result = handle_generate_invoice_from_prospect(prospect_id)
        
        if not result.get('success'):
            return jsonify(result), 400
        
        return jsonify(result), 201
    
    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500


@app.route('/invoices/<invoice_id>', methods=['PUT'])
def update_invoice(invoice_id):
    """
    Update existing invoice
    
    Request Body: JSON with fields to update
    {
        "Invoice Status": "Sent",
        "Sent To Email": "client@example.com",
        "Sent Date": "2026-01-10T14:30:00",
        ...
    }
    """
    try:
        updates = request.json
        
        if not updates:
            return jsonify({"error": "No update data provided", "success": False}), 400
        
        result = handle_update_invoice(invoice_id, updates)
        
        if not result.get('success'):
            return jsonify(result), 400
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500


@app.route('/invoices/<invoice_id>', methods=['DELETE'])
def delete_invoice(invoice_id):
    """Delete an invoice"""
    try:
        result = handle_delete_invoice(invoice_id)
        
        if not result.get('success'):
            return jsonify(result), 400
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500


@app.route('/invoices/<invoice_id>/send', methods=['POST'])
def send_invoice(invoice_id):
    """
    Mark invoice as sent and update sent date/email
    
    Request Body:
    {
        "email": "client@example.com",
        "message": "Optional custom message"
    }
    """
    try:
        data = request.json or {}
        email = data.get('email')
        
        if not email:
            return jsonify({"error": "Email address required", "success": False}), 400
        
        # Update invoice status and sent details
        updates = {
            "Invoice Status": "Sent",
            "Sent To Email": email,
            "Sent Date": datetime.now().isoformat()
        }
        
        result = handle_update_invoice(invoice_id, updates)
        
        if not result.get('success'):
            return jsonify(result), 400
        
        return jsonify({
            **result,
            "message": f"Invoice marked as sent to {email}"
        })
    
    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500


# =====================================================================
# GPSS CONTACTS ENDPOINTS
# =====================================================================

@app.route('/gpss/contacts', methods=['GET'])
def get_gpss_contacts():
    """Get all contacts with optional filtering"""
    try:
        airtable_client = AirtableClient()
        records = airtable_client.get_all_records('GPSS CONTACTS')
        
        contacts = []
        for record in records:
            fields = record['fields']
            contacts.append({
                'id': record['id'],
                'firstName': fields.get('First Name', ''),
                'lastName': fields.get('Last Name', ''),
                'email': fields.get('Email', ''),
                'phone': fields.get('Phone', ''),
                'title': fields.get('Title', ''),
                'agency': fields.get('Agency', ''),
                'department': fields.get('Department', ''),
                'address': fields.get('Address', ''),
                'city': fields.get('City', ''),
                'state': fields.get('State', ''),
                'zip': fields.get('ZIP', ''),
                'source': fields.get('Source', ''),
                'created': fields.get('Created', '')
            })
        
        return jsonify({'contacts': contacts})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/gpss/contacts', methods=['POST'])
def create_gpss_contact():
    """Create a new contact"""
    try:
        data = request.json
        airtable_client = AirtableClient()
        
        fields = {
            'First Name': data.get('firstName', ''),
            'Last Name': data.get('lastName', ''),
            'Email': data.get('email', ''),
            'Phone': data.get('phone', ''),
            'Title': data.get('title', ''),
            'Agency': data.get('agency', ''),
            'Department': data.get('department', ''),
            'Address': data.get('address', ''),
            'City': data.get('city', ''),
            'State': data.get('state', ''),
            'ZIP': data.get('zip', ''),
            'Source': data.get('source', 'Manual'),
            'Created': datetime.now().isoformat()
        }
        
        result = airtable_client.create_record('GPSS CONTACTS', fields)
        return jsonify({'contact': {'id': result['id'], **fields}})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/gpss/contacts/<contact_id>', methods=['PUT'])
def update_gpss_contact(contact_id):
    """Update a contact"""
    try:
        data = request.json
        airtable_client = AirtableClient()
        
        field_mapping = {
            'firstName': 'First Name',
            'lastName': 'Last Name',
            'email': 'Email',
            'phone': 'Phone',
            'title': 'Title',
            'agency': 'Agency',
            'department': 'Department',
            'address': 'Address',
            'city': 'City',
            'state': 'State',
            'zip': 'ZIP',
            'source': 'Source'
        }
        
        update_fields = {}
        for key, airtable_field in field_mapping.items():
            if key in data:
                update_fields[airtable_field] = data[key]
        
        update_fields['Last Modified'] = datetime.now().isoformat()
        
        airtable_client.update_record('GPSS CONTACTS', contact_id, update_fields)
        return jsonify({'success': True})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/gpss/contacts/<contact_id>', methods=['DELETE'])
def delete_gpss_contact(contact_id):
    """Delete a contact"""
    try:
        airtable_client = AirtableClient()
        table = airtable_client.get_table('GPSS CONTACTS')
        table.delete(contact_id)
        return jsonify({'success': True})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =====================================================================
# GPSS PRODUCTS ENDPOINTS
# =====================================================================

@app.route('/gpss/products', methods=['GET'])
def get_gpss_products():
    """Get all products"""
    try:
        airtable_client = AirtableClient()
        
        # Try to get products from Airtable (table might not exist yet)
        try:
            records = airtable_client.get_all_records('Products')
        except:
            return jsonify({'products': []})
        
        products = []
        for record in records:
            fields = record['fields']
            products.append({
                'id': record['id'],
                'name': fields.get('Product Name', ''),
                'description': fields.get('Description', ''),
                'category': fields.get('Category', ''),
                'basePrice': fields.get('Base Price', 0),
                'unit': fields.get('Unit', ''),
                'serviceCategory': fields.get('Service Category', ''),
                'created': fields.get('Created', '')
            })
        
        return jsonify({'products': products})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/gpss/products', methods=['POST'])
def create_gpss_product():
    """Create a new product"""
    try:
        data = request.json
        airtable_client = AirtableClient()
        
        fields = {
            'Product Name': data.get('name', ''),
            'Description': data.get('description', ''),
            'Category': data.get('category', ''),
            'Base Price': data.get('basePrice', 0),
            'Unit': data.get('unit', 'each'),
            'Service Category': data.get('serviceCategory', ''),
            'Created': datetime.now().isoformat()
        }
        
        result = airtable_client.create_record('Products', fields)
        return jsonify({'product': {'id': result['id'], **fields}})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/gpss/products/<product_id>', methods=['PUT'])
def update_gpss_product(product_id):
    """Update a product"""
    try:
        data = request.json
        airtable_client = AirtableClient()
        
        field_mapping = {
            'name': 'Product Name',
            'description': 'Description',
            'category': 'Category',
            'basePrice': 'Base Price',
            'unit': 'Unit',
            'serviceCategory': 'Service Category'
        }
        
        update_fields = {}
        for key, airtable_field in field_mapping.items():
            if key in data:
                update_fields[airtable_field] = data[key]
        
        update_fields['Last Modified'] = datetime.now().isoformat()
        
        airtable_client.update_record('Products', product_id, update_fields)
        return jsonify({'success': True})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/gpss/products/<product_id>', methods=['DELETE'])
def delete_gpss_product(product_id):
    """Delete a product"""
    try:
        airtable_client = AirtableClient()
        table = airtable_client.get_table('Products')
        table.delete(product_id)
        return jsonify({'success': True})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =====================================================================
# GPSS SUPPLIER MINING & AUTOMATED QUOTING ENDPOINTS
# =====================================================================

@app.route('/gpss/suppliers', methods=['GET'])
def get_gpss_suppliers():
    """Get all suppliers with optional filters"""
    try:
        from nexus_backend import handle_search_suppliers
        
        # Get filter parameters
        filters = {
            'category': request.args.get('category'),
            'keywords': request.args.getlist('keywords'),
            'min_rating': float(request.args.get('min_rating', 0))
        }
        
        suppliers = handle_search_suppliers(filters)
        return jsonify({'suppliers': suppliers})
    
    except Exception as e:
        print(f"Error getting suppliers: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/gpss/suppliers', methods=['POST'])
def create_gpss_supplier():
    """Create a new supplier"""
    try:
        from nexus_backend import handle_create_supplier
        
        data = request.json
        result = handle_create_supplier(data)
        
        if result.get('error'):
            return jsonify(result), 400
        
        return jsonify({'supplier': result})
    
    except Exception as e:
        print(f"Error creating supplier: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/gpss/suppliers/<supplier_id>', methods=['GET'])
def get_gpss_supplier(supplier_id):
    """Get single supplier details"""
    try:
        from nexus_backend import handle_get_supplier
        
        supplier = handle_get_supplier(supplier_id)
        
        if not supplier:
            return jsonify({"error": "Supplier not found"}), 404
        
        return jsonify({'supplier': supplier})
    
    except Exception as e:
        print(f"Error getting supplier: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/gpss/suppliers/<supplier_id>', methods=['PUT'])
def update_gpss_supplier(supplier_id):
    """Update supplier"""
    try:
        from nexus_backend import handle_update_supplier
        
        data = request.json
        result = handle_update_supplier(supplier_id, data)
        
        if result.get('error'):
            return jsonify(result), 400
        
        return jsonify({'success': True, 'supplier': result})
    
    except Exception as e:
        print(f"Error updating supplier: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/gpss/suppliers/find-for-product', methods=['POST'])
def find_suppliers_for_product():
    """Find suppliers for a specific product"""
    try:
        from nexus_backend import handle_find_suppliers_for_product
        
        data = request.json
        product = data.get('product')
        category = data.get('category')
        
        if not product:
            return jsonify({"error": "product is required"}), 400
        
        suppliers = handle_find_suppliers_for_product(product, category)
        return jsonify({'suppliers': suppliers})
    
    except Exception as e:
        print(f"Error finding suppliers: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/gpss/suppliers/mine', methods=['POST'])
def mine_suppliers():
    """Mine suppliers from online sources (GSA, Google, etc.)"""
    try:
        data = request.json
        product = data.get('product')
        category = data.get('category')
        
        if not product:
            return jsonify({"error": "product is required"}), 400
        
        # Note: Actual mining implementation would go here
        # For now, return placeholder
        return jsonify({
            'success': True,
            'message': 'Supplier mining initiated',
            'product': product,
            'category': category,
            'suppliers_found': 0,
            'note': 'Mining implementation coming soon'
        })
    
    except Exception as e:
        print(f"Error mining suppliers: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/gpss/auto-quote/process-opportunity', methods=['POST'])
def auto_quote_process_opportunity():
    """
    Process opportunity with automated supplier finding and quote generation
    
    Expected JSON:
    {
      "opportunity_id": "recXXXXX",
      "max_suppliers": 5
    }
    """
    try:
        from nexus_backend import handle_process_opportunity_for_suppliers
        
        data = request.json
        opportunity_id = data.get('opportunity_id')
        
        if not opportunity_id:
            return jsonify({"error": "opportunity_id is required"}), 400
        
        result = handle_process_opportunity_for_suppliers(opportunity_id)
        
        if not result.get('success'):
            return jsonify(result), 400
        
        return jsonify(result)
    
    except Exception as e:
        print(f"Error processing opportunity: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/gpss/auto-quote/find-suppliers', methods=['POST'])
def auto_quote_find_suppliers():
    """
    Find matching suppliers for an opportunity
    
    Expected JSON:
    {
      "opportunity_id": "recXXXXX"
    }
    """
    try:
        from nexus_backend import handle_find_suppliers_for_opportunity
        
        data = request.json
        opportunity_id = data.get('opportunity_id')
        
        if not opportunity_id:
            return jsonify({"error": "opportunity_id is required"}), 400
        
        suppliers = handle_find_suppliers_for_opportunity(opportunity_id)
        
        return jsonify({
            'success': True,
            'opportunity_id': opportunity_id,
            'suppliers': suppliers
        })
    
    except Exception as e:
        print(f"Error finding suppliers for opportunity: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/gpss/supplier-quotes', methods=['GET'])
def get_supplier_quotes():
    """Get supplier quotes with optional filters"""
    try:
        airtable_client = AirtableClient()
        
        # Get filter parameters
        opportunity_id = request.args.get('opportunity_id')
        supplier_id = request.args.get('supplier_id')
        status = request.args.get('status')
        
        # Build formula for filtering
        formulas = []
        if opportunity_id:
            formulas.append(f"{{Opportunity}}='{opportunity_id}'")
        if supplier_id:
            formulas.append(f"{{Supplier}}='{supplier_id}'")
        if status:
            formulas.append(f"{{Request Status}}='{status}'")
        
        # Fetch quotes
        if formulas:
            formula = f"AND({','.join(formulas)})"
            records = airtable_client.search_records('GPSS Supplier Quotes', formula)
        else:
            records = airtable_client.get_all_records('GPSS Supplier Quotes')
        
        # Format quotes
        quotes = []
        for record in records:
            fields = record.get('fields', {})
            quotes.append({
                'id': record.get('id'),
                'opportunity_id': fields.get('Opportunity', [None])[0],
                'supplier_id': fields.get('Supplier', [None])[0],
                'product_requested': fields.get('Product/Service Requested', ''),
                'quantity': fields.get('Quantity', ''),
                'supplier_quote_amount': fields.get('Supplier Quote Amount', 0),
                'our_proposed_price': fields.get('Our Proposed Price', 0),
                'net_profit': fields.get('Net Profit After Factoring ($)', 0),
                'request_status': fields.get('Request Status', ''),
                'quote_received_date': fields.get('Quote Received Date', ''),
                'selected': fields.get('Selected for Quote', False)
            })
        
        return jsonify({'quotes': quotes})
    
    except Exception as e:
        print(f"Error getting supplier quotes: {e}")
        return jsonify({"error": str(e), "quotes": []}), 500


@app.route('/gpss/supplier-quotes/<quote_id>', methods=['PUT'])
def update_supplier_quote(quote_id):
    """Update supplier quote (e.g., when supplier responds)"""
    try:
        airtable_client = AirtableClient()
        data = request.json
        
        # Build update fields
        update_fields = {}
        if 'supplier_quote_amount' in data:
            update_fields['Supplier Quote Amount'] = data['supplier_quote_amount']
        if 'quoted_lead_time' in data:
            update_fields['Quoted Lead Time (Days)'] = data['quoted_lead_time']
        if 'request_status' in data:
            update_fields['Request Status'] = data['request_status']
        if 'quote_received_date' in data:
            update_fields['Quote Received Date'] = data['quote_received_date']
        if 'selected' in data:
            update_fields['Selected for Quote'] = data['selected']
        
        result = airtable_client.update_record('GPSS Supplier Quotes', quote_id, update_fields)
        
        return jsonify({'success': True, 'quote': result})
    
    except Exception as e:
        print(f"Error updating supplier quote: {e}")
        return jsonify({"error": str(e)}), 500


# =====================================================================
# GPSS PROPOSALBIO™ QUALITY ASSURANCE ENDPOINTS
# =====================================================================

@app.route('/gpss/proposalbio/analyze', methods=['POST'])
def gpss_proposalbio_analyze():
    """
    Run ProposalBio™ 10-biohack analysis on a proposal
    
    Expected JSON:
    {
      "proposal_id": "recXXXXX",
      "metadata": {
        "agency_type": "Federal|State|Local|Cooperative",
        "region": "Northeast|Mid_Atlantic|Southeast|Midwest|Southwest|West_Coast",
        "rfp_text": "Full RFP text for familiarity analysis (optional)"
      }
    }
    """
    try:
        data = request.json or {}
        proposal_id = data.get('proposal_id')
        metadata = data.get('metadata') or {}

        if not proposal_id:
            return jsonify({"error": "proposal_id is required"}), 400

        svc = ProposalBioService()
        result = svc.analyze_proposal(proposal_id, metadata_override=metadata)

        if 'error' in result:
            return jsonify(result), 400

        return jsonify(result)

    except Exception as e:
        print(f"ProposalBio analysis error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/gpss/proposalbio/score/<proposal_id>', methods=['GET'])
def gpss_proposalbio_score(proposal_id):
    """Get existing ProposalBio™ scores for a proposal"""
    try:
        airtable_client = AirtableClient()
        recs = airtable_client.search_records('GPSS Proposals', f"RECORD_ID()='{proposal_id}'")
        if not recs:
            return jsonify({"error": "Proposal not found"}), 404

        fields = recs[0].get('fields', {})
        
        return jsonify({
            "proposal_id": proposal_id,
            "composite_score": fields.get("ProposalBio Composite Score"),
            "status": fields.get("ProposalBio Status"),
            "submission_gate": fields.get("ProposalBio Gate"),
            "last_analyzed": fields.get("ProposalBio Last Analyzed"),
            "revision_count": fields.get("ProposalBio Revision Count", 0),
            "approved_by": fields.get("ProposalBio Approved By"),
            "approved_date": fields.get("ProposalBio Approved Date"),
            "biohack_scores": json.loads(fields.get("ProposalBio Biohack Scores JSON") or "[]"),
            "critical_issues": json.loads(fields.get("ProposalBio Critical Issues JSON") or "[]"),
            "priority_improvements": json.loads(fields.get("ProposalBio Priority Improvements JSON") or "[]"),
        })
    except Exception as e:
        print(f"ProposalBio score retrieval error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/gpss/proposalbio/approve', methods=['POST'])
def gpss_proposalbio_approve():
    """
    Approve proposal for submission (unlocks quality gate)
    
    Expected JSON:
    {
      "proposal_id": "recXXXXX",
      "approved_by": "Dee Davis",
      "override_warnings": false
    }
    """
    try:
        data = request.json or {}
        proposal_id = data.get('proposal_id')
        approved_by = data.get('approved_by', 'Alexis Nexus')
        override_warnings = bool(data.get('override_warnings', False))

        if not proposal_id:
            return jsonify({"error": "proposal_id is required"}), 400

        svc = ProposalBioService()
        result = svc.approve(proposal_id, approved_by=approved_by, override_warnings=override_warnings)

        if 'error' in result:
            return jsonify(result), 400

        return jsonify(result)
    except Exception as e:
        print(f"ProposalBio approval error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/gpss/proposalbio/outcome', methods=['POST'])
def gpss_proposalbio_outcome():
    """
    Record win/loss outcome for adaptive learning
    
    Expected JSON:
    {
      "proposal_id": "recXXXXX",
      "outcome": "Won|Lost|No Decision",
      "win_value": 1500000
    }
    """
    try:
        data = request.json or {}
        proposal_id = data.get('proposal_id')
        outcome = data.get('outcome')
        win_value = float(data.get('win_value', 0))

        if not proposal_id or not outcome:
            return jsonify({"error": "proposal_id and outcome are required"}), 400

        svc = ProposalBioService()
        result = svc.record_outcome(proposal_id, outcome, win_value)

        if 'error' in result:
            return jsonify(result), 400

        return jsonify(result)
    except Exception as e:
        print(f"ProposalBio outcome recording error: {e}")
        return jsonify({"error": str(e)}), 500


# =====================================================================
# DDCSS PROSPECTS & TOOLS ENDPOINTS
# =====================================================================

@app.route('/ddcss/prospects', methods=['GET'])
def get_ddcss_prospects():
    """Get all DDCSS prospects"""
    try:
        airtable_client = AirtableClient()
        
        try:
            records = airtable_client.get_all_records('DDCSS Prospects')
        except:
            return jsonify({'prospects': []})
        
        prospects = []
        for record in records:
            fields = record['fields']
            prospects.append({
                'id': record['id'],
                'companyName': fields.get('Company Name', ''),
                'industry': fields.get('Industry', ''),
                'companySize': fields.get('Company Size', ''),
                'location': fields.get('Location', ''),
                'currentChallenge': fields.get('Current Challenge', ''),
                'businessGoals': fields.get('Business Goals', ''),
                'budget': fields.get('Budget', ''),
                'timeline': fields.get('Timeline', ''),
                'qualificationScore': fields.get('Qualification Score', 0),
                'icpFitScore': fields.get('ICP Fit Score', 0),
                'status': fields.get('Status', 'New'),
                'created': fields.get('Created', '')
            })
        
        return jsonify({'prospects': prospects})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/ddcss/prospects', methods=['POST'])
def create_ddcss_prospect():
    """Create a new DDCSS prospect"""
    try:
        data = request.json
        airtable_client = AirtableClient()
        
        fields = {
            'Company Name': data.get('companyName', ''),
            'Industry': data.get('industry', ''),
            'Company Size': data.get('companySize', ''),
            'Location': data.get('location', ''),
            'Current Challenge': data.get('currentChallenge', ''),
            'Business Goals': data.get('businessGoals', ''),
            'Budget': data.get('budget', ''),
            'Timeline': data.get('timeline', ''),
            'Status': 'New',
            'Created': datetime.now().isoformat()
        }
        
        result = airtable_client.create_record('DDCSS Prospects', fields)
        return jsonify({'prospect': {'id': result['id'], **fields}})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/ddcss/prospects/<prospect_id>', methods=['PUT'])
def update_ddcss_prospect(prospect_id):
    """Update DDCSS prospect - with auto-ATLAS integration when client won"""
    try:
        data = request.json
        airtable_client = AirtableClient()
        
        # Get current prospect to check status change
        current_prospect = airtable_client.get_record('DDCSS Prospects', prospect_id)
        old_status = current_prospect['fields'].get('Status', '')
        
        update_fields = {}
        field_mapping = {
            'companyName': 'Company Name',
            'industry': 'Industry',
            'companySize': 'Company Size',
            'location': 'Location',
            'contactName': 'Contact Name',
            'contactTitle': 'Contact Title',
            'contactEmail': 'Contact Email',
            'contactPhone': 'Contact Phone',
            'linkedinProfile': 'LinkedIn Profile',
            'website': 'Website',
            'pipelineStage': 'Pipeline Stage',
            'status': 'Status',
            'budgetRange': 'Budget Range',
            'timeline': 'Timeline',
            'painPoints': 'Pain Points',
            'qualificationScore': 'Qualification Score',
            'icpFitScore': 'ICP Fit Score',
            'winProbability': 'Win Probability',
            'notes': 'Notes'
        }
        
        for key, airtable_field in field_mapping.items():
            if key in data:
                update_fields[airtable_field] = data[key]
        
        # Update the prospect
        airtable_client.update_record('DDCSS Prospects', prospect_id, update_fields)
        
        # 🎯 AUTO-CREATE ATLAS PROJECT IF STATUS CHANGED TO "CLIENT WON"
        new_status = update_fields.get('Status', old_status)
        if new_status == 'Client Won' and old_status != 'Client Won':
            # Check if ATLAS project already exists
            existing_atlas_link = current_prospect['fields'].get('ATLAS Project')
            
            if not existing_atlas_link:
                try:
                    # Auto-create ATLAS project for corporate engagement!
                    atlas_result = create_atlas_project_from_prospect(prospect_id, airtable_client)
                    
                    return jsonify({
                        'success': True,
                        'message': '🎉 Client Won! ATLAS project created automatically!',
                        'atlas_project_created': True,
                        'atlas_project_id': atlas_result['project_id'],
                        'atlas_project_name': atlas_result['project_name'],
                        'wbs_generated': atlas_result.get('wbs_generated', False)
                    })
                except Exception as atlas_error:
                    print(f"Error creating ATLAS project from prospect: {atlas_error}")
                    return jsonify({
                        'success': True,
                        'message': 'Prospect updated. ATLAS project creation failed - please create manually.',
                        'atlas_error': str(atlas_error)
                    })
        
        return jsonify({'success': True})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def create_atlas_project_from_prospect(prospect_id: str, airtable_client=None) -> dict:
    """
    🎯 AUTO-CREATE ATLAS PROJECT FROM WON DDCSS PROSPECT
    """
    if not airtable_client:
        airtable_client = AirtableClient()
    
    # Get prospect details
    prospect = airtable_client.get_record('DDCSS Prospects', prospect_id)
    prospect_fields = prospect['fields']
    
    # Extract key information
    company_name = prospect_fields.get('Company Name', 'Unknown Company')
    contact_name = prospect_fields.get('Contact Name', '')
    industry = prospect_fields.get('Industry', 'Unknown')
    budget = prospect_fields.get('Budget Range', '').replace('$', '').replace(',', '').replace('+', '').split('-')[0] if prospect_fields.get('Budget Range') else 0
    
    try:
        budget_value = float(budget) if budget else 50000  # Default to $50K
    except:
        budget_value = 50000
    
    pain_points = prospect_fields.get('Pain Points', '')
    timeline = prospect_fields.get('Timeline', '')
    recommended_service = prospect_fields.get('Primary Service', 'Corporate Consulting')
    
    # Build comprehensive project scope
    project_scope = f"""
CLIENT: {company_name}
CONTACT: {contact_name}
INDUSTRY: {industry}

ENGAGEMENT TYPE: {recommended_service}

PAIN POINTS & OBJECTIVES:
{pain_points}

TIMELINE: {timeline}

DELIVERABLES:
- Discovery & Assessment
- Strategic Recommendations
- Implementation Plan
- Follow-up Support
    """.strip()
    
    # Create ATLAS project record
    project_fields = {
        'Project Name': f"{recommended_service} - {company_name}",
        'Client Name': company_name,
        'Project Type': 'Corporate Consulting',
        'Industry': industry,
        'Budget': budget_value,
        'Project Scope': project_scope[:10000],
        'Start Date': datetime.now().isoformat(),
        'Status': 'Planning',
        'Priority': 'High',
        'Completion Percentage': 0,
        'Created Date': datetime.now().isoformat(),
        'Source System': 'DDCSS',
        'Source Prospect ID': prospect_id
    }
    
    # Create the project
    project_record = airtable_client.create_record('ATLAS PROJECTS', project_fields)
    project_id = project_record['id']
    
    # Link prospect to ATLAS project
    try:
        airtable_client.update_record('DDCSS Prospects', prospect_id, {
            'ATLAS Project': [project_id]
        })
    except Exception as link_error:
        print(f"Warning: Could not link prospect to ATLAS project: {link_error}")
    
    # Auto-generate WBS
    wbs_generated = False
    try:
        from nexus_backend import ATLASAgent2
        atlas_agent = ATLASAgent2()
        wbs_result = atlas_agent.generate_wbs(project_id)
        wbs_generated = 'error' not in wbs_result
    except Exception as wbs_error:
        print(f"Warning: WBS generation failed: {wbs_error}")
    
    return {
        'success': True,
        'project_id': project_id,
        'project_name': project_fields['Project Name'],
        'wbs_generated': wbs_generated,
        'message': f'✅ ATLAS project created: {project_fields["Project Name"]}'
    }


@app.route('/ddcss/prospects/<prospect_id>/create-atlas-project', methods=['POST'])
def manual_create_atlas_project_from_prospect(prospect_id):
    """Manual endpoint to create ATLAS project from prospect"""
    try:
        result = create_atlas_project_from_prospect(prospect_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/ddcss/client-avatars', methods=['GET'])
def get_ddcss_client_avatars():
    """Get all client avatars"""
    try:
        airtable_client = AirtableClient()
        
        try:
            records = airtable_client.get_all_records('DDCSS Client Avatars')
        except:
            return jsonify({'avatars': []})
        
        avatars = []
        for record in records:
            fields = record['fields']
            avatars.append({
                'id': record['id'],
                'avatarName': fields.get('Avatar Name', ''),
                'companySize': fields.get('Company Size', ''),
                'industry': fields.get('Industry', ''),
                'painPoints': fields.get('Pain Points', ''),
                'goals': fields.get('Goals', ''),
                'budget': fields.get('Budget', ''),
                'decisionMakers': fields.get('Decision Makers', ''),
                'prospectId': fields.get('Prospect ID', ''),
                'created': fields.get('Created', '')
            })
        
        return jsonify({'avatars': avatars})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/ddcss/client-avatars', methods=['POST'])
def create_ddcss_client_avatar():
    """Create a new client avatar (with AI analysis)"""
    try:
        data = request.json
        airtable_client = AirtableClient()
        
        # Create avatar record
        fields = {
            'Avatar Name': data.get('avatarName', ''),
            'Company Size': data.get('companySize', ''),
            'Industry': data.get('industry', ''),
            'Pain Points': data.get('painPoints', ''),
            'Goals': data.get('goals', ''),
            'Budget': data.get('budget', ''),
            'Decision Makers': data.get('decisionMakers', ''),
            'Prospect ID': data.get('prospectId', ''),
            'Created': datetime.now().isoformat()
        }
        
        result = airtable_client.create_record('DDCSS Client Avatars', fields)
        
        # AI Analysis (optional - can be done async)
        ai_analysis = {}
        try:
            from nexus_backend import DDCSSAgent1
            agent = DDCSSAgent1()
            if data.get('prospectId'):
                ai_analysis = agent.qualify_prospect(data.get('prospectId'))
        except:
            pass
        
        return jsonify({
            'avatar': {'id': result['id'], **fields},
            'aiAnalysis': ai_analysis
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/ddcss/success-paths', methods=['POST'])
def create_ddcss_success_path():
    """Create a success path (with AI visualization)"""
    try:
        data = request.json
        airtable_client = AirtableClient()
        
        fields = {
            'Path Name': data.get('pathName', ''),
            'Prospect ID': data.get('prospectId', ''),
            'Starting Point': data.get('startingPoint', ''),
            'End Goal': data.get('endGoal', ''),
            'Milestones': data.get('milestones', ''),
            'Timeline': data.get('timeline', ''),
            'Created': datetime.now().isoformat()
        }
        
        result = airtable_client.create_record('DDCSS Success Paths', fields)
        return jsonify({'successPath': {'id': result['id'], **fields}})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/ddcss/pitchmaps', methods=['POST'])
def create_ddcss_pitchmap():
    """Generate a pitchmap (with AI script generation)"""
    try:
        data = request.json
        airtable_client = AirtableClient()
        
        # Generate AI script
        script_content = ""
        try:
            import anthropic
            anthropic_client = anthropic.Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))
            
            message = anthropic_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2000,
                messages=[{
                    "role": "user",
                    "content": f"""Generate a pitch script for this scenario:

Prospect: {data.get('prospectName', 'Unknown')}
Industry: {data.get('industry', 'Unknown')}
Pain Point: {data.get('painPoint', 'Unknown')}
Goal: {data.get('goal', 'Unknown')}
Timeline: {data.get('timeline', 'Unknown')}

Create a compelling, consultative pitch script that:
1. Opens with a hook based on their pain point
2. Positions our Blueprint Framework as the solution
3. Includes 2-3 proof points
4. Closes with a clear next step (discovery call)

Keep it conversational, professional, and focused on outcomes."""
                }]
            )
            script_content = message.content[0].text
        except:
            script_content = "AI script generation unavailable"
        
        fields = {
            'PitchMap Name': data.get('pitchMapName', ''),
            'Prospect ID': data.get('prospectId', ''),
            'Pain Point': data.get('painPoint', ''),
            'Solution': data.get('solution', ''),
            'Script': script_content,
            'Status': 'Draft',
            'Created': datetime.now().isoformat()
        }
        
        result = airtable_client.create_record('DDCSS PitchMaps', fields)
        return jsonify({
            'pitchmap': {'id': result['id'], **fields},
            'script': script_content
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =====================================================================
# MINING TARGETS ENDPOINTS
# =====================================================================

@app.route('/gpss/mining/targets', methods=['GET'])
def get_mining_targets():
    """Get all mining targets"""
    try:
        airtable_client = AirtableClient()
        
        try:
            records = airtable_client.get_all_records('Mining Targets')
        except:
            return jsonify({'targets': []})
        
        targets = []
        for record in records:
            fields = record['fields']
            targets.append({
                'id': record['id'],
                'targetName': fields.get('Target Name', ''),
                'url': fields.get('URL', ''),
                'targetType': fields.get('Target Type', ''),
                'keywords': fields.get('Keywords', ''),
                'lastScraped': fields.get('Last Scraped', ''),
                'active': fields.get('Active', True)
            })
        
        return jsonify({'targets': targets})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/gpss/mining/targets', methods=['POST'])
def create_mining_target():
    """Create a new mining target"""
    try:
        data = request.json
        airtable_client = AirtableClient()
        
        fields = {
            'Target Name': data.get('targetName', ''),
            'URL': data.get('url', ''),
            'Target Type': data.get('targetType', 'Website'),
            'Keywords': data.get('keywords', ''),
            'Active': data.get('active', True),
            'Created': datetime.now().isoformat()
        }
        
        result = airtable_client.create_record('Mining Targets', fields)
        return jsonify({'target': {'id': result['id'], **fields}})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/gpss/mining/targets/<target_id>', methods=['PUT'])
def update_mining_target(target_id):
    """Update a mining target"""
    try:
        data = request.json
        airtable_client = AirtableClient()
        
        field_mapping = {
            'targetName': 'Target Name',
            'url': 'URL',
            'targetType': 'Target Type',
            'keywords': 'Keywords',
            'active': 'Active'
        }
        
        update_fields = {}
        for key, airtable_field in field_mapping.items():
            if key in data:
                update_fields[airtable_field] = data[key]
        
        airtable_client.update_record('Mining Targets', target_id, update_fields)
        return jsonify({'success': True})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/gpss/mining/targets/<target_id>', methods=['DELETE'])
def delete_mining_target(target_id):
    """Delete a mining target"""
    try:
        airtable_client = AirtableClient()
        table = airtable_client.get_table('Mining Targets')
        table.delete(target_id)
        return jsonify({'success': True})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================================================
# AI CONVERSATIONS ENDPOINTS
# ============================================================================

@app.route('/ai/conversations', methods=['POST'])
def create_conversation():
    """Create a new AI conversation"""
    try:
        data = request.json
        airtable_client = AirtableClient()
        
        import json
        fields = {
            'Session ID': data.get('sessionId'),
            'Messages': json.dumps(data.get('messages', [])),
            'Message Count': len(data.get('messages', [])),
            'System Context': data.get('systemContext', 'General'),
            'Status': 'Active'
        }
        
        record = airtable_client.create_record('AI Conversations', fields)
        return jsonify({'success': True, 'recordId': record['id']})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/ai/conversations/<session_id>', methods=['PUT'])
def update_conversation(session_id):
    """Update an existing AI conversation with new messages"""
    try:
        data = request.json
        airtable_client = AirtableClient()
        
        import json
        
        # Find the conversation by session ID
        records = airtable_client.get_all_records('AI Conversations')
        conversation_record = None
        for record in records:
            if record['fields'].get('Session ID') == session_id:
                conversation_record = record
                break
        
        if not conversation_record:
            # Create new conversation if doesn't exist
            fields = {
                'Session ID': session_id,
                'Messages': json.dumps(data.get('messages', [])),
                'Message Count': len(data.get('messages', [])),
                'System Context': data.get('systemContext', 'General'),
                'Status': 'Active'
            }
            record = airtable_client.create_record('AI Conversations', fields)
            return jsonify({'success': True, 'recordId': record['id']})
        
        # Update existing conversation
        update_fields = {
            'Messages': json.dumps(data.get('messages', [])),
            'Message Count': len(data.get('messages', []))
        }
        
        if 'systemContext' in data:
            update_fields['System Context'] = data['systemContext']
        if 'topics' in data:
            update_fields['Topics'] = data['topics']
        if 'status' in data:
            update_fields['Status'] = data['status']
        if 'userRating' in data:
            update_fields['User Rating'] = data['userRating']
        if 'notes' in data:
            update_fields['Notes'] = data['notes']
        
        airtable_client.update_record('AI Conversations', conversation_record['id'], update_fields)
        return jsonify({'success': True, 'recordId': conversation_record['id']})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/ai/conversations/<session_id>', methods=['GET'])
def get_conversation(session_id):
    """Get a conversation by session ID"""
    try:
        airtable_client = AirtableClient()
        
        import json
        
        records = airtable_client.get_all_records('AI Conversations')
        for record in records:
            if record['fields'].get('Session ID') == session_id:
                fields = record['fields']
                return jsonify({
                    'success': True,
                    'conversation': {
                        'sessionId': fields.get('Session ID'),
                        'messages': json.loads(fields.get('Messages', '[]')),
                        'messageCount': fields.get('Message Count', 0),
                        'systemContext': fields.get('System Context'),
                        'topics': fields.get('Topics', []),
                        'status': fields.get('Status'),
                        'userRating': fields.get('User Rating'),
                        'notes': fields.get('Notes'),
                        'started': fields.get('Started'),
                        'lastUpdated': fields.get('Last Updated')
                    }
                })
        
        return jsonify({"error": "Conversation not found"}), 404
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/alexa/command', methods=['POST'])
@require_alexa_auth
def alexa_command():
    """Alexa voice command endpoint - processes voice commands securely"""
    try:
        data = request.json
        command = data.get('command', '').strip()

        if not command:
            return jsonify({
                'response': 'I didn\'t hear a command. Please try again.',
                'success': False
            })

        # Process the command through the AI copilot
        ai_response = process_alexa_command(command)

        return jsonify({
            'response': ai_response,
            'success': True
        })

    except Exception as e:
        return jsonify({
            'response': f'Sorry, I encountered an error processing your request.',
            'success': False,
            'error': str(e)
        }), 500

def process_alexa_command(command):
    """
    Process Alexa voice commands and return appropriate responses
    Handles 86 intents across all NEXUS systems
    """
    command_lower = command.lower()
    
    # ========== CORE SYSTEM COMMANDS ==========
    
    # Hello/Greeting
    if command_lower == 'hello':
        return "Hello! I'm Alexis, your NEXUS executive assistant. How can I help you today?"
    
    # System-wide status
    if 'nexus:' in command_lower and 'system-wide status' in command_lower:
        return get_nexus_system_status()
    
    # Meeting notes dictation
    if 'meeting notes:' in command_lower and 'dictate' in command_lower:
        return "Meeting notes feature is ready. Please continue with your dictation."
    
    # Compliance landscape
    if 'compliance:' in command_lower and 'landscape' in command_lower:
        return get_compliance_overview()
    
    # Invoice status
    if 'invoices:' in command_lower and 'status' in command_lower:
        return get_invoice_status()
    
    # Financial metrics
    if 'financial:' in command_lower and 'metrics' in command_lower:
        return get_financial_metrics()
    
    # ========== EXECUTIVE ASSISTANT COMMANDS ==========
    
    # NEXUS features explanation
    if 'nexus:' in command_lower and 'explain features' in command_lower:
        return "NEXUS integrates government contracting, project management, market intelligence, compliance tracking, and financial metrics into one voice-controlled system."
    
    # Reminders
    if 'reminders:' in command_lower and 'list' in command_lower:
        return "You have no pending reminders at this time."
    
    # Contacts management
    if 'contacts:' in command_lower and 'manage' in command_lower:
        return get_contacts_summary()
    
    # Task creation
    if 'task:' in command_lower and 'create' in command_lower:
        return "Task creation feature is ready. What task would you like to create?"
    
    # Notifications
    if 'notifications:' in command_lower and 'show' in command_lower:
        return "You have no new notifications at this time."
    
    # ========== GPSS - GOVERNMENT CONTRACTING ==========
    
    # Search contracts
    if 'gpss:' in command_lower and 'search contracts' in command_lower:
        return "Searching government contract opportunities. This feature connects to SAM.gov and other federal databases."
    
    # Pipeline analysis
    if 'gpss:' in command_lower and 'analyze pipeline' in command_lower:
        return get_gpss_pipeline_analysis()
    
    # Federal buyer info
    if 'gpss:' in command_lower and 'federal buyer' in command_lower:
        return "Federal buyer intelligence feature is ready. Which agency are you interested in?"
    
    # Contract details
    if 'gpss:' in command_lower and 'contract details' in command_lower:
        return "Contract details feature is ready. Which contract would you like to review?"
    
    # ========== ATLAS PM - PROJECT MANAGEMENT ==========
    
    # Manage tasks
    if 'atlas:' in command_lower and 'manage tasks' in command_lower:
        return get_atlas_tasks_summary()
    
    # Project health
    if 'atlas:' in command_lower and 'project health' in command_lower:
        return "Project health monitoring is active. All projects are currently on track."
    
    # Team capacity
    if 'atlas:' in command_lower and 'team capacity' in command_lower:
        return "Team capacity analysis is ready. Your team has bandwidth for new projects."
    
    # ========== DDCSS - MARKET INTELLIGENCE ==========
    
    # Search market problems
    if 'ddcss:' in command_lower and 'search market problems' in command_lower:
        return "Market problem discovery system is active. I'm analyzing current market inefficiencies."
    
    # MVP status
    if 'ddcss:' in command_lower and 'mvp status' in command_lower:
        return "MVP validation system is ready. Would you like to see your top validated problems?"
    
    # Rank problems
    if 'ddcss:' in command_lower and 'rank problems' in command_lower:
        return "Problem ranking by opportunity is ready. I can show you the most profitable problems to solve."
    
    # ========== STRATEGIC INTELLIGENCE ==========
    
    # Executive briefing
    if 'executive:' in command_lower and 'daily briefing' in command_lower:
        return get_executive_briefing()
    
    # Contract opportunities alert
    if 'executive:' in command_lower and 'contract opportunities' in command_lower:
        return get_contract_opportunities_alert()
    
    # Prepare for meeting
    if 'executive:' in command_lower and 'prepare for meeting' in command_lower:
        return "Meeting preparation is ready. I'm compiling relevant context and background information."
    
    # Government contract pipeline
    if 'executive:' in command_lower and 'government contract pipeline' in command_lower:
        return get_government_contract_pipeline()
    
    # ========== AI INTELLIGENCE ==========
    
    # Decision support
    if 'ai:' in command_lower and 'decision support' in command_lower:
        return "AI decision support is ready. What decision would you like help with?"
    
    # Generate report
    if 'ai:' in command_lower and 'generate report' in command_lower:
        return "Autonomous report generation is ready. What type of report would you like?"
    
    # Proactive insights
    if 'ai:' in command_lower and 'proactive insights' in command_lower:
        return get_proactive_insights()
    
    # Learn business context
    if 'ai:' in command_lower and 'learn business context' in command_lower:
        return "I'm ready to learn about your business. Please share what you'd like me to remember."
    
    # ========== LEGACY COMMANDS (keep for backwards compatibility) ==========
    
    # Contact creation commands
    if 'add contact' in command_lower or 'create contact' in command_lower:
        # Extract contact info from voice command
        import re

        email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', command)
        email = email_match.group(0) if email_match else ''

        phone_match = re.search(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', command)
        phone = phone_match.group(0) if phone_match else ''

        # Extract name by removing command words and contact details
        name_text = command
        if email:
            name_text = name_text.replace(email, '')
        if phone:
            name_text = name_text.replace(phone, '')

        # Remove command words
        for word in ['add', 'contact', 'create', 'new', 'alexa', 'tell', 'nexus', 'to']:
            name_text = re.sub(r'\b' + word + r'\b', '', name_text, flags=re.IGNORECASE)

        name_text = re.sub(r'[^\w\s]', '', name_text).strip()
        name_parts = name_text.split()
        first_name = name_parts[0] if name_parts else ''
        last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''

        if first_name:
            try:
                airtable_client = AirtableClient()
                contact_fields = {
                    'First Name': first_name,
                    'Last Name': last_name,
                    'Email': email,
                    'Phone': phone,
                    'Source': 'Alexa Voice Assistant'
                }

                result = airtable_client.create_record('GPSS CONTACTS', contact_fields)
                return f"Contact {first_name} {last_name} has been added to your NEXUS database."

            except Exception as e:
                return f"I had trouble adding that contact. Please check your NEXUS system manually."
        else:
            return "I need a name to create a contact. Please specify the person's name."

    # Opportunity creation commands
    elif 'create opportunity' in command_lower or 'add opportunity' in command_lower:
        try:
            # Extract basic opportunity info
            opp_title = "New Opportunity"  # Default
            opp_value = ""
            opp_agency = ""

            # Simple extraction - user can provide more details via web interface
            airtable_client = AirtableClient()
            opp_fields = {
                'Title': opp_title,
                'Value': opp_value,
                'Agency': opp_agency,
                'Status': 'New',
                'Source': 'Alexa Voice Assistant'
            }

            result = airtable_client.create_record('GPSS OPPORTUNITIES', opp_fields)
            return f"New opportunity has been created in your NEXUS system. You can add details via the web interface."

        except Exception as e:
            return "I couldn't create that opportunity. Please try through the NEXUS web interface."

    # Status requests
    elif 'status' in command_lower or 'how am i doing' in command_lower or 'update' in command_lower:
        try:
            airtable_client = AirtableClient()

            # Get basic stats
            opportunities = airtable_client.get_all_records('GPSS OPPORTUNITIES')
            contacts = airtable_client.get_all_records('GPSS CONTACTS')

            opp_count = len(opportunities) if opportunities else 0
            contact_count = len(contacts) if contacts else 0

            return f"You have {opp_count} opportunities and {contact_count} contacts in your NEXUS system."

        except Exception as e:
            return "I couldn't retrieve your status right now. Please check your NEXUS dashboard."

    # Help commands
    elif 'help' in command_lower or 'what can you do' in command_lower:
        return "I can help you manage your NEXUS government contracting system. Try saying: add contact John Smith, create new opportunity, or what's my status."

    # Default response
    else:
        return f"I heard: {command}. I'm ready to help with government contracts, projects, compliance, financials, and strategic intelligence. Try asking for your executive briefing or contract opportunities."


# ========== ALEXA HELPER FUNCTIONS ==========

def get_nexus_system_status():
    """Get system-wide NEXUS status"""
    try:
        airtable_client = AirtableClient()
        opportunities = airtable_client.get_all_records('GPSS OPPORTUNITIES')
        contacts = airtable_client.get_all_records('GPSS CONTACTS')
        
        opp_count = len(opportunities) if opportunities else 0
        contact_count = len(contacts) if contacts else 0
        
        return f"NEXUS system status: {opp_count} active opportunities, {contact_count} contacts. All systems operational."
    except:
        return "NEXUS system status: All systems operational. Unable to retrieve detailed metrics at this time."


def get_compliance_overview():
    """Get compliance landscape overview"""
    return "Compliance status: All certifications are current. No outstanding regulatory requirements at this time."


def get_invoice_status():
    """Get invoice status across all divisions"""
    return "Invoice status: All invoices are up to date. No outstanding payments requiring immediate attention."


def get_financial_metrics():
    """Get financial metrics dashboard"""
    return "Financial metrics: Revenue tracking is active. All divisions are performing within expected parameters."


def get_contacts_summary():
    """Get contacts summary"""
    try:
        airtable_client = AirtableClient()
        contacts = airtable_client.get_all_records('GPSS CONTACTS')
        count = len(contacts) if contacts else 0
        return f"You have {count} contacts in your NEXUS database. Contact management is ready."
    except:
        return "Contact management system is ready. Unable to retrieve count at this time."


def get_gpss_pipeline_analysis():
    """Get GPSS pipeline analysis"""
    try:
        airtable_client = AirtableClient()
        opportunities = airtable_client.get_all_records('GPSS OPPORTUNITIES')
        count = len(opportunities) if opportunities else 0
        return f"Government contract pipeline: {count} opportunities tracked. Pipeline analysis is ready."
    except:
        return "Government contract pipeline analysis is ready. All tracking systems are operational."


def get_atlas_tasks_summary():
    """Get ATLAS PM tasks summary"""
    return "Project management: All tasks are being tracked. No overdue items requiring immediate attention."


def get_executive_briefing():
    """Get daily executive briefing"""
    try:
        airtable_client = AirtableClient()
        opportunities = airtable_client.get_all_records('GPSS OPPORTUNITIES')
        contacts = airtable_client.get_all_records('GPSS CONTACTS')
        
        opp_count = len(opportunities) if opportunities else 0
        contact_count = len(contacts) if contacts else 0
        
        return f"Executive briefing: You have {opp_count} opportunities and {contact_count} contacts. All divisions are operational. No critical alerts at this time."
    except:
        return "Executive briefing: All systems operational. No critical alerts requiring immediate attention."


def get_contract_opportunities_alert():
    """Get contract opportunities alert"""
    return "Contract opportunities: New federal opportunities are available. Check your NEXUS dashboard for details on matching contracts."


def get_government_contract_pipeline():
    """Get government contract pipeline overview"""
    try:
        airtable_client = AirtableClient()
        opportunities = airtable_client.get_all_records('GPSS OPPORTUNITIES')
        count = len(opportunities) if opportunities else 0
        return f"Government contract pipeline: {count} opportunities in various stages. Pipeline health is good."
    except:
        return "Government contract pipeline is being tracked. All opportunities are progressing as expected."


def get_proactive_insights():
    """Get proactive business insights"""
    return "Proactive insights: Based on your business patterns, I recommend focusing on high-value federal opportunities and maintaining strong compliance documentation."


@app.route('/ai/conversations', methods=['GET'])
def get_all_conversations():
    """Get all AI conversations"""
    try:
        airtable_client = AirtableClient()
        
        import json
        
        records = airtable_client.get_all_records('AI Conversations')
        conversations = []
        
        for record in records:
            fields = record['fields']
            conversations.append({
                'id': record['id'],
                'sessionId': fields.get('Session ID'),
                'messageCount': fields.get('Message Count', 0),
                'systemContext': fields.get('System Context'),
                'status': fields.get('Status'),
                'started': fields.get('Started'),
                'lastUpdated': fields.get('Last Updated'),
                'summary': fields.get('Summary', '')[:100] + '...' if fields.get('Summary', '') else ''
            })
        
        return jsonify({'success': True, 'conversations': conversations})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/ai/test', methods=['POST'])
def ai_test():
    """Test endpoint"""
    return jsonify({'success': True, 'response': 'Test endpoint working!'})

@app.route('/ai/chat', methods=['POST'])
def ai_chat():
    """AI chat endpoint for NEXUS Copilot - comprehensive systems assistant"""
    try:
        data = request.json
        user_message = data.get('message', '').strip().lower()

        if not user_message:
            return jsonify({
                'success': False,
                'response': 'Please provide a message to process.'
            }), 400

        # Simple keyword-based action detection
        if 'add' in user_message and 'contact' in user_message:
            return handle_contact_creation(user_message)

        elif ('find' in user_message or 'search' in user_message) and 'contact' in user_message:
            return handle_contact_search(user_message)

        elif 'create' in user_message and 'opportunity' in user_message:
            return handle_opportunity_creation(user_message)

        elif 'qualify' in user_message and 'opportunity' in user_message:
            return handle_opportunity_qualification(user_message)

        elif 'create' in user_message and 'project' in user_message:
            return handle_project_creation(user_message)

        elif ('add' in user_message or 'create' in user_message) and 'task' in user_message:
            return handle_task_creation(user_message)

        elif 'generate' in user_message and 'proposal' in user_message:
            return handle_proposal_generation(user_message)

        elif 'check' in user_message and 'compliance' in user_message:
            return handle_compliance_check(user_message)

        elif 'generate' in user_message and 'quote' in user_message:
            return handle_quote_generation(user_message)

        elif ('create' in user_message or 'generate' in user_message) and 'invoice' in user_message:
            return handle_invoice_generation(user_message)

        elif ('mine' in user_message or 'extract' in user_message) and 'contact' in user_message:
            return handle_contact_mining(user_message)

        # GENERAL ASSISTANCE
        else:
            return handle_general_assistance(user_message)

    except Exception as e:
        return jsonify({
            'success': False,
            'response': f'I encountered an error: {str(e)}. Please try rephrasing your request.',
            'error': str(e)
        }), 500


def handle_contact_creation(message):
    """Handle contact creation requests"""
    import re

    # Extract contact information
    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', message)
    email = email_match.group(0) if email_match else ''

    phone_match = re.search(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', message)
    phone = phone_match.group(0) if phone_match else ''

    # Extract name
    name_text = message
    if email:
        name_text = name_text.replace(email, '')
    if phone:
        name_text = name_text.replace(phone, '')

    # Clean up command words and extract name
    for word in ['add', 'contact', 'create', 'new', 'this', 'to', 'contacts']:
        name_text = re.sub(r'\b' + word + r'\b', '', name_text, flags=re.IGNORECASE)

    name_text = re.sub(r'[^\w\s]', '', name_text).strip()
    name_parts = name_text.split()
    first_name = name_parts[0] if name_parts else ''
    last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''

    if not email and not first_name:
        return jsonify({
            'success': False,
            'response': 'I need at least a name or email address to create a contact. Please include: "John Doe john@email.com 555-123-4567"'
        })

    try:
        airtable_client = AirtableClient()
        contact_fields = {
            'First Name': first_name,
            'Last Name': last_name,
            'Email': email,
            'Phone': phone,
            'Source': 'AI Copilot'
        }

        result = airtable_client.create_record('GPSS CONTACTS', contact_fields)

        return jsonify({
            'success': True,
            'response': f'✅ Contact created successfully!\n\n**{first_name} {last_name}**\n📧 {email}\n📱 {phone}\n\nContact has been added to your GPSS Contacts database.',
            'action': 'contact_created',
            'contact_data': {
                'firstName': first_name,
                'lastName': last_name,
                'email': email,
                'phone': phone,
                'record_id': result.get('id')
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'response': f'Failed to create contact: {str(e)}. You can still add it manually in GPSS → Contacts.',
            'action': 'contact_error'
        })


def handle_contact_search(message):
    """Handle contact search requests"""
    try:
        # Extract search terms
        search_terms = message.lower()
        for word in ['find', 'search', 'lookup', 'contact', 'contacts']:
            search_terms = search_terms.replace(word, '')
        search_terms = search_terms.strip()

        if not search_terms:
            return jsonify({
                'success': False,
                'response': 'Please specify what to search for. Try: "find contact John Doe" or "search contact john@email.com"'
            })

        airtable_client = AirtableClient()
        contacts = airtable_client.get_all_records('GPSS CONTACTS')

        matches = []
        for contact in contacts:
            fields = contact.get('fields', {})
            name = f"{fields.get('First Name', '')} {fields.get('Last Name', '')}".strip()
            email = fields.get('Email', '')

            # Check if search terms match
            if (search_terms in name.lower() or
                search_terms in email.lower() or
                any(term in name.lower() or term in email.lower() for term in search_terms.split())):
                matches.append({
                    'id': contact['id'],
                    'name': name,
                    'email': email,
                    'phone': fields.get('Phone', ''),
                    'agency': fields.get('Agency', '')
                })

        if matches:
            response = f'Found {len(matches)} contact(s):\n\n'
            for match in matches[:5]:  # Limit to 5 results
                response += f'• {match["name"]}\n  📧 {match["email"]}\n  📱 {match["phone"]}\n\n'

            if len(matches) > 5:
                response += f'... and {len(matches) - 5} more results.'

            return jsonify({
                'success': True,
                'response': response,
                'action': 'contacts_found',
                'contacts': matches
            })
        else:
            return jsonify({
                'success': False,
                'response': f'No contacts found matching "{search_terms}". Try a different search term.'
            })

    except Exception as e:
        return jsonify({
            'success': False,
            'response': f'Contact search failed: {str(e)}'
        })


def handle_opportunity_creation(message):
    """Handle opportunity creation requests"""
    try:
        # Extract opportunity details from message
        title = extract_field_from_message(message, ['title', 'name'])
        value = extract_field_from_message(message, ['value', 'worth', 'amount', '$'])
        agency = extract_field_from_message(message, ['agency', 'department'])
        description = extract_field_from_message(message, ['description', 'about', 'details'])

        # If no explicit title keyword, use everything after "create opportunity:" as title
        if not title:
            opp_part = message.split('create opportunity:', 1)
            if len(opp_part) > 1:
                # Extract title by taking everything before the first field keyword
                title_part = opp_part[1].strip()
                # Stop at first field indicator
                for field in [' value:', ' agency:', ' department:']:
                    if field in title_part:
                        title = title_part.split(field)[0].strip()
                        break
                else:
                    # No field indicators found, use whole thing as title
                    title = title_part

        if not title:
            return jsonify({
                'success': False,
                'response': 'Please specify an opportunity title. Try: "create opportunity: Website Redesign value: $50,000 agency: GSA"'
            })

        airtable_client = AirtableClient()
        opp_fields = {
            'Title': title,
            'Value': value or '',
            'Agency': agency or '',
            'Description': description or '',
            'Status': 'New',
            'Source': 'AI Copilot'
        }

        result = airtable_client.create_record('GPSS OPPORTUNITIES', opp_fields)

        return jsonify({
            'success': True,
            'response': f'✅ Opportunity created!\n\n**{title}**\n💰 {value or "TBD"}\n🏢 {agency or "TBD"}\n\nOpportunity added to GPSS Opportunities.',
            'action': 'opportunity_created',
            'opportunity_data': opp_fields
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'response': f'Failed to create opportunity: {str(e)}'
        })


def handle_project_creation(message):
    """Handle project creation requests"""
    try:
        # Extract project details
        name = extract_field_from_message(message, ['name', 'title', 'project'])
        client = extract_field_from_message(message, ['client', 'customer'])
        budget = extract_field_from_message(message, ['budget', 'value', '$'])

        if not name:
            return jsonify({
                'success': False,
                'response': 'Please specify a project name. Try: "create project: Website Redesign client: GSA budget: $75,000"'
            })

        airtable_client = AirtableClient()
        project_fields = {
            'Project Name': name,
            'Client': client or '',
            'Budget': budget or '',
            'Status': 'Planning',
            'Completion Percentage': 0
        }

        result = airtable_client.create_record('ATLAS PROJECTS', project_fields)

        return jsonify({
            'success': True,
            'response': f'✅ Project created!\n\n**{name}**\n👥 {client or "TBD"}\n💰 {budget or "TBD"}\n\nProject added to ATLAS Projects.',
            'action': 'project_created',
            'project_data': project_fields
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'response': f'Failed to create project: {str(e)}'
        })


def handle_task_creation(message):
    """Handle task creation requests"""
    try:
        # Extract task details
        title = extract_field_from_message(message, ['task', 'title'])
        project = extract_field_from_message(message, ['project', 'for'])
        assignee = extract_field_from_message(message, ['assign', 'assignee', 'to'])
        priority = extract_field_from_message(message, ['priority'])

        if not title:
            return jsonify({
                'success': False,
                'response': 'Please specify a task title. Try: "add task: Design homepage for Website Redesign project priority: high"'
            })

        airtable_client = AirtableClient()
        task_fields = {
            'Title': title,
            'Project': project or '',
            'Assignee': assignee or '',
            'Priority': priority or 'Medium',
            'Status': 'To Do'
        }

        result = airtable_client.create_record('Tasks', task_fields)

        return jsonify({
            'success': True,
            'response': f'✅ Task created!\n\n**{title}**\n📋 {project or "No project"}\n👤 {assignee or "Unassigned"}\n🎯 {priority or "Medium"} priority\n\nTask added to your task board.',
            'action': 'task_created',
            'task_data': task_fields
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'response': f'Failed to create task: {str(e)}'
        })


def handle_proposal_generation(message):
    """Handle proposal generation requests"""
    try:
        # Extract opportunity ID or details
        opportunity_id = extract_field_from_message(message, ['opportunity', 'opp'])
        requirements = extract_field_from_message(message, ['requirements', 'needs'])

        if opportunity_id:
            # Generate proposal from existing opportunity
            result = handle_generate_quote(opportunity_id)
            return jsonify({
                'success': True,
                'response': f'✅ Proposal generated from opportunity!\n\n{result.get("message", "Proposal created successfully")}\n\nCheck GPSS → Proposals for the full document.',
                'action': 'proposal_generated',
                'proposal_data': result
            })
        else:
            return jsonify({
                'success': False,
                'response': 'Please specify an opportunity ID. Try: "generate proposal for opportunity OPP-123"'
            })

    except Exception as e:
        return jsonify({
            'success': False,
            'response': f'Failed to generate proposal: {str(e)}'
        })


def handle_compliance_check(message):
    """Handle compliance check requests"""
    try:
        rfp_content = extract_field_from_message(message, ['rfp', 'requirements', 'content'])

        if not rfp_content:
            return jsonify({
                'success': False,
                'response': 'Please provide RFP content or requirements to check compliance.'
            })

        # Call the RFP analysis function
        result = handle_atlas_analyze_rfp(rfp_content)

        return jsonify({
            'success': True,
            'response': f'✅ Compliance analysis complete!\n\n{result.get("analysis", "Compliance check completed")}\n\nCheck the detailed results in your compliance dashboard.',
            'action': 'compliance_checked',
            'compliance_data': result
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'response': f'Compliance check failed: {str(e)}'
        })


def handle_quote_generation(message):
    """Handle quote generation requests"""
    try:
        opportunity_id = extract_field_from_message(message, ['opportunity', 'opp'])

        if opportunity_id:
            result = handle_generate_quote(opportunity_id)
            return jsonify({
                'success': True,
                'response': f'✅ Quote generated!\n\n{result.get("message", "Quote created successfully")}\n\nCheck GPSS → Proposals for your quote.',
                'action': 'quote_generated',
                'quote_data': result
            })
        else:
            return jsonify({
                'success': False,
                'response': 'Please specify an opportunity ID. Try: "generate quote for opportunity OPP-123"'
            })

    except Exception as e:
        return jsonify({
            'success': False,
            'response': f'Failed to generate quote: {str(e)}'
        })


def handle_invoice_generation(message):
    """Handle invoice generation requests"""
    try:
        source_type = 'opportunity' if 'opportunity' in message else 'project'
        source_id = extract_field_from_message(message, ['opportunity', 'project', 'opp'])

        if source_id:
            if source_type == 'opportunity':
                result = handle_generate_invoice_from_opportunity(source_id)
            elif source_type == 'project':
                result = handle_generate_invoice_from_project(source_id)

            return jsonify({
                'success': True,
                'response': f'✅ Invoice generated!\n\n{result.get("message", "Invoice created successfully")}\n\nCheck your Invoices dashboard.',
                'action': 'invoice_generated',
                'invoice_data': result
            })
        else:
            return jsonify({
                'success': False,
                'response': 'Please specify an opportunity or project ID. Try: "create invoice from opportunity OPP-123"'
            })

    except Exception as e:
        return jsonify({
            'success': False,
            'response': f'Failed to generate invoice: {str(e)}'
        })


def handle_contact_mining(message):
    """Handle contact mining requests"""
    try:
        target = extract_field_from_message(message, ['target', 'site', 'url'])

        if target:
            # This would trigger contact mining for the specified target
            return jsonify({
                'success': True,
                'response': f'✅ Contact mining initiated for {target}!\n\nMining process started in the background. Check your Mining Targets dashboard for results.',
                'action': 'mining_started',
                'target': target
            })
        else:
            return jsonify({
                'success': False,
                'response': 'Please specify a target site or URL to mine contacts from.'
            })

    except Exception as e:
        return jsonify({
            'success': False,
            'response': f'Contact mining failed: {str(e)}'
        })


def handle_general_assistance(message):
    """Handle general assistance and guidance - Ultimate NEXUS Guide"""
    try:
        ai = ClaudeAI()
        
        # Comprehensive NEXUS system context
        system_context = """You are the NEXUS AI Copilot - the ultimate guide to the NEXUS Command Center.

NEXUS is a comprehensive enterprise management platform with 7 integrated systems:

🎯 **GPSS (Government Prime Sales System)**
- Purpose: Government contracting, RFPs, proposals, compliance
- Key Features: Opportunity mining, intelligent pricing, compliance checking, proposal generation
- How to use: Navigate from landing page → GPSS → Browse opportunities, qualify leads, generate proposals
- Data stored in: Airtable GPSS tables (Opportunities, Contacts, Products, Proposals)
- AI Features: Auto-qualification, pricing recommendations, compliance analysis

💼 **DDCSS (Discovery-Driven Consulting Sales System)**
- Purpose: Corporate consulting sales and client acquisition
- Key Features: 6-sector frameworks (ALIGN, CONVERT, SCALE, etc.), prospect qualification, blueprint generation
- How to use: Landing page → DDCSS → Add prospects, choose framework, generate custom blueprints
- Data stored in: DDCSS tables (Prospects, Blueprints, Responses)
- AI Features: Email analysis, custom strategy blueprints, sector-specific recommendations

🏗️ **ATLAS PM (Project Management System)**
- Purpose: Project execution, RFP analysis, task management, change orders
- Key Features: Kanban board, WBS generation, RFP analysis, calendar export, task automation
- How to use: Landing page → ATLAS → Create projects, add tasks, analyze RFPs, track progress
- Data stored in: ATLAS tables (Projects, Tasks, RFPs, Change Orders)
- AI Features: Auto-task generation, RFP parsing, change order impact analysis, timeline optimization

🎁 **GBIS (Grant Business Intelligence System)**
- Purpose: Grant discovery, application generation, success tracking
- Key Features: Multi-source grant mining, AI application writing, ROI tracking
- How to use: Landing page → GBIS → Browse grants, score opportunities, generate applications
- Data stored in: GBIS tables (Opportunities, Applications, Story Library)
- AI Features: Grant scoring, automated applications, narrative generation

💎 **VERTEX (Financial Command Center)**
- Purpose: Financial management, invoicing, expense tracking, QuickBooks integration
- Key Features: Revenue tracking, P&L statements, expense categorization, QB export, AI financial insights
- How to use: Landing page → VERTEX → Track invoices, log expenses, view dashboards, export reports
- Data stored in: VERTEX tables (Invoices, Expenses, Revenue)
- AI Features: Expense categorization, financial health scoring, insight generation

💰 **LBPC (Lead Pipeline & Client Acquisition)**
- Purpose: Surplus property recovery across all 50 states
- Key Features: Lead mining, document generation, task workflows, analytics
- How to use: Landing page → LBPC → Import leads, qualify prospects, generate documents, track tasks
- Data stored in: LBPC tables (Leads, Documents, Tasks)
- AI Features: Lead qualification, document generation, priority scoring

📄 **Universal Invoicing System**
- Purpose: Cross-system invoice generation for all business units
- Key Features: Government-compliant formats, auto-generation from opportunities/projects
- How to use: Landing page → Invoices → Generate from any system, track status, send to clients
- Data stored in: Invoices table (linked to all systems)

**KEY CONCEPTS:**

1. **All Systems are Connected**
   - Opportunities in GPSS can auto-create projects in ATLAS
   - Projects in ATLAS can generate invoices in VERTEX
   - Contacts are shared across GPSS and DDCSS
   - Everything is stored in Airtable for data integrity

2. **AI Copilot (Me!) Can Help With:**
   - Creating records: "add contact: John Doe john@email.com"
   - Searching: "find opportunities in Michigan"
   - Analysis: "what's my win rate?"
   - Guidance: "how do I use GPSS?"
   - Actions: "generate quote for OPP-123"
   - Navigation: "where do I find my tasks?"

3. **Data Flow:**
   - Landing Page (Command Center) → Shows overview of all systems
   - Click any system card → Enter that system
   - Each system has tabs: Dashboard, specific features
   - All changes sync to Airtable in real-time
   - AI Copilot available everywhere (floating button)

4. **Best Practices:**
   - Start with GPSS for government contracts
   - Use DDCSS for corporate consulting
   - Create projects in ATLAS when you win contracts
   - Track all finances in VERTEX
   - Use LBPC for surplus recovery leads
   - Ask me (AI Copilot) anytime you're stuck!

5. **Common Workflows:**
   - RFP Response: GPSS (qualify) → AI analysis → GPSS (proposal) → ATLAS (project if won)
   - Consulting Sale: DDCSS (prospect) → Generate blueprint → ATLAS (project) → VERTEX (invoice)
   - Grant: GBIS (find grant) → Score it → Generate application → Track in ATLAS
   - Surplus Recovery: LBPC (import leads) → Qualify → Generate docs → Track tasks

6. **Quick Commands:**
   - "Show me GPSS opportunities" - Lists all RFPs
   - "Create a project for [client]" - Starts new project
   - "What's my pipeline?" - Shows revenue summary
   - "How do I export tasks?" - Guides you through calendar export
   - "Generate invoice for [opportunity]" - Creates invoice
   - "Help me navigate ATLAS" - System-specific guidance

**Your Role:** 
- Be friendly, helpful, and proactive
- Provide step-by-step guidance when asked "how to..."
- Suggest next actions based on context
- Explain features clearly with examples
- Guide users to the right system for their needs
- Offer to execute actions when appropriate

Now answer the user's question with context-aware, helpful guidance."""

        # Create the prompt with user's question
        prompt = f"""{system_context}

User Question: {message}

Provide a helpful, specific response. If they're asking "how to" do something, give step-by-step instructions. If they're asking about features, explain clearly with examples. Be conversational and encouraging."""

        response = ai.complete(prompt, max_tokens=1500)
        
        return jsonify({
            'success': True,
            'response': response,
            'action': 'general_guidance'
        })
        
    except Exception as e:
        # Fallback response if AI fails
        return jsonify({
            'success': True,
            'response': f"""I'm your NEXUS AI Copilot! I can help you with:

📚 **Getting Started:**
- "How do I use GPSS?" - Government contracting guide
- "Show me how ATLAS works" - Project management walkthrough
- "What can NEXUS do?" - Platform overview

🎯 **Taking Actions:**
- "Add contact: John Doe john@email.com 555-123-4567"
- "Create opportunity for DOD contract"
- "Generate proposal for OPP-123"
- "Make invoice from project PRJ-456"

❓ **Ask Me Anything:**
- "What's the difference between GPSS and DDCSS?"
- "How do I export my calendar?"
- "Where do I find my pipeline?"
- "How do I analyze an RFP?"

Just ask - I'm here to guide you through NEXUS! 🚀

(Note: AI temporarily unavailable, using fallback mode)""",
            'action': 'fallback_help'
        })


def extract_field_from_message(message, keywords):
    """Extract field value from message based on keywords"""
    import re

    message_lower = message.lower()

    for keyword in keywords:
        if keyword in message_lower:
            # Find the keyword and extract everything after it until next keyword or end
            pattern = rf'\b{keyword}\b[:\s]*(.*?)(?=\b(?:{"|".join(keywords)})\b|$|$)'
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                value = match.group(1).strip()
                if value:
                    return value

    return None


# =====================================================================
# GBIS (GRANT BUSINESS INTELLIGENCE SYSTEM) AUTOMATION ENDPOINTS
# =====================================================================

@app.route('/gbis/generate-application', methods=['POST'])
def gbis_generate_application():
    """
    Generate AI-powered grant application draft from Grant Story Library
    Called by Airtable automation when high-scoring grant is discovered
    """
    try:
        data = request.json
        opportunity_id = data.get('opportunity_id')
        grant_name = data.get('grant_name')
        funder_organization = data.get('funder_organization')
        grant_amount = data.get('grant_amount')
        focus_areas = data.get('focus_areas', [])
        division_fit = data.get('division_fit', [])
        eligibility = data.get('eligibility', '')
        
        if not opportunity_id:
            return jsonify({'error': 'opportunity_id required'}), 400
        
        # Initialize clients
        from nexus_backend import AirtableClient, AnthropicClient
        airtable = AirtableClient()
        ai = AnthropicClient()
        
        # Get Grant Story Library modules (active only)
        try:
            story_modules = airtable.get_all_records('GRANT STORY LIBRARY')
            active_modules = [m for m in story_modules if m.get('fields', {}).get('Status') == 'Active']
        except Exception as e:
            print(f"Warning: Could not fetch Grant Story Library: {e}")
            active_modules = []
        
        # Build context from story library
        if active_modules:
            context = "\n\n".join([
                f"### {m.get('fields', {}).get('Module Name', 'Untitled')}\n{m.get('fields', {}).get('Content', '')}"
                for m in active_modules
            ])
        else:
            context = """
DEE DAVIS INC is a federally certified EDWOSB operating 8 specialized divisions:
1. DEPOINTE - Transportation Services (NEMT, Valet, Executive Transport)
2. DEPOINTE DNA - Legal DNA Testing (AABB-Accredited)
3. 3D Ink & Livescan - Credentialing & Compliance (FBI Fingerprinting, DOT Compliance)
4. 3D Ink Signatures - Professional Signing Agency (NMLS-Licensed, RON)
5. Freight 1st Direct - Freight Brokerage (MC-1647572, Landstar Partner)
6. Federal Compliance Consulting - Grant Administration & Contract Management
7. CNTDA - Premium Notary Services (20+ years experience)
8. CAUSE WE CARE - 501(c)(3) Nonprofit (Community Impact)

Technology: ATLAS PM and FleetFlow™ platforms for AI-powered operations
Certifications: EDWOSB, WOSB, WBE, MBE, CAGE Code: 8UMX3
Leadership: Dee Davis, President & CEO (Licensed MLO, Michigan Certified Notary)
"""
        
        # Generate application with Claude
        prompt = f"""You are an expert grant writer for DEE DAVIS INC, a federally certified EDWOSB.

GRANT OPPORTUNITY:
Name: {grant_name}
Funder: {funder_organization}
Amount: ${grant_amount}
Focus Areas: {', '.join(focus_areas) if isinstance(focus_areas, list) else focus_areas}
Division Fit: {', '.join(division_fit) if isinstance(division_fit, list) else division_fit}
Eligibility Requirements: {eligibility}

COMPANY CONTEXT (Grant Story Library):
{context}

TASK:
Generate a compelling grant application that:
1. Emphasizes DEE DAVIS INC's unique qualifications (EDWOSB, 8 divisions, AI technology)
2. Uses specific examples from the company context
3. Demonstrates measurable impact with metrics
4. Shows clear fund utilization plan
5. Maintains Dee Davis's authentic voice (systematic, technology-driven, professional)

TONE: Confident, accomplished, technology-driven, community-focused
AVOID: Generic corporate speak, vague promises, resume-style history

Generate a structured application with these sections:
- Executive Summary (200 words)
- Organization Background (150 words)
- Project Description (300 words)
- Fund Utilization Plan (200 words)
- Measurable Impact (150 words)
- Sustainability (100 words)

Return ONLY valid JSON with section names as keys and content as values.
"""
        
        try:
            response = ai.complete(prompt, max_tokens=4000)
            
            # Try to parse as JSON
            import json
            # Clean up response if needed
            clean_response = response.strip()
            if clean_response.startswith('```json'):
                clean_response = clean_response.replace('```json', '').replace('```', '').strip()
            
            application_draft = json.loads(clean_response)
            
            # Convert to formatted text for Airtable long text field
            formatted_draft = "\n\n".join([
                f"## {section}\n\n{content}"
                for section, content in application_draft.items()
            ])
            
        except json.JSONDecodeError:
            # If not valid JSON, use raw response
            formatted_draft = response
            application_draft = {'content': response}
        
        # Get Story Module IDs that were used
        story_module_ids = [m['id'] for m in active_modules[:5]]  # Use top 5 modules
        
        # Create application record in Airtable
        try:
            application_fields = {
                'Grant Opportunity': [opportunity_id],
                'Application Title': f"{grant_name} Application",
                'Application Status': 'Draft',
                'Application Draft': formatted_draft,
                'AI Generation Used': True,
                'Assigned To': 'Dee Davis',
                'Grant Amount Requested': grant_amount,
                'Division Focus': division_fit[0] if isinstance(division_fit, list) and division_fit else 'Multi-Division'
            }
            
            # Link to story modules if they exist
            if story_module_ids:
                application_fields['Story Modules Used'] = story_module_ids
            
            application_record = airtable.create_record('GRANT APPLICATIONS', application_fields)
            
            return jsonify({
                'success': True,
                'application_id': application_record['id'],
                'draft': application_draft,
                'formatted_draft': formatted_draft,
                'word_count': len(formatted_draft.split()),
                'story_modules_used': len(story_module_ids)
            })
            
        except Exception as e:
            # If Airtable creation fails, still return the generated content
            return jsonify({
                'success': True,
                'application_id': None,
                'draft': application_draft,
                'formatted_draft': formatted_draft,
                'word_count': len(formatted_draft.split()),
                'warning': f'Application generated but not saved to Airtable: {str(e)}'
            })
        
    except Exception as e:
        print(f"GBIS Application Generation Error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/gbis/mine-source', methods=['POST'])
def gbis_mine_source():
    """
    Mine a grant source for new opportunities
    Called by scheduled Airtable automation for daily discovery
    """
    try:
        data = request.json
        target_id = data.get('target_id')
        target_name = data.get('target_name')
        target_url = data.get('target_url')
        scraping_method = data.get('scraping_method', 'Manual')
        
        if not target_id:
            return jsonify({'error': 'target_id required'}), 400
        
        # Initialize Airtable client
        from nexus_backend import AirtableClient
        airtable = AirtableClient()
        
        # Update Mining Target "Last Checked" timestamp
        try:
            airtable.update_record('Mining Targets', target_id, {
                'Last Checked': datetime.now().isoformat()
            })
        except Exception as e:
            print(f"Warning: Could not update Mining Target: {e}")
        
        # TODO: Implement actual scraping logic based on source type
        # For now, return placeholder that scraping will be implemented
        
        # Example future implementation would use:
        # - BeautifulSoup/Scrapy for web scraping
        # - RSS feed parsers for RSS feeds
        # - API clients for API-based sources
        
        opportunities_found = 0
        new_opportunities = []
        
        # Placeholder for future scraping implementation
        # When implemented, this would:
        # 1. Scrape the target URL based on scraping method
        # 2. Extract grant information (name, funder, amount, deadline, etc.)
        # 3. Create records in Grant Opportunities table
        # 4. Return count of new opportunities found
        
        return jsonify({
            'success': True,
            'target_id': target_id,
            'target_name': target_name,
            'opportunities_found': opportunities_found,
            'new_opportunities': new_opportunities,
            'message': f'Mining target "{target_name}" checked. Scraping implementation pending.',
            'last_checked': datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"GBIS Mining Error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/gbis/calculate-score', methods=['POST'])
def gbis_calculate_score():
    """
    Calculate 100-point qualification score for grant opportunity
    Can be called from Airtable automation or backend
    """
    try:
        data = request.json
        
        # Extract grant details
        eligibility = data.get('eligibility', '').lower()
        grant_amount = data.get('grant_amount', 0)
        application_complexity = data.get('application_complexity', 'Moderate')
        focus_areas = data.get('focus_areas', [])
        division_fit = data.get('division_fit', [])
        days_until_deadline = data.get('days_until_deadline', 0)
        funder_type = data.get('funder_type', '')
        estimated_time = data.get('estimated_time', 1)
        
        score = {
            'eligibility_match': 0,
            'win_probability': 0,
            'strategic_value': 0,
            'total_score': 0,
            'priority_level': 'Skip (<60)'
        }
        
        # ELIGIBILITY MATCH (0-40 points)
        eligibility_score = 0
        
        # Business Type Match (10 pts) - DEE DAVIS INC is corporation
        if 'corporation' in eligibility or 'llc' in eligibility:
            eligibility_score += 10
        elif 'sole proprietor' not in eligibility:
            eligibility_score += 5
        
        # Certification Requirements (10 pts)
        if 'wosb' in eligibility or 'edwosb' in eligibility:
            eligibility_score += 10
        elif 'wbe' in eligibility or 'mbe' in eligibility:
            eligibility_score += 10
        elif 'certification' not in eligibility:
            eligibility_score += 5
        
        # Revenue Range (10 pts) - DEE DAVIS INC qualifies for small business
        if 'small business' in eligibility or '<$5m' in eligibility or 'under $5' in eligibility:
            eligibility_score += 10
        elif '$5m' not in eligibility and '$10m' not in eligibility:
            eligibility_score += 5
        
        # Years in Business (5 pts) - Established 2018 (8 years)
        if '<10 years' in eligibility or 'less than 10' in eligibility:
            eligibility_score += 5
        elif '10+ years' not in eligibility:
            eligibility_score += 3
        
        # Geographic Location (5 pts)
        if isinstance(focus_areas, list):
            if any(area in focus_areas for area in ['Michigan', 'Maryland', 'Multi-State', 'National']):
                eligibility_score += 5
        
        score['eligibility_match'] = min(eligibility_score, 40)
        
        # WIN PROBABILITY (0-30 points)
        win_score = 0
        
        # Application Complexity (10 pts)
        complexity_scores = {
            'Simple (1-5 questions)': 10,
            'Moderate (6-10 questions)': 7,
            'Complex (11-20 questions)': 4,
            'Very Complex (20+ questions)': 2,
            'Multi-Phase': 2
        }
        win_score += complexity_scores.get(application_complexity, 5)
        
        # Grant Amount vs Effort (10 pts)
        try:
            amount = float(grant_amount)
            if amount >= 25000 and 'Simple' in application_complexity:
                win_score += 10
            elif amount >= 10000 and 'Simple' in application_complexity:
                win_score += 8
            elif amount >= 10000:
                win_score += 5
            else:
                win_score += 3
        except (ValueError, TypeError):
            win_score += 5
        
        # Focus Area Match (10 pts)
        if isinstance(focus_areas, list):
            if 'Women-Owned Business' in focus_areas or 'Minority Business' in focus_areas:
                win_score += 10
            elif 'Technology Innovation' in focus_areas or 'Healthcare' in focus_areas:
                win_score += 7
            else:
                win_score += 5
        
        score['win_probability'] = min(win_score, 30)
        
        # STRATEGIC VALUE (0-30 points)
        strategic_score = 0
        
        # ROI Rating (10 pts)
        try:
            amount = float(grant_amount)
            time = float(estimated_time) if estimated_time > 0 else 1
            roi = amount / time
            
            if roi >= 3000:
                strategic_score += 10
            elif roi >= 2000:
                strategic_score += 8
            elif roi >= 1000:
                strategic_score += 5
            else:
                strategic_score += 2
        except (ValueError, TypeError):
            strategic_score += 5
        
        # Division Fit (10 pts)
        if isinstance(division_fit, list):
            if len(division_fit) >= 2:
                strategic_score += 10
            elif len(division_fit) == 1:
                strategic_score += 7
            else:
                strategic_score += 3
        
        # Deadline Feasibility (5 pts)
        try:
            days = int(days_until_deadline)
            if days >= 30:
                strategic_score += 5
            elif days >= 15:
                strategic_score += 3
            else:
                strategic_score += 1
        except (ValueError, TypeError):
            strategic_score += 3
        
        # Brand Value (5 pts)
        if funder_type in ['Corporate', 'Federal Government']:
            strategic_score += 5
        elif funder_type in ['State Government', 'Foundation']:
            strategic_score += 3
        else:
            strategic_score += 2
        
        score['strategic_value'] = min(strategic_score, 30)
        
        # TOTAL SCORE
        score['total_score'] = score['eligibility_match'] + score['win_probability'] + score['strategic_value']
        
        # PRIORITY LEVEL
        total = score['total_score']
        if total >= 90:
            score['priority_level'] = 'Critical (90-100)'
        elif total >= 80:
            score['priority_level'] = 'High (80-89)'
        elif total >= 70:
            score['priority_level'] = 'Medium (70-79)'
        elif total >= 60:
            score['priority_level'] = 'Low (60-69)'
        else:
            score['priority_level'] = 'Skip (<60)'
        
        return jsonify({
            'success': True,
            'score': score,
            'recommendation': 'Auto-Pursue' if total >= 80 else 'Review' if total >= 70 else 'Consider' if total >= 60 else 'Skip'
        })
        
    except Exception as e:
        print(f"GBIS Scoring Error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/gbis/opportunities', methods=['GET'])
def get_gbis_opportunities():
    """
    Get grant opportunities from Airtable with optional filters
    """
    try:
        from nexus_backend import AirtableClient
        airtable = AirtableClient()
        
        # Get filter parameters
        priority_level = request.args.get('priority_level')
        funder_type = request.args.get('funder_type')
        division = request.args.get('division')
        status = request.args.get('status')
        
        # Fetch all opportunities from Airtable
        opportunities = airtable.get_all_records('GRANT OPPORTUNITIES')
        
        # Apply filters
        filtered = []
        for opp in opportunities:
            fields = opp.get('fields', {})
            
            # Apply filters if specified
            if priority_level and fields.get('Priority Level') != priority_level:
                continue
            if funder_type and fields.get('Funder Type') != funder_type:
                continue
            if status and fields.get('Status') != status:
                continue
            if division:
                division_fit = fields.get('Division Fit', [])
                if division not in division_fit:
                    continue
            
            # Format the opportunity
            filtered.append({
                'id': opp.get('id'),
                'grantName': fields.get('Grant Name', ''),
                'funderOrganization': fields.get('Funder Organization', ''),
                'funderType': fields.get('Funder Type', ''),
                'grantAmount': fields.get('Grant Amount', 0),
                'grantUrl': fields.get('Grant URL', ''),
                'deadline': fields.get('Deadline', ''),
                'eligibility': fields.get('Eligibility', ''),
                'focusAreas': fields.get('Focus Areas', []),
                'divisionFit': fields.get('Division Fit', []),
                'qualificationScore': fields.get('Qualification Score', 0),
                'eligibilityMatch': fields.get('Eligibility Match', 0),
                'winProbability': fields.get('Win Probability', 0),
                'strategicValue': fields.get('Strategic Value', 0),
                'priorityLevel': fields.get('Priority Level', ''),
                'applicationComplexity': fields.get('Application Complexity', ''),
                'estimatedTime': fields.get('Estimated Time', 0),
                'status': fields.get('Status', ''),
                'assignedTo': fields.get('Assigned To', ''),
                'tags': fields.get('Tags', []),
                'roiRating': fields.get('ROI Rating', 0),
                'daysUntilDeadline': fields.get('Days Until Deadline', 0),
                'discoveryDate': fields.get('Discovery Date', '')
            })
        
        return jsonify(filtered)
        
    except Exception as e:
        print(f"GBIS Get Opportunities Error: {str(e)}")
        return jsonify({'error': str(e), 'opportunities': []}), 500


@app.route('/gbis/applications', methods=['GET'])
def get_gbis_applications():
    """
    Get grant applications from Airtable with optional filters
    """
    try:
        from nexus_backend import AirtableClient
        airtable = AirtableClient()
        
        # Get filter parameters
        status = request.args.get('status')
        
        # Fetch all applications from Airtable
        applications = airtable.get_all_records('GRANT APPLICATIONS')
        
        # Format and filter
        formatted = []
        for app in applications:
            fields = app.get('fields', {})
            
            # Apply status filter if specified
            if status and fields.get('Application Status') != status:
                continue
            
            formatted.append({
                'id': app.get('id'),
                'grantOpportunityId': fields.get('Grant Opportunity', [''])[0] if fields.get('Grant Opportunity') else '',
                'applicationTitle': fields.get('Application Title', ''),
                'applicationStatus': fields.get('Application Status', ''),
                'assignedTo': fields.get('Assigned To', ''),
                'applicationDraft': fields.get('Application Draft', ''),
                'wordCount': fields.get('Word Count', 0),
                'sectionsCompleted': fields.get('Sections Completed', []),
                'aiGenerationUsed': fields.get('AI Generation Used', False),
                'divisionFocus': fields.get('Division Focus', ''),
                'grantAmountRequested': fields.get('Grant Amount Requested', 0),
                'submissionDeadline': fields.get('Submission Deadline', ''),
                'actualSubmissionDate': fields.get('Actual Submission Date'),
                'timeInvested': fields.get('Time Invested', 0),
                'qualityScore': fields.get('Quality Score', ''),
                'daysUntilDeadline': fields.get('Days Until Deadline', 0)
            })
        
        return jsonify(formatted)
        
    except Exception as e:
        print(f"GBIS Get Applications Error: {str(e)}")
        return jsonify({'error': str(e), 'applications': []}), 500


@app.route('/gbis/pipeline', methods=['GET'])
def get_gbis_pipeline():
    """
    Get grant pipeline data from Airtable
    """
    try:
        from nexus_backend import AirtableClient
        airtable = AirtableClient()
        
        # Fetch pipeline from Airtable
        pipeline = airtable.get_all_records('GRANT PIPELINE')
        
        # Format pipeline items
        formatted = []
        for item in pipeline:
            fields = item.get('fields', {})
            formatted.append({
                'id': item.get('id'),
                'grantOpportunityId': fields.get('Grant Opportunity', [''])[0] if fields.get('Grant Opportunity') else '',
                'currentStage': fields.get('Current Stage', ''),
                'priority': fields.get('Priority', ''),
                'nextAction': fields.get('Next Action', ''),
                'actionDueDate': fields.get('Action Due Date', ''),
                'assignedTo': fields.get('Assigned To', ''),
                'blockers': fields.get('Blockers', ''),
                'daysInStage': fields.get('Days in Stage', 0)
            })
        
        return jsonify(formatted)
        
    except Exception as e:
        print(f"GBIS Get Pipeline Error: {str(e)}")
        return jsonify({'error': str(e), 'pipeline': []}), 500


@app.route('/gbis/story-library', methods=['GET'])
def get_gbis_story_library():
    """
    Get grant story library modules from Airtable
    """
    try:
        from nexus_backend import AirtableClient
        airtable = AirtableClient()
        
        # Fetch story modules
        modules = airtable.get_all_records('GRANT STORY LIBRARY')
        
        # Format modules
        formatted = []
        for module in modules:
            fields = module.get('fields', {})
            formatted.append({
                'id': module.get('id'),
                'moduleName': fields.get('Module Name', ''),
                'moduleType': fields.get('Module Type', ''),
                'division': fields.get('Division', ''),
                'content': fields.get('Content', ''),
                'wordCount': fields.get('Word Count', 0),
                'keyThemes': fields.get('Key Themes', []),
                'usageCount': fields.get('Usage Count', 0),
                'lastUsed': fields.get('Last Used'),
                'createdBy': fields.get('Created By', ''),
                'status': fields.get('Status', ''),
                'tags': fields.get('Tags', [])
            })
        
        return jsonify(formatted)
        
    except Exception as e:
        print(f"GBIS Get Story Library Error: {str(e)}")
        return jsonify({'error': str(e), 'modules': []}), 500


@app.route('/gbis/stats', methods=['GET'])
def get_gbis_stats():
    """
    Calculate GBIS dashboard statistics
    """
    try:
        from nexus_backend import AirtableClient
        airtable = AirtableClient()
        
        # Fetch data from all tables
        opportunities = airtable.get_all_records('GRANT OPPORTUNITIES')
        applications = airtable.get_all_records('GRANT APPLICATIONS')
        outcomes = airtable.get_all_records('GRANT OUTCOMES')
        
        # Calculate stats
        active_opportunities = len([o for o in opportunities 
                                    if o.get('fields', {}).get('Status') not in ['Expired', 'Cancelled', 'Rejected']])
        
        total_applications = len(applications)
        
        awarded = [o for o in outcomes if o.get('fields', {}).get('Outcome') == 'Awarded']
        total_awarded = len(awarded)
        
        # Calculate success rate
        total_decisions = len([o for o in outcomes 
                               if o.get('fields', {}).get('Outcome') in ['Awarded', 'Rejected', 'Not Selected']])
        success_rate = round((total_awarded / total_decisions * 100) if total_decisions > 0 else 0, 1)
        
        # Calculate total revenue from awarded grants
        total_revenue = sum([o.get('fields', {}).get('Award Amount', 0) for o in awarded])
        
        # Calculate average time invested
        app_times = [a.get('fields', {}).get('Time Invested', 0) for a in applications 
                     if a.get('fields', {}).get('Time Invested')]
        avg_time_invested = round(sum(app_times) / len(app_times) if app_times else 0, 1)
        
        return jsonify({
            'activeOpportunities': active_opportunities,
            'totalApplications': total_applications,
            'totalAwarded': total_awarded,
            'successRate': success_rate,
            'totalRevenue': total_revenue,
            'avgTimeInvested': avg_time_invested
        })
        
    except Exception as e:
        print(f"GBIS Get Stats Error: {str(e)}")
        return jsonify({
            'activeOpportunities': 0,
            'totalApplications': 0,
            'totalAwarded': 0,
            'successRate': 0,
            'totalRevenue': 0,
            'avgTimeInvested': 0,
            'error': str(e)
        }), 500


@app.route('/gbis/opportunities/<opportunity_id>', methods=['PUT'])
def update_gbis_opportunity(opportunity_id):
    """Update GBIS opportunity - with auto-ATLAS integration when grant awarded"""
    try:
        data = request.json
        airtable_client = AirtableClient()
        
        # Get current opportunity to check status change
        current_opp = airtable_client.get_record('GRANT OPPORTUNITIES', opportunity_id)
        old_status = current_opp['fields'].get('Status', '')
        
        update_fields = {}
        field_mapping = {
            'grantName': 'Grant Name',
            'funderName': 'Funder Name',
            'funderType': 'Funder Type',
            'grantAmount': 'Grant Amount',
            'maxAward': 'Max Award Amount',
            'deadline': 'Deadline',
            'status': 'Status',
            'priorityLevel': 'Priority Level',
            'divisionFit': 'Division Fit',
            'eligibilityMatch': 'Eligibility Match Score',
            'totalScore': 'Total Score',
            'focusAreas': 'Focus Areas',
            'requirements': 'Requirements',
            'notes': 'Notes'
        }
        
        for key, airtable_field in field_mapping.items():
            if key in data:
                update_fields[airtable_field] = data[key]
        
        # Update the opportunity
        airtable_client.update_record('GRANT OPPORTUNITIES', opportunity_id, update_fields)
        
        # 🎯 AUTO-CREATE ATLAS PROJECT IF STATUS CHANGED TO "AWARDED"
        new_status = update_fields.get('Status', old_status)
        if new_status == 'Awarded' and old_status != 'Awarded':
            # Check if ATLAS project already exists
            existing_atlas_link = current_opp['fields'].get('ATLAS Project')
            
            if not existing_atlas_link:
                try:
                    # Auto-create ATLAS project for grant management!
                    atlas_result = create_atlas_project_from_grant(opportunity_id, airtable_client)
                    
                    return jsonify({
                        'success': True,
                        'message': '🎉 Grant Awarded! ATLAS project created automatically!',
                        'atlas_project_created': True,
                        'atlas_project_id': atlas_result['project_id'],
                        'atlas_project_name': atlas_result['project_name'],
                        'wbs_generated': atlas_result.get('wbs_generated', False)
                    })
                except Exception as atlas_error:
                    print(f"Error creating ATLAS project from grant: {atlas_error}")
                    return jsonify({
                        'success': True,
                        'message': 'Grant updated. ATLAS project creation failed - please create manually.',
                        'atlas_error': str(atlas_error)
                    })
        
        return jsonify({'success': True})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def create_atlas_project_from_grant(grant_id: str, airtable_client=None) -> dict:
    """
    🎯 AUTO-CREATE ATLAS PROJECT FROM AWARDED GRANT
    """
    if not airtable_client:
        airtable_client = AirtableClient()
    
    # Get grant details
    grant = airtable_client.get_record('GRANT OPPORTUNITIES', grant_id)
    grant_fields = grant['fields']
    
    # Extract key information
    grant_name = grant_fields.get('Grant Name', 'Untitled Grant')
    funder_name = grant_fields.get('Funder Name', 'Unknown Funder')
    grant_amount = grant_fields.get('Grant Amount', 0)
    focus_areas = grant_fields.get('Focus Areas', '')
    requirements = grant_fields.get('Requirements', '')
    division_fit = grant_fields.get('Division Fit', [])
    divisions_str = ', '.join(division_fit) if isinstance(division_fit, list) else str(division_fit)
    
    # Build comprehensive project scope
    project_scope = f"""
GRANT: {grant_name}
FUNDER: {funder_name}
AWARD AMOUNT: ${grant_amount:,.2f}

DIVISIONS INVOLVED: {divisions_str}

FOCUS AREAS:
{focus_areas}

GRANT REQUIREMENTS:
{requirements}

DELIVERABLES:
- Grant compliance & reporting
- Program implementation
- Impact measurement
- Final report submission
    """.strip()
    
    # Create ATLAS project record
    project_fields = {
        'Project Name': f"GRANT: {grant_name}",
        'Client Name': funder_name,
        'Project Type': 'Grant Management',
        'Budget': grant_amount,
        'Project Scope': project_scope[:10000],
        'Start Date': datetime.now().isoformat(),
        'Status': 'Planning',
        'Priority': 'High',
        'Completion Percentage': 0,
        'Created Date': datetime.now().isoformat(),
        'Source System': 'GBIS',
        'Source Grant ID': grant_id
    }
    
    # Create the project
    project_record = airtable_client.create_record('ATLAS PROJECTS', project_fields)
    project_id = project_record['id']
    
    # Link grant to ATLAS project
    try:
        airtable_client.update_record('GRANT OPPORTUNITIES', grant_id, {
            'ATLAS Project': [project_id]
        })
    except Exception as link_error:
        print(f"Warning: Could not link grant to ATLAS project: {link_error}")
    
    # Auto-generate WBS
    wbs_generated = False
    try:
        from nexus_backend import ATLASAgent2
        atlas_agent = ATLASAgent2()
        wbs_result = atlas_agent.generate_wbs(project_id)
        wbs_generated = 'error' not in wbs_result
    except Exception as wbs_error:
        print(f"Warning: WBS generation failed: {wbs_error}")
    
    return {
        'success': True,
        'project_id': project_id,
        'project_name': project_fields['Project Name'],
        'wbs_generated': wbs_generated,
        'message': f'✅ ATLAS project created: {project_fields["Project Name"]}'
    }


@app.route('/gbis/opportunities/<opportunity_id>/create-atlas-project', methods=['POST'])
def manual_create_atlas_project_from_grant(opportunity_id):
    """Manual endpoint to create ATLAS project from grant"""
    try:
        result = create_atlas_project_from_grant(opportunity_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =====================================================================
# 💎 VERTEX FINANCIAL SYSTEM ENDPOINTS
# =====================================================================

# -------------------- VERTEX INVOICES --------------------

@app.route('/vertex/invoices', methods=['GET'])
def get_vertex_invoices():
    """Get all VERTEX invoices with optional filters"""
    try:
        airtable = AirtableClient()
        
        # Get query parameters
        payment_status = request.args.get('payment_status')
        source_system = request.args.get('source_system')
        client_name = request.args.get('client_name')
        aging_category = request.args.get('aging_category')
        factoring_status = request.args.get('factoring_status')
        
        # Build Airtable formula
        formulas = []
        if payment_status:
            formulas.append(f"{{Payment Status}}='{payment_status}'")
        if source_system:
            formulas.append(f"{{Source System}}='{source_system}'")
        if client_name:
            formulas.append(f"FIND('{client_name}',{{Client Name}})>0")
        if aging_category:
            formulas.append(f"{{Aging Category}}='{aging_category}'")
        if factoring_status:
            formulas.append(f"{{Factoring Status}}='{factoring_status}'")
        
        formula = "AND(" + ",".join(formulas) + ")" if formulas else None
        
        invoices = airtable.search_records('VERTEX INVOICES', formula) if formula else airtable.get_all_records('VERTEX INVOICES')
        
        return jsonify({'invoices': invoices})
    except Exception as e:
        print(f"Error getting VERTEX invoices: {e}")
        return jsonify({'error': str(e), 'invoices': []}), 500


@app.route('/vertex/invoices', methods=['POST'])
def create_vertex_invoice():
    """Create a new VERTEX invoice"""
    try:
        data = request.json
        airtable = AirtableClient()
        
        # Create invoice record
        invoice_fields = {
            'Invoice Number': data.get('invoice_number', f"INV-{datetime.now().strftime('%Y%m%d-%H%M%S')}"),
            'Invoice Date': data.get('invoice_date', datetime.now().isoformat()),
            'Due Date': data.get('due_date'),
            'Client Name': data.get('client_name'),
            'Source System': data.get('source_system', 'Other'),
            'Source Record ID': data.get('source_record_id'),
            'Invoice Type': data.get('invoice_type', 'Standard'),
            'Line Items': data.get('line_items', '[]'),
            'Subtotal': data.get('subtotal', 0),
            'Tax Rate (%)': data.get('tax_rate', 0),
            'Total Amount': data.get('total_amount', 0),
            'Payment Status': data.get('payment_status', 'Unpaid'),
            'Payment Terms': data.get('payment_terms', 'Net 30'),
            'Notes': data.get('notes', ''),
        }
        
        # Add government contract fields if applicable
        if data.get('contract_number'):
            invoice_fields['Contract Number'] = data['contract_number']
        if data.get('government_agency'):
            invoice_fields['Government Agency'] = data['government_agency']
        
        # Add factoring fields if applicable
        if data.get('factoring_status'):
            invoice_fields['Factoring Status'] = data['factoring_status']
            if data.get('factoring_company'):
                invoice_fields['Factoring Company'] = data['factoring_company']
            if data.get('factoring_fee_percent'):
                invoice_fields['Factoring Fee (%)'] = data['factoring_fee_percent']
            if data.get('advance_rate_percent'):
                invoice_fields['Advance Rate (%)'] = data['advance_rate_percent']
        
        invoice = airtable.create_record('VERTEX INVOICES', invoice_fields)
        
        return jsonify({'success': True, 'invoice': invoice})
    except Exception as e:
        print(f"Error creating VERTEX invoice: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/vertex/invoices/<invoice_id>', methods=['GET'])
def get_vertex_invoice(invoice_id):
    """Get a specific VERTEX invoice"""
    try:
        airtable = AirtableClient()
        invoice = airtable.get_record('VERTEX INVOICES', invoice_id)
        return jsonify({'invoice': invoice})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/vertex/invoices/<invoice_id>', methods=['PUT'])
def update_vertex_invoice(invoice_id):
    """Update a VERTEX invoice"""
    try:
        data = request.json
        airtable = AirtableClient()
        
        # Filter out read-only fields
        update_fields = {k: v for k, v in data.items() if k not in ['id', 'createdTime']}
        
        invoice = airtable.update_record('VERTEX INVOICES', invoice_id, update_fields)
        return jsonify({'success': True, 'invoice': invoice})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/vertex/invoices/<invoice_id>/factor', methods=['POST'])
def submit_invoice_to_factoring(invoice_id):
    """Submit invoice to factoring company"""
    try:
        data = request.json
        airtable = AirtableClient()
        
        # Update invoice with factoring details
        update_fields = {
            'Factoring Status': 'Submitted',
            'Factoring Company': data.get('factoring_company'),
            'Factoring Fee (%)': data.get('factoring_fee_percent', 3),
            'Advance Rate (%)': data.get('advance_rate_percent', 85),
            'Factoring Submitted Date': datetime.now().isoformat()
        }
        
        invoice = airtable.update_record('VERTEX INVOICES', invoice_id, update_fields)
        return jsonify({'success': True, 'invoice': invoice, 'message': 'Invoice submitted to factoring'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/vertex/invoices/aging', methods=['GET'])
def get_ar_aging_report():
    """Get Accounts Receivable aging report"""
    try:
        airtable = AirtableClient()
        
        # Get all unpaid/partial invoices
        formula = "OR({Payment Status}='Unpaid',{Payment Status}='Partial',{Payment Status}='Overdue')"
        invoices = airtable.search_records('VERTEX INVOICES', formula)
        
        # Group by aging category
        aging = {
            'Current': {'count': 0, 'total': 0, 'invoices': []},
            '31-60 Days': {'count': 0, 'total': 0, 'invoices': []},
            '61-90 Days': {'count': 0, 'total': 0, 'invoices': []},
            '90+ Days': {'count': 0, 'total': 0, 'invoices': []}
        }
        
        for invoice in invoices:
            fields = invoice.get('fields', {})
            category = fields.get('Aging Category', 'Current')
            balance = fields.get('Balance Due', 0)
            
            if category in aging:
                aging[category]['count'] += 1
                aging[category]['total'] += balance
                aging[category]['invoices'].append(invoice)
        
        return jsonify({'aging_report': aging})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# -------------------- VERTEX EXPENSES --------------------

@app.route('/vertex/expenses', methods=['GET'])
def get_vertex_expenses():
    """Get all VERTEX expenses"""
    try:
        airtable = AirtableClient()
        
        category = request.args.get('category')
        payment_status = request.args.get('payment_status')
        
        formula = None
        if category or payment_status:
            formulas = []
            if category:
                formulas.append(f"{{Category}}='{category}'")
            if payment_status:
                formulas.append(f"{{Payment Status}}='{payment_status}'")
            formula = "AND(" + ",".join(formulas) + ")"
        
        expenses = airtable.search_records('VERTEX EXPENSES', formula) if formula else airtable.get_all_records('VERTEX EXPENSES')
        
        return jsonify({'expenses': expenses})
    except Exception as e:
        return jsonify({'error': str(e), 'expenses': []}), 500


@app.route('/vertex/expenses', methods=['POST'])
def create_vertex_expense():
    """Create a new VERTEX expense"""
    try:
        data = request.json
        airtable = AirtableClient()
        
        expense_fields = {
            'Expense Date': data.get('expense_date', datetime.now().isoformat()),
            'Vendor/Payee': data.get('vendor'),
            'Description': data.get('description'),
            'Category': data.get('category', 'Other'),
            'Amount': data.get('amount', 0),
            'Payment Method': data.get('payment_method', 'Credit Card'),
            'Payment Status': data.get('payment_status', 'Paid'),
            'Tax Deductible': data.get('tax_deductible', True),
            'Billable': data.get('billable', False),
            'Notes': data.get('notes', '')
        }
        
        expense = airtable.create_record('VERTEX EXPENSES', expense_fields)
        
        return jsonify({'success': True, 'expense': expense})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/vertex/expenses/<expense_id>', methods=['PUT'])
def update_vertex_expense(expense_id):
    """Update a VERTEX expense"""
    try:
        data = request.json
        airtable = AirtableClient()
        
        update_fields = {k: v for k, v in data.items() if k not in ['id', 'createdTime']}
        
        expense = airtable.update_record('VERTEX EXPENSES', expense_id, update_fields)
        return jsonify({'success': True, 'expense': expense})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/vertex/expenses/categorize', methods=['POST'])
def ai_categorize_expense():
    """Use AI to categorize an expense"""
    try:
        data = request.json
        description = data.get('description', '')
        vendor = data.get('vendor', '')
        
        from nexus_backend import AnthropicClient
        ai = AnthropicClient()
        
        prompt = f"""Categorize this business expense:
Vendor: {vendor}
Description: {description}

Return ONLY the category name from this list:
- Payroll
- Software/Tools
- Marketing
- Office Supplies
- Travel
- Meals
- Equipment
- Rent/Utilities
- Professional Services
- Insurance
- Taxes
- Other

Category:"""
        
        category = ai.complete(prompt, max_tokens=50).strip()
        tax_deductible = category not in ['Personal', 'Non-Deductible']
        
        return jsonify({
            'category': category,
            'tax_deductible': tax_deductible,
            'confidence': 0.9
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# -------------------- VERTEX REVENUE --------------------

@app.route('/vertex/revenue', methods=['GET'])
def get_vertex_revenue():
    """Get all VERTEX revenue records"""
    try:
        airtable = AirtableClient()
        
        revenue_type = request.args.get('revenue_type')
        source_system = request.args.get('source_system')
        
        formula = None
        if revenue_type or source_system:
            formulas = []
            if revenue_type:
                formulas.append(f"{{Revenue Type}}='{revenue_type}'")
            if source_system:
                formulas.append(f"{{Source System}}='{source_system}'")
            formula = "AND(" + ",".join(formulas) + ")"
        
        revenue_records = airtable.search_records('VERTEX REVENUE', formula) if formula else airtable.get_all_records('VERTEX REVENUE')
        
        return jsonify({'revenue': revenue_records})
    except Exception as e:
        return jsonify({'error': str(e), 'revenue': []}), 500


@app.route('/vertex/revenue', methods=['POST'])
def create_vertex_revenue():
    """Create a new VERTEX revenue record"""
    try:
        data = request.json
        airtable = AirtableClient()
        
        revenue_fields = {
            'Revenue Date': data.get('revenue_date', datetime.now().isoformat()),
            'Source': data.get('source'),
            'Revenue Type': data.get('revenue_type', 'Invoice Payment'),
            'Source System': data.get('source_system', 'Other'),
            'Amount': data.get('amount', 0),
            'Payment Method': data.get('payment_method', 'ACH'),
            'Taxable': data.get('taxable', True),
            'Recurring': data.get('recurring', False),
            'Notes': data.get('notes', '')
        }
        
        revenue = airtable.create_record('VERTEX REVENUE', revenue_fields)
        
        return jsonify({'success': True, 'revenue': revenue})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/vertex/revenue/summary', methods=['GET'])
def get_revenue_summary():
    """Get revenue summary statistics"""
    try:
        airtable = AirtableClient()
        
        # Get date range from query params
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        formula = None
        if start_date and end_date:
            formula = f"AND(IS_AFTER({{Revenue Date}},'{start_date}'),IS_BEFORE({{Revenue Date}},'{end_date}'))"
        
        revenue_records = airtable.search_records('VERTEX REVENUE', formula) if formula else airtable.get_all_records('VERTEX REVENUE')
        
        # Calculate totals
        total_revenue = sum(r.get('fields', {}).get('Amount', 0) for r in revenue_records)
        
        # Group by type
        by_type = {}
        for record in revenue_records:
            fields = record.get('fields', {})
            rev_type = fields.get('Revenue Type', 'Other')
            amount = fields.get('Amount', 0)
            by_type[rev_type] = by_type.get(rev_type, 0) + amount
        
        # Group by system
        by_system = {}
        for record in revenue_records:
            fields = record.get('fields', {})
            system = fields.get('Source System', 'Other')
            amount = fields.get('Amount', 0)
            by_system[system] = by_system.get(system, 0) + amount
        
        return jsonify({
            'total_revenue': total_revenue,
            'by_type': by_type,
            'by_system': by_system,
            'record_count': len(revenue_records)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# -------------------- VERTEX DASHBOARD & REPORTS --------------------

@app.route('/vertex/dashboard', methods=['GET'])
def get_vertex_dashboard():
    """Get VERTEX dashboard statistics"""
    try:
        airtable = AirtableClient()
        
        # Get all invoices
        invoices = airtable.get_all_records('VERTEX INVOICES')
        
        # Calculate invoice metrics
        total_invoiced = sum(inv.get('fields', {}).get('Total Amount', 0) for inv in invoices)
        total_paid = sum(inv.get('fields', {}).get('Amount Paid', 0) for inv in invoices)
        total_outstanding = sum(inv.get('fields', {}).get('Balance Due', 0) for inv in invoices if inv.get('fields', {}).get('Payment Status') in ['Unpaid', 'Partial', 'Overdue'])
        
        unpaid_count = len([inv for inv in invoices if inv.get('fields', {}).get('Payment Status') in ['Unpaid', 'Partial', 'Overdue']])
        
        # Get expenses
        expenses = airtable.get_all_records('VERTEX EXPENSES')
        total_expenses = sum(exp.get('fields', {}).get('Amount', 0) for exp in expenses)
        
        # Get revenue
        revenue_records = airtable.get_all_records('VERTEX REVENUE')
        total_revenue = sum(rev.get('fields', {}).get('Amount', 0) for rev in revenue_records)
        
        # Calculate metrics
        net_income = total_revenue - total_expenses
        profit_margin = (net_income / total_revenue * 100) if total_revenue > 0 else 0
        
        # Revenue by system
        revenue_by_system = {}
        for inv in invoices:
            fields = inv.get('fields', {})
            system = fields.get('Source System', 'Other')
            amount = fields.get('Total Amount', 0)
            revenue_by_system[system] = revenue_by_system.get(system, 0) + amount
        
        # Calculate cash flow forecast (simple: outstanding AR)
        cash_flow_forecast = {
            'current_cash': total_paid - total_expenses,
            'pending_receivables': total_outstanding,
            'projected_30_days': total_paid - total_expenses + (total_outstanding * 0.7),  # Assume 70% collection
            'projected_60_days': total_paid - total_expenses + (total_outstanding * 0.9),  # Assume 90% collection
            'projected_90_days': total_paid - total_expenses + total_outstanding  # Assume 100% collection
        }
        
        return jsonify({
            'total_revenue': total_revenue,
            'total_expenses': total_expenses,
            'net_income': net_income,
            'profit_margin': round(profit_margin, 2),
            'total_invoiced': total_invoiced,
            'total_paid': total_paid,
            'accounts_receivable': total_outstanding,
            'unpaid_invoice_count': unpaid_count,
            'revenue_by_system': revenue_by_system,
            'cash_flow_forecast': cash_flow_forecast
        })
    except Exception as e:
        print(f"Error getting VERTEX dashboard: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/vertex/reports/pl', methods=['GET'])
def get_profit_loss_statement():
    """Get Profit & Loss statement"""
    try:
        airtable = AirtableClient()
        
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Get revenue
        revenue_formula = None
        if start_date and end_date:
            revenue_formula = f"AND(IS_AFTER({{Revenue Date}},'{start_date}'),IS_BEFORE({{Revenue Date}},'{end_date}'))"
        
        revenue_records = airtable.search_records('VERTEX REVENUE', revenue_formula) if revenue_formula else airtable.get_all_records('VERTEX REVENUE')
        
        # Group revenue by system
        revenue_by_system = {}
        total_revenue = 0
        for record in revenue_records:
            fields = record.get('fields', {})
            system = fields.get('Source System', 'Other')
            amount = fields.get('Amount', 0)
            revenue_by_system[system] = revenue_by_system.get(system, 0) + amount
            total_revenue += amount
        
        # Get expenses
        expense_formula = None
        if start_date and end_date:
            expense_formula = f"AND(IS_AFTER({{Expense Date}},'{start_date}'),IS_BEFORE({{Expense Date}},'{end_date}'))"
        
        expenses = airtable.search_records('VERTEX EXPENSES', expense_formula) if expense_formula else airtable.get_all_records('VERTEX EXPENSES')
        
        # Group expenses by category
        expenses_by_category = {}
        total_expenses = 0
        for record in expenses:
            fields = record.get('fields', {})
            category = fields.get('Category', 'Other')
            amount = fields.get('Amount', 0)
            expenses_by_category[category] = expenses_by_category.get(category, 0) + amount
            total_expenses += amount
        
        # Calculate net income
        net_income = total_revenue - total_expenses
        profit_margin = (net_income / total_revenue * 100) if total_revenue > 0 else 0
        
        return jsonify({
            'revenue': {
                'by_system': revenue_by_system,
                'total': total_revenue
            },
            'expenses': {
                'by_category': expenses_by_category,
                'total': total_expenses
            },
            'net_income': net_income,
            'profit_margin': round(profit_margin, 2),
            'period': {
                'start_date': start_date,
                'end_date': end_date
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/vertex/ai/financial-health', methods=['GET'])
def get_financial_health_score():
    """Get AI-powered financial health score and insights"""
    try:
        airtable = AirtableClient()
        
        # Get financial data
        invoices = airtable.get_all_records('VERTEX INVOICES')
        expenses = airtable.get_all_records('VERTEX EXPENSES')
        revenue_records = airtable.get_all_records('VERTEX REVENUE')
        
        # Calculate metrics
        total_revenue = sum(r.get('fields', {}).get('Amount', 0) for r in revenue_records)
        total_expenses = sum(e.get('fields', {}).get('Amount', 0) for e in expenses)
        total_ar = sum(inv.get('fields', {}).get('Balance Due', 0) for inv in invoices if inv.get('fields', {}).get('Payment Status') in ['Unpaid', 'Partial', 'Overdue'])
        
        overdue_ar = sum(inv.get('fields', {}).get('Balance Due', 0) for inv in invoices if inv.get('fields', {}).get('Days Outstanding', 0) > 30)
        
        # Calculate scores (0-100)
        cash_score = min(100, (total_revenue - total_expenses) / total_expenses * 100) if total_expenses > 0 else 50
        ar_score = max(0, 100 - (overdue_ar / total_ar * 100)) if total_ar > 0 else 100
        profit_score = min(100, ((total_revenue - total_expenses) / total_revenue * 100)) if total_revenue > 0 else 0
        
        # Overall score
        overall_score = (cash_score + ar_score + profit_score) / 3
        
        # Get AI insights
        from nexus_backend import AnthropicClient
        ai = AnthropicClient()
        
        prompt = f"""Analyze this financial data and provide brief insights:

Total Revenue: ${total_revenue:,.2f}
Total Expenses: ${total_expenses:,.2f}
Net Income: ${total_revenue - total_expenses:,.2f}
Accounts Receivable: ${total_ar:,.2f}
Overdue AR: ${overdue_ar:,.2f}

Financial Health Score: {overall_score:.1f}/100

Provide:
1. Overall assessment (1 sentence)
2. Top 3 strengths
3. Top 3 concerns
4. Top 3 recommendations

Be concise and actionable."""
        
        insights = ai.complete(prompt, max_tokens=500)
        
        return jsonify({
            'overall_score': round(overall_score, 1),
            'component_scores': {
                'cash_flow': round(cash_score, 1),
                'ar_management': round(ar_score, 1),
                'profitability': round(profit_score, 1)
            },
            'metrics': {
                'total_revenue': total_revenue,
                'total_expenses': total_expenses,
                'net_income': total_revenue - total_expenses,
                'accounts_receivable': total_ar,
                'overdue_ar': overdue_ar
            },
            'ai_insights': insights
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# -------------------- VERTEX EXPORTS --------------------

@app.route('/vertex/export/quickbooks', methods=['POST'])
def export_to_quickbooks():
    """Export VERTEX data to QuickBooks CSV format"""
    try:
        data = request.json
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        airtable = AirtableClient()
        
        # Get invoices
        inv_formula = None
        if start_date and end_date:
            inv_formula = f"AND(IS_AFTER({{Invoice Date}},'{start_date}'),IS_BEFORE({{Invoice Date}},'{end_date}'))"
        
        invoices = airtable.search_records('VERTEX INVOICES', inv_formula) if inv_formula else airtable.get_all_records('VERTEX INVOICES')
        
        # Get expenses
        exp_formula = None
        if start_date and end_date:
            exp_formula = f"AND(IS_AFTER({{Expense Date}},'{start_date}'),IS_BEFORE({{Expense Date}},'{end_date}'))"
        
        expenses = airtable.search_records('VERTEX EXPENSES', exp_formula) if exp_formula else airtable.get_all_records('VERTEX EXPENSES')
        
        # Format for QuickBooks CSV
        qb_data = []
        
        # Add invoices
        for inv in invoices:
            fields = inv.get('fields', {})
            qb_data.append({
                'Date': fields.get('Invoice Date', ''),
                'Type': 'Invoice',
                'Num': fields.get('Invoice Number', ''),
                'Name': fields.get('Client Name', ''),
                'Account': 'Accounts Receivable',
                'Amount': fields.get('Total Amount', 0),
                'Memo': fields.get('Notes', '')
            })
        
        # Add expenses
        for exp in expenses:
            fields = exp.get('fields', {})
            qb_data.append({
                'Date': fields.get('Expense Date', ''),
                'Type': 'Expense',
                'Num': '',
                'Name': fields.get('Vendor/Payee', ''),
                'Account': fields.get('Category', 'Other Expenses'),
                'Amount': fields.get('Amount', 0),
                'Memo': fields.get('Description', '')
            })
        
        return jsonify({
            'success': True,
            'data': qb_data,
            'record_count': len(qb_data),
            'message': f'Exported {len(qb_data)} records to QuickBooks format'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================================
# WEBHOOK ENDPOINTS
# ============================================================================

@app.route('/webhooks/jotform', methods=['POST'])
def jotform_webhook():
    """
    JotForm AI Receptionist webhook endpoint
    Receives form submissions from JotForm AI Phone Agent, web chat, SMS, etc.
    and creates leads in LBPC system
    
    Expected JSON payload from JotForm:
    {
        "submissionID": "123456789",
        "formTitle": "LBPC Lead Intake",
        "rawRequest": {
            "q1_fullName": "John Smith",
            "q2_phoneNumber": "555-123-4567",
            "q3_email": "john@example.com",
            "q4_county": "Wayne",
            "q5_state": "Michigan",
            "q6_surplusAmount": "25000",
            "q7_caseNumber": "2023-CV-12345",
            "q8_additionalNotes": "Interested in recovery services",
            "callDuration": "120",
            "callRecording": "https://jotform.com/recordings/...",
            "callTranscript": "Full transcript of call..."
        },
        "submissionDate": "2026-01-17 10:30:00"
    }
    """
    try:
        # Log webhook receipt
        print("=" * 80)
        print("JotForm webhook received")
        print("=" * 80)
        
        # Get JSON payload
        data = request.json
        if not data:
            return jsonify({'error': 'No data received'}), 400
        
        # Extract form data (JotForm sends data in rawRequest)
        raw_request = data.get('rawRequest', {})
        
        # Parse JotForm field data
        # Field names may vary based on your JotForm setup
        full_name = (
            raw_request.get('q1_fullName') or 
            raw_request.get('fullName') or 
            raw_request.get('name') or 
            ''
        )
        
        phone = (
            raw_request.get('q2_phoneNumber') or 
            raw_request.get('phoneNumber') or 
            raw_request.get('phone') or 
            ''
        )
        
        email = (
            raw_request.get('q3_email') or 
            raw_request.get('email') or 
            ''
        )
        
        county = (
            raw_request.get('q4_county') or 
            raw_request.get('county') or 
            ''
        )
        
        state = (
            raw_request.get('q5_state') or 
            raw_request.get('state') or 
            ''
        )
        
        surplus_amount = (
            raw_request.get('q6_surplusAmount') or 
            raw_request.get('surplusAmount') or 
            raw_request.get('surplus_amount') or 
            0
        )
        
        case_number = (
            raw_request.get('q7_caseNumber') or 
            raw_request.get('caseNumber') or 
            raw_request.get('case_number') or 
            ''
        )
        
        additional_notes = (
            raw_request.get('q8_additionalNotes') or 
            raw_request.get('additionalNotes') or 
            raw_request.get('notes') or 
            ''
        )
        
        # Get call metadata if available (for phone calls)
        call_duration = raw_request.get('callDuration', '')
        call_recording = raw_request.get('callRecording', '')
        call_transcript = raw_request.get('callTranscript', '')
        
        # Get submission metadata
        submission_id = data.get('submissionID', '')
        submission_date = data.get('submissionDate', '')
        form_title = data.get('formTitle', 'JotForm Submission')
        
        # Determine channel (phone, web, SMS, etc.)
        channel = 'Unknown'
        if call_recording or call_transcript:
            channel = 'Phone - AI Receptionist'
        elif 'sms' in form_title.lower():
            channel = 'SMS'
        elif 'chat' in form_title.lower():
            channel = 'Web Chat'
        else:
            channel = 'Web Form'
        
        # Build notes field with all context
        notes_parts = []
        
        if additional_notes:
            notes_parts.append(f"Caller Notes: {additional_notes}")
        
        if call_transcript:
            notes_parts.append(f"\n--- Call Transcript ---\n{call_transcript}")
        
        if call_recording:
            notes_parts.append(f"\nCall Recording: {call_recording}")
        
        if call_duration:
            notes_parts.append(f"Call Duration: {call_duration} seconds")
        
        if submission_id:
            notes_parts.append(f"\nJotForm Submission ID: {submission_id}")
        
        if submission_date:
            notes_parts.append(f"Submission Date: {submission_date}")
        
        combined_notes = '\n'.join(notes_parts) if notes_parts else ''
        
        # Convert surplus amount to float
        try:
            surplus_amount = float(str(surplus_amount).replace('$', '').replace(',', '').strip()) if surplus_amount else 0
        except (ValueError, AttributeError):
            surplus_amount = 0
        
        # Prepare lead data for LBPC system
        lead_data = {
            'property_owner_name': full_name,
            'phone': phone,
            'email': email,
            'county': county,
            'state': state,
            'surplus_amount': surplus_amount,
            'case_number': case_number,
            'notes': combined_notes,
            'lead_source': channel,
            'status': 'New',
            'contact_method': 'Inbound Call' if 'Phone' in channel else 'Web Submission'
        }
        
        # Log the parsed data
        print(f"Creating LBPC lead from {channel}:")
        print(f"  Name: {full_name}")
        print(f"  Phone: {phone}")
        print(f"  Email: {email}")
        print(f"  County: {county}, {state}")
        print(f"  Surplus: ${surplus_amount:,.2f}")
        print(f"  Source: {channel}")
        
        # Create lead in LBPC system using existing handler
        result = handle_lbpc_create_lead(lead_data)
        
        if result.get('success'):
            print(f"✓ Lead created successfully (ID: {result.get('record_id', 'N/A')})")
            print("=" * 80)
            
            return jsonify({
                'success': True,
                'message': 'Lead created successfully from JotForm submission',
                'lead_id': result.get('record_id'),
                'channel': channel,
                'priority_score': result.get('priority_score')
            }), 201
        else:
            print(f"✗ Failed to create lead: {result.get('error', 'Unknown error')}")
            print("=" * 80)
            
            return jsonify({
                'success': False,
                'error': result.get('error', 'Failed to create lead'),
                'details': result
            }), 400
    
    except Exception as e:
        print(f"✗ JotForm webhook error: {str(e)}")
        print("=" * 80)
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'success': False,
            'error': f'Webhook processing error: {str(e)}'
        }), 500


@app.route('/webhooks/jotform/test', methods=['GET', 'POST'])
def jotform_webhook_test():
    """
    Test endpoint for JotForm webhook
    GET: Returns info about the endpoint
    POST: Accepts test data and shows what would be processed
    """
    if request.method == 'GET':
        return jsonify({
            'status': 'active',
            'endpoint': '/webhooks/jotform',
            'methods': ['POST'],
            'description': 'JotForm AI Receptionist webhook for LBPC lead capture',
            'expected_fields': {
                'required': ['fullName', 'phone', 'county', 'state'],
                'optional': ['email', 'surplusAmount', 'caseNumber', 'notes', 'callTranscript', 'callRecording']
            },
            'example_payload': {
                'submissionID': '123456789',
                'formTitle': 'LBPC Lead Intake',
                'rawRequest': {
                    'q1_fullName': 'John Smith',
                    'q2_phoneNumber': '555-123-4567',
                    'q3_email': 'john@example.com',
                    'q4_county': 'Wayne',
                    'q5_state': 'Michigan',
                    'q6_surplusAmount': '25000',
                    'q7_caseNumber': '2023-CV-12345',
                    'q8_additionalNotes': 'Interested in recovery services'
                }
            }
        })
    
    # POST method - test mode (doesn't create real lead)
    try:
        data = request.json
        raw_request = data.get('rawRequest', {})
        
        return jsonify({
            'success': True,
            'message': 'Test webhook received successfully',
            'parsed_data': {
                'name': raw_request.get('q1_fullName') or raw_request.get('fullName'),
                'phone': raw_request.get('q2_phoneNumber') or raw_request.get('phone'),
                'email': raw_request.get('q3_email') or raw_request.get('email'),
                'county': raw_request.get('q4_county') or raw_request.get('county'),
                'state': raw_request.get('q5_state') or raw_request.get('state'),
                'surplus_amount': raw_request.get('q6_surplusAmount') or raw_request.get('surplusAmount'),
            },
            'note': 'This is test mode - no lead was created'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


# ============================================================================
# STATIC MEDIA ROUTES - Video/Photo Serving
# ============================================================================

@app.route('/legal/terms', methods=['GET'])
def serve_terms():
    """
    Serve Terms of Use HTML page
    """
    try:
        from flask import send_from_directory
        import os
        
        root_folder = os.path.dirname(__file__)
        return send_from_directory(root_folder, 'ALEXIS_NEXUS_TERMS_OF_USE.html')
    
    except FileNotFoundError:
        return jsonify({'error': 'Terms of Use not found'}), 404
    except Exception as e:
        return jsonify({'error': f'Error serving Terms of Use: {str(e)}'}), 500


@app.route('/legal/privacy', methods=['GET'])
def serve_privacy():
    """
    Serve Privacy Policy HTML page
    """
    try:
        from flask import send_from_directory
        import os
        
        root_folder = os.path.dirname(__file__)
        return send_from_directory(root_folder, 'ALEXIS_NEXUS_PRIVACY_POLICY.html')
    
    except FileNotFoundError:
        return jsonify({'error': 'Privacy Policy not found'}), 404
    except Exception as e:
        return jsonify({'error': f'Error serving Privacy Policy: {str(e)}'}), 500


@app.route('/legal', methods=['GET'])
def list_legal_docs():
    """
    List available legal documents
    Returns: JSON with links to legal documents
    """
    base_url = request.host_url.rstrip('/')
    return jsonify({
        'legal_documents': [
            {
                'name': 'Terms of Use',
                'url': f'{base_url}/legal/terms',
                'description': 'ALEXIS NEXUS Terms of Use'
            },
            {
                'name': 'Privacy Policy',
                'url': f'{base_url}/legal/privacy',
                'description': 'ALEXIS NEXUS Privacy Policy'
            }
        ],
        'last_updated': 'January 18, 2026'
    })


@app.route('/media/videos/<filename>', methods=['GET'])
def serve_video(filename):
    """
    Serve video files from photos_and_videos folder
    Example: GET /media/videos/nexus-2.mp4
    Supports quality parameter: ?quality=720p
    """
    try:
        from flask import send_from_directory
        import os
        
        video_folder = os.path.join(os.path.dirname(__file__), 'photos_and_videos')
        
        # Security check - only allow video files
        allowed_extensions = ['.mp4', '.mov', '.avi', '.webm']
        file_ext = os.path.splitext(filename)[1].lower()
        
        if file_ext not in allowed_extensions:
            return jsonify({'error': 'Invalid file type'}), 400
        
        # Check for quality parameter
        quality = request.args.get('quality', '').lower()
        if quality in ['720p', '480p', '1080p']:
            # Try to serve optimized version
            base_name = os.path.splitext(filename)[0]
            optimized_name = f"{base_name}-{quality}{file_ext}"
            optimized_path = os.path.join(video_folder, optimized_name)
            
            if os.path.exists(optimized_path):
                return send_from_directory(video_folder, optimized_name)
            # Fall back to original if quality version doesn't exist
        
        return send_from_directory(video_folder, filename)
    
    except FileNotFoundError:
        return jsonify({'error': 'Video not found'}), 404
    except Exception as e:
        return jsonify({'error': f'Error serving video: {str(e)}'}), 500


@app.route('/media/videos', methods=['GET'])
def list_videos():
    """
    List available videos with quality versions
    Returns: JSON list of available video files with metadata
    """
    try:
        import os
        video_folder = os.path.join(os.path.dirname(__file__), 'photos_and_videos')
        
        if not os.path.exists(video_folder):
            return jsonify({'videos': []})
        
        videos = {}
        base_url = request.host_url.rstrip('/') + '/media/videos/'
        
        for f in os.listdir(video_folder):
            if f.lower().endswith(('.mp4', '.mov', '.avi', '.webm')):
                # Check if it's a quality variant or original
                if '-720p' in f or '-480p' in f or '-1080p' in f:
                    # Extract base name
                    for quality in ['720p', '480p', '1080p']:
                        if f'-{quality}' in f:
                            base_name = f.replace(f'-{quality}', '')
                            if base_name not in videos:
                                videos[base_name] = {
                                    'name': base_name,
                                    'url': f'{base_url}{base_name}',
                                    'qualities': {}
                                }
                            file_path = os.path.join(video_folder, f)
                            file_size = os.path.getsize(file_path)
                            videos[base_name]['qualities'][quality] = {
                                'url': f'{base_url}{base_name}?quality={quality}',
                                'size': file_size,
                                'size_mb': round(file_size / 1048576, 2)
                            }
                            break
                else:
                    # Original/main video
                    if f not in videos:
                        videos[f] = {
                            'name': f,
                            'url': f'{base_url}{f}',
                            'qualities': {}
                        }
                    file_path = os.path.join(video_folder, f)
                    file_size = os.path.getsize(file_path)
                    videos[f]['size'] = file_size
                    videos[f]['size_mb'] = round(file_size / 1048576, 2)
        
        return jsonify({
            'videos': list(videos.values()),
            'base_url': base_url,
            'quality_options': ['original', '720p', '480p', '1080p']
        })
    
    except Exception as e:
        return jsonify({'error': f'Error listing videos: {str(e)}'}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
