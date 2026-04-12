import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { api } from '../../../api/client';
import type { JetaDeal } from './DealManagerTab';

const API_BASE = process.env.REACT_APP_API_BASE || 'http://127.0.0.1:8000';

const DOC_TYPES = ['NCNDA', 'IMFPA', 'Fee Agreement', 'LOA'] as const;

function parseTermDaysFromDeal(termLength: string | undefined): number | null {
  if (!termLength?.trim()) return null;
  const s = termLength.trim().toLowerCase();
  const dm = s.match(/(\d+(?:\.\d+)?)\s*days?/i);
  if (dm) return Math.round(parseFloat(dm[1]));
  const wm = s.match(/(\d+(?:\.\d+)?)\s*weeks?/i);
  if (wm) return Math.round(parseFloat(wm[1]) * 7);
  const mm = s.match(/(\d+(?:\.\d+)?)\s*months?/i);
  if (mm) return Math.round(parseFloat(mm[1]) * 30.4375);
  const ym = s.match(/(\d+(?:\.\d+)?)\s*years?/i);
  if (ym) return Math.round(parseFloat(ym[1]) * 365.25);
  if (/^\d+$/.test(s)) return parseInt(s, 10);
  return null;
}

/** Mirrors api_server jeta_fee_escalation.select_escalation_clause_version */
function inferEscalationClauseLabel(deal: { dealType?: string; termLength?: string } | null): string {
  if (!deal) return '—';
  const dt = (deal.dealType || '').trim().toLowerCase();
  if (dt === 'spot') return 'Version B — Market price adjustment (spot)';
  const days = parseTermDaysFromDeal(deal.termLength);
  if (days == null) return 'Version A — Fuel price escalation (default; set Term Length for &gt;90d → C)';
  return days > 90
    ? 'Version C — Multi-year provision'
    : 'Version A — Fuel price escalation (≤90 days)';
}

export interface JetaDocumentRow {
  id: string;
  documentType: string;
  dealId: string;
  buyerName: string;
  generatedDate: string;
  signedStatus: string;
  downloadUrl: string;
  pdfPath?: string;
  createdTime?: string;
  /** Fee Agreement only — Version A / B / C */
  escalationClauseVersion?: string | null;
}

