# Quote Requests Table - Airtable Schema

**Table Name:** `Quote Requests`

**Purpose:** Track supplier quote requests sent from solicitations, with timestamps and follow-up automation.

---

## Fields

| Field Name | Type | Description | Options |
|------------|------|-------------|---------|
| **Name** | Formula | Auto-generated | `{Opportunity} & " → " & {Supplier}` |
| **Opportunity** | Link to Opportunities | Link to the solicitation/bid | |
| **Supplier** | Link to Suppliers | Supplier the request was sent to | |
| **Sent Date** | Date & Time | When quote request was sent | Include time |
| **Sent Method** | Single Select | How it was sent | `Email`, `Fax`, `Phone`, `Portal` |
| **Sent To** | Single Line Text | Email address or fax number | |
| **Status** | Single Select | Current status | `Sent`, `Received`, `Quoted`, `Declined`, `No Response`, `Failed` |
| **PDF Path** | Single Line Text | Path to generated quote request PDF | |
| **Due Date** | Date | When we need the quote by | |
| **Quote Received Date** | Date & Time | When supplier responded | Include time |
| **Quote Amount** | Currency | Total quoted price | $ |
| **Follow-up Needed** | Checkbox | Auto-check if no response | |
| **Follow-up Date** | Date | When to follow up | |
| **Follow-up Count** | Number | How many follow-ups sent | Integer |
| **Last Follow-up** | Date & Time | Last follow-up timestamp | Include time |
| **Notes** | Long Text | Internal notes | |
| **Response Time** | Formula | Days from sent to received | `DATETIME_DIFF({Quote Received Date}, {Sent Date}, 'days')` |

---

## Views

### 1. **Pending Quotes**
- Filter: `Status = "Sent"`
- Sort: Due Date (ascending)
- Group: Opportunity

### 2. **Need Follow-up**
- Filter: `AND(Follow-up Needed, Follow-up Date <= TODAY(), Status = "Sent")`
- Sort: Follow-up Date (ascending)
- Group: Supplier

### 3. **Received Quotes**
- Filter: `Status = "Quoted"`
- Sort: Quote Received Date (descending)
- Group: Opportunity

### 4. **No Response**
- Filter: `AND(Status = "Sent", Due Date < TODAY())`
- Sort: Due Date (ascending)

### 5. **All Requests**
- Filter: None
- Sort: Sent Date (descending)

---

## Automations

### 1. **Auto Follow-up Reminder**
**Trigger:** When Follow-up Date arrives
**Action:** Send Slack/email notification to follow up

### 2. **Mark Overdue**
**Trigger:** When Due Date passes and Status = "Sent"
**Action:** Change Status to "No Response"

### 3. **Log to Opportunity**
**Trigger:** When Quote Received
**Action:** Update Opportunity with quote count and amounts

---

## API Usage

```python
from supplier_quote_workflow import request_quotes_for_opportunity

# When you find a solicitation to bid on:
result = request_quotes_for_opportunity('opp_rec_id')

# System automatically:
# 1. Extracts items from solicitation
# 2. Finds matching suppliers
# 3. Generates quote PDFs
# 4. Emails/faxes to suppliers
# 5. Logs to this table with timestamp
# 6. Schedules follow-up
```

---

## Workflow Integration

### Step 1: Find Solicitation (ATLAS/GPSS)
Solicitation added to Opportunities table

### Step 2: Request Quotes Button
Click "Request Supplier Quotes" button in NEXUS

### Step 3: Auto-Process
- System finds suppliers
- Generates quote requests
- Sends via email/fax
- Creates records here with timestamps

### Step 4: Track Status
View in "Pending Quotes" view

### Step 5: Auto Follow-up
System checks daily, sends follow-ups automatically

### Step 6: Record Quote
When supplier responds, update Status to "Quoted" and add amount

### Step 7: Price Bid
Use quote amounts to price your bid with margin

---

## Quick Setup

```bash
# Create the table in Airtable
1. Go to your NEXUS base
2. Add new table: "Quote Requests"
3. Add all fields listed above
4. Create views as specified
5. Set up automations (optional)
```

---

## Example Record

```json
{
  "Opportunity": ["Sterling Heights Aggregates"],
  "Supplier": ["Detroit Salt Company"],
  "Sent Date": "2026-01-26T10:30:00",
  "Sent Method": "Email",
  "Sent To": "quotes@detroitsalt.com",
  "Status": "Sent",
  "Due Date": "2026-02-02",
  "Follow-up Needed": true,
  "Follow-up Date": "2026-01-29",
  "Follow-up Count": 0
}
```

After supplier responds:
```json
{
  "Status": "Quoted",
  "Quote Received Date": "2026-01-28T14:20:00",
  "Quote Amount": 42000,
  "Follow-up Needed": false,
  "Response Time": 2
}
```

---

## Dashboard Metrics

Track:
- **Response Rate:** % of quotes that get responses
- **Average Response Time:** Days from sent to received
- **Best Suppliers:** Suppliers with fastest response times
- **Follow-up Effectiveness:** Response rate after follow-ups

---

## Integration with Pricing

Once quotes received:

```python
# Get all quotes for opportunity
quotes = get_quotes_for_opportunity(opp_id)

# Find best price
best_quote = min(quotes, key=lambda x: x['Quote Amount'])

# Calculate your bid
your_bid = best_quote['Quote Amount'] * 1.15  # 15% margin

# Submit bid
```

---

**This table completes the workflow loop from solicitation to quote to bid!**
