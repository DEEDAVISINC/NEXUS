# 🔮 FORECAST → CAPABILITY STATEMENT → OFFICER OUTREACH INTEGRATION

**Complete workflow for proactive positioning on forecasted opportunities**

---

## 🎯 THE WORKFLOW

### **Correct Use Case:**

```
1. Federal Forecasts System discovers upcoming contract
   "NASA planning $5M IT contract, solicitation expected April 2026"
   ↓
2. You identify the contracting officer
   "John Smith, NASA Contracting Officer"
   ↓
3. Click "📧 Reach Out to Officer" button in Airtable
   ↓
4. System generates capability statement FOR THIS FORECAST
   - Tailored to this contract type
   - Highlights relevant experience
   - Shows you're qualified for THIS work
   ↓
5. System pre-fills email with:
   - Officer contact info
   - Introduction message about upcoming contract
   - Capability statement attached
   - Request to be considered when RFP drops
   ↓
6. You review, customize, and send
   ↓
7. System creates Officer Outreach Tracking record
   - Links to forecast
   - Tracks communication
   - Schedules follow-up
   ↓
8. When RFP actually drops → You're already known to buyer!
```

**This is RELATIONSHIP BUILDING before competition starts!**

---

## 📊 AIRTABLE INTEGRATION

### **1. Federal Forecasts Table - ADD THESE FIELDS:**

| Field Name | Type | Description |
|------------|------|-------------|
| **Contracting Officer** | Single line text | Name of the CO |
| **Officer Email** | Email | CO email address |
| **Officer Phone** | Phone | CO phone (optional) |
| **Officer Title** | Single line text | Their official title |
| **Outreach Status** | Single select | Not Contacted, Planned, Cap Statement Sent, Relationship Active, Meeting Scheduled |
| **Outreach Date** | Date | When you reached out |
| **Outreach Record** | Link to Officer Outreach Tracking | Links to outreach record |
| **Cap Statement Generated** | Checkbox | Has cap statement been generated for this forecast? |
| **Cap Statement File** | Attachment | Generated capability statement PDF |
| **Next Contact Date** | Date | When to follow up |
| **Relationship Notes** | Long text | Track all communication |

**Purpose:** Track proactive relationship building for each forecast

---

### **2. Officer Outreach Tracking Table - ADD THESE FIELDS:**

| Field Name | Type | Description |
|------------|------|-------------|
| **Outreach Type** | Single select | Options: **Forecast (Proactive)**, Closed Opportunity (Reactive) |
| **Related Forecast** | Link to Federal Forecasts | Link to forecast (for proactive outreach) |
| **Related Opportunity** | Link to GPSS OPPORTUNITIES | Link to opportunity (for reactive outreach) |
| **Forecast Value** | Lookup | From Related Forecast → Estimated Value |
| **Forecast Solicitation Date** | Lookup | From Related Forecast → Estimated Solicitation Date |

**Purpose:** Track BOTH types of outreach in one place

**Note:** The existing Officer Outreach Tracking table can handle both:
- **Forecast (Proactive):** Reaching out BEFORE RFP drops
- **Closed Opportunity (Reactive):** Reaching out AFTER bid closes

---

## 🔧 PYTHON INTEGRATION

### **New Module: `forecast_capstat_outreach.py`**

