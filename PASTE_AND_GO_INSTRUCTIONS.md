# 🚀 PASTE AND GO - QUOTE REQUEST GENERATOR

**The easiest way to create quote requests!**

---

## ✅ 3 Simple Steps

### Step 1: Edit the Template File
Open `example_quote_request_template.txt` and replace the sample text with your info:

```bash
nano example_quote_request_template.txt
```

**What to edit:**
- RFQ_NUMBER: Your tracking number
- TITLE: What you're buying
- Dates: When quotes are due
- ITEMS section: Your actual items (one per line)

### Step 2: Run the Generator
```bash
python3 create_from_paste.py rfq example_quote_request_template.txt
```

### Step 3: Get Your Files!
You'll instantly get:
- ✅ Professional HTML file
- ✅ Print-ready PDF
- ✅ Saved config for future use

**That's it!** 🎉

---

## 📝 Real Example

### What You Paste:
```
RFQ_NUMBER: RFQ-2026-CLEANING-001
TITLE: Cleaning Supplies - Monthly Contract
ISSUE_DATE: January 26, 2026
DUE_DATE: February 5, 2026
DUE_TIME: 3:00 PM EST
CONTRACT_PERIOD: 6 months

COLOR_SCHEME: 1

INTRODUCTION:
DEE DAVIS INC is seeking quotes for cleaning supplies for a Michigan municipal client. We need reliable suppliers with competitive pricing.

SCOPE:
Vendor will provide cleaning supplies on a monthly basis. Delivery to Metro Detroit area. All products must be commercial grade.

KEY_REQUIREMENTS:
- Commercial grade products
- Monthly delivery capability
- Competitive pricing
- References required

ITEMS:
1 | Industrial Paper Towels | Roll size 11" x 9", case of 30 rolls | 500 cases | case
2 | All-Purpose Cleaner | Concentrated, 1-gallon containers | 200 gallons | gallon
3 | Microfiber Cleaning Cloths | 16" x 16", color-coded, pkg of 12 | 1000 pieces | piece
4 | Trash Can Liners | 55-gallon, heavy duty, black | 5000 bags | bag
```

### What You Get:
- `rfq_rfq_2026_cleaning_001.html` - Beautiful web version
- `rfq_rfq_2026_cleaning_001.pdf` - Ready to send
- `rfq_rfq_2026_cleaning_001_config.json` - Saved for editing

**Time: 1 minute!** ⚡

---

## 💡 Pro Tips

### Tip 1: Keep Your Template
Save successful quote requests as templates:
```bash
cp good_template.txt plumbing_template.txt
cp good_template.txt electrical_template.txt
```

### Tip 2: Multiple Items?
Just add more lines to the ITEMS section:
```
ITEMS:
1 | First item | Specs | Qty | unit
2 | Second item | Specs | Qty | unit
3 | Third item | Specs | Qty | unit
... add as many as you need!
```

### Tip 3: Change Colors
Pick the color scheme that fits your industry:
- 1 = Industrial/Manufacturing (Navy/Gold)
- 2 = Transportation/Logistics (Brown/Orange)
- 3 = Technology/IT (Purple/Violet)
- 4 = Healthcare/Medical (Blue/Teal)
- 5 = Construction (Dark Brown/Orange)

---

## 🎯 Quick Command

**From anywhere in your terminal:**
```bash
cd "/Users/deedavis/NEXUS BACKEND"
nano example_quote_request_template.txt
# Edit your info, save (Ctrl+O, Enter, Ctrl+X)
python3 create_from_paste.py rfq example_quote_request_template.txt
# Done! Check your files!
```

---

## ✅ What Gets Sent to Suppliers

Your generated PDF includes:
- ✅ Professional header with your company info
- ✅ Clear RFQ details (number, dates, deadlines)
- ✅ Introduction explaining what you need
- ✅ Detailed item specifications in a table
- ✅ Submission requirements
- ✅ Terms & conditions
- ✅ Evaluation criteria
- ✅ Contact information

**Suppliers will be impressed!** 🌟

---

## 🆘 Need Help?

**Template file location:**
```bash
/Users/deedavis/NEXUS BACKEND/example_quote_request_template.txt
```

**Can't find it?**
```bash
cd "/Users/deedavis/NEXUS BACKEND"
ls example_quote_request_template.txt
```

**Want to start fresh?**
Just edit the example file again or create a new one!

---

**Now go create your first quote request in 1 minute!** 🚀
