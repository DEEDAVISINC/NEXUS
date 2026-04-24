import React, { useState, useEffect, useMemo, useCallback } from 'react';

const API_BASE = process.env.REACT_APP_API_BASE || 'http://127.0.0.1:8000';

const COLORS = {
  navy: '#0B1628',
  navyMid: '#142039',
  navyLight: '#1E2F4D',
  gold: '#C9A84C',
  goldLight: '#E8C97A',
  goldDim: 'rgba(201,168,76,0.12)',
  cream: '#F5F0E8',
  white: '#FFFFFF',
  muted: 'rgba(245,240,232,0.55)',
  border: 'rgba(201,168,76,0.25)',
  success: '#2D9B6F',
  error: '#C0392B',
};

const styles = {
  wrap: {
    fontFamily: "'DM Serif Display', Georgia, serif",
    background: COLORS.navy,
    minHeight: '100vh',
    color: COLORS.cream,
    position: 'relative' as const,
    overflow: 'hidden',
  },
  noise: {
    position: 'fixed' as const,
    inset: 0,
    opacity: 0.035,
    backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='4'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E")`,
    pointerEvents: 'none' as const,
    zIndex: 0,
  },
  glow: {
    position: 'fixed' as const,
    top: 0,
    right: 0,
    width: '55%',
    height: '55%',
    background: 'radial-gradient(ellipse at 80% 20%, rgba(201,168,76,0.06) 0%, transparent 65%)',
    pointerEvents: 'none' as const,
    zIndex: 0,
  },
  inner: { position: 'relative' as const, zIndex: 1, maxWidth: 680, margin: '0 auto', padding: '2.5rem 1.5rem 4rem' },
};

export interface QualificationResult {
  eligible: boolean | 'conditional';
  confidence: string;
  headline: string;
  summary: string;
  estimatedRefund: string;
  feeRate: number;
  ddiFee: string;
  flags: string[];
  nextSteps: string[];
  urgency: string;
  urgencyNote: string;
}

interface BizData {
  bizName: string;
  dba: string;
  ein: string;
  contact: string;
  title: string;
  email: string;
  phone: string;
  state: string;
}

interface ImportData {
  importerOfRecord: string;
  goodsDescription: string;
  estimatedTariff: string;
  entryCount: string;
  acePortal: string;
  hasBroker: string;
}

function buildCapePayload(biz: BizData, imp: ImportData) {
  return {
    legal_business_name: biz.bizName,
    dba: biz.dba || undefined,
    ein: biz.ein,
    contact_name: biz.contact,
    title: biz.title || undefined,
    email: biz.email,
    phone: biz.phone || undefined,
    state: biz.state,
    importer_of_record: imp.importerOfRecord,
    goods_description: imp.goodsDescription,
    estimated_tariff_band: imp.estimatedTariff,
    entry_count_band: imp.entryCount || undefined,
    ace_portal_status: imp.acePortal || undefined,
    has_customs_broker: imp.hasBroker || undefined,
  };
}

function StepDots({ current, total }: { current: number; total: number }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 8, justifyContent: 'center', marginBottom: '2rem' }}>
      {Array.from({ length: total }, (_, i) => (
        <div
          key={i}
          style={{
            width: i === current ? 28 : 8,
            height: 8,
            borderRadius: 4,
            background: i < current ? COLORS.gold : i === current ? COLORS.gold : COLORS.border,
            opacity: i < current ? 0.5 : 1,
            transition: 'all 0.3s ease',
          }}
        />
      ))}
    </div>
  );
}

function Field({
  label,
  required,
  children,
  hint,
}: {
  label: string;
  required?: boolean;
  children: React.ReactNode;
  hint?: string;
}) {
  return (
    <div style={{ marginBottom: '1.1rem' }}>
      <label
        style={{
          display: 'block',
          fontFamily: "'DM Sans', sans-serif",
          fontSize: '0.68rem',
          fontWeight: 700,
          letterSpacing: '0.18em',
          textTransform: 'uppercase',
          color: COLORS.gold,
          marginBottom: '0.35rem',
        }}
      >
        {label}
        {required && <span style={{ color: COLORS.error, marginLeft: 3 }}>*</span>}
      </label>
      {children}
      {hint && (
        <p
          style={{
            fontFamily: "'DM Sans', sans-serif",
            fontSize: '0.72rem',
            color: COLORS.muted,
            marginTop: '0.3rem',
            lineHeight: 1.5,
          }}
        >
          {hint}
        </p>
      )}
    </div>
  );
}

function Input({
  value,
  onChange,
  placeholder,
  type = 'text',
}: {
  value: string;
  onChange: (v: string) => void;
  placeholder?: string;
  type?: string;
}) {
  const [focused, setFocused] = useState(false);
  return (
    <input
      type={type}
      value={value}
      onChange={(e) => onChange(e.target.value)}
      placeholder={placeholder}
      onFocus={() => setFocused(true)}
      onBlur={() => setFocused(false)}
      style={{
        width: '100%',
        background: 'rgba(255,255,255,0.04)',
        border: `1px solid ${focused ? COLORS.gold : COLORS.border}`,
        color: COLORS.cream,
        fontFamily: "'DM Sans', sans-serif",
        fontSize: '0.9rem',
        padding: '0.8rem 1rem',
        outline: 'none',
        boxSizing: 'border-box',
        transition: 'border-color 0.2s',
      }}
    />
  );
}

