# AUTOMATED SUBCONTRACTOR SOURCING SYSTEM
**Find, Vet, and Manage Subs Automatically**

**Similar to:** Officer Outreach Automation, Auto CapStat  
**Integration:** NEXUS + Airtable + Email Automation

---

## 🎯 THE VISION

**Manual Process (Current):**
- Find subs on Google/Yelp manually (2-3 hours)
- Email/call each one individually (1-2 hours)
- Track responses in spreadsheet (30 min)
- Chase follow-ups manually (ongoing)
- **Total: 4-6 hours per service bid**

**Automated Process (New):**
- Click "Find Subs" button in NEXUS
- System searches Google/Yelp API
- Automatically sends outreach emails to 10 potential subs
- Tracks responses in Airtable
- Auto-sends follow-ups
- Generates comparison report
- **Total: 15 minutes of your time**

---

## 🏗️ SYSTEM ARCHITECTURE

```
┌─────────────────────────────────────────────────────────┐
│                   NEXUS FRONTEND                         │
│            (React - New "Subcontractors" Tab)           │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  🔍 FIND SUBS FOR OPPORTUNITY                           │
│  ┌────────────────────────────────────────────────┐    │
│  │ Opportunity: Madison Heights Lawn Care         │    │
│  │ Service Type: [Landscaping ▼]                  │    │
│  │ Location: [Oakland County, MI]                 │    │
│  │ Search Radius: [25 miles ▼]                   │    │
│  │                                                 │    │
│  │ [🔍 Find Subcontractors]                       │    │
│  │                                                 │    │
│  │ ⏳ Searching Google, Yelp, Angi...            │    │
│  │ ✓ Found 47 potential subcontractors           │    │
│  │ ✓ Filtered to 15 qualified (3+ stars, etc.)  │    │
│  │ ✓ Sending outreach emails...                  │    │
│  │ ✓ 15 emails sent, tracking in Airtable       │    │
│  └────────────────────────────────────────────────┘    │
│                                                          │
│  📊 SUBCONTRACTOR RESPONSES                             │
│  ┌────────────────────────────────────────────────┐    │
│  │ ABC Lawn Care         ✓ Interested   $450/park│    │
│  │ XYZ Landscaping       ⏳ Pending     $___     │    │
│  │ 123 Maintenance       ✓ Interested   $500/park│    │
│  │ Green Gardens         ❌ Not available        │    │
│  │ ...                                            │    │
│  │                                                 │    │
│  │ [📧 Send Follow-ups] [📋 Compare Quotes]      │    │
│  └────────────────────────────────────────────────┘    │
│                                                          │
└─────────────────────────────────────────────────────────┘
                         ↓ API Calls ↓
┌─────────────────────────────────────────────────────────┐
│                  NEXUS BACKEND API                       │
│                (Python/FastAPI)                          │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  POST /api/subs/find                                    │
│  • Search Google Maps API for contractors               │
│  • Search Yelp API for contractors                      │
│  • Scrape Angi/Thumbtack (if needed)                   │
│  • Filter by rating, years, commercial experience       │
│  • Save to Airtable SUBCONTRACTORS table               │
│  • Return list of qualified subs                        │
│                                                          │
│  POST /api/subs/outreach                                │
│  • Generate personalized email for each sub             │
│  • Send via SendGrid/Mailgun                           │
│  • Create tracking record in Airtable                   │
│  • Schedule follow-up if no response                    │
│                                                          │
│  GET /api/subs/responses                                │
│  • Fetch responses from Airtable                        │
│  • Parse for interested/pricing/availability            │
│  • Generate comparison report                           │
│                                                          │
│  POST /api/subs/follow-up                               │
│  • Send follow-up emails to non-responders             │
│  • Update tracking in Airtable                          │
│                                                          │
│  POST /api/subs/generate-loi                            │
│  • Auto-generate Letter of Intent from template        │
│  • Populate with sub details and pricing               │
│  • Send for e-signature via DocuSign                    │
│                                                          │
└─────────────────────────────────────────────────────────┘
                         ↓ Stores In ↓
┌─────────────────────────────────────────────────────────┐
│                    AIRTABLE DATABASE                     │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  SUBCONTRACTORS Table (Master Database)                │
│  • Company name, contact, phone, email                  │
│  • Service type(s), coverage area                       │
│  • Rating, years in business, certifications            │
│  • Insurance info, license numbers                      │
│  • Past performance, availability                       │
│                                                          │
│  SUB OUTREACH TRACKING Table                            │
│  • Link to Opportunity + Subcontractor                  │
│  • Outreach date, email sent                            │
│  • Response status (pending/interested/declined)        │
│  • Quote amount, terms                                  │
│  • Follow-up dates, notes                               │
│                                                          │
│  SUB PERFORMANCE Table                                  │
│  • Link to Opportunity + Subcontractor                  │
│  • Response time, completion rate                       │
│  • Quality rating, issues                               │
│  • Would use again? (Y/N)                              │
│                                                          │
└─────────────────────────────────────────────────────────┘
                         ↓ Integrates With ↓
┌─────────────────────────────────────────────────────────┐
│                  EMAIL AUTOMATION                        │
│              (SendGrid or Mailgun)                       │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  • Sends personalized outreach emails                   │
│  • Tracks opens, clicks, replies                        │
│  • Auto-sends follow-ups after 3-5 days                │
│  • Logs all activity to Airtable                        │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## 📊 AIRTABLE SCHEMA

### **Table 1: SUBCONTRACTORS** (Master Database)

```javascript
{
  "CompanyName": "ABC Lawn Care",
  "ContactName": "John Smith",
  "Email": "john@abclawn.com",
  "Phone": "(555) 123-4567",
  "Website": "https://abclawn.com",
  "ServiceTypes": ["Landscaping", "Snow Removal", "Lawn Care"],
  "CoverageArea": "Oakland County, MI",
  "GoogleRating": 4.8,
  "YelpRating": 4.7,
  "YearsInBusiness": 12,
  "CommercialExperience": true,
  "GovernmentExperience": true,
  "Insurance_Liability": "$2M",
  "Insurance_WorkersComp": true,
  "License_Number": "MI-12345",
  "License_State": "Michigan",
  "Certifications": ["MNLA Member", "ISA Certified"],
  "GoogleMapsURL": "https://maps.google.com/...",
  "YelpURL": "https://yelp.com/biz/...",
  "FirstContactDate": "2026-02-04",
  "LastContactDate": "2026-02-04",
  "Status": "Active",
  "Notes": "Responsive, good pricing",
  "AvgResponseTime_Hours": 4,
  "AvgQuoteTime_Hours": 24,
  "UsedBefore": true,
  "WouldUseAgain": true,
  "OverallRating": 5
}
```

---

### **Table 2: SUB_OUTREACH_TRACKING**

```javascript
{
  "OpportunityID": "rec123...",  // Link to Opportunities table
  "SubcontractorID": "rec456...", // Link to Subcontractors table
  "OutreachDate": "2026-02-04T10:30:00",
  "EmailSubject": "Government Contract Opportunity - Lawn Care",
  "EmailSent": true,
  "EmailOpened": true,
  "EmailOpenedDate": "2026-02-04T14:22:00",
  "EmailClicked": true,
  "ResponseStatus": "Interested",  // Pending, Interested, Declined, No Response
  "ResponseDate": "2026-02-04T15:30:00",
  "QuoteAmount": 4500,
  "QuoteDetails": "Per park per month for 7 months",
  "Available": true,
  "AvailabilityNotes": "Can start April 1",
  "FollowUpNeeded": false,
  "FollowUpDate": null,
  "FollowUpSent": false,
  "LOI_Requested": true,
  "LOI_Received": false,
  "InsuranceCert_Requested": true,
  "InsuranceCert_Received": false,
  "Selected": false,
  "DeclineReason": null,
  "Notes": "Very responsive, competitive pricing"
}
```

---

### **Table 3: SUB_PERFORMANCE**

```javascript
{
  "OpportunityID": "rec123...",
  "SubcontractorID": "rec456...",
  "ProjectStartDate": "2026-04-01",
  "ProjectEndDate": "2026-10-31",
  "ServiceType": "Lawn Care",
  "NumberOfServices": 280,
  "CompletedServices": 276,
  "MissedServices": 4,
  "CompletionRate": 98.57,
  "AvgResponseTime_Hours": 36,
  "QualityIssues": 2,
  "ClientSatisfaction": 4.8,
  "OnTimePerformance": 97.5,
  "CommunicationRating": 5,
  "SafetyIncidents": 0,
  "WouldUseAgain": true,
  "Strengths": "Reliable, good communication, quality work",
  "WeaknessesImprovements": "Occasional scheduling conflicts in peak season",
  "OverallRating": 5,
  "Notes": "Excellent sub, will use again"
}
```

---

## 🔍 AUTOMATED SUB DISCOVERY

### **Search APIs to Use:**

**1. Google Maps Places API**
```python
# Search: "landscaping Oakland County MI"
# Returns: Business name, rating, reviews, phone, website
# Filter: ≥4 stars, ≥10 reviews, commercial keywords
```

**2. Yelp Fusion API**
```python
# Search: "lawn care Oakland County MI"
# Returns: Business details, ratings, photos, hours
# Filter: ≥4 stars, "commercial" in description
```

**3. Yellow Pages API** (optional)
```python
# Business listings with contact info
```

**4. Web Scraping** (if APIs insufficient)
```python
# Scrape Angi, Thumbtack, HomeAdvisor
# Extract: Name, phone, rating, reviews
```

---

### **Filtering Logic:**

**Auto-qualify if:**
- ✅ Rating ≥4.0 stars
- ✅ ≥10 reviews (established business)
- ✅ Phone number available
- ✅ Email or website available
- ✅ Service area includes target location
- ✅ Keywords: "commercial", "government", "municipal" (bonus)

**Auto-disqualify if:**
- ❌ Rating <3.5 stars
- ❌ <5 reviews (too new/unproven)
- ❌ No contact info
- ❌ Keywords: "residential only"

---

## 📧 AUTOMATED OUTREACH EMAILS

### **Email Template (Auto-Personalized):**

```
Subject: Government Contract Opportunity - {{ServiceType}} in {{Location}}

