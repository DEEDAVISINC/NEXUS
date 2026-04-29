import React, { useState, useEffect, useCallback } from 'react';
import { api } from '../../api/client';

interface PRISMSystemProps {
  onBackToNexus: () => void;
  onNavigate?: (view: any) => void;
  activeTab: string;
  setActiveTab: (tab: string) => void;
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
  { id: 'courier',        label: 'Courier / Delivery',   icon: '📦', types: ['medical_courier', 'courier'],  color: '#6366F1', solid: '#4F46E5' },
];

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
  },
  {
    id: 'fingerprint_bg',
    name: 'Fingerprinting & Background',
    subtitle: 'LiveScan • FD-258 Ink Cards • EFT • FCRA Background Checks',
    icon: '🖐️',
    color: '#4ADE80',
    solid: '#16A34A',
    gradient: 'from-green-600 to-green-800',
    types: ['fingerprint', 'background'],
    agentSpecialties: ['Print Technician', 'Background Specialist'],
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
  },
  {
    id: 'transport',
    name: 'Transport & Courier',
    subtitle: 'NEMT • Rx Delivery • Medical Courier • Legal Courier • Specimen Transport',
    icon: '🚐',
    color: '#14B8A6',
    solid: '#0D9488',
    gradient: 'from-teal-600 to-teal-800',
    types: ['nemt', 'rx_delivery', 'medical_courier', 'courier'],
    agentSpecialties: ['Courier', 'NEMT Driver', 'Medical Courier', 'Rx Delivery Driver'],
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
  },
];

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
interface PrismOrder { id: string; type: string; status: string; agent: string; client: string; signer: string; address: string; date: string; time: string; fee: number; priority: string; qc_checklist?: QCItem[]; qc_status?: string; qc_progress?: number; workflow?: WorkflowStage[]; workflow_stage?: number; workflow_stage_label?: string; scanback?: ScanbackData; }
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

