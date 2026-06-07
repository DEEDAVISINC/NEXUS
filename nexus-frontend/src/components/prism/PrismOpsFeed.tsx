import React, { useMemo } from 'react';

export interface PrismNotification {
  id: string;
  type: string;
  icon?: string;
  title: string;
  message: string;
  severity?: string;
  target?: string;
  order_id?: string;
  read?: boolean;
  created_at?: string;
  timestamp?: string;
  metadata?: Record<string, unknown>;
}

interface PrismOpsFeedProps {
  notifications: PrismNotification[];
  unreadCount: number;
  open: boolean;
  onToggle: () => void;
  onMarkAllRead: () => void;
  onMarkRead: (id: string) => void;
  onSelectNotification?: (n: PrismNotification) => void;
  accent?: string;
  /** Compact = bell only; full = bell + inline activity strip */
  variant?: 'compact' | 'full';
}

const SEVERITY_COLORS: Record<string, string> = {
  critical: '#EF4444',
  high: '#F97316',
  warning: '#EAB308',
  medium: '#60A5FA',
  info: '#9CA3AF',
  success: '#10B981',
};

function notifTime(n: PrismNotification): string {
  const raw = n.created_at || n.timestamp;
  if (!raw) return '';
  const d = new Date(raw);
  if (Number.isNaN(d.getTime())) return '';
  const diff = Date.now() - d.getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return 'Just now';
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}

const IconBell = () => (
  <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
    <path strokeLinecap="round" strokeLinejoin="round" d="M14.857 17.082a23.848 23.848 0 005.454-1.31A8.967 8.967 0 0118 9.75V9A6 6 0 006 9v.75a8.967 8.967 0 01-2.312 6.022c1.733.64 3.56 1.085 5.455 1.31m5.714 0a24.255 24.255 0 01-5.714 0m5.714 0a3 3 0 11-5.714 0" />
  </svg>
);

