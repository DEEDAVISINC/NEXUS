#!/usr/bin/env python3
"""
vertex_ai_advisor.py — VERTEX AI Financial Advisor

Runs daily via nexus_scheduler.py. Also callable on-demand via
POST /vertex/ai/advisor (registered in api_server.py).

What it analyzes:
  • Cash position: bank balance + AR - AP = net cash
  • 30/60/90-day cash flow forecast using per-client payment timing
  • Risk alerts: invoice anomalies, cash gaps, sub payment conflicts
  • Margin analysis per service line vs DDI_BUSINESS_MODEL.md targets
  • Collection priority: amount × days × payment history score
  • Payment prediction per client based on historical timing

Output:
  • Returns a structured dict (JSON-serialisable)
  • Appends a spoken-word Alexa snippet to DAILY_BRIEFING.md
  • Appends a ## FINANCIAL SNAPSHOT section to TODAY_AGENDA.md
  • Writes a VERTEX REPORTS record for audit trail
"""

import json
import logging
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv

load_dotenv()

log = logging.getLogger("vertex_ai_advisor")
if not log.handlers:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [vertex_ai_advisor] %(levelname)s %(message)s",
    )

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Margin targets by service type (from DDI_BUSINESS_MODEL.md)
MARGIN_TARGETS = {
    "Drug Testing":    0.35,
    "Fingerprinting":  0.50,
    "DNA Testing":     0.50,
    "NEMT":            0.27,
    "Janitorial":      0.25,
    "Grounds":         0.25,
    "Staffing":        0.30,
    "Freight":         0.30,
    "Consulting":      0.65,
    "Other":           0.25,
}

# How many days past due before a client is considered "slow payer"
SLOW_PAYER_THRESHOLD = 45


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _airtable():
    from nexus_backend import AirtableClient
    return AirtableClient()


def _vi():
    from api_server import VI
    return VI


def _vr():
    from api_server import VR
    return VR


def _ve():
    from api_server import VE
    return VE


def _vap():
    from api_server import VAP
    return VAP


def _today():
    return datetime.now().date()


def _days_since(date_str: str) -> int:
    if not date_str:
        return 0
    try:
        d = datetime.fromisoformat(date_str[:10]).date()
        return (_today() - d).days
    except Exception:
        return 0


def _safe_float(v) -> float:
    try:
        return float(v or 0)
    except Exception:
        return 0.0


# ---------------------------------------------------------------------------
# Data Collection
# ---------------------------------------------------------------------------

def _collect_financial_data(at) -> Dict:
    """Pull all VERTEX tables needed for analysis."""
    VI = _vi(); VR = _vr(); VE = _ve(); VAP = _vap()

    invoices  = at.get_all_records("VERTEX INVOICES")
    revenue   = at.get_all_records("VERTEX REVENUE")
    expenses  = at.get_all_records("VERTEX EXPENSES")

    try:
        ap_bills = at.get_all_records("VERTEX ACCOUNTS PAYABLE")
    except Exception:
        ap_bills = []

    try:
        bank_txns = at.get_all_records("VERTEX BANK TRANSACTIONS")
    except Exception:
        bank_txns = []

    return {
        "invoices":  invoices,
        "revenue":   revenue,
        "expenses":  expenses,
        "ap_bills":  ap_bills,
        "bank_txns": bank_txns,
    }


# ---------------------------------------------------------------------------
# Analysis Functions
# ---------------------------------------------------------------------------

def _cash_position(data: Dict) -> Dict:
    """Calculate current cash position from bank transactions + AR - AP."""
    VR = _vr(); VE = _ve(); VAP = _vap(); VI = _vi()

    # Bank balance from VERTEX BANK TRANSACTIONS (most recent balance field)
    bank_balance = 0.0
    for txn in data["bank_txns"]:
        f = txn.get("fields", {})
        bal = _safe_float(f.get("RUNNING BALANCE") or f.get("BALANCE") or 0)
        if bal:
            bank_balance = bal  # last record wins — assumes sorted by date

    # Outstanding AR
    total_ar = sum(
        _safe_float(inv.get("fields", {}).get(VI["balance_due"]) or
                    inv.get("fields", {}).get(VI["total_amount"], 0))
        for inv in data["invoices"]
        if inv.get("fields", {}).get(VI["payment_status"]) in ("Unpaid", "Partial", "Overdue")
    )

    # Outstanding AP
    total_ap = sum(
        _safe_float(bill.get("fields", {}).get(VAP["total_amount"], 0)) -
        _safe_float(bill.get("fields", {}).get(VAP["amount_paid"], 0) or 0)
        for bill in data["ap_bills"]
        if bill.get("fields", {}).get(VAP["payment_status"]) in ("Unpaid", "Partial")
    )

    net_cash = bank_balance + total_ar - total_ap

    return {
        "bank_balance":  round(bank_balance, 2),
        "total_ar":      round(total_ar, 2),
        "total_ap":      round(total_ap, 2),
        "net_cash":      round(net_cash, 2),
    }


