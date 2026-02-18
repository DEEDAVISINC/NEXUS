#!/usr/bin/env python3
"""
ADD MICHIGAN EDUCATION CONTACTS TO NEXUS
Imports Michigan school district and education contacts for drug testing services outreach

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
CONTACTS_TABLE = 'GPSS CONTACTS'

# Initialize Airtable
api = Api(AIRTABLE_API_KEY)
table = api.table(AIRTABLE_BASE_ID, CONTACTS_TABLE)


class MichiganEducationImporter:
    """Import Michigan education contacts to GPSS CONTACTS"""
    
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
            formula = f"{{Email}} = '{email}'"
            existing = self.table.all(formula=formula, max_records=1)
            return existing[0] if existing else None
        except Exception as e:
            print(f"Error checking duplicate: {e}")
            return None
    
    def add_contact(
        self,
        name: str,
        email: str,
        phone: str,
        organization: str,
        contact_type: str = 'Procurement Officer',
        title: str = None,
        org_type: str = 'Government',
        agency_level: str = None,
        location: str = 'Michigan',
        tags: List[str] = None,
        notes: str = None,
        priority: str = "Medium",
        source: str = "B2B Outreach List",
        relationship_stage: str = "New"
    ) -> Optional[str]:
        """
        Add or update contact in GPSS CONTACTS
        
        Returns: record_id if successful, None if failed
        """
        
        if not email:
            print(f"⚠️ Skipping {name}: No email provided")
            self.skipped_count += 1
            return None
        
        # Check for duplicate
        existing = self.check_duplicate(email)
        
        # Prepare fields using actual Airtable field names
        fields = {
            'Name': name,
            'Email': email,
            'Organization': organization,
            'Role Category': contact_type
        }
        
        # Build notes field with all the metadata
        notes_parts = []
        if phone:
            notes_parts.append(f"Phone: {phone}")
        if location:
            notes_parts.append(f"Location: {location}")
        if agency_level:
            notes_parts.append(f"Agency Level: {agency_level}")
        if tags:
            notes_parts.append(f"Tags: {', '.join(tags)}")
        if notes:
            notes_parts.append(f"\n{notes}")
        
        if notes_parts:
            fields['Notes'] = '\n'.join(notes_parts)
        
        if title:
            fields['Title'] = title
        
        try:
            if existing:
                # Update existing contact - add organization if missing
                record_id = existing['id']
                update_fields = {}
                
                # Add organization if it's not already there
                if organization and not existing.get('fields', {}).get('Organization'):
                    update_fields['Organization'] = organization
                
                if update_fields:
                    self.table.update(record_id, update_fields)
                    print(f"✅ UPDATED: {name} ({organization})")
                    self.updated_count += 1
                else:
                    print(f"⏩ SKIPPED: {name} (already exists)")
                    self.skipped_count += 1
                
                return record_id
            else:
                # Create new contact
                record = self.table.create(fields)
                print(f"✅ ADDED: {name} - {organization}")
                self.added_count += 1
                return record['id']
                
        except Exception as e:
            print(f"❌ ERROR adding {name}: {e}")
            return None
    
    def import_michigan_education_contacts(self):
        """Import Michigan education contacts"""
        
        print("\n" + "="*80)
        print("🎓 IMPORTING MICHIGAN EDUCATION CONTACTS")
        print("="*80 + "\n")
        
        # Michigan education contacts for drug testing services
        contacts = [
            {
                'name': 'Maisha Parham',
                'email': 'maisha.parham@detroitk12.org',
                'phone': '313-873-2753',
                'organization': 'Detroit Public Schools Community District',
                'agency_level': 'School District'
            },
            {
                'name': 'Laura Gyorkos',
                'email': 'gyorkosl@michigan.gov',
                'phone': '517-388-6234',
                'organization': 'Michigan Department of Education',
                'agency_level': 'State'
            },
            {
                'name': 'Claire Kidder',
                'email': 'kidderc@gpschools.org',
                'phone': '313-432-3033',
                'organization': 'Grosse Pointe Public Schools',
                'agency_level': 'School District'
            },
            {
                'name': 'Will Lackey',
                'email': 'lackeyw@westottawa.net',
                'phone': '616-786-2077',
                'organization': 'West Ottawa Public Schools',
                'agency_level': 'School District'
            },
            {
                'name': 'Melanierose Smith',
                'email': 'melanierosesmith@kentisd.org',
                'phone': '616-365-2221',
                'organization': 'Kent Intermediate School District',
                'agency_level': 'ISD'
            },
            {
                'name': 'Kristi Zakrzewski',
                'email': 'ZakrzewskiK@michigan.gov',
                'phone': '517-243-5669',
                'organization': 'Michigan Department of Education',
                'agency_level': 'State'
            },
            {
                'name': 'Jennifer Williamsen',
                'email': 'WilliamsenJ1@michigan.gov',
                'phone': '517-335-9361',
                'organization': 'Michigan Department of Education',
                'agency_level': 'State'
            },
            {
                'name': 'Cassandra Shook',
                'email': 'shook@monroe.k12.mi.us',
                'phone': '734-265-3064',
                'organization': 'Monroe Public Schools',
                'agency_level': 'School District'
            },
            {
                'name': 'Megan Sturk',
                'email': 'msturk@geneseeisd.org',
                'phone': '810-591-6175',
                'organization': 'Genesee Intermediate School District',
                'agency_level': 'ISD'
            },
            {
                'name': 'Deanna Mayer',
                'email': 'dmayer@eup.k12.mi.us',
                'phone': '906-632-3373',
                'organization': 'Eastern Upper Peninsula ISD',
                'agency_level': 'ISD'
            },
            {
                'name': 'Kevin Doty',
                'email': 'dotyk@masonk12.net',
                'phone': '517-883-8275',
                'organization': 'Mason Public Schools',
                'agency_level': 'School District'
            },
            {
                'name': 'Lisa Lehnert',
                'email': 'LehnertL@michigan.gov',
                'phone': '517-335-4904',
                'organization': 'Michigan Department of Education',
                'agency_level': 'State'
            },
            {
                'name': 'Jesse Sutton',
                'email': 'jesse.sutton@southfieldk12.org',
                'phone': '248-746-8519',
                'organization': 'Southfield Public Schools',
                'agency_level': 'School District'
            },
            {
                'name': 'Leslie Cummings',
                'email': 'lcummings@integrityedservices.org',
                'phone': '616-600-6503',
                'organization': 'Integrity Ed Services',
                'agency_level': 'Cooperative'
            },
            {
                'name': 'Brandon Weingartz',
                'email': 'weingab@gowcs.net',
                'phone': '517-655-7562',
                'organization': 'Webberville Community Schools',
                'agency_level': 'School District'
            },
            {
                'name': 'Beverly McCoy',
                'email': 'bmccoy@tawas.net',
                'phone': '989-984-2255',
                'organization': 'Tawas Area Schools',
                'agency_level': 'School District'
            },
            {
                'name': 'Amanda Pauly',
                'email': 'PaulyA3@michigan.gov',
                'phone': '989-734-2543',
                'organization': 'Michigan Department of Education',
                'agency_level': 'State'
            },
            {
                'name': 'Elizabeth Noffsinger',
                'email': 'NoffsingerE@michigan.gov',
                'phone': '989-344-6190',
                'organization': 'Michigan Department of Education',
                'agency_level': 'State'
            },
            {
                'name': 'Krystal Kozuch',
                'email': 'kkozuch@midlandesa.org',
                'phone': '989-631-5890',
                'organization': 'Midland County ESA',
                'agency_level': 'ISD'
            },
            {
                'name': 'Jill Latham',
                'email': 'jill.latham@ppps.org',
                'phone': '269-415-5206',
                'organization': 'Portage Public Schools',
                'agency_level': 'School District'
            },
            {
                'name': 'Christine Pratt',
                'email': 'cpratt@fhps.net',
                'phone': '616-493-8804',
                'organization': 'Forest Hills Public Schools',
                'agency_level': 'School District'
            },
            {
                'name': 'Marta Moore',
                'email': 'MooreM42@michigan.gov',
                'phone': '517-241-3188',
                'organization': 'Michigan Department of Education',
                'agency_level': 'State'
            },
            {
                'name': 'Stacey Shaw',
                'email': 'shaw@macservcorp.com',
                'phone': '989-307-1307',
                'organization': 'Michigan Association for Computer Users in Learning',
                'agency_level': 'Cooperative'
            },
            {
                'name': 'Tracy Aceron',
                'email': 'tracy.aceron@lok12.org',
                'phone': '248-814-1798',
                'organization': 'Lake Orion Community Schools',
                'agency_level': 'School District'
            },
            {
                'name': 'Ruth Thole',
                'email': 'THOLER@michigan.gov',
                'phone': '517-335-4972',
                'organization': 'Michigan Department of Education',
                'agency_level': 'State'
            },
            {
                'name': 'Melissa Butler',
                'email': 'melissa.butler@jcisd.org',
                'phone': '517-990-6709',
                'organization': 'Jackson County Intermediate School District',
                'agency_level': 'ISD'
            },
            {
                'name': 'Patience Nemeth',
                'email': 'pnemeth@moisd.org',
                'phone': '231-796-3543',
                'organization': 'Muskegon Area Intermediate School District',
                'agency_level': 'ISD'
            },
            {
                'name': 'Donald Klein',
                'email': 'KleinD4@michigan.gov',
                'phone': '248-207-7950',
                'organization': 'Michigan Department of Education',
                'agency_level': 'State'
            },
            {
                'name': 'Scott Barclay',
                'email': 'barclays@michigan.gov',
                'phone': '517-636-7744',
                'organization': 'Michigan Department of Education',
                'agency_level': 'State'
            },
            {
                'name': 'Katrina Bontekoe',
                'email': 'kbontekoe@wmisd.org',
                'phone': '231-876-4821',
                'organization': 'West Michigan ISD',
                'agency_level': 'ISD'
            },
            {
                'name': 'Theodore Jaworski',
                'email': 'theodore.jaworski@oakland.k12.mi.us',
                'phone': '248-655-4441',
                'organization': 'Oakland Schools',
                'agency_level': 'ISD'
            },
            {
                'name': 'Amiee Erfourth',
                'email': 'erfourtha@benzieschools.net',
                'phone': '231-882-9653',
                'organization': 'Benzie County Central Schools',
                'agency_level': 'School District'
            },
            {
                'name': 'Angela Sutton',
                'email': 'asutton7@livoniapublicschools.org',
                'phone': '734-744-2552',
                'organization': 'Livonia Public Schools',
                'agency_level': 'School District'
            },
            {
                'name': 'Jesse Rickard',
                'email': 'jrickard@muskegonisd.org',
                'phone': '231-767-7209',
                'organization': 'Muskegon Area ISD',
                'agency_level': 'ISD'
            },
            {
                'name': 'Robin Lampert',
                'email': 'LampertR1@michigan.gov',
                'phone': '517-582-2746',
                'organization': 'Michigan Department of Education',
                'agency_level': 'State'
            },
            {
                'name': 'Victoria Paull',
                'email': 'victoria.paull@rcashurons.org',
                'phone': '989-734-9100',
                'organization': 'Huron Intermediate School District',
                'agency_level': 'ISD'
            },
            {
                'name': 'Mary Van Ostran',
                'email': 'VanOstranL@michigan.gov',
                'phone': '517-599-7680',
                'organization': 'Michigan Department of Education',
                'agency_level': 'State'
            },
            {
                'name': 'Kendra Leib',
                'email': 'kleib@marshallpublicschools.org',
                'phone': '269-781-1262',
                'organization': 'Marshall Public Schools',
                'agency_level': 'School District'
            },
            {
                'name': 'James Stottlemyer',
                'email': 'james.stottlemyer@wbsd.org',
                'phone': '248-701-4630',
                'organization': 'West Bloomfield School District',
                'agency_level': 'School District'
            },
            {
                'name': 'Jennifer Fickel',
                'email': 'jfickel@rochester.k12.mi.us',
                'phone': '248-726-3045',
                'organization': 'Rochester Community Schools',
                'agency_level': 'School District'
            },
            {
                'name': 'David Blackmar',
                'email': 'dblackmar@charterschoolpartners.com',
                'phone': '810-626-8606',
                'organization': 'Charter School Partners',
                'agency_level': 'Charter Network'
            },
            {
                'name': 'Alyssa Smith',
                'email': 'alyssa.smith@hillsdaleschools.org',
                'phone': '517-689-1404',
                'organization': 'Hillsdale Community Schools',
                'agency_level': 'School District'
            },
            {
                'name': 'Patrice Bushart',
                'email': 'pbushart@livoniapublicschools.org',
                'phone': '734-367-6553',
                'organization': 'Livonia Public Schools',
                'agency_level': 'School District'
            },
            {
                'name': 'Marc Bennett',
                'email': 'bennettm@grps.org',
                'phone': '616-819-3024',
                'organization': 'Grand Rapids Public Schools',
                'agency_level': 'School District'
            },
            {
                'name': 'Ruth Stagner',
                'email': 'stagnerr@aaps.k12.mi.us',
                'phone': '734-994-2261',
                'organization': 'Ann Arbor Public Schools',
                'agency_level': 'School District'
            },
            {
                'name': 'Dillon Boyd',
                'email': 'boyddp@kalamazoopublicschools.net',
                'phone': '269-337-0400',
                'organization': 'Kalamazoo Public Schools',
                'agency_level': 'School District'
            },
            {
                'name': 'Victoria Amore',
                'email': 'victoriaamore@wlcsd.org',
                'phone': '248-956-2042',
                'organization': 'Walled Lake Consolidated Schools',
                'agency_level': 'School District'
            },
            {
                'name': 'Simon Baldwin',
                'email': 'BaldwinS@michigan.gov',
                'phone': '517-897-7681',
                'organization': 'Michigan Department of Education',
                'agency_level': 'State'
            },
            {
                'name': 'Sarah Kandell',
                'email': 'skandell@inghamisd.org',
                'phone': '517-204-2103',
                'organization': 'Ingham Intermediate School District',
                'agency_level': 'ISD'
            },
            {
                'name': 'Kim Conroy',
                'email': 'kconroy@springlakeschools.org',
                'phone': '616-847-7919',
                'organization': 'Spring Lake Public Schools',
                'agency_level': 'School District'
            },
            {
                'name': 'Tracey French',
                'email': 'frencht@reeths-puffer.org',
                'phone': '231-719-3110',
                'organization': 'Reeths-Puffer Schools',
                'agency_level': 'School District'
            },
            {
                'name': 'Tricia Root',
                'email': 'roott@lakeviewschools.net',
                'phone': '616-225-6190',
                'organization': 'Lakeview Community Schools',
                'agency_level': 'School District'
            },
            {
                'name': 'Sandra Brasil',
                'email': 'sandra.brasil@novik12.org',
                'phone': '248-449-1218',
                'organization': 'Novi Community Schools',
                'agency_level': 'School District'
            },
            {
                'name': 'Jolene Compton',
                'email': 'comptonj@bcschools.net',
                'phone': '989-667-8111',
                'organization': 'Bay City Public Schools',
                'agency_level': 'School District'
            },
            {
                'name': 'Lisa Crozier-Green',
                'email': 'CrozierGreenL@michigan.gov',
                'phone': '517-388-6626',
                'organization': 'Michigan Department of Education',
                'agency_level': 'State'
            },
            {
                'name': 'Melissa Nelson',
                'email': 'mnelson@vbisd.org',
                'phone': '269-539-5216',
                'organization': 'Van Buren Intermediate School District',
                'agency_level': 'ISD'
            },
            {
                'name': 'Sandra Koski',
                'email': 'koskisa@northvilleschools.org',
                'phone': '248-344-3250',
                'organization': 'Northville Public Schools',
                'agency_level': 'School District'
            },
            {
                'name': 'Erica Vega',
                'email': 'erica.vega@uticak12.org',
                'phone': '586-797-1196',
                'organization': 'Utica Community Schools',
                'agency_level': 'School District'
            },
            {
                'name': 'Nibal Hamdan',
                'email': 'nibal.hamdan@southredford.org',
                'phone': '734-629-7507',
                'organization': 'South Redford School District',
                'agency_level': 'School District'
            },
            {
                'name': 'Michael Waldie',
                'email': 'mlwaldie@stcs.org',
                'phone': '989-399-8026',
                'organization': 'St. Charles Community Schools',
                'agency_level': 'School District'
            }
        ]
        
        # Add all contacts
        for contact in contacts:
            self.add_contact(
                name=contact['name'],
                email=contact['email'],
                phone=contact['phone'],
                organization=contact['organization'],
                contact_type='Procurement Officer',
                org_type='Government',
                agency_level=contact.get('agency_level'),
                location='Michigan',
                tags=['Education', 'Michigan Schools', 'Drug Testing Prospect'],
                priority='Medium',
                source='B2B Outreach List',
                relationship_stage='New',
                notes='Michigan education contact for drug testing services outreach. Added Feb 2026.'
            )
    
    def print_summary(self):
        """Print import summary"""
        print("\n" + "="*80)
        print("📊 IMPORT SUMMARY")
        print("="*80)
        print(f"✅ Added:   {self.added_count} new contacts")
        print(f"🔄 Updated: {self.updated_count} existing contacts")
        print(f"⏩ Skipped: {self.skipped_count} contacts")
        print(f"📋 Total:   {self.added_count + self.updated_count} contacts processed")
        print("="*80 + "\n")


def main():
    """Main import function"""
    
    print("\n" + "="*80)
    print("🚀 MICHIGAN EDUCATION CONTACTS IMPORTER")
    print("="*80)
    print("Importing Michigan education contacts to GPSS CONTACTS...")
    print("="*80 + "\n")
    
    # Check environment
    if not AIRTABLE_API_KEY or not AIRTABLE_BASE_ID:
        print("❌ ERROR: Missing Airtable credentials in .env file")
        print("Required: AIRTABLE_API_KEY, AIRTABLE_BASE_ID")
        return
    
    # Initialize importer
    importer = MichiganEducationImporter()
    
    # Import Michigan education contacts
    importer.import_michigan_education_contacts()
    
    # Print summary
    importer.print_summary()
    
    print("✅ Import complete! Check your GPSS CONTACTS table in Airtable.")
    print("\n💡 NEXT STEPS:")
    print("   1. Filter by TAG: 'Michigan Schools' to see all education contacts")
    print("   2. Filter by TAG: 'Drug Testing Prospect' for outreach campaigns")
    print("   3. Use ORGANIZATION field to segment by district type")
    print()


if __name__ == "__main__":
    main()
