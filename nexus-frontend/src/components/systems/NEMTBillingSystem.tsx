import React, { useCallback, useEffect, useState } from 'react';
import { api } from '../../api/client';

/**
 * VERTEX NEMT Medical Billing — embedded in VERTEXSystem (not standalone).
 * Trip log (local JSON) → claims on VERTEX INVOICES → ERA payment → VERTEX REVENUE.
 * HCPCS rates: Airtable table "NEMT RATES" (managed below).
 */

type RateRow = {
  id: string;
  hcpcs_code: string;
  description: string;
  rate_amount: number;
};

const defaultTripForm = {
  member_medicaid_id: '',
  pickup_time: '',
  dropoff_time: '',
  pickup_address: '',
  dropoff_address: '',
  mileage: 0,
  trip_purpose: '',
  hcpcs_code: '',
  payer: 'HAP CareSource',
};

const defaultPaymentForm = {
  invoice_id: '',
  amount: 0,
  payment_date: new Date().toISOString().split('T')[0],
  era_reference: '',
  notes: '',
};

const NEMTBillingSystem: React.FC = () => {
  const [tripForm, setTripForm] = useState(defaultTripForm);
  const [paymentForm, setPaymentForm] = useState(defaultPaymentForm);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<{ type: 'ok' | 'err'; text: string } | null>(null);

  const [pendingClaims, setPendingClaims] = useState<any[]>([]);
  const [loggedTrips, setLoggedTrips] = useState<any[]>([]);
  const [summary, setSummary] = useState<any>(null);
  const [rateRows, setRateRows] = useState<RateRow[]>([]);
  const [rateDrafts, setRateDrafts] = useState<Record<string, { hcpcs_code: string; description: string; rate_amount: string }>>({});
  const [selectedTripId, setSelectedTripId] = useState('');

  const refresh = useCallback(async () => {
    setLoading(true);
    try {
      const data = await api.vertexNemtPendingClaims();
      setPendingClaims(data.pending_claims || []);
      setLoggedTrips(data.logged_trips || []);
      setSummary(data.summary || null);
      const rows: RateRow[] = Array.isArray(data.rates) ? data.rates : [];
      setRateRows(rows);
    } catch (e) {
      console.error(e);
      setMessage({ type: 'err', text: 'Failed to load NEMT data (check Airtable NEMT RATES table exists).' });
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  useEffect(() => {
    const next: Record<string, { hcpcs_code: string; description: string; rate_amount: string }> = {};
    rateRows.forEach((r) => {
      if (r.id) {
        next[r.id] = {
          hcpcs_code: r.hcpcs_code || '',
          description: r.description || '',
          rate_amount: String(r.rate_amount ?? 0),
        };
      }
    });
    setRateDrafts(next);
  }, [rateRows]);

  useEffect(() => {
    if (rateRows.length === 0) return;
    const codes = new Set(rateRows.map((r) => r.hcpcs_code));
    setTripForm((f) => {
      if (f.hcpcs_code && codes.has(f.hcpcs_code)) return f;
      return { ...f, hcpcs_code: rateRows[0].hcpcs_code };
    });
  }, [rateRows]);

  const show = (text: string, ok = true) => {
    setMessage({ type: ok ? 'ok' : 'err', text });
    setTimeout(() => setMessage(null), 5000);
  };

  const seedPlaceholderRates = async () => {
    setLoading(true);
    try {
      const res = await api.vertexNemtSeedRates();
      if (res.error || res.success === false) {
        show(res.error || 'Seed failed', false);
        return;
      }
      const n = res.created_count ?? 0;
      show(n ? `Seeded ${n} placeholder row(s) at $0.00` : 'All placeholder HCPCS rows already exist');
      await refresh();
    } catch (err: any) {
      show(err?.message || 'Seed failed — ensure Airtable table "NEMT RATES" exists with HCPCS Code, Description, Rate Amount', false);
    } finally {
      setLoading(false);
    }
  };

  const saveRateRow = async (recordId: string) => {
    const d = rateDrafts[recordId];
    if (!d) return;
    const amt = parseFloat(d.rate_amount);
    if (Number.isNaN(amt) || amt < 0) {
      show('Enter a valid rate amount', false);
      return;
    }
    setLoading(true);
    try {
      const res = await api.vertexNemtUpdateRate(recordId, {
        hcpcs_code: d.hcpcs_code.trim(),
        description: d.description.trim(),
        rate_amount: amt,
      });
      if (res.error || res.success === false) {
        show(res.error || 'Update failed', false);
        return;
      }
      show('Rate saved to Airtable');
      await refresh();
    } catch (err: any) {
      show(err?.message || 'Update failed', false);
    } finally {
      setLoading(false);
    }
  };

  const submitTrip = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await api.vertexNemtLogTrip({
        member_medicaid_id: tripForm.member_medicaid_id,
        pickup_time: tripForm.pickup_time,
        dropoff_time: tripForm.dropoff_time,
        pickup_address: tripForm.pickup_address,
        dropoff_address: tripForm.dropoff_address,
        mileage: tripForm.mileage,
        trip_purpose: tripForm.trip_purpose,
        hcpcs_code: tripForm.hcpcs_code,
        payer: tripForm.payer || 'HAP CareSource',
      });
      if (res.error || res.success === false) {
        show(res.error || 'Log failed', false);
        return;
      }
      show('Trip logged');
      setTripForm(defaultTripForm);
      await refresh();
    } catch (err: any) {
      show(err?.message || 'Request failed', false);
    } finally {
      setLoading(false);
    }
  };

  const generateClaim = async () => {
    if (!selectedTripId) {
      show('Select a trip', false);
      return;
    }
    setLoading(true);
    try {
      const res = await api.vertexNemtGenerateClaim({ trip_id: selectedTripId });
      if (res.error || res.success === false) {
        show(res.error || 'Claim failed', false);
        return;
      }
      show('Claim created in VERTEX INVOICES');
      setSelectedTripId('');
      await refresh();
    } catch (err: any) {
      show(err?.message || 'Request failed', false);
    } finally {
      setLoading(false);
    }
  };

  const postPayment = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!paymentForm.invoice_id.trim()) {
      show('Invoice record ID required', false);
      return;
    }
    setLoading(true);
    try {
      const res = await api.vertexNemtPostPayment({
        invoice_id: paymentForm.invoice_id.trim(),
        amount: paymentForm.amount,
        payment_date: paymentForm.payment_date,
        era_reference: paymentForm.era_reference || undefined,
        notes: paymentForm.notes || undefined,
      });
      if (res.error || res.success === false) {
        show(res.error || 'Payment post failed', false);
        return;
      }
      show('Payment posted — invoice Paid, VERTEX REVENUE created');
      setPaymentForm({ ...defaultPaymentForm });
      await refresh();
    } catch (err: any) {
      show(err?.message || 'Request failed', false);
    } finally {
      setLoading(false);
    }
  };

  const unclaimedTrips = loggedTrips.filter((t) => t.status === 'logged');

  const totalBilledOutstanding =
    summary?.total_billed_all_claims != null && summary?.total_received != null
      ? Math.max(0, (summary.total_billed_all_claims || 0) - (summary.total_received || 0))
      : null;

  return (
    <div className="space-y-8">
      {message && (
        <div
          className={`px-4 py-3 rounded-lg ${
            message.type === 'ok' ? 'bg-green-900/50 text-green-200' : 'bg-red-900/50 text-red-200'
          }`}
        >
          {message.text}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-gray-800/80 rounded-xl p-4 border border-purple-700/40">
          <div className="text-sm text-gray-400">Pending AR (unpaid NEMT)</div>
          <div className="text-2xl font-bold text-white">
            ${summary?.total_billed_pending?.toFixed(2) ?? '—'}
          </div>
        </div>
        <div className="bg-gray-800/80 rounded-xl p-4 border border-purple-700/40">
          <div className="text-sm text-gray-400">Total received (VERTEX REVENUE)</div>
          <div className="text-2xl font-bold text-emerald-400">
            ${summary?.total_received?.toFixed(2) ?? '—'}
          </div>
        </div>
        <div className="bg-gray-800/80 rounded-xl p-4 border border-purple-700/40">
          <div className="text-sm text-gray-400">Lifetime billed (all NEMT claims)</div>
          <div className="text-2xl font-bold text-purple-300">
            ${summary?.total_billed_all_claims?.toFixed(2) ?? '—'}
          </div>
          {totalBilledOutstanding != null && (
            <div className="text-xs text-gray-500 mt-1">
              Outstanding vs received (approx.): ${totalBilledOutstanding.toFixed(2)}
            </div>
          )}
        </div>
      </div>

      <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
        <div className="flex flex-wrap items-start justify-between gap-4 mb-4">
          <div>
            <h3 className="text-lg font-semibold text-white">Rates management (Airtable: NEMT RATES)</h3>
            <p className="text-sm text-gray-400 mt-1 max-w-3xl">
              Rates are read at billing time from the NEMT RATES table (fields: HCPCS Code, Description, Rate Amount).
              First-time: create that table in Airtable, then use &quot;Seed placeholders&quot; to add T2002 / A0130 / A0380 at
              $0.00 — update amounts here after you review the HAP CareSource contract.
            </p>
          </div>
          <button
            type="button"
            onClick={seedPlaceholderRates}
            disabled={loading}
            className="shrink-0 px-4 py-2 rounded-lg bg-amber-700/80 hover:bg-amber-600 text-white text-sm font-medium disabled:opacity-50"
          >
            Seed placeholders ($0.00)
          </button>
        </div>
        {rateRows.length === 0 && !loading && (
          <p className="text-amber-200/90 text-sm mb-4">No rate rows loaded. Seed placeholders or add rows in Airtable.</p>
        )}
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left min-w-[640px]">
            <thead>
              <tr className="text-gray-400 border-b border-gray-600">
                <th className="py-2 pr-3">HCPCS</th>
                <th className="py-2 pr-3">Description</th>
                <th className="py-2 pr-3">Rate ($)</th>
                <th className="py-2">Actions</th>
              </tr>
            </thead>
            <tbody>
              {rateRows.map((row) => {
                const draft = rateDrafts[row.id] || {
                  hcpcs_code: row.hcpcs_code,
                  description: row.description,
                  rate_amount: String(row.rate_amount ?? 0),
                };
                return (
                  <tr key={row.id} className="border-b border-gray-700/50">
                    <td className="py-2 pr-2">
                      <input
                        className="w-28 bg-gray-900 border border-gray-600 rounded px-2 py-1.5 text-white font-mono text-xs"
                        value={draft.hcpcs_code}
                        onChange={(e) =>
                          setRateDrafts((prev) => ({
                            ...prev,
                            [row.id]: { ...draft, hcpcs_code: e.target.value.toUpperCase() },
                          }))
                        }
                      />
                    </td>
                    <td className="py-2 pr-2">
                      <input
                        className="w-full min-w-[180px] bg-gray-900 border border-gray-600 rounded px-2 py-1.5 text-white"
                        value={draft.description}
                        onChange={(e) =>
                          setRateDrafts((prev) => ({
                            ...prev,
                            [row.id]: { ...draft, description: e.target.value },
                          }))
                        }
                      />
                    </td>
                    <td className="py-2 pr-2">
                      <input
                        type="number"
                        step="0.01"
                        min={0}
                        className="w-32 bg-gray-900 border border-gray-600 rounded px-2 py-1.5 text-white"
                        value={draft.rate_amount}
                        onChange={(e) =>
                          setRateDrafts((prev) => ({
                            ...prev,
                            [row.id]: { ...draft, rate_amount: e.target.value },
                          }))
                        }
                      />
                    </td>
                    <td className="py-2">
                      <button
                        type="button"
                        onClick={() => saveRateRow(row.id)}
                        disabled={loading}
                        className="px-3 py-1.5 rounded-lg bg-purple-600 hover:bg-purple-500 text-white text-xs font-medium disabled:opacity-50"
                      >
                        Save
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
          <h2 className="text-xl font-bold text-white mb-4">Log completed trip</h2>
          <form onSubmit={submitTrip} className="space-y-3">
            <label className="block text-sm text-gray-400">Member Medicaid ID</label>
            <input
              className="w-full bg-gray-900 border border-gray-600 rounded px-3 py-2 text-white"
              value={tripForm.member_medicaid_id}
              onChange={(e) => setTripForm({ ...tripForm, member_medicaid_id: e.target.value })}
              required
            />
            <div className="grid grid-cols-2 gap-2">
              <div>
                <label className="block text-sm text-gray-400">Pickup (ISO datetime)</label>
                <input
                  className="w-full bg-gray-900 border border-gray-600 rounded px-3 py-2 text-white text-sm"
                  value={tripForm.pickup_time}
                  onChange={(e) => setTripForm({ ...tripForm, pickup_time: e.target.value })}
                  placeholder="2026-03-27T14:00:00"
                  required
                />
              </div>
              <div>
                <label className="block text-sm text-gray-400">Dropoff</label>
                <input
                  className="w-full bg-gray-900 border border-gray-600 rounded px-3 py-2 text-white text-sm"
                  value={tripForm.dropoff_time}
                  onChange={(e) => setTripForm({ ...tripForm, dropoff_time: e.target.value })}
                  required
                />
              </div>
            </div>
            <label className="block text-sm text-gray-400">Pickup address</label>
            <input
              className="w-full bg-gray-900 border border-gray-600 rounded px-3 py-2 text-white"
              value={tripForm.pickup_address}
              onChange={(e) => setTripForm({ ...tripForm, pickup_address: e.target.value })}
              required
            />
            <label className="block text-sm text-gray-400">Dropoff address</label>
            <input
              className="w-full bg-gray-900 border border-gray-600 rounded px-3 py-2 text-white"
              value={tripForm.dropoff_address}
              onChange={(e) => setTripForm({ ...tripForm, dropoff_address: e.target.value })}
              required
            />
            <div className="grid grid-cols-2 gap-2">
              <div>
                <label className="block text-sm text-gray-400">Mileage</label>
                <input
                  type="number"
                  step="0.1"
                  className="w-full bg-gray-900 border border-gray-600 rounded px-3 py-2 text-white"
                  value={tripForm.mileage}
                  onChange={(e) => setTripForm({ ...tripForm, mileage: parseFloat(e.target.value) || 0 })}
                />
              </div>
              <div>
                <label className="block text-sm text-gray-400">HCPCS (from NEMT RATES)</label>
                <select
                  className="w-full bg-gray-900 border border-gray-600 rounded px-3 py-2 text-white"
                  value={tripForm.hcpcs_code}
                  onChange={(e) => setTripForm({ ...tripForm, hcpcs_code: e.target.value })}
                  required
                  disabled={rateRows.length === 0}
                >
                  {rateRows.length === 0 ? (
                    <option value="">— Add or seed rates first —</option>
                  ) : (
                    rateRows.map((r) => (
                      <option key={r.id} value={r.hcpcs_code}>
                        {r.hcpcs_code} — {r.description} (${Number(r.rate_amount).toFixed(2)})
                      </option>
                    ))
                  )}
                </select>
              </div>
            </div>
            <label className="block text-sm text-gray-400">Trip purpose</label>
            <input
              className="w-full bg-gray-900 border border-gray-600 rounded px-3 py-2 text-white"
              value={tripForm.trip_purpose}
              onChange={(e) => setTripForm({ ...tripForm, trip_purpose: e.target.value })}
              required
            />
            <label className="block text-sm text-gray-400">Payer</label>
            <input
              className="w-full bg-gray-900 border border-gray-600 rounded px-3 py-2 text-white"
              value={tripForm.payer}
              onChange={(e) => setTripForm({ ...tripForm, payer: e.target.value })}
            />
            <button
              type="submit"
              disabled={loading}
              className="w-full py-2 rounded-lg bg-gradient-to-r from-purple-600 to-pink-600 text-white font-medium disabled:opacity-50"
            >
              {loading ? 'Working…' : 'Log trip'}
            </button>
          </form>
        </div>

        <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
          <h2 className="text-xl font-bold text-white mb-4">Generate claim (VERTEX INVOICES)</h2>
          <p className="text-sm text-gray-400 mb-3">
            Provider NPI and CHAMPS ID are applied from company_info on the server.
          </p>
          <label className="block text-sm text-gray-400 mb-1">Trip not yet claimed</label>
          <select
            className="w-full bg-gray-900 border border-gray-600 rounded px-3 py-2 text-white mb-3"
            value={selectedTripId}
            onChange={(e) => setSelectedTripId(e.target.value)}
          >
            <option value="">— Select trip —</option>
            {unclaimedTrips.map((t) => (
              <option key={t.trip_id} value={t.trip_id}>
                {t.trip_id.slice(0, 8)}… · {t.hcpcs_code} · {t.trip_purpose?.slice(0, 40)}
              </option>
            ))}
          </select>
          <button
            type="button"
            onClick={generateClaim}
            disabled={loading || !selectedTripId}
            className="w-full py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-medium disabled:opacity-50"
          >
            Generate CMS-1500-style claim
          </button>
        </div>
      </div>

      <div className="bg-gray-800 rounded-xl p-6 border border-gray-700 overflow-x-auto">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold text-white">Pending claims</h2>
          <button
            type="button"
            onClick={() => refresh()}
            className="text-sm text-purple-400 hover:text-purple-300"
          >
            Refresh
          </button>
        </div>
        {loading && <p className="text-gray-500 text-sm">Loading…</p>}
        <table className="w-full text-sm text-left">
          <thead>
            <tr className="text-gray-400 border-b border-gray-600">
              <th className="py-2 pr-4">Record ID</th>
              <th className="py-2 pr-4">Invoice #</th>
              <th className="py-2 pr-4">Client</th>
              <th className="py-2 pr-4">Amount</th>
              <th className="py-2 pr-4">Factoring</th>
              <th className="py-2 pr-4">PDF</th>
              <th className="py-2">Status</th>
            </tr>
          </thead>
          <tbody>
            {pendingClaims.map((row) => {
              const f = row.fields || {};
              const pdfHref = api.vertexNemtInvoicePdfUrl(row.id);
              return (
                <tr key={row.id} className="border-b border-gray-700/50 text-gray-200">
                  <td className="py-2 pr-4 font-mono text-xs">{row.id}</td>
                  <td className="py-2 pr-4">{f['Invoice Number']}</td>
                  <td className="py-2 pr-4">{f['Client Name']}</td>
                  <td className="py-2 pr-4">${Number(f['Total Amount'] || 0).toFixed(2)}</td>
                  <td className="py-2 pr-4 text-xs">{f['Factoring Status'] ?? '—'}</td>
                  <td className="py-2 pr-4">
                    <a
                      href={pdfHref}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-purple-400 hover:text-purple-300 text-xs"
                    >
                      Open PDF
                    </a>
                  </td>
                  <td className="py-2">{f['Payment Status']}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
        {pendingClaims.length === 0 && !loading && (
          <p className="text-gray-500 text-sm mt-2">No pending NEMT claims.</p>
        )}
      </div>

      <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
        <h2 className="text-xl font-bold text-white mb-2">Post ERA payment</h2>
        <p className="text-sm text-gray-400 mb-4">
          Matches a pending invoice, sets Paid, posts to VERTEX REVENUE (Source System NEMT).
        </p>
        <form onSubmit={postPayment} className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="md:col-span-2">
            <label className="block text-sm text-gray-400">Airtable invoice record ID</label>
            <input
              className="w-full bg-gray-900 border border-gray-600 rounded px-3 py-2 text-white font-mono text-sm"
              value={paymentForm.invoice_id}
              onChange={(e) => setPaymentForm({ ...paymentForm, invoice_id: e.target.value })}
              placeholder="recXXXXXXXXXXXXXX"
              required
            />
          </div>
          <div>
            <label className="block text-sm text-gray-400">Amount</label>
            <input
              type="number"
              step="0.01"
              className="w-full bg-gray-900 border border-gray-600 rounded px-3 py-2 text-white"
              value={paymentForm.amount || ''}
              onChange={(e) => setPaymentForm({ ...paymentForm, amount: parseFloat(e.target.value) || 0 })}
              required
            />
          </div>
          <div>
            <label className="block text-sm text-gray-400">Payment date</label>
            <input
              type="date"
              className="w-full bg-gray-900 border border-gray-600 rounded px-3 py-2 text-white"
              value={paymentForm.payment_date}
              onChange={(e) => setPaymentForm({ ...paymentForm, payment_date: e.target.value })}
            />
          </div>
          <div>
            <label className="block text-sm text-gray-400">ERA / check reference</label>
            <input
              className="w-full bg-gray-900 border border-gray-600 rounded px-3 py-2 text-white"
              value={paymentForm.era_reference}
              onChange={(e) => setPaymentForm({ ...paymentForm, era_reference: e.target.value })}
            />
          </div>
          <div>
            <label className="block text-sm text-gray-400">Notes</label>
            <input
              className="w-full bg-gray-900 border border-gray-600 rounded px-3 py-2 text-white"
              value={paymentForm.notes}
              onChange={(e) => setPaymentForm({ ...paymentForm, notes: e.target.value })}
            />
          </div>
          <div className="md:col-span-2">
            <button
              type="submit"
              disabled={loading}
              className="px-6 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-medium disabled:opacity-50"
            >
              Post payment
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default NEMTBillingSystem;