function Select({
  value,
  onChange,
  options,
}: {
  value: string;
  onChange: (v: string) => void;
  options: { value: string; label: string }[];
}) {
  const [focused, setFocused] = useState(false);
  return (
    <select
      value={value}
      onChange={(e) => onChange(e.target.value)}
      onFocus={() => setFocused(true)}
      onBlur={() => setFocused(false)}
      style={{
        width: '100%',
        background: COLORS.navyMid,
        border: `1px solid ${focused ? COLORS.gold : COLORS.border}`,
        color: value ? COLORS.cream : COLORS.muted,
        fontFamily: "'DM Sans', sans-serif",
        fontSize: '0.9rem',
        padding: '0.8rem 1rem',
        outline: 'none',
        boxSizing: 'border-box',
        cursor: 'pointer',
        appearance: 'none',
      }}
    >
      {options.map((o) => (
        <option key={o.value} value={o.value} style={{ background: COLORS.navyMid }}>
          {o.label}
        </option>
      ))}
    </select>
  );
}

function Btn({
  onClick,
  children,
  variant = 'primary',
  disabled,
  loading,
}: {
  onClick: () => void;
  children: React.ReactNode;
  variant?: 'primary' | 'secondary';
  disabled?: boolean;
  loading?: boolean;
}) {
  const isPrimary = variant === 'primary';
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={disabled || loading}
      style={{
        background: isPrimary ? COLORS.gold : 'transparent',
        color: isPrimary ? COLORS.navy : COLORS.cream,
        border: isPrimary ? 'none' : `1px solid ${COLORS.border}`,
        fontFamily: "'DM Sans', sans-serif",
        fontWeight: 700,
        fontSize: '0.8rem',
        letterSpacing: '0.12em',
        textTransform: 'uppercase',
        padding: '0.9rem 2rem',
        cursor: disabled || loading ? 'not-allowed' : 'pointer',
        opacity: disabled || loading ? 0.6 : 1,
        transition: 'all 0.2s',
        minWidth: 130,
      }}
    >
      {loading ? 'Processing…' : children}
    </button>
  );
}

function Card({ children, accent }: { children: React.ReactNode; accent?: boolean }) {
  return (
    <div
      style={{
        background: COLORS.navyMid,
        border: `1px solid ${COLORS.border}`,
        borderLeft: accent ? `3px solid ${COLORS.gold}` : `1px solid ${COLORS.border}`,
        padding: '2rem 1.8rem',
        marginBottom: '1.5rem',
      }}
    >
      {children}
    </div>
  );
}

const US_STATES = [
  'AL',
  'AK',
  'AZ',
  'AR',
  'CA',
  'CO',
  'CT',
  'DE',
  'FL',
  'GA',
  'HI',
  'ID',
  'IL',
  'IN',
  'IA',
  'KS',
  'KY',
  'LA',
  'ME',
  'MD',
  'MA',
  'MI',
  'MN',
  'MS',
  'MO',
  'MT',
  'NE',
  'NV',
  'NH',
  'NJ',
  'NM',
  'NY',
  'NC',
  'ND',
  'OH',
  'OK',
  'OR',
  'PA',
  'RI',
  'SC',
  'SD',
  'TN',
  'TX',
  'UT',
  'VT',
  'VA',
  'WA',
  'WV',
  'WI',
  'WY',
];

function StepBusinessInfo({
  data,
  setData,
  onNext,
}: {
  data: BizData;
  setData: React.Dispatch<React.SetStateAction<BizData>>;
  onNext: () => void;
}) {
  const valid = data.bizName && data.contact && data.email && data.state && data.ein;
  return (
    <>
      <div style={{ marginBottom: '1.8rem' }}>
        <p
          style={{
            fontFamily: "'DM Sans', sans-serif",
            fontSize: '0.68rem',
            fontWeight: 700,
            letterSpacing: '0.22em',
            textTransform: 'uppercase',
            color: COLORS.gold,
            marginBottom: '0.5rem',
          }}
        >
          Step 1 of 4
        </p>
        <h2 style={{ fontFamily: "'DM Serif Display', serif", fontSize: '1.7rem', color: COLORS.white, margin: 0, lineHeight: 1.2 }}>
          Your Business
        </h2>
        <p style={{ fontFamily: "'DM Sans', sans-serif", fontSize: '0.9rem', color: COLORS.muted, marginTop: '0.5rem' }}>
          Tell us who we&apos;re working with.
        </p>
      </div>
      <Card accent>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0 1rem' }}>
          <div style={{ gridColumn: '1 / -1' }}>
            <Field label="Business Legal Name" required>
              <Input value={data.bizName} onChange={(v) => setData({ ...data, bizName: v })} placeholder="ABC Imports LLC" />
            </Field>
          </div>
          <Field label="DBA (if any)">
            <Input value={data.dba} onChange={(v) => setData({ ...data, dba: v })} placeholder="Optional" />
          </Field>
          <Field label="EIN" required>
            <Input value={data.ein} onChange={(v) => setData({ ...data, ein: v })} placeholder="XX-XXXXXXX" />
          </Field>
          <div style={{ gridColumn: '1 / -1' }}>
            <Field label="Your Name" required>
              <Input value={data.contact} onChange={(v) => setData({ ...data, contact: v })} placeholder="Full name" />
            </Field>
          </div>
          <Field label="Title / Role">
            <Input value={data.title} onChange={(v) => setData({ ...data, title: v })} placeholder="Owner, CEO, CFO…" />
          </Field>
          <Field label="State" required>
            <Select
              value={data.state}
              onChange={(v) => setData({ ...data, state: v })}
              options={[{ value: '', label: 'Select state…' }, ...US_STATES.map((s) => ({ value: s, label: s }))]}
            />
          </Field>
          <div style={{ gridColumn: '1 / -1' }}>
            <Field label="Email" required>
              <Input type="email" value={data.email} onChange={(v) => setData({ ...data, email: v })} placeholder="you@yourbusiness.com" />
            </Field>
          </div>
          <Field label="Phone">
            <Input value={data.phone} onChange={(v) => setData({ ...data, phone: v })} placeholder="(000) 000-0000" />
          </Field>
        </div>
      </Card>
      <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
        <Btn onClick={onNext} disabled={!valid}>
          Continue →
        </Btn>
      </div>
    </>
  );
}

