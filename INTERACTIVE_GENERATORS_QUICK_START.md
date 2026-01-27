# ⚡ INTERACTIVE GENERATORS - QUICK START

## 🎯 The Easiest Way to Create Documents!

No more editing JSON files - just answer questions and paste your info!

---

## 🚀 Two Interactive Scripts

### 1. Capability Statement Creator
**Creates:** Professional capability statements for clients
**Use when:** Bidding on contracts, responding to RFQs

### 2. RFQ Creator  
**Creates:** Professional RFQs for your vendors
**Use when:** Buying supplies, contracting services

---

## 📋 How It Works

### Step 1: Run the Script
```bash
# For Capability Statement
python3 create_capability_statement_interactive.py

# For RFQ
python3 create_rfq_interactive.py
```

### Step 2: Answer Questions
The script will ask you simple questions like:
- Client name?
- RFQ number?
- What colors do you want?
- Paste your overview text
- Add highlights/items

### Step 3: Get Your Files!
Automatically generates:
- ✅ HTML file (for web/email)
- ✅ PDF file (for submission)
- ✅ Config file (to edit later)

**That's it!** No JSON editing, no command line complexity.

---

## 📄 Example: Create Capability Statement

```bash
$ python3 create_capability_statement_interactive.py

============================================================
CAPABILITY STATEMENT CREATOR
============================================================
Let's create your capability statement!
Just answer the questions below.
============================================================

--- COMPANY INFORMATION (press Enter to use defaults) ---
Company name [DEE DAVIS INC]: ← Press Enter
CAGE Code [8UMX3]: ← Press Enter
UEI [HJB4KNYJVGZ1]: ← Press Enter
DUNS [002636755]: ← Press Enter
Tax ID [84-4114181]: ← Press Enter

--- RFQ/CLIENT INFORMATION ---
Client name: VA Medical Center
RFQ number: 789456
Date [January 2026]: ← Press Enter

============================================================
CHOOSE COLOR SCHEME
============================================================
1. Professional Navy & Gold
2. Healthcare Blue & Teal ← Choose this!
3. Construction Brown & Orange
4. Technology Purple & Violet
5. Corporate Blue & Sky
6. Environmental Green

Enter number (1-6) [1]: 2

--- COMPANY OVERVIEW ---
Paste or type your company overview:
(Press Enter twice when done)
DEE DAVIS INC specializes in healthcare logistics...
← Press Enter twice

--- ADD HIGHLIGHTS ---
Add NAICS code? (y/n) [y]: y
  NAICS code: 621999 - Medical Supplies
Add key partners? (y/n) [y]: y
  Partners: Cardinal Health | McKesson
...

============================================================
✓ Configuration saved: cap_stmt_va_medical_center_config.json
============================================================

🎨 Generating HTML and PDF...

============================================================
✅ SUCCESS! Your capability statement is ready!
============================================================

📄 Your files:
   • cap_stmt_va_medical_center.html
   • cap_stmt_va_medical_center_enhanced.pdf
   • cap_stmt_va_medical_center_config.json

🎯 Next steps:
   1. Open cap_stmt_va_medical_center.html in browser
   2. Submit cap_stmt_va_medical_center_enhanced.pdf to client
============================================================
```

---

## 📝 Example: Create RFQ

```bash
$ python3 create_rfq_interactive.py

============================================================
RFQ CREATOR
============================================================
Let's create your Request for Quote!
============================================================

--- RFQ DETAILS ---
RFQ Number: RFQ-2026-SUPPLIES-001
RFQ Title: Office Supplies - Annual Contract
Issue Date [January 26, 2026]: ← Press Enter
Due Date [February 15, 2026]: ← Press Enter
Due Time [3:00 PM EST]: ← Press Enter
Contract Period [12 months]: ← Press Enter

============================================================
CHOOSE COLOR SCHEME
============================================================
1. Industrial Navy & Gold ← Choose this
2. Transportation Brown & Orange
3. Technology Purple & Violet
4. Healthcare Blue & Teal
5. Construction Dark Brown

Enter number (1-5) [1]: ← Press Enter

--- INTRODUCTION ---
Paste or type your RFQ introduction:
(Press Enter twice when done)
DEE DAVIS INC is seeking qualified suppliers...
← Press Enter twice

--- ADD ITEMS/SERVICES ---

--- Item #1 ---
Description: Copy Paper
Specifications: 8.5" x 11", 20lb, white, 10 reams per case
Estimated Quantity: 100 cases
Unit: case

Add another item? (y/n) [n]: y

--- Item #2 ---
Description: Ballpoint Pens
Specifications: Medium point, blue ink, box of 12
Estimated Quantity: 50 boxes
Unit: box

Add another item? (y/n) [n]: ← Press Enter (done)

============================================================
✓ Configuration saved: rfq_rfq_2026_supplies_001_config.json
============================================================

🎨 Generating HTML and PDF...

============================================================
✅ SUCCESS! Your RFQ is ready!
============================================================

📄 Your files:
   • rfq_rfq_2026_supplies_001.html
   • rfq_rfq_2026_supplies_001.pdf
   • rfq_rfq_2026_supplies_001_config.json

🎯 Next steps:
   1. Open rfq_rfq_2026_supplies_001.html in browser
   2. Send rfq_rfq_2026_supplies_001.pdf to vendors
============================================================
```

