"""
Beautiful, print-ready HTML audit reports for member trip grades (MCO packets).
"""

from __future__ import annotations

import html
import os
from datetime import datetime
from functools import lru_cache
from typing import Any, Dict, List, Optional
from zoneinfo import ZoneInfo

from company_info import (
    ADDRESS_FULL,
    BRAND_NAME,
    COMPANY_NAME,
    EMAIL,
    PHONE_MEMBER_CARE_DISPLAY,
    PHONE_PRIMARY,
    WEBSITE,
)

EASTERN = ZoneInfo("America/Detroit")

GRADE_COLORS = {
    "A": ("#059669", "#ecfdf5", "Excellent"),
    "B": ("#2563eb", "#eff6ff", "Good"),
    "C": ("#d97706", "#fffbeb", "Fair"),
    "D": ("#ea580c", "#fff7ed", "Poor"),
    "F": ("#dc2626", "#fef2f2", "Unacceptable"),
}

_BASE_CSS = """
  @page { margin: 0.6in; }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: system-ui, -apple-system, 'Segoe UI', sans-serif; background: #f1f5f9; color: #0f172a; line-height: 1.5; }
  .page { max-width: 920px; margin: 0 auto; background: #fff; box-shadow: 0 8px 32px rgba(15,23,42,.08); }
  @media print { body { background: #fff; } .page { box-shadow: none; max-width: 100%; } .no-print { display: none !important; } }
  .hero { background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 55%, #6b21a8 100%); color: #fff; padding: 32px 40px 28px; }
  .hero-top { display: flex; align-items: flex-start; gap: 20px; }
  .hero-brand { display: flex; align-items: flex-start; gap: 18px; flex: 1; min-width: 0; }
  .hero-logo { width: 76px; height: 76px; flex-shrink: 0; background: rgba(255,255,255,.97); border-radius: 14px; padding: 10px; box-shadow: 0 6px 20px rgba(0,0,0,.18); }
  .hero-logo img { width: 100%; height: 100%; object-fit: contain; display: block; }
  .hero-text { flex: 1; min-width: 0; }
  .hero-kicker { font-size: 11px; font-weight: 800; letter-spacing: .12em; text-transform: uppercase; color: #c4b5fd; margin-bottom: 8px; }
  .hero h1 { font-size: 26px; font-weight: 800; margin-bottom: 6px; }
  .hero-sub { font-size: 14px; color: rgba(255,255,255,.82); max-width: 620px; line-height: 1.55; }
  .hero-meta { display: flex; flex-wrap: wrap; gap: 16px 28px; margin-top: 20px; font-size: 12px; color: rgba(255,255,255,.75); }
  .hero-meta strong { color: #fde68a; font-weight: 700; }
  .body { padding: 32px 40px 40px; }
  .section-title { font-size: 11px; font-weight: 800; letter-spacing: .1em; text-transform: uppercase; color: #64748b; margin: 28px 0 12px; padding-bottom: 8px; border-bottom: 2px solid #e2e8f0; }
  .section-title:first-child { margin-top: 0; }
  .stat-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 12px; }
  .stat-card { border: 1px solid #e2e8f0; border-radius: 12px; padding: 16px 14px; background: #f8fafc; }
  .stat-label { font-size: 10px; font-weight: 700; text-transform: uppercase; color: #64748b; }
  .stat-value { font-size: 28px; font-weight: 800; margin-top: 4px; }
  .stat-hint { font-size: 11px; color: #94a3b8; margin-top: 4px; }
  .grade-row { display: flex; flex-wrap: wrap; gap: 12px; margin: 8px 0 4px; }
  .grade-badge { display: flex; flex-direction: column; align-items: center; min-width: 88px; padding: 14px 12px; border-radius: 14px; border: 2px solid; }
  .grade-letter { font-size: 32px; font-weight: 900; line-height: 1; }
  .grade-label { font-size: 9px; font-weight: 700; text-transform: uppercase; margin-top: 6px; }
  .grade-cat { font-size: 11px; font-weight: 700; color: #475569; text-align: center; margin-top: 6px; max-width: 100px; }
  .detail-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px 24px; }
  @media (max-width: 640px) { .detail-grid { grid-template-columns: 1fr; } .hero, .body { padding-left: 20px; padding-right: 20px; } }
  .detail-item { padding: 10px 0; border-bottom: 1px solid #f1f5f9; }
  .detail-key { font-size: 10px; font-weight: 700; text-transform: uppercase; color: #94a3b8; margin-bottom: 3px; }
  .detail-val { font-size: 14px; font-weight: 600; color: #1e293b; word-break: break-word; }
  .detail-full { grid-column: 1 / -1; }
  .comment-box { background: #f8fafc; border: 1px solid #e2e8f0; border-left: 4px solid #6b21a8; border-radius: 10px; padding: 16px 18px; font-size: 14px; color: #334155; font-style: italic; }
  .comment-empty { color: #94a3b8; font-style: normal; }
  .timeline { list-style: none; margin: 8px 0; }
  .timeline li { display: flex; gap: 12px; padding: 10px 0; border-bottom: 1px solid #f1f5f9; font-size: 13px; }
  .timeline-dot { width: 10px; height: 10px; border-radius: 50%; margin-top: 5px; flex-shrink: 0; background: #6b21a8; }
  .timeline-dot.pending { background: #cbd5e1; }
  .timeline-dot.done { background: #059669; }
  table.data-table { width: 100%; border-collapse: collapse; font-size: 12px; margin-top: 8px; }
  table.data-table th { text-align: left; font-size: 10px; font-weight: 800; text-transform: uppercase; color: #64748b; padding: 10px 8px; border-bottom: 2px solid #e2e8f0; background: #f8fafc; }
  table.data-table td { padding: 12px 8px; border-bottom: 1px solid #f1f5f9; }
  .pill { display: inline-block; font-size: 10px; font-weight: 800; padding: 3px 8px; border-radius: 999px; }
  .dist-row { display: flex; align-items: center; gap: 10px; margin: 6px 0; font-size: 12px; }
  .dist-label { width: 20px; font-weight: 800; text-align: center; }
  .dist-track { flex: 1; height: 10px; background: #e2e8f0; border-radius: 999px; overflow: hidden; }
  .dist-fill { height: 100%; border-radius: 999px; }
  .dist-pct { width: 42px; text-align: right; color: #64748b; font-weight: 600; }
  .footer { padding: 20px 40px 28px; border-top: 1px solid #e2e8f0; background: #f8fafc; font-size: 11px; color: #64748b; line-height: 1.6; }
  .footer-brand { display: flex; align-items: center; gap: 12px; margin-bottom: 10px; }
  .footer-logo { width: 40px; height: 40px; flex-shrink: 0; }
  .footer-logo img { width: 100%; height: 100%; object-fit: contain; display: block; }
  .footer strong { color: #334155; }
  @media print { .hero-logo { background: #fff; box-shadow: none; } }
  .print-btn { display: inline-block; margin: 16px 40px 0; padding: 10px 18px; background: #6b21a8; color: #fff; border: none; border-radius: 8px; font-size: 13px; font-weight: 700; cursor: pointer; }
  .overall-banner { display: flex; align-items: center; gap: 20px; padding: 20px 22px; background: linear-gradient(90deg, #faf5ff, #f8fafc); border: 1px solid #e9d5ff; border-radius: 14px; margin-bottom: 8px; }
  .overall-title { font-size: 15px; font-weight: 800; }
  .overall-sub { font-size: 13px; color: #64748b; margin-top: 4px; }
  .callout { background: #eff6ff; border: 1px solid #bfdbfe; border-left: 4px solid #2563eb; border-radius: 12px; padding: 14px 16px; font-size: 13px; color: #1e40af; margin: 16px 0 4px; line-height: 1.55; }
  .callout strong { font-weight: 800; }
  .legend { display: flex; flex-wrap: wrap; gap: 8px; margin: 10px 0 4px; }
  .legend-item { display: flex; align-items: center; gap: 6px; font-size: 11px; font-weight: 600; color: #475569; padding: 6px 10px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 999px; }
  .legend-dot { width: 12px; height: 12px; border-radius: 50%; flex-shrink: 0; }
  table.data-table tbody tr:nth-child(even) { background: #fafafa; }
  table.data-table tbody tr:hover { background: #f1f5f9; }
  .status-pill { display: inline-block; font-size: 10px; font-weight: 800; letter-spacing: .04em; text-transform: uppercase; padding: 4px 10px; border-radius: 999px; }
  .status-completed { background: #dcfce7; color: #166534; }
  .status-pending { background: #fef3c7; color: #92400e; }
  .channel-tag { font-size: 11px; font-weight: 700; color: #6b21a8; background: #f3e8ff; padding: 2px 8px; border-radius: 6px; }
  .trip-card { border: 1px solid #e2e8f0; border-radius: 14px; margin: 16px 0 0; overflow: hidden; page-break-inside: avoid; }
  .trip-card-head { display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 10px; padding: 14px 18px; background: #f8fafc; border-bottom: 1px solid #e2e8f0; }
  .trip-card-title { font-size: 14px; font-weight: 800; color: #0f172a; }
  .trip-card-sub { font-size: 11px; color: #64748b; margin-top: 3px; }
  .trip-card-body { padding: 16px 18px 18px; }
  .mini-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px 16px; font-size: 12px; }
  @media (max-width: 720px) { .mini-grid { grid-template-columns: 1fr 1fr; } }
  .mini-k { font-size: 9px; font-weight: 700; text-transform: uppercase; color: #94a3b8; }
  .mini-v { font-weight: 600; color: #1e293b; margin-top: 2px; word-break: break-word; }
  .prog-block { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 16px 18px; margin-bottom: 4px; font-size: 13px; color: #334155; line-height: 1.6; }
  .prog-block h3 { font-size: 13px; font-weight: 800; color: #0f172a; margin-bottom: 8px; }
  .prog-block ul { margin: 8px 0 0 18px; }
  .prog-block li { margin: 4px 0; }
  table.data-table td.addr { max-width: 140px; font-size: 11px; line-height: 1.35; }
  table.data-table td.comment { max-width: 120px; font-size: 11px; font-style: italic; color: #475569; }
  .score-line { font-size: 12px; color: #475569; margin-top: 6px; }
  .score-line strong { color: #0f172a; }
"""


