import React, { useState } from 'react';

interface PRISMHubProps {
  divisions: { id: string; name: string; icon: string; color: string; solid: string }[];
  /** Per-division count of orders needing ops attention */
  divisionNotifications?: Record<string, number>;
  onSelectDivision: (id: string) => void;
  onNewOrder: () => void;
}

// ─── Mock data ───────────────────────────────────────────────────────────────
const SCHEDULE = [
  { id: '1', time: '10:00 AM', subject: 'James Wilson',   type: 'DOT Drug Test',   client: 'ABC Trucking',        status: 'scheduled',   divId: 'drug_testing',      color: '#3B82F6' },
  { id: '2', time: '2:30 PM',  subject: 'Robert Chen',    type: 'Post-Accident',   client: 'ABC Trucking',        status: 'in_progress', divId: 'drug_testing',      color: '#8B5CF6' },
  { id: '3', time: '3:00 PM',  subject: 'Rx Delivery',    type: 'Same-Day Rx',     client: 'Walgreens #1234',     status: 'scheduled',   divId: 'pharmacy_courier',  color: '#10B981' },
  { id: '4', time: '4:15 PM',  subject: 'Maria Garcia',   type: 'Random Selection', client: 'Metro Transit',      status: 'scheduled',   divId: 'drug_testing',      color: '#06B6D4' },
];

const ATTENTION = [
  { id: 'n1', subject: 'Patricia Moore', issue: 'Awaiting scheduling', client: 'Metro Transit',     divId: 'drug_testing' },
  { id: 'n2', subject: 'Lab Pickup',     issue: 'No driver assigned',  client: 'Quest Diagnostics', divId: 'medical_courier' },
];

// ─── SVG icon helpers ─────────────────────────────────────────────────────────
const IconPlus = () => (
  <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2.5">
    <path strokeLinecap="round" strokeLinejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
  </svg>
);
const IconChevron = () => (
  <svg width="12" height="12" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
    <path strokeLinecap="round" strokeLinejoin="round" d="M8.25 4.5l7.5 7.5-7.5 7.5" />
  </svg>
);

const IconBell = () => (
  <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
    <path strokeLinecap="round" strokeLinejoin="round" d="M14.857 17.082a23.848 23.848 0 005.454-1.31A8.967 8.967 0 0118 9.75V9A6 6 0 006 9v.75a8.967 8.967 0 01-2.312 6.022c1.733.64 3.56 1.085 5.455 1.31m5.714 0a24.255 24.255 0 01-5.714 0m5.714 0a3 3 0 11-5.714 0" />
  </svg>
);

