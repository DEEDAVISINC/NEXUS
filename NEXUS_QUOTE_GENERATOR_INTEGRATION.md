# 🚀 NEXUS Quote Generator Integration

**Integrated supplier quote request system for NEXUS**

---

## ✅ What Was Built

### Backend API (`quote_generator_api.py`)
- REST API endpoints for quote generation
- Runs on port 5001 (separate from main NEXUS backend)
- Automatically converts JSON data to professional PDFs
- Stores generated quotes in `GENERATED_QUOTES/` folder

### Frontend Component (`QuoteGenerator.tsx`)
- Beautiful React interface
- Form-based data entry
- Real-time quote generation
- Instant PDF download

---

## 🚀 Quick Start

### Step 1: Start the Quote Generator API

```bash
cd "/Users/deedavis/NEXUS BACKEND"
python3 quote_generator_api.py
```

You'll see:
```
============================================================
🚀 NEXUS Quote Generator API
============================================================
Output directory: /Users/deedavis/NEXUS BACKEND/GENERATED_QUOTES
API running on: http://localhost:5001
Frontend should connect to: http://localhost:5001/api/quote/
============================================================
```

**Leave this running!**

### Step 2: Add to NEXUS Frontend

The QuoteGenerator component is ready at:
```
nexus-frontend/src/components/QuoteGenerator.tsx
```

Add it to your main NEXUS interface by editing `App.tsx`:

```typescript
import { QuoteGenerator } from './components/QuoteGenerator';

// Add to your navigation/tabs:
<Tab label="Quote Generator">
  <QuoteGenerator />
</Tab>
```

### Step 3: Start NEXUS Frontend

```bash
cd nexus-frontend
npm start
```

---

## 📋 API Endpoints

### 1. Generate Quote
```
POST /api/quote/generate
```

**Body:**
```json
{
  "rfq_number": "DDI-2026-001",
  "title": "Aggregate Materials - Annual Contract",
  "issue_date": "January 26, 2026",
  "due_date": "February 5, 2026",
  "due_time": "5:00 PM EST",
  "contract_period": "12 months",
  "color_scheme": "1",
  "introduction": "DEE DAVIS INC is seeking quotes...",
  "scope": "Vendor will provide...",
  "requirements": [
    "Competitive pricing",
    "Fast delivery"
  ],
  "items": [
    {
      "number": "1",
      "description": "Fill Sand",
      "specs": "Clear of debris",
      "quantity": "300 tons",
      "unit": "ton"
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "files": {
    "html": "GENERATED_QUOTES/rfq_ddi_2026_001.html",
    "pdf": "GENERATED_QUOTES/rfq_ddi_2026_001.pdf",
    "config": "GENERATED_QUOTES/rfq_ddi_2026_001_config.json"
  },
  "download_url": "/api/quote/download/rfq_ddi_2026_001.pdf"
}
```

### 2. Download Generated File
```
GET /api/quote/download/<filename>
```

### 3. Get Template
```
GET /api/quote/template
```

Returns a blank template with all fields.

### 4. Health Check
```
GET /api/quote/health
```

---

## 🎯 How It Works

### User Flow:
1. User opens Quote Generator in NEXUS
2. Fills in form with quote details and items
3. Clicks "Generate Quote Request"
4. API processes request and creates PDF
5. User downloads professional PDF
6. Email to suppliers!

### Behind the Scenes:
1. React form sends JSON to API
2. API converts JSON to template format
3. Calls `create_from_paste.py` to generate docs
4. Returns file paths and download link
5. User clicks download button
6. PDF downloaded to computer

---

## 💡 Integration Examples

### Example 1: From Opportunity Data

If you have an opportunity in Airtable, you can auto-populate the form:

```typescript
// In your NEXUS frontend
const opportunity = getOpportunityFromAirtable(id);

const quoteData = {
  rfq_number: `DDI-2026-${opportunity.id}`,
  title: opportunity.title,
  due_date: calculateDueDate(opportunity.deadline), // Before opp deadline!
  items: opportunity.items.map((item, index) => ({
    number: String(index + 1),
    description: item.description,
    specs: item.specifications,
    quantity: item.quantity,
    unit: item.unit
  }))
};

// Send to API
generateQuote(quoteData);
```

