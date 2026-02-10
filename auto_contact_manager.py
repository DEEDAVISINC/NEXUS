#!/usr/bin/env python3
"""
AUTOMATIC CONTACT MANAGER FOR NEXUS
Automatically extracts and adds contacts from:
1. Solicitations (buyer contacts)
2. Supplier RFQs (supplier contacts)
3. Subcontractor identification (sub contacts)
"""

import os
import re
from pyairtable import Api
from dotenv import load_dotenv
from typing import Dict, List

load_dotenv()

class AutoContactManager:
    """Automatically extract and manage contacts across NEXUS"""
    
    def __init__(self):
        self.api = Api(os.getenv('AIRTABLE_API_KEY'))
        self.base_id = os.getenv('AIRTABLE_BASE_ID')
        self.contacts_table = self.api.table(self.base_id, 'GPSS CONTACTS')
    
    def extract_and_add_from_solicitation(self, solicitation_text: str, solicitation_name: str) -> Dict:
        """
        Extract buyer/procurement contacts from solicitation and add to system
        
        Returns: {
            'contacts_found': int,
            'contacts_added': int,
            'contacts': [list of contact dicts]
        }
        """
        
        contacts_found = []
        
        # Extract email addresses
        emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', solicitation_text)
        
        # Extract phone numbers
        phones = re.findall(r'(\d{3}[-.\s]?\d{3}[-.\s]?\d{4}|\(\d{3}\)\s*\d{3}[-.\s]?\d{4})', solicitation_text)
        
        # Extract names with titles
        name_patterns = [
            r'(?:Contracting Officer|Contract Specialist|Buyer|Procurement Officer|POC|Point of Contact)[:\s]+([A-Z][a-z]+(?:\s+[A-Z]\.?)?\s+[A-Z][a-z]+)',
            r'(?:Contact|Name)[:\s]+([A-Z][a-z]+(?:\s+[A-Z]\.?)?\s+[A-Z][a-z]+)',
        ]
        
        names = []
        for pattern in name_patterns:
            matches = re.findall(pattern, solicitation_text, re.IGNORECASE)
            names.extend(matches)
        
        # Extract organization/agency
        org_patterns = [
            r'Issuing Organization[:\s]+([^\n]+)',
            r'Agency[:\s]+([^\n]+)',
            r'Department[:\s]+([^\n]+)',
        ]
        
        organization = None
        for pattern in org_patterns:
            match = re.search(pattern, solicitation_text, re.IGNORECASE)
            if match:
                organization = match.group(1).strip()
                break
        
        # Build contact records
        if names and emails:
            # Match names to emails (simple pairing)
            for i, name in enumerate(names[:len(emails)]):
                contact = {
                    'Name': name.strip(),
                    'Email': emails[i] if i < len(emails) else '',
                    'Organization': organization or solicitation_name,
                    'Title': self._extract_title_from_context(name, solicitation_text),
                    'Role Category': 'Procurement',
                    'Notes': f'''Extracted from: {solicitation_name}
Date: {os.environ.get('CURRENT_DATE', 'Today')}
Phone: {phones[i] if i < len(phones) else 'Not found'}

Contact for future capability statement outreach.
Solicitation: {solicitation_name}'''
                }
                contacts_found.append(contact)
        
        elif emails:
            # Just emails, no names
            for i, email in enumerate(emails):
                contact = {
                    'Name': email.split('@')[0].replace('.', ' ').title(),
                    'Email': email,
                    'Organization': organization or solicitation_name,
                    'Title': 'Procurement Contact',
                    'Role Category': 'Procurement',
                    'Notes': f'''Extracted from: {solicitation_name}
Date: {os.environ.get('CURRENT_DATE', 'Today')}
Phone: {phones[i] if i < len(phones) else 'Not found'}'''
                }
                contacts_found.append(contact)
        
        # Add contacts to Airtable
        added_count = 0
        for contact in contacts_found:
            try:
                # Check if exists
                existing = self.contacts_table.all(formula=f"{{Email}}='{contact['Email']}'")
                if not existing:
                    self.contacts_table.create(contact)
                    added_count += 1
            except Exception as e:
                print(f"Error adding contact {contact.get('Name')}: {e}")
        
        return {
            'contacts_found': len(contacts_found),
            'contacts_added': added_count,
            'contacts': contacts_found
        }
    
    def add_supplier_contact(self, supplier_name: str, supplier_email: str = None, 
                            supplier_phone: str = None, product_type: str = None,
                            context: str = None) -> Dict:
        """
        Add supplier contact when RFQ is sent or quote is requested
        
        Args:
            supplier_name: Company name
            supplier_email: Email address
            supplier_phone: Phone number
            product_type: What they supply
            context: How you know them / what quote was for
        """
        
        contact = {
            'Name': supplier_name,
            'Organization': supplier_name,
            'Role Category': 'Supplier',
            'Notes': f'''Supplier Contact
Product/Services: {product_type or 'Various'}
{context or 'Added to system'}
Phone: {supplier_phone or 'To be obtained'}'''
        }
        
        if supplier_email:
            contact['Email'] = supplier_email
        
        try:
            # Check if exists
            if supplier_email:
                existing = self.contacts_table.all(formula=f"{{Email}}='{supplier_email}'")
            else:
                existing = self.contacts_table.all(formula=f"{{Name}}='{supplier_name}'")
            
            if not existing:
                record = self.contacts_table.create(contact)
                return {
                    'success': True,
                    'message': f'Supplier contact added: {supplier_name}',
                    'record_id': record['id']
                }
            else:
                return {
                    'success': False,
                    'message': f'Contact already exists: {supplier_name}',
                    'record_id': existing[0]['id']
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def add_subcontractor_contact(self, sub_name: str, sub_email: str = None,
                                 sub_phone: str = None, services: str = None,
                                 context: str = None) -> Dict:
        """
        Add subcontractor contact when identified for opportunity
        
        Args:
            sub_name: Company/person name
            sub_email: Email address
            sub_phone: Phone number
            services: Services they provide
            context: How identified / what opportunity
        """
        
        contact = {
            'Name': sub_name,
            'Organization': sub_name,
            'Role Category': 'Subcontractor',
            'Notes': f'''Subcontractor Contact
Services: {services or 'Various'}
{context or 'Identified for future opportunities'}
Phone: {sub_phone or 'To be obtained'}'''
        }
        
        if sub_email:
            contact['Email'] = sub_email
        
        try:
            # Check if exists
            if sub_email:
                existing = self.contacts_table.all(formula=f"{{Email}}='{sub_email}'")
            else:
                existing = self.contacts_table.all(formula=f"{{Name}}='{sub_name}'")
            
            if not existing:
                record = self.contacts_table.create(contact)
                return {
                    'success': True,
                    'message': f'Subcontractor contact added: {sub_name}',
                    'record_id': record['id']
                }
            else:
                return {
                    'success': False,
                    'message': f'Contact already exists: {sub_name}',
                    'record_id': existing[0]['id']
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _extract_title_from_context(self, name: str, text: str) -> str:
        """Extract job title from context around name"""
        # Look for common titles near the name
        context_start = max(0, text.find(name) - 100)
        context_end = min(len(text), text.find(name) + 100)
        context = text[context_start:context_end]
        
        titles = [
            'Contracting Officer', 'Contract Specialist', 'Procurement Officer',
            'Buyer', 'Purchasing Agent', 'Procurement Specialist',
            'Director', 'Manager', 'Coordinator', 'Administrator'
        ]
        
        for title in titles:
            if title.lower() in context.lower():
                return title
        
        return 'Procurement Contact'


# Flask endpoints to add to api_server.py

def api_add_supplier_contact():
    """API endpoint to add supplier contact"""
    from flask import request, jsonify
    
    data = request.json
    manager = AutoContactManager()
    
    result = manager.add_supplier_contact(
        supplier_name=data.get('name'),
        supplier_email=data.get('email'),
        supplier_phone=data.get('phone'),
        product_type=data.get('product_type'),
        context=data.get('context')
    )
    
    return jsonify(result)


def api_add_subcontractor_contact():
    """API endpoint to add subcontractor contact"""
    from flask import request, jsonify
    
    data = request.json
    manager = AutoContactManager()
    
    result = manager.add_subcontractor_contact(
        sub_name=data.get('name'),
        sub_email=data.get('email'),
        sub_phone=data.get('phone'),
        services=data.get('services'),
        context=data.get('context')
    )
    
    return jsonify(result)


def api_extract_contacts_from_solicitation():
    """API endpoint to auto-extract contacts from solicitation"""
    from flask import request, jsonify
    
    data = request.json
    manager = AutoContactManager()
    
    result = manager.extract_and_add_from_solicitation(
        solicitation_text=data.get('text'),
        solicitation_name=data.get('name')
    )
    
    return jsonify(result)


if __name__ == '__main__':
    # Test the contact manager
    print("="*60)
    print("NEXUS AUTO CONTACT MANAGER - TEST")
    print("="*60)
    
    manager = AutoContactManager()
    
    # Test adding a supplier
    result = manager.add_supplier_contact(
        supplier_name="Test Supplier Inc",
        supplier_email="test@supplier.com",
        supplier_phone="555-123-4567",
        product_type="Industrial supplies",
        context="Test contact for system validation"
    )
    
    print(f"\nTest Result: {result}")
    print("\n✅ Auto Contact Manager is ready!")
    print("="*60)