const PrismOpsFeed: React.FC<PrismOpsFeedProps> = ({
  notifications,
  unreadCount,
  open,
  onToggle,
  onMarkAllRead,
  onMarkRead,
  onSelectNotification,
  accent = '#F97316',
  variant = 'compact',
}) => {
  const recent = useMemo(
    () => notifications.slice(0, variant === 'full' ? 8 : 30),
    [notifications, variant]
  );

  const unreadRecent = useMemo(() => recent.filter((n) => !n.read), [recent]);

  return (
    <>
      <button
        type="button"
        onClick={onToggle}
        title="Ops notifications"
        style={{
          position: 'relative',
          display: 'flex',
          alignItems: 'center',
          gap: 8,
          padding: '8px 14px',
          background: open ? 'rgba(255,255,255,0.08)' : 'rgba(255,255,255,0.04)',
          border: '1px solid rgba(255,255,255,0.1)',
          borderRadius: 9,
          color: '#E5E7EB',
          fontSize: 13,
          fontWeight: 600,
          cursor: 'pointer',
        }}
      >
        <IconBell />
        Ops
        {unreadCount > 0 && (
          <span
            style={{
              minWidth: 18,
              height: 18,
              padding: '0 5px',
              borderRadius: 999,
              background: accent,
              color: '#fff',
              fontSize: 10,
              fontWeight: 800,
              lineHeight: '18px',
              textAlign: 'center',
            }}
          >
            {unreadCount > 99 ? '99+' : unreadCount}
          </span>
        )}
      </button>

      {variant === 'full' && unreadRecent.length > 0 && !open && (
        <div style={{ marginTop: 12, display: 'flex', flexDirection: 'column', gap: 6 }}>
          {unreadRecent.slice(0, 3).map((n) => (
            <button
              key={n.id}
              type="button"
              onClick={() => {
                onMarkRead(n.id);
                onSelectNotification?.(n);
              }}
              style={{
                width: '100%',
                textAlign: 'left',
                padding: '10px 12px',
                background: 'rgba(249,115,22,0.06)',
                border: '1px solid rgba(249,115,22,0.15)',
                borderRadius: 8,
                cursor: 'pointer',
              }}
            >
              <p style={{ fontSize: 12, fontWeight: 600, color: '#F9FAFB' }}>
                {n.icon ? `${n.icon} ` : ''}{n.title}
              </p>
              <p style={{ fontSize: 11, color: 'rgba(156,163,175,0.9)', marginTop: 2 }}>{n.message}</p>
            </button>
          ))}
        </div>
      )}

      {open && (
        <>
          <div
            role="presentation"
            onClick={onToggle}
            style={{
              position: 'fixed',
              inset: 0,
              background: 'rgba(0,0,0,0.45)',
              zIndex: 60,
            }}
          />
          <div
            style={{
              position: 'fixed',
              top: 0,
              right: 0,
              width: 400,
              maxWidth: '92vw',
              height: '100vh',
              background: '#1C1C26',
              borderLeft: '2px solid rgba(255,255,255,0.12)',
              zIndex: 70,
              display: 'flex',
              flexDirection: 'column',
              boxShadow: '-8px 0 32px rgba(0,0,0,0.4)',
            }}
          >
            <div
              style={{
                padding: '18px 20px',
                borderBottom: '1px solid rgba(255,255,255,0.06)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
              }}
            >
              <div>
                <h2 style={{ fontSize: 18, fontWeight: 800, color: '#FFFFFF' }}>Ops Feed</h2>
                <p style={{ fontSize: 13, color: '#D1D5DB', marginTop: 4 }}>
                  Intake · voice · email · queue events
                </p>
              </div>
              <div style={{ display: 'flex', gap: 8 }}>
                {unreadCount > 0 && (
                  <button
                    type="button"
                    onClick={onMarkAllRead}
                    style={{
                      fontSize: 11,
                      fontWeight: 600,
                      color: accent,
                      background: 'transparent',
                      border: 'none',
                      cursor: 'pointer',
                    }}
                  >
                    Mark all read
                  </button>
                )}
                <button
                  type="button"
                  onClick={onToggle}
                  style={{
                    width: 28,
                    height: 28,
                    borderRadius: 6,
                    border: '1px solid rgba(255,255,255,0.1)',
                    background: 'transparent',
                    color: '#9CA3AF',
                    cursor: 'pointer',
                  }}
                >
                  ✕
                </button>
              </div>
            </div>

            <div style={{ flex: 1, overflowY: 'auto', padding: '12px 16px' }}>
              {recent.length === 0 ? (
                <div style={{ padding: '48px 16px', textAlign: 'center' }}>
                  <p style={{ fontSize: 13, color: 'rgba(107,114,128,0.8)' }}>No ops events yet</p>
                  <p style={{ fontSize: 11, color: 'rgba(107,114,128,0.6)', marginTop: 8 }}>
                    New orders, voice intake, and status changes appear here in real time.
                  </p>
                </div>
              ) : (
                recent.map((n) => {
                  const sev = n.severity || 'info';
                  const barColor = SEVERITY_COLORS[sev] || SEVERITY_COLORS.info;
                  return (
                    <button
                      key={n.id}
                      type="button"
                      onClick={() => {
                        if (!n.read) onMarkRead(n.id);
                        onSelectNotification?.(n);
                      }}
                      style={{
                        width: '100%',
                        textAlign: 'left',
                        display: 'flex',
                        gap: 12,
                        padding: '12px 10px',
                        marginBottom: 6,
                        background: n.read ? 'transparent' : 'rgba(255,255,255,0.03)',
                        border: '1px solid rgba(255,255,255,0.05)',
                        borderRadius: 10,
                        cursor: 'pointer',
                        opacity: n.read ? 0.75 : 1,
                      }}
                    >
                      <div
                        style={{
                          width: 3,
                          borderRadius: 2,
                          background: barColor,
                          flexShrink: 0,
                          alignSelf: 'stretch',
                        }}
                      />
                      <div style={{ flex: 1, minWidth: 0 }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', gap: 8 }}>
                          <p style={{ fontSize: 15, fontWeight: 700, color: '#FFFFFF' }}>
                            {n.icon ? `${n.icon} ` : ''}{n.title}
                          </p>
                          <span style={{ fontSize: 11, color: '#D1D5DB', flexShrink: 0 }}>
                            {notifTime(n)}
                          </span>
                        </div>
                        <p
                          style={{
                            fontSize: 14,
                            color: '#E5E7EB',
                            marginTop: 6,
                            lineHeight: 1.4,
                          }}
                        >
                          {n.message}
                        </p>
                        {n.order_id && (
                          <p
                            style={{
                              fontSize: 13,
                              fontFamily: 'ui-monospace, monospace',
                              color: accent,
                              marginTop: 8,
                              fontWeight: 700,
                            }}
                          >
                            {n.order_id} →
                          </p>
                        )}
                      </div>
                    </button>
                  );
                })
              )}
            </div>
          </div>
        </>
      )}
    </>
  );
};

export default PrismOpsFeed;
