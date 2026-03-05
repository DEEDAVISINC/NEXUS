import React, { useState, useEffect } from 'react';
import { api } from '../api/client';
import { ViewType } from './Header';
import { ReviewOpportunityModal } from './modals/ReviewOpportunityModal';

interface AutonomousCommandCenterProps {
  onEnterSystem: (system: ViewType, initialTab?: string) => void;
}

interface Action {
  type: string;
  priority: 'high' | 'medium' | 'low' | 'info';
  title: string;
  description?: string;
  agency?: string;
  value?: number;
  deadline?: string;
  airtable_id?: string;
  action_text: string;
  cta?: string;
  cta_link?: string;
  can_auto?: boolean;
  auto_generated?: boolean;
  low_hanging_score?: number;
  progress?: string;
  urgent?: boolean;
  needs_review?: number;
}

interface DailyStats {
  target: number;
  found_today: number;
  target_met: boolean;
  urgent_mode: boolean;
}

const AutonomousCommandCenter: React.FC<AutonomousCommandCenterProps> = ({ onEnterSystem }) => {
  const [actions, setActions] = useState<Action[]>([]);
  const [loading, setLoading] = useState(true);
  const [dailyStats, setDailyStats] = useState<DailyStats | null>(null);
  const [expandedAction, setExpandedAction] = useState<string | null>(null);
  const [reviewingOpportunity, setReviewingOpportunity] = useState<any | null>(null);

  useEffect(() => {
    fetchAutonomousActions();
  }, []);

  const fetchAutonomousActions = async () => {
    setLoading(true);
    try {
      // Get autonomous actions from NEXUS
      const response = await api.get('/api/hunter/autonomous-actions');
      if (response.success) {
        setActions(response.actions || []);
      }
      
      // Also get daily target stats
      const profileResponse = await api.get('/api/hunter/profile');
      if (profileResponse?.daily_target) {
        setDailyStats(profileResponse.daily_target);
      }
    } catch (error) {
      console.error('Error fetching autonomous actions:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (value?: number): string => {
    if (!value) return '';
    if (value >= 1000000) return `$${(value / 1000000).toFixed(1)}M`;
    if (value >= 1000) return `$${(value / 1000).toFixed(0)}K`;
    return `$${value}`;
  };

  const formatDate = (dateStr?: string): string => {
    if (!dateStr) return '';
    try {
      return new Date(dateStr).toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric'
      });
    } catch {
      return dateStr;
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'bg-red-500/20 text-red-400 border-red-500/30';
      case 'medium': return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
      case 'low': return 'bg-blue-500/20 text-blue-400 border-blue-500/30';
      default: return 'bg-gray-700 text-gray-400 border-gray-600';
    }
  };

  const getActionIcon = (type: string) => {
    switch (type) {
      case 'review_opportunity': return '🎯';
      case 'generate_cap_statement': return '📄';
      case 'daily_target': return '📊';
      case 'nova_summary': return '🌟';
      case 'find_contacts': return '👥';
      case 'supplier_search': return '🔍';
      case 'past_performance_available': return '🏆';
      default: return '⚡';
    }
  };

  const handleAction = (action: Action) => {
    // Navigate based on action type
    switch (action.type) {
      case 'review_opportunity':
        // Open review modal with opportunity data formatted for the modal
        if (action.airtable_id) {
          setReviewingOpportunity({
            id: action.airtable_id,
            fields: {
              'Title': action.title,
              'Agency': action.agency,
              'Contract Value': action.value,
              'Due Date': action.deadline,
              'Description': action.description,
              'Priority': action.priority,
              'Action Type': action.type
            }
          });
        } else {
          // No airtable_id, navigate to GPSS opportunities tab
          onEnterSystem('gpss', 'opportunities');
        }
        break;
      case 'nova_summary':
        // NOVA summary - navigate to GPSS opportunities tab to see what needs review
        onEnterSystem('gpss', 'opportunities');
        break;
      case 'generate_cap_statement':
        // If we have an airtable_id, we could open a cap statement modal
        // For now, navigate to documents
        onEnterSystem('documents');
        break;
      case 'daily_target':
        onEnterSystem('opportunity-hunter');
        break;
      case 'supplier_search':
        onEnterSystem('gpss');
        break;
      default:
        // Expand to see details
        setExpandedAction(expandedAction === action.title ? null : action.title);
    }
  };

  // Calculate stats
  const highPriorityCount = actions.filter(a => a.priority === 'high').length;
  const totalValue = actions
    .filter(a => a.type === 'review_opportunity')
    .reduce((sum, a) => sum + (a.value || 0), 0);

  if (loading) {
    return (
      <div className="bg-gray-800/50 border border-gray-700 rounded-xl p-8">
        <div className="flex items-center justify-center gap-3">
          <span className="animate-spin text-2xl">⟳</span>
          <span className="text-gray-400">NEXUS is analyzing your workflow...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-gradient-to-br from-blue-600/20 to-purple-600/20 border border-blue-500/30 rounded-xl p-4">
          <div className="text-3xl font-black text-white">{actions.length}</div>
          <div className="text-sm text-gray-400">Actions Today</div>
        </div>
        <div className="bg-gradient-to-br from-red-600/20 to-orange-600/20 border border-red-500/30 rounded-xl p-4">
          <div className="text-3xl font-black text-red-400">{highPriorityCount}</div>
          <div className="text-sm text-gray-400">High Priority</div>
        </div>
        <div className="bg-gradient-to-br from-green-600/20 to-emerald-600/20 border border-green-500/30 rounded-xl p-4">
          <div className="text-3xl font-black text-green-400">{formatCurrency(totalValue)}</div>
          <div className="text-sm text-gray-400">Pipeline Value</div>
        </div>
        <div className="bg-gradient-to-br from-violet-600/20 to-indigo-600/20 border border-violet-500/30 rounded-xl p-4">
          <div className="text-3xl font-black text-violet-400">
            {dailyStats ? `${dailyStats.found_today}/${dailyStats.target}` : '-/-'}
          </div>
          <div className="text-sm text-gray-400">Daily Target</div>
          {dailyStats?.urgent_mode && (
            <div className="text-xs text-red-400 mt-1 animate-pulse">⚠️ URGENT</div>
          )}
        </div>
      </div>

      {/* AI-Powered Action Feed */}
      <div className="bg-gray-800/50 border border-gray-700 rounded-xl p-6">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <span className="text-2xl">🤖</span>
            <div>
              <h3 className="text-xl font-bold text-white">NEXUS Autonomous Command</h3>
              <p className="text-sm text-gray-400">
                {actions.length > 0 
                  ? `I've identified ${actions.length} actions for you today`
                  : 'All caught up! Check back tomorrow for new opportunities.'}
              </p>
            </div>
          </div>
          <button
            onClick={fetchAutonomousActions}
            className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg text-sm font-semibold transition"
          >
            Refresh
          </button>
        </div>

        {actions.length === 0 ? (
          <div className="text-center py-12 bg-gray-800/30 border border-gray-700 rounded-xl">
            <div className="text-6xl mb-4">✅</div>
            <h4 className="text-lg font-bold text-white mb-2">All Tasks Complete</h4>
            <p className="text-gray-400 mb-4">No pending actions at this time.</p>
            <button
              onClick={() => onEnterSystem('opportunity-hunter')}
              className="px-6 py-3 bg-blue-600 hover:bg-blue-500 rounded-lg font-semibold text-white transition"
            >
              Hunt for Opportunities →
            </button>
          </div>
        ) : (
          <div className="space-y-3">
            {actions.map((action, index) => (
              <div
                key={index}
                className={`border rounded-xl p-4 transition-all cursor-pointer hover:scale-[1.01] ${
                  action.priority === 'high' 
                    ? 'bg-red-900/10 border-red-500/30 hover:bg-red-900/20' 
                    : action.priority === 'medium'
                      ? 'bg-yellow-900/10 border-yellow-500/30 hover:bg-yellow-900/20'
                      : 'bg-gray-800/50 border-gray-700 hover:border-gray-600'
                }`}
                onClick={() => handleAction(action)}
              >
                <div className="flex items-start gap-4">
                  <div className="text-3xl">{getActionIcon(action.type)}</div>
                  
                  <div className="flex-1">
                    <div className="flex items-start justify-between gap-4">
                      <div>
                        <div className="flex items-center gap-2 mb-1">
                          <span className={`px-2 py-0.5 text-xs rounded font-bold ${getPriorityColor(action.priority)}`}>
                            {action.priority.toUpperCase()}
                          </span>
                          {action.auto_generated && (
                            <span className="px-2 py-0.5 bg-violet-500/20 text-violet-400 text-xs rounded">
                              AI DISCOVERED
                            </span>
                          )}
                          {action.low_hanging_score && action.low_hanging_score >= 70 && (
                            <span className="px-2 py-0.5 bg-green-500/20 text-green-400 text-xs rounded">
                              🍎 EASY WIN ({action.low_hanging_score})
                            </span>
                          )}
                        </div>
                        
                        <h4 className="font-bold text-white text-lg">{action.title}</h4>
                        <p className="text-gray-400 text-sm">{action.action_text}</p>
                        
                        {/* Expanded details */}
                        {expandedAction === action.title && (
                          <div className="mt-3 space-y-2 text-sm">
                            {action.agency && (
                              <p className="text-gray-300">Agency: {action.agency}</p>
                            )}
                            {action.value && (
                              <p className="text-gray-300">Value: {formatCurrency(action.value)}</p>
                            )}
                            {action.deadline && (
                              <p className="text-gray-300">Deadline: {formatDate(action.deadline)}</p>
                            )}
                            {action.can_auto && (
                              <p className="text-green-400">✓ This can be auto-generated</p>
                            )}
                          </div>
                        )}
                      </div>
                      
                      <div className="text-right">
                        {action.progress && (
                          <div className="text-lg font-bold text-blue-400">{action.progress}</div>
                        )}
                        <button 
                          className="text-sm text-blue-400 hover:text-blue-300 font-semibold"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleAction(action);
                          }}
                        >
                          {action.cta || 'Take Action →'}
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Quick Launch Pad */}
      <div className="grid grid-cols-2 md:grid-cols-6 gap-3">
        {[
          { id: 'opportunity-hunter' as ViewType, icon: '🌟', label: 'NOVA', desc: 'Find contracts' },
          { id: 'gpss' as ViewType, icon: '🎯', label: 'GPSS', desc: 'Pipeline' },
          { id: 'atlas' as ViewType, icon: '🏗️', label: 'ATLAS', desc: 'Projects' },
          { id: 'prism' as ViewType, icon: '🔮', label: 'PRISM', desc: 'Field ops' },
          { id: 'compass' as ViewType, icon: '🧭', label: 'COMPASS', desc: 'Deliveries' },
          { id: 'vertex' as ViewType, icon: '💎', label: 'VERTEX', desc: 'Financials' }
        ].map((system) => (
          <button
            key={system.id}
            onClick={() => onEnterSystem(system.id)}
            className="bg-gray-800 hover:bg-gray-700 border border-gray-700 hover:border-gray-600 rounded-xl p-4 transition-all text-left"
          >
            <div className="text-2xl mb-2">{system.icon}</div>
            <div className="font-bold text-white">{system.label}</div>
            <div className="text-xs text-gray-500">{system.desc}</div>
          </button>
        ))}
      </div>

      {/* Review Opportunity Modal */}
      {reviewingOpportunity && (
        <ReviewOpportunityModal
          opportunity={reviewingOpportunity}
          onClose={() => setReviewingOpportunity(null)}
          onSuccess={() => {
            fetchAutonomousActions();
            setReviewingOpportunity(null);
          }}
        />
      )}
    </div>
  );
};

export default AutonomousCommandCenter;
