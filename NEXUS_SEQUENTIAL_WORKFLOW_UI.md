# 🎯 NEXUS Sequential Workflow UI Design

**Workflow-Driven Dashboard: Complete Steps in the Right Order**

---

## PART 1: The "Deadlines" Box (Sequential Workflow)

### ✅ What You Should See:

```
┌─────────────────────────────────────────────────────────────────┐
│ ⏰ DEADLINES & WORKFLOW STEPS                                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ CPS ENERGY - Industrial Supplies                                │
│ Final Deadline: February 5, 2026 (10 days)                     │
│ ├─ ✅ 1. Opportunity Added (Jan 20)                            │
│ ├─ ✅ 2. Suppliers Identified (Jan 21)                         │
│ ├─ ✅ 3. Quotes Requested (Jan 22) - 5 sent                    │
│ ├─ 🔄 4. Quotes Received (Jan 26) - 3 of 5 ⏳                  │
│ │      → Waiting on: Grainger, Sunbelt Mill                   │
│ │      → [Send Follow-up Now]                                 │
│ ├─ 🔒 5. Price Bid (LOCKED until 4 complete)                   │
│ ├─ 🔒 6. Generate Proposal (LOCKED until 5 complete)           │
│ ├─ 🔒 7. Final Review (LOCKED until 6 complete)                │
│ └─ 🔒 8. Submit Bid (LOCKED until 7 complete)                  │
│                                                                 │
│ STERLING HEIGHTS - Aggregates                                  │
│ Final Deadline: January 28, 2026 (2 days) ⚠️ URGENT           │
│ ├─ ✅ 1. Opportunity Added (Jan 24)                            │
│ ├─ ✅ 2. Suppliers Identified (Jan 24)                         │
│ ├─ ✅ 3. Quotes Requested (Jan 25) - 3 sent                    │
│ ├─ ✅ 4. Quotes Received (Jan 26) - 3 of 3 ✅                  │
│ ├─ ▶️ 5. Price Bid (READY - DO NOW!) [Start Pricing]          │
│ ├─ 🔒 6. Generate Proposal (LOCKED until 5 complete)           │
│ ├─ 🔒 7. Final Review (LOCKED until 6 complete)                │
│ └─ 🔒 8. Submit Bid (LOCKED until 7 complete)                  │
│                                                                 │
│ OAKLAND COUNTY - Body Bags                                     │
│ Final Deadline: February 10, 2026 (15 days)                    │
│ ├─ ✅ 1. Opportunity Added (Jan 26)                            │
│ ├─ ▶️ 2. Review Specs (READY - DO NOW!) [Review]              │
│ ├─ 🔒 3. Identify Suppliers (LOCKED until 2 complete)          │
│ ├─ 🔒 4. Request Quotes (LOCKED until 3 complete)              │
│ ├─ 🔒 5. Receive Quotes (LOCKED until 4 complete)              │
│ ├─ 🔒 6. Price Bid (LOCKED until 5 complete)                   │
│ ├─ 🔒 7. Generate Proposal (LOCKED until 6 complete)           │
│ └─ 🔒 8. Submit Bid (LOCKED until 7 complete)                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## PART 2: Sequential Workflow Logic (Can't Skip Steps!)

### The Rules:

**✅ = Completed (Green check)**
- Step is done
- Can proceed to next step

**▶️ = READY (Orange play button)**
- All prerequisites complete
- This step can be started NOW
- Action button enabled

**🔄 = IN PROGRESS (Blue spinner)**
- Step is active but not complete
- Waiting on something (quotes, delivery, etc.)
- Shows status and what's pending

**🔒 = LOCKED (Gray lock)**
- Prerequisites not met
- Cannot start this step yet
- Button is disabled/grayed out

**⚠️ = URGENT (Red warning)**
- Deadline within 3 days
- Highlighted in red
- Top of the list

---

### Example Workflow States:

#### State 1: Just Started
```
CPS ENERGY
├─ ✅ 1. Opportunity Added
├─ ▶️ 2. Review Specs [Review Now]  ← CAN DO THIS
├─ 🔒 3. Identify Suppliers         ← LOCKED (can't skip step 2)
├─ 🔒 4. Request Quotes
└─ 🔒 5. Price Bid
```

**You click "Review Now":**
- Opens opportunity details
- You read specs
- You click "Mark as Reviewed"
- Status changes to ✅

#### State 2: After Review
```
CPS ENERGY
├─ ✅ 1. Opportunity Added
├─ ✅ 2. Review Specs
├─ ▶️ 3. Identify Suppliers [Find Suppliers]  ← NOW UNLOCKED
├─ 🔒 4. Request Quotes
└─ 🔒 5. Price Bid
```

#### State 3: Waiting on Quotes
```
CPS ENERGY
├─ ✅ 1. Opportunity Added
├─ ✅ 2. Review Specs
├─ ✅ 3. Identify Suppliers (5 suppliers)
├─ ✅ 4. Quotes Requested (5 sent on Jan 22)
├─ 🔄 5. Receive Quotes (3 of 5) ⏳          ← WAITING
│      → Received: Fastenal, Detroit Salt, Cut King
│      → Waiting: Grainger (sent follow-up), Sunbelt Mill
│      → [Send Follow-up] [Proceed with 3 Quotes]
├─ 🔒 6. Price Bid                            ← LOCKED until quotes complete
└─ 🔒 7. Submit Bid
```

**Two options:**
1. Wait for all 5 quotes (preferred)
2. Click "Proceed with 3 Quotes" (override, but system warns you)

#### State 4: Ready to Price
```
CPS ENERGY
├─ ✅ 1. Opportunity Added
├─ ✅ 2. Review Specs
├─ ✅ 3. Identify Suppliers
├─ ✅ 4. Quotes Requested
├─ ✅ 5. Quotes Received (5 of 5) ✅
├─ ▶️ 6. Price Bid [Start Pricing]           ← READY!
├─ 🔒 7. Generate Proposal
└─ 🔒 8. Submit Bid
```

---

## PART 3: Email Notification Button

### Location: Top Right of Dashboard

```
┌─────────────────────────────────────────────────────────────────┐
│ NEXUS Command Center          📧 bids.deedavisinc@gmail.com 🔔 │
│                                  [3 New] [Check Now]            │
└─────────────────────────────────────────────────────────────────┘
```

### Email Notification Button Design:

```
┌─────────────────────────────────────┐
│  📧 bids.deedavisinc@gmail.com      │
│  ────────────────────────────────   │
│  🔔 3 New Emails                    │
│  [Check Inbox Now]                  │
│                                     │
│  Last Checked: 2 min ago            │
│  Auto-check: Every 15 min ✅        │
│                                     │
│  Recent Activity:                   │
│  • New solicitation (5 min ago)    │
│  • Supplier quote (12 min ago)     │
│  • Client email (45 min ago)       │
│                                     │
│  [View All Email Activity]          │
│  [Email Settings]                   │
└─────────────────────────────────────┘
```

### Notification States:

**No New Emails:**
```
📧 bids.deedavisinc@gmail.com ✅
   Last checked: 2 min ago
```

**New Emails (Not Urgent):**
```
📧 bids.deedavisinc@gmail.com 🔵 (3)
   3 new emails
```

**New Emails (Urgent - Needs Action):**
```
📧 bids.deedavisinc@gmail.com 🔴 (5)
   5 new • 2 need review!
   [Review Now]
```

**Checking Now:**
```
📧 bids.deedavisinc@gmail.com ⏳
   Checking inbox...
```

---

## PART 4: Full Dashboard Layout (Workflow-Driven)

```
┌─────────────────────────────────────────────────────────────────┐
│ NEXUS Command Center - Monday, Jan 26, 2026                    │
│                 📧 bids.deedavisinc@gmail.com 🔔 (3)            │
│                 [Check Now]  📆 [Export All to Calendar]        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ 🔥 URGENT ACTION REQUIRED                                       │
│ ├─ Sterling Heights: Price bid NOW (due in 2 days) [START]    │
│ └─ Grainger payment: $42K due today [APPROVE]                 │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ ⏰ DEADLINES & WORKFLOW STEPS (3 Active Bids)                  │
│                                                                 │
│ ⚠️ STERLING HEIGHTS - Aggregates (2 days)                      │
│ Final: Jan 28, 2026 @ 2:00 PM  📆 [Add to Calendar]           │
│ ├─ ✅ Steps 1-4 complete                                       │
│ ├─ ▶️ 5. Price Bid (READY) [Start Pricing]                    │
│ └─ 🔒 6-8 Locked until pricing complete                        │
│                                                                 │
│ CPS ENERGY - Industrial Supplies (10 days)                     │
│ Final: Feb 5, 2026 @ 5:00 PM  📆 [Add to Calendar]            │
│ ├─ ✅ Steps 1-3 complete                                       │
│ ├─ 🔄 4. Quotes: 3 of 5 received ⏳                            │
│ │      → [Send Follow-up] [Proceed with 3]                    │
│ └─ 🔒 5-8 Locked until quotes complete                         │
│                                                                 │
│ OAKLAND COUNTY - Body Bags (15 days)                           │
│ Final: Feb 10, 2026 @ 2:00 PM  📆 [Add to Calendar]           │
│ ├─ ✅ 1. Opportunity Added                                     │
│ ├─ ▶️ 2. Review Specs (READY) [Review]                        │
│ └─ 🔒 3-8 Locked until review complete                         │
│                                                                 │
│ 📆 [Export All Deadlines to Calendar]  [View Calendar]         │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ ✅ PENDING APPROVALS (2)                                        │
│ ├─ Grainger payment: $42K for CPS Energy [Review & Approve]   │
│ └─ Invoice to Canton: $25K (INV-2026-008) [Review & Send]     │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ 🏆 ACTIVE CONTRACTS (Post-Award)                               │
│                                                                 │
│ Canton Water Infrastructure                                    │
│ ├─ Month 3 of 12 • $45K/month                                 │
│ ├─ ▶️ Next Delivery: Feb 1 (6 days) [Schedule]                │
│ └─ [Track] [Invoice] [Contact Client]                         │
│                                                                 │
│ Detroit Water Treatment                                        │
│ ├─ Month 7 of 24 • $18K/month                                 │
│ ├─ ✅ Delivered on time (Jan 15)                              │
│ └─ 🔄 Invoice sent (Jan 20) - Payment due Feb 5               │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ 📊 SYSTEM METRICS (Today)                                       │
│ ├─ 📧 Email: 8 sent, 3 received, 2 need review                │
│ ├─ 💰 Revenue: $250K this month (28% margin)                  │
│ ├─ 🎯 Active Bids: 3 in progress                              │
│ ├─ 📆 Upcoming: 7 deadlines this week                         │
│ └─ ⚡ System Health: All systems online ✅                     │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ 📆 THIS WEEK'S CALENDAR (Quick View)                           │
│                                                                 │
│ TODAY (Mon Jan 26)                                             │
│ • 9:00 AM - Notary appointment (Madison Heights docs)         │
│ • 3:00 PM - Grainger payment due                              │
│                                                                 │
│ TOMORROW (Tue Jan 27)                                          │
│ • 1:00 PM - Hand deliver Madison Heights bid 🚨               │
│ • 5:00 PM - CPS Energy deadline 🚨                            │
│                                                                 │
│ Wed Jan 28                                                     │
│ • 2:00 PM - Sterling Heights deadline 🚨                      │
│                                                                 │
│ Thu Jan 29                                                     │
│ • All day - Follow up with suppliers                          │
│                                                                 │
│ [View Full Calendar] [Export All to .ics]                      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## PART 5: Workflow Step Definitions

### Pre-Award Workflow (Bidding):

```
1. ✅ Opportunity Added
   - Email received or manually added
   - PDF downloaded
   - Airtable record created

2. ▶️ Review Specs
   - Read solicitation document
   - Verify you can fulfill requirements
   - Check certifications needed
   - Mark as "Reviewed" or "Skip"

3. 🔒 Identify Suppliers
   - Search Airtable for matching suppliers
   - Add new suppliers if needed
   - Select 3-5 suppliers to contact

4. 🔒 Request Quotes
   - Generate quote request PDFs
   - Send via email/fax
   - Log sent date/time
   - Schedule follow-ups

5. 🔄 Receive Quotes
   - Monitor email for responses
   - Log quotes in Airtable
   - Track: X of Y received
   - Send follow-ups if needed

6. 🔒 Price Bid
   - Compare supplier quotes
   - Calculate your markup
   - Determine final bid price
   - Complete pricing worksheet

7. 🔒 Generate Proposal
   - Create capability statement (if needed)
   - Fill out bid forms
   - Attach required documents
   - Generate final proposal PDF

8. 🔒 Final Review
   - Review all forms for accuracy
   - Check calculations
   - Verify all requirements met
   - Get approval to submit

9. 🔒 Submit Bid
   - Upload to portal or email
   - Confirm submission received
   - Log submission timestamp
   - Set reminder for award date
```

### Post-Award Workflow (Contract Management):

```
1. ✅ Contract Awarded
   - Award notification received
   - Contract created in CCC
   - Suppliers notified

2. ▶️ Order from Suppliers
   - Send purchase orders
   - Confirm delivery dates
   - Log PO numbers

3. 🔄 Track Delivery
   - Monitor supplier shipments
   - Update delivery status
   - Alert for delays

4. 🔒 Receive & Inspect
   - Confirm receipt
   - Verify quantities/quality
   - Log receipt date

5. 🔒 Deliver to Client
   - Coordinate delivery
   - Client signs receipt
   - Log delivery date

6. 🔒 Generate Invoice
   - Create invoice PDF
   - Review for accuracy
   - Attach delivery receipts

7. 🔒 Send Invoice (APPROVAL REQUIRED)
   - YOU review invoice
   - YOU click "Send to Client"
   - System emails invoice
   - Logs sent timestamp

8. 🔄 Track Payment
   - Monitor for payment
   - Send reminder at Net 25
   - Alert for overdue

9. ✅ Payment Received
   - Log payment date
   - Update financial records
   - Close contract cycle
```

---

## PART 6: Button States & User Experience

### Button States in Workflow:

**1. READY (Can do now):**
```html
<button class="bg-green-600 hover:bg-green-700">
  ▶️ Start Pricing
</button>
```

**2. LOCKED (Prerequisites not met):**
```html
<button class="bg-gray-400 cursor-not-allowed" disabled>
  🔒 Start Pricing (Complete quotes first)
</button>
```

**3. IN PROGRESS (Started but not done):**
```html
<button class="bg-blue-600 hover:bg-blue-700">
  🔄 Continue Pricing (3 of 10 items priced)
</button>
```

**4. NEEDS REVIEW (Waiting on you):**
```html
<button class="bg-orange-600 hover:bg-orange-700">
  ⚠️ Review & Approve Payment ($42K)
</button>
```

**5. URGENT (Deadline soon):**
```html
<button class="bg-red-600 hover:bg-red-700 animate-pulse">
  🔥 URGENT: Submit Bid (Due in 4 hours!)
</button>
```

---

## PART 7: Email Notification Button (Detailed)

### Top Right Corner of Dashboard:

```javascript
// Email Notification Component
<div className="email-notification">
  {/* Compact View (Default) */}
  <button 
    onClick={toggleEmailPanel}
    className={`relative px-4 py-2 rounded-lg ${
      hasUrgent ? 'bg-red-600' : 
      hasNew ? 'bg-blue-600' : 
      'bg-gray-700'
    }`}
  >
    📧 bids.deedavisinc@gmail.com
    
    {newCount > 0 && (
      <span className="absolute -top-2 -right-2 bg-red-500 rounded-full px-2 py-1 text-xs">
        {newCount}
      </span>
    )}
  </button>

  {/* Expanded Panel (Click to open) */}
  {emailPanelOpen && (
    <div className="absolute top-16 right-4 w-96 bg-gray-800 rounded-lg shadow-xl p-4">
      
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-bold">📧 Email Activity</h3>
        <button onClick={checkEmailNow} className="bg-blue-600 px-3 py-1 rounded">
          Check Now
        </button>
      </div>

      <div className="mb-4">
        <p className="text-sm text-gray-400">
          Last checked: {lastChecked} ago
        </p>
        <p className="text-sm text-gray-400">
          Auto-check: Every 15 minutes ✅
        </p>
      </div>

      {/* New Emails (Need Action) */}
      {urgentEmails.length > 0 && (
        <div className="mb-4">
          <h4 className="font-bold text-red-400 mb-2">⚠️ Needs Your Review ({urgentEmails.length})</h4>
          {urgentEmails.map(email => (
            <div key={email.id} className="bg-red-900/30 p-3 rounded mb-2">
              <p className="font-semibold">{email.subject}</p>
              <p className="text-sm text-gray-400">From: {email.from}</p>
              <button className="mt-2 bg-red-600 px-3 py-1 rounded text-sm">
                Review Now
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Recent Activity (Auto-processed) */}
      <div className="mb-4">
        <h4 className="font-bold text-green-400 mb-2">✅ Recently Processed ({processedCount})</h4>
        {recentProcessed.map(item => (
          <div key={item.id} className="bg-gray-700 p-2 rounded mb-2 text-sm">
            <p>{item.action}</p>
            <p className="text-gray-400">{item.time} ago</p>
          </div>
        ))}
      </div>

      {/* Email Stats */}
      <div className="border-t border-gray-700 pt-3">
        <h4 className="font-bold mb-2">📊 Today's Email Activity</h4>
        <div className="grid grid-cols-2 gap-2 text-sm">
          <div>
            <span className="text-gray-400">Sent:</span>
            <span className="ml-2 font-bold">{sentCount}</span>
          </div>
          <div>
            <span className="text-gray-400">Received:</span>
            <span className="ml-2 font-bold">{receivedCount}</span>
          </div>
          <div>
            <span className="text-gray-400">Processed:</span>
            <span className="ml-2 font-bold text-green-400">{processedCount}</span>
          </div>
          <div>
            <span className="text-gray-400">Pending:</span>
            <span className="ml-2 font-bold text-orange-400">{pendingCount}</span>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="mt-4 flex gap-2">
        <button className="flex-1 bg-gray-700 px-3 py-2 rounded text-sm">
          View All Emails
        </button>
        <button className="flex-1 bg-gray-700 px-3 py-2 rounded text-sm">
          Email Settings
        </button>
      </div>

    </div>
  )}
</div>
```

---

## PART 8: Sequential Workflow Enforcement

### Backend Logic:

```python
class WorkflowManager:
    """Enforces sequential workflow steps"""
    
    BIDDING_WORKFLOW = [
        "opportunity_added",
        "specs_reviewed",
        "suppliers_identified",
        "quotes_requested",
        "quotes_received",
        "bid_priced",
        "proposal_generated",
        "final_review",
        "bid_submitted"
    ]
    
    def can_start_step(self, opportunity_id, step):
        """Check if prerequisites are met"""
        current_progress = self.get_progress(opportunity_id)
        step_index = self.BIDDING_WORKFLOW.index(step)
        
        # Check all previous steps are complete
        for i in range(step_index):
            prev_step = self.BIDDING_WORKFLOW[i]
            if not current_progress.get(prev_step, {}).get('completed'):
                return {
                    'can_start': False,
                    'reason': f'Must complete "{prev_step}" first',
                    'next_step': prev_step
                }
        
        return {'can_start': True}
    
    def start_step(self, opportunity_id, step):
        """Start a workflow step"""
        # Check prerequisites
        check = self.can_start_step(opportunity_id, step)
        if not check['can_start']:
            raise WorkflowError(check['reason'])
        
        # Mark step as in progress
        self.airtable.update_opportunity(opportunity_id, {
            f'workflow_{step}_status': 'in_progress',
            f'workflow_{step}_started': datetime.now().isoformat()
        })
    
    def complete_step(self, opportunity_id, step):
        """Mark step as complete"""
        self.airtable.update_opportunity(opportunity_id, {
            f'workflow_{step}_status': 'completed',
            f'workflow_{step}_completed': datetime.now().isoformat()
        })
        
        # Check what's next
        next_step = self.get_next_available_step(opportunity_id)
        return {
            'completed': step,
            'next_step': next_step
        }
```

---

## PART 9: Calendar Integration (Already Built!)

### 📆 Calendar Export Features

**Already Implemented in NEXUS:**

```javascript
// Export ALL tasks/deadlines to calendar
exportAllTasksToCalendar()
  → Downloads: NEXUS_All_Tasks.ics
  → Includes: All ATLAS tasks with due dates
  → Auto-sync to Apple Calendar, Google Calendar, Outlook
```

### Calendar Button Locations:

**1. Top Right - Quick Action:**
```
NEXUS Command Center
   📆 [Export All to Calendar]
```

**2. Each Opportunity - Individual Export:**
```
CPS ENERGY - Industrial Supplies
Final: Feb 5, 2026 @ 5:00 PM  📆 [Add to Calendar]
```

**3. Deadlines Box - Batch Export:**
```
⏰ DEADLINES & WORKFLOW STEPS
   📆 [Export All Deadlines to Calendar]
```

**4. Calendar Widget - Dashboard View:**
```
📆 THIS WEEK'S CALENDAR
   [View Full Calendar] [Export All to .ics]
```

---

### What Gets Exported:

**When you click "Add to Calendar" on an opportunity:**

Generates `.ics` file with:
- ✅ Deadline date and time
- ✅ Opportunity name and agency
- ✅ Full description with specs
- ✅ Auto-reminders:
  - 7 days before
  - 3 days before
  - 1 day before at 5pm
  - Morning of at 9am
  - 2 hours before deadline

**Example filename:**
```
cps_energy_industrial_supplies_2026-02-05.ics
```

**When you click "Export All Deadlines":**

Generates single `.ics` file with:
- ✅ All active bid deadlines
- ✅ All quote request deadlines
- ✅ All delivery dates
- ✅ All payment due dates
- ✅ All reminders

**Example filename:**
```
NEXUS_All_Deadlines_2026-01-26.ics
```

---

### Calendar Integration with Workflow:

**Auto-generate calendar events when:**

```
1. New opportunity created
   → Generate .ics with bid deadline
   → Auto-reminders set

2. Quote requested from supplier
   → Generate .ics with quote deadline
   → Email .ics to supplier
   → Calendar link in email

3. Contract awarded
   → Generate .ics with delivery dates
   → Generate .ics with payment dates
   → Monthly milestone reminders

4. Invoice sent
   → Generate .ics with payment due date
   → Reminder at Net 25 days
   → Alert at Net 35 (overdue)
```

---

### Supplier Calendar Links (In Quote Requests):

**When you send a quote request, email includes:**

```
╔════════════════════════════════════════╗
║  🚨 QUOTE DEADLINE                     ║
║  Friday, February 2, 2026              ║
║  5:00 PM EST (3 days from now)         ║
╚════════════════════════════════════════╝

📅 Add to your calendar:
   → Google Calendar: [One-click link]
   → Apple Calendar: [Download .ics]
   → Outlook: [Download .ics]
```

**Suppliers click once → Deadline in their calendar!**

---

### Calendar Dashboard Widget:

**Shows THIS WEEK at-a-glance:**

```
📆 THIS WEEK'S CALENDAR

TODAY (Mon Jan 26)
• 9:00 AM - Notary appointment
• 3:00 PM - Grainger payment due

TOMORROW (Tue Jan 27) 🚨
• 1:00 PM - Hand deliver Madison Heights
• 5:00 PM - CPS Energy deadline

Wed Jan 28 🚨
• 2:00 PM - Sterling Heights deadline

Thu Jan 29
• All day - Follow up with suppliers

Fri Jan 30
• 5:00 PM - Quote collection deadline

[View Full Calendar] [Export to .ics]
```

**Color coding:**
- 🔴 Red: Urgent (< 3 days)
- 🟡 Yellow: Soon (3-7 days)
- 🟢 Green: Plenty of time (> 7 days)

---

### Calendar Sync Across All Devices:

**Once you import .ics file:**

- ✅ Shows on Mac
- ✅ Shows on iPhone
- ✅ Shows on iPad
- ✅ Shows on Apple Watch
- ✅ Shows on Windows/Outlook
- ✅ Shows on Android/Google Calendar
- ✅ Notifications on ALL devices

**Never miss a deadline!**

---

### Auto-Calendar Generation Logic:

```python
class CalendarManager:
    """Handles all calendar generation and exports"""
    
    def generate_opportunity_calendar(self, opportunity_id):
        """Generate .ics for single opportunity"""
        opp = self.airtable.get_opportunity(opportunity_id)
        
        # Create calendar event
        event = {
            'uid': f"{opportunity_id}@nexus.deedavis.biz",
            'title': f"🚨 {opp['Name']} - BID DEADLINE",
            'start': opp['Deadline'],
            'description': self._build_description(opp),
            'location': opp['Agency Name'],
            'reminders': [
                {'days': 7, 'message': '1 week until deadline'},
                {'days': 3, 'message': '3 days - start final review'},
                {'days': 1, 'message': 'Tomorrow - final prep'},
                {'hours': 2, 'message': '2 hours - submit NOW'}
            ]
        }
        
        # Generate .ics file
        ics_content = self._create_ics(event)
        filename = f"{opp['Name'].lower().replace(' ', '_')}_{opp['Deadline']}.ics"
        
        return {
            'filename': filename,
            'content': ics_content,
            'download_url': f"/api/calendar/download/{filename}"
        }
    
    def generate_all_deadlines_calendar(self):
        """Generate .ics with ALL active deadlines"""
        opportunities = self.airtable.get_active_opportunities()
        events = []
        
        for opp in opportunities:
            # Add bid deadline
            events.append(self._create_event(opp, 'bid_deadline'))
            
            # Add quote deadlines
            quote_deadline = self._calculate_quote_deadline(opp['Deadline'])
            events.append(self._create_event(opp, 'quote_deadline', quote_deadline))
        
        # Get contracts
        contracts = self.airtable.get_active_contracts()
        for contract in contracts:
            # Add delivery dates
            events.append(self._create_event(contract, 'delivery'))
            
            # Add payment dates
            events.append(self._create_event(contract, 'payment_due'))
        
        # Generate combined .ics
        ics_content = self._create_ics_multi(events)
        filename = f"NEXUS_All_Deadlines_{datetime.now().strftime('%Y-%m-%d')}.ics"
        
        return {
            'filename': filename,
            'content': ics_content,
            'event_count': len(events)
        }
    
    def generate_supplier_calendar_link(self, quote_request_id):
        """Generate Google Calendar link for suppliers"""
        quote = self.airtable.get_quote_request(quote_request_id)
        
        # Build Google Calendar URL
        title = f"Quote Due: {quote['Project_Name']}"
        start = quote['Quote_Deadline']
        description = f"Submit quote to Dee Davis Inc. - {quote['Project_Name']}"
        
        google_url = self._build_google_calendar_url(title, start, description)
        
        # Also generate .ics for Apple/Outlook users
        ics_content = self._create_ics({
            'title': title,
            'start': start,
            'description': description,
            'reminders': [
                {'days': 1, 'message': 'Quote due tomorrow'},
                {'hours': 2, 'message': 'Quote due in 2 hours'}
            ]
        })
        
        return {
            'google_calendar_url': google_url,
            'ics_download_url': f"/api/calendar/supplier/{quote_request_id}.ics",
            'ics_content': ics_content
        }
```

---

### API Endpoints:

```
GET  /api/calendar/opportunity/{id}
     → Download .ics for single opportunity

GET  /api/calendar/all-deadlines
     → Download .ics with all active deadlines

GET  /api/calendar/this-week
     → Get JSON of this week's events (for dashboard widget)

GET  /api/calendar/supplier/{quote_request_id}
     → Download .ics for supplier quote deadline

POST /api/calendar/google-link
     → Generate Google Calendar add link
     Body: { title, date, time, description }
```

---

### Existing Calendar Files:

**Already in `/calendars/` folder:**

```
1. cps_energy_deadline.ics
2. madison_heights_hand_delivery.ics
3. madison_heights_deadline.ics
4. warren_dda_deadline.ics
5. followup_thursday.ics
6. quote_collection_friday.ics
7. notary_sunday.ics
8. warren_dda_submit_monday.ics
```

**These are READY to double-click and import!**

---

### Quick Actions with Calendar:

```
Landing Page Quick Actions:
├─ Upload RFP
├─ Request Quote
├─ Create Invoice
└─ 📆 Export Calendar  ← Already implemented!
```

**Clicking "Export Calendar" downloads all ATLAS tasks!**

---

### Future Calendar Enhancements:

**V2 Features:**
- [ ] Two-way sync with Google Calendar API
- [ ] Auto-update calendar when dates change
- [ ] SMS reminders for critical deadlines
- [ ] Team calendar (share with employees)
- [ ] Client portal with countdown timers

**V3 Features:**
- [ ] Voice reminders via Alexa
- [ ] Mobile app push notifications
- [ ] Automatic rescheduling suggestions
- [ ] AI-predicted optimal work schedule

---

## ✅ SUMMARY

### Deadlines Box Shows:
- ✅ All active bids with final deadline dates/times
- ✅ Sequential workflow steps (1-9)
- ✅ Step status: ✅ Done, ▶️ Ready, 🔄 In Progress, 🔒 Locked
- ✅ What you can do NOW
- ✅ What's blocked and why
- ✅ Days until deadline
- ✅ Urgent items at top (< 3 days)
- ✅ 📆 "Add to Calendar" button for each opportunity
- ✅ 📆 "Export All Deadlines" button

### Email Notification Button:
- ✅ Top right corner (bids.deedavisinc@gmail.com)
- ✅ Shows new email count with badge
- ✅ Click to expand activity panel
- ✅ "Check Now" button for immediate check
- ✅ Auto-check every 15 min (shown in status)
- ✅ Recent activity log (processed emails)
- ✅ Emails that need your review (urgent)
- ✅ Today's email stats (sent/received/processed)

### Calendar Integration:
- ✅ Individual opportunity .ics export
- ✅ Export all deadlines to single .ics file
- ✅ This week's calendar widget on dashboard
- ✅ Auto-reminders (7d, 3d, 1d, 2h before)
- ✅ Supplier calendar links in quote requests
- ✅ Syncs to Apple, Google, Outlook calendars
- ✅ One-click import (double-click .ics)
- ✅ Color-coded by urgency
- ✅ Already implemented in LandingPage!

### Sequential Workflow:
- ✅ Can't skip steps (enforced by system)
- ✅ Must complete in order
- ✅ System enforces prerequisites
- ✅ Clear visual indication of status
- ✅ Action buttons only enabled when ready
- ✅ Lock icon on unavailable steps
- ✅ Orange "READY" indicator for next step

### Dashboard Layout:
- ✅ Urgent actions at top
- ✅ Active bids with workflow steps
- ✅ Email activity monitoring
- ✅ Calendar widget (this week's view)
- ✅ Active contracts tracking
- ✅ Financial metrics (VERTEX)
- ✅ System health status

**Systematic. Workflow-driven. Calendar-integrated. Nothing falls through!** 🎯📆
