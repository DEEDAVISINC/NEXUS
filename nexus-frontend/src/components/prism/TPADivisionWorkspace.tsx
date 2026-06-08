import React, { useEffect, useState } from 'react';
import { api } from '../../api/client';
import PrismAgentDirectory from './PrismAgentDirectory';
import PrismVoiceCallCenter from './PrismVoiceCallCenter';
import PrismOpsFeed, { PrismNotification } from './PrismOpsFeed';
import { countDivisionAgents, PrismAgentRecord } from './prismAgentNetwork';

// ─── TYPES ─────────────────────────────────────────────────────────
interface Client {
  id: string;
  name: string;
  contactName: string;
  contactEmail: string;
  contactPhone: string;
  portalLink: string;
  contractType: 'monthly' | 'per-test' | 'annual';
  activeOrders: number;
  totalOrders: number;
  status: 'active' | 'inactive' | 'pending';
  createdAt: string;
}

interface Order {
  id: string;
  clientId: string;
  clientName: string;
  type: string; // 'dot', 'non-dot', 'random', 'pre-employment', etc.
  subject: string; // person being tested/served
  subjectInfo: {
    name: string;
    dob?: string;
    ssn4?: string;
    cdl?: string;
    phone?: string;
    email?: string;
  };
  status: 'pending' | 'scheduled' | 'in_progress' | 'completed' | 'cancelled';
  scheduledDate?: string;
  scheduledTime?: string;
  location?: string;
  assignedAgent?: string;
  confirmationNumber?: string;
  notes: string;
  attachments: { name: string; url: string; type: 'screenshot' | 'document' | 'result' }[];
  createdAt: string;
  updatedAt: string;
  /** Linked NEMT pipeline order (HAP / MCO trips) */
  nemtOrderId?: string;
  vertexInvoiceId?: string;
  /** Guest ride tracking link — shown on client portal dashboard */
  rideTrackingUrl?: string;
}

interface CapturedDoc {
  id: string;
  orderId?: string;
  filename: string;
  url: string;
  type: 'screenshot' | 'pdf' | 'excel';
  extractedData?: Record<string, string>;
  uploadedAt: string;
  matched: boolean;
}

/** Map NEXUS `/prism/orders` API row → workspace order card */
export function mapPrismApiOrderToWorkspace(o: Record<string, unknown>): Order {
  const statusRaw = String(o.status || 'New').toLowerCase();
  let status: Order['status'] = 'pending';
  if (['complete', 'completed', 'verified', 'closed'].some((s) => statusRaw.includes(s))) {
    status = 'completed';
  } else if (['en route', 'arrived', 'in progress', 'departed'].some((s) => statusRaw.includes(s))) {
    status = 'in_progress';
  } else if (['agent assigned', 'confirmed', 'scheduled'].some((s) => statusRaw.includes(s))) {
    status = 'scheduled';
  } else if (statusRaw.includes('cancel')) {
    status = 'cancelled';
  } else if (statusRaw === 'new' || statusRaw.includes('order received')) {
    status = 'pending';
  }

  const time = String(o.time || '');
  const tz = String(o.timezone || '');
  const details =
    o.details && typeof o.details === 'object' && !Array.isArray(o.details)
      ? (o.details as Record<string, unknown>)
      : {};

  return {
    id: String(o.id || ''),
    clientId: String(o.client_email || o.client || 'unknown'),
    clientName: String(o.client || '—'),
    type: String(o.type || o.service_key || '—'),
    subject: String(o.service_label || o.workflow_stage_label || o.type || 'Order'),
    subjectInfo: {
      name: String(o.signer || '—'),
      phone: o.subject_phone ? String(o.subject_phone) : undefined,
      email: o.subject_email ? String(o.subject_email) : o.client_email ? String(o.client_email) : undefined,
      dob: o.subject_dob ? String(o.subject_dob) : undefined,
    },
    status,
    scheduledDate: o.date ? String(o.date) : undefined,
    scheduledTime: [time, tz].filter(Boolean).join(' ') || undefined,
    location: String(o.collection_site || o.address || ''),
    assignedAgent: o.agent ? String(o.agent) : undefined,
    confirmationNumber: String(o.id || ''),
    notes: String(o.notes || ''),
    attachments: [],
    createdAt: String(o.created_at || ''),
    updatedAt: String(o.updated_at || o.created_at || ''),
    nemtOrderId: details.nemt_order_id ? String(details.nemt_order_id) : undefined,
    vertexInvoiceId: details.vertex_invoice_id ? String(details.vertex_invoice_id) : undefined,
    rideTrackingUrl: details.ride_tracking_url ? String(details.ride_tracking_url) : undefined,
  };
}

interface TPADivisionWorkspaceProps {
  division: {
    id: string;
    name: string;
    icon: string;
    color: string;
    solid: string;
    serviceTypes: { id: string; label: string }[];
    partnerPortals: { id: string; name: string; url: string; icon: string }[];
  };
  /** Live orders from GET /prism/orders (division-filtered by parent) */
  orders?: Order[];
  ordersLoading?: boolean;
  onRefreshOrders?: () => void;
  /** Nationwide field agent network from GET /prism/agents */
  agents?: PrismAgentRecord[];
  agentsLoading?: boolean;
  agentSpecialtyLabels?: string[];
  onAssignAgent?: (orderId: string, agent: PrismAgentRecord) => void | Promise<void>;
  opsNotifications?: PrismNotification[];
  opsUnreadCount?: number;
  opsFeedOpen?: boolean;
  onToggleOpsFeed?: () => void;
  onMarkOpsRead?: (id: string) => void;
  onMarkAllOpsRead?: () => void;
  onOpsNotificationClick?: (n: PrismNotification) => void;
  onOpenPortal: (portal: { id: string; name: string; url: string; icon: string }) => void;
  onBack: () => void;
}

// ─── MOCK DATA (Replace with API calls) ────────────────────────────
const MOCK_CLIENTS: Client[] = [
  {
    id: 'c1',
    name: 'ABC Trucking Co.',
    contactName: 'Mike Johnson',
    contactEmail: 'mike@abctrucking.com',
    contactPhone: '555-123-4567',
    portalLink: 'ABC-7X9K2',
    contractType: 'monthly',
    activeOrders: 3,
    totalOrders: 47,
    status: 'active',
    createdAt: '2026-01-15',
  },
  {
    id: 'c2',
    name: 'Metro Transit Authority',
    contactName: 'Sarah Williams',
    contactEmail: 'swilliams@metrotransit.gov',
    contactPhone: '555-987-6543',
    portalLink: 'MTA-3K7P9',
    contractType: 'annual',
    activeOrders: 12,
    totalOrders: 234,
    status: 'active',
    createdAt: '2025-06-01',
  },
  {
    id: 'c3',
    name: 'Midwest Logistics LLC',
    contactName: 'Tom Richards',
    contactEmail: 'tom@midwestlog.com',
    contactPhone: '555-456-7890',
    portalLink: 'MWL-8N2X5',
    contractType: 'per-test',
    activeOrders: 0,
    totalOrders: 15,
    status: 'inactive',
    createdAt: '2026-03-20',
  },
];

const MOCK_ORDERS: Order[] = [
  {
    id: 'o1',
    clientId: 'c1',
    clientName: 'ABC Trucking Co.',
    type: 'dot',
    subject: 'Pre-Employment',
    subjectInfo: { name: 'James Wilson', dob: '1985-03-15', cdl: 'D1234567', phone: '555-111-2222' },
    status: 'scheduled',
    scheduledDate: '2026-05-19',
    scheduledTime: '10:00 AM',
    location: 'Quest - Troy, MI',
    assignedAgent: 'Mobile Unit 1',
    notes: 'New driver hire, needs DOT physical same day',
    attachments: [],
    createdAt: '2026-05-17T10:30:00Z',
    updatedAt: '2026-05-17T14:00:00Z',
  },
  {
    id: 'o2',
    clientId: 'c2',
    clientName: 'Metro Transit Authority',
    type: 'random',
    subject: 'Random Selection',
    subjectInfo: { name: 'Patricia Moore', dob: '1978-11-22', cdl: 'M9876543', phone: '555-333-4444' },
    status: 'pending',
    notes: 'From Q2 random pool selection',
    attachments: [],
    createdAt: '2026-05-18T08:00:00Z',
    updatedAt: '2026-05-18T08:00:00Z',
  },
  {
    id: 'o3',
    clientId: 'c1',
    clientName: 'ABC Trucking Co.',
    type: 'post-accident',
    subject: 'Post-Accident',
    subjectInfo: { name: 'Robert Chen', dob: '1990-07-04', cdl: 'D7654321', phone: '555-555-6666' },
    status: 'in_progress',
    scheduledDate: '2026-05-18',
    scheduledTime: '2:30 PM',
    location: 'On-site - ABC Trucking Yard',
    assignedAgent: 'Sarah M.',
    confirmationNumber: 'CH-2026-05-18-001',
    notes: 'Minor fender bender, no injuries. Alcohol test also required within 8 hrs.',
    attachments: [{ name: 'incident_report.pdf', url: '#', type: 'document' }],
    createdAt: '2026-05-18T11:00:00Z',
    updatedAt: '2026-05-18T14:30:00Z',
  },
];

