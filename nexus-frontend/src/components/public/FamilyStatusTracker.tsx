import React, { useCallback, useMemo, useState } from 'react';
import { api } from '../../api/client';

/*
 * SHIELD — Family Status Tracker
 *
 * Public page at /status. No login, no account. Families enter their
 * SHIELD case number + last name and see exactly where things stand.
 *
 * Design principles:
 *   - Mobile-first (most parents will open this from a text link)
 *   - Emoji iconography for warmth and immediate recognition
 *   - Zero clinical jargon — plain language a stressed parent can scan
 *   - MDHHS palette so it feels like the state ecosystem they know
 */

const MDHHS_TEAL = '#026666';
const MDHHS_NAVY = '#17415f';
const CWC_YELLOW = '#f5c23e';
const CWC_COBALT = '#1f3fae';

const SERVICE_COLOR_MAP: Record<string, string> = {
  'Blood Lead Level (BLL) Testing':             '#026666',
  'Lead Screening':                             '#026666',
  'CLPPP Case Management':                      '#17415f',
  'CLPPP Follow-up':                            '#17415f',
  'NEMT — Non-Emergency Medical Transportation': '#CA4D22',
  'NEMT':                                       '#CA4D22',
  'Lead Remediation Coordination':               '#862074',
  'Lead Remediation':                            '#862074',
  'Housing Navigation':                          '#093C44',
  'Housing':                                     '#093C44',
  'MIBridges Benefits Navigation':               '#76BAB2',
  'Food Navigation':                             '#76BAB2',
  'Filter Safety Net / Drinking Water':          '#046791',
  'Filter Safety Net':                           '#046791',
  'Community Health Worker Home Visit':           '#2F8D98',
  'Nurse Home Visit':                            '#115E6E',
  'Drug Testing':                                '#046791',
  'DNA':                                         '#2F8D98',
  'Specimen Transport':                          '#115E6E',
  'Medical Monitoring':                          '#026666',
};

const SERVICE_EMOJI: Record<string, string> = {
  'Blood Lead Level (BLL) Testing': '🩸',
  'Lead Screening':                 '🩸',
  'CLPPP Case Management':          '📋',
  'CLPPP Follow-up':                '📋',
  'NEMT — Non-Emergency Medical Transportation': '🚕',
  'NEMT':                           '🚕',
  'Lead Remediation Coordination':  '🛠️',
  'Lead Remediation':               '🛠️',
  'Housing Navigation':             '🏩',
  'Housing':                        '🏩',
  'MIBridges Benefits Navigation':  '🤝',
  'Food Navigation':                '🤝',
  'Filter Safety Net / Drinking Water': '💧',
  'Filter Safety Net':              '💧',
  'Community Health Worker Home Visit': '💛',
  'Nurse Home Visit':               '🩺',
  'Drug Testing':                   '🧪',
  'DNA':                            '🧬',
  'Specimen Transport':             '📦',
  'Medical Monitoring':             '🩺',
};

const SERVICE_PLAIN: Record<string, string> = {
  'Blood Lead Level (BLL) Testing':             'Blood lead test',
  'Lead Screening':                             'Blood lead test',
  'CLPPP Case Management':                      'Lead program follow-up',
  'CLPPP Follow-up':                            'Lead program follow-up',
  'NEMT — Non-Emergency Medical Transportation': 'Your ride to appointments',
  'NEMT':                                       'Your ride to appointments',
  'Lead Remediation Coordination':               'Home repairs underway',
  'Lead Remediation':                            'Home repairs underway',
  'Housing Navigation':                          'Temporary housing while your home is fixed',
  'Housing':                                     'Temporary housing while your home is fixed',
  'MIBridges Benefits Navigation':               'Benefits & assistance',
  'Food Navigation':                             'Benefits & assistance',
  'Filter Safety Net / Drinking Water':          'Safe drinking water',
  'Filter Safety Net':                           'Safe drinking water',
  'Community Health Worker Home Visit':           'Community health visit',
  'Nurse Home Visit':                            'Nurse home visit',
  'Drug Testing':                                'Drug testing',
  'DNA':                                         'DNA testing',
  'Specimen Transport':                          'Lab specimen pickup',
  'Medical Monitoring':                          'Medical monitoring',
};

