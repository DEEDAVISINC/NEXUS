#!/usr/bin/env python3
"""
Populate workflow queues with REAL bid data - CORRECTED VERSION
Categorizes your active bids by their ACTUAL current status
"""

import json
import os
from datetime import datetime

# ACTUAL BIDS with VERIFIED status
REAL_BIDS = {
    # =====================================================================
    # SUBMITTED - CONFIRMED with evidence (8 bids - $101K+)
    # =====================================================================
    'CPS ENERGY': {
        'value': 25000,
        'deadline': '2026-02-11',
        'status': 'submitted',
        'reason': 'Submitted Jan 26 - Signed docs in folder',
        'confirmed': True
    },
    'OAKLAND COUNTY BODY BAGS': {
        'value': 4000,
        'deadline': '2026-01-29',
        'status': 'submitted',
        'reason': 'Submitted Jan 27 (Conf #0000374755)',
        'confirmed': True
    },
    'RCOC 7797 AUTOMOTIVE': {
        'value': 3978,
        'deadline': '2026-02-04',
        'status': 'submitted',
        'reason': 'Submitted Feb 3 (Conf #0000377157)',
        'confirmed': True
    },
    'RCOC 7798 WIPER BLADES': {
        'value': 1521,
        'deadline': '2026-02-04',
        'status': 'submitted',
        'reason': 'Submitted Feb 3 (Conf #0000377182)',
        'confirmed': True
    },
    'WARREN ZEP PARTS WASHER': {
        'value': 3735,
        'deadline': '2026-02-10',
        'status': 'submitted',
        'reason': 'Submitted Feb 5 (Conf #0000378410)',
        'confirmed': True
    },
    'RCOC 7799 GREASE AIR COUPLER': {
        'value': 6128,
        'deadline': '2026-02-06',
        'status': 'submitted',
        'reason': 'Submitted Feb 5 - $6,128.35',
        'confirmed': True
    },
    'RCOC 7802 BUILDING TOOLS': {
        'value': 7292,
        'deadline': '2026-02-06',
        'status': 'submitted',
        'reason': 'Submitted Feb 5 (Conf #0000378385)',
        'confirmed': True
    },
    'RCOC 7732 PAPER': {
        'value': 80437,
        'deadline': '2026-02-10',
        'status': 'submitted',
        'reason': 'Submitted Feb 7 (Conf #0000378881)',
        'confirmed': True
    },
    
    # =====================================================================
    # URGENT - Need immediate action (2 days or less)
    # =====================================================================
    'HENRY FORD BATTERY CABINETS': {
        'value': 15000,
        'deadline': '2026-02-11',
        'status': 'find_suppliers',
        'reason': 'DUE MONDAY! No quotes yet, need suppliers ASAP'
    },
    'OAKLAND COUNTY FLOW METERS': {
        'value': 8000,
        'deadline': '2026-02-12',
        'status': 'needs_review',
        'reason': 'DUE TUESDAY! Just downloaded, needs GO/NO-GO'
    },
    'OAKLAND COUNTY TREATED SALT': {
        'value': 50000,
        'deadline': '2026-02-12',
        'status': 'needs_review',
        'reason': 'DUE TUESDAY! High value, needs quick analysis'
    },
    'PORT HURON CHEMICALS': {
        'value': 12000,
        'deadline': '2026-02-12',
        'status': 'needs_review',
        'reason': 'DUE TUESDAY! Bundle bid, needs review'
    },
    
    # =====================================================================
    # THIS WEEK (2-7 days out)
    # =====================================================================
    'CPS ENERGY PADLOCKS': {
        'value': 32000,
        'deadline': '2026-02-13',
        'status': 'awaiting_quotes',
        'reason': 'Sent requests to Master Lock, Fastenal - Follow up Monday!'
    },
    'AUBURN HILLS PRESSURE WASHING': {
        'value': 5000,
        'deadline': '2026-02-13',
        'status': 'find_suppliers',
        'reason': 'Service bid, need pressure washing subcontractors'
    },
    'SHELBY TOWNSHIP POWER CABLES': {
        'value': 75000,
        'deadline': '2026-02-13',
        'status': 'find_suppliers',
        'reason': 'High value! Complete sourcing done, need final quotes'
    },
    'OAKLAND COUNTY EXAM STOOLS': {
        'value': 3000,
        'deadline': '2026-02-16',
        'status': 'awaiting_quotes',
        'reason': 'Contacted MOPEC, waiting for product specs'
    },
    'RCOC 7790 SIGNS': {
        'value': 30000,
        'deadline': '2026-02-17',
        'status': 'awaiting_quotes',
        'reason': 'Awaiting specialized quote from sign suppliers'
    },
    'RCOC 7814 TRUCKS': {
        'value': 720000,
        'deadline': '2026-02-17',
        'status': 'ready_to_price',
        'reason': '$720K! Sourcewell portal access granted - Log in and price all 16 trucks yourself!'
    },
    'OAKLAND COUNTY TRUCK EQUIPMENT': {
        'value': 20000,
        'deadline': '2026-02-17',
        'status': 'needs_review',
        'reason': 'Need to download PDF and analyze'
    },
    'GENESEE WOOD POLES': {
        'value': 45000,
        'deadline': '2026-02-18',
        'status': 'awaiting_quotes',
        'reason': 'Complete review done, sent RFQs to suppliers'
    },
    'HCMA CHLORINE': {
        'value': 30000,
        'deadline': '2026-02-18',
        'status': 'awaiting_quotes',
        'reason': 'Vendor form ready, waiting for supplier confirmation'
    },
    
    # =====================================================================
    # NEXT WEEK+ (7+ days out)
    # =====================================================================
    'LIVONIA MATERIALS': {
        'value': 15000,
        'deadline': '2026-02-23',
        'status': 'find_suppliers',
        'reason': 'Bundle bid (sand, limestone), need aggregate suppliers'
    },
    'HCMA UTILITY VEHICLES': {
        'value': 120000,
        'deadline': '2026-02-25',
        'status': 'needs_review',
        'reason': 'HIGH VALUE! Needs dealer sourcing and strategy'
    },
    'ALASKA STEEL CONTAINERS': {
        'value': 85000,
        'deadline': '2026-03-02',
        'status': 'needs_review',
        'reason': 'Long lead time, start planning now'
    }
}