// ─── COMPONENT ─────────────────────────────────────────────────────
const TPADivisionWorkspace: React.FC<TPADivisionWorkspaceProps> = ({
  division,
  orders: ordersProp,
  ordersLoading = false,
  onRefreshOrders,
  agents: agentsProp = [],
  agentsLoading = false,
  agentSpecialtyLabels = [],
  onAssignAgent,
  opsNotifications = [],
  opsUnreadCount = 0,
  opsFeedOpen = false,
  onToggleOpsFeed,
  onMarkOpsRead,
  onMarkAllOpsRead,
  onOpsNotificationClick,
  onOpenPortal,
  onBack,
}) => {
  const [activeSection, setActiveSection] = useState<'dashboard' | 'clients' | 'orders' | 'agents' | 'scanbacks' | 'analytics' | 'payments' | 'capture' | 'voice'>('dashboard');
  const [showAgentPicker, setShowAgentPicker] = useState(false);
  const [assigningOrder, setAssigningOrder] = useState(false);
  const [selectedClient, setSelectedClient] = useState<Client | null>(null);
  const [selectedOrder, setSelectedOrder] = useState<Order | null>(null);
  const [orderFilter, setOrderFilter] = useState<'all' | 'pending' | 'scheduled' | 'in_progress' | 'completed'>('all');
  const [showNewOrderModal, setShowNewOrderModal] = useState(false);
  const [showNewClientModal, setShowNewClientModal] = useState(false);
  const [dragOver, setDragOver] = useState(false);
  const [capturedDocs, setCapturedDocs] = useState<CapturedDoc[]>([]);
  const [nemtBusy, setNemtBusy] = useState<string | null>(null);
  const [nemtMsg, setNemtMsg] = useState<{ ok: boolean; text: string } | null>(null);
  const [rideTrackingInput, setRideTrackingInput] = useState('');

  const isNemtDivision = division.id === 'transport';

  const inferTrackingPlatform = (url: string): 'uber_health' | 'lyft_healthcare' => {
    try {
      const host = new URL(url.trim()).hostname.toLowerCase();
      if (host === 'trip.uber.com') return 'uber_health';
      return 'lyft_healthcare';
    } catch {
      return 'uber_health';
    }
  };

  useEffect(() => {
    setRideTrackingInput(selectedOrder?.rideTrackingUrl || '');
  }, [selectedOrder?.id, selectedOrder?.rideTrackingUrl]);

  /** Real API orders when parent passes them; mock only when prop omitted (dev) */
  const displayOrders = ordersProp !== undefined ? ordersProp : MOCK_ORDERS;

  const filteredOrders = orderFilter === 'all'
    ? displayOrders
    : displayOrders.filter((o) => o.status === orderFilter);

  const divisionTypes = division.serviceTypes.map((s) => s.id);

  const divisionAgentCount = countDivisionAgents(agentsProp, divisionTypes, agentSpecialtyLabels);

  const stats = {
    pending: displayOrders.filter((o) => o.status === 'pending').length,
    scheduled: displayOrders.filter((o) => o.status === 'scheduled').length,
    inProgress: displayOrders.filter((o) => o.status === 'in_progress').length,
    completedToday: displayOrders.filter((o) => o.status === 'completed').length,
    activeClients: MOCK_CLIENTS.filter((c) => c.status === 'active').length,
    unassigned: displayOrders.filter((o) => !o.assignedAgent && o.status !== 'completed' && o.status !== 'cancelled').length,
  };

  const handleAssignFromPicker = async (agent: PrismAgentRecord) => {
    if (!selectedOrder || !onAssignAgent) return;
    setAssigningOrder(true);
    try {
      await onAssignAgent(selectedOrder.id, agent);
      setSelectedOrder({ ...selectedOrder, assignedAgent: agent.name, status: 'scheduled' });
      setShowAgentPicker(false);
      onRefreshOrders?.();
    } finally {
      setAssigningOrder(false);
    }
  };

  const resolveNemtOrderId = async (): Promise<string | null> => {
    if (!selectedOrder) return null;
    if (selectedOrder.nemtOrderId) return selectedOrder.nemtOrderId;
    try {
      const res = await api.getNemtOrderByPrism(selectedOrder.id);
      if (res?.order_id) {
        const nemtId = String(res.order_id);
        setSelectedOrder({ ...selectedOrder, nemtOrderId: nemtId });
        return nemtId;
      }
    } catch {
      /* lookup failed */
    }
    return null;
  };

  const handleNemtVerify = async () => {
    if (!selectedOrder) return;
    setNemtBusy('verify');
    setNemtMsg(null);
    try {
      const nemtId = await resolveNemtOrderId();
      if (!nemtId) {
        setNemtMsg({ ok: false, text: 'No NEMT order linked to this intake. Run voice simulate or create NEMT order first.' });
        return;
      }
      const res = await api.verifyNemtEligibility(nemtId);
      if (res?.error) {
        setNemtMsg({ ok: false, text: String(res.error) });
        return;
      }
      const passed = res.checklist?.eligible_to_dispatch;
      setNemtMsg({
        ok: !!passed,
        text: passed
          ? 'Eligibility verified — ready to dispatch.'
          : `Eligibility incomplete (${res.checklist?.failed_count ?? '?'} checks failed).`,
      });
    } catch (e) {
      setNemtMsg({ ok: false, text: e instanceof Error ? e.message : 'Verify failed' });
    } finally {
      setNemtBusy(null);
    }
  };

  const handleNemtDispatch = async () => {
    if (!selectedOrder) return;
    setNemtBusy('dispatch');
    setNemtMsg(null);
    try {
      const nemtId = await resolveNemtOrderId();
      if (!nemtId) {
        setNemtMsg({ ok: false, text: 'No NEMT order linked to this intake.' });
        return;
      }
      await api.verifyNemtEligibility(nemtId);
      const trackingUrl = rideTrackingInput.trim();
      const res = await api.dispatchNemtOrder(nemtId, {
        member_phone: selectedOrder.subjectInfo.phone || undefined,
        ...(trackingUrl
          ? {
              rider_tracking_url: trackingUrl,
              fulfillment_platform: inferTrackingPlatform(trackingUrl),
            }
          : {}),
      });
      if (res?.error) {
        setNemtMsg({ ok: false, text: String(res.error) });
        return;
      }
      setSelectedOrder({ ...selectedOrder, status: 'in_progress' });
      setNemtMsg({ ok: true, text: 'Trip dispatched. Fulfillment platform notified or queued for manual dispatch.' });
      onRefreshOrders?.();
    } catch (e) {
      setNemtMsg({ ok: false, text: e instanceof Error ? e.message : 'Dispatch failed' });
    } finally {
      setNemtBusy(null);
    }
  };

  const handleSaveRideTracking = async () => {
    if (!selectedOrder) return;
    const url = rideTrackingInput.trim();
    if (!url) {
      setNemtMsg({ ok: false, text: 'Paste the guest trip tracking link from your dispatch dashboard.' });
      return;
    }
    setNemtBusy('tracking');
    setNemtMsg(null);
    try {
      const nemtId = await resolveNemtOrderId();
      if (!nemtId) {
        setNemtMsg({ ok: false, text: 'No NEMT order linked to this intake.' });
        return;
      }
      const res = await api.setNemtRideTracking(nemtId, {
        rider_tracking_url: url,
        fulfillment_platform: inferTrackingPlatform(url),
      });
      if (res?.error) {
        setNemtMsg({ ok: false, text: String(res.error) });
        return;
      }
      const saved = String(res.ride_tracking_url || url);
      setSelectedOrder({ ...selectedOrder, status: 'in_progress', rideTrackingUrl: saved });
      setNemtMsg({ ok: true, text: 'Tracking link saved — visible on client portal dashboard.' });
      onRefreshOrders?.();
    } catch (e) {
      setNemtMsg({ ok: false, text: e instanceof Error ? e.message : 'Could not save tracking link' });
    } finally {
      setNemtBusy(null);
    }
  };

  const handleNemtComplete = async () => {
    if (!selectedOrder) return;
    setNemtBusy('complete');
    setNemtMsg(null);
    try {
      const nemtId = await resolveNemtOrderId();
      if (!nemtId) {
        setNemtMsg({ ok: false, text: 'No NEMT order linked to this intake.' });
        return;
      }
      let nemt = await api.getNemtOrderByPrism(selectedOrder.id);
      if (nemt?.error) {
        setNemtMsg({ ok: false, text: String(nemt.error) });
        return;
      }
      const status = String(nemt.status || '');
      if (status === 'scheduled') {
        await api.verifyNemtEligibility(nemtId);
        const disp = await api.dispatchNemtOrder(nemtId, {
          member_phone: selectedOrder.subjectInfo.phone || undefined,
        });
        if (disp?.error) {
          setNemtMsg({ ok: false, text: String(disp.error) });
          return;
        }
      }
      const now = new Date().toISOString();
      const res = await api.completeNemtTrip(nemtId, {
        actual_pickup_time: now,
        actual_dropoff_time: now,
        actual_mileage: 0,
        auto_generate_claim: true,
        member_phone: selectedOrder.subjectInfo.phone || undefined,
      });
      if (res?.error) {
        setNemtMsg({ ok: false, text: String(res.error) });
        return;
      }
      const invId =
        res.order?.vertex_invoice_id ||
        res.claim?.invoice?.id ||
        res.claim?.invoice_id;
      setSelectedOrder({
        ...selectedOrder,
        status: 'completed',
        vertexInvoiceId: invId ? String(invId) : selectedOrder.vertexInvoiceId,
        nemtOrderId: nemtId,
      });
      setNemtMsg({
        ok: true,
        text: invId
          ? `Trip complete — VERTEX invoice generated (${invId}). Check Payments tab.`
          : 'Trip complete — claim logged. Check Payments if invoice ID is pending.',
      });
      onRefreshOrders?.();
    } catch (e) {
      setNemtMsg({ ok: false, text: e instanceof Error ? e.message : 'Complete failed' });
    } finally {
      setNemtBusy(null);
    }
  };

  // Handle file drop for capture
  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const files = Array.from(e.dataTransfer.files);
    files.forEach(file => {
      const newDoc: CapturedDoc = {
        id: `doc-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        filename: file.name,
        url: URL.createObjectURL(file),
        type: file.type.includes('pdf') ? 'pdf' : file.type.includes('sheet') ? 'excel' : 'screenshot',
        uploadedAt: new Date().toISOString(),
        matched: false,
      };
      setCapturedDocs(prev => [newDoc, ...prev]);
    });
  };

  // Status style helper — inline, no dynamic Tailwind
  const statusStyle = (status: string): React.CSSProperties => {
    const map: Record<string, React.CSSProperties> = {
      pending:     { background: 'rgba(234,179,8,0.12)',   color: '#FCD34D' },
      scheduled:   { background: 'rgba(59,130,246,0.12)',  color: '#93C5FD' },
      in_progress: { background: 'rgba(139,92,246,0.15)', color: '#C4B5FD' },
      completed:   { background: 'rgba(16,185,129,0.12)', color: '#6EE7B7' },
      cancelled:   { background: 'rgba(107,114,128,0.15)', color: '#9CA3AF' },
    };
    return { ...(map[status] || map.scheduled), padding: '3px 9px', borderRadius: 6, fontSize: 10, fontWeight: 700, letterSpacing: 0.3 };
  };

  // Divisions that show scanbacks (results/documents to review)
  const SCANBACK_DIVISIONS = ['notary_legal', 'drug_testing', 'dna'];
  const showScanbacks = SCANBACK_DIVISIONS.includes(division.id);
  const showVoiceIntake = division.id === 'transport';

  // Nav items config — filtered by division
  const NAV_ITEMS = [
    { id: 'dashboard', label: 'Dashboard',  icon: (
      <svg width="15" height="15" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="1.8"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></svg>
    )},
    { id: 'clients',   label: 'Clients',    badge: stats.activeClients, icon: (
      <svg width="15" height="15" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="1.8"><path strokeLinecap="round" strokeLinejoin="round" d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/><circle cx="9" cy="7" r="4"/><path strokeLinecap="round" strokeLinejoin="round" d="M23 21v-2a4 4 0 00-3-3.87M16 3.13a4 4 0 010 7.75"/></svg>
    )},
    { id: 'orders',    label: 'Orders',     badge: stats.pending + stats.scheduled + stats.inProgress, icon: (
      <svg width="15" height="15" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="1.8"><path strokeLinecap="round" strokeLinejoin="round" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/></svg>
    )},
    ...(showVoiceIntake ? [{ id: 'voice', label: 'Voice Intake', icon: (
      <svg width="15" height="15" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="1.8"><path strokeLinecap="round" strokeLinejoin="round" d="M12 18.75a6 6 0 006-6v-1.5m-6 7.5a6 6 0 01-6-6v-1.5m6 7.5v3.75m-3.75 0h7.5M12 15.75a3 3 0 01-3-3V4.5a3 3 0 116 0v8.25a3 3 0 01-3 3z"/></svg>
    )}] : []),
    { id: 'agents',    label: 'Agent Network', badge: divisionAgentCount || undefined, icon: (
      <svg width="15" height="15" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="1.8"><circle cx="12" cy="8" r="4"/><path strokeLinecap="round" strokeLinejoin="round" d="M4 20c0-4 3.6-7 8-7s8 3 8 7"/></svg>
    )},
    // Scanbacks only for notary, drug testing, DNA
    ...(showScanbacks ? [{ id: 'scanbacks', label: 'Scanbacks',  badge: 2, icon: (
      <svg width="15" height="15" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="1.8"><path strokeLinecap="round" strokeLinejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>
    )}] : []),
    { id: 'analytics', label: 'Analytics',  icon: (
      <svg width="15" height="15" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="1.8"><path strokeLinecap="round" strokeLinejoin="round" d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z"/></svg>
    )},
    { id: 'payments',  label: 'Payments',   icon: (
      <svg width="15" height="15" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="1.8"><rect x="1" y="4" width="22" height="16" rx="2" ry="2"/><line x1="1" y1="10" x2="23" y2="10"/></svg>
    )},
    { id: 'capture',   label: 'Capture',    badge: capturedDocs.filter(d => !d.matched).length || undefined, icon: (
      <svg width="15" height="15" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="1.8"><path strokeLinecap="round" strokeLinejoin="round" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"/><circle cx="12" cy="13" r="3"/></svg>
    )},
  ];

  return (
    <div style={{ display: 'flex', height: '100%', fontFamily: '-apple-system, BlinkMacSystemFont, "Inter", sans-serif', background: '#0D0D12' }}>

      {/* ─── SIDEBAR ─── */}
      <div style={{ width: 220, background: '#0A0A0F', borderRight: '1px solid rgba(255,255,255,0.06)', display: 'flex', flexDirection: 'column', flexShrink: 0 }}>

        {/* Division header */}
        <div style={{ padding: '16px 14px', borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
          <button
            onClick={onBack}
            style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 12, color: 'rgba(156,163,175,0.6)', background: 'none', border: 'none', cursor: 'pointer', marginBottom: 14, padding: 0 }}
          >
            <svg width="12" height="12" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2"><path strokeLinecap="round" strokeLinejoin="round" d="M15.75 19.5L8.25 12l7.5-7.5"/></svg>
            Back to Hub
          </button>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <span style={{ fontSize: 22 }}>{division.icon}</span>
            <div>
              <p style={{ fontWeight: 700, fontSize: 13, color: '#F9FAFB' }}>{division.name}</p>
              <p style={{ fontSize: 10, color: 'rgba(107,114,128,0.7)', marginTop: 1 }}>TPA Division</p>
            </div>
          </div>
        </div>

        {/* Nav */}
        <nav style={{ flex: 1, padding: '10px 8px', overflowY: 'auto' }}>
          {NAV_ITEMS.map(item => {
            const active = activeSection === item.id;
            return (
              <button
                key={item.id}
                onClick={() => { setActiveSection(item.id as any); setSelectedClient(null); setSelectedOrder(null); }}
                style={{ width: '100%', display: 'flex', alignItems: 'center', gap: 10, padding: '9px 12px', borderRadius: 8, border: 'none', cursor: 'pointer', marginBottom: 2, background: active ? 'rgba(249,115,22,0.12)' : 'transparent', color: active ? '#FB923C' : 'rgba(156,163,175,0.7)', textAlign: 'left' as const, transition: 'all 0.12s', fontSize: 13, fontWeight: active ? 600 : 400 }}
                onMouseEnter={e => { if (!active) { e.currentTarget.style.background = 'rgba(255,255,255,0.04)'; e.currentTarget.style.color = '#E5E7EB'; }}}
                onMouseLeave={e => { if (!active) { e.currentTarget.style.background = 'transparent'; e.currentTarget.style.color = 'rgba(156,163,175,0.7)'; }}}
              >
                {item.icon}
                <span style={{ flex: 1 }}>{item.label}</span>
                {item.badge !== undefined && item.badge > 0 && (
                  <span style={{ padding: '1px 6px', borderRadius: 5, fontSize: 10, fontWeight: 700, background: active ? 'rgba(251,146,60,0.2)' : 'rgba(255,255,255,0.08)', color: active ? '#FB923C' : '#9CA3AF' }}>{item.badge}</span>
                )}
              </button>
            );
          })}
        </nav>

        {/* Partner portals */}
        <div style={{ padding: '10px 8px', borderTop: '1px solid rgba(255,255,255,0.06)' }}>
          <p style={{ fontSize: 10, fontWeight: 600, color: 'rgba(107,114,128,0.6)', textTransform: 'uppercase', letterSpacing: 0.8, padding: '4px 12px', marginBottom: 4 }}>Live Portals</p>
          {division.partnerPortals.slice(0, 4).map(portal => (
            <button
              key={portal.id}
              onClick={() => onOpenPortal(portal)}
              style={{ width: '100%', display: 'flex', alignItems: 'center', gap: 8, padding: '8px 12px', borderRadius: 7, border: 'none', cursor: 'pointer', fontSize: 12, color: 'rgba(156,163,175,0.7)', background: 'transparent', textAlign: 'left' as const, transition: 'all 0.12s' }}
              onMouseEnter={e => { e.currentTarget.style.background = 'rgba(255,255,255,0.04)'; e.currentTarget.style.color = '#E5E7EB'; }}
              onMouseLeave={e => { e.currentTarget.style.background = 'transparent'; e.currentTarget.style.color = 'rgba(156,163,175,0.7)'; }}
            >
              <span>{portal.icon}</span>
              <span style={{ flex: 1, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{portal.name}</span>
              <span style={{ width: 6, height: 6, borderRadius: '50%', background: '#10B981', flexShrink: 0 }} />
            </button>
          ))}
        </div>
      </div>

      {/* ─── MAIN CONTENT ─── */}
      <div className="flex-1 overflow-y-auto" style={{ background: '#0D0D12' }}>
        {/* ═══ DASHBOARD ═══ */}
        {activeSection === 'dashboard' && (
          <div>
            {/* Header bar */}
            <div style={{ padding: '20px 28px', borderBottom: '1px solid rgba(255,255,255,0.05)', display: 'flex', alignItems: 'center', justifyContent: 'space-between', background: '#0D0D12' }}>
              <div>
                <h1 style={{ fontSize: 18, fontWeight: 700, color: '#F9FAFB', letterSpacing: -0.3 }}>{division.name}</h1>
                <p style={{ fontSize: 12, color: 'rgba(107,114,128,0.7)', marginTop: 2 }}>Division Command Center</p>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                {onToggleOpsFeed && onMarkOpsRead && onMarkAllOpsRead && (
                  <PrismOpsFeed
                    notifications={opsNotifications}
                    unreadCount={opsUnreadCount}
                    open={opsFeedOpen}
                    onToggle={onToggleOpsFeed}
                    onMarkRead={onMarkOpsRead}
                    onMarkAllRead={onMarkAllOpsRead}
                    onSelectNotification={onOpsNotificationClick}
                    accent={division.solid}
                  />
                )}
                <button
                  type="button"
                  onClick={() => setShowNewOrderModal(true)}
                  style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '9px 18px', background: '#F97316', color: '#fff', borderRadius: 9, fontWeight: 600, fontSize: 13, border: 'none', cursor: 'pointer' }}
                >
                  + New Order
                </button>
              </div>
            </div>

            {/* KPI ribbon */}
            <div style={{ display: 'flex', borderBottom: '1px solid rgba(255,255,255,0.05)', background: '#0A0A0F' }}>
              {[
                { label: 'Pending',         value: stats.pending,        color: '#FCD34D' },
                { label: 'Scheduled',       value: stats.scheduled,      color: '#93C5FD' },
                { label: 'In Progress',     value: stats.inProgress,     color: '#C4B5FD' },
                { label: 'Completed Today', value: stats.completedToday, color: '#6EE7B7' },
                { label: 'Active Clients',  value: stats.activeClients,  color: '#9CA3AF' },
              ].map((s, i) => (
                <div key={s.label} style={{ flex: 1, padding: '14px 20px', borderRight: i < 4 ? '1px solid rgba(255,255,255,0.05)' : 'none' }}>
                  <p style={{ fontSize: 22, fontWeight: 800, color: s.color, letterSpacing: -0.5 }}>{s.value}</p>
                  <p style={{ fontSize: 11, color: 'rgba(107,114,128,0.7)', marginTop: 2 }}>{s.label}</p>
                </div>
              ))}
            </div>

            <div style={{ padding: 28 }}>
            {showVoiceIntake && opsNotifications.length > 0 && (
              <div style={{ background: '#14141A', border: '1px solid rgba(20,184,166,0.2)', borderRadius: 14, padding: 20, marginBottom: 24 }}>
                <p style={{ fontSize: 11, fontWeight: 600, color: '#5EEAD4', textTransform: 'uppercase', letterSpacing: 0.8, marginBottom: 14 }}>
                  Live Ops — Voice &amp; Intake
                </p>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                  {opsNotifications.slice(0, 5).map((n) => (
                    <button
                      key={n.id}
                      type="button"
                      onClick={() => {
                        onMarkOpsRead?.(n.id);
                        onOpsNotificationClick?.(n);
                      }}
                      style={{ textAlign: 'left', padding: '10px 12px', background: '#0D0D12', borderRadius: 8, border: '1px solid rgba(255,255,255,0.06)', cursor: 'pointer' }}
                    >
                      <p style={{ fontSize: 13, fontWeight: 600, color: '#F9FAFB' }}>{n.icon ? `${n.icon} ` : ''}{n.title}</p>
                      <p style={{ fontSize: 11, color: 'rgba(156,163,175,0.85)', marginTop: 2 }}>{n.message}</p>
                    </button>
                  ))}
                </div>
              </div>
            )}
            {/* Today's Schedule */}
            <div style={{ background: '#14141A', border: '1px solid rgba(255,255,255,0.06)', borderRadius: 14, padding: 20, marginBottom: 24 }}>
              <p style={{ fontSize: 11, fontWeight: 600, color: 'rgba(156,163,175,0.7)', textTransform: 'uppercase', letterSpacing: 0.8, marginBottom: 14 }}>Today's Schedule</p>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                {displayOrders.filter(o => o.status === 'scheduled' || o.status === 'in_progress').map(order => (
                  <div
                    key={order.id}
                    onClick={() => { setActiveSection('orders'); setSelectedOrder(order); }}
                    style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '12px 16px', background: '#0D0D12', borderRadius: 10, border: '1px solid rgba(255,255,255,0.05)', cursor: 'pointer' }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                      <span style={{ ...statusStyle(order.status), flexShrink: 0 }}>
                        {order.scheduledTime || 'TBD'}
                      </span>
                      <div>
                        <p style={{ fontWeight: 600, fontSize: 14, color: '#F9FAFB' }}>{order.subjectInfo.name}</p>
                        <p style={{ fontSize: 12, color: 'rgba(107,114,128,0.8)', marginTop: 2 }}>{order.clientName} &nbsp;·&nbsp; {order.type.toUpperCase()}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-xs text-gray-400">{order.location}</p>
                      {order.assignedAgent && <p className="text-xs text-gray-500">{order.assignedAgent}</p>}
                    </div>
                  </div>
                ))}
                {displayOrders.filter(o => o.status === 'scheduled' || o.status === 'in_progress').length === 0 && (
                  <p className="text-gray-500 text-sm text-center py-4">No scheduled orders today</p>
                )}
              </div>
            </div>

            {/* Needs Attention */}
            {displayOrders.filter(o => o.status === 'pending').length > 0 && (
              <div style={{ background: 'rgba(234,179,8,0.05)', border: '1px solid rgba(234,179,8,0.15)', borderRadius: 14, padding: 20, marginBottom: 24 }}>
                <p style={{ fontSize: 11, fontWeight: 600, color: '#FCD34D', textTransform: 'uppercase', letterSpacing: 0.8, marginBottom: 14 }}>Needs Attention</p>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                  {displayOrders.filter(o => o.status === 'pending').map(order => (
                    <div
                      key={order.id}
                      onClick={() => { setActiveSection('orders'); setSelectedOrder(order); }}
                      style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '12px 16px', background: 'rgba(234,179,8,0.05)', borderRadius: 9, cursor: 'pointer', border: '1px solid rgba(234,179,8,0.1)' }}
                    >
                      <div>
                        <p style={{ fontWeight: 600, fontSize: 14, color: '#F9FAFB' }}>{order.subjectInfo.name}</p>
                        <p style={{ fontSize: 12, color: 'rgba(107,114,128,0.8)', marginTop: 2 }}>{order.clientName} &nbsp;·&nbsp; {order.type.toUpperCase()}</p>
                      </div>
                      <span style={{ fontSize: 11, fontWeight: 700, color: '#FCD34D' }}>NEEDS SCHEDULING →</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
            </div>{/* end padding wrapper */}
          </div>
        )}

        {/* ═══ CLIENTS (CRM) ═══ */}
        {activeSection === 'clients' && !selectedClient && (
          <div>
            <div style={{ padding: '20px 28px', borderBottom: '1px solid rgba(255,255,255,0.05)', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div>
                <h1 style={{ fontSize: 18, fontWeight: 700, color: '#F9FAFB' }}>Clients</h1>
                <p style={{ fontSize: 12, color: 'rgba(107,114,128,0.7)', marginTop: 2 }}>{MOCK_CLIENTS.length} accounts</p>
              </div>
              <button
                onClick={() => setShowNewClientModal(true)}
                style={{ padding: '9px 18px', background: '#F97316', color: '#fff', borderRadius: 9, fontWeight: 600, fontSize: 13, border: 'none', cursor: 'pointer' }}
              >
                + Add Client
              </button>
            </div>
            <div style={{ padding: 28, display: 'flex', flexDirection: 'column', gap: 8 }}>
              {MOCK_CLIENTS.map(client => {
                const statusCfg = client.status === 'active'
                  ? { bg: 'rgba(16,185,129,0.12)', color: '#6EE7B7' }
                  : client.status === 'inactive'
                  ? { bg: 'rgba(107,114,128,0.12)', color: '#9CA3AF' }
                  : { bg: 'rgba(234,179,8,0.12)', color: '#FCD34D' };
                return (
                  <button
                    key={client.id}
                    onClick={() => setSelectedClient(client)}
                    style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '16px 20px', background: '#14141A', border: '1px solid rgba(255,255,255,0.06)', borderRadius: 12, cursor: 'pointer', textAlign: 'left' as const, width: '100%' }}
                    onMouseEnter={e => { e.currentTarget.style.background = '#1A1A22'; e.currentTarget.style.borderColor = 'rgba(255,255,255,0.1)'; }}
                    onMouseLeave={e => { e.currentTarget.style.background = '#14141A'; e.currentTarget.style.borderColor = 'rgba(255,255,255,0.06)'; }}
                  >
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 5 }}>
                        <p style={{ fontWeight: 700, fontSize: 15, color: '#F9FAFB' }}>{client.name}</p>
                        <span style={{ ...statusCfg, padding: '2px 8px', borderRadius: 5, fontSize: 10, fontWeight: 700 }}>{client.status.toUpperCase()}</span>
                      </div>
                      <p style={{ fontSize: 12, color: 'rgba(107,114,128,0.8)' }}>{client.contactName} &nbsp;·&nbsp; {client.contactEmail}</p>
                      <p style={{ fontSize: 11, color: 'rgba(107,114,128,0.5)', marginTop: 4 }}>
                        {client.totalOrders} total orders &nbsp;·&nbsp; since {client.createdAt} &nbsp;·&nbsp; portal/{client.portalLink}
                      </p>
                    </div>
                    <div style={{ textAlign: 'right', flexShrink: 0, paddingLeft: 20 }}>
                      <p style={{ fontSize: 22, fontWeight: 800, color: '#F97316' }}>{client.activeOrders}</p>
                      <p style={{ fontSize: 11, color: 'rgba(107,114,128,0.7)', marginTop: 2 }}>active orders</p>
                    </div>
                  </button>
                );
              })}
            </div>
          </div>
        )}

        {/* ═══ CLIENT DETAIL ═══ */}
        {activeSection === 'clients' && selectedClient && (
          <div className="p-6">
            <button onClick={() => setSelectedClient(null)} className="text-gray-400 hover:text-white text-sm mb-4 flex items-center gap-1">
              ← Back to Clients
            </button>

            <div className="bg-gray-800 border border-gray-700 rounded-xl p-6 mb-6">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h1 className="text-xl font-bold">{selectedClient.name}</h1>
                  <p className="text-gray-400">{selectedClient.contactName}</p>
                </div>
                <span className={`px-3 py-1 rounded-lg text-xs font-bold ${
                  selectedClient.status === 'active' ? 'bg-green-500/20 text-green-400' : 'bg-gray-500/20 text-gray-400'
                }`}>
                  {selectedClient.status.toUpperCase()}
                </span>
              </div>

              <div className="grid grid-cols-3 gap-4 mb-4">
                <div>
                  <p className="text-xs text-gray-500">Email</p>
                  <p className="text-sm">{selectedClient.contactEmail}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Phone</p>
                  <p className="text-sm">{selectedClient.contactPhone}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Contract Type</p>
                  <p className="text-sm capitalize">{selectedClient.contractType}</p>
                </div>
              </div>

              <div className="bg-gray-700/50 rounded-lg p-3 flex items-center justify-between">
                <div>
                  <p className="text-xs text-gray-500">Client Portal Link</p>
                  <p className="text-sm font-mono">portal.deedavis.biz/t/{selectedClient.portalLink}</p>
                </div>
                <button className="px-3 py-1.5 bg-gray-600 hover:bg-gray-500 rounded-lg text-xs font-semibold transition">
                  Copy Link
                </button>
              </div>
            </div>

            {/* Client's Orders */}
            <div className="flex items-center justify-between mb-4">
              <h2 className="font-bold">Orders</h2>
              <button
                onClick={() => setShowNewOrderModal(true)}
                className="px-3 py-1.5 rounded-lg font-semibold text-xs text-white transition hover:opacity-90"
                style={{ backgroundColor: division.solid }}
              >
                + New Order for {selectedClient.name}
              </button>
            </div>

            <div className="space-y-2">
              {displayOrders.filter(o => o.clientId === selectedClient.id).map(order => (
                <div
                  key={order.id}
                  onClick={() => { setActiveSection('orders'); setSelectedOrder(order); }}
                  className="bg-gray-800 border border-gray-700 rounded-lg p-3 hover:border-gray-600 cursor-pointer transition"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <span style={statusStyle(order.status)}>
                        {order.status.replace('_', ' ').toUpperCase()}
                      </span>
                      <div>
                        <p className="font-medium text-sm">{order.subjectInfo.name}</p>
                        <p className="text-xs text-gray-400">{order.type.toUpperCase()} • {order.subject}</p>
                      </div>
                    </div>
                    <p className="text-xs text-gray-500">{new Date(order.createdAt).toLocaleDateString()}</p>
                  </div>
                </div>
              ))}
              {displayOrders.filter(o => o.clientId === selectedClient.id).length === 0 && (
                <p className="text-gray-500 text-sm text-center py-8">No orders yet for this client</p>
              )}
            </div>
          </div>
        )}

        {/* ═══ ORDERS ═══ */}
        {activeSection === 'orders' && !selectedOrder && (
          <div style={{ padding: 24, color: '#F9FAFB' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 24 }}>
              <h1 style={{ fontSize: 22, fontWeight: 800 }}>Orders</h1>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                {onRefreshOrders && (
                  <button
                    type="button"
                    onClick={onRefreshOrders}
                    disabled={ordersLoading}
                    style={{ padding: '8px 14px', borderRadius: 9, fontSize: 14, fontWeight: 600, color: '#F9FAFB', background: '#374151', border: '1px solid rgba(255,255,255,0.15)', cursor: 'pointer' }}
                  >
                    {ordersLoading ? 'Refreshing…' : '↻ Refresh'}
                  </button>
                )}
                <select
                  value={orderFilter}
                  onChange={(e) => setOrderFilter(e.target.value as typeof orderFilter)}
                  style={{ padding: '8px 14px', borderRadius: 9, fontSize: 14, color: '#F9FAFB', background: '#374151', border: '1px solid rgba(255,255,255,0.15)' }}
                >
                  <option value="all">All Orders</option>
                  <option value="pending">Pending</option>
                  <option value="scheduled">Scheduled</option>
                  <option value="in_progress">In Progress</option>
                  <option value="completed">Completed</option>
                </select>
                <button
                  type="button"
                  onClick={() => setShowNewOrderModal(true)}
                  style={{ padding: '8px 16px', borderRadius: 9, fontWeight: 700, fontSize: 14, color: '#fff', border: 'none', cursor: 'pointer', backgroundColor: division.solid }}
                >
                  + New Order
                </button>
              </div>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
              {ordersLoading && filteredOrders.length === 0 && (
                <p style={{ fontSize: 15, color: '#9CA3AF', textAlign: 'center', padding: '32px 0' }}>Loading orders…</p>
              )}
              {!ordersLoading && filteredOrders.length === 0 && (
                <p style={{ fontSize: 15, color: '#9CA3AF', textAlign: 'center', padding: '32px 0' }}>
                  No orders yet for this division. Client portal submissions appear here automatically.
                </p>
              )}
              {filteredOrders.map((order) => (
                <div
                  key={order.id}
                  role="button"
                  tabIndex={0}
                  onClick={() => setSelectedOrder(order)}
                  onKeyDown={(e) => e.key === 'Enter' && setSelectedOrder(order)}
                  style={{
                    background: '#14141A',
                    border: '1px solid rgba(255,255,255,0.12)',
                    borderRadius: 14,
                    padding: 18,
                    cursor: 'pointer',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 16 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 14, minWidth: 0 }}>
                      <span style={statusStyle(order.status)}>
                        {order.status.replace('_', ' ').toUpperCase()}
                      </span>
                      <div style={{ minWidth: 0 }}>
                        <p style={{ fontSize: 17, fontWeight: 700, color: '#FFFFFF' }}>{order.subjectInfo.name}</p>
                        <p style={{ fontSize: 14, color: '#D1D5DB', marginTop: 2 }}>{order.clientName}</p>
                        <p
                          style={{
                            fontSize: 13,
                            fontFamily: 'ui-monospace, monospace',
                            color: division.solid,
                            marginTop: 6,
                            fontWeight: 700,
                          }}
                        >
                          {order.confirmationNumber || order.id}
                        </p>
                      </div>
                    </div>
                    <div style={{ textAlign: 'right', flexShrink: 0 }}>
                      <p style={{ fontSize: 15, fontWeight: 700, color: '#F9FAFB' }}>{order.type.toUpperCase()}</p>
                      <p style={{ fontSize: 13, color: '#D1D5DB', marginTop: 2 }}>{order.subject}</p>
                    </div>
                  </div>
                  {(order.scheduledDate || order.location) && (
                    <div style={{ marginTop: 12, paddingTop: 12, borderTop: '1px solid rgba(255,255,255,0.08)', display: 'flex', flexWrap: 'wrap', gap: 16, fontSize: 14, color: '#D1D5DB' }}>
                      {order.scheduledDate && <span>📅 {order.scheduledDate} {order.scheduledTime}</span>}
                      {order.location && <span>📍 {order.location}</span>}
                      {order.assignedAgent && <span>👤 {order.assignedAgent}</span>}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* ═══ ORDER DETAIL ═══ */}
        {activeSection === 'orders' && selectedOrder && (
          <div style={{ padding: 24, color: '#F9FAFB' }}>
            <button
              type="button"
              onClick={() => setSelectedOrder(null)}
              style={{ color: '#D1D5DB', fontSize: 14, marginBottom: 16, background: 'none', border: 'none', cursor: 'pointer' }}
            >
              ← Back to Orders
            </button>

            {(selectedOrder.confirmationNumber || selectedOrder.id) && (
              <div
                style={{
                  marginBottom: 20,
                  padding: '18px 22px',
                  borderRadius: 14,
                  background: `linear-gradient(135deg, ${division.solid}22 0%, #14141A 100%)`,
                  border: `2px solid ${division.solid}`,
                  boxShadow: `0 0 24px ${division.solid}33`,
                }}
              >
                <p style={{ fontSize: 11, fontWeight: 700, letterSpacing: 1.2, color: '#E5E7EB', textTransform: 'uppercase', marginBottom: 8 }}>
                  Confirmation ID
                </p>
                <p
                  style={{
                    fontSize: 22,
                    fontWeight: 800,
                    fontFamily: 'ui-monospace, SFMono-Regular, Menlo, monospace',
                    color: '#FFFFFF',
                    letterSpacing: 0.5,
                    wordBreak: 'break-all',
                    lineHeight: 1.35,
                  }}
                >
                  {selectedOrder.confirmationNumber || selectedOrder.id}
                </p>
              </div>
            )}

            <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: 24 }}>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
                <div style={{ background: '#14141A', border: '1px solid rgba(255,255,255,0.12)', borderRadius: 14, padding: 22 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 18 }}>
                    <div>
                      <span style={statusStyle(selectedOrder.status)}>
                        {selectedOrder.status.replace('_', ' ').toUpperCase()}
                      </span>
                      <h1 style={{ fontSize: 24, fontWeight: 800, marginTop: 10, color: '#FFFFFF' }}>{selectedOrder.subjectInfo.name}</h1>
                      <p style={{ fontSize: 15, color: '#D1D5DB', marginTop: 4 }}>{selectedOrder.clientName}</p>
                    </div>
                    <div style={{ textAlign: 'right' }}>
                      <p style={{ fontSize: 18, fontWeight: 800, color: division.solid }}>{selectedOrder.type.toUpperCase()}</p>
                      <p style={{ fontSize: 14, color: '#D1D5DB', marginTop: 4 }}>{selectedOrder.subject}</p>
                    </div>
                  </div>

                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
                    {[
                      { label: 'DOB', value: selectedOrder.subjectInfo.dob || '—' },
                      { label: 'CDL#', value: selectedOrder.subjectInfo.cdl || '—', mono: true },
                      { label: 'Phone', value: selectedOrder.subjectInfo.phone || '—' },
                      { label: 'SSN (last 4)', value: selectedOrder.subjectInfo.ssn4 || '—', mono: true },
                    ].map((field) => (
                      <div key={field.label}>
                        <p style={{ fontSize: 11, fontWeight: 700, color: '#9CA3AF', textTransform: 'uppercase', letterSpacing: 0.6, marginBottom: 4 }}>{field.label}</p>
                        <p style={{ fontSize: 16, fontWeight: 600, color: '#F9FAFB', fontFamily: field.mono ? 'ui-monospace, monospace' : 'inherit' }}>{field.value}</p>
                      </div>
                    ))}
                  </div>
                </div>

                <div style={{ background: '#14141A', border: '1px solid rgba(255,255,255,0.12)', borderRadius: 14, padding: 22 }}>
                  <h3 style={{ fontSize: 16, fontWeight: 700, color: '#FFFFFF', marginBottom: 16 }}>Schedule & Assignment</h3>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
                    {[
                      { label: 'Date', value: selectedOrder.scheduledDate || 'Not scheduled' },
                      { label: 'Time', value: selectedOrder.scheduledTime || '—' },
                      { label: 'Location', value: selectedOrder.location || '—' },
                      { label: 'Assigned To', value: selectedOrder.assignedAgent || 'Unassigned', highlight: !selectedOrder.assignedAgent },
                    ].map((field) => (
                      <div key={field.label}>
                        <p style={{ fontSize: 11, fontWeight: 700, color: '#9CA3AF', textTransform: 'uppercase', letterSpacing: 0.6, marginBottom: 4 }}>{field.label}</p>
                        <p style={{ fontSize: 16, fontWeight: 600, color: field.highlight ? '#FCD34D' : '#F9FAFB' }}>{field.value}</p>
                      </div>
                    ))}
                  </div>
                  {onAssignAgent && (
                    <button
                      type="button"
                      disabled={assigningOrder}
                      onClick={() => setShowAgentPicker(true)}
                      style={{
                        marginTop: 18,
                        width: '100%',
                        padding: '12px 16px',
                        borderRadius: 10,
                        border: 'none',
                        fontWeight: 700,
                        fontSize: 15,
                        color: '#fff',
                        cursor: assigningOrder ? 'wait' : 'pointer',
                        opacity: assigningOrder ? 0.6 : 1,
                        backgroundColor: division.solid,
                      }}
                    >
                      {assigningOrder ? 'Assigning…' : selectedOrder.assignedAgent ? 'Reassign Agent' : 'Assign Agent'}
                    </button>
                  )}
                </div>

                {selectedOrder.notes && (
                  <div style={{ background: '#14141A', border: '1px solid rgba(255,255,255,0.12)', borderRadius: 14, padding: 22 }}>
                    <h3 style={{ fontSize: 16, fontWeight: 700, color: '#FFFFFF', marginBottom: 8 }}>Notes</h3>
                    <p style={{ fontSize: 15, color: '#E5E7EB', lineHeight: 1.5 }}>{selectedOrder.notes}</p>
                  </div>
                )}
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
                <div style={{ background: '#14141A', border: '1px solid rgba(255,255,255,0.12)', borderRadius: 14, padding: 18 }}>
                  <h3 style={{ fontSize: 16, fontWeight: 700, color: '#FFFFFF', marginBottom: 12 }}>Actions</h3>
                  {isNemtDivision ? (
                    <>
                      {selectedOrder.nemtOrderId && (
                        <p style={{ fontSize: 12, color: '#9CA3AF', marginBottom: 10, fontFamily: 'monospace' }}>
                          NEMT: {selectedOrder.nemtOrderId.slice(0, 8)}…
                        </p>
                      )}
                      {selectedOrder.vertexInvoiceId && (
                        <p style={{ fontSize: 12, color: '#34D399', marginBottom: 10 }}>
                          Invoice: {selectedOrder.vertexInvoiceId}
                        </p>
                      )}
                      {nemtMsg && (
                        <p style={{
                          fontSize: 13,
                          marginBottom: 10,
                          padding: '8px 10px',
                          borderRadius: 8,
                          background: nemtMsg.ok ? 'rgba(5,150,105,0.15)' : 'rgba(220,38,38,0.15)',
                          color: nemtMsg.ok ? '#6EE7B7' : '#FCA5A5',
                        }}>
                          {nemtMsg.text}
                        </p>
                      )}
                      <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                        <button
                          type="button"
                          disabled={!!nemtBusy || selectedOrder.status === 'completed'}
                          onClick={handleNemtVerify}
                          style={{ width: '100%', padding: '12px 16px', borderRadius: 10, border: '1px solid rgba(255,255,255,0.15)', fontWeight: 600, fontSize: 14, color: '#F9FAFB', background: '#1F2937', cursor: nemtBusy ? 'wait' : 'pointer', opacity: nemtBusy || selectedOrder.status === 'completed' ? 0.6 : 1 }}
                        >
                          {nemtBusy === 'verify' ? 'Verifying…' : 'Verify Eligibility'}
                        </button>
                        <button
                          type="button"
                          disabled={!!nemtBusy || selectedOrder.status === 'completed'}
                          onClick={handleNemtDispatch}
                          style={{ width: '100%', padding: '12px 16px', borderRadius: 10, border: 'none', fontWeight: 700, fontSize: 14, color: '#fff', backgroundColor: division.solid, cursor: nemtBusy ? 'wait' : 'pointer', opacity: nemtBusy || selectedOrder.status === 'completed' ? 0.6 : 1 }}
                        >
                          {nemtBusy === 'dispatch' ? 'Dispatching…' : 'Dispatch Trip'}
                        </button>
                        <div style={{ marginTop: 4 }}>
                          <label style={{ display: 'block', fontSize: 11, fontWeight: 600, color: '#9CA3AF', marginBottom: 6 }}>
                            Guest ride tracking link
                          </label>
                          <input
                            type="url"
                            value={rideTrackingInput}
                            onChange={(e) => setRideTrackingInput(e.target.value)}
                            placeholder="Paste tracking URL from dispatch dashboard"
                            disabled={!!nemtBusy || selectedOrder.status === 'completed'}
                            style={{ width: '100%', padding: '10px 12px', borderRadius: 8, border: '1px solid rgba(255,255,255,0.15)', background: '#0D0D12', color: '#F9FAFB', fontSize: 13, marginBottom: 8 }}
                          />
                          <button
                            type="button"
                            disabled={!!nemtBusy || selectedOrder.status === 'completed'}
                            onClick={handleSaveRideTracking}
                            style={{ width: '100%', padding: '10px 14px', borderRadius: 8, border: '1px solid rgba(255,255,255,0.2)', fontWeight: 600, fontSize: 13, color: '#E5E7EB', background: '#1F2937', cursor: nemtBusy ? 'wait' : 'pointer', opacity: nemtBusy || selectedOrder.status === 'completed' ? 0.6 : 1 }}
                          >
                            {nemtBusy === 'tracking' ? 'Saving…' : 'Save link → client portal'}
                          </button>
                          {selectedOrder.rideTrackingUrl && (
                            <a
                              href={selectedOrder.rideTrackingUrl}
                              target="_blank"
                              rel="noopener noreferrer"
                              style={{ display: 'inline-block', marginTop: 8, fontSize: 12, color: '#A78BFA' }}
                            >
                              Open current tracking link ↗
                            </a>
                          )}
                          <p style={{ fontSize: 11, color: '#6B7280', marginTop: 6, lineHeight: 1.4 }}>
                            Paste after dispatch. Member sees &quot;Track live ride&quot; on portal.deedavis.biz — no app required.
                          </p>
                        </div>
                        <button
                          type="button"
                          disabled={!!nemtBusy || selectedOrder.status === 'completed'}
                          onClick={handleNemtComplete}
                          style={{ width: '100%', padding: '12px 16px', borderRadius: 10, border: 'none', fontWeight: 700, fontSize: 14, color: '#fff', background: '#059669', cursor: nemtBusy ? 'wait' : 'pointer', opacity: nemtBusy || selectedOrder.status === 'completed' ? 0.6 : 1 }}
                        >
                          {nemtBusy === 'complete' ? 'Closing trip…' : 'Mark Complete → Invoice'}
                        </button>
                      </div>
                    </>
                  ) : (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                      <button type="button" style={{ width: '100%', padding: '12px 16px', borderRadius: 10, border: 'none', fontWeight: 700, fontSize: 14, color: '#fff', backgroundColor: division.solid, cursor: 'pointer' }}>
                        Schedule / Update
                      </button>
                      <button type="button" style={{ width: '100%', padding: '12px 16px', borderRadius: 10, border: '1px solid rgba(255,255,255,0.15)', fontWeight: 600, fontSize: 14, color: '#F9FAFB', background: '#1F2937', cursor: 'pointer' }}>
                        Add Confirmation #
                      </button>
                      <button type="button" style={{ width: '100%', padding: '12px 16px', borderRadius: 10, border: '1px solid rgba(255,255,255,0.15)', fontWeight: 600, fontSize: 14, color: '#F9FAFB', background: '#1F2937', cursor: 'pointer' }}>
                        Upload Document
                      </button>
                      <button type="button" style={{ width: '100%', padding: '12px 16px', borderRadius: 10, border: 'none', fontWeight: 700, fontSize: 14, color: '#fff', background: '#059669', cursor: 'pointer' }}>
                        Mark Complete
                      </button>
                    </div>
                  )}
                </div>

                <div style={{ background: '#14141A', border: '1px solid rgba(255,255,255,0.12)', borderRadius: 14, padding: 18 }}>
                  <h3 style={{ fontSize: 16, fontWeight: 700, color: '#FFFFFF', marginBottom: 12 }}>Attachments</h3>
                  {selectedOrder.attachments.length > 0 ? (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                      {selectedOrder.attachments.map((att, i) => (
                        <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 8, padding: 10, background: '#0D0D12', borderRadius: 8, fontSize: 14, color: '#E5E7EB' }}>
                          <span>{att.type === 'screenshot' ? '📸' : att.type === 'document' ? '📄' : '📊'}</span>
                          <span style={{ flex: 1, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{att.name}</span>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p style={{ fontSize: 14, color: '#9CA3AF' }}>No attachments</p>
                  )}
                </div>

                <div style={{ background: '#14141A', border: '1px solid rgba(255,255,255,0.12)', borderRadius: 14, padding: 18 }}>
                  <h3 style={{ fontSize: 16, fontWeight: 700, color: '#FFFFFF', marginBottom: 12 }}>Open in Portal</h3>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                    {division.partnerPortals.slice(0, 3).map((portal) => (
                      <button
                        key={portal.id}
                        type="button"
                        onClick={() => onOpenPortal(portal)}
                        style={{ width: '100%', display: 'flex', alignItems: 'center', gap: 8, padding: '10px 12px', borderRadius: 8, fontSize: 14, color: '#F9FAFB', background: '#1F2937', border: '1px solid rgba(255,255,255,0.1)', cursor: 'pointer' }}
                      >
                        <span>{portal.icon}</span>
                        <span>{portal.name}</span>
                        <span style={{ marginLeft: 'auto', color: '#9CA3AF' }}>→</span>
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* ═══ AGENT NETWORK (searchable directory — scales to hundreds) ═══ */}
        {activeSection === 'agents' && (
          <div>
            <div style={{ padding: '20px 28px', borderBottom: '1px solid rgba(255,255,255,0.05)', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div>
                <h1 style={{ fontSize: 18, fontWeight: 700, color: '#F9FAFB' }}>Agent Network</h1>
                <p style={{ fontSize: 12, color: 'rgba(107,114,128,0.7)', marginTop: 2 }}>
                  Search nationwide · filter by division, state, and availability
                </p>
              </div>
              <a
                href="/agent-portal"
                target="_blank"
                rel="noopener noreferrer"
                style={{ padding: '9px 18px', background: division.solid, color: '#fff', borderRadius: 9, fontWeight: 600, fontSize: 13, textDecoration: 'none' }}
              >
                + Recruit Agent
              </a>
            </div>
            <div style={{ padding: 28 }}>
              <PrismAgentDirectory
                agents={agentsProp}
                loading={agentsLoading}
                accent={division.solid}
                divisionName={division.name}
                divisionTypes={divisionTypes}
                agentSpecialtyLabels={agentSpecialtyLabels}
                mode="directory"
              />
            </div>
          </div>
        )}

        {/* ═══ SCANBACKS ═══ */}
        {activeSection === 'scanbacks' && (
          <div>
            <div style={{ padding: '20px 28px', borderBottom: '1px solid rgba(255,255,255,0.05)', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div>
                <h1 style={{ fontSize: 18, fontWeight: 700, color: '#F9FAFB' }}>Scanbacks & Results</h1>
                <p style={{ fontSize: 12, color: 'rgba(107,114,128,0.7)', marginTop: 2 }}>2 pending review</p>
              </div>
              <div style={{ display: 'flex', gap: 6 }}>
                {['All', 'Needs Review (2)', 'Verified'].map((label, i) => (
                  <button key={label} style={{ padding: '7px 14px', borderRadius: 7, fontSize: 12, fontWeight: 500, cursor: 'pointer', background: i === 1 ? 'rgba(234,179,8,0.12)' : 'rgba(255,255,255,0.05)', color: i === 1 ? '#FCD34D' : '#9CA3AF', border: i === 1 ? '1px solid rgba(234,179,8,0.25)' : '1px solid rgba(255,255,255,0.07)' }}>
                    {label}
                  </button>
                ))}
              </div>
            </div>
            <div style={{ padding: 28, display: 'flex', flexDirection: 'column', gap: 8 }}>
              {[
                { id: 's1', orderId: 'ORD-2026-0542', subject: 'James Wilson',   type: 'DOT',          status: 'needs_review', labResult: 'Negative', receivedAt: '2026-05-18 11:30 AM' },
                { id: 's2', orderId: 'ORD-2026-0541', subject: 'Patricia Moore',  type: 'Random',       status: 'needs_review', labResult: 'Pending',  receivedAt: '2026-05-18 10:15 AM' },
                { id: 's3', orderId: 'ORD-2026-0538', subject: 'Robert Chen',    type: 'Post-Accident', status: 'verified',     labResult: 'Negative', receivedAt: '2026-05-17 4:00 PM' },
              ].map(scan => {
                const needsReview = scan.status === 'needs_review';
                const resultColor = scan.labResult === 'Negative' ? '#34D399' : scan.labResult === 'Pending' ? '#FCD34D' : '#F87171';
                return (
                  <div key={scan.id} style={{ display: 'flex', alignItems: 'center', gap: 16, padding: '14px 18px', background: '#14141A', border: `1px solid ${needsReview ? 'rgba(234,179,8,0.25)' : 'rgba(255,255,255,0.06)'}`, borderRadius: 11 }}>
                    <div style={{ width: 42, height: 42, borderRadius: 10, background: needsReview ? 'rgba(234,179,8,0.1)' : 'rgba(16,185,129,0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                      <svg width="18" height="18" fill="none" viewBox="0 0 24 24" stroke={needsReview ? '#FCD34D' : '#34D399'} strokeWidth="1.8"><path strokeLinecap="round" strokeLinejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>
                    </div>
                    <div style={{ flex: 1 }}>
                      <p style={{ fontWeight: 700, fontSize: 14, color: '#F9FAFB' }}>{scan.subject}</p>
                      <p style={{ fontSize: 12, color: 'rgba(107,114,128,0.7)', marginTop: 2 }}>{scan.orderId} &nbsp;·&nbsp; {scan.type} &nbsp;·&nbsp; {scan.receivedAt}</p>
                    </div>
                    <div style={{ textAlign: 'right' as const }}>
                      <p style={{ fontWeight: 700, fontSize: 14, color: resultColor }}>{scan.labResult}</p>
                      <p style={{ fontSize: 11, color: 'rgba(107,114,128,0.6)', marginTop: 2 }}>{needsReview ? 'Needs Review' : 'Verified'}</p>
                    </div>
                    <button style={{ padding: '7px 14px', borderRadius: 7, background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(255,255,255,0.08)', color: '#D1D5DB', fontSize: 12, cursor: 'pointer' }}>
                      View →
                    </button>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* ═══ ANALYTICS ═══ */}
        {activeSection === 'analytics' && (
          <div>
            <div style={{ padding: '20px 28px', borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
              <h1 style={{ fontSize: 18, fontWeight: 700, color: '#F9FAFB' }}>Analytics</h1>
              <p style={{ fontSize: 12, color: 'rgba(107,114,128,0.7)', marginTop: 2 }}>Month-to-date performance</p>
            </div>

            {/* KPI ribbon */}
            <div style={{ display: 'flex', borderBottom: '1px solid rgba(255,255,255,0.05)', background: '#0A0A0F' }}>
              {[
                { label: 'Total Orders',       value: '47',       trend: '+12%', up: true  },
                { label: 'Gross Revenue',       value: '$8,450',   trend: '+8%',  up: true  },
                { label: 'Avg Turnaround',      value: '2.3 days', trend: '-15%', up: false },
                { label: 'Client Rating',       value: '4.8 ★',   trend: '+0.2', up: true  },
              ].map((s, i) => (
                <div key={s.label} style={{ flex: 1, padding: '16px 22px', borderRight: i < 3 ? '1px solid rgba(255,255,255,0.05)' : 'none' }}>
                  <div style={{ display: 'flex', alignItems: 'baseline', gap: 8 }}>
                    <p style={{ fontSize: 24, fontWeight: 800, color: '#F9FAFB', letterSpacing: -0.5 }}>{s.value}</p>
                    <span style={{ fontSize: 11, fontWeight: 600, color: s.up ? '#34D399' : '#F87171' }}>{s.trend}</span>
                  </div>
                  <p style={{ fontSize: 11, color: 'rgba(107,114,128,0.7)', marginTop: 3 }}>{s.label}</p>
                </div>
              ))}
            </div>

            <div style={{ padding: 28, display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20 }}>
              {/* Orders by Type bar chart */}
              <div style={{ background: '#14141A', border: '1px solid rgba(255,255,255,0.06)', borderRadius: 14, padding: 22 }}>
                <p style={{ fontSize: 12, fontWeight: 600, color: 'rgba(156,163,175,0.7)', textTransform: 'uppercase', letterSpacing: 0.7, marginBottom: 20 }}>Orders by Type</p>
                <div style={{ display: 'flex', alignItems: 'flex-end', justifyContent: 'space-around', height: 160, gap: 10, paddingBottom: 8 }}>
                  {[
                    { label: 'DOT',      value: 65, color: '#F97316' },
                    { label: 'Non-DOT',  value: 25, color: '#6366F1' },
                    { label: 'Random',   value: 40, color: '#F59E0B' },
                    { label: 'Pre-Emp',  value: 55, color: '#10B981' },
                  ].map(bar => (
                    <div key={bar.label} style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 6 }}>
                      <div style={{ width: '100%', borderRadius: '4px 4px 0 0', backgroundColor: bar.color, height: `${bar.value * 1.5}px`, opacity: 0.85 }} />
                      <span style={{ fontSize: 11, color: 'rgba(107,114,128,0.7)' }}>{bar.label}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Revenue trend placeholder */}
              <div style={{ background: '#14141A', border: '1px solid rgba(255,255,255,0.06)', borderRadius: 14, padding: 22 }}>
                <p style={{ fontSize: 12, fontWeight: 600, color: 'rgba(156,163,175,0.7)', textTransform: 'uppercase', letterSpacing: 0.7, marginBottom: 20 }}>Revenue Trend</p>
                <div style={{ height: 160, display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column', gap: 8 }}>
                  <svg width="40" height="40" fill="none" viewBox="0 0 24 24" stroke="rgba(107,114,128,0.4)" strokeWidth="1.5"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>
                  <p style={{ fontSize: 12, color: 'rgba(107,114,128,0.5)' }}>Chart integration coming soon</p>
                </div>
              </div>

              {/* Top clients */}
              <div style={{ background: '#14141A', border: '1px solid rgba(255,255,255,0.06)', borderRadius: 14, padding: 22, gridColumn: '1 / -1' }}>
                <p style={{ fontSize: 12, fontWeight: 600, color: 'rgba(156,163,175,0.7)', textTransform: 'uppercase', letterSpacing: 0.7, marginBottom: 16 }}>Top Clients by Volume</p>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                  {[
                    { name: 'ABC Trucking Co.',       orders: 18, revenue: '$3,240', pct: 38 },
                    { name: 'Metro Transit Authority', orders: 14, revenue: '$2,800', pct: 30 },
                    { name: 'Midwest Logistics LLC',  orders: 9,  revenue: '$1,620', pct: 19 },
                  ].map(c => (
                    <div key={c.name} style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
                      <p style={{ fontSize: 13, fontWeight: 600, color: '#E5E7EB', width: 220, flexShrink: 0 }}>{c.name}</p>
                      <div style={{ flex: 1, height: 6, background: 'rgba(255,255,255,0.06)', borderRadius: 3 }}>
                        <div style={{ width: `${c.pct}%`, height: '100%', background: '#F97316', borderRadius: 3 }} />
                      </div>
                      <p style={{ fontSize: 12, color: 'rgba(107,114,128,0.7)', width: 40, textAlign: 'right' as const }}>{c.orders}</p>
                      <p style={{ fontSize: 12, fontWeight: 600, color: '#34D399', width: 60, textAlign: 'right' as const }}>{c.revenue}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* ═══ PAYMENTS ═══ */}
        {activeSection === 'payments' && (
          <div>
            <div style={{ padding: '20px 28px', borderBottom: '1px solid rgba(255,255,255,0.05)', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div>
                <h1 style={{ fontSize: 18, fontWeight: 700, color: '#F9FAFB' }}>Payments & Invoicing</h1>
                <p style={{ fontSize: 12, color: 'rgba(107,114,128,0.7)', marginTop: 2 }}>Month-to-date billing</p>
              </div>
              <button style={{ padding: '9px 18px', background: '#F97316', color: '#fff', borderRadius: 9, fontWeight: 600, fontSize: 13, border: 'none', cursor: 'pointer' }}>
                + Create Invoice
              </button>
            </div>

            {/* Summary ribbon */}
            <div style={{ display: 'flex', borderBottom: '1px solid rgba(255,255,255,0.05)', background: '#0A0A0F' }}>
              {[
                { label: 'Collected (MTD)', value: '$6,240', bg: 'rgba(16,185,129,0.08)',  border: 'rgba(16,185,129,0.15)',  color: '#34D399' },
                { label: 'Pending',         value: '$2,180', bg: 'rgba(234,179,8,0.08)',   border: 'rgba(234,179,8,0.15)',   color: '#FCD34D' },
                { label: 'Overdue',         value: '$450',   bg: 'rgba(239,68,68,0.08)',   border: 'rgba(239,68,68,0.15)',   color: '#FCA5A5' },
              ].map((s, i) => (
                <div key={s.label} style={{ flex: 1, padding: '18px 28px', borderRight: i < 2 ? '1px solid rgba(255,255,255,0.05)' : 'none', background: s.bg, borderBottom: `2px solid ${s.border}` }}>
                  <p style={{ fontSize: 24, fontWeight: 800, color: s.color, letterSpacing: -0.5 }}>{s.value}</p>
                  <p style={{ fontSize: 11, color: 'rgba(107,114,128,0.7)', marginTop: 3 }}>{s.label}</p>
                </div>
              ))}
            </div>

            <div style={{ padding: 28 }}>
              <p style={{ fontSize: 11, fontWeight: 600, color: 'rgba(156,163,175,0.6)', textTransform: 'uppercase', letterSpacing: 0.8, marginBottom: 14 }}>Recent Invoices</p>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                {[
                  { id: 'INV-2026-0089', client: 'ABC Trucking Co.',         amount: '$1,250', status: 'paid',    date: '2026-05-15' },
                  { id: 'INV-2026-0088', client: 'Metro Transit Authority',  amount: '$3,400', status: 'pending', date: '2026-05-12' },
                  { id: 'INV-2026-0087', client: 'Midwest Logistics LLC',    amount: '$450',   status: 'overdue', date: '2026-05-01' },
                ].map(inv => {
                  const cfg = inv.status === 'paid'
                    ? { bg: 'rgba(16,185,129,0.12)',  color: '#34D399'  }
                    : inv.status === 'pending'
                    ? { bg: 'rgba(234,179,8,0.12)',   color: '#FCD34D'  }
                    : { bg: 'rgba(239,68,68,0.12)',   color: '#FCA5A5'  };
                  return (
                    <div key={inv.id} style={{ display: 'flex', alignItems: 'center', gap: 16, padding: '14px 18px', background: '#14141A', border: '1px solid rgba(255,255,255,0.06)', borderRadius: 11 }}>
                      <div style={{ flex: 1, minWidth: 0 }}>
                        <p style={{ fontWeight: 700, fontSize: 14, color: '#F9FAFB' }}>{inv.id}</p>
                        <p style={{ fontSize: 12, color: 'rgba(107,114,128,0.7)', marginTop: 2 }}>{inv.client} &nbsp;·&nbsp; {inv.date}</p>
                      </div>
                      <p style={{ fontWeight: 800, fontSize: 16, color: '#F9FAFB' }}>{inv.amount}</p>
                      <span style={{ ...cfg, padding: '3px 10px', borderRadius: 6, fontSize: 10, fontWeight: 700, letterSpacing: 0.3 }}>
                        {inv.status.toUpperCase()}
                      </span>
                      <button style={{ padding: '7px 14px', borderRadius: 7, background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(255,255,255,0.08)', color: '#D1D5DB', fontSize: 12, cursor: 'pointer' }}>
                        View
                      </button>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        )}

        {/* ═══ NEW ORDER MODAL ═══ */}
        {showNewOrderModal && (
          <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4" onClick={() => setShowNewOrderModal(false)}>
            <div className="bg-gray-900 border border-gray-700 rounded-2xl w-full max-w-lg shadow-2xl" onClick={e => e.stopPropagation()}>
              <div className="flex items-center justify-between p-6 border-b border-gray-700">
                <div>
                  <h2 className="text-lg font-bold text-white">New Order</h2>
                  <p className="text-xs text-gray-400 mt-0.5">{division.name} Division</p>
                </div>
                <button onClick={() => setShowNewOrderModal(false)} className="w-8 h-8 rounded-lg bg-gray-800 hover:bg-gray-700 flex items-center justify-center text-gray-400 hover:text-white transition">✕</button>
              </div>
              <div className="p-6 space-y-4">
                <div>
                  <label className="block text-xs font-semibold text-gray-400 mb-2">Service Type</label>
                  <select className="w-full bg-gray-800 border border-gray-700 rounded-xl px-4 py-3 text-sm text-white focus:outline-none focus:border-gray-500">
                    <option value="">Select service type...</option>
                    {division.serviceTypes.map(s => <option key={s.id} value={s.id}>{s.label}</option>)}
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-semibold text-gray-400 mb-2">Subject / Employee Name</label>
                  <input type="text" placeholder="Full legal name" className="w-full bg-gray-800 border border-gray-700 rounded-xl px-4 py-3 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-gray-500" />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-semibold text-gray-400 mb-2">Client</label>
                    <select className="w-full bg-gray-800 border border-gray-700 rounded-xl px-4 py-3 text-sm text-white focus:outline-none focus:border-gray-500">
                      <option value="">Select client...</option>
                      {MOCK_CLIENTS.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-gray-400 mb-2">Phone</label>
                    <input type="tel" placeholder="(555) 555-5555" className="w-full bg-gray-800 border border-gray-700 rounded-xl px-4 py-3 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-gray-500" />
                  </div>
                </div>
                <div>
                  <label className="block text-xs font-semibold text-gray-400 mb-2">Notes</label>
                  <textarea placeholder="Special instructions..." className="w-full bg-gray-800 border border-gray-700 rounded-xl px-4 py-3 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-gray-500 h-20 resize-none" />
                </div>
                <div className="flex items-center gap-3 p-4 bg-red-500/10 border border-red-500/30 rounded-xl">
                  <input type="checkbox" id="urgent" className="w-4 h-4 accent-red-500" />
                  <label htmlFor="urgent" className="text-sm text-red-400 font-semibold cursor-pointer">Urgent / Post-Accident (within 8 hours)</label>
                </div>
              </div>
              <div className="px-6 pb-6 flex gap-3">
                <button onClick={() => setShowNewOrderModal(false)} className="flex-1 px-4 py-3 rounded-xl font-semibold text-sm bg-gray-800 hover:bg-gray-700 text-gray-300 transition">Cancel</button>
                <button className="flex-1 px-4 py-3 rounded-xl font-semibold text-sm text-white transition hover:opacity-90" style={{ backgroundColor: division.solid }}>Create Order</button>
              </div>
            </div>
          </div>
        )}

        {/* ═══ VOICE INTAKE (NEMT call center) ═══ */}
        {activeSection === 'voice' && (
          <PrismVoiceCallCenter accent={division.solid} />
        )}

        {/* ═══ CAPTURE (Screenshot/Doc Drop) ═══ */}
        {activeSection === 'capture' && (
          <div className="p-6">
            <h1 className="text-xl font-bold mb-6">Capture</h1>
            <p className="text-gray-400 text-sm mb-4">
              Drop screenshots or documents here to link them to orders. Capture confirmation numbers, status updates, and results.
            </p>

            {/* Drop Zone */}
            <div
              onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
              onDragLeave={() => setDragOver(false)}
              onDrop={handleDrop}
              className={`border-2 border-dashed rounded-xl p-12 text-center transition ${
                dragOver 
                  ? 'border-green-500 bg-green-500/10' 
                  : 'border-gray-600 hover:border-gray-500'
              }`}
            >
              <div className="text-4xl mb-3">📸</div>
              <p className="font-semibold mb-1">Drop screenshots or files here</p>
              <p className="text-sm text-gray-500">or click to browse</p>
              <input type="file" multiple className="hidden" accept="image/*,.pdf,.xlsx,.xls,.csv" />
            </div>

            {/* Captured Documents */}
            {capturedDocs.length > 0 && (
              <div className="mt-6">
                <h3 className="font-bold mb-3">Captured Documents</h3>
                <div className="space-y-2">
                  {capturedDocs.map(doc => (
                    <div key={doc.id} className="bg-gray-800 border border-gray-700 rounded-xl p-4 flex items-center gap-4">
                      {doc.type === 'screenshot' && (
                        <img src={doc.url} alt="" className="w-20 h-20 object-cover rounded-lg" />
                      )}
                      {doc.type !== 'screenshot' && (
                        <div className="w-20 h-20 bg-gray-700 rounded-lg flex items-center justify-center text-2xl">
                          {doc.type === 'pdf' ? '📄' : '📊'}
                        </div>
                      )}
                      <div className="flex-1">
                        <p className="font-medium">{doc.filename}</p>
                        <p className="text-xs text-gray-500">{new Date(doc.uploadedAt).toLocaleString()}</p>
                        {doc.matched ? (
                          <span className="text-xs text-green-400">✓ Linked to Order</span>
                        ) : (
                          <span className="text-xs text-yellow-400">⚠ Not linked</span>
                        )}
                      </div>
                      <div className="flex flex-col gap-2">
                        <button className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-gray-700 hover:bg-gray-600 transition">
                          Link to Order
                        </button>
                        <button className="px-3 py-1.5 rounded-lg text-xs font-semibold text-red-400 hover:bg-red-500/20 transition">
                          Delete
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {showAgentPicker && selectedOrder && (
        <PrismAgentDirectory
          agents={agentsProp}
          loading={agentsLoading}
          accent={division.solid}
          divisionName={division.name}
          divisionTypes={divisionTypes}
          agentSpecialtyLabels={agentSpecialtyLabels}
          mode="picker"
          pickerTitle={`Assign agent · ${selectedOrder.subjectInfo.name}`}
          onSelectAgent={handleAssignFromPicker}
          onClose={() => setShowAgentPicker(false)}
        />
      )}
    </div>
  );
};

export default TPADivisionWorkspace;
