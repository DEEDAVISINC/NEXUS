# 📄 Professional Document Generators for DEE DAVIS INC

**Create beautiful, professional documents in minutes!**

---

## 🎯 What This Does

This system gives you two powerful interactive tools to create professional business documents:

### 1. **Capability Statement Generator**
Creates polished capability statements for government bids and RFQs.

**Perfect for:**
- Responding to government RFPs
- Introducing your company to procurement officers
- Submitting to buyer portals
- Building relationships with agencies

### 2. **RFQ Generator**
Creates professional Request for Quote documents to send to your suppliers.

**Perfect for:**
- Getting quotes from vendors
- Standardizing your purchasing process
- Looking professional to suppliers
- Managing multiple quote requests

---

## ✨ Features

**Both generators create:**
- 🎨 **Beautiful HTML** - Professional design with your branding
- 📱 **Responsive Design** - Looks great on any device
- 📄 **Print-Ready PDF** - High-quality PDF for submission
- 💾 **Editable Config** - Save and reuse your templates
- 🎨 **Multiple Color Schemes** - Choose what fits your industry
- 🚀 **Fast & Easy** - Just answer questions, no coding needed

---

## 🚀 Quick Start

### Option 1: Interactive Mode (Easiest!)

**Create a Capability Statement:**
```bash
cd "/Users/deedavis/NEXUS BACKEND"
python3 create_capability_statement_interactive.py
```

**Create an RFQ:**
```bash
cd "/Users/deedavis/NEXUS BACKEND"
python3 create_rfq_interactive.py
```

Just answer the questions and paste your content!

### Option 2: Use Existing Config

If you've already created a config file:

```bash
# For capability statement
python3 generate_html_with_highlights.py your_config.json
python3 generate_enhanced_pdf.py your_config.json

# For RFQ
python3 generate_rfq_html.py your_config.json
python3 generate_rfq_pdf.py your_config.json
```

---

## 📁 Files Included

### Interactive Creators:
- `create_capability_statement_interactive.py` - Walk-through for capability statements
- `create_rfq_interactive.py` - Walk-through for RFQs

### HTML Generators:
- `generate_html_with_highlights.py` - Creates capability statement HTML
- `generate_rfq_html.py` - Creates RFQ HTML

### PDF Generators:
- `generate_enhanced_pdf.py` - Creates capability statement PDF
- `generate_rfq_pdf.py` - Creates RFQ PDF

### Documentation:
- `INTERACTIVE_GENERATORS_QUICK_START.md` - Detailed guide with examples
- `DOCUMENT_GENERATORS_README.md` - This file

---

## 🎨 Color Schemes Available

### Capability Statements:
1. **Professional Navy & Gold** - General business
2. **Healthcare Blue & Teal** - Medical/healthcare bids
3. **Construction Brown & Orange** - Construction/facilities
4. **Technology Purple & Violet** - IT/tech services
5. **Corporate Blue & Sky** - Financial/professional services
6. **Environmental Green** - Environmental/sustainability

### RFQs:
1. **Industrial Navy & Gold** - Industrial supplies
2. **Transportation Brown & Orange** - Logistics/transportation
3. **Technology Purple & Violet** - Tech equipment
4. **Healthcare Blue & Teal** - Medical supplies
5. **Construction Dark Brown** - Building materials

---

## 📝 What You'll Need

### For Capability Statement:
- Client/agency name
- RFQ number
- Company overview text
- Core competencies list
- What makes you different
- Optional: NAICS codes, partners, certifications

### For RFQ:
- RFQ number and title
- Introduction text
- Scope of work description
- List of items/services needed
- Quantities and specifications

---

## 💡 Pro Tips

### Make It Faster:

1. **Prepare your text beforehand**
   - Write your overview in a doc first
   - Copy/paste when prompted

2. **Save your configs**
   - Reuse them for similar projects
   - Just change client name and RFQ number

3. **Use templates**
   - Create a "template_config.json" for each type of bid
   - Copy and customize quickly

### Make It Better:

