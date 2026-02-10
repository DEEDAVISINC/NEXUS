import React, { useState, useEffect } from 'react';
import { api } from '../api/client';

interface TransportationNotification {
  new_opportunities: Array<{
    id: string;
    title: string;
    value: number;
    due_date?: string;
    status: string;
    category: string;
  }>;
  todays_focus: {
    day: string;
    focus: string;
    icon: string;
    searches: string[];
    expected_results: string;
    revenue_potential: string;
    special_note?: string;
  };
  weekly_stats: {
    total_opportunities: number;
    new_this_week: number;
    total_value: number;
    average_value: number;
    high_value_count: number;
  };
  high_priority: Array<{
    id: string;
    title: string;
    value: number;
    due_date?: string;
    status: string;
    category: string;
  }>;
}

interface TransportationNotificationBannerProps {
  onViewAll?: () => void;
}

export const TransportationNotificationBanner: React.FC<TransportationNotificationBannerProps> = ({ onViewAll }) => {
  const [notification, setNotification] = useState<TransportationNotification | null>(null);
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState(false);
  const [copiedSearch, setCopiedSearch] = useState<string | null>(null);

  useEffect(() => {
    loadNotifications();
    // Refresh every 5 minutes
    const interval = setInterval(loadNotifications, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  const loadNotifications = async () => {
    try {
      const response = await fetch('http://localhost:8000/transportation-logistics/notifications');
      const data = await response.json();
      setNotification(data);
    } catch (error) {
      console.error('Error loading transportation notifications:', error);
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedSearch(text);
    setTimeout(() => setCopiedSearch(null), 2000);
  };

  if (loading || !notification) {
    return null;
  }

  // Don't show if no new opportunities and it's weekend
  const isWeekend = notification.todays_focus?.day && ['Saturday', 'Sunday'].includes(notification.todays_focus.day);
  if (notification.new_opportunities.length === 0 && notification.weekly_stats.new_this_week === 0 && isWeekend) {
    return null;
  }

  return (
    <div className="bg-gradient-to-br from-blue-600 via-purple-600 to-pink-600 rounded-xl p-1 shadow-2xl">
      <div className="bg-gray-900 rounded-lg p-6">
        {/* Header */}
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="text-3xl">✈️🚢</div>
            <div>
              <h3 className="text-xl font-black text-white">Transportation & Logistics Opportunities</h3>
              <p className="text-sm text-gray-400">
                {notification.weekly_stats.new_this_week > 0 && (
                  <span className="text-green-400 font-bold">
                    {notification.weekly_stats.new_this_week} new this week
                  </span>
                )}
                {notification.weekly_stats.new_this_week === 0 && (
                  <span>No new opportunities this week</span>
                )}
              </p>
            </div>
          </div>

          <button
            onClick={() => setExpanded(!expanded)}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg font-bold transition text-sm"
          >
            {expanded ? 'Collapse' : 'Expand'}
          </button>
        </div>

        {/* Stats Bar */}
        <div className="grid grid-cols-4 gap-3 mb-4">
          <div className="bg-gray-800/50 border border-gray-700 rounded-lg p-3">
            <div className="text-2xl font-black text-green-400">
              {notification.weekly_stats.new_this_week}
            </div>
            <div className="text-xs text-gray-400">New This Week</div>
          </div>

          <div className="bg-gray-800/50 border border-gray-700 rounded-lg p-3">
            <div className="text-2xl font-black text-blue-400">
              {notification.weekly_stats.total_opportunities}
            </div>
            <div className="text-xs text-gray-400">Total Active</div>
          </div>

          <div className="bg-gray-800/50 border border-gray-700 rounded-lg p-3">
            <div className="text-2xl font-black text-yellow-400">
              ${(notification.weekly_stats.total_value / 1000000).toFixed(1)}M
            </div>
            <div className="text-xs text-gray-400">Pipeline Value</div>
          </div>

          <div className="bg-gray-800/50 border border-gray-700 rounded-lg p-3">
            <div className="text-2xl font-black text-purple-400">
              {notification.high_priority.length}
            </div>
            <div className="text-xs text-gray-400">High Value (&gt;$100K)</div>
          </div>
        </div>

        {/* Today's Focus */}
        {notification.todays_focus && !isWeekend && (
          <div className="bg-gradient-to-r from-green-900/30 to-blue-900/30 border-2 border-green-500/50 rounded-lg p-4 mb-4">
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center gap-2">
                <span className="text-2xl">{notification.todays_focus.icon}</span>
                <div>
                  <h4 className="text-lg font-black text-green-400">
                    Today's Focus: {notification.todays_focus.focus}
                  </h4>
                  <p className="text-xs text-gray-400">
                    Expected: {notification.todays_focus.expected_results} • {notification.todays_focus.revenue_potential}
                  </p>
                </div>
              </div>

              {onViewAll && (
                <button
                  onClick={onViewAll}
                  className="px-3 py-1 bg-green-600 hover:bg-green-700 rounded text-xs font-bold transition"
                >
                  Run Searches →
                </button>
              )}
            </div>

            {notification.todays_focus.special_note && (
              <div className="bg-yellow-900/20 border border-yellow-500/30 rounded px-3 py-2 mb-3">
                <p className="text-xs text-yellow-400 font-bold">
                  💡 {notification.todays_focus.special_note}
                </p>
              </div>
            )}

            {expanded && (
              <div className="space-y-2">
                <div className="text-xs font-bold text-green-400 mb-1">RECOMMENDED SEARCHES:</div>
                {notification.todays_focus.searches.map((search, idx) => (
                  <div key={idx} className="flex items-center gap-2">
                    <code className="flex-1 bg-gray-900/70 px-3 py-2 rounded text-green-300 text-xs font-mono">
                      {search}
                    </code>
                    <button
                      onClick={() => copyToClipboard(search)}
                      className="px-2 py-1 bg-blue-600 hover:bg-blue-700 rounded text-xs font-bold transition"
                    >
                      {copiedSearch === search ? '✓' : 'Copy'}
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* High Priority Opportunities */}
        {expanded && notification.high_priority.length > 0 && (
          <div className="bg-gray-800/30 border border-yellow-500/30 rounded-lg p-4 mb-4">
            <h4 className="text-sm font-black text-yellow-400 mb-3">
              ⭐ HIGH VALUE OPPORTUNITIES (&gt;$100K)
            </h4>
            <div className="space-y-2">
              {notification.high_priority.map((opp, idx) => (
                <div key={idx} className="flex items-center justify-between bg-gray-900/50 rounded px-3 py-2">
                  <div className="flex-1">
                    <div className="text-sm text-white font-semibold">{opp.title}</div>
                    <div className="text-xs text-gray-400">{opp.category}</div>
                  </div>
                  <div className="text-right ml-3">
                    <div className="text-sm font-black text-green-400">
                      ${(opp.value / 1000).toFixed(0)}K
                    </div>
                    {opp.due_date && (
                      <div className="text-xs text-gray-400">
                        Due: {new Date(opp.due_date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* New Opportunities */}
        {expanded && notification.new_opportunities.length > 0 && (
          <div className="bg-gray-800/30 border border-blue-500/30 rounded-lg p-4">
            <h4 className="text-sm font-black text-blue-400 mb-3">
              🆕 RECENTLY ADDED (Last 7 Days)
            </h4>
            <div className="space-y-2">
              {notification.new_opportunities.map((opp, idx) => (
                <div key={idx} className="flex items-center justify-between bg-gray-900/50 rounded px-3 py-2">
                  <div className="flex-1">
                    <div className="text-sm text-white font-semibold">{opp.title}</div>
                    <div className="text-xs text-gray-400">{opp.category}</div>
                  </div>
                  <div className="text-right ml-3">
                    <div className="text-sm font-black text-blue-400">
                      ${(opp.value / 1000).toFixed(0)}K
                    </div>
                    <div className="text-xs text-gray-500">{opp.status}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Footer Action */}
        {!expanded && onViewAll && (
          <div className="flex items-center justify-between pt-3 border-t border-gray-700">
            <div className="text-sm text-gray-400">
              Click expand to see all opportunities and today's searches
            </div>
            <button
              onClick={onViewAll}
              className="text-blue-400 hover:text-blue-300 font-bold text-sm transition"
            >
              Open Transportation System →
            </button>
          </div>
        )}
      </div>
    </div>
  );
};
