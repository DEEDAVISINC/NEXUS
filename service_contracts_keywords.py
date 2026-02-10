"""
Service Contracts Keywords and Configuration
============================================

Prime Contractor + Subcontractor Model
Find service opportunities, manage with subs, keep 10-25% margin

Categories:
- Janitorial & Custodial
- Landscaping & Grounds Maintenance
- Facility Maintenance & Repair
- IT Services & Support
- Security Services
- Construction & Renovation
- Moving & Relocation
- Event Services
"""

SERVICE_CONTRACTS_CATEGORIES = {
    "janitorial_custodial": {
        "display_name": "🧹 Janitorial & Custodial Services",
        "description": "Building cleaning, custodial services, facility sanitation",
        "primary_keywords": [
            "janitorial services",
            "custodial services",
            "building cleaning",
            "facility cleaning",
            "office cleaning",
            "floor maintenance",
            "window cleaning",
            "sanitation services",
            "cleaning services",
            "housekeeping services"
        ],
        "secondary_keywords": [
            "commercial cleaning",
            "government building cleaning",
            "post construction cleaning",
            "carpet cleaning",
            "floor stripping waxing",
            "pressure washing",
            "restroom cleaning",
            "trash removal",
            "recycling services",
            "green cleaning"
        ],
        "sam_gov_searches": [
            '"janitorial services" WOSB',
            '"custodial services" small business',
            '"building cleaning" EDWOSB',
            '"facility cleaning" woman owned',
            '"office cleaning services" WOSB',
            '"floor maintenance" small business',
            '"sanitation services" EDWOSB',
            '"housekeeping services" WOSB'
        ],
        "naics_codes": ["561720"],
        "estimated_contract_range": "$50K-$1M annually",
        "typical_duration": "1-3 years, with option years",
        "prime_margin": "12-20%",
        "sourcing_difficulty": "Easy - many local janitorial companies",
        "key_considerations": [
            "Sub needs workers comp insurance",
            "Background checks often required",
            "Green cleaning preference common",
            "Performance bonds for larger contracts"
        ],
        "typical_subs": ["Local janitorial companies", "Regional cleaning services"],
        "special_notes": "Very common contracts, steady revenue, easy to manage"
    },
    
    "landscaping_grounds": {
        "display_name": "🌳 Landscaping & Grounds Maintenance",
        "description": "Lawn care, landscaping, snow removal, grounds keeping",
        "primary_keywords": [
            "landscaping services",
            "grounds maintenance",
            "lawn care",
            "landscape maintenance",
            "turf management",
            "tree services",
            "snow removal",
            "grounds keeping",
            "exterior maintenance",
            "green space maintenance"
        ],
        "secondary_keywords": [
            "mowing services",
            "fertilization",
            "irrigation maintenance",
            "mulching services",
            "seasonal cleanup",
            "leaf removal",
            "ice management",
            "salt application",
            "sidewalk clearing",
            "parking lot maintenance",
            "tree trimming",
            "shrub maintenance"
        ],
        "sam_gov_searches": [
            '"landscaping services" WOSB',
            '"grounds maintenance" small business',
            '"lawn care" EDWOSB',
            '"landscape maintenance" woman owned',
            '"snow removal" WOSB',
            '"grounds keeping" small business',
            '"turf management" EDWOSB',
            '"tree services" WOSB'
        ],
        "naics_codes": ["561730"],
        "estimated_contract_range": "$50K-$500K annually",
        "typical_duration": "1-5 years (seasonal or annual)",
        "prime_margin": "15-25%",
        "sourcing_difficulty": "Easy - many local landscapers",
        "key_considerations": [
            "Seasonal variations (summer vs winter)",
            "Equipment requirements",
            "Response time for snow removal",
            "Licensed/insured required"
        ],
        "typical_subs": ["Landscape companies", "Lawn care services", "Snow removal companies"],
        "special_notes": "Snow removal can be very profitable. Multi-year terms common."
    },
    
    "facility_maintenance": {
        "display_name": "🔧 Facility Maintenance & Repair",
        "description": "Building maintenance, HVAC, electrical, plumbing, repairs",
        "primary_keywords": [
            "facility maintenance",
            "building maintenance",
            "maintenance services",
            "HVAC maintenance",
            "preventive maintenance",
            "repair services",
            "facility repair",
            "building systems maintenance",
            "mechanical maintenance",
            "electrical maintenance"
        ],
        "secondary_keywords": [
            "plumbing services",
            "HVAC repair",
            "electrical repair",
            "handyman services",
            "painting services",
            "door repair",
            "lock services",
            "ceiling repair",
            "drywall repair",
            "lighting maintenance",
            "roof maintenance",
            "elevator maintenance"
        ],
        "sam_gov_searches": [
            '"facility maintenance" WOSB',
            '"building maintenance" small business',
            '"HVAC maintenance" EDWOSB',
            '"maintenance services" woman owned',
            '"repair services" WOSB',
            '"preventive maintenance" small business',
            '"building systems" EDWOSB',
            '"mechanical maintenance" WOSB'
        ],
        "naics_codes": ["561210", "238220", "238210"],
        "estimated_contract_range": "$100K-$1M annually",
        "typical_duration": "1-5 years",
        "prime_margin": "15-20%",
        "sourcing_difficulty": "Medium - need licensed trades",
        "key_considerations": [
            "Subs need trade licenses",
            "24/7 emergency response may be required",
            "Multiple trades needed (HVAC, electrical, plumbing)",
            "Strong insurance requirements"
        ],
        "typical_subs": ["HVAC contractors", "Electricians", "Plumbers", "General handyman services"],
        "special_notes": "High value contracts. Can use multiple specialized subs."
    },
    
    "it_services": {
        "display_name": "💻 IT Services & Support",
        "description": "IT support, network services, cybersecurity, help desk",
        "primary_keywords": [
            "IT services",
            "IT support",
            "network services",
            "technical support",
            "help desk",
            "IT infrastructure",
            "system administration",
            "network administration",
            "cybersecurity services",
            "IT consulting"
        ],
        "secondary_keywords": [
            "desktop support",
            "server maintenance",
            "network installation",
            "cable installation",
            "firewall management",
            "backup services",
            "disaster recovery",
            "cloud services",
            "software installation",
            "hardware maintenance",
            "patch management",
            "security monitoring"
        ],
        "sam_gov_searches": [
            '"IT services" WOSB',
            '"IT support" small business',
            '"network services" EDWOSB',
            '"technical support" woman owned',
            '"help desk" WOSB',
            '"cybersecurity services" small business',
            '"system administration" EDWOSB',
            '"IT infrastructure" WOSB'
        ],
        "naics_codes": ["541512", "541513", "541519"],
        "estimated_contract_range": "$100K-$3M annually",
        "typical_duration": "1-5 years",
        "prime_margin": "10-18%",
        "sourcing_difficulty": "Medium - need qualified IT professionals",
        "key_considerations": [
            "Security clearances may be required",
            "Certifications important (CompTIA, CISSP, etc.)",
            "E&O insurance critical (you have this!)",
            "Response time SLAs common"
        ],
        "typical_subs": ["IT consulting firms", "MSPs (Managed Service Providers)", "Cybersecurity firms"],
        "special_notes": "Your E&O insurance is a major advantage here! High-value contracts."
    },
    
    "security_services": {
        "display_name": "🛡️ Security Services",
        "description": "Security guards, access control, surveillance monitoring",
        "primary_keywords": [
            "security services",
            "security guard",
            "protective services",
            "facility security",
            "access control",
            "security monitoring",
            "patrol services",
            "uniformed security"
        ],
        "secondary_keywords": [
            "armed security",
            "unarmed security",
            "event security",
            "building security",
            "parking enforcement",
            "surveillance monitoring",
            "CCTV monitoring",
            "alarm response",
            "security assessment",
            "loss prevention"
        ],
        "sam_gov_searches": [
            '"security services" WOSB',
            '"security guard" small business',
            '"protective services" EDWOSB',
            '"facility security" woman owned',
            '"access control" WOSB',
            '"patrol services" small business',
            '"uniformed security" EDWOSB'
        ],
        "naics_codes": ["561612", "561613"],
        "estimated_contract_range": "$200K-$2M annually",
        "typical_duration": "1-5 years",
        "prime_margin": "10-15%",
        "sourcing_difficulty": "Medium - subs need licenses/bonding",
        "key_considerations": [
            "State licensing required for security firms",
            "Background checks mandatory",
            "High insurance requirements",
            "Armed vs unarmed affects pricing",
            "Performance bonds often required"
        ],
        "typical_subs": ["Licensed security companies", "Regional security firms"],
        "special_notes": "Large contracts. Federal facilities have strict requirements."
    },
    
    "construction_renovation": {
        "display_name": "🏗️ Construction & Renovation",
        "description": "Building renovation, construction services, facility upgrades",
        "primary_keywords": [
            "construction services",
            "renovation services",
            "building renovation",
            "facility renovation",
            "remodeling services",
            "construction management",
            "general contracting",
            "facility upgrades"
        ],
        "secondary_keywords": [
            "ADA compliance",
            "accessibility upgrades",
            "restroom renovation",
            "office renovation",
            "interior renovation",
            "exterior renovation",
            "tenant improvements",
            "building modernization",
            "energy efficiency upgrades",
            "HVAC replacement",
            "roofing services",
            "flooring installation"
        ],
        "sam_gov_searches": [
            '"building renovation" WOSB',
            '"construction services" small business',
            '"facility renovation" EDWOSB',
            '"renovation services" woman owned',
            '"remodeling services" WOSB',
            '"general contracting" small business',
            '"ADA compliance" EDWOSB',
            '"facility upgrades" WOSB'
        ],
        "naics_codes": ["236220", "238210", "238310"],
        "estimated_contract_range": "$100K-$5M per project",
        "typical_duration": "Project-based (3-18 months)",
        "prime_margin": "10-20%",
        "sourcing_difficulty": "Medium-Hard - need licensed contractors",
        "key_considerations": [
            "General contractor license required (sub has)",
            "Performance & payment bonds required",
            "Prevailing wage rules apply",
            "Insurance requirements high",
            "May need architect/engineer on team"
        ],
        "typical_subs": ["General contractors", "Specialized trade contractors"],
        "special_notes": "Largest contracts. Strong past performance needed. Start with smaller renovations."
    },
    
    "moving_relocation": {
        "display_name": "🚚 Moving & Relocation Services",
        "description": "Office moves, equipment relocation, moving services",
        "primary_keywords": [
            "moving services",
            "relocation services",
            "office moving",
            "furniture moving",
            "equipment relocation",
            "office relocation",
            "moving and storage"
        ],
        "secondary_keywords": [
            "furniture installation",
            "cubicle installation",
            "office setup",
            "warehouse relocation",
            "lab relocation",
            "IT equipment moving",
            "specialty moving",
            "records relocation",
            "decommissioning services"
        ],
        "sam_gov_searches": [
            '"moving services" WOSB',
            '"relocation services" small business',
            '"office moving" EDWOSB',
            '"furniture moving" woman owned',
            '"office relocation" WOSB',
            '"equipment relocation" small business'
        ],
        "naics_codes": ["484210", "484220"],
        "estimated_contract_range": "$50K-$500K per project",
        "typical_duration": "Project-based or multi-year contract",
        "prime_margin": "15-25%",
        "sourcing_difficulty": "Easy - many moving companies",
        "key_considerations": [
            "DOT authority may be required (sub has)",
            "Insurance for valuable equipment",
            "Weekend/after-hours work common",
            "Security clearances for sensitive areas"
        ],
        "typical_subs": ["Commercial moving companies", "Specialized relocation firms"],
        "special_notes": "Government agencies relocate frequently. Can be recurring."
    },
    
    "event_services": {
        "display_name": "🎪 Event Services",
        "description": "Event planning, conferences, catering, venue services",
        "primary_keywords": [
            "event services",
            "event planning",
            "conference services",
            "catering services",
            "event management",
            "meeting services",
            "special event services"
        ],
        "secondary_keywords": [
            "conference planning",
            "AV services",
            "audio visual",
            "event setup",
            "venue management",
            "food service",
            "hospitality services",
            "registration services",
            "event coordination",
            "training event services"
        ],
        "sam_gov_searches": [
            '"event services" WOSB',
            '"event planning" small business',
            '"conference services" EDWOSB',
            '"catering services" woman owned',
            '"meeting services" WOSB',
            '"event management" small business'
        ],
        "naics_codes": ["561920", "722310"],
        "estimated_contract_range": "$25K-$250K per event or annually",
        "typical_duration": "Per event or annual contract",
        "prime_margin": "15-25%",
        "sourcing_difficulty": "Easy - many event/catering companies",
        "key_considerations": [
            "Food service licenses required (sub has)",
            "Liability insurance for events",
            "Varying event sizes and requirements",
            "Short turnaround times common"
        ],
        "typical_subs": ["Event planning companies", "Caterers", "AV companies"],
        "special_notes": "Government training events, conferences, ceremonies. Recurring annual events."
    }
}

