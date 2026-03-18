#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║         NEXUS — STANDARD RFQ HTML GENERATOR                                 ║
║         Dee Davis Inc. | CAGE 8UMX3 | EDWOSB                                ║
║                                                                              ║
║  This is the MASTER template for all supplier RFQs.                         ║
║  EVERY quote request to a supplier MUST use this template.                  ║
║                                                                              ║
║  USAGE:                                                                      ║
║    1. Copy this file into your bid's SEND_TO_SUPPLIER/ folder               ║
║    2. Edit the CONFIG section at the top                                     ║
║    3. Run: python3 RFQ_STANDARD_TEMPLATE_GENERATOR.py                       ║
║    4. Open the generated HTML in Chrome → Cmd+P → Save as PDF               ║
║    5. Attach PDF to email and send to suppliers                              ║
║                                                                              ║
║  BUYER PROTECTION: NEVER put the end client's name, solicitation number,    ║
║  or specific address in this file. Use generic terms only.                  ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import base64, os, sys, re
from datetime import datetime

# ══════════════════════════════════════════════════════════════════════════════
#  ▶ CONFIGURATION — Edit this section for each new RFQ
# ══════════════════════════════════════════════════════════════════════════════

CONFIG = {
    # ── RFQ Identity ──────────────────────────────────────────────────────────
    "rfq_number":       "DDI-2026-XXX",           # Sequential: DDI-YYYY-###
    "rfq_title":        "Product/Service Description",
    "rfq_subtitle":     "Region | Generic Client Type",  # e.g. "Jackson, MS | Government Client"
    "issue_date":       datetime.today().strftime("%B %d, %Y"),
    "due_date":         "MONTH DD, YYYY",          # 3-5 days before govt deadline
    "due_time":         "12:00 PM EST",
    "contract_period":  "One-time order",          # or "Annual contract", "Base + options"

    # ── Submit email ─────────────────────────────────────────────────────────
    "submit_to_email":  "bids.deedavisinc@gmail.com",
    "submit_cc_email":  "info@deedavis.biz",

    # ── Introduction paragraph ────────────────────────────────────────────────
    "introduction": (
        "Dee Davis Inc. (CAGE: 8UMX3 | EDWOSB Certified | Troy, MI) is the prime contractor "
        "managing this procurement on behalf of a government client. We are soliciting competitive "
        "pricing from qualified suppliers. [ADD SPECIFIC CONTEXT HERE — volume, region, urgency, etc.]"
    ),

    # ── Scope boxes (two columns) ─────────────────────────────────────────────
    "scope_supplier_must": [
        "Requirement 1",
        "Requirement 2",
        "Requirement 3",
        "Requirement 4",
        "Requirement 5",
    ],
    "scope_compliance": [
        "General Liability Insurance — minimum $1M per occurrence",
        "W-9 on file (required prior to first payment)",
        "COI with Dee Davis Inc. listed as Additional Insured",
        "Must NOT contact end client directly — all coordination through DDI",
    ],

    # ── Line items ────────────────────────────────────────────────────────────
    # Each item: no, item (HTML ok), specs (list of strings), est_qty, freq,
    #            price_label (e.g. "per lb", "per unit", "per trip")
    "items": [
        {
            "no":          "1",
            "item":        "Item Name<br><span class='item-sub'>Sub-label</span>",
            "specs":       [
                "Specification line 1",
                "Specification line 2",
                "Specification line 3",
            ],
            "est_qty":     "Quantity",
            "freq":        "Per order",
            "price_label": "per unit",
        },
    ],

    # ── Submission steps ──────────────────────────────────────────────────────
    "submission_steps": [
        "Provide firm unit pricing for all line items",
        "Confirm delivery area and lead times",
        "Attach COI, W-9, and any required licenses",
        "Email to <strong>bids.deedavisinc@gmail.com</strong> by the deadline above",
        "Subject: <strong>Quote — DDI-2026-XXX — [Product] — [Your Company Name]</strong>",
    ],

    # ── Terms ─────────────────────────────────────────────────────────────────
    "terms": [
        ("Payment Terms",    "Net 30 days from invoice date"),
        ("Delivery",         "FOB Destination — delivery charges itemized separately"),
        ("Quote Validity",   "Quote must remain valid for 60 days from submission"),
        ("Award",            "DDI reserves the right to split award, award by line item, or in whole"),
        ("Questions",        "Submit all questions to info@deedavis.biz by [DATE]"),
    ],

    # ── Supplier fill-in fields ───────────────────────────────────────────────
    "fill_in_fields": [
        "Company Legal Name",
        "Contact Name & Title",
        "Phone Number",
        "Email Address",
        "Earliest Available Start Date",
        "Payment Terms Offered",
        "Delivery Lead Time",
        "Quote Valid Through",
        "References Available? (Y/N)",
    ],

    # ── Mailto pre-filled email body template ─────────────────────────────────
    "mailto_body_lines": [
        "Dee Davis Inc. Procurement Team,",
        "",
        "Please find our quote response for RFQ DDI-2026-XXX attached.",
        "",
        "Company Name: ",
        "Contact Name: ",
        "Phone: ",
        "",
        "--- PRICING SUMMARY ---",
        "",
        "Item 1 — [Description]: $________ per [unit]",
        "",
        "Estimated Total: $________",
        "",
        "--- COMPLIANCE ---",
        "",
        "Earliest Start Date: ",
        "Quote Valid Through: ",
        "",
        "Attached:",
        "[ ] Certificate of Insurance",
        "[ ] W-9",
        "",
        "Thank you,",
        "",
        "[Your Name]",
        "[Company Name]",
        "[Phone]",
    ],
}

