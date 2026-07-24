#!/usr/bin/env python3
"""
NEXUS RADAR — CCAM-TAC grants & FTA human-services transport funding monitor.

Scrapes CCAM-TAC grant listing pages (Partner + External + ICAM + Community Rides).
Writes ccam_tac_grants_cache.json for compile_radar_results.py.

Run:  python3 mine_ccam_tac_grants.py
"""

from __future__ import annotations

import json
import logging
import re
import urllib.error
import urllib.request
from datetime import datetime
from html import unescape
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

BASE_DIR = Path(__file__).resolve().parent
CACHE_FILE = BASE_DIR / "ccam_tac_grants_cache.json"
USER_AGENT = "NEXUS-RADAR/1.0 (Dee Davis Inc.; opportunity monitor)"

# Primary listing pages + standing program references
SEED_PAGES: Tuple[Tuple[str, str], ...] = (
    ("partner_funding", "https://www.ccam-tac.org/partner-funding-opportunities/"),
    ("external_grants", "https://www.ccam-tac.org/external-grants/"),
    ("icam_program", "https://www.ccam-tac.org/innovative-coordinated-access-and-mobility-icam-pilot-program/"),
    ("community_rides", "https://www.ccam-tac.org/2026-community-rides-grants/"),
    ("grants_hub", "https://www.ccam-tac.org/grants/"),
)

# Section headers on listing pages → opportunity blocks until next header
_HEADER_RE = re.compile(
    r"(FY\s*\d{4}[^<\n]{0,120}|US DOT Navigator|USDA[^<\n]{0,80}|"
    r"Kevin and Avonte[^<\n]{0,80}|Community Rides|ICAM[^<\n]{0,80})",
    re.I,
)
_DEADLINE_RE = re.compile(
    r"Deadline:\s*([^<\n]+?)(?:\s*$|\s+(?:Apply|A DOJ|The |BUILD|Go to))",
    re.I,
)
_TBA_RE = re.compile(r"\bTBA\b|yet to open|do not yet have deadlines", re.I)

_HIGH_FIT = re.compile(
    r"ICAM|coordinated access|mobility management|5310|5311|NEMT|non-?emergency medical|"
    r"human service.*transport|community rides|trip cost allocation|braiding",
    re.I,
)
_MED_FIT = re.compile(
    r"transport|mobility|medicaid|nemt|dialysis|paratransit|5311|rural transit",
    re.I,
)
_NO_GO = re.compile(
    r"BUILD Grants|surface transportation infrastructure|Kevin and Avonte|"
    r"Rural Economic Development Loan|wandering|dementia.*developmental",
    re.I,
)

log = logging.getLogger(__name__)


def _fetch(url: str, timeout: int = 45) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="replace")