Hi {{ContactName or "there"}},

I'm Dee Davis with DEE DAVIS INC, a certified EDWOSB prime contractor. 
I found {{CompanyName}} on {{Source}} and was impressed by your {{Rating}}-star 
rating and {{ReviewCount}} reviews.

I'm bidding on a {{ServiceType}} contract for a {{ClientType}} in {{Location}} 
and looking for a qualified subcontractor partner.

PROJECT SCOPE:
• Service: {{ServiceDescription}}
• Location: {{GeneralLocation}}
• Duration: {{ContractLength}}
• Volume: {{VolumeEstimate}}
• Start Date: {{StartDate}}

REQUIREMENTS:
• $1M liability insurance
• {{OtherRequirements}}

If you're interested and available, I'd appreciate a response with your:
1. Pricing (per {{PricingUnit}})
2. Availability starting {{StartDate}}
3. Confirmation of insurance coverage

Please respond by {{ResponseDeadline}} if interested. I'm evaluating multiple 
contractors and will select partners this week.

You can reply to this email or call me at {{YourPhone}}.

Best regards,

Dee Davis
DEE DAVIS INC
{{YourPhone}}
{{YourEmail}}
www.deedavis.biz

---

P.S. This is a government contract with reliable payment and potential for 
ongoing work. References required if selected.
```

**Auto-personalization from data:**
- {{ContactName}}: From business listing or "there" if unknown
- {{CompanyName}}: From search results
- {{Source}}: "Google" or "Yelp"
- {{Rating}}: Actual star rating
- {{ReviewCount}}: Number of reviews
- {{ServiceType}}: From opportunity record
- {{ClientType}}: "municipal client" (generic - protect buyer!)
- {{Location}}: County/region only (not specific city)
- All other {{fields}}: From opportunity in Airtable

---

### **Follow-Up Email (Auto-Sent After 3 Days):**

```
Subject: Follow-up - Government Contract Opportunity - {{ServiceType}}