function StepImportDetails({
  data,
  setData,
  onNext,
  onBack,
}: {
  data: ImportData;
  setData: React.Dispatch<React.SetStateAction<ImportData>>;
  onNext: () => void;
  onBack: () => void;
}) {
  const valid = data.importerOfRecord && data.importerOfRecord !== '' && data.estimatedTariff && data.goodsDescription;
  return (
    <>
      <div style={{ marginBottom: '1.8rem' }}>
        <p
          style={{
            fontFamily: "'DM Sans', sans-serif",
            fontSize: '0.68rem',
            fontWeight: 700,
            letterSpacing: '0.22em',
            textTransform: 'uppercase',
            color: COLORS.gold,
            marginBottom: '0.5rem',
          }}
        >
          Step 2 of 4
        </p>
        <h2 style={{ fontFamily: "'DM Serif Display', serif", fontSize: '1.7rem', color: COLORS.white, margin: 0, lineHeight: 1.2 }}>
          Import Details
        </h2>
        <p style={{ fontFamily: "'DM Sans', sans-serif", fontSize: '0.9rem', color: COLORS.muted, marginTop: '0.5rem' }}>
          This determines your eligibility.
        </p>
      </div>
      <Card accent>
        <Field
          label="Were you listed as the Importer of Record on your CBP entries?"
          required
          hint="The 'Importer of Record' is the business named on CBP Form 7501. If a customs broker filed for you, they should be able to confirm this."
        >
          <Select
            value={data.importerOfRecord}
            onChange={(v) => setData({ ...data, importerOfRecord: v })}
            options={[
              { value: '', label: 'Select…' },
              { value: 'yes', label: 'Yes — my business is the Importer of Record' },
              { value: 'no', label: 'No — another entity is listed' },
              { value: 'unsure', label: 'Not sure — I need to verify' },
            ]}
          />
        </Field>
        <Field
          label="What goods did you import?"
          required
          hint="General description is fine — e.g., electronics, auto parts, clothing, medical supplies"
        >
          <Input
            value={data.goodsDescription}
            onChange={(v) => setData({ ...data, goodsDescription: v })}
            placeholder="e.g., electronic components, steel parts, consumer goods"
          />
        </Field>
        <Field
          label="Approximate total IEEPA tariffs paid in 2025 (USD)"
          required
          hint="Estimate is fine. Check your CBP Form 7501 entries or ask your customs broker."
        >
          <Select
            value={data.estimatedTariff}
            onChange={(v) => setData({ ...data, estimatedTariff: v })}
            options={[
              { value: '', label: 'Select range…' },
              { value: 'under5k', label: 'Under $5,000' },
              { value: '5k-25k', label: '$5,000 – $25,000' },
              { value: '25k-100k', label: '$25,000 – $100,000' },
              { value: '100k-500k', label: '$100,000 – $500,000' },
              { value: 'over500k', label: 'Over $500,000' },
            ]}
          />
        </Field>
        <Field label="Approximate number of import entries" hint="Each shipment typically has one entry number.">
          <Select
            value={data.entryCount}
            onChange={(v) => setData({ ...data, entryCount: v })}
            options={[
              { value: '', label: 'Select…' },
              { value: '1-5', label: '1 – 5 entries' },
              { value: '6-25', label: '6 – 25 entries' },
              { value: '26-100', label: '26 – 100 entries' },
              { value: 'over100', label: '100+ entries' },
            ]}
          />
        </Field>
        <Field label="Do you have a CBP ACE Portal account?" hint="This is required to file a CAPE Declaration. If not, we help you set one up.">
          <Select
            value={data.acePortal}
            onChange={(v) => setData({ ...data, acePortal: v })}
            options={[
              { value: '', label: 'Select…' },
              { value: 'yes', label: 'Yes, I have an active ACE account' },
              { value: 'no', label: "No, I don't have one" },
              { value: 'unsure', label: 'Not sure' },
            ]}
          />
        </Field>
        <Field label="Do you have a customs broker?" hint="If yes, they may already have your entry data organized.">
          <Select
            value={data.hasBroker}
            onChange={(v) => setData({ ...data, hasBroker: v })}
            options={[
              { value: '', label: 'Select…' },
              { value: 'yes', label: 'Yes' },
              { value: 'no', label: 'No' },
            ]}
          />
        </Field>
      </Card>
      <div style={{ display: 'flex', justifyContent: 'space-between' }}>
        <Btn onClick={onBack} variant="secondary">
          ← Back
        </Btn>
        <Btn onClick={onNext} disabled={!valid}>
          Assess Eligibility →
        </Btn>
      </div>
    </>
  );
}

