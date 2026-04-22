#!/usr/bin/env python3
"""
NEXUS PRICING INTELLIGENCE
=============================
Unified pricing brain that connects CLIN parsing, market benchmarks,
historical data, markup recommendations, and learning feedback.

Feeds into:
  - Evaluator Scoring Engine (Price factor gets real data, not keyword matching)
  - Learning Engine (pricing outcomes tracked for continuous improvement)
  - Bid Workflow (auto-CLIN extraction and pricing validation)

Uses:
  - subcontractor_quote_validator.py → Market rate benchmarks
  - historical_pricing_scraper.py → USASpending historical data
  - multi_year_pricing_calculator.py → Base + option year math
  - service_labor_rate_calculator.py → Fully burdened rates
  - nexus_learning_engine.py → Outcome-based markup optimization
"""

import re
import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
from dotenv import load_dotenv

load_dotenv()

# ─── MARKET BENCHMARKS (imported from sub quote validator) ───────────────────

try:
    from subcontractor_quote_validator import MARKET_RATE_BENCHMARKS
except ImportError:
    MARKET_RATE_BENCHMARKS = {}

# ─── SERVICE LANE KEYWORD MAPPING ───────────────────────────────────────────

SERVICE_LANE_KEYWORDS = {
    'notary_credentialing': [
        'notary', 'notarization', 'mobile notary', 'RON', 'remote online notarization',
        'signing agent', 'loan signing', 'document authentication', 'apostille',
        'witness', 'witnessing', 'credentialing', 'provider credentialing', 'PSV',
        'primary source verification', 'enrollment and credentialing',
    ],
    'drug_testing_per_test': [
        'drug test', 'drug testing', 'drug and alcohol testing', 'drug screen', 'substance abuse', 'urine test',
        'DOT testing', 'DOT drug', 'workplace drug testing', 'occupational drug testing',
        'SAMHSA', 'C/TPA', 'consortium', 'Part 40', '49 CFR Part 40',
        'chain of custody', 'specimen collection',
        'alcohol testing', 'oral fluid', 'breathalyzer', 'BAT',
        'pre-employment', 'random testing', 'post-accident',
    ],
    'fingerprinting_per_person': [
        'fingerprint', 'fingerprinting', 'livescan', 'live scan', 'biometrics', 'biometric',
        'electronic fingerprinting', 'background check',
        'FBI check', 'identity verification', 'FD-258',
    ],
    'medical_courier_ohio': [
        'medical courier', 'healthcare logistics', 'specimen transport', 'lab transport',
        'biological specimen', 'temperature controlled', 'IATA',
        'medical delivery', 'pathology transport',
    ],
    'nemt_per_mile': [
        'non-emergency medical transport', 'non-emergency medical transportation',
        'NEMT', 'medical transport', 'medical transportation',
        'patient transport', 'patient transportation',
        'wheelchair transport', 'stretcher transport', 'ambulatory transport',
        'Medicaid transport', 'Medicaid transportation', 'paratransit',
        'special needs transportation',
    ],
    'grounds_maintenance_per_acre': [
        'grounds maintenance', 'landscaping', 'lawn care', 'mowing',
        'snow removal', 'turf management', 'tree trimming', 'weed control',
    ],
    'janitorial_per_sqft': [
        'janitorial', 'custodial', 'cleaning service', 'building maintenance',
        'floor care', 'restroom service', 'sanitation',
    ],
    'shuttle_per_hour': [
        'shuttle service', 'passenger transport', 'vehicle service',
        'driver service', 'transportation service',
    ],
}

# ─── DEFAULT MARKUP RECOMMENDATIONS ─────────────────────────────────────────

DEFAULT_MARKUP_RANGES = {
    'products': {
        'aggressive': {'min': 10, 'max': 15, 'label': 'Win on price'},
        'competitive': {'min': 15, 'max': 22, 'label': 'Balanced'},
        'premium': {'min': 22, 'max': 30, 'label': 'Maximize margin'},
    },
    'services_subcontracted': {
        'aggressive': {'min': 8, 'max': 12, 'label': 'Win on price'},
        'competitive': {'min': 12, 'max': 18, 'label': 'Balanced'},
        'premium': {'min': 18, 'max': 25, 'label': 'Maximize margin'},
    },
    'services_direct': {
        'aggressive': {'min': 20, 'max': 30, 'label': 'Win on price'},
        'competitive': {'min': 30, 'max': 40, 'label': 'Balanced'},
        'premium': {'min': 40, 'max': 55, 'label': 'Maximize margin'},
    },
}

