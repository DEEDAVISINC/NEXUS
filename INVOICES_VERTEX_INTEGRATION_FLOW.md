# 💎 How Invoices & VERTEX Integrate with NEXUS

**Complete financial integration across all systems**

---

## 🔄 The Complete Revenue Flow

```
OPPORTUNITY → BID → WIN → DELIVER → INVOICE → GET PAID → VERTEX TRACKING
```

---

## 💰 Invoice Table = Universal Billing Hub

### The Invoices Table Links to EVERYTHING:

```
Invoices Table (Central Hub)
├── Links to GPSS Opportunities (government contracts)
├── Links to ATLAS Projects (project billing)
├── Links to DDCSS Prospects (corporate consulting)
├── Links to LBPC Leads (surplus recovery fees)
├── Links to GBIS Grants (grant billing)
├── Links to Contracts (post-award billing) 🆕
└── Links to VERTEX Clients (who owes you money)
```

**ONE invoice table serves ALL systems!**

---

## 📊 Integration Flow by System

### 1. GPSS (Government Contracts) → Invoices

```
GPSS Workflow:
1. Find opportunity in GPSS Opportunities
2. Win contract (status = "WON")
3. Click "Generate Invoice" button
   ↓
4. System creates invoice record:
   • Source System: "GPSS"
   • Links to: GPSS Opportunity
   • Client Name: Government agency
   • Contract Number: From opportunity
   • Invoice Type: "Government Contract"
   • Line items: From contract deliverables
   ↓
5. Invoice appears in VERTEX dashboard
6. Track payment status
7. When paid → Updates VERTEX Revenue
```

**Code in nexus_backend.py:**
```python
invoice_generator.generate_from_opportunity(opportunity_id)
→ Creates invoice linked to opportunity
→ Sets government compliance fields
→ Tracks in VERTEX
```

### 2. ATLAS (Project Management) → Invoices

```
ATLAS Workflow:
1. Project in ATLAS Projects table
2. Milestone completed or monthly billing
3. Click "Invoice Project" button
   ↓
4. System creates invoice:
   • Source System: "ATLAS"
   • Links to: ATLAS Project
   • Client Name: Project client
   • Invoice Type: "Milestone" or "Progress"
   • Line items: Time & materials or deliverables
   ↓
5. Track in VERTEX
6. Link expenses to this project
7. Calculate profit margin
```

### 3. DDCSS (Corporate Sales) → Invoices

```
DDCSS Workflow:
1. Close deal with corporate prospect
2. Deliver consulting services
3. Click "Invoice Prospect" button
   ↓
4. System creates invoice:
   • Source System: "DDCSS"
   • Links to: DDCSS Prospect
   • Client Name: Company name
   • Invoice Type: "Standard"
   • Line items: Consulting services
   ↓
5. Track payment in VERTEX
```

### 4. LBPC (Surplus Recovery) → Invoices

```
LBPC Workflow:
1. Successfully recover surplus for client
2. Client signs agreement
3. Generate invoice for fee
   ↓
4. System creates invoice:
   • Source System: "LBPC"
   • Links to: LBPC Lead
   • Client Name: Surplus recovery client
   • Invoice Type: "Standard"
   • Amount: % of recovered surplus
   ↓
5. Track contingency fee payment
```

### 5. Contracts (Post-Award) → Invoices 🆕

```
Contract Workflow:
1. Win bid → Contract created
2. Delivery completed (tracked in Contract Deliveries)
3. Auto-generate invoice on schedule
   ↓
4. System creates invoice:
   • Source System: "GPSS" (or others)
   • Links to: Contract
   • Links to: Specific Delivery
   • Invoice Type: Based on contract terms
   • Recurring: If monthly/quarterly
   ↓
5. Track multi-year contract billing
6. Automatic invoice generation
```

---

## 💎 VERTEX = Financial Intelligence Layer

### What VERTEX Does:

**VERTEX sits ABOVE all systems and provides:**

```
┌─────────────────────────────────────────┐
│          VERTEX Financial Dashboard     │
│                                         │
│  Revenue  │  Expenses  │  Profit  │ Cash│
│  $500K    │  $350K     │  $150K   │ $80K│
└─────────────────────────────────────────┘
            ↓ Data flows up from ↓
┌─────────────────────────────────────────┐
│              Invoices Table             │
│  (Links to all source systems)          │
└─────────────────────────────────────────┘
            ↓ Generated from ↓
┌────────┬────────┬────────┬────────┬─────┐
│  GPSS  │ ATLAS  │ DDCSS  │  LBPC  │ etc │
└────────┴────────┴────────┴────────┴─────┘
```

### VERTEX Tables:

1. **VERTEX Invoices** (linked to central Invoices table)
2. **VERTEX Expenses** (costs of doing business)
3. **VERTEX Revenue** (all income sources)
4. **VERTEX Bank Transactions** (cash flow)
5. **VERTEX Clients** (who owes/pays you)
6. **VERTEX Payroll** (employee costs)
7. **VERTEX Reports** (financial analytics)

---

## 🔗 Data Flow Example

### Complete Flow: Government Contract

```
Step 1: OPPORTUNITY DISCOVERY
┌─────────────────────────┐
│  GPSS Opportunities     │
│  • CPS Energy RFQ       │
│  • Value: $2.4M         │
│  • Status: New          │
└─────────────────────────┘

Step 2: BID PROCESS
┌─────────────────────────┐
│  Quote Requests 🆕       │
│  • 3 suppliers quoted   │
│  • Best price: $42K     │
└─────────────────────────┘
         ↓
┌─────────────────────────┐
│  GPSS Pricing           │
│  • Your bid: $48K       │
│  • Margin: 12.5%        │
└─────────────────────────┘
         ↓
┌─────────────────────────┐
│  GPSS Proposals         │
│  • Proposal generated   │
│  • Status: Submitted    │
└─────────────────────────┘

Step 3: WIN! 🎉
┌─────────────────────────┐
│  Opportunity            │
│  • Status: WON          │
│  • Triggers workflow    │
└─────────────────────────┘
         ↓
┌─────────────────────────┐
│  Contracts 🆕            │
│  • Contract created     │
│  • Start date set       │
│  • Billing schedule     │
└─────────────────────────┘

Step 4: SUPPLIER ORDERS
┌─────────────────────────┐
│  Purchase Orders 🆕      │
│  • PO sent to supplier  │
│  • Cost: $42K           │
│  • Due: Feb 15          │
└─────────────────────────┘

Step 5: DELIVERY
┌─────────────────────────┐
│  Contract Deliveries 🆕  │
│  • Delivered: Feb 15    │
│  • Client accepted      │
│  • Proof of delivery    │
└─────────────────────────┘

Step 6: INVOICE CLIENT
┌─────────────────────────┐
│  Invoices Table         │
│  • Source: GPSS         │
│  • Opportunity: CPS     │
│  • Contract: CPS-2026   │
│  • Amount: $48K         │
│  • Due: Net 30          │
│  • Status: Sent         │
└─────────────────────────┘

Step 7: PAY SUPPLIER
┌─────────────────────────┐
│  VERTEX Expenses        │
│  • Vendor: Grainger     │
│  • Amount: $42K         │
│  • Linked to: Invoice   │
│  • Billable: Yes        │
└─────────────────────────┘

Step 8: GET PAID
┌─────────────────────────┐
│  Invoices Table         │
│  • Payment received     │
│  • Amount: $48K         │
│  • Date: March 15       │
│  • Status: Paid ✅      │
└─────────────────────────┘
         ↓
┌─────────────────────────┐
│  VERTEX Revenue         │
│  • Revenue: $48K        │
│  • Cost: $42K           │
│  • Profit: $6K (12.5%)  │
│  • Margin: Calculated   │
└─────────────────────────┘

Step 9: FINANCIAL INTELLIGENCE
┌─────────────────────────┐
│  VERTEX Dashboard       │
│  • Contract P&L visible │
│  • Cash flow tracked    │
│  • QuickBooks export    │
│  • Tax reporting ready  │
└─────────────────────────┘
```

---

## 🎯 Key Integration Points

### 1. Invoice Generation (Automated)

**From any system, click "Generate Invoice":**

```python
# From GPSS Opportunity
invoice = generate_invoice_from_opportunity(opp_id)

# From ATLAS Project  
invoice = generate_invoice_from_project(project_id)

# From Contract (post-award)
invoice = generate_invoice_from_contract(contract_id, delivery_id)
```

**Invoice auto-fills:**
- Client name from source system
- Line items from deliverables
- Contract numbers (if government)
- Tax/compliance fields
- Payment terms
- Due dates

### 2. Financial Tracking (Automatic)

**When invoice is paid:**
```
Invoice Status → "Paid"
   ↓
VERTEX Revenue record created
   ↓
VERTEX Dashboard updates
   ↓
Profit margin calculated (Revenue - Expenses)
   ↓
Cash flow chart updates
```

### 3. Expense Linking (Smart)

**Link expenses to invoices:**
```
VERTEX Expenses Table:
• Supplier payment: $42K
• Linked to: Invoice INV-2026-001
• Billable: Yes
• Project: CPS Energy

Result:
• Profit = Invoice Amount - Linked Expenses
• Margin % auto-calculated
• Client billing reconciled
```

### 4. Multi-System View

**VERTEX shows complete picture:**