const NotificationBell: React.FC<{ count: number; accent: string }> = ({ count, accent }) => {
  if (count <= 0) return null;
  const label = count > 99 ? '99+' : String(count);
  return (
    <span
      title={`${count} order${count === 1 ? '' : 's'} need attention`}
      style={{ position: 'relative', display: 'inline-flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0, color: accent }}
    >
      <IconBell />
      <span
        style={{
          position: 'absolute',
          top: -7,
          right: -8,
          minWidth: 16,
          height: 16,
          padding: '0 4px',
          borderRadius: 999,
          background: accent,
          color: '#fff',
          fontSize: 9,
          fontWeight: 800,
          lineHeight: '16px',
          textAlign: 'center',
          boxShadow: '0 0 0 2px #14141A',
        }}
      >
        {label}
      </span>
    </span>
  );
};

// ─── Status pill ──────────────────────────────────────────────────────────────
const StatusPill: React.FC<{ status: string }> = ({ status }) => {
  const cfg: Record<string, { label: string; bg: string; color: string }> = {
    in_progress: { label: 'Active',     bg: 'rgba(139,92,246,0.15)', color: '#A78BFA' },
    scheduled:   { label: 'Scheduled',  bg: 'rgba(55,65,81,0.6)',    color: '#9CA3AF' },
    pending:     { label: 'Pending',    bg: 'rgba(234,179,8,0.12)',  color: '#FCD34D' },
    completed:   { label: 'Done',       bg: 'rgba(16,185,129,0.12)', color: '#34D399' },
  };
  const c = cfg[status] || cfg.scheduled;
  return (
    <span style={{ padding: '3px 9px', borderRadius: 6, fontSize: 10, fontWeight: 700, background: c.bg, color: c.color, letterSpacing: 0.3 }}>
      {c.label}
    </span>
  );
};

const PRISMHub: React.FC<PRISMHubProps> = ({ divisions, divisionNotifications = {}, onSelectDivision, onNewOrder }) => {
  const [search, setSearch] = useState('');
  const filtered = search ? divisions.filter(d => d.name.toLowerCase().includes(search.toLowerCase())) : divisions;
  const totalAlerts = Object.values(divisionNotifications).reduce((sum, n) => sum + n, 0);

  return (
    <div style={{ minHeight: '100vh', background: '#0D0D12', color: '#E5E7EB', fontFamily: '-apple-system, BlinkMacSystemFont, "Inter", sans-serif' }}>

      {/* ── TOP BAR ── */}
      <div style={{ borderBottom: '1px solid rgba(255,255,255,0.06)', background: '#0A0A0F' }}>
        <div style={{ maxWidth: 1140, margin: '0 auto', padding: '0 36px', height: 56, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <div style={{ width: 28, height: 28, borderRadius: 7, background: '#F97316', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <span style={{ color: '#fff', fontWeight: 900, fontSize: 11 }}>P</span>
            </div>
            <span style={{ fontWeight: 700, fontSize: 15, color: '#F9FAFB', letterSpacing: -0.3 }}>PRISM</span>
            <span style={{ fontSize: 11, color: 'rgba(156,163,175,0.6)', paddingLeft: 6, borderLeft: '1px solid rgba(255,255,255,0.08)' }}>Field Service Command Center</span>
          </div>
          <button
            onClick={onNewOrder}
            style={{ display: 'flex', alignItems: 'center', gap: 7, padding: '8px 16px', background: '#F97316', color: '#fff', borderRadius: 9, fontWeight: 600, fontSize: 13, border: 'none', cursor: 'pointer' }}
          >
            <IconPlus /> New Order
          </button>
        </div>
      </div>

      {/* ── KPI RIBBON ── */}
      <div style={{ borderBottom: '1px solid rgba(255,255,255,0.05)', background: '#0D0D12' }}>
        <div style={{ maxWidth: 1140, margin: '0 auto', padding: '0 36px', display: 'flex', gap: 0 }}>
          {[
            { label: 'Scheduled Today', value: SCHEDULE.filter(s => s.status === 'scheduled').length,   color: '#60A5FA' },
            { label: 'In Progress',     value: SCHEDULE.filter(s => s.status === 'in_progress').length, color: '#A78BFA' },
            { label: 'Needs Attention', value: totalAlerts,                                        color: '#FCD34D' },
            { label: 'Active Clients',  value: 12,                                                      color: '#34D399' },
            { label: 'MTD Revenue',     value: '$8,450',                                                color: '#FB923C' },
          ].map((kpi, i) => (
            <div key={kpi.label} style={{ padding: '14px 28px', borderRight: i < 4 ? '1px solid rgba(255,255,255,0.05)' : 'none', minWidth: 140 }}>
              <p style={{ fontSize: 20, fontWeight: 800, color: kpi.color, letterSpacing: -0.5 }}>{kpi.value}</p>
              <p style={{ fontSize: 11, color: 'rgba(156,163,175,0.7)', marginTop: 2 }}>{kpi.label}</p>
            </div>
          ))}
        </div>
      </div>

      {/* ── MAIN ── */}
      <div style={{ maxWidth: 1140, margin: '0 auto', padding: '32px 36px' }}>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 340px', gap: 28 }}>

          {/* LEFT: Schedule */}
          <div>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16 }}>
              <p style={{ fontSize: 12, fontWeight: 600, color: 'rgba(156,163,175,0.8)', textTransform: 'uppercase', letterSpacing: 0.8 }}>Today's Schedule</p>
              <span style={{ fontSize: 11, color: 'rgba(107,114,128,0.7)' }}>{new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'short', day: 'numeric' })}</span>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
              {SCHEDULE.map(item => (
                <button
                  key={item.id}
                  onClick={() => onSelectDivision(item.divId)}
                  style={{ width: '100%', display: 'flex', alignItems: 'center', gap: 14, padding: '14px 18px', background: '#14141A', border: '1px solid rgba(255,255,255,0.06)', borderRadius: 12, cursor: 'pointer', textAlign: 'left' as const, transition: 'border-color 0.15s, background 0.15s' }}
                  onMouseEnter={e => { e.currentTarget.style.background = '#1A1A22'; e.currentTarget.style.borderColor = 'rgba(255,255,255,0.1)'; }}
                  onMouseLeave={e => { e.currentTarget.style.background = '#14141A'; e.currentTarget.style.borderColor = 'rgba(255,255,255,0.06)'; }}
                >
                  <span style={{ width: 64, fontSize: 12, fontWeight: 600, color: item.status === 'in_progress' ? '#A78BFA' : 'rgba(156,163,175,0.7)', flexShrink: 0 }}>{item.time}</span>
                  <div style={{ width: 3, height: 32, borderRadius: 2, background: item.color, flexShrink: 0 }} />
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <p style={{ fontWeight: 600, color: '#F9FAFB', fontSize: 14 }}>{item.subject}</p>
                    <p style={{ fontSize: 12, color: 'rgba(107,114,128,0.9)', marginTop: 2 }}>{item.type} &nbsp;·&nbsp; {item.client}</p>
                  </div>
                  <StatusPill status={item.status} />
                  <IconChevron />
                </button>
              ))}
              {SCHEDULE.length === 0 && (
                <div style={{ padding: '40px 18px', textAlign: 'center', background: '#14141A', borderRadius: 12, border: '1px solid rgba(255,255,255,0.06)' }}>
                  <p style={{ color: 'rgba(107,114,128,0.6)', fontSize: 13 }}>No work scheduled today</p>
                </div>
              )}
            </div>
          </div>

          {/* RIGHT: Attention + Revenue */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
            {/* Needs Attention */}
            {ATTENTION.length > 0 && (
              <div>
                <p style={{ fontSize: 11, fontWeight: 600, color: '#FCD34D', textTransform: 'uppercase', letterSpacing: 0.8, marginBottom: 10 }}>Needs Attention</p>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                  {ATTENTION.map(a => (
                    <button
                      key={a.id}
                      onClick={() => onSelectDivision(a.divId)}
                      style={{ width: '100%', display: 'flex', alignItems: 'center', gap: 12, padding: '13px 16px', background: 'rgba(234,179,8,0.05)', border: '1px solid rgba(234,179,8,0.2)', borderRadius: 10, cursor: 'pointer', textAlign: 'left' as const }}
                    >
                      <div style={{ flex: 1 }}>
                        <p style={{ fontWeight: 600, color: '#F9FAFB', fontSize: 13 }}>{a.subject}</p>
                        <p style={{ fontSize: 11, color: '#FCD34D', marginTop: 2 }}>{a.issue} · {a.client}</p>
                      </div>
                      <IconChevron />
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Revenue card */}
            <div style={{ background: '#14141A', border: '1px solid rgba(255,255,255,0.06)', borderRadius: 14, padding: 22 }}>
              <p style={{ fontSize: 11, fontWeight: 600, color: 'rgba(156,163,175,0.6)', textTransform: 'uppercase', letterSpacing: 0.8, marginBottom: 16 }}>This Week</p>
              <p style={{ fontSize: 28, fontWeight: 800, color: '#F9FAFB', letterSpacing: -0.5 }}>$4,250</p>
              <p style={{ fontSize: 11, color: 'rgba(107,114,128,0.7)', marginTop: 4 }}>Revenue generated</p>
              <div style={{ display: 'flex', gap: 0, marginTop: 18, borderTop: '1px solid rgba(255,255,255,0.05)', paddingTop: 16 }}>
                {[{ v: '18', l: 'Orders' }, { v: '94%', l: 'On-time' }, { v: '4', l: 'Clients' }].map((x, i) => (
                  <div key={x.l} style={{ flex: 1, textAlign: 'center' as const, borderRight: i < 2 ? '1px solid rgba(255,255,255,0.05)' : 'none' }}>
                    <p style={{ fontWeight: 700, fontSize: 18, color: '#F9FAFB' }}>{x.v}</p>
                    <p style={{ fontSize: 11, color: 'rgba(107,114,128,0.7)', marginTop: 2 }}>{x.l}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* ── DIVISIONS ── */}
        <div style={{ marginTop: 40, paddingTop: 32, borderTop: '1px solid rgba(255,255,255,0.05)' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 18 }}>
            <p style={{ fontSize: 12, fontWeight: 600, color: 'rgba(156,163,175,0.8)', textTransform: 'uppercase', letterSpacing: 0.8 }}>Divisions</p>
            <input
              type="text"
              placeholder="Search..."
              value={search}
              onChange={e => setSearch(e.target.value)}
              style={{ padding: '7px 13px', borderRadius: 8, border: '1px solid rgba(255,255,255,0.08)', background: '#14141A', color: '#F9FAFB', fontSize: 12, outline: 'none', width: 180 }}
            />
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(160px, 1fr))', gap: 10 }}>
            {filtered.map(div => {
              const alertCount = divisionNotifications[div.id] || 0;
              return (
              <button
                key={div.id}
                onClick={() => onSelectDivision(div.id)}
                style={{
                  display: 'flex', alignItems: 'center', gap: 12, padding: '14px 16px', background: '#14141A',
                  border: `1px solid ${alertCount > 0 ? div.color + '55' : 'rgba(255,255,255,0.06)'}`,
                  borderRadius: 12, cursor: 'pointer', textAlign: 'left' as const, transition: 'all 0.15s',
                }}
                onMouseEnter={e => { e.currentTarget.style.background = '#1A1A22'; e.currentTarget.style.borderColor = (div.color || '#F97316') + '40'; }}
                onMouseLeave={e => { e.currentTarget.style.background = '#14141A'; e.currentTarget.style.borderColor = alertCount > 0 ? div.color + '55' : 'rgba(255,255,255,0.06)'; }}
              >
                <span style={{ fontSize: 20 }}>{div.icon}</span>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <p style={{ fontWeight: 600, fontSize: 13, color: '#F9FAFB', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{div.name}</p>
                </div>
                <NotificationBell count={alertCount} accent={div.solid || div.color || '#F97316'} />
                <IconChevron />
              </button>
            );})}
          </div>
        </div>
      </div>
    </div>
  );
};

export default PRISMHub;
