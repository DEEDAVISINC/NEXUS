import React, { useState, useEffect } from 'react';

// ─── TYPES ─────────────────────────────────────────────────────────────────
interface ClientOrder {
  id: string;
  type: string;
  subject: string;
  status: 'pending' | 'scheduled' | 'in_progress' | 'completed' | 'cancelled';
  scheduledDate?: string;
  scheduledTime?: string;
  location?: string;
  notes: string;
  createdAt: string;
  result?: string;
  resultFileUrl?: string;
  invoiceId?: string;
}

interface ClientDocument {
  id: string;
  orderId: string;
  name: string;
  type: 'result' | 'scanback' | 'report' | 'invoice' | 'certificate' | 'pod';
  date: string;
  downloadUrl: string;
  subject?: string;
  status?: 'ready' | 'processing';
}

interface Invoice {
  id: string;
  date: string;
  dueDate: string;
  amount: number;
  status: 'paid' | 'pending' | 'overdue';
  orderIds: string[];
  paidDate?: string;
  pdfUrl?: string;
}

interface CalendarEvent {
  id: string;
  date: string;
  time: string;
  title: string;
  subtitle: string;
  type: string;
  color: string;
  orderId: string;
}

interface ClientInfo {
  id: string;
  name: string;
  code: string;
  contactName: string;
  services: string[];
  serviceCategory: 'drug_testing' | 'notary' | 'nemt' | 'courier' | 'fingerprinting' | 'dna' | 'multi';
  logoUrl?: string;
}

interface ClientPortalProps {
  clientCode: string;
}

// ─── MOCK DATA ──────────────────────────────────────────────────────────────
const MOCK_CLIENT: ClientInfo = {
  id: 'c1',
  name: 'ABC Trucking Co.',
  code: 'ABC-7X9K2',
  contactName: 'Mike Johnson',
  services: ['dot', 'non_dot', 'random', 'pre_employment', 'post_accident', 'return_to_duty'],
  serviceCategory: 'drug_testing',
};

const MOCK_ORDERS: ClientOrder[] = [
  { id: 'ORD-2026-0542', type: 'pre_employment', subject: 'James Wilson', status: 'scheduled', scheduledDate: '2026-05-19', scheduledTime: '10:00 AM', location: 'Quest Diagnostics - Troy, MI', notes: 'New driver hire', createdAt: '2026-05-17' },
  { id: 'ORD-2026-0540', type: 'random', subject: 'Patricia Moore', status: 'scheduled', scheduledDate: '2026-05-21', scheduledTime: '2:00 PM', location: 'Quest Diagnostics - Southfield, MI', notes: 'Q2 random pool', createdAt: '2026-05-17' },
  { id: 'ORD-2026-0538', type: 'post_accident', subject: 'Robert Chen', status: 'completed', scheduledDate: '2026-05-18', scheduledTime: '2:30 PM', location: 'On-site collection', notes: 'Minor incident', createdAt: '2026-05-18', result: 'Negative', resultFileUrl: '#', invoiceId: 'INV-2026-0089' },
  { id: 'ORD-2026-0535', type: 'random', subject: 'Maria Garcia', status: 'completed', scheduledDate: '2026-05-15', scheduledTime: '9:00 AM', location: 'Quest Diagnostics - Southfield, MI', notes: 'Q2 random selection', createdAt: '2026-05-14', result: 'Negative', resultFileUrl: '#', invoiceId: 'INV-2026-0089' },
  { id: 'ORD-2026-0530', type: 'dot', subject: 'Anthony Davis', status: 'completed', scheduledDate: '2026-05-10', scheduledTime: '11:00 AM', location: 'Quest Diagnostics - Troy, MI', notes: 'Annual DOT', createdAt: '2026-05-08', result: 'Negative', resultFileUrl: '#', invoiceId: 'INV-2026-0085' },
  { id: 'ORD-2026-0525', type: 'pre_employment', subject: 'Lisa Thompson', status: 'completed', scheduledDate: '2026-05-05', scheduledTime: '1:00 PM', location: 'On-site collection', notes: 'New hire', createdAt: '2026-05-03', result: 'Negative', resultFileUrl: '#', invoiceId: 'INV-2026-0085' },
];

const MOCK_DOCUMENTS: ClientDocument[] = [
  { id: 'd1', orderId: 'ORD-2026-0538', name: 'Lab Result - Robert Chen', type: 'result', date: '2026-05-18', downloadUrl: '#', subject: 'Robert Chen', status: 'ready' },
  { id: 'd2', orderId: 'ORD-2026-0535', name: 'Lab Result - Maria Garcia', type: 'result', date: '2026-05-16', downloadUrl: '#', subject: 'Maria Garcia', status: 'ready' },
  { id: 'd3', orderId: 'ORD-2026-0530', name: 'Lab Result - Anthony Davis', type: 'result', date: '2026-05-12', downloadUrl: '#', subject: 'Anthony Davis', status: 'ready' },
  { id: 'd4', orderId: 'ORD-2026-0525', name: 'Lab Result - Lisa Thompson', type: 'result', date: '2026-05-07', downloadUrl: '#', subject: 'Lisa Thompson', status: 'ready' },
  { id: 'd5', orderId: '', name: 'Q1 2026 Compliance Report', type: 'report', date: '2026-04-01', downloadUrl: '#', status: 'ready' },
  { id: 'd6', orderId: '', name: 'Random Testing Pool Certificate', type: 'certificate', date: '2026-01-15', downloadUrl: '#', status: 'ready' },
];

const MOCK_INVOICES: Invoice[] = [
  { id: 'INV-2026-0089', date: '2026-05-15', dueDate: '2026-06-14', amount: 250.00, status: 'pending', orderIds: ['ORD-2026-0538', 'ORD-2026-0535'], pdfUrl: '#' },
  { id: 'INV-2026-0085', date: '2026-04-15', dueDate: '2026-05-15', amount: 375.00, status: 'paid', orderIds: ['ORD-2026-0530', 'ORD-2026-0525'], paidDate: '2026-05-10', pdfUrl: '#' },
];

