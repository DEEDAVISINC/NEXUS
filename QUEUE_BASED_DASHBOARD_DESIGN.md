# 🎯 Queue-Based Systematic Dashboard Design

**Principle: Organize by ACTION TYPE, not by individual opportunity**

---

## 📊 Dashboard Structure

### **Each Section = One Type of Action**

When you complete an action in one section:
1. Item disappears from that section
2. Next item in queue moves up
3. Item appears in next appropriate section
4. When section is empty → "All caught up!"

---

## 🔄 The Systematic Workflow Sections

### **1. 🔍 NEEDS REVIEW**
**Purpose:** First step - review all new/unnamed opportunities

**Shows:**
```
🔍 NEEDS REVIEW (3 items)

1. Unnamed Opportunity - Municipal Supplies
   Added: 2 hours ago | Source: Email
   [Review & Name] [Skip]

2. Unnamed Opportunity - Road Salt Contract  
   Added: 5 hours ago | Source: SAM.gov
   [Review & Name] [Skip]

3. Unnamed Opportunity - Janitorial Services
   Added: Yesterday | Source: Portal
   [Review & Name] [Skip]
```

**Actions:**
- Click "Review & Name" → Opens detail modal
- You review specs, name it, decide to pursue or skip
- Item disappears from this section
- Moves to "FIND SUPPLIERS" (if pursuing) or archived (if skipping)
- Next unnamed opportunity moves up

**When Empty:**
```
🔍 NEEDS REVIEW
✅ All caught up! No opportunities need review.
```

---

### **2. 🔎 FIND SUPPLIERS**
**Purpose:** Identify and select suppliers for opportunities

**Shows:**
```
🔎 FIND SUPPLIERS (2 items)

1. CPS Energy - Industrial Supplies | Due: Feb 5
   [Search Suppliers] [Add Supplier]

2. Canton Township - Water Infrastructure | Due: Feb 10
   [Search Suppliers] [Add Supplier]
```

**Actions:**
- Click "Search Suppliers" → Opens supplier search
- Select 3-5 suppliers
- Mark as "Suppliers Identified"
- Item disappears from this section
- Moves to "REQUEST QUOTES"

**When Empty:**
```
🔎 FIND SUPPLIERS
✅ All suppliers identified for active bids.
```

---

### **3. 📋 REQUEST QUOTES**
**Purpose:** Send quote requests to selected suppliers

**Shows:**
```
📋 REQUEST QUOTES (2 items)

1. Sterling Heights - Aggregates | Due: Jan 28 (2 days)
   3 suppliers selected
   [Generate & Send Quotes]

2. Oakland County - Body Bags | Due: Feb 10
   4 suppliers selected
   [Generate & Send Quotes]
```

**Actions:**
- Click "Generate & Send Quotes"
- System generates PDFs, sends emails
- Timestamps and tracks
- Item disappears from this section
- Moves to "AWAITING QUOTES"

**When Empty:**
```
📋 REQUEST QUOTES
✅ All quote requests sent.
```

---

### **4. ⏳ AWAITING QUOTES**
**Purpose:** Track quote responses, send follow-ups

**Shows:**
```
⏳ AWAITING QUOTES (3 items)

1. CPS Energy - Industrial Supplies
   Quotes: 3 of 5 received (60%)
   ├─ ✅ Fastenal: $38K (Jan 24)
   ├─ ✅ Detroit Salt: $41K (Jan 25)  
   ├─ ✅ Cut King: $39K (Jan 25)
   ├─ ⏰ Grainger: Sent follow-up (Jan 25)
   └─ ⏰ Sunbelt Mill: Sent follow-up (Jan 25)
   [Send Follow-ups] [Proceed with 3 Quotes]

2. Madison Heights - Lawn Service
   Quotes: 0 of 3 received (0%)
   ├─ ⏰ Leys Lawn Care: Sent Jan 23 (3 days ago)
   ├─ ⏰ Green Thumb: Sent Jan 23 (3 days ago)
   └─ ⏰ Pro Landscaping: Sent Jan 23 (3 days ago)
   [Send Follow-ups] [Call Suppliers]

3. Sterling Heights - Aggregates
   Quotes: 3 of 3 received (100%) ✅
   [Move to Pricing]
```

