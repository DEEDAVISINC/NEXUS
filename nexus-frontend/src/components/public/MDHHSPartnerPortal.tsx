import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { api } from '../../api/client';

/**
 * MDHHS Partner Portal — What Aimee Surma & Angela Medina see.
 *
 * This is the agency-facing dashboard that shows MDHHS leadership how
 * SHIELD is performing across their counties. No internal DDI operations
 * visible — only outcomes, SLA compliance, and referral tracking.
 *
 * Route: /mdhhs
 * Brand: MDHHS teal/navy + CWC yellow accents
 */

const MDHHS_NAVY  = '#003366';
const MDHHS_TEAL  = '#046791';
const CWC_YELLOW  = '#f5c23e';
const SURFACE     = '#f8fafc';
const CARD_BG     = '#ffffff';
const BORDER_CLR  = '#e2e8f0';
const MUTED       = '#64748b';

const SERVICE_COLOR: Record<string, string> = {
  'Blood Lead Level (BLL) Testing':               '#026666',
  'Lead Screening':                                '#026666',
  'CLPPP Case Management':                        '#17415f',
  'CLPPP Follow-up':                               '#17415f',
  'NEMT — Non-Emergency Medical Transportation':   '#CA4D22',
  'NEMT':                                          '#CA4D22',
  'Lead Remediation Coordination':                 '#862074',
  'Lead Remediation':                              '#862074',
  'Housing Navigation':                            '#093C44',
  'Housing':                                       '#093C44',
  'MIBridges Benefits Navigation':                 '#76BAB2',
  'Food Navigation':                               '#76BAB2',
  'Filter Safety Net / Drinking Water':            '#046791',
  'Filter Safety Net':                             '#046791',
  'Community Health Worker Home Visit':            '#2F8D98',
  'Nurse Home Visit':                              '#6A1B9A',
};

const SERVICE_EMOJI: Record<string, string> = {
  'Blood Lead Level (BLL) Testing': '🩸', 'Lead Screening': '🩸',
  'CLPPP Case Management': '📋', 'CLPPP Follow-up': '📋',
  'NEMT — Non-Emergency Medical Transportation': '🚕', 'NEMT': '🚕',
  'Lead Remediation Coordination': '🛠️', 'Lead Remediation': '🛠️',
  'Housing Navigation': '🏩', 'Housing': '🏩',
  'MIBridges Benefits Navigation': '🤝', 'Food Navigation': '🤝',
  'Filter Safety Net / Drinking Water': '🚰', 'Filter Safety Net': '🚰',
  'Community Health Worker Home Visit': '👩‍⚕️',
  'Nurse Home Visit': '🏥',
};

const COUNTIES = ['Wayne', 'Oakland', 'Macomb', 'Genesee'];

type Tab = 'overview' | 'referrals' | 'outcomes' | 'services' | 'counties';

