# ⚡ CAPABILITY STATEMENT GENERATOR - QUICK REFERENCE

## 🎯 Generate New Capability Statement (3 Commands)

### Step 1: Edit Config
```bash
# Open and edit any config file
nano default_config.json

# Change:
# - Client name
# - RFQ number  
# - Colors
# - Highlights
```

### Step 2: Generate HTML (For NEXUS)
```bash
python3 generate_html_with_highlights.py default_config.json
# Output: default.html
```

### Step 3: Generate PDF (For Submission)
```bash
python3 generate_enhanced_pdf.py default_config.json
# Output: default_enhanced.pdf
```

---

## 📋 Use Different Templates

### CPS Energy (Industrial)
```bash
python3 generate_html_with_highlights.py default_config.json
python3 generate_enhanced_pdf.py default_config.json
```

### VA Medical (Healthcare)
```bash
python3 generate_html_with_highlights.py example_va_medical_config.json
python3 generate_enhanced_pdf.py example_va_medical_config.json
```

### Construction
```bash
python3 generate_html_with_highlights.py example_construction_config.json
python3 generate_enhanced_pdf.py example_construction_config.json
```

---

## ⚡ Generate Both at Once

```bash
# Generate HTML + PDF in one go
python3 generate_html_with_highlights.py your_config.json && \
python3 generate_enhanced_pdf.py your_config.json
```

---

## 🤖 NEXUS Integration

### API Endpoint
```http
POST http://localhost:5000/capability-statements/generate
Content-Type: application/json

{
    "opportunity_id": "recXXXXXXXXXXX",  // Optional: generate from opportunity
    "client_name": "CPS Energy",         // Required if no opportunity_id
    "rfq_number": "7000205103",          // Required if no opportunity_id
    "rfq_title": "Industrial Wipers",    // Optional
    "template": "default",               // Optional: default, va_medical, construction
    "custom_config": {...}               // Optional: full custom config
}
```

### Simple Python Integration
```python
import json
import subprocess

# Load config
with open('default_config.json') as f:
    config = json.load(f)

# Update for new RFQ
config['opportunity']['client_name'] = "New Client"
config['opportunity']['rfq_number'] = "12345"

# Save
with open('new_rfq.json', 'w') as f:
    json.dump(config, f)

# Generate
subprocess.run(['python3', 'generate_html_with_highlights.py', 'new_rfq.json'])
subprocess.run(['python3', 'generate_enhanced_pdf.py', 'new_rfq.json'])
```

### Direct Function Call
```python
from capability_statement_generator import handle_generate_capability_statement

# Generate from opportunity
result = handle_generate_capability_statement(
    opportunity_id="recXXXXXXXXXXX",
    template="default"
)

# Generate custom
result = handle_generate_capability_statement(
    client_name="CPS Energy",
    rfq_number="7000205103",
    rfq_title="Industrial Supplies",
    template="default"
)

print(f"HTML: {result['html_file']}")
print(f"PDF: {result['pdf_file']}")
```

---

## 📁 What Each File Does

| File | Purpose | Output |
|------|---------|--------|
| `generate_html_with_highlights.py` | HTML generator | .html file |
| `generate_enhanced_pdf.py` | PDF generator | .pdf file |
| `capability_statement_generator.py` | NEXUS automation module | API integration |
| `capability_statement_template.html` | Beautiful Tailwind template | HTML template |
| `default_config.json` | Default config template | Config data |
| `example_va_medical_config.json` | VA Medical template | Config data |
| `example_construction_config.json` | Construction template | Config data |

---

## 📝 Config File Structure

```json
{
    "company": {
        "name": "DEE DAVIS INC",
        "cage_code": "8UMX3",           ← Your CAGE
        "uei": "HJB4KNYJVGZ1",          ← Your UEI
        "duns": "002636755",            ← Your DUNS
        "tax_id": "84-4114181",         ← Your EIN
        "sam_status": "Active",
        "founded": "2018",
        "address": "755 W Big Beaver Rd, Suite 2020",
        "city": "Troy",
        "state": "MI",
        "zip": "48084",
        "phone": "248-376-4550",
        "email": "info@deedavis.biz",
        "website": "www.deedavis.biz",
        "president": "Dee Davis"
    },
    "opportunity": {
        "client_name": "CPS Energy",    ← Change this
        "rfq_number": "7000205103",     ← Change this
        "date": "January 2026",         ← Change this
        "title": "Industrial Supplies"  ← Change this
    },
    "colors": {
        "primary": "#0f172a",           ← Change colors
        "secondary": "#1e293b",
        "accent": "#d97706",            ← Change accent
        "text": "#334155",
        "light": "#f1f5f9"
    },
    "highlights": {
        "title": "QUICK FACTS",
        "items": [
            {
                "icon": "🎯",
                "label": "Primary NAICS",
                "value": "423850 - Industrial Supplies"
            },
            {
                "icon": "🤝",
                "label": "Key Partners",
                "value": "Grainger | Fastenal | Landstar"
            }
        ]
    },
    "overview": "Your company description...",
    "core_competencies": [
        {
            "title": "Competency Name",
            "description": "Description..."
        }
    ],
    "benefits": [
        {
            "icon": "✓",
            "title": "Benefit Name",
            "description": "Description..."
        }
    ],
    "certifications": [
        "EDWOSB - SBA Certified",
        "WOSB - Women-Owned Small Business"
    ],
    "contract_capabilities": {
        "payment_terms": "Net 30",
        "delivery_time": "10-15 business days",
        "coverage": "Nationwide",
        "insurance": "$1M+ General Liability"
    },
    "commitment": "Your commitment statement..."
}
```