function StepQualification({
  payload,
  result,
  setResult,
  onNext,
  onBack,
  onSubmissionId,
}: {
  payload: Record<string, unknown>;
  result: QualificationResult | null;
  setResult: (r: QualificationResult | null) => void;
  onNext: () => void;
  onBack: () => void;
  onSubmissionId: (id: string) => void;
}) {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    let cancelled = false;
    async function run() {
      setLoading(true);
      setError('');
      try {
        const res = await fetch(`${API_BASE}/fleetflow/cape-intake`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        });
        const json = await res.json();
        if (cancelled) return;
        if (!res.ok || !json.success) {
          setError(json.error || `Request failed (${res.status})`);
          setLoading(false);
          return;
        }
        onSubmissionId(json.submission_id || '');
        const q = json.qualification || {};
        setResult({
          eligible: q.eligible,
          confidence: q.confidence || 'medium',
          headline: q.headline || 'Assessment complete',
          summary: q.summary || '',
          estimatedRefund: q.estimatedRefund || 'TBD',
          feeRate: typeof q.feeRate === 'number' ? q.feeRate : 15,
          ddiFee: q.ddiFee || 'TBD',
          flags: Array.isArray(q.flags) ? q.flags : [],
          nextSteps: Array.isArray(q.nextSteps) ? q.nextSteps : [],
          urgency: q.urgency || 'medium',
          urgencyNote: q.urgencyNote || '',
        });
      } catch {
        if (!cancelled) setError('Assessment failed. Check API connection and try again.');
      }
      if (!cancelled) setLoading(false);
    }
    run();
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps -- one POST per mount; parent uses key={assessmentKey} to re-run.
  }, []);

  const eligColor =
    result?.eligible === true ? COLORS.success : result?.eligible === 'conditional' ? COLORS.gold : COLORS.error;
  const eligLabel =
    result?.eligible === true
      ? 'LIKELY ELIGIBLE'
      : result?.eligible === 'conditional'
        ? 'CONDITIONALLY ELIGIBLE'
        : 'ELIGIBILITY UNCLEAR';

  return (
    <>
      <div style={{ marginBottom: '1.8rem' }}>
        <p
          style={{
            fontFamily: "'DM Sans', sans-serif",
            fontSize: '0.68rem',
            fontWeight: 700,
            letterSpacing: '0.22em',
            textTransform: 'uppercase',
            color: COLORS.gold,
            marginBottom: '0.5rem',
          }}
        >
          Step 3 of 4
        </p>
        <h2 style={{ fontFamily: "'DM Serif Display', serif", fontSize: '1.7rem', color: COLORS.white, margin: 0, lineHeight: 1.2 }}>
          Your Assessment
        </h2>
      </div>

      {loading && (
        <Card accent>
          <div style={{ textAlign: 'center', padding: '2rem 0' }}>
            <div
              style={{
                width: 40,
                height: 40,
                border: `3px solid ${COLORS.border}`,
                borderTop: `3px solid ${COLORS.gold}`,
                borderRadius: '50%',
                animation: 'spin 0.9s linear infinite',
                margin: '0 auto 1rem',
              }}
            />
            <p style={{ fontFamily: "'DM Sans', sans-serif", color: COLORS.muted, fontSize: '0.9rem' }}>
              Analyzing your import profile…
            </p>
          </div>
          <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
        </Card>
      )}

      {error && (
        <Card>
          <p style={{ fontFamily: "'DM Sans', sans-serif", color: COLORS.error, fontSize: '0.9rem' }}>{error}</p>
          <p style={{ fontFamily: "'DM Sans', sans-serif", color: COLORS.muted, fontSize: '0.8rem', marginTop: '0.5rem' }}>
            Ensure NEXUS API is running and <code style={{ color: COLORS.cream }}>REACT_APP_API_BASE</code> points to it (
            {API_BASE}).
          </p>
        </Card>
      )}

      {result && !loading && !error && (
        <>
          <div style={{ background: COLORS.navyMid, border: `1px solid ${eligColor}`, borderTop: `4px solid ${eligColor}`, padding: '1.5rem 1.8rem', marginBottom: '1rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.8rem', marginBottom: '0.6rem' }}>
              <div style={{ width: 10, height: 10, borderRadius: '50%', background: eligColor, flexShrink: 0 }} />
              <span
                style={{
                  fontFamily: "'DM Sans', sans-serif",
                  fontSize: '0.68rem',
                  fontWeight: 700,
                  letterSpacing: '0.2em',
                  textTransform: 'uppercase',
                  color: eligColor,
                }}
              >
                {eligLabel}
              </span>
              <span style={{ fontFamily: "'DM Sans', sans-serif", fontSize: '0.68rem', color: COLORS.muted, marginLeft: 'auto' }}>
                Confidence: {result.confidence}
              </span>
            </div>
            <h3 style={{ fontFamily: "'DM Serif Display', serif", fontSize: '1.35rem', color: COLORS.white, margin: '0 0 0.6rem' }}>
              {result.headline}
            </h3>
            <p style={{ fontFamily: "'DM Sans', sans-serif", fontSize: '0.88rem', color: COLORS.muted, lineHeight: 1.65, margin: 0 }}>
              {result.summary}
            </p>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1rem' }}>
            {[
              { label: 'Estimated Refund', value: result.estimatedRefund, note: 'Gross amount from CBP' },
              { label: 'DDI Fee', value: result.ddiFee, note: `${result.feeRate}% contingency` },
            ].map(({ label, value, note }) => (
              <div key={label} style={{ background: COLORS.navyLight, border: `1px solid ${COLORS.border}`, padding: '1.2rem 1.4rem' }}>
                <p
                  style={{
                    fontFamily: "'DM Sans', sans-serif",
                    fontSize: '0.65rem',
                    fontWeight: 700,
                    letterSpacing: '0.18em',
                    textTransform: 'uppercase',
                    color: COLORS.gold,
                    margin: '0 0 0.3rem',
                  }}
                >
                  {label}
                </p>
                <p style={{ fontFamily: "'DM Serif Display', serif", fontSize: '1.4rem', color: COLORS.white, margin: '0 0 0.2rem' }}>
                  {value}
                </p>
                <p style={{ fontFamily: "'DM Sans', sans-serif", fontSize: '0.72rem', color: COLORS.muted, margin: 0 }}>{note}</p>
              </div>
            ))}
          </div>

          {result.urgency === 'high' && (
            <div
              style={{
                background: 'rgba(192,57,43,0.1)',
                border: '1px solid rgba(192,57,43,0.4)',
                borderLeft: '3px solid #C0392B',
                padding: '0.8rem 1.2rem',
                marginBottom: '1rem',
              }}
            >
              <p style={{ fontFamily: "'DM Sans', sans-serif", fontSize: '0.82rem', color: '#E88080', margin: 0, lineHeight: 1.5 }}>
                <strong>Time Sensitive:</strong> {result.urgencyNote}
              </p>
            </div>
          )}

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1.5rem' }}>
            <div style={{ background: COLORS.navyMid, border: `1px solid ${COLORS.border}`, padding: '1.2rem 1.4rem' }}>
              <p
                style={{
                  fontFamily: "'DM Sans', sans-serif",
                  fontSize: '0.65rem',
                  fontWeight: 700,
                  letterSpacing: '0.18em',
                  textTransform: 'uppercase',
                  color: COLORS.gold,
                  margin: '0 0 0.8rem',
                }}
              >
                Flags / Risks
              </p>
              {result.flags?.map((f, i) => (
                <p key={i} style={{ fontFamily: "'DM Sans', sans-serif", fontSize: '0.82rem', color: COLORS.muted, margin: '0 0 0.5rem', lineHeight: 1.5 }}>
                  ◆ {f}
                </p>
              ))}
            </div>
            <div style={{ background: COLORS.navyMid, border: `1px solid ${COLORS.border}`, padding: '1.2rem 1.4rem' }}>
              <p
                style={{
                  fontFamily: "'DM Sans', sans-serif",
                  fontSize: '0.65rem',
                  fontWeight: 700,
                  letterSpacing: '0.18em',
                  textTransform: 'uppercase',
                  color: COLORS.gold,
                  margin: '0 0 0.8rem',
                }}
              >
                Next Steps
              </p>
              {result.nextSteps?.map((s, i) => (
                <p key={i} style={{ fontFamily: "'DM Sans', sans-serif", fontSize: '0.82rem', color: COLORS.cream, margin: '0 0 0.5rem', lineHeight: 1.5 }}>
                  {i + 1}. {s}
                </p>
              ))}
            </div>
          </div>

          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <Btn onClick={onBack} variant="secondary">
              ← Back
            </Btn>
            <Btn onClick={onNext}>Generate Agreement →</Btn>
          </div>
        </>
      )}
    </>
  );
}