_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
_LOGO_ASSET = os.path.join(_BASE_DIR, "assets", "ddi_logo_base64.txt")


@lru_cache(maxsize=1)
def _get_ddi_logo_data_uri() -> str:
    """Embedded DDI logo for print-ready reports (no external image dependency)."""
    try:
        with open(_LOGO_ASSET, "r", encoding="utf-8") as f:
            data = f.read().strip()
            if data.startswith("data:image"):
                return data
    except OSError:
        pass
    try:
        from capability_statement_generator import _get_logo_base64

        return _get_logo_base64() or ""
    except Exception:
        return ""


def _logo_img(alt: str, css_class: str) -> str:
    uri = _get_ddi_logo_data_uri()
    if not uri:
        return ""
    return f'<img class="{css_class}" src="{uri}" alt="{html.escape(alt)}">'


def _esc(val: Any) -> str:
    return html.escape(str(val if val not in (None, "") else "—"))


def _fmt_dt(raw: Optional[str]) -> str:
    if not raw:
        return "—"
    try:
        dt = datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=EASTERN)
        else:
            dt = dt.astimezone(EASTERN)
        return dt.strftime("%b %d, %Y · %I:%M %p ET")
    except Exception:
        return _esc(raw)


def _grade_badge(letter: Optional[str], category: str = "") -> str:
    g = (letter or "").upper()
    if g not in GRADE_COLORS:
        return f'<div class="grade-cat">{_esc(category)}</div><div class="detail-val">Pending</div>'
    fg, bg, lbl = GRADE_COLORS[g]
    cat = f'<div class="grade-cat">{_esc(category)}</div>' if category else ""
    return (
        f'<div>{cat}<div class="grade-badge" style="border-color:{fg};background:{bg};color:{fg}">'
        f'<div class="grade-letter">{g}</div><div class="grade-label">{lbl}</div></div></div>'
    )


