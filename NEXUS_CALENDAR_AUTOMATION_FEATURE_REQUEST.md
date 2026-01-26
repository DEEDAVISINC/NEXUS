# NEXUS CALENDAR AUTOMATION - FEATURE REQUEST
**Auto-Generate Calendar Files & Email Reminders**

**Date:** January 22, 2026  
**Priority:** HIGH  
**Effort:** LOW (2-3 days development)  
**Impact:** HIGH (saves hours per week, prevents missed deadlines)

---

## 🎯 PROBLEM STATEMENT:

**Current Pain Point:**
- User manually creates calendar events for every bid deadline
- No automatic reminders for quote deadlines
- Suppliers/subcontractors forget to respond to quote requests
- Risk of missing critical deadlines
- Time-consuming manual tracking

**What Happens Now:**
1. User finds opportunity in NEXUS
2. User manually adds deadline to calendar
3. User manually calculates quote request deadline
4. User manually follows up with suppliers
5. Risk of forgetting = missed opportunities

---

## ✅ PROPOSED SOLUTION:

### **FEATURE: Auto-Calendar Generation**

When a new opportunity is imported to NEXUS:
1. ✅ Extract deadline date automatically
2. ✅ Generate .ics calendar file with reminders
3. ✅ Email calendar file to user
4. ✅ Calculate supplier quote deadlines automatically
5. ✅ Send calendar links to suppliers in quote requests
6. ✅ Auto-follow-up if no response

---

## 📋 DETAILED FEATURES:

### **1. Opportunity Deadline Management**

**When opportunity is created/imported:**
- Parse deadline date from opportunity
- Calculate reminder schedule:
  - 7 days before
  - 3 days before
  - 1 day before (end of day)
  - Morning of deadline (9am)
  - 2 hours before deadline
- Generate .ics calendar file
- Email to user with subject: "📅 New Deadline: [Opportunity Name]"

**File format:**
```
madison_heights_lawn_deadline_2026-01-29.ics
```

---

### **2. Quote Request Deadline Calculator**

**Auto-calculate supplier deadlines:**
- Bid deadline - 3 days = Quote request deadline
- Bid deadline - 5 days = Send quote requests
- Bid deadline - 4 days = Send reminder to non-responders

**Example:**
- Bid due: Tuesday, Jan 28 @ 2pm
- Send quote requests: Thursday, Jan 23 (auto-scheduled)
- Quote deadline: Friday, Jan 24 @ 5pm (auto-calculated)
- Reminder: Thursday, Jan 24 @ 5pm (auto-sent if no response)

---

### **3. Supplier Calendar Link Generation**

**In every quote request email, include:**

```
╔════════════════════════════════════════╗
║  🚨 QUOTE DEADLINE                     ║
║  Friday, January 24, 2026              ║
║  5:00 PM EST (2 days from now)         ║
╚════════════════════════════════════════╝

📅 Add to your calendar: [Auto-generated Google Calendar link]
```

**Auto-generate link for:**
- Google Calendar
- Apple Calendar (.ics download)
- Outlook Calendar

---

### **4. Automated Follow-Up System**

**If supplier doesn't respond:**
- 24 hours before deadline: Send reminder email
- 12 hours before deadline: Flag in NEXUS dashboard
- 2 hours before deadline: SMS alert (optional)
- After deadline: Mark as "No Response" and suggest alternatives

---

### **5. Dashboard Calendar View**

**Add to NEXUS dashboard:**
- Calendar view of all upcoming deadlines
- Color coding:
  - 🔴 Red: < 3 days
  - 🟡 Yellow: 3-7 days
  - 🟢 Green: > 7 days
- Filter by:
  - Bid deadlines
  - Quote request deadlines
  - Delivery dates
  - Invoice due dates
  - Project milestones

---

## 🔧 TECHNICAL IMPLEMENTATION:

### **Backend (Python):**

