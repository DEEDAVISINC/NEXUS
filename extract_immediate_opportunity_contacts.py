#!/usr/bin/env python3
"""
EXTRACT CONTRACTING OFFICER CONTACTS FOR IMMEDIATE OPPORTUNITIES
Pulls CO info from SAM.gov and adds to GPSS CONTACTS for outreach

Dee Davis Inc. - NEXUS Backend
February 6, 2026
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

sys.path.append('/Users/deedavis/NEXUS BACKEND')

from nexus_backend import AirtableClient
from extract_buyer_contacts import BuyerContactExtractor

# Priority opportunities to extract contacts for
PRIORITY_OPPORTUNITIES = [
    {
        'rfp': '36C24826Q0302',
        'name': 'VA Orlando Courier Service',
        'deadline': '2026-02-12',
        'agency': 'VA Orlando Healthcare System',
        'sam_url': 'https://sam.gov/opp/36c24826q0302/view'
    },
    {
        'rfp': '140G0326Q0026',
        'name': 'FEMA Volcano Disaster Assistance',
        'deadline': '2026-02-04',
        'agency': 'USGS/FEMA',
        'sam_url': 'https://sam.gov/opp/140g0326q0026/view'
    },
    {
        'rfp': '36C25726Q0090',
        'name': 'VA Moving and Storage Services',
        'deadline': '2026-02-19',
        'agency': 'VA',
        'sam_url': 'https://sam.gov/opp/36c25726q0090/view'
    },
    {
        'rfp': '36C24126Q0238',
        'name': 'VA Medical Waste Disposal',
        'deadline': '2026-02-11',
        'agency': 'VA',
        'sam_url': 'https://sam.gov/opp/36c24126q0238/view'
    }
]

def extract_co_from_sam_gov(opportunity):
    """
    Extracts contracting officer info from SAM.gov opportunity
    
    Note: This is a placeholder - actual implementation would:
    1. Fetch the opportunity HTML from SAM.gov
    2. Parse for CO name, email, phone
    3. Return structured contact info
    
    For now, we'll create template for manual entry
    """
    
    print(f"\n{'='*70}")
    print(f"  {opportunity['name']}")
    print(f"  RFP: {opportunity['rfp']}")
    print(f"{'='*70}")
    
    print(f"\n📋 MANUAL ACTION REQUIRED:")
    print(f"1. Go to: {opportunity['sam_url']}")
    print(f"2. Look for 'Point of Contact' or 'Contracting Officer' section")
    print(f"3. Copy the following information:")
    print(f"   - Name:")
    print(f"   - Title:")
    print(f"   - Email:")
    print(f"   - Phone:")
    print(f"\n4. This contact will be added to GPSS CONTACTS")
    print(f"5. Outreach email will be generated (like Eileen Meyer)")
    
    return {
        'opportunity_name': opportunity['name'],
        'rfp_number': opportunity['rfp'],
        'agency': opportunity['agency'],
        'deadline': opportunity['deadline'],
        'sam_url': opportunity['sam_url'],
        'co_name': None,  # To be filled manually from SAM.gov
        'co_email': None,  # To be filled manually from SAM.gov
        'co_phone': None,  # To be filled manually from SAM.gov
        'co_title': 'Contracting Officer'  # Default
    }


def add_co_to_nexus_contacts(client, contact_info):
    """
    Adds contracting officer to GPSS CONTACTS table
    Same process as adding Eileen Meyer
    """
    
    try:
        contact_data = {
            "Name": contact_info['co_name'],
            "Email": contact_info['co_email'],
            "Title": contact_info['co_title'],
            "Organization": contact_info['agency'],
            "Role Category": "Government Buyer",
            "Notes": f"Contracting Officer for {contact_info['opportunity_name']} ({contact_info['rfp_number']}). Deadline: {contact_info['deadline']}. EDWOSB outreach opportunity."
        }
        
        # Add phone if provided
        if contact_info.get('co_phone'):
            contact_data["Phone"] = contact_info['co_phone']
        
        result = client.create_record('GPSS CONTACTS', contact_data)
        
        print(f"\n✅ ADDED TO NEXUS CONTACTS:")
        print(f"   Name: {contact_info['co_name']}")
        print(f"   Title: {contact_info['co_title']}")
        print(f"   Organization: {contact_info['agency']}")
        print(f"   Email: {contact_info['co_email']}")
        print(f"   Record ID: {result['id']}")
        
        return result['id']
        
    except Exception as e:
        print(f"\n❌ Error adding contact: {e}")
        return None


def generate_outreach_email(contact_info, service_type):
    """
    Generates outreach email template for contracting officer
    Like the email we created for Eileen Meyer
    """
    
    email_templates = {
        'courier': """Subject: EDWOSB-Certified Medical Courier Provider - {opportunity_name}

