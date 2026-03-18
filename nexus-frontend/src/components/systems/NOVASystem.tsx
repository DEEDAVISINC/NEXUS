import React, { useState, useEffect } from 'react';
import { api } from '../../api/client';

interface NOVASystemProps {
  onBackToNexus: () => void;
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

interface DDIProfile {
  name: string;
  certifications: string[];
  business_types: Array<{
    code: string;
    label: string;
    description: string;
    ddi_has: boolean;
  }>;
  naics_codes: string[];
  daily_target: {
    target: number;
    found_today: number;
    urgent_mode: boolean;
    last_reset: string;
  };
}

interface Opportunity {
  id: string;
  title: string;
  agency: string;
  solicitation_number?: string;
  contract_value: number;
  due_date?: string;
  posted_date?: string;
  set_aside_type?: string;
  description?: string;
  url?: string;
  match_score?: number;
  match_reasons?: string[];
  low_hanging_score?: number;
  low_hanging_reasons?: string[];
  naics_codes?: string[];
  business_types?: string[];
  past_perf_required?: boolean;
  past_perf_note?: string;
}

interface AgencyScorecard {
  name: string;
  total_awards: number;
  total_value: number;
  avg_award_size: number;
  success_rate: number;
  to_ddi: number;
  ddi_rank: number;
  opportunity_count: number;
  scorecard_data?: any;
}

interface SearchCriteria {
  mode: 'internal' | 'live' | 'combined' | 'low-hanging';
  naicsCodes: string[];
  businessTypes: string[];
  contractSize: string;
  minValue: number;
  maxValue: number;
  keywords: string;
  onlyNoPastPerf: boolean;
}

const NOVASystem: React.FC<NOVASystemProps> = ({ 
  onBackToNexus, 
  activeTab, 
  setActiveTab 
}) => {
  // State Management
  const [loading, setLoading] = useState(false);
  const [profile, setProfile] = useState<DDIProfile | null>(null);
  const [opportunities, setOpportunities] = useState<Opportunity[]>([]);
  const [agencyScorecards, setAgencyScorecards] = useState<AgencyScorecard[]>([]);
  const [warning, setWarning] = useState<string | null>(null);
  const [searchCriteria, setSearchCriteria] = useState<SearchCriteria>({
    mode: 'combined',
    naicsCodes: [],
    businessTypes: ['EDWOSB'],
    contractSize: 'any',
    minValue: 0,
    maxValue: 100000000,
    keywords: '',
    onlyNoPastPerf: false
  });
  const [selectedOpportunity, setSelectedOpportunity] = useState<Opportunity | null>(null);
  const [notification, setNotification] = useState<{message: string, type: 'success' | 'error'} | null>(null);
  const [addingToPipeline, setAddingToPipeline] = useState(false);

  // Tab definitions
  const tabs = [
    { id: 'search', label: '🔍 Search', icon: '🔍' },
    { id: 'results', label: '📊 Results', icon: '📊' },
    { id: 'agencies', label: '🏛️ Agencies', icon: '🏛️' },
    { id: 'settings', label: '⚙️ Settings', icon: '⚙️' }
  ];

  // Load profile on mount
  useEffect(() => {
    fetchProfile();
    // Set default active tab if not set
    if (!activeTab || !tabs.find(t => t.id === activeTab)) {
      setActiveTab('search');
    }
  }, []);

  const fetchProfile = async () => {
    try {
      const response = await api.get('/api/hunter/profile');
      setProfile(response);
    } catch (error) {
      console.error('Error fetching profile:', error);
      showNotification('Error loading profile', 'error');
    }
  };

  const showNotification = (message: string, type: 'success' | 'error' = 'success') => {
    setNotification({ message, type });
    setTimeout(() => setNotification(null), 5000);
  };

  const handleAddToPipeline = async (opp: Opportunity) => {
    setAddingToPipeline(true);
    try {
      const response = await api.post('/api/hunter/add-to-pipeline', {
        title: opp.title,
        agency: opp.agency,
        solicitation_number: opp.solicitation_number,
        contract_value: opp.contract_value,
        due_date: opp.due_date,
        description: opp.description,
        set_aside_type: opp.set_aside_type,
        naics_codes: opp.naics_codes,
        url: opp.url,
        source: 'SAM.gov - NOVA Discovery',
        auto_generate_cap_statement: true,
        past_perf_required: opp.past_perf_required,
        low_hanging_score: opp.low_hanging_score,
        match_score: opp.match_score
      });

      if (response.success) {
        showNotification(`✅ Added to GPSS: ${opp.title.substring(0, 50)}...`, 'success');
        setSelectedOpportunity(null);
        // Could also navigate to GPSS here: onBackToNexus() then navigateToSystem('gpss')
      } else {
        showNotification(`❌ Failed: ${response.error}`, 'error');
      }
    } catch (error) {
      console.error('Error adding to pipeline:', error);
      showNotification('❌ Failed to add to pipeline', 'error');
    } finally {
      setAddingToPipeline(false);
    }
  };

  const handleSearch = async () => {
    setLoading(true);
    setWarning(null);
    setOpportunities([]);
    setAgencyScorecards([]);

    try {
      const endpoint = searchCriteria.mode === 'low-hanging' 
        ? '/api/hunter/low-hanging-fruit'
        : '/api/hunter/agencies';

      const response = await api.post(endpoint, {
        business_types: searchCriteria.businessTypes,
        naics_codes: searchCriteria.naicsCodes,
        contract_size: searchCriteria.contractSize,
        min_value: searchCriteria.minValue,
        max_value: searchCriteria.maxValue,
        keywords: searchCriteria.keywords,
        no_past_perf_required: searchCriteria.onlyNoPastPerf
      });

      if (response.opportunities) {
        setOpportunities(response.opportunities);
        showNotification(`Found ${response.opportunities.length} opportunities`, 'success');
      }

      if (response.agency_scorecards) {
        setAgencyScorecards(response.agency_scorecards);
      }

      if (response.past_perf_warning) {
        setWarning(response.past_perf_warning);
      }

      // Switch to results tab
      setActiveTab('results');
    } catch (error) {
      console.error('Search error:', error);
      showNotification('Search failed. Please try again.', 'error');
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (value: number): string => {
    if (value >= 1000000) return `$${(value / 1000000).toFixed(1)}M`;
    if (value >= 1000) return `$${(value / 1000).toFixed(0)}K`;
    return `$${value}`;
  };

  const formatDate = (dateStr?: string): string => {
    if (!dateStr) return 'N/A';
    try {
      return new Date(dateStr).toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric'
      });
    } catch {
      return dateStr;
    }
  };

  const toggleBusinessType = (typeCode: string) => {
    setSearchCriteria(prev => ({
      ...prev,
      businessTypes: prev.businessTypes.includes(typeCode)
        ? prev.businessTypes.filter(t => t !== typeCode)
        : [...prev.businessTypes, typeCode]
    }));
  };

  const getContractSizeLabel = (size: string): string => {
    const labels: Record<string, string> = {
      'any': '🌟 Any Size',
      'micro': '🛒 Micro-Purchase (< $10K)',
      'simplified': '📋 Simplified Acquisition (< $250K)',
      'under350k': '💰 Under $350K (No Past Perf)',
      'sb_setaside': '💼 Small Business Set-Aside (< $500K)',
      'mid': '📊 Mid-Size ($500K - $1M)',
      'strategic': '🎯 Strategic ($1M+)'
    };
    return labels[size] || size;
  };

  // Render functions
  const renderSearchTab = () => (
    <div className="space-y-6">
      {/* Daily Target Progress */}
      {profile?.daily_target && (
        <div className="bg-gradient-to-r from-blue-900/30 to-purple-900/30 border border-blue-500/30 rounded-xl p-4">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-3">
              <span className="text-2xl">🎯</span>
              <div>
                <h3 className="font-bold text-white">Daily Target Progress</h3>
                <p className="text-sm text-gray-400">
                  {profile.daily_target.found_today} of {profile.daily_target.target} opportunities found today
                </p>
              </div>
            </div>
            <div className={`px-3 py-1 rounded-full text-sm font-bold ${
              profile.daily_target.urgent_mode 
                ? 'bg-red-500/20 text-red-400 animate-pulse' 
                : profile.daily_target.found_today >= profile.daily_target.target
                  ? 'bg-green-500/20 text-green-400'
                  : 'bg-yellow-500/20 text-yellow-400'
            }`}>
              {profile.daily_target.urgent_mode ? '⚠️ URGENT MODE' : 
               profile.daily_target.found_today >= profile.daily_target.target ? '✅ TARGET MET' : 
               '⏳ IN PROGRESS'}
            </div>
          </div>
          <div className="w-full bg-gray-700 rounded-full h-3">
            <div 
              className={`h-3 rounded-full transition-all ${
                profile.daily_target.urgent_mode ? 'bg-red-500' :
                profile.daily_target.found_today >= profile.daily_target.target ? 'bg-green-500' :
                'bg-yellow-500'
              }`}
              style={{ 
                width: `${Math.min(100, (profile.daily_target.found_today / profile.daily_target.target) * 100)}%` 
              }}
            />
          </div>
        </div>
      )}

      {/* Search Mode Selector */}
      <div className="bg-gray-800/50 border border-gray-700 rounded-xl p-6">
        <h3 className="text-lg font-bold text-white mb-4">Search Mode</h3>
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
          {[
            { id: 'internal', label: '🗄️ Internal Database', desc: 'Search existing Airtable data' },
            { id: 'live', label: '🔴 Live Federal', desc: 'Real-time SAM.gov search' },
            { id: 'combined', label: '🌟 Full Opportunity Hunt', desc: 'Internal + Live + Intelligence', featured: true },
            { id: 'low-hanging', label: '🍎 Quick Wins Only', desc: 'Low-competition opportunities' }
          ].map((mode) => (
            <button
              key={mode.id}
              onClick={() => setSearchCriteria(prev => ({ ...prev, mode: mode.id as any }))}
              className={`p-4 rounded-xl border text-left transition-all ${
                searchCriteria.mode === mode.id
                  ? mode.featured
                    ? 'bg-gradient-to-br from-blue-600/30 to-purple-600/30 border-blue-500/50 ring-2 ring-blue-500/30'
                    : 'bg-blue-600/20 border-blue-500/50'
                  : 'bg-gray-800 border-gray-700 hover:border-gray-600'
              }`}
            >
              <div className="font-bold text-white mb-1">{mode.label}</div>
              <div className="text-xs text-gray-400">{mode.desc}</div>
              {mode.featured && (
                <div className="mt-2 inline-block px-2 py-0.5 bg-blue-500/20 text-blue-400 text-xs rounded-full">
                  Recommended
                </div>
              )}
            </button>
          ))}
        </div>
      </div>

      {/* Business Types */}
      <div className="bg-gray-800/50 border border-gray-700 rounded-xl p-6">
        <h3 className="text-lg font-bold text-white mb-4">Business Type Filters</h3>
        <p className="text-sm text-gray-400 mb-4">Select certifications to filter opportunities (DDI has these):</p>
        <div className="grid grid-cols-3 lg:grid-cols-5 gap-3">
          {profile?.business_types?.map((bt) => (
            <label
              key={bt.code}
              className={`flex items-center gap-2 p-3 rounded-lg border cursor-pointer transition-all ${
                searchCriteria.businessTypes.includes(bt.code)
                  ? 'bg-blue-600/20 border-blue-500/50'
                  : 'bg-gray-800 border-gray-700 hover:border-gray-600'
              }`}
            >
              <input
                type="checkbox"
                checked={searchCriteria.businessTypes.includes(bt.code)}
                onChange={() => toggleBusinessType(bt.code)}
                className="w-4 h-4 rounded border-gray-600 text-blue-500 focus:ring-blue-500"
              />
              <span className="text-sm text-white">{bt.label}</span>
              {bt.ddi_has && (
                <span className="ml-auto text-xs bg-green-500/20 text-green-400 px-1.5 py-0.5 rounded">
                  DDI
                </span>
              )}
            </label>
          ))}
        </div>
      </div>

      {/* Contract Size */}
      <div className="bg-gray-800/50 border border-gray-700 rounded-xl p-6">
        <h3 className="text-lg font-bold text-white mb-4">Contract Size</h3>
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
          {[
            { id: 'any', label: '🌟 Any Size', desc: 'All contract values' },
            { id: 'strategic', label: '🎯 Strategic ($1M+)', desc: 'Large opportunities' },
            { id: 'mid', label: '💼 Mid-Size ($500K-$1M)', desc: 'Medium contracts' },
            { id: 'sb_setaside', label: '💰 SB Set-Aside (<$500K)', desc: 'Small business' },
            { id: 'under350k', label: '📋 Under $350K', desc: '✓ No past perf required' },
            { id: 'simplified', label: '🛒 Simplified (<$250K)', desc: 'Quick wins' },
            { id: 'micro', label: '🛒 Micro (<$10K)', desc: 'Purchase card' }
          ].map((size) => (
            <button
              key={size.id}
              onClick={() => setSearchCriteria(prev => ({ ...prev, contractSize: size.id }))}
              className={`p-3 rounded-lg border text-left transition-all ${
                searchCriteria.contractSize === size.id
                  ? 'bg-blue-600/20 border-blue-500/50'
                  : 'bg-gray-800 border-gray-700 hover:border-gray-600'
              }`}
            >
              <div className="font-semibold text-white text-sm">{size.label}</div>
              <div className="text-xs text-gray-400">{size.desc}</div>
            </button>
          ))}
        </div>
      </div>

      {/* Keywords */}
      <div className="bg-gray-800/50 border border-gray-700 rounded-xl p-6">
        <h3 className="text-lg font-bold text-white mb-4">Keywords (Optional)</h3>
        <input
          type="text"
          placeholder="Enter keywords to search (e.g., 'medical courier', 'IT services', 'construction')..."
          value={searchCriteria.keywords}
          onChange={(e) => setSearchCriteria(prev => ({ ...prev, keywords: e.target.value }))}
          className="w-full bg-gray-900 border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-blue-500"
        />
      </div>

      {/* Past Performance Filter */}
      <div className="bg-yellow-900/20 border border-yellow-500/30 rounded-xl p-6">
        <div className="flex items-start gap-3">
          <span className="text-2xl">⚠️</span>
          <div>
            <h3 className="font-bold text-yellow-400 mb-2">Past Performance Requirements (FAR 42.1502)</h3>
            <p className="text-sm text-gray-300 mb-3">
              Contracts under <strong>$350,000</strong> (Simplified Acquisition Threshold) do NOT require past performance evaluations. 
              This applies to ALL contracts regardless of set-aside type.
            </p>
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={searchCriteria.onlyNoPastPerf}
                onChange={(e) => setSearchCriteria(prev => ({ ...prev, onlyNoPastPerf: e.target.checked }))}
                className="w-4 h-4 rounded border-gray-600 text-yellow-500 focus:ring-yellow-500"
              />
              <span className="text-sm text-white">Only show opportunities with NO past performance required</span>
            </label>
          </div>
        </div>
      </div>

      {/* Search Button */}
      <button
        onClick={handleSearch}
        disabled={loading}
        className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 disabled:from-gray-700 disabled:to-gray-600 disabled:cursor-not-allowed py-4 rounded-xl font-bold text-white text-lg transition-all"
      >
        {loading ? (
          <span className="flex items-center justify-center gap-2">
            <span className="animate-spin">⟳</span>
            Hunting Opportunities...
          </span>
        ) : searchCriteria.mode === 'low-hanging' ? (
          '🍎 FIND QUICK WINS'
        ) : (
          '🚀 HUNT ALL OPPORTUNITIES'
        )}
      </button>
    </div>
  );

  const renderResultsTab = () => (
    <div className="space-y-6">
      {warning && (
        <div className="bg-yellow-900/20 border border-yellow-500/30 rounded-xl p-4">
          <div className="flex items-start gap-3">
            <span className="text-xl">⚠️</span>
            <div>
              <h4 className="font-bold text-yellow-400">Past Performance Required</h4>
              <p className="text-sm text-gray-300">{warning}</p>
            </div>
          </div>
        </div>
      )}

      {opportunities.length === 0 ? (
        <div className="text-center py-16 bg-gray-800/50 border border-gray-700 rounded-xl">
          <div className="text-6xl mb-4">🔍</div>
          <h3 className="text-xl font-bold text-white mb-2">No Opportunities Yet</h3>
          <p className="text-gray-400 mb-4">Run a search to find federal contracting opportunities</p>
          <button
            onClick={() => setActiveTab('search')}
            className="px-6 py-3 bg-blue-600 hover:bg-blue-500 rounded-lg font-semibold text-white transition"
          >
            Start Search →
          </button>
        </div>
      ) : (
        <>
          <div className="flex items-center justify-between">
            <h3 className="text-xl font-bold text-white">
              📊 {opportunities.length} Opportunities Found
            </h3>
            <div className="flex gap-2">
              <button
                onClick={() => setOpportunities([])}
                className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg text-sm font-semibold transition"
              >
                Clear Results
              </button>
              <button
                onClick={() => setActiveTab('search')}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-500 rounded-lg text-sm font-semibold transition"
              >
                New Search
              </button>
            </div>
          </div>

          <div className="grid gap-4">
            {opportunities.map((opp) => (
              <div
                key={opp.id}
                onClick={() => setSelectedOpportunity(opp)}
                className="bg-gray-800/50 border border-gray-700 hover:border-blue-500/50 rounded-xl p-5 cursor-pointer transition-all hover:shadow-lg hover:shadow-blue-500/10"
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h4 className="font-bold text-white text-lg">{opp.title}</h4>
                      {opp.low_hanging_score && opp.low_hanging_score >= 70 && (
                        <span className="px-2 py-1 bg-green-500/20 text-green-400 text-xs rounded-full font-bold">
                          🍎 Easy Win ({opp.low_hanging_score}/100)
                        </span>
                      )}
                      {opp.past_perf_required === false && (
                        <span className="px-2 py-1 bg-blue-500/20 text-blue-400 text-xs rounded-full">
                          ✓ No Past Perf
                        </span>
                      )}
                    </div>
                    <p className="text-gray-400 text-sm mb-3">{opp.agency}</p>
                    
                    <div className="flex flex-wrap gap-2 mb-3">
                      {opp.solicitation_number && (
                        <span className="px-2 py-1 bg-gray-700 text-gray-300 text-xs rounded">
                          📋 {opp.solicitation_number}
                        </span>
                      )}
                      <span className="px-2 py-1 bg-gray-700 text-gray-300 text-xs rounded">
                        💰 {formatCurrency(opp.contract_value)}
                      </span>
                      {opp.due_date && (
                        <span className="px-2 py-1 bg-gray-700 text-gray-300 text-xs rounded">
                          ⏰ Due: {formatDate(opp.due_date)}
                        </span>
                      )}
                      {opp.set_aside_type && (
                        <span className="px-2 py-1 bg-purple-500/20 text-purple-400 text-xs rounded">
                          {opp.set_aside_type}
                        </span>
                      )}
                    </div>

                    {(opp.low_hanging_reasons || opp.match_reasons) && (
                      <div className="flex flex-wrap gap-2">
                        {(opp.low_hanging_reasons || opp.match_reasons)?.map((reason, idx) => (
                          <span key={idx} className="px-2 py-1 bg-blue-500/10 text-blue-400 text-xs rounded-full">
                            {reason}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>

                  <div className="text-right">
                    {opp.match_score && (
                      <div className="text-2xl font-bold text-blue-400 mb-1">
                        {opp.match_score}%
                      </div>
                    )}
                    <div className="text-xs text-gray-500">Match Score</div>
                    {opp.url && (
                      <a
                        href={opp.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        onClick={(e) => e.stopPropagation()}
                        className="text-sm text-blue-400 hover:text-blue-300 mt-2 inline-block"
                      >
                        View →
                      </a>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </>
      )}

      {/* Opportunity Detail Modal */}
      {selectedOpportunity && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
          <div className="bg-gray-800 border border-gray-700 rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-start justify-between mb-4">
                <h3 className="text-xl font-bold text-white">{selectedOpportunity.title}</h3>
                <button
                  onClick={() => setSelectedOpportunity(null)}
                  className="text-gray-400 hover:text-white text-2xl"
                >
                  ×
                </button>
              </div>
              
              <div className="space-y-4">
                <div>
                  <label className="text-sm text-gray-400">Agency</label>
                  <p className="text-white font-semibold">{selectedOpportunity.agency}</p>
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm text-gray-400">Contract Value</label>
                    <p className="text-white font-semibold">{formatCurrency(selectedOpportunity.contract_value)}</p>
                  </div>
                  <div>
                    <label className="text-sm text-gray-400">Due Date</label>
                    <p className="text-white font-semibold">{formatDate(selectedOpportunity.due_date)}</p>
                  </div>
                </div>

                {selectedOpportunity.description && (
                  <div>
                    <label className="text-sm text-gray-400">Description</label>
                    <p className="text-gray-300 text-sm mt-1">{selectedOpportunity.description}</p>
                  </div>
                )}

                {selectedOpportunity.past_perf_note && (
                  <div className="bg-yellow-900/20 border border-yellow-500/30 rounded-lg p-3">
                    <p className="text-yellow-400 text-sm">⚠️ {selectedOpportunity.past_perf_note}</p>
                  </div>
                )}

                <div className="flex gap-3 pt-4">
                  <button
                    onClick={() => handleAddToPipeline(selectedOpportunity)}
                    disabled={addingToPipeline}
                    className="flex-1 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-500 hover:to-emerald-500 disabled:from-gray-700 disabled:to-gray-600 py-3 rounded-lg font-semibold text-white transition flex items-center justify-center gap-2"
                  >
                    {addingToPipeline ? (
                      <>
                        <span className="animate-spin">⟳</span>
                        Adding to Pipeline...
                      </>
                    ) : (
                      <>
                        <span>➕</span>
                        Add to GPSS Pipeline
                      </>
                    )}
                  </button>
                  {selectedOpportunity.url && (
                    <a
                      href={selectedOpportunity.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="px-6 py-3 bg-blue-600 hover:bg-blue-500 rounded-lg font-semibold text-white transition text-center"
                    >
                      SAM.gov →
                    </a>
                  )}
                  <button
                    onClick={() => setSelectedOpportunity(null)}
                    className="px-6 py-3 bg-gray-700 hover:bg-gray-600 rounded-lg font-semibold text-white transition"
                  >
                    Close
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );

  const renderAgenciesTab = () => (
    <div className="space-y-6">
      {agencyScorecards.length === 0 ? (
        <div className="text-center py-16 bg-gray-800/50 border border-gray-700 rounded-xl">
          <div className="text-6xl mb-4">🏛️</div>
          <h3 className="text-xl font-bold text-white mb-2">No Agency Data Yet</h3>
          <p className="text-gray-400 mb-4">Run a search to see agency scorecards</p>
          <button
            onClick={() => setActiveTab('search')}
            className="px-6 py-3 bg-blue-600 hover:bg-blue-500 rounded-lg font-semibold text-white transition"
          >
            Start Search →
          </button>
        </div>
      ) : (
        <>
          <h3 className="text-xl font-bold text-white">🏛️ Agency Scorecards</h3>
          <div className="grid gap-4">
            {agencyScorecards.map((agency) => (
              <div
                key={agency.name}
                className="bg-gray-800/50 border border-gray-700 rounded-xl p-5"
              >
                <div className="flex items-start justify-between gap-4 mb-4">
                  <div>
                    <h4 className="font-bold text-white text-lg">{agency.name}</h4>
                    <p className="text-gray-400 text-sm">
                      {agency.opportunity_count} opportunities • Rank #{agency.ddi_rank}
                    </p>
                  </div>
                  <div className="text-right">
                    <div className="text-2xl font-bold text-green-400">
                      ${(agency.to_ddi / 1000000).toFixed(1)}M
                    </div>
                    <div className="text-xs text-gray-500">To DDI</div>
                  </div>
                </div>

                <div className="grid grid-cols-4 gap-4">
                  <div className="bg-gray-700/50 rounded-lg p-3 text-center">
                    <div className="text-xl font-bold text-blue-400">{agency.total_awards}</div>
                    <div className="text-xs text-gray-500">Awards</div>
                  </div>
                  <div className="bg-gray-700/50 rounded-lg p-3 text-center">
                    <div className="text-xl font-bold text-purple-400">
                      ${(agency.total_value / 1000000).toFixed(1)}M
                    </div>
                    <div className="text-xs text-gray-500">Total Value</div>
                  </div>
                  <div className="bg-gray-700/50 rounded-lg p-3 text-center">
                    <div className="text-xl font-bold text-yellow-400">
                      ${(agency.avg_award_size / 1000).toFixed(0)}K
                    </div>
                    <div className="text-xs text-gray-500">Avg Award</div>
                  </div>
                  <div className="bg-gray-700/50 rounded-lg p-3 text-center">
                    <div className="text-xl font-bold text-green-400">
                      {(agency.success_rate * 100).toFixed(0)}%
                    </div>
                    <div className="text-xs text-gray-500">Win Rate</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );

  const renderSettingsTab = () => (
    <div className="space-y-6">
      <div className="bg-gray-800/50 border border-gray-700 rounded-xl p-6">
        <h3 className="text-lg font-bold text-white mb-4">DDI Profile</h3>
        {profile && (
          <div className="space-y-4">
            <div>
              <label className="text-sm text-gray-400">Company</label>
              <p className="text-white font-semibold">{profile.name}</p>
            </div>
            <div>
              <label className="text-sm text-gray-400">Certifications</label>
              <div className="flex flex-wrap gap-2 mt-1">
                {profile.certifications?.map((cert) => (
                  <span key={cert} className="px-2 py-1 bg-blue-500/20 text-blue-400 text-xs rounded-full">
                    {cert}
                  </span>
                ))}
              </div>
            </div>
            <div>
              <label className="text-sm text-gray-400">NAICS Codes</label>
              <p className="text-gray-300 text-sm mt-1">{profile.naics_codes?.join(', ')}</p>
            </div>
          </div>
        )}
      </div>

      <div className="bg-gray-800/50 border border-gray-700 rounded-xl p-6">
        <h3 className="text-lg font-bold text-white mb-4">About NOVA</h3>
      <div className="space-y-3 text-sm text-gray-400">
        <p className="text-base font-bold text-white">N·O·V·A — New Opportunity Vetting & Acquisition</p>
        <p>🎯 <strong className="text-white">Daily Target:</strong> Find 3 new opportunities each day to bid on 12+ per month</p>
        <p>🔴 <strong className="text-white">Live Search:</strong> Real-time SAM.gov API integration</p>
        <p>🍎 <strong className="text-white">Quick Wins:</strong> AI-powered low-competition scoring</p>
        <p>🏛️ <strong className="text-white">Agency Intelligence:</strong> Historical award data and success rates</p>
        <p>⚠️ <strong className="text-white">Past Performance:</strong> Automatic flagging of contracts requiring past performance</p>
        <p>🔗 <strong className="text-white">NEXUS-Native:</strong> Every opportunity flows directly into GPSS pipeline</p>
      </div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Notification */}
      {notification && (
        <div className={`fixed top-20 right-4 z-50 px-6 py-3 rounded-lg shadow-lg transition-all ${
          notification.type === 'success' ? 'bg-green-600' : 'bg-red-600'
        }`}>
          <p className="font-semibold">{notification.message}</p>
        </div>
      )}

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Tab Navigation */}
        <div className="flex gap-2 mb-8 border-b border-gray-700 pb-4">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-6 py-3 rounded-lg font-semibold transition-all ${
                activeTab === tab.id
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-800 text-gray-400 hover:bg-gray-700 hover:text-white'
              }`}
            >
              <span className="mr-2">{tab.icon}</span>
              {tab.label}
            </button>
          ))}
        </div>

        {/* Tab Content */}
        <div className="min-h-[500px]">
          {activeTab === 'search' && renderSearchTab()}
          {activeTab === 'results' && renderResultsTab()}
          {activeTab === 'agencies' && renderAgenciesTab()}
          {activeTab === 'settings' && renderSettingsTab()}
        </div>
      </div>
    </div>
  );
};

export default NOVASystem;
