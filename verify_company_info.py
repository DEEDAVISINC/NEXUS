"""
Verify Company Information is Loaded Correctly
Run this to confirm all company info is in the system
"""

import os
import re

def load_env_file():
    """Load .env file manually"""
    env_vars = {}
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    # Remove quotes
                    value = value.strip('"').strip("'")
                    env_vars[key] = value
    
    return env_vars

# Load environment variables
env_vars = load_env_file()

def verify_company_info():
    """Check that all required company information is loaded"""
    
    print("\n" + "="*70)
    print("🔍 VERIFYING COMPANY INFORMATION IN SYSTEM")
    print("="*70 + "\n")
    
    required_fields = {
        'COMPANY_NAME': 'Company Name',
        'CONTACT_NAME': 'Contact Name',
        'CONTACT_TITLE': 'Contact Title',
        'CONTACT_EMAIL': 'Email Address',
        'CONTACT_PHONE': 'Phone Number',
        'CAGE_CODE': 'CAGE Code',
        'UEI_NUMBER': 'UEI/SAM Registration',
        'CERTIFICATIONS': 'Certifications',
    }
    
    optional_fields = {
        'GSA_SCHEDULE': 'GSA Schedule',
        'BUSINESS_DESCRIPTION': 'Business Description',
    }
    
    all_good = True
    
    # Check required fields
    print("📋 REQUIRED INFORMATION:")
    print("-" * 70)
    
    for env_var, display_name in required_fields.items():
        value = env_vars.get(env_var, '')
        
        if value and '[' not in value and 'YOUR' not in value.upper():
            status = "✅"
            display_value = value[:50] + "..." if len(value) > 50 else value
        else:
            status = "❌ MISSING"
            display_value = "Not set or placeholder"
            all_good = False
        
        print(f"{status} {display_name:25} {display_value}")
    
    # Check optional fields
    print("\n📝 OPTIONAL INFORMATION:")
    print("-" * 70)
    
    for env_var, display_name in optional_fields.items():
        value = env_vars.get(env_var, '')
        
        if value:
            status = "✅"
            display_value = value[:50] + "..." if len(value) > 50 else value
        else:
            status = "⚪ Not Set (Optional)"
            display_value = "Not provided"
        
        print(f"{status} {display_name:25} {display_value}")
    
    # Summary
    print("\n" + "="*70)
    if all_good:
        print("✅ ALL REQUIRED INFORMATION IS LOADED!")
        print("\n🎉 Your system is ready to auto-generate letters!")
        print("\nRun: python3 contracting_officer_outreach.py")
        print("All letters will automatically include your company information.")
    else:
        print("❌ SOME REQUIRED INFORMATION IS MISSING")
        print("\nPlease check your .env file and add missing information.")
        print("See: ONE_TIME_SETUP.md for instructions")
    print("="*70 + "\n")
    
    return all_good


if __name__ == "__main__":
    verify_company_info()
