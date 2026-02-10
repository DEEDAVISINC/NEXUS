"""
Transportation & Logistics Keywords Configuration for NEXUS
Integrated keyword system for finding airport, port, cargo, courier, and marine opportunities
"""

# Transportation & Logistics Categories and Keywords
TRANSPORTATION_LOGISTICS_KEYWORDS = {
    "airport_aviation": {
        "display_name": "✈️ Airport & Aviation",
        "description": "Airport operations, aviation supplies, ground equipment",
        "primary_keywords": [
            "airport supplies",
            "aviation supplies",
            "airfield supplies",
            "runway supplies",
            "ground support equipment",
            "aircraft servicing supplies",
            "airport operations",
            "airport maintenance supplies",
            "terminal supplies",
            "aviation safety equipment"
        ],
        "secondary_keywords": [
            "airfield lighting",
            "runway marking materials",
            "aviation fuel equipment",
            "aviation ground equipment",
            "deicing equipment",
            "hangar supplies",
            "aircraft cleaning supplies",
            "baggage handling supplies",
            "airport facility supplies"
        ],
        "sam_gov_searches": [
            '"airport supplies" WOSB',
            '"aviation supplies" small business',
            '"airfield supplies" woman owned',
            '"ground support equipment" EDWOSB',
            '"airport operations" WOSB',
            '"aviation safety" small business',
            '"terminal supplies" EDWOSB',
            '"deicing equipment" WOSB'
        ],
        "estimated_contract_range": "$30K-$500K",
        "typical_duration": "Annual or multi-year",
        "sourcing_difficulty": "Medium",
        "key_suppliers": ["Grainger", "Fastenal", "Aviation specialty distributors"]
    },
    
    "port_marine": {
        "display_name": "🚢 Port & Marine",
        "description": "Port operations, marine supplies, dock equipment",
        "primary_keywords": [
            "port supplies",
            "marine supplies",
            "maritime supplies",
            "dock equipment",
            "harbor supplies",
            "port operations equipment",
            "marine safety equipment",
            "vessel supplies",
            "ship chandlery",
            "marine hardware"
        ],
        "secondary_keywords": [
            "dock hardware",
            "mooring equipment",
            "fenders",
            "marine rope",
            "dock lines",
            "nautical supplies",
            "port facility supplies",
            "marine maintenance supplies",
            "maritime safety equipment",
            "navigation supplies",
            "buoys",
            "channel markers"
        ],
        "sam_gov_searches": [
            '"marine supplies" WOSB',
            '"port supplies" EDWOSB',
            '"maritime supplies" small business',
            '"dock equipment" woman owned',
            '"harbor supplies" WOSB',
            '"vessel supplies" small business',
            '"ship chandlery" EDWOSB',
            '"marine safety" WOSB'
        ],
        "estimated_contract_range": "$40K-$400K",
        "typical_duration": "Annual contracts",
        "sourcing_difficulty": "Medium-High",
        "key_suppliers": ["West Marine Commercial", "Defender Industries", "Fisheries Supply"]
    },
    
    "cargo_freight": {
        "display_name": "📦 Cargo & Freight",
        "description": "Cargo handling, warehouse operations, freight supplies",
        "primary_keywords": [
            "cargo handling equipment",
            "freight supplies",
            "warehouse equipment",
            "material handling equipment",
            "warehouse supplies",
            "logistics equipment",
            "cargo securing",
            "freight containers",
            "packaging materials",
            "shipping supplies"
        ],
        "secondary_keywords": [
            "pallet jacks",
            "pallet wrap",
            "stretch film",
            "shrink wrap",
            "strapping",
            "cargo straps",
            "tie-down straps",
            "load securing",
            "cargo nets",
            "shipping boxes",
            "corrugated boxes"
        ],
        "sam_gov_searches": [
            '"cargo handling equipment" WOSB',
            '"warehouse supplies" small business',
            '"material handling" EDWOSB',
            '"freight supplies" woman owned',
            '"logistics equipment" WOSB',
            '"packaging materials" small business',
            '"warehouse equipment" EDWOSB'
        ],
        "estimated_contract_range": "$25K-$300K",
        "typical_duration": "Annual contracts",
        "sourcing_difficulty": "Easy-Medium",
        "key_suppliers": ["Uline", "Grainger", "Fastenal"]
    },
    
    "courier_postal": {
        "display_name": "📬 Courier & Postal",
        "description": "USPS, courier services, mailing supplies",
        "primary_keywords": [
            "postal supplies",
            "courier supplies",
            "delivery supplies",
            "mailing supplies",
            "shipping envelopes",
            "mailroom supplies",
            "mail processing",
            "USPS supplies",
            "postal operations"
        ],
        "secondary_keywords": [
            "padded envelopes",
            "bubble mailers",
            "shipping boxes",
            "packaging tape",
            "shipping labels",
            "label printers",
            "postal scales",
            "mail carts",
            "delivery vehicle supplies",
            "parcel handling equipment"
        ],
        "sam_gov_searches": [
            '"postal supplies" WOSB',
            '"mailing supplies" small business',
            '"courier supplies" EDWOSB',
            '"shipping envelopes" woman owned',
            '"mailroom supplies" WOSB',
            '"delivery supplies" small business',
            '"USPS" supplies WOSB',
            '"mail processing" equipment small business'
        ],
        "estimated_contract_range": "$20K-$200K",
        "typical_duration": "Annual or multi-facility",
        "sourcing_difficulty": "Easy",
        "key_suppliers": ["Uline", "Grainger", "Standard shipping suppliers"],
        "special_note": "USPS is HUGE opportunity - 31,000+ facilities nationwide!"
    },
    
    "transit_transportation": {
        "display_name": "🚌 Transit & Transportation",
        "description": "Transit authorities, bus operations, transportation facilities",
        "primary_keywords": [
            "transit supplies",
            "transportation supplies",
            "bus supplies",
            "transit operations",
            "transit facility supplies",
            "vehicle maintenance supplies",
            "fleet operations",
            "passenger transport supplies"
        ],
        "secondary_keywords": [
            "bus terminal supplies",
            "dispatch supplies",
            "driver supplies",
            "vehicle safety equipment",
            "traffic control equipment",
            "transportation safety supplies",
            "fare collection supplies",
            "transit signage"
        ],
        "sam_gov_searches": [
            '"transit supplies" WOSB',
            '"transportation supplies" small business',
            '"bus supplies" EDWOSB',
            '"transit operations" woman owned',
            '"fleet operations" WOSB',
            '"transit facility" small business'
        ],
        "estimated_contract_range": "$30K-$250K",
        "typical_duration": "Annual contracts",
        "sourcing_difficulty": "Easy-Medium",
        "key_suppliers": ["Grainger", "Fastenal", "Fleet specialty suppliers"]
    },
    
    "nemt_healthcare_transport": {
        "display_name": "🚑 NEMT & Healthcare Transportation",
        "description": "Non-Emergency Medical Transportation services (via Uber Health)",
        "primary_keywords": [
            "NEMT",
            "non-emergency medical transportation",
            "medical transportation",
            "patient transportation",
            "healthcare transportation",
            "ambulatory transportation",
            "medical transport services",
            "patient transport services",
            "Medicaid transportation",
            "Medicare transportation"
        ],
        "secondary_keywords": [
            "wheelchair transportation",
            "stretcher transportation",
            "dialysis transportation",
            "chemotherapy transportation",
            "medical appointment transportation",
            "hospital discharge transportation",
            "clinic transportation",
            "nursing home transportation",
            "assisted living transportation",
            "behavioral health transportation",
            "pharmacy transportation",
            "veteran medical transportation"
        ],
        "sam_gov_searches": [
            '"NEMT" WOSB',
            '"non-emergency medical transportation" small business',
            '"medical transportation services" EDWOSB',
            '"patient transportation" woman owned',
            '"healthcare transportation" WOSB',
            '"Medicaid transportation" small business',
            '"ambulatory transportation" EDWOSB',
            '"medical transport services" WOSB'
        ],
        "estimated_contract_range": "$50K-$2M",
        "typical_duration": "Annual or multi-year (1-5 years)",
        "sourcing_difficulty": "Medium (requires Uber Health partnership)",
        "key_suppliers": ["Uber Health (fulfillment partner)"],
        "special_note": "HIGH VALUE! NEMT contracts often $500K-$2M annually. Medicaid, Medicare, hospitals, healthcare systems. Perfect for WOSB set-asides!"
    }
}

