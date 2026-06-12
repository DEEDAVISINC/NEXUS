#!/usr/bin/env python3
"""Print-ready MCO QC Master Breakdown — all 9 pillars + request index + trip register."""

from __future__ import annotations

import html
import os
from typing import Any, Dict, List, Optional

from nexus_qc_engine import PILLAR_DEFINITIONS, build_mco_breakdown_data

_BASE = os.path.dirname(os.path.abspath(__file__))
_LOGO_PATH = os.path.join(_BASE, "assets", "ddi_logo_base64.txt")


def _esc(val: Any) -> str:
    return html.escape(str(val) if val is not None else "—")


def _load_logo_data_uri() -> str:
    try:
        if os.path.isfile(_LOGO_PATH):
            with open(_LOGO_PATH, "r", encoding="utf-8") as f:
                b64 = f.read().strip()
            if b64:
                return f"data:image/png;base64,{b64}"
    except OSError:
        pass
    return ""


def _pillar_row(pid: int, summary: Dict[str, int], meta: Dict[str, Any]) -> str:
    s = summary.get(str(pid), {})
    total = sum(s.values()) or 1
    pass_n = s.get("pass", 0)
    pct = round(100 * pass_n / total, 1)
    st_class = "ok" if pct >= 95 else ("warn" if pct >= 80 else "bad")
    return f"""<tr>
  <td><strong>P{pid}</strong></td>
  <td>{_esc(meta['name'])}</td>
  <td>{_esc(meta['module'])}</td>
  <td class="{st_class}">{pass_n}/{total} pass ({pct}%)</td>
  <td>{_esc(meta['pass_criteria'][:120])}…</td>
</tr>"""


def _request_rows(items: List[Dict[str, Any]], payer: str) -> str:
    rows = []
    for item in items:
        export = (item.get("export") or "").replace("{payer}", payer or "").replace("{contract_id}", "")
        rows.append(
            f"<tr><td>{_esc(item.get('request'))}</td>"
            f"<td>P{item.get('pillar')}</td>"
            f"<td><code>{_esc(export)}</code></td>"
            f"<td>{_esc(item.get('sla'))}</td></tr>"
        )
    return "\n".join(rows)


def _trip_register_rows(records: List[Dict[str, Any]], limit: int = 100) -> str:
    rows = []
    for rec in records[:limit]:
        p = rec.get("pillars", {})
        p6 = p.get("6", {}).get("status", "pending")
        p7 = p.get("7", {}).get("status", "pending")
        gate = rec.get("gate_billing", {}).get("status", "—")
        nemt = rec.get("nemt_order_id") or "—"
        trip_link = f"/prism/nemt/satisfaction/trip/{nemt}.html" if nemt != "—" else "—"
        rows.append(
            f"<tr><td>{_esc(rec.get('qc_id'))}</td>"
            f"<td><a href=\"{trip_link}\">{_esc(nemt)}</a></td>"
            f"<td>{_esc(p.get('1', {}).get('status'))}</td>"
            f"<td>{_esc(p6)}</td>"
            f"<td>{_esc(p7)}</td>"
            f"<td>{_esc(gate)}</td></tr>"
        )
    return "\n".join(rows) or "<tr><td colspan=\"6\">No QC records yet.</td></tr>"


def render_mco_breakdown_html(
    *,
    payer: Optional[str] = None,
    contract_id: Optional[str] = None,
) -> str:
    data = build_mco_breakdown_data(payer=payer, contract_id=contract_id)
    payer_disp = data.get("payer") or "All payers"
    contract = data.get("contract") or {}
    logo = _load_logo_data_uri()
    logo_html = f'<img src="{logo}" alt="DDI" class="logo" />' if logo else "<div class=\"logo-text\">DEE DAVIS INC</div>"

    pillar_rows = "".join(
        _pillar_row(pid, data["pillar_summary"], meta)
        for pid, meta in sorted(PILLAR_DEFINITIONS.items())
    )

    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"/>
