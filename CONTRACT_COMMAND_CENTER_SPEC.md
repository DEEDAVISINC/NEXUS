# 🏆 Contract Command Center (CCC) - Technical Specification

**Mission: Nothing Falls Through the Cracks**

---

## 🎯 Core Purpose

Manage complete post-award lifecycle:
- WIN → Setup → Order → Deliver → Invoice → Get Paid → Maintain

---

## 📊 Database Schema (Airtable)

### 1. **Contracts Table**

```yaml
Table: Contracts

Fields:
  # Core Info
  - Contract ID (Auto-number): CONTRACT-{0000}
  - Name (Formula): {Opportunity} & " - " & {Client}
  - Status (Single Select):
      - Active
      - Completed
      - On Hold
      - Cancelled
  
  # Links
  - Opportunity (Link to Opportunities)
  - Client (Link to Contacts) [Primary contact]
  - Suppliers (Link to Suppliers) [Multiple]
  - Quote Requests (Link to Quote Requests)
  
  # Timeline
  - Start Date (Date)
  - End Date (Date)
  - Duration (Formula): DATETIME_DIFF({End Date}, {Start Date}, 'days')
  - Days Remaining (Formula): DATETIME_DIFF({End Date}, TODAY(), 'days')
  
  # Financial
  - Contract Value (Currency)
  - Billed to Date (Rollup from Invoices)
  - Paid to Date (Rollup from Invoices)
  - Outstanding (Formula): {Billed to Date} - {Paid to Date}
  - Supplier Costs (Rollup from Purchase Orders)
  - Profit Margin (Formula): ({Contract Value} - {Supplier Costs}) / {Contract Value}
  
  # Delivery
  - Delivery Schedule (Long text)
  - Next Delivery Due (Date)
  - Deliveries Completed (Number)
  - Deliveries Total (Number)
  - On-Time Performance (Percent): {On-Time Count} / {Deliveries Completed}
  
  # Status Tracking
  - Health Status (Single Select):
      - 🟢 Healthy
      - 🟡 At Risk
      - 🔴 Critical
  - Last Contact Date (Date)
  - Next Action Date (Date)
  - Next Action (Long text)
  
  # Relationships
  - Client Satisfaction (Rating 1-5)
  - Issues Count (Count from Issues table)
  - Open Issues (Rollup)
  - Performance Notes (Long text)

Views:
  - All Active Contracts
  - Needs Attention (Health Status = At Risk or Critical)
  - Deliveries Due Soon (Next Delivery Due < 7 days)
  - Invoicing Due (Next billing date < 7 days)
  - High Value (Contract Value > $100K)
```

### 2. **Purchase Orders Table**

```yaml
Table: Purchase Orders

Fields:
  # Core
  - PO Number (Auto-number): PO-2026-{0000}
  - Name (Formula): {PO Number} & " - " & {Supplier}
  - Status (Single Select):
      - Draft
      - Sent
      - Acknowledged
      - In Progress
      - Delivered
      - Cancelled
  
  # Links
  - Contract (Link to Contracts)
  - Supplier (Link to Suppliers)
  - Quote Request (Link to Quote Requests) [Original quote]
  
  # Details
  - Items (Long text / JSON)
  - Order Date (Date)
  - Expected Delivery (Date)
  - Actual Delivery (Date)
  - Days Late (Formula)
  
  # Financial
  - PO Amount (Currency)
  - Paid Amount (Currency)
  - Outstanding (Formula): {PO Amount} - {Paid Amount}
  - Payment Terms (Single Select): Net 15 / Net 30 / Net 45 / Due on Delivery
  - Payment Due Date (Formula)
  
  # Tracking
  - Sent Date (Date)
  - Sent Method (Single Select): Email / Fax / Portal
  - Sent To (Email)
  - Delivery Notes (Long text)
  - Received By (Text) [Client signature/confirmation]
  
  # Performance
  - On Time (Checkbox)
  - Quality Issues (Long text)
  - Supplier Rating (Rating 1-5)

Views:
  - Active POs
  - Delivery This Week
  - Payment Due
  - Late Deliveries
  - By Supplier
  - By Contract
```

### 3. **Contract Deliveries Table**

```yaml
Table: Contract Deliveries

Fields:
  # Core
  - Delivery ID (Auto-number): DEL-{0000}
  - Name (Formula): {Contract} & " - " & {Scheduled Date}
  - Status (Single Select):
      - Scheduled
      - Ordered
      - In Transit
      - Delivered
      - Accepted
      - Issue
  
  # Links
  - Contract (Link to Contracts)
  - Purchase Orders (Link to POs) [Multiple - all POs for this delivery]
  
  # Schedule
  - Scheduled Date (Date)
  - Actual Date (Date)
  - On Time (Checkbox)
  - Days Variance (Formula)
  
  # Details
  - Delivery Address (Long text)
  - Delivery Contact (Link to Contacts)
  - Delivery Instructions (Long text)
  - Proof of Delivery (Attachment)
  - Acceptance Signature (Attachment)
  
  # Alerts
  - Supplier Ready (Checkbox) [All POs received]
  - Alert 7 Days (Formula)
  - Alert 3 Days (Formula)
  - Alert 1 Day (Formula)

Views:
  - Upcoming (Next 30 days)
  - This Week
  - Overdue
  - By Contract
  - Delivery Calendar
```

