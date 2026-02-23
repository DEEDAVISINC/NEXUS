#!/usr/bin/env python3
"""
NEXUS EVALUATOR SCORING ENGINE
================================
Simulates how government evaluators score proposals using Section M criteria.
Closes the loop: RFP → Parse → Score → Improve → Submit → Win/Loss → Learn → Better Scores.

EVALUATION METHODS:
  1. Best Value Tradeoff — Weighted factors, technical can outweigh price
  2. LPTA — Pass/fail technical, lowest price wins
  3. Highest Technically Rated — Best technical score at fair price

ADJECTIVAL RATINGS (FAR-standard scale):
  Outstanding → Good → Acceptable → Marginal → Unacceptable

LEARNING LOOP:
  Score proposal → Submit → Record outcome → Calibrate scoring model → Better predictions
"""

import os
import re
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
from dotenv import load_dotenv

load_dotenv()

# ─── ADJECTIVAL RATINGS (FAR-standard scale) ────────────────────────────────

ADJECTIVAL_RATINGS = {
    'Outstanding': {
        'score': 10,
        'min_threshold': 9.0,
        'color': '#16a34a',
        'description': 'Exceeds requirements with innovative approach. Very low risk.',
        'evaluator_language': 'Offeror demonstrated exceptional understanding and significantly exceeded requirements.',
    },
    'Good': {
        'score': 8,
        'min_threshold': 7.0,
        'color': '#2563eb',
        'description': 'Meets and partially exceeds requirements. Low risk.',
        'evaluator_language': 'Offeror adequately addressed all requirements with notable strengths.',
    },
    'Acceptable': {
        'score': 6,
        'min_threshold': 5.0,
        'color': '#ca8a04',
        'description': 'Meets minimum requirements. Moderate risk.',
        'evaluator_language': 'Offeror meets basic requirements with no significant weaknesses.',
    },
    'Marginal': {
        'score': 4,
        'min_threshold': 3.0,
        'color': '#ea580c',
        'description': 'Does not fully meet requirements. High risk.',
        'evaluator_language': 'Offeror failed to address one or more requirements, creating doubt.',
    },
    'Unacceptable': {
        'score': 0,
        'min_threshold': 0,
        'color': '#dc2626',
        'description': 'Fails to meet requirements. Proposal is unawardable.',
        'evaluator_language': 'Offeror did not provide required elements. Non-responsive.',
    },
}


def score_to_rating(score: float) -> str:
    for rating, data in ADJECTIVAL_RATINGS.items():
        if score >= data['min_threshold']:
            return rating
    return 'Unacceptable'


# ─── EVALUATION METHODS ─────────────────────────────────────────────────────

EVAL_METHODS = {
    'best_value': {
        'name': 'Best Value Tradeoff',
        'description': 'Technical and non-price factors traded off against price.',
        'keywords': ['best value', 'trade-off', 'tradeoff', 'technical is more important',
                     'non-price factors', 'technically superior'],
    },
    'lpta': {
        'name': 'Lowest Price Technically Acceptable',
        'description': 'Technical must be acceptable. Lowest price among acceptable offerors wins.',
        'keywords': ['lowest price technically acceptable', 'lpta', 'acceptable/unacceptable',
                     'pass/fail', 'lowest priced'],
    },
    'highest_rated': {
        'name': 'Highest Technically Rated at Fair and Reasonable Price',
        'description': 'Highest technical score wins if price is fair and reasonable.',
        'keywords': ['highest technically rated', 'fair and reasonable', 'highest rated'],
    },
}

# ─── STANDARD EVALUATION FACTORS WITH SCORING HEURISTICS ────────────────────

