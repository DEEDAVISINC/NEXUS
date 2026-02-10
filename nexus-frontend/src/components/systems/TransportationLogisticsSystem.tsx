import React, { useState, useEffect } from 'react';
import { api } from '../../api/client';

interface TransportationLogisticsSystemProps {
  onBackToNexus: () => void;
}

interface Category {
  display_name: string;
  description: string;
  primary_keywords: string[];
  secondary_keywords: string[];
  sam_gov_searches: string[];
  estimated_contract_range: string;
  typical_duration: string;
  sourcing_difficulty: string;
  key_suppliers: string[];
  special_note?: string;
}

interface SearchString {
  category: string;
  category_name: string;
  search_string: string;
  estimated_results: string;
}

interface TodaysFocus {
  day: string;
  focus: string;
  searches: string[];
  direct_sites: string[];
  message: string;
}

const TransportationLogisticsSystem: React.FC<TransportationLogisticsSystemProps> = ({ onBackToNexus }) => {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [categories, setCategories] = useState<Record<string, Category>>({});
  const [searchStrings, setSearchStrings] = useState<SearchString[]>([]);
  const [todaysFocus, setTodaysFocus] = useState<TodaysFocus | null>(null);
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [copiedText, setCopiedText] = useState<string | null>(null);

  const tabs = [
    { id: 'dashboard', label: '📊 Dashboard', icon: '📊' },
    { id: 'quick-start', label: '🚀 Quick Start', icon: '🚀' },
    { id: 'categories', label: '📚 Categories', icon: '📚' },
    { id: 'searches', label: '🔍 Search Strings', icon: '🔍' },
    { id: 'sources', label: '🌐 Direct Sources', icon: '🌐' },
    { id: 'revenue', label: '💰 Revenue Potential', icon: '💰' }
  ];

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      // In production, these would be actual API calls
      // For now, using mock data structure
      setCategories({
        airport_aviation: {
          display_name: '✈️ Airport & Aviation',
          description: 'Airport operations, aviation supplies, ground equipment',
          primary_keywords: ['airport supplies', 'aviation supplies', 'airfield supplies'],
          secondary_keywords: ['runway marking', 'deicing equipment', 'hangar supplies'],
          sam_gov_searches: [
            '"airport supplies" WOSB',
            '"aviation supplies" small business',
            '"airfield supplies" woman owned'
          ],
          estimated_contract_range: '$30K-$500K',
          typical_duration: 'Annual or multi-year',
          sourcing_difficulty: 'Medium',
          key_suppliers: ['Grainger', 'Fastenal', 'Aviation specialty distributors']
        },
        port_marine: {
          display_name: '🚢 Port & Marine',
          description: 'Port operations, marine supplies, dock equipment',
          primary_keywords: ['port supplies', 'marine supplies', 'maritime supplies'],
          secondary_keywords: ['dock hardware', 'mooring equipment', 'marine rope'],
          sam_gov_searches: [
            '"marine supplies" WOSB',
            '"port supplies" EDWOSB',
            '"maritime supplies" small business'
          ],
          estimated_contract_range: '$40K-$400K',
          typical_duration: 'Annual contracts',
          sourcing_difficulty: 'Medium-High',
          key_suppliers: ['West Marine Commercial', 'Defender Industries', 'Fisheries Supply']
        },
        cargo_freight: {
          display_name: '📦 Cargo & Freight',
          description: 'Cargo handling, warehouse operations, freight supplies',
          primary_keywords: ['cargo handling equipment', 'freight supplies', 'warehouse equipment'],
          secondary_keywords: ['pallet wrap', 'stretch film', 'cargo straps'],
          sam_gov_searches: [
            '"cargo handling equipment" WOSB',
            '"warehouse supplies" small business',
            '"material handling" EDWOSB'
          ],
          estimated_contract_range: '$25K-$300K',
          typical_duration: 'Annual contracts',
          sourcing_difficulty: 'Easy-Medium',
          key_suppliers: ['Uline', 'Grainger', 'Fastenal']
        },
        courier_postal: {
          display_name: '📬 Courier & Postal',
          description: 'USPS, courier services, mailing supplies',
          primary_keywords: ['postal supplies', 'courier supplies', 'mailing supplies'],
          secondary_keywords: ['bubble mailers', 'shipping boxes', 'packaging tape'],
          sam_gov_searches: [
            '"postal supplies" WOSB',
            '"mailing supplies" small business',
            '"courier supplies" EDWOSB'
          ],
          estimated_contract_range: '$20K-$200K',
          typical_duration: 'Annual or multi-facility',
          sourcing_difficulty: 'Easy',
          key_suppliers: ['Uline', 'Grainger', 'Standard shipping suppliers'],
          special_note: 'USPS is HUGE opportunity - 31,000+ facilities nationwide!'
        },
        transit_transportation: {
          display_name: '🚌 Transit & Transportation',
          description: 'Transit authorities, bus operations, transportation facilities',
          primary_keywords: ['transit supplies', 'transportation supplies', 'bus supplies'],
          secondary_keywords: ['bus terminal supplies', 'dispatch supplies', 'driver supplies'],
          sam_gov_searches: [
            '"transit supplies" WOSB',
            '"transportation supplies" small business',
            '"bus supplies" EDWOSB'
          ],
          estimated_contract_range: '$30K-$250K',
          typical_duration: 'Annual contracts',
          sourcing_difficulty: 'Easy-Medium',
          key_suppliers: ['Grainger', 'Fastenal', 'Fleet specialty suppliers']
        }
      });

      setTodaysFocus({
        day: new Date().toLocaleDateString('en-US', { weekday: 'long' }),
        focus: 'Airport & Aviation',
        searches: [
          '"airport supplies" WOSB',
          '"aviation supplies" small business',
          '"terminal supplies" EDWOSB'
        ],
        direct_sites: ['Detroit Metro Airport', 'Gerald R. Ford Airport'],
        message: "Today's focus: Airport & Aviation"
      });

      setStats({
        total_categories: 5,
        total_keywords: 100,
        total_search_strings: 35,
        expected_weekly_opportunities: '30-50 opportunities',
        expected_monthly_revenue: '$10K-$30K',
        expected_annual_revenue: '$300K-$500K'
      });
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedText(text);
    setTimeout(() => setCopiedText(null), 2000);
  };

  const renderDashboard = () => (
    <div className="space-y-6">
      {/* Hero Section */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl p-8 text-white">
        <h2 className="text-3xl font-black mb-3">✈️🚢 Transportation & Logistics Opportunities</h2>
        <p className="text-lg text-blue-100 mb-6">
          Find airport, port, cargo, courier, and marine contracts • $300K-$500K annual revenue potential
        </p>
        
        <div className="grid grid-cols-3 gap-4">
          <div className="bg-white/10 backdrop-blur rounded-lg p-4">
            <div className="text-4xl font-black">{stats?.total_categories || 5}</div>
            <div className="text-sm text-blue-100">Categories</div>
          </div>
          <div className="bg-white/10 backdrop-blur rounded-lg p-4">
            <div className="text-4xl font-black">{stats?.total_keywords || 100}+</div>
            <div className="text-sm text-blue-100">Keywords</div>
          </div>
          <div className="bg-white/10 backdrop-blur rounded-lg p-4">
            <div className="text-4xl font-black">{stats?.total_search_strings || 35}</div>
            <div className="text-sm text-blue-100">Search Strings</div>
          </div>
        </div>
      </div>

      {/* Today's Focus */}
      {todaysFocus && (
        <div className="bg-gradient-to-br from-green-900/30 to-green-800/20 border-2 border-green-500 rounded-xl p-6">
          <div className="flex items-start justify-between mb-4">
            <div>
              <h3 className="text-2xl font-black text-green-400 mb-2">
                🎯 TODAY'S FOCUS: {todaysFocus.focus}
              </h3>
              <p className="text-gray-300">
                {todaysFocus.day}'s recommended searches
              </p>
            </div>
          </div>

          <div className="space-y-3">
            <div>
              <div className="text-sm font-bold text-green-400 mb-2">SEARCH STRINGS:</div>
              {todaysFocus.searches.map((search, idx) => (
                <div key={idx} className="flex items-center gap-2 mb-2">
                  <code className="flex-1 bg-gray-900/50 px-3 py-2 rounded text-green-300 text-sm">
                    {search}
                  </code>
                  <button
                    onClick={() => copyToClipboard(search)}
                    className="px-3 py-2 bg-green-600 hover:bg-green-700 rounded text-sm font-bold transition"
                  >
                    {copiedText === search ? '✓ Copied!' : 'Copy'}
                  </button>
                </div>
              ))}
            </div>

            <div>
              <div className="text-sm font-bold text-green-400 mb-2">CHECK THESE SITES:</div>
              <div className="flex flex-wrap gap-2">
                {todaysFocus.direct_sites.map((site, idx) => (
                  <span key={idx} className="bg-green-900/30 px-3 py-1 rounded-full text-sm text-green-300">
                    {site}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Quick Stats */}
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-gray-800/50 border border-gray-700 rounded-lg p-5">
          <div className="text-yellow-400 text-2xl font-black mb-2">
            {stats?.expected_weekly_opportunities || '30-50'}
          </div>
          <div className="text-sm text-gray-400">Expected Weekly Opportunities</div>
        </div>

        <div className="bg-gray-800/50 border border-gray-700 rounded-lg p-5">
          <div className="text-green-400 text-2xl font-black mb-2">
            {stats?.expected_annual_revenue || '$300K-$500K'}
          </div>
          <div className="text-sm text-gray-400">Expected Annual Revenue</div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-2 gap-4">
        <button
          onClick={() => setActiveTab('quick-start')}
          className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 rounded-lg p-6 text-left transition"
        >
          <div className="text-3xl mb-2">🚀</div>
          <div className="text-xl font-black text-white mb-1">Quick Start Guide</div>
          <div className="text-sm text-blue-100">Find 25-40 opportunities in 30 minutes</div>
        </button>

        <button
          onClick={() => setActiveTab('searches')}
          className="bg-gradient-to-r from-green-600 to-teal-600 hover:from-green-700 hover:to-teal-700 rounded-lg p-6 text-left transition"
        >
          <div className="text-3xl mb-2">🔍</div>
          <div className="text-xl font-black text-white mb-1">Browse Search Strings</div>
          <div className="text-sm text-green-100">35+ ready-to-use SAM.gov searches</div>
        </button>
      </div>
    </div>
  );

  const renderQuickStart = () => (
    <div className="space-y-6">
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl p-6 text-white">
        <h2 className="text-2xl font-black mb-2">🚀 Quick Start Guide</h2>
        <p className="text-blue-100">Run these 5 searches right now to find 25-40 opportunities</p>
      </div>

      <div className="bg-yellow-900/20 border-2 border-yellow-500 rounded-lg p-4">
        <div className="flex items-start gap-3">
          <div className="text-2xl">💡</div>
          <div>
            <div className="font-bold text-yellow-400 mb-1">TIME REQUIRED: 30 minutes</div>
            <div className="text-sm text-gray-300">Expected result: 25-40 new transportation/logistics opportunities</div>
          </div>
        </div>
      </div>

      <div className="space-y-4">
        {[
          {
            priority: 1,
            search: '"postal supplies" WOSB',
            category: '📬 Courier & Postal',
            why: 'USPS has 31,000+ facilities - massive opportunity!',
            expected: '10-15 opportunities'
          },
          {
            priority: 2,
            search: '"airport supplies" WOSB',
            category: '✈️ Airport & Aviation',
            why: 'Large contracts, recurring revenue',
            expected: '5-8 opportunities'
          },
          {
            priority: 3,
            search: '"marine supplies" WOSB Michigan',
            category: '🚢 Port & Marine',
            why: 'Local advantage with Detroit Port Authority',
            expected: '3-5 opportunities'
          },
          {
            priority: 4,
            search: '"courier supplies" small business',
            category: '📬 Courier & Postal',
            why: 'Easy to source, quick wins',
            expected: '5-7 opportunities'
          },
          {
            priority: 5,
            search: '"cargo handling equipment" WOSB',
            category: '📦 Cargo & Freight',
            why: 'Federal warehouses, good contract values',
            expected: '4-6 opportunities'
          }
        ].map((item) => (
          <div key={item.priority} className="bg-gray-800/50 border border-gray-700 rounded-lg p-5">
            <div className="flex items-start justify-between mb-3">
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  <div className="bg-blue-600 w-8 h-8 rounded-full flex items-center justify-center font-black">
                    {item.priority}
                  </div>
                  <div className="text-lg font-black text-white">{item.category}</div>
                </div>
                
                <code className="block bg-gray-900/70 px-4 py-3 rounded text-green-400 mb-3 font-mono text-sm">
                  {item.search}
                </code>

                <div className="text-sm text-gray-300 mb-2">
                  <strong className="text-yellow-400">Why:</strong> {item.why}
                </div>
                <div className="text-sm text-gray-400">
                  <strong>Expected:</strong> {item.expected}
                </div>
              </div>

              <button
                onClick={() => copyToClipboard(item.search)}
                className="ml-4 px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded font-bold transition whitespace-nowrap"
              >
                {copiedText === item.search ? '✓ Copied!' : 'Copy Search'}
              </button>
            </div>
          </div>
        ))}
      </div>

      <div className="bg-green-900/20 border-2 border-green-500 rounded-lg p-6">
        <h3 className="text-xl font-black text-green-400 mb-3">🎯 NEXT STEPS</h3>
        <ol className="space-y-2 text-sm text-gray-300">
          <li>1. Copy each search string above</li>
          <li>2. Go to <a href="https://sam.gov" target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:underline">SAM.gov</a></li>
          <li>3. Paste into search box and hit Enter</li>
          <li>4. Download 3-5 promising opportunities per search</li>
          <li>5. Review tonight and select 2-3 to pursue</li>
        </ol>
      </div>
    </div>
  );

  const renderCategories = () => (
    <div className="space-y-6">
      <div className="bg-gradient-to-r from-purple-600 to-pink-600 rounded-xl p-6 text-white">
        <h2 className="text-2xl font-black mb-2">📚 Transportation & Logistics Categories</h2>
        <p className="text-purple-100">5 major categories with 100+ keywords</p>
      </div>

      <div className="grid gap-6">
        {Object.entries(categories).map(([key, category]) => (
          <div key={key} className="bg-gray-800/50 border border-gray-700 rounded-lg p-6">
            <div className="flex items-start justify-between mb-4">
              <div className="flex-1">
                <h3 className="text-2xl font-black text-white mb-2">{category.display_name}</h3>
                <p className="text-gray-300 mb-4">{category.description}</p>

                {category.special_note && (
                  <div className="bg-yellow-900/20 border border-yellow-500/30 rounded-lg p-3 mb-4">
                    <div className="text-sm text-yellow-400 font-bold">💡 {category.special_note}</div>
                  </div>
                )}

                <div className="grid grid-cols-2 gap-4 mb-4">
                  <div>
                    <div className="text-xs font-bold text-gray-400 mb-1">CONTRACT RANGE:</div>
                    <div className="text-green-400 font-bold">{category.estimated_contract_range}</div>
                  </div>
                  <div>
                    <div className="text-xs font-bold text-gray-400 mb-1">DURATION:</div>
                    <div className="text-blue-400 font-bold">{category.typical_duration}</div>
                  </div>
                  <div>
                    <div className="text-xs font-bold text-gray-400 mb-1">SOURCING:</div>
                    <div className="text-purple-400 font-bold">{category.sourcing_difficulty}</div>
                  </div>
                  <div>
                    <div className="text-xs font-bold text-gray-400 mb-1">KEYWORDS:</div>
                    <div className="text-yellow-400 font-bold">
                      {category.primary_keywords.length + category.secondary_keywords.length}
                    </div>
                  </div>
                </div>

                <div className="mb-4">
                  <div className="text-xs font-bold text-gray-400 mb-2">KEY SUPPLIERS:</div>
                  <div className="flex flex-wrap gap-2">
                    {category.key_suppliers.map((supplier, idx) => (
                      <span key={idx} className="bg-blue-900/30 px-3 py-1 rounded-full text-sm text-blue-300">
                        {supplier}
                      </span>
                    ))}
                  </div>
                </div>

                <div>
                  <div className="text-xs font-bold text-gray-400 mb-2">SAM.GOV SEARCHES ({category.sam_gov_searches.length}):</div>
                  <div className="space-y-2">
                    {category.sam_gov_searches.slice(0, 3).map((search, idx) => (
                      <div key={idx} className="flex items-center gap-2">
                        <code className="flex-1 bg-gray-900/50 px-3 py-2 rounded text-green-300 text-sm">
                          {search}
                        </code>
                        <button
                          onClick={() => copyToClipboard(search)}
                          className="px-3 py-2 bg-blue-600 hover:bg-blue-700 rounded text-sm font-bold transition"
                        >
                          Copy
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const renderRevenue = () => (
    <div className="space-y-6">
      <div className="bg-gradient-to-r from-green-600 to-emerald-600 rounded-xl p-6 text-white">
        <h2 className="text-2xl font-black mb-2">💰 Revenue Potential</h2>
        <p className="text-green-100">Expected revenue by category and timeline</p>
      </div>

      <div className="bg-gradient-to-br from-yellow-900/30 to-yellow-800/20 border-2 border-yellow-500 rounded-xl p-6">
        <h3 className="text-2xl font-black text-yellow-400 mb-4">💎 TOTAL POTENTIAL</h3>
        <div className="grid grid-cols-3 gap-4">
          <div className="bg-black/30 rounded-lg p-4">
            <div className="text-sm text-gray-400 mb-1">Monthly (Near Term)</div>
            <div className="text-3xl font-black text-green-400">$10K-$30K</div>
          </div>
          <div className="bg-black/30 rounded-lg p-4">
            <div className="text-sm text-gray-400 mb-1">Transportation/Logistics Annual</div>
            <div className="text-3xl font-black text-green-400">$300K-$500K</div>
          </div>
          <div className="bg-black/30 rounded-lg p-4">
            <div className="text-sm text-gray-400 mb-1">Combined with Traditional</div>
            <div className="text-3xl font-black text-green-400">$660K-$980K</div>
          </div>
        </div>
      </div>

      <div className="grid gap-4">
        {Object.entries(categories).map(([key, category]) => (
          <div key={key} className="bg-gray-800/50 border border-gray-700 rounded-lg p-5">
            <div className="flex items-center justify-between mb-4">
              <div className="text-xl font-black text-white">{category.display_name}</div>
              <div className="text-2xl font-black text-green-400">{category.estimated_contract_range}</div>
            </div>
            <div className="grid grid-cols-3 gap-3 text-sm">
              <div>
                <div className="text-gray-400 mb-1">Small Contracts</div>
                <div className="text-white font-bold">$20K-$100K</div>
              </div>
              <div>
                <div className="text-gray-400 mb-1">Medium Contracts</div>
                <div className="text-white font-bold">$100K-$250K</div>
              </div>
              <div>
                <div className="text-gray-400 mb-1">Large Contracts</div>
                <div className="text-white font-bold">$250K-$500K+</div>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="bg-blue-900/20 border border-blue-500/30 rounded-lg p-6">
        <h3 className="text-xl font-black text-blue-400 mb-3">📈 TIMELINE TO REVENUE</h3>
        <div className="space-y-3 text-sm">
          <div className="flex justify-between items-center">
            <span className="text-gray-300"><strong>Months 1-3:</strong> Win 2-3 contracts</span>
            <span className="text-green-400 font-bold">$10K-$15K/month</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-gray-300"><strong>Months 4-6:</strong> Scale up</span>
            <span className="text-green-400 font-bold">$20K-$30K/month</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-gray-300"><strong>Months 7-12:</strong> Big game contracts</span>
            <span className="text-green-400 font-bold">$40K-$60K/month</span>
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 border-b border-gray-700 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <button
                onClick={onBackToNexus}
                className="text-white hover:text-gray-300 transition"
              >
                ← Back to NEXUS
              </button>
              <div className="w-px h-6 bg-white/20" />
              <h1 className="text-2xl font-black text-white">
                ✈️🚢 Transportation & Logistics
              </h1>
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="bg-gray-800/50 border-b border-gray-700 sticky top-[72px] z-10">
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex gap-1 overflow-x-auto">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-6 py-4 font-bold whitespace-nowrap transition ${
                  activeTab === tab.id
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-400 hover:text-white hover:bg-gray-700/50'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-6 py-8">
        {loading ? (
          <div className="flex items-center justify-center py-20">
            <div className="text-white text-xl">Loading...</div>
          </div>
        ) : (
          <>
            {activeTab === 'dashboard' && renderDashboard()}
            {activeTab === 'quick-start' && renderQuickStart()}
            {activeTab === 'categories' && renderCategories()}
            {activeTab === 'revenue' && renderRevenue()}
            {activeTab === 'searches' && (
              <div className="text-white">Search strings coming soon...</div>
            )}
            {activeTab === 'sources' && (
              <div className="text-white">Direct sources coming soon...</div>
            )}
          </>
        )}
      </div>

      {/* Copied notification */}
      {copiedText && (
        <div className="fixed bottom-4 right-4 bg-green-600 text-white px-6 py-3 rounded-lg shadow-xl font-bold animate-bounce">
          ✓ Copied to clipboard!
        </div>
      )}
    </div>
  );
};

export default TransportationLogisticsSystem;