def _cash_flow_forecast(data: Dict) -> Dict:
    """
    30/60/90-day forecast.
    Assume 70% of AR collected in 30 days, 85% in 60, 95% in 90.
    Adjust downward for slow-paying clients.
    """
    VI = _vi(); VAP = _vap()
    today = _today()

    # Identify slow payers (historically pay > SLOW_PAYER_THRESHOLD days)
    slow_payers: set = set()
    for inv in data["invoices"]:
        f = inv.get("fields", {})
        if f.get(VI["payment_status"]) == "Paid":
            days = _safe_float(f.get(VI["days_outstanding"], 0))
            if days > SLOW_PAYER_THRESHOLD:
                slow_payers.add(f.get(VI["client_name"], ""))

    outstanding_ar = []
    for inv in data["invoices"]:
        f = inv.get("fields", {})
        if f.get(VI["payment_status"]) not in ("Unpaid", "Partial", "Overdue"):
            continue
        balance = _safe_float(f.get(VI["balance_due"]) or f.get(VI["total_amount"], 0))
        client  = f.get(VI["client_name"], "")
        is_slow = client in slow_payers
        outstanding_ar.append({"balance": balance, "slow": is_slow})

    def _collect_pct(days_pct: float, slow_adj: float) -> float:
        total = 0.0
        for item in outstanding_ar:
            pct = days_pct * (slow_adj if item["slow"] else 1.0)
            total += item["balance"] * pct
        return round(total, 2)

    # AP payments coming due
    ap_due_30 = sum(
        _safe_float(b.get("fields", {}).get("TOTAL AMOUNT", 0)) - _safe_float(b.get("fields", {}).get("AMOUNT PAID", 0) or 0)
        for b in data["ap_bills"]
        if b.get("fields", {}).get("PAYMENT STATUS") in ("Unpaid", "Partial")
        and _days_since(b.get("fields", {}).get("DUE DATE", "")) > -30
    )

    collected_30 = _collect_pct(0.70, 0.60)
    collected_60 = _collect_pct(0.85, 0.75)
    collected_90 = _collect_pct(0.95, 0.90)

    bank = 0.0
    for txn in data["bank_txns"]:
        f = txn.get("fields", {})
        bal = _safe_float(f.get("RUNNING BALANCE") or f.get("BALANCE") or 0)
        if bal:
            bank = bal

    return {
        "forecast_30_days": round(bank + collected_30 - ap_due_30, 2),
        "forecast_60_days": round(bank + collected_60 - ap_due_30, 2),
        "forecast_90_days": round(bank + collected_90 - ap_due_30, 2),
        "ar_collected_30":  collected_30,
        "ar_collected_60":  collected_60,
        "ar_collected_90":  collected_90,
        "ap_due_30":        round(ap_due_30, 2),
        "slow_payers":      list(slow_payers),
    }