# ══════════════════════════════════════════════════════════════════════════════
#  ▶ ENGINE — Do not edit below this line
# ══════════════════════════════════════════════════════════════════════════════

NEXUS_ROOT = "/Users/deedavis/NEXUS BACKEND"

def load_logo() -> str:
    """Returns base64-encoded white DDI logo for dark backgrounds."""
    paths = [
        f"{NEXUS_ROOT}/BIDS:RESOURCES/ESSENTIALS/DEE-DAVIS-INC.-white-high-res.png",
        f"{NEXUS_ROOT}/BIDS:RESOURCES/MISCELLANEOUS/deedavisinclogo.png",
        f"{NEXUS_ROOT}/BIDS:RESOURCES/SOURCES SOUGHT NOTICEGENERAL BID/dee_davis_inc_logo.png",
        f"{NEXUS_ROOT}/dee_davis_logo.png",
    ]
    for p in paths:
        if os.path.exists(p):
            with open(p, "rb") as f:
                b64 = base64.b64encode(f.read()).decode()
            print(f"✓ Logo: {os.path.basename(p)}")
            return f'<img src="data:image/png;base64,{b64}" alt="Dee Davis Inc." class="logo-img">'
    return '<div class="logo-text">DEE DAVIS INC</div>'


def build_mailto(cfg: dict) -> str:
    """Build a pre-filled mailto: URL."""
    subj = f"Quote — {cfg['rfq_number']} — {cfg['rfq_title']} — [Your Company Name]"
    body = "\n".join(cfg["mailto_body_lines"])
    from urllib.parse import quote
    url = (
        f"mailto:{cfg['submit_to_email']}"
        f"?cc={cfg['submit_cc_email']}"
        f"&subject={quote(subj)}"
        f"&body={quote(body)}"
    )
    return url


def specs_html(spec_list: list) -> str:
    items = "".join(f"<li>{s}</li>" for s in spec_list)
    return f"<ul class='spec-list'>{items}</ul>"


def scope_list_html(items: list) -> str:
    return "<ul class='scope-list'>" + "".join(f"<li>{i}</li>" for i in items) + "</ul>"