# Weekly Search Schedule for Service Contracts
WEEKLY_SEARCH_SCHEDULE = {
    "monday": {
        "focus": "High-Value Services (IT & Security)",
        "categories": ["it_services", "security_services"],
        "searches": [
            '"IT services" WOSB',
            '"security services" small business',
            '"cybersecurity services" EDWOSB'
        ],
        "expected_results": "15-25 opportunities",
        "revenue_potential": "$100K-$3M per contract"
    },
    "tuesday": {
        "focus": "Facility Services (Janitorial & Maintenance)",
        "categories": ["janitorial_custodial", "facility_maintenance"],
        "searches": [
            '"janitorial services" WOSB',
            '"facility maintenance" small business',
            '"building maintenance" EDWOSB'
        ],
        "expected_results": "20-30 opportunities",
        "revenue_potential": "$50K-$1M per contract"
    },
    "wednesday": {
        "focus": "Outdoor Services (Landscaping & Grounds)",
        "categories": ["landscaping_grounds"],
        "searches": [
            '"landscaping services" WOSB',
            '"grounds maintenance" small business',
            '"snow removal" EDWOSB'
        ],
        "expected_results": "15-20 opportunities",
        "revenue_potential": "$50K-$500K per contract"
    },
    "thursday": {
        "focus": "Construction & Renovation",
        "categories": ["construction_renovation"],
        "searches": [
            '"building renovation" WOSB',
            '"construction services" small business',
            '"facility renovation" EDWOSB'
        ],
        "expected_results": "10-15 opportunities",
        "revenue_potential": "$100K-$5M per project"
    },
    "friday": {
        "focus": "Support Services (Moving & Events)",
        "categories": ["moving_relocation", "event_services"],
        "searches": [
            '"moving services" WOSB',
            '"event services" small business',
            '"relocation services" EDWOSB'
        ],
        "expected_results": "10-15 opportunities",
        "revenue_potential": "$25K-$500K per project"
    }
}

