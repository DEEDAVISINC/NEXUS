import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { ViewType } from '../Header';
import { api } from '../../api/client';
import {
  NEXUS_SHELL_PAGE,
  NEXUS_SHELL_PAD,
  NEXUS_CONTAINER,
  NEXUS_TITLE,
  NEXUS_SUBTITLE,
  NEXUS_TAB_ACTIVE,
  NEXUS_TAB_IDLE,
  NEXUS_BTN_PRIMARY,
  NEXUS_BTN_SECONDARY,
  NexusMetricCard,
  NexusPanel,
} from '../shared/NexusDashboardShell';

interface HRSystemProps {
  onBackToNexus: () => void;
  onNavigate?: (system: ViewType, tab?: string) => void;
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

interface PhaseItem { key: string; title: string; owner: string; items: string[]; }
interface TrainingDef { name: string; recurring: boolean; }
interface TrainingRow { status: string; due: string; certRef: string; completedBy: string; completedDate: string; }
interface ScreeningEntry { date: string; result: string; notes: string; loggedBy: string; ts: string; }
interface AuditEntry { ts: string; actor: string; action: string; }

interface RosterRow {
  id: string;
  name: string;
  workerType: 'employee' | 'contractor';
  division: string;
  startdate: string;
  status: 'Active' | 'Archived';
  progress: number;
}

interface HRRecord extends RosterRow {
  checklist: Record<string, boolean[]>;
  training: TrainingRow[];
  exclusionLog: ScreeningEntry[];
  auditLog: AuditEntry[];
  _progress?: number;
}

interface Config {
  phases_employee: PhaseItem[];
  phases_contractor: PhaseItem[];
  trainings: TrainingDef[];
  divisions: string[];
  fwa_training_name: string;
  fwa_deadline_days: number;
  screening_stale_days: number;
}

interface Alerts {
  fwa_training_overdue: { id: string; name: string; division: string; deadline: string }[];
  screening_stale: { id: string; name: string; last_screened: string | null }[];
  flagged_screenings_open: { id: string; name: string }[];
  active_count: number;
  alert_count: number;
}

const TAB_IDS = ['dashboard', 'roster', 'detail'] as const;

const WORKER_LABEL: Record<string, string> = {
  employee: 'Employee (W-2)',
  contractor: 'Contractor (1099)',
};

function csvEscape(v: unknown): string {
  const s = v === undefined || v === null ? '' : String(v);
  return '"' + s.replace(/"/g, '""') + '"';
}

function downloadCsv(filename: string, lines: string[]) {
  const csv = lines.join('\n');
  const blob = new Blob([csv], { type: 'text/csv' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

const HRSystem: React.FC<HRSystemProps> = ({ onBackToNexus, onNavigate, activeTab, setActiveTab }) => {
  const resolvedTab = TAB_IDS.includes(activeTab as (typeof TAB_IDS)[number]) ? activeTab : 'dashboard';

  const [config, setConfig] = useState<Config | null>(null);
  const [roster, setRoster] = useState<RosterRow[]>([]);
  const [alerts, setAlerts] = useState<Alerts | null>(null);
  const [selected, setSelected] = useState<HRRecord | null>(null);
  const [loading, setLoading] = useState(true);
  const [apiError, setApiError] = useState<string | null>(null);
  const [actor, setActor] = useState<string>(() => localStorage.getItem('nexus_hr_actor') || '');

  // Add-hire form state
  const [nhName, setNhName] = useState('');
  const [nhType, setNhType] = useState<'employee' | 'contractor'>('employee');
  const [nhDivision, setNhDivision] = useState('');
  const [nhStart, setNhStart] = useState('');
  const [adding, setAdding] = useState(false);

  // Screening form state (detail view)
  const [scrDate, setScrDate] = useState('');
  const [scrResult, setScrResult] = useState('Clear');
  const [scrNotes, setScrNotes] = useState('');

  const persistActor = (v: string) => {
    setActor(v);
    try { localStorage.setItem('nexus_hr_actor', v); } catch { /* ignore */ }
  };

  const loadConfig = useCallback(async () => {
    try {
      const res: any = await api.getHrOnboardingConfig();
      setConfig(res);
    } catch { /* config is optional for rendering roster */ }
  }, []);

  const loadRoster = useCallback(async () => {
    setLoading(true);
    setApiError(null);
    try {
      const res: any = await api.getHrOnboardingRoster();
      setRoster(res?.roster || []);
    } catch (e: any) {
      setApiError(e?.message || 'Could not load HR roster');
      setRoster([]);
    } finally {
      setLoading(false);
    }
  }, []);

  const loadAlerts = useCallback(async () => {
    try {
      const res: any = await api.getHrOnboardingAlerts();
      setAlerts(res);
    } catch { setAlerts(null); }
  }, []);

  useEffect(() => {
    loadConfig();
    loadRoster();
    loadAlerts();
  }, [loadConfig, loadRoster, loadAlerts]);

  const openDetail = useCallback(async (id: string) => {
    try {
      const res: any = await api.getHrOnboardingRecord(id);
      setSelected(res);
      setActiveTab('detail');
    } catch (e: any) {
      setApiError(e?.message || 'Could not load record');
    }
  }, [setActiveTab]);

  const refreshSelected = useCallback(async () => {
    if (!selected) return;
    const res: any = await api.getHrOnboardingRecord(selected.id);
    setSelected(res);
  }, [selected]);

  const phasesFor = useCallback((workerType: string): PhaseItem[] => {
    if (!config) return [];
    return workerType === 'contractor' ? config.phases_contractor : config.phases_employee;
  }, [config]);

  const handleAddHire = async () => {
    if (!nhName.trim()) { alert('Enter a name for the new hire.'); return; }
    setAdding(true);
    try {
      await api.addHrOnboardingHire({
        name: nhName.trim(),
        workerType: nhType,
        division: nhDivision,
        startdate: nhStart,
        actor,
      });
      setNhName(''); setNhDivision(''); setNhStart(''); setNhType('employee');
      await loadRoster();
      await loadAlerts();
    } catch (e: any) {
      alert(e?.message || 'Could not add new hire');
    } finally {
      setAdding(false);
    }
  };

  const toggleChecklist = async (phase: string, index: number, checked: boolean) => {
    if (!selected) return;
    await api.updateHrOnboardingChecklist(selected.id, { phase, index, checked, actor });
    await refreshSelected();
    await loadRoster();
    await loadAlerts();
  };

  const updateTraining = async (index: number, field: string, value: string) => {
    if (!selected) return;
    await api.updateHrOnboardingTraining(selected.id, { index, field, value, actor });
    await refreshSelected();
    await loadRoster();
    await loadAlerts();
  };

  const submitScreening = async () => {
    if (!selected) return;
    if (!scrDate) { alert('Enter a screening date.'); return; }
    await api.logHrOnboardingScreening(selected.id, { date: scrDate, result: scrResult, notes: scrNotes, actor });
    setScrDate(''); setScrResult('Clear'); setScrNotes('');
    await refreshSelected();
    await loadAlerts();
  };

  const archiveRecord = async (rec: RosterRow) => {
    if (!window.confirm(
      `Archive ${rec.name}? This record and its full audit/training/screening history are retained (10-year CMS FDR standard) — not deleted.`
    )) return;
    await api.updateHrOnboardingStatus(rec.id, { status: 'Archived', actor });
    if (selected?.id === rec.id) setSelected(null);
    await loadRoster();
    await loadAlerts();
  };

  const exportRecord = (rec: HRRecord) => {
    if (!config) return;
    const lines: string[] = [];
    lines.push('DDI NEXUS HR Onboarding Record Export');
    lines.push([csvEscape('Name'), csvEscape(rec.name)].join(','));
    lines.push([csvEscape('Worker Type'), csvEscape(WORKER_LABEL[rec.workerType])].join(','));
    lines.push([csvEscape('Division'), csvEscape(rec.division)].join(','));
    lines.push([csvEscape('Date of Hire/Engagement'), csvEscape(rec.startdate)].join(','));
    lines.push([csvEscape('Status'), csvEscape(rec.status)].join(','));
    lines.push([csvEscape('Exported'), csvEscape(new Date().toISOString())].join(','));
    lines.push('');
    lines.push('CHECKLIST');
    lines.push([csvEscape('Phase'), csvEscape('Item'), csvEscape('Complete')].join(','));
    phasesFor(rec.workerType).forEach((p) => {
      p.items.forEach((item, i) => {
        lines.push([csvEscape(p.title), csvEscape(item), csvEscape(rec.checklist[p.key]?.[i] ? 'Yes' : 'No')].join(','));
      });
    });
    lines.push('');
    lines.push('TRAINING');
    lines.push([csvEscape('Training'), csvEscape('Status'), csvEscape('Due'), csvEscape('Certificate/Ref'), csvEscape('Completed By'), csvEscape('Completed Date'), csvEscape('Recurring')].join(','));
    config.trainings.forEach((t, i) => {
      const tr = rec.training[i] || ({} as TrainingRow);
      lines.push([csvEscape(t.name), csvEscape(tr.status), csvEscape(tr.due), csvEscape(tr.certRef), csvEscape(tr.completedBy), csvEscape(tr.completedDate), csvEscape(t.recurring ? 'Annual' : 'One-time')].join(','));
    });
    lines.push('');
    lines.push('EXCLUSION SCREENING LOG (OIG LEIE + GSA SAM.gov)');
    lines.push([csvEscape('Date'), csvEscape('Result'), csvEscape('Notes'), csvEscape('Logged By'), csvEscape('Timestamp')].join(','));
    (rec.exclusionLog || []).forEach((e) => {
      lines.push([csvEscape(e.date), csvEscape(e.result), csvEscape(e.notes), csvEscape(e.loggedBy), csvEscape(e.ts)].join(','));
    });
    lines.push('');
    lines.push('AUDIT LOG (append-only)');
    lines.push([csvEscape('Timestamp'), csvEscape('Actor'), csvEscape('Action')].join(','));
    (rec.auditLog || []).forEach((a) => {
      lines.push([csvEscape(a.ts), csvEscape(a.actor), csvEscape(a.action)].join(','));
    });
    downloadCsv(`DDI_HR_Onboarding_${rec.name.replace(/\s+/g, '_')}_${new Date().toISOString().slice(0, 10)}.csv`, lines);
  };

  const exportRoster = () => {
    const lines: string[] = [];
    lines.push([csvEscape('Name'), csvEscape('Worker Type'), csvEscape('Division'), csvEscape('Date of Hire/Engagement'), csvEscape('Status'), csvEscape('Completion %')].join(','));
    roster.forEach((r) => {
      lines.push([csvEscape(r.name), csvEscape(WORKER_LABEL[r.workerType]), csvEscape(r.division), csvEscape(r.startdate), csvEscape(r.status), csvEscape(r.progress + '%')].join(','));
    });
    downloadCsv(`DDI_HR_Onboarding_Roster_${new Date().toISOString().slice(0, 10)}.csv`, lines);
  };

  const activeRoster = useMemo(() => roster.filter((r) => r.status === 'Active'), [roster]);

  const tabs = [
    { id: 'dashboard', label: 'Dashboard', icon: '📊' },
    { id: 'roster', label: 'Roster', icon: '🧑‍💼' },
    { id: 'detail', label: 'New Hire Detail', icon: '🗂️' },
  ];

  return (
    <div className={NEXUS_SHELL_PAGE}>
      <div className={`${NEXUS_SHELL_PAD} ${NEXUS_CONTAINER}`}>
        <div className="flex flex-wrap items-start justify-between gap-4 mb-6">
          <div>
            <button type="button" onClick={onBackToNexus} className="text-sm text-gray-400 hover:text-white mb-2 transition-colors">
              ← NEXUS Command Center
            </button>
            <h1 className={NEXUS_TITLE}>HR</h1>
            <p className={NEXUS_SUBTITLE}>
              Employee (W-2) &amp; Contractor (1099) onboarding — Pre-boarding → Day 1 → Week 1 → 30/60/90 Day.
              CMS FDR training + OIG LEIE/GSA SAM exclusion screening (42 CFR 422.504(d)). All divisions.
            </p>
          </div>
          <div className="flex items-center gap-2">
            <label className="text-xs text-gray-400 whitespace-nowrap">Your initials:</label>
            <input
              value={actor}
              onChange={(e) => persistActor(e.target.value)}
              placeholder="e.g. DD"
              className="w-20 bg-gray-800 border border-gray-700 rounded px-2 py-1.5 text-sm text-white"
            />
            <button type="button" onClick={() => { loadRoster(); loadAlerts(); }} className={NEXUS_BTN_SECONDARY}>
              Refresh
            </button>
          </div>
        </div>

        {apiError && (
          <div className="mb-4 p-4 bg-red-900/30 border border-red-500/40 rounded-xl text-red-300 text-sm flex justify-between items-center">
            <span>{apiError}</span>
            <button type="button" onClick={loadRoster} className={NEXUS_BTN_PRIMARY}>Retry</button>
          </div>
        )}

        <div className="flex flex-wrap gap-2 mb-6">
          {tabs.map((t) => (
            <button
              key={t.id}
              type="button"
              onClick={() => setActiveTab(t.id)}
              className={`px-4 py-2 rounded-lg text-sm font-semibold transition-all ${resolvedTab === t.id ? NEXUS_TAB_ACTIVE : NEXUS_TAB_IDLE}`}
            >
              {t.icon} {t.label}
            </button>
          ))}
        </div>

        {/* ─────────── DASHBOARD ─────────── */}
        {resolvedTab === 'dashboard' && (
          <>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
              <NexusMetricCard label="Active Roster" value={activeRoster.length} icon="🧑‍💼" accent="purple" />
              <NexusMetricCard label="FWA Training Overdue" value={alerts?.fwa_training_overdue.length || 0} icon="⏰" accent={alerts?.fwa_training_overdue.length ? 'red' : 'green'} />
              <NexusMetricCard label="Screening Stale (30d+)" value={alerts?.screening_stale.length || 0} icon="🔍" accent={alerts?.screening_stale.length ? 'yellow' : 'green'} />
              <NexusMetricCard label="Flagged — Escalate" value={alerts?.flagged_screenings_open.length || 0} icon="🚨" accent={alerts?.flagged_screenings_open.length ? 'red' : 'green'} />
            </div>

            {alerts && alerts.alert_count > 0 && (
              <NexusPanel title="⚠️ Compliance Alerts — CMS FDR Audit Readiness (COMPASS)">
                <div className="space-y-2 text-sm">
                  {alerts.flagged_screenings_open.map((a) => (
                    <div key={`flag-${a.id}`} className="p-3 bg-red-900/20 border border-red-500/40 rounded-lg flex justify-between items-center">
                      <span className="text-red-300">🚨 {a.name} — open flagged exclusion screening, escalate to Compliance</span>
                      <button onClick={() => openDetail(a.id)} className={NEXUS_BTN_SECONDARY}>Open</button>
                    </div>
                  ))}
                  {alerts.fwa_training_overdue.map((a) => (
                    <div key={`fwa-${a.id}`} className="p-3 bg-amber-900/20 border border-amber-500/40 rounded-lg flex justify-between items-center">
                      <span className="text-amber-300">⏰ {a.name} ({a.division || 'no division'}) — FWA training overdue since {a.deadline}</span>
                      <button onClick={() => openDetail(a.id)} className={NEXUS_BTN_SECONDARY}>Open</button>
                    </div>
                  ))}
                  {alerts.screening_stale.map((a) => (
                    <div key={`stale-${a.id}`} className="p-3 bg-yellow-900/10 border border-yellow-600/30 rounded-lg flex justify-between items-center">
                      <span className="text-yellow-300">🔍 {a.name} — exclusion screening {a.last_screened ? `stale since ${a.last_screened}` : 'never logged'}</span>
                      <button onClick={() => openDetail(a.id)} className={NEXUS_BTN_SECONDARY}>Open</button>
                    </div>
                  ))}
                </div>
              </NexusPanel>
            )}

            <NexusPanel title="Active Roster" className="mt-6">
              {loading ? (
                <p className="text-gray-400 text-sm">Loading roster…</p>
              ) : activeRoster.length === 0 ? (
                <p className="text-gray-400 text-sm">No active employees or contractors yet. Add one in the Roster tab.</p>
              ) : (
                <div className="space-y-2">
                  {activeRoster.slice(0, 8).map((r) => (
                    <button key={r.id} type="button" onClick={() => openDetail(r.id)} className="w-full text-left p-3 bg-gray-700/40 rounded-lg border border-gray-600/50 hover:border-purple-500/40 transition-all flex flex-wrap items-center gap-3">
                      <span className="font-bold text-white text-sm min-w-[140px]">{r.name}</span>
                      <span className="text-xs text-gray-400">{WORKER_LABEL[r.workerType]}</span>
                      <span className="text-xs text-gray-500">{r.division || '—'}</span>
                      <div className="flex-1 min-w-[100px] h-2 bg-gray-800 rounded overflow-hidden">
                        <div className="h-full bg-purple-500" style={{ width: `${r.progress}%` }} />
                      </div>
                      <span className="text-xs font-bold text-purple-400">{r.progress}%</span>
                    </button>
                  ))}
                </div>
              )}
            </NexusPanel>

            <p className="text-xs text-gray-500 mt-4">
              This is HR onboarding for internal DDI employees &amp; engaged contractors only. Field agents (PRISM) and
              external subcontractors/suppliers (GPSS) follow the separate pipeline in NEXUS_ONBOARDING_SYSTEM.md.
            </p>
          </>
        )}

        {/* ─────────── ROSTER ─────────── */}
        {resolvedTab === 'roster' && (
          <>
            <NexusPanel title="Add New Hire">
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 mb-3">
                <input
                  value={nhName}
                  onChange={(e) => setNhName(e.target.value)}
                  placeholder="Full name"
                  className="bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm text-white"
                />
                <select value={nhType} onChange={(e) => setNhType(e.target.value as 'employee' | 'contractor')} className="bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm text-white">
                  <option value="employee">Employee (W-2)</option>
                  <option value="contractor">Independent Contractor (1099)</option>
                </select>
                <select value={nhDivision} onChange={(e) => setNhDivision(e.target.value)} className="bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm text-white">
                  <option value="">Division / role area</option>
                  {(config?.divisions || []).map((d) => <option key={d} value={d}>{d}</option>)}
                </select>
                <input
                  type="date"
                  value={nhStart}
                  onChange={(e) => setNhStart(e.target.value)}
                  title="Date of hire/engagement — anchors the 90-day FWA deadline and 10-year retention clock"
                  className="bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm text-white"
                />
              </div>
              <button type="button" onClick={handleAddHire} disabled={adding} className={NEXUS_BTN_PRIMARY}>
                {adding ? 'Adding…' : 'Add New Hire'}
              </button>
              <p className="text-xs text-gray-500 mt-2">
                Date field = date of hire (anchors the CMS 90-day FWA/General Compliance deadline and the 10-year retention clock).
              </p>
            </NexusPanel>

            <div className="flex items-center justify-between mt-6 mb-2">
              <h3 className="text-lg font-bold text-white">Full Roster ({roster.length})</h3>
              <button type="button" onClick={exportRoster} className={NEXUS_BTN_SECONDARY}>Export Roster Summary (CSV)</button>
            </div>

            {roster.length === 0 ? (
              <div className="text-gray-400 text-sm p-6 border border-dashed border-gray-700 rounded-lg text-center">
                No hires tracked yet. Use the form above to start onboarding.
              </div>
            ) : (
              <div className="space-y-2">
                {roster.map((r) => (
                  <div key={r.id} className={`flex flex-wrap items-center gap-3 p-3 rounded-lg border ${r.status === 'Archived' ? 'bg-gray-800/30 border-gray-700/50 opacity-60' : 'bg-gray-700/40 border-gray-600/50'}`}>
                    <button type="button" onClick={() => openDetail(r.id)} className="font-bold text-white text-sm min-w-[160px] text-left hover:text-purple-400">
                      {r.name}
                    </button>
                    <span className="text-xs text-gray-400 min-w-[150px]">{WORKER_LABEL[r.workerType]} · {r.division || '—'}</span>
                    <span className="text-xs text-gray-500">Start: {r.startdate || '—'}</span>
                    {r.status === 'Archived' && <span className="text-[10px] uppercase tracking-wide text-gray-500 border border-gray-600 px-1.5 py-0.5 rounded">Archived</span>}
                    <div className="flex-1 min-w-[100px] h-2 bg-gray-800 rounded overflow-hidden">
                      <div className="h-full bg-purple-500" style={{ width: `${r.progress}%` }} />
                    </div>
                    <span className="text-xs font-bold text-purple-400">{r.progress}%</span>
                    {r.status === 'Active' && (
                      <button type="button" onClick={() => archiveRecord(r)} className="text-xs px-3 py-1.5 border border-red-500/40 text-red-400 rounded hover:bg-red-900/20 transition">
                        Archive
                      </button>
                    )}
                  </div>
                ))}
              </div>
            )}
          </>
        )}

        {/* ─────────── DETAIL ─────────── */}
        {resolvedTab === 'detail' && (
          <>
            {!selected ? (
              <NexusPanel title="Select a record">
                <p className="text-gray-400 text-sm">Open a record from the Roster tab to view onboarding detail.</p>
              </NexusPanel>
            ) : (
              <>
                <div className="flex flex-wrap items-center justify-between gap-3 mb-4">
                  <div>
                    <h2 className="text-xl font-bold text-white">{selected.name}</h2>
                    <p className="text-sm text-gray-400">
                      {selected.division || '—'} · {WORKER_LABEL[selected.workerType]} · Date of hire/engagement: {selected.startdate || '—'} · {selected._progress ?? 0}% complete
                    </p>
                  </div>
                  <button type="button" onClick={() => exportRecord(selected)} className={NEXUS_BTN_SECONDARY}>
                    Export Record (CSV)
                  </button>
                </div>

                <div className="w-full h-2.5 bg-gray-800 rounded overflow-hidden mb-6">
                  <div className="h-full bg-purple-500" style={{ width: `${selected._progress ?? 0}%` }} />
                </div>

                {selected.workerType === 'contractor' && (
                  <div className="mb-4 p-3 bg-amber-900/15 border border-amber-500/30 rounded-lg text-sm text-amber-300">
                    Contractor track: no I-9/E-Verify, no calendar-based performance reviews. Check-ins should reference
                    contract deliverables, not employee-style supervision, to support worker classification.
                  </div>
                )}

                {phasesFor(selected.workerType).map((p) => (
                  <NexusPanel key={p.key} title={`${p.title} — Owner: ${p.owner}`} className="mb-4">
                    <div className="space-y-1">
                      {p.items.map((item, i) => {
                        const checked = !!selected.checklist?.[p.key]?.[i];
                        return (
                          <label key={i} className={`flex items-center gap-3 py-1.5 border-b border-gray-700/50 last:border-b-0 text-sm cursor-pointer ${checked ? 'text-gray-500 line-through' : 'text-gray-200'}`}>
                            <input
                              type="checkbox"
                              checked={checked}
                              onChange={(e) => toggleChecklist(p.key, i, e.target.checked)}
                              className="w-4 h-4 accent-purple-500"
                            />
                            {item}
                          </label>
                        );
                      })}
                    </div>
                  </NexusPanel>
                ))}

                <NexusPanel title="Required Training — CMS floor: FWA/General Compliance within 90 days of hire, annual thereafter" className="mb-4">
                  <div className="overflow-x-auto">
                    <table className="w-full text-xs">
                      <thead>
                        <tr className="text-purple-400 uppercase text-[10px] tracking-wide text-left border-b border-gray-700">
                          <th className="py-2 pr-2">Training</th>
                          <th className="py-2 pr-2">Status</th>
                          <th className="py-2 pr-2">Due</th>
                          <th className="py-2 pr-2">Cert/Ref</th>
                          <th className="py-2 pr-2">Completed By</th>
                          <th className="py-2 pr-2">Completed</th>
                        </tr>
                      </thead>
                      <tbody>
                        {(config?.trainings || []).map((t, i) => {
                          const tr = selected.training[i] || ({} as TrainingRow);
                          return (
                            <tr key={i} className="border-b border-gray-800">
                              <td className="py-2 pr-2 text-gray-200">
                                {t.name}
                                {t.recurring && <span className="ml-1 text-[9px] px-1.5 py-0.5 bg-red-900/40 text-red-300 rounded font-bold">ANNUAL</span>}
                              </td>
                              <td className="py-2 pr-2">
                                <select value={tr.status || 'Not Started'} onChange={(e) => updateTraining(i, 'status', e.target.value)} className="bg-gray-800 border border-gray-700 rounded px-2 py-1 text-xs text-white">
                                  <option>Not Started</option>
                                  <option>In Progress</option>
                                  <option>Complete</option>
                                </select>
                              </td>
                              <td className="py-2 pr-2">
                                <input type="date" value={tr.due || ''} onChange={(e) => updateTraining(i, 'due', e.target.value)} className="bg-gray-800 border border-gray-700 rounded px-2 py-1 text-xs text-white" />
                              </td>
                              <td className="py-2 pr-2">
                                <input type="text" value={tr.certRef || ''} onChange={(e) => updateTraining(i, 'certRef', e.target.value)} placeholder="Cert #" className="w-20 bg-gray-800 border border-gray-700 rounded px-2 py-1 text-xs text-white" />
                              </td>
                              <td className="py-2 pr-2">
                                <input type="text" value={tr.completedBy || ''} onChange={(e) => updateTraining(i, 'completedBy', e.target.value)} placeholder="Initials" className="w-16 bg-gray-800 border border-gray-700 rounded px-2 py-1 text-xs text-white" />
                              </td>
                              <td className="py-2 pr-2 text-gray-500">{tr.completedDate || '—'}</td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>
                </NexusPanel>

                <NexusPanel title="Exclusion Screening Log — OIG LEIE + GSA SAM.gov (required at hire and monthly thereafter)" className="mb-4">
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mb-3">
                    <input type="date" value={scrDate} onChange={(e) => setScrDate(e.target.value)} className="bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm text-white" />
                    <select value={scrResult} onChange={(e) => setScrResult(e.target.value)} className="bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm text-white">
                      <option>Clear</option>
                      <option>Flagged — escalated to Compliance</option>
                    </select>
                    <input type="text" value={scrNotes} onChange={(e) => setScrNotes(e.target.value)} placeholder="Notes (optional)" className="bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm text-white" />
                  </div>
                  <button type="button" onClick={submitScreening} className={NEXUS_BTN_PRIMARY}>Log Screening Entry</button>

                  <div className="mt-4 overflow-x-auto">
                    <table className="w-full text-xs">
                      <thead>
                        <tr className="text-purple-400 uppercase text-[10px] tracking-wide text-left border-b border-gray-700">
                          <th className="py-2 pr-2">Date</th>
                          <th className="py-2 pr-2">Result</th>
                          <th className="py-2 pr-2">Notes</th>
                          <th className="py-2 pr-2">Logged By</th>
                          <th className="py-2 pr-2">Timestamp</th>
                        </tr>
                      </thead>
                      <tbody>
                        {(selected.exclusionLog || []).length === 0 ? (
                          <tr><td colSpan={5} className="py-4 text-center text-gray-500">No screening entries logged yet.</td></tr>
                        ) : (
                          [...selected.exclusionLog].reverse().map((e, i) => {
                            const flagged = e.result?.startsWith('Flagged');
                            return (
                              <tr key={i} className="border-b border-gray-800">
                                <td className="py-2 pr-2 text-gray-200">{e.date}</td>
                                <td className={`py-2 pr-2 ${flagged ? 'text-red-400' : 'text-emerald-400'}`}>{e.result}</td>
                                <td className="py-2 pr-2 text-gray-400">{e.notes || '—'}</td>
                                <td className="py-2 pr-2 text-gray-400">{e.loggedBy}</td>
                                <td className="py-2 pr-2 text-gray-500">{e.ts?.slice(0, 16).replace('T', ' ')}</td>
                              </tr>
                            );
                          })
                        )}
                      </tbody>
                    </table>
                  </div>
                </NexusPanel>

                <NexusPanel title="Audit Log — append-only, 10-year retention per CMS FDR standard (42 CFR 422.504(d))">
                  <div className="overflow-x-auto max-h-64 overflow-y-auto">
                    <table className="w-full text-xs">
                      <thead>
                        <tr className="text-purple-400 uppercase text-[10px] tracking-wide text-left border-b border-gray-700">
                          <th className="py-2 pr-2">Timestamp</th>
                          <th className="py-2 pr-2">Actor</th>
                          <th className="py-2 pr-2">Action</th>
                        </tr>
                      </thead>
                      <tbody>
                        {[...(selected.auditLog || [])].reverse().map((a, i) => (
                          <tr key={i} className="border-b border-gray-800">
                            <td className="py-2 pr-2 text-gray-500 whitespace-nowrap">{a.ts?.slice(0, 16).replace('T', ' ')}</td>
                            <td className="py-2 pr-2 text-gray-300">{a.actor}</td>
                            <td className="py-2 pr-2 text-gray-300">{a.action}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </NexusPanel>

                {onNavigate && (
                  <div className="flex flex-wrap gap-2 mt-4">
                    <p className="w-full text-xs text-gray-500 mb-1">
                      MCO/HIDE SNP-facing assignments should confirm the compliance gate first — Compass tracks contract-level FDR audit evidence.
                    </p>
                    <button type="button" onClick={() => onNavigate('compass', 'dashboard')} className={NEXUS_BTN_SECONDARY}>Open COMPASS</button>
                    <button type="button" onClick={() => onNavigate('vertex', 'dashboard')} className={NEXUS_BTN_SECONDARY}>Open VERTEX</button>
                  </div>
                )}
              </>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default HRSystem;
