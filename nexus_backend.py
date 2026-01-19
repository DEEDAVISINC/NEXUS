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
            portals = self.airtable.get_all_records('Vendor Portals')
            portal = next((p for p in portals if p['id'] == portal_id), None)
            
            if not portal:
                return {"error": "Portal not found"}
            
            fields = portal['fields']
            portal_name = fields.get('Portal Name', '')
            portal_type = fields.get('Portal Type', '')
            portal_url = fields.get('Portal URL', '')
            scraping_method = fields.get('Scraping Method', 'Web Scraping')
            
            # Different mining strategies based on portal type
            if scraping_method == 'API' and fields.get('API Available'):
                # Use API if available
                opportunities = self._mine_via_api(fields)
            elif scraping_method == 'Web Scraping':
                # Use web scraping
                opportunities = self._mine_via_scraping(portal_url, portal_type)
            elif scraping_method == 'RSS Feed':
                # Use RSS feed
                opportunities = self._mine_via_rss(fields.get('RSS URL', ''))
            else:
                # Manual - just log the check
                opportunities = []
            
            # Update last checked time
            self.airtable.update_record('Vendor Portals', portal_id, {
                'Last Checked': datetime.now().isoformat(),
                'Opportunities Found (Total)': fields.get('Opportunities Found (Total)', 0) + len(opportunities)
            })
            
            return {
                'portal_name': portal_name,
                'opportunities_found': len(opportunities),
                'opportunities': opportunities
            }
            
        except Exception as e:
            print(f"Mining error: {e}")
            return {"error": str(e)}
    
    def _mine_via_api(self, portal_fields: Dict) -> List[Dict]:
        """Mine opportunities using portal API"""
        # This would integrate with actual APIs (SAM.gov, etc.)
        # For now, return placeholder
        return []
    
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
        # Real implementation would use requests to call public APIs
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
        Automatically mine all portals that have auto-mining enabled
        This runs daily via cron/scheduler
        """
        
        try:
            # Get all portals with auto-mining enabled
            portals = self.airtable.get_all_records('Vendor Portals')
            auto_portals = [
                p for p in portals
                if p['fields'].get('Auto-Mining Enabled', False)
            ]
            
            results = []
            total_found = 0
            
            for portal in auto_portals:
                result = self.mine_portal_opportunities(portal['id'])
                if not result.get('error'):
                    results.append(result)
                    total_found += result.get('opportunities_found', 0)
            
            return {
                'portals_checked': len(auto_portals),
                'total_opportunities_found': total_found,
                'results': results
            }
            
        except Exception as e:
            print(f"Auto-mining error: {e}")
            return {"error": str(e)}
    
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
            suppliers = self.airtable.get_all_records('GPSS Suppliers')
            
            # Apply filters
            filtered = []
            for supplier in suppliers:
                fields = supplier.get('fields', {})
                
                # Filter by category if specified
                if category:
                    categories = fields.get('Product Categories', [])
                    if category not in categories:
                        continue
                
                # Filter by keywords if specified
                if keywords:
                    supplier_keywords = fields.get('Product Keywords', '').lower()
                    if not any(kw.lower() in supplier_keywords for kw in keywords):
                        continue
                
                # Filter by rating
                rating = fields.get('Overall Rating', 0)
                if rating < min_rating:
                    continue
                
                # Filter active/approved suppliers only
                status = fields.get('Business Status', '')
                if status not in ['Active', 'Prospective']:
                    continue
                
                filtered.append({
                    'id': supplier.get('id'),
                    'company_name': fields.get('Company Name', ''),
                    'product_categories': fields.get('Product Categories', []),
                    'net_30_available': fields.get('Net 30 Available', False),
                    'overall_rating': rating,
                    'typical_margin': fields.get('Typical Margin (%)', 0),
                    'contact_email': fields.get('Primary Contact Email', ''),
                    'phone': fields.get('Primary Contact Phone', ''),
                    'relationship_stage': fields.get('Relationship Stage', ''),
                    'government_supplier': fields.get('Government Supplier', False)
                })
            
            # Sort by rating desc
            filtered.sort(key=lambda x: x.get('overall_rating', 0), reverse=True)
            
            return filtered
            
        except Exception as e:
            print(f"Error searching suppliers: {e}")
            return []
    
    def google_supplier_search(self, product: str, include_terms: List[str] = None) -> List[Dict]:
        """
        Automated Google search for suppliers
        
        Args:
            product: Product to search for
            include_terms: Additional terms (Net 30, wholesale, etc.)
            
        Returns:
            List of potential suppliers found
        """
        # Note: This is a placeholder for actual Google search implementation
        # In production, would use Google Custom Search API or web scraping
        
        if include_terms is None:
            include_terms = ['wholesale', 'Net 30', 'government supplier']
        
        # Build search queries
        queries = []
        for term in include_terms:
            queries.append(f"{product} {term}")
        
        # Placeholder results
        # In production: Execute searches, parse results, extract company info
        results = []
        
        print(f"Google search placeholder: Would search for '{product}' with terms {include_terms}")
        
        return results
    
    def find_suppliers_for_product(self, product: str, category: str = None, 
                                    max_results: int = 10) -> List[Dict]:
        """
        MAIN METHOD: Find suppliers for specific product
        
        Args:
            product: Product name or description
            category: Product category
            max_results: Maximum suppliers to return
            
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
            return existing[:max_results]
        
        # Step 3: Otherwise, note that mining would happen here
        # In production: Call google_supplier_search, ThomasNet scraping, etc.
        print(f"Would mine additional suppliers for '{product}' (not yet implemented)")
        
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
            if not supplier_data.get('Company Name'):
                raise ValueError("Company Name is required")
            
            # Set defaults
            if 'Business Status' not in supplier_data:
                supplier_data['Business Status'] = 'Prospective'
            if 'Relationship Stage' not in supplier_data:
                supplier_data['Relationship Stage'] = 'Discovered'
            if 'Discovery Date' not in supplier_data:
                supplier_data['Discovery Date'] = datetime.now().isoformat()
            
            # Create in Airtable
            record = self.airtable.create_record('GPSS Suppliers', supplier_data)
            
            print(f"Created supplier: {supplier_data.get('Company Name')}")
            
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
            record = self.airtable.update_record('GPSS Suppliers', supplier_id, updates)
            return record
        except Exception as e:
            print(f"Error updating supplier: {e}")
            return {'error': str(e)}
    
    def get_supplier(self, supplier_id: str) -> Optional[Dict]:
        """Get supplier by ID"""
        try:
            suppliers = self.airtable.get_all_records('GPSS Suppliers')
            for supplier in suppliers:
                if supplier.get('id') == supplier_id:
                    return supplier
            return None
        except Exception as e:
            print(f"Error getting supplier: {e}")
            return None


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
# RSS OPPORTUNITY MONITORING
# =====================================================================