```python
class CalendarGenerator:
    """Generate .ics calendar files for deadlines"""
    
    def generate_opportunity_calendar(self, opportunity_id):
        """Generate calendar file for opportunity deadline"""
        opp = self.airtable.get_record('GPSS OPPORTUNITIES', opportunity_id)
        fields = opp['fields']
        
        deadline = fields.get('Deadline')
        title = fields.get('Name')
        
        # Parse deadline
        deadline_dt = datetime.strptime(deadline, '%Y-%m-%d')
        
        # Calculate reminders
        reminders = [
            timedelta(days=7),
            timedelta(days=3),
            timedelta(days=1),
            timedelta(hours=2)
        ]
        
        # Generate .ics file
        calendar = self._create_ics(
            uid=f"{opportunity_id}@nexus.deedavis.biz",
            title=f"🚨 {title} - BID DEADLINE",
            start=deadline_dt,
            description=self._generate_description(fields),
            location=fields.get('Agency Name', ''),
            reminders=reminders
        )
        
        # Save to file
        filename = f"{title.lower().replace(' ', '_')}_{deadline}.ics"
        filepath = f"/calendars/{filename}"
        
        with open(filepath, 'w') as f:
            f.write(calendar)
        
        # Email to user
        self._email_calendar_file(filepath, fields)
        
        return filepath
    
    def calculate_quote_deadline(self, bid_deadline):
        """Calculate when supplier quotes are due"""
        bid_dt = datetime.strptime(bid_deadline, '%Y-%m-%d')
        quote_dt = bid_dt - timedelta(days=3)
        return quote_dt.strftime('%Y-%m-%d')
    
    def generate_google_calendar_link(self, title, date, time, description):
        """Generate Google Calendar add link"""
        # Convert to UTC
        start_dt = datetime.strptime(f"{date} {time}", '%Y-%m-%d %H:%M')
        start_utc = start_dt.strftime('%Y%m%dT%H%M%SZ')
        
        # End time (1 hour later)
        end_dt = start_dt + timedelta(hours=1)
        end_utc = end_dt.strftime('%Y%m%dT%H%M%SZ')
        
        # Build URL
        base_url = "https://calendar.google.com/calendar/render"
        params = {
            'action': 'TEMPLATE',
            'text': title,
            'dates': f"{start_utc}/{end_utc}",
            'details': description,
            'sf': 'true',
            'output': 'xml'
        }
        
        return f"{base_url}?{'&'.join([f'{k}={v}' for k, v in params.items()])}"
    
    def _create_ics(self, uid, title, start, description, location, reminders):
        """Create .ics file content"""
        ics = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//DEE DAVIS INC//NEXUS//EN
CALSCALE:GREGORIAN
METHOD:PUBLISH
BEGIN:VEVENT
UID:{uid}
DTSTAMP:{datetime.now().strftime('%Y%m%dT%H%M%SZ')}
DTSTART:{start.strftime('%Y%m%dT%H%M%SZ')}
DTEND:{(start + timedelta(hours=1)).strftime('%Y%m%dT%H%M%SZ')}
SUMMARY:{title}
DESCRIPTION:{description}
LOCATION:{location}
STATUS:CONFIRMED
SEQUENCE:0
"""
        
        # Add reminders
        for reminder in reminders:
            ics += f"""BEGIN:VALARM
TRIGGER:-P{reminder.days}D
ACTION:DISPLAY
DESCRIPTION:{title}
END:VALARM
"""
        
        ics += """END:VEVENT
END:VCALENDAR
"""
        return ics
```

---

### **Frontend (React/UI):**

```javascript
// Calendar button on opportunity page
<CalendarButton 
  opportunityId={opp.id}
  deadline={opp.deadline}
  onClick={() => downloadCalendarFile(opp.id)}
/>

// Dashboard calendar view
<CalendarView 
  opportunities={opportunities}
  filter={['deadlines', 'quotes', 'deliveries']}
  colorCode={true}
/>
```

---

### **Email Template Integration:**

```python
def send_quote_request_with_calendar(supplier_email, quote_data):
    """Send quote request email with calendar link"""
    
    # Calculate deadline
    bid_deadline = quote_data['bid_deadline']
    quote_deadline = calculate_quote_deadline(bid_deadline)
    
    # Generate calendar link
    calendar_link = generate_google_calendar_link(
        title=f"Quote Due: {quote_data['contract_name']}",
        date=quote_deadline,
        time="17:00",
        description=f"Submit quote to Dee Davis - {quote_data['contract_name']}"
    )
    
    # Build email
    email_body = f"""
Subject: URGENT: Quote Needed by {quote_deadline} - {quote_data['contract_name']}

Hi {quote_data['supplier_name']},

╔════════════════════════════════════════╗
║  🚨 QUOTE DEADLINE                     ║
║  {format_date(quote_deadline)}         ║
║  5:00 PM EST                           ║
╚════════════════════════════════════════╝

📅 Add to your calendar: {calendar_link}

{quote_data['email_body']}

⏰ CRITICAL TIMELINE:
- {format_date(quote_deadline)} @ 5pm: Your quote due
- {format_date(bid_deadline)}: We submit our bid

⚠️ If I don't receive your quote by {format_date(quote_deadline)} at 5pm,
I'll need to proceed with other suppliers.

Thanks!
Dee Davis
"""
    
    send_email(supplier_email, email_body)
    
    # Schedule follow-up reminder
    schedule_reminder(
        supplier_email,
        quote_deadline - timedelta(days=1),
        quote_data
    )
```

---

## 📊 DATA FLOW:

```
1. New Opportunity Created
   ↓
2. Extract Deadline Date
   ↓
3. Generate Calendar File (.ics)
   ↓
4. Email File to User
   ↓
5. Calculate Quote Request Deadlines
   ↓
6. Generate Calendar Links for Suppliers
   ↓
7. Send Quote Requests with Calendar Links
   ↓
8. Track Responses
   ↓
9. Auto Follow-Up if No Response
   ↓
10. Alert User of Approaching Deadlines
```

---

## 🎯 SUCCESS METRICS:

**Measure success by:**
- ✅ 0 missed bid deadlines (currently 2-3% miss rate)
- ✅ 50% increase in supplier response rate
- ✅ 80% reduction in manual calendar entry time
- ✅ 90% of users use calendar export feature
- ✅ User satisfaction: "Never miss a deadline again"