# Revenue Potential by Category
REVENUE_POTENTIAL = {
    "janitorial_custodial": {
        "small_contracts": "$50K-$150K",
        "medium_contracts": "$150K-$500K",
        "large_contracts": "$500K-$1M+",
        "annual_potential": "$200K-$800K",
        "prime_margin": "12-20%",
        "typical_profit": "$24K-$160K per contract",
        "special_note": "Very common, steady revenue, easy to find subs"
    },
    "landscaping_grounds": {
        "small_contracts": "$50K-$150K",
        "medium_contracts": "$150K-$300K",
        "large_contracts": "$300K-$500K+",
        "annual_potential": "$150K-$600K",
        "prime_margin": "15-25%",
        "typical_profit": "$22.5K-$150K per contract",
        "special_note": "Snow removal can double revenue in winter months"
    },
    "facility_maintenance": {
        "small_contracts": "$100K-$250K",
        "medium_contracts": "$250K-$600K",
        "large_contracts": "$600K-$1M+",
        "annual_potential": "$300K-$1M",
        "prime_margin": "15-20%",
        "typical_profit": "$45K-$200K per contract",
        "special_note": "Multi-trade contracts have higher margins"
    },
    "it_services": {
        "small_contracts": "$100K-$300K",
        "medium_contracts": "$300K-$1M",
        "large_contracts": "$1M-$3M+",
        "annual_potential": "$500K-$2M",
        "prime_margin": "10-18%",
        "typical_profit": "$50K-$360K per contract",
        "special_note": "Your E&O insurance is a major competitive advantage!"
    },
    "security_services": {
        "small_contracts": "$200K-$500K",
        "medium_contracts": "$500K-$1M",
        "large_contracts": "$1M-$2M+",
        "annual_potential": "$400K-$1.5M",
        "prime_margin": "10-15%",
        "typical_profit": "$40K-$300K per contract",
        "special_note": "Federal facilities = large contracts"
    },
    "construction_renovation": {
        "small_contracts": "$100K-$500K",
        "medium_contracts": "$500K-$2M",
        "large_contracts": "$2M-$5M+",
        "annual_potential": "$500K-$3M",
        "prime_margin": "10-20%",
        "typical_profit": "$50K-$600K per project",
        "special_note": "Largest contracts, but need strong past performance"
    },
    "moving_relocation": {
        "small_contracts": "$50K-$150K",
        "medium_contracts": "$150K-$300K",
        "large_contracts": "$300K-$500K+",
        "annual_potential": "$100K-$400K",
        "prime_margin": "15-25%",
        "typical_profit": "$15K-$125K per contract",
        "special_note": "Project-based, can stack multiple projects"
    },
    "event_services": {
        "small_contracts": "$25K-$100K",
        "medium_contracts": "$100K-$200K",
        "large_contracts": "$200K-$250K+",
        "annual_potential": "$100K-$300K",
        "prime_margin": "15-25%",
        "typical_profit": "$15K-$75K per contract",
        "special_note": "Recurring annual events, easy wins"
    }
}

