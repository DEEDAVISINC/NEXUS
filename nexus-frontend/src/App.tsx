import React, { useState } from 'react';
import Header, { ViewType, NexusIdentity, getNexusIdentity } from './components/Header';
import HIPAAGate from './components/shield/HIPAAGate';
import LandingPage from './components/LandingPage';
import GPSSSystem from './components/systems/GPSSSystem';
import DDCSSSystem from './components/systems/DDCSSSystem';
import ATLASSystem from './components/systems/ATLASSystem';
import GBISSystem from './components/systems/GBISSystem';
import VERTEXSystem from './components/systems/VERTEXSystem';
import { LBPCSystem } from './components/systems/LBPCSystem';
import { InvoiceDashboard } from './components/InvoiceDashboard';
import { FloatingAICopilot } from './components/FloatingAICopilot';
import { QuoteSystem } from './components/systems/QuoteSystem';
import { CapStatSystem } from './components/systems/CapStatSystem';
import { DocumentGenerator } from './components/systems/DocumentGenerator';
import PRISMSystem from './components/systems/PRISMSystem';
import COMPASSSystem from './components/systems/COMPASSSystem';
import FieldAgentPortal from './components/systems/FieldAgentPortal';
import AgentPortalRouter from './components/portal/AgentPortalRouter';
import NOVASystem from './components/systems/NOVASystem';
import AlexaSystem from './components/systems/AlexaSystem';
import JETASystem from './components/systems/JETASystem';
import SHIELDSystem from './components/systems/SHIELDSystem';
import PublicReferrerIntake from './components/public/PublicReferrerIntake';
import FamilyStatusTracker from './components/public/FamilyStatusTracker';
import NavigatorWorkspace from './components/shield/NavigatorWorkspace';
import TariffRefundNavigator from './components/fleetflow/TariffRefundNavigator';
import MDHHSPartnerPortal from './components/public/MDHHSPartnerPortal';
import { api } from './api/client';

function App() {
  const path = typeof window !== 'undefined' ? window.location.pathname : '';
  if (path === '/refer') return <HIPAAGate><PublicReferrerIntake /></HIPAAGate>;
  if (path === '/status') return <HIPAAGate><FamilyStatusTracker /></HIPAAGate>;
  if (path === '/navigator') return <NavigatorLogin />;
  if (path === '/mdhhs') return <HIPAAGate><MDHHSPartnerPortal /></HIPAAGate>;
  return <NexusApp />;
}

