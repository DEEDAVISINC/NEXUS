# 🔄 Airtable Workflow Tracking - Field Definitions

**For GPSS Opportunities Table**

---

## Required Fields to Add

### **Workflow Tracking Fields:**

```
1. Workflow Status (Single Select)
   Options:
   - Needs Review
   - Find Suppliers
   - Request Quotes
   - Awaiting Quotes
   - Ready to Price
   - Generate Proposal
   - Final Review
   - Submitted
   - Awaiting Award
   - Won
   - Lost

2. Workflow Step (Number)
   Values: 1-10
   Tracks current step in workflow

3. Review Status (Single Select)
   Options:
   - Not Reviewed
   - Under Review
   - Reviewed - Pursue
   - Reviewed - Skip

4. Review Date (Date)
   When opportunity was reviewed

5. Reviewed By (Single Line Text)
   Who reviewed it

6. Suppliers Identified (Multiple Record Links)
   Link to Suppliers table
   
7. Suppliers Identified Date (Date)

8. Quotes Requested (Number)
   How many quote requests sent

9. Quotes Requested Date (Date)

10. Quotes Received (Number)
    How many quotes received

11. Quotes Complete (Checkbox)
    All quotes received?

12. Pricing Started Date (Date)

13. Pricing Complete (Checkbox)

14. Final Bid Amount (Currency)

15. Proposal Generated (Checkbox)

16. Proposal Generated Date (Date)

17. Submitted Date (Date/Time)

18. Submission Method (Single Select)
    - Portal
    - Email
    - Mail
    - Hand Delivery
    - Fax

19. Award Decision Date (Date)

20. Award Status (Single Select)
    - Pending
    - Won
    - Lost
    - No Response
```

---

## Formulas for Automation

### **Auto-Calculate Workflow Status:**
```
IF({Review Status} = "Not Reviewed", "Needs Review",
IF(AND({Review Status} = "Reviewed - Pursue", {Suppliers Identified} = BLANK()), "Find Suppliers",
IF(AND(NOT({Suppliers Identified} = BLANK()), {Quotes Requested} = 0), "Request Quotes",
IF(AND({Quotes Requested} > 0, {Quotes Complete} = FALSE()), "Awaiting Quotes",
IF(AND({Quotes Complete} = TRUE(), {Pricing Complete} = FALSE()), "Ready to Price",
IF(AND({Pricing Complete} = TRUE(), {Proposal Generated} = FALSE()), "Generate Proposal",
IF(AND({Proposal Generated} = TRUE(), {Submitted Date} = BLANK()), "Final Review",
IF(NOT({Submitted Date} = BLANK()), "Submitted"
))))))))
```

### **Days in Current Stage:**
```
IF({Workflow Status} = "Needs Review",
   DATETIME_DIFF(NOW(), {Date Added}, 'days'),
IF({Workflow Status} = "Find Suppliers",
   DATETIME_DIFF(NOW(), {Review Date}, 'days'),
IF({Workflow Status} = "Awaiting Quotes",
   DATETIME_DIFF(NOW(), {Quotes Requested Date}, 'days'),
   0
)))
```

### **Stage Duration Tracking:**
```
Review Duration: DATETIME_DIFF({Review Date}, {Date Added}, 'hours')
Supplier Search Duration: DATETIME_DIFF({Suppliers Identified Date}, {Review Date}, 'hours')
Quote Response Duration: DATETIME_DIFF({Quotes Received Date}, {Quotes Requested Date}, 'hours')
```

---

## Views to Create

### **1. Needs Review Queue**
Filter: `{Workflow Status} = "Needs Review"`
Sort: Date Added (oldest first)

### **2. Find Suppliers Queue**
Filter: `{Workflow Status} = "Find Suppliers"`
Sort: Response Deadline (soonest first)

### **3. Request Quotes Queue**
Filter: `{Workflow Status} = "Request Quotes"`
Sort: Response Deadline (soonest first)

### **4. Awaiting Quotes Queue**
Filter: `{Workflow Status} = "Awaiting Quotes"`
Sort: Days in Stage (longest first)

### **5. Ready to Price Queue**
Filter: `{Workflow Status} = "Ready to Price"`
Sort: Response Deadline (soonest first)

### **6. Generate Proposal Queue**
Filter: `{Workflow Status} = "Generate Proposal"`
Sort: Response Deadline (soonest first)

### **7. Final Review Queue**
Filter: `{Workflow Status} = "Final Review"`
Sort: Response Deadline (soonest first)

---

## API Endpoints Needed

### **Get Workflow Queues**
```python
GET /api/workflow/queues
Response:
{
  "needsReview": [...opportunities],
  "findSuppliers": [...opportunities],
  "requestQuotes": [...opportunities],
  "awaitingQuotes": [...opportunities],
  "readyToPrice": [...opportunities],
  "generateProposal": [...opportunities],
  "finalReview": [...opportunities]
}
```

### **Move to Next Step**
```python
POST /api/workflow/opportunity/{id}/advance
Body: { "action": "reviewed", "data": {...} }
Response: { "success": true, "newStatus": "Find Suppliers" }
```

