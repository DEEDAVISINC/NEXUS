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

  useEffect(() => {
    if (activeTab === 'opportunities') {
      fetchOpportunities();
    } else if (activeTab === 'applications') {
      fetchApplications();
    } else if (activeTab === 'pipeline') {
      fetchPipeline();
    } else if (activeTab === 'dashboard') {
      fetchStats();
    }
  }, [activeTab, filters]);

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
                      ${opp.grantAmount.toLocaleString()}
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-sm text-gray-300">{new Date(opp.deadline).toLocaleDateString()}</div>
                      <div className={`text-xs ${opp.daysUntilDeadline <= 7 ? 'text-red-400' : 'text-gray-400'}`}>
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
                    <td className="px-6 py-4 text-sm text-gray-300">{opp.status}</td>
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
                      <div className="text-sm text-gray-300">{new Date(app.submissionDeadline).toLocaleDateString()}</div>
                      <div className={`text-xs ${app.daysUntilDeadline <= 7 ? 'text-red-400' : 'text-gray-400'}`}>
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

  const renderPipeline = () => (
    <div className="space-y-6">
      <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
        <h3 className="text-xl font-bold mb-4">Grant Pipeline</h3>
        <p className="text-gray-400 mb-6">Kanban view coming soon - for now, view in Airtable</p>
        
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-gray-700 p-4 rounded-lg">
            <h4 className="font-semibold mb-2 text-blue-400">Discovery</h4>
            <div className="text-2xl font-bold">{pipeline.filter(p => p.currentStage === 'Discovery').length}</div>
          </div>

          <div className="bg-gray-700 p-4 rounded-lg">
            <h4 className="font-semibold mb-2 text-yellow-400">Application Development</h4>
            <div className="text-2xl font-bold">{pipeline.filter(p => p.currentStage === 'Application Development').length}</div>
          </div>

          <div className="bg-gray-700 p-4 rounded-lg">
            <h4 className="font-semibold mb-2 text-purple-400">Decision Pending</h4>
            <div className="text-2xl font-bold">{pipeline.filter(p => p.currentStage === 'Decision Pending').length}</div>
          </div>

          <div className="bg-gray-700 p-4 rounded-lg">
            <h4 className="font-semibold mb-2 text-green-400">Won</h4>
            <div className="text-2xl font-bold">{pipeline.filter(p => p.currentStage === 'Won').length}</div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderStoryLibrary = () => (
    <div className="space-y-6">
      <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
        <h3 className="text-xl font-bold mb-4">Grant Story Library</h3>
        <p className="text-gray-400 mb-6">Modular content used for AI application generation - manage in Airtable</p>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-gray-700 p-4 rounded-lg border-l-4 border-blue-500">
            <h4 className="font-semibold mb-2">Company Core Stories</h4>
            <p className="text-gray-400 text-sm">Origin, mission, vision modules</p>
          </div>

          <div className="bg-gray-700 p-4 rounded-lg border-l-4 border-green-500">
            <h4 className="font-semibold mb-2">Division Overviews</h4>
            <p className="text-gray-400 text-sm">8 division success stories</p>
          </div>

          <div className="bg-gray-700 p-4 rounded-lg border-l-4 border-purple-500">
            <h4 className="font-semibold mb-2">Impact Metrics</h4>
            <p className="text-gray-400 text-sm">Measurable outcomes & data</p>
          </div>
        </div>

        <div className="mt-6">
          <button
            onClick={() => window.open('https://airtable.com', '_blank')}
            className="px-6 py-3 bg-blue-500 hover:bg-blue-600 rounded-lg font-semibold transition"
          >
            Open Story Library in Airtable →
          </button>
        </div>
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
              { id: 'dashboard', label: '📊 Dashboard', icon: '📊' },
              { id: 'opportunities', label: '🎯 Opportunities', icon: '🎯' },
              { id: 'applications', label: '✍️ Applications', icon: '✍️' },
              { id: 'pipeline', label: '📈 Pipeline', icon: '📈' },
              { id: 'story-library', label: '📚 Story Library', icon: '📚' }
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
        {activeTab === 'dashboard' && renderDashboard()}
        {activeTab === 'opportunities' && renderOpportunities()}
        {activeTab === 'applications' && renderApplications()}
        {activeTab === 'pipeline' && renderPipeline()}
        {activeTab === 'story-library' && renderStoryLibrary()}
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
                  <p className="text-2xl font-bold text-green-400">${selectedOpportunity.grantAmount.toLocaleString()}</p>
                </div>
                <div>
                  <label className="text-gray-400 text-sm">Qualification Score</label>
                  <p className="text-2xl font-bold text-yellow-400">{selectedOpportunity.qualificationScore}/100</p>
                </div>
                <div>
                  <label className="text-gray-400 text-sm">Deadline</label>
                  <p className="text-lg">{new Date(selectedOpportunity.deadline).toLocaleDateString()}</p>
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
