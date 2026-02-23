#!/usr/bin/env python3
"""
NEXUS INTELLIGENCE LEARNING ENGINE
=====================================
Makes the Contract Intelligence system self-learning. Every action Dee takes
on an opportunity (contact, skip, win, lose) becomes training data that
improves future scoring.

Learning Loop:
  1. TRACK — Log every action on every opportunity (contacted, responded, won, lost, skipped)
  2. ANALYZE — Claude reviews outcome history and finds patterns
  3. ADJUST — Scoring weights update based on what actually works
  4. SURFACE — Insights shown in dashboard ("VA janitorial has 80% response rate")

This is NOT theoretical ML. This is practical feedback-driven scoring:
  - Start with baseline weights (hardcoded)
  - As Dee takes actions and logs outcomes, patterns emerge
  - AI analyzes patterns → generates new weights + insights
  - Weights get saved and used by the scoring engine
  - Cycle repeats — system gets smarter with every action
"""

import os
import json
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from collections import defaultdict
from dotenv import load_dotenv

load_dotenv()

LEARNING_DATA_PATH = Path(os.environ.get(
    'LEARNING_DATA_PATH',
    '/Users/deedavis/NEXUS BACKEND/intelligence_learning_data.json'
))

# Action lifecycle for an opportunity
ACTION_TYPES = [
    'discovered',    # System found it
    'reviewed',      # Dee looked at it
    'contacted',     # Dee reached out to prime/buyer
    'responded',     # Prime/buyer responded
    'meeting',       # Meeting scheduled
    'pursuing',      # Actively working the opportunity
    'bid_submitted', # Bid/proposal sent
    'won',           # Contract awarded to DDI
    'lost',          # Went to someone else
    'skipped',       # Dee decided not to pursue
    'no_response',   # Contacted but no response after follow-up
]

POSITIVE_OUTCOMES = {'responded', 'meeting', 'pursuing', 'bid_submitted', 'won'}
NEGATIVE_OUTCOMES = {'no_response', 'lost', 'skipped'}
TERMINAL_OUTCOMES = {'won', 'lost', 'skipped', 'no_response'}

# Baseline scoring weights — these get overridden by learned weights
BASELINE_WEIGHTS = {
    'sub_under_prime': {
        'has_contact_info': 40,
        'prime_in_directory': 20,
        'is_priority_lane': 20,
        'value_under_50m': 20,
        'value_under_500m': 10,
        'value_over_500m': 5,
    },
    'prime_recompete': {
        'is_priority_lane': 30,
        'value_under_10m': 30,
        'value_under_50m': 20,
        'value_under_200m': 10,
        'value_over_200m': 5,
        'va_agency': 15,
        'hhs_agency': 10,
    },
    'hire_subs': {
        'priority_lane': 25,
        'value_under_25m': 25,
        'value_under_100m': 15,
        'high_sub_availability': 20,
    },
}