def _grade_legend() -> str:
    items = "".join(
        f'<div class="legend-item"><span class="legend-dot" style="background:{GRADE_COLORS[g][0]}"></span>'
        f'<span><strong>{g}</strong> — {GRADE_COLORS[g][2]}</span></div>'
        for g in "ABCDF"
    )
    return f'<div class="section-title">Grade scale (A–F)</div><div class="legend">{items}</div>'


def _read_callout() -> str:
    return (
        '<div class="callout"><strong>How to read this report.</strong> '
        "Each completed medical mobility trip receives an A–F member grade (DDI service, driver, trip) "
        f"via SMS from {_esc(PHONE_MEMBER_CARE_DISPLAY)} or the member portal. "
        "This packet includes program summary, grade distribution, full trip register, and per-trip audit detail. "
        "Use <strong>Save as PDF / Print</strong> for MCO quality review.</div>"
    )


def _program_overview(payer: str) -> str:
    pl = payer or "All enrolled payers"
    return f"""<div class="section-title">Program overview</div>
<div class="prog-block"><h3>{_esc(BRAND_NAME)} member trip grade program</h3>
<ul>
<li><strong>Prime / TPA:</strong> {_esc(COMPANY_NAME)} — nationwide contract management; fulfillment dispatched per trip.</li>
<li><strong>Health plan / payer:</strong> {_esc(pl)}</li>
<li><strong>Member contact:</strong> SMS grade requests from {_esc(PHONE_MEMBER_CARE_DISPLAY)} (member care). No phone-call surveys.</li>
<li><strong>Grade scale:</strong> A (Excellent) through F (Unacceptable) on DDI overall, driver, and trip experience.</li>
<li><strong>Portal gate:</strong> Members must grade pending trips before scheduling new rides in the portal.</li>
<li><strong>Audit storage:</strong> PRISM — immutable JSON + HTML per trip; this report aggregates for quality packets.</li>
</ul></div>"""


