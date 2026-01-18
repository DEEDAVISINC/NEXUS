# 🏦 LBPC Integration into Nexus - Architecture Plan

**Date:** January 13, 2026  
**Priority:** MEDIUM  
**Status:** PLANNING PHASE  

---

## 🎯 **Integration Decision**

**User's Statement:**
> "I want it to have the same backend and frontend as Nexus"

**This means:**
- LBPC should use Python backend (not SvelteKit)
- LBPC should use React frontend (not Svelte)
- LBPC should use Airtable database (not Supabase)
- LBPC should integrate with VERTEX for financials

---

## 📊 **What is LBPC?**

**LBPC = Lancaster Banques P.C.**

### **Business Model:**
- Surplus recovery from tax sales and foreclosures
- Find property owners who are owed money
- Help them claim their surplus
- Charge 30% contingency fee
- No upfront costs to clients

### **Revenue Potential:**
- Average surplus: $25,000
- Your 30% fee: $7,500 per client
- Volume potential: 50-100 clients/month
- Monthly revenue: $375K - $750K

### **Current Status:**
- Exists as standalone HTML system
- Has AI document generation
- Email/SMS automation planned
- E-signature workflows designed
- Needs integration with Nexus

---

## 🏗️ **Target Architecture**

### **LBPC Within Nexus Ecosystem:**
```
NEXUS COMMAND CENTER
├── GPSS (Government Contracting)
├── ATLAS (Project Management)
├── DDCSS (Consulting)
├── LBPC (Surplus Recovery) ← INTEGRATING THIS
├── GBIS (Grant Management)
└── VERTEX (Financial Hub)
```

### **LBPC → VERTEX Flow:**
```
Surplus Recovery Successful
  ↓
Create VERTEX Invoice (30% contingency fee)
  ↓
Client pays you directly (no factoring needed)
  ↓
Record in VERTEX Revenue
  ↓
Track LBPC system ROI
  ↓
Calculate profitability per lead source
```

---

## 💾 **Airtable Schema for LBPC**

### **Table 1: LBPC Leads** (Main table)

**Primary Purpose:** Track all surplus recovery leads

**Fields:**
1. `lead_id` (autonumber) - Unique identifier
2. `client_name` (text) - Property owner name
3. `property_address` (text) - Property location
4. `city` (text)
5. `county` (text)
6. `state` (single select) - All 50 states
7. `zip_code` (text)

**Contact Information:**
8. `phone` (phone number)
9. `email` (email)
10. `phone_verified` (checkbox)
11. `email_verified` (checkbox)

**Surplus Details:**
12. `surplus_amount` (currency) - Amount owed to client
13. `case_number` (text) - Court case number
14. `foreclosure_date` (date)
15. `county_holding_funds` (text) - Which county has the money
16. `deadline_to_claim` (date) - Important!

**Fee Calculation:**
17. `fee_percentage` (number, default 30)
18. `your_fee_amount` (formula) - `surplus_amount * 0.30`
19. `client_portion` (formula) - `surplus_amount * 0.70`

**Status Tracking:**
20. `status` (single select)
    - New
    - Contacted
    - Interested
    - Not Interested
    - Contract Sent
    - Contract Signed
    - Documents Submitted
    - Claim Filed
    - Payment Received
    - Closed - Won
    - Closed - Lost
21. `lead_source` (single select)
    - County Website
    - Data Provider
    - Referral
    - Marketing
    - Other

**Lead Scoring:**
22. `lead_score` (number, 0-100) - Auto-calculated
23. `priority` (single select) - High, Medium, Low

**Important Dates:**
24. `date_added` (created time)
25. `first_contact_date` (date)
26. `contract_sent_date` (date)
27. `contract_signed_date` (date)
28. `claim_submitted_date` (date)
29. `payment_received_date` (date)

**Next Actions:**
30. `next_action` (text)
31. `next_action_date` (date)
32. `assigned_to` (user) - Team member responsible

**Automation:**
33. `workflows_triggered` (multiple select)
    - Initial Contact
    - Follow-up Day 3
    - Follow-up Day 7
    - Contract Workflow
    - Document Collection
34. `automation_paused` (checkbox)

**Links:**
35. `tasks` (linked to LBPC Tasks)
36. `communications` (linked to LBPC Communications)
37. `documents` (linked to LBPC Documents)
38. `invoice` (linked to VERTEX Invoices)

**Notes:**
39. `internal_notes` (long text)
40. `client_notes` (long text)

---

### **Table 2: LBPC Tasks**

**Purpose:** Action items for lead follow-up

