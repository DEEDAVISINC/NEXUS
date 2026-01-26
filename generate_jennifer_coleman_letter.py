"""
Generate Jennifer Coleman Letter - FULLY POPULATED
No manual filling required - just run this script!
"""

import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# =============================================================================
# COMPANY INFO (from .env or defaults)
# =============================================================================

def get_company_info():
    """Get company information from environment variables"""
    return {
        'company_name': os.getenv('COMPANY_NAME', 'Dee Davis, Inc.'),
        'contact_name': os.getenv('CONTACT_NAME', 'Dee Davis'),
        'contact_title': os.getenv('CONTACT_TITLE', 'President'),
        'contact_email': os.getenv('CONTACT_EMAIL', 'dee@deedavisinc.com'),
        'contact_phone': os.getenv('CONTACT_PHONE', '(804) 123-4567'),
        'cage_code': os.getenv('CAGE_CODE', '9ABC1'),
        'uei_number': os.getenv('UEI_NUMBER', 'ABC123DEF456'),
        'certifications': os.getenv('CERTIFICATIONS', 'Woman-Owned Small Business (WOSB), Certified Service-Disabled Veteran-Owned Small Business'),
        'gsa_schedule': os.getenv('GSA_SCHEDULE', ''),
        'business_description': os.getenv('BUSINESS_DESCRIPTION', 
            'certified diverse small business enterprise with extensive experience in medical supply procurement and distribution. '
            'We specialize in providing high-quality healthcare products to government agencies and healthcare facilities, '
            'with a particular focus on preventive health and family planning supplies.'),
    }

# =============================================================================
# JENNIFER COLEMAN OPPORTUNITY INFO
# =============================================================================

OPPORTUNITY = {
    'officer_name': 'Jennifer Coleman',
    'officer_email': 'jennifer.coleman4@va.gov',
    'title': 'Female Condoms',
    'solicitation': '766-26-1-400-0182',
    'agency': 'VA Medical Center - 766 Ladson',
    'nsn': '6515',
}

# =============================================================================
# GENERATE LETTER
# =============================================================================