def categorize_bids():
    """Categorize bids by workflow stage"""
    
    workflow = {
        'needs_review': [],
        'find_suppliers': [],
        'request_quotes': [],
        'awaiting_quotes': [],
        'ready_to_price': [],
        'generate_proposal': [],
        'final_review': [],
        'submitted': []
    }
    
    for bid_name, info in REAL_BIDS.items():
        status = info['status']
        
        bid_data = {
            'id': bid_name.replace(' ', '_'),
            'name': bid_name,
            'value': info['value'],
            'deadline': info['deadline'],
            'reason': info['reason'],
            'folder': f"BIDS:RESOURCES/{bid_name}/",
            'confirmed': info.get('confirmed', False)
        }
        
        workflow[status].append(bid_data)
    
    return workflow

def generate_workflow_data():
    """Generate workflow data for frontend"""
    
    workflow = categorize_bids()
    
    # Calculate counts
    counts = {k: len(v) for k, v in workflow.items()}
    
    # Calculate total values
    submitted_value = sum(b['value'] for b in workflow['submitted'])
    active_value = sum(
        b['value'] for stage in workflow 
        for b in workflow[stage] 
        if stage != 'submitted'
    )
    
    # Generate output file
    output = {
        'queues': workflow,
        'counts': counts,
        'updated': datetime.now().isoformat(),
        'total_active': sum(counts[k] for k in counts if k != 'submitted'),
        'total_submitted': counts['submitted'],
        'submitted_value': submitted_value,
        'active_pipeline': active_value
    }
    
    output_path = 'workflow_queues_data.json'
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)
    
    print("📊 CORRECTED Workflow Queues\n")
    print("=" * 70)
    
    # Print submitted bids
    print("\n✅ SUBMITTED BIDS (WITH CONFIRMATION):")
    print("=" * 70)
    for bid in workflow['submitted']:
        print(f"  ✓ {bid['name']:<35} ${bid['value']:>7,}  ({bid['reason']})")
    print(f"\n  TOTAL SUBMITTED: ${submitted_value:,}")
    
    # Print active bids by stage
    for stage in ['needs_review', 'find_suppliers', 'awaiting_quotes', 'ready_to_price']:
        bids = workflow[stage]
        if bids:
            stage_name = stage.replace('_', ' ').upper()
            stage_value = sum(b['value'] for b in bids)
            print(f"\n{stage_name}: {len(bids)} bids - ${stage_value:,}")
            print("-" * 70)
            for bid in sorted(bids, key=lambda x: x['deadline']):
                print(f"  - {bid['name']:<35} ${bid['value']:>7,}  Due: {bid['deadline']}")
                print(f"    → {bid['reason']}")
    
    print("\n" + "=" * 70)
    print(f"\n📈 SUMMARY:")
    print(f"   Submitted: {counts['submitted']} bids - ${submitted_value:,}")
    print(f"   Active Pipeline: {output['total_active']} bids - ${active_value:,}")
    print(f"   Total Value: ${submitted_value + active_value:,}")
    print(f"\n✅ Generated: {output_path}")
    print(f"   Last Updated: {datetime.now().strftime('%Y-%m-%d %I:%M %p')}")

if __name__ == "__main__":
    generate_workflow_data()
