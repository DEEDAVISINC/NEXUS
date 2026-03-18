import React, { useState, useEffect } from 'react';
import { api } from '../../api/client';

interface GBISSystemProps {
  onBackToNexus: () => void;
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

interface GrantOpportunity {
  id: string;
  grantName: string;
  funderOrganization: string;
  funderType: string;
  grantAmount: number;
  grantAmountDisplay?: string | number;
  grantUrl: string;
  deadline: string;
  eligibility: string;
  focusAreas: string[];
  divisionFit: string[];
  qualificationScore: number;
  eligibilityMatch: number;
  winProbability: number;
  strategicValue: number;
  priorityLevel: string;
  applicationComplexity: string;
  estimatedTime: number;
  status: string;
  assignedTo: string;
  tags: string[];
  roiRating: number;
  daysUntilDeadline: number;
  discoveryDate: string;
}

interface GrantApplication {
  id: string;
  grantOpportunityId: string;
  applicationTitle: string;
  applicationStatus: string;
  assignedTo: string;
  applicationDraft: string;
  wordCount: number;
  sectionsCompleted: string[];
  aiGenerationUsed: boolean;
  divisionFocus: string;
  grantAmountRequested: number;
  submissionDeadline: string;
  actualSubmissionDate?: string;
  timeInvested: number;
  qualityScore: string;
  daysUntilDeadline: number;
}

interface PipelineItem {
  id: string;
  grantOpportunityId: string;
  currentStage: string;
  priority: string;
  nextAction: string;
  actionDueDate: string;
  assignedTo: string;
  blockers: string;
  daysInStage: number;
}

const GBISSystem: React.FC<GBISSystemProps> = ({ onBackToNexus, activeTab, setActiveTab }) => {
  const [opportunities, setOpportunities] = useState<GrantOpportunity[]>([]);
  const [applications, setApplications] = useState<GrantApplication[]>([]);
  const [pipeline, setPipeline] = useState<PipelineItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [notification, setNotification] = useState<{message: string, type: 'success' | 'error'} | null>(null);

  // Filters
  const [filters, setFilters] = useState({
    priorityLevel: 'all',
    funderType: 'all',
    division: 'all',
    status: 'all'
  });

  // Modal states
  const [showOpportunityModal, setShowOpportunityModal] = useState(false);
  const [selectedOpportunity, setSelectedOpportunity] = useState<GrantOpportunity | null>(null);
  const [showApplicationModal, setShowApplicationModal] = useState(false);
  const [selectedApplication, setSelectedApplication] = useState<GrantApplication | null>(null);
  const [generatingApplication, setGeneratingApplication] = useState(false);

  // Stats
  const [stats, setStats] = useState({
    activeOpportunities: 0,
    totalApplications: 0,
    totalAwarded: 0,
    successRate: 0,
    totalRevenue: 0,
    avgTimeInvested: 0
  });

  const [dailyDigest, setDailyDigest] = useState<{
    date?: string;
    actions?: Array<{ priority: string; source: string; action: string; url: string; fee?: string; time?: string }>;
  } | null>(null);

  const [storyLibrary, setStoryLibrary] = useState<any[]>([]);
  const [storyLoading, setStoryLoading] = useState(false);

  const loadStoryLibrary = async () => {
    setStoryLoading(true);
    try {
      const res = await api.getGbisStoryLibrary();
      const modules = Array.isArray(res) ? res : (res?.modules || res?.stories || res?.story_library || []);
      setStoryLibrary(modules);
    } catch { setStoryLibrary([]); }
    setStoryLoading(false);
  };

  useEffect(() => {
    if (activeTab === 'opportunities') {
      fetchOpportunities();
    } else if (activeTab === 'applications') {
      fetchApplications();
    } else if (activeTab === 'pipeline') {
      fetchPipeline();
    } else if (activeTab === 'dashboard' || activeTab === 'mining') {
      fetchStats();
    } else if (activeTab === 'story-library') {
      loadStoryLibrary();
    }
  }, [activeTab, filters]);

  useEffect(() => {
    if (activeTab === 'mining') {
      api.gbisSmallGrantsDailyDigest()
        .then((res: any) => {
          if (res?.actions) setDailyDigest({ date: res.date, actions: res.actions });
          else setDailyDigest(null);
        })
        .catch(() => setDailyDigest(null));
    } else {
      setDailyDigest(null);
    }
  }, [activeTab]);

  const fetchOpportunities = async () => {
    setLoading(true);
    try {
      const data = await api.getGbisOpportunities(filters);
      setOpportunities(data);
    } catch (error) {
      console.error('Error fetching opportunities:', error);
      showNotification('Failed to load grant opportunities', 'error');
    } finally {
      setLoading(false);
    }
  };

  const fetchApplications = async () => {
    setLoading(true);
    try {
      const data = await api.getGbisApplications();
      setApplications(data);
    } catch (error) {
      console.error('Error fetching applications:', error);
      showNotification('Failed to load applications', 'error');
    } finally {
      setLoading(false);
    }
  };

  const fetchPipeline = async () => {
    setLoading(true);
    try {
      const data = await api.getGbisPipeline();
      setPipeline(data);
    } catch (error) {
      console.error('Error fetching pipeline:', error);
      showNotification('Failed to load pipeline', 'error');
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    setLoading(true);
    try {
      const data = await api.getGbisStats();
      setStats(data);
    } catch (error) {
      console.error('Error fetching stats:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateApplication = async (opportunityId: string) => {
    setGeneratingApplication(true);
    try {
      const result = await api.generateGrantApplication(opportunityId);
      showNotification('Application draft generated successfully!', 'success');
      fetchApplications();
      setShowOpportunityModal(false);
    } catch (error) {
      console.error('Error generating application:', error);
      showNotification('Failed to generate application', 'error');
    } finally {
      setGeneratingApplication(false);
    }
  };

  const showNotification = (message: string, type: 'success' | 'error') => {
    setNotification({ message, type });
    setTimeout(() => setNotification(null), 3000);
  };

  const formatGrantAmount = (opportunity: GrantOpportunity): string => {
    const displayValue = opportunity.grantAmountDisplay;
    if (typeof displayValue === 'string' && displayValue.trim()) {
      return displayValue.trim();
    }

    if (Number.isFinite(opportunity.grantAmount)) {
      return `$${Math.round(opportunity.grantAmount).toLocaleString()}`;
    }

    return 'Amount not listed';
  };

  const formatDate = (rawDate: string): string => {
    if (!rawDate) return 'No deadline listed';
    const parsed = new Date(rawDate);
    return Number.isNaN(parsed.getTime()) ? rawDate : parsed.toLocaleDateString();
  };

  const renderDashboard = () => (
    <div className="space-y-6">
      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Active Opportunities</p>
              <p className="text-3xl font-bold text-white mt-2">{stats.activeOpportunities}</p>
            </div>
            <div className="text-4xl">🎯</div>
          </div>
        </div>

        <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Total Applications</p>
              <p className="text-3xl font-bold text-white mt-2">{stats.totalApplications}</p>
            </div>
            <div className="text-4xl">📝</div>
          </div>
        </div>

        <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Grants Awarded</p>
              <p className="text-3xl font-bold text-green-400 mt-2">{stats.totalAwarded}</p>
            </div>
            <div className="text-4xl">🏆</div>
          </div>
        </div>

        <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Success Rate</p>
              <p className="text-3xl font-bold text-blue-400 mt-2">{stats.successRate}%</p>
            </div>
            <div className="text-4xl">📊</div>
          </div>
        </div>

        <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Total Grant Revenue</p>
              <p className="text-3xl font-bold text-green-400 mt-2">${stats.totalRevenue.toLocaleString()}</p>
            </div>
            <div className="text-4xl">💰</div>
          </div>
        </div>

        <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Avg Time per Grant</p>
              <p className="text-3xl font-bold text-purple-400 mt-2">{stats.avgTimeInvested}h</p>
            </div>
            <div className="text-4xl">⏱️</div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
        <h3 className="text-xl font-bold mb-4">Quick Actions</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button
            onClick={() => setActiveTab('opportunities')}
            className="p-4 bg-blue-500/20 hover:bg-blue-500/30 rounded-lg border border-blue-500/50 text-left transition"
          >
            <div className="text-2xl mb-2">🔍</div>
            <div className="font-semibold">View Opportunities</div>
            <div className="text-sm text-gray-400">Browse discovered grants</div>
          </button>

          <button
            onClick={() => setActiveTab('applications')}
            className="p-4 bg-green-500/20 hover:bg-green-500/30 rounded-lg border border-green-500/50 text-left transition"
          >
            <div className="text-2xl mb-2">✍️</div>
            <div className="font-semibold">Manage Applications</div>
            <div className="text-sm text-gray-400">Track applications in progress</div>
          </button>

          <button
            onClick={() => setActiveTab('pipeline')}
            className="p-4 bg-purple-500/20 hover:bg-purple-500/30 rounded-lg border border-purple-500/50 text-left transition"
          >
            <div className="text-2xl mb-2">📊</div>
            <div className="font-semibold">View Pipeline</div>
            <div className="text-sm text-gray-400">Kanban board view</div>
          </button>
        </div>
      </div>
    </div>
  );

  const renderOpportunities = () => (
    <div className="space-y-6">
      {/* Filters */}
      <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
        <h3 className="text-lg font-bold mb-4">Filters</h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm text-gray-400 mb-2">Priority Level</label>
            <select
              value={filters.priorityLevel}
              onChange={(e) => setFilters({...filters, priorityLevel: e.target.value})}
              className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2"
            >
              <option value="all">All Priorities</option>
              <option value="Critical (90-100)">Critical (90-100)</option>
              <option value="High (80-89)">High (80-89)</option>
              <option value="Medium (70-79)">Medium (70-79)</option>
              <option value="Low (60-69)">Low (60-69)</option>
            </select>
          </div>

          <div>
            <label className="block text-sm text-gray-400 mb-2">Funder Type</label>
            <select
              value={filters.funderType}
              onChange={(e) => setFilters({...filters, funderType: e.target.value})}
              className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2"
            >
              <option value="all">All Funders</option>
              <option value="Foundation">Foundation</option>
              <option value="Corporate">Corporate</option>
              <option value="State Government">State Government</option>
              <option value="Federal Government">Federal Government</option>
            </select>
          </div>

          <div>
            <label className="block text-sm text-gray-400 mb-2">Status</label>
            <select
              value={filters.status}
              onChange={(e) => setFilters({...filters, status: e.target.value})}
              className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2"
            >
              <option value="all">All Status</option>
              <option value="New Discovery">New Discovery</option>
              <option value="Qualified">Qualified</option>
              <option value="Drafting Application">Drafting Application</option>
              <option value="Submitted">Submitted</option>
            </select>
          </div>

          <div className="flex items-end">
            <button
              onClick={fetchOpportunities}
              className="w-full bg-blue-500 hover:bg-blue-600 px-4 py-2 rounded-lg font-semibold transition"
            >
              Apply Filters
            </button>
          </div>
        </div>
      </div>

      {/* Opportunities Table */}
      <div className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-700">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Grant Name</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Funder</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Amount</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Deadline</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Score</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Priority</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-700">
              {loading ? (
                <tr>
                  <td colSpan={8} className="px-6 py-4 text-center text-gray-400">
                    Loading opportunities...
                  </td>
                </tr>
              ) : opportunities.length === 0 ? (
                <tr>
                  <td colSpan={8} className="px-6 py-4 text-center text-gray-400">
                    No grant opportunities found. Connect to grant sources in Airtable.
                  </td>
                </tr>
              ) : (
                opportunities.map((opp) => (
                  <tr key={opp.id} className="hover:bg-gray-700/50">
                    <td className="px-6 py-4">
                      <div className="font-medium text-white">{opp.grantName}</div>
                      <div className="text-sm text-gray-400">{opp.applicationComplexity}</div>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-300">{opp.funderOrganization}</td>
                    <td className="px-6 py-4 text-sm font-semibold text-green-400">
                      {formatGrantAmount(opp)}
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-sm text-gray-300">{formatDate(opp.deadline)}</div>
                      <div className={`text-xs ${opp.daysUntilDeadline > 0 && opp.daysUntilDeadline <= 7 ? 'text-red-400' : 'text-gray-400'}`}>
                        {opp.daysUntilDeadline} days left
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2">
                        <div className="text-2xl font-bold text-yellow-400">{opp.qualificationScore}</div>
                        <div className="text-xs text-gray-400">/100</div>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                        opp.priorityLevel.startsWith('Critical') ? 'bg-red-500/20 text-red-400 border border-red-500/50' :
                        opp.priorityLevel.startsWith('High') ? 'bg-orange-500/20 text-orange-400 border border-orange-500/50' :
                        opp.priorityLevel.startsWith('Medium') ? 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/50' :
                        'bg-gray-500/20 text-gray-400 border border-gray-500/50'
                      }`}>
                        {opp.priorityLevel}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <select
                        value={opp.status}
                        onChange={async (e) => {
                          const newStatus = e.target.value;
                          try {
                            await api.put(`/gbis/opportunities/${opp.id}`, { status: newStatus });
                            showNotification(`Grant status updated to ${newStatus}`, 'success');
                            fetchOpportunities();
                          } catch (err) {
                            showNotification('Failed to update status', 'error');
                          }
                        }}
                        className="bg-gray-700 border border-gray-600 rounded-lg px-2 py-1 text-sm text-white"
                      >
                        <option value="New Discovery">New Discovery</option>
                        <option value="Qualified">Qualified</option>
                        <option value="Drafting Application">Drafting</option>
                        <option value="Submitted">Submitted</option>
                        <option value="Under Review">Under Review</option>
                        <option value="Awarded">Awarded</option>
                        <option value="Rejected">Rejected</option>
                        <option value="Expired">Expired</option>
                      </select>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex gap-2">
                        <button
                          onClick={() => {
                            setSelectedOpportunity(opp);
                            setShowOpportunityModal(true);
                          }}
                          className="px-3 py-1 bg-blue-500/20 hover:bg-blue-500/30 text-blue-400 rounded-lg text-sm transition"
                        >
                          View
                        </button>
                        {opp.qualificationScore >= 80 && (
                          <button
                            onClick={() => handleGenerateApplication(opp.id)}
                            disabled={generatingApplication}
                            className="px-3 py-1 bg-green-500/20 hover:bg-green-500/30 text-green-400 rounded-lg text-sm transition disabled:opacity-50"
                          >
                            Generate App
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );

  const renderApplications = () => (
    <div className="space-y-6">
      <div className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
        <div className="p-6 border-b border-gray-700">
          <h3 className="text-xl font-bold">Grant Applications</h3>
          <p className="text-gray-400 text-sm mt-1">Track and manage your grant applications</p>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-700">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Application Title</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Amount</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Deadline</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Time Invested</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Progress</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-700">
              {loading ? (
                <tr>
                  <td colSpan={7} className="px-6 py-4 text-center text-gray-400">
                    Loading applications...
                  </td>
                </tr>
              ) : applications.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-6 py-4 text-center text-gray-400">
                    No applications yet. Generate applications from high-scoring opportunities.
                  </td>
                </tr>
              ) : (
                applications.map((app) => (
                  <tr key={app.id} className="hover:bg-gray-700/50">
                    <td className="px-6 py-4">
                      <div className="font-medium text-white">{app.applicationTitle}</div>
                      <div className="text-sm text-gray-400">{app.divisionFocus}</div>
                    </td>
                    <td className="px-6 py-4 text-sm font-semibold text-green-400">
                      ${app.grantAmountRequested.toLocaleString()}
                    </td>
                    <td className="px-6 py-4">
                      <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                        app.applicationStatus === 'Awarded' ? 'bg-green-500/20 text-green-400' :
                        app.applicationStatus === 'Submitted' ? 'bg-blue-500/20 text-blue-400' :
                        app.applicationStatus === 'Rejected' ? 'bg-red-500/20 text-red-400' :
                        'bg-gray-500/20 text-gray-400'
                      }`}>
                        {app.applicationStatus}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-sm text-gray-300">{formatDate(app.submissionDeadline)}</div>
                      <div className={`text-xs ${app.daysUntilDeadline > 0 && app.daysUntilDeadline <= 7 ? 'text-red-400' : 'text-gray-400'}`}>
                        {app.daysUntilDeadline} days left
                      </div>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-300">{app.timeInvested}h</td>
                    <td className="px-6 py-4">
                      <div className="w-full bg-gray-700 rounded-full h-2">
                        <div 
                          className="bg-blue-500 h-2 rounded-full" 
                          style={{width: `${(app.sectionsCompleted.length / 8) * 100}%`}}
                        ></div>
                      </div>
                      <div className="text-xs text-gray-400 mt-1">{app.sectionsCompleted.length}/8 sections</div>
                    </td>
                    <td className="px-6 py-4">
                      <button
                        onClick={() => {
                          setSelectedApplication(app);
                          setShowApplicationModal(true);
                        }}
                        className="px-3 py-1 bg-blue-500/20 hover:bg-blue-500/30 text-blue-400 rounded-lg text-sm transition"
                      >
                        View/Edit
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );

  const PIPELINE_STAGES = [
    { key: 'Discovery', label: 'Discovery', color: 'blue' },
    { key: 'Application Development', label: 'Development', color: 'yellow' },
    { key: 'Submitted', label: 'Submitted', color: 'purple' },
    { key: 'Decision Pending', label: 'Pending', color: 'orange' },
    { key: 'Won', label: 'Won', color: 'green' },
    { key: 'Lost', label: 'Lost', color: 'red' },
  ];

  const renderPipeline = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-xl font-bold">Grant Pipeline</h3>
        <span className="text-sm text-gray-400">{pipeline.length} grants in pipeline</span>
      </div>
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        {PIPELINE_STAGES.map(stage => {
          const items = pipeline.filter(p => p.currentStage === stage.key);
          return (
            <div key={stage.key} className="bg-gray-800 rounded-xl border border-gray-700 flex flex-col">
              <div className={`px-4 py-3 border-b border-gray-700 flex items-center justify-between`}>
                <span className={`font-semibold text-sm text-${stage.color}-400`}>{stage.label}</span>
                <span className={`w-6 h-6 rounded-full bg-${stage.color}-500/20 text-${stage.color}-400 flex items-center justify-center text-xs font-bold`}>
                  {items.length}
                </span>
              </div>
              <div className="p-2 space-y-2 flex-1 min-h-[200px]">
                {items.length === 0 ? (
                  <div className="text-center py-8 text-gray-600 text-xs">No grants</div>
                ) : (
                  items.map(item => (
                    <div key={item.id} className="bg-gray-700/50 rounded-lg p-3 border border-gray-600 hover:border-gray-500 transition cursor-pointer">
                      <div className="text-sm font-medium truncate">{item.grantOpportunityId}</div>
                      <div className="text-xs text-gray-400 mt-1">{item.assignedTo || 'Unassigned'}</div>
                      {item.priority && (
                        <span className={`mt-2 inline-block px-2 py-0.5 rounded text-xs font-medium ${
                          item.priority === 'High' || item.priority === 'Critical' ? 'bg-red-500/20 text-red-400' :
                          item.priority === 'Medium' ? 'bg-yellow-500/20 text-yellow-400' :
                          'bg-gray-500/20 text-gray-400'
                        }`}>{item.priority}</span>
                      )}
                      {item.nextAction && <div className="text-xs text-gray-500 mt-1 truncate">Next: {item.nextAction}</div>}
                    </div>
                  ))
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );

  // ── Mining state ──────────────────────────────────────────────────────────
  interface MiningResult {
    success: boolean;
    message: string;
    total_new?: number;
    imported?: number;
    breakdown?: {
      michigan_foundations: { imported: number; skipped: number; label: string };
      veteran_grants:       { imported: number; skipped: number; label: string };
      grants_gov:           { imported: number; found: number;   label: string };
    };
    last_run?: string;
    error?: string;
  }

  const [miningLoading, setMiningLoading] = useState<string | null>(null);
  const [miningResult, setMiningResult]   = useState<MiningResult | null>(null);

  const runMining = async (
    label: string,
    action: () => Promise<any>
  ) => {
    setMiningLoading(label);
    setMiningResult(null);
    try {
      const res = await action();
      const data = res?.data ?? res;
      setMiningResult(data);
      if (data?.total_new || data?.imported) {
        showNotification(data.message || `${label} complete`, 'success');
        fetchOpportunities();
        fetchStats();
      } else if (data?.error) {
        showNotification(`${label} failed: ${data.error}`, 'error');
      } else {
        showNotification(data?.message || `${label} complete`, 'success');
      }
    } catch (err: any) {
      const msg = err?.response?.data?.error || err?.message || 'Unknown error';
      setMiningResult({ success: false, message: msg, error: msg });
      showNotification(`${label} failed: ${msg}`, 'error');
    } finally {
      setMiningLoading(null);
    }
  };

  const MINING_SOURCES = [
    {
      id: 'all',
      label: 'Run Full Pipeline',
      description: 'ALL sources in one click — Small business grants + Michigan foundations + Veteran grants + Grants.gov live federal mining.',
      action: () => api.gbisRunAll(),
      color: 'green',
      priority: 'Full Discovery',
    },
    {
      id: 'small_business_free',
      label: 'FREE Small Business Grants Only',
      description: '45 free sources: Hello Alice, IFundWomen, Comcast RISE, FedEx, Google, Bank of America, Chase, Nav, SBA, SCORE, Michigan SBDC, MEDC, DEGC, WBENC portal, LinkedIn monitoring, NAWBO, Cartier, Eileen Fisher, Oakland County, and more.',
      action: () => api.gbisSeedSmallGrantsFreeOnly(),
      color: 'cyan',
      priority: 'FREE — No Fees',
    },
    {
      id: 'small_business',
      label: 'All Small Business Grants (incl. paid)',
      description: '46 sources including the Amber Grant ($15/mo fee). Everything above + Amber Grant — $10K monthly, $25K annual. Apply every month.',
      action: () => api.gbisSeedSmallGrants(),
      color: 'orange',
      priority: 'All Sources (46)',
    },
    {
      id: 'michigan_foundations',
      label: 'Michigan Foundation Grants',
      description: 'Seeds 6 Michigan foundation sources: MHEF, Kresge, Kellogg, RWJF, CFSEM, Ralph C. Wilson Jr. (Cause We Care applicant)',
      action: () => api.gbisSeedMichiganFoundations(),
      color: 'blue',
      priority: 'Community Health',
    },
    {
      id: 'veteran_grants',
      label: 'Veteran Grant Sources',
      description: 'Seeds 7 veteran sources: DAV (apply first), DOL HVRP, VFW Foundation, Bob Woodruff, Gary Sinise, JPMorgan. Unlocked by Gary Felton Jr.',
      action: () => api.gbisSeedVeteranSources(),
      color: 'yellow',
      priority: 'Veteran Focused',
    },
    {
      id: 'grants_gov',
      label: 'Mine Grants.gov (Federal Live)',
      description: 'Live API search — NIH NIMHD, HRSA, SAMHSA, USDA FNS, HUD, ACF, HHS ASPE. Returns open + forecasted grants right now.',
      action: () => api.gbisMineFederal(),
      color: 'purple',
      priority: 'Federal Live',
    },
  ];

  const renderMining = () => (
    <div className="space-y-6">
      {/* Today's Grant Actions — Daily Digest */}
      {dailyDigest?.actions && dailyDigest.actions.length > 0 && (
        <div className="bg-amber-900/20 border border-amber-500/40 rounded-lg p-5">
          <h4 className="font-bold text-amber-400 mb-3 flex items-center gap-2">
            <span>📋</span> Today&apos;s Grant Actions
            {dailyDigest.date && (
              <span className="text-xs font-normal text-gray-400">({dailyDigest.date})</span>
            )}
          </h4>
          <div className="space-y-3">
            {dailyDigest.actions.map((a, i) => (
              <div key={i} className="bg-gray-800/60 rounded-lg p-3 border border-gray-700">
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <span className="text-xs font-semibold px-2 py-0.5 rounded bg-amber-500/20 text-amber-400">
                      {a.priority}
                    </span>
                    <p className="font-semibold text-gray-200 mt-1">{a.source}</p>
                    <p className="text-gray-400 text-sm mt-0.5">{a.action}</p>
                    {a.time && (
                      <p className="text-xs text-gray-500 mt-1">⏱ {a.time}</p>
                    )}
                  </div>
                  <div className="flex flex-col items-end gap-1 shrink-0">
                    <span className={`text-xs px-2 py-0.5 rounded ${a.fee ? 'bg-red-500/20 text-red-400' : 'bg-green-500/20 text-green-400'}`}>
                      {a.fee || 'FREE'}
                    </span>
                    <a
                      href={a.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-xs text-amber-400 hover:text-amber-300 underline"
                    >
                      Open →
                    </a>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Header */}
      <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
        <div className="flex items-start justify-between">
          <div>
            <h3 className="text-xl font-bold">Grant Discovery Engine</h3>
            <p className="text-gray-400 text-sm mt-1">
              53 grant sources (51 free) — small business, Michigan foundations, veteran, fellowship/builder + live Grants.gov.
              All sources skip duplicates — safe to run anytime.
            </p>
          </div>
          <button
            onClick={() => runMining('Full Pipeline', () => api.gbisRunAll())}
            disabled={miningLoading !== null}
            className="px-6 py-3 bg-green-500 hover:bg-green-600 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg font-bold text-sm transition whitespace-nowrap"
          >
            {miningLoading === 'Full Pipeline' ? (
              <span className="flex items-center gap-2">
                <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.4 0 0 5.4 0 12h4z"/>
                </svg>
                Mining…
              </span>
            ) : '⚡ Run Full Pipeline'}
          </button>
        </div>
      </div>

      {/* Source cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {MINING_SOURCES.map((source) => (
          <div key={source.id} className={`bg-gray-800 rounded-lg border border-gray-700 p-5 hover:border-${source.color}-500/50 transition`}>
            <div className="flex items-start justify-between mb-3">
              <div>
                <span className={`text-xs font-semibold px-2 py-0.5 rounded-full bg-${source.color}-500/20 text-${source.color}-400 border border-${source.color}-500/30`}>
                  {source.priority}
                </span>
                <h4 className="font-bold mt-2">{source.label}</h4>
                <p className="text-gray-400 text-sm mt-1 leading-relaxed">{source.description}</p>
              </div>
            </div>
            <button
              onClick={() => runMining(source.label, source.action)}
              disabled={miningLoading !== null}
              className={`w-full mt-2 py-2 rounded-lg text-sm font-semibold transition
                bg-${source.color}-500/20 hover:bg-${source.color}-500/30 text-${source.color}-400
                border border-${source.color}-500/40 disabled:opacity-40 disabled:cursor-not-allowed`}
            >
              {miningLoading === source.label ? (
                <span className="flex items-center justify-center gap-2">
                  <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.4 0 0 5.4 0 12h4z"/>
                  </svg>
                  Running…
                </span>
              ) : `Mine — ${source.label}`}
            </button>
          </div>
        ))}
      </div>

      {/* Result card */}
      {miningResult && (
        <div className={`rounded-lg border p-6 ${miningResult.success === false ? 'bg-red-900/20 border-red-500/40' : 'bg-green-900/20 border-green-500/40'}`}>
          <div className="flex items-center gap-3 mb-4">
            <span className="text-2xl">{miningResult.success === false ? '❌' : '✅'}</span>
            <div>
              <p className="font-bold text-lg">{miningResult.message}</p>
              {miningResult.last_run && (
                <p className="text-xs text-gray-400">Run at: {new Date(miningResult.last_run).toLocaleTimeString()}</p>
              )}
            </div>
          </div>

          {miningResult.breakdown && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mt-2">
              {Object.entries(miningResult.breakdown).map(([key, info]) => (
                <div key={key} className="bg-gray-800 rounded-lg p-4 border border-gray-700">
                  <p className="text-xs text-gray-400 mb-1">{info.label}</p>
                  <p className="text-2xl font-bold text-green-400">+{info.imported}</p>
                  <p className="text-xs text-gray-500">
                    {'found' in info ? `${info.found} found on Grants.gov` : `${info.skipped} already tracked`}
                  </p>
                </div>
              ))}
            </div>
          )}

          {miningResult.imported !== undefined && !miningResult.breakdown && (
            <p className="text-gray-300">
              <span className="text-green-400 font-bold text-xl">+{miningResult.imported}</span> new records added to GRANT OPPORTUNITIES
            </p>
          )}

          {miningResult.error && (
            <p className="text-red-400 text-sm mt-2 font-mono">{miningResult.error}</p>
          )}

          {miningResult.success !== false && (miningResult.total_new ?? miningResult.imported ?? 0) === 0 && (
            <p className="text-gray-400 text-sm mt-2">All sources already tracked — no duplicates added. Pipeline is up to date.</p>
          )}
        </div>
      )}

      {/* Quick reference */}
      <div className="bg-gray-800 rounded-lg border border-gray-700 p-5">
        <h4 className="font-semibold mb-3 text-gray-300">Grant Sources Covered</h4>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-sm">
          <div>
            <p className="text-orange-400 font-semibold mb-2">Small Business (DDI) — Apply Monthly</p>
            <ul className="text-gray-400 space-y-1">
              <li>• Hello Alice (daily check)</li>
              <li>• Amber Grant ($10K, 1st of month)</li>
              <li>• IFundWomen Universal (quarterly)</li>
              <li>• NASE Growth Grant (monthly)</li>
              <li>• Comcast RISE (rolling)</li>
              <li>• FedEx $50K (annual, Spring)</li>
              <li>• Nav Business Grants (weekly)</li>
              <li>• GrantWatch (daily digest)</li>
              <li>• SBA Grants (weekly)</li>
              <li>• Michigan SBDC (weekly)</li>
              <li>• Cartier $100K (annual, Q1)</li>
              <li>• InnovateHER/SBA (annual, Fall)</li>
              <li className="text-orange-300 font-medium mt-2">Fellowship / Builder</li>
              <li>• O&apos;Shaughnessy ($100K — Apr 30)</li>
              <li>• Soma Scholars ($30K — rolling)</li>
              <li>• Women Who Tech ($3–15K — rolling)</li>
              <li>• AT&T She&apos;s Connected ($50K — Spring)</li>
              <li>• Proposium (AI matching)</li>
              <li>• Merge Grant ($100–$1K — fast)</li>
            </ul>
          </div>
          <div>
            <p className="text-blue-400 font-semibold mb-2">Michigan Foundations</p>
            <ul className="text-gray-400 space-y-1">
              <li>• CFSEM (Quarterly — Q2 PRIORITY)</li>
              <li>• Michigan Health Endowment Fund</li>
              <li>• Kresge Foundation (Detroit HQ)</li>
              <li>• W.K. Kellogg Foundation</li>
              <li>• Robert Wood Johnson Foundation</li>
              <li>• Ralph C. Wilson Jr. Foundation</li>
            </ul>
          </div>
          <div>
            <p className="text-yellow-400 font-semibold mb-2">Veteran Grants</p>
            <ul className="text-gray-400 space-y-1">
              <li>• DAV Charitable Trust (APPLY FIRST)</li>
              <li>• DOL VETS — HVRP (federal)</li>
              <li>• VFW Foundation</li>
              <li>• Bob Woodruff Foundation</li>
              <li>• Gary Sinise Foundation</li>
              <li>• JPMorgan Veteran Jobs Mission</li>
              <li>• HIRE Vets Medallion (DOL)</li>
            </ul>
          </div>
          <div>
            <p className="text-purple-400 font-semibold mb-2">Federal (Grants.gov Live)</p>
            <ul className="text-gray-400 space-y-1">
              <li>• NIH NIMHD (93.307)</li>
              <li>• HRSA Community Health (93.910)</li>
              <li>• SAMHSA Behavioral (93.243)</li>
              <li>• USDA FNS SNAP (10.561)</li>
              <li>• HUD CDBG (14.218)</li>
              <li>• ACF Family Support (93.647)</li>
              <li>• HHS ASPE Policy (93.239)</li>
            </ul>
          </div>
        </div>

        {/* Daily action cadence */}
        <div className="mt-5 pt-4 border-t border-gray-700">
          <p className="text-gray-300 font-semibold mb-3">Daily / Weekly Action Cadence</p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
            <div className="bg-gray-700/50 rounded-lg p-3">
              <p className="text-orange-400 font-semibold mb-1">Every Day</p>
              <p className="text-gray-400">Check Hello Alice for new grants</p>
            </div>
            <div className="bg-gray-700/50 rounded-lg p-3">
              <p className="text-orange-400 font-semibold mb-1">Every Monday</p>
              <p className="text-gray-400">Scan Nav Business Grants + Michigan SBDC</p>
            </div>
            <div className="bg-gray-700/50 rounded-lg p-3">
              <p className="text-red-400 font-semibold mb-1">1st of Every Month</p>
              <p className="text-gray-400">Apply: Amber Grant ($15 fee) + NASE Growth Grant</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderStoryLibrary = () => (
    <div className="space-y-6">
      <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-xl font-bold">Grant Story Library</h3>
            <p className="text-gray-400 text-sm">Modular content used for AI application generation</p>
          </div>
          <button onClick={loadStoryLibrary} className="bg-blue-500 hover:bg-blue-600 px-4 py-2 rounded-lg text-sm font-medium transition">
            {storyLoading ? 'Loading...' : 'Load Stories'}
          </button>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="bg-gray-700 p-4 rounded-lg border-l-4 border-blue-500">
            <h4 className="font-semibold mb-2">Company Core</h4>
            <p className="text-gray-400 text-sm">Business narrative, mission, owner bio</p>
          </div>
          <div className="bg-gray-700 p-4 rounded-lg border-l-4 border-green-500">
            <h4 className="font-semibold mb-2">Use of Funds</h4>
            <p className="text-gray-400 text-sm">Templates by award amount ($5K–$100K)</p>
          </div>
          <div className="bg-gray-700 p-4 rounded-lg border-l-4 border-purple-500">
            <h4 className="font-semibold mb-2">Impact & Proof</h4>
            <p className="text-gray-400 text-sm">Community impact, financial need, FAQ</p>
          </div>
        </div>

        {storyLibrary.length > 0 ? (
          <div className="space-y-3">
            {storyLibrary.map((story: any, i: number) => (
              <div key={story.id || i} className="bg-gray-700/50 rounded-lg p-4 border border-gray-600">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-semibold">{story.moduleName || story['Module Name'] || story.title || `Module ${i + 1}`}</span>
                  <span className="px-2 py-1 bg-blue-500/20 text-blue-400 rounded text-xs shrink-0 ml-2">
                    {story.moduleType || story['Module Type'] || story.status || story['Status'] || 'Active'}
                  </span>
                </div>
                <p className="text-sm text-gray-400 line-clamp-2">
                  {story.content || story['Content'] || story['Story Content'] || ''}
                </p>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500">
            {storyLoading ? (
              <p className="text-lg">Loading Story Library…</p>
            ) : (
              <>
                <p className="text-lg mb-1">No modules in Story Library</p>
                <p className="text-sm">Run <code className="bg-gray-700 px-1 rounded">gbis_populate_story_library.py</code> to sync from Grant Application Package.</p>
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Notification */}
      {notification && (
        <div className={`fixed top-20 right-6 z-50 px-6 py-4 rounded-lg shadow-lg ${
          notification.type === 'success' ? 'bg-green-500' : 'bg-red-500'
        }`}>
          {notification.message}
        </div>
      )}

      {/* Navigation Tabs */}
      <div className="bg-gray-800 border-b border-gray-700">
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex gap-1 overflow-x-auto">
            {[
              { id: 'dashboard',     label: '📊 Dashboard' },
              { id: 'mining',        label: '⚡ Mine Grants' },
              { id: 'opportunities', label: '🎯 Opportunities' },
              { id: 'applications',  label: '✍️ Applications' },
              { id: 'pipeline',      label: '📈 Pipeline' },
              { id: 'story-library', label: '📚 Story Library' },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-6 py-4 font-semibold whitespace-nowrap transition border-b-2 ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-400 bg-gray-700/50'
                    : 'border-transparent text-gray-400 hover:text-gray-300 hover:bg-gray-700/30'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Content Area */}
      <div className="max-w-7xl mx-auto px-6 py-8">
        {activeTab === 'dashboard'     && renderDashboard()}
        {activeTab === 'mining'         && renderMining()}
        {activeTab === 'opportunities'  && renderOpportunities()}
        {activeTab === 'applications'   && renderApplications()}
        {activeTab === 'pipeline'       && renderPipeline()}
        {activeTab === 'story-library'  && renderStoryLibrary()}
      </div>

      {/* Opportunity Modal */}
      {showOpportunityModal && selectedOpportunity && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-6">
          <div className="bg-gray-800 rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b border-gray-700 flex justify-between items-start">
              <div>
                <h3 className="text-2xl font-bold">{selectedOpportunity.grantName}</h3>
                <p className="text-gray-400">{selectedOpportunity.funderOrganization}</p>
              </div>
              <button
                onClick={() => setShowOpportunityModal(false)}
                className="text-gray-400 hover:text-white text-2xl"
              >
                ×
              </button>
            </div>
            
            <div className="p-6 space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-gray-400 text-sm">Grant Amount</label>
                  <p className="text-2xl font-bold text-green-400">{formatGrantAmount(selectedOpportunity)}</p>
                </div>
                <div>
                  <label className="text-gray-400 text-sm">Qualification Score</label>
                  <p className="text-2xl font-bold text-yellow-400">{selectedOpportunity.qualificationScore}/100</p>
                </div>
                <div>
                  <label className="text-gray-400 text-sm">Deadline</label>
                  <p className="text-lg">{formatDate(selectedOpportunity.deadline)}</p>
                  <p className="text-sm text-gray-400">{selectedOpportunity.daysUntilDeadline} days left</p>
                </div>
                <div>
                  <label className="text-gray-400 text-sm">Estimated Time</label>
                  <p className="text-lg">{selectedOpportunity.estimatedTime} hours</p>
                </div>
              </div>

              <div>
                <label className="text-gray-400 text-sm">Eligibility</label>
                <p className="text-white mt-1">{selectedOpportunity.eligibility}</p>
              </div>

              <div>
                <label className="text-gray-400 text-sm">Focus Areas</label>
                <div className="flex flex-wrap gap-2 mt-2">
                  {selectedOpportunity.focusAreas.map((area, idx) => (
                    <span key={idx} className="px-3 py-1 bg-blue-500/20 text-blue-400 rounded-full text-sm">
                      {area}
                    </span>
                  ))}
                </div>
              </div>

              <div>
                <label className="text-gray-400 text-sm">Division Fit</label>
                <div className="flex flex-wrap gap-2 mt-2">
                  {selectedOpportunity.divisionFit.map((div, idx) => (
                    <span key={idx} className="px-3 py-1 bg-purple-500/20 text-purple-400 rounded-full text-sm">
                      {div}
                    </span>
                  ))}
                </div>
              </div>

              <div className="pt-4">
                <a
                  href={selectedOpportunity.grantUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-block px-6 py-3 bg-blue-500 hover:bg-blue-600 rounded-lg font-semibold transition"
                >
                  View Grant Application Page →
                </a>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default GBISSystem;
