import React, { useState, useEffect, useRef } from 'react';

export type ViewType = 'landing' | 'gpss' | 'ddcss' | 'atlas' | 'gbis' | 'vertex' | 'lbpc' | 'invoices' | 'documents' | 'quotes' | 'capstats' | 'vault' | 'compass' | 'prism' | 'agent-portal' | 'agent-login' | 'opportunity-hunter' | 'alexa' | 'jeta' | 'fleetflow-cape' | 'shield' | 'calendar' | 'haven' | 'hr';

export type NexusRole = 'Ultimate Supervisor' | 'Supervisor' | 'Navigator' | 'Viewer';

export interface NexusIdentity {
  name: string;
  email: string;
  role: NexusRole;
}

const ROLE_PROFILES: Array<NexusIdentity & { desc: string }> = [
  { name: 'Dee Davis',       email: 'dee@deedavisinc.com',    role: 'Ultimate Supervisor', desc: 'Full access — approve, override, billing' },
  { name: 'Supervisor Demo', email: 'supervisor@cwcare.org',   role: 'Supervisor',          desc: 'Approve services & billing, SLA overrides' },
  { name: 'Navigator Demo',  email: 'navigator@cwcare.org',    role: 'Navigator',           desc: 'Case management, service requests' },
  { name: 'Viewer Demo',     email: 'viewer@cwcare.org',       role: 'Viewer',              desc: 'Read-only dashboard access' },
];

const ROLE_BADGE: Record<NexusRole, { bg: string; text: string; border: string }> = {
  'Ultimate Supervisor': { bg: 'bg-yellow-500/20', text: 'text-yellow-400', border: 'border-yellow-500/40' },
  'Supervisor':          { bg: 'bg-purple-500/20', text: 'text-purple-400', border: 'border-purple-500/40' },
  'Navigator':           { bg: 'bg-blue-500/20',   text: 'text-blue-400',   border: 'border-blue-500/40' },
  'Viewer':              { bg: 'bg-gray-500/20',   text: 'text-gray-400',   border: 'border-gray-500/40' },
};

const STORAGE_KEY = 'nexus_identity';

export function getNexusIdentity(): NexusIdentity {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) return JSON.parse(raw);
  } catch { /* ignore */ }
  return ROLE_PROFILES[0]; // Default: Dee Davis, Ultimate Supervisor
}

export function setNexusIdentity(identity: NexusIdentity): void {
  try { localStorage.setItem(STORAGE_KEY, JSON.stringify(identity)); } catch { /* ignore */ }
}

export function isNexusSupervisor(identity?: NexusIdentity | null): boolean {
  const role = (identity || getNexusIdentity()).role;
  return role === 'Ultimate Supervisor' || role === 'Supervisor';
}

export function isNexusUltimateSupervisor(identity?: NexusIdentity | null): boolean {
  return (identity || getNexusIdentity()).role === 'Ultimate Supervisor';
}

interface HeaderProps {
  currentView: ViewType;
  onBackToNexus: () => void;
  identity?: NexusIdentity;
  onIdentityChange?: (identity: NexusIdentity) => void;
}

