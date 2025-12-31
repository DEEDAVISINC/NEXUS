"""
NEXUS Backend - DEE DAVIS INC
Complete AI-powered business automation system
"""

import os
import json
import anthropic
from pyairtable import Api
from datetime import datetime
import re
from typing import Dict, List, Optional

# =====================================================================
# CONFIGURATION
# =====================================================================

class Config:
    """Configuration from environment variables"""
    ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY', '')
    AIRTABLE_API_KEY = os.environ.get('AIRTABLE_API_KEY', '')
    AIRTABLE_BASE_ID = os.environ.get('AIRTABLE_BASE_ID', '')
    
    @classmethod
    def validate(cls):
        """Validate all required credentials are present"""
        if not cls.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY not set")
        if not cls.AIRTABLE_API_KEY:
            raise ValueError("AIRTABLE_API_KEY not set")
        return True

# =====================================================================
# AIRTABLE CLIENT
# =====================================================================

class AirtableClient:
    """Handle all Airtable operations"""
    
    def __init__(self):
        self.api = Api(Config.AIRTABLE_API_KEY)
        self.base_id = Config.AIRTABLE_BASE_ID
        
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
        self.client = anthropic.Anthropic(api_key=Config.ANTHROPIC_API_KEY)
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
                existing = self.airtable.search_records('Contacts', formula)
                
                # Prepare fields
                fields = {
                    'Name': contact.get('name', ''),
                    'Email': email,
                    'Phone': contact.get('phone', ''),
                    'Title': contact.get('title', ''),
                    'Organization': contact.get('organization', ''),
                    'Role Category': contact.get('categorization', {}).get('role', ''),
                    'Priority': contact.get('categorization', {}).get('priority', 'MEDIUM'),
                    'Notes': contact.get('context', {}).get('notes', '')
                }
                
                if existing:
                    # Update existing contact
                    record_id = existing[0]['id']
                    updated = self.airtable.update_record('Contacts', record_id, fields)
                    stored_contacts.append({
                        'action': 'updated',
                        'record_id': record_id,
                        'email': email
                    })
                else:
                    # Create new contact
                    created = self.airtable.create_record('Contacts', fields)
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
        records = self.airtable.get_all_records('Opportunities')
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
            self.airtable.update_record('Opportunities', opportunity_id, {
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
        records = self.airtable.get_all_records('Opportunities')
        opportunity = next((r for r in records if r['id'] == opportunity_id), None)
        
        if not opportunity:
            return {"error": "Opportunity not found"}
        
        fields = opportunity['fields']
        
        # Get relevant contacts
        contacts = self.airtable.get_all_records('Contacts')
        
        # Get products
        products = self.airtable.get_all_records('Products')
        
        prompt = f"""
Generate a professional government contract proposal for:

OPPORTUNITY:
RFP: {fields.get('RFP Number')}
Agency: {fields.get('Agency Name')}
Value: ${fields.get('Contract Value', 0):,.0f}
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

Generate proposal as JSON:
{{
  "executive_summary": "2-3 paragraph summary",
  "technical_approach": "Detailed technical approach (5+ paragraphs)",
  "staffing_plan": "Detailed staffing (NOT 'we will post an ad')",
  "past_performance": "Relevant contract experience with specifics",
  "pricing": {{
    "total": 0,
    "breakdown": {{}},
    "justification": "Why this price is reasonable"
  }},
  "compliance_checklist": {{
    "format_compliant": true,
    "all_questions_answered": true,
    "staffing_detailed": true,
    "pricing_realistic": true,
    "reps_certs_included": true
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