def _risk_alerts(data: Dict) -> List[Dict]:
    """Generate risk alerts for anomalous invoices and cash gaps."""
    VI = _vi(); VAP = _vap()
    alerts = []
    today  = _today()

    # Invoices overdue > 30 days with no follow-up scheduled
    for inv in data["invoices"]:
        f = inv.get("fields", {})
        if f.get(VI["payment_status"]) not in ("Unpaid", "Partial", "Overdue"):
            continue
        due_str = f.get(VI["due_date"], "")
        days_overdue = _days_since(due_str)
        if days_overdue > 30:
            follow_up = f.get(VI.get("follow_up_date", "FOLLOW-UP DATE"), "")
            if not follow_up or _days_since(follow_up) > 0:
                alerts.append({
                    "type":     "overdue_no_followup",
                    "severity": "HIGH" if days_overdue > 60 else "MEDIUM",
                    "message":  f"Invoice {f.get(VI['invoice_number'], inv['id'])} for {f.get(VI['client_name'], '')} is {days_overdue} days overdue with no follow-up scheduled.",
                    "invoice_id": inv["id"],
                    "amount":   _safe_float(f.get(VI["total_amount"], 0)),
                })

    # AP bill due within 5 days but linked client invoice is still unpaid
    for bill in data["ap_bills"]:
        bf = bill.get("fields", {})
        due_str = bf.get(VAP.get("due_date", "DUE DATE"), "")
        if not due_str:
            continue
        try:
            due = datetime.fromisoformat(due_str[:10]).date()
        except Exception:
            continue
        days_to_due = (due - today).days
        if 0 <= days_to_due <= 5:
            vendor  = bf.get(VAP.get("vendor_name", "VENDOR NAME"), "")
            amount  = _safe_float(bf.get(VAP.get("total_amount", "TOTAL AMOUNT"), 0))
            alerts.append({
                "type":     "ap_due_soon_cash_risk",
                "severity": "HIGH",
                "message":  f"AP bill to {vendor} for ${amount:,.2f} is due in {days_to_due} day(s). Verify cash is available.",
                "bill_id":  bill["id"],
                "amount":   amount,
            })

    # Unusually large invoices (> 3x average for that client)
    client_avg: Dict[str, List[float]] = {}
    for inv in data["invoices"]:
        f = inv.get("fields", {})
        client = f.get(VI["client_name"], "")
        amt    = _safe_float(f.get(VI["total_amount"], 0))
        if client and amt > 0:
            client_avg.setdefault(client, []).append(amt)

    for inv in data["invoices"]:
        f = inv.get("fields", {})
        if f.get(VI["payment_status"]) not in ("Unpaid",):
            continue
        client = f.get(VI["client_name"], "")
        amt    = _safe_float(f.get(VI["total_amount"], 0))
        hist   = client_avg.get(client, [])
        if len(hist) >= 3:
            avg = sum(hist) / len(hist)
            if avg > 0 and amt > avg * 3:
                alerts.append({
                    "type":     "anomalous_invoice_amount",
                    "severity": "MEDIUM",
                    "message":  f"Invoice {f.get(VI['invoice_number'], inv['id'])} for {client} is ${amt:,.2f} — 3x their average of ${avg:,.2f}. Verify before sending.",
                    "invoice_id": inv["id"],
                    "amount":   amt,
                })

    return alerts


def _margin_analysis(data: Dict) -> Dict:
    """Compare actual margin per service line against DDI targets."""
    VI = _vi(); VR = _vr(); VE = _ve()

    revenue_by_type: Dict[str, float] = {}
    for rec in data["revenue"]:
        f   = rec.get("fields", {})
        rtype = f.get(VR["revenue_type"], "Other")
        amt   = _safe_float(f.get(VR["amount"], 0))
        revenue_by_type[rtype] = revenue_by_type.get(rtype, 0) + amt

    expense_by_cat: Dict[str, float] = {}
    for rec in data["expenses"]:
        f   = rec.get("fields", {})
        cat = f.get(VE["category"], "Other")
        amt = _safe_float(f.get(VE["amount"], 0))
        expense_by_cat[cat] = expense_by_cat.get(cat, 0) + amt

    total_revenue = sum(revenue_by_type.values())
    total_expense = sum(expense_by_cat.values())
    actual_margin = (total_revenue - total_expense) / total_revenue if total_revenue > 0 else 0

    flags = []
    for service, target in MARGIN_TARGETS.items():
        rev = revenue_by_type.get(service, 0)
        if rev > 0:
            exp = expense_by_cat.get(service, 0) + expense_by_cat.get("Cost of Goods Sold", 0) * (rev / total_revenue)
            actual = (rev - exp) / rev if rev > 0 else 0
            if actual < target * 0.85:
                flags.append({
                    "service":        service,
                    "actual_margin":  round(actual * 100, 1),
                    "target_margin":  round(target * 100, 1),
                    "revenue":        round(rev, 2),
                })

    return {
        "total_revenue":   round(total_revenue, 2),
        "total_expenses":  round(total_expense, 2),
        "actual_margin":   round(actual_margin * 100, 1),
        "below_target_lines": flags,
        "revenue_by_type": {k: round(v, 2) for k, v in revenue_by_type.items()},
    }