**Fields:**
1. `task_id` (autonumber)
2. `lead` (linked to LBPC Leads) - Which lead this task is for
3. `title` (text)
4. `description` (long text)
5. `task_type` (single select)
   - Email
   - Call
   - SMS
   - Mail Document
   - Follow-up
   - Document Collection
   - Other
6. `priority` (single select) - Urgent, High, Medium, Low
7. `status` (single select) - Pending, In Progress, Completed, Cancelled
8. `due_date` (date)
9. `completed_date` (date)
10. `assigned_to` (user)
11. `auto_created` (checkbox) - Created by automation?
12. `workflow_name` (text) - Which workflow created this

---

### **Table 3: LBPC Communications**

**Purpose:** Log all interactions with leads

**Fields:**
1. `comm_id` (autonumber)
2. `lead` (linked to LBPC Leads)
3. `date_time` (date/time)
4. `type` (single select)
   - Email
   - SMS
   - Phone Call
   - Direct Mail
   - Meeting
   - Note
5. `direction` (single select) - Outbound, Inbound
6. `subject` (text)
7. `message_body` (long text)
8. `template_used` (text)
9. `status` (single select)
   - Sent
   - Delivered
   - Opened
   - Clicked
   - Replied
   - Failed
   - Bounced
10. `external_id` (text) - SendGrid/Twilio message ID
11. `opened_at` (date/time)
12. `clicked_at` (date/time)
13. `replied_at` (date/time)
14. `automation_sent` (checkbox)
15. `logged_by` (user)

---

### **Table 4: LBPC Documents**

**Purpose:** Track all generated documents and contracts

**Fields:**
1. `document_id` (autonumber)
2. `lead` (linked to LBPC Leads)
3. `created_date` (created time)
4. `document_type` (single select)
   - Initial Notice
   - Engagement Agreement
   - Document Checklist
   - Power of Attorney
   - W-9 Form
   - Custom Letter
5. `template_name` (text)
6. `document_content` (long text) - Generated text
7. `file_attachment` (attachment) - PDF/DOC version
8. `sent_to_client` (checkbox)
9. `sent_date` (date)
10. `docusign_envelope_id` (text) - If sent via DocuSign
11. `docusign_status` (single select)
    - Sent
    - Delivered
    - Signed
    - Declined
    - Voided
12. `signed_date` (date)
13. `signer_email` (email)
14. `signer_name` (text)

---

### **Table 5: LBPC Automation Workflows**

**Purpose:** Define automation rules and track execution

**Fields:**
1. `workflow_id` (autonumber)
2. `workflow_name` (text)
3. `description` (long text)
4. `active` (checkbox)
5. `trigger_type` (single select)
   - Lead Created
   - Status Change
   - Time-Based
   - Manual
6. `trigger_conditions` (long text) - JSON or description
7. `steps` (long text) - Workflow steps defined
8. `total_executions` (number)
9. `successful_executions` (number)
10. `failed_executions` (number)
11. `last_run` (date/time)

---

### **Table 6: LBPC Lead Sources**

**Purpose:** Track where leads come from and their effectiveness

**Fields:**
1. `source_name` (text, primary)
2. `source_type` (single select)
   - County Website
   - Data Provider
   - Purchased List
   - Referral
   - Marketing Campaign
   - Other
3. `cost_per_lead` (currency)
4. `total_leads` (rollup from LBPC Leads)
5. `total_converted` (rollup count where status = Closed - Won)
6. `conversion_rate` (formula)
7. `total_revenue` (rollup of fees from converted leads)
8. `roi` (formula) - Revenue / Cost
9. `active` (checkbox)
10. `notes` (long text)

---

## 🔌 **Backend API Endpoints (Python)**

### **Location:** `nexus_backend.py` or `api_server.py`

### **LBPC Routes:**

```python
# Leads
@app.route('/api/lbpc/leads', methods=['GET', 'POST'])
@app.route('/api/lbpc/leads/<lead_id>', methods=['GET', 'PUT', 'DELETE'])
@app.route('/api/lbpc/leads/import', methods=['POST'])  # CSV import
@app.route('/api/lbpc/leads/export', methods=['GET'])   # CSV export

# Tasks
@app.route('/api/lbpc/tasks', methods=['GET', 'POST'])
@app.route('/api/lbpc/tasks/<task_id>/complete', methods=['POST'])

# Communications
@app.route('/api/lbpc/communications', methods=['GET', 'POST'])
@app.route('/api/lbpc/communications/send-email', methods=['POST'])
@app.route('/api/lbpc/communications/send-sms', methods=['POST'])

# Documents
@app.route('/api/lbpc/documents/generate', methods=['POST'])
@app.route('/api/lbpc/documents/<doc_id>', methods=['GET'])
@app.route('/api/lbpc/documents/send-docusign', methods=['POST'])

# Automation
@app.route('/api/lbpc/automation/run', methods=['POST'])
@app.route('/api/lbpc/automation/workflows', methods=['GET'])

# Analytics
@app.route('/api/lbpc/analytics/dashboard', methods=['GET'])
@app.route('/api/lbpc/analytics/conversion-rates', methods=['GET'])
@app.route('/api/lbpc/analytics/revenue-forecast', methods=['GET'])

# Webhooks
@app.route('/api/lbpc/webhooks/sendgrid', methods=['POST'])
@app.route('/api/lbpc/webhooks/twilio', methods=['POST'])
@app.route('/api/lbpc/webhooks/docusign', methods=['POST'])
```

