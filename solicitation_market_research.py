#!/usr/bin/env python3
"""
NEXUS — Solicitation incumbent & award pricing research (USASpending).

Pulls recent federal awards similar to the opportunity (keywords, NAICS, place of performance)
to surface likely incumbents and obligation amounts. Supports proposal pricing and competitive
context. Does not replace human judgment; line-item pricing is rarely public.
"""

from __future__ import annotations

import re
import time
from collections import defaultdict
from datetime import datetime, timedelta
from statistics import median
from typing import Any, Dict, List, Optional, Set

import requests

USASPEND_URL = "https://api.usaspending.gov/api/v2/search/spending_by_award/"

STOPWORDS = {
    "the", "and", "for", "with", "from", "that", "this", "will", "are", "has", "have", "been",
    "services", "service", "support", "provide", "providing", "government", "federal", "state",
    "contract", "contracts", "year", "years", "base", "period", "performance", "work", "task",
    "order", "required", "requirements", "all", "any", "per", "may", "not", "use", "using", "inc",
    "llc", "corp",
}

US_STATE_ABBREV = {
    "alabama": "AL", "alaska": "AK", "arizona": "AZ", "arkansas": "AR", "california": "CA",
    "colorado": "CO", "connecticut": "CT", "delaware": "DE", "florida": "FL", "georgia": "GA",
    "hawaii": "HI", "idaho": "ID", "illinois": "IL", "indiana": "IN", "iowa": "IA",
    "kansas": "KS", "kentucky": "KY", "louisiana": "LA", "maine": "ME", "maryland": "MD",
    "massachusetts": "MA", "michigan": "MI", "minnesota": "MN", "mississippi": "MS",
    "missouri": "MO", "montana": "MT", "nebraska": "NE", "nevada": "NV", "new hampshire": "NH",
    "new jersey": "NJ", "new mexico": "NM", "new york": "NY", "north carolina": "NC",
    "north dakota": "ND", "ohio": "OH", "oklahoma": "OK", "oregon": "OR", "pennsylvania": "PA",
    "rhode island": "RI", "south carolina": "SC", "south dakota": "SD", "tennessee": "TN",
    "texas": "TX", "utah": "UT", "vermont": "VT", "virginia": "VA", "washington": "WA",
    "west virginia": "WV", "wisconsin": "WI", "wyoming": "WY", "district of columbia": "DC",
}


