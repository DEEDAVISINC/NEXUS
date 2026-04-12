import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { api } from '../../../api/client';
import type { JetaBuyer } from './BuyerPipelineTab';
import { JETA_FUEL_TYPES, normalizeJetaFuelType } from './BuyerPipelineTab';

/** Matches api_server JETA_DEAL_STAGES */
export const JETA_DEAL_STAGES = [
  'Qualifying',
  'Supply Sourcing',
  'NCNDA Pending',
  'NCNDA Signed',
  'Docs Exchanged',
  'IMFPA Executed',
  'Closed Won',
  'Closed Lost',
] as const;

export interface JetaDealIntegrity {
  blacklist_critical?: boolean;
  blacklist_findings?: { code?: string; message?: string }[];
  warning_messages?: string[];
}

export interface JetaDeal {
  id: string;
  buyerId: string;
  buyerName: string;
  companyName: string;
  contactName: string;
  dealName: string;
  /** Airtable: Deal Description — used for JETA document generation */
  dealDescription?: string;
  dealStage: string;
  supplySource: string;
  volumeGallons: number;
  pricePerGallon: number;
  jetaFeePerGallon: number;
  projectedTotalFee: number;
  ncndaStatus: string;
  imfpaStatus: string;
  feeAgreementStatus: string;
  createdTime?: string;
  /** Airtable: Fuel Type — Conventional | SAF | Both */
  fuelType?: string;
  /** Present when deals are loaded with integrity=1 — terminology blacklist (api_server + jeta_fraud_detection). */
  integrity?: JetaDealIntegrity;
  /** Spot | Term | … — drives Fee Agreement escalation clause (Version B vs A/C). */
  dealType?: string;
  /** e.g. "90 days", "6 months" — term &gt; 90 days selects Version C. */
  termLength?: string;
  /** IATA $/bbl stored when Fee Agreement PDF is generated. */
  escalationBaseBenchmarkBbl?: number | null;
  /** Version A / B / C from last Fee Agreement generation. */
  escalationClauseVersion?: string | null;
}

function fmtMoney(n: number): string {
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 4 }).format(
    Number.isFinite(n) ? n : 0
  );
}

function fmtGallons(n: number): string {
  return `${new Intl.NumberFormat('en-US', { maximumFractionDigits: 0 }).format(Number.isFinite(n) ? n : 0)} gal`;
}

function docBadgeClass(status: string): string {
  const s = (status || '').toLowerCase();
  if (!s) return 'bg-gray-700/80 text-gray-500 ring-1 ring-gray-600';
  if (
    s.includes('sign') ||
    s.includes('execut') ||
    s.includes('complete') ||
    s.includes('done') ||
    s === 'yes'
  ) {
    return 'bg-emerald-950/70 text-emerald-200 ring-1 ring-emerald-700';
  }
  if (s.includes('pend') || s.includes('draft') || s.includes('wait')) {
    return 'bg-amber-950/60 text-amber-200 ring-1 ring-amber-700';
  }
  if (s.includes('lost') || s.includes('void') || s.includes('n/a')) {
    return 'bg-gray-800 text-gray-400 ring-1 ring-gray-600';
  }
  return 'bg-slate-800 text-slate-200 ring-1 ring-slate-600';
}

const DocBadge: React.FC<{ label: string; status: string }> = ({ label, status }) => (
  <span
    title={`${label}: ${status || '—'}`}
    className={`inline-flex max-w-[7rem] truncate rounded px-1.5 py-0.5 text-[10px] font-semibold uppercase tracking-wide ${docBadgeClass(
      status
    )}`}
  >
    {label}: {status || '—'}
  </span>
);

