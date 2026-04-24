"""
NEXUS Backend - DEE DAVIS INC
Complete AI-powered business automation system
"""

import os
import json
import time
import anthropic
import requests
from pyairtable import Api
from datetime import datetime, timedelta
import re
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# =====================================================================
# CONFIGURATION
# =====================================================================

class Config:
    """Configuration from environment variables"""

    @classmethod
    def get_anthropic_key(cls):
        return os.environ.get('ANTHROPIC_API_KEY', '')

    @classmethod
    def get_airtable_key(cls):
        return os.environ.get('AIRTABLE_API_KEY', '')

    @classmethod
    def get_airtable_base_id(cls):
        return os.environ.get('AIRTABLE_BASE_ID', '')
    
    @classmethod
    def get_sam_gov_key(cls):
        return os.environ.get('SAM_GOV_API_KEY', '')
    
    @classmethod
    def get_govcon_key(cls):
        return os.environ.get('GOVCON_API_KEY', '')

    @classmethod
    def validate(cls):
        """Validate all required credentials are present"""
        if not cls.get_anthropic_key():
            raise ValueError("ANTHROPIC_API_KEY not set")
        if not cls.get_airtable_key():
            raise ValueError("AIRTABLE_API_KEY not set")
        return True

    # For backward compatibility - these will be updated when accessed
    @property
    def ANTHROPIC_API_KEY(self):
        return os.environ.get('ANTHROPIC_API_KEY', '')

    @property
    def AIRTABLE_API_KEY(self):
        return os.environ.get('AIRTABLE_API_KEY', '')

    @property
    def AIRTABLE_BASE_ID(self):
        return os.environ.get('AIRTABLE_BASE_ID', '')

# =====================================================================
# AIRTABLE CLIENT
# =====================================================================

class AirtableClient:
    """Handle all Airtable operations"""
    
    def __init__(self):
        self.api = Api(os.environ.get('AIRTABLE_API_KEY', ''))
        self.base_id = os.environ.get('AIRTABLE_BASE_ID', '')
        
    def get_table(self, table_name: str):
        """Get a specific table"""
        return self.api.table(self.base_id, table_name)
    
    def create_record(self, table_name: str, fields: Dict):
        """Create a new record"""
        table = self.get_table(table_name)
        return table.create(fields)
    
    def update_record(self, table_name: str, record_id: str, fields: Dict):
        """Update existing record"""
        table = self.get_table(table_name)
        return table.update(record_id, fields)
    
    def get_record(self, table_name: str, record_id: str):
        """Get a single record by ID"""
        table = self.get_table(table_name)
        return table.get(record_id)
    
    def delete_record(self, table_name: str, record_id: str):
        """Delete a record by ID"""
        table = self.get_table(table_name)
        return table.delete(record_id)
    
    def get_all_records(self, table_name: str, **kwargs):
        """Get all records from a table"""
        table = self.get_table(table_name)
        return table.all(**kwargs)
    
    def search_records(self, table_name: str, formula: str):
        """Search records with formula"""
        table = self.get_table(table_name)
        return table.all(formula=formula)

# =====================================================================
# ANTHROPIC CLIENT
# =====================================================================

class AnthropicClient:
    """Handle all Claude AI operations"""

    def __init__(self):
        # Simple initialization without custom http client to avoid proxy issues
        self.client = anthropic.Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY', ''))
        self.model = "claude-sonnet-4-20250514"
    
    def complete(self, prompt: str, max_tokens: int = 4000) -> str:
        """Get completion from Claude"""
        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text

# =====================================================================
# WORKFLOW MANAGER - Track opportunity workflow stages
# =====================================================================

class WorkflowManager:
    """Manage workflow stages and transitions for opportunities"""
    
    def __init__(self):
        self.airtable = AirtableClient()
        
    def get_workflow_queues(self):
        """Get all opportunities organized by workflow stage"""
        try:
            # Get all opportunities
            opportunities_table = self.airtable.get_table('GPSS Opportunities')
            all_opps = opportunities_table.all()
            
            # Initialize queues
            queues = {
                'needsReview': [],
                'findSuppliers': [],
                'requestQuotes': [],
                'awaitingQuotes': [],
                'readyToPrice': [],
                'generateProposal': [],
                'finalReview': [],
                'submitted': []
            }
            
            # Sort opportunities into queues based on workflow status
            for opp in all_opps:
                fields = opp['fields']
                # Check both 'Workflow Status' and 'Status' fields (Status takes precedence)
                status = fields.get('Status') or fields.get('Workflow Status', 'Needs Review')
                status_lower = status.lower().replace(' ', '_') if status else 'needs_review'
                
                # Skip "Skipped" opportunities - they don't show in workflow
                if status_lower == 'skipped':
                    continue

                # Determine queue based on status - STATUS TAKES PRIORITY over Name check
                if status_lower in ['find_suppliers', 'find suppliers']:
                    queues['findSuppliers'].append(opp)
                elif status_lower in ['request_quotes', 'request quotes', 'requesting_quotes']:
                    queues['requestQuotes'].append(opp)
                elif status_lower in ['awaiting_quotes', 'awaiting quotes']:
                    queues['awaitingQuotes'].append(opp)
                elif status_lower in ['ready_to_price', 'ready to price']:
                    queues['readyToPrice'].append(opp)
                elif status_lower in ['generate_proposal', 'generate proposal']:
                    queues['generateProposal'].append(opp)
                elif status_lower in ['final_review', 'final review']:
                    queues['finalReview'].append(opp)
                elif status_lower in ['submitted']:
                    queues['submitted'].append(opp)
                else:
                    # Default to needsReview for unknown or empty status
                    # Also put unnamed opportunities here
                    queues['needsReview'].append(opp)
            
            return {
                'success': True,
                'queues': queues,
                'counts': {
                    'needsReview': len(queues['needsReview']),
                    'findSuppliers': len(queues['findSuppliers']),
                    'requestQuotes': len(queues['requestQuotes']),
                    'awaitingQuotes': len(queues['awaitingQuotes']),
                    'readyToPrice': len(queues['readyToPrice']),
                    'generateProposal': len(queues['generateProposal']),
                    'finalReview': len(queues['finalReview']),
                    'submitted': len(queues['submitted'])
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'queues': {},
                'counts': {}
            }
    
    def review_opportunity(self, opportunity_id: str, name: str, decision: str, notes: str = ''):
        """Review and name an opportunity, move to next stage.
        
        Uses only fields known to exist in GPSS Opportunities.
        Falls back gracefully if optional fields don't exist.
        """
        try:
            opportunities_table = self.airtable.get_table('GPSS Opportunities')
            
            new_status = 'Find Suppliers' if decision == 'pursue' else 'Skipped'
            
            # Build updates with all possible status field names
            updates = {
                'Name': name,
                'Notes': f'[{decision.upper()}] {notes}' if notes else f'[{decision.upper()}]',
                'Status': new_status,
                'Workflow Status': new_status,
            }
            
            if decision == 'pursue':
                updates['Priority'] = 'High'
                updates['Source Status'] = 'Pursuing'
            else:
                updates['Priority'] = 'Low'
                updates['Source Status'] = 'Skipped'
            
            print(f"[WORKFLOW] Updating opportunity {opportunity_id} with: {updates}")
            
            # Try full update first
            update_success = False
            try:
                result = opportunities_table.update(opportunity_id, updates)
                print(f"[WORKFLOW] Full update success: {result}")
                update_success = True
            except Exception as field_err:
                print(f"[WORKFLOW] Full update failed: {field_err}")
                # Try without 'Workflow Status' (in case that field doesn't exist)
                try:
                    fallback_updates = {
                        'Name': name,
                        'Notes': f'[{decision.upper()}] {notes}' if notes else f'[{decision.upper()}]',
                        'Status': new_status,
                    }
                    if decision == 'pursue':
                        fallback_updates['Priority'] = 'High'
                    result = opportunities_table.update(opportunity_id, fallback_updates)
                    print(f"[WORKFLOW] Fallback update success: {result}")
                    update_success = True
                except Exception as fallback_err:
                    print(f"[WORKFLOW] Fallback update also failed: {fallback_err}")
                    # Last resort: just update Name
                    result = opportunities_table.update(opportunity_id, {'Name': name})
                    print(f"[WORKFLOW] Name-only update: {result}")
            
            return {
                'success': True,
                'message': f'Opportunity reviewed: {name}',
                'newStatus': new_status,
                'updated': update_success
            }
            
        except Exception as e:
            print(f"[WORKFLOW] review_opportunity ERROR: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def identify_suppliers(self, opportunity_id: str, supplier_ids: List[str]):
        """Link suppliers to opportunity"""
        try:
            opportunities_table = self.airtable.get_table('GPSS Opportunities')
            
            updates = {
                'Source Status': 'Requesting Quotes',
                'Workflow Status': 'Request Quotes',
                'Status': 'Request Quotes',
                'Notes': f'Linked {len(supplier_ids)} suppliers on {datetime.now().strftime("%Y-%m-%d")}',
            }

            try:
                opportunities_table.update(opportunity_id, updates)
            except:
                # Fallback if Workflow Status field doesn't exist
                opportunities_table.update(opportunity_id, {
                    'Source Status': 'Requesting Quotes',
                    'Status': 'Request Quotes',
                    'Notes': f'Linked {len(supplier_ids)} suppliers on {datetime.now().strftime("%Y-%m-%d")}'
                })
            
            return {
                'success': True,
                'message': f'Added {len(supplier_ids)} suppliers',
                'newStatus': 'Request Quotes'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def mark_quotes_requested(self, opportunity_id: str, count: int):
        """Mark that quote requests have been sent"""
        try:
            opportunities_table = self.airtable.get_table('GPSS Opportunities')
            
            updates = {
                'Source Status': 'Awaiting Quotes',
                'Workflow Status': 'Awaiting Quotes',
                'Status': 'Awaiting Quotes',
                'Notes': f'Sent {count} quote requests on {datetime.now().strftime("%Y-%m-%d")}',
            }

            try:
                opportunities_table.update(opportunity_id, updates)
            except:
                # Fallback if Workflow Status field doesn't exist
                opportunities_table.update(opportunity_id, {
                    'Source Status': 'Awaiting Quotes',
                    'Status': 'Awaiting Quotes',
                    'Notes': f'Sent {count} quote requests on {datetime.now().strftime("%Y-%m-%d")}'
                })
            
            return {
                'success': True,
                'message': f'Sent {count} quote requests',
                'newStatus': 'Awaiting Quotes'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def advance_workflow(self, opportunity_id: str, new_status: str):
        """Manually advance opportunity to next workflow stage.
        
        Uses Source Status (known field) to track workflow progression.
        Falls back gracefully if other fields don't exist.
        """
        try:
            opportunities_table = self.airtable.get_table('GPSS Opportunities')
            
            # Map workflow status to Source Status values
            status_map = {
                'Find Suppliers': 'Finding Suppliers',
                'Request Quotes': 'Requesting Quotes',
                'Awaiting Quotes': 'Awaiting Quotes',
                'Ready to Price': 'Ready to Price',
                'Generate Proposal': 'Generating Proposal',
                'Final Review': 'Final Review',
                'Submitted': 'Submitted',
            }
            
            updates = {
                'Source Status': status_map.get(new_status, new_status),
            }
            
            try:
                opportunities_table.update(opportunity_id, updates)
            except Exception as field_err:
                # Minimal fallback
                print(f"Advance update failed ({field_err}), trying Notes only...")
                current = opportunities_table.get(opportunity_id)
                existing_notes = current['fields'].get('Notes', '')
                opportunities_table.update(opportunity_id, {
                    'Notes': f'{existing_notes}\n[{new_status}] {datetime.now().strftime("%Y-%m-%d %H:%M")}'
                })
            
            return {
                'success': True,
                'message': f'Advanced to {new_status}',
                'newStatus': new_status
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

# =====================================================================
# SUPPLIER QUOTE SYSTEM - Request quotes from suppliers
# =====================================================================

class SupplierQuoteSystem:
    """
    Integrated supplier quote request system
    Part of NEXUS workflow: Solicitation → Quote Request → Tracking → Follow-up
    """
    
    def __init__(self):
        self.airtable = AirtableClient()
        self.ai = AnthropicClient()
    
    def generate_quote_request(self, opportunity_id: str, supplier_ids: List[str] = None):
        """
        Generate and send quote requests for an opportunity
        
        Args:
            opportunity_id: Airtable record ID for opportunity
            supplier_ids: Optional list of supplier IDs. If None, auto-match suppliers
            
        Returns:
            dict: Generated quote requests with tracking info
        """
        # Get opportunity details
        opportunity = self.airtable.get_record('Opportunities', opportunity_id)
        opp_fields = opportunity['fields']
        
        # Extract items from solicitation
        items = self._extract_items_from_opportunity(opportunity)
        
        # Match suppliers if not provided
        if not supplier_ids:
            supplier_ids = self._match_suppliers(items, opp_fields)
        
        # Generate quote requests
        quote_requests = []
        for supplier_id in supplier_ids:
            supplier = self.airtable.get_record('Suppliers', supplier_id)
            
            # Generate PDF
            pdf_data = self._generate_quote_pdf(opportunity, items, supplier)
            
            # Send to supplier
            sent_info = self._send_to_supplier(supplier, pdf_data)
            
            # Log to Airtable
            quote_request = self._log_quote_request(
                opportunity_id, 
                supplier_id,
                pdf_data,
                sent_info
            )
            
            quote_requests.append(quote_request)
        
        return {
            'success': True,
            'opportunity_id': opportunity_id,
            'quote_requests': quote_requests,
            'count': len(quote_requests)
        }
    
    def _extract_items_from_opportunity(self, opportunity):
        """Extract items from opportunity using AI"""
        opp_fields = opportunity['fields']
        description = opp_fields.get('Description', '')
        
        # Use Claude to extract items
        prompt = f"""
Extract items/products/services from this solicitation:

{description}

Return JSON array of items:
[
  {{
    "number": "1",
    "description": "Item name",
    "specifications": "Details and specs",
    "quantity": "Estimated quantity",
    "unit": "unit/piece/ton/etc"
  }}
]
"""
        try:
            response = self.ai.complete(prompt, max_tokens=2000)
            items = json.loads(response.replace('```json', '').replace('```', '').strip())
            return items
        except:
            # Fallback to structured items if available
            return opp_fields.get('Items', [])
    
    def _match_suppliers(self, items, opp_fields):
        """Find matching suppliers for items"""
        # Get all active suppliers
        suppliers = self.airtable.get_all_records('Suppliers', formula="Active = TRUE()")
        
        # TODO: Smart matching based on categories, location, past performance
        # For now, return top 5
        return [s['id'] for s in suppliers[:5]]
    
    def _generate_quote_pdf(self, opportunity, items, supplier):
        """Generate quote request PDF"""
        import subprocess
        import tempfile
        from pathlib import Path
        
        opp_fields = opportunity['fields']
        rfq_number = f"DDI-{datetime.now().strftime('%Y')}-{opportunity['id'][:6].upper()}"
        
        # Build template
        template = f"""RFQ_NUMBER: {rfq_number}
TITLE: {opp_fields.get('Title', 'Quote Request')}
ISSUE_DATE: {datetime.now().strftime('%B %d, %Y')}
DUE_DATE: {(datetime.now() + timedelta(days=7)).strftime('%B %d, %Y')}
DUE_TIME: 5:00 PM EST
CONTRACT_PERIOD: {opp_fields.get('Contract Period', '12 months')}

COLOR_SCHEME: 1

INTRODUCTION:
DEE DAVIS INC is preparing a bid for a Michigan municipal client. We need competitive quotes by the date specified.

SCOPE:
Vendor will provide materials/services as specified. Delivery to Southeast Michigan location.

KEY_REQUIREMENTS:
- Competitive pricing required
- Confirm availability and lead times
- Provide delivery terms
- Net 30 payment terms preferred

ITEMS:
"""
        for item in items:
            template += f"{item['number']} | {item['description']} | {item['specifications']} | {item['quantity']} | {item['unit']}\n"
        
        # Save and generate PDF
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(template)
            temp_file = f.name
        
        result = subprocess.run(
            ['python3', 'create_from_paste.py', 'rfq', temp_file],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        
        # Find generated PDF
        output_dir = Path("GENERATED_QUOTES")
        pdf_files = list(output_dir.glob(f"*{rfq_number.lower().replace('-', '_')}*.pdf"))
        
        return {
            'rfq_number': rfq_number,
            'pdf_path': str(pdf_files[0]) if pdf_files else None,
            'template': template
        }
    
    def _send_to_supplier(self, supplier, pdf_data):
        """Send quote request via email"""
        # TODO: Implement email sending
        return {
            'method': 'email',
            'to': supplier['fields'].get('Email', ''),
            'timestamp': datetime.now().isoformat(),
            'success': True
        }
    
    def _log_quote_request(self, opportunity_id, supplier_id, pdf_data, sent_info):
        """Log quote request to GPSS QUOTES table"""
        # Convert timestamp to date format for Airtable date field
        sent_date = datetime.now().strftime('%Y-%m-%d')
        try:
            from datetime import datetime as dt
            parsed = dt.fromisoformat(sent_info['timestamp'])
            sent_date = parsed.strftime('%Y-%m-%d')
        except:
            pass
        
        return self.airtable.create_record('GPSS QUOTES', {
            'Opportunity': opportunity_id,
            'SUPPLIER': supplier_id,
            'SENT DATE': sent_date,
            'SENT METHOD': sent_info['method'].upper(),
            'SENT TO': sent_info['to'],
            'Status': 'Sent' if sent_info['success'] else 'Failed',
            'PDF PATH': pdf_data.get('pdf_path', ''),
            'Quote Number': pdf_data.get('rfq_number', ''),
            'DUE DATE': (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d'),
            'FOLLOW-UP NEEDED': True,
            'FOLLOW-UP DATE': (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d')
        })


# =====================================================================
# CAPABILITY STATEMENT SYSTEM - Generate capability statements
# =====================================================================

class CapabilityStatementSystem:
    """
    Generate professional capability statements for opportunities
    Integrated into NEXUS workflow
    """
    
    def __init__(self):
        self.airtable = AirtableClient()
    
    def generate_for_opportunity(self, opportunity_id: str, customization: Dict = None):
        """
        Generate capability statement for an opportunity
        
        Args:
            opportunity_id: Opportunity record ID
            customization: Optional customizations (color scheme, highlights, etc.)
            
        Returns:
            dict: Generated capability statement info
        """
        import subprocess
        import tempfile
        from pathlib import Path
        
        opportunity = self.airtable.get_record('Opportunities', opportunity_id)
        opp_fields = opportunity['fields']
        
        # Build capability statement template
        template = f"""CLIENT_NAME: {opp_fields.get('Agency', 'Client')}
RFQ_NUMBER: {opp_fields.get('Solicitation Number', 'RFQ-001')}
DATE: {datetime.now().strftime('%B %Y')}

COLOR_SCHEME: {customization.get('color_scheme', '1') if customization else '1'}

OVERVIEW:
DEE DAVIS INC specializes in supply chain management and logistics for government and commercial clients. As a Michigan-based EDWOSB, we provide reliable sourcing, competitive pricing, and exceptional service for diverse procurement needs.

HIGHLIGHTS:
NAICS: 423850 - Industrial Supplies
Partners: National supplier network | Grainger | Fastenal | Regional partners
Performance: 98%+ On-Time Delivery | 100% Contract Compliance
Coverage: Nationwide sourcing with Southeast Michigan delivery
Contract Range: $50K - $500K Successfully Delivered
"""
        
        # Generate PDF
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(template)
            temp_file = f.name
        
        result = subprocess.run(
            ['python3', 'create_from_paste.py', 'capability', temp_file],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        
        # Log to Airtable
        self.airtable.create_record('Generated Documents', {
            'Type': 'Capability Statement',
            'Opportunity': [opportunity_id],
            'Generated Date': datetime.now().isoformat(),
            'Status': 'Complete'
        })
        
        return {
            'success': True,
            'opportunity_id': opportunity_id,
            'generated': True
        }


# =====================================================================
# DOCUMENT INTELLIGENCE - Contact Extraction
# =====================================================================

class DocumentContactExtractor:
    """Extract contacts from any document with AI categorization"""
    
    def __init__(self):
        self.ai = AnthropicClient()
        self.airtable = AirtableClient()
    
    def extract_from_text(self, text: str, document_name: str = "Unknown") -> Dict:
        """
        Extract and categorize contacts from text using Claude AI
        Returns: {contacts: [...], metadata: {...}}
        """
        
        prompt = f"""
Analyze this document and extract ALL contact information.
For EACH contact, determine their role, priority, and purpose.

Document: {document_name}

Text:
{text}

Return ONLY valid JSON (no markdown, no preamble):
{{
  "contacts": [
    {{
      "name": "Full Name",
      "email": "email@domain.gov",
      "phone": "555-123-4567",
      "title": "Job Title",
      "organization": "Organization Name",
      "department": "Department",
      
      "categorization": {{
        "role": "Contracting Officer|Program Manager|Technical POC|Small Business Liaison|Decision Maker|Reviewer|Administrative",
        "agency_type": "Federal|State|Local|Military|Educational|Healthcare|Private Sector|Non-Profit",
        "priority": "HIGH|MEDIUM|LOW",
        "purpose": ["Proposal Submission", "Technical Questions", etc],
        "decision_authority": true/false
      }},
      
      "context": {{
        "found_on_page": 3,
        "section": "Section name",
        "quote": "Relevant quote from document",
        "notes": "Any relevant notes"
      }}
    }}
  ],
  
  "document_metadata": {{
    "primary_contact": "email of main contact",
    "document_type": "RFP|Contract|Proposal|Email|Other",
    "agency": "Agency name if applicable",
    "total_contacts_found": 0,
    "high_priority_contacts": 0
  }}
}}
"""
        
        try:
            response = self.ai.complete(prompt)
            # Clean potential markdown code fences
            clean_response = response.replace('```json', '').replace('```', '').strip()
            extracted_data = json.loads(clean_response)
            return extracted_data
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            print(f"Response was: {response[:500]}")
            return {"contacts": [], "document_metadata": {}}
        except Exception as e:
            print(f"Extraction error: {e}")
            return {"contacts": [], "document_metadata": {}}
    
    def store_contacts(self, contacts: List[Dict], source_document: str = None):
        """
        Store extracted contacts in Airtable
        Handles deduplication and updates
        """
        stored_contacts = []

        for contact in contacts:
            try:
                email = contact.get('email', '')
                if not email:
                    continue
                
                # Check if contact already exists
                formula = f"{{Email}} = '{email}'"
                existing = self.airtable.search_records('GPSS CONTACTS', formula)
                
                # Prepare fields (only include fields that exist in Airtable)
                fields = {
                    'Name': contact.get('name', ''),
                    'Email': email,
                    'Title': contact.get('title', ''),
                    'Organization': contact.get('organization', ''),
                    'Role Category': contact.get('categorization', {}).get('role', ''),
                    'Priority': contact.get('categorization', {}).get('priority', 'MEDIUM'),
                    'Notes': contact.get('context', {}).get('notes', '')
                }
                
                if existing:
                    # Update existing contact
                    record_id = existing[0]['id']
                    updated = self.airtable.update_record('GPSS CONTACTS', record_id, fields)
                    stored_contacts.append({
                        'action': 'updated',
                        'record_id': record_id,
                        'email': email
                    })
                else:
                    # Create new contact
                    created = self.airtable.create_record('GPSS CONTACTS', fields)
                    stored_contacts.append({
                        'action': 'created',
                        'record_id': created['id'],
                        'email': email
                    })
            
            except Exception as e:
                print(f"Error storing contact {contact.get('email', 'unknown')}: {e}")
                continue
        
        return stored_contacts

# =====================================================================
# DDCSS AGENTS - Corporate Sales System
# =====================================================================

class PrimeContractorMiner:
    """
    Automated Prime Contractor Mining System
    Finds companies with $10M+ federal contracts who MUST meet diversity goals
    Uses USASpending.gov (FREE) + SAM.gov APIs
    """
    
    def __init__(self):
        self.airtable = AirtableClient()
        self.ai = AnthropicClient()
        self.sam_api_key = os.environ.get('SAM_GOV_API_KEY', '')
    
    def mine_prime_contractors(self, min_contract_value=10000000, limit=50):
        """
        Find prime contractors from USASpending.gov with contracts over threshold
        
        Args:
            min_contract_value: Minimum total contract value (default: $10M)
            limit: Max number of prospects to find (default: 50)
        
        Returns:
            Dict with results summary
        """
        print(f"\n🔍 MINING PRIME CONTRACTORS (>${min_contract_value/1000000}M)")
        print("=" * 70)
        
        prospects_found = []
        prospects_created = 0
        duplicates_skipped = 0
        low_scores_skipped = 0
        
        try:
            # Query USASpending.gov for recent awards
            print("📊 Querying USASpending.gov...")
            awards = self._query_usaspending(min_contract_value, limit)
            print(f"   Found {len(awards)} prime contractors with >${min_contract_value/1000000}M in contracts")
            
            # Get existing prospects to avoid duplicates
            existing_prospects = self.airtable.get_all_records('DDCSS Prospects')
            existing_companies = {p['fields'].get('Company Name', '').upper() for p in existing_prospects}
            
            for award_data in awards:
                recipient_name = award_data.get('recipient_name', '')
                
                # Skip if we already have this company
                if recipient_name.upper() in existing_companies:
                    duplicates_skipped += 1
                    continue
                
                print(f"\n📋 Processing: {recipient_name}")
                
                # Get detailed company info from SAM.gov
                company_details = self._get_sam_details(award_data)
                
                # Calculate diversity gap (estimate based on contract value)
                diversity_analysis = self._estimate_diversity_gap(award_data)
                
                # AI scores the prospect
                score = self._ai_score_prospect(company_details, diversity_analysis)
                print(f"   🎯 AI Score: {score}/100")
                
                # Only create high-quality prospects
                if score >= 70:
                    prospect = self._create_prospect_record(
                        company_details,
                        diversity_analysis,
                        award_data,
                        score
                    )
                    prospects_found.append(prospect)
                    prospects_created += 1
                    print(f"   ✅ Added to DDCSS Prospects")
                else:
                    low_scores_skipped += 1
                    print(f"   ⏭️  Skipped (score too low)")
            
            # Summary
            print("\n" + "=" * 70)
            print("✅ MINING COMPLETE")
            print("=" * 70)
            print(f"📊 Results:")
            print(f"   • Prime contractors found: {len(awards)}")
            print(f"   • High-quality prospects created: {prospects_created}")
            print(f"   • Duplicates skipped: {duplicates_skipped}")
            print(f"   • Low scores skipped: {low_scores_skipped}")
            print("=" * 70)
            
            return {
                'success': True,
                'total_found': len(awards),
                'prospects_created': prospects_created,
                'duplicates_skipped': duplicates_skipped,
                'low_scores_skipped': low_scores_skipped,
                'prospects': prospects_found
            }
        
        except Exception as e:
            print(f"\n❌ Error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _query_usaspending(self, min_value, limit):
        """Query USASpending.gov API for prime contractors"""
        import requests
        
        url = "https://api.usaspending.gov/api/v2/search/spending_by_award/"
        
        # Query for recent large contracts
        payload = {
            "filters": {
                "time_period": [
                    {"start_date": "2023-01-01", "end_date": "2026-01-31"}
                ],
                "award_type_codes": ["A", "B", "C", "D"],  # Contracts only
                "award_amounts": [
                    {"lower_bound": min_value}
                ]
            },
            "fields": ["Award ID", "Recipient Name", "Award Amount", "Total Obligation"],
            "limit": limit,
            "page": 1,
            "sort": "Award Amount",
            "order": "desc"
        }
        
        try:
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            # Extract award data
            awards = []
            results = data.get('results', [])
            
            # Group by recipient to get total per company
            recipients = {}
            for result in results:
                recipient = result.get('Recipient Name', '')
                amount = result.get('Award Amount', 0)
                
                if recipient not in recipients:
                    recipients[recipient] = {
                        'recipient_name': recipient,
                        'recipient_duns': result.get('recipient_duns', ''),
                        'recipient_uei': result.get('recipient_uei', ''),
                        'total_contract_value': 0,
                        'award_count': 0,
                        'awarding_agencies': set()
                    }
                
                recipients[recipient]['total_contract_value'] += amount
                recipients[recipient]['award_count'] += 1
                agency = result.get('Awarding Agency', '')
                if agency:
                    recipients[recipient]['awarding_agencies'].add(agency)
            
            # Convert to list
            for recipient_data in recipients.values():
                recipient_data['awarding_agencies'] = list(recipient_data['awarding_agencies'])
                awards.append(recipient_data)
            
            # Sort by total value
            awards.sort(key=lambda x: x['total_contract_value'], reverse=True)
            
            return awards[:limit]
        
        except Exception as e:
            print(f"   ⚠️  USASpending API error: {e}")
            return []
    
    def _get_sam_details(self, award_data):
        """Get company details from SAM.gov"""
        import requests
        
        company_name = award_data.get('recipient_name', '')
        uei = award_data.get('recipient_uei', '')
        
        # If we have UEI, query SAM.gov
        if uei and self.sam_api_key:
            try:
                url = f"https://api.sam.gov/entity-information/v3/entities"
                params = {
                    'api_key': self.sam_api_key,
                    'ueiSAM': uei,
                    'includeSections': 'entityRegistration,coreData'
                }
                
                response = requests.get(url, params=params, timeout=15)
                if response.status_code == 200:
                    data = response.json()
                    entity_data = data.get('entityData', [{}])[0]
                    
                    return {
                        'company_name': company_name,
                        'uei': uei,
                        'cage_code': entity_data.get('cageCode', ''),
                        'address': entity_data.get('physicalAddress', {}),
                        'business_types': entity_data.get('businessTypes', []),
                        'naics_codes': entity_data.get('naicsCodes', []),
                        'registration_date': entity_data.get('registrationDate', ''),
                        'expiration_date': entity_data.get('expirationDate', '')
                    }
            except:
                pass
        
        # Fallback: basic info from USASpending
        return {
            'company_name': company_name,
            'uei': uei,
            'duns': award_data.get('recipient_duns', ''),
            'cage_code': '',
            'address': {},
            'business_types': [],
            'naics_codes': []
        }
    
    def _estimate_diversity_gap(self, award_data):
        """
        Estimate diversity subcontracting gap
        
        Companies with >$10M in federal contracts MUST have subcontracting plans
        Federal goal: 23% small business, 5% WOSB, varies by agency
        """
        total_value = award_data.get('total_contract_value', 0)
        
        # Federal requirements (typical)
        required_small_business_pct = 23
        required_wosb_pct = 5
        
        # Estimate current (conservative - assume they're underperforming)
        estimated_current_sb = 15  # Most are below goal
        estimated_current_wosb = 2  # Most are below goal
        
        sb_gap = required_small_business_pct - estimated_current_sb
        wosb_gap = required_wosb_pct - estimated_current_wosb
        
        # Calculate dollar value of gap
        sb_gap_dollars = (sb_gap / 100) * total_value
        wosb_gap_dollars = (wosb_gap / 100) * total_value
        
        return {
            'total_contract_value': total_value,
            'required_sb_pct': required_small_business_pct,
            'estimated_current_sb_pct': estimated_current_sb,
            'sb_gap_pct': sb_gap,
            'sb_gap_dollars': sb_gap_dollars,
            'required_wosb_pct': required_wosb_pct,
            'estimated_current_wosb_pct': estimated_current_wosb,
            'wosb_gap_pct': wosb_gap,
            'wosb_gap_dollars': wosb_gap_dollars,
            'pain_point': f"Estimated ${sb_gap_dollars/1000000:.1f}M gap in small business subcontracting"
        }
    
    def _ai_score_prospect(self, company_details, diversity_analysis):
        """AI scores prospect fit (0-100)"""
        
        company_name = company_details.get('company_name', 'Unknown')
        contract_value = diversity_analysis.get('total_contract_value', 0)
        sb_gap = diversity_analysis.get('sb_gap_pct', 0)
        
        prompt = f"""
Score this prime contractor prospect for supplier diversity consulting (0-100).

COMPANY: {company_name}
TOTAL FEDERAL CONTRACTS: ${contract_value:,.0f}
ESTIMATED SMALL BUSINESS GAP: {sb_gap}%
UEI: {company_details.get('uei', 'Unknown')}
BUSINESS TYPES: {', '.join(company_details.get('business_types', [])[:3])}

SCORING CRITERIA:
1. Contract Value (30 points):
   - $10M-$50M: 15 points
   - $50M-$100M: 20 points
   - $100M+: 30 points

2. Diversity Gap (30 points):
   - Gap <5%: 10 points
   - Gap 5-10%: 20 points
   - Gap >10%: 30 points

3. Company Size (20 points):
   - Large enough to need help: 20 points
   - Too small: 10 points

4. Industry Fit (20 points):
   - Defense/Healthcare/Tech/Construction: 20 points
   - Other: 10 points

Return ONLY a number between 0-100.
"""
        
        try:
            response = self.ai.complete(prompt, max_tokens=10)
            score = float(response.strip())
            return min(100, max(0, score))
        except:
            # Fallback scoring based on contract value
            if contract_value > 100000000:
                return 85
            elif contract_value > 50000000:
                return 75
            elif contract_value > 25000000:
                return 70
            else:
                return 65
    
    def _create_prospect_record(self, company_details, diversity_analysis, award_data, score):
        """Create prospect record in Airtable"""
        
        company_name = company_details.get('company_name', '')
        total_value = diversity_analysis.get('total_contract_value', 0)
        pain_point = diversity_analysis.get('pain_point', '')
        
        # Format address
        address_parts = company_details.get('address', {})
        address_str = f"{address_parts.get('addressLine1', '')}, {address_parts.get('city', '')}, {address_parts.get('stateOrProvinceCode', '')} {address_parts.get('zipCode', '')}"
        
        prospect_data = {
            'Company Name': company_name,
            'Company Size': 'Large' if total_value > 50000000 else 'Medium',
            'Total Contract Value': total_value,
            'Pain Point': pain_point,
            'AI Score': score,
            'Status': 'New Lead',
            'Source': 'USASpending.gov Auto-Mining',
            'Priority': 'HIGH' if score >= 85 else 'MEDIUM',
            'Date Found': datetime.now().strftime('%Y-%m-%d'),
            'UEI': company_details.get('uei', ''),
            'CAGE Code': company_details.get('cage_code', ''),
            'Location': address_str.strip(', '),
            'Contract Count': award_data.get('award_count', 0),
            'Awarding Agencies': ', '.join(award_data.get('awarding_agencies', [])[:3]),
            'Diversity Gap %': diversity_analysis.get('sb_gap_pct', 0),
            'Gap Dollar Value': diversity_analysis.get('sb_gap_dollars', 0),
            'Notes': f"Prime contractor with ${total_value/1000000:.1f}M in federal contracts. " +
                     f"Estimated {diversity_analysis.get('sb_gap_pct', 0)}% gap in small business subcontracting. " +
                     f"Legally required to meet diversity goals. " +
                     f"Works with: {', '.join(award_data.get('awarding_agencies', [])[:2])}."
        }
        
        try:
            record = self.airtable.create_record('DDCSS Prospects', prospect_data)
            return prospect_data
        except Exception as e:
            print(f"   ⚠️  Error creating record: {e}")
            return None


class DDCSSAgent1:
    """Corporate Sales Qualification Agent"""

    def __init__(self):
        self.ai = AnthropicClient()
        self.airtable = AirtableClient()

    def qualify_prospect(self, prospect_id: str) -> Dict:
        """
        Qualify a corporate prospect using DEE DAVIS INC frameworks
        Returns: qualification analysis, ICP fit, recommended approach
        """

        # Get prospect details from Airtable (DDCSS Prospects table)
        records = self.airtable.get_all_records('DDCSS Prospects')
        prospect = next((r for r in records if r['id'] == prospect_id), None)

        if not prospect:
            return {"error": "Prospect not found"}

        fields = prospect['fields']

        prompt = f"""
Analyze this corporate prospect and provide qualification assessment for DEE DAVIS INC consulting services:

COMPANY INFO:
Company: {fields.get('Company Name', 'Unknown')}
Industry: {fields.get('Industry', 'Unknown')}
Size: {fields.get('Company Size', 'Unknown')}
Location: {fields.get('Location', 'Unknown')}

CONTACT INFO:
Name: {fields.get('Contact Name', 'Unknown')}
Title: {fields.get('Contact Title', 'Unknown')}
LinkedIn: {fields.get('LinkedIn Profile', 'Unknown')}

CURRENT STATUS:
Stage: {fields.get('Pipeline Stage', 'Unknown')}
Budget: {fields.get('Budget Range', 'Unknown')}
Timeline: {fields.get('Timeline', 'Unknown')}

DEE DAVIS INC SPECIALTIES:
- Corporate Consulting ($25K Blueprint Frameworks)
- ALIGN, DEFINE, DESIGN, SHINE Methodology
- Change Management & Organizational Development
- Leadership Development & Team Alignment
- Strategic Planning & Execution
- Project Management Office (PMO) Setup

TARGET ICP:
- Mid-size companies (100-1000 employees)
- Growing companies needing organizational change
- Companies in transition (mergers, leadership changes, digital transformation)
- Companies wanting to scale operations

Provide assessment as JSON:
{{
  "qualification_score": 0-100,
  "icp_fit_score": 0-100,
  "recommended_approach": "DIRECT|NETWORKING|CONTENT|OUTREACH",
  "primary_service": "Blueprint Framework|Change Management|Leadership Development|Strategic Planning",
  "estimated_value": "$25K-$50K|$50K-$100K|$100K+",
  "timeline_fit": "HOT|WARM|COLD",
  "strengths": ["strength 1", "strength 2"],
  "concerns": ["concern 1", "concern 2"],
  "recommended_next_step": "Book Discovery Call|Send Framework Overview|Schedule Assessment|Content Nurture",
  "win_probability": 0-100
}}
"""

        try:
            response = self.ai.complete(prompt)
            clean_response = response.replace('```json', '').replace('```', '').strip()
            analysis = json.loads(clean_response)

            # Update prospect in Airtable
            self.airtable.update_record('DDCSS Prospects', prospect_id, {
                'Qualification Score': analysis['qualification_score'],
                'ICP Fit Score': analysis['icp_fit_score'],
                'Recommended Approach': analysis['recommended_approach'],
                'Win Probability': analysis['win_probability']
            })

            return analysis

        except Exception as e:
            print(f"DDCSS Qualification error: {e}")
            return {"error": str(e)}


class DDCSSAgent2:
    """Blueprint Framework Generator Agent"""

    def __init__(self):
        self.ai = AnthropicClient()
        self.airtable = AirtableClient()

    def generate_blueprint(self, prospect_id: str, framework_type: str = "ALIGN") -> Dict:
        """
        Generate a customized $25K Blueprint Framework
        Supports: ALIGN, DEFINE, DESIGN, SHINE frameworks
        """

        # Get prospect details
        records = self.airtable.get_all_records('DDCSS Prospects')
        prospect = next((r for r in records if r['id'] == prospect_id), None)

        if not prospect:
            return {"error": "Prospect not found"}

        fields = prospect['fields']

        framework_prompts = {
            "ALIGN": """
Generate an ALIGN Blueprint Framework for this prospect:

ALIGN Framework focuses on organizational alignment and team cohesion.
Key deliverables: Leadership alignment assessment, team dynamics analysis,
communication strategy, change management roadmap.
""",
            "DEFINE": """
Generate a DEFINE Blueprint Framework for this prospect:

DEFINE Framework focuses on strategic clarity and goal definition.
Key deliverables: Vision articulation, mission refinement, strategic objectives,
KPIs and success metrics definition.
""",
            "DESIGN": """
Generate a DESIGN Blueprint Framework for this prospect:

DESIGN Framework focuses on process and system optimization.
Key deliverables: Current state analysis, process mapping, workflow design,
implementation roadmap, training plans.
""",
            "SHINE": """
Generate a SHINE Blueprint Framework for this prospect:

SHINE Framework focuses on culture and performance excellence.
Key deliverables: Culture assessment, leadership development plan,
performance management system, employee engagement strategy.
"""
        }

        prompt = f"""
{framework_prompts.get(framework_type, framework_prompts["ALIGN"])}

PROSPECT DETAILS:
Company: {fields.get('Company Name', 'Unknown')}
Industry: {fields.get('Industry', 'Unknown')}
Size: {fields.get('Company Size', 'Unknown')}
Challenge: {fields.get('Current Challenge', 'Unknown')}
Goals: {fields.get('Business Goals', 'Unknown')}

Generate a customized {framework_type} Blueprint Framework as JSON:
{{
  "framework_type": "{framework_type}",
  "executive_summary": "2-paragraph overview of the framework and benefits",
  "current_state_analysis": "Assessment of their current situation",
  "recommended_solution": "Detailed solution approach",
  "implementation_phases": [
    {{
      "phase": "Phase 1 Name",
      "duration": "X weeks",
      "deliverables": ["Deliverable 1", "Deliverable 2"],
      "milestones": ["Milestone 1", "Milestone 2"]
    }}
  ],
  "expected_outcomes": ["Outcome 1", "Outcome 2", "Outcome 3"],
  "investment_required": "$25,000",
  "timeline": "8-12 weeks",
  "success_metrics": ["Metric 1", "Metric 2"],
  "next_steps": "Recommended immediate actions"
}}
"""

        try:
            response = self.ai.complete(prompt, max_tokens=3000)
            clean_response = response.replace('```json', '').replace('```', '').strip()
            blueprint = json.loads(clean_response)

            # Save blueprint to Airtable
            blueprint_data = {
                'Prospect ID': prospect_id,
                'Framework Type': framework_type,
                'Generated Blueprint': json.dumps(blueprint),
                'Created Date': datetime.now().isoformat(),
                'Status': 'Generated'
            }
            self.airtable.create_record('DDCSS Blueprints', blueprint_data)

            return blueprint

        except Exception as e:
            print(f"Blueprint generation error: {e}")
            return {"error": str(e)}


class DDCSSAgent3:
    """AI Response Handler Agent"""

    def __init__(self):
        self.ai = AnthropicClient()
        self.airtable = AirtableClient()

    def analyze_response(self, email_content: str, prospect_id: str = None) -> Dict:
        """
        Analyze inbound email responses using Claude AI
        Categorize intent, sentiment, and recommend next actions
        """

        # Get prospect context if available
        prospect_context = ""
        if prospect_id:
            records = self.airtable.get_all_records('DDCSS Prospects')
            prospect = next((r for r in records if r['id'] == prospect_id), None)
            if prospect:
                fields = prospect['fields']
                prospect_context = f"""
PROSPECT CONTEXT:
Company: {fields.get('Company Name', 'Unknown')}
Current Stage: {fields.get('Pipeline Stage', 'Unknown')}
Last Contact: {fields.get('Last Contact Date', 'Unknown')}
"""

        prompt = f"""
Analyze this inbound email response and provide AI-powered insights:

{prospect_context}

EMAIL CONTENT:
{email_content}

Analyze the email and provide insights as JSON:
{{
  "sentiment": "POSITIVE|NEUTRAL|NEGATIVE",
  "intent": "INTERESTED|QUESTIONING|OBJECTION|COMMITMENT|NO_RESPONSE",
  "urgency_level": "HOT|WARM|COLD",
  "key_topics": ["topic1", "topic2"],
  "action_required": "IMMEDIATE_RESPONSE|FOLLOW_UP|SCHEDULE_CALL|PROPOSAL|NO_ACTION",
  "recommended_response": "Suggested response strategy or script",
  "objections_identified": ["objection1", "objection2"],
  "next_steps": ["step1", "step2"],
  "confidence_score": 0-100,
  "summary": "2-3 sentence summary of the email"
}}
"""

        try:
            response = self.ai.complete(prompt)
            clean_response = response.replace('```json', '').replace('```', '').strip()
            analysis = json.loads(clean_response)

            # Log the analysis in Airtable
            analysis_data = {
                'Prospect ID': prospect_id or '',
                'Email Content': email_content[:1000],  # Truncate for storage
                'Analysis Result': json.dumps(analysis),
                'Analyzed Date': datetime.now().isoformat(),
                'Sentiment': analysis['sentiment'],
                'Action Required': analysis['action_required']
            }
            self.airtable.create_record('DDCSS AI Responses', analysis_data)

            return analysis

        except Exception as e:
            print(f"AI Response analysis error: {e}")
            return {"error": str(e)}


# =====================================================================
# ATLAS PM AGENTS - Project Management System
# =====================================================================

class ATLASAgent1:
    """RFP Analysis and Qualification Agent"""

    def __init__(self):
        self.ai = AnthropicClient()
        self.airtable = AirtableClient()

    def analyze_rfp(self, rfp_content: str, project_id: str = None) -> Dict:
        """
        Analyze RFP content and extract key requirements, compliance needs, and win strategy
        """

        prompt = f"""
Analyze this RFP document and provide comprehensive project management insights:

RFP CONTENT:
{rfp_content}

Provide analysis as JSON:
{{
  "executive_summary": "2-paragraph summary of the RFP",
  "key_requirements": [
    {{
      "requirement": "Requirement description",
      "category": "TECHNICAL|COMPLIANCE|DELIVERABLE|TIMELINE|BUDGET",
      "priority": "CRITICAL|HIGH|MEDIUM|LOW",
      "complexity": "HIGH|MEDIUM|LOW"
    }}
  ],
  "compliance_requirements": ["requirement1", "requirement2"],
  "timeline_analysis": {{
    "total_duration": "X weeks/months",
    "critical_milestones": ["milestone1", "milestone2"],
    "risk_areas": ["risk1", "risk2"]
  }},
  "budget_estimate": {{
    "range": "$X-$Y",
    "confidence": "HIGH|MEDIUM|LOW",
    "assumptions": ["assumption1", "assumption2"]
  }},
  "win_strategy": {{
    "competitive_advantages": ["advantage1", "advantage2"],
    "differentiation_points": ["point1", "point2"],
    "recommended_approach": "Technical superiority|Relationship|Innovation|Cost"
  }},
  "risk_assessment": {{
    "high_risks": ["risk1", "risk2"],
    "mitigation_strategies": ["strategy1", "strategy2"]
  }},
  "recommended_team": ["role1", "role2", "role3"],
  "estimated_effort": "HIGH|MEDIUM|LOW"
}}
"""

        try:
            response = self.ai.complete(prompt, max_tokens=3000)
            clean_response = response.replace('```json', '').replace('```', '').strip()
            analysis = json.loads(clean_response)

            # Save analysis to Airtable if project_id provided
            if project_id:
                analysis_data = {
                    'Project ID': project_id,
                    'RFP Content': rfp_content[:2000],  # Truncate
                    'Analysis Result': json.dumps(analysis),
                    'Analyzed Date': datetime.now().isoformat()
                }
                self.airtable.create_record('ATLAS RFP Analysis', analysis_data)

            return analysis

        except Exception as e:
            print(f"RFP Analysis error: {e}")
            return {"error": str(e)}


class ATLASAgent2:
    """Project Planning and WBS Generator"""

    def __init__(self):
        self.ai = AnthropicClient()
        self.airtable = AirtableClient()

    def generate_wbs(self, project_id: str) -> Dict:
        """
        Generate Work Breakdown Structure and project plan
        """

        # Get project details
        records = self.airtable.get_all_records('ATLAS Projects')
        project = next((r for r in records if r['id'] == project_id), None)

        if not project:
            return {"error": "Project not found"}

        fields = project['fields']

        prompt = f"""
Generate a comprehensive Work Breakdown Structure (WBS) for this project:

PROJECT DETAILS:
Name: {fields.get('Project Name', 'Unknown')}
Client: {fields.get('Client Name', 'Unknown')}
Type: {fields.get('Project Type', 'Unknown')}
Budget: {fields.get('Budget', 'Unknown')}
Timeline: {fields.get('Timeline', 'Unknown')}
Scope: {fields.get('Project Scope', 'Unknown')}

Generate WBS as JSON:
{{
  "wbs_structure": {{
    "1.0": {{
      "name": "Project Management",
      "description": "Overall project coordination and management",
      "subtasks": {{
        "1.1": {{
          "name": "Project Planning",
          "deliverables": ["Project Charter", "Project Plan", "Risk Register"],
          "estimated_hours": 40,
          "resources": ["Project Manager"],
          "dependencies": []
        }},
        "1.2": {{
          "name": "Stakeholder Management",
          "deliverables": ["Stakeholder Register", "Communication Plan"],
          "estimated_hours": 20,
          "resources": ["Project Manager"],
          "dependencies": ["1.1"]
        }}
      }}
    }},
    "2.0": {{
      "name": "Technical Delivery",
      "description": "Core project deliverables",
      "subtasks": {{
        "2.1": {{
          "name": "Requirements Analysis",
          "deliverables": ["Requirements Document", "Use Cases"],
          "estimated_hours": 60,
          "resources": ["Business Analyst", "Technical Lead"],
          "dependencies": ["1.1"]
        }}
      }}
    }}
  }},
  "critical_path": ["1.1", "2.1", "3.1"],
  "milestones": [
    {{
      "name": "Project Kickoff",
      "date": "2025-01-XX",
      "deliverables": ["Kickoff Meeting", "Project Charter"]
    }}
  ],
  "resource_allocation": {{
    "Project Manager": 160,
    "Business Analyst": 120,
    "Developer": 320
  }},
  "risk_mitigation": ["risk1", "risk2"]
}}
"""

        try:
            response = self.ai.complete(prompt, max_tokens=3000)
            clean_response = response.replace('```json', '').replace('```', '').strip()
            wbs = json.loads(clean_response)

            # Save WBS to Airtable
            wbs_data = {
                'Project ID': project_id,
                'WBS Data': json.dumps(wbs),
                'Generated Date': datetime.now().isoformat(),
                'Status': 'Generated'
            }
            self.airtable.create_record('ATLAS WBS', wbs_data)

            return wbs

        except Exception as e:
            print(f"WBS Generation error: {e}")
            return {"error": str(e)}


class ATLASAgent3:
    """Change Order Management Agent"""

    def __init__(self):
        self.ai = AnthropicClient()
        self.airtable = AirtableClient()

    def analyze_change_request(self, change_description: str, project_id: str) -> Dict:
        """
        Analyze change request and provide impact assessment
        """

        # Get project context
        records = self.airtable.get_all_records('ATLAS Projects')
        project = next((r for r in records if r['id'] == project_id), None)

        project_context = ""
        if project:
            fields = project['fields']
            project_context = f"""
PROJECT CONTEXT:
Name: {fields.get('Project Name', 'Unknown')}
Budget: {fields.get('Budget', 'Unknown')}
Timeline: {fields.get('Timeline', 'Unknown')}
Current Status: {fields.get('Status', 'Unknown')}
"""

        prompt = f"""
Analyze this change request and provide impact assessment:

{project_context}

CHANGE REQUEST:
{change_description}

Provide analysis as JSON:
{{
  "change_type": "SCOPE|SCHEDULE|BUDGET|QUALITY|RESOURCE",
  "impact_assessment": {{
    "scope_impact": "HIGH|MEDIUM|LOW|NONE",
    "schedule_impact": "X weeks delay",
    "budget_impact": "$X additional cost",
    "resource_impact": "Additional resources needed",
    "risk_impact": "Increased/Decreased risk level"
  }},
  "approval_required": true/false,
  "recommended_action": "APPROVE|DENY|MODIFY|REVIEW",
  "alternative_solutions": ["option1", "option2"],
  "implementation_plan": {{
    "steps": ["step1", "step2"],
    "timeline": "X weeks",
    "resources_needed": ["resource1", "resource2"]
  }},
  "contractual_implications": "Any contract changes needed",
  "client_notification": "Required/Recommended/Not Required"
}}
"""

        try:
            response = self.ai.complete(prompt)
            clean_response = response.replace('```json', '').replace('```', '').strip()
            analysis = json.loads(clean_response)

            # Create change order record
            change_data = {
                'Project ID': project_id,
                'Change Description': change_description,
                'Analysis Result': json.dumps(analysis),
                'Impact Assessment': f"Schedule: {analysis['impact_assessment']['schedule_impact']}, Budget: {analysis['impact_assessment']['budget_impact']}",
                'Recommended Action': analysis['recommended_action'],
                'Status': 'Pending Review',
                'Created Date': datetime.now().isoformat()
            }
            self.airtable.create_record('ATLAS Change Orders', change_data)

            return analysis

        except Exception as e:
            print(f"Change order analysis error: {e}")
            return {"error": str(e)}


# =====================================================================
# GPSS AGENTS
# =====================================================================

class GPSSAgent2:
    """AI Qualification Agent with RFP Compliance Analysis"""
    
    def __init__(self):
        self.ai = AnthropicClient()
        self.airtable = AirtableClient()
    
    def qualify_opportunity(self, opportunity_id: str) -> Dict:
        """
        Qualify a government opportunity
        Returns: qualification score, analysis, go/no-go decision
        """
        
        # Get opportunity details from Airtable
        records = self.airtable.get_all_records('GPSS OPPORTUNITIES')
        opportunity = next((r for r in records if r['id'] == opportunity_id), None)
        
        if not opportunity:
            return {"error": "Opportunity not found"}
        
        fields = opportunity['fields']
        
        prompt = f"""
Analyze this government contracting opportunity and provide qualification assessment:

RFP Number: {fields.get('RFP Number', 'Unknown')}
Agency: {fields.get('Agency Name', 'Unknown')}
Contract Value: ${fields.get('Contract Value', 0):,.0f}
Deadline: {fields.get('Deadline', 'Unknown')}

Based on DEE DAVIS INC capabilities:
- EDWOSB certified small business
- Government contracting experience (NEMT, transportation, emergency services)
- Product portfolio: Emergency kits, generators, manufactured homes, containers
- CAGE Code: 8UMX3
- GSA Schedule pending approval

Provide assessment as JSON:
{{
  "qualification_score": 0-100,
  "go_no_go": "GO|NO-GO|REVIEW",
  "strengths": ["strength 1", "strength 2"],
  "weaknesses": ["weakness 1", "weakness 2"],
  "requirements_met": ["requirement 1", "requirement 2"],
  "requirements_gap": ["gap 1", "gap 2"],
  "win_probability": 0-100,
  "recommended_action": "Detailed recommendation",
  "compliance_concerns": ["concern 1 if any"],
  "estimated_effort": "LOW|MEDIUM|HIGH"
}}
"""
        
        try:
            response = self.ai.complete(prompt)
            clean_response = response.replace('```json', '').replace('```', '').strip()
            analysis = json.loads(clean_response)
            
            # Update opportunity in Airtable with qualification
            self.airtable.update_record('GPSS OPPORTUNITIES', opportunity_id, {
                'Status': analysis['go_no_go']
            })
            
            return analysis
            
        except Exception as e:
            print(f"Qualification error: {e}")
            return {"error": str(e)}


class GPSSAgent3:
    """Quote Generation Agent with Compliance Verification"""
    
    def __init__(self):
        self.ai = AnthropicClient()
        self.airtable = AirtableClient()
    
    def generate_quote(self, opportunity_id: str) -> Dict:
        """
        Generate a compliant government proposal/quote
        Returns: quote content, compliance checklist, recipient info
        """
        
        # Get opportunity
        records = self.airtable.get_all_records('GPSS OPPORTUNITIES')
        opportunity = next((r for r in records if r['id'] == opportunity_id), None)
        
        if not opportunity:
            return {"error": "Opportunity not found"}
        
        fields = opportunity['fields']
        
        # Get relevant contacts
        contacts = self.airtable.get_all_records('GPSS CONTACTS')
        
        # Get products
        products = self.airtable.get_all_records('GPSS PRODUCTS')
        
        contract_value = fields.get('Contract Value', 0)
        is_under_250k = contract_value < 250000
        
        past_performance_instruction = (
            "Brief statement: 'Past performance not required for contracts under $250K. DEE DAVIS INC is ready to demonstrate capability.'"
            if is_under_250k else
            "Detailed relevant contract experience with specifics (contract numbers, agencies, values, outcomes)"
        )
        
        prompt = f"""
Generate a professional government contract proposal for:

OPPORTUNITY:
RFP: {fields.get('RFP Number')}
Agency: {fields.get('Agency Name')}
Value: ${contract_value:,.0f}
Deadline: {fields.get('Deadline')}

COMPANY:
DEE DAVIS INC
CAGE: 8UMX3
EDWOSB Certified
Certifications: EDWOSB/WOSB/WBE/MBE

AVAILABLE PRODUCTS:
{json.dumps([p['fields'] for p in products[:5]], indent=2)}

CONTACTS:
{json.dumps([c['fields'] for c in contacts if c['fields'].get('Organization') == fields.get('Agency Name')], indent=2)}

IMPORTANT BUSINESS RULE:
{"⚠️ This RFP is UNDER $250K - Past performance is NOT required. Keep this section brief." if is_under_250k else "This RFP is OVER $250K - Past performance IS required. Provide detailed experience."}

🎯 WINNING PROPOSAL PRINCIPLES (CRITICAL - FOLLOW THESE):

1. PAIN POINT ALIGNMENT: Align yourself with the problem the agency is trying to resolve. Show you understand their pain.

2. RFP ANALYSIS: Review the RFP for context. Understand the full context and scope. Don't just answer - demonstrate understanding.

3. RESPONSIVE ANSWERS: Give responsive answers. Use bullet points. Use the client's EXACT language from the RFP. Mirror their terms.

4. RECIPE COMPLIANCE: Think of the RFP like a recipe you need to follow to the 'T'. Every requirement must be addressed in order.

5. DOCUMENT ORGANIZATION: Present clear solutions. Use headers, bullet points, short paragraphs. Make it easy to score.

6. PROJECT MANAGEMENT: Think like a project manager. Show the plan from start to finish. Timeline, milestones, deliverables.

7. QUALITY ASSURANCE: Talk about quality control metrics, final walkthrough, testing procedures, success criteria.

8. TEAM PRESENTATION: Show organization chart. Who's doing what on what level. Name key personnel with qualifications.

Generate proposal as JSON following the 8 winning principles above:
{{
  "executive_summary": "2-3 paragraphs showing you understand their pain point and how you'll solve it. Use their exact language from RFP.",
  
  "technical_approach": "FOLLOW THIS STRUCTURE:
    - UNDERSTANDING OF REQUIREMENTS (use bullet points, mirror RFP language)
    - PROPOSED SOLUTION (clear, responsive answers to their needs)
    - METHODOLOGY (step-by-step like a project manager)
    - TIMELINE & MILESTONES (start to finish plan)
    - QUALITY ASSURANCE (QC metrics, testing, final walkthrough)
    - DELIVERABLES (what they'll receive, when)
    Use headers, bullet points, short paragraphs. 5-7 sections.",
  
  "staffing_plan": "SHOW ORGANIZATION:
    - Organization chart (who reports to whom)
    - Key personnel with names and qualifications
    - Role descriptions (who's doing what on what level)
    - Staffing levels and hours
    - Backup personnel plan
    NOT 'we will post an ad' - show actual team structure.",
  
  {past_performance_instruction},
  
  "pricing": {{
    "total": 0,
    "breakdown": {{}},
    "justification": "Explain why this price is fair and reasonable. Tie to scope and quality."
  }},
  
  "compliance_checklist": {{
    "format_compliant": true,
    "all_questions_answered": true,
    "staffing_detailed": true,
    "pricing_realistic": true,
    "reps_certs_included": true,
    "past_performance_required": {"false" if is_under_250k else "true"},
    "pain_point_addressed": true,
    "client_language_used": true,
    "clear_organization": true,
    "quality_assurance_included": true
  }},
  
  "recipients": {{
    "primary_to": "contracting.officer@agency.gov",
    "cc": ["program.manager@agency.gov"]
  }}
}}
"""
        
        try:
            response = self.ai.complete(prompt, max_tokens=4000)
            clean_response = response.replace('```json', '').replace('```', '').strip()
            quote = json.loads(clean_response)
            
            return quote
            
        except Exception as e:
            print(f"Quote generation error: {e}")
            return {"error": str(e)}


class GPSSPricingAgent:
    """Intelligent Pricing Agent with Market Analysis & Win Probability"""
    
    def __init__(self):
        self.ai = AnthropicClient()
        self.airtable = AirtableClient()
    
    def calculate_intelligent_price(self, opportunity_id: str, service_category: str = None) -> Dict:
        """
        Generate intelligent pricing recommendation based on:
        - Historical win/loss data
        - Market intelligence
        - Cost templates
        - Competition analysis
        - Win probability optimization
        
        Returns: Pricing recommendation with multiple scenarios
        """
        
        # Get opportunity details
        try:
            opportunities = self.airtable.get_all_records('GPSS OPPORTUNITIES')
            opportunity = next((r for r in opportunities if r['id'] == opportunity_id), None)
            
            if not opportunity:
                return {"error": "Opportunity not found"}
            
            opp_fields = opportunity['fields']
            
            # Determine service category
            if not service_category:
                service_category = self._determine_service_category(opp_fields)
            
            # Get historical pricing data
            pricing_history = self._get_pricing_history(service_category)
            
            # Get cost template
            cost_template = self._get_cost_template(service_category)
            
            # Get market intelligence
            market_intel = self._get_market_intelligence(
                service_category,
                opp_fields.get('State', 'Federal'),
                opp_fields.get('Set-Aside Type')
            )
            
            # Calculate base costs
            base_cost = self._calculate_base_cost(opp_fields, cost_template)
            
            # Get AI pricing recommendation
            pricing_data = {
                'opportunity': {
                    'rfp_number': opp_fields.get('RFP Number', ''),
                    'agency': opp_fields.get('Agency Name', ''),
                    'value': opp_fields.get('Contract Value', 0),
                    'contract_type': opp_fields.get('Contract Type', 'Fixed Price'),
                    'duration_months': opp_fields.get('Performance Period (months)', 12),
                    'set_aside': opp_fields.get('Set-Aside Type', ''),
                    'state': opp_fields.get('State', 'Federal'),
                    'urgency': opp_fields.get('Urgency', 'Medium')
                },
                'historical_data': pricing_history,
                'cost_template': cost_template,
                'market_intelligence': market_intel,
                'base_cost': base_cost,
                'service_category': service_category
            }
            
            ai_recommendation = self._get_ai_pricing_recommendation(pricing_data)
            
            # Calculate pricing scenarios
            scenarios = self._calculate_pricing_scenarios(base_cost, pricing_data, ai_recommendation)
            
            return {
                'recommended_price': ai_recommendation.get('recommended_price', base_cost * 1.15),
                'price_range': ai_recommendation.get('price_range', {}),
                'scenarios': scenarios,
                'win_probability': ai_recommendation.get('win_probability', 50),
                'pricing_strategy': ai_recommendation.get('strategy', 'Competitive'),
                'cost_breakdown': base_cost,
                'market_position': ai_recommendation.get('market_position', 'Average'),
                'justification': ai_recommendation.get('justification', ''),
                'risk_assessment': ai_recommendation.get('risk_assessment', 'Medium'),
                'competitive_intelligence': market_intel,
                'recommendations': ai_recommendation.get('recommendations', [])
            }
            
        except Exception as e:
            print(f"Pricing calculation error: {e}")
            return {"error": str(e)}
    
    def _determine_service_category(self, opp_fields: Dict) -> str:
        """Determine service category from opportunity details"""
        title = opp_fields.get('Title', '').lower()
        description = opp_fields.get('Description', '').lower()
        
        keywords = {
            'Project Management & Consulting': ['project management', 'consulting', 'advisory', 'management', 'pm', 'pmo'],
            'Healthcare Transportation & Diagnostics': ['nemt', 'non-emergency', 'medical transport', 'transportation broker', 'ambulance', 'emergency medical', 'ems', 'diagnostics'],
            'Compliance & Credentialing': ['compliance', 'credentialing', 'certification', 'licensing', 'regulatory'],
            'Notary & Settlement Services': ['notary', 'settlement', 'closing', 'title', 'escrow'],
            'Document Preparation & Corporate Services': ['document preparation', 'corporate services', 'filing', 'formation', 'business services'],
            'Freight Brokerage & Logistics': ['freight', 'brokerage', 'logistics', 'shipping', 'transportation', 'trucking', 'cargo'],
            'Staffing & Recruitment': ['staffing', 'recruitment', 'personnel', 'temporary', 'contractor', 'hiring', 'talent'],
            'Emergency Equipment & Supplies (GPSS)': ['emergency equipment', 'supplies', 'gpss', 'equipment', 'medical supplies', 'ppe'],
            'Technology & Software Development': ['technology', 'software', 'development', 'it', 'programming', 'app', 'web', 'tech', 'digital']
        }
        
        for category, words in keywords.items():
            if any(word in title or word in description for word in words):
                return category
        
        return 'Project Management & Consulting'
    
    def _get_pricing_history(self, service_category: str) -> List[Dict]:
        """Get relevant historical pricing data"""
        try:
            all_history = self.airtable.get_all_records('Pricing History')
            
            # Filter by service category and sort by most recent
            relevant = [
                h['fields'] for h in all_history 
                if h['fields'].get('Service Category') == service_category
            ]
            
            # Sort by bid date (most recent first)
            relevant.sort(key=lambda x: x.get('Bid Date', ''), reverse=True)
            
            return relevant[:10]  # Return last 10 bids
            
        except Exception as e:
            print(f"Error fetching pricing history: {e}")
            return []
    
    def _get_cost_template(self, service_category: str) -> Dict:
        """Get cost template for service category"""
        try:
            templates = self.airtable.get_all_records('Cost Templates')
            
            # Find matching template
            for template in templates:
                if template['fields'].get('Service Category') == service_category:
                    return template['fields']
            
            # Return default if not found
            return {
                'Base Hourly Rate': 65.0,
                'Labor Cost per Hour': 45.0,
                'Materials Cost %': 0.10,
                'Overhead Rate %': 0.25,
                'Target Profit Margin %': 0.15,
                'Minimum Margin %': 0.08
            }
            
        except Exception as e:
            print(f"Error fetching cost template: {e}")
            return {}
    
    def _get_market_intelligence(self, service_category: str, region: str, set_aside: str = None) -> Dict:
        """Get market intelligence data"""
        try:
            intel = self.airtable.get_all_records('Market Intelligence')
            
            # Filter by service category and region
            relevant = [
                i['fields'] for i in intel
                if i['fields'].get('Service Type') == service_category and
                   i['fields'].get('Geographic Region') == region
            ]
            
            if not relevant:
                # Fallback to any data for this service category
                relevant = [
                    i['fields'] for i in intel
                    if i['fields'].get('Service Type') == service_category
                ]
            
            if relevant:
                # Return most recent and high confidence data
                relevant.sort(key=lambda x: (
                    x.get('Confidence Level') == 'High',
                    x.get('Date Observed', '')
                ), reverse=True)
                return relevant[0]
            
            return {}
            
        except Exception as e:
            print(f"Error fetching market intelligence: {e}")
            return {}
    
    def _calculate_base_cost(self, opp_fields: Dict, cost_template: Dict) -> Dict:
        """Calculate base costs for the opportunity"""
        try:
            contract_value = opp_fields.get('Contract Value', 0)
            duration_months = opp_fields.get('Performance Period (months)', 12)
            
            # If we have contract value, work backwards
            if contract_value > 0:
                # Assume target margin
                target_margin = cost_template.get('Target Profit Margin %', 15) / 100
                overhead_rate = cost_template.get('Overhead Rate %', 25) / 100
                
                # Cost = Value / (1 + overhead) / (1 + margin)
                estimated_base_cost = contract_value / (1 + overhead_rate) / (1 + target_margin)
                
                labor_cost = estimated_base_cost * 0.7  # 70% labor
                materials_cost = estimated_base_cost * 0.2  # 20% materials
                other_costs = estimated_base_cost * 0.1  # 10% other
                
            else:
                # Estimate from hours/staff requirements
                base_hourly_rate = cost_template.get('Base Hourly Rate', 65)
                labor_cost_per_hour = cost_template.get('Labor Cost per Hour', 45)
                
                # Assume 2080 hours per year per FTE
                annual_hours = 2080
                estimated_fte = cost_template.get('Staff Required', 2)
                
                total_hours = (duration_months / 12) * annual_hours * estimated_fte
                labor_cost = total_hours * labor_cost_per_hour
                
                materials_cost = labor_cost * cost_template.get('Materials Cost %', 10) / 100
                other_costs = (labor_cost + materials_cost) * 0.05
                
                estimated_base_cost = labor_cost + materials_cost + other_costs
            
            overhead_amount = estimated_base_cost * (cost_template.get('Overhead Rate %', 25) / 100)
            total_cost = estimated_base_cost + overhead_amount
            
            return {
                'labor': round(labor_cost, 2),
                'materials': round(materials_cost, 2),
                'other': round(other_costs, 2),
                'subtotal': round(estimated_base_cost, 2),
                'overhead_rate': cost_template.get('Overhead Rate %', 25),
                'overhead_amount': round(overhead_amount, 2),
                'total_cost': round(total_cost, 2)
            }
            
        except Exception as e:
            print(f"Error calculating base cost: {e}")
            return {'total_cost': 0}
    
    def _get_ai_pricing_recommendation(self, pricing_data: Dict) -> Dict:
        """Get AI-powered pricing recommendation"""
        
        prompt = f"""
You are an expert government contract pricing analyst. Analyze this opportunity and provide intelligent pricing recommendations.

OPPORTUNITY:
{json.dumps(pricing_data['opportunity'], indent=2)}

SERVICE CATEGORY: {pricing_data['service_category']}

BASE COST ESTIMATE:
{json.dumps(pricing_data['base_cost'], indent=2)}

HISTORICAL PRICING DATA (Last 10 Similar Bids):
{json.dumps(pricing_data['historical_data'][:5], indent=2)}

Historical Win Rate: {self._calculate_win_rate(pricing_data['historical_data'])}%

COST TEMPLATE:
{json.dumps(pricing_data['cost_template'], indent=2)}

MARKET INTELLIGENCE:
{json.dumps(pricing_data['market_intelligence'], indent=2)}

ANALYSIS REQUIRED:
1. Recommended bid price (single number)
2. Price range (low to high)
3. Win probability estimate (0-100)
4. Recommended pricing strategy (Aggressive/Competitive/Premium/Cost-Plus/Market Rate)
5. Market position (Below Market/Average/Above Market/Premium)
6. Detailed justification (2-3 paragraphs)
7. Risk assessment (Low/Medium/High)
8. Key recommendations (3-5 bullet points)

PRICING FACTORS TO CONSIDER:
- Historical win rate at different price points
- Market rates for this service type
- Competition level (set-aside vs unrestricted)
- Urgency (faster = potential premium)
- Geographic region advantages
- Our cost structure vs market
- Profit margin optimization

Return as JSON:
{{
  "recommended_price": 0,
  "price_range": {{
    "minimum": 0,
    "competitive": 0,
    "optimal": 0,
    "maximum": 0
  }},
  "win_probability": 0,
  "strategy": "Competitive",
  "market_position": "Average",
  "justification": "Detailed explanation...",
  "risk_assessment": "Medium",
  "recommendations": [
    "Recommendation 1",
    "Recommendation 2",
    "Recommendation 3"
  ]
}}
"""
        
        try:
            response = self.ai.complete(prompt, max_tokens=2000)
            clean_response = response.replace('```json', '').replace('```', '').strip()
            recommendation = json.loads(clean_response)
            return recommendation
            
        except Exception as e:
            print(f"AI pricing recommendation error: {e}")
            # Return fallback recommendation
            base_cost = pricing_data['base_cost'].get('total_cost', 0)
            return {
                'recommended_price': base_cost * 1.15,
                'price_range': {
                    'minimum': base_cost * 1.08,
                    'competitive': base_cost * 1.12,
                    'optimal': base_cost * 1.15,
                    'maximum': base_cost * 1.20
                },
                'win_probability': 50,
                'strategy': 'Competitive',
                'market_position': 'Average',
                'justification': 'Standard markup based on cost template.',
                'risk_assessment': 'Medium',
                'recommendations': ['Review market intelligence', 'Consider competitive factors']
            }
    
    def _calculate_win_rate(self, pricing_history: List[Dict]) -> float:
        """Calculate win rate from historical data"""
        if not pricing_history:
            return 50.0
        
        wins = sum(1 for h in pricing_history if h.get('Win/Loss') == 'Won')
        total = len([h for h in pricing_history if h.get('Win/Loss') in ['Won', 'Lost']])
        
        if total == 0:
            return 50.0
        
        return round((wins / total) * 100, 1)
    
    def _calculate_pricing_scenarios(self, base_cost: Dict, pricing_data: Dict, ai_rec: Dict) -> List[Dict]:
        """Generate multiple pricing scenarios"""
        total_cost = base_cost.get('total_cost', 0)
        
        scenarios = [
            {
                'name': 'Aggressive (Must Win)',
                'price': round(total_cost * 1.08, 2),
                'margin': 8.0,
                'win_probability': 75,
                'risk': 'High',
                'description': 'Minimum viable pricing - use only for strategic must-win opportunities',
                'profit': round(total_cost * 0.08, 2)
            },
            {
                'name': 'Competitive (Recommended)',
                'price': round(ai_rec.get('recommended_price', total_cost * 1.15), 2),
                'margin': round(((ai_rec.get('recommended_price', total_cost * 1.15) - total_cost) / total_cost) * 100, 1),
                'win_probability': ai_rec.get('win_probability', 60),
                'risk': 'Medium',
                'description': 'AI-optimized pricing balancing win probability and profit',
                'profit': round(ai_rec.get('recommended_price', total_cost * 1.15) - total_cost, 2)
            },
            {
                'name': 'Standard Market Rate',
                'price': round(total_cost * 1.18, 2),
                'margin': 18.0,
                'win_probability': 45,
                'risk': 'Medium',
                'description': 'Industry standard markup - good for established relationships',
                'profit': round(total_cost * 0.18, 2)
            },
            {
                'name': 'Premium (High Value)',
                'price': round(total_cost * 1.25, 2),
                'margin': 25.0,
                'win_probability': 30,
                'risk': 'Low',
                'description': 'Premium pricing - use when we have unique capabilities or low competition',
                'profit': round(total_cost * 0.25, 2)
            }
        ]
        
        return scenarios


class GPSSComplianceAgent:
    """Proposal Compliance Checker - Prevents rejection due to non-compliance"""
    
    def __init__(self):
        self.ai = AnthropicClient()
        self.airtable = AirtableClient()
    
    def analyze_rfp_requirements(self, rfp_content: str) -> Dict:
        """
        Extract requirements, evaluation factors, and compliance items from RFP
        Returns: Structured compliance checklist
        """
        
        prompt = f"""
You are an expert Federal Contracting Officer analyzing an RFP for compliance requirements.

RFP CONTENT:
{rfp_content[:10000]}  # Limit to first 10K chars for analysis

Extract and structure ALL compliance requirements:

1. SUBMISSION REQUIREMENTS (what must be included):
   - Required documents
   - Required certifications
   - Required forms
   - Required attachments

2. FORMATTING REQUIREMENTS:
   - Page limits (by section)
   - Font size/type
   - Margin requirements
   - File format requirements
   - Naming conventions

3. EVALUATION FACTORS (how proposals will be scored):
   - Technical approach (weight %)
   - Past performance (weight %)
   - Staffing plan (weight %)
   - Price (weight %)
   - Other factors

4. CRITICAL COMPLIANCE ITEMS (auto-reject if missing):
   - SAM registration
   - Required signatures
   - Deadline requirements
   - Specific questions to answer

5. SPECIAL REQUIREMENTS:
   - Security clearances
   - Facility requirements
   - Equipment requirements
   - Certifications needed

Return as JSON:
{{
  "submission_requirements": [
    {{"item": "SF 33 signed", "required": true, "auto_reject": true}},
    ...
  ],
  "formatting_requirements": {{
    "technical_approach_pages": 10,
    "past_performance_pages": 5,
    "font_size": "12pt",
    "font_type": "Times New Roman",
    "margins": "1 inch",
    "file_format": "PDF"
  }},
  "evaluation_factors": [
    {{"factor": "Technical Approach", "weight": 40, "subfactors": ["Understanding of requirements", "Proposed methodology"]}},
    {{"factor": "Past Performance", "weight": 30, "subfactors": ["Relevance", "Recency", "Quality"]}},
    {{"factor": "Staffing Plan", "weight": 20, "subfactors": ["Key personnel qualifications", "Organizational structure"]}},
    {{"factor": "Price", "weight": 10, "subfactors": []}}
  ],
  "critical_items": [
    "SAM.gov registration active",
    "Proposal signed by authorized official",
    "All required certifications included"
  ],
  "special_requirements": [
    "Security clearance: Secret required for key personnel",
    "Facility: Government-furnished workspace"
  ],
  "deadline": "2026-02-15 2:00 PM EST",
  "submission_method": "Email to contracting.officer@agency.gov",
  "questions_due": "2026-01-20",
  "amendments_issued": []
}}
"""
        
        try:
            response = self.ai.complete(prompt, max_tokens=3000)
            clean_response = response.replace('```json', '').replace('```', '').strip()
            requirements = json.loads(clean_response)
            return requirements
            
        except Exception as e:
            print(f"RFP analysis error: {e}")
            return {"error": str(e)}
    
    def check_proposal_compliance(self, proposal_data: Dict, rfp_requirements: Dict) -> Dict:
        """
        Check proposal against RFP requirements
        Returns: Compliance score and list of issues
        """
        
        issues = []
        warnings = []
        compliant_items = []
        
        # Check submission requirements
        for req in rfp_requirements.get('submission_requirements', []):
            item_name = req.get('item', '')
            is_required = req.get('required', True)
            auto_reject = req.get('auto_reject', False)
            
            # Check if item is present in proposal
            # This is a simplified check - in production, you'd parse actual documents
            is_present = self._check_item_presence(item_name, proposal_data)
            
            if not is_present and is_required:
                if auto_reject:
                    issues.append({
                        'type': 'CRITICAL',
                        'item': item_name,
                        'message': f'Missing required item: {item_name}. This will result in automatic rejection.',
                        'fix': f'Add {item_name} to your proposal package'
                    })
                else:
                    warnings.append({
                        'type': 'WARNING',
                        'item': item_name,
                        'message': f'Recommended item missing: {item_name}',
                        'fix': f'Consider adding {item_name} to strengthen proposal'
                    })
            elif is_present:
                compliant_items.append(item_name)
        
        # Check formatting requirements
        format_reqs = rfp_requirements.get('formatting_requirements', {})
        for section, page_limit in format_reqs.items():
            if 'pages' in section and isinstance(page_limit, int):
                # Check if section exists and is within page limit
                section_name = section.replace('_pages', '').replace('_', ' ').title()
                # Simplified check
                if section_name.lower() in str(proposal_data).lower():
                    compliant_items.append(f'{section_name} formatting')
        
        # Check evaluation factors coverage
        for factor in rfp_requirements.get('evaluation_factors', []):
            factor_name = factor.get('factor', '')
            subfactors = factor.get('subfactors', [])
            
            # Check if factor is addressed in proposal
            is_addressed = self._check_factor_coverage(factor_name, proposal_data)
            
            if not is_addressed:
                issues.append({
                    'type': 'MAJOR',
                    'item': factor_name,
                    'message': f'Evaluation factor not adequately addressed: {factor_name}',
                    'fix': f'Add section addressing {factor_name} and subfactors: {", ".join(subfactors)}'
                })
            else:
                compliant_items.append(f'{factor_name} addressed')
        
        # Check critical items
        for critical in rfp_requirements.get('critical_items', []):
            # Simplified check
            if 'SAM' in critical:
                compliant_items.append('SAM registration (assumed active)')
            elif 'sign' in critical.lower():
                warnings.append({
                    'type': 'REMINDER',
                    'item': 'Signature',
                    'message': 'Ensure proposal is signed by authorized official before submission',
                    'fix': 'Obtain signature from authorized representative'
                })
        
        # Check 8 Winning Principles (Best Practices)
        proposal_str = str(proposal_data).lower()
        
        # 1. Pain Point Alignment
        if not any(word in proposal_str for word in ['challenge', 'problem', 'need', 'requirement', 'objective']):
            warnings.append({
                'type': 'BEST PRACTICE',
                'item': '1. Pain Point Alignment',
                'message': 'Proposal should explicitly address the agency\'s pain points and challenges',
                'fix': 'Add section showing you understand their problem and how you\'ll solve it'
            })
        else:
            compliant_items.append('Pain point alignment')
        
        # 2. RFP Context Understanding
        if len(proposal_data.get('technical_approach', '')) < 500:
            warnings.append({
                'type': 'BEST PRACTICE',
                'item': '2. RFP Analysis & Context',
                'message': 'Technical approach seems brief. Show deeper understanding of scope and context.',
                'fix': 'Expand technical approach to demonstrate full understanding of requirements'
            })
        else:
            compliant_items.append('Comprehensive RFP analysis')
        
        # 3. Responsive Answers (bullet points)
        if proposal_data.get('technical_approach', '').count('•') < 5 and proposal_data.get('technical_approach', '').count('-') < 5:
            warnings.append({
                'type': 'BEST PRACTICE',
                'item': '3. Responsive Format',
                'message': 'Use more bullet points for easier readability and scoring',
                'fix': 'Convert dense paragraphs to bullet points where appropriate'
            })
        else:
            compliant_items.append('Bullet point formatting')
        
        # 4. Document Organization (headers)
        tech_approach = proposal_data.get('technical_approach', '')
        if tech_approach.upper().count('UNDERSTANDING') == 0 or tech_approach.upper().count('METHODOLOGY') == 0:
            warnings.append({
                'type': 'BEST PRACTICE',
                'item': '5. Document Organization',
                'message': 'Use clear headers like "UNDERSTANDING OF REQUIREMENTS" and "METHODOLOGY"',
                'fix': 'Add structured headers to organize your technical approach'
            })
        else:
            compliant_items.append('Clear document organization')
        
        # 6. Project Management (timeline/milestones)
        if not any(word in proposal_str for word in ['timeline', 'milestone', 'schedule', 'phase', 'deliverable']):
            warnings.append({
                'type': 'BEST PRACTICE',
                'item': '6. Project Management',
                'message': 'Show project plan from start to finish with timeline and milestones',
                'fix': 'Add project timeline, phases, milestones, and deliverables'
            })
        else:
            compliant_items.append('Project management approach')
        
        # 7. Quality Assurance
        if not any(word in proposal_str for word in ['quality', 'qc', 'testing', 'review', 'verification']):
            warnings.append({
                'type': 'BEST PRACTICE',
                'item': '7. Quality Assurance',
                'message': 'Include quality control metrics, testing procedures, and final walkthrough',
                'fix': 'Add QA/QC section with metrics and procedures'
            })
        else:
            compliant_items.append('Quality assurance included')
        
        # 8. Team Presentation (org chart)
        staffing = proposal_data.get('staffing_plan', '')
        if 'chart' not in staffing.lower() and 'organization' not in staffing.lower():
            warnings.append({
                'type': 'BEST PRACTICE',
                'item': '8. Team Organization',
                'message': 'Show organization chart with who\'s doing what on what level',
                'fix': 'Add organization chart showing reporting structure and key personnel'
            })
        else:
            compliant_items.append('Team organization structure')
        
        # Calculate compliance score
        total_requirements = len(rfp_requirements.get('submission_requirements', [])) + \
                            len(rfp_requirements.get('evaluation_factors', [])) + \
                            len(rfp_requirements.get('critical_items', []))
        
        if total_requirements == 0:
            compliance_score = 100
        else:
            compliance_score = (len(compliant_items) / total_requirements) * 100
        
        # Determine risk level
        critical_issues = len([i for i in issues if i['type'] == 'CRITICAL'])
        if critical_issues > 0:
            risk_level = 'HIGH - Likely rejection'
        elif len(issues) > 3:
            risk_level = 'MEDIUM - May lose points'
        elif len(warnings) > 2:
            risk_level = 'LOW - Minor improvements needed'
        else:
            risk_level = 'MINIMAL - Well structured'
        
        return {
            'compliance_score': round(compliance_score, 1),
            'risk_level': risk_level,
            'critical_issues': critical_issues,
            'total_issues': len(issues),
            'total_warnings': len(warnings),
            'issues': issues,
            'warnings': warnings,
            'compliant_items': compliant_items,
            'summary': f'Compliance: {compliance_score:.1f}% | Risk: {risk_level} | Issues: {len(issues)} | Warnings: {len(warnings)}'
        }
    
    def _check_item_presence(self, item_name: str, proposal_data: Dict) -> bool:
        """Check if item is present in proposal (simplified)"""
        # This is a simplified check - in production, you'd check actual documents
        item_lower = item_name.lower()
        proposal_str = str(proposal_data).lower()
        
        # Check for common keywords
        if 'sf' in item_lower or 'form' in item_lower:
            return 'form' in proposal_str or 'sf' in proposal_str
        if 'certification' in item_lower:
            return 'certification' in proposal_str or 'certified' in proposal_str
        if 'signature' in item_lower:
            return True  # Assume will be signed before submission
        
        return item_lower in proposal_str
    
    def _check_factor_coverage(self, factor_name: str, proposal_data: Dict) -> bool:
        """Check if evaluation factor is adequately addressed"""
        factor_lower = factor_name.lower()
        
        # Check if factor is mentioned in proposal
        if 'technical' in factor_lower:
            return bool(proposal_data.get('technical_approach'))
        elif 'past performance' in factor_lower or 'experience' in factor_lower:
            return bool(proposal_data.get('past_performance'))
        elif 'staffing' in factor_lower or 'personnel' in factor_lower:
            return bool(proposal_data.get('staffing_plan'))
        elif 'price' in factor_lower or 'cost' in factor_lower:
            return bool(proposal_data.get('pricing'))
        
        return True  # Assume covered if not standard factor
    
    def generate_compliance_report(self, compliance_check: Dict, rfp_requirements: Dict) -> str:
        """Generate human-readable compliance report"""
        
        report = f"""
PROPOSAL COMPLIANCE REPORT
{"="*50}

OVERALL SCORE: {compliance_check['compliance_score']}%
RISK LEVEL: {compliance_check['risk_level']}

SUMMARY:
- Compliant Items: {len(compliance_check['compliant_items'])}
- Critical Issues: {compliance_check['critical_issues']}
- Total Issues: {compliance_check['total_issues']}
- Warnings: {compliance_check['total_warnings']}

"""
        
        if compliance_check['critical_issues'] > 0:
            report += "\n🚨 CRITICAL ISSUES (WILL CAUSE REJECTION):\n"
            for issue in compliance_check['issues']:
                if issue['type'] == 'CRITICAL':
                    report += f"\n❌ {issue['item']}\n"
                    report += f"   Problem: {issue['message']}\n"
                    report += f"   Fix: {issue['fix']}\n"
        
        if compliance_check['total_issues'] > compliance_check['critical_issues']:
            report += "\n⚠️  MAJOR ISSUES (WILL LOSE POINTS):\n"
            for issue in compliance_check['issues']:
                if issue['type'] != 'CRITICAL':
                    report += f"\n⚠️  {issue['item']}\n"
                    report += f"   Problem: {issue['message']}\n"
                    report += f"   Fix: {issue['fix']}\n"
        
        if compliance_check['warnings']:
            report += "\n💡 WARNINGS & RECOMMENDATIONS:\n"
            for warning in compliance_check['warnings']:
                report += f"\n💡 {warning['item']}\n"
                report += f"   {warning['message']}\n"
                report += f"   {warning['fix']}\n"
        
        report += f"\n\n✅ COMPLIANT ITEMS ({len(compliance_check['compliant_items'])}):\n"
        for item in compliance_check['compliant_items']:
            report += f"  ✓ {item}\n"
        
        report += "\n" + "="*50 + "\n"
        
        if compliance_check['critical_issues'] == 0 and compliance_check['total_issues'] == 0:
            report += "\n🎉 Your proposal meets all compliance requirements!\n"
            report += "You may proceed with confidence.\n"
        elif compliance_check['critical_issues'] > 0:
            report += "\n⛔ DO NOT SUBMIT until critical issues are resolved!\n"
            report += "Your proposal will be rejected as non-responsive.\n"
        else:
            report += "\n⚠️  Address issues to improve your evaluation score.\n"
        
        return report


class GPSSOpportunityMiningAgent:
    """
    Universal Opportunity Mining & Forecasting System
    
    Supports 2 modes:
    1. Vendor Portal Mining - Registered portals with login access
    2. Open Intelligence Mining - Public scraping of ANY site
    """
    
    def __init__(self):
        self.ai = AnthropicClient()
        self.airtable = AirtableClient()
    
    def mine_portal_opportunities(self, portal_id: str) -> Dict:
        """
        Mine opportunities from a specific portal
        Works with any portal type (Federal, State, Local, Enterprise)
        """
        
        # Get portal details
        try:
            portals = self.airtable.get_all_records('VENDOR PORTAL')
            portal = next((p for p in portals if p['id'] == portal_id), None)
            
            if not portal:
                return {"error": "Portal not found"}
            
            fields = portal['fields']
            portal_name = fields.get('Portal Name', '')
            portal_type = fields.get('Portal Type', '')
            portal_url = fields.get('PORTAL URL', '') or fields.get('Portal URL', '') or ''
            keywords = fields.get('Keywords', '')
            
            if not portal_url:
                return {"error": f"Portal '{portal_name}' has no URL configured"}
            
            # Determine mining strategy based on portal URL
            # Known API portals get API treatment, everything else gets scraped
            SAM_DOMAINS = ['sam.gov', 'beta.sam.gov']
            is_sam = any(d in portal_url.lower() for d in SAM_DOMAINS)
            
            if is_sam:
                # SAM.gov has a real API — use it
                opportunities = self._mine_sam_api(keywords)
            else:
                # All other portals: scrape the page + AI extraction
                opportunities = self._mine_via_scraping(portal_url, keywords or portal_type)
            
            # Update last checked time (only if field exists, gracefully skip if not)
            try:
                self.airtable.update_record('VENDOR PORTAL', portal_id, {
                    'Last Checked': datetime.now().isoformat()
                })
            except:
                pass  # Field may not exist yet
            
            return {
                'portal_name': portal_name,
                'opportunities_found': len(opportunities),
                'opportunities': opportunities
            }
            
        except Exception as e:
            print(f"Mining error: {e}")
            return {"error": str(e)}
    
    def _mine_sam_api(self, keywords: str = '') -> List[Dict]:
        """Mine opportunities from SAM.gov using the real API"""
        try:
            sam_client = SAMgovAPIClient()
            results = sam_client.search_opportunities(
                keywords=keywords or 'supplies equipment services',
                limit=25
            )
            
            opportunities = []
            for opp in results:
                opportunities.append({
                    'title': opp.get('title', ''),
                    'agency': opp.get('department', ''),
                    'solicitation_number': opp.get('solicitationNumber', ''),
                    'estimated_value': 0,
                    'deadline': opp.get('responseDeadLine', ''),
                    'description': opp.get('description', '')[:300],
                    'url': f"https://sam.gov/opp/{opp.get('noticeId', '')}",
                    'set_aside_type': opp.get('typeOfSetAside', ''),
                    'confidence': 'High',
                    'source': 'SAM.gov API'
                })
            
            return opportunities
        except Exception as e:
            print(f"SAM API mining error: {e}")
            return []
    
    def _mine_via_api(self, portal_fields: Dict) -> List[Dict]:
        """Mine opportunities using portal API (legacy compatibility)"""
        return self._mine_sam_api(portal_fields.get('Keywords', ''))
    
    def _mine_via_scraping(self, url: str, portal_type: str) -> List[Dict]:
        """
        Mine opportunities using web scraping
        Works with ANY public website - no login required
        """
        try:
            import requests
            from bs4 import BeautifulSoup
            
            # Fetch the page
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract text content
            page_text = soup.get_text(separator='\n', strip=True)
            
            # Use AI to extract opportunities
            opportunities = self._ai_extract_opportunities(page_text, portal_type)
            
            return opportunities
            
        except Exception as e:
            print(f"Scraping error for {url}: {e}")
            return []
    
    def scrape_mining_target(self, target_id: str) -> Dict:
        """
        Scrape a Mining Target (public sites - NO login required)
        This finds opportunities ANYWHERE on the internet
        """
        
        try:
            # Get mining target details
            targets = self.airtable.get_all_records('Mining Targets')
            target = next((t for t in targets if t['id'] == target_id), None)
            
            if not target:
                return {"error": "Mining target not found"}
            
            fields = target['fields']
            target_name = fields.get('Target Name', '')
            target_url = fields.get('Target URL', '')
            target_type = fields.get('Target Type', '')
            scraping_method = fields.get('Scraping Method', 'Public Web Scraping')
            search_keywords = fields.get('Search Keywords', '')
            
            # Different scraping strategies
            if scraping_method == 'Public Web Scraping':
                opportunities = self._scrape_public_site(target_url, search_keywords, fields)
            elif scraping_method == 'RSS Feed':
                opportunities = self._mine_via_rss(target_url)
            elif scraping_method == 'API (Public)':
                opportunities = self._scrape_public_api(target_url, fields)
            else:
                opportunities = []
            
            # Update last scraped time
            self.airtable.update_record('Mining Targets', target_id, {
                'Last Scraped': datetime.now().isoformat(),
                'Opportunities Found': fields.get('Opportunities Found', 0) + len(opportunities)
            })
            
            return {
                'target_name': target_name,
                'target_type': target_type,
                'opportunities_found': len(opportunities),
                'opportunities': opportunities,
                'purpose': fields.get('Purpose', 'Direct Opportunities')
            }
            
        except Exception as e:
            print(f"Target scraping error: {e}")
            return {"error": str(e)}
    
    def _scrape_public_site(self, url: str, keywords: str, target_fields: Dict) -> List[Dict]:
        """
        Scrape public website for opportunities
        Uses AI to extract relevant information from ANY page format
        """
        
        try:
            import requests
            from bs4 import BeautifulSoup
            
            # Fetch page
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            page_text = soup.get_text(separator='\n', strip=True)
            
            # Use AI to extract opportunities from unstructured text
            opportunities = self._ai_extract_opportunities(page_text, keywords)
            return opportunities
            
        except Exception as e:
            print(f"Scraping error for {url}: {e}")
            return []
    
    def _ai_extract_opportunities(self, page_content: str, keywords: str) -> List[Dict]:
        """
        Use AI to extract opportunities from ANY webpage content
        This is the magic - AI understands ANY format!
        """
        
        prompt = f"""
You are an expert at finding government contract opportunities in ANY format.

WEB PAGE CONTENT:
{page_content[:8000]}  # Limit content

SEARCH KEYWORDS:
{keywords}

Extract ALL opportunities/contracts/RFPs mentioned on this page.

For EACH opportunity found, extract:
1. Title/Name
2. Agency/Organization
3. Solicitation Number (if any)
4. Value/Budget (if mentioned)
5. Deadline/Due Date (if mentioned)
6. Brief Description
7. Link/URL (if present)
8. Set-Aside Type (if mentioned)

Return as JSON array:
[
  {{
    "title": "...",
    "agency": "...",
    "solicitation_number": "...",
    "estimated_value": 0,
    "deadline": "YYYY-MM-DD",
    "description": "...",
    "url": "...",
    "set_aside_type": "...",
    "confidence": "High|Medium|Low"
  }}
]

If NO opportunities found, return empty array: []
"""
        
        try:
            response = self.ai.complete(prompt, max_tokens=3000)
            clean_response = response.replace('```json', '').replace('```', '').strip()
            opportunities = json.loads(clean_response)
            return opportunities if isinstance(opportunities, list) else []
            
        except Exception as e:
            print(f"AI extraction error: {e}")
            return []
    
    def _scrape_public_api(self, api_url: str, target_fields: Dict) -> List[Dict]:
        """
        Call public API endpoints (no authentication required)
        Example: SAM.gov public API, USASpending.gov API
        """
        try:
            import requests
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(api_url, headers=headers, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            # Use AI to extract opportunities from JSON response
            keywords = target_fields.get('Search Keywords', '')
            return self._ai_extract_opportunities(json.dumps(data)[:8000], keywords)
        except Exception as e:
            print(f"Public API scrape error: {e}")
            return []
    
    def scrape_all_targets(self) -> Dict:
        """
        Scrape ALL Mining Targets that are active
        This finds opportunities from ANY public source
        """
        
        try:
            # Get all active mining targets
            targets = self.airtable.get_all_records('Mining Targets')
            active_targets = [
                t for t in targets
                if t['fields'].get('Scraping Status', 'Active') == 'Active'
            ]
            
            results = []
            total_found = 0
            
            for target in active_targets:
                result = self.scrape_mining_target(target['id'])
                if not result.get('error'):
                    results.append(result)
                    total_found += result.get('opportunities_found', 0)
            
            return {
                'targets_scraped': len(active_targets),
                'total_opportunities_found': total_found,
                'results': results
            }
            
        except Exception as e:
            print(f"Target scraping error: {e}")
            return {"error": str(e)}
    
    def competitive_intelligence_search(self, competitor_name: str, keywords: str = None) -> Dict:
        """
        Search for what contracts a competitor has won
        Scrapes news, press releases, USASpending.gov, etc.
        """
        
        search_keywords = f"{competitor_name} contract award"
        if keywords:
            search_keywords += f" {keywords}"
        
        # This would scrape:
        # - Company press releases
        # - News articles
        # - USASpending.gov awards
        # - LinkedIn company updates
        # - Industry publications
        
        prompt = f"""
Find recent government contract awards for: {competitor_name}

Search keywords: {search_keywords}

Based on typical public sources (news, press releases, government databases),
generate a competitive intelligence report:

{{
  "competitor": "{competitor_name}",
  "recent_wins": [
    {{
      "contract_title": "...",
      "agency": "...",
      "value": 0,
      "award_date": "YYYY-MM-DD",
      "source": "USASpending.gov|News|Press Release",
      "naics_code": "...",
      "description": "..."
    }}
  ],
  "total_value": 0,
  "active_agencies": ["Agency 1", "Agency 2"],
  "strengths": ["Strength 1", "Strength 2"],
  "opportunities_for_us": ["Opportunity 1", "Opportunity 2"]
}}
"""
        
        try:
            response = self.ai.complete(prompt, max_tokens=2000)
            clean_response = response.replace('```json', '').replace('```', '').strip()
            intel = json.loads(clean_response)
            return intel
            
        except Exception as e:
            print(f"Competitive intel error: {e}")
            return {"error": str(e)}
    
    def _mine_via_rss(self, rss_url: str) -> List[Dict]:
        """Mine opportunities from RSS feed"""
        # This would parse RSS feeds
        return []
    
    def forecast_opportunities(self, agency_name: str = None, lookback_months: int = 24) -> Dict:
        """
        Forecast upcoming opportunities based on historical patterns
        Analyzes past contracts to predict future opportunities
        """
        
        try:
            # Get historical opportunities
            opportunities = self.airtable.get_all_records('GPSS OPPORTUNITIES')
            
            # Filter by agency if specified
            if agency_name:
                opportunities = [
                    opp for opp in opportunities 
                    if opp['fields'].get('Agency Name', '').lower() == agency_name.lower()
                ]
            
            # Group by agency and analyze patterns
            agency_patterns = {}
            for opp in opportunities:
                agency = opp['fields'].get('Agency Name', 'Unknown')
                if agency not in agency_patterns:
                    agency_patterns[agency] = []
                agency_patterns[agency].append(opp['fields'])
            
            # Generate forecasts using AI
            forecasts = []
            for agency, opps in agency_patterns.items():
                if len(opps) >= 2:  # Need at least 2 data points
                    forecast = self._generate_agency_forecast(agency, opps)
                    if forecast:
                        forecasts.append(forecast)
            
            return {
                'total_forecasts': len(forecasts),
                'forecasts': forecasts
            }
            
        except Exception as e:
            print(f"Forecasting error: {e}")
            return {"error": str(e)}
    
    def _generate_agency_forecast(self, agency: str, historical_opps: List[Dict]) -> Dict:
        """Generate forecast for a specific agency based on historical data"""
        
        # Sort by date
        sorted_opps = sorted(
            historical_opps,
            key=lambda x: x.get('Posted Date', ''),
            reverse=True
        )
        
        if len(sorted_opps) < 2:
            return None
        
        # Analyze patterns
        latest_opp = sorted_opps[0]
        previous_opp = sorted_opps[1]
        
        # Use AI to analyze and forecast
        prompt = f"""
Analyze these historical government contracts and forecast the next opportunity:

AGENCY: {agency}

RECENT CONTRACTS:
{json.dumps(sorted_opps[:3], indent=2)}

Analyze:
1. Frequency pattern (annual, biannual, etc.)
2. Value trends
3. Timing patterns
4. Service type consistency

Generate forecast as JSON:
{{
  "forecast_title": "Predicted opportunity title",
  "predicted_post_date": "YYYY-MM-DD",
  "confidence_level": "Very High|High|Medium|Low",
  "estimated_value": 0,
  "contract_duration": 12,
  "frequency": "Annual|Biannual|etc",
  "reasoning": "Why we think this will happen",
  "preparation_tips": ["Tip 1", "Tip 2"],
  "key_differences": "What might change from last time"
}}
"""
        
        try:
            response = self.ai.complete(prompt, max_tokens=1500)
            clean_response = response.replace('```json', '').replace('```', '').strip()
            forecast = json.loads(clean_response)
            
            # Add agency info
            forecast['agency'] = agency
            forecast['historical_count'] = len(sorted_opps)
            forecast['last_value'] = latest_opp.get('Contract Value', 0)
            forecast['forecast_type'] = 'Historical Pattern'
            
            return forecast
            
        except Exception as e:
            print(f"AI forecast error: {e}")
            return None
    
    def analyze_agency_spending(self, agency_name: str) -> Dict:
        """
        Analyze an agency's spending patterns and preferences
        Helps predict what they'll buy and when
        """
        
        try:
            opportunities = self.airtable.get_all_records('GPSS OPPORTUNITIES')
            
            # Filter for this agency
            agency_opps = [
                opp['fields'] for opp in opportunities
                if opp['fields'].get('Agency Name', '').lower() == agency_name.lower()
            ]
            
            if not agency_opps:
                return {"error": f"No data found for agency: {agency_name}"}
            
            # Calculate statistics
            total_opps = len(agency_opps)
            total_value = sum(opp.get('Contract Value', 0) for opp in agency_opps)
            avg_value = total_value / total_opps if total_opps > 0 else 0
            
            # Analyze service categories
            categories = {}
            for opp in agency_opps:
                category = opp.get('Category', 'Unknown')
                categories[category] = categories.get(category, 0) + 1
            
            # Analyze set-aside usage
            set_asides = {}
            for opp in agency_opps:
                set_aside = opp.get('Set-Aside Type', 'Unrestricted')
                set_asides[set_aside] = set_asides.get(set_aside, 0) + 1
            
            # Use AI to generate insights
            prompt = f"""
Analyze this agency's contracting patterns and provide actionable insights:

AGENCY: {agency_name}

STATISTICS:
- Total Contracts: {total_opps}
- Total Value: ${total_value:,.0f}
- Average Value: ${avg_value:,.0f}

SERVICE CATEGORIES:
{json.dumps(categories, indent=2)}

SET-ASIDE USAGE:
{json.dumps(set_asides, indent=2)}

RECENT CONTRACTS:
{json.dumps(agency_opps[:5], indent=2)}

Provide analysis as JSON:
{{
  "spending_profile": "Description of their spending patterns",
  "preferred_contract_types": ["Type 1", "Type 2"],
  "typical_values": {{"small": 0, "medium": 0, "large": 0}},
  "set_aside_preference": "Which set-asides they use most",
  "timing_patterns": "When they typically post opportunities",
  "best_opportunities_for_us": ["Opportunity type 1", "Opportunity type 2"],
  "competitive_advantage": "How to position ourselves",
  "action_items": ["Action 1", "Action 2", "Action 3"]
}}
"""
            
            response = self.ai.complete(prompt, max_tokens=2000)
            clean_response = response.replace('```json', '').replace('```', '').strip()
            analysis = json.loads(clean_response)
            
            # Add raw statistics
            analysis['statistics'] = {
                'total_opportunities': total_opps,
                'total_value': total_value,
                'average_value': avg_value,
                'service_categories': categories,
                'set_aside_breakdown': set_asides
            }
            
            return analysis
            
        except Exception as e:
            print(f"Agency analysis error: {e}")
            return {"error": str(e)}
    
    def auto_mine_all_portals(self) -> Dict:
        """
        Automatically mine ALL portals that have URLs.
        Runs on schedule via nexus_scheduler.py.
        Skips portals without URLs.
        """
        
        try:
            portals = self.airtable.get_all_records('VENDOR PORTAL')
            # Mine all portals that have a URL
            minable = [
                p for p in portals
                if p['fields'].get('PORTAL URL', '') or p['fields'].get('Portal URL', '')
            ]
            
            results = []
            total_found = 0
            errors = []
            
            for portal in minable:
                portal_name = portal['fields'].get('Portal Name', 'Unknown')
                try:
                    result = self.mine_portal_opportunities(portal['id'])
                    if result.get('error'):
                        errors.append(f"{portal_name}: {result['error']}")
                    else:
                        results.append(result)
                        total_found += result.get('opportunities_found', 0)
                        print(f"  Mined {portal_name}: {result.get('opportunities_found', 0)} opportunities")
                except Exception as e:
                    errors.append(f"{portal_name}: {str(e)}")
            
            return {
                'success': True,
                'portals_checked': len(minable),
                'portals_skipped': len(portals) - len(minable),
                'total_opportunities_found': total_found,
                'results': results,
                'errors': errors
            }
            
        except Exception as e:
            print(f"Auto-mining error: {e}")
            return {"error": str(e), "success": False}
    
    def generate_opportunity_alerts(self) -> List[Dict]:
        """
        Generate alerts for opportunities that need attention
        Returns list of urgent opportunities
        """
        
        try:
            opportunities = self.airtable.get_all_records('GPSS OPPORTUNITIES')
            forecasts = self.airtable.get_all_records('Opportunity Forecasts')
            
            alerts = []
            
            # Check for urgent deadlines
            for opp in opportunities:
                fields = opp['fields']
                deadline = fields.get('Deadline', '')
                status = fields.get('Status', '')
                
                # Add logic for urgent opportunities
                if deadline and status in ['New', 'Reviewing']:
                    # Calculate days until deadline
                    # If < 7 days, create alert
                    alerts.append({
                        'type': 'URGENT_DEADLINE',
                        'opportunity_id': opp['id'],
                        'title': fields.get('Title', ''),
                        'deadline': deadline,
                        'message': f'Deadline approaching: {deadline}'
                    })
            
            # Check for forecasted opportunities that should be posted soon
            for forecast in forecasts:
                fields = forecast['fields']
                predicted_date = fields.get('Predicted Post Date', '')
                status = fields.get('Status', '')
                
                if status == 'Watching' and predicted_date:
                    alerts.append({
                        'type': 'FORECAST_ALERT',
                        'forecast_id': forecast['id'],
                        'title': fields.get('Forecast Title', ''),
                        'predicted_date': predicted_date,
                        'message': f'Forecasted opportunity expected: {predicted_date}'
                    })
            
            return alerts
            
        except Exception as e:
            print(f"Alert generation error: {e}")
            return []

# =====================================================================
# NEXUS INVOICE GENERATOR
# =====================================================================

class InvoiceGeneratorAgent:
    """
    AI-powered Invoice Generator
    Generates government & enterprise compliant invoices from GPSS, ATLAS, and DDCSS
    """
    
    def __init__(self):
        self.airtable = AirtableClient()
        self.ai = AnthropicClient()
    
    def generate_from_opportunity(self, opportunity_id: str) -> Dict:
        """Generate invoice from GPSS opportunity"""
        try:
            # Get opportunity details
            opp_record = self.airtable.get_table("GPSS OPPORTUNITIES").get(opportunity_id)
            opp = opp_record['fields']
            
            # Prepare invoice data
            invoice_data = {
                "Source System": "GPSS",
                "Opportunity": [opportunity_id],
                "Client Name": opp.get("AGENCY NAME", ""),
                "Client Type": self._determine_client_type(opp.get("AGENCY NAME", "")),
                "Contract Number": opp.get("SOLICITATION NUMBER", ""),
                "Contract Type": self._determine_contract_type(opp.get("Type", "")),
                "CAGE Code": "8UMX3",
                "Invoice Status": "Draft",
                "Invoice Date": datetime.now().strftime("%Y-%m-%d"),
                "Due Date": self._calculate_due_date(30),  # Net 30 default
                "Payment Terms": "Net 30"
            }
            
            # Use AI to generate line items and calculate amounts
            invoice_details = self._ai_generate_invoice_details(opp, "GPSS")
            invoice_data.update(invoice_details)
            
            # Create invoice in Airtable
            invoice_record = self.airtable.create_record("Invoices", invoice_data)
            
            return {
                "success": True,
                "invoice_id": invoice_record['id'],
                "invoice_number": invoice_record['fields'].get('Invoice Number'),
                "total_amount": invoice_record['fields'].get('Total Amount'),
                "message": "Invoice generated successfully from opportunity"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to generate invoice from opportunity"
            }
    
    def generate_from_project(self, project_id: str) -> Dict:
        """Generate invoice from ATLAS project"""
        try:
            # Get project details
            project_record = self.airtable.get_table("ATLAS Projects").get(project_id)
            project = project_record['fields']
            
            # Prepare invoice data
            invoice_data = {
                "Source System": "ATLAS",
                "Project": [project_id],
                "Client Name": project.get("Client Name", ""),
                "Client Type": self._determine_client_type(project.get("Client Name", "")),
                "Project Name": project.get("Project Name", ""),
                "Contract Number": project.get("Contract Number", ""),
                "Invoice Status": "Draft",
                "Invoice Date": datetime.now().strftime("%Y-%m-%d"),
                "Due Date": self._calculate_due_date(30),
                "Payment Terms": "Net 30",
                "CAGE Code": "8UMX3"
            }
            
            # Use AI to generate line items and calculate amounts
            invoice_details = self._ai_generate_invoice_details(project, "ATLAS")
            invoice_data.update(invoice_details)
            
            # Create invoice in Airtable
            invoice_record = self.airtable.create_record("Invoices", invoice_data)
            
            return {
                "success": True,
                "invoice_id": invoice_record['id'],
                "invoice_number": invoice_record['fields'].get('Invoice Number'),
                "total_amount": invoice_record['fields'].get('Total Amount'),
                "message": "Invoice generated successfully from project"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to generate invoice from project"
            }
    
    def generate_from_prospect(self, prospect_id: str) -> Dict:
        """Generate invoice from DDCSS prospect"""
        try:
            # Get prospect details
            prospect_record = self.airtable.get_table("DDCSS Prospects").get(prospect_id)
            prospect = prospect_record['fields']
            
            # Prepare invoice data
            invoice_data = {
                "Source System": "DDCSS",
                "Prospect": [prospect_id],
                "Client Name": prospect.get("Company Name", ""),
                "Client Type": "Enterprise - Private",  # DDCSS is for corporate
                "Project Name": prospect.get("Project Type", ""),
                "Invoice Status": "Draft",
                "Invoice Date": datetime.now().strftime("%Y-%m-%d"),
                "Due Date": self._calculate_due_date(30),
                "Payment Terms": "Net 30"
            }
            
            # Use AI to generate line items and calculate amounts
            invoice_details = self._ai_generate_invoice_details(prospect, "DDCSS")
            invoice_data.update(invoice_details)
            
            # Create invoice in Airtable
            invoice_record = self.airtable.create_record("Invoices", invoice_data)
            
            return {
                "success": True,
                "invoice_id": invoice_record['id'],
                "invoice_number": invoice_record['fields'].get('Invoice Number'),
                "total_amount": invoice_record['fields'].get('Total Amount'),
                "message": "Invoice generated successfully from prospect"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to generate invoice from prospect"
            }
    
    def _ai_generate_invoice_details(self, source_data: Dict, source_system: str) -> Dict:
        """Use AI to generate line items and calculate amounts"""
        
        prompt = f"""You are generating an invoice for Dee Davis Inc.

SOURCE SYSTEM: {source_system}
SOURCE DATA: {json.dumps(source_data, indent=2)}

Generate professional invoice line items and calculate amounts.

Return ONLY a valid JSON object with this exact structure:
{{
    "Line Items": "1. [Service/Product] - [Description] = $X.XX\\n2. [Service/Product] - [Description] = $X.XX\\n...",
    "Subtotal": 1000.00,
    "Shipping & Handling": 0.00,
    "Tax Rate": 0.00,
    "Invoice Notes": "Professional notes about this invoice"
}}

IMPORTANT:
- For government contracts (GPSS/ATLAS), Tax Rate should be 0.00 (tax-exempt)
- For private sector (DDCSS), Tax Rate should be 0.06 (6%) unless in tax-exempt state
- Shipping & Handling: Add if physical goods involved
- Line Items: Itemized list with quantities, rates, amounts
- Be professional, accurate, and government-compliant

Generate the invoice details now:"""
        
        try:
            response = self.ai.complete(prompt, max_tokens=2000)
            
            # Parse AI response
            invoice_details = json.loads(response)
            
            # Validate and return
            return {
                "Line Items": invoice_details.get("Line Items", ""),
                "Subtotal": float(invoice_details.get("Subtotal", 0)),
                "Shipping & Handling": float(invoice_details.get("Shipping & Handling", 0)),
                "Tax Rate": float(invoice_details.get("Tax Rate", 0)),
                "Invoice Notes": invoice_details.get("Invoice Notes", "")
            }
            
        except Exception as e:
            print(f"AI invoice generation error: {e}")
            # Return default values if AI fails
            return {
                "Line Items": "1. Professional Services = $1,000.00",
                "Subtotal": 1000.00,
                "Shipping & Handling": 0.00,
                "Tax Rate": 0.00,
                "Invoice Notes": "Invoice generated automatically"
            }
    
    def _determine_client_type(self, client_name: str) -> str:
        """Determine if client is government or private"""
        gov_keywords = ['department', 'dept', 'agency', 'office of', 'bureau', 'administration', 
                       'commission', 'government', 'federal', 'state', 'county', 'city', 'municipal']
        
        client_lower = client_name.lower()
        for keyword in gov_keywords:
            if keyword in client_lower:
                # Determine federal vs state vs local
                if any(word in client_lower for word in ['federal', 'u.s.', 'united states', 'dept of', 'va ', 'dod', 'hhs']):
                    return "Government - Federal"
                elif any(word in client_lower for word in ['state', 'commonwealth']):
                    return "Government - State"
                else:
                    return "Government - Local"
        
        return "Enterprise - Private"
    
    def _determine_contract_type(self, type_string: str) -> str:
        """Determine contract type from opportunity type"""
        type_lower = type_string.lower()
        
        if 'fixed' in type_lower or 'ffp' in type_lower:
            return "FFP (Fixed Price)"
        elif 'time' in type_lower or 't&m' in type_lower or 'material' in type_lower:
            return "T&M (Time & Materials)"
        elif 'cost plus' in type_lower or 'cost-plus' in type_lower:
            return "Cost Plus"
        elif 'idiq' in type_lower:
            return "IDIQ"
        elif 'task order' in type_lower or 'to' in type_lower:
            return "Task Order"
        elif 'bpa' in type_lower:
            return "BPA Call"
        else:
            return "FFP (Fixed Price)"  # Default
    
    def _calculate_due_date(self, days: int) -> str:
        """Calculate due date from today"""
        from datetime import timedelta
        due_date = datetime.now() + timedelta(days=days)
        return due_date.strftime("%Y-%m-%d")
    
    def update_invoice(self, invoice_id: str, updates: Dict) -> Dict:
        """Update an existing invoice"""
        try:
            updated = self.airtable.update_record("Invoices", invoice_id, updates)
            
            return {
                "success": True,
                "invoice_id": updated['id'],
                "message": "Invoice updated successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to update invoice"
            }
    
    def get_invoice(self, invoice_id: str) -> Dict:
        """Get invoice details"""
        try:
            invoice_record = self.airtable.get_table("Invoices").get(invoice_id)
            
            return {
                "success": True,
                "invoice": invoice_record['fields'],
                "invoice_id": invoice_record['id']
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to get invoice"
            }
    
    def get_all_invoices(self, filters: Dict = None) -> Dict:
        """Get all invoices with optional filters"""
        try:
            # Build Airtable formula if filters provided
            formula = None
            if filters:
                conditions = []
                if filters.get('status'):
                    conditions.append(f"{{Invoice Status}} = '{filters['status']}'")
                if filters.get('source_system'):
                    conditions.append(f"{{Source System}} = '{filters['source_system']}'")
                if filters.get('client_type'):
                    conditions.append(f"{{Client Type}} = '{filters['client_type']}'")
                
                if conditions:
                    formula = "AND(" + ", ".join(conditions) + ")"
            
            if formula:
                invoices = self.airtable.search_records("Invoices", formula)
            else:
                invoices = self.airtable.get_all_records("Invoices")
            
            return {
                "success": True,
                "invoices": [{"id": inv['id'], **inv['fields']} for inv in invoices],
                "count": len(invoices)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to get invoices"
            }
    
    def delete_invoice(self, invoice_id: str) -> Dict:
        """Delete an invoice"""
        try:
            self.airtable.get_table("Invoices").delete(invoice_id)
            
            return {
                "success": True,
                "message": "Invoice deleted successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to delete invoice"
            }

# =====================================================================
# AI RECOMMENDATION & APPROVAL SYSTEM
# =====================================================================

class AIRecommendationAgent:
    """
    AI Recommendation Agent - Suggests actions, user approves/denies
    
    Core Philosophy:
    - AI analyzes and suggests the BEST option with reasoning
    - User reviews and decides: Yay, Nay, or Modify
    - System learns from user decisions to improve over time
    """
    
    def __init__(self):
        self.airtable = AirtableClient()
        self.ai = AnthropicClient()
    
    def analyze_capability_gap(self, opportunity_id: str) -> Dict:
        """
        Analyze RFP requirements vs company capabilities
        Returns: Gap analysis with recommendation to self-perform or partner
        """
        try:
            # Get opportunity details
            opp_record = self.airtable.get_table("GPSS OPPORTUNITIES").get(opportunity_id)
            opp = opp_record['fields']
            
            # Get company capabilities
            capabilities = self._get_company_capabilities()
            
            # AI analyzes the gap
            prompt = f"""
            Analyze this government contract opportunity and determine if we should self-perform or partner with a subcontractor.
            
            OPPORTUNITY:
            Title: {opp.get('TITLE', 'N/A')}
            Description: {opp.get('DESCRIPTION', 'N/A')}
            Type: {opp.get('Type', 'N/A')}
            Set-Aside: {opp.get('SET_ASIDE', 'N/A')}
            
            OUR COMPANY CAPABILITIES:
            {json.dumps(capabilities, indent=2)}
            
            ANALYZE:
            1. What skills/capabilities are required for this contract?
            2. What can WE do (list specific capabilities we have)?
            3. What do we NEED (skills/capabilities we're missing)?
            4. Recommendation: Self-perform 100% OR Partner with subcontractor?
            5. If partner recommended: What % should we do vs subcontractor? (Must meet 50% self-performance rule for small business set-asides)
            6. Confidence level (0-100): How confident are you in this recommendation?
            7. Risk assessment: What are the risks of each approach?
            
            Return JSON format:
            {{
                "required_capabilities": ["skill1", "skill2", ...],
                "we_can_do": ["skill1", ...],
                "we_can_do_percentage": 70,
                "we_need": ["skill3", ...],
                "recommendation": "self_perform" or "partner",
                "recommended_workshare": {{"us": 60, "subcontractor": 40}},
                "confidence": 85,
                "reasoning": "Detailed explanation...",
                "risks_self_perform": ["risk1", ...],
                "risks_partner": ["risk1", ...],
                "compliance_check": {{"meets_50_percent_rule": true, "notes": "..."}}
            }}
            """
            
            analysis = self.ai.generate_with_json(prompt, model="claude-sonnet-4-20250514")
            
            # Add metadata
            analysis['opportunity_id'] = opportunity_id
            analysis['analyzed_at'] = datetime.now().isoformat()
            analysis['status'] = 'pending_approval'
            
            # Store recommendation for tracking
            recommendation_record = self.airtable.create_record("AI RECOMMENDATIONS", {
                "OPPORTUNITY": [opportunity_id],
                "TYPE": "Capability Gap Analysis",
                "RECOMMENDATION": analysis.get('recommendation', '').upper(),
                "CONFIDENCE": analysis.get('confidence', 0),
                "REASONING": analysis.get('reasoning', ''),
                "STATUS": "Pending Approval",
                "CREATED": datetime.now().isoformat()
            })
            
            analysis['recommendation_id'] = recommendation_record['id']
            
            return {
                "success": True,
                "analysis": analysis,
                "message": "AI recommendation ready for your review"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to analyze capability gap"
            }
    
    def _opportunity_fields_for_sub_ranking(self, opportunity_id: str) -> Dict:
        """Load opportunity text/location for job-specific sub ranking."""
        fields = {}
        for table in ('GPSS OPPORTUNITIES', 'Opportunities', 'GPSS Opportunities'):
            try:
                rec = self.airtable.get_record(table, opportunity_id)
                if rec and rec.get('fields'):
                    fields = dict(rec['fields'])
                    break
            except Exception:
                continue
        return fields

    @staticmethod
    def _sub_row_company_name(sub: Dict) -> str:
        return (sub.get('COMPANY NAME') or sub.get('COMPANY_NAME') or '').strip() or 'Unknown'

    @staticmethod
    def _sub_row_should_skip(sub: Dict) -> bool:
        """Exclude only explicitly disqualified rows; do not require Active-only."""
        st = (sub.get('STATUS') or sub.get('RELATIONSHIP STATUS') or '').strip().lower()
        if not st:
            return False
        blocked = {'inactive', 'disqualified', 'blacklisted', 'do not use', 'archived', 'closed — do not use'}
        return st in blocked

    def recommend_subcontractors(
        self,
        opportunity_id: str,
        needed_skills: List[str],
        contract_value: float = None,
        minimal_research: bool = True,
    ) -> Dict:
        """
        Rank subcontractors for best fit on this job. When minimal_research=True, NEXUS pulls
        a homepage excerpt and optional Google CSE snippets so scoring is not only stale DB fields.
        """
        try:
            miner = GPSSSubcontractorMiner()
            opp = self._opportunity_fields_for_sub_ranking(opportunity_id)
            title = opp.get('TITLE') or opp.get('Title') or opp.get('OPPORTUNITY TITLE') or ''
            desc = opp.get('DESCRIPTION') or opp.get('Description') or opp.get('description') or ''
            job_location = (
                opp.get('PLACE OF PERFORMANCE') or opp.get('Place of Performance')
                or opp.get('LOCATION') or opp.get('State') or opp.get('STATE') or ''
            )
            if isinstance(job_location, list):
                job_location = ', '.join(str(x) for x in job_location if x)
            job_summary = f"{title}\n{desc}".strip()[:6000]

            all_subs = self.airtable.get_all_records("GPSS SUBCONTRACTORS")
            if not all_subs:
                return {
                    "success": False,
                    "message": "No subcontractors found in database. Mine or import subs first, then re-run ranking.",
                    "recommended_subcontractors": [],
                }

            scored_subs = []
            for sub_record in all_subs:
                sub = sub_record['fields']
                if self._sub_row_should_skip(sub):
                    continue

                cname = self._sub_row_company_name(sub)
                website = (sub.get('WEBSITE') or sub.get('Website') or '').strip()
                caps = sub.get('CAPABILITIES') or sub.get('DESCRIPTION') or sub.get('Description') or ''
                past = sub.get('PAST_PERFORMANCE') or sub.get('PAST PERFORMANCE') or ''
                rating = sub.get('RATING') or sub.get('RELIABILITY RATING') or 'N/A'
                loc = sub.get('LOCATION') or f"{sub.get('CITY', '')} {sub.get('STATE', '')}".strip()
                certs = sub.get('CERTIFICATIONS') or ''
                contact = sub.get('CONTACT_EMAIL') or sub.get('EMAIL') or ''

                research = {
                    "minimal_research_enabled": bool(minimal_research),
                    "sources_used": [],
                    "research_summary": "",
                    "website_excerpt_preview": "",
                    "cse_highlights": [],
                }
                if minimal_research:
                    full_research = miner.minimal_research_for_ranking(
                        company_name=cname,
                        website=website,
                        needed_skills=needed_skills,
                        job_location=str(job_location) if job_location else '',
                        job_summary=job_summary,
                    )
                    research["sources_used"] = full_research.get("sources_used") or []
                    research["research_summary"] = full_research.get("research_summary") or ""
                    excerpt = full_research.get("website_excerpt") or ""
                    research["website_excerpt_preview"] = excerpt.replace("\n", " ")[:900]
                    research["cse_highlights"] = [
                        {"title": x.get("title"), "snippet": x.get("snippet"), "link": x.get("link")}
                        for x in (full_research.get("cse_results") or [])[:4]
                    ]
                    research["website_fetch_error"] = full_research.get("website_fetch_error")

                score_prompt = f"""
You rank subcontractors for a SPECIFIC contract. Decide who is BEST FOR THIS JOB — not who has
the nicest database row. Use INTERNAL RECORD + FRESH RESEARCH; if they conflict, trust public
signals from research for current services and geography, and note uncertainty.

JOB (prime is Dee Davis Inc. — do not reveal buyer/agency names to subs in real outreach):
Required skills / scope focus: {', '.join(needed_skills)}
Contract value (if known): ${contract_value if contract_value else 'Unknown'}
Place / region context: {job_location or 'Not specified'}
Opportunity summary:
{job_summary or '(No opportunity text loaded — rely on skills + research.)'}

INTERNAL DATABASE RECORD:
Company: {cname}
Capabilities / notes: {caps}
Past performance (may be stale): {past}
Rating field: {rating}
Location fields: {loc}
Certifications: {certs}
Website on file: {website or 'None'}

FRESH MINIMAL RESEARCH (homepage excerpt + short web snippets; may be empty):
{research.get('research_summary') or 'No live research — score conservatively and flag data gaps.'}
Website excerpt (truncated): {research.get('website_excerpt_preview') or 'None'}
Search snippets: {json.dumps(research.get('cse_highlights'), indent=0) if research.get('cse_highlights') else 'None'}

Score 0-100 for FIT FOR THIS JOB:
- Match of services to required skills and region (highest weight)
- Evidence from research that they still perform this work (not a dead site or unrelated business)
- Past performance / rating / certs when credible; penalize if research contradicts the record
- If research is empty, cap score at 78 unless the internal record is exceptionally strong, and say why

Return JSON only:
{{
  "score": 85,
  "reason": "2-4 sentences: why this score for THIS job, citing research if used.",
  "strengths": ["..."],
  "concerns": ["..."],
  "research_used": "how research influenced the score (or 'none available')"
}}
"""

                try:
                    scoring = self.ai.generate_with_json(score_prompt, model="claude-sonnet-4-20250514")
                    scored_subs.append({
                        "id": sub_record['id'],
                        "name": cname,
                        "score": scoring.get('score', 0),
                        "reason": scoring.get('reason', ''),
                        "strengths": scoring.get('strengths', []),
                        "concerns": scoring.get('concerns', []),
                        "capabilities": caps,
                        "rating": rating,
                        "location": loc,
                        "contact": contact,
                        "website": website,
                        "research": research,
                        "research_used": scoring.get('research_used', ''),
                    })
                except Exception as e:
                    print(f"Error scoring subcontractor {cname}: {e}")
                    continue

            scored_subs.sort(key=lambda x: x['score'], reverse=True)
            top_5 = scored_subs[:5]

            if top_5:
                reasoning_block = top_5[0]['reason']
                if top_5[0].get('research_used'):
                    reasoning_block = f"{reasoning_block}\n\nResearch note: {top_5[0]['research_used']}"
                recommendation_record = self.airtable.create_record("AI RECOMMENDATIONS", {
                    "OPPORTUNITY": [opportunity_id],
                    "TYPE": "Subcontractor Recommendation",
                    "RECOMMENDATION": f"Top choice: {top_5[0]['name']}",
                    "CONFIDENCE": top_5[0]['score'],
                    "REASONING": reasoning_block[:95000],
                    "STATUS": "Pending Approval",
                    "CREATED": datetime.now().isoformat()
                })

                return {
                    "success": True,
                    "recommended_subcontractors": top_5,
                    "total_ranked": len(scored_subs),
                    "recommendation_id": recommendation_record['id'],
                    "ai_top_pick": top_5[0] if top_5 else None,
                    "minimal_research": minimal_research,
                    "message": (
                        f"Ranked {len(scored_subs)} subcontractors for this job (research={'on' if minimal_research else 'off'}). "
                        f"Top pick: {top_5[0]['name']} ({top_5[0]['score']}/100)."
                    ),
                }

            return {
                "success": False,
                "message": "No suitable subcontractors found after ranking",
                "recommended_subcontractors": [],
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to recommend subcontractors"
            }
    
    def recommend_suppliers(self, opportunity_id: str, product_description: str) -> Dict:
        """
        Find and rank suppliers for product-based opportunities
        Returns: Top 10 recommended suppliers with AI reasoning
        """
        try:
            # Search supplier database
            all_suppliers = self.airtable.get_all_records("GPSS SUPPLIERS")
            
            if not all_suppliers:
                return {
                    "success": False,
                    "message": "No suppliers found. Run supplier mining first.",
                    "recommended_suppliers": []
                }
            
            # AI scores each supplier
            scored_suppliers = []
            for sup_record in all_suppliers:
                sup = sup_record['fields']
                
                # AI scores this supplier
                score_prompt = f"""
                Score this supplier for product: {product_description}
                
                SUPPLIER:
                Name: {sup.get('COMPANY_NAME', 'N/A')}
                Products: {sup.get('PRODUCTS', 'N/A')}
                Category: {sup.get('CATEGORY', 'N/A')}
                Rating: {sup.get('RATING', 'N/A')}
                Payment Terms: {sup.get('PAYMENT_TERMS', 'N/A')}
                GSA Schedule: {sup.get('GSA_SCHEDULE', 'N/A')}
                
                Score 0-100 based on:
                - Product match
                - GSA status (important for government contracts)
                - Payment terms (Net 30 preferred)
                - Rating/reputation
                
                Return JSON:
                {{
                    "score": 88,
                    "reason": "Perfect product match, GSA approved, Net 30 terms",
                    "estimated_pricing": "competitive" or "above_market" or "below_market"
                }}
                """
                
                try:
                    scoring = self.ai.generate_with_json(score_prompt, model="claude-sonnet-4-20250514")
                    ai_score = scoring.get('score', 0)
                    
                    # Factor in OVERALL RATING (1-5 stars) from past performance
                    # Each star is worth up to 10 bonus points
                    overall_rating = sup_record['fields'].get('OVERALL RATING', 0) or 0
                    performance_bonus = min(overall_rating * 2, 10)  # Max 10 pts bonus
                    adjusted_score = min(ai_score + performance_bonus, 100)
                    
                    scored_suppliers.append({
                        "id": sup_record['id'],
                        "name": sup.get('COMPANY_NAME', 'Unknown'),
                        "score": adjusted_score,
                        "ai_score": ai_score,
                        "performance_rating": overall_rating,
                        "reason": scoring.get('reason', ''),
                        "pricing_estimate": scoring.get('estimated_pricing', 'unknown'),
                        "gsa_schedule": sup.get('GSA_SCHEDULE', 'No'),
                        "payment_terms": sup.get('PAYMENT_TERMS', 'Unknown'),
                        "rating": overall_rating if overall_rating else 'N/A',
                        "contact": sup.get('CONTACT_EMAIL', '')
                    })
                except Exception as e:
                    print(f"Error scoring supplier {sup.get('COMPANY_NAME')}: {e}")
                    continue
            
            # Sort by score
            scored_suppliers.sort(key=lambda x: x['score'], reverse=True)
            top_10 = scored_suppliers[:10]
            
            # Store recommendation
            if top_10:
                recommendation_record = self.airtable.create_record("AI RECOMMENDATIONS", {
                    "OPPORTUNITY": [opportunity_id],
                    "TYPE": "Supplier Recommendation",
                    "RECOMMENDATION": f"Top choice: {top_10[0]['name']}",
                    "CONFIDENCE": top_10[0]['score'],
                    "REASONING": top_10[0]['reason'],
                    "STATUS": "Pending Approval",
                    "CREATED": datetime.now().isoformat()
                })
                
                return {
                    "success": True,
                    "recommended_suppliers": top_10,
                    "total_found": len(scored_suppliers),
                    "recommendation_id": recommendation_record['id'],
                    "ai_top_pick": top_10[0] if top_10 else None,
                    "message": f"AI analyzed {len(scored_suppliers)} suppliers. Top recommendation: {top_10[0]['name']} (score: {top_10[0]['score']}/100)"
                }
            else:
                return {
                    "success": False,
                    "message": "No suitable suppliers found",
                    "recommended_suppliers": []
                }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to recommend suppliers"
            }
    
    def approve_recommendation(self, recommendation_id: str, user_decision: str, user_notes: str = "", selected_id: str = None) -> Dict:
        """
        User approves, denies, or modifies AI recommendation
        
        Args:
            recommendation_id: The AI recommendation record ID
            user_decision: "approved", "denied", or "modified"
            user_notes: User's reasoning for the decision
            selected_id: If user picked different option, the ID of what they selected
        """
        try:
            # Get recommendation
            rec_record = self.airtable.get_table("AI RECOMMENDATIONS").get(recommendation_id)
            rec = rec_record['fields']
            
            # Update status
            updates = {
                "STATUS": user_decision.capitalize(),
                "USER_DECISION": user_decision.upper(),
                "USER_NOTES": user_notes,
                "DECIDED_AT": datetime.now().isoformat()
            }
            
            if selected_id:
                updates["SELECTED_OPTION"] = selected_id
            
            self.airtable.update_record("AI RECOMMENDATIONS", recommendation_id, updates)
            
            # Learn from decision (update confidence scoring)
            self._learn_from_decision(recommendation_id, user_decision, rec)
            
            return {
                "success": True,
                "decision": user_decision,
                "message": f"Recommendation {user_decision}. System learning from your decision."
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to process decision"
            }
    
    def get_pending_recommendations(self, opportunity_id: str = None) -> Dict:
        """Get all pending recommendations for review"""
        try:
            if opportunity_id:
                formula = f"AND({{OPPORTUNITY}}='{opportunity_id}', {{STATUS}}='Pending Approval')"
                recs = self.airtable.search_records("AI RECOMMENDATIONS", formula)
            else:
                formula = "{STATUS}='Pending Approval'"
                recs = self.airtable.search_records("AI RECOMMENDATIONS", formula)
            
            return {
                "success": True,
                "pending_recommendations": [{"id": r['id'], **r['fields']} for r in recs],
                "count": len(recs)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to get recommendations"
            }
    
    def calculate_compliance(self, contract_value: float, your_work_value: float, sub_work_value: float) -> Dict:
        """
        Calculate workshare percentages and compliance with 50% self-performance rule
        """
        try:
            total = your_work_value + sub_work_value
            
            if total == 0:
                return {
                    "success": False,
                    "message": "Total value cannot be zero"
                }
            
            your_percentage = (your_work_value / total) * 100
            sub_percentage = (sub_work_value / total) * 100
            margin = contract_value - total
            margin_percentage = (margin / contract_value) * 100 if contract_value > 0 else 0
            
            meets_50_rule = your_percentage >= 50
            
            return {
                "success": True,
                "compliance": {
                    "contract_value": contract_value,
                    "your_work": your_work_value,
                    "your_percentage": round(your_percentage, 1),
                    "subcontractor_work": sub_work_value,
                    "subcontractor_percentage": round(sub_percentage, 1),
                    "margin": margin,
                    "margin_percentage": round(margin_percentage, 1),
                    "meets_50_percent_rule": meets_50_rule,
                    "compliant": meets_50_rule,
                    "status": "✅ Compliant" if meets_50_rule else "❌ Non-Compliant",
                    "message": f"You perform {round(your_percentage, 1)}% - " + 
                              ("Meets 50% rule" if meets_50_rule else "FAILS 50% rule - adjust workshare")
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to calculate compliance"
            }
    
    def _get_company_capabilities(self) -> Dict:
        """Get company capabilities from database"""
        try:
            # Try to get from COMPANY CAPABILITIES table
            capabilities = self.airtable.get_all_records("COMPANY CAPABILITIES")
            
            if capabilities:
                return {
                    "capabilities": [
                        {
                            "name": cap['fields'].get('CAPABILITY_NAME', ''),
                            "level": cap['fields'].get('SKILL_LEVEL', ''),
                            "capacity": cap['fields'].get('CAPACITY', '')
                        }
                        for cap in capabilities
                    ]
                }
            else:
                # Default capabilities if table doesn't exist
                return {
                    "capabilities": [
                        {"name": "Project Management", "level": "Expert", "capacity": "High"},
                        {"name": "Government Contracting", "level": "Expert", "capacity": "High"},
                        {"name": "Proposal Writing", "level": "Expert", "capacity": "High"},
                        {"name": "Product Sourcing", "level": "Expert", "capacity": "High"}
                    ],
                    "note": "Using default capabilities. Create COMPANY CAPABILITIES table to customize."
                }
        except Exception as e:
            # Return defaults if table doesn't exist yet
            return {
                "capabilities": [
                    {"name": "Project Management", "level": "Expert", "capacity": "High"},
                    {"name": "Government Contracting", "level": "Expert", "capacity": "High"}
                ],
                "note": "COMPANY CAPABILITIES table not found. Using defaults."
            }
    
    def _learn_from_decision(self, recommendation_id: str, user_decision: str, recommendation: Dict):
        """Learn from user's decision to improve future recommendations"""
        try:
            # Track approval patterns
            # This could be expanded to update scoring algorithms based on patterns
            # For now, just log the decision for future analysis
            
            learning_data = {
                "RECOMMENDATION_ID": recommendation_id,
                "DECISION": user_decision.upper(),
                "TYPE": recommendation.get('TYPE', ''),
                "AI_CONFIDENCE": recommendation.get('CONFIDENCE', 0),
                "TIMESTAMP": datetime.now().isoformat()
            }
            
            # Store in learning table (if exists)
            try:
                self.airtable.create_record("AI LEARNING", learning_data)
            except:
                # Table doesn't exist yet - that's okay
                pass
                
        except Exception as e:
            print(f"Learning error: {e}")

# =====================================================================
# API ENDPOINTS (for Make.com webhooks)
# =====================================================================

def handle_document_upload(document_text: str, document_name: str) -> Dict:
    """
    Handle document upload and extract contacts
    Called by Make.com webhook
    """
    extractor = DocumentContactExtractor()
    
    # Extract contacts
    extracted = extractor.extract_from_text(document_text, document_name)

    # Store in Airtable
    stored = extractor.store_contacts(extracted.get('contacts', []), document_name)
    
    return {
        "success": True,
        "contacts_found": len(extracted.get('contacts', [])),
        "contacts_stored": len(stored),
        "metadata": extracted.get('document_metadata', {}),
        "stored_contacts": stored
    }


def handle_qualify_opportunity(opportunity_id: str) -> Dict:
    """
    Qualify an opportunity
    Called by Make.com when new opportunity created
    """
    agent = GPSSAgent2()
    return agent.qualify_opportunity(opportunity_id)


def handle_generate_quote(opportunity_id: str) -> Dict:
    """
    Generate quote for opportunity
    Called by Make.com when opportunity approved
    """
    agent = GPSSAgent3()
    return agent.generate_quote(opportunity_id)

# =====================================================================
# DDCSS API HANDLERS
# =====================================================================

def handle_ddcss_qualify_prospect(prospect_id: str) -> Dict:
    """
    Qualify a corporate prospect
    Returns: qualification analysis, ICP fit, recommended approach
    """
    agent = DDCSSAgent1()
    return agent.qualify_prospect(prospect_id)


def handle_ddcss_generate_blueprint(prospect_id: str, framework_type: str = "ALIGN") -> Dict:
    """
    Generate a customized Blueprint Framework
    Framework types: ALIGN, DEFINE, DESIGN, SHINE
    """
    agent = DDCSSAgent2()
    return agent.generate_blueprint(prospect_id, framework_type)


def handle_ddcss_analyze_response(email_content: str, prospect_id: str = None) -> Dict:
    """
    Analyze inbound email response using AI
    Returns: sentiment, intent, recommended actions
    """
    agent = DDCSSAgent3()
    return agent.analyze_response(email_content, prospect_id)


def handle_ddcss_mine_prime_contractors(min_contract_value: int = 10000000, limit: int = 50) -> Dict:
    """
    Mine prime contractors from USASpending.gov
    Finds companies with federal contracts who need diversity suppliers
    
    Args:
        min_contract_value: Minimum contract value (default: $10M)
        limit: Max prospects to find (default: 50)
    
    Returns: Mining results with prospects created
    """
    miner = PrimeContractorMiner()
    return miner.mine_prime_contractors(min_contract_value, limit)


# =====================================================================
# ATLAS PM API HANDLERS
# =====================================================================

def handle_atlas_analyze_rfp(rfp_content: str, project_id: str = None) -> Dict:
    """
    Analyze RFP content and extract requirements
    Returns: comprehensive RFP analysis, win strategy, risk assessment
    """
    agent = ATLASAgent1()
    return agent.analyze_rfp(rfp_content, project_id)


def handle_atlas_generate_wbs(project_id: str) -> Dict:
    """
    Generate Work Breakdown Structure for project
    Returns: detailed WBS with tasks, dependencies, resources
    """
    agent = ATLASAgent2()
    return agent.generate_wbs(project_id)


def handle_atlas_analyze_change_request(change_description: str, project_id: str) -> Dict:
    """
    Analyze change request and provide impact assessment
    Returns: impact analysis, recommendations, implementation plan
    """
    agent = ATLASAgent3()
    return agent.analyze_change_request(change_description, project_id)


# =====================================================================
# LBPC (LANCASTER BANQUES P.C.) - SURPLUS RECOVERY SYSTEM
# =====================================================================

class LBPCLeadMiner:
    """Mine surplus recovery leads from county/state websites"""
    
    def __init__(self):
        self.airtable_client = AirtableClient()
    
    def calculate_priority_score(self, lead_data: Dict) -> int:
        """Calculate 0-100 priority score for a lead"""
        score = 0
        
        # Surplus amount (0-40 points)
        amount = float(lead_data.get('Surplus Amount', 0))
        if amount >= 50000:
            score += 40
        elif amount >= 25000:
            score += 30
        elif amount >= 10000:
            score += 20
        else:
            score += 10
        
        # Has contact info (0-30 points)
        if lead_data.get('Contact Email'):
            score += 15
        if lead_data.get('Contact Phone'):
            score += 15
        
        # Home state bonus (0-10 points)
        if lead_data.get('State') in ['MI', 'GA', 'MD', 'TX', 'CA', 'IL']:
            score += 10
        
        # Has case number (0-10 points)
        if lead_data.get('Case Number'):
            score += 10
        
        return min(score, 100)
    
    def clean_lead_data(self, raw_lead: Dict) -> Dict:
        """Clean and normalize lead data"""
        cleaned = {
            'Client Name': str(raw_lead.get('client_name', '')).strip(),
            'Property Address': str(raw_lead.get('property', '')).strip(),
            'City': str(raw_lead.get('city', '')).strip(),
            'County': str(raw_lead.get('county', '')).strip(),
            'State': str(raw_lead.get('state', '')).strip().upper(),
            'Zip Code': str(raw_lead.get('zip_code', '')).strip(),
            'Surplus Amount': float(raw_lead.get('surplus_amount', 0)),
            'Case Number': str(raw_lead.get('case_number', '')).strip(),
            'Contact Phone': str(raw_lead.get('phone', '')).strip(),
            'Contact Email': str(raw_lead.get('email', '')).strip(),
            'Lead Source': raw_lead.get('source', 'Manual Entry'),
            'Source URL': raw_lead.get('source_url', ''),
            'Status': 'New',
            'Lead Stage': 'Cold',
            'Date Discovered': datetime.now().isoformat()
        }
        
        # Calculate priority score
        cleaned['Priority Score'] = self.calculate_priority_score(cleaned)
        
        # Calculate win probability (simplified for now)
        cleaned['Win Probability'] = min(cleaned['Priority Score'] + 10, 100)
        
        return cleaned
    
    def parse_csv_data(self, csv_content: str, county: str, state: str) -> List[Dict]:
        """Parse CSV data from uploaded file or downloaded county list"""
        import csv
        from io import StringIO
        
        leads = []
        reader = csv.DictReader(StringIO(csv_content))
        
        for row in reader:
            # Flexible field mapping (handles various CSV formats)
            raw_lead = {
                'client_name': (
                    row.get('Owner Name') or 
                    row.get('Property Owner') or 
                    row.get('Name') or 
                    row.get('CLIENT NAME') or ''
                ),
                'property': (
                    row.get('Property Address') or 
                    row.get('Address') or 
                    row.get('PROPERTY ADDRESS') or ''
                ),
                'city': row.get('City') or row.get('CITY') or '',
                'county': county,
                'state': state,
                'zip_code': row.get('ZIP') or row.get('Zip Code') or '',
                'surplus_amount': float(
                    str(row.get('Surplus Amount') or 
                        row.get('Excess Proceeds') or 
                        row.get('Overage') or '0')
                    .replace('$', '').replace(',', '').strip() or '0'
                ),
                'case_number': (
                    row.get('Case Number') or 
                    row.get('Case ID') or 
                    row.get('Parcel ID') or ''
                ),
                'phone': row.get('Phone') or row.get('Contact Phone') or '',
                'email': row.get('Email') or row.get('Contact Email') or '',
                'source': f'{county} County {state} - CSV Import',
                'source_url': ''
            }
            
            # Only add if has minimum required data
            if raw_lead['client_name'] and raw_lead['surplus_amount'] > 0:
                cleaned = self.clean_lead_data(raw_lead)
                leads.append(cleaned)
        
        return leads
    
    def parse_pdf_table(self, pdf_path: str, county: str, state: str) -> List[Dict]:
        """Parse surplus data from PDF tables"""
        import pdfplumber
        
        leads = []
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    tables = page.extract_tables()
                    
                    for table in tables:
                        if not table or len(table) < 2:
                            continue
                        
                        # Assume first row is headers
                        headers = [str(h).strip().lower() if h else '' for h in table[0]]
                        
                        for row in table[1:]:
                            if not row or all(not cell for cell in row):
                                continue
                            
                            # Create dict from headers and row data
                            row_data = {}
                            for i, cell in enumerate(row):
                                if i < len(headers) and headers[i]:
                                    row_data[headers[i]] = str(cell).strip() if cell else ''
                            
                            # Map to standard fields (flexible mapping)
                            raw_lead = {
                                'client_name': (
                                    row_data.get('owner name') or 
                                    row_data.get('name') or 
                                    row_data.get('property owner') or ''
                                ),
                                'property': (
                                    row_data.get('property address') or 
                                    row_data.get('address') or ''
                                ),
                                'city': row_data.get('city') or '',
                                'county': county,
                                'state': state,
                                'zip_code': row_data.get('zip') or row_data.get('zip code') or '',
                                'surplus_amount': float(
                                    str(row_data.get('surplus amount') or 
                                        row_data.get('excess proceeds') or 
                                        row_data.get('amount') or '0')
                                    .replace('$', '').replace(',', '').strip() or '0'
                                ),
                                'case_number': (
                                    row_data.get('case number') or 
                                    row_data.get('case') or 
                                    row_data.get('parcel id') or ''
                                ),
                                'source': f'{county} County {state} - PDF Import',
                                'source_url': pdf_path
                            }
                            
                            if raw_lead['client_name'] and raw_lead['surplus_amount'] > 0:
                                cleaned = self.clean_lead_data(raw_lead)
                                leads.append(cleaned)
        
        except Exception as e:
            print(f"Error parsing PDF: {e}")
        
        return leads
    
    def scrape_wayne_county_mi(self) -> List[Dict]:
        """Scrape surplus leads from Wayne County, Michigan"""
        import requests
        from bs4 import BeautifulSoup
        
        leads = []
        base_url = "https://www.waynecounty.com/elected/treasurer/foreclosure.aspx"
        
        try:
            response = requests.get(base_url, timeout=30)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for surplus/excess proceeds links
            pdf_links = soup.find_all('a', href=lambda x: x and ('surplus' in x.lower() or 'excess' in x.lower()))
            
            for link in pdf_links[:3]:  # Limit to 3 most recent
                pdf_url = link.get('href')
                if not pdf_url.startswith('http'):
                    pdf_url = f"https://www.waynecounty.com{pdf_url}"
                
                # Download PDF
                pdf_response = requests.get(pdf_url, timeout=30)
                temp_path = f'/tmp/wayne_surplus_{datetime.now().timestamp()}.pdf'
                
                with open(temp_path, 'wb') as f:
                    f.write(pdf_response.content)
                
                # Parse PDF
                pdf_leads = self.parse_pdf_table(temp_path, 'Wayne', 'MI')
                leads.extend(pdf_leads)
        
        except Exception as e:
            print(f"Error scraping Wayne County: {e}")
        
        return leads
    
    def scrape_fulton_county_ga(self) -> List[Dict]:
        """Scrape surplus leads from Fulton County, Georgia"""
        import requests
        from bs4 import BeautifulSoup
        
        leads = []
        base_url = "https://www.fultoncountyga.gov"
        
        try:
            # Fulton County posts surplus funds lists
            search_url = f"{base_url}/inside-fulton-county/fulton-county-departments/finance/real-estate-tax-division"
            response = requests.get(search_url, timeout=30)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for surplus-related documents
            links = soup.find_all('a', href=lambda x: x and ('surplus' in x.lower() or 'excess' in x.lower()))
            
            for link in links[:3]:
                href = link.get('href')
                if not href.startswith('http'):
                    href = f"{base_url}{href}"
                
                # Process PDF or webpage
                if href.endswith('.pdf'):
                    pdf_response = requests.get(href, timeout=30)
                    temp_path = f'/tmp/fulton_surplus_{datetime.now().timestamp()}.pdf'
                    
                    with open(temp_path, 'wb') as f:
                        f.write(pdf_response.content)
                    
                    pdf_leads = self.parse_pdf_table(temp_path, 'Fulton', 'GA')
                    leads.extend(pdf_leads)
        
        except Exception as e:
            print(f"Error scraping Fulton County: {e}")
        
        return leads
    
    def scrape_harris_county_tx(self) -> List[Dict]:
        """Scrape surplus leads from Harris County, Texas"""
        import requests
        from bs4 import BeautifulSoup
        
        leads = []
        
        try:
            # Harris County Tax Office posts surplus proceeds
            url = "https://www.hctax.net/Property/PropertyTax"
            response = requests.get(url, timeout=30)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for surplus/overage information
            # Note: May require additional navigation or search
            
            # Placeholder for actual implementation
            # Each county has unique website structure
            pass
        
        except Exception as e:
            print(f"Error scraping Harris County: {e}")
        
        return leads
    
    def import_leads_to_airtable(self, leads: List[Dict]) -> Dict:
        """Import mined leads to Airtable, avoiding duplicates"""
        if not leads:
            return {'success': True, 'imported': 0, 'skipped': 0, 'message': 'No leads to import'}
        
        imported = 0
        skipped = 0
        
        try:
            # Get existing leads to check for duplicates
            existing_leads = self.airtable_client.get_all_records('LBPC Leads')
            
            # Create set of existing lead keys (name + property)
            existing_keys = set()
            for lead in existing_leads:
                fields = lead.get('fields', {})
                key = f"{fields.get('Client Name', '')}|{fields.get('Property Address', '')}".lower()
                existing_keys.add(key)
            
            for lead in leads:
                # Check if duplicate
                key = f"{lead.get('Client Name', '')}|{lead.get('Property Address', '')}".lower()
                
                if key in existing_keys:
                    skipped += 1
                    continue
                
                # Import new lead
                try:
                    self.airtable_client.create_record('LBPC Leads', lead)
                    imported += 1
                    existing_keys.add(key)
                except Exception as e:
                    print(f"Error importing lead: {e}")
                    skipped += 1
            
            return {
                'success': True,
                'imported': imported,
                'skipped': skipped,
                'total': len(leads),
                'message': f'Imported {imported} new leads, skipped {skipped} duplicates'
            }
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def mine_county(self, county: str, state: str) -> Dict:
        """Mine leads from specific county"""
        leads = []
        
        # Route to appropriate scraper
        county_key = f"{county.lower()}_{state.lower()}"
        
        scrapers = {
            'wayne_mi': self.scrape_wayne_county_mi,
            'fulton_ga': self.scrape_fulton_county_ga,
            'harris_tx': self.scrape_harris_county_tx,
        }
        
        scraper = scrapers.get(county_key)
        
        if scraper:
            try:
                leads = scraper()
                result = self.import_leads_to_airtable(leads)
                return result
            except Exception as e:
                return {'success': False, 'error': f'Scraping error: {str(e)}'}
        else:
            return {
                'success': False, 
                'error': f'No scraper configured for {county} County, {state}. Please use CSV/PDF upload instead.'
            }


class LBPCDocumentGenerator:
    """Generate documents from templates with AI enhancement"""
    
    def __init__(self):
        self.airtable_client = AirtableClient()
        self.ai_client = AnthropicClient()
    
    def get_template(self, template_type: str) -> Optional[Dict]:
        """Get active template by type"""
        try:
            templates = self.airtable_client.search_records(
                'LBPC Templates',
                f"AND({{Template Type}}='{template_type}', {{Active}}=TRUE())"
            )
            return templates[0] if templates else None
        except:
            return None
    
    def replace_variables(self, template_content: str, lead_data: Dict) -> str:
        """Replace {{variables}} with actual data"""
        # Generate claim number if not exists
        claim_number = lead_data.get('Case Number', f"LBPC-{lead_data.get('State', 'XX')}-{datetime.now().strftime('%Y%m%d')}")
        
        # Prepare replacements
        replacements = {
            '{{date}}': datetime.now().strftime('%B %d, %Y'),
            '{{clientName}}': lead_data.get('Client Name', ''),
            '{{property}}': lead_data.get('Property Address', ''),
            '{{city}}': lead_data.get('City', ''),
            '{{state}}': lead_data.get('State', ''),
            '{{zipCode}}': lead_data.get('Zip Code', ''),
            '{{county}}': lead_data.get('County', ''),
            '{{surplusAmount}}': f"{float(lead_data.get('Surplus Amount', 0)):,.2f}",
            '{{caseNumber}}': lead_data.get('Case Number', claim_number),
            '{{claimNumber}}': claim_number,
            '{{yourFeeAmount}}': f"{float(lead_data.get('Surplus Amount', 0)) * 0.30:,.2f}",
            '{{clientPortion}}': f"{float(lead_data.get('Surplus Amount', 0)) * 0.70:,.2f}",
        }
        
        # Replace all variables
        result = template_content
        for var, value in replacements.items():
            result = result.replace(var, str(value))
        
        return result
    
    def ai_enhance_document(self, document_text: str, lead_data: Dict) -> str:
        """Use AI to personalize and enhance document"""
        surplus_amount = float(lead_data.get('Surplus Amount', 0))
        
        prompt = f"""You are helping generate a professional letter for surplus recovery services.

Lead Information:
- Client: {lead_data.get('Client Name')}
- Property: {lead_data.get('Property Address')}
- Surplus Amount: ${surplus_amount:,.2f}
- County: {lead_data.get('County')}, {lead_data.get('State')}

Base Document:
{document_text}

Task: Enhance this document to be more personalized and compelling while maintaining professionalism. Consider:
1. Adjust tone based on surplus amount (${surplus_amount:,.2f})
2. Add relevant details about the property/location if appropriate
3. Emphasize the substantial amount and no-risk service
4. Keep it concise and professional

Return ONLY the enhanced document text, no explanations."""

        try:
            response = self.ai_client.chat(prompt, max_tokens=2000)
            return response
        except:
            # If AI fails, return original
            return document_text


class LBPCWorkflowEngine:
    """Automated workflow and task generation"""
    
    def __init__(self):
        self.airtable_client = AirtableClient()
    
    def create_task(self, task_data: Dict) -> Dict:
        """Create a new task in Airtable"""
        return self.airtable_client.create_record('LBPC Tasks', task_data)
    
    def generate_new_lead_tasks(self, lead_id: str, lead_data: Dict) -> List[Dict]:
        """Generate task sequence for new lead"""
        tasks = []
        today = datetime.now()
        
        # Task 1: Send Initial Notice (Due: Today)
        tasks.append({
            'Task Title': f"Send Initial Notice - {lead_data.get('Client Name')}",
            'Task Description': f"Send initial notice letter about ${float(lead_data.get('Surplus Amount', 0)):,.2f} surplus funds",
            'Lead': [lead_id],
            'Task Type': 'Send Initial Notice',
            'Priority': 'High' if float(lead_data.get('Surplus Amount', 0)) > 25000 else 'Medium',
            'Status': 'Pending',
            'Due Date': today.strftime('%Y-%m-%d'),
            'Auto-Generated': True,
            'Triggered By Rule': 'New Lead Day 0'
        })
        
        # Task 2: Make Follow-up Call (Due: +3 days)
        tasks.append({
            'Task Title': f"Make Follow-up Call - {lead_data.get('Client Name')}",
            'Task Description': 'Follow up on initial notice with phone call',
            'Lead': [lead_id],
            'Task Type': 'Make Call',
            'Priority': 'Medium',
            'Status': 'Pending',
            'Due Date': (today + timedelta(days=3)).strftime('%Y-%m-%d'),
            'Auto-Generated': True,
            'Triggered By Rule': 'New Lead Day 3'
        })
        
        # Task 3: Send Second Notice (Due: +7 days)
        tasks.append({
            'Task Title': f"Send Second Notice - {lead_data.get('Client Name')}",
            'Task Description': 'Send follow-up notice if no response',
            'Lead': [lead_id],
            'Task Type': 'Send Follow-up Email',
            'Priority': 'Low',
            'Status': 'Pending',
            'Due Date': (today + timedelta(days=7)).strftime('%Y-%m-%d'),
            'Auto-Generated': True,
            'Triggered By Rule': 'New Lead Day 7'
        })
        
        return tasks
    
    def generate_contract_signed_tasks(self, lead_id: str, lead_data: Dict) -> List[Dict]:
        """Generate tasks when contract is signed"""
        tasks = []
        today = datetime.now()
        
        # Task 1: Submit Documents to County (Due: +1 day)
        tasks.append({
            'Task Title': f"Submit Documents - {lead_data.get('Client Name')}",
            'Task Description': 'Submit claim documents to county treasurer',
            'Lead': [lead_id],
            'Task Type': 'Submit Documents to County',
            'Priority': 'Critical',
            'Status': 'Pending',
            'Due Date': (today + timedelta(days=1)).strftime('%Y-%m-%d'),
            'Auto-Generated': True,
            'Triggered By Rule': 'Contract Signed'
        })
        
        return tasks


# =====================================================================
# LBPC API HANDLERS
# =====================================================================

def handle_lbpc_get_leads(filters: Dict = None) -> Dict:
    """Get all LBPC leads with optional filters"""
    try:
        airtable_client = AirtableClient()
        
        if filters:
            # Build formula for filtering
            formula_parts = []
            if filters.get('state'):
                formula_parts.append(f"{{State}}='{filters['state']}'")
            if filters.get('status'):
                formula_parts.append(f"{{Status}}='{filters['status']}'")
            if filters.get('min_amount'):
                formula_parts.append(f"{{Surplus Amount}}>={filters['min_amount']}")
            
            if formula_parts:
                formula = "AND(" + ",".join(formula_parts) + ")"
                leads = airtable_client.search_records('LBPC Leads', formula)
            else:
                leads = airtable_client.get_all_records('LBPC Leads')
        else:
            leads = airtable_client.get_all_records('LBPC Leads')
        
        return {
            'success': True,
            'leads': leads,
            'count': len(leads)
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def handle_lbpc_create_lead(lead_data: Dict) -> Dict:
    """Create new LBPC lead"""
    try:
        miner = LBPCLeadMiner()
        
        # Clean and enrich data
        cleaned_data = miner.clean_lead_data(lead_data)
        
        # Create in Airtable
        airtable_client = AirtableClient()
        result = airtable_client.create_record('LBPC Leads', cleaned_data)
        
        # Generate workflow tasks
        workflow = LBPCWorkflowEngine()
        tasks = workflow.generate_new_lead_tasks(result['id'], cleaned_data)
        
        # Create tasks
        created_tasks = []
        for task in tasks:
            task_result = workflow.create_task(task)
            created_tasks.append(task_result)
        
        return {
            'success': True,
            'lead': result,
            'tasks_created': len(created_tasks),
            'tasks': created_tasks
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def handle_lbpc_update_lead(lead_id: str, updates: Dict) -> Dict:
    """Update existing LBPC lead - with auto-ATLAS integration when contract signed"""
    try:
        airtable_client = AirtableClient()
        
        # Get current lead to check status change
        try:
            current_lead = airtable_client.get_record('LBPC Leads', lead_id)
            old_status = current_lead['fields'].get('Status', '')
        except:
            old_status = ''
        
        result = airtable_client.update_record('LBPC Leads', lead_id, updates)
        
        # If status changed to "Contract Signed", trigger workflow
        new_status = updates.get('Status', old_status)
        if new_status == 'Contract Signed' and old_status != 'Contract Signed':
            workflow = LBPCWorkflowEngine()
            lead_data = result['fields']
            tasks = workflow.generate_contract_signed_tasks(lead_id, lead_data)
            
            for task in tasks:
                workflow.create_task(task)
            
            # 🎯 AUTO-CREATE ATLAS PROJECT FOR CASE MANAGEMENT
            try:
                atlas_result = create_atlas_project_from_lbpc_case(lead_id, airtable_client)
                result['atlas_project_created'] = True
                result['atlas_project_id'] = atlas_result['project_id']
                result['atlas_project_name'] = atlas_result['project_name']
            except Exception as atlas_error:
                print(f"Warning: ATLAS project creation failed for LBPC case: {atlas_error}")
                result['atlas_project_created'] = False
            
            # Also trigger invoice creation
            try:
                invoice_result = handle_lbpc_create_invoice(lead_id)
            except:
                pass
        
        return {
            'success': True,
            'lead': result
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def create_atlas_project_from_lbpc_case(lead_id: str, airtable_client=None) -> dict:
    """
    🎯 AUTO-CREATE ATLAS PROJECT FROM SIGNED LBPC CASE
    """
    if not airtable_client:
        airtable_client = AirtableClient()
    
    # Get lead/case details
    lead = airtable_client.get_record('LBPC Leads', lead_id)
    lead_fields = lead['fields']
    
    # Extract key information
    client_name = lead_fields.get('Owner Name', 'Unknown Client')
    property_address = lead_fields.get('Property Address', '')
    county = lead_fields.get('County', '')
    property_value = lead_fields.get('Property Value', 0)
    service_fee = lead_fields.get('Service Fee', 0)
    case_type = lead_fields.get('Case Type', 'Surplus Recovery')
    
    # Build project scope
    project_scope = f"""
LBPC CASE: {case_type}
CLIENT: {client_name}
PROPERTY: {property_address}
COUNTY: {county}
PROPERTY VALUE: ${property_value:,.2f}

DELIVERABLES:
- Document preparation & filing
- County submission & tracking
- Client communication & updates
- Funds recovery & disbursement

TIMELINE: 60-90 days (county dependent)
    """.strip()
    
    # Create ATLAS project record
    project_fields = {
        'Project Name': f"LBPC: {client_name} - {county} County",
        'Client Name': client_name,
        'Project Type': 'LBPC Case Management',
        'Budget': service_fee,
        'Project Scope': project_scope[:10000],
        'Start Date': datetime.now().isoformat(),
        'Status': 'Active',
        'Priority': 'Medium',
        'Completion Percentage': 0,
        'Created Date': datetime.now().isoformat(),
        'Source System': 'LBPC',
        'Source Case ID': lead_id
    }
    
    # Create the project
    project_record = airtable_client.create_record('ATLAS Projects', project_fields)
    project_id = project_record['id']
    
    # Link case to ATLAS project
    try:
        airtable_client.update_record('LBPC Leads', lead_id, {
            'ATLAS Project': [project_id]
        })
    except Exception as link_error:
        print(f"Warning: Could not link LBPC case to ATLAS project: {link_error}")
    
    return {
        'success': True,
        'project_id': project_id,
        'project_name': project_fields['Project Name'],
        'message': f'✅ ATLAS project created: {project_fields["Project Name"]}'
    }


def handle_lbpc_delete_lead(lead_id: str) -> Dict:
    """Delete LBPC lead"""
    try:
        airtable_client = AirtableClient()
        airtable_client.get_table('LBPC Leads').delete(lead_id)
        
        return {
            'success': True,
            'message': 'Lead deleted'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def handle_lbpc_generate_document(lead_id: str, template_type: str, use_ai: bool = True) -> Dict:
    """Generate document from template"""
    try:
        # Get lead data
        airtable_client = AirtableClient()
        leads = airtable_client.search_records('LBPC Leads', f"RECORD_ID()='{lead_id}'")
        
        if not leads:
            return {'success': False, 'error': 'Lead not found'}
        
        lead_data = leads[0]['fields']
        
        # Get template and generate document
        doc_gen = LBPCDocumentGenerator()
        template = doc_gen.get_template(template_type)
        
        if not template:
            return {'success': False, 'error': f'Template {template_type} not found'}
        
        template_content = template['fields'].get('Template Content', '')
        
        # Replace variables
        document_text = doc_gen.replace_variables(template_content, lead_data)
        
        # AI enhancement (if enabled)
        if use_ai and template['fields'].get('Use AI Enhancement'):
            document_text = doc_gen.ai_enhance_document(document_text, lead_data)
        
        # Save document record
        document_data = {
            'Document Name': f"{lead_data.get('Client Name')} - {template_type}",
            'Lead': [lead_id],
            'Document Type': template_type,
            'Template Used': [template['id']],
            'Generated Content': document_text,
            'Status': 'Generated',
            'Generated Date': datetime.now().isoformat(),
            'AI Enhanced': use_ai
        }
        
        doc_record = airtable_client.create_record('LBPC Documents', document_data)
        
        return {
            'success': True,
            'document': doc_record,
            'document_text': document_text
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def handle_lbpc_get_documents(lead_id: str = None) -> Dict:
    """Get LBPC documents"""
    try:
        airtable_client = AirtableClient()
        
        if lead_id:
            documents = airtable_client.search_records('LBPC Documents', f"{{Lead}}='{lead_id}'")
        else:
            documents = airtable_client.get_all_records('LBPC Documents')
        
        return {
            'success': True,
            'documents': documents,
            'count': len(documents)
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def handle_lbpc_get_tasks(filters: Dict = None) -> Dict:
    """Get LBPC tasks"""
    try:
        airtable_client = AirtableClient()
        
        if filters:
            formula_parts = []
            if filters.get('status'):
                formula_parts.append(f"{{Status}}='{filters['status']}'")
            if filters.get('lead_id'):
                formula_parts.append(f"{{Lead}}='{filters['lead_id']}'")
            
            if formula_parts:
                formula = "AND(" + ",".join(formula_parts) + ")"
                tasks = airtable_client.search_records('LBPC Tasks', formula)
            else:
                tasks = airtable_client.get_all_records('LBPC Tasks')
        else:
            tasks = airtable_client.get_all_records('LBPC Tasks')
        
        return {
            'success': True,
            'tasks': tasks,
            'count': len(tasks)
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def handle_lbpc_update_task(task_id: str, updates: Dict) -> Dict:
    """Update LBPC task"""
    try:
        airtable_client = AirtableClient()
        result = airtable_client.update_record('LBPC Tasks', task_id, updates)
        
        return {
            'success': True,
            'task': result
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def handle_lbpc_ai_qualify_lead(lead_id: str) -> Dict:
    """AI qualification of a lead"""
    try:
        # Get lead data
        airtable_client = AirtableClient()
        leads = airtable_client.search_records('LBPC Leads', f"RECORD_ID()='{lead_id}'")
        
        if not leads:
            return {'success': False, 'error': 'Lead not found'}
        
        lead_data = leads[0]['fields']
        
        # Build AI prompt
        prompt = f"""Analyze this surplus recovery lead and provide qualification analysis:

Lead Information:
- Client Name: {lead_data.get('Client Name')}
- Property: {lead_data.get('Property Address')}
- County: {lead_data.get('County')}, {lead_data.get('State')}
- Surplus Amount: ${lead_data.get('Surplus Amount', 0):,.2f}
- Has Email: {'Yes' if lead_data.get('Contact Email') else 'No'}
- Has Phone: {'Yes' if lead_data.get('Contact Phone') else 'No'}
- Case Number: {lead_data.get('Case Number', 'Unknown')}

Provide analysis in this JSON format:
{{
    "priority_score": 0-100,
    "win_probability": 0-100,
    "recommendation": "GO - High Priority" or "GO - Standard" or "REVIEW - Needs Analysis" or "NO-GO - Skip",
    "strengths": ["strength1", "strength2", ...],
    "concerns": ["concern1", "concern2", ...],
    "recommended_action": "Specific next step"
}}"""

        ai_client = AnthropicClient()
        response = ai_client.chat(prompt, max_tokens=1000)
        
        # Parse JSON response
        try:
            import json
            analysis = json.loads(response)
        except:
            # If JSON parsing fails, return raw response
            analysis = {'raw_response': response}
        
        # Update lead with AI analysis
        updates = {
            'AI Qualification Result': response,
            'AI Recommendation': analysis.get('recommendation', 'REVIEW - Needs Analysis'),
            'AI Strengths': '\n'.join(analysis.get('strengths', [])),
            'AI Concerns': '\n'.join(analysis.get('concerns', [])),
            'Qualification Date': datetime.now().isoformat()
        }
        
        if 'priority_score' in analysis:
            updates['Priority Score'] = analysis['priority_score']
        if 'win_probability' in analysis:
            updates['Win Probability'] = analysis['win_probability']
        
        airtable_client.update_record('LBPC Leads', lead_id, updates)
        
        return {
            'success': True,
            'analysis': analysis
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def handle_lbpc_create_invoice(lead_id: str) -> Dict:
    """Create invoice for LBPC lead (when contract signed)"""
    try:
        # Get lead data
        airtable_client = AirtableClient()
        leads = airtable_client.search_records('LBPC Leads', f"RECORD_ID()='{lead_id}'")
        
        if not leads:
            return {'success': False, 'error': 'Lead not found'}
        
        lead_data = leads[0]['fields']
        surplus_amount = float(lead_data.get('Surplus Amount', 0))
        fee_amount = surplus_amount * 0.30
        
        # Create invoice
        invoice_data = {
            'Client Name': lead_data.get('Client Name'),
            'Client Type': 'Enterprise - Private',
            'Source System': 'LBPC',
            'Invoice Date': datetime.now().strftime('%Y-%m-%d'),
            'Due Date': datetime.now().strftime('%Y-%m-%d'),  # Due on receipt
            'Subtotal': fee_amount,
            'Total Amount': fee_amount,
            'Invoice Status': 'Draft',
            'Payment Terms': 'Due on Receipt',
            'Invoice Notes': f"Surplus Recovery Services - 30% contingency fee on ${surplus_amount:,.2f} surplus recovery",
            'Bill To Address': lead_data.get('Property Address', '')
        }
        
        invoice = airtable_client.create_record('Invoices', invoice_data)
        
        # Link invoice to lead
        airtable_client.update_record('LBPC Leads', lead_id, {
            'Invoice': [invoice['id']]
        })

        # VERTEX BRIDGE: Also create in VERTEX INVOICES
        try:
            from api_server import VI
            inv_num = invoice_data.get('Invoice Number') or invoice_data.get('INVOICE NUMBER', '')
            airtable_client.create_record('VERTEX INVOICES', {
                VI['invoice_number']:  inv_num,
                VI['invoice_date']:    invoice_data.get('Invoice Date', ''),
                VI['due_date']:        invoice_data.get('Due Date', ''),
                VI['client_name']:     invoice_data.get('Client Name', ''),
                VI['source_system']:   'LBPC',
                VI['source_record']:   lead_id,
                VI['invoice_type']:    'Standard',
                VI['total_amount']:    fee_amount,
                VI['payment_status']:  'Unpaid',
                VI['payment_terms']:   'Due on Receipt',
                VI['notes']:           invoice_data.get('Invoice Notes', ''),
            })
        except Exception as ve:
            print(f"LBPC → VERTEX bridge: {ve}")
        
        return {
            'success': True,
            'invoice': invoice
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def handle_lbpc_import_csv(csv_data: List[Dict]) -> Dict:
    """Import leads from CSV data"""
    try:
        miner = LBPCLeadMiner()
        airtable_client = AirtableClient()
        workflow = LBPCWorkflowEngine()
        
        imported = 0
        skipped = 0
        
        for row in csv_data:
            # Clean data
            cleaned = miner.clean_lead_data(row)
            
            # Check for duplicates (by case number)
            if cleaned.get('Case Number'):
                existing = airtable_client.search_records(
                    'LBPC Leads',
                    f"{{Case Number}}='{cleaned['Case Number']}'"
                )
                if existing:
                    skipped += 1
                    continue
            
            # Create lead
            result = airtable_client.create_record('LBPC Leads', cleaned)
            
            # Generate tasks
            tasks = workflow.generate_new_lead_tasks(result['id'], cleaned)
            for task in tasks:
                workflow.create_task(task)
            
            imported += 1
        
        return {
            'success': True,
            'imported': imported,
            'skipped': skipped,
            'total': len(csv_data)
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def handle_lbpc_get_analytics() -> Dict:
    """Get LBPC analytics and dashboard stats"""
    try:
        airtable_client = AirtableClient()
        leads = airtable_client.get_all_records('LBPC Leads')
        tasks = airtable_client.get_all_records('LBPC Tasks')
        
        # Calculate statistics
        total_leads = len(leads)
        total_surplus = sum(float(lead['fields'].get('Surplus Amount', 0)) for lead in leads)
        total_fees = total_surplus * 0.30
        
        # Tasks due today
        today = datetime.now().strftime('%Y-%m-%d')
        tasks_today = len([t for t in tasks if t['fields'].get('Due Date') == today and t['fields'].get('Status') in ['Pending', 'In Progress']])
        
        # Contracts signed
        contracts_signed = len([l for l in leads if l['fields'].get('Status') == 'Contract Signed'])
        
        # Leads by state
        leads_by_state = {}
        for lead in leads:
            state = lead['fields'].get('State', 'Unknown')
            leads_by_state[state] = leads_by_state.get(state, 0) + 1
        
        # Leads by status
        leads_by_status = {}
        for lead in leads:
            status = lead['fields'].get('Status', 'Unknown')
            leads_by_status[status] = leads_by_status.get(status, 0) + 1
        
        return {
            'success': True,
            'analytics': {
                'total_leads': total_leads,
                'total_surplus': total_surplus,
                'total_fees': total_fees,
                'tasks_today': tasks_today,
                'contracts_signed': contracts_signed,
                'leads_by_state': leads_by_state,
                'leads_by_status': leads_by_status,
                'average_surplus': total_surplus / total_leads if total_leads > 0 else 0
            }
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def handle_lbpc_mine_county(county: str, state: str) -> Dict:
    """Mine leads from specific county website"""
    try:
        miner = LBPCLeadMiner()
        result = miner.mine_county(county, state)
        return result
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def handle_lbpc_upload_pdf(pdf_path: str, county: str, state: str) -> Dict:
    """Parse PDF and import leads"""
    try:
        miner = LBPCLeadMiner()
        leads = miner.parse_pdf_table(pdf_path, county, state)
        result = miner.import_leads_to_airtable(leads)
        return result
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def handle_lbpc_upload_csv(csv_content: str, county: str, state: str) -> Dict:
    """Parse CSV and import leads"""
    try:
        miner = LBPCLeadMiner()
        leads = miner.parse_csv_data(csv_content, county, state)
        result = miner.import_leads_to_airtable(leads)
        return result
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


# =====================================================================
# INVOICE API HANDLERS
# =====================================================================

def handle_generate_invoice_from_opportunity(opportunity_id: str) -> Dict:
    """Generate invoice from GPSS opportunity"""
    agent = InvoiceGeneratorAgent()
    return agent.generate_from_opportunity(opportunity_id)


def handle_generate_invoice_from_project(project_id: str) -> Dict:
    """Generate invoice from ATLAS project"""
    agent = InvoiceGeneratorAgent()
    return agent.generate_from_project(project_id)


def handle_generate_invoice_from_prospect(prospect_id: str) -> Dict:
    """Generate invoice from DDCSS prospect"""
    agent = InvoiceGeneratorAgent()
    return agent.generate_from_prospect(prospect_id)


def handle_get_invoices(filters: Dict = None) -> Dict:
    """Get all invoices with optional filters"""
    agent = InvoiceGeneratorAgent()
    return agent.get_all_invoices(filters)


def handle_get_invoice(invoice_id: str) -> Dict:
    """Get single invoice details"""
    agent = InvoiceGeneratorAgent()
    return agent.get_invoice(invoice_id)


def handle_update_invoice(invoice_id: str, updates: Dict) -> Dict:
    """Update existing invoice"""
    agent = InvoiceGeneratorAgent()
    return agent.update_invoice(invoice_id, updates)


def handle_delete_invoice(invoice_id: str) -> Dict:
    """Delete an invoice"""
    agent = InvoiceGeneratorAgent()
    return agent.delete_invoice(invoice_id)


# =====================================================================
# AI RECOMMENDATION SYSTEM HANDLERS
# =====================================================================

def handle_analyze_capability_gap(opportunity_id: str) -> Dict:
    """
    Analyze opportunity and recommend self-perform vs partner approach
    AI suggests best path, user approves/denies
    """
    agent = AIRecommendationAgent()
    return agent.analyze_capability_gap(opportunity_id)


def handle_recommend_subcontractors(
    opportunity_id: str,
    needed_skills: List[str],
    contract_value: float = None,
    minimal_research: bool = True,
) -> Dict:
    """
    AI recommends top 5 subcontractors based on needed skills and optional live research.
    """
    agent = AIRecommendationAgent()
    return agent.recommend_subcontractors(
        opportunity_id, needed_skills, contract_value, minimal_research=minimal_research
    )


def handle_recommend_suppliers(opportunity_id: str, product_description: str) -> Dict:
    """
    AI recommends top 10 suppliers for product-based opportunities
    Returns ranked list with reasoning for each
    """
    agent = AIRecommendationAgent()
    return agent.recommend_suppliers(opportunity_id, product_description)


def handle_solicitation_market_research(opportunity_id: str, persist_notes: bool = False) -> Dict:
    """
    USASpending pass: likely incumbents + award-value benchmarks for proposal pricing.
    GPSS should call this when qualifying or pricing a solicitation (federal-focused).
    """
    try:
        from solicitation_market_research import SolicitationMarketResearch

        airtable = AirtableClient()
        rec = airtable.get_record("GPSS OPPORTUNITIES", opportunity_id)
        if not rec:
            return {"success": False, "error": "Opportunity not found in GPSS OPPORTUNITIES"}
        fields = rec.get("fields") or {}
        smr = SolicitationMarketResearch()
        payload = smr.research_from_airtable_fields(fields)
        payload["success"] = True
        payload["opportunity_id"] = opportunity_id

        if persist_notes:
            block = smr.format_notes_block(payload)
            existing = (fields.get("Notes") or "").strip()
            merged = f"{existing}\n\n{block}".strip() if existing else block
            airtable.update_record(
                "GPSS OPPORTUNITIES",
                opportunity_id,
                {"Notes": merged[:100000]},
            )
            payload["notes_persisted"] = True
        return payload
    except Exception as e:
        return {"success": False, "error": str(e)}


def handle_approve_recommendation(recommendation_id: str, user_decision: str, user_notes: str = "", selected_id: str = None) -> Dict:
    """
    User approves, denies, or modifies AI recommendation
    System learns from the decision
    
    Args:
        recommendation_id: ID of AI recommendation
        user_decision: "approved", "denied", or "modified"
        user_notes: User's reasoning
        selected_id: If user picked different option
    """
    agent = AIRecommendationAgent()
    return agent.approve_recommendation(recommendation_id, user_decision, user_notes, selected_id)


def handle_get_pending_recommendations(opportunity_id: str = None) -> Dict:
    """Get all pending AI recommendations awaiting user decision"""
    agent = AIRecommendationAgent()
    return agent.get_pending_recommendations(opportunity_id)


def handle_calculate_compliance(contract_value: float, your_work_value: float, sub_work_value: float) -> Dict:
    """
    Calculate workshare percentages and check 50% rule compliance
    Used for subcontracting compliance verification
    """
    agent = AIRecommendationAgent()
    return agent.calculate_compliance(contract_value, your_work_value, sub_work_value)


# =====================================================================
# GPSS SUPPLIER MINING & AUTOMATED QUOTING SYSTEM
# =====================================================================

class GPSSSupplierMiner:
    """
    Mine and qualify wholesale suppliers for government contract fulfillment
    
    Discovers suppliers from multiple sources:
    - GSA Advantage (government supplier database)
    - Google Search (automated queries)
    - ThomasNet (industrial directory)
    - Manual entry
    
    Qualifies suppliers based on:
    - Product match
    - Net 30 terms availability
    - Government supplier status
    - Pricing competitiveness
    """
    
    def __init__(self):
        self.airtable = AirtableClient()
        self.ai = AnthropicClient()
    
    def search_existing_suppliers(self, category: str = None, keywords: List[str] = None, 
                                   min_rating: float = 0) -> List[Dict]:
        """
        Search existing supplier database
        
        Args:
            category: Product category to filter by
            keywords: Keywords to match in product keywords field
            min_rating: Minimum overall rating
            
        Returns:
            List of matching supplier records
        """
        try:
            # Get all suppliers from Airtable
            suppliers = self.airtable.get_all_records('GPSS SUPPLIERS')
            
            # Apply filters
            filtered = []
            for supplier in suppliers:
                fields = supplier.get('fields', {})
                
                # Filter by category if specified
                if category:
                    categories = fields.get('PRODUCT CATEGORIES', [])
                    if category not in categories:
                        continue
                
                # Filter by keywords if specified
                if keywords:
                    supplier_keywords = fields.get('PRODUCT KEYWORDS', '').lower()
                    if not all(kw.lower() in supplier_keywords for kw in keywords):
                        continue
                
                # Filter by rating
                rating = fields.get('OVERALL RATING', 0)
                if rating < min_rating:
                    continue
                
                # Filter out explicitly inactive suppliers only
                status = fields.get('BUSINESS STATUS', '')
                if status in ['Inactive', 'Blocked', 'Rejected', 'INACTIVE', 'BLOCKED', 'BLACKLISTED']:
                    continue
                
                # Skip suppliers with no company name
                company_name = fields.get('COMPANY NAME', '').strip()
                if not company_name:
                    continue
                
                # Normalize status to title case for frontend display
                status_display = status.title() if status else ''
                
                filtered.append({
                    'id': supplier.get('id'),
                    'company_name': company_name,
                    'website': fields.get('WEBSITE', ''),
                    'product_keywords': fields.get('PRODUCT KEYWORDS', ''),
                    'net_30_available': fields.get('NET 30', False),
                    'net_45_available': fields.get('NET 45', False),
                    'overall_rating': rating,
                    'typical_margin': fields.get('TYPICAL MARGIN', 0),
                    'contact_email': fields.get('PRIMARY CONTACT EMAIL', ''),
                    'phone': fields.get('PRIMARY CONTACT PHONE', ''),
                    'business_status': status_display,
                    'discovery_method': (fields.get('DISCOVERY METHOD', '') or '').title(),
                    'discovery_date': fields.get('DISCOVERY DATE', ''),
                    'discovered_by': (fields.get('DISCOVERED BY', '') or '').title()
                })
            
            # Sort by rating desc
            filtered.sort(key=lambda x: x.get('overall_rating', 0), reverse=True)
            
            return filtered
            
        except Exception as e:
            print(f"Error searching suppliers: {e}")
            return []
    
    # ============================================
    # THOMASNET MINING
    # ============================================
    
    def search_thomasnet(self, product: str, max_results: int = 15) -> List[Dict]:
        """
        Search ThomasNet for manufacturers/wholesalers.
        
        ThomasNet uses Cloudflare bot protection that blocks all headless browsers,
        so we go directly to the Google CSE fallback (site:thomasnet.com searches).
        This indexes ThomasNet's public supplier profiles through Google.
        
        Credentials (THOMASNET_EMAIL/PASSWORD in .env) are kept for future use
        if ThomasNet releases an API or relaxes bot detection.
        
        Args:
            product: Product to search for
            max_results: Maximum suppliers to return
            
        Returns:
            List of supplier dictionaries ready for Airtable
        """
        # ThomasNet has aggressive Cloudflare bot detection that blocks all
        # headless browsers. Go directly to Google CSE fallback.
        print(f"🏭 Searching ThomasNet (via Google index) for: {product}")
        return self._search_thomasnet_fallback(product, max_results)
        
        # PRESERVED: Original Playwright approach (blocked by Cloudflare as of Feb 2026)
        try:
            from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
            
            print(f"🔍 Searching ThomasNet for: {product}")
            results = []
            
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(
                    user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
                )
                page = context.new_page()
                
                # Login to ThomasNet
                email = os.environ.get('THOMASNET_EMAIL')
                password = os.environ.get('THOMASNET_PASSWORD')
                
                if email and password:
                    try:
                        print("  🔐 Logging into ThomasNet...")
                        page.goto('https://www.thomasnet.com/account/login', timeout=30000)
                        page.fill('input[type="email"], input[name="email"], #email', email, timeout=10000)
                        page.fill('input[type="password"], input[name="password"], #password', password, timeout=10000)
                        page.click('button[type="submit"], input[type="submit"]', timeout=10000)
                        page.wait_for_load_state('networkidle', timeout=15000)
                        print("  ✅ Logged in successfully")
                    except Exception as e:
                        print(f"  ⚠️  Login failed: {e}. Continuing with guest access...")
                else:
                    print("  ℹ️  No ThomasNet credentials. Using guest access...")
                
                # Perform search
                search_url = f'https://www.thomasnet.com/search?term={product.replace(" ", "+")}'
                page.goto(search_url, timeout=30000)
                
                try:
                    # Wait for results - try multiple possible selectors
                    page.wait_for_selector('.search-result, .company-listing, .supplier-card, .product-listing', timeout=15000)
                except PlaywrightTimeout:
                    print("  ⚠️  No results found or page timeout")
                    browser.close()
                    return []
                
                # Scroll to load more results
                for _ in range(3):
                    page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                    page.wait_for_timeout(1000)
                
                # Extract supplier data
                suppliers = page.query_selector_all('.search-result, .company-listing, .product-supplier, .supplier-card')
                
                print(f"  📦 Found {len(suppliers)} potential suppliers")
                
                for i, supplier_elem in enumerate(suppliers[:max_results]):
                    try:
                        # Extract company info - try multiple selector patterns
                        company_name = self._extract_text(supplier_elem, '.company-name, h3, .title, .supplier-name, h2')
                        location = self._extract_text(supplier_elem, '.location, .address, .city, .region')
                        phone = self._extract_text(supplier_elem, '.phone, .contact-phone, .tel, .telephone')
                        website = self._extract_attribute(supplier_elem, 'a[href*="http"]', 'href')
                        description = self._extract_text(supplier_elem, '.description, .summary, p, .about')
                        products = self._extract_text(supplier_elem, '.products, .categories, .capabilities')
                        
                        if company_name and company_name.strip():
                            results.append({
                                'COMPANY NAME': company_name.strip(),
                                'LOCATION': location.strip() if location else '',
                                'PRIMARY CONTACT PHONE': phone.strip() if phone else '',
                                'WEBSITE': website if website else '',
                                'DESCRIPTION': description.strip() if description else '',
                                'PRODUCT KEYWORDS': (products.strip() if products else product),
                                'DISCOVERY METHOD': 'ThomasNet',
                                'DISCOVERY DATE': datetime.now().strftime('%Y-%m-%d'),
                                'DISCOVERED BY': 'NEXUS Auto-Mining',
                                'BUSINESS STATUS': 'Prospective',
                                'RELATIONSHIP STAGE': 'Discovered',
                                'SOURCE NOTES': f'Found via ThomasNet search for "{product}"'
                            })
                            print(f"    ✓ {company_name.strip()}")
                    
                    except Exception as e:
                        print(f"    ⚠️  Error extracting result {i+1}: {e}")
                        continue
                
                browser.close()
            
            print(f"  ✅ Found {len(results)} qualified suppliers on ThomasNet\n")
            return results
        
        except ImportError:
            print("  ⚠️  Playwright not available. Falling back to requests-based ThomasNet search...\n")
            return self._search_thomasnet_fallback(product, max_results)
        except Exception as e:
            print(f"  ⚠️  Playwright ThomasNet search failed: {e}. Trying fallback...\n")
            return self._search_thomasnet_fallback(product, max_results)

    def _search_thomasnet_fallback(self, product: str, max_results: int = 15) -> List[Dict]:
        """
        ThomasNet fallback: Search Google for ThomasNet supplier listings.
        ThomasNet blocks direct scraping (bot detection), so we use Google
        to index their public supplier profiles via site:thomasnet.com.
        Requires: GOOGLE_CSE_API_KEY and GOOGLE_CSE_ID in .env
        """
        try:
            api_key = os.environ.get('GOOGLE_CSE_API_KEY')
            cse_id = os.environ.get('GOOGLE_CSE_ID')
            
            if not api_key or not cse_id:
                print("  ℹ️  Google CSE not configured. Skipping ThomasNet via Google.\n")
                return []
            
            print(f"  🔍 Searching ThomasNet via Google for: {product}")
            results = []
            
            # Search Google for ThomasNet supplier/company pages
            # ThomasNet URLs: /suppliers/usa/..., /company/..., /profile/...
            queries = [
                f'site:thomasnet.com {product} supplier',
                f'site:thomasnet.com {product} manufacturers',
                f'site:thomasnet.com/company {product}',
            ]
            
            seen_urls = set()
            
            for query in queries:
                try:
                    url = 'https://www.googleapis.com/customsearch/v1'
                    params = {
                        'key': api_key,
                        'cx': cse_id,
                        'q': query,
                        'num': 10
                    }
                    
                    response = requests.get(url, params=params, timeout=10)
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        for item in data.get('items', []):
                            link = item.get('link', '')
                            title = item.get('title', '')
                            snippet = item.get('snippet', '')
                            
                            # Only include actual ThomasNet supplier/company pages
                            if 'thomasnet.com' not in link:
                                continue
                            # Skip blog posts, articles, insights — only want supplier pages
                            if any(skip in link for skip in ['blog.thomasnet', '/insights/', '/articles/', '.pdf']):
                                continue
                            if link in seen_urls:
                                continue
                            seen_urls.add(link)
                            
                            # Extract company name from title
                            # ThomasNet formats: "Company: City, ST 12345 - Thomasnet"
                            # or "Category Manufacturers and Suppliers in the USA"
                            company_name = title.split('|')[0].strip() if '|' in title else title.split('-')[0].strip()
                            
                            # Clean up common suffixes / category page titles
                            for suffix in ['ThomasNet', 'Thomasnet', 'Supplier Discovery', 'Products',
                                         'Manufacturers and Suppliers in the USA and Canada',
                                         'Manufacturers and Suppliers in the USA',
                                         'Manufacturers and Suppliers in the',
                                         'Manufacturers and Suppliers',
                                         'Manufacturers & Suppliers',
                                         'in the USA and Canada',
                                         'in the USA']:
                                company_name = company_name.replace(suffix, '').strip(' -|:.')
                            
                            # Skip generic category pages (not actual companies)
                            if '/suppliers/usa/' in link and '/company/' not in link and '/profile/' not in link:
                                # This is a category listing page, not a specific company
                                # Still useful as it lists the category, but mark accordingly
                                company_name = f"[Category] {company_name}"
                            
                            # Try to extract location from title (format: "Company: City, ST ZIP")
                            location = ''
                            if ':' in title:
                                loc_part = title.split(':')[1].split('-')[0].strip()
                                if loc_part and any(c.isdigit() for c in loc_part):
                                    location = loc_part.strip()
                            
                            if company_name and len(company_name) > 2:
                                results.append({
                                    'COMPANY NAME': company_name,
                                    'LOCATION': location,
                                    'PRIMARY CONTACT PHONE': '',
                                    'WEBSITE': link,
                                    'DESCRIPTION': snippet[:500],
                                    'PRODUCT KEYWORDS': product,
                                    'DISCOVERY METHOD': 'ThomasNet (via Google)',
                                    'DISCOVERY DATE': datetime.now().strftime('%Y-%m-%d'),
                                    'DISCOVERED BY': 'NEXUS Auto-Mining',
                                    'BUSINESS STATUS': 'Prospective',
                                    'RELATIONSHIP STAGE': 'Discovered',
                                    'SOURCE NOTES': f'ThomasNet supplier found via Google search for "{product}"'
                                })
                                print(f"    ✓ {company_name}")
                    
                    elif response.status_code == 429:
                        print(f"  ⚠️  Google API rate limit reached")
                        break
                    
                    import time
                    time.sleep(1)  # Rate limit
                
                except Exception as e:
                    print(f"  ⚠️  Error in Google ThomasNet search: {e}")
                    continue
            
            print(f"  ✅ Found {len(results)} ThomasNet suppliers via Google\n")
            return results[:max_results]
        
        except Exception as e:
            print(f"  ❌ ThomasNet Google fallback error: {e}\n")
            return []
    
    def _extract_text(self, element, selector: str) -> str:
        """Helper: Extract text from element using multiple possible selectors"""
        try:
            for sel in selector.split(', '):
                elem = element.query_selector(sel.strip())
                if elem:
                    text = elem.inner_text()
                    if text and text.strip():
                        return text
            return ''
        except:
            return ''
    
    def _extract_attribute(self, element, selector: str, attribute: str) -> str:
        """Helper: Extract attribute from element"""
        try:
            elem = element.query_selector(selector)
            return elem.get_attribute(attribute) if elem else ''
        except:
            return ''
    
    # ============================================
    # GOOGLE CUSTOM SEARCH
    # ============================================
    
    def search_google_suppliers(self, product: str, max_results: int = 10) -> List[Dict]:
        """
        Search Google for suppliers using Custom Search API
        Requires: GOOGLE_CSE_API_KEY and GOOGLE_CSE_ID in .env
        
        Args:
            product: Product to search for
            max_results: Maximum suppliers to return
            
        Returns:
            List of supplier dictionaries
        """
        try:
            api_key = os.environ.get('GOOGLE_CSE_API_KEY')
            cse_id = os.environ.get('GOOGLE_CSE_ID')
            
            if not api_key or not cse_id:
                print("  ℹ️  Google CSE credentials not set. Skipping Google search.\n")
                return []
            
            print(f"🔍 Searching Google for: {product}")
            results = []
            
            # Build search queries
            queries = [
                f'{product} wholesale distributor',
                f'{product} manufacturer supplier',
                f'{product} government supplier Net 30'
            ]
            
            seen_domains = set()
            
            for query in queries:
                try:
                    url = 'https://www.googleapis.com/customsearch/v1'
                    params = {
                        'key': api_key,
                        'cx': cse_id,
                        'q': query,
                        'num': 10
                    }
                    
                    response = requests.get(url, params=params, timeout=10)
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        for item in data.get('items', []):
                            title = item.get('title', '')
                            snippet = item.get('snippet', '')
                            link = item.get('link', '')
                            
                            # Extract domain to avoid duplicates
                            from urllib.parse import urlparse
                            domain = urlparse(link).netloc
                            
                            if domain in seen_domains:
                                continue
                            
                            # Use AI to extract company info from snippet
                            company_info = self._ai_extract_company_info(title, snippet, link)
                            
                            if company_info and company_info.get('company_name'):
                                seen_domains.add(domain)
                                results.append({
                                    'COMPANY NAME': company_info['company_name'],
                                    'WEBSITE': link,
                                    'DESCRIPTION': snippet[:500],
                                    'PRODUCT KEYWORDS': product,
                                    'DISCOVERY METHOD': 'Google Search',
                                    'DISCOVERY DATE': datetime.now().strftime('%Y-%m-%d'),
                                    'DISCOVERED BY': 'NEXUS Auto-Mining',
                                    'BUSINESS STATUS': 'Prospective',
                                    'RELATIONSHIP STAGE': 'Discovered',
                                    'SOURCE NOTES': f'Found via Google search for "{query}"'
                                })
                                print(f"  ✓ {company_info['company_name']}")
                    
                    elif response.status_code == 429:
                        print(f"  ⚠️  Google API rate limit reached")
                        break
                    
                    # Respect rate limits
                    time.sleep(1)
                
                except Exception as e:
                    print(f"  ⚠️  Error searching '{query}': {e}")
                    continue
            
            print(f"  ✅ Found {len(results)} unique suppliers via Google\n")
            return results[:max_results]
        
        except Exception as e:
            print(f"  ❌ Google search error: {e}\n")
            return []
    
    def _ai_extract_company_info(self, title: str, snippet: str, url: str) -> Dict:
        """Use AI to extract company info from search result"""
        prompt = f"""Extract company information from this Google search result.

Title: {title}
Snippet: {snippet}
URL: {url}

ONLY extract if this is a SUPPLIER/MANUFACTURER/DISTRIBUTOR (not a marketplace like Amazon/eBay, not a review site, not a news article).

Return JSON with:
- company_name: The actual company name (not "Amazon" or "Walmart" unless they're the actual supplier)
- is_supplier: true if this is a legitimate supplier, false otherwise

Return ONLY valid JSON, no other text."""
        
        try:
            response = self.ai.complete(prompt, max_tokens=100)
            clean_json = response.replace('```json', '').replace('```', '').strip()
            data = json.loads(clean_json)
            
            if data.get('is_supplier'):
                return data
            return {}
        except:
            return {}
    
    # ============================================
    # GSA ADVANTAGE API
    # ============================================
    
    def search_gsa_suppliers(self, product: str, max_results: int = 10) -> List[Dict]:
        """
        Search GSA Advantage for government suppliers
        Requires: SAM_GOV_API_KEY in .env
        
        Args:
            product: Product to search for
            max_results: Maximum suppliers to return
            
        Returns:
            List of GSA-verified suppliers
        """
        try:
            api_key = os.environ.get('SAM_GOV_API_KEY')
            
            if not api_key:
                print("  ℹ️  SAM.gov API key not set. Skipping GSA search.\n")
                return []
            
            print(f"🔍 Searching GSA Advantage for: {product}")
            results = []
            
            # GSA Advantage search endpoint
            url = 'https://api.gsa.gov/acquisitions/advantage/v1/product'
            headers = {'X-Api-Key': api_key}
            params = {
                'keyword': product,
                'limit': max_results * 2  # Get more to account for duplicates
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                vendors_seen = set()
                
                for item in data.get('data', []):
                    vendor = item.get('vendor', {})
                    vendor_name = vendor.get('name', '')
                    
                    if vendor_name and vendor_name not in vendors_seen:
                        vendors_seen.add(vendor_name)
                        
                        results.append({
                            'COMPANY NAME': vendor_name,
                            'GSA CONTRACT HOLDER': True,
                            'GSA SCHEDULE NUMBER': item.get('schedule', ''),
                            'PRODUCT KEYWORDS': item.get('description', product)[:500],
                            'GOVERNMENT SUPPLIER': True,
                            'DISCOVERY METHOD': 'GSA Advantage',
                            'DISCOVERY DATE': datetime.now().strftime('%Y-%m-%d'),
                            'DISCOVERED BY': 'NEXUS Auto-Mining',
                            'BUSINESS STATUS': 'Active',
                            'RELATIONSHIP STAGE': 'Discovered',
                            'SOURCE NOTES': f'GSA Advantage verified supplier for "{product}"'
                        })
                        print(f"  ✓ {vendor_name} (GSA Schedule)")
                        
                        if len(results) >= max_results:
                            break
            
            elif response.status_code == 401:
                print(f"  ⚠️  Invalid SAM.gov API key")
            elif response.status_code == 429:
                print(f"  ⚠️  GSA API rate limit reached")
            else:
                print(f"  ⚠️  GSA API returned status {response.status_code}")
            
            print(f"  ✅ Found {len(results)} GSA-verified suppliers\n")
            return results
        
        except Exception as e:
            print(f"  ❌ GSA search error: {e}\n")
            return []
    
    # ============================================
    # AI QUALIFICATION
    # ============================================
    
    def _ai_qualify_supplier(self, supplier: Dict) -> int:
        """
        AI scores supplier 0-100 based on available info
        
        Args:
            supplier: Supplier dictionary with available fields
            
        Returns:
            Score from 0-100
        """
        prompt = f"""Score this supplier for government contract fulfillment (0-100).

Company: {supplier.get('COMPANY NAME', 'Unknown')}
Location: {supplier.get('LOCATION', 'Unknown')}
Website: {supplier.get('WEBSITE', 'Unknown')}
Phone: {supplier.get('PRIMARY CONTACT PHONE', 'Unknown')}
Products: {supplier.get('PRODUCT KEYWORDS', 'Unknown')}
Description: {supplier.get('DESCRIPTION', 'Unknown')[:200]}
GSA Contract: {supplier.get('GSA CONTRACT HOLDER', False)}
Government Supplier: {supplier.get('GOVERNMENT SUPPLIER', False)}

Score based on:
1. Has contact info (phone/email/website) = +20 points
2. Looks legitimate (not spam/marketplace) = +20 points
3. Relevant to government contracting = +20 points
4. Has GSA contract = +20 points bonus
5. Professional presence = +20 points

Return ONLY a number 0-100, nothing else."""
        
        try:
            response = self.ai.complete(prompt, max_tokens=10)
            score = int(response.strip())
            return min(100, max(0, score))
        except:
            return 50  # Default moderate score if AI fails
    
    # ============================================
    # MASTER MINING FUNCTION
    # ============================================
    
    def mine_all_sources(self, product: str, category: str = None, 
                         sources: List[str] = None, auto_import_threshold: int = 80) -> Dict:
        """
        Search all supplier sources and combine results
        
        Args:
            product: Product to search for
            category: Product category (optional)
            sources: List of sources to search ['database', 'thomasnet', 'google', 'gsa']
                    If None, searches all available
            auto_import_threshold: Auto-import suppliers scoring above this (0-100)
            
        Returns:
            Dictionary with results and stats
        """
        if sources is None:
            sources = ['database', 'thomasnet', 'google', 'gsa']
        
        all_results = []
        stats = {
            'database': 0,
            'thomasnet': 0,
            'google': 0,
            'gsa': 0,
            'total_found': 0,
            'qualified': 0,
            'auto_imported': 0,
            'review_queue': 0
        }
        
        print(f"\n{'='*60}")
        print(f"🚀 MINING SUPPLIERS FOR: {product}")
        print(f"{'='*60}\n")
        
        # Source 1: Existing database
        if 'database' in sources:
            print("📊 Searching existing database...")
            db_results = self.search_existing_suppliers(
                category=category,
                keywords=product.split(),
                min_rating=0
            )
            
            # Convert to full format for consistency
            for supplier in db_results:
                supplier['already_in_db'] = True
                supplier['ai_score'] = 100  # Already vetted
            
            all_results.extend(db_results)
            stats['database'] = len(db_results)
            print(f"  ✅ Found {len(db_results)} existing suppliers\n")
        
        # Source 2: ThomasNet
        if 'thomasnet' in sources:
            print("🏭 Mining ThomasNet.com...")
            thomasnet_results = self.search_thomasnet(product, max_results=15)
            all_results.extend(thomasnet_results)
            stats['thomasnet'] = len(thomasnet_results)
        
        # Source 3: Google Custom Search
        if 'google' in sources:
            print("🌐 Mining Google Custom Search...")
            google_results = self.search_google_suppliers(product, max_results=10)
            all_results.extend(google_results)
            stats['google'] = len(google_results)
        
        # Source 4: GSA Advantage
        if 'gsa' in sources:
            print("🏛️  Mining GSA Advantage...")
            gsa_results = self.search_gsa_suppliers(product, max_results=10)
            all_results.extend(gsa_results)
            stats['gsa'] = len(gsa_results)
        
        stats['total_found'] = len(all_results)
        
        # AI qualify and import new suppliers
        print(f"{'='*60}")
        print(f"🤖 AI QUALIFICATION & IMPORT")
        print(f"{'='*60}\n")
        
        qualified = []
        review_queue = []
        
        for supplier in all_results:
            # Skip if already in database
            if supplier.get('already_in_db') or supplier.get('id'):
                qualified.append(supplier)
                continue
            
            # AI qualification
            print(f"  Scoring: {supplier['COMPANY NAME'][:50]}...")
            score = self._ai_qualify_supplier(supplier)
            supplier['AI SCORE'] = score
            supplier['ai_score'] = score  # For sorting
            
            print(f"    Score: {score}/100", end='')
            
            if score >= auto_import_threshold:
                # Auto-import high scores
                try:
                    # Check for duplicates
                    existing = self.airtable.search_records(
                        'GPSS SUPPLIERS',
                        formula=f"{{COMPANY NAME}} = '{supplier['COMPANY NAME']}'"
                    )
                    
                    if not existing:
                        self.airtable.create_record('GPSS SUPPLIERS', supplier)
                        stats['auto_imported'] += 1
                        print(f" → ✅ AUTO-IMPORTED")
                        qualified.append(supplier)
                    else:
                        print(f" → ⏭️  Already exists")
                        qualified.append(supplier)
                except Exception as e:
                    print(f" → ⚠️  Import failed: {e}")
                    review_queue.append(supplier)
                    stats['review_queue'] += 1
            
            elif score >= 70:
                # Add to review queue
                print(f" → 📋 Review queue")
                review_queue.append(supplier)
                stats['review_queue'] += 1
            
            else:
                # Too low score, skip
                print(f" → ❌ Score too low")
        
        stats['qualified'] = len(qualified)
        
        # Final summary
        print(f"\n{'='*60}")
        print(f"✅ MINING COMPLETE")
        print(f"{'='*60}")
        print(f"  📊 Database:        {stats['database']} suppliers")
        print(f"  🏭 ThomasNet:       {stats['thomasnet']} suppliers")
        print(f"  🌐 Google:          {stats['google']} suppliers")
        print(f"  🏛️  GSA Advantage:   {stats['gsa']} suppliers")
        print(f"  {'─'*56}")
        print(f"  📦 Total Found:     {stats['total_found']} suppliers")
        print(f"  ✅ Qualified:       {stats['qualified']} suppliers")
        print(f"  ⚡ Auto-Imported:   {stats['auto_imported']} suppliers")
        print(f"  📋 Review Queue:    {stats['review_queue']} suppliers")
        print(f"{'='*60}\n")
        
        return {
            'success': True,
            'suppliers': qualified,
            'review_queue': review_queue,
            'stats': stats
        }
    
    # ============================================
    # UPDATED MAIN FIND METHOD
    # ============================================
    
    def find_suppliers_for_product(self, product: str, category: str = None, 
                                    max_results: int = 10, auto_mine: bool = True) -> List[Dict]:
        """
        MAIN METHOD: Find suppliers for specific product
        
        Args:
            product: Product name or description
            category: Product category
            max_results: Maximum suppliers to return
            auto_mine: If True, automatically mine web sources if needed
            
        Returns:
            List of qualified suppliers ranked by fit
        """
        # Step 1: Check existing database
        keywords = product.split()
        existing = self.search_existing_suppliers(
            category=category,
            keywords=keywords,
            min_rating=3.0
        )
        
        print(f"Found {len(existing)} existing suppliers for '{product}'")
        
        # Step 2: If we have enough good suppliers, return them
        if len(existing) >= max_results:
            print(f"✅ Sufficient suppliers in database\n")
            return existing[:max_results]
        
        # Step 3: Mine from web if enabled and needed
        if auto_mine and len(existing) < max_results:
            print(f"\n⚠️  Only {len(existing)} suppliers in database. Mining web sources...\n")
            
            mine_results = self.mine_all_sources(
                product=product,
                category=category,
                sources=['thomasnet', 'google', 'gsa']  # Skip database (already checked)
            )
            
            # Combine existing + newly mined
            all_suppliers = existing + mine_results.get('suppliers', [])
            
            # Sort by score/rating
            all_suppliers.sort(key=lambda x: x.get('ai_score', x.get('overall_rating', 0)), reverse=True)
            
            return all_suppliers[:max_results]
        
        print(f"⚠️  Auto-mining disabled. Returning {len(existing)} suppliers from database.\n")
        return existing[:max_results]
    
    def create_supplier(self, supplier_data: Dict) -> Dict:
        """
        Add new supplier to database
        
        Args:
            supplier_data: Dictionary with supplier fields
            
        Returns:
            Created supplier record
        """
        try:
            # Required fields check
            if not supplier_data.get('COMPANY NAME'):
                raise ValueError("COMPANY NAME is required")
            
            # Set defaults
            if 'BUSINESS STATUS' not in supplier_data:
                supplier_data['BUSINESS STATUS'] = 'Prospective'
            if 'DISCOVERY DATE' not in supplier_data:
                supplier_data['DISCOVERY DATE'] = datetime.now().strftime('%Y-%m-%d')
            
            # Create in Airtable
            record = self.airtable.create_record('GPSS SUPPLIERS', supplier_data)
            
            print(f"Created supplier: {supplier_data.get('COMPANY NAME')}")
            
            return record
            
        except Exception as e:
            print(f"Error creating supplier: {e}")
            return {'error': str(e)}
    
    def update_supplier(self, supplier_id: str, updates: Dict) -> Dict:
        """
        Update supplier information
        
        Args:
            supplier_id: Airtable record ID
            updates: Fields to update
            
        Returns:
            Updated record
        """
        try:
            record = self.airtable.update_record('GPSS SUPPLIERS', supplier_id, updates)
            return record
        except Exception as e:
            print(f"Error updating supplier: {e}")
            return {'error': str(e)}
    
    def get_supplier(self, supplier_id: str) -> Optional[Dict]:
        """Get supplier by ID"""
        try:
            suppliers = self.airtable.get_all_records('GPSS SUPPLIERS')
            for supplier in suppliers:
                if supplier.get('id') == supplier_id:
                    return supplier
            return None
        except Exception as e:
            print(f"Error getting supplier: {e}")
            return None

    def update_supplier_rating(self, supplier_id: str, outcome: str) -> Dict:
        """
        Update supplier OVERALL RATING based on quote/bid outcome.
        
        The system learns from each interaction:
        - 'quote_received_fast' (< 2 days): +1 star (max 5)
        - 'quote_received': no change
        - 'quote_late' (> 5 days): -1 star (min 1)
        - 'no_response': -1 star (min 1)
        - 'competitive_price': +1 star (max 5)
        - 'overpriced': -1 star (min 1)
        - 'won_with_supplier': +1 star (max 5)
        
        Args:
            supplier_id: Airtable record ID
            outcome: One of the outcome strings above
            
        Returns:
            Updated rating info
        """
        try:
            supplier = self.get_supplier(supplier_id)
            if not supplier:
                return {'error': f'Supplier {supplier_id} not found'}
            
            current_rating = supplier['fields'].get('OVERALL RATING', 3)
            if not current_rating:
                current_rating = 3  # Default to middle rating
            
            # Adjust rating based on outcome
            adjustments = {
                'quote_received_fast': +1,
                'quote_received': 0,
                'quote_late': -1,
                'no_response': -1,
                'competitive_price': +1,
                'overpriced': -1,
                'won_with_supplier': +1,
                'reliable_delivery': +1,
                'late_delivery': -1,
            }
            
            adjustment = adjustments.get(outcome, 0)
            new_rating = max(1, min(5, current_rating + adjustment))
            
            if new_rating != current_rating:
                self.airtable.update_record('GPSS SUPPLIERS', supplier_id, {
                    'OVERALL RATING': new_rating
                })
                print(f"Updated supplier {supplier['fields'].get('COMPANY NAME', supplier_id)}: "
                      f"rating {current_rating} → {new_rating} (outcome: {outcome})")
            
            return {
                'success': True,
                'supplier_id': supplier_id,
                'previous_rating': current_rating,
                'new_rating': new_rating,
                'outcome': outcome,
                'adjustment': adjustment,
            }
            
        except Exception as e:
            print(f"Error updating supplier rating: {e}")
            return {'error': str(e)}
    
    # ============================================
    # CSV IMPORT
    # ============================================
    
    def import_suppliers_from_csv(self, csv_file_path: str, field_mapping: Dict = None) -> Dict:
        """
        Import suppliers from CSV file
        
        Args:
            csv_file_path: Path to CSV file
            field_mapping: Dictionary mapping CSV columns to Airtable fields
                          Example: {'Company': 'Company Name', 'Email': 'Primary Contact Email'}
                          If None, assumes CSV columns match Airtable field names
            
        Returns:
            Dictionary with import stats
        """
        import csv
        
        try:
            print(f"📥 Importing suppliers from CSV: {csv_file_path}\n")
            
            imported = 0
            skipped = 0
            errors = []
            
            with open(csv_file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row_num, row in enumerate(reader, start=2):  # Start at 2 (header is row 1)
                    try:
                        # Map CSV columns to Airtable fields
                        supplier_data = {}
                        
                        if field_mapping:
                            for csv_col, airtable_field in field_mapping.items():
                                if csv_col in row:
                                    supplier_data[airtable_field] = row[csv_col]
                        else:
                            # Assume CSV columns match Airtable fields
                            supplier_data = dict(row)
                        
                        # Add import metadata
                        supplier_data['DISCOVERY METHOD'] = 'CSV Import'
                        supplier_data['DISCOVERY DATE'] = datetime.now().strftime('%Y-%m-%d')
                        supplier_data['DISCOVERED BY'] = 'NEXUS CSV Import'
                        supplier_data['BUSINESS STATUS'] = supplier_data.get('BUSINESS STATUS', 'Prospective')
                        supplier_data['RELATIONSHIP STAGE'] = supplier_data.get('RELATIONSHIP STAGE', 'Discovered')
                        
                        # Check if company name exists
                        company_name = supplier_data.get('COMPANY NAME', '')
                        if not company_name:
                            errors.append(f"Row {row_num}: Missing company name")
                            skipped += 1
                            continue
                        
                        # Check for duplicates
                        existing = self.airtable.search_records(
                            'GPSS SUPPLIERS',
                            formula=f"{{COMPANY NAME}} = '{company_name}'"
                        )
                        
                        if existing:
                            print(f"  ⏭️  Row {row_num}: {company_name} - Already exists")
                            skipped += 1
                        else:
                            self.airtable.create_record('GPSS SUPPLIERS', supplier_data)
                            print(f"  ✅ Row {row_num}: {company_name} - Imported")
                            imported += 1
                    
                    except Exception as e:
                        error_msg = f"Row {row_num}: {str(e)}"
                        errors.append(error_msg)
                        print(f"  ❌ {error_msg}")
                        skipped += 1
            
            print(f"\n{'='*60}")
            print(f"📊 CSV IMPORT SUMMARY")
            print(f"{'='*60}")
            print(f"  ✅ Imported: {imported}")
            print(f"  ⏭️  Skipped:  {skipped}")
            print(f"  ❌ Errors:   {len(errors)}")
            print(f"{'='*60}\n")
            
            return {
                'success': True,
                'imported': imported,
                'skipped': skipped,
                'errors': errors
            }
        
        except FileNotFoundError:
            return {'success': False, 'error': f'File not found: {csv_file_path}'}
        except Exception as e:
            return {'success': False, 'error': str(e)}


class GPSSAutomatedQuoting:
    """
    AI-powered automated quoting system
    
    Connects:
    - Opportunity mining (finds RFQs)
    - Supplier mining (finds suppliers)
    - AI matching (connects them)
    - Auto-quote generation
    """
    
    def __init__(self):
        self.airtable = AirtableClient()
        self.ai = AnthropicClient()
        self.supplier_miner = GPSSSupplierMiner()
    
    def extract_product_specs(self, opportunity_id: str) -> Dict:
        """
        Extract product specifications from opportunity
        
        Args:
            opportunity_id: Airtable opportunity ID
            
        Returns:
            Dictionary with extracted specs
        """
        try:
            # Get opportunity details
            opportunities = self.airtable.get_all_records('Opportunities')
            opportunity = None
            for opp in opportunities:
                if opp.get('id') == opportunity_id:
                    opportunity = opp
                    break
            
            if not opportunity:
                return {'error': 'Opportunity not found'}
            
            fields = opportunity.get('fields', {})
            description = fields.get('Description', '') or fields.get('RFP Description', '')
            title = fields.get('Opportunity Name', '') or fields.get('Title', '')
            
            # Use AI to extract specifications
            prompt = f"""Extract product specifications from this government opportunity.

Opportunity Title: {title}
Description: {description}

Extract and return as JSON:
{{
  "product_name": "Main product/service",
  "quantity": "Number or range",
  "category": "Product category (Office Supplies, Technology, Furniture, etc.)",
  "specifications": "Technical requirements",
  "delivery_location": "Where to deliver",
  "delivery_deadline": "When needed",
  "keywords": ["keyword1", "keyword2", "keyword3"]
}}

Return ONLY valid JSON, no other text."""
            
            response = self.ai.complete(prompt, max_tokens=1000)
            
            # Parse response
            clean_response = response.strip()
            if clean_response.startswith('```json'):
                clean_response = clean_response.replace('```json', '').replace('```', '').strip()
            
            specs = json.loads(clean_response)
            specs['opportunity_id'] = opportunity_id
            
            return specs
            
        except Exception as e:
            print(f"Error extracting specs: {e}")
            return {
                'opportunity_id': opportunity_id,
                'product_name': 'Unknown',
                'category': None,
                'keywords': []
            }
    
    def find_suppliers_for_opportunity(self, opportunity_id: str, max_suppliers: int = 8) -> List[Dict]:
        """
        Find matching suppliers for an opportunity
        
        Args:
            opportunity_id: Opportunity to find suppliers for
            max_suppliers: Maximum number of suppliers to return
            
        Returns:
            List of ranked suppliers
        """
        # Extract specs
        specs = self.extract_product_specs(opportunity_id)
        
        # Find suppliers
        suppliers = self.supplier_miner.find_suppliers_for_product(
            product=specs.get('product_name', ''),
            category=specs.get('category'),
            max_results=max_suppliers
        )
        
        return suppliers
    
    def generate_quote_request_email(self, supplier: Dict, specs: Dict) -> Dict:
        """
        Generate personalized quote request email for supplier
        
        Args:
            supplier: Supplier record
            specs: Product specifications
            
        Returns:
            Dictionary with subject and body
        """
        try:
            company_name = supplier.get('company_name', 'Supplier')
            contact_name = supplier.get('primary_contact_name', 'Sales Team')
            relationship = supplier.get('relationship_stage', 'New')
            past_orders = supplier.get('total_orders', 0)
            
            # Build context for AI
            context = f"""
Company: {company_name}
Contact: {contact_name}
Relationship: {relationship}
Past Orders: {past_orders}
"""
            
            prompt = f"""Generate a professional quote request email for a government contract.

SUPPLIER INFO:
{context}

PRODUCT REQUEST:
Product: {specs.get('product_name', 'Unknown')}
Quantity: {specs.get('quantity', 'To be determined')}
Specifications: {specs.get('specifications', 'Standard specifications')}
Delivery Location: {specs.get('delivery_location', 'To be determined')}
Delivery Deadline: {specs.get('delivery_deadline', 'As soon as possible')}

REQUIREMENTS:
- Professional tone
- Request Net 30 payment terms
- Ask for delivery timeline
- Mention this is for government contract
- Include DEE DAVIS INC details (EDWOSB, CAGE: 8UMX3)
- Request response within 24-48 hours

Return as JSON:
{{
  "subject": "Quote Request - [Product] for Government Contract",
  "body": "Email body text"
}}"""
            
            response = self.ai.complete(prompt, max_tokens=1000)
            
            # Parse response
            clean_response = response.strip()
            if clean_response.startswith('```json'):
                clean_response = clean_response.replace('```json', '').replace('```', '').strip()
            
            email = json.loads(clean_response)
            
            return email
            
        except Exception as e:
            print(f"Error generating email: {e}")
            return {
                'subject': f"Quote Request - {specs.get('product_name')}",
                'body': f"We are requesting a quote for {specs.get('product_name')} for a government contract."
            }
    
    def create_supplier_quote_request(self, opportunity_id: str, supplier_id: str, specs: Dict) -> Dict:
        """
        Create supplier quote request record
        
        Args:
            opportunity_id: Opportunity ID
            supplier_id: Supplier ID  
            specs: Product specifications
            
        Returns:
            Created quote request record
        """
        try:
            # Get supplier details
            supplier = self.supplier_miner.get_supplier(supplier_id)
            if not supplier:
                return {'error': 'Supplier not found'}
            
            # Generate email
            email = self.generate_quote_request_email(supplier.get('fields', {}), specs)
            
            # Create quote request record
            quote_data = {
                'Opportunity': [opportunity_id],
                'Supplier': [supplier_id],
                'Product/Service Requested': specs.get('product_name', ''),
                'Quantity': specs.get('quantity', ''),
                'Specifications': specs.get('specifications', ''),
                'Delivery Location': specs.get('delivery_location', ''),
                'Request Status': 'Draft',
                'Request Method': 'Auto-Generated',
                'Request Email': f"Subject: {email.get('subject')}\n\n{email.get('body')}"
            }
            
            record = self.airtable.create_record('GPSS Supplier Quotes', quote_data)
            
            return record
            
        except Exception as e:
            print(f"Error creating quote request: {e}")
            return {'error': str(e)}
    
    def process_opportunity(self, opportunity_id: str, max_suppliers: int = 5) -> Dict:
        """
        MAIN METHOD: Process opportunity end-to-end
        
        Args:
            opportunity_id: Opportunity to process
            max_suppliers: Number of suppliers to contact
            
        Returns:
            Processing summary
        """
        try:
            # Step 1: Extract specs
            print(f"Extracting specifications for opportunity {opportunity_id}...")
            specs = self.extract_product_specs(opportunity_id)
            
            if specs.get('error'):
                return specs
            
            # Step 2: Find suppliers
            print(f"Finding suppliers for '{specs.get('product_name')}'...")
            suppliers = self.find_suppliers_for_opportunity(opportunity_id, max_suppliers)
            
            # Step 3: Generate quote requests
            print(f"Generating quote requests for {len(suppliers)} suppliers...")
            quote_requests = []
            for supplier in suppliers:
                quote = self.create_supplier_quote_request(
                    opportunity_id=opportunity_id,
                    supplier_id=supplier.get('id'),
                    specs=specs
                )
                if not quote.get('error'):
                    quote_requests.append(quote)
            
            return {
                'success': True,
                'opportunity_id': opportunity_id,
                'specs': specs,
                'suppliers_found': len(suppliers),
                'quote_requests_created': len(quote_requests),
                'quote_requests': quote_requests
            }
            
        except Exception as e:
            print(f"Error processing opportunity: {e}")
            return {
                'success': False,
                'error': str(e)
            }


# =====================================================================
# SUBCONTRACTOR MINING & MANAGEMENT
# =====================================================================

class GPSSSubcontractorMiner:
    """
    Find and manage subcontractors in the area of each contract
    
    Core Strategy: Partner with subcontractors in each contract location
    - Leverage their local expertise and past performance
    - You manage as prime contractor (EDWOSB status)
    - They execute work (local jobs, local knowledge)
    
    4 Core Functions:
    1. Find Subcontractors (Google search by service + location)
    2. Send RFQs (bulk email with scope)
    3. Score Quotes (AI ranks responses 0-100)
    4. Calculate Markup (add percentage, generate final bid)
    """
    
    def __init__(self):
        self.airtable = AirtableClient()
        self.ai = AnthropicClient()

    def _fetch_url_text_excerpt(self, url: str, max_chars: int = 12000) -> Dict:
        """Pull visible text from a homepage for ranking context (best-effort)."""
        out = {'text': '', 'error': None}
        if not url or not str(url).strip().startswith('http'):
            out['error'] = 'no_url'
            return out
        try:
            from bs4 import BeautifulSoup
            headers = {
                'User-Agent': 'Mozilla/5.0 (compatible; NEXUS/1.0; business research; +https://deedavis.biz)'
            }
            r = requests.get(url.strip(), headers=headers, timeout=14, allow_redirects=True)
            if r.status_code != 200:
                out['error'] = f'http_{r.status_code}'
                return out
            soup = BeautifulSoup(r.content, 'html.parser')
            for tag in soup(['script', 'style', 'noscript', 'svg']):
                tag.decompose()
            text = soup.get_text(separator='\n', strip=True)
            lines = [ln for ln in text.splitlines() if ln.strip()]
            text = '\n'.join(lines[:500])
            if len(text) > max_chars:
                text = text[:max_chars] + '\n...[truncated]'
            out['text'] = text
        except Exception as e:
            out['error'] = str(e)[:240]
        return out

    def _cse_snippets_for_query(self, query: str, num: int = 4) -> List[Dict]:
        """Optional Google Custom Search snippets (same env as subcontractor discovery)."""
        api_key = os.environ.get('GOOGLE_CSE_API_KEY')
        cse_id = os.environ.get('GOOGLE_CSE_ID')
        if not api_key or not cse_id or not (query or '').strip():
            return []
        try:
            url = 'https://www.googleapis.com/customsearch/v1'
            params = {'key': api_key, 'cx': cse_id, 'q': query.strip()[:200], 'num': min(num, 10)}
            response = requests.get(url, params=params, timeout=12)
            if response.status_code != 200:
                return []
            items = []
            for item in response.json().get('items', []) or []:
                items.append({
                    'title': item.get('title', ''),
                    'snippet': item.get('snippet', ''),
                    'link': item.get('link', ''),
                })
            time.sleep(0.35)
            return items
        except Exception:
            return []

    def minimal_research_for_ranking(
        self,
        company_name: str,
        website: str = '',
        needed_skills: Optional[List[str]] = None,
        job_location: str = '',
        job_summary: str = '',
    ) -> Dict:
        """
        Minimal fresh research so ranking reflects fit-for-job, not only Airtable fields.
        Uses homepage text when WEBSITE is set, plus one CSE query when keys exist.
        """
        needed_skills = needed_skills or []
        primary_skill = needed_skills[0] if needed_skills else ''
        fetched = self._fetch_url_text_excerpt(website) if website else {'text': '', 'error': 'no_url'}
        cse_query_parts = [f'"{company_name}"']
        if primary_skill:
            cse_query_parts.append(primary_skill)
        if job_location:
            cse_query_parts.append(job_location)
        cse_query = ' '.join(cse_query_parts)
        cse_items = self._cse_snippets_for_query(cse_query, num=4)
        sources = []
        if fetched.get('text'):
            sources.append('website')
        if cse_items:
            sources.append('google_cse')
        return {
            'company_name': company_name,
            'website_excerpt': fetched.get('text', ''),
            'website_fetch_error': fetched.get('error'),
            'cse_query': cse_query if cse_items or os.environ.get('GOOGLE_CSE_API_KEY') else '',
            'cse_results': cse_items,
            'sources_used': sources,
            'research_summary': self._brief_research_summary(fetched.get('text', ''), cse_items),
        }

    @staticmethod
    def _brief_research_summary(website_text: str, cse_items: List[Dict]) -> str:
        parts = []
        if website_text:
            preview = website_text.replace('\n', ' ')[:420]
            parts.append(f'Website: {preview}')
        for it in (cse_items or [])[:2]:
            sn = (it.get('snippet') or '').replace('\n', ' ')
            if sn:
                parts.append(f'Search: {sn[:320]}')
        return ' | '.join(parts) if parts else 'No live research retrieved (add WEBSITE or configure Google CSE).'
    
    # ============================================
    # FUNCTION 1: FIND SUBCONTRACTORS IN AREA
    # ============================================
    
    def find_subcontractors(self, service_type: str, location: str, max_results: int = 10) -> List[Dict]:
        """
        Find subcontractors in the area using Google Custom Search
        
        Args:
            service_type: e.g. "aircraft wash", "janitorial services", "IT support"
            location: e.g. "Virginia Beach VA", "San Antonio TX"
            max_results: Maximum subcontractors to return
            
        Returns:
            List of subcontractor dictionaries ready for Airtable
        """
        try:
            api_key = os.environ.get('GOOGLE_CSE_API_KEY')
            cse_id = os.environ.get('GOOGLE_CSE_ID')
            
            if not api_key or not cse_id:
                print("  ℹ️  Google CSE credentials not set. Cannot search for subcontractors.\n")
                return []
            
            print(f"🔍 Searching for subcontractors: {service_type} in {location}")
            results = []
            seen_domains = set()
            
            # Build targeted search queries
            queries = [
                f'"{service_type}" "{location}"',
                f'"{service_type}" contractor "{location}"',
                f'"{service_type}" services "{location}"',
                f'"{service_type}" government contract "{location}"'
            ]
            
            for query in queries:
                try:
                    url = 'https://www.googleapis.com/customsearch/v1'
                    params = {
                        'key': api_key,
                        'cx': cse_id,
                        'q': query,
                        'num': 10
                    }
                    
                    response = requests.get(url, params=params, timeout=10)
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        for item in data.get('items', []):
                            title = item.get('title', '')
                            snippet = item.get('snippet', '')
                            link = item.get('link', '')
                            
                            # Extract domain to avoid duplicates
                            from urllib.parse import urlparse
                            domain = urlparse(link).netloc
                            
                            # Skip if we've already seen this domain
                            if domain in seen_domains:
                                continue
                            
                            # Skip non-business sites
                            skip_domains = ['facebook.com', 'linkedin.com', 'yelp.com', 'yellowpages.com', 'bbb.org', 'wikipedia.org']
                            if any(skip in domain for skip in skip_domains):
                                continue
                            
                            # Use AI to extract company info
                            company_info = self._ai_extract_subcontractor_info(title, snippet, link, service_type, location)
                            
                            if company_info and company_info.get('company_name'):
                                seen_domains.add(domain)
                                results.append({
                                    'COMPANY NAME': company_info['company_name'],
                                    'SERVICE TYPE': service_type,
                                    'CITY': company_info.get('city', location.split(',')[0].strip()),
                                    'STATE': company_info.get('state', location.split(',')[-1].strip()),
                                    'WEBSITE': link,
                                    'DESCRIPTION': snippet[:500],
                                    'PHONE': company_info.get('phone', ''),
                                    'EMAIL': company_info.get('email', ''),
                                    'DISCOVERY METHOD': 'Google Search',
                                    'DISCOVERY DATE': datetime.now().strftime('%Y-%m-%d'),
                                    'DISCOVERED BY': 'NEXUS Auto-Mining',
                                    'RELATIONSHIP STATUS': 'Cold',
                                    'SOURCE NOTES': f'Found via Google search for "{query}"'
                                })
                                print(f"  ✓ {company_info['company_name']}")
                                
                                if len(results) >= max_results:
                                    break
                    
                    # Add small delay to respect rate limits
                    time.sleep(0.5)
                    
                    if len(results) >= max_results:
                        break
                        
                except Exception as e:
                    print(f"  ⚠️  Error with query '{query}': {e}")
                    continue
            
            print(f"  ✅ Found {len(results)} subcontractors in area\n")
            return results
            
        except Exception as e:
            print(f"  ❌ Error finding subcontractors: {e}\n")
            return []

    # ============================================
    # SOURCE 2: SBA DYNAMIC SMALL BUSINESS SEARCH
    # ============================================

    def find_subcontractors_sba(self, service_type: str, naics_code: str = '', state: str = '', max_results: int = 10) -> List[Dict]:
        """
        Search SBA Dynamic Small Business Search for certified small business subs.
        Great for finding EDWOSB, WOSB, 8(a), HUBZone, SDVOSB subs.
        Free API, no key needed.
        """
        try:
            print(f"🔍 Searching SBA for: {service_type} (NAICS: {naics_code}, State: {state})")
            results = []

            # SBA DSBS API endpoint
            base_url = 'https://web.sba.gov/pro-net/search/dsp_dsbs.cfm'
            api_url = 'https://web.sba.gov/api/pro-net/search/profiles'
            
            # Also try the SAM.gov entity search for small business subs
            sam_key = os.environ.get('SAM_GOV_API_KEY', '')
            if sam_key and naics_code:
                try:
                    url = 'https://api.sam.gov/entity-information/v3/entities'
                    params = {
                        'api_key': sam_key,
                        'naicsCode': naics_code.split(',')[0].strip() if naics_code else '',
                        'registrationStatus': 'A',
                        'purposeOfRegistrationCode': 'Z2',  # Government business
                        'sbaBusinessTypeCode': ['23', '27', 'A2', 'XX'],  # Small biz types
                        'page': 0,
                        'size': min(max_results, 25),
                    }
                    if state:
                        params['physicalAddressStateCode'] = state.upper()[:2]
                    
                    response = requests.get(url, params=params, timeout=15)
                    if response.status_code == 200:
                        data = response.json()
                        entities = data.get('entityData', [])
                        
                        for entity in entities:
                            core = entity.get('coreData', {})
                            entity_info = core.get('entityInformation', {})
                            phys_addr = core.get('physicalAddress', {})
                            
                            company_name = entity_info.get('entityLegalBusinessName', '')
                            if not company_name:
                                continue
                            
                            # Get certifications
                            certs = []
                            biz_types = entity.get('assertions', {}).get('sbaBusinessTypes', [])
                            for bt in (biz_types if isinstance(biz_types, list) else []):
                                cert_name = bt.get('sbaBusinessTypeDesc', '')
                                if cert_name:
                                    certs.append(cert_name)
                            
                            # Get POC info
                            poc = core.get('generalInformation', {}).get('agencyBusinessPOC', {})
                            email = poc.get('email', '') if isinstance(poc, dict) else ''
                            phone = poc.get('phone', '') if isinstance(poc, dict) else ''
                            
                            results.append({
                                'COMPANY NAME': company_name,
                                'SERVICE TYPE': service_type,
                                'CITY': phys_addr.get('city', ''),
                                'STATE': phys_addr.get('stateOrProvinceCode', state),
                                'WEBSITE': entity_info.get('entityURL', ''),
                                'EMAIL': email,
                                'PHONE': phone,
                                'DESCRIPTION': f"SAM.gov registered entity. NAICS: {naics_code}. {', '.join(certs) if certs else ''}",
                                'SOCIOECONOMIC CERTS': certs[:5] if certs else [],
                                'NAISC CODES': [naics_code] if naics_code else [],
                                'DISCOVERY METHOD': 'SAM.gov Entity Search',
                                'DISCOVERY DATE': datetime.now().strftime('%Y-%m-%d'),
                                'DISCOVERED BY': 'NEXUS Auto-Mining',
                                'RELATIONSHIP STATUS': 'Cold',
                                'SOURCE NOTES': f'Found via SAM.gov entity search for NAICS {naics_code}'
                            })
                            print(f"  ✓ {company_name} ({', '.join(certs[:2]) if certs else 'small biz'})")
                            
                            if len(results) >= max_results:
                                break
                    else:
                        print(f"  ⚠️  SAM.gov API returned {response.status_code}")
                except Exception as e:
                    print(f"  ⚠️  SAM.gov entity search error: {e}")
            
            # Fallback: Google search specifically for SBA-registered subs
            if len(results) < max_results:
                google_results = self.find_subcontractors(
                    f"{service_type} small business certified", 
                    state or 'Michigan',
                    max_results=max_results - len(results)
                )
                results.extend(google_results)
            
            print(f"  ✅ SBA search found {len(results)} subcontractors\n")
            return results
            
        except Exception as e:
            print(f"  ❌ SBA search error: {e}\n")
            return []

    # ============================================
    # SOURCE 3: GOOGLE MAPS / PLACES API
    # ============================================

    def find_subcontractors_google_maps(self, service_type: str, location: str, max_results: int = 10) -> List[Dict]:
        """
        Search Google Maps/Places for local businesses matching the service type.
        Uses Google Custom Search with site:google.com/maps as fallback if no Places API key.
        """
        try:
            print(f"🔍 Searching Google Maps for: {service_type} near {location}")
            results = []
            
            api_key = os.environ.get('GOOGLE_CSE_API_KEY')
            cse_id = os.environ.get('GOOGLE_CSE_ID')
            
            if not api_key or not cse_id:
                print("  ℹ️  No Google API keys set. Skipping Google Maps search.\n")
                return []
            
            # Use Google CSE with local-business focused queries
            queries = [
                f'{service_type} near {location} site:google.com/maps',
                f'{service_type} contractor {location}',
                f'{service_type} company {location} phone email',
                f'small business {service_type} {location}',
            ]
            
            seen_domains = set()
            
            for query in queries:
                if len(results) >= max_results:
                    break
                try:
                    url = 'https://www.googleapis.com/customsearch/v1'
                    params = {
                        'key': api_key,
                        'cx': cse_id,
                        'q': query,
                        'num': 10
                    }
                    
                    response = requests.get(url, params=params, timeout=10)
                    
                    if response.status_code == 200:
                        data = response.json()
                        for item in data.get('items', []):
                            title = item.get('title', '')
                            snippet = item.get('snippet', '')
                            link = item.get('link', '')
                            
                            from urllib.parse import urlparse
                            domain = urlparse(link).netloc
                            
                            if domain in seen_domains:
                                continue
                            
                            skip_domains = ['facebook.com', 'linkedin.com', 'yelp.com', 
                                          'yellowpages.com', 'wikipedia.org', 'google.com', 
                                          'maps.google.com', 'indeed.com', 'glassdoor.com']
                            if any(skip in domain for skip in skip_domains):
                                continue
                            
                            company_info = self._ai_extract_subcontractor_info(title, snippet, link, service_type, location)
                            
                            if company_info and company_info.get('company_name'):
                                seen_domains.add(domain)
                                results.append({
                                    'COMPANY NAME': company_info['company_name'],
                                    'SERVICE TYPE': service_type,
                                    'CITY': company_info.get('city', location.split(',')[0].strip()),
                                    'STATE': company_info.get('state', location.split(',')[-1].strip() if ',' in location else ''),
                                    'WEBSITE': link,
                                    'PHONE': company_info.get('phone', ''),
                                    'EMAIL': company_info.get('email', ''),
                                    'DESCRIPTION': snippet[:500],
                                    'DISCOVERY METHOD': 'Google Maps Search',
                                    'DISCOVERY DATE': datetime.now().strftime('%Y-%m-%d'),
                                    'DISCOVERED BY': 'NEXUS Auto-Mining',
                                    'RELATIONSHIP STATUS': 'Cold',
                                    'SOURCE NOTES': f'Found via Google Maps search for "{service_type}" in {location}'
                                })
                                print(f"  ✓ {company_info['company_name']}")
                                
                                if len(results) >= max_results:
                                    break
                    
                    time.sleep(0.5)
                except Exception as e:
                    print(f"  ⚠️  Google Maps query error: {e}")
                    continue
            
            print(f"  ✅ Google Maps found {len(results)} subcontractors\n")
            return results
            
        except Exception as e:
            print(f"  ❌ Google Maps search error: {e}\n")
            return []

    # ============================================
    # SOURCE 4: FACEBOOK BUSINESS PAGES (via Google)
    # ============================================

    def find_subcontractors_facebook(self, service_type: str, location: str, max_results: int = 10) -> List[Dict]:
        """
        Find small business owners on Facebook Business Pages via Google search.
        Facebook Marketplace & business pages are where small trade businesses
        (landscapers, haulers, painters, cleaners, handymen) advertise.
        No FB API needed — Google indexes FB business pages.
        """
        try:
            print(f"🔍 Searching Facebook Business Pages for: {service_type} in {location}")
            results = []
            
            api_key = os.environ.get('GOOGLE_CSE_API_KEY')
            cse_id = os.environ.get('GOOGLE_CSE_ID')
            
            if not api_key or not cse_id:
                print("  ℹ️  No Google API keys. Skipping Facebook search.\n")
                return []
            
            # Search Google for Facebook business pages
            queries = [
                f'site:facebook.com "{service_type}" "{location}"',
                f'site:facebook.com "{service_type}" near "{location}" small business',
                f'site:facebook.com/pages "{service_type}" "{location}"',
            ]
            
            seen_pages = set()
            
            for query in queries:
                if len(results) >= max_results:
                    break
                try:
                    url = 'https://www.googleapis.com/customsearch/v1'
                    params = {
                        'key': api_key,
                        'cx': cse_id,
                        'q': query,
                        'num': 10
                    }
                    
                    response = requests.get(url, params=params, timeout=10)
                    
                    if response.status_code == 200:
                        data = response.json()
                        for item in data.get('items', []):
                            title = item.get('title', '')
                            snippet = item.get('snippet', '')
                            link = item.get('link', '')
                            
                            # Only process facebook.com results
                            if 'facebook.com' not in link:
                                continue
                            
                            # Skip non-business pages (groups, events, posts, photos, etc)
                            skip_patterns = ['/groups/', '/events/', '/photo', '/posts/', '/videos/', 
                                           '/marketplace/item/', '/story.php', '/permalink']
                            if any(sp in link for sp in skip_patterns):
                                continue
                            
                            # Deduplicate by page URL
                            page_key = link.split('?')[0].rstrip('/')
                            if page_key in seen_pages:
                                continue
                            
                            # Use AI to extract business info from FB page snippet
                            extract_prompt = f"""Extract small business information from this Facebook business page result.

Title: {title}
Snippet: {snippet}
URL: {link}
Service we're looking for: {service_type}
Location: {location}

Return ONLY valid JSON:
{{
  "company_name": "Business name (clean, no ' - Home | Facebook' suffix)",
  "city": "City if found",
  "state": "State abbreviation if found",
  "phone": "Phone if found in snippet, else empty string",
  "email": "Email if found in snippet, else empty string",
  "is_relevant_business": true/false,
  "description": "Brief description of what they do based on snippet"
}}

Rules:
- Remove " - Home | Facebook" or similar suffixes from company name
- is_relevant_business = true only if this looks like a real small business offering {service_type}
- If it's a news article, directory listing, or not a business, set is_relevant_business = false
- Return ONLY JSON"""
                            
                            try:
                                resp = self.ai.complete(extract_prompt, max_tokens=300)
                                clean = resp.strip()
                                if clean.startswith('```'):
                                    clean = re.sub(r'^```json\s*', '', clean)
                                    clean = re.sub(r'```\s*$', '', clean)
                                    clean = clean.strip()
                                info = json.loads(clean)
                                
                                if info.get('is_relevant_business') and info.get('company_name'):
                                    seen_pages.add(page_key)
                                    results.append({
                                        'COMPANY NAME': info['company_name'],
                                        'SERVICE TYPE': service_type,
                                        'CITY': info.get('city', location.split(',')[0].strip()),
                                        'STATE': info.get('state', ''),
                                        'WEBSITE': link,
                                        'PHONE': info.get('phone', ''),
                                        'EMAIL': info.get('email', ''),
                                        'DESCRIPTION': info.get('description', snippet[:300]),
                                        'DISCOVERY METHOD': 'Facebook Business Pages',
                                        'DISCOVERY DATE': datetime.now().strftime('%Y-%m-%d'),
                                        'DISCOVERED BY': 'NEXUS Auto-Mining',
                                        'RELATIONSHIP STATUS': 'Cold',
                                        'SOURCE NOTES': f'Found on Facebook: {link}'
                                    })
                                    print(f"  ✓ {info['company_name']} (via Facebook)")
                                    
                                    if len(results) >= max_results:
                                        break
                            except Exception as e:
                                continue
                    
                    time.sleep(0.5)
                except Exception as e:
                    print(f"  ⚠️  Facebook search query error: {e}")
                    continue
            
            print(f"  ✅ Facebook search found {len(results)} subcontractors\n")
            return results
            
        except Exception as e:
            print(f"  ❌ Facebook search error: {e}\n")
            return []

    # ============================================
    # MULTI-SOURCE MINE: ALL SOURCES AT ONCE
    # ============================================

    def mine_all_sources(self, service_type: str, location: str = 'Michigan', 
                         naics_code: str = '', max_per_source: int = 5) -> Dict:
        """
        Mine subcontractors from ALL available sources at once.
        Deduplicates results across sources.
        Returns dict with results by source + combined unique list.
        """
        try:
            print(f"\n{'='*60}")
            print(f"🚀 MULTI-SOURCE MINING: {service_type}")
            print(f"   Location: {location} | NAICS: {naics_code or 'N/A'}")
            print(f"{'='*60}\n")

            all_results = []
            source_counts = {}
            seen_names = set()

            # Source 1: Google Search
            print("--- Source 1: Google Search ---")
            google_results = self.find_subcontractors(service_type, location, max_results=max_per_source)
            source_counts['Google Search'] = len(google_results)
            for r in google_results:
                name_key = r.get('COMPANY NAME', '').lower().strip()
                if name_key and name_key not in seen_names:
                    seen_names.add(name_key)
                    r['_source'] = 'Google Search'
                    all_results.append(r)

            # Source 2: SAM.gov / SBA
            state = ''
            if location:
                # Try to extract state from location
                parts = location.split(',')
                if len(parts) > 1:
                    state = parts[-1].strip()
                elif len(location) == 2:
                    state = location
                elif location.lower() in ['michigan', 'mi']:
                    state = 'MI'
            
            print("\n--- Source 2: SAM.gov / SBA ---")
            sba_results = self.find_subcontractors_sba(service_type, naics_code=naics_code, 
                                                        state=state, max_results=max_per_source)
            source_counts['SAM.gov / SBA'] = len(sba_results)
            for r in sba_results:
                name_key = r.get('COMPANY NAME', '').lower().strip()
                if name_key and name_key not in seen_names:
                    seen_names.add(name_key)
                    r['_source'] = 'SAM.gov / SBA'
                    all_results.append(r)

            # Source 3: Google Maps / Local
            print("\n--- Source 3: Google Maps / Local ---")
            maps_results = self.find_subcontractors_google_maps(service_type, location, max_results=max_per_source)
            source_counts['Google Maps'] = len(maps_results)
            for r in maps_results:
                name_key = r.get('COMPANY NAME', '').lower().strip()
                if name_key and name_key not in seen_names:
                    seen_names.add(name_key)
                    r['_source'] = 'Google Maps'
                    all_results.append(r)

            # Source 4: Facebook Business Pages
            print("\n--- Source 4: Facebook Business Pages ---")
            fb_results = self.find_subcontractors_facebook(service_type, location, max_results=max_per_source)
            source_counts['Facebook'] = len(fb_results)
            for r in fb_results:
                name_key = r.get('COMPANY NAME', '').lower().strip()
                if name_key and name_key not in seen_names:
                    seen_names.add(name_key)
                    r['_source'] = 'Facebook'
                    all_results.append(r)

            print(f"\n{'='*60}")
            print(f"✅ MINING COMPLETE: {len(all_results)} unique subcontractors found")
            for src, count in source_counts.items():
                print(f"   {src}: {count}")
            print(f"{'='*60}\n")

            return {
                'results': all_results,
                'total': len(all_results),
                'by_source': source_counts,
                'service_type': service_type,
                'location': location
            }
            
        except Exception as e:
            print(f"  ❌ Multi-source mining error: {e}\n")
            return {'results': [], 'total': 0, 'by_source': {}, 'error': str(e)}

    def _ai_extract_subcontractor_info(self, title: str, snippet: str, url: str, service_type: str, location: str) -> Dict:
        """Use AI to extract structured company information from search result"""
        try:
            prompt = f"""Extract company information from this Google search result.

Title: {title}
Snippet: {snippet}
URL: {url}

Service Type: {service_type}
Location: {location}

Extract and return ONLY valid JSON (no other text):
{{
  "company_name": "Company name",
  "city": "City name",
  "state": "State abbreviation (e.g. VA, TX)",
  "phone": "Phone number if found, else empty string",
  "email": "Email if found, else empty string"
}}

Rules:
- Extract actual company name from title/snippet
- If no company name found, return null
- Keep phone/email empty string if not found
- Return ONLY the JSON, nothing else"""
            
            response = self.ai.complete(prompt, max_tokens=200)
            clean_response = response.strip()
            
            # Remove markdown code blocks if present
            if clean_response.startswith('```'):
                clean_response = re.sub(r'^```json\s*', '', clean_response)
                clean_response = re.sub(r'```\s*$', '', clean_response)
                clean_response = clean_response.strip()
            
            info = json.loads(clean_response)
            return info if info.get('company_name') else None
            
        except Exception as e:
            print(f"  ⚠️  AI extraction error: {e}")
            return None
    
    def search_existing_subcontractors(self, service_type: str = None, location: str = None, 
                                        min_rating: float = 0) -> List[Dict]:
        """
        Search existing subcontractor database
        
        Args:
            service_type: Filter by service type
            location: Filter by city or state
            min_rating: Minimum reliability rating
            
        Returns:
            List of matching subcontractor records
        """
        try:
            providers = self.airtable.get_all_records('GPSS SUBCONTRACTORS')
            
            filtered = []
            for provider in providers:
                fields = provider.get('fields', {})
                
                # Filter by service type
                if service_type:
                    provider_service = fields.get('SERVICE TYPE', '').lower()
                    if service_type.lower() not in provider_service:
                        continue
                
                # Filter by location
                if location:
                    city = fields.get('CITY', '').lower()
                    state = fields.get('STATE', '').lower()
                    location_lower = location.lower()
                    if location_lower not in city and location_lower not in state:
                        continue
                
                # Filter by rating
                rating = fields.get('RELIABILITY RATING', 0)
                if rating < min_rating:
                    continue
                
                filtered.append({
                    'id': provider.get('id'),
                    'company_name': fields.get('COMPANY NAME', ''),
                    'service_type': fields.get('SERVICE TYPE', ''),
                    'city': fields.get('CITY', ''),
                    'state': fields.get('STATE', ''),
                    'phone': fields.get('PHONE', ''),
                    'email': fields.get('EMAIL', ''),
                    'website': fields.get('WEBSITE', ''),
                    'reliability_rating': rating,
                    'response_rate': fields.get('RESPONSE RATE (%)', 0),
                    'relationship_status': fields.get('RELATIONSHIP STATUS', ''),
                    'contracts_won_together': fields.get('CONTRACTS WON TOGETHER', 0)
                })
            
            # Sort by reliability rating and contracts won together
            filtered.sort(key=lambda x: (x.get('contracts_won_together', 0), x.get('reliability_rating', 0)), reverse=True)
            
            return filtered
            
        except Exception as e:
            print(f"Error searching subcontractors: {e}")
            return []
    
    # ============================================
    # FUNCTION 2: GENERATE & SEND RFQs
    # ============================================
    
    def generate_rfq_email(self, subcontractor: Dict, opportunity: Dict, scope: str) -> Dict:
        """
        Generate personalized RFQ email for subcontractor in the area
        
        Args:
            subcontractor: Subcontractor record
            opportunity: Opportunity details
            scope: Scope of work description
            
        Returns:
            Dictionary with subject, body, and metadata
        """
        try:
            company_name = subcontractor.get('company_name', subcontractor.get('COMPANY NAME', 'Company'))
            service_type = opportunity.get('service_type', '')
            location = opportunity.get('location', '')
            contract_value = opportunity.get('value', 0)
            agency = opportunity.get('agency', 'Federal Agency')
            
            prompt = f"""Generate a professional RFQ (Request for Quote) email for a subcontractor in the area.

CONTEXT:
- We are Dee Davis Inc., a certified EDWOSB (Economically Disadvantaged Women-Owned Small Business)
- We're bidding on a federal contract
- We want to partner with subcontractors in the area who have local expertise
- This is a WIN-WIN: They get work, we manage the federal paperwork

SUBCONTRACTOR:
Company: {company_name}
Service: {service_type}
Location: {location}

OPPORTUNITY:
Agency: {agency}
Service Needed: {service_type}
Location: {location}
Est. Value: ${contract_value:,}

SCOPE OF WORK:
{scope}

Generate an email that:
1. Introduces Dee Davis Inc. (EDWOSB, CAGE: 8UMX3)
2. Explains the partnership opportunity (we prime, they execute)
3. Emphasizes their LOCAL ADVANTAGE (they know the area, have local equipment/staff)
4. Requests quote based on scope
5. Professional but friendly tone
6. Asks for response within 3-5 business days
7. Includes: pricing, timeline, capabilities, past similar work

Return as JSON:
{{
  "subject": "Federal Contract Partnership Opportunity - [Service] in [Location]",
  "body": "Email body text with proper paragraphs"
}}

Return ONLY valid JSON, no other text."""
            
            response = self.ai.complete(prompt, max_tokens=1500)
            clean_response = response.strip()
            
            # Remove markdown code blocks
            if clean_response.startswith('```'):
                clean_response = re.sub(r'^```json\s*', '', clean_response)
                clean_response = re.sub(r'```\s*$', '', clean_response)
                clean_response = clean_response.strip()
            
            email = json.loads(clean_response)
            
            return {
                'subject': email.get('subject', f'Federal Contract Quote Request - {service_type}'),
                'body': email.get('body', ''),
                'to_email': subcontractor.get('email', subcontractor.get('EMAIL', '')),
                'to_company': company_name,
                'opportunity_id': opportunity.get('id', '')
            }
            
        except Exception as e:
            print(f"Error generating RFQ email: {e}")
            # Fallback simple email
            return {
                'subject': f"Federal Contract Quote Request - {opportunity.get('service_type', 'Services')}",
                'body': f"We are requesting a quote for {opportunity.get('service_type', 'services')} for a federal contract in {opportunity.get('location', 'your area')}.",
                'to_email': subcontractor.get('email', subcontractor.get('EMAIL', '')),
                'to_company': subcontractor.get('company_name', subcontractor.get('COMPANY NAME', '')),
                'opportunity_id': opportunity.get('id', '')
            }
    
    def send_rfqs_to_subcontractors(self, opportunity_id: str, subcontractor_ids: List[str], scope: str) -> Dict:
        """
        Send RFQs to multiple subcontractors at once
        
        Args:
            opportunity_id: Airtable opportunity ID
            subcontractor_ids: List of subcontractor IDs to contact
            scope: Scope of work description
            
        Returns:
            Summary of emails sent
        """
        try:
            # Get opportunity details
            opportunity = self.airtable.get_record('Opportunities', opportunity_id)
            if not opportunity:
                return {'error': 'Opportunity not found'}
            
            opp_fields = opportunity.get('fields', {})
            
            # Build opportunity dict for email generation
            opp_data = {
                'id': opportunity_id,
                'service_type': opp_fields.get('SERVICE TYPE', ''),
                'location': opp_fields.get('LOCATION', ''),
                'value': opp_fields.get('Value', 0),
                'agency': opp_fields.get('Agency', 'Federal Agency')
            }
            
            emails_generated = []
            
            for subcontractor_id in subcontractor_ids:
                try:
                    # Get subcontractor details
                    subcontractor = self.airtable.get_record('GPSS SUBCONTRACTORS', subcontractor_id)
                    if not subcontractor:
                        continue
                    
                    subcontractor_fields = subcontractor.get('fields', {})
                    subcontractor_data = {
                        'company_name': subcontractor_fields.get('COMPANY NAME', ''),
                        'email': subcontractor_fields.get('EMAIL', ''),
                        'service_type': subcontractor_fields.get('SERVICE TYPE', '')
                    }
                    
                    # Generate email
                    email = self.generate_rfq_email(subcontractor_data, opp_data, scope)
                    
                    # Create quote request record in Airtable
                    quote_record = {
                        'OPPORTUNITY': [opportunity_id],
                        'SUBCONTRACTOR': [subcontractor_id],
                        'STATUS': 'RFQ Sent',
                        'RFQ SENT DATE': datetime.now().strftime('%Y-%m-%d'),
                        'QUOTE DUE DATE': (datetime.now() + timedelta(days=5)).strftime('%Y-%m-%d'),
                        'EMAIL SUBJECT': email['subject'],
                        'EMAIL BODY': email['body']
                    }
                    
                    quote_id = self.airtable.create_record('GPSS SUBCONTRACTOR QUOTES', quote_record)
                    
                    emails_generated.append({
                        'subcontractor': subcontractor_data['company_name'],
                        'email': email['to_email'],
                        'subject': email['subject'],
                        'quote_id': quote_id.get('id') if quote_id else None
                    })
                    
                    print(f"  ✓ RFQ generated for {subcontractor_data['company_name']}")
                    
                except Exception as e:
                    print(f"  ⚠️  Error processing subcontractor {subcontractor_id}: {e}")
                    continue
            
            print(f"\n  ✅ Generated {len(emails_generated)} RFQs")
            
            return {
                'success': True,
                'rfqs_generated': len(emails_generated),
                'emails': emails_generated,
                'message': f'Generated {len(emails_generated)} RFQs. Copy/paste emails to send manually or integrate with email service.'
            }
            
        except Exception as e:
            print(f"Error sending RFQs: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    # ============================================
    # FUNCTION 3: SCORE QUOTES (AI 0-100)
    # ============================================
    
    def score_quote(self, quote_id: str) -> Dict:
        """
        AI scores a subcontractor's quote response 0-100
        
        Scoring Criteria:
        - Price competitiveness (30 points)
        - Capabilities match (25 points)
        - Response quality/completeness (20 points)
        - Timeline feasibility (15 points)
        - Past experience indicators (10 points)
        
        Args:
            quote_id: Airtable quote record ID
            
        Returns:
            Score and detailed reasoning
        """
        try:
            # Get quote details
            quote = self.airtable.get_record('GPSS QUOTES', quote_id)
            if not quote:
                return {'error': 'Quote not found'}
            
            fields = quote.get('fields', {})
            
            # Extract quote details
            quote_amount = fields.get('QUOTE AMOUNT', 0)
            response_text = fields.get('RESPONSE TEXT', '')
            response_time_days = fields.get('RESPONSE TIME (DAYS)', 999)
            
            # Get opportunity for context
            opp_ids = fields.get('OPPORTUNITY', [])
            estimated_value = 0
            requirements = ''
            
            if opp_ids:
                opportunity = self.airtable.get_record('Opportunities', opp_ids[0])
                if opportunity:
                    opp_fields = opportunity.get('fields', {})
                    estimated_value = opp_fields.get('Value', 0)
                    requirements = opp_fields.get('Requirements', '')
            
            # Build AI scoring prompt
            prompt = f"""Score this quote response from a subcontractor in the area on a scale of 0-100.

SCORING CRITERIA (total 100 points):
1. Price Competitiveness (30 points)
   - Is the quote reasonable for the scope?
   - Estimated contract value: ${estimated_value:,}
   - Their quote: ${quote_amount:,}
   
2. Capabilities Match (25 points)
   - Do they address all requirements?
   - Show relevant experience?
   
3. Response Quality (20 points)
   - Complete and detailed?
   - Professional?
   - Includes timeline, deliverables?
   
4. Timeline Feasibility (15 points)
   - Can they meet deadlines?
   - Realistic schedule?
   
5. Experience Indicators (10 points)
   - Past similar work mentioned?
   - Certifications/credentials?

REQUIREMENTS:
{requirements}

THEIR RESPONSE:
{response_text}

Quote Amount: ${quote_amount:,}
Response Time: {response_time_days} days

Return as JSON:
{{
  "score": 85,
  "price_score": 28,
  "capabilities_score": 22,
  "quality_score": 18,
  "timeline_score": 12,
  "experience_score": 5,
  "reasoning": "Detailed explanation of score",
  "strengths": ["strength 1", "strength 2"],
  "concerns": ["concern 1", "concern 2"],
  "recommendation": "Recommend/Consider/Pass"
}}

Return ONLY valid JSON."""
            
            response = self.ai.complete(prompt, max_tokens=1000)
            clean_response = response.strip()
            
            # Remove markdown
            if clean_response.startswith('```'):
                clean_response = re.sub(r'^```json\s*', '', clean_response)
                clean_response = re.sub(r'```\s*$', '', clean_response)
                clean_response = clean_response.strip()
            
            score_data = json.loads(clean_response)
            
            # Update quote record with score
            self.airtable.update_record('GPSS SUBCONTRACTOR QUOTES', quote_id, {
                'AI SCORE': score_data.get('score', 0),
                'SCORE REASONING': score_data.get('reasoning', ''),
                'RECOMMENDATION': score_data.get('recommendation', 'Consider')
            })
            
            print(f"  ✓ Quote scored: {score_data.get('score')}/100 - {score_data.get('recommendation')}")
            
            return {
                'success': True,
                'quote_id': quote_id,
                **score_data
            }
            
        except Exception as e:
            print(f"Error scoring quote: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def score_all_quotes_for_opportunity(self, opportunity_id: str) -> List[Dict]:
        """
        Score all quotes for an opportunity and return ranked list
        
        Args:
            opportunity_id: Opportunity ID
            
        Returns:
            List of quotes sorted by score (highest first)
        """
        try:
            # Get all quotes for this opportunity
            quotes = self.airtable.get_all_records('GPSS SUBCONTRACTOR QUOTES')
            
            opportunity_quotes = []
            for quote in quotes:
                fields = quote.get('fields', {})
                opp_ids = fields.get('OPPORTUNITY', [])
                
                if opportunity_id in opp_ids:
                    opportunity_quotes.append({
                        'id': quote.get('id'),
                        'fields': fields
                    })
            
            if not opportunity_quotes:
                return []
            
            print(f"📊 Scoring {len(opportunity_quotes)} quotes...")
            
            scored_quotes = []
            for quote in opportunity_quotes:
                # Check if already scored
                if not quote['fields'].get('AI SCORE'):
                    # Score it
                    score_result = self.score_quote(quote['id'])
                    if score_result.get('success'):
                        scored_quotes.append({
                            'quote_id': quote['id'],
                            'provider': quote['fields'].get('PROVIDER', ['Unknown'])[0],
                            'quote_amount': quote['fields'].get('QUOTE AMOUNT', 0),
                            'score': score_result.get('score', 0),
                            'recommendation': score_result.get('recommendation', ''),
                            'reasoning': score_result.get('reasoning', '')
                        })
                else:
                    # Already scored
                    scored_quotes.append({
                        'quote_id': quote['id'],
                        'provider': quote['fields'].get('PROVIDER', ['Unknown'])[0],
                        'quote_amount': quote['fields'].get('QUOTE AMOUNT', 0),
                        'score': quote['fields'].get('AI SCORE', 0),
                        'recommendation': quote['fields'].get('RECOMMENDATION', ''),
                        'reasoning': quote['fields'].get('SCORE REASONING', '')
                    })
            
            # Sort by score descending
            scored_quotes.sort(key=lambda x: x.get('score', 0), reverse=True)
            
            print(f"  ✅ Quotes ranked. Top score: {scored_quotes[0].get('score')}/100")
            
            return scored_quotes
            
        except Exception as e:
            print(f"Error scoring quotes: {e}")
            return []
    
    # ============================================
    # FUNCTION 4: CALCULATE MARKUP & FINAL BID
    # ============================================
    
    def calculate_markup_bid(self, quote_id: str, markup_percentage: float = 20.0) -> Dict:
        """
        Calculate final bid amount with markup
        
        Args:
            quote_id: Selected quote ID
            markup_percentage: Your markup % (default 20%)
            
        Returns:
            Bid calculation details
        """
        try:
            # Get quote details
            quote = self.airtable.get_record('GPSS SUBCONTRACTOR QUOTES', quote_id)
            if not quote:
                return {'error': 'Quote not found'}
            
            fields = quote.get('fields', {})
            
            subcontractor_cost = fields.get('QUOTE AMOUNT', 0)
            
            # Calculate markup
            markup_amount = subcontractor_cost * (markup_percentage / 100)
            final_bid = subcontractor_cost + markup_amount
            
            # Calculate profit margin if we have estimated costs
            your_overhead = final_bid * 0.10  # Assume 10% overhead for PM/admin
            net_profit = markup_amount - your_overhead
            profit_margin_pct = (net_profit / final_bid * 100) if final_bid > 0 else 0
            
            calculation = {
                'subcontractor_cost': subcontractor_cost,
                'markup_percentage': markup_percentage,
                'markup_amount': markup_amount,
                'your_overhead_estimate': your_overhead,
                'net_profit_estimate': net_profit,
                'profit_margin_percentage': round(profit_margin_pct, 1),
                'final_bid_amount': final_bid
            }
            
            # Update quote record with bid calculation
            self.airtable.update_record('GPSS SUBCONTRACTOR QUOTES', quote_id, {
                'SELECTED': True,
                'MARKUP PERCENTAGE': markup_percentage,
                'MARKUP AMOUNT': markup_amount,
                'FINAL BID AMOUNT': final_bid,
                'ESTIMATED PROFIT': net_profit
            })
            
            print(f"\n💰 BID CALCULATION:")
            print(f"  Subcontractor Cost: ${subcontractor_cost:,.2f}")
            print(f"  Your Markup ({markup_percentage}%): ${markup_amount:,.2f}")
            print(f"  Final Bid: ${final_bid:,.2f}")
            print(f"  Estimated Profit: ${net_profit:,.2f} ({profit_margin_pct:.1f}% margin)\n")
            
            return {
                'success': True,
                'quote_id': quote_id,
                **calculation
            }
            
        except Exception as e:
            print(f"Error calculating markup: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def generate_final_bid_summary(self, opportunity_id: str, selected_quote_id: str, markup_percentage: float = 20.0) -> Dict:
        """
        Generate complete bid package summary
        
        Args:
            opportunity_id: Opportunity ID
            selected_quote_id: Selected quote ID
            markup_percentage: Your markup %
            
        Returns:
            Complete bid summary ready for proposal
        """
        try:
            # Calculate markup
            bid_calc = self.calculate_markup_bid(selected_quote_id, markup_percentage)
            
            if not bid_calc.get('success'):
                return bid_calc
            
            # Get opportunity details
            opportunity = self.airtable.get_record('Opportunities', opportunity_id)
            opp_fields = opportunity.get('fields', {}) if opportunity else {}
            
            # Get quote details
            quote = self.airtable.get_record('GPSS SUBCONTRACTOR QUOTES', selected_quote_id)
            quote_fields = quote.get('fields', {}) if quote else {}
            
            # Get subcontractor details
            subcontractor_ids = quote_fields.get('SUBCONTRACTOR', [])
            subcontractor = None
            if subcontractor_ids:
                subcontractor = self.airtable.get_record('GPSS SUBCONTRACTORS', subcontractor_ids[0])
            
            subcontractor_fields = subcontractor.get('fields', {}) if subcontractor else {}
            
            summary = {
                'opportunity_name': opp_fields.get('Opportunity Name', ''),
                'agency': opp_fields.get('Agency', ''),
                'location': opp_fields.get('LOCATION', ''),
                'service_type': opp_fields.get('SERVICE TYPE', ''),
                'selected_subcontractor': subcontractor_fields.get('COMPANY NAME', ''),
                'subcontractor_location': f"{subcontractor_fields.get('CITY', '')}, {subcontractor_fields.get('STATE', '')}",
                'subcontractor_quote': bid_calc['subcontractor_cost'],
                'your_markup': bid_calc['markup_amount'],
                'final_bid': bid_calc['final_bid_amount'],
                'estimated_profit': bid_calc['net_profit_estimate'],
                'profit_margin_pct': bid_calc['profit_margin_percentage']
            }
            
            print(f"\n📋 FINAL BID SUMMARY")
            print(f"="*60)
            print(f"Opportunity: {summary['opportunity_name']}")
            print(f"Agency: {summary['agency']}")
            print(f"Location: {summary['location']}")
            print(f"\nSELECTED SUBCONTRACTOR:")
            print(f"  Company: {summary['selected_subcontractor']}")
            print(f"  Location: {summary['subcontractor_location']}")
            print(f"\nPRICING:")
            print(f"  Subcontractor Cost: ${summary['subcontractor_quote']:,.2f}")
            print(f"  Your Markup: ${summary['your_markup']:,.2f}")
            print(f"  FINAL BID: ${summary['final_bid']:,.2f}")
            print(f"\nPROFIT:")
            print(f"  Estimated Profit: ${summary['estimated_profit']:,.2f}")
            print(f"  Profit Margin: {summary['profit_margin_pct']:.1f}%")
            print(f"="*60 + "\n")
            
            return {
                'success': True,
                **summary
            }
            
        except Exception as e:
            print(f"Error generating bid summary: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    # ============================================
    # COMPLIANCE DOCUMENT TRACKING
    # ============================================
    
    def check_compliance(self, subcontractor_id: str, required_docs: List[str] = None) -> Dict:
        """
        Check if subcontractor has all required compliance documents
        
        Args:
            subcontractor_id: Airtable record ID
            required_docs: List of required document types (defaults to essential docs)
            
        Returns:
            Compliance status with details
        """
        try:
            # Default required documents
            if required_docs is None:
                required_docs = [
                    'W-9',
                    'General Liability Insurance',
                    'Subcontractor Agreement'
                ]
            
            # Get subcontractor info
            subcontractor = self.airtable.get_record('GPSS SUBCONTRACTORS', subcontractor_id)
            if not subcontractor:
                return {
                    'success': False,
                    'error': 'Subcontractor not found'
                }
            
            sub_fields = subcontractor.get('fields', {})
            company_name = sub_fields.get('COMPANY NAME', 'Unknown')
            
            # Get all compliance documents for this subcontractor
            all_compliance = self.airtable.get_all_records('GPSS SUBCONTRACTOR COMPLIANCE')
            
            # Filter to this subcontractor's documents
            sub_docs = []
            for doc in all_compliance:
                fields = doc.get('fields', {})
                linked_subs = fields.get('SUBCONTRACTOR', [])
                if subcontractor_id in linked_subs:
                    sub_docs.append({
                        'id': doc['id'],
                        'type': fields.get('DOCUMENT_TYPE', ''),
                        'status': fields.get('DOCUMENT_STATUS', ''),
                        'expiration': fields.get('EXPIRATION_DATE', ''),
                        'days_until_expiration': fields.get('DAYS_UNTIL_EXPIRATION', ''),
                        'alert_status': fields.get('ALERT_STATUS', '')
                    })
            
            # Check each required document
            compliance_issues = []
            approved_docs = []
            expiring_docs = []
            expired_docs = []
            
            for required_doc in required_docs:
                # Find this document type
                doc_found = None
                for doc in sub_docs:
                    if doc['type'] == required_doc:
                        doc_found = doc
                        break
                
                if not doc_found:
                    compliance_issues.append(f"Missing: {required_doc}")
                elif doc_found['status'] != 'Approved':
                    compliance_issues.append(f"{required_doc}: Status = {doc_found['status']}")
                elif '⚠️ EXPIRED' in str(doc_found.get('alert_status', '')):
                    expired_docs.append(required_doc)
                    compliance_issues.append(f"{required_doc}: EXPIRED")
                elif '⏰ Expiring Soon' in str(doc_found.get('alert_status', '')):
                    expiring_docs.append(required_doc)
                    # Don't block, but warn
                else:
                    approved_docs.append(required_doc)
            
            # Overall compliance status
            is_compliant = len(compliance_issues) == 0
            
            result = {
                'success': True,
                'subcontractor_id': subcontractor_id,
                'company_name': company_name,
                'compliant': is_compliant,
                'required_documents': required_docs,
                'approved_documents': approved_docs,
                'compliance_issues': compliance_issues,
                'expiring_soon': expiring_docs,
                'expired_documents': expired_docs,
                'total_documents_tracked': len(sub_docs),
                'compliance_percentage': int((len(approved_docs) / len(required_docs)) * 100) if required_docs else 0
            }
            
            print(f"\n🔒 COMPLIANCE CHECK: {company_name}")
            print(f"="*60)
            print(f"Status: {'✅ COMPLIANT' if is_compliant else '❌ NON-COMPLIANT'}")
            print(f"Compliance: {result['compliance_percentage']}% ({len(approved_docs)}/{len(required_docs)} docs)")
            
            if approved_docs:
                print(f"\n✅ Approved Documents:")
                for doc in approved_docs:
                    print(f"  • {doc}")
            
            if expiring_docs:
                print(f"\n⏰ Expiring Soon (30 days):")
                for doc in expiring_docs:
                    print(f"  • {doc}")
            
            if compliance_issues:
                print(f"\n❌ Issues:")
                for issue in compliance_issues:
                    print(f"  • {issue}")
            
            print(f"="*60 + "\n")
            
            return result
            
        except Exception as e:
            print(f"Error checking compliance: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_compliance_documents(self, subcontractor_id: str) -> Dict:
        """
        Get all compliance documents for a subcontractor
        
        Args:
            subcontractor_id: Airtable record ID
            
        Returns:
            List of all compliance documents
        """
        try:
            # Get all compliance documents
            all_compliance = self.airtable.get_all_records('GPSS SUBCONTRACTOR COMPLIANCE')
            
            # Filter to this subcontractor
            sub_docs = []
            for doc in all_compliance:
                fields = doc.get('fields', {})
                linked_subs = fields.get('SUBCONTRACTOR', [])
                if subcontractor_id in linked_subs:
                    sub_docs.append({
                        'id': doc['id'],
                        'document_type': fields.get('DOCUMENT_TYPE', ''),
                        'status': fields.get('DOCUMENT_STATUS', ''),
                        'date_received': fields.get('DATE_RECEIVED', ''),
                        'date_approved': fields.get('DATE_APPROVED', ''),
                        'expiration_date': fields.get('EXPIRATION_DATE', ''),
                        'days_until_expiration': fields.get('DAYS_UNTIL_EXPIRATION', ''),
                        'alert_status': fields.get('ALERT_STATUS', ''),
                        'insurance_amount': fields.get('INSURANCE_AMOUNT', 0),
                        'policy_number': fields.get('POLICY_NUMBER', ''),
                        'notes': fields.get('NOTES', '')
                    })
            
            return {
                'success': True,
                'subcontractor_id': subcontractor_id,
                'documents_found': len(sub_docs),
                'documents': sub_docs
            }
            
        except Exception as e:
            print(f"Error getting compliance documents: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def add_compliance_document(self, subcontractor_id: str, document_type: str, 
                               status: str = 'Missing', expiration_date: str = None,
                               insurance_amount: float = None, notes: str = '') -> Dict:
        """
        Add a compliance document record
        
        Args:
            subcontractor_id: Airtable record ID
            document_type: Type of document (W-9, Insurance, etc.)
            status: Document status (default: Missing)
            expiration_date: Expiration date (YYYY-MM-DD format)
            insurance_amount: Coverage amount for insurance docs
            notes: Additional notes
            
        Returns:
            Created document record
        """
        try:
            # Create compliance record
            record_data = {
                'SUBCONTRACTOR': [subcontractor_id],
                'DOCUMENT_TYPE': document_type,
                'DOCUMENT_STATUS': status,
                'NOTES': notes
            }
            
            if expiration_date:
                record_data['EXPIRATION_DATE'] = expiration_date
            
            if insurance_amount:
                record_data['INSURANCE_AMOUNT'] = insurance_amount
            
            # Create record
            record_id = self.airtable.create_record('GPSS SUBCONTRACTOR COMPLIANCE', record_data)
            
            print(f"✅ Added compliance document: {document_type} (Status: {status})")
            
            return {
                'success': True,
                'record_id': record_id,
                'document_type': document_type,
                'status': status
            }
            
        except Exception as e:
            print(f"Error adding compliance document: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def update_compliance_document(self, document_id: str, updates: Dict) -> Dict:
        """
        Update a compliance document record
        
        Args:
            document_id: Compliance document record ID
            updates: Dictionary of fields to update
            
        Returns:
            Update status
        """
        try:
            # Update record
            self.airtable.update_record('GPSS SUBCONTRACTOR COMPLIANCE', document_id, updates)
            
            print(f"✅ Updated compliance document: {document_id}")
            
            return {
                'success': True,
                'document_id': document_id,
                'updated_fields': list(updates.keys())
            }
            
        except Exception as e:
            print(f"Error updating compliance document: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_expiring_documents(self, days_threshold: int = 30) -> Dict:
        """
        Get all documents expiring within threshold
        
        Args:
            days_threshold: Alert for docs expiring in this many days (default 30)
            
        Returns:
            List of expiring/expired documents
        """
        try:
            # Get all compliance documents
            all_compliance = self.airtable.get_all_records('GPSS SUBCONTRACTOR COMPLIANCE')
            
            expiring_soon = []
            expired = []
            
            for doc in all_compliance:
                fields = doc.get('fields', {})
                days_until = fields.get('DAYS_UNTIL_EXPIRATION', '')
                alert_status = fields.get('ALERT_STATUS', '')
                
                # Check if expiring or expired
                if '⚠️ EXPIRED' in str(alert_status):
                    expired.append({
                        'id': doc['id'],
                        'subcontractor': fields.get('SUBCONTRACTOR', []),
                        'document_type': fields.get('DOCUMENT_TYPE', ''),
                        'expiration_date': fields.get('EXPIRATION_DATE', ''),
                        'days_overdue': abs(int(days_until)) if days_until != 'No Expiration' else 0,
                        'alert': 'EXPIRED'
                    })
                elif '⏰ Expiring Soon' in str(alert_status):
                    expiring_soon.append({
                        'id': doc['id'],
                        'subcontractor': fields.get('SUBCONTRACTOR', []),
                        'document_type': fields.get('DOCUMENT_TYPE', ''),
                        'expiration_date': fields.get('EXPIRATION_DATE', ''),
                        'days_until_expiration': int(days_until) if days_until != 'No Expiration' else 999,
                        'alert': 'EXPIRING_SOON'
                    })
            
            print(f"\n⚠️ COMPLIANCE ALERTS")
            print(f"="*60)
            print(f"Expired Documents: {len(expired)}")
            print(f"Expiring Soon (30 days): {len(expiring_soon)}")
            print(f"="*60 + "\n")
            
            return {
                'success': True,
                'expired_count': len(expired),
                'expiring_soon_count': len(expiring_soon),
                'expired_documents': expired,
                'expiring_soon_documents': expiring_soon,
                'total_alerts': len(expired) + len(expiring_soon)
            }
            
        except Exception as e:
            print(f"Error getting expiring documents: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def mark_subcontractor_compliance_ready(self, subcontractor_id: str, ready: bool = True) -> Dict:
        """
        Mark subcontractor as compliance ready (or not)
        
        Args:
            subcontractor_id: Airtable record ID
            ready: TRUE if compliant, FALSE if not
            
        Returns:
            Update status
        """
        try:
            # Update COMPLIANCE_READY field
            self.airtable.update_record('GPSS SUBCONTRACTORS', subcontractor_id, {
                'COMPLIANCE_READY': ready,
                'LAST_COMPLIANCE_CHECK': datetime.now().strftime('%Y-%m-%d')
            })
            
            status = "✅ COMPLIANCE READY" if ready else "❌ NOT COMPLIANCE READY"
            print(f"{status}: Subcontractor {subcontractor_id}")
            
            return {
                'success': True,
                'subcontractor_id': subcontractor_id,
                'compliance_ready': ready
            }
            
        except Exception as e:
            print(f"Error updating compliance status: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    # ============================================
    # DOCUMENT GENERATORS (NDA, Teaming, Emails)
    # ============================================
    
    def generate_nda(self, subcontractor_id: str, opportunity_id: str = None) -> Dict:
        """
        Auto-generate a pre-filled NDA for a subcontractor/teaming partner.
        
        Triggered by:
        - Workflow advance to 'Teaming' status
        - Manual request from SubcontractorMiner
        - Compliance check showing missing NDA
        
        Args:
            subcontractor_id: Airtable record ID for the partner
            opportunity_id: Optional opportunity this NDA relates to
            
        Returns:
            Generated NDA content + compliance record created
        """
        try:
            # 1. Pull subcontractor data from Airtable
            sub = self.airtable.get_record('GPSS SUBCONTRACTORS', subcontractor_id)
            if not sub:
                return {'success': False, 'error': 'Subcontractor not found'}
            
            sub_fields = sub.get('fields', {})
            company_name = sub_fields.get('COMPANY NAME', '')
            contact_name = sub_fields.get('CONTACT NAME', sub_fields.get('PRIMARY CONTACT', ''))
            contact_title = sub_fields.get('CONTACT TITLE', 'Authorized Representative')
            contact_email = sub_fields.get('EMAIL', '')
            contact_phone = sub_fields.get('PHONE', '')
            cage_code = sub_fields.get('CAGE CODE', '')
            uei = sub_fields.get('UEI', '')
            address = f"{sub_fields.get('CITY', '')}, {sub_fields.get('STATE', '')}"
            
            # 2. Get opportunity context if provided
            opp_context = ''
            if opportunity_id:
                opp = self.airtable.get_record('GPSS Opportunities', opportunity_id)
                if opp:
                    opp_fields = opp.get('fields', {})
                    opp_context = f"regarding potential teaming for {opp_fields.get('Name', 'a government contract opportunity')}"
            
            today = datetime.now().strftime('%B %d, %Y')
            expiration_date = (datetime.now() + timedelta(days=730)).strftime('%Y-%m-%d')
            
            # 3. Generate pre-filled NDA
            nda_content = f"""MUTUAL NON-DISCLOSURE AGREEMENT

Effective Date: {today}

BETWEEN:

PARTY A:
Dee Davis Inc.
Troy, Michigan
CAGE Code: 8UMX3 | UEI: HJB4KNYJVGZ1
Contact: Dieasha Davis, President

PARTY B:
{company_name}
{address}
{'CAGE Code: ' + cage_code if cage_code else ''}{'| UEI: ' + uei if uei else ''}
Contact: {contact_name}, {contact_title}
Email: {contact_email}
Phone: {contact_phone}

1. PURPOSE
The Parties are entering into discussions {opp_context} for the purpose of pursuing government contract opportunities. This Agreement governs the protection of confidential information exchanged during these discussions.

2. DEFINITION OF CONFIDENTIAL INFORMATION
"Confidential Information" means any non-public information disclosed by either Party including: pricing strategies, cost structures, supplier relationships, proposal content, technical approaches, past performance data, financial information, and government contract intelligence.

3. EXCLUSIONS
Information that: (a) is publicly available, (b) was already known, (c) is independently developed, (d) is received from third party without restriction, or (e) required by law to disclose.

4. OBLIGATIONS
Each Party agrees to: protect information with reasonable care, limit access to need-to-know personnel, not disclose to third parties, not use for any purpose other than the teaming discussions.

5. GOVCON-SPECIFIC PROTECTIONS
(a) NO END-RUN: Neither Party shall independently pursue opportunities identified through this relationship.
(b) NO SUPPLIER POACHING: Neither Party shall contact the other's suppliers or subcontractors to bypass the Disclosing Party.
(c) NO CLIENT DISCLOSURE: Neither Party shall reveal government end-client identities to vendors.
(d) PROPOSAL INTEGRITY: Shared proposal content shall not be reused without written consent.

6. TERM
Effective for two (2) years. Confidentiality obligations survive for three (3) years after termination.

7. REMEDIES
Breach may entitle Disclosing Party to injunctive relief plus attorneys' fees.

8. GENERAL
Governed by Michigan law. No obligation to proceed with any business arrangement. Electronic signatures valid.

SIGNATURES:

PARTY A — DEE DAVIS INC.
Signature: _______________________________
Name: Dieasha Davis
Title: President
Date: _______________

PARTY B — {company_name.upper()}
Signature: _______________________________
Name: {contact_name}
Title: {contact_title}
Date: _______________"""

            # 4. Create compliance tracking record
            compliance_result = self.add_compliance_document(
                subcontractor_id=subcontractor_id,
                document_type='NDA',
                status='Generated',
                expiration_date=expiration_date,
                notes=f"Auto-generated {today}. {opp_context}"
            )
            
            print(f"📄 NDA Generated for {company_name}")
            
            return {
                'success': True,
                'document_type': 'NDA',
                'subcontractor': company_name,
                'content': nda_content,
                'compliance_record_id': compliance_result.get('record_id'),
                'expiration_date': expiration_date,
                'next_step': 'Send for signature via DocuSign/Adobe Sign/Rocket Lawyer'
            }
            
        except Exception as e:
            print(f"Error generating NDA: {e}")
            return {'success': False, 'error': str(e)}
    
    def generate_teaming_agreement(self, subcontractor_id: str, opportunity_id: str,
                                     workshare_prime: int = 55, workshare_sub: int = 45,
                                     prime_tasks: List[str] = None, sub_tasks: List[str] = None) -> Dict:
        """
        Auto-generate a pre-filled Teaming Agreement for a subcontractor.
        
        Triggered by:
        - Workflow advance to 'Generate Proposal' when subcontractors are linked
        - After NDA is signed and workshare is agreed
        - Manual request
        
        Args:
            subcontractor_id: Airtable record ID
            opportunity_id: Opportunity this agreement covers
            workshare_prime: Prime contractor workshare % (default 55)
            workshare_sub: Sub workshare % (default 45)
            prime_tasks: List of prime's tasks
            sub_tasks: List of sub's tasks
            
        Returns:
            Generated Teaming Agreement content + compliance record
        """
        try:
            # 1. Pull all data from Airtable
            sub = self.airtable.get_record('GPSS SUBCONTRACTORS', subcontractor_id)
            opp = self.airtable.get_record('GPSS Opportunities', opportunity_id)
            
            if not sub:
                return {'success': False, 'error': 'Subcontractor not found'}
            if not opp:
                return {'success': False, 'error': 'Opportunity not found'}
            
            sub_fields = sub.get('fields', {})
            opp_fields = opp.get('fields', {})
            
            company_name = sub_fields.get('COMPANY NAME', '')
            contact_name = sub_fields.get('CONTACT NAME', sub_fields.get('PRIMARY CONTACT', ''))
            contact_title = sub_fields.get('CONTACT TITLE', 'Authorized Representative')
            cage_code = sub_fields.get('CAGE CODE', '')
            uei = sub_fields.get('UEI', '')
            sub_certs = sub_fields.get('CERTIFICATIONS', sub_fields.get('SOCIOECONOMIC STATUS', ''))
            address = f"{sub_fields.get('CITY', '')}, {sub_fields.get('STATE', '')}"
            
            opp_name = opp_fields.get('Name', opp_fields.get('Opportunity Name', ''))
            rfp_number = opp_fields.get('RFP NUMBER', opp_fields.get('Solicitation Number', ''))
            agency = opp_fields.get('AGENCY NAME', opp_fields.get('Agency', ''))
            naics = opp_fields.get('NAISC Codes', opp_fields.get('NAICS', ''))
            est_value = opp_fields.get('Value', opp_fields.get('Estimated Value', 'TBD'))
            deadline = opp_fields.get('Deadline', 'TBD')
            
            today = datetime.now().strftime('%B %d, %Y')
            agreement_number = f"DDI-TA-{datetime.now().strftime('%Y')}-{subcontractor_id[-3:]}"
            
            # Default tasks
            if not prime_tasks:
                prime_tasks = [
                    'Program/Project Management',
                    'Contract administration and compliance',
                    'Client relationship management',
                    'Quality assurance and oversight',
                    'Reporting and documentation'
                ]
            
            if not sub_tasks:
                sub_tasks = [f'Specialized services per SOW for {opp_name}']
            
            prime_tasks_str = '\n'.join([f'  - {t}' for t in prime_tasks])
            sub_tasks_str = '\n'.join([f'  - {t}' for t in sub_tasks])
            
            # 2. Generate the agreement
            agreement_content = f"""TEAMING AGREEMENT

Agreement Number: {agreement_number}
Effective Date: {today}

PARTIES:

PARTY A (Prime Contractor):
Dee Davis Inc.
Troy, Michigan
CAGE Code: 8UMX3 | UEI: HJB4KNYJVGZ1
EDWOSB / WOSB Certified
Contact: Dieasha Davis, President

PARTY B (Team Member / Subcontractor):
{company_name}
{address}
{'CAGE Code: ' + cage_code if cage_code else ''}{'| UEI: ' + uei if uei else ''}
Socioeconomic Status: {sub_certs}
Contact: {contact_name}, {contact_title}

OPPORTUNITY:
Description: {opp_name}
Solicitation: {rfp_number if rfp_number else 'Pending'}
Agency: {agency}
NAICS: {naics}
Estimated Value: {'${:,.0f}'.format(est_value) if isinstance(est_value, (int, float)) else est_value}
Deadline: {deadline}

ARTICLE 1: PURPOSE
Party A shall serve as Prime Contractor. Party B shall serve as subcontractor/team member for the Opportunity described above.

ARTICLE 2: WORKSHARE
Party A (Dee Davis Inc.) — {workshare_prime}% of contract value:
{prime_tasks_str}

Party B ({company_name}) — {workshare_sub}% of contract value:
{sub_tasks_str}

Compliance: Party A shall perform at least 50% of contract value per FAR 52.219-14.

ARTICLE 3: PROPOSAL PREPARATION
Party A leads proposal effort. Party B provides: technical content, past performance references, key personnel resumes, and pricing within 5 business days of request.
Each Party bears its own proposal preparation costs.

ARTICLE 4: PRICING
Party B provides firm pricing for workshare within 5 business days of final solicitation.
Pricing is confidential and not disclosed to third parties.

ARTICLE 5: SUBCONTRACT (IF AWARDED)
Parties execute formal subcontract within 30 days of award with all required FAR/DFARS flow-downs.
Payment: Party A pays Party B within 15 days of receiving government payment, or Net 30.

ARTICLE 6: EXCLUSIVITY
During this Agreement, Party B shall not pursue this Opportunity independently or with another team.

ARTICLE 7: CONFIDENTIALITY
All exchanged information is confidential. No disclosure of government end-clients to vendors. No supplier poaching. No end-runs.

ARTICLE 8: INTELLECTUAL PROPERTY
Each Party retains pre-existing IP. Joint proposal content is jointly owned.

ARTICLE 9: TERM
Effective until: contract award and subcontract execution, solicitation cancellation, mutual termination, or 18 months — whichever first. Confidentiality survives 3 years.

ARTICLE 10: REPRESENTATIONS
Each Party: has authority to enter agreement, is not debarred/suspended, SAM.gov active, no conflicts of interest.

ARTICLE 11: DISPUTES
Direct negotiation first, then mediation. Governed by Michigan law.

ARTICLE 12: GENERAL
No joint venture or partnership created. Independent contractors. Electronic signatures valid.

SIGNATURES:

PARTY A — DEE DAVIS INC.
Signature: _______________________________
Name: Dieasha Davis
Title: President
Date: _______________

PARTY B — {company_name.upper()}
Signature: _______________________________
Name: {contact_name}
Title: {contact_title}
Date: _______________"""

            # 3. Create compliance tracking record
            compliance_result = self.add_compliance_document(
                subcontractor_id=subcontractor_id,
                document_type='Teaming Agreement',
                status='Generated',
                notes=f"Auto-generated {today} for {opp_name} ({rfp_number}). Workshare: {workshare_prime}/{workshare_sub}."
            )
            
            print(f"🤝 Teaming Agreement Generated: {company_name} for {opp_name}")
            
            return {
                'success': True,
                'document_type': 'Teaming Agreement',
                'agreement_number': agreement_number,
                'subcontractor': company_name,
                'opportunity': opp_name,
                'workshare': f"{workshare_prime}% prime / {workshare_sub}% sub",
                'content': agreement_content,
                'compliance_record_id': compliance_result.get('record_id'),
                'next_step': 'Review terms with partner, then send for signature'
            }
            
        except Exception as e:
            print(f"Error generating teaming agreement: {e}")
            return {'success': False, 'error': str(e)}
    
    def generate_govcon_email(self, email_type: str, opportunity_id: str = None,
                               subcontractor_id: str = None, contact_id: str = None,
                               custom_context: str = '') -> Dict:
        """
        Auto-generate context-aware GovCon emails by pulling real data from Airtable.
        
        Triggered by:
        - Workflow stage changes (CO outreach, debrief requests, etc.)
        - Subcontractor relationship changes (teaming outreach)
        - Manual request from any system
        
        Args:
            email_type: One of: 'sb_office_intro', 'co_sources_sought', 'co_presolicitation',
                       'co_question', 'capstat_intro', 'capstat_to_prime', 'debrief_formal',
                       'debrief_informal', 'debrief_thanks', 'sub_outreach', 'prime_outreach',
                       'teaming_followup'
            opportunity_id: Airtable opportunity ID (for context)
            subcontractor_id: Airtable subcontractor ID (for teaming emails)
            contact_id: Airtable contact ID (for CO/buyer emails)
            custom_context: Additional context for AI generation
            
        Returns:
            Generated email with subject, body, metadata
        """
        try:
            # 1. Pull context data from Airtable
            opp_data = {}
            sub_data = {}
            contact_data = {}
            
            if opportunity_id:
                opp = self.airtable.get_record('GPSS Opportunities', opportunity_id)
                if opp:
                    f = opp.get('fields', {})
                    opp_data = {
                        'name': f.get('Name', f.get('Opportunity Name', '')),
                        'rfp_number': f.get('RFP NUMBER', ''),
                        'agency': f.get('AGENCY NAME', f.get('Agency', '')),
                        'naics': f.get('NAISC Codes', ''),
                        'set_aside': f.get('Set-Aside Type', ''),
                        'deadline': f.get('Deadline', ''),
                        'value': f.get('Value', ''),
                        'state': f.get('State', ''),
                        'location': f.get('LOCATION', f.get('Performance Location', '')),
                        'scope': f.get('Notes', '')[:300]
                    }
            
            if subcontractor_id:
                sub = self.airtable.get_record('GPSS SUBCONTRACTORS', subcontractor_id)
                if sub:
                    f = sub.get('fields', {})
                    sub_data = {
                        'company': f.get('COMPANY NAME', ''),
                        'contact': f.get('CONTACT NAME', f.get('PRIMARY CONTACT', '')),
                        'email': f.get('EMAIL', ''),
                        'city': f.get('CITY', ''),
                        'state': f.get('STATE', ''),
                        'service_type': f.get('SERVICE TYPE', '')
                    }
            
            if contact_id:
                contact = self.airtable.get_record('GPSS Contacts', contact_id)
                if contact:
                    f = contact.get('fields', {})
                    contact_data = {
                        'name': f.get('Name', ''),
                        'email': f.get('Email', ''),
                        'title': f.get('Title', ''),
                        'organization': f.get('Organization', ''),
                        'role': f.get('Role Category', '')
                    }
            
            # 2. Build AI prompt based on email type
            email_configs = {
                'sb_office_intro': {
                    'description': 'Introduction to agency Small Business Office',
                    'tone': 'warm, professional, relationship-building',
                    'key_info': 'EDWOSB cert, NAICS codes, what we do, ask about upcoming opportunities'
                },
                'co_sources_sought': {
                    'description': 'Response to Sources Sought notice',
                    'tone': 'direct, capability-focused, concise',
                    'key_info': 'Match our capabilities to their requirements, include CAGE/UEI'
                },
                'co_presolicitation': {
                    'description': 'Inquiry about forecasted/upcoming opportunity',
                    'tone': 'professional, interested, asking smart questions',
                    'key_info': 'Ask timeline, set-aside status, industry days, draft SOW'
                },
                'co_question': {
                    'description': 'Question during open solicitation period',
                    'tone': 'specific, brief, reference exact section',
                    'key_info': 'Reference solicitation number and specific section'
                },
                'capstat_intro': {
                    'description': 'Capability statement introduction to agency',
                    'tone': 'warm, confident, frame relevance to their agency',
                    'key_info': 'Why we match their needs, NAICS alignment, certifications'
                },
                'capstat_to_prime': {
                    'description': 'Capability statement to prime contractor for teaming',
                    'tone': 'value-focused, EDWOSB advantage to their SB plan',
                    'key_info': 'How EDWOSB status helps them, our capabilities'
                },
                'debrief_formal': {
                    'description': 'Post-award debrief request per FAR 15.506',
                    'tone': 'professional, direct, citing right to debrief',
                    'key_info': 'Solicitation number, request eval scores, strengths/weaknesses'
                },
                'debrief_informal': {
                    'description': 'Feedback request for simplified acquisitions',
                    'tone': 'friendly, brief, asking for quick feedback',
                    'key_info': 'Were we competitive on price, any compliance issues'
                },
                'debrief_thanks': {
                    'description': 'Thank you after receiving debrief',
                    'tone': 'grateful, show you listened, relationship maintenance',
                    'key_info': 'Reference specific feedback, say how you are improving'
                },
                'sub_outreach': {
                    'description': 'Looking for subcontractor (we are prime)',
                    'tone': 'direct, professional, what we need from them',
                    'key_info': 'Service type, general location, requirements, NO buyer name'
                },
                'prime_outreach': {
                    'description': 'Approaching prime contractor (we want to sub)',
                    'tone': 'value-focused, EDWOSB advantage, what we bring',
                    'key_info': 'Our certs help their SB plan, our capabilities'
                },
                'teaming_followup': {
                    'description': 'Follow-up after initial teaming conversation',
                    'tone': 'action-oriented, recap discussion, propose next steps',
                    'key_info': 'Recap workshare, suggest NDA/teaming agreement, timeline'
                }
            }
            
            config = email_configs.get(email_type)
            if not config:
                return {'success': False, 'error': f"Unknown email type: {email_type}. Valid types: {list(email_configs.keys())}"}
            
            prompt = f"""Generate a professional GovCon email for Dee Davis Inc. (EDWOSB).

EMAIL TYPE: {config['description']}
TONE: {config['tone']}
KEY INFO TO INCLUDE: {config['key_info']}

COMPANY INFO:
- Company: Dee Davis Inc.
- Owner: Dieasha Davis (goes by Dee)
- Certifications: EDWOSB, WOSB, MBE, WBE, E-Verify, CMMC-AB (do not claim SWFT — see COMPANY_INFO_MASTER.md)
- CAGE: 8UMX3 | UEI: HJB4KNYJVGZ1
- MC: 1647572 | DOT: 4250594
- Location: Troy, Michigan

{f"OPPORTUNITY CONTEXT: {json.dumps(opp_data)}" if opp_data else ""}
{f"RECIPIENT (Subcontractor/Partner): {json.dumps(sub_data)}" if sub_data else ""}
{f"RECIPIENT (Government Contact): {json.dumps(contact_data)}" if contact_data else ""}
{f"ADDITIONAL CONTEXT: {custom_context}" if custom_context else ""}

CRITICAL RULES:
- NEVER reveal government client names to suppliers/subcontractors
- Use "Dee Davis" as signature name (professional name)
- Keep under 200 words for CO emails
- Include CAGE and UEI in government-facing emails
- Reference specific solicitation numbers when available
- Be human, not robotic — but professional

Return ONLY valid JSON:
{{
  "subject": "Email subject line",
  "body": "Full email body with proper formatting",
  "recipient_email": "email if known",
  "recipient_name": "name if known",
  "notes": "Any notes about this email"
}}"""

            response = self.ai.complete(prompt, max_tokens=1500)
            clean_response = response.strip()
            if clean_response.startswith('```'):
                clean_response = re.sub(r'^```json\s*', '', clean_response)
                clean_response = re.sub(r'```\s*$', '', clean_response)
                clean_response = clean_response.strip()
            
            email = json.loads(clean_response)
            
            print(f"📧 Generated {email_type} email" + (f" for {opp_data.get('name', '')}" if opp_data else ''))
            
            return {
                'success': True,
                'email_type': email_type,
                'description': config['description'],
                'subject': email.get('subject', ''),
                'body': email.get('body', ''),
                'recipient_email': email.get('recipient_email', contact_data.get('email', sub_data.get('email', ''))),
                'recipient_name': email.get('recipient_name', contact_data.get('name', sub_data.get('contact', ''))),
                'opportunity_id': opportunity_id,
                'notes': email.get('notes', '')
            }
            
        except Exception as e:
            print(f"Error generating email: {e}")
            return {'success': False, 'error': str(e)}
    
    def generate_proposal_matrix(self, opportunity_id: str) -> Dict:
        """
        Auto-generate a compliance/proposal matrix from an analyzed RFP.
        
        Triggered by:
        - After RFP upload and AI analysis completes
        - Workflow advance to 'Generate Proposal'
        - Manual request
        
        Pulls the AI analysis from the opportunity record and builds a
        structured compliance matrix showing every requirement and where
        it must be addressed.
        
        Args:
            opportunity_id: Airtable opportunity ID
            
        Returns:
            Structured proposal matrix with all requirements mapped
        """
        try:
            # 1. Get opportunity and its analysis
            opp = self.airtable.get_record('GPSS Opportunities', opportunity_id)
            if not opp:
                return {'success': False, 'error': 'Opportunity not found'}
            
            opp_fields = opp.get('fields', {})
            opp_name = opp_fields.get('Name', '')
            rfp_number = opp_fields.get('RFP NUMBER', '')
            agency = opp_fields.get('AGENCY NAME', opp_fields.get('Agency', ''))
            deadline = opp_fields.get('Deadline', '')
            set_aside = opp_fields.get('Set-Aside Type', '')
            notes = opp_fields.get('Notes', '')
            
            # 2. Use AI to build the matrix from the opportunity data
            prompt = f"""You are building a proposal compliance matrix for Dee Davis Inc. (EDWOSB) based on this analyzed government opportunity.

OPPORTUNITY:
Name: {opp_name}
RFP Number: {rfp_number}
Agency: {agency}
Deadline: {deadline}
Set-Aside: {set_aside}

ANALYSIS/NOTES:
{notes[:5000]}

Based on this information, generate a structured proposal compliance matrix. For each requirement you can identify, create a row with:
1. Reference (Section/paragraph if identifiable)
2. Requirement description
3. Which proposal volume should address it (Admin, Technical, Past Performance, Price, or Compliance)
4. Priority (Critical, Important, Standard)
5. Status placeholder (Not Started)

Also identify:
- Evaluation factors (if discernible from the notes)
- Required documents/certifications
- Special compliance requirements
- Whether subcontractors are needed

Return ONLY valid JSON:
{{
  "opportunity_name": "{opp_name}",
  "rfp_number": "{rfp_number}",
  "agency": "{agency}",
  "deadline": "{deadline}",
  "evaluation_approach": "Best Value|LPTA|Highest Technical|Unknown",
  "evaluation_factors": [
    {{"factor": "Factor name", "weight": "Weight if known", "priority": "Critical|Important"}}
  ],
  "compliance_matrix": [
    {{
      "ref": "Section reference",
      "requirement": "What is required",
      "volume": "Admin|Technical|Past Performance|Price|Compliance",
      "priority": "Critical|Important|Standard",
      "status": "Not Started",
      "notes": "Any specific guidance"
    }}
  ],
  "required_documents": ["List of required docs"],
  "required_certifications": ["SAM.gov", "E-Verify", "etc"],
  "subcontractor_needed": true/false,
  "subcontractor_reason": "Why/why not",
  "total_requirements": 0,
  "critical_requirements": 0
}}"""

            response = self.ai.complete(prompt, max_tokens=4000)
            clean_response = response.strip()
            if clean_response.startswith('```'):
                clean_response = re.sub(r'^```json\s*', '', clean_response)
                clean_response = re.sub(r'```\s*$', '', clean_response)
                clean_response = clean_response.strip()
            
            matrix = json.loads(clean_response)
            
            # Count stats
            total = len(matrix.get('compliance_matrix', []))
            critical = sum(1 for r in matrix.get('compliance_matrix', []) if r.get('priority') == 'Critical')
            matrix['total_requirements'] = total
            matrix['critical_requirements'] = critical
            
            print(f"📋 Proposal Matrix Generated: {opp_name}")
            print(f"   {total} requirements identified ({critical} critical)")
            
            return {
                'success': True,
                'opportunity_id': opportunity_id,
                'matrix': matrix,
                'summary': f"{total} requirements identified ({critical} critical) for {opp_name}",
                'next_step': 'Address each requirement starting with Critical items'
            }
            
        except Exception as e:
            print(f"Error generating proposal matrix: {e}")
            return {'success': False, 'error': str(e)}


# =====================================================================
# RSS OPPORTUNITY MONITORING
# =====================================================================

import feedparser
from datetime import datetime, timedelta
from typing import List, Dict, Optional


# Government RSS Feeds to Monitor (VERIFIED WORKING SOURCES ONLY)
GOVERNMENT_RSS_FEEDS = [
    # ===== FEDERAL - BROAD COVERAGE =====
    {
        'name': 'SAM.gov - All Opportunities',
        'url': 'https://sam.gov/api/prod/opps/v3/opportunities/rss',
        'type': 'Federal',
        'keywords': [
            # Services - Professional
            'consulting', 'management', 'advisory', 'professional services',
            'project management', 'program management', 'business services',
            'strategic planning', 'organizational development', 'change management',
            
            # Services - Technical
            'technical services', 'engineering', 'design', 'analysis',
            'research', 'development', 'testing', 'evaluation',
            
            # Services - IT & Technology
            'it', 'information technology', 'software', 'systems', 'hardware',
            'cybersecurity', 'networking', 'cloud', 'data', 'digital',
            
            # Services - Administrative
            'administrative', 'clerical', 'office', 'secretarial',
            'data entry', 'records', 'documentation', 'scheduling',
            
            # Services - Facilities
            'facilities', 'maintenance', 'janitorial', 'cleaning', 'grounds',
            'landscaping', 'custodial', 'building services', 'hvac',
            
            # Services - Transportation & Logistics
            'transportation', 'logistics', 'shipping', 'delivery', 'freight',
            'courier', 'warehousing', 'distribution', 'supply chain',
            
            # Services - Healthcare & Medical
            'medical', 'healthcare', 'health', 'clinical', 'nursing',
            'pharmacy', 'laboratory', 'diagnostic', 'patient care',
            
            # Services - Education & Training
            'training', 'education', 'instruction', 'curriculum', 'teaching',
            'learning', 'workshops', 'certification', 'development',
            
            # Services - Security & Emergency
            'security', 'emergency', 'disaster', 'preparedness', 'response',
            'safety', 'protection', 'surveillance', 'guard',
            
            # Products - General
            'supplies', 'equipment', 'materials', 'products', 'goods',
            'inventory', 'stock', 'commodities', 'merchandise',
            
            # Products - Office & Admin
            'office supplies', 'furniture', 'computers', 'printers',
            'paper', 'stationery', 'toner', 'storage', 'desks', 'chairs',
            
            # Products - Medical & Lab
            'medical supplies', 'laboratory supplies', 'pharmaceuticals',
            'medical equipment', 'diagnostic equipment', 'hospital supplies',
            
            # Products - Safety & Emergency
            'safety equipment', 'emergency supplies', 'first aid', 'ppe',
            'personal protective equipment', 'fire safety', 'rescue equipment',
            
            # Products - Construction & Tools
            'tools', 'hardware', 'construction materials', 'building supplies',
            'electrical', 'plumbing', 'hvac equipment',
            
            # Products - Vehicles & Transportation
            'vehicles', 'trucks', 'cars', 'vans', 'buses', 'trailers',
            'automotive', 'fleet', 'transportation equipment',
            
            # Set-Asides & Certifications
            'small business', 'women-owned', 'edwosb', 'wosb', 'hubzone',
            '8(a)', 'sdvosb', 'veteran-owned', 'minority-owned',
            
            # Contract Types
            'rfp', 'rfq', 'solicitation', 'contract', 'award',
            'idiq', 'bpa', 'gsa schedule', 'blanket purchase'
        ],
        'enabled': True,
        'verified': True,
        'priority': 'CRITICAL'
    },
    
    # ===== FEDERAL - SET-ASIDES (HIGH PRIORITY) =====
    {
        'name': 'SAM.gov - EDWOSB Set-Asides',
        'url': 'https://sam.gov/api/prod/opps/v3/opportunities/rss?setAside=EDWOSB',
        'type': 'Federal',
        'keywords': ['edwosb', 'women-owned', 'economically disadvantaged', 'small business'],
        'enabled': True,
        'verified': True,
        'priority': 'CRITICAL'
    },
    {
        'name': 'SAM.gov - WOSB Set-Asides',
        'url': 'https://sam.gov/api/prod/opps/v3/opportunities/rss?setAside=WOSB',
        'type': 'Federal',
        'keywords': ['wosb', 'women-owned', 'small business'],
        'enabled': True,
        'verified': True,
        'priority': 'CRITICAL'
    },
    {
        'name': 'SAM.gov - Small Business Set-Asides',
        'url': 'https://sam.gov/api/prod/opps/v3/opportunities/rss?setAside=SBA',
        'type': 'Federal',
        'keywords': ['small business', 'sba', 'set-aside'],
        'enabled': True,
        'verified': False,
        'priority': 'HIGH'
    },
    
    # ===== DDI ACTIVE SERVICE LINES (HIGHEST PRIORITY) =====
    {
        'name': 'NAICS 621511 - Medical Laboratories (Drug Testing, Genetic Testing)',
        'url': 'https://sam.gov/api/prod/opps/v3/opportunities/rss?naics=621511',
        'type': 'Federal',
        'keywords': [
            'drug testing', 'drug and alcohol testing', 'workplace drug testing', 'DOT drug testing',
            'laboratory', 'lab testing', 'specimen', 'urinalysis', 'genetic', 'DNA', 'toxicology', 'SAMHSA',
            'C/TPA', 'consortium', 'random testing', 'pre-employment', 'Part 40',
        ],
        'enabled': True,
        'naics': '621511',
        'description': 'Drug Testing, Genetic Testing, Medical Lab Services — ACTIVE DDI SERVICE LINE'
    },
    {
        'name': 'NAICS 621999 - All Other Ambulatory Health Care (Drug Testing Services)',
        'url': 'https://sam.gov/api/prod/opps/v3/opportunities/rss?naics=621999',
        'type': 'Federal',
        'keywords': [
            'drug testing', 'drug and alcohol testing', 'alcohol testing', 'health screening', 'workplace testing',
            'workplace drug testing', 'substance abuse', 'DOT testing', 'DOT drug', 'occupational testing',
            'C/TPA', 'consortium', 'SAMHSA',
        ],
        'enabled': True,
        'naics': '621999',
        'description': 'Drug Testing Services — ACTIVE DDI SERVICE LINE'
    },
    {
        'name': 'NAICS 541380 - Testing Laboratories & Services (Drug/Substance Testing)',
        'url': 'https://sam.gov/api/prod/opps/v3/opportunities/rss?naics=541380',
        'type': 'Federal',
        'keywords': [
            'testing laboratory', 'drug testing', 'drug and alcohol testing', 'substance testing',
            'forensic testing', 'analytical testing', 'lab services', 'toxicology', 'workplace drug testing',
        ],
        'enabled': True,
        'naics': '541380',
        'description': 'Testing Laboratories — Drug/Substance/Forensic Testing — ACTIVE DDI SERVICE LINE'
    },
    {
        'name': 'NAICS 561611 - Investigation Services (Fingerprinting)',
        'url': 'https://sam.gov/api/prod/opps/v3/opportunities/rss?naics=561611',
        'type': 'Federal',
        'keywords': [
            'biometrics', 'biometric', 'fingerprinting', 'fingerprint', 'background check', 'investigation',
            'identity verification', 'livescan', 'live scan', 'electronic fingerprinting', 'ink rolling',
            'FD-258', 'criminal history fingerprinting', 'applicant fingerprint',
        ],
        'enabled': True,
        'naics': '561611',
        'description': 'Fingerprinting, Background Checks — ACTIVE DDI SERVICE LINE'
    },
    {
        'name': 'NAICS 621910 - Ambulance Services (NEMT)',
        'url': 'https://sam.gov/api/prod/opps/v3/opportunities/rss?naics=621910',
        'type': 'Federal',
        'keywords': ['NEMT', 'non-emergency', 'medical transportation', 'patient transport', 'patient transportation', 'ambulance', 'medical transit', 'paratransit'],
        'enabled': True,
        'naics': '621910',
        'description': 'Non-Emergency Medical Transportation — ACTIVE DDI SERVICE LINE'
    },
    {
        'name': 'NAICS 485991 - Special Needs Transportation (PRIMARY NEMT)',
        'url': 'https://sam.gov/api/prod/opps/v3/opportunities/rss?naics=485991',
        'type': 'Federal',
        'keywords': ['NEMT', 'non-emergency medical transportation', 'non-emergency medical transport', 'special needs', 'medical transport', 'patient transport', 'patient transportation', 'wheelchair', 'stretcher', 'disabled transport', 'paratransit', 'Medicaid transportation'],
        'enabled': True,
        'naics': '485991',
        'description': 'PRIMARY NAICS for NEMT — ACTIVE DDI SERVICE LINE'
    },
    {
        'name': 'NAICS 485999 - All Other Transit & Ground Passenger (NEMT/Shuttle)',
        'url': 'https://sam.gov/api/prod/opps/v3/opportunities/rss?naics=485999',
        'type': 'Federal',
        'keywords': ['NEMT', 'shuttle', 'passenger transport', 'transit', 'transportation services', 'medical transport', 'patient transport', 'paratransit'],
        'enabled': True,
        'naics': '485999',
        'description': 'NEMT, Shuttle Services — ACTIVE DDI SERVICE LINE'
    },
    {
        'name': 'NAICS 485510 - Charter Bus (Shuttle Transportation)',
        'url': 'https://sam.gov/api/prod/opps/v3/opportunities/rss?naics=485510',
        'type': 'Federal',
        'keywords': ['shuttle', 'charter', 'bus', 'passenger', 'employee transport'],
        'enabled': True,
        'naics': '485510',
        'description': 'Shuttle Transportation — ACTIVE DDI SERVICE LINE'
    },
    {
        'name': 'NAICS 485410 - School & Employee Bus Transportation (Shuttle)',
        'url': 'https://sam.gov/api/prod/opps/v3/opportunities/rss?naics=485410',
        'type': 'Federal',
        'keywords': ['employee shuttle', 'bus transportation', 'shuttle service', 'facility shuttle', 'base shuttle'],
        'enabled': True,
        'naics': '485410',
        'description': 'Employee/Facility Shuttle — ACTIVE DDI SERVICE LINE'
    },
    {
        'name': 'NAICS 492110 - Couriers & Express Delivery (Medical Courier)',
        'url': 'https://sam.gov/api/prod/opps/v3/opportunities/rss?naics=492110',
        'type': 'Federal',
        'keywords': ['courier', 'medical courier', 'healthcare logistics', 'specimen transport', 'express delivery', 'laboratory courier', 'chain of custody'],
        'enabled': True,
        'naics': '492110',
        'description': 'Healthcare logistics / medical courier, express delivery — ACTIVE DDI SERVICE LINE'
    },
    {
        'name': 'NAICS 492210 - Local Messengers & Local Delivery',
        'url': 'https://sam.gov/api/prod/opps/v3/opportunities/rss?naics=492210',
        'type': 'Federal',
        'keywords': ['messenger', 'local delivery', 'local courier', 'document delivery', 'same-day delivery'],
        'enabled': True,
        'naics': '492210',
        'description': 'Local Courier/Messenger — ACTIVE DDI SERVICE LINE'
    },
    {
        'name': 'NAICS 541199 - All Other Legal Services (Notary)',
        'url': 'https://sam.gov/api/prod/opps/v3/opportunities/rss?naics=541199',
        'type': 'Federal',
        'keywords': [
            'notary', 'notary public', 'notarization', 'notarial', 'legal services', 'document authentication',
            'signing agent', 'mobile notary', 'loan signing', 'RON', 'remote online notarization',
            'acknowledgment', 'jurat', 'apostille', 'witness', 'witnessing', 'subscribing witness',
            'credentialing', 'provider credentialing', 'primary source verification', 'PSV',
        ],
        'enabled': True,
        'naics': '541199',
        'description': 'Notary Services — ACTIVE DDI SERVICE LINE'
    },

    # ===== DDI DISASTER RELIEF & EMERGENCY SERVICES =====
    {
        'name': 'NAICS 624230 - Emergency & Other Relief Services',
        'url': 'https://sam.gov/api/prod/opps/v3/opportunities/rss?naics=624230',
        'type': 'Federal',
        'keywords': ['disaster', 'emergency', 'relief', 'shelter', 'FEMA', 'hurricane', 'flood', 'evacuation', 'disaster relief'],
        'enabled': True,
        'naics': '624230',
        'description': 'Emergency & Disaster Relief — DDI GROWTH SERVICE LINE'
    },
    {
        'name': 'NAICS 624221 - Temporary Shelters',
        'url': 'https://sam.gov/api/prod/opps/v3/opportunities/rss?naics=624221',
        'type': 'Federal',
        'keywords': ['temporary shelter', 'emergency housing', 'transitional housing', 'shelter management'],
        'enabled': True,
        'naics': '624221',
        'description': 'Temporary Shelters — DDI GROWTH SERVICE LINE'
    },
    {
        'name': 'NAICS 722320 - Caterers (Emergency Feeding)',
        'url': 'https://sam.gov/api/prod/opps/v3/opportunities/rss?naics=722320',
        'type': 'Federal',
        'keywords': ['catering', 'emergency feeding', 'mass feeding', 'meals', 'food service', 'disaster meals'],
        'enabled': True,
        'naics': '722320',
        'description': 'Emergency Feeding / Catering — DDI GROWTH SERVICE LINE'
    },
    {
        'name': 'NAICS 562119 - Other Waste Collection (Debris Removal)',
        'url': 'https://sam.gov/api/prod/opps/v3/opportunities/rss?naics=562119',
        'type': 'Federal',
        'keywords': ['debris', 'waste', 'storm cleanup', 'demolition', 'disposal', 'hauling'],
        'enabled': True,
        'naics': '562119',
        'description': 'Debris Removal & Storm Cleanup — DDI GROWTH SERVICE LINE'
    },
    {
        'name': 'NAICS 562910 - Remediation Services (Hazmat/Disaster Cleanup)',
        'url': 'https://sam.gov/api/prod/opps/v3/opportunities/rss?naics=562910',
        'type': 'Federal',
        'keywords': ['remediation', 'hazmat', 'mold', 'contamination', 'cleanup', 'environmental'],
        'enabled': True,
        'naics': '562910',
        'description': 'Remediation / Hazmat Cleanup — DDI GROWTH SERVICE LINE'
    },
    {
        'name': 'NAICS 532490 - Equipment Rental & Leasing (Emergency Equipment)',
        'url': 'https://sam.gov/api/prod/opps/v3/opportunities/rss?naics=532490',
        'type': 'Federal',
        'keywords': ['equipment rental', 'generator rental', 'leasing', 'emergency equipment', 'temporary'],
        'enabled': True,
        'naics': '532490',
        'description': 'Emergency Equipment Rental — DDI GROWTH SERVICE LINE'
    },
    {
        'name': 'NAICS 424490 - Grocery & Related Products (Emergency Supplies)',
        'url': 'https://sam.gov/api/prod/opps/v3/opportunities/rss?naics=424490',
        'type': 'Federal',
        'keywords': ['food supplies', 'water', 'MRE', 'emergency food', 'bottled water', 'canned goods'],
        'enabled': True,
        'naics': '424490',
        'description': 'Emergency Food & Water Supplies — DDI GROWTH SERVICE LINE'
    },

    # ===== NAICS 54 - PROFESSIONAL, SCIENTIFIC & TECHNICAL SERVICES =====
    {
        'name': 'NAICS 541 - Professional Services (All)',
        'url': 'https://sam.gov/api/prod/opps/v3/opportunities/rss?naics=541',
        'type': 'Federal',
        'keywords': ['professional', 'consulting', 'technical', 'scientific', 'services'],
        'enabled': True,
        'naics': '541',
        'description': 'All Professional, Scientific, and Technical Services'
    },
    {
        'name': 'NAICS 541611 - Management Consulting',
        'url': 'https://sam.gov/api/prod/opps/v3/opportunities/rss?naics=541611',
        'type': 'Federal',
        'keywords': ['management', 'consulting', 'advisory', 'strategic planning'],
        'enabled': True,
        'naics': '541611'
    },
    {
        'name': 'NAICS 541618 - Other Management Consulting',
        'url': 'https://sam.gov/api/prod/opps/v3/opportunities/rss?naics=541618',
        'type': 'Federal',
        'keywords': ['consulting', 'operations', 'process improvement', 'efficiency'],
        'enabled': True,
        'naics': '541618'
    },
    {
        'name': 'NAICS 541512 - Computer Systems Design',
        'url': 'https://sam.gov/api/prod/opps/v3/opportunities/rss?naics=541512',
        'type': 'Federal',
        'keywords': ['it', 'software', 'systems', 'computer', 'technology'],
        'enabled': True,
        'naics': '541512'
    },
    {
        'name': 'NAICS 541519 - Other Computer Services',
        'url': 'https://sam.gov/api/prod/opps/v3/opportunities/rss?naics=541519',
        'type': 'Federal',
        'keywords': ['it services', 'computer support', 'technical support'],
        'enabled': True,
        'naics': '541519'
    },
    {
        'name': 'NAICS 541330 - Engineering Services',
        'url': 'https://sam.gov/api/prod/opps/v3/opportunities/rss?naics=541330',
        'type': 'Federal',
        'keywords': ['engineering', 'design', 'technical', 'structural', 'mechanical'],
        'enabled': True,
        'naics': '541330'
    },
    {
        'name': 'NAICS 541990 - All Other Professional Services',
        'url': 'https://sam.gov/api/prod/opps/v3/opportunities/rss?naics=541990',
        'type': 'Federal',
        'keywords': ['professional services', 'technical services', 'consulting'],
        'enabled': True,
        'naics': '541990'
    },
    
    # ===== NAICS 56 - ADMINISTRATIVE & SUPPORT SERVICES =====
    {
        'name': 'NAICS 561 - Administrative Services (All)',
        'url': 'https://sam.gov/api/prod/opps/v3/opportunities/rss?naics=561',
        'type': 'Federal',
        'keywords': ['administrative', 'support', 'business services', 'office'],
        'enabled': True,
        'naics': '561'
    },
    {
        'name': 'NAICS 561110 - Office Administrative Services',
        'url': 'https://sam.gov/api/prod/opps/v3/opportunities/rss?naics=561110',
        'type': 'Federal',
        'keywords': ['office', 'administrative', 'clerical', 'secretarial'],
        'enabled': True,
        'naics': '561110'
    },
    {
        'name': 'NAICS 561210 - Facilities Support Services',
        'url': 'https://sam.gov/api/prod/opps/v3/opportunities/rss?naics=561210',
        'type': 'Federal',
        'keywords': ['facilities', 'maintenance', 'janitorial', 'building services'],
        'enabled': True,
        'naics': '561210'
    },
    {
        'name': 'NAICS 561720 - Janitorial Services',
        'url': 'https://sam.gov/api/prod/opps/v3/opportunities/rss?naics=561720',
        'type': 'Federal',
        'keywords': ['janitorial', 'cleaning', 'custodial', 'housekeeping'],
        'enabled': True,
        'naics': '561720'
    },
    {
        'name': 'NAICS 561730 - Landscaping Services',
        'url': 'https://sam.gov/api/prod/opps/v3/opportunities/rss?naics=561730',
        'type': 'Federal',
        'keywords': ['landscaping', 'grounds', 'lawn', 'gardening', 'horticulture'],
        'enabled': True,
        'naics': '561730'
    },
    {
        'name': 'NAICS 561990 - Other Support Services',
        'url': 'https://sam.gov/api/prod/opps/v3/opportunities/rss?naics=561990',
        'type': 'Federal',
        'keywords': ['support services', 'business support', 'administrative support'],
        'enabled': True,
        'naics': '561990'
    },
    
    # ===== NAICS 48-49 - TRANSPORTATION & WAREHOUSING =====
    {
        'name': 'NAICS 484 - Truck Transportation',
        'url': 'https://sam.gov/api/prod/opps/v3/opportunities/rss?naics=484',
        'type': 'Federal',
        'keywords': ['trucking', 'freight', 'cargo', 'hauling', 'delivery'],
        'enabled': True,
        'naics': '484'
    },
    {
        'name': 'NAICS 492 - Couriers & Messengers',
        'url': 'https://sam.gov/api/prod/opps/v3/opportunities/rss?naics=492',
        'type': 'Federal',
        'keywords': ['courier', 'messenger', 'delivery', 'express', 'package'],
        'enabled': True,
        'naics': '492'
    },
    {
        'name': 'NAICS 493 - Warehousing & Storage',
        'url': 'https://sam.gov/api/prod/opps/v3/opportunities/rss?naics=493',
        'type': 'Federal',
        'keywords': ['warehousing', 'storage', 'distribution', 'inventory'],
        'enabled': True,
        'naics': '493'
    },
    
    # ===== NAICS 62 - HEALTHCARE & SOCIAL ASSISTANCE =====
    {
        'name': 'NAICS 621 - Ambulatory Healthcare Services',
        'url': 'https://sam.gov/api/prod/opps/v3/opportunities/rss?naics=621',
        'type': 'Federal',
        'keywords': ['healthcare', 'medical', 'clinical', 'health services'],
        'enabled': True,
        'naics': '621'
    },
    {
        'name': 'NAICS 624 - Social Assistance',
        'url': 'https://sam.gov/api/prod/opps/v3/opportunities/rss?naics=624',
        'type': 'Federal',
        'keywords': ['social services', 'assistance', 'community services'],
        'enabled': True,
        'naics': '624'
    },
    
    # ===== NAICS 23 - CONSTRUCTION =====
    {
        'name': 'NAICS 236 - Construction of Buildings',
        'url': 'https://sam.gov/api/prod/opps/v3/opportunities/rss?naics=236',
        'type': 'Federal',
        'keywords': ['construction', 'building', 'contractor', 'renovation'],
        'enabled': True,
        'naics': '236'
    },
    {
        'name': 'NAICS 238 - Specialty Trade Contractors',
        'url': 'https://sam.gov/api/prod/opps/v3/opportunities/rss?naics=238',
        'type': 'Federal',
        'keywords': ['contractor', 'trades', 'electrical', 'plumbing', 'hvac'],
        'enabled': True,
        'naics': '238'
    },
    
    # ===== NAICS 42 - WHOLESALE TRADE (PRODUCTS) =====
    {
        'name': 'NAICS 423 - Merchant Wholesalers, Durable Goods',
        'url': 'https://sam.gov/api/prod/opps/v3/opportunities/rss?naics=423',
        'type': 'Federal',
        'keywords': ['wholesale', 'supplies', 'equipment', 'durable goods'],
        'enabled': True,
        'naics': '423'
    },
    {
        'name': 'NAICS 423840 - Industrial Supplies (RCOC, CPS Energy type bids)',
        'url': 'https://sam.gov/api/prod/opps/v3/opportunities/rss?naics=423840',
        'type': 'Federal',
        'keywords': ['industrial supplies', 'safety supplies', 'PPE', 'wipers', 'welding', 'janitorial', 'cleaning'],
        'enabled': True,
        'naics': '423840',
        'description': 'Industrial Supplies — ACTIVE DDI PRODUCT LINE'
    },
    {
        'name': 'NAICS 423610 - Electrical Equipment & Supplies (DLA, power cables)',
        'url': 'https://sam.gov/api/prod/opps/v3/opportunities/rss?naics=423610',
        'type': 'Federal',
        'keywords': ['electrical', 'power cable', 'cable assembly', 'relay', 'VFD', 'switchgear', 'generator', 'transformer'],
        'enabled': True,
        'naics': '423610',
        'description': 'Electrical Equipment — ACTIVE DDI PRODUCT LINE'
    },
    {
        'name': 'NAICS 423120 - Motor Vehicle Supplies & Parts',
        'url': 'https://sam.gov/api/prod/opps/v3/opportunities/rss?naics=423120',
        'type': 'Federal',
        'keywords': ['automotive', 'vehicle parts', 'wiper blades', 'truck parts', 'fleet', 'auto supplies'],
        'enabled': True,
        'naics': '423120',
        'description': 'Automotive Parts & Vehicle Supplies — ACTIVE DDI PRODUCT LINE'
    },
    {
        'name': 'NAICS 423450 - Medical Equipment & Supplies',
        'url': 'https://sam.gov/api/prod/opps/v3/opportunities/rss?naics=423450',
        'type': 'Federal',
        'keywords': ['medical supplies', 'hospital supplies', 'lab supplies', 'exam', 'surgical', 'diagnostic'],
        'enabled': True,
        'naics': '423450',
        'description': 'Medical & Lab Supplies — ACTIVE DDI PRODUCT LINE'
    },
    {
        'name': 'NAICS 423720 - Plumbing & Heating Equipment (Water infrastructure)',
        'url': 'https://sam.gov/api/prod/opps/v3/opportunities/rss?naics=423720',
        'type': 'Federal',
        'keywords': ['plumbing', 'valves', 'pipes', 'fittings', 'water', 'hydrant', 'infrastructure'],
        'enabled': True,
        'naics': '423720',
        'description': 'Water Infrastructure & Plumbing — ACTIVE DDI PRODUCT LINE'
    },
    {
        'name': 'NAICS 423390 - Other Construction Materials (Guardrails, barricades)',
        'url': 'https://sam.gov/api/prod/opps/v3/opportunities/rss?naics=423390',
        'type': 'Federal',
        'keywords': ['construction materials', 'guardrails', 'barricades', 'signs', 'aggregate', 'concrete', 'asphalt'],
        'enabled': True,
        'naics': '423390',
        'description': 'Construction Materials — ACTIVE DDI PRODUCT LINE'
    },
    {
        'name': 'NAICS 424690 - Chemical & Allied Products (Chlorine, solvents)',
        'url': 'https://sam.gov/api/prod/opps/v3/opportunities/rss?naics=424690',
        'type': 'Federal',
        'keywords': ['chemicals', 'chlorine', 'solvent', 'de-icer', 'salt', 'cleaning chemicals'],
        'enabled': True,
        'naics': '424690',
        'description': 'Chemicals & Allied Products — ACTIVE DDI PRODUCT LINE'
    },
    {
        'name': 'NAICS 424 - Merchant Wholesalers, Nondurable Goods',
        'url': 'https://sam.gov/api/prod/opps/v3/opportunities/rss?naics=424',
        'type': 'Federal',
        'keywords': ['wholesale', 'supplies', 'nondurable goods', 'products'],
        'enabled': True,
        'naics': '424'
    },
    
    # ===== NAICS 61 - EDUCATIONAL SERVICES =====
    {
        'name': 'NAICS 611 - Educational Services',
        'url': 'https://sam.gov/api/prod/opps/v3/opportunities/rss?naics=611',
        'type': 'Federal',
        'keywords': ['training', 'education', 'instruction', 'teaching', 'learning'],
        'enabled': True,
        'naics': '611'
    },
    
    # ===== NAICS 81 - OTHER SERVICES =====
    {
        'name': 'NAICS 811 - Repair & Maintenance',
        'url': 'https://sam.gov/api/prod/opps/v3/opportunities/rss?naics=811',
        'type': 'Federal',
        'keywords': ['repair', 'maintenance', 'service', 'fix', 'restore'],
        'enabled': True,
        'naics': '811'
    },
]

# NOTE: Most state/local/cooperative sources DON'T have RSS feeds
# These will be handled by API integrations and web scrapers below


class RSSOpportunityMonitor:
    """
    RSS Feed Monitoring System
    Checks government RSS feeds for new opportunities
    """
    
    def __init__(self):
        self.airtable = AirtableClient()
        self.anthropic_client = anthropic.Anthropic(api_key=Config.get_anthropic_key())
        self.feeds = GOVERNMENT_RSS_FEEDS
    
    def check_all_feeds(self) -> Dict:
        """
        Check all RSS feeds for new opportunities
        Returns summary of what was found
        """
        try:
            new_opportunities = []
            skipped = 0
            errors = []
            
            # Filter to only enabled feeds
            enabled_feeds = [f for f in self.feeds if f.get('enabled', True)]
            
            print(f"📡 Checking {len(enabled_feeds)} RSS feeds (out of {len(self.feeds)} total)...")
            
            for feed_config in enabled_feeds:
                try:
                    print(f"  Checking: {feed_config['name']}...")
                    opportunities = self.check_feed(feed_config)
                    new_opportunities.extend(opportunities)
                    print(f"    ✓ Found {len(opportunities)} new opportunities")
                except Exception as e:
                    error_msg = f"Error checking {feed_config['name']}: {str(e)}"
                    print(f"    ✗ {error_msg}")
                    errors.append(error_msg)
            
            return {
                'success': True,
                'feeds_checked': len(enabled_feeds),
                'total_feeds': len(self.feeds),
                'new_opportunities': len(new_opportunities),
                'opportunities': new_opportunities,
                'errors': errors
            }
            
        except Exception as e:
            print(f"RSS Monitor Error: {e}")
            return {
                'success': False,
                'error': str(e),
                'feeds_checked': 0,
                'new_opportunities': 0
            }
    
    def check_feed(self, feed_config: Dict) -> List[Dict]:
        """Check a single RSS feed for new opportunities"""
        try:
            # Parse RSS feed
            feed = feedparser.parse(feed_config['url'])
            
            if not feed.entries:
                print(f"    No entries found in feed")
                return []
            
            opportunities = []
            
            for entry in feed.entries[:10]:  # Check last 10 entries
                try:
                    # Extract opportunity data
                    opp_data = {
                        'title': entry.get('title', 'No Title'),
                        'description': entry.get('summary', entry.get('description', '')),
                        'url': entry.get('link', ''),
                        'published': entry.get('published', datetime.now().isoformat()),
                        'source': feed_config['name'],
                        'source_type': feed_config['type']
                    }
                    
                    # Check if it's recent (last 7 days)
                    pub_date = self._parse_date(entry.get('published'))
                    if pub_date and pub_date < datetime.now() - timedelta(days=7):
                        continue  # Skip old opportunities
                    
                    # Check if already exists
                    if self._is_duplicate(opp_data['url']):
                        continue  # Skip duplicates
                    
                    # Qualify with AI
                    qualification = self._qualify_opportunity(opp_data, feed_config['keywords'])
                    
                    if qualification['score'] >= 40:  # Threshold for import
                        # Prepare for Airtable (using correct field names)
                        airtable_data = {
                            'Name': opp_data['title'][:255],
                            'RFP NUMBER': f"RSS-{datetime.now().strftime('%Y%m%d')}-{len(opportunities)}",
                            'Status': 'New - RSS',
                            'Deadline': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
                        }
                        
                        # Save to Airtable
                        record = self.airtable.create_record('GPSS OPPORTUNITIES', airtable_data)
                        
                        opp_data['airtable_id'] = record['id']
                        opp_data['ai_score'] = qualification['score']
                        opp_data['ai_reason'] = qualification['reason']
                        
                        opportunities.append(opp_data)
                        
                except Exception as e:
                    print(f"      Error processing entry: {str(e)[:100]}")
                    continue
            
            return opportunities
            
        except Exception as e:
            print(f"    Feed parsing error: {e}")
            return []
    
    def _parse_date(self, date_string: str) -> Optional[datetime]:
        """Parse RSS date string to datetime"""
        if not date_string:
            return None
        
        try:
            # Try common RSS date formats
            from email.utils import parsedate_to_datetime
            return parsedate_to_datetime(date_string)
        except:
            try:
                return datetime.fromisoformat(date_string.replace('Z', '+00:00'))
            except:
                return None
    
    def _is_duplicate(self, url: str) -> bool:
        """Check if opportunity already exists in Airtable"""
        try:
            existing = self.airtable.get_all_records('GPSS OPPORTUNITIES')
            return any(
                opp['fields'].get('URL') == url 
                for opp in existing
            )
        except:
            return False
    
    def _qualify_opportunity(self, opp: Dict, keywords: List[str]) -> Dict:
        """Use Claude AI to qualify this opportunity"""
        try:
            # Build prompt
            prompt = f"""
Analyze this government opportunity from an RSS feed:

Title: {opp['title']}
Description: {opp['description'][:500]}
Source: {opp['source']}
Keywords: {', '.join(keywords)}

This is for an EDWOSB company specializing in:
- Professional services
- Management consulting  
- IT services
- Project management
- Training and development

Score this opportunity from 0-100 based on:
1. Is it a real RFP/RFQ/solicitation? (not just a notice or update)
2. Is it suitable for an EDWOSB company?
3. Does it match the keywords and services?
4. Is the description clear enough to qualify?

Return ONLY valid JSON:
{{"score": 0-100, "recommendation": "pursue/skip", "reason": "brief explanation"}}
"""
            
            message = self.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=200,
                messages=[{"role": "user", "content": prompt}]
            )
            response = message.content[0].text
            
            # Parse JSON response
            import json
            import re
            
            # Extract JSON from response
            json_match = re.search(r'\{[^}]+\}', response)
            if json_match:
                result = json.loads(json_match.group())
                return {
                    'score': result.get('score', 0),
                    'recommendation': result.get('recommendation', 'skip'),
                    'reason': result.get('reason', 'No reason provided')
                }
            else:
                # Fallback scoring
                score = 50  # Default moderate score
                if any(kw.lower() in opp['title'].lower() for kw in keywords):
                    score += 20
                if 'rfp' in opp['title'].lower() or 'rfq' in opp['title'].lower():
                    score += 20
                
                return {
                    'score': score,
                    'recommendation': 'review' if score >= 50 else 'skip',
                    'reason': 'Keyword-based scoring (AI parsing failed)'
                }
                
        except Exception as e:
            print(f"      Qualification error: {str(e)[:100]}")
            return {
                'score': 30,
                'recommendation': 'skip',
                'reason': f'Error: {str(e)[:100]}'
            }


def handle_check_rss_feeds() -> Dict:
    """Handler function for RSS feed checking"""
    monitor = RSSOpportunityMonitor()
    return monitor.check_all_feeds()


# =============================================================================
# SAM.GOV API CLIENT
# =============================================================================

class SAMgovAPIClient:
    """
    SAM.gov Opportunities API Client
    Fetches federal contract opportunities from SAM.gov API
    """
    
    def __init__(self):
        self.api_key = os.environ.get('SAM_GOV_API_KEY', '')
        self.base_url = "https://api.sam.gov/opportunities/v2/search"
        self.airtable = AirtableClient()
        self.anthropic_client = anthropic.Anthropic(api_key=Config.get_anthropic_key())
    
    # Set-aside codes that Dee Davis Inc qualifies for
    ELIGIBLE_SET_ASIDES = [
        'EDWOSB',     # Economically Disadvantaged Woman-Owned Small Business
        'WOSB',       # Woman-Owned Small Business
        'SBA',        # Small Business Set-Aside (Total)
        'SBP',        # Small Business Set-Aside (Partial)
    ]

    # Set-aside codes to EXCLUDE (cannot bid on these)
    INELIGIBLE_SET_ASIDES = [
        'SDVOSBC',    # Service-Disabled Veteran-Owned (Competitive)
        'SDVOSBS',    # Service-Disabled Veteran-Owned (Sole Source)
        'VOSB',       # Veteran-Owned Small Business — not veteran-owned
        'VSA',        # Veterans Set-Aside — not veteran-owned
        'VSB',        # Veterans Small Business — not veteran-owned
        'HZC',        # HUBZone (Competitive)
        'HZS',        # HUBZone (Sole Source)
        '8A',         # 8(a) Competitive
        '8AN',        # 8(a) Sole Source
        'IEE',        # Indian Economic Enterprise
        'ISBEE',      # Indian Small Business Economic Enterprise
    ]

    # Notice types we search for — includes presolicitations, sources sought, etc.
    NOTICE_TYPES_SOLICITATION = [
        'o',   # Solicitation
        'k',   # Combined Synopsis/Solicitation
    ]
    NOTICE_TYPES_PRESOLICITATION = [
        'p',   # Presolicitation
        'r',   # Sources Sought
        'i',   # Intent to Bundle / Special Notice
        's',   # Special Notice
    ]

    def search_opportunities(self, params: Dict = None) -> Dict:
        """
        Search SAM.gov for opportunities.
        FILTERS: EDWOSB, WOSB, Small Business ONLY.
        Excludes SDVOSB, VOSB, HUBZone, 8(a) — we don't qualify for those.
        NOW ALSO SEARCHES: Presolicitations, Sources Sought, Special Notices.
        """
        try:
            # Build request parameters — filtered for eligible set-asides
            # Include ALL relevant notice types: solicitations + presolicitations
            all_notice_types = self.NOTICE_TYPES_SOLICITATION + self.NOTICE_TYPES_PRESOLICITATION
            default_params = {
                'limit': 100,
                'postedFrom': (datetime.now() - timedelta(days=14)).strftime('%m/%d/%Y'),
                'postedTo': datetime.now().strftime('%m/%d/%Y'),
                'typeOfSetAside': ','.join(self.ELIGIBLE_SET_ASIDES),
                'ntype': ','.join(all_notice_types),
            }
            
            if params:
                default_params.update(params)
            
            # Build headers with API key
            headers = {}
            if self.api_key:
                headers['X-Api-Key'] = self.api_key
                print(f"🔍 Searching SAM.gov API — EDWOSB/WOSB/SB ONLY...")
            else:
                print("⚠️  SAM_GOV_API_KEY not configured - using public access (limited)")
                print("   Get a free API key from: https://sam.gov/data-services/")
            
            print(f"   Request URL: {self.base_url}")
            print(f"   Date Range: {default_params['postedFrom']} to {default_params['postedTo']}")
            print(f"   Set-Aside Filter: {default_params.get('typeOfSetAside', 'NONE')}")
            
            response = requests.get(self.base_url, params=default_params, headers=headers, timeout=30)
            
            print(f"   Response Status: {response.status_code}")
            
            if response.status_code != 200:
                print(f"   Response: {response.text[:500]}")
            
            response.raise_for_status()
            
            data = response.json()
            opportunities_data = data.get('opportunitiesData', [])
            total_records = data.get('totalRecords', 0)
            
            print(f"   ✓ Found {total_records} total, retrieved {len(opportunities_data)}")
            
            if len(opportunities_data) == 0:
                print("   ℹ️  No opportunities found in the past 7 days")
                print("   This is normal - try expanding the date range")
            
            qualified_opportunities = []
            skipped_duplicates = 0
            low_scores = 0
            
            skipped_ineligible = 0
            for idx, opp in enumerate(opportunities_data, 1):
                try:
                    notice_id = opp.get('noticeId', '')
                    
                    if self._is_duplicate(notice_id):
                        skipped_duplicates += 1
                        continue
                    
                    # CRITICAL: Double-check set-aside eligibility
                    set_aside = (opp.get('typeOfSetAside') or '').upper()
                    set_aside_code = (opp.get('typeOfSetAsideDescription') or '').upper()
                    combined = set_aside + ' ' + set_aside_code
                    
                    # Skip if it's a set-aside we can't bid on
                    is_ineligible = False
                    for code in self.INELIGIBLE_SET_ASIDES:
                        if code.upper() in combined:
                            is_ineligible = True
                            break
                    if 'SDVOSB' in combined or 'VOSB' in combined or 'VETERAN' in combined or 'SERVICE-DISABLED' in combined or 'HUBZONE' in combined or '8(A)' in combined:
                        is_ineligible = True
                    
                    if is_ineligible:
                        skipped_ineligible += 1
                        continue
                    
                    qualified_opportunities.append({
                        'opportunity': opp,
                        'qualification': {'score': 75, 'reasoning': f'SAM.gov — Set-aside: {set_aside or "Eligible"}'}
                    })
                    
                except Exception as e:
                    if idx <= 3:
                        print(f"   ⚠️  Error processing opportunity {idx}: {str(e)[:100]}")
                    continue
            
            if skipped_ineligible > 0:
                print(f"   ⏭️  Filtered out {skipped_ineligible} ineligible set-asides (SDVOSB/VOSB/HUBZone/8(a))")
            
            print(f"   ✓ Qualified {len(qualified_opportunities)} opportunities")
            if skipped_duplicates > 0:
                print(f"   ⏭️  Skipped {skipped_duplicates} duplicates")
            
            imported_count = 0
            errors = []
            
            for idx, item in enumerate(qualified_opportunities, 1):
                try:
                    self._import_to_airtable(item['opportunity'], item['qualification'])
                    imported_count += 1
                    if idx <= 3:
                        title = item['opportunity'].get('title', 'Untitled')[:30]
                        print(f"   ✓ [{idx}] Imported: {title}...")
                except Exception as e:
                    error_msg = str(e)
                    errors.append(error_msg)
                    if len(errors) <= 3:
                        print(f"   ❌ [{idx}] Import error: {error_msg[:100]}")
            
            print(f"\n   ✅ IMPORT COMPLETE: {imported_count} imported")
            if errors:
                print(f"   ⚠️  {len(errors)} errors during import")
            
            return {
                'success': True,
                'total_found': total_records,
                'retrieved': len(opportunities_data),
                'qualified': len(qualified_opportunities),
                'imported': imported_count,
                'duplicates': skipped_duplicates,
                'errors': len(errors),
                'source': 'SAM.gov API'
            }
            
        except requests.exceptions.HTTPError as e:
            error_msg = f"HTTP {e.response.status_code}: {e.response.text[:200]}"
            print(f"❌ SAM.gov API Error: {error_msg}")
            return {'success': False, 'error': error_msg, 'total_found': 0, 'imported': 0}
        except Exception as e:
            print(f"❌ SAM.gov Error: {e}")
            import traceback
            traceback.print_exc()
            return {'success': False, 'error': str(e), 'total_found': 0, 'imported': 0}
    
    def _is_duplicate(self, notice_id: str) -> bool:
        """Check if exists"""
        try:
            records = self.airtable.get_all_records('GPSS OPPORTUNITIES')
            return any(r['fields'].get('RFP NUMBER') == notice_id for r in records)
        except:
            return False
    
    def _qualify_opportunity(self, opp: Dict) -> Dict:
        """AI qualification"""
        try:
            title = opp.get('title', '')
            set_aside = opp.get('typeOfSetAsideDescription', '')
            
            score = 50
            if 'women' in set_aside.lower() or 'wosb' in set_aside.lower():
                score += 30
            if any(kw in title.lower() for kw in ['consulting', 'professional', 'management', 'training']):
                score += 15
                
            return {'score': score, 'recommendation': 'pursue' if score >= 70 else 'skip', 'reason': 'Auto-scored'}
        except:
            return {'score': 50, 'recommendation': 'skip', 'reason': 'Error'}
    
    # Map SAM.gov notice type codes to readable labels
    PRESOLICITATION_NOTICE_TYPES = {
        'Presolicitation': True,
        'Sources Sought': True,
        'Special Notice': True,
        'Intent to Bundle Requirements (DOD- Loss of Small Business Opportunities)': True,
    }

    def _is_presolicitation_type(self, opp: Dict) -> str:
        """
        Determine if an opportunity is a presolicitation, sources sought, or sole source notice.
        Returns the type string if yes, empty string if no.
        """
        notice_type = (opp.get('type') or opp.get('noticeType') or '').strip()
        
        # Check against known presolicitation types
        if notice_type in self.PRESOLICITATION_NOTICE_TYPES:
            return notice_type
        
        # Check by common keywords in the type field
        notice_lower = notice_type.lower()
        if 'presolicitation' in notice_lower:
            return 'Presolicitation'
        if 'sources sought' in notice_lower:
            return 'Sources Sought'
        if 'special notice' in notice_lower:
            return 'Special Notice'
        if 'intent' in notice_lower and 'sole' in notice_lower:
            return 'Intent to Sole Source'
        
        # Check the title for sole source / sources sought indicators
        title_lower = (opp.get('title') or '').lower()
        if 'sources sought' in title_lower:
            return 'Sources Sought'
        if 'sole source' in title_lower or 'intent to sole' in title_lower:
            return 'Intent to Sole Source'
        if 'presolicitation' in title_lower:
            return 'Presolicitation'
        if 'request for information' in title_lower or ' rfi ' in f' {title_lower} ':
            return 'Sources Sought'
        
        return ''

    def _import_to_airtable(self, opp: Dict, qualification: Dict):
        """Import to Airtable — auto-triggers presolicitation response if applicable"""
        from dateutil import parser
        
        # Parse dates safely
        due_date = ''
        try:
            if opp.get('responseDeadLine'):
                due_date = parser.parse(opp['responseDeadLine']).strftime('%Y-%m-%d')
        except:
            pass
        
        # Detect presolicitation type
        presol_type = self._is_presolicitation_type(opp)
        
        # Map to actual Airtable field names
        fields = {
            'Name': opp.get('title', 'Untitled')[:255],
            'RFP NUMBER': opp.get('noticeId', ''),
            'Status': f'New - {presol_type}' if presol_type else 'New - API',
        }

        # Add optional fields
        if due_date:
            fields['Deadline'] = due_date

        # Research Lane detection — tag if community health / market research
        research_tags = ResearchLaneDetector().detect(
            title=opp.get('title', ''),
            description=opp.get('description', ''),
            agency=opp.get('fullParentPathName', '') or opp.get('department', ''),
            naics=opp.get('naicsCode', ''),
        )
        if research_tags:
            fields.update(research_tags)
            print(f"   🔬 Research Lane detected: {research_tags.get('Research Subtype')} — {opp.get('title','')[:60]}")

        self.airtable.create_record('GPSS OPPORTUNITIES', fields)
        
        # AUTO-RESPONSE: If presolicitation type, generate cap statement + buyer email + folder
        if presol_type:
            try:
                self._auto_respond_presolicitation(opp, presol_type)
            except Exception as e:
                print(f"   ⚠️  Auto-response generation failed for {opp.get('noticeId', 'unknown')}: {e}")

    def _auto_respond_presolicitation(self, opp: Dict, presol_type: str):
        """
        AUTOMATIC presolicitation response:
        1. Creates bid folder with SEND_TO_BUYER/
        2. Generates tailored capability statement (HTML)
        3. Generates buyer outreach email
        4. Places both in SEND_TO_BUYER/
        
        This runs automatically when a presolicitation/sources sought/sole source
        notice is mined from SAM.gov. No manual trigger needed.
        """
        import os
        
        title = opp.get('title', 'Untitled')
        notice_id = opp.get('noticeId', '')
        agency = opp.get('fullParentPathName', '') or opp.get('department', '') or ''
        description = opp.get('description', '')[:1000]
        set_aside = opp.get('typeOfSetAsideDescription', '') or opp.get('typeOfSetAside', '')
        naics = opp.get('naicsCode', '')
        deadline = opp.get('responseDeadLine', '')
        
        # Extract contracting officer info
        contact_name = ''
        contact_email = ''
        contact_phone = ''
        point_of_contact = opp.get('pointOfContact', [])
        if isinstance(point_of_contact, list) and len(point_of_contact) > 0:
            poc = point_of_contact[0]
            contact_name = poc.get('fullName', '') or f"{poc.get('firstName', '')} {poc.get('lastName', '')}".strip()
            contact_email = poc.get('email', '')
            contact_phone = poc.get('phone', '')
        elif isinstance(point_of_contact, dict):
            contact_name = point_of_contact.get('fullName', '') or f"{point_of_contact.get('firstName', '')} {point_of_contact.get('lastName', '')}".strip()
            contact_email = point_of_contact.get('email', '')
            contact_phone = point_of_contact.get('phone', '')
        
        # Generate folder name: [AGENCY SHORT] [BID TYPE]
        folder_name = self._generate_folder_name(agency, title)
        
        base_path = os.path.join(os.path.dirname(__file__), 'BIDS:RESOURCES', folder_name)
        send_to_buyer = os.path.join(base_path, 'SEND_TO_BUYER')
        send_to_supplier = os.path.join(base_path, 'SEND_TO_SUPPLIER')
        send_to_sub = os.path.join(base_path, 'SEND_TO_SUBCONTRACTOR')
        
        # Create folder structure
        for d in [send_to_buyer, send_to_supplier, send_to_sub]:
            os.makedirs(d, exist_ok=True)
        
        print(f"   📁 Created bid folder: {folder_name}")
        
        # Generate capability statement HTML
        capstat_html = self._generate_presol_capstat_html(
            title=title,
            notice_id=notice_id,
            agency=agency,
            presol_type=presol_type,
            description=description,
            set_aside=set_aside,
            naics=naics,
        )
        
        safe_notice_id = notice_id.replace('/', '-').replace(' ', '_')
        capstat_filename = f'{safe_notice_id}_Capability_Statement.html'
        capstat_path = os.path.join(send_to_buyer, capstat_filename)
        with open(capstat_path, 'w') as f:
            f.write(capstat_html)
        
        print(f"   📄 Generated capability statement: {capstat_filename}")
        
        # Generate buyer outreach email
        email_text = self._generate_presol_buyer_email(
            title=title,
            notice_id=notice_id,
            agency=agency,
            presol_type=presol_type,
            contact_name=contact_name,
            contact_email=contact_email,
            contact_phone=contact_phone,
            set_aside=set_aside,
            description=description,
        )
        
        email_path = os.path.join(send_to_buyer, 'SEND_TO_BUYER_EMAIL_READY.md')
        with open(email_path, 'w') as f:
            f.write(email_text)
        
        print(f"   📧 Generated buyer email: SEND_TO_BUYER_EMAIL_READY.md")
        
        # Generate workflow checklist
        checklist = self._generate_presol_workflow_checklist(
            title=title,
            notice_id=notice_id,
            agency=agency,
            presol_type=presol_type,
            contact_name=contact_name,
            contact_email=contact_email,
            deadline=deadline,
        )
        
        checklist_path = os.path.join(base_path, 'WORKFLOW_CHECKLIST.md')
        with open(checklist_path, 'w') as f:
            f.write(checklist)
        
        print(f"   ✅ Auto-response complete for: {folder_name}")
        print(f"   📬 SEND_TO_BUYER ready — email {contact_email or 'CO'} with cap statement attached")

    def _generate_folder_name(self, agency: str, title: str) -> str:
        """Generate a short, readable folder name from agency + title.
        Format: [AGENCY ABBREVIATION] [KEY WORDS FROM TITLE]
        Examples: USACE GUARDRAILS, VA COURIER SERVICE, DLA CABLE ASSEMBLY
        """
        import re
        
        # Full agency path might be like "DEPARTMENT OF THE ARMY.US ARMY CORPS OF ENGINEERS.WHATEVER"
        # We want to check the ENTIRE string for abbreviation matches
        agency_upper = agency.upper().strip()
        
        # Common abbreviations — check from most specific to least specific
        abbrevs = [
            ('ARMY CORPS OF ENGINEERS', 'USACE'),
            ('CORPS OF ENGINEERS', 'USACE'),
            ('DEFENSE LOGISTICS AGENCY', 'DLA'),
            ('NAVAL SUPPLY SYSTEMS COMMAND', 'NAVSUP'),
            ('NAVAL SEA SYSTEMS COMMAND', 'NAVSEA'),
            ('NAVAL AIR SYSTEMS COMMAND', 'NAVAIR'),
            ('NATIONAL INSTITUTES OF HEALTH', 'NIH'),
            ('FISH AND WILDLIFE SERVICE', 'FWS'),
            ('BUREAU OF RECLAMATION', 'BOR'),
            ('GENERAL SERVICES ADMINISTRATION', 'GSA'),
            ('NATIONAL AERONAUTICS AND SPACE', 'NASA'),
            ('VETERANS AFFAIRS', 'VA'),
            ('VETERAN AFFAIRS', 'VA'),
            ('DEPARTMENT OF ENERGY', 'DOE'),
            ('HOMELAND SECURITY', 'DHS'),
            ('DEPARTMENT OF THE ARMY', 'ARMY'),
            ('DEPARTMENT OF THE NAVY', 'NAVY'),
            ('DEPARTMENT OF THE AIR FORCE', 'USAF'),
            ('DEPARTMENT OF DEFENSE', 'DOD'),
            ('DEPARTMENT OF AGRICULTURE', 'USDA'),
            ('DEPARTMENT OF INTERIOR', 'DOI'),
            ('DEPARTMENT OF COMMERCE', 'DOC'),
            ('DEPARTMENT OF LABOR', 'DOL'),
            ('DEPARTMENT OF JUSTICE', 'DOJ'),
            ('DEPARTMENT OF STATE', 'DOS'),
            ('SMALL BUSINESS ADMINISTRATION', 'SBA'),
            ('ENVIRONMENTAL PROTECTION AGENCY', 'EPA'),
            ('FEDERAL EMERGENCY MANAGEMENT', 'FEMA'),
            ('INSTALLATION MANAGEMENT COMMAND', 'IMCOM'),
            ('MISSION AND INSTALLATION CONTRACTING', 'MICC'),
        ]
        
        short = ''
        for full, abbr in abbrevs:
            if full in agency_upper:
                short = abbr
                break
        
        # If no match, take the last segment of the dotted path and use first word
        if not short:
            last_segment = agency.split('.')[-1].strip() if '.' in agency else agency
            last_segment = last_segment.split('/')[-1].strip()
            words = last_segment.upper().split()
            short = words[0] if words else 'FEDERAL'
        
        # Extract key words from title (remove filler words and notice-type words)
        filler_pattern = r'(?i)\b(sources?\s*sought|presolicitation|notice\s*of\s*intent|combined\s*synopsis|solicitation|amendment|modification|rfp|rfq|rfi|for|the|and|of|at|in|to|a|an|is|are|be|was|were|this|that|with|from|by|on|or|not|as|it|its|has|have|had|will|shall|may|can|all|any|each|per|but)\b'
        title_clean = re.sub(filler_pattern, ' ', title)
        title_clean = re.sub(r'[^a-zA-Z0-9\s]', '', title_clean)
        title_words = [w for w in title_clean.upper().split() if len(w) > 2][:3]
        
        folder_name = f"{short} {' '.join(title_words)}".strip()
        
        # Cap at 30 chars
        if len(folder_name) > 30:
            folder_name = folder_name[:30].strip()
        
        return folder_name

    def _generate_presol_capstat_html(self, title: str, notice_id: str, agency: str,
                                       presol_type: str, description: str, set_aside: str,
                                       naics: str) -> str:
        """Generate a tailored capability statement HTML for presolicitation response."""
        
        # Determine color scheme based on industry keywords
        title_lower = title.lower() + ' ' + description.lower()
        if any(kw in title_lower for kw in ['ground', 'landscape', 'lawn', 'mow', 'vegetation', 'tree', 'environmental']):
            primary_color = '#14532d'
            accent_color = '#d97706'
            industry_label = 'Grounds Maintenance & Environmental Services'
        elif any(kw in title_lower for kw in ['medical', 'health', 'clinical', 'hospital', 'pharma', 'surgical', 'courier']):
            primary_color = '#1e40af'
            accent_color = '#dc2626'
            industry_label = 'Medical & Healthcare Services'
        elif any(kw in title_lower for kw in ['construction', 'building', 'repair', 'renovation', 'facility']):
            primary_color = '#7c2d12'
            accent_color = '#ea580c'
            industry_label = 'Construction & Facility Services'
        elif any(kw in title_lower for kw in ['it ', 'software', 'technology', 'cyber', 'network', 'computer']):
            primary_color = '#312e81'
            accent_color = '#7c3aed'
            industry_label = 'Information Technology Services'
        elif any(kw in title_lower for kw in ['supply', 'equipment', 'material', 'product', 'part', 'hardware']):
            primary_color = '#0c4a6e'
            accent_color = '#0284c7'
            industry_label = 'Supply Chain & Equipment Procurement'
        else:
            primary_color = '#1e3a5f'
            accent_color = '#d4a017'
            industry_label = 'Federal Service Management & Contract Administration'
        
        # Determine response framing based on type
        if presol_type == 'Intent to Sole Source':
            type_label = 'EDWOSB ALTERNATIVE RESPONSE'
            type_desc = f'Notice of Intent to Sole Source: {notice_id}'
        elif presol_type == 'Sources Sought':
            type_label = 'SOURCES SOUGHT RESPONSE'
            type_desc = f'Sources Sought Notice: {notice_id}'
        else:
            type_label = 'EDWOSB INTEREST — CAPABILITY STATEMENT'
            type_desc = f'Presolicitation: {notice_id}'
        
        # Set-aside badge
        set_aside_html = ''
        if set_aside:
            set_aside_html = f'<div class="badge">{set_aside}</div>'
        
        from datetime import datetime
        date_str = datetime.now().strftime('%B %Y')
        
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DEE DAVIS INC - Capability Statement - {notice_id}</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Inter', -apple-system, sans-serif; line-height: 1.6; color: #1e293b; background: white; -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
        .page {{ width: 8.5in; min-height: 11in; margin: 0 auto; padding: 0.75in; background: white; }}
        .header {{ background: linear-gradient(135deg, {primary_color} 0%, {primary_color}dd 100%); color: white; padding: 2rem; border-radius: 12px; margin-bottom: 1.5rem; box-shadow: 0 4px 6px rgba(0,0,0,0.2); display: flex; align-items: flex-start; gap: 2rem; }}
        .logo-section {{ flex-shrink: 0; width: 130px; height: 130px; background: white; border-radius: 12px; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 12px rgba(0,0,0,0.2); padding: 0.75rem; }}
        .logo-img {{ width: 100%; height: 100%; object-fit: contain; }}
        .header-content {{ flex: 1; }}
        .company-name {{ font-size: 2.25rem; font-weight: 800; letter-spacing: -0.5px; margin-bottom: 0.25rem; }}
        .dba {{ font-size: 1rem; font-weight: 500; opacity: 0.9; margin-bottom: 0.75rem; }}
        .cage-uei {{ display: flex; gap: 1.5rem; font-size: 0.8rem; font-weight: 600; margin-bottom: 0.75rem; padding: 0.6rem 1rem; background: rgba(255,255,255,0.15); border-radius: 6px; }}
        .cage-uei-item {{ display: flex; gap: 0.5rem; }}
        .badges {{ display: flex; gap: 0.75rem; margin-top: 0.75rem; flex-wrap: wrap; }}
        .badge {{ background: rgba(255,255,255,0.2); padding: 0.4rem 1rem; border-radius: 20px; font-size: 0.8rem; font-weight: 600; border: 1px solid rgba(255,255,255,0.3); }}
        .title-bar {{ background: linear-gradient(135deg, {accent_color} 0%, {accent_color}cc 100%); color: white; padding: 1rem 1.5rem; border-radius: 8px; margin-bottom: 1.5rem; text-align: center; }}
        .title-bar h2 {{ font-size: 1.3rem; font-weight: 700; }}
        .title-bar .sol {{ font-size: 0.95rem; margin-top: 0.25rem; opacity: 0.95; }}
        .section {{ margin-bottom: 1.5rem; }}
        .section-header {{ background: linear-gradient(135deg, {primary_color} 0%, {primary_color}dd 100%); color: white; padding: 0.6rem 1.25rem; border-radius: 8px; font-size: 1.05rem; font-weight: 700; margin-bottom: 0.75rem; }}
        .info-box {{ background: #f8fafc; border-left: 4px solid {primary_color}; padding: 1rem 1.25rem; border-radius: 8px; margin-bottom: 1rem; font-size: 0.9rem; }}
        .highlight-box {{ background: linear-gradient(135deg, #ecfdf5, #d1fae5); border-left: 4px solid #10b981; padding: 1rem 1.25rem; border-radius: 8px; margin-bottom: 1rem; }}
        .edwosb-box {{ background: linear-gradient(135deg, #fef3c7, #fde68a); border-left: 4px solid #d97706; padding: 1rem 1.25rem; border-radius: 8px; margin-bottom: 1rem; }}
        .key-points {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 0.75rem; margin: 1rem 0; }}
        .key-point {{ background: white; border: 2px solid #e2e8f0; padding: 0.75rem; border-radius: 8px; display: flex; align-items: start; gap: 0.75rem; }}
        .key-point-icon {{ font-size: 1.25rem; flex-shrink: 0; }}
        .key-point h4 {{ font-weight: 700; color: {primary_color}; font-size: 0.85rem; margin-bottom: 0.1rem; }}
        .key-point p {{ font-size: 0.78rem; color: #64748b; }}
        ul {{ list-style: none; padding: 0; }}
        ul li {{ padding-left: 1.5rem; position: relative; margin-bottom: 0.4rem; font-size: 0.9rem; }}
        ul li::before {{ content: "\\2713"; position: absolute; left: 0; color: #10b981; font-weight: bold; }}
        .contact-grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 0.75rem; background: #f1f5f9; padding: 1.25rem; border-radius: 8px; margin-top: 1rem; }}
        .contact-item {{ display: flex; align-items: center; gap: 0.75rem; }}
        .contact-label {{ font-size: 0.7rem; color: #64748b; font-weight: 600; text-transform: uppercase; }}
        .contact-value {{ font-size: 0.9rem; font-weight: 600; color: #1e293b; }}
        .footer {{ margin-top: 2rem; padding-top: 1.5rem; border-top: 2px solid #e2e8f0; text-align: center; color: #64748b; font-size: 0.85rem; }}
        .footer strong {{ color: {primary_color}; }}
        @media print {{ .page {{ margin: 0; padding: 0.5in; }} }}
    </style>
</head>
<body>
<div class="page">
    <div class="header">
        <div class="logo-section">
            <img src="dee_davis_inc_logo.png" alt="Dee Davis Inc. Logo" class="logo-img">
        </div>
        <div class="header-content">
            <div class="company-name">DEE DAVIS INC</div>
            <div class="dba">{industry_label}</div>
            <div class="cage-uei">
                <div class="cage-uei-item"><span style="opacity:0.8">CAGE Code:</span> <span>8UMX3</span></div>
                <div class="cage-uei-item"><span style="opacity:0.8">UEI:</span> <span>HJB4KNYJVGZ1</span></div>
                <div class="cage-uei-item"><span style="opacity:0.8">SAM.gov:</span> <span>ACTIVE</span></div>
            </div>
            <div class="badges">
                <div class="badge">EDWOSB/WOSB Certified</div>
                <div class="badge">WBE / MBE / SBE</div>
                {set_aside_html}
            </div>
        </div>
    </div>

    <div class="title-bar">
        <h2>{type_label}</h2>
        <div class="sol">{type_desc}</div>
        <div class="sol">{title[:100]}</div>
    </div>

    <div class="edwosb-box">
        <h3 style="color:#92400e;font-weight:700;margin-bottom:0.5rem;">EDWOSB CERTIFICATION ADVANTAGE</h3>
        <p style="font-size:0.9rem;">Dee Davis Inc. is a <strong>certified EDWOSB/WOSB</strong>. Our certification provides socioeconomic contracting value and supports the federal government's 5% WOSB contracting goal.</p>
    </div>

    <div class="section">
        <div class="section-header">COMPANY OVERVIEW</div>
        <div class="info-box">
            <p><strong>Dee Davis Inc.</strong> is an EDWOSB/WOSB-certified service management firm and licensed freight brokerage specializing in federal contract administration, supply chain management, and subcontractor coordination. We serve as prime contractor on federal contracts, partnering with qualified local contractors and suppliers while managing compliance, quality assurance, and government reporting.</p>
        </div>
    </div>

    <div class="section">
        <div class="section-header">KEY QUALIFICATIONS</div>
        <div class="key-points">
            <div class="key-point">
                <div class="key-point-icon">&#127942;</div>
                <div><h4>EDWOSB/WOSB Certified</h4><p>Meets set-aside requirements, supports 5% WOSB goal</p></div>
            </div>
            <div class="key-point">
                <div class="key-point-icon">&#128203;</div>
                <div><h4>Contract Administration</h4><p>Compliance, QA, invoicing, government reporting</p></div>
            </div>
            <div class="key-point">
                <div class="key-point-icon">&#128666;</div>
                <div><h4>Licensed Freight Broker</h4><p>FMCSA MC# 1647572, 20+ carrier network</p></div>
            </div>
            <div class="key-point">
                <div class="key-point-icon">&#9989;</div>
                <div><h4>Federal Contracting Ready</h4><p>CAGE 8UMX3, SAM.gov Active, immediate capacity</p></div>
            </div>
            <div class="key-point">
                <div class="key-point-icon">&#129309;</div>
                <div><h4>Subcontractor Network</h4><p>Vetted local partners for service delivery</p></div>
            </div>
            <div class="key-point">
                <div class="key-point-icon">&#128200;</div>
                <div><h4>Multi-Site Coordination</h4><p>Route planning and scheduling across locations</p></div>
            </div>
        </div>
    </div>

    {"<div class='section'><div class='section-header'>NAICS CODES</div><div class='info-box'><p><strong>" + naics + "</strong></p></div></div>" if naics else ""}

    <div class="contact-grid">
        <div class="contact-item"><div><div class="contact-label">Email</div><div class="contact-value">info@deedavis.biz</div></div></div>
        <div class="contact-item"><div><div class="contact-label">Phone</div><div class="contact-value">248.376.4550</div></div></div>
        <div class="contact-item"><div><div class="contact-label">Address</div><div class="contact-value">755 W. Big Beaver Rd., Suite 2020<br>Troy, Michigan 48084</div></div></div>
        <div class="contact-item"><div><div class="contact-label">Certifications</div><div class="contact-value">EDWOSB / WOSB / WBE / MBE / SBE</div></div></div>
    </div>

    <div class="footer">
        <p><strong>Dee Davis Inc.</strong> | {industry_label}</p>
        <p>755 W. Big Beaver Rd., Suite 2020 | Troy, Michigan 48084</p>
        <p>Phone: 248.376.4550 | Email: info@deedavis.biz | Web: www.deedavis.biz</p>
        <p style="margin-top:0.75rem"><strong>EDWOSB/WOSB Certified</strong> | CAGE Code: 8UMX3 | UEI: HJB4KNYJVGZ1</p>
        <p style="margin-top:0.75rem;font-size:0.75rem;color:#94a3b8">{type_label} — {notice_id} | {date_str}</p>
    </div>
</div>
</body>
</html>'''

    def _generate_presol_buyer_email(self, title: str, notice_id: str, agency: str,
                                      presol_type: str, contact_name: str, contact_email: str,
                                      contact_phone: str, set_aside: str, description: str) -> str:
        """Generate buyer outreach email for presolicitation response."""
        from datetime import datetime
        
        # Parse contact name for greeting
        if contact_name:
            # Try to get last name for formal greeting
            parts = contact_name.split()
            if len(parts) >= 2:
                greeting = f"Dear {parts[-1]},"  # Use last name
                greeting_alt = f"Good evening {parts[0]},"  # First name
            else:
                greeting = f"Dear {contact_name},"
                greeting_alt = greeting
        else:
            greeting = "Good evening,"
            greeting_alt = greeting
        
        # Frame based on type
        if presol_type == 'Intent to Sole Source':
            subject = f"EDWOSB Alternative — {title[:60]} ({notice_id})"
            intro = f"I'm writing to submit our capability as a certified EDWOSB alternative regarding {presol_type.lower()} notice {notice_id}."
            questions = """- We respectfully submit our qualification as an EDWOSB alternative
- We can provide competitive pricing through our supplier/subcontractor network
- Our EDWOSB certification provides additional socioeconomic contracting value
- We are prepared to demonstrate full technical capability"""
        elif presol_type == 'Sources Sought':
            subject = f"EDWOSB Capability Response — {title[:60]} ({notice_id})"
            intro = f"I'm writing to express our strong interest and capability regarding Sources Sought notice {notice_id}."
            questions = """- What is the anticipated procurement timeline?
- Will this be set aside for small business / WOSB / EDWOSB?
- Will there be a site visit or pre-bid conference?
- Can we be added to the interested vendors list for this procurement?"""
        else:
            subject = f"EDWOSB Interest — {title[:60]} ({notice_id})"
            intro = f"I'm writing to express our strong interest in the upcoming solicitation referenced in presolicitation {notice_id}."
            questions = """- Is the anticipated timeline still on track for the full solicitation release?
- Will there be a site visit or pre-bid conference?
- Are there capability requirements beyond the presolicitation notice?
- Can we be added to the interested vendors list for this procurement?"""
        
        email = f"""# READY TO SEND — {presol_type} Response

**To:** {contact_email or '[CO EMAIL]'}
**From:** info@deedavis.biz
**Subject:** {subject}

---

{greeting_alt}

My name is Dee Davis, owner of Dee Davis Inc., a certified EDWOSB based in Troy, Michigan. {intro}

We are a service management firm and licensed freight brokerage that partners with qualified local contractors and suppliers to deliver on federal contracts. We handle contract management, compliance, invoicing, and quality assurance while our partners handle execution.

{questions}

I've attached our Capability Statement for your review, which outlines our company qualifications, EDWOSB certification, and relevant experience.

We're genuinely excited about this opportunity and look forward to competing. Thank you for your time, and please don't hesitate to reach out if you have any questions about our company.

Best regards,

Dee Davis
Owner, Dee Davis Inc.
755 W. Big Beaver Rd., Suite 2020
Troy, Michigan 48084
Phone: 248.376.4550
Email: info@deedavis.biz

EDWOSB / WOSB Certified
CAGE Code: 8UMX3 | UEI: HJB4KNYJVGZ1
SAM.gov Active

---

## BEFORE SENDING — CHECKLIST
- [ ] Copy everything between the --- lines above
- [ ] Paste into email
- [ ] To: {contact_email or '[FIND CO EMAIL]'}
- [ ] Subject: {subject}
- [ ] ATTACH: Capability statement (open HTML in browser > Print > Save as PDF)
- [ ] Double-check signature
- [ ] SEND

## CO CONTACT INFO
- **Name:** {contact_name or 'TBD'}
- **Email:** {contact_email or 'TBD'}
- **Phone:** {contact_phone or 'TBD'}
- **Agency:** {agency}

---
*Auto-generated by Nexus — {presol_type} response for {notice_id} | {datetime.now().strftime('%B %d, %Y')}*
"""
        return email

    def _generate_presol_workflow_checklist(self, title: str, notice_id: str, agency: str,
                                             presol_type: str, contact_name: str,
                                             contact_email: str, deadline: str) -> str:
        """Generate workflow checklist for presolicitation response."""
        from datetime import datetime
        
        return f"""# WORKFLOW CHECKLIST — {presol_type}
## {title[:80]}
## {notice_id}

**Agency:** {agency}
**Type:** {presol_type}
**Deadline:** {deadline or 'TBD'}
**CO:** {contact_name or 'TBD'} ({contact_email or 'TBD'})
**Created:** {datetime.now().strftime('%B %d, %Y')} (auto-generated by Nexus)

---

## STEP 1: REVIEW NOTICE
- [ ] Read and understand what the buyer is signaling
- [ ] Identify NAICS code, set-aside type, estimated value
- [ ] Note any specific capability requirements
- [ ] Check if EDWOSB/WOSB set-aside (HIGH PRIORITY if yes)

## STEP 2: GO / NO-GO DECISION
- [x] AUTO-PURSUE: {presol_type} identified — default is YES for EDWOSB-eligible
- [ ] Dee confirms pursuit (or kills it)

## STEP 3: GENERATE CAP STATEMENT (AUTO-COMPLETE)
- [x] Capability statement generated and placed in SEND_TO_BUYER/
- [x] Tailored to opportunity type and industry

## STEP 4: GENERATE BUYER EMAIL (AUTO-COMPLETE)
- [x] Buyer outreach email generated and placed in SEND_TO_BUYER/
- [x] CO contact info populated: {contact_name or 'TBD'} ({contact_email or 'TBD'})

## STEP 5: SEND TO BUYER
- [ ] Review cap statement (open HTML, print to PDF)
- [ ] Review email text
- [ ] Send email to {contact_email or 'CO'} with cap statement attached
- [ ] Log send date

## STEP 6: MONITOR FOR FULL RFP
- [ ] Watch SAM.gov for full solicitation release
- [ ] Set alert for {notice_id}
- [ ] Check email for CO response / follow-up questions

## STEP 7: IDENTIFY SUPPLIERS / SUBCONTRACTORS
- [ ] Research local suppliers/subcontractors for this contract
- [ ] Make initial outreach calls (protect buyer identity!)
- [ ] Document capabilities and pricing

## STEP 8: FULL BID (When RFP Drops)
- [ ] Download complete RFP from SAM.gov
- [ ] Switch to regular bid workflow (10-step)
- [ ] Request formal quotes from suppliers/subs
- [ ] Prepare and submit full proposal

---

*Auto-generated by Nexus presolicitation auto-response system*
"""


class GovConAPIClient:
    """GovCon API Client - Free tier: 25 requests/day, 50 results max"""
    
    def __init__(self):
        self.api_key = os.environ.get('GOVCON_API_KEY', '')
        self.base_url = "https://govconapi.com/api/v1/opportunities/search"
        self.airtable = AirtableClient()
    
    def search_opportunities(self, params: Dict = None) -> Dict:
        """Search GovCon - Free plan has basic filters only"""
        try:
            # Check for API key first
            if not self.api_key:
                error_msg = "❌ GOVCON_API_KEY environment variable not set!"
                print(error_msg)
                print("   Please add GOVCON_API_KEY to your .env file")
                print("   Get your API key from: https://govconapi.com")
                return {
                    'success': False, 
                    'error': 'GOVCON_API_KEY not configured', 
                    'total_found': 0, 
                    'imported': 0
                }
            
            headers = {'Authorization': f'Bearer {self.api_key}'}
            
            # Strategy: Make two calls to get both Solicitation and Combined Synopsis/Solicitation
            # The docs say ~33% of opportunities are combined type
            all_opportunities = []
            total_found = 0
            
            notice_types = [
                'Solicitation', 
                'Combined Synopsis/Solicitation',
                'Presolicitation',
                'Sources Sought',
                'Special Notice',
            ]
            
            for notice_type in notice_types:
                # Free plan: limit=50 max, basic filters only
                search_params = {
                    'limit': 50,  # Free plan max
                    'notice_type': notice_type
                }
                
                # Allow custom params to override defaults
                if params:
                    search_params.update(params)
                
                print(f"🔍 Searching GovCon API: {notice_type}...")
                print(f"   Request URL: {self.base_url}")
                print(f"   Parameters: {search_params}")
                
                response = requests.get(self.base_url, headers=headers, params=search_params, timeout=30)
                
                print(f"   Response Status: {response.status_code}")
                
                if response.status_code != 200:
                    print(f"   Response Body: {response.text[:500]}")
                
                response.raise_for_status()
                
                data = response.json()
                opportunities = data.get('data', [])
                batch_total = data.get('pagination', {}).get('total', 0)
                
                print(f"   ✓ Found {batch_total} total ({len(opportunities)} retrieved for {notice_type})")
                
                all_opportunities.extend(opportunities)
                total_found += batch_total
            
            if len(all_opportunities) == 0:
                print("   ⚠️ No opportunities found. Check your API key and parameters.")
            else:
                print(f"\n   📊 Combined Results: {total_found} total across both notice types")
                print(f"   📦 Retrieved {len(all_opportunities)} opportunities to process")
            
            imported_count = 0
            skipped_duplicates = 0
            errors = []
            
            print(f"\n   💾 Importing to Airtable...")
            for idx, opp in enumerate(all_opportunities, 1):
                try:
                    notice_id = opp.get('notice_id', opp.get('solicitation_number', ''))
                    title = opp.get('title', 'Untitled')[:30]
                    
                    if not self._is_duplicate(notice_id):
                        self._import_to_airtable(opp)
                        imported_count += 1
                        if idx <= 3 or imported_count == 1:  # Show first few successes
                            print(f"   ✓ [{idx}] Imported: {title}...")
                    else:
                        skipped_duplicates += 1
                        if skipped_duplicates <= 2:  # Show first few duplicates
                            print(f"   ⏭️  [{idx}] Skipped duplicate: {title}...")
                except Exception as e:
                    error_detail = f"[{idx}] {notice_id or title}: {str(e)}"
                    errors.append(error_detail)
                    if len(errors) <= 5:  # Show first 5 errors in detail
                        print(f"   ❌ {error_detail}")
                    continue
            
            print(f"\n   ✅ IMPORT COMPLETE")
            print(f"   ✓ Imported {imported_count} new opportunities")
            if skipped_duplicates > 0:
                print(f"   ⏭️  Skipped {skipped_duplicates} duplicates")
            if errors:
                print(f"   ⚠️ Encountered {len(errors)} errors during import")
            
            return {
                'success': True, 
                'total_found': total_found, 
                'retrieved': len(all_opportunities),
                'imported': imported_count,
                'duplicates': skipped_duplicates,
                'errors': len(errors),
                'source': 'GovCon API'
            }
        except requests.exceptions.HTTPError as e:
            error_msg = f"HTTP Error: {e.response.status_code} - {e.response.text[:500]}"
            print(f"❌ GovCon API Error: {error_msg}")
            return {'success': False, 'error': error_msg, 'total_found': 0, 'imported': 0}
        except requests.exceptions.RequestException as e:
            error_msg = f"Request Error: {str(e)}"
            print(f"❌ GovCon Network Error: {error_msg}")
            return {'success': False, 'error': error_msg, 'total_found': 0, 'imported': 0}
        except Exception as e:
            error_msg = f"Unexpected Error: {str(e)}"
            print(f"❌ GovCon Error: {error_msg}")
            import traceback
            traceback.print_exc()
            return {'success': False, 'error': error_msg, 'total_found': 0, 'imported': 0}
    
    def _is_duplicate(self, notice_id: str) -> bool:
        try:
            records = self.airtable.get_all_records('GPSS OPPORTUNITIES')
            return any(r['fields'].get('RFP NUMBER') == notice_id for r in records)
        except:
            return False
    
    def _import_to_airtable(self, opp: Dict):
        from dateutil import parser
        
        # Parse dates safely
        due_date = ''
        posted_date = ''
        try:
            if opp.get('response_deadline'):
                due_date = parser.parse(opp['response_deadline']).strftime('%Y-%m-%d')
            if opp.get('posted_date'):
                posted_date = parser.parse(opp['posted_date']).strftime('%Y-%m-%d')
        except:
            pass
        
        # Get performance location
        perf_state = opp.get('performance_state_code', '')
        
        # Get notice type for tracking
        notice_type = opp.get('notice_type', '')
        
        # Build description with key info
        agency = opp.get('agency', '')
        set_aside = opp.get('set_aside_type', '')
        naics = ','.join(opp.get('naics', [])) if isinstance(opp.get('naics'), list) and opp.get('naics') else ''
        sam_url = opp.get('sam_url', '')
        description_parts = []
        if agency:
            description_parts.append(f"Agency: {agency}")
        if set_aside:
            description_parts.append(f"Set-Aside: {set_aside}")
        if naics:
            description_parts.append(f"NAICS: {naics}")
        if perf_state:
            description_parts.append(f"State: {perf_state}")
        if sam_url:
            description_parts.append(f"URL: {sam_url}")
        description = opp.get('description_text', '') or ' | '.join(description_parts)
        
        # Map to EXACT Airtable field names (as they exist in the table)
        fields = {
            'Name': opp.get('title', 'Untitled')[:255],
            'RFP NUMBER': opp.get('notice_id', opp.get('solicitation_number', '')),
            'Status': 'New - API',
            'Source': 'GovCon API',
        }
        
        # Add optional fields only if they have values
        if agency:
            fields['AGENCY'] = agency[:255]
        if description:
            fields['Notes'] = description[:2000]
        if set_aside:
            fields['Set-Aside Type'] = set_aside[:100]
        if naics:
            fields['NAISC Codes'] = naics[:100]
        if perf_state:
            fields['State'] = perf_state[:50]
        if sam_url:
            fields['Source URL'] = sam_url[:500]
        if due_date:
            fields['Deadline'] = due_date
        
        # Debug: print what we're saving (first few times)
        if not hasattr(self, '_debug_count'):
            self._debug_count = 0
        if self._debug_count < 3:
            print(f"      DEBUG - Saving fields: {list(fields.keys())}")
            if agency:
                print(f"      DEBUG - AGENCY value: {agency[:50]}")
            self._debug_count += 1

        # Research Lane detection — tag if community health / market research
        research_tags = ResearchLaneDetector().detect(
            title=opp.get('title', ''),
            description=opp.get('description_text', '') or opp.get('description', ''),
            agency=agency,
            naics=naics,
        )
        if research_tags:
            fields.update(research_tags)
            print(f"   🔬 Research Lane: {research_tags.get('Research Subtype')} — {opp.get('title','')[:60]}")

        self.airtable.create_record('GPSS OPPORTUNITIES', fields)


# =============================================================================
# RESEARCH LANE DETECTOR
# Bridges GPSS (contracts) and GBIS (grants) for the Community Health &
# Market Research lane. Auto-tags opportunities and assigns applicant entity.
# =============================================================================

class ResearchLaneDetector:
    """
    Detects whether an incoming opportunity (contract or grant) belongs to
    the Community Health & Market Research lane, and determines whether
    DDI or Cause We Care should be the applicant.

    Called by GPSS _import_to_airtable (contracts) and
    GBIS _import_to_airtable (grants) to tag records consistently.
    """

    RESEARCH_NAICS = {'541910', '541720', '624190', '621999', '541611',
                      '541690', '624230', '541720'}

    RESEARCH_AGENCIES = [
        'HHS', 'HRSA', 'SAMHSA', 'NIH', 'NIMHD', 'USDA FNS', 'ACF',
        'ASPE', 'CMS', 'SBA', 'MBDA', 'MDHHS',
        'Health and Human Services', 'Health Resources',
        'Substance Abuse', 'Food and Nutrition',
        'Administration for Children', 'Medicaid',
    ]

    RESEARCH_KEYWORDS = [
        'community health', 'needs assessment', 'program evaluation',
        'market research', 'survey research', 'public opinion',
        'benefits access', 'social determinants', 'sdoh',
        'snap outreach', 'snap enrollment', 'food insecurity',
        'medicaid access', 'medicaid enrollment', 'navigator',
        'behavioral health', 'substance abuse evaluation',
        'small business research', 'diversity research', 'wosb study',
        'health disparities', 'underserved communities', 'health equity',
        'community assessment', 'population health', 'public health',
        'community-based', 'community outreach', 'lead testing',
        'social services', 'human services', 'welfare program',
        'housing instability', 'homelessness research', 'coordinated entry',
        'minority health', 'health screening', 'health data',
    ]

    # Funders that indicate Cause We Care (nonprofit) should be the applicant
    CWC_FUNDERS = [
        'NIH', 'NIMHD', 'HRSA', 'SAMHSA', 'USDA FNS', 'HUD', 'ACF',
        'ASPE', 'CMS', 'MDHHS', 'Kresge', 'Robert Wood Johnson',
        'W.K. Kellogg', 'Michigan Health Endowment', 'Community Foundation',
        'Ralph C. Wilson', 'United Way',
    ]

    CWC_GRANT_KEYWORDS = [
        '501(c)(3)', 'nonprofit', 'non-profit', 'community-based organization',
        'cbo', 'charitable', 'foundation grant', 'community grant',
    ]

    def detect(self, title: str = '', description: str = '',
               agency: str = '', naics: str = '') -> dict:
        """
        Returns a dict of extra fields to add to Airtable if the opportunity
        matches the Community Health & Research lane, otherwise returns {}.

        Usage:
            extra = ResearchLaneDetector().detect(
                title=opp.get('title',''),
                description=opp.get('description',''),
                agency=opp.get('agency',''),
                naics=opp.get('naicsCode',''),
            )
            if extra:
                fields.update(extra)
        """
        text = f"{title} {description}".lower()
        naics_clean = str(naics).replace(',', ' ')

        naics_match = any(n in naics_clean for n in self.RESEARCH_NAICS)
        agency_match = any(a.lower() in agency.lower() for a in self.RESEARCH_AGENCIES)
        keyword_match = any(kw in text for kw in self.RESEARCH_KEYWORDS)

        if not (naics_match or agency_match or keyword_match):
            return {}

        subtype = self._detect_subtype(text)

        return {
            'Service Lane': 'Community Health & Research',
            'Research Subtype': subtype,
        }

    def assign_applicant_entity(self, funder: str = '',
                                description: str = '') -> str:
        """
        Determines whether DDI or Cause We Care should apply for a GBIS grant.
        Used only by GBIS — GPSS contracts always default to DDI.
        """
        funder_lower = funder.lower()
        desc_lower = description.lower()
        combined = f"{funder_lower} {desc_lower}"

        is_cwc = (
            any(f.lower() in combined for f in self.CWC_FUNDERS) or
            any(kw in combined for kw in self.CWC_GRANT_KEYWORDS)
        )
        is_ddi = any(kw in combined for kw in [
            'for-profit', 'small business', 'woman-owned', 'edwosb', 'wosb',
            'small business set-aside', 'sbir', 'sttr',
        ])

        if is_cwc and is_ddi:
            return 'DDI + Cause We Care (Teaming)'
        elif is_cwc:
            return 'Cause We Care'
        else:
            return 'DDI'

    def _detect_subtype(self, text: str) -> str:
        if any(kw in text for kw in ['needs assessment', 'community health assessment',
                                      'health disparities', 'sdoh', 'social determinants',
                                      'population health', 'health screening']):
            return 'Community Health Assessment'
        if any(kw in text for kw in ['program evaluation', 'effectiveness', 'outcome',
                                      'performance evaluation', 'impact evaluation']):
            return 'Program Evaluation'
        if any(kw in text for kw in ['snap', 'benefits access', 'medicaid access',
                                      'enrollment barrier', 'navigator', 'food insecurity',
                                      'mibridges', 'benefits enrollment']):
            return 'Benefits Access Research'
        if any(kw in text for kw in ['small business research', 'diversity research',
                                      'wosb study', 'edwosb', 'mbda', 'minority business',
                                      'woman-owned research']):
            return 'SB/Diversity Research'
        return 'Survey / Market Research'


def handle_sam_api_search(params: Dict = None) -> Dict:
    """Handler for SAM.gov API search"""
    client = SAMgovAPIClient()
    return client.search_opportunities(params)


def handle_govcon_api_search(params: Dict = None) -> Dict:
    """Handler for GovCon API search"""
    client = GovConAPIClient()
    return client.search_opportunities(params)


# =============================================================================
# STATE & LOCAL OPPORTUNITY MINER
# =============================================================================

class StateLocalMiner:
    """
    State and Local Government Opportunity Miner
    Web scraping for state/local portals and aggregators
    """
    
    # State portal configurations
    STATE_PORTALS = {
        'California': {
            'name': 'Cal eProcure',
            'url': 'https://caleprocure.ca.gov/pages/index.aspx',
            'enabled': True
        },
        'Texas': {
            'name': 'ESBD (Texas)',
            'url': 'https://www.txsmartbuy.com/sp',
            'enabled': True
        },
        'Florida': {
            'name': 'MyFloridaMarketPlace',
            'url': 'https://www.myfloridamarketplace.com',
            'enabled': True
        },
        'New York': {
            'name': 'NYS Contract Reporter',
            'url': 'https://www.nyscr.ny.gov',
            'enabled': True
        },
        'Michigan': {
            'name': 'SIGMA VSS',
            'url': 'https://www.michigan.gov/sigmavss',
            'enabled': True
        }
    }
    
    # Aggregator portals (free access)
    AGGREGATORS = {
        'BidNet': {
            'url': 'https://www.bidnetdirect.com/bidnet-government-bids',
            'enabled': True
        },
        'PublicPurchase': {
            'url': 'https://www.publicpurchase.com',
            'enabled': True
        },
        'GovSpend': {
            'url': 'https://www.govspend.com',
            'rss': 'https://www.govspend.com/opportunities.rss',
            'enabled': True
        },
        'InstantMarkets': {
            'url': 'https://www.instantmarkets.com',
            'search_categories': [
                'Vehicle', 'Truck', 'Landscape', 'Snow_Removal',
                'Cleaning_Supplies', 'Janitorial_Services', 'Chemicals',
                'Salt', 'Healthcare', 'Medical', 'Furniture',
                'Uniforms', 'Tools', 'Fabricated_Metal',
                'Highway', 'Building', 'Construction',
                'Plumber', 'Electrician', 'Waste_Management'
            ],
            'enabled': True
        },
        'SkysTheLimit': {
            'url': 'https://www.skysthelimit.org',
            'description': 'FREE GBIS - Government Bid Information System',
            'enabled': True
        }
    }
    
    def __init__(self):
        self.airtable = AirtableClient()
        self.anthropic_client = anthropic.Anthropic(api_key=Config.get_anthropic_key())
    
    def mine_all_sources(self) -> Dict:
        """Mine all enabled state/local sources"""
        results = {
            'success': True,
            'sources_checked': 0,
            'total_found': 0,
            'imported': 0,
            'errors': []
        }
        
        print("🏛️  Mining State & Local Opportunities...")
        
        # Try PublicPurchase first (good free aggregator)
        try:
            pp_result = self._mine_publicpurchase()
            results['sources_checked'] += 1
            results['total_found'] += pp_result['found']
            results['imported'] += pp_result['imported']
        except Exception as e:
            results['errors'].append(f"PublicPurchase: {str(e)}")
        
        # Try BidNet Direct
        try:
            bn_result = self._mine_bidnet()
            results['sources_checked'] += 1
            results['total_found'] += bn_result['found']
            results['imported'] += bn_result['imported']
        except Exception as e:
            results['errors'].append(f"BidNet: {str(e)}")
        
        # Try GovSpend RSS
        try:
            gs_result = self._mine_govspend()
            results['sources_checked'] += 1
            results['total_found'] += gs_result['found']
            results['imported'] += gs_result['imported']
        except Exception as e:
            results['errors'].append(f"GovSpend: {str(e)}")
        
        # Try InstantMarkets (Playwright browser scraper)
        try:
            im_result = self._mine_instantmarkets()
            results['sources_checked'] += 1
            results['total_found'] += im_result['found']
            results['imported'] += im_result['imported']
        except Exception as e:
            results['errors'].append(f"InstantMarkets: {str(e)}")
        
        # Try SkysTheLimit.org (FREE GBIS)
        try:
            stl_result = self._mine_skysthelimit()
            results['sources_checked'] += 1
            results['total_found'] += stl_result['found']
            results['imported'] += stl_result['imported']
        except Exception as e:
            results['errors'].append(f"SkysTheLimit: {str(e)}")
        
        print(f"✓ Checked {results['sources_checked']} sources")
        print(f"✓ Found {results['total_found']} opportunities")
        print(f"✓ Imported {results['imported']} to Airtable")
        
        return results
    
    def _mine_publicpurchase(self) -> Dict:
        """
        Mine PublicPurchase.com - free aggregator
        This aggregates bids from 1000s of agencies
        """
        print("   🔍 Mining PublicPurchase.com...")
        
        try:
            # PublicPurchase has RSS feeds by category
            feeds = [
                'https://www.publicpurchase.com/gems/rss/index.cfm?category=construction',
                'https://www.publicpurchase.com/gems/rss/index.cfm?category=consulting',
                'https://www.publicpurchase.com/gems/rss/index.cfm?category=professional_services'
            ]
            
            found = 0
            imported = 0
            
            for feed_url in feeds:
                try:
                    import feedparser
                    feed = feedparser.parse(feed_url)
                    
                    for entry in feed.entries[:20]:  # Limit to 20 per feed
                        try:
                            # Check for duplicates
                            if self._is_duplicate(entry.get('title', '')):
                                continue
                            
                            # Parse opportunity data
                            opp_data = {
                                'title': entry.get('title', 'Untitled')[:255],
                                'description': entry.get('summary', '')[:5000],
                                'url': entry.get('link', ''),
                                'posted_date': entry.get('published', ''),
                                'source': 'PublicPurchase.com'
                            }
                            
                            # Qualify with AI
                            qualification = self._qualify_state_local(opp_data)
                            
                            if qualification['score'] >= 60:  # Lower threshold for state/local
                                self._import_state_local(opp_data, qualification)
                                imported += 1
                            
                            found += 1
                            
                        except Exception as e:
                            continue
                    
                except Exception as e:
                    print(f"      ⚠ Feed error: {e}")
                    continue
            
            print(f"      ✓ PublicPurchase: {found} found, {imported} imported")
            return {'found': found, 'imported': imported}
            
        except Exception as e:
            print(f"      ❌ PublicPurchase error: {e}")
            return {'found': 0, 'imported': 0}
    
    def _mine_bidnet(self) -> Dict:
        """Mine BidNet Direct free listings"""
        print("   🔍 Mining BidNet Direct...")
        
        try:
            # BidNet has RSS feeds for different categories
            feeds = [
                'https://www.bidnetdirect.com/rss/network-bids.xml',
                'https://www.bidnetdirect.com/rss/featured-bids.xml'
            ]
            
            found = 0
            imported = 0
            
            import feedparser
            
            for feed_url in feeds:
                try:
                    feed = feedparser.parse(feed_url)
                    
                    for entry in feed.entries[:20]:
                        try:
                            if self._is_duplicate(entry.get('title', '')):
                                continue
                            
                            opp_data = {
                                'title': entry.get('title', 'Untitled')[:255],
                                'description': entry.get('summary', '')[:5000],
                                'url': entry.get('link', ''),
                                'posted_date': entry.get('published', ''),
                                'source': 'BidNet Direct'
                            }
                            
                            qualification = self._qualify_state_local(opp_data)
                            
                            if qualification['score'] >= 60:
                                self._import_state_local(opp_data, qualification)
                                imported += 1
                            
                            found += 1
                            
                        except:
                            continue
                    
                except:
                    continue
            
            print(f"      ✓ BidNet: {found} found, {imported} imported")
            return {'found': found, 'imported': imported}
            
        except Exception as e:
            print(f"      ❌ BidNet error: {e}")
            return {'found': 0, 'imported': 0}
    
    def _mine_govspend(self) -> Dict:
        """Mine GovSpend RSS feed"""
        print("   🔍 Mining GovSpend...")
        
        try:
            import feedparser
            
            # GovSpend RSS (if available publicly)
            feed_url = 'https://www.govspend.com/opportunities.rss'
            
            feed = feedparser.parse(feed_url)
            
            found = 0
            imported = 0
            
            for entry in feed.entries[:30]:
                try:
                    if self._is_duplicate(entry.get('title', '')):
                        continue
                    
                    opp_data = {
                        'title': entry.get('title', 'Untitled')[:255],
                        'description': entry.get('summary', '')[:5000],
                        'url': entry.get('link', ''),
                        'posted_date': entry.get('published', ''),
                        'source': 'GovSpend'
                    }
                    
                    qualification = self._qualify_state_local(opp_data)
                    
                    if qualification['score'] >= 60:
                        self._import_state_local(opp_data, qualification)
                        imported += 1
                    
                    found += 1
                    
                except:
                    continue
            
            print(f"      ✓ GovSpend: {found} found, {imported} imported")
            return {'found': found, 'imported': imported}
            
        except Exception as e:
            print(f"      ❌ GovSpend error: {e}")
            return {'found': 0, 'imported': 0}
    
    def _mine_instantmarkets(self) -> Dict:
        """Mine InstantMarkets.com using Playwright headless browser"""
        print("   🔍 Mining InstantMarkets.com (Playwright)...")
        
        found = 0
        imported = 0
        
        try:
            from playwright.sync_api import sync_playwright
            import time
            
            categories = self.sources.get('InstantMarkets', {}).get('search_categories', [
                'Vehicle', 'Truck', 'Landscape', 'Cleaning_Supplies',
                'Chemicals', 'Healthcare', 'Tools'
            ])
            
            # State filters for Michigan and nearby
            state_filters = ['MI']
            
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(
                    user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                )
                page = context.new_page()
                
                for category in categories:
                    try:
                        # Build search URL — active bid notifications
                        search_url = f'https://www.instantmarkets.com/q/{category}?ot=Bid%20Notification,Pre-Bid%20Notification&os=Active'
                        
                        page.goto(search_url, wait_until='domcontentloaded', timeout=20000)
                        
                        # Wait for SPA to render results
                        time.sleep(8)
                        
                        # Extract opportunity links and descriptions from rendered page
                        opps = page.evaluate('''() => {
                            const results = [];
                            document.querySelectorAll('a[href*="/view/"]').forEach(a => {
                                const href = a.getAttribute('href') || '';
                                const text = a.textContent.trim();
                                if (text.length > 5 && text.length < 300 
                                    && !text.includes('See more') 
                                    && !text.includes('Reset')) {
                                    // Try to get the parent card's full text for description
                                    let desc = '';
                                    let parent = a.parentElement;
                                    for (let i = 0; i < 5 && parent; i++) {
                                        const pText = parent.textContent || '';
                                        if (pText.length > text.length + 20 && pText.length < 2000) {
                                            desc = pText.trim().substring(0, 500);
                                            break;
                                        }
                                        parent = parent.parentElement;
                                    }
                                    results.push({
                                        title: text.substring(0, 255),
                                        url: href,
                                        description: desc
                                    });
                                }
                            });
                            return results;
                        }''')
                        
                        cat_found = 0
                        for opp in opps[:15]:
                            try:
                                title = opp.get('title', '').strip()
                                url = opp.get('url', '')
                                
                                if not title or len(title) < 5:
                                    continue
                                
                                # Make URL absolute
                                if url.startswith('/'):
                                    url = f'https://www.instantmarkets.com{url}'
                                
                                if self._is_duplicate(title):
                                    continue
                                
                                desc = opp.get('description', '') or ''
                                opp_data = {
                                    'title': title[:255],
                                    'description': f'Category: {category.replace("_", " ")}. {desc[:400]}',
                                    'url': url,
                                    'posted_date': '',
                                    'source': 'InstantMarkets'
                                }
                                
                                qualification = self._qualify_instantmarkets(opp_data)
                                
                                if qualification['score'] >= 50:
                                    self._import_state_local(opp_data, qualification)
                                    imported += 1
                                
                                found += 1
                                cat_found += 1
                                
                            except Exception:
                                continue
                        
                        print(f"      📂 {category}: {cat_found} new opps")
                        
                        # Delay between categories to avoid rate limiting
                        time.sleep(2)
                        
                    except Exception as e:
                        print(f"      ⚠️ {category}: {str(e)[:80]}")
                        continue
                
                browser.close()
            
            print(f"      ✓ InstantMarkets: {found} found, {imported} imported")
            return {'found': found, 'imported': imported}
            
        except Exception as e:
            print(f"      ❌ InstantMarkets error: {e}")
            import traceback
            traceback.print_exc()
            return {'found': 0, 'imported': 0}
    
    def _qualify_instantmarkets(self, opp: Dict) -> Dict:
        """Qualify InstantMarkets opportunity — tuned for Dee Davis Inc business model"""
        try:
            title = opp.get('title', '').lower()
            description = opp.get('description', '').lower()
            combined = f'{title} {description}'
            
            score = 35  # Base score
            reasons = []
            
            # HIGH VALUE keywords (product resale, our core model)
            high_value = [
                'vehicle', 'truck', 'trailer', 'plow', 'snow', 'salt',
                'chemical', 'chlorine', 'padlock', 'lock', 'safety supply',
                'sign', 'traffic sign', 'barricade', 'cone',
                'tool', 'hand tool', 'power tool', 'building material',
                'paper product', 'janitorial', 'cleaning supply',
                'medical supply', 'surgical', 'ppe', 'glove',
                'furniture', 'office supply', 'aggregate', 'sand',
                'gravel', 'concrete', 'asphalt', 'lumber',
                'pipe', 'valve', 'fitting', 'pump', 'generator',
                'mower', 'landscap', 'turf', 'seed', 'fertilizer',
                'wiper', 'automotive', 'fleet', 'parts',
                'uniform', 'clothing', 'boot', 'equipment'
            ]
            
            for kw in high_value:
                if kw in combined:
                    score += 15
                    reasons.append(f'product match: {kw}')
                    break  # Only count once per category
            
            # MEDIUM VALUE (services we can sub out)
            medium_value = [
                'pressure wash', 'power wash', 'cleaning service',
                'lawn', 'mowing', 'yard', 'grounds maintenance',
                'pest control', 'painting', 'moving service',
                'hauling', 'demolition', 'remediation'
            ]
            
            for kw in medium_value:
                if kw in combined:
                    score += 10
                    reasons.append(f'service match: {kw}')
                    break
            
            # LOCATION boost (Michigan / nearby states)
            location_boost = ['michigan', ' mi ', 'detroit', 'oakland', 'wayne',
                            'macomb', 'livingston', 'washtenaw', 'genesee',
                            'troy', 'warren', 'livonia', 'auburn hills']
            
            for loc in location_boost:
                if loc in combined:
                    score += 20
                    reasons.append(f'location: {loc.strip()}')
                    break
            
            # DIVERSITY boost
            diversity_terms = ['wosb', 'edwosb', 'woman-owned', 'women-owned',
                             'small business set-aside', 'sba', 'minority',
                             '8(a)', 'hubzone', 'sdvosb', 'set-aside']
            
            for term in diversity_terms:
                if term in combined:
                    score += 25
                    reasons.append(f'diversity: {term}')
                    break
            
            # NEGATIVE keywords (things we can't do / don't want)
            negative = ['software', 'it services', 'consulting', 'staffing',
                       'audit', 'accounting', 'legal service', 'architect',
                       'engineering design', 'survey', 'insurance broker',
                       'financial', 'banking', 'real estate', 'hotel',
                       'catering', 'food service', 'weapons', 'ammunition']
            
            for kw in negative:
                if kw in combined:
                    score -= 20
                    reasons.append(f'negative: {kw}')
                    break
            
            score = max(0, min(score, 100))
            
            return {
                'score': score,
                'recommendation': 'pursue' if score >= 50 else 'skip',
                'reason': '; '.join(reasons) if reasons else 'No strong match'
            }
            
        except Exception as e:
            return {'score': 30, 'recommendation': 'skip', 'reason': f'Error: {str(e)}'}
    
    def _mine_skysthelimit(self) -> Dict:
        """Mine SkysTheLimit.org - FREE GBIS (Government Bid Information System)"""
        print("   🔍 Mining SkysTheLimit.org (FREE GBIS)...")
        
        try:
            import feedparser
            
            # SkysTheLimit has RSS feeds for government bids
            # Try common RSS feed patterns
            feed_urls = [
                'https://www.skysthelimit.org/rss/opportunities',
                'https://www.skysthelimit.org/rss/bids',
                'https://www.skysthelimit.org/feed',
                'https://www.skysthelimit.org/opportunities.rss'
            ]
            
            found = 0
            imported = 0
            
            # Try each potential feed URL
            for feed_url in feed_urls:
                try:
                    feed = feedparser.parse(feed_url)
                    
                    # If we got entries, process them
                    if feed.entries and len(feed.entries) > 0:
                        print(f"      ✓ Found RSS feed: {feed_url}")
                        
                        for entry in feed.entries[:30]:
                            try:
                                if self._is_duplicate(entry.get('title', '')):
                                    continue
                                
                                opp_data = {
                                    'title': entry.get('title', 'Untitled')[:255],
                                    'description': entry.get('summary', entry.get('description', ''))[:5000],
                                    'url': entry.get('link', ''),
                                    'posted_date': entry.get('published', ''),
                                    'source': 'SkysTheLimit GBIS'
                                }
                                
                                qualification = self._qualify_state_local(opp_data)
                                
                                if qualification['score'] >= 60:
                                    self._import_state_local(opp_data, qualification)
                                    imported += 1
                                
                                found += 1
                                
                            except:
                                continue
                        
                        # If we found a working feed, stop trying others
                        break
                        
                except:
                    continue
            
            if found > 0:
                print(f"      ✓ SkysTheLimit: {found} found, {imported} imported")
            else:
                print(f"      ⚠ SkysTheLimit: No RSS feed found (may require account)")
            
            return {'found': found, 'imported': imported}
            
        except Exception as e:
            print(f"      ❌ SkysTheLimit error: {e}")
            return {'found': 0, 'imported': 0}
    
    def _is_duplicate(self, title: str) -> bool:
        """Check if opportunity already exists"""
        try:
            records = self.airtable.get_all_records('GPSS OPPORTUNITIES')
            return any(r['fields'].get('Name') == title for r in records)
        except:
            return False
    
    def _qualify_state_local(self, opp: Dict) -> Dict:
        """Qualify state/local opportunity with AI"""
        try:
            title = opp.get('title', '')
            description = opp.get('description', '')[:500]
            
            # Simple keyword scoring
            score = 40
            
            # Boost for relevant keywords
            relevant_keywords = ['consulting', 'professional services', 'management', 
                               'training', 'technology', 'it services', 'program', 
                               'evaluation', 'assessment', 'advisory']
            
            for keyword in relevant_keywords:
                if keyword in title.lower() or keyword in description.lower():
                    score += 10
            
            # Boost for EDWOSB/WOSB mentions
            if 'women' in title.lower() or 'wosb' in title.lower():
                score += 20
            
            score = min(score, 100)
            
            return {
                'score': score,
                'recommendation': 'pursue' if score >= 60 else 'skip',
                'reason': f'State/Local keyword match (score: {score})'
            }
            
        except Exception as e:
            return {'score': 40, 'recommendation': 'skip', 'reason': f'Error: {str(e)}'}
    
    def _import_state_local(self, opp: Dict, qualification: Dict):
        """Import state/local opportunity to Airtable"""
        from dateutil import parser
        
        # Parse date safely
        due_date = ''
        try:
            if opp.get('posted_date'):
                # If we have a posted date, estimate deadline 30 days out
                posted_dt = parser.parse(opp['posted_date'])
                due_date = (posted_dt + timedelta(days=30)).strftime('%Y-%m-%d')
        except:
            # Default to 30 days from now
            due_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        
        # Generate a unique RFP NUMBER
        import hashlib
        title_hash = hashlib.md5(opp.get('title', '').encode()).hexdigest()[:8]
        rfp_number = f"STATE-{datetime.now().strftime('%Y%m%d')}-{title_hash}"
        
        # Map to actual Airtable field names
        fields = {
            'Name': opp.get('title', 'Untitled')[:255],
            'RFP NUMBER': rfp_number,
            'Status': 'New - State/Local',
            'Deadline': due_date
        }
        
        self.airtable.create_record('GPSS OPPORTUNITIES', fields)


def handle_mine_state_local() -> Dict:
    """Handler for state/local mining"""
    miner = StateLocalMiner()
    return miner.mine_all_sources()


# =====================================================================
# SUPPLIER MINING HANDLER FUNCTIONS
# =====================================================================

def handle_search_suppliers(filters: Dict) -> List[Dict]:
    """Search existing suppliers"""
    miner = GPSSSupplierMiner()
    return miner.search_existing_suppliers(
        category=filters.get('category'),
        keywords=filters.get('keywords'),
        min_rating=filters.get('min_rating', 0)
    )


def handle_find_suppliers_for_product(product: str, category: str = None) -> List[Dict]:
    """Find suppliers for specific product"""
    miner = GPSSSupplierMiner()
    return miner.find_suppliers_for_product(product, category)


def handle_create_supplier(supplier_data: Dict) -> Dict:
    """Create new supplier"""
    miner = GPSSSupplierMiner()
    return miner.create_supplier(supplier_data)


def handle_update_supplier(supplier_id: str, updates: Dict) -> Dict:
    """Update supplier"""
    miner = GPSSSupplierMiner()
    return miner.update_supplier(supplier_id, updates)


def handle_get_supplier(supplier_id: str) -> Optional[Dict]:
    """Get supplier by ID"""
    miner = GPSSSupplierMiner()
    return miner.get_supplier(supplier_id)


def handle_process_opportunity_for_suppliers(opportunity_id: str) -> Dict:
    """Process opportunity with automated supplier finding and quote requests"""
    auto_quote = GPSSAutomatedQuoting()
    return auto_quote.process_opportunity(opportunity_id)


def handle_find_suppliers_for_opportunity(opportunity_id: str) -> List[Dict]:
    """Find matching suppliers for opportunity"""
    auto_quote = GPSSAutomatedQuoting()
    return auto_quote.find_suppliers_for_opportunity(opportunity_id)


# =====================================================================
# CALENDAR AUTOMATION HANDLER FUNCTIONS
# =====================================================================

def handle_generate_calendar(opportunity_id: str) -> Dict:
    """
    Generate .ics calendar file for opportunity deadline
    
    Args:
        opportunity_id: Airtable record ID for opportunity
        
    Returns:
        Dict with success status and file path
    """
    from calendar_automation import CalendarAutomation
    
    automation = CalendarAutomation()
    table = automation.api.table(automation.base_id, 'GPSS OPPORTUNITIES')
    record = table.get(opportunity_id)
    
    filepath = automation.generate_opportunity_calendar(record)
    
    if filepath:
        automation.email_calendar_file(
            filepath,
            record['fields'].get('Name'),
            record['fields'].get('Deadline')
        )
        
        return {
            'success': True,
            'filepath': filepath,
            'message': f'Calendar file generated and emailed: {os.path.basename(filepath)}'
        }
    else:
        return {
            'success': False,
            'message': 'Failed to generate calendar file - no deadline found'
        }


def handle_daily_deadline_report() -> Dict:
    """
    Send daily email with upcoming deadlines
    Run via cron at 7 AM daily
    
    Returns:
        Dict with success status
    """
    from calendar_automation import CalendarAutomation
    
    automation = CalendarAutomation()
    automation.send_daily_deadline_report()
    
    return {
        'success': True,
        'message': 'Daily deadline report sent'
    }


def handle_get_upcoming_deadlines(days_ahead: int = 7) -> Dict:
    """
    Get list of upcoming deadlines
    
    Args:
        days_ahead: Number of days to look ahead (default: 7)
        
    Returns:
        Dict with upcoming deadlines
    """
    from calendar_automation import CalendarAutomation
    
    automation = CalendarAutomation()
    upcoming = automation.get_upcoming_deadlines(days_ahead)
    
    return {
        'success': True,
        'count': len(upcoming),
        'deadlines': upcoming
    }


def handle_process_new_opportunities() -> Dict:
    """
    Process new opportunities and generate calendar files
    Run via cron hourly
    
    Returns:
        Dict with number of opportunities processed
    """
    from calendar_automation import CalendarAutomation
    
    automation = CalendarAutomation()
    count = automation.process_new_opportunities()
    
    return {
        'success': True,
        'processed': count,
        'message': f'Processed {count} new opportunities'
    }


# =====================================================================
# CONTRACT FULFILLMENT SYSTEM
# =====================================================================

class FulfillmentManager:
    """
    Comprehensive Contract Fulfillment & Inventory Management System
    
    Handles:
    - Contract setup and delivery scheduling
    - Inventory tracking and reorder alerts
    - Delivery management and tracking
    - Purchase order management
    - Financial integration with VERTEX
    """
    
    def __init__(self):
        self.airtable = AirtableClient()
        self.ai = AnthropicClient()
    
    # ============ CONTRACT MANAGEMENT ============
    
    def create_fulfillment_contract(self, contract_data: Dict) -> Dict:
        """
        Create new fulfillment contract and auto-generate delivery schedule
        
        Args:
            contract_data: {
                'CONTRACT_NAME': 'VA Hospital - Socks',
                'CLIENT_NAME': 'Veterans Affairs',
                'PRODUCT': 'Diabetic Socks - White L',
                'TOTAL_QUANTITY': 2500,
                'UNIT_PRICE': 5.00,
                'DELIVERY_FREQUENCY': 'Monthly',
                'QUANTITY_PER_DELIVERY': 200,
                'START_DATE': '2026-02-01',
                'END_DATE': '2028-01-31',
                'SUPPLIER_ID': ['rec123...'],
                'SUPPLIER_UNIT_COST': 3.50
            }
        
        Returns: {
            'contract': {...},
            'deliveries_generated': 24,
            'contract_id': 'recXYZ'
        }
        """
        try:
            # Generate unique contract ID
            import time
            contract_id = f"CONT-{datetime.now().year}-{str(int(time.time()))[-6:]}"
            
            # Calculate delivery schedule
            total_qty = contract_data['TOTAL_QUANTITY']
            qty_per_delivery = contract_data['QUANTITY_PER_DELIVERY']
            total_deliveries = total_qty // qty_per_delivery
            
            # Calculate margin
            margin_per_unit = contract_data['UNIT_PRICE'] - contract_data['SUPPLIER_UNIT_COST']
            
            # Create contract record
            contract_fields = {
                'CONTRACT_ID': contract_id,
                'CONTRACT_NAME': contract_data['CONTRACT_NAME'],
                'CLIENT_NAME': contract_data['CLIENT_NAME'],
                'PRODUCT': contract_data['PRODUCT'],
                'TOTAL_QUANTITY': total_qty,
                'UNIT_PRICE': contract_data['UNIT_PRICE'],
                'TOTAL_VALUE': total_qty * contract_data['UNIT_PRICE'],
                'START_DATE': contract_data['START_DATE'],
                'END_DATE': contract_data.get('END_DATE', ''),
                'DELIVERY_FREQUENCY': contract_data['DELIVERY_FREQUENCY'],
                'QUANTITY_PER_DELIVERY': qty_per_delivery,
                'TOTAL_DELIVERIES': total_deliveries,
                'DELIVERIES_COMPLETED': 0,
                'DELIVERIES_REMAINING': total_deliveries,
                'STATUS': 'Active',
                'SUPPLIER_ID': contract_data.get('SUPPLIER_ID', []),
                'SUPPLIER_UNIT_COST': contract_data['SUPPLIER_UNIT_COST'],
                'MARGIN_PER_UNIT': margin_per_unit,
                'ALERT_THRESHOLD': contract_data.get('ALERT_THRESHOLD', qty_per_delivery * 2),
                'NOTES': contract_data.get('NOTES', '')
            }
            
            contract_record = self.airtable.create_record('FULFILLMENT CONTRACTS', contract_fields)
            contract_record_id = contract_record['id']
            
            # Auto-generate delivery schedule
            deliveries = self._generate_delivery_schedule(
                contract_record_id,
                contract_id,
                contract_data['START_DATE'],
                contract_data['DELIVERY_FREQUENCY'],
                total_deliveries,
                qty_per_delivery
            )
            
            # Update inventory tracking
            self._update_inventory_commitment(
                contract_data['PRODUCT'],
                total_qty,
                contract_data.get('SUPPLIER_ID', []),
                contract_data['SUPPLIER_UNIT_COST']
            )
            
            # Set next delivery date
            if deliveries:
                next_delivery = deliveries[0]['DUE_DATE']
                self.airtable.update_record(
                    'FULFILLMENT CONTRACTS',
                    contract_record_id,
                    {'NEXT_DELIVERY_DATE': next_delivery}
                )
            
            return {
                'success': True,
                'contract': contract_record,
                'contract_id': contract_id,
                'deliveries_generated': len(deliveries),
                'total_value': contract_fields['TOTAL_VALUE'],
                'total_profit': margin_per_unit * total_qty
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _generate_delivery_schedule(self, contract_record_id: str, contract_id: str,
                                   start_date: str, frequency: str, 
                                   total_deliveries: int, qty_per_delivery: int) -> List[Dict]:
        """Generate delivery schedule based on frequency"""
        from dateutil.relativedelta import relativedelta
        from datetime import datetime
        
        deliveries = []
        current_date = datetime.strptime(start_date, '%Y-%m-%d')
        
        # Determine interval based on frequency
        interval_map = {
            'Weekly': relativedelta(weeks=1),
            'Biweekly': relativedelta(weeks=2),
            'Monthly': relativedelta(months=1),
            'Quarterly': relativedelta(months=3),
            'Semi-Annual': relativedelta(months=6),
            'Annual': relativedelta(years=1)
        }
        
        interval = interval_map.get(frequency, relativedelta(months=1))
        
        for i in range(total_deliveries):
            # Calculate due date
            due_date = current_date + (interval * i)
            
            # Generate delivery ID
            delivery_id = f"DEL-{contract_id}-{str(i+1).zfill(3)}"
            
            # Create delivery record
            delivery_fields = {
                'DELIVERY_ID': delivery_id,
                'CONTRACT': [contract_record_id],
                'DELIVERY_NUMBER': i + 1,
                'DUE_DATE': due_date.strftime('%Y-%m-%d'),
                'QUANTITY': qty_per_delivery,
                'STATUS': 'Scheduled',
                'NOTES': f'Auto-generated delivery {i+1} of {total_deliveries}'
            }
            
            try:
                delivery_record = self.airtable.create_record('FULFILLMENT DELIVERIES', delivery_fields)
                deliveries.append(delivery_fields)
            except Exception as e:
                print(f"Error creating delivery {i+1}: {e}")
        
        return deliveries
    
    def get_active_contracts(self) -> List[Dict]:
        """Get all active fulfillment contracts"""
        try:
            formula = "{STATUS} = 'Active'"
            records = self.airtable.search_records('FULFILLMENT CONTRACTS', formula)
            return [{'id': r['id'], **r['fields']} for r in records]
        except Exception as e:
            print(f"Error getting active contracts: {e}")
            return []
    
    def get_contract_details(self, contract_id: str) -> Dict:
        """Get contract with all deliveries and inventory status"""
        try:
            # Get contract
            contract = self.airtable.get_record('FULFILLMENT CONTRACTS', contract_id)
            
            # Get all deliveries for this contract
            formula = f"{{CONTRACT}} = '{contract_id}'"
            deliveries = self.airtable.search_records('FULFILLMENT DELIVERIES', formula)
            
            # Get inventory status for product
            product = contract['fields'].get('PRODUCT')
            inventory = self._get_inventory_status(product)
            
            return {
                'contract': contract,
                'deliveries': [{'id': d['id'], **d['fields']} for d in deliveries],
                'inventory': inventory
            }
        except Exception as e:
            return {'error': str(e)}
    
    # ============ DELIVERY MANAGEMENT ============
    
    def get_upcoming_deliveries(self, days_ahead: int = 7) -> List[Dict]:
        """Get deliveries due within X days"""
        try:
            from datetime import datetime, timedelta
            
            today = datetime.now()
            future_date = today + timedelta(days=days_ahead)
            
            # Get all scheduled or in-transit deliveries
            formula = f"AND(OR({{STATUS}} = 'Scheduled', {{STATUS}} = 'In Transit'), {{DUE_DATE}} <= '{future_date.strftime('%Y-%m-%d')}')"
            records = self.airtable.search_records('FULFILLMENT DELIVERIES', formula)
            
            deliveries = []
            for r in records:
                fields = r['fields']
                due_date = datetime.strptime(fields['DUE_DATE'], '%Y-%m-%d')
                days_until = (due_date - today).days
                
                deliveries.append({
                    'id': r['id'],
                    'days_until_due': days_until,
                    **fields
                })
            
            # Sort by due date
            deliveries.sort(key=lambda x: x['days_until_due'])
            return deliveries
            
        except Exception as e:
            print(f"Error getting upcoming deliveries: {e}")
            return []
    
    def update_delivery_status(self, delivery_id: str, updates: Dict) -> Dict:
        """
        Update delivery status and trigger cascading updates
        
        Args:
            updates: {
                'STATUS': 'Delivered',
                'ACTUAL_DELIVERY_DATE': '2026-02-15',
                'TRACKING_NUMBER': '1Z999...',
                'CARRIER': 'UPS',
                'SHIPPING_COST': 45.00,
                'DELIVERED_TO': 'John Smith',
                'NOTES': 'Left at loading dock'
            }
        """
        try:
            # Get current delivery
            delivery = self.airtable.get_record('FULFILLMENT DELIVERIES', delivery_id)
            quantity = delivery['fields']['QUANTITY']
            contract_ids = delivery['fields'].get('CONTRACT', [])
            
            # Calculate performance metric
            if updates.get('ACTUAL_DELIVERY_DATE') and delivery['fields'].get('DUE_DATE'):
                actual = datetime.strptime(updates['ACTUAL_DELIVERY_DATE'], '%Y-%m-%d')
                due = datetime.strptime(delivery['fields']['DUE_DATE'], '%Y-%m-%d')
                days_early_late = (due - actual).days
                updates['DAYS_EARLY_LATE'] = days_early_late
            
            # Update delivery record
            updated_delivery = self.airtable.update_record('FULFILLMENT DELIVERIES', delivery_id, updates)
            
            # If delivered, trigger cascading updates
            if updates.get('STATUS') == 'Delivered':
                # Update contract progress
                if contract_ids:
                    self._update_contract_progress(contract_ids[0], quantity)
                
                # Update inventory
                product = self._get_product_from_contract(contract_ids[0])
                if product:
                    self._reduce_inventory(product, quantity)
                
                # Create financial records in VERTEX
                self._create_financial_records(contract_ids[0], quantity, delivery_id)
            
            return {
                'success': True,
                'delivery': updated_delivery
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _update_contract_progress(self, contract_id: str, quantity_delivered: int):
        """Update contract delivery progress"""
        try:
            contract = self.airtable.get_record('FULFILLMENT CONTRACTS', contract_id)
            fields = contract['fields']
            
            completed = fields.get('DELIVERIES_COMPLETED', 0) + 1
            remaining = fields.get('DELIVERIES_REMAINING', 0) - 1
            
            updates = {
                'DELIVERIES_COMPLETED': completed,
                'DELIVERIES_REMAINING': remaining
            }
            
            # If all deliveries complete, mark contract as completed
            if remaining <= 0:
                updates['STATUS'] = 'Completed'
            else:
                # Update next delivery date
                next_delivery = self._get_next_scheduled_delivery(contract_id)
                if next_delivery:
                    updates['NEXT_DELIVERY_DATE'] = next_delivery['DUE_DATE']
            
            self.airtable.update_record('FULFILLMENT CONTRACTS', contract_id, updates)
            
        except Exception as e:
            print(f"Error updating contract progress: {e}")
    
    def _get_next_scheduled_delivery(self, contract_id: str) -> Optional[Dict]:
        """Get the next scheduled delivery for a contract"""
        try:
            formula = f"AND({{CONTRACT}} = '{contract_id}', {{STATUS}} = 'Scheduled')"
            deliveries = self.airtable.search_records('FULFILLMENT DELIVERIES', formula)
            
            if not deliveries:
                return None
            
            # Sort by due date and return first
            sorted_deliveries = sorted(deliveries, key=lambda x: x['fields']['DUE_DATE'])
            return sorted_deliveries[0]['fields']
            
        except Exception as e:
            print(f"Error getting next delivery: {e}")
            return None
    
    # ============ INVENTORY MANAGEMENT ============
    
    def _update_inventory_commitment(self, product: str, quantity: int, 
                                    supplier_ids: List[str], unit_cost: float):
        """Update or create inventory record with commitment"""
        try:
            # Check if inventory record exists
            formula = f"{{PRODUCT_NAME}} = '{product}'"
            existing = self.airtable.search_records('FULFILLMENT INVENTORY', formula)
            
            if existing:
                # Update existing
                record = existing[0]
                current_committed = record['fields'].get('QUANTITY_COMMITTED', 0)
                new_committed = current_committed + quantity
                
                updates = {
                    'QUANTITY_COMMITTED': new_committed,
                    'ACTIVE_CONTRACTS': record['fields'].get('ACTIVE_CONTRACTS', 0) + 1
                }
                
                # Recalculate available
                on_hand = record['fields'].get('QUANTITY_ON_HAND', 0)
                updates['QUANTITY_AVAILABLE'] = on_hand - new_committed
                
                # Update status based on availability
                if updates['QUANTITY_AVAILABLE'] < 0:
                    updates['STATUS'] = 'Critical'
                elif updates['QUANTITY_AVAILABLE'] < record['fields'].get('REORDER_POINT', 400):
                    updates['STATUS'] = 'Low Stock'
                
                self.airtable.update_record('FULFILLMENT INVENTORY', record['id'], updates)
            else:
                # Create new inventory record
                sku = self._generate_sku(product)
                inventory_fields = {
                    'PRODUCT_SKU': sku,
                    'PRODUCT_NAME': product,
                    'QUANTITY_ON_HAND': 0,
                    'QUANTITY_COMMITTED': quantity,
                    'QUANTITY_AVAILABLE': -quantity,
                    'REORDER_POINT': 400,
                    'REORDER_QUANTITY': 1000,
                    'SUPPLIER': supplier_ids,
                    'UNIT_COST': unit_cost,
                    'STATUS': 'Critical',
                    'ACTIVE_CONTRACTS': 1
                }
                
                self.airtable.create_record('FULFILLMENT INVENTORY', inventory_fields)
                
        except Exception as e:
            print(f"Error updating inventory commitment: {e}")
    
    def _reduce_inventory(self, product: str, quantity: int):
        """Reduce inventory when delivery is made"""
        try:
            formula = f"{{PRODUCT_NAME}} = '{product}'"
            records = self.airtable.search_records('FULFILLMENT INVENTORY', formula)
            
            if records:
                record = records[0]
                fields = record['fields']
                
                new_on_hand = fields.get('QUANTITY_ON_HAND', 0) - quantity
                new_committed = fields.get('QUANTITY_COMMITTED', 0) - quantity
                new_available = new_on_hand - new_committed
                
                updates = {
                    'QUANTITY_ON_HAND': new_on_hand,
                    'QUANTITY_COMMITTED': new_committed,
                    'QUANTITY_AVAILABLE': new_available
                }
                
                # Update status
                reorder_point = fields.get('REORDER_POINT', 400)
                if new_available < 0:
                    updates['STATUS'] = 'Critical'
                elif new_on_hand < reorder_point:
                    updates['STATUS'] = 'Low Stock'
                else:
                    updates['STATUS'] = 'Healthy'
                
                self.airtable.update_record('FULFILLMENT INVENTORY', record['id'], updates)
                
        except Exception as e:
            print(f"Error reducing inventory: {e}")
    
    def _get_inventory_status(self, product: str) -> Dict:
        """Get current inventory status for a product"""
        try:
            formula = f"{{PRODUCT_NAME}} = '{product}'"
            records = self.airtable.search_records('FULFILLMENT INVENTORY', formula)
            
            if records:
                return {'id': records[0]['id'], **records[0]['fields']}
            return {}
            
        except Exception as e:
            print(f"Error getting inventory status: {e}")
            return {}
    
    def check_inventory_health(self) -> Dict:
        """
        Daily inventory health check - identifies products needing reorder
        Returns alerts and recommendations
        """
        try:
            all_inventory = self.airtable.get_all_records('FULFILLMENT INVENTORY')
            
            alerts = {
                'critical': [],  # Available < 0
                'low_stock': [],  # On hand < reorder point
                'reorder_needed': [],  # Calculated runout < 30 days
                'healthy': []
            }
            
            for record in all_inventory:
                fields = record['fields']
                product = fields.get('PRODUCT_NAME', 'Unknown')
                on_hand = fields.get('QUANTITY_ON_HAND', 0)
                committed = fields.get('QUANTITY_COMMITTED', 0)
                available = fields.get('QUANTITY_AVAILABLE', 0)
                reorder_point = fields.get('REORDER_POINT', 400)
                burn_rate = fields.get('MONTHLY_BURN_RATE', 0)
                
                item = {
                    'product': product,
                    'on_hand': on_hand,
                    'committed': committed,
                    'available': available,
                    'reorder_point': reorder_point,
                    'record_id': record['id']
                }
                
                # Critical: Cannot fulfill commitments
                if available < 0:
                    item['alert'] = f"CRITICAL: Short by {abs(available)} units"
                    item['action'] = f"Order at least {abs(available) + reorder_point} units immediately"
                    alerts['critical'].append(item)
                
                # Low stock: Below reorder point
                elif on_hand < reorder_point:
                    item['alert'] = f"Low stock: {on_hand} units (reorder at {reorder_point})"
                    item['action'] = f"Order {fields.get('REORDER_QUANTITY', 1000)} units"
                    alerts['low_stock'].append(item)
                
                # Calculate runout date if burn rate is known
                elif burn_rate > 0 and available > 0:
                    days_remaining = (available / burn_rate) * 30
                    if days_remaining < 30:
                        item['alert'] = f"Will run out in {int(days_remaining)} days"
                        item['action'] = f"Order {fields.get('REORDER_QUANTITY', 1000)} units soon"
                        alerts['reorder_needed'].append(item)
                    else:
                        alerts['healthy'].append(item)
                else:
                    alerts['healthy'].append(item)
            
            return {
                'success': True,
                'alerts': alerts,
                'summary': {
                    'critical_count': len(alerts['critical']),
                    'low_stock_count': len(alerts['low_stock']),
                    'reorder_needed_count': len(alerts['reorder_needed']),
                    'healthy_count': len(alerts['healthy'])
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_inventory_dashboard(self) -> List[Dict]:
        """Get all inventory with status indicators"""
        try:
            records = self.airtable.get_all_records('FULFILLMENT INVENTORY')
            return [{'id': r['id'], **r['fields']} for r in records]
        except Exception as e:
            print(f"Error getting inventory dashboard: {e}")
            return []
    
    # ============ PURCHASE ORDER MANAGEMENT ============
    
    def create_purchase_order(self, po_data: Dict) -> Dict:
        """
        Create purchase order to restock inventory
        
        Args:
            po_data: {
                'SUPPLIER': ['rec123...'],
                'PRODUCT_SKU': 'SOCK-DIAB-WHT-L',
                'PRODUCT_NAME': 'Diabetic Socks - White L',
                'QUANTITY_ORDERED': 2000,
                'UNIT_COST': 3.50,
                'EXPECTED_DELIVERY_DATE': '2026-04-20',
                'PAYMENT_TERMS': 'Net 30',
                'NOTES': 'Rush order'
            }
        """
        try:
            import time
            po_number = f"PO-{datetime.now().year}-{str(int(time.time()))[-6:]}"
            
            po_fields = {
                'PO_NUMBER': po_number,
                'SUPPLIER': po_data.get('SUPPLIER', []),
                'ORDER_DATE': datetime.now().strftime('%Y-%m-%d'),
                'EXPECTED_DELIVERY_DATE': po_data['EXPECTED_DELIVERY_DATE'],
                'PRODUCTS': po_data.get('PRODUCT_NAME', ''),
                'QUANTITY_ORDERED': po_data['QUANTITY_ORDERED'],
                'QUANTITY_RECEIVED': 0,
                'UNIT_COST': po_data['UNIT_COST'],
                'TOTAL_COST': po_data['QUANTITY_ORDERED'] * po_data['UNIT_COST'],
                'PAYMENT_TERMS': po_data.get('PAYMENT_TERMS', 'Net 30'),
                'PAYMENT_STATUS': 'Pending',
                'STATUS': 'Ordered',
                'NOTES': po_data.get('NOTES', '')
            }
            
            # Calculate payment due date based on terms
            if po_data.get('PAYMENT_TERMS') == 'Net 30':
                from dateutil.relativedelta import relativedelta
                expected = datetime.strptime(po_data['EXPECTED_DELIVERY_DATE'], '%Y-%m-%d')
                due_date = expected + relativedelta(days=30)
                po_fields['PAYMENT_DUE_DATE'] = due_date.strftime('%Y-%m-%d')
            
            po_record = self.airtable.create_record('FULFILLMENT PURCHASE ORDERS', po_fields)
            
            return {
                'success': True,
                'po': po_record,
                'po_number': po_number
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def receive_purchase_order(self, po_id: str, received_data: Dict) -> Dict:
        """
        Mark PO as received and update inventory
        
        Args:
            received_data: {
                'ACTUAL_DELIVERY_DATE': '2026-04-19',
                'QUANTITY_RECEIVED': 2000,
                'NOTES': 'All items in good condition'
            }
        """
        try:
            # Get PO details
            po = self.airtable.get_record('FULFILLMENT PURCHASE ORDERS', po_id)
            po_fields = po['fields']
            
            # Update PO status
            updates = {
                'STATUS': 'Received',
                'ACTUAL_DELIVERY_DATE': received_data['ACTUAL_DELIVERY_DATE'],
                'QUANTITY_RECEIVED': received_data['QUANTITY_RECEIVED'],
                'NOTES': po_fields.get('NOTES', '') + '\n' + received_data.get('NOTES', '')
            }
            
            updated_po = self.airtable.update_record('FULFILLMENT PURCHASE ORDERS', po_id, updates)
            
            # Update inventory - add to on hand
            product = po_fields.get('PRODUCTS', '')
            quantity = received_data['QUANTITY_RECEIVED']
            
            if product:
                self._add_inventory(product, quantity, received_data['ACTUAL_DELIVERY_DATE'])
            
            return {
                'success': True,
                'po': updated_po,
                'inventory_updated': True
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _add_inventory(self, product: str, quantity: int, restock_date: str):
        """Add inventory when PO is received"""
        try:
            formula = f"{{PRODUCT_NAME}} = '{product}'"
            records = self.airtable.search_records('FULFILLMENT INVENTORY', formula)
            
            if records:
                record = records[0]
                fields = record['fields']
                
                new_on_hand = fields.get('QUANTITY_ON_HAND', 0) + quantity
                committed = fields.get('QUANTITY_COMMITTED', 0)
                new_available = new_on_hand - committed
                
                updates = {
                    'QUANTITY_ON_HAND': new_on_hand,
                    'QUANTITY_AVAILABLE': new_available,
                    'LAST_RESTOCK_DATE': restock_date
                }
                
                # Update status
                reorder_point = fields.get('REORDER_POINT', 400)
                if new_available < 0:
                    updates['STATUS'] = 'Critical'
                elif new_on_hand < reorder_point:
                    updates['STATUS'] = 'Low Stock'
                else:
                    updates['STATUS'] = 'Healthy'
                
                self.airtable.update_record('FULFILLMENT INVENTORY', record['id'], updates)
                
        except Exception as e:
            print(f"Error adding inventory: {e}")
    
    def get_pending_purchase_orders(self) -> List[Dict]:
        """Get all POs that are ordered but not yet received"""
        try:
            formula = "{STATUS} = 'Ordered'"
            records = self.airtable.search_records('FULFILLMENT PURCHASE ORDERS', formula)
            return [{'id': r['id'], **r['fields']} for r in records]
        except Exception as e:
            print(f"Error getting pending POs: {e}")
            return []
    
    # ============ FINANCIAL INTEGRATION ============
    
    def _create_financial_records(self, contract_id: str, quantity: int, delivery_id: str):
        """Create invoice and expense records in VERTEX when delivery is complete"""
        try:
            # Get contract details
            contract = self.airtable.get_record('FULFILLMENT CONTRACTS', contract_id)
            fields = contract['fields']
            
            unit_price = fields.get('UNIT_PRICE', 0)
            unit_cost = fields.get('SUPPLIER_UNIT_COST', 0)
            client_name = fields.get('CLIENT_NAME', '')
            product = fields.get('PRODUCT', '')
            contract_name = fields.get('CONTRACT_NAME', '')
            
            # Create invoice in VERTEX
            invoice_amount = quantity * unit_price
            from api_server import VI, VE
            self.airtable.create_record('VERTEX INVOICES', {
                VI['invoice_number']:  f"INV-FULFIL-{delivery_id}",
                VI['invoice_date']:    datetime.now().date().isoformat(),
                VI['due_date']:        (datetime.now() + timedelta(days=30)).date().isoformat(),
                VI['client_name']:     client_name,
                VI['source_system']:   'Other',
                VI['source_record']:   delivery_id,
                VI['invoice_type']:    'Standard',
                VI['total_amount']:    invoice_amount,
                VI['payment_status']:  'Unpaid',
                VI['payment_terms']:   'Net 30',
                VI['notes']:           f'{contract_name} — Delivery {delivery_id} — {quantity} units of {product} — Contract {fields.get("CONTRACT_ID", "")}',
            })

            # Create expense for COGS in VERTEX
            expense_amount = quantity * unit_cost
            self.airtable.create_record('VERTEX EXPENSES', {
                VE['expense_date']:    datetime.now().date().isoformat(),
                VE['vendor_payee']:    f'COGS — {product}',
                VE['description']:     f'Inventory cost for {quantity} units delivered to {client_name}',
                VE['category']:        'Cost of Goods Sold',
                VE['amount']:          expense_amount,
                VE['payment_status']:  'Paid',
                VE['notes']:           f'Delivery {delivery_id} — Contract {fields.get("CONTRACT_ID", "")}',
            })
            
            print(f"✅ Financial records created: Revenue ${invoice_amount}, COGS ${expense_amount}, Profit ${invoice_amount - expense_amount}")
            
        except Exception as e:
            print(f"Error creating financial records: {e}")
    
    # ============ HELPER FUNCTIONS ============
    
    def _generate_sku(self, product_name: str) -> str:
        """Generate SKU from product name"""
        # Simple SKU generation - can be enhanced
        words = product_name.upper().replace('-', ' ').split()
        sku_parts = [w[:4] for w in words[:3]]
        return '-'.join(sku_parts)
    
    def _get_product_from_contract(self, contract_id: str) -> str:
        """Get product name from contract"""
        try:
            contract = self.airtable.get_record('FULFILLMENT CONTRACTS', contract_id)
            return contract['fields'].get('PRODUCT', '')
        except:
            return ''


# =====================================================================
# FULFILLMENT HANDLERS (for API endpoints)
# =====================================================================

def handle_create_fulfillment_contract(contract_data: Dict) -> Dict:
    """Create new fulfillment contract"""
    manager = FulfillmentManager()
    return manager.create_fulfillment_contract(contract_data)


def handle_get_active_contracts() -> List[Dict]:
    """Get all active contracts"""
    manager = FulfillmentManager()
    return manager.get_active_contracts()


def handle_get_contract_details(contract_id: str) -> Dict:
    """Get contract with deliveries and inventory"""
    manager = FulfillmentManager()
    return manager.get_contract_details(contract_id)


def handle_get_upcoming_deliveries(days_ahead: int = 7) -> List[Dict]:
    """Get deliveries due soon"""
    manager = FulfillmentManager()
    return manager.get_upcoming_deliveries(days_ahead)


def handle_update_delivery_status(delivery_id: str, updates: Dict) -> Dict:
    """Update delivery status"""
    manager = FulfillmentManager()
    return manager.update_delivery_status(delivery_id, updates)


def handle_check_inventory_health() -> Dict:
    """Run daily inventory health check"""
    manager = FulfillmentManager()
    return manager.check_inventory_health()


def handle_get_inventory_dashboard() -> List[Dict]:
    """Get inventory dashboard"""
    manager = FulfillmentManager()
    return manager.get_inventory_dashboard()


def handle_create_purchase_order(po_data: Dict) -> Dict:
    """Create purchase order"""
    manager = FulfillmentManager()
    return manager.create_purchase_order(po_data)


def handle_receive_purchase_order(po_id: str, received_data: Dict) -> Dict:
    """Receive purchase order"""
    manager = FulfillmentManager()
    return manager.receive_purchase_order(po_id, received_data)


def handle_get_pending_purchase_orders() -> List[Dict]:
    """Get pending POs"""
    manager = FulfillmentManager()
    return manager.get_pending_purchase_orders()


# =====================================================================
# DDCSS PROSPECT MINER — Corporate & Enterprise Sourcing Engine
# Free sources: SAM.gov federal primes, job posting boards, diversity news
# =====================================================================

class DDCSSProspectMiner:
    """
    Automated corporate prospect mining for DDCSS.
    Sources: SAM.gov federal primes, job postings, diversity news RSS.
    All free. No new tools required to start.
    """

    JOB_TITLES_TO_SERVICES = {
        'notary': 'Mobile Notary Services',
        'signing agent': 'Mobile Notary Services',
        'drug testing': 'Drug Testing Program Management',
        'drug test': 'Drug Testing Program Management',
        'fingerprint': 'Mobile Fingerprinting Services',
        'background check': 'Background Screening Services',
        'compliance officer': 'Compliance Consulting',
        'medical courier': 'Medical Specimen Transport',
        'document processor': 'Document Management Services',
        'courier': 'Courier & Delivery Services',
    }

    # Corporate sectors that buy DDI's direct-delivery services
    # (drug testing, fingerprinting, notary, courier, background screening)
    CORPORATE_HR_RSS_FEEDS = [
        # Healthcare systems — high-volume drug testing + background screening buyers
        'https://news.google.com/rss/search?q=michigan+hospital+system+hiring+expanding&hl=en-US&gl=US&ceid=US:en',
        'https://news.google.com/rss/search?q=michigan+healthcare+system+new+facility&hl=en-US&gl=US&ceid=US:en',
        # Staffing agencies — drug test every placed employee, recurring volume
        'https://news.google.com/rss/search?q=michigan+staffing+agency+expanding+workforce&hl=en-US&gl=US&ceid=US:en',
        # Manufacturing plants — DOT and safety drug testing required
        'https://news.google.com/rss/search?q=michigan+manufacturing+plant+opening+new&hl=en-US&gl=US&ceid=US:en',
        'https://news.google.com/rss/search?q=michigan+auto+supplier+plant+expansion+hiring&hl=en-US&gl=US&ceid=US:en',
        # Construction/logistics — DOT-regulated, drug testing mandatory
        'https://news.google.com/rss/search?q=michigan+logistics+distribution+center+opening&hl=en-US&gl=US&ceid=US:en',
    ]

    DIVERSITY_RSS_FEEDS = [
        'https://news.google.com/rss/search?q=supplier+diversity+initiative&hl=en-US&gl=US&ceid=US:en',
        'https://news.google.com/rss/search?q=women+owned+business+program+corporate&hl=en-US&gl=US&ceid=US:en',
        'https://news.google.com/rss/search?q=diverse+supplier+commitment+2026&hl=en-US&gl=US&ceid=US:en',
    ]

    JOB_RSS_FEEDS = [
        'https://www.indeed.com/rss?q=notary+michigan&l=Michigan',
        'https://www.indeed.com/rss?q=drug+testing+coordinator+michigan&l=Michigan',
        'https://www.indeed.com/rss?q=fingerprint+technician&l=Michigan',
        'https://www.indeed.com/rss?q=medical+courier+michigan&l=Michigan',
        'https://www.indeed.com/rss?q=signing+agent&l=Michigan',
    ]

    def __init__(self):
        self.airtable = AirtableClient()
        self.ai = AnthropicClient()

    # ------------------------------------------------------------------
    # SOURCE 1: CORPORATE HR SIGNALS (Google News RSS — free)
    # Targets sectors that buy DDI's direct-delivery services:
    # healthcare, staffing, manufacturing, logistics, construction.
    # These companies pay DDI directly — no government contract, no sub needed.
    # Drug testing via Quest/CRL network. Notary via signing agent network.
    # Fingerprinting: capture + channel per contract; DCSA SWFT not claimed (denied Mar 2026). Lakota/partner subs as needed.
    # ------------------------------------------------------------------

    def mine_corporate_hr_signals(self) -> List[Dict]:
        """
        Monitor industry news for corporate employers in sectors that need
        DDI's direct-delivery services: drug testing, fingerprinting, notary,
        courier, and background screening.

        Target sectors and why:
        - Healthcare systems: drug test all new hires + ongoing random testing
        - Staffing agencies: drug test every placed employee (recurring, high volume)
        - Manufacturing/auto: DOT and safety drug testing mandatory
        - Logistics/distribution: DOT-regulated workforce
        - Construction: safety-sensitive, drug testing required

        DDI delivers these services directly via Quest/CRL, fingerprinting
        partners (e.g. Lakota/WHORL path), and signing agent networks as applicable.
        """
        try:
            import feedparser
        except ImportError:
            return [{'error': 'feedparser not installed. Run: pip install feedparser'}]

        results = []
        seen_companies = set()

        for feed_url in self.CORPORATE_HR_RSS_FEEDS:
            try:
                feed = feedparser.parse(feed_url)
                for entry in feed.entries[:8]:
                    article_title = entry.get('title', '')
                    article_summary = entry.get('summary', '')
                    article_link = entry.get('link', '')

                    extracted = self._ai_extract_corporate_employer(article_title, article_summary)
                    if not extracted or not extracted.get('company'):
                        continue

                    company = extracted['company']
                    if company.lower() in seen_companies:
                        continue
                    seen_companies.add(company.lower())

                    sector = extracted.get('sector', 'Corporate')
                    service_need = extracted.get('service_need', 'Drug testing program')
                    pitch = extracted.get('pitch', '')

                    prospect = {
                        'Company Name': company,
                        'Industry': sector,
                        'Location': 'Michigan',
                        'Source': 'Corporate HR Signal Mining',
                        'AI Score': 80,
                        'Status': 'New Lead',
                        'Current Challenge': extracted.get('trigger', article_title),
                        'Business Goals': f'Need {service_need} — DDI delivers directly',
                        'Notes': f'{pitch} | Article: {article_link}',
                        'Date Found': datetime.now().strftime('%Y-%m-%d'),
                    }
                    saved = self._save_prospect(prospect)
                    if saved:
                        results.append(prospect)
            except Exception as e:
                results.append({'error': f'Corporate HR feed: {str(e)}'})

        return results

    def _ai_extract_corporate_employer(self, title: str, summary: str) -> Optional[Dict]:
        """
        Extract company and DDI service opportunity from a corporate expansion
        or hiring news article.
        """
        try:
            prompt = f"""Extract employer information from this business news article.
DDI (Dee Davis Inc.) provides: drug testing, fingerprinting, mobile notary, courier, background screening.
These services are needed by: healthcare systems, staffing agencies, manufacturers, logistics companies, construction firms.

Title: {title}
Summary: {summary}

Return JSON only (no markdown):
{{
  "company": "company name or null if not identifiable",
  "sector": "Healthcare | Staffing | Manufacturing | Logistics | Construction | Corporate",
  "trigger": "what event triggered this (new facility, hiring surge, expansion, etc.)",
  "service_need": "which DDI service this company most likely needs",
  "pitch": "one sentence pitch for why DDI should reach out now"
}}

If no specific company is identifiable, return {{"company": null}}."""
            response = self.ai.complete(prompt, max_tokens=200)
            clean = response.replace('```json', '').replace('```', '').strip()
            return json.loads(clean)
        except Exception:
            return None

    # ------------------------------------------------------------------
    # SOURCE 2: JOB POSTING MINING (Indeed RSS — free)
    # Companies hiring for roles DDI can replace = budget + urgency
    # ------------------------------------------------------------------

    def mine_job_postings(self) -> List[Dict]:
        """
        Monitor job boards for postings DDI can replace with a vendor contract.
        A company hiring a notary has budget approved and urgent need.
        Pitch: vendor solution vs. W-2 hire = faster, cheaper, no overhead.
        """
        try:
            import feedparser
        except ImportError:
            return [{'error': 'feedparser not installed. Run: pip install feedparser'}]

        results = []
        seen_companies = set()

        for feed_url in self.JOB_RSS_FEEDS:
            try:
                feed = feedparser.parse(feed_url)
                for entry in feed.entries[:15]:
                    title = entry.get('title', '').lower()
                    summary = entry.get('summary', '')
                    company = self._extract_company_from_job(entry)

                    if not company or company.lower() in seen_companies:
                        continue

                    service = self._map_job_to_service(title)
                    if not service:
                        continue

                    seen_companies.add(company.lower())

                    pitch = (
                        f"Hiring for '{entry.get('title', '')}' — "
                        f"DDI can provide {service} as a vendor: no W-2, no benefits, "
                        f"certified and insured, start immediately."
                    )

                    prospect = {
                        'Company Name': company,
                        'Industry': 'Corporate — Active Hiring Signal',
                        'Source': 'Job Posting Mining (Indeed)',
                        'AI Score': 78,
                        'Status': 'HOT LEAD',
                        'Current Challenge': f'Actively hiring for {entry.get("title", "")}',
                        'Business Goals': f'Need {service} capability immediately',
                        'Notes': pitch,
                        'Job Posting URL': entry.get('link', ''),
                        'Date Found': datetime.now().strftime('%Y-%m-%d'),
                    }
                    saved = self._save_prospect(prospect)
                    if saved:
                        results.append(prospect)
            except Exception as e:
                results.append({'error': f'Job feed {feed_url}: {str(e)}'})

        return results

    def _extract_company_from_job(self, entry: Dict) -> str:
        """Extract company name from Indeed RSS entry."""
        # Indeed puts company in the title: "Job Title - Company Name"
        title = entry.get('title', '')
        if ' - ' in title:
            parts = title.split(' - ')
            if len(parts) >= 2:
                return parts[-1].strip()
        author = entry.get('author', '')
        if author:
            return author.strip()
        return ''

    def _map_job_to_service(self, job_title_lower: str) -> str:
        """Map a job title to a DDI service type."""
        for keyword, service in self.JOB_TITLES_TO_SERVICES.items():
            if keyword in job_title_lower:
                return service
        return ''

    # ------------------------------------------------------------------
    # SOURCE 3: DIVERSITY NEWS MONITORING (Google News RSS — free)
    # Companies announcing diversity initiatives = HOT leads with budget
    # ------------------------------------------------------------------

    def mine_diversity_news(self) -> List[Dict]:
        """
        Monitor Google News RSS for companies announcing diversity initiatives.
        These are HOT leads — budget is approved, initiative is public, timing is perfect.
        """
        try:
            import feedparser
        except ImportError:
            return [{'error': 'feedparser not installed. Run: pip install feedparser'}]

        results = []
        seen_companies = set()

        for feed_url in self.DIVERSITY_RSS_FEEDS:
            try:
                feed = feedparser.parse(feed_url)
                for entry in feed.entries[:10]:
                    article_title = entry.get('title', '')
                    article_summary = entry.get('summary', '')
                    article_link = entry.get('link', '')

                    extracted = self._ai_extract_diversity_company(article_title, article_summary)
                    if not extracted or not extracted.get('company'):
                        continue

                    company = extracted['company']
                    if company.lower() in seen_companies:
                        continue
                    seen_companies.add(company.lower())

                    prospect = {
                        'Company Name': company,
                        'Industry': extracted.get('industry', 'Corporate'),
                        'Source': 'Diversity News Monitoring',
                        'AI Score': 85,
                        'Status': 'HOT LEAD',
                        'Current Challenge': extracted.get('initiative', 'Supplier diversity initiative announced'),
                        'Business Goals': 'Execute on diversity spend commitment with qualified EDWOSB vendors',
                        'Notes': f"Article: {article_title} | {article_link}",
                        'Date Found': datetime.now().strftime('%Y-%m-%d'),
                    }
                    saved = self._save_prospect(prospect)
                    if saved:
                        results.append(prospect)
            except Exception as e:
                results.append({'error': f'News feed: {str(e)}'})

        return results

    def _ai_extract_diversity_company(self, title: str, summary: str) -> Optional[Dict]:
        """Use AI to extract company and initiative details from a news article."""
        try:
            prompt = f"""Extract supplier diversity information from this article.

Title: {title}
Summary: {summary}

Return JSON only (no markdown):
{{
  "company": "company name or null if no specific company",
  "industry": "industry sector",
  "initiative": "brief description of the diversity initiative"
}}

If no specific company name is identifiable, return {{"company": null}}."""
            response = self.ai.complete(prompt, max_tokens=150)
            clean = response.replace('```json', '').replace('```', '').strip()
            return json.loads(clean)
        except Exception:
            return None

    # ------------------------------------------------------------------
    # DEDUPLICATION & SAVE
    # ------------------------------------------------------------------

    def _save_prospect(self, prospect: Dict) -> bool:
        """
        Save prospect to DDCSS Prospects table in Airtable.
        Skips if a record with the same company name already exists.
        """
        try:
            existing = self.airtable.get_all_records('DDCSS Prospects')
            existing_names = {
                r['fields'].get('Company Name', '').lower().strip()
                for r in existing
            }
            if prospect.get('Company Name', '').lower().strip() in existing_names:
                return False

            fields = {
                'Company Name': prospect.get('Company Name', ''),
                'Industry': prospect.get('Industry', ''),
                'Location': prospect.get('Location', ''),
                'Company Size': prospect.get('Company Size', ''),
                'Source': prospect.get('Source', ''),
                'Qualification Score': prospect.get('AI Score', 0),
                'Status': prospect.get('Status', 'New Lead'),
                'Current Challenge': prospect.get('Current Challenge', ''),
                'Business Goals': prospect.get('Business Goals', ''),
                'Notes': prospect.get('Notes', ''),
                'Created': datetime.now().isoformat(),
            }
            self.airtable.create_record('DDCSS Prospects', fields)
            return True
        except Exception:
            return False

    # ------------------------------------------------------------------
    # MASTER RUN — executes all free sources in one call
    # ------------------------------------------------------------------

    def run_all_free_sources(self) -> Dict:
        """
        Run all three free mining sources and return a summary.
        Call this daily or on-demand from the NEXUS dashboard.

        Sources:
        1. Corporate HR Signals — healthcare, staffing, manufacturing, logistics expanding in Michigan
        2. Job Postings — companies hiring for roles DDI can replace with a vendor contract
        3. Diversity News — companies announcing supplier diversity initiatives (hot leads)

        All three target corporate clients DDI can serve DIRECTLY without a government
        contract or a subcontractor. Drug testing via Quest/CRL, notary via signing
        agent network, fingerprinting via partner/cleared channel per solicitation.
        """
        summary = {
            'corporate_hr_signals': [],
            'job_postings': [],
            'diversity_news': [],
            'total_added': 0,
            'errors': [],
            'run_time': datetime.now().isoformat(),
        }

        print('DDCSS Mining: corporate HR signals...')
        hr = self.mine_corporate_hr_signals()
        summary['corporate_hr_signals'] = [p for p in hr if 'error' not in p]
        summary['errors'] += [p['error'] for p in hr if 'error' in p]

        print('DDCSS Mining: job postings...')
        jobs = self.mine_job_postings()
        summary['job_postings'] = [p for p in jobs if 'error' not in p]
        summary['errors'] += [p['error'] for p in jobs if 'error' in p]

        print('DDCSS Mining: diversity news...')
        news = self.mine_diversity_news()
        summary['diversity_news'] = [p for p in news if 'error' not in p]
        summary['errors'] += [p['error'] for p in news if 'error' in p]

        summary['total_added'] = (
            len(summary['corporate_hr_signals']) +
            len(summary['job_postings']) +
            len(summary['diversity_news'])
        )

        print(f"DDCSS Mining complete — {summary['total_added']} new prospects added.")
        return summary


# =====================================================================
# DDCSS PORTAL TRACKER — Corporate Supplier Registration Manager
# Tracks which corporate supplier diversity portals DDI has registered with,
# status, contacts, and follow-up actions.
# =====================================================================

class DDCSSPortalTracker:
    """
    Manages DDI's corporate supplier portal registrations.
    Tracks status, contacts, and next actions for each portal.

    Table: DDCSS Corporate Portals (Airtable)
    """

    # Pre-seeded list of priority portals for DDI's Michigan-based
    # drug testing, fingerprinting, notary, courier, and background screening services.
    # Grouped by sector — Michigan companies first, then national.
    SEED_PORTALS = [
        # ── MICHIGAN AUTOMOTIVE ────────────────────────────────────────
        {
            'Company': 'Kelly Services',
            'Sector': 'Staffing',
            'Portal URL': 'https://www.kellyservices.com/us/businesses/supplier-diversity/',
            'Why DDI': 'Headquartered in Troy, MI — same city as DDI. Drug tests every placed employee. High-volume recurring.',
            'Services to Register': 'Drug Testing, Background Screening, Fingerprinting',
            'Priority': 'HIGH',
            'Notes': 'Troy HQ — relationship opportunity. Target: VP HR or Supplier Diversity Manager.',
        },
        {
            'Company': 'General Motors',
            'Sector': 'Automotive',
            'Portal URL': 'https://supplier.gm.com',
            'Why DDI': 'Active WBENC corporate member. Mandated diversity spend. Large Michigan workforce.',
            'Services to Register': 'Drug Testing, Background Screening, Courier',
            'Priority': 'HIGH',
            'Notes': 'Register under supplier diversity program. EDWOSB + WBENC = double advantage.',
        },
        {
            'Company': 'Ford Motor Company',
            'Sector': 'Automotive',
            'Portal URL': 'https://www.fordsupplier.com',
            'Why DDI': 'Major WBENC supporter. WBE spend goals published annually.',
            'Services to Register': 'Drug Testing, Background Screening, Fingerprinting',
            'Priority': 'HIGH',
            'Notes': 'Ford Supplier Diversity has dedicated WBE portal. Upload WBENC cert.',
        },
        {
            'Company': 'Stellantis',
            'Sector': 'Automotive',
            'Portal URL': 'https://www.stellantis.com/en/company/suppliers',
            'Why DDI': 'Michigan-based, large hourly workforce, DOT and safety drug testing.',
            'Services to Register': 'Drug Testing, Background Screening',
            'Priority': 'HIGH',
            'Notes': 'Supplier registration via Covisint/Ariba. Check current portal URL.',
        },
        {
            'Company': 'Lear Corporation',
            'Sector': 'Automotive Supplier',
            'Portal URL': 'https://www.lear.com/suppliers',
            'Why DDI': 'Southfield, MI HQ. Large manufacturing workforce, drug testing required.',
            'Services to Register': 'Drug Testing, Background Screening',
            'Priority': 'MEDIUM',
            'Notes': 'Tier 1 auto supplier — safety-sensitive workforce.',
        },
        {
            'Company': 'BorgWarner',
            'Sector': 'Automotive Supplier',
            'Portal URL': 'https://www.borgwarner.com/suppliers',
            'Why DDI': 'Auburn Hills, MI HQ. Manufacturing plants statewide. DOT drug testing.',
            'Services to Register': 'Drug Testing, Background Screening',
            'Priority': 'MEDIUM',
            'Notes': 'Ariba-based supplier portal.',
        },
        # ── MICHIGAN ENERGY / UTILITIES ────────────────────────────────
        {
            'Company': 'DTE Energy',
            'Sector': 'Energy/Utilities',
            'Portal URL': 'https://www.dteenergy.com/us/en/business/about-dte-energy/supplier-diversity.html',
            'Why DDI': 'Michigan-based utility. Active supplier diversity program. Large regulated workforce requiring drug testing.',
            'Services to Register': 'Drug Testing, Background Screening, Courier',
            'Priority': 'HIGH',
            'Notes': 'DTE has published WBE/MBE spend goals. EDWOSB is qualifying cert.',
        },
        {
            'Company': 'Consumers Energy',
            'Sector': 'Energy/Utilities',
            'Portal URL': 'https://www.consumersenergy.com/company/suppliers/supplier-diversity',
            'Why DDI': 'Michigan utility, regulated DOT workforce, drug testing mandatory.',
            'Services to Register': 'Drug Testing, Background Screening',
            'Priority': 'HIGH',
            'Notes': 'Active supplier diversity program with WBE goals.',
        },
        # ── MICHIGAN HEALTHCARE ────────────────────────────────────────
        {
            'Company': 'Corewell Health',
            'Sector': 'Healthcare',
            'Portal URL': 'https://corewellhealth.org/about/suppliers',
            'Why DDI': 'Largest health system in Michigan (Beaumont + Spectrum merger). Drug tests all new hires + random testing. High volume.',
            'Services to Register': 'Drug Testing, Background Screening, Fingerprinting, Courier',
            'Priority': 'HIGH',
            'Notes': 'Formerly Beaumont Health + Spectrum Health. Combined = 60K+ employees.',
        },
        {
            'Company': 'Henry Ford Health',
            'Sector': 'Healthcare',
            'Portal URL': 'https://www.henryford.com/about/suppliers',
            'Why DDI': 'Detroit-based health system. Pre-employment and random drug testing for all clinical staff.',
            'Services to Register': 'Drug Testing, Background Screening, Fingerprinting',
            'Priority': 'HIGH',
            'Notes': 'Target: Supply Chain or HR procurement contact.',
        },
        {
            'Company': 'Ascension Michigan',
            'Sector': 'Healthcare',
            'Portal URL': 'https://ascension.org/suppliers',
            'Why DDI': 'Multi-hospital Michigan system. Drug testing and credentialing for all clinical and non-clinical staff.',
            'Services to Register': 'Drug Testing, Background Screening, Fingerprinting',
            'Priority': 'MEDIUM',
            'Notes': 'National system with Michigan footprint. May need national supplier registration.',
        },
        {
            'Company': 'McLaren Health Care',
            'Sector': 'Healthcare',
            'Portal URL': 'https://www.mclaren.org/main/suppliers',
            'Why DDI': 'Michigan-based, 14 hospitals. Pre-employment drug testing for all hires.',
            'Services to Register': 'Drug Testing, Background Screening',
            'Priority': 'MEDIUM',
            'Notes': 'Grand Blanc, MI HQ. Target procurement or HR.',
        },
        # ── MICHIGAN INSURANCE / FINANCE ──────────────────────────────
        {
            'Company': 'Blue Cross Blue Shield of Michigan',
            'Sector': 'Insurance',
            'Portal URL': 'https://www.bcbsm.com/index/about-bcbsm/supplier-diversity.html',
            'Why DDI': 'Active WBENC corporate member. Detroit-based, large employer. Supplier diversity program with WBE goals.',
            'Services to Register': 'Drug Testing, Background Screening, Notary',
            'Priority': 'HIGH',
            'Notes': 'BCBSM is a WBENC corporate member — actively seeking WBE vendors.',
        },
        {
            'Company': 'Rocket Companies / Quicken Loans',
            'Sector': 'Finance/Mortgage',
            'Portal URL': 'https://www.rocketcompanies.com/suppliers/',
            'Why DDI': 'Detroit HQ, thousands of employees. Pre-employment drug testing + notary services for mortgage closings.',
            'Services to Register': 'Drug Testing, Background Screening, Mobile Notary',
            'Priority': 'HIGH',
            'Notes': 'Notary angle: Rocket processes mortgage closings — mobile notary for signing events.',
        },
        # ── NATIONAL STAFFING (HIGH-VOLUME DRUG TESTING BUYERS) ──────
        {
            'Company': 'Manpower Group',
            'Sector': 'Staffing',
            'Portal URL': 'https://www.manpowergroup.com/suppliers',
            'Why DDI': 'Global staffing agency. Drug tests every placed employee. Recurring, high-volume buyer.',
            'Services to Register': 'Drug Testing, Background Screening, Fingerprinting',
            'Priority': 'HIGH',
            'Notes': 'Target Michigan regional office. Volume = recurring revenue.',
        },
        {
            'Company': 'Adecco Group',
            'Sector': 'Staffing',
            'Portal URL': 'https://www.adeccogroup.com/suppliers/',
            'Why DDI': 'Large staffing firm placing workers in Michigan manufacturers. Drug testing on every placement.',
            'Services to Register': 'Drug Testing, Background Screening',
            'Priority': 'MEDIUM',
            'Notes': 'Target Michigan branch managers directly.',
        },
        # ── NATIONAL RETAIL / LOGISTICS ──────────────────────────────
        {
            'Company': 'Amazon',
            'Sector': 'Logistics/Retail',
            'Portal URL': 'https://sellercentral.amazon.com/gp/homepage.html',
            'Why DDI': 'Multiple Michigan fulfillment centers. Pre-employment drug testing for thousands of warehouse hires. Large WBE program.',
            'Services to Register': 'Drug Testing, Background Screening',
            'Priority': 'MEDIUM',
            'Notes': 'Amazon Supplier Diversity portal separate from seller central. Search: amazon.com/supplier-diversity.',
        },
        {
            'Company': 'Home Depot',
            'Sector': 'Retail/Construction',
            'Portal URL': 'https://corporate.homedepot.com/suppliers',
            'Why DDI': 'Active supplier diversity program. Drug tests contractors and warehouse staff.',
            'Services to Register': 'Drug Testing, Background Screening',
            'Priority': 'LOW',
            'Notes': 'National program — may need to work through Michigan district contact.',
        },
        # ── NATIONAL FINANCIAL / BANKING ─────────────────────────────
        {
            'Company': 'JPMorgan Chase',
            'Sector': 'Banking/Finance',
            'Portal URL': 'https://www.jpmorganchase.com/impact/diversity/supplier-diversity',
            'Why DDI': 'Published $750M+ supplier diversity spend goal. Michigan offices.',
            'Services to Register': 'Drug Testing, Background Screening, Mobile Notary',
            'Priority': 'MEDIUM',
            'Notes': 'Large national bank — notary services for banking docs is an angle.',
        },
        # ── NATIONAL HEALTHCARE ──────────────────────────────────────
        {
            'Company': 'CVS Health / Caremark',
            'Sector': 'Healthcare/Retail',
            'Portal URL': 'https://www.cvshealth.com/news-and-insights/supplier-diversity',
            'Why DDI': 'National supplier diversity program. Michigan stores + PBM operations. Drug testing for all pharmacy staff.',
            'Services to Register': 'Drug Testing, Background Screening, Courier',
            'Priority': 'MEDIUM',
            'Notes': 'Pharmacy courier angle: specimen transport between CVS MinuteClinics.',
        },
    ]

    def __init__(self):
        self.airtable = AirtableClient()

    def seed_portals(self) -> Dict:
        """
        Populate the DDCSS Corporate Portals table with DDI's priority target list.
        Safe to run multiple times — skips portals already in the table.
        """
        try:
            existing = self.airtable.get_all_records('DDCSS Corporate Portals')
            existing_companies = {
                r['fields'].get('Company', '').lower().strip()
                for r in existing
            }
        except Exception:
            existing_companies = set()

        added = []
        skipped = []

        for portal in self.SEED_PORTALS:
            company_key = portal['Company'].lower().strip()
            if company_key in existing_companies:
                skipped.append(portal['Company'])
                continue
            try:
                self.airtable.create_record('DDCSS Corporate Portals', {
                    'Company': portal['Company'],
                    'Sector': portal['Sector'],
                    'Portal URL': portal['Portal URL'],
                    'Why DDI': portal['Why DDI'],
                    'Services to Register': portal['Services to Register'],
                    'Priority': portal['Priority'],
                    'Registration Status': 'Not Started',
                    'Notes': portal['Notes'],
                    'Date Added': datetime.now().strftime('%Y-%m-%d'),
                })
                added.append(portal['Company'])
                existing_companies.add(company_key)
            except Exception as e:
                skipped.append(f"{portal['Company']} (error: {e})")

        return {
            'success': True,
            'added': added,
            'skipped': skipped,
            'total_added': len(added),
            'total_skipped': len(skipped),
        }

    def get_portals(self, status_filter: Optional[str] = None) -> List[Dict]:
        """
        Get all corporate portals, optionally filtered by registration status.
        Statuses: Not Started | Registered | Pending Approval | Active | Needs Renewal
        """
        try:
            records = self.airtable.get_all_records('DDCSS Corporate Portals')
            portals = []
            for r in records:
                f = r['fields']
                if status_filter and f.get('Registration Status', '') != status_filter:
                    continue
                portals.append({
                    'id': r['id'],
                    'company': f.get('Company', ''),
                    'sector': f.get('Sector', ''),
                    'portalUrl': f.get('Portal URL', ''),
                    'whyDDI': f.get('Why DDI', ''),
                    'servicesToRegister': f.get('Services to Register', ''),
                    'priority': f.get('Priority', ''),
                    'registrationStatus': f.get('Registration Status', 'Not Started'),
                    'accountNumber': f.get('Account/Confirmation Number', ''),
                    'contactName': f.get('Primary Contact Name', ''),
                    'contactTitle': f.get('Primary Contact Title', ''),
                    'contactEmail': f.get('Primary Contact Email', ''),
                    'registrationDate': f.get('Registration Date', ''),
                    'lastLogin': f.get('Last Login Date', ''),
                    'nextAction': f.get('Next Action', ''),
                    'nextActionDate': f.get('Next Action Date', ''),
                    'notes': f.get('Notes', ''),
                })
            priority_order = {'HIGH': 0, 'MEDIUM': 1, 'LOW': 2}
            portals.sort(key=lambda x: priority_order.get(x['priority'], 3))
            return portals
        except Exception as e:
            return [{'error': str(e)}]

    def update_portal(self, portal_id: str, updates: Dict) -> Dict:
        """Update a portal record — status, contact info, next action, etc."""
        try:
            field_map = {
                'registrationStatus': 'Registration Status',
                'accountNumber': 'Account/Confirmation Number',
                'contactName': 'Primary Contact Name',
                'contactTitle': 'Primary Contact Title',
                'contactEmail': 'Primary Contact Email',
                'registrationDate': 'Registration Date',
                'lastLogin': 'Last Login Date',
                'nextAction': 'Next Action',
                'nextActionDate': 'Next Action Date',
                'notes': 'Notes',
            }
            fields = {field_map[k]: v for k, v in updates.items() if k in field_map}
            self.airtable.update_record('DDCSS Corporate Portals', portal_id, fields)
            return {'success': True, 'id': portal_id}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def get_dashboard_summary(self) -> Dict:
        """Quick summary of portal registration progress for the DDCSS dashboard."""
        portals = self.get_portals()
        if portals and 'error' in portals[0]:
            return {'error': portals[0]['error']}

        status_counts = {}
        priority_counts = {'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
        not_started_high = []

        for p in portals:
            status = p['registrationStatus']
            status_counts[status] = status_counts.get(status, 0) + 1
            priority_counts[p.get('priority', 'LOW')] = priority_counts.get(p.get('priority', 'LOW'), 0) + 1
            if status == 'Not Started' and p.get('priority') == 'HIGH':
                not_started_high.append(p['company'])

        return {
            'total_portals': len(portals),
            'status_breakdown': status_counts,
            'high_priority_not_started': not_started_high,
            'active_count': status_counts.get('Active', 0),
            'registered_count': status_counts.get('Registered', 0) + status_counts.get('Pending Approval', 0),
            'not_started_count': status_counts.get('Not Started', 0),
        }


# =====================================================================
# MAIN - For testing
# =====================================================================

if __name__ == "__main__":
    print("NEXUS Backend Initialized")
    print("=" * 60)
    
    # Validate config
    try:
        Config.validate()
        print("✅ Configuration valid")
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        exit(1)
    
    # Test Airtable connection
    try:
        airtable = AirtableClient()
        # Note: Will need base ID set in environment
        print("✅ Airtable client initialized")
    except Exception as e:
        print(f"❌ Airtable error: {e}")
    
    # Test Anthropic connection
    try:
        ai = AnthropicClient()
        test_response = ai.complete("Say 'NEXUS is online!'", max_tokens=100)
        print(f"✅ Anthropic connected: {test_response}")
    except Exception as e:
        print(f"❌ Anthropic error: {e}")
    
    print("=" * 60)
    print("Backend ready for deployment!")