DEFAULT_FACTORS = [
    {
        'name': 'Technical Approach',
        'weight': 40,
        'subfactors': ['Understanding of Requirements', 'Proposed Methodology',
                       'Quality Control Plan', 'Innovation/Value-Added'],
        'critical': False,
        'section_ref': 'M.1',
        'requirements_summary': 'Demonstrate clear understanding of SOW and a detailed, feasible approach.',
        'scoring_keywords': {
            'strong': ['methodology', 'approach', 'process', 'procedure', 'timeline',
                       'milestone', 'deliverable', 'schedule', 'transition', 'quality control',
                       'risk mitigation', 'work plan', 'task order', 'phase', 'SOW'],
            'specific': ['will', 'shall', 'within', 'days', 'hours', 'weekly', 'monthly',
                         'quarterly', 'per', 'each', 'using', 'through', 'by', 'steps',
                         'implement', 'execute', 'deploy'],
            'vague': ['excellent', 'best', 'proven', 'high quality', 'committed to',
                      'dedicated to', 'world-class', 'extensive experience', 'premier',
                      'top-notch', 'superior'],
        },
    },
    {
        'name': 'Past Performance',
        'weight': 25,
        'subfactors': ['Relevance of Experience', 'Recency (within 5 years)',
                       'Quality of Performance', 'Customer References'],
        'critical': False,
        'section_ref': 'M.2',
        'requirements_summary': 'Demonstrate relevant, recent, and successful contract performance.',
        'scoring_keywords': {
            'strong': ['contract', 'awarded', 'performed', 'completed', 'CPARS',
                       'satisfactory', 'exceptional', 'reference', 'contract value',
                       'period of performance', 'similar scope', 'government', 'federal',
                       'state', 'municipal'],
            'specific': ['$', 'million', 'contract number', 'agency', 'same NAICS',
                         'awarded in', 'completed in', 'duration', 'contact name',
                         'contact phone', 'contact email'],
            'vague': ['extensive experience', 'years of experience', 'many contracts',
                      'various clients', 'long history', 'track record'],
        },
    },
    {
        'name': 'Staffing / Management',
        'weight': 20,
        'subfactors': ['Key Personnel Qualifications', 'Organizational Structure',
                       'Backup / Contingency Plans', 'Transition Plan'],
        'critical': False,
        'section_ref': 'M.3',
        'requirements_summary': 'Qualified key personnel, clear org structure, and contingency planning.',
        'scoring_keywords': {
            'strong': ['project manager', 'site lead', 'key personnel', 'resume',
                       'certification', 'license', 'degree', 'clearance', 'org chart',
                       'reporting structure', 'staffing plan', 'backup', 'contingency',
                       'transition'],
            'specific': ['years', 'certified', 'licensed', 'background check', 'trained',
                         'qualified', 'assigned', 'dedicated', 'full-time', 'part-time',
                         'hours per week'],
            'vague': ['experienced team', 'qualified staff', 'professional personnel',
                      'capable team', 'best people'],
        },
    },
    {
        'name': 'Price',
        'weight': 15,
        'subfactors': ['Price Reasonableness', 'Price Realism',
                       'Unbalanced Pricing Check'],
        'critical': False,
        'section_ref': 'M.4',
        'requirements_summary': 'Pricing that is realistic, reasonable, and properly structured.',
        'scoring_keywords': {
            'strong': ['CLIN', 'line item', 'unit price', 'total price', 'option year',
                       'base year', 'labor rate', 'materials', 'travel', 'ODC',
                       'subcontract costs', 'indirect rate', 'profit', 'fee'],
            'specific': ['$', 'per hour', 'per unit', 'fixed price', 'cost reimbursable',
                         'T&M', 'firm-fixed', 'IDIQ', 'cost-plus'],
            'vague': ['competitive pricing', 'best price', 'cost effective',
                      'affordable', 'value for money'],
        },
    },
]

# ─── SCORING DATA STORAGE ───────────────────────────────────────────────────

EVALUATOR_DB_PATH = Path(os.environ.get(
    'NEXUS_EVALUATOR_DB',
    '/Users/deedavis/NEXUS BACKEND/evaluator_scores_db.json'
))


