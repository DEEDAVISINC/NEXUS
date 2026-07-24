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

interface VaultSystemProps {
  onBackToNexus: () => void;
  onNavigate?: (system: ViewType, tab?: string) => void;
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

interface VaultRecord {
  id: string;
  title: string;
  agency: string;
  value?: number;
  status: string;
  contract_type: string;
  service_type: string;
  program_line?: string;
  service_area?: string;
  champs_provider_id?: string;
  agreement_role?: string;
  systems?: {
    prism_contract_id?: string;
    qc_contract_id?: string;
    compass_contract_id?: string;
    vendor_id?: string;
    atlas_project_id?: string;
  };
  timeline?: {
    won?: string;
    start_date?: string;
    end_date?: string;
  };
  health?: {
    overall?: number;
    compliance?: string;
  };
  payer?: string;
  plan_name?: string;
  profile_path?: string;
  naics?: string;
  set_aside?: string;
}

const TAB_IDS = ['dashboard', 'registry', 'timeline'] as const;

const STATUS_STYLES: Record<string, string> = {
  Active: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
  Completed: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
  'On Hold': 'bg-amber-500/20 text-amber-400 border-amber-500/30',
  Cancelled: 'bg-red-500/20 text-red-400 border-red-500/30',
};

const formatCurrency = (n: number) =>
  n >= 1_000_000
    ? `$${(n / 1_000_000).toFixed(1)}M`
    : n >= 1_000
      ? `$${(n / 1_000).toFixed(0)}K`
      : n > 0
        ? `$${n.toLocaleString()}`
        : null;

const agreementTypeCount = (records: VaultRecord[]) =>
  new Set(records.map((r) => r.contract_type).filter(Boolean)).size;

const VaultAgreementCard: React.FC<{
  record: VaultRecord;
  onClick: () => void;
}> = ({ record, onClick }) => (
  <button
    type="button"
    onClick={onClick}
    className="w-full text-left p-4 bg-gray-700/40 rounded-lg border border-gray-600/50 hover:border-amber-500/40 transition-all"
  >
    <div className="flex flex-wrap items-start justify-between gap-2">
      <div className="min-w-0 flex-1">
        <div className="font-bold text-white">{record.title}</div>
        <div className="text-sm text-gray-400">{record.agency}</div>
        {record.program_line && (
          <div className="text-xs text-amber-400/90 mt-1">{record.program_line}</div>
        )}
      </div>
      <span
        className={`px-2 py-1 text-xs rounded border shrink-0 ${
          STATUS_STYLES[record.status] || STATUS_STYLES.Active
        }`}
      >
        {record.status}
      </span>
    </div>
    <div className="flex flex-wrap gap-2 mt-3">
      <span className="px-2 py-0.5 text-[10px] uppercase tracking-wide rounded bg-gray-800 text-gray-300 border border-gray-600">
        {record.contract_type}
      </span>
      {record.service_type && (
        <span className="px-2 py-0.5 text-[10px] uppercase tracking-wide rounded bg-gray-800 text-gray-300 border border-gray-600">
          {record.service_type}
        </span>
      )}
    </div>
    <div className="flex flex-wrap gap-x-4 gap-y-1 mt-2 text-xs text-gray-500">
      <span className="font-mono">{record.id}</span>
      {record.systems?.vendor_id && <span>Vendor {record.systems.vendor_id}</span>}
      {record.champs_provider_id && <span>CHAMPS {record.champs_provider_id}</span>}
      {record.service_area && <span>{record.service_area}</span>}
    </div>
    {record.agreement_role && (
      <div className="mt-2 text-xs text-gray-400 border-t border-gray-700/60 pt-2">
        {record.agreement_role}
      </div>
    )}
  </button>
);

const VaultSystem: React.FC<VaultSystemProps> = ({
  onBackToNexus,
  onNavigate,
  activeTab,
  setActiveTab,
}) => {
  const resolvedTab = TAB_IDS.includes(activeTab as (typeof TAB_IDS)[number]) ? activeTab : 'dashboard';

  const [records, setRecords] = useState<VaultRecord[]>([]);
  const [selected, setSelected] = useState<VaultRecord | null>(null);
  const [detail, setDetail] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [apiError, setApiError] = useState<string | null>(null);

  const loadVault = useCallback(async () => {
    setLoading(true);
    setApiError(null);
    try {
      const res: any = await api.getNexusContracts();
      const list = res?.contracts || [];
      setRecords(list);
      if (selected) {
        const fresh = list.find((c: VaultRecord) => c.id === selected.id);
        if (fresh) setSelected(fresh);
      }
    } catch (e: any) {
      setApiError(e?.message || 'Could not load VAULT');
      setRecords([]);
    } finally {
      setLoading(false);
    }
  }, [selected]);

  useEffect(() => {
    loadVault();
  }, [loadVault]);

  const loadDetail = useCallback(async (record: VaultRecord) => {
    try {
      const res: any = await api.getNexusContract(record.id);
      setDetail(res);
    } catch {
      setDetail(null);
    }
  }, []);

  const selectRecord = (c: VaultRecord) => {
    setSelected(c);
    setActiveTab('registry');
    loadDetail(c);
  };

  const stats = useMemo(() => {
    const active = records.filter((c) => c.status === 'Active');
    const lanes = new Set(records.map((c) => c.service_type).filter(Boolean));
    return {
      total: records.length,
      active: active.length,
      types: agreementTypeCount(records),
      lanes: lanes.size,
    };
  }, [records]);

  const activeRecords = useMemo(
    () => records.filter((c) => c.status === 'Active'),
    [records]
  );

  const tabs = [
    { id: 'dashboard', label: 'Dashboard', icon: '📊' },
    { id: 'registry', label: 'The Vault', icon: '🔐' },
    { id: 'timeline', label: 'Events', icon: '🕐' },
  ];

  return (
    <div className={NEXUS_SHELL_PAGE}>
      <div className={`${NEXUS_SHELL_PAD} ${NEXUS_CONTAINER}`}>
        <div className="flex flex-wrap items-start justify-between gap-4 mb-6">
          <div>
            <button
              type="button"
              onClick={onBackToNexus}
              className="text-sm text-gray-400 hover:text-white mb-2 transition-colors"
            >
              ← NEXUS Command Center
            </button>
            <h1 className={NEXUS_TITLE}>VAULT</h1>
            <p className={NEXUS_SUBTITLE}>
              Agreement file cabinet — who, what, IDs, and POP. Not a spend tracker. Revenue and invoices live in VERTEX.
            </p>
          </div>
          <div className="flex gap-2">
            <button type="button" onClick={loadVault} className={NEXUS_BTN_SECONDARY}>
              Refresh
            </button>
          </div>
        </div>

        {apiError && (
          <div className="mb-4 p-4 bg-red-900/30 border border-red-500/40 rounded-xl text-red-300 text-sm flex justify-between items-center">
            <span>{apiError}</span>
            <button type="button" onClick={loadVault} className={NEXUS_BTN_PRIMARY}>
              Retry
            </button>
          </div>
        )}

        <div className="flex flex-wrap gap-2 mb-6">
          {tabs.map((t) => (
            <button
              key={t.id}
              type="button"
              onClick={() => setActiveTab(t.id)}
              className={`px-4 py-2 rounded-lg text-sm font-semibold transition-all ${
                resolvedTab === t.id ? NEXUS_TAB_ACTIVE : NEXUS_TAB_IDLE
              }`}
            >
              {t.icon} {t.label}
            </button>
          ))}
        </div>

        {resolvedTab === 'dashboard' && (
          <>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
              <NexusMetricCard label="In the Vault" value={stats.total} icon="🔐" accent="purple" />
              <NexusMetricCard label="Active Agreements" value={stats.active} icon="✅" accent="green" />
              <NexusMetricCard label="Agreement Types" value={stats.types} icon="📂" accent="yellow" />
              <NexusMetricCard label="Service Lanes" value={stats.lanes} icon="🔀" accent="teal" />
            </div>

            <NexusPanel title="Active Agreements">
              {loading ? (
                <p className="text-gray-400 text-sm">Loading vault…</p>
              ) : activeRecords.length === 0 ? (
                <p className="text-gray-400 text-sm">
                  No active agreements in the vault yet. Enrolled vendor and service contracts sync on load.
                </p>
              ) : (
                <div className="space-y-3">
                  {activeRecords.map((c) => (
                    <VaultAgreementCard key={c.id} record={c} onClick={() => selectRecord(c)} />
                  ))}
                </div>
              )}
            </NexusPanel>

            {records.length > activeRecords.length && (
              <p className="text-xs text-gray-500 mt-4">
                {records.length - activeRecords.length} non-active record
                {records.length - activeRecords.length !== 1 ? 's' : ''} — open The Vault tab to view all.
              </p>
            )}
          </>
        )}

        {resolvedTab === 'registry' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-1 space-y-2 max-h-[70vh] overflow-y-auto">
              {records.map((c) => (
                <button
                  key={c.id}
                  type="button"
                  onClick={() => selectRecord(c)}
                  className={`w-full text-left p-3 rounded-lg border transition-all ${
                    selected?.id === c.id
                      ? 'bg-amber-500/10 border-amber-500/50'
                      : 'bg-gray-800/50 border-gray-700 hover:border-gray-600'
                  }`}
                >
                  <div className="font-semibold text-white text-sm">{c.title}</div>
                  <div className="text-xs text-gray-500">{c.id}</div>
                </button>
              ))}
            </div>

            <div className="lg:col-span-2">
              {selected ? (
                <NexusPanel title={selected.title}>
                  <div className="grid grid-cols-2 gap-4 text-sm mb-6">
                    <div>
                      <div className="text-gray-500 text-xs uppercase">Buyer / Payer</div>
                      <div className="text-white">{selected.agency}</div>
                    </div>
                    <div>
                      <div className="text-gray-500 text-xs uppercase">Status</div>
                      <div className="text-emerald-400">{selected.status}</div>
                    </div>
                    <div>
                      <div className="text-gray-500 text-xs uppercase">Type</div>
                      <div className="text-white">{selected.contract_type}</div>
                    </div>
                    <div>
                      <div className="text-gray-500 text-xs uppercase">Service</div>
                      <div className="text-white">{selected.service_type}</div>
                    </div>
                    {selected.systems?.vendor_id && (
                      <div>
                        <div className="text-gray-500 text-xs uppercase">Vendor ID</div>
                        <div className="text-white font-mono">{selected.systems.vendor_id}</div>
                      </div>
                    )}
                    {selected.plan_name && (
                      <div>
                        <div className="text-gray-500 text-xs uppercase">Plan</div>
                        <div className="text-white">{selected.plan_name}</div>
                      </div>
                    )}
                    {selected.program_line && (
                      <div>
                        <div className="text-gray-500 text-xs uppercase">Program line</div>
                        <div className="text-amber-400">{selected.program_line}</div>
                      </div>
                    )}
                    {selected.service_area && (
                      <div>
                        <div className="text-gray-500 text-xs uppercase">Service area</div>
                        <div className="text-white">{selected.service_area}</div>
                      </div>
                    )}
                    {selected.champs_provider_id && (
                      <div>
                        <div className="text-gray-500 text-xs uppercase">CHAMPS provider ID</div>
                        <div className="text-white font-mono">{selected.champs_provider_id}</div>
                      </div>
                    )}
                    {selected.agreement_role && (
                      <div className="col-span-2">
                        <div className="text-gray-500 text-xs uppercase">DDI role</div>
                        <div className="text-white">{selected.agreement_role}</div>
                      </div>
                    )}
                    {selected.value != null && selected.value > 0 && (
                      <div>
                        <div className="text-gray-500 text-xs uppercase">Est. contract value</div>
                        <div className="text-white">{formatCurrency(selected.value)}</div>
                      </div>
                    )}
                    {selected.profile_path && (
                      <div className="col-span-2">
                        <div className="text-gray-500 text-xs uppercase">QC Profile</div>
                        <div className="text-cyan-400 text-xs font-mono break-all">{selected.profile_path}</div>
                      </div>
                    )}
                  </div>

                  {detail?.qc && (
                    <div className="mb-4 p-3 bg-gray-700/30 rounded-lg text-sm">
                      <div className="text-gray-400 text-xs mb-1">QC DELIVERIES</div>
                      <div className="text-white">{detail.qc.delivery_count ?? 0} units tracked</div>
                    </div>
                  )}

                  {detail?.prism && (
                    <div className="mb-4 p-3 bg-gray-700/30 rounded-lg text-sm">
                      <div className="text-gray-400 text-xs mb-1">PRISM ORDERS</div>
                      <div className="text-white">
                        {detail.prism.active} active · {detail.prism.completed} complete ·{' '}
                        {detail.prism.total_orders} total
                      </div>
                    </div>
                  )}

                  <div className="flex flex-wrap gap-2 pt-4 border-t border-gray-700">
                    <p className="w-full text-xs text-gray-500 mb-1">
                      Trips, claims, and revenue → PRISM + VERTEX. VAULT holds the agreement record only.
                    </p>
                    {onNavigate && (
                      <>
                        <button
                          type="button"
                          onClick={() => onNavigate('prism', 'transport')}
                          className={NEXUS_BTN_PRIMARY}
                        >
                          Open PRISM
                        </button>
                        <button
                          type="button"
                          onClick={() => onNavigate('vertex', 'nemt')}
                          className={NEXUS_BTN_SECONDARY}
                        >
                          Open VERTEX NEMT
                        </button>
                      </>
                    )}
                  </div>
                </NexusPanel>
              ) : (
                <NexusPanel title="Select a record">
                  <p className="text-gray-400 text-sm">Choose an agreement from the vault to view details and system links.</p>
                </NexusPanel>
              )}
            </div>
          </div>
        )}

        {resolvedTab === 'timeline' && (
          <NexusPanel title="Vault Events">
            {selected && detail?.events?.length > 0 ? (
              <div className="space-y-2">
                {detail.events.map((evt: any) => (
                  <div
                    key={evt.id}
                    className="flex flex-wrap gap-2 p-3 bg-gray-700/30 rounded-lg text-sm"
                  >
                    <span className="text-emerald-400 font-bold">{evt.source}</span>
                    <span className="text-gray-600">→</span>
                    <span className="text-cyan-400">{evt.target}</span>
                    <span className="text-gray-300">{evt.type?.replace(/_/g, ' ')}</span>
                    <span className="text-gray-500 text-xs ml-auto">{evt.timestamp?.slice(0, 10)}</span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-400 text-sm">
                Select a record in The Vault to view pipeline events.
              </p>
            )}
          </NexusPanel>
        )}
      </div>
    </div>
  );
};

export default VaultSystem;
