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
import { DeadlineNotifications } from './components/DeadlineNotifications';
import { AgendaDashboard } from './components/AgendaDashboard';
import { BidsDashboard } from './components/BidsDashboard';
import { BidsFlow } from './components/BidsFlow';

function App() {
  const [currentView, setCurrentView] = useState<ViewType>('landing');
  const [currentSystemTab, setCurrentSystemTab] = useState('dashboard');
  const [showAgenda, setShowAgenda] = useState(false);
  const [showBidsDashboard, setShowBidsDashboard] = useState(false);
  const [showBidsFlow, setShowBidsFlow] = useState(true); // Show flow by default

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
      default:
        return <LandingPage onEnterSystem={navigateToSystem} />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <Header currentView={currentView} onBackToNexus={navigateToLanding} />
      {currentView === 'landing' && <DeadlineNotifications />}
      
      {/* Simple Flow Toggle */}
      {currentView === 'landing' && (
        <div className="bg-gray-800 border-b border-gray-700 px-6 py-2 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <button
              onClick={() => {
                setShowBidsFlow(!showBidsFlow);
                if (!showBidsFlow) {
                  setShowBidsDashboard(false);
                  setShowAgenda(false);
                }
              }}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg transition font-medium ${
                showBidsFlow ? 'bg-blue-500 hover:bg-blue-600' : 'bg-gray-700 hover:bg-gray-600'
              }`}
            >
              <span>→</span>
              <span>Flow Mode</span>
            </button>
            <button
              onClick={() => {
                setShowBidsDashboard(!showBidsDashboard);
                if (!showBidsDashboard) setShowBidsFlow(false);
              }}
              className={`flex items-center gap-2 px-3 py-2 rounded-lg transition text-sm ${
                showBidsDashboard ? 'bg-gray-600' : 'bg-gray-700 hover:bg-gray-600'
              }`}
            >
              <span>📊</span>
              <span>Full Dashboard</span>
            </button>
          </div>
          <div className="text-sm text-gray-400">
            {showBidsFlow && 'One step at a time'}
          </div>
        </div>
      )}

      {/* Simple Flow Mode - One thing at a time */}
      {showBidsFlow && currentView === 'landing' && (
        <BidsFlow />
      )}

      {/* Full Dashboard - Only if explicitly requested */}
      {showBidsDashboard && currentView === 'landing' && !showBidsFlow && (
        <div className="max-w-7xl mx-auto px-6 py-6">
          <BidsDashboard />
        </div>
      )}

      {/* Agenda - Only if explicitly requested */}
      {showAgenda && !showBidsFlow && (
        <div className="max-w-7xl mx-auto px-6 py-6">
          <AgendaDashboard />
        </div>
      )}
      
      {!showBidsFlow && renderCurrentView()}
      <FloatingAICopilot />
    </div>
  );
}

export default App;
