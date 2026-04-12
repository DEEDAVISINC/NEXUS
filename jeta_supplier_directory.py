"""
JETA — airport fuel supplier lookup by ICAO.

The IATA Aviation Energy Hub Supplier Directory (aviation-energy-hub.iata.org) is a
logged-in web application without a public HTTP API, so live directory data cannot be
scraped reliably. This module:

1. Resolves airport name from OurAirports open data (airports.csv).
2. Returns supplier rows from a curated reference map (major airports) — replace/extend
   with your own Airtable rows or a future authenticated IATA integration.
3. Optionally merges cached rows already stored in JETA_SupplierDirectory.

Reference: IATA Fuel program — Supplier Directory description:
https://www.iata.org/en/programs/ops-infra/fuel/
"""

from __future__ import annotations

import csv
import io
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

import requests

from jeta_supplier_directory_schema import JSD

OURAIRPORTS_CSV = "https://ourairports.com/data/airports.csv"
IATA_DIRECTORY_PORTAL = "https://aviation-energy-hub.iata.org/"
IATA_FUEL_PROGRAM_PAGE = "https://www.iata.org/en/programs/ops-infra/fuel/"

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:128.0) "
        "Gecko/20100101 Firefox/128.0"
    ),
}

# Illustrative suppliers for common airports — expand via Airtable or env-driven import.
# fuel_type describes typical supply (CAF = conventional aviation fuel / Jet A).
_CURATED_SUPPLIERS: Dict[str, List[Dict[str, str]]] = {
    "KDTW": [
        {"supplier_name": "Shell Aviation", "fuel_type": "CAF (Jet A / Jet A-1)"},
        {"supplier_name": "Signature Aviation (DTW)", "fuel_type": "Into-plane; CAF"},
        {"supplier_name": "Menzies Aviation", "fuel_type": "Into-plane services; CAF"},
    ],
    "KORD": [
        {"supplier_name": "Shell Aviation", "fuel_type": "CAF (Jet A / Jet A-1)"},
        {"supplier_name": "Air bp", "fuel_type": "CAF"},
        {"supplier_name": "Signature Aviation (ORD)", "fuel_type": "Into-plane; CAF"},
    ],
    "KJFK": [
        {"supplier_name": "Shell Aviation", "fuel_type": "CAF"},
        {"supplier_name": "Air bp", "fuel_type": "CAF"},
        {"supplier_name": "Signature Aviation (JFK)", "fuel_type": "Into-plane; CAF"},
    ],
    "KLAX": [
        {"supplier_name": "Shell Aviation", "fuel_type": "CAF"},
        {"supplier_name": "Air bp", "fuel_type": "CAF"},
        {"supplier_name": "Signature Aviation (LAX)", "fuel_type": "Into-plane; CAF"},
    ],
    "EGLL": [
        {"supplier_name": "Air bp", "fuel_type": "CAF (Jet A-1)"},
        {"supplier_name": "Shell Aviation", "fuel_type": "CAF"},
    ],
    "LFPG": [
        {"supplier_name": "TotalEnergies Aviation", "fuel_type": "CAF / SAF (location-dependent)"},
        {"supplier_name": "Air bp", "fuel_type": "CAF"},
    ],
    "OMDB": [
        {"supplier_name": "Shell Aviation", "fuel_type": "CAF"},
        {"supplier_name": "EPPCO Aviation", "fuel_type": "Into-plane; CAF"},
    ],
}

_airport_cache: Dict[str, Dict[str, str]] = {}
_airport_index: Optional[Dict[str, Dict[str, str]]] = None


def _ensure_airport_index() -> Dict[str, Dict[str, str]]:
    """Load OurAirports CSV once; key by ICAO gps_code / icao_code / ident."""
    global _airport_index
    if _airport_index is not None:
        return _airport_index
    idx: Dict[str, Dict[str, str]] = {}
    try:
        r = requests.get(OURAIRPORTS_CSV, headers=_HEADERS, timeout=90)
        r.raise_for_status()
        reader = csv.DictReader(io.StringIO(r.text))
        for row in reader:
            name = (row.get("name") or "").strip()
            mun = (row.get("municipality") or "").strip()
            for key in (
                (row.get("icao_code") or "").strip().upper(),
                (row.get("gps_code") or "").strip().upper(),
                (row.get("ident") or "").strip().upper(),
            ):
                if key and re.match(r"^[A-Z][A-Z0-9]{3}$", key) and key not in idx:
                    idx[key] = {
                        "icao": key,
                        "name": name or key,
                        "municipality": mun,
                        "iso_country": (row.get("iso_country") or "").strip(),
                        "iso_region": (row.get("iso_region") or "").strip(),
                    }
    except Exception:
        _airport_index = {}
        return _airport_index
    _airport_index = idx
    return _airport_index


