#!/usr/bin/env python3
"""
FleetFlow™ / DDI — CAPE (IEEPA tariff) refund navigator intake
================================================================
POST /fleetflow/cape-intake
  Accepts JSON from the public qualification form, persists the lead,
  runs optional Claude qualification, and emails the admin via Gmail SMTP
  (same credentials as PRISM: NEXUS_EMAIL + NEXUS_EMAIL_PASSWORD).

Not legal or customs-broker advice — operational intake only.
"""

from __future__ import annotations

import json
import os
import re
import smtplib
import threading
import uuid
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any, Dict

from dotenv import load_dotenv
from flask import Blueprint, jsonify, request

load_dotenv()

fleetflow_cape = Blueprint("fleetflow_cape", __name__)

DATA_DIR = os.path.join(os.path.dirname(__file__), "uploads", "fleetflow")
os.makedirs(DATA_DIR, exist_ok=True)
SUBMISSIONS_FILE = os.path.join(DATA_DIR, "cape_intake_submissions.json")

SMTP_SERVER = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
EMAIL_FROM = os.environ.get("NEXUS_EMAIL", "bids.deedavisinc@gmail.com")
EMAIL_PASSWORD = os.environ.get("NEXUS_EMAIL_PASSWORD")
ADMIN_EMAIL = os.environ.get("USER_EMAIL", "info@deedavis.biz")
ANTHROPIC_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
CLAUDE_MODEL = "claude-sonnet-4-20250514"


def _load_submissions() -> list:
    if not os.path.exists(SUBMISSIONS_FILE):
        return []
    try:
        with open(SUBMISSIONS_FILE, "r") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def _save_submissions(rows: list) -> None:
    with open(SUBMISSIONS_FILE, "w") as f:
        json.dump(rows, f, indent=2, default=str)


def _parse_json_blob(text: str) -> Dict[str, Any]:
    text = (text or "").strip()
    m = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if m:
        text = m.group(1).strip()
    return json.loads(text)


def _tariff_band_range(band: str) -> tuple[float | None, float | None]:
    """Return (low, high) USD for IEEPA paid band from intake form."""
    b = (band or "").strip().lower()
    table = {
        "under5k": (500.0, 5000.0),
        "5k-25k": (5000.0, 25000.0),
        "25k-100k": (25000.0, 100000.0),
        "100k-500k": (100000.0, 500000.0),
        "over500k": (500000.0, 2000000.0),
    }
    return table.get(b, (None, None))


def _format_refund_range(low: float | None, high: float | None) -> str:
    if low is None or high is None:
        return "TBD — confirm entry data"
    def fmt(x: float) -> str:
        return f"${x:,.0f}"
    return f"{fmt(low)} – {fmt(high)}"


