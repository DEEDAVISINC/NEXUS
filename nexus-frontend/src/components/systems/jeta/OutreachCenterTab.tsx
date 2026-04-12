import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { api } from '../../../api/client';
import type { JetaBuyer } from './BuyerPipelineTab';

export interface JetaDueBuyer extends JetaBuyer {
  touchNumberDue: number;
  lastResponse: string;
}

export interface JetaOutreachRow {
  id: string;
  buyerId: string;
  companyName: string;
  contactName: string;
  touchNumber: number;
  channel: string;
  touchDate: string;
  responseReceived: string;
  responseStatus: string;
  notes: string;
  nextTouchDate: string;
  createdTime?: string;
}

const CHANNEL_OPTIONS = ['Email', 'Phone', 'LinkedIn', 'In-person', 'Other'] as const;
const RESPONSE_STATUS_OPTIONS = [
  'Pending',
  'Positive',
  'Negative',
  'No response',
  'Scheduled',
  'Other',
] as const;

function todayISO(): string {
  const d = new Date();
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${y}-${m}-${day}`;
}

const OutreachCenterTab: React.FC = () => {
  const [dueBuyers, setDueBuyers] = useState<JetaDueBuyer[]>([]);
  const [outreachRows, setOutreachRows] = useState<JetaOutreachRow[]>([]);
  const [allBuyers, setAllBuyers] = useState<JetaBuyer[]>([]);
  const [filterOptions, setFilterOptions] = useState<{
    channels: string[];
    responseStatuses: string[];
  }>({ channels: [], responseStatuses: [] });

  const [loadingDue, setLoadingDue] = useState(true);
  const [loadingLog, setLoadingLog] = useState(true);
  const [errorDue, setErrorDue] = useState<string | null>(null);
  const [errorLog, setErrorLog] = useState<string | null>(null);
  const [hint, setHint] = useState<string | null>(null);

  const [sort, setSort] = useState<'touch_date_desc' | 'touch_date_asc'>('touch_date_desc');
  const [filterChannel, setFilterChannel] = useState('');
  const [filterResponse, setFilterResponse] = useState('');

  const [modalOpen, setModalOpen] = useState(false);
  const [saving, setSaving] = useState(false);
  const [formBuyerId, setFormBuyerId] = useState('');
  const [formTouchNumber, setFormTouchNumber] = useState(1);
  const [formChannel, setFormChannel] = useState<string>(CHANNEL_OPTIONS[0]);
  const [formTouchDate, setFormTouchDate] = useState(todayISO);
  const [formResponseReceived, setFormResponseReceived] = useState('');
  const [formResponseStatus, setFormResponseStatus] = useState<string>(RESPONSE_STATUS_OPTIONS[0]);
  const [formNotes, setFormNotes] = useState('');
  const [formNextTouchDate, setFormNextTouchDate] = useState('');

  const [aiModalOpen, setAiModalOpen] = useState(false);
  const [aiDraftBody, setAiDraftBody] = useState('');
  const [aiSubject, setAiSubject] = useState('JETA COURTIÈRE — Jet-A supply / quick introduction');
  const [aiTargetBuyer, setAiTargetBuyer] = useState<JetaDueBuyer | null>(null);
  const [aiLoadingId, setAiLoadingId] = useState<string | null>(null);
  const [aiError, setAiError] = useState<string | null>(null);

  const loadDue = useCallback(async () => {
    setLoadingDue(true);
    setErrorDue(null);
    try {
      const res = (await api.getJetaOutreachDueBuyers()) as {
        success?: boolean;
        buyers?: JetaDueBuyer[];
        error?: string;
        hint?: string;
      };
      if (res.hint) setHint(res.hint);
      if (res.success === false && res.error) setErrorDue(res.error);
      else setDueBuyers(res.buyers || []);
    } catch (e: unknown) {
      setErrorDue(e instanceof Error ? e.message : 'Failed to load due buyers');
      setDueBuyers([]);
    } finally {
      setLoadingDue(false);
    }
  }, []);

  const loadLog = useCallback(async () => {
    setLoadingLog(true);
    setErrorLog(null);
    try {
      const res = (await api.getJetaOutreach({
        sort,
        channel: filterChannel || undefined,
        response_status: filterResponse || undefined,
      })) as {
        success?: boolean;
        outreach?: JetaOutreachRow[];
        filterOptions?: { channels: string[]; responseStatuses: string[] };
        error?: string;
        hint?: string;
      };
      if (res.hint) setHint(res.hint);
      if (res.success === false && res.error) setErrorLog(res.error);
      else {
        setOutreachRows(res.outreach || []);
        if (res.filterOptions) {
          setFilterOptions({
            channels: res.filterOptions.channels || [],
            responseStatuses: res.filterOptions.responseStatuses || [],
          });
        }
      }
    } catch (e: unknown) {
      setErrorLog(e instanceof Error ? e.message : 'Failed to load outreach log');
      setOutreachRows([]);
    } finally {
      setLoadingLog(false);
    }
  }, [sort, filterChannel, filterResponse]);

  const loadBuyers = useCallback(async () => {
    try {
      const res = (await api.getJetaBuyers({})) as { buyers?: JetaBuyer[] };
      setAllBuyers(res.buyers || []);
    } catch {
      setAllBuyers([]);
    }
  }, []);

  useEffect(() => {
    loadDue();
    loadBuyers();
  }, [loadDue, loadBuyers]);

  useEffect(() => {
    loadLog();
  }, [loadLog]);

  const nextTouchForBuyer = useCallback(
    (buyerId: string) => {
      const nums = outreachRows.filter((r) => r.buyerId === buyerId).map((r) => r.touchNumber || 0);
      const m = nums.length ? Math.max(...nums) : 0;
      return m + 1;
    },
    [outreachRows]
  );

  const openNewOutreach = () => {
    setFormBuyerId(allBuyers[0]?.id || '');
    setFormTouchNumber(allBuyers[0] ? nextTouchForBuyer(allBuyers[0].id) : 1);
    setFormChannel(CHANNEL_OPTIONS[0]);
    setFormTouchDate(todayISO());
    setFormResponseReceived('');
    setFormResponseStatus(RESPONSE_STATUS_OPTIONS[0]);
    setFormNotes('');
    setFormNextTouchDate('');
    setModalOpen(true);
  };

  useEffect(() => {
    if (!modalOpen || !formBuyerId) return;
    setFormTouchNumber(nextTouchForBuyer(formBuyerId));
  }, [formBuyerId, modalOpen, nextTouchForBuyer]);

  const channelOptionsForFilter = useMemo(() => {
    const merged = new Set<string>([...filterOptions.channels, ...CHANNEL_OPTIONS]);
    return Array.from(merged).sort();
  }, [filterOptions.channels]);

  const responseOptionsForFilter = useMemo(() => {
    const merged = new Set<string>([...filterOptions.responseStatuses, ...RESPONSE_STATUS_OPTIONS]);
    return Array.from(merged).sort();
  }, [filterOptions.responseStatuses]);

  const runAiDraft = async (b: JetaDueBuyer) => {
    setAiLoadingId(b.id);
    setAiError(null);
    try {
      const res = (await api.postJetaOutreachAiDraft({
        buyerId: b.id,
        touchNumber: b.touchNumberDue,
        contactName: b.contactName,
        companyName: b.companyName,
        buyerType: b.buyerType,
        airport: b.airport,
        state: b.state,
      })) as { success?: boolean; draft?: string; error?: string };
      if (res.success === false || !res.draft) {
        setAiError(res.error || 'No draft returned');
        setAiDraftBody('');
        setAiTargetBuyer(b);
        setAiModalOpen(true);
        return;
      }
      setAiDraftBody(res.draft);
      setAiTargetBuyer(b);
      setAiModalOpen(true);
    } catch (e: unknown) {
      setAiError(e instanceof Error ? e.message : 'AI draft failed');
      setAiDraftBody('');
      setAiTargetBuyer(b);
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

  const saveOutreach = async () => {
    if (!formBuyerId) {
      alert('Select a buyer.');
      return;
    }
    setSaving(true);
    try {
      const res = (await api.createJetaOutreach({
        buyerId: formBuyerId,
        touchNumber: formTouchNumber,
        channel: formChannel,
        touchDate: formTouchDate,
        responseReceived: formResponseReceived,
        responseStatus: formResponseStatus,
        notes: formNotes,
        nextTouchDate: formNextTouchDate || '',
      })) as { success?: boolean; error?: string };
      if (res.success === false) {
        alert(res.error || 'Save failed');
        return;
      }
      setModalOpen(false);
      await Promise.all([loadDue(), loadLog(), loadBuyers()]);
    } catch (e: unknown) {
      alert(e instanceof Error ? e.message : 'Save failed');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="relative min-h-[420px] space-y-10">
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h3 className="text-xl font-bold text-white">Outreach Center</h3>
          <p className="text-sm text-gray-400">Airtable · JETA_Buyers · JETA_Outreach</p>
        </div>
        <button
          type="button"
          onClick={openNewOutreach}
          className="rounded-lg bg-gradient-to-r from-amber-600 to-orange-600 px-4 py-2 text-sm font-semibold text-white shadow hover:from-amber-500 hover:to-orange-500"
        >
          + Log new touch
        </button>
      </div>

      {hint && (
        <div className="rounded-lg border border-amber-700/50 bg-amber-950/40 px-4 py-3 text-sm text-amber-100">
          {hint}
        </div>
      )}

      {/* 1. DUE TODAY */}
      <section>
        <h4 className="mb-3 text-lg font-semibold text-amber-200/95">Due today &amp; overdue</h4>
        <p className="mb-3 text-xs text-gray-500">
          Buyers with <span className="text-gray-400">Next Touch Date</span> on or before today. Touch # is next
          sequence; last response from the latest outreach row.
        </p>
        {errorDue && (
          <p className="mb-2 text-sm text-red-400">Error: {errorDue}</p>
        )}
        {loadingDue ? (
          <div className="py-8 text-center text-gray-400">Loading…</div>
        ) : (
          <div className="overflow-x-auto rounded-xl border border-gray-700">
            <table className="min-w-full divide-y divide-gray-700 text-left text-sm">
              <thead className="bg-gray-800/80">
                <tr>
                  <th className="px-4 py-3 font-semibold text-gray-300">Contact</th>
                  <th className="px-4 py-3 font-semibold text-gray-300">Company</th>
                  <th className="px-4 py-3 font-semibold text-gray-300">Touch # due</th>
                  <th className="px-4 py-3 font-semibold text-gray-300">Next touch date</th>
                  <th className="px-4 py-3 font-semibold text-gray-300">Last response</th>
                  <th className="px-4 py-3 font-semibold text-gray-300">AI</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-700/80">
                {dueBuyers.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="px-4 py-10 text-center text-gray-500">
                      No buyers due. Set <code className="text-gray-400">Next Touch Date</code> on buyers in
                      Airtable, or log outreach with a follow-up date.
                    </td>
                  </tr>
                ) : (
                  dueBuyers.map((b) => (
                    <tr key={b.id} className="bg-gray-900/40">
                      <td className="px-4 py-3 font-medium text-white">{b.contactName || '—'}</td>
                      <td className="px-4 py-3 text-gray-300">{b.companyName || '—'}</td>
                      <td className="px-4 py-3 text-amber-300">{b.touchNumberDue}</td>
                      <td className="px-4 py-3 text-gray-400">{b.nextTouchDate || '—'}</td>
                      <td className="max-w-md px-4 py-3 text-gray-400">
                        {b.lastResponse ? (
                          <span className="line-clamp-2">{b.lastResponse}</span>
                        ) : (
                          '—'
                        )}
                      </td>
                      <td className="whitespace-nowrap px-4 py-3">
                        <button
                          type="button"
                          disabled={aiLoadingId === b.id}
                          onClick={() => runAiDraft(b)}
                          className="rounded-md border border-violet-500/60 bg-violet-950/50 px-2.5 py-1 text-xs font-semibold text-violet-200 hover:bg-violet-900/60 disabled:opacity-50"
                        >
                          {aiLoadingId === b.id ? '…' : 'AI Draft'}
                        </button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        )}
      </section>

      {/* 2. OUTREACH LOG */}
      <section>
        <h4 className="mb-3 text-lg font-semibold text-amber-200/95">Outreach log</h4>
        <div className="mb-4 flex flex-wrap items-center gap-3">
          <label className="text-xs text-gray-500">
            Sort
            <select
              value={sort}
              onChange={(e) => setSort(e.target.value as 'touch_date_desc' | 'touch_date_asc')}
              className="ml-2 rounded-lg border border-gray-600 bg-gray-800 px-3 py-2 text-sm text-white"
            >
              <option value="touch_date_desc">Newest first</option>
              <option value="touch_date_asc">Oldest first</option>
            </select>
          </label>
          <select
            value={filterChannel}
            onChange={(e) => setFilterChannel(e.target.value)}
            className="rounded-lg border border-gray-600 bg-gray-800 px-3 py-2 text-sm text-white"
          >
            <option value="">All channels</option>
            {channelOptionsForFilter.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
          <select
            value={filterResponse}
            onChange={(e) => setFilterResponse(e.target.value)}
            className="rounded-lg border border-gray-600 bg-gray-800 px-3 py-2 text-sm text-white"
          >
            <option value="">All response statuses</option>
            {responseOptionsForFilter.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
          <button
            type="button"
            onClick={() => loadLog()}
            className="rounded-lg border border-gray-600 px-3 py-2 text-sm text-gray-300 hover:bg-gray-800"
          >
            Refresh
          </button>
        </div>
        {errorLog && <p className="mb-2 text-sm text-red-400">Error: {errorLog}</p>}
        {loadingLog ? (
          <div className="py-8 text-center text-gray-400">Loading log…</div>
        ) : (
          <div className="overflow-x-auto rounded-xl border border-gray-700">
            <table className="min-w-full divide-y divide-gray-700 text-left text-sm">
              <thead className="bg-gray-800/80">
                <tr>
                  <th className="px-4 py-3 font-semibold text-gray-300">Touch date</th>
                  <th className="px-4 py-3 font-semibold text-gray-300">Company</th>
                  <th className="px-4 py-3 font-semibold text-gray-300">Contact</th>
                  <th className="px-4 py-3 font-semibold text-gray-300">#</th>
                  <th className="px-4 py-3 font-semibold text-gray-300">Channel</th>
                  <th className="px-4 py-3 font-semibold text-gray-300">Response status</th>
                  <th className="px-4 py-3 font-semibold text-gray-300">Response</th>
                  <th className="px-4 py-3 font-semibold text-gray-300">Next touch</th>
                  <th className="px-4 py-3 font-semibold text-gray-300">Notes</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-700/80">
                {outreachRows.length === 0 ? (
                  <tr>
                    <td colSpan={9} className="px-4 py-10 text-center text-gray-500">
                      No outreach rows yet.
                    </td>
                  </tr>
                ) : (
                  outreachRows.map((r) => (
                    <tr key={r.id} className="bg-gray-900/40">
                      <td className="whitespace-nowrap px-4 py-3 text-gray-300">{r.touchDate || '—'}</td>
                      <td className="px-4 py-3 text-gray-300">{r.companyName || '—'}</td>
                      <td className="px-4 py-3 text-gray-300">{r.contactName || '—'}</td>
                      <td className="px-4 py-3 text-amber-300">{r.touchNumber || '—'}</td>
                      <td className="px-4 py-3 text-gray-400">{r.channel || '—'}</td>
                      <td className="px-4 py-3 text-gray-400">{r.responseStatus || '—'}</td>
                      <td className="max-w-xs px-4 py-3 text-gray-400">
                        <span className="line-clamp-2">{r.responseReceived || '—'}</span>
                      </td>
                      <td className="whitespace-nowrap px-4 py-3 text-gray-400">{r.nextTouchDate || '—'}</td>
                      <td className="max-w-xs px-4 py-3 text-gray-500">
                        <span className="line-clamp-2">{r.notes || '—'}</span>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        )}
      </section>

      {/* Modal: AI DRAFT */}
      {aiModalOpen && (
        <>
          <button
            type="button"
            className="fixed inset-0 z-40 bg-black/60"
            aria-label="Close"
            onClick={() => setAiModalOpen(false)}
          />
          <div className="fixed left-1/2 top-1/2 z-50 max-h-[90vh] w-full max-w-2xl -translate-x-1/2 -translate-y-1/2 overflow-y-auto rounded-xl border border-violet-900/50 bg-gray-900 p-6 shadow-xl">
            <h4 className="text-lg font-bold text-white">AI email draft</h4>
            {aiTargetBuyer && (
              <p className="mt-1 text-sm text-gray-400">
                Touch {aiTargetBuyer.touchNumberDue} · {aiTargetBuyer.contactName || 'Contact'} at{' '}
                {aiTargetBuyer.companyName || 'Company'}
              </p>
            )}
            {aiError && (
              <p className="mt-3 rounded border border-red-900/50 bg-red-950/40 px-3 py-2 text-sm text-red-200">
                {aiError}
              </p>
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

      {/* Modal: NEW OUTREACH */}
      {modalOpen && (
        <>
          <button
            type="button"
            className="fixed inset-0 z-40 bg-black/60"
            aria-label="Close"
            onClick={() => setModalOpen(false)}
          />
          <div className="fixed left-1/2 top-1/2 z-50 max-h-[90vh] w-full max-w-lg -translate-x-1/2 -translate-y-1/2 overflow-y-auto rounded-xl border border-amber-900/50 bg-gray-900 p-6 shadow-xl">
            <h4 className="text-lg font-bold text-white">Log outreach</h4>
            <p className="mt-1 text-xs text-gray-500">Creates a row in JETA_Outreach and updates buyer dates.</p>
            <div className="mt-4 space-y-3">
              <label className="block text-sm text-gray-300">
                Buyer
                <select
                  value={formBuyerId}
                  onChange={(e) => setFormBuyerId(e.target.value)}
                  className="mt-1 w-full rounded-lg border border-gray-600 bg-gray-800 px-3 py-2 text-white"
                >
                  <option value="">Select buyer…</option>
                  {allBuyers.map((b) => (
                    <option key={b.id} value={b.id}>
                      {b.companyName || 'Company'} — {b.contactName || 'Contact'}
                    </option>
                  ))}
                </select>
              </label>
              <label className="block text-sm text-gray-300">
                Touch number
                <input
                  type="number"
                  min={1}
                  value={formTouchNumber}
                  onChange={(e) => setFormTouchNumber(Number(e.target.value) || 1)}
                  className="mt-1 w-full rounded-lg border border-gray-600 bg-gray-800 px-3 py-2 text-white"
                />
              </label>
              <label className="block text-sm text-gray-300">
                Channel
                <select
                  value={formChannel}
                  onChange={(e) => setFormChannel(e.target.value)}
                  className="mt-1 w-full rounded-lg border border-gray-600 bg-gray-800 px-3 py-2 text-white"
                >
                  {CHANNEL_OPTIONS.map((c) => (
                    <option key={c} value={c}>
                      {c}
                    </option>
                  ))}
                </select>
              </label>
              <label className="block text-sm text-gray-300">
                Date
                <input
                  type="date"
                  value={formTouchDate}
                  onChange={(e) => setFormTouchDate(e.target.value)}
                  className="mt-1 w-full rounded-lg border border-gray-600 bg-gray-800 px-3 py-2 text-white"
                />
              </label>
              <label className="block text-sm text-gray-300">
                Response status
                <select
                  value={formResponseStatus}
                  onChange={(e) => setFormResponseStatus(e.target.value)}
                  className="mt-1 w-full rounded-lg border border-gray-600 bg-gray-800 px-3 py-2 text-white"
                >
                  {RESPONSE_STATUS_OPTIONS.map((c) => (
                    <option key={c} value={c}>
                      {c}
                    </option>
                  ))}
                </select>
              </label>
              <label className="block text-sm text-gray-300">
                Response received
                <textarea
                  value={formResponseReceived}
                  onChange={(e) => setFormResponseReceived(e.target.value)}
                  rows={3}
                  className="mt-1 w-full rounded-lg border border-gray-600 bg-gray-800 px-3 py-2 text-white"
                  placeholder="What they said or replied…"
                />
              </label>
              <label className="block text-sm text-gray-300">
                Notes
                <textarea
                  value={formNotes}
                  onChange={(e) => setFormNotes(e.target.value)}
                  rows={2}
                  className="mt-1 w-full rounded-lg border border-gray-600 bg-gray-800 px-3 py-2 text-white"
                />
              </label>
              <label className="block text-sm text-gray-300">
                Next touch date
                <input
                  type="date"
                  value={formNextTouchDate}
                  onChange={(e) => setFormNextTouchDate(e.target.value)}
                  className="mt-1 w-full rounded-lg border border-gray-600 bg-gray-800 px-3 py-2 text-white"
                />
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
                onClick={saveOutreach}
                className="rounded-lg bg-gradient-to-r from-amber-600 to-orange-600 px-4 py-2 text-sm font-semibold text-white disabled:opacity-50"
              >
                {saving ? 'Saving…' : 'Save touch'}
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default OutreachCenterTab;