const MOCK_PROPERTY_ORDERS: PropertyWorkOrder[] = [
  { id: 'FO-2026-001', property_address: '14520 Greenfield Rd', city: 'Detroit', state: 'MI', zip: '48227', property_type: 'single_family', program: 'hud_fsm', service_type: 'occupancy_check', status: 'assigned', priority: 'standard', assigned_to: 'DDI Agent - Metro Detroit', vendor_source: 'ddi_direct', photos_required: 6, photos_submitted: 0, condition_code: '', due_date: '03/23/2026', recurring: true, recurring_freq: 'monthly', fee: 35, notes: 'Monthly occupancy verification — check mailbox, lawn, windows', created_at: '2026-03-20T10:00:00' },
  { id: 'FO-2026-002', property_address: '8831 Outer Dr', city: 'Detroit', state: 'MI', zip: '48213', property_type: 'single_family', program: 'hud_fsm', service_type: 'interior_inspection', status: 'on_site', priority: 'rush', assigned_to: 'iVueit Inspector #4412', vendor_source: 'ivueit', photos_required: 24, photos_submitted: 18, condition_code: 'C4-Poor', due_date: '03/21/2026', recurring: false, fee: 125, notes: 'Full interior — reported water damage in basement. Document all rooms + damage areas.', created_at: '2026-03-19T14:00:00' },
  { id: 'FO-2026-003', property_address: '2200 Joslyn Ct', city: 'Pontiac', state: 'MI', zip: '48340', property_type: 'townhouse', program: 'va_reo', service_type: 'condition_report', status: 'photos_submitted', priority: 'standard', assigned_to: 'CS Field - Oakland Region', vendor_source: 'cs_field', photos_required: 18, photos_submitted: 18, condition_code: 'C3-Average', due_date: '03/24/2026', recurring: false, fee: 150, notes: 'VA REO — full property condition report needed for listing decision', created_at: '2026-03-18T09:00:00' },
  { id: 'FO-2026-004', property_address: '6742 Maplewood Ave', city: 'Flint', state: 'MI', zip: '48505', property_type: 'single_family', program: 'hud_fsm', service_type: 'board_up', status: 'new', priority: 'rush', assigned_to: '', vendor_source: 'ddi_direct', photos_required: 12, photos_submitted: 0, condition_code: '', due_date: '03/22/2026', recurring: false, fee: 275, notes: 'Broken front window + side door open. Secure immediately. HUD priority.', created_at: '2026-03-21T08:00:00' },
  { id: 'FO-2026-005', property_address: '310 W Huron St', city: 'Ann Arbor', state: 'MI', zip: '48103', property_type: 'condo', program: 'fannie_mae', service_type: 'damage_assessment', status: 'qc_review', priority: 'standard', assigned_to: 'VRM Inspector - Washtenaw', vendor_source: 'vrm', photos_required: 20, photos_submitted: 20, condition_code: 'C5-Distressed', due_date: '03/22/2026', recurring: false, fee: 175, notes: 'Fire damage — kitchen and adjacent bedroom. Insurance claim pending.', created_at: '2026-03-17T11:00:00' },
  { id: 'FO-2026-006', property_address: '1455 Bewick St', city: 'Detroit', state: 'MI', zip: '48214', property_type: 'single_family', program: 'hud_fsm', service_type: 'lawn_maintenance', status: 'complete', priority: 'standard', assigned_to: 'DDI Agent - Metro Detroit', vendor_source: 'ddi_direct', photos_required: 4, photos_submitted: 4, condition_code: 'C3-Average', due_date: '03/20/2026', recurring: true, recurring_freq: 'biweekly', fee: 85, notes: 'Biweekly lawn cut — front and back. Photo before/after.', created_at: '2026-03-14T10:00:00' },
  { id: 'FO-2026-007', property_address: '920 E Grand Blvd', city: 'Detroit', state: 'MI', zip: '48207', property_type: 'multi_family', program: 'bank_reo', service_type: 'winterization', status: 'report_pending', priority: 'rush', assigned_to: 'Altisource Tech #2287', vendor_source: 'altisource', photos_required: 16, photos_submitted: 16, condition_code: 'C4-Poor', due_date: '03/21/2026', recurring: false, fee: 325, notes: 'Drain all pipes, apply antifreeze to toilets/traps, shut off water main. Document every step.', created_at: '2026-03-19T13:00:00' },
  { id: 'FO-2026-008', property_address: '3380 Sheridan Dr', city: 'Warren', state: 'MI', zip: '48091', property_type: 'single_family', program: 'usda_rd', service_type: 'occupancy_check', status: 'en_route', priority: 'standard', assigned_to: 'DDI Agent - Macomb', vendor_source: 'ddi_direct', photos_required: 6, photos_submitted: 0, condition_code: '', due_date: '03/21/2026', recurring: true, recurring_freq: 'monthly', fee: 35, notes: 'USDA Rural Dev property — monthly check, photograph front + mailbox + lawn condition', created_at: '2026-03-21T07:30:00' },
  { id: 'FO-2026-009', property_address: '17200 Livernois Ave', city: 'Detroit', state: 'MI', zip: '48221', property_type: 'single_family', program: 'hud_fsm', service_type: 'debris_removal', status: 'assigned', priority: 'standard', assigned_to: 'CS Field - Wayne Region', vendor_source: 'cs_field', photos_required: 8, photos_submitted: 0, condition_code: '', due_date: '03/25/2026', recurring: false, fee: 200, notes: 'Illegal dumping on side lot. Clear all debris + photograph before/after.', created_at: '2026-03-20T15:00:00' },
  { id: 'FO-2026-010', property_address: '5488 Chalmers St', city: 'Detroit', state: 'MI', zip: '48213', property_type: 'single_family', program: 'hud_fsm', service_type: 'preservation', status: 'assigned', priority: 'rush', assigned_to: 'DDI Agent - Metro Detroit', vendor_source: 'ddi_direct', photos_required: 14, photos_submitted: 0, condition_code: '', due_date: '03/22/2026', recurring: false, fee: 350, notes: 'Full preservation — lock change, board-up rear, debris clear, lawn initial cut. HUD FSM compliance.', created_at: '2026-03-21T09:00:00' },
];

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
const PRISMSystem: React.FC<PRISMSystemProps> = ({ onBackToNexus, onNavigate, activeTab, setActiveTab }) => {
  const [activeDivision, setActiveDivision] = useState<string | null>(null);
  const [divisionSection, setDivisionSection] = useState<'overview' | 'orders' | 'agents' | 'scanbacks'>('overview');
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
  const [propertyOrders] = useState<PropertyWorkOrder[]>(MOCK_PROPERTY_ORDERS);

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

  const exitDivision = () => {
    setActiveDivision(null);
    setActiveTab('dashboard');
    setSelectedOrder(null);
  };

  const currentDivision = PRISM_DIVISIONS.find(d => d.id === activeDivision);

  const getDivisionOrders = (div: PrismDivision) => orders.filter(o => div.types.includes(o.type));
  const getDivisionAgents = (div: PrismDivision) => agents.filter(a => a.specialties?.some(s => div.agentSpecialties.some(ds => s.toLowerCase().includes(ds.toLowerCase()))) || div.types.some(t => a.specialties?.map(s => s.toLowerCase()).includes(t)));
  const getDivisionScanbacks = (div: PrismDivision) => scanbacks.filter(s => div.types.includes(s.type));

  const [orders, setOrders] = useState<PrismOrder[]>([]);
  const [agents, setAgents] = useState<PrismAgent[]>([]);
  const [clients, setClients] = useState<PrismClient[]>([]);
  const [prismStats, setPrismStats] = useState<any>(null);
  const [dataLoading, setDataLoading] = useState(true);
  const [notifications, setNotifications] = useState<any[]>([]);
  const [showNotifPanel, setShowNotifPanel] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);

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

  return (
    <div className="min-h-screen">
      {/* ─── TABS ───────────────────────────────────────── */}
      <div className="bg-gray-800 border-b border-gray-700 sticky top-[73px] z-40">
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex gap-1 overflow-x-auto py-1 items-center">
            {activeDivision && currentDivision && (
              <button onClick={exitDivision} className="flex items-center gap-1.5 px-3 py-2 text-sm font-semibold rounded-t-lg transition text-gray-400 hover:text-white hover:bg-gray-700 mr-1 border-r border-gray-700 pr-3">
                ← Hub
              </button>
            )}
            {activeDivision && currentDivision && (
              <div className="flex items-center gap-2 mr-3 pr-3 border-r border-gray-700">
                <span className="text-lg">{currentDivision.icon}</span>
                <span className="text-sm font-bold" style={{ color: currentDivision.color }}>{currentDivision.name}</span>
              </div>
            )}
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-4 py-3 text-sm font-semibold rounded-t-lg transition whitespace-nowrap ${
                  activeTab === tab.id
                    ? activeDivision && currentDivision
                      ? 'text-white'
                      : 'bg-gradient-to-r from-orange-500 to-amber-500 text-white'
                    : 'text-gray-400 hover:text-white hover:bg-gray-700'
                }`}
                style={activeTab === tab.id && activeDivision && currentDivision ? { backgroundColor: currentDivision.solid } : {}}
              >
                {tab.label}
                {tab.id === 'scanbacks' && needsReview.length > 0 && (
                  <span className="ml-1.5 px-1.5 py-0.5 rounded-full text-[10px] font-bold bg-red-500 text-white animate-pulse">{needsReview.length}</span>
                )}
                {tab.id === 'orders' && orders.length > 0 && (
                  <span className="ml-1.5 px-1.5 py-0.5 rounded-full text-[10px] font-bold bg-white/20">{orders.length}</span>
                )}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* ─── CONTENT ────────────────────────────────────── */}
      <div className="max-w-7xl mx-auto px-6 py-6">

        {/* ════════════════════════════════════════════════════
            DIVISION HUB — Main PRISM Landing
        ════════════════════════════════════════════════════ */}
        {!activeDivision && activeTab === 'dashboard' && (
          <div>
            <div className="mb-6 flex items-center justify-between">
              <div>
                <h2 className="text-3xl font-bold mb-1">🎯 PRISM Command Center</h2>
                <p className="text-gray-400">See every detail. Miss nothing. — Select a division.</p>
              </div>
              <div className="flex gap-2 items-center">
                <button onClick={() => setShowNotifPanel(!showNotifPanel)}
                  className="relative text-gray-400 hover:text-white transition bg-gray-700 hover:bg-gray-600 px-3 py-2 rounded-lg">
                  🔔
                  {unreadCount > 0 && (
                    <span className="absolute -top-1 -right-1 bg-red-500 text-white text-[10px] font-bold rounded-full w-5 h-5 flex items-center justify-center">
                      {unreadCount > 9 ? '9+' : unreadCount}
                    </span>
                  )}
                </button>
                <button onClick={() => setShowNewOrderModal(true)} className="bg-orange-500 hover:bg-orange-600 px-4 py-2 rounded-lg font-semibold text-sm transition">
                  + New Order
                </button>
              </div>
            </div>

            {/* Cross-Division Summary */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
              <StatCard label="Total Active Orders" value={activeOrders.length} icon="📋" color="orange" sub="All divisions" />
              <StatCard label="Today's Appointments" value={todayOrders.length} icon="📅" color="blue" sub="Across all divisions" />
              <StatCard label="Awaiting Scanback" value={awaitingScanback.length} icon="📸" color="yellow" sub="Service done, no upload" />
              <StatCard label="Errors Found" value={errorsFound.length} icon="🚨" color="red" sub="Need correction" />
            </div>

            {/* Sub / agent credentialing quote (API-backed) */}
            <div className="mb-8 rounded-2xl border border-teal-500/35 bg-gradient-to-br from-teal-500/10 to-gray-900/80 overflow-hidden">
              <button
                type="button"
                onClick={() => setCredentialingOpen(v => !v)}
                className="w-full flex items-center justify-between gap-3 px-5 py-4 text-left hover:bg-teal-500/10 transition"
              >
                <div>
                  <h3 className="font-bold text-white text-base">🎓 Sub credentialing fees</h3>
                  <p className="text-sm text-gray-400 mt-0.5">Quote DDI credentialing (NALI / Quest / NCS) — subs pay DDI, not the other way around.</p>
                </div>
                <span className="text-teal-400 font-semibold text-sm shrink-0">{credentialingOpen ? 'Hide ▲' : 'Expand ▼'}</span>
              </button>
              {credentialingOpen && (
                <div className="px-5 pb-5 border-t border-teal-500/20">
                  {credentialingLoad === 'loading' && <p className="text-gray-400 text-sm py-4">Loading fee catalog…</p>}
                  {credentialingLoad === 'error' && <p className="text-red-400 text-sm py-4">Could not load /prism/router/credentialing-pricing. Is the API server running?</p>}
                  {credentialingLoad === 'ok' && credentialingCatalog && (
                    <div className="pt-4 space-y-4">
                      {credentialingCatalog.policy && (
                        <p className="text-xs text-gray-500 leading-relaxed">{String(credentialingCatalog.policy)}</p>
                      )}
                      <div className="flex flex-wrap gap-2">
                        {(['package', 'bundles', 'credentials'] as const).map(m => (
                          <button
                            key={m}
                            type="button"
                            onClick={() => { setCredQuoteMode(m); setCredQuoteResult(null); }}
                            className={`px-3 py-1.5 rounded-lg text-sm font-semibold transition ${
                              credQuoteMode === m ? 'bg-teal-600 text-white' : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                            }`}
                          >
                            {m === 'package' ? 'Full package' : m === 'bundles' ? 'Bundles' : 'À la carte'}
                          </button>
                        ))}
                      </div>

                      {credQuoteMode === 'package' && credentialingCatalog.full_packages && (
                        <div>
                          <label className="text-xs text-gray-500 uppercase font-bold block mb-1">Full package</label>
                          <select
                            value={selectedFullPackage}
                            onChange={e => setSelectedFullPackage(e.target.value)}
                            className="w-full max-w-md bg-gray-800 border border-gray-600 rounded-lg px-3 py-2 text-sm text-white"
                          >
                            {Object.keys(credentialingCatalog.full_packages).map(pid => (
                              <option key={pid} value={pid}>{pid.replace(/_/g, ' ')}</option>
                            ))}
                          </select>
                        </div>
                      )}

                      {credQuoteMode === 'bundles' && credentialingCatalog.bundles && (
                        <div className="max-h-48 overflow-y-auto space-y-2 pr-1">
                          {Object.entries(credentialingCatalog.bundles).map(([bid, row]) => {
                            const label = (row as { label?: string })?.label || bid;
                            const fee = (row as { ddi_credentialing_fee?: number })?.ddi_credentialing_fee;
                            return (
                              <label key={bid} className="flex items-start gap-2 cursor-pointer text-sm text-gray-300 hover:text-white">
                                <input
                                  type="checkbox"
                                  checked={selectedBundleIds.includes(bid)}
                                  onChange={() => toggleCredBundle(bid)}
                                  className="mt-1 rounded border-gray-500"
                                />
                                <span><span className="font-semibold text-white">{label}</span> <span className="text-teal-400">${fee}</span></span>
                              </label>
                            );
                          })}
                        </div>
                      )}

                      {credQuoteMode === 'credentials' && credentialingCatalog.credentials && (
                        <div>
                          <label className="text-xs text-gray-500 uppercase font-bold block mb-1">Credentials (multi-select)</label>
                          <select
                            multiple
                            size={8}
                            value={selectedCredKeys}
                            onChange={e => {
                              const opts = Array.from(e.target.selectedOptions).map(o => o.value);
                              setSelectedCredKeys(opts);
                            }}
                            className="w-full max-w-lg bg-gray-800 border border-gray-600 rounded-lg px-2 py-2 text-sm text-white font-mono"
                          >
                            {Object.keys(credentialingCatalog.credentials).sort().map(ck => (
                              <option key={ck} value={ck}>{ck}</option>
                            ))}
                          </select>
                          <p className="text-[11px] text-gray-500 mt-1">Hold Cmd/Ctrl to select multiple.</p>
                        </div>
                      )}

                      <div className="flex flex-wrap items-center gap-3">
                        <button
                          type="button"
                          disabled={credQuoteLoading}
                          onClick={() => void runCredentialQuote()}
                          className="bg-teal-600 hover:bg-teal-500 disabled:opacity-50 px-4 py-2 rounded-lg font-semibold text-sm text-white"
                        >
                          {credQuoteLoading ? 'Quoting…' : 'Get quote'}
                        </button>
                      </div>

                      {credQuoteResult && (
                        <div className={`rounded-xl border px-4 py-3 text-sm ${credQuoteResult.error ? 'border-red-500/40 bg-red-500/10' : 'border-teal-500/40 bg-teal-500/10'}`}>
                          {credQuoteResult.error ? (
                            <p className="text-red-300 font-semibold">{String(credQuoteResult.error)}</p>
                          ) : (
                            <div className="space-y-2 text-gray-200">
                              <p className="text-lg font-bold text-white">
                                DDI credentialing total:{' '}
                                <span className="text-teal-400">${String(credQuoteResult.ddi_credentialing_fee_total ?? '—')}</span>
                              </p>
                              {credQuoteResult.mode === 'full_package' && credQuoteResult.package_savings_vs_separate_bundles != null && Number(credQuoteResult.package_savings_vs_separate_bundles) > 0 && (
                                <p className="text-xs text-teal-200/90">
                                  Package savings vs buying bundles separately: ${String(credQuoteResult.package_savings_vs_separate_bundles)}
                                </p>
                              )}
                              {Array.isArray(credQuoteResult.bundles_in_package) && (
                                <ul className="text-xs text-gray-400 list-disc list-inside">
                                  {(credQuoteResult.bundles_in_package as { label?: string; ddi_credentialing_fee?: number }[]).map((b, i) => (
                                    <li key={i}>{b.label} — ${b.ddi_credentialing_fee}</li>
                                  ))}
                                </ul>
                              )}
                              {Array.isArray(credQuoteResult.bundles) && credQuoteResult.mode === 'bundles' && (
                                <ul className="text-xs text-gray-400 list-disc list-inside">
                                  {(credQuoteResult.bundles as { label?: string; ddi_credentialing_fee?: number }[]).map((b, i) => (
                                    <li key={i}>{b.label} — ${b.ddi_credentialing_fee}</li>
                                  ))}
                                </ul>
                              )}
                              {Array.isArray(credQuoteResult.breakdown) && (
                                <ul className="text-xs text-gray-400 list-disc list-inside max-h-32 overflow-y-auto font-mono">
                                  {(credQuoteResult.breakdown as { credential?: string; ddi_credentialing_fee?: number | null }[]).map((row, i) => (
                                    <li key={i}>{row.credential}: {row.ddi_credentialing_fee != null ? `$${row.ddi_credentialing_fee}` : '—'}</li>
                                  ))}
                                </ul>
                              )}
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Division Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5 mb-8">
              {PRISM_DIVISIONS.map(div => {
                const divOrders = div.id === 'field_ops' ? propertyOrders : getDivisionOrders(div);
                const divActive = div.id === 'field_ops'
                  ? propertyOrders.filter(p => !['complete'].includes(p.status)).length
                  : (divOrders as PrismOrder[]).filter(o => !['Closed', 'Verified'].includes(o.status)).length;
                const divErrors = div.id === 'field_ops'
                  ? propertyOrders.filter(p => p.status === 'rejected').length
                  : getDivisionScanbacks(div).filter(s => s.status === 'Errors Found').length;
                const divToday = div.id === 'field_ops'
                  ? 0
                  : (divOrders as PrismOrder[]).filter(o => o.date === today).length;
                const divUnassigned = div.id === 'field_ops'
                  ? propertyOrders.filter(p => !p.assigned_to).length
                  : (divOrders as PrismOrder[]).filter(o => o.status === 'New').length;
                const divAwaitingScanback = div.id === 'field_ops'
                  ? 0
                  : getDivisionScanbacks(div).filter(s => s.status === 'Awaiting Upload').length;
                const needsAttention = divErrors + divUnassigned + divAwaitingScanback;

                return (
                  <div key={div.id}
                    onClick={() => enterDivision(div.id)}
                    className="group relative cursor-pointer rounded-2xl border-2 overflow-hidden transition-all hover:scale-[1.02] hover:shadow-2xl"
                    style={{ borderColor: div.color + '40', background: `linear-gradient(135deg, ${div.solid}15 0%, ${div.color}08 100%)` }}>
                    {needsAttention > 0 && (
                      <div className="absolute top-3 right-3 flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-bold animate-pulse"
                        style={{ backgroundColor: '#EF444430', color: '#EF4444', border: '1px solid #EF444450' }}>
                        ⚠ {needsAttention}
                      </div>
                    )}
                    <div className="p-6">
                      <div className="flex items-center gap-3 mb-3">
                        <span className="text-3xl">{div.icon}</span>
                        <div>
                          <h3 className="text-lg font-bold text-white group-hover:text-opacity-100">{div.name}</h3>
                          <p className="text-[11px] text-gray-500 leading-tight">{div.subtitle}</p>
                        </div>
                      </div>
                      <div className="grid grid-cols-3 gap-3 mt-4">
                        <div className="text-center">
                          <p className="text-2xl font-bold" style={{ color: div.color }}>{divActive}</p>
                          <p className="text-[10px] text-gray-500 uppercase font-semibold">Active</p>
                        </div>
                        <div className="text-center">
                          <p className="text-2xl font-bold text-blue-400">{divToday}</p>
                          <p className="text-[10px] text-gray-500 uppercase font-semibold">Today</p>
                        </div>
                        <div className="text-center">
                          <p className={`text-2xl font-bold ${divErrors > 0 ? 'text-red-400' : 'text-green-400'}`}>{divErrors > 0 ? divErrors : '✓'}</p>
                          <p className="text-[10px] text-gray-500 uppercase font-semibold">{divErrors > 0 ? 'Errors' : 'Clean'}</p>
                        </div>
                      </div>
                      {/* Status tags */}
                      <div className="flex flex-wrap gap-1.5 mt-4">
                        {divUnassigned > 0 && (
                          <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-yellow-500/20 text-yellow-400 border border-yellow-500/30">
                            {divUnassigned} unassigned
                          </span>
                        )}
                        {divAwaitingScanback > 0 && (
                          <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-orange-500/20 text-orange-400 border border-orange-500/30">
                            {divAwaitingScanback} awaiting scanback
                          </span>
                        )}
                        {divErrors > 0 && (
                          <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-red-500/20 text-red-400 border border-red-500/30">
                            {divErrors} errors
                          </span>
                        )}
                        {needsAttention === 0 && divActive > 0 && (
                          <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-green-500/20 text-green-400 border border-green-500/30">
                            All clear
                          </span>
                        )}
                        {divActive === 0 && (
                          <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-gray-500/20 text-gray-500 border border-gray-500/30">
                            No active orders
                          </span>
                        )}
                      </div>
                    </div>
                    <div className="h-1.5 w-full transition-all group-hover:h-2" style={{ backgroundColor: div.color }} />
                  </div>
                );
              })}
            </div>

            {/* Cross-Division Needs Attention */}
            {(errorsFound.length > 0 || unassigned.length > 0) && (
              <div className="mb-8">
                <h3 className="text-lg font-bold mb-3 text-red-400">⚠️ Needs Your Attention — All Divisions</h3>
                <div className="space-y-2">
                  {errorsFound.slice(0, 5).map(o => {
                    const matchDiv = PRISM_DIVISIONS.find(d => d.types.includes(o.type));
                    return (
                      <div key={o.id} className="flex items-center justify-between bg-red-500/10 border border-red-500/30 rounded-lg px-4 py-3 hover:bg-red-500/15 transition cursor-pointer"
                        onClick={() => matchDiv && enterDivision(matchDiv.id)}>
                        <div className="flex items-center gap-3">
                          <span className="text-red-400 font-bold text-sm">ERRORS</span>
                          <ServiceBadge type={o.type} />
                          <span className="text-sm">{o.orderId}</span>
                          <span className="text-gray-400 text-sm">— {o.agent}</span>
                        </div>
                        <span className="text-red-400 text-sm font-semibold">{matchDiv?.name} →</span>
                      </div>
                    );
                  })}
                  {unassigned.slice(0, 5).map(o => {
                    const matchDiv = PRISM_DIVISIONS.find(d => d.types.includes(o.type));
                    return (
                      <div key={o.id} className="flex items-center justify-between bg-yellow-500/10 border border-yellow-500/30 rounded-lg px-4 py-3 hover:bg-yellow-500/15 transition cursor-pointer"
                        onClick={() => matchDiv && enterDivision(matchDiv.id)}>
                        <div className="flex items-center gap-3">
                          <span className="text-yellow-400 font-bold text-sm">UNASSIGNED</span>
                          <ServiceBadge type={o.type} />
                          <span className="text-sm">{o.id}</span>
                          <span className="text-gray-400 text-sm">— {o.client}</span>
                        </div>
                        <span className="text-yellow-400 text-sm font-semibold">{matchDiv?.name} →</span>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* Agent Leaderboard (cross-division) */}
            <div>
              <h3 className="text-lg font-bold mb-3">🏆 Top Agents — All Divisions</h3>
              <div className="bg-gray-800 border border-gray-700 rounded-xl overflow-hidden">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-gray-700 text-gray-400 text-xs uppercase">
                      <th className="text-left px-4 py-3">#</th>
                      <th className="text-left px-4 py-3">Agent</th>
                      <th className="text-center px-4 py-3">Specialties</th>
                      <th className="text-center px-4 py-3">Orders</th>
                      <th className="text-center px-4 py-3">On-Time</th>
                      <th className="text-center px-4 py-3">Rating</th>
                    </tr>
                  </thead>
                  <tbody>
                    {agents
                      .filter(a => a.status === 'Active')
                      .sort((a, b) => b.ordersCompleted - a.ordersCompleted)
                      .slice(0, 8)
                      .map((agent, i) => (
                        <tr key={agent.id} className="border-b border-gray-700/50 hover:bg-gray-700/30 transition">
                          <td className="px-4 py-3 font-bold text-gray-500">{i + 1}</td>
                          <td className="px-4 py-3 font-semibold">{agent.name}</td>
                          <td className="text-center px-4 py-3">
                            <div className="flex flex-wrap gap-1 justify-center">
                              {(agent.specialties || []).slice(0, 2).map((s, si) => (
                                <span key={si} className="text-[10px] px-1.5 py-0.5 rounded-full bg-gray-700 text-gray-400">{s}</span>
                              ))}
                            </div>
                          </td>
                          <td className="text-center px-4 py-3">{agent.ordersCompleted}</td>
                          <td className="text-center px-4 py-3 text-blue-400">{agent.onTimeRate}%</td>
                          <td className="text-center px-4 py-3 text-yellow-400">⭐ {agent.rating}</td>
                        </tr>
                      ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* ════════════════════════════════════════════════════
            DIVISION VIEW — Focused single-division page
        ════════════════════════════════════════════════════ */}
        {activeDivision && currentDivision && activeTab === 'dashboard' && currentDivision.id !== 'field_ops' && (() => {
          const div = currentDivision;
          const divOrders = getDivisionOrders(div);
          const divAgents = getDivisionAgents(div);
          const divScanbacks = getDivisionScanbacks(div);
          const divActive = divOrders.filter(o => !['Closed', 'Verified'].includes(o.status));
          const divToday = divOrders.filter(o => o.date === today);
          const divErrors = divScanbacks.filter(s => s.status === 'Errors Found');
          const divUnassigned = divOrders.filter(o => o.status === 'New');
          const divAwaitingScanback = divScanbacks.filter(s => s.status === 'Awaiting Upload');
          const divNeedsReview = divScanbacks.filter(s => s.status === 'Needs Review');
          const divRevenue = divOrders.reduce((sum, o) => sum + (o.fee || 0), 0);
          const divInspection = div.types.map(t => SERVICE_INSPECTION[t]).filter(Boolean);

          return (
            <div>
              {/* Division Header */}
              <div className="mb-6">
                <button onClick={exitDivision} className="flex items-center gap-2 text-gray-400 hover:text-white text-sm mb-3 transition">
                  ← Back to PRISM Hub
                </button>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="w-14 h-14 rounded-2xl flex items-center justify-center text-3xl" style={{ backgroundColor: div.color + '20', border: `2px solid ${div.color}50` }}>
                      {div.icon}
                    </div>
                    <div>
                      <h2 className="text-2xl font-bold">{div.name}</h2>
                      <p className="text-sm text-gray-500">{div.subtitle}</p>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <button onClick={() => setShowNewOrderModal(true)} className="px-4 py-2 rounded-lg font-semibold text-sm transition text-white" style={{ backgroundColor: div.solid }}>
                      + New Order
                    </button>
                  </div>
                </div>
              </div>

              {/* Division Section Nav */}
              <div className="flex gap-1 bg-gray-800 rounded-xl p-1 mb-6 border border-gray-700">
                {[
                  { id: 'overview' as const, label: 'Overview', icon: '🎯' },
                  { id: 'orders' as const, label: `Orders (${divActive.length})`, icon: '📋' },
                  { id: 'agents' as const, label: `Agents (${divAgents.length})`, icon: '👤' },
                  { id: 'scanbacks' as const, label: `Scanbacks${divErrors.length > 0 ? ` (${divErrors.length} errors)` : ''}`, icon: '📸' },
                ].map(sec => (
                  <button key={sec.id} onClick={() => setDivisionSection(sec.id)}
                    className={`flex-1 px-4 py-2.5 rounded-lg text-sm font-semibold transition ${
                      divisionSection === sec.id
                        ? 'text-white shadow-lg'
                        : 'text-gray-400 hover:text-white hover:bg-gray-700'
                    }`}
                    style={divisionSection === sec.id ? { backgroundColor: div.solid } : {}}>
                    {sec.icon} {sec.label}
                  </button>
                ))}
              </div>

              {/* OVERVIEW */}
              {divisionSection === 'overview' && (
                <div className="space-y-6">
                  {/* Stats */}
                  <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
                    <StatCard label="Active" value={divActive.length} icon={div.icon} color="orange" />
                    <StatCard label="Today" value={divToday.length} icon="📅" color="blue" />
                    <StatCard label="Errors" value={divErrors.length} icon="🚨" color="red" />
                    <StatCard label="Awaiting Scanback" value={divAwaitingScanback.length} icon="📸" color="yellow" />
                    <StatCard label="Revenue" value={`$${divRevenue.toLocaleString()}`} icon="💰" color="green" />
                  </div>

                  {/* Needs Attention */}
                  {(divErrors.length > 0 || divUnassigned.length > 0 || divNeedsReview.length > 0 || divAwaitingScanback.length > 0) && (
                    <div className="rounded-xl border-2 p-5" style={{ borderColor: '#EF444440', backgroundColor: '#EF444408' }}>
                      <h3 className="text-base font-bold text-red-400 mb-3">⚠️ Needs Your Attention</h3>
                      <div className="space-y-2">
                        {divErrors.map(s => (
                          <div key={s.id} className="flex items-center justify-between bg-red-500/10 border border-red-500/30 rounded-lg px-4 py-2.5 cursor-pointer hover:bg-red-500/15 transition"
                            onClick={() => setDivisionSection('scanbacks')}>
                            <div className="flex items-center gap-3">
                              <span className="text-red-400 font-bold text-xs">ERRORS</span>
                              <span className="text-sm">{s.orderId}</span>
                              <span className="text-gray-500 text-sm">{s.agent}</span>
                            </div>
                            <span className="text-red-400 text-xs font-semibold">Review →</span>
                          </div>
                        ))}
                        {divUnassigned.map(o => (
                          <div key={o.id} className="flex items-center justify-between bg-yellow-500/10 border border-yellow-500/30 rounded-lg px-4 py-2.5 cursor-pointer hover:bg-yellow-500/15 transition"
                            onClick={() => setDivisionSection('orders')}>
                            <div className="flex items-center gap-3">
                              <span className="text-yellow-400 font-bold text-xs">UNASSIGNED</span>
                              <ServiceBadge type={o.type} />
                              <span className="text-sm">{o.id}</span>
                            </div>
                            <span className="text-yellow-400 text-xs font-semibold">Assign →</span>
                          </div>
                        ))}
                        {divAwaitingScanback.map(s => (
                          <div key={s.id} className="flex items-center justify-between bg-orange-500/10 border border-orange-500/30 rounded-lg px-4 py-2.5 cursor-pointer hover:bg-orange-500/15 transition"
                            onClick={() => setDivisionSection('scanbacks')}>
                            <div className="flex items-center gap-3">
                              <span className="text-orange-400 font-bold text-xs">SCANBACK</span>
                              <span className="text-sm">{s.orderId}</span>
                              <span className="text-gray-500 text-sm">{s.agent}</span>
                            </div>
                            <span className="text-orange-400 text-xs font-semibold">Awaiting →</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Today's Schedule */}
                  <div>
                    <h3 className="text-base font-bold mb-3">📅 Today's Schedule</h3>
                    {divToday.length > 0 ? (
                      <div className="space-y-2">
                        {divToday.sort((a, b) => a.time.localeCompare(b.time)).map(order => {
                          const svc = SERVICE_COLORS[order.type];
                          return (
                            <div key={order.id} className="flex items-center gap-4 border rounded-lg px-4 py-3 hover:brightness-110 transition cursor-pointer"
                              style={{ borderLeftWidth: '5px', borderLeftColor: div.color, backgroundColor: div.color + '10', borderColor: div.color + '30' }}
                              onClick={() => { setSelectedOrder(order.id); setDivisionSection('orders'); }}>
                              <span className="text-sm font-mono font-bold w-20" style={{ color: div.color }}>{order.time}</span>
                              <ServiceBadge type={order.type} />
                              <span className="text-sm font-semibold flex-1">{order.signer}</span>
                              <span className="text-sm text-gray-400 truncate max-w-[200px]">{order.address}</span>
                              <span className="text-sm text-gray-500">{order.agent || 'Unassigned'}</span>
                            </div>
                          );
                        })}
                      </div>
                    ) : (
                      <div className="text-center py-6 text-gray-500 bg-gray-800/50 rounded-xl border border-gray-700">
                        <p className="text-sm">No {div.name.toLowerCase()} appointments today</p>
                      </div>
                    )}
                  </div>

                  {/* Recent Orders */}
                  <div>
                    <div className="flex items-center justify-between mb-3">
                      <h3 className="text-base font-bold">Recent Orders</h3>
                      <button onClick={() => setDivisionSection('orders')} className="text-xs font-semibold hover:text-white transition" style={{ color: div.color }}>
                        View All →
                      </button>
                    </div>
                    <div className="bg-gray-800 border border-gray-700 rounded-xl overflow-hidden">
                      <table className="w-full text-sm">
                        <thead>
                          <tr className="border-b border-gray-700 text-gray-400 text-xs uppercase">
                            <th className="text-left px-4 py-2">Order</th>
                            <th className="text-left px-4 py-2">Type</th>
                            <th className="text-left px-4 py-2">Status</th>
                            <th className="text-left px-4 py-2">Agent</th>
                            <th className="text-left px-4 py-2">Subject</th>
                            <th className="text-right px-4 py-2">Fee</th>
                          </tr>
                        </thead>
                        <tbody>
                          {divOrders.slice(0, 8).map(order => {
                            const svc = SERVICE_COLORS[order.type];
                            return (
                              <tr key={order.id} className="border-b border-gray-700/50 hover:bg-gray-700/30 transition cursor-pointer"
                                style={{ borderLeftWidth: '4px', borderLeftColor: svc?.color || div.color }}
                                onClick={() => { setSelectedOrder(order.id); setDivisionSection('orders'); }}>
                                <td className="px-4 py-2.5 font-mono text-xs">{order.id}</td>
                                <td className="px-4 py-2.5"><ServiceBadge type={order.type} /></td>
                                <td className="px-4 py-2.5"><StatusBadge status={order.status} /></td>
                                <td className="px-4 py-2.5 text-sm">{order.agent || <span className="text-yellow-400 text-xs">UNASSIGNED</span>}</td>
                                <td className="px-4 py-2.5 text-sm text-gray-300">{order.signer}</td>
                                <td className="px-4 py-2.5 text-right font-semibold text-green-400">${order.fee}</td>
                              </tr>
                            );
                          })}
                        </tbody>
                      </table>
                    </div>
                  </div>

                  {/* Division Agents */}
                  {divAgents.length > 0 && (
                    <div>
                      <div className="flex items-center justify-between mb-3">
                        <h3 className="text-base font-bold">👤 Division Agents</h3>
                        <button onClick={() => setDivisionSection('agents')} className="text-xs font-semibold hover:text-white transition" style={{ color: div.color }}>
                          View All →
                        </button>
                      </div>
                      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                        {divAgents.slice(0, 6).map(agent => (
                          <div key={agent.id} className="bg-gray-800 border border-gray-700 rounded-xl p-4 hover:border-gray-600 transition">
                            <div className="flex items-center justify-between mb-2">
                              <span className="font-semibold text-sm">{agent.name}</span>
                              <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${agent.status === 'Active' ? 'bg-green-500/20 text-green-400' : 'bg-gray-500/20 text-gray-400'}`}>
                                {agent.status}
                              </span>
                            </div>
                            <div className="flex items-center gap-4 text-xs text-gray-400">
                              <span>📦 {agent.ordersCompleted} completed</span>
                              <span>⭐ {agent.rating}</span>
                              <span className={agent.errorRate <= 2 ? 'text-green-400' : 'text-yellow-400'}>{agent.errorRate}% errors</span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Compliance Quick Ref */}
                  {divInspection.length > 0 && (
                    <div>
                      <h3 className="text-base font-bold mb-3">🔍 Compliance Quick Reference</h3>
                      <div className="space-y-3">
                        {divInspection.map(insp => (
                          <div key={insp.title} className="bg-gray-800 border border-gray-700 rounded-xl p-4">
                            <h4 className="text-sm font-bold mb-2" style={{ color: div.color }}>{insp.title}</h4>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                              {insp.fundamentals.filter(f => f.severity === 'FATAL').slice(0, 4).map(f => (
                                <div key={f.id} className="flex items-start gap-2 text-xs">
                                  <span className="px-1.5 py-0.5 rounded bg-red-600 text-white text-[9px] font-bold flex-shrink-0">FATAL</span>
                                  <span className="text-gray-300">{f.check}</span>
                                </div>
                              ))}
                            </div>
                            <div className="mt-2 pt-2 border-t border-gray-700">
                              <p className="text-[10px] text-gray-500">Required certs: {insp.certs.join(' • ')}</p>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* ORDERS (within division) */}
              {divisionSection === 'orders' && (
                <div>
                  <div className="bg-gray-800 border border-gray-700 rounded-xl overflow-hidden">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="border-b border-gray-700 text-gray-400 text-xs uppercase">
                          <th className="text-left px-4 py-3">Order</th>
                          <th className="text-left px-4 py-3">Service</th>
                          <th className="text-left px-4 py-3">Status</th>
                          <th className="text-left px-4 py-3">Agent</th>
                          <th className="text-left px-4 py-3">Client / Subject</th>
                          <th className="text-left px-4 py-3">Date</th>
                          <th className="text-right px-4 py-3">Fee</th>
                        </tr>
                      </thead>
                      <tbody>
                        {divOrders.map(order => {
                          const svc = SERVICE_COLORS[order.type];
                          const isSelected = selectedOrder === order.id;
                          return (
                            <tr key={order.id}
                              className={`border-b border-gray-700/50 hover:brightness-110 transition cursor-pointer ${isSelected ? 'ring-2 ring-inset' : ''}`}
                              style={{ borderLeftWidth: '5px', borderLeftColor: svc?.color || div.color, backgroundColor: isSelected ? svc?.color + '30' : svc?.color + '10' }}
                              onClick={() => setSelectedOrder(isSelected ? null : order.id)}>
                              <td className="px-4 py-3">
                                <span className="font-mono text-xs">{order.id}</span>
                                {order.priority !== 'Standard' && (
                                  <span className={`ml-1.5 px-1.5 py-0.5 rounded text-[9px] font-bold ${order.priority === 'STAT' ? 'bg-red-500/20 text-red-400' : 'bg-yellow-500/20 text-yellow-400'}`}>
                                    {order.priority}
                                  </span>
                                )}
                              </td>
                              <td className="px-4 py-3"><ServiceBadge type={order.type} /></td>
                              <td className="px-4 py-3"><StatusBadge status={order.status} /></td>
                              <td className="px-4 py-3">{order.agent || <span className="text-yellow-400 text-xs font-semibold">UNASSIGNED</span>}</td>
                              <td className="px-4 py-3">
                                <div className="text-gray-300 text-sm">{order.client}</div>
                                <div className="text-gray-500 text-xs">{order.signer}</div>
                              </td>
                              <td className="px-4 py-3 text-gray-400 text-xs">{order.date}<br/><span className="text-gray-500">{order.time}</span></td>
                              <td className="px-4 py-3 text-right font-semibold text-green-400">${order.fee}</td>
                            </tr>
                          );
                        })}
                        {divOrders.length === 0 && (
                          <tr><td colSpan={7} className="text-center py-8 text-gray-500">No orders in this division</td></tr>
                        )}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {/* AGENTS (within division) */}
              {divisionSection === 'agents' && (
                <div className="space-y-4">
                  {divAgents.length > 0 ? divAgents.map(agent => (
                    <div key={agent.id} className="bg-gray-800 border border-gray-700 rounded-xl p-5 hover:border-gray-600 transition">
                      <div className="flex items-center justify-between mb-3">
                        <div>
                          <h4 className="font-bold text-lg">{agent.name}</h4>
                          <p className="text-sm text-gray-400">{agent.city}, {agent.state}</p>
                        </div>
                        <span className={`px-3 py-1 rounded-full text-xs font-bold ${agent.status === 'Active' ? 'bg-green-500/20 text-green-400 border border-green-500/30' : 'bg-gray-500/20 text-gray-400 border border-gray-500/30'}`}>
                          {agent.status}
                        </span>
                      </div>
                      <div className="grid grid-cols-5 gap-4 text-center">
                        <div>
                          <p className="text-xl font-bold text-white">{agent.ordersCompleted}</p>
                          <p className="text-[10px] text-gray-500 uppercase">Completed</p>
                        </div>
                        <div>
                          <p className="text-xl font-bold text-blue-400">{agent.activeOrders}</p>
                          <p className="text-[10px] text-gray-500 uppercase">Active</p>
                        </div>
                        <div>
                          <p className="text-xl font-bold text-green-400">{agent.completionRate}%</p>
                          <p className="text-[10px] text-gray-500 uppercase">Completion</p>
                        </div>
                        <div>
                          <p className="text-xl font-bold text-blue-400">{agent.onTimeRate}%</p>
                          <p className="text-[10px] text-gray-500 uppercase">On-Time</p>
                        </div>
                        <div>
                          <p className={`text-xl font-bold ${agent.errorRate <= 2 ? 'text-green-400' : agent.errorRate <= 5 ? 'text-yellow-400' : 'text-red-400'}`}>{agent.errorRate}%</p>
                          <p className="text-[10px] text-gray-500 uppercase">Error Rate</p>
                        </div>
                      </div>
                      <div className="flex flex-wrap gap-1.5 mt-3">
                        {(agent.specialties || []).map((s, i) => (
                          <span key={i} className="text-[10px] px-2 py-0.5 rounded-full border" style={{ backgroundColor: div.color + '15', borderColor: div.color + '30', color: div.color }}>{s}</span>
                        ))}
                      </div>
                    </div>
                  )) : (
                    <div className="text-center py-12 text-gray-500 bg-gray-800/50 rounded-xl border border-gray-700">
                      <p>No agents assigned to this division yet</p>
                    </div>
                  )}
                </div>
              )}

              {/* SCANBACKS (within division) */}
              {divisionSection === 'scanbacks' && (
                <div>
                  <div className="flex gap-2 mb-4">
                    {['all', 'Awaiting Upload', 'Needs Review', 'Errors Found', 'Clean'].map(f => (
                      <button key={f} onClick={() => setScanbackFilter(f)}
                        className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition border ${
                          scanbackFilter === f ? 'text-white border-opacity-60' : 'bg-gray-800 border-gray-700 text-gray-400 hover:text-white'
                        }`}
                        style={scanbackFilter === f ? { backgroundColor: div.solid, borderColor: div.color } : {}}>
                        {f === 'all' ? 'All' : f}
                      </button>
                    ))}
                  </div>
                  <div className="bg-gray-800 border border-gray-700 rounded-xl overflow-hidden">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="border-b border-gray-700 text-gray-400 text-xs uppercase">
                          <th className="text-left px-4 py-3">Order</th>
                          <th className="text-left px-4 py-3">Type</th>
                          <th className="text-left px-4 py-3">Agent</th>
                          <th className="text-left px-4 py-3">Status</th>
                          <th className="text-center px-4 py-3">Pages</th>
                          <th className="text-center px-4 py-3">Errors</th>
                          <th className="text-left px-4 py-3">Uploaded</th>
                        </tr>
                      </thead>
                      <tbody>
                        {(scanbackFilter === 'all' ? divScanbacks : divScanbacks.filter(s => s.status === scanbackFilter)).map(sb => {
                          const svc = SERVICE_COLORS[sb.type];
                          return (
                            <tr key={sb.id} className="border-b border-gray-700/50 hover:bg-gray-700/30 transition cursor-pointer"
                              style={{ borderLeftWidth: '4px', borderLeftColor: svc?.color || div.color }}>
                              <td className="px-4 py-3 font-mono text-xs">{sb.orderId}</td>
                              <td className="px-4 py-3"><ServiceBadge type={sb.type} /></td>
                              <td className="px-4 py-3 text-sm">{sb.agent}</td>
                              <td className="px-4 py-3">
                                <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                                  sb.status === 'Clean' ? 'bg-green-500/20 text-green-400' :
                                  sb.status === 'Errors Found' ? 'bg-red-500/20 text-red-400' :
                                  sb.status === 'Awaiting Upload' ? 'bg-yellow-500/20 text-yellow-400' :
                                  'bg-blue-500/20 text-blue-400'
                                }`}>{sb.status}</span>
                              </td>
                              <td className="px-4 py-3 text-center text-sm">{sb.pages}/{sb.expected}</td>
                              <td className="px-4 py-3 text-center">
                                {sb.errors.length > 0
                                  ? <span className="text-red-400 font-bold text-sm">{sb.errors.length}</span>
                                  : <span className="text-green-400 text-sm">✓</span>
                                }
                              </td>
                              <td className="px-4 py-3 text-xs text-gray-400">{sb.uploadDate || '—'}</td>
                            </tr>
                          );
                        })}
                        {divScanbacks.length === 0 && (
                          <tr><td colSpan={7} className="text-center py-8 text-gray-500">No scanbacks in this division</td></tr>
                        )}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
            </div>
          );
        })()}

        {/* ════════════════════════════════════════════════════
            TAB: ORDERS
        ════════════════════════════════════════════════════ */}
        {activeTab === 'orders' && (
          <div>
            <div className="mb-6 flex items-center justify-between">
              <div>
                <h2 className="text-3xl font-bold mb-1">📋 Orders</h2>
                <p className="text-gray-400">{orders.length} total orders — each order carries mandatory QC due diligence on close</p>
              </div>
              <div className="flex gap-2">
                <button onClick={() => setShowNewOrderModal(true)} className="bg-orange-500 hover:bg-orange-600 px-4 py-2 rounded-lg font-semibold text-sm transition">
                  + New Order
                </button>
              </div>
            </div>

            <MandatoryQcDueDiligenceNotice compact className="mb-6" />

            {/* View toggles + stage filter */}
            <div className="flex items-center justify-between mb-4">
              <div className="flex gap-1 bg-gray-800 rounded-lg p-1">
                {(['list', 'kanban', 'calendar'] as const).map(v => (
                  <button key={v} onClick={() => setOrderView(v)}
                    className={`px-3 py-1.5 rounded text-sm font-semibold transition capitalize ${orderView === v ? 'bg-gray-600 text-white' : 'text-gray-400 hover:text-white'}`}>
                    {v === 'list' ? '☰ List' : v === 'kanban' ? '▦ Kanban' : '📅 Calendar'}
                  </button>
                ))}
              </div>
              <select value={stageFilter} onChange={e => setStageFilter(e.target.value)}
                className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-1.5 text-sm text-gray-300">
                <option value="all">All Stages</option>
                <option value="received">1 — Received</option>
                <option value="validated">2 — Validated</option>
                <option value="assigned">3 — Assigned</option>
                <option value="en_route">4 — En Route</option>
                <option value="in_progress">5 — In Progress</option>
                <option value="qc_review">6 — QC Review</option>
                <option value="documentation">7 — Documentation</option>
                <option value="delivered">8 — Delivered</option>
                <option value="billed">9 — Billed</option>
                <option value="complete">10 — Complete</option>
              </select>
            </div>

            {/* ── SERVICE COLOR KEY + FILTER ── */}
            <div className="bg-gray-800/60 border border-gray-700 rounded-xl p-3 mb-4">
              <div className="flex items-center gap-3 flex-wrap">
                <span className="text-[10px] font-bold text-gray-500 uppercase tracking-wider mr-1">Services</span>
                {SERVICE_GROUPS.map(grp => {
                  const count = orders.filter(o => grp.types.includes(o.type)).length;
                  const isActive = orderFilter === grp.id;
                  const isAll = orderFilter === 'all';
                  return (
                    <button key={grp.id}
                      onClick={() => setOrderFilter(orderFilter === grp.id ? 'all' : grp.id)}
                      className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold transition border ${
                        isActive
                          ? 'ring-2 ring-offset-1 ring-offset-gray-900 shadow-lg'
                          : isAll
                            ? 'hover:brightness-125'
                            : 'opacity-25 hover:opacity-60'
                      }`}
                      style={{
                        backgroundColor: isActive ? grp.solid : grp.solid + '25',
                        borderColor: isActive ? grp.color : grp.color + '30',
                        color: isActive ? '#FFFFFF' : grp.color,
                        // @ts-ignore
                        '--tw-ring-color': grp.color,
                      } as React.CSSProperties}>
                      <span className="w-3 h-3 rounded-full flex-shrink-0 shadow-sm" style={{ backgroundColor: grp.solid }} />
                      {grp.label}
                      <span className="px-1.5 rounded-full text-[10px] font-bold"
                        style={{
                          backgroundColor: isActive ? 'rgba(255,255,255,0.2)' : grp.solid + '35',
                          color: isActive ? '#FFFFFF' : grp.color,
                        }}>
                        {count}
                      </span>
                    </button>
                  );
                })}
                {orderFilter !== 'all' && (
                  <button onClick={() => setOrderFilter('all')} className="text-[10px] text-gray-500 hover:text-white transition ml-1">
                    ✕ Clear
                  </button>
                )}
              </div>
            </div>

            {/* Stage summary bar */}
            {orderView === 'list' && (() => {
              const STAGE_META: { key: string; label: string; color: string; short: string }[] = [
                { key: 'received', label: 'Received', color: '#3B82F6', short: 'RCV' },
                { key: 'validated', label: 'Validated', color: '#06B6D4', short: 'VAL' },
                { key: 'assigned', label: 'Assigned', color: '#6366F1', short: 'ASN' },
                { key: 'en_route', label: 'En Route', color: '#A855F7', short: 'ENR' },
                { key: 'in_progress', label: 'In Progress', color: '#F97316', short: 'SVC' },
                { key: 'qc_review', label: 'QC Review', color: '#EAB308', short: 'QC' },
                { key: 'documentation', label: 'Docs', color: '#14B8A6', short: 'DOC' },
                { key: 'delivered', label: 'Delivered', color: '#10B981', short: 'DLV' },
                { key: 'billed', label: 'Billed', color: '#84CC16', short: 'BIL' },
                { key: 'complete', label: 'Complete', color: '#22C55E', short: 'DONE' },
              ];
              return (
                <div className="flex gap-1 mb-3 overflow-x-auto pb-1">
                  {STAGE_META.map(s => {
                    const count = orders.filter(o => {
                      const stageKey = o.workflow?.[o.workflow_stage ?? 0]?.stage || '';
                      return stageKey === s.key;
                    }).length;
                    const isActive = stageFilter === s.key;
                    return (
                      <button key={s.key}
                        onClick={() => setStageFilter(stageFilter === s.key ? 'all' : s.key)}
                        className={`flex-shrink-0 flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition border ${
                          isActive
                            ? 'bg-opacity-30 border-opacity-60'
                            : 'bg-gray-800 border-gray-700 hover:border-gray-600'
                        }`}
                        style={isActive ? { backgroundColor: s.color + '20', borderColor: s.color + '60', color: s.color } : {}}>
                        <span className="w-2 h-2 rounded-full flex-shrink-0" style={{ backgroundColor: s.color }} />
                        <span className={isActive ? '' : 'text-gray-400'}>{s.short}</span>
                        <span className={`text-[10px] px-1.5 py-0 rounded-full font-bold ${count > 0 ? '' : 'opacity-30'}`}
                          style={count > 0 ? { backgroundColor: s.color + '20', color: s.color } : {}}>
                          {count}
                        </span>
                      </button>
                    );
                  })}
                </div>
              );
            })()}

            {/* List View */}
            {orderView === 'list' && (
              <div className="bg-gray-800 border border-gray-700 rounded-xl overflow-hidden">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-gray-700 text-gray-400 text-xs uppercase">
                      <th className="text-left px-4 py-3">Order</th>
                      <th className="text-left px-4 py-3">Service</th>
                      <th className="text-left px-4 py-3">Stage</th>
                      <th className="text-left px-4 py-3">Progress</th>
                      <th className="text-left px-4 py-3">Agent</th>
                      <th className="text-left px-4 py-3">Client / Subject</th>
                      <th className="text-left px-4 py-3">Date</th>
                      <th className="text-right px-4 py-3">Fee</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredOrders.map(order => {
                      const svc = SERVICE_COLORS[order.type];
                      const isSelected = selectedOrder === order.id;
                      const rowBg = isSelected
                        ? `${svc?.color}30`
                        : `${svc?.color}18`;
                      return (
                        <tr key={order.id}
                          className={`border-b border-gray-700/50 hover:brightness-110 transition cursor-pointer ${isSelected ? 'ring-2 ring-inset' : ''}`}
                          style={{
                            borderLeftWidth: '6px',
                            borderLeftColor: svc?.color || '#6B7280',
                            backgroundColor: rowBg,
                            // @ts-ignore
                            '--tw-ring-color': svc?.color ? svc.color + '60' : undefined,
                          } as React.CSSProperties}
                          onClick={() => setSelectedOrder(isSelected ? null : order.id)}>
                          <td className="px-4 py-3">
                            <span className="font-mono text-xs">{order.id}</span>
                            {order.priority !== 'Standard' && (
                              <span className={`ml-1.5 px-1.5 py-0.5 rounded text-[9px] font-bold ${order.priority === 'STAT' ? 'bg-red-500/20 text-red-400' : 'bg-yellow-500/20 text-yellow-400'}`}>
                                {order.priority}
                              </span>
                            )}
                          </td>
                          <td className="px-4 py-3"><ServiceBadge type={order.type} /></td>
                          <td className="px-4 py-3">
                            {(() => {
                              const stageIdx = order.workflow_stage ?? 0;
                              const totalStages = order.workflow?.length || 10;
                              const label = order.workflow_stage_label || order.status;
                              const STAGE_COLORS: Record<string, string> = {
                                'received': 'bg-blue-500/20 text-blue-400 border-blue-500/30',
                                'validated': 'bg-cyan-500/20 text-cyan-400 border-cyan-500/30',
                                'assigned': 'bg-indigo-500/20 text-indigo-400 border-indigo-500/30',
                                'en_route': 'bg-purple-500/20 text-purple-400 border-purple-500/30',
                                'in_progress': 'bg-orange-500/20 text-orange-400 border-orange-500/30',
                                'qc_review': 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
                                'documentation': 'bg-teal-500/20 text-teal-400 border-teal-500/30',
                                'delivered': 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
                                'billed': 'bg-lime-500/20 text-lime-400 border-lime-500/30',
                                'complete': 'bg-green-500/20 text-green-400 border-green-500/30',
                              };
                              const stageKey = order.workflow?.[stageIdx]?.stage || '';
                              const colorCls = STAGE_COLORS[stageKey] || 'bg-gray-500/20 text-gray-400 border-gray-500/30';
                              return (
                                <div className="flex flex-col gap-0.5">
                                  <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold border inline-block w-fit ${colorCls}`}>
                                    {stageIdx + 1}. {label.length > 16 ? label.slice(0, 14) + '…' : label}
                                  </span>
                                </div>
                              );
                            })()}
                          </td>
                          <td className="px-4 py-3">
                            {(() => {
                              const wf = order.workflow || [];
                              const stageIdx = order.workflow_stage ?? 0;
                              const cl = order.qc_checklist || [];
                              const qcPct = order.qc_progress ?? 0;
                              const totalChecks = cl.length;
                              const passedChecks = cl.filter(c => c.completed).length;
                              const fatalOpen = cl.filter(c => c.severity === 'FATAL' && !c.completed).length;
                              const critOpen = cl.filter(c => c.severity === 'CRITICAL' && !c.completed).length;
                              const qcAllClear = totalChecks > 0 && fatalOpen === 0 && critOpen === 0;
                              const qcHasFatal = fatalOpen > 0;
                              return (
                                <div className="flex flex-col gap-1.5">
                                  {/* Workflow progress bar */}
                                  <div className="flex gap-[2px]">
                                    {wf.map((s, i) => (
                                      <div key={s.stage}
                                        className={`h-2 rounded-sm flex-1 transition-all ${
                                          i < stageIdx ? 'bg-green-500' :
                                          i === stageIdx ? 'bg-orange-500 animate-pulse' :
                                          'bg-gray-700'
                                        }`}
                                        title={`${i+1}. ${s.label}`} />
                                    ))}
                                  </div>
                                  <div className="flex items-center gap-1.5">
                                    <span className="text-[10px] text-gray-500 font-semibold">{stageIdx}/{wf.length}</span>
                                    {/* QC Badge */}
                                    {totalChecks > 0 && (
                                      <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold border ${
                                        qcAllClear
                                          ? 'bg-green-500/20 text-green-400 border-green-500/40'
                                          : qcHasFatal
                                            ? 'bg-red-500/25 text-red-400 border-red-500/50 animate-pulse'
                                            : 'bg-yellow-500/20 text-yellow-400 border-yellow-500/40'
                                      }`}>
                                        {qcAllClear ? '✓ QC PASS' : qcHasFatal ? `⛔ ${fatalOpen} FATAL` : `⚠ ${critOpen} OPEN`}
                                      </span>
                                    )}
                                    {totalChecks > 0 && !qcAllClear && (
                                      <span className="text-[9px] text-gray-500">{passedChecks}/{totalChecks}</span>
                                    )}
                                  </div>
                                </div>
                              );
                            })()}
                          </td>
                          <td className="px-4 py-3">{order.agent || <span className="text-yellow-400 text-xs font-semibold">UNASSIGNED</span>}</td>
                          <td className="px-4 py-3">
                            <div className="text-gray-300 text-sm">{order.client}</div>
                            <div className="text-gray-500 text-xs">{order.signer}</div>
                          </td>
                          <td className="px-4 py-3 text-gray-400 text-xs">{order.date}<br/><span className="text-gray-500">{order.time}</span></td>
                          <td className="px-4 py-3 text-right font-semibold text-green-400">${order.fee}</td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            )}

            {/* Kanban View */}
            {orderView === 'kanban' && (
              <div className="flex gap-3 overflow-x-auto pb-4">
                {kanbanColumns.map(col => (
                  <div key={col.status} className="flex-shrink-0 w-64">
                    <div className="rounded-t-lg px-3 py-2 border-b-2" style={{ backgroundColor: col.color + '15', borderBottomColor: col.color }}>
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-1.5">
                          <span className="w-2 h-2 rounded-full" style={{ backgroundColor: col.color }} />
                          <span className="font-semibold text-sm">{col.status}</span>
                        </div>
                        <span className="text-xs font-bold px-2 py-0.5 rounded-full" style={{ backgroundColor: col.color + '20', color: col.color }}>{col.orders.length}</span>
                      </div>
                    </div>
                    <div className="space-y-2 mt-2 min-h-[200px]">
                      {col.orders.map(order => {
                        const svc = SERVICE_COLORS[order.type];
                        return (
                          <div key={order.id} className="border rounded-lg p-3 hover:brightness-110 transition cursor-pointer"
                            style={{ borderLeftWidth: '5px', borderLeftColor: svc?.color || '#6B7280', backgroundColor: svc?.color + '20', borderColor: svc?.color + '40' }}
                            onClick={() => { setSelectedOrder(order.id); setOrderView('list'); }}>
                            <div className="flex items-center justify-between mb-1.5">
                              <ServiceBadge type={order.type} size="sm" />
                              {order.priority !== 'Standard' && (
                                <span className={`px-1.5 py-0.5 rounded text-[9px] font-bold ${order.priority === 'STAT' ? 'bg-red-500/30 text-red-400' : 'bg-yellow-500/30 text-yellow-400'}`}>
                                  {order.priority}
                                </span>
                              )}
                            </div>
                            <p className="font-semibold text-sm mb-0.5 text-white">{order.signer}</p>
                            <p className="text-[10px] text-gray-400 mb-1">{order.address}</p>
                            <div className="flex items-center justify-between">
                              <span className="text-[10px] font-bold" style={{ color: svc?.color }}>{order.agent || 'Unassigned'}</span>
                              <span className="text-[10px] text-gray-500">{order.time}</span>
                            </div>
                            {order.workflow && (
                              <div className="flex gap-[2px] mt-1.5">
                                {order.workflow.map((s: WorkflowStage, idx: number) => (
                                  <div key={s.stage} className="h-2 rounded-sm flex-1"
                                    style={{ backgroundColor: idx < (order.workflow_stage ?? 0) ? svc?.color : idx === (order.workflow_stage ?? 0) ? svc?.color + '70' : '#374151' }} />
                                ))}
                              </div>
                            )}
                            {(() => {
                              const cl = order.qc_checklist || [];
                              if (cl.length === 0) return null;
                              const fatalOpen = cl.filter((c: any) => c.severity === 'FATAL' && !c.completed).length;
                              const critOpen = cl.filter((c: any) => c.severity === 'CRITICAL' && !c.completed).length;
                              const allClear = fatalOpen === 0 && critOpen === 0;
                              return (
                                <div className={`mt-1.5 px-2 py-1 rounded text-[10px] font-bold text-center border ${
                                  allClear
                                    ? 'bg-green-500/20 text-green-400 border-green-500/30'
                                    : fatalOpen > 0
                                      ? 'bg-red-500/25 text-red-400 border-red-500/40'
                                      : 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30'
                                }`}>
                                  {allClear ? '✓ QC CLEAR' : fatalOpen > 0 ? `⛔ ${fatalOpen} FATAL OPEN` : `⚠ ${critOpen} CHECKS OPEN`}
                                </div>
                              );
                            })()}
                          </div>
                        );
                      })}
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Calendar View */}
            {orderView === 'calendar' && (
              <div className="bg-gray-800 border border-gray-700 rounded-xl p-6">
                <div className="text-center mb-4">
                  <h3 className="text-xl font-bold">February 2026</h3>
                </div>
                <div className="grid grid-cols-7 gap-1 text-center text-xs text-gray-500 mb-2">
                  {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(d => (
                    <div key={d} className="py-2 font-semibold">{d}</div>
                  ))}
                </div>
                <div className="grid grid-cols-7 gap-1">
                  {Array.from({ length: 28 }, (_, i) => i + 1).map(day => {
                    const dateStr = `02/${String(day).padStart(2, '0')}/2026`;
                    const dayOrders = orders.filter(o => o.date === dateStr);
                    const isToday = day === 14;
                    return (
                      <div key={day} className={`min-h-[80px] border rounded-lg p-1 ${isToday ? 'border-orange-500 bg-orange-500/10' : 'border-gray-700 bg-gray-800/50'}`}>
                        <span className={`text-xs font-semibold ${isToday ? 'text-orange-400' : 'text-gray-500'}`}>{day}</span>
                        <div className="space-y-0.5 mt-1">
                          {dayOrders.slice(0, 3).map(o => {
                            const svc = SERVICE_COLORS[o.type];
                            return (
                              <div key={o.id} className="text-[10px] px-1 py-0.5 rounded truncate font-bold" style={{ backgroundColor: svc?.solid, color: '#FFFFFF' }}>
                                {o.time.replace(' ', '')} {svc?.label?.split(' ')[0]}
                              </div>
                            );
                          })}
                          {dayOrders.length > 3 && <div className="text-[10px] text-gray-500 px-1">+{dayOrders.length - 3} more</div>}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* Order Detail Slide-out */}
            {selectedOrder && (() => {
              const order = orders.find(o => o.id === selectedOrder);
              if (!order) return null;
              const svc = SERVICE_COLORS[order.type];
              return (
                <div className="fixed inset-y-0 right-0 w-[480px] bg-gray-900 border-l border-gray-700 z-50 overflow-y-auto shadow-2xl">
                  <div className="h-2 w-full" style={{ backgroundColor: svc?.color }} />
                  <div className="p-6">
                    <div className="flex items-center justify-between mb-6">
                      <div>
                        <span className="text-xs font-mono text-gray-500">{order.id}</span>
                        <div className="flex items-center gap-2 mt-1">
                          <ServiceBadge type={order.type} size="md" />
                          <StatusBadge status={order.status} />
                          {order.priority !== 'Standard' && <span className="px-2 py-0.5 bg-red-500/20 text-red-400 border border-red-500/30 rounded-full text-xs font-semibold">{order.priority}</span>}
                        </div>
                      </div>
                      <button onClick={() => setSelectedOrder(null)} className="text-gray-500 hover:text-white text-xl transition">✕</button>
                    </div>

                    <div className="space-y-4">
                      {/* ── WORKFLOW PIPELINE ── */}
                      {order.workflow && order.workflow.length > 0 && (() => {
                        const wf = order.workflow;
                        const currentIdx = order.workflow_stage ?? 0;

                        const clearGate = async (gateId: string) => {
                          try {
                            const res = await api.patch(`/prism/orders/${order.id}/gate`, {
                              gate_id: gateId,
                              agent: 'Dee Davis',
                            });
                            if (res.data?.success) {
                              setOrders(prev => prev.map(o => o.id === order.id ? { ...o, ...res.data.order } : o));
                            }
                          } catch (err) { console.error('Gate clear failed:', err); }
                        };

                        return (
                          <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
                            <h4 className="text-xs text-gray-500 uppercase mb-3 font-semibold">
                              Order Workflow — Stage {currentIdx + 1} of {wf.length}
                            </h4>

                            {/* Horizontal pipeline */}
                            <div className="flex items-center gap-0.5 mb-4 overflow-x-auto pb-1">
                              {wf.map((stage, i) => {
                                const allPassed = stage.gates.every((g: WorkflowGate) => g.passed);
                                const isActive = i === currentIdx;
                                const isPast = i < currentIdx;
                                const isFuture = i > currentIdx;
                                return (
                                  <div key={stage.stage} className="flex items-center flex-shrink-0">
                                    <div className={`flex flex-col items-center ${isActive ? 'scale-110' : ''}`}>
                                      <div className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold border-2 transition-all ${
                                        isPast || (isActive && allPassed)
                                          ? 'bg-green-500 border-green-500 text-white'
                                          : isActive
                                            ? 'bg-orange-500/20 border-orange-500 text-orange-400 ring-2 ring-orange-500/30'
                                            : 'bg-gray-700 border-gray-600 text-gray-500'
                                      }`}>
                                        {isPast || (isActive && allPassed) ? '✓' : i + 1}
                                      </div>
                                      <span className={`text-[8px] mt-1 text-center max-w-[60px] leading-tight ${
                                        isActive ? 'text-orange-400 font-bold' : isPast ? 'text-green-400' : 'text-gray-600'
                                      }`}>{stage.label.length > 14 ? stage.label.slice(0, 12) + '…' : stage.label}</span>
                                    </div>
                                    {i < wf.length - 1 && (
                                      <div className={`w-4 h-0.5 mx-0.5 mt-[-12px] ${isPast ? 'bg-green-500' : 'bg-gray-700'}`} />
                                    )}
                                  </div>
                                );
                              })}
                            </div>

                            {/* Active stage gates */}
                            {wf[currentIdx] && (
                              <div className={`rounded-lg p-3 border ${wf[currentIdx].gates.every((g: WorkflowGate) => g.passed) ? 'border-green-500/30 bg-green-500/5' : 'border-orange-500/30 bg-orange-500/5'}`}>
                                <div className="flex items-center justify-between mb-2">
                                  <span className="text-sm font-bold text-orange-400">{wf[currentIdx].label}</span>
                                  <span className="text-[10px] text-gray-500">
                                    {wf[currentIdx].gates.filter((g: WorkflowGate) => g.passed).length}/{wf[currentIdx].gates.length} gates
                                  </span>
                                </div>
                                <div className="space-y-1.5">
                                  {wf[currentIdx].gates.map((gate: WorkflowGate) => (
                                    <div key={gate.id}
                                      className={`flex items-start gap-2 p-1.5 rounded transition ${gate.passed ? 'opacity-60' : 'hover:bg-gray-700/30 cursor-pointer'}`}
                                      onClick={() => !gate.passed && gate.rule === 'manual' && clearGate(gate.id)}>
                                      <div className={`mt-0.5 w-4 h-4 rounded border-2 flex items-center justify-center flex-shrink-0 ${
                                        gate.passed ? 'bg-green-500 border-green-500 text-white' : 'border-orange-500 bg-orange-500/10'
                                      }`}>
                                        {gate.passed && <span className="text-[9px]">✓</span>}
                                      </div>
                                      <div className="flex-1">
                                        <p className={`text-xs ${gate.passed ? 'line-through text-gray-500' : ''}`}>{gate.check}</p>
                                        {gate.passed && gate.passed_by && (
                                          <p className="text-[9px] text-gray-600">{gate.passed_by} — {gate.passed_at ? new Date(gate.passed_at).toLocaleTimeString() : ''}</p>
                                        )}
                                        {!gate.passed && gate.rule !== 'manual' && (
                                          <p className="text-[9px] text-yellow-500/70">Auto-evaluates when conditions are met</p>
                                        )}
                                      </div>
                                    </div>
                                  ))}
                                </div>
                                {wf[currentIdx].gates.length > 0 && !wf[currentIdx].gates.every((g: WorkflowGate) => g.passed) && (
                                  <p className="text-[10px] text-orange-400/70 mt-2 text-center">
                                    Clear all gates to advance to next stage
                                  </p>
                                )}
                              </div>
                            )}
                          </div>
                        );
                      })()}

                      <div className="bg-gray-800 rounded-lg p-4 border border-gray-700" style={{ borderLeftWidth: '4px', borderLeftColor: svc?.color }}>
                        <h4 className="text-xs text-gray-500 uppercase mb-2 font-semibold">Appointment</h4>
                        <p className="font-bold text-lg">{order.signer}</p>
                        <p className="text-gray-400 text-sm mt-1">{order.address}</p>
                        <p className="text-gray-400 text-sm">{order.date} at {order.time}</p>
                      </div>

                      <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
                        <h4 className="text-xs text-gray-500 uppercase mb-2 font-semibold">Assignment</h4>
                        <p className="font-semibold">{order.agent || <span className="text-yellow-400">Unassigned</span>}</p>
                        <p className="text-gray-400 text-sm">Client: {order.client}</p>
                        <p className="text-green-400 text-sm font-semibold mt-1">Agent Fee: ${order.fee}</p>
                      </div>

                      <MandatoryQcDueDiligenceNotice compact className="mb-1" />

                      {/* ── MANDATORY QC CHECKLIST ── */}
                      {(() => {
                        const checklist = order.qc_checklist || [];
                        const fatalTotal = checklist.filter(c => c.severity === 'FATAL').length;
                        const fatalDone = checklist.filter(c => c.severity === 'FATAL' && c.completed).length;
                        const totalDone = checklist.filter(c => c.completed).length;
                        const progress = checklist.length ? Math.round(totalDone / checklist.length * 100) : 0;
                        const gatePass = fatalDone === fatalTotal;

                        const toggleQCItem = async (itemId: string, currentState: boolean) => {
                          try {
                            const res = await api.patch(`/prism/orders/${order.id}/qc`, {
                              item_id: itemId,
                              completed: !currentState,
                              agent: 'Dee Davis',
                            });
                            if (res.data?.success) {
                              setOrders(prev => prev.map(o => o.id === order.id ? { ...o, ...res.data.order } : o));
                            }
                          } catch (err) { console.error('QC update failed:', err); }
                        };

                        return (
                          <div className={`rounded-xl p-4 border-2 ${gatePass ? 'border-green-500/50 bg-green-500/5' : 'border-red-500/50 bg-red-500/5'}`}>
                            {/* QC Header Banner */}
                            <div className={`-mx-4 -mt-4 mb-4 px-4 py-3 rounded-t-xl flex items-center justify-between ${
                              gatePass ? 'bg-green-600' : 'bg-red-600'
                            }`}>
                              <div className="flex items-center gap-2">
                                <span className="text-lg">{gatePass ? '✅' : '🛑'}</span>
                                <div>
                                  <h4 className="text-sm font-bold text-white uppercase tracking-wide">
                                    Mandatory QC due diligence
                                  </h4>
                                  <p className="text-[10px] text-white/70">{SERVICE_INSPECTION[order.type]?.title || order.type}</p>
                                </div>
                              </div>
                              <span className="px-3 py-1 rounded-full text-xs font-black bg-white/20 text-white border border-white/30">
                                {gatePass ? '✓ ALL CLEAR' : `⛔ ${fatalTotal - fatalDone} FATAL OPEN`}
                              </span>
                            </div>

                            {/* Progress Bar */}
                            <div className="mb-4">
                              <div className="flex items-center justify-between text-xs mb-1.5">
                                <span className="text-gray-300 font-semibold">{totalDone}/{checklist.length} checks completed</span>
                                <span className={`text-sm font-black ${progress === 100 ? 'text-green-400' : progress >= 50 ? 'text-yellow-400' : 'text-red-400'}`}>{progress}%</span>
                              </div>
                              <div className="w-full bg-gray-700 rounded-full h-3 overflow-hidden">
                                <div className={`h-3 rounded-full transition-all ${gatePass ? 'bg-green-500' : progress >= 50 ? 'bg-yellow-500' : 'bg-red-500'}`} style={{ width: `${progress}%` }} />
                              </div>
                            </div>

                            <div className="space-y-2 max-h-[350px] overflow-y-auto">
                              {checklist.map(item => (
                                <div key={item.id}
                                  className={`flex items-start gap-3 p-2.5 rounded-lg cursor-pointer transition border ${
                                    item.completed
                                      ? 'opacity-60 bg-gray-800/50 border-gray-700/50 hover:opacity-80'
                                      : item.severity === 'FATAL'
                                        ? 'bg-red-500/8 border-red-500/25 hover:bg-red-500/15'
                                        : 'bg-gray-800/50 border-gray-700/50 hover:bg-gray-700/70'
                                  }`}
                                  onClick={() => toggleQCItem(item.id, item.completed)}>
                                  <div className={`mt-0.5 w-6 h-6 rounded-md border-2 flex items-center justify-center flex-shrink-0 transition ${
                                    item.completed
                                      ? 'bg-green-500 border-green-500 text-white'
                                      : item.severity === 'FATAL'
                                        ? 'border-red-500 bg-red-500/15'
                                        : 'border-gray-500 bg-gray-700'
                                  }`}>
                                    {item.completed && <span className="text-sm font-bold">✓</span>}
                                  </div>
                                  <div className="flex-1 min-w-0">
                                    <div className="flex items-center gap-2 mb-0.5">
                                      <span className={`text-[10px] font-black px-2 py-0.5 rounded ${
                                        item.severity === 'FATAL' ? 'bg-red-600 text-white' :
                                        item.severity === 'CRITICAL' ? 'bg-yellow-600 text-white' :
                                        'bg-gray-600 text-gray-300'
                                      }`}>{item.severity}</span>
                                      <span className="text-[10px] text-gray-500 font-mono">{item.id}</span>
                                    </div>
                                    <p className={`text-sm ${item.completed ? 'line-through text-gray-500' : 'text-gray-200'}`}>{item.check}</p>
                                    {item.completed && item.completed_by && (
                                      <p className="text-[10px] text-green-500/70 mt-0.5">✓ {item.completed_by} — {item.completed_at ? new Date(item.completed_at).toLocaleString() : ''}</p>
                                    )}
                                  </div>
                                </div>
                              ))}
                              {checklist.length === 0 && (
                                <p className="text-amber-200/90 text-sm text-center py-3 border border-amber-500/30 rounded-lg bg-amber-500/5">
                                  No per-order checklist loaded — use <strong className="text-white">mandatory due diligence reference</strong> below (Inspection Engine) until the API syncs items for this type.
                                </p>
                              )}
                            </div>

                            {SERVICE_INSPECTION[order.type]?.certs && (
                              <div className="mt-3 pt-3 border-t border-gray-700">
                                <h5 className="text-[10px] text-gray-500 uppercase font-semibold mb-1">Required Certifications</h5>
                                <div className="flex flex-wrap gap-1">
                                  {SERVICE_INSPECTION[order.type].certs.map((c: string, i: number) => (
                                    <span key={i} className="text-[10px] px-2 py-0.5 bg-blue-500/10 text-blue-400 border border-blue-500/20 rounded-full">{c}</span>
                                  ))}
                                </div>
                              </div>
                            )}

                            {/* Full rule set — same engine as Inspection tab + scanback due diligence; applies to all service types */}
                            {SERVICE_INSPECTION[order.type] && (() => {
                              const ref = SERVICE_INSPECTION[order.type];
                              return (
                                <div className="mt-4 pt-4 border-t border-gray-600 space-y-3">
                                  <h5 className="text-xs font-bold text-amber-300 uppercase tracking-wide">Mandatory due diligence — full reference</h5>
                                  <p className="text-[10px] text-gray-500">Complete rule set for <span className="text-gray-300 font-semibold">{ref.title}</span>. Check each fundamental against documentation and field execution.</p>
                                  <div className="max-h-40 overflow-y-auto space-y-1.5 pr-1">
                                    {ref.fundamentals.map((rule) => (
                                      <div key={rule.id} className="text-xs text-gray-300 flex gap-2">
                                        <span className={`flex-shrink-0 font-mono text-[9px] px-1 rounded ${rule.severity === 'FATAL' ? 'bg-red-500/20 text-red-300' : 'bg-gray-700 text-gray-400'}`}>{rule.id}</span>
                                        <span>{rule.check}</span>
                                      </div>
                                    ))}
                                  </div>
                                  <div>
                                    <p className="text-[10px] font-bold text-red-400/90 mb-1">Fatal / zero-tolerance</p>
                                    <ul className="text-[10px] text-gray-400 space-y-0.5 list-disc list-inside">
                                      {ref.fatalFlaws.slice(0, 6).map((f, i) => <li key={i}>{f}</li>)}
                                      {ref.fatalFlaws.length > 6 && <li className="text-gray-600">+ {ref.fatalFlaws.length - 6} more (see Inspection)</li>}
                                    </ul>
                                  </div>
                                  <div>
                                    <p className="text-[10px] font-bold text-yellow-500/80 mb-1">Common errors</p>
                                    <ul className="text-[10px] text-gray-400 space-y-0.5 list-disc list-inside">
                                      {ref.commonErrors.map((e, i) => <li key={i}>{e}</li>)}
                                    </ul>
                                  </div>
                                </div>
                              );
                            })()}
                          </div>
                        );
                      })()}

                      {(() => {
                        const cl = order.qc_checklist || [];
                        const fatalOpen = cl.filter(c => c.severity === 'FATAL' && !c.completed).length;
                        const canComplete = fatalOpen === 0;

                        const handleComplete = async () => {
                          if (!canComplete) return;
                          try {
                            const res = await api.patch(`/prism/orders/${order.id}`, { status: 'Completed' });
                            if (res.data?.success) {
                              setOrders(prev => prev.map(o => o.id === order.id ? { ...o, ...res.data.order } : o));
                            }
                          } catch (err: any) {
                            const msg = err?.response?.data?.message || err?.response?.data?.error || 'Failed';
                            alert(`QC GATE BLOCKED: ${msg}`);
                          }
                        };

                        return (
                          <div className="space-y-2">
                            <div className="flex gap-2">
                              {order.status === 'New' && (
                                <button className="flex-1 bg-blue-600 hover:bg-blue-700 px-4 py-2.5 rounded-lg font-semibold text-sm transition">
                                  Assign Agent
                                </button>
                              )}
                              {order.status === 'Errors Found' && (
                                <button className="flex-1 bg-red-600 hover:bg-red-700 px-4 py-2.5 rounded-lg font-semibold text-sm transition"
                                  onClick={() => { setActiveTab('scanbacks'); setSelectedOrder(null); }}>
                                  View Scanback Errors
                                </button>
                              )}
                              {order.status !== 'Completed' && (
                                <button
                                  className={`flex-1 px-4 py-2.5 rounded-lg font-semibold text-sm transition ${
                                    canComplete
                                      ? 'bg-green-600 hover:bg-green-700 cursor-pointer'
                                      : 'bg-gray-700 text-gray-500 cursor-not-allowed'
                                  }`}
                                  disabled={!canComplete}
                                  onClick={handleComplete}
                                  title={canComplete ? 'Mark order complete' : `${fatalOpen} FATAL QC items must be completed first`}>
                                  {canComplete ? 'Complete Order' : `QC Gate: ${fatalOpen} Fatal Open`}
                                </button>
                              )}
                              <button className="bg-gray-700 hover:bg-gray-600 px-4 py-2.5 rounded-lg font-semibold text-sm transition">
                                Edit
                              </button>
                            </div>
                            {!canComplete && order.status !== 'Completed' && (
                              <p className="text-red-400 text-xs text-center font-semibold">
                                All FATAL QC items must be checked before this order can be completed
                              </p>
                            )}
                          </div>
                        );
                      })()}
                    </div>
                  </div>
                </div>
              );
            })()}
          </div>
        )}

        {/* ════════════════════════════════════════════════════
            TAB: DISPATCH
        ════════════════════════════════════════════════════ */}
        {activeTab === 'dispatch' && (
          <div>
            <div className="mb-6">
              <h2 className="text-3xl font-bold mb-1">🚀 Dispatch</h2>
              <p className="text-gray-400">{unassigned.length} orders need agents</p>
            </div>

            <MandatoryQcDueDiligenceNotice compact className="mb-6" />

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Unassigned Orders */}
              <div>
                <h3 className="text-lg font-bold mb-3">Orders Awaiting Assignment</h3>
                <div className="space-y-3">
                  {unassigned.length === 0 ? (
                    <div className="bg-gray-800 border border-gray-700 rounded-xl p-8 text-center">
                      <p className="text-green-400 text-lg font-semibold">✅ All orders assigned!</p>
                      <p className="text-gray-500 text-sm mt-1">No pending assignments</p>
                    </div>
                  ) : (
                    unassigned.map(order => {
                      const svc = SERVICE_COLORS[order.type];
                      return (
                        <div key={order.id} className="bg-gray-800 border border-gray-700 rounded-xl p-4 hover:border-yellow-500/50 transition"
                          style={{ borderLeftWidth: '5px', borderLeftColor: svc?.color, backgroundColor: svc?.color + '10' }}>
                          <div className="flex items-center justify-between mb-2">
                            <div className="flex items-center gap-2">
                              <ServiceBadge type={order.type} />
                              <span className="font-mono text-xs text-gray-500">{order.id}</span>
                            </div>
                            {order.priority !== 'Standard' && <span className="px-2 py-0.5 bg-red-500/20 text-red-400 rounded-full text-xs font-bold">{order.priority}</span>}
                          </div>
                          <p className="font-semibold">{order.signer}</p>
                          <p className="text-sm text-gray-400">{order.address} — {order.date} {order.time}</p>
                          <p className="text-sm text-gray-500">Client: {order.client}</p>
                          <div className="mt-3 flex gap-2">
                            <button className="bg-blue-600 hover:bg-blue-700 px-3 py-1.5 rounded-lg font-semibold text-xs transition">
                              Auto-Match Agent
                            </button>
                            <button className="bg-gray-700 hover:bg-gray-600 px-3 py-1.5 rounded-lg font-semibold text-xs transition">
                              Manual Assign
                            </button>
                          </div>
                        </div>
                      );
                    })
                  )}
                </div>
              </div>

              {/* Available Agents */}
              <div>
                <h3 className="text-lg font-bold mb-3">Available Agents</h3>
                <div className="space-y-3">
                  {agents.filter(a => a.status === 'Active').map(agent => (
                    <div key={agent.id} className="bg-gray-800 border border-gray-700 rounded-xl p-4 hover:border-blue-500/50 transition cursor-pointer">
                      <div className="flex items-center justify-between mb-2">
                        <div>
                          <p className="font-semibold">{agent.name}</p>
                          <p className="text-xs text-gray-500">{agent.city}, {agent.state}</p>
                        </div>
                        <div className="text-right">
                          <p className="text-xs text-gray-400">{agent.activeOrders} active</p>
                          <p className="text-xs text-yellow-400">⭐ {agent.rating}</p>
                        </div>
                      </div>
                      <div className="flex flex-wrap gap-1 mb-2">
                        {agent.specialties.map(s => (
                          <span key={s} className="px-2 py-0.5 bg-gray-700 text-gray-300 rounded text-xs">{s}</span>
                        ))}
                      </div>
                      <div className="flex gap-4 text-xs text-gray-400">
                        <span>✅ {agent.completionRate}%</span>
                        <span>⏱ {agent.onTimeRate}%</span>
                        <span className={agent.errorRate <= 2 ? 'text-green-400' : 'text-yellow-400'}>⚠ {agent.errorRate}% errors</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* ════════════════════════════════════════════════════
            TAB: FIELD OPS (REO / MORTGAGE FIELD SERVICES)
        ════════════════════════════════════════════════════ */}
        {activeTab === 'fieldops' && (() => {
          const filteredProps = fieldOpsFilter === 'all' ? propertyOrders
            : Object.keys(FIELD_OPS_PROGRAMS).includes(fieldOpsFilter)
              ? propertyOrders.filter(p => p.program === fieldOpsFilter)
              : propertyOrders.filter(p => p.status === fieldOpsFilter);

          const statusCounts = Object.keys(FIELD_OPS_STATUSES).reduce((acc, k) => {
            acc[k] = propertyOrders.filter(p => p.status === k).length; return acc;
          }, {} as Record<string, number>);

          const totalPhotosReq = propertyOrders.reduce((s, p) => s + p.photos_required, 0);
          const totalPhotosSub = propertyOrders.reduce((s, p) => s + p.photos_submitted, 0);
          const totalRevenue = propertyOrders.reduce((s, p) => s + p.fee, 0);
          const rushCount = propertyOrders.filter(p => p.priority === 'rush' && p.status !== 'complete').length;
          const overdueCount = propertyOrders.filter(p => {
            if (p.status === 'complete') return false;
            const parts = p.due_date.split('/');
            if (parts.length !== 3) return false;
            const due = new Date(parseInt(parts[2]), parseInt(parts[0]) - 1, parseInt(parts[1]));
            return due < new Date();
          }).length;

          const selectedProp = propertyOrders.find(p => p.id === selectedProperty);
          const selProgram = selectedProp ? FIELD_OPS_PROGRAMS[selectedProp.program] : null;
          const selService = selectedProp ? FIELD_OPS_SERVICES[selectedProp.service_type] : null;
          const selStatus = selectedProp ? FIELD_OPS_STATUSES[selectedProp.status] : null;
          const selVendor = selectedProp ? VENDOR_SOURCES[selectedProp.vendor_source] : null;

          return (
          <div>
            {/* Header */}
            <div className="mb-6 flex items-center justify-between">
              <div>
                <h2 className="text-3xl font-bold mb-1">🏠 Field Operations</h2>
                <p className="text-gray-400">REO & Mortgage Field Services — Property Inspections, Preservation, Maintenance</p>
                <p className="text-[11px] text-amber-200/80 mt-1">Mandatory QC due diligence: photo counts, program standards, and vendor documentation are required before work orders close (same quality bar as other PRISM lanes).</p>
              </div>
              <div className="flex gap-2">
                {(['list', 'route', 'photos'] as const).map(v => (
                  <button key={v} onClick={() => setFieldOpsView(v)}
                    className={`px-3 py-1.5 rounded-lg text-sm font-semibold transition ${fieldOpsView === v ? 'bg-blue-600 text-white' : 'bg-gray-800 text-gray-400 hover:text-white'}`}>
                    {v === 'list' ? '📋 Work Orders' : v === 'route' ? '🗺️ Routes' : '📸 Photos'}
                  </button>
                ))}
              </div>
            </div>

            {/* Stats Row */}
            <div className="grid grid-cols-6 gap-3 mb-6">
              <div className="bg-gray-800 border border-gray-700 rounded-xl p-3 text-center">
                <p className="text-2xl font-bold text-white">{propertyOrders.length}</p>
                <p className="text-[10px] text-gray-500 uppercase font-semibold">Total Orders</p>
              </div>
              <div className="bg-gray-800 border border-gray-700 rounded-xl p-3 text-center">
                <p className="text-2xl font-bold text-yellow-400">{rushCount}</p>
                <p className="text-[10px] text-gray-500 uppercase font-semibold">Rush Priority</p>
              </div>
              <div className="bg-gray-800 border border-red-500/30 rounded-xl p-3 text-center">
                <p className="text-2xl font-bold text-red-400">{overdueCount}</p>
                <p className="text-[10px] text-gray-500 uppercase font-semibold">Overdue</p>
              </div>
              <div className="bg-gray-800 border border-gray-700 rounded-xl p-3 text-center">
                <p className="text-2xl font-bold text-teal-400">{totalPhotosSub}/{totalPhotosReq}</p>
                <p className="text-[10px] text-gray-500 uppercase font-semibold">Photos</p>
              </div>
              <div className="bg-gray-800 border border-gray-700 rounded-xl p-3 text-center">
                <p className="text-2xl font-bold text-green-400">${totalRevenue.toLocaleString()}</p>
                <p className="text-[10px] text-gray-500 uppercase font-semibold">Pipeline Value</p>
              </div>
              <div className="bg-gray-800 border border-gray-700 rounded-xl p-3 text-center">
                <p className="text-2xl font-bold text-purple-400">{propertyOrders.filter(p => p.recurring).length}</p>
                <p className="text-[10px] text-gray-500 uppercase font-semibold">Recurring</p>
              </div>
            </div>

            {/* Program Filter Bar */}
            <div className="flex gap-2 mb-4 flex-wrap">
              <button onClick={() => setFieldOpsFilter('all')}
                className={`px-3 py-1.5 rounded-lg text-xs font-bold transition ${fieldOpsFilter === 'all' ? 'bg-white text-gray-900' : 'bg-gray-800 text-gray-400 hover:text-white'}`}>
                All ({propertyOrders.length})
              </button>
              {Object.entries(FIELD_OPS_PROGRAMS).map(([key, prog]) => {
                const cnt = propertyOrders.filter(p => p.program === key).length;
                if (cnt === 0) return null;
                return (
                  <button key={key} onClick={() => setFieldOpsFilter(key)}
                    className={`px-3 py-1.5 rounded-lg text-xs font-bold transition flex items-center gap-1.5 ${fieldOpsFilter === key ? 'text-white' : 'text-gray-400 hover:text-white'}`}
                    style={{ backgroundColor: fieldOpsFilter === key ? prog.solid : '#1F2937', borderWidth: '1px', borderColor: prog.color + '40' }}>
                    <span>{prog.icon}</span> {prog.label} <span className="opacity-60">({cnt})</span>
                  </button>
                );
              })}
            </div>

            {/* Status Pipeline Bar */}
            <div className="flex gap-1 mb-6 bg-gray-800 rounded-xl p-1.5 overflow-x-auto">
              {Object.entries(FIELD_OPS_STATUSES).map(([key, st]) => (
                <button key={key} onClick={() => setFieldOpsFilter(fieldOpsFilter === key ? 'all' : key)}
                  className={`px-2.5 py-1 rounded text-[10px] font-bold transition whitespace-nowrap flex items-center gap-1 ${fieldOpsFilter === key ? 'text-white' : 'text-gray-500 hover:text-gray-300'}`}
                  style={{ backgroundColor: fieldOpsFilter === key ? st.color : 'transparent' }}>
                  {st.label} <span className="opacity-60">{statusCounts[key] || 0}</span>
                </button>
              ))}
            </div>

            {/* ──── WORK ORDERS LIST VIEW ──── */}
            {fieldOpsView === 'list' && (
              <div className="flex gap-4">
                {/* Order List */}
                <div className={`space-y-2 ${selectedProperty ? 'w-3/5' : 'w-full'}`}>
                  {filteredProps.length === 0 && (
                    <div className="bg-gray-800 border border-gray-700 rounded-xl p-10 text-center">
                      <p className="text-gray-500 text-lg">No work orders match this filter</p>
                    </div>
                  )}
                  {filteredProps.map(wo => {
                    const prog = FIELD_OPS_PROGRAMS[wo.program];
                    const svc = FIELD_OPS_SERVICES[wo.service_type];
                    const st = FIELD_OPS_STATUSES[wo.status];
                    const vendor = VENDOR_SOURCES[wo.vendor_source];
                    const photoPercent = wo.photos_required > 0 ? Math.round((wo.photos_submitted / wo.photos_required) * 100) : 0;
                    const isSelected = selectedProperty === wo.id;
                    return (
                      <div key={wo.id} onClick={() => setSelectedProperty(isSelected ? null : wo.id)}
                        className={`bg-gray-800 border rounded-xl p-3 cursor-pointer transition hover:border-gray-500 ${isSelected ? 'border-blue-500 ring-2 ring-blue-500/30' : 'border-gray-700'}`}
                        style={{ borderLeftWidth: '5px', borderLeftColor: prog?.color, backgroundColor: isSelected ? prog?.color + '08' : undefined }}>
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex items-center gap-2">
                            <span className="text-lg">{prog?.icon}</span>
                            <span className="font-mono text-[10px] text-gray-500">{wo.id}</span>
                            <span className="px-2 py-0.5 rounded-full text-[10px] font-bold text-white" style={{ backgroundColor: prog?.solid }}>{prog?.label}</span>
                            {wo.priority === 'rush' && <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-red-600 text-white animate-pulse">RUSH</span>}
                            {wo.recurring && <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-purple-600 text-white">🔁 {wo.recurring_freq}</span>}
                          </div>
                          <div className="flex items-center gap-2">
                            <span className="px-2 py-0.5 rounded-full text-[10px] font-bold text-white" style={{ backgroundColor: st?.color }}>{st?.label}</span>
                            <span className="text-xs font-bold text-green-400">${wo.fee}</span>
                          </div>
                        </div>
                        <div className="flex items-center justify-between">
                          <div>
                            <p className="text-sm font-semibold text-white">{wo.property_address}</p>
                            <p className="text-xs text-gray-400">{wo.city}, {wo.state} {wo.zip}</p>
                          </div>
                          <div className="text-right">
                            <p className="text-xs text-gray-400">{svc?.icon} {svc?.label}</p>
                            <p className="text-[10px] text-gray-500">{vendor?.icon} {vendor?.label}</p>
                          </div>
                        </div>
                        {/* Photo progress bar */}
                        <div className="mt-2 flex items-center gap-2">
                          <span className="text-[10px] text-gray-500">📸 {wo.photos_submitted}/{wo.photos_required}</span>
                          <div className="flex-1 bg-gray-700 rounded-full h-1.5">
                            <div className="h-1.5 rounded-full transition-all" style={{ width: `${photoPercent}%`, backgroundColor: photoPercent >= 100 ? '#10B981' : photoPercent > 0 ? '#F59E0B' : '#374151' }} />
                          </div>
                          <span className="text-[10px] text-gray-500">Due {wo.due_date}</span>
                        </div>
                      </div>
                    );
                  })}
                </div>

                {/* Property Detail Slide-out */}
                {selectedProp && selProgram && (
                  <div className="w-2/5 bg-gray-800 border border-gray-700 rounded-xl overflow-hidden sticky top-36 self-start max-h-[80vh] overflow-y-auto">
                    <div className="h-2 w-full" style={{ backgroundColor: selProgram.color }} />
                    <div className="p-5">
                      <div className="flex items-center justify-between mb-4">
                        <div className="flex items-center gap-2">
                          <span className="text-xl">{selProgram.icon}</span>
                          <span className="px-2.5 py-1 rounded-full text-xs font-bold text-white" style={{ backgroundColor: selProgram.solid }}>{selProgram.label}</span>
                          {selectedProp.priority === 'rush' && <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-red-600 text-white animate-pulse">RUSH</span>}
                        </div>
                        <button onClick={() => setSelectedProperty(null)} className="text-gray-500 hover:text-white text-lg">✕</button>
                      </div>

                      <h3 className="text-lg font-bold text-white mb-1">{selectedProp.property_address}</h3>
                      <p className="text-sm text-gray-400 mb-4">{selectedProp.city}, {selectedProp.state} {selectedProp.zip}</p>

                      <div className="grid grid-cols-2 gap-3 mb-4">
                        <div className="bg-gray-900 rounded-lg p-3">
                          <p className="text-[10px] text-gray-500 uppercase font-semibold">Service</p>
                          <p className="text-sm text-white font-semibold">{selService?.icon} {selService?.label}</p>
                        </div>
                        <div className="bg-gray-900 rounded-lg p-3">
                          <p className="text-[10px] text-gray-500 uppercase font-semibold">Status</p>
                          <p className="text-sm font-bold" style={{ color: selStatus?.color }}>{selStatus?.label}</p>
                        </div>
                        <div className="bg-gray-900 rounded-lg p-3">
                          <p className="text-[10px] text-gray-500 uppercase font-semibold">Property Type</p>
                          <p className="text-sm text-white capitalize">{selectedProp.property_type.replace('_', ' ')}</p>
                        </div>
                        <div className="bg-gray-900 rounded-lg p-3">
                          <p className="text-[10px] text-gray-500 uppercase font-semibold">Fee</p>
                          <p className="text-sm text-green-400 font-bold">${selectedProp.fee}</p>
                        </div>
                        <div className="bg-gray-900 rounded-lg p-3">
                          <p className="text-[10px] text-gray-500 uppercase font-semibold">Assigned To</p>
                          <p className="text-sm text-white">{selectedProp.assigned_to || <span className="text-red-400">Unassigned</span>}</p>
                        </div>
                        <div className="bg-gray-900 rounded-lg p-3">
                          <p className="text-[10px] text-gray-500 uppercase font-semibold">Vendor</p>
                          <p className="text-sm text-white">{selVendor?.icon} {selVendor?.label}</p>
                        </div>
                        <div className="bg-gray-900 rounded-lg p-3">
                          <p className="text-[10px] text-gray-500 uppercase font-semibold">Due Date</p>
                          <p className="text-sm text-white font-semibold">{selectedProp.due_date}</p>
                        </div>
                        <div className="bg-gray-900 rounded-lg p-3">
                          <p className="text-[10px] text-gray-500 uppercase font-semibold">Condition Code</p>
                          <p className="text-sm text-white">{selectedProp.condition_code || '—'}</p>
                        </div>
                      </div>

                      {selectedProp.recurring && (
                        <div className="bg-purple-500/10 border border-purple-500/30 rounded-lg p-3 mb-4">
                          <p className="text-xs font-bold text-purple-400">🔁 Recurring — {selectedProp.recurring_freq}</p>
                        </div>
                      )}

                      {/* Photo Documentation */}
                      <div className="bg-gray-900 rounded-lg p-4 mb-4">
                        <h4 className="text-sm font-bold text-white mb-2">📸 Photo Documentation</h4>
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-xs text-gray-400">{selectedProp.photos_submitted} of {selectedProp.photos_required} required photos</span>
                          <span className={`text-xs font-bold ${selectedProp.photos_submitted >= selectedProp.photos_required ? 'text-green-400' : 'text-yellow-400'}`}>
                            {selectedProp.photos_submitted >= selectedProp.photos_required ? '✅ Complete' : `⚠️ ${selectedProp.photos_required - selectedProp.photos_submitted} needed`}
                          </span>
                        </div>
                        <div className="w-full bg-gray-700 rounded-full h-3">
                          <div className="h-3 rounded-full transition-all"
                            style={{ width: `${Math.min(100, Math.round((selectedProp.photos_submitted / selectedProp.photos_required) * 100))}%`,
                              backgroundColor: selectedProp.photos_submitted >= selectedProp.photos_required ? '#10B981' : '#F59E0B' }} />
                        </div>
                        {selectedProp.service_type === 'interior_inspection' && (
                          <div className="mt-3 grid grid-cols-3 gap-1 text-[10px] text-gray-500">
                            {['Front Exterior', 'Rear Exterior', 'Left Side', 'Right Side', 'Kitchen', 'Living Room', 'Bathroom 1', 'Bedroom 1', 'Bedroom 2', 'Basement', 'Garage', 'Damage Areas'].map((room, i) => (
                              <div key={i} className={`px-2 py-1 rounded text-center border ${i < selectedProp.photos_submitted ? 'bg-green-500/10 border-green-500/30 text-green-400' : 'bg-gray-800 border-gray-700'}`}>
                                {i < selectedProp.photos_submitted ? '✅' : '⬜'} {room}
                              </div>
                            ))}
                          </div>
                        )}
                      </div>

                      {/* Notes */}
                      <div className="bg-gray-900 rounded-lg p-3 mb-4">
                        <p className="text-[10px] text-gray-500 uppercase font-semibold mb-1">Notes</p>
                        <p className="text-sm text-gray-300">{selectedProp.notes}</p>
                      </div>

                      {/* Action Buttons */}
                      <div className="flex gap-2 flex-wrap">
                        {selectedProp.status === 'new' && (
                          <button className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg font-bold text-sm transition">🚀 Dispatch</button>
                        )}
                        {['assigned', 'en_route', 'on_site'].includes(selectedProp.status) && (
                          <button className="bg-teal-600 hover:bg-teal-700 px-4 py-2 rounded-lg font-bold text-sm transition">📸 Upload Photos</button>
                        )}
                        {selectedProp.status === 'photos_submitted' && (
                          <button className="bg-purple-600 hover:bg-purple-700 px-4 py-2 rounded-lg font-bold text-sm transition">📋 Generate Report</button>
                        )}
                        {selectedProp.status === 'qc_review' && (
                          <>
                            <button className="bg-green-600 hover:bg-green-700 px-4 py-2 rounded-lg font-bold text-sm transition">✅ Approve</button>
                            <button className="bg-red-600 hover:bg-red-700 px-4 py-2 rounded-lg font-bold text-sm transition">❌ Reject</button>
                          </>
                        )}
                        {selectedProp.status === 'report_pending' && (
                          <button className="bg-orange-600 hover:bg-orange-700 px-4 py-2 rounded-lg font-bold text-sm transition">📝 Submit Report</button>
                        )}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* ──── ROUTE VIEW ──── */}
            {fieldOpsView === 'route' && (
              <div>
                <h3 className="text-lg font-bold text-white mb-4">🗺️ Daily Routes — Agent Deployment</h3>
                {(() => {
                  const agentGroups: Record<string, PropertyWorkOrder[]> = {};
                  propertyOrders.filter(p => p.status !== 'complete' && p.assigned_to).forEach(p => {
                    if (!agentGroups[p.assigned_to]) agentGroups[p.assigned_to] = [];
                    agentGroups[p.assigned_to].push(p);
                  });
                  const unassigned = propertyOrders.filter(p => !p.assigned_to);
                  return (
                    <div className="space-y-4">
                      {Object.entries(agentGroups).map(([agent, wos]) => {
                        const vendor = VENDOR_SOURCES[wos[0].vendor_source];
                        const totalFee = wos.reduce((s, w) => s + w.fee, 0);
                        return (
                          <div key={agent} className="bg-gray-800 border border-gray-700 rounded-xl p-4">
                            <div className="flex items-center justify-between mb-3">
                              <div className="flex items-center gap-2">
                                <span className="text-lg">{vendor?.icon || '👤'}</span>
                                <h4 className="font-bold text-white">{agent}</h4>
                                <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-gray-700 text-gray-300">{vendor?.label}</span>
                              </div>
                              <div className="flex items-center gap-3">
                                <span className="text-xs text-gray-400">{wos.length} properties</span>
                                <span className="text-xs font-bold text-green-400">${totalFee}</span>
                              </div>
                            </div>
                            <div className="space-y-1.5">
                              {wos.map((wo, idx) => {
                                const prog = FIELD_OPS_PROGRAMS[wo.program];
                                const svc = FIELD_OPS_SERVICES[wo.service_type];
                                const st = FIELD_OPS_STATUSES[wo.status];
                                return (
                                  <div key={wo.id} className="flex items-center gap-3 bg-gray-900 rounded-lg px-3 py-2 border border-gray-700">
                                    <span className="text-xs font-bold text-gray-500 w-5">{idx + 1}.</span>
                                    <span className="text-sm">{prog?.icon}</span>
                                    <div className="flex-1">
                                      <p className="text-sm text-white font-semibold">{wo.property_address}, {wo.city}</p>
                                      <p className="text-[10px] text-gray-500">{svc?.label} · Due {wo.due_date}</p>
                                    </div>
                                    <span className="px-2 py-0.5 rounded-full text-[10px] font-bold text-white" style={{ backgroundColor: st?.color }}>{st?.label}</span>
                                    {wo.priority === 'rush' && <span className="text-[10px] font-bold text-red-400">🔴 RUSH</span>}
                                    <span className="text-xs text-green-400 font-bold">${wo.fee}</span>
                                  </div>
                                );
                              })}
                            </div>
                          </div>
                        );
                      })}
                      {unassigned.length > 0 && (
                        <div className="bg-gray-800 border-2 border-dashed border-red-500/30 rounded-xl p-4">
                          <h4 className="font-bold text-red-400 mb-3">⚠️ Unassigned ({unassigned.length})</h4>
                          <div className="space-y-1.5">
                            {unassigned.map(wo => {
                              const prog = FIELD_OPS_PROGRAMS[wo.program];
                              const svc = FIELD_OPS_SERVICES[wo.service_type];
                              return (
                                <div key={wo.id} className="flex items-center gap-3 bg-gray-900 rounded-lg px-3 py-2 border border-red-500/20">
                                  <span className="text-sm">{prog?.icon}</span>
                                  <div className="flex-1">
                                    <p className="text-sm text-white font-semibold">{wo.property_address}, {wo.city}</p>
                                    <p className="text-[10px] text-gray-500">{svc?.label} · Due {wo.due_date}</p>
                                  </div>
                                  {wo.priority === 'rush' && <span className="text-[10px] font-bold text-red-400 animate-pulse">🔴 RUSH</span>}
                                  <button className="bg-blue-600 hover:bg-blue-700 px-3 py-1 rounded text-xs font-bold transition">Assign</button>
                                </div>
                              );
                            })}
                          </div>
                        </div>
                      )}
                    </div>
                  );
                })()}
              </div>
            )}

            {/* ──── PHOTO PIPELINE VIEW ──── */}
            {fieldOpsView === 'photos' && (
              <div>
                <h3 className="text-lg font-bold text-white mb-4">📸 Photo Documentation Pipeline</h3>
                <div className="grid grid-cols-3 gap-4 mb-6">
                  <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-4 text-center">
                    <p className="text-2xl font-bold text-red-400">{propertyOrders.filter(p => p.photos_submitted === 0 && p.status !== 'complete' && p.status !== 'new').length}</p>
                    <p className="text-xs text-gray-400">No Photos Yet</p>
                  </div>
                  <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-xl p-4 text-center">
                    <p className="text-2xl font-bold text-yellow-400">{propertyOrders.filter(p => p.photos_submitted > 0 && p.photos_submitted < p.photos_required).length}</p>
                    <p className="text-xs text-gray-400">Partial — Missing Photos</p>
                  </div>
                  <div className="bg-green-500/10 border border-green-500/30 rounded-xl p-4 text-center">
                    <p className="text-2xl font-bold text-green-400">{propertyOrders.filter(p => p.photos_submitted >= p.photos_required && p.photos_required > 0).length}</p>
                    <p className="text-xs text-gray-400">Complete Photo Sets</p>
                  </div>
                </div>

                <div className="space-y-2">
                  {propertyOrders.filter(p => p.status !== 'new').sort((a, b) => (a.photos_submitted / a.photos_required) - (b.photos_submitted / b.photos_required)).map(wo => {
                    const prog = FIELD_OPS_PROGRAMS[wo.program];
                    const svc = FIELD_OPS_SERVICES[wo.service_type];
                    const pct = wo.photos_required > 0 ? Math.round((wo.photos_submitted / wo.photos_required) * 100) : 0;
                    const barColor = pct >= 100 ? '#10B981' : pct >= 50 ? '#F59E0B' : pct > 0 ? '#F97316' : '#EF4444';
                    return (
                      <div key={wo.id} className="bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 flex items-center gap-4"
                        style={{ borderLeftWidth: '4px', borderLeftColor: barColor }}>
                        <span className="text-sm">{prog?.icon}</span>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm text-white font-semibold truncate">{wo.property_address}, {wo.city}</p>
                          <p className="text-[10px] text-gray-500">{svc?.label} · {wo.assigned_to || 'Unassigned'}</p>
                        </div>
                        <div className="w-40 flex items-center gap-2">
                          <div className="flex-1 bg-gray-700 rounded-full h-2.5">
                            <div className="h-2.5 rounded-full transition-all" style={{ width: `${pct}%`, backgroundColor: barColor }} />
                          </div>
                          <span className="text-xs font-bold w-12 text-right" style={{ color: barColor }}>{wo.photos_submitted}/{wo.photos_required}</span>
                        </div>
                        <span className={`text-xs font-bold ${pct >= 100 ? 'text-green-400' : 'text-gray-500'}`}>
                          {pct >= 100 ? '✅ Complete' : pct > 0 ? `${100 - pct}% missing` : '❌ No photos'}
                        </span>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}
          </div>
          );
        })()}

        {/* ════════════════════════════════════════════════════
            TAB: SCANBACKS
        ════════════════════════════════════════════════════ */}
        {activeTab === 'scanbacks' && (
          <div>
            <div className="mb-6 flex items-center justify-between">
              <div>
                <h2 className="text-3xl font-bold mb-1">📸 Scanbacks</h2>
                <p className="text-gray-400">{scanbacks.length} orders in document pipeline — mandatory QC due diligence on every review</p>
              </div>
              <div className="flex gap-1 bg-gray-800 rounded-lg p-1">
                {[
                  { key: 'all', label: 'All', color: '' },
                  { key: 'Awaiting Upload', label: '⏳ Awaiting', color: 'text-gray-400' },
                  { key: 'Needs Review', label: '🔍 Review', color: 'text-blue-400' },
                  { key: 'Errors Found', label: '🚨 Errors', color: 'text-red-400' },
                  { key: 'Clean', label: '✅ Clean', color: 'text-green-400' },
                ].map(f => {
                  const count = f.key === 'all' ? scanbacks.length : scanbacks.filter(s => s.status === f.key).length;
                  return (
                    <button key={f.key} onClick={() => setScanbackFilter(f.key)}
                      className={`px-3 py-1.5 rounded text-sm font-semibold transition flex items-center gap-1.5 ${scanbackFilter === f.key ? 'bg-gray-600 text-white' : 'text-gray-400 hover:text-white'}`}>
                      {f.label}
                      <span className={`text-[10px] font-bold px-1.5 rounded-full ${
                        scanbackFilter === f.key ? 'bg-white/20' : count > 0 ? 'bg-gray-700' : 'bg-gray-800 opacity-30'
                      }`}>{count}</span>
                    </button>
                  );
                })}
              </div>
            </div>

            <MandatoryQcDueDiligenceNotice compact className="mb-6" />

            {/* Summary Cards */}
            <div className="grid grid-cols-4 gap-4 mb-6">
              <StatCard label="Awaiting Upload" value={awaitingScanback.length} icon="⏳" color="yellow" sub="Agent hasn't submitted" />
              <StatCard label="Needs Review" value={needsReview.length} icon="🔍" color="blue" sub="Ready for QC inspection" />
              <StatCard label="Errors Found" value={errorsFound.length} icon="🚨" color="red" sub="Needs correction" />
              <StatCard label="Clean" value={scanbacks.filter(s => s.status === 'Clean').length} icon="✅" color="green" sub="Passed inspection" />
            </div>

            <div className="space-y-3">
              {filteredScanbacks.length === 0 && (
                <div className="bg-gray-800 border border-gray-700 rounded-xl p-10 text-center">
                  <p className="text-gray-500 text-lg">No scanbacks match this filter</p>
                  <p className="text-gray-600 text-sm mt-1">Orders appear here when they reach the QC Review or Documentation stage</p>
                </div>
              )}
              {filteredScanbacks.map(sb => {
                const svc = SERVICE_COLORS[sb.type];
                const isExpanded = selectedScanback === sb.id;
                const statusStyle = sb.status === 'Clean' ? 'bg-green-600 text-white'
                  : sb.status === 'Errors Found' ? 'bg-red-600 text-white'
                  : sb.status === 'Needs Review' ? 'bg-blue-600 text-white'
                  : 'bg-gray-600 text-gray-300';

                const reviewScanback = async (action: 'clean' | 'errors') => {
                  try {
                    const res = await api.patch(`/prism/orders/${sb.orderId}/scanback/review`, {
                      action,
                      reviewer: 'Dee Davis',
                      errors: action === 'errors' ? [{ severity: 'CRITICAL', page: 1, description: 'Issue flagged by reviewer' }] : [],
                    });
                    if (res?.order) {
                      setOrders(prev => prev.map(o => o.id === sb.orderId ? { ...o, ...res.order } : o));
                    }
                  } catch (err) { console.error('Review failed:', err); }
                };

                return (
                  <div key={sb.id} className="bg-gray-800 border border-gray-700 rounded-xl overflow-hidden hover:border-gray-600 transition"
                    style={{ borderLeftWidth: '5px', borderLeftColor: svc?.color, backgroundColor: svc?.color + '08' }}>
                    <div className="px-4 py-3 flex items-center justify-between cursor-pointer"
                      onClick={() => setSelectedScanback(isExpanded ? null : sb.id)}>
                      <div className="flex items-center gap-3">
                        <ServiceBadge type={sb.type} />
                        <div>
                          <span className="font-mono text-xs text-gray-400">{sb.orderId}</span>
                          <p className="text-sm text-white font-semibold">{sb.signer || sb.client}</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-3">
                        <span className="text-sm text-gray-400">{sb.agent}</span>
                        {sb.attempt > 0 && (
                          <span className="text-xs text-gray-500">{sb.pages}/{sb.expected} pg · Attempt #{sb.attempt}</span>
                        )}
                        <span className={`px-2.5 py-1 rounded-full text-xs font-bold ${statusStyle}`}>
                          {sb.status}
                        </span>
                        <span className="text-gray-500 text-sm">{isExpanded ? '▲' : '▼'}</span>
                      </div>
                    </div>

                    {isExpanded && (
                      <div className="border-t border-gray-700 px-5 py-4">
                        {/* Upload Info */}
                        <div className="grid grid-cols-4 gap-4 mb-4 text-sm">
                          <div>
                            <span className="text-gray-500 text-xs block mb-0.5">Upload Date</span>
                            <span className="text-gray-200">{sb.uploadDate ? new Date(sb.uploadDate).toLocaleString() : '—'}</span>
                          </div>
                          <div>
                            <span className="text-gray-500 text-xs block mb-0.5">Attempt</span>
                            <span className="text-gray-200">{sb.attempt > 0 ? `#${sb.attempt}` : 'No upload'}</span>
                          </div>
                          <div>
                            <span className="text-gray-500 text-xs block mb-0.5">Page Count</span>
                            {sb.attempt > 0
                              ? (sb.pages >= sb.expected
                                  ? <span className="text-green-400 font-bold">✅ {sb.pages}/{sb.expected}</span>
                                  : <span className="text-red-400 font-bold">❌ {sb.pages}/{sb.expected}</span>)
                              : <span className="text-gray-500">—</span>
                            }
                          </div>
                          <div>
                            <span className="text-gray-500 text-xs block mb-0.5">Reviewed By</span>
                            <span className="text-gray-200">{sb.reviewed_by || '—'}</span>
                          </div>
                        </div>

                        {/* Errors Section */}
                        {sb.errors && sb.errors.length > 0 && (
                          <div className="mb-4">
                            <h4 className="text-sm font-bold text-red-400 mb-2">Inspection Errors ({sb.errors.length})</h4>
                            <div className="space-y-2">
                              {sb.errors.map((err, i) => (
                                <div key={i} className={`px-3 py-2.5 rounded-lg text-sm border ${
                                  err.severity === 'CRITICAL' ? 'bg-red-500/10 border-red-500/40' : 'bg-yellow-500/10 border-yellow-500/40'
                                }`}>
                                  <div className="flex items-center gap-2 mb-1">
                                    <span className={`text-[10px] font-black px-2 py-0.5 rounded ${
                                      err.severity === 'CRITICAL' ? 'bg-red-600 text-white' : 'bg-yellow-600 text-white'
                                    }`}>{err.severity}</span>
                                    <span className="text-xs text-gray-500">Page {err.page}</span>
                                  </div>
                                  <p className="text-gray-300">{err.description}</p>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}

                        {/* Scanback due diligence — same QC context as order slide-out (signing agent / notary = SERVICE_INSPECTION fundamentals) */}
                        {SERVICE_INSPECTION[sb.type] && (() => {
                          const insp = SERVICE_INSPECTION[sb.type];
                          const isSigningLane = ['notary', 'ron', 'apostille', 'process'].includes(sb.type);
                          return (
                            <div className={`mb-4 rounded-xl border p-4 ${
                              isSigningLane ? 'border-pink-500/30 bg-pink-500/5' : 'border-gray-600 bg-gray-800/50'
                            }`}>
                              <h4 className="text-sm font-bold text-white mb-0.5">
                                Mandatory QC due diligence — {insp.title}
                              </h4>
                              <p className="text-xs text-gray-500 mb-2">
                                {isSigningLane
                                  ? 'Loan signing & notary: verify uploads against these fundamentals before marking clean (same engine as order Mandatory QC).'
                                  : 'Match uploaded documentation to these checks before review — required for every service lane.'}
                              </p>
                              <ul className="text-xs text-gray-300 space-y-1.5 max-h-36 overflow-y-auto pr-1">
                                {insp.fundamentals.map((rule) => (
                                  <li key={rule.id} className="flex gap-2">
                                    <span className={`flex-shrink-0 text-[9px] font-bold px-1.5 py-0 rounded ${
                                      rule.severity === 'FATAL' ? 'bg-red-500/25 text-red-300' : 'bg-orange-500/20 text-orange-200'
                                    }`}>{rule.severity}</span>
                                    <span>{rule.check}</span>
                                  </li>
                                ))}
                              </ul>
                              <p className="text-[10px] text-gray-600 mt-2">Full fatal/common lists: PRISM → Inspection → select service.</p>
                            </div>
                          );
                        })()}

                        {/* DOT: operator “basics” brief (autopilot / audit) — PRISM API */}
                        {sb.type === 'dot' && (
                          <div className="mb-4 rounded-xl border border-orange-500/30 bg-orange-500/5 p-4">
                            <h4 className="text-sm font-bold text-orange-200 mb-1">DOT — operator due diligence (scanback)</h4>
                            <p className="text-xs text-gray-500 mb-2">Experienced collectors: small misses void collections. 49 CFR Part 40.</p>
                            {dotDueDiligenceLoad === 'loading' && (
                              <p className="text-xs text-gray-500">Loading brief…</p>
                            )}
                            {dotDueDiligenceLoad === 'error' && (
                              <p className="text-xs text-red-300">Could not load <code className="bg-gray-900 px-1 rounded">/prism/dot/collector-due-diligence</code></p>
                            )}
                            {dotDueDiligenceLoad === 'ok' && dotDueDiligence && (
                              <ul className="text-xs text-gray-300 space-y-2 max-h-48 overflow-y-auto">
                                {(dotDueDiligence.reminders || []).map((r) => (
                                  <li key={r.order} className="border-l-2 border-orange-500/50 pl-2">
                                    <span className="font-bold text-white">{r.order}. {r.title}</span>
                                    <p className="text-gray-400 mt-0.5 leading-snug">{r.body}</p>
                                  </li>
                                ))}
                              </ul>
                            )}
                          </div>
                        )}

                        {/* Awaiting Upload State */}
                        {sb.status === 'Awaiting Upload' && (
                          <div className="mb-4 p-4 rounded-lg border-2 border-dashed border-yellow-500/30 bg-yellow-500/5 text-center">
                            <p className="text-yellow-400 font-bold mb-1">⏳ Awaiting Document Upload</p>
                            <p className="text-gray-500 text-sm">Agent has not yet submitted documents for this order</p>
                          </div>
                        )}

                        {/* Action Buttons */}
                        <div className="flex gap-2 flex-wrap">
                          {sb.status === 'Needs Review' && (
                            <>
                              <button onClick={() => reviewScanback('clean')}
                                className="bg-green-600 hover:bg-green-700 px-4 py-2 rounded-lg font-bold text-sm transition shadow-sm">
                                ✅ Mark Clean
                              </button>
                              <button onClick={() => reviewScanback('errors')}
                                className="bg-red-600 hover:bg-red-700 px-4 py-2 rounded-lg font-bold text-sm transition shadow-sm">
                                🚨 Flag Errors
                              </button>
                            </>
                          )}
                          {sb.status === 'Errors Found' && (
                            <button className="bg-orange-600 hover:bg-orange-700 px-4 py-2 rounded-lg font-bold text-sm transition shadow-sm">
                              📩 Request Correction
                            </button>
                          )}
                          <button onClick={() => { setSelectedOrder(sb.orderId); setActiveTab('orders'); }}
                            className="bg-gray-700 hover:bg-gray-600 px-4 py-2 rounded-lg font-semibold text-sm transition">
                            📋 View Order
                          </button>
                        </div>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* ════════════════════════════════════════════════════
            TAB: FIELD AGENTS
        ════════════════════════════════════════════════════ */}
        {activeTab === 'agents' && (
          <div>
            <div className="mb-6 flex items-center justify-between">
              <div>
                <h2 className="text-3xl font-bold mb-1">👤 Field Agents</h2>
                <p className="text-gray-400">{agents.length} agents in network — must meet lane credentials for mandatory QC due diligence</p>
              </div>
              <div className="flex gap-2">
                <select value={agentFilter} onChange={e => setAgentFilter(e.target.value)}
                  className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-1.5 text-sm text-gray-300">
                  <option value="all">All Status</option>
                  <option value="Active">Active</option>
                  <option value="Screening">Screening</option>
                  <option value="Suspended">Suspended</option>
                </select>
                <button className="bg-orange-500 hover:bg-orange-600 px-4 py-2 rounded-lg font-semibold text-sm transition">
                  + Add Agent
                </button>
              </div>
            </div>

            <MandatoryQcDueDiligenceNotice compact className="mb-6" />

            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
              {filteredAgents.map(agent => (
                <div key={agent.id} className="bg-gray-800 border border-gray-700 rounded-xl p-5 hover:border-gray-600 transition cursor-pointer">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-gradient-to-br from-orange-500 to-amber-600 rounded-full flex items-center justify-center text-white font-bold">
                        {agent.name.split(' ').map(n => n[0]).join('')}
                      </div>
                      <div>
                        <p className="font-bold">{agent.name}</p>
                        <p className="text-xs text-gray-500">{agent.id} • {agent.city}, {agent.state}</p>
                      </div>
                    </div>
                    <span className={`px-2 py-0.5 rounded-full text-xs font-semibold ${
                      agent.status === 'Active' ? 'bg-green-500/20 text-green-400' :
                      agent.status === 'Screening' ? 'bg-yellow-500/20 text-yellow-400' :
                      'bg-red-500/20 text-red-400'
                    }`}>{agent.status}</span>
                  </div>

                  <div className="flex flex-wrap gap-1 mb-3">
                    {agent.specialties.map(s => (
                      <span key={s} className="px-2 py-0.5 bg-gray-700 text-gray-300 rounded text-xs font-semibold">{s}</span>
                    ))}
                  </div>

                  {agent.status === 'Active' && (
                    <>
                      <div className="grid grid-cols-2 gap-2 mb-3">
                        <div className="bg-gray-700/50 rounded-lg p-2 text-center">
                          <p className="text-lg font-bold text-green-400">{agent.completionRate}%</p>
                          <p className="text-[10px] text-gray-500 uppercase">Completion</p>
                        </div>
                        <div className="bg-gray-700/50 rounded-lg p-2 text-center">
                          <p className="text-lg font-bold text-blue-400">{agent.onTimeRate}%</p>
                          <p className="text-[10px] text-gray-500 uppercase">On-Time</p>
                        </div>
                        <div className="bg-gray-700/50 rounded-lg p-2 text-center">
                          <p className={`text-lg font-bold ${agent.errorRate <= 2 ? 'text-green-400' : agent.errorRate <= 5 ? 'text-yellow-400' : 'text-red-400'}`}>{agent.errorRate}%</p>
                          <p className="text-[10px] text-gray-500 uppercase">Error Rate</p>
                        </div>
                        <div className="bg-gray-700/50 rounded-lg p-2 text-center">
                          <p className="text-lg font-bold text-yellow-400">⭐ {agent.rating}</p>
                          <p className="text-[10px] text-gray-500 uppercase">Rating</p>
                        </div>
                      </div>
                      <div className="flex items-center justify-between text-xs text-gray-500">
                        <span>{agent.ordersCompleted} orders completed</span>
                        <span>{agent.activeOrders} active now</span>
                      </div>
                    </>
                  )}

                  {agent.status === 'Screening' && (
                    <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-lg p-3 text-center">
                      <p className="text-yellow-400 text-sm font-semibold">Background check in progress</p>
                      <p className="text-xs text-gray-500 mt-1">Awaiting clearance before activation</p>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* ════════════════════════════════════════════════════
            TAB: CLIENTS
        ════════════════════════════════════════════════════ */}
        {activeTab === 'clients' && (
          <div>
            <div className="mb-6 flex items-center justify-between">
              <div>
                <h2 className="text-3xl font-bold mb-1">🏢 Clients</h2>
                <p className="text-gray-400">{clients.length} active clients</p>
              </div>
              <button className="bg-orange-500 hover:bg-orange-600 px-4 py-2 rounded-lg font-semibold text-sm transition">
                + Add Client
              </button>
            </div>

            <MandatoryQcDueDiligenceNotice compact className="mb-6" />

            <div className="space-y-4">
              {clients.map(client => (
                <div key={client.id} className="bg-gray-800 border border-gray-700 rounded-xl p-5 hover:border-gray-600 transition cursor-pointer">
                  <div className="flex items-center justify-between mb-3">
                    <div>
                      <div className="flex items-center gap-3">
                        <h3 className="text-lg font-bold">{client.name}</h3>
                        <span className={`px-2 py-0.5 rounded-full text-xs font-semibold ${
                          client.type.includes('Blueprint') ? 'bg-purple-500/20 text-purple-400 border border-purple-500/30' :
                          client.type === 'Title Company' ? 'bg-blue-500/20 text-blue-400 border border-blue-500/30' :
                          'bg-gray-500/20 text-gray-400 border border-gray-500/30'
                        }`}>{client.type}</span>
                      </div>
                      <p className="text-xs text-gray-500">{client.id}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-lg font-bold text-green-400">${client.revenue.toLocaleString()}</p>
                      <p className="text-xs text-gray-500">total revenue</p>
                    </div>
                  </div>

                  <div className="flex flex-wrap gap-1 mb-3">
                    {client.services.map(s => {
                      const key = Object.keys(SERVICE_COLORS).find(k => SERVICE_COLORS[k].label === s);
                      return key ? <ServiceBadge key={s} type={key} /> : <span key={s} className="px-2 py-0.5 bg-gray-700 text-gray-300 rounded-full text-xs">{s}</span>;
                    })}
                  </div>

                  <div className="flex items-center justify-between text-sm">
                    <div className="flex gap-6">
                      <span className="text-gray-400">{client.orders} orders</span>
                      {client.retainer > 0 && <span className="text-purple-400">Retainer: ${client.retainer.toLocaleString()}/yr</span>}
                    </div>
                    <span className="px-2 py-0.5 bg-green-500/20 text-green-400 rounded-full text-xs font-semibold">{client.status}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* ════════════════════════════════════════════════════
            TAB: INSPECTION
        ════════════════════════════════════════════════════ */}
        {activeTab === 'inspection' && (() => {
          const inspectionTypes = Object.keys(SERVICE_INSPECTION);
          const current = SERVICE_INSPECTION[inspSvc] || SERVICE_INSPECTION['dot'];
          const svcColor = SERVICE_COLORS[inspSvc];
          const totalRules = Object.values(SERVICE_INSPECTION).reduce((sum, s) => sum + s.fundamentals.length, 0);

          return (
          <div>
            <div className="mb-4">
              <h2 className="text-3xl font-bold mb-1">🔍 Inspection Engine</h2>
              <p className="text-gray-400">Authoritative rule sets for mandatory QC due diligence across all PRISM service systems</p>
            </div>

            <MandatoryQcDueDiligenceNotice compact className="mb-6" />

            {/* Stats Bar */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
              <StatCard label="Service Modules" value={inspectionTypes.length} icon="📋" color="orange" sub="Active inspection engines" />
              <StatCard label="Total Rules" value={totalRules} icon="📐" color="blue" sub="Across all services" />
              <StatCard label="Fatal Flaw Rules" value={Object.values(SERVICE_INSPECTION).reduce((s, v) => s + v.fatalFlaws.length, 0)} icon="🚨" color="red" sub="Zero-tolerance checks" />
              <StatCard label="Certifications Tracked" value={Object.values(SERVICE_INSPECTION).reduce((s, v) => s + v.certs.length, 0)} icon="🎓" color="green" sub="Agent requirements" />
            </div>

            {/* Service Selector */}
            <div className="flex flex-wrap gap-2 mb-6">
              {inspectionTypes.map(key => {
                const svc = SERVICE_COLORS[key];
                const insp = SERVICE_INSPECTION[key];
                return (
                  <button key={key} onClick={() => setInspSvc(key)}
                    className={`px-3 py-2 rounded-lg text-sm font-bold transition border ${inspSvc === key ? 'ring-2 ring-offset-1 ring-offset-gray-900 shadow-lg' : 'opacity-50 hover:opacity-90'}`}
                    style={{
                      borderColor: svc?.color || '#6B7280',
                      backgroundColor: inspSvc === key ? svc?.solid : 'transparent',
                      color: inspSvc === key ? '#FFFFFF' : (svc?.color || '#9CA3AF'),
                      ...(inspSvc === key ? { ringColor: svc?.color } : {}),
                    }}>
                    {svc?.icon} {insp.title.split('/')[0].split('(')[0].trim()}
                  </button>
                );
              })}
            </div>

            {/* Active Module Header */}
            <div className="bg-gray-800 border border-gray-700 rounded-xl p-5 mb-6" style={{ borderLeftWidth: '5px', borderLeftColor: svcColor?.color, backgroundColor: svcColor?.color + '12' }}>
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-xl font-bold">{current.title}</h3>
                <span className="px-3 py-1 rounded-full text-xs font-bold shadow-sm" style={{ backgroundColor: svcColor?.solid, color: '#FFFFFF' }}>
                  {current.fundamentals.length} Checks
                </span>
              </div>
              <p className="text-gray-400 text-sm">{current.fundamentals.filter(f => f.severity === 'FATAL').length} fatal flaw checks · {current.fundamentals.filter(f => f.severity === 'CRITICAL').length} critical checks · {current.certs.length} certifications required</p>
            </div>

            {/* Required Certifications (CTPA) */}
            <div className="mb-6">
              <h3 className="text-lg font-bold mb-3">🎓 Required Agent Certifications</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {current.certs.map((cert, i) => (
                  <div key={i} className="bg-gray-800 border border-gray-700 rounded-lg p-4 flex items-center gap-3 hover:border-gray-600 transition">
                    <div className="w-8 h-8 bg-green-500/20 text-green-400 rounded-full flex items-center justify-center font-bold text-sm flex-shrink-0">✓</div>
                    <p className="text-sm font-semibold">{cert}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Fundamentals Checklist */}
            <div className="mb-6">
              <h3 className="text-lg font-bold mb-3">📐 Inspection Fundamentals</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {current.fundamentals.map((rule, i) => (
                  <div key={rule.id} className="bg-gray-800 border border-gray-700 rounded-lg p-4 flex items-center gap-4 hover:border-gray-600 transition">
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm flex-shrink-0 ${
                      rule.severity === 'FATAL' ? 'bg-red-500/20 text-red-400' : rule.severity === 'CRITICAL' ? 'bg-orange-500/20 text-orange-400' : 'bg-blue-500/20 text-blue-400'
                    }`}>{i + 1}</div>
                    <div className="flex-1">
                      <p className="text-sm font-semibold">{rule.check}</p>
                      <div className="flex items-center gap-2 mt-1">
                        <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${
                          rule.severity === 'FATAL' ? 'bg-red-500/20 text-red-400' : rule.severity === 'CRITICAL' ? 'bg-orange-500/20 text-orange-400' : 'bg-blue-500/20 text-blue-400'
                        }`}>{rule.severity}</span>
                        <span className="text-[10px] text-gray-500">{rule.id}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Fatal Flaws */}
            <div className="mb-6">
              <h3 className="text-lg font-bold mb-3 text-red-400">🚨 Fatal Flaws — Zero Tolerance</h3>
              <div className="bg-gray-800 border border-red-500/30 rounded-xl p-5">
                <div className="space-y-2">
                  {current.fatalFlaws.map((flaw, i) => (
                    <div key={i} className="flex items-start gap-3 text-sm">
                      <span className="text-red-400 font-bold mt-0.5">✕</span>
                      <span className="text-gray-300">{flaw}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Common Errors */}
            <div className="mb-6">
              <h3 className="text-lg font-bold mb-3">⚠️ Common Errors to Watch</h3>
              <div className="bg-gray-800 border border-yellow-500/30 rounded-xl p-5">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                  {current.commonErrors.map((err, i) => (
                    <div key={i} className="flex items-center gap-2 text-sm">
                      <span className="text-yellow-400">⚠</span>
                      <span className="text-gray-300">{err}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* DOT: operator due diligence (same lane as signing-agent “never skip basics” — loaded from PRISM API) */}
            {inspSvc === 'dot' && (
              <div className="mb-6">
                <h3 className="text-lg font-bold mb-1 text-orange-300">🛡️ Mandatory QC due diligence — DOT operator basics</h3>
                <p className="text-sm text-gray-500 mb-3">Experienced collectors: audit risk from autopilot, not ignorance. Sourced from PRISM DOT compliance engine.</p>
                {dotDueDiligenceLoad === 'loading' && (
                  <div className="bg-gray-800 border border-gray-700 rounded-xl p-5 text-sm text-gray-400">Loading due diligence brief…</div>
                )}
                {dotDueDiligenceLoad === 'error' && (
                  <div className="bg-gray-800 border border-red-500/30 rounded-xl p-5 text-sm text-red-300">
                    Could not load due diligence (is the API running?). Endpoint: <code className="text-xs bg-gray-900 px-1 rounded">GET /prism/dot/collector-due-diligence</code>
                  </div>
                )}
                {dotDueDiligenceLoad === 'ok' && dotDueDiligence && (
                  <div className="space-y-4">
                    <div className="bg-gray-800 border border-orange-500/30 rounded-xl p-5" style={{ borderLeftWidth: '5px', borderLeftColor: SERVICE_COLORS.dot.color }}>
                      <h4 className="font-bold text-white mb-1">{dotDueDiligence.title || 'DOT collector due diligence'}</h4>
                      {dotDueDiligence.summary && <p className="text-sm text-gray-300 mb-0">{dotDueDiligence.summary}</p>}
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      {(dotDueDiligence.reminders || []).map((r) => (
                        <div key={r.order} className="bg-gray-800 border border-gray-700 rounded-lg p-4 flex gap-3">
                          <div className="w-9 h-9 rounded-full flex items-center justify-center font-bold text-sm flex-shrink-0 bg-orange-500/20 text-orange-300">{r.order}</div>
                          <div>
                            <p className="text-sm font-bold text-white mb-1">{r.title}</p>
                            <p className="text-sm text-gray-300 leading-relaxed">{r.body}</p>
                            <div className="flex flex-wrap gap-2 mt-2">
                              {r.reference && <span className="text-[10px] px-1.5 py-0.5 rounded bg-gray-700 text-gray-400">{r.reference}</span>}
                              {r.prism_workflow_ref && <span className="text-[10px] px-1.5 py-0.5 rounded bg-red-500/10 text-red-300">{r.prism_workflow_ref}</span>}
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                    {dotDueDiligence.mindset && (
                      <div className="bg-gray-800/80 border border-gray-600 rounded-xl p-4">
                        <p className="text-xs text-gray-500 uppercase mb-1">Mindset</p>
                        <p className="text-sm text-gray-200 leading-relaxed">{dotDueDiligence.mindset}</p>
                      </div>
                    )}
                    {dotDueDiligence.closing && (
                      <p className="text-center text-sm font-semibold text-orange-300/90 py-2">{dotDueDiligence.closing}</p>
                    )}
                  </div>
                )}
              </div>
            )}

            {/* Adaptive Learning */}
            <div>
              <h3 className="text-lg font-bold mb-3">🧠 Adaptive Learning</h3>
              <div className="grid grid-cols-3 gap-4 mb-4">
                <div className="bg-gray-800 border border-gray-700 rounded-xl p-4 text-center">
                  <p className="text-xs text-gray-500 uppercase mb-1">Level 1: Rule-Based</p>
                  <p className="text-2xl font-bold text-green-400">{totalRules}</p>
                  <p className="text-xs text-gray-500">Active rules</p>
                </div>
                <div className="bg-gray-800 border border-gray-700 rounded-xl p-4 text-center">
                  <p className="text-xs text-gray-500 uppercase mb-1">Level 2: Learned Patterns</p>
                  <p className="text-2xl font-bold text-blue-400">{scanbacks.length}</p>
                  <p className="text-xs text-gray-500">From QC reviews</p>
                </div>
                <div className="bg-gray-800 border border-gray-700 rounded-xl p-4 text-center">
                  <p className="text-xs text-gray-500 uppercase mb-1">Level 3: Anomalies</p>
                  <p className="text-2xl font-bold text-purple-400">0</p>
                  <p className="text-xs text-gray-500">Needs more data</p>
                </div>
              </div>
            </div>
          </div>
          );
        })()}

        {/* ════════════════════════════════════════════════════
            TAB: PAYMENTS
        ════════════════════════════════════════════════════ */}
        {activeTab === 'payments' && (
          <div>
            <div className="mb-6">
              <h2 className="text-3xl font-bold mb-1">💰 Payments</h2>
              <p className="text-gray-400">Agent payouts & margin tracking — gated on mandatory QC due diligence (clean scanback / order verification)</p>
            </div>

            <MandatoryQcDueDiligenceNotice compact className="mb-6" />

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
              <StatCard label="Pending Payouts" value={prismStats?.pending_payouts || '$0'} icon="⏳" color="yellow" />
              <StatCard label="Paid This Month" value={prismStats?.paid_this_month || '$0'} icon="✅" color="green" />
              <StatCard label="Revenue This Month" value={prismStats?.monthly_revenue || '$0'} icon="💰" color="blue" />
              <StatCard label="Avg Margin" value={prismStats?.avg_margin || '—'} icon="📈" color="purple" />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Pending Payments */}
              <div>
                <h3 className="text-lg font-bold mb-3">Pending Payouts</h3>
                <div className="bg-gray-800 border border-gray-700 rounded-xl overflow-hidden">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-gray-700 text-gray-400 text-xs uppercase">
                        <th className="text-left px-4 py-3">Agent</th>
                        <th className="text-left px-4 py-3">Order</th>
                        <th className="text-right px-4 py-3">Amount</th>
                        <th className="text-right px-4 py-3">Status</th>
                      </tr>
                    </thead>
                    <tbody>
                      {orders.filter(o => ['Verified', 'Completed'].includes(o.status)).slice(0, 5).map((o, i) => ({
                        agent: o.agent || 'Unassigned', order: o.id, amount: o.fee, status: o.status === 'Verified' ? 'Approved' : 'Pending',
                      })).map((p, i) => (
                        <tr key={i} className="border-b border-gray-700/50 hover:bg-gray-700/30 transition">
                          <td className="px-4 py-3 font-semibold">{p.agent}</td>
                          <td className="px-4 py-3 font-mono text-xs text-gray-500">{p.order}</td>
                          <td className="px-4 py-3 text-right text-green-400 font-semibold">${p.amount}</td>
                          <td className="px-4 py-3 text-right">
                            <span className={`px-2 py-0.5 rounded-full text-xs font-semibold ${
                              p.status === 'Approved' ? 'bg-green-500/20 text-green-400' :
                              p.status.includes('Hold') ? 'bg-red-500/20 text-red-400' :
                              'bg-yellow-500/20 text-yellow-400'
                            }`}>{p.status}</span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Margin Report */}
              <div>
                <h3 className="text-lg font-bold mb-3">Margin by Service Type</h3>
                <div className="space-y-3">
                  {Object.entries(orders.reduce((acc: Record<string, { type: string; revenue: number; cost: number; orders: number }>, o) => {
                    if (!acc[o.type]) acc[o.type] = { type: o.type, revenue: 0, cost: 0, orders: 0 };
                    acc[o.type].revenue += o.fee || 0;
                    const costRate = 1 - (SERVICE_MARGIN_RATES[o.type] || 0.40);
                    acc[o.type].cost += Math.round((o.fee || 0) * costRate);
                    acc[o.type].orders += 1;
                    return acc;
                  }, {})).map(([, m]) => m).sort((a, b) => b.revenue - a.revenue).slice(0, 5).map(m => {
                    const margin = Math.round(((m.revenue - m.cost) / m.revenue) * 100);
                    const svc = SERVICE_COLORS[m.type];
                    return (
                      <div key={m.type} className="bg-gray-800 border border-gray-700 rounded-lg p-4" style={{ borderLeftWidth: '5px', borderLeftColor: svc?.color, backgroundColor: svc?.color + '10' }}>
                        <div className="flex items-center justify-between mb-2">
                          <ServiceBadge type={m.type} />
                          <span className="text-xs text-gray-400 font-semibold">{m.orders} orders</span>
                        </div>
                        <div className="flex items-center justify-between">
                          <div className="flex gap-4 text-sm">
                            <span className="text-gray-400">Revenue: <span className="text-green-400">${m.revenue.toLocaleString()}</span></span>
                            <span className="text-gray-400">Cost: <span className="text-red-400">${m.cost.toLocaleString()}</span></span>
                          </div>
                          <span className="text-lg font-bold text-purple-400">{margin}%</span>
                        </div>
                        <div className="mt-2 h-2 bg-gray-700 rounded-full overflow-hidden">
                          <div className="h-full bg-gradient-to-r from-green-500 to-emerald-500 rounded-full" style={{ width: `${margin}%` }}></div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* ════════════════════════════════════════════════════
            TAB: ANALYTICS
        ════════════════════════════════════════════════════ */}
        {activeTab === 'analytics' && (
          <div>
            <div className="mb-6">
              <h2 className="text-3xl font-bold mb-1">📊 Analytics</h2>
              <p className="text-gray-400">Volume, quality, revenue, and agent performance — quality metrics track mandatory due diligence outcomes by lane</p>
            </div>

            <MandatoryQcDueDiligenceNotice compact className="mb-6" />

            {/* Volume by Service Type */}
            <div className="mb-8">
              <h3 className="text-lg font-bold mb-3">Volume by Service Type</h3>
              <div className="bg-gray-800 border border-gray-700 rounded-xl p-5">
                <div className="space-y-3">
                  {(() => {
                    const totals = orders.reduce((acc: Record<string, number>, o) => {
                      acc[o.type] = (acc[o.type] || 0) + 1; return acc;
                    }, {});
                    const total = orders.length || 1;
                    return Object.entries(totals).map(([type, count]) => ({
                      type, count, pct: Math.round((count / total) * 100),
                    })).sort((a, b) => b.count - a.count);
                  })().map(item => {
                    const svc = SERVICE_COLORS[item.type];
                    return (
                      <div key={item.type} className="flex items-center gap-4">
                        <div className="w-40"><ServiceBadge type={item.type} /></div>
                        <div className="flex-1">
                          <div className="h-6 bg-gray-700 rounded-full overflow-hidden">
                            <div className="h-full rounded-full flex items-center px-2" style={{ width: `${item.pct}%`, backgroundColor: svc?.solid }}>
                              {item.pct >= 10 && <span className="text-white text-xs font-bold">{item.count}</span>}
                            </div>
                          </div>
                        </div>
                        <span className="text-sm font-semibold text-gray-400 w-16 text-right">{item.count} ({item.pct}%)</span>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>

            {/* Quality Metrics */}
            <div className="mb-8">
              <h3 className="text-lg font-bold mb-3">Quality Metrics</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <StatCard label="First-Pass Rate" value={prismStats?.clean_rate || '—'} icon="✅" color="green" sub="Clean on first upload" />
                <StatCard label="Rejection Rate" value={prismStats?.rejection_rate || '—'} icon="🚫" color="red" sub="Post-ship rejections" />
                <StatCard label="Avg Correction Time" value={prismStats?.avg_correction_time || '—'} icon="⏱" color="yellow" sub="Time to fix errors" />
                <StatCard label="Most Common Error" value={prismStats?.common_error || '—'} icon="📝" color="orange" sub={prismStats?.common_error_pct || ''} />
              </div>
            </div>

            {/* Revenue Breakdown */}
            <div className="mb-8">
              <h3 className="text-lg font-bold mb-3">Revenue & Margin</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <StatCard label="Revenue (Month)" value={prismStats?.monthly_revenue || '$0'} icon="💰" color="green" />
                <StatCard label="Agent Costs" value={prismStats?.agent_costs || '$0'} icon="💸" color="red" />
                <StatCard label="Net Margin" value={prismStats?.net_margin || '$0'} icon="📈" color="purple" />
                <StatCard label="Margin %" value={prismStats?.margin_pct || '—'} icon="🎯" color="blue" />
              </div>
            </div>

            {/* Agent Utilization */}
            <div>
              <h3 className="text-lg font-bold mb-3">Agent Utilization</h3>
              <div className="bg-gray-800 border border-gray-700 rounded-xl p-5">
                <div className="space-y-3">
                  {agents.filter(a => a.status === 'Active').map(agent => {
                    const utilization = Math.min(Math.round((agent.activeOrders / 5) * 100), 100);
                    return (
                      <div key={agent.id} className="flex items-center gap-4">
                        <span className="w-32 text-sm font-semibold">{agent.name}</span>
                        <div className="flex-1 h-6 bg-gray-700 rounded-full overflow-hidden">
                          <div className={`h-full rounded-full ${utilization >= 80 ? 'bg-red-500' : utilization >= 50 ? 'bg-yellow-500' : 'bg-green-500'}`}
                            style={{ width: `${Math.max(utilization, 5)}%` }}></div>
                        </div>
                        <span className="text-sm text-gray-400 w-20 text-right">{agent.activeOrders}/5 slots</span>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          </div>
        )}

      </div>

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
              {/* Service Type Selection */}
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

              {/* Basic Fields */}
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
    </div>
  );
};

export default PRISMSystem;
