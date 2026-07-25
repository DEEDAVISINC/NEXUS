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
interface TrainingDef {
  name: string; source: string; recurrence: string; interval_months: number | null;
  recurrence_label: string; contractor_trigger: string; contractor_default: string;
  cms_hard_deadline_days?: number; employee_only?: boolean;
}
interface TrainingRow {
  status: string; due: string; certRef: string; completedBy: string; completedDate: string;
  applicable?: 'yes' | 'no' | 'pending';
}
interface ScreeningEntry { date: string; result: string; notes: string; loggedBy: string; ts: string; }
interface AuditEntry { ts: string; actor: string; action: string; }
interface ComplianceState {
  state: string; severity: 'none' | 'info' | 'warning' | 'critical'; nextDue: string | null; detail: string;
}
interface Classification {
  boundedScope: boolean; ownToolsSchedule: boolean; worksOtherClients: boolean;
  noSupervisoryIntegration: boolean; deliverableBasedPay: boolean;
  notes: string; routedToCounsel: boolean; routedDate: string;
}
interface AgendaPhase { items: boolean[]; notes: string; }
interface Attestation {
  year: number; attested: boolean; attestorName: string; attestedDate: string; referenceNotes: string;
}

interface PortalActivity {
  lastLogin: string | null;
  loginCount: number;
  lastIp?: string | null;
}

interface RosterRow {
  id: string;
  name: string;
  email?: string;
  workerType: 'employee' | 'contractor';
  division: string;
  startdate: string;
  status: 'Active' | 'Archived';
  memberFacing: boolean;
  progress: number;
  screening: string;
  portalActivity?: PortalActivity;
}

interface GatewayDocument {
  key: string; label: string; filename: string; uploadedAt: string; sizeBytes: number;
  localPath?: string; attachmentUrl?: string | null;
}
interface GatewayAcknowledgment {
  key: string; label: string; typedName: string; ip: string; ts: string;
}

interface HRRecord extends RosterRow {
  email?: string;
  checklist: Record<string, boolean[]>;
  training: TrainingRow[];
  exclusionLog: ScreeningEntry[];
  classification: Classification | null;
  agenda: Record<string, AgendaPhase>;
  documents?: GatewayDocument[];
  acknowledgments?: GatewayAcknowledgment[];
  auditLog: AuditEntry[];
  _progress?: number;
  _trainingCompliance?: ComplianceState[];
  _screening?: ComplianceState;
}

interface Config {
  phases_employee: PhaseItem[];
  phases_contractor: PhaseItem[];
  trainings: TrainingDef[];
  divisions: string[];
  agendas: Record<string, string[]>;
  internal_target_days: number;
  cms_hard_deadline_days: number;
  screening_cadence_months: number;
}

interface AlertRow { id: string; name: string; division?: string; workerType?: string; training?: string; detail: string; nextDue: string | null; }

interface Alerts {
  training_cms_hard_missed: AlertRow[];
  training_internal_target_missed: AlertRow[];
  training_recurrence_due: AlertRow[];
  training_pending_scoping: AlertRow[];
  screening_flagged_open: AlertRow[];
  screening_never: AlertRow[];
  screening_overdue: AlertRow[];
  fdr_attestation_current_year: number;
  fdr_attestation_on_file: boolean;
  active_count: number;
  alert_count: number;
}

/** CRM-style contact card for the roster grid — avatar, name, chips, progress ring. */
const RosterCard: React.FC<{
  r: RosterRow;
  status: RosterStatus;
  onOpen: () => void;
  onArchive?: () => void;
  compact?: boolean;
}> = ({ r, status, onOpen, onArchive, compact }) => {
  const days = daysSince(r.startdate);
  return (
    <div className={`bg-gradient-to-br from-gray-800 to-gray-900 rounded-xl border ${
      r.status === 'Archived' ? 'border-gray-700/40 opacity-60' : 'border-purple-500/20'
    } p-4 flex flex-col gap-3 hover:border-purple-500/40 transition-all`}>
      <div className="flex items-start gap-3">
        <Avatar name={r.name} workerType={r.workerType} size={compact ? 'sm' : 'md'} />
        <div className="min-w-0 flex-1">
          <button type="button" onClick={onOpen} className="font-bold text-white text-sm hover:text-purple-300 transition-colors text-left truncate block w-full">
            {r.name}
          </button>
          <div className="text-xs text-gray-400 truncate">
            {WORKER_LABEL[r.workerType]}{r.division ? ` · ${r.division}` : ''}
          </div>
        </div>
        <ProgressRing pct={r.progress} size={compact ? 40 : 48} strokeWidth={4} />
      </div>

      <div className="flex items-center justify-between gap-2">
        <span className="text-[11px] text-gray-500">
          {days !== null ? (days >= 0 ? `Day ${days} of onboarding` : `Starts in ${Math.abs(days)}d`) : '—'}
        </span>
        {r.status === 'Archived' ? (
          <span className="text-[10px] uppercase tracking-wide text-gray-500 border border-gray-600 px-1.5 py-0.5 rounded">Archived</span>
        ) : (
          <StatusChip status={status} />
        )}
      </div>

      {r.status === 'Active' && (
        <PortalActivityBadge activity={r.portalActivity} hasEmail={!!r.email} />
      )}

      {!compact && (
        <div className="flex gap-2 pt-1 border-t border-gray-700/50">
          <button type="button" onClick={onOpen} className="flex-1 text-xs font-semibold text-purple-300 hover:text-purple-200 py-1.5 transition-colors">
            View Profile →
          </button>
          {onArchive && r.status === 'Active' && (
            <button type="button" onClick={onArchive} className="text-xs px-2 py-1.5 text-red-400/80 hover:text-red-300 transition-colors">
              Archive
            </button>
          )}
        </div>
      )}
    </div>
  );
};

const TAB_IDS = ['dashboard', 'roster', 'detail'] as const;

const WORKER_LABEL: Record<string, string> = {
  employee: 'Employee (W-2)',
  contractor: 'Contractor (1099)',
};

const SEVERITY_STYLE: Record<string, string> = {
  critical: 'bg-red-900/30 border-red-500/50 text-red-300',
  warning: 'bg-amber-900/20 border-amber-500/40 text-amber-300',
  info: 'bg-blue-900/20 border-blue-500/40 text-blue-300',
  none: 'bg-emerald-900/10 border-emerald-600/30 text-emerald-300',
};

