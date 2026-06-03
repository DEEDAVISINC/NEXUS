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
BIDS = ROOT / "BIDS:RESOURCES"

# Solicitation / event ID patterns found in pipeline files
_ID_PATTERNS = [
    re.compile(r"\b\d{2}[A-Z]{2,}\d{2}[\w-]+\b", re.I),
    re.compile(r"\b(?:NB|RF[PBQ]|IFB|ITB|CR|HMCS|S-)\s*[\w-]+", re.I),
    re.compile(r"\bPANMCC[\w-]+\b", re.I),
    re.compile(r"\b\d{2}C\d{3}[\w-]+\b", re.I),
    re.compile(r"\b0010000000\d+\b"),
    re.compile(r"\bFAP\d+\w*\b", re.I),
    re.compile(r"\bYH27-[\w-]+\b", re.I),
    re.compile(r"\b41NHA-[\w-]+\b", re.I),
    re.compile(r"\b26-87598\b", re.I),
    re.compile(r"\b25-83596\b", re.I),
    re.compile(r"\bW912[\w-]+\b", re.I),
]

# Healthcare portal index pages — prose scraped as fake "opportunities"
_PORTAL_INDEX_FRAGMENTS = (
    "umms.org/about/vendors-services/minority-business-program/open-rfp",
    "inspirahealthnetwork.org/about-us/request-proposals-rfp",
    "medcenterhealth.org/procurement-opportunities",
)

_HEALTHCARE_BOILERPLATE_TITLES = (
    "should you have additional questions",
    "umms representative listed in the rfp",
    "umms open rfps",
    "committed to an open and transparent",
    "posting the upcoming",
    "prospective vendors maximum time",
    "request for proposal (rfp) process",
    "inspira's request for proposal",
)

_HEALTHCARE_INTEL_URLS: Optional[set] = None


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


def _extract_ids(text: str) -> set:
    found: set = set()
    for pat in _ID_PATTERNS:
        for m in pat.finditer(text or ""):
            found.add(re.sub(r"\s+", "", m.group(0)).upper())
    return found


def _build_pipeline_index() -> tuple[set, set]:
    """Return (known_ids, known_url_fragments) from active pipeline files."""
    ids: set = set()
    urls: set = set()
    text_blobs: List[str] = []

    for rel in (
        "NEXUS_WATCH_LIST.md",
        "BID_TRACKER_DASHBOARD.md",
        "PENDING_ACTIONS.md",
        "BIDS:RESOURCES/FEDERAL CO OUTREACH PIPELINE/CO_OUTREACH_TRACKER.md",
    ):
        p = ROOT / rel
        if p.exists():
            text_blobs.append(p.read_text(encoding="utf-8", errors="ignore"))

    if BIDS.exists():
        for wf in BIDS.glob("**/WORKFLOW_CHECKLIST.md"):
            text_blobs.append(wf.read_text(encoding="utf-8", errors="ignore"))
        for exp in (BIDS / "RADAR HEALTHCARE MCO").glob("*.md"):
            text_blobs.append(exp.read_text(encoding="utf-8", errors="ignore"))

    for blob in text_blobs:
        ids |= _extract_ids(blob)
        for u in re.findall(r"https?://[^\s\)|>]+", blob):
            urls.add(u.rstrip(".,;"))

    return ids, urls


def _healthcare_intel_urls() -> set:
    global _HEALTHCARE_INTEL_URLS
    if _HEALTHCARE_INTEL_URLS is not None:
        return _HEALTHCARE_INTEL_URLS
    urls: set = set()
    intel_dir = BIDS / "RADAR HEALTHCARE MCO"
    if intel_dir.exists():
        for md in intel_dir.glob("*.md"):
            for u in re.findall(r"https?://[^\s\)|>]+", md.read_text(encoding="utf-8", errors="ignore")):
                urls.add(u.rstrip(".,;"))
    _HEALTHCARE_INTEL_URLS = urls
    return urls


def _opp_fingerprint(opp: Dict[str, Any]) -> set:
    parts = [
        opp.get("title") or "",
        opp.get("description") or "",
        opp.get("url") or opp.get("link") or "",
        opp.get("solicitationNumber") or opp.get("solicitation_number") or "",
        opp.get("agency") or opp.get("source") or "",
    ]
    return _extract_ids(" ".join(str(p) for p in parts))


def _in_pipeline(opp: Dict[str, Any], known_ids: set, known_urls: set) -> bool:
    link = (opp.get("url") or opp.get("link") or opp.get("uiLink") or "").rstrip(".,;")
    if link and link in known_urls:
        return True
    if _opp_fingerprint(opp) & known_ids:
        return True
    title = (opp.get("title") or "").lower()
    # Hard excludes for items logged as passed / exploration-only
    if "87598" in title or "26-87598" in title:
        return True
    if link in _healthcare_intel_urls():
        return True
    return False


def _is_healthcare_portal_noise(opp: Dict[str, Any]) -> bool:
    """Hospital/MCO portal index pages scraped as duplicate pseudo-RFPs."""
    title = (opp.get("title") or "").lower()
    link = (opp.get("link") or opp.get("url") or "").lower()
    if any(b in title for b in _HEALTHCARE_BOILERPLATE_TITLES):
        return True
    if any(idx in link for idx in _PORTAL_INDEX_FRAGMENTS):
        if not opp.get("deadline") and not opp.get("responseDeadLine"):
            if not re.search(r"\brfp\s*#|\bsolicitation\b|\bdue\b|\bifb\b|\bitb\b", title):
                return True
    return False


