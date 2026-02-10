# 🔬 NEXUS DETAILED SYSTEM FLOW

**Comprehensive step-by-step breakdown of every action, system interaction, and data flow**

---

## 📊 TABLE OF CONTENTS

1. [Phase 1: Opportunity Discovery (Mining)](#phase-1-opportunity-discovery)
2. [Phase 2A: Federal Forecasting (Proactive)](#phase-2a-federal-forecasting)
3. [Phase 2B: Forecast Capability Statement & Outreach](#phase-2b-forecast-outreach)
4. [Phase 3: Bid Preparation & Submission](#phase-3-bid-preparation)
5. [Phase 3B: Closed Opportunity Outreach (Reactive)](#phase-3b-reactive-outreach)
6. [Phase 4: Contract Award & Setup](#phase-4-contract-award)
7. [Phase 5: Fulfillment & Delivery](#phase-5-fulfillment)
8. [Phase 6: Invoicing & Payment](#phase-6-invoicing)
9. [Phase 7: Financial Tracking & Learning](#phase-7-financial-tracking)

---

## PHASE 1: OPPORTUNITY DISCOVERY (Mining)

### **Step 1.1: Automated Daily Mining Trigger**

**Time:** Every day at 6:00 AM (configured in cron)

**Cron Job:**
```bash
0 6 * * * cd "/Users/deedavis/NEXUS BACKEND" && /usr/local/bin/python3 -c "from nexus_backend import GPSSOpportunityMiningAgent; agent = GPSSOpportunityMiningAgent(); agent.mine_all_sources()" >> mining.log 2>&1
```

**What Happens:**
1. Cron daemon executes Python script
2. Loads environment variables from `.env`
3. Initializes `GPSSOpportunityMiningAgent`
4. Connects to Airtable API (validates `AIRTABLE_API_KEY`)

---

### **Step 1.2: Mining SAM.gov (Federal Opportunities)**

**Module:** `nexus_backend.py` → `GPSSOpportunityMiningAgent._mine_sam_gov()`

**Detailed Process:**

**1.2.1: API Connection**
```python
# Connect to SAM.gov API
url = "https://api.sam.gov/opportunities/v2/search"
headers = {
    'X-Api-Key': os.environ['SAM_GOV_API_KEY'],
    'Content-Type': 'application/json'
}
```

**1.2.2: Search Parameters**
```python
params = {
    'postedFrom': (datetime.now() - timedelta(days=7)).strftime('%m/%d/%Y'),
    'postedTo': datetime.now().strftime('%m/%d/%Y'),
    'ptype': 'o',  # Opportunities
    'limit': 1000
}
```

**1.2.3: API Request & Response**
```python
response = requests.get(url, headers=headers, params=params)
data = response.json()
opportunities = data['opportunitiesData']
```

**1.2.4: Parse Each Opportunity**

For each opportunity in response:

```python
opportunity = {
    'solicitation_number': opp['solicitationNumber'],
    'title': opp['title'],
    'agency': opp['fullParentPathName'],
    'office': opp['officeAddress']['city'],
    'posted_date': opp['postedDate'],
    'response_deadline': opp['responseDeadLine'],
    'notice_type': opp['type'],
    'naics_code': opp['naicsCode'],
    'set_aside': opp['typeOfSetAside'],
    'place_of_performance': opp['placeOfPerformance']['city']['name'],
    'description': opp['description']['body'],
    'contact_name': opp['pointOfContact'][0]['fullName'],
    'contact_email': opp['pointOfContact'][0]['email'],
    'contact_phone': opp['pointOfContact'][0]['phone'],
    'attachments': [att['url'] for att in opp.get('attachments', [])],
    'award_amount': opp.get('award', {}).get('amount'),
    'source': 'SAM.gov',
    'source_url': f"https://sam.gov/opp/{opp['noticeId']}"
}
```

**1.2.5: Deduplication Check**
```python
# Check if already in Airtable
existing = airtable.search_records(
    'GPSS OPPORTUNITIES',
    formula=f"{{Solicitation Number}}='{solicitation_number}'"
)

if existing:
    print(f"⏭️  Skipping duplicate: {solicitation_number}")
    continue
```

---

### **Step 1.3: AI Fit Scoring & Analysis**

**Module:** `nexus_backend.py` → `GPSSOpportunityMiningAgent._analyze_opportunity()`

**1.3.1: Prepare Analysis Context**
```python
context = {
    'company_name': 'Dee Davis Inc',
    'certifications': ['EDWOSB', 'WOSB', 'MBE', 'WBE'],
    'capabilities': [
        'Industrial supplies distribution',
        'Medical supplies',
        'Construction materials',
        'Government contracting'
    ],
    'past_performance': 'Federal, state, local government contracts',
    'geographic_coverage': 'Nationwide',
    'capacity': '$50K - $5M contracts'
}
```

**1.3.2: AI Analysis Request**
```python
# Using GPT-4 or similar
prompt = f"""
Analyze this government contract opportunity for Dee Davis Inc:

OPPORTUNITY:
Title: {opportunity['title']}
Agency: {opportunity['agency']}
NAICS: {opportunity['naics_code']}
Set-Aside: {opportunity['set_aside']}
Description: {opportunity['description'][:500]}

COMPANY:
{json.dumps(context, indent=2)}

Provide:
1. Fit Score (0-100)
2. Capability Gaps (what we're missing)
3. Win Probability (High/Medium/Low)
4. Recommended Actions
5. Key Requirements
"""

ai_response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[{"role": "user", "content": prompt}]
)

analysis = parse_ai_response(ai_response)
```

**1.3.3: Fit Score Calculation**

AI considers:
- **NAICS Code Match** (30 points)
  - Exact match: 30 pts
  - Related industry: 15 pts
  - Unrelated: 0 pts

- **Set-Aside Alignment** (25 points)
  - EDWOSB/WOSB: 25 pts (we have this!)
  - Other small business: 15 pts
  - Unrestricted: 10 pts

- **Contract Value Range** (20 points)
  - $50K-$5M: 20 pts (our sweet spot)
  - < $50K: 10 pts (too small)
  - > $5M: 5 pts (need partners)

- **Geographic Match** (15 points)
  - Nationwide: 15 pts
  - Our region: 10 pts
  - Far away: 5 pts

- **Capability Match** (10 points)
  - Keywords in description match our capabilities

**Example Result:**
```python
{
    'fit_score': 85,
    'capability_gaps': ['HVAC installation', '24/7 emergency response'],
    'win_probability': 'High',
    'recommended_actions': [
        'Partner with HVAC subcontractor',
        'Highlight EDWOSB certification',
        'Emphasize past federal performance'
    ],
    'key_requirements': [
        'EDWOSB certification (✓ we have)',
        'Past performance (✓ we have)',
        'HVAC capability (✗ need partner)'
    ]
}
```

---

### **Step 1.4: Save to Airtable (GPSS OPPORTUNITIES)**

**1.4.1: Prepare Airtable Fields**
```python
airtable_fields = {
    # Basic Information
    'Solicitation Number': opportunity['solicitation_number'],
    'Title': opportunity['title'],
    'Agency': opportunity['agency'],
    'Office': opportunity['office'],
    'Source': 'SAM.gov',
    'Source URL': opportunity['source_url'],
    
    # Dates
    'Posted Date': opportunity['posted_date'],
    'Response Deadline': opportunity['response_deadline'],
    'Mined Date': datetime.now().isoformat(),
    
    # Classification
    'NAICS Code': opportunity['naics_code'],
    'Notice Type': opportunity['notice_type'],
    'Set-Aside Type': opportunity['set_aside'],
    
    # Location
    'Place of Performance': opportunity['place_of_performance'],
    
    # Content
    'Description': opportunity['description'],
    'Attachments': opportunity['attachments'],
    
    # AI Analysis
    'Fit Score': analysis['fit_score'],
    'Capability Gaps': '\n'.join(analysis['capability_gaps']),
    'Win Probability': analysis['win_probability'],
    'Recommended Actions': '\n'.join(analysis['recommended_actions']),
    'Key Requirements': '\n'.join(analysis['key_requirements']),
    
    # Contact
    'Point of Contact': opportunity['contact_name'],
    'Contact Email': opportunity['contact_email'],
    'Contact Phone': opportunity['contact_phone'],
    
    # Status
    'Status': 'New',
    'Priority': 'High' if analysis['fit_score'] >= 80 else 'Medium' if analysis['fit_score'] >= 60 else 'Low',
    
    # Financial
    'Estimated Value': opportunity['award_amount'],
}
```

**1.4.2: Create Airtable Record**
```python
record = airtable_client.create_record('GPSS OPPORTUNITIES', airtable_fields)
print(f"✅ Saved: {opportunity['title']} (Fit: {analysis['fit_score']})")
```

**1.4.3: Result in Airtable**
- New record appears in "GPSS OPPORTUNITIES" table
- Status: "New"
- Fit Score: 85/100
- Priority: "High" (auto-calculated)
- All fields populated

---

### **Step 1.5: Calendar Notification Setup**

**Module:** `calendar_automation.py`

**1.5.1: Check for Upcoming Deadlines**
```python
# For opportunities with deadline within 14 days
if days_until_deadline <= 14 and days_until_deadline > 0:
    # Create calendar event
    create_calendar_reminder(opportunity)
```

**1.5.2: Create ICS Calendar File**
```python
from icalendar import Calendar, Event

cal = Calendar()
event = Event()

event.add('summary', f"BID DUE: {opportunity['title']}")
event.add('dtstart', deadline_date)
event.add('dtend', deadline_date)
event.add('description', f"""
Solicitation: {opportunity['solicitation_number']}
Agency: {opportunity['agency']}
Fit Score: {analysis['fit_score']}/100
Priority: High

Action: Review and prepare bid!
Link: {opportunity['source_url']}
""")
event.add('location', opportunity['place_of_performance'])

# Add reminders
event.add('valarm', {
    'action': 'DISPLAY',
    'trigger': timedelta(days=-7),  # 7 days before
    'description': 'Bid deadline in 7 days!'
})
event.add('valarm', {
    'action': 'DISPLAY',
    'trigger': timedelta(days=-3),  # 3 days before
    'description': 'Bid deadline in 3 days!'
})
event.add('valarm', {
    'action': 'DISPLAY',
    'trigger': timedelta(days=-1),  # 1 day before
    'description': 'Bid deadline TOMORROW!'
})

cal.add_component(event)

# Save to file
with open(f'calendars/bid_{solicitation_number}.ics', 'wb') as f:
    f.write(cal.to_ical())
```

**1.5.3: Email Notification (Optional)**
```python
if opportunity['priority'] == 'High':
    send_email(
        to=os.environ['USER_EMAIL'],
        subject=f"🎯 HIGH PRIORITY Opportunity: {opportunity['title']}",
        body=f"""
New high-priority opportunity discovered:

Title: {opportunity['title']}
Agency: {opportunity['agency']}
Deadline: {opportunity['response_deadline']}
Fit Score: {analysis['fit_score']}/100

Why it's a good fit:
{analysis['recommended_actions']}

View in NEXUS: [Airtable link]
        """
    )
```

---

### **Step 1.6: Mining State/Local Portals**

**Similar process for:**
- State procurement portals (Michigan SIGMA, etc.)
- BidNet
- DemandStar
- PlanetBids
- Direct agency websites

**Each source follows same pattern:**
1. API/scraping → 2. Parse data → 3. AI analysis → 4. Deduplication → 5. Save to Airtable

---

### **Step 1.7: Mining Summary Report**

**1.7.1: Generate Daily Summary**
```python
summary = {
    'date': datetime.now().date(),
    'total_mined': len(all_opportunities),
    'new_records': len(new_records),
    'duplicates_skipped': len(duplicates),
    'high_priority': len([o for o in new_records if o['fit_score'] >= 80]),
    'medium_priority': len([o for o in new_records if 60 <= o['fit_score'] < 80]),
    'sources': {
        'SAM.gov': sam_count,
        'State portals': state_count,
        'BidNet': bidnet_count,
        # etc.
    }
}
```

**1.7.2: Log to File**
```
2026-01-31 06:15:32 - Mining complete
✅ Total mined: 247 opportunities
✅ New records: 23
⏭️  Duplicates skipped: 224
🎯 High priority (≥80): 5
📊 Medium priority (60-79): 11
📉 Low priority (<60): 7

Sources:
  - SAM.gov: 183
  - Michigan SIGMA: 28
  - BidNet: 36

High-priority opportunities:
  1. NASA - IT Equipment ($2.5M, Fit: 85)
  2. VA - Medical Supplies ($1.2M, Fit: 87)
  3. DHS - Security Services ($800K, Fit: 82)
  4. GSA - Office Furniture ($650K, Fit: 84)
  5. DoD - Industrial Supplies ($1.8M, Fit: 86)
```

---

## PHASE 2A: FEDERAL FORECASTING (Proactive)

### **Step 2A.1: Forecast Mining Trigger**

**Time:** Every day at 6:00 AM (runs after opportunity mining)

**Cron Job:**
```bash
0 6 * * * cd "/Users/deedavis/NEXUS BACKEND" && /usr/local/bin/python3 federal_forecasts_system.py >> forecast_mining.log 2>&1
```

---

### **Step 2A.2: Mine SAM.gov Pre-Solicitations**

**Module:** `federal_forecasts_system.py` → `_mine_sam_presolicitations()`

**2A.2.1: API Request**
```python
url = "https://api.sam.gov/opportunities/v2/search"
params = {
    'ptype': 'p',  # Pre-solicitations (forecasts!)
    'postedFrom': datetime.now().strftime('%m/%d/%Y'),
    'postedTo': (datetime.now() + timedelta(days=90)).strftime('%m/%d/%Y'),
    'limit': 1000
}

response = requests.get(url, headers=headers, params=params)
presolicitations = response.json()['opportunitiesData']
```

**2A.2.2: Parse Forecast Data**
```python
for presol in presolicitations:
    forecast = {
        'title': presol['title'],
        'agency': presol['fullParentPathName'],
        'sub_agency': presol['subtierName'],
        'description': presol['description']['body'],
        'naics_code': presol['naicsCode'],
        'psc_code': presol.get('classificationCode'),
        'estimated_value': parse_value(presol.get('responseDeadLine')),
        'estimated_solicitation_date': presol['archiveDate'],  # Expected RFP date
        'solicitation_number': presol.get('solicitationNumber'),
        'set_aside_type': presol.get('typeOfSetAside'),
        'place_of_performance': presol['placeOfPerformance']['city']['name'],
        'state': presol['placeOfPerformance']['state']['name'],
        'source': 'SAM.gov Pre-Solicitation',
        'source_url': f"https://sam.gov/opp/{presol['noticeId']}",
        'forecast_type': 'Near-Term (0-3 months)',
        'confidence': 'High',  # Pre-solicitations are highly likely
        'posted_date': presol['postedDate'],
    }
```

**2A.2.3: Extract Officer Contact (if available)**
```python
if presol.get('pointOfContact'):
    poc = presol['pointOfContact'][0]
    forecast['contracting_officer'] = poc.get('fullName')
    forecast['officer_email'] = poc.get('email')
    forecast['officer_phone'] = poc.get('phone')
    forecast['officer_title'] = poc.get('title', 'Contracting Officer')
```

---

### **Step 2A.3: Mine NASA Procurement Forecasts**

**Module:** `federal_forecasts_system.py` → `_mine_nasa_forecasts()`

**2A.3.1: Web Scraping**
```python
from bs4 import BeautifulSoup

url = "https://www.hq.nasa.gov/office/procurement/forecast/"
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

# Find forecast tables
forecast_tables = soup.find_all('table', class_='procurement-forecast')
```

**2A.3.2: Parse HTML Tables**
```python
for table in forecast_tables:
    rows = table.find_all('tr')[1:]  # Skip header
    
    for row in rows:
        cols = row.find_all('td')
        
        forecast = {
            'title': cols[0].text.strip(),
            'agency': 'NASA',
            'sub_agency': cols[1].text.strip(),  # NASA center
            'description': cols[2].text.strip(),
            'naics_code': cols[3].text.strip(),
            'estimated_value': parse_currency(cols[4].text),
            'estimated_solicitation_date': parse_date(cols[5].text),
            'fiscal_year': cols[6].text.strip(),
            'set_aside_type': cols[7].text.strip() if len(cols) > 7 else 'Unrestricted',
            'source': 'NASA Official Forecast',
            'source_url': url,
            'forecast_type': 'Long-Term (6-12 months)',
            'confidence': 'Medium',  # Quarterly forecasts can change
        }
```

---

### **Step 2A.4: AI Forecast Analysis**

**Module:** `federal_forecasts_system.py` → `_analyze_forecast()`

**2A.4.1: Fit Score Calculation**
```python
# Same scoring as opportunities, but adjusted for forecast uncertainty

fit_score = calculate_fit_score(forecast)

# Adjust for forecast confidence
if forecast['confidence'] == 'High':
    confidence_multiplier = 1.0
elif forecast['confidence'] == 'Medium':
    confidence_multiplier = 0.9
else:
    confidence_multiplier = 0.8

adjusted_score = fit_score * confidence_multiplier
```

**2A.4.2: AI Analysis**
```python
analysis_prompt = f"""
This is a FORECAST (not active solicitation) for Dee Davis Inc:

{forecast_details}

Estimated solicitation: {forecast['estimated_solicitation_date']}
(That's {days_until} days away)

Analyze:
1. Fit Score (0-100) - How well do we match?
2. Preparation Tips - What to do NOW (before RFP drops)
3. Relationship Strategy - Should we reach out to the contracting officer?
4. Recommended Actions - Steps to take in next 30-90 days
"""

ai_response = gpt4_analyze(analysis_prompt)
```

**2A.4.3: Preparation Recommendations**

AI provides specific actions:
```python
{
    'fit_score': 85,
    'fit_analysis': 'Strong match - EDWOSB set-aside aligns with certifications',
    'priority': 'HIGH',
    'preparation_tips': [
        'Research NASA past awards for similar contracts',
        'Identify 2-3 subcontractors with NASA experience',
        'Prepare capability statement focused on aerospace compliance',
        'Monitor SAM.gov for actual solicitation posting',
        'Contact contracting officer to introduce company'
    ],
    'recommended_action': 'REACH OUT TO OFFICER - Build relationship before RFP',
    'relationship_strategy': 'Send introduction letter with capability statement',
    'competitive_advantage': 'EDWOSB status + early positioning'
}
```

---

### **Step 2A.5: Save to Airtable (FEDERAL FORECASTS)**

**2A.5.1: Prepare Record**
```python
airtable_fields = {
    # Basic Info
    'Title': forecast['title'],
    'Agency': forecast['agency'],
    'Sub-Agency': forecast['sub_agency'],
    'Description': forecast['description'],
    'NAICS Code': forecast['naics_code'],
    'PSC Code': forecast['psc_code'],
    
    # Financial & Timeline
    'Estimated Value': forecast['estimated_value'],
    'Estimated Solicitation Date': forecast['estimated_solicitation_date'],
    'Expected Award Date': forecast.get('expected_award_date'),
    'Contract Duration': forecast.get('contract_duration'),
    'Fiscal Year': forecast['fiscal_year'],
    
    # Procurement Details
    'Set-Aside Type': forecast['set_aside_type'],
    'Contract Type': forecast.get('contract_type'),
    'Place of Performance': forecast['place_of_performance'],
    'State': forecast['state'],
    'Solicitation Number': forecast.get('solicitation_number'),
    
    # Source & Tracking
    'Source': forecast['source'],
    'Source URL': forecast['source_url'],
    'Forecast Type': forecast['forecast_type'],
    'Confidence': forecast['confidence'],
    'Posted Date': forecast['posted_date'],
    'Mined Date': datetime.now().isoformat(),
    
    # Officer Contact (if available)
    'Contracting Officer': forecast.get('contracting_officer'),
    'Officer Email': forecast.get('officer_email'),
    'Officer Phone': forecast.get('officer_phone'),
    'Officer Title': forecast.get('officer_title'),
    
    # AI Analysis
    'Fit Score': analysis['fit_score'],
    'Fit Analysis': analysis['fit_analysis'],
    'Priority': analysis['priority'],
    'Preparation Tips': '\n'.join(analysis['preparation_tips']),
    'Recommended Action': analysis['recommended_action'],
    
    # Status
    'Status': 'New',
    'Outreach Status': 'Not Contacted',
}
```

**2A.5.2: Create Record**
```python
record = airtable_client.create_record('Federal Forecasts', airtable_fields)
print(f"✅ Forecast saved: {forecast['title']} (Fit: {analysis['fit_score']})")
```

---

### **Step 2A.6: High-Priority Alert**

**2A.6.1: Check Alert Criteria**
```python
if (
    analysis['fit_score'] >= 80 and 
    analysis['priority'] == 'HIGH' and
    forecast.get('officer_email') and
    30 <= days_until_solicitation <= 90
):
    send_high_priority_forecast_alert(forecast, analysis)
```

**2A.6.2: Email Alert**
```python
email_body = f"""
🔮 HIGH PRIORITY Federal Forecast Discovered!

FORECAST: {forecast['title']}
AGENCY: {forecast['agency']}
ESTIMATED VALUE: ${forecast['estimated_value']:,}
SOLICITATION DATE: {forecast['estimated_solicitation_date']} ({days_until} days away)
SET-ASIDE: {forecast['set_aside_type']}

FIT SCORE: {analysis['fit_score']}/100
PRIORITY: HIGH

WHY IT'S A GOOD FIT:
{analysis['fit_analysis']}

RECOMMENDED ACTION:
{analysis['recommended_action']}

PREPARATION TIPS:
{chr(10).join(f"• {tip}" for tip in analysis['preparation_tips'])}

CONTRACTING OFFICER:
Name: {forecast.get('contracting_officer', 'Not identified')}
Email: {forecast.get('officer_email', 'Not available')}

ACTION: Click "📧 Reach Out to Officer" in Airtable to generate capability statement and introduction letter!

View in NEXUS: [Airtable link]
"""

send_email(
    to=os.environ['USER_EMAIL'],
    subject=f"🔮 HIGH PRIORITY Forecast: {forecast['title'][:50]}...",
    body=email_body
)
```

---

## PHASE 2B: FORECAST CAPABILITY STATEMENT & OUTREACH

### **Step 2B.1: User Reviews Forecast in Airtable**

**2B.1.1: User Opens Federal Forecasts Table**
- Navigates to Airtable
- Opens "Federal Forecasts" table
- Clicks "High Priority Forecasts" view (filtered: Fit Score ≥ 80)

**2B.1.2: User Selects High-Priority Forecast**
```
Record Details:
  Title: NASA - IT Equipment Modernization
  Agency: NASA Johnson Space Center
  Estimated Value: $2,500,000
  Solicitation Date: April 15, 2026 (74 days away)
  Set-Aside: WOSB
  Fit Score: 85/100
  Priority: HIGH
  
  Contracting Officer: John Smith
  Officer Email: john.smith@nasa.gov
  Officer Phone: (281) 555-0123
  
  Outreach Status: Not Contacted
```

**2B.1.3: User Decision**
- Reads AI preparation tips
- Decides to reach out proactively
- Clicks "📧 Reach Out to Officer" button

---

### **Step 2B.2: Button Click Triggers Airtable Automation**

**2B.2.1: Airtable Button Configuration**
```javascript
// Button script in Airtable
let forecast = input.config();
let forecastId = forecast.id;

// Call NEXUS API
let response = await fetch(
    `http://your-server.com/api/forecasts/${forecastId}/generate-capstat-outreach`,
    {
        method: 'POST',
        headers: {'Content-Type': 'application/json'}
    }
);

let result = await response.json();

if (result.success) {
    output.markdown(`✅ **Success!**
    
Cap Statement Generated: ${result.capstat_pdf}
Outreach Letter Generated: Ready to review

Officer: ${result.officer_name}
Email: ${result.officer_email}

Next steps:
1. Download capability statement PDF
2. Review outreach letter in Officer Outreach Tracking
3. Customize if needed
4. Send email to officer
5. Track relationship!
    `);
} else {
    output.markdown(`❌ Error: ${result.error}`);
}
```

---

### **Step 2B.3: API Endpoint Processes Request**

**File:** `api_server.py` → `generate_forecast_capstat_outreach()`

**2B.3.1: Receive Request**
```python
@app.route('/api/forecasts/<forecast_id>/generate-capstat-outreach', methods=['POST'])
def generate_forecast_capstat_outreach(forecast_id: str):
    try:
        from forecast_capstat_outreach import handle_forecast_capstat_outreach
        
        result = handle_forecast_capstat_outreach(forecast_id)
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
```

**2B.3.2: Call Handler Function**
```python
# forecast_capstat_outreach.py
def handle_forecast_capstat_outreach(forecast_id: str) -> Dict:
    airtable = AirtableClient()
    forecast_outreach = ForecastCapStatOutreach(airtable)
    
    result = forecast_outreach.generate_forecast_capstat_and_outreach(forecast_id)
    
    return result
```

---

### **Step 2B.4: Get Forecast Details from Airtable**

**2B.4.1: Fetch Forecast Record**
```python
forecast = airtable.get_record('Federal Forecasts', forecast_id)
fields = forecast['fields']
```

**2B.4.2: Extract Data**
```python
forecast_data = {
    'title': fields['Title'],
    'agency': fields['Agency'],
    'sub_agency': fields.get('Sub-Agency'),
    'estimated_value': fields.get('Estimated Value'),
    'estimated_date': fields.get('Estimated Solicitation Date'),
    'set_aside': fields.get('Set-Aside Type'),
    'description': fields.get('Description'),
    'fit_analysis': fields.get('Fit Analysis'),
    'officer_name': fields.get('Contracting Officer'),
    'officer_email': fields.get('Officer Email'),
    'officer_phone': fields.get('Officer Phone'),
    'officer_title': fields.get('Officer Title', 'Contracting Officer'),
}
```

**2B.4.3: Validate Required Fields**
```python
if not forecast_data['officer_name'] or not forecast_data['officer_email']:
    return {
        'success': False,
        'error': 'Forecast must have Contracting Officer name and email'
    }
```

---

### **Step 2B.5: Generate Capability Statement**

**Module:** `forecast_capstat_outreach.py` → `_generate_forecast_capstat()`

**2B.5.1: Determine Template**
```python
def _determine_template(fields):
    title_lower = fields['Title'].lower()
    desc_lower = fields.get('Description', '').lower()
    
    # Medical/Healthcare template
    if any(word in title_lower or word in desc_lower for word in [
        'medical', 'healthcare', 'hospital', 'va ', 'health'
    ]):
        return 'va_medical'
    
    # Construction template
    if any(word in title_lower or word in desc_lower for word in [
        'construction', 'building', 'renovation', 'facility'
    ]):
        return 'construction'
    
    # Default (industrial supplies)
    return 'default'

template = _determine_template(forecast_data)
```

**2B.5.2: Call Capability Statement Generator**
```python
from capability_statement_generator import handle_generate_capability_statement

result = handle_generate_capability_statement(
    client_name=forecast_data['agency'],
    rfq_number=f"FORECAST-{forecast_id[:8]}",
    rfq_title=forecast_data['title'],
    template=template
)
```

**2B.5.3: Generate HTML Capability Statement**

**File:** `generate_html_with_highlights.py`

```python
# Load template
with open('capability_statement_template.html', 'r') as f:
    template_html = f.read()

# Replace variables
html = template_html.replace('{{COMPANY_NAME}}', 'DEE DAVIS INC')
html = html.replace('{{CLIENT_NAME}}', forecast_data['agency'])
html = html.replace('{{RFQ_NUMBER}}', f"FORECAST-{forecast_id[:8]}")
html = html.replace('{{RFQ_TITLE}}', forecast_data['title'])
html = html.replace('{{DATE}}', datetime.now().strftime('%B %Y'))

# Company data
html = html.replace('{{CAGE_CODE}}', '8UMX3')
html = html.replace('{{UEI}}', 'HJB4KNYJVGZ1')
html = html.replace('{{DUNS}}', '002636755')
html = html.replace('{{TAX_ID}}', '84-4114181')

# ... replace all other variables ...

# Save HTML
output_file = f'generated_capability_statements/capstat_{forecast_data["agency"].replace(" ", "_")}_FORECAST_{datetime.now().strftime("%Y%m%d")}.html'
with open(output_file, 'w') as f:
    f.write(html)
```

**2B.5.4: Generate PDF from HTML**

**File:** `generate_enhanced_pdf.py`

```python
from weasyprint import HTML

html_file = result['html_file']
pdf_file = html_file.replace('.html', '.pdf')

HTML(html_file).write_pdf(pdf_file)

print(f"✅ PDF generated: {pdf_file}")
```

---

### **Step 2B.6: Generate Forecast Outreach Letter**

**Module:** `forecast_capstat_outreach.py` → `_generate_forecast_outreach_letter()`

**2B.6.1: Build Letter Content**

**(I'll continue with the extremely detailed breakdown in the next section due to length...)**

Would you like me to continue with the complete detailed breakdown? I can go through every single step of:
- Letter generation with exact text
- ProposalBio™ automatic analysis
- Saving to Airtable with all fields
- The entire bid preparation phase
- Supplier/subcontractor sourcing
- Proposal generation with ProposalBio™
- Document assembly
- Fulfillment workflow
- Invoicing process
- Financial tracking

Each with code examples, API calls, data transformations, and exact sequences?