"""
RFQ Generator — v1 Engine
Produces supplier RFQ documents matching the Dry Ice reference format:
  Header → Meta Strip → Confidentiality Banner → Introduction →
  Scope (Requirements + Compliance) → Line Items Table →
  Submission Instructions & Terms → Supplier Info Form → Submit CTA → Footer

SUPPLIER PROTECTION: No buyer names, no solicitation numbers, no specific
addresses, no procurement officer names. DDI-YYYY-### format only.
"""

import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import quote as urlquote

from capability_statement_generator import _get_logo_base64


DEFAULT_COMPLIANCE = [
    "General Liability Insurance &mdash; minimum $1M per occurrence",
    "Commercial Auto Insurance &mdash; minimum $1M per occurrence",
    "W-9 on file (required prior to first payment)",
    "COI with Dee Davis Inc. listed as Additional Insured",
    "Must NOT contact end client directly &mdash; all coordination through DDI",
]

DEFAULT_SUPPLIER_FIELDS = [
    "Company Legal Name",
    "Contact Name &amp; Title",
    "Phone Number",
    "Email Address",
    "Earliest Available Start Date",
    "Payment Terms Offered",
    "Delivery Lead Time",
    "Quote Valid Through",
    "References Available? (Y/N)",
]

DEFAULT_CONTRACT_TERMS = [
    {"label": "Payment Terms", "value": "Net 30 days from invoice date"},
    {"label": "Delivery", "value": "FOB Destination &mdash; delivery charges itemized separately"},
    {"label": "Pricing", "value": "Firm for base year. Price adjustments require 30-day written notice"},
    {"label": "Quote Validity", "value": "Quote must remain valid for 60 days from submission"},
    {"label": "Award", "value": "DDI reserves the right to split award, award by line item, or in whole"},
]

BANNED_TERMS = [
    "canton", "genesee", "rcoc", "oakland county", "wayne county",
    "flint", "detroit", "troy", "livonia", "sterling heights", "warren",
    "madison heights", "macomb", "rock island", "cps energy",
]


# ═══════════════════════════════════════════════════════════════════════════════
# HTML BUILDERS
# ═══════════════════════════════════════════════════════════════════════════════

def build_scope_list_html(items: List[str]) -> str:
    return "\n      ".join(f"<li>{item}</li>" for item in items)


def build_line_items_html(items: List[Dict]) -> str:
    rows = []
    for i, item in enumerate(items):
        shade = ' class="row-shade"' if i % 2 == 1 else ""
        specs = item.get("specs", [])
        if isinstance(specs, list) and specs:
            specs_html = "<ul class='spec-list'>" + "".join(f"<li>{s}</li>" for s in specs) + "</ul>"
        elif isinstance(specs, str):
            specs_html = specs
        else:
            specs_html = "&mdash;"

        sub = item.get("sub", "")
        sub_html = f"<br><span class='item-sub'>{sub}</span>" if sub else ""

        price_unit = item.get("price_unit", "per unit")

        rows.append(
            f'    <tr{shade}>\n'
            f'      <td class="col-no">{i + 1}</td>\n'
            f'      <td class="col-item">{item["name"]}{sub_html}</td>\n'
            f'      <td class="col-specs">{specs_html}</td>\n'
            f'      <td class="col-qty">{item.get("qty", "TBD")}</td>\n'
            f'      <td class="col-freq">{item.get("freq", "Per order")}</td>\n'
            f'      <td class="col-price">$________<br><span style="font-size:7pt;color:#9ca3af;">{price_unit}</span></td>\n'
            f'      <td class="col-total">$________</td>\n'
            f'    </tr>'
        )
    return "\n".join(rows)


def build_total_row_html(label: str) -> str:
    if not label:
        return ""
    return (
        f'    <tr class="total-row">\n'
        f'      <td colspan="5"></td>\n'
        f'      <td style="text-align:right;font-size:8pt;font-weight:700;padding-right:8px;">{label}:</td>\n'
        f'      <td style="text-align:right;font-weight:700;">$________________</td>\n'
        f'    </tr>'
    )


def build_submission_steps_html(
    rfq_number: str,
    product_short: str,
    due_date: str,
    questions_deadline: Optional[str] = None,
    extra_attachments: Optional[List[str]] = None,
) -> str:
    attachments = "COI, W-9"
    if extra_attachments:
        attachments += ", and " + ", ".join(extra_attachments)

    steps = [
        "Provide firm unit pricing for all line items",
        "Confirm delivery area and lead times",
        f"Attach {attachments}",
        f"Email to <strong>info@deedavis.biz</strong> by {due_date}",
        f"Subject: <strong>Quote &mdash; {rfq_number} &mdash; {product_short} &mdash; [Your Company Name]</strong>",
    ]
    return "\n      ".join(f"<li>{s}</li>" for s in steps)


def build_contract_terms_html(
    terms: Optional[List[Dict]] = None,
    questions_deadline: Optional[str] = None,
) -> str:
    t = terms or DEFAULT_CONTRACT_TERMS
    items = [f"<li><strong>{term['label']}:</strong> {term['value']}</li>" for term in t]
    if questions_deadline:
        items.append(f"<li><strong>Questions:</strong> Submit all questions to info@deedavis.biz by {questions_deadline}</li>")
    return "\n      ".join(items)


def build_supplier_fields_html(fields: Optional[List[str]] = None) -> str:
    f_list = fields or DEFAULT_SUPPLIER_FIELDS
    parts = []
    for label in f_list:
        parts.append(
            f'    <div class="fill-field">\n'
            f'      <div class="fill-label">{label}</div>\n'
            f'      <div class="fill-line">&nbsp;</div>\n'
            f'    </div>'
        )
    return "\n".join(parts)


