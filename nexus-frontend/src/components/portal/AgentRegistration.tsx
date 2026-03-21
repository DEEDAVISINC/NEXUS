import React, { useState } from 'react';

// DDI Brand Colors
// Deep Blue: #1B2A4A (primary dark — backgrounds, headers)
// Teal: #2DD4BF (accent — highlights, active states, links)
// Pink: #EC4899 (secondary accent — CTAs, energy, buttons)
// Gold: #F59E0B (premium — certifications, warmth, badges)

interface AgentRegistrationProps {
  onRegister: (data: any) => void;
  onSwitchToLogin: () => void;
  loading?: boolean;
}

const STEPS = [
  { num: 1, label: 'Personal Info' },
  { num: 2, label: 'Specialties & Area' },
  { num: 3, label: 'Certifications' },
  { num: 4, label: 'Account Setup' },
];

const SPECIALTIES = [
  { id: 'signing', label: 'Notary Signing Agent', icon: '🟠', desc: 'Loan signings, general notarizations, closings' },
  { id: 'ron', label: 'Remote Online Notary (RON)', icon: '🟣', desc: 'Remote notarization via video platform' },
  { id: 'collector-dot', label: 'Drug Test Collector (DOT)', icon: '🔴', desc: 'DOT-regulated urine, hair, oral fluid collections' },
  { id: 'collector-nondot', label: 'Drug Test Collector (Non-DOT)', icon: '🔴', desc: 'Employer-mandated drug testing' },
  { id: 'dna', label: 'DNA Collection Specialist', icon: '🟣', desc: 'Legal and private DNA sample collection' },
  { id: 'fingerprint', label: 'Fingerprint / EFT Technician', icon: '🟢', desc: 'LiveScan, ink cards, electronic fingerprint (EFT) — FBI, ATF, state' },
  { id: 'courier', label: 'Courier / Runner', icon: '🔵', desc: 'Document pickup, delivery, court filings' },
  { id: 'background', label: 'Background Check Specialist', icon: '⚫', desc: 'FCRA-compliant background investigations' },
  { id: 'process', label: 'Process Server', icon: '🟢', desc: 'Legal document service of process' },
];

// Shared input style
const inputStyle: React.CSSProperties = {
  background: 'rgba(15, 26, 46, 0.8)',
  border: '1px solid rgba(45, 212, 191, 0.2)',
};

const inputFocus = (e: React.FocusEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
  e.target.style.borderColor = '#2DD4BF';
  e.target.style.boxShadow = '0 0 0 2px rgba(45, 212, 191, 0.2)';
};
const inputBlur = (e: React.FocusEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
  e.target.style.borderColor = 'rgba(45, 212, 191, 0.2)';
  e.target.style.boxShadow = 'none';
};

