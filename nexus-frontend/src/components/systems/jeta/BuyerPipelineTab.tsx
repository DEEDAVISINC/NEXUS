import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { api } from '../../../api/client';

/** Matches api_server JETA_STAGE_LABELS + Airtable `JETA_Buyers` */
export const JETA_STAGE_LABELS = [
  'Identified',
  'Qualified',
  'Contacted',
  'Engaged',
  'Benchmarked',
  'Presenting',
  'NCNDA Signed',
  'Deal Active',
  'Closed',
] as const;

/** Conventional vs SAF — Airtable single select `Fuel Type` on JETA_Buyers / JETA_Deals */
export const JETA_FUEL_TYPES = ['Conventional', 'SAF', 'Both'] as const;
export type JetaFuelType = (typeof JETA_FUEL_TYPES)[number];

export function normalizeJetaFuelType(v: string | undefined | null): JetaFuelType {
  const s = (v || '').trim();
  if (s === 'SAF' || s === 'Both' || s === 'Conventional') return s;
  return 'Conventional';
}

export function buyerShowsSafBadge(b: { fuelType?: string }): boolean {
  const ft = normalizeJetaFuelType(b.fuelType);
  return ft === 'SAF' || ft === 'Both';
}

const STAGE_BADGE_CLASS: Record<number, string> = {
  1: 'bg-slate-600 text-white ring-1 ring-slate-500',
  2: 'bg-zinc-600 text-white ring-1 ring-zinc-500',
  3: 'bg-blue-600 text-white ring-1 ring-blue-500',
  4: 'bg-cyan-600 text-white ring-1 ring-cyan-500',
  5: 'bg-teal-600 text-white ring-1 ring-teal-500',
  6: 'bg-emerald-600 text-white ring-1 ring-emerald-500',
  7: 'bg-amber-600 text-white ring-1 ring-amber-500',
  8: 'bg-orange-600 text-white ring-1 ring-orange-500',
  9: 'bg-violet-600 text-white ring-1 ring-violet-500',
};

export interface JetaBuyer {
  id: string;
  companyName: string;
  contactName: string;
  email: string;
  phone: string;
  state: string;
  city: string;
  /** Airport / FBO name for outreach (Airtable: Airport) */
  airport?: string;
  /** ICAO airport code for supplier lookup (Airtable: ICAO Code), e.g. KDTW */
  icaoCode?: string;
  website: string;
  buyerType: string;
  pipelineStage: number;
  stageLabel: string;
  lastContactDate: string;
  /** Set on buyer for Outreach Center scheduling (Airtable: Next Touch Date) */
  nextTouchDate?: string;
  nextAction: string;
  notes: string;
  /** Airtable: Fuel Type — Conventional | SAF | Both */
  fuelType?: string;
  /** Airtable Source — e.g. FAA 5010 Import */
  importSource?: string;
  /** Airtable Supplier Status — Open | Branded | Unknown */
  supplierStatus?: string;
  /** Airtable Priority Score — 0–130 */
  priorityScore?: number;
  /** From priority engine — e.g. PRIORITY, HIGH VALUE */
  priorityTags?: string[];
  supplyAdjacent?: boolean;
  canada?: boolean;
  country?: string;
  scoreBreakdown?: Record<string, number>;
  createdTime?: string;
}

/** After CSV airport imports, narrow the pipeline to matching Airtable Source values */
export type PipelineImportFilter = 'faa_5010' | 'transport_canada' | 'csv_imports';

function buyerMatchesPipelineImportFilter(b: JetaBuyer, f: PipelineImportFilter): boolean {
  const src = (b.importSource || '').trim();
  if (f === 'faa_5010') return src === 'FAA 5010 Import';
  if (f === 'transport_canada') return src === 'Transport Canada Import';
  if (f === 'csv_imports') return src === 'FAA 5010 Import' || src === 'Transport Canada Import';
  return true;
}

export interface BuyerPipelineTabProps {
  /** Narrow table to FAA 5010, Transport Canada, or both CSV import sources */
  pipelineImportFilter?: PipelineImportFilter | null;
  onClearPipelineImportFilter?: () => void;
  /** Increment to trigger a full reload of buyers (e.g. after CSV import) */
  refreshKey?: number;
}

function normalizeSupplierStatus(v: string | undefined): 'Open' | 'Branded' | 'Unknown' {
  const s = (v || '').trim();
  if (s === 'Open' || s === 'Branded' || s === 'Unknown') return s;
  return 'Unknown';
}

export const JETA_PRIORITY_MAX = 130;

