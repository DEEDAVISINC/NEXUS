#!/usr/bin/env python3
"""
NEXUS RFQ Generator — Standard Template
Generates professional HTML RFQs matching the approved NEXUS format.
Applies sector color system for instant visual recognition.
"""

import json
import sys
import os

# Load DDI logo from assets
LOGO_PATH = os.path.join(os.path.dirname(__file__), 'assets', 'ddi_logo_base64.txt')

# Sector color schemes — matches cap-statement-colors.mdc
SECTOR_COLORS = {
    'fingerprinting': {
        'primary': '#1a2e1a',
        'secondary': '#2d5016',
        'accent_bg': '#f0fdf4',
        'table_header': '#2d5016',
        'badge': '#2d5016',
        'badge_border': '#1a2e1a'
    },
    'nemt': {
        'primary': '#1e3a5f',
        'secondary': '#dc2626',
        'accent_bg': '#fef2f2',
        'table_header': '#991b1b',
        'badge': '#dc2626',
        'badge_border': '#991b1b'
    },
    'drug_testing': {
        'primary': '#3b0764',
        'secondary': '#7c3aed',
        'accent_bg': '#faf5ff',
        'table_header': '#5b21b6',
        'badge': '#7c3aed',
        'badge_border': '#5b21b6'
    },
    'dna': {
        'primary': '#134e4a',
        'secondary': '#0d9488',
        'accent_bg': '#f0fdfa',
        'table_header': '#0f766e',
        'badge': '#0d9488',
        'badge_border': '#0f766e'
    },
    'janitorial': {
        'primary': '#451a03',
        'secondary': '#b45309',
        'accent_bg': '#fffbeb',
        'table_header': '#92400e',
        'badge': '#b45309',
        'badge_border': '#92400e'
    },
    'grounds': {
        'primary': '#451a03',
        'secondary': '#b45309',
        'accent_bg': '#fffbeb',
        'table_header': '#92400e',
        'badge': '#b45309',
        'badge_border': '#92400e'
    },
    'industrial': {
        'primary': '#1e293b',
        'secondary': '#475569',
        'accent_bg': '#f8fafc',
        'table_header': '#334155',
        'badge': '#475569',
        'badge_border': '#334155'
    },
    'courier': {
        'primary': '#7c2d12',
        'secondary': '#ea580c',
        'accent_bg': '#fff7ed',
        'table_header': '#c2410c',
        'badge': '#ea580c',
        'badge_border': '#c2410c'
    },
    'notary': {
        'primary': '#6b21a8',
        'secondary': '#a78bdb',
        'accent_bg': '#fdf4ff',
        'table_header': '#7c3aed',
        'badge': '#a78bdb',
        'badge_border': '#7c3aed'
    },
    'professional': {
        'primary': '#171717',
        'secondary': '#404040',
        'accent_bg': '#fafafa',
        'table_header': '#262626',
        'badge': '#404040',
        'badge_border': '#262626'
    },
    'default': {
        'primary': '#0f172a',
        'secondary': '#1e3a8a',
        'accent_bg': '#f8fafc',
        'table_header': '#1e3a8a',
        'badge': '#d97706',
        'badge_border': '#b45309'
    }
}

def get_sector_colors(sector):
    """Get color scheme for a sector"""
    return SECTOR_COLORS.get(sector.lower(), SECTOR_COLORS['default'])