const SERVICE_TYPES: Record<string, { label: string; color: string; short: string }> = {
  dot: { label: 'DOT Drug Test', color: '#2563EB', short: 'DOT' },
  non_dot: { label: 'Non-DOT Drug Test', color: '#7C3AED', short: 'Non-DOT' },
  random: { label: 'Random Selection', color: '#0891B2', short: 'Random' },
  pre_employment: { label: 'Pre-Employment', color: '#059669', short: 'Pre-Emp' },
  post_accident: { label: 'Post-Accident', color: '#DC2626', short: 'Post-Acc' },
  return_to_duty: { label: 'Return to Duty', color: '#D97706', short: 'RTD' },
  reasonable_suspicion: { label: 'Reasonable Suspicion', color: '#BE185D', short: 'R. Susp' },
  follow_up: { label: 'Follow-Up', color: '#4F46E5', short: 'Follow-Up' },
};

const DOC_TYPE_META: Record<string, { icon: string; label: string; color: string }> = {
  result: { icon: '🧬', label: 'Lab Result', color: '#059669' },
  scanback: { icon: '📄', label: 'Scanback', color: '#2563EB' },
  report: { icon: '📊', label: 'Report', color: '#7C3AED' },
  invoice: { icon: '💳', label: 'Invoice', color: '#D97706' },
  certificate: { icon: '🏅', label: 'Certificate', color: '#0891B2' },
  pod: { icon: '📦', label: 'Proof of Delivery', color: '#DC2626' },
};

