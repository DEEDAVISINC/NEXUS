"""
JETA_Deals Airtable field names — canonical snake_case (see workspace schema).
Reads fall back to legacy Title Case / older names where older bases still use them.
"""
from __future__ import annotations

from typing import Any, List, Optional, Tuple


class JD:
    """Canonical Airtable field names on JETA_Deals (snake_case)."""

    deal_name = 'deal_name'
    buyer_id = 'buyer_id'
    seller_id = 'seller_id'
    fuel_type = 'fuel_type'
    fuel_product = 'fuel_product'
    volume_gallons = 'volume_gallons'
    volume_frequency = 'volume_frequency'
    price_per_gallon = 'price_per_gallon'
    market_benchmark_ppg = 'market_benchmark_ppg'
    jeta_fee_per_gallon = 'jeta_fee_per_gallon'
    jeta_total_fee = 'jeta_total_fee'
    gross_deal_value = 'gross_deal_value'
    deal_stage = 'deal_stage'
    stage_entered_date = 'stage_entered_date'
    deal_open_date = 'deal_open_date'
    deal_close_date = 'deal_close_date'
    multi_broker_chain = 'multi_broker_chain'
    broker_chain_count = 'broker_chain_count'
    imfpa_required = 'imfpa_required'
    imfpa_total_pct = 'imfpa_total_pct'
    jeta_chain_pct = 'jeta_chain_pct'
    ncnda_status = 'ncnda_status'
    ncnda_signed_date = 'ncnda_signed_date'
    icpo_received = 'icpo_received'
    fco_received = 'fco_received'
    fee_agreement_status = 'fee_agreement_status'
    fee_agreement_signed = 'fee_agreement_signed'
    imfpa_status = 'imfpa_status'
    imfpa_signed_date = 'imfpa_signed_date'
    delivery_confirmed = 'delivery_confirmed'
    payment_status = 'payment_status'
    payment_received_date = 'payment_received_date'
    gate_1_complete = 'gate_1_complete'
    gate_2_complete = 'gate_2_complete'
    gate_3_complete = 'gate_3_complete'
    gate_4_complete = 'gate_4_complete'
    gate_5_complete = 'gate_5_complete'
    gate_6_complete = 'gate_6_complete'
    gate_7_complete = 'gate_7_complete'
    gate_8_complete = 'gate_8_complete'
    fraud_cleared = 'fraud_cleared'
    stale_alert = 'stale_alert'
    last_activity_date = 'last_activity_date'
    notes = 'notes'
    deal_lost_reason = 'deal_lost_reason'
    documents = 'documents'
    outreach_log = 'outreach_log'
    # Fee agreement / escalation (set when Fee Agreement PDF is generated)
    deal_type = 'deal_type'
    term_length = 'term_length'
    escalation_base_benchmark_bbl = 'escalation_base_benchmark_bbl'
    escalation_clause_version = 'escalation_clause_version'