def _html_to_text(html: str) -> str:
    text = re.sub(r"<script[^>]*>.*?</script>", " ", html, flags=re.S | re.I)
    text = re.sub(r"<style[^>]*>.*?</style>", " ", text, flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", "\n", text)
    text = unescape(text)
    lines = [re.sub(r"\s+", " ", ln).strip() for ln in text.splitlines()]
    return "\n".join(ln for ln in lines if ln)


def _parse_deadline_status(deadline_raw: str, body: str) -> Tuple[str, str]:
    raw = (deadline_raw or "").strip()
    if not raw or _TBA_RE.search(raw) or _TBA_RE.search(body[:500]):
        return "tba", raw or "TBA"
    # Closed if date clearly in past (Jun 2026 reference)
    dm = re.search(
        r"(January|February|March|April|May|June|July|August|September|October|November|December)"
        r"\s+\d{1,2},?\s+\d{4}",
        raw,
        re.I,
    )
    if dm:
        try:
            dt = datetime.strptime(dm.group(0).replace(",", ""), "%B %d %Y")
            if dt.date() < datetime(2026, 6, 14).date():
                return "closed", raw
        except ValueError:
            pass
    if re.search(r"Quarterly|Rolling|N/A", raw, re.I):
        return "rolling", raw
    if raw:
        return "open_or_unknown", raw
    return "tba", "TBA"


def _ddi_fit(title: str, body: str) -> Tuple[str, str]:
    blob = f"{title} {body}"
    if _NO_GO.search(blob):
        return "no-go", "Wrong lane (infra / DOJ wandering / USDA utility RLF) or partner-only 5311 lead"
    if _HIGH_FIT.search(blob):
        return "high", "Mobility management / NEMT / ICAM / CCAM coordination lane"
    if _MED_FIT.search(blob):
        return "medium", "Transport-adjacent — verify GO/NO-GO"
    if "DOT Navigator" in title:
        return "reference", "Grant prep resource — not revenue"
    return "low", "Review manually"


def _extract_opportunities(source: str, url: str, html: str) -> List[Dict[str, Any]]:
    text = _html_to_text(html)
    opportunities: List[Dict[str, Any]] = []

    if source == "icam_program":
        title = "Innovative Coordinated Access and Mobility (ICAM) Pilot Program"
        body = text[:4000]
        status, deadline = _parse_deadline_status("", body)
        fit, note = _ddi_fit(title, body)
        opportunities.append(
            {
                "title": title,
                "source": source,
                "url": url,
                "deadline": deadline,
                "status": status if status != "open_or_unknown" else "watch",
                "ddi_fit": fit,
                "fit_note": note,
                "partner": "NEXUS/PRISM coordination infra · team w/ 5310 lead",
            }
        )
        return opportunities

    if source == "community_rides":
        title = "Community Rides Grants (National RTAP / FTA)"
        body = text[:4000]
        fit, note = _ddi_fit(title, body)
        opportunities.append(
            {
                "title": title,
                "source": source,
                "url": url,
                "deadline": "2026 cycle closed (check National RTAP for 2027)",
                "status": "closed",
                "ddi_fit": "low",
                "fit_note": "5311 transit must lead — DDI partner/sub only · ~$60K avg",
                "partner": "CWC navigation + DDI TPA if rural transit invites",
            }
        )
        return opportunities

    # Partner / external listings: split on strong headings in plain text
    chunks = re.split(
        r"\n(?=(?:FY\s*\d{4}|US DOT Navigator|USDA|Kevin and Avonte))",
        text,
        flags=re.I,
    )
    for chunk in chunks:
        chunk = chunk.strip()
        if len(chunk) < 40:
            continue
        first_line = chunk.split("\n", 1)[0].strip()
        if not re.search(r"FY\s*\d{4}|Navigator|USDA|Kevin", first_line, re.I):
            continue
        title = first_line[:200]
        dm = _DEADLINE_RE.search(chunk)
        deadline_raw = dm.group(1).strip() if dm else ""
        status, deadline = _parse_deadline_status(deadline_raw, chunk)
        fit, note = _ddi_fit(title, chunk)
        opportunities.append(
            {
                "title": title,
                "source": source,
                "url": url,
                "deadline": deadline,
                "status": status,
                "ddi_fit": fit,
                "fit_note": note,
                "partner": _partner_for(title, chunk),
            }
        )

    return opportunities


def _partner_for(title: str, body: str) -> str:
    t = f"{title} {body}".lower()
    if "icam" in t or "mobility management" in t:
        return "NEXUS/PRISM · DEPOINTE proof"
    if "nemt" in t or "medical transport" in t:
        return "Uber Health / DEPOINTE TPA"
    if "navigation" in t or "sdoh" in t:
        return "DDI / CWC direct"
    return "Review lane"


def mine_ccam_tac() -> Dict[str, Any]:
    all_opps: List[Dict[str, Any]] = []
    errors: List[str] = []

    for source, url in SEED_PAGES:
        try:
            html = _fetch(url)
            all_opps.extend(_extract_opportunities(source, url, html))
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            errors.append(f"{source}: {exc}")
            log.warning("CCAM-TAC fetch failed %s: %s", url, exc)

    # De-dupe by title
    seen: set = set()
    unique: List[Dict[str, Any]] = []
    for o in all_opps:
        key = o["title"].lower()[:80]
        if key in seen:
            continue
        seen.add(key)
        unique.append(o)

    actionable = [
        o
        for o in unique
        if o.get("ddi_fit") in ("high", "medium")
        and o.get("status") in ("tba", "watch", "rolling", "open_or_unknown")
    ]
    watch = [o for o in unique if o.get("status") == "watch" or o.get("ddi_fit") == "high"]

    payload = {
        "scan_date": datetime.now().isoformat(),
        "source": "ccam-tac.org",
        "pages_scanned": len(SEED_PAGES),
        "total_found": len(unique),
        "actionable_count": len(actionable),
        "watch_count": len(watch),
        "errors": errors,
        "opportunities": unique,
        "intel_file": "NEXUS_LEARNING/CCAM_FTA_COORDINATION_INTEL.md",
    }
    CACHE_FILE.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    data = mine_ccam_tac()
    print(f"Wrote {CACHE_FILE} — {data['total_found']} items, {data['actionable_count']} actionable")


if __name__ == "__main__":
    main()