### Example 2: Quick Quote Button

Add a "Request Quotes" button to any opportunity:

```typescript
<OpportunityCard opportunity={opp}>
  <Button onClick={() => {
    // Auto-fill quote generator with opp data
    navigate('/quote-generator', { state: { opportunity: opp } });
  }}>
    📋 Request Supplier Quotes
  </Button>
</OpportunityCard>
```

---

## 🔧 Configuration

### Color Schemes
```
1 = Navy/Gold (Industrial)
2 = Brown/Orange (Construction)
3 = Purple/Violet (Technology)
4 = Blue/Teal (Healthcare)
5 = Dark Brown (Aggregates/Materials)
```

### Output Location
All generated files go to:
```
/Users/deedavis/NEXUS BACKEND/GENERATED_QUOTES/
```

---

## 🎨 Frontend Customization

The React component is fully customizable. Edit `QuoteGenerator.tsx` to:

- Change colors
- Add/remove fields
- Integrate with Airtable
- Add email automation
- Connect to supplier database

---

## 🚀 Advanced: Auto-Email to Suppliers

Add this to automatically email generated quotes to suppliers:

```python
# In quote_generator_api.py

@app.route('/api/quote/generate-and-email', methods=['POST'])
def generate_and_email():
    data = request.json
    
    # Generate quote
    result = generate_quote_internal(data)
    
    # Get supplier emails from data
    supplier_emails = data.get('supplier_emails', [])
    
    # Send emails
    for email in supplier_emails:
        send_email(
            to=email,
            subject=f"Quote Request - {data['title']}",
            body=f"Please see attached quote request...",
            attachment=result['files']['pdf']
        )
    
    return jsonify({'success': True, 'emails_sent': len(supplier_emails)})
```

---

## 📊 Usage Statistics

Track quote generation in Airtable:

```python
# Log to Airtable after generation
airtable.create('Quote Requests Generated', {
    'RFQ Number': data['rfq_number'],
    'Title': data['title'],
    'Generated At': datetime.now().isoformat(),
    'Item Count': len(data['items']),
    'Opportunity Link': data.get('opportunity_id')
})
```

---

## ✅ Installation Checklist

- [ ] API file created: `quote_generator_api.py`
- [ ] React component created: `QuoteGenerator.tsx`
- [ ] Start API: `python3 quote_generator_api.py`
- [ ] Verify API: Visit `http://localhost:5001/api/quote/health`
- [ ] Add component to NEXUS frontend
- [ ] Test: Generate a sample quote
- [ ] Verify: Check `GENERATED_QUOTES/` folder
- [ ] Download: Click download button, get PDF
- [ ] Success! ✨

---

## 🎯 Real-World Workflow

**You see Sterling Heights aggregate solicitation:**

1. Open NEXUS
2. Click "Quote Generator" tab
3. Auto-fills from opportunity data (or paste items)
4. Click "Generate"
5. PDF created in 2 seconds
6. Click "Download PDF"
7. Email to Detroit Salt, Stoneco, Martin Marietta
8. Get quotes back
9. Price your bid with margin
10. Win the contract! 🎉

**Time: 30 seconds from solicitation to supplier request!**

---

## 🆘 Troubleshooting

**API won't start:**
```bash
pip install flask flask-cors
```

**Frontend can't connect:**
Check API is running on port 5001:
```bash
curl http://localhost:5001/api/quote/health
```

**No PDF generated:**
Check `GENERATED_QUOTES/` folder for HTML file (always generates).
For PDF, ensure wkhtmltopdf is installed or use reportlab.

**Component not showing:**
Make sure you imported and added to App.tsx:
```typescript
import { QuoteGenerator } from './components/QuoteGenerator';
```

---

## 🎉 You're Done!

**Your NEXUS system now has integrated quote generation!**

Start the API, open NEXUS, and generate professional quote requests in seconds!

---

**Built for DEE DAVIS INC - Integrated into NEXUS** 🚀