# Top Direct Sources for Service Contracts
SERVICE_CONTRACT_SOURCES = {
    "sam_gov": {
        "name": "SAM.gov",
        "url": "https://sam.gov/search",
        "focus": "Federal service contracts",
        "search_frequency": "Daily",
        "expected_finds": "50-100 service contracts daily",
        "notes": "Primary source. Use WOSB filter!"
    },
    "state_procurement": {
        "name": "State Procurement Portals",
        "examples": [
            {"state": "Michigan", "url": "https://www.michigan.gov/buy", "focus": "State facilities"},
            {"state": "Illinois", "url": "https://www2.illinois.gov/cms/business/sell/Pages/default.aspx"},
            {"state": "Ohio", "url": "https://procure.ohio.gov/"},
        ],
        "search_frequency": "Weekly",
        "expected_finds": "10-20 per state weekly"
    },
    "county_municipalities": {
        "name": "County & Municipal Portals",
        "examples": [
            {"name": "Wayne County", "url": "https://www.waynecounty.com/departments/procurement.aspx"},
            {"name": "Oakland County", "url": "https://www.oakgov.com/advantageoakland/procurement/"},
            {"name": "City of Detroit", "url": "https://detroitmi.gov/departments/office-contracting-and-procurement"},
        ],
        "search_frequency": "Bi-weekly",
        "expected_finds": "5-10 per jurisdiction monthly"
    },
    "school_districts": {
        "name": "School Districts",
        "focus": "Janitorial, landscaping, maintenance, IT, security",
        "examples": [
            {"name": "Detroit Public Schools", "note": "Large facilities"},
            {"name": "Wayne RESA", "note": "Regional contracts"},
        ],
        "search_frequency": "Monthly",
        "expected_finds": "3-5 monthly",
        "notes": "Schools need janitorial, landscaping, IT, security year-round"
    },
    "universities": {
        "name": "Public Universities",
        "focus": "All service categories",
        "examples": [
            {"name": "University of Michigan", "note": "Massive campus"},
            {"name": "Wayne State University"},
            {"name": "Michigan State University"},
        ],
        "search_frequency": "Monthly",
        "expected_finds": "2-5 monthly",
        "notes": "Large recurring contracts, prefer local vendors"
    },
    "bid_aggregators": {
        "name": "Bid Aggregator Sites",
        "examples": [
            {"name": "BidNet", "url": "https://www.bidnet.com/"},
            {"name": "DemandStar", "url": "https://www.demandstar.com/"},
            {"name": "GovSpend", "url": "https://www.govspend.com/"},
        ],
        "search_frequency": "Weekly",
        "expected_finds": "20-40 weekly"
    }
}

