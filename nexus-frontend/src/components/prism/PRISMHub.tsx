import React, { useState } from 'react';
import PrismOpsFeed, { PrismNotification } from './PrismOpsFeed';
import {
  NEXUS_SHELL_PAGE,
  NEXUS_SHELL_PAD,
  NEXUS_CONTAINER,
  NEXUS_TITLE,
  NEXUS_SUBTITLE,
  NEXUS_BTN_PRIMARY,
  NEXUS_BTN_SECONDARY,
  NexusMetricCard,
  NexusPanel,
  NexusListRow,
} from '../shared/NexusDashboardShell';

export interface HubScheduleItem {
  id: string;
  time: string;
  subject: string;
  type: string;
  client: string;
  status: 'scheduled' | 'in_progress' | 'pending' | 'completed';
  divId: string;
  color: string;
}

interface PRISMHubProps {
  divisions: { id: string; name: string; icon: string; color: string; solid: string }[];
  todaySchedule?: HubScheduleItem[];
  divisionNotifications?: Record<string, number>;
  opsNotifications?: PrismNotification[];
  opsUnreadCount?: number;
  opsFeedOpen?: boolean;
  onToggleOpsFeed?: () => void;
  onMarkOpsRead?: (id: string) => void;
  onMarkAllOpsRead?: () => void;
  onOpsNotificationClick?: (n: PrismNotification) => void;
  onSelectDivision: (id: string) => void;
  onNewOrder: () => void;
  onBackToNexus?: () => void;
}

const StatusPill: React.FC<{ status: string }> = ({ status }) => {
  const cfg: Record<string, string> = {
    in_progress: 'bg-purple-500/15 text-purple-300',
    scheduled: 'bg-gray-600/40 text-gray-300',
    pending: 'bg-yellow-500/15 text-yellow-300',
    completed: 'bg-green-500/15 text-green-300',
  };
  const labels: Record<string, string> = {
    in_progress: 'Active',
    scheduled: 'Scheduled',
    pending: 'Pending',
    completed: 'Done',
  };
  const cls = cfg[status] || cfg.scheduled;
  return (
    <span className={`px-2.5 py-1 rounded-md text-[10px] font-bold tracking-wide ${cls}`}>
      {labels[status] || 'Scheduled'}
    </span>
  );
};

