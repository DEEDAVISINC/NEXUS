import React, { useState, useEffect, useCallback } from 'react';

const API = process.env.REACT_APP_API_URL || 'http://localhost:8000';

interface Milestone {
  id: string;
  name: string;
  description: string;
  achieved_at?: string;
}

interface Brief {
  growth_stats: Record<string, number>;
  win_rate: number;
  total_bids: number;
  milestones_achieved: Milestone[];
  milestones_next: Milestone[];
  most_used_systems: [string, number][];
  underutilized_systems: string[];
  knowledge_coverage: number;
  topics_learned: number;
  total_topics_available: number;
  total_lessons_delivered: number;
  patterns: string[];
}

interface KnowledgeSystem {
  system: string;
  name: string;
  action_count: number;
  actions: { action: string; key_concept: string; has_far_reference: boolean }[];
}

interface TeachResult {
  has_advice: boolean;
  system?: string;
  action?: string;
  teach?: string;
  key_concept?: string;
  far_reference?: string | null;
  is_new_topic?: boolean;
}

interface DebriefResult {
  has_debrief: boolean;
  title?: string;
  prompts?: string[];
  next_actions?: string[];
  current_record?: {
    total_bids: number;
    wins: number;
    losses: number;
    win_rate: number;
    total_value: number;
  };
  milestones_earned?: Milestone[];
}

const StatCard: React.FC<{ label: string; value: string | number; sub?: string }> = ({ label, value, sub }) => (
  <div className="bg-gray-800/50 rounded-xl p-4 border border-gray-700/50">
    <div className="text-2xl font-bold text-white">{value}</div>
    <div className="text-sm text-gray-400">{label}</div>
    {sub && <div className="text-xs text-gray-500 mt-1">{sub}</div>}
  </div>
);

