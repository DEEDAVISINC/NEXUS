#!/usr/bin/env python3
"""
NEXUS Invoice Generator — Sector Color System
Generates professional HTML invoices with government/enterprise compliance fields.
"""

import json
import sys
import os
from datetime import datetime

# Load DDI logo from assets
LOGO_PATH = os.path.join(os.path.dirname(__file__), 'assets', 'ddi_logo_base64.txt')

# Sector color schemes — matches unified-document-branding.mdc
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
        'badge': '#1e3a8a',
        'badge_border': '#1e40af'
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

def format_currency(amount):
    """Format amount as USD currency"""
    return f"${amount:,.2f}"

def generate_invoice_html(config):
    """Generate NEXUS-standard Invoice HTML from config"""
    
    invoice = config['invoice']
    client = config.get('client', {})
    items = config.get('line_items', [])
    contract = config.get('contract', {})
    
    # Get sector colors
    sector = config.get('sector', 'default')
    colors = get_sector_colors(sector)
    
    # Get logo
    logo_data = get_logo_data()
    logo_html = f'<img class="logo-img" src="{logo_data}" alt="Dee Davis Inc.">' if logo_data else ''
    
    # Build line items table
    items_rows = ''
    subtotal = 0
    for i, item in enumerate(items):
        shade = 'row-shade' if i % 2 == 1 else ''
        qty = item.get('quantity', 1)
        rate = item.get('rate', 0)
        amount = qty * rate
        subtotal += amount
        items_rows += f'''
      <tr class="{shade}">
        <td class="col-no">{i+1}</td>
        <td class="col-desc">{item.get('description', '')}<br><span class="item-sub">{item.get('details', '')}</span></td>
        <td class="col-qty">{qty}</td>
        <td class="col-rate">{format_currency(rate)}</td>
        <td class="col-amount">{format_currency(amount)}</td>
      </tr>'''
    
    # Calculate totals
    shipping = invoice.get('shipping', 0)
    tax_rate = invoice.get('tax_rate', 0)
    tax_amount = subtotal * tax_rate
    total = subtotal + shipping + tax_amount
    
    # Contract info section (for government invoices)
    contract_html = ''
    if contract:
        contract_html = f'''
<div class="section-header">Contract Information</div>
<div class="contract-grid">
  <div class="contract-item"><span class="contract-label">Contract Number</span><span class="contract-value">{contract.get('number', 'N/A')}</span></div>
  <div class="contract-item"><span class="contract-label">Contract Type</span><span class="contract-value">{contract.get('type', 'FFP')}</span></div>
  <div class="contract-item"><span class="contract-label">CLIN</span><span class="contract-value">{contract.get('clin', 'N/A')}</span></div>
  <div class="contract-item"><span class="contract-label">Period of Performance</span><span class="contract-value">{contract.get('pop', 'N/A')}</span></div>
  <div class="contract-item"><span class="contract-label">Contracting Officer</span><span class="contract-value">{contract.get('co_name', 'N/A')}</span></div>
  <div class="contract-item"><span class="contract-label">Payment Office</span><span class="contract-value">{contract.get('payment_office', 'N/A')}</span></div>
</div>'''
    
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Invoice {invoice.get('number', '')} — Dee Davis Inc.</title>
<style>
  @page {{ size: letter; margin: 0.5in; }}
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ font-family: 'Avenir Next','Avenir','Helvetica Neue',Arial,sans-serif; font-size: 10pt; color: #1f2937; background: #fff; }}

  .header {{ background: {colors['primary']}; color: #fff; padding: 24px 30px; display: flex; align-items: center; justify-content: space-between; }}
  .logo-img {{ height: 56px; width: auto; object-fit: contain; }}
  .header-right {{ text-align: right; }}
  .invoice-badge {{ display: inline-block; background: {colors['badge']}; color: #fff; font-size: 9pt; font-weight: 700; letter-spacing: 1.2px; padding: 4px 12px; border-radius: 3px; margin-bottom: 4px; }}
  .invoice-title {{ font-size: 14pt; font-weight: 700; color: #fff; }}
  .invoice-number {{ font-size: 18pt; font-weight: 700; color: #fff; margin-top: 2px; }}

  .meta-strip {{ display: flex; justify-content: space-between; background: {colors['accent_bg']}; border-bottom: 2px solid #e5e7eb; padding: 12px 24px; }}
  .meta-cell {{ text-align: center; flex: 1; }}
  .meta-label {{ font-size: 8pt; font-weight: 700; color: #6b7280; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 2px; }}
  .meta-value {{ font-size: 10pt; font-weight: 700; color: #0f172a; }}
  .meta-due {{ color: #b91c1c; }}

  .addresses {{ display: grid; grid-template-columns: 1fr 1fr; gap: 30px; padding: 20px 24px; border-bottom: 1px solid #e5e7eb; }}
  .address-block {{ }}
  .address-title {{ font-size: 8pt; font-weight: 700; color: #6b7280; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 8px; }}
  .address-content {{ font-size: 10pt; line-height: 1.6; color: #374151; }}
  .address-content strong {{ color: #0f172a; }}

  .section-header {{ background: {colors['primary']}; color: #fff; font-size: 9pt; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase; padding: 8px 16px; }}

  .contract-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; padding: 14px 18px; border-bottom: 1px solid #e5e7eb; }}
  .contract-item {{ }}
  .contract-label {{ font-size: 8pt; font-weight: 700; color: #6b7280; text-transform: uppercase; display: block; }}
  .contract-value {{ font-size: 10pt; color: #0f172a; font-weight: 500; }}

  .table-wrap {{ padding: 0 24px; }}
  table.items-table {{ width: 100%; border-collapse: collapse; font-size: 10pt; margin: 16px 0; }}
  table.items-table thead tr {{ background: {colors['table_header']}; color: #fff; }}
  table.items-table thead th {{ padding: 10px 12px; text-align: left; font-size: 8pt; font-weight: 700; letter-spacing: 0.8px; text-transform: uppercase; }}
  table.items-table thead th.right {{ text-align: right; }}
  table.items-table tbody tr {{ border-bottom: 1px solid #e5e7eb; }}
  table.items-table tbody tr.row-shade {{ background: {colors['accent_bg']}; }}
  table.items-table td {{ padding: 12px; line-height: 1.4; }}
  .col-no {{ width: 5%; text-align: center; font-weight: 600; color: {colors['secondary']}; }}
  .col-desc {{ width: 45%; color: #0f172a; }}
  .col-qty {{ width: 12%; text-align: center; }}
  .col-rate {{ width: 18%; text-align: right; }}
  .col-amount {{ width: 20%; text-align: right; font-weight: 600; color: {colors['secondary']}; }}
  .item-sub {{ font-size: 9pt; color: #6b7280; }}

  .totals-section {{ display: flex; justify-content: flex-end; padding: 0 24px 20px; }}
  .totals-box {{ width: 280px; }}
  .total-row {{ display: flex; justify-content: space-between; padding: 8px 12px; border-bottom: 1px solid #e5e7eb; font-size: 10pt; }}
  .total-row.grand {{ background: {colors['primary']}; color: #fff; font-size: 12pt; font-weight: 700; border-radius: 4px; margin-top: 8px; }}

  .payment-section {{ background: {colors['accent_bg']}; padding: 16px 24px; border-top: 2px solid #e5e7eb; }}
  .payment-title {{ font-size: 9pt; font-weight: 700; color: #0f172a; text-transform: uppercase; margin-bottom: 10px; }}
  .payment-details {{ font-size: 10pt; color: #374151; line-height: 1.6; }}
  .payment-details strong {{ color: #0f172a; }}

  .notes-section {{ padding: 16px 24px; border-top: 1px solid #e5e7eb; font-size: 9pt; color: #6b7280; line-height: 1.5; }}

  .footer {{ background: {colors['primary']}; color: #94a3b8; padding: 14px 24px; display: flex; justify-content: space-between; align-items: center; font-size: 8pt; }}
  .footer strong {{ color: #fff; }}

  @media print {{ body, .header, .section-header, table.items-table thead tr, .footer, .total-row.grand {{ -webkit-print-color-adjust: exact; print-color-adjust: exact; }} }}
</style>
</head>
<body>

<div class="header">
  {logo_html}
  <div class="header-right">
    <div class="invoice-badge">INVOICE</div>
    <div class="invoice-title">{invoice.get('service_description', 'Professional Services')}</div>
    <div class="invoice-number">{invoice.get('number', '')}</div>
  </div>
</div>

<div class="meta-strip">
  <div class="meta-cell"><div class="meta-label">Invoice Date</div><div class="meta-value">{invoice.get('date', '')}</div></div>
  <div class="meta-cell"><div class="meta-label">Due Date</div><div class="meta-value meta-due">{invoice.get('due_date', '')}</div></div>
  <div class="meta-cell"><div class="meta-label">Payment Terms</div><div class="meta-value">{invoice.get('terms', 'Net 30')}</div></div>
  <div class="meta-cell"><div class="meta-label">PO Number</div><div class="meta-value">{invoice.get('po_number', 'N/A')}</div></div>
  <div class="meta-cell"><div class="meta-label">Amount Due</div><div class="meta-value meta-due">{format_currency(total)}</div></div>
</div>

<div class="addresses">
  <div class="address-block">
    <div class="address-title">From</div>
    <div class="address-content">
      <strong>Dee Davis Inc.</strong><br>
      755 W. Big Beaver Rd., Suite 2020<br>
      Troy, MI 48084<br>
      248.376.4550 | info@deedavis.biz<br>
      <br>
      CAGE: 8UMX3 | UEI: HJB4KNYJVGZ1
    </div>
  </div>
  <div class="address-block">
    <div class="address-title">Bill To</div>
    <div class="address-content">
      <strong>{client.get('name', '')}</strong><br>
      {client.get('address', '').replace(chr(10), '<br>')}
      {f"<br>Attn: {client.get('contact', '')}" if client.get('contact') else ''}
    </div>
  </div>
</div>

{contract_html}

<div class="section-header">Services & Line Items</div>
<div class="table-wrap">
  <table class="items-table">
    <thead>
      <tr>
        <th class="col-no">#</th>
        <th>Description</th>
        <th class="right">Qty</th>
        <th class="right">Rate</th>
        <th class="right">Amount</th>
      </tr>
    </thead>
    <tbody>
{items_rows}
    </tbody>
  </table>
</div>

<div class="totals-section">
  <div class="totals-box">
    <div class="total-row"><span>Subtotal</span><span>{format_currency(subtotal)}</span></div>
    {f'<div class="total-row"><span>Shipping & Handling</span><span>{format_currency(shipping)}</span></div>' if shipping else ''}
    {f'<div class="total-row"><span>Tax ({tax_rate*100:.1f}%)</span><span>{format_currency(tax_amount)}</span></div>' if tax_amount else ''}
    <div class="total-row grand"><span>Total Due</span><span>{format_currency(total)}</span></div>
  </div>
</div>

<div class="payment-section">
  <div class="payment-title">Payment Information</div>
  <div class="payment-details">
    <strong>Pay by ACH (Preferred):</strong> Contact info@deedavis.biz for ACH details<br>
    <strong>Pay by Check:</strong> Make payable to "Dee Davis Inc." and mail to address above<br>
    {f"<strong>WAWF:</strong> Submit via Wide Area Workflow — CAGE 8UMX3" if contract.get('wawf') else ''}
  </div>
</div>

<div class="notes-section">
  {invoice.get('notes', 'Thank you for your business. Please remit payment by the due date.')}
</div>

<div class="footer">
  <div><strong>Dee Davis Inc.</strong> — EDWOSB | WOSB | WBENC | MBE | SBE | CAGE: 8UMX3</div>
  <div>Invoice {invoice.get('number', '')} — {invoice.get('date', '')}</div>
</div>

</body>
</html>'''
    
    return html


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 generate_invoice_html.py <config.json>")
        print("\nConfig JSON structure:")
        print('''{
  "sector": "courier",
  "invoice": {
    "number": "INV-2026-0001",
    "date": "March 12, 2026",
    "due_date": "April 11, 2026",
    "terms": "Net 30",
    "po_number": "PO-12345",
    "service_description": "Medical Courier Services"
  },
  "client": {
    "name": "VA Medical Center",
    "address": "123 Main St\\nDetroit, MI 48201",
    "contact": "John Smith"
  },
  "contract": {
    "number": "36C25626P0001",
    "type": "FFP",
    "clin": "0001",
    "pop": "01/01/2026 - 12/31/2026",
    "co_name": "Jane Doe",
    "payment_office": "DFAS Columbus",
    "wawf": true
  },
  "line_items": [
    {
      "description": "Medical Courier Services",
      "details": "Weekly specimen transport - January 2026",
      "quantity": 4,
      "rate": 250.00
    }
  ]
}''')
        sys.exit(1)
    
    config_file = sys.argv[1]
    
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    html = generate_invoice_html(config)
    
    output_file = config_file.replace('_config.json', '.html').replace('.json', '.html')
    with open(output_file, 'w') as f:
        f.write(html)
    
    print(f"✓ Generated: {output_file}")


if __name__ == "__main__":
    main()