const DealCard: React.FC<{
  deal: JetaDeal;
  stages: readonly string[];
  onStageChange: (dealId: string, stage: string) => void;
  onFuelTypeChange: (dealId: string, fuelType: string) => void;
  updating: boolean;
}> = ({ deal, stages, onStageChange, onFuelTypeChange, updating }) => {
  const title = deal.dealName?.trim() || deal.buyerName || 'Deal';
  const ft = normalizeJetaFuelType(deal.fuelType);
  const crit = deal.integrity?.blacklist_critical;
  const warnings = (deal.integrity?.warning_messages || []).filter(Boolean).slice(0, 3);
  return (
    <div className="rounded-lg border border-gray-600 bg-gray-900/90 p-3 shadow-sm ring-1 ring-black/20">
      {crit ? (
        <div className="mb-2 rounded border border-red-800 bg-red-950/70 px-2 py-2 text-[10px] leading-snug text-red-100">
          <span className="font-bold uppercase tracking-wide text-red-300">Critical — terminology</span>
          <p className="mt-1 text-red-100/95">Blocked term(s) detected on deal or counterparty text. Review before proceeding.</p>
          {warnings.length > 0 ? (
            <ul className="mt-1 list-inside list-disc text-red-200/90">
              {warnings.map((w, i) => (
                <li key={i}>{w}</li>
              ))}
            </ul>
          ) : null}
        </div>
      ) : null}
      <div className="flex items-start justify-between gap-2">
        <div className="min-w-0">
          <p className="truncate text-sm font-semibold text-white">{title}</p>
          {deal.dealName?.trim() ? (
            <p className="truncate text-xs text-gray-400">{deal.buyerName || '—'}</p>
          ) : null}
        </div>
        {ft === 'SAF' || ft === 'Both' ? (
          <span className="shrink-0 rounded bg-emerald-900/80 px-1.5 py-0.5 text-[10px] font-bold text-emerald-200 ring-1 ring-emerald-700/60">
            SAF
          </span>
        ) : null}
      </div>
      <p className="mt-2 text-xs text-gray-500">Supply</p>
      <p className="text-sm text-gray-300">{deal.supplySource?.trim() || '—'}</p>
      <dl className="mt-2 grid grid-cols-2 gap-x-2 gap-y-1 text-xs">
        <dt className="text-gray-500">Volume</dt>
        <dd className="text-right text-gray-200">{fmtGallons(deal.volumeGallons)}</dd>
        <dt className="text-gray-500">$/gal</dt>
        <dd className="text-right text-gray-200">{fmtMoney(deal.pricePerGallon)}</dd>
        <dt className="text-gray-500">JETA fee/gal</dt>
        <dd className="text-right text-amber-200/90">{fmtMoney(deal.jetaFeePerGallon)}</dd>
        <dt className="text-gray-500">Proj. fee</dt>
        <dd className="text-right font-semibold text-amber-300">{fmtMoney(deal.projectedTotalFee)}</dd>
      </dl>
      <div className="mt-2 flex flex-wrap gap-1">
        <DocBadge label="NCNDA" status={deal.ncndaStatus} />
        <DocBadge label="IMFPA" status={deal.imfpaStatus} />
        <DocBadge label="Fee agr." status={deal.feeAgreementStatus} />
      </div>
      <label className="mt-3 block text-[10px] uppercase tracking-wide text-gray-500">
        Stage
        <select
          disabled={updating}
          value={deal.dealStage}
          onChange={(e) => onStageChange(deal.id, e.target.value)}
          className="mt-0.5 w-full rounded border border-gray-600 bg-gray-800 px-2 py-1.5 text-xs text-white"
        >
          {stages.map((s) => (
            <option key={s} value={s}>
              {s}
            </option>
          ))}
        </select>
      </label>
      <label className="mt-2 block text-[10px] uppercase tracking-wide text-gray-500">
        Fuel type
        <select
          disabled={updating}
          value={ft}
          onChange={(e) => onFuelTypeChange(deal.id, e.target.value)}
          className="mt-0.5 w-full rounded border border-gray-600 bg-gray-800 px-2 py-1.5 text-xs text-white"
        >
          {JETA_FUEL_TYPES.map((x) => (
            <option key={x} value={x}>
              {x}
            </option>
          ))}
        </select>
      </label>
    </div>
  );
};