def normalize_icao(code: Optional[str]) -> Optional[str]:
    if not code or not isinstance(code, str):
        return None
    c = code.strip().upper()
    if not re.match(r"^[A-Z][A-Z0-9]{3}$", c):
        return None
    return c


def extract_icao_from_text(text: Optional[str]) -> Optional[str]:
    """Pull a 4-char ICAO from free text (e.g. 'Detroit KDTW' or 'KDTW')."""
    if not text or not str(text).strip():
        return None
    s = str(text).strip().upper()
    m = re.search(r"\b([A-Z][A-Z0-9]{3})\b", s)
    return m.group(1) if m else None


def _load_airport_row(icao: str) -> Optional[Dict[str, str]]:
    if icao in _airport_cache:
        return _airport_cache[icao]
    idx = _ensure_airport_index()
    rec = idx.get(icao)
    if rec:
        _airport_cache[icao] = rec
        return rec
    _airport_cache[icao] = {
        "icao": icao,
        "name": icao,
        "municipality": "",
        "iso_country": "",
        "iso_region": "",
    }
    return _airport_cache[icao]


def build_supplier_rows(icao: str, airport_name: str) -> List[Dict[str, Any]]:
    """Return supplier dicts for API + Airtable (supplier_name, fuel_type)."""
    rows: List[Dict[str, Any]] = []
    seen: set = set()
    for item in _CURATED_SUPPLIERS.get(icao, []):
        key = (item.get("supplier_name"), item.get("fuel_type"))
        if key in seen:
            continue
        seen.add(key)
        rows.append(
            {
                "supplier_name": item["supplier_name"],
                "fuel_type": item["fuel_type"],
                "source_note": "NEXUS reference list (verify against IATA Aviation Energy Hub / contracts)",
            }
        )
    return rows


def fetch_iata_context_snippet() -> str:
    """Light touch: confirm IATA fuel program page is reachable (metadata only)."""
    try:
        r = requests.get(IATA_FUEL_PROGRAM_PAGE, headers=_HEADERS, timeout=20)
        if r.status_code == 200 and "Supplier Directory" in (r.text or ""):
            return "IATA Fuel program page reachable; Supplier Directory tool lives on Aviation Energy Hub."
    except Exception as exc:
        return f"IATA page check failed: {exc}"
    return "IATA Fuel program page fetched."


def lookup_suppliers_for_icao(icao_raw: Optional[str]) -> Tuple[Optional[str], Dict[str, Any]]:
    """
    Returns (error_message_or_None, payload) where payload includes:
      icao, airport_name, suppliers[], iata_directory_portal, fuel_program_url, notice
    """
    icao = normalize_icao(icao_raw)
    if not icao:
        return "Invalid or missing ICAO code (expect 4 characters, e.g. KDTW).", {}

    ap = _load_airport_row(icao)
    airport_name = (ap.get("name") if ap else "") or icao
    snippet = fetch_iata_context_snippet()
    suppliers = build_supplier_rows(icao, airport_name)

    iso_region = (ap or {}).get("iso_region") or ""
    iso_country = (ap or {}).get("iso_country") or ""
    mun = (ap or {}).get("municipality") or ""
    state_short = ""
    ir = iso_region.strip().upper()
    if len(ir) >= 5 and ir.startswith("US-"):
        state_short = ir[3:5]
    elif ir:
        state_short = ir

    payload = {
        "icao": icao,
        "airport_name": airport_name,
        "municipality": mun,
        "city": mun,
        "state": state_short,
        "country": iso_country,
        "iso_region": iso_region,
        "suppliers": suppliers,
        "iata_directory_portal": IATA_DIRECTORY_PORTAL,
        "iata_fuel_program_url": IATA_FUEL_PROGRAM_PAGE,
        "notice": (
            "Live IATA Supplier Directory data is served inside the password-protected Aviation Energy Hub; "
            "NEXUS returns OurAirports metadata plus a reference supplier list where curated. "
            + snippet
        ),
    }
    return None, payload


def today_iso_utc() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def fuel_types_offered_list(fuel_type_note: str) -> List[str]:
    """Map curated free-text fuel line → Airtable multiple-select options (Jet-A, SAF, Avgas, Jet A-1)."""
    t = (fuel_type_note or "").lower()
    out: List[str] = []
    if "saf" in t:
        out.append("SAF")
    if "avgas" in t or "100ll" in t or "100 ll" in t:
        out.append("Avgas")
    if "jet a-1" in t or "jet a1" in t or "a-1" in t:
        out.append("Jet A-1")
    if any(x in t for x in ("jet-a", "jet a", "caf", "into-plane", "into plane", "jet fuel")):
        if "Jet A-1" not in out:
            out.append("Jet-A")
    return out or ["Jet-A"]


