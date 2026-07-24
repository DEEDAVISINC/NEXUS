import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { api } from '../../api/client';
import PartnerWebview from '../PartnerWebview';
import TPADivisionWorkspace, { mapPrismApiOrderToWorkspace, mapPrismApiClientToWorkspace, DivisionScanback } from '../prism/TPADivisionWorkspace';
import PRISMHub, { HubScheduleItem } from '../prism/PRISMHub';
import { countDivisionNotifications } from '../prism/prismDivisionAlerts';
import type { PrismNotification } from '../prism/PrismOpsFeed';

// Check if we're running in Electron
const isElectron = () => {
  return typeof window !== 'undefined' && 
         (window as any).electronAPI?.isElectron === true;
};

interface PRISMSystemProps {
  onBackToNexus: () => void;
  onNavigate?: (view: any, tab?: string) => void;
  activeTab: string;
  setActiveTab: (tab: string) => void;
  initialDivision?: string;
  initialDivisionSection?: string;
  onDeepLinkConsumed?: () => void;
}

// ─── SERVICE TYPE COLORS ───────────────────────────────────────────
// `color` = accent for tints/borders/text on dark bg
// `solid` = darker shade used as badge/pill background with white text
const SERVICE_COLORS: Record<string, { color: string; solid: string; bg: string; label: string; icon: string; border: string }> = {
  'dot':             { color: '#EF4444', solid: '#DC2626', bg: '#FEF2F2', label: 'Drug Test (DOT)',     icon: '🔴', border: '#F87171' },
  'non-dot':         { color: '#EF4444', solid: '#DC2626', bg: '#FEF2F2', label: 'Drug Test (Non-DOT)', icon: '🔴', border: '#F87171' },
  'dna':             { color: '#A855F7', solid: '#7C3AED', bg: '#FAF5FF', label: 'DNA Collection',      icon: '🟣', border: '#C084FC' },
  'fingerprint':     { color: '#4ADE80', solid: '#16A34A', bg: '#F0FDF4', label: 'Fingerprinting/EFT',  icon: '🟢', border: '#86EFAC' },
  'background':      { color: '#4ADE80', solid: '#16A34A', bg: '#F0FDF4', label: 'Background Check',    icon: '🟢', border: '#86EFAC' },
  'notary':          { color: '#EC4899', solid: '#DB2777', bg: '#FDF2F8', label: 'Notary',              icon: '🩷', border: '#F472B6' },
  'ron':             { color: '#EC4899', solid: '#DB2777', bg: '#FDF2F8', label: 'Notary (RON)',        icon: '🩷', border: '#F472B6' },
  'apostille':       { color: '#EC4899', solid: '#DB2777', bg: '#FDF2F8', label: 'Apostille',           icon: '🩷', border: '#F472B6' },
  'process':         { color: '#EC4899', solid: '#DB2777', bg: '#FDF2F8', label: 'Process Serving',     icon: '🩷', border: '#F472B6' },
  'nemt':            { color: '#14B8A6', solid: '#0D9488', bg: '#F0FDFA', label: 'NEMT / Transport',    icon: '🟢', border: '#2DD4BF' },
  'community_transition': { color: '#F59E0B', solid: '#D97706', bg: '#FFFBEB', label: 'Community Transition (CTS)', icon: '🏠', border: '#FCD34D' },
  'medical_courier': { color: '#6366F1', solid: '#4F46E5', bg: '#EEF2FF', label: 'Medical Courier',     icon: '🟣', border: '#818CF8' },
  'courier':         { color: '#6366F1', solid: '#4F46E5', bg: '#EEF2FF', label: 'Courier/Runner',      icon: '🟣', border: '#818CF8' },
  'rx_delivery':     { color: '#14B8A6', solid: '#0D9488', bg: '#F0FDFA', label: 'Rx Delivery',         icon: '💊', border: '#2DD4BF' },
  'phlebotomy':      { color: '#EF4444', solid: '#DC2626', bg: '#FEF2F2', label: 'Occ Health',          icon: '🔴', border: '#F87171' },
};

const SERVICE_GROUPS: { id: string; label: string; icon: string; types: string[]; color: string; solid: string }[] = [
  { id: 'drug_testing',   label: 'Drug Testing',        icon: '🔴', types: ['dot', 'non-dot', 'phlebotomy'], color: '#EF4444', solid: '#DC2626' },
  { id: 'dna',            label: 'DNA Collection',       icon: '🟣', types: ['dna'],                         color: '#A855F7', solid: '#7C3AED' },
  { id: 'fingerprint',    label: 'Fingerprint / BG',     icon: '🟢', types: ['fingerprint', 'background'],   color: '#4ADE80', solid: '#16A34A' },
  { id: 'notary_legal',   label: 'Notary & Legal',       icon: '🩷', types: ['notary', 'ron', 'apostille', 'process'], color: '#EC4899', solid: '#DB2777' },
  { id: 'nemt',           label: 'NEMT / Transport',     icon: '🚐', types: ['nemt', 'rx_delivery'],          color: '#14B8A6', solid: '#0D9488' },
  { id: 'community_transition', label: 'Community Transition (CTS)', icon: '🏠', types: ['community_transition', 'cts'], color: '#F59E0B', solid: '#D97706' },
  { id: 'courier',        label: 'Courier / Delivery',   icon: '📦', types: ['medical_courier', 'courier'],  color: '#6366F1', solid: '#4F46E5' },
];

// ─── PARTNER PORTALS (Direct Login Links for Each TPA Sector) ────
interface PartnerPortal {
  id: string;
  name: string;
  url: string;
  icon: string;
  description: string;
  loginType: 'dashboard' | 'portal' | 'api' | 'phone';
  credentials?: string;
  status: 'active' | 'pending' | 'api_only';
}

const PARTNER_PORTALS: Record<string, PartnerPortal[]> = {
  drug_testing: [
    { id: 'quest', name: 'Quest Diagnostics', url: 'https://employer.questdiagnostics.com', icon: '🧪', description: 'Lab results, scheduling, chain of custody', loginType: 'portal', status: 'active' },
    { id: 'amro', name: 'AMRO (MRO Services)', url: 'https://amro.com', icon: '👨‍⚕️', description: 'MRO review status, result verification', loginType: 'portal', status: 'active' },
    { id: 'clearinghouse', name: 'FMCSA Clearinghouse', url: 'https://clearinghouse.fmcsa.dot.gov', icon: '🚛', description: 'DOT queries, violations, reporting', loginType: 'dashboard', status: 'active' },
    { id: 'escreen', name: 'eScreen Network', url: 'https://escreen.com', icon: '📍', description: 'Collection site network, scheduling', loginType: 'portal', status: 'active' },
  ],
  dna_testing: [
    { id: 'ddc', name: 'DNA Diagnostics Center', url: 'https://dnacenter.com/professional', icon: '🧬', description: 'Case management, kit orders, results', loginType: 'portal', status: 'active' },
  ],
  fingerprint_bg: [
    { id: 'ncs', name: 'National Crime Search', url: 'https://nationalcrimesearch.com', icon: '🔍', description: 'Background checks, drug screening, verifications', loginType: 'portal', status: 'active' },
    { id: 'fieldprint', name: 'FieldPrint (if contracted)', url: 'https://fieldprintfbi.com', icon: '🖐️', description: 'FBI channeling, livescan management', loginType: 'portal', status: 'pending' },
  ],
  notary_legal: [
    { id: 'zigsig', name: 'ZigSig RON Platform', url: 'https://zigsig.com', icon: '✍️', description: 'Remote Online Notarization sessions', loginType: 'dashboard', status: 'active' },
    { id: 'notarize', name: 'Notarize.com', url: 'https://app.notarize.com', icon: '📄', description: 'Additional RON platform', loginType: 'dashboard', status: 'pending' },
  ],
  transport: [
    {
      id: 'hap_caresource',
      name: 'HAP CareSource Portal',
      url: 'https://providerportal.caresource.com/MI/User/Login.aspx?ReturnUrl=%2fMI%2fLogout.aspx',
      icon: '🏥',
      description: 'MI login — eligibility, claims, prior auth (Vendor 100000469269)',
      loginType: 'portal',
      status: 'active',
      credentials: 'Provider portal login set up May 6, 2026 · Support 1-833-230-2102',
    },
    {
      id: 'hap_provider_resources',
      name: 'HAP Provider Resources',
      url: 'https://www.hap.org/providers',
      icon: '📋',
      description: 'HAP network hub — forms, prior auth policies, portal link',
      loginType: 'portal',
      status: 'active',
    },
    { id: 'uber_health', name: 'Uber Health', url: 'https://health.uber.com', icon: '🚗', description: 'NEMT rides, WAV transport', loginType: 'dashboard', status: 'active', credentials: 'Dashboard live since May 15, 2026' },
    { id: 'uber_business', name: 'Uber Business Portal', url: 'https://business.uber.com', icon: '💼', description: 'Admin, reporting, expense management', loginType: 'portal', status: 'active' },
    { id: 'lyft_health', name: 'Lyft Healthcare', url: 'https://www.lyft.com/healthcare', icon: '🩷', description: 'NEMT, Lyft Assisted (door-to-door), Medicaid in 21 states. WAV via consumer app only.', loginType: 'dashboard', status: 'active', credentials: 'Account created — awaiting AE sales call' },
  ],
  pharmacy_courier: [
    { id: 'uber_health_rx', name: 'Uber Health (Rx)', url: 'https://health.uber.com', icon: '💊', description: 'Pharmacy delivery, same-day Rx', loginType: 'dashboard', status: 'active' },
    { id: 'roadie', name: 'Roadie', url: 'https://business.roadie.com', icon: '🚙', description: 'Same-day Rx delivery, last-mile logistics', loginType: 'dashboard', status: 'active' },
    { id: 'doordash_drive', name: 'DoorDash Drive', url: 'https://drive.doordash.com', icon: '📦', description: 'Pharmacy fulfillment, item delivery', loginType: 'portal', status: 'pending' },
    { id: 'scriptdrop', name: 'ScriptDrop', url: 'https://scriptdrop.co', icon: '💉', description: 'Pharmacy delivery network', loginType: 'portal', status: 'pending' },
  ],
  medical_courier: [
    { id: 'uber_health_med', name: 'Uber Health', url: 'https://health.uber.com', icon: '🏥', description: 'Medical courier, specimen transport', loginType: 'dashboard', status: 'active' },
    { id: 'stat_courier', name: 'STAT Network', url: 'https://statcourier.com', icon: '⚡', description: 'STAT lab runs, urgent specimens', loginType: 'portal', status: 'pending' },
  ],
  legal_courier: [
    { id: 'abc_legal', name: 'ABC Legal', url: 'https://abclegal.com', icon: '⚖️', description: 'Court filings, process serving', loginType: 'portal', status: 'pending' },
    { id: 'file_thru', name: 'File & ServeXpress', url: 'https://fileandservexpress.com', icon: '📁', description: 'E-filing, court services', loginType: 'portal', status: 'pending' },
  ],
  field_ops: [
    { id: 'ivueit', name: 'iVueit', url: 'https://ivueit.com', icon: '📱', description: 'Property inspections, field tasks', loginType: 'portal', status: 'active' },
    { id: 'csfield', name: 'CS Field Services', url: 'https://csfield.com', icon: '🏠', description: 'REO, preservation dispatch', loginType: 'portal', status: 'pending' },
  ],
  logistics: [
    { id: 'dat', name: 'DAT Load Board', url: 'https://one.dat.com', icon: '🚚', description: 'Load matching, carrier network', loginType: 'portal', status: 'pending' },
    { id: 'truckstop', name: 'Truckstop.com', url: 'https://truckstop.com', icon: '📦', description: 'Load board, rate data', loginType: 'portal', status: 'pending' },
  ],
  background: [
    { id: 'ncs_bg', name: 'NCS Portal', url: 'https://nationalcrimesearch.com', icon: '🔐', description: 'Full background suite, verifications', loginType: 'portal', status: 'active' },
  ],
  credentialing: [
    { id: 'caqh', name: 'CAQH ProView', url: 'https://proview.caqh.org', icon: '🏥', description: 'Provider credentialing database', loginType: 'portal', status: 'pending' },
    { id: 'npdb', name: 'NPDB', url: 'https://npdb.hrsa.gov', icon: '📋', description: 'National Practitioner Data Bank queries', loginType: 'portal', status: 'pending' },
  ],
  workforce: [
    { id: 'everify', name: 'E-Verify', url: 'https://everify.gov', icon: '✅', description: 'Work authorization verification', loginType: 'dashboard', status: 'active' },
    { id: 'clearinghouse2', name: 'FMCSA Clearinghouse', url: 'https://clearinghouse.fmcsa.dot.gov', icon: '🚛', description: 'Fleet compliance, DOT queries', loginType: 'dashboard', status: 'active' },
  ],
};

