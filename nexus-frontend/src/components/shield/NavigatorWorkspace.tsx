import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { api } from '../../api/client';

/**
 * SHIELD Navigator Workspace
 *
 * This is what the CWC navigator sees daily — their caseload, family details,
 * phone panel (Twilio click-to-call + softphone), task queue, call log, and
 * AI co-pilot. Completely separate from the admin Command Center.
 *
 * Brand: CWC sunflower yellow + cobalt blue. Left sidebar. Mobile-friendly.
 */

// ─── Palette ────────────────────────────────────────────────────────────────
const BG       = 'bg-[#050f2e]';
const SURFACE  = 'bg-[#081849]';
const CARD     = 'bg-[#0a1a52]/40';
const BORDER   = 'border-[#1c2f6a]';
const MUTED    = 'text-[#8ea2d6]';
const YELLOW   = '#f5c23e';
const COBALT   = '#1f3fae';

const SERVICE_COLOR: Record<string, string> = {
  'Blood Lead Level (BLL) Testing':             '#026666',
  'Lead Screening':                             '#026666',
  'CLPPP Case Management':                      '#17415f',
  'CLPPP Follow-up':                            '#17415f',
  'NEMT — Non-Emergency Medical Transportation': '#CA4D22',
  'NEMT':                                       '#CA4D22',
  'Lead Remediation Coordination':               '#862074',
  'Lead Remediation':                            '#862074',
  'Housing Navigation':                          '#093C44',
  'Housing':                                     '#093C44',
  'MIBridges Benefits Navigation':               '#76BAB2',
  'Food Navigation':                             '#76BAB2',
  'Filter Safety Net / Drinking Water':          '#046791',
  'Filter Safety Net':                           '#046791',
  'Community Health Worker Home Visit':           '#2F8D98',
  'Nurse Home Visit':                            '#6A1B9A',
  'Drug Testing':                                '#BF360C',
  'DNA / Paternity Testing':                     '#1565C0',
  'Specimen Transport':                          '#4E342E',
};
const svcColor = (s: string) => SERVICE_COLOR[s] || '#3B82F6';

const SERVICE_EMOJI: Record<string, string> = {
  'Blood Lead Level (BLL) Testing': '🩸', 'Lead Screening': '🩸',
  'CLPPP Case Management': '📋', 'CLPPP Follow-up': '📋',
  'NEMT — Non-Emergency Medical Transportation': '🚕', 'NEMT': '🚕',
  'Lead Remediation Coordination': '🛠️', 'Lead Remediation': '🛠️',
  'Housing Navigation': '🏩', 'Housing': '🏩',
  'MIBridges Benefits Navigation': '🤝', 'Food Navigation': '🤝',
  'Filter Safety Net / Drinking Water': '💧', 'Filter Safety Net': '💧',
  'Community Health Worker Home Visit': '💛',
  'Nurse Home Visit': '🩺', 'Drug Testing': '🧪',
  'DNA / Paternity Testing': '🧬', 'Specimen Transport': '📦',
};

// ─── Types ──────────────────────────────────────────────────────────────────
interface NavigatorWorkspaceProps {
  navigator: { email: string; name: string; role: string; id?: string };
  onLogout: () => void;
}

type Referral = {
  id: string;
  referral_id?: string;
  date_received?: string;
  county?: string;
  urgency?: string;
  status?: string;
  services_requested?: string[];
  notes?: string;
  sla?: any;
  navigator_id?: string;
};

type CallLogEntry = {
  id: string;
  referral_id: string;
  family_name?: string;
  phone: string;
  direction: 'outbound' | 'inbound';
  duration_sec: number;
  started_at: string;
  notes: string;
  transcript?: string;
  recording_url?: string;
  status: 'completed' | 'no-answer' | 'busy' | 'failed';
};

type TaskItem = {
  id: string;
  referral_id: string;
  family_name: string;
  label: string;
  due: string;
  urgency: 'overdue' | 'today' | 'upcoming';
  type: 'follow-up' | 'appointment' | 'document' | 'outreach';
};

type Appointment = {
  id: string;
  referral_id: string;
  family_name: string;
  service_line: string;
  date: string;
  time: string;
  address?: string;
  vendor?: string;
  notes?: string;
  type: 'home-visit' | 'office' | 'telehealth' | 'transport';
};

// ─── Sidebar Sections ───────────────────────────────────────────────────────
const NAV_SECTIONS = [
  { id: 'caseload',   label: 'My Caseload',  glyph: '📂', sub: 'Active families'      },
  { id: 'calendar',   label: 'Calendar',      glyph: '📅', sub: 'Appointments & visits' },
  { id: 'tasks',      label: 'Tasks',         glyph: '✅', sub: 'Follow-ups due'       },
  { id: 'phone',      label: 'Phone',         glyph: '📞', sub: 'Call & log'            },
  { id: 'sms',        label: 'Messages',      glyph: '💬', sub: 'Text families'         },
  { id: 'docs',       label: 'Documents',     glyph: '📎', sub: 'Upload & attach'       },
  { id: 'time',       label: 'Activity Log',   glyph: '⏱️', sub: 'Track your time'        },
  { id: 'calls',      label: 'Call History',  glyph: '📝', sub: 'Transcripts & notes'   },
  { id: 'resources',  label: 'Resources',     glyph: '📖', sub: 'Directory & links'     },
  { id: 'ai',         label: 'AI Co-Pilot',   glyph: '🤖', sub: 'Prep · Suggest · Doc'  },
];

// ─── Helpers ────────────────────────────────────────────────────────────────
function timeAgo(iso?: string): string {
  if (!iso) return '—';
  const diff = Date.now() - new Date(iso).getTime();
  const hrs = Math.floor(diff / 3600000);
  if (hrs < 1) return 'just now';
  if (hrs < 24) return `${hrs}h ago`;
  return `${Math.floor(hrs / 24)}d ago`;
}

function urgencyDot(u?: string) {
  const colors: Record<string, string> = {
    'Critical': '#EF4444', 'Urgent': '#F59E0B', 'Standard': '#3B82F6', 'Low': '#6B7280',
  };
  return colors[u || ''] || '#6B7280';
}

function slaPercent(sla: any): number {
  if (!sla) return 0;
  return typeof sla.percent === 'number' ? Math.min(sla.percent, 100) : 0;
}

function slaBarColor(sla: any): string {
  if (!sla) return '#3B82F6';
  if (sla.breached) return '#EF4444';
  if (sla.warning) return '#F59E0B';
  return '#10B981';
}

function formatDuration(sec: number): string {
  const m = Math.floor(sec / 60);
  const s = sec % 60;
  return `${m}:${s.toString().padStart(2, '0')}`;
}

// ═══════════════════════════════════════════════════════════════════════════
// MAIN COMPONENT
// ═══════════════════════════════════════════════════════════════════════════
const STATUS_OPTIONS = [
  { id: 'online',    label: 'Online',       dot: 'bg-emerald-400', desc: 'Available for calls & tasks'   },
  { id: 'in-field',  label: 'In the Field', dot: 'bg-blue-400',    desc: 'Home visit — limited access'   },
  { id: 'break',     label: 'On Break',     dot: 'bg-amber-400',   desc: 'Temporarily away'              },
  { id: 'off-duty',  label: 'Off Duty',     dot: 'bg-slate-500',   desc: 'Shift ended'                   },
];