---

## 🎨 **Frontend Components (React)**

### **Location:** `nexus-frontend/src/components/systems/LBPCSystem.tsx`

### **Component Structure:**

```
LBPCSystem (main container)
├── LBPCDashboard (metrics & KPIs)
│   ├── StatsCards (total leads, revenue, conversion)
│   ├── PipelineChart (leads by status)
│   └── RevenueChart (monthly revenue)
│
├── LeadsTable (main lead management)
│   ├── LeadsFilter (state, status, date filters)
│   ├── LeadsSearch (search by name, address, etc.)
│   ├── LeadsList (paginated table)
│   └── LeadDetail (modal with full lead info)
│
├── TasksPanel (task management)
│   ├── TasksList (due today, overdue, upcoming)
│   └── TaskCreate (quick task creation)
│
├── CommunicationsPanel (communication log)
│   ├── EmailComposer (send emails)
│   ├── SMSComposer (send texts)
│   └── CommunicationsList (history)
│
├── DocumentsPanel (document generation)
│   ├── TemplateSelector (choose document type)
│   ├── DocumentPreview (show generated doc)
│   └── DocumentActions (send, download, copy)
│
└── AutomationPanel (workflow management)
    ├── WorkflowsList (active workflows)
    └── ManualRun (trigger workflows manually)
```

---

## 🤖 **Automation Workflows**

### **Workflow 1: Initial Contact (Runs automatically on lead creation)**

```
Step 1: Wait 1 hour (give time for data enrichment)
  ↓
Step 2: Generate personalized initial notice (AI)
  ↓
Step 3: Send email (SendGrid)
  ↓
Step 4: Wait 15 minutes
  ↓
Step 5: Send SMS (Twilio)
  ↓
Step 6: Create follow-up task (3 days)
  ↓
Step 7: Update lead status → "Contacted"
```

### **Workflow 2: Follow-Up Drip Campaign**

```
Day 0: Initial contact (email + SMS)
Day 1: Follow-up email (if no response)
Day 3: SMS reminder
Day 5: Email with testimonial
Day 7: Create call task (urgent)
Day 10: Final email ("last chance")
Day 14: Mark as "Not Interested" or restart
```

### **Workflow 3: Contract Workflow**

```
Trigger: Lead status changed to "Interested"
  ↓
Step 1: Generate engagement agreement (AI)
  ↓
Step 2: Send via DocuSign
  ↓
Step 3: Send email notification
  ↓
Step 4: Wait 30 minutes
  ↓
Step 5: Send SMS: "Check email for contract"
  ↓
Step 6: Create follow-up task (24 hours)
  ↓
Step 7: Update status → "Contract Sent"
```

### **Workflow 4: Contract Signed**

```
Trigger: DocuSign webhook (contract signed)
  ↓
Step 1: Update lead status → "Contract Signed"
  ↓
Step 2: Create VERTEX Invoice (30% fee)
  ↓
Step 3: Send document checklist to client
  ↓
Step 4: Create task: "Collect documents"
  ↓
Step 5: Send congratulations email
```

---

## 🔗 **Integration Points**

### **LBPC → VERTEX:**
- When contract signed → Create VERTEX Invoice
- When payment received → Update VERTEX Revenue
- Track factoring? NO (clients pay you directly, 30% fee)
- Monthly reporting: LBPC revenue in VERTEX dashboard

### **LBPC → NEXUS Command Center:**
- LBPC module in main navigation
- Shared task system (LBPC tasks show in main task list)
- Shared communication log
- Shared client management (if client uses multiple systems)

### **LBPC → AI Copilot:**
- "How many LBPC leads do I have?"
- "What's my LBPC conversion rate?"
- "Show me high-priority surplus recovery leads"
- "Generate initial notice for lead #123"

---

## 🔧 **Technical Implementation Steps**

