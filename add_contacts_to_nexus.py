#!/usr/bin/env python3
"""
ADD CONTACTS TO NEXUS
Imports contacts from markdown files to NEXUS CONTACTS Airtable table
Handles: Procurement Officers, Suppliers, Subcontractors, Partners

Part of NEXUS Backend - Dee Davis Inc
"""

import os
import re
from datetime import datetime
from typing import Dict, List, Optional
from dotenv import load_dotenv
from pyairtable import Api

# Load environment variables
load_dotenv()

AIRTABLE_API_KEY = os.getenv('AIRTABLE_API_KEY')
AIRTABLE_BASE_ID = os.getenv('AIRTABLE_BASE_ID')
CONTACTS_TABLE = 'NEXUS CONTACTS'

# Initialize Airtable
api = Api(AIRTABLE_API_KEY)
table = api.table(AIRTABLE_BASE_ID, CONTACTS_TABLE)


class ContactImporter:
    """Import contacts from various sources to NEXUS CONTACTS"""
    
    def __init__(self):
        self.api = Api(AIRTABLE_API_KEY)
        self.table = self.api.table(AIRTABLE_BASE_ID, CONTACTS_TABLE)
        self.added_count = 0
        self.updated_count = 0
        self.skipped_count = 0
    
    def check_duplicate(self, email: str) -> Optional[Dict]:
        """Check if contact already exists by email"""
        if not email:
            return None
        
        try:
            formula = f"{{EMAIL}} = '{email}'"
            existing = self.table.all(formula=formula, max_records=1)
            return existing[0] if existing else None
        except Exception as e:
            print(f"Error checking duplicate: {e}")
            return None
    
    def add_contact(
        self,
        name: str,
        email: str,
        contact_type: str,
        organization: str = None,
        title: str = None,
        phone: str = None,
        alt_email: str = None,
        fax: str = None,
        department: str = None,
        location: str = None,
        address: str = None,
        website: str = None,
        org_type: str = None,
        agency_level: str = None,
        tags: List[str] = None,
        notes: str = None,
        priority: str = "Medium",
        source: str = "RFP/RFQ",
        relationship_stage: str = "New"
    ) -> Optional[str]:
        """
        Add or update contact in NEXUS CONTACTS
        
        Returns: record_id if successful, None if failed
        """
        
        if not email:
            print(f"⚠️ Skipping {name}: No email provided")
            self.skipped_count += 1
            return None
        
        # Check for duplicate
        existing = self.check_duplicate(email)
        
        # Prepare fields
        fields = {
            'CONTACT NAME': name,
            'EMAIL': email,
            'CONTACT TYPE': contact_type,
            'RELATIONSHIP STAGE': relationship_stage,
            'SOURCE': source,
            'PRIORITY': priority,
            'ADDED BY': 'NEXUS AI'
        }
        
        # Add optional fields
        if organization:
            fields['ORGANIZATION'] = organization
        if title:
            fields['TITLE'] = title
        if phone:
            fields['PHONE'] = phone
        if alt_email:
            fields['ALT EMAIL'] = alt_email
        if fax:
            fields['FAX'] = fax
        if department:
            fields['DEPARTMENT'] = department
        if location:
            fields['LOCATION'] = location
        if address:
            fields['ADDRESS'] = address
        if website:
            fields['WEBSITE'] = website
        if org_type:
            fields['ORG TYPE'] = org_type
        if agency_level:
            fields['AGENCY LEVEL'] = agency_level
        if tags:
            fields['TAGS'] = tags
        if notes:
            fields['NOTES'] = notes
        
        try:
            if existing:
                # Update existing contact
                record_id = existing['id']
                # Only update if new info is provided
                update_fields = {}
                for key, value in fields.items():
                    if value and key not in ['ADDED BY', 'FIRST CONTACT DATE']:
                        update_fields[key] = value
                
                if update_fields:
                    self.table.update(record_id, update_fields)
                    print(f"✅ UPDATED: {name} ({organization or 'N/A'})")
                    self.updated_count += 1
                else:
                    print(f"⏩ SKIPPED: {name} (no new info)")
                    self.skipped_count += 1
                
                return record_id
            else:
                # Add FIRST CONTACT DATE for new contacts
                fields['FIRST CONTACT DATE'] = datetime.now().strftime('%Y-%m-%d')
                
                # Create new contact
                record = self.table.create(fields)
                print(f"✅ ADDED: {name} ({organization or 'N/A'}) - {contact_type}")
                self.added_count += 1
                return record['id']
                
        except Exception as e:
            print(f"❌ ERROR adding {name}: {e}")
            return None
    
    def import_procurement_officers(self, filepath: str = "PROCUREMENT_OFFICERS_LIST.md"):
        """Import procurement officers from markdown file"""
        
        print("\n" + "="*80)
        print("📋 IMPORTING PROCUREMENT OFFICERS")
        print("="*80 + "\n")
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse officers from markdown
            officers = []
            
            # Mark Rozinsky - Dearborn
            if "Mark Rozinsky" in content:
                officers.append({
                    'name': 'Mark Rozinsky',
                    'email': 'mrozinsky@dearborn.gov',
                    'phone': '(313) 943-2375',
                    'title': 'Purchasing Manager',
                    'organization': 'City of Dearborn',
                    'department': 'Purchasing Division',
                    'org_type': 'Government',
                    'agency_level': 'City',
                    'location': 'Dearborn, Michigan',
                    'tags': ['City Gov', 'Local', 'Emergency Equipment'],
                    'priority': 'High',
                    'notes': 'Contact for emergency generator vendor list. ITB #161219 - Phase 2 opportunity estimated $120K-$180K. Email Jan 27 to get on vendor list.'
                })
            
            # Tina Kern - CPS Energy
            if "Tina Marie Kern" in content or "Tina Kern" in content:
                officers.append({
                    'name': 'Tina Marie Kern',
                    'email': 'tkern@cpsenergy.com',
                    'alt_email': 'BidSubmittal@cpsenergy.com',
                    'phone': '210-935-5988',
                    'fax': '210-353-3056',
                    'title': 'Buyer',
                    'organization': 'CPS Energy',
                    'org_type': 'Government',
                    'agency_level': 'City',
                    'location': 'San Antonio, TX',
                    'address': 'PO Box 2906, San Antonio, TX 78299-2906',
                    'website': 'https://cpsenergy.com',
                    'tags': ['City Gov', 'Out of State', 'Office Supplies'],
                    'priority': 'High',
                    'notes': 'RFQ 7000205103 - Industrial Wipers (3-year contract). Bid due Jan 31, 2026. Our bid: $504,141. Buyer #108.'
                })
            
            # Joan Daniels - Oakland County
            if "Joan E. Daniels" in content or "Joan Daniels" in content:
                officers.append({
                    'name': 'Joan E. Daniels',
                    'email': 'danielsj@oakgov.com',
                    'phone': '248-326-8391',
                    'organization': 'Oakland County',
                    'department': 'Medical Examiner\'s Office',
                    'org_type': 'Government',
                    'agency_level': 'County',
                    'location': 'Pontiac, MI',
                    'tags': ['County Gov', 'Local', 'Medical Supplies'],
                    'priority': 'High',
                    'notes': 'RFQ Oak-0000001089 - Medical Examiner Body Bags. Due Jan 29, 2026. Local preference (15 min from Troy). Diversity weighting in evaluation.'
                })
            
            # Madison Heights
            if "Madison Heights" in content:
                officers.append({
                    'name': 'City Clerk',
                    'email': 'clerk@madisonheights.org',
                    'organization': 'City of Madison Heights',
                    'department': 'City Clerk',
                    'org_type': 'Government',
                    'agency_level': 'City',
                    'location': 'Madison Heights, MI',
                    'address': '300 W 13 Mile Rd, Madison Heights, MI 48071',
                    'tags': ['City Gov', 'Local', 'Professional Services'],
                    'priority': 'Medium',
                    'notes': 'MH 26-03 - Senior Citizen Yard and Lawn Services. Due Jan 28, 2026. CDBG/OLHSA funded. EDWOSB/WOSB advantage. Hand delivery required. Notary required.'
                })
            
            # Warren DDA
            if "Warren" in content and "DDA" in content:
                officers.append({
                    'name': 'Purchasing Department',
                    'email': 'purchasing@warrenmich.gov',
                    'organization': 'City of Warren - DDA',
                    'department': 'Purchasing Department',
                    'org_type': 'Government',
                    'agency_level': 'City',
                    'location': 'Warren, MI',
                    'tags': ['City Gov', 'Local', 'Landscape'],
                    'priority': 'Medium',
                    'notes': 'ITB-W-1699 - Commercial Landscape Maintenance (7 DDA locations). Due Jan 27, 2026. Requires 10+ years municipal experience. Via BidNet (MITN).'
                })
            
            # Jackson County
            if "Jackson County" in content:
                officers.append({
                    'name': 'Purchasing Contact',
                    'email': 'jcouling@mijackson.org',
                    'organization': 'Jackson County',
                    'department': 'Department of Transportation',
                    'org_type': 'Government',
                    'agency_level': 'County',
                    'location': 'Jackson, MI',
                    'tags': ['County Gov', 'Local', 'Construction'],
                    'priority': 'High',
                    'notes': 'RFB #188 - 2026 Sodium Chloride (Road Salt). 21,000 tons. Value: $1.8M+ (LARGEST OPPORTUNITY!). Due Feb 2, 2026. Questions due Jan 26. EMAIL ONLY (DO NOT use BidNet).'
                })
            
            # Add all officers
            for officer in officers:
                self.add_contact(
                    name=officer['name'],
                    email=officer['email'],
                    contact_type='Procurement Officer',
                    organization=officer.get('organization'),
                    title=officer.get('title'),
                    phone=officer.get('phone'),
                    alt_email=officer.get('alt_email'),
                    fax=officer.get('fax'),
                    department=officer.get('department'),
                    location=officer.get('location'),
                    address=officer.get('address'),
                    website=officer.get('website'),
                    org_type=officer.get('org_type'),
                    agency_level=officer.get('agency_level'),
                    tags=officer.get('tags'),
                    notes=officer.get('notes'),
                    priority=officer.get('priority', 'Medium'),
                    source='RFP/RFQ',
                    relationship_stage='Contacted'
                )
            
        except FileNotFoundError:
            print(f"⚠️ File not found: {filepath}")
        except Exception as e:
            print(f"❌ Error importing officers: {e}")
    
    def import_suppliers(self, filepath: str = "VENDOR_CLIENT_CONTACTS.md"):
        """Import suppliers and subcontractors from markdown file"""
        
        print("\n" + "="*80)
        print("🏭 IMPORTING SUPPLIERS & SUBCONTRACTORS")
        print("="*80 + "\n")
        
        # Hardcoded supplier data (since it's structured)
        suppliers = [
            {
                'name': 'GSA Sales Team',
                'email': 'salesteam@generac.com',
                'phone': '(888) 436-3722',
                'organization': 'Generac Power Systems',
                'org_type': 'Private Company',
                'location': 'Waukesha, Wisconsin',
                'website': 'https://www.generac.com/gsa',
                'tags': ['Emergency Equipment', 'GSA Schedule', 'Large Enterprise'],
                'priority': 'High',
                'notes': 'GSA contract holder for emergency generators. Need to establish account for government pricing. GSA Schedule holder.',
                'contact_type': 'Supplier'
            },
            {
                'name': 'Government Sales',
                'email': 'governmentsales@kohler.com',
                'phone': '(920) 457-4441',
                'organization': 'Kohler Power Systems',
                'org_type': 'Private Company',
                'location': 'Kohler, Wisconsin',
                'website': 'https://www.kohlerpower.com',
                'tags': ['Emergency Equipment', 'GSA Schedule', 'Large Enterprise'],
                'priority': 'High',
                'notes': 'GSA contract holder for generators. Alternative to Generac. Premium brand.',
                'contact_type': 'Supplier'
            },
            {
                'name': 'Sales Team',
                'email': 'info@impcorp.com',
                'phone': '(800) 533-8882',
                'organization': 'IMP Corporation',
                'org_type': 'Private Company',
                'location': 'Troy, Michigan',
                'website': 'https://www.impcorp.com',
                'tags': ['Emergency Equipment', 'Local', 'Small Business'],
                'priority': 'High',
                'notes': 'Wholesale distributor of emergency equipment. LOCAL TO MICHIGAN (Troy). May offer better pricing than manufacturer direct.',
                'contact_type': 'Supplier'
            },
            {
                'name': 'Government Sales',
                'email': 'government.sales@grainger.com',
                'phone': '(800) 472-4643',
                'organization': 'Grainger',
                'org_type': 'Private Company',
                'location': 'Chicago, Illinois',
                'website': 'https://www.grainger.com',
                'tags': ['Office Supplies', 'GSA Schedule', 'Large Enterprise'],
                'priority': 'High',
                'notes': 'Primary supplier for CPS Energy industrial wipers bid. GSA contract holder. Account established.',
                'contact_type': 'Supplier'
            },
            {
                'name': 'Sales Team',
                'email': 'info@detroitsalt.com',
                'phone': '(313) 841-5800',
                'fax': '(313) 841-5989',
                'organization': 'Detroit Salt Company',
                'org_type': 'Private Company',
                'location': 'Detroit, Michigan',
                'website': 'https://www.detroitsalt.com',
                'tags': ['Construction', 'Local', 'Small Business'],
                'priority': 'High',
                'notes': 'Road salt supplier for Jackson County RFB #188 (21,000 tons). LOCAL supplier. Need quote for sodium chloride.',
                'contact_type': 'Supplier'
            },
            {
                'name': 'Sales Team',
                'email': 'sales@mopec.com',
                'phone': '(800) 362-8491',
                'organization': 'Mopec',
                'org_type': 'Private Company',
                'location': 'Oak Park, Michigan',
                'website': 'https://www.mopec.com',
                'tags': ['Medical Supplies', 'Local', 'Small Business'],
                'priority': 'High',
                'notes': 'Medical examiner supplies (cadaver bags) for Oakland County RFQ. LOCAL to Michigan. Need pricing on 6 bag items.',
                'contact_type': 'Supplier'
            },
            {
                'name': 'Owner',
                'email': 'cutkinglawncare@gmail.com',
                'phone': '(586) 555-1234',
                'organization': 'Cut King Lawn Care',
                'org_type': 'Private Company',
                'location': 'Madison Heights, Michigan',
                'tags': ['Landscape', 'Local', 'Small Business'],
                'priority': 'Medium',
                'notes': 'Subcontractor for Madison Heights Senior Lawn Services. Target rate: $40-45/cut. Awaiting quote.',
                'contact_type': 'Subcontractor'
            },
        ]
        
        # Add all suppliers
        for supplier in suppliers:
            self.add_contact(
                name=supplier['name'],
                email=supplier['email'],
                contact_type=supplier['contact_type'],
                organization=supplier['organization'],
                title=supplier.get('title'),
                phone=supplier.get('phone'),
                fax=supplier.get('fax'),
                location=supplier.get('location'),
                website=supplier.get('website'),
                org_type=supplier.get('org_type'),
                tags=supplier.get('tags'),
                notes=supplier.get('notes'),
                priority=supplier.get('priority', 'Medium'),
                source='Web Search',
                relationship_stage='New'
            )
    
    def print_summary(self):
        """Print import summary"""
        print("\n" + "="*80)
        print("📊 IMPORT SUMMARY")
        print("="*80)
        print(f"✅ Added:   {self.added_count} new contacts")
        print(f"🔄 Updated: {self.updated_count} existing contacts")
        print(f"⏩ Skipped: {self.skipped_count} contacts")
        print(f"📋 Total:   {self.added_count + self.updated_count} contacts in NEXUS")
        print("="*80 + "\n")


def main():
    """Main import function"""
    
    print("\n" + "="*80)
    print("🚀 NEXUS CONTACTS IMPORTER")
    print("="*80)
    print("Importing contacts to NEXUS CONTACTS Airtable table...")
    print("="*80 + "\n")
    
    # Check environment
    if not AIRTABLE_API_KEY or not AIRTABLE_BASE_ID:
        print("❌ ERROR: Missing Airtable credentials in .env file")
        print("Required: AIRTABLE_API_KEY, AIRTABLE_BASE_ID")
        return
    
    # Initialize importer
    importer = ContactImporter()
    
    # Import procurement officers
    importer.import_procurement_officers()
    
    # Import suppliers and subcontractors
    importer.import_suppliers()
    
    # Print summary
    importer.print_summary()
    
    print("✅ Import complete! Check your NEXUS CONTACTS table in Airtable.")
    print("\n💡 TIP: Use views to organize contacts by type:")
    print("   - 🏛️ Procurement Officers")
    print("   - 🏭 Suppliers")
    print("   - 👷 Subcontractors")
    print()


if __name__ == "__main__":
    main()
