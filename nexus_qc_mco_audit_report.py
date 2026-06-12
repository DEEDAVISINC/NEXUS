#!/usr/bin/env python3
"""Print-ready MCO QC Master Breakdown — matches Member Trip Grade Report design."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from company_info import BRAND_NAME, COMPANY_NAME
from member_trip_grade_audit_report import _esc, _fmt_dt, _page_shell
from nexus_qc_engine import PILLAR_DEFINITIONS, build_mco_breakdown_data

_QC_EXTRA_CSS = """
  .pillar-ok { color: #059669; font-weight: 800; }
  .pillar-warn { color: #d97706; font-weight: 800; }
  .pillar-bad { color: #dc2626; font-weight: 800; }
  .export-link { font-size: 11px; word-break: break-all; color: #6b21a8; font-weight: 600; }
"""


def _pillar_row(pid: int, summary: Dict[str, int], meta: Dict[str, Any]) -> str:
    s = summary.get(str(pid), {})
    total = sum(s.values()) or 1
    pass_n = s.get("pass", 0)
    pct = round(100 * pass_n / total, 1)
    if pct >= 95:
        st_class = "pillar-ok"
    elif pct >= 80:
        st_class = "pillar-warn"
    else:
        st_class = "pillar-bad"
    criteria = meta.get("pass_criteria") or ""
    if len(criteria) > 100:
        criteria = criteria[:97] + "…"
    return (
        f"<tr><td><strong>P{pid}</strong></td>"
        f"<td>{_esc(meta['name'])}</td>"
        f"<td>{_esc(meta['module'])}</td>"
        f'<td class="{st_class}">{pass_n}/{total} pass ({pct}%)</td>'
        f"<td>{_esc(criteria)}</td></tr>"
    )


def _request_rows(items: List[Dict[str, Any]], payer: str) -> str:
    rows = []
    for item in items:
        export = (item.get("export") or "").replace("{payer}", payer or "").replace("{contract_id}", "")
        rows.append(
            f"<tr><td>{_esc(item.get('request'))}</td>"
            f"<td><span class=\"pill\" style=\"background:#f3e8ff;color:#6b21a8\">P{item.get('pillar')}</span></td>"
            f"<td><span class=\"export-link\">{_esc(export)}</span></td>"
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
        gate_cls = "status-completed" if gate == "released" else "status-pending"
        rows.append(
            f"<tr><td>{_esc(rec.get('qc_id'))}</td>"
            f'<td><a href="{trip_link}" style="color:#6b21a8;font-weight:700">{_esc(nemt)}</a></td>'
            f"<td>{_esc(p.get('1', {}).get('status'))}</td>"
            f"<td>{_esc(p6)}</td>"
            f"<td>{_esc(p7)}</td>"
            f'<td><span class="status-pill {gate_cls}">{_esc(gate)}</span></td></tr>'
        )
    return rows or '<tr><td colspan="6" style="text-align:center;padding:24px;color:#94a3b8">No QC records yet.</td></tr>'


def _read_callout() -> str:
    return (
        '<div class="callout"><strong>How to read this report.</strong> '
        "Nine universal quality pillars cover authorization, credentialing, execution, documentation, "
        "inspection, member experience, billing integrity, regulatory compliance, and audit readiness. "
        "Each row in the MCO Request Index maps a typical plan audit question to the pillar, export path, and SLA. "
        "Use <strong>Save as PDF / Print</strong> for desk reviews and on-site audits.</div>"
    )


def _program_overview(payer: str, contract: Dict[str, Any]) -> str:
    return f"""<div class="section-title">Program overview</div>
<div class="prog-block"><h3>{_esc(BRAND_NAME)} — MCO quality control program</h3>
<ul>
<li><strong>Prime / TPA:</strong> {_esc(COMPANY_NAME)} — nationwide contract management TPA (EDWOSB).</li>
<li><strong>Health plan / payer:</strong> {_esc(payer or "All enrolled payers")}</li>
<li><strong>Contract ID:</strong> {_esc(contract.get('contract_id', '—'))} · Vendor ID: {_esc(contract.get('vendor_id', '—'))}</li>
<li><strong>QC spine:</strong> PRISM execution proof · VERTEX billing gate · COMPASS contract deliverables.</li>
<li><strong>Audit SLA:</strong> Full packet response ≤ 2 business days · immutable per-trip archive in PRISM.</li>
</ul></div>"""


def render_mco_breakdown_html(
    *,
    payer: Optional[str] = None,
    contract_id: Optional[str] = None,
) -> str:
    data = build_mco_breakdown_data(payer=payer, contract_id=contract_id)
    payer_disp = data.get("payer") or "All payers"
    contract = data.get("contract") or {}
    gen = _fmt_dt(data.get("generated_at"))

    pillar_rows = "".join(
        _pillar_row(pid, data["pillar_summary"], meta)
        for pid, meta in sorted(PILLAR_DEFINITIONS.items())
    )

    stats = f"""<div class="stat-grid">
    <div class="stat-card"><div class="stat-label">Trips in QC register</div>
    <div class="stat-value">{data.get('delivery_count', 0)}</div>
    <div class="stat-hint">Per-trip pillar tracking</div></div>
    <div class="stat-card"><div class="stat-label">Open grievances</div>
    <div class="stat-value">{data.get('grievances_open', 0)}</div>
    <div class="stat-hint">Pillar 6 — member experience</div></div>
    <div class="stat-card"><div class="stat-label">Universal pillars</div>
    <div class="stat-value">9</div>
    <div class="stat-hint">System-wide framework</div></div>
    <div class="stat-card"><div class="stat-label">Audit response</div>
    <div class="stat-value">≤2d</div>
    <div class="stat-hint">Business days SLA</div></div></div>"""

    body = f"""<style>{_QC_EXTRA_CSS}</style>
    {_read_callout()}
    {_program_overview(payer_disp, contract)}
    {stats}
    <div class="section-title">Nine universal pillars — status summary</div>
    <table class="data-table"><thead><tr>
    <th>#</th><th>Pillar</th><th>System</th><th>Delivery status</th><th>Pass criteria</th>
    </tr></thead><tbody>{pillar_rows}</tbody></table>
    <div class="section-title">MCO request index — what you ask for → where we deliver it</div>
    <p style="font-size:13px;color:#64748b;margin-bottom:12px;line-height:1.55">
    Use this index for desk reviews, on-site audits, and ad-hoc plan requests. Each row maps a typical audit question to pillar, export URL, and SLA.</p>
    <table class="data-table"><thead><tr>
    <th>Typical MCO / plan request</th><th>Pillar</th><th>Export / artifact</th><th>SLA</th>
    </tr></thead><tbody>{_request_rows(data.get('mco_request_index', []), payer or '')}</tbody></table>
    <div class="section-title">Related audit packets</div>
    <div class="detail-grid">
    <div class="detail-item"><div class="detail-key">Member Trip Grade Report</div>
    <div class="detail-val"><span class="export-link">{_esc(data.get('exports', {}).get('member_trip_grade_packet'))}</span></div></div>
    <div class="detail-item"><div class="detail-key">This master breakdown</div>
    <div class="detail-val"><span class="export-link">{_esc(data.get('exports', {}).get('qc_master_breakdown'))}</span></div></div>
    <div class="detail-item detail-full"><div class="detail-key">Grievance log (API)</div>
    <div class="detail-val"><span class="export-link">{_esc(data.get('exports', {}).get('grievance_log'))}</span></div></div>
    </div>
    <div class="section-title">Trip QC register</div>
    <table class="data-table"><thead><tr>
    <th>QC ID</th><th>NEMT order</th><th>Auth (P1)</th><th>Member (P6)</th><th>Billing (P7)</th><th>Gate</th>
    </tr></thead><tbody>{_trip_register_rows(data.get('records', []))}</tbody></table>"""

    meta = (
        f"<span><strong>Payer</strong> {_esc(payer_disp)}</span>"
        f"<span><strong>Report generated</strong> {gen}</span>"
        f"<span><strong>TPA</strong> {_esc(BRAND_NAME)}</span>"
        f"<span><strong>Vendor ID</strong> {_esc(contract.get('vendor_id', '—'))}</span>"
    )

    html_doc = _page_shell(
        f"MCO QC Master Breakdown — {payer_disp}",
        "MCO Quality Control · Nine-Pillar Framework",
        "MCO QC Master Breakdown",
        "Program summary, pillar status, MCO request index, and trip QC register for managed care quality review.",
        meta,
        body,
        footer_tagline="MCO QC Master Breakdown",
    )
    return html_doc