const MDHHSPartnerPortal: React.FC = () => {
  const [tab, setTab] = useState<Tab>('overview');
  const [referrals, setReferrals] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [countyFilter, setCountyFilter] = useState('All');

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const data = await api.getShieldReferrals();
      setReferrals(data?.referrals || data || []);
    } catch { /* silent */ }
    setLoading(false);
  }, []);

  useEffect(() => { fetchData(); }, [fetchData]);

  const filtered = useMemo(() => {
    if (countyFilter === 'All') return referrals;
    return referrals.filter(r => r.county === countyFilter);
  }, [referrals, countyFilter]);

  // ─── Computed metrics ──────────────────────────────────────────────
  const metrics = useMemo(() => {
    const total = filtered.length;
    const byCounty: Record<string, number> = {};
    const byService: Record<string, number> = {};
    const byStage: Record<string, number> = { 'Intake': 0, 'Active': 0, 'In Service': 0, 'Closed': 0 };
    const byUrgency: Record<string, number> = { 'Standard': 0, 'Urgent': 0, 'Emergency': 0, 'Critical': 0 };
    let slaCompliant = 0;
    let slaBreach = 0;
    let contactTotalHrs = 0;
    let contactCount = 0;

    filtered.forEach(r => {
      const county = r.county || 'Other';
      byCounty[county] = (byCounty[county] || 0) + 1;

      (r.services_requested || []).forEach((s: string) => {
        byService[s] = (byService[s] || 0) + 1;
      });

      const status = (r.status || '').toLowerCase();
      if (status === 'closed' || status === 'completed') byStage['Closed']++;
      else if (r.services_requested?.length > 0 && (status === 'active' || status === 'in service')) byStage['In Service']++;
      else if (status === 'active' || status === 'assigned') byStage['Active']++;
      else byStage['Intake']++;

      const urg = r.urgency || 'Standard';
      byUrgency[urg] = (byUrgency[urg] || 0) + 1;

      if (r.sla) {
        if (r.sla.breached) slaBreach++;
        else slaCompliant++;
      }

      if (r.first_contact_at && r.date_received) {
        const hrs = (new Date(r.first_contact_at).getTime() - new Date(r.date_received).getTime()) / 3600000;
        if (hrs > 0 && hrs < 500) { contactTotalHrs += hrs; contactCount++; }
      }
    });

    const slaRate = (slaCompliant + slaBreach) > 0
      ? Math.round((slaCompliant / (slaCompliant + slaBreach)) * 100) : 100;
    const avgContact = contactCount > 0 ? (contactTotalHrs / contactCount).toFixed(1) : '—';

    return { total, byCounty, byService, byStage, byUrgency, slaRate, avgContact, slaCompliant, slaBreach };
  }, [filtered]);

  // ─── Tabs ──────────────────────────────────────────────────────────
  const TABS: { id: Tab; label: string; icon: string }[] = [
    { id: 'overview',  label: 'Dashboard',    icon: '📊' },
    { id: 'referrals', label: 'Referrals',    icon: '📋' },
    { id: 'services',  label: 'Services',     icon: '⚡' },
    { id: 'counties',  label: 'By County',    icon: '🗺️' },
    { id: 'outcomes',  label: 'Outcomes',     icon: '📈' },
  ];

  return (
    <div className="min-h-screen" style={{ backgroundColor: SURFACE }}>
      {/* ══════ HEADER ══════ */}
      <header style={{ background: `linear-gradient(135deg, ${MDHHS_NAVY} 0%, ${MDHHS_TEAL} 100%)` }}>
        <div className="max-w-7xl mx-auto px-6 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="w-14 h-14 rounded-xl bg-white/10 border border-white/20 flex items-center justify-center">
                <span className="text-3xl">🛡️</span>
              </div>
              <div>
                <div className="text-xs text-white/60 uppercase tracking-widest font-bold">MDHHS Partner Portal</div>
                <h1 className="text-2xl font-black text-white">SHIELD Program Dashboard</h1>
                <div className="text-xs text-white/50 mt-0.5">
                  Screening · Health · Intake · Early Intervention · Lead Defense
                </div>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <div className="text-right hidden sm:block">
                <div className="text-xs text-white/60">Operated by</div>
                <div className="text-sm font-bold text-white">Cause We Care + DDI</div>
                <div className="text-[10px] text-white/40 italic">Care. Navigate. Transform.</div>
              </div>
              <img src="/cwc-logo.png" alt="CWC" className="w-12 h-12 rounded-xl object-contain bg-white/10 p-1.5 hidden sm:block" />
            </div>
          </div>

          {/* Tab bar */}
          <div className="flex gap-1 mt-5">
            {TABS.map(t => (
              <button
                key={t.id}
                onClick={() => setTab(t.id)}
                className={`px-4 py-2 rounded-t-lg text-sm font-bold transition ${
                  tab === t.id
                    ? 'bg-white text-gray-900'
                    : 'text-white/70 hover:text-white hover:bg-white/10'
                }`}
              >
                {t.icon} {t.label}
              </button>
            ))}
          </div>
        </div>
      </header>

      {/* ══════ CONTROLS BAR ══════ */}
      <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <label className="text-xs font-bold text-gray-500 uppercase tracking-wider">County</label>
          <select
            value={countyFilter}
            onChange={e => setCountyFilter(e.target.value)}
            className="border border-gray-300 rounded-lg px-3 py-1.5 text-sm text-gray-700 focus:border-blue-500 focus:outline-none"
          >
            <option value="All">All Counties</option>
            {COUNTIES.map(c => <option key={c} value={c}>{c} County</option>)}
          </select>
        </div>
        <div className="flex items-center gap-3">
          <button onClick={fetchData} className="text-xs text-gray-500 hover:text-blue-600 transition">↻ Refresh</button>
          {loading && <div className="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />}
          <span className="text-[10px] text-gray-400">
            Last updated: {new Date().toLocaleString('en-US', { dateStyle: 'medium', timeStyle: 'short' })}
          </span>
        </div>
      </div>

      {/* ══════ MAIN CONTENT ══════ */}
      <div className="max-w-7xl mx-auto px-6 pb-12">
        {tab === 'overview' && <OverviewTab metrics={metrics} referrals={filtered} />}
        {tab === 'referrals' && <ReferralsTab referrals={filtered} />}
        {tab === 'services' && <ServicesTab metrics={metrics} referrals={filtered} />}
        {tab === 'counties' && <CountiesTab metrics={metrics} referrals={filtered} />}
        {tab === 'outcomes' && <OutcomesTab metrics={metrics} referrals={filtered} />}
      </div>

      {/* ══════ FOOTER ══════ */}
      <footer className="border-t" style={{ borderColor: BORDER_CLR }}>
        <div className="max-w-7xl mx-auto px-6 py-6 flex items-center justify-between">
          <div>
            <div className="text-xs font-bold" style={{ color: MDHHS_NAVY }}>
              SHIELD — A CWC + DDI Program in Partnership with MDHHS
            </div>
            <div className="text-[10px] text-gray-400 mt-0.5">
              Every Family Deserves a SHIELD 🛡️ · Michigan Public Act 146 of 2023
            </div>
          </div>
          <div className="text-[10px] text-gray-400">
            Confidential — For MDHHS internal use only
          </div>
        </div>
      </footer>
    </div>
  );
};