Dear {co_name},

I'm writing to introduce Dee Davis Inc. as a qualified EDWOSB-certified medical courier provider for {opportunity_name} (Solicitation {rfp_number}).

**About Dee Davis Inc.:**
- EDWOSB/WOSB Certified (provides diversity value)
- Licensed Freight Broker (MC# 1647572)
- TWIC-Certified Personnel (TSA security clearance)
- 20+ Carrier Network, 200+ Trucks Available
- Multi-State Operational Capability
- CAGE Code: 8UMX3 | UEI: HJB4KNYJVGZ1

**Why Dee Davis Inc. for {agency}:**
✅ Proven transportation logistics coordination
✅ EDWOSB sole-source eligible (up to $7M under FAR 19.1505)
✅ Secure facility access (TWIC certification)
✅ 24/7 dispatch and tracking capabilities
✅ Experience with VA medical facilities (currently pursuing VA Illiana contract)

We specialize in coordinating time-sensitive medical deliveries across multi-location networks, making us well-positioned to support {agency}'s courier service requirements.

I've attached our capability statement for your review. I'd welcome a brief call to discuss how Dee Davis Inc. can support {agency}.

**Capability Statement attached.**

Best regards,

Dee Davis
Owner
Dee Davis Inc.
755 W. Big Beaver Rd., Suite 2020
Troy, Michigan 48084
Phone: 248.376.4550
Email: info@deedavis.biz

EDWOSB Certified | CAGE: 8UMX3 | MC# 1647572 | TWIC-Certified Personnel
""",
        
        'disaster': """Subject: EDWOSB Emergency Response Services - {opportunity_name}

Dear {co_name},

I'm writing to introduce Dee Davis Inc. as an EDWOSB-certified emergency response provider for {opportunity_name} (Solicitation {rfp_number}).

**Emergency Services - Immediate Deployment:**
🚨 Emergency Transportation & Logistics
🚨 Emergency Supplies & Equipment Coordination
🚨 Disaster Response Services
🚨 24/7 Availability - Rapid Response

**About Dee Davis Inc.:**
- EDWOSB/WOSB Certified (fast sole-source awards up to $7M)
- Licensed Freight Broker (MC# 1647572) - logistics expertise
- 20+ Carrier Network - nationwide rapid deployment
- TWIC-Certified Personnel - secure facility access
- CAGE Code: 8UMX3 | UEI: HJB4KNYJVGZ1

**Why Dee Davis Inc. for Emergency Response:**
✅ EDWOSB sole-source authority = fast awards when disasters strike
✅ Proven multi-state logistics coordination capability
✅ 24/7 emergency operations center
✅ Scalable response (small incidents to major disasters)
✅ Helps {agency} meet WOSB contracting goals

I've attached our emergency response capability statement. I'd welcome a brief call to discuss pre-positioning Dee Davis Inc. for emergency response support.

**Capability Statement attached.**

Best regards,

Dee Davis
Owner & Emergency Response Director
Dee Davis Inc.
755 W. Big Beaver Rd., Suite 2020
Troy, Michigan 48084
24/7 Emergency Line: 248.376.4550
Email: info@deedavis.biz

EDWOSB Certified | CAGE: 8UMX3 | Licensed Freight Broker MC# 1647572
""",
        
        'warehousing': """Subject: EDWOSB Warehousing & Logistics Services - {opportunity_name}

Dear {co_name},

I'm writing to introduce Dee Davis Inc. as an EDWOSB-certified logistics provider for {opportunity_name} (Solicitation {rfp_number}).

**Services We Coordinate:**
📦 Warehousing & Storage (nationwide facilities)
📦 Moving & Relocation Services
📦 Inventory Management
📦 Distribution & Fulfillment

**About Dee Davis Inc.:**
- EDWOSB/WOSB Certified (provides diversity value)
- Licensed Freight Broker (MC# 1647572)
- 20+ Partner Network (warehouses, movers, logistics providers)
- Multi-State Coordination Capability
- CAGE Code: 8UMX3 | UEI: HJB4KNYJVGZ1

**Why Dee Davis Inc. for {agency}:**
✅ Logistics coordination is our core competency
✅ EDWOSB sole-source eligible (up to $7M)
✅ Nationwide warehouse facility partnerships
✅ Professional moving company coordination
✅ Single point of contact for complex logistics

We specialize in coordinating warehousing, moving, and storage services for federal agencies, serving as prime contractor with established subcontractor networks.

I've attached our logistics capability statement. I'd welcome a brief call to discuss how Dee Davis Inc. can support {agency}'s needs.

**Capability Statement attached.**

Best regards,

Dee Davis
Owner
Dee Davis Inc.
755 W. Big Beaver Rd., Suite 2020
Troy, Michigan 48084
Phone: 248.376.4550
Email: info@deedavis.biz

EDWOSB Certified | CAGE: 8UMX3 | Licensed Freight Broker MC# 1647572
"""
    }
    
    # Determine template based on opportunity type
    if 'courier' in contact_info['opportunity_name'].lower():
        template = email_templates['courier']
    elif 'disaster' in contact_info['opportunity_name'].lower() or 'emergency' in contact_info['opportunity_name'].lower():
        template = email_templates['disaster']
    elif 'warehouse' in contact_info['opportunity_name'].lower() or 'storage' in contact_info['opportunity_name'].lower() or 'moving' in contact_info['opportunity_name'].lower():
        template = email_templates['warehousing']
    else:
        template = email_templates['courier']  # Default
    
    # Fill in template
    email = template.format(
        co_name=contact_info['co_name'],
        opportunity_name=contact_info['opportunity_name'],
        rfp_number=contact_info['rfp_number'],
        agency=contact_info['agency']
    )
    
    return email


def main():
    """
    Main extraction workflow
    """
    
    print("="*70)
    print("  CONTRACTING OFFICER CONTACT EXTRACTION")
    print("  Immediate Opportunities - February 6, 2026")
    print("="*70)
    
    client = AirtableClient()
    
    print(f"\n📋 Processing {len(PRIORITY_OPPORTUNITIES)} opportunities\n")
    
    # Extract contact info for each opportunity
    extracted_contacts = []
    
    for opp in PRIORITY_OPPORTUNITIES:
        contact_info = extract_co_from_sam_gov(opp)
        extracted_contacts.append(contact_info)
    
    print("\n" + "="*70)
    print("  NEXT STEPS")
    print("="*70)
    
    print("\n1. **Visit each SAM.gov URL above**")
    print("2. **Copy contracting officer information**")
    print("3. **Run the add_opportunity_contacts.py script** (will be created)")
    print("4. **Generate outreach emails** (like Eileen Meyer)")
    print("5. **Submit responses + send intro emails**")
    
    print("\n📧 EMAIL TEMPLATE EXAMPLES:")
    print("\nFor VA Orlando Courier, you'll send an email like:")
    print("\n" + "-"*70)
    
    example_contact = {
        'co_name': '[CO Name from SAM.gov]',
        'opportunity_name': 'VA Orlando Courier Service',
        'rfp_number': '36C24826Q0302',
        'agency': 'VA Orlando Healthcare System'
    }
    
    print(generate_outreach_email(example_contact, 'courier'))
    print("-"*70)
    
    print("\n" + "="*70)
    print("  ✅ SYSTEM READY - MANUAL SAM.GOV LOOKUP REQUIRED")
    print("="*70)
    
    print("\n💡 TIP: Once you get CO info from SAM.gov, I'll add them to")
    print("   NEXUS CONTACTS and generate personalized outreach emails!")


if __name__ == '__main__':
    main()