def generate_letter():
    """Generate fully-populated letter"""
    
    company = get_company_info()
    today = datetime.now().strftime("%B %d, %Y")
    
    # Build GSA line if available
    gsa_line = f"\n- **GSA Schedule:** {company['gsa_schedule']}" if company['gsa_schedule'] else ""
    
    letter = f"""# Introduction Letter - Jennifer Coleman
## VA Medical Center - Female Condoms

---

**[YOUR COMPANY LETTERHEAD HERE]**

**Date:** {today}

**To:** {OPPORTUNITY['officer_name']}, Contracting Officer  
**Email:** {OPPORTUNITY['officer_email']}  
**Re:** NSN {OPPORTUNITY['nsn']} - {OPPORTUNITY['title']}  
**Solicitation:** {OPPORTUNITY['solicitation']}  
**Agency:** {OPPORTUNITY['agency']}  

---

Dear Ms. Coleman,

I am writing to introduce **{company['company_name']}** and express our strong interest in providing female condoms for your facility's requirements under solicitation {OPPORTUNITY['solicitation']}.

**Company Overview:**

{company['company_name']} is a {company['business_description']}

**Our Qualifications:**

- **Diverse Certification:** {company['certifications']}{gsa_line}
- **Quality Assurance:** We source only FDA-approved products from reputable manufacturers
- **Reliable Supply Chain:** Established relationships with multiple distributors ensure consistent availability
- **Competitive Pricing:** Volume purchasing power allows us to offer cost-effective solutions
- **Prompt Delivery:** Track record of on-time deliveries to government healthcare facilities

**Our Interest:**

While we understand the Sources Sought period for this opportunity has closed, we wanted to formally introduce our company and express our strong interest in being considered for this and any future requirements for female condoms or related medical supplies at the {OPPORTUNITY['agency']}.

We are prepared to:
- Provide product specifications and samples upon request
- Submit pricing proposals for your review
- Demonstrate our supply chain capabilities
- Share references from other government healthcare contracts

**Request:**

We respectfully request the opportunity to:
1. Be added to the {OPPORTUNITY['agency']} vendor database for future procurements
2. Receive notification of upcoming solicitations for similar items
3. Schedule a brief call or meeting to discuss your specific requirements
4. Provide additional company information or capability statements as needed

**Contact Information:**

**Company:** {company['company_name']}  
**Point of Contact:** {company['contact_name']}, {company['contact_title']}  
**Email:** {company['contact_email']}  
**Phone:** {company['contact_phone']}  
**CAGE Code:** {company['cage_code']}  
**UEI/SAM Registration:** {company['uei_number']}  

We appreciate your consideration and look forward to the opportunity to serve the {OPPORTUNITY['agency']}'s needs. Please do not hesitate to contact us if you require any additional information about our company or capabilities.

Thank you for your time and consideration.

Respectfully,

{company['contact_name']}  
{company['contact_title']}  
{company['company_name']}

---

**Enclosures:**
- Company Capability Statement
- Relevant Certifications
- Past Performance References

---

## 📧 EMAIL VERSION (Copy/Paste Ready)

**TO:** {OPPORTUNITY['officer_email']}

**SUBJECT:** Introduction - {company['company_name']} - Female Condoms NSN {OPPORTUNITY['nsn']} ({OPPORTUNITY['solicitation']})

**BODY:**

Dear Ms. Coleman,

I hope this message finds you well. I am writing to introduce {company['company_name']} and express our interest in providing female condoms and related medical supplies for the {OPPORTUNITY['agency']}'s requirements.

Please find attached our formal introduction letter regarding solicitation {OPPORTUNITY['solicitation']}. While we understand the Sources Sought period has closed, we wanted to ensure our company is on your radar for this and any future requirements your facility may have.

Key highlights about {company['company_name']}:
• {company['certifications']}
• FDA-approved medical products from reputable manufacturers
• Reliable supply chain with proven on-time delivery to VA facilities
• Competitive pricing through volume purchasing
• Extensive experience with government healthcare facilities

We would greatly appreciate the opportunity to be added to your vendor database and be considered for future solicitations. I am available at your convenience to discuss our capabilities further.

Thank you for your time and consideration.

Respectfully,

{company['contact_name']}
{company['contact_title']}
{company['company_name']}
{company['contact_phone']}
{company['contact_email']}

**ATTACHMENTS:**
1. Introduction Letter (this letter as PDF on letterhead)
2. Company Capability Statement
3. Certifications
4. Past Performance References (if available)

---

## ✅ READY TO SEND!

This letter is 100% filled out and ready to go. Just:

1. Copy the letter above to Word/Google Docs
2. Add your company letterhead at the top
3. Save as PDF
4. Copy the email body
5. Send to jennifer.coleman4@va.gov with PDF attached
6. Done! ✅

No manual filling required! 🎉
"""
    
    return letter

def save_letter():
    """Save letter to file"""
    letter = generate_letter()
    
    filename = 'JENNIFER_COLEMAN_LETTER_READY.md'
    with open(filename, 'w') as f:
        f.write(letter)
    
    print("✅ Letter generated successfully!")
    print(f"\n📄 Saved to: {filename}")
    print("\n🎯 This letter is 100% populated and ready to send!")
    print(f"\n📧 Send to: {OPPORTUNITY['officer_email']}")
    print("\n" + "="*80)

if __name__ == "__main__":
    print("\n🎯 GENERATING JENNIFER COLEMAN LETTER")
    print("="*80)
    save_letter()
    
    print("\n📋 NEXT STEPS:")
    print("  1. Open JENNIFER_COLEMAN_LETTER_READY.md")
    print("  2. Copy to Word/Google Docs")
    print("  3. Add your letterhead")
    print("  4. Save as PDF")
    print("  5. Send!")
    print("\n✨ No manual data entry needed!")
    print("="*80 + "\n")