const NavigatorWorkspace: React.FC<NavigatorWorkspaceProps> = ({ navigator, onLogout }) => {
  const [section, setSection] = useState('caseload');
  const [referrals, setReferrals] = useState<Referral[]>([]);
  const [selectedRef, setSelectedRef] = useState<any>(null);
  const [callLog, setCallLog] = useState<CallLogEntry[]>([]);
  const [tasks, setTasks] = useState<TaskItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [navStatus, setNavStatus] = useState('online');
  const [showStatusMenu, setShowStatusMenu] = useState(false);
  const currentStatus = STATUS_OPTIONS.find(s => s.id === navStatus) || STATUS_OPTIONS[0];

  // ─── Data fetching ──────────────────────────────────────────────────────
  const fetchCaseload = useCallback(async () => {
    setLoading(true);
    try {
      const data = await api.getShieldReferrals();
      const all = (data?.referrals || []) as Referral[];
      setReferrals(all);
    } catch { /* silent */ }
    finally { setLoading(false); }
  }, []);

  const fetchCaseDetail = useCallback(async (refId: string) => {
    setLoading(true);
    try {
      const data = await api.getShieldReferral(refId);
      setSelectedRef(data);
    } catch { /* silent */ }
    finally { setLoading(false); }
  }, []);

  const fetchCallLog = useCallback(async () => {
    try {
      const data = await api.getShieldCallLog?.();
      setCallLog((data?.calls || []) as CallLogEntry[]);
    } catch { /* silent — endpoint may not exist yet */ }
  }, []);

  useEffect(() => { fetchCaseload(); }, [fetchCaseload]);

  // Derive tasks from referrals
  const derivedTasks = useMemo<TaskItem[]>(() => {
    const now = Date.now();
    const items: TaskItem[] = [];
    referrals.forEach(r => {
      const sla = r.sla;
      if (sla?.breached) {
        items.push({
          id: `sla-${r.id}`, referral_id: r.referral_id || r.id,
          family_name: r.referral_id || r.id.slice(-6),
          label: `SLA BREACHED — first contact overdue (${Math.abs(Math.round(sla.remaining_hours || 0))}h over)`,
          due: sla.deadline_iso || '', urgency: 'overdue', type: 'outreach',
        });
      } else if (sla?.warning) {
        items.push({
          id: `sla-warn-${r.id}`, referral_id: r.referral_id || r.id,
          family_name: r.referral_id || r.id.slice(-6),
          label: `SLA warning — ${Math.round(sla.remaining_hours || 0)}h remaining for first contact`,
          due: sla.deadline_iso || '', urgency: 'today', type: 'outreach',
        });
      }
      if (r.status === 'Intake' || r.status === 'New') {
        items.push({
          id: `intake-${r.id}`, referral_id: r.referral_id || r.id,
          family_name: r.referral_id || r.id.slice(-6),
          label: 'New referral — make first contact',
          due: r.date_received || '', urgency: 'today', type: 'outreach',
        });
      }
    });
    items.sort((a, b) => {
      const order = { overdue: 0, today: 1, upcoming: 2 };
      return (order[a.urgency] ?? 2) - (order[b.urgency] ?? 2);
    });
    return items;
  }, [referrals]);

  const allTasks = [...derivedTasks, ...tasks];

  // ─── Render ─────────────────────────────────────────────────────────────
  return (
    <div className={`flex min-h-screen ${BG} text-slate-100`}>
      {/* ══════ LEFT SIDEBAR ══════ */}
      <aside className={`w-64 ${SURFACE} border-r ${BORDER} flex flex-col sticky top-0 h-screen`}>
        {/* Navigator identity */}
        <div className={`px-5 py-5 border-b ${BORDER}`}>
          <div className="flex items-center gap-3">
            <div className="w-11 h-11 rounded-full bg-gradient-to-br from-[#f5c23e] to-[#e0a92e] border-2 border-[#fcd75a] flex items-center justify-center text-[#1f3fae] font-black text-lg">
              {navigator.name.charAt(0).toUpperCase()}
            </div>
            <div className="flex-1 min-w-0">
              <div className="text-sm font-bold text-white truncate">{navigator.name}</div>
              <div className="text-[10px] text-[#8ea2d6] truncate">{navigator.email}</div>
              <div className="relative">
                <button
                  onClick={() => setShowStatusMenu(v => !v)}
                  className="flex items-center gap-1.5 mt-0.5 hover:opacity-80 transition"
                >
                  <span className={`w-2 h-2 rounded-full ${currentStatus.dot} ${navStatus === 'online' ? 'animate-pulse' : ''}`} />
                  <span className="text-[10px] font-bold" style={{ color: navStatus === 'online' ? '#34D399' : navStatus === 'in-field' ? '#60A5FA' : navStatus === 'break' ? '#FBBF24' : '#94A3B8' }}>
                    {currentStatus.label}
                  </span>
                  <span className="text-[10px] text-[#6b7ba6]">▾</span>
                </button>
                {showStatusMenu && (
                  <div className={`absolute left-0 top-6 z-50 w-48 ${SURFACE} border ${BORDER} rounded-lg shadow-xl overflow-hidden`}>
                    {STATUS_OPTIONS.map(opt => (
                      <button
                        key={opt.id}
                        onClick={() => { setNavStatus(opt.id); setShowStatusMenu(false); }}
                        className={`w-full text-left px-3 py-2 flex items-center gap-2 hover:bg-[#0f2468]/60 transition ${navStatus === opt.id ? 'bg-[#0f2468]/40' : ''}`}
                      >
                        <span className={`w-2.5 h-2.5 rounded-full ${opt.dot}`} />
                        <span className="flex-1">
                          <span className="text-xs font-bold text-white block">{opt.label}</span>
                          <span className="text-[9px] text-[#8ea2d6] block">{opt.desc}</span>
                        </span>
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
          <div className="mt-3 flex items-center gap-2">
            <span className="text-[10px] font-black text-[#f5c23e] tracking-wider uppercase">🛡️ SHIELD Navigator</span>
          </div>
          <div className="text-[9px] text-[#f5c23e]/50 italic mt-0.5">Care. Navigate. Transform.</div>
        </div>

        {/* Section nav */}
        <nav className="flex-1 px-2 py-3 overflow-y-auto">
          {NAV_SECTIONS.map(s => {
            const active = section === s.id;
            return (
              <button
                key={s.id}
                onClick={() => { setSection(s.id); if (s.id !== 'caseload') setSelectedRef(null); }}
                className={`w-full group flex items-center gap-3 px-3 py-2.5 rounded-lg mb-0.5 transition text-left relative ${
                  active ? `border ${BORDER} bg-[#0f2468]/60` : `border border-transparent hover:bg-[#0f2468]/40`
                }`}
              >
                {active && <span className="absolute left-0 top-2 bottom-2 w-[3px] rounded-r bg-[#f5c23e]" />}
                <span className="w-8 h-8 rounded-md flex items-center justify-center text-base shrink-0">
                  {s.glyph}
                </span>
                <span className="flex-1 min-w-0">
                  <span className={`block text-sm font-bold ${active ? 'text-white' : 'text-slate-200'}`}>{s.label}</span>
                  <span className={`block text-[10px] ${active ? 'text-[#f5c23e]' : MUTED}`}>{s.sub}</span>
                </span>
                {s.id === 'tasks' && allTasks.length > 0 && (
                  <span className="bg-red-500 text-white text-[10px] font-black rounded-full w-5 h-5 flex items-center justify-center">
                    {allTasks.length}
                  </span>
                )}
              </button>
            );
          })}
        </nav>

        {/* Quick stats footer */}
        <div className={`px-4 py-4 border-t ${BORDER}`}>
          <div className="grid grid-cols-2 gap-2 text-center">
            <div className={`${CARD} border ${BORDER} rounded-lg py-2`}>
              <div className="text-lg font-black text-white">{referrals.length}</div>
              <div className="text-[9px] text-[#8ea2d6] uppercase tracking-wider">Cases</div>
            </div>
            <div className={`${CARD} border ${BORDER} rounded-lg py-2`}>
              <div className="text-lg font-black text-red-400">{allTasks.filter(t => t.urgency === 'overdue').length}</div>
              <div className="text-[9px] text-[#8ea2d6] uppercase tracking-wider">Overdue</div>
            </div>
          </div>
          <button onClick={onLogout} className="w-full mt-3 text-[10px] text-[#8ea2d6] hover:text-red-400 transition text-center">
            Sign out
          </button>
        </div>
      </aside>

      {/* ══════ MAIN CONTENT ══════ */}
      <main className="flex-1 overflow-y-auto">
        {/* Top bar */}
        <header className={`sticky top-0 z-30 ${SURFACE} border-b ${BORDER} px-6 py-3 flex items-center justify-between`}>
          <div>
            <h1 className="text-lg font-black text-white">
              {NAV_SECTIONS.find(s => s.id === section)?.label || 'SHIELD'}
            </h1>
            <div className={`text-[10px] ${MUTED}`}>
              {NAV_SECTIONS.find(s => s.id === section)?.sub}
            </div>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={fetchCaseload}
              className="text-xs text-[#8ea2d6] hover:text-[#f5c23e] transition"
            >↻ Refresh</button>
            {loading && <div className="w-4 h-4 border-2 border-[#f5c23e] border-t-transparent rounded-full animate-spin" />}
          </div>
        </header>

        <div className="p-6">
          {section === 'caseload' && !selectedRef && (
            <CaseloadView
              referrals={referrals}
              onSelect={(r) => { fetchCaseDetail(r.id); setSelectedRef(r); }}
            />
          )}
          {section === 'caseload' && selectedRef && (
            <FamilyDetailView
              caseData={selectedRef}
              onBack={() => setSelectedRef(null)}
              onCall={(phone, refId, familyName) => {
                setSection('phone');
                setSelectedRef(null);
              }}
              navigatorName={navigator.name}
            />
          )}
          {section === 'tasks' && (
            <TasksView
              tasks={allTasks}
              onGoToCase={(refId) => { fetchCaseDetail(refId); setSection('caseload'); }}
            />
          )}
          {section === 'phone' && (
            <PhonePanel
              referrals={referrals}
              navigatorName={navigator.name}
              onCallLogged={() => { fetchCallLog(); fetchCaseload(); }}
            />
          )}
          {section === 'calendar' && (
            <CalendarView referrals={referrals} />
          )}
          {section === 'sms' && (
            <SMSPanel referrals={referrals} navigatorName={navigator.name} />
          )}
          {section === 'docs' && (
            <DocumentsPanel referrals={referrals} />
          )}
          {section === 'time' && (
            <TimeLogPanel referrals={referrals} navigatorName={navigator.name} />
          )}
          {section === 'calls' && (
            <CallHistoryView calls={callLog} onRefresh={fetchCallLog} />
          )}
          {section === 'resources' && (
            <ResourceDirectory />
          )}
          {section === 'ai' && (
            <AICoPilot
              referrals={referrals}
              selectedCase={selectedRef}
              navigatorName={navigator.name}
            />
          )}
        </div>
      </main>
    </div>
  );
};

// ═══════════════════════════════════════════════════════════════════════════
// CASELOAD VIEW — all assigned families
// ═══════════════════════════════════════════════════════════════════════════
const CaseloadView: React.FC<{
  referrals: Referral[];
  onSelect: (r: Referral) => void;
}> = ({ referrals, onSelect }) => {
  const [search, setSearch] = useState('');
  const [filterUrgency, setFilterUrgency] = useState('');

  const filtered = useMemo(() => {
    let list = [...referrals];
    if (search) {
      const q = search.toLowerCase();
      list = list.filter(r =>
        (r.referral_id || '').toLowerCase().includes(q) ||
        (r.county || '').toLowerCase().includes(q) ||
        (r.notes || '').toLowerCase().includes(q)
      );
    }
    if (filterUrgency) list = list.filter(r => r.urgency === filterUrgency);
    return list;
  }, [referrals, search, filterUrgency]);

  return (
    <div className="space-y-4">
      {/* Search + filter bar */}
      <div className="flex flex-wrap gap-3">
        <input
          value={search}
          onChange={e => setSearch(e.target.value)}
          placeholder="Search cases..."
          className={`flex-1 min-w-[200px] bg-[#050f2e] border ${BORDER} rounded-lg px-4 py-2.5 text-sm text-white placeholder:text-[#6b7ba6] focus:border-[#f5c23e] focus:outline-none`}
        />
        <select
          value={filterUrgency}
          onChange={e => setFilterUrgency(e.target.value)}
          className={`bg-[#050f2e] border ${BORDER} rounded-lg px-3 py-2.5 text-sm text-white focus:border-[#f5c23e] focus:outline-none`}
        >
          <option value="">All urgencies</option>
          <option value="Critical">🔴 Critical</option>
          <option value="Urgent">🟡 Urgent</option>
          <option value="Standard">🔵 Standard</option>
          <option value="Low">⚪ Low</option>
        </select>
      </div>

      {/* Caseload stat strip */}
      <div className="grid grid-cols-4 gap-3">
        {[
          { label: 'Total', value: referrals.length, color: YELLOW },
          { label: 'Critical', value: referrals.filter(r => r.urgency === 'Critical').length, color: '#EF4444' },
          { label: 'Urgent', value: referrals.filter(r => r.urgency === 'Urgent').length, color: '#F59E0B' },
          { label: 'SLA Breach', value: referrals.filter(r => r.sla?.breached).length, color: '#EF4444' },
        ].map(s => (
          <div key={s.label} className={`${CARD} border ${BORDER} rounded-xl px-4 py-3 text-center`}>
            <div className="text-2xl font-black" style={{ color: s.color }}>{s.value}</div>
            <div className={`text-[10px] uppercase tracking-wider ${MUTED}`}>{s.label}</div>
          </div>
        ))}
      </div>

      {/* Case cards */}
      <div className="space-y-2">
        {filtered.length === 0 && (
          <div className={`text-center py-12 ${MUTED}`}>
            {search || filterUrgency ? 'No cases match your filters.' : 'No cases assigned yet.'}
          </div>
        )}
        {filtered.map(r => (
          <button
            key={r.id}
            onClick={() => onSelect(r)}
            className={`w-full text-left ${CARD} border ${BORDER} rounded-xl px-5 py-4 hover:bg-[#0f2468]/70 hover:border-[#f5c23e]/40 transition group`}
          >
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: urgencyDot(r.urgency) }} />
                <span className="text-sm font-black text-white font-mono tracking-wider">
                  {r.referral_id || r.id.slice(-8)}
                </span>
                <span className={`text-xs ${MUTED}`}>{r.county || 'No county'}</span>
              </div>
              <span className="text-[10px] text-[#8ea2d6]">{timeAgo(r.date_received)}</span>
            </div>

            {/* SLA bar */}
            {r.sla && (
              <div className="mb-2">
                <div className="flex justify-between text-[10px] mb-0.5">
                  <span className={MUTED}>SLA</span>
                  <span style={{ color: slaBarColor(r.sla) }}>
                    {r.sla.breached ? 'BREACHED' : r.sla.warning ? `${Math.round(r.sla.remaining_hours || 0)}h left` : `${Math.round(r.sla.remaining_hours || 0)}h left`}
                  </span>
                </div>
                <div className="h-1.5 bg-[#0a1a52] rounded-full overflow-hidden">
                  <div
                    className="h-full rounded-full transition-all"
                    style={{ width: `${slaPercent(r.sla)}%`, backgroundColor: slaBarColor(r.sla) }}
                  />
                </div>
              </div>
            )}

            {/* Services */}
            {r.services_requested && r.services_requested.length > 0 && (
              <div className="flex flex-wrap gap-1.5">
                {r.services_requested.map(s => (
                  <span
                    key={s}
                    className="text-[10px] font-bold px-2 py-0.5 rounded-full border"
                    style={{ borderColor: svcColor(s), color: svcColor(s), backgroundColor: `${svcColor(s)}15` }}
                  >
                    {SERVICE_EMOJI[s] || '📌'} {s.length > 25 ? s.slice(0, 22) + '…' : s}
                  </span>
                ))}
              </div>
            )}
          </button>
        ))}
      </div>
    </div>
  );
};

// ═══════════════════════════════════════════════════════════════════════════
// FAMILY DETAIL VIEW — single case deep-dive
// ═══════════════════════════════════════════════════════════════════════════
const SHIELD_SERVICE_LINES = [
  'Blood Lead Level (BLL) Testing',
  'CLPPP Case Management',
  'NEMT — Non-Emergency Medical Transportation',
  'Lead Remediation Coordination',
  'Housing Navigation',
  'MIBridges Benefits Navigation',
  'Filter Safety Net / Drinking Water',
  'Community Health Worker Home Visit',
  'Nurse Home Visit',
];

const FamilyDetailView: React.FC<{
  caseData: any;
  onBack: () => void;
  onCall: (phone: string, refId: string, familyName: string) => void;
  navigatorName: string;
}> = ({ caseData, onBack, onCall, navigatorName }) => {
  const referral = caseData?.referral || {};
  const family = caseData?.family || {};
  const children = caseData?.children || [];
  const activations = caseData?.activations || [];
  const milestones = caseData?.milestones || [];
  const [showAddService, setShowAddService] = useState(false);
  const [requestedServices, setRequestedServices] = useState<Array<{ name: string; requestedAt: string }>>([]);

  const allServiceNames = [
    ...activations.map((a: any) => a.service_line),
    ...requestedServices.map(s => s.name),
  ];
  const availableToAdd = SHIELD_SERVICE_LINES.filter(s => !allServiceNames.includes(s));

  const familyPhone = family.phone_primary || family.phone || '';
  const familyName = family.family_name || 'Family';

  return (
    <div className="space-y-5">
      {/* Back + header */}
      <div className="flex items-center gap-3">
        <button onClick={onBack} className="text-[#8ea2d6] hover:text-[#f5c23e] transition text-sm">← Back</button>
        <div className="flex-1">
          <h2 className="text-xl font-black text-white">{familyName} Family</h2>
          <div className={`text-xs ${MUTED}`}>
            Case #{referral.referral_id || referral.id?.slice(-6)} · {referral.county || 'No county'} · {referral.urgency || 'Standard'}
          </div>
        </div>
        {familyPhone && (
          <button
            onClick={() => onCall(familyPhone, referral.id, familyName)}
            className="flex items-center gap-2 bg-emerald-500 hover:bg-emerald-400 text-white px-4 py-2.5 rounded-lg text-sm font-bold transition"
          >
            📞 Call {familyName}
          </button>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        {/* Left column — family info + children */}
        <div className="lg:col-span-2 space-y-4">
          {/* Family info card */}
          <div className={`${CARD} border ${BORDER} rounded-xl overflow-hidden`}>
            <div className="px-5 py-3 border-b border-[#1c2f6a] flex items-center justify-between">
              <span className="text-xs font-bold text-[#f5c23e] uppercase tracking-wider">Family Information</span>
              <span className="text-[10px] text-[#8ea2d6]">Received {timeAgo(referral.date_received)}</span>
            </div>
            <div className="px-5 py-4 grid grid-cols-2 gap-4 text-sm">
              <InfoRow label="Family Name" value={familyName} />
              <InfoRow label="Phone" value={familyPhone || '—'} />
              <InfoRow label="County" value={referral.county || '—'} />
              <InfoRow label="Referring Agency" value={referral.referring_agency || '—'} />
              <InfoRow label="Case Worker" value={referral.case_worker_name || '—'} />
              <InfoRow label="Case Worker Phone" value={referral.case_worker_phone || '—'} />
              <InfoRow label="Status" value={referral.status || '—'} />
              <InfoRow label="Urgency" value={referral.urgency || '—'} dot={urgencyDot(referral.urgency)} />
              {family.address && <InfoRow label="Address" value={family.address} span />}
              {referral.notes && <InfoRow label="Notes" value={referral.notes} span />}
            </div>
          </div>

          {/* Children */}
          {children.length > 0 && (
            <div className={`${CARD} border ${BORDER} rounded-xl overflow-hidden`}>
              <div className="px-5 py-3 border-b border-[#1c2f6a]">
                <span className="text-xs font-bold text-[#f5c23e] uppercase tracking-wider">Children</span>
              </div>
              <div className="divide-y divide-[#1c2f6a]">
                {children.map((c: any) => (
                  <div key={c.id} className="px-5 py-3 flex items-center justify-between">
                    <div>
                      <div className="text-sm font-bold text-white">{c.child_name || 'Unnamed'}</div>
                      <div className="text-[10px] text-[#8ea2d6]">
                        {c.age_months ? `${c.age_months} months` : '—'} · BLL: {c.blood_lead_level ?? '—'} µg/dL
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      {c.blood_lead_level >= 5 && (
                        <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-red-500/20 text-red-400 border border-red-500/40">
                          EBL
                        </span>
                      )}
                      <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${
                        c.lead_test_status === 'Completed' ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/40'
                        : 'bg-amber-500/20 text-amber-400 border-amber-500/40'
                      }`}>
                        {c.lead_test_status || 'Pending'}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Service activations */}
          <div className={`${CARD} border ${BORDER} rounded-xl overflow-hidden`}>
            <div className="px-5 py-3 border-b border-[#1c2f6a] flex items-center justify-between">
              <span className="text-xs font-bold text-[#f5c23e] uppercase tracking-wider">Active Services</span>
              <button
                onClick={() => setShowAddService(v => !v)}
                className="text-[10px] font-bold text-[#f5c23e] hover:text-[#fcd75a] transition"
              >
                {showAddService ? '✕ Close' : '+ Add Service'}
              </button>
            </div>

            {showAddService && (
              <div className="px-5 py-3 border-b border-[#1c2f6a] bg-[#050f2e]/60">
                <div className={`text-[10px] ${MUTED} mb-2`}>Tap a service to request it for this family. A supervisor must approve before it becomes active.</div>
                <div className="flex flex-wrap gap-1.5">
                  {availableToAdd.map(svc => {
                    const hex = svcColor(svc);
                    return (
                      <button
                        key={svc}
                        onClick={() => { setRequestedServices(prev => [...prev, { name: svc, requestedAt: new Date().toISOString() }]); }}
                        className="flex items-center gap-1 px-3 py-1.5 rounded-full border text-[10px] font-bold transition hover:scale-105"
                        style={{ borderColor: hex, color: hex, backgroundColor: `${hex}15` }}
                      >
                        {SERVICE_EMOJI[svc] || '📌'} {svc.length > 30 ? svc.slice(0, 27) + '…' : svc}
                      </button>
                    );
                  })}
                  {availableToAdd.length === 0 && (
                    <div className={`text-[10px] ${MUTED} py-2`}>All services are already requested or active for this family.</div>
                  )}
                </div>
              </div>
            )}

            {allServiceNames.length === 0 ? (
              <div className="px-5 py-6 text-center text-[#8ea2d6] text-sm">No services activated yet.</div>
            ) : (
              <div className="divide-y divide-[#1c2f6a]">
                {activations.map((a: any) => {
                  const hex = svcColor(a.service_line || '');
                  return (
                    <div key={a.id} className="px-5 py-3 flex items-center gap-3">
                      <span className="text-lg">{SERVICE_EMOJI[a.service_line] || '📌'}</span>
                      <div className="flex-1 min-w-0">
                        <div className="text-sm font-bold" style={{ color: hex }}>{a.service_line}</div>
                        <div className="text-[10px] text-[#8ea2d6]">
                          {a.vendor || 'No vendor assigned'} · {a.status || 'Active'}
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        {a.appointment_date && (
                          <div className="text-[10px] text-[#8ea2d6]">
                            📅 {new Date(a.appointment_date).toLocaleDateString()}
                          </div>
                        )}
                        <span className="text-[8px] px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 font-bold">APPROVED</span>
                      </div>
                    </div>
                  );
                })}
                {requestedServices.map(svc => {
                  const hex = svcColor(svc.name);
                  return (
                    <div key={svc.name} className="px-5 py-3 flex items-center gap-3">
                      <span className="text-lg">{SERVICE_EMOJI[svc.name] || '📌'}</span>
                      <div className="flex-1 min-w-0">
                        <div className="text-sm font-bold" style={{ color: hex }}>{svc.name}</div>
                        <div className="text-[10px] text-amber-400">
                          Requested by {navigatorName} · Awaiting supervisor approval
                        </div>
                      </div>
                      <span className="text-[8px] px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-400 border border-amber-500/30 font-bold animate-pulse">PENDING</span>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>

        {/* Right column — timeline + quick actions */}
        <div className="space-y-4">
          {/* Quick actions */}
          <div className={`${CARD} border ${BORDER} rounded-xl p-5 space-y-2`}>
            <div className="text-xs font-bold text-[#f5c23e] uppercase tracking-wider mb-3">Quick Actions</div>
            {familyPhone && (
              <button
                onClick={() => onCall(familyPhone, referral.id, familyName)}
                className="w-full flex items-center gap-2 bg-emerald-500/20 hover:bg-emerald-500/30 border border-emerald-500/40 text-emerald-400 px-4 py-2.5 rounded-lg text-sm font-bold transition"
              >
                📞 Call Family
              </button>
            )}
            <button className="w-full flex items-center gap-2 bg-blue-500/20 hover:bg-blue-500/30 border border-blue-500/40 text-blue-400 px-4 py-2.5 rounded-lg text-sm font-bold transition">
              📝 Log Note
            </button>
            <button
              onClick={() => setShowAddService(v => !v)}
              className="w-full flex items-center gap-2 bg-violet-500/20 hover:bg-violet-500/30 border border-violet-500/40 text-violet-400 px-4 py-2.5 rounded-lg text-sm font-bold transition"
            >
              ⚡ Request Service
            </button>
            <button className="w-full flex items-center gap-2 bg-amber-500/20 hover:bg-amber-500/30 border border-amber-500/40 text-amber-400 px-4 py-2.5 rounded-lg text-sm font-bold transition">
              📅 Schedule Appointment
            </button>
          </div>

          {/* Milestones timeline */}
          <div className={`${CARD} border ${BORDER} rounded-xl p-5`}>
            <div className="text-xs font-bold text-[#f5c23e] uppercase tracking-wider mb-3">Timeline</div>
            {milestones.length === 0 ? (
              <div className="text-[#8ea2d6] text-xs text-center py-4">No milestones yet.</div>
            ) : (
              <div className="space-y-3">
                {milestones.slice(0, 10).map((m: any, i: number) => (
                  <div key={i} className="flex gap-3">
                    <div className="flex flex-col items-center">
                      <div className="w-2.5 h-2.5 rounded-full bg-[#f5c23e] shrink-0 mt-1" />
                      {i < milestones.length - 1 && <div className="flex-1 w-px bg-[#1c2f6a] mt-1" />}
                    </div>
                    <div className="pb-3">
                      <div className="text-xs font-bold text-white">{m.milestone_type || m.milestone_id || 'Event'}</div>
                      <div className="text-[10px] text-[#8ea2d6]">{m.notes || ''}</div>
                      <div className="text-[10px] text-[#6b7ba6]">{timeAgo(m.date_logged)}</div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

const InfoRow: React.FC<{ label: string; value: string; dot?: string; span?: boolean }> = ({ label, value, dot, span }) => (
  <div className={span ? 'col-span-2' : ''}>
    <div className="text-[10px] text-[#8ea2d6] uppercase tracking-wider mb-0.5">{label}</div>
    <div className="text-sm text-white flex items-center gap-1.5">
      {dot && <span className="w-2 h-2 rounded-full shrink-0" style={{ backgroundColor: dot }} />}
      {value}
    </div>
  </div>
);

// ═══════════════════════════════════════════════════════════════════════════
// TASKS VIEW — prioritized follow-ups
// ═══════════════════════════════════════════════════════════════════════════
const TasksView: React.FC<{
  tasks: TaskItem[];
  onGoToCase: (refId: string) => void;
}> = ({ tasks, onGoToCase }) => {
  const grouped = useMemo(() => ({
    overdue: tasks.filter(t => t.urgency === 'overdue'),
    today: tasks.filter(t => t.urgency === 'today'),
    upcoming: tasks.filter(t => t.urgency === 'upcoming'),
  }), [tasks]);

  const sections = [
    { key: 'overdue' as const, label: '🔴 Overdue', color: '#EF4444' },
    { key: 'today' as const, label: '🟡 Today', color: '#F59E0B' },
    { key: 'upcoming' as const, label: '🔵 Upcoming', color: '#3B82F6' },
  ];

  return (
    <div className="space-y-5">
      <div className="flex items-center gap-3">
        <h2 className="text-lg font-black text-white">Task Queue</h2>
        <span className={`text-xs ${MUTED}`}>{tasks.length} item{tasks.length !== 1 ? 's' : ''}</span>
      </div>

      {tasks.length === 0 && (
        <div className={`${CARD} border ${BORDER} rounded-xl p-8 text-center`}>
          <div className="text-3xl mb-2">✅</div>
          <div className="text-sm font-bold text-white">All clear</div>
          <div className={`text-xs ${MUTED} mt-1`}>No tasks due right now. Nice work.</div>
        </div>
      )}

      {sections.map(s => grouped[s.key].length > 0 && (
        <div key={s.key}>
          <div className="flex items-center gap-2 mb-2">
            <span className="text-sm font-bold" style={{ color: s.color }}>{s.label}</span>
            <span className="text-[10px] text-[#8ea2d6]">({grouped[s.key].length})</span>
          </div>
          <div className="space-y-1.5">
            {grouped[s.key].map(t => (
              <button
                key={t.id}
                onClick={() => onGoToCase(t.referral_id)}
                className={`w-full text-left ${CARD} border ${BORDER} rounded-lg px-4 py-3 hover:bg-[#0f2468]/70 hover:border-[#f5c23e]/40 transition flex items-center gap-3`}
              >
                <span className="text-lg">{t.type === 'outreach' ? '📞' : t.type === 'appointment' ? '📅' : t.type === 'document' ? '📄' : '📌'}</span>
                <div className="flex-1 min-w-0">
                  <div className="text-sm font-bold text-white">{t.label}</div>
                  <div className="text-[10px] text-[#8ea2d6]">Case #{t.family_name}</div>
                </div>
                <span className="text-[#8ea2d6] text-sm">→</span>
              </button>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
};

// ═══════════════════════════════════════════════════════════════════════════
// PHONE PANEL — click-to-call + call logging
// ═══════════════════════════════════════════════════════════════════════════
const PhonePanel: React.FC<{
  referrals: Referral[];
  navigatorName: string;
  onCallLogged: () => void;
}> = ({ referrals, navigatorName, onCallLogged }) => {
  const [selectedRefId, setSelectedRefId] = useState('');
  const [dialNumber, setDialNumber] = useState('');
  const [callState, setCallState] = useState<'idle' | 'connecting' | 'active' | 'ended'>('idle');
  const [callTimer, setCallTimer] = useState(0);
  const [callNotes, setCallNotes] = useState('');
  const [timerInterval, setTimerInterval] = useState<any>(null);

  const selectedReferral = referrals.find(r => r.id === selectedRefId || r.referral_id === selectedRefId);

  const startCall = () => {
    if (!dialNumber.trim()) return;
    setCallState('connecting');
    setTimeout(() => {
      setCallState('active');
      setCallTimer(0);
      const interval = setInterval(() => setCallTimer(t => t + 1), 1000);
      setTimerInterval(interval);
    }, 2000);
  };

  const endCall = () => {
    setCallState('ended');
    if (timerInterval) clearInterval(timerInterval);
  };

  const saveAndReset = () => {
    onCallLogged();
    setCallState('idle');
    setCallTimer(0);
    setCallNotes('');
    setDialNumber('');
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
      {/* Dialer */}
      <div className={`${CARD} border ${BORDER} rounded-xl overflow-hidden`}>
        <div className="px-5 py-4 border-b border-[#1c2f6a]">
          <div className="text-xs font-bold text-[#f5c23e] uppercase tracking-wider">📞 Make a Call</div>
          <div className={`text-[10px] ${MUTED} mt-0.5`}>Select a case, then call. Twilio connects through your phone.</div>
        </div>
        <div className="px-5 py-5 space-y-4">
          {/* Case selector */}
          <div>
            <label className="text-[10px] text-[#8ea2d6] uppercase tracking-wider font-bold block mb-1">Link to case</label>
            <select
              value={selectedRefId}
              onChange={e => setSelectedRefId(e.target.value)}
              className={`w-full bg-[#050f2e] border ${BORDER} rounded-lg px-3 py-2.5 text-sm text-white focus:border-[#f5c23e] focus:outline-none`}
            >
              <option value="">— Select a case —</option>
              {referrals.map(r => (
                <option key={r.id} value={r.id}>
                  {r.referral_id || r.id.slice(-8)} · {r.county || 'No county'}
                </option>
              ))}
            </select>
          </div>

          {/* Phone number */}
          <div>
            <label className="text-[10px] text-[#8ea2d6] uppercase tracking-wider font-bold block mb-1">Phone number</label>
            <input
              type="tel"
              value={dialNumber}
              onChange={e => setDialNumber(e.target.value)}
              placeholder="(313) 555-0123"
              className={`w-full bg-[#050f2e] border ${BORDER} rounded-lg px-4 py-3 text-lg font-mono text-white tracking-wider placeholder:text-[#6b7ba6] focus:border-[#f5c23e] focus:outline-none`}
              disabled={callState !== 'idle'}
            />
          </div>

          {/* Call state */}
          {callState === 'idle' && (
            <button
              onClick={startCall}
              disabled={!dialNumber.trim()}
              className="w-full bg-emerald-500 hover:bg-emerald-400 disabled:opacity-40 text-white py-3.5 rounded-xl text-sm font-black transition flex items-center justify-center gap-2"
            >
              📞 Call Now
            </button>
          )}

          {callState === 'connecting' && (
            <div className="text-center py-4">
              <div className="w-12 h-12 border-4 border-[#f5c23e] border-t-transparent rounded-full animate-spin mx-auto mb-3" />
              <div className="text-sm font-bold text-[#f5c23e]">Connecting...</div>
              <div className={`text-[10px] ${MUTED}`}>Ringing your phone first, then connecting to family</div>
            </div>
          )}

          {callState === 'active' && (
            <div className="text-center space-y-4">
              <div>
                <div className="text-3xl font-mono font-black text-emerald-400">{formatDuration(callTimer)}</div>
                <div className="flex items-center justify-center gap-1.5 mt-1">
                  <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                  <span className="text-xs text-emerald-400 font-bold">Connected</span>
                </div>
                <div className={`text-xs ${MUTED} mt-1`}>{dialNumber}</div>
              </div>
              <button
                onClick={endCall}
                className="w-full bg-red-500 hover:bg-red-400 text-white py-3 rounded-xl text-sm font-black transition"
              >
                End Call
              </button>
            </div>
          )}

          {callState === 'ended' && (
            <div className="space-y-3">
              <div className="text-center">
                <div className="text-sm font-bold text-white">Call ended · {formatDuration(callTimer)}</div>
              </div>
              <div>
                <label className="text-[10px] text-[#8ea2d6] uppercase tracking-wider font-bold block mb-1">Call notes</label>
                <textarea
                  value={callNotes}
                  onChange={e => setCallNotes(e.target.value)}
                  placeholder="What was discussed? Any follow-ups needed?"
                  rows={4}
                  className={`w-full bg-[#050f2e] border ${BORDER} rounded-lg px-4 py-3 text-sm text-white placeholder:text-[#6b7ba6] focus:border-[#f5c23e] focus:outline-none resize-none`}
                />
              </div>
              <button
                onClick={saveAndReset}
                className="w-full bg-[#f5c23e] hover:bg-[#fcd75a] text-[#081849] py-3 rounded-xl text-sm font-black transition"
              >
                Save & Close
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Right side — call info + tips */}
      <div className="space-y-4">
        {/* Selected case info */}
        {selectedReferral && (
          <div className={`${CARD} border ${BORDER} rounded-xl p-5`}>
            <div className="text-xs font-bold text-[#f5c23e] uppercase tracking-wider mb-3">Case Context</div>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className={MUTED}>Case</span>
                <span className="text-white font-mono">{selectedReferral.referral_id || selectedReferral.id.slice(-8)}</span>
              </div>
              <div className="flex justify-between">
                <span className={MUTED}>County</span>
                <span className="text-white">{selectedReferral.county || '—'}</span>
              </div>
              <div className="flex justify-between">
                <span className={MUTED}>Urgency</span>
                <span className="flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full" style={{ backgroundColor: urgencyDot(selectedReferral.urgency) }} />
                  <span className="text-white">{selectedReferral.urgency || 'Standard'}</span>
                </span>
              </div>
              <div className="flex justify-between">
                <span className={MUTED}>Status</span>
                <span className="text-white">{selectedReferral.status || '—'}</span>
              </div>
              {selectedReferral.services_requested && (
                <div className="pt-2 border-t border-[#1c2f6a]">
                  <div className="text-[10px] text-[#8ea2d6] mb-1.5">Services</div>
                  <div className="flex flex-wrap gap-1">
                    {selectedReferral.services_requested.map(s => (
                      <span key={s} className="text-[10px] px-2 py-0.5 rounded-full border" style={{ borderColor: svcColor(s), color: svcColor(s) }}>
                        {SERVICE_EMOJI[s] || '📌'} {s.length > 20 ? s.slice(0, 18) + '…' : s}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Call tips */}
        <div className={`${CARD} border ${BORDER} rounded-xl p-5`}>
          <div className="text-xs font-bold text-[#f5c23e] uppercase tracking-wider mb-3">Call Tips</div>
          <div className="space-y-2 text-xs text-[#8ea2d6] leading-relaxed">
            <p>• Introduce yourself: <strong className="text-white">"Hi, I'm {navigatorName} from Cause We Care."</strong></p>
            <p>• Confirm you're speaking with the right person before sharing any info.</p>
            <p>• Ask about immediate needs first — transportation, housing, food.</p>
            <p>• If the family seems overwhelmed, slow down. You're their person.</p>
            <p>• Always end with: <strong className="text-white">"Is there anything else I can help with?"</strong></p>
          </div>
        </div>

        {/* How it works */}
        <div className={`${CARD} border ${BORDER} rounded-xl p-5`}>
          <div className="text-xs font-bold text-[#f5c23e] uppercase tracking-wider mb-3">How It Works</div>
          <div className="space-y-2 text-xs text-[#8ea2d6] leading-relaxed">
            <p><strong className="text-white">1.</strong> Select the case and enter the number</p>
            <p><strong className="text-white">2.</strong> Hit "Call Now" — your phone rings first</p>
            <p><strong className="text-white">3.</strong> When you answer, we connect you to the family</p>
            <p><strong className="text-white">4.</strong> Family sees the CWC number, not your personal number</p>
            <p><strong className="text-white">5.</strong> Call is recorded and logged to the case automatically</p>
          </div>
        </div>
      </div>
    </div>
  );
};

// ═══════════════════════════════════════════════════════════════════════════
// CALL HISTORY — transcripts + notes
// ═══════════════════════════════════════════════════════════════════════════
const CallHistoryView: React.FC<{
  calls: CallLogEntry[];
  onRefresh: () => void;
}> = ({ calls, onRefresh }) => {
  const [expandedId, setExpandedId] = useState<string | null>(null);

  useEffect(() => { onRefresh(); }, [onRefresh]);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-black text-white">Call History</h2>
        <button onClick={onRefresh} className={`text-xs ${MUTED} hover:text-[#f5c23e] transition`}>↻ Refresh</button>
      </div>

      {calls.length === 0 && (
        <div className={`${CARD} border ${BORDER} rounded-xl p-8 text-center`}>
          <div className="text-3xl mb-2">📞</div>
          <div className="text-sm font-bold text-white">No calls yet</div>
          <div className={`text-xs ${MUTED} mt-1`}>Your call history will appear here after your first call.</div>
        </div>
      )}

      <div className="space-y-2">
        {calls.map(c => (
          <div key={c.id} className={`${CARD} border ${BORDER} rounded-xl overflow-hidden`}>
            <button
              onClick={() => setExpandedId(expandedId === c.id ? null : c.id)}
              className="w-full text-left px-5 py-3.5 flex items-center gap-3 hover:bg-[#0f2468]/50 transition"
            >
              <span className={`text-lg ${c.direction === 'outbound' ? '' : 'rotate-180'}`}>📞</span>
              <div className="flex-1 min-w-0">
                <div className="text-sm font-bold text-white">
                  {c.family_name || c.phone} · Case #{c.referral_id?.slice(-6) || '—'}
                </div>
                <div className="text-[10px] text-[#8ea2d6]">
                  {new Date(c.started_at).toLocaleString()} · {formatDuration(c.duration_sec)} ·
                  <span className={c.status === 'completed' ? ' text-emerald-400' : ' text-red-400'}> {c.status}</span>
                </div>
              </div>
              {c.transcript && <span className="text-[10px] text-[#f5c23e] font-bold">📝 Transcript</span>}
              <span className={`text-[#8ea2d6] transition ${expandedId === c.id ? 'rotate-90' : ''}`}>→</span>
            </button>
            {expandedId === c.id && (
              <div className="px-5 py-4 border-t border-[#1c2f6a] space-y-3">
                {c.notes && (
                  <div>
                    <div className="text-[10px] text-[#8ea2d6] uppercase tracking-wider mb-1">Notes</div>
                    <div className="text-sm text-white whitespace-pre-wrap">{c.notes}</div>
                  </div>
                )}
                {c.transcript && (
                  <div>
                    <div className="text-[10px] text-[#f5c23e] uppercase tracking-wider mb-1">Transcript</div>
                    <div className="text-xs text-[#8ea2d6] whitespace-pre-wrap bg-[#050f2e] rounded-lg p-3 max-h-60 overflow-y-auto">
                      {c.transcript}
                    </div>
                  </div>
                )}
                {c.recording_url && (
                  <div>
                    <div className="text-[10px] text-[#8ea2d6] uppercase tracking-wider mb-1">Recording</div>
                    <audio controls className="w-full" src={c.recording_url} />
                  </div>
                )}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

// ═══════════════════════════════════════════════════════════════════════════
// AI CO-PILOT — prep, suggestions, post-call documentation
// ═══════════════════════════════════════════════════════════════════════════
const AICoPilot: React.FC<{
  referrals: Referral[];
  selectedCase: any;
  navigatorName: string;
}> = ({ referrals, selectedCase, navigatorName }) => {
  const [messages, setMessages] = useState<{ role: 'user' | 'assistant'; text: string }[]>([]);
  const [input, setInput] = useState('');
  const [busy, setBusy] = useState(false);
  const [prepCase, setPrepCase] = useState('');

  const send = async (text?: string) => {
    const msg = text || input.trim();
    if (!msg) return;
    setMessages(m => [...m, { role: 'user', text: msg }]);
    setInput('');
    setBusy(true);
    try {
      const result: any = await api.shieldAiChat(msg, { navigator: navigatorName });
      const reply = result?.reply || result?.error || 'No response.';
      setMessages(m => [...m, { role: 'assistant', text: reply }]);
    } catch (e: any) {
      setMessages(m => [...m, { role: 'assistant', text: `Error: ${e.message}` }]);
    } finally {
      setBusy(false);
    }
  };

  const prepForCall = (refId: string) => {
    const r = referrals.find(ref => ref.id === refId || ref.referral_id === refId);
    if (r) {
      send(`Prep me for a call with the family on case ${r.referral_id || r.id.slice(-6)}. County: ${r.county || 'unknown'}. Urgency: ${r.urgency || 'Standard'}. Services: ${(r.services_requested || []).join(', ') || 'none yet'}. Status: ${r.status || 'unknown'}. Give me talking points, what to ask, and any risks to watch for.`);
    }
  };

  const suggestions = [
    { label: '📋 Prep me for my next call', action: () => {
      if (referrals.length > 0) prepForCall(referrals[0].id);
      else send('What should I prioritize today?');
    }},
    { label: '🔴 Which cases need attention now?', action: () => send('Which of my cases are overdue or at risk of breaching SLA? List them with urgency.') },
    { label: '📝 Help me document a call', action: () => send('I just finished a call. Help me write a structured case note. Ask me what happened.') },
    { label: '❓ What is the CLPPP protocol for BLL over 10?', action: () => send('What is the CLPPP follow-up protocol when a child has a blood lead level above 10 µg/dL?') },
    { label: '🤝 How do I help a family apply for MIBridges?', action: () => send('Walk me through helping a family apply for benefits through MIBridges. What do they need to bring? What\'s the process?') },
    { label: '🏩 Family needs emergency housing — what do I do?', action: () => send('A family needs emergency housing because their home is being remediated for lead. What are the steps and who do I contact?') },
  ];

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
      {/* Chat */}
      <div className={`lg:col-span-2 ${CARD} border ${BORDER} rounded-xl flex flex-col`} style={{ minHeight: 560 }}>
        <div className="px-5 py-4 border-b border-[#1c2f6a] flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-[#f5c23e] to-[#e0a92e] border border-[#fcd75a] flex items-center justify-center text-lg">
            🤖
          </div>
          <div>
            <div className="font-bold text-white">AI Co-Pilot</div>
            <div className="text-[10px] text-[#8ea2d6] uppercase tracking-wider">Prep · Suggest · Document · Your backup brain</div>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto px-5 py-4 space-y-3">
          {messages.length === 0 && (
            <div className="text-center py-16">
              <div className="text-4xl mb-3">🤖</div>
              <div className="text-sm font-bold text-white">Hey {navigatorName.split(' ')[0]} — I'm your co-pilot.</div>
              <div className={`text-xs ${MUTED} mt-1 max-w-sm mx-auto`}>
                I can prep you for calls, suggest what to ask, document conversations, and answer questions about protocols, resources, and your caseload.
              </div>
            </div>
          )}
          {messages.map((m, i) => (
            <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[85%] px-4 py-3 rounded-xl text-sm whitespace-pre-wrap leading-relaxed ${
                m.role === 'user'
                  ? 'bg-[#f5c23e] text-[#081849] border border-[#fcd75a] font-medium'
                  : 'bg-[#081849] text-slate-100 border border-[#1c2f6a]'
              }`}>{m.text}</div>
            </div>
          ))}
          {busy && (
            <div className="flex gap-2 items-center text-[#8ea2d6]">
              <div className="w-4 h-4 border-2 border-[#f5c23e] border-t-transparent rounded-full animate-spin" />
              <span className="text-xs italic">Thinking...</span>
            </div>
          )}
        </div>

        <div className="px-5 py-3 border-t border-[#1c2f6a] flex gap-2">
          <input
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(); } }}
            placeholder="Ask me anything — protocols, resources, case prep..."
            className={`flex-1 bg-[#050f2e] border ${BORDER} rounded-lg px-4 py-2.5 text-sm text-white placeholder:text-[#6b7ba6] focus:border-[#f5c23e] focus:outline-none`}
            disabled={busy}
          />
          <button
            onClick={() => send()}
            disabled={busy || !input.trim()}
            className="bg-[#f5c23e] hover:bg-[#fcd75a] disabled:opacity-40 text-[#081849] px-5 py-2.5 rounded-lg text-sm font-black transition"
          >
            Send
          </button>
        </div>
      </div>

      {/* Right panel — quick prompts + case prep */}
      <div className="space-y-4">
        <div className={`${CARD} border ${BORDER} rounded-xl p-5`}>
          <div className="text-xs font-bold text-[#f5c23e] uppercase tracking-wider mb-3">Quick Prompts</div>
          <div className="space-y-1.5">
            {suggestions.map((s, i) => (
              <button
                key={i}
                onClick={s.action}
                className={`w-full text-left text-xs ${CARD} hover:bg-[#0f2468]/70 border ${BORDER} hover:border-[#f5c23e]/40 rounded-lg px-3 py-2.5 text-slate-200 transition`}
              >
                {s.label}
              </button>
            ))}
          </div>
        </div>

        {/* Case prep shortcut */}
        <div className={`${CARD} border ${BORDER} rounded-xl p-5`}>
          <div className="text-xs font-bold text-[#f5c23e] uppercase tracking-wider mb-3">🎯 Prep For a Call</div>
          <select
            value={prepCase}
            onChange={e => setPrepCase(e.target.value)}
            className={`w-full bg-[#050f2e] border ${BORDER} rounded-lg px-3 py-2.5 text-sm text-white focus:border-[#f5c23e] focus:outline-none mb-2`}
          >
            <option value="">— Select a case —</option>
            {referrals.map(r => (
              <option key={r.id} value={r.id}>
                {r.referral_id || r.id.slice(-8)} · {r.county || ''} · {r.urgency || 'Standard'}
              </option>
            ))}
          </select>
          <button
            onClick={() => { if (prepCase) prepForCall(prepCase); }}
            disabled={!prepCase}
            className="w-full bg-[#1f3fae] hover:bg-[#2a4fd0] disabled:opacity-40 text-white py-2.5 rounded-lg text-sm font-bold transition"
          >
            Prep Me
          </button>
        </div>

        <div className={`${CARD} border ${BORDER} rounded-xl p-5`}>
          <div className="text-xs font-bold text-[#f5c23e] uppercase tracking-wider mb-2">What I Can Do</div>
          <ul className="text-xs text-[#8ea2d6] space-y-1.5 leading-relaxed">
            <li><strong className="text-white">Before calls</strong> — prep talking points, flag risks</li>
            <li><strong className="text-white">During calls</strong> — answer protocol questions in real-time</li>
            <li><strong className="text-white">After calls</strong> — help write structured case notes</li>
            <li><strong className="text-white">Anytime</strong> — answer questions about MIBridges, CLPPP, NEMT, housing, lead programs</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

// ═══════════════════════════════════════════════════════════════════════════
// CALENDAR VIEW — appointments with maps + add-to-calendar
// ═══════════════════════════════════════════════════════════════════════════
function mapsUrl(address: string) {
  const ua = navigator.userAgent || '';
  if (/iPhone|iPad|iPod/i.test(ua)) return `maps://maps.apple.com/?q=${encodeURIComponent(address)}`;
  return `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(address)}`;
}

function calendarUrl(appt: { family_name: string; service_line: string; date: string; time: string; address?: string; notes?: string }) {
  const start = new Date(`${appt.date}T${appt.time || '09:00'}`);
  const end = new Date(start.getTime() + 60 * 60 * 1000);
  const fmt = (d: Date) => d.toISOString().replace(/[-:]/g, '').replace(/\.\d{3}/, '');
  const title = `${appt.service_line} — ${appt.family_name} Family`;
  const details = [appt.notes, appt.address].filter(Boolean).join('\n');
  return `https://calendar.google.com/calendar/render?action=TEMPLATE&text=${encodeURIComponent(title)}&dates=${fmt(start)}/${fmt(end)}&details=${encodeURIComponent(details)}&location=${encodeURIComponent(appt.address || '')}`;
}

const CalendarView: React.FC<{ referrals: Referral[] }> = ({ referrals }) => {
  const appointments = useMemo<Appointment[]>(() => {
    const appts: Appointment[] = [];
    referrals.forEach(r => {
      if (r.services_requested) {
        r.services_requested.forEach((svc, i) => {
          appts.push({
            id: `${r.id}-svc-${i}`,
            referral_id: r.referral_id || r.id.slice(-8),
            family_name: r.referral_id || r.id.slice(-6),
            service_line: svc,
            date: r.date_received?.split('T')[0] || new Date().toISOString().split('T')[0],
            time: '09:00',
            address: r.county ? `${r.county} County, Michigan` : undefined,
            type: svc.includes('Home Visit') ? 'home-visit' : svc.includes('NEMT') ? 'transport' : 'office',
          });
        });
      }
    });
    appts.sort((a, b) => a.date.localeCompare(b.date));
    return appts;
  }, [referrals]);

  const today = new Date().toISOString().split('T')[0];
  const upcoming = appointments.filter(a => a.date >= today);
  const past = appointments.filter(a => a.date < today);

  const renderAppt = (a: Appointment) => {
    const hex = svcColor(a.service_line);
    return (
      <div key={a.id} className={`${CARD} border ${BORDER} rounded-xl px-5 py-4 hover:bg-[#0f2468]/50 transition`}>
        <div className="flex items-start gap-3">
          <div className="rounded-xl w-12 h-12 flex flex-col items-center justify-center shrink-0" style={{ backgroundColor: `${hex}20`, color: hex }}>
            <div className="text-xs font-black leading-none">{new Date(a.date + 'T12:00').toLocaleDateString('en-US', { weekday: 'short' })}</div>
            <div className="text-lg font-black leading-none">{new Date(a.date + 'T12:00').getDate()}</div>
          </div>
          <div className="flex-1 min-w-0">
            <div className="text-sm font-bold" style={{ color: hex }}>
              {SERVICE_EMOJI[a.service_line] || '📅'} {a.service_line}
            </div>
            <div className={`text-xs ${MUTED} mt-0.5`}>
              Case #{a.referral_id} · {a.family_name} Family
            </div>
            <div className={`text-xs ${MUTED}`}>{a.time} · {a.vendor || 'No vendor assigned'}</div>
            {a.address && (
              <div className="text-xs text-white mt-1">📍 {a.address}</div>
            )}
          </div>
          <div className="flex flex-col gap-1.5 shrink-0">
            {a.address && (
              <a
                href={mapsUrl(a.address)}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-1 bg-blue-500/20 hover:bg-blue-500/30 border border-blue-500/40 text-blue-400 px-3 py-1.5 rounded-lg text-[10px] font-bold transition"
              >
                🗺️ Directions
              </a>
            )}
            <a
              href={calendarUrl(a)}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-1 bg-violet-500/20 hover:bg-violet-500/30 border border-violet-500/40 text-violet-400 px-3 py-1.5 rounded-lg text-[10px] font-bold transition"
            >
              📅 Add to Calendar
            </a>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="space-y-5">
      <h2 className="text-lg font-black text-white">My Schedule</h2>

      {upcoming.length === 0 && past.length === 0 && (
        <div className={`${CARD} border ${BORDER} rounded-xl p-8 text-center`}>
          <div className="text-3xl mb-2">📅</div>
          <div className="text-sm font-bold text-white">No appointments yet</div>
          <div className={`text-xs ${MUTED} mt-1`}>Appointments from your cases will appear here.</div>
        </div>
      )}

      {upcoming.length > 0 && (
        <div>
          <div className="text-xs font-bold text-[#f5c23e] uppercase tracking-wider mb-2">Upcoming</div>
          <div className="space-y-2">{upcoming.map(renderAppt)}</div>
        </div>
      )}

      {past.length > 0 && (
        <div>
          <div className={`text-xs font-bold ${MUTED} uppercase tracking-wider mb-2`}>Past</div>
          <div className="space-y-2 opacity-60">{past.map(renderAppt)}</div>
        </div>
      )}
    </div>
  );
};

// ═══════════════════════════════════════════════════════════════════════════
// SMS PANEL — quick text to family
// ═══════════════════════════════════════════════════════════════════════════
const SMSPanel: React.FC<{ referrals: Referral[]; navigatorName: string }> = ({ referrals, navigatorName }) => {
  const [selectedRefId, setSelectedRefId] = useState('');
  const [phone, setPhone] = useState('');
  const [message, setMessage] = useState('');
  const [sent, setSent] = useState(false);

  const templates = [
    `Hi, this is ${navigatorName.split(' ')[0]} from Cause We Care. Just checking in — is there anything you need help with today?`,
    `Hi, this is ${navigatorName.split(' ')[0]} from CWC. Your appointment is coming up. Please let us know if you need a ride.`,
    `Hi, this is ${navigatorName.split(' ')[0]} from Cause We Care. I have some good news about your case. When's a good time to talk?`,
    `Hi, this is ${navigatorName.split(' ')[0]} from CWC. We have some resources for your family. Can I call you today?`,
  ];

  const sendMessage = () => {
    if (!phone.trim() || !message.trim()) return;
    setSent(true);
    setTimeout(() => setSent(false), 3000);
    setMessage('');
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
      <div className={`${CARD} border ${BORDER} rounded-xl overflow-hidden`}>
        <div className="px-5 py-4 border-b border-[#1c2f6a]">
          <div className="text-xs font-bold text-[#f5c23e] uppercase tracking-wider">💬 Send a Text</div>
          <div className={`text-[10px] ${MUTED} mt-0.5`}>Family sees the CWC number. Your personal number stays private.</div>
        </div>
        <div className="px-5 py-5 space-y-4">
          <div>
            <label className="text-[10px] text-[#8ea2d6] uppercase tracking-wider font-bold block mb-1">Link to case</label>
            <select
              value={selectedRefId}
              onChange={e => setSelectedRefId(e.target.value)}
              className={`w-full bg-[#050f2e] border ${BORDER} rounded-lg px-3 py-2.5 text-sm text-white focus:border-[#f5c23e] focus:outline-none`}
            >
              <option value="">— Select a case —</option>
              {referrals.map(r => (
                <option key={r.id} value={r.id}>
                  {r.referral_id || r.id.slice(-8)} · {r.county || ''}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="text-[10px] text-[#8ea2d6] uppercase tracking-wider font-bold block mb-1">Phone number</label>
            <input
              type="tel" value={phone} onChange={e => setPhone(e.target.value)}
              placeholder="(313) 555-0123"
              className={`w-full bg-[#050f2e] border ${BORDER} rounded-lg px-4 py-3 text-sm text-white font-mono placeholder:text-[#6b7ba6] focus:border-[#f5c23e] focus:outline-none`}
            />
          </div>
          <div>
            <label className="text-[10px] text-[#8ea2d6] uppercase tracking-wider font-bold block mb-1">Message</label>
            <textarea
              value={message} onChange={e => setMessage(e.target.value)}
              placeholder="Type your message..."
              rows={4}
              className={`w-full bg-[#050f2e] border ${BORDER} rounded-lg px-4 py-3 text-sm text-white placeholder:text-[#6b7ba6] focus:border-[#f5c23e] focus:outline-none resize-none`}
            />
            <div className={`text-[10px] ${MUTED} mt-1`}>{message.length}/160 characters</div>
          </div>
          {sent ? (
            <div className="text-center py-2 text-emerald-400 text-sm font-bold">✓ Message sent</div>
          ) : (
            <button onClick={sendMessage} disabled={!phone.trim() || !message.trim()}
              className="w-full bg-[#f5c23e] hover:bg-[#fcd75a] disabled:opacity-40 text-[#081849] py-3 rounded-xl text-sm font-black transition">
              Send Text
            </button>
          )}
        </div>
      </div>

      <div className="space-y-4">
        <div className={`${CARD} border ${BORDER} rounded-xl p-5`}>
          <div className="text-xs font-bold text-[#f5c23e] uppercase tracking-wider mb-3">Quick Templates</div>
          <div className="space-y-1.5">
            {templates.map((t, i) => (
              <button key={i} onClick={() => setMessage(t)}
                className={`w-full text-left text-xs ${CARD} hover:bg-[#0f2468]/70 border ${BORDER} hover:border-[#f5c23e]/40 rounded-lg px-3 py-2.5 text-slate-200 transition`}>
                {t.length > 80 ? t.slice(0, 77) + '…' : t}
              </button>
            ))}
          </div>
        </div>
        <div className={`${CARD} border ${BORDER} rounded-xl p-5`}>
          <div className="text-xs font-bold text-[#f5c23e] uppercase tracking-wider mb-2">Tips</div>
          <ul className="text-xs text-[#8ea2d6] space-y-1.5 leading-relaxed">
            <li>• Keep it short and friendly</li>
            <li>• Always identify yourself: <strong className="text-white">"This is [name] from Cause We Care"</strong></li>
            <li>• Never include sensitive health info in a text</li>
            <li>• If they don't respond, follow up with a call</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

// ═══════════════════════════════════════════════════════════════════════════
// DOCUMENTS PANEL — upload & attach to cases
// ═══════════════════════════════════════════════════════════════════════════
const DocumentsPanel: React.FC<{ referrals: Referral[] }> = ({ referrals }) => {
  const [selectedRefId, setSelectedRefId] = useState('');
  const [docType, setDocType] = useState('');
  const [uploadNote, setUploadNote] = useState('');

  const docTypes = [
    { id: 'consent', label: '📝 Signed Consent Form', desc: 'Family consent for services' },
    { id: 'photo-home', label: '📸 Home Condition Photo', desc: 'Lead paint, mold, hazards' },
    { id: 'photo-remediation', label: '🛠️ Remediation Progress', desc: 'Before/during/after work' },
    { id: 'mibridges', label: '🤝 MIBridges Application', desc: 'Benefits enrollment docs' },
    { id: 'bll-result', label: '🩸 BLL Test Result', desc: 'Lab results for child' },
    { id: 'referral-form', label: '📋 Referral Paperwork', desc: 'MDHHS/LHD referral docs' },
    { id: 'insurance', label: '💳 Insurance Card', desc: 'Medicaid/MCO card photo' },
    { id: 'other', label: '📎 Other Document', desc: 'Any supporting document' },
  ];

  return (
    <div className="space-y-5">
      <h2 className="text-lg font-black text-white">Documents & Photos</h2>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        <div className={`${CARD} border ${BORDER} rounded-xl overflow-hidden`}>
          <div className="px-5 py-4 border-b border-[#1c2f6a]">
            <div className="text-xs font-bold text-[#f5c23e] uppercase tracking-wider">📎 Upload</div>
          </div>
          <div className="px-5 py-5 space-y-4">
            <div>
              <label className="text-[10px] text-[#8ea2d6] uppercase tracking-wider font-bold block mb-1">Link to case</label>
              <select value={selectedRefId} onChange={e => setSelectedRefId(e.target.value)}
                className={`w-full bg-[#050f2e] border ${BORDER} rounded-lg px-3 py-2.5 text-sm text-white focus:border-[#f5c23e] focus:outline-none`}>
                <option value="">— Select a case —</option>
                {referrals.map(r => (
                  <option key={r.id} value={r.id}>{r.referral_id || r.id.slice(-8)} · {r.county || ''}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="text-[10px] text-[#8ea2d6] uppercase tracking-wider font-bold block mb-1">Document type</label>
              <select value={docType} onChange={e => setDocType(e.target.value)}
                className={`w-full bg-[#050f2e] border ${BORDER} rounded-lg px-3 py-2.5 text-sm text-white focus:border-[#f5c23e] focus:outline-none`}>
                <option value="">— Select type —</option>
                {docTypes.map(d => <option key={d.id} value={d.id}>{d.label}</option>)}
              </select>
            </div>
            <div>
              <label className="text-[10px] text-[#8ea2d6] uppercase tracking-wider font-bold block mb-1">Note (optional)</label>
              <input value={uploadNote} onChange={e => setUploadNote(e.target.value)} placeholder="e.g. Front of house, visible paint chips"
                className={`w-full bg-[#050f2e] border ${BORDER} rounded-lg px-4 py-2.5 text-sm text-white placeholder:text-[#6b7ba6] focus:border-[#f5c23e] focus:outline-none`} />
            </div>
            <div className={`border-2 border-dashed ${BORDER} rounded-xl p-8 text-center hover:border-[#f5c23e]/50 transition cursor-pointer`}>
              <div className="text-3xl mb-2">📤</div>
              <div className="text-sm font-bold text-white">Tap to upload or take a photo</div>
              <div className={`text-[10px] ${MUTED} mt-1`}>JPG, PNG, PDF — max 10MB</div>
              <input type="file" className="hidden" accept="image/*,.pdf" capture="environment" />
            </div>
          </div>
        </div>

        <div className={`${CARD} border ${BORDER} rounded-xl p-5`}>
          <div className="text-xs font-bold text-[#f5c23e] uppercase tracking-wider mb-3">Document Types</div>
          <div className="space-y-2">
            {docTypes.map(d => (
              <div key={d.id} className="flex items-center gap-3 text-sm">
                <span className="text-lg">{d.label.split(' ')[0]}</span>
                <div>
                  <div className="text-white font-bold text-xs">{d.label.slice(d.label.indexOf(' ') + 1)}</div>
                  <div className={`text-[10px] ${MUTED}`}>{d.desc}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

// ═══════════════════════════════════════════════════════════════════════════
// ACTIVITY LOG — auto-timer + service tracking (billing is supervisor-only)
// ═══════════════════════════════════════════════════════════════════════════
const TimeLogPanel: React.FC<{ referrals: Referral[]; navigatorName: string }> = ({ referrals, navigatorName }) => {
  const [selectedRefId, setSelectedRefId] = useState('');
  const [activityType, setActivityType] = useState('');
  const [note, setNote] = useState('');
  const [timerRunning, setTimerRunning] = useState(false);
  const [timerStart, setTimerStart] = useState<number | null>(null);
  const [timerElapsed, setTimerElapsed] = useState(0);
  const [entries, setEntries] = useState<Array<{
    id: string; case_ref: string; activity: string; minutes: number; note: string; date: string; auto: boolean;
  }>>([]);

  const activityTypes = [
    { id: 'home-visit',    label: '🏠 Home Visit' },
    { id: 'phone-call',    label: '📞 Phone Call' },
    { id: 'care-coord',    label: '🤝 Care Coordination' },
    { id: 'mibridges',     label: '📋 MIBridges Navigation' },
    { id: 'clppp',         label: '🩸 CLPPP Follow-up' },
    { id: 'transport',     label: '🚕 Transportation Coordination' },
    { id: 'housing',       label: '🏩 Housing Navigation' },
    { id: 'health-ed',     label: '📖 Health Education' },
    { id: 'benefits',      label: '💳 Benefits Enrollment' },
    { id: 'admin',         label: '✏️ Documentation' },
  ];

  useEffect(() => {
    if (!timerRunning || !timerStart) return;
    const iv = setInterval(() => setTimerElapsed(Math.floor((Date.now() - timerStart) / 1000)), 1000);
    return () => clearInterval(iv);
  }, [timerRunning, timerStart]);

  const startTimer = () => {
    if (!selectedRefId || !activityType) return;
    setTimerStart(Date.now());
    setTimerElapsed(0);
    setTimerRunning(true);
  };

  const stopTimer = () => {
    const mins = Math.max(1, Math.ceil(timerElapsed / 60));
    const ref = referrals.find(r => r.id === selectedRefId);
    const label = activityTypes.find(a => a.id === activityType)?.label || activityType;
    setEntries(prev => [{
      id: `al-${Date.now()}`,
      case_ref: ref?.referral_id || selectedRefId.slice(-8),
      activity: label,
      minutes: mins,
      note,
      date: new Date().toISOString(),
      auto: true,
    }, ...prev]);
    setTimerRunning(false);
    setTimerStart(null);
    setTimerElapsed(0);
    setNote('');
  };

  const totalMinutes = entries.reduce((sum, e) => sum + e.minutes, 0);
  const totalHours = (totalMinutes / 60).toFixed(1);
  const fmtTimer = (sec: number) => {
    const h = Math.floor(sec / 3600);
    const m = Math.floor((sec % 3600) / 60);
    const s = sec % 60;
    return h > 0
      ? `${h}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`
      : `${m}:${s.toString().padStart(2, '0')}`;
  };

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-black text-white">Activity Log</h2>
          <div className={`text-[10px] ${MUTED}`}>Time is tracked automatically. Billing is handled by your supervisor.</div>
        </div>
        <div className={`${CARD} border ${BORDER} rounded-lg px-4 py-2 flex items-center gap-3`}>
          <div className="text-center">
            <div className="text-lg font-black text-[#f5c23e]">{totalHours}</div>
            <div className="text-[9px] text-[#8ea2d6] uppercase">Hours today</div>
          </div>
          <div className="text-center">
            <div className="text-lg font-black text-white">{entries.length}</div>
            <div className="text-[9px] text-[#8ea2d6] uppercase">Activities</div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        {/* Timer card */}
        <div className={`${CARD} border ${BORDER} rounded-xl overflow-hidden`}>
          <div className="px-5 py-4 border-b border-[#1c2f6a]">
            <div className="text-xs font-bold text-[#f5c23e] uppercase tracking-wider">⏱️ Activity Timer</div>
            <div className={`text-[10px] ${MUTED} mt-0.5`}>Select a case and activity, then hit Start. Clock runs until you stop.</div>
          </div>
          <div className="px-5 py-5 space-y-3">
            <div>
              <label className="text-[10px] text-[#8ea2d6] uppercase tracking-wider font-bold block mb-1">Case</label>
              <select value={selectedRefId} onChange={e => setSelectedRefId(e.target.value)} disabled={timerRunning}
                className={`w-full bg-[#050f2e] border ${BORDER} rounded-lg px-3 py-2.5 text-sm text-white focus:border-[#f5c23e] focus:outline-none disabled:opacity-50`}>
                <option value="">— Select —</option>
                {referrals.map(r => (
                  <option key={r.id} value={r.id}>{r.referral_id || r.id.slice(-8)} · {r.county || ''}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="text-[10px] text-[#8ea2d6] uppercase tracking-wider font-bold block mb-1">Activity</label>
              <select value={activityType} onChange={e => setActivityType(e.target.value)} disabled={timerRunning}
                className={`w-full bg-[#050f2e] border ${BORDER} rounded-lg px-3 py-2.5 text-sm text-white focus:border-[#f5c23e] focus:outline-none disabled:opacity-50`}>
                <option value="">— Select —</option>
                {activityTypes.map(a => <option key={a.id} value={a.id}>{a.label}</option>)}
              </select>
            </div>
            <div>
              <label className="text-[10px] text-[#8ea2d6] uppercase tracking-wider font-bold block mb-1">Note (optional)</label>
              <input value={note} onChange={e => setNote(e.target.value)} placeholder="What are you working on?"
                className={`w-full bg-[#050f2e] border ${BORDER} rounded-lg px-4 py-2.5 text-sm text-white placeholder:text-[#6b7ba6] focus:border-[#f5c23e] focus:outline-none`} />
            </div>

            {/* Timer display */}
            <div className={`rounded-xl p-5 text-center ${timerRunning ? 'bg-emerald-500/10 border border-emerald-500/30' : `bg-[#050f2e] border ${BORDER}`}`}>
              <div className={`text-4xl font-mono font-black ${timerRunning ? 'text-emerald-400' : 'text-[#8ea2d6]'}`}>
                {fmtTimer(timerElapsed)}
              </div>
              {timerRunning && (
                <div className="flex items-center justify-center gap-1.5 mt-2">
                  <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                  <span className="text-[10px] text-emerald-400 font-bold uppercase tracking-wider">Recording</span>
                </div>
              )}
            </div>

            {timerRunning ? (
              <button onClick={stopTimer}
                className="w-full bg-red-500 hover:bg-red-400 text-white py-3 rounded-xl text-sm font-black transition">
                Stop & Save
              </button>
            ) : (
              <button onClick={startTimer} disabled={!selectedRefId || !activityType}
                className="w-full bg-emerald-500 hover:bg-emerald-400 disabled:opacity-40 text-white py-3 rounded-xl text-sm font-black transition">
                Start Timer
              </button>
            )}
          </div>
        </div>

        {/* Today's activities */}
        <div className="space-y-4">
          <div className={`${CARD} border ${BORDER} rounded-xl p-5`}>
            <div className="text-xs font-bold text-[#f5c23e] uppercase tracking-wider mb-3">Today's Activities</div>
            {entries.length === 0 ? (
              <div className={`text-center py-8 ${MUTED} text-xs`}>No activities logged yet today.</div>
            ) : (
              <div className="space-y-2">
                {entries.map(e => (
                  <div key={e.id} className={`bg-[#050f2e] border ${BORDER} rounded-lg px-4 py-3`}>
                    <div className="flex justify-between items-center">
                      <span className="text-xs font-bold text-white">{e.activity}</span>
                      <div className="flex items-center gap-2">
                        {e.auto && <span className="text-[8px] px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 font-bold">AUTO</span>}
                        <span className="text-xs font-mono text-[#f5c23e]">{e.minutes} min</span>
                      </div>
                    </div>
                    <div className={`text-[10px] ${MUTED} mt-0.5`}>
                      Case #{e.case_ref} · {e.note || 'No note'} · {new Date(e.date).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className={`${CARD} border ${BORDER} rounded-xl p-4`}>
            <div className="text-[10px] text-[#8ea2d6] leading-relaxed">
              <strong className="text-white">How it works:</strong> Start the timer when you begin an activity. When you're done, hit Stop &amp; Save. Time is logged automatically to the case.
              Your supervisor reviews and submits all billing.
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// ═══════════════════════════════════════════════════════════════════════════
// RESOURCE DIRECTORY — quick-access links and numbers
// ═══════════════════════════════════════════════════════════════════════════
const ResourceDirectory: React.FC = () => {
  const categories = [
    {
      title: '🏛️ State Programs',
      items: [
        { name: 'MIBridges Portal', desc: 'Benefits application — Medicaid, SNAP, WIC, childcare', url: 'https://newmibridges.michigan.gov', phone: '1-844-799-9876' },
        { name: 'MDHHS — Get Ahead of Lead', desc: 'MI Lead Safe drinking water programs', url: 'https://www.michigan.gov/mileadsafe/get-ahead-of-lead' },
        { name: 'Apply for Home Lead Services', desc: 'State intake for lead services eligibility', url: 'https://www.michigan.gov/mileadsafe/lead-services/apply-for-home-lead-services' },
        { name: 'MDHHS Provider Support', desc: 'Medicaid provider inquiries', phone: '1-800-292-2550' },
      ],
    },
    {
      title: '🏥 Health & Safety',
      items: [
        { name: 'MI Poison Control', desc: '24/7 poison help line', phone: '1-800-222-1222' },
        { name: 'CLPPP — Lead Poisoning Prevention', desc: 'Childhood lead program contacts', phone: '1-866-691-5323' },
        { name: '211 Michigan', desc: 'Connect to local services — housing, food, health', phone: '211', url: 'https://www.211.org' },
      ],
    },
    {
      title: '🏩 Housing & Utilities',
      items: [
        { name: 'MSHDA — MI Housing Authority', desc: 'Emergency housing, Section 8, HUD programs', url: 'https://www.michigan.gov/mshda', phone: '517-373-8370' },
        { name: 'Wayne Metro CAA', desc: 'Wayne County emergency assistance', phone: '313-388-9799', url: 'https://www.waynemetro.org' },
        { name: 'DTE Energy Assistance', desc: 'Low-income energy programs', phone: '800-477-4747' },
        { name: 'THAW — Heat & Warmth Fund', desc: 'Utility bill assistance', url: 'https://www.thawfund.org', phone: '800-866-8429' },
      ],
    },
    {
      title: '🍎 Food & Nutrition',
      items: [
        { name: 'WIC Michigan', desc: 'Women, Infants, Children nutrition program', url: 'https://www.michigan.gov/mdhhs/assistance-programs/wic', phone: '1-800-26-BIRTH' },
        { name: 'Gleaners Food Bank', desc: 'Southeast Michigan food assistance', url: 'https://www.gcfb.org', phone: '866-452-3674' },
        { name: 'Forgotten Harvest', desc: 'Metro Detroit food rescue', url: 'https://www.forgottenharvest.org', phone: '248-967-1500' },
      ],
    },
    {
      title: '📞 SHIELD Contacts',
      items: [
        { name: 'Angela Medina — MDHHS', desc: 'Section Manager, Care Coordination, EHB', phone: '517-897-5203' },
        { name: 'Aimee Surma — MDHHS', desc: 'Environmental Health Bureau', phone: '' },
        { name: 'Dee Davis — DDI', desc: 'CEO, Program Administration', phone: '248-376-4550' },
      ],
    },
  ];

  return (
    <div className="space-y-5">
      <h2 className="text-lg font-black text-white">Resource Directory</h2>
      <div className={`text-xs ${MUTED}`}>Quick-access numbers, links, and contacts for navigators in the field.</div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {categories.map(cat => (
          <div key={cat.title} className={`${CARD} border ${BORDER} rounded-xl overflow-hidden`}>
            <div className="px-5 py-3 border-b border-[#1c2f6a]">
              <div className="text-xs font-bold text-[#f5c23e] uppercase tracking-wider">{cat.title}</div>
            </div>
            <div className="divide-y divide-[#1c2f6a]">
              {cat.items.map(item => (
                <div key={item.name} className="px-5 py-3 hover:bg-[#0f2468]/40 transition">
                  <div className="text-sm font-bold text-white">{item.name}</div>
                  <div className={`text-[10px] ${MUTED}`}>{item.desc}</div>
                  <div className="flex gap-3 mt-1.5">
                    {item.phone && (
                      <a href={`tel:${item.phone}`} className="text-[10px] font-bold text-emerald-400 hover:text-emerald-300 transition">
                        📞 {item.phone}
                      </a>
                    )}
                    {item.url && (
                      <a href={item.url} target="_blank" rel="noopener noreferrer" className="text-[10px] font-bold text-blue-400 hover:text-blue-300 transition">
                        🔗 Website
                      </a>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default NavigatorWorkspace;
