import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { api } from '../../api/client';
import SHIELDAcronym from '../shield/Acronym';

/**
 * SHIELD — Lead Screening & MDHHS Referral Command Center
 * DEE DAVIS INC + CAUSE WE CARE
 *
 * Anchored by Michigan Public Act 146 of 2023 — universal blood lead screening
 * mandate, effective April 30, 2025.
 *
 * Brand: CWC sunflower yellow + cobalt blue. Left sidebar nav. Alerts-first
 * landing. Wizard intake. Case-centric detail view. CWC + DDI co-branded.
 *
 * Palette (CWC-keyed)
 *   cwc-blue-950  #050f2e   deepest — app backdrop
 *   cwc-blue-900  #081849   primary surface / sidebar
 *   cwc-blue-800  #0f2468   card hover
 *   cwc-blue-600  #1f3fae   brand cobalt (logo text color)
 *   cwc-yellow    #f5c23e   sunflower primary accent
 *   cwc-yellow-hi #fcd75a   hover / highlight
 *   cream         #fff6d8   warm emphasis ink
 *
 * Semantic greens/reds/ambers kept for success/danger/warning states.
 */

interface SHIELDSystemProps {
  onBackToNexus: () => void;
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

type SLASnapshot = {
  urgency: string;
  target_hours: number;
  source: 'override' | 'urgency' | 'default';
  override: { hours: number; reason: string; by: string; at: string } | null;
  auto_escalated: boolean;
  escalated_reason: string | null;
  escalated_at: string | null;
  escalated_from: string | null;
  date_received?: string;
  first_contact_at?: string;
  deadline_iso?: string | null;
  elapsed_hours: number | null;
  remaining_hours: number | null;
  percent: number | null;
  breached: boolean;
  warning: boolean;
  stopped: boolean;
};

type ReferralRow = {
  id: string;
  referral_id?: string | number;
  date_received?: string;
  first_contact_at?: string;
  referral_source?: string;
  referring_agency?: string;
  case_worker_name?: string;
  case_worker_email?: string;
  case_worker_phone?: string;
  county?: string;
  services_requested?: string[];
  urgency?: string;
  status?: string;
  notes?: string;
  intake_method?: string;
  sla?: SLASnapshot;
  urgency_auto_escalated?: boolean;
  urgency_escalated_from?: string;
  urgency_escalated_reason?: string;
  urgency_escalated_at?: string;
  sla_override_hours?: number;
  sla_override_reason?: string;
  sla_override_by?: string;
  sla_override_at?: string;
};

// Role-based access — mirrors backend SUPERVISOR_ROLES
type CurrentUser = { email: string; name: string; role: string };
const SUPERVISOR_ROLES = ['Supervisor', 'Admin'];
const isSupervisor = (u: CurrentUser | null) => !!u && SUPERVISOR_ROLES.includes(u.role);

type ChildRow = {
  id: string;
  child_name?: string;
  age_months?: number;
  lead_test_status?: string;
  blood_lead_level?: number;
  clppp_case_number?: string;
  clppp_status?: string;
};

type Alert = {
  type: string;
  severity: string;
  message: string;
  referral_id?: string;
  child_id?: string;
};

// Each section gets its own wayfinding color so you know where you are
const SECTIONS = [
  { id: 'overview',    label: 'Command',      sub: 'Alerts • Queue', glyph: 'O',  color: '#F5C23E' }, // CWC yellow
  { id: 'referrals',   label: 'Referrals',    sub: 'All cases',      glyph: 'R',  color: '#3B82F6' }, // blue
  { id: 'intake',      label: 'New Intake',   sub: 'MDHHS form',     glyph: '+',  color: '#10B981' }, // emerald
  { id: 'families',    label: 'Families',     sub: 'Households',     glyph: 'F',  color: '#8B5CF6' }, // violet
  { id: 'children',    label: 'Children',     sub: 'BLL • CLPPP',    glyph: 'C',  color: '#EC4899' }, // pink
  { id: 'activations', label: 'Services',     sub: 'Activations',    glyph: 'S',  color: '#F97316' }, // orange
  { id: 'billing',     label: 'Billing',      sub: 'MCO • Payers',   glyph: 'B',  color: '#14B8A6' }, // teal
  { id: 'outcomes',    label: 'Outcomes',     sub: 'MDHHS report',   glyph: 'M',  color: '#6366F1' }, // indigo
  { id: 'ai',          label: 'Navigator AI', sub: 'Case Q&A',       glyph: 'AI', color: '#D946EF' }, // fuchsia
];

// ──────────────────────────────────────────────────────────────────────────
// SHIELD referral pipeline — 6 stages, each with color + definition.
// Matches NEXUS pattern (PRISM, GBIS). Stage is derived from status +
// milestones + activations; computed purely on the frontend for now.
// ──────────────────────────────────────────────────────────────────────────
type Stage = 'Intake' | 'Triage' | 'Outreach' | 'Engaged' | 'In Service' | 'Closed';

const STAGES: { key: Stage; label: string; color: string; description: string }[] = [
  { key: 'Intake',     label: 'Intake',     color: '#3B82F6', description: 'Just received — awaiting navigator assignment' },
  { key: 'Triage',     label: 'Triage',     color: '#06B6D4', description: 'Navigator assigned, urgency + plan being built' },
  { key: 'Outreach',   label: 'Outreach',   color: '#8B5CF6', description: 'Inside 48-hour family contact window' },
  { key: 'Engaged',    label: 'Engaged',    color: '#F97316', description: 'Family reached, needs assessed' },
  { key: 'In Service', label: 'In Service', color: '#F5C23E', description: 'Services activated & delivering' },
  { key: 'Closed',     label: 'Closed',     color: '#10B981', description: 'Outcomes documented, billing finalized' },
];

function stageOf(r: { status?: string; services_requested?: string[] } | any, milestones?: any[], activations?: any[]): Stage {
  const status = (r?.status || '').toLowerCase();
  if (status === 'closed' || status === 'completed') return 'Closed';
  if (activations && activations.length > 0 && activations.some((a: any) => {
    const s = (a.status || '').toLowerCase();
    return s === 'active' || s === 'delivered' || s === 'completed' || s === 'in service' || s === 'in-service';
  })) return 'In Service';
  if (milestones && milestones.some((m: any) => /family.*contacted|engagement|assessment/i.test(m.milestone_type || ''))) return 'Engaged';
  if (status === 'active' || status === 'pending') return 'Outreach';
  if (status === 'assigned') return 'Triage';
  return 'Intake';
}

function stageMeta(key: Stage) {
  return STAGES.find(s => s.key === key) || STAGES[0];
}

const COUNTIES = ['Wayne', 'Oakland', 'Macomb', 'Genesee', 'Kent', 'Muskegon', 'Other'];
const URGENCY_LEVELS = ['Standard', 'Urgent', 'Emergency'];
const SERVICE_CHOICES = [
  'Lead Screening',
  'CLPPP Follow-up',
  'NEMT',
  'Lead Remediation',
  'Housing',
  'Food Navigation',
  'Drug Testing',
  'DNA',
  'Specimen Transport',
  'Filter Safety Net',
];

const SERVICE_COLOR_MAP: Record<string, string> = {
  'Lead Screening':     '#026666',
  'CLPPP Follow-up':    '#17415f',
  'NEMT':               '#CA4D22',
  'Lead Remediation':   '#862074',
  'Housing':            '#093C44',
  'Food Navigation':    '#76BAB2',
  'Drug Testing':       '#046791',
  'DNA':                '#2F8D98',
  'Specimen Transport': '#115E6E',
  'Filter Safety Net':  '#046791',
  'Medical Monitoring': '#026666',
  'Blood Lead Level (BLL) Testing':             '#026666',
  'CLPPP Case Management':                      '#17415f',
  'NEMT — Non-Emergency Medical Transportation': '#CA4D22',
  'Lead Remediation Coordination':               '#862074',
  'Housing Navigation':                          '#093C44',
  'MIBridges Benefits Navigation':               '#76BAB2',
  'Filter Safety Net / Drinking Water':          '#046791',
  'Community Health Worker Home Visit':           '#2F8D98',
  'Nurse Home Visit':                            '#115E6E',
};

function svcColor(name: string): string {
  return SERVICE_COLOR_MAP[name] || '#8ea2d6';
}

// Brand tokens (used in arbitrary Tailwind values)
const BG_APP = 'bg-[#050f2e]';
const BG_SURFACE = 'bg-[#081849]';
const BG_SURFACE_ALT = 'bg-[#0a1a52]';
const BORDER_SOFT = 'border-[#1c2f6a]/70';
const TEXT_MUTED = 'text-[#8ea2d6]';
const YELLOW = 'text-[#f5c23e]';

const SHIELDSystem: React.FC<SHIELDSystemProps> = ({ activeTab, setActiveTab }) => {
  const [dashboard, setDashboard] = useState<any>(null);
  const [referrals, setReferrals] = useState<ReferralRow[]>([]);
  const [families, setFamilies] = useState<any[]>([]);
  const [children, setChildren] = useState<ChildRow[]>([]);
  const [activations, setActivations] = useState<any[]>([]);
  const [billing, setBilling] = useState<any[]>([]);
  const [outcomes, setOutcomes] = useState<any>(null);
  const [selectedCase, setSelectedCase] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [toast, setToast] = useState<{ tone: 'ok' | 'err' | 'info'; message: string } | null>(null);
  const [filters, setFilters] = useState({ status: '', county: '', urgency: '' });

  // Acting user — drives supervisor gating (SLA override etc.)
  // Persisted to localStorage so the selection survives reloads.
  const [navigators, setNavigators] = useState<Array<{ id: string; name?: string; email?: string; role?: string }>>([]);
  const [currentUser, setCurrentUser] = useState<CurrentUser | null>(() => {
    try {
      const raw = localStorage.getItem('shield_current_user');
      return raw ? JSON.parse(raw) : null;
    } catch { return null; }
  });
  const updateCurrentUser = useCallback((u: CurrentUser | null) => {
    setCurrentUser(u);
    try {
      if (u) localStorage.setItem('shield_current_user', JSON.stringify(u));
      else localStorage.removeItem('shield_current_user');
    } catch { /* quota etc. */ }
  }, []);

  const mappedTab = useMemo(() => {
    const known = SECTIONS.map(s => s.id);
    return known.includes(activeTab) ? activeTab : 'overview';
  }, [activeTab]);

  const showToast = useCallback((tone: 'ok' | 'err' | 'info', message: string) => {
    setToast({ tone, message });
    setTimeout(() => setToast(null), 4000);
  }, []);

  const fetchDashboard = useCallback(async () => {
    try {
      setLoading(true);
      const data = await api.getShieldDashboard();
      setDashboard(data);
    } catch (e: any) {
      showToast('err', `Dashboard load failed: ${e.message || 'unknown'}`);
    } finally {
      setLoading(false);
    }
  }, [showToast]);

  const fetchReferrals = useCallback(async () => {
    try {
      setLoading(true);
      const clean: any = {};
      if (filters.status) clean.status = filters.status;
      if (filters.county) clean.county = filters.county;
      if (filters.urgency) clean.urgency = filters.urgency;
      const data = await api.getShieldReferrals(clean);
      setReferrals((data?.referrals || []) as ReferralRow[]);
    } catch (e: any) {
      showToast('err', `Referrals load failed: ${e.message || 'unknown'}`);
    } finally {
      setLoading(false);
    }
  }, [filters, showToast]);

  const fetchFamilies = useCallback(async () => {
    try { const data = await api.getShieldFamilies(); setFamilies(data?.families || []); }
    catch { /* silent */ }
  }, []);

  const fetchChildren = useCallback(async () => {
    try { const data = await api.getShieldChildren(); setChildren((data?.children || []) as ChildRow[]); }
    catch { /* silent */ }
  }, []);

  const fetchActivations = useCallback(async () => {
    try { const data = await api.getShieldActivations(); setActivations(data?.activations || []); }
    catch { /* silent */ }
  }, []);

  const fetchBilling = useCallback(async () => {
    try { const data = await api.getShieldBilling(); setBilling(data?.billing || []); }
    catch { /* silent */ }
  }, []);

  const fetchOutcomes = useCallback(async () => {
    try { const data = await api.getShieldOutcomesReport(); setOutcomes(data?.report || null); }
    catch { /* silent */ }
  }, []);

  const fetchNavigators = useCallback(async () => {
    try {
      const data = await api.getShieldNavigators();
      const list = (data?.navigators || []) as any[];
      setNavigators(list);
      // Auto-select previously saved user if still present & fresh their role
      if (currentUser) {
        const match = list.find((n: any) => (n.email || '').toLowerCase() === currentUser.email.toLowerCase());
        if (match && match.role !== currentUser.role) {
          updateCurrentUser({
            email: match.email || currentUser.email,
            name: match.name || currentUser.name,
            role: match.role || currentUser.role,
          });
        }
      }
    } catch { /* silent */ }
  }, [currentUser, updateCurrentUser]);

  useEffect(() => { fetchDashboard(); fetchNavigators(); }, [fetchDashboard, fetchNavigators]);

  useEffect(() => {
    switch (mappedTab) {
      case 'overview':
      case 'referrals': fetchReferrals(); break;
      case 'families': fetchFamilies(); break;
      case 'children': fetchChildren(); break;
      case 'activations': fetchActivations(); break;
      case 'billing': fetchBilling(); break;
      case 'outcomes': fetchOutcomes(); break;
      default: break;
    }
  }, [mappedTab, fetchReferrals, fetchFamilies, fetchChildren, fetchActivations, fetchBilling, fetchOutcomes]);

  const openCase = useCallback(async (referralId: string) => {
    try {
      setLoading(true);
      const data = await api.getShieldReferral(referralId);
      setSelectedCase(data);
    } catch (e: any) {
      showToast('err', `Case load failed: ${e.message || 'unknown'}`);
    } finally {
      setLoading(false);
    }
  }, [showToast]);

  const closeCase = () => setSelectedCase(null);

  const summary = dashboard?.summary || {};
  const alerts: Alert[] = dashboard?.alerts || [];
  const configured = dashboard?.configured !== false;

  return (
    <div className={`flex min-h-screen ${BG_APP} text-slate-100`}>
      {/* ───────── LEFT SIDEBAR ───────── */}
      <aside className={`w-64 ${BG_SURFACE} border-r ${BORDER_SOFT} flex flex-col sticky top-0 h-screen`}>
        {/* SHIELD mark */}
        <div className={`px-5 py-5 border-b ${BORDER_SOFT}`}>
          <div className="flex items-center gap-3">
            <ShieldMark />
            <div className="leading-tight min-w-0">
              <div className="text-base font-black tracking-wide text-white">🛡️ SHIELD</div>
              <div className="text-[9px] text-[#8ea2d6] tracking-wider uppercase font-bold mt-0.5 leading-snug">
                Support · Health · Intake<br />
                Enrollment · Linkage · Delivery
              </div>
            </div>
          </div>

          {/* CWC × DDI co-brand — actual brand wordmarks */}
          <div className={`mt-4 pt-4 border-t ${BORDER_SOFT}`}>
            <div className={`text-[10px] uppercase tracking-widest ${TEXT_MUTED} mb-2 font-bold`}>A partnership of</div>
            <div className="flex items-center gap-2">
              <CWCWordmark />
              <div className="text-[#3b4a80] text-sm font-black">×</div>
              <DDIWordmark />
            </div>
            <div className="mt-3">
              <div className="text-[10px] font-black text-[#f5c23e] tracking-wider uppercase">Care. Navigate. Transform.</div>
              <div className="text-[9px] text-[#f5c23e]/50 italic mt-0.5">More than a mission — a movement.</div>
            </div>
          </div>
        </div>

        {/* Section nav — each section uses its own wayfinding color */}
        <nav className="flex-1 px-2 py-3 overflow-y-auto">
          {SECTIONS.map((s) => {
            const active = mappedTab === s.id;
            const tint = s.color;
            return (
              <button
                key={s.id}
                onClick={() => { setActiveTab(s.id); setSelectedCase(null); }}
                className={`w-full group flex items-center gap-3 px-3 py-2.5 rounded-lg mb-0.5 transition text-left relative ${
                  active ? 'border' : 'border border-transparent hover:bg-[#0f2468]/60'
                }`}
                style={active ? { backgroundColor: `${tint}1A`, borderColor: `${tint}66` } : undefined}
              >
                {active && <span className="absolute left-0 top-2 bottom-2 w-[3px] rounded-r" style={{ backgroundColor: tint }} />}
                <span
                  className="w-8 h-8 rounded-md flex items-center justify-center font-black text-xs shrink-0 transition"
                  style={active
                    ? { backgroundColor: tint, color: '#081849' }
                    : { backgroundColor: '#0a1a52', color: '#8ea2d6' }}
                >
                  {s.glyph}
                </span>
                <span className="flex-1 min-w-0">
                  <span className={`block text-sm font-bold ${active ? 'text-white' : 'text-slate-200'}`}>{s.label}</span>
                  <span className="block text-[10px]" style={{ color: active ? tint : '#8ea2d6' }}>{s.sub}</span>
                </span>
              </button>
            );
          })}
        </nav>

        {/* Acting navigator — drives supervisor gating (SLA overrides etc.) */}
        <div className={`px-4 py-3 border-t ${BORDER_SOFT}`}>
          <div className={`text-[10px] uppercase tracking-widest ${TEXT_MUTED} font-bold mb-1.5 flex items-center justify-between`}>
            <span>Acting as</span>
            {isSupervisor(currentUser) && (
              <span className="text-[9px] text-[#f5c23e] bg-[#f5c23e]/15 border border-[#f5c23e]/50 rounded px-1.5 py-0.5">SUPERVISOR</span>
            )}
          </div>
          <select
            value={currentUser?.email || ''}
            onChange={(e) => {
              const email = e.target.value;
              if (!email) { updateCurrentUser(null); return; }
              const match = navigators.find((n: any) => (n.email || '') === email);
              if (match) {
                updateCurrentUser({
                  email: match.email || '',
                  name: match.name || match.email || 'Navigator',
                  role: match.role || 'Navigator',
                });
              }
            }}
            className="w-full bg-[#050f2e] border border-[#1c2f6a] rounded-md px-2 py-1.5 text-xs text-slate-100 focus:border-[#f5c23e] focus:outline-none"
          >
            <option value="">— Select navigator —</option>
            {navigators.map((n: any) => (
              <option key={n.id} value={n.email || n.id}>
                {(n.name || n.email || 'Unnamed')}{n.role ? ` · ${n.role}` : ''}
              </option>
            ))}
          </select>
          {currentUser && (
            <div className="text-[10px] text-[#8ea2d6] mt-1 truncate">{currentUser.email}</div>
          )}
          {!currentUser && (
            <div className="text-[10px] text-[#6b7ba6] italic mt-1">SLA overrides require a Supervisor.</div>
          )}
        </div>

        {/* Mission + regulatory anchor footer */}
        <div className={`px-4 py-4 border-t ${BORDER_SOFT}`}>
          <div className={`text-[10px] ${TEXT_MUTED} leading-relaxed`}>
            <div className="font-black text-[#f5c23e] mb-1.5 tracking-wider uppercase">Care. Navigate. Transform.</div>
            <div className="font-bold text-[#8ea2d6] mb-1 tracking-wider uppercase text-[9px]">Mandate</div>
            Michigan Public Act 146 of 2023 — universal blood lead screening, effective April 30, 2025.
          </div>
        </div>
      </aside>

      {/* ───────── MAIN CONTENT ───────── */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Top bar — eyebrow colored by active section */}
        <header className={`${BG_SURFACE}/80 backdrop-blur border-b ${BORDER_SOFT} px-8 py-4 sticky top-0 z-20`}>
          <div className="flex items-center justify-between gap-6">
            <div className="flex items-center gap-3">
              <span className="w-1 h-10 rounded-full" style={{ backgroundColor: sectionColor(mappedTab) }} />
              <div>
                <div className="text-[10px] uppercase tracking-[0.25em] font-bold" style={{ color: sectionColor(mappedTab) }}>
                  {SECTIONS.find(s => s.id === mappedTab)?.label || 'Command'} {selectedCase ? ' / Case Detail' : ''}
                </div>
                <div className="text-xl font-black text-white mt-0.5">
                  {selectedCase ? caseTitle(selectedCase) : sectionTitle(mappedTab)}
                </div>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <StatusChip active={configured} />
              <NotificationChannels />
              <button
                onClick={fetchDashboard}
                disabled={loading}
                className={`text-xs font-semibold text-slate-200 hover:text-white ${BG_SURFACE_ALT} hover:bg-[#12286b] border ${BORDER_SOFT} rounded-md px-3 py-1.5 disabled:opacity-50`}
              >
                {loading ? 'Syncing…' : 'Refresh'}
              </button>
              <button
                onClick={() => { setActiveTab('intake'); setSelectedCase(null); }}
                className="bg-[#f5c23e] hover:bg-[#fcd75a] text-[#081849] text-sm font-black px-4 py-2 rounded-md shadow-[0_2px_0_0_rgba(146,102,0,0.4)]"
              >
                + New Intake
              </button>
            </div>
          </div>
        </header>

        {/* Config banner */}
        {!configured && (
          <div className="bg-amber-950/40 border-b border-amber-700/50 px-8 py-3 flex items-start gap-3">
            <div className="w-6 h-6 rounded-full bg-amber-600/30 border border-amber-500 flex items-center justify-center shrink-0 text-amber-200 font-black text-xs">!</div>
            <div className="flex-1 text-sm">
              <div className="font-bold text-amber-200">Airtable base not configured</div>
              <div className="text-xs text-amber-200/70 mt-0.5">
                {dashboard?.hint || 'Set LEAD_SCREENING_BASE_ID in .env and create the nexus_lead_screening base with the 10 tables. Restart API to apply.'}
              </div>
            </div>
          </div>
        )}

        {/* Toast */}
        {toast && (
          <div className={`fixed top-6 right-8 z-50 px-4 py-2 rounded-md shadow-lg border text-sm font-semibold ${
            toast.tone === 'ok' ? 'bg-emerald-900/90 border-emerald-600 text-emerald-50' :
            toast.tone === 'err' ? 'bg-rose-900/90 border-rose-600 text-rose-50' :
            'bg-[#0a1a52] border-[#1c2f6a] text-slate-100'
          }`}>
            {toast.message}
          </div>
        )}

        {/* Body */}
        <main className="flex-1 px-8 py-6 overflow-y-auto">
          {selectedCase ? (
            <CaseDetailPanel
              caseDetail={selectedCase}
              onBack={closeCase}
              onRefresh={() => openCase(selectedCase.referral?.id)}
              onToast={showToast}
              currentUser={currentUser}
            />
          ) : (
            <>
              {mappedTab === 'overview' && (
                <OverviewSection
                  summary={summary}
                  alerts={alerts}
                  referrals={referrals}
                  onOpenCase={openCase}
                  onJumpToQueue={() => setActiveTab('referrals')}
                />
              )}
              {mappedTab === 'referrals' && (
                <ReferralsSection
                  referrals={referrals}
                  filters={filters}
                  onFiltersChange={setFilters}
                  onRefresh={fetchReferrals}
                  onOpenCase={openCase}
                  loading={loading}
                />
              )}
              {mappedTab === 'intake' && (
                <IntakeWizard
                  onSuccess={(ref) => {
                    showToast('ok', `Referral received — reference ${ref}`);
                    setActiveTab('overview');
                    fetchDashboard();
                    fetchReferrals();
                  }}
                  onError={(msg) => showToast('err', msg)}
                />
              )}
              {mappedTab === 'families' && <FamiliesSection families={families} />}
              {mappedTab === 'children' && <ChildrenSection childrenRows={children} />}
              {mappedTab === 'activations' && <ActivationsSection activations={activations} />}
              {mappedTab === 'billing' && <BillingSection billing={billing} />}
              {mappedTab === 'outcomes' && <OutcomesSection outcomes={outcomes} onRefresh={fetchOutcomes} />}
              {mappedTab === 'ai' && <AISection />}
            </>
          )}
        </main>
      </div>
    </div>
  );
};

// ──────────────────────────────────────────────────────────────────────────
// Brand marks
// ──────────────────────────────────────────────────────────────────────────

/** SHIELD icon — yellow disc (CWC) with cobalt shield stroke (CWC brush-blue) */
const ShieldMark: React.FC = () => (
  <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-[#f5c23e] to-[#e0a92e] border border-[#fcd75a] flex items-center justify-center shadow-[0_2px_0_0_rgba(0,0,0,0.25)]">
    <svg viewBox="0 0 24 24" className="w-5 h-5 text-[#1f3fae]" fill="none" stroke="currentColor" strokeWidth="2.6" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 2l8 3v7c0 5-3.5 9-8 10-4.5-1-8-5-8-10V5l8-3z" />
      <path d="M9 12l2 2 4-4" />
    </svg>
  </div>
);

/** Cause We Care logo — real brand asset, square yellow card */
const CWCWordmark: React.FC = () => (
  <div className="flex-1 min-w-0 bg-[#f5c23e] border border-[#fcd75a] rounded-md p-1 flex items-center justify-center overflow-hidden">
    <img src="/cwc-logo.png" alt="Cause We Care" className="w-full h-14 object-contain" />
  </div>
);

/** Dee Davis Inc logo — real brand asset on cobalt */
const DDIWordmark: React.FC = () => (
  <div className="flex-1 min-w-0 bg-white border border-[#1c2f6a] rounded-md p-1 flex items-center justify-center overflow-hidden">
    <img src="/ddi-logo.png" alt="DEE DAVIS INC" className="w-full h-14 object-contain" />
  </div>
);

/**
 * AcronymKey — the "What SHIELD stands for" reference card.
 * Shows all three variants with their audience so the team and any visitor
 * to the command center immediately understands the name's intent.
 */
const AcronymKey: React.FC = () => {
  const variants: Array<{ key: 'operations' | 'mission' | 'compliance'; title: string; audience: string }> = [
    { key: 'operations', title: 'Navigator view',  audience: 'Internal — what the system does for staff' },
    { key: 'mission',    title: 'Family view',     audience: 'Public /refer — child-welfare mission' },
    { key: 'compliance', title: 'MDHHS / grants',  audience: 'Auditor view — formal process framing' },
  ];
  return (
    <section className="bg-[#0a1a52]/60 border border-[#1c2f6a] rounded-xl p-5">
      <div className="flex items-center gap-3 mb-4">
        <div className="w-8 h-8 rounded-md bg-[#f5c23e] text-[#1f3fae] font-black text-sm flex items-center justify-center">S</div>
        <div>
          <div className="text-[10px] uppercase tracking-[0.22em] text-[#f5c23e] font-bold">Every Family Deserves a SHIELD 🛡️</div>
          <div className="text-xs text-[#8ea2d6] mt-0.5">One name, three audiences — we use whichever fits the situation.</div>
        </div>
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-3">
        {variants.map(v => (
          <div key={v.key} className="bg-[#050f2e] border border-[#1c2f6a] rounded-lg p-4">
            <div className="text-[10px] uppercase tracking-widest text-[#f5c23e] font-black mb-0.5">{v.title}</div>
            <div className="text-[10px] text-[#8ea2d6] mb-3">{v.audience}</div>
            <SHIELDAcronym
              variant={v.key}
              layout="grid"
              letterClass="text-2xl font-black text-[#f5c23e] leading-none"
              wordClass="text-[9px] uppercase tracking-wider font-bold text-slate-200 mt-1"
            />
          </div>
        ))}
      </div>
    </section>
  );
};

// ──────────────────────────────────────────────────────────────────────────
// Shared atoms
// ──────────────────────────────────────────────────────────────────────────

function sectionTitle(section: string): string {
  switch (section) {
    case 'overview': return 'Navigator Command Center';
    case 'referrals': return 'Referral Queue';
    case 'intake': return 'New Referral Intake';
    case 'families': return 'Families';
    case 'children': return 'Children & Lead Screening';
    case 'activations': return 'Service Activations';
    case 'billing': return 'Billing & Payer Routing';
    case 'outcomes': return 'MDHHS Outcomes Report';
    case 'ai': return 'Navigator AI Assistant';
    default: return 'SHIELD';
  }
}

function caseTitle(caseDetail: any): string {
  const name = caseDetail?.family?.family_name || 'Family';
  const ref = caseDetail?.referral?.referral_id ?? (caseDetail?.referral?.id || '').slice(-6);
  return `${name} Family — #${ref}`;
}

function sectionColor(id: string): string {
  return SECTIONS.find(s => s.id === id)?.color || '#F5C23E';
}

// ──────────────────────────────────────────────────────────────────────────
// Stage components — color-coded pill, pipeline, and funnel
// ──────────────────────────────────────────────────────────────────────────
const StagePill: React.FC<{ stage: Stage }> = ({ stage }) => {
  const m = stageMeta(stage);
  return (
    <span
      className="inline-flex items-center gap-1.5 text-[10px] font-black tracking-wider uppercase px-2 py-0.5 rounded border"
      style={{ backgroundColor: `${m.color}15`, borderColor: `${m.color}80`, color: m.color }}
    >
      <span className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: m.color }} />
      {m.label}
    </span>
  );
};

