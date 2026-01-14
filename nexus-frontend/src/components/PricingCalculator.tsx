import React, { useState } from 'react';
import { api } from '../api/client';

interface PricingCalculatorProps {
  opportunityId: string;
  opportunityTitle: string;
  estimatedValue: number;
  onClose: () => void;
  onSelectPrice: (price: number, strategy: string) => void;
}

interface PricingScenario {
  name: string;
  price: number;
  margin: number;
  win_probability: number;
  risk: string;
  description: string;
  profit: number;
}

interface PricingRecommendation {
  recommended_price: number;
  price_range: {
    minimum: number;
    competitive: number;
    optimal: number;
    maximum: number;
  };
  scenarios: PricingScenario[];
  win_probability: number;
  pricing_strategy: string;
  cost_breakdown: {
    labor: number;
    materials: number;
    other: number;
    subtotal: number;
    overhead_rate: number;
    overhead_amount: number;
    total_cost: number;
  };
  market_position: string;
  justification: string;
  risk_assessment: string;
  recommendations: string[];
}

const PricingCalculator: React.FC<PricingCalculatorProps> = ({
  opportunityId,
  opportunityTitle,
  estimatedValue,
  onClose,
  onSelectPrice
}) => {
  const [loading, setLoading] = useState(false);
  const [pricing, setPricing] = useState<PricingRecommendation | null>(null);
  const [selectedScenario, setSelectedScenario] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);

  const calculatePricing = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await api.calculateIntelligentPricing(opportunityId);
      
      if (result.error) {
        setError(result.error);
      } else {
        setPricing(result);
        // Auto-select recommended scenario (index 1)
        setSelectedScenario(1);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to calculate pricing');
    } finally {
      setLoading(false);
    }
  };

  const handleSelectPrice = () => {
    if (pricing && selectedScenario !== null) {
      const scenario = pricing.scenarios[selectedScenario];
      onSelectPrice(scenario.price, scenario.name);
      onClose();
    }
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  const getRiskColor = (risk: string) => {
    switch (risk.toLowerCase()) {
      case 'low': return 'text-green-400 bg-green-500/20';
      case 'medium': return 'text-yellow-400 bg-yellow-500/20';
      case 'high': return 'text-red-400 bg-red-500/20';
      default: return 'text-gray-400 bg-gray-500/20';
    }
  };

  return (
    <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-6 overflow-y-auto">
      <div className="bg-gray-800 rounded-xl max-w-7xl w-full max-h-[90vh] overflow-y-auto border border-gray-700">
        {/* Header */}
        <div className="bg-gradient-to-r from-green-600 to-blue-600 p-6 sticky top-0 z-10">
          <div className="flex items-start justify-between">
            <div>
              <h2 className="text-2xl font-bold mb-2">🧠 Intelligent Pricing Calculator</h2>
              <p className="text-white/80">{opportunityTitle}</p>
              <p className="text-sm text-white/60 mt-1">Estimated Value: {formatCurrency(estimatedValue)}</p>
            </div>
            <button 
              onClick={onClose}
              className="text-white hover:text-gray-300 text-3xl font-bold"
            >
              ×
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="p-6">
          {!pricing && !loading && (
            <div className="text-center py-12">
              <div className="text-6xl mb-4">💰</div>
              <h3 className="text-xl font-bold mb-4">AI-Powered Pricing Analysis</h3>
              <p className="text-gray-400 mb-6 max-w-2xl mx-auto">
                Our intelligent pricing engine analyzes historical win/loss data, market rates, 
                cost structures, and competition to recommend optimal pricing strategies.
              </p>
              <button 
                onClick={calculatePricing}
                className="bg-green-600 hover:bg-green-700 px-8 py-4 rounded-lg font-bold text-lg transition"
              >
                🚀 Calculate Intelligent Pricing
              </button>
            </div>
          )}

          {loading && (
            <div className="text-center py-12">
              <div className="text-6xl mb-4 animate-pulse">🤖</div>
              <h3 className="text-xl font-bold mb-2">Analyzing Opportunity...</h3>
              <p className="text-gray-400">
                Reviewing historical data, market intelligence, and cost structures...
              </p>
            </div>
          )}

          {error && (
            <div className="bg-red-900/30 border border-red-600 rounded-xl p-6 text-center">
              <p className="text-red-400 font-semibold">❌ {error}</p>
              <button 
                onClick={calculatePricing}
                className="mt-4 bg-red-600 hover:bg-red-700 px-6 py-2 rounded-lg font-semibold transition"
              >
                Try Again
              </button>
            </div>
          )}

          {pricing && (
            <div className="space-y-6">
              {/* AI Recommendation Banner */}
              <div className="bg-gradient-to-r from-blue-900/50 to-purple-900/50 border border-blue-600 rounded-xl p-6">
                <div className="flex items-start gap-4">
                  <div className="text-5xl">🎯</div>
                  <div className="flex-1">
                    <h3 className="text-2xl font-bold text-blue-400 mb-2">AI Recommendation</h3>
                    <div className="text-4xl font-black text-white mb-3">
                      {formatCurrency(pricing.recommended_price)}
                    </div>
                    <div className="flex gap-4 text-sm mb-3">
                      <span className="text-gray-300">
                        Strategy: <span className="font-bold text-blue-400">{pricing.pricing_strategy}</span>
                      </span>
                      <span className="text-gray-300">•</span>
                      <span className="text-gray-300">
                        Win Probability: <span className="font-bold text-green-400">{pricing.win_probability}%</span>
                      </span>
                      <span className="text-gray-300">•</span>
                      <span className="text-gray-300">
                        Market Position: <span className="font-bold text-purple-400">{pricing.market_position}</span>
                      </span>
                      <span className="text-gray-300">•</span>
                      <span className={`px-2 py-1 rounded font-bold ${getRiskColor(pricing.risk_assessment)}`}>
                        {pricing.risk_assessment} Risk
                      </span>
                    </div>
                    <p className="text-gray-300 text-sm leading-relaxed">{pricing.justification}</p>
                  </div>
                </div>
              </div>

              {/* Pricing Scenarios */}
              <div>
                <h3 className="text-xl font-bold mb-4">📊 Pricing Scenarios</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {pricing.scenarios.map((scenario, index) => (
                    <div 
                      key={index}
                      onClick={() => setSelectedScenario(index)}
                      className={`p-6 rounded-xl border-2 cursor-pointer transition ${
                        selectedScenario === index
                          ? 'border-blue-500 bg-blue-900/30'
                          : 'border-gray-700 bg-gray-700/30 hover:border-gray-600'
                      }`}
                    >
                      <div className="flex items-start justify-between mb-3">
                        <div>
                          <h4 className="font-bold text-lg">{scenario.name}</h4>
                          <p className="text-3xl font-black text-green-400 mt-2">
                            {formatCurrency(scenario.price)}
                          </p>
                        </div>
                        <div className="text-right">
                          <div className="text-sm text-gray-400">Win Probability</div>
                          <div className="text-2xl font-bold text-blue-400">{scenario.win_probability}%</div>
                        </div>
                      </div>
                      
                      <div className="grid grid-cols-2 gap-3 mb-3 text-sm">
                        <div>
                          <span className="text-gray-400">Profit Margin:</span>
                          <span className="ml-2 font-bold text-green-400">{scenario.margin}%</span>
                        </div>
                        <div>
                          <span className="text-gray-400">Profit:</span>
                          <span className="ml-2 font-bold text-green-400">{formatCurrency(scenario.profit)}</span>
                        </div>
                      </div>
                      
                      <div className="mb-3">
                        <span className={`px-3 py-1 rounded-full text-xs font-bold ${getRiskColor(scenario.risk)}`}>
                          {scenario.risk} Risk
                        </span>
                      </div>
                      
                      <p className="text-sm text-gray-400">{scenario.description}</p>
                      
                      {selectedScenario === index && (
                        <div className="mt-3 pt-3 border-t border-blue-500">
                          <div className="text-blue-400 font-semibold text-sm">✓ Selected</div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>

              {/* Cost Breakdown */}
              <div className="bg-gray-700/50 rounded-xl p-6">
                <h3 className="text-xl font-bold mb-4">💵 Cost Breakdown</h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                  <div>
                    <div className="text-sm text-gray-400 mb-1">Labor</div>
                    <div className="text-xl font-bold">{formatCurrency(pricing.cost_breakdown.labor)}</div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-400 mb-1">Materials</div>
                    <div className="text-xl font-bold">{formatCurrency(pricing.cost_breakdown.materials)}</div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-400 mb-1">Other Costs</div>
                    <div className="text-xl font-bold">{formatCurrency(pricing.cost_breakdown.other)}</div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-400 mb-1">Subtotal</div>
                    <div className="text-xl font-bold">{formatCurrency(pricing.cost_breakdown.subtotal)}</div>
                  </div>
                </div>
                <div className="border-t border-gray-600 pt-4 grid grid-cols-2 gap-4">
                  <div>
                    <div className="text-sm text-gray-400 mb-1">
                      Overhead ({pricing.cost_breakdown.overhead_rate}%)
                    </div>
                    <div className="text-xl font-bold">{formatCurrency(pricing.cost_breakdown.overhead_amount)}</div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-400 mb-1">Total Cost</div>
                    <div className="text-2xl font-black text-yellow-400">
                      {formatCurrency(pricing.cost_breakdown.total_cost)}
                    </div>
                  </div>
                </div>
              </div>

              {/* Key Recommendations */}
              <div className="bg-blue-900/30 border border-blue-700 rounded-xl p-6">
                <h3 className="text-xl font-bold text-blue-400 mb-4">💡 Key Recommendations</h3>
                <ul className="space-y-2">
                  {pricing.recommendations.map((rec, index) => (
                    <li key={index} className="flex items-start gap-3">
                      <span className="text-blue-400 font-bold">•</span>
                      <span className="text-gray-300">{rec}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        {pricing && (
          <div className="bg-gray-700 p-6 flex gap-4 justify-end sticky bottom-0">
            <button 
              onClick={onClose}
              className="bg-gray-600 hover:bg-gray-500 px-6 py-3 rounded-lg font-semibold transition"
            >
              Cancel
            </button>
            <button 
              onClick={handleSelectPrice}
              disabled={selectedScenario === null}
              className={`${
                selectedScenario === null 
                  ? 'bg-gray-600 cursor-not-allowed' 
                  : 'bg-green-600 hover:bg-green-700'
              } px-6 py-3 rounded-lg font-semibold transition`}
            >
              ✓ Use Selected Price
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default PricingCalculator;