### 4. **Contract Interactions Table**

```yaml
Table: Contract Interactions

Fields:
  # Core
  - Interaction ID (Auto-number)
  - Date Time (Date with time)
  - Type (Single Select):
      - Phone Call
      - Email
      - Meeting
      - Site Visit
      - Issue Resolution
      - Check-in
      - Invoice Sent
      - Payment Received
  
  # Links
  - Contract (Link to Contracts)
  - Contact (Link to Contacts)
  
  # Details
  - Subject (Text)
  - Notes (Long text)
  - Sentiment (Single Select): Positive / Neutral / Negative
  - Action Items (Long text)
  - Follow-up Date (Date)
  - Follow-up Status (Single Select): Pending / Completed
  
  # Attachments
  - Files (Attachments)

Views:
  - All Interactions
  - By Contract
  - Needs Follow-up
  - Recent Activity
  - By Type
```

### 5. **Contract Issues Table**

```yaml
Table: Contract Issues

Fields:
  # Core
  - Issue ID (Auto-number): ISSUE-{0000}
  - Title (Text)
  - Status (Single Select):
      - Open
      - In Progress
      - Resolved
      - Closed
  - Severity (Single Select):
      - Low
      - Medium
      - High
      - Critical
  
  # Links
  - Contract (Link to Contracts)
  - Related Delivery (Link to Deliveries)
  - Related PO (Link to Purchase Orders)
  
  # Details
  - Description (Long text)
  - Impact (Long text)
  - Root Cause (Long text)
  - Resolution (Long text)
  
  # Timeline
  - Reported Date (Date)
  - Resolved Date (Date)
  - Days to Resolve (Formula)
  
  # Responsibility
  - Assigned To (Single Select): Internal / Supplier / Client
  - Supplier Responsible (Link to Suppliers)

Views:
  - Open Issues
  - By Contract
  - By Severity
  - Critical Issues
```

---

## 🔄 Automated Workflows

### Workflow 1: Win → Contract Setup

**Trigger:** Opportunity status changes to "WON"

**Actions:**
1. Create Contract record
   - Import all opportunity data
   - Set start date (today or contract start)
   - Set end date (from RFP terms)
   - Link to opportunity
   - Calculate contract value

2. Create ATLAS PM Project
   - Project name: Contract name
   - Import milestones from opportunity
   - Create delivery schedule tasks
   - Assign team members

3. Link Supplier Quotes
   - Find all accepted quotes for this opportunity
   - Link to contract
   - Mark for PO generation

4. Generate Purchase Orders (Draft)
   - For each accepted supplier quote
   - Create PO record
   - Status: Draft
   - Populate items from quote

5. Create Delivery Schedule
   - Based on contract terms
   - Create delivery records
   - Set expected dates
   - Link to contract

6. Setup Billing Schedule
   - Based on payment terms
   - Create invoice schedule in VERTEX
   - Link to contract

7. Notify Team
   - Email notification
   - Slack notification (if configured)
   - Task assignments in ATLAS

### Workflow 2: Daily Contract Health Check

**Trigger:** Every day at 9:00 AM

**Checks:**
1. **Deliveries Due Soon**
   ```python
   deliveries = airtable.all('Contract Deliveries', 
       formula="AND({Scheduled Date} <= DATEADD(TODAY(), 7, 'days'), 
                    {Status} != 'Delivered')")
   
   for delivery in deliveries:
       # Check if POs are ready
       if not delivery['Supplier Ready']:
           alert("⚠️ Delivery in 7 days but supplier not ready!")
       
       # Check if 3 days out
       if days_until(delivery['Scheduled Date']) <= 3:
           alert("🚨 Delivery in 3 days - confirm status!")
   ```

2. **Invoices Due**
   ```python
   contracts = airtable.all('Contracts',
       formula="AND({Next Invoice Date} <= TODAY(),
                    {Status} = 'Active')")
   
   for contract in contracts:
       if not has_invoice_for_period(contract):
           alert(f"📋 Invoice due for {contract['Name']}")
           generate_invoice_draft(contract)
   ```

3. **Payments Overdue**
   ```python
   invoices = airtable.all('Invoices',
       formula="AND({Due Date} < TODAY(),
                    {Payment Status} != 'Paid')")
   
   for invoice in invoices:
       days_overdue = days_since(invoice['Due Date'])
       if days_overdue == 15:
           send_payment_reminder(invoice, level=1)
       elif days_overdue == 30:
           send_payment_reminder(invoice, level=2)
           alert_manager(invoice)
   ```

4. **Supplier Payments Due**
   ```python
   pos = airtable.all('Purchase Orders',
       formula="AND({Payment Due Date} <= DATEADD(TODAY(), 3, 'days'),
                    {Paid Amount} < {PO Amount})")
   
   for po in pos:
       alert(f"💰 Payment due to {po['Supplier']} in 3 days")
   ```