/** Horizontal stage tracker — shows the 6 stages and highlights where the case is */
const StagePipeline: React.FC<{ current: Stage }> = ({ current }) => {
  const idx = STAGES.findIndex(s => s.key === current);
  return (
    <div className="w-full">
      <div className="flex items-stretch gap-0 rounded-lg overflow-hidden border border-[#1c2f6a] bg-[#081849]/60">
        {STAGES.map((s, i) => {
          const isPast = i < idx;
          const isCurrent = i === idx;
          const isFuture = i > idx;
          return (
            <div
              key={s.key}
              className="flex-1 relative px-3 py-2.5 flex items-center gap-2 border-r last:border-r-0"
              style={{
                borderColor: '#1c2f6a',
                backgroundColor: isCurrent ? `${s.color}22` : isPast ? `${s.color}10` : 'transparent',
              }}
            >
              <div
                className="w-6 h-6 rounded-full flex items-center justify-center text-[10px] font-black shrink-0"
                style={{
                  backgroundColor: isCurrent || isPast ? s.color : '#0a1a52',
                  color: isCurrent || isPast ? '#081849' : '#6b7ba6',
                  boxShadow: isCurrent ? `0 0 0 3px ${s.color}33` : 'none',
                }}
              >
                {isPast ? '✓' : i + 1}
              </div>
              <div className="min-w-0">
                <div
                  className="text-[10px] uppercase tracking-wider font-black truncate"
                  style={{ color: isCurrent ? s.color : isPast ? '#cbd5e1' : '#6b7ba6' }}
                >
                  {s.label}
                </div>
                {isCurrent && (
                  <div className="text-[9px] text-[#8ea2d6] truncate leading-tight">{s.description}</div>
                )}
              </div>
              {isFuture && i === idx + 1 && <div className="absolute left-0 top-0 bottom-0 w-px bg-[#1c2f6a]" />}
            </div>
          );
        })}
      </div>
    </div>
  );
};

