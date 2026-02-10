#!/usr/bin/env python3
"""
Generate Bid Status Agenda - Shows what's done and what needs action
Run this daily or after solicitation processing
"""

import os
from datetime import datetime, timedelta
from pyairtable import Api
from dotenv import load_dotenv

load_dotenv()

api = Api(os.getenv('AIRTABLE_API_KEY'))
base_id = os.getenv('AIRTABLE_BASE_ID')

opportunities = api.table(base_id, 'GPSS OPPORTUNITIES')

def generate_bid_status_agenda():
    """Generate markdown agenda showing bid statuses"""
    
    print("📊 Generating bid status agenda...")
    
    # Get all active opportunities
    all_opps = opportunities.all()
    
    # Categorize by status
    review_needed = []
    quotes_requested = []
    ready_to_submit = []
    urgent = []
    submitted = []
    
    today = datetime.now()
    
    for record in all_opps:
        fields = record.get('fields', {})
        
        # Skip if no deadline
        deadline_str = fields.get('Deadline')
        if not deadline_str:
            continue
        
        # Parse deadline
        try:
            deadline = datetime.strptime(deadline_str, '%Y-%m-%d')
            days_left = (deadline - today).days
        except:
            continue
        
        # ONLY show FUTURE deadlines (skip if past)
        if days_left < 0:
            continue
        
        # Skip if deadline is too far out (more than 30 days)
        if days_left > 30:
            continue
        
        name = fields.get('Name', 'Unknown')
        
        # Skip Sources Sought and Forecasts (not real solicitations)
        skip_keywords = ['SOURCES SOUGHT', 'FORECASTED', '[FORECAST', 'PRE-SOLICITATION', 
                        'NOTICE OF INTENT', 'INTENT TO SOLE SOURCE', 'RFI -']
        if any(skip in name.upper() for skip in skip_keywords):
            continue
        
        # Get value
        value = fields.get('VALUE', 0) or 0
        
        status = fields.get('STATUS', '')
        rfp_number = fields.get('RFP NUMBER', '')
        notes = fields.get('Notes', '')
        
        opp_data = {
            'name': name,
            'rfp': rfp_number,
            'deadline': deadline,
            'days_left': days_left,
            'value': value,
            'status': status,
            'notes': notes,
            'record_id': record['id']
        }
        
        # Categorize
        if 'submitted' in status.lower() or 'sent' in status.lower():
            submitted.append(opp_data)
        elif days_left <= 3:
            urgent.append(opp_data)
        elif 'ready' in status.lower():
            ready_to_submit.append(opp_data)
        elif 'quote' in status.lower() and 'requested' in status.lower():
            quotes_requested.append(opp_data)
        else:
            review_needed.append(opp_data)
    
    # Generate markdown
    agenda_path = "BID_STATUS_AGENDA.md"
    
    with open(agenda_path, 'w') as f:
        f.write(f"# 📊 BID STATUS DASHBOARD\n")
        f.write(f"**Generated:** {datetime.now().strftime('%A, %B %d, %Y at %I:%M %p')}\n\n")
        f.write("---\n\n")
        
        # Summary
        total = len(review_needed) + len(quotes_requested) + len(ready_to_submit) + len(urgent)
        f.write(f"## 📈 OVERVIEW\n\n")
        f.write(f"- **Active Bids:** {total}\n")
        f.write(f"- **Need Review:** {len(review_needed)}\n")
        f.write(f"- **Quotes Requested:** {len(quotes_requested)}\n")
        f.write(f"- **Ready to Submit:** {len(ready_to_submit)}\n")
        f.write(f"- **Urgent (≤3 days):** {len(urgent)}\n")
        f.write(f"- **Submitted:** {len(submitted)}\n\n")
        f.write("---\n\n")
        
        # Urgent section
        if urgent:
            f.write(f"## 🔥 URGENT - ACTION NEEDED ({len(urgent)})\n\n")
            f.write("**These bids have 3 days or less until deadline!**\n\n")
            for opp in sorted(urgent, key=lambda x: x['days_left']):
                f.write(f"### ⚠️ {opp['name']}\n\n")
                f.write(f"- **Deadline:** {opp['deadline'].strftime('%A, %B %d')} ({opp['days_left']} days left)\n")
                f.write(f"- **RFP#:** {opp['rfp']}\n")
                f.write(f"- **Value:** ${opp['value']:,.0f}\n")
                f.write(f"- **Status:** {opp['status']}\n")
                
                # Check for supplier info in notes
                if 'found' in opp['notes'].lower() and 'supplier' in opp['notes'].lower():
                    f.write(f"- ✅ Suppliers found automatically\n")
                    f.write(f"- 📋 **ACTION:** Review recommendations and request quotes\n")
                else:
                    f.write(f"- ⚠️ **ACTION:** Find suppliers and request quotes ASAP\n")
                
                f.write(f"\n**Checklist:**\n")
                f.write(f"- [ ] Review analysis document\n")
                f.write(f"- [ ] Request quotes from 3-5 suppliers\n")
                f.write(f"- [ ] Receive quotes\n")
                f.write(f"- [ ] Submit bid\n\n")
            
            f.write("---\n\n")
        
        # Review needed
        if review_needed:
            f.write(f"## 📋 READY TO REVIEW ({len(review_needed)})\n\n")
            f.write("**These bids have been processed and need your review:**\n\n")
            for opp in sorted(review_needed, key=lambda x: x['days_left']):
                f.write(f"### {opp['name']}\n\n")
                f.write(f"- **Deadline:** {opp['deadline'].strftime('%A, %B %d')} ({opp['days_left']} days left)\n")
                f.write(f"- **RFP#:** {opp['rfp']}\n")
                f.write(f"- **Value:** ${opp['value']:,.0f}\n")
                
                # Parse notes for supplier info
                if 'found' in opp['notes'].lower():
                    supplier_count = 0
                    if 'subcontractors' in opp['notes'].lower() or 'suppliers' in opp['notes'].lower():
                        import re
                        match = re.search(r'(\d+)\s+(?:supplier|subcontractor)', opp['notes'].lower())
                        if match:
                            supplier_count = int(match.group(1))
                    
                    if supplier_count > 0:
                        f.write(f"- ✅ {supplier_count} suppliers/subs found automatically\n")
                        f.write(f"- 📋 **ACTION:** Review recommendations\n")
                    else:
                        f.write(f"- ✅ Processed automatically\n")
                        f.write(f"- 📋 **ACTION:** Review analysis\n")
                else:
                    f.write(f"- 📋 **ACTION:** Analyze opportunity\n")
                
                f.write(f"\n**Next Steps:**\n")
                f.write(f"1. [ ] Open analysis document in BIDS:RESOURCES/\n")
                f.write(f"2. [ ] Review supplier recommendations\n")
                f.write(f"3. [ ] Request quotes\n\n")
            
            f.write("---\n\n")
        
        # Quotes requested
        if quotes_requested:
            f.write(f"## 📞 QUOTES REQUESTED ({len(quotes_requested)})\n\n")
            f.write("**Waiting for supplier responses:**\n\n")
            for opp in sorted(quotes_requested, key=lambda x: x['days_left']):
                f.write(f"### {opp['name']}\n\n")
                f.write(f"- **Deadline:** {opp['deadline'].strftime('%A, %B %d')} ({opp['days_left']} days left)\n")
                f.write(f"- **Status:** {opp['status']}\n")
                f.write(f"- ⏳ **ACTION:** Wait for quotes or follow up\n\n")
            
            f.write("---\n\n")
        
        # Ready to submit
        if ready_to_submit:
            f.write(f"## ✅ READY TO SUBMIT ({len(ready_to_submit)})\n\n")
            f.write("**Quotes received, ready for submission:**\n\n")
            for opp in sorted(ready_to_submit, key=lambda x: x['days_left']):
                f.write(f"### {opp['name']}\n\n")
                f.write(f"- **Deadline:** {opp['deadline'].strftime('%A, %B %d')} ({opp['days_left']} days left)\n")
                f.write(f"- ✅ Quotes received\n")
                f.write(f"- 📝 **ACTION:** Prepare and submit bid\n\n")
            
            f.write("---\n\n")
        
        # Submitted
        if submitted:
            f.write(f"## 📤 SUBMITTED ({len(submitted)})\n\n")
            f.write("**Awaiting award decision:**\n\n")
            for opp in submitted:
                f.write(f"- {opp['name']} (Submitted)\n")
            
            f.write("\n---\n\n")
        
        # Summary footer
        f.write("## 🎯 TODAY'S PRIORITIES\n\n")
        
        priority_list = []
        
        if urgent:
            priority_list.append(f"1. ⚠️ **URGENT:** Handle {len(urgent)} bid(s) with ≤3 days left")
        
        if ready_to_submit:
            priority_list.append(f"2. ✅ Submit {len(ready_to_submit)} bid(s) that are ready")
        
        if review_needed:
            priority_list.append(f"3. 📋 Review {len(review_needed)} bid(s) with supplier recommendations")
        
        if quotes_requested:
            priority_list.append(f"4. 📞 Follow up on {len(quotes_requested)} quote request(s)")
        
        if priority_list:
            for item in priority_list:
                f.write(f"{item}\n")
        else:
            f.write("✨ No pending actions - Great job!\n")
        
        f.write("\n---\n\n")
        f.write("*This agenda is automatically generated. Run `python3 generate_bid_status_agenda.py` to refresh.*\n")
    
    print(f"✅ Agenda generated: {agenda_path}")
    print(f"\n📊 Summary:")
    print(f"   - Review Needed: {len(review_needed)}")
    print(f"   - Quotes Requested: {len(quotes_requested)}")
    print(f"   - Ready to Submit: {len(ready_to_submit)}")
    print(f"   - Urgent: {len(urgent)}")
    print(f"   - Submitted: {len(submitted)}")
    print(f"\n🎯 Open BID_STATUS_AGENDA.md to see your action list!")

if __name__ == "__main__":
    generate_bid_status_agenda()