// ═══════════════════════════════════════════════════════════════════════════
// STAT CARD
// ═══════════════════════════════════════════════════════════════════════════
const Stat: React.FC<{ label: string; value: string | number; sub?: string; color?: string; large?: boolean }> = ({ label, value, sub, color, large }) => (
  <div className="rounded-xl p-5 border" style={{ backgroundColor: CARD_BG, borderColor: BORDER_CLR }}>
    <div className="text-[10px] uppercase tracking-widest font-bold" style={{ color: MUTED }}>{label}</div>
    <div className={`${large ? 'text-3xl' : 'text-2xl'} font-black mt-1`} style={{ color: color || MDHHS_NAVY }}>{value}</div>
    {sub && <div className="text-[10px] mt-1" style={{ color: MUTED }}>{sub}</div>}
  </div>
);

// ═══════════════════════════════════════════════════════════════════════════
// PROGRESS BAR
// ═══════════════════════════════════════════════════════════════════════════
const ProgressBar: React.FC<{ pct: number; color: string; label?: string; height?: number }> = ({ pct, color, label, height = 8 }) => (
  <div>
    {label && <div className="flex justify-between text-[10px] mb-1"><span style={{ color: MUTED }}>{label}</span><span className="font-bold" style={{ color }}>{pct}%</span></div>}
    <div className="rounded-full overflow-hidden" style={{ height, backgroundColor: `${color}15` }}>
      <div className="h-full rounded-full transition-all duration-500" style={{ width: `${Math.min(pct, 100)}%`, backgroundColor: color }} />
    </div>
  </div>
);