/** Funnel view — shows case counts per stage, used on the Command dashboard */
const StageFunnel: React.FC<{ counts: Record<Stage, number>; onFilter?: (stage: Stage) => void }> = ({ counts, onFilter }) => (
  <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-2">
    {STAGES.map(s => {
      const count = counts[s.key] || 0;
      return (
        <button
          key={s.key}
          onClick={() => onFilter?.(s.key)}
          disabled={!onFilter}
          className="text-left rounded-lg border p-3 transition hover:brightness-125"
          style={{ backgroundColor: `${s.color}10`, borderColor: `${s.color}55` }}
        >
          <div className="flex items-baseline justify-between mb-1">
            <span className="text-[10px] uppercase tracking-wider font-black" style={{ color: s.color }}>{s.label}</span>
            <span className="text-xl font-black" style={{ color: s.color }}>{count}</span>
          </div>
          <div className="text-[9px] text-[#8ea2d6] leading-tight">{s.description}</div>
        </button>
      );
    })}
  </div>
);

const StatusChip: React.FC<{ active: boolean }> = ({ active }) => (
  <span className={`inline-flex items-center gap-2 text-[10px] font-bold uppercase tracking-widest px-2.5 py-1 rounded ${
    active ? 'bg-emerald-900/50 text-emerald-300' : 'bg-amber-900/50 text-amber-300'
  }`}>
    <span className={`w-1.5 h-1.5 rounded-full ${active ? 'bg-emerald-400 animate-pulse' : 'bg-amber-400'}`} />
    {active ? 'Live' : 'Setup'}
  </span>
);

const NotificationChannels: React.FC = () => {
  const [status, setStatus] = React.useState<any>(null);
  React.useEffect(() => {
    api.getShieldNotificationStatus().then((r: any) => { if (r?.success) setStatus(r); }).catch(() => {});
  }, []);
  if (!status) return null;
  const sms = status.sms?.enabled;
  const email = status.email?.enabled;
  return (
    <div className="flex items-center gap-1.5">
      <span className={`inline-flex items-center gap-1 text-[9px] font-bold uppercase tracking-wider px-2 py-0.5 rounded ${sms ? 'bg-sky-900/50 text-sky-300' : 'bg-slate-800 text-slate-500'}`}>
        <span className={`w-1 h-1 rounded-full ${sms ? 'bg-sky-400' : 'bg-slate-600'}`} />
        SMS
      </span>
      <span className={`inline-flex items-center gap-1 text-[9px] font-bold uppercase tracking-wider px-2 py-0.5 rounded ${email ? 'bg-violet-900/50 text-violet-300' : 'bg-slate-800 text-slate-500'}`}>
        <span className={`w-1 h-1 rounded-full ${email ? 'bg-violet-400' : 'bg-slate-600'}`} />
        Email
      </span>
    </div>
  );
};

const StatCard: React.FC<{ label: string; value: number | string; hint?: string; tone?: 'alert' | 'warn' | 'ok' | 'info' | 'neutral' | 'brand' }> = ({ label, value, hint, tone = 'neutral' }) => {
  const toneCls =
    tone === 'alert' ? 'text-rose-200 border-rose-700/40 bg-rose-950/30' :
    tone === 'warn' ? 'text-amber-200 border-amber-700/40 bg-amber-950/30' :
    tone === 'ok' ? 'text-emerald-200 border-emerald-700/40 bg-emerald-950/30' :
    tone === 'info' ? 'text-sky-200 border-sky-700/40 bg-sky-950/30' :
    tone === 'brand' ? 'text-[#fcd75a] border-[#f5c23e]/40 bg-[#f5c23e]/10' :
    'text-slate-100 border-[#1c2f6a]/70 bg-[#0a1a52]/60';
  return (
    <div className={`rounded-lg border px-4 py-3 ${toneCls}`}>
      <div className="text-2xl font-black leading-none">{value}</div>
      <div className="text-[10px] uppercase tracking-wider text-[#8ea2d6] mt-2 font-bold">{label}</div>
      {hint && <div className="text-[10px] text-[#6b7ba6] mt-0.5">{hint}</div>}
    </div>
  );
};

/** Urgency pill — 3-dot severity pattern (Standard = 1, Urgent = 2, Emergency = 3) */
const UrgencyPill: React.FC<{ urgency: string }> = ({ urgency }) => {
  const cfg =
    urgency === 'Emergency'
      ? { filled: 3, color: '#EF4444', bg: 'bg-rose-950/60', border: 'border-rose-600/60', text: 'text-rose-200' }
      : urgency === 'Urgent'
      ? { filled: 2, color: '#F59E0B', bg: 'bg-[#f5c23e]/15', border: 'border-[#f5c23e]/60', text: 'text-[#fcd75a]' }
      : { filled: 1, color: '#64748B', bg: 'bg-[#0a1a52]', border: 'border-[#1c2f6a]', text: 'text-slate-300' };
  return (
    <span className={`inline-flex items-center gap-1.5 text-[10px] font-bold tracking-wider uppercase px-2 py-0.5 rounded border ${cfg.bg} ${cfg.border} ${cfg.text}`}>
      <span className="flex items-center gap-[2px]">
        {[0, 1, 2].map(i => (
          <span
            key={i}
            className="w-1.5 h-1.5 rounded-full transition"
            style={{
              backgroundColor: i < cfg.filled ? cfg.color : 'transparent',
              border: i < cfg.filled ? 'none' : `1px solid ${cfg.color}66`,
            }}
          />
        ))}
      </span>
      {urgency}
    </span>
  );
};

/**
 * SLA countdown bar — server-computed snapshot.
 *
 * Target hours come from the backend SLA matrix (Emergency 24h / Urgent 48h /
 * Standard 120h) OR a supervisor override. The server also flags when the
 * clock has been stopped (first_contact_at set). Bar turns amber past 65%,
 * red when breached.
 *
 * Hidden on Engaged+ because the first-contact SLA is no longer the
 * bottleneck — downstream SLAs take over (CLPPP 24h, remediation 10 business
 * days, Medicaid prior-auth 3 business days).
 */
const SLABar: React.FC<{
  sla?: SLASnapshot;
  stage: Stage;
  compact?: boolean;
  dateReceived?: string;  // fallback for legacy calls
}> = ({ sla, stage, compact, dateReceived }) => {
  if (stage === 'Engaged' || stage === 'In Service' || stage === 'Closed') return null;

  // Prefer server snapshot. Fall back to simple client compute (default 48h).
  let targetHours = sla?.target_hours ?? 48;
  let elapsed = sla?.elapsed_hours;
  if (elapsed == null && (sla?.date_received || dateReceived)) {
    const d = sla?.date_received || dateReceived;
    if (d) {
      try {
        elapsed = Math.max(0, (Date.now() - new Date(d).getTime()) / 3_600_000);
      } catch { elapsed = null; }
    }
  }
  if (elapsed == null) return null;
  if (targetHours <= 0) targetHours = 48;

  const stopped = sla?.stopped ?? false;
  const breached = sla?.breached ?? (elapsed > targetHours);
  const warn = sla?.warning ?? (!breached && elapsed > targetHours * 0.65);
  const pct = Math.min(100, (elapsed / targetHours) * 100);
  const color = stopped ? '#64748B' : breached ? '#EF4444' : warn ? '#F59E0B' : '#10B981';

  // Friendly target label: "24h" / "48h" / "5 business days" / "Override Nh"
  const targetLabel =
    sla?.source === 'override' ? `Override ${Math.round(targetHours)}h`
    : targetHours === 120 ? '5 business days'
    : `${Math.round(targetHours)}h`;

  const label = stopped
    ? 'Contacted'
    : breached
      ? `${Math.round(elapsed - targetHours)}h past ${targetLabel}`
      : `${Math.round(elapsed)}h / ${targetLabel}`;

  if (compact) {
    return (
      <div className="inline-flex items-center gap-2 min-w-[90px]" title={stopped ? 'First contact logged — SLA clock stopped' : `Target: ${targetLabel}`}>
        <div className="flex-1 h-1 rounded-full bg-[#1c2f6a] overflow-hidden">
          <div className="h-full rounded-full transition-all" style={{ width: `${pct}%`, backgroundColor: color }} />
        </div>
        <span className="text-[10px] font-bold whitespace-nowrap" style={{ color }}>{label}</span>
      </div>
    );
  }
  return (
    <div className="inline-flex flex-col gap-1 min-w-[200px]">
      <div className="flex items-center justify-between text-[10px] font-bold">
        <span className="uppercase tracking-wider text-[#8ea2d6]">
          {stopped ? 'Contact SLA — met' : sla?.source === 'override' ? 'Contact SLA — supervisor override' : 'Contact SLA'}
        </span>
        <span style={{ color }}>{label}</span>
      </div>
      <div className="h-1.5 rounded-full bg-[#1c2f6a] overflow-hidden">
        <div className="h-full rounded-full transition-all" style={{ width: `${pct}%`, backgroundColor: color, boxShadow: breached ? `0 0 6px ${color}` : 'none' }} />
      </div>
    </div>
  );
};

/**
 * Tiny badge shown when SLA was auto-escalated by the BLL engine, or when a
 * supervisor override is currently in effect. Clicking reveals the reason.
 */
const SLAContextBadges: React.FC<{ sla?: SLASnapshot }> = ({ sla }) => {
  if (!sla) return null;
  const bits: React.ReactNode[] = [];
  if (sla.auto_escalated) {
    bits.push(
      <span
        key="esc"
        title={sla.escalated_reason || 'Auto-escalated by SLA engine'}
        className="inline-flex items-center gap-1 text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded border border-rose-600/60 bg-rose-950/50 text-rose-200"
      >
        <span className="w-1.5 h-1.5 rounded-full bg-rose-400 animate-pulse" />
        Auto-escalated{sla.escalated_from ? ` · ${sla.escalated_from} → ${sla.urgency}` : ''}
      </span>
    );
  }
  if (sla.source === 'override' && sla.override) {
    bits.push(
      <span
        key="ovr"
        title={`Set by ${sla.override.by || 'supervisor'}${sla.override.reason ? `: ${sla.override.reason}` : ''}`}
        className="inline-flex items-center gap-1 text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded border border-[#f5c23e]/60 bg-[#f5c23e]/15 text-[#fcd75a]"
      >
        <span className="w-1.5 h-1.5 rounded-full bg-[#fcd75a]" />
        SLA override · {Math.round(sla.override.hours)}h
      </span>
    );
  }
  if (!bits.length) return null;
  return <div className="flex items-center gap-2 flex-wrap">{bits}</div>;
};

const StatusPill: React.FC<{ status: string }> = ({ status }) => {
  const tone =
    status === 'New' ? 'bg-sky-950/60 border-sky-600/60 text-sky-200' :
    status === 'Active' ? 'bg-emerald-950/60 border-emerald-600/60 text-emerald-200' :
    status === 'Assigned' ? 'bg-[#f5c23e]/15 border-[#f5c23e]/60 text-[#fcd75a]' :
    status === 'Pending' ? 'bg-amber-950/60 border-amber-600/60 text-amber-200' :
    status === 'Completed' ? 'bg-[#0a1a52] border-[#1c2f6a] text-slate-400' :
    status === 'Closed' ? 'bg-[#0a1a52]/50 border-[#1c2f6a]/70 text-slate-500' :
    'bg-[#0a1a52] border-[#1c2f6a] text-slate-300';
  return <span className={`text-[10px] font-bold tracking-wider uppercase px-2 py-0.5 rounded border ${tone}`}>{status}</span>;
};