```python
"""
FORECAST CAPABILITY STATEMENT OUTREACH
Proactive relationship building for forecasted opportunities
"""

from datetime import datetime
from typing import Dict, Optional
from capability_statement_generator import CapabilityStatementGenerator
from contracting_officer_outreach import ContractingOfficerOutreachAgent


class ForecastCapStatOutreach:
    """
    Generate capability statements and outreach letters for forecasted opportunities
    Proactive positioning BEFORE RFP drops
    """
    
    def __init__(self, airtable_client):
        self.airtable = airtable_client
        self.capstat_gen = CapabilityStatementGenerator(
            airtable_api_key=os.environ['AIRTABLE_API_KEY'],
            base_id=os.environ['AIRTABLE_BASE_ID']
        )
        self.outreach_agent = ContractingOfficerOutreachAgent(airtable_client)
    
    def generate_forecast_capstat_and_outreach(self, forecast_record_id: str) -> Dict:
        """
        Complete workflow: Generate cap statement and outreach letter for forecast
        
        Args:
            forecast_record_id: Airtable record ID from Federal Forecasts table
        
        Returns:
            Dict with cap statement, outreach letter, and tracking info
        """
        
        # 1. Get forecast details
        forecast = self.airtable.get_record('Federal Forecasts', forecast_record_id)
        fields = forecast['fields']
        
        # 2. Generate capability statement TAILORED to this forecast
        capstat_result = self._generate_forecast_capstat(forecast)
        
        # 3. Generate introduction/outreach email
        outreach_letter = self._generate_forecast_outreach_letter(forecast, capstat_result)
        
        # 4. Create Officer Outreach Tracking record
        outreach_record_id = self._create_forecast_outreach_record(
            forecast, 
            capstat_result, 
            outreach_letter
        )
        
        # 5. Update forecast record
        self.airtable.update_record('Federal Forecasts', forecast_record_id, {
            'Cap Statement Generated': True,
            'Outreach Status': 'Cap Statement Generated - Ready to Send',
            'Outreach Record': [outreach_record_id],
            # Attach PDF if local file
            # 'Cap Statement File': [{'url': capstat_result['pdf_file']}]
        })
        
        return {
            'success': True,
            'forecast_id': forecast_record_id,
            'capstat_pdf': capstat_result['pdf_file'],
            'capstat_html': capstat_result['html_file'],
            'outreach_record_id': outreach_record_id,
            'outreach_letter': outreach_letter,
            'officer_email': fields.get('Officer Email'),
            'officer_name': fields.get('Contracting Officer'),
        }
    
    def _generate_forecast_capstat(self, forecast: Dict) -> Dict:
        """Generate capability statement tailored to forecast"""
        fields = forecast['fields']
        
        # Determine template based on forecast type
        template = 'default'
        if 'medical' in fields.get('Title', '').lower() or 'healthcare' in fields.get('Description', '').lower():
            template = 'va_medical'
        elif 'construction' in fields.get('Title', '').lower():
            template = 'construction'
        
        # Generate capability statement
        result = self.capstat_gen.generate_custom(
            client_name=fields.get('Agency', 'Federal Agency'),
            rfq_number=fields.get('Solicitation Number', 'FORECAST'),
            rfq_title=fields.get('Title', 'Upcoming Procurement'),
            template=template
        )
        
        return result
    
    def _generate_forecast_outreach_letter(self, forecast: Dict, capstat: Dict) -> Dict:
        """Generate introduction letter for forecasted opportunity"""
        fields = forecast['fields']
        
        officer_name = fields.get('Contracting Officer', 'Contracting Officer')
        officer_email = fields.get('Officer Email', '')
        agency = fields.get('Agency', 'Your Agency')
        title = fields.get('Title', 'Upcoming Procurement')
        estimated_date = fields.get('Estimated Solicitation Date', 'upcoming')
        estimated_value = fields.get('Estimated Value', 0)
        
        # Salutation
        if officer_name and officer_name != 'Contracting Officer':
            name_parts = officer_name.split()
            if len(name_parts) >= 2:
                salutation = f"Dear Ms./Mr. {name_parts[-1]},"
            else:
                salutation = f"Dear {officer_name},"
        else:
            salutation = "Dear Contracting Officer,"
        
        today = datetime.now().strftime("%B %d, %Y")
        
        letter = f"""**Date:** {today}

**To:** {officer_name}
**Email:** {officer_email}
**Re:** Upcoming Procurement - {title}
**Agency:** {agency}

---

{salutation}

I am writing to introduce **Dee Davis Inc.** regarding your agency's upcoming procurement for {title}, which we understand is planned for solicitation around {estimated_date}.

**Why We're Reaching Out Now:**

We believe in proactive engagement with contracting officers to ensure you're aware of qualified, diverse suppliers like ours BEFORE the solicitation period begins. This allows you to:
- Understand available diverse supplier options
- Plan for successful socioeconomic goal achievement
- Reduce time spent sourcing qualified vendors when the RFP drops

**About Dee Davis Inc.:**

Dee Davis Inc. is a certified **Economically Disadvantaged Woman-Owned Small Business (EDWOSB)** with proven experience delivering high-quality products and services to federal, state, and local government agencies.

**Our Certifications:**
- EDWOSB (Economically Disadvantaged Woman-Owned Small Business) - SBA Certified
- WOSB (Women-Owned Small Business) - SBA Certified  
- MBE (Minority Business Enterprise)
- WBE (Women Business Enterprise)

**Why Dee Davis Inc. for This Project:**

{fields.get('Fit Analysis', 'We have the capabilities and experience to successfully deliver on this requirement.')}

**What We Can Offer:**
- Competitive pricing through strategic supplier partnerships
- Proven track record of on-time delivery (98%+ performance rate)
- Socioeconomic credit for WOSB/EDWOSB contracting goals
- Professional, responsive service throughout contract period

**Our Request:**

We respectfully request the opportunity to:

1. **Be considered** when the solicitation is released
2. **Receive notification** when the RFP/RFQ is posted
3. **Schedule a brief call** to discuss your specific requirements (optional)
4. **Provide additional information** about our capabilities

**Enclosed:**

I have attached our **Capability Statement** which provides detailed information about our company, certifications, past performance, and core competencies relevant to this procurement.

**Next Steps:**

When the solicitation is released, we are prepared to:
- Submit a comprehensive, competitive proposal
- Provide product specifications and samples
- Demonstrate our supply chain capabilities
- Share references from similar government contracts

Thank you for considering Dee Davis Inc. for this upcoming procurement. We are genuinely excited about the opportunity to serve {agency} and contribute to your mission success.

Please feel free to contact me directly with any questions or to discuss this opportunity further.

**Contact Information:**

**Company:** Dee Davis Inc.
**Point of Contact:** Dee Davis, President
**Email:** info@deedavis.biz
**Phone:** 248-376-4550
**CAGE Code:** 8UMX3
**UEI/SAM Registration:** Active

We look forward to the opportunity to work with your agency!

Respectfully,

Dee Davis
President
Dee Davis Inc.

---

**Enclosure:** Company Capability Statement
"""
        
        return {
            'letter': letter,
            'recipient_name': officer_name,
            'recipient_email': officer_email,
            'subject_line': f"Introduction - Dee Davis Inc. - Upcoming Procurement: {title}",
            'forecast_title': title,
            'agency': agency,
        }
    
    def _create_forecast_outreach_record(
        self, 
        forecast: Dict, 
        capstat: Dict, 
        outreach_letter: Dict
    ) -> str:
        """Create Officer Outreach Tracking record for forecast outreach"""
        
        fields = forecast['fields']
        
        record = self.airtable.create_record('Officer Outreach Tracking', {
            'Outreach Type': 'Forecast (Proactive)',
            'Related Forecast': [forecast['id']],
            'Officer Name': outreach_letter['recipient_name'],
            'Officer Email': outreach_letter['recipient_email'],
            'Opportunity Title': f"FORECAST: {outreach_letter['forecast_title']}",
            'Agency': outreach_letter['agency'],
            'Letter Generated Date': datetime.now().isoformat(),
            'Status': 'Draft',
            'Letter Content': outreach_letter['letter'],
            'Subject Line': outreach_letter['subject_line'],
            'Tags': ['Forecast', 'Proactive'],
            'Priority': fields.get('Priority', 'Medium'),
            'Created By': 'NEXUS AI - Forecast Outreach',
        })
        
        return record['id']


# ========================================================================
# API HANDLER FOR FRONTEND/AIRTABLE BUTTON
# ========================================================================

def handle_forecast_capstat_outreach(forecast_id: str) -> Dict:
    """
    Handler that can be called from:
    - API endpoint
    - Airtable automation (via webhook)
    - Make.com webhook
    - Direct Python call
    
    Args:
        forecast_id: Federal Forecasts record ID
    
    Returns:
        Complete result with files, links, and next steps
    """
    from nexus_backend import AirtableClient
    
    airtable = AirtableClient()
    forecast_outreach = ForecastCapStatOutreach(airtable)
    
    result = forecast_outreach.generate_forecast_capstat_and_outreach(forecast_id)
    
    return {
        'success': result['success'],
        'message': f"Capability statement and outreach letter generated for forecast!",
        'capstat_pdf': result['capstat_pdf'],
        'capstat_html': result['capstat_html'],
        'outreach_record_id': result['outreach_record_id'],
        'officer_email': result['officer_email'],
        'officer_name': result['officer_name'],
        'next_steps': [
            f"1. Review capability statement: {result['capstat_pdf']}",
            f"2. Review outreach letter in Airtable (ID: {result['outreach_record_id']})",
            f"3. Customize if needed",
            f"4. Send email to {result['officer_email']}",
            "5. Update 'Date Sent' in Airtable",
            "6. Schedule follow-up in 2 weeks"
        ]
    }
```

