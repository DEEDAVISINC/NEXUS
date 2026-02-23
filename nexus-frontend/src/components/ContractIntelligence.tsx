import React, { useState, useEffect, useCallback } from 'react';
import {
  Target, Users, Building2, RefreshCw, ChevronDown, ChevronRight,
  Mail, Phone, Filter, Zap, Shield, Briefcase, ArrowRight,
  Database, BarChart3, Globe, Brain, Activity, CheckCircle,
  XCircle, Eye, Send, Clock, Lightbulb, TrendingUp
} from 'lucide-react';

const API_BASE = process.env.REACT_APP_API_BASE || 'http://127.0.0.1:8000';

interface PipelineItem {
  id: string;
  award_id: string;
  agency: string;
  incumbent: string;
  lane: string;
  value: number;
  value_display: string;
  expiry: string;
  is_priority_lane: boolean;
  prime_company: string;
  prime_contact: string;
  prime_email: string;
  prime_phone: string;
  has_contact: boolean;
  best_avenue: string;
  score: number;
  sub_score: number;
  prime_score: number;
  hire_score: number;
  action: string;
}

interface Avenue {
  title: string;
  subtitle: string;
  color: string;
  count: number;
  items: PipelineItem[];
}

interface PipelineData {
  last_ingested: string;
  total_opportunities: number;
  avenues: {
    sub_under_prime: Avenue;
    prime_recompete: Avenue;
    hire_subs: Avenue;
  };
  stats: {
    total_expiring: number;
    ddi_lane_matches: number;
    primes_in_directory: number;
    subs_in_directory: number;
    cross_ref_matches: number;
    by_lane: Record<string, number>;
    by_agency: Record<string, number>;
  };
}

interface DomainStatus {
  name: string;
  events: number;
  entities: number;
  positive: number;
  negative: number;
  positive_rate: number;
  level: string;
  has_learned_weights: boolean;
  weights_version: number;
}

interface LearningStatus {
  total_events: number;
  total_domains_active: number;
  total_analyses: number;
  last_analysis: string | null;
  last_weight_update: string | null;
  insights_count: number;
  domains: Record<string, DomainStatus>;
  system_readiness: {
    level: string;
    message: string;
    active_domains: number;
    mature_domains: number;
    total_events: number;
  };
}

interface Insight {
  title: string;
  body: string;
  impact: string;
  category: string;
  generated_at?: string;
}

const AVENUE_CONFIG: Record<string, { icon: React.ReactNode; gradient: string; border: string; badge: string }> = {
  sub_under_prime: {
    icon: <Shield className="w-6 h-6" />,
    gradient: 'from-blue-600/20 to-blue-900/10',
    border: 'border-blue-500/30',
    badge: 'bg-blue-500/20 text-blue-300',
  },
  prime_recompete: {
    icon: <Target className="w-6 h-6" />,
    gradient: 'from-purple-600/20 to-purple-900/10',
    border: 'border-purple-500/30',
    badge: 'bg-purple-500/20 text-purple-300',
  },
  hire_subs: {
    icon: <Users className="w-6 h-6" />,
    gradient: 'from-amber-600/20 to-amber-900/10',
    border: 'border-amber-500/30',
    badge: 'bg-amber-500/20 text-amber-300',
  },
};

const LANE_COLORS: Record<string, string> = {
  'Facilities Support': 'bg-emerald-500/20 text-emerald-300',
  'Janitorial': 'bg-teal-500/20 text-teal-300',
  'Landscaping / Grounds': 'bg-green-500/20 text-green-300',
  'Medical Labs / Drug Testing': 'bg-red-500/20 text-red-300',
  'Courier / Express Delivery': 'bg-violet-500/20 text-violet-300',
  'Temp Staffing': 'bg-cyan-500/20 text-cyan-300',
  'Security Guards': 'bg-orange-500/20 text-orange-300',
  'Office Admin': 'bg-sky-500/20 text-sky-300',
  'Engineering Services': 'bg-indigo-500/20 text-indigo-300',
  'Freight Transport Arrangement': 'bg-fuchsia-500/20 text-fuchsia-300',
};