function StepAgreement({
  data,
  result,
  submissionId,
  onBack,
}: {
  data: BizData;
  result: QualificationResult | null;
  submissionId: string | null;
  onBack: () => void;
}) {
  const [agreed, setAgreed] = useState(false);
  const [generated, setGenerated] = useState(false);
  const today = new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });
  const agreementNo =
    submissionId || `DDI-TRN-${new Date().getFullYear()}-${Math.floor(1000 + Math.random() * 9000)}`;

  function buildAgreementText() {
    const fee = result?.feeRate || 15;
    return `
DEE DAVIS INC — IEEPA TARIFF REFUND NAVIGATOR
CONSULTING SERVICES ENGAGEMENT AGREEMENT
Agreement No.: ${agreementNo}
Effective Date: ${today}
${'═'.repeat(60)}

PARTIES
${'─'.repeat(60)}
SERVICE PROVIDER:
  Dee Davis Inc (DDI) — FleetFlow™ Division
  755 W. Big Beaver Rd., Ste. 2020, Troy, MI 48084
  EIN: 84-4114181 | CAGE: 8UMX3 | EDWOSB · WOSB · MBE · WBENC

CLIENT:
  Business Legal Name: ${data.bizName}
  DBA: ${data.dba || 'N/A'}
  EIN: ${data.ein}
  State: ${data.state}
  Authorized Representative: ${data.contact}
  Title: ${data.title || 'N/A'}
  Email: ${data.email}
  Phone: ${data.phone || 'N/A'}

${'═'.repeat(60)}
SECTION 1 — SCOPE OF SERVICES
${'─'.repeat(60)}
DDI agrees to provide the following consulting and document preparation
assistance in connection with Client's potential eligibility for refunds
of tariffs paid under the International Emergency Economic Powers Act
(IEEPA), as affected by the U.S. Supreme Court ruling of February 20, 2026:

  1. Eligibility Assessment — Review import history and importer-of-record
     status to determine IEEPA tariff refund exposure.
  2. ACE Portal Guidance — Step-by-step setup and ACH enrollment support.
  3. Entry Data Organization — Compile and format entry numbers into the
     CSV structure required for CAPE Declaration submission.
  4. CAPE Filing Support — Guide Client through CBP CAPE portal submission.
     CLIENT REMAINS THE FILER OF RECORD AT ALL TIMES.
  5. Status Monitoring — Advise on tracking refund status via ACE Portal.
  6. Referral Services — Identify matters requiring licensed customs broker
     or legal counsel.

IMPORTANT: DDI is not a licensed customs broker and does not provide
customs brokerage, legal, or tax advisory services. All services are
consulting and operational assistance only.

${'═'.repeat(60)}
SECTION 2 — FEES & PAYMENT
${'─'.repeat(60)}
2.1 CONTINGENCY FEE
  DDI shall receive ${fee}% of the gross refund amount received by Client
  from CBP under any CAPE Declaration facilitated by DDI.
  Estimated refund: ${result?.estimatedRefund || 'TBD'}
  Estimated DDI fee: ${result?.ddiFee || 'TBD'}

2.2 ENGAGEMENT RETAINER
  Non-refundable retainer: $ __________ (credited against contingency fee)
  Due upon execution of this Agreement.

2.3 ASSIGNMENT OF PROCEEDS
  Client irrevocably assigns to DDI a security interest in and lien upon
  DDI's percentage of any IEEPA refund proceeds. DDI's fee constitutes
  a debt owed at the moment of Client's receipt of any refund. Client
  agrees to pay DDI's invoice within FIVE (5) BUSINESS DAYS of receiving
  any CBP refund payment. Late payments accrue interest at 1.5%/month.

2.4 ESCROW (Refunds Exceeding $25,000)
  For anticipated refunds over $25,000, Client agrees to direct deposits
  into a mutually agreed account from which DDI's fee shall be disbursed
  prior to release of the remaining balance to Client.

2.5 PERSONAL GUARANTEE
  If Client is a corporation, LLC, or other entity, the Authorized
  Representative personally and unconditionally guarantees all fees owed.

${'═'.repeat(60)}
SECTION 3 — CLIENT OBLIGATIONS
${'─'.repeat(60)}
Client agrees to:
  • Provide accurate import entry documentation (CBP Form 7501, invoices)
  • Create and maintain an active CBP ACE Portal account
  • Complete ACH enrollment with CBP before refund is issued
  • Notify DDI within TWO (2) business days of receiving any CBP refund
  • Remain solely responsible as importer of record for all CBP filings
  • Not engage another party to file duplicative CAPE Declarations for
    entries covered by this Agreement during the term

${'═'.repeat(60)}
SECTION 4 — REPRESENTATIONS & WARRANTIES
${'─'.repeat(60)}
Client represents that: (a) Client is the importer of record on entries
for which refunds are sought; (b) Client has authority to execute this
Agreement; (c) all information provided is accurate; and (d) Client has
not previously filed or assigned rights to file CAPE Declarations for
the same entries covered herein.

${'═'.repeat(60)}
SECTION 5 — DISCLAIMER & LIMITATION OF LIABILITY
${'─'.repeat(60)}
DDI does not guarantee any refund or specific refund amount. Eligibility
and amounts are determined solely by CBP and applicable law. DDI's
liability shall not exceed retainer fees paid. Tariff refund policies are
subject to ongoing government guidance and may change without notice.

${'═'.repeat(60)}
SECTION 6 — TERM & TERMINATION
${'─'.repeat(60)}
Agreement commences on Effective Date and continues until full
disbursement and payment of all fees, or by mutual written agreement.
Either party may terminate with 14 days written notice. Client remains
obligated to pay DDI's contingency fee on any refund received within
12 months of termination for entries assisted during the engagement.

${'═'.repeat(60)}
SECTION 7 — GENERAL PROVISIONS
${'─'.repeat(60)}
Governing Law: State of Michigan. Disputes resolved in Oakland County, MI.
This Agreement is the entire agreement between the parties. Amendments
must be in writing and signed by both parties.

${'═'.repeat(60)}
SIGNATURES
${'─'.repeat(60)}

FOR DEE DAVIS INC:
  Signature: _______________________________  Date: ________________
  Name: Dee Davis
  Title: President & CEO

FOR CLIENT:
  Signature: _______________________________  Date: ________________
  Name: ${data.contact}
  Title: ${data.title || '_______________'}
  Business: ${data.bizName}

PERSONAL GUARANTEE:
  Signature: _______________________________  Date: ________________
  Guarantor Name: _______________________________

${'═'.repeat(60)}
DDI is a federally certified EDWOSB, WOSB, MBE, and WBENC firm.
EIN: 84-4114181 · UEI: HJB4KNYJVGZ1 · CAGE: 8UMX3
755 W. Big Beaver Rd., Ste. 2020, Troy, MI 48084
This document is for consulting services only and does not constitute
legal advice. Complex customs matters should involve a licensed broker
or trade attorney.
${'═'.repeat(60)}
`;
  }

  function generateAndDownload() {
    const text = buildAgreementText();
    const blob = new Blob([text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `DDI_Engagement_Agreement_${data.bizName.replace(/\s+/g, '_')}.txt`;
    a.click();
    URL.revokeObjectURL(url);
    setGenerated(true);
  }

  return (
    <>
      <div style={{ marginBottom: '1.8rem' }}>
        <p
          style={{
            fontFamily: "'DM Sans', sans-serif",
            fontSize: '0.68rem',
            fontWeight: 700,
            letterSpacing: '0.22em',
            textTransform: 'uppercase',
            color: COLORS.gold,
            marginBottom: '0.5rem',
          }}
        >
          Step 4 of 4
        </p>
        <h2 style={{ fontFamily: "'DM Serif Display', serif", fontSize: '1.7rem', color: COLORS.white, margin: 0, lineHeight: 1.2 }}>
          Your Agreement
        </h2>
        <p style={{ fontFamily: "'DM Sans', sans-serif", fontSize: '0.9rem', color: COLORS.muted, marginTop: '0.5rem' }}>
          Pre-filled and ready to download.
        </p>
      </div>

      <Card accent>
        <p
          style={{
            fontFamily: "'DM Sans', sans-serif",
            fontSize: '0.65rem',
            fontWeight: 700,
            letterSpacing: '0.18em',
            textTransform: 'uppercase',
            color: COLORS.gold,
            margin: '0 0 1rem',
          }}
        >
          Agreement Summary
        </p>
        {[
          ['Agreement No.', agreementNo],
          ['Date', today],
          ['Client', data.bizName],
          ['Representative', `${data.contact}${data.title ? ` — ${data.title}` : ''}`],
          ['Contingency Fee', `${result?.feeRate || 15}%`],
          ['Estimated Refund', result?.estimatedRefund || 'TBD'],
          ['Estimated DDI Fee', result?.ddiFee || 'TBD'],
        ].map(([label, val]) => (
          <div
            key={label}
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'baseline',
              borderBottom: `1px solid ${COLORS.border}`,
              padding: '0.5rem 0',
            }}
          >
            <span style={{ fontFamily: "'DM Sans', sans-serif", fontSize: '0.8rem', color: COLORS.muted }}>{label}</span>
            <span style={{ fontFamily: "'DM Sans', sans-serif", fontSize: '0.88rem', color: COLORS.cream, fontWeight: 600 }}>{val}</span>
          </div>
        ))}
      </Card>

      <div
        style={{
          background: 'rgba(201,168,76,0.07)',
          border: `1px solid ${COLORS.border}`,
          borderLeft: `3px solid ${COLORS.gold}`,
          padding: '1rem 1.4rem',
          marginBottom: '1.5rem',
        }}
      >
        <label style={{ display: 'flex', alignItems: 'flex-start', gap: '0.7rem', cursor: 'pointer' }}>
          <input
            type="checkbox"
            checked={agreed}
            onChange={(e) => setAgreed(e.target.checked)}
            style={{ marginTop: 3, accentColor: COLORS.gold, width: 16, height: 16, flexShrink: 0 }}
          />
          <span style={{ fontFamily: "'DM Sans', sans-serif", fontSize: '0.82rem', color: COLORS.muted, lineHeight: 1.6 }}>
            I confirm that the information I have provided is accurate and that I am authorized to enter into this agreement on behalf of{' '}
            <strong style={{ color: COLORS.cream }}>{data.bizName}</strong>. I understand DDI is providing consulting services only, not customs brokerage or legal advice.
          </span>
        </label>
      </div>

      {generated && (
        <div
          style={{
            background: 'rgba(45,155,111,0.12)',
            border: '1px solid rgba(45,155,111,0.4)',
            borderLeft: '3px solid #2D9B6F',
            padding: '1rem 1.4rem',
            marginBottom: '1.2rem',
          }}
        >
          <p style={{ fontFamily: "'DM Sans', sans-serif", fontSize: '0.88rem', color: '#6ECFA8', margin: 0, lineHeight: 1.6 }}>
            Agreement downloaded. Next: sign and return to <strong>bids.deedavisinc@gmail.com</strong> along with your retainer payment to begin your engagement.
          </p>
        </div>
      )}

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Btn onClick={onBack} variant="secondary">
          ← Back
        </Btn>
        <Btn onClick={generateAndDownload} disabled={!agreed}>
          {generated ? 'Download Again ↓' : 'Download Agreement ↓'}
        </Btn>
      </div>
    </>
  );
}