def items_rows_html(items: list) -> str:
    rows = []
    for i, item in enumerate(items):
        shade = "row-shade" if i % 2 == 1 else ""
        rows.append(f"""
    <tr class="{shade}">
      <td class="col-no">{item['no']}</td>
      <td class="col-item">{item['item']}</td>
      <td class="col-specs">{specs_html(item['specs'])}</td>
      <td class="col-qty">{item['est_qty']}</td>
      <td class="col-freq">{item['freq']}</td>
      <td class="col-price">$________<br><span style='font-size:7pt;color:#9ca3af;'>{item.get('price_label','per unit')}</span></td>
      <td class="col-total">$________</td>
    </tr>""")
    return "\n".join(rows)


def fill_fields_html(fields: list) -> str:
    html = '<div class="fill-grid">'
    for f in fields:
        html += f"""
    <div class="fill-field">
      <div class="fill-label">{f}</div>
      <div class="fill-line">&nbsp;</div>
    </div>"""
    html += "</div>"
    return html


def submission_steps_html(steps: list) -> str:
    items = "".join(f"<li>{s}</li>" for s in steps)
    return f"<ol class='step-list'>{items}</ol>"


def terms_html(terms: list) -> str:
    items = "".join(
        f"<li><strong>{t[0]}:</strong> {t[1]}</li>" for t in terms
    )
    return f"<ul class='terms-list'>{items}</ul>"


def render(cfg: dict) -> str:
    logo = load_logo()
    mailto = build_mailto(cfg)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>{cfg['rfq_number']} — {cfg['rfq_title']} — Dee Davis Inc.</title>