---

## 📅 IMPLEMENTATION TIMELINE:

### **Phase 1: Basic Calendar Generation (Week 1)**
- [ ] Backend: .ics file generation
- [ ] Backend: Email calendar files to user
- [ ] Frontend: Download calendar button on opportunity page
- [ ] Testing: Verify .ics imports correctly on Mac/Windows

### **Phase 2: Supplier Calendar Links (Week 2)**
- [ ] Backend: Google Calendar link generator
- [ ] Backend: Auto-calculate quote deadlines
- [ ] Email: Update quote request template with calendar links
- [ ] Testing: Verify links work across platforms

### **Phase 3: Auto Follow-Up System (Week 3)**
- [ ] Backend: Supplier response tracking
- [ ] Backend: Auto-reminder scheduling
- [ ] Email: Follow-up email templates
- [ ] Dashboard: Quote response status

### **Phase 4: Dashboard Calendar View (Week 4)**
- [ ] Frontend: Calendar component
- [ ] Frontend: Filter and color coding
- [ ] Frontend: Integrate with existing dashboard
- [ ] Testing: User acceptance testing

---

## 💰 COST/BENEFIT ANALYSIS:

### **Development Cost:**
- Developer time: 2-3 weeks (~80-120 hours)
- Cost: ~$8,000-$12,000

### **Benefits:**
- **Time Saved:** 2-3 hours per week per user
  - Manual calendar entry: 30 min/week
  - Follow-ups: 1 hour/week
  - Tracking: 1 hour/week
  - **Annual savings: ~120 hours = $6,000-$12,000**

- **Risk Reduction:**
  - Missed deadlines: 2-3% → 0%
  - Lost opportunities: ~$50K-$100K per year prevented

- **Increased Win Rate:**
  - Better supplier response: +20%
  - More complete bids: +10%
  - **Estimated additional revenue: $100K-$200K annually**

**ROI: 10-20X in first year**

---

## 🚀 FUTURE ENHANCEMENTS:

### **V2 Features:**
- SMS reminders for critical deadlines
- Slack/Teams integration
- Two-way calendar sync (iCal, Google Calendar API)
- AI-suggested optimal quote request timing
- Supplier performance tracking (who responds fastest)
- Automated proposal timeline generation (day-by-day tasks)

### **V3 Features:**
- Voice reminders (Alexa integration)
- Mobile app push notifications
- Automated calendar invite acceptance tracking
- Team calendar coordination
- Client-facing proposal status portal with countdown

---

## ✅ ACCEPTANCE CRITERIA:

**Feature is complete when:**
1. ✅ User clicks "Add to Calendar" button, downloads .ics file
2. ✅ .ics file imports successfully to Apple Calendar
3. ✅ .ics file imports successfully to Google Calendar
4. ✅ .ics file imports successfully to Outlook
5. ✅ Reminders trigger at correct times (7d, 3d, 1d, 2h)
6. ✅ Quote request emails include working calendar links
7. ✅ Suppliers can add to their calendar in 1 click
8. ✅ Auto-follow-up emails send 24h before deadline
9. ✅ Dashboard shows all upcoming deadlines
10. ✅ Zero missed deadlines in 30-day testing period

---

## 🛠️ TECHNICAL REQUIREMENTS:

**Dependencies:**
- Python `icalendar` library
- Email service (current SendGrid/Mailgun)
- Cron/scheduler for automated follow-ups
- Frontend calendar component (FullCalendar.js recommended)

**API Endpoints Needed:**
```
POST   /api/calendar/generate/{opportunity_id}
GET    /api/calendar/download/{file_id}
GET    /api/calendar/link/{opportunity_id}
POST   /api/quotes/send-request
GET    /api/calendar/dashboard
```

---

## 📝 USER STORIES:

**As a user, I want to:**
1. "Click one button and have my bid deadline in my calendar"
2. "Never manually calculate when to send quote requests"
3. "Know suppliers got my calendar reminder"
4. "See all my deadlines in one dashboard"
5. "Get reminded before I forget about a deadline"

**As a supplier, I want to:**
1. "Add this deadline to my calendar in one click"
2. "Know exactly when my quote is due"
3. "Get reminded so I don't forget to respond"

---

## 🎯 PRIORITY JUSTIFICATION:

**Why HIGH priority:**
1. **Prevents revenue loss** - Missed deadlines = lost opportunities ($50K-$100K/year)
2. **High user pain point** - Manually tracking deadlines is time-consuming
3. **Low development effort** - 2-3 weeks, standard libraries available
4. **High ROI** - 10-20X return in first year
5. **Competitive advantage** - Most competitors don't offer this
6. **User retention** - "Never miss a deadline" is a killer feature

---

## 📞 STAKEHOLDER APPROVAL:

**Approved by:** [Pending]  
**Date:** [Pending]  
**Budget Allocated:** [Pending]  
**Start Date:** [Pending]  
**Target Completion:** [Pending]

---

**Let's build this! This feature will save hours every week and prevent missed opportunities!** 🚀📅

---

Last updated: January 22, 2026