// ─── PRISM DIVISIONS ─────────────────────────────────────────────
interface PrismDivision {
  id: string;
  name: string;
  subtitle: string;
  icon: string;
  color: string;
  solid: string;
  gradient: string;
  types: string[];
  agentSpecialties: string[];
  portalKey: string;
  revenueTarget: string;
  status: 'active' | 'building';
}

const PRISM_DIVISIONS: PrismDivision[] = [
  {
    id: 'drug_testing',
    name: 'Drug Testing & Occ Health',
    subtitle: 'DOT • Non-DOT • BAT • Random Pools • Mass Events • Clearinghouse',
    icon: '🧪',
    color: '#EF4444',
    solid: '#DC2626',
    gradient: 'from-red-600 to-red-800',
    types: ['dot', 'non-dot', 'phlebotomy'],
    agentSpecialties: ['Collection Agent', 'BAT', 'Phlebotomist'],
    portalKey: 'drug_testing',
    revenueTarget: '$500K–$2M',
    status: 'active',
  },
  {
    id: 'dna_testing',
    name: 'DNA / Genetic Testing',
    subtitle: 'DePointe DNA • Legal • Immigration • Paternity • Informational',
    icon: '🧬',
    color: '#A855F7',
    solid: '#7C3AED',
    gradient: 'from-purple-600 to-purple-800',
    types: ['dna'],
    agentSpecialties: ['Collection Agent', 'DNA Collector'],
    portalKey: 'dna_testing',
    revenueTarget: '$200K–$750K',
    status: 'active',
  },
  {
    id: 'fingerprint_bg',
    name: 'Fingerprinting & Background',
    subtitle: 'LiveScan • FD-258 Ink Cards • EFT • NCS Background Checks',
    icon: '🖐️',
    color: '#4ADE80',
    solid: '#16A34A',
    gradient: 'from-green-600 to-green-800',
    types: ['fingerprint', 'background'],
    agentSpecialties: ['Print Technician', 'Background Specialist'],
    portalKey: 'fingerprint_bg',
    revenueTarget: '$550K–$2M',
    status: 'active',
  },
  {
    id: 'notary_legal',
    name: 'Notary & Legal Services',
    subtitle: '3D Ink Signatures • Loan Signing • RON • Apostille • CNTDA • Process Serving',
    icon: '✍️',
    color: '#EC4899',
    solid: '#DB2777',
    gradient: 'from-pink-600 to-pink-800',
    types: ['notary', 'ron', 'apostille', 'process'],
    agentSpecialties: ['Signing Agent', 'Notary', 'Process Server'],
    portalKey: 'notary_legal',
    revenueTarget: '$200K–$500K',
    status: 'active',
  },
  {
    id: 'transport',
    name: 'NEMT & Medical Transport',
    subtitle: 'HAP CareSource NEMT • WAV • Uber Health • Claims & Eligibility',
    icon: '🚐',
    color: '#14B8A6',
    solid: '#0D9488',
    gradient: 'from-teal-600 to-teal-800',
    types: ['nemt'],
    agentSpecialties: ['NEMT Driver', 'WAV Driver', 'Stretcher Transport'],
    portalKey: 'transport',
    revenueTarget: '$2M–$10M',
    status: 'active',
  },
  {
        id: 'community_transition',
        name: 'Community Transition (CTS)',
        subtitle: 'MCO/Medicaid LTSS • Nursing Facility → Community • PCSP • Home Assessment • Authorization Cases (live: Molina)',
    icon: '🔑',
    color: '#EAB308',
    solid: '#CA8A04',
    gradient: 'from-yellow-600 to-yellow-800',
    types: ['community_transition', 'cts'],
    agentSpecialties: ['CTS Case Coordinator'],
    portalKey: 'community_transition',
    revenueTarget: '$25K–$100K',
    status: 'active',
  },
  {
    id: 'pharmacy_courier',
    name: 'Pharmacy & Rx Delivery',
    subtitle: 'Pharmacy Delivery • Controlled Substances • Same-Day Rx • Lab Specimens',
    icon: '💊',
    color: '#10B981',
    solid: '#059669',
    gradient: 'from-emerald-600 to-emerald-800',
    types: ['rx_delivery'],
    agentSpecialties: ['Rx Courier', 'Controlled Substance Driver', 'Lab Courier'],
    portalKey: 'pharmacy_courier',
    revenueTarget: '$500K–$2M',
    status: 'active',
  },
  {
    id: 'medical_courier',
    name: 'Medical & Lab Courier',
    subtitle: 'Specimen Transport • Medical Records • Equipment Delivery • STAT Runs',
    icon: '🧫',
    color: '#6366F1',
    solid: '#4F46E5',
    gradient: 'from-indigo-600 to-indigo-800',
    types: ['medical_courier'],
    agentSpecialties: ['Medical Courier', 'Lab Courier', 'STAT Driver'],
    portalKey: 'medical_courier',
    revenueTarget: '$300K–$1M',
    status: 'active',
  },
  {
    id: 'legal_courier',
    name: 'Legal & Document Courier',
    subtitle: 'Court Filings • Legal Documents • Time-Sensitive Delivery • Chain of Custody',
    icon: '📜',
    color: '#78716C',
    solid: '#57534E',
    gradient: 'from-stone-600 to-stone-800',
    types: ['courier'],
    agentSpecialties: ['Legal Courier', 'Document Runner', 'Court Filing Specialist'],
    portalKey: 'legal_courier',
    revenueTarget: '$200K–$500K',
    status: 'active',
  },
  {
    id: 'field_ops',
    name: 'Field Ops',
    subtitle: 'REO • Property Preservation • Inspections • HUD FSM',
    icon: '🏠',
    color: '#3B82F6',
    solid: '#2563EB',
    gradient: 'from-blue-600 to-blue-800',
    types: [],
    agentSpecialties: ['Field Inspector', 'Preservation Tech'],
    portalKey: 'field_ops',
    revenueTarget: '$300K–$1M',
    status: 'active',
  },
  {
    id: 'logistics',
    name: 'Logistics & Fleet (Freight 1st)',
    subtitle: 'Freight Brokerage • Government Courier • Last-Mile • Fleet Dispatch',
    icon: '🚚',
    color: '#F59E0B',
    solid: '#D97706',
    gradient: 'from-amber-600 to-amber-800',
    types: ['courier'],
    agentSpecialties: ['Driver', 'Logistics Coordinator'],
    portalKey: 'logistics',
    revenueTarget: '$500K–$2M',
    status: 'active',
  },
  {
    id: 'credentialing',
    name: 'Medical Credentialing',
    subtitle: 'Provider Licensing • CAQH • NPDB • Hospital Privileging',
    icon: '🏥',
    color: '#06B6D4',
    solid: '#0891B2',
    gradient: 'from-cyan-600 to-cyan-800',
    types: [],
    agentSpecialties: ['Credentialing Specialist'],
    portalKey: 'credentialing',
    revenueTarget: '$500K–$3M',
    status: 'building',
  },
  {
    id: 'workforce',
    name: 'Workforce Compliance',
    subtitle: 'DOT DQ Files • I-9/E-Verify • Occ Health • Fleet Compliance',
    icon: '👷',
    color: '#8B5CF6',
    solid: '#7C3AED',
    gradient: 'from-violet-600 to-violet-800',
    types: ['phlebotomy'],
    agentSpecialties: ['Compliance Admin', 'Fleet Manager'],
    portalKey: 'workforce',
    revenueTarget: '$750K–$4M',
    status: 'building',
  },
];