// ═══════════════════════════════════════════════════════════════════════════
// OVERVIEW TAB
// ═══════════════════════════════════════════════════════════════════════════
const OverviewTab: React.FC<{ metrics: any; referrals: any[] }> = ({ metrics, referrals }) => {
  const recentRefs = useMemo(() =>
    [...referrals].sort((a, b) => (b.date_received || '').localeCompare(a.date_received || '')).slice(0, 8),
    [referrals]
  );

  return (
    <div className="space-y-6">
      {/* Hero stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Stat label="Total Referrals" value={metrics.total} color={MDHHS_NAVY} large />
        <Stat label="SLA Compliance" value={`${metrics.slaRate}%`} color={metrics.slaRate >= 90 ? '#10B981' : metrics.slaRate >= 75 ? '#F59E0B' : '#EF4444'} sub={`${metrics.slaCompliant} on time · ${metrics.slaBreach} breached`} large />
        <Stat label="Avg First Contact" value={metrics.avgContact === '—' ? '—' : `${metrics.avgContact}h`} color={MDHHS_TEAL} sub="Target: 48 hours" large />
        <Stat label="Counties Active" value={Object.keys(metrics.byCounty).length} color={CWC_YELLOW} sub={Object.keys(metrics.byCounty).join(', ')} large />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Pipeline by stage */}
        <div className="rounded-xl border p-5" style={{ backgroundColor: CARD_BG, borderColor: BORDER_CLR }}>
          <div className="text-xs font-bold uppercase tracking-wider mb-4" style={{ color: MDHHS_NAVY }}>Referral Pipeline</div>
          <div className="space-y-3">
            {Object.entries(metrics.byStage).map(([stage, count]) => {
              const colors: Record<string, string> = { 'Intake': '#3B82F6', 'Active': '#8B5CF6', 'In Service': '#F5C23E', 'Closed': '#10B981' };
              const pct = metrics.total > 0 ? Math.round(((count as number) / metrics.total) * 100) : 0;
              return (
                <div key={stage}>
                  <div className="flex justify-between text-xs mb-1">
                    <span className="font-bold" style={{ color: colors[stage] || MUTED }}>{stage}</span>
                    <span className="font-mono" style={{ color: MUTED }}>{count as number}</span>
                  </div>
                  <ProgressBar pct={pct} color={colors[stage] || '#94A3B8'} />
                </div>
              );
            })}
          </div>
        </div>

        {/* Urgency breakdown */}
        <div className="rounded-xl border p-5" style={{ backgroundColor: CARD_BG, borderColor: BORDER_CLR }}>
          <div className="text-xs font-bold uppercase tracking-wider mb-4" style={{ color: MDHHS_NAVY }}>Urgency Distribution</div>
          <div className="space-y-3">
            {Object.entries(metrics.byUrgency).filter(([, c]) => (c as number) > 0).map(([urg, count]) => {
              const colors: Record<string, string> = { 'Standard': '#3B82F6', 'Urgent': '#F59E0B', 'Emergency': '#EF4444', 'Critical': '#DC2626' };
              return (
                <div key={urg} className="flex items-center gap-3">
                  <span className="w-3 h-3 rounded-full" style={{ backgroundColor: colors[urg] || '#94A3B8' }} />
                  <span className="text-sm font-bold flex-1" style={{ color: MDHHS_NAVY }}>{urg}</span>
                  <span className="text-sm font-mono" style={{ color: MUTED }}>{count as number}</span>
                </div>
              );
            })}
          </div>
          {Object.values(metrics.byUrgency).every(v => v === 0) && (
            <div className="text-sm text-center py-4" style={{ color: MUTED }}>No referrals yet</div>
          )}
        </div>

        {/* Recent referrals */}
        <div className="rounded-xl border p-5" style={{ backgroundColor: CARD_BG, borderColor: BORDER_CLR }}>
          <div className="text-xs font-bold uppercase tracking-wider mb-4" style={{ color: MDHHS_NAVY }}>Recent Referrals</div>
          {recentRefs.length === 0 ? (
            <div className="text-sm text-center py-4" style={{ color: MUTED }}>No referrals yet</div>
          ) : (
            <div className="space-y-2">
              {recentRefs.map(r => (
                <div key={r.id} className="flex items-center gap-2 py-1.5 border-b" style={{ borderColor: `${BORDER_CLR}80` }}>
                  <span className="w-2 h-2 rounded-full" style={{ backgroundColor: r.sla?.breached ? '#EF4444' : r.sla?.warning ? '#F59E0B' : '#10B981' }} />
                  <div className="flex-1 min-w-0">
                    <div className="text-xs font-bold truncate" style={{ color: MDHHS_NAVY }}>
                      {r.referral_id || r.id?.slice(-8)}
                    </div>
                    <div className="text-[10px]" style={{ color: MUTED }}>
                      {r.county || '—'} · {r.urgency || 'Standard'}
                    </div>
                  </div>
                  <div className="text-[10px]" style={{ color: MUTED }}>
                    {r.date_received ? new Date(r.date_received).toLocaleDateString() : '—'}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* County map cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {COUNTIES.map(county => {
          const count = metrics.byCounty[county] || 0;
          return (
            <div key={county} className="rounded-xl border p-4 text-center" style={{ backgroundColor: CARD_BG, borderColor: BORDER_CLR }}>
              <div className="text-xs font-bold uppercase tracking-wider" style={{ color: MUTED }}>{county} County</div>
              <div className="text-3xl font-black mt-2" style={{ color: count > 0 ? MDHHS_NAVY : '#CBD5E1' }}>{count}</div>
              <div className="text-[10px]" style={{ color: MUTED }}>referrals</div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

// ═══════════════════════════════════════════════════════════════════════════
// REFERRALS TAB — full table of every referral
// ═══════════════════════════════════════════════════════════════════════════
const ReferralsTab: React.FC<{ referrals: any[] }> = ({ referrals }) => {
  const sorted = useMemo(() =>
    [...referrals].sort((a, b) => (b.date_received || '').localeCompare(a.date_received || '')),
    [referrals]
  );

  const urgColor = (u: string) => {
    const m: Record<string, string> = { 'Critical': '#DC2626', 'Emergency': '#EF4444', 'Urgent': '#F59E0B', 'Standard': '#3B82F6' };
    return m[u] || '#94A3B8';
  };

  return (
    <div>
      <div className="text-xs font-bold uppercase tracking-wider mb-4" style={{ color: MDHHS_NAVY }}>
        All Referrals ({sorted.length})
      </div>
      <div className="rounded-xl border overflow-hidden" style={{ backgroundColor: CARD_BG, borderColor: BORDER_CLR }}>
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b" style={{ borderColor: BORDER_CLR, backgroundColor: '#f1f5f9' }}>
              <th className="text-left px-4 py-3 text-[10px] uppercase tracking-wider font-bold" style={{ color: MUTED }}>Case #</th>
              <th className="text-left px-4 py-3 text-[10px] uppercase tracking-wider font-bold" style={{ color: MUTED }}>Date</th>
              <th className="text-left px-4 py-3 text-[10px] uppercase tracking-wider font-bold" style={{ color: MUTED }}>County</th>
              <th className="text-left px-4 py-3 text-[10px] uppercase tracking-wider font-bold" style={{ color: MUTED }}>Urgency</th>
              <th className="text-left px-4 py-3 text-[10px] uppercase tracking-wider font-bold" style={{ color: MUTED }}>Services</th>
              <th className="text-left px-4 py-3 text-[10px] uppercase tracking-wider font-bold" style={{ color: MUTED }}>Status</th>
              <th className="text-left px-4 py-3 text-[10px] uppercase tracking-wider font-bold" style={{ color: MUTED }}>SLA</th>
            </tr>
          </thead>
          <tbody>
            {sorted.length === 0 ? (
              <tr><td colSpan={7} className="text-center py-12 text-sm" style={{ color: MUTED }}>No referrals match the current filter.</td></tr>
            ) : sorted.map(r => (
              <tr key={r.id} className="border-b hover:bg-blue-50/40 transition" style={{ borderColor: `${BORDER_CLR}60` }}>
                <td className="px-4 py-3 font-bold" style={{ color: MDHHS_NAVY }}>{r.referral_id || r.id?.slice(-8)}</td>
                <td className="px-4 py-3 text-xs" style={{ color: MUTED }}>{r.date_received ? new Date(r.date_received).toLocaleDateString() : '—'}</td>
                <td className="px-4 py-3 text-xs font-bold" style={{ color: MDHHS_NAVY }}>{r.county || '—'}</td>
                <td className="px-4 py-3">
                  <span className="px-2 py-0.5 rounded-full text-[10px] font-bold text-white" style={{ backgroundColor: urgColor(r.urgency || 'Standard') }}>
                    {r.urgency || 'Standard'}
                  </span>
                </td>
                <td className="px-4 py-3">
                  <div className="flex flex-wrap gap-1">
                    {(r.services_requested || []).map((s: string, i: number) => (
                      <span key={i} className="text-[10px] px-2 py-0.5 rounded-full border font-bold" style={{
                        borderColor: SERVICE_COLOR[s] || MUTED,
                        color: SERVICE_COLOR[s] || MUTED,
                        backgroundColor: `${SERVICE_COLOR[s] || MUTED}10`
                      }}>
                        {SERVICE_EMOJI[s] || '📌'} {s.length > 18 ? s.slice(0, 15) + '…' : s}
                      </span>
                    ))}
                  </div>
                </td>
                <td className="px-4 py-3 text-xs font-bold" style={{ color: MDHHS_TEAL }}>{r.status || 'Pending'}</td>
                <td className="px-4 py-3">
                  {r.sla ? (
                    <div className="flex items-center gap-2">
                      <span className={`w-2.5 h-2.5 rounded-full ${r.sla.breached ? 'bg-red-500' : r.sla.warning ? 'bg-amber-400' : 'bg-emerald-500'}`} />
                      <span className="text-[10px] font-bold" style={{ color: r.sla.breached ? '#EF4444' : r.sla.warning ? '#F59E0B' : '#10B981' }}>
                        {r.sla.breached ? 'Breached' : r.sla.warning ? 'Warning' : 'On Track'}
                      </span>
                    </div>
                  ) : (
                    <span className="text-[10px]" style={{ color: MUTED }}>—</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

// ═══════════════════════════════════════════════════════════════════════════
// SERVICES TAB — breakdown by service line
// ═══════════════════════════════════════════════════════════════════════════
const ServicesTab: React.FC<{ metrics: any; referrals: any[] }> = ({ metrics }) => {
  const sorted = Object.entries(metrics.byService as Record<string, number>)
    .sort(([, a], [, b]) => (b as number) - (a as number));

  const maxCount = sorted.length > 0 ? (sorted[0][1] as number) : 1;

  return (
    <div className="space-y-6">
      <div className="text-xs font-bold uppercase tracking-wider" style={{ color: MDHHS_NAVY }}>
        Service Line Utilization
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {sorted.map(([svc, count]) => {
          const hex = SERVICE_COLOR[svc] || '#94A3B8';
          const pct = Math.round(((count as number) / maxCount) * 100);
          return (
            <div key={svc} className="rounded-xl border p-5" style={{ backgroundColor: CARD_BG, borderColor: BORDER_CLR }}>
              <div className="flex items-center gap-3 mb-3">
                <span className="text-2xl">{SERVICE_EMOJI[svc] || '📌'}</span>
                <div className="flex-1">
                  <div className="text-sm font-bold" style={{ color: hex }}>{svc}</div>
                  <div className="text-[10px]" style={{ color: MUTED }}>{count} referral{(count as number) !== 1 ? 's' : ''} requesting this service</div>
                </div>
                <div className="text-2xl font-black" style={{ color: hex }}>{count as number}</div>
              </div>
              <ProgressBar pct={pct} color={hex} />
            </div>
          );
        })}
      </div>
      {sorted.length === 0 && (
        <div className="rounded-xl border p-12 text-center" style={{ backgroundColor: CARD_BG, borderColor: BORDER_CLR, color: MUTED }}>
          No service data yet.
        </div>
      )}
    </div>
  );
};

// ═══════════════════════════════════════════════════════════════════════════
// COUNTIES TAB — per-county deep dive
// ═══════════════════════════════════════════════════════════════════════════
const CountiesTab: React.FC<{ metrics: any; referrals: any[] }> = ({ metrics, referrals }) => (
  <div className="space-y-6">
    <div className="text-xs font-bold uppercase tracking-wider" style={{ color: MDHHS_NAVY }}>
      County-Level Breakdown
    </div>
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      {COUNTIES.map(county => {
        const countyRefs = referrals.filter(r => r.county === county);
        const count = countyRefs.length;
        const svcCounts: Record<string, number> = {};
        countyRefs.forEach(r => (r.services_requested || []).forEach((s: string) => {
          svcCounts[s] = (svcCounts[s] || 0) + 1;
        }));
        const breached = countyRefs.filter(r => r.sla?.breached).length;
        const onTrack = countyRefs.filter(r => r.sla && !r.sla.breached).length;
        const slaRate = (onTrack + breached) > 0 ? Math.round((onTrack / (onTrack + breached)) * 100) : 100;

        return (
          <div key={county} className="rounded-xl border overflow-hidden" style={{ backgroundColor: CARD_BG, borderColor: BORDER_CLR }}>
            <div className="px-5 py-4 border-b flex items-center justify-between" style={{ borderColor: BORDER_CLR, background: `linear-gradient(135deg, ${MDHHS_NAVY}08 0%, ${MDHHS_TEAL}08 100%)` }}>
              <div>
                <div className="text-lg font-black" style={{ color: MDHHS_NAVY }}>{county} County</div>
                <div className="text-[10px]" style={{ color: MUTED }}>{count} referral{count !== 1 ? 's' : ''}</div>
              </div>
              <div className="text-right">
                <div className="text-2xl font-black" style={{ color: slaRate >= 90 ? '#10B981' : slaRate >= 75 ? '#F59E0B' : '#EF4444' }}>
                  {count > 0 ? `${slaRate}%` : '—'}
                </div>
                <div className="text-[10px]" style={{ color: MUTED }}>SLA compliance</div>
              </div>
            </div>
            <div className="px-5 py-4">
              {count === 0 ? (
                <div className="text-sm text-center py-4" style={{ color: MUTED }}>No referrals yet for {county} County</div>
              ) : (
                <div className="space-y-2">
                  {Object.entries(svcCounts).sort(([, a], [, b]) => b - a).map(([svc, ct]) => (
                    <div key={svc} className="flex items-center gap-2 text-xs">
                      <span>{SERVICE_EMOJI[svc] || '📌'}</span>
                      <span className="flex-1 font-bold" style={{ color: SERVICE_COLOR[svc] || MUTED }}>{svc}</span>
                      <span className="font-mono" style={{ color: MUTED }}>{ct}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        );
      })}
    </div>
  </div>
);

// ═══════════════════════════════════════════════════════════════════════════
// OUTCOMES TAB — the report MDHHS sends to Lansing
// ═══════════════════════════════════════════════════════════════════════════
const OutcomesTab: React.FC<{ metrics: any; referrals: any[] }> = ({ metrics, referrals }) => {
  const today = new Date();
  const reportPeriod = `${today.toLocaleString('en-US', { month: 'long' })} ${today.getFullYear()}`;

  const printReport = () => {
    window.print();
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <div className="text-xs font-bold uppercase tracking-wider" style={{ color: MDHHS_NAVY }}>
            MDHHS Outcomes Report
          </div>
          <div className="text-[10px]" style={{ color: MUTED }}>Period: {reportPeriod} · Generated: {today.toLocaleDateString()}</div>
        </div>
        <button
          onClick={printReport}
          className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-bold text-white transition hover:opacity-90"
          style={{ backgroundColor: MDHHS_NAVY }}
        >
          📄 Export / Print Report
        </button>
      </div>

      {/* Report header — printable */}
      <div className="rounded-xl border p-6" style={{ backgroundColor: CARD_BG, borderColor: BORDER_CLR }}>
        <div className="text-center mb-6">
          <div className="text-xs uppercase tracking-widest font-bold" style={{ color: MUTED }}>Michigan Department of Health & Human Services</div>
          <h2 className="text-xl font-black mt-1" style={{ color: MDHHS_NAVY }}>
            SHIELD Program Outcomes Report
          </h2>
          <div className="text-xs" style={{ color: MUTED }}>
            Screening · Health · Intake · Early Intervention · Lead Defense
          </div>
          <div className="text-xs mt-1" style={{ color: MDHHS_TEAL }}>
            Operated by Cause We Care Foundation + DDI · {reportPeriod}
          </div>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <div className="text-center p-4 rounded-lg" style={{ backgroundColor: `${MDHHS_NAVY}08` }}>
            <div className="text-2xl font-black" style={{ color: MDHHS_NAVY }}>{metrics.total}</div>
            <div className="text-[10px] font-bold uppercase" style={{ color: MUTED }}>Total Referrals</div>
          </div>
          <div className="text-center p-4 rounded-lg" style={{ backgroundColor: `${MDHHS_TEAL}08` }}>
            <div className="text-2xl font-black" style={{ color: MDHHS_TEAL }}>{metrics.byStage['In Service'] || 0}</div>
            <div className="text-[10px] font-bold uppercase" style={{ color: MUTED }}>Actively Served</div>
          </div>
          <div className="text-center p-4 rounded-lg" style={{ backgroundColor: metrics.slaRate >= 90 ? '#10B98108' : '#F59E0B08' }}>
            <div className="text-2xl font-black" style={{ color: metrics.slaRate >= 90 ? '#10B981' : '#F59E0B' }}>{metrics.slaRate}%</div>
            <div className="text-[10px] font-bold uppercase" style={{ color: MUTED }}>SLA Compliance</div>
          </div>
          <div className="text-center p-4 rounded-lg" style={{ backgroundColor: '#10B98108' }}>
            <div className="text-2xl font-black" style={{ color: '#10B981' }}>{metrics.byStage['Closed'] || 0}</div>
            <div className="text-[10px] font-bold uppercase" style={{ color: MUTED }}>Cases Closed</div>
          </div>
        </div>

        {/* County breakdown table */}
        <div className="mb-6">
          <div className="text-xs font-bold uppercase tracking-wider mb-3" style={{ color: MDHHS_NAVY }}>Referrals by County</div>
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b" style={{ borderColor: BORDER_CLR }}>
                <th className="text-left py-2 text-[10px] uppercase" style={{ color: MUTED }}>County</th>
                <th className="text-center py-2 text-[10px] uppercase" style={{ color: MUTED }}>Referrals</th>
                <th className="text-center py-2 text-[10px] uppercase" style={{ color: MUTED }}>Active</th>
                <th className="text-center py-2 text-[10px] uppercase" style={{ color: MUTED }}>Closed</th>
                <th className="text-center py-2 text-[10px] uppercase" style={{ color: MUTED }}>SLA Rate</th>
              </tr>
            </thead>
            <tbody>
              {COUNTIES.map(county => {
                const cRefs = referrals.filter(r => r.county === county);
                const active = cRefs.filter(r => !['closed', 'completed'].includes((r.status || '').toLowerCase())).length;
                const closed = cRefs.filter(r => ['closed', 'completed'].includes((r.status || '').toLowerCase())).length;
                const onTrack = cRefs.filter(r => r.sla && !r.sla.breached).length;
                const totalSla = cRefs.filter(r => r.sla).length;
                const rate = totalSla > 0 ? Math.round((onTrack / totalSla) * 100) : 100;
                return (
                  <tr key={county} className="border-b" style={{ borderColor: `${BORDER_CLR}60` }}>
                    <td className="py-2 font-bold" style={{ color: MDHHS_NAVY }}>{county}</td>
                    <td className="py-2 text-center font-mono">{cRefs.length}</td>
                    <td className="py-2 text-center font-mono" style={{ color: MDHHS_TEAL }}>{active}</td>
                    <td className="py-2 text-center font-mono" style={{ color: '#10B981' }}>{closed}</td>
                    <td className="py-2 text-center font-bold" style={{ color: rate >= 90 ? '#10B981' : '#F59E0B' }}>{cRefs.length > 0 ? `${rate}%` : '—'}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        {/* Service utilization */}
        <div className="mb-6">
          <div className="text-xs font-bold uppercase tracking-wider mb-3" style={{ color: MDHHS_NAVY }}>Service Line Utilization</div>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            {Object.entries(metrics.byService as Record<string, number>)
              .sort(([, a], [, b]) => (b as number) - (a as number))
              .map(([svc, count]) => (
                <div key={svc} className="flex items-center gap-2 p-2 rounded-lg" style={{ backgroundColor: `${SERVICE_COLOR[svc] || '#94A3B8'}08` }}>
                  <span>{SERVICE_EMOJI[svc] || '📌'}</span>
                  <span className="text-xs font-bold flex-1" style={{ color: SERVICE_COLOR[svc] || MUTED }}>{svc}</span>
                  <span className="text-xs font-mono font-bold" style={{ color: MDHHS_NAVY }}>{count as number}</span>
                </div>
              ))}
          </div>
        </div>

        {/* Footer */}
        <div className="border-t pt-4 text-center" style={{ borderColor: BORDER_CLR }}>
          <div className="text-[10px]" style={{ color: MUTED }}>
            This report was generated by the SHIELD system — a joint program of Cause We Care Foundation
            and DDI (Dee Davis Inc.), in partnership with the Michigan Department of Health & Human Services.
          </div>
          <div className="text-[10px] mt-1" style={{ color: MUTED }}>
            Michigan Public Act 146 of 2023 · Every Family Deserves a SHIELD 🛡️
          </div>
        </div>
      </div>
    </div>
  );
};

export default MDHHSPartnerPortal;