interface TimelineStage {
  key: string;
  emoji: string;
  label: string;
  detail: string;
  reached: boolean;
  current: boolean;
}

function buildTimeline(stage: string, milestones: any[]): TimelineStage[] {
  const stageOrder = ['Intake', 'Triage', 'Outreach', 'Engaged', 'In Service', 'Closed'];
  const stageIdx = Math.max(0, stageOrder.indexOf(stage));

  const defs: { key: string; emoji: string; label: string; detail: string }[] = [
    { key: 'Intake',      emoji: '📩', label: 'We got your info',           detail: 'Everything came through safe and sound. We\'re getting started.' },
    { key: 'Triage',      emoji: '🔍', label: 'Figuring out what you need', detail: 'Our team is looking at your family\'s situation and putting together the right help.' },
    { key: 'Outreach',    emoji: '📞', label: 'Someone\'s calling you soon', detail: 'A real person from our team is reaching out to say hi, answer your questions, and set up your first visit.' },
    { key: 'Engaged',     emoji: '🤝', label: 'You\'re connected',         detail: 'You have a navigator now — they\'re your go-to person. They handle the coordination so you don\'t have to.' },
    { key: 'In Service',  emoji: '⚡', label: 'Things are moving',         detail: 'Your services are happening. Your navigator is keeping everything on track so you can focus on your family.' },
    { key: 'Closed',      emoji: '✅', label: 'All done',                  detail: 'Everything is wrapped up. If you ever need us again, we\'re just a call or text away. 💛' },
  ];

  return defs.map((d, i) => ({
    ...d,
    reached: i <= stageIdx,
    current: i === stageIdx,
  }));
}

function formatDate(iso: string | undefined): string {
  if (!iso) return '';
  try {
    const d = new Date(iso);
    return d.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' });
  } catch { return ''; }
}

function formatTime(iso: string | undefined): string {
  if (!iso) return '';
  try {
    const d = new Date(iso);
    return d.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' });
  } catch { return ''; }
}

