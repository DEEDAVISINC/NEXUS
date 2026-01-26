"""
Capability Statement Generator Module
Automated generation of professional capability statements for NEXUS
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional
from pyairtable import Api
from generate_html_with_highlights import generate_html
from generate_enhanced_pdf import generate_enhanced_pdf


class CapabilityStatementGenerator:
    """Generate capability statements and manage them in Airtable"""
    
    def __init__(self, airtable_api_key: str, base_id: str):
        self.api = Api(airtable_api_key)
        self.base_id = base_id
        self.output_dir = Path('generated_capability_statements')
        self.output_dir.mkdir(exist_ok=True)
        
    def get_company_info(self) -> Dict:
        """Get company information from Airtable CompanyInfo table"""
        try:
            table = self.api.table(self.base_id, 'CompanyInfo')
            records = table.all()
            
            if not records:
                return self._get_default_company_info()
            
            # Get the first record (should only be one)
            record = records[0]['fields']
            
            return {
                'name': record.get('CompanyName', 'DEE DAVIS INC'),
                'cage_code': record.get('CAGECode', '8UMX3'),
                'uei': record.get('UEI', 'HJB4KNYJVGZ1'),
                'duns': record.get('DUNSNumber', '002636755'),
                'tax_id': record.get('TaxID', '84-4114181'),
                'sam_status': record.get('SAMStatus', 'Active'),
                'founded': record.get('YearFounded', '2018'),
                'address': record.get('Address', '755 W Big Beaver Rd, Suite 2020'),
                'city': record.get('City', 'Troy'),
                'state': record.get('State', 'MI'),
                'zip': record.get('ZipCode', '48084'),
                'phone': record.get('Phone', '248-376-4550'),
                'email': record.get('Email', 'info@deedavis.biz'),
                'website': record.get('Website', 'www.deedavis.biz'),
                'president': record.get('President', 'Dee Davis')
            }
        except Exception as e:
            print(f"Warning: Could not fetch company info from Airtable: {e}")
            return self._get_default_company_info()
    
    def _get_default_company_info(self) -> Dict:
        """Get default company information"""
        return {
            'name': 'DEE DAVIS INC',
            'cage_code': '8UMX3',
            'uei': 'HJB4KNYJVGZ1',
            'duns': '002636755',
            'tax_id': '84-4114181',
            'sam_status': 'Active',
            'founded': '2018',
            'address': '755 W Big Beaver Rd, Suite 2020',
            'city': 'Troy',
            'state': 'MI',
            'zip': '48084',
            'phone': '248-376-4550',
            'email': 'info@deedavis.biz',
            'website': 'www.deedavis.biz',
            'president': 'Dee Davis'
        }
    
    def generate_from_opportunity(
        self,
        opportunity_id: str,
        template: str = 'default',
        custom_highlights: Optional[Dict] = None
    ) -> Dict:
        """
        Generate capability statement from an Opportunities record
        
        Args:
            opportunity_id: Airtable record ID
            template: Template to use (default, va_medical, construction)
            custom_highlights: Optional custom highlights to override defaults
        
        Returns:
            Dict with generated file paths and metadata
        """
        # Get opportunity details
        table = self.api.table(self.base_id, 'Opportunities')
        opportunity = table.get(opportunity_id)
        fields = opportunity['fields']
        
        # Build config
        config = self._build_config(fields, template, custom_highlights)
        
        # Generate files
        client_name = fields.get('ClientName', 'Client')
        rfq_number = fields.get('OpportunityNumber', 'RFQ')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        base_filename = f"capstat_{client_name.replace(' ', '_')}_{rfq_number}_{timestamp}"
        html_file = self.output_dir / f"{base_filename}.html"
        pdf_file = self.output_dir / f"{base_filename}.pdf"
        
        # Generate HTML
        generate_html(config, str(html_file))
        
        # Generate PDF
        generate_enhanced_pdf(config, str(pdf_file))
        
        # Save to Airtable
        capstat_record = self._save_to_airtable(
            opportunity_id=opportunity_id,
            client_name=client_name,
            rfq_number=rfq_number,
            html_path=str(html_file),
            pdf_path=str(pdf_file),
            config=config
        )
        
        return {
            'success': True,
            'html_file': str(html_file),
            'pdf_file': str(pdf_file),
            'airtable_record_id': capstat_record['id'],
            'client_name': client_name,
            'rfq_number': rfq_number
        }
    
    def generate_custom(
        self,
        client_name: str,
        rfq_number: str,
        rfq_title: str,
        template: str = 'default',
        custom_config: Optional[Dict] = None
    ) -> Dict:
        """
        Generate capability statement with custom parameters
        
        Args:
            client_name: Name of client/agency
            rfq_number: RFQ/solicitation number
            rfq_title: Title/description of opportunity
            template: Template to use
            custom_config: Optional full custom config
        
        Returns:
            Dict with generated file paths
        """
        if custom_config:
            config = custom_config
        else:
            config = self._build_config({
                'ClientName': client_name,
                'OpportunityNumber': rfq_number,
                'Title': rfq_title
            }, template)
        
        # Generate files
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        base_filename = f"capstat_{client_name.replace(' ', '_')}_{rfq_number}_{timestamp}"
        html_file = self.output_dir / f"{base_filename}.html"
        pdf_file = self.output_dir / f"{base_filename}.pdf"
        
        # Generate HTML
        generate_html(config, str(html_file))
        
        # Generate PDF
        generate_enhanced_pdf(config, str(pdf_file))
        
        return {
            'success': True,
            'html_file': str(html_file),
            'pdf_file': str(pdf_file),
            'client_name': client_name,
            'rfq_number': rfq_number
        }
    
    def _build_config(
        self,
        opportunity_fields: Dict,
        template: str,
        custom_highlights: Optional[Dict] = None
    ) -> Dict:
        """Build config from opportunity and template"""
        
        company = self.get_company_info()
        
        # Base config
        config = {
            'company': company,
            'opportunity': {
                'client_name': opportunity_fields.get('ClientName', 'Client'),
                'rfq_number': opportunity_fields.get('OpportunityNumber', 'RFQ'),
                'date': datetime.now().strftime('%B %Y'),
                'title': opportunity_fields.get('Title', 'Government Contract')
            }
        }
        
        # Apply template
        if template == 'va_medical':
            config.update(self._get_va_medical_template())
        elif template == 'construction':
            config.update(self._get_construction_template())
        else:
            config.update(self._get_default_template())
        
        # Override highlights if provided
        if custom_highlights:
            config['highlights'] = custom_highlights
        
        return config
    
    def _get_default_template(self) -> Dict:
        """Get default template (industrial supplies)"""
        return {
            'colors': {
                'primary': '#0f172a',
                'secondary': '#1e293b',
                'accent': '#d97706',
                'text': '#334155',
                'light': '#f1f5f9'
            },
            'highlights': {
                'title': 'QUICK FACTS',
                'items': [
                    {'icon': '🎯', 'label': 'EDWOSB Certified', 'value': 'SBA Verified 2024'},
                    {'icon': '📦', 'label': 'Contract Range', 'value': '$50K - $500K+'},
                    {'icon': '✓', 'label': 'On-Time Delivery', 'value': '98%+ Performance'},
                    {'icon': '🤝', 'label': 'Strategic Partners', 'value': 'Grainger, Fastenal+'}
                ]
            },
            'overview': 'DEE DAVIS INC is a certified EDWOSB specializing in government contracting and industrial supply distribution. Since 2018, we have successfully delivered quality products to federal, state, and local government agencies nationwide.',
            'core_competencies': [
                {
                    'title': 'Industrial Supplies & Distribution',
                    'description': 'Industrial wipers, rags, cleaning supplies, PPE, janitorial supplies, office supplies'
                },
                {
                    'title': 'Government Contracting',
                    'description': 'Federal, state, local government procurement | Municipal utility contracts | Multi-year term contracts'
                },
                {
                    'title': 'Supply Chain Management',
                    'description': 'Strategic partnerships with national distributors | Just-in-time delivery | Quality assurance'
                }
            ],
            'benefits': [
                {'icon': '✓', 'title': 'EDWOSB/WOSB Certified', 'description': 'Meets socioeconomic contracting goals'},
                {'icon': '✓', 'title': 'Competitive Pricing', 'description': 'Strategic partnerships ensure best pricing'},
                {'icon': '✓', 'title': 'Reliable Delivery', 'description': 'Nationwide distribution, consistent performance'},
                {'icon': '✓', 'title': 'Proven Performance', 'description': '98%+ on-time delivery | 100% specification compliance'}
            ],
            'certifications': [
                'EDWOSB (Economically Disadvantaged Women-Owned Small Business) - SBA Certified',
                'WOSB (Women-Owned Small Business) - SBA Certified',
                'MBE (Minority Business Enterprise)',
                'WBE (Women Business Enterprise)'
            ],
            'contract_capabilities': {
                'payment_terms': 'Net 30',
                'delivery_time': '10-15 business days',
                'coverage': 'Nationwide',
                'insurance': '$1M+ General Liability'
            },
            'commitment': 'DEE DAVIS INC is committed to providing quality products, competitive pricing through strategic supplier partnerships, reliable on-time delivery, and professional service throughout the contract period.'
        }
    
    def _get_va_medical_template(self) -> Dict:
        """Get VA Medical template"""
        template = self._get_default_template()
        template['colors']['accent'] = '#0066cc'
        template['highlights']['items'] = [
            {'icon': '🏥', 'label': 'Healthcare Focus', 'value': 'VA Certified'},
            {'icon': '✓', 'label': 'Medical Supplies', 'value': '500+ Products'},
            {'icon': '🎯', 'label': 'EDWOSB', 'value': 'Set-Aside Ready'},
            {'icon': '📦', 'label': 'Fast Delivery', 'value': '3-5 Business Days'}
        ]
        template['overview'] = 'DEE DAVIS INC is a certified EDWOSB specializing in medical and healthcare supplies for VA facilities and government healthcare agencies. Since 2018, we have provided critical medical products with reliable delivery and competitive pricing.'
        return template
    
    def _get_construction_template(self) -> Dict:
        """Get construction template"""
        template = self._get_default_template()
        template['colors']['accent'] = '#f97316'
        template['highlights']['items'] = [
            {'icon': '🏗️', 'label': 'Construction Ready', 'value': '$2M Bonding'},
            {'icon': '✓', 'label': 'Licensed', 'value': 'Multi-State'},
            {'icon': '🎯', 'label': 'EDWOSB', 'value': 'DBE Certified'},
            {'icon': '📦', 'label': 'Project Range', 'value': '$50K - $2M'}
        ]
        template['overview'] = 'DEE DAVIS INC is a certified EDWOSB construction contractor specializing in government facility projects. With proven experience in federal, state, and local construction contracts, we deliver quality work on time and within budget.'
        return template
    
    def _save_to_airtable(
        self,
        opportunity_id: str,
        client_name: str,
        rfq_number: str,
        html_path: str,
        pdf_path: str,
        config: Dict
    ) -> Dict:
        """Save capability statement record to Airtable"""
        try:
            table = self.api.table(self.base_id, 'CapabilityStatements')
            
            record = table.create({
                'OpportunityID': [opportunity_id],
                'ClientName': client_name,
                'RFQNumber': rfq_number,
                'GeneratedDate': datetime.now().isoformat(),
                'HTMLPath': html_path,
                'PDFPath': pdf_path,
                'ConfigJSON': json.dumps(config, indent=2),
                'Status': 'Generated'
            })
            
            return record
        except Exception as e:
            print(f"Warning: Could not save to Airtable: {e}")
            return {'id': 'local_only'}


def handle_generate_capability_statement(
    opportunity_id: Optional[str] = None,
    client_name: Optional[str] = None,
    rfq_number: Optional[str] = None,
    rfq_title: Optional[str] = None,
    template: str = 'default',
    custom_config: Optional[Dict] = None
) -> Dict:
    """
    Handler for generating capability statements
    Can be called from API or directly
    """
    airtable_key = os.environ.get('AIRTABLE_API_KEY', '')
    base_id = os.environ.get('AIRTABLE_BASE_ID', '')
    
    generator = CapabilityStatementGenerator(airtable_key, base_id)
    
    if opportunity_id:
        # Generate from opportunity
        return generator.generate_from_opportunity(opportunity_id, template)
    elif client_name and rfq_number:
        # Generate custom
        return generator.generate_custom(
            client_name=client_name,
            rfq_number=rfq_number,
            rfq_title=rfq_title or 'Government Contract',
            template=template,
            custom_config=custom_config
        )
    else:
        return {
            'success': False,
            'error': 'Must provide either opportunity_id or (client_name + rfq_number)'
        }