class IntelligenceLearningEngine:
    """
    Tracks actions, analyzes patterns, adjusts scoring weights.
    Persists all learning data to local JSON.
    """

    def __init__(self):
        self._data = None
        self._anthropic = None

    def _get_anthropic(self):
        if self._anthropic is None:
            import anthropic
            self._anthropic = anthropic.Anthropic(
                api_key=os.environ.get('ANTHROPIC_API_KEY', '')
            )
        return self._anthropic

    # ------------------------------------------------------------------
    # DATA PERSISTENCE
    # ------------------------------------------------------------------

    def _load_data(self) -> Dict:
        if self._data is not None:
            return self._data
        if LEARNING_DATA_PATH.exists():
            with open(LEARNING_DATA_PATH, 'r') as f:
                self._data = json.load(f)
        else:
            self._data = {
                'actions': [],
                'insights': [],
                'learned_weights': None,
                'weight_history': [],
                'analysis_history': [],
                'stats': {
                    'total_actions': 0,
                    'total_analyses': 0,
                    'last_analysis': None,
                    'last_weight_update': None,
                },
            }
        return self._data

    def _save_data(self):
        if self._data:
            with open(LEARNING_DATA_PATH, 'w') as f:
                json.dump(self._data, f, indent=2, default=str)

    # ------------------------------------------------------------------
    # TRACK — Log every action
    # ------------------------------------------------------------------

    def log_action(self, opportunity_id: str, action: str, metadata: Dict = None) -> Dict:
        """
        Log an action taken on an opportunity.
        This is the raw training data for the learning system.
        """
        if action not in ACTION_TYPES:
            return {'error': f'Invalid action: {action}. Valid: {ACTION_TYPES}'}

        data = self._load_data()

        entry = {
            'id': hashlib.md5(f"{opportunity_id}-{action}-{datetime.now().isoformat()}".encode()).hexdigest()[:12],
            'opportunity_id': opportunity_id,
            'action': action,
            'timestamp': datetime.now().isoformat(),
            'metadata': metadata or {},
        }

        data['actions'].append(entry)
        data['stats']['total_actions'] = len(data['actions'])
        self._save_data()

        return {'success': True, 'action_logged': entry}

    def get_opportunity_history(self, opportunity_id: str) -> List[Dict]:
        """Get all actions taken on a specific opportunity."""
        data = self._load_data()
        return [a for a in data['actions'] if a['opportunity_id'] == opportunity_id]

    # ------------------------------------------------------------------
    # ANALYZE — AI finds patterns in outcome data
    # ------------------------------------------------------------------

    def run_analysis(self, use_ai: bool = True) -> Dict:
        """
        Analyze all tracked actions. Two modes:
          1. AI-powered (use_ai=True) — Claude finds deep patterns and generates prose insights
          2. Statistical (use_ai=False or AI unavailable) — Pure math pattern analysis, still adjusts weights
        Falls back to statistical automatically if AI fails.
        """
        data = self._load_data()
        actions = data.get('actions', [])

        if len(actions) < 5:
            return {
                'status': 'insufficient_data',
                'message': f'Need at least 5 logged actions to analyze. Currently have {len(actions)}.',
                'actions_count': len(actions),
            }

        outcome_summary = self._build_outcome_summary(actions)
        result = None

        if use_ai:
            result = self._try_ai_analysis(outcome_summary, data)

        if result is None:
            result = self._run_statistical_analysis(outcome_summary, data)

        data['analysis_history'].append({
            'timestamp': datetime.now().isoformat(),
            'actions_analyzed': len(actions),
            'mode': result.get('mode', 'unknown'),
            'outcome_summary': outcome_summary,
        })

        if result.get('new_weights'):
            old_weights = data.get('learned_weights') or BASELINE_WEIGHTS
            data['weight_history'].append({
                'timestamp': datetime.now().isoformat(),
                'old_weights': old_weights,
                'new_weights': result['new_weights'],
                'reason': result.get('weight_change_reason', 'Analysis'),
            })
            data['learned_weights'] = result['new_weights']
            data['stats']['last_weight_update'] = datetime.now().isoformat()

        if result.get('insights'):
            for insight in result['insights']:
                insight['generated_at'] = datetime.now().isoformat()
                insight['actions_analyzed'] = len(actions)
            data['insights'] = result['insights'] + data.get('insights', [])
            data['insights'] = data['insights'][:50]

        data['stats']['total_analyses'] = len(data['analysis_history'])
        data['stats']['last_analysis'] = datetime.now().isoformat()
        self._save_data()

        return {
            'status': 'complete',
            'mode': result.get('mode', 'statistical'),
            'actions_analyzed': len(actions),
            'insights_generated': len(result.get('insights', [])),
            'weights_updated': bool(result.get('new_weights')),
            'insights': result.get('insights', []),
            'patterns': result.get('patterns', []),
        }

    def _try_ai_analysis(self, summary: Dict, data: Dict) -> Optional[Dict]:
        """Attempt AI analysis with Claude. Returns None if unavailable."""
        try:
            intel_data = self._load_intelligence_data()
            prompt = self._build_analysis_prompt(summary, intel_data, data.get('learned_weights'))
            client = self._get_anthropic()
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4000,
                messages=[{"role": "user", "content": prompt}],
            )
            result = self._parse_analysis_response(response.content[0].text)
            result['mode'] = 'ai'
            return result
        except Exception as e:
            print(f"AI analysis unavailable ({e}), falling back to statistical")
            return None

    def _run_statistical_analysis(self, summary: Dict, data: Dict) -> Dict:
        """
        Pure statistical analysis — no AI needed. Adjusts weights based on
        actual success/failure rates by lane, agency, avenue, and value range.
        """
        current_weights = data.get('learned_weights') or BASELINE_WEIGHTS.copy()
        import copy
        new_weights = copy.deepcopy(current_weights)

        insights = []
        patterns = []

        # Analyze by lane
        for lane, counts in summary.get('by_lane', {}).items():
            total = counts['total']
            positive = counts['positive']
            negative = counts['negative']
            if total >= 2:
                rate = positive / total
                if rate >= 0.6:
                    patterns.append({
                        'pattern': f'{lane} has {rate:.0%} positive outcome rate',
                        'confidence': 'high' if total >= 5 else 'medium',
                        'evidence': f'{positive} positive out of {total} tracked',
                    })
                    insights.append({
                        'title': f'{lane} is a hot lane',
                        'body': f'{positive} of {total} {lane} opportunities led to positive outcomes. Increase focus here.',
                        'impact': 'high',
                        'category': 'lane',
                    })
                elif rate <= 0.2 and negative > 0:
                    patterns.append({
                        'pattern': f'{lane} has low success — only {rate:.0%} positive',
                        'confidence': 'medium',
                        'evidence': f'{negative} negative out of {total} tracked',
                    })
                    insights.append({
                        'title': f'{lane} is underperforming',
                        'body': f'Only {positive} of {total} {lane} opportunities worked. Consider deprioritizing or changing approach.',
                        'impact': 'medium',
                        'category': 'lane',
                    })

        # Analyze by agency
        for agency, counts in summary.get('by_agency', {}).items():
            total = counts['total']
            positive = counts['positive']
            if total >= 2:
                rate = positive / total
                if rate >= 0.5:
                    insights.append({
                        'title': f'{agency} is responsive',
                        'body': f'{rate:.0%} positive rate from {agency}. These contracts are worth pursuing.',
                        'impact': 'high' if rate >= 0.7 else 'medium',
                        'category': 'strategy',
                    })

        # Analyze by avenue
        for avenue, counts in summary.get('by_avenue', {}).items():
            total = counts['total']
            positive = counts['positive']
            if total >= 2:
                rate = positive / total
                avenue_label = avenue.replace('_', ' ').title()
                if rate >= 0.5:
                    insights.append({
                        'title': f'{avenue_label} avenue is working',
                        'body': f'{rate:.0%} success rate. Keep investing in this strategy.',
                        'impact': 'high',
                        'category': 'strategy',
                    })
                elif rate < 0.3 and total >= 3:
                    insights.append({
                        'title': f'{avenue_label} needs adjustment',
                        'body': f'Only {rate:.0%} success. Review your approach for this avenue.',
                        'impact': 'medium',
                        'category': 'strategy',
                    })

        # Adjust weights based on response rate
        response_rate = summary.get('response_rate', 0)
        if response_rate > 0:
            insights.append({
                'title': f'Overall response rate: {response_rate:.0%}',
                'body': 'This is the percentage of contacts that got a response. Track this to optimize outreach.',
                'impact': 'medium',
                'category': 'outreach',
            })

        # Statistical weight adjustments
        by_avenue = summary.get('by_avenue', {})
        sub_data = by_avenue.get('sub_under_prime', {'positive': 0, 'total': 0})
        prime_data = by_avenue.get('prime_recompete', {'positive': 0, 'total': 0})
        hire_data = by_avenue.get('hire_subs', {'positive': 0, 'total': 0})

        if sub_data['total'] >= 3:
            sub_rate = sub_data['positive'] / sub_data['total']
            if sub_rate >= 0.5:
                new_weights['sub_under_prime']['has_contact_info'] = min(50, current_weights.get('sub_under_prime', {}).get('has_contact_info', 40) + 5)
            elif sub_rate < 0.2:
                new_weights['sub_under_prime']['has_contact_info'] = max(20, current_weights.get('sub_under_prime', {}).get('has_contact_info', 40) - 5)

        # Boost VA weights if VA responses are high
        va_data = summary.get('by_agency', {}).get('Department of Veterans Affairs', {'positive': 0, 'total': 0})
        if va_data['total'] >= 2 and va_data['positive'] / max(va_data['total'], 1) >= 0.5:
            new_weights['prime_recompete']['va_agency'] = min(25, current_weights.get('prime_recompete', {}).get('va_agency', 15) + 5)

        weights_changed = json.dumps(new_weights) != json.dumps(current_weights)

        return {
            'mode': 'statistical',
            'patterns': patterns,
            'insights': insights,
            'new_weights': new_weights if weights_changed else None,
            'weight_change_reason': 'Statistical analysis of outcome rates' if weights_changed else None,
        }

    def _build_outcome_summary(self, actions: List[Dict]) -> Dict:
        """Aggregate actions into a summary for AI analysis."""
        by_opportunity = defaultdict(list)
        for a in actions:
            by_opportunity[a['opportunity_id']].append(a)

        outcomes = []
        for opp_id, opp_actions in by_opportunity.items():
            sorted_actions = sorted(opp_actions, key=lambda x: x['timestamp'])
            last_action = sorted_actions[-1]
            meta = {}
            for a in sorted_actions:
                meta.update(a.get('metadata', {}))

            outcomes.append({
                'opportunity_id': opp_id,
                'actions': [a['action'] for a in sorted_actions],
                'final_outcome': last_action['action'],
                'is_positive': last_action['action'] in POSITIVE_OUTCOMES,
                'is_negative': last_action['action'] in NEGATIVE_OUTCOMES,
                'is_terminal': last_action['action'] in TERMINAL_OUTCOMES,
                'metadata': meta,
                'action_count': len(sorted_actions),
                'days_active': self._days_between(
                    sorted_actions[0]['timestamp'],
                    sorted_actions[-1]['timestamp']
                ),
            })

        by_lane = defaultdict(lambda: {'positive': 0, 'negative': 0, 'total': 0})
        by_agency = defaultdict(lambda: {'positive': 0, 'negative': 0, 'total': 0})
        by_avenue = defaultdict(lambda: {'positive': 0, 'negative': 0, 'total': 0})
        by_value_range = defaultdict(lambda: {'positive': 0, 'negative': 0, 'total': 0})

        for o in outcomes:
            meta = o['metadata']
            lane = meta.get('lane', 'Unknown')
            agency = meta.get('agency', 'Unknown')
            avenue = meta.get('avenue', 'Unknown')
            value = meta.get('value', 0)

            val_range = self._value_range(value)

            for group, key in [(by_lane, lane), (by_agency, agency),
                               (by_avenue, avenue), (by_value_range, val_range)]:
                group[key]['total'] += 1
                if o['is_positive']:
                    group[key]['positive'] += 1
                if o['is_negative']:
                    group[key]['negative'] += 1

        return {
            'total_opportunities': len(outcomes),
            'total_actions': len(actions),
            'outcomes': outcomes,
            'by_lane': dict(by_lane),
            'by_agency': dict(by_agency),
            'by_avenue': dict(by_avenue),
            'by_value_range': dict(by_value_range),
            'positive_rate': sum(1 for o in outcomes if o['is_positive']) / max(len(outcomes), 1),
            'response_rate': sum(
                1 for o in outcomes if 'responded' in o['actions']
            ) / max(sum(1 for o in outcomes if 'contacted' in o['actions']), 1),
        }

    def _build_analysis_prompt(self, summary: Dict, intel_data: Dict, current_weights: Dict) -> str:
        """Build the prompt for Claude to analyze patterns."""
        weights = current_weights or BASELINE_WEIGHTS

        return f"""You are the AI learning engine for Dee Davis Inc. (DDI), a woman-owned small business 
that does government contracting. DDI uses a three-avenue strategy:

1. SUB UNDER PRIME — Get on existing prime contractor's subcontractor list
2. PRIME THE RECOMPETE — When a contract expires, DDI bids as the prime
3. HIRE SUBS — DDI primes the contract and hires Tier 2 subcontractors

DDI's priority service lanes: Facilities Support, Janitorial, Landscaping/Grounds, 
Medical Labs/Drug Testing, Courier/Express Delivery, Temp Staffing, Security Guards, 
Office Admin, Industrial Supplies.

CURRENT SCORING WEIGHTS:
{json.dumps(weights, indent=2)}

OUTCOME DATA FROM DEE'S ACTIONS:
Total opportunities tracked: {summary['total_opportunities']}
Total actions logged: {summary['total_actions']}
Overall positive outcome rate: {summary['positive_rate']:.1%}
Response rate (contacted → responded): {summary['response_rate']:.1%}

BY SERVICE LANE:
{json.dumps(summary['by_lane'], indent=2)}

BY AGENCY:
{json.dumps(summary['by_agency'], indent=2)}

BY AVENUE:
{json.dumps(summary['by_avenue'], indent=2)}

BY CONTRACT VALUE:
{json.dumps(summary['by_value_range'], indent=2)}

INDIVIDUAL OUTCOMES:
{json.dumps(summary['outcomes'][:30], indent=2)}

Analyze this data and respond with EXACTLY this JSON structure:
{{
  "patterns": [
    {{"pattern": "description of pattern found", "confidence": "high/medium/low", "evidence": "what data supports this"}}
  ],
  "insights": [
    {{"title": "short title", "body": "actionable insight for Dee", "impact": "high/medium/low", "category": "strategy/scoring/outreach/lane"}}
  ],
  "new_weights": {{
    "sub_under_prime": {{
      "has_contact_info": 40,
      "prime_in_directory": 20,
      "is_priority_lane": 20,
      "value_under_50m": 20,
      "value_under_500m": 10,
      "value_over_500m": 5
    }},
    "prime_recompete": {{
      "is_priority_lane": 30,
      "value_under_10m": 30,
      "value_under_50m": 20,
      "value_under_200m": 10,
      "value_over_200m": 5,
      "va_agency": 15,
      "hhs_agency": 10
    }},
    "hire_subs": {{
      "priority_lane": 25,
      "value_under_25m": 25,
      "value_under_100m": 15,
      "high_sub_availability": 20
    }}
  }},
  "weight_change_reason": "why weights were adjusted"
}}

RULES:
- Only adjust weights if the data clearly supports it. If insufficient data, return current weights unchanged.
- Insights must be SPECIFIC and ACTIONABLE — not generic advice.
- Patterns must cite actual data from the summary.
- Weight values should stay between 0-50 for any single factor.
- If a lane or agency has a notably high or low success rate, reflect that in weights.
- Be direct. Dee doesn't want fluff."""

    def _parse_analysis_response(self, response_text: str) -> Dict:
        """Parse Claude's JSON response, handling markdown code blocks."""
        text = response_text.strip()
        if '```json' in text:
            text = text.split('```json')[1].split('```')[0].strip()
        elif '```' in text:
            text = text.split('```')[1].split('```')[0].strip()

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return {
                'patterns': [],
                'insights': [{
                    'title': 'Analysis Complete',
                    'body': response_text[:500],
                    'impact': 'medium',
                    'category': 'strategy',
                }],
                'new_weights': None,
                'weight_change_reason': 'Could not parse structured response',
            }

    # ------------------------------------------------------------------
    # GET LEARNED WEIGHTS — Used by the scoring engine
    # ------------------------------------------------------------------

    def get_active_weights(self) -> Dict:
        """
        Return the current active scoring weights.
        Uses learned weights if available, otherwise baseline.
        """
        data = self._load_data()
        return data.get('learned_weights') or BASELINE_WEIGHTS

    def get_insights(self, limit: int = 10) -> List[Dict]:
        """Get the most recent AI-generated insights."""
        data = self._load_data()
        return data.get('insights', [])[:limit]

    def get_learning_status(self) -> Dict:
        """Dashboard-ready summary of the learning system's state."""
        data = self._load_data()
        actions = data.get('actions', [])

        by_action = defaultdict(int)
        for a in actions:
            by_action[a['action']] += 1

        unique_opportunities = len(set(a['opportunity_id'] for a in actions))
        terminal_count = sum(1 for a in actions if a['action'] in TERMINAL_OUTCOMES)

        has_learned = data.get('learned_weights') is not None
        weights_version = len(data.get('weight_history', []))

        return {
            'total_actions': len(actions),
            'unique_opportunities': unique_opportunities,
            'terminal_outcomes': terminal_count,
            'actions_breakdown': dict(by_action),
            'has_learned_weights': has_learned,
            'weights_version': weights_version,
            'total_analyses': data['stats'].get('total_analyses', 0),
            'last_analysis': data['stats'].get('last_analysis'),
            'last_weight_update': data['stats'].get('last_weight_update'),
            'insights_count': len(data.get('insights', [])),
            'learning_readiness': self._assess_readiness(actions),
        }

    def _assess_readiness(self, actions: List[Dict]) -> Dict:
        """How ready is the system to learn? What does it need more of?"""
        total = len(actions)
        terminal = sum(1 for a in actions if a['action'] in TERMINAL_OUTCOMES)
        contacted = sum(1 for a in actions if a['action'] == 'contacted')
        positive = sum(1 for a in actions if a['action'] in POSITIVE_OUTCOMES)

        if total < 5:
            level = 'collecting'
            message = f'Need {5 - total} more actions before first analysis'
        elif terminal < 3:
            level = 'early'
            message = f'Need more outcomes (won/lost/skipped). Have {terminal}, want 3+'
        elif contacted < 5:
            level = 'learning'
            message = f'Building contact history. {contacted} contacts logged.'
        elif total >= 20 and terminal >= 5:
            level = 'mature'
            message = f'Strong data. {total} actions, {terminal} outcomes. Weights are data-driven.'
        else:
            level = 'growing'
            message = f'{total} actions tracked. More outcomes will sharpen the model.'

        return {
            'level': level,
            'message': message,
            'actions_needed': max(0, 5 - total),
            'outcomes_needed': max(0, 3 - terminal),
        }

    # ------------------------------------------------------------------
    # HELPERS
    # ------------------------------------------------------------------

    def _load_intelligence_data(self) -> Dict:
        """Load the main intelligence data for context."""
        intel_path = Path('/Users/deedavis/NEXUS BACKEND/intelligence_data.json')
        if intel_path.exists():
            with open(intel_path, 'r') as f:
                return json.load(f)
        return {}

    def _days_between(self, ts1: str, ts2: str) -> int:
        try:
            d1 = datetime.fromisoformat(ts1.replace('Z', '+00:00'))
            d2 = datetime.fromisoformat(ts2.replace('Z', '+00:00'))
            return abs((d2 - d1).days)
        except Exception:
            return 0

    def _value_range(self, value) -> str:
        try:
            value = float(value)
        except (TypeError, ValueError):
            return 'Unknown'
        if not value or value <= 0:
            return 'Unknown'
        if value < 1_000_000:
            return 'Under $1M'
        if value < 10_000_000:
            return '$1M - $10M'
        if value < 50_000_000:
            return '$10M - $50M'
        if value < 200_000_000:
            return '$50M - $200M'
        return 'Over $200M'


# ------------------------------------------------------------------
# MODULE-LEVEL CONVENIENCE FUNCTIONS
# ------------------------------------------------------------------

_engine = None

def get_learning_engine() -> IntelligenceLearningEngine:
    global _engine
    if _engine is None:
        _engine = IntelligenceLearningEngine()
    return _engine

def handle_log_action(opportunity_id: str, action: str, metadata: Dict = None) -> Dict:
    return get_learning_engine().log_action(opportunity_id, action, metadata)

def handle_run_analysis() -> Dict:
    return get_learning_engine().run_analysis()

def handle_get_insights(limit: int = 10) -> List[Dict]:
    return get_learning_engine().get_insights(limit)

def handle_get_learning_status() -> Dict:
    return get_learning_engine().get_learning_status()

def handle_get_active_weights() -> Dict:
    return get_learning_engine().get_active_weights()

def handle_get_opportunity_history(opportunity_id: str) -> List[Dict]:
    return get_learning_engine().get_opportunity_history(opportunity_id)