def _collection_priority(data: Dict) -> List[Dict]:
    """
    Rank overdue invoices by: amount × days_overdue × (1 / client_payment_score).
    Higher score = collect first.
    """
    VI = _vi()
    today = _today()

    # Build client payment score (lower = slower payer → more urgent)
    client_scores: Dict[str, float] = {}
    for inv in data["invoices"]:
        f = inv.get("fields", {})
        if f.get(VI["payment_status"]) == "Paid":
            client  = f.get(VI["client_name"], "")
            days    = _safe_float(f.get(VI["days_outstanding"], 30))
            existing = client_scores.get(client, days)
            client_scores[client] = (existing + days) / 2  # rolling avg

    priority_list = []
    for inv in data["invoices"]:
        f = inv.get("fields", {})
        if f.get(VI["payment_status"]) not in ("Unpaid", "Partial", "Overdue"):
            continue
        due_str = f.get(VI["due_date"], "")
        try:
            due = datetime.fromisoformat(due_str[:10]).date()
            days_overdue = max(0, (today - due).days)
        except Exception:
            days_overdue = 0

        if days_overdue < 1:
            continue

        amount  = _safe_float(f.get(VI["balance_due"]) or f.get(VI["total_amount"], 0))
        client  = f.get(VI["client_name"], "")
        pay_avg = client_scores.get(client, 30)
        slowness = max(1.0, pay_avg / 30)
        score   = amount * days_overdue * slowness

        priority_list.append({
            "invoice_id":     inv["id"],
            "invoice_number": f.get(VI["invoice_number"], ""),
            "client_name":    client,
            "amount":         round(amount, 2),
            "days_overdue":   days_overdue,
            "priority_score": round(score, 2),
            "action":         "Call directly" if days_overdue > 60 else "Send reminder",
        })

    priority_list.sort(key=lambda x: x["priority_score"], reverse=True)
    return priority_list[:10]


def _payment_prediction(data: Dict) -> List[Dict]:
    """Predict when each outstanding invoice will actually be paid based on client history."""
    VI = _vi()
    today = _today()

    client_avg_days: Dict[str, float] = {}
    for inv in data["invoices"]:
        f = inv.get("fields", {})
        if f.get(VI["payment_status"]) == "Paid":
            client  = f.get(VI["client_name"], "")
            days    = _safe_float(f.get(VI["days_outstanding"], 30))
            existing = client_avg_days.get(client)
            client_avg_days[client] = (existing + days) / 2 if existing else days

    predictions = []
    for inv in data["invoices"]:
        f = inv.get("fields", {})
        if f.get(VI["payment_status"]) not in ("Unpaid", "Partial", "Overdue"):
            continue
        client      = f.get(VI["client_name"], "")
        inv_date    = f.get(VI["invoice_date"], "")
        amount      = _safe_float(f.get(VI["balance_due"]) or f.get(VI["total_amount"], 0))
        avg_days    = client_avg_days.get(client, 35)

        try:
            issued = datetime.fromisoformat(inv_date[:10]).date()
            predicted_payment = issued + timedelta(days=int(avg_days))
            days_until_paid   = max(0, (predicted_payment - today).days)
        except Exception:
            predicted_payment = today + timedelta(days=int(avg_days))
            days_until_paid   = int(avg_days)

        predictions.append({
            "invoice_id":         inv["id"],
            "invoice_number":     f.get(VI["invoice_number"], ""),
            "client_name":        client,
            "amount":             round(amount, 2),
            "predicted_payment_date": predicted_payment.isoformat(),
            "days_until_paid":    days_until_paid,
            "based_on_avg_days":  round(avg_days, 0),
        })

    predictions.sort(key=lambda x: x["predicted_payment_date"])
    return predictions[:15]


# ---------------------------------------------------------------------------
# AI Narrative (Anthropic)
# ---------------------------------------------------------------------------

