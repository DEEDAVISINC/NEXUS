"""
AUTOMATIC RFP TO AIRTABLE PROCESSOR
Automatically adds ALL new RFPs, suppliers, quotes, and BUYER CONTACTS to Airtable
This should run EVERY TIME an RFP is processed - NO EXCEPTIONS
"""

import os
from datetime import datetime
from dotenv import load_dotenv
from pyairtable import Api
from extract_buyer_contacts import BuyerContactExtractor

load_dotenv()

api = Api(os.environ.get('AIRTABLE_API_KEY'))
base_id = os.environ.get('AIRTABLE_BASE_ID')

opps_table = api.table(base_id, 'GPSS OPPORTUNITIES')
subs_table = api.table(base_id, 'GPSS SUBCONTRACTORS')
quotes_table = api.table(base_id, 'GPSS SUBCONTRACTOR QUOTES')

# Initialize buyer contact extractor
contact_extractor = BuyerContactExtractor()

class AirtableAutoSync:
    """Automatically sync ALL RFP data to Airtable"""
    
    def __init__(self):
        self.opps_table = opps_table
        self.subs_table = subs_table
        self.quotes_table = quotes_table
        
    def add_opportunity(self, rfp_data, rfp_full_text=None):
        """
        Add opportunity to Airtable
        
        Required fields in rfp_data:
        - Name (str)
        - RFP NUMBER (str)
        - Deadline (str, ISO format)
        - Status (str)
        - Agency (str, optional)
        - Estimated Value (int, optional)
        - Est Profit (int, optional)
        - CONTRACTING OFFICER (str, optional) - will be extracted if rfp_full_text provided
        - Contacts Extracted (str, optional) - will be extracted if rfp_full_text provided
        
        Args:
        - rfp_data: Dict with opportunity fields
        - rfp_full_text: Full text of RFP for contact extraction (optional)
        """
        
        # Extract buyer contacts if full text provided
        if rfp_full_text:
            print("🔍 Extracting buyer contacts from RFP...")
            contacts = contact_extractor.extract_contacts_from_text(rfp_full_text)
            contacts_data = contact_extractor.format_contacts_for_airtable(contacts)
            
            # Add contact info to rfp_data
            if contacts_data.get("CONTRACTING OFFICER"):
                rfp_data["CONTRACTING OFFICER"] = contacts_data["CONTRACTING OFFICER"]
            if contacts_data.get("Contacts Extracted"):
                rfp_data["Contacts Extracted"] = contacts_data["Contacts Extracted"]
            
            print(f"✅ Extracted buyer contacts")
        
        # Check if already exists
        existing = self.opps_table.all(formula=f"{{RFP NUMBER}}='{rfp_data['RFP NUMBER']}'")
        
        if existing:
            # Update existing
            record_id = existing[0]['id']
            self.opps_table.update(record_id, rfp_data)
            print(f"✅ UPDATED OPPORTUNITY: {rfp_data['Name']}")
            return record_id
        else:
            # Create new
            result = self.opps_table.create(rfp_data)
            print(f"✨ CREATED OPPORTUNITY: {rfp_data['Name']}")
            return result['id']
    
    def add_supplier(self, supplier_data):
        """
        Add supplier/subcontractor to Airtable
        
        Required fields in supplier_data:
        - COMPANY NAME (str)
        - SERVICE TYPE (str, optional)
        - EMAIL (str, optional)
        - PHONE (str, optional)
        - CITY (str, optional)
        - STATE (str, optional)
        - NOTES (str, optional)
        """
        
        # Check if already exists
        company_name = supplier_data['COMPANY NAME']
        existing = self.subs_table.all(formula=f"{{COMPANY NAME}}='{company_name}'")
        
        if existing:
            # Update existing
            record_id = existing[0]['id']
            self.subs_table.update(record_id, supplier_data)
            print(f"✅ UPDATED SUPPLIER: {company_name}")
            return record_id
        else:
            # Create new
            result = self.subs_table.create(supplier_data)
            print(f"✨ CREATED SUPPLIER: {company_name}")
            return result['id']
    
    def link_quote(self, rfp_number, company_name, quote_data=None):
        """
        Link opportunity to supplier via quote record
        
        Args:
        - rfp_number: RFP NUMBER from opportunities table
        - company_name: COMPANY NAME from subcontractors table
        - quote_data: Optional dict with Status, RFQ Sent Date, Quote Due Date, Quote Amount, Notes
        """
        
        # Get opportunity ID
        opp = self.opps_table.all(formula=f"{{RFP NUMBER}}='{rfp_number}'")
        if not opp:
            print(f"⚠️  Opportunity not found: {rfp_number}")
            return None
        opp_id = opp[0]['id']
        
        # Get supplier ID
        sub = self.subs_table.all(formula=f"{{COMPANY NAME}}='{company_name}'")
        if not sub:
            print(f"⚠️  Supplier not found: {company_name}")
            return None
        sub_id = sub[0]['id']
        
        # Check if link already exists
        existing = self.quotes_table.all(
            formula=f"AND({{Opportunity}}='{opp_id}', {{Subcontractor}}='{sub_id}')"
        )
        
        link_data = {
            "Opportunity": [opp_id],
            "Subcontractor": [sub_id],
            "Status": quote_data.get("Status", "Pending") if quote_data else "Pending"
        }
        
        # Add optional fields if provided
        if quote_data:
            if "RFQ Sent Date" in quote_data:
                link_data["RFQ Sent Date"] = quote_data["RFQ Sent Date"]
            if "Quote Due Date" in quote_data:
                link_data["Quote Due Date"] = quote_data["Quote Due Date"]
            if "Quote Amount" in quote_data:
                link_data["Quote Amount"] = quote_data["Quote Amount"]
            if "Notes" in quote_data:
                link_data["Notes"] = quote_data["Notes"]
        
        if existing:
            # Update existing link
            record_id = existing[0]['id']
            self.quotes_table.update(record_id, link_data)
            print(f"✅ UPDATED LINK: {company_name} → {rfp_number}")
            return record_id
        else:
            # Create new link
            result = self.quotes_table.create(link_data)
            print(f"✨ CREATED LINK: {company_name} → {rfp_number}")
            return result['id']
    
    def process_rfp_complete(self, rfp_data, suppliers_list, rfp_full_text=None):
        """
        Complete RFP processing - add opportunity, extract buyer contacts, add all suppliers, and create all links
        
        Args:
        - rfp_data: Dict with opportunity info
        - suppliers_list: List of dicts, each with supplier info and optional quote_data
        - rfp_full_text: Full text of RFP for buyer contact extraction (RECOMMENDED)
        
        Example:
        rfp_data = {
            "Name": "ITB 123 - Widget Supply",
            "RFP NUMBER": "ITB 123",
            "Deadline": "2026-02-01",
            "Status": "Awaiting Quotes",
            "Agency": "City of Example"
        }
        
        suppliers_list = [
            {
                "supplier": {
                    "COMPANY NAME": "Widget Co",
                    "SERVICE TYPE": "Widget Manufacturing",
                    "EMAIL": "sales@widgetco.com"
                },
                "quote_data": {
                    "Status": "Pending",
                    "RFQ Sent Date": "2026-01-24",
                    "Quote Due Date": "2026-01-31"
                }
            }
        ]
        
        rfp_full_text = "Full RFP document text for contact extraction..."
        """
        
        print(f"\n{'='*70}")
        print(f"🚀 AUTO-PROCESSING RFP: {rfp_data['Name']}")
        print(f"{'='*70}\n")
        
        # Add opportunity (with buyer contact extraction if text provided)
        opp_id = self.add_opportunity(rfp_data, rfp_full_text)
        
        # Add all suppliers and create links
        for supplier_entry in suppliers_list:
            supplier_data = supplier_entry['supplier']
            quote_data = supplier_entry.get('quote_data')
            
            # Add supplier
            sub_id = self.add_supplier(supplier_data)
            
            # Create link
            if opp_id and sub_id:
                self.link_quote(
                    rfp_data['RFP NUMBER'],
                    supplier_data['COMPANY NAME'],
                    quote_data
                )
        
        print(f"\n✅ COMPLETE: {rfp_data['Name']} added to NEXUS Airtable")
        print(f"   - Opportunity: ✅")
        print(f"   - Buyer Contacts: ✅" if rfp_full_text else "   - Buyer Contacts: ⚠️ (no RFP text provided)")
        print(f"   - Suppliers: {len(suppliers_list)}")
        print(f"   - Links: {len(suppliers_list)}")
        print(f"\n{'='*70}\n")


# Example usage
if __name__ == "__main__":
    sync = AirtableAutoSync()
    
    # Example: New RFP comes in
    example_rfp = {
        "Name": "Example RFP - Test",
        "RFP NUMBER": "TEST-001",
        "Deadline": "2026-02-15",
        "Status": "Awaiting Quotes",
        "Agency": "Test Agency"
    }
    
    example_suppliers = [
        {
            "supplier": {
                "COMPANY NAME": "Test Supplier Inc",
                "SERVICE TYPE": "Test Services",
                "EMAIL": "test@example.com",
                "NOTES": "Test supplier for demonstration"
            },
            "quote_data": {
                "Status": "Pending",
                "RFQ Sent Date": "2026-01-24",
                "Notes": "Test quote request"
            }
        }
    ]
    
    # This automatically adds EVERYTHING to Airtable
    # sync.process_rfp_complete(example_rfp, example_suppliers)
    
    print("Auto-sync module loaded and ready.")
    print("Import this in your RFP processing scripts to automatically add to Airtable.")