### **Phase 1: Airtable Setup (Week 1)**
- [ ] Create LBPC Airtable base
- [ ] Create 6 tables with all fields
- [ ] Set up views and filters
- [ ] Configure formulas
- [ ] Test data import

### **Phase 2: Backend API (Week 2)**
- [ ] Add LBPC routes to `api_server.py`
- [ ] Implement Airtable CRUD operations
- [ ] Add CSV import/export
- [ ] Integrate SendGrid (email)
- [ ] Integrate Twilio (SMS)
- [ ] Set up webhook handlers

### **Phase 3: Frontend UI (Week 3)**
- [ ] Create `LBPCSystem.tsx` component
- [ ] Build dashboard with KPIs
- [ ] Build leads table with filters
- [ ] Build task management panel
- [ ] Build communication log
- [ ] Build document generator

### **Phase 4: Automation (Week 4)**
- [ ] Implement workflow engine
- [ ] Create initial contact workflow
- [ ] Create drip campaign workflow
- [ ] Create contract workflow
- [ ] Set up cron jobs or scheduled tasks
- [ ] Test automation end-to-end

### **Phase 5: VERTEX Integration (Week 5)**
- [ ] Create VERTEX Invoice on contract signed
- [ ] Link LBPC lead to VERTEX Invoice
- [ ] Track LBPC revenue in VERTEX
- [ ] Add LBPC metrics to VERTEX dashboard
- [ ] Set up financial reporting

### **Phase 6: Advanced Features (Week 6+)**
- [ ] DocuSign integration
- [ ] AI document generation (OpenAI)
- [ ] Lead scoring algorithm
- [ ] Predictive analytics
- [ ] Mobile-responsive design
- [ ] Performance optimization

---

## 💡 **Key Decisions Needed**

1. **AI Integration:**
   - Use OpenAI for document generation? (vs templates)
   - Use AI for lead scoring?
   - Cost: ~$20-50/month

2. **Email/SMS:**
   - SendGrid for email? (vs others)
   - Twilio for SMS? (vs others)
   - Cost: ~$50-200/month depending on volume

3. **E-Signature:**
   - DocuSign? (vs HelloSign, PandaDoc)
   - Cost: ~$25-40/month

4. **Priority:**
   - Build basic version first, then add automation?
   - Or build automation from start?

5. **Team:**
   - Solo operation or plan for team?
   - Multi-user access needed?

---

## 📊 **Estimated Timeline**

### **Minimum Viable Product (MVP):**
- Airtable setup: 3 days
- Basic API: 1 week
- Basic frontend: 1 week
- **Total: 2.5 weeks**

**Features:** Manual lead entry, basic task tracking, simple communication log

### **Full Automated System:**
- MVP: 2.5 weeks
- Automation: 1 week
- Email/SMS: 1 week
- DocuSign: 3 days
- VERTEX integration: 3 days
- **Total: 5-6 weeks**

**Features:** Everything automated, AI-powered, full integration

---

## 💰 **Cost Estimate**

### **One-time Costs:**
- Development time: DIY (free) or contractor ($5-10K)
- Initial setup: Minimal

### **Monthly Operational Costs:**
- Airtable: Free (< 1,200 records) or $20/month
- OpenAI: $20-50/month
- SendGrid: Free (100 emails/day) or $20/month
- Twilio: ~$50-200/month (depends on SMS volume)
- DocuSign: $25-40/month
- **Total: $115-330/month**

### **Revenue Potential:**
- 10 clients/month × $7,500 avg = $75,000/month
- **ROI: 225-650x** 🚀

---

## 🎯 **Success Metrics**

### **Track These KPIs:**
1. Total leads in system
2. Lead-to-client conversion rate (target: 10%)
3. Average time to conversion
4. Revenue per lead
5. Cost per acquisition
6. Monthly recurring revenue
7. Automation success rate

### **Goals:**
- Month 1: 100 leads, 5 clients, $37,500 revenue
- Month 3: 500 leads, 50 clients, $375,000 revenue
- Month 6: 1000 leads/month, 100 clients, $750,000 revenue

---

## ❓ **Open Questions for User**

1. **Priority:** How urgent is LBPC integration? (High/Medium/Low)
2. **Budget:** OK with ~$300/month for automation services?
3. **Timeline:** When do you want this live?
4. **Features:** MVP first or full system?
5. **Team:** Solo or planning to hire help?
6. **Lead Source:** Where will leads come from?

---

**Status:** READY TO BUILD  
**Awaiting:** User approval to proceed  
**Next Step:** Phase 1 - Create Airtable schema  
**Estimated Completion:** 5-6 weeks for full system