# Direct Source URLs for Transportation/Logistics
TRANSPORTATION_LOGISTICS_SOURCES = {
    "airports": {
        "display_name": "Airports",
        "sources": [
            {
                "name": "Detroit Metro Airport (DTW)",
                "url": "https://www.metroairport.com/business/procurement",
                "location": "Detroit, MI",
                "advantage": "LOCAL - Michigan advantage",
                "check_frequency": "Weekly"
            },
            {
                "name": "Chicago O'Hare (ORD)",
                "url": "https://www.flychicago.com/business/contracts-and-procurement",
                "location": "Chicago, IL",
                "advantage": "Major hub - large contracts",
                "check_frequency": "Weekly"
            },
            {
                "name": "DFW International",
                "url": "https://www.dfwairport.com/business/procurement/",
                "location": "Dallas/Fort Worth, TX",
                "advantage": "Texas location - CPS relationship",
                "check_frequency": "Bi-weekly"
            },
            {
                "name": "Gerald R. Ford International",
                "url": "https://www.grr.org/corporate/procurement",
                "location": "Grand Rapids, MI",
                "advantage": "LOCAL - Michigan, smaller contracts",
                "check_frequency": "Weekly"
            }
        ]
    },
    "ports": {
        "display_name": "Ports & Marine",
        "sources": [
            {
                "name": "Detroit-Wayne County Port Authority",
                "url": "https://www.portdetroit.com/",
                "location": "Detroit, MI",
                "advantage": "LOCAL - Michigan advantage",
                "check_frequency": "Weekly"
            },
            {
                "name": "Port of Toledo",
                "url": "https://www.toledoportauthority.org/",
                "location": "Toledo, OH",
                "advantage": "Close proximity to Michigan",
                "check_frequency": "Bi-weekly"
            },
            {
                "name": "Port of Chicago",
                "url": "https://www.portofchicago.com/",
                "location": "Chicago, IL",
                "advantage": "Great Lakes operations",
                "check_frequency": "Bi-weekly"
            }
        ]
    },
    "transit": {
        "display_name": "Transit Authorities",
        "sources": [
            {
                "name": "SMART Bus",
                "url": "https://www.smartbus.org/About/Procurement",
                "location": "Detroit Metro, MI",
                "advantage": "LOCAL - Michigan advantage",
                "check_frequency": "Weekly"
            },
            {
                "name": "TheRide (Ann Arbor)",
                "url": "https://www.theride.org/about/procurement",
                "location": "Ann Arbor, MI",
                "advantage": "LOCAL - Michigan advantage",
                "check_frequency": "Weekly"
            },
            {
                "name": "Chicago Transit Authority",
                "url": "https://www.transitchicago.com/business/",
                "location": "Chicago, IL",
                "advantage": "Large system - high volume",
                "check_frequency": "Bi-weekly"
            }
        ]
    }
}