const AgentRegistration: React.FC<AgentRegistrationProps> = ({ onRegister, onSwitchToLogin, loading }) => {
  const [step, setStep] = useState(1);

  // Step 1 — Personal Info
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [address, setAddress] = useState('');
  const [city, setCity] = useState('');
  const [state, setState] = useState('');
  const [zip, setZip] = useState('');

  // Step 2 — Specialties & Area
  const [selectedSpecialties, setSelectedSpecialties] = useState<string[]>([]);
  const [serviceRadius, setServiceRadius] = useState('25');
  const [serviceZips, setServiceZips] = useState('');
  const [yearsExperience, setYearsExperience] = useState('');
  const [hasVehicle, setHasVehicle] = useState(false);

  // Step 3 — Certifications
  const [notaryState, setNotaryState] = useState('');
  const [notaryNumber, setNotaryNumber] = useState('');
  const [notaryExpiration, setNotaryExpiration] = useState('');
  const [hasNNA, setHasNNA] = useState(false);
  const [hasEO, setHasEO] = useState(false);
  const [hasDOTCert, setHasDOTCert] = useState(false);
  const [hasLiveScan, setHasLiveScan] = useState(false);
  const [hasFCRA, setHasFCRA] = useState(false);
  const [otherCerts, setOtherCerts] = useState('');
  const [agreeBackgroundCheck, setAgreeBackgroundCheck] = useState(false);

  // Step 4 — Account
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [agreeTerms, setAgreeTerms] = useState(false);
  const [agreeNDA, setAgreeNDA] = useState(false);

  const toggleSpecialty = (id: string) => {
    setSelectedSpecialties(prev => prev.includes(id) ? prev.filter(s => s !== id) : [...prev, id]);
  };

  const canProceed = () => {
    switch (step) {
      case 1: return firstName && lastName && email && phone && city && state && zip;
      case 2: return selectedSpecialties.length > 0 && serviceRadius;
      case 3: return agreeBackgroundCheck;
      case 4: return password && password === confirmPassword && agreeTerms && agreeNDA;
      default: return false;
    }
  };

  const handleSubmit = () => {
    onRegister({
      firstName, lastName, email, phone, address, city, state, zip,
      specialties: selectedSpecialties, serviceRadius, serviceZips, yearsExperience, hasVehicle,
      notaryState, notaryNumber, notaryExpiration, hasNNA, hasEO, hasDOTCert, hasLiveScan, hasFCRA, otherCerts,
      agreeBackgroundCheck, agreeTerms, agreeNDA,
    });
  };

  return (
    <div className="min-h-screen flex flex-col" style={{ background: 'linear-gradient(135deg, #0F1A2E 0%, #1B2A4A 50%, #0F1A2E 100%)' }}>
      {/* ─── TOP BAR ─────────────────────────────────── */}
      <div className="w-full border-b px-6 py-4" style={{ background: 'rgba(15, 26, 46, 0.9)', borderColor: 'rgba(45, 212, 191, 0.1)' }}>
        <div className="max-w-2xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl flex items-center justify-center text-white font-black text-sm shadow-lg" style={{ background: 'linear-gradient(135deg, #EC4899, #DB2777)', boxShadow: '0 4px 15px rgba(236, 72, 153, 0.3)' }}>DDI</div>
            <div>
              <p className="font-bold text-white text-sm">Dee Davis Inc.</p>
              <p className="text-[10px] uppercase tracking-wider" style={{ color: '#2DD4BF' }}>Field Agent Application</p>
            </div>
          </div>
          <button onClick={onSwitchToLogin} className="text-sm transition hover:text-white" style={{ color: '#94A3B8' }}>
            Already an agent? <span className="font-semibold" style={{ color: '#2DD4BF' }}>Sign In</span>
          </button>
        </div>
      </div>

      {/* ─── CONTENT ─────────────────────────────────── */}
      <div className="flex-1 flex items-start justify-center px-4 py-8">
        <div className="w-full max-w-2xl">

          {/* Header */}
          <div className="text-center mb-6">
            <h1 className="text-2xl font-black text-white mb-1">Join Our Field Agent Network</h1>
            <p className="text-sm" style={{ color: '#94A3B8' }}>EDWOSB-certified company serving Metro Detroit & beyond</p>
          </div>

          {/* Progress Steps */}
          <div className="flex items-center justify-center gap-2 mb-8">
            {STEPS.map((s, i) => (
              <React.Fragment key={s.num}>
                <div className="flex items-center gap-2">
                  <div className="w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold transition"
                    style={{
                      background: step > s.num ? '#2DD4BF' : step === s.num ? '#EC4899' : 'rgba(27, 42, 74, 0.8)',
                      color: step >= s.num ? 'white' : '#64748B',
                      boxShadow: step === s.num ? '0 0 12px rgba(236, 72, 153, 0.4)' : 'none',
                    }}>
                    {step > s.num ? '✓' : s.num}
                  </div>
                  <span className={`text-xs font-semibold hidden sm:block`} style={{ color: step === s.num ? 'white' : '#64748B' }}>{s.label}</span>
                </div>
                {i < STEPS.length - 1 && <div className="w-8 h-0.5" style={{ background: step > s.num ? '#2DD4BF' : 'rgba(27, 42, 74, 0.8)' }}></div>}
              </React.Fragment>
            ))}
          </div>

          {/* Form Card */}
          <div className="backdrop-blur rounded-2xl p-8 shadow-2xl" style={{ background: 'rgba(27, 42, 74, 0.7)', border: '1px solid rgba(45, 212, 191, 0.15)' }}>

            {/* ── STEP 1: Personal Info ── */}
            {step === 1 && (
              <div>
                <h2 className="text-xl font-bold mb-1">Personal Information</h2>
                <p className="text-sm mb-6" style={{ color: '#94A3B8' }}>Tell us about yourself</p>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-semibold mb-1" style={{ color: '#94A3B8' }}>First Name *</label>
                    <input type="text" value={firstName} onChange={e => setFirstName(e.target.value)}
                      className="w-full rounded-xl px-4 py-3 text-sm text-white focus:outline-none transition" style={inputStyle} onFocus={inputFocus} onBlur={inputBlur} placeholder="First name" required />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold mb-1" style={{ color: '#94A3B8' }}>Last Name *</label>
                    <input type="text" value={lastName} onChange={e => setLastName(e.target.value)}
                      className="w-full rounded-xl px-4 py-3 text-sm text-white focus:outline-none transition" style={inputStyle} onFocus={inputFocus} onBlur={inputBlur} placeholder="Last name" required />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold mb-1" style={{ color: '#94A3B8' }}>Email *</label>
                    <input type="email" value={email} onChange={e => setEmail(e.target.value)}
                      className="w-full rounded-xl px-4 py-3 text-sm text-white focus:outline-none transition" style={inputStyle} onFocus={inputFocus} onBlur={inputBlur} placeholder="you@email.com" required />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold mb-1" style={{ color: '#94A3B8' }}>Phone *</label>
                    <input type="tel" value={phone} onChange={e => setPhone(e.target.value)}
                      className="w-full rounded-xl px-4 py-3 text-sm text-white focus:outline-none transition" style={inputStyle} onFocus={inputFocus} onBlur={inputBlur} placeholder="(248) 555-0000" required />
                  </div>
                  <div className="md:col-span-2">
                    <label className="block text-xs font-semibold mb-1" style={{ color: '#94A3B8' }}>Street Address</label>
                    <input type="text" value={address} onChange={e => setAddress(e.target.value)}
                      className="w-full rounded-xl px-4 py-3 text-sm text-white focus:outline-none transition" style={inputStyle} onFocus={inputFocus} onBlur={inputBlur} placeholder="Street address" />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold mb-1" style={{ color: '#94A3B8' }}>City *</label>
                    <input type="text" value={city} onChange={e => setCity(e.target.value)}
                      className="w-full rounded-xl px-4 py-3 text-sm text-white focus:outline-none transition" style={inputStyle} onFocus={inputFocus} onBlur={inputBlur} placeholder="City" required />
                  </div>
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block text-xs font-semibold mb-1" style={{ color: '#94A3B8' }}>State *</label>
                      <input type="text" value={state} onChange={e => setState(e.target.value)} maxLength={2}
                        className="w-full rounded-xl px-4 py-3 text-sm text-white uppercase focus:outline-none transition" style={inputStyle} onFocus={inputFocus} onBlur={inputBlur} placeholder="MI" required />
                    </div>
                    <div>
                      <label className="block text-xs font-semibold mb-1" style={{ color: '#94A3B8' }}>ZIP *</label>
                      <input type="text" value={zip} onChange={e => setZip(e.target.value)} maxLength={5}
                        className="w-full rounded-xl px-4 py-3 text-sm text-white focus:outline-none transition" style={inputStyle} onFocus={inputFocus} onBlur={inputBlur} placeholder="48084" required />
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* ── STEP 2: Specialties & Area ── */}
            {step === 2 && (
              <div>
                <h2 className="text-xl font-bold mb-1">Specialties & Service Area</h2>
                <p className="text-sm mb-6" style={{ color: '#94A3B8' }}>What services can you perform? Select all that apply.</p>

                <div className="space-y-2 mb-6">
                  {SPECIALTIES.map(s => (
                    <button key={s.id} type="button" onClick={() => toggleSpecialty(s.id)}
                      className="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-left transition"
                      style={{
                        border: selectedSpecialties.includes(s.id) ? '1px solid #2DD4BF' : '1px solid rgba(45, 212, 191, 0.15)',
                        background: selectedSpecialties.includes(s.id) ? 'rgba(45, 212, 191, 0.08)' : 'rgba(15, 26, 46, 0.5)',
                      }}>
                      <span className="text-lg">{s.icon}</span>
                      <div className="flex-1">
                        <p className="font-semibold text-sm">{s.label}</p>
                        <p className="text-xs" style={{ color: '#64748B' }}>{s.desc}</p>
                      </div>
                      <div className="w-5 h-5 rounded flex items-center justify-center"
                        style={{
                          background: selectedSpecialties.includes(s.id) ? '#2DD4BF' : 'transparent',
                          border: selectedSpecialties.includes(s.id) ? '1px solid #2DD4BF' : '1px solid rgba(100, 116, 139, 0.5)',
                        }}>
                        {selectedSpecialties.includes(s.id) && <span className="text-xs text-white">✓</span>}
                      </div>
                    </button>
                  ))}
                </div>

                <div className="pt-6" style={{ borderTop: '1px solid rgba(45, 212, 191, 0.1)' }}>
                  <h3 className="font-semibold text-sm mb-4">Service Area</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-xs font-semibold mb-1" style={{ color: '#94A3B8' }}>Service Radius (miles) *</label>
                      <input type="number" value={serviceRadius} onChange={e => setServiceRadius(e.target.value)}
                        className="w-full rounded-xl px-4 py-3 text-sm text-white focus:outline-none transition" style={inputStyle} onFocus={inputFocus} onBlur={inputBlur} placeholder="25" />
                    </div>
                    <div>
                      <label className="block text-xs font-semibold mb-1" style={{ color: '#94A3B8' }}>Years Experience</label>
                      <input type="number" value={yearsExperience} onChange={e => setYearsExperience(e.target.value)}
                        className="w-full rounded-xl px-4 py-3 text-sm text-white focus:outline-none transition" style={inputStyle} onFocus={inputFocus} onBlur={inputBlur} placeholder="0" />
                    </div>
                    <div className="md:col-span-2">
                      <label className="block text-xs font-semibold mb-1" style={{ color: '#94A3B8' }}>Additional ZIP Codes (optional)</label>
                      <input type="text" value={serviceZips} onChange={e => setServiceZips(e.target.value)}
                        className="w-full rounded-xl px-4 py-3 text-sm text-white focus:outline-none transition" style={inputStyle} onFocus={inputFocus} onBlur={inputBlur} placeholder="48084, 48083, 48085..." />
                      <p className="text-xs mt-1" style={{ color: '#64748B' }}>Comma-separated. We'll also match orders within your radius.</p>
                    </div>
                    <div className="md:col-span-2">
                      <label className="flex items-center gap-3 cursor-pointer">
                        <input type="checkbox" checked={hasVehicle} onChange={e => setHasVehicle(e.target.checked)}
                          className="w-4 h-4 rounded accent-teal-400" />
                        <span className="text-sm">I have a reliable vehicle for mobile appointments</span>
                      </label>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* ── STEP 3: Certifications ── */}
            {step === 3 && (
              <div>
                <h2 className="text-xl font-bold mb-1">Certifications & Credentials</h2>
                <p className="text-sm mb-6" style={{ color: '#94A3B8' }}>Tell us what you're certified for. You can upload documents after registration.</p>

                {/* Notary (conditional) */}
                {(selectedSpecialties.includes('signing') || selectedSpecialties.includes('ron')) && (
                  <div className="rounded-xl p-5 mb-4" style={{ background: 'rgba(15, 26, 46, 0.5)', border: '1px solid rgba(45, 212, 191, 0.15)' }}>
                    <h3 className="font-semibold text-sm mb-3" style={{ color: '#EC4899' }}>🩷 Notary Credentials</h3>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                      <div>
                        <label className="block text-xs mb-1" style={{ color: '#94A3B8' }}>Commissioning State</label>
                        <input type="text" value={notaryState} onChange={e => setNotaryState(e.target.value)}
                          className="w-full rounded-lg px-3 py-2 text-sm text-white focus:outline-none transition" style={inputStyle} onFocus={inputFocus} onBlur={inputBlur} placeholder="Michigan" />
                      </div>
                      <div>
                        <label className="block text-xs mb-1" style={{ color: '#94A3B8' }}>Commission Number</label>
                        <input type="text" value={notaryNumber} onChange={e => setNotaryNumber(e.target.value)}
                          className="w-full rounded-lg px-3 py-2 text-sm text-white focus:outline-none transition" style={inputStyle} onFocus={inputFocus} onBlur={inputBlur} placeholder="NC-XXXXXXX" />
                      </div>
                      <div>
                        <label className="block text-xs mb-1" style={{ color: '#94A3B8' }}>Expiration Date</label>
                        <input type="date" value={notaryExpiration} onChange={e => setNotaryExpiration(e.target.value)}
                          className="w-full rounded-lg px-3 py-2 text-sm text-white focus:outline-none transition" style={inputStyle} onFocus={inputFocus} onBlur={inputBlur} />
                      </div>
                    </div>
                    <div className="flex flex-wrap gap-4 mt-3">
                      <label className="flex items-center gap-2 cursor-pointer">
                        <input type="checkbox" checked={hasNNA} onChange={e => setHasNNA(e.target.checked)} className="w-4 h-4 rounded accent-yellow-500" />
                        <span className="text-sm">NNA Certified Signing Agent</span>
                      </label>
                      <label className="flex items-center gap-2 cursor-pointer">
                        <input type="checkbox" checked={hasEO} onChange={e => setHasEO(e.target.checked)} className="w-4 h-4 rounded accent-yellow-500" />
                        <span className="text-sm">E&O Insurance</span>
                      </label>
                    </div>
                  </div>
                )}

                {/* Drug Testing (conditional) */}
                {(selectedSpecialties.includes('collector-dot') || selectedSpecialties.includes('collector-nondot')) && (
                  <div className="rounded-xl p-5 mb-4" style={{ background: 'rgba(15, 26, 46, 0.5)', border: '1px solid rgba(45, 212, 191, 0.15)' }}>
                    <h3 className="font-semibold text-sm mb-3 text-red-400">🔴 Drug Test Collector Credentials</h3>
                    <label className="flex items-center gap-2 cursor-pointer">
                      <input type="checkbox" checked={hasDOTCert} onChange={e => setHasDOTCert(e.target.checked)} className="w-4 h-4 rounded accent-red-500" />
                      <span className="text-sm">DOT-Certified Collector (49 CFR Part 40)</span>
                    </label>
                  </div>
                )}

                {/* Fingerprinting (conditional) */}
                {selectedSpecialties.includes('fingerprint') && (
                  <div className="rounded-xl p-5 mb-4" style={{ background: 'rgba(15, 26, 46, 0.5)', border: '1px solid rgba(45, 212, 191, 0.15)' }}>
                    <h3 className="font-semibold text-sm mb-3 text-green-400">🟢 Fingerprint / EFT Credentials</h3>
                    <label className="flex items-center gap-2 cursor-pointer">
                      <input type="checkbox" checked={hasLiveScan} onChange={e => setHasLiveScan(e.target.checked)} className="w-4 h-4 rounded accent-green-500" />
                      <span className="text-sm">LiveScan / EFT Certified</span>
                    </label>
                  </div>
                )}

                {/* Background Check (conditional) */}
                {selectedSpecialties.includes('background') && (
                  <div className="rounded-xl p-5 mb-4" style={{ background: 'rgba(15, 26, 46, 0.5)', border: '1px solid rgba(45, 212, 191, 0.15)' }}>
                    <h3 className="font-semibold text-sm mb-3" style={{ color: '#94A3B8' }}>⚫ Background Check Credentials</h3>
                    <label className="flex items-center gap-2 cursor-pointer">
                      <input type="checkbox" checked={hasFCRA} onChange={e => setHasFCRA(e.target.checked)} className="w-4 h-4 rounded accent-gray-500" />
                      <span className="text-sm">FCRA Certified</span>
                    </label>
                  </div>
                )}

                {/* Other Certs */}
                <div className="mb-6">
                  <label className="block text-xs font-semibold mb-1" style={{ color: '#94A3B8' }}>Other Certifications (optional)</label>
                  <textarea value={otherCerts} onChange={e => setOtherCerts(e.target.value)}
                    className="w-full rounded-xl px-4 py-3 text-sm text-white focus:outline-none transition h-20 resize-none"
                    style={inputStyle}
                    onFocus={inputFocus as any} onBlur={inputBlur as any}
                    placeholder="List any other relevant certifications, training, or qualifications..." />
                </div>

                {/* Background Check Agreement */}
                <div className="rounded-xl p-5" style={{ background: 'rgba(245, 158, 11, 0.08)', border: '1px solid rgba(245, 158, 11, 0.25)' }}>
                  <label className="flex items-start gap-3 cursor-pointer">
                    <input type="checkbox" checked={agreeBackgroundCheck} onChange={e => setAgreeBackgroundCheck(e.target.checked)}
                      className="w-5 h-5 rounded mt-0.5 flex-shrink-0 accent-yellow-500" />
                    <div>
                      <p className="font-semibold text-sm" style={{ color: '#F59E0B' }}>Background Check Authorization *</p>
                      <p className="text-xs mt-1" style={{ color: '#94A3B8' }}>I understand that Dee Davis Inc. will conduct a background check as part of the agent application process. I consent to this screening and understand that my application will not be processed without it.</p>
                    </div>
                  </label>
                </div>
              </div>
            )}

            {/* ── STEP 4: Account Setup ── */}
            {step === 4 && (
              <div>
                <h2 className="text-xl font-bold mb-1">Create Your Account</h2>
                <p className="text-sm mb-6" style={{ color: '#94A3B8' }}>Set your password and agree to our terms</p>

                <div className="space-y-4 mb-6">
                  <div>
                    <label className="block text-xs font-semibold mb-1" style={{ color: '#94A3B8' }}>Password *</label>
                    <input type="password" value={password} onChange={e => setPassword(e.target.value)}
                      className="w-full rounded-xl px-4 py-3 text-sm text-white focus:outline-none transition"
                      style={inputStyle} onFocus={inputFocus} onBlur={inputBlur}
                      placeholder="Minimum 8 characters" autoComplete="new-password" />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold mb-1" style={{ color: '#94A3B8' }}>Confirm Password *</label>
                    <input type="password" value={confirmPassword} onChange={e => setConfirmPassword(e.target.value)}
                      className="w-full rounded-xl px-4 py-3 text-sm text-white focus:outline-none transition"
                      style={{
                        ...inputStyle,
                        borderColor: confirmPassword && confirmPassword !== password ? '#EF4444' : 'rgba(45, 212, 191, 0.2)',
                      }}
                      onFocus={inputFocus} onBlur={inputBlur}
                      placeholder="Re-enter password" autoComplete="new-password" />
                    {confirmPassword && confirmPassword !== password && (
                      <p className="text-red-400 text-xs mt-1">Passwords don't match</p>
                    )}
                  </div>
                </div>

                {/* Password Strength */}
                {password && (
                  <div className="mb-6">
                    <div className="flex gap-1 mb-1">
                      {[1, 2, 3, 4].map(i => (
                        <div key={i} className="h-1.5 flex-1 rounded" style={{
                          background: password.length >= i * 3
                            ? (password.length >= 12 ? '#2DD4BF' : password.length >= 8 ? '#F59E0B' : '#EF4444')
                            : 'rgba(27, 42, 74, 0.8)',
                        }}></div>
                      ))}
                    </div>
                    <p className="text-xs" style={{ color: '#64748B' }}>{password.length >= 12 ? 'Strong' : password.length >= 8 ? 'Good' : 'Too short'}</p>
                  </div>
                )}

                {/* Agreements */}
                <div className="space-y-3">
                  <label className="flex items-start gap-3 cursor-pointer rounded-xl p-4" style={{ background: 'rgba(15, 26, 46, 0.5)', border: '1px solid rgba(45, 212, 191, 0.15)' }}>
                    <input type="checkbox" checked={agreeTerms} onChange={e => setAgreeTerms(e.target.checked)}
                      className="w-5 h-5 rounded mt-0.5 flex-shrink-0 accent-teal-400" />
                    <div>
                      <p className="font-semibold text-sm">Terms of Service & Independent Contractor Agreement *</p>
                      <p className="text-xs mt-1" style={{ color: '#64748B' }}>I agree to the Dee Davis Inc. Field Agent Terms of Service and acknowledge that I am operating as an independent contractor, not an employee.</p>
                    </div>
                  </label>
                  <label className="flex items-start gap-3 cursor-pointer rounded-xl p-4" style={{ background: 'rgba(15, 26, 46, 0.5)', border: '1px solid rgba(45, 212, 191, 0.15)' }}>
                    <input type="checkbox" checked={agreeNDA} onChange={e => setAgreeNDA(e.target.checked)}
                      className="w-5 h-5 rounded mt-0.5 flex-shrink-0 accent-teal-400" />
                    <div>
                      <p className="font-semibold text-sm">Non-Disclosure Agreement (NDA) *</p>
                      <p className="text-xs mt-1" style={{ color: '#64748B' }}>I agree not to disclose client information, signer details, document contents, or any proprietary business information obtained through assignments with Dee Davis Inc.</p>
                    </div>
                  </label>
                </div>

                {/* What Happens Next */}
                <div className="mt-6 rounded-xl p-5" style={{ background: 'rgba(45, 212, 191, 0.08)', border: '1px solid rgba(45, 212, 191, 0.2)' }}>
                  <h4 className="font-semibold text-sm mb-2" style={{ color: '#2DD4BF' }}>What happens after you apply?</h4>
                  <div className="space-y-2 text-xs" style={{ color: '#94A3B8' }}>
                    <p>1. We review your application (1-2 business days)</p>
                    <p>2. Background check is initiated</p>
                    <p>3. We verify your certifications</p>
                    <p>4. You'll receive an email when approved</p>
                    <p>5. Orders start coming your way based on your specialties and area</p>
                  </div>
                </div>
              </div>
            )}

            {/* ── Navigation Buttons ── */}
            <div className="flex items-center justify-between mt-8 pt-6" style={{ borderTop: '1px solid rgba(45, 212, 191, 0.1)' }}>
              {step > 1 ? (
                <button type="button" onClick={() => setStep(step - 1)}
                  className="transition font-semibold text-sm hover:text-white" style={{ color: '#94A3B8' }}>
                  ← Back
                </button>
              ) : (
                <div></div>
              )}

              {step < 4 ? (
                <button type="button" onClick={() => setStep(step + 1)} disabled={!canProceed()}
                  className="disabled:opacity-40 disabled:cursor-not-allowed px-8 py-3 rounded-xl font-bold text-sm text-white transition"
                  style={{ background: '#EC4899', boxShadow: '0 4px 15px rgba(236, 72, 153, 0.3)' }}>
                  Continue →
                </button>
              ) : (
                <button type="button" onClick={handleSubmit} disabled={!canProceed() || loading}
                  className="disabled:opacity-40 disabled:cursor-not-allowed px-8 py-3 rounded-xl font-bold text-sm text-white transition"
                  style={{ background: 'linear-gradient(135deg, #2DD4BF, #14B8A6)', boxShadow: '0 4px 15px rgba(45, 212, 191, 0.3)' }}>
                  {loading ? 'Submitting...' : '🚀 Submit Application'}
                </button>
              )}
            </div>
          </div>

          {/* Already have account */}
          <div className="text-center mt-6">
            <button onClick={onSwitchToLogin} className="text-sm transition hover:text-white" style={{ color: '#64748B' }}>
              Already have an account? <span className="font-semibold" style={{ color: '#2DD4BF' }}>Sign in</span>
            </button>
          </div>
        </div>
      </div>

      {/* ─── FOOTER ──────────────────────────────────── */}
      <div className="w-full border-t px-6 py-4" style={{ background: 'rgba(15, 26, 46, 0.9)', borderColor: 'rgba(45, 212, 191, 0.1)' }}>
        <div className="max-w-2xl mx-auto flex items-center justify-between text-[11px]" style={{ color: '#475569' }}>
          <span>© 2026 Dee Davis Inc. All rights reserved.</span>
          <div className="flex gap-4">
            <button className="hover:text-gray-300 transition">Privacy</button>
            <button className="hover:text-gray-300 transition">Terms</button>
            <button className="hover:text-gray-300 transition">Support</button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AgentRegistration;
