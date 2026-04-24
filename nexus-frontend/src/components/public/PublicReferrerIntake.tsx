import React, { useMemo, useState } from 'react';
import { api } from '../../api/client';
import SHIELDAcronym from '../shield/Acronym';

/**
 * SHIELD — Public referrer-facing intake.
 *
 * Accessed at /refer — no NEXUS chrome, no login. What an MDHHS case worker,
 * county health department partner, or self-referring family sees when you
 * share the link. Full CWC branding (yellow hero, real logo), friendly copy,
 * light card over cobalt backdrop for maximum accessibility.
 */

const COUNTIES = ['Wayne', 'Oakland', 'Macomb', 'Genesee', 'Kent', 'Muskegon', 'Other'];
const URGENCY_LEVELS = ['Standard', 'Urgent', 'Emergency'];
const SERVICE_CHOICES = [
  'Lead Screening',
  'CLPPP Follow-up',
  'NEMT (transportation)',
  'Lead Remediation',
  'Housing Assistance',
  'Food Navigation',
  'Filter Safety Net',
];

const STEPS = [
  { id: 1, label: 'About You', hint: 'Who is referring this family' },
  { id: 2, label: 'The Family', hint: 'Household & contact' },
  { id: 3, label: 'Children', hint: 'Lead screening status' },
  { id: 4, label: 'Services', hint: 'What they need' },
  { id: 5, label: 'Send It', hint: 'Review & submit' },
];

