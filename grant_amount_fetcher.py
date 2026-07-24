"""
Fetch grant award amounts for Grants.gov NOFOs.

Primary source: simpler.grants.gov HTML (no API key required).
Optional: Simpler Grants API when SIMPLER_GRANTS_API_KEY is set in .env.
"""
from __future__ import annotations

import json
import os
import re
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, Optional

import requests

try:
    from dotenv import load_dotenv

    load_dotenv(Path(__file__).resolve().parent / ".env")
except ImportError:
    pass

ROOT = Path(__file__).resolve().parent
CACHE_PATH = ROOT / "logs" / "grant_amount_cache.json"
SIMPLER_SEARCH = "https://simpler.grants.gov/search"
SIMPLER_OPP = "https://simpler.grants.gov/opportunity/{uuid}"
SIMPLER_API = "https://api.simpler.grants.gov/v1"
GRANTS_GOV_SEARCH = "https://apply07.grants.gov/grantsws/rest/opportunities/search/"
USER_AGENT = "NEXUS-GBIS/1.0 (Dee Davis Inc.; grant pipeline)"
REQUEST_GAP_SEC = 0.35

_GRID_PAIR_RE = re.compile(
    r'<p class="font-sans-sm text-bold margin-bottom-0">([^<]+)</p>\s*'
    r'<p class="desktop-lg:font-sans-sm">([^<]+)</p>'
)


@dataclass
class GrantAmountInfo:
    opportunity_number: str = ""
    simpler_uuid: str = ""
    program_funding: Optional[float] = None
    award_min: Optional[float] = None
    award_max: Optional[float] = None
    expected_awards: Optional[int] = None
    source: str = ""

    def display_line(self) -> str:
        """Human-readable Amount line for Airtable NOTES."""
        parts: list[str] = []
        if self.award_max is not None:
            parts.append(f"Up to {_fmt_money(self.award_max)}/award")
        elif self.award_min is not None:
            parts.append(f"From {_fmt_money(self.award_min)}/award")
        if self.program_funding is not None:
            parts.append(f"Program pool: {_fmt_money(self.program_funding)}")
        if self.expected_awards is not None:
            parts.append(f"~{self.expected_awards} awards")
        if not parts:
            return ""
        return "Amount: " + " | ".join(parts)

    def display_short(self) -> str:
        """Compact label for GRANTS_RESULTS.md rows."""
        if self.award_max is not None and self.program_funding is not None:
            return f"{_fmt_money_short(self.award_max)}/award · {_fmt_money_short(self.program_funding)} pool"
        if self.award_max is not None:
            return f"Up to {_fmt_money_short(self.award_max)}"
        if self.program_funding is not None:
            return f"Pool {_fmt_money_short(self.program_funding)}"
        if self.award_min is not None:
            return f"From {_fmt_money_short(self.award_min)}"
        return ""