// ─── COMPACT TPA DIVISION ROW (Minimal accordion style) ─────────────
const TPADivisionRow: React.FC<{
  division: PrismDivision;
  isExpanded: boolean;
  onToggle: () => void;
  onEnterDivision: () => void;
  orderCount: number;
  onOpenPortal: (portal: PartnerPortal, division: PrismDivision) => void;
}> = ({ division, isExpanded, onToggle, onEnterDivision, orderCount, onOpenPortal }) => {
  const portals = PARTNER_PORTALS[division.portalKey] || [];
  const activePortals = portals.filter(p => p.status === 'active');

  return (
    <div className={`border-b border-gray-700/50 ${isExpanded ? 'bg-gray-800/30' : ''}`}>
      {/* Compact Row - Always visible */}
      <button
        onClick={onToggle}
        className="w-full flex items-center gap-3 px-4 py-3 hover:bg-gray-800/50 transition text-left"
      >
        <span className="text-xl w-8 text-center">{division.icon}</span>
        <span className="font-semibold text-sm flex-1" style={{ color: division.color }}>{division.name}</span>
        {division.status === 'building' && (
          <span className="px-1.5 py-0.5 rounded text-[9px] font-bold bg-yellow-500/20 text-yellow-400">BUILD</span>
        )}
        {orderCount > 0 && (
          <span className="px-2 py-0.5 rounded-full text-xs font-bold" style={{ backgroundColor: `${division.color}30`, color: division.color }}>
            {orderCount}
          </span>
        )}
        <span className="text-gray-500 text-sm">{isExpanded ? '▲' : '▼'}</span>
      </button>

      {/* Expanded Content - Compact */}
      {isExpanded && (
        <div className="px-4 pb-4 pt-2 ml-11 border-l-2" style={{ borderColor: division.color }}>
          <p className="text-xs text-gray-500 mb-3">{division.subtitle}</p>
          
          {/* Partner Links - Open in Webview (Electron) or New Tab (Browser) */}
          {activePortals.length > 0 && (
            <div className="flex flex-wrap gap-2 mb-3">
              {activePortals.map(portal => (
                <button
                  key={portal.id}
                  onClick={(e) => { 
                    e.stopPropagation(); 
                    onOpenPortal(portal, division);
                  }}
                  className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-xs font-medium bg-gray-700 hover:bg-gray-600 transition"
                >
                  <span>{portal.icon}</span>
                  <span>{portal.name}</span>
                  {isElectron() ? (
                    <span className="text-green-400 text-[10px]">●</span>
                  ) : (
                    <span className="text-gray-500">↗</span>
                  )}
                </button>
              ))}
            </div>
          )}
          
          {/* Enter Button */}
          <button
            onClick={(e) => { e.stopPropagation(); onEnterDivision(); }}
            className="px-3 py-1.5 rounded-lg text-xs font-semibold text-white transition hover:opacity-90"
            style={{ backgroundColor: division.solid }}
          >
            Open Workspace →
          </button>
        </div>
      )}
    </div>
  );
};

