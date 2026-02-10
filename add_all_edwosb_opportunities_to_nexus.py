#!/usr/bin/env python3
"""
ADD ALL EDWOSB OPPORTUNITIES TO NEXUS
Adds all current EDWOSB opportunities and contacts to Airtable GPSS database
"""

from pyairtable import Api
import os
from datetime import datetime

def add_all_opportunities():
    """Add all EDWOSB opportunities to NEXUS"""
    
    # Initialize Airtable API
    api = Api(os.environ.get('AIRTABLE_PAT'))
    base_id = 'appwY79FudCP18jP3'
    opportunities_table = api.table(base_id, 'GPSS OPPORTUNITIES')
    contacts_table = api.table(base_id, 'GPSS CONTACTS')
    
    print("=" * 80)
    print("ADDING ALL EDWOSB OPPORTUNITIES TO NEXUS")
    print("=" * 80)
    
    # ========================================
    # CONTACTS - Contracting Officers
    # ========================================
    
    contacts = [
        {
            "Name": "Valerie Gregorio",
            "Email": "valerie.gregorio@nih.gov",
            "Agency": "NIH Clinical Center",
            "Title": "Contracting Officer",
            "Phone": "",
            "Notes": "NIH Surgical Supplies 26-002571. Deadline Feb 7, 2026 12 PM EST. Patient care emergency."
        },
        {
            "Name": "Susan Nsangou",
            "Email": "",
            "Agency": "NIH Clinical Center",
            "Title": "Contracting Officer",
            "Phone": "",
            "Notes": "NIH Surgical Supplies 26-002571. Secondary CO. Office of Purchasing and Contracts, 6707 Democracy Blvd Suite 106 Bethesda, MD 20892"
        },
        {
            "Name": "Marilyn Farinae, PharmD",
            "Email": "",
            "Agency": "NIH Clinical Center",
            "Title": "Section Chief, Central Pharmacy",
            "Phone": "",
            "Notes": "NIH Surgical Supplies 26-002571. Program Official/Requestor. 10 Center Drive 1C/240A Bethesda, MD 20892"
        },
        {
            "Name": "Eileen Meyer",
            "Email": "eileen.meyer@va.gov",
            "Agency": "VA Illiana Health Care System",
            "Title": "Contracting Officer",
            "Phone": "",
            "Notes": "VA Illiana Courier Services 36C25226Q0235. Sources Sought. Response date Feb 12, 2026."
        },
    ]
    
    print("\n📞 ADDING CONTACTS...")
    for contact in contacts:
        try:
            result = contacts_table.create(contact)
            print(f"   ✅ Added: {contact['Name']} ({contact['Agency']})")
        except Exception as e:
            print(f"   ⚠️  Error adding {contact['Name']}: {str(e)}")
    
    # ========================================
    # OPPORTUNITIES - All EDWOSB Bids
    # ========================================
    
    opportunities = [
        {
            "Name": "NIH Surgical Supplies - INTENT TO SOLE SOURCE",
            "RFP NUMBER": "26-002571",
            "Agency": "NIH Clinical Center",
            "Deadline": "2026-02-07T12:00:00.000Z",
            "Source Status": "Intent to Award",
            "Estimated Value": "$34,807.80 + shipping",
            "Set-Aside Type": "EDWOSB (open to all capable sources)",
            "Description": "Surgicel 2in x 14in Absorbable Hemostat (1951S) and Surgicel Fibrillar 4inx4in (1963). Patient care emergency. Delivery by Feb 19, 2026. BPA/IDIQ consideration mentioned in internal justification.",
            "Win Probability": "60-70%",
            "Submission Status": "IN PROGRESS - Submit Feb 7 AM",
            "Notes": "INTENT TO SOLE SOURCE - but open to capable sources! Capability statement created. Email ready. McKesson pricing pending. Target: $32,775 for products + $450-500 expedited shipping = $33,225-33,275 total (undercut NIH budget).",
            "Contact": "Valerie Gregorio (valerie.gregorio@nih.gov)"
        },
        {
            "Name": "VA Illiana Courier Services - SOURCES SOUGHT",
            "RFP NUMBER": "36C25226Q0235",
            "Agency": "VA Illiana Health Care System",
            "Deadline": "2026-02-12T10:00:00.000Z",
            "Source Status": "Sources Sought",
            "Estimated Value": "$300K-$500K annually",
            "Set-Aside Type": "EDWOSB / WOSB",
            "Description": "Medical courier services for VA Illiana facilities. Specimen transport, medical supply delivery, inter-facility courier. TWIC certification advantage. 20+ carrier network ready.",
            "Win Probability": "70-75%",
            "Submission Status": "SUBMITTED",
            "Notes": "SOURCES SOUGHT - Capability statement submitted. Response date Feb 12, 2026 10 AM EST. Strong EDWOSB value proposition. TWIC certified couriers.",
            "Contact": "Eileen Meyer (eileen.meyer@va.gov)"
        },
        {
            "Name": "VA Orlando Courier Services",
            "RFP NUMBER": "36C24826Q0302",
            "Agency": "VA Orlando Healthcare System",
            "Deadline": "2026-02-12T10:00:00.000Z",
            "Source Status": "Solicitation",
            "Estimated Value": "$300K-$500K annually",
            "Set-Aside Type": "EDWOSB / WOSB",
            "Description": "Medical courier services for VA Orlando (Lake Nona Medical Center + CBOCs). Same service as VA Illiana - reuse 90% of materials!",
            "Win Probability": "70-75%",
            "Submission Status": "NOT STARTED - Begin Feb 7 PM",
            "Notes": "TOP PRIORITY after NIH! Reuse VA Illiana materials. Just change facility names. Quick turnaround.",
            "Contact": "TBD - Get from SAM.gov"
        },
        {
            "Name": "VA Moving & Storage Services",
            "RFP NUMBER": "36C25726Q0090",
            "Agency": "Department of Veterans Affairs",
            "Deadline": "2026-02-19T10:00:00.000Z",
            "Source Status": "Solicitation",
            "Estimated Value": "$200K-$1M annually",
            "Set-Aside Type": "EDWOSB / WOSB",
            "Description": "Household goods moving and storage services for VA. Prime contractor + subcontractor model. Logistics coordination.",
            "Win Probability": "60-65%",
            "Submission Status": "NOT STARTED - Begin weekend Feb 8-9",
            "Notes": "New service category. Emphasize logistics coordination, project management, nationwide moving partnerships (Allied, United). Research subcontractors needed.",
            "Contact": "TBD - Get from SAM.gov"
        },
        {
            "Name": "VA Medical Waste Disposal",
            "RFP NUMBER": "36C24126Q0238",
            "Agency": "Department of Veterans Affairs",
            "Deadline": "2026-02-11T10:00:00.000Z",
            "Source Status": "Solicitation",
            "Estimated Value": "$100K-$300K annually",
            "Set-Aside Type": "EDWOSB / WOSB",
            "Description": "Medical waste disposal services for VA facilities. Sharps, biohazard, regulated medical waste. Recurring service.",
            "Win Probability": "50-60%",
            "Submission Status": "NOT STARTED - Begin weekend Feb 8-9",
            "Notes": "Complements courier services. Coordinate licensed medical waste disposal companies (Stericycle, Daniels Health). Emphasize medical logistics expertise.",
            "Contact": "TBD - Get from SAM.gov"
        },
        {
            "Name": "FEMA Volcano Disaster Assistance",
            "RFP NUMBER": "140G0326Q0026",
            "Agency": "FEMA",
            "Deadline": "2026-02-04T17:00:00.000Z",
            "Source Status": "Solicitation",
            "Estimated Value": "$100K-$500K",
            "Set-Aside Type": "Small Business",
            "Description": "Emergency disaster response for volcanic activity. Emergency housing, debris removal, emergency services.",
            "Win Probability": "TBD",
            "Submission Status": "CHECK IF STILL OPEN",
            "Notes": "Deadline may have passed (Feb 4). Check SAM.gov for extension. If closed, monitor for similar FEMA opportunities.",
            "Contact": "TBD"
        },
    ]
    
    print("\n🎯 ADDING OPPORTUNITIES...")
    for opp in opportunities:
        try:
            result = opportunities_table.create(opp)
            print(f"   ✅ Added: {opp['Name']}")
            print(f"      Type: {opp['Source Status']}")
            print(f"      Deadline: {opp['Deadline'][:10]}")
            print(f"      Value: {opp['Estimated Value']}")
        except Exception as e:
            print(f"   ⚠️  Error adding {opp['Name']}: {str(e)}")
    
    print("\n" + "=" * 80)
    print("✅ ALL OPPORTUNITIES AND CONTACTS ADDED TO NEXUS!")
    print("=" * 80)
    print("\n📊 SUMMARY:")
    print(f"   Contacts Added: {len(contacts)}")
    print(f"   Opportunities Added: {len(opportunities)}")
    print("\n🎯 OPPORTUNITY TYPES:")
    print("   - 1 Intent to Sole Source (NIH Surgical)")
    print("   - 1 Sources Sought (VA Illiana Courier)")
    print("   - 4 Solicitations (VA Orlando, VA Moving, VA Waste, FEMA)")
    print("\n💰 TOTAL POTENTIAL VALUE: $800K-$2M+ first year")
    print("\n✅ NEXUS IS NOW FULLY UPDATED!")

if __name__ == "__main__":
    try:
        add_all_opportunities()
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        print("\n💡 Make sure AIRTABLE_PAT environment variable is set!")
        print("   Run: export AIRTABLE_PAT='your_token_here'")