def get_logo_data():
    """Load the DDI logo base64 data"""
    try:
        with open(LOGO_PATH, 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        return None

def generate_html(config):
    """Generate NEXUS-standard RFQ HTML from config"""
    
    rfq = config['rfq']
    items = config.get('items', [])
    scope = config.get('scope', {})
    submission = config.get('submission', {})
    terms = config.get('terms', {})
    supplier_fields = config.get('supplier_fields', [])
    
    # Get sector colors
    sector = config.get('sector', 'default')
    colors = get_sector_colors(sector)
    
    # Get logo
    logo_data = get_logo_data()
    logo_html = f'<img class="logo-img" src="{logo_data}" alt="Dee Davis Inc.">' if logo_data else ''
    
    # Build scope columns
    left_col = scope.get('left_column', {'title': 'Requirements', 'items': []})
    right_col = scope.get('right_column', {'title': 'Specifications', 'items': []})
    
    left_items = '\n'.join([f'      <li>{item}</li>' for item in left_col.get('items', [])])
    right_items = '\n'.join([f'      <li>{item}</li>' for item in right_col.get('items', [])])
    
    # Build items table rows
    items_rows = ''
    for i, item in enumerate(items):
        shade = 'row-shade' if i % 2 == 1 else ''
        if item.get('highlight'):
            shade = ''
            style = 'style="background:#eff6ff;"' if item.get('highlight') == 'blue' else 'style="background:#f0fdf4;"'
            no_style = 'style="color:#1e40af; font-size:12pt;"' if item.get('highlight') == 'blue' else 'style="color:#059669; font-size:12pt;"'
            item_style = f'style="color:#1e40af;"' if item.get('highlight') == 'blue' else 'style="color:#059669;"'
            price_style = 'style="font-size:9pt;color:#1e40af;font-weight:700;"' if item.get('highlight') == 'blue' else 'style="font-size:9pt;color:#059669;font-weight:700;"'
        else:
            style = ''
            no_style = ''
            item_style = ''
            price_style = 'style="font-size:9pt;color:#9ca3af;"'
        
        specs_list = item.get('specs', [])
        specs_html = '<ul class="spec-list">' + ''.join([f'<li>{s}</li>' for s in specs_list]) + '</ul>' if specs_list else item.get('specifications', '')
        
        icon = '★' if item.get('highlight') else item.get('number', i+1)
        
        items_rows += f'''
      <tr class="{shade}" {style}>
        <td class="col-no" {no_style}>{icon}</td>
        <td class="col-item" {item_style}>{item.get('description', '')}<br><span class="item-sub" style="color:#6b7280;">{item.get('sub', '')}</span></td>
        <td class="col-specs">{specs_html}</td>
        <td class="col-qty">{item.get('quantity', '')}</td>
        <td class="col-freq">{item.get('frequency', '')}</td>
        <td class="col-price">$________<br><span {price_style}>{item.get('price_label', 'per unit')}</span></td>
      </tr>'''
    
    # Build submission steps
    submission_steps = submission.get('steps', [])
    steps_html = '\n'.join([f'      <li>{step}</li>' for step in submission_steps])
    
    # Build terms list
    terms_items = terms.get('items', [])
    terms_html = '\n'.join([f'      <li><strong>{t.get("label", "")}:</strong> {t.get("value", "")}</li>' for t in terms_items])
    
    # Build supplier fields grid
    fields_html = ''
    for field in supplier_fields:
        fields_html += f'''
    <div class="fill-field">
      <div class="fill-label">{field}</div>
      <div class="fill-line">&nbsp;</div>
    </div>'''
    
    # Build email mailto link
    email_subject = rfq.get('email_subject', f"Quote — {rfq.get('number', 'RFQ')} — {rfq.get('title', 'Quote Request')}")
    email_body = rfq.get('email_body', 'Please find our quote attached.')
    import urllib.parse
    mailto_link = f"mailto:info@deedavis.biz?subject={urllib.parse.quote(email_subject)}&body={urllib.parse.quote(email_body)}"
    
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>RFQ {rfq.get('number', '')} — {rfq.get('title', '')} — Dee Davis Inc.</title>
<style>
  @page {{ size: letter; margin: 0; }}
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ font-family: 'Avenir Next','Avenir','Helvetica Neue',Arial,sans-serif; font-size: 11pt; color: #1f2937; background: #fff; }}

  .header {{ background: {colors['primary']}; color: #fff; padding: 26px 34px 22px; display: flex; align-items: center; justify-content: space-between; }}
  .logo-img {{ height: 64px; width: auto; object-fit: contain; }}
  .header-right {{ text-align: right; }}
  .rfq-badge {{ display: inline-block; background: {colors['badge']}; color: #fff; font-size: 9pt; font-weight: 700; letter-spacing: 1.2px; padding: 4px 12px; border-radius: 3px; margin-bottom: 4px; }}
  .rfq-title {{ font-size: 16pt; font-weight: 700; color: #fff; line-height: 1.2; }}
  .rfq-sub {{ font-size: 10pt; color: #94a3b8; margin-top: 3px; }}

  .meta-strip {{ display: flex; justify-content: space-between; background: {colors['accent_bg']}; border-bottom: 2px solid #e5e7eb; padding: 12px 24px; }}
  .meta-cell {{ text-align: center; flex: 1; }}
  .meta-label {{ font-size: 8.5pt; font-weight: 700; color: #6b7280; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 3px; }}
  .meta-value {{ font-size: 11pt; font-weight: 700; color: #0f172a; }}
  .meta-deadline {{ color: #b91c1c; }}

  .protection-banner {{ background: #fef3c7; border-left: 4px solid #d97706; padding: 10px 18px; font-size: 10pt; color: #78350f; }}

  .section-header {{ background: {colors['primary']}; color: #fff; font-size: 10pt; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase; padding: 9px 16px; }}

  .intro-block {{ padding: 14px 18px; border-bottom: 1px solid #e5e7eb; font-size: 11pt; line-height: 1.6; color: #374151; }}

  .scope-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 0; border-bottom: 1px solid #e5e7eb; }}
  .scope-col {{ padding: 16px 18px; }}
  .scope-col-title {{ font-size: 10pt; font-weight: 700; color: #0f172a; margin-bottom: 8px; letter-spacing: 0.5px; text-transform: uppercase; }}
  .scope-list {{ list-style: none; }}
  .scope-list li {{ font-size: 10.5pt; color: #374151; padding: 4px 0 4px 18px; position: relative; line-height: 1.5; border-bottom: 1px solid #f3f4f6; }}
  .scope-list li:last-child {{ border-bottom: none; }}
  .scope-list li::before {{ content: "✓"; position: absolute; left: 0; color: #059669; font-weight: 700; font-size: 10pt; }}

  .table-wrap {{ overflow-x: auto; }}
  table.items-table {{ width: 100%; border-collapse: collapse; font-size: 10.5pt; }}
  table.items-table thead tr {{ background: {colors['table_header']}; color: #fff; }}
  table.items-table thead th {{ padding: 10px 10px; text-align: left; font-size: 9pt; font-weight: 700; letter-spacing: 0.8px; text-transform: uppercase; white-space: nowrap; }}
  table.items-table thead th.right {{ text-align: right; }}
  table.items-table tbody tr {{ border-bottom: 1px solid #e5e7eb; vertical-align: top; }}
  table.items-table tbody tr.row-shade {{ background: #f8fafc; }}
  table.items-table td {{ padding: 12px 10px; line-height: 1.5; }}
  .col-no {{ width: 4%; text-align: center; font-weight: 700; color: #0f172a; }}
  .col-item {{ width: 20%; font-weight: 600; color: #0f172a; font-size: 10.5pt; }}
  .col-specs {{ width: 34%; color: #374151; }}
  .col-qty {{ width: 12%; text-align: center; font-weight: 600; color: {colors['secondary']}; }}
  .col-freq {{ width: 10%; text-align: center; color: #6b7280; font-size: 10pt; }}
  .col-price {{ width: 10%; text-align: right; }}
  .item-sub {{ font-size: 9pt; color: #6b7280; font-weight: 400; }}
  .spec-list {{ list-style: none; }}
  .spec-list li {{ font-size: 10pt; color: #4b5563; padding: 2px 0; line-height: 1.45; }}
  .total-row td {{ border-top: 2px solid #0f172a; font-weight: 700; font-size: 11pt; }}

  .two-col {{ display: grid; grid-template-columns: 1fr 1fr; border-bottom: 1px solid #e5e7eb; }}
  .two-col-block {{ padding: 14px 18px; }}
  .two-col-block:first-child {{ border-right: 1px solid #e5e7eb; }}
  .block-title {{ font-size: 9.5pt; font-weight: 700; color: #0f172a; text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 10px; }}
  .step-list {{ list-style: none; counter-reset: steps; }}
  .step-list li {{ counter-increment: steps; padding: 4px 0 4px 28px; position: relative; font-size: 10pt; color: #374151; line-height: 1.5; border-bottom: 1px solid #f3f4f6; }}
  .step-list li:last-child {{ border-bottom: none; }}
  .step-list li::before {{ content: counter(steps); position: absolute; left: 0; width: 18px; height: 18px; background: {colors['table_header']}; color: #fff; border-radius: 50%; font-size: 8.5pt; font-weight: 700; text-align: center; line-height: 18px; top: 4px; }}
  .terms-list {{ list-style: none; }}
  .terms-list li {{ padding: 5px 0; font-size: 10pt; color: #374151; border-bottom: 1px solid #f3f4f6; line-height: 1.5; }}
  .terms-list li:last-child {{ border-bottom: none; }}
  .terms-list strong {{ color: #0f172a; }}

  .fill-in-block {{ padding: 14px 18px; border-bottom: 1px solid #e5e7eb; }}
  .fill-grid {{ display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 12px; }}
  .fill-field {{ border: 1px solid #d1d5db; border-radius: 4px; padding: 8px 12px; background: #f9fafb; }}
  .fill-label {{ font-size: 8.5pt; font-weight: 700; color: #6b7280; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px; }}
  .fill-line {{ border-bottom: 1px solid #9ca3af; min-height: 22px; }}

  .submit-block {{ background: linear-gradient(135deg, {colors['primary']} 0%, {colors['table_header']} 100%); padding: 26px 34px; display: flex; align-items: center; justify-content: space-between; gap: 24px; }}
  .submit-copy {{ color: #cbd5e1; font-size: 11pt; line-height: 1.5; }}
  .submit-copy strong {{ color: #fff; font-size: 12pt; display: block; margin-bottom: 3px; }}
  .submit-deadline {{ color: #fde68a; font-size: 10.5pt; font-weight: 700; margin-top: 5px; display: block; }}
  .submit-sub {{ font-size: 9pt; color: #94a3b8; margin-top: 8px; line-height: 1.4; }}
  .submit-btn {{ display: inline-block; background: {colors['badge']}; color: #fff !important; text-decoration: none; font-size: 12pt; font-weight: 700; padding: 14px 30px; border-radius: 6px; white-space: nowrap; letter-spacing: 0.3px; border: 2px solid {colors['badge_border']}; flex-shrink: 0; }}

  .footer {{ background: {colors['primary']}; color: #94a3b8; padding: 14px 24px; display: flex; justify-content: space-between; align-items: center; font-size: 9pt; }}
  .footer strong {{ color: #fff; }}
  .footer-right {{ text-align: right; }}

  @media print {{ body, .header, .section-header, table.items-table thead tr, .footer, .submit-block {{ -webkit-print-color-adjust: exact; print-color-adjust: exact; }} }}
</style>
</head>
<body>

<div class="header">
  {logo_html}
  <div class="header-right">
    <div class="rfq-badge">REQUEST FOR QUOTE</div>
    <div class="rfq-title">{rfq.get('title', '')}</div>
    <div class="rfq-sub">{rfq.get('subtitle', '')}</div>
  </div>
</div>

<div class="meta-strip">
  <div class="meta-cell"><div class="meta-label">RFQ Number</div><div class="meta-value">{rfq.get('number', '')}</div></div>
  <div class="meta-cell"><div class="meta-label">Issue Date</div><div class="meta-value">{rfq.get('issue_date', '')}</div></div>
  <div class="meta-cell"><div class="meta-label">Quote Due</div><div class="meta-value meta-deadline">{rfq.get('due_date', '')}</div></div>
  <div class="meta-cell"><div class="meta-label">Due Time</div><div class="meta-value meta-deadline">{rfq.get('due_time', '')}</div></div>
  <div class="meta-cell"><div class="meta-label">Contract Type</div><div class="meta-value">{rfq.get('contract_type', '')}</div></div>
  <div class="meta-cell"><div class="meta-label">Send Quote To</div><div class="meta-value">info@deedavis.biz</div></div>
</div>

<div class="protection-banner">
  <strong>&#9888; CONFIDENTIAL —</strong> This RFQ is issued by Dee Davis Inc. as Prime Contractor. Supplier shall not contact the end client directly. All coordination through DDI.
</div>

<div class="section-header">{scope.get('about_title', 'About This Procurement')}</div>
<div class="intro-block">{scope.get('about_text', '')}</div>

<div class="section-header">{scope.get('scope_title', 'Scope of Work')}</div>
<div class="scope-grid">
  <div class="scope-col">
    <div class="scope-col-title">{left_col.get('title', 'Requirements')}</div>
    <ul class="scope-list">
{left_items}
    </ul>
  </div>
  <div class="scope-col">
    <div class="scope-col-title">{right_col.get('title', 'Specifications')}</div>
    <ul class="scope-list">
{right_items}
    </ul>
  </div>
</div>

<div class="section-header">{rfq.get('items_title', 'Line Items — Pricing Request')}</div>
<div class="table-wrap">
  <table class="items-table">
    <thead>
      <tr>
        <th class="col-no">#</th>
        <th class="col-item">Item / Description</th>
        <th class="col-specs">Specifications &amp; Notes</th>
        <th class="col-qty">Est. Qty</th>
        <th class="col-freq">Frequency</th>
        <th class="col-price right">Your Price</th>
      </tr>
    </thead>
    <tbody>
{items_rows}
    </tbody>
  </table>
</div>

<div class="section-header">How to Respond &amp; Contract Terms</div>
<div class="two-col">
  <div class="two-col-block">
    <div class="block-title">{submission.get('title', 'How to Submit Your Quote')}</div>
    <ol class="step-list">
{steps_html}
    </ol>
  </div>
  <div class="two-col-block">
    <div class="block-title">{terms.get('title', 'Contract Terms')}</div>
    <ul class="terms-list">
{terms_html}
    </ul>
  </div>
</div>

<div class="section-header">Supplier Information</div>
<div class="fill-in-block">
  <div class="fill-grid">
{fields_html}
  </div>
</div>

<div class="submit-block">
  <div class="submit-copy">
    <strong>Ready to Submit Your Quote?</strong>
    Click the button — a pre-addressed email will open. Attach your pricing and any supporting documents.
    <span class="submit-deadline">&#9200; Deadline: {rfq.get('due_date', '')} @ {rfq.get('due_time', '')} — Late submissions will not be accepted.</span>
    <div class="submit-sub">
      Subject line will auto-populate. Questions? Call 248.376.4550 or email info@deedavis.biz.
    </div>
  </div>
  <a class="submit-btn" href="{mailto_link}">&#128231; Submit Quote by Email</a>
</div>

<div class="footer">
  <div><strong>Dee Davis Inc.</strong> — EDWOSB | WOSB | WBENC | MBE | SBE | CAGE: 8UMX3 | UEI: HJB4KNYJVGZ1</div>
  <div class="footer-right">755 W. Big Beaver Rd., Suite 2020, Troy, MI 48084 • 248.376.4550 • info@deedavis.biz</div>
</div>

</body>
</html>'''
    
    return html


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 generate_rfq_html.py <config.json>")
        print("\nConfig JSON structure:")
        print('''{
  "rfq": {
    "number": "DDI-2026-XXX",
    "title": "Product/Service Name",
    "subtitle": "Location — Client Type",
    "issue_date": "Month DD, YYYY",
    "due_date": "Month DD, YYYY",
    "due_time": "HH:MM AM/PM TZ",
    "contract_type": "Recurring / One-Time",
    "badge_color": "#d97706",
    "badge_border": "#b45309"
  },
  "scope": {
    "about_title": "About This Procurement",
    "about_text": "Description of DDI and procurement...",
    "scope_title": "Scope of Work",
    "left_column": { "title": "Requirements", "items": ["Item 1", "Item 2"] },
    "right_column": { "title": "Specifications", "items": ["Spec 1", "Spec 2"] }
  },
  "items": [
    {
      "number": 1,
      "description": "Item Name",
      "sub": "Sub-description",
      "specs": ["Spec 1", "Spec 2"],
      "quantity": "100",
      "frequency": "Per month",
      "price_label": "per unit",
      "highlight": null
    }
  ],
  "submission": {
    "title": "How to Submit Your Quote",
    "steps": ["Step 1", "Step 2"]
  },
  "terms": {
    "title": "Contract Terms",
    "items": [
      { "label": "Payment Terms", "value": "Net 30" }
    ]
  },
  "supplier_fields": ["Company Name", "Contact Name", "Phone", "Email"]
}''')
        sys.exit(1)
    
    config_file = sys.argv[1]
    
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    html = generate_html(config)
    
    output_file = config_file.replace('_config.json', '.html').replace('.json', '.html')
    with open(output_file, 'w') as f:
        f.write(html)
    
    print(f"✓ Generated: {output_file}")


if __name__ == "__main__":
    main()
