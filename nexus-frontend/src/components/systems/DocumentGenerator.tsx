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
                <span>Answer Solicitation</span>
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

const SECTOR_OPTIONS = [
  { key: 'main', label: 'Main — Contract Management Firm (All Sectors)', color: '#c5963a' },
  { key: 'drug_testing', label: 'Drug & Alcohol Testing / TPA', color: '#a78bfa' },
  { key: 'fingerprinting', label: 'Fingerprinting / Background Screening', color: '#4ade80' },
  { key: 'nemt', label: 'NEMT / Medical Transportation', color: '#dc2626' },
  { key: 'courier', label: 'Courier / Delivery / Logistics', color: '#fb923c' },
  { key: 'dna_testing', label: 'DNA / Paternity / Genetic Testing', color: '#2dd4bf' },
  { key: 'janitorial', label: 'Janitorial / Grounds Maintenance / Facilities', color: '#f59e0b' },
  { key: 'industrial', label: 'Industrial Supplies / Equipment / Parts', color: '#94a3b8' },
  { key: 'notary', label: 'Notary / Signing Agent / Legal Services', color: '#e879a8' },
  { key: 'professional', label: 'Professional Services / Consulting / Staffing', color: '#a3a3a3' },
  { key: 'georgia', label: 'Georgia State Agencies (State Override)', color: '#f87171' },
];

