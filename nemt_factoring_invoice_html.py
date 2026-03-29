"""
NEMT factoring-compliant invoice HTML — universal factoring standards (HTML → PDF via NEXUS pipeline).
"""

from __future__ import annotations

import html as html_module
from typing import Any, Dict


def _esc(s: Any) -> str:
    return html_module.escape("" if s is None else str(s))


def generate_nemt_factoring_invoice_html(ctx: Dict[str, Any]) -> str:
    """
    ctx keys:
      invoice_number, invoice_date_display, due_date_display, payment_terms (Net 30)
      vendor_name, vendor_address, ein, cage, npi
      payer_legal_name, payer_address (multiline plain text)
      service_date_display, member_id, trip_origin, trip_destination
      hcpcs_code, service_type_label
      unit_quantity, unit_rate, total_amount (float)
      assignment_language, certification_language
      signer_name, signer_title
    """
    inv = ctx["invoice_number"]
    total = float(ctx["total_amount"])
    total_fmt = f"${total:,.2f}"
    rate_fmt = f"${float(ctx['unit_rate']):,.2f}"

    payer_name = _esc(ctx["payer_legal_name"])
    payer_addr = _esc(ctx.get("payer_address") or "").replace("\n", "<br>\n")

    vaddr = _esc(ctx["vendor_address"]).replace("\n", "<br>\n")

    detail_lines = [
        f"<strong>Service date(s):</strong> {_esc(ctx.get('service_date_display'))}",
        f"<strong>Member ID:</strong> {_esc(ctx.get('member_id'))}",
        f"<strong>Trip origin:</strong> {_esc(ctx.get('trip_origin'))}",
        f"<strong>Trip destination:</strong> {_esc(ctx.get('trip_destination'))}",
        f"<strong>HCPCS:</strong> {_esc(ctx.get('hcpcs_code'))}",
        f"<strong>Service type:</strong> {_esc(ctx.get('service_type_label'))}",
    ]
    detail_html = "<br>".join(detail_lines)

    assignment = _esc(ctx.get("assignment_language"))
    cert = _esc(ctx.get("certification_language"))
    signer = _esc(ctx.get("signer_name"))
    title = _esc(ctx.get("signer_title"))

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Invoice { _esc(inv) } — {_esc(ctx['vendor_name'])}</title>
<style>
  @page {{ size: letter; margin: 0.55in; }}
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; font-size: 10.5pt; color: #111827; line-height: 1.45; }}
  .top {{ display: flex; justify-content: space-between; align-items: flex-start; border-bottom: 3px solid #1e3a5f; padding-bottom: 14px; margin-bottom: 16px; }}
  .brand {{ font-size: 16pt; font-weight: 800; color: #1e3a5f; }}
  .meta {{ text-align: right; font-size: 9pt; }}
  .meta strong {{ font-size: 11pt; display: block; margin-bottom: 4px; }}
  .row2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 24px; margin-bottom: 18px; }}
  .box-title {{ font-size: 8pt; text-transform: uppercase; letter-spacing: 0.08em; color: #6b7280; margin-bottom: 6px; font-weight: 700; }}
  .vendor-id {{ font-size: 9pt; margin-top: 8px; color: #374151; }}
  .bill-to strong {{ font-size: 11pt; display: block; margin-bottom: 4px; }}
  .service-block {{ border: 1px solid #e5e7eb; border-radius: 6px; padding: 12px 14px; margin-bottom: 16px; background: #f9fafb; }}
  .service-block .detail {{ font-size: 9.5pt; }}
  table.inv {{ width: 100%; border-collapse: collapse; margin-bottom: 14px; }}
  table.inv th {{ background: #1e3a5f; color: #fff; text-align: left; padding: 10px 12px; font-size: 8pt; text-transform: uppercase; letter-spacing: 0.06em; }}
  table.inv td {{ padding: 10px 12px; border-bottom: 1px solid #e5e7eb; vertical-align: top; }}
  table.inv td.num {{ text-align: right; font-variant-numeric: tabular-nums; }}
  .total-due-wrap {{ text-align: right; margin: 18px 0 22px; }}
  .total-due-label {{ font-size: 9pt; color: #6b7280; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 4px; }}
  .total-due-amount {{ font-size: 28pt; font-weight: 800; color: #0f172a; letter-spacing: -0.02em; }}
  .remit {{ background: #eff6ff; border-left: 4px solid #2563eb; padding: 12px 14px; margin-bottom: 14px; font-size: 10pt; }}
  .legal {{ font-size: 9pt; color: #374151; border: 1px solid #d1d5db; padding: 12px 14px; margin-bottom: 12px; line-height: 1.5; }}
  .cert {{ margin-top: 18px; font-size: 9.5pt; }}
  .sig {{ margin-top: 36px; border-top: 1px solid #9ca3af; padding-top: 8px; max-width: 320px; }}
  .sig .name {{ font-weight: 700; }}
  @media print {{ body {{ -webkit-print-color-adjust: exact; print-color-adjust: exact; }} }}
</style>
</head>
<body>

<div class="top">
  <div>
    <div class="brand">{_esc(ctx['vendor_name'])}</div>
    <div class="vendor-id">
      {vaddr}<br>
      <strong>EIN:</strong> {_esc(ctx['ein'])} &nbsp;|&nbsp; <strong>CAGE:</strong> {_esc(ctx['cage'])} &nbsp;|&nbsp; <strong>NPI:</strong> {_esc(ctx['npi'])}
    </div>
  </div>
  <div class="meta">
    <strong>INVOICE</strong>
    <div>Invoice # {_esc(inv)}</div>
    <div>Invoice date: {_esc(ctx['invoice_date_display'])}</div>
    <div>Due date: {_esc(ctx['due_date_display'])}</div>
    <div>Payment terms: {_esc(ctx.get('payment_terms', 'Net 30'))}</div>
  </div>
</div>

<div class="row2">
  <div>
    <div class="box-title">Remit / Legal payee</div>
    <div>{_esc(ctx['vendor_name'])}<br>{vaddr}</div>
  </div>
  <div>
    <div class="box-title">Bill to (payer)</div>
    <div class="bill-to"><strong>{payer_name}</strong><br>{payer_addr if payer_addr else '<em>— Address: add payer in VERTEX CLIENTS —</em>'}</div>
  </div>
</div>

<div class="service-block">
  <div class="box-title" style="margin-bottom:8px;">Detailed service description</div>
  <div class="detail">{detail_html}</div>
</div>

<table class="inv">
  <thead>
    <tr>
      <th style="width:52%">Description</th>
      <th style="width:12%">Qty (trips)</th>
      <th style="width:18%">Unit rate</th>
      <th style="width:18%">Line total</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Non-emergency medical transportation (NEMT) — {_esc(ctx.get('service_type_label'))} — HCPCS {_esc(ctx.get('hcpcs_code'))}</td>
      <td class="num">{_esc(ctx.get('unit_quantity', 1))}</td>
      <td class="num">{rate_fmt}</td>
      <td class="num">{total_fmt}</td>
    </tr>
  </tbody>
</table>

<div class="total-due-wrap">
  <div class="total-due-label">Total amount due</div>
  <div class="total-due-amount">{total_fmt}</div>
</div>

<div class="remit">
  <strong>Remittance instructions:</strong> Make payment payable to <strong>{_esc(ctx['vendor_name'])}</strong> and remit using the address shown under “Remit / Legal payee” unless you have received a written notice of assignment to a third-party factor (see below).
</div>

<div class="legal">
  <strong>Assignment of benefits / factoring notice.</strong> {assignment}
</div>

<div class="legal">
  <strong>Certification.</strong> {cert}
</div>

<div class="cert">
  <div class="sig">
    <div class="name">{signer}</div>
    <div>{title}</div>
    <div style="margin-top:8px;font-size:8pt;color:#6b7280;">Authorized signature</div>
  </div>
</div>

</body>
</html>"""
