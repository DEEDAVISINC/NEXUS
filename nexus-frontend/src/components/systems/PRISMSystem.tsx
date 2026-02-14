import React, { useState } from 'react';

interface PRISMSystemProps {
  onBackToNexus: () => void;
  onNavigate?: (view: any) => void;
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

// ─── SERVICE TYPE COLORS ───────────────────────────────────────────
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

// ─── MOCK DATA ─────────────────────────────────────────────────────
const mockOrders = [
  { id: 'PRISM-2026-0001', type: 'notary', status: 'In Progress', agent: 'Sarah Chen', client: 'Metro Title Co.', signer: 'James Wilson', address: 'Troy, MI', date: '02/14/2026', time: '1:00 PM', fee: 125, priority: 'Standard' },
  { id: 'PRISM-2026-0002', type: 'dot', status: 'Confirmed', agent: 'Marcus Brown', client: 'Champion Homes', signer: 'Robert Davis', address: 'Auburn Hills, MI', date: '02/14/2026', time: '9:00 AM', fee: 65, priority: 'Rush' },
  { id: 'PRISM-2026-0003', type: 'fingerprint', status: 'New', agent: '', client: 'Staffing Solutions Inc.', signer: 'Group (12 subjects)', address: 'Southfield, MI', date: '02/14/2026', time: '10:30 AM', fee: 480, priority: 'Standard' },
  { id: 'PRISM-2026-0004', type: 'dna', status: 'Scanned Back', agent: 'Dee Davis', client: 'Family Law Office', signer: 'Michael Thompson', address: 'Royal Oak, MI', date: '02/13/2026', time: '3:00 PM', fee: 75, priority: 'Standard' },
  { id: 'PRISM-2026-0005', type: 'notary', status: 'Errors Found', agent: 'Lisa Park', client: 'Homeland Title', signer: 'Angela Martinez', address: 'Farmington Hills, MI', date: '02/13/2026', time: '4:30 PM', fee: 150, priority: 'Standard' },
  { id: 'PRISM-2026-0006', type: 'non-dot', status: 'Assigned', agent: 'Marcus Brown', client: 'Acme Trucking', signer: 'Kevin Lee', address: 'Pontiac, MI', date: '02/15/2026', time: '8:00 AM', fee: 45, priority: 'Standard' },
  { id: 'PRISM-2026-0007', type: 'courier', status: 'Completed', agent: 'Dee Davis', client: 'Metro Title Co.', signer: 'N/A', address: 'Detroit, MI → Troy, MI', date: '02/13/2026', time: '11:00 AM', fee: 35, priority: 'Standard' },
  { id: 'PRISM-2026-0008', type: 'ron', status: 'Confirmed', agent: 'Sarah Chen', client: 'National Signing Co.', signer: 'Patricia Harris', address: 'Remote / Zoom', date: '02/14/2026', time: '2:30 PM', fee: 40, priority: 'Standard' },
  { id: 'PRISM-2026-0009', type: 'notary', status: 'Verified', agent: 'Lisa Park', client: 'First American Title', signer: 'David Kim', address: 'Bloomfield Hills, MI', date: '02/12/2026', time: '10:00 AM', fee: 175, priority: 'Standard' },
  { id: 'PRISM-2026-0010', type: 'background', status: 'New', agent: '', client: 'TempForce Staffing', signer: 'Group (8 subjects)', address: 'Southfield, MI', date: '02/15/2026', time: '9:00 AM', fee: 320, priority: 'Standard' },
];

const mockAgents = [
  { id: 'FA-0001', name: 'Sarah Chen', specialties: ['Signing Agent'], status: 'Active', city: 'Troy', state: 'MI', completionRate: 98, onTimeRate: 96, errorRate: 2, rating: 4.9, ordersCompleted: 147, activeOrders: 2 },
  { id: 'FA-0002', name: 'Marcus Brown', specialties: ['Collection Agent'], status: 'Active', city: 'Auburn Hills', state: 'MI', completionRate: 95, onTimeRate: 94, errorRate: 4, rating: 4.7, ordersCompleted: 89, activeOrders: 2 },
  { id: 'FA-0003', name: 'Lisa Park', specialties: ['Signing Agent', 'Courier'], status: 'Active', city: 'Farmington Hills', state: 'MI', completionRate: 97, onTimeRate: 99, errorRate: 1, rating: 4.9, ordersCompleted: 203, activeOrders: 1 },
  { id: 'FA-0004', name: 'Dee Davis', specialties: ['Signing Agent', 'Collection Agent', 'Print Technician', 'Courier'], status: 'Active', city: 'Troy', state: 'MI', completionRate: 100, onTimeRate: 100, errorRate: 0, rating: 5.0, ordersCompleted: 412, activeOrders: 2 },
  { id: 'FA-0005', name: 'Jamal Washington', specialties: ['Print Technician'], status: 'Active', city: 'Detroit', state: 'MI', completionRate: 93, onTimeRate: 91, errorRate: 5, rating: 4.5, ordersCompleted: 56, activeOrders: 0 },
  { id: 'FA-0006', name: 'Priya Patel', specialties: ['Signing Agent'], status: 'Screening', city: 'Novi', state: 'MI', completionRate: 0, onTimeRate: 0, errorRate: 0, rating: 0, ordersCompleted: 0, activeOrders: 0 },
];

const mockScanbacks = [
  { id: 'SB-001', orderId: 'PRISM-2026-0004', type: 'dna', agent: 'Dee Davis', status: 'Needs Review', pages: 4, expected: 4, uploadDate: '02/13/2026 3:42 PM', attempt: 1 },
  { id: 'SB-002', orderId: 'PRISM-2026-0005', type: 'notary', agent: 'Lisa Park', status: 'Errors Found', pages: 46, expected: 47, uploadDate: '02/13/2026 5:15 PM', attempt: 1, errors: [
    { severity: 'CRITICAL', page: 12, description: 'Patriot Act form — only 1 ID documented, requires 2' },
    { severity: 'CRITICAL', page: 37, description: 'Missing borrower initials on statement 3 of 5' },
    { severity: 'WARNING', page: 3, description: 'Signature appears on possible wrong line — verify borrower signed correct line' },
  ]},
  { id: 'SB-003', orderId: 'PRISM-2026-0009', type: 'notary', agent: 'Lisa Park', status: 'Clean', pages: 52, expected: 52, uploadDate: '02/12/2026 11:30 AM', attempt: 1 },
  { id: 'SB-004', orderId: 'PRISM-2026-0007', type: 'courier', agent: 'Dee Davis', status: 'Clean', pages: 1, expected: 1, uploadDate: '02/13/2026 11:45 AM', attempt: 1 },
];

const mockClients = [
  { id: 'PC-001', name: 'Champion Homes', type: 'Blueprint Enterprise', services: ['Drug Test (DOT)', 'Drug Test (Non-DOT)', 'Background Check'], orders: 47, revenue: 18500, status: 'Active', retainer: 25000 },
  { id: 'PC-002', name: 'Metro Title Co.', type: 'Title Company', services: ['Notary', 'Courier/Runner'], orders: 134, revenue: 28700, status: 'Active', retainer: 0 },
  { id: 'PC-003', name: 'Staffing Solutions Inc.', type: 'Blueprint Business', services: ['Fingerprinting/EFT', 'Background Check', 'Drug Test (Non-DOT)'], orders: 23, revenue: 9200, status: 'Active', retainer: 12000 },
  { id: 'PC-004', name: 'Family Law Office', type: 'Retail/One-Off', services: ['DNA Collection'], orders: 5, revenue: 1250, status: 'Active', retainer: 0 },
  { id: 'PC-005', name: 'First American Title', type: 'Title Company', services: ['Notary'], orders: 89, revenue: 22400, status: 'Active', retainer: 0 },
  { id: 'PC-006', name: 'TempForce Staffing', type: 'Blueprint Starter', services: ['Background Check', 'Fingerprinting/EFT'], orders: 8, revenue: 3200, status: 'Active', retainer: 6000 },
];

// ─── HELPER COMPONENTS ─────────────────────────────────────────────
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
  const [orderView, setOrderView] = useState<'list' | 'kanban' | 'calendar'>('list');
  const [orderFilter, setOrderFilter] = useState('all');
  const [selectedOrder, setSelectedOrder] = useState<string | null>(null);
  const [selectedScanback, setSelectedScanback] = useState<string | null>(null);
  const [showNewOrderModal, setShowNewOrderModal] = useState(false);
  const [scanbackFilter, setScanbackFilter] = useState('all');
  const [agentFilter, setAgentFilter] = useState('all');

