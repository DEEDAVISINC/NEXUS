import React, { useEffect, useState } from 'react';

interface Bid {
  name: string;
  value: number;
  deadline: string;
  daysLeft: number;
  status: 'urgent' | 'active' | 'completed' | 'monitoring';
  activity: {
    fileCount: number;
    lastEdited: string;
  };
  hasQuotes: boolean;
  hasSubmission: boolean;
}

interface DashboardData {
  focusBid: Bid | null;
  urgentBids: Bid[];
  thisWeekBids: Bid[];
  completedBids: Bid[];
  totalValue: number;
  completedValue: number;
  autoRemovedCount: number;
}

export const BidsDashboard: React.FC = () => {
  const [dashboardData, setDashboardData] = useState<DashboardData>({
    focusBid: null,
    urgentBids: [],
    thisWeekBids: [],
    completedBids: [],
    totalValue: 0,
    completedValue: 0,
    autoRemovedCount: 0
  });
  const [loading, setLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());

  // Load dashboard data
  useEffect(() => {
    loadDashboardData();
    
    // Refresh every 5 minutes
    const interval = setInterval(loadDashboardData, 5 * 60 * 1000);
    return () => clearInterval(interval);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const loadDashboardData = async () => {
    try {
      // In production, this would call the backend API
      // For now, load from the adaptive system's learning data
      const response = await fetch('/api/bids/dashboard');
      if (response.ok) {
        const data = await response.json();
        setDashboardData(data);
      } else {
        // Fallback to mock data
        loadMockData();
      }
    } catch (error) {
      console.error('Failed to load dashboard:', error);
      loadMockData();
    } finally {
      setLoading(false);
      setLastUpdate(new Date());
    }
  };

  const loadMockData = () => {
    // Real submitted bids from BIDS:RESOURCES confirmation files
    setDashboardData({
      focusBid: null,
      urgentBids: [],
      thisWeekBids: [],
      completedBids: [
        { name: 'RCOC 7732 PAPER PRODUCTS', value: 80437, deadline: 'February 10, 2026', daysLeft: 0, status: 'completed', activity: { fileCount: 24, lastEdited: 'Feb 7' }, hasQuotes: true, hasSubmission: true },
        { name: 'RCOC 7802 BUILDING TOOLS', value: 7292, deadline: 'February 6, 2026', daysLeft: 0, status: 'completed', activity: { fileCount: 16, lastEdited: 'Feb 5' }, hasQuotes: true, hasSubmission: true },
        { name: 'RCOC 7799 GREASE AIR COUPLERS', value: 6128, deadline: 'February 6, 2026', daysLeft: 0, status: 'completed', activity: { fileCount: 14, lastEdited: 'Feb 5' }, hasQuotes: true, hasSubmission: true },
        { name: 'RCOC 7797 AUTOMOTIVE TOOLS', value: 3978, deadline: 'February 4, 2026', daysLeft: 0, status: 'completed', activity: { fileCount: 12, lastEdited: 'Feb 3' }, hasQuotes: true, hasSubmission: true },
        { name: 'WARREN ZEP PARTS WASHER', value: 3735, deadline: 'February 10, 2026', daysLeft: 0, status: 'completed', activity: { fileCount: 8, lastEdited: 'Feb 5' }, hasQuotes: true, hasSubmission: true },
        { name: 'RCOC 7798 WIPER BLADES', value: 1521, deadline: 'February 4, 2026', daysLeft: 0, status: 'completed', activity: { fileCount: 10, lastEdited: 'Feb 3' }, hasQuotes: true, hasSubmission: true },
        { name: 'OAKLAND COUNTY BODY BAGS', value: 126000, deadline: 'January 29, 2026', daysLeft: 0, status: 'completed', activity: { fileCount: 23, lastEdited: 'Jan 27' }, hasQuotes: true, hasSubmission: true },
        { name: 'VA COURIER SERVICES', value: 300000, deadline: 'February 12, 2026', daysLeft: 0, status: 'completed', activity: { fileCount: 15, lastEdited: 'Feb 1' }, hasQuotes: false, hasSubmission: true },
      ],
      totalValue: 0,
      completedValue: 529091,
      autoRemovedCount: 0
    });
  };

  const refreshDashboard = () => {
    setLoading(true);
    loadDashboardData();
  };

  const openBidFolder = (bidName: string) => {
    // This would use shell command or file system API
    const folderPath = `BIDS:RESOURCES/${bidName}/`;
    console.log('Opening folder:', folderPath);
    // In Electron, you could use: shell.openPath(folderPath)
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'urgent': return 'bg-red-500';
      case 'active': return 'bg-yellow-500';
      case 'completed': return 'bg-green-500';
      case 'monitoring': return 'bg-blue-500';
      default: return 'bg-gray-500';
    }
  };

  const getUrgencyClass = (daysLeft: number) => {
    if (daysLeft <= 1) return 'text-red-500 font-bold';
    if (daysLeft <= 3) return 'text-orange-500 font-semibold';
    if (daysLeft <= 7) return 'text-yellow-500';
    return 'text-gray-400';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header Stats */}
      <div className="grid grid-cols-4 gap-4">
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="text-gray-400 text-sm mb-2">Active Pipeline</div>
          <div className="text-3xl font-bold text-blue-400">${(dashboardData.totalValue / 1000).toFixed(0)}K</div>
          <div className="text-xs text-gray-500 mt-1">{dashboardData.urgentBids.length + dashboardData.thisWeekBids.length} bids</div>
        </div>

        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="text-gray-400 text-sm mb-2">Submitted</div>
          <div className="text-3xl font-bold text-green-400">${(dashboardData.completedValue / 1000).toFixed(0)}K</div>
          <div className="text-xs text-gray-500 mt-1">{dashboardData.completedBids.length} bids awaiting award</div>
        </div>

        <div className="bg-gray-800 rounded-lg p-6 border border-red-900">
          <div className="text-gray-400 text-sm mb-2">Urgent (≤3 days)</div>
          <div className="text-3xl font-bold text-red-400">{dashboardData.urgentBids.length + (dashboardData.focusBid && dashboardData.focusBid.daysLeft <= 3 ? 1 : 0)}</div>
          <div className="text-xs text-red-500 mt-1 font-semibold">IMMEDIATE ACTION</div>
        </div>

        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="text-gray-400 text-sm mb-2">Awaiting Award</div>
          <div className="text-3xl font-bold text-purple-400">{dashboardData.completedBids.length}</div>
          <div className="text-xs text-gray-500 mt-1">Submitted, pending decisions</div>
        </div>
      </div>

      {/* Focus Bid */}
      {dashboardData.focusBid && (
        <div className="bg-gradient-to-r from-red-900/40 to-orange-900/40 rounded-lg p-6 border-2 border-red-500">
          <div className="flex items-start justify-between mb-4">
            <div>
              <div className="text-red-400 text-sm font-semibold mb-1">🔥 YOUR #1 FOCUS RIGHT NOW</div>
              <h2 className="text-2xl font-bold text-white mb-2">{dashboardData.focusBid.name}</h2>
              <div className="text-gray-300 text-sm">System detected: You edited this {dashboardData.focusBid.activity.lastEdited}</div>
            </div>
            <button
              onClick={() => openBidFolder(dashboardData.focusBid!.name)}
              className="px-6 py-3 bg-red-500 hover:bg-red-600 rounded-lg font-semibold transition flex items-center gap-2"
            >
              <span>📂</span>
              <span>Open Folder</span>
            </button>
          </div>

          <div className="grid grid-cols-4 gap-4 mb-4">
            <div className="bg-black/30 rounded p-3">
              <div className="text-gray-400 text-xs mb-1">Value</div>
              <div className="text-xl font-bold text-green-400">${(dashboardData.focusBid.value / 1000).toFixed(0)}K</div>
            </div>
            <div className="bg-black/30 rounded p-3">
              <div className="text-gray-400 text-xs mb-1">Deadline</div>
              <div className="text-xl font-bold text-red-400">{dashboardData.focusBid.daysLeft} days</div>
            </div>
            <div className="bg-black/30 rounded p-3">
              <div className="text-gray-400 text-xs mb-1">Activity</div>
              <div className="text-xl font-bold text-blue-400">{dashboardData.focusBid.activity.fileCount} files</div>
            </div>
            <div className="bg-black/30 rounded p-3">
              <div className="text-gray-400 text-xs mb-1">Status</div>
              <div className="text-xl font-bold text-yellow-400">In Progress</div>
            </div>
          </div>

          <div className="bg-black/30 rounded p-4">
            <div className="text-sm font-semibold text-white mb-2">Natural Flow - Your Next Steps:</div>
            <div className="space-y-2 text-sm">
              <label className="flex items-center gap-2 text-gray-300">
                <input type="checkbox" className="form-checkbox h-4 w-4 text-blue-500" />
                <span>1. Check folder for analysis document</span>
              </label>
              <label className="flex items-center gap-2 text-gray-300">
                <input type="checkbox" className="form-checkbox h-4 w-4 text-blue-500" />
                <span>2. Find battery cabinet suppliers</span>
              </label>
              <label className="flex items-center gap-2 text-gray-300">
                <input type="checkbox" className="form-checkbox h-4 w-4 text-blue-500" />
                <span>3. Request quotes from suppliers</span>
              </label>
              <label className="flex items-center gap-2 text-gray-300">
                <input type="checkbox" className="form-checkbox h-4 w-4 text-blue-500" />
                <span>4. Review quotes and complete bid forms</span>
              </label>
              <label className="flex items-center gap-2 text-gray-300">
                <input type="checkbox" className="form-checkbox h-4 w-4 text-blue-500" />
                <span>5. Submit by Wednesday at 2:00 PM</span>
              </label>
            </div>
          </div>
        </div>
      )}

      {/* Urgent Bids */}
      {dashboardData.urgentBids.length > 0 && (
        <div>
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-xl font-bold text-red-400">⚠️ Also Urgent ({dashboardData.urgentBids.length} bids)</h3>
            <div className="text-sm text-gray-400">≤3 days remaining</div>
          </div>
          <div className="grid gap-3">
            {dashboardData.urgentBids.map((bid, index) => (
              <div key={index} className="bg-gray-800 rounded-lg p-4 border border-red-900 hover:border-red-500 transition">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h4 className="font-semibold text-white">{bid.name}</h4>
                      <span className={`px-2 py-1 rounded text-xs ${getUrgencyClass(bid.daysLeft)}`}>
                        {bid.daysLeft}d left
                      </span>
                    </div>
                    <div className="flex items-center gap-4 text-sm">
                      <span className="text-green-400 font-semibold">${(bid.value / 1000).toFixed(0)}K</span>
                      <span className="text-gray-400">•</span>
                      <span className="text-gray-400">{bid.activity.fileCount} files</span>
                      <span className="text-gray-400">•</span>
                      <span className="text-gray-400">Last: {bid.activity.lastEdited}</span>
                    </div>
                  </div>
                  <button
                    onClick={() => openBidFolder(bid.name)}
                    className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg text-sm transition"
                  >
                    Open
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* This Week */}
      {dashboardData.thisWeekBids.length > 0 && (
        <div>
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-xl font-bold text-yellow-400">📅 This Week ({dashboardData.thisWeekBids.length} bids)</h3>
            <div className="text-sm text-gray-400">4-7 days remaining</div>
          </div>
          <div className="grid grid-cols-3 gap-4">
            {dashboardData.thisWeekBids.map((bid, index) => (
              <div key={index} className="bg-gray-800 rounded-lg p-4 border border-gray-700 hover:border-yellow-500 transition">
                <div className="flex items-center justify-between mb-2">
                  <span className={`w-2 h-2 rounded-full ${getStatusColor(bid.status)}`}></span>
                  <span className="text-xs text-gray-400">{bid.daysLeft}d</span>
                </div>
                <h4 className="font-semibold text-white text-sm mb-2 line-clamp-2">{bid.name}</h4>
                <div className="text-green-400 font-bold mb-2">${(bid.value / 1000).toFixed(0)}K</div>
                <button
                  onClick={() => openBidFolder(bid.name)}
                  className="w-full px-3 py-1.5 bg-gray-700 hover:bg-gray-600 rounded text-xs transition"
                >
                  Open
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Completed Bids */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-xl font-bold text-blue-400">📨 Submitted ({dashboardData.completedBids.length} bids) - ${(dashboardData.completedValue / 1000).toFixed(0)}K</h3>
          <div className="text-sm text-gray-400">Awaiting award decisions</div>
        </div>
        <div className="grid grid-cols-6 gap-3">
          {dashboardData.completedBids.map((bid, index) => (
            <div key={index} className="bg-gray-800 rounded-lg p-3 border border-green-900">
              <div className="flex items-center justify-between mb-2">
                <span className="text-green-400">✅</span>
                <span className="text-xs text-gray-400">${(bid.value / 1000).toFixed(0)}K</span>
              </div>
              <div className="text-xs text-white line-clamp-2 mb-2">{bid.name}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Footer Actions */}
      <div className="bg-gray-800 rounded-lg p-4 border border-gray-700 flex items-center justify-between">
        <div className="text-sm text-gray-400">
          Last updated: {lastUpdate.toLocaleTimeString()} • System learning active • Auto-refresh in 5 min
        </div>
        <button
          onClick={refreshDashboard}
          className="px-4 py-2 bg-blue-500 hover:bg-blue-600 rounded-lg text-sm font-semibold transition flex items-center gap-2"
        >
          <span>🔄</span>
          <span>Refresh Now</span>
        </button>
      </div>
    </div>
  );
};
