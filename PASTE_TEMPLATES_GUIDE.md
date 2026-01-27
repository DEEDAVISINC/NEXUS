# 📋 PASTE TEMPLATES - EASIEST WAY!

## 🎯 Two Ways to Create Documents

### Method 1: Interactive Script (Guided Questions)
**Best for:** First time, complex documents
```bash
# For Capability Statements
python3 create_capability_statement_interactive.py

# For RFQs
python3 create_rfq_interactive.py
```

### Method 2: Paste Template (Copy & Fill)
**Best for:** Quick generation, bulk creation
See templates below!

---

## 📄 Capability Statement - Paste Template

**How to use:**
1. Copy the template below
2. Replace ALL_CAPS text with your info
3. Save as `my_data.txt`
4. Run generator (coming next!)

```
CLIENT_NAME: CPS Energy
RFQ_NUMBER: 7000205103
DATE: January 2026

COLOR_SCHEME: 1
(1=Navy/Gold, 2=Blue/Teal, 3=Brown/Orange, 4=Purple/Violet, 5=Corporate Blue, 6=Green)

OVERVIEW:
Paste your company overview here. This can be multiple sentences describing what you do and who you serve.

HIGHLIGHTS:
NAICS: 423850 - Industrial Supplies
Partners: Grainger | Fastenal | Landstar
Contract Range: $50K - $500K Successfully Delivered
Performance: 98%+ On-Time | 100% Compliance
Coverage: Nationwide Coverage
```

---

## 📝 RFQ - Paste Template

**How to use:**
1. Copy the template below
2. Replace ALL_CAPS text with your info
3. Save as `rfq_data.txt`
4. Run generator

```
RFQ_NUMBER: RFQ-2026-001
TITLE: Industrial Cleaning Supplies - Annual Contract
ISSUE_DATE: January 26, 2026
DUE_DATE: February 15, 2026
DUE_TIME: 3:00 PM EST
CONTRACT_PERIOD: 12 months

COLOR_SCHEME: 1
(1=Navy/Gold, 2=Brown/Orange, 3=Purple/Violet, 4=Blue/Teal, 5=Dark Brown/Orange)

INTRODUCTION:
Paste your introduction here. Explain what you're looking for and the purpose of this RFQ.

SCOPE:
Describe the scope of work. What will the selected vendor need to provide?

KEY_REQUIREMENTS:
- Requirement 1
- Requirement 2
- Requirement 3

ITEMS:
1 | Industrial Paper Towels | Roll size 11" x 9", case of 30 | 500 cases | case
2 | Cleaning Solution | Concentrated, 1-gallon containers | 200 gallons | gallon
3 | Microfiber Cloths | 16" x 16", color-coded | 1000 pieces | piece
(Format: Number | Description | Specifications | Quantity | Unit)
```

---

## ⚡ Even Easier: Excel/CSV Template

Create a spreadsheet with these columns:

### For Capability Statement Highlights:
| Icon | Label | Value |
|------|-------|-------|
| 🎯 | Primary NAICS | 423850 - Industrial Supplies |
| 🤝 | Key Partners | Grainger \| Fastenal |
| 📊 | Contract Range | $50K - $500K |

Save as CSV, import with script!

### For RFQ Items:
| Item # | Description | Specifications | Est. Quantity | Unit |
|--------|-------------|----------------|---------------|------|
| 1 | Paper Towels | 11" x 9" roll | 500 cases | case |
| 2 | Cleaner | 1 gallon | 200 gallons | gallon |

---

## 🚀 Quick Commands

### Interactive (Asks Questions)
```bash
# Capability Statement
python3 create_capability_statement_interactive.py

# RFQ
python3 create_rfq_interactive.py
```

### From Paste Template (Coming Soon!)
```bash
# Capability Statement
python3 create_from_paste.py capability my_data.txt

# RFQ
python3 create_from_paste.py rfq rfq_data.txt
```

### From CSV/Excel (Coming Soon!)
```bash
# Import items from CSV
python3 import_from_csv.py items.csv
```

---

## 💡 Which Method Should I Use?

| Method | Best For | Speed |
|--------|----------|-------|
| **Interactive Script** | First time, learning | Slow (guided) |
| **Paste Template** | Quick updates, bulk | Fast |
| **CSV Import** | Many items, spreadsheets | Fastest |
| **JSON Direct** | Full control, automation | Expert |

---

## 🎯 Pro Workflow

**Step 1:** Use interactive script ONCE to learn
```bash
python3 create_capability_statement_interactive.py
```

**Step 2:** Save the generated config as your template

**Step 3:** For future docs, just copy & edit the config:
```bash
cp my_template_config.json new_client_config.json
nano new_client_config.json  # Edit just what changed
python3 generate_html_with_highlights.py new_client_config.json
python3 generate_enhanced_pdf.py new_client_config.json
```

**Even faster:**
- Keep a folder of client-specific configs
- Copy, edit 2-3 fields, generate
- Done in 30 seconds! ⚡

---

## 📝 Real Example Workflow

### Monday: Need capability statement for VA Medical

**Option A - Interactive:**
```bash
python3 create_capability_statement_interactive.py
# Answer questions
# Done in 3 minutes
```

**Option B - Copy existing:**
```bash
cp default_config.json va_medical_config.json
nano va_medical_config.json
# Change: client_name, rfq_number, colors
# Save and exit
python3 generate_html_with_highlights.py va_medical_config.json
python3 generate_enhanced_pdf.py va_medical_config.json
# Done in 1 minute
```

### Tuesday: Need RFQ for cleaning supplies

**Option A - Interactive:**
```bash
python3 create_rfq_interactive.py
# Answer questions, paste items
# Done in 5 minutes
```

**Option B - Paste template:**
```
1. Copy paste template to text file
2. Fill in your info
3. Run generator (once we build it!)
4. Done in 2 minutes
```

---

## ✅ What's Available Now

- ✅ Interactive capability statement creator
- ✅ Interactive RFQ creator
- ✅ Manual JSON editing
- ⏳ Paste template parser (next!)
- ⏳ CSV import (next!)

**You can start using the interactive scripts right now!**

---

## 🎉 Try It Now!

```bash
# Go to your workspace
cd "/Users/deedavis/NEXUS BACKEND"

# Create capability statement
python3 create_capability_statement_interactive.py

# OR create RFQ
python3 create_rfq_interactive.py
```

**Just answer the questions and paste your info - we handle the rest!** 🚀
