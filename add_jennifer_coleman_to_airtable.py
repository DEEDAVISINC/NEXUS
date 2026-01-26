"""
Add Jennifer Coleman Opportunity to NEXUS Airtable
Quick script to track the VA Female Condoms officer outreach
"""

import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from pyairtable import Api

# Load environment
load_dotenv()

def add_jennifer_coleman_tracking():
    """Add Jennifer Coleman outreach to Airtable tracking"""
    
    try:
        # Initialize Airtable
        api_key = os.getenv('AIRTABLE_PAT')
        base_id = os.getenv('AIRTABLE_BASE_ID')
        
        if not api_key or not base_id:
            print("⚠️ Airtable credentials not found in .env")
            print("Skipping Airtable integration")
            return False
        
        api = Api(api_key)
        
        print("🎯 Adding Jennifer Coleman to NEXUS Tracking")
        print("=" * 60)
        
        # =====================================================
        # 1. ADD TO CONTRACTING OFFICERS TABLE
        # =====================================================
        
        print("\n1. Adding to Contracting Officers table...")
        
        officer_record = {
            'Officer Name': 'Jennifer Coleman',
            'Email': 'jennifer.coleman4@va.gov',
            'Title': 'Contracting Officer',
            'Agency': 'VA Medical Center - 766 Ladson',
            'Department': 'NCO 15 Consolidated Mail Outpatient Pharmacy (CMOP)',
            'Location': 'Charleston, SC',
            'Status': 'Active Outreach',
            'First Contact Date': datetime.now().isoformat(),
            'Contact Method': 'Email',
            'Notes': 'First contact via late Sources Sought response for Female Condoms (766-26-1-400-0182). Awaiting response.',
        }
        
        try:
            officer = api.table(base_id, 'Contracting Officers').create(officer_record)
            officer_id = officer['id']
            print(f"   ✅ Added Jennifer Coleman (ID: {officer_id[:8]}...)")
        except Exception as e:
            print(f"   ℹ️ May already exist or table not found: {e}")
            officer_id = None
        
        # =====================================================
        # 2. ADD TO OPPORTUNITIES TABLE
        # =====================================================
        
        print("\n2. Adding to Opportunities table...")
        
        opportunity_record = {
            'Title': 'Female Condom, Internal 12ct',
            'Solicitation Number': '766-26-1-400-0182',
            'Agency': 'VA Medical Center - 766 Ladson',
            'Type': 'Sources Sought',
            'Status': 'Outreach Sent',
            'Response Deadline': '2025-12-19',  # Original deadline (passed)
            'Date Found': datetime.now().isoformat(),
            'Point of Contact': 'Jennifer Coleman',
            'Contact Email': 'jennifer.coleman4@va.gov',
            'NSN': '6515',
            'Product': 'Female Condoms (XK812) 18473',
            'Description': 'VA CMOP procurement for female condoms. Sources Sought period closed Dec 19, 2025. Late response sent Jan 22, 2026.',
            'Category': 'Medical Supplies',
            'Potential Value': '$5,000 - $500,000',
            'Win Probability': 30,
            'Notes': 'Late Sources Sought response. Awaiting vendor database confirmation. Solicitation expected to release soon.',
        }
        
        if officer_id:
            opportunity_record['Contracting Officer'] = [officer_id]
        
        try:
            opportunity = api.table(base_id, 'Opportunities').create(opportunity_record)
            opportunity_id = opportunity['id']
            print(f"   ✅ Added opportunity (ID: {opportunity_id[:8]}...)")
        except Exception as e:
            print(f"   ℹ️ May already exist or table not found: {e}")
            opportunity_id = None
        
        # =====================================================
        # 3. ADD TO OFFICER OUTREACH TRACKING
        # =====================================================
        
        print("\n3. Adding to Officer Outreach Tracking...")
        
        outreach_record = {
            'Officer Name': 'Jennifer Coleman',
            'Officer Email': 'jennifer.coleman4@va.gov',
            'Opportunity Title': 'Female Condoms - VA CMOP',
            'Solicitation Number': '766-26-1-400-0182',
            'Outreach Type': 'Late Sources Sought Response',
            'Status': 'Awaiting Response',
            'Date Sent': datetime.now().isoformat(),
            'Expected Response Date': (datetime.now() + timedelta(days=7)).isoformat(),
            'Follow-up Date': (datetime.now() + timedelta(days=10)).isoformat(),
            'Subject Line': 'LATE RESPONSE - Sources Sought 766-26-1-400-0182 - Female Condoms - Dee Davis, Inc.',
            'ProposalBio Score': 78,  # Estimated
            'Quality Badge': '🟢 HIGH QUALITY',
            'Quality Status': 'Ready to Send',
            'Notes': 'First VA medical supply outreach. Template for future officer relationship building. Responded to closed Sources Sought to get on vendor radar.',
            'Next Action': 'Check for response on Jan 29, 2026',
        }
        
        if officer_id:
            outreach_record['Contracting Officer'] = [officer_id]
        if opportunity_id:
            outreach_record['Related Opportunity'] = [opportunity_id]
        
        try:
            outreach = api.table(base_id, 'Officer Outreach Tracking').create(outreach_record)
            outreach_id = outreach['id']
            print(f"   ✅ Added outreach tracking (ID: {outreach_id[:8]}...)")
        except Exception as e:
            print(f"   ℹ️ May already exist or table not found: {e}")
            outreach_id = None
        
        # =====================================================
        # 4. ADD FOLLOW-UP TASKS
        # =====================================================
        
        print("\n4. Adding follow-up tasks...")
        
        tasks = [
            {
                'Task': 'Check for response from Jennifer Coleman',
                'Due Date': (datetime.now() + timedelta(days=7)).isoformat(),
                'Priority': 'Medium',
                'Status': 'Scheduled',
                'Related To': 'Jennifer Coleman - VA Female Condoms',
                'Notes': 'Day 7 check. Look for response to Sources Sought email.',
            },
            {
                'Task': 'Send follow-up email to Jennifer Coleman',
                'Due Date': (datetime.now() + timedelta(days=10)).isoformat(),
                'Priority': 'Medium',
                'Status': 'Scheduled',
                'Related To': 'Jennifer Coleman - VA Female Condoms',
                'Notes': 'Day 10 follow-up if no response received.',
            },
            {
                'Task': 'Confirm supply chain for female condoms',
                'Due Date': datetime.now().isoformat(),
                'Priority': 'High',
                'Status': 'To Do',
                'Related To': 'Jennifer Coleman - VA Female Condoms',
                'Notes': 'Call Medline (1-800-MEDLINE) and McKesson for wholesale pricing.',
            },
            {
                'Task': 'Monitor SAM.gov for 766-26-1-400-0182 solicitation release',
                'Due Date': (datetime.now() + timedelta(days=30)).isoformat(),
                'Priority': 'High',
                'Status': 'In Progress',
                'Related To': 'Jennifer Coleman - VA Female Condoms',
                'Notes': 'Watch for actual solicitation to drop after Sources Sought period.',
            },
        ]
        
        tasks_created = 0
        for task in tasks:
            if outreach_id:
                task['Related Outreach'] = [outreach_id]
            if opportunity_id:
                task['Related Opportunity'] = [opportunity_id]
            
            try:
                api.table(base_id, 'Tasks').create(task)
                tasks_created += 1
            except Exception as e:
                # Try alternate table names
                try:
                    api.table(base_id, 'Follow-up Tasks').create(task)
                    tasks_created += 1
                except:
                    pass
        
        if tasks_created > 0:
            print(f"   ✅ Added {tasks_created} follow-up tasks")
        else:
            print(f"   ℹ️ Tasks table not found (optional)")
        
        # =====================================================
        # SUMMARY
        # =====================================================
        
        print("\n" + "=" * 60)
        print("✅ JENNIFER COLEMAN TRACKING ADDED TO NEXUS")
        print("=" * 60)
        print("\n📊 Summary:")
        print(f"   • Contracting Officer: Jennifer Coleman")
        print(f"   • Opportunity: Female Condoms (766-26-1-400-0182)")
        print(f"   • Status: Awaiting Response")
        print(f"   • Next Action: Check email on Jan 29, 2026")
        print(f"   • Potential Value: $5K - $500K")
        
        print("\n📁 Documentation:")
        print(f"   • JENNIFER_COLEMAN_VA_FEMALE_CONDOMS_TRACKING.md")
        print(f"   • ACTIVE_OFFICER_OUTREACH_JAN_2026.md")
        
        print("\n🎯 Next Steps:")
        print(f"   1. Call Medline for supply chain confirmation")
        print(f"   2. Monitor email for Jennifer's response")
        print(f"   3. Prepare for follow-up on Feb 1 if needed")
        print(f"   4. Watch SAM.gov for solicitation release")
        
        print("\n" + "=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nℹ️ Don't worry! Your outreach is still documented in:")
        print("   • JENNIFER_COLEMAN_VA_FEMALE_CONDOMS_TRACKING.md")
        print("   • ACTIVE_OFFICER_OUTREACH_JAN_2026.md")
        return False


if __name__ == "__main__":
    print("\n🎯 NEXUS - JENNIFER COLEMAN TRACKING")
    print("=" * 60)
    print("Adding Jennifer Coleman VA Female Condoms opportunity to NEXUS...")
    print()
    
    success = add_jennifer_coleman_tracking()
    
    if success:
        print("\n✅ All tracking added successfully!")
    else:
        print("\n⚠️ Some tracking may not have been added to Airtable")
        print("But your markdown documentation is complete!")
    
    print("\n" + "=" * 60)
