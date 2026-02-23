import React, { useState, useCallback, useEffect } from 'react';
import {
  Shield, AlertTriangle, CheckCircle, Target, FileText, Award,
  ChevronDown, ChevronUp, Zap, AlertCircle, ArrowRight, BarChart3,
  BookOpen, RefreshCw, Trophy, XCircle
} from 'lucide-react';

// ─── Types ──────────────────────────────────────────────────────────────────

interface SubfactorAssessment {
  subfactor: string;
  addressed: boolean;
  strength: string;
}

interface FactorScore {
  name: string;
  weight: number;
  rating: string;
  score: number;
  weighted_score: number;
  subfactor_assessments: SubfactorAssessment[];
  strengths: string[];
  weaknesses: string[];
  evaluator_narrative: string;
  improvement_actions: string[];
  scoring_method: string;
  scoring_detail?: {
    coverage_pct: number;
    specificity_net: number;
    subfactor_pct: number;
    depth_score: number;
  };
}

interface CompositeScore {
  score: number;
  max_possible: number;
  rating: string;
  method: string;
  message: string;
  technically_acceptable?: boolean;
  failing_factors?: string[];
}

interface ImprovementItem {
  action: string;
  factor: string;
  current_rating: string;
  impact: string;
  weight: number;
}

interface Improvements {
  critical: ImprovementItem[];
  high: ImprovementItem[];
  medium: ImprovementItem[];
  total_actions: number;
}

interface RiskAssessment {
  level: string;
  auto_reject_risks: { factor: string; reason: string }[];
  critical_gaps: { factor: string; reason: string }[];
  message: string;
}

interface CompetitivePosition {
  position: string;
  score: number;
  edwosb_advantage: boolean;
  small_business_advantage: boolean;
  recommendation: string;
}

interface EvaluationResult {
  proposal_id: string;
  evaluation_method: string;
  method_name: string;
  factors: FactorScore[];
  composite: CompositeScore;
  improvements: Improvements;
  risk_assessment: RiskAssessment;
  competitive_position: CompetitivePosition;
  scored_at: string;
}

interface RFPAnalysis {
  evaluation_method: string;
  method_description: string;
  factors: { name: string; weight: number; subfactors: string[] }[];
  relative_importance_statement: string;
  special_considerations: string[];
  parse_method: string;
}

interface CalibrationData {
  total_evaluations: number;
  outcomes_recorded: number;
  rating_win_rates?: Record<string, { won: number; lost: number; win_rate: number }>;
  calibration_correlation?: number;
  message: string;
}

// ─── Constants ──────────────────────────────────────────────────────────────

const RATING_COLORS: Record<string, string> = {
  'Outstanding': '#16a34a',
  'Good': '#2563eb',
  'Acceptable': '#ca8a04',
  'Marginal': '#ea580c',
  'Unacceptable': '#dc2626',
};

const RATING_BG: Record<string, string> = {
  'Outstanding': 'rgba(22,163,74,0.15)',
  'Good': 'rgba(37,99,235,0.15)',
  'Acceptable': 'rgba(202,138,4,0.15)',
  'Marginal': 'rgba(234,88,12,0.15)',
  'Unacceptable': 'rgba(220,38,38,0.15)',
};

const RISK_COLORS: Record<string, string> = {
  'LOW': '#16a34a',
  'MODERATE': '#ca8a04',
  'HIGH': '#ea580c',
  'CRITICAL': '#dc2626',
};

const API_BASE = 'http://localhost:8000';

// ─── Sub-Components ─────────────────────────────────────────────────────────

