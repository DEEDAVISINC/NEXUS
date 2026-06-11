import React, { useState } from 'react';
import AgentLogin from './AgentLogin';
import AgentRegistration from './AgentRegistration';
import FieldAgentPortal from '../systems/FieldAgentPortal';

// DDI Brand Colors
// Deep Blue: #1B2A4A (primary dark — backgrounds, headers)
// Teal: #2DD4BF (accent — highlights, active states, links)
// Pink: #EC4899 (secondary accent — CTAs, energy, buttons)
// Gold: #F59E0B (premium — certifications, warmth, badges)

interface AgentPortalRouterProps {
  onBackToNexus: () => void;
  skipLogin?: boolean;
}

type PortalView = 'login' | 'register' | 'portal' | 'submitted';

const AgentPortalRouter: React.FC<AgentPortalRouterProps> = ({ onBackToNexus, skipLogin }) => {
  const [view, setView] = useState<PortalView>(skipLogin ? 'portal' : 'login');
  const [loginError, setLoginError] = useState('');
  const [loginLoading, setLoginLoading] = useState(false);
  const [registerLoading, setRegisterLoading] = useState(false);
  const [portalTab, setPortalTab] = useState('dashboard');
  const [applicantName, setApplicantName] = useState('');

  const handleLogin = (email: string, password: string) => {
    setLoginLoading(true);
    setLoginError('');

    // Simulated login — replace with real API call later
    setTimeout(() => {
      // Demo: accept any login with "agent" in email or use demo credentials
      if (email.includes('agent') || email === 'sarah@email.com' || email === 'demo@deedavis.biz') {
        setView('portal');
      } else {
        setLoginError('Invalid email or password. Try demo@deedavis.biz / any password.');
      }
      setLoginLoading(false);
    }, 800);
  };

  const handleRegister = (data: any) => {
    setRegisterLoading(true);
    setApplicantName(data.firstName);

    // Simulated registration — replace with real API call later
    setTimeout(() => {
      setView('submitted');
      setRegisterLoading(false);
    }, 1200);
  };

  // ─── LOGIN ────────────────────────────────────────
  if (view === 'login') {
    return (
      <AgentLogin
        onLogin={handleLogin}
        onSwitchToRegister={() => { setView('register'); setLoginError(''); }}
        error={loginError}
        loading={loginLoading}
      />
    );
  }

  // ─── REGISTRATION ─────────────────────────────────
  if (view === 'register') {
    return (
      <AgentRegistration
        onRegister={handleRegister}
        onSwitchToLogin={() => setView('login')}
        loading={registerLoading}
      />
    );
  }

  // ─── APPLICATION SUBMITTED ────────────────────────
  if (view === 'submitted') {
    return (
      <div className="min-h-screen flex flex-col" style={{ background: 'linear-gradient(135deg, #0F1A2E 0%, #1B2A4A 50%, #0F1A2E 100%)' }}>
        <div className="w-full border-b px-6 py-4" style={{ background: 'rgba(15, 26, 46, 0.9)', borderColor: 'rgba(45, 212, 191, 0.1)' }}>
          <div className="max-w-md mx-auto flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl flex items-center justify-center text-white font-black text-sm shadow-lg" style={{ background: 'linear-gradient(135deg, #EC4899, #DB2777)', boxShadow: '0 4px 15px rgba(236, 72, 153, 0.3)' }}>DDI</div>
            <div>
              <p className="font-bold text-white text-sm">DDI</p>
              <p className="text-[10px] uppercase tracking-wider" style={{ color: '#2DD4BF' }}>Field Agent Portal</p>
            </div>
          </div>
        </div>

        <div className="flex-1 flex items-center justify-center px-4">
          <div className="max-w-md text-center">
            <div className="w-24 h-24 rounded-3xl flex items-center justify-center mx-auto mb-6 shadow-2xl" style={{ background: 'linear-gradient(135deg, #2DD4BF, #14B8A6)', boxShadow: '0 8px 30px rgba(45, 212, 191, 0.35)' }}>
              <span className="text-5xl">✅</span>
            </div>
            <h1 className="text-3xl font-black text-white mb-3">Application Submitted!</h1>
            <p className="mb-8" style={{ color: '#94A3B8' }}>
              Thank you, {applicantName}! We've received your application to join the DDI Field Agent Network. Here's what happens next:
            </p>

            <div className="rounded-2xl p-6 text-left mb-8" style={{ background: 'rgba(27, 42, 74, 0.7)', border: '1px solid rgba(45, 212, 191, 0.15)' }}>
              <div className="space-y-4">
                {[
                  { step: '1', label: 'Application Review', desc: 'Our team reviews your qualifications (1-2 business days)', status: 'In Progress' },
                  { step: '2', label: 'Background Check', desc: 'We initiate your background screening', status: 'Upcoming' },
                  { step: '3', label: 'Certification Verification', desc: 'We verify your licenses and certifications', status: 'Upcoming' },
                  { step: '4', label: 'Approval & Onboarding', desc: 'You\'ll receive an email with login instructions', status: 'Upcoming' },
                  { step: '5', label: 'Start Receiving Orders', desc: 'Orders matched to your specialties and area', status: 'Upcoming' },
                ].map((item, i) => (
                  <div key={i} className="flex items-start gap-3">
                    <div className="w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0"
                      style={{
                        background: item.status === 'In Progress' ? '#EC4899' : 'rgba(27, 42, 74, 0.8)',
                        color: item.status === 'In Progress' ? 'white' : '#64748B',
                        boxShadow: item.status === 'In Progress' ? '0 0 10px rgba(236, 72, 153, 0.3)' : 'none',
                      }}>{item.step}</div>
                    <div>
                      <p className="font-semibold text-sm">{item.label}</p>
                      <p className="text-xs" style={{ color: '#64748B' }}>{item.desc}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <p className="text-sm mb-6" style={{ color: '#64748B' }}>
              Questions? Email <a href="mailto:agents@deedavis.biz" className="transition hover:opacity-80" style={{ color: '#2DD4BF' }}>agents@deedavis.biz</a> or call <a href="tel:2483764550" className="transition hover:opacity-80" style={{ color: '#2DD4BF' }}>(248) 376-4550</a>
            </p>

            <button onClick={() => setView('login')}
              className="px-6 py-3 rounded-xl font-semibold text-sm text-white transition hover:opacity-90"
              style={{ background: 'rgba(27, 42, 74, 0.8)', border: '1px solid rgba(45, 212, 191, 0.2)' }}>
              ← Back to Login
            </button>
          </div>
        </div>

        <div className="w-full border-t px-6 py-4" style={{ background: 'rgba(15, 26, 46, 0.9)', borderColor: 'rgba(45, 212, 191, 0.1)' }}>
          <div className="max-w-md mx-auto text-center text-[11px]" style={{ color: '#475569' }}>
            © 2026 DDI · Legal entity: Dee Davis Inc.
          </div>
        </div>
      </div>
    );
  }

  // ─── AGENT PORTAL (Authenticated) ─────────────────
  return (
    <div className="min-h-screen text-white" style={{ background: '#0F1A2E' }}>
      {/* Portal Header (replaces NEXUS header) */}
      <header className="sticky top-0 z-50" style={{ background: '#1B2A4A', borderBottom: '1px solid rgba(45, 212, 191, 0.15)' }}>
        <div className="max-w-5xl mx-auto px-6 py-3">
          <div className="flex justify-between items-center">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-xl flex items-center justify-center text-white font-black text-xs shadow-lg" style={{ background: 'linear-gradient(135deg, #EC4899, #DB2777)', boxShadow: '0 4px 12px rgba(236, 72, 153, 0.3)' }}>DDI</div>
              <div>
                <h1 className="text-lg font-bold text-white">DDI</h1>
                <p className="text-[10px] uppercase tracking-wider" style={{ color: '#2DD4BF' }}>Field Agent Portal</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-2 px-3 py-1 rounded-lg text-xs" style={{ background: 'rgba(45, 212, 191, 0.15)' }}>
                <div className="w-2 h-2 rounded-full animate-pulse" style={{ background: '#2DD4BF' }}></div>
                <span className="font-semibold" style={{ color: '#2DD4BF' }}>Online</span>
              </div>
              <button onClick={() => { setView('login'); }}
                className="transition text-sm font-semibold hover:text-red-400" style={{ color: '#94A3B8' }}>
                Sign Out
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Agent Portal Content */}
      <FieldAgentPortal
        onBackToNexus={onBackToNexus}
        activeTab={portalTab}
        setActiveTab={setPortalTab}
      />
    </div>
  );
};

export default AgentPortalRouter;