Hi {{ContactName or "there"}},

I wanted to follow up on my email from {{OriginalEmailDate}} regarding the 
{{ServiceType}} opportunity in {{Location}}.

I'm still evaluating contractors and would love to include {{CompanyName}} 
if you're interested and available.

Quick reminder of the scope:
• Service: {{ServiceDescription}}
• Duration: {{ContractLength}}
• Start: {{StartDate}}

Please let me know by {{NewDeadline}} if you'd like to be considered.

Thanks,
Dee Davis
DEE DAVIS INC
{{YourPhone}}
```

---

## 🤖 THE AUTOMATION WORKFLOW

### **Step 1: User Clicks "Find Subs" in NEXUS**

**What happens:**
1. NEXUS frontend sends opportunity details to backend
2. Backend extracts: Service type, location, requirements
3. Calls Google Maps API: "lawn care Oakland County MI"
4. Calls Yelp API: "landscaping Oakland County MI"
5. Filters results (rating, reviews, keywords)
6. Saves 10-20 qualified subs to Airtable SUBCONTRACTORS table
7. Returns list to frontend

**Time: 30 seconds**

---

### **Step 2: User Clicks "Send Outreach Emails"**

**What happens:**
1. Backend generates personalized email for each sub
2. Fills template with opportunity details + sub details
3. Sends via SendGrid/Mailgun API
4. Creates tracking record in SUB_OUTREACH_TRACKING table
5. Sets follow-up reminder for 3 days
6. Returns confirmation to frontend

**Time: 15 seconds to send 15 emails**

---

### **Step 3: Automated Response Tracking**

**What happens:**
1. Email service tracks opens/clicks automatically
2. When sub replies:
   - Email forwarded to dedicated address (subs@deedavis.biz)
   - OR sub clicks "I'm Interested" button in email (webhook)
   - Backend parses response for keywords (interested, pricing, available)
   - Updates SUB_OUTREACH_TRACKING status
   - Notifies you in NEXUS
   - You review and respond manually (or use template)

**Time: Automatic**

---

### **Step 4: Automated Follow-Ups** (After 3 Days)

**What happens:**
1. Airtable automation triggers after 3 days if no response
2. Sends follow-up email automatically
3. Updates tracking record
4. Sets final follow-up for 5 days if still no response

**Time: Automatic**

---

### **Step 5: Quote Comparison**

**What happens:**
1. User clicks "Compare Quotes" in NEXUS
2. Backend pulls all responses with pricing
3. Generates comparison table:
   - Sub name, rating, price, availability
   - Sorts by price or rating
   - Highlights best value
4. Displays in NEXUS frontend

**Time: Instant**

---

### **Step 6: Letter of Intent Generation**

**What happens:**
1. User selects sub and clicks "Request LOI"
2. Backend auto-fills LOI template with:
   - Sub details
   - Opportunity details
   - Agreed pricing
3. Generates PDF
4. Sends via DocuSign for e-signature
5. Tracks in Airtable

**Time: 2 minutes**

---

## 🖥️ BACKEND IMPLEMENTATION

### **File: `automated_sub_sourcing.py`**

```python
#!/usr/bin/env python3
"""
Automated Subcontractor Sourcing System
Finds, vets, and contacts subcontractors automatically
"""