class EvaluatorScoringEngine:
    """
    Simulates government evaluator scoring process.

    Flow:
      1. parse_rfp()        → Extract Section M evaluation criteria
      2. score_proposal()   → Rate proposal against each factor
      3. (improvements)     → Actionable steps to raise scores
      4. record_outcome()   → Win/loss feeds back to learning engine
      5. get_calibration()  → Track prediction accuracy over time
    """

    def __init__(self):
        self._ai = None
        self._db = self._load_db()

    def _get_ai(self):
        if self._ai is None:
            try:
                from anthropic import Anthropic
                key = os.environ.get('ANTHROPIC_API_KEY')
                if key:
                    self._ai = Anthropic(api_key=key)
            except ImportError:
                pass
        return self._ai

    def _load_db(self) -> Dict:
        if EVALUATOR_DB_PATH.exists():
            try:
                return json.loads(EVALUATOR_DB_PATH.read_text())
            except Exception:
                pass
        return {
            'evaluations': [],
            'outcomes': [],
            'calibration': {
                'total_scored': 0,
                'outcomes_recorded': 0,
                'accuracy_by_factor': {},
                'agency_patterns': {},
            },
        }

    def _save_db(self):
        try:
            EVALUATOR_DB_PATH.write_text(json.dumps(self._db, indent=2, default=str))
        except Exception as e:
            print(f"DB save error: {e}")

    # ─── STEP 1: PARSE RFP EVALUATION CRITERIA ──────────────────────────────

    def parse_rfp(self, rfp_text: str, use_ai: bool = True) -> Dict:
        """
        Extract evaluation method, factors, weights, and subfactors from RFP.
        Falls back to rule-based parsing when AI is unavailable.
        """
        if use_ai and self._get_ai():
            try:
                return self._parse_rfp_ai(rfp_text)
            except Exception as e:
                print(f"AI parse failed, falling back to rules: {e}")

        return self._parse_rfp_rules(rfp_text)

    def _parse_rfp_ai(self, rfp_text: str) -> Dict:
        prompt = f"""You are an expert Federal Contracting Officer reviewing a solicitation.
Extract the EVALUATION CRITERIA from this RFP text. Focus on Section M (Evaluation Factors)
and Section L (Instructions to Offerors).

RFP TEXT:
{rfp_text[:12000]}

Return ONLY valid JSON with this exact structure:
{{
  "evaluation_method": "best_value" | "lpta" | "highest_rated",
  "method_description": "How the evaluation method was stated in the RFP",
  "factors": [
    {{
      "name": "Factor name exactly as stated in RFP",
      "weight": <numeric weight or points, use 0 if not specified>,
      "relative_importance": "Most Important" | "Important" | "Least Important",
      "subfactors": ["Subfactor 1", "Subfactor 2"],
      "critical": true/false,
      "section_ref": "M.1.a or wherever specified",
      "requirements_summary": "What the evaluator is looking for"
    }}
  ],
  "relative_importance_statement": "The exact quote about relative importance from the RFP",
  "special_considerations": ["EDWOSB preference", "Local preference", etc.],
  "price_evaluation_method": "How price will be evaluated",
  "evaluation_team_hints": ["Any hints about who evaluates or how"]
}}

If numeric weights are not stated, assign proportional weights based on the stated relative importance.
If no evaluation criteria are found, use standard defaults but flag it."""

        response = self._get_ai().messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=3000,
            messages=[{"role": "user", "content": prompt}]
        )

        text = response.content[0].text
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
        if json_match:
            text = json_match.group(1)

        result = json.loads(text)
        result['parse_method'] = 'ai'
        result['parsed_at'] = datetime.now().isoformat()
        return result

    def _parse_rfp_rules(self, rfp_text: str) -> Dict:
        text_lower = rfp_text.lower()

        method = 'best_value'
        method_desc = ''
        for method_key, method_data in EVAL_METHODS.items():
            for kw in method_data['keywords']:
                if kw in text_lower:
                    method = method_key
                    idx = text_lower.index(kw)
                    method_desc = rfp_text[max(0, idx - 50):idx + len(kw) + 100].strip()
                    break

        factors = []
        factor_patterns = [
            r'(?:factor|criteria)\s*(?:\d+|[a-z])[.:)]\s*([A-Z][A-Za-z\s/&]+?)(?:\s*[-–—]\s*(\d+)\s*(?:points?|%)?)?',
            r'([A-Z][A-Za-z\s]+?)\s*:\s*(\d+)\s*(?:points?|%)',
            r'(?:evaluation\s+(?:factor|criteria))[:\s]+([A-Z][A-Za-z\s/&]+?)(?:\s*\((\d+)\s*(?:points?|%)?\))?',
        ]

        for pattern in factor_patterns:
            matches = re.findall(pattern, rfp_text)
            for match in matches:
                name = match[0].strip() if isinstance(match, tuple) else match.strip()
                weight = int(match[1]) if isinstance(match, tuple) and len(match) > 1 and match[1] else 0

                if len(name) < 3 or len(name) > 60:
                    continue
                skip_words = ['the', 'this', 'that', 'each', 'all', 'any', 'section', 'note', 'see']
                if name.lower().split()[0] in skip_words:
                    continue
                if name not in [f['name'] for f in factors]:
                    factors.append({
                        'name': name,
                        'weight': weight,
                        'relative_importance': 'Important',
                        'subfactors': [],
                        'critical': False,
                        'section_ref': '',
                        'requirements_summary': '',
                    })

        importance_statement = ''
        importance_patterns = [
            r'((?:technical|past performance|price|management|staffing)[\s\S]{0,100}(?:more important|greater weight|significantly more|equal)[\s\S]{0,100}(?:technical|past performance|price|management|staffing))',
            r'(factors?\s+(?:are\s+)?listed\s+in\s+(?:descending|order)\s+of\s+importance)',
        ]
        for pattern in importance_patterns:
            match = re.search(pattern, rfp_text, re.IGNORECASE)
            if match:
                importance_statement = match.group(1).strip()
                break

        if not factors or all(f['weight'] == 0 for f in factors):
            factors = [dict(f) for f in DEFAULT_FACTORS]
            if 'technical' in text_lower and 'more important' in text_lower and 'price' in text_lower:
                factors[0]['weight'] = 45
                factors[1]['weight'] = 25
                factors[2]['weight'] = 15
                factors[3]['weight'] = 15

        total = sum(f['weight'] for f in factors)
        if total > 0 and total != 100:
            for f in factors:
                f['weight'] = round(f['weight'] / total * 100)

        special = []
        if 'edwosb' in text_lower or 'economically disadvantaged women' in text_lower:
            special.append('EDWOSB set-aside or preference')
        if 'wosb' in text_lower or 'woman-owned' in text_lower:
            special.append('WOSB set-aside or preference')
        if 'small business' in text_lower and ('set-aside' in text_lower or 'set aside' in text_lower):
            special.append('Small business set-aside')
        if 'local' in text_lower and ('preference' in text_lower or 'bonus' in text_lower):
            special.append('Local vendor preference')

        return {
            'evaluation_method': method,
            'method_description': method_desc,
            'factors': factors,
            'relative_importance_statement': importance_statement,
            'special_considerations': special,
            'price_evaluation_method': 'Standard price evaluation',
            'evaluation_team_hints': [],
            'parse_method': 'rules',
            'parsed_at': datetime.now().isoformat(),
        }

    # ─── STEP 2: SCORE PROPOSAL ─────────────────────────────────────────────

    def score_proposal(
        self,
        proposal_text: str,
        rfp_analysis: Dict,
        rfp_text: str = '',
        proposal_id: str = None,
        use_ai: bool = True,
    ) -> Dict:
        """
        Score a proposal against parsed evaluation factors.
        Returns factor-by-factor adjectival ratings and weighted composite.
        """
        factors = rfp_analysis.get('factors', DEFAULT_FACTORS)
        method = rfp_analysis.get('evaluation_method', 'best_value')

        if use_ai and self._get_ai() and rfp_text:
            try:
                factor_scores = self._score_all_factors_ai(factors, proposal_text, rfp_text)
            except Exception as e:
                print(f"AI scoring failed, using rules: {e}")
                factor_scores = self._score_factors_with_pricing(factors, proposal_text, rfp_text)
        else:
            factor_scores = self._score_factors_with_pricing(factors, proposal_text, rfp_text)

        composite = self._compute_composite(factor_scores, method)
        improvements = self._generate_improvements(factor_scores)
        risk = self._assess_risk(factor_scores, method)
        competitive = self._estimate_competitive_position(composite, rfp_analysis)

        result = {
            'proposal_id': proposal_id or f"eval_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'evaluation_method': method,
            'method_name': EVAL_METHODS.get(method, {}).get('name', method),
            'factors': factor_scores,
            'composite': composite,
            'improvements': improvements,
            'risk_assessment': risk,
            'competitive_position': competitive,
            'scored_at': datetime.now().isoformat(),
        }

        self._db['evaluations'].append({
            'id': result['proposal_id'],
            'composite_score': composite['score'],
            'composite_rating': composite['rating'],
            'factor_ratings': {f['name']: f['rating'] for f in factor_scores},
            'method': method,
            'scored_at': result['scored_at'],
            'outcome': 'pending',
        })
        self._db['calibration']['total_scored'] += 1
        self._save_db()

        try:
            from nexus_learning_engine import nxlearn
            weakest = min(factor_scores, key=lambda f: f['score'])['name'] if factor_scores else ''
            nxlearn('bids', result['proposal_id'], 'bid_prepared', {
                'evaluator_composite': composite['score'],
                'evaluator_rating': composite['rating'],
                'factor_count': len(factor_scores),
                'method': method,
                'weakest_factor': weakest,
            })
        except Exception:
            pass

        return result

    def _score_all_factors_ai(self, factors: List[Dict], proposal_text: str, rfp_text: str) -> List[Dict]:
        """Single AI call to evaluate all factors at once (token-efficient)."""
        factors_desc = "\n".join([
            f"  {i+1}. {f['name']} (Weight: {f.get('weight', 0)}%) — Subfactors: {', '.join(f.get('subfactors', []))}"
            for i, f in enumerate(factors)
        ])

        prompt = f"""You are a government source selection evaluation board member scoring a proposal.

EVALUATION FACTORS:
{factors_desc}

RFP REQUIREMENTS:
{rfp_text[:5000]}

PROPOSAL TEXT:
{proposal_text[:8000]}

Score each factor using the standard adjectival rating scale:
- Outstanding (10): Exceeds requirements, innovative, very low risk
- Good (8): Meets and partially exceeds, low risk
- Acceptable (6): Meets minimum requirements, moderate risk
- Marginal (4): Doesn't fully meet requirements, high risk
- Unacceptable (0): Fails to meet requirements

Return ONLY valid JSON — an array with one object per factor:
[
  {{
    "name": "Factor Name",
    "rating": "Outstanding|Good|Acceptable|Marginal|Unacceptable",
    "score": <0-10>,
    "subfactor_assessments": [
      {{"subfactor": "name", "addressed": true/false, "strength": "brief note"}}
    ],
    "strengths": ["strength 1"],
    "weaknesses": ["weakness 1"],
    "evaluator_narrative": "2-3 sentence evaluation as a government evaluator would write",
    "improvement_actions": ["specific action to improve this rating"]
  }}
]"""

        response = self._get_ai().messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}]
        )

        text = response.content[0].text
        json_match = re.search(r'```(?:json)?\s*(\[.*?\])\s*```', text, re.DOTALL)
        if json_match:
            text = json_match.group(1)

        scored = json.loads(text)

        results = []
        for i, factor in enumerate(factors):
            ai_score = scored[i] if i < len(scored) else {}
            weight = factor.get('weight', 0)
            score_val = ai_score.get('score', 5)
            results.append({
                'name': factor.get('name', ai_score.get('name', f'Factor {i+1}')),
                'weight': weight,
                'rating': ai_score.get('rating', score_to_rating(score_val)),
                'score': score_val,
                'weighted_score': round(score_val / 10 * weight, 1),
                'subfactor_assessments': ai_score.get('subfactor_assessments', []),
                'strengths': ai_score.get('strengths', []),
                'weaknesses': ai_score.get('weaknesses', []),
                'evaluator_narrative': ai_score.get('evaluator_narrative', ''),
                'improvement_actions': ai_score.get('improvement_actions', []),
                'scoring_method': 'ai',
            })

        return results

    def _score_factors_with_pricing(self, factors: List[Dict], proposal_text: str, rfp_text: str) -> List[Dict]:
        """Score all factors, routing Price to pricing intelligence module."""
        results = []
        for factor in factors:
            if self._is_price_factor(factor):
                try:
                    from pricing_intelligence import get_pricing_intelligence
                    pi = get_pricing_intelligence()
                    price_score = pi.score_price_factor(proposal_text, rfp_text)
                    price_score['weight'] = factor.get('weight', 0)
                    price_score['weighted_score'] = round(price_score['score'] / 10 * factor.get('weight', 0), 1)
                    results.append(price_score)
                except Exception as e:
                    print(f"Pricing intelligence failed, falling back to rules: {e}")
                    results.append(self._score_factor_rules(factor, proposal_text))
            else:
                results.append(self._score_factor_rules(factor, proposal_text))
        return results

    @staticmethod
    def _is_price_factor(factor: Dict) -> bool:
        name = factor.get('name', '').lower()
        return any(term in name for term in ['price', 'cost', 'pricing', 'budget'])

    def _score_factor_rules(self, factor: Dict, proposal_text: str) -> Dict:
        """Rule-based scoring when AI is unavailable."""
        text_lower = proposal_text.lower()
        factor_name_lower = factor['name'].lower()

        keywords = factor.get('scoring_keywords', {})
        if not keywords:
            for df in DEFAULT_FACTORS:
                if df['name'].lower() in factor_name_lower or factor_name_lower in df['name'].lower():
                    keywords = df.get('scoring_keywords', {})
                    break

        # Dimension 1: COVERAGE — key topic keywords addressed
        strong_kw = keywords.get('strong', [])
        strong_hits = sum(1 for kw in strong_kw if kw.lower() in text_lower)
        coverage_pct = (strong_hits / max(len(strong_kw), 1)) * 100

        # Dimension 2: SPECIFICITY — concrete vs vague language
        specific_kw = keywords.get('specific', [])
        specific_hits = sum(1 for kw in specific_kw if kw.lower() in text_lower)
        vague_kw = keywords.get('vague', [])
        vague_hits = sum(1 for kw in vague_kw if kw.lower() in text_lower)
        specificity_score = min(specific_hits * 12, 100)
        vague_penalty = vague_hits * 8
        specificity_net = max(specificity_score - vague_penalty, 0)

        # Dimension 3: SUBFACTOR COVERAGE
        subfactors = factor.get('subfactors', [])
        subfactor_assessments = []
        subfactor_hits = 0
        for sf in subfactors:
            sf_words = [w for w in sf.lower().split() if len(w) > 3]
            addressed = any(w in text_lower for w in sf_words) if sf_words else False
            subfactor_assessments.append({
                'subfactor': sf,
                'addressed': addressed,
                'strength': 'Addressed in proposal' if addressed else 'Not clearly addressed',
            })
            if addressed:
                subfactor_hits += 1
        subfactor_pct = (subfactor_hits / max(len(subfactors), 1)) * 100

        # Dimension 4: DEPTH — sufficient content
        word_count = len(proposal_text.split())
        depth_score = min(word_count / 30, 100)

        raw = (
            coverage_pct * 0.35 +
            specificity_net * 0.25 +
            subfactor_pct * 0.25 +
            depth_score * 0.15
        )
        score = min(round(raw / 10, 1), 10)
        rating = score_to_rating(score)

        strengths = []
        weaknesses = []
        improvement_actions = []

        if coverage_pct >= 70:
            strengths.append(f'{int(coverage_pct)}% of key topic areas addressed')
        else:
            weaknesses.append(f'Only {int(coverage_pct)}% of key topic areas covered')
            missing = [kw for kw in strong_kw if kw.lower() not in text_lower][:5]
            if missing:
                improvement_actions.append(f'Address missing topics: {", ".join(missing)}')

        if specificity_net >= 50:
            strengths.append('Good use of concrete, specific language')
        elif vague_hits > specific_hits:
            weaknesses.append('Too much vague language — needs specific evidence')
            improvement_actions.append('Replace vague claims with numbers, dates, names, and measurable outcomes')

        missed_subfactors = [sa['subfactor'] for sa in subfactor_assessments if not sa['addressed']]
        if missed_subfactors:
            weaknesses.append(f'Missing subfactors: {", ".join(missed_subfactors)}')
            for msf in missed_subfactors:
                improvement_actions.append(f'Add section addressing: {msf}')
        elif subfactors:
            strengths.append('All subfactors addressed')

        if word_count < 200:
            weaknesses.append('Response is too brief — evaluators will see this as lack of effort')
            improvement_actions.append('Expand response with detailed methodology and specific examples')

        narrative = self._build_narrative(factor['name'], rating, strengths, weaknesses)

        return {
            'name': factor['name'],
            'weight': factor.get('weight', 0),
            'rating': rating,
            'score': score,
            'weighted_score': round(score / 10 * factor.get('weight', 0), 1),
            'subfactor_assessments': subfactor_assessments,
            'strengths': strengths,
            'weaknesses': weaknesses,
            'evaluator_narrative': narrative,
            'improvement_actions': improvement_actions,
            'scoring_method': 'rules',
            'scoring_detail': {
                'coverage_pct': round(coverage_pct, 1),
                'specificity_net': round(specificity_net, 1),
                'subfactor_pct': round(subfactor_pct, 1),
                'depth_score': round(depth_score, 1),
            },
        }

    def _build_narrative(self, factor_name: str, rating: str, strengths: List[str], weaknesses: List[str]) -> str:
        if rating in ('Outstanding', 'Good'):
            parts = [f"The offeror's {factor_name.lower()} is rated {rating}."]
            if strengths:
                parts.append(f"Strengths include: {'; '.join(strengths[:2])}.")
            if weaknesses:
                parts.append(f"Minor area for improvement: {weaknesses[0]}.")
            return ' '.join(parts)
        elif rating == 'Acceptable':
            parts = [f"The offeror's {factor_name.lower()} is rated {rating}.",
                     "The proposal meets minimum requirements."]
            if weaknesses:
                parts.append(f"However, {weaknesses[0].lower()}.")
            return ' '.join(parts)
        else:
            parts = [f"The offeror's {factor_name.lower()} is rated {rating}."]
            if weaknesses:
                parts.append(f"Significant concerns: {'; '.join(weaknesses[:2])}.")
            return ' '.join(parts)

    # ─── STEP 3: COMPOSITE SCORING ──────────────────────────────────────────

    def _compute_composite(self, factor_scores: List[Dict], method: str) -> Dict:
        if method == 'lpta':
            non_price = [f for f in factor_scores if f['name'].lower() != 'price']
            all_acceptable = all(
                ADJECTIVAL_RATINGS.get(f['rating'], {}).get('score', 0) >= 6
                for f in non_price
            )
            failing = [f['name'] for f in non_price
                       if ADJECTIVAL_RATINGS.get(f['rating'], {}).get('score', 0) < 6]
            return {
                'score': 100 if all_acceptable else 0,
                'max_possible': 100,
                'rating': 'Acceptable' if all_acceptable else 'Unacceptable',
                'method': 'lpta',
                'technically_acceptable': all_acceptable,
                'failing_factors': failing,
                'message': ('Technically Acceptable — now compete on price'
                            if all_acceptable else
                            f'NOT Technically Acceptable — fix: {", ".join(failing)}'),
            }

        total_weight = sum(f.get('weight', 0) for f in factor_scores)
        if total_weight == 0:
            total_weight = len(factor_scores) * 25
            for f in factor_scores:
                f['weight'] = 25
                f['weighted_score'] = round(f['score'] / 10 * 25, 1)

        weighted_sum = sum(f.get('weighted_score', 0) for f in factor_scores)
        score = round((weighted_sum / total_weight) * 100, 1) if total_weight > 0 else 0
        rating = score_to_rating(score / 10)

        return {
            'score': score,
            'max_possible': 100,
            'rating': rating,
            'method': method,
            'weighted_sum': round(weighted_sum, 1),
            'total_weight': total_weight,
            'message': self._composite_message(score),
        }

    def _composite_message(self, score: float) -> str:
        if score >= 90:
            return 'Strong competitive position. Proposal exceeds requirements across factors.'
        elif score >= 75:
            return 'Competitive proposal. Address noted weaknesses to strengthen position.'
        elif score >= 60:
            return 'Meets minimum bar but vulnerable. Significant improvement needed.'
        elif score >= 40:
            return 'Below competitive threshold. Major revisions required.'
        else:
            return 'Not submission-ready. Fundamental gaps in proposal coverage.'

    # ─── STEP 4: IMPROVEMENT PLAN ───────────────────────────────────────────

    def _generate_improvements(self, factor_scores: List[Dict]) -> Dict:
        critical = []
        high = []
        medium = []

        for f in factor_scores:
            rating = f.get('rating', 'Acceptable')
            weight = f.get('weight', 0)
            actions = f.get('improvement_actions', [])

            for action in actions:
                item = {
                    'action': action,
                    'factor': f['name'],
                    'current_rating': rating,
                    'weight': weight,
                }
                if rating == 'Unacceptable':
                    item['impact'] = 'REQUIRED — prevents elimination'
                    critical.append(item)
                elif rating == 'Marginal':
                    item['impact'] = f'Moves {f["name"]} from Marginal to Acceptable'
                    critical.append(item)
                elif rating == 'Acceptable' and weight >= 20:
                    item['impact'] = f'Moves {f["name"]} from Acceptable to Good (+{weight * 0.2:.0f}pts)'
                    high.append(item)
                elif rating == 'Acceptable':
                    item['impact'] = f'Strengthens {f["name"]} rating'
                    medium.append(item)
                elif rating == 'Good' and weight >= 30:
                    item['impact'] = f'Pushes {f["name"]} to Outstanding (+{weight * 0.2:.0f}pts)'
                    medium.append(item)

        return {
            'critical': critical,
            'high': high,
            'medium': medium,
            'total_actions': len(critical) + len(high) + len(medium),
        }

    def _assess_risk(self, factor_scores: List[Dict], method: str) -> Dict:
        critical_gaps = []
        auto_reject = []

        for f in factor_scores:
            rating = f.get('rating', 'Acceptable')
            if rating == 'Unacceptable':
                if f.get('critical', False) or method == 'lpta':
                    auto_reject.append({
                        'factor': f['name'],
                        'reason': f'{f["name"]} rated Unacceptable — proposal eliminated',
                    })
                else:
                    critical_gaps.append({
                        'factor': f['name'],
                        'reason': f'{f["name"]} rated Unacceptable — severely damages score',
                    })
            elif rating == 'Marginal':
                critical_gaps.append({
                    'factor': f['name'],
                    'reason': f'{f["name"]} rated Marginal — high risk',
                })

        risk_level = 'LOW'
        if auto_reject:
            risk_level = 'CRITICAL'
        elif critical_gaps:
            risk_level = 'HIGH'
        elif any(f.get('rating') == 'Acceptable' and f.get('weight', 0) >= 30 for f in factor_scores):
            risk_level = 'MODERATE'

        messages = {
            'CRITICAL': 'DO NOT SUBMIT — proposal will be eliminated. Fix critical issues.',
            'HIGH': 'Submission risky. Address Marginal ratings before submission.',
            'MODERATE': 'Competitive but vulnerable. Strengthen Acceptable-rated high-weight factors.',
            'LOW': 'Proposal is competitive. Fine-tune for optimal score.',
        }

        return {
            'level': risk_level,
            'auto_reject_risks': auto_reject,
            'critical_gaps': critical_gaps,
            'message': messages[risk_level],
        }

    def _estimate_competitive_position(self, composite: Dict, rfp_analysis: Dict) -> Dict:
        score = composite.get('score', 0)
        special = rfp_analysis.get('special_considerations', [])
        edwosb_boost = any('edwosb' in s.lower() for s in special)
        sb_boost = any('small business' in s.lower() for s in special)

        if score >= 85:
            position = 'Strong Favorite' if edwosb_boost else 'Strong Contender'
        elif score >= 70:
            position = 'Competitive' if edwosb_boost else 'In the Mix'
        elif score >= 55:
            position = 'Vulnerable'
        else:
            position = 'Weak'

        recs = {
            'Strong Favorite': 'Submit with confidence. Focus final review on compliance.',
            'Strong Contender': 'Strong position. Review improvement plan for easy wins.',
            'Competitive': 'Good position. Address HIGH priority improvements to separate from field.',
            'In the Mix': 'Competitive but not dominant. Implement improvement plan.',
            'Vulnerable': 'Do not submit as-is. Complete HIGH priority improvements first.',
            'Weak': 'Significant work needed. Evaluate if timeline allows adequate preparation.',
        }

        return {
            'position': position,
            'score': score,
            'edwosb_advantage': edwosb_boost,
            'small_business_advantage': sb_boost,
            'recommendation': recs.get(position, ''),
        }

    # ─── STEP 5: LEARNING FEEDBACK ──────────────────────────────────────────

    def record_outcome(self, proposal_id: str, won: bool, debrief_data: Dict = None) -> Dict:
        """
        Record win/loss outcome and correlate with predicted scores.
        This is the learning feedback loop that makes scoring better over time.
        """
        evaluation = None
        for ev in self._db['evaluations']:
            if ev['id'] == proposal_id:
                evaluation = ev
                break

        if not evaluation:
            return {'error': f'No evaluation found for {proposal_id}'}

        outcome = {
            'proposal_id': proposal_id,
            'won': won,
            'our_composite': evaluation.get('composite_score', 0),
            'our_rating': evaluation.get('composite_rating', 'Unknown'),
            'our_factor_ratings': evaluation.get('factor_ratings', {}),
            'debrief_data': debrief_data,
            'recorded_at': datetime.now().isoformat(),
        }

        self._db['outcomes'].append(outcome)
        evaluation['outcome'] = 'won' if won else 'lost'

        cal = self._db['calibration']
        cal['outcomes_recorded'] += 1

        for factor_name, our_rating in evaluation.get('factor_ratings', {}).items():
            if factor_name not in cal['accuracy_by_factor']:
                cal['accuracy_by_factor'][factor_name] = {
                    'predictions': [], 'correct': 0, 'total': 0
                }

            af = cal['accuracy_by_factor'][factor_name]
            af['predictions'].append({
                'predicted': our_rating,
                'outcome': 'won' if won else 'lost',
                'debrief_rating': debrief_data.get(factor_name) if debrief_data else None,
            })
            af['total'] += 1

            if debrief_data and factor_name in debrief_data:
                if debrief_data[factor_name] == our_rating:
                    af['correct'] += 1

        self._save_db()

        try:
            from nexus_learning_engine import nxlearn
            nxlearn('bids', proposal_id, 'won' if won else 'lost', {
                'evaluator_composite': evaluation.get('composite_score', 0),
                'evaluator_rating': evaluation.get('composite_rating', ''),
                'had_debrief': debrief_data is not None,
            })
        except Exception:
            pass

        return {
            'recorded': True,
            'proposal_id': proposal_id,
            'outcome': 'won' if won else 'lost',
            'our_prediction': evaluation.get('composite_rating', 'Unknown'),
            'calibration': self._compute_accuracy(),
        }

    def _compute_accuracy(self) -> Dict:
        cal = self._db['calibration']
        outcomes = self._db['outcomes']

        if not outcomes:
            return {
                'total_evaluations': cal['total_scored'],
                'outcomes_recorded': 0,
                'accuracy': None,
                'message': 'No outcomes recorded yet — submit bids and log results to start learning.',
            }

        rating_outcomes = defaultdict(lambda: {'won': 0, 'lost': 0})
        for o in outcomes:
            r = o.get('our_rating', 'Unknown')
            if o['won']:
                rating_outcomes[r]['won'] += 1
            else:
                rating_outcomes[r]['lost'] += 1

        rating_order = ['Outstanding', 'Good', 'Acceptable', 'Marginal', 'Unacceptable']
        win_rates = []
        for r in rating_order:
            data = rating_outcomes.get(r, {'won': 0, 'lost': 0})
            total = data['won'] + data['lost']
            if total > 0:
                win_rates.append(data['won'] / total)

        correlation_score = 0
        if len(win_rates) >= 2:
            correct_order = sum(1 for i in range(len(win_rates) - 1) if win_rates[i] >= win_rates[i + 1])
            correlation_score = correct_order / (len(win_rates) - 1) * 100

        return {
            'total_evaluations': cal['total_scored'],
            'outcomes_recorded': cal['outcomes_recorded'],
            'rating_win_rates': {
                r: {
                    'won': rating_outcomes[r]['won'],
                    'lost': rating_outcomes[r]['lost'],
                    'win_rate': round(
                        rating_outcomes[r]['won'] /
                        max(rating_outcomes[r]['won'] + rating_outcomes[r]['lost'], 1) * 100, 1
                    ),
                }
                for r in rating_order
                if rating_outcomes.get(r, {}).get('won', 0) + rating_outcomes.get(r, {}).get('lost', 0) > 0
            },
            'calibration_correlation': round(correlation_score, 1),
            'message': (
                f'{cal["outcomes_recorded"]} outcomes recorded. '
                + ('Model is well-calibrated.' if correlation_score >= 70
                   else 'Needs more data to calibrate — keep logging outcomes.')
            ),
        }

    def get_calibration(self) -> Dict:
        return self._compute_accuracy()

    def get_evaluation_history(self) -> List[Dict]:
        return self._db.get('evaluations', [])


# ─── SINGLETON ───────────────────────────────────────────────────────────────

_engine = None


def get_engine() -> EvaluatorScoringEngine:
    global _engine
    if _engine is None:
        _engine = EvaluatorScoringEngine()
    return _engine


# ─── CONVENIENCE FUNCTIONS ───────────────────────────────────────────────────

def parse_rfp(rfp_text: str, use_ai: bool = True) -> Dict:
    return get_engine().parse_rfp(rfp_text, use_ai=use_ai)


def score_proposal(proposal_text: str, rfp_analysis: Dict, rfp_text: str = '',
                   proposal_id: str = None, use_ai: bool = True) -> Dict:
    return get_engine().score_proposal(proposal_text, rfp_analysis, rfp_text, proposal_id, use_ai)


def record_outcome(proposal_id: str, won: bool, debrief_data: Dict = None) -> Dict:
    return get_engine().record_outcome(proposal_id, won, debrief_data)


def get_calibration() -> Dict:
    return get_engine().get_calibration()