const PRISMHub: React.FC<PRISMHubProps> = ({
  divisions,
  todaySchedule = [],
  divisionNotifications = {},
  opsNotifications = [],
  opsUnreadCount = 0,
  opsFeedOpen = false,
  onToggleOpsFeed,
  onMarkOpsRead,
  onMarkAllOpsRead,
  onOpsNotificationClick,
  onSelectDivision,
  onNewOrder,
  onBackToNexus,
}) => {
  const [search, setSearch] = useState('');
  const filtered = search
    ? divisions.filter((d) => d.name.toLowerCase().includes(search.toLowerCase()))
    : divisions;
  const totalAlerts = Object.values(divisionNotifications).reduce((sum, n) => sum + n, 0);
  const unreadOps = opsNotifications.filter((n) => !n.read);
  const scheduledToday = todaySchedule.filter(
    (s) => s.status === 'scheduled' || s.status === 'pending'
  ).length;
  const inProgress = todaySchedule.filter((s) => s.status === 'in_progress').length;

  return (
    <div className={`${NEXUS_SHELL_PAGE} ${NEXUS_SHELL_PAD}`}>
      {/* Header — VERTEX-style */}
      <div className="flex flex-wrap items-start justify-between gap-4 mb-8">
        <div>
          <h1 className={NEXUS_TITLE}>⚡ PRISM Dashboard</h1>
          <p className={NEXUS_SUBTITLE}>Field Service Command Center — dispatch, QC, and delivery</p>
        </div>
        <div className="flex items-center gap-3 flex-wrap">
          {onToggleOpsFeed && onMarkOpsRead && onMarkAllOpsRead && (
            <PrismOpsFeed
              notifications={opsNotifications}
              unreadCount={opsUnreadCount}
              open={opsFeedOpen}
              onToggle={onToggleOpsFeed}
              onMarkRead={onMarkOpsRead}
              onMarkAllRead={onMarkAllOpsRead}
              onSelectNotification={onOpsNotificationClick}
            />
          )}
          <button type="button" onClick={onNewOrder} className={NEXUS_BTN_PRIMARY}>
            + New Order
          </button>
          {onBackToNexus && (
            <button type="button" onClick={onBackToNexus} className={NEXUS_BTN_SECONDARY}>
              ← Back to NEXUS
            </button>
          )}
        </div>
      </div>

      <div className={NEXUS_CONTAINER}>
        {/* KPI metrics — VERTEX 4-col grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
          <NexusMetricCard label="Scheduled Today" value={scheduledToday} icon="📅" accent="blue" />
          <NexusMetricCard label="In Progress" value={inProgress} icon="⚡" accent="purple" />
          <NexusMetricCard
            label="Needs Attention"
            value={totalAlerts + opsUnreadCount}
            icon="⚠️"
            accent="yellow"
          />
          <NexusMetricCard label="Ops Events" value={opsNotifications.length} icon="📡" accent="green" />
          <NexusMetricCard label="Unread Ops" value={opsUnreadCount} icon="🔔" accent="pink" />
        </div>

        {/* Schedule + Ops feed */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <NexusPanel
              title="Today's Schedule"
              titleAccent="flex items-center justify-between"
            >
              <div className="flex items-center justify-between mb-4 -mt-2">
                <span />
                <span className="text-xs text-gray-500 font-normal">
                  {new Date().toLocaleDateString('en-US', {
                    weekday: 'long',
                    month: 'short',
                    day: 'numeric',
                  })}
                </span>
              </div>
              <div className="space-y-2">
                {todaySchedule.length === 0 && (
                  <div className="text-center py-10 text-gray-400 text-sm">
                    <p>No orders scheduled for today</p>
                    <p className="text-xs text-gray-500 mt-2">
                      Orders with today&apos;s date from GET /prism/orders appear here.
                    </p>
                  </div>
                )}
                {todaySchedule.map((item) => (
                  <NexusListRow key={item.id} onClick={() => onSelectDivision(item.divId)}>
                    <span
                      className={`w-16 shrink-0 text-xs font-semibold ${
                        item.status === 'in_progress' ? 'text-purple-300' : 'text-gray-400'
                      }`}
                    >
                      {item.time}
                    </span>
                    <div
                      className="w-1 h-8 rounded-full shrink-0"
                      style={{ background: item.color }}
                    />
                    <div className="flex-1 min-w-0">
                      <p className="font-semibold text-white text-sm truncate">{item.subject}</p>
                      <p className="text-xs text-gray-400 mt-0.5">
                        {item.type} · {item.client}
                      </p>
                    </div>
                    <StatusPill status={item.status} />
                    <span className="text-gray-500 text-xs">›</span>
                  </NexusListRow>
                ))}
              </div>
            </NexusPanel>
          </div>

          <NexusPanel title="Ops Feed" titleAccent="text-yellow-300">
            {opsUnreadCount > 0 && (
              <p className="text-xs text-pink-400 font-bold mb-3 -mt-2">{opsUnreadCount} unread</p>
            )}
            {unreadOps.length === 0 ? (
              <p className="text-sm text-gray-500 text-center py-8">
                No new ops events — intake, voice, and email land here.
              </p>
            ) : (
              <div className="space-y-2">
                {unreadOps.slice(0, 6).map((n) => (
                  <button
                    key={n.id}
                    type="button"
                    onClick={() => {
                      onMarkOpsRead?.(n.id);
                      onOpsNotificationClick?.(n);
                    }}
                    className="w-full text-left p-3 bg-yellow-500/5 border border-yellow-500/20 rounded-lg hover:bg-yellow-500/10 transition-all"
                  >
                    <p className="font-semibold text-white text-sm">
                      {n.icon ? `${n.icon} ` : ''}
                      {n.title}
                    </p>
                    <p className="text-xs text-yellow-300 mt-1">{n.message}</p>
                    {n.order_id && (
                      <p className="text-[10px] text-orange-400 mt-1">{n.order_id}</p>
                    )}
                  </button>
                ))}
              </div>
            )}
          </NexusPanel>
        </div>

        {/* Divisions grid */}
        <NexusPanel title="TPA Divisions">
          <div className="flex items-center justify-between mb-4 -mt-2">
            <span className="text-sm text-gray-400">Select a division to open workspace</span>
            <input
              type="text"
              placeholder="Search divisions..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="px-3 py-2 rounded-lg border border-gray-600 bg-gray-800 text-gray-100 text-sm outline-none focus:border-purple-500 w-48"
            />
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-3">
            {filtered.map((div) => {
              const alertCount = divisionNotifications[div.id] || 0;
              return (
                <button
                  key={div.id}
                  type="button"
                  onClick={() => onSelectDivision(div.id)}
                  className={`flex flex-col items-start gap-2 p-4 rounded-xl border text-left transition-all hover:scale-[1.02] bg-gradient-to-br from-gray-800 to-gray-900 hover:from-gray-700 hover:to-gray-800 ${
                    alertCount > 0 ? 'border-yellow-500/40' : 'border-purple-500/20'
                  }`}
                  style={{ borderLeftWidth: 4, borderLeftColor: div.color }}
                >
                  <span className="text-2xl">{div.icon}</span>
                  <p className="font-semibold text-sm text-white leading-tight">{div.name}</p>
                  {alertCount > 0 && (
                    <span
                      className="text-[10px] font-bold px-2 py-0.5 rounded-full text-white"
                      style={{ background: div.solid || div.color }}
                    >
                      {alertCount} alert{alertCount !== 1 ? 's' : ''}
                    </span>
                  )}
                </button>
              );
            })}
          </div>
        </NexusPanel>
      </div>
    </div>
  );
};

export default PRISMHub;