const ACTION_BUTTONS = [
  { action: 'reviewed', label: 'Reviewed', icon: <Eye className="w-3 h-3" />, color: 'bg-gray-600 hover:bg-gray-500' },
  { action: 'contacted', label: 'Contacted', icon: <Send className="w-3 h-3" />, color: 'bg-blue-600 hover:bg-blue-500' },
  { action: 'responded', label: 'Got Response', icon: <Mail className="w-3 h-3" />, color: 'bg-emerald-600 hover:bg-emerald-500' },
  { action: 'pursuing', label: 'Pursuing', icon: <TrendingUp className="w-3 h-3" />, color: 'bg-purple-600 hover:bg-purple-500' },
  { action: 'won', label: 'Won', icon: <CheckCircle className="w-3 h-3" />, color: 'bg-green-600 hover:bg-green-500' },
  { action: 'lost', label: 'Lost', icon: <XCircle className="w-3 h-3" />, color: 'bg-red-600 hover:bg-red-500' },
  { action: 'skipped', label: 'Skip', icon: <XCircle className="w-3 h-3" />, color: 'bg-gray-700 hover:bg-gray-600' },
  { action: 'no_response', label: 'No Response', icon: <Clock className="w-3 h-3" />, color: 'bg-amber-700 hover:bg-amber-600' },
];

const READINESS_COLORS: Record<string, string> = {
  collecting: 'text-gray-400',
  early: 'text-amber-400',
  learning: 'text-blue-400',
  growing: 'text-purple-400',
  mature: 'text-emerald-400',
};

