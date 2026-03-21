import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { ViewType } from './Header';
import { api } from '../api/client';
import { ReviewOpportunityModal } from './modals/ReviewOpportunityModal';
import { SupplierSearchModal } from './modals/SupplierSearchModal';
import AutonomousCommandCenter from './AutonomousCommandCenter';

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
    gbis: {
      active_grants: number;
      applications: number;
      awarded: number;
    };
    lbpc: {
      active_leads: number;
      pipeline: number;
      tasks_due: number;
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
      atlas: { projects: 0, rfps_analyzed: 0, total_value: 0 },
      gbis: { active_grants: 0, applications: 0, awarded: 0 },
      lbpc: { active_leads: 0, pipeline: 0, tasks_due: 0 },
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
  
  // Mining State
  const [isMining, setIsMining] = useState(false);
  const [miningStatus, setMiningStatus] = useState<any>(null);
  const [miningResult, setMiningResult] = useState<any>(null);

  // Opportunities and Tasks for Deadlines
  const [opportunities, setOpportunities] = useState<any[]>([]);
  const [tasks, setTasks] = useState<any[]>([]);

  // Workflow queues state
  const [workflowQueues, setWorkflowQueues] = useState<any>({
    needsReview: [],
    findSuppliers: [],
    requestQuotes: [],
    awaitingQuotes: [],
    readyToPrice: [],
    generateProposal: [],
    finalReview: [],
    submitted: []
  });
  const [workflowCounts, setWorkflowCounts] = useState<any>({});

  // Email monitoring state
  const [emailStatus, setEmailStatus] = useState({
    newCount: 0,
    lastChecked: new Date(),
    checking: false,
    recentActivity: [] as any[]
  });

  // Review modal state
  const [reviewingOpportunity, setReviewingOpportunity] = useState<any>(null);
  
  // Supplier search modal state
  const [searchingSuppliersFor, setSearchingSuppliersFor] = useState<any>(null);

  // Pipeline health state
  const [pipelineHealth, setPipelineHealth] = useState<any>(null);

  // Fetch dashboard data
  const fetchDashboardData = useCallback(async () => {
    try {
      const [statsData, activityData, alertsData] = await Promise.all([
        api.getDashboardStats(),
        api.getDashboardActivity(),
        api.getDashboardAlerts()
      ]);

      const merged = { ...defaultStats, ...statsData };
      if (!merged.systems.gbis) merged.systems.gbis = defaultStats.systems.gbis;
      if (!merged.systems.lbpc) merged.systems.lbpc = defaultStats.systems.lbpc;

      // Pull live stats for GBIS and LBPC
      try {
        const [gbisRes, lbpcRes] = await Promise.allSettled([
          api.get('/gbis/stats'),
          api.get('/lbpc/stats'),
        ]);
        if (gbisRes.status === 'fulfilled') {
          const g = (gbisRes.value as any) || {};
          merged.systems.gbis = {
            active_grants: g.activeOpportunities || g.active_opportunities || 0,
            applications: g.totalApplications || g.total_applications || 0,
            awarded: g.totalAwarded || g.total_awarded || 0,
          };
        }
        if (lbpcRes.status === 'fulfilled') {
          const l = (lbpcRes.value as any) || {};
          merged.systems.lbpc = {
            active_leads: l.totalLeads || l.active_leads || 0,
            pipeline: l.totalRecoveryPotential || l.total_surplus || 0,
            tasks_due: l.newLeads || l.tasks_due || 0,
          };
        }
      } catch { /* fallback to zeros */ }

      setStats(merged);
      setActivities(activityData.activities || []);
      setAlerts(alertsData.alerts || []);
      setLastUpdated(new Date());
      setLoading(false);

      try {
        const ph = await api.getPipelineHealth();
        setPipelineHealth(ph);
      } catch { /* pipeline offline */ }
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
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

  // Fetch workflow queues
  const fetchWorkflowQueues = useCallback(async () => {
    try {
      const response = await api.getWorkflowQueues();
      if (response.success) {
        setWorkflowQueues(response.queues || {});
        setWorkflowCounts(response.counts || {});
      }
    } catch (error) {
      console.error('Error fetching workflow queues:', error);
      
      // API failed — show empty state, no fake data
      setWorkflowQueues({
        needsReview: [],
        findSuppliers: [],
        requestQuotes: [],
        awaitingQuotes: [],
        readyToPrice: [],
        generateProposal: [],
        finalReview: [],
        submitted: []
      });
      setWorkflowCounts({});
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

  // Fetch mining status
  const fetchMiningStatus = async () => {
    try {
      const response = await api.getMiningStatus();
      setMiningStatus(response);
    } catch (error) {
      console.error('Error fetching mining status:', error);
    }
  };

  // Run mining on all portals
  const runMiningNow = async () => {
    setIsMining(true);
    setMiningResult(null);
    try {
      const result = await api.autoMineAll();
      setMiningResult(result);
      fetchMiningStatus();
    } catch (error) {
      console.error('Mining error:', error);
      setMiningResult({ error: 'Mining failed — check backend logs' });
    } finally {
      setIsMining(false);
    }
  };

  // Mine single portal
  const minePortal = async (portalId: string) => {
    try {
      const result = await api.minePortal(portalId);
      alert(`Found ${result.opportunities_found || 0} opportunities from ${result.portal_name || 'portal'}`);
      fetchMiningStatus();
    } catch (error) {
      console.error('Portal mining error:', error);
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

  const handleDrop = async (e: React.DragEvent, category: string) => {
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

  // Handle successful opportunity review
  const handleReviewSuccess = useCallback(() => {
    // Refresh workflow queues to show updated data
    fetchWorkflowQueues();
    fetchDeadlineData();
  }, [fetchWorkflowQueues, fetchDeadlineData]);

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
    fetchWorkflowQueues();
    fetchMiningStatus();
    
    const interval = setInterval(() => {
      fetchDashboardData();
      fetchDeadlineData();
      fetchWorkflowQueues();
    }, 30000); // 30 seconds

    return () => clearInterval(interval);
  }, [fetchDashboardData, fetchDeadlineData, fetchWorkflowQueues]);

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

  // PRIMARY WORKFLOW SYSTEMS - Your daily drivers
  const coreSystems = [
    {
      id: 'opportunity-hunter' as ViewType,
      name: 'NOVA',
      fullName: 'New Opportunity Vetting & Acquisition',
      icon: '🌟',
      description: 'Find federal contracts • 3/day target • Live SAM.gov search',
      stats: [
        'Live SAM.gov Search',
        'Quick Wins Mode',
        'Daily Target Tracker',
        'Agency Intelligence'
      ],
      gradient: 'from-violet-600 to-indigo-600',
      status: 'online',
      lastUsed: 'NEW! 🔥',
      phase: '1. DISCOVER'
    },
    {
      id: 'gpss' as ViewType,
      name: 'GPSS',
      fullName: 'Government Prime Sales System',
      icon: '🎯',
      description: 'Manage pipeline • Submit proposals • Track opportunities',
      stats: [
        `${stats.systems.gpss.opportunities} Active RFP${stats.systems.gpss.opportunities !== 1 ? 's' : ''}`,
        `${formatNumber(stats.systems.gpss.pipeline)} Pipeline`,
        `${stats.systems.gpss.contacts} Contact${stats.systems.gpss.contacts !== 1 ? 's' : ''}`
      ],
      gradient: 'from-blue-600 to-purple-600',
      status: 'online',
      lastUsed: '2 min ago',
      phase: '2. PURSUE'
    },
    {
      id: 'atlas' as ViewType,
      name: 'ATLAS PM',
      fullName: 'Project Management System',
      icon: '🏗️',
      description: 'Analyze RFPs • Generate WBS • Track projects',
      stats: [
        `${stats.systems.atlas.projects} Project${stats.systems.atlas.projects !== 1 ? 's' : ''}`,
        `${stats.systems.atlas.rfps_analyzed} RFP${stats.systems.atlas.rfps_analyzed !== 1 ? 's' : ''} Analyzed`,
        `${formatNumber(stats.systems.atlas.total_value)} Value`
      ],
      gradient: 'from-purple-600 to-pink-600',
      status: 'online',
      lastUsed: 'Just now',
      phase: '3. PLAN'
    },
    {
      id: 'prism' as ViewType,
      name: 'PRISM',
      fullName: 'Field Service Command Center',
      icon: '🔮',
      description: 'Dispatch agents • Track orders • Scanbacks & inspections',
      stats: [
        '10 Active Orders',
        '5 Field Agents',
        '82% First-Pass Rate',
        'See Every Detail'
      ],
      gradient: 'from-orange-500 to-amber-600',
      status: 'online',
      lastUsed: 'NEW! 🔥',
      phase: '4. EXECUTE'
    },
    {
      id: 'compass' as ViewType,
      name: 'COMPASS',
      fullName: 'Post-Award Fulfillment',
      icon: '🧭',
      description: 'Deliver contracts • Track compliance • Manage subcontractors',
      stats: [
        '0 Active Contracts',
        '$0 Under Management',
        'Nothing Falls Through!'
      ],
      gradient: 'from-yellow-600 to-red-600',
      status: 'online',
      lastUsed: 'COMING SOON',
      phase: '5. DELIVER'
    },
    {
      id: 'vertex' as ViewType,
      name: 'VERTEX',
      fullName: 'Financial Command Center',
      icon: '💎',
      description: 'Invoices • Expenses • Revenue • P&L • QB Export',
      stats: [
        'P&L Tracker (NEW!)',
        'Invoices + Expenses',
        'Revenue Tracking',
        'Financial Reports'
      ],
      gradient: 'from-purple-600 to-pink-600',
      status: 'online',
      lastUsed: 'NEW! 🔥',
      phase: '6. FINANCE'
    }
  ];

  // SUPPORT SYSTEMS - Available but secondary
  const supportSystems = [
    {
      id: 'documents' as ViewType,
      name: 'DOCUMENTS',
      fullName: 'Document & Pricing Hub',
      icon: '📄',
      description: 'Quotes • Cap Statements • RFPs • Pricing Engine',
      stats: ['Quote Generator', 'Cap Statements', 'Pricing Engine'],
      gradient: 'from-blue-600 to-cyan-600',
      status: 'online',
      lastUsed: 'Available'
    },
    {
      id: 'ddcss' as ViewType,
      name: 'DDCSS',
      fullName: 'Corporate Sales System',
      icon: '💼',
      description: 'Blueprint Framework • 6 Sectors • AI Copilot',
      stats: ['Corporate Pipeline', 'Private Sector', 'B2B Sales'],
      gradient: 'from-green-600 to-blue-600',
      status: 'online',
      lastUsed: 'Available'
    },
    {
      id: 'gbis' as ViewType,
      name: 'GBIS',
      fullName: 'Grant Business Intelligence',
      icon: '🎁',
      description: 'Grant Discovery • AI Applications • ROI Tracking',
      stats: ['Grant Opportunities', 'Application Tracker', 'Award Monitor'],
      gradient: 'from-yellow-600 to-orange-600',
      status: 'online',
      lastUsed: 'Available'
    },
    {
      id: 'lbpc' as ViewType,
      name: 'LBPC',
      fullName: 'Surplus Recovery System',
      icon: '💰',
      description: 'Surplus Recovery • All 50 States • Automated Workflows',
      stats: ['State Surplus', 'Recovery Tracking', 'Lead Management'],
      gradient: 'from-indigo-600 to-purple-600',
      status: 'online',
      lastUsed: 'Available'
    },
    {
      id: 'alexa' as ViewType,
      name: 'ALEXA',
      fullName: 'Voice Command Center',
      icon: '🎙️',
      description: '98 Voice Commands • Test Lab • All NEXUS Systems Connected',
      stats: ['98 Commands', 'Live Testing', 'Full NEXUS Access'],
      gradient: 'from-cyan-600 to-blue-600',
      status: 'online',
      lastUsed: 'Connected'
    }
  ];

  // Use live activities or fallback to empty array
  const recentActivity = activities.map(activity => ({
    ...activity,
    time: timeAgo(activity.time)
  }));

  // Build upcoming deadlines from real opportunities and tasks
  const upcomingDeadlines = useMemo(() => {
    const deadlines: Array<{ date: string; title: string; system: string; priority: string; timestamp: number; id?: string; oppId?: string; rfpNumber?: string; status?: string }> = [];
    const now = new Date();

    // Add opportunities — ONLY pipeline / active / presolicitation / sources sought
    const SHOW_STATUSES = [
      'active', 'pursuing', 'awaiting quotes', 'ready to bid', 'submitted',
      'submitted - awaiting award', 'in-progress', 'not started',
      'sources sought', 'presolicitation', 'sole source', 'intent to sole source',
      'no contact yet', 'active - analyzing', 'solicitation', 'conditional',
    ];
    
    opportunities.forEach(opp => {
      const deadlineStr = opp['Response Deadline'] || opp['Deadline'] || opp['dueDate'] || opp['deadline'];
      if (!deadlineStr) return;
      
      // Only show pipeline or relevant status
      const status = (opp['Status'] || opp['internalStatus'] || opp['status'] || '').toLowerCase();
      const isRelevant = opp.isPipeline || SHOW_STATUSES.some(s => status.includes(s));
      if (!isRelevant) return;

      const deadline = new Date(deadlineStr);
      if (!isNaN(deadline.getTime()) && deadline > now) {
        deadlines.push({
          date: deadline.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }),
          title: opp.Name || opp.Title || opp.title || 'Unnamed Opportunity',
          system: 'GPSS',
          priority: (opp['Priority'] === 'High' || opp['priority'] === 'high') ? 'high' : 'medium',
          timestamp: deadline.getTime(),
          id: opp.id || opp.airtable_id,
          oppId: opp.id || opp.airtable_id,
          rfpNumber: opp['RFP NUMBER'] || opp['rfpNumber'] || '',
          status: opp['Status'] || opp['internalStatus'] || '',
        });
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
            timestamp: deadline.getTime(),
            id: task.id,
            status: task.status || '',
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
    { label: 'Request Quote', icon: '📋', action: () => onEnterSystem('documents'), gradient: 'from-cyan-600 to-cyan-700' },
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
    <>
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
          {/* AUTONOMOUS COMMAND CENTER - Shows what NEXUS recommends you do */}
          <div className="mb-8">
            <AutonomousCommandCenter onEnterSystem={onEnterSystem} />
          </div>

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
                    className={`relative overflow-hidden border rounded-lg p-3 backdrop-blur-sm cursor-pointer hover:opacity-90 transition-all ${
                      alert.type === 'urgent'
                        ? 'bg-red-900/20 border-red-500/50'
                        : 'bg-yellow-900/20 border-yellow-500/50'
                    }`}
                    onClick={() => {
                      const systemMap: { [key: string]: ViewType } = {
                        'GPSS': 'gpss',
                        'DDCSS': 'ddcss',
                        'ATLAS': 'atlas',
                        'GBIS': 'gbis',
                        'VERTEX': 'vertex'
                      };
                      const system = systemMap[alert.system];
                      if (system) {
                        onEnterSystem(system);
                      } else {
                        window.alert(`📋 ${alert.title}\n\n${alert.message}\n\nSystem: ${alert.system}`);
                      }
                    }}
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
                      }`} onClick={(e) => e.stopPropagation()}>
                        {alert.action} →
                      </button>
                    </div>
                  </div>
                ))}
                {/* Urgent Deadlines */}
                {upcomingDeadlines.filter(d => d.priority === 'high').slice(0, 2).map((deadline, index) => (
                  <div key={`deadline-${index}`} className="relative overflow-hidden border rounded-lg p-3 backdrop-blur-sm bg-orange-900/20 border-orange-500/50 cursor-pointer hover:bg-orange-900/30 transition-colors"
                    onClick={() => {
                      if (deadline.system === 'GPSS') {
                        onEnterSystem('gpss');
                      } else if (deadline.system === 'ATLAS') {
                        onEnterSystem('atlas');
                      } else {
                        window.alert(`📋 ${deadline.title}\n\nDue: ${deadline.date}\nSystem: ${deadline.system}\n\n💡 Click on ${deadline.system} in the header to view this opportunity.`);
                      }
                    }}>
                    <div className="relative">
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex-1">
                          <h4 className="text-sm font-bold text-white mb-1">{deadline.title}</h4>
                          <p className="text-xs text-gray-300">Due: {deadline.date}</p>
                        </div>
                        <span className="text-xs bg-gray-800 px-2 py-0.5 rounded font-semibold">{deadline.system}</span>
                      </div>
                      <button className="text-xs font-bold text-orange-400 hover:text-orange-300 transition-colors" onClick={(e) => e.stopPropagation()}>
                        Click to Open {deadline.system} →
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* WORKFLOW QUEUES - COMPACT 2-COLUMN GRID */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-4">
            
            {/* 1. NEEDS REVIEW */}
            <div>
              <div className="flex items-center gap-2 mb-2">
                <span className="text-base">🔍</span>
                <div className="text-xs font-black text-white">NEEDS REVIEW</div>
                <span className="text-xs bg-blue-500/20 text-blue-400 px-2 py-0.5 rounded-full font-bold">
                  {workflowCounts.needsReview || 0}
                </span>
                <div className="h-px flex-1 bg-gradient-to-r from-blue-500/30 to-transparent"></div>
              </div>
              {workflowQueues.needsReview && workflowQueues.needsReview.length > 0 ? (
                <div className="space-y-2">
                  {workflowQueues.needsReview.slice(0, 2).map((opp: any) => (
                    <div key={opp.id} className="bg-blue-900/10 border border-blue-500/30 rounded p-2 hover:border-blue-500/50 transition">
                      <div className="flex items-center justify-between gap-2">
                        <div className="flex-1 min-w-0">
                          <div className="text-xs font-bold text-white mb-0.5 truncate">
                            {opp.fields.Name || 'Unnamed Opportunity'}
                          </div>
                          <div className="text-xs text-gray-500">
                            Added: {opp.fields['Date Added'] ? new Date(opp.fields['Date Added']).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }) : 'Recently'}
                          </div>
                        </div>
                        <button 
                          onClick={() => setReviewingOpportunity(opp)}
                          className="px-2 py-1 bg-blue-600 hover:bg-blue-700 rounded text-xs font-bold transition shrink-0"
                        >
                          Review
                        </button>
                      </div>
                    </div>
                  ))}
                  {workflowQueues.needsReview.length > 2 && (
                    <button className="text-xs text-blue-400 hover:text-blue-300 font-bold w-full text-center py-1">
                      +{workflowQueues.needsReview.length - 2} more
                    </button>
                  )}
                </div>
              ) : (
                <div className="text-center py-3 bg-gray-800/20 border border-gray-700 rounded">
                  <div className="text-xs text-gray-500">✅ All caught up</div>
                </div>
              )}
            </div>

            {/* 2. FIND SUPPLIERS */}
            <div>
              <div className="flex items-center gap-2 mb-2">
                <span className="text-base">🔎</span>
                <div className="text-xs font-black text-white">FIND SUPPLIERS</div>
                <span className="text-xs bg-purple-500/20 text-purple-400 px-2 py-0.5 rounded-full font-bold">
                  {workflowCounts.findSuppliers || 0}
                </span>
                <div className="h-px flex-1 bg-gradient-to-r from-purple-500/30 to-transparent"></div>
              </div>
              {workflowQueues.findSuppliers && workflowQueues.findSuppliers.length > 0 ? (
                <div className="space-y-2">
                  {workflowQueues.findSuppliers.slice(0, 2).map((opp: any) => (
                    <div key={opp.id} className="bg-purple-900/10 border border-purple-500/30 rounded p-2 hover:border-purple-500/50 transition">
                      <div className="flex items-center justify-between gap-2">
                        <div className="flex-1 min-w-0">
                          <div className="text-xs font-bold text-white mb-0.5 truncate">{opp.fields.Name}</div>
                          <div className="text-xs text-gray-500">
                            Due: {opp.fields['Response Deadline'] ? new Date(opp.fields['Response Deadline']).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }) : 'TBD'}
                          </div>
                        </div>
                        <button 
                          onClick={() => setSearchingSuppliersFor(opp)}
                          className="px-2 py-1 bg-purple-600 hover:bg-purple-700 rounded text-xs font-bold transition shrink-0"
                        >
                          Search
                        </button>
                      </div>
                    </div>
                  ))}
                  {workflowQueues.findSuppliers.length > 2 && (
                    <button className="text-xs text-purple-400 hover:text-purple-300 font-bold w-full text-center py-1">
                      +{workflowQueues.findSuppliers.length - 2} more
                    </button>
                  )}
                </div>
              ) : (
                <div className="text-center py-3 bg-gray-800/20 border border-gray-700 rounded">
                  <div className="text-xs text-gray-500">✅ All identified</div>
                </div>
              )}
            </div>

            {/* 3. AWAITING QUOTES */}
            <div>
              <div className="flex items-center gap-2 mb-2">
                <span className="text-base">⏳</span>
                <div className="text-xs font-black text-white">AWAITING QUOTES</div>
                <span className="text-xs bg-yellow-500/20 text-yellow-400 px-2 py-0.5 rounded-full font-bold">
                  {workflowCounts.awaitingQuotes || 0}
                </span>
                <div className="h-px flex-1 bg-gradient-to-r from-yellow-500/30 to-transparent"></div>
              </div>
              {workflowQueues.awaitingQuotes && workflowQueues.awaitingQuotes.length > 0 ? (
                <div className="space-y-2">
                  {workflowQueues.awaitingQuotes.slice(0, 2).map((opp: any) => {
                    const quotesReceived = opp.fields['Quotes Received'] || 0;
                    const quotesRequested = opp.fields['Quotes Requested'] || 0;
                    const percentage = quotesRequested > 0 ? Math.round((quotesReceived / quotesRequested) * 100) : 0;
                    
                    return (
                      <div key={opp.id} className="bg-yellow-900/10 border border-yellow-500/30 rounded p-2 hover:border-yellow-500/50 transition">
                        <div className="flex items-center justify-between gap-2 mb-1">
                          <div className="flex-1 min-w-0">
                            <div className="text-xs font-bold text-white mb-0.5 truncate">{opp.fields.Name}</div>
                            <div className="text-xs text-gray-500">{quotesReceived}/{quotesRequested} quotes</div>
                          </div>
                        </div>
                        <div className="w-full bg-gray-700 rounded-full h-1">
                          <div 
                            className="bg-gradient-to-r from-yellow-500 to-green-500 h-1 rounded-full transition-all"
                            style={{ width: `${percentage}%` }}
                          ></div>
                        </div>
                      </div>
                    );
                  })}
                  {workflowQueues.awaitingQuotes.length > 2 && (
                    <button className="text-xs text-yellow-400 hover:text-yellow-300 font-bold w-full text-center py-1">
                      +{workflowQueues.awaitingQuotes.length - 2} more
                    </button>
                  )}
                </div>
              ) : (
                <div className="text-center py-3 bg-gray-800/20 border border-gray-700 rounded">
                  <div className="text-xs text-gray-500">✅ All received</div>
                </div>
              )}
            </div>

            {/* 4. READY TO PRICE */}
            <div>
              <div className="flex items-center gap-2 mb-2">
                <span className="text-base">💰</span>
                <div className="text-xs font-black text-white">READY TO PRICE</div>
                <span className="text-xs bg-green-500/20 text-green-400 px-2 py-0.5 rounded-full font-bold">
                  {workflowCounts.readyToPrice || 0}
                </span>
                <div className="h-px flex-1 bg-gradient-to-r from-green-500/30 to-transparent"></div>
              </div>
              {workflowQueues.readyToPrice && workflowQueues.readyToPrice.length > 0 ? (
                <div className="space-y-2">
                  {workflowQueues.readyToPrice.slice(0, 2).map((opp: any) => (
                    <div key={opp.id} className="bg-green-900/10 border border-green-500/30 rounded p-2 hover:border-green-500/50 transition">
                      <div className="flex items-center justify-between gap-2">
                        <div className="flex-1 min-w-0">
                          <div className="text-xs font-bold text-white mb-0.5 truncate">{opp.fields.Name}</div>
                          <div className="text-xs text-gray-500">{opp.fields['Quotes Received'] || 0} quotes</div>
                        </div>
                        <button 
                          onClick={() => onEnterSystem('documents' as ViewType)}
                          className="px-2 py-1 bg-green-600 hover:bg-green-700 rounded text-xs font-bold transition shrink-0"
                        >
                          Price
                        </button>
                      </div>
                    </div>
                  ))}
                  {workflowQueues.readyToPrice.length > 2 && (
                    <button className="text-xs text-green-400 hover:text-green-300 font-bold w-full text-center py-1">
                      +{workflowQueues.readyToPrice.length - 2} more
                    </button>
                  )}
                </div>
              ) : (
                <div className="text-center py-3 bg-gray-800/20 border border-gray-700 rounded">
                  <div className="text-xs text-gray-500">✅ All priced</div>
                </div>
              )}
            </div>
          </div>

          {/* THIS WEEK & PENDING - COMBINED ROW */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-4">
            {/* THIS WEEK'S CALENDAR - Compact */}
            <div>
              <div className="flex items-center gap-2 mb-2">
                <span className="text-base">📆</span>
                <div className="text-xs font-black text-white">THIS WEEK</div>
                <div className="h-px flex-1 bg-gradient-to-r from-purple-500/30 to-transparent"></div>
              </div>
              <div className="grid grid-cols-2 gap-2">
                {upcomingDeadlines.slice(0, 2).map((deadline, idx) => (
                  <div
                    key={idx}
                    className="bg-gray-800/40 border border-gray-700 rounded p-2 hover:border-blue-500/50 hover:bg-gray-700/50 transition cursor-pointer group"
                    onClick={() => {
                      if (deadline.system === 'GPSS') {
                        onEnterSystem('gpss');
                      } else if (deadline.system === 'ATLAS PM') {
                        onEnterSystem('atlas');
                      }
                    }}
                  >
                    <div className="flex items-center justify-between mb-0.5">
                      <div className="text-xs text-gray-500">{deadline.date}</div>
                      <div className={`w-2 h-2 rounded-full ${deadline.priority === 'high' ? 'bg-red-400' : 'bg-blue-400'}`} />
                    </div>
                    <div className="text-xs font-bold text-white mb-0.5 line-clamp-1 group-hover:text-blue-300 transition-colors">{deadline.title}</div>
                    <div className="flex items-center justify-between">
                      <div className="text-xs text-gray-400">{deadline.system}</div>
                      <div className="text-xs text-blue-400 opacity-0 group-hover:opacity-100 transition-opacity">View →</div>
                    </div>
                  </div>
                ))}
                {upcomingDeadlines.length === 0 && (
                  <div className="col-span-2 text-center py-3 bg-gray-800/30 border border-gray-700 rounded">
                    <div className="text-xs text-gray-500">📆 No events</div>
                  </div>
                )}
              </div>
            </div>

            {/* PENDING APPROVALS - Compact */}
            <div>
              <div className="flex items-center gap-2 mb-2">
                <span className="text-base">✅</span>
                <div className="text-xs font-black text-white">PENDING APPROVALS</div>
                <div className="h-px flex-1 bg-gradient-to-r from-green-500/30 to-transparent"></div>
              </div>
              <div className="text-center py-8 bg-gray-800/20 border border-gray-700 rounded">
                <div className="text-2xl mb-1 opacity-20">✅</div>
                <p className="text-xs text-gray-500">No pending approvals</p>
              </div>
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

          {/* NEXUS INTEGRATION PIPELINE — System Connections */}
          {pipelineHealth && (
            <div className="mb-8">
              <div className="flex items-center gap-3 mb-4">
                <div className="text-lg font-black text-white bg-gradient-to-r from-emerald-400 to-cyan-400 bg-clip-text text-transparent">
                  INTEGRATION PIPELINE
                </div>
                <div className="h-px flex-1 bg-gradient-to-r from-emerald-500/50 to-transparent"></div>
                <div className="flex items-center gap-2 px-3 py-1 bg-emerald-500/10 border border-emerald-500/30 rounded-full">
                  <div className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse"></div>
                  <span className="text-xs text-emerald-400 font-bold">{pipelineHealth.status?.toUpperCase()}</span>
                </div>
                <span className="text-xs text-gray-500 font-mono">
                  {pipelineHealth.registry?.active_contracts || 0} contracts | {pipelineHealth.registry?.total_events || 0} events
                </span>
              </div>

              <div className="bg-gray-800/50 border border-gray-700 rounded-xl p-5">
                {/* Core Contract Lifecycle Flow */}
                <div className="text-[10px] text-gray-500 font-bold mb-3 text-center tracking-wider">CONTRACT LIFECYCLE</div>
                <div className="flex items-center justify-center gap-0 overflow-x-auto pb-1">
                  {(() => {
                    const lifecycle = [
                      { id: 'NOVA', label: 'NOVA', sub: 'Find', icon: '🔍' },
                      { id: 'GPSS', label: 'GPSS', sub: 'Bid', icon: '📋' },
                      { id: 'ATLAS', label: 'ATLAS', sub: 'Plan', icon: '📐' },
                      { id: 'PRISM', label: 'PRISM', sub: 'Execute', icon: '⚡' },
                      { id: 'COMPASS', label: 'COMPASS', sub: 'Manage', icon: '🧭' },
                      { id: 'VERTEX', label: 'VERTEX', sub: 'Invoice', icon: '💰' },
                    ];
                    const systems = pipelineHealth.systems || {};
                    return lifecycle.map((sys, i) => (
                      <React.Fragment key={sys.id}>
                        <div className="flex flex-col items-center min-w-[72px]">
                          <div className={`w-12 h-12 rounded-xl flex flex-col items-center justify-center ${
                            systems[sys.id]?.status === 'online'
                              ? 'bg-emerald-500/15 border-2 border-emerald-500/50 shadow-lg shadow-emerald-500/10'
                              : 'bg-yellow-500/15 border-2 border-yellow-500/50'
                          }`}>
                            <span className="text-base leading-none">{sys.icon}</span>
                            <span className={`text-[9px] font-black mt-0.5 ${
                              systems[sys.id]?.status === 'online' ? 'text-emerald-400' : 'text-yellow-400'
                            }`}>{sys.label}</span>
                          </div>
                          <span className="text-[9px] text-gray-500 mt-1 font-medium">{sys.sub}</span>
                        </div>
                        {i < lifecycle.length - 1 && (
                          <div className="flex flex-col items-center mx-1 mt-[-8px]">
                            <div className="flex items-center">
                              <div className="h-0.5 w-5 bg-emerald-500/60"></div>
                              <div className="w-0 h-0 border-t-[3px] border-t-transparent border-b-[3px] border-b-transparent border-l-[5px] border-l-emerald-500/60"></div>
                            </div>
                          </div>
                        )}
                      </React.Fragment>
                    ));
                  })()}
                </div>

                {/* Support Systems feeding into the pipeline */}
                <div className="mt-4 pt-3 border-t border-gray-700/50">
                  <div className="text-[10px] text-gray-500 font-bold mb-2.5 text-center tracking-wider">SUPPORT SYSTEMS</div>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                    {[
                      { id: 'DDCSS', icon: '💼', label: 'DDCSS', desc: 'Corporate Sales', feeds: 'ATLAS + VERTEX', color: 'blue' },
                      { id: 'GBIS', icon: '🎁', label: 'GBIS', desc: 'Grant Intel', feeds: 'VERTEX', color: 'yellow' },
                      { id: 'DOCUMENTS', icon: '📄', label: 'DOCS', desc: 'Quotes & Cap Stmts', feeds: 'GPSS + DDCSS', color: 'cyan' },
                      { id: 'LBPC', icon: '🏷️', label: 'LBPC', desc: 'Surplus Recovery', feeds: 'GPSS + VERTEX', color: 'purple' },
                    ].map((sys) => (
                      <div key={sys.id} className="flex items-center gap-2 px-3 py-2 bg-gray-700/30 border border-gray-700 rounded-lg">
                        <span className="text-sm">{sys.icon}</span>
                        <div className="flex-1 min-w-0">
                          <div className="text-[10px] font-black text-gray-300">{sys.label}</div>
                          <div className="text-[9px] text-gray-500 truncate">{sys.desc}</div>
                        </div>
                        <div className="text-[8px] text-gray-600 whitespace-nowrap">→ {sys.feeds}</div>
                      </div>
                    ))}
                  </div>
                  <div className="flex items-center justify-center gap-3 mt-2">
                    <div className="flex items-center gap-1.5 px-2 py-1 bg-gray-700/20 rounded text-[9px]">
                      <span>🎙️</span>
                      <span className="text-gray-400 font-bold">ALEXA</span>
                      <span className="text-gray-600">— Voice interface to all systems</span>
                    </div>
                  </div>
                </div>

                {/* Recent Events */}
                {(pipelineHealth.recent_events || []).length > 0 && (
                  <div className="mt-3 pt-3 border-t border-gray-700/50">
                    <div className="text-[10px] text-gray-500 font-bold mb-1.5">RECENT PIPELINE EVENTS</div>
                    <div className="flex flex-wrap gap-2">
                      {(pipelineHealth.recent_events || []).slice(0, 5).map((evt: any, i: number) => (
                        <div key={i} className="flex items-center gap-1.5 px-2.5 py-1 bg-gray-700/40 border border-gray-700 rounded-lg text-[10px]">
                          <span className="text-emerald-400 font-bold">{evt.source}</span>
                          <span className="text-gray-600">→</span>
                          <span className="text-cyan-400 font-bold">{evt.target}</span>
                          <span className="text-gray-400 ml-1">{evt.type?.replace(/_/g, ' ')}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* CORE WORKFLOW SYSTEMS - Your Daily Driver */}
          <div className="mb-8">
            <div className="flex items-center gap-3 mb-6">
              <div className="text-2xl font-black text-white bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                CORE WORKFLOW SYSTEMS
              </div>
              <div className="h-px flex-1 bg-gradient-to-r from-blue-500/50 to-transparent"></div>
              <span className="text-sm text-gray-500">Your contract lifecycle</span>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {coreSystems.map((system) => (
                <div
                  key={system.id}
                  onClick={() => onEnterSystem(system.id)}
                  className="group relative overflow-hidden bg-gradient-to-br from-gray-800 to-gray-900 border border-gray-700 rounded-2xl hover:border-blue-500/50 transition-all duration-500 cursor-pointer hover:scale-[1.02] hover:shadow-2xl hover:shadow-blue-500/20"
                >
                  {/* Phase Badge */}
                  <div className="absolute top-4 left-4">
                    <span className="px-2 py-1 bg-gray-700/80 text-gray-300 text-xs rounded font-mono">
                      {system.phase}
                    </span>
                  </div>
                  
                  <div className="absolute inset-0 bg-gradient-to-br from-blue-500/0 via-purple-500/0 to-pink-500/0 group-hover:from-blue-500/10 group-hover:via-purple-500/5 group-hover:to-pink-500/10 transition-all duration-500"></div>
                  
                  <div className="relative p-6 pt-12">
                    <div className="flex items-start justify-between mb-4">
                      <div className="text-4xl transform group-hover:scale-110 transition-transform duration-300">{system.icon}</div>
                      <div className="flex flex-col items-end gap-1">
                        <div className="flex items-center gap-2 px-3 py-1 bg-green-500/20 rounded-full">
                          <div className="w-1.5 h-1.5 bg-green-400 rounded-full animate-pulse"></div>
                          <span className="text-xs text-green-400 font-bold">ACTIVE</span>
                        </div>
                        <span className="text-xs text-gray-500 font-mono">{system.lastUsed}</span>
                      </div>
                    </div>
                    
                    <div className="mb-4">
                      <h3 className="text-2xl font-black mb-1 bg-gradient-to-r from-white to-gray-300 bg-clip-text text-transparent">{system.name}</h3>
                      <p className="text-xs text-gray-400">{system.fullName}</p>
                    </div>
                    
                    <p className="text-sm text-gray-300 mb-4">{system.description}</p>
                    
                    <div className="flex flex-wrap gap-2 mb-4">
                      {system.stats.slice(0, 2).map((stat, idx) => (
                        <span key={idx} className="px-2 py-1 bg-gray-700/50 rounded text-xs text-gray-300">
                          {stat}
                        </span>
                      ))}
                    </div>
                    
                    <button className={`w-full bg-gradient-to-r ${system.gradient} hover:shadow-lg px-4 py-3 rounded-xl font-bold text-white text-sm transition-all`}>
                      Open {system.name} →
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* SUPPORT SYSTEMS - Available When Needed */}
          <div className="mb-8">
            <div className="flex items-center gap-3 mb-4">
              <div className="text-lg font-semibold text-gray-400">Support Systems</div>
              <div className="h-px flex-1 bg-gradient-to-r from-gray-700/50 to-transparent"></div>
            </div>
            
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {supportSystems.map((system) => (
                <div
                  key={system.id}
                  onClick={() => onEnterSystem(system.id)}
                  className="group bg-gray-800/50 border border-gray-700/50 rounded-xl p-4 hover:border-gray-600 cursor-pointer transition-all hover:bg-gray-800"
                >
                  <div className="flex items-center gap-3 mb-2">
                    <span className="text-2xl">{system.icon}</span>
                    <span className="font-bold text-white">{system.name}</span>
                  </div>
                  <p className="text-xs text-gray-500">{system.description}</p>
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
                  Drag & drop URLs to add portals • Click to open • Mine for opportunities on any portal
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
              <div className="text-3xl font-black mb-1">{portals.filter(p => p.category === 'GOVERNMENT' || p.category === 'Government').length}</div>
              <div className="text-xs text-blue-100 font-semibold uppercase tracking-wide">Government Portals</div>
            </div>
            <div className="bg-gradient-to-br from-purple-600 to-purple-800 rounded-xl p-4">
              <div className="text-3xl mb-2">🏢</div>
              <div className="text-3xl font-black mb-1">{portals.filter(p => p.category === 'COMMERCIAL' || p.category === 'COOPERATIVE' || p.category === 'Development').length}</div>
              <div className="text-xs text-purple-100 font-semibold uppercase tracking-wide">Commercial / Prime</div>
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
                  onDrop={(e) => handleDrop(e, 'GOVERNMENT')}
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
                  .filter(p => p.category === 'GOVERNMENT' || p.category === 'Government')
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
                            <div className="flex gap-3">
                              <button
                                onClick={(e) => {
                                  e.stopPropagation();
                                  minePortal(portal.id);
                                }}
                                className="text-xs text-green-400 hover:text-green-300 font-semibold"
                              >
                                MINE
                              </button>
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
                    </div>
                  ))}
                
                {portals.filter(p => p.category === 'GOVERNMENT' || p.category === 'Government').length === 0 && (
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
                  <div className="text-3xl">🏢</div>
                  <div>
                    <h3 className="text-2xl font-black text-purple-400">COMMERCIAL & PRIME</h3>
                    <p className="text-xs text-gray-400">Prime contractor portals, cooperative contracts, commercial vendors</p>
                  </div>
                </div>
                
                {/* Drop Zone */}
                <div
                  onDragOver={handleDragOver}
                  onDragLeave={handleDragLeave}
                  onDrop={(e) => handleDrop(e, 'COMMERCIAL')}
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
                  .filter(p => p.category === 'COMMERCIAL' || p.category === 'COOPERATIVE' || p.category === 'Development')
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
                            <div className="flex gap-3">
                              <button
                                onClick={(e) => {
                                  e.stopPropagation();
                                  minePortal(portal.id);
                                }}
                                className="text-xs text-green-400 hover:text-green-300 font-semibold"
                              >
                                MINE
                              </button>
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
                    </div>
                  ))}
                
                {portals.filter(p => p.category === 'COMMERCIAL' || p.category === 'COOPERATIVE' || p.category === 'Development').length === 0 && (
                  <div className="text-center py-12 bg-gray-800/30 border border-gray-700 rounded-xl">
                    <div className="text-6xl mb-3 opacity-20">🏢</div>
                    <p className="text-gray-500 font-semibold">No commercial/prime portals yet</p>
                    <p className="text-xs text-gray-600 mt-1">Drag & drop contractor portal URLs above</p>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* AUTOMATED OPPORTUNITY MINING - LIVE */}
          <div className="bg-gradient-to-br from-green-900/20 to-emerald-900/20 border-2 border-green-500/30 rounded-xl p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-4">
                <div className="text-5xl">⛏️</div>
                <div>
                  <h3 className="text-xl font-black text-green-400 mb-1">AUTOMATED OPPORTUNITY MINING</h3>
                  <p className="text-gray-400 text-sm">
                    AI-powered scraping of {miningStatus?.minable_portals || portals.filter(p => p.url).length} vendor portals
                    {miningStatus?.last_mine?.timestamp && (
                      <span className="text-gray-500 ml-2">
                        | Last run: {new Date(miningStatus.last_mine.timestamp).toLocaleDateString()} at {new Date(miningStatus.last_mine.timestamp).toLocaleTimeString()}
                      </span>
                    )}
                  </p>
                </div>
              </div>
              <button
                onClick={runMiningNow}
                disabled={isMining}
                className={`px-6 py-3 rounded-lg font-bold text-sm transition-all ${
                  isMining
                    ? 'bg-gray-700 text-gray-400 cursor-wait animate-pulse'
                    : 'bg-green-600 hover:bg-green-500 text-white hover:shadow-lg hover:shadow-green-500/20'
                }`}
              >
                {isMining ? 'MINING...' : 'MINE NOW'}
              </button>
            </div>
            
            {/* Mining Stats */}
            <div className="grid grid-cols-4 gap-3 mb-4">
              <div className="bg-gray-800/60 rounded-lg p-3 text-center">
                <div className="text-2xl font-black text-green-400">{miningStatus?.total_portals || portals.length}</div>
                <div className="text-xs text-gray-500 font-semibold uppercase">Total Portals</div>
              </div>
              <div className="bg-gray-800/60 rounded-lg p-3 text-center">
                <div className="text-2xl font-black text-blue-400">{miningStatus?.minable_portals || portals.filter(p => p.url).length}</div>
                <div className="text-xs text-gray-500 font-semibold uppercase">Active URLs</div>
              </div>
              <div className="bg-gray-800/60 rounded-lg p-3 text-center">
                <div className="text-2xl font-black text-yellow-400">{miningStatus?.last_mine?.portals_checked || 0}</div>
                <div className="text-xs text-gray-500 font-semibold uppercase">Last Checked</div>
              </div>
              <div className="bg-gray-800/60 rounded-lg p-3 text-center">
                <div className="text-2xl font-black text-purple-400">{miningStatus?.last_mine?.total_opportunities_found || 0}</div>
                <div className="text-xs text-gray-500 font-semibold uppercase">Opps Found</div>
              </div>
            </div>

            {/* Mining Result (after clicking Mine Now) */}
            {miningResult && (
              <div className={`rounded-lg p-4 border ${
                miningResult.error 
                  ? 'bg-red-900/20 border-red-500/30' 
                  : 'bg-green-900/20 border-green-500/30'
              }`}>
                {miningResult.error ? (
                  <p className="text-red-400 text-sm font-semibold">{miningResult.error}</p>
                ) : (
                  <div>
                    <p className="text-green-400 text-sm font-bold mb-2">
                      Mining complete — {miningResult.portals_checked} portals scanned, {miningResult.total_opportunities_found} opportunities found
                    </p>
                    {miningResult.errors?.length > 0 && (
                      <p className="text-yellow-400 text-xs">
                        {miningResult.errors.length} portal(s) had issues (check logs)
                      </p>
                    )}
                  </div>
                )}
              </div>
            )}

            {/* Schedule Info */}
            <div className="flex gap-3 text-xs mt-3">
              <span className="bg-green-500/20 text-green-400 px-3 py-1 rounded-full font-semibold">Runs Every 4 Hours</span>
              <span className="bg-blue-500/20 text-blue-400 px-3 py-1 rounded-full font-semibold">AI Qualification</span>
              <span className="bg-purple-500/20 text-purple-400 px-3 py-1 rounded-full font-semibold">SAM.gov + Web Scraping</span>
            </div>
          </div>
        </div>
      )}
      </div>
    </main>

    {/* Review Opportunity Modal */}
    {reviewingOpportunity && (
      <ReviewOpportunityModal
        opportunity={reviewingOpportunity}
        onClose={() => setReviewingOpportunity(null)}
        onSuccess={handleReviewSuccess}
      />
    )}

    {/* Supplier Search Modal */}
    {searchingSuppliersFor && (
      <SupplierSearchModal
        opportunity={searchingSuppliersFor}
        onClose={() => setSearchingSuppliersFor(null)}
        onSuccess={handleReviewSuccess}
      />
    )}
  </>
  );
};

export default LandingPage;