const PublicReferrerIntake: React.FC = () => {
  const [step, setStep] = useState(1);
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState<{ reference: string; navigatorMessage: string } | null>(null);
  const [error, setError] = useState<string | null>(null);

  const [form, setForm] = useState<any>({
    referral_source: 'MDHHS',
    referring_agency: '',
    case_worker_name: '',
    case_worker_email: '',
    case_worker_phone: '',
    county: 'Wayne',
    family_name: '',
    address: '',
    city: '',
    zip: '',
    primary_contact_name: '',
    primary_contact_phone: '',
    primary_contact_email: '',
    language: 'English',
    medicaid_enrolled: false,
    snap_enrolled: false,
    children: [{ child_name: '', age_months: '', lead_test_status: 'Not Tested', blood_lead_level: '', clppp_case_number: '' }],
    services_requested: [] as string[],
    urgency: 'Standard',
    notes: '',
    intake_method: 'Public Web Form',
  });

  const set = (k: string, v: any) => setForm((f: any) => ({ ...f, [k]: v }));
  const toggleService = (svc: string) => setForm((f: any) => ({
    ...f,
    services_requested: f.services_requested.includes(svc)
      ? f.services_requested.filter((s: string) => s !== svc)
      : [...f.services_requested, svc],
  }));
  const updChild = (i: number, k: string, v: any) => setForm((f: any) => ({
    ...f,
    children: f.children.map((c: any, idx: number) => idx === i ? { ...c, [k]: v } : c),
  }));
  const addChild = () => setForm((f: any) => ({
    ...f,
    children: [...f.children, { child_name: '', age_months: '', lead_test_status: 'Not Tested', blood_lead_level: '', clppp_case_number: '' }],
  }));
  const removeChild = (i: number) => setForm((f: any) => ({ ...f, children: f.children.filter((_: any, idx: number) => idx !== i) }));

  const canAdvance = useMemo(() => {
    if (step === 1) return !!form.case_worker_name && !!form.case_worker_email && !!form.county;
    if (step === 4) return form.services_requested.length > 0;
    return true;
  }, [step, form]);

  const submit = async () => {
    try {
      setSubmitting(true);
      setError(null);
      const result: any = await api.createShieldReferral(form);
      if (result?.success) {
        setSubmitted({
          reference: String(result.reference_number ?? result.referral_id ?? 'received'),
          navigatorMessage: result.navigator_message || 'A navigator will reach out within 48 hours.',
        });
        window.scrollTo({ top: 0, behavior: 'smooth' });
      } else {
        setError(result?.error || 'Something went wrong. Please try again or call CWC directly.');
      }
    } catch (e: any) {
      setError(`Submission failed: ${e.message}`);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#050f2e] text-slate-900">
      {/* ───────── YELLOW HERO ───────── */}
      <header className="bg-[#f5c23e] border-b-4 border-[#e0a92e]">
        <div className="max-w-5xl mx-auto px-6 py-8">
          <div className="flex items-center justify-between flex-wrap gap-6">
            <div className="flex items-center gap-5 min-w-0">
              <img src="/cwc-logo.png" alt="Cause We Care" className="w-24 h-24 rounded-xl object-contain bg-white/40 p-2 shadow-md shrink-0" />
              <div className="min-w-0">
                <div className="text-[11px] uppercase tracking-[0.3em] text-[#1f3fae]/80 font-black">Partner in Michigan's Lead-Safe Ecosystem</div>
                <h1 className="text-3xl md:text-4xl font-black text-[#1f3fae] leading-tight mt-1">
                  Refer a family. We'll take it from here.
                </h1>
                <div className="text-[11px] uppercase tracking-[0.25em] text-[#1f3fae]/70 font-black italic mt-2">
                  Care. Navigate. Transform.
                </div>
                <p className="text-sm text-[#1f3fae]/90 mt-3 max-w-2xl">
                  A Cause We Care navigator will reach the family within <strong>48 hours</strong> to arrange lead screening, CLPPP follow-up, transportation, remediation, and housing — whatever they need. No SSN or full date of birth collected. HIPAA compliant. Michigan Public Act 146 of 2023.
                </p>
              </div>
            </div>
            <div className="shrink-0 bg-white rounded-lg p-3 shadow-md">
              <img src="/ddi-logo.png" alt="DEE DAVIS INC" className="h-16 object-contain" />
            </div>
          </div>

          {/* SHIELD acronym — mission variant — the brand moment for family-facing pages */}
          <div className="mt-7 pt-5 border-t-2 border-[#1f3fae]/25">
            <div className="flex items-center justify-between gap-4 flex-wrap mb-3">
              <div className="text-[10px] uppercase tracking-[0.28em] text-[#1f3fae] font-black">SHIELD stands for</div>
              <div className="text-[10px] text-[#1f3fae]/70 italic">Protecting Michigan's children from lead</div>
            </div>
            <SHIELDAcronym
              variant="mission"
              layout="grid"
              letterClass="text-3xl md:text-4xl font-black text-[#1f3fae] leading-none"
              wordClass="text-[10px] md:text-xs uppercase tracking-wider font-black text-[#1f3fae]/80 mt-1.5"
            />
          </div>
        </div>
      </header>

      {/* ───────── MODEL STRIP — "MDHHS refers · CWC navigates · DDI administers" ───────── */}
      <section className="bg-[#0a1f6e] border-b border-[#1c2f6a]">
        <div className="max-w-5xl mx-auto px-6 py-5">
          <div className="text-[10px] uppercase tracking-[0.28em] text-[#f5c23e] font-black text-center mb-3">
            How this works
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3 md:gap-4 items-stretch">
            <ModelStep stepNo="1" actor="MDHHS / Health Dept" verb="refers" detail="Case worker sends the family here. Zero cost to the state." />
            <ModelStep stepNo="2" actor="Cause We Care" verb="navigates" detail="Navigator contacts family within 48 hours, resolves barriers, follows through." />
            <ModelStep stepNo="3" actor="DEE DAVIS INC" verb="administers" detail="Manages compliance, billing, authorizations, and outcomes reporting." />
          </div>
        </div>
      </section>

      {/* ───────── TRUST STRIP ───────── */}
      <section className="bg-[#081849] border-b border-[#1c2f6a]">
        <div className="max-w-5xl mx-auto px-6 py-4 grid grid-cols-2 md:grid-cols-4 gap-4 text-xs">
          <TrustItem icon="48" label="Hours to first contact" />
          <TrustItem icon="0" label="SSN required" />
          <TrustItem icon="HIPAA" label="Compliant data handling" />
          <TrustItem icon="PA 146" label="Michigan mandate" />
        </div>
      </section>

      {/* ───────── BODY ───────── */}
      <main className="max-w-3xl mx-auto px-6 py-8">
        {submitted ? (
          <div className="bg-white rounded-2xl shadow-xl overflow-hidden">
            <div className="bg-[#f5c23e] px-6 py-5 border-b-4 border-[#e0a92e] text-center">
              <div className="inline-flex items-center justify-center w-14 h-14 rounded-full bg-[#1f3fae] mb-3">
                <svg viewBox="0 0 24 24" className="w-8 h-8 text-[#f5c23e]" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round"><path d="M5 12l5 5L20 7" /></svg>
              </div>
              <div className="text-2xl font-black text-[#1f3fae]">Referral received.</div>
              <div className="text-sm text-[#1f3fae]/80 mt-1">Reference #{submitted.reference}</div>
            </div>
            <div className="px-6 py-6 text-slate-700">
              <p className="text-base">{submitted.navigatorMessage}</p>
              <div className="mt-5 bg-slate-50 border border-slate-200 rounded-lg p-4 text-sm text-slate-600">
                A Cause We Care navigator will contact the primary family contact using the phone and email you provided. You'll receive a confirmation at <strong>{form.case_worker_email}</strong>.
              </div>
              <div className="mt-6 text-xs text-slate-500">
                Need to refer another family?{' '}
                <button
                  onClick={() => { setSubmitted(null); setStep(1); setForm({ ...form, family_name: '', address: '', city: '', zip: '', primary_contact_name: '', primary_contact_phone: '', primary_contact_email: '', children: [{ child_name: '', age_months: '', lead_test_status: 'Not Tested', blood_lead_level: '', clppp_case_number: '' }], services_requested: [], notes: '' }); }}
                  className="text-[#1f3fae] font-bold underline"
                >
                  Start a new referral
                </button>
              </div>
            </div>
          </div>
        ) : (
          <div className="bg-white rounded-2xl shadow-xl overflow-hidden">
            {/* Step rail */}
            <div className="bg-slate-50 border-b border-slate-200 px-6 py-4">
              <div className="flex items-center gap-1.5">
                {STEPS.map((s, i) => {
                  const active = step === s.id;
                  const done = step > s.id;
                  return (
                    <React.Fragment key={s.id}>
                      <button
                        onClick={() => done && setStep(s.id)}
                        disabled={!done && !active}
                        className="flex-1 text-left"
                      >
                        <div className="flex items-center gap-2 mb-1">
                          <div className={`w-6 h-6 rounded-full flex items-center justify-center text-[10px] font-black transition ${
                            active ? 'bg-[#1f3fae] text-white' :
                            done ? 'bg-[#f5c23e] text-[#1f3fae]' :
                            'bg-slate-200 text-slate-500'
                          }`}>
                            {done ? '✓' : s.id}
                          </div>
                          <div className={`text-[10px] uppercase tracking-wider font-black ${
                            active ? 'text-[#1f3fae]' : done ? 'text-slate-700' : 'text-slate-400'
                          }`}>{s.label}</div>
                        </div>
                        <div className={`h-1 rounded-full ${
                          active || done ? 'bg-[#f5c23e]' : 'bg-slate-200'
                        }`} />
                      </button>
                      {i < STEPS.length - 1 && <div className="w-2" />}
                    </React.Fragment>
                  );
                })}
              </div>
            </div>

            <div className="px-6 py-8">
              {/* ───── STEP 1 ───── */}
              {step === 1 && (
                <div>
                  <h2 className="text-xl font-black text-[#1f3fae] mb-1">Tell us about you</h2>
                  <p className="text-sm text-slate-500 mb-6">We'll confirm receipt at your email and CC you on navigator updates.</p>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <LightField label="Referral source *">
                      <select className={lightInput} value={form.referral_source} onChange={(e) => set('referral_source', e.target.value)}>
                        {['MDHHS', 'County Health Dept', 'Self (family member)', 'Community organization', 'Other'].map(s => <option key={s}>{s}</option>)}
                      </select>
                    </LightField>
                    <LightField label="Your agency / org">
                      <input className={lightInput} value={form.referring_agency} onChange={(e) => set('referring_agency', e.target.value)} placeholder="e.g. Wayne County Health Dept" />
                    </LightField>
                    <LightField label="Your full name *">
                      <input className={lightInput} value={form.case_worker_name} onChange={(e) => set('case_worker_name', e.target.value)} />
                    </LightField>
                    <LightField label="Your email *">
                      <input type="email" className={lightInput} value={form.case_worker_email} onChange={(e) => set('case_worker_email', e.target.value)} />
                    </LightField>
                    <LightField label="Your phone">
                      <input className={lightInput} value={form.case_worker_phone} onChange={(e) => set('case_worker_phone', e.target.value)} />
                    </LightField>
                    <LightField label="County the family lives in *">
                      <select className={lightInput} value={form.county} onChange={(e) => set('county', e.target.value)}>
                        {COUNTIES.map(c => <option key={c}>{c}</option>)}
                      </select>
                    </LightField>
                  </div>
                </div>
              )}

              {/* ───── STEP 2 ───── */}
              {step === 2 && (
                <div>
                  <h2 className="text-xl font-black text-[#1f3fae] mb-1">The family</h2>
                  <p className="text-sm text-slate-500 mb-6">Last name and best contact info so we can reach them. Addresses help with lead-remediation routing.</p>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <LightField label="Family last name"><input className={lightInput} value={form.family_name} onChange={(e) => set('family_name', e.target.value)} /></LightField>
                    <LightField label="Primary language">
                      <select className={lightInput} value={form.language} onChange={(e) => set('language', e.target.value)}>
                        {['English', 'Spanish', 'Arabic', 'Other'].map(l => <option key={l}>{l}</option>)}
                      </select>
                    </LightField>
                    <LightField label="Street address"><input className={lightInput} value={form.address} onChange={(e) => set('address', e.target.value)} /></LightField>
                    <div className="grid grid-cols-2 gap-3">
                      <LightField label="City"><input className={lightInput} value={form.city} onChange={(e) => set('city', e.target.value)} /></LightField>
                      <LightField label="ZIP"><input className={lightInput} value={form.zip} onChange={(e) => set('zip', e.target.value)} /></LightField>
                    </div>
                    <LightField label="Primary contact name"><input className={lightInput} value={form.primary_contact_name} onChange={(e) => set('primary_contact_name', e.target.value)} /></LightField>
                    <LightField label="Primary contact phone"><input className={lightInput} value={form.primary_contact_phone} onChange={(e) => set('primary_contact_phone', e.target.value)} /></LightField>
                    <LightField label="Primary contact email"><input className={lightInput} value={form.primary_contact_email} onChange={(e) => set('primary_contact_email', e.target.value)} /></LightField>
                    <div className="flex items-end gap-5 pb-2">
                      <label className="flex items-center gap-2 text-sm text-slate-700 cursor-pointer">
                        <input type="checkbox" checked={form.medicaid_enrolled} onChange={(e) => set('medicaid_enrolled', e.target.checked)} className="w-4 h-4 accent-[#1f3fae]" />
                        Medicaid enrolled
                      </label>
                      <label className="flex items-center gap-2 text-sm text-slate-700 cursor-pointer">
                        <input type="checkbox" checked={form.snap_enrolled} onChange={(e) => set('snap_enrolled', e.target.checked)} className="w-4 h-4 accent-[#1f3fae]" />
                        SNAP enrolled
                      </label>
                    </div>
                  </div>
                </div>
              )}

              {/* ───── STEP 3 ───── */}
              {step === 3 && (
                <div>
                  <div className="flex items-center justify-between mb-1">
                    <h2 className="text-xl font-black text-[#1f3fae]">Children</h2>
                    <button onClick={addChild} className="text-xs font-black text-[#1f3fae] hover:text-[#0a1f6e] border border-[#1f3fae]/40 bg-[#f5c23e]/30 hover:bg-[#f5c23e]/60 px-3 py-1.5 rounded-md">
                      + Add another child
                    </button>
                  </div>
                  <p className="text-sm text-slate-500 mb-6">First name only — we don't collect full DOB or SSN.</p>
                  <div className="space-y-3">
                    {form.children.map((child: any, i: number) => (
                      <div key={i} className="border border-slate-200 rounded-lg p-4 bg-slate-50">
                        <div className="flex items-center justify-between mb-3">
                          <div className="text-[10px] uppercase tracking-widest text-[#1f3fae] font-black">Child {i + 1}</div>
                          {form.children.length > 1 && (
                            <button onClick={() => removeChild(i)} className="text-[10px] text-rose-600 hover:text-rose-700 uppercase tracking-wider font-bold">Remove</button>
                          )}
                        </div>
                        <div className="grid grid-cols-1 md:grid-cols-5 gap-3">
                          <LightField label="First name"><input className={lightInput} value={child.child_name} onChange={(e) => updChild(i, 'child_name', e.target.value)} /></LightField>
                          <LightField label="Age (months)"><input type="number" className={lightInput} value={child.age_months} onChange={(e) => updChild(i, 'age_months', e.target.value)} /></LightField>
                          <LightField label="Test status">
                            <select className={lightInput} value={child.lead_test_status} onChange={(e) => updChild(i, 'lead_test_status', e.target.value)}>
                              {['Not Tested', 'Tested - Normal', 'Tested - Elevated', 'Confirmed EBL'].map(s => <option key={s}>{s}</option>)}
                            </select>
                          </LightField>
                          <LightField label="BLL (µg/dL)"><input type="number" step="0.1" className={lightInput} value={child.blood_lead_level} onChange={(e) => updChild(i, 'blood_lead_level', e.target.value)} /></LightField>
                          <LightField label="CLPPP case #"><input className={lightInput} value={child.clppp_case_number} onChange={(e) => updChild(i, 'clppp_case_number', e.target.value)} /></LightField>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* ───── STEP 4 ───── */}
              {step === 4 && (
                <div>
                  <h2 className="text-xl font-black text-[#1f3fae] mb-1">What does the family need?</h2>
                  <p className="text-sm text-slate-500 mb-6">Check all that apply — activation chains will fire automatically (e.g., lead remediation + housing for displaced families).</p>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                    {SERVICE_CHOICES.map(svc => {
                      const on = form.services_requested.includes(svc);
                      return (
                        <label key={svc} className={`flex items-center gap-3 border-2 rounded-lg px-4 py-3 cursor-pointer transition ${
                          on ? 'bg-[#f5c23e]/20 border-[#1f3fae] text-[#1f3fae]' : 'bg-white border-slate-200 text-slate-700 hover:border-slate-400'
                        }`}>
                          <input type="checkbox" checked={on} onChange={() => toggleService(svc)} className="w-4 h-4 accent-[#1f3fae]" />
                          <span className="text-sm font-bold">{svc}</span>
                        </label>
                      );
                    })}
                  </div>
                </div>
              )}

              {/* ───── STEP 5 ───── */}
              {step === 5 && (
                <div>
                  <h2 className="text-xl font-black text-[#1f3fae] mb-1">Urgency & notes</h2>
                  <p className="text-sm text-slate-500 mb-6">Last bit. If there's active displacement or a confirmed EBL, mark Emergency.</p>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                    <LightField label="Urgency">
                      <select className={lightInput} value={form.urgency} onChange={(e) => set('urgency', e.target.value)}>
                        {URGENCY_LEVELS.map(u => <option key={u}>{u}</option>)}
                      </select>
                    </LightField>
                    <div />
                  </div>
                  <LightField label="Additional notes / Best time to reach family">
                    <textarea className={lightInput} rows={4} value={form.notes} onChange={(e) => set('notes', e.target.value)} placeholder="Mom works 7-3, best reached evenings. Grandma helps with kids — spanish speaker in the household…" />
                  </LightField>

                  <div className="mt-6 bg-[#f5c23e]/15 border border-[#f5c23e] rounded-lg p-4">
                    <div className="text-[10px] uppercase tracking-widest text-[#1f3fae] font-black mb-2">Review</div>
                    <dl className="grid grid-cols-1 md:grid-cols-2 gap-y-1 gap-x-6 text-xs text-slate-700">
                      <Review label="Source" value={form.referring_agency || form.referral_source} />
                      <Review label="You" value={`${form.case_worker_name || '—'}${form.case_worker_email ? ` · ${form.case_worker_email}` : ''}`} />
                      <Review label="Family" value={form.family_name || '—'} />
                      <Review label="County" value={form.county} />
                      <Review label="Children" value={`${form.children.length}`} />
                      <Review label="Services" value={form.services_requested.length ? form.services_requested.join(', ') : '—'} />
                      <Review label="Medicaid / SNAP" value={`${form.medicaid_enrolled ? 'Medicaid' : ''}${form.medicaid_enrolled && form.snap_enrolled ? ' · ' : ''}${form.snap_enrolled ? 'SNAP' : ''}${!form.medicaid_enrolled && !form.snap_enrolled ? '—' : ''}`} />
                      <Review label="Urgency" value={form.urgency} />
                    </dl>
                  </div>
                </div>
              )}

              {error && (
                <div className="mt-5 bg-rose-50 border border-rose-200 rounded-lg px-4 py-3 text-sm text-rose-700">
                  {error}
                </div>
              )}
            </div>

            {/* Footer nav */}
            <div className="bg-slate-50 border-t border-slate-200 px-6 py-4 flex items-center justify-between">
              <button
                onClick={() => setStep(Math.max(1, step - 1))}
                disabled={step === 1}
                className="text-sm font-bold text-slate-600 hover:text-slate-900 disabled:text-slate-300 disabled:cursor-not-allowed"
              >
                ← Back
              </button>
              <div className="text-xs text-slate-500">Step {step} of {STEPS.length}</div>
              {step < STEPS.length ? (
                <button
                  onClick={() => canAdvance && setStep(step + 1)}
                  disabled={!canAdvance}
                  className="bg-[#1f3fae] hover:bg-[#0a1f6e] disabled:bg-slate-300 disabled:cursor-not-allowed text-white text-sm font-black px-6 py-2.5 rounded-md shadow"
                >
                  Continue →
                </button>
              ) : (
                <button
                  onClick={submit}
                  disabled={submitting}
                  className="bg-[#1f3fae] hover:bg-[#0a1f6e] disabled:opacity-60 text-white text-sm font-black px-6 py-2.5 rounded-md shadow-lg"
                >
                  {submitting ? 'Submitting…' : 'Submit referral →'}
                </button>
              )}
            </div>
          </div>
        )}

        {/* ───────── MILEADSAFE GRACEFUL FALLBACK ─────────
            Not every referral is a fit for CWC+DDI's navigation scope. Point
            families to the state's official intake as a first-class fallback —
            never as a competitor. Reinforces the "partner in the ecosystem"
            positioning rather than a replacement for state services. */}
        <div className="mt-6 bg-white/5 border border-[#1c2f6a] rounded-xl p-5 text-slate-200">
          <div className="text-[10px] uppercase tracking-[0.25em] text-[#f5c23e] font-black mb-2">
            Not a fit for Cause We Care navigation?
          </div>
          <p className="text-sm leading-relaxed">
            Every family in Michigan can apply directly to the State's Lead Services program. The state intake will identify which programs the family qualifies for — drinking water, home lead hazards, filter distribution, or blood-lead follow-up — even when CWC+DDI isn't the right navigation fit.
          </p>
          <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-3">
            <a
              href="https://www.michigan.gov/mileadsafe/lead-services/apply-for-home-lead-services"
              target="_blank"
              rel="noopener noreferrer"
              className="block bg-[#0a1f6e] hover:bg-[#1f3fae] border border-[#1f3fae] rounded-lg px-4 py-3 transition"
            >
              <div className="text-[10px] uppercase tracking-wider text-[#f5c23e] font-black">Michigan.gov</div>
              <div className="text-sm font-bold text-white mt-1">Apply for Home Lead Services →</div>
              <div className="text-[11px] text-[#8ea2d6] mt-1">State intake — routes family to qualifying lead programs</div>
            </a>
            <a
              href="https://www.michigan.gov/mileadsafe/get-ahead-of-lead"
              target="_blank"
              rel="noopener noreferrer"
              className="block bg-[#0a1f6e] hover:bg-[#1f3fae] border border-[#1f3fae] rounded-lg px-4 py-3 transition"
            >
              <div className="text-[10px] uppercase tracking-wider text-[#f5c23e] font-black">Michigan.gov</div>
              <div className="text-sm font-bold text-white mt-1">Get Ahead of Lead →</div>
              <div className="text-[11px] text-[#8ea2d6] mt-1">MiLeadSafe info hub — drinking water & lead programs</div>
            </a>
          </div>
        </div>
      </main>

      {/* ───────── FOOTER ───────── */}
      <footer className="border-t border-[#1c2f6a] bg-[#081849]">
        <div className="max-w-5xl mx-auto px-6 py-8 grid grid-cols-1 md:grid-cols-3 gap-6 items-center text-slate-300 text-sm">
          <div className="flex items-center gap-3">
            <img src="/cwc-logo.png" alt="Cause We Care" className="w-14 h-14 rounded-md object-contain bg-[#f5c23e] p-1" />
            <div>
              <div className="font-black text-white">Cause We Care</div>
              <div className="text-xs text-[#8ea2d6]">Michigan family navigation</div>
            </div>
          </div>
          <div className="text-xs text-[#8ea2d6] text-center leading-relaxed">
            <span className="text-[#f5c23e] font-black uppercase tracking-wider">Partner in Michigan's Lead-Safe Ecosystem</span><br />
            Operating under Michigan Public Act 146 of 2023.<br />
            HIPAA-compliant. Family data stored per MDHHS retention policy.
          </div>
          <div className="flex items-center gap-3 md:justify-end">
            <img src="/ddi-logo.png" alt="DEE DAVIS INC" className="w-14 h-14 rounded-md object-contain bg-white p-1" />
            <div className="text-right">
              <div className="font-black text-white">DEE DAVIS INC</div>
              <div className="text-xs text-[#8ea2d6]">Program administration layer</div>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

const ModelStep: React.FC<{ stepNo: string; actor: string; verb: string; detail: string }> = ({ stepNo, actor, verb, detail }) => (
  <div className="bg-[#081849] border border-[#1f3fae]/50 rounded-lg px-4 py-3 flex items-start gap-3">
    <div className="w-8 h-8 rounded-full bg-[#f5c23e] text-[#0a1f6e] font-black text-sm flex items-center justify-center shrink-0">
      {stepNo}
    </div>
    <div className="min-w-0">
      <div className="text-xs text-white">
        <span className="font-black">{actor}</span>{' '}
        <span className="text-[#f5c23e] italic font-bold">{verb}</span>
      </div>
      <div className="text-[11px] text-[#8ea2d6] mt-0.5 leading-snug">{detail}</div>
    </div>
  </div>
);

const TrustItem: React.FC<{ icon: string; label: string }> = ({ icon, label }) => (
  <div className="flex items-center gap-3">
    <div className="w-12 h-12 rounded-lg bg-[#f5c23e] text-[#1f3fae] font-black text-sm flex items-center justify-center shrink-0 border border-[#fcd75a]">
      {icon}
    </div>
    <div className="text-slate-200 leading-snug">{label}</div>
  </div>
);

const lightInput = 'w-full bg-white border border-slate-300 rounded-md px-3 py-2 text-sm text-slate-900 placeholder:text-slate-400 focus:border-[#1f3fae] focus:ring-2 focus:ring-[#f5c23e]/30 focus:outline-none';

const LightField: React.FC<{ label: string; children: React.ReactNode }> = ({ label, children }) => (
  <label className="block">
    <span className="block text-[11px] uppercase tracking-wider text-slate-600 font-black mb-1">{label}</span>
    {children}
  </label>
);

const Review: React.FC<{ label: string; value: string }> = ({ label, value }) => (
  <div className="flex gap-2">
    <dt className="text-slate-500 min-w-[110px]">{label}:</dt>
    <dd className="text-slate-900 font-semibold flex-1">{value || '—'}</dd>
  </div>
);

export default PublicReferrerIntake;
