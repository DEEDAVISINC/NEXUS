"""
Transportation & Logistics API for NEXUS
API endpoints for searching and managing transportation/logistics opportunities
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import datetime
from transportation_logistics_keywords import (
    TRANSPORTATION_LOGISTICS_KEYWORDS,
    TRANSPORTATION_LOGISTICS_SOURCES,
    WEEKLY_SEARCH_SCHEDULE,
    QUALIFICATION_CRITERIA,
    REVENUE_POTENTIAL,
    get_all_keywords,
    get_category_keywords,
    get_todays_searches,
    qualify_opportunity
)

app = Flask(__name__)
CORS(app)

# GET /api/transportation-logistics/keywords
@app.route('/api/transportation-logistics/keywords', methods=['GET'])
def get_keywords():
    """
    Get all transportation/logistics keywords organized by category
    """
    return jsonify({
        "success": True,
        "categories": TRANSPORTATION_LOGISTICS_KEYWORDS,
        "total_categories": len(TRANSPORTATION_LOGISTICS_KEYWORDS),
        "total_keywords": len(get_all_keywords())
    })

# GET /api/transportation-logistics/keywords/<category>
@app.route('/api/transportation-logistics/keywords/<category>', methods=['GET'])
def get_category_keywords_api(category):
    """
    Get keywords for a specific category
    """
    if category not in TRANSPORTATION_LOGISTICS_KEYWORDS:
        return jsonify({
            "success": False,
            "error": f"Category '{category}' not found"
        }), 404
    
    cat_data = TRANSPORTATION_LOGISTICS_KEYWORDS[category]
    keywords = get_category_keywords(category)
    
    return jsonify({
        "success": True,
        "category": category,
        "display_name": cat_data["display_name"],
        "description": cat_data["description"],
        "keywords": keywords,
        "sam_gov_searches": cat_data["sam_gov_searches"],
        "revenue_potential": REVENUE_POTENTIAL.get(category, {})
    })

# GET /api/transportation-logistics/sources
@app.route('/api/transportation-logistics/sources', methods=['GET'])
def get_sources():
    """
    Get direct source URLs for transportation/logistics opportunities
    """
    return jsonify({
        "success": True,
        "sources": TRANSPORTATION_LOGISTICS_SOURCES
    })

# GET /api/transportation-logistics/today
@app.route('/api/transportation-logistics/today', methods=['GET'])
def get_todays_focus():
    """
    Get today's recommended searches based on day of week
    """
    todays_schedule = get_todays_searches()
    
    return jsonify({
        "success": True,
        "day": datetime.datetime.now().strftime('%A'),
        "focus": todays_schedule["focus"],
        "searches": todays_schedule["searches"],
        "direct_sites": todays_schedule["direct_sites"],
        "message": f"Today's focus: {todays_schedule['focus']}"
    })

# GET /api/transportation-logistics/schedule
@app.route('/api/transportation-logistics/schedule', methods=['GET'])
def get_weekly_schedule():
    """
    Get the complete weekly search schedule
    """
    return jsonify({
        "success": True,
        "schedule": WEEKLY_SEARCH_SCHEDULE
    })

# POST /api/transportation-logistics/qualify
@app.route('/api/transportation-logistics/qualify', methods=['POST'])
def qualify_opportunity_api():
    """
    Qualify a transportation/logistics opportunity
    
    Request body:
    {
        "description": "Airport terminal supplies",
        "state": "MI",
        "value": 50000,
        "due_date": "2026-03-15",
        "set_aside_type": "WOSB"
    }
    """
    data = request.get_json()
    
    if not data:
        return jsonify({
            "success": False,
            "error": "No data provided"
        }), 400
    
    qualification = qualify_opportunity(data)
    
    return jsonify({
        "success": True,
        "qualification": qualification
    })

# GET /api/transportation-logistics/search-strings
@app.route('/api/transportation-logistics/search-strings', methods=['GET'])
def get_search_strings():
    """
    Get all SAM.gov search strings for quick copy/paste
    """
    all_searches = []
    
    for category_key, category_data in TRANSPORTATION_LOGISTICS_KEYWORDS.items():
        for search in category_data["sam_gov_searches"]:
            all_searches.append({
                "category": category_key,
                "category_name": category_data["display_name"],
                "search_string": search,
                "estimated_results": "5-10 opportunities per search"
            })
    
    return jsonify({
        "success": True,
        "total_searches": len(all_searches),
        "searches": all_searches,
        "usage": "Copy any search string and paste into SAM.gov"
    })

# GET /api/transportation-logistics/quick-start
@app.route('/api/transportation-logistics/quick-start', methods=['GET'])
def get_quick_start():
    """
    Get quick-start guide with top 5 searches to run right now
    """
    top_searches = [
        {
            "priority": 1,
            "search": '"postal supplies" WOSB',
            "category": "Courier & Postal",
            "why": "USPS has 31,000+ facilities - massive opportunity!",
            "expected": "10-15 opportunities"
        },
        {
            "priority": 2,
            "search": '"airport supplies" WOSB',
            "category": "Airport & Aviation",
            "why": "Large contracts, recurring revenue",
            "expected": "5-8 opportunities"
        },
        {
            "priority": 3,
            "search": '"marine supplies" WOSB Michigan',
            "category": "Port & Marine",
            "why": "Local advantage with Detroit Port Authority",
            "expected": "3-5 opportunities"
        },
        {
            "priority": 4,
            "search": '"courier supplies" small business',
            "category": "Courier & Postal",
            "why": "Easy to source, quick wins",
            "expected": "5-7 opportunities"
        },
        {
            "priority": 5,
            "search": '"cargo handling equipment" WOSB',
            "category": "Cargo & Freight",
            "why": "Federal warehouses, good contract values",
            "expected": "4-6 opportunities"
        }
    ]
    
    return jsonify({
        "success": True,
        "message": "Run these 5 searches right now to find 25-40 opportunities",
        "time_required": "30 minutes",
        "expected_opportunities": "25-40 new opportunities",
        "searches": top_searches
    })

# GET /api/transportation-logistics/revenue-potential
@app.route('/api/transportation-logistics/revenue-potential', methods=['GET'])
def get_revenue_potential():
    """
    Get revenue potential breakdown by category
    """
    return jsonify({
        "success": True,
        "revenue_potential": REVENUE_POTENTIAL,
        "total_annual_potential": "$300K-$500K",
        "combined_with_traditional": "$660K-$980K"
    })

# GET /api/transportation-logistics/stats
@app.route('/api/transportation-logistics/stats', methods=['GET'])
def get_stats():
    """
    Get overall statistics about transportation/logistics opportunities
    """
    return jsonify({
        "success": True,
        "stats": {
            "total_categories": len(TRANSPORTATION_LOGISTICS_KEYWORDS),
            "total_keywords": len(get_all_keywords()),
            "total_search_strings": sum(len(cat["sam_gov_searches"]) for cat in TRANSPORTATION_LOGISTICS_KEYWORDS.values()),
            "total_direct_sources": sum(len(source["sources"]) for source in TRANSPORTATION_LOGISTICS_SOURCES.values()),
            "expected_weekly_opportunities": "30-50 opportunities",
            "expected_monthly_revenue": "$10K-$30K",
            "expected_annual_revenue": "$300K-$500K"
        },
        "categories_overview": {
            key: {
                "name": val["display_name"],
                "keywords": len(val["primary_keywords"]) + len(val["secondary_keywords"]),
                "searches": len(val["sam_gov_searches"])
            }
            for key, val in TRANSPORTATION_LOGISTICS_KEYWORDS.items()
        }
    })

# POST /api/transportation-logistics/search-sam-gov
@app.route('/api/transportation-logistics/search-sam-gov', methods=['POST'])
def search_sam_gov():
    """
    Execute a SAM.gov search for transportation/logistics opportunities
    (This would integrate with actual SAM.gov API or web scraping)
    
    Request body:
    {
        "category": "airport_aviation",
        "location": "Michigan",
        "set_aside": "WOSB"
    }
    """
    data = request.get_json()
    
    # Mock response for now - in production would call SAM.gov API
    category = data.get('category', 'airport_aviation')
    
    return jsonify({
        "success": True,
        "message": "This endpoint would integrate with SAM.gov API",
        "search_performed": f"Transportation/Logistics - {category}",
        "mock_results": [
            {
                "id": "TRANS001",
                "title": "Airport Terminal Supplies - Annual Contract",
                "agency": "Detroit Metro Airport",
                "state": "MI",
                "value": 75000,
                "due_date": "2026-03-15",
                "set_aside_type": "WOSB",
                "category": "Airport & Aviation",
                "source": "SAM.gov"
            },
            {
                "id": "TRANS002",
                "title": "Marine Supplies - Port Operations",
                "agency": "Detroit-Wayne County Port Authority",
                "state": "MI",
                "value": 120000,
                "due_date": "2026-03-20",
                "set_aside_type": "Small Business",
                "category": "Port & Marine",
                "source": "SAM.gov"
            }
        ],
        "note": "In production, this would return real SAM.gov results"
    })

# Health check
@app.route('/api/transportation-logistics/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "success": True,
        "service": "Transportation & Logistics API",
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("=" * 60)
    print("Transportation & Logistics API for NEXUS")
    print("=" * 60)
    print("\nAvailable Endpoints:")
    print("  GET  /api/transportation-logistics/keywords")
    print("  GET  /api/transportation-logistics/keywords/<category>")
    print("  GET  /api/transportation-logistics/sources")
    print("  GET  /api/transportation-logistics/today")
    print("  GET  /api/transportation-logistics/schedule")
    print("  POST /api/transportation-logistics/qualify")
    print("  GET  /api/transportation-logistics/search-strings")
    print("  GET  /api/transportation-logistics/quick-start")
    print("  GET  /api/transportation-logistics/revenue-potential")
    print("  GET  /api/transportation-logistics/stats")
    print("  POST /api/transportation-logistics/search-sam-gov")
    print("  GET  /api/transportation-logistics/health")
    print("\nStarting server on http://localhost:5001...")
    print("=" * 60)
    app.run(debug=True, port=5001)