def _load_cache() -> Dict[str, Any]:
    if not CACHE_PATH.exists():
        return {}
    try:
        return json.loads(CACHE_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def _save_cache(cache: Dict[str, Any]) -> None:
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    CACHE_PATH.write_text(json.dumps(cache, indent=2), encoding="utf-8")


def _sleep() -> None:
    time.sleep(REQUEST_GAP_SEC)


def _parse_money(raw: str) -> Optional[float]:
    text = (raw or "").strip()
    if not text or text in ("$--", "--", "N/A", "TBD"):
        return None
    text = text.replace("$", "").replace(",", "")
    try:
        return float(text)
    except ValueError:
        return None


def _parse_int(raw: str) -> Optional[int]:
    text = (raw or "").strip()
    if not text or text in ("$--", "--"):
        return None
    text = text.replace(",", "")
    try:
        return int(text)
    except ValueError:
        return None


def _fmt_money(value: float) -> str:
    if value >= 1_000_000_000:
        return f"${value / 1_000_000_000:.2f}B"
    if value >= 1_000_000:
        return f"${value / 1_000_000:.2f}M" if value % 1_000_000 else f"${int(value / 1_000_000)}M"
    if value >= 1_000:
        return f"${value / 1_000:.0f}K" if value % 1_000 == 0 else f"${value:,.0f}"
    return f"${value:,.0f}"


def _fmt_money_short(value: float) -> str:
    if value >= 1_000_000_000:
        return f"${value / 1_000_000_000:.1f}B".replace(".0B", "B")
    if value >= 1_000_000:
        return f"${value / 1_000_000:.1f}M".replace(".0M", "M")
    if value >= 1_000:
        return f"${value / 1_000:.0f}K".replace(".0K", "K")
    return f"${value:,.0f}"


def _http_get(url: str, **kwargs) -> requests.Response:
    headers = kwargs.pop("headers", {})
    headers.setdefault("User-Agent", USER_AGENT)
    return requests.get(url, headers=headers, timeout=kwargs.pop("timeout", 30), **kwargs)


def _http_post(url: str, **kwargs) -> requests.Response:
    headers = kwargs.pop("headers", {})
    headers.setdefault("User-Agent", USER_AGENT)
    headers.setdefault("Content-Type", "application/json")
    return requests.post(url, headers=headers, timeout=kwargs.pop("timeout", 30), **kwargs)


def parse_simpler_grid(html: str) -> Dict[str, str]:
    return {label.strip(): val.strip() for val, label in _GRID_PAIR_RE.findall(html or "")}


def grid_to_amount_info(grid: Dict[str, str], opp_number: str = "", simpler_uuid: str = "", source: str = "") -> GrantAmountInfo:
    return GrantAmountInfo(
        opportunity_number=opp_number,
        simpler_uuid=simpler_uuid,
        program_funding=_parse_money(grid.get("Program Funding", "")),
        award_min=_parse_money(grid.get("Award Minimum", "")),
        award_max=_parse_money(grid.get("Award Maximum", "")),
        expected_awards=_parse_int(grid.get("Expected awards", "")),
        source=source,
    )


def find_simpler_uuid(opportunity_number: str) -> str:
    if not opportunity_number:
        return ""
    cache = _load_cache()
    key = f"uuid:{opportunity_number.upper()}"
    if key in cache:
        return cache[key]
    _sleep()
    resp = _http_get(SIMPLER_SEARCH, params={"query": opportunity_number})
    resp.raise_for_status()
    uuids = list(dict.fromkeys(re.findall(r"/opportunity/([0-9a-f-]{36})", resp.text)))
    uuid = uuids[0] if uuids else ""
    if uuid:
        cache[key] = uuid
        _save_cache(cache)
    return uuid


def fetch_amounts_simpler_html(opportunity_number: str) -> Optional[GrantAmountInfo]:
    if not opportunity_number:
        return None
    cache = _load_cache()
    cache_key = f"amount:{opportunity_number.upper()}"
    if cache_key in cache:
        return GrantAmountInfo(**cache[cache_key])

    uuid = find_simpler_uuid(opportunity_number)
    if not uuid:
        return None
    _sleep()
    resp = _http_get(SIMPLER_OPP.format(uuid=uuid))
    resp.raise_for_status()
    info = grid_to_amount_info(
        parse_simpler_grid(resp.text),
        opp_number=opportunity_number,
        simpler_uuid=uuid,
        source="simpler_html",
    )
    if info.display_line():
        cache[cache_key] = asdict(info)
        _save_cache(cache)
    return info if info.display_line() else None


def fetch_amounts_simpler_api(opportunity_number: str) -> Optional[GrantAmountInfo]:
    api_key = os.getenv("SIMPLER_GRANTS_API_KEY", "").strip()
    if not api_key or not opportunity_number:
        return None
    cache = _load_cache()
    cache_key = f"amount_api:{opportunity_number.upper()}"
    if cache_key in cache:
        return GrantAmountInfo(**cache[cache_key])

    payload = {
        "query": opportunity_number,
        "pagination": {
            "page_offset": 1,
            "page_size": 5,
            "sort_order": [{"order_by": "relevancy", "sort_direction": "descending"}],
        },
    }
    _sleep()
    resp = _http_post(
        f"{SIMPLER_API}/opportunities/search",
        headers={"X-API-Key": api_key},
        json=payload,
    )
    if not resp.ok:
        return None
    rows = resp.json().get("data") or []
    match = None
    for row in rows:
        if (row.get("opportunity_number") or "").upper() == opportunity_number.upper():
            match = row
            break
    if not match and rows:
        match = rows[0]

    if not match:
        return None

    info = GrantAmountInfo(
        opportunity_number=match.get("opportunity_number") or opportunity_number,
        simpler_uuid=match.get("opportunity_id") or "",
        program_funding=_coerce_float(match.get("estimated_total_program_funding")),
        award_min=_coerce_float(match.get("award_floor")),
        award_max=_coerce_float(match.get("award_ceiling")),
        expected_awards=_coerce_int(match.get("expected_number_of_awards")),
        source="simpler_api",
    )
    if info.display_line():
        cache[cache_key] = asdict(info)
        _save_cache(cache)
    return info if info.display_line() else None


def _coerce_float(value: Any) -> Optional[float]:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _coerce_int(value: Any) -> Optional[int]:
    if value is None or value == "":
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def resolve_opportunity_number(grant_id: str, title: str = "") -> str:
    """Map Grants.gov listing id → funding opportunity number (e.g. HRSA-26-037)."""
    grant_id = str(grant_id or "").strip()
    if not grant_id:
        return ""
    cache = _load_cache()
    key = f"oppnum:{grant_id}"
    if key in cache:
        return cache[key]

    keyword = title.strip()
    if "(" in keyword:
        keyword = keyword.split("(")[-1].replace(")", "").strip() or keyword[:50]
    else:
        keyword = keyword[:50]

    if not keyword:
        return ""

    _sleep()
    resp = _http_post(
        GRANTS_GOV_SEARCH,
        json={"keyword": keyword, "rows": 25, "oppStatuses": "posted|forecasted"},
    )
    if not resp.ok:
        return ""
    for hit in resp.json().get("oppHits", []):
        if str(hit.get("id", "")) == grant_id:
            number = (hit.get("number") or "").strip()
            if number:
                cache[key] = number
                _save_cache(cache)
            return number
    return ""


def fetch_grant_amounts(
    grant_id: str = "",
    title: str = "",
    opportunity_number: str = "",
) -> Optional[GrantAmountInfo]:
    """
    Resolve and fetch award amounts for a Grants.gov NOFO.
    Uses API when key present; falls back to simpler HTML scrape.
    """
    opp_num = (opportunity_number or "").strip()
    if not opp_num and grant_id:
        opp_num = resolve_opportunity_number(grant_id, title)

    if not opp_num:
        return None

    info = fetch_amounts_simpler_api(opp_num)
    if info and info.display_line():
        return info
    return fetch_amounts_simpler_html(opp_num)


def amount_line_from_notes(notes: str) -> str:
    m = re.search(r"(?m)^Amount:\s*(.+)$", notes or "", re.I)
    return m.group(0).strip() if m else ""


def parse_amount_display_line(line: str) -> str:
    """Return short display from existing Amount: note line."""
    if not line:
        return ""
    text = re.sub(r"^Amount:\s*", "", line, flags=re.I).strip()
    return text[:120]