import os
import requests
from typing import List, Dict
from pyairtable import Api
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from datetime import datetime, timedelta

class SubcontractorSourcingSystem:
    """Automated subcontractor discovery and outreach"""
    
    def __init__(self):
        self.airtable_key = os.getenv('AIRTABLE_API_KEY')
        self.base_id = os.getenv('AIRTABLE_BASE_ID')
        self.google_maps_key = os.getenv('GOOGLE_MAPS_API_KEY')
        self.yelp_api_key = os.getenv('YELP_API_KEY')
        self.sendgrid_key = os.getenv('SENDGRID_API_KEY')
        
        self.api = Api(self.airtable_key)
        self.subs_table = self.api.table(self.base_id, 'SUBCONTRACTORS')
        self.tracking_table = self.api.table(self.base_id, 'SUB_OUTREACH_TRACKING')
    
    def find_subcontractors(self, service_type: str, location: str, 
                           radius_miles: int = 25) -> List[Dict]:
        """
        Find subcontractors using Google Maps and Yelp APIs
        """
        print(f"🔍 Searching for {service_type} contractors in {location}...")
        
        # Search Google Maps
        google_results = self._search_google_maps(service_type, location, radius_miles)
        print(f"   ✓ Google Maps: Found {len(google_results)} businesses")
        
        # Search Yelp
        yelp_results = self._search_yelp(service_type, location, radius_miles)
        print(f"   ✓ Yelp: Found {len(yelp_results)} businesses")
        
        # Combine and deduplicate
        all_results = self._merge_results(google_results, yelp_results)
        
        # Filter by quality
        qualified = self._filter_qualified(all_results)
        print(f"   ✓ Filtered to {len(qualified)} qualified contractors")
        
        # Save to Airtable
        saved = self._save_to_airtable(qualified)
        print(f"   ✓ Saved {saved} new contractors to database")
        
        return qualified
    
    def _search_google_maps(self, service_type: str, location: str, 
                           radius_miles: int) -> List[Dict]:
        """Search Google Maps Places API"""
        url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
        
        params = {
            'query': f"{service_type} {location}",
            'radius': radius_miles * 1609,  # Convert miles to meters
            'key': self.google_maps_key
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
        results = []
        for place in data.get('results', []):
            results.append({
                'name': place.get('name'),
                'rating': place.get('rating', 0),
                'total_reviews': place.get('user_ratings_total', 0),
                'address': place.get('formatted_address'),
                'place_id': place.get('place_id'),
                'source': 'Google Maps'
            })
        
        return results
    
    def _search_yelp(self, service_type: str, location: str, 
                    radius_miles: int) -> List[Dict]:
        """Search Yelp Fusion API"""
        url = "https://api.yelp.com/v3/businesses/search"
        
        headers = {
            'Authorization': f'Bearer {self.yelp_api_key}'
        }
        
        params = {
            'term': service_type,
            'location': location,
            'radius': int(radius_miles * 1609),  # Convert to meters
            'limit': 50,
            'sort_by': 'rating'
        }
        
        response = requests.get(url, headers=headers, params=params)
        data = response.json()
        
        results = []
        for business in data.get('businesses', []):
            results.append({
                'name': business.get('name'),
                'rating': business.get('rating', 0),
                'total_reviews': business.get('review_count', 0),
                'phone': business.get('phone'),
                'address': business['location'].get('address1'),
                'city': business['location'].get('city'),
                'yelp_url': business.get('url'),
                'source': 'Yelp'
            })
        
        return results
    
    def _merge_results(self, google_results: List[Dict], 
                      yelp_results: List[Dict]) -> List[Dict]:
        """Combine and deduplicate results from multiple sources"""
        merged = {}
        
        # Add all results, keying by normalized name
        for result in google_results + yelp_results:
            key = result['name'].lower().strip()
            if key not in merged:
                merged[key] = result
            else:
                # Merge data from multiple sources
                existing = merged[key]
                if result.get('phone') and not existing.get('phone'):
                    existing['phone'] = result['phone']
                if result.get('yelp_url'):
                    existing['yelp_url'] = result['yelp_url']
        
        return list(merged.values())
    
    def _filter_qualified(self, results: List[Dict]) -> List[Dict]:
        """Filter for qualified contractors only"""
        qualified = []
        
        for sub in results:
            # Must have rating ≥4.0
            if sub.get('rating', 0) < 4.0:
                continue
            
            # Must have at least 10 reviews (established)
            if sub.get('total_reviews', 0) < 10:
                continue
            
            # Must have contact info
            if not sub.get('phone') and not sub.get('yelp_url'):
                continue
            
            qualified.append(sub)
        
        return qualified
    
    def _save_to_airtable(self, subs: List[Dict]) -> int:
        """Save contractors to Airtable SUBCONTRACTORS table"""
        saved_count = 0
        
        for sub in subs:
            # Check if already exists
            existing = self.subs_table.all(
                formula=f"{{CompanyName}}='{sub['name']}'"
            )
            
            if existing:
                continue  # Skip duplicates
            
            # Create new record
            self.subs_table.create({
                'CompanyName': sub['name'],
                'Phone': sub.get('phone', ''),
                'GoogleRating': sub.get('rating', 0),
                'YelpURL': sub.get('yelp_url', ''),
                'Address': sub.get('address', ''),
                'FirstContactDate': datetime.now().isoformat(),
                'Status': 'New',
                'Source': sub.get('source', 'API Search')
            })
            
            saved_count += 1
        
        return saved_count
    
    def send_outreach_emails(self, opportunity_id: str, 
                           subcontractor_ids: List[str]) -> Dict:
        """
        Send personalized outreach emails to selected subcontractors
        """
        print(f"📧 Sending outreach emails to {len(subcontractor_ids)} contractors...")
        
        # Get opportunity details
        opp_table = self.api.table(self.base_id, 'Opportunities')
        opportunity = opp_table.get(opportunity_id)
        opp_fields = opportunity['fields']
        
        results = {
            'sent': 0,
            'failed': 0,
            'errors': []
        }
        
        for sub_id in subcontractor_ids:
            try:
                # Get subcontractor details
                sub = self.subs_table.get(sub_id)
                sub_fields = sub['fields']
                
                # Generate personalized email
                email_content = self._generate_outreach_email(opp_fields, sub_fields)
                
                # Send via SendGrid
                self._send_email(
                    to_email=sub_fields.get('Email', ''),
                    subject=email_content['subject'],
                    body=email_content['body']
                )
                
                # Create tracking record
                self.tracking_table.create({
                    'OpportunityID': [opportunity_id],
                    'SubcontractorID': [sub_id],
                    'OutreachDate': datetime.now().isoformat(),
                    'EmailSubject': email_content['subject'],
                    'EmailSent': True,
                    'ResponseStatus': 'Pending',
                    'FollowUpNeeded': True,
                    'FollowUpDate': (datetime.now() + timedelta(days=3)).isoformat()
                })
                
                results['sent'] += 1
                print(f"   ✓ Sent to {sub_fields.get('CompanyName')}")
                
            except Exception as e:
                results['failed'] += 1
                results['errors'].append(str(e))
                print(f"   ✗ Failed to send to {sub_fields.get('CompanyName')}: {e}")
        
        print(f"\n✅ Outreach complete: {results['sent']} sent, {results['failed']} failed")
        return results
    
    def _generate_outreach_email(self, opp: Dict, sub: Dict) -> Dict:
        """Generate personalized outreach email"""
        
        # Get response deadline (5 days from now)
        deadline = (datetime.now() + timedelta(days=5)).strftime('%B %d, %Y')
        
        subject = f"Government Contract Opportunity - {opp.get('ServiceType', 'Services')} in {opp.get('Location', '')}"
        
        body = f"""Hi {sub.get('ContactName', 'there')},

I'm Dee Davis with DEE DAVIS INC, a certified EDWOSB prime contractor. 
I found {sub.get('CompanyName')} and was impressed by your {sub.get('GoogleRating', 'high')}-star rating.

I'm bidding on a {opp.get('ServiceType')} contract for a municipal client in {opp.get('GeneralLocation', opp.get('Location'))} 
and looking for a qualified subcontractor partner.

PROJECT SCOPE:
• Service: {opp.get('Description', 'See RFP for details')}
• Location: {opp.get('GeneralLocation', 'County/region')}
• Duration: {opp.get('ContractLength', 'TBD')}
• Start Date: {opp.get('StartDate', 'TBD')}

REQUIREMENTS:
• $1M liability insurance (DEE DAVIS INC as additional insured)
• {opp.get('OtherRequirements', 'License in good standing')}

If you're interested and available, please respond with:
1. Your pricing (per {opp.get('PricingUnit', 'unit')})
2. Availability starting {opp.get('StartDate', 'soon')}
3. Confirmation of insurance coverage

Please respond by {deadline} if interested. I'm evaluating multiple contractors 
and will select partners this week.

Best regards,

Dee Davis, President
DEE DAVIS INC
248-376-4550
info@deedavis.biz
www.deedavis.biz

---

P.S. This is a government contract with reliable payment and potential for 
ongoing work. References required if selected.
"""
        
        return {
            'subject': subject,
            'body': body
        }
    
    def _send_email(self, to_email: str, subject: str, body: str):
        """Send email via SendGrid"""
        message = Mail(
            from_email='info@deedavis.biz',
            to_emails=to_email,
            subject=subject,
            plain_text_content=body
        )
        
        sg = SendGridAPIClient(self.sendgrid_key)
        response = sg.send(message)
        
        return response.status_code == 202
    
    def send_follow_ups(self):
        """
        Send automated follow-up emails to non-responders
        Called by scheduled task (daily)
        """
        print("🔄 Checking for follow-ups needed...")
        
        # Find tracking records that need follow-up
        today = datetime.now().date().isoformat()
        
        records = self.tracking_table.all(
            formula=f"AND({{FollowUpNeeded}}=TRUE(), {{FollowUpDate}}<='{today}', {{ResponseStatus}}='Pending')"
        )
        
        print(f"   Found {len(records)} follow-ups to send")
        
        for record in records:
            fields = record['fields']
            
            # Get opportunity and sub details
            opp_id = fields['OpportunityID'][0]
            sub_id = fields['SubcontractorID'][0]
            
            opp_table = self.api.table(self.base_id, 'Opportunities')
            opportunity = opp_table.get(opp_id)
            subcontractor = self.subs_table.get(sub_id)
            
            # Generate follow-up email
            email = self._generate_follow_up_email(
                opportunity['fields'],
                subcontractor['fields'],
                fields.get('OutreachDate')
            )
            
            # Send email
            self._send_email(
                to_email=subcontractor['fields'].get('Email'),
                subject=email['subject'],
                body=email['body']
            )
            
            # Update tracking record
            self.tracking_table.update(record['id'], {
                'FollowUpSent': True,
                'FollowUpNeeded': False
            })
            
            print(f"   ✓ Follow-up sent to {subcontractor['fields'].get('CompanyName')}")
        
        print(f"✅ Follow-ups complete")
    
    def _generate_follow_up_email(self, opp: Dict, sub: Dict, 
                                  original_date: str) -> Dict:
        """Generate follow-up email"""
        
        original = datetime.fromisoformat(original_date).strftime('%B %d')
        deadline = (datetime.now() + timedelta(days=2)).strftime('%B %d, %Y')
        
        subject = f"Follow-up - Government Contract Opportunity - {opp.get('ServiceType')}"
        
        body = f"""Hi {sub.get('ContactName', 'there')},

I wanted to follow up on my email from {original} regarding the 
{opp.get('ServiceType')} opportunity in {opp.get('GeneralLocation')}.

I'm still evaluating contractors and would love to include {sub.get('CompanyName')} 
if you're interested and available.

Quick reminder of the scope:
• Service: {opp.get('Description', 'See original email')}
• Duration: {opp.get('ContractLength', 'TBD')}
• Start: {opp.get('StartDate', 'TBD')}

Please let me know by {deadline} if you'd like to be considered.

Thanks,
Dee Davis
DEE DAVIS INC
248-376-4550
info@deedavis.biz
"""
        
        return {
            'subject': subject,
            'body': body
        }
    
    def compare_quotes(self, opportunity_id: str) -> List[Dict]:
        """
        Generate comparison report of all quotes received
        """
        # Get all tracking records for this opportunity with quotes
        records = self.tracking_table.all(
            formula=f"AND({{OpportunityID}}='{opportunity_id}', {{ResponseStatus}}='Interested')"
        )
        
        comparisons = []
        
        for record in records:
            fields = record['fields']
            sub_id = fields['SubcontractorID'][0]
            sub = self.subs_table.get(sub_id)
            sub_fields = sub['fields']
            
            comparisons.append({
                'company': sub_fields.get('CompanyName'),
                'rating': sub_fields.get('GoogleRating', 0),
                'quote_amount': fields.get('QuoteAmount', 0),
                'available': fields.get('Available', False),
                'response_time_hours': (
                    datetime.fromisoformat(fields.get('ResponseDate')) - 
                    datetime.fromisoformat(fields.get('OutreachDate'))
                ).total_seconds() / 3600 if fields.get('ResponseDate') else 999,
                'notes': fields.get('Notes', '')
            })
        
        # Sort by quote amount (lowest first)
        comparisons.sort(key=lambda x: x['quote_amount'])
        
        return comparisons


# API endpoint handlers
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()
sourcing_system = SubcontractorSourcingSystem()

class FindSubsRequest(BaseModel):
    service_type: str
    location: str
    radius_miles: int = 25

class OutreachRequest(BaseModel):
    opportunity_id: str
    subcontractor_ids: List[str]

@app.post("/api/subs/find")
def find_subs(request: FindSubsRequest):
    """Find subcontractors for opportunity"""
    try:
        results = sourcing_system.find_subcontractors(
            service_type=request.service_type,
            location=request.location,
            radius_miles=request.radius_miles
        )
        return {
            'success': True,
            'count': len(results),
            'subcontractors': results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/subs/outreach")
def send_outreach(request: OutreachRequest):
    """Send outreach emails to selected subs"""
    try:
        results = sourcing_system.send_outreach_emails(
            opportunity_id=request.opportunity_id,
            subcontractor_ids=request.subcontractor_ids
        )
        return {
            'success': True,
            'sent': results['sent'],
            'failed': results['failed']
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/subs/follow-up")
def send_followups():
    """Send automated follow-ups (called by cron)"""
    try:
        sourcing_system.send_follow_ups()
        return {'success': True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/subs/compare/{opportunity_id}")
def compare_quotes_endpoint(opportunity_id: str):
    """Compare quotes for opportunity"""
    try:
        comparisons = sourcing_system.compare_quotes(opportunity_id)
        return {
            'success': True,
            'quotes': comparisons
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=5006)
```

---

## 🎯 INTEGRATION WITH TRANSFORMATION FRAMEWORK

**The automation provides everything you need for transformation proposals:**

```
AUTOMATED SUB SOURCING
↓
• Finds 10-15 qualified subs (ratings, reviews, experience)
• Sends personalized outreach
• Tracks responses automatically
• Collects quotes and availability
↓
YOU MANUALLY:
• Review responses (5-10 minutes)
• Select 3 top candidates
• Request additional info if needed
↓
AUTOMATION CONTINUES:
• Generates Letter of Intent automatically
• Sends for e-signature
• Tracks performance after project starts
• Builds metrics library
↓
TRANSFORMATION WORKSHEET:
• Use sub's ratings/reviews as proof
• Use sub's response time as metric
• Use sub's track record as case study
↓
WRITE PROPOSAL:
• "Our subcontractor network maintained 4.8/5 average rating across 3 townships"
• "Response time averaged 4 hours (industry standard: 24-48 hours)"
• "Delivered 98.7% completion rate proven by 340+ Google reviews"
```

---

## ⏱️ TIME SAVINGS

**Manual Process:**
- Find subs: 2-3 hours
- Email each individually: 1-2 hours
- Track responses: 30 minutes
- Follow up: 1 hour
- **Total: 4-6 hours**

**Automated Process:**
- Click "Find Subs": 30 seconds
- System searches: 30 seconds (automatic)
- Review results: 5 minutes
- Click "Send Outreach": 15 seconds
- System sends emails: 15 seconds (automatic)
- System tracks responses: Automatic
- System sends follow-ups: Automatic
- Review quotes: 10 minutes
- **Total: 20 minutes of your time**

**Time saved: 4-5 hours per service bid!**

---

## 🚀 IMPLEMENTATION ROADMAP

### **Phase 1: Core Automation** (Week 1-2)
- [ ] Set up Google Maps API
- [ ] Set up Yelp API
- [ ] Create Airtable tables (SUBCONTRACTORS, SUB_OUTREACH_TRACKING)
- [ ] Build Python backend (`automated_sub_sourcing.py`)
- [ ] Test search and filtering logic
- [ ] Set up SendGrid for email

### **Phase 2: NEXUS Integration** (Week 3-4)
- [ ] Add "Subcontractors" tab to NEXUS frontend
- [ ] Build "Find Subs" interface
- [ ] Build "Send Outreach" interface
- [ ] Build "Compare Quotes" interface
- [ ] Test end-to-end workflow

### **Phase 3: Automated Follow-Ups** (Week 5)
- [ ] Set up cron job for daily follow-up checks
- [ ] Test follow-up email generation
- [ ] Monitor delivery and responses

### **Phase 4: Performance Tracking** (Week 6+)
- [ ] Build SUB_PERFORMANCE tracking
- [ ] Auto-populate metrics after project completion
- [ ] Generate transformation metrics library
- [ ] Feed into Transformation Worksheet automatically

---

## 📊 SUCCESS METRICS

**Track for automated system:**
- Subs found per search: Target 15-20
- Qualified subs: Target 10-15
- Emails sent: Target 100% of qualified
- Response rate: Target 30-40%
- Interested rate: Target 20-30%
- Quotes received: Target 3-5 per opportunity
- Time to complete: Target <20 minutes (vs 4-6 hours manual)

---

## 💡 FUTURE ENHANCEMENTS

### **Phase 5: AI-Powered Vetting**
- Use AI to read reviews and identify quality signals
- Auto-score subs based on review sentiment
- Prioritize outreach to highest-quality subs

### **Phase 6: Sub Portal**
- Create public portal where subs can register
- Subs can see available opportunities
- Subs can submit quotes directly
- Build internal marketplace

### **Phase 7: Integration with DocuSign**
- Auto-generate contracts
- E-signature workflow
- Track contract status

### **Phase 8: Performance Dashboards**
- Real-time sub performance tracking
- Quality scores and trends
- Recommendations for future projects

---

**YES - It's completely automatable! Just like Officer Outreach and Auto CapStat, we can automate sub sourcing end-to-end.**

---

**Last Updated:** February 4, 2026  
**Owner:** Dee Davis  
**Status:** Design complete, ready to build