const RatingBadge: React.FC<{ rating: string; size?: 'sm' | 'md' | 'lg' }> = ({ rating, size = 'md' }) => {
  const color = RATING_COLORS[rating] || '#6b7280';
  const bg = RATING_BG[rating] || 'rgba(107,114,128,0.15)';
  const sizes = { sm: '0.65rem', md: '0.75rem', lg: '0.9rem' };
  const pads = { sm: '2px 8px', md: '4px 12px', lg: '6px 16px' };
  return (
    <span style={{
      color, background: bg, border: `1px solid ${color}`,
      borderRadius: 6, padding: pads[size], fontSize: sizes[size],
      fontWeight: 700, letterSpacing: 0.5, textTransform: 'uppercase',
      whiteSpace: 'nowrap',
    }}>
      {rating}
    </span>
  );
};

const ScoreRing: React.FC<{ score: number; rating: string }> = ({ score, rating }) => {
  const color = RATING_COLORS[rating] || '#6b7280';
  const radius = 54;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (score / 100) * circumference;
  return (
    <div style={{ position: 'relative', width: 140, height: 140 }}>
      <svg width="140" height="140" viewBox="0 0 140 140">
        <circle cx="70" cy="70" r={radius} fill="none" stroke="#374151" strokeWidth="10" />
        <circle cx="70" cy="70" r={radius} fill="none" stroke={color} strokeWidth="10"
          strokeDasharray={circumference} strokeDashoffset={offset}
          strokeLinecap="round" transform="rotate(-90 70 70)"
          style={{ transition: 'stroke-dashoffset 0.8s ease' }} />
      </svg>
      <div style={{
        position: 'absolute', top: 0, left: 0, right: 0, bottom: 0,
        display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
      }}>
        <span style={{ fontSize: '2rem', fontWeight: 800, color }}>{Math.round(score)}</span>
        <span style={{ fontSize: '0.65rem', color: '#9ca3af', fontWeight: 600 }}>/ 100</span>
      </div>
    </div>
  );
};