def _methodology_block() -> str:
    return """<div class="section-title">Survey methodology</div>
<div class="prog-block"><h3>Collection &amp; timing</h3>
<ul>
<li>Grade SMS sent ~60 minutes after trip drop-off (configurable).</li>
<li>One reminder SMS at 24 hours if no grade submitted.</li>
<li>Portal modal backup if member logs in before grading.</li>
<li>Composite grade = average of DDI, driver, and trip letter scores mapped to A–F.</li>
<li>Member comments stored verbatim; members asked not to include PHI in free text.</li>
</ul></div>"""


def _score_line(rec: Dict[str, Any]) -> str:
    parts = []
    for label, gkey, nkey in (
        ("DDI", "ddi_grade", "ddi_rating"),
        ("Driver", "driver_grade", "driver_rating"),
        ("Trip", "trip_grade", "trip_rating"),
    ):
        g = rec.get(gkey) or "—"
        n = rec.get(nkey)
        parts.append(f"<strong>{label}:</strong> {g}" + (f" ({n}/5)" if n is not None else ""))
    comp = rec.get("overall_average")
    comp_s = f" · <strong>Composite:</strong> {comp}/5" if comp is not None else ""
    return f'<div class="score-line">{"".join(f"{p} · " for p in parts[:-1])}{parts[-1]}{comp_s}</div>'


def _compliance_grid(rec: Dict[str, Any], snap: Dict[str, Any]) -> str:
    return f"""<div class="section-title">Compliance &amp; authorization</div><div class="detail-grid">
    {_detail_item('Eligibility verified', snap.get('eligibility_verified'))}
    {_detail_item('Prior authorization', snap.get('prior_auth_number'))}
    {_detail_item('HCPCS / transport code', snap.get('hcpcs_code'))}
    {_detail_item('Medicaid ID (masked)', snap.get('member_medicaid_id_masked'))}
    {_detail_item('Member DOB', snap.get('member_dob'))}
    {_detail_item('NEMT status at queue', snap.get('nemt_status_at_grade_queue'))}
    {_detail_item('Fulfillment platform', snap.get('fulfillment_platform'))}
    {_detail_item('VERTEX invoice', snap.get('vertex_invoice_id'))}</div>"""


def _member_contact_grid(rec: Dict[str, Any]) -> str:
    return f"""<div class="section-title">Member contact (masked)</div><div class="detail-grid">
    {_detail_item('Member name', rec.get('member_name'))}
    {_detail_item('Member phone', rec.get('member_phone_masked') or '—')}
    {_detail_item('Member email', _mask_email(rec.get('member_email')))}
    {_detail_item('Portal-only survey', 'Yes' if rec.get('portal_only') else 'No')}</div>"""


def _mask_email(raw: Any) -> str:
    s = str(raw or "").strip()
    if not s or "@" not in s:
        return "—"
    local, domain = s.split("@", 1)
    if len(local) <= 2:
        masked_local = "*" * len(local)
    else:
        masked_local = local[0] + ("*" * (len(local) - 2)) + local[-1]
    return f"{masked_local}@{domain}"


def _dist_block(title: str, dist: Dict[str, Optional[float]]) -> str:
    rows = "".join(
        f'<div class="dist-row"><div class="dist-label" style="color:{GRADE_COLORS[g][0]}">{g}</div>'
        f'<div class="dist-track"><div class="dist-fill" style="width:{min(dist.get(g) or 0, 100)}%;background:{GRADE_COLORS[g][0]}"></div></div>'
        f'<div class="dist-pct">{dist.get(g) if dist.get(g) is not None else 0}%</div></div>'
        for g in "ABCDF"
    )
    return f'<div class="section-title">{_esc(title)}</div>{rows}'


def _grade_distribution(records: List[Dict[str, Any]], field: str) -> Dict[str, Optional[float]]:
    grades = [str(r.get(field) or "").upper() for r in records if r.get(field)]
    if not grades:
        return {g: None for g in "ABCDF"}
    total = len(grades)
    return {g: round(sum(1 for x in grades if x == g) / total * 100, 1) for g in "ABCDF"}


