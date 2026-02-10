#!/usr/bin/env python3
"""
Add Rockdale County contact to GPSS CONTACTS
For future capability statement outreach
"""

import os
from pyairtable import Api
from dotenv import load_dotenv

# Load environment
load_dotenv()

AIRTABLE_API_KEY = os.getenv('AIRTABLE_API_KEY') or os.getenv('AIRTABLE_PERSONAL_ACCESS_TOKEN')
BASE_ID = os.getenv('AIRTABLE_BASE_ID')

# Initialize Airtable
api = Api(AIRTABLE_API_KEY)
contacts_table = api.table(BASE_ID, 'GPSS CONTACTS')

# Rockdale County contact
# Available fields: Name, Email, Title, Organization, Role Category, Notes
contact = {
    'Name': 'Adrienne Brown',
    'Organization': 'Rockdale County, Georgia',
    'Email': 'adrienne.m.brown@rockdalecountyga.gov',
    'Title': 'Procurement Specialist',
    'Role Category': 'Procurement',
    'Notes': '''Contact: 770-278-7557

Contacted regarding Indirect Cost Allocation Plan services (Feb 4, 2026). Not pursued due to specialized accounting requirement outside our core services.

GOOD NETWORKING CONTACT for future opportunities in:
- Transportation services (NEMT, logistics)
- Drug testing & fingerprinting programs
- Project management services (ATLAS PM)
- Emergency services & disaster response
- Staffing services
- Value-added supply contracts
- EDWOSB set-aside opportunities

Action: Send capability statement highlighting our actual service capabilities.

Source: Email solicitation notification
Location: Georgia
Type: County Government'''
}

print("Adding Rockdale County contact to GPSS CONTACTS...")
print(f"Name: {contact['Name']}")
print(f"Organization: {contact['Organization']}")
print(f"Email: {contact['Email']}")
print()

try:
    # Create contact record
    record = contacts_table.create(contact)
    
    print("✅ Contact added successfully!")
    print(f"Record ID: {record['id']}")
    print()
    print("📧 Future Action: Send capability statement highlighting:")
    print("   - Transportation services (NEMT, logistics)")
    print("   - Drug testing & fingerprinting")
    print("   - Project management (ATLAS PM)")
    print("   - Emergency services & disaster response")
    print("   - Staffing services")
    print("   - EDWOSB certification advantages")
    print()
    print("💡 She may have opportunities better suited to your capabilities!")
    
except Exception as e:
    print(f"❌ Error adding contact: {e}")
    print()
    print("Contact info for manual entry:")
    print(f"Name: Adrienne Brown")
    print(f"Organization: Rockdale County, Georgia")
    print(f"Email: adrienne.m.brown@rockdalecountyga.gov")
    print(f"Phone: 770-278-7557")
