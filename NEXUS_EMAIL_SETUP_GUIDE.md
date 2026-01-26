# NEXUS EMAIL AUTOMATION - QUICK SETUP GUIDE
**Get Your Email Bot Running in 30 Minutes**

---

## ✅ WHAT THIS DOES

**NEXUS will automatically:**
1. ✅ Check `bids@deedavisinc.com` every 30 minutes
2. ✅ Detect new solicitation emails (RFPs, RFQs, RFBs)
3. ✅ Extract key info using AI (deadline, buyer, value, etc.)
4. ✅ Create Airtable records automatically
5. ✅ Send diversity inquiry emails to buyers
6. ✅ Track responses and update records

**Result:** Wake up to pre-qualified opportunities with diversity intel!

---

## 🚀 SETUP (30 Minutes)

### **STEP 1: Create Dedicated Email (5 min)**

**Option A: Gmail (Easiest)**
1. Go to gmail.com
2. Create new account: `bids@deedavisinc.com`
3. Enable "2-Step Verification"
4. Generate "App Password":
   - Go to: https://myaccount.google.com/apppasswords
   - Select "Mail" and "Other (Custom name)"
   - Name it: "NEXUS Automation"
   - Copy the 16-character password
   - Save it securely!

**Option B: Custom Domain** (More Professional)
- Use your domain: bids@deedavisinc.com
- Set up email forwarding or mailbox
- Get IMAP/SMTP credentials from host

---

### **STEP 2: Update Airtable Schema (10 min)**

Add these fields to your "BID OPPORTUNITIES" table:

```
BASIC FIELDS:
- Solicitation Number (Text)
- Title (Long Text)
- Organization (Text)
- Buyer Name (Text)
- Buyer Email (Email)
- Buyer Phone (Phone)
- Deadline (Date/Time)
- Estimated Value (Currency)
- Contract Duration (Text)
- Location (Text)
- Description (Long Text)
- Product/Service Category (Single Select)

AI FIELDS:
- AI Fit Score (Number, 0-100)
- Fit Analysis (Long Text)
- Priority Level (Single Select: High/Medium/Low)

DIVERSITY FIELDS:
- Diversity Inquiry Status (Single Select)
  Options: "Not Sent", "Sent - Awaiting Response", 
           "YES - Diversity Valued", "NO - Price Only",
           "MAYBE - Other Factors"
- Diversity Inquiry Sent Date (Date)
- Diversity Response (Long Text)

TRACKING FIELDS:
- Bid Status (Single Select)
- Source (Single Select: Email/SAM.gov/BidNet/Other)
- Source Email From (Text)
- Source Email Subject (Text)
```

---

### **STEP 3: Set Environment Variables (5 min)**

**On Mac/Linux (add to `~/.bash_profile` or `~/.zshrc`):**

```bash
# NEXUS Email Automation
export NEXUS_EMAIL="bids@deedavisinc.com"
export NEXUS_EMAIL_PASSWORD="your_app_password_here"
export IMAP_SERVER="imap.gmail.com"
export SMTP_SERVER="smtp.gmail.com"

# Your existing variables
export AIRTABLE_API_KEY="your_airtable_key"
export AIRTABLE_BASE_ID="your_base_id"
export ANTHROPIC_API_KEY="your_anthropic_key"
export CAGE_CODE="your_cage_code"
```

**Then reload:**
```bash
source ~/.bash_profile  # or source ~/.zshrc
```

**On PythonAnywhere (when deploying):**
- Go to "Files" → "Bash console"
- Edit `.bashrc` file
- Add export statements above
- Run: `source ~/.bashrc`

---

### **STEP 4: Install Dependencies (2 min)**

```bash
cd "/Users/deedavis/NEXUS BACKEND"
pip install anthropic pyairtable
```

---

### **STEP 5: Test Manual Run (5 min)**

```bash
python nexus_email_automation.py
```