// ─── SERVICE-SPECIFIC INSPECTION FUNDAMENTALS ─────────────────────
const SERVICE_INSPECTION: Record<string, { title: string; certs: string[]; fundamentals: { id: string; check: string; severity: string }[]; fatalFlaws: string[]; commonErrors: string[] }> = {
  'dot': {
    title: 'DOT Drug & Alcohol Testing',
    certs: ['49 CFR §40.33 Initial Collector Training', '5 Consecutive Error-Free Mock Collections', 'Proficiency Demonstration (§40.31)', 'Refresher Training Every 5 Years', 'Error Correction Training After Any Collection Error'],
    fundamentals: [
      { id: 'DOT-1', check: 'Collector signature on CCF?', severity: 'FATAL' },
      { id: 'DOT-2', check: 'Donor signature on CCF (or documented refusal)?', severity: 'FATAL' },
      { id: 'DOT-3', check: 'Specimen ID matches bottle and CCF?', severity: 'FATAL' },
      { id: 'DOT-4', check: 'Tamper-evident seal intact?', severity: 'FATAL' },
      { id: 'DOT-5', check: 'Sufficient volume (≥45 mL urine)?', severity: 'FATAL' },
      { id: 'DOT-6', check: 'Collector name printed and identifiable?', severity: 'FATAL' },
      { id: 'DOT-7', check: 'Temperature recorded within 4 min (90-100°F)?', severity: 'CRITICAL' },
      { id: 'DOT-8', check: 'Specimen split correctly (30 mL primary, 15 mL split)?', severity: 'CRITICAL' },
      { id: 'DOT-9', check: 'Donor identity verified with photo ID?', severity: 'CRITICAL' },
      { id: 'DOT-10', check: 'Shipped to SAMHSA-certified lab?', severity: 'CRITICAL' },
    ],
    fatalFlaws: ['No collector signature → CANCEL TEST', 'No donor signature (no refusal doc) → CANCEL TEST', 'Specimen ID mismatch → CANCEL TEST', 'Broken seal → CANCEL TEST', 'Insufficient volume → CANCEL TEST', 'Collector unidentifiable → CANCEL TEST'],
    commonErrors: ['Missing collector/donor signature', 'Specimen ID mismatch', 'Temperature out of range', 'Broken seal', 'Insufficient volume', 'Missing temp on CCF'],
  },
  'non-dot': {
    title: 'Non-DOT Drug Testing',
    certs: ['Drug & Alcohol Testing Collector Training', 'Chain of Custody Procedures', 'Specimen Handling & Shipping'],
    fundamentals: [
      { id: 'NDT-1', check: 'Collector signature on chain of custody?', severity: 'FATAL' },
      { id: 'NDT-2', check: 'Donor signature on chain of custody?', severity: 'FATAL' },
      { id: 'NDT-3', check: 'Specimen ID matches bottle and form?', severity: 'FATAL' },
      { id: 'NDT-4', check: 'Seal intact on specimen?', severity: 'FATAL' },
      { id: 'NDT-5', check: 'Sufficient specimen volume?', severity: 'CRITICAL' },
      { id: 'NDT-6', check: 'Correct panel type documented?', severity: 'CRITICAL' },
      { id: 'NDT-7', check: 'Donor identity verified?', severity: 'CRITICAL' },
    ],
    fatalFlaws: ['No collector signature → RECOLLECT', 'Specimen ID mismatch → RECOLLECT', 'Broken seal → RECOLLECT'],
    commonErrors: ['Wrong panel type ordered', 'Missing signatures', 'Insufficient volume'],
  },
  'dna': {
    title: 'DNA / Paternity Collection',
    certs: ['AABB Chain of Custody Training (legal collections)', 'Buccal Swab Collection Technique', 'Identity Verification & Photography'],
    fundamentals: [
      { id: 'DNA-1', check: 'Collector signature on chain of custody?', severity: 'FATAL' },
      { id: 'DNA-2', check: 'All participant signatures on consent/COC?', severity: 'FATAL' },
      { id: 'DNA-3', check: 'Tamper-evident seal intact?', severity: 'FATAL' },
      { id: 'DNA-4', check: 'Samples in PAPER envelope (never plastic)?', severity: 'FATAL' },
      { id: 'DNA-5', check: 'Envelopes labeled DURING collection (no pre-labeling)?', severity: 'FATAL' },
      { id: 'DNA-6', check: 'Government photo ID verified for all participants?', severity: 'FATAL' },
      { id: 'DNA-7', check: 'Photographs taken of all participants?', severity: 'FATAL' },
      { id: 'DNA-8', check: 'Collection observed by collector?', severity: 'FATAL' },
      { id: 'DNA-9', check: 'Samples remained in collector possession until shipped?', severity: 'FATAL' },
      { id: 'DNA-10', check: 'Gloves changed between participants?', severity: 'CRITICAL' },
    ],
    fatalFlaws: ['No collector signature → RECOLLECT', 'No participant signatures → RECOLLECT', 'Broken seal → RECOLLECT', 'Samples in plastic → RECOLLECT', 'Pre-labeled envelopes → RECOLLECT', 'No photo ID verification → RECOLLECT', 'No photographs → RECOLLECT', 'Collector related to participant → RECOLLECT', 'Samples left with participant → RECOLLECT', 'Collection not observed → RECOLLECT'],
    commonErrors: ['Plastic containers used', 'Pre-labeled envelopes', 'Missing photographs', 'Unobserved collection', 'Samples left with participant'],
  },
  'fingerprint': {
    title: 'Fingerprinting & Background',
    certs: ['LiveScan & FD-258 capture', 'Channel per client program rules', 'Livescan equipment training'],
    fundamentals: [
      { id: 'FP-1', check: 'Government photo ID verified (current, not expired)?', severity: 'FATAL' },
      { id: 'FP-2', check: 'Correct ORI code entered?', severity: 'FATAL' },
      { id: 'FP-3', check: 'All 10 fingers captured or properly documented (AMP/XX)?', severity: 'FATAL' },
      { id: 'FP-4', check: 'NFIQ quality score 3 or better on all prints?', severity: 'CRITICAL' },
      { id: 'FP-5', check: 'Name entered exactly as on government ID?', severity: 'CRITICAL' },
      { id: 'FP-6', check: 'Collector signed FD-258 (ink card only)?', severity: 'CRITICAL' },
      { id: 'FP-7', check: 'Receipt provided with TCN, date, ORI, turnaround?', severity: 'STANDARD' },
    ],
    fatalFlaws: ['Wrong ORI → results sent to wrong agency', 'Name mismatch → rejection', 'NFIQ below 3 → rejection', 'Missing fingers not documented → incomplete set', 'Invalid/expired ID → rejection'],
    commonErrors: ['Wrong ORI code', 'Name mismatch with records', 'Low quality (dry fingers)', 'Smudged prints', 'Excessive pressure', 'Incomplete capture'],
  },
  'notary': {
    title: 'Notary / RON / Apostille',
    certs: ['Active State Notary Commission', 'E&O Insurance (current)', 'RON Certification (if applicable)', 'NNA Certified Signing Agent (preferred)'],
    fundamentals: [
      { id: 'NOT-1', check: 'Signer personally present (in-person or RON)?', severity: 'FATAL' },
      { id: 'NOT-2', check: 'Signer identity verified with acceptable ID?', severity: 'FATAL' },
      { id: 'NOT-3', check: 'Notary commission current (not expired)?', severity: 'FATAL' },
      { id: 'NOT-4', check: 'Acting within correct jurisdiction?', severity: 'FATAL' },
      { id: 'NOT-5', check: 'Notarial certificate complete (all fields)?', severity: 'CRITICAL' },
      { id: 'NOT-6', check: 'Notary seal/stamp applied?', severity: 'CRITICAL' },
      { id: 'NOT-7', check: 'All required signatures present?', severity: 'CRITICAL' },
      { id: 'NOT-8', check: 'All required initials present?', severity: 'CRITICAL' },
      { id: 'NOT-9', check: 'All required dates filled in?', severity: 'CRITICAL' },
      { id: 'NOT-10', check: 'ID copy included (when required)?', severity: 'STANDARD' },
    ],
    fatalFlaws: ['Notarizing without signer present → VOID + criminal charges', 'Not verifying identity → VOID + liability', 'Expired commission → VOID + fines', 'Outside jurisdiction → VOID', 'Backdating → criminal fraud + revocation', 'Notarizing own signature → VOID', 'Prohibited family member → VOID'],
    commonErrors: ['Notarizing without signer present', 'Not verifying ID', 'Incomplete certificate', 'Expired commission', 'Wrong venue/county', 'Missing seal'],
  },
  'ron': {
    title: 'Remote Online Notarization',
    certs: ['Active State Notary Commission', 'RON Certification', 'RON Platform Authorization', 'E&O Insurance (current)'],
    fundamentals: [
      { id: 'RON-1', check: 'Signer identity verified via KBA + credential analysis?', severity: 'FATAL' },
      { id: 'RON-2', check: 'Audio/video recording active for full session?', severity: 'FATAL' },
      { id: 'RON-3', check: 'Notary commission current?', severity: 'FATAL' },
      { id: 'RON-4', check: 'State permits RON for this document type?', severity: 'FATAL' },
      { id: 'RON-5', check: 'Electronic seal applied?', severity: 'CRITICAL' },
      { id: 'RON-6', check: 'Tamper-evident certificate applied?', severity: 'CRITICAL' },
      { id: 'RON-7', check: 'Session recording stored per state retention rules?', severity: 'CRITICAL' },
    ],
    fatalFlaws: ['KBA failure → STOP session', 'No recording → VOID', 'Expired commission → VOID', 'State does not allow RON for document type → VOID'],
    commonErrors: ['KBA failure not documented', 'Recording not started', 'Wrong state rules applied', 'Missing tamper-evident certificate'],
  },
  'phlebotomy': {
    title: 'Occupational Health Screening',
    certs: ['FMCSA National Registry (DOT physicals)', 'PLHCP Certification (respirator evals)', 'Fit Test Administrator Training', 'CAOHC Certification (audiometric testing)'],
    fundamentals: [
      { id: 'OCC-1', check: 'DOT physical by FMCSA-registered examiner?', severity: 'FATAL' },
      { id: 'OCC-2', check: 'Vision: 20/40 each eye, 70° field, color?', severity: 'CRITICAL' },
      { id: 'OCC-3', check: 'Hearing: whisper at 5ft or audiometric ≤40 dB?', severity: 'CRITICAL' },
      { id: 'OCC-4', check: 'BP recorded and certification period correct?', severity: 'CRITICAL' },
      { id: 'OCC-5', check: 'Urinalysis completed (protein, blood, sugar)?', severity: 'CRITICAL' },
      { id: 'OCC-6', check: 'Respirator medical eval before fit test?', severity: 'FATAL' },
      { id: 'OCC-7', check: 'Fit test: all 8 exercises completed?', severity: 'CRITICAL' },
      { id: 'OCC-8', check: 'Audiometric baseline within 6 months of exposure?', severity: 'CRITICAL' },
      { id: 'OCC-9', check: 'STS notification within 21 days if ≥10 dB shift?', severity: 'CRITICAL' },
    ],
    fatalFlaws: ['DOT physical by non-registered examiner → INVALID', 'BP ≥180/110 without treatment → DISQUALIFIED', 'Respirator fit test without medical eval → INVALID'],
    commonErrors: ['Non-registered examiner', 'Skipping respirator medical eval', 'Fit test without medical clearance', 'Missing STS notification', 'Wrong BP certification period'],
  },
  'nemt': {
    title: 'NEMT / Donor Transport',
    certs: ['State NEMT Certification/License', 'CPR/First Aid Certification', 'Defensive Driving Course', 'HIPAA Compliance Training', 'Passenger Assistance Training', 'Vehicle Inspection Certification'],
    fundamentals: [
      { id: 'NEMT-1', check: 'Driver license current and matches state requirements?', severity: 'FATAL' },
      { id: 'NEMT-2', check: 'Vehicle insurance current with required minimums ($1M+)?', severity: 'FATAL' },
      { id: 'NEMT-3', check: 'Vehicle inspection current (daily pre-trip completed)?', severity: 'CRITICAL' },
      { id: 'NEMT-4', check: 'Passenger identity verified before transport?', severity: 'CRITICAL' },
      { id: 'NEMT-5', check: 'Pick-up and drop-off times documented?', severity: 'CRITICAL' },
      { id: 'NEMT-6', check: 'Passenger signature obtained on trip log?', severity: 'CRITICAL' },
      { id: 'NEMT-7', check: 'ADA accessibility requirements met (if applicable)?', severity: 'FATAL' },
      { id: 'NEMT-8', check: 'No-show documented with timestamp and attempt details?', severity: 'CRITICAL' },
      { id: 'NEMT-9', check: 'HIPAA — passenger medical info protected?', severity: 'FATAL' },
      { id: 'NEMT-10', check: 'Incident/accident report filed within 24 hours?', severity: 'CRITICAL' },
    ],
    fatalFlaws: ['Expired license → DRIVER CANNOT OPERATE', 'Lapsed insurance → DRIVER CANNOT OPERATE', 'ADA non-compliance → FEDERAL VIOLATION', 'HIPAA breach → FINE + LIABILITY', 'Wrong passenger transported → LIABILITY'],
    commonErrors: ['Missing trip log signatures', 'Pre-trip inspection skipped', 'No-show not documented', 'Late pickup outside SLA window', 'Passenger complaint not escalated'],
  },
  'rx_delivery': {
    title: 'Prescription Delivery',
    certs: ['HIPAA Compliance Training', 'State Board of Pharmacy Delivery Registration (if required)', 'Background Check (no drug-related offenses)', 'Valid Driver License', 'Temperature-Controlled Transport Training'],
    fundamentals: [
      { id: 'RX-1', check: 'Prescription verified against delivery manifest (patient name, Rx number, pharmacy)?', severity: 'FATAL' },
      { id: 'RX-2', check: 'Recipient identity verified (photo ID or signature match)?', severity: 'FATAL' },
      { id: 'RX-3', check: 'Chain of custody maintained — pharmacy to patient with no unauthorized access?', severity: 'FATAL' },
      { id: 'RX-4', check: 'Temperature-sensitive medications stored in insulated container with temp monitor?', severity: 'FATAL' },
      { id: 'RX-5', check: 'Controlled substance delivery follows DEA requirements (Schedule II-V — signature required, no leave-at-door)?', severity: 'FATAL' },
      { id: 'RX-6', check: 'Delivery timestamp and GPS coordinates recorded?', severity: 'CRITICAL' },
      { id: 'RX-7', check: 'Patient signature or electronic proof of delivery captured?', severity: 'CRITICAL' },
      { id: 'RX-8', check: 'Failed delivery attempt documented with timestamp and reason?', severity: 'CRITICAL' },
      { id: 'RX-9', check: 'HIPAA — no patient health information visible on exterior packaging?', severity: 'FATAL' },
      { id: 'RX-10', check: 'Undeliverable medications returned to pharmacy within required timeframe?', severity: 'CRITICAL' },
      { id: 'RX-11', check: 'Tamper-evident packaging intact upon delivery?', severity: 'FATAL' },
      { id: 'RX-12', check: 'Delivery window SLA met (same-day if ordered before 2 PM)?', severity: 'CRITICAL' },
    ],
    fatalFlaws: [
      'Wrong patient receives medication → PATIENT SAFETY + LIABILITY',
      'Controlled substance left unattended → DEA VIOLATION',
      'Temperature excursion on cold-chain medication → MEDICATION DESTROYED + LIABILITY',
      'Tampered packaging delivered → PATIENT SAFETY CRISIS',
      'HIPAA breach on packaging → FINE + LIABILITY',
      'Chain of custody broken → MEDICATION CANNOT BE DELIVERED',
    ],
    commonErrors: ['Missing delivery signature', 'Temperature monitor not activated', 'Delivery photo not uploaded', 'Wrong delivery address (old address on file)', 'Failed attempt not documented in system'],
  },
  'medical_courier': {
    title: 'Medical Courier / Specimen Transport',
    certs: ['OSHA Bloodborne Pathogens Training', 'DOT/IATA Dangerous Goods (Category B)', 'HIPAA Compliance Training', 'Temperature-Controlled Transport Certification'],
    fundamentals: [
      { id: 'MC-1', check: 'Specimen labeled with patient ID, date, time?', severity: 'FATAL' },
      { id: 'MC-2', check: 'Chain of custody form complete and signed?', severity: 'FATAL' },
      { id: 'MC-3', check: 'Temperature requirements maintained during transport?', severity: 'FATAL' },
      { id: 'MC-4', check: 'Triple-packaging per DOT/IATA requirements?', severity: 'CRITICAL' },
      { id: 'MC-5', check: 'Biohazard markings on outer packaging?', severity: 'CRITICAL' },
      { id: 'MC-6', check: 'Absorbent material in secondary container?', severity: 'CRITICAL' },
      { id: 'MC-7', check: 'Delivery receipt signed at destination?', severity: 'STANDARD' },
    ],
    fatalFlaws: ['Specimen not labeled → REJECT', 'Chain of custody broken → INVALIDATE', 'Temperature excursion → SPECIMEN COMPROMISED'],
    commonErrors: ['Missing patient ID on label', 'Temperature excursion', 'Broken chain of custody', 'Missing biohazard markings'],
  },
  'courier': {
    title: 'Courier / Runner',
    certs: ['Valid Driver License', 'Vehicle Insurance (current)', 'Background Check Clearance'],
    fundamentals: [
      { id: 'CR-1', check: 'Package picked up within scheduled window?', severity: 'CRITICAL' },
      { id: 'CR-2', check: 'Delivery receipt signed at destination?', severity: 'CRITICAL' },
      { id: 'CR-3', check: 'Package condition verified at pickup and delivery?', severity: 'STANDARD' },
      { id: 'CR-4', check: 'Photo documentation of delivery?', severity: 'STANDARD' },
      { id: 'CR-5', check: 'Chain of custody maintained (if applicable)?', severity: 'CRITICAL' },
    ],
    fatalFlaws: ['Package lost → CLAIM', 'Delivery to wrong address → RE-DELIVER'],
    commonErrors: ['Late pickup', 'Missing delivery signature', 'No photo documentation'],
  },
  'background': {
    title: 'Background Check Services',
    certs: ['FCRA Compliance Training', 'State-Specific Background Check Laws', 'CRA (Consumer Reporting Agency) Authorization', 'EEOC Guidance on Criminal Records'],
    fundamentals: [
      { id: 'BG-1', check: 'Written applicant consent/authorization obtained?', severity: 'FATAL' },
      { id: 'BG-2', check: 'FCRA-compliant disclosure provided (standalone document)?', severity: 'FATAL' },
      { id: 'BG-3', check: 'Applicant identity verified with government photo ID?', severity: 'FATAL' },
      { id: 'BG-4', check: 'SSN trace completed for address history?', severity: 'CRITICAL' },
      { id: 'BG-5', check: 'County criminal search covers all relevant jurisdictions?', severity: 'CRITICAL' },
      { id: 'BG-6', check: 'National sex offender registry checked?', severity: 'CRITICAL' },
      { id: 'BG-7', check: 'Pre-adverse action notice sent before denial (FCRA §604)?', severity: 'FATAL' },
      { id: 'BG-8', check: 'Applicant given copy of report + Summary of Rights?', severity: 'FATAL' },
      { id: 'BG-9', check: 'Adverse action notice sent with dispute instructions?', severity: 'FATAL' },
      { id: 'BG-10', check: 'State ban-the-box laws followed (if applicable)?', severity: 'CRITICAL' },
    ],
    fatalFlaws: ['No written consent → FCRA VIOLATION ($100-$1,000 per violation)', 'Disclosure not standalone → FCRA VIOLATION', 'No pre-adverse action notice → LAWSUIT RISK', 'No adverse action notice → FCRA VIOLATION', 'No copy of report to applicant → FCRA VIOLATION'],
    commonErrors: ['Consent form bundled with application (must be standalone)', 'Pre-adverse action notice skipped', 'Wrong jurisdiction searched', 'State ban-the-box law violated', 'Stale records used (7-year lookback)'],
  },
  'apostille': {
    title: 'Apostille Services',
    certs: ['Active State Notary Commission', 'Secretary of State Filing Procedures', 'Hague Convention Knowledge', 'Document Authentication Training'],
    fundamentals: [
      { id: 'APO-1', check: 'Document is a public document eligible for apostille?', severity: 'FATAL' },
      { id: 'APO-2', check: 'Notarization on document is current and valid?', severity: 'FATAL' },
      { id: 'APO-3', check: 'Correct Secretary of State office identified?', severity: 'CRITICAL' },
      { id: 'APO-4', check: 'Destination country is Hague Convention member?', severity: 'FATAL' },
      { id: 'APO-5', check: 'Original document (not photocopy) submitted?', severity: 'CRITICAL' },
      { id: 'APO-6', check: 'Correct fees paid to Secretary of State?', severity: 'CRITICAL' },
      { id: 'APO-7', check: 'Apostille certificate attached to correct document?', severity: 'FATAL' },
      { id: 'APO-8', check: 'Client provided tracking for return shipment?', severity: 'STANDARD' },
    ],
    fatalFlaws: ['Non-public document submitted → REJECTED by SOS', 'Non-Hague country → needs embassy legalization instead', 'Photocopy submitted → REJECTED', 'Apostille attached to wrong document → REDO'],
    commonErrors: ['Submitting to wrong SOS', 'Non-Hague country (need legalization)', 'Missing notarization on document', 'Wrong fee amount', 'Photocopy instead of original'],
  },
  'process': {
    title: 'Process Serving',
    certs: ['State Process Server License/Registration', 'Knowledge of State Service Rules', 'Skip Tracing Training', 'Court Filing Procedures'],
    fundamentals: [
      { id: 'PS-1', check: 'Correct individual/entity identified for service?', severity: 'FATAL' },
      { id: 'PS-2', check: 'Service method compliant with jurisdiction rules?', severity: 'FATAL' },
      { id: 'PS-3', check: 'Documents served within statute of limitations?', severity: 'FATAL' },
      { id: 'PS-4', check: 'Proof of service / affidavit completed accurately?', severity: 'FATAL' },
      { id: 'PS-5', check: 'Date, time, and location of service documented?', severity: 'CRITICAL' },
      { id: 'PS-6', check: 'Physical description of person served recorded?', severity: 'CRITICAL' },
      { id: 'PS-7', check: 'Substitute service documented properly (if applicable)?', severity: 'CRITICAL' },
      { id: 'PS-8', check: 'Proof of service filed with court within deadline?', severity: 'FATAL' },
    ],
    fatalFlaws: ['Wrong person served → SERVICE VOID, case dismissed', 'Service method non-compliant → SERVICE VOID', 'Expired statute of limitations → CASE DISMISSED', 'Proof of service not filed → DEFAULT JUDGMENT RISK', 'Affidavit inaccurate → PERJURY RISK'],
    commonErrors: ['Wrong person served', 'Service outside allowed hours', 'Affidavit filed late', 'Substitute service not properly documented', 'Missing physical description'],
  },
};