---

## 🌐 API ENDPOINT

### **Add to `api_server.py`:**

```python
@app.post("/api/forecasts/<forecast_id>/generate-capstat-outreach")
def generate_forecast_capstat_outreach(forecast_id: str):
    """
    Generate capability statement and outreach letter for a forecast
    Triggered by button click in Airtable or NEXUS frontend
    """
    try:
        from forecast_capstat_outreach import handle_forecast_capstat_outreach
        
        result = handle_forecast_capstat_outreach(forecast_id)
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
```

**Endpoint URL:**
```
POST http://localhost:5000/api/forecasts/{forecast_id}/generate-capstat-outreach
```

---

## 🎨 AIRTABLE BUTTON AUTOMATION

### **Create Button in Federal Forecasts Table:**

**Button Field:** "📧 Reach Out to Officer"

**Automation Trigger:** When button clicked

**Automation Actions:**

1. **Run Script** (or webhook to Make.com):
```javascript
// Airtable script
let record = input.config();
let forecastId = record.id;

// Call NEXUS API
let response = await fetch(`http://your-server.com/api/forecasts/${forecastId}/generate-capstat-outreach`, {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    }
});

let result = await response.json();

if (result.success) {
    output.markdown(`✅ **Capability Statement Generated!**
    
📄 Cap Statement: ${result.capstat_pdf}
✉️ Outreach Record: ${result.outreach_record_id}
👤 Officer: ${result.officer_name}
📧 Email: ${result.officer_email}

**Next Steps:**
${result.next_steps.join('\n')}
    `);
} else {
    output.markdown(`❌ **Error:** ${result.error}`);
}
```

2. **Update Record:**
   - Set "Outreach Status" to "Cap Statement Sent"
   - Set "Outreach Date" to today

3. **Send Email Notification** to you:
```
Subject: ✅ Forecast Outreach Ready - {Forecast Title}

