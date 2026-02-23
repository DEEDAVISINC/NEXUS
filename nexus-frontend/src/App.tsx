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
import { DeadlineNotifications } from './components/DeadlineNotifications';
import { AgendaDashboard } from './components/AgendaDashboard';
import { BidsDashboard } from './components/BidsDashboard';
import { BidsFlow } from './components/BidsFlow';
import { ContractIntelligence } from './components/ContractIntelligence';
import { NexusAdvisorPanel } from './components/NexusAdvisorPanel';
import { AutonomousPanel } from './components/AutonomousPanel';

function App() {
  const [currentView, setCurrentView] = useState<ViewType>('landing');
  const [currentSystemTab, setCurrentSystemTab] = useState('dashboard');
  const [showAgenda, setShowAgenda] = useState(true);
  const [showBidsDashboard, setShowBidsDashboard] = useState(false);
  const [showBidsFlow, setShowBidsFlow] = useState(false);
  const [showIntelligence, setShowIntelligence] = useState(false);
  const [showAdvisor, setShowAdvisor] = useState(false);
  const [showAutonomous, setShowAutonomous] = useState(false);

  const navigateToSystem = (system: ViewType) => {
    setCurrentView(system);
    setCurrentSystemTab('dashboard');
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
      default:
        return <LandingPage onEnterSystem={navigateToSystem} />;
    }
  };

  // ─── STANDALONE AGENT PORTAL (own header, no NEXUS chrome) ───
  if (currentView === 'agent-login' || currentView === 'agent-portal') {
    return <AgentPortalRouter onBackToNexus={navigateToLanding} skipLogin />;
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <Header currentView={currentView} onBackToNexus={navigateToLanding} />
      {currentView === 'landing' && <DeadlineNotifications onNavigateToSystem={navigateToSystem} />}
      
      {/* View Switcher */}
      {currentView === 'landing' && (
        <div className="bg-gray-800 border-b border-gray-700 px-6 py-2 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <button
              onClick={() => {
                setShowAgenda(true);
                setShowBidsFlow(false);
                setShowBidsDashboard(false);
                setShowIntelligence(false);
                setShowAdvisor(false);
                setShowAutonomous(false);
              }}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg transition font-medium ${
                showAgenda ? 'bg-blue-500 hover:bg-blue-600' : 'bg-gray-700 hover:bg-gray-600'
              }`}
            >
              <span>Agenda</span>
            </button>
            <button
              onClick={() => {
                setShowAutonomous(true);
                setShowAgenda(false);
                setShowBidsFlow(false);
                setShowBidsDashboard(false);
                setShowIntelligence(false);
                setShowAdvisor(false);
              }}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg transition font-medium ${
                showAutonomous ? 'bg-indigo-500 hover:bg-indigo-600' : 'bg-gray-700 hover:bg-gray-600'
              }`}
            >
              <span>⚡ Autonomous</span>
            </button>
            <button
              onClick={() => {
                setShowIntelligence(true);
                setShowAgenda(false);
                setShowBidsFlow(false);
                setShowBidsDashboard(false);
                setShowAdvisor(false);
                setShowAutonomous(false);
              }}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg transition font-medium ${
                showIntelligence ? 'bg-blue-500 hover:bg-blue-600' : 'bg-gray-700 hover:bg-gray-600'
              }`}
            >
              <span>Intelligence</span>
            </button>
            <button
              onClick={() => {
                setShowAdvisor(true);
                setShowAgenda(false);
                setShowBidsFlow(false);
                setShowBidsDashboard(false);
                setShowIntelligence(false);
                setShowAutonomous(false);
              }}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg transition font-medium ${
                showAdvisor ? 'bg-amber-500 hover:bg-amber-600' : 'bg-gray-700 hover:bg-gray-600'
              }`}
            >
              <span>Advisor</span>
            </button>
            <button
              onClick={() => {
                setShowBidsFlow(true);
                setShowAgenda(false);
                setShowBidsDashboard(false);
                setShowIntelligence(false);
                setShowAdvisor(false);
                setShowAutonomous(false);
              }}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg transition font-medium ${
                showBidsFlow ? 'bg-blue-500 hover:bg-blue-600' : 'bg-gray-700 hover:bg-gray-600'
              }`}
            >
              <span>Flow Mode</span>
            </button>
            <button
              onClick={() => {
                setShowBidsDashboard(true);
                setShowBidsFlow(false);
                setShowAgenda(false);
                setShowIntelligence(false);
                setShowAdvisor(false);
                setShowAutonomous(false);
              }}
              className={`flex items-center gap-2 px-3 py-2 rounded-lg transition text-sm ${
                showBidsDashboard ? 'bg-blue-500 hover:bg-blue-600' : 'bg-gray-700 hover:bg-gray-600'
              }`}
            >
              <span>Full Dashboard</span>
            </button>
          </div>
          <div className="text-sm text-gray-400">
            {showAgenda && 'What needs to be done'}
            {showAutonomous && 'AI that works while you sleep — self-learning, self-improving'}
            {showIntelligence && 'Three-avenue contract pipeline'}
            {showAdvisor && 'Learn while you build — growth tracking across all systems'}
            {showBidsFlow && 'One step at a time'}
            {showBidsDashboard && 'All bids overview'}
          </div>
        </div>
      )}

      {/* LANDING PAGE: Active panel + system cards always visible */}
      {currentView === 'landing' && (
        <>
          {/* Active workbench panel */}
          {showAgenda && (
            <div className="max-w-7xl mx-auto px-6 py-6">
              <AgendaDashboard />
            </div>
          )}
          {showIntelligence && (
            <div className="max-w-7xl mx-auto px-6 py-6">
              <ContractIntelligence />
            </div>
          )}
          {showAdvisor && (
            <div className="max-w-7xl mx-auto px-6 py-6">
              <NexusAdvisorPanel />
            </div>
          )}
          {showAutonomous && (
            <div className="max-w-7xl mx-auto px-6 py-6">
              <AutonomousPanel />
            </div>
          )}
          {showBidsFlow && <BidsFlow />}
          {showBidsDashboard && (
            <div className="max-w-7xl mx-auto px-6 py-6">
              <BidsDashboard />
            </div>
          )}

          {/* System cards — ALWAYS visible on landing page */}
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