const DocumentsTab: React.FC = () => {
  const [documents, setDocuments] = useState<JetaDocumentRow[]>([]);
  const [deals, setDeals] = useState<JetaDeal[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [hint, setHint] = useState<string | null>(null);

  const [modalOpen, setModalOpen] = useState(false);
  const [docType, setDocType] = useState<string>(DOC_TYPES[0]);
  const [dealId, setDealId] = useState('');
  const [generating, setGenerating] = useState(false);
  const [genError, setGenError] = useState<string | null>(null);

  const loadDocs = useCallback(async () => {
    setLoading(true);
    setError(null);
    setHint(null);
    try {
      const res = (await api.getJetaDocuments()) as {
        success?: boolean;
        documents?: JetaDocumentRow[];
        error?: string;
        hint?: string;
      };
      if (res.hint) setHint(res.hint);
      if (res.success === false && res.error) setError(res.error);
      else setDocuments(res.documents || []);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Failed to load documents');
      setDocuments([]);
    } finally {
      setLoading(false);
    }
  }, []);

  const loadDeals = useCallback(async () => {
    try {
      const res = (await api.getJetaDeals()) as { deals?: JetaDeal[] };
      setDeals(res.deals || []);
    } catch {
      setDeals([]);
    }
  }, []);

  useEffect(() => {
    loadDocs();
    loadDeals();
  }, [loadDocs, loadDeals]);

  const selectedDeal = useMemo(() => deals.find((d) => d.id === dealId) || null, [deals, dealId]);

  const openGenerate = () => {
    setDocType(DOC_TYPES[0]);
    setDealId(deals[0]?.id || '');
    setGenError(null);
    setModalOpen(true);
  };

  const runGenerate = async () => {
    if (!dealId) {
      setGenError('Select a deal.');
      return;
    }
    setGenerating(true);
    setGenError(null);
    try {
      const res = (await api.postJetaDocumentsGenerate({
        dealId,
        documentType: docType,
      })) as {
        success?: boolean;
        error?: string;
        downloadUrl?: string;
        document?: JetaDocumentRow;
        escalationClauseVersion?: string;
        escalation_base_benchmark_bbl?: number;
      };
      if (res.success === false) {
        setGenError(res.error || 'Generation failed');
        return;
      }
      setModalOpen(false);
      await loadDocs();
      await loadDeals();
      const path = res.downloadUrl || res.document?.downloadUrl;
      if (path) {
        window.open(`${API_BASE}${path}`, '_blank', 'noopener,noreferrer');
      }
    } catch (e: unknown) {
      setGenError(e instanceof Error ? e.message : 'Generation failed');
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div className="relative min-h-[420px]">
      <div className="mb-6 flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h3 className="text-xl font-bold text-white">Documents</h3>
          <p className="text-sm text-gray-400">Airtable · JETA_Documents · PDF generation (reportlab)</p>
        </div>
        <button
          type="button"
          onClick={openGenerate}
          className="rounded-lg bg-gradient-to-r from-amber-600 to-orange-600 px-4 py-2 text-sm font-semibold text-white shadow hover:from-amber-500 hover:to-orange-500"
        >
          Generate document
        </button>
      </div>

      {(error || hint) && (
        <div className="mb-4 rounded-lg border border-amber-700/50 bg-amber-950/40 px-4 py-3 text-sm text-amber-100">
          {error && <p className="font-medium text-amber-200">Error: {error}</p>}
          {hint && <p className="mt-1 text-amber-100/90">{hint}</p>}
        </div>
      )}

      <div className="overflow-x-auto rounded-xl border border-gray-700">
        <table className="min-w-full divide-y divide-gray-700 text-left text-sm">
          <thead className="bg-gray-800/80">
            <tr>
              <th className="px-4 py-3 font-semibold text-gray-300">Document type</th>
              <th className="px-4 py-3 font-semibold text-gray-300">Deal ID</th>
              <th className="px-4 py-3 font-semibold text-gray-300">Buyer</th>
              <th className="px-4 py-3 font-semibold text-gray-300">Generated date</th>
              <th className="px-4 py-3 font-semibold text-gray-300">Signed status</th>
              <th className="px-4 py-3 font-semibold text-gray-300">Escalation</th>
              <th className="px-4 py-3 font-semibold text-gray-300">Download</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-700/80">
            {loading ? (
              <tr>
                <td colSpan={7} className="px-4 py-12 text-center text-gray-500">
                  Loading…
                </td>
              </tr>
            ) : documents.length === 0 ? (
              <tr>
                <td colSpan={7} className="px-4 py-12 text-center text-gray-500">
                  No documents yet. Use <strong>Generate document</strong> (creates a row in{' '}
                  <code className="text-gray-400">JETA_Documents</code> and saves a PDF).
                </td>
              </tr>
            ) : (
              documents.map((row) => (
                <tr key={row.id} className="bg-gray-900/40">
                  <td className="px-4 py-3 font-medium text-white">{row.documentType || '—'}</td>
                  <td className="px-4 py-3 font-mono text-xs text-gray-400">
                    <span title={row.dealId}>{row.dealId ? `${row.dealId.slice(0, 12)}…` : '—'}</span>
                  </td>
                  <td className="max-w-xs truncate px-4 py-3 text-gray-300">{row.buyerName || '—'}</td>
                  <td className="whitespace-nowrap px-4 py-3 text-gray-400">{row.generatedDate || '—'}</td>
                  <td className="px-4 py-3 text-gray-400">{row.signedStatus || '—'}</td>
                  <td className="max-w-[10rem] truncate px-4 py-3 text-xs text-amber-200/90" title={row.escalationClauseVersion || ''}>
                    {row.documentType === 'Fee Agreement' ? row.escalationClauseVersion || '—' : '—'}
                  </td>
                  <td className="px-4 py-3">
                    {row.downloadUrl ? (
                      <a
                        href={`${API_BASE}${row.downloadUrl}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="font-semibold text-amber-400 hover:text-amber-300"
                      >
                        PDF
                      </a>
                    ) : (
                      '—'
                    )}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {modalOpen && (
        <>
          <button
            type="button"
            className="fixed inset-0 z-40 bg-black/60"
            aria-label="Close"
            onClick={() => setModalOpen(false)}
          />
          <div className="fixed left-1/2 top-1/2 z-50 max-h-[90vh] w-full max-w-lg -translate-x-1/2 -translate-y-1/2 overflow-y-auto rounded-xl border border-amber-900/50 bg-gray-900 p-6 shadow-xl">
            <h4 className="text-lg font-bold text-white">Generate document</h4>
            <p className="mt-1 text-xs text-gray-500">
              POST <code className="text-gray-400">/jeta/documents/generate</code> (also{' '}
              <code className="text-gray-400">/api/jeta/documents/generate</code>). NCNDA uses Party 1 as JETA /
              DEE DAVIS INC (Troy, MI), Party 2 from the buyer, today&apos;s date, and deal description.
            </p>

            <div className="mt-4 space-y-3">
              <label className="block text-sm text-gray-300">
                Document type
                <select
                  value={docType}
                  onChange={(e) => setDocType(e.target.value)}
                  className="mt-1 w-full rounded-lg border border-gray-600 bg-gray-800 px-3 py-2 text-white"
                >
                  {DOC_TYPES.map((t) => (
                    <option key={t} value={t}>
                      {t}
                    </option>
                  ))}
                </select>
              </label>
              <label className="block text-sm text-gray-300">
                Deal <span className="text-red-400">*</span>
                <select
                  value={dealId}
                  onChange={(e) => setDealId(e.target.value)}
                  className="mt-1 w-full rounded-lg border border-gray-600 bg-gray-800 px-3 py-2 text-white"
                >
                  <option value="">Select deal…</option>
                  {deals.map((d) => (
                    <option key={d.id} value={d.id}>
                      {d.dealName?.trim() || d.buyerName || d.id.slice(0, 8)} — {d.dealStage}
                    </option>
                  ))}
                </select>
              </label>

              {selectedDeal && (
                <div className="rounded-lg border border-gray-700 bg-gray-800/50 p-3 text-xs text-gray-400">
                  <p>
                    <span className="text-gray-500">Buyer:</span>{' '}
                    <span className="text-gray-200">{selectedDeal.buyerName || '—'}</span>
                  </p>
                  <p className="mt-1">
                    <span className="text-gray-500">Deal:</span>{' '}
                    <span className="text-gray-200">{selectedDeal.dealName?.trim() || '—'}</span>
                  </p>
                  <p className="mt-1">
                    <span className="text-gray-500">Description (into PDF):</span>
                  </p>
                  <p className="mt-0.5 text-gray-300">
                    {selectedDeal.dealDescription?.trim() || '— (add Deal Description on the deal in Airtable)'}
                  </p>
                  {docType === 'Fee Agreement' && (
                    <div className="mt-3 border-t border-amber-900/40 pt-3">
                      <p className="text-[10px] font-semibold uppercase tracking-wide text-amber-400/95">
                        Step — Escalation clause (auto)
                      </p>
                      <p className="mt-1 text-amber-100/90">{inferEscalationClauseLabel(selectedDeal)}</p>
                      <p className="mt-1 text-[10px] text-gray-500">
                        Uses <span className="text-gray-400">Deal Type</span> = Spot → B; else{' '}
                        <span className="text-gray-400">Term Length</span> ≤90 days → A, &gt;90 → C. Base benchmark =
                        latest IATA $/bbl from JETA_MarketData; base fee = JETA Fee Per Gallon on the deal.
                      </p>
                    </div>
                  )}
                </div>
              )}
            </div>

            {genError && (
              <p className="mt-3 rounded border border-red-900/50 bg-red-950/40 px-3 py-2 text-sm text-red-200">
                {genError}
              </p>
            )}

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
                disabled={generating || !dealId}
                onClick={runGenerate}
                className="rounded-lg bg-gradient-to-r from-amber-600 to-orange-600 px-4 py-2 text-sm font-semibold text-white disabled:opacity-50"
              >
                {generating ? 'Generating…' : 'Generate PDF'}
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default DocumentsTab;