function CapabilityStatementContent({ selectedOpportunity }: { selectedOpportunity?: any }) {
  const [formData, setFormData] = useState({
    sector: 'main',
    agencyName: '',
    solicitationNumber: '',
    serviceDescription: '',
    naicsCodes: '',
    customOverview: '',
  });
  const [generating, setGenerating] = useState(false);
  const [generated, setGenerated] = useState<any>(null);

  useEffect(() => {
    if (selectedOpportunity) {
      const category = (selectedOpportunity.Category || '').toLowerCase();
      let detectedSector = 'main';
      if (category.includes('drug') || category.includes('testing') || category.includes('tpa')) detectedSector = 'drug_testing';
      else if (category.includes('fingerprint') || category.includes('swft') || category.includes('background')) detectedSector = 'fingerprinting';
      else if (category.includes('nemt') || category.includes('transport') || category.includes('wheelchair')) detectedSector = 'nemt';
      else if (category.includes('courier') || category.includes('delivery') || category.includes('logistics')) detectedSector = 'courier';
      else if (category.includes('dna') || category.includes('paternity') || category.includes('genetic')) detectedSector = 'dna_testing';
      else if (category.includes('janitorial') || category.includes('grounds') || category.includes('landscap')) detectedSector = 'janitorial';
      else if (category.includes('industrial') || category.includes('supplies') || category.includes('equipment')) detectedSector = 'industrial';
      else if (category.includes('notary') || category.includes('signing') || category.includes('legal')) detectedSector = 'notary';

      setFormData(prev => ({
        ...prev,
        sector: detectedSector,
        agencyName: selectedOpportunity['Issuing Organization'] || '',
        solicitationNumber: selectedOpportunity['RFP NUMBER'] || '',
        serviceDescription: selectedOpportunity.Name || '',
        naicsCodes: selectedOpportunity['NAICS'] || selectedOpportunity['NAICS Code'] || prev.naicsCodes,
      }));
    }
  }, [selectedOpportunity]);

  const selectedColor = SECTOR_OPTIONS.find(s => s.key === formData.sector)?.color || '#c5963a';

  const handleGenerate = async () => {
    setGenerating(true);
    setGenerated(null);
    try {
      const response = await fetch((process.env.REACT_APP_API_BASE || 'http://127.0.0.1:8000') + '/api/capstat/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        const contentType = response.headers.get('content-type') || '';
        if (contentType.includes('text/html')) {
          const blob = await response.blob();
          const url = window.URL.createObjectURL(blob);
          window.open(url, '_blank');
          setGenerated({ success: true, sector: formData.sector, agency: formData.agencyName });
        } else {
          const data = await response.json();
          if (data.success) {
            setGenerated(data);
          } else {
            alert(data.error || 'Generation failed');
          }
        }
      } else {
        alert('Error generating capability statement. Check API server.');
      }
    } catch (error) {
      console.error('Error generating capability statement:', error);
      alert('Error generating capability statement. Make sure the API server is running.');
    }
    setGenerating(false);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white">Generate Capability Statement</h2>
          <p className="text-sm text-gray-400 mt-1">v3 Engine — Contract Management Firm design with sector-specific colors</p>
        </div>
        <button
          onClick={handleGenerate}
          disabled={generating}
          className="px-5 py-2.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center space-x-2 disabled:opacity-50 font-semibold"
        >
          <Award className="w-4 h-4" />
          <span>{generating ? 'Generating...' : 'Generate Cap Statement'}</span>
        </button>
      </div>

      {generated && (
        <div className="bg-green-900/30 border border-green-600 rounded-lg p-4">
          <h3 className="text-lg font-semibold text-green-300">Cap Statement Generated</h3>
          <p className="text-sm text-green-200 mt-1">
            Sector: <strong>{SECTOR_OPTIONS.find(s => s.key === generated.sector)?.label}</strong>
            {generated.agency && <> | Agency: <strong>{generated.agency}</strong></>}
          </p>
          <p className="text-xs text-green-400 mt-1">Opened in new tab — Cmd+P to save as PDF</p>
        </div>
      )}

      <div className="grid grid-cols-2 gap-6">
        <div className="col-span-2">
          <label className="block text-sm font-semibold text-blue-400 mb-2">
            Service Sector
          </label>
          <div className="relative">
            <select
              value={formData.sector}
              onChange={(e) => setFormData({ ...formData, sector: e.target.value })}
              className="w-full px-4 py-3 bg-gray-700 border-2 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500 appearance-none font-medium"
              style={{ borderColor: selectedColor }}
            >
              {SECTOR_OPTIONS.map(s => (
                <option key={s.key} value={s.key}>{s.label}</option>
              ))}
            </select>
            <div className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 rounded-full" style={{ backgroundColor: selectedColor }} />
          </div>
          <p className="text-xs text-gray-500 mt-1">Colors, competencies, past performance, and differentiators auto-populate per sector</p>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">Agency Name</label>
          <input
            type="text"
            value={formData.agencyName}
            onChange={(e) => setFormData({ ...formData, agencyName: e.target.value })}
            className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="e.g., US Army Corps of Engineers"
          />
          <p className="text-xs text-gray-500 mt-1">Used in gold bar subtitle and tailored intro</p>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">Solicitation Number</label>
          <input
            type="text"
            value={formData.solicitationNumber}
            onChange={(e) => setFormData({ ...formData, solicitationNumber: e.target.value })}
            className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="e.g., W912DR25QA005"
          />
        </div>

        <div className="col-span-2">
          <label className="block text-sm font-medium text-gray-300 mb-2">Service Description (Gold Bar Title Override)</label>
          <input
            type="text"
            value={formData.serviceDescription}
            onChange={(e) => setFormData({ ...formData, serviceDescription: e.target.value })}
            className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Leave blank to use sector default (e.g., DRUG & ALCOHOL TESTING — THIRD-PARTY ADMINISTRATION)"
          />
          <p className="text-xs text-gray-500 mt-1">Override the gold bar title — leave blank for the sector default</p>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">NAICS Codes (Override)</label>
          <input
            type="text"
            value={formData.naicsCodes}
            onChange={(e) => setFormData({ ...formData, naicsCodes: e.target.value })}
            className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Leave blank for sector defaults"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">Custom Overview (Override)</label>
          <input
            type="text"
            value={formData.customOverview}
            onChange={(e) => setFormData({ ...formData, customOverview: e.target.value })}
            className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Leave blank for sector default intro paragraph"
          />
        </div>
      </div>

      <div className="bg-gray-700/50 rounded-lg p-4 border border-gray-600">
        <h4 className="text-sm font-semibold text-gray-300 mb-3">What Gets Generated (v3 Structure)</h4>
        <div className="grid grid-cols-2 gap-3 text-xs text-gray-400">
          <div className="flex items-start gap-2">
            <span style={{ color: selectedColor }}>&#9632;</span>
            <span><strong className="text-white">Header</strong> — DDI logo, CAGE/UEI/DUNS, SAM Active</span>
          </div>
          <div className="flex items-start gap-2">
            <span style={{ color: selectedColor }}>&#9632;</span>
            <span><strong className="text-white">Gold Bar</strong> — Sector title + EDWOSB sole-source line</span>
          </div>
          <div className="flex items-start gap-2">
            <span style={{ color: selectedColor }}>&#9632;</span>
            <span><strong className="text-white">Overview</strong> — CO-grade intro with headshot, framework line</span>
          </div>
          <div className="flex items-start gap-2">
            <span style={{ color: selectedColor }}>&#9632;</span>
            <span><strong className="text-white">Competencies</strong> — 6-8 sector-specific boxes in grid</span>
          </div>
          <div className="flex items-start gap-2">
            <span style={{ color: selectedColor }}>&#9632;</span>
            <span><strong className="text-white">Past Performance</strong> — Verified track record with metrics</span>
          </div>
          <div className="flex items-start gap-2">
            <span style={{ color: selectedColor }}>&#9632;</span>
            <span><strong className="text-white">Differentiators</strong> — EDWOSB, facilities, credentialing, compliance</span>
          </div>
          <div className="flex items-start gap-2">
            <span style={{ color: selectedColor }}>&#9632;</span>
            <span><strong className="text-white">Certifications</strong> — Badge images + full cert list</span>
          </div>
          <div className="flex items-start gap-2">
            <span style={{ color: selectedColor }}>&#9632;</span>
            <span><strong className="text-white">Partners + Footer</strong> — Alliance logos, contact, NAICS</span>
          </div>
        </div>
      </div>

      <div className="text-xs text-gray-500">
        Engine: v3 Contract Management Firm | Template: capability_statement_template.html | API: /api/capstat/generate
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
// SOLICITATION ANSWERING ENGINE
// ============================================================================

function SourcesSoughtContent({ selectedOpportunity }: { selectedOpportunity?: any }) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [analysisStep, setAnalysisStep] = useState('');
  const [result, setResult] = useState<any>(null);
  const [activeSection, setActiveSection] = useState('executive_summary');
  const [editingSection, setEditingSection] = useState<string | null>(null);
  const [editBuffer, setEditBuffer] = useState('');

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) { setSelectedFile(file); }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault(); setIsDragging(false);
    const file = e.dataTransfer.files[0];
    if (file) { setSelectedFile(file); }
  };

  const handleAnalyze = async () => {
    if (!selectedFile) return;
    setAnalyzing(true); setResult(null);
    setAnalysisStep('Reading document...');
    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      setAnalysisStep('AI analyzing solicitation requirements...');
      const resp = await fetch((process.env.REACT_APP_API_BASE || 'http://127.0.0.1:8000') + '/api/solicitation/answer', {
        method: 'POST', body: formData,
      });
      setAnalysisStep('Generating response document...');
      const data = await resp.json();
      if (data.success) {
        setResult(data);
        setActiveSection('executive_summary');
      } else {
        alert(data.error || 'Analysis failed');
      }
    } catch (err: any) {
      alert(err.message || 'Error analyzing solicitation');
    }
    setAnalyzing(false); setAnalysisStep('');
  };

  const startEdit = (section: string, content: string) => {
    setEditingSection(section); setEditBuffer(content);
  };
  const saveEdit = (section: string) => {
    if (result?.response) {
      setResult({ ...result, response: { ...result.response, [section]: editBuffer } });
    }
    setEditingSection(null);
  };

  const sections = [
    { key: 'executive_summary', label: 'Executive Summary', icon: '01' },
    { key: 'understanding_of_requirement', label: 'Understanding of Requirement', icon: '02' },
    { key: 'technical_approach', label: 'Technical Approach', icon: '03' },
    { key: 'management_approach', label: 'Management Approach', icon: '04' },
    { key: 'staffing_plan', label: 'Staffing Plan', icon: '05' },
    { key: 'past_performance', label: 'Past Performance', icon: '06' },
    { key: 'quality_assurance', label: 'Quality Assurance', icon: '07' },
    { key: 'pricing_strategy', label: 'Pricing Strategy', icon: '08' },
    { key: 'edwosb_value_proposition', label: 'EDWOSB Value Proposition', icon: '09' },
    { key: 'compliance_matrix', label: 'Compliance Matrix', icon: '10' },
  ];

  const exportPDF = () => {
    if (!result) return;
    const sol = result.analysis?.solicitation_info || {};
    const r = result.response || {};
    const compMatrix = (r.compliance_matrix || []).map((c: any) =>
      `<tr><td style="padding:8px;border:1px solid #ddd;font-size:10pt;">${c.requirement}</td>
       <td style="padding:8px;border:1px solid #ddd;font-size:10pt;">${c.response}</td>
       <td style="padding:8px;border:1px solid #ddd;font-size:10pt;color:#6B7280;">${c.reference || ''}</td></tr>`
    ).join('');

    const html = `<!DOCTYPE html><html><head><meta charset="utf-8">
<title>Response — ${sol.number || ''} ${sol.title || ''}</title>
<style>
  @page { margin: 0.75in; }
  body { font-family: 'Segoe UI', Tahoma, sans-serif; color: #1F2937; font-size: 11pt; line-height: 1.7; margin: 0; padding: 0; }
  .cover { background: linear-gradient(135deg, #0F172A 0%, #1E3A5F 60%, #0D47A1 100%); color: white; padding: 60px 50px 40px; position: relative; }
  .cover::after { content: ''; position: absolute; bottom: 0; left: 0; right: 0; height: 4px; background: linear-gradient(90deg, #D97706, #F59E0B, #D97706); }
  .cover .company { font-size: 12pt; font-weight: 700; color: #F59E0B; letter-spacing: 1px; margin-bottom: 6px; }
  .cover h1 { font-size: 20pt; margin: 0 0 8px; font-weight: 700; line-height: 1.3; }
  .cover .meta { font-size: 10pt; color: #CBD5E1; }
  .cover .badges { margin-top: 16px; display: flex; gap: 8px; flex-wrap: wrap; }
  .cover .badge { background: rgba(255,255,255,0.15); padding: 3px 12px; border-radius: 4px; font-size: 8pt; font-weight: 700; letter-spacing: 0.5px; }
  .content { padding: 40px 50px; }
  .section { margin-bottom: 32px; page-break-inside: avoid; }
  .section h2 { color: #0F172A; font-size: 13pt; font-weight: 700; border-left: 4px solid #D97706; padding-left: 12px; margin-bottom: 12px; text-transform: uppercase; letter-spacing: 0.5px; }
  .section .num { color: #D97706; font-weight: 800; margin-right: 8px; }
  .section p { margin-bottom: 10px; text-align: justify; }
  table.compliance { width: 100%; border-collapse: collapse; margin-top: 12px; }
  table.compliance th { background: #0F172A; color: #F59E0B; padding: 10px; text-align: left; font-size: 9pt; text-transform: uppercase; letter-spacing: 0.5px; }
  table.compliance td { border: 1px solid #E5E7EB; }
  .footer { background: #0F172A; color: #94A3B8; padding: 20px 50px; font-size: 8pt; text-align: center; line-height: 1.8; }
  .footer .co { color: #F59E0B; font-weight: 700; font-size: 9pt; }
</style></head><body>
<div class="cover">
  <div class="company">DEE DAVIS INC</div>
  <h1>${sol.title || 'Solicitation Response'}</h1>
  <div class="meta">Solicitation: ${sol.number || 'N/A'} | Agency: ${sol.agency || 'N/A'} | ${new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })}</div>
  <div class="badges">
    <span class="badge">EDWOSB</span><span class="badge">WOSB</span><span class="badge">WBENC</span><span class="badge">MBE</span><span class="badge">SBE</span>
  </div>
</div>
<div class="content">
  <div class="section"><h2><span class="num">01</span>Executive Summary</h2>${(r.executive_summary || '').split('\n').map((p: string) => '<p>' + p + '</p>').join('')}</div>
  <div class="section"><h2><span class="num">02</span>Understanding of Requirement</h2>${(r.understanding_of_requirement || '').split('\n').map((p: string) => '<p>' + p + '</p>').join('')}</div>
  <div class="section"><h2><span class="num">03</span>Technical Approach</h2>${(r.technical_approach || '').split('\n').map((p: string) => '<p>' + p + '</p>').join('')}</div>
  <div class="section"><h2><span class="num">04</span>Management Approach</h2>${(r.management_approach || '').split('\n').map((p: string) => '<p>' + p + '</p>').join('')}</div>
  <div class="section"><h2><span class="num">05</span>Staffing Plan</h2>${(r.staffing_plan || '').split('\n').map((p: string) => '<p>' + p + '</p>').join('')}</div>
  <div class="section"><h2><span class="num">06</span>Past Performance</h2>${(r.past_performance || '').split('\n').map((p: string) => '<p>' + p + '</p>').join('')}</div>
  <div class="section"><h2><span class="num">07</span>Quality Assurance</h2>${(r.quality_assurance || '').split('\n').map((p: string) => '<p>' + p + '</p>').join('')}</div>
  <div class="section"><h2><span class="num">08</span>Pricing Strategy</h2>${(r.pricing_strategy || '').split('\n').map((p: string) => '<p>' + p + '</p>').join('')}</div>
  <div class="section"><h2><span class="num">09</span>EDWOSB Value Proposition</h2>${(r.edwosb_value_proposition || '').split('\n').map((p: string) => '<p>' + p + '</p>').join('')}</div>
  ${compMatrix ? `<div class="section"><h2><span class="num">10</span>Compliance Matrix</h2><table class="compliance"><thead><tr><th>Requirement</th><th>Response</th><th>Reference</th></tr></thead><tbody>${compMatrix}</tbody></table></div>` : ''}
</div>
<div class="footer">
  <div class="co">DEE DAVIS INC</div>
  755 W. Big Beaver Rd., Suite 2020, Troy, MI 48084 | (248) 376-4550 | info@deedavis.biz<br>
  EDWOSB | WOSB | WBENC | MBE | SBE | CAGE: 8UMX3 | SAM UEI: HJB4KNYJVGZ1
</div></body></html>`;

    const blob = new Blob([html], { type: 'text/html' });
    const url = window.URL.createObjectURL(blob);
    window.open(url, '_blank');
  };

  // ─── UPLOAD STATE ───
  if (!result) {
    return (
      <div className="space-y-6">
        <div>
          <h2 className="text-3xl font-bold text-white mb-2">Answer Solicitation</h2>
          <p className="text-gray-400">Upload any solicitation (RFP, RFQ, IFB, ITB, Sources Sought) and AI generates a complete, ProposalBio-scored response</p>
        </div>

        <div
          className={`border-2 border-dashed rounded-xl p-16 text-center cursor-pointer transition ${isDragging ? 'border-blue-500 bg-blue-900/20' : 'border-gray-600 hover:border-blue-500 hover:bg-gray-700/30'}`}
          onClick={() => document.getElementById('solFileInput')?.click()}
          onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
          onDragLeave={() => setIsDragging(false)}
          onDrop={handleDrop}
        >
          <div className="text-5xl mb-4">📄</div>
          <h3 className="text-xl font-bold text-blue-400 mb-2">Drop Solicitation PDF Here</h3>
          <p className="text-gray-400 mb-1">or click to browse</p>
          <p className="text-gray-500 text-sm">Supports RFP, RFQ, IFB, ITB, Sources Sought, Presolicitation, RFI</p>
          <input type="file" id="solFileInput" accept=".pdf,.txt,.doc,.docx" className="hidden" onChange={handleFileSelect} />
        </div>

        {selectedFile && (
          <div className="bg-green-900/30 border border-green-700 rounded-lg p-4 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <span className="text-2xl">✅</span>
              <div>
                <div className="font-semibold text-green-400">{selectedFile.name}</div>
                <div className="text-xs text-gray-400">{(selectedFile.size / 1024).toFixed(1)} KB</div>
              </div>
            </div>
            <button onClick={() => setSelectedFile(null)} className="text-gray-400 hover:text-white text-sm">Clear</button>
          </div>
        )}

        {selectedFile && !analyzing && (
          <div className="text-center">
            <button onClick={handleAnalyze}
              className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 px-10 py-4 rounded-xl font-bold text-lg transition shadow-lg shadow-blue-900/30">
              Analyze &amp; Generate Response
            </button>
          </div>
        )}

        {analyzing && (
          <div className="bg-blue-900/30 border border-blue-700 rounded-xl p-8">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
              <div>
                <h4 className="font-bold text-blue-400 text-lg mb-1">Generating Response...</h4>
                <p className="text-gray-400">{analysisStep}</p>
                <p className="text-gray-500 text-xs mt-1">This takes 15-30 seconds — AI is reading, analyzing, and writing your response</p>
              </div>
            </div>
          </div>
        )}
      </div>
    );
  }

  // ─── RESULTS STATE ───
  const sol = result.analysis?.solicitation_info || {};
  const bid = result.analysis?.bid_recommendation || {};
  const pb = result.proposalbio || {};
  const resp = result.response || {};
  const isGo = bid.decision === 'GO';
  const pbScore = pb.composite_score || 0;
  const pbColor = pbScore >= 75 ? 'green' : pbScore >= 60 ? 'yellow' : 'red';

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">{sol.title || result.document_name}</h2>
          <p className="text-gray-400 text-sm">{sol.number} | {sol.agency} | {result.pages_read} pages analyzed</p>
        </div>
        <div className="flex gap-3">
          <button onClick={() => { setResult(null); setSelectedFile(null); }}
            className="bg-gray-700 hover:bg-gray-600 px-4 py-2 rounded-lg font-semibold text-sm transition">
            New Upload
          </button>
          <button onClick={exportPDF}
            className="bg-green-600 hover:bg-green-700 px-4 py-2 rounded-lg font-semibold text-sm transition flex items-center gap-2">
            <FileText className="w-4 h-4" /> Export Response
          </button>
        </div>
      </div>

      {/* Score Cards Row */}
      <div className="grid grid-cols-3 gap-4">
        {/* Bid Recommendation */}
        <div className={`rounded-xl p-5 border ${isGo ? 'bg-green-900/20 border-green-500/50' : 'bg-yellow-900/20 border-yellow-500/50'}`}>
          <div className="text-xs text-gray-400 font-semibold mb-1">BID RECOMMENDATION</div>
          <div className={`text-3xl font-black ${isGo ? 'text-green-400' : 'text-yellow-400'}`}>{bid.decision || 'REVIEW'}</div>
          <div className="text-sm text-gray-400 mt-1">{bid.score}/100 fit score</div>
        </div>

        {/* ProposalBio Score */}
        <div className={`rounded-xl p-5 border ${pbColor === 'green' ? 'bg-green-900/20 border-green-500/50' : pbColor === 'yellow' ? 'bg-yellow-900/20 border-yellow-500/50' : 'bg-red-900/20 border-red-500/50'}`}>
          <div className="text-xs text-gray-400 font-semibold mb-1">PROPOSALBIO SCORE</div>
          <div className={`text-3xl font-black ${pbColor === 'green' ? 'text-green-400' : pbColor === 'yellow' ? 'text-yellow-400' : 'text-red-400'}`}>
            {pbScore.toFixed(0)}
          </div>
          <div className="text-sm text-gray-400 mt-1">
            {(pb.biohack_scores || []).filter((b: any) => b.score >= 6).length}/10 biohacks passing
          </div>
        </div>

        {/* Solicitation Info */}
        <div className="rounded-xl p-5 border border-blue-500/30 bg-blue-900/20">
          <div className="text-xs text-gray-400 font-semibold mb-1">SOLICITATION</div>
          <div className="text-sm text-white font-semibold">{sol.type || 'RFP'}</div>
          <div className="text-xs text-gray-400 mt-1">{sol.set_aside || 'Open'} | {sol.naics || 'N/A'}</div>
          <div className="text-xs text-gray-400">{sol.deadline || 'No deadline listed'}</div>
        </div>
      </div>

      {/* ProposalBio Biohacks */}
      {pb.biohack_scores && (
        <div className="bg-gray-800 rounded-xl p-4">
          <div className="text-xs font-semibold text-gray-400 mb-3">PROPOSALBIO BIOHACKS</div>
          <div className="grid grid-cols-5 gap-2">
            {pb.biohack_scores.map((bh: any) => (
              <div key={bh.biohack_number} className={`rounded-lg px-3 py-2 text-center ${bh.score >= 6 ? 'bg-green-900/30 border border-green-700/50' : 'bg-red-900/30 border border-red-700/50'}`}>
                <div className={`text-lg font-bold ${bh.score >= 6 ? 'text-green-400' : 'text-red-400'}`}>{bh.score.toFixed(1)}</div>
                <div className="text-[10px] text-gray-400 leading-tight">{bh.biohack_name}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Strengths / Concerns */}
      {(bid.strengths?.length > 0 || bid.concerns?.length > 0) && (
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-gray-800 rounded-xl p-4">
            <div className="text-xs font-semibold text-green-400 mb-2">STRENGTHS</div>
            {(bid.strengths || []).map((s: string, i: number) => (
              <div key={i} className="text-sm text-gray-300 mb-1">+ {s}</div>
            ))}
          </div>
          <div className="bg-gray-800 rounded-xl p-4">
            <div className="text-xs font-semibold text-red-400 mb-2">CONCERNS</div>
            {(bid.concerns || []).map((c: string, i: number) => (
              <div key={i} className="text-sm text-gray-300 mb-1">- {c}</div>
            ))}
          </div>
        </div>
      )}

      {/* Response Document — Section Navigation + Content */}
      <div className="grid grid-cols-12 gap-4">
        {/* Section Outline (Left) */}
        <div className="col-span-3 bg-gray-800 rounded-xl p-4 space-y-1">
          <div className="text-xs font-semibold text-gray-400 mb-3">RESPONSE OUTLINE</div>
          {sections.map((s) => (
            <button key={s.key} onClick={() => setActiveSection(s.key)}
              className={`w-full text-left px-3 py-2 rounded-lg text-sm transition flex items-center gap-2 ${
                activeSection === s.key ? 'bg-blue-600 text-white' : 'text-gray-400 hover:bg-gray-700 hover:text-white'
              }`}>
              <span className="text-xs font-mono text-blue-300 w-5">{s.icon}</span>
              <span className="truncate">{s.label}</span>
            </button>
          ))}
        </div>

        {/* Section Content (Right) */}
        <div className="col-span-9 bg-gray-800 rounded-xl p-6">
          {sections.map((s) => {
            if (activeSection !== s.key) return null;
            const content = resp[s.key];
            const isCompliance = s.key === 'compliance_matrix';

            return (
              <div key={s.key}>
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-xl font-bold text-white flex items-center gap-2">
                    <span className="text-blue-400 font-mono text-sm">{s.icon}</span>
                    {s.label}
                  </h3>
                  {!isCompliance && (
                    editingSection === s.key ? (
                      <div className="flex gap-2">
                        <button onClick={() => saveEdit(s.key)} className="bg-green-600 hover:bg-green-700 px-3 py-1 rounded text-xs font-semibold">Save</button>
                        <button onClick={() => setEditingSection(null)} className="bg-gray-600 hover:bg-gray-700 px-3 py-1 rounded text-xs font-semibold">Cancel</button>
                      </div>
                    ) : (
                      <button onClick={() => startEdit(s.key, content || '')}
                        className="bg-gray-700 hover:bg-gray-600 px-3 py-1 rounded text-xs font-semibold transition">
                        Edit
                      </button>
                    )
                  )}
                </div>

                {isCompliance ? (
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead><tr className="bg-gray-700">
                        <th className="text-left px-4 py-2 text-gray-300">Requirement</th>
                        <th className="text-left px-4 py-2 text-gray-300">Response</th>
                        <th className="text-left px-4 py-2 text-gray-300">Ref</th>
                      </tr></thead>
                      <tbody>
                        {(Array.isArray(content) ? content : []).map((row: any, i: number) => (
                          <tr key={i} className="border-t border-gray-700">
                            <td className="px-4 py-2 text-gray-300">{row.requirement}</td>
                            <td className="px-4 py-2 text-gray-400">{row.response}</td>
                            <td className="px-4 py-2 text-gray-500 text-xs">{row.reference}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : editingSection === s.key ? (
                  <textarea value={editBuffer} onChange={(e) => setEditBuffer(e.target.value)}
                    rows={12} className="w-full bg-gray-700 border border-gray-600 rounded-lg p-4 text-gray-200 text-sm leading-relaxed focus:outline-none focus:ring-2 focus:ring-blue-500" />
                ) : (
                  <div className="text-gray-300 text-sm leading-relaxed whitespace-pre-wrap">
                    {content || 'Not generated'}
                  </div>
                )}
              </div>
            );
          })}
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
    justificationType: 'edwosb_set_aside',
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
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        window.open(url, '_blank');
        alert('Sole Source Justification generated! Review it in the new tab.');
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
            <option value="edwosb_set_aside">EDWOSB Sole Source (FAR 19.1506)</option>
            <option value="unique_capability">Unique Capability (FAR 6.302-1)</option>
            <option value="brand_name">Brand Name — EDWOSB Procurement Vehicle</option>
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
          <div><strong>Manufacturing:</strong> Up to $8,500,000</div>
        </div>
        <p className="text-xs text-green-300 mt-2">
          The contracting officer must determine in writing that the EDWOSB is a responsible contractor
          with a reasonable expectation of performance.
        </p>
      </div>
    </div>
  );
}
