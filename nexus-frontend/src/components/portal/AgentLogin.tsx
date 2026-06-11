import React, { useState } from 'react';

// DDI Brand Colors
// Deep Blue: #1B2A4A (primary dark — backgrounds, headers)
// Teal: #2DD4BF (accent — highlights, active states, links)
// Pink: #EC4899 (secondary accent — CTAs, energy, buttons)
// Gold: #F59E0B (premium — certifications, warmth, badges)

interface AgentLoginProps {
  onLogin: (email: string, password: string) => void;
  onSwitchToRegister: () => void;
  error?: string;
  loading?: boolean;
}

const AgentLogin: React.FC<AgentLoginProps> = ({ onLogin, onSwitchToRegister, error, loading }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (email.trim() && password.trim()) {
      onLogin(email.trim(), password.trim());
    }
  };

  return (
    <div className="min-h-screen flex flex-col" style={{ background: 'linear-gradient(135deg, #0F1A2E 0%, #1B2A4A 50%, #0F1A2E 100%)' }}>
      {/* ─── TOP BAR ─────────────────────────────────── */}
      <div className="w-full border-b border-white/10 px-6 py-4" style={{ background: 'rgba(15, 26, 46, 0.9)' }}>
        <div className="max-w-md mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl flex items-center justify-center text-white font-black text-sm shadow-lg" style={{ background: 'linear-gradient(135deg, #EC4899, #DB2777)', boxShadow: '0 4px 15px rgba(236, 72, 153, 0.3)' }}>
              DDI
            </div>
            <div>
              <p className="font-bold text-white text-sm">DDI</p>
              <p className="text-[10px] uppercase tracking-wider" style={{ color: '#2DD4BF' }}>Field Agent Portal</p>
            </div>
          </div>
          <span className="text-[10px] uppercase tracking-widest" style={{ color: 'rgba(45, 212, 191, 0.5)' }}>Powered by PRISM</span>
        </div>
      </div>

      {/* ─── LOGIN CARD ──────────────────────────────── */}
      <div className="flex-1 flex items-center justify-center px-4 py-12">
        <div className="w-full max-w-md">
          {/* Header */}
          <div className="text-center mb-8">
            <div className="w-20 h-20 rounded-2xl flex items-center justify-center mx-auto mb-5 shadow-2xl" style={{ background: 'linear-gradient(135deg, #EC4899, #DB2777)', boxShadow: '0 8px 30px rgba(236, 72, 153, 0.35)' }}>
              <span className="text-3xl">🔮</span>
            </div>
            <h1 className="text-3xl font-black text-white mb-2">Welcome Back</h1>
            <p style={{ color: '#94A3B8' }}>Sign in to your Field Agent account</p>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="backdrop-blur rounded-2xl p-8 shadow-2xl" style={{ background: 'rgba(27, 42, 74, 0.7)', border: '1px solid rgba(45, 212, 191, 0.15)' }}>
            {/* Error */}
            {error && (
              <div className="rounded-lg px-4 py-3 mb-6" style={{ background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.3)' }}>
                <p className="text-red-400 text-sm font-semibold">{error}</p>
              </div>
            )}

            {/* Email */}
            <div className="mb-5">
              <label className="block text-sm font-semibold mb-2" style={{ color: '#CBD5E1' }}>Email Address</label>
              <div className="relative">
                <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500">✉️</span>
                <input
                  type="email"
                  value={email}
                  onChange={e => setEmail(e.target.value)}
                  placeholder="you@email.com"
                  className="w-full rounded-xl pl-10 pr-4 py-3 text-sm text-white placeholder-gray-500 focus:outline-none transition"
                  style={{ background: 'rgba(15, 26, 46, 0.8)', border: '1px solid rgba(45, 212, 191, 0.2)' }}
                  onFocus={e => { e.target.style.borderColor = '#2DD4BF'; e.target.style.boxShadow = '0 0 0 2px rgba(45, 212, 191, 0.2)'; }}
                  onBlur={e => { e.target.style.borderColor = 'rgba(45, 212, 191, 0.2)'; e.target.style.boxShadow = 'none'; }}
                  required
                  autoComplete="email"
                />
              </div>
            </div>

            {/* Password */}
            <div className="mb-6">
              <div className="flex items-center justify-between mb-2">
                <label className="text-sm font-semibold" style={{ color: '#CBD5E1' }}>Password</label>
                <button type="button" className="text-xs font-semibold transition hover:opacity-80" style={{ color: '#2DD4BF' }}>
                  Forgot password?
                </button>
              </div>
              <div className="relative">
                <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500">🔒</span>
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={e => setPassword(e.target.value)}
                  placeholder="Enter your password"
                  className="w-full rounded-xl pl-10 pr-12 py-3 text-sm text-white placeholder-gray-500 focus:outline-none transition"
                  style={{ background: 'rgba(15, 26, 46, 0.8)', border: '1px solid rgba(45, 212, 191, 0.2)' }}
                  onFocus={e => { e.target.style.borderColor = '#2DD4BF'; e.target.style.boxShadow = '0 0 0 2px rgba(45, 212, 191, 0.2)'; }}
                  onBlur={e => { e.target.style.borderColor = 'rgba(45, 212, 191, 0.2)'; e.target.style.boxShadow = 'none'; }}
                  required
                  autoComplete="current-password"
                />
                <button type="button" onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-300 transition text-sm">
                  {showPassword ? '🙈' : '👁️'}
                </button>
              </div>
            </div>

            {/* Remember Me */}
            <div className="flex items-center gap-2 mb-6">
              <input type="checkbox" id="remember" className="w-4 h-4 rounded border-gray-600 bg-gray-900 accent-pink-500" />
              <label htmlFor="remember" className="text-sm" style={{ color: '#94A3B8' }}>Keep me signed in</label>
            </div>

            {/* Submit */}
            <button type="submit" disabled={loading || !email || !password}
              className="w-full disabled:opacity-50 disabled:cursor-not-allowed px-6 py-3.5 rounded-xl font-bold text-white text-sm transition"
              style={{ background: 'linear-gradient(135deg, #EC4899, #DB2777)', boxShadow: '0 4px 15px rgba(236, 72, 153, 0.3)' }}
              onMouseEnter={e => { if (!loading) (e.target as HTMLElement).style.boxShadow = '0 6px 20px rgba(236, 72, 153, 0.45)'; }}
              onMouseLeave={e => { (e.target as HTMLElement).style.boxShadow = '0 4px 15px rgba(236, 72, 153, 0.3)'; }}
            >
              {loading ? (
                <span className="flex items-center justify-center gap-2">
                  <svg className="animate-spin w-4 h-4" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" /><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" /></svg>
                  Signing in...
                </span>
              ) : 'Sign In'}
            </button>
          </form>

          {/* Register Link */}
          <div className="text-center mt-6">
            <p className="text-sm" style={{ color: '#64748B' }}>
              Not an agent yet?{' '}
              <button onClick={onSwitchToRegister} className="font-semibold transition hover:opacity-80" style={{ color: '#2DD4BF' }}>
                Apply to join our network →
              </button>
            </p>
          </div>

          {/* Trust Indicators */}
          <div className="mt-10 flex items-center justify-center gap-6 text-[10px] uppercase tracking-wider" style={{ color: 'rgba(245, 158, 11, 0.6)' }}>
            <span>🔒 256-bit Encrypted</span>
            <span style={{ color: 'rgba(45, 212, 191, 0.3)' }}>•</span>
            <span>EDWOSB Certified</span>
            <span style={{ color: 'rgba(45, 212, 191, 0.3)' }}>•</span>
            <span>Troy, MI</span>
          </div>
        </div>
      </div>

      {/* ─── FOOTER ──────────────────────────────────── */}
      <div className="w-full border-t px-6 py-4" style={{ background: 'rgba(15, 26, 46, 0.9)', borderColor: 'rgba(45, 212, 191, 0.1)' }}>
        <div className="max-w-md mx-auto flex items-center justify-between text-[11px]" style={{ color: '#475569' }}>
          <span>© 2026 DDI · Legal entity: Dee Davis Inc.</span>
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

export default AgentLogin;
