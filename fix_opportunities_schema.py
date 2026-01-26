#!/usr/bin/env python3
"""
FIX GPSS OPPORTUNITIES SCHEMA
Adds missing fields to existing opportunities so they display properly in NEXUS
"""

import os
from pyairtable import Api
from dotenv import load_dotenv
from datetime import datetime, timedelta
import re

load_dotenv()

api = Api(os.environ.get('AIRTABLE_API_KEY'))
base_id = os.environ.get('AIRTABLE_BASE_ID')
table = api.table(base_id, 'GPSS OPPORTUNITIES')

print("🔧 FIXING GPSS OPPORTUNITIES SCHEMA")
print("=" * 70)

# Get all records
print("\n📊 Fetching all opportunities...")
records = table.all()
print(f"   Found {len(records)} opportunities to process")

updated_count = 0
skipped_count = 0

for record in records:
    record_id = record['id']
    fields = record['fields']
    
    # Build updates dictionary
    updates = {}
    
    # Add default value if missing (set to $0 for now, can be updated later)
    if 'Value' not in fields and 'Estimated Value' not in fields:
        updates['Value'] = 0
    
    # Add source if missing (try to infer from name or default to Federal)
    if 'Source' not in fields:
        name = fields.get('Name', '').lower()
        if any(word in name for word in ['county', 'city', 'municipal', 'township']):
            updates['Source'] = 'Local'
        elif any(word in name for word in ['state', 'michigan', 'texas', 'california']):
            updates['Source'] = 'State'
        else:
            updates['Source'] = 'Federal'
    
    # Add agency if missing (extract from name or use placeholder)
    if 'Agency Name' not in fields and 'Agency' not in fields:
        name = fields.get('Name', '')
        # Try to extract agency from name (e.g., "ITB 4614 - Midland" -> "Midland")
        if ' - ' in name:
            potential_agency = name.split(' - ')[-1].strip()
            updates['Agency Name'] = potential_agency
        else:
            updates['Agency Name'] = 'TBD'
    
    # Add urgency based on deadline
    if 'Urgency' not in fields:
        deadline = fields.get('Deadline', fields.get('Due Date', ''))
        if deadline:
            try:
                # Parse deadline
                deadline_date = datetime.fromisoformat(deadline.replace('Z', '+00:00'))
                days_until = (deadline_date - datetime.now()).days
                
                if days_until < 0:
                    updates['Urgency'] = 'Critical'  # Overdue
                elif days_until <= 7:
                    updates['Urgency'] = 'Critical'
                elif days_until <= 14:
                    updates['Urgency'] = 'High'
                elif days_until <= 30:
                    updates['Urgency'] = 'Medium'
                else:
                    updates['Urgency'] = 'Low'
                
                updates['Days Until Due'] = max(0, days_until)
            except:
                updates['Urgency'] = 'Medium'
                updates['Days Until Due'] = 0
        else:
            updates['Urgency'] = 'Medium'
    
    # Add priority score
    if 'Priority Score' not in fields:
        # Calculate based on urgency and high value flag
        urgency = updates.get('Urgency', fields.get('Urgency', 'Medium'))
        high_value = fields.get('HIGH VALUE FLAG', False)
        
        base_score = 50
        if urgency == 'Critical':
            base_score = 85
        elif urgency == 'High':
            base_score = 70
        elif urgency == 'Medium':
            base_score = 50
        else:
            base_score = 30
        
        if high_value:
            base_score = min(100, base_score + 15)
        
        updates['Priority Score'] = base_score
    
    # Add state if missing
    if 'State' not in fields:
        name = fields.get('Name', '').lower()
        agency = updates.get('Agency Name', fields.get('Agency Name', '')).lower()
        
        # Try to detect state from name or agency
        state_keywords = {
            'michigan': 'MI',
            'midland': 'MI',
            'livonia': 'MI',
            'warren': 'MI',
            'madison heights': 'MI',
            'oakland': 'MI',
            'jackson': 'MI',
            'texas': 'TX',
            'cps energy': 'TX',
            'san antonio': 'TX',
            'california': 'CA',
            'georgia': 'GA',
            'maryland': 'MD',
            'illinois': 'IL'
        }
        
        detected_state = 'Federal'  # Default
        for keyword, state_code in state_keywords.items():
            if keyword in name or keyword in agency:
                detected_state = state_code
                break
        
        updates['State'] = detected_state
    
    # Add category if missing
    if 'Opportunity Category' not in fields and 'Category' not in fields:
        name = fields.get('Name', '').lower()
        
        if any(word in name for word in ['container', 'storage', 'equipment']):
            updates['Opportunity Category'] = 'Equipment & Supplies'
        elif any(word in name for word in ['lawn', 'landscape', 'grass', 'topsoil', 'aggregate', 'materials']):
            updates['Opportunity Category'] = 'Construction Materials'
        elif any(word in name for word in ['salt', 'chlorine', 'chemical']):
            updates['Opportunity Category'] = 'Chemicals'
        elif any(word in name for word in ['paper', 'wipers', 'supplies']):
            updates['Opportunity Category'] = 'Office & Industrial Supplies'
        else:
            updates['Opportunity Category'] = 'Other'
    
    # Add strategic fit
    if 'Strategic Fit' not in fields:
        priority = updates.get('Priority Score', fields.get('Priority Score', 50))
        if priority >= 80:
            updates['Strategic Fit'] = 'Excellent'
        elif priority >= 60:
            updates['Strategic Fit'] = 'Good'
        else:
            updates['Strategic Fit'] = 'Fair'
    
    # Add pipeline stage
    if 'Pipeline Stage' not in fields:
        status = fields.get('Source Status', 'NEW')
        if status == 'NEW':
            updates['Pipeline Stage'] = 'Active'
        elif status == 'INQUIRY SENT':
            updates['Pipeline Stage'] = 'Qualifying'
        else:
            updates['Pipeline Stage'] = 'Active'
    
    # Update if there are changes
    if updates:
        try:
            table.update(record_id, updates)
            updated_count += 1
            print(f"   ✓ Updated: {fields.get('Name', 'Unknown')[:50]} ({len(updates)} fields)")
        except Exception as e:
            print(f"   ✗ Failed to update {record_id}: {e}")
    else:
        skipped_count += 1

print("\n" + "=" * 70)
print(f"✅ MIGRATION COMPLETE")
print(f"   • Updated: {updated_count} opportunities")
print(f"   • Skipped: {skipped_count} opportunities (already had all fields)")
print(f"   • Total:   {len(records)} opportunities")
print("\n🎯 Your opportunities should now display correctly in NEXUS!")
print("   Refresh the Opportunities tab in GPSS to see the changes.")