EVAL_METHOD_MARKUP_ADJUSTMENT = {
    'lpta': -5,
    'best_value': 0,
    'highest_rated': +3,
}

# ─── CLIN PARSING ───────────────────────────────────────────────────────────

CLIN_PATTERNS = [
    # "CLIN 0001" or "CLIN 0001:" or "CLIN 0001 -"
    r'CLIN\s*(\d{3,4})\s*[-:.]?\s*(.+?)(?=\n|CLIN\s*\d|$)',
    # "Item 0001" or "Item No. 0001"
    r'Item\s*(?:No\.?\s*)?(\d{3,4})\s*[-:.]?\s*(.+?)(?=\n|Item\s|$)',
    # "B.1.1" or "B-1" section references
    r'B[.-](\d+(?:\.\d+)?)\s*[-:.]?\s*(.+?)(?=\n|B[.-]\d|$)',
    # "0001 | Description" (table format)
    r'(\d{4})\s*\|\s*(.+?)(?=\n|\d{4}\s*\|)',
    # "Line Item 1:" or "Line 1."
    r'Line\s*(?:Item\s*)?(\d+)\s*[:.]\s*(.+?)(?=\n|Line\s|$)',
]

QUANTITY_PATTERN = r'(?:est(?:imated)?\.?\s*)?(?:qty|quantity|volume)[:\s]*(\d[\d,]*)'
UNIT_PATTERN = r'\b(each|ea|lot|hour|hr|month|mo|year|yr|mile|test|person|trip|shipment|sqft|sq\s*ft|acre|per\s+\w+)\b'
PRICING_TYPE_PATTERN = r'\b(FFP|firm[- ]fixed[- ]price|T&M|time\s*(?:and|&)\s*materials?|cost[- ]plus|cost\s*reimburs|IDIQ|indefinite\s*delivery)\b'

OPTION_YEAR_PATTERNS = [
    r'(base\s*year|option\s*year\s*\d|option\s*period\s*\d)',
    r'(base\s*period|option\s*period)',
    r'(year\s*(?:one|two|three|four|five|1|2|3|4|5))',
]


