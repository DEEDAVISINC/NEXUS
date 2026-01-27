# 🚀 How to Use the Quote Generator - REAL MODE

**The Quote Generator is now running and generating REAL PDFs!**

---

## ✅ Current Status

- ✅ Backend API is running on port 5001
- ✅ Frontend is connected to backend
- ✅ PDFs are being generated in `GENERATED_QUOTES/` folder
- ✅ Download button works
- ✅ Ready to use for your business!

---

## 📋 How to Use It

### **Step 1: Open NEXUS Locally**

Since the backend runs on your computer (localhost), you need to run NEXUS locally:

```bash
cd "/Users/deedavis/NEXUS BACKEND/nexus-frontend"
npm start
```

This will open NEXUS on `http://localhost:3000`

### **Step 2: Navigate to Quote System**

1. Scroll down to "INTEGRATED SYSTEMS"
2. Click the **📋 QUOTES** card
3. You'll see "Paste Mode" (recommended!)

### **Step 3: Generate a Quote**

**Option A: Use Template (Easiest)**
1. Click "Load Template"
2. Edit the information:
```
RFQ_NUMBER: DDI-2026-001
TITLE: Industrial Wipers Quote Request
DUE_DATE: February 5, 2026
DUE_TIME: 2:00 PM EST

ITEMS:
1 | Industrial Wipers | Bulk pack 1000ct | 50 | box
2 | Safety Gloves | Nitrile XL | 100 | box
```

**Option B: Paste Your Own**
Paste info from a solicitation you're working on!

3. Click "✨ Generate Quote Request"
4. Wait 1-2 seconds
5. See success message with **📥 Download PDF** button
6. Click to download your professional PDF!

---

## 📁 Where Are the PDFs?

All generated quotes are saved in:
```
/Users/deedavis/NEXUS BACKEND/GENERATED_QUOTES/
```

Each quote creates:
- `.pdf` - The actual PDF file
- `.html` - HTML version
- `_config.json` - Configuration data

---

## 🎯 Real Example - SAFE FORMAT

🚨 **CRITICAL: NEVER reveal client name, agency, or government RFQ numbers to suppliers!**

**Safe example for ANY industrial supplies bid:**

```
RFQ_NUMBER: DDI-2026-001
TITLE: Industrial Supplies Quote Request
ISSUE_DATE: January 27, 2026
DUE_DATE: February 3, 2026
DUE_TIME: 2:00 PM EST
CONTRACT_PERIOD: 12 months

COLOR_SCHEME: 1

INTRODUCTION:
DEE DAVIS INC is seeking competitive quotes for a Michigan municipal client requiring industrial supplies for facility operations.

SCOPE:
Vendor will provide industrial supplies as specified below for a 12-month contract period with delivery to Metro Detroit area.

KEY_REQUIREMENTS:
- Competitive pricing required
- Standard delivery terms
- Net 30 payment terms preferred
- Confirm availability and lead times

ITEMS:
1 | Industrial Wipers - Heavy Duty | 1000ct per case, oil-absorbent | 100 | case
2 | Safety Glasses - Clear | ANSI Z87.1 certified, anti-fog | 500 | each
3 | Nitrile Gloves - Large | Powder-free, 100/box | 200 | box
4 | First Aid Kits | 25-person capacity, OSHA compliant | 20 | kit
```

**✅ SAFE - Generic DDI number, no client name, generic location!**

**❌ NEVER USE:**
- Client-specific RFQ numbers (DDI-2026-CPS, DDI-2026-CANTON)
- Government RFQ numbers (RFQ 7000205103)
- Agency names (CPS Energy, Canton Township)
- Specific addresses
- Exact government deadlines (use date 3-5 days earlier!)

**Click Generate → Download PDF → Send to suppliers!**

---

## 💡 Pro Tips

### **Keep Backend Running**
The backend API needs to stay running. I've already started it for you!

To check if it's running:
```bash
curl http://localhost:5001/api/quote/generate-from-paste
```

If you need to restart it:
```bash
cd "/Users/deedavis/NEXUS BACKEND"
./START_QUOTE_API.sh
```

### **Email the PDF**
Once downloaded:
1. Open your email client
2. Attach the PDF
3. Send to suppliers!

No need to reveal the end buyer - the template already says "Michigan municipal client" or similar generic terms.

### **Track in Airtable** (Coming Soon)
Future enhancement will auto-log:
- Who you sent it to
- When you sent it
- Follow-up reminders
- Quote responses

---

## 🔄 Switching Between Modes

**Local (Real PDFs):**
- Run `npm start` in nexus-frontend folder
- Open http://localhost:3000
- Backend must be running on port 5001
- Downloads work!

**Netlify (Mock Mode):**
- Open https://nexus-command.netlify.app
- No backend needed
- Shows mock success message
- Good for UI testing only

---

## ✅ You're Ready!

The system is **LIVE and WORKING** on your computer right now!

Try generating a quote for one of your current bids and download the PDF! 🎉

---

**Questions?**
- PDFs not downloading? Check backend is running (port 5001)
- Want different formatting? We can customize the template
- Need to add your logo? We can add that too!