const FeeCalculatorPanel: React.FC = () => {
  const [volume, setVolume] = useState('');
  const [pricePerGal, setPricePerGal] = useState('');
  const [jetaFeePerGal, setJetaFeePerGal] = useState('');
  const [brokers, setBrokers] = useState('1');
  const [imfpaApplies, setImfpaApplies] = useState(false);

  const v = parseFloat(volume.replace(/,/g, '')) || 0;
  const ppg = parseFloat(pricePerGal) || 0;
  const jfg = parseFloat(jetaFeePerGal) || 0;
  const nBrokers = Math.max(1, Math.min(99, parseInt(brokers, 10) || 1));
  const jetaTotalFee = v * jfg;
  const grossValue = v * ppg;
  const perBrokerSplit = imfpaApplies && nBrokers >= 1 ? jetaTotalFee / nBrokers : null;

  return (
    <div className="rounded-xl border border-amber-900/40 bg-gradient-to-b from-amber-950/30 to-gray-900/90 p-4 shadow-lg">
      <h4 className="text-sm font-bold uppercase tracking-wide text-amber-200/95">Fee calculator</h4>
      <p className="mt-1 text-xs text-gray-500">Estimates JETA fee, gross deal value, and optional IMFPA broker split.</p>
      <div className="mt-4 space-y-3">
        <label className="block text-xs text-gray-400">
          Volume (gallons)
          <input
            type="text"
            inputMode="decimal"
            value={volume}
            onChange={(e) => setVolume(e.target.value)}
            className="mt-1 w-full rounded-lg border border-gray-600 bg-gray-800 px-3 py-2 text-sm text-white"
            placeholder="0"
          />
        </label>
        <label className="block text-xs text-gray-400">
          Price per gallon ($)
          <input
            type="text"
            inputMode="decimal"
            value={pricePerGal}
            onChange={(e) => setPricePerGal(e.target.value)}
            className="mt-1 w-full rounded-lg border border-gray-600 bg-gray-800 px-3 py-2 text-sm text-white"
            placeholder="0.00"
          />
        </label>
        <label className="block text-xs text-gray-400">
          JETA fee per gallon ($)
          <input
            type="text"
            inputMode="decimal"
            value={jetaFeePerGal}
            onChange={(e) => setJetaFeePerGal(e.target.value)}
            className="mt-1 w-full rounded-lg border border-gray-600 bg-gray-800 px-3 py-2 text-sm text-white"
            placeholder="0.00"
          />
        </label>
        <label className="block text-xs text-gray-400">
          Brokers in chain
          <input
            type="number"
            min={1}
            max={99}
            value={brokers}
            onChange={(e) => setBrokers(e.target.value)}
            className="mt-1 w-full rounded-lg border border-gray-600 bg-gray-800 px-3 py-2 text-sm text-white"
          />
        </label>
        <label className="flex cursor-pointer items-center gap-2 text-xs text-gray-300">
          <input
            type="checkbox"
            checked={imfpaApplies}
            onChange={(e) => setImfpaApplies(e.target.checked)}
            className="rounded border-gray-600 bg-gray-800 text-amber-600 focus:ring-amber-500"
          />
          IMFPA applies (show per-broker split)
        </label>
      </div>
      <dl className="mt-4 space-y-2 border-t border-gray-700 pt-4 text-sm">
        <div className="flex justify-between gap-2">
          <dt className="text-gray-500">JETA total fee</dt>
          <dd className="font-semibold text-amber-300">{fmtMoney(jetaTotalFee)}</dd>
        </div>
        <div className="flex justify-between gap-2">
          <dt className="text-gray-500">Deal gross value</dt>
          <dd className="font-semibold text-white">{fmtMoney(grossValue)}</dd>
        </div>
        {imfpaApplies && perBrokerSplit !== null && (
          <div className="flex justify-between gap-2">
            <dt className="text-gray-500">Per-broker split ({nBrokers})</dt>
            <dd className="font-semibold text-violet-300">{fmtMoney(perBrokerSplit)}</dd>
          </div>
        )}
      </dl>
    </div>
  );
};

