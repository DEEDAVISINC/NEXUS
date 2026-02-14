import React, { useState } from 'react';

interface FieldAgentPortalProps {
  onBackToNexus: () => void;
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

// ─── SERVICE TYPE COLORS (shared with PRISM) ──────────────────────
const SERVICE_COLORS: Record<string, { color: string; bg: string; label: string; icon: string; border: string }> = {
  'notary':        { color: '#F97316', bg: '#FFF7ED', label: 'Notary',              icon: '🟠', border: '#FB923C' },
  'ron':           { color: '#6366F1', bg: '#EEF2FF', label: 'Notary (RON)',        icon: '🟣', border: '#818CF8' },
  'dot':           { color: '#EF4444', bg: '#FEF2F2', label: 'Drug Test (DOT)',     icon: '🔴', border: '#F87171' },
  'non-dot':       { color: '#F43F5E', bg: '#FFF1F2', label: 'Drug Test (Non-DOT)', icon: '🔴', border: '#FB7185' },
  'dna':           { color: '#A855F7', bg: '#FAF5FF', label: 'DNA Collection',      icon: '🟣', border: '#C084FC' },
  'fingerprint':   { color: '#22C55E', bg: '#F0FDF4', label: 'Fingerprinting/EFT',  icon: '🟢', border: '#4ADE80' },
  'courier':       { color: '#3B82F6', bg: '#EFF6FF', label: 'Courier/Runner',      icon: '🔵', border: '#60A5FA' },
  'background':    { color: '#64748B', bg: '#F8FAFC', label: 'Background Check',    icon: '⚫', border: '#94A3B8' },
  'apostille':     { color: '#EAB308', bg: '#FEFCE8', label: 'Apostille',           icon: '🟡', border: '#FACC15' },
  'process':       { color: '#14B8A6', bg: '#F0FDFA', label: 'Process Serving',     icon: '🟢', border: '#2DD4BF' },
};

// ─── BADGES ────────────────────────────────────────────────────────
const ServiceBadge: React.FC<{ type: string; size?: 'sm' | 'md' }> = ({ type, size = 'sm' }) => {
  const svc = SERVICE_COLORS[type] || SERVICE_COLORS['notary'];
  const px = size === 'sm' ? 'px-2 py-0.5 text-xs' : 'px-3 py-1 text-sm';
  return (
    <span className={`${px} rounded-full font-semibold inline-flex items-center gap-1`}
      style={{ backgroundColor: svc.bg, color: svc.color, border: `1px solid ${svc.border}` }}>
      {svc.icon} {svc.label}
    </span>
  );
};

const StatusBadge: React.FC<{ status: string }> = ({ status }) => {
  const styles: Record<string, string> = {
    'New':                  'bg-blue-500/20 text-blue-400 border-blue-500/30',
    'Assigned':             'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
    'Confirmed':            'bg-cyan-500/20 text-cyan-400 border-cyan-500/30',
    'In Progress':          'bg-purple-500/20 text-purple-400 border-purple-500/30',
    'Completed':            'bg-green-500/20 text-green-400 border-green-500/30',
    'Scanned Back':         'bg-indigo-500/20 text-indigo-400 border-indigo-500/30',
    'Errors Found':         'bg-red-500/20 text-red-400 border-red-500/30',
    'Correction Requested': 'bg-red-500/20 text-red-300 border-red-500/30',
    'Verified':             'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
    'Closed':               'bg-gray-500/20 text-gray-400 border-gray-500/30',
  };
  return <span className={`px-2 py-0.5 rounded-full text-xs font-semibold border ${styles[status] || 'bg-gray-500/20 text-gray-400 border-gray-500/30'}`}>{status}</span>;
};

// ─── MOCK DATA — Sarah Chen's perspective ──────────────────────────
const agentProfile = {
  id: 'FA-0001',
  name: 'Sarah Chen',
  email: 'sarah.chen@email.com',
  phone: '(248) 555-1234',
  address: '1420 Maple Rd, Troy, MI 48084',
  city: 'Troy',
  state: 'MI',
  specialties: ['Signing Agent'],
  serviceRadius: 30,
  serviceZips: '48084, 48083, 48085, 48098, 48301, 48302, 48304, 48009, 48025, 48034',
  status: 'Active',
  notaryState: 'Michigan',
  notaryNumber: 'NC-2024-7729103',
  notaryExpiration: '09/15/2028',
  nnaExpiration: '03/22/2027',
  eoInsurance: true,
  eoPolicyNumber: 'ENO-8847291',
  eoExpiration: '06/30/2026',
  backgroundCleared: true,
  backgroundDate: '11/01/2025',
  equipment: ['Notary Stamp', 'Notary Journal', 'Vehicle'],
  paymentMethod: 'Direct Deposit',
  completionRate: 98,
  onTimeRate: 96,
  errorRate: 2,
  rating: 4.9,
  ordersCompleted: 147,
  totalEarned: 19850,
  dateJoined: '04/15/2025',
};

// ─── ORDER WORKFLOW STEPS ────────────────────────────────────────
// This is the gated lifecycle every order follows. Agent cannot skip steps.
const ORDER_WORKFLOW_STEPS = [
  { key: 'accept', label: 'Accept', icon: '📩', statusMatch: 'Assigned' },
  { key: 'start', label: 'Start', icon: '▶️', statusMatch: 'Confirmed' },
  { key: 'complete', label: 'Complete', icon: '✅', statusMatch: 'In Progress' },
  { key: 'scanback', label: 'Upload Scanback', icon: '📸', statusMatch: 'Completed' },
  { key: 'shipped', label: 'Shipped / Done', icon: '📦', statusMatch: 'Scanned Back' },
] as const;

function getWorkflowStep(status: string): number {
  switch (status) {
    case 'Assigned': return 0;
    case 'Confirmed': return 1;
    case 'In Progress': return 2;
    case 'Completed': return 3;
    case 'Scanned Back': return 4;
    case 'Correction Requested': return 3; // Back to scanback step
    case 'Verified': return 5; // Past all steps
    case 'Closed': return 5;
    default: return 0;
  }
}

const initialOrders = [
  {
    id: 'PRISM-2026-0001', type: 'notary', status: 'In Progress',
    signer: 'James Wilson', signerPhone: '(248) 555-8820', signerEmail: 'jwilson@email.com',
    address: '2847 Rochester Rd, Troy, MI 48084', date: '02/14/2026', time: '1:00 PM',
    client: 'Metro Title Co.', fee: 125, travelFee: 20, surcharge: 0,
    documentsAttached: true, pageCount: 47,
    rules: ['Scanbacks required', 'Blue pen only', 'Ship same day via FedEx', '2 copies — 1 for borrower'],
    specialInstructions: 'Refinance package. Borrower is elderly — be patient and thorough. Call 15 min before arrival.',
    appointmentConfirmed: true,
    shippingMethod: 'FedEx — drop at Troy FedEx Ship Center (1950 E Big Beaver)',
    scanbackUploaded: false, scanbackFiles: [] as string[],
  },
  {
    id: 'PRISM-2026-0008', type: 'ron', status: 'Confirmed',
    signer: 'Patricia Harris', signerPhone: '(313) 555-4410', signerEmail: 'pharris@email.com',
    address: 'Remote / Zoom', date: '02/14/2026', time: '2:30 PM',
    client: 'National Signing Co.', fee: 40, travelFee: 0, surcharge: 0,
    documentsAttached: true, pageCount: 12,
    rules: ['Scanbacks required', 'Black pen only'],
    specialInstructions: 'RON session via Notarize platform. Login link will be emailed 30 min before.',
    appointmentConfirmed: true,
    shippingMethod: 'Electronic submission',
    scanbackUploaded: false, scanbackFiles: [] as string[],
  },
  {
    id: 'PRISM-2026-0015', type: 'notary', status: 'Assigned',
    signer: 'Robert & Maria Gonzalez', signerPhone: '(248) 555-3301', signerEmail: 'rgonzalez@email.com',
    address: '5120 Livernois Rd, Rochester Hills, MI 48306', date: '02/15/2026', time: '10:00 AM',
    client: 'First American Title', fee: 150, travelFee: 20, surcharge: 0,
    documentsAttached: false, pageCount: 0,
    rules: ['Scanbacks required', 'Blue pen only', 'Legal paper for deed', 'Ship same day via FedEx', 'ID copies required'],
    specialInstructions: 'Purchase closing — 2 signers. Deed requires legal paper. Double-check both signers have valid photo ID.',
    appointmentConfirmed: false,
    shippingMethod: 'FedEx — drop at Rochester Hills FedEx (1180 Walton Blvd)',
    scanbackUploaded: false, scanbackFiles: [] as string[],
  },
  {
    id: 'PRISM-2026-0020', type: 'notary', status: 'Correction Requested',
    signer: 'Linda Park', signerPhone: '(248) 555-6612', signerEmail: 'lpark@email.com',
    address: '880 W Long Lake Rd, Bloomfield Hills, MI 48302', date: '02/12/2026', time: '3:00 PM',
    client: 'Homeland Title', fee: 175, travelFee: 20, surcharge: 50,
    documentsAttached: true, pageCount: 53,
    rules: ['Scanbacks required', 'Blue pen only', 'Ship same day via FedEx'],
    specialInstructions: 'Reverse mortgage. Extended appointment time.',
    appointmentConfirmed: true,
    shippingMethod: 'FedEx',
    scanbackUploaded: true, scanbackFiles: ['scanback_20260212.pdf'],
    corrections: [
      { severity: 'CRITICAL', page: 22, description: 'Notice of Right to Cancel — Date line is blank. Borrower must date this.' },
      { severity: 'CRITICAL', page: 41, description: 'Acknowledgement page — Missing borrower initials on line 3.' },
    ],
  },
  {
    id: 'PRISM-2026-0012', type: 'notary', status: 'Verified',
    signer: 'Michael Thompson', signerPhone: '(248) 555-9901', signerEmail: 'mthompson@email.com',
    address: '300 E Maple Rd, Birmingham, MI 48009', date: '02/11/2026', time: '11:00 AM',
    client: 'Metro Title Co.', fee: 125, travelFee: 0, surcharge: 0,
    documentsAttached: true, pageCount: 38,
    rules: ['Scanbacks required', 'Blue pen only'],
    specialInstructions: '',
    appointmentConfirmed: true,
    shippingMethod: 'FedEx',
    scanbackUploaded: true, scanbackFiles: ['scanback_20260211.pdf'],
  },
  {
    id: 'PRISM-2026-0009', type: 'notary', status: 'Closed',
    signer: 'Angela Martinez', signerPhone: '(248) 555-2244', signerEmail: 'amartinez@email.com',
    address: '1220 Woodward Ave, Royal Oak, MI 48067', date: '02/10/2026', time: '9:00 AM',
    client: 'First American Title', fee: 100, travelFee: 20, surcharge: 0,
    documentsAttached: true, pageCount: 22,
    rules: ['Scanbacks required'],
    specialInstructions: '',
    appointmentConfirmed: true,
    shippingMethod: 'FedEx',
    scanbackUploaded: true, scanbackFiles: ['scanback_20260210.pdf'],
  },
];

const myPayments = [
  { orderId: 'PRISM-2026-0009', signer: 'Angela Martinez', date: '02/10/2026', base: 100, travel: 20, surcharge: 0, total: 120, status: 'Paid', paidDate: '02/13/2026' },
  { orderId: 'PRISM-2026-0012', signer: 'Michael Thompson', date: '02/11/2026', base: 125, travel: 0, surcharge: 0, total: 125, status: 'Processing', paidDate: '' },
  { orderId: 'PRISM-2026-0020', signer: 'Linda Park', date: '02/12/2026', base: 175, travel: 20, surcharge: 50, total: 245, status: 'On Hold', paidDate: '' },
  { orderId: 'PRISM-2026-0001', signer: 'James Wilson', date: '02/14/2026', base: 125, travel: 20, surcharge: 0, total: 145, status: 'Pending', paidDate: '' },
  { orderId: 'PRISM-2026-0008', signer: 'Patricia Harris', date: '02/14/2026', base: 40, travel: 0, surcharge: 0, total: 40, status: 'Pending', paidDate: '' },
];

const notifications = [
  { id: 1, type: 'correction', message: 'Correction needed on PRISM-2026-0020 — 2 critical errors. Review and re-scan.', time: '2 hours ago', read: false },
  { id: 2, type: 'new-order', message: 'New order available — Notary signing in Troy, MI on 02/15. Accept?', time: '3 hours ago', read: false },
  { id: 3, type: 'payment', message: 'Payment of $120 sent for PRISM-2026-0009 (Angela Martinez).', time: '1 day ago', read: true },
  { id: 4, type: 'reminder', message: 'Appointment tomorrow at 1:00 PM — James Wilson, Troy, MI. Confirm?', time: '1 day ago', read: true },
  { id: 5, type: 'verified', message: 'Scanback for PRISM-2026-0012 verified — clean. Ready to ship.', time: '2 days ago', read: true },
];

// ─── MAIN COMPONENT ────────────────────────────────────────────────
// ─── COMPLIANCE DOCUMENT DATA ────────────────────────────────────────
type ComplianceDoc = {
  id: string;
  type: string;
  status: 'Missing' | 'Submitted' | 'Under Review' | 'Approved' | 'Expired' | 'Rejected';
  required: boolean;
  dateReceived?: string;
  dateApproved?: string;
  expirationDate?: string;
  policyNumber?: string;
  commissionNumber?: string;
  fileName?: string;
  fileSize?: string;
  notes?: string;
  rejectionReason?: string;
};

const complianceDocs: ComplianceDoc[] = [
  { id: 'doc-1', type: 'W-9', status: 'Approved', required: true, dateReceived: '04/15/2025', dateApproved: '04/15/2025', fileName: 'W9_SarahChen_2025.pdf', fileSize: '142 KB' },
  { id: 'doc-2', type: 'NDA / Confidentiality Agreement', status: 'Approved', required: true, dateReceived: '04/15/2025', dateApproved: '04/16/2025', fileName: 'NDA_SarahChen_Signed.pdf', fileSize: '98 KB' },
  { id: 'doc-3', type: 'Independent Contractor Agreement', status: 'Approved', required: true, dateReceived: '04/15/2025', dateApproved: '04/16/2025', fileName: 'ICA_SarahChen_Signed.pdf', fileSize: '215 KB' },
  { id: 'doc-4', type: 'Background Check', status: 'Approved', required: true, dateReceived: '04/20/2025', dateApproved: '11/01/2025', expirationDate: '11/01/2026', fileName: 'BGCheck_Cleared.pdf', fileSize: '67 KB' },
  { id: 'doc-5', type: 'Photo ID', status: 'Approved', required: true, dateReceived: '04/15/2025', dateApproved: '04/15/2025', fileName: 'ID_SarahChen.jpg', fileSize: '1.2 MB' },
  { id: 'doc-6', type: 'Notary Commission', status: 'Approved', required: true, dateReceived: '04/15/2025', dateApproved: '04/16/2025', expirationDate: '09/15/2028', commissionNumber: 'NC-2024-7729103', fileName: 'NotaryCommission_MI.pdf', fileSize: '340 KB' },
  { id: 'doc-7', type: 'NNA Signing Agent Certification', status: 'Approved', required: true, dateReceived: '04/15/2025', dateApproved: '04/16/2025', expirationDate: '03/22/2027', fileName: 'NNA_Cert_SarahChen.pdf', fileSize: '189 KB' },
  { id: 'doc-8', type: 'E&O Insurance', status: 'Approved', required: true, dateReceived: '04/18/2025', dateApproved: '04/19/2025', expirationDate: '06/30/2026', policyNumber: 'ENO-8847291', fileName: 'EO_Insurance_Policy.pdf', fileSize: '512 KB' },
  { id: 'doc-9', type: 'Vehicle Insurance', status: 'Expired', required: true, expirationDate: '01/31/2026', policyNumber: 'AUTO-334821', fileName: 'VehicleIns_2025.pdf', fileSize: '276 KB', dateReceived: '04/18/2025', dateApproved: '04/19/2025' },
  { id: 'doc-10', type: 'DOT Collector Certification', status: 'Missing', required: false, notes: 'Not required for current specialties' },
];

const FieldAgentPortal: React.FC<FieldAgentPortalProps> = ({ onBackToNexus, activeTab, setActiveTab }) => {
  const [selectedOrderId, setSelectedOrderId] = useState<string | null>(null);
  const [orderViewFilter, setOrderViewFilter] = useState<'active' | 'history'>('active');
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [uploadOrderId, setUploadOrderId] = useState('');
  const [uploadType, setUploadType] = useState<'scanback' | 'credential'>('scanback');
  const [uploadDocId, setUploadDocId] = useState('');
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [uploadStatus, setUploadStatus] = useState<'idle' | 'uploading' | 'success' | 'error'>('idle');
  const [showConfirmAccept, setShowConfirmAccept] = useState<string | null>(null);
  const [profileEditing, setProfileEditing] = useState(false);
  const [showNotifPanel, setShowNotifPanel] = useState(false);
  const [docs, setDocs] = useState<ComplianceDoc[]>(complianceDocs);
  const [orders, setOrders] = useState(initialOrders);

  // ─── WORKFLOW ADVANCE FUNCTIONS ───────────────────────────────
  const advanceOrder = (orderId: string, newStatus: string) => {
    setOrders(prev => prev.map(o => o.id === orderId ? { ...o, status: newStatus } : o));
  };

  const handleAcceptOrder = (orderId: string) => {
    advanceOrder(orderId, 'Confirmed');
    setShowConfirmAccept(null);
  };

  const handleStartOrder = (orderId: string) => {
    advanceOrder(orderId, 'In Progress');
  };

  const handleCompleteOrder = (orderId: string) => {
    advanceOrder(orderId, 'Completed');
  };

  const handleMarkShipped = (orderId: string) => {
    // Only available after scanback is uploaded
    const order = orders.find(o => o.id === orderId);
    if (order && order.scanbackUploaded) {
      advanceOrder(orderId, 'Scanned Back');
    }
  };

  const tabs = [
    { id: 'dashboard', label: '🏠 Dashboard' },
    { id: 'orders', label: '📋 My Orders' },
    { id: 'payments', label: '💰 Payments' },
    { id: 'profile', label: '👤 Profile' },
  ];

  // File handling
  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setSelectedFiles(prev => [...prev, ...Array.from(e.target.files!)]);
    }
  };

  const removeFile = (index: number) => {
    setSelectedFiles(prev => prev.filter((_, i) => i !== index));
  };

  const handleUploadSubmit = async () => {
    if (selectedFiles.length === 0) return;
    setUploadStatus('uploading');
    
    try {
      const formData = new FormData();
      
      if (uploadType === 'scanback') {
        // Scanback upload
        selectedFiles.forEach(f => formData.append('files', f));
        formData.append('order_id', uploadOrderId);
        
        try {
          const res = await fetch('http://localhost:5000/prism/scanback/upload', { method: 'POST', body: formData });
          if (res.ok) {
            const result = await res.json();
            console.log('Scanback upload result:', result);
          }
        } catch {
          // API not running — that's ok, still show success in UI
          console.log('API not available — scanback saved locally in state');
        }
      } else {
        // Credential upload
        formData.append('file', selectedFiles[0]);
        formData.append('compliance_id', uploadDocId);
        formData.append('document_type', docs.find(d => d.id === uploadDocId)?.type || '');
        formData.append('person_type', 'Field Agent');
        
        try {
          const res = await fetch('http://localhost:5000/prism/compliance/upload', { method: 'POST', body: formData });
          if (res.ok) {
            const result = await res.json();
            console.log('Compliance upload result:', result);
          }
        } catch {
          console.log('API not available — credential saved locally in state');
        }
      }
      
      setUploadStatus('success');
      
      // Update local state
      if (uploadType === 'scanback' && uploadOrderId) {
        // Mark the order's scanback as uploaded and advance status
        setOrders(prev => prev.map(o =>
          o.id === uploadOrderId
            ? { ...o, scanbackUploaded: true, scanbackFiles: [...o.scanbackFiles, ...selectedFiles.map(f => f.name)], status: 'Scanned Back' }
            : o
        ));
      } else if (uploadType === 'credential' && uploadDocId) {
        setDocs(prev => prev.map(d =>
          d.id === uploadDocId ? { ...d, status: 'Submitted' as const, dateReceived: new Date().toLocaleDateString(), fileName: selectedFiles[0]?.name, fileSize: `${(selectedFiles[0]?.size / 1024).toFixed(0)} KB` } : d
        ));
      }
      
      setTimeout(() => {
        setShowUploadModal(false);
        setSelectedFiles([]);
        setUploadStatus('idle');
        setUploadDocId('');
      }, 1500);
      
    } catch (err) {
      console.error('Upload error:', err);
      setUploadStatus('error');
      setTimeout(() => setUploadStatus('idle'), 3000);
    }
  };

  const openCredentialUpload = (docId: string) => {
    setUploadType('credential');
    setUploadDocId(docId);
    setUploadOrderId('');
    setSelectedFiles([]);
    setUploadStatus('idle');
    setShowUploadModal(true);
  };

  const openScanbackUpload = (orderId: string) => {
    setUploadType('scanback');
    setUploadOrderId(orderId);
    setUploadDocId('');
    setSelectedFiles([]);
    setUploadStatus('idle');
    setShowUploadModal(true);
  };

  // Compliance stats
  const requiredDocs = docs.filter(d => d.required);
  const approvedDocs = requiredDocs.filter(d => d.status === 'Approved');
  const missingDocs = requiredDocs.filter(d => d.status === 'Missing');
  const expiredDocs = docs.filter(d => d.status === 'Expired');
  const submittedDocs = docs.filter(d => d.status === 'Submitted' || d.status === 'Under Review');
  const compliancePercent = requiredDocs.length > 0 ? Math.round((approvedDocs.length / requiredDocs.length) * 100) : 0;

  const activeOrders = orders.filter(o => !['Verified', 'Closed'].includes(o.status));
  const historyOrders = orders.filter(o => ['Verified', 'Closed'].includes(o.status));
  const actionRequired = orders.filter(o => ['Assigned', 'Correction Requested'].includes(o.status));
  const todayOrders = orders.filter(o => o.date === '02/14/2026');
  const upcomingOrders = orders.filter(o => o.date > '02/14/2026' && !['Verified', 'Closed'].includes(o.status));
  const unreadNotifs = notifications.filter(n => !n.read).length;

  // ─── ORDER DETAIL VIEW ─────────────────────────────────────────
  const renderOrderDetail = (order: typeof orders[0]) => {
    const svc = SERVICE_COLORS[order.type];
    const currentStep = getWorkflowStep(order.status);
    const isFinished = ['Verified', 'Closed'].includes(order.status);

    return (
      <div>
        {/* Back button */}
        <button onClick={() => setSelectedOrderId(null)}
          className="flex items-center gap-2 text-gray-400 hover:text-white mb-4 transition text-sm">
          ← Back to Orders
        </button>

        {/* Order Header */}
        <div className="bg-gray-800 border border-gray-700 rounded-xl p-5 mb-4" style={{ borderLeftWidth: '5px', borderLeftColor: svc?.color }}>
          <div className="flex items-center justify-between mb-3">
            <div>
              <span className="text-xs font-mono text-gray-500">{order.id}</span>
              <div className="flex items-center gap-2 mt-1">
                <ServiceBadge type={order.type} size="md" />
                <StatusBadge status={order.status} />
              </div>
            </div>
            <div className="text-right">
              <p className="text-xl font-bold text-green-400">${order.fee + order.travelFee + order.surcharge}</p>
              <p className="text-xs text-gray-500">
                ${order.fee} fee{order.travelFee > 0 ? ` + $${order.travelFee} travel` : ''}{order.surcharge > 0 ? ` + $${order.surcharge} surcharge` : ''}
              </p>
            </div>
          </div>
        </div>

        {/* ═══ WORKFLOW TRACKER ═══ */}
        {!isFinished && (
          <div className="rounded-xl p-5 mb-4" style={{ background: '#1B2A4A', border: '1px solid rgba(45, 212, 191, 0.15)' }}>
            <h3 className="text-sm font-bold uppercase mb-4" style={{ color: '#2DD4BF' }}>📋 Order Workflow</h3>
            <div className="flex items-center justify-between mb-4">
              {ORDER_WORKFLOW_STEPS.map((step, i) => {
                const isCompleted = currentStep > i;
                const isCurrent = currentStep === i;
                const isFuture = currentStep < i;
                // Special case: correction requested goes back to scanback
                const isCorrectionStep = order.status === 'Correction Requested' && step.key === 'scanback';

                return (
                  <div key={step.key} className="flex flex-col items-center flex-1 relative">
                    {/* Connector line */}
                    {i > 0 && (
                      <div className="absolute top-4 -left-1/2 w-full h-0.5" style={{
                        background: isCompleted ? '#2DD4BF' : 'rgba(100, 116, 139, 0.3)',
                      }} />
                    )}
                    {/* Step circle */}
                    <div className={`relative z-10 w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold border-2 transition-all ${
                      isCompleted ? 'text-white' : isCurrent || isCorrectionStep ? 'text-white animate-pulse' : 'text-gray-600'
                    }`} style={{
                      background: isCompleted ? '#2DD4BF' : isCurrent ? '#EC4899' : isCorrectionStep ? '#EF4444' : 'rgba(30, 41, 59, 0.8)',
                      borderColor: isCompleted ? '#2DD4BF' : isCurrent ? '#EC4899' : isCorrectionStep ? '#EF4444' : 'rgba(100, 116, 139, 0.3)',
                      boxShadow: isCurrent ? '0 0 12px rgba(236, 72, 153, 0.4)' : isCorrectionStep ? '0 0 12px rgba(239, 68, 68, 0.4)' : 'none',
                    }}>
                      {isCompleted ? '✓' : step.icon}
                    </div>
                    {/* Step label */}
                    <p className={`text-[10px] mt-1.5 text-center font-semibold leading-tight ${
                      isCurrent || isCorrectionStep ? 'text-white' : isCompleted ? 'text-teal-400' : 'text-gray-600'
                    }`}>
                      {isCorrectionStep ? '⚠️ Re-upload' : step.label}
                    </p>
                  </div>
                );
              })}
            </div>

            {/* Current step action prompt */}
            <div className="rounded-lg p-3 text-center" style={{
              background: order.status === 'Correction Requested' ? 'rgba(239, 68, 68, 0.1)' : 'rgba(236, 72, 153, 0.08)',
              border: order.status === 'Correction Requested' ? '1px solid rgba(239, 68, 68, 0.3)' : '1px solid rgba(236, 72, 153, 0.2)',
            }}>
              {order.status === 'Assigned' && (
                <p className="text-sm font-semibold">📩 <b>Step 1:</b> Review the assignment details below, then accept or decline.</p>
              )}
              {order.status === 'Confirmed' && (
                <p className="text-sm font-semibold">▶️ <b>Step 2:</b> When you arrive at the appointment, tap "Start" to begin.</p>
              )}
              {order.status === 'In Progress' && (
                <p className="text-sm font-semibold">✅ <b>Step 3:</b> Complete the signing, then tap "Mark Complete".</p>
              )}
              {order.status === 'Completed' && (
                <p className="text-sm font-semibold">📸 <b>Step 4:</b> Upload your scanback documents now. This is required before payment.</p>
              )}
              {order.status === 'Scanned Back' && (
                <p className="text-sm font-semibold">📦 <b>Step 5:</b> Confirm shipping or mark as done. DDI will verify your scanback.</p>
              )}
              {order.status === 'Correction Requested' && (
                <p className="text-sm font-semibold text-red-400">🚨 Corrections were found in your scanback. Fix and re-upload the corrected pages below.</p>
              )}
            </div>
          </div>
        )}

        {/* Finished order notice */}
        {isFinished && (
          <div className="rounded-xl p-4 mb-4 text-center" style={{ background: 'rgba(34, 197, 94, 0.08)', border: '1px solid rgba(34, 197, 94, 0.3)' }}>
            <p className="text-sm font-semibold text-green-400">
              {order.status === 'Verified' ? '✅ Scanback verified — payment processing' : '🏁 Order complete and closed'}
            </p>
          </div>
        )}

        {/* Signer / Subject Info */}
        <div className="bg-gray-800 border border-gray-700 rounded-xl p-5 mb-4">
          <h3 className="text-sm font-bold text-gray-400 uppercase mb-3">Signer / Subject</h3>
          <p className="text-xl font-bold mb-2">{order.signer}</p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
            <div className="flex items-center gap-2">
              <span className="text-gray-500">📞</span>
              <a href={`tel:${order.signerPhone}`} className="text-blue-400 hover:text-blue-300">{order.signerPhone}</a>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-gray-500">✉️</span>
              <a href={`mailto:${order.signerEmail}`} className="text-blue-400 hover:text-blue-300">{order.signerEmail}</a>
            </div>
            <div className="flex items-center gap-2 md:col-span-2">
              <span className="text-gray-500">📍</span>
              <span>{order.address}</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-gray-500">📅</span>
              <span className="font-semibold">{order.date} at {order.time}</span>
            </div>
          </div>
        </div>

        {/* Client Rules */}
        <div className="bg-gray-800 border border-gray-700 rounded-xl p-5 mb-4">
          <h3 className="text-sm font-bold text-gray-400 uppercase mb-3">📌 Client Rules</h3>
          <div className="space-y-2">
            {order.rules.map((rule, i) => (
              <div key={i} className="flex items-center gap-2 text-sm">
                <span className="font-bold" style={{ color: '#2DD4BF' }}>•</span>
                <span>{rule}</span>
              </div>
            ))}
          </div>
          {order.specialInstructions && (
            <div className="mt-4 bg-yellow-500/10 border border-yellow-500/30 rounded-lg p-3">
              <p className="text-xs font-bold text-yellow-400 uppercase mb-1">Special Instructions</p>
              <p className="text-sm text-yellow-100">{order.specialInstructions}</p>
            </div>
          )}
        </div>

        {/* Shipping Info */}
        {order.shippingMethod && (
          <div className="bg-gray-800 border border-gray-700 rounded-xl p-5 mb-4">
            <h3 className="text-sm font-bold text-gray-400 uppercase mb-3">📦 Shipping</h3>
            <p className="text-sm">{order.shippingMethod}</p>
          </div>
        )}

        {/* Documents */}
        <div className="bg-gray-800 border border-gray-700 rounded-xl p-5 mb-4">
          <h3 className="text-sm font-bold text-gray-400 uppercase mb-3">📄 Documents</h3>
          {order.documentsAttached ? (
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-semibold">Signing package attached</p>
                <p className="text-xs text-gray-500">{order.pageCount} pages</p>
              </div>
              <button className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg font-semibold text-sm transition">
                ⬇️ Download Package
              </button>
            </div>
          ) : (
            <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-lg p-4 text-center">
              <p className="text-yellow-400 font-semibold">Documents not yet attached</p>
              <p className="text-xs text-gray-500 mt-1">Documents will be available once the title company uploads them</p>
            </div>
          )}
        </div>

        {/* Corrections (if any) */}
        {order.corrections && order.corrections.length > 0 && (
          <div className="bg-red-500/5 border border-red-500/40 rounded-xl p-5 mb-4">
            <h3 className="text-sm font-bold text-red-400 uppercase mb-3">🚨 Corrections Required</h3>
            <div className="space-y-3">
              {order.corrections.map((err, i) => (
                <div key={i} className={`px-4 py-3 rounded-lg ${
                  err.severity === 'CRITICAL' ? 'bg-red-500/10 border border-red-500/30' : 'bg-yellow-500/10 border border-yellow-500/30'
                }`}>
                  <div className="flex items-center gap-2 mb-1">
                    <span className={`text-xs font-bold ${err.severity === 'CRITICAL' ? 'text-red-400' : 'text-yellow-400'}`}>{err.severity}</span>
                    <span className="text-xs text-gray-500">Page {err.page}</span>
                  </div>
                  <p className="text-sm">{err.description}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* ═══ SCANBACK & QC — ALWAYS VISIBLE ═══ */}
        <div className="rounded-xl p-5 mb-4" style={{
          background: order.status === 'Correction Requested' ? 'rgba(239, 68, 68, 0.05)'
            : order.status === 'Verified' ? 'rgba(34, 197, 94, 0.05)'
            : 'rgba(236, 72, 153, 0.05)',
          border: order.status === 'Correction Requested' ? '1px solid rgba(239, 68, 68, 0.3)'
            : order.status === 'Verified' ? '1px solid rgba(34, 197, 94, 0.3)'
            : '1px solid rgba(236, 72, 153, 0.2)',
        }}>
          {/* Section Header */}
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-bold uppercase" style={{
              color: order.status === 'Correction Requested' ? '#EF4444'
                : order.status === 'Verified' ? '#22C55E'
                : '#EC4899'
            }}>
              {order.status === 'Correction Requested' ? '🚨 Corrections Required'
                : order.status === 'Verified' ? '✅ QC Passed — Verified'
                : order.status === 'Scanned Back' ? '🔍 Scanback Under QC Review'
                : '📸 Scanback Upload'}
            </h3>
            {order.scanbackUploaded && !['Correction Requested'].includes(order.status) && (
              <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold" style={{
                background: order.status === 'Verified' ? 'rgba(34, 197, 94, 0.1)' : order.status === 'Scanned Back' ? 'rgba(59, 130, 246, 0.1)' : 'rgba(34, 197, 94, 0.1)',
                color: order.status === 'Verified' ? '#22C55E' : order.status === 'Scanned Back' ? '#3B82F6' : '#22C55E',
                border: order.status === 'Verified' ? '1px solid rgba(34, 197, 94, 0.3)' : order.status === 'Scanned Back' ? '1px solid rgba(59, 130, 246, 0.3)' : '1px solid rgba(34, 197, 94, 0.3)',
              }}>
                {order.status === 'Verified' ? '✅ Verified' : order.status === 'Scanned Back' ? '🔍 In QC' : '📤 Uploaded'}
              </span>
            )}
          </div>

          {/* QC Pipeline Visual */}
          {order.scanbackUploaded && (
            <div className="flex items-center gap-2 mb-4">
              {[
                { key: 'upload', label: 'Uploaded', done: true },
                { key: 'qc', label: 'QC Review', done: ['Scanned Back', 'Verified', 'Closed'].includes(order.status), active: order.status === 'Scanned Back' },
                { key: 'result', label: order.status === 'Correction Requested' ? 'Corrections' : 'Verified', done: ['Verified', 'Closed'].includes(order.status), error: order.status === 'Correction Requested' },
                { key: 'payment', label: 'Payment', done: order.status === 'Closed' },
              ].map((step, i) => (
                <div key={step.key} className="flex items-center gap-2 flex-1">
                  <div className={`w-6 h-6 rounded-full flex items-center justify-center text-[10px] font-bold flex-shrink-0 ${
                    step.error ? 'bg-red-500/30 text-red-400 border border-red-500/40'
                    : step.done ? 'bg-teal-500/30 text-teal-400 border border-teal-500/40'
                    : step.active ? 'bg-blue-500/30 text-blue-400 border border-blue-500/40 animate-pulse'
                    : 'bg-gray-700/50 text-gray-600 border border-gray-600/30'
                  }`}>
                    {step.error ? '!' : step.done ? '✓' : i + 1}
                  </div>
                  <p className={`text-[10px] font-semibold ${
                    step.error ? 'text-red-400'
                    : step.done ? 'text-teal-400'
                    : step.active ? 'text-blue-400'
                    : 'text-gray-600'
                  }`}>{step.label}</p>
                  {i < 3 && <div className={`flex-1 h-px ${step.done ? 'bg-teal-500/40' : 'bg-gray-700'}`} />}
                </div>
              ))}
            </div>
          )}

          {/* Status: Verified — QC passed */}
          {order.status === 'Verified' && (
            <div className="rounded-lg p-3" style={{ background: 'rgba(34, 197, 94, 0.08)' }}>
              <p className="text-sm font-semibold text-green-400">All checks passed. Payment is processing.</p>
              <p className="text-xs text-gray-500 mt-1">Files: {order.scanbackFiles?.join(', ')}</p>
            </div>
          )}

          {/* Status: Scanned Back — waiting on QC */}
          {order.status === 'Scanned Back' && (
            <div className="rounded-lg p-3" style={{ background: 'rgba(59, 130, 246, 0.08)', border: '1px solid rgba(59, 130, 246, 0.2)' }}>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-semibold text-blue-400">DDI is reviewing your scanback</p>
                  <p className="text-xs text-gray-500 mt-1">The 7-point inspection checks: signatures, initials, dates, seal, pages, ID, and markings.</p>
                  <p className="text-xs text-gray-600 mt-1">Files: {order.scanbackFiles?.join(', ')}</p>
                </div>
                <button
                  onClick={() => openScanbackUpload(order.id)}
                  className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-gray-700 hover:bg-gray-600 transition flex-shrink-0 ml-3">
                  + Upload Additional
                </button>
              </div>
            </div>
          )}

          {/* Status: Correction Requested — QC found errors */}
          {order.status === 'Correction Requested' && (
            <div>
              <div className="rounded-lg p-3 mb-3" style={{ background: 'rgba(239, 68, 68, 0.08)' }}>
                <p className="text-sm font-semibold text-red-400">QC found issues that need to be fixed before payment can process.</p>
                <p className="text-xs text-gray-500 mt-1">Review the corrections above, fix the pages, and re-upload.</p>
              </div>
              <button
                onClick={() => openScanbackUpload(order.id)}
                className="w-full px-5 py-2.5 rounded-lg font-bold text-sm text-white transition"
                style={{ background: 'linear-gradient(135deg, #EF4444, #DC2626)' }}>
                📸 Upload Corrected Pages
              </button>
            </div>
          )}

          {/* Status: Not yet uploaded */}
          {!order.scanbackUploaded && order.status !== 'Correction Requested' && (
            <div className="flex items-center justify-between">
              <p className="text-sm text-gray-400 flex-1 mr-4">
                {order.status === 'Assigned' || order.status === 'Confirmed'
                  ? 'Upload after signing is complete.'
                  : order.status === 'In Progress'
                    ? 'Upload when the signing is finished.'
                    : 'Upload scanned docs — required before payment.'}
              </p>
              <button
                onClick={() => openScanbackUpload(order.id)}
                className="px-5 py-2.5 rounded-lg font-bold text-sm text-white transition flex-shrink-0"
                style={{ background: 'linear-gradient(135deg, #EC4899, #DB2777)' }}>
                📸 Upload Scanback
              </button>
            </div>
          )}

          {/* Status: Uploaded but not yet in QC (Completed status) */}
          {order.scanbackUploaded && order.status === 'Completed' && (
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-400">{order.scanbackFiles?.join(', ')}</p>
              </div>
              <button
                onClick={() => openScanbackUpload(order.id)}
                className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-gray-700 hover:bg-gray-600 transition">
                + Upload Additional
              </button>
            </div>
          )}

          {/* Closed order — everything done */}
          {order.status === 'Closed' && (
            <div className="rounded-lg p-3" style={{ background: 'rgba(34, 197, 94, 0.05)' }}>
              <p className="text-sm text-gray-500">QC verified. Payment complete. Order closed.</p>
              <p className="text-xs text-gray-600 mt-1">Files: {order.scanbackFiles?.join(', ')}</p>
            </div>
          )}
        </div>

        {/* ═══ GATED ACTION BUTTONS ═══ */}
        <div className="flex flex-wrap gap-3">
          {/* Step 1: Accept */}
          {order.status === 'Assigned' && (
            <>
              <button className="bg-green-600 hover:bg-green-700 px-6 py-3 rounded-lg font-bold text-sm transition flex-1"
                onClick={() => setShowConfirmAccept(order.id)}>
                ✅ Accept Assignment
              </button>
              <button className="bg-red-600/50 hover:bg-red-600 px-6 py-3 rounded-lg font-bold text-sm transition">
                ✕ Decline
              </button>
            </>
          )}

          {/* Step 2: Start */}
          {order.status === 'Confirmed' && (
            <button
              className="bg-purple-600 hover:bg-purple-700 px-6 py-3 rounded-lg font-bold text-sm transition flex-1"
              onClick={() => handleStartOrder(order.id)}>
              ▶️ Start — I'm at the Appointment
            </button>
          )}

          {/* Step 3: Complete */}
          {order.status === 'In Progress' && (
            <button
              className="bg-green-600 hover:bg-green-700 px-6 py-3 rounded-lg font-bold text-sm transition flex-1"
              onClick={() => handleCompleteOrder(order.id)}>
              ✅ Mark Complete — Signing Finished
            </button>
          )}

          {/* Step 5: Shipped/Done (only after scanback uploaded) */}
          {order.status === 'Scanned Back' && (
            <div className="w-full text-center rounded-xl p-4" style={{ background: 'rgba(34, 197, 94, 0.08)', border: '1px solid rgba(34, 197, 94, 0.3)' }}>
              <p className="text-sm font-semibold text-green-400">📦 Scanback submitted — awaiting DDI verification</p>
              <p className="text-xs text-gray-500 mt-1">You'll be notified once verified. Payment processes after verification.</p>
            </div>
          )}
        </div>
      </div>
    );
  };

  // ─── ORDER ROW (compact) ───────────────────────────────────────
  const renderOrderRow = (order: typeof orders[0]) => {
    const svc = SERVICE_COLORS[order.type];
    const hasCorrections = order.status === 'Correction Requested';
    const step = getWorkflowStep(order.status);
    const isFinished = ['Verified', 'Closed'].includes(order.status);

    // Next action prompt for the list view
    const nextAction: Record<string, string> = {
      'Assigned': '→ Accept to begin',
      'Confirmed': '→ Tap Start at appointment',
      'In Progress': '→ Mark Complete when done',
      'Completed': '→ Upload Scanback',
      'Scanned Back': '→ Awaiting verification',
      'Correction Requested': '→ Fix & re-upload',
    };

    return (
      <div key={order.id}
        className={`bg-gray-800 border rounded-xl p-4 cursor-pointer transition hover:border-gray-500 ${hasCorrections ? 'border-red-500/50 bg-red-500/5' : 'border-gray-700'}`}
        style={{ borderLeftWidth: '4px', borderLeftColor: svc?.color }}
        onClick={() => setSelectedOrderId(order.id)}>
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <ServiceBadge type={order.type} />
            <StatusBadge status={order.status} />
            {hasCorrections && <span className="text-red-400 text-xs font-bold animate-pulse">ACTION NEEDED</span>}
          </div>
          <span className="text-green-400 font-bold">${order.fee + order.travelFee + order.surcharge}</span>
        </div>
        <p className="font-semibold">{order.signer}</p>
        <p className="text-sm text-gray-400">{order.address}</p>
        <div className="flex items-center justify-between mt-1">
          <p className="text-sm text-gray-500">{order.date} at {order.time}</p>
          {!isFinished && (
            <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full" style={{
              background: hasCorrections ? 'rgba(239, 68, 68, 0.1)' : 'rgba(236, 72, 153, 0.08)',
              color: hasCorrections ? '#EF4444' : '#EC4899',
              border: hasCorrections ? '1px solid rgba(239, 68, 68, 0.3)' : '1px solid rgba(236, 72, 153, 0.2)',
            }}>
              Step {Math.min(step + 1, 5)}/5 {nextAction[order.status] || ''}
            </span>
          )}
        </div>
      </div>
    );
  };

  return (
    <div className="min-h-screen">
      {/* ─── AGENT HEADER BAR ─────────────────────────────── */}
      <div className="sticky top-[73px] z-40" style={{ background: '#1B2A4A', borderBottom: '1px solid rgba(45, 212, 191, 0.15)' }}>
        <div className="max-w-5xl mx-auto px-6">
          <div className="flex items-center justify-between py-2">
            {/* Tabs */}
            <div className="flex gap-1">
              {tabs.map(tab => (
                <button key={tab.id} onClick={() => { setActiveTab(tab.id); setSelectedOrderId(null); }}
                  className={`px-4 py-3 text-sm font-semibold rounded-t-lg transition whitespace-nowrap ${
                    activeTab === tab.id
                      ? 'text-white'
                      : 'text-gray-400 hover:text-white'
                  }`}
                  style={activeTab === tab.id ? { background: 'linear-gradient(135deg, #EC4899, #DB2777)', boxShadow: '0 2px 10px rgba(236, 72, 153, 0.3)' } : { background: 'transparent' }}>
                  {tab.label}
                </button>
              ))}
            </div>

            {/* Agent info + notifications */}
            <div className="flex items-center gap-4">
              <button onClick={() => setShowNotifPanel(!showNotifPanel)}
                className="relative text-gray-400 hover:text-white transition">
                🔔
                {unreadNotifs > 0 && (
                  <span className="absolute -top-1 -right-1 w-4 h-4 text-white text-[10px] font-bold rounded-full flex items-center justify-center" style={{ background: '#EC4899' }}>{unreadNotifs}</span>
                )}
              </button>
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-full flex items-center justify-center text-white font-bold text-xs" style={{ background: 'linear-gradient(135deg, #EC4899, #DB2777)' }}>SC</div>
                <div className="text-right hidden md:block">
                  <p className="text-sm font-semibold">{agentProfile.name}</p>
                  <p className="text-[10px] text-gray-500">{agentProfile.id} • {agentProfile.city}, {agentProfile.state}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* ─── NOTIFICATION PANEL ───────────────────────────── */}
      {showNotifPanel && (
        <div className="fixed top-[140px] right-4 w-96 rounded-xl shadow-2xl z-50 max-h-[60vh] overflow-y-auto" style={{ background: '#0F1A2E', border: '1px solid rgba(45, 212, 191, 0.2)' }}>
          <div className="p-4 flex items-center justify-between" style={{ borderBottom: '1px solid rgba(45, 212, 191, 0.1)' }}>
            <h3 className="font-bold">Notifications</h3>
            <button onClick={() => setShowNotifPanel(false)} className="text-gray-500 hover:text-white">✕</button>
          </div>
          <div className="divide-y divide-gray-800">
            {notifications.map(n => (
              <div key={n.id} className={`px-4 py-3 hover:bg-gray-800 transition cursor-pointer ${!n.read ? 'bg-gray-800/50' : ''}`}>
                <div className="flex items-start gap-2">
                  {!n.read && <div className="w-2 h-2 rounded-full mt-1.5 flex-shrink-0" style={{ background: '#2DD4BF' }}></div>}
                  <div>
                    <p className="text-sm">{n.message}</p>
                    <p className="text-xs text-gray-500 mt-1">{n.time}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ─── CONTENT ──────────────────────────────────────── */}
      <div className="max-w-5xl mx-auto px-6 py-6">

        {/* ════════════════════════════════════════════════
            DASHBOARD
        ════════════════════════════════════════════════ */}
        {activeTab === 'dashboard' && !selectedOrderId && (
          <div>
            {/* Welcome */}
            <div className="mb-6">
              <h2 className="text-2xl font-bold">Welcome back, {agentProfile.name.split(' ')[0]} 👋</h2>
              <p className="text-gray-400 text-sm">Here's what's happening today</p>
            </div>

            {/* Quick Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
              <div className="bg-gray-800 border border-gray-700 rounded-xl p-4">
                <p className="text-xs text-gray-500 uppercase font-semibold">Active Orders</p>
                <p className="text-2xl font-bold" style={{ color: '#EC4899' }}>{activeOrders.length}</p>
              </div>
              <div className="bg-gray-800 border border-gray-700 rounded-xl p-4">
                <p className="text-xs text-gray-500 uppercase font-semibold">Today</p>
                <p className="text-2xl font-bold text-blue-400">{todayOrders.length}</p>
              </div>
              <div className="bg-gray-800 border border-gray-700 rounded-xl p-4">
                <p className="text-xs text-gray-500 uppercase font-semibold">This Month</p>
                <p className="text-2xl font-bold text-green-400">${myPayments.reduce((sum, p) => sum + p.total, 0).toLocaleString()}</p>
              </div>
              <div className="bg-gray-800 border border-gray-700 rounded-xl p-4">
                <p className="text-xs text-gray-500 uppercase font-semibold">Rating</p>
                <p className="text-2xl font-bold text-yellow-400">⭐ {agentProfile.rating}</p>
              </div>
            </div>

            {/* Compliance Alert on Dashboard */}
            {(expiredDocs.length > 0 || missingDocs.length > 0) && (
              <div className="rounded-xl p-4 mb-6 cursor-pointer hover:opacity-90 transition" onClick={() => setActiveTab('profile')}
                style={{ background: 'rgba(239, 68, 68, 0.08)', border: '1px solid rgba(239, 68, 68, 0.3)' }}>
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-bold text-sm text-red-400">⚠️ Document Action Required</p>
                    <p className="text-xs text-gray-400 mt-1">
                      {expiredDocs.length > 0 && `${expiredDocs.length} expired. `}
                      {missingDocs.length > 0 && `${missingDocs.length} missing. `}
                      Compliance: {compliancePercent}%
                    </p>
                  </div>
                  <span className="text-xs font-semibold" style={{ color: '#2DD4BF' }}>View in Profile →</span>
                </div>
              </div>
            )}

            {/* Action Required */}
            {actionRequired.length > 0 && (
              <div className="mb-6">
                <h3 className="text-lg font-bold mb-3 text-red-400">🔴 Action Required</h3>
                <div className="space-y-3">
                  {actionRequired.map(order => renderOrderRow(order))}
                </div>
              </div>
            )}

            {/* Today's Schedule */}
            <div className="mb-6">
              <h3 className="text-lg font-bold mb-3">📅 Today — {todayOrders.length} Appointment{todayOrders.length !== 1 ? 's' : ''}</h3>
              {todayOrders.length > 0 ? (
                <div className="space-y-3">
                  {todayOrders.sort((a, b) => a.time.localeCompare(b.time)).map(order => {
                    const svc = SERVICE_COLORS[order.type];
                    return (
                      <div key={order.id} className="bg-gray-800 border border-gray-700 rounded-xl p-4 cursor-pointer hover:border-gray-500 transition"
                        style={{ borderLeftWidth: '5px', borderLeftColor: svc?.color }}
                        onClick={() => { setSelectedOrderId(order.id); setActiveTab('orders'); }}>
                        <div className="flex items-center justify-between">
                          <div>
                            <div className="flex items-center gap-2 mb-1">
                              <span className="text-lg font-bold">{order.time}</span>
                              <ServiceBadge type={order.type} />
                              <StatusBadge status={order.status} />
                            </div>
                            <p className="font-semibold">{order.signer}</p>
                            <p className="text-sm text-gray-400">{order.address}</p>
                          </div>
                          <div className="text-right">
                            <p className="text-green-400 font-bold text-lg">${order.fee + order.travelFee + order.surcharge}</p>
                            <p className="text-xs text-gray-500">View Details →</p>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              ) : (
                <div className="bg-gray-800 border border-gray-700 rounded-xl p-8 text-center">
                  <p className="text-gray-500">No appointments today</p>
                </div>
              )}
            </div>

            {/* Upcoming */}
            {upcomingOrders.length > 0 && (
              <div className="mb-6">
                <h3 className="text-lg font-bold mb-3">📋 Upcoming</h3>
                <div className="space-y-3">
                  {upcomingOrders.map(order => renderOrderRow(order))}
                </div>
              </div>
            )}

            {/* Performance */}
            <div>
              <h3 className="text-lg font-bold mb-3">📊 My Performance</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-gray-800 border border-gray-700 rounded-xl p-4 text-center">
                  <p className="text-2xl font-bold text-green-400">{agentProfile.completionRate}%</p>
                  <p className="text-xs text-gray-500 uppercase">Completion</p>
                </div>
                <div className="bg-gray-800 border border-gray-700 rounded-xl p-4 text-center">
                  <p className="text-2xl font-bold text-blue-400">{agentProfile.onTimeRate}%</p>
                  <p className="text-xs text-gray-500 uppercase">On-Time</p>
                </div>
                <div className="bg-gray-800 border border-gray-700 rounded-xl p-4 text-center">
                  <p className={`text-2xl font-bold ${agentProfile.errorRate <= 2 ? 'text-green-400' : 'text-yellow-400'}`}>{agentProfile.errorRate}%</p>
                  <p className="text-xs text-gray-500 uppercase">Error Rate</p>
                </div>
                <div className="bg-gray-800 border border-gray-700 rounded-xl p-4 text-center">
                  <p className="text-2xl font-bold text-purple-400">{agentProfile.ordersCompleted}</p>
                  <p className="text-xs text-gray-500 uppercase">Total Orders</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* ════════════════════════════════════════════════
            MY ORDERS
        ════════════════════════════════════════════════ */}
        {activeTab === 'orders' && !selectedOrderId && (
          <div>
            <div className="mb-6 flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-bold">📋 My Orders</h2>
                <p className="text-gray-400 text-sm">{activeOrders.length} active, {historyOrders.length} completed</p>
              </div>
              <div className="flex gap-1 bg-gray-800 rounded-lg p-1">
                <button onClick={() => setOrderViewFilter('active')}
                  className={`px-4 py-1.5 rounded text-sm font-semibold transition ${orderViewFilter === 'active' ? 'bg-gray-600 text-white' : 'text-gray-400 hover:text-white'}`}>
                  Active ({activeOrders.length})
                </button>
                <button onClick={() => setOrderViewFilter('history')}
                  className={`px-4 py-1.5 rounded text-sm font-semibold transition ${orderViewFilter === 'history' ? 'bg-gray-600 text-white' : 'text-gray-400 hover:text-white'}`}>
                  History ({historyOrders.length})
                </button>
              </div>
            </div>

            <div className="space-y-3">
              {(orderViewFilter === 'active' ? activeOrders : historyOrders).map(order => renderOrderRow(order))}
              {(orderViewFilter === 'active' ? activeOrders : historyOrders).length === 0 && (
                <div className="bg-gray-800 border border-gray-700 rounded-xl p-8 text-center text-gray-500">
                  {orderViewFilter === 'active' ? 'No active orders' : 'No completed orders yet'}
                </div>
              )}
            </div>
          </div>
        )}

        {/* ── Order Detail ── */}
        {activeTab === 'orders' && selectedOrderId && (() => {
          const order = orders.find(o => o.id === selectedOrderId);
          if (!order) return null;
          return renderOrderDetail(order);
        })()}

        {/* Dashboard → Order detail redirect */}
        {activeTab === 'dashboard' && selectedOrderId && (() => {
          setActiveTab('orders');
          return null;
        })()}

        {/* ════════════════════════════════════════════════
            PAYMENTS
        ════════════════════════════════════════════════ */}
        {activeTab === 'payments' && (
          <div>
            <div className="mb-6">
              <h2 className="text-2xl font-bold">💰 Payments</h2>
              <p className="text-gray-400 text-sm">Earnings and payment history</p>
            </div>

            {/* Summary Cards */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
              <div className="bg-gray-800 border border-gray-700 rounded-xl p-4">
                <p className="text-xs text-gray-500 uppercase font-semibold">Pending</p>
                <p className="text-2xl font-bold text-yellow-400">${myPayments.filter(p => p.status === 'Pending').reduce((s, p) => s + p.total, 0)}</p>
              </div>
              <div className="bg-gray-800 border border-gray-700 rounded-xl p-4">
                <p className="text-xs text-gray-500 uppercase font-semibold">Processing</p>
                <p className="text-2xl font-bold text-blue-400">${myPayments.filter(p => p.status === 'Processing').reduce((s, p) => s + p.total, 0)}</p>
              </div>
              <div className="bg-gray-800 border border-gray-700 rounded-xl p-4">
                <p className="text-xs text-gray-500 uppercase font-semibold">Paid This Month</p>
                <p className="text-2xl font-bold text-green-400">${myPayments.filter(p => p.status === 'Paid').reduce((s, p) => s + p.total, 0)}</p>
              </div>
              <div className="bg-gray-800 border border-gray-700 rounded-xl p-4">
                <p className="text-xs text-gray-500 uppercase font-semibold">Total Earned</p>
                <p className="text-2xl font-bold text-purple-400">${agentProfile.totalEarned.toLocaleString()}</p>
              </div>
            </div>

            {/* Payment Table */}
            <div className="bg-gray-800 border border-gray-700 rounded-xl overflow-hidden">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-gray-700 text-gray-400 text-xs uppercase">
                    <th className="text-left px-4 py-3">Order</th>
                    <th className="text-left px-4 py-3">Signer</th>
                    <th className="text-left px-4 py-3">Date</th>
                    <th className="text-right px-4 py-3">Base</th>
                    <th className="text-right px-4 py-3">Travel</th>
                    <th className="text-right px-4 py-3">Extra</th>
                    <th className="text-right px-4 py-3">Total</th>
                    <th className="text-right px-4 py-3">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {myPayments.map((p, i) => (
                    <tr key={i} className="border-b border-gray-700/50 hover:bg-gray-700/30 transition">
                      <td className="px-4 py-3 font-mono text-xs text-gray-500">{p.orderId}</td>
                      <td className="px-4 py-3">{p.signer}</td>
                      <td className="px-4 py-3 text-gray-400">{p.date}</td>
                      <td className="px-4 py-3 text-right">${p.base}</td>
                      <td className="px-4 py-3 text-right text-gray-400">{p.travel > 0 ? `$${p.travel}` : '—'}</td>
                      <td className="px-4 py-3 text-right text-gray-400">{p.surcharge > 0 ? `$${p.surcharge}` : '—'}</td>
                      <td className="px-4 py-3 text-right font-bold text-green-400">${p.total}</td>
                      <td className="px-4 py-3 text-right">
                        <span className={`px-2 py-0.5 rounded-full text-xs font-semibold ${
                          p.status === 'Paid' ? 'bg-green-500/20 text-green-400' :
                          p.status === 'Processing' ? 'bg-blue-500/20 text-blue-400' :
                          p.status === 'On Hold' ? 'bg-red-500/20 text-red-400' :
                          'bg-yellow-500/20 text-yellow-400'
                        }`}>{p.status}</span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* On Hold Note */}
            {myPayments.some(p => p.status === 'On Hold') && (
              <div className="mt-4 bg-red-500/10 border border-red-500/30 rounded-lg p-4">
                <p className="text-sm text-red-400 font-semibold">⚠️ Payment on hold</p>
                <p className="text-xs text-gray-400 mt-1">PRISM-2026-0020 has unresolved corrections. Payment releases after scanback is verified clean.</p>
              </div>
            )}
          </div>
        )}

        {/* ════════════════════════════════════════════════
            PROFILE
        ════════════════════════════════════════════════ */}
        {activeTab === 'profile' && (
          <div>
            <div className="mb-6 flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-bold">👤 My Profile</h2>
                <p className="text-gray-400 text-sm">{agentProfile.id} • Member since {agentProfile.dateJoined}</p>
              </div>
              <button onClick={() => setProfileEditing(!profileEditing)}
                className={`px-4 py-2 rounded-lg font-semibold text-sm transition ${profileEditing ? 'bg-green-600 hover:bg-green-700' : 'bg-gray-700 hover:bg-gray-600'}`}>
                {profileEditing ? '💾 Save Changes' : '✏️ Edit Profile'}
              </button>
            </div>

            {/* Personal Info */}
            <div className="bg-gray-800 border border-gray-700 rounded-xl p-5 mb-4">
              <h3 className="text-sm font-bold text-gray-400 uppercase mb-4">Personal Information</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs text-gray-500 mb-1">Full Name</label>
                  <input type="text" defaultValue={agentProfile.name} disabled={!profileEditing}
                    className="w-full bg-gray-700/50 border border-gray-600 rounded-lg px-3 py-2 text-sm disabled:opacity-60" />
                </div>
                <div>
                  <label className="block text-xs text-gray-500 mb-1">Email</label>
                  <input type="email" defaultValue={agentProfile.email} disabled={!profileEditing}
                    className="w-full bg-gray-700/50 border border-gray-600 rounded-lg px-3 py-2 text-sm disabled:opacity-60" />
                </div>
                <div>
                  <label className="block text-xs text-gray-500 mb-1">Phone</label>
                  <input type="tel" defaultValue={agentProfile.phone} disabled={!profileEditing}
                    className="w-full bg-gray-700/50 border border-gray-600 rounded-lg px-3 py-2 text-sm disabled:opacity-60" />
                </div>
                <div>
                  <label className="block text-xs text-gray-500 mb-1">Address</label>
                  <input type="text" defaultValue={agentProfile.address} disabled={!profileEditing}
                    className="w-full bg-gray-700/50 border border-gray-600 rounded-lg px-3 py-2 text-sm disabled:opacity-60" />
                </div>
              </div>
            </div>

            {/* Service Area */}
            <div className="bg-gray-800 border border-gray-700 rounded-xl p-5 mb-4">
              <h3 className="text-sm font-bold text-gray-400 uppercase mb-4">Service Area</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs text-gray-500 mb-1">Service Radius</label>
                  <div className="flex items-center gap-2">
                    <input type="number" defaultValue={agentProfile.serviceRadius} disabled={!profileEditing}
                      className="w-24 bg-gray-700/50 border border-gray-600 rounded-lg px-3 py-2 text-sm disabled:opacity-60" />
                    <span className="text-sm text-gray-500">miles</span>
                  </div>
                </div>
                <div>
                  <label className="block text-xs text-gray-500 mb-1">Specialties</label>
                  <div className="flex flex-wrap gap-1">
                    {agentProfile.specialties.map(s => (
                      <span key={s} className="px-2 py-1 rounded-full text-xs font-semibold" style={{ background: 'rgba(45, 212, 191, 0.15)', color: '#2DD4BF', border: '1px solid rgba(45, 212, 191, 0.3)' }}>{s}</span>
                    ))}
                  </div>
                </div>
                <div className="md:col-span-2">
                  <label className="block text-xs text-gray-500 mb-1">Service ZIP Codes</label>
                  <input type="text" defaultValue={agentProfile.serviceZips} disabled={!profileEditing}
                    className="w-full bg-gray-700/50 border border-gray-600 rounded-lg px-3 py-2 text-sm disabled:opacity-60" />
                </div>
              </div>
            </div>

            {/* ═══ COMPLIANCE STATUS ═══ */}
            <div className="rounded-xl p-5 mb-4" style={{ background: '#1B2A4A', border: '1px solid rgba(45, 212, 191, 0.15)' }}>
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm font-bold uppercase" style={{ color: '#2DD4BF' }}>Compliance Status</h3>
                <div className="flex items-center gap-2">
                  <div className="w-24 h-2 rounded-full bg-gray-700 overflow-hidden">
                    <div className="h-full rounded-full transition-all" style={{ width: `${compliancePercent}%`, background: compliancePercent === 100 ? '#2DD4BF' : compliancePercent >= 70 ? '#F59E0B' : '#EF4444' }} />
                  </div>
                  <span className="text-sm font-bold" style={{ color: compliancePercent === 100 ? '#2DD4BF' : compliancePercent >= 70 ? '#F59E0B' : '#EF4444' }}>{compliancePercent}%</span>
                </div>
              </div>
              <div className="grid grid-cols-3 gap-3 mb-4">
                <div className="text-center rounded-lg p-2 bg-gray-800/50">
                  <p className="text-lg font-bold text-green-400">{approvedDocs.length}</p>
                  <p className="text-[10px] text-gray-500 uppercase">Approved</p>
                </div>
                <div className="text-center rounded-lg p-2 bg-gray-800/50">
                  <p className="text-lg font-bold" style={{ color: '#EC4899' }}>{missingDocs.length + expiredDocs.length}</p>
                  <p className="text-[10px] text-gray-500 uppercase">Needs Action</p>
                </div>
                <div className="text-center rounded-lg p-2 bg-gray-800/50">
                  <p className="text-lg font-bold text-blue-400">{submittedDocs.length}</p>
                  <p className="text-[10px] text-gray-500 uppercase">Under Review</p>
                </div>
              </div>

              {/* Alert */}
              {(missingDocs.length > 0 || expiredDocs.length > 0) && (
                <div className="rounded-lg p-3 mb-4" style={{ background: 'rgba(239, 68, 68, 0.08)', border: '1px solid rgba(239, 68, 68, 0.3)' }}>
                  <p className="text-xs text-red-400 font-semibold">
                    {expiredDocs.length > 0 && `${expiredDocs.length} expired. `}
                    {missingDocs.length > 0 && `${missingDocs.length} missing. `}
                    Upload to stay active and keep receiving orders.
                  </p>
                </div>
              )}

              {/* Document List */}
              <div className="space-y-2">
                {docs.map(doc => {
                  const statusConfig: Record<string, { bg: string; text: string; border: string; icon: string }> = {
                    'Approved': { bg: 'rgba(34, 197, 94, 0.1)', text: '#22C55E', border: 'rgba(34, 197, 94, 0.3)', icon: '✅' },
                    'Missing': { bg: 'rgba(239, 68, 68, 0.08)', text: '#EF4444', border: 'rgba(239, 68, 68, 0.3)', icon: '❌' },
                    'Expired': { bg: 'rgba(239, 68, 68, 0.08)', text: '#F97316', border: 'rgba(239, 68, 68, 0.3)', icon: '⏰' },
                    'Submitted': { bg: 'rgba(59, 130, 246, 0.08)', text: '#3B82F6', border: 'rgba(59, 130, 246, 0.3)', icon: '📤' },
                    'Under Review': { bg: 'rgba(245, 158, 11, 0.08)', text: '#F59E0B', border: 'rgba(245, 158, 11, 0.3)', icon: '🔄' },
                    'Rejected': { bg: 'rgba(239, 68, 68, 0.08)', text: '#EF4444', border: 'rgba(239, 68, 68, 0.3)', icon: '🚫' },
                  };
                  const cfg = statusConfig[doc.status] || statusConfig['Missing'];

                  return (
                    <div key={doc.id} className="rounded-lg p-3 flex items-center justify-between" style={{ background: 'rgba(15, 26, 46, 0.6)', borderLeft: `3px solid ${cfg.text}` }}>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <p className="font-semibold text-sm truncate">{doc.type}</p>
                          {doc.required && <span className="text-[9px] px-1 py-0.5 rounded bg-gray-700 text-gray-400 font-semibold flex-shrink-0">REQ</span>}
                        </div>
                        <div className="flex items-center gap-2 mt-1">
                          <span className="px-1.5 py-0.5 rounded-full text-[10px] font-semibold" style={{ background: cfg.bg, color: cfg.text, border: `1px solid ${cfg.border}` }}>
                            {cfg.icon} {doc.status}
                          </span>
                          {doc.expirationDate && doc.status === 'Approved' && (
                            <span className="text-[10px] text-gray-500">Exp {doc.expirationDate}</span>
                          )}
                          {doc.fileName && (
                            <span className="text-[10px] text-gray-600">📎 {doc.fileName}</span>
                          )}
                        </div>
                        {doc.status === 'Rejected' && doc.rejectionReason && (
                          <p className="text-[10px] text-red-400 mt-1">Reason: {doc.rejectionReason}</p>
                        )}
                      </div>
                      <div className="flex items-center gap-1 ml-2 flex-shrink-0">
                        {doc.status === 'Approved' && doc.fileName && (
                          <button className="px-2 py-1 rounded text-[10px] font-semibold bg-gray-700 hover:bg-gray-600 transition">View</button>
                        )}
                        {(doc.status === 'Missing' || doc.status === 'Expired' || doc.status === 'Rejected') && doc.required && (
                          <button
                            onClick={() => openCredentialUpload(doc.id)}
                            className="px-2 py-1 rounded text-[10px] font-bold text-white transition"
                            style={{ background: 'linear-gradient(135deg, #EC4899, #DB2777)' }}>
                            Upload
                          </button>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>

              {/* Upload New Document */}
              <div className="mt-4 text-center">
                <button
                  onClick={() => { setUploadType('credential'); setUploadDocId(''); setSelectedFiles([]); setUploadStatus('idle'); setShowUploadModal(true); }}
                  className="px-5 py-2 rounded-lg font-bold text-xs text-white transition"
                  style={{ background: 'linear-gradient(135deg, #EC4899, #DB2777)' }}>
                  + Upload New Document
                </button>
              </div>
            </div>

            {/* ═══ DDI AGREEMENTS — DOWNLOAD & SIGN ═══ */}
            <div className="rounded-xl p-5 mb-4" style={{ background: '#1B2A4A', border: '1px solid rgba(45, 212, 191, 0.15)' }}>
              <h3 className="text-sm font-bold uppercase mb-3" style={{ color: '#2DD4BF' }}>DDI Agreements — Download & Sign</h3>
              <p className="text-xs text-gray-500 mb-3">Download, sign, and upload back to complete your onboarding.</p>
              <div className="space-y-2">
                {[
                  { id: 'nda', name: 'NDA / Confidentiality Agreement', icon: '🔒', status: docs.find(d => d.type === 'NDA / Confidentiality Agreement')?.status },
                  { id: 'ic-agreement', name: 'Independent Contractor Agreement', icon: '📋', status: docs.find(d => d.type === 'Independent Contractor Agreement')?.status },
                  { id: 'w9-request', name: 'W-9 Request & Instructions', icon: '📄', status: docs.find(d => d.type === 'W-9')?.status },
                ].map(template => (
                  <div key={template.id} className="rounded-lg p-3 flex items-center justify-between" style={{ background: 'rgba(15, 26, 46, 0.6)' }}>
                    <div className="flex items-center gap-2">
                      <span>{template.icon}</span>
                      <div>
                        <p className="font-semibold text-sm">{template.name}</p>
                        {template.status === 'Approved' && (
                          <span className="text-[10px] text-green-400 font-semibold">✅ On file</span>
                        )}
                      </div>
                    </div>
                    <button
                      onClick={async () => {
                        try {
                          const res = await fetch(`http://localhost:5000/prism/documents/generate/${template.id}`, {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ person_name: agentProfile.name, specialties: agentProfile.specialties }),
                          });
                          if (res.ok) {
                            const blob = await res.blob();
                            const url = URL.createObjectURL(blob);
                            const a = document.createElement('a');
                            a.href = url;
                            a.download = `DDI_${template.id}_${agentProfile.name.replace(' ', '_')}.pdf`;
                            a.click();
                            URL.revokeObjectURL(url);
                          } else {
                            alert('API server not running — start with: python3 api_server.py');
                          }
                        } catch {
                          alert('API server not running — start with: python3 api_server.py');
                        }
                      }}
                      className="px-3 py-1.5 rounded-lg text-[10px] font-bold text-white transition flex-shrink-0"
                      style={{ background: '#1B2A4A', border: '1px solid rgba(45, 212, 191, 0.3)' }}>
                      ⬇️ Download PDF
                    </button>
                  </div>
                ))}
              </div>
            </div>

            {/* Equipment */}
            <div className="bg-gray-800 border border-gray-700 rounded-xl p-5 mb-4">
              <h3 className="text-sm font-bold text-gray-400 uppercase mb-4">Equipment</h3>
              <div className="flex flex-wrap gap-2">
                {agentProfile.equipment.map(e => (
                  <span key={e} className="px-3 py-1.5 bg-gray-700 text-gray-300 rounded-lg text-sm">{e}</span>
                ))}
              </div>
            </div>

            {/* Payment Method */}
            <div className="bg-gray-800 border border-gray-700 rounded-xl p-5">
              <h3 className="text-sm font-bold text-gray-400 uppercase mb-4">Payment Method</h3>
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-semibold">{agentProfile.paymentMethod}</p>
                  <p className="text-xs text-gray-500">Ending in ****4821</p>
                </div>
                {profileEditing && (
                  <button className="bg-gray-700 hover:bg-gray-600 px-4 py-2 rounded-lg font-semibold text-sm transition">
                    Update
                  </button>
                )}
              </div>
            </div>
          </div>
        )}

      </div>

      {/* ─── UPLOAD MODAL (Scanbacks + Credentials) ──────────── */}
      {showUploadModal && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center" onClick={() => { if (uploadStatus !== 'uploading') { setShowUploadModal(false); setSelectedFiles([]); setUploadStatus('idle'); } }}>
          <div className="rounded-2xl w-full max-w-lg mx-4 shadow-2xl" style={{ background: '#0F1A2E', border: '1px solid rgba(45, 212, 191, 0.2)' }} onClick={e => e.stopPropagation()}>
            <div className="p-6" style={{ borderBottom: '1px solid rgba(45, 212, 191, 0.1)' }}>
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-xl font-bold">
                    {uploadType === 'scanback' ? '📸 Upload Scanback' : '📄 Upload Document'}
                  </h3>
                  <p className="text-sm text-gray-500">
                    {uploadType === 'scanback' ? uploadOrderId : uploadDocId ? docs.find(d => d.id === uploadDocId)?.type : 'New document'}
                  </p>
                </div>
                {uploadStatus !== 'uploading' && (
                  <button onClick={() => { setShowUploadModal(false); setSelectedFiles([]); setUploadStatus('idle'); }} className="text-gray-500 hover:text-white transition text-lg">✕</button>
                )}
              </div>
            </div>

            <div className="p-6 space-y-4">
              {/* Success State */}
              {uploadStatus === 'success' ? (
                <div className="text-center py-8">
                  <div className="text-5xl mb-4">✅</div>
                  <h4 className="text-xl font-bold mb-2">Upload Complete!</h4>
                  <p className="text-sm text-gray-400">
                    {uploadType === 'scanback'
                      ? 'Your scanback has been submitted for inspection. You\'ll be notified of the results.'
                      : 'Your document has been submitted for review. DDI will verify it within 1-2 business days.'}
                  </p>
                </div>
              ) : uploadStatus === 'uploading' ? (
                <div className="text-center py-8">
                  <div className="w-12 h-12 border-4 border-gray-700 rounded-full mx-auto mb-4 animate-spin" style={{ borderTopColor: '#EC4899' }}></div>
                  <h4 className="text-lg font-bold mb-1">Uploading...</h4>
                  <p className="text-sm text-gray-500">Sending to DDI compliance system...</p>
                </div>
              ) : uploadStatus === 'error' ? (
                <div className="text-center py-8">
                  <div className="w-16 h-16 rounded-full mx-auto mb-4 flex items-center justify-center text-3xl" style={{ background: 'rgba(239, 68, 68, 0.1)' }}>❌</div>
                  <h4 className="text-lg font-bold mb-1 text-red-400">Upload Failed</h4>
                  <p className="text-sm text-gray-500">File saved locally. Will sync when API is available.</p>
                  <button onClick={() => setUploadStatus('idle')} className="mt-4 px-4 py-2 rounded-lg text-sm font-bold text-white" style={{ background: '#EC4899' }}>Try Again</button>
                </div>
              ) : (
                <>
                  {/* Upload Zone */}
                  <label className="block border-2 border-dashed rounded-xl p-8 text-center transition cursor-pointer hover:opacity-80" style={{ borderColor: 'rgba(45, 212, 191, 0.3)', background: 'rgba(45, 212, 191, 0.03)' }}>
                    <input
                      type="file"
                      multiple
                      accept=".pdf,.jpg,.jpeg,.png"
                      className="hidden"
                      onChange={handleFileSelect}
                    />
                    <div className="text-4xl mb-3">{uploadType === 'scanback' ? '📷' : '📄'}</div>
                    <p className="font-semibold mb-1">Tap to select files</p>
                    <p className="text-sm text-gray-500">PDF, JPEG, or PNG — max 50MB per file</p>
                  </label>

                  {/* Selected Files */}
                  {selectedFiles.length > 0 && (
                    <div className="space-y-2">
                      <h4 className="text-xs font-bold text-gray-400 uppercase">Selected Files ({selectedFiles.length})</h4>
                      {selectedFiles.map((file, i) => (
                        <div key={i} className="flex items-center justify-between rounded-lg p-3" style={{ background: 'rgba(27, 42, 74, 0.7)', border: '1px solid rgba(45, 212, 191, 0.1)' }}>
                          <div className="flex items-center gap-3 flex-1 min-w-0">
                            <span className="text-lg flex-shrink-0">{file.type.includes('pdf') ? '📄' : '🖼️'}</span>
                            <div className="min-w-0">
                              <p className="text-sm font-semibold truncate">{file.name}</p>
                              <p className="text-xs text-gray-500">{(file.size / 1024).toFixed(0)} KB</p>
                            </div>
                          </div>
                          <button onClick={() => removeFile(i)} className="text-gray-500 hover:text-red-400 transition ml-2 flex-shrink-0">✕</button>
                        </div>
                      ))}
                    </div>
                  )}

                  {/* Tips */}
                  <div className="rounded-lg p-4" style={{ background: 'rgba(27, 42, 74, 0.5)', border: '1px solid rgba(45, 212, 191, 0.1)' }}>
                    <h4 className="text-xs font-bold text-gray-400 uppercase mb-2">
                      {uploadType === 'scanback' ? 'Scan Tips' : 'Document Tips'}
                    </h4>
                    <div className="space-y-1 text-xs text-gray-400">
                      {uploadType === 'scanback' ? (
                        <>
                          <p>• Scan all pages in order — do not skip or rearrange</p>
                          <p>• Make sure all 4 corners of each page are visible</p>
                          <p>• Check that signatures and stamps are clearly legible</p>
                          <p>• Use good lighting — no shadows across text</p>
                          <p>• Include ID copies if required by client rules</p>
                        </>
                      ) : (
                        <>
                          <p>• Make sure the entire document is visible and legible</p>
                          <p>• Include all pages (front and back if applicable)</p>
                          <p>• Ensure names and dates match your profile</p>
                          <p>• For insurance: coverage amounts and policy number must be visible</p>
                          <p>• For notary commission: commission number and expiration must be visible</p>
                        </>
                      )}
                    </div>
                  </div>
                </>
              )}
            </div>

            {uploadStatus === 'idle' && (
              <div className="p-6 flex gap-3" style={{ borderTop: '1px solid rgba(45, 212, 191, 0.1)' }}>
                <button
                  onClick={handleUploadSubmit}
                  disabled={selectedFiles.length === 0}
                  className="flex-1 px-4 py-2.5 rounded-lg font-bold text-white transition disabled:opacity-40 disabled:cursor-not-allowed"
                  style={{ background: selectedFiles.length > 0 ? 'linear-gradient(135deg, #EC4899, #DB2777)' : '#374151' }}>
                  {uploadType === 'scanback' ? 'Upload & Submit for Inspection' : 'Upload & Submit for Review'}
                </button>
                <button onClick={() => { setShowUploadModal(false); setSelectedFiles([]); setUploadStatus('idle'); }}
                  className="bg-gray-700 hover:bg-gray-600 px-4 py-2.5 rounded-lg font-semibold transition">
                  Cancel
                </button>
              </div>
            )}
          </div>
        </div>
      )}

      {/* ─── ACCEPT CONFIRMATION ──────────────────────────── */}
      {showConfirmAccept && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center" onClick={() => setShowConfirmAccept(null)}>
          <div className="bg-gray-900 border border-gray-700 rounded-2xl w-full max-w-md mx-4 shadow-2xl" onClick={e => e.stopPropagation()}>
            <div className="p-6 text-center">
              <div className="text-4xl mb-3">✅</div>
              <h3 className="text-xl font-bold mb-2">Accept this assignment?</h3>
              <p className="text-sm text-gray-400 mb-4">By accepting, you're confirming you can be at the appointment on time with all required equipment.</p>
              <div className="rounded-lg p-3 mb-4 text-left text-xs text-gray-400" style={{ background: 'rgba(45, 212, 191, 0.05)', border: '1px solid rgba(45, 212, 191, 0.15)' }}>
                <p className="font-bold text-white text-sm mb-2">What happens next:</p>
                <p className="mb-1">1️⃣ <b>Accept</b> → Assignment confirmed</p>
                <p className="mb-1">2️⃣ <b>Start</b> → Tap when you arrive at appointment</p>
                <p className="mb-1">3️⃣ <b>Complete</b> → Tap when signing is finished</p>
                <p className="mb-1">4️⃣ <b>Upload Scanback</b> → Upload scanned docs (required for payment)</p>
                <p>5️⃣ <b>Ship & Done</b> → DDI verifies and processes payment</p>
              </div>
              <div className="flex gap-3">
                <button className="flex-1 bg-green-600 hover:bg-green-700 px-4 py-3 rounded-lg font-bold transition"
                  onClick={() => handleAcceptOrder(showConfirmAccept)}>
                  ✅ Yes, Accept
                </button>
                <button className="bg-gray-700 hover:bg-gray-600 px-4 py-3 rounded-lg font-semibold transition"
                  onClick={() => setShowConfirmAccept(null)}>
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default FieldAgentPortal;