const STATE_LABEL: Record<string, string> = {
  cms_hard_missed: 'CMS 90-DAY FLOOR MISSED',
  internal_target_missed: 'PAST 30-DAY TARGET',
  recurrence_due: 'RECURRENCE DUE',
  pending_scoping: 'PENDING SCOPING',
  pending: 'NOT YET DUE',
  not_applicable: 'N/A',
  ok: 'CURRENT',
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

// ─────────────────────────── CRM-style presentation helpers ───────────────────────────
// The compliance engine underneath is intentionally strict (CMS FDR citations, exclusion
// screening cadence, audit trails). None of that belongs on the first screen someone sees.
// These helpers turn raw roster/status data into something that reads like an onboarding
// CRM (avatars, pipeline stages, plain-language status) — the regulatory detail still
// exists, it just lives one click away in the "Compliance & Audit" tab.

function initials(name: string): string {
  const parts = name.trim().split(/\s+/).filter(Boolean);
  if (parts.length === 0) return '?';
  if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase();
  return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
}

const AVATAR_COLORS: Record<string, string> = {
  employee: 'from-purple-500 to-pink-500',
  contractor: 'from-teal-500 to-blue-500',
};

const Avatar: React.FC<{ name: string; workerType: string; size?: 'sm' | 'md' | 'lg' }> = ({ name, workerType, size = 'md' }) => {
  const dims = size === 'lg' ? 'w-16 h-16 text-lg' : size === 'sm' ? 'w-9 h-9 text-xs' : 'w-11 h-11 text-sm';
  return (
    <div className={`${dims} rounded-full bg-gradient-to-br ${AVATAR_COLORS[workerType] || AVATAR_COLORS.employee} flex items-center justify-center font-bold text-white shrink-0 shadow-lg`}>
      {initials(name)}
    </div>
  );
};

const ProgressRing: React.FC<{ pct: number; size?: number; strokeWidth?: number; label?: string }> = ({ pct, size = 56, strokeWidth = 5, label }) => {
  const clamped = Math.max(0, Math.min(100, pct));
  const r = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * r;
  const offset = circumference * (1 - clamped / 100);
  const color = clamped >= 100 ? '#34d399' : clamped >= 50 ? '#a78bfa' : '#fbbf24';
  return (
    <div className="relative shrink-0" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="-rotate-90">
        <circle cx={size / 2} cy={size / 2} r={r} stroke="#374151" strokeWidth={strokeWidth} fill="none" />
        <circle
          cx={size / 2} cy={size / 2} r={r} stroke={color} strokeWidth={strokeWidth} fill="none"
          strokeDasharray={circumference} strokeDashoffset={offset} strokeLinecap="round"
          style={{ transition: 'stroke-dashoffset 0.4s ease' }}
        />
      </svg>
      <div className="absolute inset-0 flex items-center justify-center text-xs font-bold text-white">
        {label || `${Math.round(clamped)}%`}
      </div>
    </div>
  );
};

type RosterStatus = 'critical' | 'warning' | 'info' | 'complete' | 'on_track';

const STATUS_CHIP_STYLE: Record<RosterStatus, string> = {
  critical: 'bg-red-900/30 border-red-500/50 text-red-300',
  warning: 'bg-amber-900/20 border-amber-500/40 text-amber-300',
  info: 'bg-blue-900/20 border-blue-500/40 text-blue-300',
  complete: 'bg-emerald-900/20 border-emerald-500/40 text-emerald-300',
  on_track: 'bg-purple-900/20 border-purple-500/40 text-purple-300',
};

const STATUS_CHIP_LABEL: Record<RosterStatus, string> = {
  critical: '🚨 Needs Attention',
  warning: '⏰ Attention Soon',
  info: '🧭 Scoping Needed',
  complete: '✅ Complete',
  on_track: '🟣 On Track',
};

function daysSince(startdate?: string): number | null {
  if (!startdate) return null;
  const start = new Date(startdate);
  if (Number.isNaN(start.getTime())) return null;
  const diff = Math.floor((Date.now() - start.getTime()) / (1000 * 60 * 60 * 24));
  return diff;
}

/** Plain-language "last active" for GATEWAY portal visibility — this is what
 * lets Dee see whether the employee/contractor has even logged into
 * gateway.deedavis.biz yet, not just what they've uploaded/signed once they do. */
function timeAgo(iso?: string | null): string {
  if (!iso) return 'Never signed in';
  const then = new Date(iso).getTime();
  if (Number.isNaN(then)) return 'Never signed in';
  const diffMs = Date.now() - then;
  const mins = Math.floor(diffMs / 60000);
  if (mins < 1) return 'Just now';
  if (mins < 60) return `${mins}m ago`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  if (days < 30) return `${days}d ago`;
  const months = Math.floor(days / 30);
  return `${months}mo ago`;
}

const PortalActivityBadge: React.FC<{ activity?: PortalActivity; hasEmail: boolean }> = ({ activity, hasEmail }) => {
  if (!hasEmail) {
    return <span className="text-[10px] text-gray-500">🔑 No portal access — add email</span>;
  }
  const logged = !!activity?.lastLogin;
  return (
    <span className={`text-[10px] font-semibold ${logged ? 'text-teal-400' : 'text-amber-400'}`}>
      🔑 {logged ? `Portal: active ${timeAgo(activity?.lastLogin)}` : 'Portal: invited, not signed in yet'}
    </span>
  );
};

const StatusChip: React.FC<{ status: RosterStatus; className?: string }> = ({ status, className = '' }) => (
  <span className={`text-[10px] font-bold uppercase tracking-wide px-2 py-1 rounded-full border whitespace-nowrap ${STATUS_CHIP_STYLE[status]} ${className}`}>
    {STATUS_CHIP_LABEL[status]}
  </span>
);

/** Horizontal onboarding-stage pipeline — the visual "where are they right now" view. */
const StagePipeline: React.FC<{
  phases: PhaseItem[];
  checklist: Record<string, boolean[]>;
  expanded: string | null;
  onSelect: (key: string) => void;
}> = ({ phases, checklist, expanded, onSelect }) => {
  const phaseComplete = (p: PhaseItem) => {
    const items = checklist[p.key] || [];
    return p.items.length > 0 && p.items.every((_, i) => items[i]);
  };
  const currentIdx = phases.findIndex((p) => !phaseComplete(p));
  const activeIdx = currentIdx === -1 ? phases.length - 1 : currentIdx;

  return (
    <div className="flex items-center overflow-x-auto pb-2">
      {phases.map((p, i) => {
        const done = phaseComplete(p);
        const isCurrent = i === activeIdx && !done;
        const isSelected = expanded === p.key;
        return (
          <React.Fragment key={p.key}>
            {i > 0 && (
              <div className={`h-0.5 w-8 sm:w-12 shrink-0 ${i <= activeIdx ? 'bg-purple-500' : 'bg-gray-700'}`} />
            )}
            <button
              type="button"
              onClick={() => onSelect(p.key)}
              className="flex flex-col items-center gap-1.5 shrink-0 group"
              title={p.title}
            >
              <div className={[
                'w-9 h-9 rounded-full flex items-center justify-center text-sm font-bold border-2 transition-all',
                done ? 'bg-emerald-500 border-emerald-400 text-white' :
                  isCurrent ? 'bg-purple-600 border-purple-400 text-white ring-4 ring-purple-500/30' :
                    'bg-gray-800 border-gray-600 text-gray-500',
                isSelected ? 'scale-110' : 'group-hover:scale-105',
              ].join(' ')}>
                {done ? '✓' : i + 1}
              </div>
              <span className={`text-[10px] font-semibold text-center max-w-[80px] leading-tight ${
                isCurrent ? 'text-purple-300' : done ? 'text-emerald-400' : 'text-gray-500'
              }`}>
                {p.title}
              </span>
            </button>
          </React.Fragment>
        );
      })}
    </div>
  );
};

const HRSystem: React.FC<HRSystemProps> = ({ onBackToNexus, onNavigate, activeTab, setActiveTab }) => {
  const resolvedTab = TAB_IDS.includes(activeTab as (typeof TAB_IDS)[number]) ? activeTab : 'dashboard';

  const [config, setConfig] = useState<Config | null>(null);
  const [roster, setRoster] = useState<RosterRow[]>([]);
  const [alerts, setAlerts] = useState<Alerts | null>(null);
  const [attestations, setAttestations] = useState<Attestation[]>([]);
  const [selected, setSelected] = useState<HRRecord | null>(null);
  const [loading, setLoading] = useState(true);
  const [apiError, setApiError] = useState<string | null>(null);
  const [actor, setActor] = useState<string>(() => localStorage.getItem('nexus_hr_actor') || '');

  // Add-hire form state
  const [nhName, setNhName] = useState('');
  const [nhType, setNhType] = useState<'employee' | 'contractor'>('employee');
  const [nhDivision, setNhDivision] = useState('');
  const [nhStart, setNhStart] = useState('');
  const [nhMemberFacing, setNhMemberFacing] = useState(true);
  const [nhEmail, setNhEmail] = useState('');
  const [adding, setAdding] = useState(false);

  // Screening form state (detail view)
  const [scrDate, setScrDate] = useState('');
  const [scrResult, setScrResult] = useState('Clear');
  const [scrNotes, setScrNotes] = useState('');

  // Attestation form state (dashboard)
  const [attYear, setAttYear] = useState<number>(new Date().getFullYear());
  const [attName, setAttName] = useState('');
  const [attNotes, setAttNotes] = useState('');
  const [attSaving, setAttSaving] = useState(false);

  // Profile view state — which phase is expanded in the stage pipeline, and
  // whether we're looking at the friendly Overview or the technical Compliance tab
  const [expandedPhase, setExpandedPhase] = useState<string | null>(null);
  const [detailInnerTab, setDetailInnerTab] = useState<'overview' | 'compliance'>('overview');
  const [showAddHireForm, setShowAddHireForm] = useState(false);

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

  const loadAttestations = useCallback(async () => {
    try {
      const res: any = await api.getHrFdrAttestations();
      setAttestations(res?.attestations || []);
    } catch { setAttestations([]); }
  }, []);

  useEffect(() => {
    loadConfig();
    loadRoster();
    loadAlerts();
    loadAttestations();
  }, [loadConfig, loadRoster, loadAlerts, loadAttestations]);

  const openDetail = useCallback(async (id: string) => {
    try {
      const res: any = await api.getHrOnboardingRecord(id);
      setSelected(res);
      setActiveTab('detail');
      setDetailInnerTab('overview');
      setExpandedPhase(null);
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
        ...( { memberFacing: nhMemberFacing, email: nhEmail.trim().toLowerCase() } as any),
      });
      setNhName(''); setNhDivision(''); setNhStart(''); setNhType('employee'); setNhMemberFacing(true); setNhEmail('');
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
    await loadRoster();
    await loadAlerts();
  };

  const updateClassification = async (field: keyof Classification, value: boolean | string) => {
    if (!selected) return;
    await api.updateHrOnboardingClassification(selected.id, { [field]: value, actor } as any);
    await refreshSelected();
  };

  const updateAgenda = async (phase: string, index: number, checked: boolean) => {
    if (!selected) return;
    await api.updateHrOnboardingAgenda(selected.id, { phase, index, checked, actor });
    await refreshSelected();
  };

  const updateAgendaNotes = async (phase: string, notes: string) => {
    if (!selected) return;
    await api.updateHrOnboardingAgenda(selected.id, { phase, notes, actor });
    await refreshSelected();
  };

  const toggleMemberFacing = async () => {
    if (!selected) return;
    await api.updateHrOnboardingMemberFacing(selected.id, { memberFacing: !selected.memberFacing, actor });
    await refreshSelected();
    await loadAlerts();
  };

  const submitAttestation = async () => {
    if (!attName.trim()) { alert('Enter the attesting officer\'s name.'); return; }
    setAttSaving(true);
    try {
      await api.addHrFdrAttestation({ year: attYear, attestorName: attName.trim(), referenceNotes: attNotes, actor });
      setAttName(''); setAttNotes('');
      await loadAttestations();
      await loadAlerts();
    } catch (e: any) {
      alert(e?.message || 'Could not save attestation');
    } finally {
      setAttSaving(false);
    }
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
    lines.push('DDI NEXUS GATEWAY Onboarding Record Export');
    lines.push([csvEscape('Name'), csvEscape(rec.name)].join(','));
    lines.push([csvEscape('Worker Type'), csvEscape(WORKER_LABEL[rec.workerType])].join(','));
    lines.push([csvEscape('Division'), csvEscape(rec.division)].join(','));
    lines.push([csvEscape('Date of Hire/Engagement'), csvEscape(rec.startdate)].join(','));
    lines.push([csvEscape('Member-Facing'), csvEscape(rec.memberFacing ? 'Yes' : 'No')].join(','));
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
    lines.push([csvEscape('Training'), csvEscape('Applicable'), csvEscape('Status'), csvEscape('Completed Date'), csvEscape('Recurrence'), csvEscape('Compliance State'), csvEscape('Next Due')].join(','));
    config.trainings.forEach((t, i) => {
      const tr = rec.training[i] || ({} as TrainingRow);
      const comp = rec._trainingCompliance?.[i];
      lines.push([csvEscape(t.name), csvEscape(tr.applicable || 'yes'), csvEscape(tr.status), csvEscape(tr.completedDate), csvEscape(t.recurrence_label), csvEscape(comp?.state || ''), csvEscape(comp?.nextDue || '')].join(','));
    });
    lines.push('');
    lines.push('EXCLUSION SCREENING LOG (OIG LEIE + GSA SAM.gov — monthly cadence)');
    lines.push([csvEscape('Date'), csvEscape('Result'), csvEscape('Notes'), csvEscape('Logged By'), csvEscape('Timestamp')].join(','));
    (rec.exclusionLog || []).forEach((e) => {
      lines.push([csvEscape(e.date), csvEscape(e.result), csvEscape(e.notes), csvEscape(e.loggedBy), csvEscape(e.ts)].join(','));
    });
    if (rec.classification) {
      lines.push('');
      lines.push('WORKER CLASSIFICATION DOCUMENTATION');
      lines.push([csvEscape('Bounded scope of work'), csvEscape(rec.classification.boundedScope ? 'Yes' : 'No')].join(','));
      lines.push([csvEscape('Own tools/schedule'), csvEscape(rec.classification.ownToolsSchedule ? 'Yes' : 'No')].join(','));
      lines.push([csvEscape('Works for other clients'), csvEscape(rec.classification.worksOtherClients ? 'Yes' : 'No')].join(','));
      lines.push([csvEscape('No supervisory integration'), csvEscape(rec.classification.noSupervisoryIntegration ? 'Yes' : 'No')].join(','));
      lines.push([csvEscape('Deliverable-based pay'), csvEscape(rec.classification.deliverableBasedPay ? 'Yes' : 'No')].join(','));
      lines.push([csvEscape('Routed to counsel'), csvEscape(rec.classification.routedToCounsel ? `Yes (${rec.classification.routedDate})` : 'No')].join(','));
      lines.push([csvEscape('Notes'), csvEscape(rec.classification.notes)].join(','));
    }
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
    lines.push([csvEscape('Name'), csvEscape('Worker Type'), csvEscape('Division'), csvEscape('Date of Hire/Engagement'), csvEscape('Status'), csvEscape('Completion %'), csvEscape('Screening State')].join(','));
    roster.forEach((r) => {
      lines.push([csvEscape(r.name), csvEscape(WORKER_LABEL[r.workerType]), csvEscape(r.division), csvEscape(r.startdate), csvEscape(r.status), csvEscape(r.progress + '%'), csvEscape(r.screening)].join(','));
    });
    downloadCsv(`DDI_HR_Onboarding_Roster_${new Date().toISOString().slice(0, 10)}.csv`, lines);
  };

  const activeRoster = useMemo(() => roster.filter((r) => r.status === 'Active'), [roster]);
  const currentYear = new Date().getFullYear();
  const currentAttestation = attestations.find((a) => a.year === currentYear);

  // Roll every alert bucket into a single "how worried should I be about this person"
  // status so the roster cards can show one plain-language chip instead of raw
  // compliance-state jargon.
  const rosterStatusById = useMemo(() => {
    const map = new Map<string, RosterStatus>();
    if (alerts) {
      const mark = (rows: AlertRow[], status: RosterStatus) => {
        rows.forEach((r) => {
          const existing = map.get(r.id);
          const rank: Record<RosterStatus, number> = { critical: 3, warning: 2, info: 1, complete: 0, on_track: 0 };
          if (!existing || rank[status] > rank[existing]) map.set(r.id, status);
        });
      };
      mark(alerts.screening_flagged_open, 'critical');
      mark(alerts.training_cms_hard_missed, 'critical');
      mark(alerts.screening_never, 'critical');
      mark(alerts.screening_overdue, 'warning');
      mark(alerts.training_internal_target_missed, 'warning');
      mark(alerts.training_recurrence_due, 'warning');
      mark(alerts.training_pending_scoping, 'info');
    }
    return map;
  }, [alerts]);

  const statusForRow = useCallback((r: RosterRow): RosterStatus => {
    return rosterStatusById.get(r.id) || (r.progress >= 100 ? 'complete' : 'on_track');
  }, [rosterStatusById]);

  // Which phase should be open in the profile pipeline — defaults to the first
  // incomplete phase (i.e. "where they actually are right now"), unless the
  // user has clicked a different node on the pipeline.
  const currentPhases = useMemo(() => (selected ? phasesFor(selected.workerType) : []), [selected, phasesFor]);
  const defaultPhaseKey = useMemo(() => {
    if (!selected || currentPhases.length === 0) return null;
    const firstIncomplete = currentPhases.find((p) => {
      const items = selected.checklist?.[p.key] || [];
      return !(p.items.length > 0 && p.items.every((_, i) => items[i]));
    });
    return (firstIncomplete || currentPhases[currentPhases.length - 1]).key;
  }, [selected, currentPhases]);
  const activePhaseKey = expandedPhase || defaultPhaseKey;
  const activePhase = currentPhases.find((p) => p.key === activePhaseKey) || null;

  const tabs = [
    { id: 'dashboard', label: 'Dashboard', icon: '📊' },
    { id: 'roster', label: 'Roster', icon: '🧑‍💼' },
    { id: 'detail', label: 'Onboarding Detail', icon: '🗂️' },
  ];

  const AlertBadge: React.FC<{ row: AlertRow; icon: string; severity: 'critical' | 'warning' | 'info' }> = ({ row, icon, severity }) => (
    <div className={`p-3 rounded-lg border flex justify-between items-center ${SEVERITY_STYLE[severity]}`}>
      <span>
        {icon} <span className="font-semibold">{row.name}</span>
        {row.division ? ` (${row.division})` : ''}{row.workerType ? ` — ${WORKER_LABEL[row.workerType]}` : ''}
        {row.training ? ` — ${row.training}` : ''}: {row.detail}
      </span>
      <button onClick={() => openDetail(row.id)} className={NEXUS_BTN_SECONDARY}>Open</button>
    </div>
  );

  return (
    <div className={NEXUS_SHELL_PAGE}>
      <div className={`${NEXUS_SHELL_PAD} ${NEXUS_CONTAINER}`}>
        <div className="flex flex-wrap items-start justify-between gap-4 mb-6">
          <div>
            <button type="button" onClick={onBackToNexus} className="text-sm text-gray-400 hover:text-white mb-2 transition-colors">
              ← NEXUS Command Center
            </button>
            <h1 className={NEXUS_TITLE}>GATEWAY</h1>
            <p className={NEXUS_SUBTITLE}>
              Automates the DDI New Hire &amp; Independent Contractor Onboarding SOPs — Pre-boarding → Day 1 → Week 1 → 30/60/90 Day
              (employees) / Pre-Engagement → Start → Ongoing → Renewal (contractors). CMS FDR training recurrence,
              monthly OIG LEIE/GSA SAM exclusion screening, annual FDR attestation, worker-classification documentation.
              Self-service at <span className="text-teal-400">gateway.deedavis.biz</span> — new hires/contractors upload
              documents and sign acknowledgments themselves.
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
            <button type="button" onClick={() => { loadRoster(); loadAlerts(); loadAttestations(); }} className={NEXUS_BTN_SECONDARY}>
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
              <NexusMetricCard label="CMS 90-Day Floor Missed" value={alerts?.training_cms_hard_missed.length || 0} icon="🚨" accent={alerts?.training_cms_hard_missed.length ? 'red' : 'green'} />
              <NexusMetricCard label="Screening Overdue/Never" value={(alerts?.screening_overdue.length || 0) + (alerts?.screening_never.length || 0)} icon="🔍" accent={((alerts?.screening_overdue.length || 0) + (alerts?.screening_never.length || 0)) ? 'yellow' : 'green'} />
              <NexusMetricCard label="Flagged — Escalate" value={alerts?.screening_flagged_open.length || 0} icon="🚨" accent={alerts?.screening_flagged_open.length ? 'red' : 'green'} />
            </div>

            <NexusPanel title={`📋 Annual FDR Compliance Attestation — Calendar Year ${currentYear}`} className="mb-6">
              {currentAttestation ? (
                <div className="p-3 bg-emerald-900/15 border border-emerald-600/30 rounded-lg text-sm text-emerald-300">
                  ✅ Attested by <strong>{currentAttestation.attestorName}</strong> on {currentAttestation.attestedDate}.
                  {currentAttestation.referenceNotes ? ` Reference: ${currentAttestation.referenceNotes}` : ''}
                </div>
              ) : (
                <>
                  <div className="p-3 mb-3 bg-amber-900/20 border border-amber-500/40 rounded-lg text-sm text-amber-300">
                    ⚠️ No attestation on file for {currentYear}. Per SOP Section 6, an authorized DDI representative
                    (Compliance Officer / President) must attest annually that General Compliance/FWA training,
                    Code of Conduct distribution, and OIG LEIE/GSA SAM screening are complete and current for all
                    applicable personnel (employees and contractors touching Medicaid/Medicare-adjacent work).
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mb-3">
                    <input type="number" value={attYear} onChange={(e) => setAttYear(parseInt(e.target.value, 10) || currentYear)} className="bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm text-white" />
                    <input value={attName} onChange={(e) => setAttName(e.target.value)} placeholder="Attesting officer (e.g. Dieasha D. Davis)" className="bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm text-white" />
                    <input value={attNotes} onChange={(e) => setAttNotes(e.target.value)} placeholder="Reference notes (optional)" className="bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm text-white" />
                  </div>
                  <button type="button" onClick={submitAttestation} disabled={attSaving} className={NEXUS_BTN_PRIMARY}>
                    {attSaving ? 'Saving…' : `Attest for ${attYear}`}
                  </button>
                </>
              )}
              {attestations.length > 0 && (
                <div className="mt-3 text-xs text-gray-500">
                  Prior attestations on file: {attestations.filter(a => a.year !== currentYear).map(a => a.year).join(', ') || '—'}
                </div>
              )}
            </NexusPanel>

            {alerts && alerts.alert_count > 0 && (
              <NexusPanel title="⚠️ Compliance Alerts — CMS FDR Audit Readiness (COMPASS)">
                <div className="space-y-2 text-sm">
                  {alerts.screening_flagged_open.map((a) => <AlertBadge key={`flag-${a.id}`} row={a} icon="🚨" severity="critical" />)}
                  {alerts.training_cms_hard_missed.map((a, i) => <AlertBadge key={`hard-${a.id}-${i}`} row={a} icon="🚨" severity="critical" />)}
                  {alerts.screening_never.map((a) => <AlertBadge key={`never-${a.id}`} row={a} icon="🔍" severity="critical" />)}
                  {alerts.screening_overdue.map((a) => <AlertBadge key={`overdue-${a.id}`} row={a} icon="🔍" severity="warning" />)}
                  {alerts.training_internal_target_missed.map((a, i) => <AlertBadge key={`soft-${a.id}-${i}`} row={a} icon="⏰" severity="warning" />)}
                  {alerts.training_recurrence_due.map((a, i) => <AlertBadge key={`recur-${a.id}-${i}`} row={a} icon="🔁" severity="warning" />)}
                  {alerts.training_pending_scoping.map((a, i) => <AlertBadge key={`scope-${a.id}-${i}`} row={a} icon="🧭" severity="info" />)}
                </div>
              </NexusPanel>
            )}

            <NexusPanel title="Currently Onboarding" className="mt-6">
              {loading ? (
                <p className="text-gray-400 text-sm">Loading roster…</p>
              ) : activeRoster.length === 0 ? (
                <p className="text-gray-400 text-sm">No active employees or contractors yet. Add one in the Roster tab.</p>
              ) : (
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                  {activeRoster.slice(0, 6).map((r) => (
                    <RosterCard key={r.id} r={r} status={statusForRow(r)} onOpen={() => openDetail(r.id)} compact />
                  ))}
                </div>
              )}
              {activeRoster.length > 6 && (
                <button type="button" onClick={() => setActiveTab('roster')} className="text-xs text-purple-400 hover:text-purple-300 mt-3">
                  View all {activeRoster.length} in Roster →
                </button>
              )}
            </NexusPanel>

            <p className="text-xs text-gray-500 mt-4">
              GATEWAY handles onboarding for internal DDI employees &amp; engaged contractors only. Field agents (PRISM) and
              external subcontractors/suppliers (GPSS) follow the separate pipeline in NEXUS_ONBOARDING_SYSTEM.md.
            </p>
          </>
        )}

        {/* ─────────── ROSTER ─────────── */}
        {resolvedTab === 'roster' && (
          <>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-bold text-white">Roster ({roster.length})</h3>
              <div className="flex gap-2">
                <button type="button" onClick={exportRoster} className={NEXUS_BTN_SECONDARY}>Export (CSV)</button>
                <button type="button" onClick={() => setShowAddHireForm((v) => !v)} className={NEXUS_BTN_PRIMARY}>
                  {showAddHireForm ? '✕ Cancel' : '+ New Hire / Engagement'}
                </button>
              </div>
            </div>

            {showAddHireForm && (
            <NexusPanel title="Add New Hire / Engagement" className="mb-4">
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3 mb-3">
                <input
                  value={nhName}
                  onChange={(e) => setNhName(e.target.value)}
                  placeholder="Full name"
                  className="bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm text-white"
                />
                <input
                  type="email"
                  value={nhEmail}
                  onChange={(e) => setNhEmail(e.target.value)}
                  placeholder="Email (enables GATEWAY portal)"
                  title="This email is how they sign in to the GATEWAY self-service portal at gateway.deedavis.biz — no email, no portal access"
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
                  title="Date of hire/engagement — anchors the 90-day CMS training floor and 10-year retention clock"
                  className="bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm text-white"
                />
                <label className="flex items-center gap-2 text-xs text-gray-300 bg-gray-800 border border-gray-700 rounded px-3 py-2">
                  <input type="checkbox" checked={nhMemberFacing} onChange={(e) => setNhMemberFacing(e.target.checked)} className="w-4 h-4 accent-purple-500" />
                  Member-facing role
                </label>
              </div>
              <button type="button" onClick={handleAddHire} disabled={adding} className={NEXUS_BTN_PRIMARY}>
                {adding ? 'Adding…' : 'Add New Hire / Engagement'}
              </button>
              <p className="text-xs text-gray-500 mt-2">
                Date field = date of hire/engagement (anchors the CMS 90-day General Compliance/FWA + Medicare Fraud &amp; Abuse
                floor and the 10-year retention clock). Member-facing controls whether Recipient Rights and Abuse &amp; Neglect
                training recur annually. Email is optional but strongly recommended — it's the only way this person can sign
                into the <strong className="text-teal-400">GATEWAY portal</strong> (gateway.deedavis.biz) to upload their own
                documents and sign acknowledgments themselves instead of HR chasing paperwork.
              </p>
            </NexusPanel>
            )}

            {roster.length === 0 ? (
              <div className="text-gray-400 text-sm p-6 border border-dashed border-gray-700 rounded-lg text-center">
                No hires/engagements tracked yet. Click "+ New Hire / Engagement" to start onboarding.
              </div>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                {roster.map((r) => (
                  <RosterCard key={r.id} r={r} status={statusForRow(r)} onOpen={() => openDetail(r.id)} onArchive={() => archiveRecord(r)} />
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
                {/* ── Profile header — the "contact card" view of an onboarding CRM ── */}
                <div className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-xl border border-purple-500/20 p-5 mb-4">
                  <div className="flex flex-wrap items-start justify-between gap-4">
                    <div className="flex items-center gap-4">
                      <Avatar name={selected.name} workerType={selected.workerType} size="lg" />
                      <div>
                        <h2 className="text-xl font-bold text-white">{selected.name}</h2>
                        <p className="text-sm text-gray-400">
                          {WORKER_LABEL[selected.workerType]}{selected.division ? ` · ${selected.division}` : ''}
                        </p>
                        <p className="text-xs text-gray-500 mt-0.5">
                          {selected.email || 'No email on file'}
                          {(() => { const d = daysSince(selected.startdate); return d !== null ? ` · Day ${d} of onboarding` : ''; })()}
                        </p>
                        <div className="flex items-center gap-2 mt-2">
                          <StatusChip status={statusForRow(selected as unknown as RosterRow)} />
                          {selected.memberFacing && (
                            <span className="text-[10px] font-bold uppercase tracking-wide px-2 py-1 rounded-full border border-teal-500/40 bg-teal-900/20 text-teal-300">Member-Facing</span>
                          )}
                          <PortalActivityBadge activity={selected.portalActivity} hasEmail={!!selected.email} />
                        </div>
                      </div>
                    </div>
                    <div className="flex flex-col items-center gap-2">
                      <ProgressRing pct={selected._progress ?? 0} size={64} strokeWidth={6} />
                      <span className="text-[10px] text-gray-500">Onboarding progress</span>
                    </div>
                  </div>

                  <div className="flex gap-2 mt-4 pt-4 border-t border-gray-700/50">
                    <button type="button" onClick={toggleMemberFacing} className={NEXUS_BTN_SECONDARY}>
                      {selected.memberFacing ? '✓ Member-Facing Role' : '✗ Not Member-Facing'}
                    </button>
                    <button type="button" onClick={() => exportRecord(selected)} className={NEXUS_BTN_SECONDARY}>
                      Export Record (CSV)
                    </button>
                  </div>
                </div>

                {/* Inner tabs: friendly Overview (default) vs technical Compliance & Audit */}
                <div className="flex gap-2 mb-4">
                  {([
                    ['overview', '👤 Overview'],
                    ['compliance', '🛡️ Compliance & Audit'],
                  ] as const).map(([id, label]) => (
                    <button
                      key={id}
                      type="button"
                      onClick={() => setDetailInnerTab(id)}
                      className={`px-3 py-1.5 rounded-lg text-sm font-semibold transition-all ${detailInnerTab === id ? NEXUS_TAB_ACTIVE : NEXUS_TAB_IDLE}`}
                    >
                      {label}
                    </button>
                  ))}
                </div>

              {detailInnerTab === 'overview' && (
                <>
                {selected._screening && selected._screening.severity !== 'none' && (
                  <div className={`mb-4 p-3 rounded-lg text-sm border ${SEVERITY_STYLE[selected._screening.severity]}`}>
                    🔍 {selected._screening.detail}
                    {selected._screening.nextDue ? ` · Next check: ${selected._screening.nextDue}` : ''}
                    <button type="button" onClick={() => setDetailInnerTab('compliance')} className="ml-2 underline hover:no-underline">Details →</button>
                  </div>
                )}

                {/* GATEWAY self-service portal activity — read-only, uploads/e-signs happen at gateway.deedavis.biz */}
                <NexusPanel
                  title={`🔑 GATEWAY Portal Activity ${selected.email ? `— ${selected.email}` : '— no email on file'}`}
                  className="mb-4"
                >
                  {!selected.email ? (
                    <p className="text-sm text-amber-300">
                      No email on this record — {selected.name} cannot sign in to gateway.deedavis.biz. Add an email above to enable portal access.
                    </p>
                  ) : (
                    <>
                    <div className={`flex flex-wrap items-center gap-3 mb-4 pb-4 border-b border-gray-700/50 text-sm ${selected.portalActivity?.lastLogin ? 'text-teal-300' : 'text-amber-300'}`}>
                      <span className="font-bold">
                        {selected.portalActivity?.lastLogin
                          ? `🟢 Last active in portal: ${timeAgo(selected.portalActivity.lastLogin)}`
                          : '⚪ Has not signed in to gateway.deedavis.biz yet'}
                      </span>
                      {!!selected.portalActivity?.loginCount && (
                        <span className="text-gray-500 text-xs">{selected.portalActivity.loginCount} visit{selected.portalActivity.loginCount === 1 ? '' : 's'} total</span>
                      )}
                      {selected.portalActivity?.lastLogin && (
                        <span className="text-gray-500 text-xs">{new Date(selected.portalActivity.lastLogin).toLocaleString()}</span>
                      )}
                    </div>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
                      <div>
                        <h4 className="font-bold text-gray-300 mb-1.5">Documents Uploaded ({(selected.documents || []).length})</h4>
                        {(selected.documents || []).length === 0 ? (
                          <p className="text-gray-500">Nothing uploaded yet via the portal.</p>
                        ) : (
                          <ul className="space-y-1">
                            {(selected.documents || []).map((d: any) => (
                              <li key={d.key} className="text-gray-300">
                                {d.attachmentUrl ? (
                                  <a href={d.attachmentUrl} target="_blank" rel="noreferrer" className="text-teal-400 hover:underline">{d.label}</a>
                                ) : <span>{d.label}</span>}
                                <span className="text-gray-500"> — {d.filename} · {d.uploadedAt?.slice(0, 10)}</span>
                              </li>
                            ))}
                          </ul>
                        )}
                      </div>
                      <div>
                        <h4 className="font-bold text-gray-300 mb-1.5">Acknowledgments Signed ({(selected.acknowledgments || []).length})</h4>
                        {(selected.acknowledgments || []).length === 0 ? (
                          <p className="text-gray-500">Nothing signed yet via the portal.</p>
                        ) : (
                          <ul className="space-y-1">
                            {(selected.acknowledgments || []).map((a: any) => (
                              <li key={a.key} className="text-gray-300">
                                {a.label} — <span className="text-gray-500">signed "{a.typedName}" on {a.ts?.slice(0, 10)}</span>
                              </li>
                            ))}
                          </ul>
                        )}
                      </div>
                    </div>
                    </>
                  )}
                </NexusPanel>

                {selected.workerType === 'contractor' && (
                  <div className="mb-4 p-3 bg-amber-900/15 border border-amber-500/30 rounded-lg text-sm text-amber-300">
                    Contractor track: no I-9/E-Verify. Check-ins should reference contract deliverables, not
                    employee-style supervision, to support worker classification.
                  </div>
                )}

                <NexusPanel title="Onboarding Journey" className="mb-4">
                  <StagePipeline
                    phases={currentPhases}
                    checklist={selected.checklist || {}}
                    expanded={activePhaseKey}
                    onSelect={(key) => setExpandedPhase(key)}
                  />

                  {activePhase && (
                    <div className="mt-5 pt-5 border-t border-gray-700/50">
                      <div className="flex items-center justify-between mb-3">
                        <h4 className="text-sm font-bold text-purple-300">{activePhase.title}</h4>
                        <span className="text-[10px] text-gray-500">Owner: {activePhase.owner}</span>
                      </div>
                      <div className="space-y-1">
                        {activePhase.items.map((item, i) => {
                          const checked = !!selected.checklist?.[activePhase.key]?.[i];
                          return (
                            <label key={i} className={`flex items-center gap-3 py-1.5 border-b border-gray-700/50 last:border-b-0 text-sm cursor-pointer ${checked ? 'text-gray-500 line-through' : 'text-gray-200'}`}>
                              <input
                                type="checkbox"
                                checked={checked}
                                onChange={(e) => toggleChecklist(activePhase.key, i, e.target.checked)}
                                className="w-4 h-4 accent-purple-500"
                              />
                              {item}
                            </label>
                          );
                        })}
                      </div>

                      {/* 30-Day Check-In Agenda — nested under the employee day30 phase, SOP Section 8 */}
                      {activePhase.key === 'day30' && config?.agendas?.day30 && (
                        <div className="mt-4 pt-4 border-t border-gray-700/50">
                          <h4 className="text-sm font-bold text-purple-300 mb-2">30-Day Check-In Agenda</h4>
                          <div className="space-y-1 mb-3">
                            {config.agendas.day30.map((item, i) => {
                              const checked = !!selected.agenda?.day30?.items?.[i];
                              return (
                                <label key={i} className={`flex items-center gap-3 py-1 text-sm cursor-pointer ${checked ? 'text-gray-500 line-through' : 'text-gray-300'}`}>
                                  <input type="checkbox" checked={checked} onChange={(e) => updateAgenda('day30', i, e.target.checked)} className="w-4 h-4 accent-purple-500" />
                                  {item}
                                </label>
                              );
                            })}
                          </div>
                          <textarea
                            defaultValue={selected.agenda?.day30?.notes || ''}
                            onBlur={(e) => updateAgendaNotes('day30', e.target.value)}
                            placeholder="Check-in notes…"
                            className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm text-white"
                            rows={2}
                          />
                        </div>
                      )}
                    </div>
                  )}
                </NexusPanel>
                </>
              )}

              {detailInnerTab === 'compliance' && (
                <>
                <p className="text-xs text-gray-500 mb-4">
                  This tab is the audit trail — CMS FDR training cadence, exclusion screening, worker classification, and
                  the append-only action log. Pulled in full for any CMS/MCO compliance request.
                </p>

                {/* Worker classification documentation — contractor track only */}
                {selected.workerType === 'contractor' && selected.classification && (
                  <NexusPanel title="Worker Classification — Documentation, Not Legal Advice" className="mb-4">
                    <p className="text-xs text-gray-500 mb-3">
                      Contemporaneous record of why this relationship supports independent-contractor status.
                      A written label alone does not settle classification if practices look like employment.
                    </p>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 mb-3">
                      {([
                        ['boundedScope', 'Specific, bounded scope of work (not open-ended duties)'],
                        ['ownToolsSchedule', 'Contractor sets own schedule / uses own tools where applicable'],
                        ['worksOtherClients', 'Contractor works for other clients'],
                        ['noSupervisoryIntegration', 'No integration into DDI\'s internal supervisory structure'],
                        ['deliverableBasedPay', 'Deliverable/milestone-based pay (not hourly wage mirroring payroll)'],
                      ] as [keyof Classification, string][]).map(([field, label]) => (
                        <label key={field} className="flex items-center gap-2 text-sm text-gray-300 cursor-pointer">
                          <input
                            type="checkbox"
                            checked={!!selected.classification?.[field]}
                            onChange={(e) => updateClassification(field, e.target.checked)}
                            className="w-4 h-4 accent-purple-500"
                          />
                          {label}
                        </label>
                      ))}
                    </div>
                    <textarea
                      defaultValue={selected.classification?.notes || ''}
                      onBlur={(e) => updateClassification('notes', e.target.value)}
                      placeholder="Classification notes / basis…"
                      className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm text-white mb-3"
                      rows={2}
                    />
                    <label className="flex items-center gap-2 text-sm cursor-pointer">
                      <input
                        type="checkbox"
                        checked={!!selected.classification?.routedToCounsel}
                        onChange={(e) => updateClassification('routedToCounsel', e.target.checked)}
                        className="w-4 h-4 accent-red-500"
                      />
                      <span className={selected.classification?.routedToCounsel ? 'text-red-300' : 'text-gray-300'}>
                        Classification unclear — routed to legal counsel {selected.classification?.routedDate ? `(${selected.classification.routedDate})` : ''}
                      </span>
                    </label>
                  </NexusPanel>
                )}

                <NexusPanel title="Required Training — DDI internal target: 30 days. CMS hard floor: General Compliance/FWA + Medicare Fraud & Abuse within 90 days of hire, annual thereafter." className="mb-4">
                  <div className="overflow-x-auto">
                    <table className="w-full text-xs">
                      <thead>
                        <tr className="text-purple-400 uppercase text-[10px] tracking-wide text-left border-b border-gray-700">
                          <th className="py-2 pr-2">Training</th>
                          {selected.workerType === 'contractor' && <th className="py-2 pr-2">Applicable?</th>}
                          <th className="py-2 pr-2">Status</th>
                          <th className="py-2 pr-2">Cert/Ref</th>
                          <th className="py-2 pr-2">Completed By</th>
                          <th className="py-2 pr-2">Completed</th>
                          <th className="py-2 pr-2">Compliance</th>
                        </tr>
                      </thead>
                      <tbody>
                        {(config?.trainings || []).map((t, i) => {
                          const tr = selected.training[i] || ({} as TrainingRow);
                          const comp = selected._trainingCompliance?.[i];
                          const isNA = comp?.state === 'not_applicable';
                          return (
                            <tr key={i} className={`border-b border-gray-800 ${isNA ? 'opacity-40' : ''}`}>
                              <td className="py-2 pr-2 text-gray-200">
                                {t.name}
                                <div className="text-[9px] text-gray-500 mt-0.5">{t.source} · {t.recurrence_label}</div>
                                {selected.workerType === 'contractor' && (
                                  <div className="text-[9px] text-gray-600 mt-0.5">Trigger: {t.contractor_trigger}</div>
                                )}
                              </td>
                              {selected.workerType === 'contractor' && (
                                <td className="py-2 pr-2">
                                  {t.employee_only ? (
                                    <span className="text-[10px] text-gray-500">N/A</span>
                                  ) : (
                                    <select value={tr.applicable || 'pending'} onChange={(e) => updateTraining(i, 'applicable', e.target.value)} className="bg-gray-800 border border-gray-700 rounded px-2 py-1 text-xs text-white">
                                      <option value="pending">Pending</option>
                                      <option value="yes">Yes</option>
                                      <option value="no">No</option>
                                    </select>
                                  )}
                                </td>
                              )}
                              <td className="py-2 pr-2">
                                <select disabled={isNA} value={tr.status || 'Not Started'} onChange={(e) => updateTraining(i, 'status', e.target.value)} className="bg-gray-800 border border-gray-700 rounded px-2 py-1 text-xs text-white disabled:opacity-40">
                                  <option>Not Started</option>
                                  <option>In Progress</option>
                                  <option>Complete</option>
                                </select>
                              </td>
                              <td className="py-2 pr-2">
                                <input disabled={isNA} type="text" value={tr.certRef || ''} onChange={(e) => updateTraining(i, 'certRef', e.target.value)} placeholder="Cert #" className="w-20 bg-gray-800 border border-gray-700 rounded px-2 py-1 text-xs text-white disabled:opacity-40" />
                              </td>
                              <td className="py-2 pr-2">
                                <input disabled={isNA} type="text" value={tr.completedBy || ''} onChange={(e) => updateTraining(i, 'completedBy', e.target.value)} placeholder="Initials" className="w-16 bg-gray-800 border border-gray-700 rounded px-2 py-1 text-xs text-white disabled:opacity-40" />
                              </td>
                              <td className="py-2 pr-2 text-gray-500">{tr.completedDate || '—'}</td>
                              <td className="py-2 pr-2">
                                {comp && (
                                  <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded whitespace-nowrap ${SEVERITY_STYLE[comp.severity]}`}>
                                    {STATE_LABEL[comp.state] || comp.state}
                                  </span>
                                )}
                                {comp?.nextDue && <div className="text-[9px] text-gray-500 mt-0.5">Next: {comp.nextDue}</div>}
                              </td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>
                </NexusPanel>

                <NexusPanel title="Exclusion Screening Log — OIG LEIE + GSA SAM.gov (at hire, then monthly for the life of employment/engagement)" className="mb-4">
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mb-3">
                    <input type="date" value={scrDate} onChange={(e) => setScrDate(e.target.value)} className="bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm text-white" />
                    <select value={scrResult} onChange={(e) => setScrResult(e.target.value)} className="bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm text-white">
                      <option>Clear</option>
                      <option>Flagged — escalated to Compliance</option>
                      <option>Resolved — see notes</option>
                    </select>
                    <input type="text" value={scrNotes} onChange={(e) => setScrNotes(e.target.value)} placeholder="Notes (optional)" className="bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm text-white" />
                  </div>
                  <button type="button" onClick={submitScreening} className={NEXUS_BTN_PRIMARY}>Log Screening Entry</button>
                  <p className="text-[10px] text-gray-500 mt-2">Append-only — corrections/resolutions are logged as new entries, never overwrites.</p>

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
                            const resolved = e.result?.startsWith('Resolved');
                            return (
                              <tr key={i} className="border-b border-gray-800">
                                <td className="py-2 pr-2 text-gray-200">{e.date}</td>
                                <td className={`py-2 pr-2 ${flagged ? 'text-red-400' : resolved ? 'text-blue-400' : 'text-emerald-400'}`}>{e.result}</td>
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
          </>
        )}
      </div>
    </div>
  );
};

export default HRSystem;
