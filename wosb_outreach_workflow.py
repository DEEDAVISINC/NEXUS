"""
WOSB OPPORTUNITY OUTREACH WORKFLOW
Uses NEXUS systems for capability statements and officer outreach

This is the RIGHT way - using existing NEXUS infrastructure!
"""

import os
from dotenv import load_dotenv
from pyairtable import Api

load_dotenv()

# Initialize
api_key = os.getenv('AIRTABLE_API_KEY')
base_id = os.getenv('AIRTABLE_BASE_ID')

api = Api(api_key)
base = api.base(base_id)

# Opportunity IDs for our 2 WOSB opportunities
OPPORTUNITIES = [
    {
        'id': 'rec5SJfdAENfqa3D3',
        'name': 'CABLE ASSEMBLY',
        'rfp_number': 'SPRRA2-26-R-0008_0002',
        'sam_url': 'https://sam.gov/opp/ed07086e9ffd4879be7339b9f509457e',
        'naics': '335931',
        'deadline': '2026-02-16'
    },
    {
        'id': 'recTY3QfOammWyJIu',
        'name': 'SHIPPING and STORG',
        'rfp_number': 'SPRRA1-26-R-0032',
        'sam_url': 'https://sam.gov/opp/2ee63d8ba07149688cdabc37d468453b',
        'naics': '336413',
        'deadline': '2026-02-17'
    }
]


def generate_capability_statement(opportunity_id: str, opportunity_name: str):
    """
    Generate capability statement using NEXUS capability statement system
    This creates a record in CAPABILITY STATEMENTS table
    
    NOTE: Skipping auto-generation for now - will do manually from frontend
    """
    print(f"📄 Capability statement for {opportunity_name} will be generated from NEXUS frontend")
    return None


def create_officer_outreach_record(opportunity: dict):
    """
    Create officer outreach record in OFFICER OUTREACH TRACKING table
    This tracks that we need to contact the contracting officer
    """
    try:
        print(f"📧 Creating officer outreach record for {opportunity['name']}...")
        
        outreach_table = base.table('OFFICER OUTREACH TRACKING')
        
        # Create outreach record with correct field names
        record = outreach_table.create({
            'OPPORTUNITY TITLE': opportunity['name'],
            'SOLICITATION NUMBER': opportunity['rfp_number'],
            'STATUS': 'DRAFT',
            'PRIORITY': 'HIGH',
            'GPSS OPPORTUNITIES': [opportunity['id']],  # Link to opportunity
            'TAGS': ['SUPPLIES'],  # Use existing tag
            'SUBJECT LINE': f"EDWOSB Interest - {opportunity['name']} ({opportunity['rfp_number']})",
            'LETTER CONTENT': f"""Good morning [Contracting Officer Name],

I'm writing to express Dee Davis Inc.'s strong interest in the {opportunity['name']} solicitation ({opportunity['rfp_number']}) with a deadline of {opportunity['deadline']}.

**About Dee Davis Inc.:**
We are a certified Economically Disadvantaged Woman-Owned Small Business (EDWOSB) specializing in procurement and distribution. Our company has extensive experience sourcing quality products for government clients.

**Certifications:**
- EDWOSB Certified (SBA)
- CAGE Code: 8UMX3
- Active SAM.gov Registration
- Woman-Owned Small Business (WOSB)
- Minority Business Enterprise (MBE)
- Women's Business Enterprise (WBE)

We are well-suited for this WOSB set-aside opportunity and eager to submit a competitive proposal.

**Request:**
1. Can you confirm that the full solicitation will be available on SAM.gov on {opportunity['deadline']}?
2. Will there be a pre-proposal conference or site visit?
3. Should questions be submitted through SAM.gov, or is there another preferred method?
4. May I provide our capability statement for your files?

We are committed to delivering quality products on time and within budget. Thank you for considering Dee Davis Inc. for this opportunity.

Looking forward to your response.

Best regards,

Dee Davis
President
Dee Davis, Inc.
248-376-4550
info@deedavis.biz

CAGE Code: 8UMX3
EDWOSB Certified
SAM.gov Active

---

SAM.gov Link: {opportunity['sam_url']}

ACTION NEEDED:
1. Go to SAM.gov link above
2. Find contracting officer name and email
3. Update this record with officer info
4. Send this letter (personalize with officer name)
5. Attach capability statement""",
            'CREATED BY': 'NEXUS Workflow - WOSB Outreach'
        })
        
        print(f"   ✅ Created outreach record: {record['id']}")
        
        # Link opportunity to outreach record
        print(f"   🔗 Linking opportunity to outreach record...")
        opp_table = base.table('GPSS OPPORTUNITIES')
        opp_table.update(opportunity['id'], {
            'OFFICER OUTREACH SENT': False,  # Not sent yet - ready to send
            'OFFICER OUTREACH LINK': [record['id']]
        })
        
        print(f"   ✅ Linked!")
        return record
        
    except Exception as e:
        print(f"   ⚠️  Error: {e}")
        return None


def mark_opportunity_for_capstat_generation(opportunity_id: str, opportunity_name: str):
    """
    Mark opportunity as needing a capability statement
    This flags it in the GPSS OPPORTUNITIES table
    """
    try:
        print(f"🏷️  Marking {opportunity_name} for capability statement generation...")
        
        opp_table = base.table('GPSS OPPORTUNITIES')
        opp_table.update(opportunity_id, {
            'CAPSTATGENERATED': False,  # Flag that we need to generate one
            'Notes': f"WOSB SET-ASIDE - HIGH PRIORITY\n\nNeed to generate capability statement and reach out to contracting officer.\n\nRFP releases: {OPPORTUNITIES[0]['deadline'] if 'CABLE' in opportunity_name else OPPORTUNITIES[1]['deadline']}"
        })
        
        print(f"   ✅ Marked!")
        
    except Exception as e:
        print(f"   ⚠️ Error: {e}")


def main():
    """
    Main workflow - processes both WOSB opportunities
    """
    print("=" * 80)
    print("🎯 WOSB OPPORTUNITY OUTREACH WORKFLOW")
    print("=" * 80)
    print()
    print("Using NEXUS systems:")
    print("  - CAPABILITY STATEMENTS table")
    print("  - OFFICER OUTREACH TRACKING table")
    print("  - GPSS OPPORTUNITIES table")
    print()
    print("=" * 80)
    print()
    
    for opp in OPPORTUNITIES:
        print(f"📋 PROCESSING: {opp['name']}")
        print(f"   RFP: {opp['rfp_number']}")
        print(f"   Due: {opp['deadline']}")
        print()
        
        # Step 1: Generate capability statement
        # cap_result = generate_capability_statement(opp['id'], opp['name'])
        
        # Step 2: Create officer outreach record
        outreach_record = create_officer_outreach_record(opp)
        
        # Step 3: Mark opportunity for capstat
        mark_opportunity_for_capstat_generation(opp['id'], opp['name'])
        
        print()
        print("-" * 80)
        print()
    
    print()
    print("=" * 80)
    print("✅ WORKFLOW COMPLETE!")
    print("=" * 80)
    print()
    print("NEXT STEPS:")
    print("1. Open NEXUS frontend → GPSS → Opportunities")
    print("2. Filter for these 2 WOSB opportunities")
    print("3. Click 'Officer Outreach' tab to see records")
    print("4. Go to SAM.gov links to get contracting officer info")
    print("5. Send outreach emails from NEXUS")
    print()
    print("All tracked in Airtable automatically! 🎉")
    print()


if __name__ == '__main__':
    main()