_LEGACY: dict[str, Tuple[str, ...]] = {
    JD.deal_name: ('Deal Name',),
    JD.buyer_id: ('Buyer',),
    JD.seller_id: ('Seller',),
    JD.fuel_type: ('Fuel Type',),
    JD.fuel_product: ('Fuel Product',),
    JD.volume_gallons: ('Volume Gallons',),
    JD.volume_frequency: ('Volume Frequency',),
    JD.price_per_gallon: ('Price Per Gallon',),
    JD.market_benchmark_ppg: ('Market Benchmark PPG', 'IATA Benchmark PPG'),
    JD.jeta_fee_per_gallon: ('JETA Fee Per Gallon',),
    JD.jeta_total_fee: ('Projected Total Fee', 'JETA Total Fee'),
    JD.gross_deal_value: ('Gross Deal Value',),
    JD.deal_stage: ('Deal Stage',),
    JD.stage_entered_date: ('Stage Entered Date',),
    JD.deal_open_date: ('Deal Open Date',),
    JD.deal_close_date: ('Deal Close Date',),
    JD.multi_broker_chain: ('Multiple Brokers In Chain',),
    JD.broker_chain_count: ('Broker Chain Count',),
    JD.imfpa_required: ('IMFPA Required',),
    JD.imfpa_total_pct: ('IMFPA Pct Total',),
    JD.jeta_chain_pct: ('JETA Chain Pct',),
    JD.ncnda_status: ('NCNDA Status',),
    JD.ncnda_signed_date: ('NCNDA Signed Date', 'NCNDA Signed'),
    JD.icpo_received: ('ICPO Received From Buyer',),
    JD.fco_received: ('FCO Received From Seller',),
    JD.fee_agreement_status: ('Fee Agreement Status',),
    JD.fee_agreement_signed: ('Fee Agreement Signed',),
    JD.imfpa_status: ('IMFPA Status',),
    JD.imfpa_signed_date: ('IMFPA Signed Date',),
    JD.delivery_confirmed: ('Fuel Delivery Confirmed',),
    JD.payment_status: ('Payment Status',),
    JD.payment_received_date: ('Payment Received Date', 'Fee Payment Received Date'),
    JD.gate_1_complete: ('Gate 1 Complete',),
    JD.gate_2_complete: ('Gate 2 Complete',),
    JD.gate_3_complete: ('Gate 3 Complete',),
    JD.gate_4_complete: ('Gate 4 Complete',),
    JD.gate_5_complete: ('Gate 5 Complete',),
    JD.gate_6_complete: ('Gate 6 Complete',),
    JD.gate_7_complete: ('Gate 7 Complete',),
    JD.gate_8_complete: ('Gate 8 Complete',),
    JD.fraud_cleared: ('Fraud Cleared',),
    JD.stale_alert: ('Stale Alert',),
    JD.last_activity_date: ('Last Activity Date',),
    JD.notes: ('Deal Description', 'Notes'),
    JD.deal_lost_reason: ('Deal Lost Reason',),
    JD.documents: ('Documents',),
    JD.outreach_log: ('Outreach Log',),
    JD.deal_type: ('Deal Type',),
    JD.term_length: ('Term Length',),
    JD.escalation_base_benchmark_bbl: ('Escalation Base Benchmark Bbl', 'Escalation Base Benchmark ($/bbl)'),
    JD.escalation_clause_version: ('Escalation Clause Version',),
}


def _jd_keys(canonical: str) -> tuple:
    leg = _LEGACY.get(canonical, ())
    return (canonical,) + leg


def jd_get_raw(f: dict, canonical: str) -> Any:
    for k in _jd_keys(canonical):
        if k in f:
            return f.get(k)
    return None


def jd_get_str(f: dict, canonical: str) -> str:
    for k in _jd_keys(canonical):
        if k not in f:
            continue
        v = f[k]
        if v is None:
            continue
        if isinstance(v, (int, float)):
            s = str(int(v) if isinstance(v, float) and v == int(v) else v)
        else:
            s = str(v).strip()
        if s == '':
            continue
        return s
    return ''


def jd_get_float(f: dict, canonical: str) -> Optional[float]:
    for k in _jd_keys(canonical):
        if k not in f or f[k] is None or f[k] == '':
            continue
        try:
            return float(f[k])
        except (TypeError, ValueError):
            continue
    return None


def jd_get_bool(f: dict, canonical: str) -> Optional[bool]:
    for k in _jd_keys(canonical):
        if k not in f or f[k] is None:
            continue
        v = f[k]
        if isinstance(v, bool):
            return v
        if isinstance(v, (int, float)):
            return bool(v)
        s = str(v).strip().lower()
        if s in ('yes', 'true', '1', 'y'):
            return True
        if s in ('no', 'false', '0', 'n'):
            return False
    return None


def jd_link_ids(f: dict, canonical: str) -> List[str]:
    raw = jd_get_raw(f, canonical)
    if raw is None:
        return []
    if isinstance(raw, list):
        return [str(x) for x in raw if x]
    return []


def jd_first_link_id(f: dict, canonical: str) -> str:
    ids = jd_link_ids(f, canonical)
    return ids[0] if ids else ''


def jd_notes_or_description(f: dict) -> str:
    """Primary long text: notes (canonical) or legacy Deal Description / Notes."""
    return jd_get_str(f, JD.notes)
