import React, { useState, useEffect } from 'react';
import { FileText, DollarSign, Award, Send, ArrowLeft, Handshake, Search, Calculator, Shield, Target } from 'lucide-react';
import { api } from '../../api/client';
import { AutoPricingCalculator } from './PnLEngine';

interface DocumentGeneratorProps {
  onBackToNexus: () => void;
  activeTab?: string;
  setActiveTab?: (tab: string) => void;
}

type DocType = 'quotes' | 'capstats' | 'rfps' | 'partnerships' | 'sources_sought' | 'sole_source' | 'pricing';

const VALID_DOC_TYPES: DocType[] = ['quotes', 'capstats', 'rfps', 'partnerships', 'sources_sought', 'sole_source', 'pricing'];

export function DocumentGenerator({ onBackToNexus, activeTab = 'quotes', setActiveTab }: DocumentGeneratorProps) {
  const initialTab = VALID_DOC_TYPES.includes(activeTab as DocType) ? (activeTab as DocType) : 'quotes';
  const [currentDocType, setCurrentDocType] = useState<DocType>(initialTab);
  const [searchQuery, setSearchQuery] = useState('');
  const [opportunities, setOpportunities] = useState<any[]>([]);
  const [filteredOpportunities, setFilteredOpportunities] = useState<any[]>([]);
  const [selectedOpportunity, setSelectedOpportunity] = useState<any>(null);
  const [showResults, setShowResults] = useState(false);

  // Sync with external activeTab changes
  useEffect(() => {
    if (activeTab && VALID_DOC_TYPES.includes(activeTab as DocType)) {
      setCurrentDocType(activeTab as DocType);
    }
  }, [activeTab]);

  // Fetch opportunities from Airtable
  useEffect(() => {
    const fetchOpportunities = async () => {
      try {
        const response = await api.getGpssOpportunities();
        setOpportunities(response.opportunities || []);
      } catch (error) {
        console.error('Error fetching opportunities:', error);
      }
    };
    fetchOpportunities();
  }, []);

  // Filter opportunities as user types
  useEffect(() => {
    if (searchQuery.trim() === '') {
      setFilteredOpportunities([]);
      setShowResults(false);
      return;
    }

    const query = searchQuery.toLowerCase();
    const filtered = opportunities.filter(opp => {
      const name = (opp.Name || '').toLowerCase();
      const rfpNumber = (opp['RFP NUMBER'] || '').toLowerCase();
      return name.includes(query) || rfpNumber.includes(query);
    });

    setFilteredOpportunities(filtered.slice(0, 5)); // Show top 5 results
    setShowResults(true);
  }, [searchQuery, opportunities]);

  const handleSelectOpportunity = (opp: any) => {
    setSelectedOpportunity(opp);
    setSearchQuery(opp['RFP NUMBER'] || opp.Name || '');
    setShowResults(false);
  };

  const handleClearSelection = () => {
    setSelectedOpportunity(null);
    setSearchQuery('');
  };

  const handleTabChange = (tab: DocType) => {
    setCurrentDocType(tab);
    if (setActiveTab) {
      setActiveTab(tab);
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white p-6">
      {/* Header */}
      <div className="mb-8">
        <button
          onClick={onBackToNexus}
          className="flex items-center text-blue-400 hover:text-blue-300 mb-4"
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back to NEXUS
        </button>
        
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold text-white mb-2">Document Generator</h1>
            <p className="text-gray-400">Create professional quotes, capability statements, and supplier RFPs</p>
          </div>
          <div className="text-right">
            <div className="text-sm text-gray-400">NEXUS Integrated System</div>
            <div className="text-xs text-gray-500">Document Creation & Management</div>
          </div>
        </div>
      </div>

      {/* SEARCH BAR */}
      <div className="mb-6 relative">
        <div className="bg-gray-800 rounded-lg p-4 border-2 border-blue-500/30">
          <label className="block text-sm font-semibold text-blue-400 mb-2">
            🔍 Search Opportunity by RFP# or Name
          </label>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onFocus={() => searchQuery && setShowResults(true)}
              placeholder="Type RFP# (e.g., ITB 2026-007, 7790) or opportunity name..."
              className="w-full pl-10 pr-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            {selectedOpportunity && (
              <button
                onClick={handleClearSelection}
                className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-white"
              >
                ✕
              </button>
            )}
          </div>

          {/* Search Results Dropdown */}
          {showResults && filteredOpportunities.length > 0 && (
            <div className="absolute z-10 w-full mt-2 bg-gray-800 border border-gray-600 rounded-lg shadow-xl max-h-64 overflow-y-auto">
              {filteredOpportunities.map((opp, index) => (
                <button
                  key={index}
                  onClick={() => handleSelectOpportunity(opp)}
                  className="w-full px-4 py-3 text-left hover:bg-gray-700 border-b border-gray-700 last:border-b-0 transition"
                >
                  <div className="font-semibold text-white">{opp['RFP NUMBER'] || 'No RFP#'}</div>
                  <div className="text-sm text-gray-400 truncate">{opp.Name || 'Unnamed Opportunity'}</div>
                  {opp.Deadline && (
                    <div className="text-xs text-blue-400 mt-1">Due: {opp.Deadline}</div>
                  )}
                </button>
              ))}
            </div>
          )}

          {showResults && filteredOpportunities.length === 0 && searchQuery.trim() !== '' && (
            <div className="absolute z-10 w-full mt-2 bg-gray-800 border border-gray-600 rounded-lg shadow-xl p-4 text-center text-gray-400">
              No opportunities found matching "{searchQuery}"
            </div>
          )}

          {/* Selected Opportunity Display */}
          {selectedOpportunity && (
            <div className="mt-3 p-3 bg-blue-900/20 border border-blue-500/50 rounded-lg">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="text-xs text-blue-400 font-semibold mb-1">SELECTED OPPORTUNITY</div>
                  <div className="font-bold text-white">{selectedOpportunity['RFP NUMBER']}</div>
                  <div className="text-sm text-gray-300">{selectedOpportunity.Name}</div>
                  {selectedOpportunity.Deadline && (
                    <div className="text-xs text-gray-400 mt-1">Deadline: {selectedOpportunity.Deadline}</div>
                  )}
                </div>
                <div className="text-2xl">✅</div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="mb-6">
        <div className="border-b border-gray-700">
          <nav className="flex space-x-8">
            <button
              onClick={() => handleTabChange('quotes')}
              className={`
                pb-4 px-1 border-b-2 font-medium text-sm transition-colors
                ${currentDocType === 'quotes'
                  ? 'border-blue-500 text-blue-400'
                  : 'border-transparent text-gray-400 hover:text-gray-300 hover:border-gray-300'
                }
              `}
            >
              <div className="flex items-center space-x-2">
                <DollarSign className="w-4 h-4" />
                <span>Quote Generator</span>
              </div>
            </button>

            <button
              onClick={() => handleTabChange('capstats')}
              className={`
                pb-4 px-1 border-b-2 font-medium text-sm transition-colors
                ${currentDocType === 'capstats'
                  ? 'border-blue-500 text-blue-400'
                  : 'border-transparent text-gray-400 hover:text-gray-300 hover:border-gray-300'
                }
              `}
            >
              <div className="flex items-center space-x-2">
                <Award className="w-4 h-4" />
                <span>Capability Statements</span>
              </div>
            </button>

            <button
              onClick={() => handleTabChange('rfps')}
              className={`
                pb-4 px-1 border-b-2 font-medium text-sm transition-colors
                ${currentDocType === 'rfps'
                  ? 'border-blue-500 text-blue-400'
                  : 'border-transparent text-gray-400 hover:text-gray-300 hover:border-gray-300'
                }
              `}
            >
              <div className="flex items-center space-x-2">
                <Send className="w-4 h-4" />
                <span>RFP Generator</span>
              </div>
            </button>

            <button
              onClick={() => handleTabChange('partnerships')}
              className={`
                pb-4 px-1 border-b-2 font-medium text-sm transition-colors
                ${currentDocType === 'partnerships'
                  ? 'border-blue-500 text-blue-400'
                  : 'border-transparent text-gray-400 hover:text-gray-300 hover:border-gray-300'
                }
              `}
            >
              <div className="flex items-center space-x-2">
                <Handshake className="w-4 h-4" />
                <span>Partnership Proposals</span>
              </div>
            </button>

            <button
              onClick={() => handleTabChange('sources_sought')}
              className={`
                pb-4 px-1 border-b-2 font-medium text-sm transition-colors
                ${currentDocType === 'sources_sought'
                  ? 'border-blue-500 text-blue-400'
                  : 'border-transparent text-gray-400 hover:text-gray-300 hover:border-gray-300'
                }
              `}
            >
              <div className="flex items-center space-x-2">
                <Target className="w-4 h-4" />
                <span>Sources Sought</span>
              </div>
            </button>

            <button
              onClick={() => handleTabChange('sole_source')}
              className={`
                pb-4 px-1 border-b-2 font-medium text-sm transition-colors
                ${currentDocType === 'sole_source'
                  ? 'border-blue-500 text-blue-400'
                  : 'border-transparent text-gray-400 hover:text-gray-300 hover:border-gray-300'
                }
              `}
            >
              <div className="flex items-center space-x-2">
                <Shield className="w-4 h-4" />
                <span>Sole Source</span>
              </div>
            </button>

            <div className="border-l border-gray-600 mx-2 self-stretch" />

            <button
              onClick={() => handleTabChange('pricing')}
              className={`
                pb-4 px-1 border-b-2 font-medium text-sm transition-colors
                ${currentDocType === 'pricing'
                  ? 'border-orange-500 text-orange-400'
                  : 'border-transparent text-gray-400 hover:text-gray-300 hover:border-gray-300'
                }
              `}
            >
              <div className="flex items-center space-x-2">
                <Calculator className="w-4 h-4" />
                <span>Pricing Engine</span>
              </div>
            </button>

          </nav>
        </div>
      </div>

      {/* Content Area */}
      {currentDocType === 'pricing' ? (
        <div className="bg-gray-800 rounded-lg p-6" style={{ background: '#111', fontFamily: "'JetBrains Mono', 'Fira Code', monospace" }}>
          <AutoPricingCalculator />
          <div className="mt-8 pt-4 border-t border-gray-700 flex justify-between text-xs text-gray-600 font-mono">
            <span>NEXUS P&L Engine v3.0 — Cost × (1+OH) × (1+G&A) × (1+Tax) × (1+D&A) × (1+Cont) × (1+Profit)</span>
            <span>DEE DAVIS INC © 2026</span>
          </div>
        </div>
      ) : (
        <div className="bg-gray-800 rounded-lg p-6">
          {currentDocType === 'quotes' && <QuoteGeneratorContent selectedOpportunity={selectedOpportunity} />}
          {currentDocType === 'capstats' && <CapabilityStatementContent selectedOpportunity={selectedOpportunity} />}
          {currentDocType === 'rfps' && <RFPGeneratorContent selectedOpportunity={selectedOpportunity} />}
          {currentDocType === 'partnerships' && <PartnershipProposalContent selectedOpportunity={selectedOpportunity} />}
          {currentDocType === 'sources_sought' && <SourcesSoughtContent selectedOpportunity={selectedOpportunity} />}
          {currentDocType === 'sole_source' && <SoleSourceContent selectedOpportunity={selectedOpportunity} />}
        </div>
      )}
    </div>
  );
}

// ============================================================================
// QUOTE GENERATOR CONTENT
// ============================================================================

function QuoteGeneratorContent({ selectedOpportunity }: { selectedOpportunity?: any }) {
  const [formData, setFormData] = useState({
    clientName: '',
    projectName: '',
    items: [{ description: '', quantity: 1, unitPrice: 0 }],
  });

  // Auto-populate when opportunity selected
  useEffect(() => {
    if (selectedOpportunity) {
      setFormData({
        clientName: selectedOpportunity['Issuing Organization'] || '',
        projectName: selectedOpportunity.Name || '',
        items: [{ description: 'Items from ' + (selectedOpportunity['RFP NUMBER'] || 'opportunity'), quantity: 1, unitPrice: 0 }],
      });
    }
  }, [selectedOpportunity]);

  const addItem = () => {
    setFormData({
      ...formData,
      items: [...formData.items, { description: '', quantity: 1, unitPrice: 0 }],
    });
  };

  const handleGenerateQuote = async () => {
    try {
      const response = await fetch((process.env.REACT_APP_API_BASE || 'http://127.0.0.1:8000') + '/api/quote/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });
      
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        
        // Open PDF in new tab for preview/review FIRST
        window.open(url, '_blank');
        
        // Also prepare download link (user can save after reviewing)
        const a = document.createElement('a');
        a.href = url;
        a.download = `quote_${Date.now()}.pdf`;
        // Don't auto-click, let user review first
        
        // Show success message
        alert('✅ Quote generated! Review it in the new tab.\n\nYou can save it using your browser\'s download button.');
      }
    } catch (error) {
      console.error('Error generating quote:', error);
      alert('Error generating quote. Make sure the API server is running.');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-white">Create New Quote</h2>
        <button
          onClick={handleGenerateQuote}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center space-x-2"
        >
          <DollarSign className="w-4 h-4" />
          <span>Generate Quote PDF</span>
        </button>
      </div>

      <div className="grid grid-cols-2 gap-6">
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Client Name
          </label>
          <input
            type="text"
            value={formData.clientName}
            onChange={(e) => setFormData({ ...formData, clientName: e.target.value })}
            className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Enter client name"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Project Name
          </label>
          <input
            type="text"
            value={formData.projectName}
            onChange={(e) => setFormData({ ...formData, projectName: e.target.value })}
            className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Enter project name"
          />
        </div>
      </div>

      <div>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-white">Line Items</h3>
          <button
            onClick={addItem}
            className="px-3 py-1 bg-gray-700 text-white rounded hover:bg-gray-600 transition-colors text-sm"
          >
            + Add Item
          </button>
        </div>

        <div className="space-y-3">
          {formData.items.map((item, index) => (
            <div key={index} className="grid grid-cols-12 gap-3">
              <div className="col-span-6">
                <input
                  type="text"
                  value={item.description}
                  onChange={(e) => {
                    const newItems = [...formData.items];
                    newItems[index].description = e.target.value;
                    setFormData({ ...formData, items: newItems });
                  }}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white text-sm"
                  placeholder="Item description"
                />
              </div>
              <div className="col-span-2">
                <input
                  type="number"
                  value={item.quantity}
                  onChange={(e) => {
                    const newItems = [...formData.items];
                    newItems[index].quantity = parseInt(e.target.value) || 1;
                    setFormData({ ...formData, items: newItems });
                  }}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white text-sm"
                  placeholder="Qty"
                />
              </div>
              <div className="col-span-3">
                <input
                  type="number"
                  value={item.unitPrice}
                  onChange={(e) => {
                    const newItems = [...formData.items];
                    newItems[index].unitPrice = parseFloat(e.target.value) || 0;
                    setFormData({ ...formData, items: newItems });
                  }}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white text-sm"
                  placeholder="Unit Price"
                />
              </div>
              <div className="col-span-1 flex items-center">
                <span className="text-gray-400 text-sm">
                  ${(item.quantity * item.unitPrice).toFixed(2)}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="bg-gray-700 rounded-lg p-4">
        <div className="flex justify-between items-center">
          <span className="text-lg font-semibold text-white">Total:</span>
          <span className="text-2xl font-bold text-green-400">
            ${formData.items.reduce((sum, item) => sum + (item.quantity * item.unitPrice), 0).toFixed(2)}
          </span>
        </div>
      </div>

      <div className="text-sm text-gray-400">
        <p>💡 <strong>Tip:</strong> The quote will be generated with DDI branding and saved as a PDF.</p>
        <p className="mt-2">API Endpoint: /api/quote/generate</p>
      </div>
    </div>
  );
}

// ============================================================================
// CAPABILITY STATEMENT CONTENT
// ============================================================================

function CapabilityStatementContent({ selectedOpportunity }: { selectedOpportunity?: any }) {
  const [formData, setFormData] = useState({
    companyName: 'DEE DAVIS INC',
    naicsCodes: '',
    coreCompetencies: '',
    pastPerformance: '',
  });

  // Auto-populate NAICS codes and context from selected opportunity
  useEffect(() => {
    if (selectedOpportunity) {
      setFormData(prev => ({
        ...prev,
        naicsCodes: selectedOpportunity['NAICS'] || selectedOpportunity['NAICS Code'] || prev.naicsCodes,
        coreCompetencies: selectedOpportunity.Category
          ? `${selectedOpportunity.Category} — tailored for ${selectedOpportunity.Name || 'this opportunity'}`
          : prev.coreCompetencies,
      }));
    }
  }, [selectedOpportunity]);

  const handleGenerateCapStat = async () => {
    try {
      const response = await fetch((process.env.REACT_APP_API_BASE || 'http://127.0.0.1:8000') + '/api/capstat/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });
      
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        
        // Open PDF in new tab for preview/review FIRST
        window.open(url, '_blank');
        
        // Also prepare download link (user can save after reviewing)
        const a = document.createElement('a');
        a.href = url;
        a.download = `capability_statement_${Date.now()}.pdf`;
        // Don't auto-click, let user review first
        
        // Show success message
        alert('✅ Capability Statement generated! Review it in the new tab.\n\nYou can save it using your browser\'s download button.');
      }
    } catch (error) {
      console.error('Error generating capability statement:', error);
      alert('Error generating capability statement. Make sure the API server is running.');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-white">Create Capability Statement</h2>
        <button
          onClick={handleGenerateCapStat}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center space-x-2"
        >
          <Award className="w-4 h-4" />
          <span>Generate PDF</span>
        </button>
      </div>

      <div className="space-y-6">
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Company Name
          </label>
          <input
            type="text"
            value={formData.companyName}
            onChange={(e) => setFormData({ ...formData, companyName: e.target.value })}
            className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="DEE DAVIS INC"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            NAICS Codes
          </label>
          <input
            type="text"
            value={formData.naicsCodes}
            onChange={(e) => setFormData({ ...formData, naicsCodes: e.target.value })}
            className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="423840, 541614, 238990"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Core Competencies
          </label>
          <textarea
            rows={4}
            value={formData.coreCompetencies}
            onChange={(e) => setFormData({ ...formData, coreCompetencies: e.target.value })}
            className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Enter core competencies, one per line..."
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Past Performance
          </label>
          <textarea
            rows={4}
            value={formData.pastPerformance}
            onChange={(e) => setFormData({ ...formData, pastPerformance: e.target.value })}
            className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Enter past performance examples..."
          />
        </div>
      </div>

      <div className="text-sm text-gray-400">
        <p>💡 <strong>Tip:</strong> Capability statements showcase your company's qualifications for government contracts.</p>
        <p className="mt-2">API Endpoint: /api/capstat/generate</p>
      </div>
    </div>
  );
}

// ============================================================================
// RFP GENERATOR CONTENT
// ============================================================================

function RFPGeneratorContent({ selectedOpportunity }: { selectedOpportunity?: any }) {
  const [formData, setFormData] = useState({
    projectName: '',
    category: 'General Services',
    sanitizedLocation: '',
    scopeOfWork: '',
    contractValueMin: 0,
    contractValueMax: 0,
    quoteDueDate: '',
    contractPeriod: '',
    serviceLocationsCount: 0,
    insuranceRequirements: '',
    buyerName: '',
    buyerRfpNumber: '',
  });

  const [generatedRfp, setGeneratedRfp] = useState<any>(null);

  // Auto-populate form when opportunity is selected
  useEffect(() => {
    if (selectedOpportunity) {
      setFormData({
        projectName: selectedOpportunity.Name || '',
        category: selectedOpportunity.Category || 'General Services',
        sanitizedLocation: selectedOpportunity.State ? `${selectedOpportunity.State} (Generic Location)` : '',
        scopeOfWork: selectedOpportunity.Description || '',
        contractValueMin: selectedOpportunity['Estimated Value'] ? selectedOpportunity['Estimated Value'] * 0.8 : 0,
        contractValueMax: selectedOpportunity['Estimated Value'] || 0,
        quoteDueDate: selectedOpportunity.Deadline ? new Date(new Date(selectedOpportunity.Deadline).getTime() - 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0] : '',
        contractPeriod: '12 months',
        serviceLocationsCount: 0,
        insuranceRequirements: 'General Liability: $1,000,000 per occurrence\nAutomobile Liability: $1,000,000 (if applicable)\nWorkers Compensation: As required by state law',
        buyerName: selectedOpportunity['Issuing Organization'] || '',
        buyerRfpNumber: selectedOpportunity['RFP NUMBER'] || '',
      });
    }
  }, [selectedOpportunity]);

  const handleGenerateRFP = async () => {
    try {
      const response = await fetch((process.env.REACT_APP_API_BASE || 'http://127.0.0.1:8000') + '/api/rfp/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          project_name: formData.projectName,
          category: formData.category,
          sanitized_location: formData.sanitizedLocation,
          scope_of_work: formData.scopeOfWork,
          contract_value_min: formData.contractValueMin,
          contract_value_max: formData.contractValueMax,
          quote_due_date: formData.quoteDueDate,
          contract_period: formData.contractPeriod,
          service_locations_count: formData.serviceLocationsCount,
          insurance_requirements: formData.insuranceRequirements,
          buyer_name: formData.buyerName,
          buyer_rfp_number: formData.buyerRfpNumber,
        }),
      });
      
      const result = await response.json();
      
      if (result.success) {
        setGeneratedRfp(result);
        // Automatically open the PDF for preview
        openPDFPreview(result.rfp_number);
      } else {
        alert(`❌ Error: ${result.error}`);
      }
    } catch (error) {
      console.error('Error generating RFP:', error);
      alert('Error generating RFP. Make sure the API server is running.');
    }
  };

  const handleTestRFP = async () => {
    try {
      const response = await fetch((process.env.REACT_APP_API_BASE || 'http://127.0.0.1:8000') + '/api/rfp/test', {
        method: 'POST',
      });
      
      const result = await response.json();
      
      if (result.success) {
        setGeneratedRfp(result);
        // Automatically open the PDF for preview
        openPDFPreview(result.rfp_number);
      } else {
        alert(`Error: ${result.error}`);
      }
    } catch (error) {
      console.error('Error generating test RFP:', error);
      alert('Error generating RFP. Make sure the API server is running.');
    }
  };

  const openPDFPreview = (rfpNumber: string) => {
    // Open PDF in new tab for preview/review (inline, not download)
    const pdfUrl = `${process.env.REACT_APP_API_BASE || 'http://127.0.0.1:8000'}/api/rfp/view/${rfpNumber}`;
    window.open(pdfUrl, '_blank');
  };

  const handleDownloadRFP = () => {
    if (generatedRfp && generatedRfp.rfp_number) {
      // Use view endpoint to open for review again
      window.open(`${process.env.REACT_APP_API_BASE || 'http://127.0.0.1:8000'}/api/rfp/view/${generatedRfp.rfp_number}`, '_blank');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white">Create Supplier RFP</h2>
          <p className="text-sm text-gray-400 mt-1">Generate professional, DDI-branded RFPs with buyer protection</p>
        </div>
        <div className="flex space-x-3">
          <button
            onClick={handleTestRFP}
            className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors flex items-center space-x-2"
          >
            <FileText className="w-4 h-4" />
            <span>Generate Test RFP</span>
          </button>
          <button
            onClick={handleGenerateRFP}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center space-x-2"
          >
            <Send className="w-4 h-4" />
            <span>Generate RFP PDF</span>
          </button>
        </div>
      </div>

      {generatedRfp && (
        <div className="bg-green-900 border border-green-700 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold text-green-100">✅ RFP Generated Successfully!</h3>
              <p className="text-sm text-green-200 mt-1">
                RFP Number: <strong>{generatedRfp.rfp_number}</strong>
              </p>
              <p className="text-xs text-green-300 mt-1">PDF opened in new tab for review</p>
              <p className="text-xs text-green-400 mt-1">💡 Review it, then save from your browser if satisfied</p>
            </div>
            <button
              onClick={handleDownloadRFP}
              className="px-4 py-2 bg-green-700 text-white rounded-lg hover:bg-green-600 transition-colors"
            >
              Open Again
            </button>
          </div>
        </div>
      )}

      <div className="grid grid-cols-2 gap-6">
        {/* CONFIDENTIAL SECTION */}
        <div className="col-span-2 border-l-4 border-red-500 bg-red-900 bg-opacity-20 p-4 rounded">
          <h3 className="text-lg font-semibold text-red-400 mb-3">🔒 CONFIDENTIAL - Buyer Information</h3>
          <p className="text-sm text-red-300 mb-4">This information is NOT shared with suppliers</p>
          
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Buyer Name (Confidential)
              </label>
              <input
                type="text"
                value={formData.buyerName}
                onChange={(e) => setFormData({ ...formData, buyerName: e.target.value })}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white text-sm"
                placeholder="City of Auburn Hills"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Buyer's RFP Number (Confidential)
              </label>
              <input
                type="text"
                value={formData.buyerRfpNumber}
                onChange={(e) => setFormData({ ...formData, buyerRfpNumber: e.target.value })}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white text-sm"
                placeholder="RFQ-01-30-2026-001"
              />
            </div>
          </div>
        </div>

        {/* PUBLIC SECTION */}
        <div className="col-span-2 border-l-4 border-green-500 bg-green-900 bg-opacity-20 p-4 rounded">
          <h3 className="text-lg font-semibold text-green-400 mb-3">✅ PUBLIC - Supplier-Facing Information</h3>
          <p className="text-sm text-green-300 mb-4">This information IS shared with suppliers in the RFP</p>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Project Name
          </label>
          <input
            type="text"
            value={formData.projectName}
            onChange={(e) => setFormData({ ...formData, projectName: e.target.value })}
            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white"
            placeholder="Municipal Parks Pressure Washing Services"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Category
          </label>
          <select
            value={formData.category}
            onChange={(e) => setFormData({ ...formData, category: e.target.value })}
            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white"
          >
            <option>Pressure Washing</option>
            <option>Landscaping</option>
            <option>Janitorial</option>
            <option>Construction</option>
            <option>Supplies</option>
            <option>HVAC</option>
            <option>Plumbing</option>
            <option>Electrical</option>
            <option>General Services</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Location (Sanitized - Generic Only)
          </label>
          <input
            type="text"
            value={formData.sanitizedLocation}
            onChange={(e) => setFormData({ ...formData, sanitizedLocation: e.target.value })}
            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white"
            placeholder="Oakland County, Michigan"
          />
          <p className="text-xs text-gray-400 mt-1">Use county/region, NOT specific city</p>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Number of Service Locations
          </label>
          <input
            type="number"
            value={formData.serviceLocationsCount}
            onChange={(e) => setFormData({ ...formData, serviceLocationsCount: parseInt(e.target.value) || 0 })}
            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white"
            placeholder="20"
          />
        </div>

        <div className="col-span-2">
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Scope of Work
          </label>
          <textarea
            rows={4}
            value={formData.scopeOfWork}
            onChange={(e) => setFormData({ ...formData, scopeOfWork: e.target.value })}
            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white"
            placeholder="Hot water pressure washing services for park structures, playground equipment..."
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Estimated Value (Min)
          </label>
          <input
            type="number"
            value={formData.contractValueMin}
            onChange={(e) => setFormData({ ...formData, contractValueMin: parseFloat(e.target.value) || 0 })}
            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white"
            placeholder="8000"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Estimated Value (Max)
          </label>
          <input
            type="number"
            value={formData.contractValueMax}
            onChange={(e) => setFormData({ ...formData, contractValueMax: parseFloat(e.target.value) || 0 })}
            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white"
            placeholder="15000"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Quote Due Date (to DDI)
          </label>
          <input
            type="date"
            value={formData.quoteDueDate}
            onChange={(e) => setFormData({ ...formData, quoteDueDate: e.target.value })}
            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Contract Period
          </label>
          <input
            type="text"
            value={formData.contractPeriod}
            onChange={(e) => setFormData({ ...formData, contractPeriod: e.target.value })}
            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white"
            placeholder="March 2026 - December 2026"
          />
        </div>

        <div className="col-span-2">
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Insurance Requirements
          </label>
          <textarea
            rows={3}
            value={formData.insuranceRequirements}
            onChange={(e) => setFormData({ ...formData, insuranceRequirements: e.target.value })}
            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white"
            placeholder="General Liability: $1,000,000 per occurrence..."
          />
        </div>
      </div>

      <div className="bg-blue-900 bg-opacity-20 border border-blue-700 rounded-lg p-4">
        <h4 className="text-sm font-semibold text-blue-300 mb-2">💡 How It Works:</h4>
        <ol className="text-sm text-blue-200 space-y-1 list-decimal list-inside">
          <li>Fill in buyer information (confidential - never shared with suppliers)</li>
          <li>Fill in sanitized supplier-facing information (generic location, no buyer names)</li>
          <li>Click "Generate RFP PDF" to create professional DDI-branded RFP</li>
          <li>System automatically protects buyer identity and adds watermark</li>
          <li>Download PDF and email to suppliers</li>
        </ol>
      </div>

      <div className="text-sm text-gray-400">
        <p>🔒 <strong>Buyer Protection:</strong> All buyer-identifying information is automatically excluded from supplier RFP.</p>
        <p className="mt-2">API Endpoint: /api/rfp/generate</p>
        <p className="mt-1">📁 Output: generated_rfps/RFP_DDI-YYYY-XX-###.pdf</p>
      </div>
    </div>
  );
}

// ============================================================================
// PARTNERSHIP PROPOSAL CONTENT
// ============================================================================

function PartnershipProposalContent({ selectedOpportunity }: { selectedOpportunity?: any }) {
  const [formData, setFormData] = useState({
    partnerName: '',
    proposalType: 'Supplier Diversity Partnership',
    servicesOffered: 'Mobile Notary Services, Courier Services',
    coverage: 'Nationwide (All 50 States)',
    certifications: 'EDWOSB (Economically Disadvantaged Woman-Owned Small Business)',
    keyAdvantages: '',
    targetRevenue: '',
    implementationTimeline: '90 days',
    contactEmail: '',
    contactPhone: '',
  });

  const [generatedProposal, setGeneratedProposal] = useState<any>(null);

  // Partnership proposals are generally not opportunity-specific
  useEffect(() => {
    if (selectedOpportunity) {
      // Partnership proposals don't typically auto-fill from opportunities
    }
  }, [selectedOpportunity]);

  const handleGenerateFedExProposal = () => {
    // Pre-fill for FedEx
    setFormData({
      ...formData,
      partnerName: 'FedEx',
      keyAdvantages: 'Fill service gap - Most FedEx Office locations do NOT offer notary services\nRevenue enhancement - Capture notary revenue without hiring staff\nCompetitive advantage over UPS Store locations\nSupports supplier diversity goals with EDWOSB partner',
      targetRevenue: '$5,000-10,000/month passive income (Conservative: 30 signings/week × $40 margin)',
    });
  };

  const handleGenerateUPSProposal = () => {
    // Pre-fill for UPS
    setFormData({
      ...formData,
      partnerName: 'UPS',
      keyAdvantages: 'Overflow capacity for 5,500+ UPS Store locations\nMobile notary for customers who cannot visit stores\nAfter-hours and weekend service extension\nEnhanced B2B service portfolio for corporate clients',
      targetRevenue: '$5,000-10,000/month passive income (Conservative: 30 signings/week × $40 margin)',
    });
  };

  const handleGenerateProposal = async () => {
    try {
      const response = await fetch((process.env.REACT_APP_API_BASE || 'http://127.0.0.1:8000') + '/api/partnership/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });
      
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        
        // Open PDF in new tab for preview
        window.open(url, '_blank');
        
        // Show success message
        alert('✅ Partnership Proposal generated! Review it in the new tab.\n\nYou can save it using your browser\'s download button.');
        
        setGeneratedProposal({ success: true, partner: formData.partnerName });
      } else {
        alert('Error generating proposal. Make sure the API server is running.');
      }
    } catch (error) {
      console.error('Error generating partnership proposal:', error);
      alert('Error generating partnership proposal. Make sure the API server is running.');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white">Create Partnership Proposal</h2>
          <p className="text-sm text-gray-400 mt-1">Generate professional partnership proposals for corporate diversity programs</p>
        </div>
        <div className="flex space-x-3">
          <button
            onClick={handleGenerateFedExProposal}
            className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors flex items-center space-x-2"
          >
            <FileText className="w-4 h-4" />
            <span>FedEx Template</span>
          </button>
          <button
            onClick={handleGenerateUPSProposal}
            className="px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 transition-colors flex items-center space-x-2"
          >
            <FileText className="w-4 h-4" />
            <span>UPS Template</span>
          </button>
          <button
            onClick={handleGenerateProposal}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center space-x-2"
          >
            <Handshake className="w-4 h-4" />
            <span>Generate Proposal PDF</span>
          </button>
        </div>
      </div>

      {generatedProposal && (
        <div className="bg-green-900 border border-green-700 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold text-green-100">✅ Partnership Proposal Generated!</h3>
              <p className="text-sm text-green-200 mt-1">
                Partner: <strong>{generatedProposal.partner}</strong>
              </p>
              <p className="text-xs text-green-300 mt-1">PDF opened in new tab for review</p>
            </div>
          </div>
        </div>
      )}

      <div className="bg-blue-900 bg-opacity-20 border border-blue-700 rounded-lg p-4">
        <h4 className="text-sm font-semibold text-blue-300 mb-2">💡 Quick Start:</h4>
        <p className="text-sm text-blue-200">
          Click <strong>FedEx Template</strong> or <strong>UPS Template</strong> to pre-fill the form with optimized content,
          then click <strong>Generate Proposal PDF</strong> to create a professional partnership proposal.
        </p>
      </div>

      <div className="grid grid-cols-2 gap-6">
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Partner Company Name <span className="text-red-400">*</span>
          </label>
          <input
            type="text"
            value={formData.partnerName}
            onChange={(e) => setFormData({ ...formData, partnerName: e.target.value })}
            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white"
            placeholder="FedEx or UPS"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Proposal Type
          </label>
          <select
            value={formData.proposalType}
            onChange={(e) => setFormData({ ...formData, proposalType: e.target.value })}
            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white"
          >
            <option>Supplier Diversity Partnership</option>
            <option>Vendor Partnership</option>
            <option>Strategic Alliance</option>
            <option>Service Provider Agreement</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Services Offered
          </label>
          <input
            type="text"
            value={formData.servicesOffered}
            onChange={(e) => setFormData({ ...formData, servicesOffered: e.target.value })}
            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white"
            placeholder="Mobile Notary Services, Courier Services"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Geographic Coverage
          </label>
          <input
            type="text"
            value={formData.coverage}
            onChange={(e) => setFormData({ ...formData, coverage: e.target.value })}
            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white"
            placeholder="Nationwide (All 50 States)"
          />
        </div>

        <div className="col-span-2">
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Certifications
          </label>
          <input
            type="text"
            value={formData.certifications}
            onChange={(e) => setFormData({ ...formData, certifications: e.target.value })}
            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white"
            placeholder="EDWOSB, WBENC, etc."
          />
        </div>

        <div className="col-span-2">
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Key Advantages (Why This Partnership Benefits Them)
          </label>
          <textarea
            rows={5}
            value={formData.keyAdvantages}
            onChange={(e) => setFormData({ ...formData, keyAdvantages: e.target.value })}
            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white"
            placeholder="One advantage per line..."
          />
          <p className="text-xs text-gray-400 mt-1">💡 Focus on THEIR benefits, not your features</p>
        </div>

        <div className="col-span-2">
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Target Revenue / Business Case
          </label>
          <textarea
            rows={3}
            value={formData.targetRevenue}
            onChange={(e) => setFormData({ ...formData, targetRevenue: e.target.value })}
            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white"
            placeholder="$5,000-10,000/month passive income (Conservative: 30 signings/week × $40 margin)"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Implementation Timeline
          </label>
          <input
            type="text"
            value={formData.implementationTimeline}
            onChange={(e) => setFormData({ ...formData, implementationTimeline: e.target.value })}
            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white"
            placeholder="90 days"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Contact Email
          </label>
          <input
            type="email"
            value={formData.contactEmail}
            onChange={(e) => setFormData({ ...formData, contactEmail: e.target.value })}
            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white"
            placeholder="dee@deedavisinc.com"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Contact Phone
          </label>
          <input
            type="tel"
            value={formData.contactPhone}
            onChange={(e) => setFormData({ ...formData, contactPhone: e.target.value })}
            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white"
            placeholder="(555) 123-4567"
          />
        </div>
      </div>

      <div className="bg-yellow-900 bg-opacity-20 border border-yellow-700 rounded-lg p-4">
        <h4 className="text-sm font-semibold text-yellow-300 mb-2">📋 What Gets Generated:</h4>
        <ul className="text-sm text-yellow-200 space-y-1 list-disc list-inside">
          <li>Executive Summary with partnership overview</li>
          <li>Service Overview (Notary + Courier services)</li>
          <li>Why Partner with Dee Davis Inc. (EDWOSB certification, nationwide coverage, technology platform)</li>
          <li>Partnership Models (Referral, White-Label, Preferred Vendor, Pilot Program)</li>
          <li>Implementation Timeline (90-day plan)</li>
          <li>Financial Projections (Conservative/Moderate/Optimistic scenarios)</li>
          <li>Quality Assurance & Compliance Standards</li>
          <li>Contact Information and Next Steps</li>
        </ul>
      </div>

      <div className="text-sm text-gray-400">
        <p>🤝 <strong>Partnership Proposals:</strong> Professional, DDI-branded proposals for supplier diversity programs.</p>
        <p className="mt-2">API Endpoint: /api/partnership/generate</p>
        <p className="mt-1">📁 Output: Partnership_Proposal_[PARTNER]_[DATE].pdf</p>
      </div>
    </div>
  );
}

// ============================================================================
// SOURCES SOUGHT RESPONSE CONTENT
// ============================================================================

function SourcesSoughtContent({ selectedOpportunity }: { selectedOpportunity?: any }) {
  const [formData, setFormData] = useState({
    solicitationNumber: '',
    solicitationTitle: '',
    issuingAgency: '',
    naicsCode: '',
    responseType: 'interested_capable',
    companyDescription: 'DEE DAVIS INC is a certified EDWOSB (Economically Disadvantaged Woman-Owned Small Business) based in Troy, Michigan. We specialize in government contract fulfillment including industrial supplies, professional services, and logistics.',
    relevantExperience: '',
    capabilityNarrative: '',
    setAsideRecommendation: 'WOSB',
    estimatedDeliveryDays: '30',
    teamingInterest: 'open',
  });
  const [generating, setGenerating] = useState(false);

  useEffect(() => {
    if (selectedOpportunity) {
      setFormData(prev => ({
        ...prev,
        solicitationNumber: selectedOpportunity['RFP NUMBER'] || '',
        solicitationTitle: selectedOpportunity.Name || '',
        issuingAgency: selectedOpportunity['Issuing Organization'] || '',
        naicsCode: selectedOpportunity['NAICS'] || selectedOpportunity['NAICS Code'] || '',
      }));
    }
  }, [selectedOpportunity]);

  const handleGenerate = async () => {
    setGenerating(true);
    try {
      const response = await fetch((process.env.REACT_APP_API_BASE || 'http://127.0.0.1:8000') + '/api/sources-sought/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/pdf')) {
          const blob = await response.blob();
          const url = window.URL.createObjectURL(blob);
          window.open(url, '_blank');
          alert('Sources Sought Response generated! Review it in the new tab.');
        } else {
          const result = await response.json();
          if (result.success) {
            alert('Sources Sought Response generated successfully!');
          } else {
            alert(`Error: ${result.error}`);
          }
        }
      } else {
        alert('Error generating response. Make sure the API server is running.');
      }
    } catch (error) {
      console.error('Error:', error);
      alert('Error generating Sources Sought response.');
    }
    setGenerating(false);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white">Sources Sought Response</h2>
          <p className="text-sm text-gray-400 mt-1">Respond to Sources Sought / RFI notices to get on agency radar</p>
        </div>
        <button
          onClick={handleGenerate}
          disabled={generating}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center space-x-2 disabled:opacity-50"
        >
          <Target className="w-4 h-4" />
          <span>{generating ? 'Generating...' : 'Generate Response'}</span>
        </button>
      </div>

      <div className="bg-blue-900 bg-opacity-20 border border-blue-700 rounded-lg p-4">
        <h4 className="text-sm font-semibold text-blue-300 mb-2">What is a Sources Sought Response?</h4>
        <p className="text-sm text-blue-200">
          A Sources Sought (or RFI) notice is when a government agency is researching whether capable vendors exist before
          issuing a formal solicitation. <strong>Responding gets your company on their radar</strong> and can influence
          set-aside decisions (WOSB, EDWOSB, small business). This is how you get in front of opportunities BEFORE they drop.
        </p>
      </div>

      <div className="grid grid-cols-2 gap-6">
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">Solicitation / Notice Number</label>
          <input type="text" value={formData.solicitationNumber}
            onChange={(e) => setFormData({ ...formData, solicitationNumber: e.target.value })}
            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white" placeholder="e.g., SS-2026-0001" />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">NAICS Code</label>
          <input type="text" value={formData.naicsCode}
            onChange={(e) => setFormData({ ...formData, naicsCode: e.target.value })}
            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white" placeholder="423840" />
        </div>
        <div className="col-span-2">
          <label className="block text-sm font-medium text-gray-300 mb-2">Solicitation Title</label>
          <input type="text" value={formData.solicitationTitle}
            onChange={(e) => setFormData({ ...formData, solicitationTitle: e.target.value })}
            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white" placeholder="Title of the Sources Sought notice" />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">Issuing Agency</label>
          <input type="text" value={formData.issuingAgency}
            onChange={(e) => setFormData({ ...formData, issuingAgency: e.target.value })}
            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white" placeholder="Department / Agency name" />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">Response Type</label>
          <select value={formData.responseType}
            onChange={(e) => setFormData({ ...formData, responseType: e.target.value })}
            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white">
            <option value="interested_capable">Interested &amp; Capable</option>
            <option value="interested_teaming">Interested — Open to Teaming</option>
            <option value="information_only">Information Only Response</option>
          </select>
        </div>
        <div className="col-span-2">
          <label className="block text-sm font-medium text-gray-300 mb-2">Company Description / Capability Narrative</label>
          <textarea rows={4} value={formData.capabilityNarrative}
            onChange={(e) => setFormData({ ...formData, capabilityNarrative: e.target.value })}
            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white"
            placeholder="Describe your specific capabilities relevant to this requirement..." />
        </div>
        <div className="col-span-2">
          <label className="block text-sm font-medium text-gray-300 mb-2">Relevant Experience / Past Performance</label>
          <textarea rows={3} value={formData.relevantExperience}
            onChange={(e) => setFormData({ ...formData, relevantExperience: e.target.value })}
            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white"
            placeholder="List relevant contracts or experience..." />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">Set-Aside Recommendation</label>
          <select value={formData.setAsideRecommendation}
            onChange={(e) => setFormData({ ...formData, setAsideRecommendation: e.target.value })}
            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white">
            <option value="WOSB">WOSB (Woman-Owned Small Business)</option>
            <option value="EDWOSB">EDWOSB</option>
            <option value="8a">8(a)</option>
            <option value="SDB">Small Disadvantaged Business</option>
            <option value="SB">Small Business</option>
            <option value="full_open">Full &amp; Open Competition</option>
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">Teaming Interest</label>
          <select value={formData.teamingInterest}
            onChange={(e) => setFormData({ ...formData, teamingInterest: e.target.value })}
            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white">
            <option value="open">Open to Teaming</option>
            <option value="prime_only">Prime Contractor Only</option>
            <option value="sub_available">Available as Subcontractor</option>
          </select>
        </div>
      </div>
    </div>
  );
}

// ============================================================================
// SOLE SOURCE JUSTIFICATION CONTENT
// ============================================================================

function SoleSourceContent({ selectedOpportunity }: { selectedOpportunity?: any }) {
  const [formData, setFormData] = useState({
    solicitationNumber: '',
    solicitationTitle: '',
    issuingAgency: '',
    contractValue: '',
    justificationType: 'unique_capability',
    uniqueCapability: '',
    marketResearch: 'Market research conducted via SAM.gov, GSA Advantage, and industry contacts confirms limited sources for this requirement.',
    urgency: '',
    priceFairness: 'Pricing is based on established GSA Schedule rates and competitive market analysis.',
    deliveryTimeline: '30 days ARO',
    periodOfPerformance: '12 months',
  });
  const [generating, setGenerating] = useState(false);

  useEffect(() => {
    if (selectedOpportunity) {
      setFormData(prev => ({
        ...prev,
        solicitationNumber: selectedOpportunity['RFP NUMBER'] || '',
        solicitationTitle: selectedOpportunity.Name || '',
        issuingAgency: selectedOpportunity['Issuing Organization'] || '',
        contractValue: selectedOpportunity['Estimated Value'] ? `$${Number(selectedOpportunity['Estimated Value']).toLocaleString()}` : '',
      }));
    }
  }, [selectedOpportunity]);

  const handleGenerate = async () => {
    setGenerating(true);
    try {
      const response = await fetch((process.env.REACT_APP_API_BASE || 'http://127.0.0.1:8000') + '/api/sole-source/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/pdf')) {
          const blob = await response.blob();
          const url = window.URL.createObjectURL(blob);
          window.open(url, '_blank');
          alert('Sole Source Justification generated! Review it in the new tab.');
        } else {
          const result = await response.json();
          if (result.success) {
            alert('Sole Source Justification generated successfully!');
          } else {
            alert(`Error: ${result.error}`);
          }
        }
      } else {
        alert('Error generating response. Make sure the API server is running.');
      }
    } catch (error) {
      console.error('Error:', error);
      alert('Error generating Sole Source Justification.');
    }
    setGenerating(false);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white">Sole Source Justification</h2>
          <p className="text-sm text-gray-400 mt-1">Generate J&amp;A documentation for non-competitive awards</p>
        </div>
        <button
          onClick={handleGenerate}
          disabled={generating}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center space-x-2 disabled:opacity-50"
        >
          <Shield className="w-4 h-4" />
          <span>{generating ? 'Generating...' : 'Generate J&A Document'}</span>
        </button>
      </div>

      <div className="bg-yellow-900 bg-opacity-20 border border-yellow-700 rounded-lg p-4">
        <h4 className="text-sm font-semibold text-yellow-300 mb-2">When to Use Sole Source</h4>
        <p className="text-sm text-yellow-200">
          A Sole Source (or Justification &amp; Approval) is used when only one vendor can meet the requirement.
          As an <strong>EDWOSB</strong>, you can receive sole source awards up to <strong>$5M for services</strong> and
          <strong> $7M for manufacturing</strong> under FAR 19.1506. This is a powerful tool — use it strategically.
        </p>
      </div>

      <div className="grid grid-cols-2 gap-6">
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">Solicitation / Contract Number</label>
          <input type="text" value={formData.solicitationNumber}
            onChange={(e) => setFormData({ ...formData, solicitationNumber: e.target.value })}
            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white" placeholder="Contract or solicitation number" />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">Estimated Value</label>
          <input type="text" value={formData.contractValue}
            onChange={(e) => setFormData({ ...formData, contractValue: e.target.value })}
            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white" placeholder="$500,000" />
        </div>
        <div className="col-span-2">
          <label className="block text-sm font-medium text-gray-300 mb-2">Requirement Title</label>
          <input type="text" value={formData.solicitationTitle}
            onChange={(e) => setFormData({ ...formData, solicitationTitle: e.target.value })}
            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white" placeholder="Description of the requirement" />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">Agency</label>
          <input type="text" value={formData.issuingAgency}
            onChange={(e) => setFormData({ ...formData, issuingAgency: e.target.value })}
            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white" placeholder="Contracting agency" />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">Justification Basis</label>
          <select value={formData.justificationType}
            onChange={(e) => setFormData({ ...formData, justificationType: e.target.value })}
            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white">
            <option value="unique_capability">Unique Capability (FAR 6.302-1)</option>
            <option value="edwosb_set_aside">EDWOSB Sole Source (FAR 19.1506)</option>
            <option value="urgency">Unusual Urgency (FAR 6.302-2)</option>
            <option value="only_one_source">Only One Responsible Source (FAR 6.302-1)</option>
          </select>
        </div>
        <div className="col-span-2">
          <label className="block text-sm font-medium text-gray-300 mb-2">Unique Capability / Justification Narrative</label>
          <textarea rows={4} value={formData.uniqueCapability}
            onChange={(e) => setFormData({ ...formData, uniqueCapability: e.target.value })}
            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white"
            placeholder="Explain why only your company can fulfill this requirement. Include certifications, unique capabilities, geographic advantages, etc." />
        </div>
        <div className="col-span-2">
          <label className="block text-sm font-medium text-gray-300 mb-2">Market Research Summary</label>
          <textarea rows={3} value={formData.marketResearch}
            onChange={(e) => setFormData({ ...formData, marketResearch: e.target.value })}
            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white"
            placeholder="Describe market research conducted..." />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">Period of Performance</label>
          <input type="text" value={formData.periodOfPerformance}
            onChange={(e) => setFormData({ ...formData, periodOfPerformance: e.target.value })}
            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white" placeholder="12 months" />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">Delivery Timeline</label>
          <input type="text" value={formData.deliveryTimeline}
            onChange={(e) => setFormData({ ...formData, deliveryTimeline: e.target.value })}
            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white" placeholder="30 days ARO" />
        </div>
        <div className="col-span-2">
          <label className="block text-sm font-medium text-gray-300 mb-2">Price Reasonableness Determination</label>
          <textarea rows={2} value={formData.priceFairness}
            onChange={(e) => setFormData({ ...formData, priceFairness: e.target.value })}
            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white"
            placeholder="Explain how pricing is fair and reasonable..." />
        </div>
      </div>

      <div className="bg-green-900 bg-opacity-20 border border-green-700 rounded-lg p-4">
        <h4 className="text-sm font-semibold text-green-300 mb-2">EDWOSB Sole Source Thresholds (FAR 19.1506)</h4>
        <div className="grid grid-cols-2 gap-4 text-sm text-green-200">
          <div><strong>Services:</strong> Up to $5,000,000</div>
          <div><strong>Manufacturing:</strong> Up to $7,000,000</div>
        </div>
        <p className="text-xs text-green-300 mt-2">
          The contracting officer must determine in writing that the EDWOSB is a responsible contractor
          with a reasonable expectation of performance.
        </p>
      </div>
    </div>
  );
}
