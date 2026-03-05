import React, { useState, useEffect, useCallback } from 'react';
import { api } from '../../api/client';

interface PRISMSystemProps {
  onBackToNexus: () => void;
  onNavigate?: (view: any) => void;
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

// ─── SERVICE TYPE COLORS ───────────────────────────────────────────
const SERVICE_COLORS: Record<string, { color: string; bg: string; label: string; icon: string; border: string }> = {
  'notary':          { color: '#F97316', bg: '#FFF7ED', label: 'Notary',              icon: '🟠', border: '#FB923C' },
  'ron':             { color: '#6366F1', bg: '#EEF2FF', label: 'Notary (RON)',        icon: '🟣', border: '#818CF8' },
  'dot':             { color: '#EF4444', bg: '#FEF2F2', label: 'Drug Test (DOT)',     icon: '🔴', border: '#F87171' },
  'non-dot':         { color: '#F43F5E', bg: '#FFF1F2', label: 'Drug Test (Non-DOT)', icon: '🔴', border: '#FB7185' },
  'dna':             { color: '#A855F7', bg: '#FAF5FF', label: 'DNA Collection',      icon: '🟣', border: '#C084FC' },
  'fingerprint':     { color: '#22C55E', bg: '#F0FDF4', label: 'Fingerprinting/EFT',  icon: '🟢', border: '#4ADE80' },
  'phlebotomy':      { color: '#DC2626', bg: '#FEF2F2', label: 'Phlebotomy',          icon: '🔴', border: '#EF4444' },
  'medical_courier': { color: '#0EA5E9', bg: '#F0F9FF', label: 'Medical Courier',     icon: '🔵', border: '#38BDF8' },
  'courier':         { color: '#3B82F6', bg: '#EFF6FF', label: 'Courier/Runner',      icon: '🔵', border: '#60A5FA' },
  'background':      { color: '#64748B', bg: '#F8FAFC', label: 'Background Check',    icon: '⚫', border: '#94A3B8' },
  'apostille':       { color: '#EAB308', bg: '#FEFCE8', label: 'Apostille',           icon: '🟡', border: '#FACC15' },
  'process':         { color: '#14B8A6', bg: '#F0FDFA', label: 'Process Serving',     icon: '🟢', border: '#2DD4BF' },
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

// ─── TYPES ──────────────────────────────────────────────────────────
interface PrismOrder { id: string; type: string; status: string; agent: string; client: string; signer: string; address: string; date: string; time: string; fee: number; priority: string; }
interface PrismAgent { id: string; name: string; specialties: string[]; status: string; city: string; state: string; completionRate: number; onTimeRate: number; errorRate: number; rating: number; ordersCompleted: number; activeOrders: number; }
interface PrismScanback { id: string; orderId: string; type: string; agent: string; status: string; pages: number; expected: number; uploadDate: string; attempt: number; errors?: { severity: string; page: number; description: string }[]; }
interface PrismClient { id: string; name: string; type: string; services: string[]; orders: number; revenue: number; status: string; retainer: number; }

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

  const [orders, setOrders] = useState<PrismOrder[]>([]);
  const [agents, setAgents] = useState<PrismAgent[]>([]);
  const [scanbacks, setScanbacks] = useState<PrismScanback[]>([]);
  const [clients, setClients] = useState<PrismClient[]>([]);
  const [prismStats, setPrismStats] = useState<any>(null);
  const [dataLoading, setDataLoading] = useState(true);
  const [notifications, setNotifications] = useState<any[]>([]);
  const [showNotifPanel, setShowNotifPanel] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);

