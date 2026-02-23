import React, { useState, useEffect, useCallback } from 'react';
import { api } from '../api/client';

interface TaskStatus {
  last_run: string;
  next_run?: string;
  minutes_until?: number;
  interval_minutes: number;
}

interface EngineStatus {
  running: boolean;
  enabled: boolean;
  started_at: string | null;
  cycle_count: number;
  stats: {
    opportunities_found: number;
    packages_generated: number;
    alerts_sent: number;
    learning_adjustments: number;
  };
  tasks: Record<string, TaskStatus>;
  recent_actions: any[];
}

interface BriefSection {
  title: string;
  message: string;
  [key: string]: any;
}

interface MorningBrief {
  generated_at: string | null;
  greeting: string;
  sections: Record<string, BriefSection>;
}

const TASK_LABELS: Record<string, { label: string; icon: string; description: string }> = {
  opportunity_scan: { label: 'Opportunity Scanner', icon: '🔍', description: 'Scans SAM.gov, state portals, BidNet for new opportunities' },
  ai_scoring: { label: 'AI Scoring', icon: '🧠', description: 'Scores unscored opportunities against DDI profile' },
  auto_package: { label: 'Auto-Package', icon: '📦', description: 'Generates cap statements + buyer emails for hot matches' },
  deadline_watch: { label: 'Deadline Watch', icon: '⏰', description: 'Monitors all active bid deadlines' },
  supplier_followup: { label: 'Supplier Follow-up', icon: '📧', description: 'Checks for unanswered RFQs and queues reminders' },
  compass_monitor: { label: 'Contract Monitor', icon: '📋', description: 'Checks contract health, deliverables, compliance' },
  prism_compliance: { label: 'PRISM Compliance', icon: '🛡️', description: 'Checks agent certs, insurance, background' },
  folder_scan: { label: 'Folder Scanner', icon: '📁', description: 'Scans BIDS:RESOURCES for workflow status' },
  learning_cycle: { label: 'Learning Cycle', icon: '🎓', description: 'Analyzes patterns and adjusts scoring weights' },
  morning_brief: { label: 'Morning Brief', icon: '☀️', description: 'Generates daily summary of everything you need' },
};