**Expected output:**
```
======================================================================
NEXUS EMAIL AUTOMATION SYSTEM
Started: 2026-01-25 18:30:00
======================================================================

Initializing components...
✓ Connected to bids@deedavisinc.com

Checking inbox for new solicitations...
Found 3 unread emails
  ✓ Solicitation: New RFQ - Office Supplies
  ✓ Solicitation: Bid Opportunity - Landscaping

✓ Found 2 new solicitations to process

[1/2] Processing: New RFQ - Office Supplies
  → Title: Office Supplies
  → Organization: City of Detroit
  → Fit Score: 85/100
  → Priority: HIGH
  ✓ Created Airtable record: rec123abc
  → Sending diversity inquiry to jsmith@detroitmi.gov
  ✓ Sent diversity inquiry to jsmith@detroitmi.gov
  ✓ Updated record rec123abc - diversity inquiry sent

[2/2] Processing: Bid Opportunity - Landscaping
  → Title: Commercial Landscaping Services
  → Organization: Oakland County
  → Fit Score: 75/100
  → Priority: HIGH
  ✓ Created Airtable record: rec456def
  → Sending diversity inquiry to procurement@oakgov.com
  ✓ Sent diversity inquiry to procurement@oakgov.com
  ✓ Updated record rec456def - diversity inquiry sent

======================================================================
NEXUS Email Automation Complete!
Processed: 2 solicitations
Completed: 2026-01-25 18:30:45
======================================================================
```

---

### **STEP 6: Schedule Automation (5 min)**

**Option A: PythonAnywhere Scheduled Tasks (Recommended)**

1. Go to PythonAnywhere Dashboard
2. Click "Tasks"
3. Add new task:
   - **Command:** `python /home/yourusername/NEXUS\ BACKEND/nexus_email_automation.py`
   - **Schedule:** Hourly (or every 30 min if available)
4. Save

**Option B: Mac/Linux Cron**

```bash
# Edit crontab
crontab -e

# Add this line (runs every 30 minutes):
*/30 * * * * cd "/Users/deedavis/NEXUS BACKEND" && python nexus_email_automation.py >> nexus_email.log 2>&1
```

**Option C: GitHub Actions (Free, Cloud-Based)**

Create `.github/workflows/nexus-email.yml`:

```yaml
name: NEXUS Email Automation
on:
  schedule:
    - cron: '*/30 * * * *'  # Every 30 minutes
  workflow_dispatch:  # Manual trigger
jobs:
  run:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - run: pip install anthropic pyairtable
      - run: python nexus_email_automation.py
        env:
          NEXUS_EMAIL: ${{ secrets.NEXUS_EMAIL }}
          NEXUS_EMAIL_PASSWORD: ${{ secrets.NEXUS_EMAIL_PASSWORD }}
          AIRTABLE_API_KEY: ${{ secrets.AIRTABLE_API_KEY }}
          AIRTABLE_BASE_ID: ${{ secrets.AIRTABLE_BASE_ID }}
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          CAGE_CODE: ${{ secrets.CAGE_CODE }}
```

---

## 🎯 HOW TO USE

### **Daily Workflow:**

**Morning:**
1. Open Airtable "BID OPPORTUNITIES" view
2. Filter by "Priority Level" = "HIGH"
3. Check "Diversity Inquiry Status"
4. Focus on opportunities marked "YES - Diversity Valued"

**Actions:**
- Review AI fit analysis
- Check if deadline is manageable
- Decide: BID or SKIP
- If bidding, move to "BID IN PROGRESS"

**Throughout Week:**
- NEXUS continues monitoring email
- Auto-creates new records
- Auto-sends diversity inquiries
- You just review and decide!

---

## 📧 SUBSCRIBING TO SOLICITATION SOURCES

**To maximize opportunities, sign up for:**

### **1. SAM.gov Opportunity Notifications**
- Go to: sam.gov
- Search for your NAICS codes
- Click "Follow This Search"
- Email notifications → `bids@deedavisinc.com`

### **2. BidNet Direct**
- Go to: bidnetdirect.com
- Create account with `bids@deedavisinc.com`
- Set notification preferences
- Select Michigan + surrounding states

### **3. PlanetBids**
- Go to: planetbids.com
- Sign up with `bids@deedavisinc.com`
- Select product categories
- Enable daily digests