  const tabs = [
    { id: 'dashboard', label: '🎯 Command Center' },
    { id: 'orders', label: '📋 Orders' },
    { id: 'dispatch', label: '🚀 Dispatch' },
    { id: 'scanbacks', label: '📸 Scanbacks' },
    { id: 'agents', label: '👤 Field Agents' },
    { id: 'clients', label: '🏢 Clients' },
    { id: 'inspection', label: '🔍 Inspection' },
    { id: 'payments', label: '💰 Payments' },
    { id: 'analytics', label: '📊 Analytics' },
  ];

  // Computed stats
  const todayOrders = mockOrders.filter(o => o.date === '02/14/2026');
  const activeOrders = mockOrders.filter(o => !['Closed', 'Verified'].includes(o.status));
  const awaitingScanback = mockOrders.filter(o => o.status === 'Completed');
  const errorsFound = mockOrders.filter(o => o.status === 'Errors Found');
  const unassigned = mockOrders.filter(o => o.status === 'New');
  const needsReview = mockScanbacks.filter(s => s.status === 'Needs Review');

  // Kanban columns
  const kanbanColumns = [
    { status: 'New', orders: mockOrders.filter(o => o.status === 'New') },
    { status: 'Assigned', orders: mockOrders.filter(o => o.status === 'Assigned') },
    { status: 'Confirmed', orders: mockOrders.filter(o => o.status === 'Confirmed') },
    { status: 'In Progress', orders: mockOrders.filter(o => o.status === 'In Progress') },
    { status: 'Completed', orders: mockOrders.filter(o => o.status === 'Completed') },
    { status: 'Scanned Back', orders: mockOrders.filter(o => o.status === 'Scanned Back') },
    { status: 'Errors Found', orders: mockOrders.filter(o => o.status === 'Errors Found') },
    { status: 'Verified', orders: mockOrders.filter(o => o.status === 'Verified') },
  ];

  const filteredOrders = orderFilter === 'all' ? mockOrders : mockOrders.filter(o => o.type === orderFilter);
  const filteredScanbacks = scanbackFilter === 'all' ? mockScanbacks : mockScanbacks.filter(s => s.status === scanbackFilter);
  const filteredAgents = agentFilter === 'all' ? mockAgents : mockAgents.filter(a => a.status === agentFilter);