export const PriorityScoreBar: React.FC<{ score: number | undefined }> = ({ score }) => {
  const s = Math.max(
    0,
    Math.min(JETA_PRIORITY_MAX, Math.round(Number.isFinite(Number(score)) ? Number(score) : 0)),
  );
  const pct = JETA_PRIORITY_MAX > 0 ? (s / JETA_PRIORITY_MAX) * 100 : 0;
  const barColor = s >= 78 ? 'bg-emerald-500' : s >= 39 ? 'bg-amber-400' : 'bg-gray-500';
  return (
    <div className="flex min-w-[108px] max-w-[160px] items-center gap-2" title={`Priority score ${s}/${JETA_PRIORITY_MAX}`}>
      <div className="h-2.5 min-w-[72px] flex-1 overflow-hidden rounded-full bg-gray-800 ring-1 ring-gray-700/80">
        <div className={`h-2.5 rounded-full transition-[width] ${barColor}`} style={{ width: `${pct}%` }} />
      </div>
      <span className="w-9 shrink-0 text-right text-xs font-semibold tabular-nums text-gray-200">{s}</span>
    </div>
  );
};

const SupplierStatusBadge: React.FC<{ status: string | undefined }> = ({ status }) => {
  const s = normalizeSupplierStatus(status);
  const cls =
    s === 'Open'
      ? 'bg-emerald-900/85 text-emerald-100 ring-1 ring-emerald-600/70'
      : s === 'Branded'
        ? 'bg-amber-900/80 text-amber-100 ring-1 ring-amber-600/60'
        : 'bg-gray-700/90 text-gray-300 ring-1 ring-gray-600/60';
  const title =
    s === 'Open'
      ? 'No major branded supplier in reference list — priority target'
      : s === 'Branded'
        ? 'Avfuel / P66 / World Fuel / Air BP–class supplier found — approach carefully'
        : 'Supplier lookup pending or not run';
  return (
    <span title={title} className={`inline-flex rounded-full px-2 py-0.5 text-[10px] font-bold uppercase tracking-wide ${cls}`}>
      {s}
    </span>
  );
};

