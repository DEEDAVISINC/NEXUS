# UPDATED RSS FEEDS CONFIGURATION
# Enhanced to capture diverse opportunity types
# Created: January 24, 2026

"""
UPDATED GOVERNMENT RSS FEEDS
- Expanded keywords for better opportunity matching
- Added service-based NAICS code feeds
- Covers full range of DEE DAVIS INC capabilities
"""

GOVERNMENT_RSS_FEEDS = [
    # ===== FEDERAL - BROAD SEARCH =====
    {
        'name': 'SAM.gov - All Opportunities',
        'url': 'https://sam.gov/api/prod/opps/v3/opportunities/rss',
        'type': 'Federal',
        'keywords': [
            # Core Services
            'consulting', 'management', 'professional services',
            'project management', 'program management', 'advisory',
            
            # Logistics & Transportation
            'logistics', 'transportation', 'shipping', 'delivery',
            'freight', 'courier', 'distribution', 'warehousing',
            
            # Emergency & Safety
            'emergency', 'disaster', 'response', 'preparedness',
            'safety equipment', 'emergency kits', 'first aid',
            
            # Facilities & Operations
            'facilities', 'operations', 'maintenance', 'janitorial',
            'grounds', 'landscape', 'cleaning', 'building services',
            
            # Administrative & Business Services
            'administrative', 'business services', 'clerical',
            'data entry', 'records management', 'document scanning',
            
            # Products & Supplies
            'supplies', 'equipment', 'materials', 'products',
            'office supplies', 'furniture', 'hardware', 'tools',
            'medical supplies', 'laboratory supplies',
            
            # IT & Technology
            'it services', 'information technology', 'software',
            'hardware', 'systems', 'networking', 'support',
            
            # Construction & Engineering
            'construction', 'engineering', 'renovation', 'repair',
            'installation', 'commissioning'
        ],
        'enabled': True,
        'verified': True
    },
    
    # ===== FEDERAL - SET-ASIDES =====
    {
        'name': 'SAM.gov - EDWOSB Set-Asides',
        'url': 'https://sam.gov/api/prod/opps/v3/opportunities/rss?setAside=EDWOSB',
        'type': 'Federal',
        'keywords': [
            'edwosb', 'women-owned', 'economically disadvantaged',
            'small business', 'set-aside', 'wosb'
        ],
        'enabled': True,
        'verified': True,
        'priority': 'HIGH'  # You're certified EDWOSB
    },
    {
        'name': 'SAM.gov - WOSB Set-Asides',
        'url': 'https://sam.gov/api/prod/opps/v3/opportunities/rss?setAside=WOSB',
        'type': 'Federal',
        'keywords': [
            'wosb', 'women-owned', 'small business', 'set-aside'
        ],
        'enabled': True,
        'verified': True,
        'priority': 'HIGH'  # You're certified WOSB
    },
    
    # ===== FEDERAL - PROFESSIONAL SERVICES (NAICS 541) =====
    {
        'name': 'SAM.gov - Management Consulting (541611)',
        'url': 'https://sam.gov/api/prod/opps/v3/opportunities/rss?naics=541611',
        'type': 'Federal',
        'keywords': [
            'consulting', 'management', 'advisory', 'strategy',
            'business consulting', 'organizational development'
        ],
        'enabled': True,
        'verified': False,
        'naics': '541611',
        'description': 'Administrative Management and General Management Consulting Services'
    },
    {
        'name': 'SAM.gov - Other Management Consulting (541618)',
        'url': 'https://sam.gov/api/prod/opps/v3/opportunities/rss?naics=541618',
        'type': 'Federal',
        'keywords': [
            'consulting', 'process improvement', 'efficiency',
            'operations consulting', 'management advisory'
        ],
        'enabled': True,
        'verified': False,
        'naics': '541618',
        'description': 'Other Management Consulting Services'
    },
    {
        'name': 'SAM.gov - IT Services (541512)',
        'url': 'https://sam.gov/api/prod/opps/v3/opportunities/rss?naics=541512',
        'type': 'Federal',
        'keywords': [
            'it', 'information technology', 'software', 'systems',
            'computer', 'technology', 'digital', 'cybersecurity'
        ],
        'enabled': True,
        'verified': False,
        'naics': '541512',
        'description': 'Computer Systems Design Services'
    },
    {
        'name': 'SAM.gov - Engineering Services (541330)',
        'url': 'https://sam.gov/api/prod/opps/v3/opportunities/rss?naics=541330',
        'type': 'Federal',
        'keywords': [
            'engineering', 'design', 'technical', 'cad',
            'mechanical', 'civil', 'structural', 'electrical'
        ],
        'enabled': False,  # Disabled - only enable if you provide engineering
        'verified': False,
        'naics': '541330',
        'description': 'Engineering Services'
    },
    
    # ===== FEDERAL - ADMIN & SUPPORT SERVICES (NAICS 561) =====
    {
        'name': 'SAM.gov - Admin Services (561110)',
        'url': 'https://sam.gov/api/prod/opps/v3/opportunities/rss?naics=561110',
        'type': 'Federal',
        'keywords': [
            'administrative', 'office management', 'clerical',
            'secretarial', 'administrative support'
        ],
        'enabled': True,
        'verified': False,
        'naics': '561110',
        'description': 'Office Administrative Services'
    },
    {
        'name': 'SAM.gov - Facilities Support (561210)',
        'url': 'https://sam.gov/api/prod/opps/v3/opportunities/rss?naics=561210',
        'type': 'Federal',
        'keywords': [
            'facilities', 'building services', 'maintenance',
            'janitorial', 'cleaning', 'groundskeeping'
        ],
        'enabled': True,
        'verified': False,
        'naics': '561210',
        'description': 'Facilities Support Services'
    },
    
    # ===== FEDERAL - TRANSPORTATION (NAICS 484-492) =====
    {
        'name': 'SAM.gov - Freight Transportation (484)',
        'url': 'https://sam.gov/api/prod/opps/v3/opportunities/rss?naics=484',
        'type': 'Federal',
        'keywords': [
            'freight', 'trucking', 'shipping', 'cargo',
            'delivery', 'transportation', 'hauling'
        ],
        'enabled': True,
        'verified': False,
        'naics': '484',
        'description': 'Truck Transportation'
    },
    {
        'name': 'SAM.gov - Courier Services (492)',
        'url': 'https://sam.gov/api/prod/opps/v3/opportunities/rss?naics=492',
        'type': 'Federal',
        'keywords': [
            'courier', 'messenger', 'delivery', 'local delivery',
            'mail services', 'package delivery'
        ],
        'enabled': True,
        'verified': False,
        'naics': '492',
        'description': 'Couriers and Messengers'
    },
    
    # ===== FEDERAL - EMERGENCY SERVICES (NAICS 624) =====
    {
        'name': 'SAM.gov - Emergency Services (624230)',
        'url': 'https://sam.gov/api/prod/opps/v3/opportunities/rss?naics=624230',
        'type': 'Federal',
        'keywords': [
            'emergency', 'disaster', 'response', 'relief',
            'crisis', 'recovery', 'preparedness', 'evacuation'
        ],
        'enabled': True,
        'verified': False,
        'naics': '624230',
        'description': 'Emergency and Other Relief Services'
    },
]