5. **Contact Frequency Check**
   ```python
   contracts = airtable.all('Contracts',
       formula="AND({Last Contact Date} < DATEADD(TODAY(), -14, 'days'),
                    {Status} = 'Active')")
   
   for contract in contracts:
       alert(f"📞 No contact with {contract['Client']} in 14+ days")
   ```

### Workflow 3: Delivery Management

**Trigger:** Delivery status changes OR date approaches

**Actions:**

**7 Days Before Delivery:**
- Alert user: "Delivery in 7 days"
- Check if POs are ready
- Confirm supplier has shipped
- Confirm delivery details with client

**3 Days Before Delivery:**
- Alert user: "Delivery in 3 days"
- Confirm tracking info
- Reconfirm with client
- Prepare delivery documentation

**Day of Delivery:**
- Alert user: "Delivery TODAY"
- Monitor delivery status
- Get proof of delivery
- Get client acceptance

**After Delivery:**
- Request client feedback
- Rate supplier performance
- Update contract status
- Trigger invoice if applicable

---

## 🎨 UI Components

### Main Dashboard

```tsx
<ContractCommandCenter>
  {/* Header Stats */}
  <Stats>
    <Stat label="Active Contracts" value={8} trend="+2" />
    <Stat label="Under Management" value="$12.4M" />
    <Stat label="On-Time Performance" value="98%" color="green" />
    <Stat label="Outstanding Payments" value="$450K" />
  </Stats>

  {/* Alert Banner */}
  <Alerts>
    <Alert priority="high">
      🚨 Sterling Heights: Delivery 2 days late
    </Alert>
    <Alert priority="medium">
      ⚠️ CPS Energy: Invoice due tomorrow
    </Alert>
  </Alerts>

  {/* Tabs */}
  <Tabs>
    <Tab id="dashboard">Overview</Tab>
    <Tab id="contracts">All Contracts</Tab>
    <Tab id="suppliers">Suppliers</Tab>
    <Tab id="deliveries">Deliveries</Tab>
    <Tab id="financials">Financials</Tab>
    <Tab id="relationships">Relationships</Tab>
  </Tabs>

  {/* Main Content */}
  <ContractList>
    {contracts.map(contract => (
      <ContractCard contract={contract}>
        <Header>
          <Title>{contract.name}</Title>
          <HealthBadge status={contract.healthStatus} />
        </Header>
        
        <Stats>
          <MiniStat label="Value" value={contract.value} />
          <MiniStat label="Days Left" value={contract.daysRemaining} />
          <MiniStat label="Completion" value={contract.percentComplete} />
        </Stats>
        
        <Actions>
          <Button icon="📦">Track Delivery</Button>
          <Button icon="💰">Create Invoice</Button>
          <Button icon="📋">View Details</Button>
        </Actions>
        
        <Timeline>
          <Event status="completed">✅ Contract signed</Event>
          <Event status="completed">✅ POs sent to suppliers</Event>
          <Event status="active">⏳ January delivery in progress</Event>
          <Event status="pending">📋 Invoice #002 due 2/1</Event>
        </Timeline>
      </ContractCard>
    ))}
  </ContractList>
</ContractCommandCenter>
```

---

## 🔌 API Endpoints

### Contract Management

```python
POST /api/contracts/create-from-win
Body: { opportunity_id: string }
→ Creates contract from won opportunity

GET /api/contracts/list
Query: ?status=active&health=at-risk
→ Returns filtered contract list

GET /api/contracts/{id}
→ Returns complete contract details

POST /api/contracts/{id}/log-interaction
Body: { type, subject, notes }
→ Logs interaction with client

GET /api/contracts/{id}/timeline
→ Returns contract timeline/history
```

### Delivery Management

```python
GET /api/deliveries/upcoming
Query: ?days=7
→ Returns deliveries in next N days

POST /api/deliveries/{id}/update-status
Body: { status, notes, proof_of_delivery }
→ Updates delivery status

GET /api/deliveries/{id}/tracking
→ Returns delivery tracking info
```

### Financial Management

```python
POST /api/contracts/{id}/generate-invoice
→ Creates invoice in VERTEX for this contract

GET /api/contracts/{id}/financials
→ Returns P&L for contract

POST /api/pos/{id}/record-payment
Body: { amount, date, method }
→ Records supplier payment
```

---

## 🎯 Success Metrics

### System Goals:
- ✅ 0% missed deliveries
- ✅ 0% missed invoices
- ✅ 100% supplier payment on time
- ✅ < 15 days average payment collection
- ✅ 95%+ client satisfaction
- ✅ Complete audit trail for every contract

---

## 📝 Next Steps

1. Create Airtable tables (Contracts, POs, Deliveries, Interactions, Issues)
2. Build backend API endpoints
3. Create Contract Command Center UI component
4. Implement automated workflows
5. Add to NEXUS landing page
6. Test with first won contract
7. Iterate based on real usage

**Goal: Launch with next contract win! Nothing falls through!**