<title>MCO QC Master Breakdown — {_esc(payer_disp)}</title>
<style>
  @page {{ margin: 0.6in; }}
  body {{ font-family: Georgia, 'Times New Roman', serif; color: #1e293b; margin: 0; padding: 24px; line-height: 1.45; }}
  .page {{ max-width: 900px; margin: 0 auto; }}
  header {{ display: flex; align-items: center; gap: 20px; border-bottom: 3px solid #6b21a8; padding-bottom: 16px; margin-bottom: 24px; }}
  .logo {{ height: 56px; }}
  .logo-text {{ font-weight: 700; font-size: 1.1rem; color: #6b21a8; }}
  h1 {{ font-size: 1.35rem; margin: 0; color: #6b21a8; }}
  .sub {{ color: #64748b; font-size: 0.9rem; margin-top: 4px; }}
  h2 {{ font-size: 1.05rem; color: #475569; border-bottom: 1px solid #e2e8f0; padding-bottom: 6px; margin-top: 28px; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 0.82rem; margin: 12px 0; }}
  th, td {{ border: 1px solid #cbd5e1; padding: 8px 10px; text-align: left; vertical-align: top; }}
  th {{ background: #f1f5f9; font-weight: 600; }}
  .ok {{ color: #166534; font-weight: 600; }}
  .warn {{ color: #b45309; font-weight: 600; }}
  .bad {{ color: #b91c1c; font-weight: 600; }}
  .box {{ background: #faf5ff; border: 1px solid #e9d5ff; border-radius: 8px; padding: 14px 18px; margin: 16px 0; }}
  .metrics {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; }}
  .metric {{ background: #fff; border: 1px solid #e2e8f0; border-radius: 6px; padding: 12px; text-align: center; }}
  .metric .n {{ font-size: 1.4rem; font-weight: 700; color: #6b21a8; }}
  .metric .l {{ font-size: 0.75rem; color: #64748b; text-transform: uppercase; }}
  footer {{ margin-top: 32px; font-size: 0.75rem; color: #94a3b8; border-top: 1px solid #e2e8f0; padding-top: 12px; }}
  code {{ font-size: 0.78rem; word-break: break-all; }}
  @media print {{ body {{ padding: 0; }} }}
</style></head>
<body><div class="page">
<header>{logo_html}
  <div><h1>MCO Quality Control — Master Breakdown</h1>
  <div class="sub">Nine-pillar framework · Nationwide contract management TPA · Prepared for {_esc(payer_disp)}</div>
  <div class="sub">Generated {_esc(data.get('generated_at'))}</div></div>
</header>

<div class="box">
<strong>Program:</strong> Dee Davis Inc. (DDI) — EDWOSB prime / NEMT contract management TPA.<br/>
<strong>Plan / payer:</strong> {_esc(payer_disp)}<br/>
<strong>Contract ID:</strong> {_esc(contract.get('contract_id', '—'))} · Vendor ID: {_esc(contract.get('vendor_id', '—'))}<br/>
<strong>Audit standard:</strong> Every unit of service has compliance check, proof record, billing match, and export path (≤ 2 business days).
</div>

<div class="metrics">
  <div class="metric"><div class="n">{data.get('delivery_count', 0)}</div><div class="l">Trips in QC register</div></div>
  <div class="metric"><div class="n">{data.get('grievances_open', 0)}</div><div class="l">Open grievances</div></div>
  <div class="metric"><div class="n">9</div><div class="l">Universal pillars</div></div>
  <div class="metric"><div class="n">≤2d</div><div class="l">Audit response SLA</div></div>
</div>

<h2>1. Nine Universal Pillars — Status Summary</h2>
<table>
<thead><tr><th>#</th><th>Pillar</th><th>System</th><th>Delivery status</th><th>Pass criteria</th></tr></thead>
<tbody>{pillar_rows}</tbody>
</table>

<h2>2. MCO Request Index — What You Ask For → Where We Deliver It</h2>
<p>Use this index for desk reviews, on-site audits, and ad-hoc requests. Each row maps a typical plan question to pillar, export URL, and SLA.</p>
<table>
<thead><tr><th>Typical MCO / plan request</th><th>Pillar</th><th>Export / artifact</th><th>SLA</th></tr></thead>
<tbody>{_request_rows(data.get('mco_request_index', []), payer or '')}</tbody>
</table>

<h2>3. Related audit packets</h2>
<ul>
<li><strong>Member Trip Grade Report:</strong> <code>{_esc(data.get('exports', {}).get('member_trip_grade_packet'))}</code></li>
<li><strong>This master breakdown:</strong> <code>{_esc(data.get('exports', {}).get('qc_master_breakdown'))}</code></li>
<li><strong>Grievance log (API):</strong> <code>{_esc(data.get('exports', {}).get('grievance_log'))}</code></li>
</ul>

<h2>4. Trip QC Register (sample)</h2>
<table>
<thead><tr><th>QC ID</th><th>NEMT order</th><th>Auth (P1)</th><th>Member (P6)</th><th>Billing (P7)</th><th>Gate</th></tr></thead>
<tbody>{_trip_register_rows(data.get('records', []))}</tbody>
</table>

<footer>
Confidential — MCO quality audit · Dee Davis Inc. · 248.376.4550 · info@deedavis.biz · Troy, MI 48084<br/>
Print: Save as PDF from browser. Immutable per-trip records retained in PRISM audit archive.
</footer>
</div></body></html>"""