const SERVICE_MARGIN_RATES: Record<string, number> = {
  'dot': 0.35, 'non-dot': 0.40, 'dna': 0.50, 'fingerprint': 0.55,
  'notary': 0.60, 'ron': 0.65, 'phlebotomy': 0.35, 'nemt': 0.30,
  'rx_delivery': 0.35, 'medical_courier': 0.35, 'courier': 0.35, 'background': 0.50,
  'apostille': 0.60, 'process': 0.50,
};

/** Every PRISM lane — no exemptions. Drives order QC, scanback review, inspection, and payout gates. */
const PRISM_MANDATORY_QC_DUE_DILIGENCE = {
  headline: 'Mandatory QC due diligence',
  policy:
    'Every PRISM service system must be verified against the Inspection Engine before orders close, scanbacks are approved, and agent payouts release: DOT and non-DOT drug testing, DNA, fingerprinting, notary and loan signing, RON, apostille, process serving, occupational health, NEMT, medical courier, general courier, and background screening. Field operations (REO, preservation, inspections) follow program photo and documentation standards. No lane is optional.',
} as const;

const MandatoryQcDueDiligenceNotice: React.FC<{ compact?: boolean; className?: string }> = ({ compact, className = '' }) => (
  <div
    className={`rounded-xl border border-amber-500/50 bg-gradient-to-r from-amber-500/10 to-orange-900/20 ${compact ? 'p-3' : 'p-4'} ${className}`}
    role="region"
    aria-label={PRISM_MANDATORY_QC_DUE_DILIGENCE.headline}
  >
    <h3 className={`font-bold text-amber-200 ${compact ? 'text-xs' : 'text-sm'}`}>🛡️ {PRISM_MANDATORY_QC_DUE_DILIGENCE.headline}</h3>
    <p className={`text-gray-300 mt-1 leading-relaxed ${compact ? 'text-[11px]' : 'text-sm'}`}>{PRISM_MANDATORY_QC_DUE_DILIGENCE.policy}</p>
  </div>
);

// ─── STATUS BADGES ─────────────────────────────────────────────────
const STATUS_STYLES: Record<string, string> = {
  'New':                  'bg-blue-500/20 text-blue-400 border-blue-500/30',
  'Assigned':             'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
  'Confirmed':            'bg-cyan-500/20 text-cyan-400 border-cyan-500/30',
  'In Progress':          'bg-purple-500/20 text-purple-400 border-purple-500/30',
  'Completed':            'bg-green-500/20 text-green-400 border-green-500/30',
  'Scanned Back':         'bg-indigo-500/20 text-indigo-400 border-indigo-500/30',
  'Under Review':         'bg-orange-500/20 text-orange-400 border-orange-500/30',
  'Errors Found':         'bg-red-500/20 text-red-400 border-red-500/30',
  'Correction Requested': 'bg-red-500/20 text-red-300 border-red-500/30',
  'Re-scanned':           'bg-amber-500/20 text-amber-400 border-amber-500/30',
  'Verified':             'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
  'Closed':               'bg-gray-500/20 text-gray-400 border-gray-500/30',
};

