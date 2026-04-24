"""
SBA SubNet — browse subcontracting opportunities posted by primes (www.sba.gov).

There is no public JSON API; this module scrapes the official Drupal listing and
detail pages. Use responsibly: low concurrency, reasonable page limits.

Listing: /federal-contracting/contracting-guide/prime-subcontracting/subcontracting-opportunities
Detail: /opportunity/{slug}
"""

from __future__ import annotations

import re
import time
from datetime import datetime
from typing import Any, Dict, List, Optional
from urllib.parse import quote, urlencode

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.sba.gov"
LIST_PATH = "/federal-contracting/contracting-guide/prime-subcontracting/subcontracting-opportunities"

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; NEXUS-BACKEND/1.0; +https://deedavis.biz) Python requests",
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "en-US,en;q=0.9",
}


def _session() -> requests.Session:
    s = requests.Session()
    s.headers.update(DEFAULT_HEADERS)
    return s


def _parse_us_date(s: str) -> str:
    s = (s or "").strip()
    if not s:
        return ""
    for fmt in ("%m/%d/%Y", "%m/%d/%y"):
        try:
            return datetime.strptime(s, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return ""


def _normalize_naics_from_cell(text: str) -> tuple[str, str]:
    """Return (6_digit_or_empty, full cell text)."""
    t = (text or "").strip()
    m = re.match(r"^(\d{6})\s*:\s*(.+)$", t)
    if m:
        return m.group(1), t
    m2 = re.search(r"\b(\d{6})\b", t)
    if m2:
        return m2.group(1), t
    return "", t


def _parse_listing_row(tr: Any) -> Optional[Dict[str, Any]]:
    title_cell = tr.select_one("td.views-field-title")
    if not title_cell:
        return None

    a = title_cell.select_one("span.subnet_title a")
    if not a or not a.get("href"):
        return None
    href = a["href"]
    if not href.startswith("/opportunity/"):
        return None
    slug = href.split("/opportunity/")[-1].split("?")[0].strip("/")
    if not slug:
        return None

    title = a.get_text(" ", strip=True)
    biz_el = title_cell.select_one("span.subnet_business_name")
    prime_name = biz_el.get_text(" ", strip=True) if biz_el else ""
    desc_p = title_cell.find("p")
    description = desc_p.get_text(" ", strip=True) if desc_p else ""

    closing_td = tr.select_one("td.views-field-field-subnet-closing-timestamp")
    start_td = tr.select_one("td.views-field-field-subnet-start-date")
    place_td = tr.select_one("td.views-field-field-subnet-place-performance")
    naics_td = tr.select_one("td.views-field-field-subnet-naics")
    poc_td = tr.select_one("td.views-field-nothing")

    naics_code, naics_label = _normalize_naics_from_cell(
        naics_td.get_text(" ", strip=True) if naics_td else ""
    )

    poc_name, poc_email, poc_phone = "", "", ""
    if poc_td:
        mail_a = poc_td.select_one('a[href^="mailto:"]')
        tel_a = poc_td.select_one('a[href^="tel:"]')
        if mail_a:
            poc_name = mail_a.get_text(" ", strip=True)
            poc_email = (mail_a.get("href") or "").replace("mailto:", "").split("?")[0]
        if tel_a:
            poc_phone = tel_a.get_text(" ", strip=True)
            if not poc_name:
                poc_name = tel_a.get_text(" ", strip=True)

    return {
        "source": "SBA SubNet",
        "slug": slug,
        "title": title,
        "prime_name": prime_name,
        "description": description,
        "closing_date_raw": closing_td.get_text(" ", strip=True) if closing_td else "",
        "performance_start_raw": start_td.get_text(" ", strip=True) if start_td else "",
        "place_of_performance": place_td.get_text(" ", strip=True) if place_td else "",
        "naics_code": naics_code,
        "naics_label": naics_label,
        "poc_name": poc_name,
        "poc_email": poc_email,
        "poc_phone": poc_phone,
        "detail_url": f"{BASE_URL}/opportunity/{quote(slug)}",
        "list_url": f"{BASE_URL}{LIST_PATH}",
    }


def fetch_subnet_listing_page(
    session: requests.Session,
    *,
    state: str = "All",
    keyword: str = "",
    page: int = 0,
    timeout: int = 45,
) -> List[Dict[str, Any]]:
    """Fetch one listing page (0-based page index)."""
    q = {"page": page, "state": state, "keyword": keyword or ""}
    url = f"{BASE_URL}{LIST_PATH}?{urlencode(q)}"
    r = session.get(url, timeout=timeout)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    rows = soup.select("table tbody tr")
    out: List[Dict[str, Any]] = []
    for tr in rows:
        rec = _parse_listing_row(tr)
        if rec:
            rec["Deadline"] = _parse_us_date(rec.get("closing_date_raw") or "")
            rec["Response Deadline"] = rec["Deadline"]
            out.append(rec)
    return out


def fetch_subnet_detail(
    session: requests.Session,
    slug: str,
    *,
    timeout: int = 45,
) -> Dict[str, Any]:
    """Optional: merge attachment URLs and long description from detail page."""
    url = f"{BASE_URL}/opportunity/{quote(slug)}"
    r = session.get(url, timeout=timeout)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    art = soup.find("article", class_="sba-subnet-opportunity")
    extra: Dict[str, Any] = {"attachments": []}
    if not art:
        return extra

    desc = art.select_one(".sba-subnet__section__desc")
    if desc:
        extra["description_detail"] = desc.get_text(" ", strip=True)

    for link in art.select(".sba-subnet__attachments a[href]"):
        href = link["href"]
        if href.startswith("/"):
            href = BASE_URL + href
        extra["attachments"].append({"name": link.get_text(" ", strip=True), "url": href})

    return extra


def search_subnet_opportunities(
    *,
    state: str = "All",
    keyword: str = "",
    max_pages: int = 5,
    fetch_details: bool = False,
    pause_sec: float = 0.35,
) -> Dict[str, Any]:
    """
    Paginate SubNet listing and return deduplicated opportunities.

    :param state: e.g. All, MI, CA (must match site dropdown values)
    :param max_pages: hard cap on listing pages (each ~10 rows)
    :param fetch_details: if True, one HTTP GET per opportunity for attachments / long text
    """
    session = _session()
    seen: set[str] = set()
    merged: List[Dict[str, Any]] = []

    for page in range(max(1, int(max_pages))):
        try:
            batch = fetch_subnet_listing_page(session, state=state, keyword=keyword, page=page)
        except requests.RequestException as e:
            return {
                "success": False,
                "error": str(e),
                "page": page,
                "opportunities": merged,
            }

        new_count = 0
        for rec in batch:
            slug = rec.get("slug") or ""
            if slug in seen:
                continue
            seen.add(slug)
            new_count += 1
            if fetch_details:
                try:
                    time.sleep(pause_sec)
                    det = fetch_subnet_detail(session, slug)
                    rec.update(det)
                except requests.RequestException:
                    rec["detail_error"] = True
            merged.append(rec)

        if new_count == 0 and page > 0:
            break
        time.sleep(pause_sec)

    # DDI scoring (optional, for dashboard parity)
    try:
        from ddi_opportunity_fit import analyze_ddi_fit, analyze_subcontract_stretch

        for rec in merged:
            title = rec.get("title") or ""
            desc = " ".join(
                filter(
                    None,
                    [
                        rec.get("description"),
                        rec.get("description_detail"),
                        rec.get("prime_name"),
                    ],
                )
            )
            opp = {
                "title": title,
                "description": desc,
                "naicsCode": rec.get("naics_code") or "",
            }
            fit = analyze_ddi_fit(opp)
            sub = analyze_subcontract_stretch(opp) if not fit["relevant"] else {}
            rec["ddi_lane_fit"] = fit
            rec["ddi_subcontract_nudge"] = sub
    except Exception:
        pass

    return {
        "success": True,
        "state": state,
        "keyword": keyword or "",
        "count": len(merged),
        "opportunities": merged,
    }


def opportunity_to_gpss_fields(rec: Dict[str, Any]) -> Dict[str, Any]:
    """Map a SubNet record to GPSS OPPORTUNITIES-style Airtable fields (best-effort)."""
    slug = rec.get("slug") or "unknown"
    lines = [
        f"Source: SBA SubNet",
        f"Prime: {rec.get('prime_name') or '—'}",
        f"Place: {rec.get('place_of_performance') or '—'}",
        f"POC: {rec.get('poc_name') or '—'} | {rec.get('poc_email') or '—'} | {rec.get('poc_phone') or '—'}",
        f"URL: {rec.get('detail_url') or ''}",
    ]
    if rec.get("description"):
        lines.append("")
        lines.append(rec["description"])
    if rec.get("description_detail") and rec["description_detail"] != rec.get("description"):
        lines.append("")
        lines.append(rec["description_detail"])
    if rec.get("attachments"):
        lines.append("")
        lines.append("Attachments:")
        for a in rec["attachments"][:12]:
            lines.append(f"  - {a.get('name')}: {a.get('url')}")

    fields: Dict[str, Any] = {
        "Name": (rec.get("title") or "SubNet opportunity")[:255],
        "RFP NUMBER": f"SUBNET-{slug}"[:255],
        "Status": "New - SBA SubNet",
        "Source Status": "Active",
        "Notes": "\n".join(lines)[:100000],
    }
    dl = rec.get("Deadline") or rec.get("Response Deadline")
    if dl:
        fields["Deadline"] = dl
    if rec.get("naics_code"):
        fields["NAICS Code"] = rec["naics_code"]
    return fields