function NavigatorLogin() {
  const [loggedIn, setLoggedIn] = useState(false);
  const [nav, setNav] = useState<{
    email: string;
    name: string;
    role: string;
    supervisor_access?: boolean;
  } | null>(null);
  const [email, setEmail] = useState('');
  const [name, setName] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  if (loggedIn && nav) {
    return <NavigatorWorkspace navigator={nav} onLogout={() => { setLoggedIn(false); setNav(null); }} />;
  }

  const handleLogin = async () => {
    if (!name.trim() || !email.trim()) { setError('Name and email are required.'); return; }
    setLoading(true);
    setError('');
    try {
      const res: any = await api.shieldNavigatorLogin({ email: email.trim(), name: name.trim() });
      if (res?.success && res.navigator) {
        setNav({
          email: res.navigator.email,
          name: res.navigator.name,
          role: res.navigator.role || 'Navigator',
          supervisor_access: res.navigator.supervisor_access,
        });
        setLoggedIn(true);
      } else {
        setError(res?.error || 'Login failed. Contact your supervisor.');
      }
    } catch {
      setError('Unable to reach server. Check your connection and try again.');
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-[#050f2e] flex items-center justify-center px-4">
      <div className="w-full max-w-sm">
        <div className="text-center mb-8">
          <img src="/cwc-logo.png" alt="CWC" className="w-20 h-20 rounded-xl object-contain bg-[#f5c23e]/20 p-2 mx-auto mb-4" />
          <h1 className="text-2xl font-black text-white">🛡️ SHIELD Navigator</h1>
          <p className="text-xs text-[#8ea2d6] mt-1">Care. Navigate. Transform.</p>
        </div>
        <div className="bg-[#081849] border border-[#1c2f6a] rounded-xl p-6 space-y-4">
          <div>
            <label className="text-[10px] text-[#8ea2d6] uppercase tracking-wider font-bold block mb-1">Your name</label>
            <input
              value={name}
              onChange={e => setName(e.target.value)}
              onKeyDown={e => { if (e.key === 'Enter') handleLogin(); }}
              placeholder="e.g. Angela Johnson"
              className="w-full bg-[#050f2e] border border-[#1c2f6a] rounded-lg px-4 py-3 text-sm text-white placeholder:text-[#6b7ba6] focus:border-[#f5c23e] focus:outline-none"
            />
          </div>
          <div>
            <label className="text-[10px] text-[#8ea2d6] uppercase tracking-wider font-bold block mb-1">Email</label>
            <input
              value={email}
              onChange={e => setEmail(e.target.value)}
              onKeyDown={e => { if (e.key === 'Enter') handleLogin(); }}
              placeholder="navigator@cwcare.org"
              className="w-full bg-[#050f2e] border border-[#1c2f6a] rounded-lg px-4 py-3 text-sm text-white placeholder:text-[#6b7ba6] focus:border-[#f5c23e] focus:outline-none"
            />
          </div>
          {error && <div className="text-xs text-red-400">{error}</div>}
          <button
            onClick={handleLogin}
            disabled={loading}
            className="w-full bg-[#f5c23e] hover:bg-[#fcd75a] disabled:opacity-60 text-[#081849] py-3 rounded-xl text-sm font-black transition"
          >
            {loading ? 'Verifying...' : 'Sign In'}
          </button>
        </div>
        <div className="text-center mt-4 text-[10px] text-[#8ea2d6]">
          Every Family Deserves a SHIELD 🛡️
        </div>
      </div>
    </div>
  );
}

function NexusApp() {
  const [currentView, setCurrentView] = useState<ViewType>('landing');
  const [currentSystemTab, setCurrentSystemTab] = useState('dashboard');
  const [identity, setIdentity] = useState<NexusIdentity>(getNexusIdentity);

  const navigateToSystem = (system: ViewType, initialTab?: string) => {
    setCurrentView(system);
    // JETA COURTIÈRE always lands on Dashboard (module home).
    if (system === 'jeta') {
      setCurrentSystemTab('dashboard');
    } else {
      setCurrentSystemTab(initialTab || 'dashboard');
    }
  };

  const navigateToLanding = () => {
    setCurrentView('landing');
  };

  const renderCurrentView = () => {
    switch (currentView) {
      case 'gpss':
        return <GPSSSystem onBackToNexus={navigateToLanding} activeTab={currentSystemTab} setActiveTab={setCurrentSystemTab} />;
      case 'ddcss':
        return <DDCSSSystem onBackToNexus={navigateToLanding} activeTab={currentSystemTab} setActiveTab={setCurrentSystemTab} />;
      case 'atlas':
        return <ATLASSystem onBackToNexus={navigateToLanding} activeTab={currentSystemTab} setActiveTab={setCurrentSystemTab} />;
      case 'gbis':
        return <GBISSystem onBackToNexus={navigateToLanding} activeTab={currentSystemTab} setActiveTab={setCurrentSystemTab} />;
      case 'vertex':
        return <VERTEXSystem onBackToNexus={navigateToLanding} activeTab={currentSystemTab} setActiveTab={setCurrentSystemTab} />;
      case 'lbpc':
        return <LBPCSystem />;
      case 'invoices':
        return <InvoiceDashboard />;
      case 'documents':
        return <DocumentGenerator onBackToNexus={navigateToLanding} activeTab={currentSystemTab} setActiveTab={setCurrentSystemTab} />;
      case 'quotes':
        return <QuoteSystem onBackToNexus={navigateToLanding} activeTab={currentSystemTab} setActiveTab={setCurrentSystemTab} />;
      case 'capstats':
        return <CapStatSystem onBackToNexus={navigateToLanding} activeTab={currentSystemTab} setActiveTab={setCurrentSystemTab} />;
      case 'compass':
        return <COMPASSSystem onBackToNexus={navigateToLanding} activeTab={currentSystemTab} setActiveTab={setCurrentSystemTab} />;
      case 'prism':
        return <PRISMSystem onBackToNexus={navigateToLanding} onNavigate={navigateToSystem} activeTab={currentSystemTab} setActiveTab={setCurrentSystemTab} />;
      case 'agent-portal':
        // Agent portal preview (from PRISM admin — no login wall)
        return <FieldAgentPortal onBackToNexus={navigateToLanding} activeTab={currentSystemTab} setActiveTab={setCurrentSystemTab} />;
      case 'opportunity-hunter':
        return <NOVASystem onBackToNexus={navigateToLanding} activeTab={currentSystemTab} setActiveTab={setCurrentSystemTab} />;
      case 'alexa':
        return <AlexaSystem onBackToNexus={navigateToLanding} activeTab={currentSystemTab} setActiveTab={setCurrentSystemTab} />;
      case 'jeta':
        return <JETASystem onBackToNexus={navigateToLanding} activeTab={currentSystemTab} setActiveTab={setCurrentSystemTab} />;
      case 'shield':
        return <SHIELDSystem onBackToNexus={navigateToLanding} activeTab={currentSystemTab} setActiveTab={setCurrentSystemTab} />;
      default:
        return <LandingPage onEnterSystem={navigateToSystem} />;
    }
  };

  // ─── STANDALONE AGENT PORTAL (own header, no NEXUS chrome) ───
  if (currentView === 'agent-login' || currentView === 'agent-portal') {
    return <AgentPortalRouter onBackToNexus={navigateToLanding} skipLogin />;
  }

  if (currentView === 'fleetflow-cape') {
    return <TariffRefundNavigator onBackToNexus={navigateToLanding} />;
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <Header currentView={currentView} onBackToNexus={navigateToLanding} identity={identity} onIdentityChange={setIdentity} />
      {currentView === 'landing' && (
        <>
          {/* Simple Command Center - just deadlines + stats + systems */}
          <LandingPage onEnterSystem={navigateToSystem} />
        </>
      )}

      {/* Individual system views */}
      {currentView !== 'landing' && renderCurrentView()}
      <FloatingAICopilot />
    </div>
  );
}

export default App;
