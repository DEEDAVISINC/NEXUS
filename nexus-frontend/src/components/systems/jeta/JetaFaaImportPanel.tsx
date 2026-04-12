import React, { useCallback, useState } from 'react';
import { api } from '../../../api/client';

export interface JetaFaaImportPanelProps {
  /** After successful import, parent can refresh buyer list */
  onImportSuccess?: () => void;
  /** Narrow Buyer Pipeline to FAA + Transport Canada CSV import sources */
  onViewAllImported?: () => void;
}

type FaaImportResult = {
  success?: boolean;
  total_processed?: number;
  total_imported?: number;
  total_skipped_duplicates?: number;
  total_filtered_out?: number;
  breakdown_by_state?: Record<string, number>;
  error_log?: string[];
  supplier_enrichment_queued?: number;
  error?: string;
};

type CanadaImportResult = {
  success?: boolean;
  created?: number;
  skipped_duplicate?: number;
  skipped_filter?: number;
  skipped_invalid_icao?: number;
  errors?: number;
  breakdown_by_province?: Record<string, number>;
  error?: string;
};

const JetaFaaImportPanel: React.FC<JetaFaaImportPanelProps> = ({ onImportSuccess, onViewAllImported }) => {
  const [faaFile, setFaaFile] = useState<File | null>(null);
  const [canadaFile, setCanadaFile] = useState<File | null>(null);
  const [importingFaa, setImportingFaa] = useState(false);
  const [importingCanada, setImportingCanada] = useState(false);
  const [faaResult, setFaaResult] = useState<FaaImportResult | null>(null);
  const [canadaResult, setCanadaResult] = useState<CanadaImportResult | null>(null);
  const [faaError, setFaaError] = useState<string | null>(null);
  const [canadaError, setCanadaError] = useState<string | null>(null);

  const resetFaaSide = useCallback(() => {
    setFaaError(null);
    setFaaResult(null);
  }, []);

  const resetCanadaSide = useCallback(() => {
    setCanadaError(null);
    setCanadaResult(null);
  }, []);

  const handleFaaFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0];
    resetFaaSide();
    if (!f) {
      setFaaFile(null);
      return;
    }
    const lower = f.name.toLowerCase();
    if (!lower.endsWith('.csv') && !lower.endsWith('.txt')) {
      setFaaError('Please choose a .csv or .txt file.');
      setFaaFile(null);
      e.target.value = '';
      return;
    }
    setFaaFile(f);
  };

  const handleCanadaFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0];
    resetCanadaSide();
    if (!f) {
      setCanadaFile(null);
      return;
    }
    const lower = f.name.toLowerCase();
    if (!lower.endsWith('.csv') && !lower.endsWith('.txt')) {
      setCanadaError('Please choose a .csv or .txt file.');
      setCanadaFile(null);
      e.target.value = '';
      return;
    }
    setCanadaFile(f);
  };

  const runFaaImport = async () => {
    if (!faaFile) {
      setFaaError('Select a CSV file first.');
      return;
    }
    setImportingFaa(true);
    setFaaError(null);
    setFaaResult(null);
    try {
      const res = (await api.postJetaImportFaa(faaFile)) as FaaImportResult;
      setFaaResult(res);
      if (res.success !== false) {
        onImportSuccess?.();
      }
    } catch (e: unknown) {
      setFaaError(e instanceof Error ? e.message : 'Import request failed');
    } finally {
      setImportingFaa(false);
    }
  };

  const runCanadaImport = async () => {
    if (!canadaFile) {
      setCanadaError('Select a CSV file first.');
      return;
    }
    setImportingCanada(true);
    setCanadaError(null);
    setCanadaResult(null);
    try {
      const res = (await api.postJetaImportCanada(canadaFile)) as CanadaImportResult;
      setCanadaResult(res);
      if (res.success !== false) {
        onImportSuccess?.();
      }
    } catch (e: unknown) {
      setCanadaError(e instanceof Error ? e.message : 'Import request failed');
    } finally {
      setImportingCanada(false);
    }
  };

  const usImported = faaResult?.success !== false ? (faaResult?.total_imported ?? 0) : 0;
  const caImported = canadaResult?.success !== false ? (canadaResult?.created ?? 0) : 0;
  const hasUsRun = faaResult != null;
  const hasCaRun = canadaResult != null;
  const showResults = hasUsRun || hasCaRun;
  const combinedTotal =
    (hasUsRun && faaResult?.success !== false ? usImported : 0) +
    (hasCaRun && canadaResult?.success !== false ? caImported : 0);

  const usBreakdown = faaResult?.breakdown_by_state || {};
  const usEntries = Object.entries(usBreakdown).sort(([a], [b]) => a.localeCompare(b));
  const usMaxBar = Math.max(1, ...usEntries.map(([, n]) => n));

  const caBreakdown = canadaResult?.breakdown_by_province || {};
  const caEntries = Object.entries(caBreakdown).sort(([a], [b]) => a.localeCompare(b));
  const caMaxBar = Math.max(1, ...caEntries.map(([, n]) => n));

  const anyImporting = importingFaa || importingCanada;

  return (
    <section className="rounded-xl border border-sky-900/40 bg-gradient-to-br from-sky-950/35 to-gray-900/80 p-4 shadow-lg ring-1 ring-sky-900/25">
      <div className="mb-4">
        <h4 className="text-sm font-bold uppercase tracking-wide text-sky-200/90">Airport data import</h4>
        <p className="mt-1 text-xs text-gray-500">
          Load U.S. (FAA 5010) and Canadian aerodrome CSVs into JETA_Buyers as Stage 1 prospects.
        </p>
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        {/* LEFT — US AIRPORTS (FAA) */}
        <div className="rounded-lg border border-sky-800/40 bg-gray-950/40 p-4">
          <h5 className="text-xs font-bold uppercase tracking-wider text-sky-300/95">US airports (FAA)</h5>
          <div className="mt-3 rounded-lg border border-gray-700/80 bg-gray-950/50 p-3 text-sm leading-relaxed text-gray-300">
            <p className="text-[10px] font-semibold uppercase tracking-wide text-gray-500">Instructions</p>
            <p className="mt-2 text-xs">
              Download FAA Airport Master Record (5010) from{' '}
              <a
                href="https://www.faa.gov/airports/airport_safety/airportdata_5010"
                target="_blank"
                rel="noopener noreferrer"
                className="text-sky-400 underline-offset-2 hover:underline"
              >
                faa.gov/airports/airport_safety/airportdata_5010
              </a>
              — all 50 states included.
            </p>
          </div>
          <div className="mt-3">
            <label className="block text-xs font-medium text-gray-400">CSV file</label>
            <input
              type="file"
              accept=".csv,.txt,text/csv,text/plain"
              disabled={importingFaa}
              onChange={handleFaaFileChange}
              className="mt-2 block w-full text-sm text-gray-300 file:mr-3 file:rounded-md file:border-0 file:bg-sky-800 file:px-3 file:py-2 file:text-sm file:font-semibold file:text-sky-100 hover:file:bg-sky-700"
            />
            {faaFile ? (
              <p className="mt-2 text-xs text-gray-500">
                Selected: <span className="text-gray-300">{faaFile.name}</span>
              </p>
            ) : null}
          </div>
          {faaError && <p className="mt-2 text-sm text-red-300">{faaError}</p>}
          {faaResult?.success === false && faaResult?.error && (
            <p className="mt-2 text-sm text-red-300">{faaResult.error}</p>
          )}
          <button
            type="button"
            disabled={importingFaa || !faaFile}
            onClick={runFaaImport}
            className="mt-4 w-full rounded-lg bg-gradient-to-r from-sky-600 to-cyan-700 px-4 py-2.5 text-sm font-semibold text-white shadow disabled:opacity-50"
          >
            {importingFaa ? (
              <span className="inline-flex items-center justify-center gap-2">
                <span className="h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white" />
                Importing…
              </span>
            ) : (
              'Import US airports'
            )}
          </button>
        </div>

        {/* RIGHT — CANADA */}
        <div className="rounded-lg border border-emerald-900/35 bg-gray-950/40 p-4">
          <h5 className="text-xs font-bold uppercase tracking-wider text-emerald-300/95">Canada airports</h5>
          <div className="mt-3 rounded-lg border border-gray-700/80 bg-gray-950/50 p-3 text-sm leading-relaxed text-gray-300">
            <p className="text-[10px] font-semibold uppercase tracking-wide text-gray-500">Instructions</p>
            <p className="mt-2 text-xs">
              Download airport data from NAV CANADA or Transport Canada aerodrome directory, then upload the CSV here.
            </p>
          </div>
          <div className="mt-3">
            <label className="block text-xs font-medium text-gray-400">CSV file</label>
            <input
              type="file"
              accept=".csv,.txt,text/csv,text/plain"
              disabled={importingCanada}
              onChange={handleCanadaFileChange}
              className="mt-2 block w-full text-sm text-gray-300 file:mr-3 file:rounded-md file:border-0 file:bg-emerald-900 file:px-3 file:py-2 file:text-sm file:font-semibold file:text-emerald-100 hover:file:bg-emerald-800"
            />
            {canadaFile ? (
              <p className="mt-2 text-xs text-gray-500">
                Selected: <span className="text-gray-300">{canadaFile.name}</span>
              </p>
            ) : null}
          </div>
          {canadaError && <p className="mt-2 text-sm text-red-300">{canadaError}</p>}
          {canadaResult?.success === false && canadaResult?.error && (
            <p className="mt-2 text-sm text-red-300">{canadaResult.error}</p>
          )}
          <button
            type="button"
            disabled={importingCanada || !canadaFile}
            onClick={runCanadaImport}
            className="mt-4 w-full rounded-lg bg-gradient-to-r from-emerald-700 to-teal-800 px-4 py-2.5 text-sm font-semibold text-white shadow disabled:opacity-50"
          >
            {importingCanada ? (
              <span className="inline-flex items-center justify-center gap-2">
                <span className="h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white" />
                Importing…
              </span>
            ) : (
              'Import Canada airports'
            )}
          </button>
        </div>
      </div>

      {/* RESULTS — below both sections */}
      {showResults && (
        <div className="mt-6 space-y-4 border-t border-gray-700/80 pt-6">
          <p className="text-xs font-bold uppercase tracking-wide text-gray-500">Results</p>

          <div className="grid gap-4 md:grid-cols-2">
            <div className="rounded-lg border border-sky-900/40 bg-gray-950/30 p-4">
              <p className="text-[11px] font-semibold uppercase tracking-wide text-sky-400/90">US airports (by state)</p>
              {hasUsRun && faaResult?.success !== false ? (
                <>
                  <p className="mt-2 text-2xl font-bold tabular-nums text-emerald-400">{usImported}</p>
                  <p className="text-xs text-gray-500">imported this run</p>
                  {(faaResult?.supplier_enrichment_queued ?? 0) > 0 && (
                    <p className="mt-2 text-xs text-sky-300/90">
                      {faaResult?.supplier_enrichment_queued} supplier lookup(s) queued (runs in background).
                    </p>
                  )}
                  {usEntries.length > 0 && (
                    <div className="mt-3 space-y-2">
                      <p className="text-[10px] font-medium uppercase text-gray-600">Breakdown</p>
                      {usEntries.map(([st, n]) => (
                        <div key={st} className="flex items-center gap-2 text-xs">
                          <span className="w-9 shrink-0 font-mono text-gray-500">{st}</span>
                          <div className="h-2 min-w-0 flex-1 rounded bg-gray-800">
                            <div
                              className="h-2 rounded bg-amber-600"
                              style={{ width: `${(n / usMaxBar) * 100}%` }}
                            />
                          </div>
                          <span className="w-8 shrink-0 text-right tabular-nums text-gray-400">{n}</span>
                        </div>
                      ))}
                    </div>
                  )}
                  {(faaResult?.error_log?.length ?? 0) > 0 && (
                    <details className="mt-3 rounded border border-gray-700 bg-black/20 p-2 text-[11px]">
                      <summary className="cursor-pointer text-gray-500">
                        US error log ({faaResult?.error_log?.length})
                      </summary>
                      <ul className="mt-2 max-h-24 list-inside list-disc overflow-y-auto text-gray-500">
                        {(faaResult?.error_log || []).slice(0, 30).map((line, i) => (
                          <li key={i}>{line}</li>
                        ))}
                      </ul>
                    </details>
                  )}
                </>
              ) : hasUsRun ? (
                <p className="mt-2 text-sm text-red-300/90">US import did not complete successfully.</p>
              ) : (
                <p className="mt-2 text-xs text-gray-600">No US import in this session yet.</p>
              )}
            </div>

            <div className="rounded-lg border border-emerald-900/35 bg-gray-950/30 p-4">
              <p className="text-[11px] font-semibold uppercase tracking-wide text-emerald-400/90">
                Canadian airports (by province)
              </p>
              {hasCaRun && canadaResult?.success !== false ? (
                <>
                  <p className="mt-2 text-2xl font-bold tabular-nums text-emerald-400">{caImported}</p>
                  <p className="text-xs text-gray-500">imported this run</p>
                  {caEntries.length > 0 && (
                    <div className="mt-3 space-y-2">
                      <p className="text-[10px] font-medium uppercase text-gray-600">Breakdown</p>
                      {caEntries.map(([prov, n]) => (
                        <div key={prov} className="flex items-center gap-2 text-xs">
                          <span className="min-w-[2.5rem] shrink-0 font-mono text-gray-500">{prov}</span>
                          <div className="h-2 min-w-0 flex-1 rounded bg-gray-800">
                            <div
                              className="h-2 rounded bg-emerald-600"
                              style={{ width: `${(n / caMaxBar) * 100}%` }}
                            />
                          </div>
                          <span className="w-8 shrink-0 text-right tabular-nums text-gray-400">{n}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </>
              ) : hasCaRun ? (
                <p className="mt-2 text-sm text-red-300/90">Canada import did not complete successfully.</p>
              ) : (
                <p className="mt-2 text-xs text-gray-600">No Canada import in this session yet.</p>
              )}
            </div>
          </div>

          <div className="flex flex-col items-stretch gap-3 rounded-lg border border-amber-900/30 bg-amber-950/15 px-4 py-4 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <p className="text-[11px] font-semibold uppercase tracking-wide text-amber-200/80">Combined total</p>
              <p className="mt-1 text-xl font-bold tabular-nums text-amber-100">
                {combinedTotal}{' '}
                <span className="text-sm font-normal text-gray-400">prospects loaded (this session)</span>
              </p>
            </div>
            <button
              type="button"
              disabled={anyImporting}
              onClick={() => onViewAllImported?.()}
              className="shrink-0 rounded-lg border border-amber-700/60 bg-amber-950/40 px-5 py-2.5 text-sm font-semibold text-amber-100 hover:bg-amber-900/50 disabled:opacity-50"
            >
              View all imported records
            </button>
          </div>
        </div>
      )}
    </section>
  );
};

export default JetaFaaImportPanel;