class SolicitationMarketResearch:
    """USASpending-backed incumbent / pricing benchmark pass for a solicitation."""

    def research_from_airtable_fields(self, fields: Dict[str, Any]) -> Dict[str, Any]:
        norm = self._normalize_fields(fields)
        return self.research_for_opportunity(norm)

    def research_for_opportunity(self, opp: Dict[str, Any]) -> Dict[str, Any]:
        """
        opp: normalized dict with keys title, description, agency, solicitation_number, state,
        naics_codes (list of 6-digit strings), estimated_value, notice_id (optional).
        """
        title = (opp.get("title") or "").strip()
        description = (opp.get("description") or "").strip()
        agency = (opp.get("agency") or "").strip()
        state = (opp.get("state") or "").strip().upper()[:2] if opp.get("state") else ""
        naics_list = [n for n in (opp.get("naics_codes") or []) if re.match(r"^\d{6}$", str(n))]
        keywords = self._keywords_from_text(title, description)

        merged: Dict[str, Dict] = {}
        queries_run: List[str] = []

        def absorb(label: str, rows: List[Dict]) -> None:
            queries_run.append(label)
            for row in rows or []:
                aid = row.get("Award ID") or row.get("generated_internal_id") or row.get("award_id")
                key = str(aid) if aid else f"row_{id(row)}"
                if key not in merged:
                    merged[key] = row

        # 1) Keyword + NAICS + geography (tightest)
        f1 = self._base_filters(years=5)
        if keywords:
            f1["keywords"] = keywords[:4]
        if naics_list:
            f1["naics_codes"] = naics_list[:3]
        if state and len(state) == 2:
            f1["place_of_performance_locations"] = [{"country": "USA", "state": state}]
        r1 = self._search_awards(f1, limit=45)
        absorb("keywords_naics_geo", r1)

        # 2) NAICS + geo only (if thin)
        if len(merged) < 12 and naics_list:
            f2 = self._base_filters(years=5)
            f2["naics_codes"] = naics_list[:3]
            if state and len(state) == 2:
                f2["place_of_performance_locations"] = [{"country": "USA", "state": state}]
            r2 = self._search_awards(f2, limit=45)
            absorb("naics_geo", r2)
            time.sleep(0.15)

        # 3) Keywords only (national) if still thin
        if len(merged) < 8 and keywords:
            f3 = self._base_filters(years=5)
            f3["keywords"] = keywords[:4]
            r3 = self._search_awards(f3, limit=35)
            absorb("keywords_national", r3)
            time.sleep(0.15)

        # 4) Awarding agency (toptier) — helps incumbent-style lists when NAICS missing
        if len(merged) < 6 and agency and len(agency) > 3:
            f4 = self._base_filters(years=3)
            f4["agencies"] = [{"type": "awarding", "tier": "toptier", "name": agency}]
            r4 = self._search_awards(f4, limit=40)
            absorb("awarding_agency", r4)
            time.sleep(0.15)

        rows = list(merged.values())
        likely = self._likely_incumbents(rows, title, description, agency)
        bench = self._pricing_benchmark(rows, opp.get("estimated_value"))

        return {
            "source": "usaspending.gov",
            "queries_run": queries_run,
            "keywords_used": keywords,
            "naics_used": naics_list,
            "state_filter": state or None,
            "award_rows_returned": len(rows),
            "likely_incumbents": likely,
            "pricing_benchmark": bench,
            "recent_comparable_awards": self._sample_awards_for_proposal(rows, limit=12),
            "proposal_pricing_notes": self._proposal_notes(likely, bench, opp.get("estimated_value")),
            "limitations": [
                "Federal USASpending awards only — state/local awards may not appear.",
                "Figures are obligated award totals, not line-item or loser bid prices.",
                "Incumbent inference is heuristic; verify via SAM/FPDS or solicitation docs.",
            ],
            "researched_at": datetime.now().isoformat() + "Z",
        }

    def format_notes_block(self, payload: Dict[str, Any]) -> str:
        """Markdown snippet for GPSS Notes / internal file."""
        lines = [
            f"### NEXUS — Incumbent & pricing research ({payload.get('researched_at', '')})",
            f"- Source: {payload.get('source')}",
            f"- Comparable awards sampled: {payload.get('award_rows_returned', 0)}",
        ]
        bench = payload.get("pricing_benchmark") or {}
        if bench.get("median_amount") is not None:
            lines.append(
                f"- Award amounts (sample): median **${bench.get('median_amount'):,.0f}**, "
                f"min ${bench.get('min_amount') or 0:,.0f}, max ${bench.get('max_amount') or 0:,.0f}"
            )
        top = (payload.get("likely_incumbents") or [])[:5]
        if top:
            lines.append("- Likely / frequent awardees (verify):")
            for x in top:
                lines.append(
                    f"  - **{x.get('recipient_name')}** — {x.get('award_count')} awards in sample, "
                    f"~${x.get('total_obligation', 0):,.0f} obligated"
                )
        for lim in (payload.get("limitations") or [])[:3]:
            lines.append(f"- _{lim}_")
        return "\n".join(lines)

    # --- internals ---

    def _normalize_fields(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        def g(*keys: str, default: Any = "") -> Any:
            for k in keys:
                v = raw.get(k)
                if v is None:
                    continue
                if isinstance(v, list) and v:
                    v = v[0]
                if v not in ("", None):
                    return v
            return default

        na = g("NAICS", "NAICS Code", "NAICS CODES", "naics")
        if isinstance(na, str):
            na_parts = [x.strip() for x in re.split(r"[,;\s]+", na) if x.strip()]
        elif isinstance(na, list):
            na_parts = [str(x).strip() for x in na if str(x).strip()]
        else:
            na_parts = []
        naics_codes = [n for n in na_parts if re.match(r"^\d{6}$", str(n))]

        val = g("ESTIMATED VALUE", "Value", "Estimated Value", "Contract Value", "value")
        try:
            est_val = float(val) if val not in ("", None) else None
        except (TypeError, ValueError):
            est_val = None

        st = g(
            "PLACE OF PERFORMANCE STATE", "State", "PLACE OF PERFORMANCE", "POP State",
            "Place of Performance State Code",
        )
        state_norm = self._norm_state(st)

        return {
            "title": str(g("TITLE", "Title", "Name", "name")),
            "description": str(g("DESCRIPTION", "Description", "description")),
            "agency": str(g("AGENCY", "Agency", "Agency Name", "Awarding Agency")),
            "solicitation_number": str(
                g("RFP NUMBER", "RFP Number", "Solicitation Number", "SOLICITATION", "Notice ID")
            ),
            "state": state_norm,
            "naics_codes": naics_codes,
            "estimated_value": est_val,
            "notice_id": str(g("Notice ID", "NOTICE ID")),
        }

    def _norm_state(self, s: Any) -> str:
        if not s:
            return ""
        t = str(s).strip()
        if len(t) == 2 and t.isalpha():
            return t.upper()
        tl = t.lower()
        for name, ab in US_STATE_ABBREV.items():
            if name in tl:
                return ab
        m = re.search(r"\b([A-Z]{2})\b", t)
        if m:
            return m.group(1).upper()
        return ""

    def _keywords_from_text(self, title: str, desc: str, max_kw: int = 5) -> List[str]:
        blob = f"{title} {(desc or '')[:1200]}"
        words = re.findall(r"[A-Za-z][A-Za-z0-9\-]{2,}", blob)
        out: List[str] = []
        seen: Set[str] = set()
        for w in words:
            wl = w.lower()
            if wl in STOPWORDS or wl in seen:
                continue
            if len(wl) < 4:
                continue
            out.append(w)
            seen.add(wl)
            if len(out) >= max_kw:
                break
        return out

    def _base_filters(self, years: int = 5) -> Dict[str, Any]:
        return {
            "time_period": [{
                "start_date": (datetime.now() - timedelta(days=365 * years)).strftime("%Y-%m-%d"),
                "end_date": datetime.now().strftime("%Y-%m-%d"),
            }],
            "award_type_codes": ["A", "B", "C", "D"],
        }

    def _search_awards(self, filters: Dict[str, Any], limit: int = 50, page: int = 1) -> List[Dict]:
        body = {
            "filters": filters,
            "fields": [
                "Award ID",
                "Recipient Name",
                "Award Amount",
                "Total Obligation",
                "Awarding Agency",
                "Awarding Sub Agency",
                "Description",
                "Start Date",
                "End Date",
                "NAICS Code",
                "PSC Code",
                "Place of Performance State Code",
                "generated_internal_id",
                "Contract Award Type",
            ],
            "limit": min(limit, 100),
            "page": page,
            "sort": "Start Date",
            "order": "desc",
        }
        try:
            r = requests.post(USASPEND_URL, json=body, timeout=50)
            if r.status_code != 200:
                return []
            return r.json().get("results") or []
        except Exception:
            return []

    def _likely_incumbents(
        self,
        rows: List[Dict],
        title: str,
        description: str,
        agency: str,
    ) -> List[Dict]:
        blob = f"{title} {description}".lower()
        agg: Dict[str, Dict[str, Any]] = defaultdict(
            lambda: {
                "recipient_name": "",
                "award_count": 0,
                "total_obligation": 0.0,
                "agencies": set(),
                "relevance_boost": 0,
            }
        )

        for row in rows:
            name = row.get("Recipient Name") or "Unknown"
            amt = float(row.get("Award Amount") or row.get("Total Obligation") or 0)
            a = agg[name]
            a["recipient_name"] = name
            a["award_count"] += 1
            a["total_obligation"] += amt
            aa = row.get("Awarding Agency") or ""
            sa = row.get("Awarding Sub Agency") or ""
            if aa:
                a["agencies"].add(aa)
            if sa:
                a["agencies"].add(sa)
            desc = (row.get("Description") or "").lower()
            boost = 0
            for w in blob.split():
                if len(w) > 4 and w in desc:
                    boost += 1
            if agency and agency.lower()[:12] in (aa + sa).lower():
                boost += 2
            a["relevance_boost"] += boost

        ranked = sorted(
            agg.values(),
            key=lambda x: (x["relevance_boost"], x["total_obligation"]),
            reverse=True,
        )
        out: List[Dict] = []
        for x in ranked[:15]:
            out.append({
                "recipient_name": x["recipient_name"],
                "award_count": x["award_count"],
                "total_obligation": round(x["total_obligation"], 2),
                "awarding_agencies_sample": sorted(x["agencies"])[:4],
                "relevance_boost": x["relevance_boost"],
            })
        return out

    def _pricing_benchmark(self, rows: List[Dict], est_value: Optional[float]) -> Dict[str, Any]:
        amounts = []
        for row in rows:
            v = row.get("Award Amount")
            if v is None:
                v = row.get("Total Obligation")
            try:
                fv = float(v)
                if fv > 0:
                    amounts.append(fv)
            except (TypeError, ValueError):
                continue

        if not amounts:
            return {
                "award_count": 0,
                "min_amount": None,
                "max_amount": None,
                "median_amount": None,
                "vs_estimate_note": None,
            }

        med = float(median(amounts))
        note = None
        if est_value and est_value > 0:
            ratio = est_value / med if med else None
            if ratio:
                if ratio < 0.55:
                    note = "Your estimate is well below the median comparable award — validate scope and risk of being non-competitive or under-scoped."
                elif ratio > 1.8:
                    note = "Your estimate is well above the median comparable award — confirm CLIN structure or incumbent pricing context."
                else:
                    note = "Your estimate is in a plausible band vs. recent comparable awards (still validate line-by-line)."

        return {
            "award_count": len(amounts),
            "min_amount": round(min(amounts), 2),
            "max_amount": round(max(amounts), 2),
            "median_amount": round(med, 2),
            "vs_estimate_note": note,
        }

    def _sample_awards_for_proposal(self, rows: List[Dict], limit: int = 12) -> List[Dict]:
        def sort_key(r: Dict):
            d = r.get("Start Date") or ""
            return d

        sorted_rows = sorted(rows, key=sort_key, reverse=True)
        slim: List[Dict] = []
        for row in sorted_rows[:limit]:
            amt = row.get("Award Amount") or row.get("Total Obligation")
            try:
                amt_f = float(amt) if amt is not None else None
            except (TypeError, ValueError):
                amt_f = None
            slim.append({
                "recipient_name": row.get("Recipient Name"),
                "award_amount": amt_f,
                "awarding_agency": row.get("Awarding Agency"),
                "awarding_sub_agency": row.get("Awarding Sub Agency"),
                "description": (row.get("Description") or "")[:280],
                "start_date": row.get("Start Date"),
                "end_date": row.get("End Date"),
                "award_id": row.get("Award ID") or row.get("generated_internal_id"),
                "naics": row.get("NAICS Code"),
                "pop_state": row.get("Place of Performance State Code"),
            })
        return slim

    def _proposal_notes(
        self,
        likely: List[Dict],
        bench: Dict[str, Any],
        est_value: Optional[float],
    ) -> List[str]:
        notes: List[str] = []
        if bench.get("median_amount"):
            notes.append(
                f"Recent comparable federal awards in this search: median **${bench['median_amount']:,.0f}** "
                f"across **{bench.get('award_count', 0)}** award amounts."
            )
        if likely:
            top = likely[0]
            notes.append(
                f"Most frequent / relevant awardee in sample: **{top.get('recipient_name')}** "
                f"({top.get('award_count')} awards, ~${top.get('total_obligation', 0):,.0f} obligated). "
                "Treat as competitive intel until verified on this solicitation."
            )
        if est_value and bench.get("vs_estimate_note"):
            notes.append(bench["vs_estimate_note"])
        if not notes:
            notes.append(
                "No strong USASpending matches — broaden NAICS/keywords or run manual FPDS/SAM check."
            )
        return notes