def infer_branded_program(supplier_name: str) -> str:
    n = (supplier_name or "").lower()
    if "avfuel" in n:
        return "Avfuel"
    if "world fuel" in n:
        return "World Fuel Services"
    if re.search(r"\bair\s*bp\b", n) or "air bp" in n:
        return "Air BP"
    if "phillips" in n and "66" in n:
        return "Phillips 66"
    if re.search(r"\bp66\b", n):
        return "Phillips 66"
    return "Unknown"


def infer_supplier_type(supplier_name: str) -> str:
    if infer_branded_program(supplier_name) != "Unknown":
        return "Major"
    n = (supplier_name or "").lower()
    if "marketer" in n or "marketing" in n:
        return "Regional Marketer"
    return "Independent"


def directory_row_fields_full(
    *,
    icao: str,
    airport_name: str,
    city: str,
    state: str,
    country: str,
    supplier_name: str,
    fuel_type_note: str,
    date_looked_up: str,
    notes: str,
    source: str = "IATA Directory",
) -> Dict[str, Any]:
    """Canonical snake_case + legacy Title Case in one dict (Airtable writes fields that exist)."""
    fts = fuel_types_offered_list(fuel_type_note)
    bp = infer_branded_program(supplier_name)
    st = infer_supplier_type(supplier_name)
    row: Dict[str, Any] = {
        JSD.icao_code: icao,
        "ICAO Code": icao,
        JSD.airport_name: airport_name,
        "Airport Name": airport_name,
        JSD.city: city,
        "City": city,
        JSD.state: state,
        "State": state,
        JSD.country: country,
        "Country": country,
        JSD.supplier_name: supplier_name,
        "Supplier Name": supplier_name,
        JSD.supplier_type: st,
        "Supplier Type": st,
        JSD.fuel_types_offered: fts,
        "Fuel Types Offered": fts,
        JSD.branded_program: bp,
        "Branded Program": bp,
        JSD.open_to_broker: "Unknown",
        "Open To Broker": "Unknown",
        JSD.date_looked_up: date_looked_up,
        "Date Looked Up": date_looked_up,
        JSD.source: source,
        "Source": source,
        "fuel_type": fuel_type_note,
        "Fuel Type": fuel_type_note,
    }
    if notes:
        row[JSD.notes] = notes
        row["Notes"] = notes
    return row


def directory_row_fields_legacy_minimal(
    icao: str,
    airport_name: str,
    supplier_name: str,
    fuel_type: str,
    date_looked_up: str,
) -> Dict[str, Any]:
    """Minimal row for bases that only have the original columns."""
    return {
        JSD.icao_code: icao,
        "ICAO Code": icao,
        JSD.airport_name: airport_name,
        "Airport Name": airport_name,
        JSD.supplier_name: supplier_name,
        "Supplier Name": supplier_name,
        "fuel_type": fuel_type,
        "Fuel Type": fuel_type,
        JSD.date_looked_up: date_looked_up,
        "Date Looked Up": date_looked_up,
    }


def airtable_fields_for_row(
    icao: str,
    airport_name: str,
    supplier_name: str,
    fuel_type: str,
    *,
    date_looked_up: Optional[str] = None,
    city: str = "",
    state: str = "",
    country: str = "",
    notes: str = "",
    source: str = "IATA Directory",
) -> Dict[str, Any]:
    """Backward-compatible name — full dual-write row."""
    return directory_row_fields_full(
        icao=icao,
        airport_name=airport_name,
        city=city,
        state=state,
        country=country,
        supplier_name=supplier_name,
        fuel_type_note=fuel_type,
        date_looked_up=date_looked_up or today_iso_utc(),
        notes=notes,
        source=source,
    )


def airtable_fields_alt_title(
    icao: str,
    airport_name: str,
    supplier_name: str,
    fuel_type: str,
    *,
    date_looked_up: Optional[str] = None,
    city: str = "",
    state: str = "",
    country: str = "",
    notes: str = "",
    source: str = "IATA Directory",
) -> Dict[str, Any]:
    """Same as airtable_fields_for_row (dual-write); kept for callers that expected Title Case."""
    return airtable_fields_for_row(
        icao,
        airport_name,
        supplier_name,
        fuel_type,
        date_looked_up=date_looked_up,
        city=city,
        state=state,
        country=country,
        notes=notes,
        source=source,
    )