1. **Choose colors that match the industry**
   - Healthcare bids → Healthcare Blue & Teal
   - Construction bids → Construction Brown & Orange

2. **Tailor your content**
   - Mention the specific client/project
   - Highlight relevant experience
   - Show you did your homework

3. **Add highlights to capability statements**
   - NAICS codes show you're serious
   - Past performance builds trust
   - Certifications prove credibility

---

## 🔧 Requirements

### Python:
- Python 3.7 or higher (already installed on Mac)

### Optional (for better PDFs):
```bash
# Install wkhtmltopdf for high-quality PDFs
brew install wkhtmltopdf

# OR install reportlab for basic PDFs
pip3 install reportlab
```

**Note:** The system works without these - HTML files always generate!

---

## 📖 Full Documentation

See `INTERACTIVE_GENERATORS_QUICK_START.md` for:
- Step-by-step examples
- Screenshots of the process
- Troubleshooting guide
- Advanced workflows
- Tips and tricks

---

## 🎯 Real-World Workflow

**Monday morning - Got 3 new bids to respond to:**

```bash
# 1. Create capability statements for each
python3 create_capability_statement_interactive.py
# Answer questions for Client A (2 minutes)

python3 create_capability_statement_interactive.py
# Answer questions for Client B (2 minutes)

python3 create_capability_statement_interactive.py
# Answer questions for Client C (2 minutes)

# Done! You have 3 professional capability statements in 6 minutes
```

**Need quotes from suppliers:**

```bash
# Create RFQ for plumbing supplies
python3 create_rfq_interactive.py
# Add items, specifications (3 minutes)

# Send PDF to 5 suppliers
# Professional, organized, trackable!
```

---

## ✅ Success Checklist

After running the generator, you should have:

**Capability Statement:**
- [ ] `cap_stmt_[client]_config.json` - Your saved configuration
- [ ] `cap_stmt_[client].html` - Beautiful HTML version
- [ ] `cap_stmt_[client]_enhanced.pdf` - Print-ready PDF
- [ ] All files match your client and look professional

**RFQ:**
- [ ] `rfq_[number]_config.json` - Your saved configuration
- [ ] `rfq_[number].html` - Beautiful HTML version
- [ ] `rfq_[number].pdf` - Print-ready PDF
- [ ] All items and specs are correct

---

## 🆘 Need Help?

### Common Issues:

**"Command not found"**
```bash
# Make sure you're in the right directory
cd "/Users/deedavis/NEXUS BACKEND"
ls create_*.py  # Should show the scripts
```

**"Permission denied"**
```bash
# Make scripts executable
chmod +x create_*.py generate_*.py
```

**"PDF not generating"**
```bash
# Install wkhtmltopdf or reportlab
brew install wkhtmltopdf
# OR
pip3 install reportlab
```

**"Don't like the colors"**
- Just run the script again and choose different colors
- Or edit the config JSON and regenerate

---

## 🚀 Next Steps

1. **Try it now!**
   ```bash
   python3 create_capability_statement_interactive.py
   ```

2. **Read the full guide**
   - Open `INTERACTIVE_GENERATORS_QUICK_START.md`
   - See examples and workflows

3. **Create templates**
   - Make one for each type of bid you do
   - Save time on future bids

4. **Integrate with your workflow**
   - Use for every bid response
   - Build your library of configs
   - Track what works best

---

## 💼 Business Impact

**Before:**
- ⏱️ 2-3 hours to create capability statement in Word
- 📝 Inconsistent formatting
- 😰 Stressful last-minute changes
- 📁 Hard to track versions

**After:**
- ⚡ 2-3 minutes to create professional docs
- 🎨 Consistent, beautiful formatting every time
- 😊 Easy updates and changes
- 💾 All configs saved and reusable

**Time saved per bid:** ~2 hours
**Professional appearance:** ⬆️⬆️⬆️
**Stress level:** ⬇️⬇️⬇️

---

**Built for DEE DAVIS INC - Michigan EDWOSB**

*Making business documentation fast, easy, and professional!* 🎉
