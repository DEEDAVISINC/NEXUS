import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { api } from '../../../api/client';
import { JETA_STAGE_LABELS, normalizeJetaFuelType, PriorityScoreBar } from './BuyerPipelineTab';
import type { JetaBuyer } from './BuyerPipelineTab';
import type { JetaDeal } from './DealManagerTab';
import type { JetaDueBuyer, JetaOutreachRow } from './OutreachCenterTab';

const CLOSED_DEAL_STAGES = new Set(['Closed Won', 'Closed Lost']);

function isActiveDeal(d: JetaDeal): boolean {
  return !CLOSED_DEAL_STAGES.has(d.dealStage);
}

function parseDay(s: string | undefined): Date | null {
  if (!s || typeof s !== 'string') return null;
  const m = s.match(/^(\d{4})-(\d{2})-(\d{2})/);
  if (!m) return null;
  const d = new Date(Number(m[1]), Number(m[2]) - 1, Number(m[3]));
  return Number.isNaN(d.getTime()) ? null : d;
}

function startOfToday(): Date {
  const t = new Date();
  return new Date(t.getFullYear(), t.getMonth(), t.getDate());
}

function daysBetween(a: Date, b: Date): number {
  return Math.round((b.getTime() - a.getTime()) / (24 * 60 * 60 * 1000));
}

function fmtMoney(n: number): string {
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(
    Number.isFinite(n) ? n : 0
  );
}

function fmtUsdPerBbl(n: number | undefined): string {
  if (n == null || !Number.isFinite(n)) return '—';
  return (
    new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 2 }).format(n) + '/bbl'
  );
}

/** Currency per barrel (WTI/Brent, crack, war premium) — same formatting, explicit /bbl suffix. */
function fmtMoneyPerBbl(n: number | undefined | null): string {
  if (n == null || !Number.isFinite(n)) return '—';
  return (
    new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 2 }).format(n) + '/bbl'
  );
}

export interface DashboardTabProps {
  setActiveTab?: (tab: string) => void;
}

type EscalationPriceAlert = {
  triggered?: boolean;
  affected_count?: number;
  affected_deals?: { deal_id: string; deal_name: string; clause_version?: string }[];
  message?: string;
};

/** Latest row from GET /jeta/market/price — see serialize_market_row (backend). */
type JetaMarketLatestRow = {
  pricePerBarrel?: number;
  priceDate?: string;
  source?: string;
  geopoliticalRiskLevel?: string | null;
  activeConflictRegions?: string[];
  chokepointStatus?: {
    hormuz?: string | null;
    suez?: string | null;
    bosphorus?: string | null;
    southChinaSea?: string | null;
  };
  priceDrivers?: string[];
  crudeOilPriceBbl?: number | null;
  jetCrackSpread?: number | null;
  priceTrend?: string | null;
  forecast30Day?: string | null;
  warPremiumEstimated?: number | null;
  supplyDisruptionAlert?: boolean;
  escalationClauseTriggered?: boolean;
  marketNotes?: string | null;
  analystSource?: string | null;
};