// ─── COMPONENT ──────────────────────────────────────────────────────────────
const ClientPortal: React.FC<ClientPortalProps> = ({ clientCode }) => {
  const [client, setClient] = useState<ClientInfo | null>(null);
  const [orders, setOrders] = useState<ClientOrder[]>([]);
  const [documents, setDocuments] = useState<ClientDocument[]>([]);
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeNav, setActiveNav] = useState<'home' | 'calendar' | 'documents' | 'invoices'>('home');
  const [showNewOrder, setShowNewOrder] = useState(false);
  const [selectedOrder, setSelectedOrder] = useState<ClientOrder | null>(null);
  const [selectedInvoice, setSelectedInvoice] = useState<Invoice | null>(null);
  const [showPayModal, setShowPayModal] = useState(false);
  const [calendarMonth, setCalendarMonth] = useState(new Date());
  const [newOrder, setNewOrder] = useState({ type: '', subjectName: '', subjectPhone: '', subjectDOB: '', subjectCDL: '', notes: '', urgent: false });

  useEffect(() => {
    const fetchPortalData = async () => {
      try {
        // Attempt to load from PRISM/NEXUS backend API
        const res = await fetch(`/prism/client-portal/${clientCode}`);
        if (res.ok) {
          const data = await res.json();
          setClient(data.client ? {
            id: data.client.id,
            name: data.client.name,
            code: data.client.code,
            contactName: data.client.contact_name,
            services: data.client.services || [],
            serviceCategory: data.client.service_category || 'drug_testing',
          } : null);
          if (data.orders?.length) setOrders(data.orders);
          if (data.documents?.length) setDocuments(data.documents);
          if (data.invoices?.length) setInvoices(data.invoices);
        } else {
          // Fallback to mock data for development/demo
          if (clientCode === 'ABC-7X9K2' || clientCode === 'demo') {
            setClient(MOCK_CLIENT);
            setOrders(MOCK_ORDERS);
            setDocuments(MOCK_DOCUMENTS);
            setInvoices(MOCK_INVOICES);
          }
        }
      } catch {
        // API not running — use mock data for development
        if (clientCode === 'ABC-7X9K2' || clientCode === 'demo') {
          setClient(MOCK_CLIENT);
          setOrders(MOCK_ORDERS);
          setDocuments(MOCK_DOCUMENTS);
          setInvoices(MOCK_INVOICES);
        }
      }
      setLoading(false);
    };
    fetchPortalData();
  }, [clientCode]);

  const handleSubmitOrder = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      // Submit to PRISM/NEXUS backend — triggers service router
      const res = await fetch(`/prism/client-portal/${clientCode}/orders`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          service_type: newOrder.type,
          subject_name: newOrder.subjectName,
          subject_phone: newOrder.subjectPhone,
          subject_dob: newOrder.subjectDOB,
          subject_cdl: newOrder.subjectCDL,
          notes: newOrder.notes,
          urgent: newOrder.urgent,
        }),
      });
      if (res.ok) {
        const data = await res.json();
        const order: ClientOrder = {
          id: data.order?.id || `ORD-2026-${String(Math.floor(Math.random() * 9000) + 1000)}`,
          type: newOrder.type, subject: newOrder.subjectName, status: 'pending',
          notes: newOrder.notes, createdAt: new Date().toISOString().split('T')[0],
        };
        setOrders([order, ...orders]);
      } else {
        // Fallback: add locally anyway (offline/demo mode)
        const order: ClientOrder = { id: `ORD-2026-${String(Math.floor(Math.random() * 9000) + 1000)}`, type: newOrder.type, subject: newOrder.subjectName, status: 'pending', notes: newOrder.notes, createdAt: new Date().toISOString().split('T')[0] };
        setOrders([order, ...orders]);
      }
    } catch {
      // API not running — local fallback
      const order: ClientOrder = { id: `ORD-2026-${String(Math.floor(Math.random() * 9000) + 1000)}`, type: newOrder.type, subject: newOrder.subjectName, status: 'pending', notes: newOrder.notes, createdAt: new Date().toISOString().split('T')[0] };
      setOrders([order, ...orders]);
    }
    setShowNewOrder(false);
    setNewOrder({ type: '', subjectName: '', subjectPhone: '', subjectDOB: '', subjectCDL: '', notes: '', urgent: false });
  };

  const activeOrders = orders.filter(o => ['pending', 'scheduled', 'in_progress'].includes(o.status));
  const completedOrders = orders.filter(o => o.status === 'completed');
  const pendingInvoices = invoices.filter(i => i.status !== 'paid');
  const totalOwed = pendingInvoices.reduce((sum, i) => sum + i.amount, 0);
  const newResults = documents.filter(d => d.type === 'result' && d.status === 'ready').length;

  // Calendar helpers
  const getDaysInMonth = (date: Date) => new Date(date.getFullYear(), date.getMonth() + 1, 0).getDate();
  const getFirstDayOfMonth = (date: Date) => new Date(date.getFullYear(), date.getMonth(), 1).getDay();
  const getCalendarEvents = (): CalendarEvent[] => {
    return orders.filter(o => o.scheduledDate && ['scheduled', 'in_progress', 'completed'].includes(o.status)).map(o => ({
      id: o.id, date: o.scheduledDate!, time: o.scheduledTime || '', title: o.subject,
      subtitle: SERVICE_TYPES[o.type]?.short || o.type, type: o.type,
      color: SERVICE_TYPES[o.type]?.color || '#6B7280', orderId: o.id,
    }));
  };

  if (loading) {
    return (
      <div style={{ minHeight: '100vh', background: '#FAFAFA', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{ width: 48, height: 48, borderRadius: '50%', border: '3px solid #F97316', borderTopColor: 'transparent', margin: '0 auto 16px', animation: 'spin 1s linear infinite' }} />
          <p style={{ color: '#6B7280', fontSize: 14 }}>Loading your portal...</p>
        </div>
        <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
      </div>
    );
  }

  if (!client) {
    return (
      <div style={{ minHeight: '100vh', background: '#FAFAFA', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 24 }}>
        <div style={{ textAlign: 'center', maxWidth: 400 }}>
          <div style={{ width: 80, height: 80, borderRadius: 20, background: '#FEF2F2', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 24px' }}>
            <svg width="36" height="36" fill="none" viewBox="0 0 24 24" stroke="#DC2626" strokeWidth="1.5"><path strokeLinecap="round" strokeLinejoin="round" d="M16.5 10.5V6.75a4.5 4.5 0 10-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 002.25-2.25v-6.75a2.25 2.25 0 00-2.25-2.25H6.75a2.25 2.25 0 00-2.25 2.25v6.75a2.25 2.25 0 002.25 2.25z" /></svg>
          </div>
          <h1 style={{ fontSize: 24, fontWeight: 700, color: '#111827', marginBottom: 8 }}>Link Expired or Invalid</h1>
          <p style={{ color: '#6B7280', marginBottom: 32 }}>Contact your account manager for a new link.</p>
          <a href="mailto:info@deedavis.biz" style={{ padding: '14px 28px', background: '#111827', color: '#fff', borderRadius: 12, fontWeight: 600, fontSize: 14, textDecoration: 'none' }}>Contact Dee Davis Inc.</a>
        </div>
      </div>
    );
  }

  const navItems = [
    { id: 'home', label: 'Home', icon: <svg width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="1.5"><path strokeLinecap="round" strokeLinejoin="round" d="M2.25 12l8.954-8.955c.44-.439 1.152-.439 1.591 0L21.75 12M4.5 9.75v10.125c0 .621.504 1.125 1.125 1.125H9.75v-4.875c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125V21h4.125c.621 0 1.125-.504 1.125-1.125V9.75M8.25 21h8.25" /></svg> },
    { id: 'calendar', label: 'Calendar', icon: <svg width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="1.5"><path strokeLinecap="round" strokeLinejoin="round" d="M6.75 3v2.25M17.25 3v2.25M3 18.75V7.5a2.25 2.25 0 012.25-2.25h13.5A2.25 2.25 0 0121 7.5v11.25m-18 0A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75m-18 0v-7.5A2.25 2.25 0 015.25 9h13.5A2.25 2.25 0 0121 11.25v7.5" /></svg> },
    { id: 'documents', label: 'Documents', icon: <svg width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="1.5"><path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" /></svg>, badge: newResults },
    { id: 'invoices', label: 'Invoices', icon: <svg width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="1.5"><path strokeLinecap="round" strokeLinejoin="round" d="M2.25 8.25h19.5M2.25 9h19.5m-16.5 5.25h6m-6 2.25h3m-3.75 3h15a2.25 2.25 0 002.25-2.25V6.75A2.25 2.25 0 0019.5 4.5h-15a2.25 2.25 0 00-2.25 2.25v10.5A2.25 2.25 0 004.5 19.5z" /></svg>, badge: pendingInvoices.length },
  ];

  return (
    <div style={{ minHeight: '100vh', background: '#FAFAFA', fontFamily: '-apple-system, BlinkMacSystemFont, "Inter", "Segoe UI", sans-serif', display: 'flex' }}>
      
      {/* ─── SIDEBAR NAV ─── */}
      <aside style={{ width: 260, background: '#FFFFFF', borderRight: '1px solid #E5E7EB', position: 'fixed', top: 0, left: 0, bottom: 0, display: 'flex', flexDirection: 'column', zIndex: 40 }}>
        {/* Brand */}
        <div style={{ padding: '28px 24px', borderBottom: '1px solid #F3F4F6' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 16 }}>
            <div style={{ width: 36, height: 36, borderRadius: 10, background: 'linear-gradient(135deg, #F97316, #EA580C)', display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: '0 2px 8px rgba(249,115,22,0.3)' }}>
              <span style={{ color: '#fff', fontWeight: 800, fontSize: 11 }}>DDI</span>
            </div>
            <div>
              <p style={{ fontSize: 13, fontWeight: 700, color: '#111827' }}>Dee Davis Inc.</p>
              <p style={{ fontSize: 11, color: '#9CA3AF' }}>Client Portal</p>
            </div>
          </div>
          <div style={{ background: '#F9FAFB', borderRadius: 12, padding: '12px 14px' }}>
            <p style={{ fontSize: 11, fontWeight: 600, color: '#6B7280', marginBottom: 2 }}>Account</p>
            <p style={{ fontSize: 14, fontWeight: 700, color: '#111827' }}>{client.name}</p>
          </div>
        </div>

        {/* Nav */}
        <nav style={{ flex: 1, padding: '16px 12px' }}>
          {navItems.map(item => (
            <button
              key={item.id}
              onClick={() => setActiveNav(item.id as any)}
              style={{ width: '100%', display: 'flex', alignItems: 'center', gap: 12, padding: '12px 14px', borderRadius: 10, border: 'none', cursor: 'pointer', marginBottom: 4, fontSize: 14, fontWeight: activeNav === item.id ? 600 : 500, background: activeNav === item.id ? '#FFF7ED' : 'transparent', color: activeNav === item.id ? '#EA580C' : '#6B7280', transition: 'all 0.15s', textAlign: 'left' }}
            >
              {item.icon}
              <span style={{ flex: 1 }}>{item.label}</span>
              {item.badge && item.badge > 0 && (
                <span style={{ padding: '2px 8px', borderRadius: 10, fontSize: 11, fontWeight: 700, background: '#FEF3C7', color: '#92400E' }}>{item.badge}</span>
              )}
            </button>
          ))}
        </nav>

        {/* New Request Button */}
        <div style={{ padding: '16px 12px', borderTop: '1px solid #F3F4F6' }}>
          <button
            onClick={() => setShowNewOrder(true)}
            style={{ width: '100%', padding: '14px 16px', background: 'linear-gradient(135deg, #F97316, #EA580C)', color: '#fff', borderRadius: 12, fontWeight: 700, fontSize: 14, border: 'none', cursor: 'pointer', boxShadow: '0 4px 12px rgba(249,115,22,0.25)', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8 }}
          >
            <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2.5"><path strokeLinecap="round" strokeLinejoin="round" d="M12 4.5v15m7.5-7.5h-15" /></svg>
            New Request
          </button>
        </div>

        {/* Footer */}
        <div style={{ padding: '16px 24px', borderTop: '1px solid #F3F4F6' }}>
          <p style={{ fontSize: 11, color: '#9CA3AF' }}>Need help?</p>
          <p style={{ fontSize: 12, color: '#6B7280', fontWeight: 500 }}>(248) 376-4550</p>
          <p style={{ fontSize: 11, color: '#9CA3AF' }}>info@deedavis.biz</p>
        </div>
      </aside>

      {/* ─── MAIN CONTENT ─── */}
      <main style={{ marginLeft: 260, flex: 1, minHeight: '100vh' }}>

        {/* ═══ HOME ═══ */}
        {activeNav === 'home' && (
          <div style={{ padding: '40px 48px', maxWidth: 960 }}>
            {/* Welcome */}
            <div style={{ marginBottom: 40 }}>
              <p style={{ fontSize: 14, color: '#9CA3AF', marginBottom: 4 }}>Welcome back,</p>
              <h1 style={{ fontSize: 28, fontWeight: 800, color: '#111827', letterSpacing: -0.5 }}>{client.contactName}</h1>
            </div>

            {/* Alert Cards */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 16, marginBottom: 40 }}>
              <div style={{ background: '#fff', border: '1px solid #E5E7EB', borderRadius: 16, padding: 24, borderLeft: '4px solid #2563EB' }}>
                <p style={{ fontSize: 32, fontWeight: 800, color: '#2563EB' }}>{activeOrders.length}</p>
                <p style={{ fontSize: 13, color: '#6B7280', marginTop: 4 }}>Active Orders</p>
              </div>
              <div onClick={() => setActiveNav('documents')} style={{ background: '#fff', border: '1px solid #E5E7EB', borderRadius: 16, padding: 24, borderLeft: '4px solid #059669', cursor: 'pointer' }}>
                <p style={{ fontSize: 32, fontWeight: 800, color: '#059669' }}>{newResults}</p>
                <p style={{ fontSize: 13, color: '#6B7280', marginTop: 4 }}>Results Ready</p>
              </div>
              <div onClick={() => setActiveNav('invoices')} style={{ background: totalOwed > 0 ? '#FFF7ED' : '#fff', border: `1px solid ${totalOwed > 0 ? '#FED7AA' : '#E5E7EB'}`, borderRadius: 16, padding: 24, borderLeft: `4px solid ${totalOwed > 0 ? '#F97316' : '#D1D5DB'}`, cursor: 'pointer' }}>
                <p style={{ fontSize: 32, fontWeight: 800, color: totalOwed > 0 ? '#F97316' : '#111827' }}>${totalOwed.toFixed(0)}</p>
                <p style={{ fontSize: 13, color: '#6B7280', marginTop: 4 }}>Balance Due</p>
              </div>
            </div>

            {/* Up Next */}
            <div style={{ marginBottom: 40 }}>
              <h2 style={{ fontSize: 16, fontWeight: 700, color: '#111827', marginBottom: 16 }}>Coming Up</h2>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                {activeOrders.filter(o => o.scheduledDate).slice(0, 4).map(order => {
                  const svc = SERVICE_TYPES[order.type] || { label: order.type, color: '#6B7280', short: '?' };
                  return (
                    <div key={order.id} onClick={() => setSelectedOrder(order)} style={{ background: '#fff', border: '1px solid #E5E7EB', borderRadius: 14, padding: '18px 22px', display: 'flex', alignItems: 'center', gap: 16, cursor: 'pointer', transition: 'box-shadow 0.2s' }} onMouseEnter={e => (e.currentTarget.style.boxShadow = '0 4px 16px rgba(0,0,0,0.06)')} onMouseLeave={e => (e.currentTarget.style.boxShadow = 'none')}>
                      <div style={{ width: 44, height: 44, borderRadius: 12, background: svc.color + '10', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                        <div style={{ width: 10, height: 10, borderRadius: '50%', background: svc.color }} />
                      </div>
                      <div style={{ flex: 1 }}>
                        <p style={{ fontWeight: 600, color: '#111827', fontSize: 14 }}>{order.subject}</p>
                        <p style={{ fontSize: 12, color: '#9CA3AF', marginTop: 2 }}>{svc.label} {order.location && `\u2022 ${order.location}`}</p>
                      </div>
                      <div style={{ textAlign: 'right', flexShrink: 0 }}>
                        <p style={{ fontWeight: 700, fontSize: 14, color: '#111827' }}>{order.scheduledDate}</p>
                        <p style={{ fontSize: 12, color: '#6B7280' }}>{order.scheduledTime}</p>
                      </div>
                    </div>
                  );
                })}
                {activeOrders.filter(o => o.status === 'pending').length > 0 && (
                  <div style={{ background: '#FFFBEB', border: '1px solid #FDE68A', borderRadius: 14, padding: '16px 22px', display: 'flex', alignItems: 'center', gap: 12 }}>
                    <svg width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="#D97706" strokeWidth="1.5"><path strokeLinecap="round" strokeLinejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                    <p style={{ fontSize: 13, color: '#92400E', fontWeight: 500 }}>{activeOrders.filter(o => o.status === 'pending').length} request{activeOrders.filter(o => o.status === 'pending').length > 1 ? 's' : ''} being scheduled by your DDI team</p>
                  </div>
                )}
                {activeOrders.length === 0 && (
                  <div style={{ background: '#fff', border: '1px solid #E5E7EB', borderRadius: 14, padding: 40, textAlign: 'center' }}>
                    <p style={{ color: '#9CA3AF' }}>No upcoming appointments</p>
                    <button onClick={() => setShowNewOrder(true)} style={{ marginTop: 12, padding: '10px 20px', background: '#F3F4F6', border: 'none', borderRadius: 8, fontSize: 13, fontWeight: 600, color: '#374151', cursor: 'pointer' }}>Submit a Request</button>
                  </div>
                )}
              </div>
            </div>

            {/* Recent Results */}
            {completedOrders.slice(0, 3).length > 0 && (
              <div>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16 }}>
                  <h2 style={{ fontSize: 16, fontWeight: 700, color: '#111827' }}>Recent Results</h2>
                  <button onClick={() => setActiveNav('documents')} style={{ fontSize: 13, fontWeight: 600, color: '#F97316', background: 'none', border: 'none', cursor: 'pointer' }}>View All &rarr;</button>
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 12 }}>
                  {completedOrders.slice(0, 3).map(order => (
                    <div key={order.id} style={{ background: '#fff', border: '1px solid #E5E7EB', borderRadius: 14, padding: 20 }}>
                      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 12 }}>
                        <span style={{ fontSize: 11, color: '#9CA3AF', fontFamily: 'monospace' }}>{order.scheduledDate}</span>
                        <span style={{ padding: '3px 8px', borderRadius: 6, fontSize: 11, fontWeight: 700, background: order.result === 'Negative' ? '#ECFDF5' : '#FEF2F2', color: order.result === 'Negative' ? '#065F46' : '#991B1B' }}>{order.result}</span>
                      </div>
                      <p style={{ fontWeight: 600, color: '#111827', fontSize: 14, marginBottom: 4 }}>{order.subject}</p>
                      <p style={{ fontSize: 12, color: '#6B7280', marginBottom: 14 }}>{SERVICE_TYPES[order.type]?.label}</p>
                      {order.resultFileUrl && (
                        <a href={order.resultFileUrl} style={{ display: 'inline-flex', alignItems: 'center', gap: 6, fontSize: 12, fontWeight: 600, color: '#F97316', textDecoration: 'none' }}>
                          <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2"><path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5M16.5 12L12 16.5m0 0L7.5 12m4.5 4.5V3" /></svg>
                          Download
                        </a>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* ═══ CALENDAR ═══ */}
        {activeNav === 'calendar' && (() => {
          const events = getCalendarEvents();
          const daysInMonth = getDaysInMonth(calendarMonth);
          const firstDay = getFirstDayOfMonth(calendarMonth);
          const monthStr = calendarMonth.toLocaleString('default', { month: 'long', year: 'numeric' });
          const days = Array.from({ length: daysInMonth }, (_, i) => i + 1);
          const blanks = Array.from({ length: firstDay }, (_, i) => i);

          return (
            <div style={{ padding: '40px 48px', maxWidth: 960 }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 32 }}>
                <h1 style={{ fontSize: 24, fontWeight: 800, color: '#111827' }}>Calendar</h1>
                <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                  <button onClick={() => setCalendarMonth(new Date(calendarMonth.getFullYear(), calendarMonth.getMonth() - 1))} style={{ width: 36, height: 36, borderRadius: 10, border: '1px solid #E5E7EB', background: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer' }}>
                    <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="#374151" strokeWidth="2"><path strokeLinecap="round" strokeLinejoin="round" d="M15.75 19.5L8.25 12l7.5-7.5" /></svg>
                  </button>
                  <span style={{ fontSize: 16, fontWeight: 700, color: '#111827', minWidth: 160, textAlign: 'center' }}>{monthStr}</span>
                  <button onClick={() => setCalendarMonth(new Date(calendarMonth.getFullYear(), calendarMonth.getMonth() + 1))} style={{ width: 36, height: 36, borderRadius: 10, border: '1px solid #E5E7EB', background: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer' }}>
                    <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="#374151" strokeWidth="2"><path strokeLinecap="round" strokeLinejoin="round" d="M8.25 4.5l7.5 7.5-7.5 7.5" /></svg>
                  </button>
                </div>
              </div>

              {/* Calendar Grid */}
              <div style={{ background: '#fff', border: '1px solid #E5E7EB', borderRadius: 20, overflow: 'hidden' }}>
                {/* Day headers */}
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)', borderBottom: '1px solid #F3F4F6' }}>
                  {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(d => (
                    <div key={d} style={{ padding: '14px 8px', textAlign: 'center', fontSize: 12, fontWeight: 600, color: '#9CA3AF', textTransform: 'uppercase', letterSpacing: 0.5 }}>{d}</div>
                  ))}
                </div>
                {/* Days */}
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)' }}>
                  {blanks.map(i => <div key={`b-${i}`} style={{ minHeight: 100, borderBottom: '1px solid #F3F4F6', borderRight: '1px solid #F3F4F6' }} />)}
                  {days.map(day => {
                    const dateStr = `${calendarMonth.getFullYear()}-${String(calendarMonth.getMonth() + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
                    const dayEvents = events.filter(e => e.date === dateStr);
                    const isToday = dateStr === new Date().toISOString().split('T')[0];
                    return (
                      <div key={day} style={{ minHeight: 100, padding: 8, borderBottom: '1px solid #F3F4F6', borderRight: '1px solid #F3F4F6', background: isToday ? '#FFF7ED' : undefined }}>
                        <p style={{ fontSize: 13, fontWeight: isToday ? 700 : 400, color: isToday ? '#F97316' : '#374151', marginBottom: 4 }}>{day}</p>
                        {dayEvents.map(evt => (
                          <div key={evt.id} style={{ padding: '4px 8px', borderRadius: 6, background: evt.color + '15', borderLeft: `3px solid ${evt.color}`, marginBottom: 4, cursor: 'pointer', fontSize: 11 }} onClick={() => { const o = orders.find(x => x.id === evt.orderId); if (o) setSelectedOrder(o); }}>
                            <p style={{ fontWeight: 600, color: '#111827', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{evt.title}</p>
                            <p style={{ color: '#6B7280', fontSize: 10 }}>{evt.time} &middot; {evt.subtitle}</p>
                          </div>
                        ))}
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          );
        })()}

        {/* ═══ DOCUMENTS ═══ */}
        {activeNav === 'documents' && (
          <div style={{ padding: '40px 48px', maxWidth: 960 }}>
            <h1 style={{ fontSize: 24, fontWeight: 800, color: '#111827', marginBottom: 8 }}>Documents</h1>
            <p style={{ fontSize: 14, color: '#6B7280', marginBottom: 32 }}>All your results, reports, and certificates in one place.</p>

            <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
              {documents.map(doc => {
                const meta = DOC_TYPE_META[doc.type] || { icon: '📄', label: doc.type, color: '#6B7280' };
                return (
                  <div key={doc.id} style={{ background: '#fff', border: '1px solid #E5E7EB', borderRadius: 14, padding: '18px 22px', display: 'flex', alignItems: 'center', gap: 16 }}>
                    <div style={{ width: 44, height: 44, borderRadius: 12, background: meta.color + '12', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 20, flexShrink: 0 }}>
                      {meta.icon}
                    </div>
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <p style={{ fontWeight: 600, color: '#111827', fontSize: 14 }}>{doc.name}</p>
                      <p style={{ fontSize: 12, color: '#9CA3AF', marginTop: 2 }}>{meta.label} &middot; {doc.date}</p>
                    </div>
                    <a href={doc.downloadUrl} download style={{ display: 'flex', alignItems: 'center', gap: 6, padding: '10px 16px', background: '#F9FAFB', border: '1px solid #E5E7EB', borderRadius: 10, fontSize: 13, fontWeight: 600, color: '#374151', textDecoration: 'none', flexShrink: 0, cursor: 'pointer' }}>
                      <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2"><path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5M16.5 12L12 16.5m0 0L7.5 12m4.5 4.5V3" /></svg>
                      Download
                    </a>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* ═══ INVOICES ═══ */}
        {activeNav === 'invoices' && (
          <div style={{ padding: '40px 48px', maxWidth: 960 }}>
            <h1 style={{ fontSize: 24, fontWeight: 800, color: '#111827', marginBottom: 8 }}>Invoices & Billing</h1>
            <p style={{ fontSize: 14, color: '#6B7280', marginBottom: 32 }}>View and pay your invoices online.</p>

            {totalOwed > 0 && (
              <div style={{ background: 'linear-gradient(135deg, #FFF7ED, #FFFBEB)', border: '1px solid #FED7AA', borderRadius: 16, padding: 24, marginBottom: 24, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <div>
                  <p style={{ fontSize: 14, fontWeight: 600, color: '#92400E' }}>Outstanding Balance</p>
                  <p style={{ fontSize: 28, fontWeight: 800, color: '#EA580C' }}>${totalOwed.toFixed(2)}</p>
                </div>
                <button onClick={() => { setSelectedInvoice(pendingInvoices[0]); setShowPayModal(true); }} style={{ padding: '14px 28px', background: 'linear-gradient(135deg, #F97316, #EA580C)', color: '#fff', borderRadius: 12, fontWeight: 700, fontSize: 14, border: 'none', cursor: 'pointer', boxShadow: '0 4px 12px rgba(249,115,22,0.3)' }}>
                  Pay Now
                </button>
              </div>
            )}

            <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
              {invoices.map(inv => (
                <div key={inv.id} style={{ background: '#fff', border: '1px solid #E5E7EB', borderRadius: 14, padding: '18px 22px', display: 'flex', alignItems: 'center', gap: 16 }}>
                  <div style={{ width: 44, height: 44, borderRadius: 12, display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0, background: inv.status === 'paid' ? '#ECFDF5' : '#FFFBEB' }}>
                    <svg width="20" height="20" fill="none" viewBox="0 0 24 24" stroke={inv.status === 'paid' ? '#059669' : '#D97706'} strokeWidth="1.5"><path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" /></svg>
                  </div>
                  <div style={{ flex: 1 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                      <p style={{ fontWeight: 600, fontSize: 14, color: '#111827', fontFamily: 'monospace' }}>{inv.id}</p>
                      <span style={{ padding: '2px 8px', borderRadius: 6, fontSize: 11, fontWeight: 700, background: inv.status === 'paid' ? '#ECFDF5' : '#FFFBEB', color: inv.status === 'paid' ? '#065F46' : '#92400E' }}>{inv.status.toUpperCase()}</span>
                    </div>
                    <p style={{ fontSize: 12, color: '#9CA3AF', marginTop: 4 }}>{inv.status === 'paid' ? `Paid ${inv.paidDate}` : `Due ${inv.dueDate}`} &middot; {inv.orderIds.length} order{inv.orderIds.length > 1 ? 's' : ''}</p>
                  </div>
                  <p style={{ fontSize: 20, fontWeight: 800, color: '#111827', flexShrink: 0 }}>${inv.amount.toFixed(2)}</p>
                  <div style={{ display: 'flex', gap: 8, flexShrink: 0 }}>
                    <a href={inv.pdfUrl || '#'} style={{ padding: '10px 14px', borderRadius: 10, border: '1px solid #E5E7EB', fontSize: 12, fontWeight: 600, color: '#374151', textDecoration: 'none', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 4 }}>
                      <svg width="12" height="12" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2"><path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5M16.5 12L12 16.5m0 0L7.5 12m4.5 4.5V3" /></svg>
                      PDF
                    </a>
                    {inv.status !== 'paid' && (
                      <button onClick={() => { setSelectedInvoice(inv); setShowPayModal(true); }} style={{ padding: '10px 18px', borderRadius: 10, border: 'none', fontSize: 12, fontWeight: 700, background: '#F97316', color: '#fff', cursor: 'pointer' }}>Pay</button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </main>

      {/* ─── ORDER DETAIL MODAL ─── */}
      {selectedOrder && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.4)', backdropFilter: 'blur(4px)', zIndex: 50, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 16 }} onClick={() => setSelectedOrder(null)}>
          <div style={{ background: '#fff', borderRadius: 24, width: '100%', maxWidth: 480, boxShadow: '0 25px 50px rgba(0,0,0,0.12)' }} onClick={e => e.stopPropagation()}>
            <div style={{ padding: '28px 32px', borderBottom: '1px solid #F3F4F6', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
              <div>
                <p style={{ fontSize: 11, color: '#9CA3AF', fontFamily: 'monospace' }}>{selectedOrder.id}</p>
                <h2 style={{ fontSize: 20, fontWeight: 700, color: '#111827', marginTop: 4 }}>{selectedOrder.subject}</h2>
                <p style={{ fontSize: 13, color: '#6B7280', marginTop: 2 }}>{SERVICE_TYPES[selectedOrder.type]?.label}</p>
              </div>
              <button onClick={() => setSelectedOrder(null)} style={{ width: 32, height: 32, borderRadius: 8, border: '1px solid #E5E7EB', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer', background: '#fff' }}>
                <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="#6B7280" strokeWidth="2"><path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" /></svg>
              </button>
            </div>
            <div style={{ padding: '24px 32px', display: 'flex', flexDirection: 'column', gap: 16 }}>
              {selectedOrder.scheduledDate && (
                <div style={{ background: '#F9FAFB', borderRadius: 12, padding: 18 }}>
                  <p style={{ fontSize: 11, fontWeight: 600, color: '#9CA3AF', textTransform: 'uppercase', letterSpacing: 0.5, marginBottom: 6 }}>Appointment</p>
                  <p style={{ fontWeight: 700, color: '#111827' }}>{selectedOrder.scheduledDate} at {selectedOrder.scheduledTime}</p>
                  {selectedOrder.location && <p style={{ fontSize: 13, color: '#6B7280', marginTop: 4 }}>{selectedOrder.location}</p>}
                </div>
              )}
              {selectedOrder.result && (
                <div style={{ background: selectedOrder.result === 'Negative' ? '#ECFDF5' : '#FEF2F2', borderRadius: 12, padding: 18, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <div>
                    <p style={{ fontSize: 11, fontWeight: 600, color: '#9CA3AF', textTransform: 'uppercase', letterSpacing: 0.5, marginBottom: 4 }}>Result</p>
                    <p style={{ fontWeight: 800, fontSize: 18, color: selectedOrder.result === 'Negative' ? '#065F46' : '#991B1B' }}>{selectedOrder.result}</p>
                  </div>
                  {selectedOrder.resultFileUrl && <a href={selectedOrder.resultFileUrl} download style={{ padding: '10px 16px', background: '#fff', border: '1px solid #E5E7EB', borderRadius: 10, fontSize: 12, fontWeight: 600, color: '#374151', textDecoration: 'none' }}>Download</a>}
                </div>
              )}
              {selectedOrder.notes && (
                <div><p style={{ fontSize: 11, fontWeight: 600, color: '#9CA3AF', marginBottom: 4 }}>NOTES</p><p style={{ fontSize: 13, color: '#374151' }}>{selectedOrder.notes}</p></div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* ─── PAY MODAL ─── */}
      {showPayModal && selectedInvoice && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)', backdropFilter: 'blur(6px)', zIndex: 60, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 16 }} onClick={() => setShowPayModal(false)}>
          <div style={{ background: '#fff', borderRadius: 24, width: '100%', maxWidth: 400, boxShadow: '0 25px 50px rgba(0,0,0,0.2)' }} onClick={e => e.stopPropagation()}>
            <div style={{ padding: 32, textAlign: 'center' }}>
              <div style={{ width: 56, height: 56, borderRadius: 14, background: 'linear-gradient(135deg, #F97316, #EA580C)', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 20px', boxShadow: '0 8px 20px rgba(249,115,22,0.3)' }}>
                <svg width="24" height="24" fill="none" viewBox="0 0 24 24" stroke="#fff" strokeWidth="1.5"><path strokeLinecap="round" strokeLinejoin="round" d="M2.25 8.25h19.5M2.25 9h19.5m-16.5 5.25h6m-6 2.25h3m-3.75 3h15a2.25 2.25 0 002.25-2.25V6.75A2.25 2.25 0 0019.5 4.5h-15a2.25 2.25 0 00-2.25 2.25v10.5A2.25 2.25 0 004.5 19.5z" /></svg>
              </div>
              <p style={{ fontSize: 13, color: '#6B7280' }}>Amount Due</p>
              <p style={{ fontSize: 36, fontWeight: 800, color: '#111827', letterSpacing: -1, margin: '4px 0 4px' }}>${selectedInvoice.amount.toFixed(2)}</p>
              <p style={{ fontSize: 12, color: '#9CA3AF', fontFamily: 'monospace' }}>{selectedInvoice.id}</p>
            </div>
            <div style={{ padding: '0 32px 32px', display: 'flex', flexDirection: 'column', gap: 10 }}>
              <button onClick={() => { alert(`Stripe checkout: $${selectedInvoice.amount.toFixed(2)}`); setShowPayModal(false); setSelectedInvoice(null); }} style={{ width: '100%', padding: 18, borderRadius: 14, border: 'none', fontWeight: 700, fontSize: 15, background: 'linear-gradient(135deg, #F97316, #EA580C)', color: '#fff', cursor: 'pointer', boxShadow: '0 4px 16px rgba(249,115,22,0.3)' }}>
                Pay with Card
              </button>
              <button disabled style={{ width: '100%', padding: 16, borderRadius: 14, border: '1.5px solid #E5E7EB', fontWeight: 600, fontSize: 14, background: '#fff', color: '#9CA3AF', cursor: 'not-allowed' }}>
                ACH Bank Transfer (Coming Soon)
              </button>
              <p style={{ textAlign: 'center', fontSize: 11, color: '#9CA3AF', marginTop: 8 }}>
                Secured by Stripe. Card info never stored on our servers.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* ─── NEW REQUEST MODAL ─── */}
      {showNewOrder && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.4)', backdropFilter: 'blur(4px)', zIndex: 50, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 16 }} onClick={() => setShowNewOrder(false)}>
          <div style={{ background: '#fff', borderRadius: 24, width: '100%', maxWidth: 520, maxHeight: '90vh', overflow: 'auto', boxShadow: '0 25px 50px rgba(0,0,0,0.15)' }} onClick={e => e.stopPropagation()}>
            <div style={{ padding: '28px 32px', borderBottom: '1px solid #F3F4F6', position: 'sticky', top: 0, background: '#fff', borderRadius: '24px 24px 0 0', zIndex: 10, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <h2 style={{ fontSize: 20, fontWeight: 700, color: '#111827' }}>New Service Request</h2>
              <button onClick={() => setShowNewOrder(false)} style={{ width: 32, height: 32, borderRadius: 8, border: '1px solid #E5E7EB', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer', background: '#fff' }}>
                <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="#6B7280" strokeWidth="2"><path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" /></svg>
              </button>
            </div>
            <form onSubmit={handleSubmitOrder} style={{ padding: '28px 32px', display: 'flex', flexDirection: 'column', gap: 20 }}>
              <div>
                <label style={{ display: 'block', fontSize: 13, fontWeight: 600, color: '#374151', marginBottom: 10 }}>Service Type *</label>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8 }}>
                  {client.services.map(svc => {
                    const service = SERVICE_TYPES[svc];
                    if (!service) return null;
                    const selected = newOrder.type === svc;
                    return (
                      <button key={svc} type="button" onClick={() => setNewOrder({ ...newOrder, type: svc })} style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '12px 14px', borderRadius: 12, border: selected ? `2px solid ${service.color}` : '1.5px solid #E5E7EB', background: selected ? service.color + '08' : '#fff', cursor: 'pointer', textAlign: 'left', fontSize: 13, fontWeight: selected ? 600 : 400, color: '#374151' }}>
                        <div style={{ width: 10, height: 10, borderRadius: '50%', background: service.color, flexShrink: 0 }} />
                        {service.label}
                      </button>
                    );
                  })}
                </div>
              </div>
              <div>
                <label style={{ display: 'block', fontSize: 12, fontWeight: 600, color: '#6B7280', marginBottom: 6 }}>Employee / Subject Name *</label>
                <input type="text" required value={newOrder.subjectName} onChange={e => setNewOrder({ ...newOrder, subjectName: e.target.value })} placeholder="Full name" style={{ width: '100%', padding: '12px 14px', borderRadius: 10, border: '1.5px solid #E5E7EB', fontSize: 14, outline: 'none', boxSizing: 'border-box' }} />
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
                <div><label style={{ display: 'block', fontSize: 12, fontWeight: 600, color: '#6B7280', marginBottom: 6 }}>Phone</label><input type="tel" value={newOrder.subjectPhone} onChange={e => setNewOrder({ ...newOrder, subjectPhone: e.target.value })} placeholder="(555) 555-5555" style={{ width: '100%', padding: '12px 14px', borderRadius: 10, border: '1.5px solid #E5E7EB', fontSize: 14, outline: 'none', boxSizing: 'border-box' }} /></div>
                <div><label style={{ display: 'block', fontSize: 12, fontWeight: 600, color: '#6B7280', marginBottom: 6 }}>CDL #</label><input type="text" value={newOrder.subjectCDL} onChange={e => setNewOrder({ ...newOrder, subjectCDL: e.target.value })} placeholder="License #" style={{ width: '100%', padding: '12px 14px', borderRadius: 10, border: '1.5px solid #E5E7EB', fontSize: 14, outline: 'none', boxSizing: 'border-box' }} /></div>
              </div>
              <div><label style={{ display: 'block', fontSize: 12, fontWeight: 600, color: '#6B7280', marginBottom: 6 }}>Notes</label><textarea value={newOrder.notes} onChange={e => setNewOrder({ ...newOrder, notes: e.target.value })} placeholder="Special instructions..." style={{ width: '100%', padding: '12px 14px', borderRadius: 10, border: '1.5px solid #E5E7EB', fontSize: 14, outline: 'none', height: 80, resize: 'none', boxSizing: 'border-box' }} /></div>
              <label style={{ display: 'flex', alignItems: 'center', gap: 12, padding: 14, background: '#FEF2F2', border: '1px solid #FECACA', borderRadius: 12, cursor: 'pointer' }}>
                <input type="checkbox" checked={newOrder.urgent} onChange={e => setNewOrder({ ...newOrder, urgent: e.target.checked })} style={{ width: 18, height: 18, accentColor: '#DC2626' }} />
                <div><p style={{ fontWeight: 600, color: '#991B1B', fontSize: 13 }}>Urgent / Post-Accident</p><p style={{ fontSize: 11, color: '#B91C1C' }}>Within 8 hours</p></div>
              </label>
              <button type="submit" disabled={!newOrder.type || !newOrder.subjectName} style={{ padding: '16px', borderRadius: 14, border: 'none', fontWeight: 700, fontSize: 15, cursor: 'pointer', background: (!newOrder.type || !newOrder.subjectName) ? '#E5E7EB' : 'linear-gradient(135deg, #F97316, #EA580C)', color: (!newOrder.type || !newOrder.subjectName) ? '#9CA3AF' : '#fff', boxShadow: (!newOrder.type || !newOrder.subjectName) ? 'none' : '0 4px 16px rgba(249,115,22,0.3)' }}>
                Submit Request
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default ClientPortal;