Capability statement and outreach letter generated!

Forecast: {Title}
Agency: {Agency}
Officer: {Contracting Officer}
Email: {Officer Email}

Review in Airtable:
{Link to Officer Outreach Tracking record}

Download Cap Statement:
{Link to PDF}

Ready to send!
```

---

## 📋 COMPLETE WORKFLOW EXAMPLE

### **Scenario: NASA IT Equipment Forecast**

**Step 1: Federal Forecasts discovers opportunity**
```
Title: NASA - IT Equipment Modernization
Agency: NASA Johnson Space Center
Estimated Value: $2.5M
Set-Aside: WOSB
Estimated Solicitation Date: April 15, 2026 (3 months away)
Contracting Officer: John Smith
Officer Email: john.smith@nasa.gov
Fit Score: 85/100
Priority: HIGH
```

**Step 2: You click "📧 Reach Out to Officer" button**

**Step 3: System generates:**
1. ✅ Capability statement PDF (tailored to IT equipment)
2. ✅ Outreach letter (proactive introduction)
3. ✅ Email pre-filled with officer contact
4. ✅ Officer Outreach Tracking record
5. ✅ Links everything together

**Step 4: You receive notification:**
```
✅ Forecast Outreach Ready - NASA IT Equipment Modernization

Capability statement generated!
Outreach letter drafted!

Review in Airtable → Officer Outreach Tracking
Download cap statement → /path/to/capstat_NASA_FORECAST_20260131.pdf

Officer: John Smith
Email: john.smith@nasa.gov