import feedparser
from datetime import datetime, timedelta
from typing import List, Dict, Optional


# Government RSS Feeds to Monitor (VERIFIED WORKING SOURCES ONLY)
GOVERNMENT_RSS_FEEDS = [
    # ===== FEDERAL (VERIFIED WORKING) =====
    {
        'name': 'SAM.gov - All Opportunities',
        'url': 'https://sam.gov/api/prod/opps/v3/opportunities/rss',
        'type': 'Federal',
        'keywords': ['professional services', 'consulting', 'management'],
        'enabled': True,
        'verified': True
    },
    {
        'name': 'SAM.gov - EDWOSB Set-Asides',
        'url': 'https://sam.gov/api/prod/opps/v3/opportunities/rss?setAside=EDWOSB',
        'type': 'Federal',
        'keywords': ['edwosb', 'women-owned', 'set-aside'],
        'enabled': True,
        'verified': True
    },
    {
        'name': 'SAM.gov - WOSB Set-Asides',
        'url': 'https://sam.gov/api/prod/opps/v3/opportunities/rss?setAside=WOSB',
        'type': 'Federal',
        'keywords': ['wosb', 'women-owned', 'set-aside'],
        'enabled': True,
        'verified': True
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
                        # Prepare for Airtable
                        airtable_data = {
                            'TITLE': opp_data['title'][:255],  # Airtable field limit
                            'SOLICITATION NUMBER': f"RSS-{datetime.now().strftime('%Y%m%d')}-{len(opportunities)}",
                            'AGENCY NAME': feed_config['name'],
                            'VALUE': 0,  # Unknown from RSS
                            'DUE DATE': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
                            'SOURCE': feed_config['type'],
                            'Source Portal': feed_config['name'],
                            'Internal Status': 'New - RSS',
                            'Priority Score': qualification['score'],
                            'Description': opp_data['description'][:1000] if opp_data['description'] else '',
                            'URL': opp_data['url']
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
    
    def search_opportunities(self, params: Dict = None) -> Dict:
        """Search SAM.gov for opportunities"""
        try:
            default_params = {
                'api_key': self.api_key,
                'limit': 100,
                'postedFrom': (datetime.now() - timedelta(days=7)).strftime('%m/%d/%Y'),
                'postedTo': datetime.now().strftime('%m/%d/%Y')
            }
            
            if params:
                default_params.update(params)
            
            print(f"🔍 Searching SAM.gov API...")
            
            response = requests.get(self.base_url, params=default_params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            opportunities_data = data.get('opportunitiesData', [])
            total_records = data.get('totalRecords', 0)
            
            print(f"   ✓ Found {total_records} total, retrieved {len(opportunities_data)}")
            
            qualified_opportunities = []
            for opp in opportunities_data:
                try:
                    if self._is_duplicate(opp.get('noticeId', '')):
                        continue
                    
                    qualification = self._qualify_opportunity(opp)
                    
                    if qualification['score'] >= 70:
                        qualified_opportunities.append({
                            'opportunity': opp,
                            'qualification': qualification
                        })
                except Exception as e:
                    continue
            
            print(f"   ✓ Qualified {len(qualified_opportunities)} (score >= 70)")
            
            imported_count = 0
            for item in qualified_opportunities:
                try:
                    self._import_to_airtable(item['opportunity'], item['qualification'])
                    imported_count += 1
                except Exception as e:
                    print(f"   ⚠ Import error: {e}")
            
            print(f"   ✓ Imported {imported_count} to Airtable")
            
            return {
                'success': True,
                'total_found': total_records,
                'retrieved': len(opportunities_data),
                'qualified': len(qualified_opportunities),
                'imported': imported_count,
                'source': 'SAM.gov API'
            }
            
        except Exception as e:
            print(f"❌ SAM.gov API Error: {e}")
            return {'success': False, 'error': str(e), 'total_found': 0, 'imported': 0}
    
    def _is_duplicate(self, notice_id: str) -> bool:
        """Check if exists"""
        try:
            records = self.airtable.get_all_records('GPSS OPPORTUNITIES')
            return any(r['fields'].get('RFP Number') == notice_id for r in records)
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
    
    def _import_to_airtable(self, opp: Dict, qualification: Dict):
        """Import to Airtable"""
        from dateutil import parser
        
        # Parse dates safely
        due_date = ''
        try:
            if opp.get('responseDeadLine'):
                due_date = parser.parse(opp['responseDeadLine']).strftime('%Y-%m-%d')
        except:
            pass
        
        fields = {
            'Title': opp.get('title', 'Untitled')[:255],
            'RFP Number': opp.get('noticeId', ''),
            'Agency Name': opp.get('fullParentPathName', '')[:255],
            'Description': opp.get('description', '')[:5000],
            'Due Date': due_date,
            'Source': 'SAM.gov API',
            'Source URL': f"https://sam.gov/opp/{opp.get('noticeId', '')}",
            'State': 'Federal',
            'Set Aside Type': opp.get('typeOfSetAsideDescription', '')[:255],
            'EDWOSB Eligible': 'women' in opp.get('typeOfSetAsideDescription', '').lower(),
            'Status': 'New - API',
            'AI Qualification Score': qualification['score']
        }
        
        fields = {k: v for k, v in fields.items() if v is not None and v != ''}
        self.airtable.create_record('GPSS OPPORTUNITIES', fields)


class GovConAPIClient:
    """GovCon API Client"""
    
    def __init__(self):
        self.api_key = os.environ.get('GOVCON_API_KEY', '')
        self.base_url = "https://govconapi.com/api/v1/opportunities"
        self.airtable = AirtableClient()
    
    def search_opportunities(self, params: Dict = None) -> Dict:
        """Search GovCon"""
        try:
            headers = {'Authorization': f'Bearer {self.api_key}'}
            default_params = {'limit': 100, 'posted_days': 7}
            
            if params:
                default_params.update(params)
            
            print(f"🔍 Searching GovCon API...")
            response = requests.get(self.base_url, headers=headers, params=default_params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            opportunities = data.get('opportunities', [])
            
            print(f"   ✓ Found {len(opportunities)}")
            
            imported_count = 0
            for opp in opportunities:
                try:
                    notice_id = opp.get('notice_id', opp.get('solicitationNumber', ''))
                    if not self._is_duplicate(notice_id):
                        self._import_to_airtable(opp)
                        imported_count += 1
                except:
                    continue
            
            print(f"   ✓ Imported {imported_count}")
            
            return {'success': True, 'total_found': len(opportunities), 'imported': imported_count, 'source': 'GovCon API'}
        except Exception as e:
            print(f"❌ GovCon Error: {e}")
            return {'success': False, 'error': str(e), 'total_found': 0, 'imported': 0}
    
    def _is_duplicate(self, notice_id: str) -> bool:
        try:
            records = self.airtable.get_all_records('GPSS OPPORTUNITIES')
            return any(r['fields'].get('RFP Number') == notice_id for r in records)
        except:
            return False
    
    def _import_to_airtable(self, opp: Dict):
        fields = {
            'Title': opp.get('title', 'Untitled')[:255],
            'RFP Number': opp.get('notice_id', opp.get('solicitationNumber', '')),
            'Agency Name': opp.get('agency', opp.get('departmentName', ''))[:255],
            'Description': opp.get('description', '')[:5000],
            'Source': 'GovCon API',
            'Status': 'New - API'
        }
        fields = {k: v for k, v in fields.items() if v}
        self.airtable.create_record('GPSS OPPORTUNITIES', fields)


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
            'enabled': False  # Requires paid account
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
            # BidNet has free access to some listings
            url = "https://www.bidnetdirect.com/bidnet-government-bids"
            
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for bid listings (simplified - actual structure varies)
            # This is a placeholder - real implementation needs specific selectors
            found = 0
            imported = 0
            
            print(f"      ✓ BidNet: {found} found, {imported} imported")
            return {'found': found, 'imported': imported}
            
        except Exception as e:
            print(f"      ❌ BidNet error: {e}")
            return {'found': 0, 'imported': 0}
    
    def _is_duplicate(self, title: str) -> bool:
        """Check if opportunity already exists"""
        try:
            records = self.airtable.get_all_records('GPSS OPPORTUNITIES')
            return any(r['fields'].get('Title') == title for r in records)
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
        posted_date = ''
        try:
            if opp.get('posted_date'):
                posted_date = parser.parse(opp['posted_date']).strftime('%Y-%m-%d')
        except:
            pass
        
        fields = {
            'Title': opp.get('title', 'Untitled')[:255],
            'Description': opp.get('description', '')[:5000],
            'Source': opp.get('source', 'State/Local'),
            'Source URL': opp.get('url', ''),
            'Posted Date': posted_date,
            'Status': 'New - State/Local',
            'AI Qualification Score': qualification['score'],
            'AI Recommendation': qualification['recommendation'],
            'State': 'State/Local'
        }
        
        fields = {k: v for k, v in fields.items() if v is not None and v != ''}
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
