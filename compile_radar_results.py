#!/usr/bin/env python3
"""
Compile RADAR_RESULTS.md — single source of truth for RADAR output.

Run after any mining sweep:
  python3 compile_radar_results.py

Called automatically at end of: python3 nexus_scheduler.py --radar
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "RADAR_RESULTS.md"


def _load_json(name: str) -> Optional[Dict[str, Any]]:
    path = ROOT / name
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def _latest_sources_sought() -> Optional[Path]:
    files = sorted(ROOT.glob("NEW_SOURCES_SOUGHT_*.md"), key=lambda p: p.stat().st_mtime, reverse=True)
    return files[0] if files else None


def _parse_sources_sought_summary(path: Path) -> Dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    total = 0
    m = re.search(r"\*\*Total:\*\*\s*(\d+)", text)
    if m:
        total = int(m.group(1))
    date_line = path.stem.replace("NEW_SOURCES_SOUGHT_", "").replace("_", " ")
    return {"file": path.name, "total_ddi_relevant": total, "label": date_line}


def _partner_hint(title: str, naics: str = "") -> str:
    t = (title or "").lower()
    n = (naics or "").strip()
    if any(k in t for k in ("drug test", "drug screen", "dot test", "mro", "urinalysis")):
        return "Quest + AMRO + 12PanelNow"
    if any(k in t for k in ("courier", "delivery", "nemt", "transport", "specimen")):
        return "Uber Health / Roadie"
    if any(k in t for k in ("fingerprint", "biometric", "livescan")):
        return "Lakota"
    if any(k in t for k in ("background", "screening")):
        return "NCS"
    if any(k in t for k in ("dna", "genetic", "paternity")):
        return "DDC"
    if any(k in t for k in ("physical", "occupational", "respirator", "audiometric")):
        return "Concentra"
    if any(k in t for k in ("navigation", "enrollment", "benefits", "navigator", "sdoh")):
        return "DDI / CWC direct"
    if n.startswith("621511") or n.startswith("541380"):
        return "Quest + AMRO"
    if n.startswith("485320") or n.startswith("492110"):
        return "Uber Health / Roadie"
    if n.startswith("624190"):
        return "DDI / CWC direct"
    return "Review lane"


def _fit_opp(opp: Dict[str, Any]) -> bool:
    try:
        from ddi_opportunity_fit import analyze_ddi_fit, is_ddi_relevant

        mapped = {
            "title": opp.get("title") or opp.get("name") or "",
            "description": opp.get("description") or opp.get("title") or "",
            "naics": opp.get("naics") or opp.get("naics_code") or "",
            "agency": opp.get("agency") or opp.get("source") or "",
        }
        ok, _ = is_ddi_relevant(mapped)
        return ok
    except Exception:
        return True


def _top_portal_opps(data: Optional[Dict[str, Any]], limit: int = 12) -> List[Dict[str, Any]]:
    if not data:
        return []
    opps = data.get("opportunities") or []
    scored = [o for o in opps if _fit_opp(o)]
    scored.sort(key=lambda o: o.get("deadline") or "9999")
    return scored[:limit]


def _healthcare_highlights(data: Optional[Dict[str, Any]], limit: int = 8) -> List[Dict[str, Any]]:
    if not data:
        return []
    keywords = (
        "nemt", "transport", "courier", "medicaid", "mco", "behavioral",
        "drug", "screening", "enrollment", "navigation", "benefits",
    )
    hits = []
    for o in data.get("opportunities") or []:
        title = (o.get("title") or "").lower()
        if any(k in title for k in keywords):
            hits.append(o)
    return hits[:limit]


def compile_radar() -> Path:
    now = datetime.now().strftime("%Y-%m-%d %I:%M %p ET")
    portal = _load_json("portal_scan_results.json")
    healthcare = _load_json("healthcare_scan_results.json")
    aog = _load_json("aog_sam_cache.json")
    digital = _load_json("digital_nav_sam_cache.json")
    ss_file = _latest_sources_sought()
    ss_summary = _parse_sources_sought_summary(ss_file) if ss_file else {}

    lines: List[str] = [
        "# RADAR RESULTS",
        f"**Last compiled:** {now}",
        "",
        "> **RADAR** = Revenue Acquisition Discovery And Reconnaissance.",
        "> Automated mining output only — **not** bid deadlines, pending tasks, or watch-list items.",
        "> Re-run: `python3 nexus_scheduler.py --radar` · Compile only: `python3 compile_radar_results.py`",
        "",
        "---",
        "",
        "## SCAN SUMMARY",
        "",
        "| Channel | Last scan | Items | Detail file |",
        "|---------|-----------|-------|-------------|",
    ]

    def row(label: str, data: Optional[Dict[str, Any]], detail: str, count_key: str = "total_found") -> None:
        if not data:
            lines.append(f"| {label} | — | — | `{detail}` (missing) |")
            return
        ts = data.get("scan_date") or data.get("generated_at") or "—"
        if isinstance(ts, str) and "T" in ts:
            ts = ts.split("T")[0]
        count = data.get(count_key, data.get("count", len(data.get("opportunities") or [])))
        lines.append(f"| {label} | {ts} | {count} | `{detail}` |")

    row("Public portals (SAM + state/local)", portal, "portal_scan_results.json")
    row("Healthcare / MCO", healthcare, "HEALTHCARE_OPPORTUNITIES_REPORT.md")
    row("AOG / Freight (488190)", aog, "aog_sam_cache.json", "count")
    row("Digital navigation (624190)", digital, "digital_nav_sam_cache.json", "count")
    if ss_summary:
        lines.append(
            f"| Sources Sought / Presol (federal) | {ss_summary.get('label', '—')} | "
            f"{ss_summary.get('total_ddi_relevant', 0)} DDI-fit | `{ss_summary.get('file', '')}` |"
        )
    else:
        lines.append("| Sources Sought / Presol (federal) | — | — | `NEW_SOURCES_SOUGHT_*.md` (missing) |")

    lines.extend(["", "---", "", "## GOVERNMENT — TOP FINDS (portal scan, DDI-fit)", ""])
    top = _top_portal_opps(portal)
    if not top:
        lines.append("*No DDI-fit portal opportunities in cache — run `--radar` or check `portal_scan_results.json`.*")
    else:
        for o in top:
            title = o.get("title", "Untitled")
            agency = (o.get("agency") or o.get("source") or "")[:60]
            due = (o.get("deadline") or "TBD")[:10]
            sa = o.get("set_aside") or "—"
            partner = _partner_hint(title, str(o.get("naics") or ""))
            url = o.get("url") or ""
            lines.append(f"- **{title}** | {agency} | Due {due} | {sa} → **{partner}**")
            if url:
                lines.append(f"  - {url}")

    lines.extend(["", "---", "", "## HEALTHCARE / MCO — HIGHLIGHTS", ""])
    hc = _healthcare_highlights(healthcare)
    if not hc:
        lines.append("*No keyword highlights — see full `HEALTHCARE_OPPORTUNITIES_REPORT.md`.*")
    else:
        for o in hc:
            lines.append(
                f"- **{o.get('title')}** | {o.get('state', '—')} | {o.get('source', '—')} → "
                f"**{_partner_hint(o.get('title', ''))}**"
            )

    if aog and (aog.get("opportunities") or []):
        lines.extend(["", "---", "", "## AOG / FREIGHT", ""])
        for o in (aog.get("opportunities") or [])[:8]:
            lines.append(f"- **{o.get('title', 'Untitled')}** → Airspace / Freight 1st Direct")

    if digital and (digital.get("opportunities") or []):
        lines.extend(["", "---", "", "## DIGITAL NAVIGATION / BENEFITS ENROLLMENT", ""])
        for o in (digital.get("opportunities") or [])[:8]:
            lines.append(f"- **{o.get('title', 'Untitled')}** | {o.get('agency', '—')[:50]}")

    lines.extend([
        "",
        "---",
        "",
        "## MCO PORTALS — MANUAL CHECK",
        "",
        "See `MCO_PORTAL_DAILY_CHECKLIST.md` for login-required portals.",
        "",
        "---",
        "",
        "## NOT RADAR (use other files)",
        "",
        "| Dee asks for… | Read instead |",
        "|---------------|--------------|",
        "| Bid deadlines / active bids | `BID_TRACKER_DASHBOARD.md` |",
        "| Tasks / follow-ups due | `PENDING_ACTIONS.md` |",
        "| Solicitations we're already watching | `NEXUS_WATCH_LIST.md` |",
        "| Today's calendar / priorities | `TODAY_AGENDA.md`, `calendars/SCHEDULED_AGENDA.md` |",
        "| Pipeline dollars | `PIPELINE_TALLY.md` |",
        "",
    ])

    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return OUT


if __name__ == "__main__":
    path = compile_radar()
    print(f"Wrote {path}")
