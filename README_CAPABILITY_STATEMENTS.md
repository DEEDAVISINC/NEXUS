# 🎯 CAPABILITY STATEMENT GENERATOR FOR NEXUS

## Welcome!

This is your complete capability statement automation system. Generate professional, beautiful capability statements in seconds.

---

## ⚡ Quick Start (30 Seconds)

```bash
# 1. Generate HTML
python3 generate_html_with_highlights.py default_config.json

# 2. View it
open default.html

# 3. Generate PDF
python3 generate_enhanced_pdf.py default_config.json

# 4. Done!
open default_enhanced.pdf
```

---

## 📚 Documentation

| File | Purpose |
|------|---------|
| **CAPABILITY_STATEMENT_QUICK_REFERENCE.md** | **START HERE** - All commands and examples |
| AIRTABLE_CAPABILITY_STATEMENTS_SETUP.md | Airtable table setup guide |
| CAPABILITY_STATEMENT_SYSTEM_COMPLETE.md | Technical system overview |
| NEXUS_CAPABILITY_STATEMENT_AUTOMATION.md | Integration guide |

---

## 🎨 Templates Available

### 1. Default (Industrial Supplies)
- **Color:** Amber
- **Use for:** General contracting, industrial supplies
- **File:** `default_config.json`

### 2. VA Medical (Healthcare)
- **Color:** Blue
- **Use for:** VA facilities, medical supplies
- **File:** `example_va_medical_config.json`

### 3. Construction
- **Color:** Orange
- **Use for:** Building projects, facilities
- **File:** `example_construction_config.json`

---

## 🔥 Most Common Workflow

```bash
# Copy template
cp default_config.json my_rfq_config.json

# Edit client name & RFQ number
nano my_rfq_config.json

# Generate HTML & PDF
python3 generate_html_with_highlights.py my_rfq_config.json && \
python3 generate_enhanced_pdf.py my_rfq_config.json

# Files created:
# - my_rfq.html (for NEXUS)
# - my_rfq_enhanced.pdf (for submission)
```

---

## 🤖 NEXUS API

### Generate Statement
```http
POST /capability-statements/generate
{
    "client_name": "Your Client",
    "rfq_number": "12345",
    "template": "default"
}
```

### List Templates
```http
GET /capability-statements/templates
```

### List Generated
```http
GET /capability-statements/list
```

---

## 🎯 What Gets Generated

### HTML File (for NEXUS)
- Modern Tailwind CSS design
- Lucide icons
- Responsive layout
- Print-optimized
- ~15-20KB file size

### PDF File (for Submission)
- A4 print-ready format
- High-resolution
- Professional quality
- ~200-500KB file size

---

## 💡 Quick Tips

1. **Start with default** - Test with `default_config.json` first
2. **Customize colors** - Match client branding when possible
3. **Tailor highlights** - Change quick facts for each RFQ
4. **Keep configs organized** - Save successful templates
5. **Review before sending** - Always check HTML first

---

## 🐛 Troubleshooting

**PDF not generating?**
```bash
brew install wkhtmltopdf
# OR
pip install weasyprint
```

**Colors not working?**
- Use `#` prefix: `"#0f172a"` ✓ not `"0f172a"` ✗

**File not found?**
- Check you're in the right directory
- Verify config file exists: `ls *_config.json`

---

## 📞 Need Help?

1. Read: `CAPABILITY_STATEMENT_QUICK_REFERENCE.md`
2. Check example configs: `example_*.json`
3. Test with default: `python3 generate_html_with_highlights.py default_config.json`
4. Review generated HTML: `open default.html`

---

## ✅ System Status

- **Core Scripts:** ✅ Ready
- **Templates:** ✅ 3 available
- **API Integration:** ✅ Complete
- **Documentation:** ✅ Comprehensive
- **Tested:** ✅ Working
- **NEXUS Integrated:** ✅ Yes

---

## 🎉 You're Ready!

Generate your first capability statement now:

```bash
python3 generate_html_with_highlights.py default_config.json
open default.html
```

**Beautiful, professional, ready in seconds!** 🚀

---

*For complete documentation, see: **CAPABILITY_STATEMENT_QUICK_REFERENCE.md***