const MilestoneBadge: React.FC<{ milestone: Milestone; achieved?: boolean }> = ({ milestone, achieved }) => (
  <div className={`flex items-center gap-3 p-3 rounded-lg border ${
    achieved ? 'bg-emerald-900/20 border-emerald-700/40' : 'bg-gray-800/30 border-gray-700/30 opacity-60'
  }`}>
    <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${
      achieved ? 'bg-emerald-500 text-white' : 'bg-gray-700 text-gray-400'
    }`}>
      {achieved ? '\u2713' : '\u25CB'}
    </div>
    <div>
      <div className={`font-medium text-sm ${achieved ? 'text-emerald-300' : 'text-gray-400'}`}>
        {milestone.name}
      </div>
      <div className="text-xs text-gray-500">{milestone.description}</div>
    </div>
  </div>
);

export const NexusAdvisorPanel: React.FC = () => {
  const [brief, setBrief] = useState<Brief | null>(null);
  const [knowledge, setKnowledge] = useState<KnowledgeSystem[]>([]);
  const [milestones, setMilestones] = useState<{ achieved: Milestone[]; upcoming: Milestone[] } | null>(null);
  const [activeTab, setActiveTab] = useState<'brief' | 'knowledge' | 'milestones' | 'teach' | 'debrief'>('brief');
  const [loading, setLoading] = useState(true);

  const [teachSystem, setTeachSystem] = useState('gpss');
  const [teachAction, setTeachAction] = useState('');
  const [teachResult, setTeachResult] = useState<TeachResult | null>(null);

  const [debriefType, setDebriefType] = useState('bid_won');
  const [debriefValue, setDebriefValue] = useState('');
  const [debriefResult, setDebriefResult] = useState<DebriefResult | null>(null);

  const fetchBrief = useCallback(async () => {
    try {
      const res = await fetch(`${API}/api/advisor/brief`);
      if (res.ok) setBrief(await res.json());
    } catch (e) { console.error('Brief fetch failed:', e); }
  }, []);

  const fetchKnowledge = useCallback(async () => {
    try {
      const res = await fetch(`${API}/api/advisor/knowledge`);
      if (res.ok) {
        const data = await res.json();
        setKnowledge(data.systems || []);
      }
    } catch (e) { console.error('Knowledge fetch failed:', e); }
  }, []);

  const fetchMilestones = useCallback(async () => {
    try {
      const res = await fetch(`${API}/api/advisor/milestones`);
      if (res.ok) setMilestones(await res.json());
    } catch (e) { console.error('Milestones fetch failed:', e); }
  }, []);

  useEffect(() => {
    setLoading(true);
    Promise.all([fetchBrief(), fetchKnowledge(), fetchMilestones()])
      .finally(() => setLoading(false));
  }, [fetchBrief, fetchKnowledge, fetchMilestones]);

  const handleTeach = async () => {
    if (!teachAction) return;
    try {
      const res = await fetch(`${API}/api/advisor/teach`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ system: teachSystem, action: teachAction }),
      });
      if (res.ok) setTeachResult(await res.json());
    } catch (e) { console.error('Teach failed:', e); }
  };

  const handleDebrief = async () => {
    try {
      const context: Record<string, unknown> = {};
      if (debriefType === 'bid_won' && debriefValue) {
        context.contract_value = parseFloat(debriefValue);
      }
      const res = await fetch(`${API}/api/advisor/debrief`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ outcome_type: debriefType, context }),
      });
      if (res.ok) {
        setDebriefResult(await res.json());
        fetchBrief();
        fetchMilestones();
      }
    } catch (e) { console.error('Debrief failed:', e); }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-blue-400"></div>
        <span className="ml-3 text-gray-400">Loading Advisor...</span>
      </div>
    );
  }

  const tabs = [
    { id: 'brief' as const, label: 'Growth Brief' },
    { id: 'milestones' as const, label: 'Milestones' },
    { id: 'knowledge' as const, label: 'Knowledge Map' },
    { id: 'teach' as const, label: 'Learn' },
    { id: 'debrief' as const, label: 'Debrief' },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white">NEXUS Advisor</h2>
          <p className="text-gray-400 text-sm mt-1">
            Teaching engine across all systems — learn while you build
          </p>
        </div>
        <div className="flex items-center gap-2 bg-gray-800/50 rounded-lg p-1">
          {brief && (
            <span className="text-xs text-gray-400 px-2">
              {brief.topics_learned}/{brief.total_topics_available} topics learned
            </span>
          )}
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 bg-gray-800/50 rounded-xl p-1">
        {tabs.map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex-1 py-2.5 px-4 rounded-lg text-sm font-medium transition ${
              activeTab === tab.id
                ? 'bg-blue-600 text-white'
                : 'text-gray-400 hover:text-white hover:bg-gray-700/50'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* BRIEF TAB */}
      {activeTab === 'brief' && brief && (
        <div className="space-y-6">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <StatCard label="Bids Submitted" value={brief.growth_stats.bids_submitted || 0} />
            <StatCard label="Win Rate" value={`${brief.win_rate}%`} sub={`${brief.growth_stats.bids_won || 0}W / ${brief.growth_stats.bids_lost || 0}L`} />
            <StatCard label="Contract Value" value={`$${((brief.growth_stats.total_contract_value || 0) / 1000).toFixed(0)}K`} />
            <StatCard label="Knowledge" value={`${brief.knowledge_coverage}%`} sub={`${brief.topics_learned} topics`} />
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <StatCard label="Outreach Emails" value={brief.growth_stats.total_outreach_emails || 0} />
            <StatCard label="Subs Managed" value={brief.growth_stats.subs_managed || 0} />
            <StatCard label="Proposals Scored" value={brief.growth_stats.proposals_scored || 0} />
            <StatCard label="Lessons Delivered" value={brief.total_lessons_delivered} />
          </div>

          {/* Patterns */}
          {brief.patterns.length > 0 && (
            <div className="bg-amber-900/20 border border-amber-700/40 rounded-xl p-5">
              <h3 className="text-amber-300 font-semibold mb-3">Advisor Observations</h3>
              <ul className="space-y-2">
                {brief.patterns.map((p, i) => (
                  <li key={i} className="text-sm text-amber-200/80 flex items-start gap-2">
                    <span className="text-amber-400 mt-0.5">*</span>
                    {p}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* System Usage */}
          {brief.most_used_systems.length > 0 && (
            <div className="bg-gray-800/50 rounded-xl p-5 border border-gray-700/50">
              <h3 className="text-white font-semibold mb-3">System Activity</h3>
              <div className="space-y-2">
                {brief.most_used_systems.map(([sys, count]) => (
                  <div key={sys} className="flex items-center justify-between">
                    <span className="text-sm text-gray-300 uppercase">{sys}</span>
                    <div className="flex items-center gap-2">
                      <div className="w-32 h-2 bg-gray-700 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-blue-500 rounded-full"
                          style={{ width: `${Math.min(100, (count / Math.max(...brief.most_used_systems.map(s => s[1]))) * 100)}%` }}
                        />
                      </div>
                      <span className="text-xs text-gray-400 w-8 text-right">{count}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* MILESTONES TAB */}
      {activeTab === 'milestones' && milestones && (
        <div className="space-y-6">
          {milestones.achieved.length > 0 && (
            <div>
              <h3 className="text-emerald-400 font-semibold mb-3">Achieved ({milestones.achieved.length})</h3>
              <div className="grid gap-2">
                {milestones.achieved.map(m => <MilestoneBadge key={m.id} milestone={m} achieved />)}
              </div>
            </div>
          )}
          <div>
            <h3 className="text-gray-300 font-semibold mb-3">Upcoming</h3>
            <div className="grid gap-2">
              {milestones.upcoming.map(m => <MilestoneBadge key={m.id} milestone={m} />)}
            </div>
          </div>
        </div>
      )}

      {/* KNOWLEDGE MAP TAB */}
      {activeTab === 'knowledge' && (
        <div className="space-y-4">
          {knowledge.map(sys => (
            <div key={sys.system} className="bg-gray-800/50 rounded-xl p-5 border border-gray-700/50">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-white font-semibold">{sys.name}</h3>
                <span className="text-xs text-gray-400 bg-gray-700 px-2 py-1 rounded">{sys.action_count} topics</span>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                {sys.actions.map(act => (
                  <div key={act.action} className="flex items-center gap-2 text-sm p-2 rounded bg-gray-900/30">
                    <span className={`w-2 h-2 rounded-full ${act.has_far_reference ? 'bg-blue-400' : 'bg-gray-600'}`} />
                    <span className="text-gray-300">{act.key_concept || act.action}</span>
                    {act.has_far_reference && <span className="text-xs text-blue-400 ml-auto">FAR</span>}
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* TEACH TAB */}
      {activeTab === 'teach' && (
        <div className="space-y-4">
          <div className="bg-gray-800/50 rounded-xl p-5 border border-gray-700/50">
            <h3 className="text-white font-semibold mb-4">Ask the Advisor</h3>
            <div className="grid grid-cols-2 gap-4 mb-4">
              <div>
                <label className="block text-sm text-gray-400 mb-1">System</label>
                <select
                  value={teachSystem}
                  onChange={e => { setTeachSystem(e.target.value); setTeachAction(''); setTeachResult(null); }}
                  className="w-full bg-gray-900 border border-gray-600 rounded-lg px-3 py-2 text-white text-sm"
                >
                  {knowledge.map(sys => (
                    <option key={sys.system} value={sys.system}>{sys.name}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-1">Topic</label>
                <select
                  value={teachAction}
                  onChange={e => { setTeachAction(e.target.value); setTeachResult(null); }}
                  className="w-full bg-gray-900 border border-gray-600 rounded-lg px-3 py-2 text-white text-sm"
                >
                  <option value="">Select a topic...</option>
                  {knowledge.find(s => s.system === teachSystem)?.actions.map(act => (
                    <option key={act.action} value={act.action}>{act.key_concept || act.action}</option>
                  ))}
                </select>
              </div>
            </div>
            <button
              onClick={handleTeach}
              disabled={!teachAction}
              className="bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed text-white px-6 py-2 rounded-lg text-sm font-medium transition"
            >
              Teach Me
            </button>
          </div>

          {teachResult && teachResult.has_advice && (
            <div className="bg-blue-900/20 border border-blue-700/40 rounded-xl p-5">
              <div className="flex items-center gap-2 mb-3">
                <span className="text-blue-300 font-semibold">{teachResult.key_concept}</span>
                {teachResult.is_new_topic && (
                  <span className="text-xs bg-emerald-600 text-white px-2 py-0.5 rounded">New Topic</span>
                )}
              </div>
              <p className="text-gray-200 text-sm leading-relaxed whitespace-pre-wrap">{teachResult.teach}</p>
              {teachResult.far_reference && (
                <div className="mt-3 text-xs text-blue-400 bg-blue-900/30 px-3 py-1.5 rounded inline-block">
                  Reference: {teachResult.far_reference}
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* DEBRIEF TAB */}
      {activeTab === 'debrief' && (
        <div className="space-y-4">
          <div className="bg-gray-800/50 rounded-xl p-5 border border-gray-700/50">
            <h3 className="text-white font-semibold mb-4">Record an Outcome</h3>
            <div className="grid grid-cols-2 gap-4 mb-4">
              <div>
                <label className="block text-sm text-gray-400 mb-1">Outcome Type</label>
                <select
                  value={debriefType}
                  onChange={e => { setDebriefType(e.target.value); setDebriefResult(null); }}
                  className="w-full bg-gray-900 border border-gray-600 rounded-lg px-3 py-2 text-white text-sm"
                >
                  <option value="bid_won">Bid Won</option>
                  <option value="bid_lost">Bid Lost</option>
                  <option value="contract_complete">Contract Complete</option>
                </select>
              </div>
              {debriefType === 'bid_won' && (
                <div>
                  <label className="block text-sm text-gray-400 mb-1">Contract Value ($)</label>
                  <input
                    type="number"
                    value={debriefValue}
                    onChange={e => setDebriefValue(e.target.value)}
                    placeholder="250000"
                    className="w-full bg-gray-900 border border-gray-600 rounded-lg px-3 py-2 text-white text-sm"
                  />
                </div>
              )}
            </div>
            <button
              onClick={handleDebrief}
              className="bg-emerald-600 hover:bg-emerald-700 text-white px-6 py-2 rounded-lg text-sm font-medium transition"
            >
              Generate Debrief
            </button>
          </div>

          {debriefResult && debriefResult.has_debrief && (
            <div className="space-y-4">
              <div className={`rounded-xl p-5 border ${
                debriefType === 'bid_won'
                  ? 'bg-emerald-900/20 border-emerald-700/40'
                  : debriefType === 'bid_lost'
                  ? 'bg-red-900/20 border-red-700/40'
                  : 'bg-blue-900/20 border-blue-700/40'
              }`}>
                <h4 className="font-semibold text-white mb-3">{debriefResult.title}</h4>

                {debriefResult.current_record && (
                  <div className="grid grid-cols-4 gap-3 mb-4">
                    <div className="text-center">
                      <div className="text-lg font-bold text-white">{debriefResult.current_record.total_bids}</div>
                      <div className="text-xs text-gray-400">Total Bids</div>
                    </div>
                    <div className="text-center">
                      <div className="text-lg font-bold text-emerald-400">{debriefResult.current_record.wins}</div>
                      <div className="text-xs text-gray-400">Wins</div>
                    </div>
                    <div className="text-center">
                      <div className="text-lg font-bold text-red-400">{debriefResult.current_record.losses}</div>
                      <div className="text-xs text-gray-400">Losses</div>
                    </div>
                    <div className="text-center">
                      <div className="text-lg font-bold text-blue-400">{debriefResult.current_record.win_rate}%</div>
                      <div className="text-xs text-gray-400">Win Rate</div>
                    </div>
                  </div>
                )}

                <div className="mb-4">
                  <h5 className="text-sm font-medium text-gray-300 mb-2">Review Questions</h5>
                  <ul className="space-y-1.5">
                    {debriefResult.prompts?.map((p, i) => (
                      <li key={i} className="text-sm text-gray-300 flex items-start gap-2">
                        <span className="text-gray-500 font-mono text-xs mt-0.5">{i + 1}.</span>
                        {p}
                      </li>
                    ))}
                  </ul>
                </div>

                <div>
                  <h5 className="text-sm font-medium text-gray-300 mb-2">Next Actions</h5>
                  <ul className="space-y-1.5">
                    {debriefResult.next_actions?.map((a, i) => (
                      <li key={i} className="text-sm text-gray-300 flex items-start gap-2">
                        <span className="text-blue-400 mt-0.5">-</span>
                        {a}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>

              {debriefResult.milestones_earned && debriefResult.milestones_earned.length > 0 && (
                <div className="bg-emerald-900/20 border border-emerald-700/40 rounded-xl p-5">
                  <h4 className="text-emerald-300 font-semibold mb-3">New Milestones Achieved!</h4>
                  <div className="grid gap-2">
                    {debriefResult.milestones_earned.map(m => (
                      <MilestoneBadge key={m.id} milestone={m} achieved />
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
};
