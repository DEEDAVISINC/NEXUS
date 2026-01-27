# 🎯 DOCUMENT GENERATORS - QUICK REFERENCE CARD

**Keep this handy for fast lookups!**

---

## 🚀 Quick Commands

### Beginner: Interactive (Guides You)
```bash
python3 create_capability_statement_interactive.py
python3 create_rfq_interactive.py
```

### Fast: Paste Template
```bash
python3 create_from_paste.py capability my_data.txt
python3 create_from_paste.py rfq rfq_data.txt
```

### Bulk: CSV Import
```bash
python3 import_from_csv.py items.csv
```

### Expert: Template Method
```bash
python3 create_template.py capability  # or rfq
cp template_*.json my_doc.json
nano my_doc.json
python3 generate_html_with_highlights.py my_doc.json
python3 generate_enhanced_pdf.py my_doc.json
```

---

## 📋 Paste Template Quick Copy

### Capability Statement
```
CLIENT_NAME: Client Name Here
RFQ_NUMBER: RFQ-123456
DATE: January 2026
COLOR_SCHEME: 1

OVERVIEW:
Your company overview here...

HIGHLIGHTS:
NAICS: 423850 - Industrial Supplies
Partners: Partner1 | Partner2
```

### RFQ
```
RFQ_NUMBER: RFQ-2026-001
TITLE: Your Title
ISSUE_DATE: January 26, 2026
DUE_DATE: February 15, 2026
DUE_TIME: 3:00 PM EST
CONTRACT_PERIOD: 12 months
COLOR_SCHEME: 1

INTRODUCTION:
Your intro...

SCOPE:
Your scope...

KEY_REQUIREMENTS:
- Requirement 1
- Requirement 2

ITEMS:
1 | Description | Specs | Qty | Unit
```

---

## 🎨 Color Schemes

### Capability Statement
1. Navy/Gold - Professional
2. Blue/Teal - Healthcare
3. Brown/Orange - Construction
4. Purple/Violet - Technology
5. Corporate Blue - Financial
6. Green - Environmental

### RFQ
1. Navy/Gold - Industrial
2. Brown/Orange - Transportation
3. Purple/Violet - Technology
4. Blue/Teal - Healthcare
5. Dark Brown - Construction

---

## ⚡ Speed Chart

| Method | Time | Best For |
|--------|------|----------|
| Interactive | 3-5 min | First time |
| Paste | 1-2 min | Quick docs |
| CSV | 30 sec | Many items |
| Template | 30 sec | Power users |

---

## 📁 File Naming

**Capability Statement:**
- Config: `cap_stmt_[client]_config.json`
- HTML: `cap_stmt_[client].html`
- PDF: `cap_stmt_[client]_enhanced.pdf`

**RFQ:**
- Config: `rfq_[number]_config.json`
- HTML: `rfq_[number].html`
- PDF: `rfq_[number].pdf`

---

## 🔧 Manual Generation

```bash
# Generate HTML
python3 generate_html_with_highlights.py config.json
python3 generate_rfq_html.py config.json

# Generate PDF
python3 generate_enhanced_pdf.py config.json
python3 generate_rfq_pdf.py config.json
```

---

## 💡 Pro Tips

**Fastest workflow:**
1. Create template once
2. Copy for each bid
3. Edit 2-3 fields only
4. Generate in 30 seconds!

**Save successful bids:**
```bash
mkdir successful_bids
cp winning_config.json successful_bids/
```

**Batch generation:**
```bash
for file in *.json; do
    python3 generate_html_with_highlights.py $file
done
```

---

## 🆘 Troubleshooting

**Script won't run:**
```bash
chmod +x *.py
```

**PDF issues:**
```bash
brew install wkhtmltopdf
# OR
pip3 install reportlab
```

**Want to start over:**
- Just run the script again
- Or delete and recreate files

---

## 📞 Quick Help

**Full guides:**
- `DOCUMENT_GENERATORS_README.md`
- `INTERACTIVE_GENERATORS_QUICK_START.md`
- `COMPLETE_TOOLKIT_SUMMARY.md`

**Where am I:**
```bash
cd "/Users/deedavis/NEXUS BACKEND"
```

---

**Print this card and keep it at your desk!** 📄