def _render_trip_card(rec: Dict[str, Any], index: int) -> str:
    snap = rec.get("trip_snapshot") or {}
    og = str(rec.get("overall_grade") or "—").upper()
    fg, bg, _ = GRADE_COLORS.get(og, ("#64748b", "#f1f5f9"))
    channel = rec.get("response_channel") or "—"
    comment = (rec.get("comments") or "").strip() or "No comment provided."
    return f"""<article class="trip-card">
    <div class="trip-card-head">
      <div><div class="trip-card-title">Trip #{index} · {_esc(rec.get('trip_ref'))}</div>
      <div class="trip-card-sub">{_esc(rec.get('member_name'))} · {_esc(rec.get('trip_purpose'))} · Graded {_fmt_dt(rec.get('responded_at'))}</div></div>
      <span class="pill" style="background:{bg};color:{fg};font-size:12px;padding:6px 12px">Overall {_esc(og)}</span>
    </div>
    <div class="trip-card-body">
      {_score_line(rec)}
      <div class="mini-grid" style="margin-top:14px">
        <div><div class="mini-k">Transport</div><div class="mini-v">{_esc(snap.get('transport_label') or snap.get('transport_type'))}</div></div>
        <div><div class="mini-k">Driver</div><div class="mini-v">{_esc(rec.get('driver_name'))}</div></div>
        <div><div class="mini-k">Vehicle</div><div class="mini-v">{_esc(snap.get('vehicle_id'))}</div></div>
        <div><div class="mini-k">Scheduled pickup</div><div class="mini-v">{_esc(snap.get('pickup_time'))}</div></div>
        <div><div class="mini-k">Actual pickup</div><div class="mini-v">{_esc(snap.get('actual_pickup_time'))}</div></div>
        <div><div class="mini-k">Actual drop-off</div><div class="mini-v">{_esc(snap.get('actual_dropoff_time'))}</div></div>
        <div><div class="mini-k">Appointment</div><div class="mini-v">{_esc(snap.get('appointment_time'))}</div></div>
        <div><div class="mini-k">Mileage</div><div class="mini-v">{_esc(snap.get('actual_mileage'))}</div></div>
        <div><div class="mini-k">Channel</div><div class="mini-v">{_esc(channel)}</div></div>
        <div><div class="mini-k">NEMT order</div><div class="mini-v">{_esc(rec.get('nemt_order_id'))}</div></div>
        <div><div class="mini-k">PRISM order</div><div class="mini-v">{_esc(rec.get('prism_order_id'))}</div></div>
        <div><div class="mini-k">VERTEX trip</div><div class="mini-v">{_esc(rec.get('vertex_trip_id'))}</div></div>
      </div>
      <div class="detail-grid" style="margin-top:12px">
        {_detail_item('Pickup address', snap.get('pickup_address'), True)}
        {_detail_item('Drop-off address', snap.get('dropoff_address'), True)}
        {_detail_item('Trip completed', _fmt_dt(rec.get('completed_at')))}
        {_detail_item('Grade SMS sent', _fmt_dt(rec.get('sent_at')))}
        {_detail_item('Reminder SMS', _fmt_dt(rec.get('reminder_sent_at')))}
        {_detail_item('Prior auth', snap.get('prior_auth_number'))}
        {_detail_item('Eligibility verified', snap.get('eligibility_verified'))}
        {_detail_item('Member comment', comment, True)}
      </div>
    </div></article>"""


def _detail_item(key: str, val: Any, full: bool = False) -> str:
    cls = "detail-item detail-full" if full else "detail-item"
    return f'<div class="{cls}"><div class="detail-key">{_esc(key)}</div><div class="detail-val">{val if isinstance(val, str) and val.startswith("<") else _esc(val)}</div></div>'


def _page_shell(
    title: str,
    kicker: str,
    h1: str,
    sub: str,
    meta: str,
    body: str,
    *,
    footer_tagline: str = "Member Trip Grade Report",
) -> str:
    gen = datetime.now(EASTERN).strftime("%B %d, %Y · %I:%M %p ET")
    logo_hero = _logo_img(BRAND_NAME, "hero-logo-img")
    logo_footer = _logo_img(BRAND_NAME, "footer-logo-img")
    hero_logo_block = f'<div class="hero-logo">{logo_hero}</div>' if logo_hero else ""
    footer_logo_block = f'<div class="footer-logo">{logo_footer}</div>' if logo_footer else ""
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{_esc(title)}</title><style>{_BASE_CSS}
  .hero-logo-img, .footer-logo-img {{ width: 100%; height: 100%; object-fit: contain; display: block; }}
