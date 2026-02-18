import React, { useState } from 'react';
import { FileText, TrendingUp, AlertCircle, CheckCircle, XCircle, Zap } from 'lucide-react';

interface BiohackScore {
  biohack_number: number;
  biohack_name: string;
  score: number;
  max_score: number;
  weight: number;
  weighted_score: number;
  issues: string[];
  recommendations: string[];
}

interface ProposalBioResult {
  composite_score: number;
  gate_status: string;
  biohacks: BiohackScore[];
  critical_issues: string[];
  strengths: string[];
  overall_assessment: string;
}

export function ProposalBioAnalyzer() {
  const [proposalText, setProposalText] = useState('');
  const [metadata, setMetadata] = useState({
    client_name: '',
    agency: '',
    agency_type: 'Federal',
    region: 'Midwest',
    rfp_number: '',
    service_type: ''
  });
  const [result, setResult] = useState<ProposalBioResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const analyzeProposal = async () => {
    if (!proposalText.trim()) {
      setError('Please enter proposal text');
      return;
    }

    setLoading(true);
    setError('');
    setResult(null);

    try {
      const response = await fetch('http://localhost:5000/api/proposalbio/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          proposal_text: proposalText,
          metadata: metadata
        })
      });

      const data = await response.json();
      if (data.success) {
        setResult(data.result);
      } else {
        setError(data.error || 'Analysis failed');
      }
    } catch (err) {
      setError('Network error: ' + (err as Error).message);
    } finally {
      setLoading(false);
    }
  };

  const getBiohackColor = (score: number, maxScore: number) => {
    const percentage = (score / maxScore) * 100;
    if (percentage >= 80) return 'text-green-400';
    if (percentage >= 60) return 'text-yellow-400';
    return 'text-red-400';
  };

  const getGateColor = (status: string) => {
    if (status === 'UNLOCKED') return 'bg-green-900/40 border-green-700';
    if (status === 'WARNING') return 'bg-yellow-900/40 border-yellow-700';
    return 'bg-red-900/40 border-red-700';
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 to-pink-600 rounded-lg p-6">
        <h2 className="text-2xl font-bold text-white mb-2">ProposalBio™ Analyzer</h2>
        <p className="text-purple-100">10 Biohack Quality Assurance System for Government Proposals</p>
      </div>

      {/* Input Section */}
      <div className="grid grid-cols-3 gap-6">
        {/* Proposal Text */}
        <div className="col-span-2 bg-gray-800 rounded-lg p-6">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <FileText className="w-5 h-5 text-purple-400" />
            Proposal Text
          </h3>
          <textarea
            value={proposalText}
            onChange={(e) => setProposalText(e.target.value)}
            placeholder="Paste your proposal text here..."
            className="w-full h-96 px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-purple-500 font-mono text-sm"
          />
          <div className="mt-2 text-sm text-gray-400">
            {proposalText.length} characters • {proposalText.split(/\s+/).filter(w => w).length} words
          </div>
        </div>

        {/* Metadata */}
        <div className="bg-gray-800 rounded-lg p-6">
          <h3 className="text-lg font-semibold mb-4">Metadata</h3>
          <div className="space-y-3">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">Client Name</label>
              <input
                type="text"
                value={metadata.client_name}
                onChange={(e) => setMetadata({ ...metadata, client_name: e.target.value })}
                placeholder="e.g., DTMB"
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white text-sm focus:ring-2 focus:ring-purple-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">Agency</label>
              <input
                type="text"
                value={metadata.agency}
                onChange={(e) => setMetadata({ ...metadata, agency: e.target.value })}
                placeholder="e.g., Michigan DTMB"
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white text-sm focus:ring-2 focus:ring-purple-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">Agency Type</label>
              <select
                value={metadata.agency_type}
                onChange={(e) => setMetadata({ ...metadata, agency_type: e.target.value })}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white text-sm focus:ring-2 focus:ring-purple-500"
              >
                <option value="Federal">Federal</option>
                <option value="State">State</option>
                <option value="Local">Local</option>
                <option value="Cooperative">Cooperative</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">Region</label>
              <select
                value={metadata.region}
                onChange={(e) => setMetadata({ ...metadata, region: e.target.value })}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white text-sm focus:ring-2 focus:ring-purple-500"
              >
                <option value="Midwest">Midwest</option>
                <option value="Northeast">Northeast</option>
                <option value="Southeast">Southeast</option>
                <option value="Southwest">Southwest</option>
                <option value="West_Coast">West Coast</option>
                <option value="Mid_Atlantic">Mid-Atlantic</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">RFP Number</label>
              <input
                type="text"
                value={metadata.rfp_number}
                onChange={(e) => setMetadata({ ...metadata, rfp_number: e.target.value })}
                placeholder="e.g., RFP-171"
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white text-sm focus:ring-2 focus:ring-purple-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">Service Type</label>
              <input
                type="text"
                value={metadata.service_type}
                onChange={(e) => setMetadata({ ...metadata, service_type: e.target.value })}
                placeholder="e.g., Drug Testing"
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white text-sm focus:ring-2 focus:ring-purple-500"
              />
            </div>
          </div>

          <button
            onClick={analyzeProposal}
            disabled={loading || !proposalText.trim()}
            className="w-full mt-6 flex items-center justify-center gap-2 px-6 py-3 bg-purple-600 hover:bg-purple-700 disabled:bg-gray-600 disabled:cursor-not-allowed rounded-lg font-medium transition"
          >
            <Zap className="w-5 h-5" />
            {loading ? 'Analyzing...' : 'Analyze Proposal'}
          </button>
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
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-gray-600 border-t-purple-500 mb-4"></div>
          <p className="text-gray-400">Analyzing proposal with 10 ProposalBio™ biohacks...</p>
        </div>
      )}

      {/* Results */}
      {result && !loading && (
        <div className="space-y-6">
          {/* Overall Score */}
          <div className={`rounded-lg p-6 border-2 ${getGateColor(result.gate_status)}`}>
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-2xl font-bold text-white mb-1">ProposalBio™ Score</h3>
                <p className="text-gray-400">{result.overall_assessment}</p>
              </div>
              <div className="text-right">
                <div className="text-5xl font-black text-white">{Math.round(result.composite_score)}</div>
                <div className="text-gray-400 text-sm">/ 100</div>
              </div>
            </div>
            
            <div className={`inline-flex items-center gap-2 px-4 py-2 rounded-full font-bold ${
              result.gate_status === 'UNLOCKED' 
                ? 'bg-green-600 text-white' 
                : result.gate_status === 'WARNING'
                ? 'bg-yellow-600 text-white'
                : 'bg-red-600 text-white'
            }`}>
              {result.gate_status === 'UNLOCKED' ? <CheckCircle className="w-5 h-5" /> : <XCircle className="w-5 h-5" />}
              {result.gate_status === 'UNLOCKED' ? 'READY TO SUBMIT' : result.gate_status === 'WARNING' ? 'NEEDS REVIEW' : 'NEEDS IMPROVEMENT'}
            </div>
          </div>

          {/* Critical Issues */}
          {result.critical_issues && result.critical_issues.length > 0 && (
            <div className="bg-red-900/20 border border-red-700 rounded-lg p-6">
              <h3 className="text-lg font-bold text-red-400 mb-4 flex items-center gap-2">
                <AlertCircle className="w-5 h-5" />
                Critical Issues to Fix
              </h3>
              <ul className="space-y-2">
                {result.critical_issues.map((issue, idx) => (
                  <li key={idx} className="flex items-start gap-2 text-red-300">
                    <span className="text-red-400 font-bold">•</span>
                    <span>{issue}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Strengths */}
          {result.strengths && result.strengths.length > 0 && (
            <div className="bg-green-900/20 border border-green-700 rounded-lg p-6">
              <h3 className="text-lg font-bold text-green-400 mb-4 flex items-center gap-2">
                <CheckCircle className="w-5 h-5" />
                Strengths
              </h3>
              <ul className="space-y-2">
                {result.strengths.map((strength, idx) => (
                  <li key={idx} className="flex items-start gap-2 text-green-300">
                    <span className="text-green-400 font-bold">✓</span>
                    <span>{strength}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Biohack Breakdown */}
          <div className="bg-gray-800 rounded-lg p-6">
            <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-purple-400" />
              10 Biohack Breakdown
            </h3>
            <div className="space-y-4">
              {result.biohacks.map((biohack) => (
                <div key={biohack.biohack_number} className="bg-gray-700/50 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-3">
                    <div>
                      <h4 className="font-bold text-white">
                        #{biohack.biohack_number} {biohack.biohack_name}
                      </h4>
                      <p className="text-sm text-gray-400">Weight: {(biohack.weight * 100).toFixed(0)}%</p>
                    </div>
                    <div className="text-right">
                      <div className={`text-2xl font-bold ${getBiohackColor(biohack.score, biohack.max_score)}`}>
                        {biohack.score.toFixed(1)}
                      </div>
                      <div className="text-xs text-gray-400">/ {biohack.max_score}</div>
                    </div>
                  </div>

                  {/* Progress Bar */}
                  <div className="w-full bg-gray-600 rounded-full h-2 mb-3">
                    <div
                      className={`h-2 rounded-full ${
                        (biohack.score / biohack.max_score) >= 0.8 ? 'bg-green-500' :
                        (biohack.score / biohack.max_score) >= 0.6 ? 'bg-yellow-500' :
                        'bg-red-500'
                      }`}
                      style={{ width: `${(biohack.score / biohack.max_score) * 100}%` }}
                    ></div>
                  </div>

                  {/* Issues */}
                  {biohack.issues && biohack.issues.length > 0 && (
                    <div className="mb-2">
                      <p className="text-xs font-semibold text-red-400 mb-1">Issues:</p>
                      <ul className="space-y-1">
                        {biohack.issues.map((issue, idx) => (
                          <li key={idx} className="text-xs text-red-300 flex items-start gap-1">
                            <span>•</span>
                            <span>{issue}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Recommendations */}
                  {biohack.recommendations && biohack.recommendations.length > 0 && (
                    <div>
                      <p className="text-xs font-semibold text-blue-400 mb-1">Recommendations:</p>
                      <ul className="space-y-1">
                        {biohack.recommendations.map((rec, idx) => (
                          <li key={idx} className="text-xs text-blue-300 flex items-start gap-1">
                            <span>→</span>
                            <span>{rec}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
