import React, { useState } from 'react';
import Header, { ViewType } from './components/Header';
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
import TariffRefundNavigator from './components/fleetflow/TariffRefundNavigator';

function App() {
  const isPublicReferrer = typeof window !== 'undefined' && window.location.pathname === '/refer';
  if (isPublicReferrer) {
    return <PublicReferrerIntake />;
  }
  return <NexusApp />;
}

function NexusApp() {
  const [currentView, setCurrentView] = useState<ViewType>('landing');
  const [currentSystemTab, setCurrentSystemTab] = useState('dashboard');
  // Simplified: Single Command Center view, no confusing tab switching

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
      <Header currentView={currentView} onBackToNexus={navigateToLanding} />
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