// ─── TYPES ──────────────────────────────────────────────────────────
interface QCItem { id: string; check: string; severity: string; completed: boolean; completed_by: string | null; completed_at: string | null; }
interface WorkflowGate { id: string; check: string; field?: string | null; rule: string; passed: boolean; passed_by: string | null; passed_at: string | null; }
interface WorkflowStage { stage: string; label: string; auto: boolean; gates: WorkflowGate[]; }
interface ScanbackUpload { attempt: number; uploaded_at: string; uploaded_by: string; pages: number; files: string[]; errors: { severity: string; page: number; description: string }[]; }
interface ScanbackData { status: string; uploads: ScanbackUpload[]; reviewed_by?: string; reviewed_at?: string; }
interface PrismOrder { id: string; type: string; service_key?: string; status: string; agent: string; client: string; signer: string; address: string; date: string; time: string; fee: number; priority: string; qc_checklist?: QCItem[]; qc_status?: string; qc_progress?: number; workflow?: WorkflowStage[]; workflow_stage?: number; workflow_stage_label?: string; scanback?: ScanbackData; }
interface PrismAgent { id: string; name: string; specialties: string[]; status: string; city: string; state: string; completionRate: number; onTimeRate: number; errorRate: number; rating: number; ordersCompleted: number; activeOrders: number; }
interface PrismClient { id: string; name: string; type: string; services: string[]; orders: number; revenue: number; status: string; retainer: number; }

/** PRISM API `/prism/dot/collector-due-diligence` — operator “basics” (audit / autopilot risk) */
interface PrismDotDueDiligencePayload {
  title?: string;
  summary?: string;
  reminders?: { order: number; title: string; body: string; reference?: string; prism_workflow_ref?: string }[];
  mindset?: string;
  closing?: string;
}

// ─── FIELD OPS (REO / MORTGAGE FIELD SERVICES) ─────────────────────
interface PropertyWorkOrder {
  id: string; property_address: string; city: string; state: string; zip: string;
  property_type: string; program: string; service_type: string; status: string;
  priority: string; assigned_to: string; vendor_source: string;
  photos_required: number; photos_submitted: number; condition_code: string;
  due_date: string; recurring: boolean; recurring_freq?: string;
  fee: number; notes: string; created_at: string;
}

const FIELD_OPS_PROGRAMS: Record<string, { label: string; color: string; solid: string; icon: string }> = {
  hud_fsm: { label: 'HUD FSM', color: '#3B82F6', solid: '#2563EB', icon: '🏛️' },
  va_reo: { label: 'VA REO', color: '#10B981', solid: '#059669', icon: '🎖️' },
  usda_rd: { label: 'USDA RD', color: '#F59E0B', solid: '#D97706', icon: '🌾' },
  fannie_mae: { label: 'Fannie Mae', color: '#8B5CF6', solid: '#7C3AED', icon: '🏘️' },
  freddie_mac: { label: 'Freddie Mac', color: '#EC4899', solid: '#DB2777', icon: '🏡' },
  bank_reo: { label: 'Bank REO', color: '#6366F1', solid: '#4F46E5', icon: '🏦' },
};

const FIELD_OPS_SERVICES: Record<string, { label: string; icon: string }> = {
  occupancy_check: { label: 'Occupancy Check', icon: '👁️' },
  interior_inspection: { label: 'Interior Inspection', icon: '🔍' },
  condition_report: { label: 'Condition Report', icon: '📋' },
  preservation: { label: 'Preservation', icon: '🔒' },
  lawn_maintenance: { label: 'Lawn / Grounds', icon: '🌿' },
  winterization: { label: 'Winterization', icon: '❄️' },
  board_up: { label: 'Board-Up / Secure', icon: '🪵' },
  debris_removal: { label: 'Debris Removal', icon: '🗑️' },
  damage_assessment: { label: 'Damage Assessment', icon: '⚠️' },
};

const FIELD_OPS_STATUSES: Record<string, { label: string; color: string }> = {
  new: { label: 'New', color: '#6B7280' },
  assigned: { label: 'Assigned', color: '#3B82F6' },
  en_route: { label: 'En Route', color: '#F59E0B' },
  on_site: { label: 'On Site', color: '#8B5CF6' },
  photos_submitted: { label: 'Photos Submitted', color: '#14B8A6' },
  report_pending: { label: 'Report Pending', color: '#F97316' },
  qc_review: { label: 'QC Review', color: '#EC4899' },
  complete: { label: 'Complete', color: '#10B981' },
  rejected: { label: 'Rejected', color: '#EF4444' },
};

const VENDOR_SOURCES: Record<string, { label: string; icon: string }> = {
  ddi_direct: { label: 'DDI Direct', icon: '🔷' },
  ivueit: { label: 'iVueit', icon: '📱' },
  cs_field: { label: 'CS Field Services', icon: '🏢' },
  vrm: { label: 'VRM Mortgage', icon: '🏠' },
  altisource: { label: 'Altisource', icon: '🔶' },
};

// ─── HELPER COMPONENTS ─────────────────────────────────────────────
const ServiceBadge: React.FC<{ type: string; size?: 'sm' | 'md' }> = ({ type, size = 'sm' }) => {
  const svc = SERVICE_COLORS[type] || SERVICE_COLORS['notary'];
  const px = size === 'sm' ? 'px-2.5 py-1 text-xs' : 'px-3 py-1.5 text-sm';
  return (
    <span className={`${px} rounded-full font-bold inline-flex items-center gap-1 shadow-md`}
      style={{ backgroundColor: svc.solid, color: '#FFFFFF' }}>
      {svc.icon} {svc.label}
    </span>
  );
};

const StatusBadge: React.FC<{ status: string }> = ({ status }) => {
  const style = STATUS_STYLES[status] || 'bg-gray-500/20 text-gray-400 border-gray-500/30';
  return <span className={`px-2 py-0.5 rounded-full text-xs font-semibold border ${style}`}>{status}</span>;
};

const StatCard: React.FC<{ label: string; value: string | number; sub?: string; color?: string; icon?: string }> = ({ label, value, sub, color = 'blue', icon }) => (
  <div className="bg-gray-800 border border-gray-700 rounded-xl p-4 hover:border-gray-600 transition">
    <div className="flex items-center justify-between mb-2">
      <span className="text-gray-400 text-xs font-semibold uppercase tracking-wider">{label}</span>
      {icon && <span className="text-lg">{icon}</span>}
    </div>
    <p className={`text-2xl font-bold text-${color}-400`}>{value}</p>
    {sub && <p className="text-xs text-gray-500 mt-1">{sub}</p>}
  </div>
);