def _ai_narrative(summary: Dict) -> str:
    """Use Claude to write a 3-5 sentence financial health summary."""
    try:
        from nexus_backend import AnthropicClient
        ai = AnthropicClient()

        cash    = summary.get("cash_position", {})
        alerts  = summary.get("risk_alerts", [])
        prio    = summary.get("collection_priority", [])
        margin  = summary.get("margin_analysis", {})

        top_prio = prio[0] if prio else {}
        hi_alerts = [a for a in alerts if a.get("severity") == "HIGH"]

        prompt = f"""You are Dee Davis Inc's financial advisor. Write a 4-sentence daily financial briefing for Dee (President & CEO).

Data:
- Net cash position: ${cash.get('net_cash', 0):,.2f}
- Total AR outstanding: ${cash.get('total_ar', 0):,.2f}
- Total AP outstanding: ${cash.get('total_ap', 0):,.2f}
- Overall margin: {margin.get('actual_margin', 0):.1f}%
- High-severity alerts: {len(hi_alerts)}
- Top collection priority: {top_prio.get('client_name', 'None')} — ${top_prio.get('amount', 0):,.2f} ({top_prio.get('days_overdue', 0)} days overdue)
- Below-target service lines: {len(margin.get('below_target_lines', []))}

Rules:
- Be direct, grounded, no cheerleader energy
- Start with the cash reality
- Mention the top collection action if any
- Flag any high alerts
- Keep it under 80 words
- Plain text only, no markdown"""

        return ai.complete(prompt, max_tokens=200).strip()
    except Exception as e:
        log.warning(f"AI narrative failed: {e}")
        return ""


# ---------------------------------------------------------------------------
# Main Advisor Function
# ---------------------------------------------------------------------------

def run_vertex_ai_advisor() -> Dict:
    """
    Run the full AI financial advisor analysis.
    Returns a complete analysis dict and updates DAILY_BRIEFING.md + TODAY_AGENDA.md.
    """
    log.info("=== VERTEX AI ADVISOR — Starting analysis ===")
    at = _airtable()

    data     = _collect_financial_data(at)
    cash     = _cash_position(data)
    forecast = _cash_flow_forecast(data)
    alerts   = _risk_alerts(data)
    margin   = _margin_analysis(data)
    priority = _collection_priority(data)
    predict  = _payment_prediction(data)

    high_alerts = [a for a in alerts if a.get("severity") == "HIGH"]
    top         = priority[0] if priority else {}

    summary = {
        "generated_at":      datetime.now().isoformat(),
        "cash_position":     cash,
        "cash_flow_forecast": forecast,
        "risk_alerts":       alerts,
        "high_alerts_count": len(high_alerts),
        "margin_analysis":   margin,
        "collection_priority": priority,
        "payment_predictions": predict,
    }

    # AI narrative
    narrative = _ai_narrative(summary)
    summary["ai_narrative"] = narrative

    # Write audit record to VERTEX REPORTS
    try:
        at.create_record("VERTEX REPORTS", {
            "REPORT DATE":   datetime.now().date().isoformat(),
            "REPORT TYPE":   "AI Financial Advisor",
            "SOURCE SYSTEM": "VERTEX",
            "DETAILS":       json.dumps({
                "cash":     cash,
                "alerts":   len(alerts),
                "hi_alerts": len(high_alerts),
                "margin":   margin.get("actual_margin"),
                "top_prio": top.get("client_name"),
            }, default=str)[:5000],
            "OUTCOME":       "success",
            "GENERATED BY":  "vertex_ai_advisor.py",
        })
    except Exception as e:
        log.warning(f"Could not write VERTEX REPORTS audit: {e}")

    # Update DAILY_BRIEFING.md (Alexa reads this)
    _update_daily_briefing(summary)

    # Update TODAY_AGENDA.md (financial snapshot section)
    _update_today_agenda(summary)

    log.info(f"=== VERTEX AI ADVISOR — Done. Cash: ${cash['net_cash']:,.2f} | Alerts: {len(alerts)} | Priority: {top.get('client_name', 'None')} ===")
    return summary


# ---------------------------------------------------------------------------
# File Writers
# ---------------------------------------------------------------------------

