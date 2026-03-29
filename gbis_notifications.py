"""
GBIS proactive email alerts — Auto-Pursue + DDI/BOTH + deadline window.
Uses SMTP env vars (same pattern as nexus_opportunity_intelligence).
"""
from __future__ import annotations

import json
import os
import smtplib
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from typing import Any, Dict, Optional

from email.mime.multipart import MIMEMultipart

GBIS_ALERT_CACHE = os.path.join(os.path.dirname(__file__), "gbis_alert_sent.json")

SMTP_SERVER = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
EMAIL_FROM = os.environ.get("NEXUS_EMAIL", os.environ.get("EMAIL_FROM", "bids.deedavisinc@gmail.com"))
EMAIL_PASSWORD = os.environ.get("NEXUS_EMAIL_PASSWORD", "")
# User request: default to info@deedavis.biz
GBIS_ALERT_TO = os.environ.get("GBIS_ALERT_EMAIL", "info@deedavis.biz")


def _load_cache() -> dict:
    try:
        if os.path.exists(GBIS_ALERT_CACHE):
            with open(GBIS_ALERT_CACHE, "r") as f:
                return json.load(f)
    except Exception:
        pass
    return {}


def _save_cache(cache: dict) -> None:
    try:
        with open(GBIS_ALERT_CACHE, "w") as f:
            json.dump(cache, f, indent=2)
    except Exception:
        pass


def _parse_deadline(fields: Dict[str, Any]) -> Optional[datetime]:
    raw = str(fields.get("Deadline") or fields.get("deadline") or "").strip()
    if not raw:
        return None
    if "T" in raw:
        raw = raw.split("T")[0]
    elif " " in raw:
        raw = raw.split(" ")[0]
    try:
        from datetime import date as date_cls

        d = date_cls.fromisoformat(raw[:10])
        return datetime(d.year, d.month, d.day)
    except Exception:
        return None


def _within_60_days_or_open(fields: Dict[str, Any]) -> bool:
    """Rolling / no deadline counts as eligible; future deadline must be within 60 days."""
    dt = _parse_deadline(fields)
    if dt is None:
        return True
    days = (dt - datetime.now()).days
    if days < 0:
        return False
    return days <= 60


def _is_auto_pursue(fields: Dict[str, Any]) -> bool:
    rec = (fields.get("Recommendation") or "").strip()
    if rec == "Auto-Pursue":
        return True
    pl = (fields.get("Priority Level") or fields.get("Priority") or "").strip()
    if pl.startswith("Critical"):
        return True
    notes = (fields.get("Notes") or "").lower()
    return "auto-pursue" in notes


def _entity_ok_for_ddi_alert(fields: Dict[str, Any]) -> bool:
    ent = (fields.get("Entity") or fields.get("ENTITY") or "").strip()
    if not ent:
        return True
    if ent == "CWC":
        return False
    return ent in ("DDI", "BOTH")


def notify_if_auto_pursue(record_id: str, fields: Dict[str, Any]) -> None:
    if not _is_auto_pursue(fields):
        return
    if not _entity_ok_for_ddi_alert(fields):
        return
    if not _within_60_days_or_open(fields):
        return

    cache = _load_cache()
    if cache.get(record_id):
        return

    if not EMAIL_PASSWORD:
        return

    name = fields.get("Grant Name") or fields.get("GRANT NAME") or "Grant"
    amount = fields.get("Grant Amount") or fields.get("Max Award Amount") or fields.get("grantAmount") or "See notes"
    deadline = fields.get("Deadline") or "Rolling / see link"
    entity = fields.get("Entity") or "DDI"
    url = fields.get("Grant URL") or fields.get("GRANT URL") or ""
    score = fields.get("Recommendation") or fields.get("Priority Level") or "Auto-Pursue"

    subject = f"[GBIS] Auto-Pursue: {name[:80]}"
    body = f"""GBIS proactive alert (NEXUS)

Grant name: {name}
Amount: {amount}
Deadline: {deadline}
Entity: {entity}
Recommendation / score: {score}
Apply / details: {url}

Record ID: {record_id}
"""

    msg = MIMEMultipart()
    msg["Subject"] = subject
    msg["From"] = EMAIL_FROM
    msg["To"] = GBIS_ALERT_TO
    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL_FROM, EMAIL_PASSWORD)
        server.sendmail(EMAIL_FROM, [GBIS_ALERT_TO], msg.as_string())

    cache[record_id] = {"alerted_at": datetime.now().isoformat(), "grant": name[:120]}
    _save_cache(cache)