export const ContractIntelligence: React.FC = () => {
  const [pipeline, setPipeline] = useState<PipelineData | null>(null);
  const [learning, setLearning] = useState<LearningStatus | null>(null);
  const [insights, setInsights] = useState<Insight[]>([]);
  const [loading, setLoading] = useState(true);
  const [ingesting, setIngesting] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [expandedAvenues, setExpandedAvenues] = useState<Record<string, boolean>>({
    sub_under_prime: true,
    prime_recompete: false,
    hire_subs: false,
  });
  const [laneFilter, setLaneFilter] = useState<string>('');
  const [showFilters, setShowFilters] = useState(false);
  const [showInsights, setShowInsights] = useState(false);
  const [generatingTasks, setGeneratingTasks] = useState<string | null>(null);
  const [taskResult, setTaskResult] = useState<{ avenue: string; count: number } | null>(null);
  const [actionToast, setActionToast] = useState<string | null>(null);

  const fetchPipeline = useCallback(async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      if (laneFilter) params.set('lane', laneFilter);
      params.set('min_score', '0');
      const res = await fetch(`${API_BASE}/api/intelligence/contracts/pipeline?${params}`);
      const data = await res.json();
      setPipeline(data);
    } catch (err) {
      console.error('Pipeline fetch failed:', err);
    } finally {
      setLoading(false);
    }
  }, [laneFilter]);

  const fetchLearning = useCallback(async () => {
    try {
      const [statusRes, insightsRes] = await Promise.all([
        fetch(`${API_BASE}/api/learning/status`),
        fetch(`${API_BASE}/api/learning/insights?domain=intelligence&limit=5`),
      ]);
      const status = await statusRes.json();
      const insData = await insightsRes.json();
      setLearning(status);
      setInsights(insData.insights || []);
    } catch (err) {
      console.error('Learning status fetch failed:', err);
    }
  }, []);

  useEffect(() => {
    fetchPipeline();
    fetchLearning();
  }, [fetchPipeline, fetchLearning]);

  const handleIngest = async () => {
    setIngesting(true);
    try {
      await fetch(`${API_BASE}/api/intelligence/contracts/ingest`, { method: 'POST' });
      await fetchPipeline();
    } catch (err) {
      console.error('Ingest failed:', err);
    } finally {
      setIngesting(false);
    }
  };

  const handleAnalyze = async () => {
    setAnalyzing(true);
    try {
      const res = await fetch(`${API_BASE}/api/learning/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ domain: null }),
      });
      const data = await res.json();
      if (data.status === 'complete') {
        setActionToast(`AI analysis complete — ${data.insights_generated} insights generated${data.weights_updated ? ', scoring weights updated' : ''}`);
        await fetchLearning();
        if (data.weights_updated) await fetchPipeline();
      } else {
        setActionToast(data.message || 'Analysis requires more data');
      }
      setTimeout(() => setActionToast(null), 6000);
    } catch (err) {
      console.error('Analysis failed:', err);
    } finally {
      setAnalyzing(false);
    }
  };

  const handleLogAction = async (opportunityId: string, action: string, metadata: Record<string, string>) => {
    try {
      await fetch(`${API_BASE}/api/learning/log`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ domain: 'intelligence', entity_id: opportunityId, action, metadata }),
      });
      setActionToast(`Logged: ${action} — system is learning`);
      setTimeout(() => setActionToast(null), 3000);
      fetchLearning();
    } catch (err) {
      console.error('Log action failed:', err);
    }
  };

  const handleGenerateTasks = async (avenue: string) => {
    setGeneratingTasks(avenue);
    try {
      const res = await fetch(`${API_BASE}/api/intelligence/contracts/generate-tasks`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ avenue, limit: 10 }),
      });
      const data = await res.json();
      setTaskResult({ avenue, count: data.tasks_created || 0 });
      setTimeout(() => setTaskResult(null), 5000);
    } catch (err) {
      console.error('Task generation failed:', err);
    } finally {
      setGeneratingTasks(null);
    }
  };

  const toggleAvenue = (key: string) => {
    setExpandedAvenues(prev => ({ ...prev, [key]: !prev[key] }));
  };

  if (loading && !pipeline) {
    return (
      <div className="flex items-center justify-center py-20">
        <RefreshCw className="w-6 h-6 animate-spin text-blue-400 mr-3" />
        <span className="text-gray-400">Loading contract intelligence...</span>
      </div>
    );
  }

  if (!pipeline || pipeline.total_opportunities === 0) {
    return (
      <div className="text-center py-16">
        <Database className="w-12 h-12 text-gray-600 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-300 mb-2">No Intelligence Data</h3>
        <p className="text-gray-500 mb-6">Ingest GovCon Giants data to populate the pipeline</p>
        <button
          onClick={handleIngest}
          disabled={ingesting}
          className="px-6 py-3 bg-blue-600 hover:bg-blue-500 rounded-lg font-medium transition flex items-center gap-2 mx-auto"
        >
          {ingesting ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Zap className="w-4 h-4" />}
          {ingesting ? 'Ingesting...' : 'Ingest Intelligence Data'}
        </button>
      </div>
    );
  }

  const { stats } = pipeline;
  const lanes = Object.entries(stats.by_lane || {});

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Globe className="w-6 h-6 text-blue-400" />
            Contract Intelligence
          </h2>
          <p className="text-sm text-gray-400 mt-1">
            Three-avenue pipeline — self-learning scoring from your actions
          </p>
        </div>
        <div className="flex items-center gap-2">
          {learning && (
            <LearningBadge status={learning} onAnalyze={handleAnalyze} analyzing={analyzing} />
          )}
          <button
            onClick={() => setShowInsights(!showInsights)}
            className={`p-2 rounded-lg transition ${showInsights ? 'bg-purple-600' : 'bg-gray-700 hover:bg-gray-600'}`}
            title="AI Insights"
          >
            <Lightbulb className="w-4 h-4" />
          </button>
          <button
            onClick={() => setShowFilters(!showFilters)}
            className={`p-2 rounded-lg transition ${showFilters ? 'bg-blue-600' : 'bg-gray-700 hover:bg-gray-600'}`}
          >
            <Filter className="w-4 h-4" />
          </button>
          <button
            onClick={handleIngest}
            disabled={ingesting}
            className="p-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition"
            title="Re-ingest data"
          >
            <RefreshCw className={`w-4 h-4 ${ingesting ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Toast */}
      {actionToast && (
        <div className="bg-blue-900/30 border border-blue-500/30 rounded-xl px-4 py-3 flex items-center gap-3 animate-pulse">
          <Brain className="w-5 h-5 text-blue-400" />
          <span className="text-blue-300 text-sm font-medium">{actionToast}</span>
        </div>
      )}
      {taskResult && (
        <div className="bg-emerald-900/30 border border-emerald-500/30 rounded-xl px-4 py-3 flex items-center gap-3">
          <Zap className="w-5 h-5 text-emerald-400" />
          <span className="text-emerald-300 text-sm font-medium">
            {taskResult.count} outreach tasks created for {taskResult.avenue.replace(/_/g, ' ')}
          </span>
        </div>
      )}

      {/* Stats Bar */}
      <div className="grid grid-cols-5 gap-3">
        <StatCard label="Expiring Contracts" value={stats.total_expiring} icon={<BarChart3 className="w-4 h-4" />} color="text-gray-300" />
        <StatCard label="DDI Lane Matches" value={stats.ddi_lane_matches} icon={<Target className="w-4 h-4" />} color="text-blue-400" />
        <StatCard label="Primes w/ SBLO" value={stats.primes_in_directory} icon={<Building2 className="w-4 h-4" />} color="text-purple-400" />
        <StatCard label="Tier 2 Subs" value={stats.subs_in_directory} icon={<Users className="w-4 h-4" />} color="text-amber-400" />
        <StatCard
          label="Events Tracked"
          value={learning?.total_events || 0}
          icon={<Brain className="w-4 h-4" />}
          color="text-emerald-400"
          subtitle={`${learning?.total_domains_active || 0} domains active`}
        />
      </div>

      {/* Insights Panel */}
      {showInsights && (
        <InsightsPanel
          insights={insights}
          learning={learning}
          onAnalyze={handleAnalyze}
          analyzing={analyzing}
        />
      )}

      {/* Lane Filter */}
      {showFilters && (
        <div className="bg-gray-800/50 border border-gray-700/50 rounded-xl p-4">
          <div className="text-xs text-gray-400 mb-2 font-medium">FILTER BY SERVICE LANE</div>
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => setLaneFilter('')}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition ${
                !laneFilter ? 'bg-blue-600 text-white' : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            >
              All Lanes ({stats.ddi_lane_matches})
            </button>
            {lanes.slice(0, 12).map(([lane, count]) => (
              <button
                key={lane}
                onClick={() => setLaneFilter(lane === laneFilter ? '' : lane)}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium transition ${
                  lane === laneFilter ? 'bg-blue-600 text-white' : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                }`}
              >
                {lane} ({count})
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Three Avenue Sections */}
      {Object.entries(pipeline.avenues).map(([key, avenue]) => {
        const config = AVENUE_CONFIG[key];
        const isExpanded = expandedAvenues[key];

        return (
          <div key={key} className={`bg-gradient-to-r ${config.gradient} border ${config.border} rounded-xl overflow-hidden`}>
            <div
              className="flex items-center justify-between px-5 py-4 cursor-pointer hover:bg-white/5 transition"
              onClick={() => toggleAvenue(key)}
            >
              <div className="flex items-center gap-3">
                <div className={config.badge + ' p-2 rounded-lg'}>
                  {config.icon}
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <h3 className="font-bold text-white">{avenue.title}</h3>
                    <span className={`${config.badge} px-2 py-0.5 rounded-full text-xs font-bold`}>
                      {avenue.count}
                    </span>
                  </div>
                  <p className="text-xs text-gray-400">{avenue.subtitle}</p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={(e) => { e.stopPropagation(); handleGenerateTasks(key); }}
                  disabled={generatingTasks === key}
                  className="px-3 py-1.5 bg-gray-700/50 hover:bg-gray-600/50 rounded-lg text-xs font-medium transition flex items-center gap-1.5"
                >
                  {generatingTasks === key ? <RefreshCw className="w-3 h-3 animate-spin" /> : <Briefcase className="w-3 h-3" />}
                  Create Tasks
                </button>
                {isExpanded ? <ChevronDown className="w-5 h-5 text-gray-400" /> : <ChevronRight className="w-5 h-5 text-gray-400" />}
              </div>
            </div>

            {isExpanded && (
              <div className="border-t border-gray-700/30">
                {avenue.items.length === 0 ? (
                  <div className="px-5 py-8 text-center text-gray-500 text-sm">
                    No opportunities in this avenue{laneFilter ? ` for "${laneFilter}"` : ''}
                  </div>
                ) : (
                  avenue.items.slice(0, 25).map((item) => (
                    <OpportunityRow
                      key={item.id + item.award_id}
                      item={item}
                      avenueKey={key}
                      onLogAction={handleLogAction}
                    />
                  ))
                )}
                {avenue.items.length > 25 && (
                  <div className="px-5 py-3 text-center text-xs text-gray-500 border-t border-gray-700/30">
                    Showing top 25 of {avenue.count} opportunities
                  </div>
                )}
              </div>
            )}
          </div>
        );
      })}

      {/* Agencies Breakdown */}
      <div className="bg-gray-800/40 border border-gray-700/30 rounded-xl p-5">
        <h3 className="font-bold text-white mb-3 flex items-center gap-2">
          <Building2 className="w-4 h-4 text-gray-400" />
          Top Agencies
        </h3>
        <div className="grid grid-cols-2 gap-2">
          {Object.entries(stats.by_agency || {}).map(([agency, count]) => (
            <div key={agency} className="flex items-center justify-between bg-gray-700/30 rounded-lg px-3 py-2">
              <span className="text-sm text-gray-300 truncate">{agency}</span>
              <span className="text-xs text-gray-400 font-mono ml-2">{count}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

// -- Learning Badge (top right of header) --
const LearningBadge: React.FC<{
  status: LearningStatus;
  onAnalyze: () => void;
  analyzing: boolean;
}> = ({ status, onAnalyze, analyzing }) => {
  const readiness = status.system_readiness;
  const color = READINESS_COLORS[readiness.level] || 'text-gray-400';

  return (
    <button
      onClick={onAnalyze}
      disabled={analyzing}
      className="flex items-center gap-2 px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg hover:bg-gray-700 transition"
      title={readiness.message}
    >
      {analyzing ? (
        <RefreshCw className="w-4 h-4 animate-spin text-purple-400" />
      ) : (
        <Brain className={`w-4 h-4 ${color}`} />
      )}
      <div className="text-left">
        <div className="text-[10px] text-gray-500 uppercase tracking-wider leading-none">NEXUS Brain</div>
        <div className={`text-xs font-medium leading-tight ${color}`}>
          {readiness.active_domains}/{Object.keys(status.domains || {}).length} domains
          {status.total_events > 0 && (
            <span className="text-gray-500 ml-1">({status.total_events} events)</span>
          )}
        </div>
      </div>
      {readiness.level === 'intelligent' && (
        <Activity className="w-3 h-3 text-emerald-400" />
      )}
    </button>
  );
};

// -- Insights Panel --
const InsightsPanel: React.FC<{
  insights: Insight[];
  learning: LearningStatus | null;
  onAnalyze: () => void;
  analyzing: boolean;
}> = ({ insights, learning, onAnalyze, analyzing }) => {
  const readiness = learning?.system_readiness;

  return (
    <div className="bg-gray-800/60 border border-purple-500/20 rounded-xl p-5 space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="font-bold text-white flex items-center gap-2">
          <Lightbulb className="w-5 h-5 text-purple-400" />
          AI Insights
        </h3>
        <button
          onClick={onAnalyze}
          disabled={analyzing}
          className="px-3 py-1.5 bg-purple-600 hover:bg-purple-500 rounded-lg text-xs font-medium transition flex items-center gap-1.5"
        >
          {analyzing ? <RefreshCw className="w-3 h-3 animate-spin" /> : <Brain className="w-3 h-3" />}
          {analyzing ? 'Analyzing...' : 'Run Analysis'}
        </button>
      </div>

      {/* System readiness */}
      {readiness && (
        <div className={`text-xs px-3 py-2 rounded-lg bg-gray-700/50 ${READINESS_COLORS[readiness.level] || 'text-gray-400'}`}>
          <span className="font-medium uppercase tracking-wider">{readiness.level}</span>
          <span className="text-gray-400 ml-2">{readiness.message}</span>
        </div>
      )}

      {/* Domain-level learning status */}
      {learning && Object.keys(learning.domains || {}).length > 0 && (
        <div>
          <div className="text-xs text-gray-500 mb-2 font-medium">LEARNING BY MODULE</div>
          <div className="grid grid-cols-2 gap-2">
            {Object.entries(learning.domains).map(([key, dom]) => {
              const domColor = READINESS_COLORS[dom.level] || 'text-gray-500';
              return (
                <div key={key} className="bg-gray-700/30 rounded-lg px-3 py-2 flex items-center justify-between">
                  <div>
                    <div className="text-xs text-gray-300 font-medium">{dom.name}</div>
                    <div className={`text-[10px] ${domColor}`}>
                      {dom.level} — {dom.events} events
                      {dom.has_learned_weights && <span className="text-emerald-500 ml-1">(v{dom.weights_version})</span>}
                    </div>
                  </div>
                  {dom.events > 0 && (
                    <div className="text-right">
                      <div className="text-xs font-mono text-gray-300">{(dom.positive_rate * 100).toFixed(0)}%</div>
                      <div className="text-[9px] text-gray-500">positive</div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* System stats */}
      {learning && (
        <div className="grid grid-cols-3 gap-3 text-center">
          <div className="bg-gray-700/30 rounded-lg p-2">
            <div className="text-lg font-bold text-white">{learning.total_events}</div>
            <div className="text-[10px] text-gray-500 uppercase">Total Events</div>
          </div>
          <div className="bg-gray-700/30 rounded-lg p-2">
            <div className="text-lg font-bold text-white">{learning.total_domains_active}</div>
            <div className="text-[10px] text-gray-500 uppercase">Active Domains</div>
          </div>
          <div className="bg-gray-700/30 rounded-lg p-2">
            <div className="text-lg font-bold text-white">{learning.total_analyses}</div>
            <div className="text-[10px] text-gray-500 uppercase">Analyses Run</div>
          </div>
        </div>
      )}

      {/* AI Insights */}
      {insights.length > 0 ? (
        <div className="space-y-3">
          <div className="text-xs text-gray-500 font-medium">AI-GENERATED INSIGHTS</div>
          {insights.map((insight, i) => (
            <div key={i} className="bg-gray-700/30 rounded-lg p-3 border-l-2 border-purple-500/50">
              <div className="flex items-center gap-2 mb-1">
                <span className={`text-xs font-bold uppercase ${
                  insight.impact === 'high' ? 'text-red-400' :
                  insight.impact === 'medium' ? 'text-amber-400' : 'text-gray-400'
                }`}>
                  {insight.impact}
                </span>
                <span className="text-xs text-gray-500">{insight.category}</span>
              </div>
              <div className="text-sm font-medium text-white">{insight.title}</div>
              <div className="text-xs text-gray-300 mt-1">{insight.body}</div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-4 text-gray-500 text-sm">
          No insights yet. Log actions on opportunities and run analysis.
        </div>
      )}
    </div>
  );
};

// -- Stat Card --
const StatCard: React.FC<{
  label: string;
  value: number;
  icon: React.ReactNode;
  color: string;
  subtitle?: string;
}> = ({ label, value, icon, color, subtitle }) => (
  <div className="bg-gray-800/50 border border-gray-700/30 rounded-xl px-4 py-3">
    <div className="flex items-center gap-2 mb-1">
      <span className={color}>{icon}</span>
      <span className="text-xs text-gray-500 uppercase tracking-wide">{label}</span>
    </div>
    <div className={`text-2xl font-bold ${color}`}>{value.toLocaleString()}</div>
    {subtitle && <div className="text-[10px] text-gray-500 mt-0.5">{subtitle}</div>}
  </div>
);

// -- Opportunity Row with Action Buttons --
const OpportunityRow: React.FC<{
  item: PipelineItem;
  avenueKey: string;
  onLogAction: (id: string, action: string, metadata: Record<string, string>) => void;
}> = ({ item, avenueKey, onLogAction }) => {
  const [expanded, setExpanded] = useState(false);
  const laneColor = LANE_COLORS[item.lane] || 'bg-gray-500/20 text-gray-300';

  const handleAction = (action: string) => {
    onLogAction(item.id, action, {
      lane: item.lane,
      agency: item.agency,
      avenue: avenueKey,
      value: String(item.value),
      incumbent: item.incumbent,
      prime: item.prime_company,
    });
  };

  return (
    <div className="border-b border-gray-700/20 last:border-0">
      <div
        className="flex items-center gap-3 px-5 py-3 hover:bg-white/5 transition cursor-pointer"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="font-medium text-sm text-white truncate">
              {avenueKey === 'sub_under_prime' && item.prime_company
                ? item.prime_company
                : item.incumbent}
            </span>
            <span className={`px-2 py-0.5 rounded-full text-[10px] font-medium ${laneColor}`}>
              {item.lane}
            </span>
            {item.is_priority_lane && (
              <span className="px-1.5 py-0.5 rounded bg-yellow-500/20 text-yellow-300 text-[10px] font-bold">
                PRIORITY
              </span>
            )}
          </div>
          <div className="flex items-center gap-3 mt-0.5">
            <span className="text-xs text-gray-500">{item.agency}</span>
            {item.has_contact && (
              <span className="text-[10px] text-emerald-500 font-medium flex items-center gap-1">
                <Mail className="w-3 h-3" /> Contact Available
              </span>
            )}
          </div>
        </div>
        <div className="text-right flex-shrink-0">
          <div className="text-sm font-mono text-gray-300">{item.value_display}</div>
          <div className="text-[10px] text-gray-500">Exp: {item.expiry}</div>
        </div>
        <div className="flex-shrink-0 w-8 text-center">
          <div className={`text-xs font-bold ${item.score >= 70 ? 'text-emerald-400' : item.score >= 50 ? 'text-blue-400' : 'text-gray-400'}`}>
            {item.score}
          </div>
        </div>
        {expanded ? <ChevronDown className="w-4 h-4 text-gray-500 flex-shrink-0" /> : <ChevronRight className="w-4 h-4 text-gray-500 flex-shrink-0" />}
      </div>

      {expanded && (
        <div className="px-5 pb-4 bg-gray-800/30">
          <div className="grid grid-cols-2 gap-4 text-xs">
            <div>
              <div className="text-gray-500 mb-1 font-medium uppercase tracking-wider">Contract Details</div>
              <div className="space-y-1">
                <div><span className="text-gray-400">Award:</span> <span className="text-gray-200 font-mono">{item.award_id}</span></div>
                <div><span className="text-gray-400">Incumbent:</span> <span className="text-gray-200">{item.incumbent}</span></div>
                <div><span className="text-gray-400">Value:</span> <span className="text-gray-200">{item.value_display}</span></div>
                <div><span className="text-gray-400">Expires:</span> <span className="text-gray-200">{item.expiry}</span></div>
              </div>
            </div>
            <div>
              <div className="text-gray-500 mb-1 font-medium uppercase tracking-wider">
                {item.has_contact ? 'Prime SBLO Contact' : 'Avenue Scores'}
              </div>
              {item.has_contact ? (
                <div className="space-y-1">
                  {item.prime_contact && <div><span className="text-gray-400">Name:</span> <span className="text-gray-200">{item.prime_contact}</span></div>}
                  {item.prime_email && (
                    <div className="flex items-center gap-1">
                      <Mail className="w-3 h-3 text-blue-400" />
                      <span className="text-blue-300 font-mono">{item.prime_email}</span>
                    </div>
                  )}
                  {item.prime_phone && (
                    <div className="flex items-center gap-1">
                      <Phone className="w-3 h-3 text-emerald-400" />
                      <span className="text-emerald-300 font-mono">{item.prime_phone}</span>
                    </div>
                  )}
                </div>
              ) : (
                <div className="space-y-1">
                  <div><span className="text-gray-400">Sub Score:</span> <span className="text-blue-300">{item.sub_score}</span></div>
                  <div><span className="text-gray-400">Prime Score:</span> <span className="text-purple-300">{item.prime_score}</span></div>
                  <div><span className="text-gray-400">Hire Score:</span> <span className="text-amber-300">{item.hire_score}</span></div>
                </div>
              )}
            </div>
          </div>

          <div className="mt-3 flex items-center gap-2 text-xs">
            <ArrowRight className="w-3 h-3 text-gray-500" />
            <span className="text-gray-300 font-medium">{item.action}</span>
          </div>

          {/* Action Buttons — this is how the system learns */}
          <div className="mt-3 pt-3 border-t border-gray-700/30">
            <div className="text-[10px] text-gray-500 mb-2 uppercase tracking-wider">Log Action (trains the AI)</div>
            <div className="flex flex-wrap gap-1.5">
              {ACTION_BUTTONS.map(btn => (
                <button
                  key={btn.action}
                  onClick={(e) => { e.stopPropagation(); handleAction(btn.action); }}
                  className={`${btn.color} px-2.5 py-1 rounded text-[11px] font-medium transition flex items-center gap-1`}
                >
                  {btn.icon}
                  {btn.label}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ContractIntelligence;
