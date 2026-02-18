import React, { useState } from 'react';
import { Search, DollarSign, FileText, TrendingUp, AlertCircle } from 'lucide-react';

interface Contract {
  recipient: string;
  amount: number;
  agency: string;
  description: string;
  start_date: string;
  end_date: string;
  award_id: string;
}

interface MarketIntelligence {
  service_type: string;
  contracts_found: number;
  market_benchmarks: {
    average_per_unit: number;
    min_per_unit: number;
    max_per_unit: number;
    sample_size: number;
  };
  top_contracts: Array<{
    contractor: string;
    total_value: number;
    estimated_per_unit: number;
  }>;
  recommendation: string;
}

export function HistoricalPricing() {
  const [searchParams, setSearchParams] = useState({
    service_type: '',
    naics_code: '',
    psc_code: '',
    min_value: '',
    max_value: '',
    estimated_annual_volume: '1000',
    years_back: '3'
  });

  const [searchResults, setSearchResults] = useState<Contract[]>([]);
  const [marketIntel, setMarketIntel] = useState<MarketIntelligence | null>(null);
  const [foiaRequest, setFoiaRequest] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState<'search' | 'intel' | 'foia'>('intel');

  const handleMarketIntelligence = async () => {
    setLoading(true);
    setError('');
    setMarketIntel(null);

    try {
      const response = await fetch('http://localhost:5000/api/pricing/market-intelligence', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          service_type: searchParams.service_type,
          naics_code: searchParams.naics_code || undefined,
          estimated_annual_volume: parseInt(searchParams.estimated_annual_volume),
          min_value: searchParams.min_value ? parseFloat(searchParams.min_value) : undefined,
          max_value: searchParams.max_value ? parseFloat(searchParams.max_value) : undefined
        })
      });

      const data = await response.json();
      if (data.success) {
        setMarketIntel(data);
      } else {
        setError(data.error || 'Failed to fetch market intelligence');
      }
    } catch (err) {
      setError('Network error: ' + (err as Error).message);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async () => {
    setLoading(true);
    setError('');
    setSearchResults([]);

    try {
      const response = await fetch('http://localhost:5000/api/pricing/search-historical', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          service_type: searchParams.service_type,
          naics_code: searchParams.naics_code || undefined,
          psc_code: searchParams.psc_code || undefined,
          min_value: searchParams.min_value ? parseFloat(searchParams.min_value) : undefined,
          max_value: searchParams.max_value ? parseFloat(searchParams.max_value) : undefined,
          years_back: parseInt(searchParams.years_back)
        })
      });

      const data = await response.json();
      if (data.success) {
        setSearchResults(data.contracts);
      } else {
        setError(data.error || 'Failed to search contracts');
      }
    } catch (err) {
      setError('Network error: ' + (err as Error).message);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateFOIA = async () => {
    setLoading(true);
    setError('');
    setFoiaRequest('');

    const solicitation = prompt('Enter solicitation number:');
    const agency = prompt('Enter agency name:');
    const title = prompt('Enter contract title:');

    if (!solicitation || !agency || !title) {
      setError('All fields required for FOIA generation');
      setLoading(false);
      return;
    }

    try {
      const response = await fetch('http://localhost:5000/api/pricing/generate-foia', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          solicitation_number: solicitation,
          agency_name: agency,
          contract_title: title
        })
      });

      const data = await response.json();
      if (data.success) {
        setFoiaRequest(data.foia_request);
        setActiveTab('foia');
      } else {
        setError(data.error || 'Failed to generate FOIA');
      }
    } catch (err) {
      setError('Network error: ' + (err as Error).message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-green-600 to-emerald-600 rounded-lg p-6">
        <h2 className="text-2xl font-bold text-white mb-2">Historical Pricing Intelligence</h2>
        <p className="text-green-100">Find pricing from previous government contracts to validate your bids</p>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b border-gray-700">
        <button
          onClick={() => setActiveTab('intel')}
          className={`px-4 py-2 font-medium transition ${
            activeTab === 'intel'
              ? 'text-green-400 border-b-2 border-green-400'
              : 'text-gray-400 hover:text-gray-300'
          }`}
        >
          <TrendingUp className="inline w-4 h-4 mr-2" />
          Market Intelligence
        </button>
        <button
          onClick={() => setActiveTab('search')}
          className={`px-4 py-2 font-medium transition ${
            activeTab === 'search'
              ? 'text-green-400 border-b-2 border-green-400'
              : 'text-gray-400 hover:text-gray-300'
          }`}
        >
          <Search className="inline w-4 h-4 mr-2" />
          Contract Search
        </button>
        <button
          onClick={() => setActiveTab('foia')}
          className={`px-4 py-2 font-medium transition ${
            activeTab === 'foia'
              ? 'text-green-400 border-b-2 border-green-400'
              : 'text-gray-400 hover:text-gray-300'
          }`}
        >
          <FileText className="inline w-4 h-4 mr-2" />
          FOIA Generator
        </button>
      </div>

      {/* Search Form */}
      <div className="bg-gray-800 rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4">Search Parameters</h3>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Service Type *
            </label>
            <input
              type="text"
              value={searchParams.service_type}
              onChange={(e) => setSearchParams({ ...searchParams, service_type: e.target.value })}
              placeholder="e.g., medical courier"
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-green-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              NAICS Code
            </label>
            <input
              type="text"
              value={searchParams.naics_code}
              onChange={(e) => setSearchParams({ ...searchParams, naics_code: e.target.value })}
              placeholder="e.g., 492110"
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-green-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Min Value ($)
            </label>
            <input
              type="number"
              value={searchParams.min_value}
              onChange={(e) => setSearchParams({ ...searchParams, min_value: e.target.value })}
              placeholder="50000"
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-green-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Max Value ($)
            </label>
            <input
              type="number"
              value={searchParams.max_value}
              onChange={(e) => setSearchParams({ ...searchParams, max_value: e.target.value })}
              placeholder="150000"
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-green-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Estimated Annual Volume
            </label>
            <input
              type="number"
              value={searchParams.estimated_annual_volume}
              onChange={(e) => setSearchParams({ ...searchParams, estimated_annual_volume: e.target.value })}
              placeholder="1000"
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-green-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Years Back
            </label>
            <input
              type="number"
              value={searchParams.years_back}
              onChange={(e) => setSearchParams({ ...searchParams, years_back: e.target.value })}
              placeholder="3"
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-green-500"
            />
          </div>
        </div>

        <div className="flex gap-3 mt-6">
          {activeTab === 'intel' && (
            <button
              onClick={handleMarketIntelligence}
              disabled={loading || !searchParams.service_type}
              className="flex items-center gap-2 px-6 py-3 bg-green-600 hover:bg-green-700 disabled:bg-gray-600 disabled:cursor-not-allowed rounded-lg font-medium transition"
            >
              <TrendingUp className="w-5 h-5" />
              Get Market Intelligence
            </button>
          )}
          {activeTab === 'search' && (
            <button
              onClick={handleSearch}
              disabled={loading || !searchParams.service_type}
              className="flex items-center gap-2 px-6 py-3 bg-green-600 hover:bg-green-700 disabled:bg-gray-600 disabled:cursor-not-allowed rounded-lg font-medium transition"
            >
              <Search className="w-5 h-5" />
              Search Contracts
            </button>
          )}
          {activeTab === 'foia' && (
            <button
              onClick={handleGenerateFOIA}
              disabled={loading}
              className="flex items-center gap-2 px-6 py-3 bg-green-600 hover:bg-green-700 disabled:bg-gray-600 disabled:cursor-not-allowed rounded-lg font-medium transition"
            >
              <FileText className="w-5 h-5" />
              Generate FOIA Request
            </button>
          )}
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="bg-red-900/20 border border-red-700 rounded-lg p-4 flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
          <div>
            <p className="font-medium text-red-400">Error</p>
            <p className="text-red-300 text-sm mt-1">{error}</p>
          </div>
        </div>
      )}

      {/* Loading */}
      {loading && (
        <div className="bg-gray-800 rounded-lg p-8 text-center">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-gray-600 border-t-green-500 mb-4"></div>
          <p className="text-gray-400">Searching USASpending.gov...</p>
        </div>
      )}

      {/* Market Intelligence Results */}
      {activeTab === 'intel' && marketIntel && !loading && (
        <div className="space-y-4">
          <div className="bg-gradient-to-r from-green-900/40 to-emerald-900/40 border border-green-700 rounded-lg p-6">
            <h3 className="text-xl font-bold text-green-400 mb-4">Market Benchmarks</h3>
            <div className="grid grid-cols-4 gap-4">
              <div className="bg-gray-800/50 rounded-lg p-4">
                <p className="text-sm text-gray-400 mb-1">Contracts Found</p>
                <p className="text-2xl font-bold text-white">{marketIntel.contracts_found}</p>
              </div>
              <div className="bg-gray-800/50 rounded-lg p-4">
                <p className="text-sm text-gray-400 mb-1">Average Per Unit</p>
                <p className="text-2xl font-bold text-green-400">${marketIntel.market_benchmarks.average_per_unit.toFixed(2)}</p>
              </div>
              <div className="bg-gray-800/50 rounded-lg p-4">
                <p className="text-sm text-gray-400 mb-1">Min Per Unit</p>
                <p className="text-2xl font-bold text-blue-400">${marketIntel.market_benchmarks.min_per_unit.toFixed(2)}</p>
              </div>
              <div className="bg-gray-800/50 rounded-lg p-4">
                <p className="text-sm text-gray-400 mb-1">Max Per Unit</p>
                <p className="text-2xl font-bold text-orange-400">${marketIntel.market_benchmarks.max_per_unit.toFixed(2)}</p>
              </div>
            </div>
            <div className="mt-4 p-4 bg-green-900/20 border border-green-700 rounded-lg">
              <p className="text-green-300 font-medium">💡 {marketIntel.recommendation}</p>
            </div>
          </div>

          <div className="bg-gray-800 rounded-lg p-6">
            <h3 className="text-lg font-semibold mb-4">Top Contracts</h3>
            <div className="space-y-3">
              {marketIntel.top_contracts.map((contract, idx) => (
                <div key={idx} className="bg-gray-700/50 rounded-lg p-4 flex items-center justify-between">
                  <div>
                    <p className="font-medium text-white">{contract.contractor}</p>
                    <p className="text-sm text-gray-400">Total: ${contract.total_value.toLocaleString()}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-lg font-bold text-green-400">${contract.estimated_per_unit.toFixed(2)}</p>
                    <p className="text-xs text-gray-400">per unit</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Contract Search Results */}
      {activeTab === 'search' && searchResults.length > 0 && !loading && (
        <div className="bg-gray-800 rounded-lg p-6">
          <h3 className="text-lg font-semibold mb-4">Found {searchResults.length} Contracts</h3>
          <div className="space-y-3">
            {searchResults.slice(0, 20).map((contract, idx) => (
              <div key={idx} className="bg-gray-700/50 rounded-lg p-4">
                <div className="flex items-start justify-between mb-2">
                  <div className="flex-1">
                    <p className="font-medium text-white">{contract.recipient}</p>
                    <p className="text-sm text-gray-400">{contract.agency || 'Unknown Agency'}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-lg font-bold text-green-400">${contract.amount.toLocaleString()}</p>
                    <p className="text-xs text-gray-400">{contract.start_date} to {contract.end_date}</p>
                  </div>
                </div>
                {contract.description && contract.description !== 'No description' && (
                  <p className="text-sm text-gray-400 mt-2">{contract.description}</p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* FOIA Request */}
      {activeTab === 'foia' && foiaRequest && !loading && (
        <div className="bg-gray-800 rounded-lg p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">FOIA Request Letter</h3>
            <button
              onClick={() => {
                navigator.clipboard.writeText(foiaRequest);
                alert('Copied to clipboard!');
              }}
              className="px-4 py-2 bg-green-600 hover:bg-green-700 rounded-lg text-sm font-medium transition"
            >
              Copy to Clipboard
            </button>
          </div>
          <pre className="bg-gray-900 rounded-lg p-4 text-sm text-gray-300 whitespace-pre-wrap overflow-x-auto">
            {foiaRequest}
          </pre>
        </div>
      )}
    </div>
  );
}
