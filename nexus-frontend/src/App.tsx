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

function App() {
  const [currentView, setCurrentView] = useState<ViewType>('landing');
  const [currentSystemTab, setCurrentSystemTab] = useState('dashboard');

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
      default:
        return <LandingPage onEnterSystem={navigateToSystem} />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <Header currentView={currentView} onBackToNexus={navigateToLanding} />
      {renderCurrentView()}
      <FloatingAICopilot />
    </div>
  );
}

export default App;