class PricingIntelligence:
    """
    Unified pricing brain for NEXUS.

    Responsibilities:
      1. Parse CLINs from RFP Section B
      2. Detect service type and pull market benchmarks
      3. Recommend markup ranges based on contract type and learning data
      4. Validate proposal pricing against RFP requirements
      5. Score the Price evaluation factor for the evaluator engine
      6. Track pricing outcomes for the learning loop
    """

    def __init__(self):
        self._learning = None

    def _get_learning(self):
        if self._learning is None:
            try:
                from nexus_learning_engine import get_engine
                self._learning = get_engine()
            except Exception:
                pass
        return self._learning

    # ─── 1. CLIN PARSING ────────────────────────────────────────────────────

    def parse_clins(self, rfp_text: str) -> Dict:
        """
        Extract CLINs from RFP Section B text.
        Returns structured CLIN data with quantities, units, and pricing type.
        """
        clins = []
        seen_ids = set()

        for pattern in CLIN_PATTERNS:
            matches = re.findall(pattern, rfp_text, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                clin_id = match[0].strip()
                description = match[1].strip()[:200]

                if clin_id in seen_ids:
                    continue
                if len(description) < 3:
                    continue

                seen_ids.add(clin_id)

                quantity = None
                qty_match = re.search(QUANTITY_PATTERN, description, re.IGNORECASE)
                if qty_match:
                    quantity = int(qty_match.group(1).replace(',', ''))

                unit = None
                unit_match = re.search(UNIT_PATTERN, description, re.IGNORECASE)
                if unit_match:
                    unit = unit_match.group(1).lower()

                clins.append({
                    'clin_id': clin_id,
                    'description': description,
                    'quantity': quantity,
                    'unit': unit,
                })

        pricing_type = self._detect_pricing_type(rfp_text)
        option_years = self._detect_option_years(rfp_text)
        contract_duration = self._estimate_duration(rfp_text, option_years)

        return {
            'clins': clins,
            'clin_count': len(clins),
            'pricing_type': pricing_type,
            'option_years': option_years,
            'contract_duration_years': contract_duration,
            'has_base_plus_options': option_years > 0,
        }

    def _detect_pricing_type(self, rfp_text: str) -> str:
        text_lower = rfp_text.lower()
        for match in re.finditer(PRICING_TYPE_PATTERN, text_lower):
            term = match.group(1)
            if 'ffp' in term or 'firm' in term:
                return 'firm_fixed_price'
            elif 't&m' in term or 'time' in term:
                return 'time_and_materials'
            elif 'cost' in term:
                return 'cost_plus'
            elif 'idiq' in term or 'indefinite' in term:
                return 'idiq'
        return 'unknown'

    def _detect_option_years(self, rfp_text: str) -> int:
        text_lower = rfp_text.lower()
        max_option = 0
        for pattern in OPTION_YEAR_PATTERNS:
            matches = re.findall(pattern, text_lower)
            for match in matches:
                m = match if isinstance(match, str) else match
                nums = re.findall(r'(\d)', m)
                if nums:
                    max_option = max(max_option, max(int(n) for n in nums))
                elif 'one' in m:
                    max_option = max(max_option, 1)
                elif 'two' in m:
                    max_option = max(max_option, 2)
                elif 'three' in m:
                    max_option = max(max_option, 3)
                elif 'four' in m:
                    max_option = max(max_option, 4)
                elif 'five' in m:
                    max_option = max(max_option, 5)
        return max_option

    def _estimate_duration(self, rfp_text: str, option_years: int) -> int:
        if option_years > 0:
            return 1 + option_years
        duration_match = re.search(r'(\d+)\s*(?:year|yr)', rfp_text, re.IGNORECASE)
        if duration_match:
            return int(duration_match.group(1))
        month_match = re.search(r'(\d+)\s*month', rfp_text, re.IGNORECASE)
        if month_match:
            months = int(month_match.group(1))
            return max(1, months // 12)
        return 1

    # ─── 2. SERVICE TYPE DETECTION + MARKET BENCHMARKS ───────────────────────

    def detect_service_type(self, rfp_text: str) -> Optional[str]:
        """Detect DDI service lane from RFP text."""
        text_lower = rfp_text.lower()
        best_match = None
        best_count = 0

        for service_key, keywords in SERVICE_LANE_KEYWORDS.items():
            hits = sum(1 for kw in keywords if kw.lower() in text_lower)
            if hits > best_count:
                best_count = hits
                best_match = service_key

        if best_count >= 2:
            return best_match
        return None

    def get_market_benchmarks(self, service_type: str = None, rfp_text: str = '') -> Dict:
        """Get market rate benchmarks for a service type."""
        if not service_type and rfp_text:
            service_type = self.detect_service_type(rfp_text)

        if not service_type or service_type not in MARKET_RATE_BENCHMARKS:
            return {
                'available': False,
                'service_type': service_type,
                'message': 'No benchmark data for this service type',
                'available_types': list(MARKET_RATE_BENCHMARKS.keys()),
            }

        benchmark = MARKET_RATE_BENCHMARKS[service_type]
        return {
            'available': True,
            'service_type': service_type,
            'unit': benchmark['unit'],
            'low': benchmark['low'],
            'typical': benchmark['typical'],
            'high': benchmark['high'],
            'notes': benchmark.get('notes', ''),
        }

    # ─── 3. MARKUP RECOMMENDATIONS ──────────────────────────────────────────

    def recommend_markup(
        self,
        contract_type: str = 'services_subcontracted',
        eval_method: str = 'best_value',
        set_aside: str = '',
        service_type: str = None,
    ) -> Dict:
        """
        Recommend markup range based on contract type, evaluation method,
        and learned outcomes.
        """
        base_range = DEFAULT_MARKUP_RANGES.get(
            contract_type, DEFAULT_MARKUP_RANGES['services_subcontracted']
        )

        adjustment = EVAL_METHOD_MARKUP_ADJUSTMENT.get(eval_method, 0)

        set_aside_lower = (set_aside or '').lower()
        if 'edwosb' in set_aside_lower or 'wosb' in set_aside_lower:
            adjustment += 2
        elif 'small business' in set_aside_lower:
            adjustment += 1

        scenarios = {}
        for key, rng in base_range.items():
            scenarios[key] = {
                'min': rng['min'] + adjustment,
                'max': rng['max'] + adjustment,
                'label': rng['label'],
            }

        recommended = 'competitive'
        if eval_method == 'lpta':
            recommended = 'aggressive'
        elif eval_method == 'highest_rated':
            recommended = 'premium'

        result = {
            'recommended_scenario': recommended,
            'recommended_range': scenarios[recommended],
            'scenarios': scenarios,
            'contract_type': contract_type,
            'eval_method': eval_method,
            'adjustments_applied': [],
        }

        if adjustment != 0:
            if 'edwosb' in set_aside_lower or 'wosb' in set_aside_lower:
                result['adjustments_applied'].append('EDWOSB/WOSB set-aside: +2% (less price competition)')
            if eval_method == 'lpta':
                result['adjustments_applied'].append('LPTA evaluation: -5% (price is decisive)')
            elif eval_method == 'highest_rated':
                result['adjustments_applied'].append('Highest Rated: +3% (technical outweighs price)')

        learned = self._get_learned_markup_insights(service_type)
        if learned:
            result['learned_insights'] = learned

        return result

    def _get_learned_markup_insights(self, service_type: str = None) -> Optional[Dict]:
        """Pull markup insights from the learning engine."""
        engine = self._get_learning()
        if not engine:
            return None

        try:
            weights = engine.get_weights('pricing')
            history = engine._db.get('events', {}).get('pricing', [])

            if not history:
                return None

            markups_won = []
            markups_lost = []
            for event in history:
                meta = event.get('metadata', {})
                markup = meta.get('markup_pct')
                action = event.get('action', '')
                if markup:
                    markup = float(markup)
                    if action == 'price_won':
                        markups_won.append(markup)
                    elif action == 'price_lost':
                        markups_lost.append(markup)

            if not markups_won and not markups_lost:
                return None

            return {
                'data_points': len(markups_won) + len(markups_lost),
                'avg_winning_markup': round(sum(markups_won) / len(markups_won), 1) if markups_won else None,
                'avg_losing_markup': round(sum(markups_lost) / len(markups_lost), 1) if markups_lost else None,
                'insight': self._format_markup_insight(markups_won, markups_lost),
            }
        except Exception:
            return None

    def _format_markup_insight(self, won: List[float], lost: List[float]) -> str:
        if won and lost:
            avg_w = sum(won) / len(won)
            avg_l = sum(lost) / len(lost)
            if avg_l > avg_w:
                return f'Winning bids averaged {avg_w:.0f}% markup vs {avg_l:.0f}% for losses. Consider pricing toward {avg_w:.0f}%.'
            else:
                return f'No clear markup pattern yet ({len(won)} wins, {len(lost)} losses). Keep logging outcomes.'
        elif won:
            avg_w = sum(won) / len(won)
            return f'Winning markup averages {avg_w:.0f}% across {len(won)} bids.'
        elif lost:
            avg_l = sum(lost) / len(lost)
            return f'Lost bids averaged {avg_l:.0f}% markup. Consider pricing lower.'
        return 'No pricing outcome data yet.'

    # ─── 4. PRICE FACTOR SCORING (for Evaluator Engine) ─────────────────────

    def score_price_factor(self, proposal_text: str, rfp_text: str = '') -> Dict:
        """
        Intelligent Price factor scoring for the evaluator engine.
        Replaces generic keyword matching with real pricing analysis.
        """
        text_lower = proposal_text.lower()
        rfp_lower = rfp_text.lower() if rfp_text else ''

        # Parse CLINs from RFP
        rfp_clins = self.parse_clins(rfp_text) if rfp_text else {'clins': [], 'clin_count': 0}
        service_type = self.detect_service_type(rfp_text or proposal_text)
        benchmarks = self.get_market_benchmarks(service_type) if service_type else {'available': False}

        scores = {
            'clin_coverage': 0,
            'pricing_structure': 0,
            'pricing_format': 0,
            'option_year_handling': 0,
            'rate_reasonableness': 0,
        }
        strengths = []
        weaknesses = []
        improvement_actions = []
        subfactor_assessments = []

        # ─── SUBFACTOR 1: CLIN Coverage ─────────────────────────────
        if rfp_clins['clins']:
            clins_addressed = 0
            for clin in rfp_clins['clins']:
                clin_id = clin['clin_id']
                desc_words = [w for w in clin['description'].lower().split() if len(w) > 3][:5]
                id_found = clin_id in text_lower or clin_id.lstrip('0') in text_lower
                desc_found = sum(1 for w in desc_words if w in text_lower) >= max(len(desc_words) // 2, 1)
                if id_found or desc_found:
                    clins_addressed += 1

            coverage_pct = (clins_addressed / len(rfp_clins['clins'])) * 100
            scores['clin_coverage'] = min(coverage_pct, 100)
            subfactor_assessments.append({
                'subfactor': f'CLIN Coverage ({clins_addressed}/{len(rfp_clins["clins"])})',
                'addressed': coverage_pct >= 80,
                'strength': f'{clins_addressed} of {len(rfp_clins["clins"])} CLINs addressed' if coverage_pct >= 80 else f'Missing {len(rfp_clins["clins"]) - clins_addressed} CLINs',
            })
            if coverage_pct >= 90:
                strengths.append(f'All {len(rfp_clins["clins"])} CLINs addressed in pricing')
            elif coverage_pct >= 60:
                weaknesses.append(f'Only {clins_addressed}/{len(rfp_clins["clins"])} CLINs covered')
                improvement_actions.append(f'Add pricing for missing CLINs: {", ".join(c["clin_id"] for c in rfp_clins["clins"])}')
            else:
                weaknesses.append(f'Major CLIN gap: only {clins_addressed}/{len(rfp_clins["clins"])} addressed — evaluator may reject as non-responsive')
                improvement_actions.append('Review Section B and price ALL line items — missing CLINs = automatic rejection')
        else:
            scores['clin_coverage'] = 50
            subfactor_assessments.append({
                'subfactor': 'CLIN Coverage',
                'addressed': True,
                'strength': 'No CLINs parsed from RFP — using general pricing assessment',
            })

        # ─── SUBFACTOR 2: Pricing Structure ─────────────────────────
        has_unit_prices = bool(re.search(r'\$\s*[\d,.]+\s*(?:per|/)\s*\w+', proposal_text, re.IGNORECASE))
        has_totals = bool(re.search(r'total[:\s]*\$\s*[\d,.]+', proposal_text, re.IGNORECASE))
        has_line_items = bool(re.search(r'(?:item|line|clin)\s*\d', proposal_text, re.IGNORECASE))
        has_pricing_table = bool(re.search(r'unit\s*price|extended\s*price|total\s*price', proposal_text, re.IGNORECASE))
        has_dollar_amounts = len(re.findall(r'\$\s*[\d,]+(?:\.\d{2})?', proposal_text))

        structure_score = 0
        if has_unit_prices:
            structure_score += 30
            strengths.append('Unit pricing provided')
        if has_totals:
            structure_score += 20
        if has_line_items:
            structure_score += 25
            strengths.append('Line item pricing structure')
        if has_pricing_table:
            structure_score += 25
            strengths.append('Pricing table format used')

        if has_dollar_amounts < 2:
            weaknesses.append('No dollar amounts found — pricing volume appears empty')
            improvement_actions.append('Add specific dollar amounts for each CLIN/line item')

        scores['pricing_structure'] = min(structure_score, 100)
        subfactor_assessments.append({
            'subfactor': 'Pricing Structure',
            'addressed': structure_score >= 50,
            'strength': 'Structured pricing with unit prices and totals' if structure_score >= 50 else 'Pricing lacks structure',
        })

        # ─── SUBFACTOR 3: Pricing Format Compliance ─────────────────
        pricing_type = rfp_clins.get('pricing_type', 'unknown')
        format_score = 50

        if pricing_type == 'firm_fixed_price':
            if has_unit_prices and has_totals:
                format_score = 100
                strengths.append('FFP pricing format matches RFP requirement')
            elif has_dollar_amounts >= 2:
                format_score = 70
            else:
                weaknesses.append('RFP requires firm-fixed pricing but no fixed prices found')
                improvement_actions.append('Provide firm-fixed unit prices for each CLIN')
        elif pricing_type == 'time_and_materials':
            has_labor_rates = bool(re.search(r'(?:hourly|labor)\s*rate|rate\s*per\s*hour|\$\s*[\d.]+\s*/\s*h', proposal_text, re.IGNORECASE))
            if has_labor_rates:
                format_score = 90
                strengths.append('T&M labor rates provided')
            else:
                weaknesses.append('RFP requires T&M pricing but no labor rates found')
                improvement_actions.append('Add hourly labor rates by labor category with fully burdened calculations')

        scores['pricing_format'] = format_score
        subfactor_assessments.append({
            'subfactor': 'Pricing Format Compliance',
            'addressed': format_score >= 60,
            'strength': f'Matches {pricing_type.replace("_", " ")} format' if format_score >= 60 else 'Format mismatch',
        })

        # ─── SUBFACTOR 4: Option Year Handling ──────────────────────
        option_years = rfp_clins.get('option_years', 0)
        if option_years > 0:
            has_option_pricing = bool(re.search(r'option\s*year|option\s*period', proposal_text, re.IGNORECASE))
            has_escalation = bool(re.search(r'escalat|increase|adjustment|CPI|inflation', proposal_text, re.IGNORECASE))

            if has_option_pricing and has_escalation:
                scores['option_year_handling'] = 100
                strengths.append(f'Option year pricing with escalation for {option_years} option years')
            elif has_option_pricing:
                scores['option_year_handling'] = 70
                weaknesses.append('Option year pricing present but no escalation methodology')
                improvement_actions.append('Add annual escalation rate (typically 2-3% per year)')
            else:
                scores['option_year_handling'] = 20
                weaknesses.append(f'RFP has {option_years} option years but no option pricing found')
                improvement_actions.append(f'Add pricing for base year + {option_years} option years with annual escalation')

            subfactor_assessments.append({
                'subfactor': f'Option Year Pricing ({option_years} years)',
                'addressed': has_option_pricing,
                'strength': 'Option years priced' if has_option_pricing else f'Missing {option_years} option year pricing',
            })
        else:
            scores['option_year_handling'] = 80

        # ─── SUBFACTOR 5: Rate Reasonableness ───────────────────────
        if benchmarks.get('available'):
            dollar_amounts = re.findall(r'\$\s*([\d,]+(?:\.\d{2})?)', proposal_text)
            if dollar_amounts:
                amounts = [float(a.replace(',', '')) for a in dollar_amounts if float(a.replace(',', '')) > 0]
                small_amounts = [a for a in amounts if a < 1000]

                if small_amounts:
                    avg_unit = sum(small_amounts) / len(small_amounts)
                    low = benchmarks['low']
                    high = benchmarks['high']
                    typical = benchmarks['typical']

                    if low <= avg_unit <= high:
                        scores['rate_reasonableness'] = 85
                        strengths.append(f'Unit pricing (~${avg_unit:.0f}) within market range (${low}-${high} {benchmarks["unit"]})')
                    elif avg_unit < low:
                        scores['rate_reasonableness'] = 50
                        weaknesses.append(f'Unit pricing (~${avg_unit:.0f}) below market low (${low}) — may trigger price realism concern')
                        improvement_actions.append(f'Review pricing — market typical is ${typical} {benchmarks["unit"]}')
                    else:
                        scores['rate_reasonableness'] = 40
                        weaknesses.append(f'Unit pricing (~${avg_unit:.0f}) above market high (${high}) — may not be competitive')
                        improvement_actions.append(f'Consider pricing closer to market typical of ${typical} {benchmarks["unit"]}')
                else:
                    scores['rate_reasonableness'] = 60
            else:
                scores['rate_reasonableness'] = 30
                weaknesses.append('No pricing amounts found for market comparison')

            subfactor_assessments.append({
                'subfactor': f'Rate Reasonableness ({benchmarks.get("service_type", "N/A")})',
                'addressed': scores['rate_reasonableness'] >= 60,
                'strength': f'Market benchmark: ${benchmarks.get("typical", "?")} {benchmarks.get("unit", "")} typical',
            })
        else:
            scores['rate_reasonableness'] = 60

        # ─── COMPOSITE PRICE SCORE ──────────────────────────────────
        weights = {
            'clin_coverage': 0.30,
            'pricing_structure': 0.25,
            'pricing_format': 0.20,
            'option_year_handling': 0.10,
            'rate_reasonableness': 0.15,
        }

        raw_score = sum(scores[k] * weights[k] for k in scores)
        score_10 = min(round(raw_score / 10, 1), 10)

        from evaluator_scoring_engine import score_to_rating, ADJECTIVAL_RATINGS
        rating = score_to_rating(score_10)

        narrative_parts = [f"The offeror's price proposal is rated {rating}."]
        if strengths:
            narrative_parts.append(f"Strengths: {'; '.join(strengths[:2])}.")
        if weaknesses:
            narrative_parts.append(f"Concerns: {'; '.join(weaknesses[:2])}.")

        return {
            'name': 'Price',
            'rating': rating,
            'score': score_10,
            'scoring_method': 'pricing_intelligence',
            'subfactor_assessments': subfactor_assessments,
            'strengths': strengths,
            'weaknesses': weaknesses,
            'evaluator_narrative': ' '.join(narrative_parts),
            'improvement_actions': improvement_actions,
            'scoring_detail': {
                'clin_coverage': round(scores['clin_coverage'], 1),
                'pricing_structure': round(scores['pricing_structure'], 1),
                'pricing_format': round(scores['pricing_format'], 1),
                'option_year_handling': round(scores['option_year_handling'], 1),
                'rate_reasonableness': round(scores['rate_reasonableness'], 1),
                'rfp_clins_found': rfp_clins['clin_count'],
                'pricing_type': rfp_clins.get('pricing_type', 'unknown'),
                'option_years': rfp_clins.get('option_years', 0),
                'service_type_detected': service_type,
                'market_benchmark_available': benchmarks.get('available', False),
            },
            'market_benchmark': benchmarks if benchmarks.get('available') else None,
            'markup_recommendation': self.recommend_markup(
                eval_method=self._detect_eval_method(rfp_text),
            ) if rfp_text else None,
        }

    def _detect_eval_method(self, rfp_text: str) -> str:
        text_lower = rfp_text.lower()
        if 'lowest price technically acceptable' in text_lower or 'lpta' in text_lower:
            return 'lpta'
        if 'highest technically rated' in text_lower:
            return 'highest_rated'
        return 'best_value'

    # ─── 5. PRICING EVENT LOGGING ────────────────────────────────────────────

    def log_pricing_event(
        self,
        entity_id: str,
        action: str,
        metadata: Dict = None,
    ) -> Dict:
        """Log a pricing event to the learning engine."""
        try:
            from nexus_learning_engine import nxlearn
            return nxlearn('pricing', entity_id, action, metadata or {})
        except Exception as e:
            return {'error': str(e)}

    def log_markup_set(
        self,
        opportunity_id: str,
        markup_pct: float,
        sub_cost: float,
        final_bid: float,
        service_type: str = None,
        contract_type: str = None,
        eval_method: str = None,
    ):
        """Log when a markup is calculated."""
        value_range = 'under_100k'
        if final_bid >= 1000000:
            value_range = 'over_1m'
        elif final_bid >= 500000:
            value_range = '500k_to_1m'
        elif final_bid >= 100000:
            value_range = '100k_to_500k'

        return self.log_pricing_event(opportunity_id, 'markup_set', {
            'markup_pct': markup_pct,
            'sub_cost': sub_cost,
            'final_bid': final_bid,
            'value_range': value_range,
            'service_type': service_type or 'unknown',
            'contract_type': contract_type or 'unknown',
            'eval_method': eval_method or 'unknown',
        })

    def log_pricing_outcome(self, opportunity_id: str, won: bool, markup_pct: float = None):
        """Log win/loss for pricing learning."""
        action = 'price_won' if won else 'price_lost'
        meta = {}
        if markup_pct is not None:
            meta['markup_pct'] = markup_pct
        return self.log_pricing_event(opportunity_id, action, meta)


# ─── SINGLETON ───────────────────────────────────────────────────────────────

_instance = None


def get_pricing_intelligence() -> PricingIntelligence:
    global _instance
    if _instance is None:
        _instance = PricingIntelligence()
    return _instance
