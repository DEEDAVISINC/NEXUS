/**
 * VERTEX HR — embedded in VERTEXSystem (Command Center tab).
 * GATEWAY = hire/clear · VERTEX HR = hours/rates/pay · Deluxe + EFTPS/MI = rails
 */
import React, { useCallback, useEffect, useState } from 'react';
import { api } from '../../api/client';
import { getNexusIdentity } from '../Header';

type HrSub = 'overview' | 'people' | 'timesheets' | 'payroll' | 'tax';

const money = (n: unknown) => {
  const v = Number(n);
  if (Number.isNaN(v)) return '—';
  return v.toLocaleString('en-US', { style: 'currency', currency: 'USD' });
};

const VERTEXHRPanel: React.FC = () => {
  const identity = getNexusIdentity();
  const actorEmail = (identity?.email || 'info@deedavis.biz').toLowerCase();

  const [sub, setSub] = useState<HrSub>('overview');
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState<{ text: string; ok: boolean } | null>(null);

  const [health, setHealth] = useState<any>(null);
  const [dash, setDash] = useState<any>(null);
  const [company, setCompany] = useState<any>(null);
  const [employees, setEmployees] = useState<any[]>([]);
  const [timesheets, setTimesheets] = useState<any[]>([]);
  const [payRuns, setPayRuns] = useState<any[]>([]);
  const [preview, setPreview] = useState<any>(null);
  const [deluxe, setDeluxe] = useState<any>(null);
  const [taxLiability, setTaxLiability] = useState<any>(null);
  const [taxDeposits, setTaxDeposits] = useState<any[]>([]);

  const [companyForm, setCompanyForm] = useState({ ein: '', miUiaRatePercent: '', michiganAccountId: '' });
  const [rateForm, setRateForm] = useState({
    core: '',
    name: '',
    payType: 'hourly',
    hourlyRate: '',
    salaryAnnual: '',
    contractorRate: '',
    federalWithholdPct: '',
    stateWithholdPct: '',
  });
  const [tsForm, setTsForm] = useState({
    personnelNumberCore: '',
    periodStart: '',
    periodEnd: '',
    regularHours: '80',
    otHours: '0',
    ptoHours: '0',
  });
  const [depositForm, setDepositForm] = useState({
    payRunId: '',
    channel: 'eftps',
    amount: '',
    confirmationNumber: '',
  });

  const flash = (text: string, ok = true) => {
    setMsg({ text, ok });
    setTimeout(() => setMsg(null), 5000);
  };

  const refresh = useCallback(async () => {
    setLoading(true);
    try {
      const [h, d, c, e, t, p, dep] = await Promise.all([
        api.getVertexHrHealth(),
        api.getVertexHrDashboard(),
        api.getVertexHrCompany(),
        api.getVertexHrEmployees(),
        api.getVertexHrTimesheets(),
        api.getVertexHrPayRuns(),
        api.getVertexHrTaxDeposits(),
      ]);
      if (!h?.ok && h?.error) {
        setHealth({ ok: false, error: h.error });
        flash(h.error || 'VERTEX HR API not available on local backend', false);
        return;
      }
      setHealth(h);
      setDash(d?.ok === false ? null : d);
      setCompany(c?.company || null);
      setCompanyForm({
        ein: c?.company?.ein || '',
        miUiaRatePercent:
          c?.company?.miUiaRatePercent != null ? String(c.company.miUiaRatePercent) : '',
        michiganAccountId: c?.company?.michiganAccountId || '',
      });
      setEmployees(e?.employees || []);
      setTimesheets(t?.timesheets || []);
      setPayRuns(p?.payRuns || []);
      setTaxDeposits(dep?.deposits || dep?.taxDeposits || []);
      const period = d?.period || h?.currentPeriod;
      if (period?.periodStart) {
        setTsForm((f) =>
          f.periodStart
            ? f
            : { ...f, periodStart: period.periodStart, periodEnd: period.periodEnd },
        );
      }
    } catch (err: any) {
      setHealth({ ok: false, error: err?.message || 'Cannot reach VERTEX HR API' });
      flash(err?.message || 'Cannot reach VERTEX HR API', false);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const syncGateway = async () => {
    setBusy(true);
    try {
      const r = await api.syncVertexHrEmployees({ actorEmail });
      if (!r?.ok) {
        flash(r?.error || 'Sync failed', false);
        return;
      }
      flash(`Synced ${r.synced} from GATEWAY (${r.total} total)`);
      await refresh();
    } finally {
      setBusy(false);
    }
  };

  const saveCompany = async () => {
    setBusy(true);
    try {
      const r = await api.putVertexHrCompany({
        actorEmail,
        ein: companyForm.ein.trim(),
        michiganAccountId: companyForm.michiganAccountId.trim(),
        miUiaRatePercent:
          companyForm.miUiaRatePercent === '' ? null : Number(companyForm.miUiaRatePercent),
      });
      if (!r?.ok) {
        flash(r?.error || 'Save failed', false);
        return;
      }
      flash('Company tax settings saved');
      await refresh();
    } finally {
      setBusy(false);
    }
  };

  const openRate = (emp: any) => {
    setRateForm({
      core: emp.personnelNumberCore || '',
      name: emp.name || '',
      payType: emp.payType || 'hourly',
      hourlyRate: emp.hourlyRate != null ? String(emp.hourlyRate) : '',
      salaryAnnual: emp.salaryAnnual != null ? String(emp.salaryAnnual) : '',
      contractorRate: emp.contractorRate != null ? String(emp.contractorRate) : '',
      federalWithholdPct: emp.federalWithholdPct != null ? String(emp.federalWithholdPct) : '',
      stateWithholdPct: emp.stateWithholdPct != null ? String(emp.stateWithholdPct) : '',
    });
    setSub('people');
  };

  const saveRate = async () => {
    if (!rateForm.core) return;
    setBusy(true);
    try {
      const rateBody: any = {
        actorEmail,
        payType: rateForm.payType,
      };
      if (rateForm.hourlyRate !== '') rateBody.hourlyRate = Number(rateForm.hourlyRate);
      if (rateForm.salaryAnnual !== '') rateBody.salaryAnnual = Number(rateForm.salaryAnnual);
      if (rateForm.contractorRate !== '') rateBody.contractorRate = Number(rateForm.contractorRate);
      const r1 = await api.putVertexHrEmployeeRate(rateForm.core, rateBody);
      if (!r1?.ok) {
        flash(r1?.error || 'Rate save failed', false);
        return;
      }
      const taxBody: any = { actorEmail };
      if (rateForm.federalWithholdPct !== '') taxBody.federalWithholdPct = Number(rateForm.federalWithholdPct);
      if (rateForm.stateWithholdPct !== '') taxBody.stateWithholdPct = Number(rateForm.stateWithholdPct);
      if (Object.keys(taxBody).length > 1) {
        await api.putVertexHrEmployeeTax(rateForm.core, taxBody);
      }
      flash(`Rate saved for ${rateForm.name}`);
      setRateForm((f) => ({ ...f, core: '' }));
      await refresh();
    } finally {
      setBusy(false);
    }
  };

  const createTimesheet = async () => {
    setBusy(true);
    try {
      const r = await api.createVertexHrTimesheet({
        actorEmail,
        personnelNumberCore: tsForm.personnelNumberCore,
        periodStart: tsForm.periodStart,
        periodEnd: tsForm.periodEnd,
        regularHours: Number(tsForm.regularHours || 0),
        otHours: Number(tsForm.otHours || 0),
        ptoHours: Number(tsForm.ptoHours || 0),
      });
      if (!r?.ok) {
        flash(r?.error || 'Timesheet create failed', false);
        return;
      }
      flash('Timesheet draft created');
      await refresh();
    } finally {
      setBusy(false);
    }
  };

  const tsAction = async (id: string, action: 'submit' | 'approve' | 'reject') => {
    setBusy(true);
    try {
      const fn =
        action === 'submit'
          ? api.submitVertexHrTimesheet
          : action === 'approve'
            ? api.approveVertexHrTimesheet
            : api.rejectVertexHrTimesheet;
      const r = await fn(id, { actorEmail });
      if (!r?.ok) {
        flash(r?.error || `${action} failed`, false);
        return;
      }
      flash(`Timesheet ${action}d`);
      await refresh();
    } finally {
      setBusy(false);
    }
  };

  const periodStart = dash?.period?.periodStart || health?.currentPeriod?.periodStart || '';
  const periodEnd = dash?.period?.periodEnd || health?.currentPeriod?.periodEnd || '';

  const runPreview = async () => {
    setBusy(true);
    try {
      const r = await api.previewVertexHrPayRun({ periodStart, periodEnd, actorEmail });
      if (!r?.ok) {
        flash(r?.error || 'Preview failed', false);
        setPreview(null);
        return;
      }
      setPreview(r);
      flash(`Preview: ${r.lineCount} lines · net ${money(r.netTotal)}`);
    } finally {
      setBusy(false);
    }
  };

  const finalizePay = async () => {
    if (!window.confirm(`Finalize pay run for ${periodStart} – ${periodEnd}? This locks timesheets.`)) return;
    setBusy(true);
    try {
      const r = await api.finalizeVertexHrPayRun({ periodStart, periodEnd, actorEmail });
      if (!r?.ok) {
        flash(r?.error || 'Finalize failed', false);
        return;
      }
      flash(`Pay run ${r.payRun?.id} finalized`);
      setPreview(null);
      await refresh();
      setSub('payroll');
    } finally {
      setBusy(false);
    }
  };

  const loadDeluxe = async (payRunId: string) => {
    setBusy(true);
    try {
      const r = await api.getVertexHrDeluxeExport(payRunId);
      if (!r?.ok) {
        flash(r?.error || 'Deluxe export failed', false);
        return;
      }
      setDeluxe(r);
      flash(`Deluxe register: ${r.unpaidCount} unpaid`);
    } finally {
      setBusy(false);
    }
  };

  const markDeluxe = async (payRunId: string) => {
    setBusy(true);
    try {
      const r = await api.markVertexHrDeluxePaid(payRunId, { actorEmail });
      if (!r?.ok) {
        flash(r?.error || 'Mark paid failed', false);
        return;
      }
      flash('Marked Deluxe paid');
      setDeluxe(null);
      await refresh();
    } finally {
      setBusy(false);
    }
  };

  const loadTax = async (payRunId?: string) => {
    setBusy(true);
    try {
      const r = await api.getVertexHrTaxLiability(payRunId);
      if (!r?.ok) {
        flash(r?.error || 'Tax liability failed', false);
        return;
      }
      setTaxLiability(r);
      if (payRunId) setDepositForm((f) => ({ ...f, payRunId }));
      setSub('tax');
    } finally {
      setBusy(false);
    }
  };

  const logDeposit = async () => {
    setBusy(true);
    try {
      const r = await api.postVertexHrTaxDeposit({
        actorEmail,
        payRunId: depositForm.payRunId,
        channel: depositForm.channel,
        amount: Number(depositForm.amount || 0),
        confirmationNumber: depositForm.confirmationNumber,
      });
      if (!r?.ok) {
        flash(r?.error || 'Deposit log failed', false);
        return;
      }
      flash('Tax deposit logged');
      setDepositForm((f) => ({ ...f, amount: '', confirmationNumber: '' }));
      await refresh();
    } finally {
      setBusy(false);
    }
  };

  const counts = dash?.counts || {};
  const subs: { id: HrSub; label: string }[] = [
    { id: 'overview', label: 'Overview' },
    { id: 'people', label: 'People & rates' },
    { id: 'timesheets', label: 'Timesheets' },
    { id: 'payroll', label: 'Pay runs' },
    { id: 'tax', label: 'Tax deposits' },
  ];

  if (loading) {
    return <div className="text-gray-400 py-12 text-center">Loading VERTEX HR…</div>;
  }

  if (health && health.ok === false) {
    return (
      <div className="p-4 rounded-lg bg-red-500/15 border border-red-500/40 text-red-300 text-sm space-y-2">
        <div>VERTEX HR API not reachable on the local backend.</div>
        <div className="text-xs text-red-200/80">
          {health.error || 'Confirm api_server.py is running with /vertex/hr/health → 200'}
        </div>
        <button
          type="button"
          onClick={refresh}
          className="px-3 py-1.5 rounded bg-red-600 text-white text-xs font-semibold"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {msg && (
        <div
          className={`fixed top-4 right-4 z-50 px-5 py-3 rounded-lg text-white text-sm shadow-lg ${
            msg.ok ? 'bg-emerald-600' : 'bg-red-600'
          }`}
        >
          {msg.text}
        </div>
      )}

      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-white">VERTEX HR</h2>
          <p className="text-sm text-gray-400 mt-1">
            Hours · rates · pay calc · Deluxe eChecks · EFTPS / MI UIA — identity from GATEWAY
          </p>
          {periodStart && (
            <p className="text-xs text-purple-300 mt-2">
              Current period: <span className="font-semibold text-white">{periodStart}</span> →{' '}
              <span className="font-semibold text-white">{periodEnd}</span>
            </p>
          )}
        </div>
        <div className="flex flex-wrap gap-2">
          <button
            type="button"
            disabled={busy}
            onClick={syncGateway}
            className="px-4 py-2 rounded-lg bg-purple-600 hover:bg-purple-500 text-white text-sm font-semibold disabled:opacity-50"
          >
            Sync GATEWAY
          </button>
          <button
            type="button"
            disabled={busy}
            onClick={refresh}
            className="px-4 py-2 rounded-lg bg-gray-700 hover:bg-gray-600 text-gray-200 text-sm"
          >
            Refresh
          </button>
        </div>
      </div>

      <div className="flex flex-wrap gap-2">
        {subs.map((s) => (
          <button
            key={s.id}
            type="button"
            onClick={() => setSub(s.id)}
            className={`px-4 py-2 rounded-lg text-sm font-medium ${
              sub === s.id
                ? 'bg-violet-600 text-white'
                : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
            }`}
          >
            {s.label}
          </button>
        ))}
      </div>

      {sub === 'overview' && (
        <div className="space-y-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {[
              ['Synced', counts.employeesSynced],
              ['Payable', counts.payable],
              ['Missing rates', counts.missingRates],
              ['Awaiting approval', counts.timesheetsAwaitingApproval],
              ['Approved this period', counts.timesheetsApprovedThisPeriod],
              ['Deluxe unpaid runs', counts.deluxeUnpaidPayRuns],
              ['Pay runs finalized', counts.payRunsFinalized],
              ['Tax deposits logged', counts.taxDepositsLogged],
            ].map(([label, val]) => (
              <div key={String(label)} className="bg-gray-800/80 border border-gray-700 rounded-xl p-4">
                <div className="text-2xl font-bold text-white">{val ?? 0}</div>
                <div className="text-xs text-gray-400 mt-1">{label}</div>
              </div>
            ))}
          </div>

          {(dash?.blockers || []).length > 0 && (
            <div className="bg-amber-500/10 border border-amber-500/40 rounded-xl p-4">
              <div className="text-amber-300 font-semibold text-sm mb-2">Blockers</div>
              <ul className="text-sm text-amber-100/90 space-y-1 list-disc pl-5">
                {(dash.blockers as string[]).map((b) => (
                  <li key={b}>{b}</li>
                ))}
              </ul>
            </div>
          )}

          <div className="bg-gray-800 border border-gray-700 rounded-xl p-5 space-y-3">
            <h3 className="text-white font-semibold">Company tax settings</h3>
            <p className="text-xs text-gray-400">
              Pay rail: {company?.payRail || 'Deluxe eChecks'} · Tax:{' '}
              {(company?.taxRails || ['EFTPS', 'Michigan']).join(' + ')}
            </p>
            <div className="grid md:grid-cols-3 gap-3">
              <label className="text-xs text-gray-400 block">
                EIN
                <input
                  className="mt-1 w-full bg-gray-900 border border-gray-600 rounded-lg px-3 py-2 text-white text-sm"
                  value={companyForm.ein}
                  onChange={(e) => setCompanyForm({ ...companyForm, ein: e.target.value })}
                  placeholder="XX-XXXXXXX"
                />
              </label>
              <label className="text-xs text-gray-400 block">
                MI UIA rate %
                <input
                  className="mt-1 w-full bg-gray-900 border border-gray-600 rounded-lg px-3 py-2 text-white text-sm"
                  value={companyForm.miUiaRatePercent}
                  onChange={(e) => setCompanyForm({ ...companyForm, miUiaRatePercent: e.target.value })}
                  placeholder="e.g. 2.7"
                />
              </label>
              <label className="text-xs text-gray-400 block">
                MI account ID
                <input
                  className="mt-1 w-full bg-gray-900 border border-gray-600 rounded-lg px-3 py-2 text-white text-sm"
                  value={companyForm.michiganAccountId}
                  onChange={(e) => setCompanyForm({ ...companyForm, michiganAccountId: e.target.value })}
                />
              </label>
            </div>
            <button
              type="button"
              disabled={busy}
              onClick={saveCompany}
              className="px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-sm font-semibold disabled:opacity-50"
            >
              Save company settings
            </button>
          </div>

          <div className="text-xs text-gray-500">
            Workflow: Sync GATEWAY → set rates → timesheets submit/approve → preview → finalize → Deluxe
            register → mark paid → tax liability → log EFTPS/MI deposits.
          </div>
        </div>
      )}

      {sub === 'people' && (
        <div className="space-y-4">
          {rateForm.core && (
            <div className="bg-violet-950/40 border border-violet-500/40 rounded-xl p-5 space-y-3">
              <h3 className="text-white font-semibold">Edit rate — {rateForm.name}</h3>
              <div className="grid md:grid-cols-3 gap-3">
                <label className="text-xs text-gray-400">
                  Pay type
                  <select
                    className="mt-1 w-full bg-gray-900 border border-gray-600 rounded-lg px-3 py-2 text-white text-sm"
                    value={rateForm.payType}
                    onChange={(e) => setRateForm({ ...rateForm, payType: e.target.value })}
                  >
                    <option value="hourly">Hourly</option>
                    <option value="salary">Salary</option>
                    <option value="contractor">Contractor</option>
                  </select>
                </label>
                <label className="text-xs text-gray-400">
                  Hourly rate
                  <input
                    className="mt-1 w-full bg-gray-900 border border-gray-600 rounded-lg px-3 py-2 text-white text-sm"
                    value={rateForm.hourlyRate}
                    onChange={(e) => setRateForm({ ...rateForm, hourlyRate: e.target.value })}
                  />
                </label>
                <label className="text-xs text-gray-400">
                  Salary annual
                  <input
                    className="mt-1 w-full bg-gray-900 border border-gray-600 rounded-lg px-3 py-2 text-white text-sm"
                    value={rateForm.salaryAnnual}
                    onChange={(e) => setRateForm({ ...rateForm, salaryAnnual: e.target.value })}
                  />
                </label>
                <label className="text-xs text-gray-400">
                  Contractor rate
                  <input
                    className="mt-1 w-full bg-gray-900 border border-gray-600 rounded-lg px-3 py-2 text-white text-sm"
                    value={rateForm.contractorRate}
                    onChange={(e) => setRateForm({ ...rateForm, contractorRate: e.target.value })}
                  />
                </label>
                <label className="text-xs text-gray-400">
                  Federal withhold %
                  <input
                    className="mt-1 w-full bg-gray-900 border border-gray-600 rounded-lg px-3 py-2 text-white text-sm"
                    value={rateForm.federalWithholdPct}
                    onChange={(e) => setRateForm({ ...rateForm, federalWithholdPct: e.target.value })}
                  />
                </label>
                <label className="text-xs text-gray-400">
                  State withhold %
                  <input
                    className="mt-1 w-full bg-gray-900 border border-gray-600 rounded-lg px-3 py-2 text-white text-sm"
                    value={rateForm.stateWithholdPct}
                    onChange={(e) => setRateForm({ ...rateForm, stateWithholdPct: e.target.value })}
                  />
                </label>
              </div>
              <div className="flex gap-2">
                <button
                  type="button"
                  disabled={busy}
                  onClick={saveRate}
                  className="px-4 py-2 rounded-lg bg-emerald-600 text-white text-sm font-semibold"
                >
                  Save rate
                </button>
                <button
                  type="button"
                  onClick={() => setRateForm((f) => ({ ...f, core: '' }))}
                  className="px-4 py-2 rounded-lg bg-gray-700 text-gray-200 text-sm"
                >
                  Cancel
                </button>
              </div>
            </div>
          )}

          <div className="overflow-x-auto rounded-xl border border-gray-700">
            <table className="w-full text-sm min-w-[900px]">
              <thead className="bg-gray-800 text-gray-400 text-xs uppercase">
                <tr>
                  <th className="text-left px-3 py-2">Name</th>
                  <th className="text-left px-3 py-2">Core #</th>
                  <th className="text-left px-3 py-2">Type</th>
                  <th className="text-left px-3 py-2">Payable</th>
                  <th className="text-left px-3 py-2">Rate</th>
                  <th className="text-left px-3 py-2">can-work</th>
                  <th className="text-left px-3 py-2" />
                </tr>
              </thead>
              <tbody>
                {employees.length === 0 && (
                  <tr>
                    <td colSpan={7} className="px-3 py-8 text-center text-gray-500">
                      No employees — click Sync GATEWAY
                    </td>
                  </tr>
                )}
                {employees.map((emp) => {
                  const pt = (emp.payType || 'hourly').toLowerCase();
                  const rate =
                    pt === 'salary'
                      ? emp.salaryAnnual
                        ? `${money(emp.salaryAnnual)}/yr`
                        : '—'
                      : pt === 'contractor'
                        ? emp.contractorRate
                          ? `${money(emp.contractorRate)}/hr`
                          : '—'
                        : emp.hourlyRate
                          ? `${money(emp.hourlyRate)}/hr`
                          : '—';
                  return (
                    <tr key={emp.personnelNumberCore} className="border-t border-gray-800 text-gray-200">
                      <td className="px-3 py-2 font-medium text-white">{emp.name}</td>
                      <td className="px-3 py-2 font-mono text-xs">{emp.personnelNumberCore}</td>
                      <td className="px-3 py-2">{emp.employeeTypeLabel || emp.workerType || pt}</td>
                      <td className="px-3 py-2">{emp.payable ? '✅' : '❌'}</td>
                      <td className="px-3 py-2">{rate}</td>
                      <td className="px-3 py-2 text-xs text-gray-400 max-w-[180px] truncate" title={emp.canWorkReason}>
                        {emp.canWork ? 'clear' : emp.canWorkReason || 'blocked'}
                      </td>
                      <td className="px-3 py-2">
                        <button
                          type="button"
                          onClick={() => openRate(emp)}
                          className="text-xs text-violet-300 hover:text-violet-200"
                        >
                          Edit rate
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {sub === 'timesheets' && (
        <div className="space-y-4">
          <div className="bg-gray-800 border border-gray-700 rounded-xl p-5 space-y-3">
            <h3 className="text-white font-semibold">New timesheet</h3>
            <div className="grid md:grid-cols-3 gap-3">
              <label className="text-xs text-gray-400 md:col-span-3">
                Employee
                <select
                  className="mt-1 w-full bg-gray-900 border border-gray-600 rounded-lg px-3 py-2 text-white text-sm"
                  value={tsForm.personnelNumberCore}
                  onChange={(e) => setTsForm({ ...tsForm, personnelNumberCore: e.target.value })}
                >
                  <option value="">Select…</option>
                  {employees.map((e) => (
                    <option key={e.personnelNumberCore} value={e.personnelNumberCore}>
                      {e.name} ({e.personnelNumberCore}){!e.payable ? ' — not payable' : ''}
                    </option>
                  ))}
                </select>
              </label>
              <label className="text-xs text-gray-400">
                Period start
                <input
                  type="date"
                  className="mt-1 w-full bg-gray-900 border border-gray-600 rounded-lg px-3 py-2 text-white text-sm"
                  value={tsForm.periodStart}
                  onChange={(e) => setTsForm({ ...tsForm, periodStart: e.target.value })}
                />
              </label>
              <label className="text-xs text-gray-400">
                Period end
                <input
                  type="date"
                  className="mt-1 w-full bg-gray-900 border border-gray-600 rounded-lg px-3 py-2 text-white text-sm"
                  value={tsForm.periodEnd}
                  onChange={(e) => setTsForm({ ...tsForm, periodEnd: e.target.value })}
                />
              </label>
              <label className="text-xs text-gray-400">
                Regular hours
                <input
                  className="mt-1 w-full bg-gray-900 border border-gray-600 rounded-lg px-3 py-2 text-white text-sm"
                  value={tsForm.regularHours}
                  onChange={(e) => setTsForm({ ...tsForm, regularHours: e.target.value })}
                />
              </label>
              <label className="text-xs text-gray-400">
                OT hours
                <input
                  className="mt-1 w-full bg-gray-900 border border-gray-600 rounded-lg px-3 py-2 text-white text-sm"
                  value={tsForm.otHours}
                  onChange={(e) => setTsForm({ ...tsForm, otHours: e.target.value })}
                />
              </label>
              <label className="text-xs text-gray-400">
                PTO hours
                <input
                  className="mt-1 w-full bg-gray-900 border border-gray-600 rounded-lg px-3 py-2 text-white text-sm"
                  value={tsForm.ptoHours}
                  onChange={(e) => setTsForm({ ...tsForm, ptoHours: e.target.value })}
                />
              </label>
            </div>
            <button
              type="button"
              disabled={busy || !tsForm.personnelNumberCore}
              onClick={createTimesheet}
              className="px-4 py-2 rounded-lg bg-violet-600 text-white text-sm font-semibold disabled:opacity-50"
            >
              Create draft
            </button>
          </div>

          <div className="overflow-x-auto rounded-xl border border-gray-700">
            <table className="w-full text-sm min-w-[800px]">
              <thead className="bg-gray-800 text-gray-400 text-xs uppercase">
                <tr>
                  <th className="text-left px-3 py-2">Name</th>
                  <th className="text-left px-3 py-2">Period</th>
                  <th className="text-left px-3 py-2">Hours</th>
                  <th className="text-left px-3 py-2">Status</th>
                  <th className="text-left px-3 py-2">Actions</th>
                </tr>
              </thead>
              <tbody>
                {timesheets.map((t) => (
                  <tr key={t.id} className="border-t border-gray-800 text-gray-200">
                    <td className="px-3 py-2">{t.name}</td>
                    <td className="px-3 py-2 text-xs">
                      {t.periodStart} → {t.periodEnd}
                    </td>
                    <td className="px-3 py-2 text-xs">
                      R {t.regularHours} · OT {t.otHours || 0}
                    </td>
                    <td className="px-3 py-2">{t.status}</td>
                    <td className="px-3 py-2 space-x-2">
                      {(t.status === 'Draft' || t.status === 'Rejected') && (
                        <button type="button" className="text-xs text-sky-300" onClick={() => tsAction(t.id, 'submit')}>
                          Submit
                        </button>
                      )}
                      {(t.status === 'Submitted' || t.status === 'Draft') && (
                        <button type="button" className="text-xs text-emerald-300" onClick={() => tsAction(t.id, 'approve')}>
                          Approve
                        </button>
                      )}
                      {t.status !== 'Paid' && (
                        <button type="button" className="text-xs text-red-300" onClick={() => tsAction(t.id, 'reject')}>
                          Reject
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {sub === 'payroll' && (
        <div className="space-y-4">
          <div className="bg-gray-800 border border-gray-700 rounded-xl p-5 flex flex-wrap gap-3 items-center">
            <div className="text-sm text-gray-300 mr-auto">
              Period <span className="text-white font-semibold">{periodStart}</span> →{' '}
              <span className="text-white font-semibold">{periodEnd}</span>
              {dash?.readyToRunPayroll ? (
                <span className="ml-2 text-emerald-400 text-xs">Ready to run</span>
              ) : (
                <span className="ml-2 text-amber-400 text-xs">Need approved timesheets + rates</span>
              )}
            </div>
            <button
              type="button"
              disabled={busy || !periodStart}
              onClick={runPreview}
              className="px-4 py-2 rounded-lg bg-sky-600 text-white text-sm font-semibold disabled:opacity-50"
            >
              Preview pay run
            </button>
            <button
              type="button"
              disabled={busy || !periodStart}
              onClick={finalizePay}
              className="px-4 py-2 rounded-lg bg-emerald-600 text-white text-sm font-semibold disabled:opacity-50"
            >
              Finalize pay run
            </button>
          </div>

          {preview && (
            <div className="bg-gray-900/80 border border-sky-500/30 rounded-xl p-4 overflow-x-auto">
              <div className="text-sm text-sky-200 mb-2">
                Preview · {preview.lineCount} lines · Gross {money(preview.grossTotal)} · Net{' '}
                {money(preview.netTotal)}
              </div>
              <table className="w-full text-xs min-w-[700px]">
                <thead className="text-gray-500">
                  <tr>
                    <th className="text-left py-1">Name</th>
                    <th className="text-left py-1">Gross</th>
                    <th className="text-left py-1">Net</th>
                    <th className="text-left py-1">Note</th>
                  </tr>
                </thead>
                <tbody>
                  {(preview.lines || []).map((l: any, i: number) => (
                    <tr key={i} className="border-t border-gray-800 text-gray-300">
                      <td className="py-1">{l.name}</td>
                      <td className="py-1">{l.error ? '—' : money(l.gross)}</td>
                      <td className="py-1">{l.error ? '—' : money(l.net)}</td>
                      <td className="py-1 text-red-300">{l.error || ''}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {deluxe && (
            <div className="bg-emerald-950/30 border border-emerald-500/30 rounded-xl p-4">
              <div className="flex justify-between items-center mb-2">
                <div className="text-sm text-emerald-200">
                  Deluxe register — {deluxe.payRunId} · unpaid {deluxe.unpaidCount} · net{' '}
                  {money(deluxe.netTotal)}
                </div>
                <button
                  type="button"
                  onClick={() => markDeluxe(deluxe.payRunId)}
                  className="text-xs px-3 py-1.5 rounded bg-emerald-600 text-white"
                >
                  Mark all Deluxe paid
                </button>
              </div>
              <pre className="text-xs text-gray-300 overflow-x-auto whitespace-pre-wrap">
                {JSON.stringify(deluxe.rows, null, 2)}
              </pre>
            </div>
          )}

          <div className="overflow-x-auto rounded-xl border border-gray-700">
            <table className="w-full text-sm min-w-[800px]">
              <thead className="bg-gray-800 text-gray-400 text-xs uppercase">
                <tr>
                  <th className="text-left px-3 py-2">Pay run</th>
                  <th className="text-left px-3 py-2">Period</th>
                  <th className="text-left px-3 py-2">Gross / Net</th>
                  <th className="text-left px-3 py-2">Deluxe</th>
                  <th className="text-left px-3 py-2">Actions</th>
                </tr>
              </thead>
              <tbody>
                {payRuns.length === 0 && (
                  <tr>
                    <td colSpan={5} className="px-3 py-8 text-center text-gray-500">
                      No pay runs yet
                    </td>
                  </tr>
                )}
                {payRuns.map((pr) => (
                  <tr key={pr.id} className="border-t border-gray-800 text-gray-200">
                    <td className="px-3 py-2 font-mono text-xs">{pr.id}</td>
                    <td className="px-3 py-2 text-xs">
                      {pr.periodStart} → {pr.periodEnd}
                    </td>
                    <td className="px-3 py-2 text-xs">
                      {money(pr.grossTotal)} / {money(pr.netTotal)}
                    </td>
                    <td className="px-3 py-2 text-xs">{pr.deluxePaidAt ? 'Paid' : 'Unpaid'}</td>
                    <td className="px-3 py-2 space-x-2">
                      <button type="button" className="text-xs text-emerald-300" onClick={() => loadDeluxe(pr.id)}>
                        Deluxe register
                      </button>
                      <button type="button" className="text-xs text-amber-300" onClick={() => loadTax(pr.id)}>
                        Tax liability
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {sub === 'tax' && (
        <div className="space-y-4">
          <div className="bg-gray-800 border border-gray-700 rounded-xl p-5 space-y-3">
            <h3 className="text-white font-semibold">Log tax deposit</h3>
            <p className="text-xs text-gray-400">
              After you pay nets in Deluxe, deposit federal (EFTPS) and Michigan (income / UIA), then log
              confirmation numbers here.
            </p>
            <div className="grid md:grid-cols-2 gap-3">
              <label className="text-xs text-gray-400">
                Pay run ID
                <select
                  className="mt-1 w-full bg-gray-900 border border-gray-600 rounded-lg px-3 py-2 text-white text-sm"
                  value={depositForm.payRunId}
                  onChange={(e) => setDepositForm({ ...depositForm, payRunId: e.target.value })}
                >
                  <option value="">Select…</option>
                  {payRuns.map((pr) => (
                    <option key={pr.id} value={pr.id}>
                      {pr.id}
                    </option>
                  ))}
                </select>
              </label>
              <label className="text-xs text-gray-400">
                Channel
                <select
                  className="mt-1 w-full bg-gray-900 border border-gray-600 rounded-lg px-3 py-2 text-white text-sm"
                  value={depositForm.channel}
                  onChange={(e) => setDepositForm({ ...depositForm, channel: e.target.value })}
                >
                  <option value="eftps">EFTPS (federal)</option>
                  <option value="mi_income">Michigan income tax</option>
                  <option value="mi_uia">Michigan UIA</option>
                  <option value="other">Other</option>
                </select>
              </label>
              <label className="text-xs text-gray-400">
                Amount
                <input
                  className="mt-1 w-full bg-gray-900 border border-gray-600 rounded-lg px-3 py-2 text-white text-sm"
                  value={depositForm.amount}
                  onChange={(e) => setDepositForm({ ...depositForm, amount: e.target.value })}
                />
              </label>
              <label className="text-xs text-gray-400">
                Confirmation #
                <input
                  className="mt-1 w-full bg-gray-900 border border-gray-600 rounded-lg px-3 py-2 text-white text-sm"
                  value={depositForm.confirmationNumber}
                  onChange={(e) => setDepositForm({ ...depositForm, confirmationNumber: e.target.value })}
                />
              </label>
            </div>
            <div className="flex gap-2">
              <button
                type="button"
                disabled={busy || !depositForm.payRunId}
                onClick={logDeposit}
                className="px-4 py-2 rounded-lg bg-amber-600 text-white text-sm font-semibold disabled:opacity-50"
              >
                Log deposit
              </button>
              {depositForm.payRunId && (
                <button
                  type="button"
                  disabled={busy}
                  onClick={() => loadTax(depositForm.payRunId)}
                  className="px-4 py-2 rounded-lg bg-gray-700 text-gray-200 text-sm"
                >
                  Refresh liability
                </button>
              )}
            </div>
          </div>

          {taxLiability && (
            <pre className="bg-gray-900 border border-gray-700 rounded-xl p-4 text-xs text-gray-300 overflow-x-auto">
              {JSON.stringify(taxLiability, null, 2)}
            </pre>
          )}

          <div className="overflow-x-auto rounded-xl border border-gray-700">
            <table className="w-full text-sm">
              <thead className="bg-gray-800 text-gray-400 text-xs uppercase">
                <tr>
                  <th className="text-left px-3 py-2">When</th>
                  <th className="text-left px-3 py-2">Channel</th>
                  <th className="text-left px-3 py-2">Amount</th>
                  <th className="text-left px-3 py-2">Confirmation</th>
                  <th className="text-left px-3 py-2">Pay run</th>
                </tr>
              </thead>
              <tbody>
                {taxDeposits.length === 0 && (
                  <tr>
                    <td colSpan={5} className="px-3 py-6 text-center text-gray-500">
                      No deposits logged
                    </td>
                  </tr>
                )}
                {taxDeposits.map((d: any, i: number) => (
                  <tr key={d.id || i} className="border-t border-gray-800 text-gray-200">
                    <td className="px-3 py-2 text-xs">{(d.depositedAt || d.createdAt || '').slice(0, 19)}</td>
                    <td className="px-3 py-2">{d.channel || d.rail}</td>
                    <td className="px-3 py-2">{money(d.amount)}</td>
                    <td className="px-3 py-2 font-mono text-xs">{d.confirmationNumber}</td>
                    <td className="px-3 py-2 font-mono text-xs">{d.payRunId}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

export default VERTEXHRPanel;