### **Review Opportunity**
```python
POST /api/workflow/opportunity/{id}/review
Body: {
  "name": "CPS Energy - Industrial Supplies",
  "decision": "pursue" | "skip",
  "notes": "..."
}
```

### **Identify Suppliers**
```python
POST /api/workflow/opportunity/{id}/suppliers
Body: {
  "supplierIds": ["rec123", "rec456", "rec789"]
}
```

### **Request Quotes**
```python
POST /api/workflow/opportunity/{id}/request-quotes
Body: {
  "supplierIds": ["rec123", "rec456"],
  "dueDate": "2026-02-01"
}
```

---

## Implementation Steps

### **1. Add Fields to Airtable (Manual)**
- Go to GPSS Opportunities table
- Add all workflow tracking fields
- Set up formulas
- Create views

### **2. Backend API (Python)**
```python
# Add to nexus_backend.py

class WorkflowManager:
    def __init__(self):
        self.airtable = AirtableClient()
    
    def get_workflow_queues(self):
        """Get all workflow queues"""
        opportunities = self.airtable.get_all_opportunities()
        
        queues = {
            'needsReview': [],
            'findSuppliers': [],
            'requestQuotes': [],
            'awaitingQuotes': [],
            'readyToPrice': [],
            'generateProposal': [],
            'finalReview': []
        }
        
        for opp in opportunities:
            status = opp['fields'].get('Workflow Status', 'Needs Review')
            if status == 'Needs Review':
                queues['needsReview'].append(opp)
            elif status == 'Find Suppliers':
                queues['findSuppliers'].append(opp)
            # ... etc
        
        return queues
    
    def review_opportunity(self, opp_id, name, decision, notes):
        """Review and name an opportunity"""
        updates = {
            'Name': name,
            'Review Status': 'Reviewed - Pursue' if decision == 'pursue' else 'Reviewed - Skip',
            'Review Date': datetime.now().isoformat(),
            'Reviewed By': 'Dee Davis',
            'Review Notes': notes
        }
        
        self.airtable.update_opportunity(opp_id, updates)
        
        return {
            'success': True,
            'newStatus': 'Find Suppliers' if decision == 'pursue' else 'Skipped'
        }
    
    def identify_suppliers(self, opp_id, supplier_ids):
        """Link suppliers to opportunity"""
        updates = {
            'Suppliers Identified': supplier_ids,
            'Suppliers Identified Date': datetime.now().isoformat()
        }
        
        self.airtable.update_opportunity(opp_id, updates)
        
        return {'success': True, 'newStatus': 'Request Quotes'}
```

### **3. Frontend Integration (React)**
```typescript
// Update LandingPage.tsx to fetch real queues

const [workflowQueues, setWorkflowQueues] = useState({
  needsReview: [],
  findSuppliers: [],
  requestQuotes: [],
  awaitingQuotes: [],
  readyToPrice: [],
  generateProposal: [],
  finalReview: []
});

const fetchWorkflowQueues = async () => {
  const response = await api.getWorkflowQueues();
  setWorkflowQueues(response);
};

// Use real data in sections
{workflowQueues.needsReview.map(opp => (
  <div>
    <h3>{opp.fields.Name || 'Unnamed Opportunity'}</h3>
    <button onClick={() => reviewOpportunity(opp.id)}>
      Review & Name
    </button>
  </div>
))}
```

---

## Quick Start Commands

### **1. Add Fields to Airtable**
Manually add all fields listed above to GPSS Opportunities table

### **2. Test Workflow**
```bash
# Get current queues
curl http://localhost:8000/api/workflow/queues

# Review an opportunity
curl -X POST http://localhost:8000/api/workflow/opportunity/rec123/review \
  -H "Content-Type: application/json" \
  -d '{
    "name": "CPS Energy - Industrial Supplies",
    "decision": "pursue",
    "notes": "Good fit, high value"
  }'

# Add suppliers
curl -X POST http://localhost:8000/api/workflow/opportunity/rec123/suppliers \
  -H "Content-Type: application/json" \
  -d '{
    "supplierIds": ["rec456", "rec789", "rec101"]
  }'
```

---

## Expected Behavior

### **User Flow:**
1. Dashboard shows 3 unnamed opportunities in "NEEDS REVIEW"
2. User clicks "Review & Name" on first one
3. Modal opens with opportunity details
4. User enters name: "CPS Energy - Industrial Supplies"
5. User selects "Pursue This"
6. User clicks "Save"

### **System Actions:**
1. POST to `/api/workflow/opportunity/{id}/review`
2. Airtable updates: Name, Review Status, Review Date
3. Formula auto-calculates: Workflow Status = "Find Suppliers"
4. Dashboard refreshes
5. "NEEDS REVIEW" now shows 2 items (not 3)
6. "FIND SUPPLIERS" now shows 1 item (the reviewed one)

### **Result:**
- Item moved from one queue to another
- Counter updated
- Next unnamed opportunity moved up in queue
- Clear progress visible

---

**This creates a fully functional, Airtable-backed workflow tracking system!** 🎯