# Qualification Criteria
QUALIFICATION_CRITERIA = {
    "start_small": {
        "recommended_first_contracts": [
            "Janitorial < $150K (no bond required)",
            "Landscaping < $150K (seasonal, no bond)",
            "Event services < $100K (single events)",
            "Moving services < $100K (small projects)"
        ],
        "why": "Build track record, learn prime contractor role, low bonding requirements"
    },
    "insurance_ready": {
        "you_have": [
            "General Liability ✅",
            "E&O Insurance ✅",
            "Business Insurance ✅"
        ],
        "sub_provides": [
            "Trade-specific insurance",
            "Workers compensation",
            "Professional licenses",
            "Equipment insurance"
        ],
        "ready_for": "Contracts up to $500K immediately"
    },
    "red_flags": [
        "Performance bond > $500K (may need partner for first few)",
        "Requires extensive past performance you don't have yet",
        "Security clearances required (time-consuming)",
        "Prevailing wage + certified payroll (adds complexity)",
        "Start small, build up to these"
    ],
    "green_lights": [
        "✅ WOSB set-aside (your advantage!)",
        "✅ Small Business set-aside",
        "✅ Local preference",
        "✅ Multiple award possible (easier to win)",
        "✅ Contract value under $150K (often no bond)",
        "✅ Michigan-based (local advantage)"
    ]
}