def _update_daily_briefing(summary: Dict):
    """Append financial snapshot to DAILY_BRIEFING.md for Alexa."""
    briefing_path = os.path.join(BASE_DIR, "DAILY_BRIEFING.md")
    cash     = summary.get("cash_position", {})
    fc       = summary.get("cash_flow_forecast", {})
    alerts   = summary.get("risk_alerts", [])
    priority = summary.get("collection_priority", [])
    narrative = summary.get("ai_narrative", "")
    top = priority[0] if priority else {}

    ar      = cash.get("total_ar", 0)
    ap      = cash.get("total_ap", 0)
    net     = cash.get("net_cash", 0)
    fc30    = fc.get("forecast_30_days", 0)
    hi_cnt  = sum(1 for a in alerts if a.get("severity") == "HIGH")

    snippet = (
        f"\n\n---\n"
        f"## FINANCIAL SNAPSHOT — {datetime.now().strftime('%B %d, %Y')}\n\n"
        f"Net cash position: ${net:,.2f}. "
        f"Receivables outstanding: ${ar:,.2f}. "
        f"Payables outstanding: ${ap:,.2f}. "
    )
    if hi_cnt:
        snippet += f"{hi_cnt} high-priority alert(s) require attention. "
    if top:
        snippet += (
            f"Top collection priority: {top.get('client_name')}, "
            f"${top.get('amount', 0):,.2f}, {top.get('days_overdue', 0)} days overdue. "
        )
    snippet += f"30-day cash forecast: ${fc30:,.2f}."
    if narrative:
        snippet += f"\n\n{narrative}"

    try:
        existing = open(briefing_path, "r", encoding="utf-8").read() if os.path.exists(briefing_path) else ""
        # Remove old snapshot section if present
        marker = "## FINANCIAL SNAPSHOT —"
        if marker in existing:
            existing = existing[:existing.index(marker)].rstrip()
        with open(briefing_path, "w", encoding="utf-8") as fh:
            fh.write(existing + snippet + "\n")
        log.info("DAILY_BRIEFING.md updated with financial snapshot")
    except Exception as e:
        log.warning(f"Could not update DAILY_BRIEFING.md: {e}")


def _update_today_agenda(summary: Dict):
    """Write/replace ## FINANCIAL SNAPSHOT section in TODAY_AGENDA.md."""
    agenda_path = os.path.join(BASE_DIR, "TODAY_AGENDA.md")
    cash     = summary.get("cash_position", {})
    fc       = summary.get("cash_flow_forecast", {})
    priority = summary.get("collection_priority", [])
    alerts   = summary.get("risk_alerts", [])
    margin   = summary.get("margin_analysis", {})

    lines = [
        f"\n\n---\n## FINANCIAL SNAPSHOT — {datetime.now().strftime('%Y-%m-%d %H:%M')}\n",
        f"| Metric | Value |",
        f"|---|---|",
        f"| Net Cash Position | ${cash.get('net_cash', 0):,.2f} |",
        f"| Total AR Outstanding | ${cash.get('total_ar', 0):,.2f} |",
        f"| Total AP Outstanding | ${cash.get('total_ap', 0):,.2f} |",
        f"| Bank Balance | ${cash.get('bank_balance', 0):,.2f} |",
        f"| Overall Margin | {margin.get('actual_margin', 0):.1f}% |",
        f"| 30-Day Cash Forecast | ${fc.get('forecast_30_days', 0):,.2f} |",
        f"| 60-Day Cash Forecast | ${fc.get('forecast_60_days', 0):,.2f} |",
        f"| High Alerts | {sum(1 for a in alerts if a.get('severity') == 'HIGH')} |",
        "",
    ]

    if priority:
        lines += ["### COLLECTION PRIORITY (Top 5)", ""]
        for i, item in enumerate(priority[:5], 1):
            lines.append(
                f"{i}. **{item['client_name']}** — ${item['amount']:,.2f} "
                f"({item['days_overdue']} days overdue) → {item['action']}"
            )
        lines.append("")

    hi_alerts = [a for a in alerts if a.get("severity") == "HIGH"]
    if hi_alerts:
        lines += ["### HIGH-PRIORITY ALERTS", ""]
        for alert in hi_alerts:
            lines.append(f"- ⚠️ {alert['message']}")
        lines.append("")

    below = margin.get("below_target_lines", [])
    if below:
        lines += ["### BELOW-TARGET MARGIN LINES", ""]
        for bl in below:
            lines.append(
                f"- **{bl['service']}**: {bl['actual_margin']}% actual vs {bl['target_margin']}% target "
                f"(Revenue: ${bl['revenue']:,.2f})"
            )
        lines.append("")

    section = "\n".join(lines)

    try:
        existing = open(agenda_path, "r", encoding="utf-8").read() if os.path.exists(agenda_path) else ""
        marker = "## FINANCIAL SNAPSHOT —"
        if marker in existing:
            existing = existing[:existing.index(marker)].rstrip()
        with open(agenda_path, "w", encoding="utf-8") as fh:
            fh.write(existing + section + "\n")
        log.info("TODAY_AGENDA.md updated with financial snapshot")
    except Exception as e:
        log.warning(f"Could not update TODAY_AGENDA.md: {e}")
