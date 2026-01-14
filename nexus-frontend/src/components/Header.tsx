import React from 'react';

export type ViewType = 'landing' | 'gpss' | 'ddcss' | 'atlas' | 'lbpc' | 'invoices';

interface HeaderProps {
  currentView: ViewType;
  onBackToNexus: () => void;
}

const Header: React.FC<HeaderProps> = ({ currentView, onBackToNexus }) => {
  const getTitle = () => {
    switch (currentView) {
      case 'gpss': return '🎯 GPSS v1.0 - Government Prime Sales System';
      case 'ddcss': return '💼 DDCSS v1.0 - Corporate Sales System';
      case 'atlas': return '🌍 ATLAS PM v1.0 - Project Management System';
      case 'lbpc': return '💰 LBPC v1.0 - Lancaster Banques P.C.';
      case 'invoices': return '💰 NEXUS Invoices - Universal Invoicing System';
      default: return '🌐 NEXUS v1.0 - Master Control Center';
    }
  };

  const getSubtitle = () => {
    switch (currentView) {
      case 'gpss': return 'Government Contracting Command Center';
      case 'ddcss': return 'Blueprint Framework • 6 Sectors • AI Powered';
      case 'atlas': return 'RFP Response Center • Portfolio Tracking • Daily Operations';
      case 'lbpc': return 'Surplus Recovery System • All 50 States • Automated Workflows';
      case 'invoices': return 'Government & Enterprise Compliant • All Systems • Real-Time Tracking';
      default: return 'Enterprise Command • 4 Systems • AI Powered';
    }
  };

  return (
    <header className="bg-gray-800 border-b border-gray-700 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-6 py-4">
        <div className="flex justify-between items-center">
          <div className="flex items-center gap-4">
            {currentView !== 'landing' && (
              <button
                onClick={onBackToNexus}
                className="flex items-center gap-2 bg-gray-700 hover:bg-gray-600 px-4 py-2 rounded-lg font-semibold transition"
              >
                ← Back to NEXUS
              </button>
            )}
            <div>
              <h1 className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-600">
                {getTitle()}
              </h1>
              <p className="text-gray-400 text-sm">{getSubtitle()}</p>
            </div>
          </div>

          <div className="flex gap-4 items-center">
            {/* Google Custom Search */}
            <div className="gcse-search"></div>

            {/* System Status */}
            <div className="flex items-center gap-2 bg-green-500/20 px-3 py-1 rounded-lg text-sm">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse-custom"></div>
              <span className="text-green-400">System Active</span>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