const WeightBar: React.FC<{ score: number; weight: number; rating: string }> = ({ score, weight, rating }) => {
  const color = RATING_COLORS[rating] || '#6b7280';
  const pct = (score / 10) * 100;
  return (
    <div style={{ flex: 1 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.7rem', color: '#9ca3af', marginBottom: 3 }}>
        <span>{weight}% weight</span>
        <span>{score}/10</span>
      </div>
      <div style={{ height: 8, background: '#1f2937', borderRadius: 4, overflow: 'hidden' }}>
        <div style={{
          height: '100%', width: `${pct}%`, background: color, borderRadius: 4,
          transition: 'width 0.6s ease',
        }} />
      </div>
    </div>
  );
};

const FactorCard: React.FC<{
  factor: FactorScore;
  expanded: boolean;
  onToggle: () => void;
}> = ({ factor, expanded, onToggle }) => {
  const color = RATING_COLORS[factor.rating] || '#6b7280';
  return (
    <div style={{
      background: '#111827', border: `1px solid ${expanded ? color : '#374151'}`,
      borderRadius: 10, overflow: 'hidden', transition: 'border-color 0.3s',
    }}>
      <div onClick={onToggle} style={{
        padding: '14px 18px', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 14,
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, minWidth: 200 }}>
          <RatingBadge rating={factor.rating} size="sm" />
          <span style={{ fontWeight: 600, fontSize: '0.9rem', color: '#e5e7eb' }}>{factor.name}</span>
        </div>
        <WeightBar score={factor.score} weight={factor.weight} rating={factor.rating} />
        <div style={{ marginLeft: 8, color: '#6b7280' }}>
          {expanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
        </div>
      </div>

      {expanded && (
        <div style={{ padding: '0 18px 16px', borderTop: '1px solid #1f2937' }}>
          <div style={{
            margin: '12px 0', padding: '10px 14px', background: '#0f172a',
            borderRadius: 6, borderLeft: `3px solid ${color}`,
            fontSize: '0.8rem', color: '#d1d5db', fontStyle: 'italic', lineHeight: 1.5,
          }}>
            <BookOpen size={12} style={{ display: 'inline', marginRight: 6, opacity: 0.6 }} />
            {factor.evaluator_narrative}
          </div>

          {factor.subfactor_assessments.length > 0 && (
            <div style={{ marginBottom: 12 }}>
              <div style={{ fontSize: '0.7rem', fontWeight: 700, color: '#9ca3af', marginBottom: 6, textTransform: 'uppercase', letterSpacing: 1 }}>
                Subfactors
              </div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                {factor.subfactor_assessments.map((sf, i) => (
                  <span key={i} style={{
                    display: 'flex', alignItems: 'center', gap: 4, padding: '3px 10px',
                    background: sf.addressed ? 'rgba(22,163,74,0.1)' : 'rgba(220,38,38,0.1)',
                    border: `1px solid ${sf.addressed ? '#16a34a' : '#dc2626'}`,
                    borderRadius: 4, fontSize: '0.72rem',
                    color: sf.addressed ? '#4ade80' : '#f87171',
                  }}>
                    {sf.addressed ? <CheckCircle size={11} /> : <XCircle size={11} />}
                    {sf.subfactor}
                  </span>
                ))}
              </div>
            </div>
          )}

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
            {factor.strengths.length > 0 && (
              <div>
                <div style={{ fontSize: '0.7rem', fontWeight: 700, color: '#4ade80', marginBottom: 4 }}>STRENGTHS</div>
                {factor.strengths.map((s, i) => (
                  <div key={i} style={{ fontSize: '0.78rem', color: '#d1d5db', marginBottom: 3, paddingLeft: 10, borderLeft: '2px solid #16a34a' }}>
                    {s}
                  </div>
                ))}
              </div>
            )}
            {factor.weaknesses.length > 0 && (
              <div>
                <div style={{ fontSize: '0.7rem', fontWeight: 700, color: '#f87171', marginBottom: 4 }}>WEAKNESSES</div>
                {factor.weaknesses.map((w, i) => (
                  <div key={i} style={{ fontSize: '0.78rem', color: '#d1d5db', marginBottom: 3, paddingLeft: 10, borderLeft: '2px solid #dc2626' }}>
                    {w}
                  </div>
                ))}
              </div>
            )}
          </div>

          {factor.improvement_actions.length > 0 && (
            <div style={{ marginTop: 10 }}>
              <div style={{ fontSize: '0.7rem', fontWeight: 700, color: '#60a5fa', marginBottom: 4 }}>IMPROVEMENT ACTIONS</div>
              {factor.improvement_actions.map((a, i) => (
                <div key={i} style={{
                  display: 'flex', alignItems: 'flex-start', gap: 6, fontSize: '0.78rem',
                  color: '#93c5fd', marginBottom: 3,
                }}>
                  <ArrowRight size={12} style={{ marginTop: 3, flexShrink: 0 }} />
                  {a}
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

// ─── Main Component ─────────────────────────────────────────────────────────

export const EvaluatorScorecard: React.FC = () => {
  const [rfpText, setRfpText] = useState('');
  const [proposalText, setProposalText] = useState('');
  const [rfpAnalysis, setRfpAnalysis] = useState<RFPAnalysis | null>(null);
  const [evaluation, setEvaluation] = useState<EvaluationResult | null>(null);
  const [calibration, setCalibration] = useState<CalibrationData | null>(null);
  const [loading, setLoading] = useState('');
  const [expandedFactor, setExpandedFactor] = useState<string | null>(null);
  const [error, setError] = useState('');
  const [outcomeRecorded, setOutcomeRecorded] = useState(false);

  useEffect(() => {
    fetchCalibration();
  }, []);

  const fetchCalibration = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE}/api/evaluator/calibration`);
      if (res.ok) setCalibration(await res.json());
    } catch { /* backend may not be running */ }
  }, []);

  const handleParseRFP = useCallback(async () => {
    if (!rfpText.trim()) return;
    setLoading('parsing');
    setError('');
    try {
      const res = await fetch(`${API_BASE}/api/evaluator/parse-rfp`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ rfp_text: rfpText }),
      });
      const data = await res.json();
      if (data.error) throw new Error(data.error);
      setRfpAnalysis(data);
    } catch (err: any) {
      setError(err.message || 'Failed to parse RFP');
    }
    setLoading('');
  }, [rfpText]);

  const handleScore = useCallback(async () => {
    if (!proposalText.trim()) return;
    setLoading('scoring');
    setError('');
    setOutcomeRecorded(false);
    try {
      const res = await fetch(`${API_BASE}/api/evaluator/score`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          proposal_text: proposalText,
          rfp_analysis: rfpAnalysis || {},
          rfp_text: rfpText,
        }),
      });
      const data = await res.json();
      if (data.error) throw new Error(data.error);
      setEvaluation(data);
      setExpandedFactor(null);
    } catch (err: any) {
      setError(err.message || 'Failed to score proposal');
    }
    setLoading('');
  }, [proposalText, rfpAnalysis, rfpText]);

  const handleRecordOutcome = useCallback(async (won: boolean) => {
    if (!evaluation) return;
    try {
      await fetch(`${API_BASE}/api/evaluator/outcome`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ proposal_id: evaluation.proposal_id, won }),
      });
      setOutcomeRecorded(true);
      fetchCalibration();
    } catch { /* silently fail */ }
  }, [evaluation, fetchCalibration]);

  const ev = evaluation;
  const comp = ev?.composite;
  const risk = ev?.risk_assessment;
  const improvements = ev?.improvements;
  const position = ev?.competitive_position;

  return (
    <div style={{ maxWidth: 1000, margin: '0 auto' }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 20 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <Shield size={28} style={{ color: '#60a5fa' }} />
          <div>
            <h2 style={{ margin: 0, fontSize: '1.4rem', fontWeight: 800, color: '#f3f4f6' }}>
              Evaluator Scorecard
            </h2>
            <div style={{ fontSize: '0.75rem', color: '#9ca3af' }}>
              Score proposals the way government evaluators do — factor by factor
            </div>
          </div>
        </div>
        {calibration && (
          <div style={{
            display: 'flex', alignItems: 'center', gap: 8, padding: '6px 14px',
            background: '#1f2937', borderRadius: 8, border: '1px solid #374151',
          }}>
            <BarChart3 size={14} style={{ color: '#60a5fa' }} />
            <span style={{ fontSize: '0.72rem', color: '#9ca3af' }}>
              {calibration.total_evaluations} scored
              {calibration.outcomes_recorded > 0 && ` · ${calibration.outcomes_recorded} outcomes`}
            </span>
          </div>
        )}
      </div>

      {/* Input Section */}
      {!evaluation && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 20 }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 8 }}>
              <label style={{ fontSize: '0.8rem', fontWeight: 700, color: '#d1d5db' }}>
                <FileText size={13} style={{ display: 'inline', marginRight: 6 }} />
                RFP / Section M Text
              </label>
              <button
                onClick={handleParseRFP}
                disabled={!rfpText.trim() || loading === 'parsing'}
                style={{
                  padding: '4px 12px', borderRadius: 6, border: 'none', cursor: 'pointer',
                  background: rfpAnalysis ? '#16a34a' : '#2563eb', color: '#fff',
                  fontSize: '0.72rem', fontWeight: 600,
                  opacity: (!rfpText.trim() || loading === 'parsing') ? 0.4 : 1,
                }}
              >
                {loading === 'parsing' ? 'Parsing...' : rfpAnalysis ? 'Re-Parse' : 'Parse Factors'}
              </button>
            </div>
            <textarea
              value={rfpText}
              onChange={e => { setRfpText(e.target.value); setRfpAnalysis(null); }}
              placeholder="Paste RFP text here — especially Section L (Instructions) and Section M (Evaluation Factors)..."
              style={{
                width: '100%', height: 200, padding: 12, background: '#0f172a',
                border: '1px solid #374151', borderRadius: 8, color: '#e5e7eb',
                fontSize: '0.8rem', fontFamily: 'inherit', resize: 'vertical',
              }}
            />
            {rfpAnalysis && (
              <div style={{
                marginTop: 8, padding: '10px 14px', background: '#0f172a',
                borderRadius: 8, border: '1px solid #1e3a5f',
              }}>
                <div style={{ fontSize: '0.7rem', fontWeight: 700, color: '#60a5fa', marginBottom: 6 }}>
                  DETECTED: {rfpAnalysis.evaluation_method?.replace('_', ' ').toUpperCase()}
                  <span style={{ color: '#6b7280', fontWeight: 400, marginLeft: 8 }}>
                    via {rfpAnalysis.parse_method}
                  </span>
                </div>
                {rfpAnalysis.factors?.map((f, i) => (
                  <div key={i} style={{
                    display: 'flex', alignItems: 'center', gap: 8, fontSize: '0.75rem',
                    color: '#d1d5db', marginBottom: 3,
                  }}>
                    <span style={{
                      background: '#1e3a5f', padding: '1px 6px', borderRadius: 3,
                      fontSize: '0.65rem', fontWeight: 700, color: '#93c5fd', minWidth: 32,
                      textAlign: 'center',
                    }}>
                      {f.weight}%
                    </span>
                    {f.name}
                    {f.subfactors?.length > 0 && (
                      <span style={{ color: '#6b7280', fontSize: '0.65rem' }}>
                        ({f.subfactors.length} subfactors)
                      </span>
                    )}
                  </div>
                ))}
                {rfpAnalysis.special_considerations?.length > 0 && (
                  <div style={{ marginTop: 6, display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                    {rfpAnalysis.special_considerations.map((s, i) => (
                      <span key={i} style={{
                        fontSize: '0.65rem', padding: '2px 8px', background: 'rgba(22,163,74,0.15)',
                        border: '1px solid #16a34a', borderRadius: 4, color: '#4ade80',
                      }}>
                        {s}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>

          <div>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 8 }}>
              <label style={{ fontSize: '0.8rem', fontWeight: 700, color: '#d1d5db' }}>
                <Award size={13} style={{ display: 'inline', marginRight: 6 }} />
                Proposal Text
              </label>
              <button
                onClick={handleScore}
                disabled={!proposalText.trim() || loading === 'scoring'}
                style={{
                  padding: '4px 12px', borderRadius: 6, border: 'none', cursor: 'pointer',
                  background: '#8b5cf6', color: '#fff',
                  fontSize: '0.72rem', fontWeight: 600,
                  opacity: (!proposalText.trim() || loading === 'scoring') ? 0.4 : 1,
                }}
              >
                {loading === 'scoring' ? 'Evaluating...' : 'Evaluate Proposal'}
              </button>
            </div>
            <textarea
              value={proposalText}
              onChange={e => setProposalText(e.target.value)}
              placeholder="Paste your proposal text here — technical approach, past performance, staffing plan, etc..."
              style={{
                width: '100%', height: 200, padding: 12, background: '#0f172a',
                border: '1px solid #374151', borderRadius: 8, color: '#e5e7eb',
                fontSize: '0.8rem', fontFamily: 'inherit', resize: 'vertical',
              }}
            />
            {!rfpAnalysis && rfpText.length === 0 && (
              <div style={{ marginTop: 8, fontSize: '0.72rem', color: '#6b7280', fontStyle: 'italic' }}>
                Tip: Parse the RFP first for accurate factor-by-factor scoring. Without RFP text, standard evaluation factors are used.
              </div>
            )}
          </div>
        </div>
      )}

      {error && (
        <div style={{
          padding: '10px 14px', background: 'rgba(220,38,38,0.1)', border: '1px solid #dc2626',
          borderRadius: 8, color: '#f87171', fontSize: '0.8rem', marginBottom: 16,
        }}>
          <AlertCircle size={14} style={{ display: 'inline', marginRight: 6 }} />
          {error}
        </div>
      )}

      {/* Loading */}
      {loading && (
        <div style={{
          padding: 30, textAlign: 'center', color: '#9ca3af',
        }}>
          <RefreshCw size={24} style={{ animation: 'spin 1s linear infinite', marginBottom: 8 }} />
          <div style={{ fontSize: '0.85rem' }}>
            {loading === 'parsing' ? 'Parsing evaluation criteria...' : 'Scoring proposal against factors...'}
          </div>
          <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
        </div>
      )}

      {/* Results */}
      {ev && comp && !loading && (
        <>
          {/* Back to inputs */}
          <button
            onClick={() => setEvaluation(null)}
            style={{
              padding: '4px 12px', borderRadius: 6, border: '1px solid #374151',
              background: 'transparent', color: '#9ca3af', fontSize: '0.72rem',
              cursor: 'pointer', marginBottom: 16,
            }}
          >
            &larr; Back to input
          </button>

          {/* Top Scorecard */}
          <div style={{
            display: 'grid', gridTemplateColumns: '160px 1fr 1fr', gap: 20,
            padding: 20, background: '#111827', borderRadius: 12,
            border: `1px solid ${RISK_COLORS[risk?.level || 'LOW']}`, marginBottom: 20,
          }}>
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
              <ScoreRing score={comp.score} rating={comp.rating} />
              <RatingBadge rating={comp.rating} size="lg" />
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
              <div style={{ fontSize: '0.7rem', color: '#9ca3af', fontWeight: 600, textTransform: 'uppercase', letterSpacing: 1, marginBottom: 4 }}>
                Evaluation Method
              </div>
              <div style={{ fontSize: '0.95rem', color: '#e5e7eb', fontWeight: 700, marginBottom: 10 }}>
                {ev.method_name || ev.evaluation_method}
              </div>
              <div style={{ fontSize: '0.7rem', color: '#9ca3af', fontWeight: 600, textTransform: 'uppercase', letterSpacing: 1, marginBottom: 4 }}>
                Risk Level
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <span style={{
                  padding: '3px 10px', borderRadius: 4, fontWeight: 700, fontSize: '0.75rem',
                  color: RISK_COLORS[risk?.level || 'LOW'],
                  background: `${RISK_COLORS[risk?.level || 'LOW']}20`,
                  border: `1px solid ${RISK_COLORS[risk?.level || 'LOW']}`,
                }}>
                  {risk?.level}
                </span>
                {risk?.level === 'CRITICAL' && <AlertTriangle size={16} style={{ color: '#dc2626' }} />}
              </div>
              <div style={{ fontSize: '0.75rem', color: '#d1d5db', marginTop: 8, lineHeight: 1.4 }}>
                {risk?.message}
              </div>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
              <div style={{ fontSize: '0.7rem', color: '#9ca3af', fontWeight: 600, textTransform: 'uppercase', letterSpacing: 1, marginBottom: 4 }}>
                Competitive Position
              </div>
              <div style={{
                fontSize: '1rem', fontWeight: 800, marginBottom: 6,
                color: position?.position?.includes('Strong') ? '#4ade80'
                  : position?.position?.includes('Competitive') ? '#60a5fa'
                  : position?.position?.includes('Vulnerable') ? '#fbbf24' : '#f87171',
              }}>
                {position?.position}
              </div>
              {position?.edwosb_advantage && (
                <div style={{
                  display: 'inline-flex', alignItems: 'center', gap: 4,
                  padding: '2px 8px', background: 'rgba(139,92,246,0.15)',
                  border: '1px solid #8b5cf6', borderRadius: 4,
                  fontSize: '0.65rem', color: '#c4b5fd', marginBottom: 6, width: 'fit-content',
                }}>
                  <Zap size={10} /> EDWOSB Advantage Active
                </div>
              )}
              <div style={{ fontSize: '0.75rem', color: '#d1d5db', lineHeight: 1.4 }}>
                {position?.recommendation}
              </div>
            </div>
          </div>

          {/* Composite message */}
          <div style={{
            padding: '10px 16px', background: '#0f172a', borderRadius: 8,
            fontSize: '0.8rem', color: '#d1d5db', marginBottom: 20,
            borderLeft: `3px solid ${RATING_COLORS[comp.rating]}`,
          }}>
            {comp.message}
          </div>

          {/* Factor Cards */}
          <div style={{ marginBottom: 20 }}>
            <h3 style={{ fontSize: '0.85rem', fontWeight: 700, color: '#e5e7eb', marginBottom: 10 }}>
              <Target size={14} style={{ display: 'inline', marginRight: 6 }} />
              Factor-by-Factor Evaluation
            </h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              {ev.factors.map(f => (
                <FactorCard
                  key={f.name}
                  factor={f}
                  expanded={expandedFactor === f.name}
                  onToggle={() => setExpandedFactor(expandedFactor === f.name ? null : f.name)}
                />
              ))}
            </div>
          </div>

          {/* Improvement Plan */}
          {improvements && improvements.total_actions > 0 && (
            <div style={{
              padding: 18, background: '#111827', borderRadius: 12,
              border: '1px solid #374151', marginBottom: 20,
            }}>
              <h3 style={{ fontSize: '0.85rem', fontWeight: 700, color: '#e5e7eb', marginBottom: 14 }}>
                <Zap size={14} style={{ display: 'inline', marginRight: 6, color: '#fbbf24' }} />
                Improvement Plan ({improvements.total_actions} actions)
              </h3>

              {improvements.critical.length > 0 && (
                <div style={{ marginBottom: 14 }}>
                  <div style={{
                    fontSize: '0.7rem', fontWeight: 700, color: '#dc2626',
                    textTransform: 'uppercase', letterSpacing: 1, marginBottom: 6,
                  }}>
                    Critical — Fix Before Submission
                  </div>
                  {improvements.critical.map((item, i) => (
                    <div key={i} style={{
                      display: 'flex', alignItems: 'flex-start', gap: 10, padding: '8px 12px',
                      background: 'rgba(220,38,38,0.08)', borderRadius: 6, marginBottom: 4,
                      borderLeft: '3px solid #dc2626',
                    }}>
                      <AlertTriangle size={14} style={{ color: '#dc2626', marginTop: 2, flexShrink: 0 }} />
                      <div>
                        <div style={{ fontSize: '0.8rem', color: '#e5e7eb', fontWeight: 600 }}>{item.action}</div>
                        <div style={{ fontSize: '0.7rem', color: '#9ca3af' }}>
                          {item.factor} · {item.impact}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {improvements.high.length > 0 && (
                <div style={{ marginBottom: 14 }}>
                  <div style={{
                    fontSize: '0.7rem', fontWeight: 700, color: '#f59e0b',
                    textTransform: 'uppercase', letterSpacing: 1, marginBottom: 6,
                  }}>
                    High Priority — Significant Score Impact
                  </div>
                  {improvements.high.map((item, i) => (
                    <div key={i} style={{
                      display: 'flex', alignItems: 'flex-start', gap: 10, padding: '8px 12px',
                      background: 'rgba(245,158,11,0.08)', borderRadius: 6, marginBottom: 4,
                      borderLeft: '3px solid #f59e0b',
                    }}>
                      <ArrowRight size={14} style={{ color: '#f59e0b', marginTop: 2, flexShrink: 0 }} />
                      <div>
                        <div style={{ fontSize: '0.8rem', color: '#e5e7eb', fontWeight: 600 }}>{item.action}</div>
                        <div style={{ fontSize: '0.7rem', color: '#9ca3af' }}>
                          {item.factor} · {item.impact}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {improvements.medium.length > 0 && (
                <div>
                  <div style={{
                    fontSize: '0.7rem', fontWeight: 700, color: '#60a5fa',
                    textTransform: 'uppercase', letterSpacing: 1, marginBottom: 6,
                  }}>
                    Medium — Nice to Have
                  </div>
                  {improvements.medium.map((item, i) => (
                    <div key={i} style={{
                      display: 'flex', alignItems: 'flex-start', gap: 10, padding: '6px 12px',
                      fontSize: '0.78rem', color: '#d1d5db', marginBottom: 3,
                    }}>
                      <ArrowRight size={12} style={{ color: '#60a5fa', marginTop: 3, flexShrink: 0 }} />
                      <span>{item.action} <span style={{ color: '#6b7280' }}>({item.factor})</span></span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Learning Feedback */}
          <div style={{
            padding: 16, background: '#111827', borderRadius: 12,
            border: '1px solid #374151', marginBottom: 20,
          }}>
            <h3 style={{ fontSize: '0.85rem', fontWeight: 700, color: '#e5e7eb', marginBottom: 12 }}>
              <BarChart3 size={14} style={{ display: 'inline', marginRight: 6, color: '#8b5cf6' }} />
              Learning Feedback
            </h3>

            {!outcomeRecorded ? (
              <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                <span style={{ fontSize: '0.8rem', color: '#9ca3af' }}>
                  When the outcome is known:
                </span>
                <button onClick={() => handleRecordOutcome(true)} style={{
                  display: 'flex', alignItems: 'center', gap: 6, padding: '6px 16px',
                  background: 'rgba(22,163,74,0.15)', border: '1px solid #16a34a',
                  borderRadius: 6, color: '#4ade80', fontSize: '0.8rem', fontWeight: 600, cursor: 'pointer',
                }}>
                  <Trophy size={14} /> Won
                </button>
                <button onClick={() => handleRecordOutcome(false)} style={{
                  display: 'flex', alignItems: 'center', gap: 6, padding: '6px 16px',
                  background: 'rgba(220,38,38,0.1)', border: '1px solid #dc2626',
                  borderRadius: 6, color: '#f87171', fontSize: '0.8rem', fontWeight: 600, cursor: 'pointer',
                }}>
                  <XCircle size={14} /> Lost
                </button>
                <span style={{ fontSize: '0.7rem', color: '#6b7280' }}>
                  This feeds the learning engine to improve future scoring accuracy.
                </span>
              </div>
            ) : (
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, color: '#4ade80', fontSize: '0.8rem' }}>
                <CheckCircle size={16} />
                Outcome recorded. Model will calibrate on the next analysis cycle.
              </div>
            )}

            {calibration && calibration.outcomes_recorded > 0 && calibration.rating_win_rates && (
              <div style={{ marginTop: 14, paddingTop: 12, borderTop: '1px solid #1f2937' }}>
                <div style={{ fontSize: '0.7rem', fontWeight: 700, color: '#9ca3af', marginBottom: 8, textTransform: 'uppercase', letterSpacing: 1 }}>
                  Calibration — Win Rate by Our Predicted Rating
                </div>
                <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
                  {Object.entries(calibration.rating_win_rates).map(([rating, data]) => (
                    <div key={rating} style={{
                      padding: '6px 14px', background: '#0f172a', borderRadius: 6,
                      border: `1px solid ${RATING_COLORS[rating] || '#374151'}`,
                      textAlign: 'center', minWidth: 90,
                    }}>
                      <div style={{ fontSize: '0.65rem', color: RATING_COLORS[rating], fontWeight: 700, marginBottom: 2 }}>
                        {rating}
                      </div>
                      <div style={{ fontSize: '1rem', fontWeight: 800, color: '#e5e7eb' }}>
                        {data.win_rate}%
                      </div>
                      <div style={{ fontSize: '0.6rem', color: '#6b7280' }}>
                        {data.won}W / {data.lost}L
                      </div>
                    </div>
                  ))}
                </div>
                <div style={{ fontSize: '0.72rem', color: '#9ca3af', marginTop: 8 }}>
                  {calibration.message}
                </div>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
};

export default EvaluatorScorecard;
