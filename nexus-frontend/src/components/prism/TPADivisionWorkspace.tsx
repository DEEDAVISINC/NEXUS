import React, { useEffect, useMemo, useState } from 'react';
import { api } from '../../api/client';
import PrismAgentDirectory from './PrismAgentDirectory';
import PrismVoiceCallCenter from './PrismVoiceCallCenter';
import PrismOpsFeed, { PrismNotification } from './PrismOpsFeed';
import { countDivisionAgents, PrismAgentRecord } from './prismAgentNetwork';
import HideSnpRevenueModel from '../systems/ddcss/HideSnpRevenueModel';
import {
  NEXUS_SHELL_PAGE,
  NEXUS_TITLE,
  NEXUS_SUBTITLE,
  NEXUS_BTN_PRIMARY,
  NEXUS_PANEL,
  NexusMetricCard,
  NexusPanel,
  NexusListRow,
} from '../shared/NexusDashboardShell';

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

/** Map NEXUS `/prism/clients` API row → workspace client card */
export function mapPrismApiClientToWorkspace(c: Record<string, unknown>): Client {
  const statusRaw = String(c.status || 'active').toLowerCase();
  let status: Client['status'] = 'active';
  if (statusRaw.includes('inactive')) status = 'inactive';
  else if (statusRaw.includes('pending')) status = 'pending';

  return {
    id: String(c.id || ''),
    name: String(c.name || '—'),
    contactName: String(c.contact_name || c.contactName || '—'),
    contactEmail: String(c.email || c.contact_email || c.contactEmail || ''),
    contactPhone: String(c.phone || c.contact_phone || c.contactPhone || ''),
    portalLink: String(c.portal_code || c.portalLink || ''),
    contractType: 'monthly',
    activeOrders: Number(c.active_orders ?? c.activeOrders ?? 0),
    totalOrders: Number(c.orders ?? c.totalOrders ?? 0),
    status,
    createdAt: String(c.created_at || c.createdAt || ''),
  };
}

export interface DivisionScanback {
  id: string;
  orderId: string;
  type: string;
  agent: string;
  client: string;
  signer: string;
  status: string;
  pages: number;
  uploadDate: string;
  errors: { severity: string; page: number; description: string }[];
}

interface VertexInvoiceRow {
  record_id: string;
  invoice_number: string;
  client_name: string;
  amount: number;
  amount_paid: number;
  balance_due: number;
  status: string;
  date: string;
  due_date: string;
  source_system: string;
  pdf_path?: string | null;
}

interface VertexInvoiceSummary {
  total_billed: number;
  collected: number;
  pending: number;
  overdue: number;
  count: number;
}

const fmtUsd = (n: number) =>
  n.toLocaleString('en-US', { style: 'currency', currency: 'USD' });

const API_BASE = process.env.REACT_APP_API_BASE || 'http://127.0.0.1:8000';

function normalizeScanbackUiStatus(status: string): 'needs_review' | 'verified' | 'other' {
  const s = status.toLowerCase();
  if (s.includes('needs review') || s.includes('under review') || s.includes('errors found') || s.includes('correction')) {
    return 'needs_review';
  }
  if (s.includes('verified') || s.includes('closed') || s.includes('complete')) {
    return 'verified';
  }
  return 'other';
}

const EmptyPanel: React.FC<{ title: string; hint?: string }> = ({ title, hint }) => (
  <div style={{ padding: '48px 28px', textAlign: 'center' }}>
    <p style={{ fontSize: 14, fontWeight: 600, color: '#9CA3AF' }}>{title}</p>
    {hint ? <p style={{ fontSize: 12, color: 'rgba(107,114,128,0.6)', marginTop: 8 }}>{hint}</p> : null}
  </div>
);

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
  /** Live clients from GET /prism/clients */
  clients?: Client[];
  clientsLoading?: boolean;
  /** Scanbacks derived from orders (division-filtered by parent) */
  scanbacks?: DivisionScanback[];
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
  /** Deep-link from App (?division=transport&section=revenue) */
  initialSection?: 'dashboard' | 'clients' | 'orders' | 'agents' | 'scanbacks' | 'analytics' | 'payments' | 'capture' | 'voice' | 'revenue';
  onNavigate?: (view: string, tab?: string) => void;
}

