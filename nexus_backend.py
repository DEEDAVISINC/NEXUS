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
    
    def recommend_subcontractors(self, opportunity_id: str, needed_skills: List[str], contract_value: float = None) -> Dict:
        """
        Find and rank subcontractors based on needed skills
        Returns: Top 5 recommended subcontractors with AI reasoning
        """
        try:
            # Search subcontractor database
            all_subs = self.airtable.get_all_records("GPSS SUBCONTRACTORS")
            
            if not all_subs:
                return {
                    "success": False,
                    "message": "No subcontractors found in database. Please add subcontractors first.",
                    "recommended_subcontractors": []
                }
            
            # AI scores each subcontractor
            scored_subs = []
            for sub_record in all_subs:
                sub = sub_record['fields']
                
                # Skip if not available
                if sub.get('STATUS', '').lower() not in ['active', 'available', '']:
                    continue
                
                # AI scores this subcontractor
                score_prompt = f"""
                Score this subcontractor for a contract requiring: {', '.join(needed_skills)}
                Contract value: ${contract_value if contract_value else 'Unknown'}
                
                SUBCONTRACTOR:
                Name: {sub.get('COMPANY_NAME', 'N/A')}
                Capabilities: {sub.get('CAPABILITIES', 'N/A')}
                Past Performance: {sub.get('PAST_PERFORMANCE', 'N/A')}
                Rating: {sub.get('RATING', 'N/A')}/5
                Location: {sub.get('LOCATION', 'N/A')}
                Certifications: {sub.get('CERTIFICATIONS', 'N/A')}
                
                Score 0-100 based on:
                - Skills match (most important)
                - Past performance and rating
                - Availability
                - Certifications
                
                Return JSON:
                {{
                    "score": 85,
                    "reason": "Strong cybersecurity expertise with 5 similar contracts completed. 4.8★ rating.",
                    "strengths": ["skill1", "skill2"],
                    "concerns": ["concern1"] or []
                }}
                """
                
                try:
                    scoring = self.ai.generate_with_json(score_prompt, model="claude-sonnet-4-20250514")
                    scored_subs.append({
                        "id": sub_record['id'],
                        "name": sub.get('COMPANY_NAME', 'Unknown'),
                        "score": scoring.get('score', 0),
                        "reason": scoring.get('reason', ''),
                        "strengths": scoring.get('strengths', []),
                        "concerns": scoring.get('concerns', []),
                        "capabilities": sub.get('CAPABILITIES', ''),
                        "rating": sub.get('RATING', 'N/A'),
                        "location": sub.get('LOCATION', ''),
                        "contact": sub.get('CONTACT_EMAIL', '')
                    })
                except Exception as e:
                    print(f"Error scoring subcontractor {sub.get('COMPANY_NAME')}: {e}")
                    continue
            
            # Sort by score
            scored_subs.sort(key=lambda x: x['score'], reverse=True)
            top_5 = scored_subs[:5]
            
            # Store recommendation
            if top_5:
                recommendation_record = self.airtable.create_record("AI RECOMMENDATIONS", {
                    "OPPORTUNITY": [opportunity_id],
                    "TYPE": "Subcontractor Recommendation",
                    "RECOMMENDATION": f"Top choice: {top_5[0]['name']}",
                    "CONFIDENCE": top_5[0]['score'],
                    "REASONING": top_5[0]['reason'],
                    "STATUS": "Pending Approval",
                    "CREATED": datetime.now().isoformat()
                })
                
                return {
                    "success": True,
                    "recommended_subcontractors": top_5,
                    "total_found": len(scored_subs),
                    "recommendation_id": recommendation_record['id'],
                    "ai_top_pick": top_5[0] if top_5 else None,
                    "message": f"AI analyzed {len(scored_subs)} subcontractors. Top recommendation: {top_5[0]['name']} (score: {top_5[0]['score']}/100)"
                }
            else:
                return {
                    "success": False,
                    "message": "No suitable subcontractors found",
                    "recommended_subcontractors": []
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
                    scored_suppliers.append({
                        "id": sup_record['id'],
                        "name": sup.get('COMPANY_NAME', 'Unknown'),
                        "score": scoring.get('score', 0),
                        "reason": scoring.get('reason', ''),
                        "pricing_estimate": scoring.get('estimated_pricing', 'unknown'),
                        "gsa_schedule": sup.get('GSA_SCHEDULE', 'No'),
                        "payment_terms": sup.get('PAYMENT_TERMS', 'Unknown'),
                        "rating": sup.get('RATING', 'N/A'),
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
# AI RECOMMENDATION SYSTEM HANDLERS
# =====================================================================

def handle_analyze_capability_gap(opportunity_id: str) -> Dict:
    """
    Analyze opportunity and recommend self-perform vs partner approach
    AI suggests best path, user approves/denies
    """
    agent = AIRecommendationAgent()
    return agent.analyze_capability_gap(opportunity_id)


def handle_recommend_subcontractors(opportunity_id: str, needed_skills: List[str], contract_value: float = None) -> Dict:
    """
    AI recommends top 5 subcontractors based on needed skills
    Returns ranked list with reasoning for each
    """
    agent = AIRecommendationAgent()
    return agent.recommend_subcontractors(opportunity_id, needed_skills, contract_value)


def handle_recommend_suppliers(opportunity_id: str, product_description: str) -> Dict:
    """
    AI recommends top 10 suppliers for product-based opportunities
    Returns ranked list with reasoning for each
    """
    agent = AIRecommendationAgent()
    return agent.recommend_suppliers(opportunity_id, product_description)


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
                    if not any(kw.lower() in supplier_keywords for kw in keywords):
                        continue
                
                # Filter by rating
                rating = fields.get('OVERALL RATING', 0)
                if rating < min_rating:
                    continue
                
                # Filter out explicitly inactive suppliers only
                status = fields.get('BUSINESS STATUS', '')
                if status in ['Inactive', 'Blocked', 'Rejected']:
                    continue
                
                # Skip suppliers with no company name
                company_name = fields.get('COMPANY NAME', '').strip()
                if not company_name:
                    continue
                
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
                    'business_status': fields.get('BUSINESS STATUS', ''),
                    'discovery_method': fields.get('DISCOVERY METHOD', ''),
                    'discovery_date': fields.get('DISCOVERY DATE', ''),
                    'discovered_by': fields.get('DISCOVERED BY', '')
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
        Search ThomasNet for manufacturers/wholesalers
        Requires: pip install playwright && python -m playwright install chromium
        Requires: THOMASNET_EMAIL and THOMASNET_PASSWORD in .env
        
        Args:
            product: Product to search for
            max_results: Maximum suppliers to return
            
        Returns:
            List of supplier dictionaries ready for Airtable
        """
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
            print("  ❌ Playwright not installed. Run: pip install playwright && python -m playwright install chromium\n")
            return []
        except Exception as e:
            print(f"  ❌ ThomasNet search error: {e}\n")
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
    {
        'name': 'NAICS 624230 - Emergency & Relief Services',
        'url': 'https://sam.gov/api/prod/opps/v3/opportunities/rss?naics=624230',
        'type': 'Federal',
        'keywords': ['emergency', 'disaster', 'relief', 'crisis', 'response'],
        'enabled': True,
        'naics': '624230'
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
    
    def search_opportunities(self, params: Dict = None) -> Dict:
        """Search SAM.gov for opportunities"""
        try:
            # Build request parameters
            default_params = {
                'limit': 100,
                'postedFrom': (datetime.now() - timedelta(days=7)).strftime('%m/%d/%Y'),
                'postedTo': datetime.now().strftime('%m/%d/%Y')
            }
            
            if params:
                default_params.update(params)
            
            # Build headers with API key
            headers = {}
            if self.api_key:
                headers['X-Api-Key'] = self.api_key
                print(f"🔍 Searching SAM.gov API with authentication...")
            else:
                print("⚠️  SAM_GOV_API_KEY not configured - using public access (limited)")
                print("   Get a free API key from: https://sam.gov/data-services/")
            
            print(f"   Request URL: {self.base_url}")
            print(f"   Date Range: {default_params['postedFrom']} to {default_params['postedTo']}")
            
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
            
            for idx, opp in enumerate(opportunities_data, 1):
                try:
                    notice_id = opp.get('noticeId', '')
                    
                    if self._is_duplicate(notice_id):
                        skipped_duplicates += 1
                        continue
                    
                    # Skip qualification for now - just import everything
                    # qualification = self._qualify_opportunity(opp)
                    # if qualification['score'] >= 70:
                    qualified_opportunities.append({
                        'opportunity': opp,
                        'qualification': {'score': 75, 'reasoning': 'Auto-imported from SAM.gov'}
                    })
                    
                except Exception as e:
                    if idx <= 3:
                        print(f"   ⚠️  Error processing opportunity {idx}: {str(e)[:100]}")
                    continue
            
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
        
        # Map to actual Airtable field names
        fields = {
            'Name': opp.get('title', 'Untitled')[:255],
            'RFP NUMBER': opp.get('noticeId', ''),
            'Status': 'New - API',
        }
        
        # Add optional fields
        if due_date:
            fields['Deadline'] = due_date
        
        self.airtable.create_record('GPSS OPPORTUNITIES', fields)


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
            
            notice_types = ['Solicitation', 'Combined Synopsis/Solicitation']
            
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
            'rss': 'https://www.govspend.com/opportunities.rss',
            'enabled': True
        },
        'InstantMarket': {
            'url': 'https://www.instantmarket.com',
            'rss': 'https://www.instantmarket.com/rss/opportunities.xml',
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
        
        # Try InstantMarket RSS
        try:
            im_result = self._mine_instantmarket()
            results['sources_checked'] += 1
            results['total_found'] += im_result['found']
            results['imported'] += im_result['imported']
        except Exception as e:
            results['errors'].append(f"InstantMarket: {str(e)}")
        
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
    
    def _mine_instantmarket(self) -> Dict:
        """Mine InstantMarket RSS feed"""
        print("   🔍 Mining InstantMarket...")
        
        try:
            import feedparser
            
            # InstantMarket RSS
            feed_url = 'https://www.instantmarket.com/rss/opportunities.xml'
            
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
                        'source': 'InstantMarket'
                    }
                    
                    qualification = self._qualify_state_local(opp_data)
                    
                    if qualification['score'] >= 60:
                        self._import_state_local(opp_data, qualification)
                        imported += 1
                    
                    found += 1
                    
                except:
                    continue
            
            print(f"      ✓ InstantMarket: {found} found, {imported} imported")
            return {'found': found, 'imported': imported}
            
        except Exception as e:
            print(f"      ❌ InstantMarket error: {e}")
            return {'found': 0, 'imported': 0}
    
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
            invoice_data = {
                'CLIENT_NAME': client_name,
                'INVOICE_AMOUNT': invoice_amount,
                'INVOICE_DATE': datetime.now().strftime('%Y-%m-%d'),
                'DUE_DATE': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
                'STATUS': 'Sent',
                'DESCRIPTION': f'{contract_name} - Delivery {delivery_id}\n{quantity} units of {product}',
                'CATEGORY': 'Product Sales',
                'NOTES': f'Fulfillment delivery - Contract {fields.get("CONTRACT_ID", "")}'
            }
            
            self.airtable.create_record('VERTEX INVOICES', invoice_data)
            
            # Create expense for COGS in VERTEX
            expense_amount = quantity * unit_cost
            expense_data = {
                'EXPENSE_NAME': f'COGS - {product}',
                'AMOUNT': expense_amount,
                'DATE': datetime.now().strftime('%Y-%m-%d'),
                'CATEGORY': 'Cost of Goods Sold',
                'DESCRIPTION': f'Inventory cost for {quantity} units delivered to {client_name}',
                'STATUS': 'Paid',
                'NOTES': f'Delivery {delivery_id} - Contract {fields.get("CONTRACT_ID", "")}'
            }
            
            self.airtable.create_record('VERTEX EXPENSES', expense_data)
            
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