def _fallback_qualification(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Rule-based summary when Anthropic is unavailable — matches public UI shape."""
    ior_raw = (
        payload.get("importer_of_record")
        or payload.get("is_importer_of_record")
        or ""
    )
    ior = str(ior_raw).lower()
    ior_yes = ior in ("true", "yes", "1", "y")
    ior_unsure = ior in ("unsure", "unknown", "")

    band = (
        payload.get("estimated_tariff_band")
        or payload.get("estimated_tariff")
        or ""
    )
    low_usd, high_usd = _tariff_band_range(str(band))

    est_f = None
    if low_usd is not None and high_usd is not None:
        est_f = (low_usd + high_usd) / 2.0

    if ior_yes:
        eligible: bool | str = True
        headline = "Importer of record — preliminary screen favorable"
        summary = (
            "You indicated your business is the importer of record on CBP entries. "
            "That is required for CAPE IEEPA refund claims. DDI still must verify "
            "entries and IEEPA-assessed duties before any engagement."
        )
        confidence = "medium"
        flags: list[str] = ["Verify IOR on Form 7501 for each entry you intend to include"]
    elif ior_unsure:
        eligible = "conditional"
        headline = "Confirm importer of record before filing"
        summary = (
            "CAPE refunds go to the importer of record. If you are unsure who is listed, "
            "pull your ACE entry summary or ask your customs broker before proceeding."
        )
        confidence = "low"
        flags = ["Confirm who is named as importer of record on relevant entries"]
    else:
        eligible = False
        headline = "Likely not eligible as described"
        summary = (
            "If another entity is the importer of record, that party (or their filer) "
            "must pursue the refund. We can still discuss whether any of your shipments "
            "were in your name."
        )
        confidence = "high"
        flags = ["Re-check CBP entries — IOR must match the refund claimant"]

    fee_pct = 20 if (low_usd is not None and low_usd < 5000) else 15
    if band == "under5k":
        fee_pct = 20

    est_refund = _format_refund_range(low_usd, high_usd) if ior_yes or eligible == "conditional" else "N/A"
    ddi_low = ddi_high = None
    if low_usd is not None and high_usd is not None and (ior_yes or eligible == "conditional"):
        ddi_low = round(low_usd * (fee_pct / 100.0), 0)
        ddi_high = round(high_usd * (fee_pct / 100.0), 0)
        ddi_fee = f"${ddi_low:,.0f} – ${ddi_high:,.0f}"
    else:
        ddi_fee = "TBD"

    urgency = "high" if ior_yes and est_f and est_f >= 25000 else "medium"
    urgency_note = (
        "CBP CAPE Phase 1 is active; completing ACE/ACH and organizing entries early "
        "reduces risk of missing liquidation-related windows. This is general guidance only."
    )

    next_steps = [
        "Confirm ACE Portal access and complete ACH enrollment if not done",
        "Gather entry numbers and IEEPA duty lines (broker or REV-603 report)",
        "Reply to DDI with retainer and signed engagement agreement to proceed",
    ]
    if not ior_yes:
        next_steps[0] = "Confirm importer of record on your CBP entries"

    return {
        "eligible": eligible,
        "confidence": confidence,
        "headline": headline,
        "summary": summary,
        "estimatedRefund": est_refund,
        "feeRate": fee_pct,
        "ddiFee": ddi_fee,
        "flags": flags,
        "nextSteps": next_steps,
        "urgency": urgency,
        "urgencyNote": urgency_note,
        "source": "fallback_rules",
        "disclaimer": "Estimate only — not a guarantee of refund or eligibility.",
    }


def _qualify_with_claude(payload: Dict[str, Any]) -> Dict[str, Any]:
    if not ANTHROPIC_KEY:
        return _fallback_qualification(payload)

    import anthropic

    client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)
    prompt = f"""You assist Dee Davis Inc / FleetFlow (Tariff Refund Navigator) with operational triage for CBP CAPE / IEEPA tariff refund interest only — not Section 232, 301, or 122.

Return ONLY valid JSON (no markdown fences) with this exact shape:
{{
  "eligible": true | false | "conditional",
  "confidence": "high" | "medium" | "low",
  "headline": "short 6-10 word headline",
  "summary": "2-3 sentence plain-English summary",
  "estimatedRefund": "dollar range string like '$5,000 – $25,000' or 'TBD'",
  "feeRate": 15 or 20,
  "ddiFee": "dollar range string for DDI contingency fee",
  "flags": ["1-4 short risks or action items"],
  "nextSteps": ["2-3 concrete next steps"],
  "urgency": "high" | "medium" | "low",
  "urgencyNote": "one sentence on time sensitivity (factual, not alarmist)",
  "disclaimer": "one short line that DDI does not guarantee refunds"
}}

Rules:
- importer_of_record: if "no", eligible should be false; if "unsure", use "conditional"; if "yes", true unless other facts contradict.
- feeRate: 20 if their tariff band is under $5k or they selected under5k; else 15.
- estimatedRefund: derive from estimated_tariff_band / estimated_tariff if present (under5k → roughly $500–$5k style band), else TBD.
- ddiFee: approximate range from estimatedRefund × feeRate.
- Do not promise refunds; preliminary screening only; client remains filer of record.
- nextSteps: ACE Portal, ACH, entry data / CAPE CSV, verify IOR as appropriate.

Submission JSON:
{json.dumps(payload, indent=2, default=str)}
"""

    try:
        resp = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=1200,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = resp.content[0].text
        parsed = _parse_json_blob(raw)
        parsed["source"] = "claude"
        for key in ("feeRate",):
            if key in parsed and isinstance(parsed[key], float):
                parsed[key] = int(parsed[key])
        return parsed
    except Exception:
        return _fallback_qualification(payload)


def _send_intake_email(submission: Dict[str, Any]) -> None:
    if not EMAIL_PASSWORD:
        print("CAPE intake email: NEXUS_EMAIL_PASSWORD not set, skipping")
        return

    sid = submission.get("id", "")
    qual = submission.get("qualification") or {}
    elig = qual.get("eligible", "new")
    subject = f"CAPE intake — {sid} — ELIGIBLE:{str(elig).upper()}"

    lines = [
        "FLEETFLOW / DDI — CAPE TARIFF REFUND INTAKE",
        "=" * 44,
        f"Submission ID: {sid}",
        f"Received:      {submission.get('created_at', '')}",
        "",
        "--- Raw payload (JSON) ---",
        json.dumps(submission.get("payload") or {}, indent=2, default=str),
        "",
        "--- Qualification summary ---",
        json.dumps(qual, indent=2, default=str),
        "",
        f"Submissions file: {SUBMISSIONS_FILE}",
    ]
    body = "\n".join(lines)

    try:
        msg = MIMEMultipart()
        msg["From"] = f"FleetFlow Intake <{EMAIL_FROM}>"
        msg["To"] = ADMIN_EMAIL
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_FROM, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        print(f"CAPE intake email sent to {ADMIN_EMAIL} for {sid}")
    except Exception as e:
        print(f"CAPE intake email failed: {e}")


def _send_intake_email_async(submission: Dict[str, Any]) -> None:
    threading.Thread(target=_send_intake_email, args=(submission,), daemon=True).start()


@fleetflow_cape.route("/fleetflow/cape-intake", methods=["POST"])
def cape_intake():
    data = request.get_json(silent=True) or {}
    if not data:
        return jsonify({"success": False, "error": "JSON body required"}), 400

    now = datetime.utcnow()
    sid = f"CAPE-{now.strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"

    qualification = _qualify_with_claude(data)

    record = {
        "id": sid,
        "created_at": now.isoformat() + "Z",
        "payload": data,
        "qualification": qualification,
    }

    rows = _load_submissions()
    rows.insert(0, record)
    _save_submissions(rows[:2000])

    _send_intake_email_async(record)

    return (
        jsonify(
            {
                "success": True,
                "submission_id": sid,
                "qualification": qualification,
            }
        ),
        201,
    )


@fleetflow_cape.route("/fleetflow/cape-intake/health", methods=["GET"])
def cape_intake_health():
    return jsonify(
        {
            "ok": True,
            "email_configured": bool(EMAIL_PASSWORD),
            "anthropic_configured": bool(ANTHROPIC_KEY),
            "admin_routes_to": ADMIN_EMAIL,
        }
    )