const StageBadge: React.FC<{ stage: number; label: string }> = ({ stage, label }) => {
  const cls = STAGE_BADGE_CLASS[stage] || STAGE_BADGE_CLASS[1];
  return (
    <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold ${cls}`}>
      {stage} {label}
    </span>
  );
};

const emptyForm = (): Record<string, string | number> => ({
  companyName: '',
  contactName: '',
  email: '',
  phone: '',
  state: '',
  city: '',
  airport: '',
  icaoCode: '',
  website: '',
  buyerType: '',
  pipelineStage: 1,
  lastContactDate: '',
  nextAction: '',
  notes: '',
  fuelType: 'Conventional',
});

function buyerToForm(b: JetaBuyer): Record<string, string | number> {
  return {
    companyName: b.companyName || '',
    contactName: b.contactName || '',
    email: b.email || '',
    phone: b.phone || '',
    state: b.state || '',
    city: b.city || '',
    airport: b.airport || '',
    icaoCode: b.icaoCode || '',
    website: b.website || '',
    buyerType: b.buyerType || '',
    pipelineStage: b.pipelineStage || 1,
    lastContactDate: b.lastContactDate || '',
    nextAction: b.nextAction || '',
    notes: b.notes || '',
    fuelType: normalizeJetaFuelType(b.fuelType),
  };
}

/** Prefer explicit ICAO Code field; else extract a 4-letter code from Airport text. */
export function resolveIcaoFromBuyer(b: JetaBuyer): string | null {
  const raw = (b.icaoCode || '').trim().toUpperCase();
  if (/^[A-Z][A-Z0-9]{3}$/.test(raw)) return raw;
  const ap = (b.airport || '').trim();
  if (!ap) return null;
  const m = ap.toUpperCase().match(/\b([A-Z][A-Z0-9]{3})\b/);
  return m ? m[1] : null;
}

const SupplierLookupPanel: React.FC<{ icao: string; airportLabel?: string }> = ({ icao, airportLabel }) => {
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [suppliers, setSuppliers] = useState<{ supplier_name: string; fuel_type: string }[]>([]);
  const [meta, setMeta] = useState<{ stored_count?: number; airport_name?: string } | null>(null);

  const runLookup = useCallback(async () => {
    setLoading(true);
    setErr(null);
    try {
      const res = (await api.getJetaSuppliersLookup(icao)) as {
        success?: boolean;
        error?: string;
        suppliers?: { supplier_name: string; fuel_type: string }[];
        notice?: string;
        airport_name?: string;
        stored_count?: number;
      };
      if (res.success === false) {
        setErr(res.error || 'Lookup failed');
        setSuppliers([]);
        return;
      }
      setSuppliers(res.suppliers || []);
      setNotice(res.notice || null);
      setMeta({ stored_count: res.stored_count, airport_name: res.airport_name });
    } catch (e: unknown) {
      setErr(e instanceof Error ? e.message : 'Lookup failed');
      setSuppliers([]);
    } finally {
      setLoading(false);
    }
  }, [icao]);

  return (
    <div className="mt-6 rounded-lg border border-cyan-900/45 bg-gradient-to-br from-cyan-950/35 to-gray-900/40 p-4 ring-1 ring-cyan-900/25">
      <h5 className="text-xs font-bold uppercase tracking-wide text-cyan-200/90">Supplier lookup</h5>
      <p className="mt-1 text-xs text-gray-500">
        Reference fuel suppliers for{' '}
        <span className="font-mono text-cyan-200/90">{icao}</span>
        {airportLabel ? ` · ${airportLabel}` : ''}. Uses IATA Fuel program context + OurAirports; rows are saved to{' '}
        <code className="text-gray-500">JETA_SupplierDirectory</code>.
      </p>
      <button
        type="button"
        disabled={loading}
        onClick={() => runLookup()}
        className="mt-3 w-full rounded-lg border border-cyan-700/60 bg-cyan-950/50 py-2.5 text-sm font-semibold text-cyan-100 hover:bg-cyan-900/50 disabled:opacity-50"
      >
        {loading ? 'Looking up…' : 'Look Up Airport Suppliers'}
      </button>
      {err && <p className="mt-2 text-xs text-red-300">{err}</p>}
      {notice && !err && <p className="mt-2 text-xs text-gray-500">{notice}</p>}
      {meta?.airport_name && (
        <p className="mt-2 text-xs text-gray-400">
          Resolved airport: <span className="text-gray-200">{meta.airport_name}</span>
          {typeof meta.stored_count === 'number' ? (
            <span className="text-gray-500"> · {meta.stored_count} row(s) stored in Airtable</span>
          ) : null}
        </p>
      )}
      {suppliers.length > 0 && (
        <ul className="mt-3 max-h-64 space-y-2 overflow-y-auto">
          {suppliers.map((s, i) => (
            <li
              key={`${s.supplier_name}-${i}`}
              className="rounded-md border border-gray-700/80 bg-gray-800/50 px-3 py-2 text-sm"
            >
              <p className="font-medium text-white">{s.supplier_name}</p>
              <p className="text-xs text-gray-400">{s.fuel_type || '—'}</p>
            </li>
          ))}
        </ul>
      )}
      {!loading && !err && suppliers.length === 0 && (
        <p className="mt-2 text-xs text-gray-600">Run a lookup to load supplier cards (if available for this airport).</p>
      )}
    </div>
  );
};

export const BuyerPipelineTab: React.FC<BuyerPipelineTabProps> = ({
  pipelineImportFilter = null,
  onClearPipelineImportFilter,
  refreshKey = 0,
}) => {
  const [buyers, setBuyers] = useState<JetaBuyer[]>([]);
  const [filterOptions, setFilterOptions] = useState<{
    states: string[];
    buyerTypes: string[];
    supplierStatuses: string[];
  }>({
    states: [],
    buyerTypes: [],
    supplierStatuses: [],
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [hint, setHint] = useState<string | null>(null);

  const [filterState, setFilterState] = useState('');
  const [filterBuyerType, setFilterBuyerType] = useState('');
  const [filterStage, setFilterStage] = useState('');
  const [fuelFilter, setFuelFilter] = useState<'all' | 'conventional' | 'saf'>('all');
  const [filterSupplierStatus, setFilterSupplierStatus] = useState('');
  const [filterTopProspects, setFilterTopProspects] = useState(false);

  const [selected, setSelected] = useState<JetaBuyer | null>(null);
  const [modalOpen, setModalOpen] = useState(false);
  const [modalEditId, setModalEditId] = useState<string | null>(null);
  const [form, setForm] = useState<Record<string, string | number>>(emptyForm());
  const [saving, setSaving] = useState(false);
  const [potentialSellerLoading, setPotentialSellerLoading] = useState(false);
  const [potentialSellerNotice, setPotentialSellerNotice] = useState<string | null>(null);

  useEffect(() => {
    setPotentialSellerNotice(null);
  }, [selected?.id]);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    setHint(null);
    try {
      const res = (await api.getJetaBuyers({
        state: filterState || undefined,
        buyer_type: filterBuyerType || undefined,
        pipeline_stage: filterStage || undefined,
        supplier_status: filterSupplierStatus || undefined,
        min_priority_score: filterTopProspects ? 60 : undefined,
      })) as {
        success?: boolean;
        buyers?: JetaBuyer[];
        filterOptions?: { states: string[]; buyerTypes: string[]; supplierStatuses?: string[] };
        error?: string;
        hint?: string;
      };
      if (res.hint) setHint(res.hint);
      if (res.success === false && res.error) {
        setError(res.error);
        setBuyers([]);
      } else {
        setBuyers(res.buyers || []);
        if (res.filterOptions) {
          setFilterOptions({
            states: res.filterOptions.states || [],
            buyerTypes: res.filterOptions.buyerTypes || [],
            supplierStatuses: res.filterOptions.supplierStatuses || [],
          });
        }
      }
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Failed to load buyers');
      setBuyers([]);
    } finally {
      setLoading(false);
    }
  }, [filterState, filterBuyerType, filterStage, filterSupplierStatus, filterTopProspects]);

  useEffect(() => {
    load();
  }, [load]);

  useEffect(() => {
    if (refreshKey > 0) {
      load();
    }
  }, [refreshKey, load]);

  const filteredBuyers = useMemo(() => {
    return buyers.filter((b) => {
      if (pipelineImportFilter) {
        if (!buyerMatchesPipelineImportFilter(b, pipelineImportFilter)) return false;
      }
      const ft = normalizeJetaFuelType(b.fuelType);
      if (fuelFilter === 'all') return true;
      if (fuelFilter === 'conventional') return ft === 'Conventional' || ft === 'Both';
      if (fuelFilter === 'saf') return ft === 'SAF' || ft === 'Both';
      return true;
    });
  }, [buyers, fuelFilter, pipelineImportFilter]);

  const openNew = () => {
    setModalEditId(null);
    setForm(emptyForm());
    setModalOpen(true);
  };

  const openEdit = (b: JetaBuyer) => {
    setSelected(null);
    setModalEditId(b.id);
    setForm(buyerToForm(b));
    setModalOpen(true);
  };

  const saveModal = async () => {
    if (!String(form.companyName || '').trim()) {
      alert('Company Name is required.');
      return;
    }
    setSaving(true);
    try {
      const payload = {
        companyName: form.companyName,
        contactName: form.contactName,
        email: form.email,
        phone: form.phone,
        state: form.state,
        city: form.city,
        airport: form.airport,
        icaoCode: form.icaoCode,
        website: form.website,
        buyerType: form.buyerType,
        pipelineStage: Number(form.pipelineStage) || 1,
        lastContactDate: form.lastContactDate || '',
        nextAction: form.nextAction,
        notes: form.notes,
        fuelType: String(form.fuelType ?? 'Conventional'),
      };
      let res: { success?: boolean; error?: string; fraud?: { tier?: string; traffic_light?: string } };
      if (modalEditId) {
        res = (await api.updateJetaBuyer(modalEditId, payload)) as { success?: boolean; error?: string };
      } else {
        res = (await api.createJetaBuyer(payload)) as { success?: boolean; error?: string; fraud?: { tier?: string } };
      }
      if (res.success === false) {
        alert(res.error || 'Save failed');
        return;
      }
      if (!modalEditId && res.fraud?.tier && res.fraud.tier !== 'GREEN') {
        alert(`Fraud / integrity score: ${res.fraud.tier}${res.fraud.traffic_light ? ` (${res.fraud.traffic_light})` : ''}`);
      }
      setModalOpen(false);
      await load();
      setSelected(null);
    } catch (e: unknown) {
      alert(e instanceof Error ? e.message : 'Save failed');
    } finally {
      setSaving(false);
    }
  };

  const selectedIcao = selected ? resolveIcaoFromBuyer(selected) : null;

  const showSupplyOpportunityBanner =
    selected &&
    selected.supplyAdjacent === true &&
    normalizeSupplierStatus(selected.supplierStatus) === 'Open';

  const addPotentialSellerFromBuyer = async () => {
    if (!selected) return;
    setPotentialSellerLoading(true);
    setPotentialSellerNotice(null);
    try {
      const res = (await api.postJetaSellerFromBuyer(selected.id)) as {
        success?: boolean;
        error?: string;
        duplicate?: boolean;
        message?: string;
        seller_id?: string;
      };
      if (res.success === false) {
        setPotentialSellerNotice(res.error || 'Request failed');
        return;
      }
      if (res.duplicate) {
        setPotentialSellerNotice(res.message || 'A seller record with this ICAO already exists.');
      } else {
        setPotentialSellerNotice(res.message || 'Created in JETA_Sellers.');
      }
    } catch (e: unknown) {
      setPotentialSellerNotice(e instanceof Error ? e.message : 'Request failed');
    } finally {
      setPotentialSellerLoading(false);
    }
  };

  return (
    <div className="relative min-h-[420px]">
      <div className="mb-6 flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h3 className="text-xl font-bold text-white">Buyer Pipeline</h3>
          <p className="text-sm text-gray-400">
            Airtable · JETA_Buyers · sorted by <span className="text-amber-200/90">priority score</span> (highest first)
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <div className="flex rounded-lg border border-gray-600 p-0.5" title="Filter by fuel scope (Both appears in both)">
            <button
              type="button"
              onClick={() => setFuelFilter('all')}
              className={`rounded-md px-2.5 py-1.5 text-xs font-semibold ${
                fuelFilter === 'all' ? 'bg-emerald-700 text-white' : 'text-gray-400 hover:text-white'
              }`}
            >
              All
            </button>
            <button
              type="button"
              onClick={() => setFuelFilter('conventional')}
              className={`rounded-md px-2.5 py-1.5 text-xs font-semibold ${
                fuelFilter === 'conventional' ? 'bg-emerald-700 text-white' : 'text-gray-400 hover:text-white'
              }`}
            >
              Conventional
            </button>
            <button
              type="button"
              onClick={() => setFuelFilter('saf')}
              className={`rounded-md px-2.5 py-1.5 text-xs font-semibold ${
                fuelFilter === 'saf' ? 'bg-emerald-700 text-white' : 'text-gray-400 hover:text-white'
              }`}
            >
              SAF
            </button>
          </div>
            <button
              type="button"
              onClick={() => setFilterTopProspects((v) => !v)}
              className={`rounded-lg border px-3 py-2 text-sm font-semibold shadow ${
                filterTopProspects
                  ? 'border-emerald-500/80 bg-emerald-950/50 text-emerald-100 ring-1 ring-emerald-600/50'
                  : 'border-gray-600 text-gray-300 hover:bg-gray-800'
              }`}
              title="Show only buyers with priority score ≥ 60 (out of 130)"
            >
              TOP PROSPECTS (≥60)
            </button>
            <button
              type="button"
              onClick={openNew}
              className="rounded-lg bg-gradient-to-r from-amber-600 to-orange-600 px-4 py-2 text-sm font-semibold text-white shadow hover:from-amber-500 hover:to-orange-500"
            >
              + Add New Buyer
            </button>
        </div>
      </div>

      {(error || hint) && (
        <div className="mb-4 rounded-lg border border-amber-700/50 bg-amber-950/40 px-4 py-3 text-sm text-amber-100">
          {error && <p className="font-medium text-amber-200">Error: {error}</p>}
          {hint && <p className="mt-1 text-amber-100/90">{hint}</p>}
        </div>
      )}

      {pipelineImportFilter && (
        <div className="mb-4 flex flex-wrap items-center justify-between gap-2 rounded-lg border border-amber-800/45 bg-amber-950/25 px-4 py-3 text-sm text-amber-100/95">
          <span>
            {pipelineImportFilter === 'faa_5010' && (
              <>
                Showing buyers with <span className="font-semibold text-amber-200">Source = FAA 5010 Import</span> only.
              </>
            )}
            {pipelineImportFilter === 'transport_canada' && (
              <>
                Showing buyers with <span className="font-semibold text-amber-200">Source = Transport Canada Import</span> only.
              </>
            )}
            {pipelineImportFilter === 'csv_imports' && (
              <>
                Showing <span className="font-semibold text-amber-200">FAA 5010 Import</span> and{' '}
                <span className="font-semibold text-amber-200">Transport Canada Import</span> records.
              </>
            )}
          </span>
          <div className="flex flex-wrap gap-2">
            <button
              type="button"
              onClick={() => setFilterSupplierStatus('Open')}
              className="rounded-md border border-emerald-800/50 bg-emerald-950/30 px-3 py-1.5 text-xs font-semibold text-emerald-200 hover:bg-emerald-950/50"
            >
              Show Open only (priority)
            </button>
            <button
              type="button"
              onClick={() => onClearPipelineImportFilter?.()}
              className="rounded-md border border-amber-700/50 px-3 py-1.5 text-xs font-semibold text-amber-200 hover:bg-amber-950/60"
            >
              Clear import filter
            </button>
          </div>
        </div>
      )}

      <div className="mb-4 flex flex-wrap gap-3">
        <select
          value={filterState}
          onChange={(e) => setFilterState(e.target.value)}
          className="rounded-lg border border-gray-600 bg-gray-800 px-3 py-2 text-sm text-white"
        >
          <option value="">All states</option>
          {filterOptions.states.map((s) => (
            <option key={s} value={s}>
              {s}
            </option>
          ))}
        </select>
        <select
          value={filterBuyerType}
          onChange={(e) => setFilterBuyerType(e.target.value)}
          className="rounded-lg border border-gray-600 bg-gray-800 px-3 py-2 text-sm text-white"
        >
          <option value="">All buyer types</option>
          {filterOptions.buyerTypes.map((t) => (
            <option key={t} value={t}>
              {t}
            </option>
          ))}
        </select>
        <select
          value={filterStage}
          onChange={(e) => setFilterStage(e.target.value)}
          className="rounded-lg border border-gray-600 bg-gray-800 px-3 py-2 text-sm text-white"
        >
          <option value="">All stages</option>
          {JETA_STAGE_LABELS.map((lab, i) => (
            <option key={lab} value={String(i + 1)}>
              {i + 1} {lab}
            </option>
          ))}
        </select>
        <select
          value={filterSupplierStatus}
          onChange={(e) => setFilterSupplierStatus(e.target.value)}
          title="Filter by supplier directory classification"
          className="rounded-lg border border-gray-600 bg-gray-800 px-3 py-2 text-sm text-white"
        >
          <option value="">All supplier status</option>
          {(filterOptions.supplierStatuses.length
            ? filterOptions.supplierStatuses
            : ['Unknown', 'Open', 'Branded']
          ).map((s) => (
            <option key={s} value={s}>
              {s}
            </option>
          ))}
        </select>
      </div>

      {loading ? (
        <div className="py-20 text-center text-gray-400">Loading buyers…</div>
      ) : (
        <div className="overflow-x-auto rounded-xl border border-gray-700">
          <table className="min-w-full divide-y divide-gray-700 text-left text-sm">
            <thead className="bg-gray-800/80">
              <tr>
                <th className="px-4 py-3 font-semibold text-gray-300">Company Name</th>
                <th className="px-4 py-3 font-semibold text-gray-300">Contact Name</th>
                <th className="px-4 py-3 font-semibold text-gray-300">State</th>
                <th className="px-4 py-3 font-semibold text-gray-300">Buyer Type</th>
                <th className="px-4 py-3 font-semibold text-gray-300">Supplier status</th>
                <th className="px-4 py-3 font-semibold text-gray-300">Priority</th>
                <th className="px-4 py-3 font-semibold text-gray-300">Pipeline Stage</th>
                <th className="px-4 py-3 font-semibold text-gray-300">Last Contact</th>
                <th className="px-4 py-3 font-semibold text-gray-300">Next Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-700/80">
              {filteredBuyers.length === 0 ? (
                <tr>
                  <td colSpan={9} className="px-4 py-12 text-center text-gray-500">
                    {buyers.length === 0 ? (
                      <>
                        No buyers yet. Add one or check your Airtable table name (<code className="text-gray-400">JETA_Buyers</code>).
                      </>
                    ) : (
                      <>No buyers match this fuel filter.</>
                    )}
                  </td>
                </tr>
              ) : (
                filteredBuyers.map((b) => (
                  <tr
                    key={b.id}
                    onClick={() => setSelected(b)}
                    className="cursor-pointer bg-gray-900/40 hover:bg-gray-800/80"
                  >
                    <td className="px-4 py-3 font-medium text-white">
                      <span className="align-middle">{b.companyName || '—'}</span>
                      {buyerShowsSafBadge(b) ? (
                        <span className="ml-2 inline-flex align-middle rounded bg-emerald-900/80 px-1.5 py-0.5 text-[10px] font-bold text-emerald-200 ring-1 ring-emerald-700/60">
                          SAF
                        </span>
                      ) : null}
                    </td>
                    <td className="px-4 py-3 text-gray-300">{b.contactName || '—'}</td>
                    <td className="px-4 py-3 text-gray-300">{b.state || '—'}</td>
                    <td className="px-4 py-3 text-gray-300">{b.buyerType || '—'}</td>
                    <td className="px-4 py-3 whitespace-nowrap">
                      <SupplierStatusBadge status={b.supplierStatus} />
                    </td>
                    <td className="px-4 py-3">
                      <PriorityScoreBar score={b.priorityScore} />
                    </td>
                    <td className="px-4 py-3">
                      <StageBadge stage={b.pipelineStage} label={b.stageLabel} />
                    </td>
                    <td className="px-4 py-3 text-gray-400">{b.lastContactDate || '—'}</td>
                    <td className="max-w-xs truncate px-4 py-3 text-gray-400">{b.nextAction || '—'}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      )}

      {/* Detail panel */}
      {selected && (
        <>
          <button
            type="button"
            className="fixed inset-0 z-40 bg-black/50"
            aria-label="Close panel"
            onClick={() => setSelected(null)}
          />
          <aside className="fixed right-0 top-0 z-50 flex h-full w-full max-w-md flex-col border-l border-gray-700 bg-gray-900 shadow-2xl">
            <div className="flex items-start justify-between border-b border-gray-700 px-5 py-4">
              <div>
                <h4 className="text-lg font-bold text-white">{selected.companyName || 'Buyer'}</h4>
                <StageBadge stage={selected.pipelineStage} label={selected.stageLabel} />
              </div>
              <button
                type="button"
                onClick={() => setSelected(null)}
                className="rounded-lg px-2 py-1 text-gray-400 hover:bg-gray-800 hover:text-white"
              >
                ✕
              </button>
            </div>
            <div className="flex-1 overflow-y-auto px-5 py-4 text-sm">
              {showSupplyOpportunityBanner ? (
                <div className="mb-4 rounded-lg border border-teal-600/50 bg-teal-950/45 p-4 ring-1 ring-teal-800/30">
                  <p className="text-xs font-bold uppercase tracking-wide text-teal-200/95">Supply opportunity</p>
                  <p className="mt-2 text-xs leading-relaxed text-teal-100/95">
                    This airport is near Gulf Coast refinery infrastructure. The current unbranded supply source may be a
                    candidate for JETA COURTIÈRE&apos;s seller network. Consider dual outreach: buyer contact{' '}
                    <span className="font-semibold text-teal-50">and</span> terminal/supplier contact.
                  </p>
                  <button
                    type="button"
                    disabled={potentialSellerLoading}
                    onClick={addPotentialSellerFromBuyer}
                    className="mt-3 w-full rounded-lg border border-teal-500/60 bg-teal-900/50 py-2.5 text-sm font-semibold text-teal-50 hover:bg-teal-800/60 disabled:opacity-50"
                  >
                    {potentialSellerLoading ? 'Creating…' : 'Add as Potential Seller'}
                  </button>
                  {potentialSellerNotice ? (
                    <p className="mt-2 text-xs text-teal-200/90">{potentialSellerNotice}</p>
                  ) : null}
                </div>
              ) : null}
              <dl className="space-y-3">
                {[
                  ['Contact Name', selected.contactName],
                  ['Email', selected.email],
                  ['Phone', selected.phone],
                  ['State', selected.state],
                  ['City', selected.city],
                  ['Airport / FBO', selected.airport],
                  ['ICAO Code', selected.icaoCode],
                  ['Website', selected.website],
                  ['Buyer Type', selected.buyerType],
                  ['Supplier status', normalizeSupplierStatus(selected.supplierStatus)],
                  [
                    'Priority score',
                    typeof selected.priorityScore === 'number' ? String(selected.priorityScore) : '—',
                  ],
                  ['Fuel type', normalizeJetaFuelType(selected.fuelType)],
                  ['Last Contact Date', selected.lastContactDate],
                  ['Next Action', selected.nextAction],
                  ['Notes', selected.notes],
                ].map(([k, v]) => (
                  <div key={k}>
                    <dt className="text-xs uppercase tracking-wide text-gray-500">{k}</dt>
                    <dd className="mt-0.5 text-gray-200 whitespace-pre-wrap">{v || '—'}</dd>
                  </div>
                ))}
                <div>
                  <dt className="text-xs uppercase tracking-wide text-gray-500">Record ID</dt>
                  <dd className="mt-0.5 font-mono text-xs text-gray-500">{selected.id}</dd>
                </div>
              </dl>
              {selectedIcao ? (
                <SupplierLookupPanel
                  icao={selectedIcao}
                  airportLabel={(selected.airport || '').trim() || undefined}
                />
              ) : null}
            </div>
            <div className="border-t border-gray-700 p-4">
              <button
                type="button"
                onClick={() => {
                  openEdit(selected);
                }}
                className="w-full rounded-lg bg-amber-600 py-2 text-sm font-semibold text-white hover:bg-amber-500"
              >
                Edit buyer
              </button>
            </div>
          </aside>
        </>
      )}

      {/* Modal */}
      {modalOpen && (
        <div className="fixed inset-0 z-[60] flex items-center justify-center p-4">
          <button
            type="button"
            className="absolute inset-0 bg-black/60"
            aria-label="Close modal"
            onClick={() => setModalOpen(false)}
          />
          <div className="relative z-10 max-h-[90vh] w-full max-w-lg overflow-y-auto rounded-xl border border-gray-600 bg-gray-900 p-6 shadow-2xl">
            <h4 className="mb-4 text-lg font-bold text-white">{modalEditId ? 'Edit buyer' : 'New buyer'}</h4>
            <div className="grid gap-3">
              <label className="block text-xs text-gray-400">
                Company Name *
                <input
                  className="mt-1 w-full rounded border border-gray-600 bg-gray-800 px-3 py-2 text-white"
                  value={String(form.companyName ?? '')}
                  onChange={(e) => setForm((f) => ({ ...f, companyName: e.target.value }))}
                />
              </label>
              <label className="block text-xs text-gray-400">
                Contact Name
                <input
                  className="mt-1 w-full rounded border border-gray-600 bg-gray-800 px-3 py-2 text-white"
                  value={String(form.contactName ?? '')}
                  onChange={(e) => setForm((f) => ({ ...f, contactName: e.target.value }))}
                />
              </label>
              <label className="block text-xs text-gray-400">
                Email
                <input
                  type="email"
                  className="mt-1 w-full rounded border border-gray-600 bg-gray-800 px-3 py-2 text-white"
                  value={String(form.email ?? '')}
                  onChange={(e) => setForm((f) => ({ ...f, email: e.target.value }))}
                />
              </label>
              <label className="block text-xs text-gray-400">
                Phone
                <input
                  className="mt-1 w-full rounded border border-gray-600 bg-gray-800 px-3 py-2 text-white"
                  value={String(form.phone ?? '')}
                  onChange={(e) => setForm((f) => ({ ...f, phone: e.target.value }))}
                />
              </label>
              <div className="grid grid-cols-2 gap-3">
                <label className="block text-xs text-gray-400">
                  State
                  <input
                    className="mt-1 w-full rounded border border-gray-600 bg-gray-800 px-3 py-2 text-white"
                    value={String(form.state ?? '')}
                    onChange={(e) => setForm((f) => ({ ...f, state: e.target.value }))}
                  />
                </label>
                <label className="block text-xs text-gray-400">
                  City
                  <input
                    className="mt-1 w-full rounded border border-gray-600 bg-gray-800 px-3 py-2 text-white"
                    value={String(form.city ?? '')}
                    onChange={(e) => setForm((f) => ({ ...f, city: e.target.value }))}
                  />
                </label>
              </div>
              <label className="block text-xs text-gray-400">
                Airport / FBO
                <input
                  className="mt-1 w-full rounded border border-gray-600 bg-gray-800 px-3 py-2 text-white"
                  placeholder="e.g. Detroit Metro or KDTW"
                  value={String(form.airport ?? '')}
                  onChange={(e) => setForm((f) => ({ ...f, airport: e.target.value }))}
                />
              </label>
              <label className="block text-xs text-gray-400">
                ICAO code
                <input
                  className="mt-1 w-full font-mono uppercase rounded border border-gray-600 bg-gray-800 px-3 py-2 text-white"
                  placeholder="e.g. KDTW"
                  maxLength={4}
                  value={String(form.icaoCode ?? '')}
                  onChange={(e) =>
                    setForm((f) => ({ ...f, icaoCode: e.target.value.toUpperCase().replace(/[^A-Z0-9]/g, '').slice(0, 4) }))
                  }
                />
              </label>
              <label className="block text-xs text-gray-400">
                Website
                <input
                  className="mt-1 w-full rounded border border-gray-600 bg-gray-800 px-3 py-2 text-white"
                  value={String(form.website ?? '')}
                  onChange={(e) => setForm((f) => ({ ...f, website: e.target.value }))}
                />
              </label>
              <label className="block text-xs text-gray-400">
                Buyer Type
                <input
                  className="mt-1 w-full rounded border border-gray-600 bg-gray-800 px-3 py-2 text-white"
                  placeholder="e.g. Airline, FBO, Cargo"
                  value={String(form.buyerType ?? '')}
                  onChange={(e) => setForm((f) => ({ ...f, buyerType: e.target.value }))}
                />
              </label>
              <label className="block text-xs text-gray-400">
                Fuel type
                <select
                  className="mt-1 w-full rounded border border-gray-600 bg-gray-800 px-3 py-2 text-white"
                  value={String(form.fuelType ?? 'Conventional')}
                  onChange={(e) => setForm((f) => ({ ...f, fuelType: e.target.value }))}
                >
                  {JETA_FUEL_TYPES.map((ft) => (
                    <option key={ft} value={ft}>
                      {ft}
                    </option>
                  ))}
                </select>
              </label>
              <label className="block text-xs text-gray-400">
                Pipeline Stage
                <select
                  className="mt-1 w-full rounded border border-gray-600 bg-gray-800 px-3 py-2 text-white"
                  value={Number(form.pipelineStage)}
                  onChange={(e) => setForm((f) => ({ ...f, pipelineStage: parseInt(e.target.value, 10) }))}
                >
                  {JETA_STAGE_LABELS.map((lab, i) => (
                    <option key={lab} value={i + 1}>
                      {i + 1} {lab}
                    </option>
                  ))}
                </select>
              </label>
              <label className="block text-xs text-gray-400">
                Last Contact Date
                <input
                  type="date"
                  className="mt-1 w-full rounded border border-gray-600 bg-gray-800 px-3 py-2 text-white"
                  value={String(form.lastContactDate ?? '').slice(0, 10)}
                  onChange={(e) => setForm((f) => ({ ...f, lastContactDate: e.target.value }))}
                />
              </label>
              <label className="block text-xs text-gray-400">
                Next Action
                <textarea
                  className="mt-1 w-full rounded border border-gray-600 bg-gray-800 px-3 py-2 text-white"
                  rows={2}
                  value={String(form.nextAction ?? '')}
                  onChange={(e) => setForm((f) => ({ ...f, nextAction: e.target.value }))}
                />
              </label>
              <label className="block text-xs text-gray-400">
                Notes
                <textarea
                  className="mt-1 w-full rounded border border-gray-600 bg-gray-800 px-3 py-2 text-white"
                  rows={3}
                  value={String(form.notes ?? '')}
                  onChange={(e) => setForm((f) => ({ ...f, notes: e.target.value }))}
                />
              </label>
            </div>
            <div className="mt-6 flex justify-end gap-2">
              <button
                type="button"
                onClick={() => setModalOpen(false)}
                className="rounded-lg px-4 py-2 text-sm text-gray-300 hover:bg-gray-800"
              >
                Cancel
              </button>
              <button
                type="button"
                disabled={saving}
                onClick={saveModal}
                className="rounded-lg bg-amber-600 px-4 py-2 text-sm font-semibold text-white hover:bg-amber-500 disabled:opacity-50"
              >
                {saving ? 'Saving…' : 'Save'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default BuyerPipelineTab;
