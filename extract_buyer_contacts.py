"""
AUTOMATIC BUYER CONTACT EXTRACTION
Extracts buyer/contracting officer contact information from RFPs
Stores in GPSS OPPORTUNITIES table
"""

import re
import os
from dotenv import load_dotenv
from pyairtable import Api

load_dotenv()

api = Api(os.environ.get('AIRTABLE_API_KEY'))
base_id = os.environ.get('AIRTABLE_BASE_ID')
opps_table = api.table(base_id, 'GPSS OPPORTUNITIES')

class BuyerContactExtractor:
    """Extract and store buyer contact information from RFPs"""
    
    def __init__(self):
        self.opps_table = opps_table
        
    def extract_contacts_from_text(self, rfp_text):
        """
        Extract buyer contact information from RFP text
        
        Looks for:
        - Names (with titles like Contracting Officer, Buyer, Procurement)
        - Email addresses
        - Phone numbers
        - Addresses
        - Submission contact info
        
        Returns dict with extracted information
        """
        
        contacts = {
            "contracting_officer": None,
            "buyer_name": None,
            "buyer_email": None,
            "buyer_phone": None,
            "buyer_address": None,
            "submission_email": None,
            "submission_address": None,
            "submission_contact": None,
            "questions_contact": None,
            "all_contacts": []
        }
        
        # Extract all email addresses
        emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', rfp_text)
        
        # Extract phone numbers (various formats)
        phones = re.findall(r'(\d{3}[-.\s]?\d{3}[-.\s]?\d{4}|\(\d{3}\)\s*\d{3}[-.\s]?\d{4})', rfp_text)
        
        # Look for contracting officer name
        co_patterns = [
            r'Contracting Officer[:\s]+([A-Z][a-z]+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',
            r'Contract Specialist[:\s]+([A-Z][a-z]+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',
            r'Buyer[:\s]+([A-Z][a-z]+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',
            r'POC[:\s]+([A-Z][a-z]+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',
            r'Point of Contact[:\s]+([A-Z][a-z]+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',
        ]
        
        for pattern in co_patterns:
            match = re.search(pattern, rfp_text, re.IGNORECASE)
            if match:
                contacts["contracting_officer"] = match.group(1)
                contacts["buyer_name"] = match.group(1)
                break
        
        # Look for submission email
        submission_patterns = [
            r'[Ss]ubmit.*?(?:to|at)[:\s]+([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,})',
            r'[Bb]id.*?(?:to|at)[:\s]+([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,})',
            r'[Pp]roposal.*?(?:to|at)[:\s]+([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,})',
        ]
        
        for pattern in submission_patterns:
            match = re.search(pattern, rfp_text)
            if match:
                contacts["submission_email"] = match.group(1)
                break
        
        # Look for questions contact
        questions_patterns = [
            r'[Qq]uestions.*?(?:to|at)[:\s]+([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,})',
            r'[Ii]nquir.*?(?:to|at)[:\s]+([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,})',
        ]
        
        for pattern in questions_patterns:
            match = re.search(pattern, rfp_text)
            if match:
                contacts["questions_contact"] = match.group(1)
                break
        
        # If we found emails, assign them
        if emails:
            if not contacts["buyer_email"] and emails:
                contacts["buyer_email"] = emails[0]
            if not contacts["submission_email"] and len(emails) > 0:
                contacts["submission_email"] = emails[0]
        
        # If we found phones, assign first one
        if phones:
            contacts["buyer_phone"] = phones[0]
        
        # Store all found contacts
        for email in emails:
            if email not in contacts["all_contacts"]:
                contacts["all_contacts"].append(email)
        
        return contacts
    
    def format_contacts_for_airtable(self, contacts):
        """
        Format extracted contacts for Airtable storage
        
        Returns:
        - CONTRACTING OFFICER: Name and primary contact
        - Contacts Extracted: All contact information
        """
        
        contracting_officer = ""
        if contacts.get("contracting_officer"):
            contracting_officer = contacts["contracting_officer"]
            if contacts.get("buyer_email"):
                contracting_officer += f"\n{contacts['buyer_email']}"
            if contacts.get("buyer_phone"):
                contracting_officer += f"\n{contacts['buyer_phone']}"
        
        contacts_extracted = []
        
        if contacts.get("submission_email"):
            contacts_extracted.append(f"Submission: {contacts['submission_email']}")
        
        if contacts.get("questions_contact"):
            contacts_extracted.append(f"Questions: {contacts['questions_contact']}")
        
        if contacts.get("buyer_email") and contacts.get("buyer_email") != contacts.get("submission_email"):
            contacts_extracted.append(f"Buyer: {contacts['buyer_email']}")
        
        for email in contacts.get("all_contacts", []):
            if email not in str(contacts_extracted):
                contacts_extracted.append(f"Contact: {email}")
        
        return {
            "CONTRACTING OFFICER": contracting_officer if contracting_officer else None,
            "Contacts Extracted": "\n".join(contacts_extracted) if contacts_extracted else None
        }
    
    def update_opportunity_contacts(self, rfp_number, contacts_data):
        """
        Update opportunity with extracted contact information
        
        Args:
        - rfp_number: RFP NUMBER to find the opportunity
        - contacts_data: Dict from format_contacts_for_airtable()
        """
        
        # Find the opportunity
        existing = self.opps_table.all(formula=f"{{RFP NUMBER}}='{rfp_number}'")
        
        if not existing:
            print(f"⚠️  Opportunity not found: {rfp_number}")
            return False
        
        record_id = existing[0]['id']
        
        # Update with contact information
        try:
            self.opps_table.update(record_id, contacts_data)
            print(f"✅ Updated contacts for: {rfp_number}")
            if contacts_data.get("CONTRACTING OFFICER"):
                print(f"   Contracting Officer: {contacts_data['CONTRACTING OFFICER'].split(chr(10))[0]}")
            return True
        except Exception as e:
            print(f"❌ Error updating contacts: {e}")
            return False
    
    def process_rfp_contacts(self, rfp_number, rfp_text):
        """
        Complete processing: extract and store contacts
        
        Args:
        - rfp_number: RFP NUMBER
        - rfp_text: Full text of the RFP document
        """
        
        print(f"\n🔍 Extracting buyer contacts from {rfp_number}...")
        
        # Extract contacts
        contacts = self.extract_contacts_from_text(rfp_text)
        
        # Format for Airtable
        contacts_data = self.format_contacts_for_airtable(contacts)
        
        # Update opportunity
        success = self.update_opportunity_contacts(rfp_number, contacts_data)
        
        if success:
            print(f"✅ Buyer contacts extracted and stored\n")
            return contacts
        else:
            print(f"⚠️  Could not store contacts\n")
            return None


# Example usage
if __name__ == "__main__":
    extractor = BuyerContactExtractor()
    
    # Example RFP text
    example_text = """
    RFQ Number: W912D0-26-Q-025982
    
    Contracting Officer: John Smith
    Email: john.smith@army.mil
    Phone: (907) 555-1234
    
    Submit proposals to: contracting@army.mil
    Questions to: john.smith@army.mil
    
    Address:
    673 SPTG/PKPC
    10471 20th Street, Suite 304
    JBER, Alaska 99506
    """
    
    # Extract contacts
    contacts = extractor.extract_contacts_from_text(example_text)
    print("Extracted contacts:")
    for key, value in contacts.items():
        if value:
            print(f"  {key}: {value}")
    
    print("\n✅ Buyer contact extractor loaded and ready")
    print("Import this in your RFP processing scripts")