const DashboardTab: React.FC<DashboardTabProps> = ({ setActiveTab }) => {
  const [buyers, setBuyers] = useState<JetaBuyer[]>([]);
  const [deals, setDeals] = useState<JetaDeal[]>([]);
  const [outreach, setOutreach] = useState<JetaOutreachRow[]>([]);
  const [dueBuyers, setDueBuyers] = useState<JetaDueBuyer[]>([]);
  const [dealAlerts, setDealAlerts] = useState<
    {
      type?: string;
      severity?: string;
      message?: string;
      deal_name?: string;
      company_name?: string;
      stage?: string;
      buyer_name?: string;
    }[]
  >([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [marketSnapshot, setMarketSnapshot] = useState<{
    latest?: JetaMarketLatestRow | null;
    previous?: { pricePerBarrel?: number; priceDate?: string } | null;
    weekOverWeekChangePct?: number | null;
    weekOverWeekChangeAbs?: number | null;
    sourceLabel?: string;
    hint?: string;
    escalationPriceAlert?: EscalationPriceAlert | null;
  } | null>(null);

  const [aiModalOpen, setAiModalOpen] = useState(false);
  const [aiDraftBody, setAiDraftBody] = useState('');
  const [aiSubject, setAiSubject] = useState('JETA COURTIÈRE — Jet-A supply / quick introduction');
  const [aiError, setAiError] = useState<string | null>(null);
  const [aiLoadingId, setAiLoadingId] = useState<string | null>(null);
  const [aiTouchNumber, setAiTouchNumber] = useState(1);
  const [aiTargetBuyer, setAiTargetBuyer] = useState<JetaBuyer | null>(null);

  const [noticeModalOpen, setNoticeModalOpen] = useState(false);
  const [noticeLoading, setNoticeLoading] = useState(false);
  const [noticeError, setNoticeError] = useState<string | null>(null);
  const [noticeDisclaimer, setNoticeDisclaimer] = useState<string | null>(null);
  const [noticeInfo, setNoticeInfo] = useState<string | null>(null);
  const [noticeDrafts, setNoticeDrafts] = useState<
    { deal_id?: string; subject?: string; body?: string; buyer_email?: string }[]
  >([]);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [bRes, dRes, oRes, dueRes, alertRes, mRes] = await Promise.all([
        api.getJetaBuyers({}) as Promise<{
          success?: boolean;
          buyers?: JetaBuyer[];
          error?: string;
        }>,
        api.getJetaDeals() as Promise<{ success?: boolean; deals?: JetaDeal[]; error?: string }>,
        api.getJetaOutreach({ sort: 'touch_date_desc' }) as Promise<{
          success?: boolean;
          outreach?: JetaOutreachRow[];
          error?: string;
        }>,
        api.getJetaOutreachDueBuyers() as Promise<{
          success?: boolean;
          buyers?: JetaDueBuyer[];
          error?: string;
        }>,
        api.getJetaFraudDashboardAlerts() as Promise<{
          success?: boolean;
          alerts?: typeof dealAlerts;
          alert_count?: number;
          error?: string;
        }>,
        api.getJetaMarketPrice() as Promise<{
          success?: boolean;
          latest?: JetaMarketLatestRow | null;
          previous?: { pricePerBarrel?: number; priceDate?: string } | null;
          weekOverWeekChangePct?: number | null;
          weekOverWeekChangeAbs?: number | null;
          sourceLabel?: string;
          hint?: string;
          error?: string;
          escalationPriceAlert?: EscalationPriceAlert | null;
        }>,
      ]);
      if (bRes.success === false && bRes.error) setError(bRes.error);
      if (dRes.success === false && dRes.error) setError(dRes.error);
      if (oRes.success === false && oRes.error) setError(oRes.error);
      if (dueRes.success === false && dueRes.error) setError(dueRes.error);
      if (alertRes.success === false && alertRes.error) setError(alertRes.error);
      if (mRes.success === false && mRes.error) setError(mRes.error);
      setBuyers(bRes.buyers || []);
      setDeals(dRes.deals || []);
      setOutreach(oRes.outreach || []);
      setDueBuyers(dueRes.buyers || []);
      setDealAlerts(alertRes.alerts || []);
      if (mRes.success !== false) {
        setMarketSnapshot({
          latest: mRes.latest,
          previous: mRes.previous,
          weekOverWeekChangePct: mRes.weekOverWeekChangePct,
          weekOverWeekChangeAbs: mRes.weekOverWeekChangeAbs,
          sourceLabel: mRes.sourceLabel,
          hint: mRes.hint,
          escalationPriceAlert: mRes.escalationPriceAlert,
        });
      } else {
        setMarketSnapshot(null);
      }
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Failed to load dashboard');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const metrics = useMemo(() => {
    const totalBuyers = buyers.length;
    const activeDealsList = deals.filter(isActiveDeal);
    const activeDeals = activeDealsList.length;
    const projectedFees = activeDealsList.reduce((sum, d) => sum + (Number(d.projectedTotalFee) || 0), 0);
    const outreachDueToday = dueBuyers.length;
    return { totalBuyers, activeDeals, projectedFees, outreachDueToday };
  }, [buyers, deals, dueBuyers]);

  const nextTouchForBuyer = useCallback(
    (buyerId: string) => {
      const nums = outreach.filter((r) => r.buyerId === buyerId).map((r) => r.touchNumber || 0);
      return nums.length ? Math.max(...nums) + 1 : 1;
    },
    [outreach]
  );

  const pipelineIntel = useMemo(() => {
    const scoreOf = (b: JetaBuyer) => Math.round(Number(b.priorityScore) || 0);
    const topProspects = [...buyers].sort((a, b) => scoreOf(b) - scoreOf(a)).slice(0, 10);

    const supplyBuyers = buyers.filter((b) => b.supplyAdjacent === true);
    const supplyByState: Record<string, number> = {};
    for (const b of supplyBuyers) {
      const st = (b.state || '').trim() || '—';
      supplyByState[st] = (supplyByState[st] || 0) + 1;
    }

    const openBuyers = buyers.filter((b) => (b.supplierStatus || '').trim() === 'Open');
    const openByState: Record<string, number> = {};
    for (const b of openBuyers) {
      const st = (b.state || '').trim() || '—';
      openByState[st] = (openByState[st] || 0) + 1;
    }
    const openRanked = Object.entries(openByState).sort((a, b) => b[1] - a[1]);

    const caBuyers = buyers.filter(
      (b) => b.canada === true || (b.country || '').trim().toLowerCase() === 'canada'
    );
    const canadaByProvince: Record<string, number> = {};
    for (const b of caBuyers) {
      const st = (b.state || '').trim() || '—';
      canadaByProvince[st] = (canadaByProvince[st] || 0) + 1;
    }
    const ontarioCorridorCount = canadaByProvince['ON'] ?? 0;

    return {
      topProspects,
      supplyAdjacentCount: supplyBuyers.length,
      supplyByState,
      openRanked,
      openCount: openBuyers.length,
      canadaByProvince,
      canadaTotal: caBuyers.length,
      ontarioCorridorCount,
    };
  }, [buyers]);

  const runDashboardAiDraft = async (buyer: JetaBuyer) => {
    const touchNumber = nextTouchForBuyer(buyer.id);
    setAiLoadingId(buyer.id);
    setAiError(null);
    setAiTargetBuyer(buyer);
    setAiTouchNumber(touchNumber);
    try {
      const res = (await api.postJetaOutreachAiDraft({
        buyerId: buyer.id,
        touchNumber,
        contactName: buyer.contactName,
        companyName: buyer.companyName,
        buyerType: buyer.buyerType,
        airport: buyer.airport,
        state: buyer.state,
      })) as { success?: boolean; draft?: string; error?: string };
      if (res.success === false || !res.draft) {
        setAiError(res.error || 'No draft returned');
        setAiDraftBody('');
        setAiModalOpen(true);
        return;
      }
      setAiDraftBody(res.draft);
      setAiModalOpen(true);
    } catch (e: unknown) {
      setAiError(e instanceof Error ? e.message : 'AI draft failed');
      setAiDraftBody('');
      setAiModalOpen(true);
    } finally {
      setAiLoadingId(null);
    }
  };

  const copyAiDraft = async () => {
    try {
      await navigator.clipboard.writeText(aiDraftBody);
    } catch {
      alert('Could not copy to clipboard.');
    }
  };

  const mailtoDraftHref =
    aiTargetBuyer && aiDraftBody
      ? (() => {
          const to = (aiTargetBuyer.email || '').trim();
          const q = new URLSearchParams();
          if (aiSubject) q.set('subject', aiSubject);
          q.set('body', aiDraftBody);
          const qs = q.toString();
          return to ? `mailto:${encodeURIComponent(to)}?${qs}` : `mailto:?${qs}`;
        })()
      : '';

  const pipelineSplit = useMemo(() => {
    const active = deals.filter(isActiveDeal);
    const sumFees = (list: JetaDeal[]) =>
      list.reduce((sum, d) => sum + (Number(d.projectedTotalFee) || 0), 0);
    const conventionalDeals = active.filter((d) => {
      const ft = normalizeJetaFuelType(d.fuelType);
      return ft === 'Conventional' || ft === 'Both';
    });
    const safDeals = active.filter((d) => {
      const ft = normalizeJetaFuelType(d.fuelType);
      return ft === 'SAF' || ft === 'Both';
    });
    return {
      conventional: { count: conventionalDeals.length, projectedFees: sumFees(conventionalDeals) },
      saf: { count: safDeals.length, projectedFees: sumFees(safDeals) },
    };
  }, [deals]);

  const stageCounts = useMemo(() => {
    const counts: number[] = Array.from({ length: 9 }, () => 0);
    for (const b of buyers) {
      const s = Math.max(1, Math.min(9, Number(b.pipelineStage) || 1));
      counts[s - 1] += 1;
    }
    return counts;
  }, [buyers]);

  const maxStageCount = useMemo(() => Math.max(1, ...stageCounts), [stageCounts]);

  const recentOutreach = useMemo(() => outreach.slice(0, 10), [outreach]);

  const marketIntelBanner = useMemo(() => {
    const latest = marketSnapshot?.latest;
    if (!marketSnapshot) return null;

    const geo = (latest?.geopoliticalRiskLevel || '').trim();
    const supply = latest?.supplyDisruptionAlert === true;
    const cp = latest?.chokepointStatus;

    const cpDefs: { key: keyof NonNullable<JetaMarketLatestRow['chokepointStatus']>; label: string }[] = [
      { key: 'hormuz', label: 'Strait of Hormuz' },
      { key: 'suez', label: 'Suez Canal' },
      { key: 'bosphorus', label: 'Strait of Bosphorus' },
      { key: 'southChinaSea', label: 'South China Sea' },
    ];
    const norm = (s: string | null | undefined) => (s || '').trim().toLowerCase();
    const restrictedNames: string[] = [];
    const closedNames: string[] = [];
    for (const { key, label } of cpDefs) {
      const st = norm(cp?.[key] as string);
      if (st === 'restricted') restrictedNames.push(label);
      if (st === 'closed') closedNames.push(label);
    }

    const escMarket = latest?.escalationClauseTriggered === true;
    const escAlert = marketSnapshot?.escalationPriceAlert;
    const escDealsTriggered = escAlert?.triggered === true;

    const lowCalm = geo === 'Low' && !supply;
    const hiddenBaseline =
      lowCalm &&
      restrictedNames.length === 0 &&
      closedNames.length === 0 &&
      !escMarket &&
      !escDealsTriggered;
    if (hiddenBaseline) return null;

    let tier: 'red' | 'orange' | 'yellow' = 'yellow';
    let title = 'Market intelligence';
    let message = '';
    const detailBits: string[] = [];

    const redReason =
      geo === 'Critical' ||
      closedNames.length > 0 ||
      escMarket ||
      escDealsTriggered;
    const orangeReason = geo === 'High' || restrictedNames.length > 0;

    if (redReason) {
      tier = 'red';
      title = 'CRITICAL — Market event';
      if (geo === 'Critical') detailBits.push('geopolitical risk: Critical');
      closedNames.forEach((n) => detailBits.push(`${n} closed`));
      if (escMarket) detailBits.push('escalation clause trigger (JETA_MarketData)');
      if (escDealsTriggered) detailBits.push(`escalation watch: ${escAlert?.affected_count ?? 0} deal(s)`);
      const detail = detailBits.length ? detailBits.join('; ') : 'multiple risk signals';
      message = `CRITICAL MARKET EVENT: ${detail}. All active deals require immediate review. War surcharge provisions may apply. Contact counterparties within 48 hours.`;
    } else if (orangeReason) {
      tier = 'orange';
      title = 'High risk — Market alert';
      const chokePart =
        restrictedNames.length > 0
          ? `${restrictedNames.join(', ')} restricted`
          : 'elevated geopolitical risk (High)';
      message = `High Risk Alert: ${chokePart}. Jet fuel prices may spike. Escalation clauses active. Spot deal premium fees recommended.`;
    } else if (geo === 'Elevated') {
      tier = 'yellow';
      title = 'Elevated risk';
      message =
        'Market Alert: Elevated geopolitical risk detected. Monitor active deal pricing weekly. Review escalation clause status.';
    } else if (supply) {
      tier = 'yellow';
      title = 'Supply disruption';
      message =
        'Supply disruption alert is active on JETA_MarketData. Monitor chokepoints and active deal pricing weekly.';
    } else {
      return null;
    }

    const iata = latest?.pricePerBarrel;
    const activeList = deals.filter(isActiveDeal);
    const benchVals = activeList
      .map((d) => d.escalationBaseBenchmarkBbl)
      .filter((n): n is number => n != null && Number.isFinite(Number(n)))
      .map(Number);
    const avgBench =
      benchVals.length > 0 ? benchVals.reduce((a, b) => a + b, 0) / benchVals.length : null;
    const affectedCount = activeList.length;
    const escWatchCount = escAlert?.affected_count ?? 0;

    return {
      tier,
      title,
      message,
      iata,
      avgBench,
      affectedCount,
      escWatchCount,
    };
  }, [marketSnapshot, deals]);

  const dealsNeedingAttention = useMemo(() => {
    const today = startOfToday();

    const lastTouchByBuyer = new Map<string, Date>();
    for (const row of outreach) {
      const bid = row.buyerId;
      if (!bid) continue;
      const td = parseDay(row.touchDate);
      if (!td) continue;
      const prev = lastTouchByBuyer.get(bid);
      if (!prev || td > prev) lastTouchByBuyer.set(bid, td);
    }

    const lastContactByBuyer = new Map<string, Date>();
    for (const b of buyers) {
      const lcd = parseDay(b.lastContactDate);
      if (lcd) lastContactByBuyer.set(b.id, lcd);
    }

    function lastActivityForDeal(deal: JetaDeal): Date | null {
      const bid = deal.buyerId;
      if (!bid) return null;
      const t = lastTouchByBuyer.get(bid);
      const c = lastContactByBuyer.get(bid);
      if (t && c) return t > c ? t : c;
      return t || c || null;
    }

    const stale: { deal: JetaDeal; last: Date | null; daysStale: number }[] = [];
    for (const deal of deals.filter(isActiveDeal)) {
      const last = lastActivityForDeal(deal);
      if (!last) {
        stale.push({ deal, last: null, daysStale: 999 });
        continue;
      }
      const daysSince = daysBetween(last, today);
      if (daysSince >= 7) {
        stale.push({ deal, last, daysStale: daysSince });
      }
    }
    stale.sort((a, b) => (b.daysStale || 0) - (a.daysStale || 0));
    return stale.slice(0, 10);
  }, [deals, outreach, buyers]);

  const runEscalationNotices = useCallback(async () => {
    setNoticeLoading(true);
    setNoticeError(null);
    setNoticeInfo(null);
    setNoticeDrafts([]);
    setNoticeDisclaimer(null);
    try {
      const ids =
        marketSnapshot?.escalationPriceAlert?.affected_deals?.map((d) => d.deal_id).filter(Boolean) ?? [];
      const res = (await api.postJetaEscalationNoticeDraft(ids.length > 0 ? { dealIds: ids } : {})) as {
        success?: boolean;
        error?: string;
        drafts?: { deal_id?: string; subject?: string; body?: string; buyer_email?: string }[];
        notice?: string;
        disclaimer?: string;
      };
      if (res.success === false) {
        setNoticeError(res.error || 'Request failed');
        return;
      }
      setNoticeDrafts(res.drafts || []);
      setNoticeDisclaimer(res.disclaimer || null);
      if ((res.drafts || []).length === 0 && res.notice) setNoticeInfo(res.notice);
    } catch (e: unknown) {
      setNoticeError(e instanceof Error ? e.message : 'Failed to generate notices');
    } finally {
      setNoticeLoading(false);
    }
  }, [marketSnapshot?.escalationPriceAlert?.affected_deals]);

  const openEscalationNoticeModal = useCallback(() => {
    setNoticeModalOpen(true);
    void runEscalationNotices();
  }, [runEscalationNotices]);

  return (
    <div className="relative min-h-[420px] space-y-8">
      {marketIntelBanner && !loading ? (
        <section
          role="alert"
          aria-live="polite"
          className={`rounded-xl border px-4 py-4 shadow-lg ring-1 ${
            marketIntelBanner.tier === 'red'
              ? 'border-red-600/70 bg-gradient-to-r from-red-950/80 to-gray-950/90 ring-red-900/40'
              : marketIntelBanner.tier === 'orange'
                ? 'border-orange-600/70 bg-gradient-to-r from-orange-950/75 to-gray-950/90 ring-orange-900/35'
                : 'border-yellow-600/60 bg-gradient-to-r from-yellow-950/50 to-gray-950/90 ring-yellow-900/30'
          }`}
        >
          <div className="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
            <div className="min-w-0 flex-1">
              <p
                className={`text-[10px] font-bold uppercase tracking-widest ${
                  marketIntelBanner.tier === 'red'
                    ? 'text-red-300/95'
                    : marketIntelBanner.tier === 'orange'
                      ? 'text-orange-200/95'
                      : 'text-yellow-200/95'
                }`}
              >
                Market intelligence alert
              </p>
              <p className="mt-1 text-sm font-semibold text-white">{marketIntelBanner.title}</p>
              <p className="mt-2 text-sm leading-relaxed text-gray-100/95">{marketIntelBanner.message}</p>
              <div className="mt-3 flex flex-wrap gap-x-6 gap-y-2 border-t border-white/10 pt-3 text-xs text-gray-300">
                <span>
                  <span className="text-gray-500">IATA (latest)</span>{' '}
                  <span className="font-mono font-semibold text-white">
                    {fmtUsdPerBbl(marketIntelBanner.iata)}
                  </span>
                </span>
                <span>
                  <span className="text-gray-500">Avg. base benchmark</span>{' '}
                  <span className="font-mono font-semibold text-white">
                    {marketIntelBanner.avgBench != null && Number.isFinite(marketIntelBanner.avgBench)
                      ? fmtUsdPerBbl(marketIntelBanner.avgBench)
                      : '—'}
                  </span>
                  <span className="ml-1 text-[10px] text-gray-500">(deals w/ FA)</span>
                </span>
                <span>
                  <span className="text-gray-500">Active deals</span>{' '}
                  <span className="font-semibold text-white">{marketIntelBanner.affectedCount}</span>
                </span>
                {marketIntelBanner.escWatchCount > 0 ? (
                  <span>
                    <span className="text-gray-500">Escalation watchlist</span>{' '}
                    <span className="font-semibold text-amber-200">{marketIntelBanner.escWatchCount}</span>
                  </span>
                ) : null}
              </div>
            </div>
            <div className="flex shrink-0 flex-wrap gap-2 lg:flex-col lg:items-stretch">
              {setActiveTab ? (
                <button
                  type="button"
                  onClick={() => setActiveTab('deal-manager')}
                  className={`rounded-lg px-3 py-2 text-xs font-semibold ${
                    marketIntelBanner.tier === 'red'
                      ? 'bg-red-900/80 text-red-50 hover:bg-red-800/90'
                      : marketIntelBanner.tier === 'orange'
                        ? 'bg-orange-900/75 text-orange-50 hover:bg-orange-800/90'
                        : 'bg-yellow-900/60 text-yellow-50 hover:bg-yellow-800/70'
                  }`}
                >
                  Review all deals
                </button>
              ) : null}
              <button
                type="button"
                onClick={openEscalationNoticeModal}
                className="inline-flex justify-center rounded-lg border border-white/20 bg-black/25 px-3 py-2 text-xs font-semibold text-white hover:bg-black/40"
              >
                Send counterparty notices
              </button>
              <button
                type="button"
                onClick={() => {
                  document.getElementById('jeta-dashboard-market-section')?.scrollIntoView({ behavior: 'smooth' });
                }}
                className="rounded-lg border border-white/20 bg-black/20 px-3 py-2 text-xs font-semibold text-gray-100 hover:bg-black/35"
              >
                Update market notes
              </button>
            </div>
          </div>
          <p className="mt-3 text-[10px] text-gray-500">
            Base benchmarks populate when Fee Agreements are generated. Edit long-form narrative in Airtable →
            JETA_MarketData → market_notes.
          </p>
        </section>
      ) : null}

      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h3 className="text-xl font-bold text-white">Dashboard</h3>
          <p className="text-sm text-gray-400">
            Pipeline KPIs · IATA market price · deal alerts · outreach — module map below
          </p>
        </div>
        <button
          type="button"
          onClick={() => load()}
          className="self-start rounded-lg border border-gray-600 px-3 py-2 text-sm text-gray-300 hover:bg-gray-800"
        >
          Refresh
        </button>
      </div>

      {error && (
        <div className="rounded-lg border border-red-900/50 bg-red-950/30 px-4 py-3 text-sm text-red-200">{error}</div>
      )}

      {/* JETA COURTIÈRE — canonical module hierarchy (reference) */}
      <section className="rounded-xl border border-amber-900/35 bg-gradient-to-br from-amber-950/25 to-gray-900/80 p-4 ring-1 ring-amber-900/20">
        <details className="group">
          <summary className="cursor-pointer list-none text-sm font-semibold text-amber-200/95 [&::-webkit-details-marker]:hidden">
            <span className="inline-flex items-center gap-2">
              <span className="text-amber-400/90">▸</span>
              JETA COURTIÈRE MODULE <span className="font-normal text-gray-500">— structure</span>
            </span>
          </summary>
          <pre className="mt-4 overflow-x-auto rounded-lg border border-gray-700/80 bg-black/40 p-4 text-[11px] leading-relaxed text-gray-300 sm:text-xs">
            {`JETA COURTIÈRE MODULE
│
├── Dashboard
│   ├── IATA Live Price Card (weekly auto-fetch)
│   ├── Conventional Pipeline Summary
│   ├── SAF Pipeline Summary
│   ├── Deal Alerts
│   ├── Outreach Due Today
│   └── Pipeline Intelligence (top prospects, markets, Canada, tier playbook / cadence)
│
├── Buyer Pipeline
│   ├── All buyers by stage
│   ├── Airport Supplier Lookup (IATA Directory)
│   └── SAF/Conventional flag per buyer
│
├── Deal Manager
│   ├── Conventional deals track
│   ├── SAF deals track
│   ├── Market price benchmark (IATA)
│   └── Fee calculator
│
├── Outreach Center
│   ├── AI email drafting
│   └── Touch sequence tracking
│
├── Documents
│   ├── NCNDA (ICC 769 E compliant)
│   ├── IMFPA
│   ├── Fee Agreement
│   └── Supply Agreement (AFSMA aligned)
│
├── Fraud Detection Layer
│   ├── Counterparty scoring
│   ├── Terminology blacklist
│   ├── Stage progression gates
│   └── Supplier directory cross-reference
│
└── Market Intelligence
    ├── IATA Fuel Price Monitor (live)
    ├── IATA Supplier Directory (by ICAO)
    └── SAF Matchmaker link`}
          </pre>
          {setActiveTab ? (
            <p className="mt-3 text-xs text-gray-500">
              Tabs:{' '}
              <button
                type="button"
                onClick={() => setActiveTab('buyer-pipeline')}
                className="text-amber-300/90 underline-offset-2 hover:underline"
              >
                Buyer Pipeline
              </button>
              {' · '}
              <button
                type="button"
                onClick={() => setActiveTab('deal-manager')}
                className="text-amber-300/90 underline-offset-2 hover:underline"
              >
                Deal Manager
              </button>
              {' · '}
              <button
                type="button"
                onClick={() => setActiveTab('outreach-center')}
                className="text-amber-300/90 underline-offset-2 hover:underline"
              >
                Outreach
              </button>
              {' · '}
              <button
                type="button"
                onClick={() => setActiveTab('documents')}
                className="text-amber-300/90 underline-offset-2 hover:underline"
              >
                Documents
              </button>
            </p>
          ) : null}
        </details>
      </section>

      {loading ? (
        <div className="py-24 text-center text-gray-400">Loading dashboard…</div>
      ) : (
        <>
          {/* Metric cards */}
          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            <div className="rounded-xl border border-amber-900/40 bg-gradient-to-br from-amber-950/50 to-gray-900/90 p-5 shadow-lg ring-1 ring-amber-900/20">
              <p className="text-xs font-semibold uppercase tracking-wide text-amber-200/80">Buyers in pipeline</p>
              <p className="mt-2 text-3xl font-bold text-white">{metrics.totalBuyers}</p>
            </div>
            <div className="rounded-xl border border-slate-700 bg-gray-900/90 p-5 shadow-lg ring-1 ring-gray-700/50">
              <p className="text-xs font-semibold uppercase tracking-wide text-gray-400">Active deals</p>
              <p className="mt-2 text-3xl font-bold text-white">{metrics.activeDeals}</p>
              <p className="mt-1 text-xs text-gray-500">Excludes Closed Won / Lost</p>
            </div>
            <div className="rounded-xl border border-emerald-900/40 bg-gradient-to-br from-emerald-950/40 to-gray-900/90 p-5 shadow-lg ring-1 ring-emerald-900/20">
              <p className="text-xs font-semibold uppercase tracking-wide text-emerald-200/80">Projected fees</p>
              <p className="mt-2 text-3xl font-bold text-emerald-200">{fmtMoney(metrics.projectedFees)}</p>
              <p className="mt-1 text-xs text-gray-500">Sum of projected fees (active)</p>
            </div>
            <div className="rounded-xl border border-violet-900/40 bg-gradient-to-br from-violet-950/50 to-gray-900/90 p-5 shadow-lg ring-1 ring-violet-900/20">
              <p className="text-xs font-semibold uppercase tracking-wide text-violet-200/80">Outreach due today</p>
              <p className="mt-2 text-3xl font-bold text-violet-200">{metrics.outreachDueToday}</p>
              <p className="mt-1 text-xs text-gray-500">Next touch date ≤ today</p>
            </div>
          </div>

          {/* PIPELINE INTELLIGENCE */}
          <section className="rounded-xl border border-cyan-900/35 bg-gradient-to-br from-cyan-950/20 to-gray-900/90 p-5 shadow-lg ring-1 ring-cyan-900/25">
            <h3 className="text-sm font-bold uppercase tracking-widest text-cyan-200/90">Pipeline intelligence</h3>
            <p className="mt-1 text-xs text-gray-500">
              Live slices from JETA_Buyers — priority score, supplier status, Gulf supply adjacency, and Canada.
            </p>

            {/* 1 — Top prospects */}
            <div className="mt-6 rounded-lg border border-gray-700/80 bg-gray-950/40 p-4">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <h4 className="text-base font-semibold text-white">Top prospects</h4>
                <span className="text-xs text-gray-500">Top 10 by priority score</span>
              </div>
              <div className="mt-3 overflow-x-auto">
                <table className="min-w-full text-left text-sm">
                  <thead>
                    <tr className="border-b border-gray-700 text-xs uppercase tracking-wide text-gray-500">
                      <th className="pb-2 pr-3 font-medium">Buyer / airport</th>
                      <th className="pb-2 pr-3 font-medium">State</th>
                      <th className="pb-2 pr-3 font-medium">Score</th>
                      <th className="pb-2 pr-3 font-medium">Tags</th>
                      <th className="pb-2 font-medium">Outreach</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-800/90">
                    {pipelineIntel.topProspects.length === 0 ? (
                      <tr>
                        <td colSpan={5} className="py-6 text-center text-gray-500">
                          No buyers loaded yet.
                        </td>
                      </tr>
                    ) : (
                      pipelineIntel.topProspects.map((b) => (
                        <tr key={b.id} className="text-gray-200">
                          <td className="py-3 pr-3 align-middle">
                            <div className="font-medium text-white">{b.companyName || '—'}</div>
                            <div className="text-xs text-gray-500">{b.airport || '—'}</div>
                          </td>
                          <td className="whitespace-nowrap py-3 pr-3 align-middle font-mono text-xs text-gray-400">
                            {b.state || '—'}
                          </td>
                          <td className="py-3 pr-3 align-middle">
                            <PriorityScoreBar score={b.priorityScore} />
                          </td>
                          <td className="py-3 pr-3 align-middle">
                            <div className="flex flex-wrap gap-1">
                              {b.priorityTags && b.priorityTags.length > 0 ? (
                                b.priorityTags.map((t, i) => (
                                  <span
                                    key={`${b.id}-t-${i}`}
                                    className="rounded-full bg-amber-950/80 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide text-amber-200/95 ring-1 ring-amber-800/50"
                                  >
                                    {t}
                                  </span>
                                ))
                              ) : (
                                <span className="text-xs text-gray-600">—</span>
                              )}
                            </div>
                          </td>
                          <td className="py-3 align-middle">
                            <button
                              type="button"
                              disabled={aiLoadingId === b.id}
                              onClick={() => runDashboardAiDraft(b)}
                              className="whitespace-nowrap rounded-lg border border-violet-700/60 bg-violet-950/50 px-3 py-1.5 text-xs font-semibold text-violet-100 hover:bg-violet-900/60 disabled:opacity-50"
                            >
                              {aiLoadingId === b.id ? 'Drafting…' : 'Begin outreach'}
                            </button>
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>

            <div className="mt-4 grid gap-4 lg:grid-cols-3">
              {/* 2 — Supply adjacent */}
              <div className="rounded-lg border border-teal-900/40 bg-gray-950/40 p-4">
                <h4 className="text-sm font-semibold text-teal-200/95">Supply adjacent markets</h4>
                <p className="mt-2 text-2xl font-bold text-white tabular-nums">
                  {pipelineIntel.supplyAdjacentCount}
                  <span className="ml-2 text-sm font-normal text-gray-500">buyers</span>
                </p>
                <p className="mt-2 text-sm leading-snug text-gray-400">
                  <span className="font-semibold text-teal-200/90">{pipelineIntel.supplyAdjacentCount}</span> airports
                  near Gulf Coast supply infrastructure
                </p>
                <ul className="mt-3 max-h-48 space-y-1.5 overflow-y-auto text-sm">
                  {Object.entries(pipelineIntel.supplyByState)
                    .sort((a, b) => b[1] - a[1])
                    .map(([st, n]) => (
                      <li key={st} className="flex justify-between gap-2 border-b border-gray-800/80 py-1 text-gray-300">
                        <span className="font-mono text-xs text-gray-400">{st}</span>
                        <span className="font-semibold text-white">{n}</span>
                      </li>
                    ))}
                  {pipelineIntel.supplyAdjacentCount === 0 && (
                    <li className="text-gray-500">No supply-adjacent buyers yet.</li>
                  )}
                </ul>
              </div>

              {/* 3 — Open markets */}
              <div className="rounded-lg border border-emerald-900/40 bg-gray-950/40 p-4">
                <h4 className="text-sm font-semibold text-emerald-200/95">Open markets</h4>
                <p className="mt-1 text-xs text-gray-500">
                  Supplier status = Open — clearest entry points ({pipelineIntel.openCount} total)
                </p>
                <ul className="mt-3 max-h-48 space-y-1.5 overflow-y-auto text-sm">
                  {pipelineIntel.openRanked.map(([st, n]) => (
                    <li key={st} className="flex justify-between gap-2 border-b border-gray-800/80 py-1 text-gray-300">
                      <span className="font-mono text-xs text-gray-400">{st}</span>
                      <span className="font-semibold text-emerald-200/90">{n}</span>
                    </li>
                  ))}
                  {pipelineIntel.openRanked.length === 0 && (
                    <li className="text-gray-500">No Open-status buyers yet.</li>
                  )}
                </ul>
              </div>

              {/* 4 — Canada */}
              <div className="rounded-lg border border-red-900/35 bg-gray-950/40 p-4">
                <h4 className="text-sm font-semibold text-red-200/90">Canada pipeline</h4>
                <p className="mt-2 text-2xl font-bold text-white tabular-nums">
                  {pipelineIntel.canadaTotal}
                  <span className="ml-2 text-sm font-normal text-gray-500">prospects</span>
                </p>
                <ul className="mt-3 max-h-40 space-y-1.5 overflow-y-auto text-sm">
                  {Object.entries(pipelineIntel.canadaByProvince)
                    .sort((a, b) => b[1] - a[1])
                    .map(([prov, n]) => (
                      <li key={prov} className="flex justify-between gap-2 border-b border-gray-800/80 py-1 text-gray-300">
                        <span className="font-mono text-xs text-gray-400">{prov}</span>
                        <span className="font-semibold text-white">{n}</span>
                      </li>
                    ))}
                  {pipelineIntel.canadaTotal === 0 && (
                    <li className="text-gray-500">No Canadian prospects yet.</li>
                  )}
                </ul>
                {pipelineIntel.ontarioCorridorCount > 0 ? (
                  <p className="mt-3 rounded-md border border-amber-800/40 bg-amber-950/30 px-3 py-2 text-xs leading-snug text-amber-100/95">
                    <span className="font-semibold text-amber-200">Ontario corridor</span> — closest to DDI home base (
                    {pipelineIntel.ontarioCorridorCount} in ON)
                  </p>
                ) : null}
              </div>
            </div>

            {/* Tier playbook — aligns with priority_score tags (backend 0–130) */}
            <div className="mt-6 rounded-lg border border-cyan-800/35 bg-gray-950/55 p-4 ring-1 ring-cyan-900/20">
              <h4 className="text-xs font-bold uppercase tracking-wide text-cyan-300/90">Outreach cadence by priority tier</h4>
              <p className="mt-1 text-xs text-gray-500">
                Score bands drive the PRIORITY / HIGH VALUE / STANDARD / LOW PRIORITY tags. Use this playbook for timing Touch 1
                and follow-up rhythm.
              </p>
              <div className="mt-4 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
                <div className="rounded-lg border border-violet-800/40 bg-violet-950/20 p-3">
                  <p className="text-[11px] font-bold uppercase tracking-wide text-violet-200/95">Priority tier · 100–130 pts</p>
                  <p className="mt-2 text-xs font-semibold text-white">Texas / Louisiana airports</p>
                  <ul className="mt-2 space-y-1.5 text-xs leading-relaxed text-gray-400">
                    <li>Near supply and high aircraft count</li>
                    <li>Open supplier status</li>
                    <li>Contact email on file</li>
                  </ul>
                  <p className="mt-3 text-xs font-medium text-violet-200/90">
                    → Touch 1 within 48 hours of import
                  </p>
                </div>
                <div className="rounded-lg border border-amber-800/40 bg-amber-950/20 p-3">
                  <p className="text-[11px] font-bold uppercase tracking-wide text-amber-200/95">High value tier · 70–99 pts</p>
                  <p className="mt-2 text-xs font-semibold text-white">Michigan / Ontario airports</p>
                  <ul className="mt-2 space-y-1.5 text-xs leading-relaxed text-gray-400">
                    <li>Home market advantage</li>
                    <li>Open supplier status</li>
                    <li>Strong aircraft count</li>
                  </ul>
                  <p className="mt-3 text-xs font-medium text-amber-200/90">→ Touch 1 within the first week</p>
                </div>
                <div className="rounded-lg border border-sky-800/40 bg-sky-950/15 p-3">
                  <p className="text-[11px] font-bold uppercase tracking-wide text-sky-200/95">Standard tier · 40–69 pts</p>
                  <p className="mt-2 text-xs font-semibold text-white">All other US and Canada airports</p>
                  <ul className="mt-2 space-y-1.5 text-xs leading-relaxed text-gray-400">
                    <li>Solid demand signal</li>
                    <li>Mixed supplier status</li>
                  </ul>
                  <p className="mt-3 text-xs font-medium text-sky-200/90">→ Outreach in a rolling 30-day sequence</p>
                </div>
                <div className="rounded-lg border border-gray-600/50 bg-gray-900/60 p-3">
                  <p className="text-[11px] font-bold uppercase tracking-wide text-gray-400">Low priority · below 40 pts</p>
                  <ul className="mt-2 space-y-1.5 text-xs leading-relaxed text-gray-500">
                    <li>Small operations</li>
                    <li>Fully branded supply locked in</li>
                  </ul>
                  <p className="mt-3 text-xs font-medium text-gray-400">→ Monitor only; revisit quarterly</p>
                </div>
              </div>
            </div>
          </section>

          <div className="grid gap-4 md:grid-cols-2">
            <div className="rounded-xl border border-slate-700/80 bg-gradient-to-br from-slate-900/90 to-gray-900/90 p-5 shadow-lg ring-1 ring-slate-600/40">
              <p className="text-xs font-semibold uppercase tracking-wide text-slate-200/85">Conventional pipeline</p>
              <p className="mt-2 text-3xl font-bold text-white tabular-nums">{pipelineSplit.conventional.count}</p>
              <p className="mt-1 text-sm text-gray-400">
                Projected fees <span className="font-semibold text-emerald-200/90">{fmtMoney(pipelineSplit.conventional.projectedFees)}</span>
              </p>
              <p className="mt-2 text-xs text-gray-500">Active deals tagged Conventional or Both (excludes Closed Won / Lost)</p>
            </div>
            <div className="rounded-xl border border-emerald-900/45 bg-gradient-to-br from-emerald-950/35 to-gray-900/90 p-5 shadow-lg ring-1 ring-emerald-900/25">
              <p className="text-xs font-semibold uppercase tracking-wide text-emerald-200/85">SAF pipeline</p>
              <p className="mt-2 text-3xl font-bold text-white tabular-nums">{pipelineSplit.saf.count}</p>
              <p className="mt-1 text-sm text-gray-400">
                Projected fees <span className="font-semibold text-emerald-200">{fmtMoney(pipelineSplit.saf.projectedFees)}</span>
              </p>
              <p className="mt-2 text-xs text-gray-500">Active deals tagged SAF or Both</p>
            </div>
          </div>

          {/* SAF resources — external registration / programs */}
          <section className="rounded-xl border border-emerald-900/40 bg-emerald-950/20 p-5 ring-1 ring-emerald-900/20">
            <h4 className="text-xs font-semibold uppercase tracking-wide text-emerald-200/90">SAF resources</h4>
            <p className="mt-1 text-sm text-gray-400">
              Register and list supply/demand for sustainable aviation fuel programs.
            </p>
            <a
              href="https://www.iata.org/en/programs/ops-infra/fuel/"
              target="_blank"
              rel="noopener noreferrer"
              className="mt-3 inline-flex items-center rounded-lg border border-emerald-700/60 bg-emerald-950/40 px-4 py-2 text-sm font-semibold text-emerald-100 hover:bg-emerald-900/50"
            >
              IATA SAF Matchmaker — Register JETA COURTIÈRE
            </a>
          </section>

          {/* IATA jet fuel — JETA_MarketData (weekly sync via nexus_scheduler --jeta-market) */}
          <section
            id="jeta-dashboard-market-section"
            className="rounded-xl border border-sky-900/45 bg-gradient-to-br from-sky-950/45 to-gray-900/90 p-5 shadow-lg ring-1 ring-sky-900/25"
          >
            <h4 className="text-xs font-semibold uppercase tracking-wide text-sky-200/85">Market price</h4>
            <p className="mt-1 text-sm text-sky-100/90">
              Global average jet fuel (IATA headline){' '}
              <span className="text-sky-300/80">· {marketSnapshot?.sourceLabel || 'IATA Fuel Price Monitor'}</span>
            </p>
            {marketSnapshot?.latest?.pricePerBarrel != null && Number.isFinite(marketSnapshot.latest.pricePerBarrel) ? (
              <>
                <p className="mt-3 text-3xl font-bold text-white tabular-nums">
                  {fmtUsdPerBbl(marketSnapshot.latest.pricePerBarrel)}
                </p>
                <p className="mt-2 text-sm text-gray-400">
                  Last updated{' '}
                  <span className="text-gray-200">
                    {marketSnapshot.latest.priceDate || '—'}
                  </span>
                </p>
                {marketSnapshot.weekOverWeekChangePct != null &&
                marketSnapshot.weekOverWeekChangeAbs != null &&
                marketSnapshot.previous?.pricePerBarrel != null ? (
                  <p className="mt-2 text-sm">
                    <span className="text-gray-500">Week over week:</span>{' '}
                    <span
                      className={
                        marketSnapshot.weekOverWeekChangePct >= 0 ? 'font-semibold text-amber-300' : 'font-semibold text-emerald-300'
                      }
                    >
                      {marketSnapshot.weekOverWeekChangePct >= 0 ? '+' : ''}
                      {marketSnapshot.weekOverWeekChangePct.toFixed(2)}% (
                      {marketSnapshot.weekOverWeekChangeAbs >= 0 ? '+' : ''}
                      {new Intl.NumberFormat('en-US', {
                        style: 'currency',
                        currency: 'USD',
                        maximumFractionDigits: 2,
                      }).format(marketSnapshot.weekOverWeekChangeAbs)}{' '}
                      vs prior {fmtUsdPerBbl(marketSnapshot.previous.pricePerBarrel)})
                    </span>
                  </p>
                ) : (
                  <p className="mt-2 text-xs text-gray-500">
                    Week-over-week change appears after a second weekly data point is stored.
                  </p>
                )}
              </>
            ) : (
              <p className="mt-3 text-sm text-gray-400">
                {marketSnapshot?.hint ||
                  'No market rows yet — ensure Airtable table JETA_MarketData exists, then run a sync (?refresh=1) or the weekly scheduler.'}
              </p>
            )}
            {marketSnapshot?.latest?.supplyDisruptionAlert ? (
              <div
                className="mt-4 rounded-lg border border-amber-600/70 bg-amber-950/50 px-3 py-2 text-sm text-amber-100"
                role="alert"
              >
                <span className="font-semibold text-amber-200">Supply disruption alert</span>
                <span className="ml-1.5 text-amber-100/90">
                  — Flagged on JETA_MarketData. Review chokepoints and regions below.
                </span>
              </div>
            ) : null}
            {marketSnapshot?.latest?.escalationClauseTriggered ? (
              <div
                className="mt-3 rounded-lg border border-violet-600/60 bg-violet-950/40 px-3 py-2 text-sm text-violet-100"
                role="alert"
              >
                <span className="font-semibold text-violet-200">Fee escalation review</span>
                <span className="ml-1.5 text-violet-100/90">
                  — Escalation clause trigger is on. Review active deals for fee agreement activation (IATA / benchmark
                  bands).
                </span>
              </div>
            ) : null}
            {(() => {
              const m = marketSnapshot?.latest;
              if (!m) return null;
              const geo = m.geopoliticalRiskLevel;
              const regions = m.activeConflictRegions?.length ? m.activeConflictRegions : [];
              const drivers = m.priceDrivers?.length ? m.priceDrivers : [];
              const cp = m.chokepointStatus;
              const hasCp = cp && (cp.hormuz || cp.suez || cp.bosphorus || cp.southChinaSea);
              const notes = m.marketNotes?.trim();
              const crude = m.crudeOilPriceBbl;
              const crack = m.jetCrackSpread;
              const warPrem = m.warPremiumEstimated;
              const hasMetrics =
                (crude != null && Number.isFinite(crude)) ||
                (crack != null && Number.isFinite(crack)) ||
                (warPrem != null && Number.isFinite(warPrem));
              const trend = m.priceTrend;
              const forecast = m.forecast30Day;
              const analyst = m.analystSource?.trim();
              if (
                !geo &&
                regions.length === 0 &&
                !hasCp &&
                drivers.length === 0 &&
                !hasMetrics &&
                !trend &&
                !forecast &&
                !notes &&
                !analyst
              ) {
                return null;
              }
              return (
                <div className="mt-4 space-y-3 border-t border-sky-800/40 pt-4">
                  <p className="text-[10px] font-semibold uppercase tracking-wide text-sky-300/90">
                    Market context (JETA_MarketData)
                  </p>
                  {geo ? (
                    <div className="flex flex-wrap items-center gap-2 text-sm">
                      <span className="text-gray-500">Geopolitical risk</span>
                      <span
                        className={`rounded px-2 py-0.5 text-xs font-semibold ${
                          geo === 'Critical'
                            ? 'bg-rose-900/80 text-rose-100'
                            : geo === 'High'
                              ? 'bg-orange-900/70 text-orange-100'
                              : geo === 'Elevated'
                                ? 'bg-amber-900/60 text-amber-100'
                                : 'bg-slate-800 text-slate-200'
                        }`}
                      >
                        {geo}
                      </span>
                    </div>
                  ) : null}
                  {regions.length > 0 ? (
                    <div>
                      <p className="text-xs text-gray-500">Active conflict regions</p>
                      <div className="mt-1 flex flex-wrap gap-1.5">
                        {regions.map((r) => (
                          <span
                            key={r}
                            className="rounded border border-sky-800/60 bg-sky-950/40 px-2 py-0.5 text-xs text-sky-100"
                          >
                            {r}
                          </span>
                        ))}
                      </div>
                    </div>
                  ) : null}
                  {drivers.length > 0 ? (
                    <div>
                      <p className="text-xs text-gray-500">Price drivers</p>
                      <div className="mt-1 flex flex-wrap gap-1.5">
                        {drivers.map((d) => (
                          <span
                            key={d}
                            className="rounded border border-amber-800/50 bg-amber-950/30 px-2 py-0.5 text-xs text-amber-100/95"
                          >
                            {d}
                          </span>
                        ))}
                      </div>
                    </div>
                  ) : null}
                  {hasMetrics ? (
                    <div className="grid gap-2 sm:grid-cols-3">
                      <div className="rounded border border-sky-800/40 bg-black/20 px-2 py-1.5">
                        <p className="text-[10px] uppercase text-gray-500">Crude (note WTI/Brent in Airtable)</p>
                        <p className="font-mono text-sm text-sky-100">{fmtMoneyPerBbl(crude ?? undefined)}</p>
                      </div>
                      <div className="rounded border border-sky-800/40 bg-black/20 px-2 py-1.5">
                        <p className="text-[10px] uppercase text-gray-500">Jet crack spread</p>
                        <p className="font-mono text-sm text-sky-100">{fmtMoneyPerBbl(crack ?? undefined)}</p>
                        <p className="text-[10px] text-gray-600">Healthy ref. ~$20–35/bbl</p>
                      </div>
                      <div className="rounded border border-sky-800/40 bg-black/20 px-2 py-1.5">
                        <p className="text-[10px] uppercase text-gray-500">War premium (est.)</p>
                        <p className="font-mono text-sm text-sky-100">{fmtMoneyPerBbl(warPrem ?? undefined)}</p>
                      </div>
                    </div>
                  ) : null}
                  {trend || forecast ? (
                    <div className="flex flex-wrap gap-3 text-sm">
                      {trend ? (
                        <div>
                          <span className="text-gray-500">Trend </span>
                          <span className="rounded bg-slate-800 px-2 py-0.5 text-xs font-medium text-slate-100">
                            {trend}
                          </span>
                        </div>
                      ) : null}
                      {forecast ? (
                        <div>
                          <span className="text-gray-500">30-day outlook </span>
                          <span className="rounded bg-slate-800 px-2 py-0.5 text-xs font-medium text-slate-100">
                            {forecast}
                          </span>
                        </div>
                      ) : null}
                    </div>
                  ) : null}
                  {hasCp ? (
                    <div className="text-sm">
                      <p className="text-xs text-gray-500">Chokepoints</p>
                      <p className="mt-1 font-mono text-[11px] leading-relaxed text-sky-100/95">
                        {`Hormuz: ${cp?.hormuz || '—'} · Suez: ${cp?.suez || '—'} · Bosphorus: ${cp?.bosphorus || '—'} · South China Sea: ${cp?.southChinaSea || '—'}`}
                      </p>
                    </div>
                  ) : null}
                  {notes ? (
                    <div>
                      <p className="text-xs text-gray-500">What&apos;s driving price (notes)</p>
                      {analyst ? (
                        <p className="mt-0.5 text-[10px] text-gray-600">Source: {analyst}</p>
                      ) : null}
                      <p className="mt-1 whitespace-pre-wrap text-sm leading-relaxed text-gray-200">{notes}</p>
                    </div>
                  ) : analyst ? (
                    <p className="text-[10px] text-gray-600">Analyst source: {analyst}</p>
                  ) : null}
                </div>
              );
            })()}
            {marketSnapshot?.escalationPriceAlert?.triggered &&
            (marketSnapshot.escalationPriceAlert.affected_count ?? 0) > 0 ? (
              <div
                className="mt-4 rounded-lg border border-orange-600/60 bg-orange-950/35 px-3 py-3 text-sm text-orange-100"
                role="alert"
              >
                <p className="font-semibold text-orange-200">
                  {marketSnapshot.escalationPriceAlert.message ||
                    `PRICE ALERT: Escalation review recommended on ${marketSnapshot.escalationPriceAlert.affected_count} active deal(s).`}
                </p>
                <p className="mt-1 text-xs text-orange-100/80">
                  Two consecutive weekly IATA snapshots vs each deal&apos;s stored base benchmark — review and notify
                  counterparties within 48 hours.
                </p>
                <ul className="mt-3 space-y-2">
                  {(marketSnapshot.escalationPriceAlert.affected_deals || []).map((d) => (
                    <li
                      key={d.deal_id}
                      className="flex flex-wrap items-center justify-between gap-2 rounded border border-orange-800/40 bg-black/20 px-2 py-1.5"
                    >
                      <span className="text-orange-50">
                        <span className="font-medium">{d.deal_name}</span>
                        {d.clause_version ? (
                          <span className="ml-2 text-xs text-orange-200/70">({d.clause_version})</span>
                        ) : null}
                      </span>
                      <a
                        href={`mailto:?subject=${encodeURIComponent(
                          `JETA — Fee escalation review: ${d.deal_name}`,
                        )}&body=${encodeURIComponent(
                          `Hello —\n\nNEXUS monitoring indicates the IATA benchmark may trigger fee escalation review for:\n\nDeal: ${d.deal_name}\n\nPlease confirm next steps within 48 hours per the executed agreement.\n`,
                        )}`}
                        className="shrink-0 rounded border border-orange-600/60 px-2 py-1 text-xs font-semibold text-orange-200 hover:bg-orange-950/50"
                      >
                        Notify
                      </a>
                    </li>
                  ))}
                </ul>
              </div>
            ) : null}
          </section>

          {/* Deal alerts — stuck deals, stale NCNDA, seller documentation SLA (backend: jeta_fraud_detection) */}
          <section className="rounded-xl border border-rose-900/40 bg-rose-950/25 p-5">
            <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <h4 className="text-lg font-semibold text-rose-200/95">Deal alerts</h4>
                <p className="mt-1 text-xs text-gray-500">
                  Stale stages, unsigned NCNDA, sellers without terminal/storage documentation (72h). Refreshes on load.
                </p>
              </div>
              {setActiveTab && (
                <button
                  type="button"
                  onClick={() => setActiveTab('deal-manager')}
                  className="rounded-lg border border-rose-800/50 px-3 py-2 text-xs font-semibold text-rose-200 hover:bg-rose-950/50"
                >
                  Deal Manager →
                </button>
              )}
            </div>
            {dealAlerts.length === 0 ? (
              <p className="mt-4 text-sm text-gray-500">No automated deal alerts right now.</p>
            ) : (
              <ul className="mt-4 divide-y divide-rose-900/30">
                {dealAlerts.map((a, i) => (
                  <li key={i} className="py-3 text-sm">
                    <div className="flex flex-wrap items-baseline gap-2">
                      <span
                        className={`rounded px-1.5 py-0.5 text-[10px] font-bold uppercase ${
                          a.severity === 'high' ? 'bg-rose-900/80 text-rose-100' : 'bg-gray-800 text-gray-300'
                        }`}
                      >
                        {a.type || 'ALERT'}
                      </span>
                      {a.deal_name ? (
                        <span className="font-medium text-white">{a.deal_name}</span>
                      ) : a.company_name ? (
                        <span className="font-medium text-white">{a.company_name}</span>
                      ) : null}
                      {a.stage ? <span className="text-xs text-gray-500">· {a.stage}</span> : null}
                    </div>
                    <p className="mt-1 text-gray-300">{a.message || '—'}</p>
                  </li>
                ))}
              </ul>
            )}
          </section>

          <div className="grid gap-8 lg:grid-cols-2">
            {/* Pipeline distribution */}
            <section className="rounded-xl border border-gray-700 bg-gray-900/50 p-5">
              <h4 className="text-lg font-semibold text-amber-200/95">Pipeline stage distribution</h4>
              <p className="mt-1 text-xs text-gray-500">Buyer counts by pipeline stage (1–9)</p>
              <div className="mt-4 space-y-2">
                {JETA_STAGE_LABELS.map((label, i) => {
                  const n = stageCounts[i] ?? 0;
                  const pct = Math.round((n / maxStageCount) * 100);
                  return (
                    <div key={label} className="flex items-center gap-3 text-sm">
                      <span className="w-8 shrink-0 text-right font-mono text-xs text-gray-500">{i + 1}</span>
                      <div className="min-w-0 flex-1">
                        <div className="mb-0.5 flex justify-between gap-2">
                          <span className="truncate text-gray-300">{label}</span>
                          <span className="shrink-0 font-semibold text-white">{n}</span>
                        </div>
                        <div className="h-2.5 overflow-hidden rounded-full bg-gray-800">
                          <div
                            className="h-full rounded-full bg-gradient-to-r from-amber-600 to-orange-600"
                            style={{ width: `${pct}%` }}
                          />
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </section>

            {/* Recent outreach */}
            <section className="rounded-xl border border-gray-700 bg-gray-900/50 p-5">
              <div className="flex items-center justify-between gap-2">
                <h4 className="text-lg font-semibold text-amber-200/95">Recent activity</h4>
                {setActiveTab && (
                  <button
                    type="button"
                    onClick={() => setActiveTab('outreach-center')}
                    className="text-xs font-semibold text-amber-400 hover:text-amber-300"
                  >
                    Outreach Center →
                  </button>
                )}
              </div>
              <p className="mt-1 text-xs text-gray-500">Last 10 outreach touches (all buyers)</p>
              <ul className="mt-3 divide-y divide-gray-700/80">
                {recentOutreach.length === 0 ? (
                  <li className="py-6 text-center text-sm text-gray-500">No outreach logged yet.</li>
                ) : (
                  recentOutreach.map((row) => (
                    <li key={row.id} className="flex flex-col gap-0.5 py-3 text-sm">
                      <div className="flex flex-wrap items-baseline justify-between gap-2">
                        <span className="font-medium text-white">{row.companyName || '—'}</span>
                        <span className="text-xs text-gray-500">{row.touchDate || '—'}</span>
                      </div>
                      <div className="text-xs text-gray-400">
                        Touch #{row.touchNumber} · {row.channel || '—'} · {row.responseStatus || row.responseReceived || '—'}
                      </div>
                    </li>
                  ))
                )}
              </ul>
            </section>
          </div>

          {/* Deals requiring attention */}
          <section className="rounded-xl border border-amber-900/30 bg-amber-950/20 p-5">
            <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <h4 className="text-lg font-semibold text-amber-200/95">Deals requiring attention</h4>
                <p className="mt-1 text-xs text-gray-500">
                  Active deals with no buyer outreach or last-contact activity in the last 7 days (uses outreach touch
                  dates and buyer last contact).
                </p>
              </div>
              {setActiveTab && (
                <button
                  type="button"
                  onClick={() => setActiveTab('deal-manager')}
                  className="rounded-lg border border-amber-700/50 px-3 py-2 text-xs font-semibold text-amber-200 hover:bg-amber-950/50"
                >
                  Deal Manager →
                </button>
              )}
            </div>
            <div className="mt-4 overflow-x-auto">
              <table className="min-w-full text-left text-sm">
                <thead>
                  <tr className="border-b border-gray-700 text-gray-500">
                    <th className="pb-2 pr-4 font-medium">Deal</th>
                    <th className="pb-2 pr-4 font-medium">Buyer</th>
                    <th className="pb-2 pr-4 font-medium">Stage</th>
                    <th className="pb-2 font-medium">Last activity</th>
                  </tr>
                </thead>
                <tbody className="text-gray-300">
                  {dealsNeedingAttention.length === 0 ? (
                    <tr>
                      <td colSpan={4} className="py-8 text-center text-gray-500">
                        No stale active deals — or add outreach / last contact dates to see this list.
                      </td>
                    </tr>
                  ) : (
                    dealsNeedingAttention.map(({ deal, last, daysStale }) => (
                      <tr key={deal.id} className="border-t border-gray-700/60">
                        <td className="py-3 pr-4 font-medium text-white">
                          {deal.dealName?.trim() || deal.id.slice(0, 10) + '…'}
                        </td>
                        <td className="py-3 pr-4">{deal.buyerName || '—'}</td>
                        <td className="py-3 pr-4 text-xs text-gray-400">{deal.dealStage}</td>
                        <td className="py-3 text-xs">
                          {!last ? (
                            <span className="text-amber-400">No tracked activity</span>
                          ) : (
                            <>
                              {last.toLocaleDateString()}
                              <span className="ml-2 text-gray-500">({daysStale}d ago)</span>
                            </>
                          )}
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </section>

          {/* AI escalation / counterparty notices (Claude) */}
          {noticeModalOpen && (
            <>
              <button
                type="button"
                className="fixed inset-0 z-[55] bg-black/65"
                aria-label="Close"
                onClick={() => setNoticeModalOpen(false)}
              />
              <div className="fixed left-1/2 top-1/2 z-[60] max-h-[92vh] w-full max-w-3xl -translate-x-1/2 -translate-y-1/2 overflow-y-auto rounded-xl border border-orange-900/50 bg-gray-900 p-6 shadow-xl">
                <h4 className="text-lg font-bold text-white">Counterparty notices — AI draft</h4>
                <p className="mt-1 text-xs text-gray-500">
                  Uses JETA_MarketData + active deals (escalation watchlist when present). Review before sending.
                </p>
                {noticeLoading ? (
                  <p className="mt-6 text-sm text-gray-400">Generating drafts with Claude…</p>
                ) : null}
                {noticeError ? (
                  <p className="mt-4 rounded border border-red-900/50 bg-red-950/40 px-3 py-2 text-sm text-red-200">{noticeError}</p>
                ) : null}
                {noticeDisclaimer ? (
                  <p className="mt-4 text-xs leading-relaxed text-amber-200/85">{noticeDisclaimer}</p>
                ) : null}
                {noticeInfo && !noticeLoading ? (
                  <p className="mt-4 text-sm text-gray-400">{noticeInfo}</p>
                ) : null}
                <div className="mt-4 space-y-4">
                  {noticeDrafts.map((row, idx) => {
                    const subj = row.subject || 'JETA COURTIÈRE — Fee escalation / market notice';
                    const body = row.body || '';
                    const mail =
                      row.buyer_email && body
                        ? `mailto:${encodeURIComponent(row.buyer_email)}?subject=${encodeURIComponent(subj)}&body=${encodeURIComponent(body)}`
                        : '';
                    return (
                      <div
                        key={`${row.deal_id || idx}-${idx}`}
                        className="rounded-lg border border-gray-700 bg-gray-950/50 p-3"
                      >
                        <p className="text-xs font-mono text-gray-500">{row.deal_id || 'deal'}</p>
                        <p className="mt-1 text-sm font-semibold text-white">{subj}</p>
                        {row.buyer_email ? (
                          <p className="mt-1 text-xs text-gray-500">
                            To: <span className="text-gray-300">{row.buyer_email}</span>
                          </p>
                        ) : (
                          <p className="mt-1 text-xs text-amber-200/80">Buyer email not on file — copy body to CRM.</p>
                        )}
                        <textarea
                          readOnly
                          value={body}
                          rows={10}
                          className="mt-2 w-full resize-y rounded border border-gray-600 bg-gray-900 px-2 py-1.5 font-mono text-xs text-gray-100"
                        />
                        <div className="mt-2 flex flex-wrap gap-2">
                          <button
                            type="button"
                            onClick={async () => {
                              try {
                                await navigator.clipboard.writeText(body);
                              } catch {
                                /* ignore */
                              }
                            }}
                            className="rounded bg-gray-700 px-2 py-1 text-xs font-semibold text-white hover:bg-gray-600"
                          >
                            Copy body
                          </button>
                          {mail ? (
                            <a
                              href={mail}
                              className="rounded bg-gradient-to-r from-orange-600 to-amber-700 px-2 py-1 text-xs font-semibold text-white hover:from-orange-500 hover:to-amber-600"
                            >
                              Email buyer
                            </a>
                          ) : null}
                        </div>
                      </div>
                    );
                  })}
                </div>
                <p className="mt-4 text-[10px] text-gray-600">
                  Seller-side counterparties: deliver through your seller contact records — seller email is not always in
                  NEXUS.
                </p>
                <button
                  type="button"
                  onClick={() => setNoticeModalOpen(false)}
                  className="mt-4 rounded-lg px-4 py-2 text-sm text-gray-400 hover:text-white"
                >
                  Close
                </button>
              </div>
            </>
          )}

          {/* AI email draft (same flow as Outreach Center) */}
          {aiModalOpen && (
            <>
              <button
                type="button"
                className="fixed inset-0 z-[45] bg-black/60"
                aria-label="Close"
                onClick={() => setAiModalOpen(false)}
              />
              <div className="fixed left-1/2 top-1/2 z-[50] max-h-[90vh] w-full max-w-2xl -translate-x-1/2 -translate-y-1/2 overflow-y-auto rounded-xl border border-violet-900/50 bg-gray-900 p-6 shadow-xl">
                <h4 className="text-lg font-bold text-white">AI email draft</h4>
                {aiTargetBuyer && (
                  <p className="mt-1 text-sm text-gray-400">
                    Touch {aiTouchNumber} · {aiTargetBuyer.contactName || 'Contact'} at {aiTargetBuyer.companyName || 'Company'}
                  </p>
                )}
                {aiError && (
                  <p className="mt-3 rounded border border-red-900/50 bg-red-950/40 px-3 py-2 text-sm text-red-200">{aiError}</p>
                )}
                <label className="mt-4 block text-sm text-gray-300">
                  Subject <span className="text-gray-500">(for email client)</span>
                  <input
                    type="text"
                    value={aiSubject}
                    onChange={(e) => setAiSubject(e.target.value)}
                    className="mt-1 w-full rounded-lg border border-gray-600 bg-gray-800 px-3 py-2 text-white"
                  />
                </label>
                <label className="mt-3 block text-sm text-gray-300">
                  Body <span className="text-gray-500">(edit before sending)</span>
                  <textarea
                    value={aiDraftBody}
                    onChange={(e) => setAiDraftBody(e.target.value)}
                    rows={16}
                    className="mt-1 w-full rounded-lg border border-gray-600 bg-gray-800 px-3 py-2 font-mono text-sm text-white"
                    placeholder="Draft will appear here…"
                  />
                </label>
                <div className="mt-4 flex flex-wrap gap-2">
                  <button
                    type="button"
                    onClick={copyAiDraft}
                    disabled={!aiDraftBody.trim()}
                    className="rounded-lg bg-gray-700 px-4 py-2 text-sm font-semibold text-white hover:bg-gray-600 disabled:opacity-50"
                  >
                    Copy body
                  </button>
                  {mailtoDraftHref && (
                    <a
                      href={mailtoDraftHref}
                      className="inline-flex items-center rounded-lg bg-gradient-to-r from-violet-600 to-amber-700 px-4 py-2 text-sm font-semibold text-white hover:from-violet-500 hover:to-amber-600"
                    >
                      Open in email
                    </a>
                  )}
                  {setActiveTab && (
                    <button
                      type="button"
                      onClick={() => {
                        setAiModalOpen(false);
                        setActiveTab('outreach-center');
                      }}
                      className="rounded-lg border border-gray-600 px-4 py-2 text-sm font-semibold text-gray-300 hover:bg-gray-800"
                    >
                      Log touch in Outreach Center
                    </button>
                  )}
                  <button
                    type="button"
                    onClick={() => setAiModalOpen(false)}
                    className="rounded-lg px-4 py-2 text-sm text-gray-400 hover:text-white"
                  >
                    Close
                  </button>
                </div>
              </div>
            </>
          )}
        </>
      )}
    </div>
  );
};

export default DashboardTab;
