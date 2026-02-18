import React, { useState } from 'react';
import { DollarSign, TrendingUp, Calculator, CheckCircle, FileText } from 'lucide-react';
import { HistoricalPricing } from './HistoricalPricing';

export function PricingDashboard() {
  const [activeTab, setActiveTab] = useState<'historical' | 'multi-year' | 'labor-rate' | 'quote-validator'>('historical');
  const [multiYearParams, setMultiYearParams] = useState({
    base_year_cost: '',
    num_years: '5',
    escalation_percent: '3',
    markup_percent: '18',
    contract_type: 'service'
  });
  const [multiYearResult, setMultiYearResult] = useState<any>(null);
  const [laborRateParams, setLaborRateParams] = useState({
    service_type: 'drug_testing_collector',
    profit_margin: '10'
  });
  const [laborRateResult, setLaborRateResult] = useState<any>(null);
  const [quoteValidatorParams, setQuoteValidatorParams] = useState({
    service_type: 'medical_courier_ohio',
    quote_amount: '',
    ddi_markup: '18'
  });
  const [quoteValidatorResult, setQuoteValidatorResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const calculateMultiYear = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:5000/api/pricing/multi-year', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          base_year_cost: parseFloat(multiYearParams.base_year_cost),
          num_years: parseInt(multiYearParams.num_years),
          escalation_percent: parseFloat(multiYearParams.escalation_percent),
          markup_percent: parseFloat(multiYearParams.markup_percent),
          contract_type: multiYearParams.contract_type
        })
      });
      const data = await response.json();
      if (data.success) {
        setMultiYearResult(data.result);
      }
    } catch (err) {
      console.error('Error calculating multi-year pricing:', err);
    } finally {
      setLoading(false);
    }
  };

  const calculateLaborRate = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:5000/api/pricing/labor-rate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          service_type: laborRateParams.service_type,
          profit_margin: parseFloat(laborRateParams.profit_margin)
        })
      });
      const data = await response.json();
      if (data.success) {
        setLaborRateResult(data.result);
      }
    } catch (err) {
      console.error('Error calculating labor rate:', err);
    } finally {
      setLoading(false);
    }
  };

  const validateQuote = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:5000/api/pricing/validate-quote', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          service_type: quoteValidatorParams.service_type,
          quote_amount: parseFloat(quoteValidatorParams.quote_amount),
          ddi_markup: parseFloat(quoteValidatorParams.ddi_markup)
        })
      });
      const data = await response.json();
      if (data.success) {
        setQuoteValidatorResult(data.result);
      }
    } catch (err) {
      console.error('Error validating quote:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-green-600 to-emerald-600 rounded-lg p-6">
        <h2 className="text-2xl font-bold text-white mb-2">Government Pricing System</h2>
        <p className="text-green-100">Complete pricing toolkit for government contracts</p>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b border-gray-700 overflow-x-auto">
        <button
          onClick={() => setActiveTab('historical')}
          className={`px-4 py-3 font-medium transition whitespace-nowrap flex items-center gap-2 ${
            activeTab === 'historical'
              ? 'text-green-400 border-b-2 border-green-400'
              : 'text-gray-400 hover:text-gray-300'
          }`}
        >
          <TrendingUp className="w-4 h-4" />
          Historical Pricing
        </button>
        <button
          onClick={() => setActiveTab('multi-year')}
          className={`px-4 py-3 font-medium transition whitespace-nowrap flex items-center gap-2 ${
            activeTab === 'multi-year'
              ? 'text-green-400 border-b-2 border-green-400'
              : 'text-gray-400 hover:text-gray-300'
          }`}
        >
          <Calculator className="w-4 h-4" />
          Multi-Year Pricing
        </button>
        <button
          onClick={() => setActiveTab('labor-rate')}
          className={`px-4 py-3 font-medium transition whitespace-nowrap flex items-center gap-2 ${
            activeTab === 'labor-rate'
              ? 'text-green-400 border-b-2 border-green-400'
              : 'text-gray-400 hover:text-gray-300'
          }`}
        >
          <DollarSign className="w-4 h-4" />
          Labor Rate Calculator
        </button>
        <button
          onClick={() => setActiveTab('quote-validator')}
          className={`px-4 py-3 font-medium transition whitespace-nowrap flex items-center gap-2 ${
            activeTab === 'quote-validator'
              ? 'text-green-400 border-b-2 border-green-400'
              : 'text-gray-400 hover:text-gray-300'
          }`}
        >
          <CheckCircle className="w-4 h-4" />
          Quote Validator
        </button>
      </div>

      {/* Historical Pricing Tab */}
      {activeTab === 'historical' && <HistoricalPricing />}

      {/* Multi-Year Pricing Tab */}
      {activeTab === 'multi-year' && (
        <div className="space-y-6">
          <div className="bg-gray-800 rounded-lg p-6">
            <h3 className="text-lg font-semibold mb-4">Multi-Year Contract Pricing Calculator</h3>
            <p className="text-sm text-gray-400 mb-6">
              Calculate pricing for contracts with base year + option years with annual escalation
            </p>

            <div className="grid grid-cols-2 gap-4 mb-6">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Base Year Cost ($) *
                </label>
                <input
                  type="number"
                  value={multiYearParams.base_year_cost}
                  onChange={(e) => setMultiYearParams({ ...multiYearParams, base_year_cost: e.target.value })}
                  placeholder="50000"
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-green-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Number of Years *
                </label>
                <input
                  type="number"
                  value={multiYearParams.num_years}
                  onChange={(e) => setMultiYearParams({ ...multiYearParams, num_years: e.target.value })}
                  placeholder="5"
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-green-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Annual Escalation (%)
                </label>
                <input
                  type="number"
                  step="0.1"
                  value={multiYearParams.escalation_percent}
                  onChange={(e) => setMultiYearParams({ ...multiYearParams, escalation_percent: e.target.value })}
                  placeholder="3"
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-green-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  DDI Markup (%)
                </label>
                <input
                  type="number"
                  step="0.1"
                  value={multiYearParams.markup_percent}
                  onChange={(e) => setMultiYearParams({ ...multiYearParams, markup_percent: e.target.value })}
                  placeholder="18"
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-green-500"
                />
              </div>

              <div className="col-span-2">
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Contract Type
                </label>
                <select
                  value={multiYearParams.contract_type}
                  onChange={(e) => setMultiYearParams({ ...multiYearParams, contract_type: e.target.value })}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-green-500"
                >
                  <option value="service">Service Contract</option>
                  <option value="product">Product Contract</option>
                </select>
              </div>
            </div>

            <button
              onClick={calculateMultiYear}
              disabled={loading || !multiYearParams.base_year_cost || !multiYearParams.num_years}
              className="w-full flex items-center justify-center gap-2 px-6 py-3 bg-green-600 hover:bg-green-700 disabled:bg-gray-600 disabled:cursor-not-allowed rounded-lg font-medium transition"
            >
              <Calculator className="w-5 h-5" />
              Calculate Multi-Year Pricing
            </button>
          </div>

          {/* Multi-Year Results */}
          {multiYearResult && (
            <div className="bg-gray-800 rounded-lg p-6">
              <h3 className="text-lg font-semibold mb-4">Pricing Breakdown</h3>
              
              <div className="grid grid-cols-3 gap-4 mb-6">
                <div className="bg-green-900/20 border border-green-700 rounded-lg p-4">
                  <p className="text-sm text-gray-400 mb-1">Total Contract Value</p>
                  <p className="text-2xl font-bold text-green-400">${multiYearResult.total_contract_value?.toLocaleString()}</p>
                </div>
                <div className="bg-blue-900/20 border border-blue-700 rounded-lg p-4">
                  <p className="text-sm text-gray-400 mb-1">Total Cost</p>
                  <p className="text-2xl font-bold text-blue-400">${multiYearResult.total_cost?.toLocaleString()}</p>
                </div>
                <div className="bg-purple-900/20 border border-purple-700 rounded-lg p-4">
                  <p className="text-sm text-gray-400 mb-1">Total Profit</p>
                  <p className="text-2xl font-bold text-purple-400">${multiYearResult.total_profit?.toLocaleString()}</p>
                </div>
              </div>

              <div className="space-y-3">
                {multiYearResult.years?.map((year: any, idx: number) => (
                  <div key={idx} className="bg-gray-700/50 rounded-lg p-4 flex items-center justify-between">
                    <div>
                      <p className="font-medium text-white">Year {year.year}</p>
                      <p className="text-sm text-gray-400">Cost: ${year.cost.toLocaleString()} → Bid: ${year.bid.toLocaleString()}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-lg font-bold text-green-400">${year.profit.toLocaleString()}</p>
                      <p className="text-xs text-gray-400">profit</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Labor Rate Calculator Tab */}
      {activeTab === 'labor-rate' && (
        <div className="space-y-6">
          <div className="bg-gray-800 rounded-lg p-6">
            <h3 className="text-lg font-semibold mb-4">Fully Burdened Labor Rate Calculator</h3>
            <p className="text-sm text-gray-400 mb-6">
              Calculate hourly billable rates for self-performed services (includes wages, taxes, benefits, overhead, profit)
            </p>

            <div className="grid grid-cols-2 gap-4 mb-6">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Service Type *
                </label>
                <select
                  value={laborRateParams.service_type}
                  onChange={(e) => setLaborRateParams({ ...laborRateParams, service_type: e.target.value })}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-green-500"
                >
                  <option value="drug_testing_collector">Drug Testing Collector</option>
                  <option value="fingerprint_technician">Fingerprint Technician</option>
                  <option value="mobile_notary">Mobile Notary</option>
                  <option value="nemt_driver">NEMT Driver</option>
                  <option value="courier_driver">Courier Driver</option>
                  <option value="grounds_maintenance">Grounds Maintenance</option>
                  <option value="janitorial_worker">Janitorial Worker</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Profit Margin (%)
                </label>
                <input
                  type="number"
                  step="0.1"
                  value={laborRateParams.profit_margin}
                  onChange={(e) => setLaborRateParams({ ...laborRateParams, profit_margin: e.target.value })}
                  placeholder="10"
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-green-500"
                />
              </div>
            </div>

            <button
              onClick={calculateLaborRate}
              disabled={loading}
              className="w-full flex items-center justify-center gap-2 px-6 py-3 bg-green-600 hover:bg-green-700 disabled:bg-gray-600 disabled:cursor-not-allowed rounded-lg font-medium transition"
            >
              <DollarSign className="w-5 h-5" />
              Calculate Labor Rate
            </button>
          </div>

          {/* Labor Rate Results */}
          {laborRateResult && (
            <div className="bg-gray-800 rounded-lg p-6">
              <h3 className="text-lg font-semibold mb-4">Billable Rate Breakdown</h3>
              
              <div className="bg-gradient-to-r from-green-900/40 to-emerald-900/40 border border-green-700 rounded-lg p-6 mb-6">
                <p className="text-sm text-gray-400 mb-2">Billable Hourly Rate</p>
                <p className="text-4xl font-bold text-green-400">${laborRateResult.billable_rate?.toFixed(2)}/hour</p>
              </div>

              <div className="space-y-2 text-sm">
                <div className="flex justify-between py-2 border-b border-gray-700">
                  <span className="text-gray-400">Base Wage</span>
                  <span className="text-white font-medium">${laborRateResult.base_wage?.toFixed(2)}/hour</span>
                </div>
                <div className="flex justify-between py-2 border-b border-gray-700">
                  <span className="text-gray-400">Payroll Taxes (7.65%)</span>
                  <span className="text-white font-medium">${laborRateResult.payroll_taxes?.toFixed(2)}/hour</span>
                </div>
                <div className="flex justify-between py-2 border-b border-gray-700">
                  <span className="text-gray-400">Workers' Comp</span>
                  <span className="text-white font-medium">${laborRateResult.workers_comp?.toFixed(2)}/hour</span>
                </div>
                <div className="flex justify-between py-2 border-b border-gray-700">
                  <span className="text-gray-400">Health Insurance</span>
                  <span className="text-white font-medium">${laborRateResult.health_insurance?.toFixed(2)}/hour</span>
                </div>
                <div className="flex justify-between py-2 border-b border-gray-700">
                  <span className="text-gray-400">PTO (10 days)</span>
                  <span className="text-white font-medium">${laborRateResult.pto?.toFixed(2)}/hour</span>
                </div>
                <div className="flex justify-between py-2 border-b border-gray-700">
                  <span className="text-gray-400">Overhead (15%)</span>
                  <span className="text-white font-medium">${laborRateResult.overhead?.toFixed(2)}/hour</span>
                </div>
                <div className="flex justify-between py-3 border-t-2 border-green-700">
                  <span className="text-green-400 font-bold">Profit ({laborRateParams.profit_margin}%)</span>
                  <span className="text-green-400 font-bold">${laborRateResult.profit?.toFixed(2)}/hour</span>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Quote Validator Tab */}
      {activeTab === 'quote-validator' && (
        <div className="space-y-6">
          <div className="bg-gray-800 rounded-lg p-6">
            <h3 className="text-lg font-semibold mb-4">Subcontractor Quote Validator</h3>
            <p className="text-sm text-gray-400 mb-6">
              Validate subcontractor quotes against market benchmarks
            </p>

            <div className="grid grid-cols-2 gap-4 mb-6">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Service Type *
                </label>
                <select
                  value={quoteValidatorParams.service_type}
                  onChange={(e) => setQuoteValidatorParams({ ...quoteValidatorParams, service_type: e.target.value })}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-green-500"
                >
                  <option value="medical_courier_ohio">Medical Courier (Ohio)</option>
                  <option value="nemt_per_mile">NEMT (per mile)</option>
                  <option value="drug_testing">Drug Testing</option>
                  <option value="fingerprinting">Fingerprinting</option>
                  <option value="mobile_notary">Mobile Notary</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Subcontractor Quote ($) *
                </label>
                <input
                  type="number"
                  step="0.01"
                  value={quoteValidatorParams.quote_amount}
                  onChange={(e) => setQuoteValidatorParams({ ...quoteValidatorParams, quote_amount: e.target.value })}
                  placeholder="60.00"
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-green-500"
                />
              </div>

              <div className="col-span-2">
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  DDI Markup (%)
                </label>
                <input
                  type="number"
                  step="0.1"
                  value={quoteValidatorParams.ddi_markup}
                  onChange={(e) => setQuoteValidatorParams({ ...quoteValidatorParams, ddi_markup: e.target.value })}
                  placeholder="18"
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-green-500"
                />
              </div>
            </div>

            <button
              onClick={validateQuote}
              disabled={loading || !quoteValidatorParams.quote_amount}
              className="w-full flex items-center justify-center gap-2 px-6 py-3 bg-green-600 hover:bg-green-700 disabled:bg-gray-600 disabled:cursor-not-allowed rounded-lg font-medium transition"
            >
              <CheckCircle className="w-5 h-5" />
              Validate Quote
            </button>
          </div>

          {/* Quote Validator Results */}
          {quoteValidatorResult && (
            <div className="space-y-4">
              <div className={`rounded-lg p-6 border-2 ${
                quoteValidatorResult.assessment === 'reasonable' 
                  ? 'bg-green-900/20 border-green-700' 
                  : quoteValidatorResult.assessment === 'too_high'
                  ? 'bg-red-900/20 border-red-700'
                  : 'bg-yellow-900/20 border-yellow-700'
              }`}>
                <h3 className="text-lg font-semibold mb-2">
                  Assessment: <span className="capitalize">{quoteValidatorResult.assessment?.replace('_', ' ')}</span>
                </h3>
                <p className="text-gray-300">{quoteValidatorResult.recommendation}</p>
              </div>

              <div className="bg-gray-800 rounded-lg p-6">
                <h3 className="text-lg font-semibold mb-4">Pricing Comparison</h3>
                <div className="grid grid-cols-3 gap-4">
                  <div className="bg-gray-700/50 rounded-lg p-4">
                    <p className="text-sm text-gray-400 mb-1">Sub Quote</p>
                    <p className="text-2xl font-bold text-white">${quoteValidatorResult.quote_amount?.toFixed(2)}</p>
                  </div>
                  <div className="bg-gray-700/50 rounded-lg p-4">
                    <p className="text-sm text-gray-400 mb-1">Market Benchmark</p>
                    <p className="text-2xl font-bold text-blue-400">${quoteValidatorResult.market_rate?.toFixed(2)}</p>
                  </div>
                  <div className="bg-gray-700/50 rounded-lg p-4">
                    <p className="text-sm text-gray-400 mb-1">DDI Bid Price</p>
                    <p className="text-2xl font-bold text-green-400">${quoteValidatorResult.ddi_bid?.toFixed(2)}</p>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