def _is_actionable_opportunity(opp: Dict[str, Any], channel: str) -> bool:
    """Healthcare scan returns many program pages — not bid opportunities."""
    if channel != "healthcare":
        return True
    if _is_healthcare_portal_noise(opp):
        return False
    title = (opp.get("title") or "").lower()
    link = (opp.get("link") or opp.get("url") or "").lower()
    bid_signals = (
        "rfp", "rfq", "ifb", "itb", "bid", "solicitation", "procurement",
        "contract opport", "request for proposal", "request for quote",
        "recompete", "nofo", "nofa",
    )
    if any(s in title or s in link for s in bid_signals):
        return True
    # Program / initiative pages without a due date are intel, not RADAR finds
    if not opp.get("deadline") and not opp.get("responseDeadLine"):
        return False
    return True


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


def _net_new_opps(
    opps: List[Dict[str, Any]],
    known_ids: set,
    known_urls: set,
    channel: str = "portal",
    limit: int = 12,
) -> tuple[List[Dict[str, Any]], int]:
    """Filter to DDI-fit opportunities NOT already in the pipeline."""
    excluded = 0
    fresh: List[Dict[str, Any]] = []
    for o in opps:
        if not _fit_opp(o):
            continue
        if not _is_actionable_opportunity(o, channel):
            excluded += 1
            continue
        if _in_pipeline(o, known_ids, known_urls):
            excluded += 1
            continue
        fresh.append(o)
    fresh.sort(key=lambda x: x.get("deadline") or x.get("responseDeadLine") or "9999")
    return fresh[:limit], excluded


def compile_radar() -> Path:
    now = datetime.now().strftime("%Y-%m-%d %I:%M %p ET")
    known_ids, known_urls = _build_pipeline_index()
    portal = _load_json("portal_scan_results.json")
    healthcare = _load_json("healthcare_scan_results.json")
    aog = _load_json("aog_sam_cache.json")
    digital = _load_json("digital_nav_sam_cache.json")
    ss_file = _latest_sources_sought()
    ss_summary = _parse_sources_sought_summary(ss_file) if ss_file else {}

    portal_pool = (portal or {}).get("opportunities") or []
    hc_pool = (healthcare or {}).get("opportunities") or []
    aog_pool = (aog or {}).get("opportunities") or []
    digital_pool = (digital or {}).get("opportunities") or []

    top, portal_excl = _net_new_opps(portal_pool, known_ids, known_urls, "portal", 12)
    hc, hc_excl = _net_new_opps(hc_pool, known_ids, known_urls, "healthcare", 8)
    aog_new, aog_excl = _net_new_opps(aog_pool, known_ids, known_urls, "aog", 8)
    digital_new, digital_excl = _net_new_opps(digital_pool, known_ids, known_urls, "digital", 8)
    total_excluded = portal_excl + hc_excl + aog_excl + digital_excl
    total_net_new = len(top) + len(hc) + len(aog_new) + len(digital_new)

    lines: List[str] = [
        "# RADAR RESULTS",
        f"**Last compiled:** {now}",
        "",
        "> **RADAR** = Revenue Acquisition Discovery And Reconnaissance.",
        "> **NET-NEW ONLY** — excludes anything already in bid folders, watch list, bid tracker, CO outreach, or healthcare exploration docs.",
        "> Re-run: `python3 nexus_scheduler.py --radar` · Compile only: `python3 compile_radar_results.py`",
        "",
        f"**Pipeline index:** {len(known_ids)} known solicitation IDs · **Excluded this compile:** {total_excluded} · **Net-new finds:** {total_net_new}",
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

    lines.extend(["", "---", "", "## NET-NEW — GOVERNMENT (portal scan)", ""])
    if not top:
        lines.append(
            "*No net-new DDI-fit portal opportunities — "
            f"{len(portal_pool)} scanned, {portal_excl} already in pipeline or not actionable.*"
        )
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

    lines.extend(["", "---", "", "## NET-NEW — HEALTHCARE / MCO", ""])
    if not hc:
        lines.append(
            "*No net-new healthcare/MCO solicitations — "
            f"{len(hc_pool)} scanned (mostly program pages), {hc_excl} excluded.*"
        )
    else:
        for o in hc:
            lines.append(
                f"- **{o.get('title')}** | {o.get('state', '—')} | {o.get('source', '—')} → "
                f"**{_partner_hint(o.get('title', ''))}**"
            )

    if aog_new:
        lines.extend(["", "---", "", "## NET-NEW — AOG / FREIGHT", ""])
        for o in aog_new:
            lines.append(f"- **{o.get('title', 'Untitled')}** → Airspace / Freight 1st Direct")

    if digital_new:
        lines.extend(["", "---", "", "## NET-NEW — DIGITAL NAVIGATION / BENEFITS", ""])
        for o in digital_new:
            agency = (o.get("department") or o.get("agency") or "—")[:50]
            lines.append(f"- **{o.get('title', 'Untitled')}** | {agency}")

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
