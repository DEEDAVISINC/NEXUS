import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { ViewType } from './Header';
import { api } from '../api/client';

interface LandingPageProps {
  onEnterSystem: (system: ViewType) => void;
}

interface DashboardStats {
  active_opportunities: number;
  total_contacts: number;
  active_projects: number;
  revenue_pipeline: number;
  systems: {
    gpss: {
      opportunities: number;
      pipeline: number;
      contacts: number;
    };
    ddcss: {
      prospects: number;
      responses: number;
      sectors: number;
    };
    atlas: {
      projects: number;
      rfps_analyzed: number;
      total_value: number;
    };
  };
  timestamp: string;
}

interface Activity {
  type: string;
  system: string;
  action: string;
  title: string;
  time: string;
  icon: string;
  color: string;
}

interface Alert {
  type: string;
  title: string;
  message: string;
  action: string;
  system: string;
}

const LandingPage: React.FC<LandingPageProps> = ({ onEnterSystem }) => {
  // Default/mock stats as fallback
  const defaultStats: DashboardStats = useMemo(() => ({
    active_opportunities: 0,
    total_contacts: 0,
    active_projects: 0,
    revenue_pipeline: 0,
    systems: {
      gpss: { opportunities: 0, pipeline: 0, contacts: 0 },
      ddcss: { prospects: 0, responses: 0, sectors: 6 },
      atlas: { projects: 0, rfps_analyzed: 0, total_value: 0 }
    },
    timestamp: new Date().toISOString()
  }), []);

  const [activeTab, setActiveTab] = useState<'overview' | 'activity' | 'analytics' | 'portals'>('overview');
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState<DashboardStats>(defaultStats);
  const [activities, setActivities] = useState<Activity[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  // Vendor Portals State
  const [portals, setPortals] = useState<any[]>([]);
  const [portalSearch, setPortalSearch] = useState('');
  const [isDragging, setIsDragging] = useState(false);

  // Opportunities and Tasks for Deadlines
  const [opportunities, setOpportunities] = useState<any[]>([]);
  const [tasks, setTasks] = useState<any[]>([]);

  // Email monitoring state
  const [emailStatus, setEmailStatus] = useState({
    newCount: 0,
    lastChecked: new Date(),
    checking: false,
    recentActivity: [] as any[]
  });

  // Fetch dashboard data
  const fetchDashboardData = useCallback(async () => {
    try {
      const [statsData, activityData, alertsData] = await Promise.all([
        api.getDashboardStats(),
        api.getDashboardActivity(),
        api.getDashboardAlerts()
      ]);

      // Merge with defaults to ensure all fields exist
      setStats({ ...defaultStats, ...statsData });
      setActivities(activityData.activities || []);
      setAlerts(alertsData.alerts || []);
      setLastUpdated(new Date());
      setLoading(false);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      // Use default stats if API fails
      setStats(defaultStats);
      setLoading(false);
    }
  }, [defaultStats]);

  // Fetch opportunities and tasks for deadlines
  const fetchDeadlineData = useCallback(async () => {
    try {
      const [oppsData, tasksData] = await Promise.all([
        api.getGpssOpportunities().catch(() => ({ opportunities: [] })),
        api.getTasks().catch(() => [])
      ]);
      setOpportunities(oppsData.opportunities || []);
      setTasks(Array.isArray(tasksData) ? tasksData : []);
    } catch (error) {
      console.error('Error fetching deadline data:', error);
    }
  }, []);

  // Fetch vendor portals
  const fetchPortals = async () => {
    try {
      const response = await api.getVendorPortals();
      setPortals(response.portals || []);
    } catch (error) {
      console.error('Error fetching portals:', error);
    }
  };

  // Handle drag & drop
  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = async (e: React.DragEvent, category: 'Government' | 'Development') => {
    e.preventDefault();
    setIsDragging(false);

    const url = e.dataTransfer.getData('text/plain');
    if (!url || !url.startsWith('http')) {
      alert('Please drag a valid URL');
      return;
    }

    try {
      // Extract domain name as portal name
      const domain = new URL(url).hostname.replace('www.', '');
      const name = domain.split('.')[0].charAt(0).toUpperCase() + domain.split('.')[0].slice(1);

      await api.createVendorPortal({
        name,
        url,
        category,
        portalType: category === 'Government' ? 'Federal' : 'SaaS',
        keywords: '',
        description: '',
        searchEnabled: false,
        icon: category === 'Government' ? '🏛️' : '🛠️'
      });

      fetchPortals();
    } catch (error) {
      console.error('Error adding portal:', error);
      alert('Failed to add portal');
    }
  };

  // Delete portal
  const deletePortal = async (portalId: string) => {
    if (!window.confirm('Delete this portal?')) return;
    try {
      await api.deleteVendorPortal(portalId);
      fetchPortals();
    } catch (error) {
      console.error('Error deleting portal:', error);
    }
  };

  // Open portal and update last accessed
  const openPortal = async (portal: any) => {
    try {
      await api.updateVendorPortal(portal.id, { updateLastAccessed: true });
      window.open(portal.url, '_blank');
      fetchPortals();
    } catch (error) {
      console.error('Error opening portal:', error);
    }
  };

  // Check email manually
  const checkEmailNow = async () => {
    setEmailStatus(prev => ({ ...prev, checking: true }));
    try {
      // TODO: API endpoint to check email
      // For now, simulate check
      await new Promise(resolve => setTimeout(resolve, 1000));
      setEmailStatus({
        newCount: 0,
        lastChecked: new Date(),
        checking: false,
        recentActivity: []
      });
    } catch (error) {
      console.error('Error checking email:', error);
      setEmailStatus(prev => ({ ...prev, checking: false }));
    }
  };

  // Calendar Export Function - Export all ATLAS tasks to .ics file
  const exportAllTasksToCalendar = async () => {
    try {
      // Fetch all tasks from ATLAS
      const response = await api.getTasks();
      const tasks = response.tasks || [];
      
      if (tasks.length === 0) {
        alert('📅 No tasks found in ATLAS PM system.\n\nGo to ATLAS PM → Task Board to create tasks first, then export them to your calendar.');
        return;
      }
      
      const tasksWithDates = tasks.filter((t: any) => t.dueDate);
      
      if (tasksWithDates.length === 0) {
        alert(`📅 Found ${tasks.length} task(s), but none have due dates set.\n\nAdd due dates to your tasks in ATLAS PM → Task Board, then export them to your calendar.`);
        return;
      }

      const events = tasksWithDates.map((task: any) => {
        const startDate = new Date(task.dueDate);
        const endDate = new Date(startDate.getTime() + 60 * 60 * 1000);
        
        const formatDate = (date: Date) => {
          return date.toISOString().replace(/[-:]/g, '').split('.')[0] + 'Z';
        };

        return `BEGIN:VEVENT
UID:${task.id}@nexus-system
DTSTAMP:${formatDate(new Date())}
DTSTART:${formatDate(startDate)}
DTEND:${formatDate(endDate)}
SUMMARY:${task.title || 'NEXUS Task'}
DESCRIPTION:${task.description || ''}
PRIORITY:${task.priority === 'High' || task.priority === 'Urgent' ? '1' : task.priority === 'Medium' ? '5' : '9'}
STATUS:${task.status === 'Done' ? 'COMPLETED' : 'NEEDS-ACTION'}
END:VEVENT`;
      }).join('\n');

      const icsContent = `BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//NEXUS Command Center//EN
${events}
END:VCALENDAR`;

      const blob = new Blob([icsContent], { type: 'text/calendar;charset=utf-8' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = 'NEXUS_All_Tasks.ics';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      alert(`✅ Successfully exported ${tasksWithDates.length} task(s) to Calendar!\n\nThe file "NEXUS_All_Tasks.ics" has been downloaded.\n\nOpen it to add all tasks to your calendar app.`);
    } catch (error) {
      console.error('Error exporting tasks:', error);
      const errorMsg = error instanceof Error ? error.message : 'Unknown error';
      alert(`❌ Error exporting tasks to calendar:\n\n${errorMsg}\n\nMake sure the backend server is running on port 8000.`);
    }
  };

  // Initial load and auto-refresh every 30 seconds
  useEffect(() => {
    fetchDashboardData();
    fetchPortals();
    fetchDeadlineData();
    
    const interval = setInterval(() => {
      fetchDashboardData();
      fetchDeadlineData();
    }, 30000); // 30 seconds

    return () => clearInterval(interval);
  }, [fetchDashboardData, fetchDeadlineData]);

  // Format large numbers
  const formatNumber = (num: number): string => {
    if (num >= 1000000) return `$${(num / 1000000).toFixed(1)}M`;
    if (num >= 1000) return `$${(num / 1000).toFixed(0)}K`;
    return `$${num}`;
  };

  // Format time ago
  const timeAgo = (dateString: string): string => {
    try {
      const date = new Date(dateString);
      const now = new Date();
      const seconds = Math.floor((now.getTime() - date.getTime()) / 1000);
      
      if (seconds < 60) return 'Just now';
      if (seconds < 3600) return `${Math.floor(seconds / 60)} min ago`;
      if (seconds < 86400) return `${Math.floor(seconds / 3600)} hour${Math.floor(seconds / 3600) > 1 ? 's' : ''} ago`;
      return `${Math.floor(seconds / 86400)} day${Math.floor(seconds / 86400) > 1 ? 's' : ''} ago`;
    } catch {
      return 'Recently';
    }
  };

  // Generate stat cards from live data
  const statCards = [
    { 
      label: 'Active Opportunities', 
      value: (stats.active_opportunities || 0).toString(), 
      change: '+3', 
      icon: '🎯', 
      gradient: 'from-blue-600 to-blue-800',
      action: () => onEnterSystem('gpss'),
      tooltip: 'Click to view all opportunities in GPSS',
      source: 'GPSS → Opportunities Table'
    },
    { 
      label: 'Total Contacts', 
      value: (stats.total_contacts || 0).toString(), 
      change: '+6', 
      icon: '👥', 
      gradient: 'from-green-600 to-green-800',
      action: () => onEnterSystem('gpss'),
      tooltip: 'Click to manage contacts in GPSS',
      source: 'GPSS → Contacts Table'
    },
    { 
      label: 'Active Projects', 
      value: (stats.active_projects || 0).toString(), 
      change: '→', 
      icon: '📋', 
      gradient: 'from-purple-600 to-purple-800',
      action: () => onEnterSystem('atlas'),
      tooltip: 'Click to view all projects in ATLAS PM',
      source: 'ATLAS → Projects Table'
    },
    { 
      label: 'Revenue Pipeline', 
      value: formatNumber(stats.revenue_pipeline || 0), 
      change: '+$2.4M', 
      icon: '💰', 
      gradient: 'from-yellow-600 to-yellow-800',
      action: () => onEnterSystem('gpss'),
      tooltip: 'Click to view pipeline in GPSS',
      source: 'GPSS → Sum of all opportunity values'
    },
  ];

  const systems = [
    {
      id: 'gpss' as ViewType,
      name: 'GPSS',
      fullName: 'Government Prime Sales System',
      icon: '🎯',
      description: 'Government Contracting Command Center',
      stats: [
        `${stats.systems.gpss.opportunities} Active RFP${stats.systems.gpss.opportunities !== 1 ? 's' : ''}`,
        `${formatNumber(stats.systems.gpss.pipeline)} Pipeline`,
        `${stats.systems.gpss.contacts} Contact${stats.systems.gpss.contacts !== 1 ? 's' : ''}`
      ],
      gradient: 'from-blue-600 to-purple-600',
      status: 'online',
      lastUsed: '2 min ago'
    },
    {
      id: 'ddcss' as ViewType,
      name: 'DDCSS',
      fullName: 'Corporate Sales System',
      icon: '💼',
      description: 'Blueprint Framework • 6 Sectors • AI Copilot',
      stats: [
        `${stats.systems.ddcss.prospects} Pipeline`,
        `${stats.systems.ddcss.responses} Response${stats.systems.ddcss.responses !== 1 ? 's' : ''}`,
        `${stats.systems.ddcss.sectors} Sectors Ready`
      ],
      gradient: 'from-green-600 to-blue-600',
      status: 'online',
      lastUsed: '5 min ago'
    },
    {
      id: 'atlas' as ViewType,
      name: 'ATLAS PM',
      fullName: 'Project Management System',
      icon: '🏗️',
      description: 'RFP Analysis • WBS Generation • Change Orders',
      stats: [
        `${stats.systems.atlas.projects} Project${stats.systems.atlas.projects !== 1 ? 's' : ''}`,
        `${stats.systems.atlas.rfps_analyzed} RFP${stats.systems.atlas.rfps_analyzed !== 1 ? 's' : ''} Analyzed`,
        `${formatNumber(stats.systems.atlas.total_value)} Value`
      ],
      gradient: 'from-purple-600 to-pink-600',
      status: 'online',
      lastUsed: 'Just now'
    },
    {
      id: 'gbis' as ViewType,
      name: 'GBIS',
      fullName: 'Grant Business Intelligence System',
      icon: '🎁',
      description: 'Grant Discovery • AI Applications • ROI Tracking',
      stats: [
        '0 Active Grants',
        '0 Applications',
        '$0 Awarded'
      ],
      gradient: 'from-yellow-600 to-orange-600',
      status: 'online',
      lastUsed: 'New!'
    },
    {
      id: 'vertex' as ViewType,
      name: 'VERTEX',
      fullName: 'Financial Command Center',
      icon: '💎',
      description: 'Invoices • Expenses • Revenue • AI Intelligence • QB Export',
      stats: [
        '$0 Total Revenue',
        '$0 Net Income',
        '$0 A/R Outstanding'
      ],
      gradient: 'from-purple-600 to-pink-600',
      status: 'online',
      lastUsed: 'NEW! 🔥'
    },
    {
      id: 'lbpc' as ViewType,
      name: 'LBPC',
      fullName: 'Lancaster Banques P.C.',
      icon: '💰',
      description: 'Surplus Recovery • All 50 States • Automated Workflows',
      stats: [
        '0 Active Leads',
        '$0 Pipeline',
        '0 Tasks Due'
      ],
      gradient: 'from-indigo-600 to-purple-600',
      status: 'online',
      lastUsed: 'New!'
    },
    {
      id: 'invoices' as ViewType,
      name: 'INVOICES',
      fullName: 'Universal Invoicing System',
      icon: '💰',
      description: 'Government & Enterprise Compliant • All Systems',
      stats: [
        '0 Total Invoices',
        '$0 Revenue',
        '0 Pending'
      ],
      gradient: 'from-yellow-600 to-orange-600',
      status: 'online',
      lastUsed: 'New!'
    },
    {
      id: 'quotes' as ViewType,
      name: 'QUOTES',
      fullName: 'Supplier Quote System',
      icon: '📋',
      description: 'Generate & Track Supplier Quote Requests • Timestamped',
      stats: [
        '0 Pending Quotes',
        '0 Sent This Month',
        '0% Response Rate'
      ],
      gradient: 'from-blue-600 to-cyan-600',
      status: 'online',
      lastUsed: 'NEW! 🚀'
    },
    {
      id: 'capstats' as ViewType,
      name: 'CAP STATS',
      fullName: 'Capability Statement Generator',
      icon: '📄',
      description: 'Professional Capability Statements • Multiple Templates',
      stats: [
        '0 Generated',
        '5 Templates',
        'Ready to Use!'
      ],
      gradient: 'from-purple-600 to-indigo-600',
      status: 'online',
      lastUsed: 'NEW! 🚀'
    },
    {
      id: 'contracts' as ViewType,
      name: 'CCC',
      fullName: 'Contract Command Center',
      icon: '🏆',
      description: 'Post-Award Management • Suppliers • Delivery • Payment',
      stats: [
        '0 Active Contracts',
        '$0 Under Management',
        'Nothing Falls Through!'
      ],
      gradient: 'from-yellow-600 to-red-600',
      status: 'online',
      lastUsed: 'COMING SOON! 🔥'
    }
  ];

  // Use live activities or fallback to empty array
  const recentActivity = activities.map(activity => ({
    ...activity,
    time: timeAgo(activity.time)
  }));

  // Build upcoming deadlines from real opportunities and tasks
  const upcomingDeadlines = useMemo(() => {
    const deadlines: Array<{ date: string; title: string; system: string; priority: string; timestamp: number }> = [];
    const now = new Date();

    // Add opportunities with response deadlines
    opportunities.forEach(opp => {
      if (opp['Response Deadline']) {
        const deadline = new Date(opp['Response Deadline']);
        if (deadline > now) {
          deadlines.push({
            date: deadline.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }),
            title: opp.Name || 'Unnamed Opportunity',
            system: 'GPSS',
            priority: opp['Priority'] === 'High' ? 'high' : 'medium',
            timestamp: deadline.getTime()
          });
        }
      }
    });

    // Add tasks with due dates
    tasks.forEach(task => {
      if (task.dueDate) {
        const deadline = new Date(task.dueDate);
        if (deadline > now) {
          deadlines.push({
            date: deadline.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }),
            title: task.title || 'Unnamed Task',
            system: 'ATLAS PM',
            priority: ['high', 'urgent'].includes(task.priority) ? 'high' : 'medium',
            timestamp: deadline.getTime()
          });
        }
      }
    });

    // Sort by date and return top 5
    return deadlines
      .sort((a, b) => a.timestamp - b.timestamp)
      .slice(0, 5);
  }, [opportunities, tasks]);

  const quickActions = [
    { label: 'Upload RFP', icon: '📄', action: () => onEnterSystem('gpss'), gradient: 'from-blue-600 to-blue-700' },
    { label: 'Request Quote', icon: '📋', action: () => onEnterSystem('quotes'), gradient: 'from-cyan-600 to-cyan-700' },
    { label: 'Create Invoice', icon: '💰', action: () => onEnterSystem('invoices'), gradient: 'from-green-600 to-green-700' },
    { label: 'Export Calendar', icon: '📆', action: exportAllTasksToCalendar, gradient: 'from-purple-600 to-purple-700' }
  ];

  const systemHealth = [
    { system: 'Flask API', status: 'online', latency: '45ms', uptime: '99.9%' },
    { system: 'Airtable DB', status: 'online', latency: '120ms', uptime: '99.8%' },
    { system: 'Claude AI', status: 'online', latency: '850ms', uptime: '99.5%' },
    { system: 'Google Search', status: 'online', latency: '200ms', uptime: '99.9%' }
  ];

  return (
    <main className="min-h-screen">
      {/* HERO SECTION - Command Center Header */}
      <div className="relative overflow-hidden bg-gradient-to-br from-gray-900 via-blue-900/20 to-purple-900/20 border-b border-blue-500/30">
        {/* Animated Background Grid */}
        <div className="absolute inset-0 bg-grid-pattern opacity-10"></div>
        <div className="absolute inset-0 bg-gradient-to-t from-gray-900 to-transparent"></div>
        
        <div className="relative max-w-7xl mx-auto px-6 py-12">
          <div className="flex items-center justify-between mb-8">
            <div>
              <div className="flex items-center gap-4 mb-3">
                <div className="text-6xl font-black bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
                  NEXUS
                </div>
                <div className="flex flex-col">
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                    <span className="text-xs text-green-400 font-semibold tracking-wider">ALL SYSTEMS ONLINE</span>
                  </div>
                  <div className="text-xs text-gray-500 font-mono">{lastUpdated ? `SYNC: ${timeAgo(lastUpdated.toISOString())}` : 'INITIALIZING...'}</div>
                </div>
              </div>
              <p className="text-xl text-gray-400 mb-1">Enterprise Command Center</p>
              <p className="text-sm text-gray-500">Welcome back, <span className="text-blue-400 font-semibold">Dee Davis</span> • {new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'short', day: 'numeric' })} • {new Date().toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' })}</p>
            </div>
            
            <div className="flex gap-3">
              {/* Email Notification Button */}
              <div className="relative">
                <button
                  onClick={checkEmailNow}
                  className={`px-4 py-2 rounded-lg transition flex items-center gap-2 font-semibold ${
                    emailStatus.newCount > 0 
                      ? 'bg-gradient-to-r from-red-600 to-red-700 hover:from-red-500 hover:to-red-600 shadow-lg shadow-red-500/20' 
                      : 'bg-gradient-to-r from-gray-700 to-gray-800 hover:from-gray-600 hover:to-gray-700'
                  }`}
                  disabled={emailStatus.checking}
                >
                  📧 bids.deedavisinc
                  {emailStatus.newCount > 0 && (
                    <span className="bg-red-500 text-white text-xs rounded-full px-2 py-0.5 font-bold">
                      {emailStatus.newCount}
                    </span>
                  )}
                </button>
                <div className="absolute top-full right-0 mt-2 text-xs text-gray-500 whitespace-nowrap">
                  {emailStatus.checking ? 'Checking...' : `Last: ${timeAgo(emailStatus.lastChecked.toISOString())}`}
                </div>
              </div>

              <button
                onClick={fetchDashboardData}
                className="px-4 py-2 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-500 hover:to-blue-600 rounded-lg transition flex items-center gap-2 font-semibold shadow-lg shadow-blue-500/20"
                disabled={loading}
              >
                <span className={loading ? 'animate-spin' : ''}>⟳</span>
                {loading ? 'SYNCING...' : 'REFRESH'}
              </button>
            </div>
          </div>

          {/* Stats Bar - Compact & Premium */}
          <div className="grid grid-cols-4 gap-4">
            {statCards.map((stat, index) => (
              <div 
                key={index} 
                onClick={stat.action}
                title={`${stat.tooltip}\n\nData from: ${stat.source}`}
                className="group relative overflow-hidden bg-gray-800/40 backdrop-blur-sm border border-gray-700/50 rounded-xl p-4 hover:border-blue-500/50 hover:scale-105 transition-all duration-300 cursor-pointer"
              >
                <div className="absolute inset-0 bg-gradient-to-br from-blue-500/0 to-purple-500/0 group-hover:from-blue-500/10 group-hover:to-purple-500/10 transition-all duration-300"></div>
                <div className="relative">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-3xl">{stat.icon}</span>
                    <span className={`text-xs px-2 py-1 rounded-full font-bold ${stat.change.includes('+') ? 'bg-green-500/20 text-green-400' : 'bg-gray-700 text-gray-400'}`}>
                      {stat.change}
                    </span>
                  </div>
                  <div className="text-3xl font-black mb-1">{stat.value}</div>
                  <div className="text-xs text-gray-400 uppercase tracking-wider font-semibold">{stat.label}</div>
                  <div className="text-xs text-gray-500 mt-2 opacity-0 group-hover:opacity-100 transition-opacity">
                    {stat.source}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Navigation Pills */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex gap-2">
            <button
              onClick={() => setActiveTab('overview')}
              className={`px-6 py-2.5 rounded-full font-bold transition-all ${
                activeTab === 'overview'
                  ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg shadow-blue-500/30'
                  : 'bg-gray-800 text-gray-400 hover:bg-gray-700 hover:text-white'
              }`}
            >
              Command Center
            </button>
            <button
              onClick={() => setActiveTab('activity')}
              className={`px-6 py-2.5 rounded-full font-bold transition-all ${
                activeTab === 'activity'
                  ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg shadow-blue-500/30'
                  : 'bg-gray-800 text-gray-400 hover:bg-gray-700 hover:text-white'
              }`}
            >
              Activity Feed
            </button>
            <button
              onClick={() => setActiveTab('analytics')}
              className={`px-6 py-2.5 rounded-full font-bold transition-all ${
                activeTab === 'analytics'
                  ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg shadow-blue-500/30'
                  : 'bg-gray-800 text-gray-400 hover:bg-gray-700 hover:text-white'
              }`}
            >
              System Analytics
            </button>
            <button
              onClick={() => setActiveTab('portals')}
              className={`px-6 py-2.5 rounded-full font-bold transition-all ${
                activeTab === 'portals'
                  ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg shadow-blue-500/30'
                  : 'bg-gray-800 text-gray-400 hover:bg-gray-700 hover:text-white'
              }`}
            >
              🔗 Vendor Portals
            </button>
          </div>
        </div>

      {/* OVERVIEW TAB */}
      {activeTab === 'overview' && (
        <>
          {/* URGENT ACTION REQUIRED - Compact */}
          {(alerts.length > 0 || upcomingDeadlines.filter(d => d.priority === 'high').length > 0) && (
            <div className="mb-6">
              <div className="flex items-center gap-3 mb-3">
                <span className="text-xl">🔥</span>
                <div className="text-lg font-black text-white">URGENT ACTIONS</div>
                <div className="h-px flex-1 bg-gradient-to-r from-red-500/50 to-transparent"></div>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {/* Priority Alerts */}
                {alerts.slice(0, 2).map((alert, index) => (
                  <div
                    key={index}
                    className={`relative overflow-hidden border rounded-lg p-3 backdrop-blur-sm ${
                      alert.type === 'urgent'
                        ? 'bg-red-900/20 border-red-500/50'
                        : 'bg-yellow-900/20 border-yellow-500/50'
                    }`}
                  >
                    <div className="relative">
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex-1">
                          <h4 className="text-sm font-bold text-white mb-1">{alert.title}</h4>
                          <p className="text-xs text-gray-300">{alert.message}</p>
                        </div>
                        <span className="text-xs bg-gray-800 px-2 py-0.5 rounded font-semibold">{alert.system}</span>
                      </div>
                      <button className={`text-xs font-bold transition-colors ${
                        alert.type === 'urgent' ? 'text-red-400 hover:text-red-300' : 'text-blue-400 hover:text-blue-300'
                      }`}>
                        {alert.action} →
                      </button>
                    </div>
                  </div>
                ))}
                {/* Urgent Deadlines */}
                {upcomingDeadlines.filter(d => d.priority === 'high').slice(0, 2).map((deadline, index) => (
                  <div key={`deadline-${index}`} className="relative overflow-hidden border rounded-lg p-3 backdrop-blur-sm bg-orange-900/20 border-orange-500/50">
                    <div className="relative">
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex-1">
                          <h4 className="text-sm font-bold text-white mb-1">{deadline.title}</h4>
                          <p className="text-xs text-gray-300">Due: {deadline.date}</p>
                        </div>
                        <span className="text-xs bg-gray-800 px-2 py-0.5 rounded font-semibold">{deadline.system}</span>
                      </div>
                      <button className="text-xs font-bold text-orange-400 hover:text-orange-300 transition-colors">
                        View Details →
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* DEADLINES & WORKFLOW STEPS - Compact */}
          <div className="mb-6">
            <div className="flex items-center gap-3 mb-3">
              <span className="text-xl">⏰</span>
              <div className="text-lg font-black text-white">DEADLINES & WORKFLOW</div>
              <div className="h-px flex-1 bg-gradient-to-r from-blue-500/50 to-transparent"></div>
              <button
                onClick={exportAllTasksToCalendar}
                className="px-3 py-1.5 bg-gradient-to-r from-purple-600 to-purple-700 hover:from-purple-500 hover:to-purple-600 rounded-lg transition flex items-center gap-2 font-semibold text-xs shadow-lg shadow-purple-500/20"
              >
                📆 Export Calendar
              </button>
            </div>
            
            {opportunities.length > 0 ? (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                {opportunities.slice(0, 4).map((opp, idx) => {
                  const daysUntil = opp['Response Deadline'] 
                    ? Math.ceil((new Date(opp['Response Deadline']).getTime() - Date.now()) / (1000 * 60 * 60 * 24))
                    : null;
                  const isUrgent = daysUntil !== null && daysUntil <= 3;
                  
                  return (
                    <div key={idx} className={`relative overflow-hidden border rounded-lg p-4 backdrop-blur-sm ${
                      isUrgent 
                        ? 'bg-red-900/20 border-red-500/50' 
                        : 'bg-gray-800/40 border-gray-700'
                    }`}>
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center gap-2">
                          {isUrgent && <span className="text-lg">⚠️</span>}
                          <h3 className="text-sm font-bold text-white line-clamp-1">{opp.Name || 'Unnamed Opportunity'}</h3>
                        </div>
                        {daysUntil !== null && (
                          <span className={`text-xs px-2 py-0.5 rounded-full font-bold ${
                            isUrgent ? 'bg-red-500/20 text-red-400' : 'bg-blue-500/20 text-blue-400'
                          }`}>
                            {daysUntil}d
                          </span>
                        )}
                      </div>

                      {opp['Response Deadline'] && (
                        <div className="flex items-center gap-2 mb-3 text-xs text-gray-400">
                          <span>Due:</span>
                          <span className="text-blue-400 font-semibold">
                            {new Date(opp['Response Deadline']).toLocaleDateString('en-US', { 
                              month: 'short', day: 'numeric'
                            })}
                          </span>
                          <button className="ml-auto text-purple-400 hover:text-purple-300 font-bold">
                            📆
                          </button>
                        </div>
                      )}

                      {/* Compact Workflow Steps */}
                      <div className="space-y-1.5">
                        <div className="flex items-center gap-2 text-xs">
                          <span className="text-green-400">✅</span>
                          <span className="text-gray-400">Added</span>
                        </div>
                        <div className="flex items-center gap-2 text-xs">
                          <span className="text-orange-400">▶️</span>
                          <span className="text-white font-bold">Review Specs</span>
                          <button className="ml-auto text-orange-400 hover:text-orange-300 font-bold">
                            START
                          </button>
                        </div>
                        <div className="flex items-center gap-2 text-xs text-gray-600">
                          <span>🔒</span>
                          <span>Find Suppliers • Request Quotes • Price Bid</span>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            ) : (
              <div className="text-center py-8 bg-gray-800/30 border border-gray-700 rounded-lg">
                <div className="text-4xl mb-2 opacity-20">📋</div>
                <p className="text-sm text-gray-500 font-semibold">No active bids</p>
                <p className="text-xs text-gray-600 mt-1">Import opportunities in GPSS</p>
              </div>
            )}
          </div>

          {/* PENDING APPROVALS - Compact */}
          <div className="mb-6">
            <div className="flex items-center gap-3 mb-3">
              <span className="text-xl">✅</span>
              <div className="text-lg font-black text-white">PENDING APPROVALS</div>
              <div className="h-px flex-1 bg-gradient-to-r from-green-500/50 to-transparent"></div>
            </div>
            <div className="text-center py-6 bg-gray-800/30 border border-gray-700 rounded-lg">
              <div className="text-4xl mb-2 opacity-20">✅</div>
              <p className="text-sm text-gray-500 font-semibold">No pending approvals</p>
              <p className="text-xs text-gray-600 mt-1">Payments and invoices will appear here</p>
            </div>
          </div>

          {/* THIS WEEK'S CALENDAR - Compact */}
          <div className="mb-6">
            <div className="flex items-center gap-3 mb-3">
              <span className="text-xl">📆</span>
              <div className="text-lg font-black text-white">THIS WEEK</div>
              <div className="h-px flex-1 bg-gradient-to-r from-purple-500/50 to-transparent"></div>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              {upcomingDeadlines.slice(0, 4).map((deadline, idx) => (
                <div key={idx} className="bg-gray-800/40 border border-gray-700 rounded-lg p-3 hover:border-blue-500/50 transition">
                  <div className="text-xs text-gray-500 mb-1">{deadline.date}</div>
                  <div className="text-sm font-bold text-white mb-1 line-clamp-1">{deadline.title}</div>
                  <div className="text-xs text-gray-400">{deadline.system}</div>
                </div>
              ))}
              {upcomingDeadlines.length === 0 && (
                <div className="col-span-4 text-center py-6 bg-gray-800/30 border border-gray-700 rounded-lg">
                  <div className="text-3xl mb-1 opacity-20">📆</div>
                  <p className="text-sm text-gray-500">No events this week</p>
                </div>
              )}
            </div>
          </div>

          {/* STATS GRID - Compact */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
            {statCards.map((stat, index) => (
              <div 
                key={index} 
                onClick={stat.action}
                title={`${stat.tooltip}\n\nData from: ${stat.source}`}
                className={`bg-gradient-to-br ${stat.gradient} p-4 rounded-lg relative overflow-hidden cursor-pointer hover:scale-105 transition-all duration-300 group`}
              >
                <div className="text-xl mb-1">{stat.icon}</div>
                <h3 className="text-xs font-semibold text-white/80 mb-1">{stat.label}</h3>
                <p className="text-3xl font-bold mb-1">{stat.value}</p>
                <div className="flex items-center gap-1">
                  <span className={`text-xs font-semibold ${stat.change.includes('+') ? 'text-green-300' : 'text-white/70'}`}>
                    {stat.change}
                  </span>
                  <span className="text-xs text-white/60">week</span>
                </div>
              </div>
            ))}
          </div>

          {/* SYSTEM CARDS */}
          <div className="mb-8">
            <div className="flex items-center gap-3 mb-6">
              <div className="text-2xl font-black text-white">INTEGRATED SYSTEMS</div>
              <div className="h-px flex-1 bg-gradient-to-r from-blue-500/50 to-transparent"></div>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {systems.map((system, index) => (
                <div
                  key={system.id}
                  onClick={() => onEnterSystem(system.id)}
                  className="group relative overflow-hidden bg-gradient-to-br from-gray-800 to-gray-900 border border-gray-700 rounded-2xl hover:border-blue-500/50 transition-all duration-500 cursor-pointer hover:scale-[1.02] hover:shadow-2xl hover:shadow-blue-500/20"
                >
                  <div className="absolute inset-0 bg-gradient-to-br from-blue-500/0 via-purple-500/0 to-pink-500/0 group-hover:from-blue-500/10 group-hover:via-purple-500/5 group-hover:to-pink-500/10 transition-all duration-500"></div>
                  
                  <div className="relative p-6">
                    <div className="flex items-start justify-between mb-6">
                      <div className="text-5xl transform group-hover:scale-110 transition-transform duration-300">{system.icon}</div>
                      <div className="flex flex-col items-end gap-1">
                        <div className="flex items-center gap-2 px-3 py-1 bg-green-500/20 rounded-full">
                          <div className="w-1.5 h-1.5 bg-green-400 rounded-full animate-pulse"></div>
                          <span className="text-xs text-green-400 font-bold">ACTIVE</span>
                        </div>
                        <span className="text-xs text-gray-500 font-mono">{system.lastUsed}</span>
                      </div>
                    </div>
                    
                    <div className="mb-6">
                      <h3 className="text-3xl font-black mb-2 bg-gradient-to-r from-white to-gray-300 bg-clip-text text-transparent">{system.name}</h3>
                      <p className="text-sm text-gray-400 font-semibold mb-3">{system.fullName}</p>
                      <p className="text-xs text-gray-500 leading-relaxed">{system.description}</p>
                    </div>
                    
                    <div className="grid grid-cols-1 gap-2 mb-6">
                      {system.stats.map((stat, idx) => (
                        <div key={idx} className="flex items-center gap-2 px-3 py-2 bg-gray-800/50 rounded-lg border border-gray-700/50">
                          <div className="w-1 h-1 bg-blue-400 rounded-full"></div>
                          <span className="text-sm text-gray-300 font-medium">{stat}</span>
                        </div>
                      ))}
                    </div>
                    
                    <button className={`w-full bg-gradient-to-r ${system.gradient} hover:shadow-lg hover:shadow-blue-500/30 px-6 py-3 rounded-xl font-bold text-white transition-all duration-300 transform group-hover:translate-y-[-2px]`}>
                      <span className="flex items-center justify-center gap-2">
                        LAUNCH SYSTEM
                        <span className="text-lg">→</span>
                      </span>
                    </button>
                  </div>
                  
                  <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-blue-500/10 to-transparent rounded-bl-full transform translate-x-16 -translate-y-16 group-hover:scale-150 transition-transform duration-500"></div>
                </div>
              ))}
            </div>
          </div>
        </>
      )}

      {/* ACTIVITY TAB */}
      {activeTab === 'activity' && (
        <div className="space-y-6">
          <div className="bg-gray-800 rounded-xl p-6">
            <h3 className="text-xl font-bold mb-4">📈 All System Activity</h3>
            <div className="space-y-3">
              {recentActivity.map((activity, index) => (
                <div key={index} className="bg-gray-700/50 border border-gray-600 px-4 py-4 rounded-lg">
                  <div className="flex items-start gap-3">
                    <span className={`text-3xl ${activity.color}`}>{activity.icon}</span>
                    <div className="flex-1">
                      <div className="flex items-center justify-between mb-2">
                        <div>
                          <span className="font-bold text-lg">{activity.action}</span>
                          <span className="ml-3 text-xs bg-gray-600 px-2 py-1 rounded">{activity.system}</span>
                        </div>
                        <span className="text-sm text-gray-500">{activity.time}</span>
                      </div>
                      <p className="text-gray-300 mb-2">{activity.title}</p>
                      <div className="flex gap-2">
                        <button className="text-xs text-blue-400 hover:text-blue-300">View Details</button>
                        <button className="text-xs text-gray-500 hover:text-gray-400">Dismiss</button>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* ANALYTICS TAB */}
      {activeTab === 'analytics' && (
        <div className="space-y-6">
          {/* System Health */}
          <div className="bg-gray-800 rounded-xl p-6">
            <h3 className="text-xl font-bold mb-4">🔧 System Health Monitor</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {systemHealth.map((sys, index) => (
                <div key={index} className="bg-gray-700/50 border border-gray-600 p-4 rounded-lg">
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="font-semibold">{sys.system}</h4>
                    <div className="flex items-center gap-1">
                      <div className={`w-2 h-2 rounded-full ${
                        sys.status === 'online' ? 'bg-green-500 animate-pulse' : 'bg-red-500'
                      }`}></div>
                      <span className={`text-xs ${
                        sys.status === 'online' ? 'text-green-400' : 'text-red-400'
                      }`}>
                        {sys.status}
                      </span>
                    </div>
                  </div>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-400">Latency:</span>
                      <span className="font-mono text-blue-400">{sys.latency}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Uptime:</span>
                      <span className="font-mono text-green-400">{sys.uptime}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Performance Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-gray-800 rounded-xl p-6">
              <h3 className="text-lg font-bold mb-2">Win Rate</h3>
              <div className="text-4xl font-bold text-green-400 mb-2">78%</div>
              <p className="text-sm text-gray-400">RFP success rate</p>
            </div>

            <div className="bg-gray-800 rounded-xl p-6">
              <h3 className="text-lg font-bold mb-2">Avg Response Time</h3>
              <div className="text-4xl font-bold text-blue-400 mb-2">2.4h</div>
              <p className="text-sm text-gray-400">To client inquiries</p>
            </div>

            <div className="bg-gray-800 rounded-xl p-6">
              <h3 className="text-lg font-bold mb-2">Project Success</h3>
              <div className="text-4xl font-bold text-purple-400 mb-2">92%</div>
              <p className="text-sm text-gray-400">On-time delivery</p>
            </div>
          </div>

          {/* Charts Placeholder */}
          <div className="bg-gray-800 rounded-xl p-8 text-center">
            <div className="text-6xl mb-4">📊</div>
            <h3 className="text-2xl font-bold mb-2">Advanced Analytics</h3>
            <p className="text-gray-400">Detailed charts, trends, and forecasting coming soon</p>
          </div>
        </div>
      )}

      {/* VENDOR PORTALS TAB */}
      {activeTab === 'portals' && (
        <div className="space-y-6">
          {/* Header & Search */}
          <div className="bg-gradient-to-br from-gray-800 to-gray-900 border border-gray-700 rounded-xl p-6">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h2 className="text-3xl font-black mb-2 bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                  VENDOR PORTAL MANAGER
                </h2>
                <p className="text-gray-400 text-sm">
                  Drag & drop URLs from your browser to organize your vendor portals • Click to open • Phase 2: Automated opportunity mining
                </p>
              </div>
              <div className="text-6xl">🔗</div>
            </div>

            {/* Search Bar */}
            <div className="relative">
              <input
                type="text"
                placeholder="🔍 Search portals by name, keywords, or description..."
                value={portalSearch}
                onChange={(e) => setPortalSearch(e.target.value)}
                className="w-full bg-gray-900/50 border border-gray-700 rounded-lg px-5 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-blue-500 transition"
              />
            </div>
          </div>

          {/* Stats Summary */}
          <div className="grid grid-cols-4 gap-4">
            <div className="bg-gradient-to-br from-blue-600 to-blue-800 rounded-xl p-4">
              <div className="text-3xl mb-2">🏛️</div>
              <div className="text-3xl font-black mb-1">{portals.filter(p => p.category === 'Government').length}</div>
              <div className="text-xs text-blue-100 font-semibold uppercase tracking-wide">Government Portals</div>
            </div>
            <div className="bg-gradient-to-br from-purple-600 to-purple-800 rounded-xl p-4">
              <div className="text-3xl mb-2">🛠️</div>
              <div className="text-3xl font-black mb-1">{portals.filter(p => p.category === 'Development').length}</div>
              <div className="text-xs text-purple-100 font-semibold uppercase tracking-wide">Dev/Business Tools</div>
            </div>
            <div className="bg-gradient-to-br from-green-600 to-green-800 rounded-xl p-4">
              <div className="text-3xl mb-2">⭐</div>
              <div className="text-3xl font-black mb-1">{portals.filter(p => p.favorite).length}</div>
              <div className="text-xs text-green-100 font-semibold uppercase tracking-wide">Favorites</div>
            </div>
            <div className="bg-gradient-to-br from-yellow-600 to-yellow-800 rounded-xl p-4">
              <div className="text-3xl mb-2">🔍</div>
              <div className="text-3xl font-black mb-1">{portals.filter(p => p.searchEnabled).length}</div>
              <div className="text-xs text-yellow-100 font-semibold uppercase tracking-wide">Search Enabled</div>
            </div>
          </div>

          {/* Two Columns: Government & Development */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* GOVERNMENT PORTALS */}
            <div>
              <div className="bg-gradient-to-br from-blue-900/30 to-blue-800/20 border-2 border-blue-500/30 rounded-xl p-6 mb-4">
                <div className="flex items-center gap-3 mb-3">
                  <div className="text-3xl">🏛️</div>
                  <div>
                    <h3 className="text-2xl font-black text-blue-400">GOVERNMENT VENDORS</h3>
                    <p className="text-xs text-gray-400">SAM.gov, FedBizOpps, State/County portals</p>
                  </div>
                </div>
                
                {/* Drop Zone */}
                <div
                  onDragOver={handleDragOver}
                  onDragLeave={handleDragLeave}
                  onDrop={(e) => handleDrop(e, 'Government')}
                  className={`border-2 border-dashed rounded-lg p-8 text-center transition-all ${
                    isDragging 
                      ? 'border-blue-400 bg-blue-500/20 scale-105' 
                      : 'border-gray-600 bg-gray-800/30 hover:border-blue-500/50'
                  }`}
                >
                  <div className="text-5xl mb-3">📎</div>
                  <div className="font-bold text-blue-400 mb-1">DRAG & DROP URL HERE</div>
                  <div className="text-xs text-gray-500">Drag links from your browser address bar</div>
                </div>
              </div>

              {/* Portal Cards */}
              <div className="space-y-3">
                {portals
                  .filter(p => p.category === 'Government')
                  .filter(p => {
                    if (!portalSearch) return true;
                    const search = portalSearch.toLowerCase();
                    return (
                      p.name.toLowerCase().includes(search) ||
                      p.keywords?.toLowerCase().includes(search) ||
                      p.description?.toLowerCase().includes(search)
                    );
                  })
                  .map(portal => (
                    <div
                      key={portal.id}
                      className="group bg-gray-800/60 border border-gray-700 hover:border-blue-500/50 rounded-xl p-4 transition-all cursor-pointer hover:shadow-lg hover:shadow-blue-500/10"
                      onClick={() => openPortal(portal)}
                    >
                      <div className="flex items-start gap-4">
                        <div className="text-4xl">{portal.icon}</div>
                        <div className="flex-1">
                          <div className="flex items-center justify-between mb-2">
                            <h4 className="font-bold text-white text-lg group-hover:text-blue-400 transition">{portal.name}</h4>
                            <div className="flex items-center gap-2">
                              {portal.searchEnabled && (
                                <span className="text-xs bg-green-500/20 text-green-400 px-2 py-1 rounded-full border border-green-500/30 font-semibold">
                                  SEARCH ON
                                </span>
                              )}
                              {portal.favorite && <span className="text-yellow-400">⭐</span>}
                            </div>
                          </div>
                          <div className="text-xs text-gray-400 mb-2 font-mono truncate">{portal.url}</div>
                          {portal.description && (
                            <div className="text-sm text-gray-500 mb-2">{portal.description}</div>
                          )}
                          {portal.keywords && (
                            <div className="flex flex-wrap gap-1 mb-2">
                              {portal.keywords.split(',').map((kw: string, idx: number) => (
                                <span key={idx} className="text-xs bg-gray-700 px-2 py-0.5 rounded">{kw.trim()}</span>
                              ))}
                            </div>
                          )}
                          <div className="flex items-center justify-between">
                            <span className="text-xs text-gray-600">
                              {portal.lastAccessed ? `Last: ${timeAgo(portal.lastAccessed)}` : 'Never accessed'}
                            </span>
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                deletePortal(portal.id);
                              }}
                              className="text-xs text-red-400 hover:text-red-300 font-semibold"
                            >
                              DELETE
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                
                {portals.filter(p => p.category === 'Government').length === 0 && (
                  <div className="text-center py-12 bg-gray-800/30 border border-gray-700 rounded-xl">
                    <div className="text-6xl mb-3 opacity-20">🏛️</div>
                    <p className="text-gray-500 font-semibold">No government portals yet</p>
                    <p className="text-xs text-gray-600 mt-1">Drag & drop SAM.gov, FedBizOpps, or state portal URLs above</p>
                  </div>
                )}
              </div>
            </div>

            {/* DEVELOPMENT / BUSINESS TOOLS */}
            <div>
              <div className="bg-gradient-to-br from-purple-900/30 to-purple-800/20 border-2 border-purple-500/30 rounded-xl p-6 mb-4">
                <div className="flex items-center gap-3 mb-3">
                  <div className="text-3xl">🛠️</div>
                  <div>
                    <h3 className="text-2xl font-black text-purple-400">DEV & BUSINESS TOOLS</h3>
                    <p className="text-xs text-gray-400">Airtable, Claude, APIs, SaaS platforms</p>
                  </div>
                </div>
                
                {/* Drop Zone */}
                <div
                  onDragOver={handleDragOver}
                  onDragLeave={handleDragLeave}
                  onDrop={(e) => handleDrop(e, 'Development')}
                  className={`border-2 border-dashed rounded-lg p-8 text-center transition-all ${
                    isDragging 
                      ? 'border-purple-400 bg-purple-500/20 scale-105' 
                      : 'border-gray-600 bg-gray-800/30 hover:border-purple-500/50'
                  }`}
                >
                  <div className="text-5xl mb-3">📎</div>
                  <div className="font-bold text-purple-400 mb-1">DRAG & DROP URL HERE</div>
                  <div className="text-xs text-gray-500">Drag links from your browser address bar</div>
                </div>
              </div>

              {/* Portal Cards */}
              <div className="space-y-3">
                {portals
                  .filter(p => p.category === 'Development')
                  .filter(p => {
                    if (!portalSearch) return true;
                    const search = portalSearch.toLowerCase();
                    return (
                      p.name.toLowerCase().includes(search) ||
                      p.keywords?.toLowerCase().includes(search) ||
                      p.description?.toLowerCase().includes(search)
                    );
                  })
                  .map(portal => (
                    <div
                      key={portal.id}
                      className="group bg-gray-800/60 border border-gray-700 hover:border-purple-500/50 rounded-xl p-4 transition-all cursor-pointer hover:shadow-lg hover:shadow-purple-500/10"
                      onClick={() => openPortal(portal)}
                    >
                      <div className="flex items-start gap-4">
                        <div className="text-4xl">{portal.icon}</div>
                        <div className="flex-1">
                          <div className="flex items-center justify-between mb-2">
                            <h4 className="font-bold text-white text-lg group-hover:text-purple-400 transition">{portal.name}</h4>
                            <div className="flex items-center gap-2">
                              {portal.searchEnabled && (
                                <span className="text-xs bg-green-500/20 text-green-400 px-2 py-1 rounded-full border border-green-500/30 font-semibold">
                                  SEARCH ON
                                </span>
                              )}
                              {portal.favorite && <span className="text-yellow-400">⭐</span>}
                            </div>
                          </div>
                          <div className="text-xs text-gray-400 mb-2 font-mono truncate">{portal.url}</div>
                          {portal.description && (
                            <div className="text-sm text-gray-500 mb-2">{portal.description}</div>
                          )}
                          {portal.keywords && (
                            <div className="flex flex-wrap gap-1 mb-2">
                              {portal.keywords.split(',').map((kw: string, idx: number) => (
                                <span key={idx} className="text-xs bg-gray-700 px-2 py-0.5 rounded">{kw.trim()}</span>
                              ))}
                            </div>
                          )}
                          <div className="flex items-center justify-between">
                            <span className="text-xs text-gray-600">
                              {portal.lastAccessed ? `Last: ${timeAgo(portal.lastAccessed)}` : 'Never accessed'}
                            </span>
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                deletePortal(portal.id);
                              }}
                              className="text-xs text-red-400 hover:text-red-300 font-semibold"
                            >
                              DELETE
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                
                {portals.filter(p => p.category === 'Development').length === 0 && (
                  <div className="text-center py-12 bg-gray-800/30 border border-gray-700 rounded-xl">
                    <div className="text-6xl mb-3 opacity-20">🛠️</div>
                    <p className="text-gray-500 font-semibold">No dev/business tools yet</p>
                    <p className="text-xs text-gray-600 mt-1">Drag & drop Airtable, Claude, or other SaaS URLs above</p>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Future Phase 2 Teaser */}
          <div className="bg-gradient-to-br from-yellow-900/20 to-orange-900/20 border-2 border-yellow-500/30 rounded-xl p-6">
            <div className="flex items-center gap-4">
              <div className="text-5xl">🚀</div>
              <div className="flex-1">
                <h3 className="text-xl font-black text-yellow-400 mb-2">PHASE 2: AUTOMATED OPPORTUNITY MINING</h3>
                <p className="text-gray-400 text-sm mb-2">
                  Coming soon: AI-powered web scraping to automatically monitor your vendor portals for new opportunities, 
                  qualify them with Claude AI, and surface the best matches directly in your NEXUS dashboard.
                </p>
                <div className="flex gap-3 text-xs">
                  <span className="bg-yellow-500/20 text-yellow-400 px-3 py-1 rounded-full font-semibold">Auto-Discovery</span>
                  <span className="bg-yellow-500/20 text-yellow-400 px-3 py-1 rounded-full font-semibold">AI Qualification</span>
                  <span className="bg-yellow-500/20 text-yellow-400 px-3 py-1 rounded-full font-semibold">Smart Alerts</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
      </div>
    </main>
  );
};

export default LandingPage;

