import React from 'react';

export type ViewType = 'landing' | 'gpss' | 'ddcss' | 'atlas' | 'gbis' | 'vertex' | 'lbpc' | 'invoices' | 'documents' | 'quotes' | 'capstats' | 'compass' | 'prism' | 'agent-portal' | 'agent-login' | 'opportunity-hunter' | 'alexa' | 'jeta' | 'fleetflow-cape' | 'shield';

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
      case 'gbis': return '🎁 GBIS v1.0 - Grant Business Intelligence System';
      case 'vertex': return '💎 VERTEX v1.0 - Financial Command Center';
      case 'lbpc': return '💰 LBPC v1.0 - Lancaster Banques P.C.';
      case 'invoices': return '💰 NEXUS Invoices - Universal Invoicing System';
      case 'documents': return '📄 Document Generator - Quotes • Pricing • Proposals';
      case 'compass': return '🧭 COMPASS v1.0 - Post-Award Operations';
      case 'prism': return '🔮 PRISM v1.0 - Field Service Command Center';
      case 'agent-portal': return '🔮 PRISM Agent Portal';
      case 'opportunity-hunter': return '🌟 NOVA v1.0 - New Opportunity Vetting & Acquisition';
      case 'alexa': return '🎙️ ALEXA NEXUS - Voice Command Center';
      case 'jeta': return '⛽ JETA COURTIÈRE — Aviation Fuel Brokerage';
      case 'shield': return '🛡️ SHIELD v1.0 — Lead Screening & MDHHS Referral';
      default: return '🌐 NEXUS v1.0 - Master Control Center';
    }
  };

  const getSubtitle = () => {
    switch (currentView) {
      case 'gpss': return 'Pre-Award Pipeline • Mining • Proposals • EDWOSB Certified';
      case 'ddcss': return 'Blueprint Framework • 6 Sectors • AI Powered';
      case 'atlas': return 'RFP Response Center • Portfolio Tracking • Daily Operations';
      case 'gbis': return 'Grant Discovery • AI Applications • 8 Divisions • ROI Tracking';
      case 'vertex': return 'Invoices • Expenses • Revenue • Reports • AI Intelligence • QB/Gusto Export';
      case 'lbpc': return 'Surplus Recovery System • All 50 States • Automated Workflows';
      case 'invoices': return 'Government & Enterprise Compliant • All Systems • Real-Time Tracking';
      case 'documents': return 'Quotes • Capability Statements • Supplier RFPs • Pricing Engine';
      case 'compass': return 'Contract Fulfillment • Delivery Tracking • Payments • Compliance';
      case 'prism': return 'Dispatch • Orders • Scanbacks • Inspection • Field Agents • See Every Detail';
      case 'agent-portal': return 'My Orders • Scanbacks • Payments • Profile • Dee Davis Inc. Field Agent Network';
      case 'opportunity-hunter': return 'Live Federal Search • Quick Wins • Agency Intelligence • 3 Opportunities/Day Target';
      case 'alexa': return '98 Voice Commands • NEXUS Integration • Test Lab • All Systems Connected';
      case 'jeta': return 'Division of DEE DAVIS INC • Jet A / Jet A-1 • Mandates & Execution';
      case 'shield': return 'DDI + CWC • MI PA 146 of 2023 • Referral Intake • Navigator Dashboard • AI Assistant';
      default: return 'Enterprise Command • 6 Systems • AI Powered';
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