// ─── MAIN COMPONENT ────────────────────────────────────────────────
const PRISMSystem: React.FC<PRISMSystemProps> = ({
  onBackToNexus,
  onNavigate,
  activeTab,
  setActiveTab,
  initialDivision,
  initialDivisionSection,
  onDeepLinkConsumed,
}) => {
  const [activeDivision, setActiveDivision] = useState<string | null>(null);
  const [expandedDivisions, setExpandedDivisions] = useState<Set<string>>(new Set());
  const [divisionSection, setDivisionSection] = useState<'overview' | 'orders' | 'agents' | 'scanbacks'>('overview');
  
  // Portal Webview State (for Electron embedded browser)
  const [activePortal, setActivePortal] = useState<{
    portal: PartnerPortal;
    division: PrismDivision;
  } | null>(null);

  const handleOpenPortal = (portal: PartnerPortal, division: PrismDivision) => {
    if (isElectron()) {
      // In Electron: open in embedded webview
      setActivePortal({ portal, division });
    } else {
      // In browser: open in new tab
      window.open(portal.url, '_blank', 'noopener,noreferrer');
    }
  };

  const handleClosePortal = () => {
    setActivePortal(null);
  };
  
  const toggleDivisionExpand = (divisionId: string) => {
    setExpandedDivisions(prev => {
      const next = new Set(prev);
      if (next.has(divisionId)) {
        next.delete(divisionId);
      } else {
        next.add(divisionId);
      }
      return next;
    });
  };
  const [orderView, setOrderView] = useState<'list' | 'kanban' | 'calendar'>('list');
  const [orderFilter, setOrderFilter] = useState('all');
  const [selectedOrder, setSelectedOrder] = useState<string | null>(null);
  const [selectedScanback, setSelectedScanback] = useState<string | null>(null);
  const [showNewOrderModal, setShowNewOrderModal] = useState(false);
  const [scanbackFilter, setScanbackFilter] = useState('all');
  const [agentFilter, setAgentFilter] = useState('all');
  const [inspSvc, setInspSvc] = useState('dot');
  const [dotDueDiligence, setDotDueDiligence] = useState<PrismDotDueDiligencePayload | null>(null);
  const [dotDueDiligenceLoad, setDotDueDiligenceLoad] = useState<'idle' | 'loading' | 'ok' | 'error'>('idle');
  const [stageFilter, setStageFilter] = useState('all');
  const [fieldOpsFilter, setFieldOpsFilter] = useState('all');
  const [fieldOpsView, setFieldOpsView] = useState<'list' | 'route' | 'photos'>('list');
  const [selectedProperty, setSelectedProperty] = useState<string | null>(null);

  const [credentialingOpen, setCredentialingOpen] = useState(false);
  const [credentialingCatalog, setCredentialingCatalog] = useState<{
    credentials?: Record<string, unknown>;
    bundles?: Record<string, unknown>;
    full_packages?: Record<string, unknown>;
    policy?: string;
  } | null>(null);
  const [credentialingLoad, setCredentialingLoad] = useState<'idle' | 'loading' | 'ok' | 'error'>('idle');
  const [credQuoteMode, setCredQuoteMode] = useState<'package' | 'bundles' | 'credentials'>('package');
  const [selectedFullPackage, setSelectedFullPackage] = useState('');
  const [selectedBundleIds, setSelectedBundleIds] = useState<string[]>([]);
  const [selectedCredKeys, setSelectedCredKeys] = useState<string[]>([]);
  const [credQuoteResult, setCredQuoteResult] = useState<Record<string, unknown> | null>(null);
  const [credQuoteLoading, setCredQuoteLoading] = useState(false);

  const enterDivision = (divId: string) => {
    setActiveDivision(divId);
    setDivisionSection('overview');
    setSelectedOrder(null);
    if (divId === 'field_ops') {
      setActiveTab('fieldops');
    } else {
      setActiveTab('dashboard');
    }
  };

  useEffect(() => {
    if (!initialDivision) return;
    const valid = PRISM_DIVISIONS.some((d) => d.id === initialDivision);
    if (valid) {
      setActiveDivision(initialDivision);
      setActiveTab('dashboard');
    }
    onDeepLinkConsumed?.();
    // Deep link consumed once on mount when App passes initialDivision
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [initialDivision]);

  const exitDivision = () => {
    setActiveDivision(null);
    setActiveTab('dashboard');
    setSelectedOrder(null);
  };

  const currentDivision = PRISM_DIVISIONS.find(d => d.id === activeDivision);

  const [orders, setOrders] = useState<PrismOrder[]>([]);
  const [agents, setAgents] = useState<PrismAgent[]>([]);
  const [clients, setClients] = useState<PrismClient[]>([]);
  const [prismStats, setPrismStats] = useState<any>(null);
  const [dataLoading, setDataLoading] = useState(true);
  const [notifications, setNotifications] = useState<PrismNotification[]>([]);
  const [showNotifPanel, setShowNotifPanel] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);

  const getDivisionOrders = (div: PrismDivision) => orders.filter(o => div.types.includes(o.type));
  const getDivisionScanbacks = (div: PrismDivision) => scanbacks.filter(s => div.types.includes(s.type));

  const loadPrismData = useCallback(async () => {
    setDataLoading(true);
    try {
      const [ordersRes, agentsRes, clientsRes] = await Promise.allSettled([
        api.get('/prism/orders').catch(() => ({ orders: [] })),
        api.get('/prism/agents').catch(() => ({ agents: [] })),
        api.get('/prism/clients').catch(() => ({ clients: [] })),
      ]);
      if (ordersRes.status === 'fulfilled') {
        const v = (ordersRes.value as any);
        setOrders(v?.orders || v?.data?.orders || []);
      }
      if (agentsRes.status === 'fulfilled') {
        const v = (agentsRes.value as any);
        setAgents(v?.agents || v?.data?.agents || []);
      }
      if (clientsRes.status === 'fulfilled') {
        const v = (clientsRes.value as any);
        setClients(v?.clients || v?.data?.clients || []);
      }
    } catch { /* empty fallback — arrays stay empty */ }
    setDataLoading(false);
  }, []);

  const loadNotifications = useCallback(async () => {
    try {
      const res = await api.getNotifications('admin', 30).catch(() => ({ notifications: [], unread: 0 }));
      setNotifications(res?.notifications || []);
      setUnreadCount(res?.unread || 0);
    } catch { /* empty */ }
  }, []);

  const markNotificationsRead = useCallback(async (ids?: string[]) => {
    try {
      await api.markNotificationsRead(ids);
      loadNotifications();
    } catch { /* empty */ }
  }, [loadNotifications]);

  const handleOpsNotificationClick = useCallback((notif: PrismNotification) => {
    const orderId = notif.order_id;
    if (orderId) {
      const order = orders.find((o) => o.id === orderId);
      const serviceType = order?.type;
      const div = serviceType
        ? PRISM_DIVISIONS.find((d) => d.types.includes(serviceType))
        : PRISM_DIVISIONS.find((d) => d.id === 'transport');
      if (div) {
        setActiveDivision(div.id);
        setActiveTab('dashboard');
      }
    }
    setShowNotifPanel(false);
  }, [orders]);

  useEffect(() => { loadPrismData(); loadNotifications(); }, [loadPrismData, loadNotifications]);

  useEffect(() => {
    if (activeTab !== 'inspection' && activeTab !== 'scanbacks') return;
    let cancelled = false;
    setDotDueDiligenceLoad('loading');
    (async () => {
      try {
        const d = await api.getPrismDotCollectorDueDiligence() as PrismDotDueDiligencePayload;
        if (cancelled) return;
        if (d && Array.isArray(d.reminders)) {
          setDotDueDiligence(d);
          setDotDueDiligenceLoad('ok');
        } else {
          setDotDueDiligence(null);
          setDotDueDiligenceLoad('error');
        }
      } catch {
        if (!cancelled) {
          setDotDueDiligence(null);
          setDotDueDiligenceLoad('error');
        }
      }
    })();
    return () => { cancelled = true; };
  }, [activeTab]);

  useEffect(() => {
    const interval = setInterval(loadNotifications, 15000);
    return () => clearInterval(interval);
  }, [loadNotifications]);

  useEffect(() => {
    if (!credentialingOpen) return;
    let cancelled = false;
    setCredentialingLoad('loading');
    (async () => {
      try {
        const d = (await api.getPrismCredentialingPricing()) as Record<string, unknown>;
        if (cancelled) return;
        setCredentialingCatalog(d);
        setCredentialingLoad('ok');
        const fp = d.full_packages as Record<string, unknown> | undefined;
        if (fp) {
          const keys = Object.keys(fp);
          setSelectedFullPackage(prev => (prev && keys.includes(prev) ? prev : keys[0] || ''));
        }
      } catch {
        if (!cancelled) setCredentialingLoad('error');
      }
    })();
    return () => { cancelled = true; };
  }, [credentialingOpen]);

  const runCredentialQuote = useCallback(async () => {
    setCredQuoteLoading(true);
    setCredQuoteResult(null);
    try {
      let body: { full_package?: string; bundles?: string[]; credentials?: string[] } = {};
      if (credQuoteMode === 'package') {
        if (!selectedFullPackage) {
          setCredQuoteResult({ error: 'Select a full package' });
          setCredQuoteLoading(false);
          return;
        }
        body = { full_package: selectedFullPackage };
      } else if (credQuoteMode === 'bundles') {
        if (selectedBundleIds.length === 0) {
          setCredQuoteResult({ error: 'Select one or more bundles' });
          setCredQuoteLoading(false);
          return;
        }
        body = { bundles: selectedBundleIds };
      } else {
        if (selectedCredKeys.length === 0) {
          setCredQuoteResult({ error: 'Select one or more credentials' });
          setCredQuoteLoading(false);
          return;
        }
        body = { credentials: selectedCredKeys };
      }
      const r = (await api.postPrismCredentialingQuote(body)) as Record<string, unknown>;
      setCredQuoteResult(r);
    } catch (e: unknown) {
      setCredQuoteResult({ error: e instanceof Error ? e.message : 'Quote request failed' });
    } finally {
      setCredQuoteLoading(false);
    }
  }, [credQuoteMode, selectedFullPackage, selectedBundleIds, selectedCredKeys]);

  const toggleCredBundle = (id: string) => {
    setSelectedBundleIds(prev => (prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]));
  };

  const tabs = [
    { id: 'dashboard', label: '🎯 Command Center' },
    { id: 'orders', label: '📋 Orders' },
    { id: 'dispatch', label: '🚀 Dispatch' },
    { id: 'fieldops', label: '🏠 Field Ops' },
    { id: 'scanbacks', label: '📸 Scanbacks' },
    { id: 'agents', label: '👤 Field Agents' },
    { id: 'clients', label: '🏢 Clients' },
    { id: 'inspection', label: '🔍 Inspection' },
    { id: 'payments', label: '💰 Payments' },
    { id: 'analytics', label: '📊 Analytics' },
  ];

  const today = new Date().toLocaleDateString('en-US', { month: '2-digit', day: '2-digit', year: 'numeric' });
  const todayOrders = orders.filter(o => o.date === today);
  const activeOrders = orders.filter(o => !['Closed', 'Verified'].includes(o.status));
  // Derive scanbacks from orders (orders at documentation stage or with scanback data)
  const scanbackOrders = orders.filter(o => o.scanback || (o.workflow_stage ?? 0) >= 5);
  const scanbacks = scanbackOrders.map(o => {
    const sb = o.scanback;
    const latest = sb?.uploads?.length ? sb.uploads[sb.uploads.length - 1] : null;
    const sbStatus = sb?.status || 'Awaiting Upload';
    return {
      id: `SB-${o.id}`,
      orderId: o.id,
      type: o.type,
      agent: o.agent || 'Unassigned',
      client: o.client,
      signer: o.signer,
      status: sbStatus,
      pages: latest?.pages || 0,
      expected: ({'dot':3,'non-dot':2,'dna':3,'fingerprint':2,'background':2,'notary':2,'ron':3,'apostille':2,'process':2,'nemt':2,'rx_delivery':2,'medical_courier':2,'courier':1,'phlebotomy':2} as Record<string,number>)[o.type] || 2,
      expectedDocs: [] as string[],
      uploadDate: latest?.uploaded_at || '',
      attempt: sb?.uploads?.length || 0,
      errors: latest?.errors || [],
      reviewed_by: sb?.reviewed_by || null,
      reviewed_at: sb?.reviewed_at || null,
    };
  });

  const awaitingScanback = scanbacks.filter(s => s.status === 'Awaiting Upload');
  const errorsFound = scanbacks.filter(s => s.status === 'Errors Found');
  const unassigned = orders.filter(o => o.status === 'New');
  const needsReview = scanbacks.filter(s => s.status === 'Needs Review');

  const KANBAN_STAGES = [
    { key: 'received', label: 'Received', color: '#3B82F6' },
    { key: 'validated', label: 'Validated', color: '#06B6D4' },
    { key: 'assigned', label: 'Assigned', color: '#6366F1' },
    { key: 'en_route', label: 'En Route', color: '#A855F7' },
    { key: 'in_progress', label: 'In Progress', color: '#F97316' },
    { key: 'qc_review', label: 'QC Review', color: '#EAB308' },
    { key: 'documentation', label: 'Documentation', color: '#14B8A6' },
    { key: 'delivered', label: 'Delivered', color: '#10B981' },
    { key: 'billed', label: 'Billed', color: '#84CC16' },
    { key: 'complete', label: 'Complete', color: '#22C55E' },
  ];
  const kanbanColumns = KANBAN_STAGES.map(s => ({
    status: s.label,
    color: s.color,
    orders: orders.filter(o => {
      const stageKey = o.workflow?.[o.workflow_stage ?? 0]?.stage || '';
      return stageKey === s.key;
    }),
  }));

  const filteredOrders = orders.filter(o => {
    if (orderFilter !== 'all') {
      const group = SERVICE_GROUPS.find(g => g.id === orderFilter);
      if (group && !group.types.includes(o.type)) return false;
      if (!group && o.type !== orderFilter) return false;
    }
    if (stageFilter !== 'all') {
      const currentStage = o.workflow?.[o.workflow_stage ?? 0]?.stage || '';
      if (currentStage !== stageFilter) return false;
    }
    return true;
  });
  const filteredScanbacks = scanbackFilter === 'all' ? scanbacks : scanbacks.filter(s => s.status === scanbackFilter);
  const filteredAgents = agentFilter === 'all' ? agents : agents.filter(a => a.status === agentFilter);

  const todaySchedule = useMemo((): HubScheduleItem[] => {
    const todayIso = new Date().toISOString().slice(0, 10);
    const todayUs = new Date().toLocaleDateString('en-US', { month: '2-digit', day: '2-digit', year: 'numeric' });

    const isToday = (dateStr: string) => {
      if (!dateStr) return false;
      if (dateStr.startsWith(todayIso)) return true;
      if (dateStr === todayUs) return true;
      const normalized = dateStr.replace(/\//g, '-');
      return normalized.startsWith(todayIso);
    };

    return orders
      .filter((o) => isToday(o.date))
      .slice(0, 25)
      .map((o) => {
        const div = PRISM_DIVISIONS.find((d) => d.types.includes(o.type));
        const svc = SERVICE_COLORS[o.type];
        let status: HubScheduleItem['status'] = 'scheduled';
        const st = o.status || '';
        if (['In Progress', 'En Route', 'Arrived', 'Departed'].some((s) => st.includes(s))) {
          status = 'in_progress';
        } else if (['Complete', 'Completed', 'Verified', 'Closed'].some((s) => st.includes(s))) {
          status = 'completed';
        } else if (st === 'New') {
          status = 'pending';
        }
        return {
          id: o.id,
          time: o.time || '—',
          subject: o.signer || svc?.label || o.type,
          type: svc?.label || o.type,
          client: o.client,
          status,
          divId: div?.id || PRISM_DIVISIONS[0].id,
          color: div?.color || svc?.color || '#6366F1',
        };
      })
      .sort((a, b) => a.time.localeCompare(b.time));
  }, [orders]);

  const divisionNotifications = useMemo(
    () =>
      countDivisionNotifications(
        orders,
        PRISM_DIVISIONS.map((d) => ({ id: d.id, types: d.types }))
      ),
    [orders]
  );

  const handleAssignAgent = useCallback(
    async (orderId: string, agent: { name: string }) => {
      await api.patch(`/prism/orders/${encodeURIComponent(orderId)}`, {
        agent: agent.name,
        status: 'Agent Assigned',
      });
      await loadPrismData();
    },
    [loadPrismData]
  );

  // Build division config for TPADivisionWorkspace
  const getDivisionConfig = (div: typeof currentDivision) => {
    if (!div) return null;
    const portals = PARTNER_PORTALS[div.portalKey] || [];
    return {
      id: div.id,
      name: div.name,
      icon: div.icon,
      color: div.color,
      solid: div.solid,
      serviceTypes: div.types.map(t => ({ id: t, label: SERVICE_COLORS[t]?.label || t })),
      partnerPortals: portals.filter(p => p.status === 'active').map(p => ({
        id: p.id,
        name: p.name,
        url: p.url,
        icon: p.icon,
      })),
    };
  };

  // Use new TPADivisionWorkspace for cleaner division view
  const useNewWorkspace = true; // Toggle this to switch between old and new UI

  return (
    <div className={`min-h-screen ${activePortal ? 'flex' : ''} bg-gradient-to-br from-gray-900 via-purple-900/20 to-gray-900`}>
      {/* ─── MAIN PRISM CONTENT (full width or half width) ─── */}
      <div className={`${activePortal ? 'w-1/2 overflow-y-auto h-[calc(100vh-73px)] border-r border-gray-700' : 'w-full'}`}>
      
      {/* ═══ NEW TPA DIVISION WORKSPACE ═══ */}
      {useNewWorkspace && activeDivision && currentDivision && getDivisionConfig(currentDivision) && (
        <TPADivisionWorkspace
          division={getDivisionConfig(currentDivision)!}
          initialSection={
            initialDivisionSection === 'revenue' && currentDivision.id === 'transport'
              ? 'revenue'
              : undefined
          }
          onNavigate={onNavigate}
          orders={getDivisionOrders(currentDivision).map((o) =>
            mapPrismApiOrderToWorkspace(o as unknown as Record<string, unknown>)
          )}
          ordersLoading={dataLoading}
          onRefreshOrders={loadPrismData}
          clients={clients.map((c) => mapPrismApiClientToWorkspace(c as unknown as Record<string, unknown>))}
          clientsLoading={dataLoading}
          scanbacks={getDivisionScanbacks(currentDivision) as DivisionScanback[]}
          agents={agents}
          agentsLoading={dataLoading}
          agentSpecialtyLabels={currentDivision.agentSpecialties}
          onAssignAgent={handleAssignAgent}
          opsNotifications={notifications}
          opsUnreadCount={unreadCount}
          opsFeedOpen={showNotifPanel}
          onToggleOpsFeed={() => setShowNotifPanel((v) => !v)}
          onMarkOpsRead={(id) => markNotificationsRead([id])}
          onMarkAllOpsRead={() => markNotificationsRead()}
          onOpsNotificationClick={handleOpsNotificationClick}
          onOpenPortal={(portal) => handleOpenPortal(
            { id: portal.id, name: portal.name, url: portal.url, icon: portal.icon, description: '', loginType: 'portal' as const, status: 'active' as const },
            currentDivision
          )}
          onBack={exitDivision}
        />
      )}

      {/* ═══ NEW CLEAN PRISM HUB ═══ */}
      {!activeDivision && (
        <PRISMHub
          divisions={PRISM_DIVISIONS.map(d => ({
            id: d.id,
            name: d.name,
            icon: d.icon,
            color: d.color,
            solid: d.solid,
          }))}
          todaySchedule={todaySchedule}
          divisionNotifications={divisionNotifications}
          opsNotifications={notifications}
          opsUnreadCount={unreadCount}
          opsFeedOpen={showNotifPanel}
          onToggleOpsFeed={() => setShowNotifPanel((v) => !v)}
          onMarkOpsRead={(id) => markNotificationsRead([id])}
          onMarkAllOpsRead={() => markNotificationsRead()}
          onOpsNotificationClick={handleOpsNotificationClick}
          onSelectDivision={(divId) => enterDivision(divId)}
          onNewOrder={() => setShowNewOrderModal(true)}
          onBackToNexus={onBackToNexus}
        />
      )}

      {/* ─── NEW ORDER MODAL ────────────────────────────── */}
      {showNewOrderModal && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center" onClick={() => setShowNewOrderModal(false)}>
          <div className="bg-gray-900 border border-gray-700 rounded-2xl w-full max-w-lg mx-4 shadow-2xl" onClick={e => e.stopPropagation()}>
            <div className="p-6 border-b border-gray-700">
              <div className="flex items-center justify-between">
                <h3 className="text-xl font-bold">New Order</h3>
                <button onClick={() => setShowNewOrderModal(false)} className="text-gray-500 hover:text-white transition text-lg">✕</button>
              </div>
            </div>
            <div className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-semibold text-gray-400 mb-2">Service Type</label>
                <div className="grid grid-cols-2 gap-2">
                  {Object.entries(SERVICE_COLORS).map(([key, svc]) => (
                    <button key={key} className="flex items-center gap-2 px-3 py-2.5 rounded-lg border border-gray-700 hover:border-gray-500 transition text-left text-sm"
                      style={{ borderLeftWidth: '4px', borderLeftColor: svc.color }}>
                      <span>{svc.icon}</span>
                      <span>{svc.label}</span>
                    </button>
                  ))}
                </div>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-gray-500 mb-1">Signer / Subject Name</label>
                  <input type="text" className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm focus:border-orange-500 focus:outline-none transition" placeholder="Full name" />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-gray-500 mb-1">Phone</label>
                  <input type="tel" className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm focus:border-orange-500 focus:outline-none transition" placeholder="(248) 555-0000" />
                </div>
              </div>
              <div>
                <label className="block text-xs font-semibold text-gray-500 mb-1">Address</label>
                <input type="text" className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm focus:border-orange-500 focus:outline-none transition" placeholder="Full address" />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-gray-500 mb-1">Date</label>
                  <input type="date" className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm focus:border-orange-500 focus:outline-none transition" />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-gray-500 mb-1">Time</label>
                  <input type="time" className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm focus:border-orange-500 focus:outline-none transition" />
                </div>
              </div>
              <div>
                <label className="block text-xs font-semibold text-gray-500 mb-1">Client</label>
                <select className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm focus:border-orange-500 focus:outline-none transition text-gray-300">
                  <option value="">Select client...</option>
                  {clients.length > 0 ? clients.map(c => <option key={c.id} value={c.id}>{c.name}</option>) : <option value="">No clients loaded</option>}
                </select>
              </div>
              <div>
                <label className="block text-xs font-semibold text-gray-500 mb-1">Special Instructions</label>
                <textarea className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm focus:border-orange-500 focus:outline-none transition h-20 resize-none" placeholder="Panel type, ORI code, collection method, test reason, compliance notes..." />
              </div>
            </div>
            <div className="p-6 border-t border-gray-700 flex gap-3">
              <button className="flex-1 bg-orange-500 hover:bg-orange-600 px-4 py-2.5 rounded-lg font-semibold transition">
                Create Order
              </button>
              <button onClick={() => setShowNewOrderModal(false)} className="bg-gray-700 hover:bg-gray-600 px-4 py-2.5 rounded-lg font-semibold transition">
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
      </div>{/* End of main PRISM content wrapper - OLD CODE DELETED FOR CLEAN BUILD */}
      
      {/* ─── SPLIT VIEW: PARTNER PORTAL ON THE RIGHT ─── */}
      {activePortal && (
        <div className="w-1/2 h-[calc(100vh-73px)] overflow-hidden flex-shrink-0">
          <PartnerWebview
            url={activePortal.portal.url}
            name={activePortal.portal.name}
            icon={activePortal.portal.icon}
            color={activePortal.division.color}
            onClose={handleClosePortal}
          />
        </div>
      )}
    </div>
  );
};

export default PRISMSystem;