  const loadPrismData = useCallback(async () => {
    setDataLoading(true);
    try {
      const [ordersRes, agentsRes, scanbacksRes, clientsRes] = await Promise.allSettled([
        api.get('/prism/orders').catch(() => ({ data: { orders: [] } })),
        api.get('/prism/agents').catch(() => ({ data: { agents: [] } })),
        api.get('/prism/qc/queue').catch(() => ({ data: { queue: [] } })),
        api.get('/prism/clients').catch(() => ({ data: { clients: [] } })),
      ]);
      if (ordersRes.status === 'fulfilled') setOrders((ordersRes.value as any).data?.orders || []);
      if (agentsRes.status === 'fulfilled') setAgents((agentsRes.value as any).data?.agents || []);
      if (scanbacksRes.status === 'fulfilled') setScanbacks((scanbacksRes.value as any).data?.queue || []);
      if (clientsRes.status === 'fulfilled') setClients((clientsRes.value as any).data?.clients || []);
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
    const interval = setInterval(loadNotifications, 15000);
    return () => clearInterval(interval);
  }, [loadNotifications]);

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

  const today = new Date().toLocaleDateString('en-US', { month: '2-digit', day: '2-digit', year: 'numeric' });
  const todayOrders = orders.filter(o => o.date === today);
  const activeOrders = orders.filter(o => !['Closed', 'Verified'].includes(o.status));
  const awaitingScanback = orders.filter(o => o.status === 'Completed');
  const errorsFound = orders.filter(o => o.status === 'Errors Found');
  const unassigned = orders.filter(o => o.status === 'New');
  const needsReview = scanbacks.filter(s => s.status === 'Needs Review');

  const kanbanColumns = [
    { status: 'New', orders: orders.filter(o => o.status === 'New') },
    { status: 'Assigned', orders: orders.filter(o => o.status === 'Assigned') },
    { status: 'Confirmed', orders: orders.filter(o => o.status === 'Confirmed') },
    { status: 'In Progress', orders: orders.filter(o => o.status === 'In Progress') },
    { status: 'Completed', orders: orders.filter(o => o.status === 'Completed') },
    { status: 'Scanned Back', orders: orders.filter(o => o.status === 'Scanned Back') },
    { status: 'Errors Found', orders: orders.filter(o => o.status === 'Errors Found') },
    { status: 'Verified', orders: orders.filter(o => o.status === 'Verified') },
  ];

  const filteredOrders = orderFilter === 'all' ? orders : orders.filter(o => o.type === orderFilter);
  const filteredScanbacks = scanbackFilter === 'all' ? scanbacks : scanbacks.filter(s => s.status === scanbackFilter);
  const filteredAgents = agentFilter === 'all' ? agents : agents.filter(a => a.status === agentFilter);

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

            {/* ── Notification Panel ── */}
            {showNotifPanel && (
              <div className="relative mb-4 z-50">
                <div className="absolute right-0 top-0 w-[420px] rounded-xl shadow-2xl max-h-[60vh] overflow-hidden" style={{ background: '#0F1A2E', border: '1px solid rgba(45, 212, 191, 0.2)' }}>
                  <div className="p-4 flex items-center justify-between" style={{ borderBottom: '1px solid rgba(45, 212, 191, 0.1)' }}>
                    <h3 className="font-bold text-sm">🔔 Notifications {unreadCount > 0 && <span className="text-orange-400 ml-1">({unreadCount} new)</span>}</h3>
                    <div className="flex gap-2">
                      {unreadCount > 0 && (
                        <button onClick={() => markNotificationsRead()} className="text-xs text-teal-400 hover:text-teal-300 font-semibold">Mark all read</button>
                      )}
                      <button onClick={() => setShowNotifPanel(false)} className="text-gray-500 hover:text-white text-sm">✕</button>
                    </div>
                  </div>
                  <div className="divide-y divide-gray-800 overflow-y-auto max-h-[50vh]">
                    {notifications.length === 0 && (
                      <div className="p-6 text-center text-gray-500 text-sm">No notifications yet</div>
                    )}
                    {notifications.map(n => {
                      const severityBorder = n.severity === 'error' ? 'border-l-red-500' : n.severity === 'warning' ? 'border-l-yellow-500' : n.severity === 'success' ? 'border-l-green-500' : 'border-l-blue-500';
                      const age = (() => {
                        const diff = Date.now() - new Date(n.created_at).getTime();
                        const mins = Math.floor(diff / 60000);
                        if (mins < 1) return 'just now';
                        if (mins < 60) return `${mins}m ago`;
                        const hrs = Math.floor(mins / 60);
                        if (hrs < 24) return `${hrs}h ago`;
                        return `${Math.floor(hrs / 24)}d ago`;
                      })();
                      return (
                        <div key={n.id} className={`px-4 py-3 hover:bg-gray-800/50 transition cursor-pointer border-l-4 ${severityBorder} ${!n.read ? 'bg-gray-800/30' : ''}`}
                          onClick={() => { if (!n.read) markNotificationsRead([n.id]); if (n.order_id) { setSelectedOrder(n.order_id); setActiveTab('orders'); setShowNotifPanel(false); } }}>
                          <div className="flex items-start gap-2">
                            {!n.read && <div className="w-2 h-2 rounded-full mt-1.5 flex-shrink-0 bg-orange-400"></div>}
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center gap-2 mb-0.5">
                                <span className="text-sm">{n.icon}</span>
                                <span className="text-xs font-bold text-white">{n.title}</span>
                                <span className="text-[10px] text-gray-500 ml-auto flex-shrink-0">{age}</span>
                              </div>
                              <p className="text-xs text-gray-400 truncate">{n.message}</p>
                              {n.order_id && <span className="text-[10px] text-gray-600 font-mono">{n.order_id}</span>}
                            </div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </div>
            )}

            {/* ── Stat Cards ── */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
              <StatCard label="Active Orders" value={activeOrders.length} icon="📋" color="orange" sub="In pipeline" />
              <StatCard label="Today's Appointments" value={todayOrders.length} icon="📅" color="blue" sub="Scheduled today" />
              <StatCard label="Awaiting Scanback" value={awaitingScanback.length} icon="📸" color="yellow" sub="Service done, no upload" />
              <StatCard label="Errors Found" value={errorsFound.length} icon="🚨" color="red" sub="Need correction" />
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
              <StatCard label="Orders This Month" value={orders.length} icon="📊" color="purple" />
              <StatCard label="Active Field Agents" value={agents.filter(a => a.status === 'Active').length} icon="👤" color="green" />
              <StatCard label="First-Pass Clean Rate" value={prismStats?.clean_rate || '—'} icon="✅" color="emerald" sub="No errors on first scan" />
              <StatCard label="Revenue This Week" value={prismStats?.weekly_revenue || '—'} icon="💰" color="blue" />
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
                    {agents
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
                <p className="text-gray-400">{orders.length} total orders</p>
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
                    const dayOrders = orders.filter(o => o.date === dateStr);
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
              const order = orders.find(o => o.id === selectedOrder);
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
                <p className="text-gray-400">{agents.length} agents in network</p>
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
                <p className="text-gray-400">{clients.length} active clients</p>
              </div>
              <button className="bg-orange-500 hover:bg-orange-600 px-4 py-2 rounded-lg font-semibold text-sm transition">
                + Add Client
              </button>
            </div>

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
                  { num: 1, check: 'Every required signature present?' },
                  { num: 2, check: 'Every required initial present?' },
                  { num: 3, check: 'Every required date filled in?' },
                  { num: 4, check: 'Notary seal/stamp present where required?' },
                  { num: 5, check: 'All required pages/forms included?' },
                  { num: 6, check: 'ID copy included (when required)?' },
                  { num: 7, check: 'No markings where there shouldn\'t be?' },
                ].map(rule => (
                  <div key={rule.num} className="bg-gray-800 border border-gray-700 rounded-lg p-4 flex items-center gap-4 hover:border-gray-600 transition">
                    <div className="w-8 h-8 bg-orange-500/20 text-orange-400 rounded-full flex items-center justify-center font-bold text-sm flex-shrink-0">
                      {rule.num}
                    </div>
                    <div className="flex-1">
                      <p className="text-sm font-semibold">{rule.check}</p>
                      <div className="flex gap-4 text-xs text-gray-500 mt-1">
                        <span className="text-green-400">Active</span>
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
                  {scanbacks.length === 0 ? (
                    <div className="text-center py-4 text-gray-500 text-sm">
                      Patterns will appear as PRISM processes more scanbacks and identifies recurring issues.
                    </div>
                  ) : (
                    <div className="text-center py-4 text-gray-500 text-sm">
                      Learning from {scanbacks.length} scanback{scanbacks.length !== 1 ? 's' : ''}. More data needed for pattern detection.
                    </div>
                  )}
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
                    acc[o.type].cost += Math.round((o.fee || 0) * 0.4);
                    acc[o.type].orders += 1;
                    return acc;
                  }, {})).map(([, m]) => m).sort((a, b) => b.revenue - a.revenue).slice(0, 5).map(m => {
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