**Actions:**
- Automatic follow-ups at 3 days
- Click "Send Follow-ups" to manually remind
- Click "Proceed with X Quotes" to move forward
- When all quotes received → "Move to Pricing" button appears
- Item moves to "READY TO PRICE"

**When Empty:**
```
⏳ AWAITING QUOTES
✅ All quotes received.
```

---

### **5. 💰 READY TO PRICE**
**Purpose:** Price bids with received quotes

**Shows:**
```
💰 READY TO PRICE (2 items)

1. Sterling Heights - Aggregates | Due: Jan 28 (2 days) ⚠️
   3 quotes received | Lowest: $120K | Highest: $145K
   [Start Pricing Calculator]

2. Oakland County - Body Bags | Due: Feb 10
   4 quotes received | Lowest: $8K | Highest: $12K
   [Start Pricing Calculator]
```

**Actions:**
- Click "Start Pricing Calculator"
- Compare quotes, calculate markup
- Set final bid price
- Item disappears from this section
- Moves to "GENERATE PROPOSAL"

**When Empty:**
```
💰 READY TO PRICE
✅ All bids priced.
```

---

### **6. 📄 GENERATE PROPOSAL**
**Purpose:** Create proposal documents

**Shows:**
```
📄 GENERATE PROPOSAL (1 item)

1. CPS Energy - Industrial Supplies | Due: Feb 5
   Pricing complete: $420,000
   [Generate Capability Statement] [Generate Proposal]
```

**Actions:**
- Click "Generate Capability Statement" → Opens cap stat generator
- Click "Generate Proposal" → Creates full bid package
- Item moves to "FINAL REVIEW"

**When Empty:**
```
📄 GENERATE PROPOSAL
✅ All proposals generated.
```

---

### **7. 👁️ FINAL REVIEW**
**Purpose:** Review before submission

**Shows:**
```
👁️ FINAL REVIEW (2 items)

1. Sterling Heights - Aggregates | Due: Jan 28 (1 day) ⚠️
   Proposal generated | All docs ready
   [Review Package] [Submit Now]

2. Oakland County - Body Bags | Due: Feb 10
   Proposal generated | All docs ready
   [Review Package] [Submit Now]
```

**Actions:**
- Click "Review Package" → Opens document preview
- Click "Submit Now" → Submits bid
- Confirmation required
- Item moves to "AWAITING AWARD"

**When Empty:**
```
👁️ FINAL REVIEW
✅ All bids submitted.
```

---

### **8. ✅ PENDING APPROVALS**
**Purpose:** Approve payments, invoices, contracts

**Shows:**
```
✅ PENDING APPROVALS (3 items)

PAYMENTS (2)
├─ Grainger: $42,000 | For: CPS Energy supplies
│  [Review] [Approve] [Decline]
└─ Detroit Salt: $15,000 | For: Madison Heights salt
   [Review] [Approve] [Decline]

INVOICES (1)
└─ Canton Township: $25,000 | Invoice #INV-2026-008
   [Review] [Send to Client]
```

**Actions:**
- Click "Review" → See full details
- Click "Approve" → Processes payment
- Click "Decline" → Needs correction
- Click "Send to Client" → Emails invoice
- Item disappears when approved

**When Empty:**
```
✅ PENDING APPROVALS
✅ Nothing pending approval.
```

---

## 🎨 Visual Design

### Section Layout:

```
┌─────────────────────────────────────────┐
│ 🔍 NEEDS REVIEW (3)                     │
├─────────────────────────────────────────┤
│ [Queue of items needing review]         │
│ • Item 1                                │
│ • Item 2                                │
│ • Item 3                                │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ 🔎 FIND SUPPLIERS (2)                   │
├─────────────────────────────────────────┤
│ [Queue of items needing suppliers]      │
│ • Item 1                                │
│ • Item 2                                │
└─────────────────────────────────────────┘

... and so on
```