---

## 💡 Tips for Using Interactive Scripts

### For Faster Input

1. **Use defaults when possible**
   - Press Enter to accept default values
   - Company info rarely changes

2. **Prepare text in advance**
   - Copy your overview/introduction beforehand
   - Paste when prompted

3. **Have your list ready**
   - Items for RFQ
   - Highlights for capability statement

### Multi-line Input

When you see:
```
Paste or type your overview:
(Press Enter twice when done)
```

You can:
- Type multiple lines
- Paste multiple paragraphs
- Press Enter twice to finish

### Saving for Later

The script creates a `.json` config file. You can:
- Edit it manually later
- Use it as a template
- Generate new files from it anytime

```bash
# Regenerate from saved config
python3 generate_html_with_highlights.py saved_config.json
python3 generate_enhanced_pdf.py saved_config.json
```

---

## 🎯 Common Workflows

### Workflow 1: New Client Each Time
```bash
# Run interactive script for each new client
python3 create_capability_statement_interactive.py
# Answer questions (2-3 minutes)
# Get your files!
```

### Workflow 2: Save Templates
```bash
# First time: Create with interactive script
python3 create_capability_statement_interactive.py
# Saves: client_config.json

# Future times: Copy and edit
cp client_config.json new_client_config.json
nano new_client_config.json  # Change just client/RFQ info
python3 generate_html_with_highlights.py new_client_config.json
# Done in 30 seconds!
```

### Workflow 3: Bulk Generation
```bash
# Create 5 capability statements on Monday
for i in {1..5}; do
    python3 create_capability_statement_interactive.py
done

# Or create 3 RFQs for different projects
for i in {1..3}; do
    python3 create_rfq_interactive.py
done
```

---

## 📊 Comparison: Interactive vs Manual

| Feature | Interactive Script | Manual JSON Edit |
|---------|-------------------|------------------|
| **Ease of use** | ⭐⭐⭐⭐⭐ Very easy | ⭐⭐⭐ Medium |
| **Speed (first time)** | ⭐⭐⭐⭐ Fast | ⭐⭐ Slow |
| **Speed (repeat)** | ⭐⭐⭐ Medium | ⭐⭐⭐⭐⭐ Very fast |
| **Learning curve** | ⭐⭐⭐⭐⭐ None | ⭐⭐⭐ Some |
| **Error prevention** | ⭐⭐⭐⭐⭐ Guided | ⭐⭐ Manual |
| **Flexibility** | ⭐⭐⭐⭐ High | ⭐⭐⭐⭐⭐ Complete |

**Recommendation:** 
- Use **Interactive** for your first few documents
- Switch to **Manual JSON** once you're comfortable
- Or just keep using Interactive - it's always easy! 😊

---

## 🆘 Troubleshooting

**Q: Script won't run?**
```bash
# Make sure you're in the right folder
cd "/Users/deedavis/NEXUS BACKEND"

# Make sure script is executable
chmod +x create_capability_statement_interactive.py
chmod +x create_rfq_interactive.py

# Run with python3
python3 create_capability_statement_interactive.py
```

**Q: Want to cancel?**
- Press `Ctrl+C` to exit anytime
- No files created until script finishes

**Q: Made a mistake?**
- Just run the script again
- Or edit the saved config file manually

**Q: Where are my files?**
- All in `/Users/deedavis/NEXUS BACKEND/`
- Look for files matching your RFQ/client name

---

## ✅ Ready to Try?

```bash
# Go to the right folder
cd "/Users/deedavis/NEXUS BACKEND"

# Start creating!
python3 create_capability_statement_interactive.py
```

**Answer the questions, paste your info, and get professional documents in minutes!** 🚀

No JSON required! 🎉