# Weekly Search Schedule
WEEKLY_SEARCH_SCHEDULE = {
    "monday": {
        "focus": "NEMT & Healthcare Transportation",
        "searches": [
            '"NEMT" WOSB',
            '"non-emergency medical transportation" small business',
            '"medical transportation services" EDWOSB'
        ],
        "direct_sites": ["SAM.gov - Medicaid/Medicare", "State health departments"],
        "special_note": "HIGH VALUE WEEK! NEMT contracts $500K-$2M+"
    },
    "tuesday": {
        "focus": "Airport & Aviation",
        "searches": [
            '"airport supplies" WOSB',
            '"aviation supplies" small business',
            '"terminal supplies" EDWOSB'
        ],
        "direct_sites": ["Detroit Metro Airport", "Gerald R. Ford Airport"]
    },
    "wednesday": {
        "focus": "Port & Marine",
        "searches": [
            '"marine supplies" WOSB',
            '"port supplies" EDWOSB',
            '"maritime supplies" small business'
        ],
        "direct_sites": ["Detroit Port Authority", "Port of Toledo"]
    },
    "thursday": {
        "focus": "Courier & Postal + Cargo",
        "searches": [
            '"postal supplies" WOSB',
            '"USPS" supplies small business',
            '"cargo handling" EDWOSB'
        ],
        "direct_sites": ["SAM.gov - USPS and warehouses"]
    },
    "friday": {
        "focus": "Transit & Transportation",
        "searches": [
            '"transit supplies" WOSB',
            '"transportation supplies" small business',
            '"bus supplies" EDWOSB'
        ],
        "direct_sites": ["SMART Bus", "TheRide", "CTA"]
    }
}

# Quick qualification checklist
QUALIFICATION_CRITERIA = {
    "can_source": {
        "question": "Can we source these products?",
        "easy_sources": ["Grainger", "Uline", "Fastenal", "Marine distributors"],
        "weight": 5
    },
    "delivery_location": {
        "question": "Is delivery location advantageous?",
        "preferred": ["Michigan", "Great Lakes", "Illinois", "Texas"],
        "weight": 4
    },
    "contract_value": {
        "question": "Is contract value in sweet spot?",
        "range": "$10K-$500K",
        "weight": 4
    },
    "timeline": {
        "question": "Do we have enough time to prepare?",
        "minimum_days": 10,
        "weight": 3
    },
    "set_aside": {
        "question": "Is there a set-aside advantage?",
        "preferred": ["WOSB", "EDWOSB", "Small Business"],
        "weight": 5
    }
}