const Header: React.FC<HeaderProps> = ({ currentView, onBackToNexus, identity, onIdentityChange }) => {
  const resolvedIdentity = identity || getNexusIdentity();
  const badge = ROLE_BADGE[resolvedIdentity.role];
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const dropRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (dropRef.current && !dropRef.current.contains(e.target as Node)) setDropdownOpen(false);
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const switchRole = (profile: NexusIdentity) => {
    setNexusIdentity(profile);
    onIdentityChange?.(profile);
    setDropdownOpen(false);
  };
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
      case 'vault': return '🔐 VAULT v1.0 - Master Contract Registry';
      case 'prism': return '🔮 PRISM v1.0 - Field Service Command Center';
      case 'agent-portal': return '🔮 PRISM Agent Portal';
      case 'opportunity-hunter': return '🌟 NOVA v1.0 - New Opportunity Vetting & Acquisition';
      case 'alexa': return '🎙️ ALEXA NEXUS - Voice Command Center';
      case 'jeta': return '⛽ JETA COURTIÈRE — Aviation Fuel Brokerage';
      case 'shield': return '🛡️ SHIELD v1.0 — Lead Screening & MDHHS Referral';
      case 'haven': return '🏠 HAVEN v1.0 — Disaster Response TPA';
      case 'hr': return '🔑 GATEWAY v1.0 — Employee & Contractor Onboarding';
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
      case 'vault': return 'Service · Vendor · Government · Commercial — agreements & IDs; money in VERTEX';
      case 'prism': return 'Dispatch • Orders • Scanbacks • Inspection • Field Agents • See Every Detail';
      case 'agent-portal': return 'My Orders • Scanbacks • Payments • Profile • DDI Field Agent Network';
      case 'opportunity-hunter': return 'Live Federal Search • Quick Wins • Agency Intelligence • 3 Opportunities/Day Target';
      case 'alexa': return '98 Voice Commands • NEXUS Integration • Test Lab • All Systems Connected';
      case 'jeta': return 'Division of DEE DAVIS INC • Jet A / Jet A-1 • Mandates & Execution';
      case 'shield': return 'DDI + CWC • MI PA 146 of 2023 • Referral Intake • Navigator Dashboard • AI Assistant';
      case 'haven': return 'Housing • Transport • Medical Continuity • FL · TX · LA · MI • MCO Pipeline';
      case 'hr': return 'Pre-Boarding → Day 1 → Week 1 → 30/60/90 Day • CMS FDR Training • OIG/SAM Exclusion Screening • gateway.deedavis.biz Self-Service Portal • All Divisions';
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

            {/* Role Switcher */}
            <div className="relative" ref={dropRef}>
              <button
                onClick={() => setDropdownOpen(!dropdownOpen)}
                className={`flex items-center gap-2 ${badge.bg} border ${badge.border} px-3 py-1.5 rounded-lg text-sm cursor-pointer hover:brightness-125 transition-all`}
              >
                <div className="text-left">
                  <div className={`text-xs font-bold ${badge.text} leading-tight`}>{resolvedIdentity.name}</div>
                  <div className={`text-[10px] ${badge.text} opacity-70 leading-tight`}>{resolvedIdentity.role}</div>
                </div>
                <svg className={`w-3 h-3 ${badge.text} transition-transform ${dropdownOpen ? 'rotate-180' : ''}`} fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M19 9l-7 7-7-7"/></svg>
              </button>

              {dropdownOpen && (
                <div className="absolute right-0 top-full mt-2 w-72 bg-gray-800 border border-gray-600 rounded-xl shadow-2xl z-[999] overflow-hidden">
                  <div className="px-4 py-2.5 border-b border-gray-700">
                    <div className="text-[10px] uppercase tracking-widest text-gray-400 font-bold">Switch Role</div>
                  </div>
                  {ROLE_PROFILES.map((profile) => {
                    const rb = ROLE_BADGE[profile.role];
                    const isActive = resolvedIdentity.role === profile.role && resolvedIdentity.email === profile.email;
                    return (
                      <button
                        key={profile.email}
                        onClick={() => switchRole(profile)}
                        className={`w-full text-left px-4 py-3 flex items-center gap-3 transition-all ${
                          isActive ? 'bg-gray-700/60' : 'hover:bg-gray-700/40'
                        }`}
                      >
                        <div className={`w-8 h-8 rounded-lg ${rb.bg} border ${rb.border} flex items-center justify-center text-xs font-black ${rb.text}`}>
                          {profile.name.charAt(0)}
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2">
                            <span className="text-sm text-white font-semibold">{profile.name}</span>
                            <span className={`text-[9px] px-1.5 py-0.5 rounded ${rb.bg} ${rb.text} border ${rb.border} font-bold`}>
                              {profile.role.toUpperCase()}
                            </span>
                          </div>
                          <div className="text-[10px] text-gray-400 truncate">{profile.desc}</div>
                        </div>
                        {isActive && (
                          <div className="w-2 h-2 rounded-full bg-green-400"></div>
                        )}
                      </button>
                    );
                  })}
                </div>
              )}
            </div>

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
