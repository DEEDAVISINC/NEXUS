#!/usr/bin/env python3
"""
RFP Response Helper - Automates RFP submission package creation
Integrates capability statement generation into RFP workflow

Usage:
    python3 rfp_response_helper.py <opportunity_id>
"""

import os
import sys
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List
from pyairtable import Api
from capability_statement_generator import handle_generate_capability_statement


class RFPResponseHelper:
    """Helper class for creating complete RFP response packages"""
    
    def __init__(self):
        self.airtable_key = os.environ.get('AIRTABLE_API_KEY')
        self.base_id = os.environ.get('AIRTABLE_BASE_ID')
        
        if not self.airtable_key or not self.base_id:
            raise ValueError("AIRTABLE_API_KEY and AIRTABLE_BASE_ID required")
        
        self.api = Api(self.airtable_key)
    
    def get_opportunity(self, opportunity_id: str) -> Dict:
        """Get opportunity details from Airtable"""
        table = self.api.table(self.base_id, 'Opportunities')
        record = table.get(opportunity_id)
        return record['fields']
    
    def ensure_capability_statement(self, opportunity_id: str) -> Dict:
        """Ensure capability statement exists, generate if needed"""
        
        print("🔍 Checking for existing capability statement...")
        
        # Check if linked in opportunity
        opp = self.get_opportunity(opportunity_id)
        
        if opp.get('CapabilityStatementID'):
            print("✓ Capability statement already exists")
            capstat_id = opp['CapabilityStatementID'][0]
            
            # Get details
            capstat_table = self.api.table(self.base_id, 'CapabilityStatements')
            capstat = capstat_table.get(capstat_id)
            
            return {
                'exists': True,
                'html_file': capstat['fields'].get('HTMLPath'),
                'pdf_file': capstat['fields'].get('PDFPath'),
                'airtable_record_id': capstat_id
            }
        
        # Generate new
        print("⏳ Generating new capability statement...")
        
        result = handle_generate_capability_statement(
            opportunity_id=opportunity_id,
            template='auto'
        )
        
        if result['success']:
            print("✓ Capability statement generated successfully")
            return result
        else:
            raise Exception(f"Failed to generate: {result.get('error')}")
    
    def create_submission_folder(self, opportunity_id: str) -> str:
        """Create organized submission folder"""
        
        opp = self.get_opportunity(opportunity_id)
        
        # Create folder name
        client_safe = opp.get('ClientName', 'Client').replace(' ', '_').replace('/', '_')
        rfq_safe = opp.get('OpportunityNumber', 'RFQ').replace(' ', '_').replace('/', '_')
        date_str = datetime.now().strftime('%Y%m%d')
        
        folder_name = f"RFP_Response_{client_safe}_{rfq_safe}_{date_str}"
        folder_path = Path('rfp_submissions') / folder_name
        
        # Create folder structure
        folder_path.mkdir(parents=True, exist_ok=True)
        
        print(f"📁 Created submission folder: {folder_name}")
        
        return str(folder_path)
    
    def copy_files_to_submission(self, folder_path: str, files: Dict) -> Dict:
        """Copy all RFP response files to submission folder"""
        
        copied_files = {}
        
        # 1. Capability Statement
        if files.get('capability_statement'):
            dest = Path(folder_path) / '01_Capability_Statement.pdf'
            shutil.copy(files['capability_statement'], dest)
            copied_files['capability_statement'] = str(dest)
            print(f"✓ Copied: Capability Statement")
        
        # 2. Pricing Schedule
        if files.get('pricing'):
            dest = Path(folder_path) / '02_Pricing_Schedule.xlsx'
            shutil.copy(files['pricing'], dest)
            copied_files['pricing'] = str(dest)
            print(f"✓ Copied: Pricing Schedule")
        
        # 3. Technical Proposal
        if files.get('proposal'):
            dest = Path(folder_path) / '03_Technical_Proposal.pdf'
            shutil.copy(files['proposal'], dest)
            copied_files['proposal'] = str(dest)
            print(f"✓ Copied: Technical Proposal")
        
        # 4. Certifications
        if files.get('certifications'):
            cert_folder = Path(folder_path) / '04_Certifications'
            cert_folder.mkdir(exist_ok=True)
            
            for cert_file in files['certifications']:
                cert_name = Path(cert_file).name
                dest = cert_folder / cert_name
                shutil.copy(cert_file, dest)
            
            copied_files['certifications'] = str(cert_folder)
            print(f"✓ Copied: Certifications ({len(files['certifications'])} files)")
        
        # 5. Past Performance
        if files.get('past_performance'):
            pp_folder = Path(folder_path) / '05_Past_Performance'
            pp_folder.mkdir(exist_ok=True)
            
            for pp_file in files['past_performance']:
                pp_name = Path(pp_file).name
                dest = pp_folder / pp_name
                shutil.copy(pp_file, dest)
            
            copied_files['past_performance'] = str(pp_folder)
            print(f"✓ Copied: Past Performance ({len(files['past_performance'])} files)")
        
        return copied_files
    
    def create_readme(self, folder_path: str, opportunity_id: str):
        """Create README for submission package"""
        
        opp = self.get_opportunity(opportunity_id)
        
        readme = f"""# RFP RESPONSE PACKAGE

## Opportunity Details
- **Client:** {opp.get('ClientName', 'N/A')}
- **RFQ Number:** {opp.get('OpportunityNumber', 'N/A')}
- **Title:** {opp.get('Title', 'N/A')}
- **Due Date:** {opp.get('DueDate', 'N/A')}

## Package Contents

### 01_Capability_Statement.pdf
DEE DAVIS INC capability statement tailored for this opportunity.

### 02_Pricing_Schedule.xlsx
Complete pricing breakdown for all line items.

### 03_Technical_Proposal.pdf
Technical approach and methodology.

### 04_Certifications/
All required certifications (EDWOSB, WOSB, etc.)

### 05_Past_Performance/
References and past performance documentation.

## Submission Instructions

1. Review all documents for accuracy
2. Verify pricing is competitive
3. Check all required sections are included
4. Submit via portal or email to procurement officer

## Contact
- **Dee Davis, President & CEO**
- **Phone:** 248-376-4550
- **Email:** info@deedavis.biz

---

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
NEXUS RFP Response Helper v1.0
"""
        
        readme_path = Path(folder_path) / 'README.md'
        with open(readme_path, 'w') as f:
            f.write(readme)
        
        print(f"✓ Created: README.md")
    
    def create_cover_letter(self, opportunity_id: str, folder_path: str) -> str:
        """Create cover letter for submission"""
        
        opp = self.get_opportunity(opportunity_id)
        
        cover_letter = f"""
DEE DAVIS INC
755 W Big Beaver Rd, Suite 2020
Troy, MI 48084
248-376-4550
info@deedavis.biz

{datetime.now().strftime('%B %d, %Y')}

{opp.get('ProcurementOfficer', 'Procurement Officer')}
{opp.get('ClientName', '')}
{opp.get('ClientAddress', '')}

RE: Response to {opp.get('OpportunityNumber', 'RFQ')} - {opp.get('Title', '')}

Dear {opp.get('ProcurementOfficer', 'Procurement Officer')}:

DEE DAVIS INC is pleased to submit our response to {opp.get('OpportunityNumber', 'your solicitation')} 
for {opp.get('Title', 'the referenced project')}.

As a certified EDWOSB with proven experience in government contracting, we are confident we can 
provide exceptional value to {opp.get('ClientName', 'your agency')}. Our strategic partnerships 
with industry leaders like Grainger and Fastenal ensure competitive pricing and reliable delivery.

This submission includes:
• Capability Statement demonstrating our qualifications
• Competitive Pricing Schedule
• Technical Approach and Methodology
• Required Certifications (EDWOSB, WOSB, MBE, WBE)
• Past Performance References

We have carefully reviewed all requirements and confirm our ability to meet or exceed all 
specifications. Our 98%+ on-time delivery rate and 100% compliance record demonstrate our 
commitment to excellence.

Thank you for considering DEE DAVIS INC. We look forward to the opportunity to serve 
{opp.get('ClientName', 'your agency')}.

Sincerely,


Dee Davis
President & CEO
DEE DAVIS INC

Enclosures: As listed above
"""
        
        cover_letter_path = Path(folder_path) / '00_Cover_Letter.txt'
        with open(cover_letter_path, 'w') as f:
            f.write(cover_letter)
        
        print(f"✓ Created: Cover Letter")
        
        return str(cover_letter_path)
    
    def create_email_draft(self, opportunity_id: str, capstat_pdf: str) -> Dict:
        """Create email draft with capability statement attached"""
        
        opp = self.get_opportunity(opportunity_id)
        
        email = {
            'to': opp.get('ProcurementOfficerEmail', ''),
            'cc': 'info@deedavis.biz',
            'subject': f"RFP Response - {opp.get('ClientName', 'Client')} {opp.get('OpportunityNumber', 'RFQ')}",
            'body': f"""Dear {opp.get('ProcurementOfficer', 'Procurement Officer')},

DEE DAVIS INC is pleased to submit our response to {opp.get('OpportunityNumber', 'your solicitation')} for {opp.get('Title', 'the referenced project')}.

As a certified EDWOSB with proven experience in {opp.get('Category', 'government contracting')}, we are confident we can deliver exceptional value to {opp.get('ClientName', 'your agency')}.

Attached please find:
1. Capability Statement
2. Pricing Schedule
3. Technical Proposal
4. Required Certifications
5. Past Performance References

Key highlights:
• EDWOSB Certified - Meets socioeconomic goals
• Strategic partnerships ensure competitive pricing
• 98%+ on-time delivery record
• Nationwide coverage and support

We look forward to the opportunity to serve {opp.get('ClientName', 'your agency')}.

Best regards,

Dee Davis, President & CEO
DEE DAVIS INC
248-376-4550
info@deedavis.biz
www.deedavis.biz
""",
            'attachments': [
                capstat_pdf
            ]
        }
        
        return email
    
    def create_complete_package(self, opportunity_id: str) -> Dict:
        """Create complete RFP response package"""
        
        print()
        print("=" * 60)
        print("📦 CREATING COMPLETE RFP RESPONSE PACKAGE")
        print("=" * 60)
        print()
        
        # 1. Ensure capability statement
        capstat = self.ensure_capability_statement(opportunity_id)
        
        # 2. Create submission folder
        folder_path = self.create_submission_folder(opportunity_id)
        
        # 3. Gather all files
        files = {
            'capability_statement': capstat['pdf_file']
            # Add other files from opportunity record
        }
        
        # 4. Copy files
        print()
        print("📋 Copying files to submission folder...")
        copied = self.copy_files_to_submission(folder_path, files)
        
        # 5. Create cover letter
        print()
        self.create_cover_letter(opportunity_id, folder_path)
        
        # 6. Create README
        self.create_readme(folder_path, opportunity_id)
        
        # 7. Create email draft
        print()
        email = self.create_email_draft(opportunity_id, capstat['pdf_file'])
        
        # Save email draft
        email_path = Path(folder_path) / 'EMAIL_DRAFT.txt'
        with open(email_path, 'w') as f:
            f.write(f"To: {email['to']}\n")
            f.write(f"CC: {email['cc']}\n")
            f.write(f"Subject: {email['subject']}\n\n")
            f.write(email['body'])
        
        print(f"✓ Created: Email Draft")
        
        print()
        print("=" * 60)
        print("✅ RFP RESPONSE PACKAGE COMPLETE!")
        print("=" * 60)
        print()
        print(f"📁 Location: {folder_path}")
        print()
        print("📋 Package includes:")
        print("  • Capability Statement (PDF)")
        print("  • Cover Letter")
        print("  • Email Draft (ready to send)")
        print("  • README with instructions")
        print()
        
        return {
            'success': True,
            'folder_path': folder_path,
            'files': copied,
            'email_draft': email
        }


def main():
    """Main function"""
    
    if len(sys.argv) < 2:
        print("Usage: python3 rfp_response_helper.py <opportunity_id>")
        print("Example: python3 rfp_response_helper.py recABC123XYZ")
        sys.exit(1)
    
    opportunity_id = sys.argv[1]
    
    print("=" * 60)
    print("🚀 RFP RESPONSE PACKAGE CREATOR")
    print("=" * 60)
    print()
    print(f"Opportunity ID: {opportunity_id}")
    print()
    
    try:
        helper = RFPResponseHelper()
        result = helper.create_complete_package(opportunity_id)
        
        if result['success']:
            print("🎉 Package ready for submission!")
            print()
            
            # Offer to open folder
            response = input("Open submission folder? (y/n): ")
            if response.lower() == 'y':
                import subprocess
                subprocess.run(['open', result['folder_path']])
    
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
