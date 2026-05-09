import React, { useState, useEffect, useCallback } from 'react';
import { api } from '../../api/client';

/**
 * HAVEN — Housing, Assistance, Vital Emergency Network
 * Disaster Response TPA System
 *
 * Palette (HAVEN-keyed):
 *   haven-dark     #0a1628   deepest backdrop
 *   haven-navy     #0f2040   primary surface
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

interface Readiness {
  readiness_level: string;
  readiness_score: number;
  transport_partners_ready: number;
  housing_partners_ready: number;
  medical_partners_ready: number;
  active_mco_contracts: number;
  total_partners: number;
  total_mcos: number;
  gaps: Record<string, boolean>;
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

interface PartnerRecord {
  id: string;
  fields: Record<string, any>;
}

const TABS = [
  { id: 'dashboard', label: 'Dashboard', icon: '📊' },
  { id: 'transport', label: 'Transport', icon: '🚗' },
  { id: 'housing', label: 'Housing', icon: '🏠' },
  { id: 'medical', label: 'Medical', icon: '💊' },
  { id: 'mcos', label: 'MCO Pipeline', icon: '🏥' },
  { id: 'readiness', label: 'Readiness', icon: '🌀' },
];

const STATE_NAMES: Record<string, string> = {
  FL: 'Florida',
  TX: 'Texas',
  LA: 'Louisiana',
  MI: 'Michigan',
};

const STATUS_BADGES: Record<string, string> = {
  Prospect: 'bg-gray-500/20 text-gray-400 border-gray-500/30',
  Outreach: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
  Negotiating: 'bg-amber-500/20 text-amber-400 border-amber-500/30',
  Signed: 'bg-purple-500/20 text-purple-400 border-purple-500/30',
  Active: 'bg-green-500/20 text-green-400 border-green-500/30',
  Target: 'bg-amber-500/20 text-amber-400 border-amber-500/30',
  'In Progress': 'bg-blue-500/20 text-blue-400 border-blue-500/30',
  Complete: 'bg-green-500/20 text-green-400 border-green-500/30',
  'Not Started': 'bg-gray-500/20 text-gray-400 border-gray-500/30',
};

const HAVENSystem: React.FC<HAVENSystemProps> = ({ onBackToNexus, activeTab, setActiveTab }) => {
  const [status, setStatus] = useState<SystemStatus | null>(null);
  const [readiness, setReadiness] = useState<Readiness | null>(null);
  const [transportPartners, setTransportPartners] = useState<PartnerRecord[]>([]);
  const [housingPartners, setHousingPartners] = useState<PartnerRecord[]>([]);
  const [medicalPartners, setMedicalPartners] = useState<PartnerRecord[]>([]);
  const [mcos, setMcos] = useState<PartnerRecord[]>([]);
  const [loading, setLoading] = useState(false);
  const [stateFilter, setStateFilter] = useState<string>('');
  const [notification, setNotification] = useState<{ message: string; type: 'success' | 'error' } | null>(null);

  const notify = (message: string, type: 'success' | 'error' = 'success') => {
    setNotification({ message, type });
    setTimeout(() => setNotification(null), 4000);
  };

  const loadDashboard = useCallback(async () => {
    setLoading(true);
    try {
      const res = await api.get('/haven/status');
      setStatus(res);
    } catch { /* empty */ }
    try {
      const res = await api.get('/haven/readiness');
      setReadiness(res);
    } catch { /* empty */ }
    setLoading(false);
  }, []);

  const loadTransport = useCallback(async () => {
    setLoading(true);
    try {
      const q = stateFilter ? `?state=${stateFilter}` : '';
      const res = await api.get(`/haven/partners/transport${q}`);
      setTransportPartners(res.partners || []);
    } catch { setTransportPartners([]); }
    setLoading(false);
  }, [stateFilter]);

  const loadHousing = useCallback(async () => {
    setLoading(true);
    try {
      const q = stateFilter ? `?state=${stateFilter}` : '';
      const res = await api.get(`/haven/partners/housing${q}`);
      setHousingPartners(res.partners || []);
    } catch { setHousingPartners([]); }
    setLoading(false);
  }, [stateFilter]);

  const loadMedical = useCallback(async () => {
    setLoading(true);
    try {
      const q = stateFilter ? `?state=${stateFilter}` : '';
      const res = await api.get(`/haven/partners/medical${q}`);
      setMedicalPartners(res.partners || []);
    } catch { setMedicalPartners([]); }
    setLoading(false);
  }, [stateFilter]);

  const loadMCOs = useCallback(async () => {
    setLoading(true);
    try {
      const q = stateFilter ? `?state=${stateFilter}` : '';
      const res = await api.get(`/haven/mcos${q}`);
      setMcos(res.mcos || []);
    } catch { setMcos([]); }
    setLoading(false);
  }, [stateFilter]);

  useEffect(() => {
    loadDashboard();
  }, [loadDashboard]);

  useEffect(() => {
    if (activeTab === 'transport') loadTransport();
    if (activeTab === 'housing') loadHousing();
    if (activeTab === 'medical') loadMedical();
    if (activeTab === 'mcos') loadMCOs();
  }, [activeTab, loadTransport, loadHousing, loadMedical, loadMCOs]);

  const updatePartnerStatus = async (table: string, recordId: string, newStatus: string) => {
    try {
      await api.patch(`/haven/partners/${table}/${recordId}`, { agreement_status: newStatus });
      notify(`Status updated to ${newStatus}`);
      if (table === 'transport') loadTransport();
      if (table === 'housing') loadHousing();
      if (table === 'medical') loadMedical();
      loadDashboard();
    } catch { notify('Failed to update status', 'error'); }
  };

  const updateMCOStatus = async (recordId: string, newStatus: string) => {
    try {
      await api.patch(`/haven/mcos/${recordId}`, { contract_status: newStatus });
      notify(`MCO status updated to ${newStatus}`);
      loadMCOs();
      loadDashboard();
    } catch { notify('Failed to update MCO', 'error'); }
  };

  // ─── RENDERERS ───────────────────────────────────────────────────

  const renderBadge = (status: string) => {
    const cls = STATUS_BADGES[status] || STATUS_BADGES['Prospect'];
    return <span className={`px-2 py-0.5 text-[10px] font-bold uppercase rounded border ${cls}`}>{status}</span>;
  };

  const renderStatCard = (icon: string, value: string | number, label: string, color = 'text-blue-400') => (
    <div className="bg-[#0f2040] rounded-xl p-4 border border-[#1e3a5f]/50">
      <div className="text-2xl mb-1">{icon}</div>
      <div className={`text-3xl font-black ${color}`}>{value}</div>
      <div className="text-[10px] text-gray-500 uppercase tracking-wider mt-1">{label}</div>
    </div>
  );

  const renderStateFilter = () => (
    <div className="flex gap-2 mb-4">
      <button
        onClick={() => setStateFilter('')}
        className={`px-3 py-1.5 rounded-lg text-xs font-bold transition ${!stateFilter ? 'bg-blue-600 text-white' : 'bg-[#0f2040] text-gray-400 hover:text-white'}`}
      >All States</button>
      {['FL', 'TX', 'LA', 'MI'].map(st => (
        <button
          key={st}
          onClick={() => setStateFilter(st)}
          className={`px-3 py-1.5 rounded-lg text-xs font-bold transition ${stateFilter === st ? 'bg-blue-600 text-white' : 'bg-[#0f2040] text-gray-400 hover:text-white'}`}
        >{st}</button>
      ))}
    </div>
  );

  // ─── DASHBOARD TAB ───────────────────────────────────────────────

  const renderDashboard = () => {
    if (!status) return <div className="text-gray-500 text-center py-12">Loading HAVEN...</div>;
    const net = status.network;
    const ops = status.operations;

    return (
      <div className="space-y-6">
        {/* System Status Banner */}
        <div className="bg-gradient-to-r from-[#0f2040] to-[#1e3a5f] rounded-xl p-6 border border-[#2563eb]/30">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-black text-white">🏠 HAVEN</h2>
              <p className="text-sm text-gray-400">Housing, Assistance, Vital Emergency Network</p>
            </div>
            <div className="flex items-center gap-3">
              <span className="px-4 py-2 bg-green-500/20 text-green-400 rounded-lg text-sm font-bold border border-green-500/30">
                ✓ OPERATIONAL
              </span>
            </div>
          </div>
        </div>

        {/* Top Stats */}
        <div className="grid grid-cols-4 gap-4">
          {renderStatCard('🤝', net.total_partners, 'Total Partners', 'text-blue-400')}
          {renderStatCard('🏥', net.total_mcos, 'MCOs in Pipeline', 'text-purple-400')}
          {renderStatCard('👥', `${(status.mcos.total_members / 1000000).toFixed(1)}M`, 'Members Covered', 'text-emerald-400')}
          {renderStatCard('📍', '4', 'States Active', 'text-amber-400')}
        </div>

        {/* Three Pillars */}
        <div className="grid grid-cols-3 gap-4">
          {/* Housing */}
          <div className="bg-[#0f2040] rounded-xl p-4 border-t-4 border-amber-500">
            <div className="flex items-center gap-2 mb-3">
              <span className="text-xl">🏠</span>
              <h3 className="font-bold text-white">HOUSING</h3>
            </div>
            <div className="grid grid-cols-2 gap-2">
              <div className="bg-[#0a1628] rounded-lg p-3 text-center">
                <div className="text-xl font-black text-amber-400">{net.housing.total}</div>
                <div className="text-[9px] text-gray-500 uppercase">Partners</div>
              </div>
              <div className="bg-[#0a1628] rounded-lg p-3 text-center">
                <div className="text-xl font-black text-green-400">{net.housing.by_status['Active'] || 0}</div>
                <div className="text-[9px] text-gray-500 uppercase">Active</div>
              </div>
            </div>
          </div>

          {/* Transport */}
          <div className="bg-[#0f2040] rounded-xl p-4 border-t-4 border-sky-500">
            <div className="flex items-center gap-2 mb-3">
              <span className="text-xl">🚗</span>
              <h3 className="font-bold text-white">TRANSPORT</h3>
            </div>
            <div className="grid grid-cols-2 gap-2">
              <div className="bg-[#0a1628] rounded-lg p-3 text-center">
                <div className="text-xl font-black text-sky-400">{net.transport.total}</div>
                <div className="text-[9px] text-gray-500 uppercase">Partners</div>
              </div>
              <div className="bg-[#0a1628] rounded-lg p-3 text-center">
                <div className="text-xl font-black text-green-400">{net.transport.by_status['Active'] || 0}</div>
                <div className="text-[9px] text-gray-500 uppercase">Active</div>
              </div>
            </div>
          </div>

          {/* Medical */}
          <div className="bg-[#0f2040] rounded-xl p-4 border-t-4 border-emerald-500">
            <div className="flex items-center gap-2 mb-3">
              <span className="text-xl">💊</span>
              <h3 className="font-bold text-white">MEDICAL</h3>
            </div>
            <div className="grid grid-cols-2 gap-2">
              <div className="bg-[#0a1628] rounded-lg p-3 text-center">
                <div className="text-xl font-black text-emerald-400">{net.medical.total}</div>
                <div className="text-[9px] text-gray-500 uppercase">Partners</div>
              </div>
              <div className="bg-[#0a1628] rounded-lg p-3 text-center">
                <div className="text-xl font-black text-green-400">{net.medical.by_status['Active'] || 0}</div>
                <div className="text-[9px] text-gray-500 uppercase">Active</div>
              </div>
            </div>
          </div>
        </div>

        {/* State Coverage */}
        <div className="bg-[#0f2040] rounded-xl p-4 border border-[#1e3a5f]/50">
          <h3 className="text-sm font-bold text-blue-400 mb-3">📍 STATE COVERAGE</h3>
          <div className="grid grid-cols-4 gap-3">
            {['FL', 'TX', 'LA', 'MI'].map(st => (
              <div key={st} className="bg-[#0a1628] rounded-lg p-3 text-center">
                <div className="text-2xl font-black text-white">{st}</div>
                <div className="text-[10px] text-gray-500 mb-2">{STATE_NAMES[st]}</div>
                <div className="flex justify-around text-[9px] text-gray-500">
                  <div className="text-center">
                    <div className="text-sm font-bold text-sky-400">{net.transport.by_state[st] || 0}</div>
                    <div>Trans</div>
                  </div>
                  <div className="text-center">
                    <div className="text-sm font-bold text-emerald-400">{net.medical.by_state[st] || 0}</div>
                    <div>Med</div>
                  </div>
                  <div className="text-center">
                    <div className="text-sm font-bold text-purple-400">{net.mcos.by_state[st] || 0}</div>
                    <div>MCOs</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Operations */}
        <div className="bg-[#0f2040] rounded-xl p-4 border border-[#1e3a5f]/50">
          <h3 className="text-sm font-bold text-blue-400 mb-3">📊 LIVE OPERATIONS</h3>
          <div className="grid grid-cols-3 gap-3">
            <div className="bg-[#0a1628] rounded-lg p-4 text-center">
              <div className="text-2xl mb-1">🌪️</div>
              <div className="text-3xl font-black text-emerald-400">{ops.active_events}</div>
              <div className="text-[10px] text-gray-500 uppercase">Active Events</div>
            </div>
            <div className="bg-[#0a1628] rounded-lg p-4 text-center">
              <div className="text-2xl mb-1">📋</div>
              <div className="text-3xl font-black text-emerald-400">{ops.active_cases}</div>
              <div className="text-[10px] text-gray-500 uppercase">Open Cases</div>
            </div>
            <div className="bg-[#0a1628] rounded-lg p-4 text-center">
              <div className="text-2xl mb-1">🚀</div>
              <div className="text-3xl font-black text-emerald-400">{ops.pending_activations}</div>
              <div className="text-[10px] text-gray-500 uppercase">Pending Activations</div>
            </div>
          </div>
        </div>
      </div>
    );
  };

  // ─── PARTNER TABLE ───────────────────────────────────────────────

  const renderPartnerTable = (
    partners: PartnerRecord[],
    tableName: string,
    nameField: string,
    columns: Array<{ key: string; label: string }>,
  ) => (
    <div className="space-y-4">
      {renderStateFilter()}
      {loading && <div className="text-gray-500 text-center py-8">Loading...</div>}
      {!loading && partners.length === 0 && (
        <div className="text-gray-500 text-center py-8">No partners found{stateFilter ? ` in ${stateFilter}` : ''}</div>
      )}
      {!loading && partners.length > 0 && (
        <div className="bg-[#0f2040] rounded-xl border border-[#1e3a5f]/50 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-[#1e3a5f]">
                  <th className="text-left px-4 py-3 text-[10px] text-gray-500 uppercase tracking-wider">Name</th>
                  {columns.map(col => (
                    <th key={col.key} className="text-left px-4 py-3 text-[10px] text-gray-500 uppercase tracking-wider">{col.label}</th>
                  ))}
                  <th className="text-left px-4 py-3 text-[10px] text-gray-500 uppercase tracking-wider">Status</th>
                  <th className="text-left px-4 py-3 text-[10px] text-gray-500 uppercase tracking-wider">Actions</th>
                </tr>
              </thead>
              <tbody>
                {partners.map(p => (
                  <tr key={p.id} className="border-b border-[#1e3a5f]/30 hover:bg-[#1e3a5f]/20 transition">
                    <td className="px-4 py-3 text-white font-medium">{p.fields[nameField] || '—'}</td>
                    {columns.map(col => (
                      <td key={col.key} className="px-4 py-3 text-gray-400 text-xs">
                        {Array.isArray(p.fields[col.key]) ? p.fields[col.key].join(', ') : (p.fields[col.key] || '—')}
                      </td>
                    ))}
                    <td className="px-4 py-3">{renderBadge(p.fields.agreement_status || p.fields.contract_status || 'Unknown')}</td>
                    <td className="px-4 py-3">
                      <select
                        className="bg-[#0a1628] border border-[#1e3a5f] text-gray-300 text-xs rounded px-2 py-1"
                        value=""
                        onChange={e => {
                          if (e.target.value) {
                            if (tableName === 'mco') {
                              updateMCOStatus(p.id, e.target.value);
                            } else {
                              updatePartnerStatus(tableName, p.id, e.target.value);
                            }
                          }
                        }}
                      >
                        <option value="">Move to...</option>
                        <option value="Prospect">Prospect</option>
                        <option value="Outreach">Outreach</option>
                        <option value="Negotiating">Negotiating</option>
                        <option value="Signed">Signed</option>
                        <option value="Active">Active</option>
                      </select>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="px-4 py-2 border-t border-[#1e3a5f] text-xs text-gray-500">
            {partners.length} partner{partners.length !== 1 ? 's' : ''}{stateFilter ? ` in ${STATE_NAMES[stateFilter] || stateFilter}` : ''}
          </div>
        </div>
      )}
    </div>
  );

  // ─── MCO TABLE ───────────────────────────────────────────────────

  const renderMCOTable = () => (
    <div className="space-y-4">
      {renderStateFilter()}

      {/* MCO Stats */}
      {status && (
        <div className="grid grid-cols-3 gap-4 mb-4">
          <div className="bg-[#0f2040] rounded-xl p-4 border border-[#1e3a5f]/50 text-center">
            <div className="text-3xl font-black text-green-400">{status.mcos.by_status['Active'] || 0}</div>
            <div className="text-[10px] text-gray-500 uppercase">Active</div>
          </div>
          <div className="bg-[#0f2040] rounded-xl p-4 border border-[#1e3a5f]/50 text-center">
            <div className="text-3xl font-black text-amber-400">{status.mcos.by_status['Target'] || 0}</div>
            <div className="text-[10px] text-gray-500 uppercase">Target</div>
          </div>
          <div className="bg-[#0f2040] rounded-xl p-4 border border-[#1e3a5f]/50 text-center">
            <div className="text-3xl font-black text-blue-400">{(status.mcos.total_members / 1000000).toFixed(1)}M</div>
            <div className="text-[10px] text-gray-500 uppercase">Members</div>
          </div>
        </div>
      )}

      {/* Parent Companies */}
      {status && (
        <div className="bg-[#0f2040] rounded-xl p-4 border border-[#1e3a5f]/50 mb-4">
          <h4 className="text-xs text-gray-500 uppercase tracking-wider mb-2">Parent Companies</h4>
          <div className="flex flex-wrap gap-1.5">
            {Object.entries(status.mcos.by_parent).sort((a, b) => b[1] - a[1]).map(([name, count]) => (
              <span key={name} className="px-2 py-1 bg-blue-500/10 text-blue-400 border border-blue-500/20 rounded text-[10px] font-medium">
                {name} ({count})
              </span>
            ))}
          </div>
        </div>
      )}

      {/* MCO Table */}
      {loading && <div className="text-gray-500 text-center py-8">Loading MCOs...</div>}
      {!loading && mcos.length > 0 && (
        <div className="bg-[#0f2040] rounded-xl border border-[#1e3a5f]/50 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-[#1e3a5f]">
                  <th className="text-left px-4 py-3 text-[10px] text-gray-500 uppercase tracking-wider">MCO</th>
                  <th className="text-left px-4 py-3 text-[10px] text-gray-500 uppercase tracking-wider">Parent</th>
                  <th className="text-left px-4 py-3 text-[10px] text-gray-500 uppercase tracking-wider">State</th>
                  <th className="text-left px-4 py-3 text-[10px] text-gray-500 uppercase tracking-wider">Members</th>
                  <th className="text-left px-4 py-3 text-[10px] text-gray-500 uppercase tracking-wider">Credentialing</th>
                  <th className="text-left px-4 py-3 text-[10px] text-gray-500 uppercase tracking-wider">Status</th>
                  <th className="text-left px-4 py-3 text-[10px] text-gray-500 uppercase tracking-wider">Actions</th>
                </tr>
              </thead>
              <tbody>
                {mcos.map(m => (
                  <tr key={m.id} className="border-b border-[#1e3a5f]/30 hover:bg-[#1e3a5f]/20 transition">
                    <td className="px-4 py-3 text-white font-medium">{m.fields.mco_name || '—'}</td>
                    <td className="px-4 py-3 text-gray-400 text-xs">{m.fields.parent_company || '—'}</td>
                    <td className="px-4 py-3">
                      <span className="px-2 py-0.5 bg-[#0a1628] text-gray-300 rounded text-xs font-bold">{m.fields.state}</span>
                    </td>
                    <td className="px-4 py-3 text-gray-400 text-xs">
                      {m.fields.member_count ? `${(m.fields.member_count / 1000).toFixed(0)}K` : '—'}
                    </td>
                    <td className="px-4 py-3">{renderBadge(m.fields.credentialing_status || 'Not Started')}</td>
                    <td className="px-4 py-3">{renderBadge(m.fields.contract_status || 'Target')}</td>
                    <td className="px-4 py-3">
                      <select
                        className="bg-[#0a1628] border border-[#1e3a5f] text-gray-300 text-xs rounded px-2 py-1"
                        value=""
                        onChange={e => e.target.value && updateMCOStatus(m.id, e.target.value)}
                      >
                        <option value="">Move to...</option>
                        <option value="Target">Target</option>
                        <option value="Outreach">Outreach</option>
                        <option value="In Progress">In Progress</option>
                        <option value="Active">Active</option>
                      </select>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="px-4 py-2 border-t border-[#1e3a5f] text-xs text-gray-500">
            {mcos.length} MCO{mcos.length !== 1 ? 's' : ''}{stateFilter ? ` in ${STATE_NAMES[stateFilter] || stateFilter}` : ''}
          </div>
        </div>
      )}
    </div>
  );

  // ─── READINESS TAB ───────────────────────────────────────────────

  const renderReadiness = () => {
    if (!readiness) return <div className="text-gray-500 text-center py-12">Loading readiness data...</div>;

    const scoreColor = readiness.readiness_score >= 75 ? 'text-green-400' : readiness.readiness_score >= 50 ? 'text-amber-400' : 'text-red-400';
    const barColor = readiness.readiness_score >= 75 ? 'bg-green-500' : readiness.readiness_score >= 50 ? 'bg-amber-500' : 'bg-red-500';

    return (
      <div className="space-y-6">
        {/* Readiness Score */}
        <div className="bg-[#0f2040] rounded-xl p-6 border border-[#1e3a5f]/50">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-bold text-white">🌀 Hurricane Season Readiness</h2>
            <span className={`text-2xl font-black ${scoreColor}`}>{readiness.readiness_score}%</span>
          </div>
          <div className="w-full bg-[#0a1628] rounded-full h-6 overflow-hidden">
            <div className={`h-full ${barColor} rounded-full transition-all duration-500 flex items-center justify-center text-xs font-bold text-white`}
              style={{ width: `${Math.max(readiness.readiness_score, 5)}%` }}>
              {readiness.readiness_score}%
            </div>
          </div>
        </div>

        {/* Checklist */}
        <div className="grid grid-cols-4 gap-4">
          {[
            { label: 'Transport Partners', ready: !readiness.gaps.transport, count: readiness.transport_partners_ready, need: 3, icon: '🚗' },
            { label: 'Housing Partners', ready: !readiness.gaps.housing, count: readiness.housing_partners_ready, need: 2, icon: '🏠' },
            { label: 'Medical Partners', ready: !readiness.gaps.medical, count: readiness.medical_partners_ready, need: 2, icon: '💊' },
            { label: 'MCO Contracts', ready: !readiness.gaps.mcos, count: readiness.active_mco_contracts, need: 1, icon: '🏥' },
          ].map(item => (
            <div key={item.label} className={`bg-[#0f2040] rounded-xl p-4 border text-center ${item.ready ? 'border-green-500/30' : 'border-red-500/30'}`}>
              <div className="text-2xl mb-2">{item.icon}</div>
              <div className={`text-2xl font-black ${item.ready ? 'text-green-400' : 'text-red-400'}`}>
                {item.ready ? '✓' : `${item.count}/${item.need}`}
              </div>
              <div className="text-[10px] text-gray-500 uppercase mt-1">{item.label}</div>
              <div className={`text-[10px] mt-1 ${item.ready ? 'text-green-400' : 'text-red-400'}`}>
                {item.ready ? 'READY' : `Need ${item.need - item.count} more`}
              </div>
            </div>
          ))}
        </div>

        {/* Action Items */}
        <div className="bg-[#0f2040] rounded-xl p-4 border border-[#1e3a5f]/50">
          <h3 className="text-sm font-bold text-amber-400 mb-3">⚡ Next Actions to Reach 100%</h3>
          <div className="space-y-2">
            {readiness.gaps.transport && (
              <div className="flex items-center gap-2 text-sm text-gray-300">
                <span className="text-red-400">●</span> Sign {3 - readiness.transport_partners_ready} transport partner(s) — Uber Health, Lyft, or fleet operators
              </div>
            )}
            {readiness.gaps.housing && (
              <div className="flex items-center gap-2 text-sm text-gray-300">
                <span className="text-red-400">●</span> Sign {2 - readiness.housing_partners_ready} housing partner(s) — Extended Stay America, Marriott
              </div>
            )}
            {readiness.gaps.medical && (
              <div className="flex items-center gap-2 text-sm text-gray-300">
                <span className="text-red-400">●</span> Sign {2 - readiness.medical_partners_ready} medical partner(s) — Home health or DME providers
              </div>
            )}
            {readiness.gaps.mcos && (
              <div className="flex items-center gap-2 text-sm text-gray-300">
                <span className="text-red-400">●</span> Secure 1 MCO contract — Target FL/TX/LA Medicaid MCOs
              </div>
            )}
            {!Object.values(readiness.gaps).some(g => g) && (
              <div className="flex items-center gap-2 text-sm text-green-400">
                <span>✓</span> HAVEN is ready for hurricane season deployment
              </div>
            )}
          </div>
        </div>

        {/* Network Totals */}
        <div className="bg-[#0f2040] rounded-xl p-4 border border-[#1e3a5f]/50">
          <h3 className="text-sm font-bold text-blue-400 mb-3">📊 Network Totals</h3>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <div className="text-[10px] text-gray-500 uppercase mb-1">Total Partners</div>
              <div className="text-2xl font-black text-blue-400">{readiness.total_partners}</div>
            </div>
            <div>
              <div className="text-[10px] text-gray-500 uppercase mb-1">Total MCOs</div>
              <div className="text-2xl font-black text-purple-400">{readiness.total_mcos}</div>
            </div>
          </div>
        </div>
      </div>
    );
  };

  // ─── MAIN RENDER ─────────────────────────────────────────────────

  return (
    <div className="min-h-screen bg-[#0a1628] text-white">
      {/* Notification */}
      {notification && (
        <div className={`fixed top-4 right-4 z-50 px-4 py-3 rounded-lg shadow-lg text-sm font-medium ${notification.type === 'success' ? 'bg-green-600 text-white' : 'bg-red-600 text-white'}`}>
          {notification.message}
        </div>
      )}

      {/* Tab Navigation */}
      <div className="bg-[#0f2040] border-b border-[#1e3a5f] sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex items-center gap-1 overflow-x-auto py-1">
            <button
              onClick={onBackToNexus}
              className="px-3 py-2 text-xs font-bold text-gray-400 hover:text-white hover:bg-[#1e3a5f] rounded-lg transition whitespace-nowrap"
            >
              ← NEXUS
            </button>
            <div className="w-px h-6 bg-[#1e3a5f] mx-1" />
            {TABS.map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-3 py-2 text-xs font-bold rounded-lg transition whitespace-nowrap ${
                  activeTab === tab.id
                    ? 'bg-blue-600/20 text-blue-400 border border-blue-500/30'
                    : 'text-gray-400 hover:text-white hover:bg-[#1e3a5f]'
                }`}
              >
                {tab.icon} {tab.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 py-6">
        {activeTab === 'dashboard' && renderDashboard()}
        {activeTab === 'transport' && renderPartnerTable(
          transportPartners, 'transport', 'company_name',
          [
            { key: 'partner_type', label: 'Type' },
            { key: 'states_served', label: 'States' },
          ],
        )}
        {activeTab === 'housing' && renderPartnerTable(
          housingPartners, 'housing', 'property_name',
          [
            { key: 'partner_type', label: 'Type' },
            { key: 'chain_brand', label: 'Chain' },
            { key: 'state', label: 'State' },
          ],
        )}
        {activeTab === 'medical' && renderPartnerTable(
          medicalPartners, 'medical', 'company_name',
          [
            { key: 'partner_type', label: 'Type' },
            { key: 'states_served', label: 'States' },
          ],
        )}
        {activeTab === 'mcos' && renderMCOTable()}
        {activeTab === 'readiness' && renderReadiness()}
      </div>
    </div>
  );
};

export default HAVENSystem;