export interface TariffRefundNavigatorProps {
  onBackToNexus?: () => void;
}

export default function TariffRefundNavigator({ onBackToNexus }: TariffRefundNavigatorProps) {
  const [step, setStep] = useState(0);
  const [assessmentKey, setAssessmentKey] = useState(0);
  const [bizData, setBizData] = useState<BizData>({
    bizName: '',
    dba: '',
    ein: '',
    contact: '',
    title: '',
    email: '',
    phone: '',
    state: '',
  });
  const [importData, setImportData] = useState<ImportData>({
    importerOfRecord: '',
    goodsDescription: '',
    estimatedTariff: '',
    entryCount: '',
    acePortal: '',
    hasBroker: '',
  });
  const [result, setResult] = useState<QualificationResult | null>(null);
  const [submissionId, setSubmissionId] = useState<string | null>(null);

  const intakePayload = useMemo(() => buildCapePayload(bizData, importData), [bizData, importData]);

  const handleSubmissionId = useCallback((id: string) => {
    setSubmissionId(id);
  }, []);

  return (
    <div style={styles.wrap}>
      <link href="https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@300;400;500;600;700&display=swap" rel="stylesheet" />
      <div style={styles.noise} />
      <div style={styles.glow} />
      <div style={styles.inner}>
        {onBackToNexus && (
          <button
            type="button"
            onClick={onBackToNexus}
            style={{
              background: 'transparent',
              border: `1px solid ${COLORS.border}`,
              color: COLORS.muted,
              fontFamily: "'DM Sans', sans-serif",
              fontSize: '0.75rem',
              padding: '0.5rem 1rem',
              marginBottom: '1rem',
              cursor: 'pointer',
              borderRadius: 4,
            }}
          >
            ← Back to NEXUS
          </button>
        )}

        <div style={{ textAlign: 'center', marginBottom: '2.5rem' }}>
          <p
            style={{
              fontFamily: "'DM Sans', sans-serif",
              fontSize: '0.62rem',
              fontWeight: 700,
              letterSpacing: '0.3em',
              textTransform: 'uppercase',
              color: COLORS.gold,
              marginBottom: '0.4rem',
            }}
          >
            Dee Davis Inc · FleetFlow™
          </p>
          <h1
            style={{
              fontFamily: "'DM Serif Display', serif",
              fontSize: 'clamp(1.6rem, 4vw, 2.2rem)',
              color: COLORS.white,
              margin: '0 0 0.4rem',
              lineHeight: 1.15,
            }}
          >
            Tariff Refund Navigator
          </h1>
          <p style={{ fontFamily: "'DM Sans', sans-serif", fontSize: '0.85rem', color: COLORS.muted, margin: 0 }}>
            IEEPA Recovery Service · No refund, no fee.
          </p>
        </div>

        <details
          style={{
            margin: '0 auto 1.75rem',
            maxWidth: 640,
            background: COLORS.navyMid,
            border: `1px solid ${COLORS.border}`,
            borderLeft: `3px solid ${COLORS.gold}`,
            padding: '0.85rem 1.1rem',
            textAlign: 'left',
          }}
        >
          <summary
            style={{
              fontFamily: "'DM Sans', sans-serif",
              fontSize: '0.72rem',
              fontWeight: 700,
              letterSpacing: '0.14em',
              textTransform: 'uppercase',
              color: COLORS.gold,
              cursor: 'pointer',
              listStyle: 'none',
            }}
          >
            About CAPE &amp; IEEPA duty refunds
          </summary>
          <div
            style={{
              fontFamily: "'DM Sans', sans-serif",
              fontSize: '0.8rem',
              color: COLORS.muted,
              lineHeight: 1.65,
              marginTop: '0.85rem',
              borderTop: `1px solid ${COLORS.border}`,
              paddingTop: '0.85rem',
            }}
          >
            <p style={{ margin: '0 0 0.75rem' }}>
              U.S. Customs and Border Protection (CBP) is rolling out the Consolidated Administration and Processing of Entries (CAPE)
              program to process refunds of certain duties collected under the International Emergency Economic Powers Act (IEEPA). This
              navigator is only about that IEEPA-related path — not Section 232, 301, or 122 tariffs unless CBP guidance expressly
              includes them in your situation.
            </p>
            <p style={{ margin: '0 0 0.75rem' }}>
              Some state agencies forward CBP&apos;s general IEEPA refund notices to in-state business subscription lists. That is
              informational only — who qualifies, how to file, and how refunds are decided are governed by <strong style={{ color: COLORS.cream }}>federal</strong> CBP and ACE rules; the state is not the program administrator.
            </p>
            <p style={{ margin: '0 0 0.75rem' }}>
              CAPE is being introduced in phases. Early phases focus on specific entry situations (for example, some unliquidated entries
              and entries within defined liquidation-related windows). Later phases may cover additional scenarios as CBP publishes them.
            </p>
            <p style={{ margin: '0 0 0.75rem' }}>
              Typically, the importer of record (or the party that files on their behalf) submits refund requests through the ACE Secure Data
              Portal using the spreadsheet-style entry listing CBP requires. Large batches of entries can be included in a single submission,
              and multiple submissions may be allowed.
            </p>
            <p style={{ margin: '0 0 0.75rem' }}>
              After CBP accepts a filing, it reviews entries before issuing payment. Timing depends on CBP workload and whether more
              information is needed — think weeks to a few months in many cases, not a fixed guarantee.
            </p>
            <p style={{ margin: 0, fontSize: '0.76rem', color: COLORS.muted }}>
              Eligibility, scope, and amounts are determined only by CBP and applicable law. Check official CBP and ACE resources for the
              latest filing rules before you rely on any summary.
            </p>
          </div>
        </details>

        <StepDots current={step} total={4} />

        {step === 0 && <StepBusinessInfo data={bizData} setData={setBizData} onNext={() => setStep(1)} />}
        {step === 1 && (
          <StepImportDetails
            data={importData}
            setData={setImportData}
            onNext={() => {
              setResult(null);
              setSubmissionId(null);
              setAssessmentKey((k) => k + 1);
              setStep(2);
            }}
            onBack={() => setStep(0)}
          />
        )}
        {step === 2 && (
          <StepQualification
            key={assessmentKey}
            payload={intakePayload}
            result={result}
            setResult={setResult}
            onNext={() => setStep(3)}
            onBack={() => setStep(1)}
            onSubmissionId={handleSubmissionId}
          />
        )}
        {step === 3 && (
          <StepAgreement data={bizData} result={result} submissionId={submissionId} onBack={() => setStep(2)} />
        )}

        <div style={{ textAlign: 'center', marginTop: '3rem', borderTop: `1px solid ${COLORS.border}`, paddingTop: '1.5rem' }}>
          <p style={{ fontFamily: "'DM Sans', sans-serif", fontSize: '0.7rem', color: COLORS.muted, lineHeight: 1.6, margin: 0 }}>
            DDI is a federally certified EDWOSB, WOSB, MBE &amp; WBENC firm · Troy, MI · EIN: 84-4114181
            <br />
            Consulting services only — not customs brokerage or legal advice.
          </p>
        </div>
      </div>
    </div>
  );
}