# Helper Functions
def get_all_keywords():
    """Get all service contract keywords across categories"""
    all_keywords = []
    for category_data in SERVICE_CONTRACTS_CATEGORIES.values():
        all_keywords.extend(category_data['primary_keywords'])
        all_keywords.extend(category_data['secondary_keywords'])
    return list(set(all_keywords))

def get_todays_searches(day_name=None):
    """Get recommended searches for today"""
    import datetime
    if not day_name:
        day_name = datetime.datetime.now().strftime("%A").lower()
    
    return WEEKLY_SEARCH_SCHEDULE.get(day_name, {})

def get_category_by_keyword(keyword):
    """Find which category a keyword belongs to"""
    keyword_lower = keyword.lower()
    for category_id, data in SERVICE_CONTRACTS_CATEGORIES.items():
        all_cat_keywords = data['primary_keywords'] + data['secondary_keywords']
        if any(keyword_lower in kw.lower() for kw in all_cat_keywords):
            return category_id, data
    return None, None

def qualify_opportunity(opportunity_data):
    """Basic qualification check for service opportunities"""
    qualifications = {
        "qualified": False,
        "reasons": [],
        "risk_level": "unknown",
        "recommended_action": ""
    }
    
    value = opportunity_data.get('estimated_value', 0)
    set_aside = opportunity_data.get('set_aside', '').lower()
    location = opportunity_data.get('location', '').lower()
    
    # Check set-aside advantage
    if 'wosb' in set_aside or 'woman' in set_aside:
        qualifications['reasons'].append("✅ WOSB set-aside - MAJOR ADVANTAGE")
        qualifications['qualified'] = True
    
    # Check contract size
    if value < 150000:
        qualifications['reasons'].append("✅ Under $150K - likely no bond required")
        qualifications['risk_level'] = "low"
        qualifications['qualified'] = True
    elif value < 500000:
        qualifications['reasons'].append("⚠️ Under $500K - small bond may be needed")
        qualifications['risk_level'] = "medium"
    else:
        qualifications['reasons'].append("⚠️ Over $500K - performance bond likely required")
        qualifications['risk_level'] = "high"
    
    # Check location
    if 'michigan' in location or 'detroit' in location:
        qualifications['reasons'].append("✅ Michigan-based - LOCAL ADVANTAGE")
        qualifications['qualified'] = True
    
    # Recommendation
    if qualifications['qualified']:
        qualifications['recommended_action'] = "PURSUE - Good fit for your capabilities"
    else:
        qualifications['recommended_action'] = "REVIEW - May need teaming partner"
    
    return qualifications

def calculate_potential_profit(contract_value, category_id, prime_margin_override=None):
    """Calculate potential profit for a service contract"""
    category_data = SERVICE_CONTRACTS_CATEGORIES.get(category_id, {})
    
    if prime_margin_override:
        margin = prime_margin_override
    else:
        margin_str = category_data.get('prime_margin', '15%')
        # Parse margin (e.g., "15-20%" -> use low end 15%)
        margin = float(margin_str.split('-')[0].replace('%', '')) / 100
    
    gross_profit = contract_value * margin
    
    # Estimate costs
    insurance_bond = contract_value * 0.02  # ~2%
    admin_overhead = contract_value * 0.03   # ~3%
    
    net_profit = gross_profit - insurance_bond - admin_overhead
    
    return {
        "contract_value": contract_value,
        "gross_margin": margin * 100,
        "gross_profit": gross_profit,
        "insurance_bond": insurance_bond,
        "admin_overhead": admin_overhead,
        "net_profit": net_profit,
        "net_margin": (net_profit / contract_value) * 100
    }