export default function FamilyStatusTracker() {
  const [caseNumber, setCaseNumber] = useState('');
  const [lastName, setLastName] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<any>(null);

  const lookup = useCallback(async () => {
    const cn = caseNumber.trim().toUpperCase();
    const ln = lastName.trim();
    if (!cn || !ln) { setError('We just need both your case number and last name to look you up.'); return; }
    setLoading(true);
    setError(null);
    try {
      const res: any = await api.shieldFamilyLookup(cn, ln);
      if (res?.success && res?.referral) {
        setData(res);
      } else {
        setError(res?.error || 'Hmm, we couldn\'t find that. Double-check the case number from your text or email, and make sure the last name matches.');
        setData(null);
      }
    } catch (e: any) {
      setError('Something didn\'t work right — try again in a sec. If it keeps happening, just call your navigator.');
      setData(null);
    } finally {
      setLoading(false);
    }
  }, [caseNumber, lastName]);

  const referral = data?.referral;
  const family = data?.family;
  const navigator = data?.navigator;
  const activations = data?.activations || [];
  const appointments = useMemo(() =>
    activations.filter((a: any) => a.appointment_date && a.status !== 'Cancelled')
      .sort((a: any, b: any) => new Date(a.appointment_date).getTime() - new Date(b.appointment_date).getTime()),
    [activations]
  );

  const stage = referral?.stage || referral?.status || 'Intake';
  const timeline = useMemo(() => buildTimeline(stage, data?.milestones || []), [stage, data?.milestones]);
  const services = referral?.services_requested || [];

  return (
    <div className="min-h-screen bg-gradient-to-b from-[#f5c23e]/10 to-white">
      {/* ───── HEADER ───── */}
      <header className="bg-gradient-to-br from-[#f5c23e] to-[#e0a92e] border-b-4 border-[#1f3fae]">
        <div className="max-w-lg mx-auto px-5 py-7 text-center">
          <img src="/cwc-logo.png" alt="Cause We Care" className="w-16 h-16 rounded-xl object-contain bg-white/60 p-1.5 shadow-md mx-auto mb-3" />
          <h1 className="text-2xl font-black tracking-tight text-[#1f3fae]">Care. Navigate. Transform.</h1>
          <p className="text-xs text-[#1f3fae]/50 italic mt-0.5">More than a mission — a movement.</p>
          <p className="text-sm text-[#1f3fae]/70 mt-2 leading-relaxed max-w-sm mx-auto">
            See what's happening with your family's care — every step, all in one place. You're not alone in this.
          </p>
        </div>
      </header>

      <main className="max-w-lg mx-auto px-5 py-6">
        {!data ? (
          /* ───── LOOKUP FORM ───── */
          <div className="bg-white rounded-2xl shadow-lg overflow-hidden">
            <div className="px-5 py-5 border-b border-slate-100">
              <h2 className="text-lg font-black text-slate-800">👋 Let's find your info</h2>
              <p className="text-sm text-slate-500 mt-1">Use the number from the text or email you received, and your last name. That's it.</p>
            </div>
            <div className="px-5 py-5 space-y-4">
              <div>
                <label className="block text-xs font-bold text-slate-600 mb-1.5">Your case number</label>
                <input
                  type="text"
                  value={caseNumber}
                  onChange={(e) => setCaseNumber(e.target.value.toUpperCase())}
                  placeholder="SHD-2026-0001"
                  className="w-full border-2 border-slate-200 rounded-xl px-4 py-3 text-base font-mono tracking-wider focus:border-[#1f3fae] focus:ring-2 focus:ring-[#1f3fae]/20 outline-none transition placeholder:text-slate-300"
                  onKeyDown={(e) => e.key === 'Enter' && lookup()}
                />
              </div>
              <div>
                <label className="block text-xs font-bold text-slate-600 mb-1.5">Your last name</label>
                <input
                  type="text"
                  value={lastName}
                  onChange={(e) => setLastName(e.target.value)}
                  placeholder="Smith"
                  className="w-full border-2 border-slate-200 rounded-xl px-4 py-3 text-base focus:border-[#1f3fae] focus:ring-2 focus:ring-[#1f3fae]/20 outline-none transition placeholder:text-slate-300"
                  onKeyDown={(e) => e.key === 'Enter' && lookup()}
                />
              </div>
              {error && (
                <div className="bg-rose-50 border border-rose-200 rounded-xl px-4 py-3 text-sm text-rose-700">
                  {error}
                </div>
              )}
              <button
                onClick={lookup}
                disabled={loading}
                className="w-full bg-[#1f3fae] hover:bg-[#0a1f6e] disabled:bg-slate-300 text-white text-base font-black py-3.5 rounded-xl shadow-md transition"
              >
                {loading ? 'One moment...' : 'Show me my progress'}
              </button>
            </div>
            <div className="bg-slate-50 px-5 py-4 border-t border-slate-100">
              <p className="text-xs text-slate-500 text-center leading-relaxed">
                🔒 Your information is safe with us. Nobody can see your details without both the case number and your name.
              </p>
            </div>
          </div>
        ) : (
          /* ───── STATUS VIEW ───── */
          <div className="space-y-5">
            {/* Case badge */}
            <div className="bg-white rounded-2xl shadow-lg overflow-hidden">
              <div className="bg-gradient-to-r from-[#f5c23e] to-[#e0a92e] px-5 py-4 border-b-4 border-[#1f3fae]">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-xs text-[#1f3fae]/70 font-bold uppercase tracking-wider">🛡️ Your case</div>
                    <div className="text-xl font-mono font-black tracking-wider mt-0.5 text-[#1f3fae]">
                      {referral?.referral_id || caseNumber}
                    </div>
                  </div>
                  <img src="/cwc-logo.png" alt="CWC" className="w-10 h-10 rounded-lg object-contain bg-white/60 p-1 shadow-sm" />
                </div>
                {family?.family_name && (
                  <div className="text-sm text-[#1f3fae]/70 mt-1">{family.family_name} Family</div>
                )}
              </div>

              {/* Current status hero */}
              <div className="px-5 py-5 text-center border-b border-slate-100">
                <div className="text-4xl mb-2">{timeline.find(t => t.current)?.emoji || '📩'}</div>
                <div className="text-lg font-black text-slate-800">
                  {timeline.find(t => t.current)?.label || 'Referral received'}
                </div>
                <p className="text-sm text-slate-500 mt-1 max-w-xs mx-auto leading-relaxed">
                  {timeline.find(t => t.current)?.detail}
                </p>
              </div>

              {/* Timeline */}
              <div className="px-5 py-5">
                <div className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-4">Where things stand</div>
                <div className="space-y-0">
                  {timeline.map((t, i) => (
                    <div key={t.key} className="flex items-start gap-3">
                      {/* Vertical line + dot */}
                      <div className="flex flex-col items-center">
                        <div className={`w-8 h-8 rounded-full flex items-center justify-center text-base shrink-0 ${
                          t.current ? 'bg-[#1f3fae] text-white shadow-md ring-4 ring-[#f5c23e]/40' :
                          t.reached ? 'bg-[#f5c23e]/30 text-[#1f3fae]' :
                          'bg-slate-100 text-slate-300'
                        }`}>
                          {t.reached ? t.emoji : '○'}
                        </div>
                        {i < timeline.length - 1 && (
                          <div className={`w-0.5 h-8 ${t.reached ? 'bg-[#f5c23e]/50' : 'bg-slate-200'}`} />
                        )}
                      </div>
                      <div className={`pt-1 pb-3 ${t.current ? '' : t.reached ? 'opacity-70' : 'opacity-40'}`}>
                        <div className={`text-sm font-bold ${t.current ? 'text-[#1f3fae]' : 'text-slate-700'}`}>
                          {t.label}
                          {t.current && <span className="ml-2 inline-flex items-center text-[10px] font-black uppercase tracking-wider bg-[#f5c23e] text-[#1f3fae] px-2 py-0.5 rounded-full">Now</span>}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* ───── NAVIGATOR CARD ───── */}
            {navigator && (
              <div className="bg-white rounded-2xl shadow-lg overflow-hidden">
                <div className="px-5 py-4 border-b border-slate-100">
                  <div className="text-xs font-bold text-slate-500 uppercase tracking-wider">Your Person</div>
                  <div className="text-sm text-slate-400 mt-0.5">This is who's looking out for your family</div>
                </div>
                <div className="px-5 py-4 flex items-center gap-4">
                  <div className="w-14 h-14 rounded-full bg-gradient-to-br from-[#f5c23e] to-[#e0a92e] flex items-center justify-center text-2xl shrink-0 shadow-sm">
                    💛
                  </div>
                  <div className="min-w-0">
                    <div className="text-base font-black text-slate-800">{navigator.name || 'Your Navigator'}</div>
                    <div className="text-sm text-slate-500">Cause We Care · Here to help</div>
                  </div>
                </div>
                <div className="px-5 pb-5 grid grid-cols-2 gap-2">
                  {navigator.phone && (
                    <a
                      href={`tel:${navigator.phone}`}
                      className="flex items-center justify-center gap-2 bg-[#1f3fae] text-white text-sm font-bold py-3 rounded-xl shadow-sm hover:bg-[#0a1f6e] transition"
                    >
                      📞 Call
                    </a>
                  )}
                  {navigator.phone && (
                    <a
                      href={`sms:${navigator.phone}`}
                      className="flex items-center justify-center gap-2 bg-[#f5c23e] border-2 border-[#f5c23e] text-[#1f3fae] text-sm font-bold py-3 rounded-xl hover:bg-[#e0a92e] transition"
                    >
                      💬 Text
                    </a>
                  )}
                  {navigator.email && !navigator.phone && (
                    <a
                      href={`mailto:${navigator.email}`}
                      className="col-span-2 flex items-center justify-center gap-2 bg-[#1f3fae] text-white text-sm font-bold py-3 rounded-xl shadow-sm hover:bg-[#0a1f6e] transition"
                    >
                      ✉️ Email your navigator
                    </a>
                  )}
                </div>
              </div>
            )}

            {/* ───── SERVICES ───── */}
            {services.length > 0 && (
              <div className="bg-white rounded-2xl shadow-lg overflow-hidden">
                <div className="px-5 py-4 border-b border-slate-100">
                  <div className="text-xs font-bold text-slate-500 uppercase tracking-wider">What We're Doing For You</div>
                  <div className="text-sm text-slate-400 mt-0.5">Every service your family is receiving — all in one place</div>
                </div>
                <div className="divide-y divide-slate-100">
                  {services.map((svc: string) => {
                    const activation = activations.find((a: any) => a.service_line === svc || a.service_line === SERVICE_PLAIN[svc]);
                    const status = activation?.status || 'Scheduled';
                    const isComplete = status === 'Completed';
                    const hex = SERVICE_COLOR_MAP[svc] || MDHHS_TEAL;
                    return (
                      <div key={svc} className="px-5 py-3.5 flex items-center gap-3">
                        <div className="w-10 h-10 rounded-xl flex items-center justify-center text-lg shrink-0" style={{ backgroundColor: `${hex}15`, color: hex }}>
                          {SERVICE_EMOJI[svc] || '📌'}
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2">
                            <span className="w-2 h-2 rounded-full shrink-0" style={{ backgroundColor: hex }} />
                            <span className="text-sm font-bold" style={{ color: hex }}>{SERVICE_PLAIN[svc] || svc}</span>
                          </div>
                          {activation?.vendor && (
                            <div className="text-xs text-slate-400 ml-4">{activation.vendor}</div>
                          )}
                        </div>
                        <div className={`text-xs font-bold px-2.5 py-1 rounded-full ${
                          isComplete ? 'bg-emerald-50 text-emerald-700' :
                          status === 'In Progress' ? 'bg-sky-50 text-sky-700' :
                          'bg-amber-50 text-amber-700'
                        }`}>
                          {isComplete ? '✅ Done' : status === 'In Progress' ? '⚡ Active' : '🕐 Upcoming'}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* ───── APPOINTMENTS ───── */}
            {appointments.length > 0 && (
              <div className="bg-white rounded-2xl shadow-lg overflow-hidden">
                <div className="px-5 py-4 border-b border-slate-100">
                  <div className="text-xs font-bold text-slate-500 uppercase tracking-wider">📅 Coming Up</div>
                  <div className="text-sm text-slate-400 mt-0.5">Your next visits and appointments</div>
                </div>
                <div className="divide-y divide-slate-100">
                  {appointments.map((appt: any, i: number) => {
                    const apptHex = SERVICE_COLOR_MAP[appt.service_line] || MDHHS_TEAL;
                    return (
                    <div key={i} className="px-5 py-4">
                      <div className="flex items-start gap-3">
                        <div className="rounded-xl w-12 h-12 flex flex-col items-center justify-center shrink-0" style={{ backgroundColor: `${apptHex}15`, color: apptHex }}>
                          <div className="text-xs font-black leading-none">{formatDate(appt.appointment_date).split(' ')[0]}</div>
                          <div className="text-lg font-black leading-none">{new Date(appt.appointment_date).getDate()}</div>
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="text-sm font-bold flex items-center gap-1.5" style={{ color: apptHex }}>
                            {SERVICE_EMOJI[appt.service_line] || '📅'} {SERVICE_PLAIN[appt.service_line] || appt.service_line}
                          </div>
                          <div className="text-xs text-slate-500 mt-0.5">
                            {formatDate(appt.appointment_date)} at {formatTime(appt.appointment_date)}
                          </div>
                          {appt.vendor && (
                            <div className="text-xs text-slate-400 mt-0.5">with {appt.vendor}</div>
                          )}
                          {appt.notes && (
                            <div className="text-xs text-slate-500 mt-1.5 bg-slate-50 rounded-lg px-3 py-2 leading-relaxed">{appt.notes}</div>
                          )}
                        </div>
                      </div>
                    </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* ───── RESOURCES ───── */}
            <div className="bg-white rounded-2xl shadow-lg overflow-hidden">
              <div className="px-5 py-4 border-b border-slate-100">
                <div className="text-xs font-bold text-slate-500 uppercase tracking-wider">More Help For Your Family</div>
                <div className="text-sm text-slate-400 mt-0.5">Free programs you may qualify for — tap any link to learn more</div>
              </div>
              <div className="divide-y divide-slate-100">
                <ResourceLink emoji="🏥" title="Get Ahead of Lead" desc="Michigan's free lead-safe program — learn what's available" url="https://michigan.gov/GetAheadofLead" />
                <ResourceLink emoji="📱" title="Apply for Home Lead Services" desc="Free application to get your home tested and fixed" url="https://www.michigan.gov/mileadsafe/lead-services/apply-for-home-lead-services" />
                <ResourceLink emoji="🛒" title="MIBridges" desc="Apply for food, cash, childcare and medical help" url="https://newmibridges.michigan.gov/" />
                <ResourceLink emoji="🍎" title="WIC" desc="Free food and nutrition for you and your baby" url="https://www.michigan.gov/mdhhs/assistance-programs/wic" />
                <ResourceLink emoji="🏡" title="Housing Help" desc="Emergency housing, rental assistance, and more" url="https://www.michigan.gov/mshda" />
                <ResourceLink emoji="💡" title="Help With Bills" desc="Assistance with heating and electric bills" url="https://www.michigan.gov/mdhhs/assistance-programs/energy" />
              </div>
            </div>

            {/* ───── REASSURANCE + FOOTER ───── */}
            <div className="bg-[#f5c23e]/15 border border-[#f5c23e]/40 rounded-2xl px-5 py-4 text-center">
              <div className="text-base mb-1">💛</div>
              <p className="text-sm text-slate-600 leading-relaxed">
                You don't have to figure this out alone. Your navigator is here to handle the hard parts — you just focus on your family.
              </p>
            </div>

            <div className="flex flex-col gap-2 pt-2 pb-8">
              <button
                onClick={() => { setData(null); setCaseNumber(''); setLastName(''); setError(null); }}
                className="w-full bg-white border-2 border-slate-200 text-slate-600 text-sm font-bold py-3 rounded-xl hover:border-slate-400 transition"
              >
                ← Check a different case
              </button>
              <div className="text-center text-xs text-slate-400 mt-2 leading-relaxed">
                Questions? Call Cause We Care — we're happy to help.
                <br />
                <span className="text-[#1f3fae] font-black mt-1 block">Care. Navigate. Transform.</span>
                <span className="text-[#1f3fae]/50 italic block text-[10px]">More than a mission — a movement.</span>
                <span className="text-slate-300 block mt-0.5">Cause We Care + Dee Davis Inc · Partner in Michigan's lead-safe ecosystem</span>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

function ResourceLink({ emoji, title, desc, url }: { emoji: string; title: string; desc: string; url: string }) {
  return (
    <a href={url} target="_blank" rel="noopener noreferrer" className="block px-5 py-3.5 hover:bg-slate-50 transition group">
      <div className="flex items-center gap-3">
        <div className="text-2xl shrink-0">{emoji}</div>
        <div className="flex-1 min-w-0">
          <div className="text-sm font-bold text-slate-800 group-hover:text-[#1f3fae] transition">{title}</div>
          <div className="text-xs text-slate-500">{desc}</div>
        </div>
        <div className="text-slate-300 group-hover:text-[#1f3fae] transition shrink-0">→</div>
      </div>
    </a>
  );
}