</style></head><body>
<button class="print-btn no-print" onclick="window.print()">Save as PDF / Print</button>
<div class="page"><header class="hero"><div class="hero-top"><div class="hero-brand">{hero_logo_block}
<div class="hero-text"><div class="hero-kicker">{kicker}</div>
<h1>{h1}</h1><p class="hero-sub">{sub}</p></div></div></div>
<div class="hero-meta">{meta}</div></header>
<main class="body">{body}</main>
<footer class="footer"><div class="footer-brand">{footer_logo_block}<div><strong>{_esc(COMPANY_NAME)}</strong> · {_esc(BRAND_NAME)} · {_esc(footer_tagline)}</div></div>
{_esc(ADDRESS_FULL)} · Member care {_esc(PHONE_MEMBER_CARE_DISPLAY)} · Desk {_esc(PHONE_PRIMARY)} · {_esc(EMAIL)} · {_esc(WEBSITE)}<br>
Generated {_esc(gen)} · Confidential — MCO / quality audit</footer></div></body></html>"""


def render_trip_detail_html(rec: Dict[str, Any]) -> str:
    snap = rec.get("trip_snapshot") or {}
    og = rec.get("overall_grade") or "—"
    _, _, olbl = GRADE_COLORS.get(str(og).upper(), ("#64748b", "#f1f5f9", "Pending"))
    status = (rec.get("status") or "pending").lower()
    status_cls = "status-completed" if status == "completed" else "status-pending"
    channel = rec.get("response_channel") or "—"
    channel_html = f'<span class="channel-tag">{_esc(channel)}</span>' if channel != "—" else "—"
    body = f"""
    {_read_callout()}
    <div class="overall-banner">{_grade_badge(og, "Overall")}
    <div><div class="overall-title">Member Trip Grade Report</div>
    <div class="overall-sub">Composite {_esc(olbl)} · Average {_esc(rec.get('overall_average', '—'))} / 5.0
    · <span class="status-pill {status_cls}">{_esc(status)}</span></div>
    {_score_line(rec)}</div></div>
    <div class="grade-row">{_grade_badge(rec.get('ddi_grade'), 'DDI overall')}
    {_grade_badge(rec.get('driver_grade'), 'Driver')}{_grade_badge(rec.get('trip_grade'), 'Trip')}</div>
    {_grade_legend()}
    {_member_contact_grid(rec)}
    <div class="section-title">Trip details</div><div class="detail-grid">
    {_detail_item('Payer', rec.get('payer'))}
    {_detail_item('Trip purpose', rec.get('trip_purpose'))}
    {_detail_item('Transport type', snap.get('transport_label') or snap.get('transport_type'))}
    {_detail_item('Scheduled pickup', snap.get('pickup_time'))}
    {_detail_item('Appointment time', snap.get('appointment_time'))}
    {_detail_item('Actual pickup', snap.get('actual_pickup_time'))}
    {_detail_item('Actual drop-off', snap.get('actual_dropoff_time'))}
    {_detail_item('Mileage', snap.get('actual_mileage'))}
    {_detail_item('Driver', rec.get('driver_name'))}
    {_detail_item('Vehicle ID', snap.get('vehicle_id'))}
    {_detail_item('Pickup address', snap.get('pickup_address'), True)}
    {_detail_item('Drop-off address', snap.get('dropoff_address'), True)}</div>
    {_compliance_grid(rec, snap)}
    <div class="section-title">Reference IDs</div><div class="detail-grid">
    {_detail_item('Trip ref', rec.get('trip_ref'))}
    {_detail_item('NEMT order', rec.get('nemt_order_id'))}
    {_detail_item('PRISM order', rec.get('prism_order_id'))}
    {_detail_item('VERTEX trip', rec.get('vertex_trip_id'))}
    {_detail_item('Survey token', rec.get('token'))}
    {_detail_item('Response channel', channel_html)}
    {_detail_item('Audit JSON path', rec.get('audit_archive_path'), True)}
    {_detail_item('Audit HTML path', rec.get('audit_html_path'), True)}</div>
    <div class="section-title">Survey &amp; SMS timeline</div><ul class="timeline">
    <li><span class="timeline-dot done"></span><span><strong>Trip completed</strong><br>{_fmt_dt(rec.get('completed_at'))}</span></li>
    <li><span class="timeline-dot {'done' if rec.get('created_at') else 'pending'}"></span><span><strong>Grade queued</strong><br>{_fmt_dt(rec.get('created_at'))}</span></li>
    <li><span class="timeline-dot {'done' if rec.get('sent_at') else 'pending'}"></span><span><strong>Grade SMS sent</strong><br>{_fmt_dt(rec.get('sent_at'))}</span></li>
    <li><span class="timeline-dot {'done' if rec.get('reminder_sent_at') else 'pending'}"></span><span><strong>Reminder SMS</strong><br>{_fmt_dt(rec.get('reminder_sent_at'))}</span></li>
    <li><span class="timeline-dot {'done' if rec.get('responded_at') else 'pending'}"></span><span><strong>Grade submitted</strong><br>{_fmt_dt(rec.get('responded_at'))}</span></li></ul>
    <div class="section-title">Member comment</div>
    <div class="comment-box {'comment-empty' if not (rec.get('comments') or '').strip() else ''}">{
        _esc(rec.get('comments')) if (rec.get('comments') or '').strip() else 'No comment provided.'}</div>"""
    meta = (
        f"<span><strong>Payer</strong> {_esc(rec.get('payer'))}</span>"
        f"<span><strong>Ref</strong> {_esc(rec.get('trip_ref'))}</span>"
        f"<span><strong>Member</strong> {_esc(rec.get('member_name'))}</span>"
    )
    return _page_shell(
        "Member Trip Grade Report",
        "Member Trip Grade Report · single trip",
        "Member Trip Grade Report",
        f"Detailed audit record for one {_esc(BRAND_NAME)} medical mobility trip.",
        meta,
        body,
    )


def render_mco_packet_html(payer: str, records: List[Dict[str, Any]], summary: Dict[str, Any]) -> str:
    totals = summary.get("totals") or {}
    avgs = summary.get("averages_numeric_1_to_5") or {}
    dist = summary.get("overall_grade_distribution_pct") or {}
    completed = [r for r in records if r.get("status") == "completed"]
    pending_list = [r for r in records if (r.get("status") or "").lower() not in ("completed",)]
    reminded = sum(1 for r in records if r.get("reminder_sent_at"))
    portal_only = sum(1 for r in records if r.get("portal_only"))

    stats = f"""{_read_callout()}
    {_program_overview(payer)}
    {_methodology_block()}
    <div class="section-title">Executive summary</div>
    <div class="stat-grid">
    <div class="stat-card"><div class="stat-label">Trips queued</div><div class="stat-value">{totals.get('surveys_queued', len(records))}</div></div>
    <div class="stat-card"><div class="stat-label">Trips graded</div><div class="stat-value">{totals.get('grades_completed', len(completed))}</div>
    <div class="stat-hint">{totals.get('awaiting_grade', len(pending_list))} awaiting grade</div></div>
    <div class="stat-card"><div class="stat-label">Grade SMS sent</div><div class="stat-value">{totals.get('sms_sent', 0)}</div>
    <div class="stat-hint">{reminded} reminders · {portal_only} portal-only</div></div>
    <div class="stat-card"><div class="stat-label">Response rate</div><div class="stat-value">{totals.get('response_rate_pct', 0)}%</div>
    <div class="stat-hint">Member care {_esc(PHONE_MEMBER_CARE_DISPLAY)}</div></div>
    <div class="stat-card"><div class="stat-label">Composite avg</div><div class="stat-value">{avgs.get('composite') or '—'}</div>
    <div class="stat-hint">Scale 1.0 – 5.0</div></div>
    <div class="stat-card"><div class="stat-label">DDI avg</div><div class="stat-value">{avgs.get('ddi_overall') or '—'}</div></div>
    <div class="stat-card"><div class="stat-label">Driver avg</div><div class="stat-value">{avgs.get('driver_experience') or '—'}</div></div>
    <div class="stat-card"><div class="stat-label">Trip avg</div><div class="stat-value">{avgs.get('trip_travel_experience') or '—'}</div></div></div>"""

    dist_html = _dist_block("Overall grade distribution", dist)
    dist_html += _dist_block("DDI grade distribution", _grade_distribution(completed, "ddi_grade"))
    dist_html += _dist_block("Driver grade distribution", _grade_distribution(completed, "driver_grade"))
    dist_html += _dist_block("Trip grade distribution", _grade_distribution(completed, "trip_grade"))

    rows = ""
    for r in sorted(completed, key=lambda x: x.get("responded_at") or "", reverse=True):
        og = str(r.get("overall_grade") or "—").upper()
        fg, bg, _ = GRADE_COLORS.get(og, ("#64748b", "#f1f5f9"))
        snap = r.get("trip_snapshot") or {}
        comment = (r.get("comments") or "").strip()
        if len(comment) > 60:
            comment = comment[:57] + "..."
        rows += f"<tr><td>{_fmt_dt(r.get('responded_at'))}</td><td>{_esc(r.get('member_name'))}</td>"
        rows += f"<td>{_esc(r.get('trip_purpose'))}</td>"
        rows += f'<td><span class="pill" style="background:{bg};color:{fg}">{_esc(og)}</span></td>'
        rows += f"<td>{_esc(r.get('ddi_grade'))}/{_esc(r.get('driver_grade'))}/{_esc(r.get('trip_grade'))}</td>"
        rows += f"<td>{_esc(snap.get('transport_label'))}</td>"
        rows += f"<td>{_esc(r.get('driver_name'))}</td>"
        rows += f"<td>{_esc(snap.get('actual_mileage'))}</td>"
        rows += f'<td class="addr">{_esc(snap.get("pickup_address"))}</td>'
        rows += f'<td class="addr">{_esc(snap.get("dropoff_address"))}</td>'
        rows += f"<td>{_esc(r.get('response_channel'))}</td>"
        rows += f'<td class="comment">{_esc(comment) if comment else "—"}</td>'
        rows += f"<td>{_esc(r.get('trip_ref'))}</td></tr>"

    table = f"""<div class="section-title">Trip register — all graded trips ({len(completed)})</div>
    <table class="data-table"><thead><tr>
    <th>Graded</th><th>Member</th><th>Purpose</th><th>Overall</th><th>DDI/Drv/Trip</th><th>Transport</th>
    <th>Driver</th><th>Miles</th><th>Pickup</th><th>Drop-off</th><th>Channel</th><th>Comment</th><th>Ref</th>
    </tr></thead>
    <tbody>{rows or '<tr><td colspan="13" style="text-align:center;padding:24px;color:#94a3b8">No grades yet — trips will appear here after members submit A–F scores.</td></tr>'}</tbody></table>"""

    pending_rows = ""
    for r in sorted(pending_list, key=lambda x: x.get("completed_at") or "", reverse=True)[:50]:
        snap = r.get("trip_snapshot") or {}
        pending_rows += f"<tr><td>{_fmt_dt(r.get('completed_at'))}</td><td>{_esc(r.get('member_name'))}</td>"
        pending_rows += f"<td>{_esc(r.get('trip_purpose'))}</td><td>{_esc(r.get('status'))}</td>"
        pending_rows += f"<td>{_fmt_dt(r.get('sent_at'))}</td><td>{_esc(r.get('trip_ref'))}</td></tr>"

    pending_table = ""
    if pending_list:
        pending_table = f"""<div class="section-title">Awaiting member grade ({len(pending_list)})</div>
        <table class="data-table"><thead><tr><th>Trip completed</th><th>Member</th><th>Purpose</th><th>Status</th><th>SMS sent</th><th>Ref</th></tr></thead>
        <tbody>{pending_rows}</tbody></table>"""

    trip_cards = "".join(
        _render_trip_card(r, i + 1)
        for i, r in enumerate(sorted(completed, key=lambda x: x.get("responded_at") or "", reverse=True))
    )
    detail_section = ""
    if trip_cards:
        detail_section = f'<div class="section-title">Per-trip audit detail ({len(completed)} trips)</div>{trip_cards}'

    body = stats + _grade_legend() + dist_html + table + pending_table + detail_section
    pl = payer or "All payers"
    gen = _fmt_dt(summary.get("generated_at"))
    return _page_shell(
        f"Member Trip Grade Report — {pl}",
        "Member Trip Grade Report · MCO quality packet",
        "Member Trip Grade Report",
        "Program summary, grade analytics, full trip register, and per-trip audit detail for managed care quality review.",
        f"<span><strong>Payer</strong> {_esc(pl)}</span><span><strong>Report generated</strong> {gen}</span><span><strong>TPA</strong> {_esc(BRAND_NAME)}</span>",
        body,
    )


def write_trip_audit_html(rec: Dict[str, Any], audit_dir: str) -> str:
    completed = rec.get("responded_at") or rec.get("completed_at") or datetime.now(EASTERN).isoformat()
    try:
        dt = datetime.fromisoformat(str(completed).replace("Z", "+00:00"))
        dt = dt.replace(tzinfo=EASTERN) if dt.tzinfo is None else dt.astimezone(EASTERN)
    except Exception:
        dt = datetime.now(EASTERN)
    year_dir = os.path.join(audit_dir, dt.strftime("%Y"))
    os.makedirs(year_dir, exist_ok=True)
    nemt_id = (rec.get("nemt_order_id") or rec.get("token") or "unknown").replace("/", "-")
    path = os.path.join(year_dir, f"{dt.strftime('%Y-%m-%d')}_{nemt_id}.html")
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(render_trip_detail_html(rec))
    os.replace(tmp, path)
    return path