export function AutonomousPanel() {
  const [status, setStatus] = useState<EngineStatus | null>(null);
  const [brief, setBrief] = useState<MorningBrief | null>(null);
  const [activeTab, setActiveTab] = useState<'status' | 'brief' | 'history' | 'config'>('status');
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [history, setHistory] = useState<any[]>([]);
  const [config, setConfig] = useState<any>(null);

  const fetchStatus = useCallback(async () => {
    try {
      const data = await api.get('/autonomous/status');
      setStatus(data);
    } catch (err) {
      console.error('Failed to fetch autonomous status:', err);
    }
    setLoading(false);
  }, []);

  const fetchBrief = useCallback(async () => {
    try {
      const data = await api.get('/autonomous/brief');
      setBrief(data);
    } catch (err) {
      console.error('Failed to fetch brief:', err);
    }
  }, []);

  const fetchHistory = useCallback(async () => {
    try {
      const data = await api.get('/autonomous/history?limit=50');
      setHistory(data.actions || []);
    } catch (err) {
      console.error('Failed to fetch history:', err);
    }
  }, []);

  const fetchConfig = useCallback(async () => {
    try {
      const data = await api.get('/autonomous/config');
      setConfig(data);
    } catch (err) {
      console.error('Failed to fetch config:', err);
    }
  }, []);

  useEffect(() => {
    fetchStatus();
    fetchBrief();
    const interval = setInterval(fetchStatus, 30000);
    return () => clearInterval(interval);
  }, [fetchStatus, fetchBrief]);

  useEffect(() => {
    if (activeTab === 'history') fetchHistory();
    if (activeTab === 'config') fetchConfig();
  }, [activeTab, fetchHistory, fetchConfig]);

  const handleStart = async () => {
    setActionLoading(true);
    try {
      await api.post('/autonomous/start', {});
      await fetchStatus();
    } catch (err) {
      console.error('Failed to start engine:', err);
    }
    setActionLoading(false);
  };

  const handleStop = async () => {
    setActionLoading(true);
    try {
      await api.post('/autonomous/stop', {});
      await fetchStatus();
    } catch (err) {
      console.error('Failed to stop engine:', err);
    }
    setActionLoading(false);
  };

  const handleRunCycle = async () => {
    setActionLoading(true);
    try {
      await api.post('/autonomous/cycle', {});
      await fetchStatus();
    } catch (err) {
      console.error('Failed to run cycle:', err);
    }
    setActionLoading(false);
  };

  const handleGenerateBrief = async () => {
    setActionLoading(true);
    try {
      const data = await api.post('/autonomous/brief/generate', {});
      setBrief(data.brief);
    } catch (err) {
      console.error('Failed to generate brief:', err);
    }
    setActionLoading(false);
  };

  const formatTimeAgo = (isoStr: string) => {
    if (!isoStr || isoStr === 'never') return 'Never';
    const diff = Date.now() - new Date(isoStr).getTime();
    const mins = Math.floor(diff / 60000);
    if (mins < 1) return 'Just now';
    if (mins < 60) return `${mins}m ago`;
    const hrs = Math.floor(mins / 60);
    if (hrs < 24) return `${hrs}h ago`;
    return `${Math.floor(hrs / 24)}d ago`;
  };

  if (loading) {
    return (
      <div className="bg-gray-800 rounded-xl p-8 text-center">
        <div className="animate-pulse text-gray-400">Loading Autonomous Engine...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-indigo-900 via-purple-900 to-indigo-900 rounded-xl p-6 border border-indigo-700">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-white flex items-center gap-3">
              <span className="text-3xl">⚡</span>
              NEXUS Autonomous Engine
            </h2>
            <p className="text-indigo-300 mt-1">AI that works while you sleep — self-learning, self-improving</p>
          </div>
          <div className="flex items-center gap-3">
            {status?.running ? (
              <>
                <span className="flex items-center gap-2 text-green-400 font-medium">
                  <span className="w-3 h-3 bg-green-400 rounded-full animate-pulse" />
                  RUNNING
                </span>
                <button onClick={handleStop} disabled={actionLoading}
                  className="px-4 py-2 bg-red-600 hover:bg-red-700 rounded-lg text-sm font-medium disabled:opacity-50">
                  Stop Engine
                </button>
              </>
            ) : (
              <>
                <span className="flex items-center gap-2 text-gray-400">
                  <span className="w-3 h-3 bg-gray-500 rounded-full" />
                  STOPPED
                </span>
                <button onClick={handleStart} disabled={actionLoading}
                  className="px-4 py-2 bg-green-600 hover:bg-green-700 rounded-lg text-sm font-medium disabled:opacity-50">
                  Start Engine
                </button>
              </>
            )}
            <button onClick={handleRunCycle} disabled={actionLoading}
              className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 rounded-lg text-sm font-medium disabled:opacity-50">
              Run Cycle Now
            </button>
          </div>
        </div>

        {/* Stats Bar */}
        {status && (
          <div className="grid grid-cols-4 gap-4 mt-4">
            <div className="bg-black/30 rounded-lg p-3 text-center">
              <div className="text-2xl font-bold text-white">{status.cycle_count}</div>
              <div className="text-xs text-indigo-300">Cycles Run</div>
            </div>
            <div className="bg-black/30 rounded-lg p-3 text-center">
              <div className="text-2xl font-bold text-blue-400">{status.stats.opportunities_found}</div>
              <div className="text-xs text-indigo-300">Opps Found</div>
            </div>
            <div className="bg-black/30 rounded-lg p-3 text-center">
              <div className="text-2xl font-bold text-green-400">{status.stats.packages_generated}</div>
              <div className="text-xs text-indigo-300">Auto-Packages</div>
            </div>
            <div className="bg-black/30 rounded-lg p-3 text-center">
              <div className="text-2xl font-bold text-amber-400">{status.stats.learning_adjustments}</div>
              <div className="text-xs text-indigo-300">Learning Adjustments</div>
            </div>
          </div>
        )}
      </div>

      {/* Tab Navigation */}
      <div className="flex gap-2">
        {(['status', 'brief', 'history', 'config'] as const).map(tab => (
          <button key={tab} onClick={() => setActiveTab(tab)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition ${
              activeTab === tab ? 'bg-indigo-600 text-white' : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
            }`}>
            {tab === 'status' && '⚙️ Tasks'}
            {tab === 'brief' && '☀️ Morning Brief'}
            {tab === 'history' && '📜 History'}
            {tab === 'config' && '🔧 Config'}
          </button>
        ))}
      </div>

      {/* Task Status Grid */}
      {activeTab === 'status' && status && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {Object.entries(status.tasks).map(([taskKey, task]) => {
            const info = TASK_LABELS[taskKey] || { label: taskKey, icon: '⚙️', description: '' };
            const isOverdue = task.minutes_until !== undefined && task.minutes_until <= 0;
            return (
              <div key={taskKey} className="bg-gray-800 rounded-xl p-4 border border-gray-700 hover:border-gray-600 transition">
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <span className="text-2xl">{info.icon}</span>
                    <div>
                      <h3 className="font-semibold text-white">{info.label}</h3>
                      <p className="text-xs text-gray-400 mt-0.5">{info.description}</p>
                    </div>
                  </div>
                  <div className={`text-xs px-2 py-1 rounded ${
                    isOverdue ? 'bg-amber-900 text-amber-300' : 'bg-gray-700 text-gray-300'
                  }`}>
                    {task.interval_minutes < 60
                      ? `Every ${task.interval_minutes}m`
                      : `Every ${Math.round(task.interval_minutes / 60)}h`}
                  </div>
                </div>
                <div className="mt-3 flex items-center justify-between text-xs">
                  <span className="text-gray-500">
                    Last: {task.last_run === 'never' ? 'Never' : formatTimeAgo(task.last_run)}
                  </span>
                  {task.minutes_until !== undefined && (
                    <span className={isOverdue ? 'text-amber-400' : 'text-gray-500'}>
                      {isOverdue ? 'Due now' : `Next in ${task.minutes_until}m`}
                    </span>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Morning Brief */}
      {activeTab === 'brief' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              {brief?.generated_at && (
                <p className="text-xs text-gray-500">
                  Generated: {new Date(brief.generated_at).toLocaleString()}
                </p>
              )}
            </div>
            <button onClick={handleGenerateBrief} disabled={actionLoading}
              className="px-4 py-2 bg-amber-600 hover:bg-amber-700 rounded-lg text-sm font-medium disabled:opacity-50">
              Generate Fresh Brief
            </button>
          </div>

          {brief?.greeting && (
            <div className="bg-gradient-to-r from-amber-900/50 to-orange-900/50 rounded-xl p-5 border border-amber-800">
              <p className="text-lg text-amber-100 font-medium">{brief.greeting}</p>
            </div>
          )}

          {brief?.sections && Object.entries(brief.sections).map(([key, section]) => (
            <div key={key} className="bg-gray-800 rounded-xl p-5 border border-gray-700">
              <h3 className="font-semibold text-white mb-2">{section.title || key}</h3>
              <p className="text-gray-300 text-sm">{section.message}</p>

              {section.bid_now && section.bid_now.length > 0 && (
                <div className="mt-3 space-y-2">
                  <p className="text-xs text-red-400 font-medium uppercase">BID NOW:</p>
                  {section.bid_now.map((opp: any, i: number) => (
                    <div key={i} className="bg-red-900/30 border border-red-800 rounded-lg p-3">
                      <p className="text-white font-medium">{opp.title}</p>
                      <p className="text-xs text-gray-400">{opp.agency} — Score: {opp.score} — {opp.set_aside}</p>
                    </div>
                  ))}
                </div>
              )}

              {section.worth_a_look && section.worth_a_look.length > 0 && (
                <div className="mt-3 space-y-2">
                  <p className="text-xs text-yellow-400 font-medium uppercase">WORTH A LOOK:</p>
                  {section.worth_a_look.map((opp: any, i: number) => (
                    <div key={i} className="bg-yellow-900/20 border border-yellow-800/50 rounded-lg p-3">
                      <p className="text-white font-medium">{opp.title}</p>
                      <p className="text-xs text-gray-400">{opp.agency} — Score: {opp.score}</p>
                    </div>
                  ))}
                </div>
              )}

              {section.alerts && section.alerts.length > 0 && (
                <div className="mt-3 space-y-2">
                  {section.alerts.map((alert: any, i: number) => (
                    <div key={i} className={`rounded-lg p-3 ${
                      alert.alert_level === 'RED' ? 'bg-red-900/30 border border-red-800' :
                      alert.alert_level === 'YELLOW' ? 'bg-yellow-900/20 border border-yellow-800/50' :
                      'bg-gray-700 border border-gray-600'
                    }`}>
                      <p className="text-white text-sm">{alert.title}</p>
                      <p className="text-xs text-gray-400">{alert.agency} — {alert.hours_left}h left</p>
                    </div>
                  ))}
                </div>
              )}

              {section.warnings && section.warnings.length > 0 && (
                <div className="mt-3 space-y-2">
                  {section.warnings.map((w: any, i: number) => (
                    <div key={i} className="bg-orange-900/20 border border-orange-800/50 rounded-lg p-2 text-sm text-orange-200">
                      {w.type}: {w.contract || w.deliverable || w.agent} — {w.days_left ?? w.days_overdue} days
                    </div>
                  ))}
                </div>
              )}

              {section.folders && section.folders.length > 0 && (
                <div className="mt-3 space-y-1">
                  {section.folders.map((f: string, i: number) => (
                    <div key={i} className="text-sm text-green-300 bg-green-900/20 rounded px-3 py-1.5">
                      📦 {f}
                    </div>
                  ))}
                </div>
              )}

              {section.insights && section.insights.length > 0 && (
                <div className="mt-3 space-y-1">
                  {section.insights.map((ins: any, i: number) => (
                    <div key={i} className="text-sm text-purple-300 bg-purple-900/20 rounded px-3 py-1.5">
                      🎓 [{ins.domain}] {ins.action}
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}

          {(!brief?.sections || Object.keys(brief.sections).length === 0) && (
            <div className="bg-gray-800 rounded-xl p-8 text-center text-gray-500">
              No brief generated yet. Click "Generate Fresh Brief" or wait for the scheduled run.
            </div>
          )}
        </div>
      )}

      {/* History */}
      {activeTab === 'history' && (
        <div className="bg-gray-800 rounded-xl border border-gray-700 overflow-hidden">
          <div className="max-h-[500px] overflow-y-auto">
            {history.length === 0 ? (
              <div className="p-8 text-center text-gray-500">No actions recorded yet.</div>
            ) : (
              <table className="w-full text-sm">
                <thead className="bg-gray-900 sticky top-0">
                  <tr>
                    <th className="text-left px-4 py-3 text-gray-400 font-medium">Time</th>
                    <th className="text-left px-4 py-3 text-gray-400 font-medium">Task</th>
                    <th className="text-left px-4 py-3 text-gray-400 font-medium">Status</th>
                    <th className="text-left px-4 py-3 text-gray-400 font-medium">Summary</th>
                    <th className="text-left px-4 py-3 text-gray-400 font-medium">Learned</th>
                  </tr>
                </thead>
                <tbody>
                  {[...history].reverse().map((action, i) => {
                    const info = TASK_LABELS[action.task] || { icon: '⚙️', label: action.task };
                    return (
                      <tr key={i} className="border-t border-gray-700 hover:bg-gray-750">
                        <td className="px-4 py-2 text-gray-500 whitespace-nowrap">
                          {formatTimeAgo(action.timestamp)}
                        </td>
                        <td className="px-4 py-2 text-white">
                          {info.icon} {info.label}
                        </td>
                        <td className="px-4 py-2">
                          <span className={`px-2 py-0.5 rounded text-xs ${
                            action.success ? 'bg-green-900/50 text-green-400' : 'bg-red-900/50 text-red-400'
                          }`}>
                            {action.success ? 'OK' : 'FAIL'}
                          </span>
                        </td>
                        <td className="px-4 py-2 text-gray-300 max-w-xs truncate">{action.summary}</td>
                        <td className="px-4 py-2">
                          {action.learning_logged && (
                            <span className="text-purple-400 text-xs">🎓 Yes</span>
                          )}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            )}
          </div>
        </div>
      )}

      {/* Config */}
      {activeTab === 'config' && config && (
        <div className="space-y-4">
          <div className="bg-gray-800 rounded-xl p-5 border border-gray-700">
            <h3 className="font-semibold text-white mb-4">Task Intervals</h3>
            <div className="grid grid-cols-2 gap-3">
              {Object.entries(config.intervals || {}).map(([key, val]) => {
                const info = TASK_LABELS[key] || { label: key, icon: '⚙️' };
                return (
                  <div key={key} className="flex items-center justify-between bg-gray-900 rounded-lg px-4 py-2">
                    <span className="text-sm text-gray-300">{info.icon} {info.label}</span>
                    <span className="text-sm text-indigo-400 font-mono">
                      {(val as number) < 60 ? `${val}m` : `${Math.round((val as number) / 60)}h`}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>

          <div className="bg-gray-800 rounded-xl p-5 border border-gray-700">
            <h3 className="font-semibold text-white mb-4">Thresholds</h3>
            <div className="grid grid-cols-2 gap-3">
              {Object.entries(config.thresholds || {}).map(([key, val]) => (
                <div key={key} className="flex items-center justify-between bg-gray-900 rounded-lg px-4 py-2">
                  <span className="text-sm text-gray-300">{key.replace(/_/g, ' ')}</span>
                  <span className="text-sm text-indigo-400 font-mono">{val as number}</span>
                </div>
              ))}
            </div>
          </div>

          {config.preferences?.priority_naics?.length > 0 && (
            <div className="bg-gray-800 rounded-xl p-5 border border-gray-700">
              <h3 className="font-semibold text-white mb-2">Learned Priority NAICS (from wins)</h3>
              <div className="flex flex-wrap gap-2">
                {config.preferences.priority_naics.map((n: string) => (
                  <span key={n} className="bg-indigo-900/50 text-indigo-300 px-3 py-1 rounded-full text-xs">{n}</span>
                ))}
              </div>
            </div>
          )}

          {config.preferences?.priority_agencies?.length > 0 && (
            <div className="bg-gray-800 rounded-xl p-5 border border-gray-700">
              <h3 className="font-semibold text-white mb-2">Learned Priority Agencies (from wins)</h3>
              <div className="flex flex-wrap gap-2">
                {config.preferences.priority_agencies.map((a: string) => (
                  <span key={a} className="bg-green-900/50 text-green-300 px-3 py-1 rounded-full text-xs">{a}</span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