  return (
    <div className="min-h-screen">
      {/* ─── TABS ───────────────────────────────────────── */}
      <div className="bg-gray-800 border-b border-gray-700 sticky top-[73px] z-40">
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex gap-1 overflow-x-auto py-1">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-4 py-3 text-sm font-semibold rounded-t-lg transition whitespace-nowrap ${
                  activeTab === tab.id
                    ? 'bg-gradient-to-r from-orange-500 to-amber-500 text-white'
                    : 'text-gray-400 hover:text-white hover:bg-gray-700'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* ─── CONTENT ────────────────────────────────────── */}
      <div className="max-w-7xl mx-auto px-6 py-6">

        {/* ════════════════════════════════════════════════════
            TAB: COMMAND CENTER
        ════════════════════════════════════════════════════ */}
        {activeTab === 'dashboard' && (
          <div>
            <div className="mb-6 flex items-center justify-between">
              <div>
                <h2 className="text-3xl font-bold mb-1">🎯 Command Center</h2>
                <p className="text-gray-400">PRISM — See every detail. Miss nothing.</p>
              </div>
              <div className="flex gap-2">
                <button onClick={() => setShowNewOrderModal(true)} className="bg-orange-500 hover:bg-orange-600 px-4 py-2 rounded-lg font-semibold text-sm transition">
                  + New Order
                </button>
                <button onClick={() => setActiveTab('dispatch')} className="bg-gray-700 hover:bg-gray-600 px-4 py-2 rounded-lg font-semibold text-sm transition">
                  🚀 Dispatch
                </button>
                {onNavigate && (
                  <>
                    <button onClick={() => onNavigate('agent-login')} className="px-4 py-2 rounded-lg font-semibold text-sm text-white transition" style={{ background: 'linear-gradient(135deg, #EC4899, #DB2777)' }}>
                      🔮 Agent Login Portal
                    </button>
                    <button onClick={() => onNavigate('agent-portal')} className="px-4 py-2 rounded-lg font-semibold text-sm text-white transition" style={{ background: '#1B2A4A', border: '1px solid rgba(45, 212, 191, 0.3)' }}>
                      👤 Preview (No Login)
                    </button>
                  </>
                )}
              </div>
            </div>

            {/* ── Stat Cards ── */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
              <StatCard label="Active Orders" value={activeOrders.length} icon="📋" color="orange" sub="In pipeline" />
              <StatCard label="Today's Appointments" value={todayOrders.length} icon="📅" color="blue" sub="Scheduled today" />
              <StatCard label="Awaiting Scanback" value={awaitingScanback.length} icon="📸" color="yellow" sub="Service done, no upload" />
              <StatCard label="Errors Found" value={errorsFound.length} icon="🚨" color="red" sub="Need correction" />
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
              <StatCard label="Orders This Month" value={mockOrders.length} icon="📊" color="purple" />
              <StatCard label="Active Field Agents" value={mockAgents.filter(a => a.status === 'Active').length} icon="👤" color="green" />
              <StatCard label="First-Pass Clean Rate" value="82%" icon="✅" color="emerald" sub="No errors on first scan" />
              <StatCard label="Revenue This Week" value="$4,210" icon="💰" color="blue" />
            </div>

            {/* ── Needs Your Attention ── */}
            {(errorsFound.length > 0 || unassigned.length > 0 || needsReview.length > 0) && (
              <div className="mb-8">
                <h3 className="text-lg font-bold mb-3 text-red-400">⚠️ Needs Your Attention</h3>
                <div className="space-y-2">
                  {errorsFound.map(o => (
                    <div key={o.id} className="flex items-center justify-between bg-red-500/10 border border-red-500/30 rounded-lg px-4 py-3 hover:bg-red-500/15 transition cursor-pointer"
                      onClick={() => { setActiveTab('scanbacks'); }}>
                      <div className="flex items-center gap-3">
                        <span className="text-red-400 font-bold text-sm">ERRORS</span>
                        <ServiceBadge type={o.type} />
                        <span className="text-sm">{o.id}</span>
                        <span className="text-gray-400 text-sm">— {o.agent}</span>
                      </div>
                      <span className="text-red-400 text-sm font-semibold">Review →</span>
                    </div>
                  ))}
                  {unassigned.map(o => (
                    <div key={o.id} className="flex items-center justify-between bg-yellow-500/10 border border-yellow-500/30 rounded-lg px-4 py-3 hover:bg-yellow-500/15 transition cursor-pointer"
                      onClick={() => { setActiveTab('dispatch'); }}>
                      <div className="flex items-center gap-3">
                        <span className="text-yellow-400 font-bold text-sm">UNASSIGNED</span>
                        <ServiceBadge type={o.type} />
                        <span className="text-sm">{o.id}</span>
                        <span className="text-gray-400 text-sm">— {o.client}</span>
                      </div>
                      <span className="text-yellow-400 text-sm font-semibold">Assign →</span>
                    </div>
                  ))}
                  {needsReview.map(s => (
                    <div key={s.id} className="flex items-center justify-between bg-blue-500/10 border border-blue-500/30 rounded-lg px-4 py-3 hover:bg-blue-500/15 transition cursor-pointer"
                      onClick={() => { setActiveTab('scanbacks'); }}>
                      <div className="flex items-center gap-3">
                        <span className="text-blue-400 font-bold text-sm">REVIEW</span>
                        <ServiceBadge type={s.type} />
                        <span className="text-sm">{s.orderId}</span>
                        <span className="text-gray-400 text-sm">— {s.agent}</span>
                      </div>
                      <span className="text-blue-400 text-sm font-semibold">Review →</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* ── Today's Schedule ── */}
            <div className="mb-8">
              <h3 className="text-lg font-bold mb-3">📅 Today's Schedule</h3>
              <div className="space-y-2">
                {todayOrders.sort((a, b) => a.time.localeCompare(b.time)).map(order => {
                  const svc = SERVICE_COLORS[order.type];
                  return (
                    <div key={order.id} className="flex items-center gap-4 bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 hover:border-gray-600 transition cursor-pointer"
                      style={{ borderLeftWidth: '4px', borderLeftColor: svc?.color || '#6B7280' }}
                      onClick={() => { setSelectedOrder(order.id); setActiveTab('orders'); }}>
                      <span className="text-sm font-mono text-gray-300 w-20">{order.time}</span>
                      <ServiceBadge type={order.type} />
                      <span className="text-sm font-semibold flex-1">{order.signer}</span>
                      <span className="text-sm text-gray-400">{order.address}</span>
                      <span className="text-sm text-gray-500">{order.agent || 'Unassigned'}</span>
                      <StatusBadge status={order.status} />
                    </div>
                  );
                })}
                {todayOrders.length === 0 && (
                  <div className="text-center py-8 text-gray-500">
                    <p className="text-lg mb-1">No appointments today</p>
                    <p className="text-sm">Create an order or check tomorrow's schedule</p>
                  </div>
                )}
              </div>
            </div>

            {/* ── Order Pipeline ── */}
            <div className="mb-8">
              <h3 className="text-lg font-bold mb-3">📊 Order Pipeline</h3>
              <div className="flex gap-2 overflow-x-auto pb-2">
                {kanbanColumns.map(col => (
                  <div key={col.status} className="flex-shrink-0 text-center">
                    <div className={`px-4 py-2 rounded-lg border ${STATUS_STYLES[col.status] || 'bg-gray-700 border-gray-600'}`}>
                      <p className="text-lg font-bold">{col.orders.length}</p>
                      <p className="text-xs">{col.status}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* ── Agent Leaderboard ── */}
            <div>
              <h3 className="text-lg font-bold mb-3">🏆 Agent Leaderboard</h3>
              <div className="bg-gray-800 border border-gray-700 rounded-xl overflow-hidden">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-gray-700 text-gray-400 text-xs uppercase">
                      <th className="text-left px-4 py-3">#</th>
                      <th className="text-left px-4 py-3">Agent</th>
                      <th className="text-center px-4 py-3">Orders</th>
                      <th className="text-center px-4 py-3">Completion</th>
                      <th className="text-center px-4 py-3">On-Time</th>
                      <th className="text-center px-4 py-3">Error Rate</th>
                      <th className="text-center px-4 py-3">Rating</th>
                    </tr>
                  </thead>
                  <tbody>
                    {mockAgents
                      .filter(a => a.status === 'Active')
                      .sort((a, b) => b.ordersCompleted - a.ordersCompleted)
                      .map((agent, i) => (
                        <tr key={agent.id} className="border-b border-gray-700/50 hover:bg-gray-700/30 transition cursor-pointer"
                          onClick={() => setActiveTab('agents')}>
                          <td className="px-4 py-3 font-bold text-gray-500">{i + 1}</td>
                          <td className="px-4 py-3 font-semibold">{agent.name}</td>
                          <td className="text-center px-4 py-3">{agent.ordersCompleted}</td>
                          <td className="text-center px-4 py-3 text-green-400">{agent.completionRate}%</td>
                          <td className="text-center px-4 py-3 text-blue-400">{agent.onTimeRate}%</td>
                          <td className="text-center px-4 py-3">
                            <span className={agent.errorRate <= 2 ? 'text-green-400' : agent.errorRate <= 5 ? 'text-yellow-400' : 'text-red-400'}>
                              {agent.errorRate}%
                            </span>
                          </td>
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
            TAB: ORDERS
        ════════════════════════════════════════════════════ */}
        {activeTab === 'orders' && (
          <div>
            <div className="mb-6 flex items-center justify-between">
              <div>
                <h2 className="text-3xl font-bold mb-1">📋 Orders</h2>
                <p className="text-gray-400">{mockOrders.length} total orders</p>
              </div>
              <div className="flex gap-2">
                <button onClick={() => setShowNewOrderModal(true)} className="bg-orange-500 hover:bg-orange-600 px-4 py-2 rounded-lg font-semibold text-sm transition">
                  + New Order
                </button>
              </div>
            </div>

            {/* View toggles + filters */}
            <div className="flex items-center justify-between mb-4">
              <div className="flex gap-1 bg-gray-800 rounded-lg p-1">
                {(['list', 'kanban', 'calendar'] as const).map(v => (
                  <button key={v} onClick={() => setOrderView(v)}
                    className={`px-3 py-1.5 rounded text-sm font-semibold transition capitalize ${orderView === v ? 'bg-gray-600 text-white' : 'text-gray-400 hover:text-white'}`}>
                    {v === 'list' ? '☰ List' : v === 'kanban' ? '▦ Kanban' : '📅 Calendar'}
                  </button>
                ))}
              </div>
              <div className="flex gap-2">
                <select value={orderFilter} onChange={e => setOrderFilter(e.target.value)}
                  className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-1.5 text-sm text-gray-300">
                  <option value="all">All Types</option>
                  {Object.entries(SERVICE_COLORS).map(([key, svc]) => (
                    <option key={key} value={key}>{svc.icon} {svc.label}</option>
                  ))}
                </select>
              </div>
            </div>

            {/* List View */}
            {orderView === 'list' && (
              <div className="bg-gray-800 border border-gray-700 rounded-xl overflow-hidden">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-gray-700 text-gray-400 text-xs uppercase">
                      <th className="text-left px-4 py-3">Order</th>
                      <th className="text-left px-4 py-3">Service</th>
                      <th className="text-left px-4 py-3">Status</th>
                      <th className="text-left px-4 py-3">Agent</th>
                      <th className="text-left px-4 py-3">Client</th>
                      <th className="text-left px-4 py-3">Signer/Subject</th>
                      <th className="text-left px-4 py-3">Date</th>
                      <th className="text-right px-4 py-3">Fee</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredOrders.map(order => {
                      const svc = SERVICE_COLORS[order.type];
                      return (
                        <tr key={order.id}
                          className={`border-b border-gray-700/50 hover:bg-gray-700/30 transition cursor-pointer ${selectedOrder === order.id ? 'bg-gray-700/50 ring-1 ring-orange-500/50' : ''}`}
                          style={{ borderLeftWidth: '3px', borderLeftColor: svc?.color || '#6B7280' }}
                          onClick={() => setSelectedOrder(selectedOrder === order.id ? null : order.id)}>
                          <td className="px-4 py-3 font-mono text-xs">{order.id}</td>
                          <td className="px-4 py-3"><ServiceBadge type={order.type} /></td>
                          <td className="px-4 py-3"><StatusBadge status={order.status} /></td>
                          <td className="px-4 py-3">{order.agent || <span className="text-yellow-400 text-xs font-semibold">UNASSIGNED</span>}</td>
                          <td className="px-4 py-3 text-gray-300">{order.client}</td>
                          <td className="px-4 py-3 text-gray-300">{order.signer}</td>
                          <td className="px-4 py-3 text-gray-400">{order.date} {order.time}</td>
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
                    <div className={`rounded-t-lg px-3 py-2 border-b-2 ${STATUS_STYLES[col.status] || 'bg-gray-700'}`}>
                      <div className="flex items-center justify-between">
                        <span className="font-semibold text-sm">{col.status}</span>
                        <span className="text-xs font-bold bg-white/10 px-2 py-0.5 rounded-full">{col.orders.length}</span>
                      </div>
                    </div>
                    <div className="space-y-2 mt-2 min-h-[200px]">
                      {col.orders.map(order => {
                        const svc = SERVICE_COLORS[order.type];
                        return (
                          <div key={order.id} className="bg-gray-800 border border-gray-700 rounded-lg p-3 hover:border-gray-600 transition cursor-pointer"
                            style={{ borderLeftWidth: '3px', borderLeftColor: svc?.color || '#6B7280' }}>
                            <div className="flex items-center justify-between mb-2">
                              <span className="text-xs font-mono text-gray-500">{order.id.split('-').pop()}</span>
                              <ServiceBadge type={order.type} size="sm" />
                            </div>
                            <p className="font-semibold text-sm mb-1">{order.signer}</p>
                            <p className="text-xs text-gray-400 mb-2">{order.address}</p>
                            <div className="flex items-center justify-between">
                              <span className="text-xs text-gray-500">{order.agent || 'Unassigned'}</span>
                              <span className="text-xs text-gray-500">{order.time}</span>
                            </div>
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
                    const dayOrders = mockOrders.filter(o => o.date === dateStr);
                    const isToday = day === 14;
                    return (
                      <div key={day} className={`min-h-[80px] border rounded-lg p-1 ${isToday ? 'border-orange-500 bg-orange-500/10' : 'border-gray-700 bg-gray-800/50'}`}>
                        <span className={`text-xs font-semibold ${isToday ? 'text-orange-400' : 'text-gray-500'}`}>{day}</span>
                        <div className="space-y-0.5 mt-1">
                          {dayOrders.slice(0, 3).map(o => {
                            const svc = SERVICE_COLORS[o.type];
                            return (
                              <div key={o.id} className="text-[10px] px-1 py-0.5 rounded truncate" style={{ backgroundColor: svc?.bg, color: svc?.color }}>
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
              const order = mockOrders.find(o => o.id === selectedOrder);
              if (!order) return null;
              const svc = SERVICE_COLORS[order.type];
              return (
                <div className="fixed inset-y-0 right-0 w-[480px] bg-gray-900 border-l border-gray-700 z-50 overflow-y-auto shadow-2xl">
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

                      <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
                        <h4 className="text-xs text-gray-500 uppercase mb-2 font-semibold">Client Rules</h4>
                        <div className="space-y-1">
                          <div className="flex items-center gap-2 text-sm"><span className="text-green-400">✓</span> Scanbacks required</div>
                          <div className="flex items-center gap-2 text-sm"><span className="text-green-400">✓</span> Blue pen only</div>
                          <div className="flex items-center gap-2 text-sm"><span className="text-green-400">✓</span> Ship same day via FedEx</div>
                        </div>
                      </div>

                      <div className="flex gap-2">
                        {order.status === 'New' && (
                          <button className="flex-1 bg-blue-600 hover:bg-blue-700 px-4 py-2.5 rounded-lg font-semibold text-sm transition">
                            🚀 Assign Agent
                          </button>
                        )}
                        {order.status === 'Errors Found' && (
                          <button className="flex-1 bg-red-600 hover:bg-red-700 px-4 py-2.5 rounded-lg font-semibold text-sm transition"
                            onClick={() => { setActiveTab('scanbacks'); setSelectedOrder(null); }}>
                            📸 View Scanback Errors
                          </button>
                        )}
                        <button className="bg-gray-700 hover:bg-gray-600 px-4 py-2.5 rounded-lg font-semibold text-sm transition">
                          ✏️ Edit
                        </button>
                      </div>
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
                          style={{ borderLeftWidth: '4px', borderLeftColor: svc?.color }}>
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
                  {mockAgents.filter(a => a.status === 'Active').map(agent => (
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
            TAB: SCANBACKS
        ════════════════════════════════════════════════════ */}
        {activeTab === 'scanbacks' && (
          <div>
            <div className="mb-6 flex items-center justify-between">
              <div>
                <h2 className="text-3xl font-bold mb-1">📸 Scanbacks</h2>
                <p className="text-gray-400">Document verification & inspection</p>
              </div>
              <div className="flex gap-1 bg-gray-800 rounded-lg p-1">
                {[
                  { key: 'all', label: 'All' },
                  { key: 'Needs Review', label: '🔍 Needs Review' },
                  { key: 'Errors Found', label: '🚨 Errors' },
                  { key: 'Clean', label: '✅ Clean' },
                ].map(f => (
                  <button key={f.key} onClick={() => setScanbackFilter(f.key)}
                    className={`px-3 py-1.5 rounded text-sm font-semibold transition ${scanbackFilter === f.key ? 'bg-gray-600 text-white' : 'text-gray-400 hover:text-white'}`}>
                    {f.label}
                  </button>
                ))}
              </div>
            </div>

            <div className="space-y-4">
              {filteredScanbacks.map(sb => {
                const svc = SERVICE_COLORS[sb.type];
                const isExpanded = selectedScanback === sb.id;
                return (
                  <div key={sb.id} className="bg-gray-800 border border-gray-700 rounded-xl overflow-hidden hover:border-gray-600 transition"
                    style={{ borderLeftWidth: '4px', borderLeftColor: svc?.color }}>
                    <div className="px-4 py-3 flex items-center justify-between cursor-pointer"
                      onClick={() => setSelectedScanback(isExpanded ? null : sb.id)}>
                      <div className="flex items-center gap-3">
                        <ServiceBadge type={sb.type} />
                        <span className="font-mono text-xs text-gray-500">{sb.orderId}</span>
                        <span className="text-sm text-gray-300">— {sb.agent}</span>
                      </div>
                      <div className="flex items-center gap-3">
                        <span className="text-xs text-gray-500">{sb.pages}/{sb.expected} pages</span>
                        <span className={`px-2 py-0.5 rounded-full text-xs font-semibold border ${
                          sb.status === 'Clean' ? 'bg-green-500/20 text-green-400 border-green-500/30' :
                          sb.status === 'Errors Found' ? 'bg-red-500/20 text-red-400 border-red-500/30' :
                          'bg-blue-500/20 text-blue-400 border-blue-500/30'
                        }`}>{sb.status}</span>
                        <span className="text-gray-500">{isExpanded ? '▲' : '▼'}</span>
                      </div>
                    </div>

                    {isExpanded && (
                      <div className="border-t border-gray-700 px-4 py-4">
                        <div className="grid grid-cols-3 gap-4 mb-4 text-sm">
                          <div><span className="text-gray-500 text-xs block">Upload Date</span>{sb.uploadDate}</div>
                          <div><span className="text-gray-500 text-xs block">Attempt</span>#{sb.attempt}</div>
                          <div><span className="text-gray-500 text-xs block">Page Match</span>
                            {sb.pages === sb.expected ? <span className="text-green-400">✅ {sb.pages}/{sb.expected}</span> : <span className="text-red-400">❌ {sb.pages}/{sb.expected}</span>}
                          </div>
                        </div>

                        {sb.errors && sb.errors.length > 0 && (
                          <div className="mb-4">
                            <h4 className="text-sm font-bold text-red-400 mb-2">Inspection Report</h4>
                            <div className="space-y-2">
                              {sb.errors.map((err, i) => (
                                <div key={i} className={`px-3 py-2 rounded-lg text-sm ${
                                  err.severity === 'CRITICAL' ? 'bg-red-500/10 border border-red-500/30' : 'bg-yellow-500/10 border border-yellow-500/30'
                                }`}>
                                  <div className="flex items-center gap-2 mb-1">
                                    <span className={`text-xs font-bold ${err.severity === 'CRITICAL' ? 'text-red-400' : 'text-yellow-400'}`}>
                                      {err.severity}
                                    </span>
                                    <span className="text-xs text-gray-500">Page {err.page}</span>
                                  </div>
                                  <p className="text-gray-300">{err.description}</p>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}

                        <div className="flex gap-2">
                          {sb.status === 'Needs Review' && (
                            <>
                              <button className="bg-green-600 hover:bg-green-700 px-4 py-2 rounded-lg font-semibold text-sm transition">✅ Mark Clean</button>
                              <button className="bg-red-600 hover:bg-red-700 px-4 py-2 rounded-lg font-semibold text-sm transition">🚨 Flag Errors</button>
                            </>
                          )}
                          {sb.status === 'Errors Found' && (
                            <button className="bg-orange-600 hover:bg-orange-700 px-4 py-2 rounded-lg font-semibold text-sm transition">📩 Send Correction Request</button>
                          )}
                          <button className="bg-gray-700 hover:bg-gray-600 px-4 py-2 rounded-lg font-semibold text-sm transition">👁 View Documents</button>
                          <button className="bg-gray-700 hover:bg-gray-600 px-4 py-2 rounded-lg font-semibold text-sm transition">🔄 Re-Inspect</button>
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
                <p className="text-gray-400">{mockAgents.length} agents in network</p>
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
                <p className="text-gray-400">{mockClients.length} active clients</p>
              </div>
              <button className="bg-orange-500 hover:bg-orange-600 px-4 py-2 rounded-lg font-semibold text-sm transition">
                + Add Client
              </button>
            </div>

            <div className="space-y-4">
              {mockClients.map(client => (
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
        {activeTab === 'inspection' && (
          <div>
            <div className="mb-6">
              <h2 className="text-3xl font-bold mb-1">🔍 Inspection Engine</h2>
              <p className="text-gray-400">Rules, learned patterns, and accuracy tracking</p>
            </div>

            {/* The 7 Fundamentals */}
            <div className="mb-8">
              <h3 className="text-lg font-bold mb-3">The 7 Fundamentals (Never Change)</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {[
                  { num: 1, check: 'Every required signature present?', accuracy: 97, triggered: 234 },
                  { num: 2, check: 'Every required initial present?', accuracy: 94, triggered: 189 },
                  { num: 3, check: 'Every required date filled in?', accuracy: 96, triggered: 156 },
                  { num: 4, check: 'Notary seal/stamp present where required?', accuracy: 99, triggered: 78 },
                  { num: 5, check: 'All required pages/forms included?', accuracy: 100, triggered: 312 },
                  { num: 6, check: 'ID copy included (when required)?', accuracy: 92, triggered: 45 },
                  { num: 7, check: 'No markings where there shouldn\'t be?', accuracy: 88, triggered: 23 },
                ].map(rule => (
                  <div key={rule.num} className="bg-gray-800 border border-gray-700 rounded-lg p-4 flex items-center gap-4 hover:border-gray-600 transition">
                    <div className="w-8 h-8 bg-orange-500/20 text-orange-400 rounded-full flex items-center justify-center font-bold text-sm flex-shrink-0">
                      {rule.num}
                    </div>
                    <div className="flex-1">
                      <p className="text-sm font-semibold">{rule.check}</p>
                      <div className="flex gap-4 text-xs text-gray-500 mt-1">
                        <span>Accuracy: <span className={rule.accuracy >= 95 ? 'text-green-400' : 'text-yellow-400'}>{rule.accuracy}%</span></span>
                        <span>Triggered {rule.triggered}x</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Adaptive Learning */}
            <div className="mb-8">
              <h3 className="text-lg font-bold mb-3">🧠 Adaptive Learning</h3>
              <div className="grid grid-cols-3 gap-4 mb-4">
                <div className="bg-gray-800 border border-gray-700 rounded-xl p-4 text-center">
                  <p className="text-xs text-gray-500 uppercase mb-1">Level 1: Rule-Based</p>
                  <p className="text-2xl font-bold text-green-400">7</p>
                  <p className="text-xs text-gray-500">Active rules</p>
                </div>
                <div className="bg-gray-800 border border-gray-700 rounded-xl p-4 text-center">
                  <p className="text-xs text-gray-500 uppercase mb-1">Level 2: Learned Patterns</p>
                  <p className="text-2xl font-bold text-blue-400">3</p>
                  <p className="text-xs text-gray-500">Patterns discovered</p>
                </div>
                <div className="bg-gray-800 border border-gray-700 rounded-xl p-4 text-center">
                  <p className="text-xs text-gray-500 uppercase mb-1">Level 3: Anomalies</p>
                  <p className="text-2xl font-bold text-purple-400">0</p>
                  <p className="text-xs text-gray-500">Needs more data</p>
                </div>
              </div>

              <div className="bg-gray-800 border border-gray-700 rounded-xl p-5">
                <h4 className="font-semibold mb-3">Learned Patterns</h4>
                <div className="space-y-3">
                  {[
                    { pattern: 'Light ink on page 12 of refinance packages correlates with 73% rejection rate', confidence: 87, source: '47 observations' },
                    { pattern: 'Missing date on CCF Step 2 when collector is under 6 months experience', confidence: 78, source: '23 observations' },
                    { pattern: 'Second ID document consistently missing on Patriot Act forms from Title Company X', confidence: 91, source: '15 observations' },
                  ].map((p, i) => (
                    <div key={i} className="bg-gray-700/50 rounded-lg p-3">
                      <p className="text-sm">{p.pattern}</p>
                      <div className="flex gap-4 text-xs text-gray-500 mt-2">
                        <span>Confidence: <span className={p.confidence >= 85 ? 'text-green-400' : 'text-yellow-400'}>{p.confidence}%</span></span>
                        <span>{p.source}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Recent Misses */}
            <div>
              <h3 className="text-lg font-bold mb-3">🚫 Recent Misses (Post-Ship Rejections)</h3>
              <div className="bg-gray-800 border border-gray-700 rounded-xl p-5">
                <div className="text-center py-4 text-gray-500">
                  <p className="text-lg mb-1">No post-ship rejections this month</p>
                  <p className="text-sm">This means the inspection engine is catching everything. 💪</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* ════════════════════════════════════════════════════
            TAB: PAYMENTS
        ════════════════════════════════════════════════════ */}
        {activeTab === 'payments' && (
          <div>
            <div className="mb-6">
              <h2 className="text-3xl font-bold mb-1">💰 Payments</h2>
              <p className="text-gray-400">Agent payouts & margin tracking</p>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
              <StatCard label="Pending Payouts" value="$685" icon="⏳" color="yellow" />
              <StatCard label="Paid This Month" value="$3,525" icon="✅" color="green" />
              <StatCard label="Revenue This Month" value="$8,210" icon="💰" color="blue" />
              <StatCard label="Avg Margin" value="57%" icon="📈" color="purple" />
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
                      {[
                        { agent: 'Sarah Chen', order: 'PRISM-2026-0001', amount: 145, status: 'Pending' },
                        { agent: 'Marcus Brown', order: 'PRISM-2026-0002', amount: 85, status: 'Pending' },
                        { agent: 'Lisa Park', order: 'PRISM-2026-0005', amount: 170, status: 'On Hold (Errors)' },
                        { agent: 'Dee Davis', order: 'PRISM-2026-0004', amount: 75, status: 'Approved' },
                        { agent: 'Dee Davis', order: 'PRISM-2026-0007', amount: 35, status: 'Approved' },
                      ].map((p, i) => (
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
                  {[
                    { type: 'notary', revenue: 4200, cost: 1800, orders: 5 },
                    { type: 'dot', revenue: 1400, cost: 520, orders: 3 },
                    { type: 'fingerprint', revenue: 1440, cost: 480, orders: 2 },
                    { type: 'dna', revenue: 500, cost: 150, orders: 2 },
                    { type: 'courier', revenue: 280, cost: 70, orders: 2 },
                  ].map(m => {
                    const margin = Math.round(((m.revenue - m.cost) / m.revenue) * 100);
                    const svc = SERVICE_COLORS[m.type];
                    return (
                      <div key={m.type} className="bg-gray-800 border border-gray-700 rounded-lg p-4" style={{ borderLeftWidth: '4px', borderLeftColor: svc?.color }}>
                        <div className="flex items-center justify-between mb-2">
                          <ServiceBadge type={m.type} />
                          <span className="text-xs text-gray-500">{m.orders} orders</span>
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
              <p className="text-gray-400">Volume, quality, revenue, and agent performance</p>
            </div>

            {/* Volume by Service Type */}
            <div className="mb-8">
              <h3 className="text-lg font-bold mb-3">Volume by Service Type</h3>
              <div className="bg-gray-800 border border-gray-700 rounded-xl p-5">
                <div className="space-y-3">
                  {[
                    { type: 'notary', count: 134, pct: 45 },
                    { type: 'dot', count: 47, pct: 16 },
                    { type: 'fingerprint', count: 38, pct: 13 },
                    { type: 'non-dot', count: 29, pct: 10 },
                    { type: 'dna', count: 18, pct: 6 },
                    { type: 'courier', count: 15, pct: 5 },
                    { type: 'background', count: 8, pct: 3 },
                    { type: 'ron', count: 6, pct: 2 },
                  ].map(item => {
                    const svc = SERVICE_COLORS[item.type];
                    return (
                      <div key={item.type} className="flex items-center gap-4">
                        <div className="w-40"><ServiceBadge type={item.type} /></div>
                        <div className="flex-1">
                          <div className="h-6 bg-gray-700 rounded-full overflow-hidden">
                            <div className="h-full rounded-full flex items-center px-2" style={{ width: `${item.pct}%`, backgroundColor: svc?.color }}>
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
                <StatCard label="First-Pass Rate" value="82%" icon="✅" color="green" sub="Clean on first upload" />
                <StatCard label="Rejection Rate" value="1.2%" icon="🚫" color="red" sub="Post-ship rejections" />
                <StatCard label="Avg Correction Time" value="2.4 hrs" icon="⏱" color="yellow" sub="Time to fix errors" />
                <StatCard label="Most Common Error" value="Missing Initial" icon="📝" color="orange" sub="31% of all errors" />
              </div>
            </div>

            {/* Revenue Breakdown */}
            <div className="mb-8">
              <h3 className="text-lg font-bold mb-3">Revenue & Margin</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <StatCard label="Revenue (Month)" value="$8,210" icon="💰" color="green" />
                <StatCard label="Agent Costs" value="$3,020" icon="💸" color="red" />
                <StatCard label="Net Margin" value="$5,190" icon="📈" color="purple" />
                <StatCard label="Margin %" value="63%" icon="🎯" color="blue" />
              </div>
            </div>

            {/* Agent Utilization */}
            <div>
              <h3 className="text-lg font-bold mb-3">Agent Utilization</h3>
              <div className="bg-gray-800 border border-gray-700 rounded-xl p-5">
                <div className="space-y-3">
                  {mockAgents.filter(a => a.status === 'Active').map(agent => {
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
                  {mockClients.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
                </select>
              </div>
              <div>
                <label className="block text-xs font-semibold text-gray-500 mb-1">Special Instructions</label>
                <textarea className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm focus:border-orange-500 focus:outline-none transition h-20 resize-none" placeholder="Blue pen, legal paper, etc." />
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