---

## 🔧 Common Tasks

### Change Client Name & RFQ
1. Open config JSON
2. Find `"opportunity"` section
3. Update `client_name` and `rfq_number`
4. Run generators

### Change Colors
1. Open config JSON
2. Find `"colors"` section
3. Update `primary` and `accent` hex codes
4. Run generators

**Color Examples:**
- Blue: `#0066cc`
- Orange: `#f97316`
- Amber: `#d97706`
- Navy: `#0f172a`

### Add/Remove Highlights
1. Open config JSON
2. Find `"highlights"` → `"items"` array
3. Add/remove items
4. Run generators

### Create New Template
1. Copy existing config: `cp default_config.json my_new_config.json`
2. Edit everything
3. Run generators with new config

---

## 📦 File Naming Convention

```
config_name.json
  ↓
config_name.html          (HTML output)
config_name_enhanced.pdf  (PDF output)
```

**Examples:**
- `default_config.json` → `default.html` + `default_enhanced.pdf`
- `va_medical_config.json` → `va_medical.html` + `va_medical_enhanced.pdf`

---

## 🐛 Troubleshooting

**Q: Logo not showing?**
```bash
# The template uses a placeholder. Add your logo as base64 or use an image path
# Logo is embedded in the template
```

**Q: Colors not working?**
```json
// Must be hex codes with #
"colors": {
    "primary": "#0f172a",  ✓ Correct
    "accent": "d97706"     ✗ Wrong (missing #)
}
```

**Q: Text overlapping in highlights?**
```json
// Keep values short (under 50 characters)
"value": "Short text works best"  ✓
"value": "Very long text that goes on and on..."  ✗
```

**Q: PDF not generating?**
```bash
# Install PDF generator
brew install wkhtmltopdf
# OR
pip install weasyprint
# OR use Chrome to print HTML to PDF
```

---

## 🎯 Most Common Workflow

```bash
# 1. Copy template
cp default_config.json client_name_config.json

# 2. Edit
nano client_name_config.json
# Change: client_name, rfq_number, colors, highlights

# 3. Generate HTML for NEXUS
python3 generate_html_with_highlights.py client_name_config.json

# 4. Generate PDF for submission
python3 generate_enhanced_pdf.py client_name_config.json

# 5. Done!
ls client_name.html
ls client_name_enhanced.pdf
```

---

## 🚀 NEXUS Automation Examples

### Automate from NEXUS Opportunity
```python
from capability_statement_generator import handle_generate_capability_statement

# Generate from existing opportunity in Airtable
result = handle_generate_capability_statement(
    opportunity_id="recABC123",
    template="default"
)

# Result contains paths to generated files
print(result['html_file'])  # /path/to/capstat_ClientName_RFQ_20260123.html
print(result['pdf_file'])   # /path/to/capstat_ClientName_RFQ_20260123.pdf
```

### Custom Generation
```python
result = handle_generate_capability_statement(
    client_name="Department of Veterans Affairs",
    rfq_number="VA-26-1234",
    rfq_title="Medical Supplies",
    template="va_medical"
)
```

### Full Custom Config
```python
custom = {
    "company": {...},
    "opportunity": {...},
    "colors": {...},
    # ... full config
}

result = handle_generate_capability_statement(
    client_name="Custom Agency",
    rfq_number="12345",
    rfq_title="Custom Project",
    custom_config=custom
)
```

---

## 📊 Available Templates