const SectionHeader: React.FC<{ eyebrow: string; title: string; action?: React.ReactNode; color?: string }> = ({ eyebrow, title, action, color = '#F5C23E' }) => (
  <div className="flex items-end justify-between gap-4 mb-4">
    <div className="flex items-center gap-2">
      <span className="w-1 h-8 rounded-full" style={{ backgroundColor: color }} />
      <div>
        <div className="text-[10px] uppercase tracking-[0.25em] font-bold" style={{ color }}>{eyebrow}</div>
        <div className="text-lg font-black text-white mt-0.5">{title}</div>
      </div>
    </div>
    {action}
  </div>
);

// ──────────────────────────────────────────────────────────────────────────
// OVERVIEW
// ──────────────────────────────────────────────────────────────────────────
const OverviewSection: React.FC<{
  summary: any;
  alerts: Alert[];
  referrals: ReferralRow[];
  onOpenCase: (id: string) => void;
  onJumpToQueue: () => void;
}> = ({ summary, alerts, referrals, onOpenCase, onJumpToQueue }) => {
  const sortedQueue = useMemo(() => {
    const copy = [...referrals];
    const urgencyWeight: Record<string, number> = { Emergency: 0, Urgent: 1, Standard: 2 };
    copy.sort((a, b) => {
      const u = (urgencyWeight[a.urgency || 'Standard'] ?? 3) - (urgencyWeight[b.urgency || 'Standard'] ?? 3);
      if (u !== 0) return u;
      return (b.date_received || '').localeCompare(a.date_received || '');
    });
    return copy.slice(0, 8);
  }, [referrals]);

  const stageCounts = useMemo(() => {
    const counts: Record<Stage, number> = { Intake: 0, Triage: 0, Outreach: 0, Engaged: 0, 'In Service': 0, Closed: 0 };
    for (const r of referrals) counts[stageOf(r)] += 1;
    return counts;
  }, [referrals]);

  return (
    <div className="space-y-6">
      {/* About SHIELD — three-variant acronym key */}
      <AcronymKey />

      {/* Alerts hero */}
      <section>
        <SectionHeader
          eyebrow="Action Items"
          title={alerts.length === 0 ? 'All cases within SLA' : `${alerts.length} alert${alerts.length === 1 ? '' : 's'} need attention`}
          color="#EF4444"
        />
        {alerts.length === 0 ? (
          <div className="bg-[#0a1a52]/60 border border-emerald-700/40 rounded-xl p-8 flex items-center gap-4">
            <div className="w-12 h-12 rounded-full bg-emerald-900/50 border border-emerald-600 flex items-center justify-center">
              <svg viewBox="0 0 24 24" className="w-6 h-6 text-emerald-300" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round"><path d="M5 12l5 5L20 7" /></svg>
            </div>
            <div>
              <div className="font-bold text-emerald-200">Nothing overdue.</div>
              <div className="text-sm text-[#8ea2d6]">Every new referral is within the 48-hour first-contact window. Every elevated BLL has a CLPPP referral. Every remediation with a displaced family has housing activated.</div>
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {alerts.slice(0, 8).map((a, i) => (
              <div key={i} className={`rounded-lg border p-4 flex items-start gap-3 ${
                a.severity === 'urgent' ? 'border-rose-700/50 bg-rose-950/30' :
                a.severity === 'high' ? 'border-[#f5c23e]/50 bg-[#f5c23e]/10' :
                'border-sky-700/50 bg-sky-950/30'
              }`}>
                <div className={`w-2 h-2 rounded-full mt-1.5 shrink-0 ${
                  a.severity === 'urgent' ? 'bg-rose-400' :
                  a.severity === 'high' ? 'bg-[#f5c23e]' : 'bg-sky-400'
                }`} />
                <div className="flex-1 min-w-0">
                  <div className="text-sm font-semibold text-slate-100 leading-snug">{a.message}</div>
                  <div className="text-[10px] text-[#8ea2d6] uppercase tracking-wider mt-1.5 font-bold">{a.type.replace(/_/g, ' ')}</div>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>

      {/* Referral Pipeline — cases grouped by stage */}
      <section>
        <SectionHeader
          eyebrow="Referral Pipeline"
          title="Where every family is right now"
          color="#3B82F6"
        />
        <StageFunnel counts={stageCounts} />
      </section>

      {/* Stat strip */}
      <section>
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-2">
          <StatCard label="New" value={summary.new_referrals ?? 0} tone="info" />
          <StatCard label="Active" value={summary.active_cases ?? 0} tone="ok" />
          <StatCard label="48hr Overdue" value={summary.overdue_follow_ups ?? 0} tone={summary.overdue_follow_ups ? 'alert' : 'neutral'} />
          <StatCard label="Pending Auth" value={summary.pending_authorizations ?? 0} tone={summary.pending_authorizations ? 'brand' : 'neutral'} />
          <StatCard label="Families" value={summary.total_families ?? 0} />
          <StatCard label="Children" value={summary.total_children ?? 0} />
          <StatCard label="EBL" value={summary.ebl_cases ?? 0} tone={summary.ebl_cases ? 'alert' : 'neutral'} />
        </div>
      </section>

      {/* Queue */}
      <section>
        <SectionHeader
          eyebrow="Priority Queue"
          title="Top cases by urgency + recency"
          color="#F5C23E"
          action={<button onClick={onJumpToQueue} className="text-xs font-bold text-[#f5c23e] hover:text-[#fcd75a]">Full queue →</button>}
        />
        {sortedQueue.length === 0 ? (
          <div className="bg-[#0a1a52]/40 border border-[#1c2f6a] rounded-xl p-8 text-center text-[#8ea2d6] text-sm">
            No referrals in queue. Submit a new intake or adjust filters.
          </div>
        ) : (
          <div className="bg-[#0a1a52]/40 border border-[#1c2f6a] rounded-xl overflow-hidden">
            <table className="w-full text-sm">
              <thead className="bg-[#081849]/80">
                <tr className="text-[10px] uppercase tracking-wider text-[#f5c23e]">
                  <th className="py-3 px-4 text-left font-bold">Family / Agency</th>
                  <th className="py-3 px-4 text-left font-bold">County</th>
                  <th className="py-3 px-4 text-left font-bold">Urgency</th>
                  <th className="py-3 px-4 text-left font-bold">Stage</th>
                  <th className="py-3 px-4 text-left font-bold">48hr SLA</th>
                  <th className="py-3 px-4"></th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#1c2f6a]/60">
                {sortedQueue.map((r) => (
                  <tr key={r.id} className="hover:bg-[#0f2468]/60 transition">
                    <td className="py-3 px-4">
                      <div className="font-semibold text-slate-100">{r.referring_agency || r.referral_source || '—'}</div>
                      <div className="text-xs text-[#8ea2d6]">{r.case_worker_name || ''}</div>
                    </td>
                    <td className="py-3 px-4 text-slate-300">{r.county || '—'}</td>
                    <td className="py-3 px-4">
                      <div className="flex items-center gap-2 flex-wrap">
                        <UrgencyPill urgency={r.urgency || 'Standard'} />
                        {r.sla?.auto_escalated && (
                          <span title={r.sla.escalated_reason || ''} className="inline-flex items-center gap-1 text-[9px] font-bold uppercase tracking-wider px-1.5 py-0.5 rounded border border-rose-600/60 bg-rose-950/50 text-rose-200">
                            <span className="w-1 h-1 rounded-full bg-rose-400" />Auto
                          </span>
                        )}
                      </div>
                    </td>
                    <td className="py-3 px-4"><StagePill stage={stageOf(r)} /></td>
                    <td className="py-3 px-4"><SLABar sla={r.sla} dateReceived={r.date_received} stage={stageOf(r)} compact /></td>
                    <td className="py-3 px-4 text-right">
                      <button onClick={() => onOpenCase(r.id)} className="text-xs font-black text-[#f5c23e] hover:text-[#fcd75a]">Open →</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
};

// ──────────────────────────────────────────────────────────────────────────
// REFERRALS
// ──────────────────────────────────────────────────────────────────────────
const ReferralsSection: React.FC<{
  referrals: ReferralRow[];
  filters: { status: string; county: string; urgency: string };
  onFiltersChange: (f: any) => void;
  onRefresh: () => void;
  onOpenCase: (id: string) => void;
  loading: boolean;
}> = ({ referrals, filters, onFiltersChange, onRefresh, onOpenCase, loading }) => {
  const selectCls = 'bg-[#081849] border border-[#1c2f6a] rounded-md px-3 py-1.5 text-sm text-slate-100 focus:border-[#f5c23e] focus:outline-none';
  const [stageFilter, setStageFilter] = useState<Stage | ''>('');
  const stageCounts = useMemo(() => {
    const counts: Record<Stage, number> = { Intake: 0, Triage: 0, Outreach: 0, Engaged: 0, 'In Service': 0, Closed: 0 };
    for (const r of referrals) counts[stageOf(r)] += 1;
    return counts;
  }, [referrals]);
  const filtered = useMemo(() => stageFilter ? referrals.filter(r => stageOf(r) === stageFilter) : referrals, [referrals, stageFilter]);

  return (
    <div className="space-y-4">
      {/* Pipeline — click a stage to filter */}
      <StageFunnel counts={stageCounts} onFilter={(s) => setStageFilter(stageFilter === s ? '' : s)} />

      {stageFilter && (
        <div className="flex items-center gap-2 text-xs">
          <span className="text-[#8ea2d6]">Filtered by stage:</span>
          <StagePill stage={stageFilter} />
          <button onClick={() => setStageFilter('')} className="text-[#f5c23e] hover:text-[#fcd75a] font-bold">Clear ×</button>
        </div>
      )}

      <div className="flex flex-wrap gap-3 items-center bg-[#0a1a52]/40 border border-[#1c2f6a] rounded-xl p-3">
        <select value={filters.status} onChange={(e) => onFiltersChange({ ...filters, status: e.target.value })} className={selectCls}>
          <option value="">All statuses</option>
          {['New', 'Assigned', 'Active', 'Pending', 'Completed', 'Closed'].map(s => <option key={s}>{s}</option>)}
        </select>
        <select value={filters.county} onChange={(e) => onFiltersChange({ ...filters, county: e.target.value })} className={selectCls}>
          <option value="">All counties</option>
          {COUNTIES.map(c => <option key={c}>{c}</option>)}
        </select>
        <select value={filters.urgency} onChange={(e) => onFiltersChange({ ...filters, urgency: e.target.value })} className={selectCls}>
          <option value="">All urgency</option>
          {URGENCY_LEVELS.map(u => <option key={u}>{u}</option>)}
        </select>
        <div className="ml-auto flex items-center gap-3">
          <span className="text-xs text-[#8ea2d6]">{filtered.length} matching</span>
          <button onClick={onRefresh} className="text-xs font-semibold text-slate-100 hover:text-white bg-[#081849] hover:bg-[#0f2468] border border-[#1c2f6a] rounded-md px-3 py-1.5">
            {loading ? 'Loading…' : 'Refresh'}
          </button>
        </div>
      </div>

      {filtered.length === 0 ? (
        <div className="bg-[#0a1a52]/40 border border-[#1c2f6a] rounded-xl p-12 text-center text-[#8ea2d6]">
          No referrals match the filter.
        </div>
      ) : (
        <div className="bg-[#0a1a52]/40 border border-[#1c2f6a] rounded-xl overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-[#081849]/80">
              <tr className="text-[10px] uppercase tracking-wider text-[#f5c23e]">
                <th className="py-3 px-4 text-left font-bold">Ref #</th>
                <th className="py-3 px-4 text-left font-bold">Source / Worker</th>
                <th className="py-3 px-4 text-left font-bold">County</th>
                <th className="py-3 px-4 text-left font-bold">Services</th>
                <th className="py-3 px-4 text-left font-bold">Urgency</th>
                <th className="py-3 px-4 text-left font-bold">Stage</th>
                <th className="py-3 px-4 text-left font-bold">48hr SLA</th>
                <th className="py-3 px-4"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#1c2f6a]/60">
              {filtered.map((r) => (
                <tr key={r.id} className="hover:bg-[#0f2468]/60 transition">
                  <td className="py-3 px-4 font-mono text-xs text-slate-300">{r.referral_id ?? r.id.slice(-6)}</td>
                  <td className="py-3 px-4">
                    <div className="font-semibold text-slate-100">{r.referring_agency || r.referral_source || '—'}</div>
                    <div className="text-xs text-[#8ea2d6]">{r.case_worker_name || ''}</div>
                    <div className="text-[10px] text-[#6b7ba6]">{r.date_received ? new Date(r.date_received).toLocaleDateString() : '—'}</div>
                  </td>
                  <td className="py-3 px-4 text-slate-300">{r.county || '—'}</td>
                  <td className="py-3 px-4">
                    <div className="flex flex-wrap gap-1">
                      {(r.services_requested || []).slice(0, 3).map((s: string, i: number) => (
                        <span key={i} className="inline-flex items-center gap-1 text-[10px] px-2 py-0.5 rounded border font-medium" style={{ borderColor: `${svcColor(s)}88`, color: svcColor(s), backgroundColor: `${svcColor(s)}18` }}>
                          <span className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: svcColor(s) }} />
                          {s}
                        </span>
                      ))}
                      {(r.services_requested || []).length > 3 && (
                        <span className="text-[10px] text-[#8ea2d6]">+{(r.services_requested || []).length - 3}</span>
                      )}
                    </div>
                  </td>
                  <td className="py-3 px-4">
                    <div className="flex items-center gap-2 flex-wrap">
                      <UrgencyPill urgency={r.urgency || 'Standard'} />
                      {r.sla?.auto_escalated && (
                        <span title={r.sla.escalated_reason || ''} className="inline-flex items-center gap-1 text-[9px] font-bold uppercase tracking-wider px-1.5 py-0.5 rounded border border-rose-600/60 bg-rose-950/50 text-rose-200">
                          <span className="w-1 h-1 rounded-full bg-rose-400" />Auto
                        </span>
                      )}
                      {r.sla?.source === 'override' && (
                        <span title={r.sla.override?.reason || ''} className="inline-flex items-center gap-1 text-[9px] font-bold uppercase tracking-wider px-1.5 py-0.5 rounded border border-[#f5c23e]/60 bg-[#f5c23e]/15 text-[#fcd75a]">
                          Override
                        </span>
                      )}
                    </div>
                  </td>
                  <td className="py-3 px-4"><StagePill stage={stageOf(r)} /></td>
                  <td className="py-3 px-4"><SLABar sla={r.sla} dateReceived={r.date_received} stage={stageOf(r)} compact /></td>
                  <td className="py-3 px-4 text-right">
                    <button onClick={() => onOpenCase(r.id)} className="text-xs font-black text-[#f5c23e] hover:text-[#fcd75a]">Open →</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

// ──────────────────────────────────────────────────────────────────────────
// CASE DETAIL PANEL
// ──────────────────────────────────────────────────────────────────────────
const CaseDetailPanel: React.FC<{
  caseDetail: any;
  onBack: () => void;
  onRefresh: () => void;
  onToast: (tone: 'ok' | 'err' | 'info', msg: string) => void;
  currentUser: CurrentUser | null;
}> = ({ caseDetail, onBack, onRefresh, onToast, currentUser }) => {
  const { referral, family, children, activations, milestones, billing } = caseDetail;
  const [noteText, setNoteText] = useState('');
  const [activating, setActivating] = useState(false);
  const [actForm, setActForm] = useState({
    service_line: 'NEMT',
    vendor: '',
    authorization_number: '',
    appointment_date: '',
    notes: '',
  });
  const [overrideOpen, setOverrideOpen] = useState(false);
  const canOverride = isSupervisor(currentUser);
  const hasOverride = referral?.sla?.source === 'override';

  const logNote = async () => {
    if (!noteText.trim()) return;
    try {
      await api.logShieldMilestone({
        referral_id: referral.id,
        family_id: family?.id,
        milestone_type: 'Family Contacted',
        recorded_by: 'Navigator',
        notes: noteText,
      });
      setNoteText('');
      onToast('ok', 'Contact logged');
      onRefresh();
    } catch (e: any) {
      onToast('err', `Failed: ${e.message}`);
    }
  };

  const submitActivation = async () => {
    try {
      const result: any = await api.activateShieldService({
        referral_id: referral.id,
        family_id: family?.id,
        ...actForm,
      });
      if (result?.success) {
        onToast('ok', `${actForm.service_line} activated${result.chained_activations?.length ? ` + ${result.chained_activations.join(', ')}` : ''}`);
        setActivating(false);
        setActForm({ service_line: 'NEMT', vendor: '', authorization_number: '', appointment_date: '', notes: '' });
        onRefresh();
      } else {
        onToast('err', result?.error || 'Activation failed');
      }
    } catch (e: any) {
      onToast('err', `Activation failed: ${e.message}`);
    }
  };

  const currentStage = stageOf(referral, milestones, activations);

  return (
    <div className="space-y-5">
      <div className="flex items-center gap-3">
        <button onClick={onBack} className="text-xs font-semibold text-[#8ea2d6] hover:text-white flex items-center gap-1.5">
          <span>←</span> All referrals
        </button>
        <span className="text-[#1c2f6a]">/</span>
        <span className="text-xs text-slate-200">Case #{referral.referral_id ?? referral.id.slice(-6)}</span>
      </div>

      {/* STAGE PIPELINE — where this family is in the flow */}
      <div>
        <div className="text-[10px] uppercase tracking-[0.25em] text-[#f5c23e] font-bold mb-2">Referral Stage</div>
        <StagePipeline current={currentStage} />
      </div>

      {/* CASE HERO */}
      <div className="bg-gradient-to-br from-[#0a1a52]/90 to-[#081849]/40 border border-[#1c2f6a] rounded-xl overflow-hidden">
        <div className="px-6 py-5 border-b border-[#1c2f6a] flex items-center justify-between flex-wrap gap-3">
          <div className="flex items-center gap-4 min-w-0">
            <div className="w-14 h-14 rounded-lg bg-gradient-to-br from-[#f5c23e] to-[#e0a92e] border border-[#fcd75a] flex items-center justify-center shrink-0 shadow-md">
              <svg viewBox="0 0 24 24" className="w-7 h-7 text-[#1f3fae]" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M12 2l8 3v7c0 5-3.5 9-8 10-4.5-1-8-5-8-10V5l8-3z" />
              </svg>
            </div>
            <div className="min-w-0">
              <div className="text-xs uppercase tracking-widest text-[#f5c23e] font-bold">Family</div>
              <div className="text-2xl font-black text-white truncate">{family?.family_name || 'Unnamed Family'}</div>
              <div className="text-xs text-[#8ea2d6] mt-0.5">
                {family?.address && <span>{family.address} · </span>}
                {family?.city} {family?.zip} {family?.county && <span>· {family.county} County</span>}
              </div>
            </div>
          </div>
          <div className="flex items-center gap-3 flex-wrap">
            <StatusPill status={referral.status || 'New'} />
            <UrgencyPill urgency={referral.urgency || 'Standard'} />
            <SLABar sla={referral.sla} dateReceived={referral.date_received} stage={currentStage} />
            {canOverride && (currentStage === 'Intake' || currentStage === 'Triage' || currentStage === 'Outreach') && (
              <button
                onClick={() => setOverrideOpen(true)}
                className={`text-[11px] font-black uppercase tracking-wider px-3 py-1.5 rounded-md border transition ${
                  hasOverride
                    ? 'bg-[#f5c23e] text-[#081849] border-[#fcd75a] hover:bg-[#fcd75a]'
                    : 'bg-[#0a1a52] text-[#f5c23e] border-[#f5c23e]/50 hover:bg-[#f5c23e]/10'
                }`}
                title={hasOverride ? 'Edit supervisor SLA override' : 'Set a supervisor SLA override'}
              >
                {hasOverride ? 'Edit SLA' : 'Override SLA'}
              </button>
            )}
          </div>
        </div>

        {/* SLA context — auto-escalation + override provenance */}
        {(referral?.sla?.auto_escalated || referral?.sla?.source === 'override') && (
          <div className="px-6 py-3 bg-[#050f2e]/70 border-b border-[#1c2f6a] flex items-center gap-3 flex-wrap">
            <SLAContextBadges sla={referral.sla} />
            {referral.sla?.auto_escalated && referral.sla?.escalated_reason && (
              <span className="text-[11px] text-[#8ea2d6]">{referral.sla.escalated_reason}</span>
            )}
            {referral.sla?.source === 'override' && referral.sla?.override && (
              <span className="text-[11px] text-[#8ea2d6]">
                Set by <span className="text-slate-200 font-semibold">{referral.sla.override.by || 'supervisor'}</span>
                {referral.sla.override.reason ? <>: <em>{referral.sla.override.reason}</em></> : null}
              </span>
            )}
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3">
          <div className="px-6 py-5 border-b lg:border-b-0 lg:border-r border-[#1c2f6a]">
            <div className="text-[10px] uppercase tracking-widest text-[#f5c23e] font-bold mb-3">Family Contact</div>
            <dl className="space-y-2 text-sm">
              <InfoRow label="Name" value={family?.primary_contact_name || '—'} />
              <InfoRow label="Phone" value={family?.primary_contact_phone || '—'} />
              <InfoRow label="Email" value={family?.primary_contact_email || '—'} />
              <InfoRow label="Language" value={family?.language || 'English'} />
            </dl>
            <div className="flex gap-2 mt-4">
              {family?.medicaid_enrolled && <ProgramChip tone="ok">Medicaid</ProgramChip>}
              {family?.snap_enrolled && <ProgramChip tone="info">SNAP</ProgramChip>}
              {!family?.medicaid_enrolled && !family?.snap_enrolled && <span className="text-[10px] text-[#6b7ba6] italic">No programs on file</span>}
            </div>
          </div>

          <div className="px-6 py-5 border-b lg:border-b-0 lg:border-r border-[#1c2f6a]">
            <div className="text-[10px] uppercase tracking-widest text-[#f5c23e] font-bold mb-3">Referral Source</div>
            <dl className="space-y-2 text-sm">
              <InfoRow label="Agency" value={referral.referring_agency || referral.referral_source || '—'} />
              <InfoRow label="Case worker" value={referral.case_worker_name || '—'} />
              <InfoRow label="Email" value={referral.case_worker_email || '—'} />
              <InfoRow label="Phone" value={referral.case_worker_phone || '—'} />
              <InfoRow label="Received" value={referral.date_received ? new Date(referral.date_received).toLocaleString() : '—'} />
            </dl>
          </div>

          <div className="px-6 py-5">
            <div className="text-[10px] uppercase tracking-widest text-[#f5c23e] font-bold mb-3 flex items-center justify-between">
              <span>Children ({children.length})</span>
            </div>
            {children.length === 0 ? (
              <div className="text-xs text-[#6b7ba6] italic">No children recorded</div>
            ) : (
              <div className="space-y-2">
                {children.map((c: any) => (
                  <div key={c.id} className="border border-[#1c2f6a] rounded-md p-2.5 bg-[#081849]/50">
                    <div className="flex items-center justify-between mb-1">
                      <div className="font-semibold text-sm text-slate-100">{c.child_name || 'Unnamed'}</div>
                      <div className="text-[10px] text-[#8ea2d6]">{c.age_months ?? '—'} mo</div>
                    </div>
                    <div className="flex items-center gap-2 text-[11px]">
                      <span className="text-[#8ea2d6]">{c.lead_test_status || 'Not Tested'}</span>
                      {c.blood_lead_level != null && (
                        <span className={`font-mono font-bold ${(c.blood_lead_level ?? 0) >= 3.5 ? 'text-rose-300' : 'text-slate-200'}`}>
                          {c.blood_lead_level} µg/dL
                        </span>
                      )}
                    </div>
                    <div className="text-[10px] text-[#8ea2d6] mt-0.5">
                      CLPPP: {c.clppp_status || 'Not Referred'}{c.clppp_case_number ? ` · #${c.clppp_case_number}` : ''}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* SERVICES + TIMELINE */}
      <div className="grid grid-cols-1 lg:grid-cols-5 gap-5">
        <div className="lg:col-span-3 bg-[#0a1a52]/40 border border-[#1c2f6a] rounded-xl">
          <div className="px-5 py-4 border-b border-[#1c2f6a] flex items-center justify-between">
            <div>
              <div className="text-[10px] uppercase tracking-widest text-[#f5c23e] font-bold">Service Activations</div>
              <div className="text-base font-black text-white mt-0.5">{activations.length} line{activations.length === 1 ? '' : 's'}</div>
            </div>
            <button
              onClick={() => setActivating(!activating)}
              className="bg-[#f5c23e] hover:bg-[#fcd75a] text-[#081849] text-sm font-black px-3 py-1.5 rounded-md"
            >
              {activating ? 'Cancel' : '+ Activate'}
            </button>
          </div>

          {activating && (
            <div className="px-5 py-4 bg-[#f5c23e]/5 border-b border-[#f5c23e]/30 space-y-3">
              <div className="grid grid-cols-2 gap-3">
                <Field label="Service line">
                  <select className={inputCls} value={actForm.service_line} onChange={(e) => setActForm({ ...actForm, service_line: e.target.value })}>
                    {['NEMT', 'Lead Remediation', 'Housing', 'Drug Testing', 'DNA', 'Food Navigation', 'Specimen Transport', 'Filter Safety Net', 'Lead Screening', 'Medical Monitoring'].map(s => <option key={s}>{s}</option>)}
                  </select>
                </Field>
                <Field label="Vendor">
                  <input className={inputCls} value={actForm.vendor} onChange={(e) => setActForm({ ...actForm, vendor: e.target.value })} placeholder="Uber Health, Quest, Extended Stay…" />
                </Field>
                <Field label="Authorization #">
                  <input className={inputCls} value={actForm.authorization_number} onChange={(e) => setActForm({ ...actForm, authorization_number: e.target.value })} />
                </Field>
                <Field label="Appointment">
                  <input type="datetime-local" className={inputCls} value={actForm.appointment_date} onChange={(e) => setActForm({ ...actForm, appointment_date: e.target.value })} />
                </Field>
              </div>
              <textarea
                value={actForm.notes}
                onChange={(e) => setActForm({ ...actForm, notes: e.target.value })}
                placeholder="Activation notes…"
                rows={2}
                className={inputCls}
              />
              <div className="flex justify-end">
                <button onClick={submitActivation} className="bg-[#f5c23e] hover:bg-[#fcd75a] text-[#081849] px-4 py-2 rounded-md text-sm font-black">
                  Activate service
                </button>
              </div>
            </div>
          )}

          {activations.length === 0 ? (
            <div className="px-5 py-10 text-center text-[#8ea2d6] text-sm">No services activated yet.</div>
          ) : (
            <div className="divide-y divide-[#1c2f6a]/60">
              {activations.map((a: any) => (
                <div key={a.id} className="px-5 py-3 flex items-center justify-between gap-3">
                  <div className="min-w-0">
                    <div className="flex items-center gap-2 text-sm font-bold text-slate-100">
                      <span className="w-2.5 h-2.5 rounded-full shrink-0" style={{ backgroundColor: svcColor(a.service_line || '') }} />
                      {a.service_line}
                    </div>
                    <div className="text-xs text-[#8ea2d6] ml-[18px]">
                      {a.vendor || 'Vendor TBD'}{a.authorization_number ? ` · Auth ${a.authorization_number}` : ''}
                    </div>
                    {a.appointment_date && <div className="text-xs text-sky-300 mt-0.5">{new Date(a.appointment_date).toLocaleString()}</div>}
                  </div>
                  <StatusPill status={a.status || 'Pending'} />
                </div>
              ))}
            </div>
          )}

          {billing.length > 0 && (
            <div className="px-5 py-4 border-t border-[#1c2f6a]">
              <div className="text-[10px] uppercase tracking-widest text-[#f5c23e] font-bold mb-2">Billing</div>
              <div className="space-y-1.5">
                {billing.map((b: any) => (
                  <div key={b.id} className="flex items-center justify-between text-xs">
                    <span className="text-[#8ea2d6]">{b.service_line} · {b.payer_name || b.payer}</span>
                    <div className="flex items-center gap-2">
                      <StatusPill status={b.status || 'Pending'} />
                      <span className="font-mono text-slate-200">${(b.amount || 0).toLocaleString()}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        <div className="lg:col-span-2 bg-[#0a1a52]/40 border border-[#1c2f6a] rounded-xl">
          <div className="px-5 py-4 border-b border-[#1c2f6a]">
            <div className="text-[10px] uppercase tracking-widest text-[#f5c23e] font-bold">Case Timeline</div>
            <div className="text-base font-black text-white mt-0.5">{milestones.length} event{milestones.length === 1 ? '' : 's'}</div>
          </div>
          <div className="px-5 py-4">
            {milestones.length === 0 ? (
              <div className="text-sm text-[#8ea2d6] text-center py-6">No milestones yet</div>
            ) : (
              <ol className="space-y-3">
                {milestones.map((m: any) => (
                  <li key={m.id} className="flex gap-3">
                    <div className="flex flex-col items-center">
                      <div className="w-2 h-2 rounded-full bg-[#f5c23e] mt-1.5" />
                      <div className="w-px flex-1 bg-[#1c2f6a] mt-1" />
                    </div>
                    <div className="flex-1 min-w-0 pb-2">
                      <div className="text-sm font-semibold text-slate-100">{m.milestone_type}</div>
                      <div className="text-[10px] text-[#8ea2d6] uppercase tracking-wider mt-0.5">
                        {m.timestamp ? new Date(m.timestamp).toLocaleString() : '—'} · {m.recorded_by || 'System'}
                      </div>
                      {m.notes && <div className="text-xs text-slate-300 mt-1">{m.notes}</div>}
                    </div>
                  </li>
                ))}
              </ol>
            )}
          </div>
          <div className="px-5 py-4 border-t border-[#1c2f6a]">
            <div className="text-[10px] uppercase tracking-widest text-[#f5c23e] font-bold mb-2">Log Contact</div>
            <textarea
              value={noteText}
              onChange={(e) => setNoteText(e.target.value)}
              placeholder="Called mom at 10:30am, confirmed Friday appointment…"
              rows={3}
              className={inputCls}
            />
            <div className="flex justify-end mt-2">
              <button
                onClick={logNote}
                disabled={!noteText.trim()}
                className="bg-[#f5c23e] hover:bg-[#fcd75a] disabled:bg-[#1c2f6a] disabled:text-[#6b7ba6] disabled:cursor-not-allowed text-[#081849] px-3 py-1.5 rounded-md text-xs font-black"
              >
                Log milestone
              </button>
            </div>
          </div>
        </div>
      </div>

      {overrideOpen && (
        <SLAOverrideModal
          currentSla={referral?.sla}
          currentUser={currentUser}
          referralId={referral.id}
          referralRef={referral.referral_id ?? referral.id?.slice(-6)}
          onClose={() => setOverrideOpen(false)}
          onSaved={() => { setOverrideOpen(false); onRefresh(); }}
          onToast={onToast}
        />
      )}
    </div>
  );
};

// ──────────────────────────────────────────────────────────────────────────
// SLA Override Modal — supervisor / admin only
// ──────────────────────────────────────────────────────────────────────────
const SLA_PRESETS: { label: string; hours: number; hint: string }[] = [
  { label: '24h — Emergency', hours: 24,  hint: 'Confirmed EBL, displacement, crisis' },
  { label: '48h — Urgent',    hours: 48,  hint: 'Elevated BLL or confirmed lead hazard' },
  { label: '5 business days', hours: 120, hint: 'Screening referral, no confirmed exposure' },
  { label: '10 business days', hours: 240, hint: 'Non-urgent downstream coordination' },
];

const SLAOverrideModal: React.FC<{
  currentSla?: SLASnapshot;
  currentUser: CurrentUser | null;
  referralId: string;
  referralRef: string | number;
  onClose: () => void;
  onSaved: () => void;
  onToast: (tone: 'ok' | 'err' | 'info', msg: string) => void;
}> = ({ currentSla, currentUser, referralId, referralRef, onClose, onSaved, onToast }) => {
  const existing = currentSla?.source === 'override';
  const [hours, setHours] = useState<number>(existing && currentSla?.override?.hours
    ? Math.round(currentSla.override.hours)
    : SLA_PRESETS[1].hours);
  const [reason, setReason] = useState<string>(existing ? (currentSla?.override?.reason || '') : '');
  const [saving, setSaving] = useState(false);

  if (!currentUser) return null;

  const save = async (clear = false) => {
    if (!clear && !reason.trim()) {
      onToast('err', 'Reason is required when setting an override.');
      return;
    }
    try {
      setSaving(true);
      const result: any = await api.overrideShieldSLA(referralId, {
        user_email: currentUser.email,
        target_hours: clear ? null : hours,
        reason: clear ? '' : reason.trim(),
      });
      if (result?.success) {
        onToast('ok', clear ? 'SLA override cleared.' : `SLA overridden to ${hours}h.`);
        onSaved();
      } else {
        onToast('err', result?.error || 'Override failed.');
      }
    } catch (e: any) {
      onToast('err', `Override failed: ${e.message || 'unknown'}`);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-6" onClick={onClose}>
      <div
        className="bg-[#081849] border border-[#f5c23e]/60 rounded-xl w-full max-w-lg shadow-2xl overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="bg-[#f5c23e] px-5 py-3 flex items-center justify-between">
          <div>
            <div className="text-[10px] uppercase tracking-[0.22em] text-[#081849]/70 font-black">Supervisor action · Case #{referralRef}</div>
            <div className="text-lg font-black text-[#081849]">{existing ? 'Edit SLA override' : 'Override first-contact SLA'}</div>
          </div>
          <button onClick={onClose} className="text-[#081849] hover:text-[#1f3fae] font-black text-xl leading-none">×</button>
        </div>

        <div className="px-5 py-5 space-y-5">
          <div>
            <div className="text-[10px] uppercase tracking-wider text-[#8ea2d6] font-bold mb-1">Acting as</div>
            <div className="text-sm text-slate-100 font-semibold">{currentUser.name || currentUser.email}</div>
            <div className="text-[11px] text-[#8ea2d6]">{currentUser.role} · {currentUser.email}</div>
          </div>

          <div>
            <div className="text-[10px] uppercase tracking-wider text-[#8ea2d6] font-bold mb-2">New target</div>
            <div className="grid grid-cols-2 gap-2 mb-3">
              {SLA_PRESETS.map((p) => (
                <button
                  key={p.hours}
                  onClick={() => setHours(p.hours)}
                  className={`text-left px-3 py-2 rounded-md border transition ${
                    hours === p.hours
                      ? 'bg-[#f5c23e]/15 border-[#f5c23e] text-white'
                      : 'bg-[#0a1a52] border-[#1c2f6a] text-slate-300 hover:border-[#3b4a80]'
                  }`}
                >
                  <div className="text-xs font-black">{p.label}</div>
                  <div className="text-[10px] text-[#8ea2d6]">{p.hint}</div>
                </button>
              ))}
            </div>
            <label className="block">
              <span className="block text-[10px] uppercase tracking-wider text-[#8ea2d6] font-bold mb-1">Custom hours</span>
              <input
                type="number"
                min={1}
                max={720}
                value={hours}
                onChange={(e) => setHours(Number(e.target.value) || 0)}
                className="w-full bg-[#0a1a52] border border-[#1c2f6a] rounded-md px-3 py-2 text-sm text-slate-100 focus:border-[#f5c23e] focus:ring-1 focus:ring-[#f5c23e]/40 focus:outline-none"
              />
            </label>
          </div>

          <div>
            <div className="text-[10px] uppercase tracking-wider text-[#8ea2d6] font-bold mb-1">Reason (required)</div>
            <textarea
              rows={3}
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              placeholder="e.g. Family requested weekend outreach; remediation contractor unavailable until Monday; mom en route to ER with confirmed EBL so standard 48h clock is restarting on discharge."
              className="w-full bg-[#0a1a52] border border-[#1c2f6a] rounded-md px-3 py-2 text-sm text-slate-100 focus:border-[#f5c23e] focus:ring-1 focus:ring-[#f5c23e]/40 focus:outline-none resize-none"
            />
            <div className="text-[10px] text-[#8ea2d6] mt-1.5 italic">
              Reason is logged as a Case Milestone — permanent audit trail.
            </div>
          </div>
        </div>

        <div className="bg-[#050f2e] border-t border-[#1c2f6a] px-5 py-3 flex items-center justify-between gap-3">
          {existing ? (
            <button
              onClick={() => save(true)}
              disabled={saving}
              className="text-xs font-bold text-rose-300 hover:text-rose-200 disabled:opacity-50"
            >
              Clear override
            </button>
          ) : <span />}
          <div className="flex items-center gap-2">
            <button
              onClick={onClose}
              className="text-xs font-bold text-[#8ea2d6] hover:text-white px-3 py-2"
            >
              Cancel
            </button>
            <button
              onClick={() => save(false)}
              disabled={saving || !reason.trim() || hours <= 0}
              className="bg-[#f5c23e] hover:bg-[#fcd75a] disabled:bg-[#1c2f6a] disabled:text-[#6b7ba6] text-[#081849] font-black text-xs px-4 py-2 rounded-md disabled:cursor-not-allowed"
            >
              {saving ? 'Saving…' : existing ? 'Update override' : 'Set override'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

const InfoRow: React.FC<{ label: string; value: string }> = ({ label, value }) => (
  <div className="flex gap-3">
    <dt className="text-[10px] uppercase tracking-wider text-[#8ea2d6] font-bold min-w-[70px] pt-0.5">{label}</dt>
    <dd className="text-sm text-slate-100 flex-1 min-w-0 break-words">{value}</dd>
  </div>
);

const ProgramChip: React.FC<{ tone: 'ok' | 'info'; children: React.ReactNode }> = ({ tone, children }) => (
  <span className={`text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded border ${
    tone === 'ok' ? 'bg-emerald-950/60 border-emerald-700/60 text-emerald-200' : 'bg-sky-950/60 border-sky-700/60 text-sky-200'
  }`}>{children}</span>
);

const inputCls = 'w-full bg-[#081849] border border-[#1c2f6a] rounded-md px-3 py-2 text-sm text-slate-100 placeholder:text-[#6b7ba6] focus:border-[#f5c23e] focus:outline-none';

const Field: React.FC<{ label: string; children: React.ReactNode; hint?: string }> = ({ label, children, hint }) => (
  <label className="block">
    <span className="block text-[10px] uppercase tracking-wider text-[#f5c23e] font-bold mb-1">{label}</span>
    {children}
    {hint && <span className="block text-[10px] text-[#6b7ba6] mt-1">{hint}</span>}
  </label>
);

// ──────────────────────────────────────────────────────────────────────────
// INTAKE WIZARD — CWC-forward external-facing face
// ──────────────────────────────────────────────────────────────────────────
const INTAKE_STEPS = [
  { id: 1, label: 'Referring Party', hint: 'Who is sending this family to us' },
  { id: 2, label: 'Family', hint: 'Household & contact information' },
  { id: 3, label: 'Children', hint: 'Lead screening status per child' },
  { id: 4, label: 'Services', hint: 'What the family needs' },
  { id: 5, label: 'Review', hint: 'Urgency, notes, submit' },
];

const IntakeWizard: React.FC<{ onSuccess: (ref: string) => void; onError: (msg: string) => void }> = ({ onSuccess, onError }) => {
  const [step, setStep] = useState(1);
  const [submitting, setSubmitting] = useState(false);
  const [form, setForm] = useState<any>({
    referral_source: 'MDHHS',
    referring_agency: '',
    case_worker_name: '',
    case_worker_email: '',
    case_worker_phone: '',
    county: 'Wayne',
    family_name: '',
    address: '',
    city: '',
    zip: '',
    primary_contact_name: '',
    primary_contact_phone: '',
    primary_contact_email: '',
    language: 'English',
    medicaid_enrolled: false,
    snap_enrolled: false,
    children: [{ child_name: '', age_months: '', lead_test_status: 'Not Tested', blood_lead_level: '', clppp_case_number: '' }],
    services_requested: [] as string[],
    urgency: 'Standard',
    notes: '',
    intake_method: 'Web Form',
  });

  const set = (k: string, v: any) => setForm((f: any) => ({ ...f, [k]: v }));
  const toggleService = (svc: string) => setForm((f: any) => ({
    ...f,
    services_requested: f.services_requested.includes(svc)
      ? f.services_requested.filter((s: string) => s !== svc)
      : [...f.services_requested, svc],
  }));
  const updChild = (i: number, k: string, v: any) => setForm((f: any) => ({
    ...f, children: f.children.map((c: any, idx: number) => idx === i ? { ...c, [k]: v } : c),
  }));
  const addChild = () => setForm((f: any) => ({
    ...f, children: [...f.children, { child_name: '', age_months: '', lead_test_status: 'Not Tested', blood_lead_level: '', clppp_case_number: '' }],
  }));
  const removeChild = (i: number) => setForm((f: any) => ({ ...f, children: f.children.filter((_: any, idx: number) => idx !== i) }));

  const canAdvance = useMemo(() => {
    if (step === 1) return !!form.case_worker_name && !!form.case_worker_email && !!form.county;
    if (step === 4) return form.services_requested.length > 0;
    return true;
  }, [step, form]);

  const submit = async () => {
    try {
      setSubmitting(true);
      const result: any = await api.createShieldReferral(form);
      if (result?.success) {
        onSuccess(String(result.case_number ?? result.reference_number ?? result.referral_id ?? 'new'));
      } else {
        onError(result?.error || 'Submission failed');
      }
    } catch (e: any) {
      onError(`Submission failed: ${e.message}`);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      {/* CWC-forward banner — real logo */}
      <div className="bg-gradient-to-br from-[#f5c23e] via-[#fcd75a] to-[#f5c23e] border border-[#fcd75a] rounded-xl p-6 mb-5 shadow-lg">
        <div className="flex items-center justify-between flex-wrap gap-4">
          <div className="flex items-center gap-4 min-w-0">
            <img src="/cwc-logo.png" alt="Cause We Care" className="w-20 h-20 rounded-lg object-contain shrink-0 bg-white/30 p-1" />
            <div className="min-w-0">
              <div className="text-[10px] uppercase tracking-[0.25em] text-[#1f3fae]/70 font-black">MDHHS Referral Intake</div>
              <div className="text-2xl font-black text-[#1f3fae] leading-tight">
                Refer a Michigan family — we'll take it from here.
              </div>
              <div className="text-[10px] uppercase tracking-wider text-[#f5c23e] font-black mt-1">Care. Navigate. Transform.</div>
              <div className="text-xs text-[#1f3fae]/80 mt-1 max-w-xl">
                A CWC/DDI navigator will reach out within <strong>48 hours</strong>. No SSN or full date of birth collected — HIPAA compliant. Michigan Public Act 146 of 2023.
              </div>
              <a
                href="/refer"
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center gap-1.5 mt-2 text-xs font-black text-[#1f3fae] hover:text-[#0a1f6e] bg-white/40 hover:bg-white/60 border border-[#1f3fae]/30 rounded-md px-2.5 py-1"
              >
                Open public referrer URL ↗
              </a>
            </div>
          </div>
          <div className="shrink-0 flex items-center gap-2 bg-white/40 border border-[#1f3fae]/20 rounded-lg p-2">
            <img src="/ddi-logo.png" alt="DEE DAVIS INC" className="h-14 object-contain" />
          </div>
        </div>
      </div>

      {/* Progress */}
      <div className="flex items-center gap-2 mb-6">
        {INTAKE_STEPS.map((s, i) => {
          const active = step === s.id;
          const done = step > s.id;
          return (
            <React.Fragment key={s.id}>
              <button
                onClick={() => done && setStep(s.id)}
                disabled={!done && !active}
                className={`flex-1 rounded-lg border px-3 py-2.5 text-left transition ${
                  active ? 'bg-[#f5c23e]/10 border-[#f5c23e] shadow-[0_0_0_1px_rgba(245,194,62,0.3)]' :
                  done ? 'bg-[#0a1a52]/60 border-[#1c2f6a] hover:border-[#f5c23e]/50 cursor-pointer' :
                  'bg-[#0a1a52]/30 border-[#1c2f6a] opacity-60'
                }`}
              >
                <div className="flex items-center gap-2">
                  <div className={`w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-black ${
                    active ? 'bg-[#f5c23e] text-[#081849]' :
                    done ? 'bg-[#0a1a52] text-[#f5c23e] border border-[#f5c23e]/60' :
                    'bg-[#081849] text-[#6b7ba6]'
                  }`}>
                    {done ? '✓' : s.id}
                  </div>
                  <div className="text-[10px] uppercase tracking-wider font-bold text-slate-200">{s.label}</div>
                </div>
                <div className="text-[10px] text-[#8ea2d6] mt-1">{s.hint}</div>
              </button>
              {i < INTAKE_STEPS.length - 1 && <div className="w-4 h-px bg-[#1c2f6a]" />}
            </React.Fragment>
          );
        })}
      </div>

      <div className="bg-[#0a1a52]/40 border border-[#1c2f6a] rounded-xl p-6">
        {step === 1 && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Field label="Referral source *">
              <select className={inputCls} value={form.referral_source} onChange={(e) => set('referral_source', e.target.value)}>
                {['MDHHS', 'County Health Dept', 'Self', 'Other'].map(s => <option key={s}>{s}</option>)}
              </select>
            </Field>
            <Field label="Referring agency">
              <input className={inputCls} value={form.referring_agency} onChange={(e) => set('referring_agency', e.target.value)} placeholder="e.g. Wayne County Health Dept" />
            </Field>
            <Field label="Your full name *">
              <input className={inputCls} value={form.case_worker_name} onChange={(e) => set('case_worker_name', e.target.value)} />
            </Field>
            <Field label="Your email *">
              <input type="email" className={inputCls} value={form.case_worker_email} onChange={(e) => set('case_worker_email', e.target.value)} />
            </Field>
            <Field label="Your phone">
              <input className={inputCls} value={form.case_worker_phone} onChange={(e) => set('case_worker_phone', e.target.value)} />
            </Field>
            <Field label="County the family lives in *">
              <select className={inputCls} value={form.county} onChange={(e) => set('county', e.target.value)}>
                {COUNTIES.map(c => <option key={c}>{c}</option>)}
              </select>
            </Field>
          </div>
        )}

        {step === 2 && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Field label="Family last name"><input className={inputCls} value={form.family_name} onChange={(e) => set('family_name', e.target.value)} /></Field>
            <Field label="Primary language">
              <select className={inputCls} value={form.language} onChange={(e) => set('language', e.target.value)}>
                {['English', 'Spanish', 'Arabic', 'Other'].map(l => <option key={l}>{l}</option>)}
              </select>
            </Field>
            <Field label="Street address"><input className={inputCls} value={form.address} onChange={(e) => set('address', e.target.value)} /></Field>
            <Field label="City"><input className={inputCls} value={form.city} onChange={(e) => set('city', e.target.value)} /></Field>
            <Field label="ZIP"><input className={inputCls} value={form.zip} onChange={(e) => set('zip', e.target.value)} /></Field>
            <div />
            <Field label="Primary contact name"><input className={inputCls} value={form.primary_contact_name} onChange={(e) => set('primary_contact_name', e.target.value)} /></Field>
            <Field label="Primary contact phone"><input className={inputCls} value={form.primary_contact_phone} onChange={(e) => set('primary_contact_phone', e.target.value)} /></Field>
            <Field label="Primary contact email"><input className={inputCls} value={form.primary_contact_email} onChange={(e) => set('primary_contact_email', e.target.value)} /></Field>
            <div className="flex items-end gap-5 pt-1">
              <label className="flex items-center gap-2 text-sm text-slate-200 cursor-pointer">
                <input type="checkbox" checked={form.medicaid_enrolled} onChange={(e) => set('medicaid_enrolled', e.target.checked)} className="accent-[#f5c23e]" />
                Medicaid enrolled
              </label>
              <label className="flex items-center gap-2 text-sm text-slate-200 cursor-pointer">
                <input type="checkbox" checked={form.snap_enrolled} onChange={(e) => set('snap_enrolled', e.target.checked)} className="accent-[#f5c23e]" />
                SNAP enrolled
              </label>
            </div>
          </div>
        )}

        {step === 3 && (
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <div className="text-sm text-[#8ea2d6]">Add one row per child. First name only (HIPAA).</div>
              <button onClick={addChild} className="text-xs font-black text-[#f5c23e] hover:text-[#fcd75a] border border-[#f5c23e]/50 bg-[#f5c23e]/10 px-3 py-1.5 rounded-md">
                + Add another child
              </button>
            </div>
            {form.children.map((child: any, i: number) => (
              <div key={i} className="border border-[#1c2f6a] rounded-lg p-4 bg-[#081849]/50">
                <div className="flex items-center justify-between mb-3">
                  <div className="text-[10px] uppercase tracking-widest text-[#f5c23e] font-bold">Child {i + 1}</div>
                  {form.children.length > 1 && (
                    <button onClick={() => removeChild(i)} className="text-[10px] text-rose-400 hover:text-rose-300 uppercase tracking-wider font-bold">Remove</button>
                  )}
                </div>
                <div className="grid grid-cols-1 md:grid-cols-5 gap-3">
                  <Field label="First name"><input className={inputCls} value={child.child_name} onChange={(e) => updChild(i, 'child_name', e.target.value)} /></Field>
                  <Field label="Age (months)"><input type="number" className={inputCls} value={child.age_months} onChange={(e) => updChild(i, 'age_months', e.target.value)} /></Field>
                  <Field label="Test status">
                    <select className={inputCls} value={child.lead_test_status} onChange={(e) => updChild(i, 'lead_test_status', e.target.value)}>
                      {['Not Tested', 'Tested - Normal', 'Tested - Elevated', 'Confirmed EBL'].map(s => <option key={s}>{s}</option>)}
                    </select>
                  </Field>
                  <Field label="BLL (µg/dL)"><input type="number" step="0.1" className={inputCls} value={child.blood_lead_level} onChange={(e) => updChild(i, 'blood_lead_level', e.target.value)} /></Field>
                  <Field label="CLPPP case #"><input className={inputCls} value={child.clppp_case_number} onChange={(e) => updChild(i, 'clppp_case_number', e.target.value)} /></Field>
                </div>
              </div>
            ))}
          </div>
        )}

        {step === 4 && (
          <div>
            <div className="text-sm text-[#8ea2d6] mb-3">Select all services the family needs. Activation chains will auto-trigger (e.g., Remediation + Housing if family is displaced).</div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
              {SERVICE_CHOICES.map(svc => {
                const on = form.services_requested.includes(svc);
                const hex = svcColor(svc);
                return (
                  <label
                    key={svc}
                    className={`flex items-center gap-3 border rounded-md px-3 py-2.5 cursor-pointer transition ${
                      on ? '' : 'bg-[#081849]/50 border-[#1c2f6a] text-slate-200 hover:border-[#1c2f6a]'
                    }`}
                    style={on ? { borderColor: hex, backgroundColor: `${hex}18`, color: hex } : undefined}
                  >
                    <input type="checkbox" checked={on} onChange={() => toggleService(svc)} style={{ accentColor: hex }} />
                    <span className="flex items-center gap-2 text-sm font-medium">
                      <span className="w-2 h-2 rounded-full shrink-0" style={{ backgroundColor: hex }} />
                      {svc}
                    </span>
                  </label>
                );
              })}
            </div>
          </div>
        )}

        {step === 5 && (
          <div className="space-y-5">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Field label="Urgency">
                <select className={inputCls} value={form.urgency} onChange={(e) => set('urgency', e.target.value)}>
                  {URGENCY_LEVELS.map(u => <option key={u}>{u}</option>)}
                </select>
              </Field>
              <div />
            </div>
            <Field label="Additional notes / Best time to reach family">
              <textarea className={inputCls} rows={4} value={form.notes} onChange={(e) => set('notes', e.target.value)} />
            </Field>

            <div className="bg-[#081849]/70 border border-[#1c2f6a] rounded-lg p-4">
              <div className="text-[10px] uppercase tracking-widest text-[#f5c23e] font-bold mb-2">Review</div>
              <dl className="grid grid-cols-1 md:grid-cols-2 gap-y-1 gap-x-6 text-xs">
                <InfoRow label="Source" value={form.referring_agency || form.referral_source} />
                <InfoRow label="Case worker" value={form.case_worker_name || '—'} />
                <InfoRow label="Family" value={form.family_name || '—'} />
                <InfoRow label="County" value={form.county} />
                <InfoRow label="Children" value={`${form.children.length}`} />
                <div className="col-span-full">
                  <dt className="text-[10px] uppercase tracking-wider text-[#8ea2d6] font-semibold">Services</dt>
                  {form.services_requested.length ? (
                    <dd className="flex flex-wrap gap-1.5 mt-1">
                      {form.services_requested.map((s: string) => (
                        <span key={s} className="inline-flex items-center gap-1 text-[10px] font-medium rounded-full px-2 py-0.5 border" style={{ borderColor: `${svcColor(s)}66`, color: svcColor(s), backgroundColor: `${svcColor(s)}18` }}>
                          <span className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: svcColor(s) }} />
                          {s}
                        </span>
                      ))}
                    </dd>
                  ) : (
                    <dd className="text-xs text-slate-400">—</dd>
                  )}
                </div>
                <InfoRow label="Medicaid" value={form.medicaid_enrolled ? 'Yes' : 'No'} />
                <InfoRow label="SNAP" value={form.snap_enrolled ? 'Yes' : 'No'} />
              </dl>
            </div>
          </div>
        )}
      </div>

      {/* Wizard footer */}
      <div className="flex items-center justify-between mt-5">
        <button
          onClick={() => setStep(Math.max(1, step - 1))}
          disabled={step === 1}
          className="text-sm font-semibold text-slate-200 hover:text-white disabled:text-[#3b4a80] disabled:cursor-not-allowed"
        >
          ← Back
        </button>
        <div className="text-xs text-[#8ea2d6]">Step {step} of {INTAKE_STEPS.length}</div>
        {step < INTAKE_STEPS.length ? (
          <button
            onClick={() => canAdvance && setStep(step + 1)}
            disabled={!canAdvance}
            className="bg-[#f5c23e] hover:bg-[#fcd75a] disabled:bg-[#1c2f6a] disabled:text-[#6b7ba6] disabled:cursor-not-allowed text-[#081849] text-sm font-black px-5 py-2 rounded-md"
          >
            Continue →
          </button>
        ) : (
          <button
            onClick={submit}
            disabled={submitting}
            className="bg-[#f5c23e] hover:bg-[#fcd75a] disabled:opacity-60 text-[#081849] text-sm font-black px-5 py-2 rounded-md"
          >
            {submitting ? 'Submitting…' : 'Submit referral'}
          </button>
        )}
      </div>
    </div>
  );
};

// ──────────────────────────────────────────────────────────────────────────
// List sections
// ──────────────────────────────────────────────────────────────────────────
const FamiliesSection: React.FC<{ families: any[] }> = ({ families }) => (
  <div className="bg-[#0a1a52]/40 border border-[#1c2f6a] rounded-xl overflow-hidden">
    {families.length === 0 ? (
      <div className="p-12 text-center text-[#8ea2d6] text-sm">No families yet. Submit an intake to create the first record.</div>
    ) : (
      <table className="w-full text-sm">
        <thead className="bg-[#081849]/80">
          <tr className="text-[10px] uppercase tracking-wider text-[#f5c23e]">
            <th className="py-3 px-4 text-left font-bold">Family</th>
            <th className="py-3 px-4 text-left font-bold">County</th>
            <th className="py-3 px-4 text-left font-bold">Contact</th>
            <th className="py-3 px-4 text-left font-bold">Programs</th>
            <th className="py-3 px-4 text-left font-bold">Status</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-[#1c2f6a]/60">
          {families.map((f) => (
            <tr key={f.id} className="hover:bg-[#0f2468]/60">
              <td className="py-3 px-4 font-semibold">{f.family_name || '—'}</td>
              <td className="py-3 px-4 text-slate-300">{f.county || '—'}</td>
              <td className="py-3 px-4">
                <div className="text-sm">{f.primary_contact_name}</div>
                <div className="text-xs text-[#8ea2d6]">{f.primary_contact_phone}</div>
              </td>
              <td className="py-3 px-4">
                <div className="flex gap-1.5">
                  {f.medicaid_enrolled && <ProgramChip tone="ok">Medicaid</ProgramChip>}
                  {f.snap_enrolled && <ProgramChip tone="info">SNAP</ProgramChip>}
                </div>
              </td>
              <td className="py-3 px-4"><StatusPill status={f.status || 'Active'} /></td>
            </tr>
          ))}
        </tbody>
      </table>
    )}
  </div>
);

const ChildrenSection: React.FC<{ childrenRows: ChildRow[] }> = ({ childrenRows }) => (
  <div className="bg-[#0a1a52]/40 border border-[#1c2f6a] rounded-xl overflow-hidden">
    {childrenRows.length === 0 ? (
      <div className="p-12 text-center text-[#8ea2d6] text-sm">No children recorded yet.</div>
    ) : (
      <table className="w-full text-sm">
        <thead className="bg-[#081849]/80">
          <tr className="text-[10px] uppercase tracking-wider text-[#f5c23e]">
            <th className="py-3 px-4 text-left font-bold">Name</th>
            <th className="py-3 px-4 text-left font-bold">Age</th>
            <th className="py-3 px-4 text-left font-bold">Test Status</th>
            <th className="py-3 px-4 text-left font-bold">BLL</th>
            <th className="py-3 px-4 text-left font-bold">CLPPP</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-[#1c2f6a]/60">
          {childrenRows.map((c) => (
            <tr key={c.id} className="hover:bg-[#0f2468]/60">
              <td className="py-3 px-4 font-semibold">{c.child_name || 'Unnamed'}</td>
              <td className="py-3 px-4 text-slate-300">{c.age_months ?? '—'} mo</td>
              <td className="py-3 px-4 text-slate-300">{c.lead_test_status || 'Not Tested'}</td>
              <td className="py-3 px-4">
                {c.blood_lead_level != null ? (
                  <span className={`font-mono font-bold ${c.blood_lead_level >= 3.5 ? 'text-rose-300' : 'text-slate-200'}`}>
                    {c.blood_lead_level} µg/dL
                  </span>
                ) : '—'}
              </td>
              <td className="py-3 px-4 text-xs">
                <div className="text-slate-300">{c.clppp_status || 'Not Referred'}</div>
                {c.clppp_case_number && <div className="text-[#8ea2d6]">#{c.clppp_case_number}</div>}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    )}
  </div>
);

const ActivationsSection: React.FC<{ activations: any[] }> = ({ activations }) => (
  <div className="bg-[#0a1a52]/40 border border-[#1c2f6a] rounded-xl overflow-hidden">
    {activations.length === 0 ? (
      <div className="p-12 text-center text-[#8ea2d6] text-sm">No service activations yet.</div>
    ) : (
      <table className="w-full text-sm">
        <thead className="bg-[#081849]/80">
          <tr className="text-[10px] uppercase tracking-wider text-[#f5c23e]">
            <th className="py-3 px-4 text-left font-bold">Service</th>
            <th className="py-3 px-4 text-left font-bold">Vendor</th>
            <th className="py-3 px-4 text-left font-bold">Auth #</th>
            <th className="py-3 px-4 text-left font-bold">Activated</th>
            <th className="py-3 px-4 text-left font-bold">Appointment</th>
            <th className="py-3 px-4 text-left font-bold">Status</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-[#1c2f6a]/60">
          {activations.map((a) => (
            <tr key={a.id} className="hover:bg-[#0f2468]/60">
              <td className="py-3 px-4 font-semibold">{a.service_line}</td>
              <td className="py-3 px-4 text-slate-300">{a.vendor || '—'}</td>
              <td className="py-3 px-4 font-mono text-xs text-[#8ea2d6]">{a.authorization_number || '—'}</td>
              <td className="py-3 px-4 text-xs text-[#8ea2d6]">{a.activated_date ? new Date(a.activated_date).toLocaleDateString() : '—'}</td>
              <td className="py-3 px-4 text-xs text-slate-300">{a.appointment_date ? new Date(a.appointment_date).toLocaleString() : '—'}</td>
              <td className="py-3 px-4"><StatusPill status={a.status || 'Pending'} /></td>
            </tr>
          ))}
        </tbody>
      </table>
    )}
  </div>
);

const BillingSection: React.FC<{ billing: any[] }> = ({ billing }) => {
  const total = useMemo(() => billing.reduce((s, b) => s + (b.amount || 0), 0), [billing]);
  return (
    <div>
      <div className="mb-4 bg-gradient-to-r from-[#f5c23e]/15 via-[#0a1a52]/40 to-[#0a1a52]/40 border border-[#f5c23e]/40 rounded-xl px-6 py-4 flex items-center justify-between">
        <div>
          <div className="text-[10px] uppercase tracking-widest text-[#f5c23e] font-bold">Total billed</div>
          <div className="text-3xl font-black text-[#fcd75a] mt-0.5">${total.toLocaleString()}</div>
        </div>
        <div className="text-xs text-[#8ea2d6] text-right">
          <div>{billing.length} record{billing.length === 1 ? '' : 's'}</div>
          <div className="text-[#6b7ba6] mt-0.5">Auto-created on service completion</div>
        </div>
      </div>

      <div className="bg-[#0a1a52]/40 border border-[#1c2f6a] rounded-xl overflow-hidden">
        {billing.length === 0 ? (
          <div className="p-12 text-center text-[#8ea2d6] text-sm">No billing records yet.</div>
        ) : (
          <table className="w-full text-sm">
            <thead className="bg-[#081849]/80">
              <tr className="text-[10px] uppercase tracking-wider text-[#f5c23e]">
                <th className="py-3 px-4 text-left font-bold">Service</th>
                <th className="py-3 px-4 text-left font-bold">Payer</th>
                <th className="py-3 px-4 text-left font-bold">Amount</th>
                <th className="py-3 px-4 text-left font-bold">Invoice</th>
                <th className="py-3 px-4 text-left font-bold">Date</th>
                <th className="py-3 px-4 text-left font-bold">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#1c2f6a]/60">
              {billing.map((b) => (
                <tr key={b.id} className="hover:bg-[#0f2468]/60">
                  <td className="py-3 px-4 font-semibold">{b.service_line}</td>
                  <td className="py-3 px-4">
                    <div className="text-sm">{b.payer || '—'}</div>
                    <div className="text-xs text-[#8ea2d6]">{b.payer_name || ''}</div>
                  </td>
                  <td className="py-3 px-4 font-mono">${(b.amount || 0).toLocaleString()}</td>
                  <td className="py-3 px-4 font-mono text-xs text-[#8ea2d6]">{b.invoice_number || '—'}</td>
                  <td className="py-3 px-4 text-xs text-[#8ea2d6]">{b.billing_date ? new Date(b.billing_date).toLocaleDateString() : '—'}</td>
                  <td className="py-3 px-4"><StatusPill status={b.status || 'Pending'} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
};

const OutcomesSection: React.FC<{ outcomes: any; onRefresh: () => void }> = ({ outcomes, onRefresh }) => (
  <div className="space-y-5">
    <SectionHeader
      eyebrow="MDHHS Report"
      title={outcomes ? `${outcomes.report_period} · ${outcomes.county}` : 'Outcomes (live)'}
      action={
        <div className="flex items-center gap-2">
          <a
            href="/mdhhs"
            target="_blank"
            rel="noopener noreferrer"
            className="bg-[#046791] hover:bg-[#035980] text-white text-xs font-black px-3 py-1.5 rounded-md transition"
          >
            Open MDHHS Portal ↗
          </a>
          <button onClick={onRefresh} className="bg-[#f5c23e] hover:bg-[#fcd75a] text-[#081849] text-xs font-black px-3 py-1.5 rounded-md">Regenerate</button>
        </div>
      }
    />
    {!outcomes ? (
      <div className="bg-[#0a1a52]/40 border border-[#1c2f6a] rounded-xl p-12 text-center text-[#8ea2d6] text-sm">
        Click Regenerate to build a live MDHHS outcomes report from Airtable data.
      </div>
    ) : (
      <div className="space-y-4">
        <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
          <StatCard label="Total Referrals" value={outcomes.total_referrals ?? 0} tone="brand" />
          <StatCard label="Families Served" value={outcomes.total_families_served ?? 0} tone="brand" />
          <StatCard label="Children Screened" value={outcomes.total_children_screened ?? 0} tone="brand" />
          <StatCard label="EBL Cases" value={outcomes.ebl_cases_navigated ?? 0} tone="alert" />
          <StatCard label="Remediations Done" value={outcomes.remediation_cases_completed ?? 0} tone="ok" />
          <StatCard label="NEMT Trips" value={outcomes.nemt_trips_authorized ?? 0} />
          <StatCard label="Housing Placements" value={outcomes.housing_placements ?? 0} />
          <StatCard label="SNAP Navigations" value={outcomes.snap_navigations ?? 0} />
          <StatCard label="Filter Safety Net" value={outcomes.filter_safety_net_enrollments ?? 0} />
          <StatCard label="Avg Contact (hrs)" value={outcomes.avg_contact_time_hours ?? '—'} hint="Target: 48" tone="info" />
        </div>
        <div className="bg-[#0a1a52]/40 border border-[#1c2f6a] rounded-xl p-5">
          <div className="flex items-center gap-3">
            <span className="text-lg">🏛️</span>
            <div className="flex-1">
              <div className="text-xs font-bold text-white">MDHHS Partner Portal</div>
              <div className="text-[10px] text-[#8ea2d6]">
                Share this link with Aimee Surma and Angela Medina — they see referral tracking,
                SLA compliance, county breakdowns, and a printable outcomes report. No internal DDI data exposed.
              </div>
            </div>
            <a
              href="/mdhhs"
              target="_blank"
              rel="noopener noreferrer"
              className="text-xs font-bold text-[#f5c23e] hover:text-[#fcd75a] transition shrink-0"
            >
              /mdhhs ↗
            </a>
          </div>
        </div>
      </div>
    )}
  </div>
);

const AISection: React.FC = () => {
  const [messages, setMessages] = useState<{ role: 'user' | 'assistant'; text: string }[]>([]);
  const [input, setInput] = useState('');
  const [busy, setBusy] = useState(false);

  const send = async () => {
    if (!input.trim()) return;
    const userMsg = input;
    setMessages((m) => [...m, { role: 'user', text: userMsg }]);
    setInput('');
    setBusy(true);
    try {
      const result: any = await api.shieldAiChat(userMsg);
      const reply = result?.reply || result?.error || 'No response.';
      setMessages((m) => [...m, { role: 'assistant', text: reply }]);
    } catch (e: any) {
      setMessages((m) => [...m, { role: 'assistant', text: `Error: ${e.message}` }]);
    } finally {
      setBusy(false);
    }
  };

  const suggestions = [
    'Which Wayne County cases are past the 48-hour window?',
    'How many children are navigated to CLPPP follow-up this month?',
    'Which remediations haven\'t had housing activated?',
    'Summarize MDHHS outcomes for this quarter.',
  ];

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
      <div className="lg:col-span-2 bg-[#0a1a52]/40 border border-[#1c2f6a] rounded-xl flex flex-col" style={{ minHeight: 520 }}>
        <div className="px-5 py-4 border-b border-[#1c2f6a] flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-[#f5c23e] to-[#e0a92e] border border-[#fcd75a] flex items-center justify-center">
            <svg viewBox="0 0 24 24" className="w-5 h-5 text-[#1f3fae]" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="12" r="9" /><path d="M12 7v5l3 2" />
            </svg>
          </div>
          <div>
            <div className="font-bold text-white">SHIELD Navigator AI</div>
            <div className="text-[10px] text-[#8ea2d6] uppercase tracking-wider">Claude Sonnet 4.5 · Live case context · Internal scope</div>
          </div>
        </div>
        <div className="flex-1 overflow-y-auto px-5 py-4 space-y-3">
          {messages.length === 0 && (
            <div className="text-center py-12 text-[#8ea2d6] text-sm">
              Ask about cases, overdue follow-ups, billing, or outcomes.
            </div>
          )}
          {messages.map((m, i) => (
            <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[80%] px-4 py-2.5 rounded-lg text-sm whitespace-pre-wrap ${
                m.role === 'user' ? 'bg-[#f5c23e] text-[#081849] border border-[#fcd75a] font-medium' : 'bg-[#081849] text-slate-100 border border-[#1c2f6a]'
              }`}>{m.text}</div>
            </div>
          ))}
          {busy && <div className="text-[11px] text-[#8ea2d6] italic">SHIELD AI thinking…</div>}
        </div>
        <div className="px-5 py-3 border-t border-[#1c2f6a] flex gap-2">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(); } }}
            placeholder="Ask about a case, alert, or outcomes…"
            className={inputCls}
            disabled={busy}
          />
          <button onClick={send} disabled={busy || !input.trim()} className="bg-[#f5c23e] hover:bg-[#fcd75a] disabled:opacity-50 text-[#081849] px-4 py-2 rounded-md text-sm font-black">
            Send
          </button>
        </div>
      </div>
      <div className="bg-[#0a1a52]/40 border border-[#1c2f6a] rounded-xl p-5">
        <div className="text-[10px] uppercase tracking-widest text-[#f5c23e] font-bold mb-3">Try asking</div>
        <div className="space-y-2">
          {suggestions.map((s, i) => (
            <button
              key={i}
              onClick={() => setInput(s)}
              className="w-full text-left text-xs bg-[#081849]/60 hover:bg-[#0f2468]/70 border border-[#1c2f6a] hover:border-[#f5c23e]/60 rounded-md px-3 py-2.5 transition text-slate-200"
            >
              {s}
            </button>
          ))}
        </div>
        <div className="mt-5 pt-5 border-t border-[#1c2f6a] text-[11px] text-[#8ea2d6] leading-relaxed">
          Live snapshot of referrals, alerts, children's test status, and service activations is injected into every query. No cross-system data sharing.
        </div>
      </div>
    </div>
  );
};

export default SHIELDSystem;
