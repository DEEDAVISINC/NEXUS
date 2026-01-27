# 🚀 Quick Setup - Quote & Capability Statement Systems

**Get your new systems visible in NEXUS in 5 minutes!**

---

## ✅ What's Already Done

1. ✅ Backend modules added to `nexus_backend.py`
2. ✅ Frontend components created (`QuoteSystem.tsx`, `CapStatSystem.tsx`)
3. ✅ Routing configured in App.tsx
4. ✅ System cards added to landing page
5. ✅ Quick action button added

---

## 🎯 To See It Right Now

### Option 1: Development Mode (Quickest!)

```bash
# Terminal 1: Start the frontend
cd "/Users/deedavis/NEXUS BACKEND/nexus-frontend"
npm start

# Your browser will open to http://localhost:3000
# You'll see two new system cards:
# - 📋 QUOTES (blue gradient)
# - 📄 CAP STATS (purple gradient)
```

**That's it!** The systems are already visible on the landing page!

### Option 2: Test Individual Components

```bash
# Just verify the React components compile
cd "/Users/deedavis/NEXUS BACKEND/nexus-frontend"
npm start
```

---

## 🔧 What You'll See

### Landing Page:
- **NEW Card:** 📋 **QUOTES** - Supplier Quote System
  - Blue/cyan gradient
  - Shows: "0 Pending Quotes | 0 Sent This Month | 0% Response Rate"
  - Click to enter Quote System

- **NEW Card:** 📄 **CAP STATS** - Capability Statement Generator
  - Purple/indigo gradient
  - Shows: "0 Generated | 5 Templates | Ready to Use!"
  - Click to enter CapStat System

- **NEW Quick Action:** 📋 **Request Quote** button (top of page)

### Quote System Page:
- Generate Quotes tab
- Track Requests tab
- Paste mode (pre-loaded template)
- Form mode (coming soon)
- Generate button creates professional PDFs

### CapStat System Page:
- Generate tab
- Templates tab
- Paste mode with template
- Generate button creates capability statements

---

## 📋 Current Status

### ✅ Working Right Now:
- Frontend UI is fully functional
- Paste templates work
- Generate buttons trigger API calls
- Navigation works (back to NEXUS, between tabs)
- Beautiful NEXUS-style UI

### ⏳ Needs Backend Connection:
The frontend is trying to connect to:
- `http://localhost:5000/api/quote/generate-from-paste`
- `http://localhost:5000/api/capstat/generate-from-paste`

**Two Options:**

#### Option A: Use Standalone API (Already Built!)
```bash
# Terminal 2: Start the quote API
cd "/Users/deedavis/NEXUS BACKEND"
python3 quote_generator_api.py

# Runs on port 5000
# Frontend will connect automatically
```

#### Option B: Add to Main NEXUS Backend
Add these routes to your main NEXUS API server (wherever Flask routes are):

```python
# In your main API file (api_server.py or similar)
from nexus_backend import SupplierQuoteSystem, CapabilityStatementSystem

@app.route('/api/quote/generate-from-paste', methods=['POST'])
def generate_quote_from_paste():
    data = request.json
    paste_text = data.get('paste_text', '')
    
    # Call the generator
    result = subprocess.run(
        ['python3', 'create_from_paste.py', 'rfq', '-'],
        input=paste_text,
        capture_output=True,
        text=True,
        cwd=os.path.dirname(__file__)
    )
    
    return jsonify({
        'success': result.returncode == 0,
        'output': result.stdout
    })

@app.route('/api/capstat/generate-from-paste', methods=['POST'])
def generate_capstat_from_paste():
    data = request.json
    paste_text = data.get('paste_text', '')
    
    # Call the generator
    result = subprocess.run(
        ['python3', 'create_from_paste.py', 'capability', '-'],
        input=paste_text,
        capture_output=True,
        text=True,
        cwd=os.path.dirname(__file__)
    )
    
    return jsonify({
        'success': result.returncode == 0,
        'output': result.stdout
    })
```

---

## 🎯 Quick Test

### 1. Start Frontend
```bash
cd "/Users/deedavis/NEXUS BACKEND/nexus-frontend"
npm start
```

### 2. Open Browser
Go to: `http://localhost:3000`

### 3. See Your New Systems!
- Scroll to see the new system cards
- Click 📋 **QUOTES** to enter Quote System
- Click 📄 **CAP STATS** to enter CapStat System
- Click "Load Template" to see a pre-filled example
- Click "Generate" to create a PDF (needs backend running)

---

## 📦 If You Get Errors

### "Module not found" errors:
```bash
cd nexus-frontend
npm install
```

### "Port 3000 already in use":
```bash
# Kill existing process
lsof -ti:3000 | xargs kill -9

# Then restart
npm start
```

### Backend connection fails:
```bash
# Option 1: Start standalone API
python3 quote_generator_api.py

# Option 2: Check your main NEXUS backend is running
# And has the new routes
```

---

## 🎨 Customize

### Change Colors:
Edit the `gradient` property in `LandingPage.tsx`:
```typescript
gradient: 'from-blue-600 to-cyan-600'  // Quote System
gradient: 'from-purple-600 to-indigo-600'  // CapStat System
```

### Change Stats:
Edit the `stats` array:
```typescript
stats: [
  '12 Pending Quotes',  // Your actual numbers
  '45 Sent This Month',
  '85% Response Rate'
]
```

### Add Icons:
Change the `icon` property:
```typescript
icon: '📋'  // Quote System
icon: '📄'  // CapStat System
```

---

## 🚀 Next Level

### Connect to Airtable:
1. Create "Quote Requests" table (see `QUOTE_REQUESTS_AIRTABLE_SCHEMA.md`)
2. Add backend code to log to Airtable
3. Stats will update automatically!

### Add "Request Quote" to Opportunities:
```typescript
// In OpportunityCard component
<button onClick={() => requestQuote(opportunity.id)}>
  📋 Request Supplier Quotes
</button>
```

### Enable Follow-ups:
```bash
# Add daily cron job
0 9 * * * cd /Users/deedavis/NEXUS\ BACKEND && python3 -c "from supplier_quote_workflow import check_and_send_followups; check_and_send_followups()"
```

---

## ✅ Summary

**Right now, with zero additional work, you can:**

1. Run `npm start` in nexus-frontend
2. See two new beautiful system cards on your landing page
3. Click them to enter the Quote and CapStat systems
4. Use paste mode with templates
5. Generate professional PDFs (if backend running)

**The systems are LIVE and ready to use!** 🎉

Just start the frontend and you'll see them on your landing page!

---

## 🆘 Need Help?

**Can't see the new cards?**
- Make sure you're running the latest code
- Try: `cd nexus-frontend && npm start`
- Clear browser cache: Cmd+Shift+R (Mac) or Ctrl+Shift+R (Windows)

**Cards visible but can't generate?**
- Start the backend: `python3 quote_generator_api.py`
- Or add routes to your main NEXUS backend

**Other issues?**
- Check console for errors: F12 → Console
- Make sure all dependencies installed: `npm install`