<style>
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: 'Avenir Next','Avenir','Helvetica Neue',Arial,sans-serif; font-size: 9.5pt; color: #1f2937; background: #fff; }}

  /* HEADER */
  .header {{ background: #0f172a; color: #fff; padding: 22px 30px 18px; display: flex; align-items: center; justify-content: space-between; }}
  .logo-img {{ height: 58px; width: auto; object-fit: contain; }}
  .logo-text {{ font-size: 22pt; font-weight: 800; color: #fff; letter-spacing: -0.5px; }}
  .header-right {{ text-align: right; }}
  .rfq-badge {{ display: inline-block; background: #d97706; color: #fff; font-size: 7.5pt; font-weight: 700; letter-spacing: 1.2px; padding: 3px 10px; border-radius: 3px; margin-bottom: 4px; }}
  .rfq-title {{ font-size: 13pt; font-weight: 700; color: #fff; line-height: 1.2; }}
  .rfq-sub {{ font-size: 8.5pt; color: #94a3b8; margin-top: 3px; }}

  /* META STRIP */
  .meta-strip {{ display: flex; gap: 0; border-bottom: 3px solid #0f172a; }}
  .meta-cell {{ flex: 1; padding: 10px 14px; border-right: 1px solid #e5e7eb; }}
  .meta-cell:last-child {{ border-right: none; }}
  .meta-label {{ font-size: 7pt; font-weight: 700; color: #6b7280; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 3px; }}
  .meta-value {{ font-size: 9.5pt; font-weight: 700; color: #0f172a; }}
  .meta-deadline {{ color: #b91c1c; }}

  /* PROTECTION BANNER */
  .protection-banner {{ background: #fef3c7; border-left: 4px solid #d97706; padding: 9px 16px; font-size: 8pt; color: #78350f; }}
  .protection-banner strong {{ color: #92400e; }}

  /* SECTION HEADERS */
  .section-header {{ background: #0f172a; color: #fff; font-size: 8pt; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase; padding: 7px 14px; }}

  /* INTRO */
  .intro-block {{ padding: 12px 16px; border-bottom: 1px solid #e5e7eb; font-size: 9pt; line-height: 1.55; color: #374151; }}

  /* SCOPE */
  .scope-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 0; border-bottom: 1px solid #e5e7eb; }}
  .scope-col {{ padding: 12px 16px; }}
  .scope-col:first-child {{ border-right: 1px solid #e5e7eb; }}
  .scope-col-title {{ font-size: 8pt; font-weight: 700; color: #0f172a; margin-bottom: 7px; letter-spacing: 0.5px; text-transform: uppercase; }}
  .scope-list {{ list-style: none; }}
  .scope-list li {{ font-size: 8.5pt; color: #374151; padding: 3px 0 3px 16px; position: relative; line-height: 1.4; border-bottom: 1px solid #f3f4f6; }}
  .scope-list li:last-child {{ border-bottom: none; }}
  .scope-list li::before {{ content: "✓"; position: absolute; left: 0; color: #059669; font-weight: 700; font-size: 8pt; }}

  /* ITEMS TABLE */
  .table-wrap {{ overflow-x: auto; }}
  table.items-table {{ width: 100%; border-collapse: collapse; font-size: 8.5pt; }}
  table.items-table thead tr {{ background: #1e3a8a; color: #fff; }}
  table.items-table thead th {{ padding: 9px 8px; text-align: left; font-size: 7.5pt; font-weight: 700; letter-spacing: 0.8px; text-transform: uppercase; white-space: nowrap; }}
  table.items-table thead th.right {{ text-align: right; }}
  table.items-table tbody tr {{ border-bottom: 1px solid #e5e7eb; vertical-align: top; }}
  table.items-table tbody tr.row-shade {{ background: #f8fafc; }}
  table.items-table td {{ padding: 10px 8px; line-height: 1.4; }}
  .col-no {{ width: 3%; text-align: center; font-weight: 700; color: #0f172a; }}
  .col-item {{ width: 17%; font-weight: 600; color: #0f172a; font-size: 8.5pt; }}
  .col-specs {{ width: 38%; color: #374151; }}
  .col-qty {{ width: 10%; text-align: center; font-weight: 600; color: #1e3a8a; }}
  .col-freq {{ width: 10%; text-align: center; color: #6b7280; font-size: 8pt; }}
  .col-price {{ width: 11%; text-align: right; color: #6b7280; font-size: 8pt; }}
  .col-total {{ width: 11%; text-align: right; color: #6b7280; font-size: 8pt; font-style: italic; }}
  .item-sub {{ font-size: 7.5pt; color: #6b7280; font-weight: 400; }}
  .spec-list {{ list-style: none; margin: 0; padding: 0; }}
  .spec-list li {{ padding: 1.5px 0 1.5px 12px; position: relative; font-size: 8pt; color: #4b5563; line-height: 1.45; }}
  .spec-list li::before {{ content: "—"; position: absolute; left: 0; color: #9ca3af; font-size: 7.5pt; }}

  /* TWO-COL */
  .two-col {{ display: grid; grid-template-columns: 1fr 1fr; gap: 0; border-bottom: 1px solid #e5e7eb; }}
  .two-col-block {{ padding: 12px 16px; }}
  .two-col-block:first-child {{ border-right: 1px solid #e5e7eb; }}
  .block-title {{ font-size: 7.5pt; font-weight: 700; color: #0f172a; text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 8px; }}
  .step-list {{ list-style: none; counter-reset: steps; }}
  .step-list li {{ counter-increment: steps; padding: 3px 0 3px 24px; position: relative; font-size: 8pt; color: #374151; line-height: 1.4; border-bottom: 1px solid #f3f4f6; }}
  .step-list li:last-child {{ border-bottom: none; }}
  .step-list li::before {{ content: counter(steps); position: absolute; left: 0; width: 16px; height: 16px; background: #1e3a8a; color: #fff; border-radius: 50%; font-size: 7pt; font-weight: 700; text-align: center; line-height: 16px; top: 3px; }}
  .terms-list {{ list-style: none; }}
  .terms-list li {{ padding: 4px 0; font-size: 8pt; color: #374151; border-bottom: 1px solid #f3f4f6; line-height: 1.45; }}
  .terms-list li:last-child {{ border-bottom: none; }}
  .terms-list strong {{ color: #0f172a; }}

  /* FILL-IN */
  .fill-in-block {{ padding: 12px 16px; border-bottom: 1px solid #e5e7eb; }}
  .fill-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; }}
  .fill-field {{ border: 1px solid #d1d5db; border-radius: 4px; padding: 7px 10px; background: #f9fafb; }}
  .fill-label {{ font-size: 7pt; font-weight: 700; color: #6b7280; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 3px; }}
  .fill-line {{ border-bottom: 1px solid #9ca3af; min-height: 18px; }}

  /* SUBMIT BUTTON */
  .submit-block {{ background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%); padding: 22px 30px; display: flex; align-items: center; justify-content: space-between; gap: 20px; }}
  .submit-copy {{ color: #cbd5e1; font-size: 9pt; line-height: 1.5; }}
  .submit-copy strong {{ color: #fff; font-size: 10pt; display: block; margin-bottom: 3px; }}
  .submit-deadline {{ color: #fde68a; font-size: 8.5pt; font-weight: 700; margin-top: 5px; display: block; }}
  .submit-sub {{ font-size: 7.5pt; color: #94a3b8; margin-top: 8px; line-height: 1.4; }}
  .submit-btn {{ display: inline-block; background: #d97706; color: #fff !important; text-decoration: none; font-size: 10pt; font-weight: 700; padding: 13px 28px; border-radius: 6px; white-space: nowrap; letter-spacing: 0.3px; border: 2px solid #b45309; flex-shrink: 0; }}

  /* FOOTER */
  .footer {{ background: #0f172a; color: #94a3b8; padding: 12px 20px; display: flex; justify-content: space-between; align-items: center; font-size: 7.5pt; }}
  .footer strong {{ color: #fff; }}
  .footer-right {{ text-align: right; }}

  @media print {{ body, .header, .section-header, table.items-table thead tr, .footer, .submit-block {{ -webkit-print-color-adjust: exact; print-color-adjust: exact; }} }}
</style>
</head>
<body>

<div class="header">
  <div>{logo}</div>
  <div class="header-right">
    <div class="rfq-badge">REQUEST FOR QUOTE</div>
    <div class="rfq-title">{cfg['rfq_title']}</div>
    <div class="rfq-sub">{cfg['rfq_subtitle']}</div>
  </div>
</div>

<div class="meta-strip">
  <div class="meta-cell"><div class="meta-label">RFQ Number</div><div class="meta-value">{cfg['rfq_number']}</div></div>
  <div class="meta-cell"><div class="meta-label">Issue Date</div><div class="meta-value">{cfg['issue_date']}</div></div>
  <div class="meta-cell"><div class="meta-label">Quote Due</div><div class="meta-value meta-deadline">{cfg['due_date']}</div></div>
  <div class="meta-cell"><div class="meta-label">Due Time</div><div class="meta-value meta-deadline">{cfg['due_time']}</div></div>
  <div class="meta-cell"><div class="meta-label">Contract Type</div><div class="meta-value">{cfg['contract_period']}</div></div>
  <div class="meta-cell"><div class="meta-label">Send Quote To</div><div class="meta-value">{cfg['submit_to_email']}</div></div>
</div>

<div class="protection-banner">
  <strong>⚠ CONFIDENTIALITY NOTICE:</strong> The identity of the end client is confidential. Do NOT contact the end client directly.
  All coordination and payments are managed exclusively through Dee Davis Inc. Violation disqualifies your quote.
</div>

<div class="section-header">Introduction</div>
<div class="intro-block">{cfg['introduction']}</div>

<div class="section-header">Scope of Work &amp; Requirements</div>
<div class="scope-grid">
  <div class="scope-col">
    <div class="scope-col-title">Supplier Must Be Able To:</div>
    {scope_list_html(cfg['scope_supplier_must'])}
  </div>
  <div class="scope-col">
    <div class="scope-col-title">Compliance Requirements:</div>
    {scope_list_html(cfg['scope_compliance'])}
  </div>
</div>

<div class="section-header">Line Items — Pricing Request</div>
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
        <th class="col-total right">Est. Total</th>
      </tr>
    </thead>
    <tbody>
      {items_rows_html(cfg['items'])}
    </tbody>
    <tfoot>
      <tr style="background:#f0f9ff; border-top:2px solid #1e3a8a;">
        <td colspan="5" style="padding:8px; font-size:8pt; font-weight:700; color:#1e3a8a; text-align:right;">ESTIMATED TOTAL:</td>
        <td colspan="2" style="padding:8px; text-align:right; font-size:8.5pt; font-weight:700; color:#1e3a8a;">$________________</td>
      </tr>
    </tfoot>
  </table>
</div>

<div class="section-header">Submission Instructions &amp; Terms</div>
<div class="two-col">
  <div class="two-col-block">
    <div class="block-title">How to Submit Your Quote</div>
    {submission_steps_html(cfg['submission_steps'])}
  </div>
  <div class="two-col-block">
    <div class="block-title">Contract Terms</div>
    {terms_html(cfg['terms'])}
  </div>
</div>

<div class="section-header">Supplier Information (Complete &amp; Return with Quote)</div>
<div class="fill-in-block">
  {fill_fields_html(cfg['fill_in_fields'])}
</div>

<div class="submit-block">
  <div class="submit-copy">
    <strong>Ready to Submit Your Quote?</strong>
    Click the button — a pre-addressed email will open with the quote template pre-filled.
    Add your pricing, attach your COI, W-9, and any required licenses, and hit Send.
    <span class="submit-deadline">⏰ Deadline: {cfg['due_date']} @ {cfg['due_time']} — Late submissions will not be accepted.</span>
    <div class="submit-sub">
      Replace <em>[Your Company Name]</em> in the subject line before sending. Questions? Call 248.376.4550.
    </div>
  </div>
  <a class="submit-btn" href="{mailto}">📧 Submit Quote by Email</a>
</div>

<div class="footer">
  <div>
    <strong>Dee Davis Inc.</strong> | CAGE: 8UMX3 | UEI: HJB4KNYJVGZ1 | EDWOSB | WOSB | WBENC | MBE | SBE<br>
    755 W. Big Beaver Rd., Suite 2020, Troy, MI 48084 &nbsp;|&nbsp; 248.376.4550 &nbsp;|&nbsp; info@deedavis.biz &nbsp;|&nbsp; deedavis.biz
  </div>
  <div class="footer-right">
    RFQ: {cfg['rfq_number']}<br>
    Due: {cfg['due_date']} @ {cfg['due_time']}
  </div>
</div>

</body>
</html>"""


# ══════════════════════════════════════════════════════════════════════════════
#  ▶ MAIN — generates the HTML file
# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    rfq_num = re.sub(r"[^A-Za-z0-9\-]", "", CONFIG["rfq_number"])
    out_dir = os.path.dirname(os.path.abspath(__file__))
    out_file = os.path.join(out_dir, f"{rfq_num}_RFQ.html")

    html = render(CONFIG)
    with open(out_file, "w") as f:
        f.write(html)

    print(f"")
    print(f"╔══════════════════════════════════════════════════════╗")
    print(f"║  ✓ RFQ GENERATED: {rfq_num}_RFQ.html")
    print(f"╠══════════════════════════════════════════════════════╣")
    print(f"║  TO CREATE PDF:                                      ║")
    print(f"║  1. Open the HTML file in Chrome                     ║")
    print(f"║  2. Cmd+P → More settings                           ║")
    print(f"║  3. Margins: None                                    ║")
    print(f"║  4. ✓ Background graphics: ON                        ║")
    print(f"║  5. Layout: Portrait                                 ║")
    print(f"║  6. Save as PDF → place in SEND_TO_SUPPLIER/         ║")
    print(f"╚══════════════════════════════════════════════════════╝")
    print(f"")