### Compact Design:
- Each section shows only 3-4 items max
- "View All (7)" link to see full queue
- Collapsible sections (click header to expand/collapse)
- Color-coded by urgency (red = urgent, yellow = soon, green = plenty of time)

---

## 🔄 Complete User Journey Example

### Day 1: Morning Check

**You open NEXUS Dashboard:**

```
🔍 NEEDS REVIEW (3)
├─ Unnamed Opportunity #1 [Review & Name]
├─ Unnamed Opportunity #2 [Review & Name]
└─ Unnamed Opportunity #3 [Review & Name]

⏳ AWAITING QUOTES (2)
├─ CPS Energy: 3 of 5 quotes
└─ Madison Heights: 0 of 3 quotes

💰 READY TO PRICE (1)
└─ Sterling Heights [Start Pricing]

✅ PENDING APPROVALS (2)
├─ Payment: Grainger $42K [Approve]
└─ Invoice: Canton $25K [Send]
```

### You take action:

**Step 1: Review unnamed opportunity #1**
- Click "Review & Name"
- Read specs: "Oakland County Body Bags"
- Name it: "Oakland County - Medical Supplies"
- Decision: "Pursue This"
- Item disappears from "NEEDS REVIEW"

**Dashboard updates automatically:**
```
🔍 NEEDS REVIEW (2)  ← Now shows 2 instead of 3
├─ Unnamed Opportunity #2 [Review & Name]  ← #2 moved up to #1 position
└─ Unnamed Opportunity #3 [Review & Name]

🔎 FIND SUPPLIERS (1)  ← New section appears
└─ Oakland County - Medical Supplies [Search Suppliers]  ← Your reviewed item
```

**Step 2: Find suppliers for Oakland County**
- Click "Search Suppliers"
- Select 4 suppliers
- Click "Save Suppliers"
- Item disappears from "FIND SUPPLIERS"

**Dashboard updates:**
```
🔎 FIND SUPPLIERS  ← Section now empty
✅ All suppliers identified.

📋 REQUEST QUOTES (1)  ← Item moved here
└─ Oakland County - Medical Supplies [Generate & Send]
```

**Step 3: Send quote requests**
- Click "Generate & Send"
- System sends 4 emails
- Item moves to "AWAITING QUOTES"

**And so on...**

---

## 💡 Key Benefits

### For You:
✅ **Clear focus** - See exactly what needs doing
✅ **No confusion** - Each section = one action type
✅ **Progress visible** - Watch items move through workflow
✅ **Nothing missed** - Empty sections = caught up
✅ **Efficient** - Batch similar actions together

### Systematic:
✅ **Sequential** - Can't skip required steps
✅ **Organized** - Similar items grouped
✅ **Predictable** - Always know what's next
✅ **Automated** - Items move automatically when action complete

---

## 🎯 Implementation Notes

### Data Structure:
```typescript
interface WorkflowQueue {
  needsReview: Opportunity[];      // Step 1
  findSuppliers: Opportunity[];    // Step 2
  requestQuotes: Opportunity[];    // Step 3
  awaitingQuotes: Opportunity[];   // Step 4
  readyToPrice: Opportunity[];     // Step 5
  generateProposal: Opportunity[]; // Step 6
  finalReview: Opportunity[];      // Step 7
  pendingApprovals: Approval[];    // Separate queue
}
```

### When User Takes Action:
```typescript
function completeAction(opportunityId, currentQueue, nextQueue) {
  // Remove from current queue
  removeFromQueue(opportunityId, currentQueue);
  
  // Add to next queue
  addToQueue(opportunityId, nextQueue);
  
  // Update dashboard
  refreshDashboard();
}
```

---

## ✅ Ready to Build?

This is a **queue-based, systematic workflow dashboard** where:
- Each section shows items needing the SAME action
- When you complete an action, item moves to next appropriate queue
- No more scrolling through individual opportunities
- Crystal clear what needs to be done

**Should I implement this design now?**