// ─── COMPONENT ─────────────────────────────────────────────────────
const TPADivisionWorkspace: React.FC<TPADivisionWorkspaceProps> = ({
  division,
  orders: ordersProp,
  ordersLoading = false,
  onRefreshOrders,
  clients: clientsProp = [],
  clientsLoading = false,
  scanbacks: scanbacksProp = [],
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
  initialSection,
  onNavigate,
}) => {
  const [activeSection, setActiveSection] = useState<'dashboard' | 'clients' | 'orders' | 'agents' | 'scanbacks' | 'analytics' | 'payments' | 'capture' | 'voice' | 'revenue'>(
    initialSection || 'dashboard'
  );
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
  const [scanbackFilter, setScanbackFilter] = useState<'all' | 'needs_review' | 'verified'>('all');
  const [vertexInvoiceRows, setVertexInvoiceRows] = useState<VertexInvoiceRow[]>([]);
  const [vertexInvoiceSummary, setVertexInvoiceSummary] = useState<VertexInvoiceSummary | null>(null);
  const [invoicesLoading, setInvoicesLoading] = useState(false);
  const [portalCopied, setPortalCopied] = useState(false);

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

  const displayOrders = ordersProp ?? [];

  const displayClients = useMemo(() => {
    const enrich = (client: Client): Client => ({
      ...client,
      activeOrders: displayOrders.filter(
        (o) => o.clientName === client.name && ['pending', 'scheduled', 'in_progress'].includes(o.status)
      ).length,
      totalOrders: displayOrders.filter((o) => o.clientName === client.name).length || client.totalOrders,
    });

    if (clientsProp.length > 0) {
      return clientsProp.map(enrich);
    }

    const byName = new Map<string, Client>();
    displayOrders.forEach((o) => {
      const name = o.clientName || 'Unknown';
      if (!byName.has(name)) {
        byName.set(name, {
          id: o.clientId || name,
          name,
          contactName: '—',
          contactEmail: '',
          contactPhone: '',
          portalLink: '',
          contractType: 'monthly',
          activeOrders: 0,
          totalOrders: 0,
          status: 'active',
          createdAt: o.createdAt || '',
        });
      }
      const client = byName.get(name)!;
      client.totalOrders += 1;
      if (['pending', 'scheduled', 'in_progress'].includes(o.status)) {
        client.activeOrders += 1;
      }
    });
    return Array.from(byName.values());
  }, [clientsProp, displayOrders]);

  const filteredScanbacks = useMemo(() => {
    if (scanbackFilter === 'all') return scanbacksProp;
    return scanbacksProp.filter((s) => normalizeScanbackUiStatus(s.status) === scanbackFilter);
  }, [scanbacksProp, scanbackFilter]);

  const needsReviewCount = scanbacksProp.filter((s) => normalizeScanbackUiStatus(s.status) === 'needs_review').length;

  const ordersByType = useMemo(() => {
    const counts: Record<string, number> = {};
    displayOrders.forEach((o) => {
      const key = o.type || 'other';
      counts[key] = (counts[key] || 0) + 1;
    });
    return Object.entries(counts)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 8);
  }, [displayOrders]);

  const topClientsByVolume = useMemo(() => {
    const map = new Map<string, number>();
    displayOrders.forEach((o) => {
      const name = o.clientName || 'Unknown';
      map.set(name, (map.get(name) || 0) + 1);
    });
    const max = Math.max(1, ...Array.from(map.values()));
    return Array.from(map.entries())
      .sort((a, b) => b[1] - a[1])
      .slice(0, 5)
      .map(([name, count]) => ({ name, orders: count, pct: Math.round((count / max) * 100) }));
  }, [displayOrders]);

  const vertexInvoices = useMemo(() => {
    const seen = new Set<string>();
    const rows: { id: string; client: string; date: string }[] = [];
    displayOrders.forEach((o) => {
      if (!o.vertexInvoiceId || seen.has(o.vertexInvoiceId)) return;
      seen.add(o.vertexInvoiceId);
      rows.push({
        id: o.vertexInvoiceId,
        client: o.clientName,
        date: (o.updatedAt || o.createdAt || '').slice(0, 10) || '—',
      });
    });
    return rows;
  }, [displayOrders]);

  useEffect(() => {
    if (activeSection !== 'payments') return;

    const ids = Array.from(new Set(displayOrders.map((o) => o.vertexInvoiceId).filter(Boolean))) as string[];
    const clientNames = Array.from(new Set(displayClients.map((c) => c.name).filter(Boolean)));

    if (ids.length === 0 && clientNames.length === 0) {
      setVertexInvoiceRows([]);
      setVertexInvoiceSummary(null);
      return;
    }

    let cancelled = false;
    setInvoicesLoading(true);

    api
      .post('/prism/billing/invoices', { ids, client_names: clientNames })
      .then((data: { invoices?: VertexInvoiceRow[]; summary?: VertexInvoiceSummary }) => {
        if (cancelled) return;
        setVertexInvoiceRows(data.invoices || []);
        setVertexInvoiceSummary(data.summary || null);
      })
      .catch(() => {
        if (cancelled) return;
        setVertexInvoiceRows([]);
        setVertexInvoiceSummary(null);
      })
      .finally(() => {
        if (!cancelled) setInvoicesLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [activeSection, displayOrders, displayClients]);

  const copyPortalLink = (code: string) => {
    if (!code) return;
    const url = `${window.location.origin}/client/${code}`;
    navigator.clipboard.writeText(url).then(() => {
      setPortalCopied(true);
      window.setTimeout(() => setPortalCopied(false), 2000);
    });
  };

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
    activeClients: displayClients.filter((c) => c.status === 'active').length,
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
      setNemtMsg({ ok: true, text: '✅ Tracking link saved — member will see 🚗 Track live ride on portal.' });
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
      const pickup = String(nemt.actual_pickup_time || nemt.pickup_time || now);
      const dropoff = String(nemt.actual_dropoff_time || nemt.dropoff_time || now);
      const mileage = Number(nemt.actual_mileage ?? nemt.mileage ?? 0);
      const res = await api.completeNemtTrip(nemtId, {
        actual_pickup_time: pickup,
        actual_dropoff_time: dropoff,
        actual_mileage: Number.isFinite(mileage) ? mileage : 0,
        auto_generate_claim: true,
        member_phone: selectedOrder.subjectInfo.phone || undefined,
      });
      if (res?.error) {
        const gateMsg = res.qc_gate_blocked
          ? `${res.error} — fix QC pillars before billing (Verify Eligibility + Dispatch first).`
          : String(res.error);
        setNemtMsg({ ok: false, text: gateMsg });
        return;
      }
      const invId =
        res.order?.vertex_invoice_id ||
        res.claim?.invoice?.id ||
        res.claim?.invoice_id;
      const qcId = res.qc_record?.qc_id;
      const gateWarnings = res.qc_record?.gate_billing?.warnings?.length;
      setSelectedOrder({
        ...selectedOrder,
        status: 'completed',
        vertexInvoiceId: invId ? String(invId) : selectedOrder.vertexInvoiceId,
        nemtOrderId: nemtId,
      });
      let successText = invId
        ? `Trip complete — VERTEX invoice (${String(invId).slice(0, 12)}…).`
        : 'Trip complete — claim logged.';
      if (qcId) successText += ` QC record ${qcId}.`;
      if (gateWarnings) successText += ' Member grade pending (normal — SMS sends after trip).';
      setNemtMsg({ ok: true, text: successText });
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
    )},
    { id: 'revenue', label: 'HIDE SNP Revenue', icon: (
      <svg width="15" height="15" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="1.8"><path strokeLinecap="round" strokeLinejoin="round" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
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
    <div className={`flex min-h-screen ${NEXUS_SHELL_PAGE}`}>

      {/* ─── SIDEBAR ─── */}
      <div className="w-56 shrink-0 bg-gray-900/80 border-r border-gray-700/60 flex flex-col backdrop-blur-sm">

        {/* Division header */}
        <div className="p-4 border-b border-gray-700/60">
          <button
            type="button"
            onClick={onBack}
            className="flex items-center gap-1.5 text-xs text-gray-400 hover:text-gray-200 mb-4 transition-colors"
          >
            <svg width="12" height="12" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2"><path strokeLinecap="round" strokeLinejoin="round" d="M15.75 19.5L8.25 12l7.5-7.5"/></svg>
            Back to Hub
          </button>
          <div className="flex items-center gap-3">
            <span className="text-2xl">{division.icon}</span>
            <div>
              <p className="font-bold text-sm text-white">{division.name}</p>
              <p className="text-[10px] text-gray-500 mt-0.5">TPA Division</p>
            </div>
          </div>
        </div>

        {/* Nav */}
        <nav className="flex-1 p-2 overflow-y-auto">
          {NAV_ITEMS.map(item => {
            const active = activeSection === item.id;
            return (
              <button
                key={item.id}
                type="button"
                onClick={() => { setActiveSection(item.id as any); setSelectedClient(null); setSelectedOrder(null); }}
                className={`w-full flex items-center gap-2.5 px-3 py-2.5 rounded-lg mb-0.5 text-left text-sm transition-all ${
                  active
                    ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white font-semibold shadow-lg shadow-purple-900/30'
                    : 'text-gray-400 hover:bg-gray-800 hover:text-gray-200'
                }`}
              >
                {item.icon}
                <span className="flex-1 truncate">{item.label}</span>
                {item.badge !== undefined && item.badge > 0 && (
                  <span className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${
                    active ? 'bg-white/20 text-white' : 'bg-gray-700 text-gray-300'
                  }`}>{item.badge}</span>
                )}
              </button>
            );
          })}
        </nav>

        {/* Partner portals */}
        <div className="p-2 border-t border-gray-700/60">
          <p className="text-[10px] font-semibold text-gray-500 uppercase tracking-wider px-3 mb-2">Live Portals</p>
          {division.partnerPortals.slice(0, 5).map(portal => (
            <button
              key={portal.id}
              type="button"
              onClick={() => onOpenPortal(portal)}
              className="w-full flex items-center gap-2 px-3 py-2 rounded-lg text-xs text-gray-400 hover:bg-gray-800 hover:text-gray-200 transition-all text-left"
            >
              <span>{portal.icon}</span>
              <span className="flex-1 truncate">{portal.name}</span>
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 shrink-0" />
            </button>
          ))}
        </div>
      </div>

      {/* ─── MAIN CONTENT ─── */}
      <div className="flex-1 overflow-y-auto p-8">
        {/* ═══ DASHBOARD ═══ */}
        {activeSection === 'dashboard' && (
          <div className="space-y-6 max-w-7xl mx-auto">
            <div className="flex flex-wrap items-start justify-between gap-4">
              <div>
                <h1 className={NEXUS_TITLE}>
                  {division.icon} {division.name}
                </h1>
                <p className={NEXUS_SUBTITLE}>Division Command Center</p>
              </div>
              <div className="flex items-center gap-3">
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
                <button type="button" onClick={() => setShowNewOrderModal(true)} className={NEXUS_BTN_PRIMARY}>
                  + New Order
                </button>
              </div>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
              <NexusMetricCard label="Pending" value={stats.pending} icon="⏳" accent="yellow" />
              <NexusMetricCard label="Scheduled" value={stats.scheduled} icon="📅" accent="blue" />
              <NexusMetricCard label="In Progress" value={stats.inProgress} icon="⚡" accent="purple" />
              <NexusMetricCard label="Completed Today" value={stats.completedToday} icon="✅" accent="green" />
              <NexusMetricCard label="Active Clients" value={stats.activeClients} icon="👥" accent="teal" />
            </div>

            {showVoiceIntake && opsNotifications.length > 0 && (
              <NexusPanel title="Live Ops — Voice & Intake" titleAccent="text-teal-300">
                <div className="space-y-2">
                  {opsNotifications.slice(0, 5).map((n) => (
                    <button
                      key={n.id}
                      type="button"
                      onClick={() => {
                        onMarkOpsRead?.(n.id);
                        onOpsNotificationClick?.(n);
                      }}
                      className="w-full text-left p-3 bg-gray-700/50 rounded-lg border border-teal-500/20 hover:bg-gray-700/70 transition-all"
                    >
                      <p className="text-sm font-semibold text-white">
                        {n.icon ? `${n.icon} ` : ''}{n.title}
                      </p>
                      <p className="text-xs text-gray-400 mt-1">{n.message}</p>
                    </button>
                  ))}
                </div>
              </NexusPanel>
            )}

            <NexusPanel title="Today's Schedule">
              <div className="space-y-2">
                {displayOrders.filter(o => o.status === 'scheduled' || o.status === 'in_progress').map(order => (
                  <NexusListRow
                    key={order.id}
                    onClick={() => { setActiveSection('orders'); setSelectedOrder(order); }}
                  >
                    <span className="shrink-0 text-xs font-semibold text-purple-300 min-w-[4rem]">
                      {order.scheduledTime || 'TBD'}
                    </span>
                    <div className="flex-1 min-w-0">
                      <p className="font-semibold text-sm text-white">{order.subjectInfo.name}</p>
                      <p className="text-xs text-gray-400 mt-0.5">
                        {order.clientName} · {order.type.toUpperCase()}
                      </p>
                    </div>
                    <div className="text-right shrink-0">
                      <p className="text-xs text-gray-400">{order.location}</p>
                      {order.assignedAgent && <p className="text-xs text-gray-500">{order.assignedAgent}</p>}
                    </div>
                  </NexusListRow>
                ))}
                {displayOrders.filter(o => o.status === 'scheduled' || o.status === 'in_progress').length === 0 && (
                  <p className="text-gray-500 text-sm text-center py-6">No scheduled orders today</p>
                )}
              </div>
            </NexusPanel>

            {displayOrders.filter(o => o.status === 'pending').length > 0 && (
              <div className={`${NEXUS_PANEL} border-yellow-500/30`}>
                <h3 className="text-xl font-bold mb-4 text-yellow-300">Needs Attention</h3>
                <div className="space-y-2">
                  {displayOrders.filter(o => o.status === 'pending').map(order => (
                    <NexusListRow
                      key={order.id}
                      onClick={() => { setActiveSection('orders'); setSelectedOrder(order); }}
                      accentBorder="border-l-yellow-400"
                    >
                      <div className="flex-1 min-w-0">
                        <p className="font-semibold text-sm text-white">{order.subjectInfo.name}</p>
                        <p className="text-xs text-gray-400 mt-0.5">
                          {order.clientName} · {order.type.toUpperCase()}
                        </p>
                      </div>
                      <span className="text-xs text-yellow-400 font-bold shrink-0">NEEDS SCHEDULING →</span>
                    </NexusListRow>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* ═══ CLIENTS (CRM) ═══ */}
        {activeSection === 'clients' && !selectedClient && (
          <div className="space-y-6 max-w-7xl mx-auto">
            <div className="flex flex-wrap items-start justify-between gap-4">
              <div>
                <h1 className={NEXUS_TITLE}>Clients</h1>
                <p className={NEXUS_SUBTITLE}>
                  {clientsLoading ? 'Loading…' : `${displayClients.length} accounts`}
                </p>
              </div>
              <button type="button" onClick={() => setShowNewClientModal(true)} className={NEXUS_BTN_PRIMARY}>
                + Add Client
              </button>
            </div>
            <div className="flex flex-col gap-2">
              {displayClients.length === 0 && !clientsLoading && (
                <EmptyPanel title="No clients yet" hint="Clients appear from GET /prism/clients or from order client names." />
              )}
              {displayClients.map(client => {
                const statusCfg = client.status === 'active'
                  ? { bg: 'rgba(16,185,129,0.12)', color: '#6EE7B7' }
                  : client.status === 'inactive'
                  ? { bg: 'rgba(107,114,128,0.12)', color: '#9CA3AF' }
                  : { bg: 'rgba(234,179,8,0.12)', color: '#FCD34D' };
                return (
                  <button
                    key={client.id}
                    type="button"
                    onClick={() => setSelectedClient(client)}
                    className="w-full flex items-center justify-between p-5 bg-gradient-to-br from-gray-800 to-gray-900 border border-purple-500/20 rounded-xl hover:border-purple-500/40 transition-all text-left"
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
                  {selectedClient.portalLink ? (
                    <p className="text-sm font-mono">{window.location.origin}/client/{selectedClient.portalLink}</p>
                  ) : (
                    <p className="text-sm text-gray-500">No portal code — add portal_code in clients.json</p>
                  )}
                </div>
                {selectedClient.portalLink && (
                  <button
                    type="button"
                    onClick={() => copyPortalLink(selectedClient.portalLink)}
                    className="px-3 py-1.5 bg-gray-600 hover:bg-gray-500 rounded-lg text-xs font-semibold transition"
                  >
                    {portalCopied ? 'Copied ✓' : 'Copy Link'}
                  </button>
                )}
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
              {displayOrders.filter(o => o.clientName === selectedClient.name).map(order => (
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
                      <div style={{ marginBottom: 12, display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                        <a
                          href={`${process.env.REACT_APP_API_BASE || 'http://127.0.0.1:8000'}/nexus/qc/mco/breakdown.html?payer=HAP%20CareSource`}
                          target="_blank"
                          rel="noopener noreferrer"
                          style={{ fontSize: 12, color: '#A78BFA', fontWeight: 600 }}
                        >
                          📋 MCO QC Breakdown (9 pillars) ↗
                        </a>
                        <a
                          href={`${process.env.REACT_APP_API_BASE || 'http://127.0.0.1:8000'}/prism/nemt/satisfaction/mco-packet.html?payer=HAP%20CareSource`}
                          target="_blank"
                          rel="noopener noreferrer"
                          style={{ fontSize: 12, color: '#6EE7B7', fontWeight: 600 }}
                        >
                          ⭐ Member Trip Grade Report ↗
                        </a>
                      </div>
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
                            🗺️ Guest ride tracking link
                          </label>
                          <input
                            type="url"
                            value={rideTrackingInput}
                            onChange={(e) => setRideTrackingInput(e.target.value)}
                            placeholder="Paste tracking URL from dispatch dashboard (trip.uber.com / lyft…)"
                            disabled={!!nemtBusy || selectedOrder.status === 'completed'}
                            style={{ width: '100%', padding: '10px 12px', borderRadius: 8, border: '1px solid rgba(255,255,255,0.15)', background: '#0D0D12', color: '#F9FAFB', fontSize: 13, marginBottom: 8 }}
                          />
                          <button
                            type="button"
                            disabled={!!nemtBusy || selectedOrder.status === 'completed'}
                            onClick={handleSaveRideTracking}
                            style={{ width: '100%', padding: '10px 14px', borderRadius: 8, border: '1px solid rgba(255,255,255,0.2)', fontWeight: 600, fontSize: 13, color: '#E5E7EB', background: '#1F2937', cursor: nemtBusy ? 'wait' : 'pointer', opacity: nemtBusy || selectedOrder.status === 'completed' ? 0.6 : 1 }}
                          >
                            {nemtBusy === 'tracking' ? 'Saving…' : '📤 Save link → client portal'}
                          </button>
                          {selectedOrder.rideTrackingUrl && (
                            <a
                              href={selectedOrder.rideTrackingUrl}
                              target="_blank"
                              rel="noopener noreferrer"
                              style={{ display: 'inline-block', marginTop: 8, fontSize: 12, color: '#A78BFA' }}
                            >
                              🚗 Open current tracking link ↗
                            </a>
                          )}
                          <p style={{ fontSize: 11, color: '#6B7280', marginTop: 6, lineHeight: 1.4 }}>
                            Paste after dispatch. Member sees 🚗 Track live ride on portal.deedavis.biz — no app required.
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
                    {division.partnerPortals.slice(0, 4).map((portal) => (
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
                <p style={{ fontSize: 12, color: 'rgba(107,114,128,0.7)', marginTop: 2 }}>
                  {needsReviewCount} pending review · {scanbacksProp.length} total
                </p>
              </div>
              <div style={{ display: 'flex', gap: 6 }}>
                {([
                  { key: 'all' as const, label: 'All' },
                  { key: 'needs_review' as const, label: `Needs Review (${needsReviewCount})` },
                  { key: 'verified' as const, label: 'Verified' },
                ]).map((tab) => (
                  <button
                    key={tab.key}
                    type="button"
                    onClick={() => setScanbackFilter(tab.key)}
                    style={{
                      padding: '7px 14px',
                      borderRadius: 7,
                      fontSize: 12,
                      fontWeight: 500,
                      cursor: 'pointer',
                      background: scanbackFilter === tab.key ? 'rgba(234,179,8,0.12)' : 'rgba(255,255,255,0.05)',
                      color: scanbackFilter === tab.key ? '#FCD34D' : '#9CA3AF',
                      border: scanbackFilter === tab.key ? '1px solid rgba(234,179,8,0.25)' : '1px solid rgba(255,255,255,0.07)',
                    }}
                  >
                    {tab.label}
                  </button>
                ))}
              </div>
            </div>
            <div style={{ padding: 28, display: 'flex', flexDirection: 'column', gap: 8 }}>
              {filteredScanbacks.length === 0 && (
                <EmptyPanel title="No scanbacks in this division" hint="Orders with documentation uploads appear here after agents submit scanbacks." />
              )}
              {filteredScanbacks.map((scan) => {
                const uiStatus = normalizeScanbackUiStatus(scan.status);
                const needsReview = uiStatus === 'needs_review';
                const verified = uiStatus === 'verified';
                const statusLabel = verified ? 'Verified' : needsReview ? 'Needs Review' : scan.status;
                return (
                  <div key={scan.id} style={{ display: 'flex', alignItems: 'center', gap: 16, padding: '14px 18px', background: '#14141A', border: `1px solid ${needsReview ? 'rgba(234,179,8,0.25)' : 'rgba(255,255,255,0.06)'}`, borderRadius: 11 }}>
                    <div style={{ width: 42, height: 42, borderRadius: 10, background: needsReview ? 'rgba(234,179,8,0.1)' : verified ? 'rgba(16,185,129,0.1)' : 'rgba(255,255,255,0.05)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                      <svg width="18" height="18" fill="none" viewBox="0 0 24 24" stroke={needsReview ? '#FCD34D' : verified ? '#34D399' : '#9CA3AF'} strokeWidth="1.8"><path strokeLinecap="round" strokeLinejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>
                    </div>
                    <div style={{ flex: 1 }}>
                      <p style={{ fontWeight: 700, fontSize: 14, color: '#F9FAFB' }}>{scan.signer || scan.client}</p>
                      <p style={{ fontSize: 12, color: 'rgba(107,114,128,0.7)', marginTop: 2 }}>
                        {scan.orderId} &nbsp;·&nbsp; {scan.type} &nbsp;·&nbsp; {scan.uploadDate || '—'}
                        {scan.pages > 0 ? ` · ${scan.pages} pg` : ''}
                      </p>
                    </div>
                    <div style={{ textAlign: 'right' as const }}>
                      <p style={{ fontWeight: 700, fontSize: 14, color: needsReview ? '#FCD34D' : verified ? '#34D399' : '#9CA3AF' }}>{statusLabel}</p>
                      <p style={{ fontSize: 11, color: 'rgba(107,114,128,0.6)', marginTop: 2 }}>{scan.agent}</p>
                    </div>
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
              <p style={{ fontSize: 12, color: 'rgba(107,114,128,0.7)', marginTop: 2 }}>Live data from division orders</p>
            </div>

            {/* KPI ribbon */}
            <div style={{ display: 'flex', borderBottom: '1px solid rgba(255,255,255,0.05)', background: '#0A0A0F' }}>
              {[
                { label: 'Total Orders', value: String(displayOrders.length) },
                { label: 'Active', value: String(displayOrders.filter((o) => ['pending', 'scheduled', 'in_progress'].includes(o.status)).length) },
                { label: 'Completed', value: String(displayOrders.filter((o) => o.status === 'completed').length) },
                { label: 'Clients', value: String(displayClients.length) },
              ].map((s, i) => (
                <div key={s.label} style={{ flex: 1, padding: '16px 22px', borderRight: i < 3 ? '1px solid rgba(255,255,255,0.05)' : 'none' }}>
                  <p style={{ fontSize: 24, fontWeight: 800, color: '#F9FAFB', letterSpacing: -0.5 }}>{s.value}</p>
                  <p style={{ fontSize: 11, color: 'rgba(107,114,128,0.7)', marginTop: 3 }}>{s.label}</p>
                </div>
              ))}
            </div>

            <div style={{ padding: 28, display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20 }}>
              {/* Orders by Type bar chart */}
              <div style={{ background: '#14141A', border: '1px solid rgba(255,255,255,0.06)', borderRadius: 14, padding: 22 }}>
                <p style={{ fontSize: 12, fontWeight: 600, color: 'rgba(156,163,175,0.7)', textTransform: 'uppercase', letterSpacing: 0.7, marginBottom: 20 }}>Orders by Type</p>
                {ordersByType.length === 0 ? (
                  <EmptyPanel title="No orders to chart" />
                ) : (
                  <div style={{ display: 'flex', alignItems: 'flex-end', justifyContent: 'space-around', height: 160, gap: 10, paddingBottom: 8 }}>
                    {ordersByType.map(([label, count]) => {
                      const max = ordersByType[0][1];
                      const height = Math.max(8, Math.round((count / max) * 120));
                      return (
                        <div key={label} style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 6 }}>
                          <span style={{ fontSize: 10, color: '#9CA3AF' }}>{count}</span>
                          <div style={{ width: '100%', borderRadius: '4px 4px 0 0', backgroundColor: division.solid, height: `${height}px`, opacity: 0.85 }} />
                          <span style={{ fontSize: 10, color: 'rgba(107,114,128,0.7)', textAlign: 'center' }}>{label}</span>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>

              {/* Revenue — VERTEX integration */}
              <div style={{ background: '#14141A', border: '1px solid rgba(255,255,255,0.06)', borderRadius: 14, padding: 22 }}>
                <p style={{ fontSize: 12, fontWeight: 600, color: 'rgba(156,163,175,0.7)', textTransform: 'uppercase', letterSpacing: 0.7, marginBottom: 20 }}>Billing</p>
                <div style={{ height: 160, display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column', gap: 8 }}>
                  <p style={{ fontSize: 28, fontWeight: 800, color: '#34D399' }}>{vertexInvoices.length}</p>
                  <p style={{ fontSize: 12, color: 'rgba(107,114,128,0.7)' }}>VERTEX invoice{vertexInvoices.length === 1 ? '' : 's'} linked from completed orders</p>
                </div>
              </div>

              {/* Top clients */}
              <div style={{ background: '#14141A', border: '1px solid rgba(255,255,255,0.06)', borderRadius: 14, padding: 22, gridColumn: '1 / -1' }}>
                <p style={{ fontSize: 12, fontWeight: 600, color: 'rgba(156,163,175,0.7)', textTransform: 'uppercase', letterSpacing: 0.7, marginBottom: 16 }}>Top Clients by Volume</p>
                {topClientsByVolume.length === 0 ? (
                  <EmptyPanel title="No client volume yet" hint="Complete orders to see client rankings." />
                ) : (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                    {topClientsByVolume.map((c) => (
                      <div key={c.name} style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
                        <p style={{ fontSize: 13, fontWeight: 600, color: '#E5E7EB', width: 220, flexShrink: 0 }}>{c.name}</p>
                        <div style={{ flex: 1, height: 6, background: 'rgba(255,255,255,0.06)', borderRadius: 3 }}>
                          <div style={{ width: `${c.pct}%`, height: '100%', background: division.solid, borderRadius: 3 }} />
                        </div>
                        <p style={{ fontSize: 12, color: 'rgba(107,114,128,0.7)', width: 40, textAlign: 'right' as const }}>{c.orders}</p>
                      </div>
                    ))}
                  </div>
                )}
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
                <p style={{ fontSize: 12, color: 'rgba(107,114,128,0.7)', marginTop: 2 }}>
                  {invoicesLoading ? 'Loading from VERTEX…' : 'Live VERTEX invoice data'}
                </p>
              </div>
              <button
                type="button"
                onClick={() => {
                  setInvoicesLoading(true);
                  const ids = Array.from(new Set(displayOrders.map((o) => o.vertexInvoiceId).filter(Boolean))) as string[];
                  const clientNames = Array.from(new Set(displayClients.map((c) => c.name).filter(Boolean)));
                  api.post('/prism/billing/invoices', { ids, client_names: clientNames }).then((data: { invoices?: VertexInvoiceRow[]; summary?: VertexInvoiceSummary }) => {
                    setVertexInvoiceRows(data.invoices || []);
                    setVertexInvoiceSummary(data.summary || null);
                  }).finally(() => setInvoicesLoading(false));
                }}
                style={{ padding: '9px 18px', background: 'rgba(255,255,255,0.08)', color: '#E5E7EB', borderRadius: 9, fontWeight: 600, fontSize: 13, border: '1px solid rgba(255,255,255,0.12)', cursor: 'pointer' }}
              >
                ↻ Refresh
              </button>
            </div>

            {/* Summary ribbon */}
            <div style={{ display: 'flex', borderBottom: '1px solid rgba(255,255,255,0.05)', background: '#0A0A0F' }}>
              {[
                { label: 'Collected', value: fmtUsd(vertexInvoiceSummary?.collected ?? 0), bg: 'rgba(16,185,129,0.08)', border: 'rgba(16,185,129,0.15)', color: '#34D399' },
                { label: 'Pending', value: fmtUsd(vertexInvoiceSummary?.pending ?? 0), bg: 'rgba(234,179,8,0.08)', border: 'rgba(234,179,8,0.15)', color: '#FCD34D' },
                { label: 'Overdue', value: fmtUsd(vertexInvoiceSummary?.overdue ?? 0), bg: 'rgba(239,68,68,0.08)', border: 'rgba(239,68,68,0.15)', color: '#FCA5A5' },
              ].map((s, i) => (
                <div key={s.label} style={{ flex: 1, padding: '18px 28px', borderRight: i < 2 ? '1px solid rgba(255,255,255,0.05)' : 'none', background: s.bg, borderBottom: `2px solid ${s.border}` }}>
                  <p style={{ fontSize: 24, fontWeight: 800, color: s.color, letterSpacing: -0.5 }}>{s.value}</p>
                  <p style={{ fontSize: 11, color: 'rgba(107,114,128,0.7)', marginTop: 3 }}>{s.label}</p>
                </div>
              ))}
            </div>

            <div style={{ padding: 28 }}>
              <p style={{ fontSize: 11, fontWeight: 600, color: 'rgba(156,163,175,0.6)', textTransform: 'uppercase', letterSpacing: 0.8, marginBottom: 14 }}>
                VERTEX Invoices · {vertexInvoiceSummary?.count ?? vertexInvoiceRows.length} total · {fmtUsd(vertexInvoiceSummary?.total_billed ?? 0)} billed
              </p>
              {invoicesLoading && vertexInvoiceRows.length === 0 ? (
                <EmptyPanel title="Loading VERTEX invoices…" />
              ) : vertexInvoiceRows.length === 0 ? (
                <EmptyPanel title="No VERTEX invoices for this division" hint="Complete NEMT trips or link client names to see invoices from Airtable VERTEX INVOICES." />
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                  {vertexInvoiceRows.map((inv) => {
                    const statusKey = (inv.status || 'Unpaid').toLowerCase();
                    const cfg = statusKey === 'paid'
                      ? { bg: 'rgba(16,185,129,0.12)', color: '#34D399' }
                      : statusKey === 'overdue'
                      ? { bg: 'rgba(239,68,68,0.12)', color: '#FCA5A5' }
                      : { bg: 'rgba(234,179,8,0.12)', color: '#FCD34D' };
                    return (
                      <div key={inv.record_id} style={{ display: 'flex', alignItems: 'center', gap: 16, padding: '14px 18px', background: '#14141A', border: '1px solid rgba(255,255,255,0.06)', borderRadius: 11 }}>
                        <div style={{ flex: 1, minWidth: 0 }}>
                          <p style={{ fontWeight: 700, fontSize: 14, color: '#F9FAFB' }}>{inv.invoice_number}</p>
                          <p style={{ fontSize: 12, color: 'rgba(107,114,128,0.7)', marginTop: 2 }}>
                            {inv.client_name} &nbsp;·&nbsp; {inv.date || '—'}
                            {inv.due_date ? ` · due ${inv.due_date}` : ''}
                          </p>
                        </div>
                        <div style={{ textAlign: 'right' as const }}>
                          <p style={{ fontWeight: 800, fontSize: 16, color: '#F9FAFB' }}>{fmtUsd(inv.amount)}</p>
                          {inv.balance_due > 0 && inv.balance_due < inv.amount && (
                            <p style={{ fontSize: 11, color: 'rgba(107,114,128,0.6)', marginTop: 2 }}>Due {fmtUsd(inv.balance_due)}</p>
                          )}
                        </div>
                        <span style={{ ...cfg, padding: '3px 10px', borderRadius: 6, fontSize: 10, fontWeight: 700, letterSpacing: 0.3 }}>
                          {(inv.status || 'UNPAID').toUpperCase()}
                        </span>
                        {inv.pdf_path && (
                          <a
                            href={`${API_BASE}${inv.pdf_path}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            style={{ padding: '7px 14px', borderRadius: 7, background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(255,255,255,0.08)', color: '#D1D5DB', fontSize: 12, textDecoration: 'none' }}
                          >
                            PDF
                          </a>
                        )}
                      </div>
                    );
                  })}
                </div>
              )}
              {vertexInvoices.length > 0 && vertexInvoiceRows.length === 0 && !invoicesLoading && (
                <p style={{ fontSize: 11, color: 'rgba(107,114,128,0.5)', marginTop: 16 }}>
                  {vertexInvoices.length} order(s) have linked invoice IDs — VERTEX lookup returned no rows (check Airtable connection).
                </p>
              )}
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
                      {displayClients.length === 0 ? (
                        <option value="">No clients — add via API or create order</option>
                      ) : (
                        displayClients.map(c => <option key={c.id} value={c.id}>{c.name}</option>)
                      )}
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

        {activeSection === 'revenue' && isNemtDivision && (
          <div style={{ flex: 1, overflow: 'auto' }}>
            <HideSnpRevenueModel embedded onNavigate={onNavigate} />
          </div>
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
