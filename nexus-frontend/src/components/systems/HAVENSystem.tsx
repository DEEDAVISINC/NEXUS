import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { api } from '../../api/client';

/**
 * HAVEN — Housing, Assistance, Vital Emergency Network
 * Disaster Response TPA System — Operational Workspace
 *
 * 7 Sections:
 *   Command · Events · Safe Haven · Dispatch · Network · MCO Contracts · Billing
 *
 * Palette (HAVEN-keyed):
 *   haven-dark     #0a1628   deepest backdrop
 *   haven-navy     #0f2040   primary surface / sidebar
 *   haven-blue     #1e3a5f   card surfaces
 *   haven-accent   #2563eb   interactive blue
 *   haven-emerald  #059669   success / medical pillar
 *   haven-amber    #d97706   housing pillar
 *   haven-sky      #38bdf8   transport pillar
 */

interface HAVENSystemProps {
  onBackToNexus: () => void;
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

interface PartnerRecord { id: string; fields: Record<string, any>; }
interface MCORecord { id: string; fields: Record<string, any>; }

interface NetworkStats {
  total_partners: number;
  total_mcos: number;
  transport: { total: number; by_status: Record<string, number>; by_state: Record<string, number> };
  housing: { total: number; by_status: Record<string, number> };
  medical: { total: number; by_status: Record<string, number>; by_state: Record<string, number> };
  mcos: { total: number; by_status: Record<string, number>; by_state: Record<string, number> };
}

interface MCOStats {
  total_mcos: number;
  total_members: number;
  by_state: Record<string, number>;
  by_parent: Record<string, number>;
  by_status: Record<string, number>;
}

interface SystemStatus {
  system: string;
  status: string;
  network: NetworkStats;
  mcos: MCOStats;
  operations: {
    active_events: number;
    active_cases: number;
    pending_activations: number;
    events: Array<{ id: string; name: string; type: string; states: string[] }>;
  };
}

interface DisasterEvent {
  id: string;
  name: string;
  type: string;
  severity: string;
  states: string[];
  status: string;
  start_date: string;
  declared_date?: string;
  fema_number?: string;
  affected_members?: number;
  notes?: string;
}

interface SafeHavenCase {
  id: string;
  member_name: string;
  member_id?: string;
  mco?: string;
  event_id?: string;
  event_name?: string;
  state: string;
  status: string;
  needs: string[];
  housing_status?: string;
  transport_status?: string;
  medical_status?: string;
  assigned_to?: string;
  created_at?: string;
  notes?: string;
}

// ──────────────────────────────────────────────────────────────────────────
// SECTIONS — 7 operational areas
// ──────────────────────────────────────────────────────────────────────────
const SECTIONS = [
  { id: 'command',   label: 'Command',       sub: 'Operations Center',  glyph: '⚡', color: '#f5c23e' },
  { id: 'events',    label: 'Events',        sub: 'Disaster Tracking',  glyph: 'E',  color: '#ef4444' },
  { id: 'safehaven', label: 'Safe Haven',    sub: 'Member Intake',      glyph: 'SH', color: '#10b981' },
  { id: 'dispatch',  label: 'Dispatch',      sub: 'Resource Deploy',    glyph: 'D',  color: '#f97316' },
  { id: 'network',   label: 'Network',       sub: 'Partner Registry',   glyph: 'N',  color: '#2563eb' },
  { id: 'mcos',      label: 'MCO Contracts', sub: 'Credentialing',      glyph: 'M',  color: '#8b5cf6' },
  { id: 'billing',   label: 'Billing',       sub: 'Claims & Revenue',   glyph: 'B',  color: '#14b8a6' },
];

const PARTNER_STAGES = ['Prospect', 'Outreach', 'Negotiating', 'Signed', 'Active'] as const;
type PartnerStage = typeof PARTNER_STAGES[number];

const MCO_STAGES = ['Target', 'Outreach', 'Credentialing', 'Negotiating', 'Active'] as const;
type MCOStage = typeof MCO_STAGES[number];

const EVENT_TYPES = ['Hurricane', 'Flood', 'Tornado', 'Wildfire', 'Winter Storm', 'Other'] as const;
const EVENT_SEVERITIES = ['Watch', 'Warning', 'Emergency', 'Major Disaster'] as const;
const EVENT_STATUSES = ['Monitoring', 'Pre-Activation', 'Active', 'Recovery', 'Closed'] as const;

const CASE_STATUSES = ['Intake', 'Assessment', 'Active', 'Stabilized', 'Closed'] as const;
const CASE_NEEDS = ['Housing', 'Transport', 'Medical', 'Pharmacy', 'DME', 'Telehealth', 'Home Health'] as const;

const PARTNER_STAGE_COLORS: Record<string, string> = {
  Prospect: '#64748b', Outreach: '#3b82f6', Negotiating: '#d97706', Signed: '#8b5cf6', Active: '#059669',
};
const MCO_STAGE_COLORS: Record<string, string> = {
  Target: '#d97706', Outreach: '#3b82f6', Credentialing: '#8b5cf6', Negotiating: '#f97316', Active: '#059669',
};
const EVENT_STATUS_COLORS: Record<string, string> = {
  Monitoring: '#64748b', 'Pre-Activation': '#d97706', Active: '#ef4444', Recovery: '#3b82f6', Closed: '#059669',
};
const CASE_STATUS_COLORS: Record<string, string> = {
  Intake: '#3b82f6', Assessment: '#d97706', Active: '#ef4444', Stabilized: '#8b5cf6', Closed: '#059669',
};
const SEVERITY_COLORS: Record<string, string> = {
  Watch: '#64748b', Warning: '#d97706', Emergency: '#ef4444', 'Major Disaster': '#dc2626',
};

const STATES = ['FL', 'TX', 'LA', 'MI'] as const;
const STATE_NAMES: Record<string, string> = { FL: 'Florida', TX: 'Texas', LA: 'Louisiana', MI: 'Michigan' };

type PartnerType = 'transport' | 'housing' | 'medical';

// ──────────────────────────────────────────────────────────────────────────
// MAIN COMPONENT
// ──────────────────────────────────────────────────────────────────────────
const HAVENSystem: React.FC<HAVENSystemProps> = ({ onBackToNexus, activeTab, setActiveTab }) => {
  // System data
  const [status, setStatus] = useState<SystemStatus | null>(null);
  const [transportPartners, setTransportPartners] = useState<PartnerRecord[]>([]);
  const [housingPartners, setHousingPartners] = useState<PartnerRecord[]>([]);
  const [medicalPartners, setMedicalPartners] = useState<PartnerRecord[]>([]);
  const [mcos, setMcos] = useState<MCORecord[]>([]);
  const [events, setEvents] = useState<DisasterEvent[]>([]);
  const [cases, setCases] = useState<SafeHavenCase[]>([]);
  const [loading, setLoading] = useState(false);

  // UI state
  const [toast, setToast] = useState<{ tone: 'ok' | 'err' | 'info'; message: string } | null>(null);
  const [partnerTypeFilter, setPartnerTypeFilter] = useState<PartnerType>('transport');
  const [stateFilter, setStateFilter] = useState<string>('');
  const [selectedPartner, setSelectedPartner] = useState<PartnerRecord | null>(null);
  const [selectedPartnerType, setSelectedPartnerType] = useState<PartnerType>('transport');
  const [selectedMCO, setSelectedMCO] = useState<MCORecord | null>(null);
  const [selectedEvent, setSelectedEvent] = useState<DisasterEvent | null>(null);
  const [selectedCase, setSelectedCase] = useState<SafeHavenCase | null>(null);
  const [noteInput, setNoteInput] = useState('');
  const [followUpDate, setFollowUpDate] = useState('');

  // Disaster Watch
  const [watchFeed, setWatchFeed] = useState<any>(null);
  const [watchLoading, setWatchLoading] = useState(false);
  const [eventsView, setEventsView] = useState<'watch' | 'declared'>('watch');

  // Outreach engine
  const [outreachPackage, setOutreachPackage] = useState<any>(null);
  const [outreachLoading, setOutreachLoading] = useState(false);

  // New event form
  const [showNewEvent, setShowNewEvent] = useState(false);
  const [newEvent, setNewEvent] = useState({ name: '', type: 'Hurricane', severity: 'Watch', states: [] as string[], fema_number: '' });

  // New case form
  const [showNewCase, setShowNewCase] = useState(false);
  const [newCase, setNewCase] = useState({ member_name: '', member_id: '', mco: '', event_id: '', state: 'FL', needs: [] as string[] });

  const mappedTab = useMemo(() => {
    const known = SECTIONS.map(s => s.id);
    return known.includes(activeTab) ? activeTab : 'command';
  }, [activeTab]);

  const showToast = useCallback((tone: 'ok' | 'err' | 'info', message: string) => {
    setToast({ tone, message });
    setTimeout(() => setToast(null), 4000);
  }, []);

  // ─── DATA FETCHING ──────────────────────────────────────────────────────
  const loadStatus = useCallback(async () => {
    try { const res = await api.getHavenStatus(); setStatus(res); } catch { /* silent */ }
  }, []);

  const loadPartners = useCallback(async (type: PartnerType) => {
    try {
      const q = stateFilter || undefined;
      let res: any;
      if (type === 'transport') res = await api.getHavenTransportPartners(q);
      else if (type === 'housing') res = await api.getHavenHousingPartners(q);
      else res = await api.getHavenMedicalPartners(q);
      const partners = res.partners || [];
      if (type === 'transport') setTransportPartners(partners);
      if (type === 'housing') setHousingPartners(partners);
      if (type === 'medical') setMedicalPartners(partners);
    } catch {
      if (type === 'transport') setTransportPartners([]);
      if (type === 'housing') setHousingPartners([]);
      if (type === 'medical') setMedicalPartners([]);
    }
  }, [stateFilter]);

  const loadMCOs = useCallback(async () => {
    try {
      const res = await api.getHavenMCOs(stateFilter || undefined);
      setMcos(res.mcos || []);
    } catch { setMcos([]); }
  }, [stateFilter]);

  const loadEvents = useCallback(async () => {
    try {
      const res = await api.getHavenEvents();
      setEvents(res.events || []);
    } catch { setEvents([]); }
  }, []);

  const loadCases = useCallback(async () => {
    try {
      const res = await api.getHavenCases();
      setCases(res.cases || []);
    } catch { setCases([]); }
  }, []);

  const loadWatchFeed = useCallback(async () => {
    setWatchLoading(true);
    try {
      const res = await api.getHavenWatchFeed();
      setWatchFeed(res);
    } catch { setWatchFeed(null); }
    setWatchLoading(false);
  }, []);

  useEffect(() => { loadStatus(); }, [loadStatus]);

  useEffect(() => {
    switch (mappedTab) {
      case 'command': loadPartners('transport'); loadPartners('housing'); loadPartners('medical'); loadMCOs(); loadEvents(); loadCases(); loadWatchFeed(); break;
      case 'events': loadEvents(); loadWatchFeed(); break;
      case 'safehaven': loadCases(); loadEvents(); break;
      case 'dispatch': loadCases(); loadPartners('transport'); loadPartners('housing'); loadPartners('medical'); break;
      case 'network': loadPartners(partnerTypeFilter); break;
      case 'mcos': loadMCOs(); break;
      case 'billing': loadCases(); loadMCOs(); break;
    }
  }, [mappedTab, partnerTypeFilter, stateFilter, loadPartners, loadMCOs, loadEvents, loadCases, loadWatchFeed]);

  // ─── ACTIONS ─────────────────────────────────────────────────────────────
  const updatePartnerStatus = async (table: PartnerType, recordId: string, newStatus: string) => {
    try {
      await api.updateHavenPartner(table, recordId, { agreement_status: newStatus });
      showToast('ok', `Status → ${newStatus}`);
      loadPartners(table); loadStatus();
    } catch { showToast('err', 'Failed to update'); }
  };

  const updateMCOStatus = async (recordId: string, newStatus: string) => {
    try {
      await api.updateHavenMCO(recordId, { contract_status: newStatus });
      showToast('ok', `MCO → ${newStatus}`);
      loadMCOs(); loadStatus();
    } catch { showToast('err', 'Failed to update'); }
  };

  const addPartnerNote = async (table: PartnerType, record: PartnerRecord, note: string) => {
    if (!note.trim()) return;
    const ts = new Date().toLocaleString('en-US', { month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' });
    const newNotes = `[${ts}] ${note.trim()}\n${record.fields.notes || ''}`;
    try {
      await api.updateHavenPartner(table, record.id, { notes: newNotes });
      showToast('ok', 'Note added');
      setNoteInput('');
      loadPartners(table);
      if (selectedPartner?.id === record.id) setSelectedPartner({ ...record, fields: { ...record.fields, notes: newNotes } });
    } catch { showToast('err', 'Failed to add note'); }
  };

  const addMCONote = async (record: MCORecord, note: string) => {
    if (!note.trim()) return;
    const ts = new Date().toLocaleString('en-US', { month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' });
    const newNotes = `[${ts}] ${note.trim()}\n${record.fields.notes || ''}`;
    try {
      await api.updateHavenMCO(record.id, { notes: newNotes });
      showToast('ok', 'Note added');
      setNoteInput('');
      loadMCOs();
      if (selectedMCO?.id === record.id) setSelectedMCO({ ...record, fields: { ...record.fields, notes: newNotes } });
    } catch { showToast('err', 'Failed to add note'); }
  };

  const createEvent = async () => {
    if (!newEvent.name.trim()) { showToast('err', 'Event name required'); return; }
    try {
      await api.createHavenEvent({
        name: newEvent.name, type: newEvent.type, severity: newEvent.severity,
        states: newEvent.states, fema_number: newEvent.fema_number, status: 'Monitoring',
      });
      showToast('ok', `Event created: ${newEvent.name}`);
      setNewEvent({ name: '', type: 'Hurricane', severity: 'Watch', states: [], fema_number: '' });
      setShowNewEvent(false);
      loadEvents(); loadStatus();
    } catch { showToast('err', 'Failed to create event'); }
  };

  const createCase = async () => {
    if (!newCase.member_name.trim()) { showToast('err', 'Member name required'); return; }
    try {
      await api.createHavenCase({
        member_name: newCase.member_name, member_id: newCase.member_id,
        mco: newCase.mco, event_id: newCase.event_id, state: newCase.state,
        needs: newCase.needs, status: 'Intake',
      });
      showToast('ok', `Safe Haven opened: ${newCase.member_name}`);
      setNewCase({ member_name: '', member_id: '', mco: '', event_id: '', state: 'FL', needs: [] });
      setShowNewCase(false);
      loadCases(); loadStatus();
    } catch { showToast('err', 'Failed to create case'); }
  };

  // ─── COMPUTED ─────────────────────────────────────────────────────────────
  const allPartners = useMemo(() => [...transportPartners, ...housingPartners, ...medicalPartners], [transportPartners, housingPartners, medicalPartners]);
  const activePartners = useMemo(() => {
    if (partnerTypeFilter === 'transport') return transportPartners;
    if (partnerTypeFilter === 'housing') return housingPartners;
    return medicalPartners;
  }, [partnerTypeFilter, transportPartners, housingPartners, medicalPartners]);

  const partnersByStatus = useMemo(() => {
    const c: Record<string, number> = {};
    PARTNER_STAGES.forEach(s => { c[s] = 0; });
    allPartners.forEach(p => { const s = p.fields.agreement_status || 'Prospect'; c[s] = (c[s] || 0) + 1; });
    return c;
  }, [allPartners]);

  const mcosByStatus = useMemo(() => {
    const c: Record<string, number> = {};
    MCO_STAGES.forEach(s => { c[s] = 0; });
    mcos.forEach(m => { const s = m.fields.contract_status || 'Target'; c[s] = (c[s] || 0) + 1; });
    return c;
  }, [mcos]);

  const activeEvents = useMemo(() => events.filter(e => e.status !== 'Closed'), [events]);
  const activeCases = useMemo(() => cases.filter(c => c.status !== 'Closed'), [cases]);

  const actionAlerts = useMemo(() => {
    const alerts: Array<{ type: 'danger' | 'warning' | 'info'; message: string; action?: string }> = [];
    activeEvents.filter(e => e.status === 'Active' || e.severity === 'Emergency' || e.severity === 'Major Disaster').forEach(e => {
      alerts.push({ type: 'danger', message: `🌀 ${e.name} — ${e.severity} — ${e.status}`, action: 'events' });
    });
    activeCases.filter(c => c.status === 'Intake').forEach(c => {
      alerts.push({ type: 'warning', message: `New intake: ${c.member_name} — needs assessment`, action: 'safehaven' });
    });
    allPartners.forEach(p => {
      if (p.fields.next_follow_up && new Date(p.fields.next_follow_up).getTime() < Date.now()) {
        alerts.push({ type: 'info', message: `Follow-up overdue: ${p.fields.company_name || p.fields.property_name}`, action: 'network' });
      }
    });
    mcos.forEach(m => {
      if (!m.fields.notes && m.fields.contract_status !== 'Active') {
        alerts.push({ type: 'info', message: `${m.fields.mco_name} — no contact logged`, action: 'mcos' });
      }
    });
    return alerts;
  }, [activeEvents, activeCases, allPartners, mcos]);

  // ─── SECTION HELPERS ──────────────────────────────────────────────────────
  const sectionColor = (id: string) => SECTIONS.find(s => s.id === id)?.color || '#f5c23e';

  const sectionTitle = (id: string): string => {
    switch (id) {
      case 'command': return 'Operations Center';
      case 'events': return 'Disaster Event Tracker';
      case 'safehaven': return 'Safe Haven Intake';
      case 'dispatch': return 'Resource Dispatch';
      case 'network': return 'Partner Network';
      case 'mcos': return 'MCO Contract Pipeline';
      case 'billing': return 'Claims & Revenue';
      default: return 'HAVEN';
    }
  };

  // ═══════════════════════════════════════════════════════════════════════════
  // SECTION 1: COMMAND — Operations Center
  // ═══════════════════════════════════════════════════════════════════════════
  const renderCommand = () => {
    const threatLevel = watchFeed?.threat_level || 'None';
    const threatColors: Record<string, string> = { 'Major Disaster': '#dc2626', Emergency: '#ef4444', Warning: '#d97706', Watch: '#64748b', None: '#059669' };
    const threatBg: Record<string, string> = { 'Major Disaster': 'bg-red-900/30 border-red-500/50', Emergency: 'bg-red-900/20 border-red-500/30', Warning: 'bg-amber-900/20 border-amber-500/30', Watch: 'bg-gray-800/30 border-gray-600/30', None: 'bg-emerald-900/20 border-emerald-500/30' };

    return (
    <div className="space-y-6">
      {/* Threat Level Banner */}
      <div className={`rounded-xl border p-4 flex items-center justify-between ${threatBg[threatLevel] || threatBg.None}`}>
        <div className="flex items-center gap-3">
          <span className="text-2xl">{threatLevel === 'Major Disaster' ? '🔴' : threatLevel === 'Emergency' ? '🟠' : threatLevel === 'Warning' ? '🟡' : threatLevel === 'Watch' ? '⚪' : '🟢'}</span>
          <div>
            <div className="text-[10px] uppercase tracking-widest font-bold text-gray-400">Disaster Watch</div>
            <div className="text-lg font-black" style={{ color: threatColors[threatLevel] || '#059669' }}>{threatLevel === 'None' ? 'ALL CLEAR' : threatLevel.toUpperCase()}</div>
          </div>
        </div>
        <div className="flex items-center gap-4 text-xs text-gray-400">
          <span>NWS: <strong className="text-white">{watchFeed?.total_alerts || 0}</strong></span>
          <span>FEMA: <strong className="text-white">{watchFeed?.total_fema_active || 0}</strong></span>
          <button onClick={() => setActiveTab('events')} className="text-blue-400 hover:text-blue-300 font-bold">View Watch →</button>
        </div>
      </div>

      {/* System Readiness */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-3">
        <StatCard label="Events" value={activeEvents.length} sub={`${events.filter(e => e.status === 'Active').length} active`} color="#ef4444" />
        <StatCard label="Safe Haven" value={activeCases.length} sub={`${cases.filter(c => c.status === 'Intake').length} intake`} color="#10b981" />
        <StatCard label="Transport" value={transportPartners.length} sub={`${transportPartners.filter(p => p.fields.agreement_status === 'Active').length} active`} color="#38bdf8" />
        <StatCard label="Housing" value={housingPartners.length} sub={`${housingPartners.filter(p => p.fields.agreement_status === 'Active').length} active`} color="#d97706" />
        <StatCard label="Medical" value={medicalPartners.length} sub={`${medicalPartners.filter(p => p.fields.agreement_status === 'Active').length} active`} color="#059669" />
        <StatCard label="MCOs" value={mcos.length} sub={`${mcosByStatus['Active'] || 0} contracted`} color="#8b5cf6" />
        <StatCard label="Alerts" value={actionAlerts.length} sub="Need action" color={actionAlerts.length > 0 ? '#ef4444' : '#64748b'} />
      </div>

      {/* Active Disaster Events */}
      {activeEvents.length > 0 && (
        <Card title="Active Disaster Events" titleColor="#ef4444">
          <div className="space-y-2">
            {activeEvents.map(e => (
              <div key={e.id} className="flex items-center justify-between bg-[#0a1628] rounded-lg px-4 py-3">
                <div className="flex items-center gap-3">
                  <span className="text-lg">{e.type === 'Hurricane' ? '🌀' : e.type === 'Flood' ? '🌊' : e.type === 'Tornado' ? '🌪️' : e.type === 'Wildfire' ? '🔥' : '⚠️'}</span>
                  <div>
                    <div className="text-sm font-bold text-white">{e.name}</div>
                    <div className="text-[10px] text-gray-500">{e.type} · {(e.states || []).join(', ')} · {e.start_date || '—'}</div>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <StatusBadge status={e.severity} colors={SEVERITY_COLORS} />
                  <StatusBadge status={e.status} colors={EVENT_STATUS_COLORS} />
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Partner Pipeline */}
      <Card title="Partner Pipeline" titleColor="#2563eb">
        <PipelineFunnel stages={PARTNER_STAGES as unknown as string[]} counts={partnersByStatus} colors={PARTNER_STAGE_COLORS} />
      </Card>

      {/* MCO Pipeline */}
      <Card title="MCO Pipeline" titleColor="#8b5cf6">
        <PipelineFunnel stages={MCO_STAGES as unknown as string[]} counts={mcosByStatus} colors={MCO_STAGE_COLORS} />
      </Card>

      {/* Action Queue */}
      {actionAlerts.length > 0 && (
        <Card title="Action Queue" titleColor="#f5c23e">
          <div className="space-y-2">
            {actionAlerts.slice(0, 15).map((a, i) => (
              <button
                key={i}
                onClick={() => a.action && setActiveTab(a.action)}
                className="w-full flex items-center gap-3 text-sm bg-[#0a1628] rounded-lg px-4 py-2.5 text-left hover:bg-[#1e3a5f]/30 transition"
              >
                <span className={`w-2 h-2 rounded-full shrink-0 ${a.type === 'danger' ? 'bg-red-400' : a.type === 'warning' ? 'bg-amber-400' : 'bg-blue-400'}`} />
                <span className="text-gray-300 flex-1">{a.message}</span>
                <span className="text-[10px] text-gray-600">→</span>
              </button>
            ))}
          </div>
        </Card>
      )}
    </div>
    );
  };

  // ═══════════════════════════════════════════════════════════════════════════
  // SECTION 2: EVENTS — Disaster Watch + Event Tracking
  // ═══════════════════════════════════════════════════════════════════════════
  const renderEvents = () => {
    if (selectedEvent) return renderEventDetail();

    const threatLevel = watchFeed?.threat_level || 'None';
    const threatColors: Record<string, string> = { 'Major Disaster': '#dc2626', Emergency: '#ef4444', Warning: '#d97706', Watch: '#64748b', None: '#059669' };
    const threatBg: Record<string, string> = { 'Major Disaster': 'bg-red-900/30 border-red-500/50', Emergency: 'bg-red-900/20 border-red-500/30', Warning: 'bg-amber-900/20 border-amber-500/30', Watch: 'bg-gray-800/30 border-gray-600/30', None: 'bg-emerald-900/20 border-emerald-500/30' };

    return (
      <div className="space-y-4">
        {/* View toggle */}
        <div className="flex items-center gap-2">
          <button onClick={() => setEventsView('watch')} className={`px-4 py-2 rounded-lg text-xs font-bold uppercase tracking-wider transition border ${eventsView === 'watch' ? 'bg-red-600/20 text-red-400 border-red-500/50' : 'bg-[#0a1628] text-gray-400 border-[#1e3a5f] hover:text-white'}`}>
            📡 Disaster Watch
          </button>
          <button onClick={() => setEventsView('declared')} className={`px-4 py-2 rounded-lg text-xs font-bold uppercase tracking-wider transition border ${eventsView === 'declared' ? 'bg-red-600/20 text-red-400 border-red-500/50' : 'bg-[#0a1628] text-gray-400 border-[#1e3a5f] hover:text-white'}`}>
            📋 HAVEN Events ({events.length})
          </button>
          <div className="flex-1" />
          <button onClick={loadWatchFeed} disabled={watchLoading} className="text-xs font-semibold text-gray-400 hover:text-white bg-[#0a1628] border border-[#1e3a5f] rounded-md px-3 py-1.5">
            {watchLoading ? 'Scanning…' : '🔄 Refresh Watch'}
          </button>
        </div>

        {/* DISASTER WATCH VIEW */}
        {eventsView === 'watch' && (
          <div className="space-y-4">
            {/* Threat Level Banner */}
            <div className={`rounded-xl border p-5 ${threatBg[threatLevel] || threatBg.None}`}>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className="text-4xl">{threatLevel === 'Major Disaster' ? '🔴' : threatLevel === 'Emergency' ? '🟠' : threatLevel === 'Warning' ? '🟡' : threatLevel === 'Watch' ? '⚪' : '🟢'}</div>
                  <div>
                    <div className="text-xs uppercase tracking-widest font-bold text-gray-400">HAVEN Threat Level</div>
                    <div className="text-2xl font-black mt-0.5" style={{ color: threatColors[threatLevel] || '#059669' }}>{threatLevel === 'None' ? 'ALL CLEAR' : threatLevel.toUpperCase()}</div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-xs text-gray-500">NWS Alerts: <span className="text-white font-bold">{watchFeed?.total_alerts || 0}</span></div>
                  <div className="text-xs text-gray-500 mt-0.5">FEMA Active: <span className="text-white font-bold">{watchFeed?.total_fema_active || 0}</span></div>
                  {watchFeed?.fetched_at && <div className="text-[9px] text-gray-600 mt-1">Updated {new Date(watchFeed.fetched_at).toLocaleTimeString()}</div>}
                </div>
              </div>
              {/* Recommendations */}
              {watchFeed?.recommendations && watchFeed.recommendations.length > 0 && (
                <div className="mt-4 pt-4 border-t border-white/10 space-y-1.5">
                  {watchFeed.recommendations.map((rec: string, i: number) => (
                    <div key={i} className="text-sm text-gray-300 flex items-start gap-2">
                      <span className="text-xs mt-0.5">▸</span><span>{rec}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* State Threat Cards */}
            {watchFeed?.states && (
              <div className="grid grid-cols-4 gap-3">
                {STATES.map(st => {
                  const stData = watchFeed.states[st];
                  if (!stData) return null;
                  const stColor = threatColors[stData.threat_level] || '#059669';
                  return (
                    <div key={st} className="bg-[#0f2040] rounded-xl border border-[#1e3a5f]/50 p-4">
                      <div className="flex items-center justify-between mb-3">
                        <span className="text-lg font-black text-white">{st}</span>
                        <span className="text-[10px] font-black uppercase px-2 py-0.5 rounded border" style={{ color: stColor, borderColor: `${stColor}80`, backgroundColor: `${stColor}15` }}>
                          {stData.threat_level === 'None' ? 'Clear' : stData.threat_level}
                        </span>
                      </div>
                      <div className="space-y-1 text-xs">
                        <div className="flex justify-between"><span className="text-gray-500">FEMA Declarations</span><span className="text-white font-bold">{stData.active_fema_declarations}</span></div>
                        <div className="flex justify-between"><span className="text-gray-500">NWS Alerts</span><span className="text-white font-bold">{stData.active_nws_alerts}</span></div>
                        {stData.hurricane_alerts > 0 && <div className="flex justify-between"><span className="text-gray-500">🌀 Hurricane</span><span className="text-red-400 font-bold">{stData.hurricane_alerts}</span></div>}
                        {stData.flood_alerts > 0 && <div className="flex justify-between"><span className="text-gray-500">🌊 Flood</span><span className="text-blue-400 font-bold">{stData.flood_alerts}</span></div>}
                        {stData.tornado_alerts > 0 && <div className="flex justify-between"><span className="text-gray-500">🌪️ Tornado</span><span className="text-amber-400 font-bold">{stData.tornado_alerts}</span></div>}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}

            {/* Live Alert Feed */}
            <Card title="Live Alert Feed" titleColor="#ef4444">
              {watchLoading && <LoadingState label="Scanning FEMA + NWS…" />}
              {!watchLoading && (!watchFeed?.feed || watchFeed.feed.length === 0) && (
                <div className="text-sm text-gray-600 italic py-4">No active alerts in HAVEN states — all clear</div>
              )}
              {!watchLoading && watchFeed?.feed && watchFeed.feed.length > 0 && (
                <div className="space-y-2 max-h-[60vh] overflow-y-auto">
                  {watchFeed.feed.map((item: any, i: number) => {
                    const sevColor = SEVERITY_COLORS[item.severity] || '#64748b';
                    const catIcon = item.category === 'Hurricane' ? '🌀' : item.category === 'Flood' ? '🌊' : item.category === 'Tornado' ? '🌪️' : item.category === 'Wildfire' ? '🔥' : item.category === 'Winter Storm' ? '❄️' : item.category === 'Severe Storm' ? '⛈️' : '⚠️';
                    return (
                      <div key={i} className="bg-[#0a1628] rounded-lg px-4 py-3 border border-[#1e3a5f]/50">
                        <div className="flex items-start justify-between gap-3">
                          <div className="flex items-start gap-3 flex-1 min-w-0">
                            <span className="text-lg shrink-0 mt-0.5">{catIcon}</span>
                            <div className="min-w-0">
                              <div className="text-sm font-bold text-white truncate">{item.title}</div>
                              <div className="text-[10px] text-gray-500 mt-0.5">
                                {item.source} · {item.state} · {item.category} · {item.date || '—'}
                                {item.expires && <span className="ml-1">· Expires {item.expires}</span>}
                              </div>
                              {item.detail && <div className="text-xs text-gray-400 mt-1 line-clamp-2">{item.detail}</div>}
                              {item.instruction && <div className="text-xs text-amber-400/80 mt-1 line-clamp-1">⚠ {item.instruction}</div>}
                            </div>
                          </div>
                          <div className="flex flex-col items-end gap-1 shrink-0">
                            <StatusBadge status={item.severity} colors={SEVERITY_COLORS} />
                            <span className="text-[9px] text-gray-600 font-mono">{item.source}</span>
                          </div>
                        </div>
                        {item.url && <a href={item.url} target="_blank" rel="noreferrer" className="text-[10px] text-blue-400 hover:text-blue-300 mt-1 inline-block">View on FEMA.gov →</a>}
                      </div>
                    );
                  })}
                </div>
              )}
            </Card>

            {/* Recent FEMA Declarations */}
            {watchFeed?.recent_fema && watchFeed.recent_fema.length > 0 && (
              <Card title="Recent FEMA Declarations (90 Days)" titleColor="#d97706">
                <div className="space-y-2">
                  {watchFeed.recent_fema.map((d: any, i: number) => (
                    <div key={i} className="flex items-center justify-between bg-[#0a1628] rounded-lg px-4 py-2.5">
                      <div>
                        <span className="text-sm text-white font-medium">{d.title}</span>
                        <span className="text-xs text-gray-500 ml-2">{d.state} · {d.declaration_date}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="text-[10px] text-gray-500 bg-[#1e3a5f] px-2 py-0.5 rounded font-mono">{d.fema_number}</span>
                        <StatusBadge status={d.severity} colors={SEVERITY_COLORS} />
                        {d.is_active && <span className="text-[9px] text-red-400 font-bold">ACTIVE</span>}
                      </div>
                    </div>
                  ))}
                </div>
              </Card>
            )}
          </div>
        )}

        {/* DECLARED HAVEN EVENTS VIEW */}
        {eventsView === 'declared' && (
          <div className="space-y-4">
            {showNewEvent && (
              <Card title="Declare New Event" titleColor="#ef4444">
                <div className="grid grid-cols-2 gap-4">
                  <FormField label="Event Name" required>
                    <input type="text" value={newEvent.name} onChange={e => setNewEvent(p => ({ ...p, name: e.target.value }))}
                      placeholder="e.g., Hurricane Milton" className="form-input" />
                  </FormField>
                  <FormField label="Type">
                    <select value={newEvent.type} onChange={e => setNewEvent(p => ({ ...p, type: e.target.value }))} className="form-input">
                      {EVENT_TYPES.map(t => <option key={t} value={t}>{t}</option>)}
                    </select>
                  </FormField>
                  <FormField label="Severity">
                    <select value={newEvent.severity} onChange={e => setNewEvent(p => ({ ...p, severity: e.target.value }))} className="form-input">
                      {EVENT_SEVERITIES.map(s => <option key={s} value={s}>{s}</option>)}
                    </select>
                  </FormField>
                  <FormField label="FEMA Disaster Number">
                    <input type="text" value={newEvent.fema_number} onChange={e => setNewEvent(p => ({ ...p, fema_number: e.target.value }))}
                      placeholder="e.g., DR-4800" className="form-input" />
                  </FormField>
                  <FormField label="Affected States">
                    <div className="flex gap-2 mt-1">
                      {STATES.map(st => (
                        <button key={st} onClick={() => setNewEvent(p => ({
                          ...p, states: p.states.includes(st) ? p.states.filter(s => s !== st) : [...p.states, st]
                        }))}
                          className={`px-3 py-1.5 rounded text-[10px] font-bold border transition ${
                            newEvent.states.includes(st) ? 'bg-red-600/20 text-red-400 border-red-500/50' : 'bg-[#0a1628] text-gray-500 border-[#1e3a5f] hover:text-white'
                          }`}
                        >{st}</button>
                      ))}
                    </div>
                  </FormField>
                </div>
                <div className="flex gap-2 mt-4">
                  <button onClick={createEvent} className="px-4 py-2 bg-red-600 hover:bg-red-500 text-white text-xs font-bold rounded-lg transition">Declare Event</button>
                  <button onClick={() => setShowNewEvent(false)} className="px-4 py-2 bg-[#0a1628] border border-[#1e3a5f] text-gray-400 text-xs font-bold rounded-lg transition hover:text-white">Cancel</button>
                </div>
              </Card>
            )}

            {loading && <LoadingState label="Loading events…" />}
            {!loading && events.length === 0 && !showNewEvent && (
              <EmptyState message="No disaster events declared" hint="Click '+ New Event' to declare one, or check Disaster Watch for active threats" />
            )}
            {!loading && events.length > 0 && (
              <div className="space-y-2">
                {events.map(e => (
                  <button key={e.id} onClick={() => setSelectedEvent(e)}
                    className="w-full text-left bg-[#0f2040] rounded-xl border border-[#1e3a5f]/50 p-4 hover:border-red-500/30 transition"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <span className="text-xl">{e.type === 'Hurricane' ? '🌀' : e.type === 'Flood' ? '🌊' : e.type === 'Tornado' ? '🌪️' : e.type === 'Wildfire' ? '🔥' : e.type === 'Winter Storm' ? '❄️' : '⚠️'}</span>
                        <div>
                          <div className="text-sm font-bold text-white">{e.name}</div>
                          <div className="text-[10px] text-gray-500">{e.type} · {(e.states || []).join(', ')} · Started {e.start_date || '—'}</div>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        {e.fema_number && <span className="text-[10px] text-gray-500 bg-[#0a1628] px-2 py-0.5 rounded font-mono">{e.fema_number}</span>}
                        <StatusBadge status={e.severity} colors={SEVERITY_COLORS} />
                        <StatusBadge status={e.status} colors={EVENT_STATUS_COLORS} />
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    );
  };

  const renderEventDetail = () => {
    if (!selectedEvent) return null;
    const e = selectedEvent;
    const linkedCases = cases.filter(c => c.event_id === e.id || c.event_name === e.name);

    return (
      <div className="space-y-5">
        <button onClick={() => setSelectedEvent(null)} className="text-xs text-red-400 hover:text-red-300 font-bold">← Back to events</button>

        <Card>
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-3">
              <span className="text-3xl">{e.type === 'Hurricane' ? '🌀' : '⚠️'}</span>
              <div>
                <h2 className="text-xl font-black text-white">{e.name}</h2>
                <div className="flex items-center gap-3 mt-1 text-xs text-gray-400">
                  <span>{e.type}</span>
                  <span>📍 {(e.states || []).join(', ')}</span>
                  {e.fema_number && <span className="font-mono bg-[#0a1628] px-2 py-0.5 rounded">{e.fema_number}</span>}
                  {e.start_date && <span>Started {e.start_date}</span>}
                </div>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <StatusBadge status={e.severity} colors={SEVERITY_COLORS} />
              <StatusBadge status={e.status} colors={EVENT_STATUS_COLORS} />
            </div>
          </div>
        </Card>

        {/* Event Stats */}
        <div className="grid grid-cols-4 gap-3">
          <StatCard label="Linked Cases" value={linkedCases.length} sub={`${linkedCases.filter(c => c.status === 'Active').length} active`} color="#10b981" />
          <StatCard label="States" value={(e.states || []).length} sub={(e.states || []).join(', ')} color="#ef4444" />
          <StatCard label="Affected" value={e.affected_members || 0} sub="Members impacted" color="#d97706" />
          <StatCard label="Status" value={e.status} sub={e.severity} color={EVENT_STATUS_COLORS[e.status] || '#64748b'} />
        </div>

        {/* Linked Safe Haven Cases */}
        <Card title="Linked Safe Haven Cases" titleColor="#10b981">
          {linkedCases.length === 0 ? (
            <div className="text-sm text-gray-600 italic">No cases linked to this event yet</div>
          ) : (
            <div className="space-y-2">
              {linkedCases.map(c => (
                <div key={c.id} className="flex items-center justify-between bg-[#0a1628] rounded-lg px-4 py-2.5">
                  <div>
                    <span className="text-sm text-white font-medium">{c.member_name}</span>
                    <span className="text-xs text-gray-500 ml-2">{c.mco || '—'} · {c.state}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="flex gap-1">
                      {(c.needs || []).map(n => (
                        <span key={n} className="text-[9px] bg-[#1e3a5f] text-gray-300 px-1.5 py-0.5 rounded">{n}</span>
                      ))}
                    </div>
                    <StatusBadge status={c.status} colors={CASE_STATUS_COLORS} />
                  </div>
                </div>
              ))}
            </div>
          )}
        </Card>
      </div>
    );
  };

  // ═══════════════════════════════════════════════════════════════════════════
  // SECTION 3: SAFE HAVEN — Member Intake
  // ═══════════════════════════════════════════════════════════════════════════
  const renderSafeHaven = () => {
    if (selectedCase) return renderCaseDetail();

    return (
      <div className="space-y-4">
        {/* New Case Form */}
        {showNewCase && (
          <Card title="Open New Safe Haven" titleColor="#10b981">
            <div className="grid grid-cols-2 gap-4">
              <FormField label="Member Name" required>
                <input type="text" value={newCase.member_name} onChange={e => setNewCase(p => ({ ...p, member_name: e.target.value }))}
                  placeholder="Full name" className="form-input" />
              </FormField>
              <FormField label="Member ID">
                <input type="text" value={newCase.member_id} onChange={e => setNewCase(p => ({ ...p, member_id: e.target.value }))}
                  placeholder="Medicaid / MCO member ID" className="form-input" />
              </FormField>
              <FormField label="MCO">
                <select value={newCase.mco} onChange={e => setNewCase(p => ({ ...p, mco: e.target.value }))} className="form-input">
                  <option value="">— Select MCO —</option>
                  {mcos.map(m => <option key={m.id} value={m.fields.mco_name}>{m.fields.mco_name} ({m.fields.state})</option>)}
                </select>
              </FormField>
              <FormField label="Disaster Event">
                <select value={newCase.event_id} onChange={e => setNewCase(p => ({ ...p, event_id: e.target.value }))} className="form-input">
                  <option value="">— Select event —</option>
                  {activeEvents.map(e => <option key={e.id} value={e.id}>{e.name}</option>)}
                </select>
              </FormField>
              <FormField label="State">
                <select value={newCase.state} onChange={e => setNewCase(p => ({ ...p, state: e.target.value }))} className="form-input">
                  {STATES.map(st => <option key={st} value={st}>{STATE_NAMES[st]}</option>)}
                </select>
              </FormField>
              <FormField label="Needs">
                <div className="flex flex-wrap gap-1.5 mt-1">
                  {CASE_NEEDS.map(n => (
                    <button key={n} onClick={() => setNewCase(p => ({
                      ...p, needs: p.needs.includes(n) ? p.needs.filter(x => x !== n) : [...p.needs, n]
                    }))}
                      className={`px-2.5 py-1 rounded text-[10px] font-bold border transition ${
                        newCase.needs.includes(n) ? 'bg-emerald-600/20 text-emerald-400 border-emerald-500/50' : 'bg-[#0a1628] text-gray-500 border-[#1e3a5f] hover:text-white'
                      }`}
                    >{n}</button>
                  ))}
                </div>
              </FormField>
            </div>
            <div className="flex gap-2 mt-4">
              <button onClick={createCase} className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold rounded-lg transition">Open Safe Haven</button>
              <button onClick={() => setShowNewCase(false)} className="px-4 py-2 bg-[#0a1628] border border-[#1e3a5f] text-gray-400 text-xs font-bold rounded-lg transition hover:text-white">Cancel</button>
            </div>
          </Card>
        )}

        {/* Status counts */}
        <div className="grid grid-cols-5 gap-3">
          {CASE_STATUSES.map(s => (
            <StatCard key={s} label={s} value={cases.filter(c => c.status === s).length} sub="" color={CASE_STATUS_COLORS[s]} />
          ))}
        </div>

        {/* Cases Table */}
        {loading && <LoadingState label="Loading Safe Haven cases…" />}
        {!loading && cases.length === 0 && !showNewCase && (
          <EmptyState message="No Safe Haven cases" hint="Click '+ New Safe Haven' to open one" />
        )}
        {!loading && cases.length > 0 && (
          <div className="bg-[#0f2040] rounded-xl border border-[#1e3a5f]/50 overflow-hidden">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-[#1e3a5f]">
                  <th className="text-left px-4 py-3 text-[10px] text-gray-500 uppercase tracking-wider">Member</th>
                  <th className="text-left px-4 py-3 text-[10px] text-gray-500 uppercase tracking-wider">MCO</th>
                  <th className="text-left px-4 py-3 text-[10px] text-gray-500 uppercase tracking-wider">Event</th>
                  <th className="text-left px-4 py-3 text-[10px] text-gray-500 uppercase tracking-wider">State</th>
                  <th className="text-left px-4 py-3 text-[10px] text-gray-500 uppercase tracking-wider">Needs</th>
                  <th className="text-left px-4 py-3 text-[10px] text-gray-500 uppercase tracking-wider">Status</th>
                </tr>
              </thead>
              <tbody>
                {cases.map(c => (
                  <tr key={c.id} onClick={() => setSelectedCase(c)}
                    className="border-b border-[#1e3a5f]/30 hover:bg-[#1e3a5f]/20 transition cursor-pointer"
                  >
                    <td className="px-4 py-3">
                      <div className="text-white font-medium">{c.member_name}</div>
                      {c.member_id && <div className="text-[10px] text-gray-500 font-mono">{c.member_id}</div>}
                    </td>
                    <td className="px-4 py-3 text-gray-400 text-xs">{c.mco || '—'}</td>
                    <td className="px-4 py-3 text-gray-400 text-xs">{c.event_name || '—'}</td>
                    <td className="px-4 py-3"><span className="px-2 py-0.5 bg-[#0a1628] text-gray-300 rounded text-xs font-bold">{c.state}</span></td>
                    <td className="px-4 py-3">
                      <div className="flex gap-1 flex-wrap">
                        {(c.needs || []).slice(0, 3).map(n => (
                          <span key={n} className="text-[9px] bg-[#1e3a5f] text-gray-300 px-1.5 py-0.5 rounded">{n}</span>
                        ))}
                        {(c.needs || []).length > 3 && <span className="text-[9px] text-gray-600">+{c.needs.length - 3}</span>}
                      </div>
                    </td>
                    <td className="px-4 py-3"><StatusBadge status={c.status} colors={CASE_STATUS_COLORS} /></td>
                  </tr>
                ))}
              </tbody>
            </table>
            <div className="px-4 py-2 border-t border-[#1e3a5f] text-xs text-gray-500">{cases.length} Safe Haven case{cases.length !== 1 ? 's' : ''}</div>
          </div>
        )}
      </div>
    );
  };

  const renderCaseDetail = () => {
    if (!selectedCase) return null;
    const c = selectedCase;

    return (
      <div className="space-y-5">
        <button onClick={() => setSelectedCase(null)} className="text-xs text-emerald-400 hover:text-emerald-300 font-bold">← Back to Safe Haven</button>

        <Card>
          <div className="flex items-start justify-between">
            <div>
              <h2 className="text-xl font-black text-white">{c.member_name}</h2>
              <div className="flex items-center gap-3 mt-1 text-xs text-gray-400">
                {c.member_id && <span className="font-mono bg-[#0a1628] px-2 py-0.5 rounded">{c.member_id}</span>}
                {c.mco && <span>{c.mco}</span>}
                <span>📍 {STATE_NAMES[c.state] || c.state}</span>
                {c.event_name && <span>🌀 {c.event_name}</span>}
              </div>
            </div>
            <StatusBadge status={c.status} colors={CASE_STATUS_COLORS} />
          </div>
        </Card>

        {/* Service Needs */}
        <Card title="Service Needs" titleColor="#10b981">
          <div className="grid grid-cols-3 gap-3">
            {(c.needs || []).map(need => {
              const icon = need === 'Housing' ? '🏠' : need === 'Transport' ? '🚗' : need === 'Medical' ? '💊' : need === 'Pharmacy' ? '💊' : need === 'DME' ? '🦽' : need === 'Telehealth' ? '📱' : '🏥';
              const statusField = need === 'Housing' ? c.housing_status : need === 'Transport' ? c.transport_status : c.medical_status;
              return (
                <div key={need} className="bg-[#0a1628] rounded-lg p-4 border border-[#1e3a5f]">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="text-lg">{icon}</span>
                    <span className="text-sm font-bold text-white">{need}</span>
                  </div>
                  <StatusBadge status={statusField || 'Pending'} colors={{ Pending: '#d97706', Dispatched: '#3b82f6', Active: '#059669', Complete: '#64748b' }} />
                </div>
              );
            })}
          </div>
        </Card>

        {/* Status Pipeline */}
        <Card title="Case Status" titleColor="#10b981">
          <div className="flex items-stretch gap-0 rounded-lg overflow-hidden border border-[#1e3a5f]">
            {CASE_STATUSES.map((stage, i) => {
              const color = CASE_STATUS_COLORS[stage];
              const isCurrent = stage === c.status;
              const isPast = CASE_STATUSES.indexOf(stage) < CASE_STATUSES.indexOf(c.status as typeof CASE_STATUSES[number]);
              return (
                <div key={stage} className="flex-1 relative px-3 py-3 text-center border-r last:border-r-0 border-[#1e3a5f]"
                  style={{ backgroundColor: isCurrent ? `${color}30` : isPast ? `${color}10` : 'transparent' }}
                >
                  <div className="w-6 h-6 mx-auto rounded-full flex items-center justify-center text-[10px] font-black mb-1"
                    style={{ backgroundColor: isCurrent || isPast ? color : '#0a1628', color: isCurrent || isPast ? '#0a1628' : '#64748b' }}
                  >{isPast ? '✓' : i + 1}</div>
                  <div className="text-[10px] uppercase tracking-wider font-bold" style={{ color: isCurrent ? color : '#64748b' }}>{stage}</div>
                </div>
              );
            })}
          </div>
        </Card>

        {/* Notes */}
        <Card title="Case Notes" titleColor="#10b981">
          {c.notes ? (
            <div className="space-y-2">
              {c.notes.split('\n').filter((l: string) => l.trim()).map((line: string, i: number) => (
                <div key={i} className="text-sm text-gray-300 bg-[#0a1628] rounded-lg px-3 py-2 font-mono">{line}</div>
              ))}
            </div>
          ) : (
            <div className="text-sm text-gray-600 italic">No notes yet</div>
          )}
        </Card>
      </div>
    );
  };

  // ═══════════════════════════════════════════════════════════════════════════
  // SECTION 4: DISPATCH — Resource Deployment
  // ═══════════════════════════════════════════════════════════════════════════
  const renderDispatch = () => {
    const pendingCases = activeCases.filter(c => c.status === 'Intake' || c.status === 'Assessment' || c.status === 'Active');
    const availableTransport = transportPartners.filter(p => p.fields.agreement_status === 'Active' || p.fields.agreement_status === 'Signed');
    const availableHousing = housingPartners.filter(p => p.fields.agreement_status === 'Active' || p.fields.agreement_status === 'Signed');
    const availableMedical = medicalPartners.filter(p => p.fields.agreement_status === 'Active' || p.fields.agreement_status === 'Signed');

    return (
      <div className="space-y-6">
        {/* Resource Readiness */}
        <div className="grid grid-cols-3 gap-3">
          <StatCard label="🚗 Transport Ready" value={availableTransport.length} sub={`of ${transportPartners.length} partners`} color="#38bdf8" />
          <StatCard label="🏠 Housing Ready" value={availableHousing.length} sub={`of ${housingPartners.length} partners`} color="#d97706" />
          <StatCard label="💊 Medical Ready" value={availableMedical.length} sub={`of ${medicalPartners.length} partners`} color="#059669" />
        </div>

        {/* Cases Needing Dispatch */}
        <Card title={`Cases Needing Resources (${pendingCases.length})`} titleColor="#f97316">
          {pendingCases.length === 0 ? (
            <div className="text-sm text-gray-600 italic">No pending cases need dispatch right now</div>
          ) : (
            <div className="space-y-3">
              {pendingCases.map(c => (
                <div key={c.id} className="bg-[#0a1628] rounded-lg p-4 border border-[#1e3a5f]">
                  <div className="flex items-center justify-between mb-3">
                    <div>
                      <span className="text-sm font-bold text-white">{c.member_name}</span>
                      <span className="text-xs text-gray-500 ml-2">{c.mco || '—'} · {c.state}</span>
                    </div>
                    <StatusBadge status={c.status} colors={CASE_STATUS_COLORS} />
                  </div>
                  <div className="flex gap-2">
                    {(c.needs || []).map(need => {
                      const icon = need === 'Housing' ? '🏠' : need === 'Transport' ? '🚗' : '💊';
                      return (
                        <span key={need} className="inline-flex items-center gap-1 text-[10px] font-bold px-2 py-1 rounded border bg-[#1e3a5f]/30 border-[#1e3a5f] text-gray-300">
                          {icon} {need}
                        </span>
                      );
                    })}
                  </div>
                </div>
              ))}
            </div>
          )}
        </Card>

        {/* Available Resources by State */}
        <Card title="Available Resources by State" titleColor="#f97316">
          <div className="grid grid-cols-4 gap-4">
            {STATES.map(st => {
              const tCount = availableTransport.filter(p => (p.fields.states_served || []).includes(st) || p.fields.state === st).length;
              const hCount = availableHousing.filter(p => (p.fields.states_served || []).includes(st) || p.fields.state === st).length;
              const mCount = availableMedical.filter(p => (p.fields.states_served || []).includes(st) || p.fields.state === st).length;
              return (
                <div key={st} className="bg-[#0a1628] rounded-lg p-4 border border-[#1e3a5f]">
                  <div className="text-lg font-black text-white mb-2">{st}</div>
                  <div className="space-y-1 text-xs">
                    <div className="flex justify-between"><span className="text-gray-500">🚗 Transport</span><span className="text-sky-400 font-bold">{tCount}</span></div>
                    <div className="flex justify-between"><span className="text-gray-500">🏠 Housing</span><span className="text-amber-400 font-bold">{hCount}</span></div>
                    <div className="flex justify-between"><span className="text-gray-500">💊 Medical</span><span className="text-emerald-400 font-bold">{mCount}</span></div>
                  </div>
                </div>
              );
            })}
          </div>
        </Card>
      </div>
    );
  };

  // ═══════════════════════════════════════════════════════════════════════════
  // SECTION 5: NETWORK — Partner Registry
  // ═══════════════════════════════════════════════════════════════════════════
  const renderNetwork = () => {
    if (selectedPartner) return renderPartnerDetail();
    const nameField = partnerTypeFilter === 'housing' ? 'property_name' : 'company_name';

    return (
      <div className="space-y-4">
        <div className="flex items-center gap-2">
          {(['transport', 'housing', 'medical'] as PartnerType[]).map(type => (
            <button key={type} onClick={() => { setPartnerTypeFilter(type); setStateFilter(''); }}
              className={`px-4 py-2 rounded-lg text-xs font-bold uppercase tracking-wider transition border ${
                partnerTypeFilter === type ? 'bg-blue-600/20 text-blue-400 border-blue-500/50' : 'bg-[#0a1628] text-gray-400 border-[#1e3a5f] hover:text-white hover:border-blue-500/30'
              }`}
            >{type === 'transport' ? '🚗 Transport' : type === 'housing' ? '🏠 Housing' : '💊 Medical'}</button>
          ))}
          <div className="flex-1" />
          <div className="flex gap-1">
            <button onClick={() => setStateFilter('')} className={`px-3 py-1.5 rounded text-[10px] font-bold transition ${!stateFilter ? 'bg-blue-600 text-white' : 'bg-[#0a1628] text-gray-500 hover:text-white'}`}>All</button>
            {STATES.map(st => (
              <button key={st} onClick={() => setStateFilter(st)} className={`px-3 py-1.5 rounded text-[10px] font-bold transition ${stateFilter === st ? 'bg-blue-600 text-white' : 'bg-[#0a1628] text-gray-500 hover:text-white'}`}>{st}</button>
            ))}
          </div>
        </div>

        {loading && <LoadingState label="Loading partners…" />}
        {!loading && activePartners.length === 0 && (
          <EmptyState message={`No ${partnerTypeFilter} partners found${stateFilter ? ` in ${stateFilter}` : ''}`} />
        )}
        {!loading && activePartners.length > 0 && (
          <div className="bg-[#0f2040] rounded-xl border border-[#1e3a5f]/50 overflow-hidden">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-[#1e3a5f]">
                  <th className="text-left px-4 py-3 text-[10px] text-gray-500 uppercase tracking-wider">Name</th>
                  <th className="text-left px-4 py-3 text-[10px] text-gray-500 uppercase tracking-wider">Type</th>
                  <th className="text-left px-4 py-3 text-[10px] text-gray-500 uppercase tracking-wider">State(s)</th>
                  <th className="text-left px-4 py-3 text-[10px] text-gray-500 uppercase tracking-wider">Status</th>
                  <th className="text-left px-4 py-3 text-[10px] text-gray-500 uppercase tracking-wider">Last Contact</th>
                  <th className="text-left px-4 py-3 text-[10px] text-gray-500 uppercase tracking-wider">Next Follow-up</th>
                </tr>
              </thead>
              <tbody>
                {activePartners.map(p => (
                  <tr key={p.id} onClick={() => { setSelectedPartner(p); setSelectedPartnerType(partnerTypeFilter); }}
                    className="border-b border-[#1e3a5f]/30 hover:bg-[#1e3a5f]/20 transition cursor-pointer"
                  >
                    <td className="px-4 py-3 text-white font-medium">{p.fields[nameField] || '—'}</td>
                    <td className="px-4 py-3 text-gray-400 text-xs">{p.fields.partner_type || '—'}</td>
                    <td className="px-4 py-3 text-gray-400 text-xs">{Array.isArray(p.fields.states_served) ? p.fields.states_served.join(', ') : (p.fields.state || '—')}</td>
                    <td className="px-4 py-3"><StatusBadge status={p.fields.agreement_status || 'Prospect'} colors={PARTNER_STAGE_COLORS} /></td>
                    <td className="px-4 py-3 text-gray-400 text-xs">{p.fields.last_contact || '—'}</td>
                    <td className="px-4 py-3 text-xs">
                      {p.fields.next_follow_up ? (
                        <span className={new Date(p.fields.next_follow_up).getTime() < Date.now() ? 'text-red-400 font-bold' : 'text-gray-400'}>{p.fields.next_follow_up}</span>
                      ) : <span className="text-gray-600">—</span>}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            <div className="px-4 py-2 border-t border-[#1e3a5f] text-xs text-gray-500">{activePartners.length} {partnerTypeFilter} partner{activePartners.length !== 1 ? 's' : ''}</div>
          </div>
        )}
      </div>
    );
  };

  const renderPartnerDetail = () => {
    if (!selectedPartner) return null;
    const p = selectedPartner;
    const nameField = selectedPartnerType === 'housing' ? 'property_name' : 'company_name';
    const currentStatus = p.fields.agreement_status || 'Prospect';

    const handleGenerateOutreach = async () => {
      setOutreachLoading(true);
      try {
        const res = await api.generateHavenOutreach(selectedPartnerType, p.fields);
        setOutreachPackage(res.package);
        showToast('ok', 'Outreach package generated');
      } catch { showToast('err', 'Failed to generate outreach'); }
      setOutreachLoading(false);
    };

    const handleGenerateFollowup = async () => {
      setOutreachLoading(true);
      try {
        const res = await api.generateHavenFollowup(selectedPartnerType, p.fields, 7);
        setOutreachPackage(res.package);
        showToast('ok', 'Follow-up generated');
      } catch { showToast('err', 'Failed to generate follow-up'); }
      setOutreachLoading(false);
    };

    const handleSendOutreach = async () => {
      if (!outreachPackage) return;
      await addPartnerNote(selectedPartnerType, p, `Outreach package sent: "${outreachPackage.email_subject}"`);
      await updatePartnerStatus(selectedPartnerType, p.id, 'Outreach');
      setOutreachPackage(null);
      showToast('ok', 'Outreach sent — status updated to Outreach');
    };

    const handleGenerateNDA = async () => {
      setOutreachLoading(true);
      try {
        const res = await api.generateHavenNDA(selectedPartnerType, p.fields);
        await addPartnerNote(selectedPartnerType, p, `NDA generated — ready for DocuSign: ${res.nda?.partner_name}`);
        showToast('ok', 'NDA ready for DocuSign');
      } catch { showToast('err', 'Failed to generate NDA'); }
      setOutreachLoading(false);
    };

    const handleGenerateAgreement = async () => {
      setOutreachLoading(true);
      try {
        const res = await api.generateHavenAgreement(selectedPartnerType, p.fields);
        await addPartnerNote(selectedPartnerType, p, `Partnership agreement generated — ready for DocuSign: ${res.agreement?.partner_name}`);
        await updatePartnerStatus(selectedPartnerType, p.id, 'Negotiating');
        showToast('ok', 'Agreement ready for DocuSign');
      } catch { showToast('err', 'Failed to generate agreement'); }
      setOutreachLoading(false);
    };

    return (
      <div className="space-y-5">
        <button onClick={() => { setSelectedPartner(null); setOutreachPackage(null); }} className="text-xs text-blue-400 hover:text-blue-300 font-bold">← Back to list</button>

        {/* Partner Header */}
        <Card>
          <div className="flex items-start justify-between">
            <div>
              <h2 className="text-xl font-black text-white">{p.fields[nameField] || 'Partner'}</h2>
              <div className="flex items-center gap-3 mt-2 text-xs text-gray-400">
                <span>{p.fields.partner_type || selectedPartnerType}</span>
                {p.fields.state && <span>📍 {p.fields.state}</span>}
                {Array.isArray(p.fields.states_served) && <span>📍 {p.fields.states_served.join(', ')}</span>}
              </div>
            </div>
            <StatusBadge status={currentStatus} colors={PARTNER_STAGE_COLORS} />
          </div>
          <div className="grid grid-cols-3 gap-4 mt-4 pt-4 border-t border-[#1e3a5f]">
            <div><div className="text-[10px] text-gray-500 uppercase tracking-wider">Phone</div><div className="text-sm text-gray-300 mt-0.5">{p.fields.phone || p.fields.contact_phone || '—'}</div></div>
            <div><div className="text-[10px] text-gray-500 uppercase tracking-wider">Email</div><div className="text-sm text-gray-300 mt-0.5">{p.fields.email || p.fields.contact_email || '—'}</div></div>
            <div><div className="text-[10px] text-gray-500 uppercase tracking-wider">Contact</div><div className="text-sm text-gray-300 mt-0.5">{p.fields.contact_name || '—'}</div></div>
          </div>
        </Card>

        {/* Automated Outreach Actions */}
        <Card title="Automated Actions" titleColor="#f5c23e">
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
            {currentStatus === 'Prospect' && (
              <button onClick={handleGenerateOutreach} disabled={outreachLoading}
                className="bg-[#0a1628] rounded-lg p-4 border border-blue-500/30 hover:border-blue-500/60 transition text-left group">
                <div className="text-lg mb-1">📧</div>
                <div className="text-sm font-bold text-blue-400 group-hover:text-blue-300">Send Outreach</div>
                <div className="text-[10px] text-gray-500 mt-0.5">Email + one-pager package</div>
              </button>
            )}
            {(currentStatus === 'Prospect' || currentStatus === 'Outreach') && (
              <button onClick={handleGenerateFollowup} disabled={outreachLoading}
                className="bg-[#0a1628] rounded-lg p-4 border border-amber-500/30 hover:border-amber-500/60 transition text-left group">
                <div className="text-lg mb-1">🔄</div>
                <div className="text-sm font-bold text-amber-400 group-hover:text-amber-300">Send Follow-Up</div>
                <div className="text-[10px] text-gray-500 mt-0.5">Auto-cadence follow-up</div>
              </button>
            )}
            {(currentStatus === 'Outreach' || currentStatus === 'Negotiating') && (
              <button onClick={handleGenerateNDA} disabled={outreachLoading}
                className="bg-[#0a1628] rounded-lg p-4 border border-purple-500/30 hover:border-purple-500/60 transition text-left group">
                <div className="text-lg mb-1">🔒</div>
                <div className="text-sm font-bold text-purple-400 group-hover:text-purple-300">Send NDA</div>
                <div className="text-[10px] text-gray-500 mt-0.5">DocuSign electronic</div>
              </button>
            )}
            {(currentStatus === 'Negotiating' || currentStatus === 'Signed') && (
              <button onClick={handleGenerateAgreement} disabled={outreachLoading}
                className="bg-[#0a1628] rounded-lg p-4 border border-emerald-500/30 hover:border-emerald-500/60 transition text-left group">
                <div className="text-lg mb-1">📝</div>
                <div className="text-sm font-bold text-emerald-400 group-hover:text-emerald-300">Send Agreement</div>
                <div className="text-[10px] text-gray-500 mt-0.5">DocuSign partnership</div>
              </button>
            )}
            {currentStatus === 'Signed' && (
              <button onClick={() => updatePartnerStatus(selectedPartnerType, p.id, 'Active')}
                className="bg-[#0a1628] rounded-lg p-4 border border-emerald-500/30 hover:border-emerald-500/60 transition text-left group">
                <div className="text-lg mb-1">✅</div>
                <div className="text-sm font-bold text-emerald-400 group-hover:text-emerald-300">Activate</div>
                <div className="text-[10px] text-gray-500 mt-0.5">Add to live network</div>
              </button>
            )}
            {currentStatus === 'Active' && (
              <div className="bg-emerald-900/20 rounded-lg p-4 border border-emerald-500/30 col-span-2">
                <div className="text-sm font-bold text-emerald-400">✅ Active in HAVEN Network</div>
                <div className="text-[10px] text-gray-400 mt-0.5">This partner will receive dispatch during disaster activations</div>
              </div>
            )}
          </div>
          {outreachLoading && <div className="text-xs text-gray-500 mt-3 animate-pulse">Generating package…</div>}
        </Card>

        {/* Generated Outreach Preview */}
        {outreachPackage && (
          <Card title="Outreach Package Preview" titleColor="#3b82f6">
            <div className="space-y-3">
              <div>
                <div className="text-[10px] text-gray-500 uppercase tracking-wider mb-1">Subject</div>
                <div className="bg-[#0a1628] rounded-lg px-4 py-2 text-sm text-white border border-[#1e3a5f]">{outreachPackage.email_subject}</div>
              </div>
              <div>
                <div className="text-[10px] text-gray-500 uppercase tracking-wider mb-1">Email Body</div>
                <pre className="bg-[#0a1628] rounded-lg px-4 py-3 text-xs text-gray-300 whitespace-pre-wrap border border-[#1e3a5f] max-h-[40vh] overflow-y-auto font-sans leading-relaxed">{outreachPackage.email_body}</pre>
              </div>
              {outreachPackage.one_pager_available && (
                <div className="flex items-center gap-2 text-xs text-emerald-400">
                  <span>📎</span> One-pager attached
                </div>
              )}
              <div className="flex gap-2 pt-2 border-t border-[#1e3a5f]">
                <button onClick={handleSendOutreach} className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold rounded-lg transition">
                  Send & Update Status →
                </button>
                <button onClick={() => { navigator.clipboard.writeText(`Subject: ${outreachPackage.email_subject}\n\n${outreachPackage.email_body}`); showToast('ok', 'Copied to clipboard'); }}
                  className="px-4 py-2 bg-[#0a1628] border border-[#1e3a5f] text-gray-300 text-xs font-bold rounded-lg transition hover:text-white">
                  📋 Copy
                </button>
                <button onClick={() => setOutreachPackage(null)} className="px-4 py-2 bg-[#0a1628] border border-[#1e3a5f] text-gray-400 text-xs font-bold rounded-lg transition hover:text-white">
                  Dismiss
                </button>
              </div>
            </div>
          </Card>
        )}

        {/* Pipeline Status */}
        <Card title="Pipeline Status" titleColor="#2563eb">
          <div className="flex items-stretch gap-0 rounded-lg overflow-hidden border border-[#1e3a5f]">
            {PARTNER_STAGES.map((stage, i) => {
              const color = PARTNER_STAGE_COLORS[stage];
              const isCurrent = stage === currentStatus;
              const isPast = PARTNER_STAGES.indexOf(stage) < PARTNER_STAGES.indexOf(currentStatus as PartnerStage);
              return (
                <button key={stage} onClick={() => updatePartnerStatus(selectedPartnerType, p.id, stage)}
                  className="flex-1 px-3 py-3 text-center border-r last:border-r-0 border-[#1e3a5f] transition hover:brightness-125"
                  style={{ backgroundColor: isCurrent ? `${color}30` : isPast ? `${color}10` : 'transparent' }}
                >
                  <div className="w-6 h-6 mx-auto rounded-full flex items-center justify-center text-[10px] font-black mb-1"
                    style={{ backgroundColor: isCurrent || isPast ? color : '#0a1628', color: isCurrent || isPast ? '#0a1628' : '#64748b', boxShadow: isCurrent ? `0 0 0 3px ${color}33` : 'none' }}
                  >{isPast ? '✓' : i + 1}</div>
                  <div className="text-[10px] uppercase tracking-wider font-bold" style={{ color: isCurrent ? color : '#64748b' }}>{stage}</div>
                </button>
              );
            })}
          </div>
        </Card>

        {/* Quick Log + Follow-up */}
        <div className="flex gap-2">
          <button onClick={() => addPartnerNote(selectedPartnerType, p, 'Called — left voicemail')} className="px-3 py-2 bg-[#0f2040] border border-[#1e3a5f] rounded-lg text-xs font-bold text-gray-300 hover:text-white hover:border-blue-500/50 transition">📞 Log Call</button>
          <button onClick={() => addPartnerNote(selectedPartnerType, p, 'Sent partnership inquiry email')} className="px-3 py-2 bg-[#0f2040] border border-[#1e3a5f] rounded-lg text-xs font-bold text-gray-300 hover:text-white hover:border-blue-500/50 transition">📧 Log Email</button>
          <div className="flex items-center gap-2 ml-auto">
            <input type="date" value={followUpDate} onChange={e => setFollowUpDate(e.target.value)} className="form-input !w-auto" />
            <button onClick={async () => { if (!followUpDate) return; try { await api.updateHavenPartner(selectedPartnerType, p.id, { next_follow_up: followUpDate }); showToast('ok', `Follow-up: ${followUpDate}`); setFollowUpDate(''); loadPartners(selectedPartnerType); } catch { showToast('err', 'Failed'); } }}
              disabled={!followUpDate} className="px-3 py-2 bg-[#0f2040] border border-[#1e3a5f] rounded-lg text-xs font-bold text-gray-300 hover:text-white hover:border-blue-500/50 transition disabled:opacity-40">📅 Set Follow-up</button>
          </div>
        </div>

        {/* Add Note */}
        <Card title="Add Note" titleColor="#2563eb">
          <div className="flex gap-2">
            <input type="text" value={noteInput} onChange={e => setNoteInput(e.target.value)} onKeyDown={e => { if (e.key === 'Enter') addPartnerNote(selectedPartnerType, p, noteInput); }}
              placeholder="Type a note…" className="form-input flex-1" />
            <button onClick={() => addPartnerNote(selectedPartnerType, p, noteInput)} disabled={!noteInput.trim()} className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold rounded-lg transition disabled:opacity-40">Add</button>
          </div>
        </Card>

        {/* Activity Log */}
        <Card title="Activity Log" titleColor="#2563eb">
          {p.fields.notes ? (
            <div className="space-y-2">
              {p.fields.notes.split('\n').filter((l: string) => l.trim()).map((line: string, i: number) => (
                <div key={i} className="text-sm text-gray-300 bg-[#0a1628] rounded-lg px-3 py-2 font-mono">{line}</div>
              ))}
            </div>
          ) : <div className="text-sm text-gray-600 italic">No activity logged yet</div>}
        </Card>
      </div>
    );
  };

  // ═══════════════════════════════════════════════════════════════════════════
  // SECTION 6: MCO CONTRACTS
  // ═══════════════════════════════════════════════════════════════════════════
  const renderMCOs = () => {
    if (selectedMCO) return renderMCODetail();

    return (
      <div className="space-y-4">
        <div className="flex gap-1">
          <button onClick={() => setStateFilter('')} className={`px-3 py-1.5 rounded text-[10px] font-bold transition ${!stateFilter ? 'bg-purple-600 text-white' : 'bg-[#0a1628] text-gray-500 hover:text-white'}`}>All</button>
          {STATES.map(st => (
            <button key={st} onClick={() => setStateFilter(st)} className={`px-3 py-1.5 rounded text-[10px] font-bold transition ${stateFilter === st ? 'bg-purple-600 text-white' : 'bg-[#0a1628] text-gray-500 hover:text-white'}`}>{st}</button>
          ))}
        </div>

        {loading && <LoadingState label="Loading MCOs…" />}
        {!loading && mcos.length === 0 && <EmptyState message={`No MCOs found${stateFilter ? ` in ${stateFilter}` : ''}`} />}
        {!loading && mcos.length > 0 && (
          <div className="bg-[#0f2040] rounded-xl border border-[#1e3a5f]/50 overflow-hidden">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-[#1e3a5f]">
                  <th className="text-left px-4 py-3 text-[10px] text-gray-500 uppercase tracking-wider">MCO Name</th>
                  <th className="text-left px-4 py-3 text-[10px] text-gray-500 uppercase tracking-wider">Parent</th>
                  <th className="text-left px-4 py-3 text-[10px] text-gray-500 uppercase tracking-wider">State</th>
                  <th className="text-left px-4 py-3 text-[10px] text-gray-500 uppercase tracking-wider">Members</th>
                  <th className="text-left px-4 py-3 text-[10px] text-gray-500 uppercase tracking-wider">Contract</th>
                  <th className="text-left px-4 py-3 text-[10px] text-gray-500 uppercase tracking-wider">Last Contact</th>
                </tr>
              </thead>
              <tbody>
                {mcos.map(m => (
                  <tr key={m.id} onClick={() => setSelectedMCO(m)} className="border-b border-[#1e3a5f]/30 hover:bg-[#1e3a5f]/20 transition cursor-pointer">
                    <td className="px-4 py-3 text-white font-medium">{m.fields.mco_name || '—'}</td>
                    <td className="px-4 py-3 text-gray-400 text-xs">{m.fields.parent_company || '—'}</td>
                    <td className="px-4 py-3"><span className="px-2 py-0.5 bg-[#0a1628] text-gray-300 rounded text-xs font-bold">{m.fields.state}</span></td>
                    <td className="px-4 py-3 text-gray-400 text-xs">{m.fields.member_count ? `${(m.fields.member_count / 1000).toFixed(0)}K` : '—'}</td>
                    <td className="px-4 py-3"><StatusBadge status={m.fields.contract_status || 'Target'} colors={MCO_STAGE_COLORS} /></td>
                    <td className="px-4 py-3 text-gray-400 text-xs">{m.fields.last_contact || '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            <div className="px-4 py-2 border-t border-[#1e3a5f] text-xs text-gray-500">{mcos.length} MCO{mcos.length !== 1 ? 's' : ''}</div>
          </div>
        )}
      </div>
    );
  };

  const renderMCODetail = () => {
    if (!selectedMCO) return null;
    const m = selectedMCO;
    const currentStatus = m.fields.contract_status || 'Target';
    const credChecklist = [
      { key: 'cred_application', label: 'Application Submitted' },
      { key: 'cred_nda', label: 'NDA Signed' },
      { key: 'cred_insurance', label: 'Insurance Verified' },
      { key: 'cred_portal', label: 'Portal Access' },
      { key: 'cred_rate_sheet', label: 'Rate Sheet Received' },
    ];

    return (
      <div className="space-y-5">
        <button onClick={() => { setSelectedMCO(null); setOutreachPackage(null); }} className="text-xs text-purple-400 hover:text-purple-300 font-bold">← Back to list</button>

        <Card>
          <div className="flex items-start justify-between">
            <div>
              <h2 className="text-xl font-black text-white">{m.fields.mco_name || 'MCO'}</h2>
              <div className="flex items-center gap-3 mt-2 text-xs text-gray-400">
                {m.fields.parent_company && <span>Parent: {m.fields.parent_company}</span>}
                {m.fields.state && <span>📍 {STATE_NAMES[m.fields.state] || m.fields.state}</span>}
                {m.fields.member_count && <span>👥 {(m.fields.member_count / 1000).toFixed(0)}K members</span>}
              </div>
            </div>
            <StatusBadge status={currentStatus} colors={MCO_STAGE_COLORS} />
          </div>
          <div className="grid grid-cols-3 gap-4 mt-4 pt-4 border-t border-[#1e3a5f]">
            <div><div className="text-[10px] text-gray-500 uppercase tracking-wider">Contact</div><div className="text-sm text-gray-300 mt-0.5">{m.fields.contact_name || '—'}</div></div>
            <div><div className="text-[10px] text-gray-500 uppercase tracking-wider">Email</div><div className="text-sm text-gray-300 mt-0.5">{m.fields.contact_email || '—'}</div></div>
            <div><div className="text-[10px] text-gray-500 uppercase tracking-wider">Phone</div><div className="text-sm text-gray-300 mt-0.5">{m.fields.contact_phone || '—'}</div></div>
          </div>
        </Card>

        <Card title="Contract Pipeline" titleColor="#8b5cf6">
          <div className="flex items-stretch gap-0 rounded-lg overflow-hidden border border-[#1e3a5f]">
            {MCO_STAGES.map((stage, i) => {
              const color = MCO_STAGE_COLORS[stage];
              const isCurrent = stage === currentStatus;
              const isPast = MCO_STAGES.indexOf(stage) < MCO_STAGES.indexOf(currentStatus as MCOStage);
              return (
                <button key={stage} onClick={() => updateMCOStatus(m.id, stage)}
                  className="flex-1 px-3 py-3 text-center border-r last:border-r-0 border-[#1e3a5f] transition hover:brightness-125"
                  style={{ backgroundColor: isCurrent ? `${color}30` : isPast ? `${color}10` : 'transparent' }}
                >
                  <div className="w-6 h-6 mx-auto rounded-full flex items-center justify-center text-[10px] font-black mb-1"
                    style={{ backgroundColor: isCurrent || isPast ? color : '#0a1628', color: isCurrent || isPast ? '#0a1628' : '#64748b', boxShadow: isCurrent ? `0 0 0 3px ${color}33` : 'none' }}
                  >{isPast ? '✓' : i + 1}</div>
                  <div className="text-[10px] uppercase tracking-wider font-bold" style={{ color: isCurrent ? color : '#64748b' }}>{stage}</div>
                </button>
              );
            })}
          </div>
        </Card>

        {/* Automated MCO Outreach */}
        <Card title="Automated Outreach" titleColor="#f5c23e">
          <div className="grid grid-cols-2 lg:grid-cols-3 gap-3">
            {currentStatus === 'Target' && (
              <button onClick={async () => {
                setOutreachLoading(true);
                try {
                  const res = await api.generateHavenOutreach('mco', m.fields);
                  setOutreachPackage(res.package);
                  showToast('ok', 'MCO outreach package generated');
                } catch { showToast('err', 'Failed to generate outreach'); }
                setOutreachLoading(false);
              }} disabled={outreachLoading}
                className="bg-[#0a1628] rounded-lg p-4 border border-purple-500/30 hover:border-purple-500/60 transition text-left group">
                <div className="text-lg mb-1">📧</div>
                <div className="text-sm font-bold text-purple-400 group-hover:text-purple-300">Send Pitch</div>
                <div className="text-[10px] text-gray-500 mt-0.5">TPA pitch + network overview</div>
              </button>
            )}
            {(currentStatus === 'Target' || currentStatus === 'Outreach') && (
              <button onClick={async () => {
                setOutreachLoading(true);
                try {
                  const res = await api.generateHavenFollowup('mco', m.fields, 7);
                  setOutreachPackage(res.package);
                  showToast('ok', 'Follow-up generated');
                } catch { showToast('err', 'Failed'); }
                setOutreachLoading(false);
              }} disabled={outreachLoading}
                className="bg-[#0a1628] rounded-lg p-4 border border-amber-500/30 hover:border-amber-500/60 transition text-left group">
                <div className="text-lg mb-1">🔄</div>
                <div className="text-sm font-bold text-amber-400 group-hover:text-amber-300">Follow-Up</div>
                <div className="text-[10px] text-gray-500 mt-0.5">Auto-cadence follow-up</div>
              </button>
            )}
            {currentStatus === 'Active' && (
              <div className="bg-emerald-900/20 rounded-lg p-4 border border-emerald-500/30 col-span-2">
                <div className="text-sm font-bold text-emerald-400">✅ Active MCO Contract</div>
                <div className="text-[10px] text-gray-400 mt-0.5">Billing and dispatch active for this MCO</div>
              </div>
            )}
          </div>
          {outreachLoading && <div className="text-xs text-gray-500 mt-3 animate-pulse">Generating package…</div>}
        </Card>

        {/* MCO Outreach Preview */}
        {outreachPackage && section === 'mcos' && (
          <Card title="MCO Outreach Preview" titleColor="#8b5cf6">
            <div className="space-y-3">
              <div>
                <div className="text-[10px] text-gray-500 uppercase tracking-wider mb-1">Subject</div>
                <div className="bg-[#0a1628] rounded-lg px-4 py-2 text-sm text-white border border-[#1e3a5f]">{outreachPackage.email_subject}</div>
              </div>
              <div>
                <div className="text-[10px] text-gray-500 uppercase tracking-wider mb-1">Email Body</div>
                <pre className="bg-[#0a1628] rounded-lg px-4 py-3 text-xs text-gray-300 whitespace-pre-wrap border border-[#1e3a5f] max-h-[40vh] overflow-y-auto font-sans leading-relaxed">{outreachPackage.email_body}</pre>
              </div>
              <div className="flex gap-2 pt-2 border-t border-[#1e3a5f]">
                <button onClick={async () => {
                  await addMCONote(m, `MCO outreach sent: "${outreachPackage.email_subject}"`);
                  await updateMCOStatus(m.id, 'Outreach');
                  setOutreachPackage(null);
                  showToast('ok', 'MCO outreach sent — status updated');
                }} className="px-4 py-2 bg-purple-600 hover:bg-purple-500 text-white text-xs font-bold rounded-lg transition">Send & Update Status →</button>
                <button onClick={() => { navigator.clipboard.writeText(`Subject: ${outreachPackage.email_subject}\n\n${outreachPackage.email_body}`); showToast('ok', 'Copied'); }}
                  className="px-4 py-2 bg-[#0a1628] border border-[#1e3a5f] text-gray-300 text-xs font-bold rounded-lg transition hover:text-white">📋 Copy</button>
                <button onClick={() => setOutreachPackage(null)} className="px-4 py-2 bg-[#0a1628] border border-[#1e3a5f] text-gray-400 text-xs font-bold rounded-lg transition hover:text-white">Dismiss</button>
              </div>
            </div>
          </Card>
        )}

        <Card title="Credentialing Checklist" titleColor="#8b5cf6">
          <div className="space-y-2">
            {credChecklist.map(item => {
              const checked = !!m.fields[item.key];
              return (
                <label key={item.key} className="flex items-center gap-3 cursor-pointer group">
                  <div className={`w-5 h-5 rounded border-2 flex items-center justify-center transition ${checked ? 'bg-purple-600 border-purple-500' : 'border-[#1e3a5f] group-hover:border-purple-500/50'}`}
                    onClick={async () => { try { await api.updateHavenMCO(m.id, { [item.key]: !checked }); setSelectedMCO({ ...m, fields: { ...m.fields, [item.key]: !checked } }); showToast('ok', `${item.label}: ${!checked ? 'Done' : 'Unchecked'}`); } catch { showToast('err', 'Failed'); } }}
                  >{checked && <span className="text-white text-xs font-black">✓</span>}</div>
                  <span className={`text-sm ${checked ? 'text-gray-300 line-through' : 'text-white'}`}>{item.label}</span>
                </label>
              );
            })}
          </div>
        </Card>

        <Card title="Add Note" titleColor="#8b5cf6">
          <div className="flex gap-2">
            <input type="text" value={noteInput} onChange={e => setNoteInput(e.target.value)} onKeyDown={e => { if (e.key === 'Enter') addMCONote(m, noteInput); }}
              placeholder="Type a note…" className="form-input flex-1" />
            <button onClick={() => addMCONote(m, noteInput)} disabled={!noteInput.trim()} className="px-4 py-2 bg-purple-600 hover:bg-purple-500 text-white text-xs font-bold rounded-lg transition disabled:opacity-40">Add</button>
          </div>
        </Card>

        <Card title="Activity Log" titleColor="#8b5cf6">
          {m.fields.notes ? (
            <div className="space-y-2">
              {m.fields.notes.split('\n').filter((l: string) => l.trim()).map((line: string, i: number) => (
                <div key={i} className="text-sm text-gray-300 bg-[#0a1628] rounded-lg px-3 py-2 font-mono">{line}</div>
              ))}
            </div>
          ) : <div className="text-sm text-gray-600 italic">No activity logged yet</div>}
        </Card>
      </div>
    );
  };

  // ═══════════════════════════════════════════════════════════════════════════
  // SECTION 7: BILLING — Claims & Revenue
  // ═══════════════════════════════════════════════════════════════════════════
  const renderBilling = () => {
    const closedCases = cases.filter(c => c.status === 'Closed' || c.status === 'Stabilized');
    const activeMCOs = mcos.filter(m => m.fields.contract_status === 'Active');

    return (
      <div className="space-y-6">
        <div className="grid grid-cols-4 gap-3">
          <StatCard label="Billable Cases" value={closedCases.length} sub="Stabilized + Closed" color="#14b8a6" />
          <StatCard label="Active MCOs" value={activeMCOs.length} sub="Ready for billing" color="#8b5cf6" />
          <StatCard label="Total Cases" value={cases.length} sub={`${activeCases.length} active`} color="#10b981" />
          <StatCard label="States" value={STATES.length} sub="FL · TX · LA · MI" color="#2563eb" />
        </div>

        <Card title="Billing Pipeline" titleColor="#14b8a6">
          <div className="text-sm text-gray-400 mb-4">Cases ready for MCO claims submission</div>
          {closedCases.length === 0 ? (
            <div className="text-sm text-gray-600 italic py-4">No cases ready for billing yet — complete Safe Haven cases to generate claims</div>
          ) : (
            <div className="space-y-2">
              {closedCases.map(c => (
                <div key={c.id} className="flex items-center justify-between bg-[#0a1628] rounded-lg px-4 py-3">
                  <div>
                    <span className="text-sm text-white font-medium">{c.member_name}</span>
                    <span className="text-xs text-gray-500 ml-2">{c.mco || '—'} · {c.state}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="flex gap-1">
                      {(c.needs || []).map(n => <span key={n} className="text-[9px] bg-[#1e3a5f] text-gray-300 px-1.5 py-0.5 rounded">{n}</span>)}
                    </div>
                    <StatusBadge status={c.status} colors={CASE_STATUS_COLORS} />
                  </div>
                </div>
              ))}
            </div>
          )}
        </Card>

        <Card title="MCO Billing Readiness" titleColor="#14b8a6">
          <div className="space-y-2">
            {mcos.map(m => {
              const mcoCases = cases.filter(c => c.mco === m.fields.mco_name);
              const billable = mcoCases.filter(c => c.status === 'Closed' || c.status === 'Stabilized').length;
              return (
                <div key={m.id} className="flex items-center justify-between bg-[#0a1628] rounded-lg px-4 py-3">
                  <div>
                    <span className="text-sm text-white font-medium">{m.fields.mco_name}</span>
                    <span className="text-xs text-gray-500 ml-2">{m.fields.state} · {m.fields.member_count ? `${(m.fields.member_count / 1000).toFixed(0)}K members` : '—'}</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="text-xs text-gray-400">{mcoCases.length} cases · {billable} billable</span>
                    <StatusBadge status={m.fields.contract_status || 'Target'} colors={MCO_STAGE_COLORS} />
                  </div>
                </div>
              );
            })}
          </div>
        </Card>
      </div>
    );
  };

  // ═══════════════════════════════════════════════════════════════════════════
  // MAIN RENDER
  // ═══════════════════════════════════════════════════════════════════════════
  const clearSelections = () => {
    setSelectedPartner(null); setSelectedMCO(null); setSelectedEvent(null); setSelectedCase(null);
    setShowNewEvent(false); setShowNewCase(false);
  };

  const primaryAction = useMemo(() => {
    switch (mappedTab) {
      case 'events': return { label: '+ New Event', onClick: () => setShowNewEvent(true), color: '#ef4444' };
      case 'safehaven': return { label: '+ New Safe Haven', onClick: () => setShowNewCase(true), color: '#10b981' };
      default: return null;
    }
  }, [mappedTab]);

  return (
    <div className="flex min-h-screen bg-[#0a1628] text-white">
      {/* ───────── LEFT SIDEBAR ───────── */}
      <aside className="w-64 bg-[#0f2040] border-r border-[#1e3a5f]/70 flex flex-col sticky top-0 h-screen">
        <div className="px-5 py-5 border-b border-[#1e3a5f]/70">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-[#2563eb] to-[#059669] border border-[#2563eb]/50 flex items-center justify-center shadow-[0_2px_0_0_rgba(0,0,0,0.25)]">
              <span className="text-lg">🏠</span>
            </div>
            <div className="leading-tight min-w-0">
              <div className="text-base font-black tracking-wide text-white">HAVEN</div>
              <div className="text-[9px] text-gray-400 tracking-wider uppercase font-bold mt-0.5 leading-snug">
                Housing · Assistance · Vital<br />Emergency Network
              </div>
            </div>
          </div>
          <div className="mt-4 pt-4 border-t border-[#1e3a5f]/70">
            <div className="text-[10px] uppercase tracking-widest text-gray-500 mb-1 font-bold">Operated by</div>
            <div className="text-xs font-black text-white tracking-wider">DEE DAVIS INC</div>
            <div className="text-[9px] text-gray-500 mt-1">Disaster Response TPA · FL · TX · LA · MI</div>
          </div>
        </div>

        {/* Readiness indicator + Watch */}
        <div className="px-4 py-3 border-b border-[#1e3a5f]/70">
          <div className="flex items-center gap-2">
            {(() => {
              const tl = watchFeed?.threat_level || 'None';
              const hasActive = activeEvents.some(e => e.status === 'Active');
              const isDanger = tl === 'Major Disaster' || tl === 'Emergency' || hasActive;
              const isWarning = tl === 'Warning';
              return (<>
                <span className={`w-2 h-2 rounded-full ${isDanger ? 'bg-red-400 animate-pulse' : isWarning ? 'bg-amber-400 animate-pulse' : 'bg-emerald-400'}`} />
                <span className={`text-[10px] uppercase tracking-wider font-bold ${isDanger ? 'text-red-400' : isWarning ? 'text-amber-400' : 'text-emerald-400'}`}>
                  {isDanger ? (hasActive ? 'Active Disaster' : `Watch: ${tl}`) : isWarning ? 'Weather Warning' : 'Standby — Network Building'}
                </span>
              </>);
            })()}
          </div>
          <div className="text-[9px] text-gray-500 mt-1">
            {allPartners.length} partners · {mcos.length} MCOs · {watchFeed?.total_alerts || 0} NWS alerts
          </div>
        </div>

        <nav className="flex-1 px-2 py-3 overflow-y-auto">
          {SECTIONS.map((s) => {
            const active = mappedTab === s.id;
            const tint = s.color;
            return (
              <button key={s.id} onClick={() => { setActiveTab(s.id); clearSelections(); }}
                className={`w-full group flex items-center gap-3 px-3 py-2.5 rounded-lg mb-0.5 transition text-left relative ${active ? 'border' : 'border border-transparent hover:bg-[#1e3a5f]/40'}`}
                style={active ? { backgroundColor: `${tint}1A`, borderColor: `${tint}66` } : undefined}
              >
                {active && <span className="absolute left-0 top-2 bottom-2 w-[3px] rounded-r" style={{ backgroundColor: tint }} />}
                <span className="w-8 h-8 rounded-md flex items-center justify-center font-black text-xs shrink-0 transition"
                  style={active ? { backgroundColor: tint, color: '#0a1628' } : { backgroundColor: '#0a1628', color: '#64748b' }}
                >{s.glyph}</span>
                <span className="flex-1 min-w-0">
                  <span className={`block text-sm font-bold ${active ? 'text-white' : 'text-slate-200'}`}>{s.label}</span>
                  <span className="block text-[10px]" style={{ color: active ? tint : '#64748b' }}>{s.sub}</span>
                </span>
              </button>
            );
          })}
        </nav>

        <div className="px-4 py-4 border-t border-[#1e3a5f]/70">
          <button onClick={onBackToNexus} className="w-full text-left text-xs font-bold text-gray-500 hover:text-white transition px-2 py-1.5 rounded hover:bg-[#1e3a5f]/40">← Back to NEXUS</button>
        </div>
      </aside>

      {/* ───────── MAIN CONTENT ───────── */}
      <div className="flex-1 flex flex-col min-w-0">
        <header className="bg-[#0f2040]/80 backdrop-blur border-b border-[#1e3a5f]/70 px-8 py-4 sticky top-0 z-20">
          <div className="flex items-center justify-between gap-6">
            <div className="flex items-center gap-3">
              <span className="w-1 h-10 rounded-full" style={{ backgroundColor: sectionColor(mappedTab) }} />
              <div>
                <div className="text-[10px] uppercase tracking-[0.25em] font-bold" style={{ color: sectionColor(mappedTab) }}>
                  {SECTIONS.find(s => s.id === mappedTab)?.label || 'Command'}
                  {(selectedPartner || selectedMCO || selectedEvent || selectedCase) ? ' / Detail' : ''}
                </div>
                <div className="text-xl font-black text-white mt-0.5">{sectionTitle(mappedTab)}</div>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <span className="inline-flex items-center gap-2 text-[10px] font-bold uppercase tracking-widest px-2.5 py-1 rounded bg-emerald-900/50 text-emerald-300">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />Live
              </span>
              <button onClick={() => { loadStatus(); if (mappedTab === 'network') loadPartners(partnerTypeFilter); else if (mappedTab === 'mcos') loadMCOs(); else if (mappedTab === 'events') loadEvents(); else if (mappedTab === 'safehaven') loadCases(); }}
                disabled={loading} className="text-xs font-semibold text-slate-200 hover:text-white bg-[#0a1628] hover:bg-[#1e3a5f] border border-[#1e3a5f] rounded-md px-3 py-1.5 disabled:opacity-50"
              >{loading ? 'Syncing…' : 'Refresh'}</button>
              {primaryAction && (
                <button onClick={primaryAction.onClick}
                  className="text-sm font-black px-4 py-2 rounded-md shadow-[0_2px_0_0_rgba(0,0,0,0.25)]"
                  style={{ backgroundColor: primaryAction.color, color: '#fff' }}
                >{primaryAction.label}</button>
              )}
            </div>
          </div>
        </header>

        {toast && (
          <div className={`fixed top-6 right-8 z-50 px-4 py-2 rounded-md shadow-lg border text-sm font-semibold ${
            toast.tone === 'ok' ? 'bg-emerald-900/90 border-emerald-600 text-emerald-50' :
            toast.tone === 'err' ? 'bg-rose-900/90 border-rose-600 text-rose-50' :
            'bg-[#0f2040] border-[#1e3a5f] text-slate-100'
          }`}>{toast.message}</div>
        )}

        <main className="flex-1 px-8 py-6 overflow-y-auto">
          {mappedTab === 'command' && renderCommand()}
          {mappedTab === 'events' && renderEvents()}
          {mappedTab === 'safehaven' && renderSafeHaven()}
          {mappedTab === 'dispatch' && renderDispatch()}
          {mappedTab === 'network' && renderNetwork()}
          {mappedTab === 'mcos' && renderMCOs()}
          {mappedTab === 'billing' && renderBilling()}
        </main>
      </div>

      {/* Global styles for form inputs */}
      <style>{`
        .form-input {
          width: 100%;
          background: #0a1628;
          border: 1px solid #1e3a5f;
          border-radius: 0.5rem;
          padding: 0.5rem 0.75rem;
          font-size: 0.8125rem;
          color: white;
          outline: none;
          transition: border-color 0.2s;
        }
        .form-input::placeholder { color: #4b5563; }
        .form-input:focus { border-color: #2563eb; }
      `}</style>
    </div>
  );
};

// ──────────────────────────────────────────────────────────────────────────
// Shared Components
// ──────────────────────────────────────────────────────────────────────────
const StatCard: React.FC<{ label: string; value: number | string; sub: string; color: string }> = ({ label, value, sub, color }) => (
  <div className="bg-[#0f2040] rounded-xl border border-[#1e3a5f]/50 p-4">
    <div className="text-2xl font-black" style={{ color }}>{value}</div>
    <div className="text-[10px] uppercase tracking-wider text-gray-500 mt-1 font-bold">{label}</div>
    {sub && <div className="text-[10px] text-gray-600 mt-0.5">{sub}</div>}
  </div>
);

const StatusBadge: React.FC<{ status: string; colors: Record<string, string> }> = ({ status, colors }) => {
  const color = colors[status] || '#64748b';
  return (
    <span className="inline-flex items-center gap-1.5 text-[10px] font-black tracking-wider uppercase px-2 py-0.5 rounded border"
      style={{ backgroundColor: `${color}15`, borderColor: `${color}80`, color }}>
      <span className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: color }} />{status}
    </span>
  );
};

const Card: React.FC<{ title?: string; titleColor?: string; children: React.ReactNode }> = ({ title, titleColor, children }) => (
  <div className="bg-[#0f2040] rounded-xl border border-[#1e3a5f]/50 p-5">
    {title && <h3 className="text-xs font-black uppercase tracking-wider mb-4" style={{ color: titleColor || '#f5c23e' }}>{title}</h3>}
    {children}
  </div>
);

const FormField: React.FC<{ label: string; required?: boolean; children: React.ReactNode }> = ({ label, required, children }) => (
  <div>
    <label className="text-[10px] text-gray-500 uppercase tracking-wider block mb-1.5 font-bold">
      {label}{required && <span className="text-red-400 ml-0.5">*</span>}
    </label>
    {children}
  </div>
);

const PipelineFunnel: React.FC<{ stages: string[]; counts: Record<string, number>; colors: Record<string, string> }> = ({ stages, counts, colors }) => (
  <div className="flex items-stretch gap-0 rounded-lg overflow-hidden border border-[#1e3a5f]">
    {stages.map((stage, i) => {
      const count = counts[stage] || 0;
      const color = colors[stage] || '#64748b';
      return (
        <div key={stage} className="flex-1 relative px-3 py-3 text-center border-r last:border-r-0 border-[#1e3a5f]"
          style={{ backgroundColor: count > 0 ? `${color}15` : 'transparent' }}>
          <div className="text-2xl font-black" style={{ color }}>{count}</div>
          <div className="text-[10px] uppercase tracking-wider font-bold mt-1" style={{ color: `${color}cc` }}>{stage}</div>
          {i < stages.length - 1 && <div className="absolute right-0 top-1/2 -translate-y-1/2 translate-x-1/2 z-10 text-[#1e3a5f] text-xs">→</div>}
        </div>
      );
    })}
  </div>
);

const LoadingState: React.FC<{ label: string }> = ({ label }) => (
  <div className="text-gray-500 text-center py-12">{label}</div>
);

const EmptyState: React.FC<{ message: string; hint?: string }> = ({ message, hint }) => (
  <div className="text-center py-16">
    <div className="text-gray-500 text-sm">{message}</div>
    {hint && <div className="text-gray-600 text-xs mt-1">{hint}</div>}
  </div>
);

export default HAVENSystem;