```
This Month Revenue Breakdown:
├── GPSS: $250K (5 contracts)
├── ATLAS: $120K (3 projects)
├── DDCSS: $80K (2 consulting engagements)
├── LBPC: $50K (10 surplus recoveries)
└── Total: $500K

This Month Expenses:
├── Suppliers: $180K (linked to GPSS invoices)
├── Subcontractors: $60K (linked to ATLAS projects)
├── Software: $5K
├── Marketing: $8K
└── Total: $253K

Net Profit: $247K (49% margin)
```

---

## 💡 Why This Integration Matters

### Before Integration:
- ❌ Manual invoice creation
- ❌ Disconnected from opportunities
- ❌ No profit tracking per contract
- ❌ No expense linking
- ❌ Separate financial system

### After Integration:
- ✅ One-click invoice generation
- ✅ Automatically linked to source
- ✅ Real-time profit tracking
- ✅ Expenses linked to revenue
- ✅ Complete financial picture

---

## 🔧 How It's Built

### Backend (`nexus_backend.py`):

```python
class InvoiceGeneratorAgent:
    """AI-powered Invoice Generator"""
    
    def generate_from_opportunity(self, opportunity_id):
        # Get opportunity details from GPSS
        opp = airtable.get_record("GPSS Opportunities", opportunity_id)
        
        # Create invoice with links
        invoice = airtable.create_record("Invoices", {
            "Source System": "GPSS",
            "GPSS Opportunity": [opportunity_id],
            "Client Name": opp['Agency'],
            "Contract Number": opp['Solicitation Number'],
            "Total Amount": opp['Value'],
            # ... all other fields
        })
        
        return invoice
```

### Frontend (`InvoiceDashboard.tsx`):

```typescript
// View invoices from all systems
const invoices = await api.getInvoices();

// Filter by source system
const gpssInvoices = invoices.filter(inv => 
  inv['Source System'] === 'GPSS'
);

// Generate invoice from opportunity
const newInvoice = await api.generateInvoiceFromOpportunity(oppId);
```

---

## 📊 VERTEX Dashboard Features

### Real-Time Metrics:

```
Revenue This Month: $500K
├── Invoices Sent: 25
├── Invoices Paid: 18
├── Outstanding: $180K
└── Overdue: $45K

Expenses This Month: $350K
├── Supplier Costs: $280K (linked to contracts)
├── Operating: $70K

Net Profit: $150K (30% margin)

Cash Flow: +$80K this month
Accounts Receivable: $220K
Average Days Outstanding: 32 days
```

### Integration Views:

1. **By Source System** - See revenue from each system
2. **By Contract** - Track multi-year contracts
3. **By Client** - Client profitability
4. **Aging Report** - Who owes you money
5. **Profit by Job** - Contract-level margins

---

## 🎯 Practical Examples

### Example 1: Government Contract

```
1. Win $2.4M CPS Energy contract (GPSS)
2. Create contract (Contracts table)
3. Order from supplier (Purchase Orders)
4. Deliver to client (Contract Deliveries)
5. Generate invoice ($200K monthly)
6. Track in VERTEX
7. Client pays
8. Update revenue
9. Pay supplier
10. Calculate profit
11. Export to QuickBooks
```

### Example 2: Consulting Project

```
1. Close corporate client (DDCSS)
2. Create project (ATLAS)
3. Track time and expenses
4. Monthly billing
5. Generate invoice from ATLAS
6. Link expenses to invoice
7. Track profit margin
8. Client pays
9. Update VERTEX
```

### Example 3: Surplus Recovery

```
1. Find surplus lead (LBPC)
2. Recover $50K for client
3. Generate 30% fee invoice ($15K)
4. Track in VERTEX
5. Client pays
6. Pure profit (no costs)
7. Update revenue
```

---

## ✅ Summary

### Invoices Table = Central Hub
- Links to ALL source systems
- Universal billing format
- Government compliance built-in
- One place for all revenue

### VERTEX = Financial Intelligence
- Aggregates all invoices
- Tracks all expenses
- Calculates profit margins
- Provides financial visibility
- QuickBooks integration

### Complete Integration:
```
Any System → Generate Invoice → Track in VERTEX → Get Paid → Know Profit
```

**Every dollar that comes in or goes out flows through this system!**

---

## 🚀 Using It

### From GPSS Opportunity:
```
Click opportunity → "Generate Invoice" button → Invoice created → Linked to opportunity
```

### From ATLAS Project:
```
Click project → "Invoice Project" button → Invoice created → Linked to project
```

### From Contract:
```
Delivery completed → Auto-generate invoice → Linked to contract + delivery
```

### View All:
```
Open VERTEX → See all revenue → Filter by system → Track payments
```

**Everything is connected. Nothing falls through!** 💎