| Template | Use Case | Accent Color | Best For |
|----------|----------|--------------|----------|
| `default` | Industrial Supplies | Amber (#d97706) | General contracting |
| `va_medical` | Healthcare/VA | Blue (#0066cc) | Medical supplies |
| `construction` | Construction | Orange (#f97316) | Building projects |

---

## 🔗 API Endpoints

### Generate Capability Statement
```
POST /capability-statements/generate
```

### List Templates
```
GET /capability-statements/templates
```

### List Generated Statements
```
GET /capability-statements/list
```

---

## 💡 Pro Tips

1. **Keep configs organized**: Create a `configs/` folder for each client
2. **Use descriptive names**: `cps_energy_2026_wipers_config.json`
3. **Test colors first**: Generate HTML first to preview colors before PDF
4. **Save successful configs**: Keep templates that work well
5. **Batch generate**: Use shell scripts to generate multiple at once

---

## 🎨 Color Palette Ideas

**Professional Blue:**
- Primary: `#0f172a` (Navy)
- Accent: `#0066cc` (Blue)

**Energy/Industrial:**
- Primary: `#0f172a` (Navy)
- Accent: `#d97706` (Amber)

**Construction:**
- Primary: `#0f172a` (Navy)
- Accent: `#f97316` (Orange)

**Healthcare:**
- Primary: `#1e3a8a` (Deep Blue)
- Accent: `#0066cc` (Medical Blue)

---

## 📱 Quick Commands Reference

```bash
# Generate from default
python3 generate_html_with_highlights.py default_config.json && \
python3 generate_enhanced_pdf.py default_config.json

# Generate from VA template
python3 generate_html_with_highlights.py example_va_medical_config.json && \
python3 generate_enhanced_pdf.py example_va_medical_config.json

# Generate from construction template
python3 generate_html_with_highlights.py example_construction_config.json && \
python3 generate_enhanced_pdf.py example_construction_config.json

# Make scripts executable
chmod +x generate_html_with_highlights.py
chmod +x generate_enhanced_pdf.py

# Then you can run without python3
./generate_html_with_highlights.py default_config.json
```

---

## 📁 Folder Structure

```
/Users/deedavis/NEXUS BACKEND/
├── generate_html_with_highlights.py     ← HTML generator script
├── generate_enhanced_pdf.py             ← PDF generator script
├── capability_statement_generator.py    ← NEXUS automation module
├── capability_statement_template.html   ← Beautiful Tailwind template
├── default_config.json                  ← Default template
├── example_va_medical_config.json       ← VA template
├── example_construction_config.json     ← Construction template
└── generated_capability_statements/     ← Output folder (auto-created)
    ├── capstat_ClientName_RFQ_timestamp.html
    └── capstat_ClientName_RFQ_timestamp.pdf
```

---

## 🎓 Advanced Usage

### Batch Generation Script
Create `generate_all.sh`:
```bash
#!/bin/bash
for config in configs/*.json; do
    python3 generate_html_with_highlights.py "$config"
    python3 generate_enhanced_pdf.py "$config"
done
```

### NEXUS Make.com Webhook
```json
{
    "url": "https://your-domain.com/capability-statements/generate",
    "method": "POST",
    "body": {
        "opportunity_id": "{{Opportunity ID}}",
        "template": "default"
    }
}
```

### Airtable Automation
1. Create "Generate Capability Statement" button in Opportunities table
2. Button triggers webhook to `/capability-statements/generate`
3. Files are generated and saved
4. Record ID is saved back to Airtable

---

## ✅ Quality Checklist

Before submitting:
- [ ] Client name is correct
- [ ] RFQ number is accurate
- [ ] Date is current
- [ ] Colors match branding
- [ ] Highlights are relevant
- [ ] All contact info is correct
- [ ] CAGE/UEI/DUNS are current
- [ ] Certifications are up to date
- [ ] PDF renders correctly
- [ ] File size is reasonable (<5MB)

---

## 🔥 Most Common Workflow

```bash
# 1. Copy template
cp default_config.json cps_energy_config.json

# 2. Edit (change client, RFQ, colors)
nano cps_energy_config.json

# 3. Generate HTML for NEXUS
python3 generate_html_with_highlights.py cps_energy_config.json

# 4. Generate PDF for submission
python3 generate_enhanced_pdf.py cps_energy_config.json

# 5. Done! Files are in current directory
open cps_energy.html
open cps_energy_enhanced.pdf
```

---

## 📞 Support

**Issues?**
- Check logs for errors
- Verify JSON is valid
- Ensure all required fields are present
- Test with default config first

**Need Help?**
- Review example configs
- Check NEXUS logs
- Test API endpoints with curl/Postman

---

**That's it!** Simple, fast, and ready for NEXUS automation. 🚀

---

## 🎯 NEXUS Integration Features

✅ **Auto-populate from Airtable** - Company info pulled from CompanyInfo table  
✅ **Template selection** - Choose from 3 pre-built templates  
✅ **Custom configurations** - Full control over every element  
✅ **API endpoints** - RESTful API for Make.com integration  
✅ **File management** - Auto-saves to Airtable with links  
✅ **Beautiful output** - Modern Tailwind CSS design  
✅ **Print-ready** - Professional PDF generation  

---

## 🔗 Related Files

- `api_server.py` - API endpoints added
- `nexus_backend.py` - Main NEXUS system
- `AIRTABLE_SETUP_AI_RECOMMENDATIONS.md` - Airtable schema guide
