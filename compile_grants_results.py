#!/usr/bin/env python3
"""
Compile GRANTS_RESULTS.md — human-readable GBIS pipeline output.

Run after GBIS mining:
  python3 compile_grants_results.py
  python3 compile_grants_results.py --backfill   # sync Entity in Airtable NOTES first

Called automatically at end of: python3 nexus_scheduler.py --gbis
"""
from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "GRANTS_RESULTS.md"
STATE = ROOT / "logs" / "grants_results_last_compile.json"

DDI_LANE_KEYWORDS = (
    "community health",
    "benefits",
    "enrollment",
    "navigator",
    "medicaid",
    "nemt",
    "transportation",
    "veteran",
    "aging",
    "senior",
    "homeless",
    "substance",
    "behavioral",
    "mental health",
    "snap",
    "sdoh",
    "social determin",
    "health disparit",
    "lead",
    "poison",
    "opioid",
    "recovery",
    "meals",
    "housing",
)


def _now_et_label() -> str:
    try:
        from zoneinfo import ZoneInfo

        now = datetime.now(ZoneInfo("America/Detroit"))
    except Exception:
        now = datetime.now()
    return now.strftime("%Y-%m-%d @ %I:%M %p ET").replace(" 0", " ")


def _load_state() -> Dict[str, Any]:
    if not STATE.exists():
        return {}
    try:
        return json.loads(STATE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def _save_state(data: Dict[str, Any]) -> None:
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def _fetch_grants() -> List[Dict[str, Any]]:
    from nexus_backend import AirtableClient
    from gbis_airtable_helpers import (
        classify_grant_entity,
        grant_id_from_fields,
        grant_name_from_fields,
        note_value,
        source_type_from_fields,
    )

    client = AirtableClient()
    rows = client.get_all_records("GRANT OPPORTUNITIES")
    out: List[Dict[str, Any]] = []
    for row in rows:
        fields = row.get("fields", {})
        gid = grant_id_from_fields(fields)
        url = (fields.get("GRANT URL") or fields.get("Grant URL") or "").strip()
        name = grant_name_from_fields(fields)
        funder = (fields.get("FUNDER ORGANIZATION") or fields.get("Funder Organization") or "").strip()
        eligibility = (fields.get("ELIGIBILITY") or fields.get("Eligibility") or "").strip()
        notes = fields.get("NOTES") or ""
        entity = classify_grant_entity(
            title=name,
            funder=funder,
            eligibility=eligibility,
            notes=notes,
        )
        out.append(
            {
                "airtable_id": row.get("id", ""),
                "name": name,
                "funder": funder,
                "url": url,
                "eligibility": eligibility,
                "grant_id": gid,
                "entity": entity,
                "source_type": source_type_from_fields(fields),
                "deadline": note_value(fields, "Deadline"),
                "recommendation": note_value(fields, "Recommendation"),
                "amount_display": _amount_display(fields),
                "is_grants_gov": "grants.gov/search-results-detail" in url.lower(),
                "notes_preview": notes[:400],
            }
        )
    return out


def _amount_display(fields: Dict[str, Any]) -> str:
    from gbis_airtable_helpers import note_value
    from grant_amount_fetcher import parse_amount_display_line

    raw = note_value(fields, "Amount")
    if raw:
        short = parse_amount_display_line(f"Amount: {raw}")
        if short:
            return short
    return "Amount TBD"


def _lane_score(name: str, notes: str = "") -> int:
    text = f"{name} {notes}".lower()
    return sum(1 for kw in DDI_LANE_KEYWORDS if kw in text)


def _entity_rank(entity: str) -> int:
    e = (entity or "").upper()
    if e == "BOTH":
        return 0
    if e == "CWC":
        return 1
    return 2


def _sort_key(row: Dict[str, Any]) -> Tuple[int, int, int, str]:
    entity = _entity_rank(row.get("entity", ""))
    lane = -_lane_score(row.get("name", ""), row.get("notes_preview", ""))
    deadline = row.get("deadline") or "9999-99-99"
    return (entity, lane, 0 if row.get("is_grants_gov") else 1, deadline)


def _format_row(g: Dict[str, Any]) -> str:
    entity = g.get("entity") or "Review"
    score = _lane_score(g.get("name", ""), g.get("notes_preview", ""))
    fit = (
        "Strong lane fit"
        if score >= 2
        else ("Possible fit" if score >= 1 else "Review eligibility")
    )
    amount = g.get("amount_display") or "Amount TBD"
    return (
        f"- **{g['name'][:100]}** — {g['funder'][:50]} | **{amount}** | {fit} | Entity: **{entity}**"
        f" | Deadline: {g['deadline'] or 'TBD'} | [NOFO]({g['url']})"
    )


def compile_grants(backfill_entities: bool = True, backfill_amounts: bool = True) -> Path:
    if backfill_entities:
        try:
            from nexus_backend import AirtableClient
            from gbis_airtable_helpers import backfill_live_grant_entities

            stats = backfill_live_grant_entities(AirtableClient())
            if stats.get("updated"):
                print(
                    f"GBIS entity backfill: {stats['updated']} updated, "
                    f"{stats['skipped']} unchanged, {stats['errors']} errors"
                )
        except Exception as e:
            print(f"GBIS entity backfill skipped: {e}")

    if backfill_amounts:
        try:
            from nexus_backend import AirtableClient
            from gbis_airtable_helpers import backfill_grant_amounts

            amt_stats = backfill_grant_amounts(AirtableClient())
            if amt_stats.get("updated") or amt_stats.get("no_data"):
                print(
                    f"GBIS amount backfill: {amt_stats['updated']} updated, "
                    f"{amt_stats['no_data']} no data, {amt_stats['skipped']} skipped, "
                    f"{amt_stats['errors']} errors"
                )
        except Exception as e:
            print(f"GBIS amount backfill skipped: {e}")

    grants = _fetch_grants()
    prev = _load_state()
    prev_ids = set(prev.get("grant_ids", []))

    live = [g for g in grants if g["is_grants_gov"]]
    tracked = [g for g in grants if not g["is_grants_gov"]]
    live_ids = {g["grant_id"] for g in live if g["grant_id"]}
    new_live = [g for g in live if g["grant_id"] and g["grant_id"] not in prev_ids]

    priority = [g for g in live if g.get("entity") in ("CWC", "BOTH")]
    ddi_only = [g for g in live if g.get("entity") == "DDI"]

    priority_strong = sorted(
        [g for g in priority if _lane_score(g["name"], g["notes_preview"]) >= 1],
        key=_sort_key,
    )
    priority_other = sorted(
        [g for g in priority if _lane_score(g["name"], g["notes_preview"]) < 1],
        key=_sort_key,
    )
    ranked_ddi = sorted(ddi_only, key=_sort_key)

    lines: List[str] = [
        "# GRANTS RESULTS — GBIS Pipeline",
        f"**Last Compiled:** {_now_et_label()}",
        "",
        "## Summary",
        "",
        "| Metric | Count |",
        "|--------|------:|",
        f"| Total in GBIS (Airtable) | {len(grants)} |",
        f"| Live Grants.gov NOFOs | {len(live)} |",
        f"| **CWC / BOTH (apply first)** | **{len(priority)}** |",
        f"| DDI-only (verify eligibility) | {len(ddi_only)} |",
        f"| New since last compile | {len(new_live)} |",
        f"| Tracked platforms / foundations | {len(tracked)} |",
        "",
    ]

    lines += [
        "## Priority — CWC / BOTH + Lane Fit (apply first)",
        "",
        "_Cause We Care primes federal grants. DDI delivers where noted as BOTH. "
        "Amounts are per-award max / program pool — verify eligibility before applying._",
        "",
    ]
    if priority_strong:
        for g in priority_strong[:20]:
            lines.append(_format_row(g))
    else:
        lines.append("_No strong CWC/BOTH lane matches — run `--gbis` to refresh._")
    lines.append("")

    if priority_other:
        lines += [
            "## CWC / BOTH — Weaker Lane Match (still review)",
            "",
        ]
        for g in priority_other[:10]:
            lines.append(_format_row(g))
        lines.append("")

    lines += [
        "## Live Federal — DDI-Only (often ineligible as prime — verify NOFO)",
        "",
    ]
    if ranked_ddi:
        for g in ranked_ddi[:12]:
            lines.append(_format_row(g))
    else:
        lines.append("_None classified DDI-only._")
    lines.append("")

    if new_live:
        new_priority = sorted(
            [g for g in new_live if g.get("entity") in ("CWC", "BOTH")],
            key=_sort_key,
        )[:10]
        if new_priority:
            lines += [
                "## New Since Last Compile (CWC / BOTH only)",
                "",
            ]
            for g in new_priority:
                lines.append(_format_row(g))
            lines.append("")

    lines += [
        "## Tracked Platforms (check manually — not live NOFOs)",
        "",
    ]
    tracked_shown = 0
    for g in sorted(tracked, key=lambda x: x["name"]):
        if not (g.get("name") or "").strip():
            continue
        url = g.get("url") or "https://www.grants.gov"
        lines.append(f"- {g['name'][:80]} — [Link]({url})")
        tracked_shown += 1
        if tracked_shown >= 15:
            break
    lines.append("")

    lines += [
        "## Action Items",
        "",
        "- [ ] Grants.gov saved searches + email alerts (if not set — 15 min at grants.gov)",
        "- [ ] Cause We Care SAM Active → link Grants.gov applicant account",
        "- [ ] Work **Priority — CWC / BOTH** section first — ignore DDI-only unless NOFO allows for-profit",
        "- [ ] Refresh pipeline: `python3 nexus_scheduler.py --gbis`",
        "",
        "---",
        "",
        "_Source: Airtable GRANT OPPORTUNITIES via `compile_grants_results.py`. "
        "Not the same as RADAR (contracts). Ask NEXUS: \"What's in GRANTS RESULTS?\"_",
        "",
    ]

    OUT.write_text("\n".join(lines), encoding="utf-8")

    _save_state(
        {
            "compiled_at": datetime.now().isoformat(),
            "total": len(grants),
            "live_grants_gov": len(live),
            "cwc_both_live": len(priority),
            "ddi_only_live": len(ddi_only),
            "new_live": len(new_live),
            "grant_ids": sorted(live_ids),
        }
    )
    return OUT


if __name__ == "__main__":
    do_backfill = "--no-backfill" not in sys.argv
    no_amounts = "--no-amounts" in sys.argv
    path = compile_grants(backfill_entities=do_backfill, backfill_amounts=do_backfill and not no_amounts)
    print(f"Compiled {path}")