Ready to send!
```

**Step 5: You review and send:**
1. Open Officer Outreach Tracking record
2. Review letter (customize if needed)
3. Download capability statement PDF
4. Send email to john.smith@nasa.gov with cap statement attached
5. Update "Date Sent" in Airtable
6. System auto-schedules follow-up for 2 weeks

**Step 6: Follow-up (2 weeks later):**
- System reminds you to follow up
- Send brief follow-up email
- Track response in Airtable

**Step 7: When RFP drops (April 15, 2026):**
- John Smith already knows you!
- You're top of mind as qualified WOSB
- Submit bid with confidence
- Higher win probability!

---

## 🎯 DIFFERENCE FROM CLOSED OPPORTUNITY OUTREACH

### **Forecast (Proactive) Outreach:**
- **Timing:** 3-6 months BEFORE RFP drops
- **Goal:** Get known to buyer, position as qualified supplier
- **Message:** "We're aware of your upcoming procurement and want to introduce ourselves"
- **Attachment:** Capability statement (general qualifications)
- **Outcome:** Buyer knows you exist, considers you when RFP drops

### **Closed Opportunity (Reactive) Outreach:**
- **Timing:** AFTER bid closes (you missed it)
- **Goal:** Get on vendor list for FUTURE similar opportunities
- **Message:** "We saw your recent solicitation, want to be considered next time"
- **Attachment:** Capability statement + intro letter
- **Outcome:** Added to vendor database, notified of future similar bids

**BOTH are valuable! But forecast outreach is PROACTIVE positioning.**

---

## 🚀 IMPLEMENTATION CHECKLIST

### **Phase 1: Airtable Setup (15 minutes)**

- [ ] Add officer contact fields to Federal Forecasts table
- [ ] Add outreach tracking fields to Federal Forecasts
- [ ] Add "Outreach Type" field to Officer Outreach Tracking
- [ ] Add "Related Forecast" link field to Officer Outreach Tracking
- [ ] Create "📧 Reach Out to Officer" button in Federal Forecasts

### **Phase 2: Code Integration (30 minutes)**

- [ ] Create `forecast_capstat_outreach.py` module
- [ ] Add API endpoint to `api_server.py`
- [ ] Test capability statement generation from forecast
- [ ] Test outreach letter generation
- [ ] Test complete workflow end-to-end

### **Phase 3: Automation Setup (20 minutes)**

- [ ] Create Airtable button automation
- [ ] Set up webhook to API (if using Make.com)
- [ ] Create email notification template
- [ ] Test button click → full workflow
- [ ] Verify all records created correctly

### **Phase 4: Testing (15 minutes)**

- [ ] Test with 1 high-priority forecast
- [ ] Review generated capability statement
- [ ] Review generated outreach letter
- [ ] Verify links between tables
- [ ] Send test outreach email

### **Total Time: 80 minutes (1 hour 20 minutes)**

---

## ✅ SUCCESS METRICS

**After implementing this system, track:**

| Metric | Target | Current |
|--------|--------|---------|
| Forecasts with officer contact info | 60%+ | - |
| Proactive outreach sent per month | 10-20 | - |
| Officer response rate | 20-30% | - |
| Relationships built before RFP drops | 5-10/month | - |
| Win rate on forecast-driven bids | 30%+ | - |
| Time savings (vs. reactive bidding) | 10+ hours/month | - |

---

## 💡 PRO TIPS

### **When to Use Forecast Outreach:**

✅ **YES - Use for:**
- High-priority forecasts (fit score ≥ 80)
- WOSB/EDWOSB set-asides
- Forecasts 30-90 days before solicitation
- Known contracting officers
- Agencies you want to build relationships with

❌ **NO - Don't use for:**
- Low-fit forecasts (score < 70)
- Forecasts >6 months out (too early)
- Forecasts <2 weeks out (too late, they're busy)
- No contracting officer identified
- Generic "vendor registration" requests

### **Email Best Practices:**

1. **Keep it brief** - Officers are busy
2. **Lead with value** - How you help them achieve goals
3. **Mention EDWOSB early** - Socioeconomic credit matters
4. **Attach cap statement** - Don't make them ask
5. **One clear ask** - "Consider us when RFP drops"
6. **Follow up once** - After 2 weeks, then move on

### **Timing Strategy:**

- **90-60 days before solicitation:** Perfect time to reach out
- **60-30 days before:** Still good, they're planning
- **30-14 days before:** Okay, but they're busy
- **< 14 days:** Too late, they're finalizing solicitation
- **>120 days:** Too early, plans may change

---

## 🎊 WHAT YOU NOW HAVE

**Complete Proactive Positioning System:**

1. ✅ Federal Forecasts discovers upcoming contracts
2. ✅ One-click capability statement generation
3. ✅ Pre-filled officer outreach emails
4. ✅ Complete tracking and follow-up
5. ✅ Relationship building BEFORE competition starts
6. ✅ Higher win rates from preparation

**You're now competing like large contractors - with advance intelligence and proactive relationship building!**

---

*Created: January 31, 2026*  
*System: Forecast Capability Statement Outreach Integration*  
*Status: Design Complete - Ready to Build*