# IMPLEMENTATION NOTES:
"""
1. Copy this entire GOVERNMENT_RSS_FEEDS list
2. Replace the existing one in nexus_backend.py (around line 6794)
3. Restart your backend server
4. Run RSS check: The system will now capture diverse opportunities

KEYWORD STRATEGY:
- Broad keywords in "All Opportunities" feed (catches everything)
- Specific keywords in NAICS-based feeds (targeted matching)
- Set-aside feeds prioritize your certifications
- Disabled feeds can be enabled as you expand capabilities

ENABLING/DISABLING FEEDS:
- Set 'enabled': True to activate a feed
- Set 'enabled': False to skip it
- Start with EDWOSB/WOSB + your core services
- Add more as you see what works

TESTING:
After updating, test with:
```python
from nexus_backend import RSSOpportunityMonitor
monitor = RSSOpportunityMonitor()
results = monitor.check_all_feeds()
print(f"Found {results['new_opportunities']} opportunities")
```
"""

# RECOMMENDED FEEDS TO ENABLE FIRST:
PRIORITY_FEEDS = [
    "SAM.gov - All Opportunities",           # Broad coverage
    "SAM.gov - EDWOSB Set-Asides",          # Your primary certification
    "SAM.gov - WOSB Set-Asides",            # Your secondary certification
    "SAM.gov - Management Consulting",       # Core service
    "SAM.gov - Admin Services",              # Core service
    "SAM.gov - Facilities Support",          # Core service
    "SAM.gov - Freight Transportation",      # If you do logistics
]

# FEEDS TO ENABLE LATER:
SECONDARY_FEEDS = [
    "SAM.gov - Other Management Consulting",
    "SAM.gov - IT Services",                 # If you expand to IT
    "SAM.gov - Courier Services",
    "SAM.gov - Emergency Services",          # Your niche
]