def build_mailto_link(
    rfq_number: str,
    product_short: str,
    items: List[Dict],
) -> str:
    subject = f"Quote — {rfq_number} — {product_short} — [Your Company Name]"

    body_lines = [
        "Dee Davis Inc. Procurement Team,",
        "",
        f"Please find our quote response for RFQ {rfq_number} attached.",
        "",
        "Company Name: ",
        "Contact Name: ",
        "Phone: ",
        "",
        "--- PRICING SUMMARY ---",
        "",
    ]
    for i, item in enumerate(items):
        body_lines.append(f"Item {i + 1} — {item['name']}: $________ per {item.get('price_unit', 'unit')}")
    body_lines += [
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
    ]

    body = "\n".join(body_lines)
    return f"mailto:info@deedavis.biz?subject={urlquote(subject)}&body={urlquote(body)}"


# ═══════════════════════════════════════════════════════════════════════════════
# SUPPLIER PROTECTION SCAN
# ═══════════════════════════════════════════════════════════════════════════════

def protection_scan(html: str) -> List[str]:
    cleaned = re.sub(r'data:image/[^"]+', '', html)
    cleaned = re.sub(r'Troy,?\s*MI[\s\d]*', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'755 W\.?\s*Big Beaver[^<]*', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'Dee Davis Inc\.?', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'CAGE:\s*8UMX3', '', cleaned, flags=re.IGNORECASE)

    violations = []
    lower = cleaned.lower()
    for term in BANNED_TERMS:
        if term in lower:
            violations.append(f"BANNED TERM FOUND: '{term}'")
    sol_patterns = [
        r'\b\d{2}[A-Z]\d{3,}[A-Z]\d+\b',
        r'\bRFQ\s*#?\s*\d{5,}',
        r'\bRFP[\s-]\d{3,}',
        r'\bITB[\s-]\d{3,}',
        r'\bW\d{5,}[A-Z]',
    ]
    for pat in sol_patterns:
        if re.search(pat, cleaned):
            violations.append(f"POSSIBLE SOLICITATION NUMBER: pattern '{pat}'")
    return violations


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN GENERATOR
# ═══════════════════════════════════════════════════════════════════════════════

def generate_rfq(
    rfq_number: str,
    title: str,
    location: str,
    client_type: str = "Government Client",
    issue_date: Optional[str] = None,
    due_date: str = "TBD",
    due_time: str = "12:00 PM EST",
    contract_type: str = "One-time order",
    introduction: str = "",
    scope_requirements: Optional[List[str]] = None,
    compliance_requirements: Optional[List[str]] = None,
    line_items: Optional[List[Dict]] = None,
    total_label: Optional[str] = None,
    contract_terms: Optional[List[Dict]] = None,
    questions_deadline: Optional[str] = None,
    supplier_fields: Optional[List[str]] = None,
    extra_attachments: Optional[List[str]] = None,
    output_path: Optional[str] = None,
) -> str:
    template_path = Path(__file__).parent / "rfq_template.html"
    template = template_path.read_text()
    logo_b64 = _get_logo_base64()

    if not issue_date:
        issue_date = datetime.now().strftime("%B %d, %Y")

    if not introduction:
        introduction = (
            f"Dee Davis Inc. (CAGE: 8UMX3 | EDWOSB Certified | Troy, MI) is the prime contractor "
            f"managing this procurement on behalf of a {client_type.lower()} in {location}. "
            f"We are soliciting competitive pricing from qualified suppliers."
        )

    product_short = title.split("—")[0].strip() if "—" in title else title

    items = line_items or []

    replacements = {
        "{{LOGO_BASE64}}": logo_b64,
        "{{RFQ_NUMBER}}": rfq_number,
        "{{RFQ_TITLE}}": title,
        "{{RFQ_LOCATION}}": location,
        "{{RFQ_CLIENT_TYPE}}": client_type,
        "{{ISSUE_DATE}}": issue_date,
        "{{DUE_DATE}}": due_date,
        "{{DUE_TIME}}": due_time,
        "{{CONTRACT_TYPE}}": contract_type,
        "{{INTRODUCTION_HTML}}": introduction,
        "{{SCOPE_REQUIREMENTS_HTML}}": build_scope_list_html(scope_requirements or []),
        "{{COMPLIANCE_REQUIREMENTS_HTML}}": build_scope_list_html(compliance_requirements or DEFAULT_COMPLIANCE),
        "{{LINE_ITEMS_HTML}}": build_line_items_html(items),
        "{{TOTAL_ROW_HTML}}": build_total_row_html(total_label or ""),
        "{{SUBMISSION_STEPS_HTML}}": build_submission_steps_html(
            rfq_number, product_short, due_date, questions_deadline, extra_attachments
        ),
        "{{CONTRACT_TERMS_HTML}}": build_contract_terms_html(contract_terms, questions_deadline),
        "{{SUPPLIER_FIELDS_HTML}}": build_supplier_fields_html(supplier_fields),
        "{{MAILTO_LINK}}": build_mailto_link(rfq_number, product_short, items),
    }

    html = template
    for placeholder, value in replacements.items():
        html = html.replace(placeholder, value)

    violations = protection_scan(html)
    if violations:
        print("⚠️  SUPPLIER PROTECTION VIOLATIONS:")
        for v in violations:
            print(f"   {v}")
        print("   FIX THESE before sending to suppliers.")

    if output_path:
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(html)

    return html