# Revenue potential by category
REVENUE_POTENTIAL = {
    "nemt_healthcare_transport": {
        "small_contracts": "$50K-$200K",
        "medium_contracts": "$200K-$800K",
        "large_contracts": "$800K-$2M+",
        "annual_potential": "$500K-$2M",
        "special_note": "HIGHEST VALUE CATEGORY! Medicaid/Medicare contracts are massive. Multi-year terms common. Perfect for WOSB set-asides!"
    },
    "airport_aviation": {
        "small_contracts": "$30K-$100K",
        "medium_contracts": "$100K-$300K",
        "large_contracts": "$300K-$500K+",
        "annual_potential": "$100K-$300K"
    },
    "port_marine": {
        "small_contracts": "$40K-$100K",
        "medium_contracts": "$100K-$250K",
        "large_contracts": "$250K-$400K+",
        "annual_potential": "$80K-$250K"
    },
    "cargo_freight": {
        "small_contracts": "$25K-$75K",
        "medium_contracts": "$75K-$200K",
        "large_contracts": "$200K-$300K+",
        "annual_potential": "$60K-$200K"
    },
    "courier_postal": {
        "small_contracts": "$20K-$50K",
        "medium_contracts": "$50K-$150K",
        "large_contracts": "$150K-$200K+",
        "annual_potential": "$100K-$300K",
        "special_note": "USPS has massive potential - multi-facility contracts"
    },
    "transit_transportation": {
        "small_contracts": "$30K-$80K",
        "medium_contracts": "$80K-$180K",
        "large_contracts": "$180K-$250K+",
        "annual_potential": "$70K-$200K"
    }
}

def get_all_keywords():
    """Get all keywords across all categories"""
    all_keywords = []
    for category in TRANSPORTATION_LOGISTICS_KEYWORDS.values():
        all_keywords.extend(category["primary_keywords"])
        all_keywords.extend(category["secondary_keywords"])
    return list(set(all_keywords))

def get_category_keywords(category_key):
    """Get keywords for a specific category"""
    if category_key in TRANSPORTATION_LOGISTICS_KEYWORDS:
        cat = TRANSPORTATION_LOGISTICS_KEYWORDS[category_key]
        return cat["primary_keywords"] + cat["secondary_keywords"]
    return []

def get_todays_searches():
    """Get recommended searches for today based on day of week"""
    import datetime
    weekday = datetime.datetime.now().strftime('%A').lower()
    
    if weekday in WEEKLY_SEARCH_SCHEDULE:
        return WEEKLY_SEARCH_SCHEDULE[weekday]
    
    # Default to Monday if weekend
    return WEEKLY_SEARCH_SCHEDULE["monday"]

def qualify_opportunity(opportunity_data):
    """
    Qualify a transportation/logistics opportunity
    Returns score out of 21 points (5 criteria × weights)
    """
    score = 0
    reasons = []
    
    # Can source (5 points)
    if any(supplier.lower() in str(opportunity_data.get('description', '')).lower() 
           for supplier in ['standard', 'industrial', 'packaging', 'marine']):
        score += 5
        reasons.append("✅ Easy to source")
    
    # Location (4 points)
    location = opportunity_data.get('state', '').upper()
    if location in ['MI', 'MICHIGAN', 'IL', 'ILLINOIS', 'TX', 'TEXAS', 'OH', 'OHIO']:
        score += 4
        reasons.append(f"✅ Advantageous location ({location})")
    
    # Contract value (4 points)
    value = opportunity_data.get('value', 0)
    if 10000 <= value <= 500000:
        score += 4
        reasons.append(f"✅ Good value range (${value:,})")
    
    # Timeline (3 points)
    import datetime
    due_date = opportunity_data.get('due_date')
    if due_date:
        try:
            due = datetime.datetime.fromisoformat(str(due_date))
            days_remaining = (due - datetime.datetime.now()).days
            if days_remaining >= 10:
                score += 3
                reasons.append(f"✅ Good timeline ({days_remaining} days)")
        except:
            pass
    
    # Set-aside (5 points)
    set_aside = opportunity_data.get('set_aside_type', '').upper()
    if any(sa in set_aside for sa in ['WOSB', 'EDWOSB', 'WOMAN', 'SMALL']):
        score += 5
        reasons.append(f"✅ Set-aside advantage ({set_aside})")
    
    return {
        "score": score,
        "max_score": 21,
        "percentage": round((score / 21) * 100),
        "recommendation": "BID THIS!" if score >= 17 else "Strong Maybe" if score >= 13 else "Review More" if score >= 9 else "Skip",
        "reasons": reasons
    }

if __name__ == "__main__":
    # Test/example usage
    print("Transportation & Logistics Keyword System for NEXUS")
    print("=" * 60)
    print(f"\nTotal Categories: {len(TRANSPORTATION_LOGISTICS_KEYWORDS)}")
    print(f"Total Keywords: {len(get_all_keywords())}")
    print(f"\nToday's Search Focus: {get_todays_searches()['focus']}")
    print(f"Searches to run: {len(get_todays_searches()['searches'])}")