const DealManagerTab: React.FC = () => {
  const [deals, setDeals] = useState<JetaDeal[]>([]);
  const [stages, setStages] = useState<string[]>([...JETA_DEAL_STAGES]);
  const [buyers, setBuyers] = useState<JetaBuyer[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [hint, setHint] = useState<string | null>(null);
  const [view, setView] = useState<'board' | 'table'>('board');
  const [updatingId, setUpdatingId] = useState<string | null>(null);

  const [modalOpen, setModalOpen] = useState(false);
  const [newBuyerId, setNewBuyerId] = useState('');
  const [newDealName, setNewDealName] = useState('');
  const [newStage, setNewStage] = useState<string>(JETA_DEAL_STAGES[0]);
  const [newDealFuelType, setNewDealFuelType] = useState<string>('Conventional');
  const [fuelFilter, setFuelFilter] = useState<'all' | 'conventional' | 'saf'>('all');
  const [saving, setSaving] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    setHint(null);
    try {
      const res = (await api.getJetaDeals({ integrity: true })) as {
        success?: boolean;
        deals?: JetaDeal[];
        stages?: string[];
        error?: string;
        hint?: string;
      };
      if (res.hint) setHint(res.hint);
      if (res.success === false && res.error) setError(res.error);
      else {
        setDeals(res.deals || []);
        if (res.stages?.length) setStages(res.stages);
      }
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Failed to load deals');
      setDeals([]);
    } finally {
      setLoading(false);
    }
  }, []);

  const loadBuyers = useCallback(async () => {
    try {
      const res = (await api.getJetaBuyers({})) as { buyers?: JetaBuyer[] };
      setBuyers(res.buyers || []);
    } catch {
      setBuyers([]);
    }
  }, []);

  useEffect(() => {
    load();
    loadBuyers();
  }, [load, loadBuyers]);

  const filteredDeals = useMemo(() => {
    return deals.filter((d) => {
      const ft = normalizeJetaFuelType(d.fuelType);
      if (fuelFilter === 'all') return true;
      if (fuelFilter === 'conventional') return ft === 'Conventional' || ft === 'Both';
      if (fuelFilter === 'saf') return ft === 'SAF' || ft === 'Both';
      return true;
    });
  }, [deals, fuelFilter]);

  const grouped = useMemo(() => {
    const g: Record<string, JetaDeal[]> = {};
    stages.forEach((s) => {
      g[s] = [];
    });
    filteredDeals.forEach((d) => {
      const s = stages.includes(d.dealStage) ? d.dealStage : stages[0];
      if (!g[s]) g[s] = [];
      g[s].push(d);
    });
    return g;
  }, [filteredDeals, stages]);

  const changeStage = async (dealId: string, dealStage: string) => {
    setUpdatingId(dealId);
    try {
      const res = (await api.updateJetaDeal(dealId, { dealStage })) as { success?: boolean; error?: string };
      if (res.success === false) {
        alert(res.error || 'Update failed');
        return;
      }
      await load();
    } catch (e: unknown) {
      alert(e instanceof Error ? e.message : 'Update failed');
    } finally {
      setUpdatingId(null);
    }
  };

  const changeFuelType = async (dealId: string, fuelType: string) => {
    setUpdatingId(dealId);
    try {
      const res = (await api.updateJetaDeal(dealId, { fuelType })) as { success?: boolean; error?: string };
      if (res.success === false) {
        alert(res.error || 'Update failed');
        return;
      }
      await load();
    } catch (e: unknown) {
      alert(e instanceof Error ? e.message : 'Update failed');
    } finally {
      setUpdatingId(null);
    }
  };

  const openNewDeal = () => {
    setNewBuyerId(buyers[0]?.id || '');
    setNewDealName('');
    setNewStage(JETA_DEAL_STAGES[0]);
    setNewDealFuelType('Conventional');
    setModalOpen(true);
  };

  const saveNewDeal = async () => {
    if (!newBuyerId) {
      alert('Select a buyer.');
      return;
    }
    setSaving(true);
    try {
      const res = (await api.createJetaDeal({
        buyerId: newBuyerId,
        dealName: newDealName.trim(),
        dealStage: newStage,
        fuelType: newDealFuelType,
      })) as { success?: boolean; error?: string };
      if (res.success === false) {
        alert(res.error || 'Create failed');
        return;
      }
      setModalOpen(false);
      await load();
    } catch (e: unknown) {
      alert(e instanceof Error ? e.message : 'Create failed');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="relative min-h-[420px]">
      <div className="mb-6 flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div>
          <h3 className="text-xl font-bold text-white">Deal Manager</h3>
          <p className="text-sm text-gray-400">Airtable · JETA_Deals · JETA_Buyers</p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <div
            className="flex rounded-lg border border-gray-600 p-0.5"
            title="Deals with “Both” appear in Conventional and SAF"
          >
            <button
              type="button"
              onClick={() => setFuelFilter('all')}
              className={`rounded-md px-2.5 py-1.5 text-xs font-semibold ${
                fuelFilter === 'all' ? 'bg-emerald-700 text-white' : 'text-gray-400 hover:text-white'
              }`}
            >
              All deals
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
          <div className="flex rounded-lg border border-gray-600 p-0.5">
            <button
              type="button"
              onClick={() => setView('board')}
              className={`rounded-md px-3 py-1.5 text-xs font-semibold ${
                view === 'board' ? 'bg-amber-600 text-white' : 'text-gray-400 hover:text-white'
              }`}
            >
              Board
            </button>
            <button
              type="button"
              onClick={() => setView('table')}
              className={`rounded-md px-3 py-1.5 text-xs font-semibold ${
                view === 'table' ? 'bg-amber-600 text-white' : 'text-gray-400 hover:text-white'
              }`}
            >
              Table
            </button>
          </div>
          <button
            type="button"
            onClick={openNewDeal}
            className="rounded-lg bg-gradient-to-r from-amber-600 to-orange-600 px-4 py-2 text-sm font-semibold text-white shadow hover:from-amber-500 hover:to-orange-500"
          >
            + New deal
          </button>
        </div>
      </div>

      {(error || hint) && (
        <div className="mb-4 rounded-lg border border-amber-700/50 bg-amber-950/40 px-4 py-3 text-sm text-amber-100">
          {error && <p className="font-medium text-amber-200">Error: {error}</p>}
          {hint && <p className="mt-1 text-amber-100/90">{hint}</p>}
        </div>
      )}

      <div className="flex flex-col gap-8 lg:flex-row lg:items-start">
        <div className="min-w-0 flex-1 space-y-4">
          {loading ? (
            <div className="py-20 text-center text-gray-400">Loading deals…</div>
          ) : view === 'board' ? (
            <div className="flex gap-3 overflow-x-auto pb-4">
              {stages.map((stage) => (
                <div key={stage} className="w-72 shrink-0">
                  <div className="mb-2 flex items-baseline justify-between gap-2">
                    <h4 className="text-xs font-bold uppercase tracking-wide text-amber-200/80">{stage}</h4>
                    <span className="text-[10px] text-gray-500">{(grouped[stage] || []).length}</span>
                  </div>
                  <div className="min-h-[120px] space-y-2 rounded-lg border border-gray-700/80 bg-gray-900/40 p-2">
                    {(grouped[stage] || []).length === 0 ? (
                      <p className="py-6 text-center text-xs text-gray-600">No deals</p>
                    ) : (
                      (grouped[stage] || []).map((d) => (
                        <DealCard
                          key={d.id}
                          deal={d}
                          stages={stages}
                          onStageChange={(id, s) => changeStage(id, s)}
                          onFuelTypeChange={(id, ft) => changeFuelType(id, ft)}
                          updating={updatingId === d.id}
                        />
                      ))
                    )}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="overflow-x-auto rounded-xl border border-gray-700">
              <table className="min-w-full divide-y divide-gray-700 text-left text-sm">
                <thead className="bg-gray-800/80">
                  <tr>
                    <th className="px-3 py-3 font-semibold text-gray-300">Deal / Buyer</th>
                    <th className="px-3 py-3 font-semibold text-gray-300">Fuel</th>
                    <th className="px-3 py-3 font-semibold text-gray-300">Stage</th>
                    <th className="px-3 py-3 font-semibold text-gray-300">Supply</th>
                    <th className="px-3 py-3 font-semibold text-gray-300">Volume</th>
                    <th className="px-3 py-3 font-semibold text-gray-300">$/gal</th>
                    <th className="px-3 py-3 font-semibold text-gray-300">JETA fee/gal</th>
                    <th className="px-3 py-3 font-semibold text-gray-300">Proj. fee</th>
                    <th className="px-3 py-3 font-semibold text-gray-300">Docs</th>
                    <th className="px-3 py-3 font-semibold text-gray-300">Integrity</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-700/80">
                  {filteredDeals.length === 0 ? (
                    <tr>
                      <td colSpan={10} className="px-4 py-12 text-center text-gray-500">
                        {deals.length === 0 ? (
                          <>
                            No deals yet. Create one with <strong>New deal</strong>.
                          </>
                        ) : (
                          <>No deals match this fuel filter.</>
                        )}
                      </td>
                    </tr>
                  ) : (
                    filteredDeals.map((d) => (
                      <tr key={d.id} className="bg-gray-900/40">
                        <td className="px-3 py-3">
                          <div className="font-medium text-white">{d.dealName?.trim() || d.buyerName || '—'}</div>
                          {d.dealName?.trim() ? (
                            <div className="text-xs text-gray-500">{d.buyerName}</div>
                          ) : null}
                        </td>
                        <td className="whitespace-nowrap px-3 py-3">
                          <select
                            value={normalizeJetaFuelType(d.fuelType)}
                            disabled={updatingId === d.id}
                            onChange={(e) => changeFuelType(d.id, e.target.value)}
                            className="rounded border border-gray-600 bg-gray-800 px-2 py-1 text-xs text-white"
                          >
                            {JETA_FUEL_TYPES.map((ft) => (
                              <option key={ft} value={ft}>
                                {ft}
                              </option>
                            ))}
                          </select>
                        </td>
                        <td className="whitespace-nowrap px-3 py-3">
                          <select
                            value={d.dealStage}
                            disabled={updatingId === d.id}
                            onChange={(e) => changeStage(d.id, e.target.value)}
                            className="rounded border border-gray-600 bg-gray-800 px-2 py-1 text-xs text-white"
                          >
                            {stages.map((s) => (
                              <option key={s} value={s}>
                                {s}
                              </option>
                            ))}
                          </select>
                        </td>
                        <td className="max-w-[140px] truncate px-3 py-3 text-gray-400">{d.supplySource || '—'}</td>
                        <td className="whitespace-nowrap px-3 py-3 text-gray-300">{fmtGallons(d.volumeGallons)}</td>
                        <td className="whitespace-nowrap px-3 py-3 text-gray-300">{fmtMoney(d.pricePerGallon)}</td>
                        <td className="whitespace-nowrap px-3 py-3 text-amber-200/90">{fmtMoney(d.jetaFeePerGallon)}</td>
                        <td className="whitespace-nowrap px-3 py-3 font-semibold text-amber-300">
                          {fmtMoney(d.projectedTotalFee)}
                        </td>
                        <td className="px-3 py-3">
                          <div className="flex flex-wrap gap-1">
                            <DocBadge label="N" status={d.ncndaStatus} />
                            <DocBadge label="I" status={d.imfpaStatus} />
                            <DocBadge label="F" status={d.feeAgreementStatus} />
                          </div>
                        </td>
                        <td className="px-3 py-3 text-xs">
                          {d.integrity?.blacklist_critical ? (
                            <span className="rounded bg-red-950/80 px-1.5 py-0.5 font-semibold text-red-200 ring-1 ring-red-800">
                              CRITICAL
                            </span>
                          ) : (
                            <span className="text-gray-600">—</span>
                          )}
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          )}
        </div>

        <aside className="w-full shrink-0 lg:sticky lg:top-4 lg:w-80">
          <FeeCalculatorPanel />
        </aside>
      </div>

      {modalOpen && (
        <>
          <button
            type="button"
            className="fixed inset-0 z-40 bg-black/60"
            aria-label="Close"
            onClick={() => setModalOpen(false)}
          />
          <div className="fixed left-1/2 top-1/2 z-50 w-full max-w-md -translate-x-1/2 -translate-y-1/2 rounded-xl border border-amber-900/50 bg-gray-900 p-6 shadow-xl">
            <h4 className="text-lg font-bold text-white">New deal</h4>
            <p className="mt-1 text-xs text-gray-500">Creates a row in JETA_Deals linked to a buyer.</p>
            <div className="mt-4 space-y-3">
              <label className="block text-sm text-gray-300">
                Buyer <span className="text-red-400">*</span>
                <select
                  value={newBuyerId}
                  onChange={(e) => setNewBuyerId(e.target.value)}
                  className="mt-1 w-full rounded-lg border border-gray-600 bg-gray-800 px-3 py-2 text-white"
                >
                  <option value="">Select buyer…</option>
                  {buyers.map((b) => (
                    <option key={b.id} value={b.id}>
                      {b.companyName || 'Company'} — {b.contactName || 'Contact'}
                    </option>
                  ))}
                </select>
              </label>
              <label className="block text-sm text-gray-300">
                Deal name <span className="text-gray-500">(optional)</span>
                <input
                  type="text"
                  value={newDealName}
                  onChange={(e) => setNewDealName(e.target.value)}
                  className="mt-1 w-full rounded-lg border border-gray-600 bg-gray-800 px-3 py-2 text-white"
                  placeholder="e.g. DTW charter — Q2"
                />
              </label>
              <label className="block text-sm text-gray-300">
                Initial stage
                <select
                  value={newStage}
                  onChange={(e) => setNewStage(e.target.value)}
                  className="mt-1 w-full rounded-lg border border-gray-600 bg-gray-800 px-3 py-2 text-white"
                >
                  {JETA_DEAL_STAGES.map((s) => (
                    <option key={s} value={s}>
                      {s}
                    </option>
                  ))}
                </select>
              </label>
              <label className="block text-sm text-gray-300">
                Fuel type
                <select
                  value={newDealFuelType}
                  onChange={(e) => setNewDealFuelType(e.target.value)}
                  className="mt-1 w-full rounded-lg border border-gray-600 bg-gray-800 px-3 py-2 text-white"
                >
                  {JETA_FUEL_TYPES.map((ft) => (
                    <option key={ft} value={ft}>
                      {ft}
                    </option>
                  ))}
                </select>
              </label>
            </div>
            <div className="mt-6 flex justify-end gap-2">
              <button
                type="button"
                onClick={() => setModalOpen(false)}
                className="rounded-lg px-4 py-2 text-sm text-gray-400 hover:text-white"
              >
                Cancel
              </button>
              <button
                type="button"
                disabled={saving}
                onClick={saveNewDeal}
                className="rounded-lg bg-gradient-to-r from-amber-600 to-orange-600 px-4 py-2 text-sm font-semibold text-white disabled:opacity-50"
              >
                {saving ? 'Saving…' : 'Create deal'}
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default DealManagerTab;