### **4. Local Government Portals**
- City of Detroit: detroitmi.gov/procurement
- Oakland County: oakgov.com/purchasing
- Wayne County: waynecounty.com/procurement
- Sign up for email notifications → `bids@deedavisinc.com`

### **5. State of Michigan**
- Go to: michigan.gov/sigmavss
- Create vendor account
- Email notifications → `bids@deedavisinc.com`

---

## 🎛️ CUSTOMIZATION

### **Adjust Thresholds:**

Edit `nexus_email_automation.py`:

```python
# Line 37-38
MIN_FIT_SCORE = 70  # Only send inquiry if fit >= 70
MIN_CONTRACT_VALUE = 20000  # Only if value >= $20K

# Adjust as needed:
MIN_FIT_SCORE = 80  # More selective
MIN_CONTRACT_VALUE = 50000  # Only larger contracts
```

### **Customize Company Info:**

Edit `nexus_email_automation.py`:

```python
# Lines 41-45
COMPANY_NAME = "DEE DAVIS INC"
COMPANY_LOCATION = "Troy, MI 48083"
COMPANY_PHONE = "248-376-4550"
COMPANY_EMAIL = "info@deedavis.biz"
CAGE_CODE = "YOUR_ACTUAL_CAGE_CODE"
```

---

## 🔧 TROUBLESHOOTING

### **Problem: "Failed to connect to email"**

**Solution:**
- Check NEXUS_EMAIL_PASSWORD is correct
- For Gmail: Use App Password, not regular password
- Check IMAP_SERVER is correct (imap.gmail.com for Gmail)

### **Problem: "Failed to create Airtable record"**

**Solution:**
- Check AIRTABLE_API_KEY is valid
- Check AIRTABLE_BASE_ID is correct
- Verify "BID OPPORTUNITIES" table exists
- Check field names match exactly

### **Problem: "AI extraction failed"**

**Solution:**
- Check ANTHROPIC_API_KEY is valid
- Check you have API credits
- Email body may be too short/empty

### **Problem: No solicitations detected**

**Solution:**
- Check email inbox has unread messages
- Keywords may not match - adjust `is_solicitation()` function
- Email may be HTML-only - check email format

---

## 📊 EXPECTED PERFORMANCE

### **After 30 Days:**

**Metrics:**
- Solicitations detected: 50-100
- High-priority opportunities: 20-30
- Diversity inquiries sent: 15-25
- Responses received: 10-15
- Qualified opportunities: 8-12

**Time Saved:**
- Email monitoring: 2-3 hours/week → 0 ✅
- Data entry: 1-2 hours/week → 0 ✅
- Diversity inquiries: 1 hour/week → 0 ✅
- **Total: 4-6 hours/week saved**

**Better Results:**
- More opportunities reviewed (100 vs 20 manual)
- Pre-qualified with diversity intel
- Focus only on high-probability bids
- Higher overall win rate

---

## 💰 COST

**Monthly:**
- Email: $0 (Gmail) or $6 (Google Workspace)
- Anthropic API: $5-10 (based on volume)
- **Total: $5-16/month**

**Value:**
- Time saved: 16-24 hours/month
- Better win rate: 10-15% increase
- **ROI: 10,000%+** 🚀

---

## 🎉 YOU'RE DONE!

**Now NEXUS will:**
- Monitor email 24/7
- Extract opportunities automatically
- Send smart diversity inquiries
- Track everything in Airtable
- Alert you to high-value opportunities

**You just:**
- Review opportunities in Airtable
- Decide BID or SKIP
- Focus on high-probability wins

**Welcome to automated bid intelligence!** 🤖✨

---

## 📞 NEED HELP?

**Check the log file:**
```bash
tail -f nexus_email.log
```

**Test individual components:**
```python
# Test email connection
python -c "from nexus_email_automation import EmailMonitor; m = EmailMonitor()"

# Test Airtable connection
python -c "from nexus_email_automation import AirtableManager; a = AirtableManager()"

# Test AI extraction
python -c "from nexus_email_automation import SolicitationExtractor; e = SolicitationExtractor()"
```

---

*Setup Guide Created: January 25, 2026*
*Estimated Setup Time: 30 minutes*
*Difficulty: Easy*
